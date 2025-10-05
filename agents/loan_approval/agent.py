"""Loan approval agent implementation."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from shared.config import get_config
from shared.logging_utils import get_logger
from shared.metrics import get_metrics_collector
from shared.security import ContextPermissionManager, SecurityContext


class LoanOutcome(str, Enum):
    """Loan decision outcomes."""

    APPROVED = "approved"
    DISAPPROVED = "disapproved"
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"


class LoanRequest(BaseModel):
    """Loan request schema."""

    request_id: str = Field(description="Unique request identifier")
    applicant_name: str = Field(description="Full name of the applicant")
    applicant_ssn: str = Field(description="Social Security Number")
    applicant_email: str = Field(description="Email address")
    annual_income: float = Field(description="Annual income in USD", gt=0)
    employment_status: str = Field(description="Employment status (employed, self-employed, unemployed)")
    employment_years: int = Field(description="Years at current employment", ge=0)
    credit_score: int | None = Field(description="Credit score (300-850)", default=None, ge=300, le=850)
    existing_debts: float = Field(description="Total existing debt in USD", default=0.0, ge=0)
    loan_amount: float = Field(description="Requested loan amount in USD", gt=0)
    loan_purpose: str = Field(description="Purpose of the loan")
    collateral_value: float = Field(description="Value of collateral if any", default=0.0, ge=0)
    requested_at: datetime = Field(default_factory=datetime.now)


class LoanDecision(BaseModel):
    """Loan decision response."""

    request_id: str
    outcome: LoanOutcome
    risk_score: int | None = Field(
        description="Risk score 0-100, where 0 is lowest risk", default=None, ge=0, le=100
    )
    reason: str | None = Field(description="Reason for disapproval", default=None)
    additional_info_required: list[str] | None = Field(
        description="List of additional information needed", default=None
    )
    approved_amount: float | None = Field(description="Approved loan amount if approved", default=None)
    interest_rate: float | None = Field(description="Proposed interest rate", default=None)
    decision_at: datetime = Field(default_factory=datetime.now)


class AgentState(TypedDict):
    """State for the loan approval agent."""

    messages: Annotated[list, add_messages]
    request: LoanRequest
    decision: LoanDecision | None
    risk_factors: list[str]
    documents_checked: bool
    retrieved_documents: list[str]
    security_context: SecurityContext


class LoanApprovalAgent:
    """Loan approval agent using LangGraph."""

    def __init__(self, security_context: SecurityContext):
        self.config = get_config().get_agent_config("loan_approval")
        self.logger = get_logger(__name__, agent_id="loan_approval")
        self.metrics = get_metrics_collector("loan_approval")
        self.security_context = security_context
        self.permission_manager = ContextPermissionManager(security_context)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.llm.model,
            temperature=self.config.llm.temperature,
            api_key=self.config.llm.api_key,
        )

        # Initialize vector store for document retrieval
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            collection_name=self.config.vector_store.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.config.vector_store.persist_directory,
        )

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("validate_request", self._validate_request)
        workflow.add_node("retrieve_rules", self._retrieve_rules)
        workflow.add_node("assess_risk", self._assess_risk)
        workflow.add_node("make_decision", self._make_decision)

        # Add edges
        workflow.set_entry_point("validate_request")
        workflow.add_edge("validate_request", "retrieve_rules")
        workflow.add_edge("retrieve_rules", "assess_risk")
        workflow.add_edge("assess_risk", "make_decision")
        workflow.add_edge("make_decision", END)

        return workflow.compile()

    def _validate_request(self, state: AgentState) -> AgentState:
        """Validate the loan request."""
        self.logger.info(f"Validating request {state['request'].request_id}")

        request = state["request"]
        missing_info = []

        # Check for missing critical information
        if request.credit_score is None:
            missing_info.append("credit_score")

        if request.employment_status == "unemployed" and request.annual_income > 0:
            missing_info.append("employment_status_clarification")

        if missing_info:
            state["decision"] = LoanDecision(
                request_id=request.request_id,
                outcome=LoanOutcome.ADDITIONAL_INFO_NEEDED,
                additional_info_required=missing_info,
            )

        state["risk_factors"] = []
        return state

    def _retrieve_rules(self, state: AgentState) -> AgentState:
        """Retrieve relevant loan approval rules from documents."""
        self.logger.info("Retrieving loan rules")

        request = state["request"]

        # Build query from request
        query = f"""
        Loan application for {request.loan_purpose}.
        Amount: ${request.loan_amount:,.2f}
        Annual Income: ${request.annual_income:,.2f}
        Credit Score: {request.credit_score or 'Unknown'}
        Employment: {request.employment_status}
        """

        # Retrieve relevant documents
        docs = self.vectorstore.similarity_search(query, k=5)

        # Filter documents based on permissions
        filtered_docs = self.permission_manager.filter_documents(
            [{"content": doc.page_content, "domain": "public"} for doc in docs]
        )

        # Store document contents for risk assessment
        doc_contents = [doc["content"] for doc in filtered_docs]
        state["retrieved_documents"] = doc_contents

        self.logger.info(f"Retrieved {len(filtered_docs)} relevant rule documents")
        state["documents_checked"] = True
        state["messages"].append({"role": "system", "content": f"Retrieved {len(filtered_docs)} rules"})

        return state

    def _assess_risk(self, state: AgentState) -> AgentState:
        """Assess risk factors using both calculation and document-based rules."""
        self.logger.info("Assessing risk factors")

        request = state["request"]
        risk_factors = []
        risk_score = 0

        # Calculate debt-to-income ratio
        dti_ratio = (request.existing_debts + (request.loan_amount / 12)) / (
            request.annual_income / 12
        )

        # Calculate loan-to-value ratio if collateral provided
        ltv_ratio = None
        if request.collateral_value > 0:
            ltv_ratio = request.loan_amount / request.collateral_value

        # Use LLM to analyze risk based on internal documents
        if state.get("retrieved_documents"):
            self.logger.info("Using retrieved documents for risk assessment")

            # Build context from retrieved documents
            documents_context = "\n\n".join([
                f"--- Document {i+1} ---\n{doc}"
                for i, doc in enumerate(state["retrieved_documents"][:3])  # Use top 3 documents
            ])
            
            # Build prompt for LLM analysis
            analysis_prompt = f"""
            You are a loan risk analyst. Based on the internal loan approval rules provided, analyze this loan application and identify risk factors.

            INTERNAL LOAN RULES:
            {documents_context}

            LOAN APPLICATION:
            - Applicant: {request.applicant_name}
            - Loan Amount: ${request.loan_amount:,.2f}
            - Loan Purpose: {request.loan_purpose}
            - Annual Income: ${request.annual_income:,.2f}
            - Credit Score: {request.credit_score or 'Not provided'}
            - Employment: {request.employment_status} ({request.employment_years} years)
            - Existing Debts: ${request.existing_debts:,.2f}
            - DTI Ratio: {dti_ratio:.1%}
            - Collateral Value: ${request.collateral_value:,.2f}
            {f'- LTV Ratio: {ltv_ratio:.1%}' if ltv_ratio else '- No collateral (unsecured loan)'}

            Based on the internal rules, provide:
            1. A list of specific risk factors (if any) that violate or raise concerns per the rules
            2. A risk score from 0-100 (0 = lowest risk, 100 = highest risk)
            3. Key considerations from the rules that apply to this application

            Format your response as:
            RISK_FACTORS: [list each risk factor on a new line]
            RISK_SCORE: [number]
            RULE_CONSIDERATIONS: [key points from rules]
            """
            
            try:
                # Get LLM analysis
                response = self.llm.invoke(analysis_prompt)
                analysis = response.content
                
                # Parse LLM response
                lines = analysis.split('\n')
                parsing_section = None
                llm_risk_factors = []
                llm_risk_score = 50  # Default if not parsed
                rule_insights = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('RISK_FACTORS:'):
                        parsing_section = 'factors'
                        continue
                    elif line.startswith('RISK_SCORE:'):
                        parsing_section = 'score'
                        # Extract number from line
                        score_text = line.replace('RISK_SCORE:', '').strip()
                        try:
                            llm_risk_score = int(''.join(filter(str.isdigit, score_text)))
                        except Exception:
                            pass
                        continue
                    elif line.startswith('RULE_CONSIDERATIONS:'):
                        parsing_section = 'considerations'
                        continue
                    
                    if parsing_section == 'factors' and line and not line.startswith('RISK_SCORE:') and not line.startswith('RULE_CONSIDERATIONS:'):
                        # Remove bullet points and clean up
                        cleaned = line.lstrip('•-*').strip()
                        if cleaned:
                            llm_risk_factors.append(cleaned)
                    elif parsing_section == 'considerations' and line:
                        cleaned = line.lstrip('•-*').strip()
                        if cleaned:
                            rule_insights.append(cleaned)
                
                # Use LLM-derived risk factors and score
                risk_factors = llm_risk_factors
                risk_score = max(0, min(100, llm_risk_score))  # Clamp to 0-100
                
                self.logger.info(f"LLM risk assessment: {len(risk_factors)} factors, score {risk_score}")
                
                # Log rule insights for traceability
                if rule_insights:
                    self.logger.info(f"Rule considerations: {'; '.join(rule_insights[:3])}")
                
            except Exception as e:
                self.logger.error(f"Error in LLM risk assessment: {e}")
                # Fallback to basic calculation if LLM fails
                risk_factors, risk_score = self._calculate_basic_risk(request, dti_ratio, ltv_ratio)
        else:
            # Fallback to basic calculation if no documents retrieved
            self.logger.warning("No documents retrieved, using basic risk calculation")
            risk_factors, risk_score = self._calculate_basic_risk(request, dti_ratio, ltv_ratio)

        state["risk_factors"] = risk_factors
        state["messages"].append(
            {"role": "system", "content": f"Risk score calculated: {risk_score}"}
        )

        return state
    
    def _calculate_basic_risk(self, request: LoanRequest, dti_ratio: float, ltv_ratio: float | None) -> tuple[list[str], int]:
        """Calculate basic risk score without document context (fallback)."""
        risk_factors = []
        risk_score = 0

        # Credit score risk
        if request.credit_score:
            if request.credit_score < 580:
                risk_factors.append("Very low credit score (below 580)")
                risk_score += 40
            elif request.credit_score < 670:
                risk_factors.append("Below average credit score (580-669)")
                risk_score += 25
            elif request.credit_score < 740:
                risk_score += 10
        else:
            risk_factors.append("Credit score not provided")
            risk_score += 30

        # Debt-to-income ratio
        if dti_ratio > 0.43:
            risk_factors.append(f"High debt-to-income ratio ({dti_ratio:.1%})")
            risk_score += 30
        elif dti_ratio > 0.36:
            risk_factors.append(f"Elevated debt-to-income ratio ({dti_ratio:.1%})")
            risk_score += 15

        # Employment stability
        if request.employment_status == "unemployed":
            risk_factors.append("Currently unemployed")
            risk_score += 50
        elif request.employment_years < 2:
            risk_factors.append("Limited employment history (< 2 years)")
            risk_score += 15

        # Loan-to-value ratio (if collateral provided)
        if ltv_ratio:
            if ltv_ratio > 0.8:
                risk_factors.append(f"High loan-to-value ratio ({ltv_ratio:.1%})")
                risk_score += 20
        else:
            if request.loan_amount > 50000:
                risk_factors.append("Large unsecured loan (>$50K)")
                risk_score += 25

        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        return risk_factors, risk_score

    def _make_decision(self, state: AgentState) -> AgentState:
        """Make final loan decision."""
        self.logger.info("Making final decision")

        # If decision already made (e.g., missing info), return
        if state.get("decision"):
            return state

        request = state["request"]
        risk_factors = state["risk_factors"]

        # Calculate risk score from factors
        risk_score = min(len(risk_factors) * 15, 100)

        # Decision logic
        if risk_score >= 70:
            outcome = LoanOutcome.DISAPPROVED
            reason = "High risk: " + "; ".join(risk_factors)
            approved_amount = None
            interest_rate = None
        elif risk_score >= 40:
            outcome = LoanOutcome.APPROVED
            # Reduce approved amount for medium risk
            approved_amount = request.loan_amount * 0.75
            interest_rate = 7.5 + (risk_score * 0.1)  # Higher rate for higher risk
            reason = None
        else:
            outcome = LoanOutcome.APPROVED
            approved_amount = request.loan_amount
            # Base rate + risk adjustment
            interest_rate = 5.0 + (risk_score * 0.05)
            reason = None

        state["decision"] = LoanDecision(
            request_id=request.request_id,
            outcome=outcome,
            risk_score=risk_score,
            reason=reason,
            approved_amount=approved_amount,
            interest_rate=interest_rate if interest_rate else None,
        )

        self.logger.info(f"Decision: {outcome.value}, Risk Score: {risk_score}")
        return state

    def process_request(self, request: LoanRequest) -> LoanDecision:
        """Process a loan request and return decision."""
        self.logger.info(f"Processing loan request {request.request_id}")

        with self.metrics.measure_duration():
            try:
                # Initialize state
                initial_state = AgentState(
                    messages=[],
                    request=request,
                    decision=None,
                    risk_factors=[],
                    documents_checked=False,
                    retrieved_documents=[],
                    security_context=self.security_context,
                )

                # Run the graph
                result = self.graph.invoke(initial_state)

                decision = result["decision"]
                self.metrics.record_request(status=decision.outcome.value)

                return decision

            except Exception as e:
                self.logger.error(f"Error processing request: {e}")
                self.metrics.record_error(error_type=type(e).__name__)
                raise
