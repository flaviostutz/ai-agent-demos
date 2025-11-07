"""Loan approval agent implementation with LangGraph."""

import time
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from shared.models.loan import (
    LoanRequest,
    LoanOutcome,
    LoanDecision,
    DecisionType,
)
from shared.monitoring import get_logger, MetricsTracker
from shared.utils import PDFLoader, SecurityContext, PermissionChecker
from agents.loan_approval.src.config import config
from agents.loan_approval.src.tools import RiskCalculator, PolicyChecker

logger = get_logger(__name__)


class AgentState(Dict[str, Any]):
    """State for the loan approval agent."""

    pass


class LoanApprovalAgent:
    """AI agent for loan approval decisions."""

    def __init__(
        self,
        security_context: Optional[SecurityContext] = None,
        metrics_tracker: Optional[MetricsTracker] = None,
    ) -> None:
        """
        Initialize loan approval agent.

        Args:
            security_context: Security context for permission checking
            metrics_tracker: Metrics tracker for observability
        """
        self.config = config
        self.security_context = security_context or PermissionChecker.create_loan_agent_context(
            agent_id="loan-approval-001",
            environment=config.environment,
        )
        self.metrics_tracker = metrics_tracker or MetricsTracker(
            experiment_name=config.mlflow_experiment_name
        )

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config.openai_model,
            temperature=config.openai_temperature,
            max_tokens=config.openai_max_tokens,
            api_key=config.openai_api_key,
        )

        # Load policy documents
        self.policy_content = self._load_policies()

        # Initialize tools
        self.risk_calculator = RiskCalculator(config)
        self.policy_checker = PolicyChecker(self.llm, self.policy_content)

        # Build workflow graph
        self.workflow = self._build_workflow()

        logger.info(f"Loan approval agent initialized (version {config.agent_version})")

    def _load_policies(self) -> str:
        """Load policy documents from PDFs."""
        try:
            logger.info(f"Loading policies from {self.config.policies_directory}")
            content = PDFLoader.load_directory(self.config.policies_directory)
            logger.info("Policy documents loaded successfully")
            return content
        except Exception as e:
            logger.error(f"Failed to load policy documents: {e}")
            return ""

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for loan approval."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("check_basic_eligibility", self._check_basic_eligibility)
        workflow.add_node("calculate_risk", self._calculate_risk)
        workflow.add_node("check_policies", self._check_policies)
        workflow.add_node("make_decision", self._make_decision)

        # Define edges
        workflow.set_entry_point("validate_input")
        workflow.add_edge("validate_input", "check_basic_eligibility")
        workflow.add_conditional_edges(
            "check_basic_eligibility",
            self._route_after_eligibility,
            {
                "continue": "calculate_risk",
                "reject": "make_decision",
                "need_info": "make_decision",
            },
        )
        workflow.add_edge("calculate_risk", "check_policies")
        workflow.add_edge("check_policies", "make_decision")
        workflow.add_edge("make_decision", END)

        return workflow.compile()

    def _validate_input(self, state: AgentState) -> AgentState:
        """Validate input data."""
        logger.info("Validating input data")
        request: LoanRequest = state["request"]

        # Security check
        self.security_context.require_all_permissions(
            *[p for p in self.security_context.permissions]
        )

        state["validation_passed"] = True
        state["validation_errors"] = []
        return state

    def _check_basic_eligibility(self, state: AgentState) -> AgentState:
        """Check basic eligibility criteria."""
        logger.info("Checking basic eligibility")
        request: LoanRequest = state["request"]

        # Credit score check
        if request.credit_history.credit_score < self.config.min_credit_score:
            state["eligible"] = False
            state["rejection_reason"] = (
                f"Credit score {request.credit_history.credit_score} is below "
                f"minimum requirement of {self.config.min_credit_score}"
            )
            return state

        # DTI ratio calculation
        monthly_income = float(request.employment.monthly_income)
        monthly_debt = float(request.financial.monthly_debt_payments)
        dti_ratio = monthly_debt / monthly_income if monthly_income > 0 else 1.0

        if dti_ratio > self.config.max_dti_ratio:
            state["eligible"] = False
            state["rejection_reason"] = (
                f"Debt-to-income ratio {dti_ratio:.2%} exceeds "
                f"maximum allowed {self.config.max_dti_ratio:.2%}"
            )
            return state

        # Employment check
        if request.employment.years_employed:
            months_employed = float(request.employment.years_employed) * 12
            if months_employed < self.config.min_employment_months:
                state["need_additional_info"] = True
                state["additional_info_description"] = (
                    "Employment history is less than 6 months. "
                    "Please provide additional employment verification documents."
                )
                return state

        state["eligible"] = True
        state["dti_ratio"] = dti_ratio
        return state

    def _route_after_eligibility(self, state: AgentState) -> str:
        """Route workflow after eligibility check."""
        if state.get("need_additional_info"):
            return "need_info"
        elif not state.get("eligible", False):
            return "reject"
        return "continue"

    def _calculate_risk(self, state: AgentState) -> AgentState:
        """Calculate risk score."""
        logger.info("Calculating risk score")
        request: LoanRequest = state["request"]

        risk_score = self.risk_calculator.calculate_risk_score(
            request, state.get("dti_ratio", 0.0)
        )

        state["risk_score"] = risk_score
        logger.info(f"Risk score calculated: {risk_score}")
        return state

    def _check_policies(self, state: AgentState) -> AgentState:
        """Check against policy documents."""
        logger.info("Checking policy compliance")
        request: LoanRequest = state["request"]

        policy_check_result = self.policy_checker.check_compliance(
            request, state.get("risk_score", 50)
        )

        state["policy_compliant"] = policy_check_result["compliant"]
        state["policy_notes"] = policy_check_result.get("notes", "")

        if not policy_check_result["compliant"]:
            state["rejection_reason"] = policy_check_result.get(
                "reason", "Policy compliance check failed"
            )

        return state

    def _make_decision(self, state: AgentState) -> AgentState:
        """Make final loan decision."""
        logger.info("Making final decision")

        # Check for rejection
        if state.get("rejection_reason"):
            decision = LoanDecision(
                decision=DecisionType.DISAPPROVED,
                disapproval_reason=state["rejection_reason"],
            )
            state["decision"] = decision
            return state

        # Check for additional info needed
        if state.get("need_additional_info"):
            decision = LoanDecision(
                decision=DecisionType.ADDITIONAL_INFO_NEEDED,
                additional_info_description=state["additional_info_description"],
            )
            state["decision"] = decision
            return state

        # Approved
        request: LoanRequest = state["request"]
        risk_score = state.get("risk_score", 50)

        # Calculate interest rate based on risk
        interest_rate = self._calculate_interest_rate(risk_score)

        # Calculate monthly payment
        loan_amount = float(request.loan_details.amount)
        term_months = request.loan_details.term_months
        monthly_rate = float(interest_rate) / 100 / 12
        monthly_payment = (
            loan_amount * monthly_rate * (1 + monthly_rate) ** term_months
        ) / ((1 + monthly_rate) ** term_months - 1)

        decision = LoanDecision(
            decision=DecisionType.APPROVED,
            risk_score=risk_score,
            interest_rate=Decimal(str(interest_rate)),
            monthly_payment=Decimal(str(round(monthly_payment, 2))),
            recommended_amount=request.loan_details.amount,
            recommended_term_months=term_months,
        )

        state["decision"] = decision
        logger.info(f"Loan approved with risk score {risk_score}")
        return state

    def _calculate_interest_rate(self, risk_score: int) -> float:
        """Calculate interest rate based on risk score."""
        # Base rate + risk premium
        base_rate = 3.5
        max_premium = 10.0
        risk_premium = (risk_score / 100) * max_premium
        return base_rate + risk_premium

    def process_loan_request(self, request: LoanRequest) -> LoanOutcome:
        """
        Process a loan request and return decision.

        Args:
            request: Loan application request

        Returns:
            Loan outcome with decision
        """
        start_time = time.time()
        trace_id = f"trace-{request.request_id}-{int(time.time())}"

        logger.info(f"Processing loan request {request.request_id}")

        try:
            with self.metrics_tracker.start_run(run_name=f"loan-{request.request_id}"):
                # Log request parameters
                self.metrics_tracker.log_params(
                    {
                        "request_id": request.request_id,
                        "loan_amount": float(request.loan_details.amount),
                        "credit_score": request.credit_history.credit_score,
                        "employment_status": request.employment.status.value,
                    }
                )

                # Execute workflow
                initial_state: AgentState = {
                    "request": request,
                    "trace_id": trace_id,
                }

                final_state = self.workflow.invoke(initial_state)
                decision: LoanDecision = final_state["decision"]

                # Calculate processing time
                processing_time_ms = int((time.time() - start_time) * 1000)

                # Log metrics
                self.metrics_tracker.log_metrics(
                    {
                        "processing_time_ms": float(processing_time_ms),
                        "risk_score": float(decision.risk_score or 0),
                    }
                )

                self.metrics_tracker.set_tag("decision", decision.decision.value)

                # Create outcome
                outcome = LoanOutcome(
                    request_id=request.request_id,
                    decision=decision,
                    processing_time_ms=processing_time_ms,
                    model_version=self.config.agent_version,
                    timestamp=datetime.utcnow(),
                    agent_trace_id=trace_id,
                )

                logger.info(
                    f"Loan request {request.request_id} processed: {decision.decision.value}"
                )
                return outcome

        except Exception as e:
            logger.error(f"Error processing loan request {request.request_id}: {e}")
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Return error decision
            error_decision = LoanDecision(
                decision=DecisionType.ADDITIONAL_INFO_NEEDED,
                additional_info_description=f"Unable to process request due to system error. Please try again later.",
            )

            return LoanOutcome(
                request_id=request.request_id,
                decision=error_decision,
                processing_time_ms=processing_time_ms,
                model_version=self.config.agent_version,
                timestamp=datetime.utcnow(),
                agent_trace_id=trace_id,
            )