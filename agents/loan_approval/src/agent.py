"""Loan approval agent implementation with LangGraph."""

import ssl
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, TypedDict

import httpx
import mlflow
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import SecretStr

if TYPE_CHECKING:
    from langchain_core.callbacks import BaseCallbackHandler

from agents.loan_approval.src.config import config
from agents.loan_approval.src.tools import PolicyChecker, RiskCalculator
from shared.models.loan import (
    DecisionType,
    LoanDecision,
    LoanOutcome,
    LoanRequest,
)
from shared.monitoring import (
    MetricsTracker,
    get_llm_callback_handler,
    get_logger,
    setup_mlflow_langchain_autologging,
)
from shared.utils import PDFLoader, PermissionChecker, SecurityContext

logger = get_logger(__name__)


class AgentState(TypedDict, total=False):
    """Type definition for agent state."""

    request: LoanRequest
    validation_passed: bool
    validation_errors: list[str]
    eligible: bool
    rejection_reason: str
    need_additional_info: bool
    additional_info_description: str
    dti_ratio: float
    risk_score: int
    policy_compliant: bool
    policy_notes: str
    decision: LoanDecision


class LoanApprovalAgent:
    """AI agent for loan approval decisions."""

    def __init__(
        self,
        security_context: SecurityContext | None = None,
        metrics_tracker: MetricsTracker | None = None,
    ) -> None:
        """Initialize loan approval agent.

        Args:
            security_context: Security context for permission checking
            metrics_tracker: Metrics tracker for observability

        """
        self.config = config

        # Validate LLM configuration
        if config.use_azure_openai:
            # Validate Azure OpenAI configuration
            if not config.azure_openai_api_key or config.azure_openai_api_key.strip() == "":
                error_msg = (
                    "Azure OpenAI API key is not configured. "
                    "Please set AZURE_OPENAI_API_KEY environment variable."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            if not config.azure_openai_endpoint or config.azure_openai_endpoint.strip() == "":
                error_msg = (
                    "Azure OpenAI endpoint is not configured. "
                    "Please set AZURE_OPENAI_ENDPOINT environment variable."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            if not config.azure_openai_deployment or config.azure_openai_deployment.strip() == "":
                error_msg = (
                    "Azure OpenAI deployment is not configured. "
                    "Please set AZURE_OPENAI_DEPLOYMENT environment variable."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
        elif (
            not config.openai_api_key
            or config.openai_api_key.strip() == ""
            or config.openai_api_key == "test-key"
        ):
            # Validate OpenAI API key is provided
            error_msg = (
                "OpenAI API key is not configured. "
                "Please set OPENAI_API_KEY environment variable or update the configuration."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.security_context = security_context or PermissionChecker.create_loan_agent_context(
            agent_id="loan-approval-001",
            environment=config.environment,
        )
        self.metrics_tracker = metrics_tracker or MetricsTracker(
            experiment_name=config.mlflow_experiment_name
        )

        # Enable MLflow LangChain autologging if configured
        if self.config.enable_llm_logging:
            setup_mlflow_langchain_autologging(
                log_models=self.config.mlflow_log_llm_models,
                log_inputs_outputs=self.config.mlflow_log_llm_inputs_outputs,
            )
            logger.info("MLflow LangChain autologging enabled")

        # Create LLM callback handler for detailed logging
        self.llm_callback = None
        if self.config.enable_llm_logging:
            self.llm_callback = get_llm_callback_handler(
                log_prompts=self.config.log_llm_prompts,
                log_responses=self.config.log_llm_responses,
            )
            logger.info("LLM callback handler initialized")

        # Initialize LLM with callbacks
        callbacks: list[BaseCallbackHandler] | None = (
            [self.llm_callback] if self.llm_callback else None
        )

        # Create HTTP client with system SSL certificates for corporate proxies
        # This uses the system's certificate store which includes corporate CA certs
        http_client = httpx.Client(
            verify=ssl.create_default_context(),
            timeout=60.0,
        )

        # Initialize LLM based on configuration (OpenAI or Azure OpenAI)
        if config.use_azure_openai:
            self.llm: ChatOpenAI | AzureChatOpenAI = AzureChatOpenAI(
                azure_deployment=config.azure_openai_deployment,
                azure_endpoint=config.azure_openai_endpoint,
                api_key=SecretStr(config.azure_openai_api_key or ""),
                api_version=config.azure_openai_api_version,
                temperature=config.openai_temperature,
                callbacks=callbacks,
                http_client=http_client,
            )
            logger.info(f"Using Azure OpenAI with deployment: {config.azure_openai_deployment}")
        else:
            self.llm = ChatOpenAI(
                model=config.openai_model,
                temperature=config.openai_temperature,
                api_key=SecretStr(config.openai_api_key),
                callbacks=callbacks,
                http_client=http_client,
            )
            logger.info(f"Using OpenAI with model: {config.openai_model}")

        # Load policy documents
        self.policy_content = self._load_policies()

        # Initialize tools
        self.risk_calculator = RiskCalculator(config)
        self.policy_checker = PolicyChecker(self.llm, self.policy_content)

        # Build workflow graph
        self.workflow = self._build_workflow()

        logger.info(f"Loan approval agent initialized (version {config.agent_version})")

    def health_check(self) -> dict[str, Any]:
        """Perform health check including LLM connectivity test.

        Returns:
            Dictionary with health check results

        """
        health_status: dict[str, Any] = {
            "agent_initialized": True,
            "llm_configured": False,
            "llm_responsive": False,
            "policies_loaded": bool(self.policy_content),
            "workflow_ready": self.workflow is not None,
            "error": None,
        }

        try:
            # Test LLM connectivity with a simple query
            logger.info("Performing LLM health check...")
            start_time = time.time()

            # Simple test query to verify LLM is responsive
            test_response = self.llm.invoke("Say 'OK' if you are operational.")

            elapsed_time = time.time() - start_time

            # Check if we got a valid response
            if test_response and hasattr(test_response, "content"):
                health_status["llm_configured"] = True
                health_status["llm_responsive"] = True
                health_status["llm_response_time_ms"] = round(elapsed_time * 1000, 2)
                logger.info(f"LLM health check passed in {elapsed_time:.2f}s")
            else:
                health_status["error"] = "LLM returned invalid response"
                logger.warning("LLM health check: invalid response format")

        except Exception as e:
            health_status["error"] = f"LLM health check failed: {e!s}"
            logger.exception("LLM health check failed")

        return health_status

    def _load_policies(self) -> str:
        """Load policy documents from PDFs."""
        try:
            logger.info(f"Loading policies from {self.config.policies_directory}")
            content = PDFLoader.load_directory(self.config.policies_directory)
            logger.info("Policy documents loaded successfully")
            return content
        except Exception:
            logger.exception("Failed to load policy documents")
            return ""

    def _build_workflow(self) -> Any:
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
        with mlflow.start_span(name="validate_input") as span:
            logger.info("Validating input data")
            request = state["request"]

            # Log span attributes
            span.set_attributes(
                {
                    "request_id": request.request_id,
                    "loan_amount": float(request.loan_details.amount),
                    "credit_score": request.credit_history.credit_score,
                }
            )

            # Security check
            self.security_context.require_all_permissions(*list(self.security_context.permissions))

            state["validation_passed"] = True
            state["validation_errors"] = []

            span.set_attribute("validation_passed", value=True)
            return state

    def _check_basic_eligibility(self, state: AgentState) -> AgentState:
        """Check basic eligibility criteria."""
        with mlflow.start_span(name="check_basic_eligibility") as span:
            logger.info("Checking basic eligibility")
            request: LoanRequest = state["request"]

            span.set_attributes(
                {
                    "credit_score": request.credit_history.credit_score,
                    "min_credit_score": self.config.min_credit_score,
                }
            )

            # Credit score check
            if request.credit_history.credit_score < self.config.min_credit_score:
                state["eligible"] = False
                state["rejection_reason"] = (
                    f"Credit score {request.credit_history.credit_score} is below "
                    f"minimum requirement of {self.config.min_credit_score}"
                )
                span.set_attribute("eligible", value=False)
                span.set_attribute("rejection_reason", value=state["rejection_reason"])
                return state

            # DTI ratio calculation
            monthly_income = float(request.employment.monthly_income)
            monthly_debt = float(request.financial.monthly_debt_payments)
            dti_ratio = monthly_debt / monthly_income if monthly_income > 0 else 1.0

            span.set_attributes(
                {
                    "dti_ratio": dti_ratio,
                    "max_dti_ratio": self.config.max_dti_ratio,
                }
            )

            if dti_ratio > self.config.max_dti_ratio:
                state["eligible"] = False
                state["rejection_reason"] = (
                    f"Debt-to-income ratio {dti_ratio:.2%} exceeds "
                    f"maximum allowed {self.config.max_dti_ratio:.2%}"
                )
                span.set_attribute("eligible", value=False)
                span.set_attribute("rejection_reason", value=state["rejection_reason"])
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
                    span.set_attribute("need_additional_info", value=True)
                    return state

            state["eligible"] = True
            state["dti_ratio"] = dti_ratio
            span.set_attribute("eligible", value=True)
            span.set_attribute("dti_ratio", value=dti_ratio)
            return state

    def _route_after_eligibility(self, state: AgentState) -> str:
        """Route workflow after eligibility check."""
        if state.get("need_additional_info"):
            return "need_info"
        if not state.get("eligible", False):
            return "reject"
        return "continue"

    def _calculate_risk(self, state: AgentState) -> AgentState:
        """Calculate risk score."""
        with mlflow.start_span(name="calculate_risk") as span:
            logger.info("Calculating risk score")
            request: LoanRequest = state["request"]

            risk_score = self.risk_calculator.calculate_risk_score(
                request, state.get("dti_ratio", 0.0)
            )

            state["risk_score"] = risk_score
            span.set_attribute("risk_score", value=risk_score)
            logger.info(f"Risk score calculated: {risk_score}")
            return state

    def _check_policies(self, state: AgentState) -> AgentState:
        """Check against policy documents."""
        with mlflow.start_span(name="check_policies") as span:
            logger.info("Checking policy compliance")
            request: LoanRequest = state["request"]

            policy_check_result = self.policy_checker.check_compliance(
                request, state.get("risk_score", 50)
            )

            state["policy_compliant"] = policy_check_result["compliant"]
            state["policy_notes"] = policy_check_result.get("notes", "")

            span.set_attributes(
                {
                    "policy_compliant": policy_check_result["compliant"],
                    "policy_notes": policy_check_result.get("notes", ""),
                }
            )

            if not policy_check_result["compliant"]:
                # Build detailed rejection reason with LLM explanation
                base_reason = policy_check_result.get("reason", "Policy compliance check failed")
                notes = policy_check_result.get("notes", "")
                missing_info = policy_check_result.get("missing_information", [])

                # Build comprehensive rejection message
                rejection_parts = [base_reason]

                if notes and notes != base_reason:
                    rejection_parts.append(f"Details: {notes}")

                if missing_info:
                    missing_str = ", ".join(missing_info)
                    rejection_parts.append(f"Missing information: {missing_str}")

                state["rejection_reason"] = ". ".join(rejection_parts)

                span.set_attribute("rejection_reason", value=state["rejection_reason"])

            return state

    def _make_decision(self, state: AgentState) -> AgentState:
        """Make final loan decision."""
        with mlflow.start_span(name="make_decision") as span:
            logger.info("Making final decision")

            # Check for rejection
            if state.get("rejection_reason"):
                decision = LoanDecision(
                    decision=DecisionType.DISAPPROVED,
                    risk_score=None,
                    disapproval_reason=state["rejection_reason"],
                    recommended_amount=None,
                    recommended_term_months=None,
                    interest_rate=None,
                    monthly_payment=None,
                )
                state["decision"] = decision
                span.set_attributes(
                    {
                        "decision": DecisionType.DISAPPROVED.value,
                        "rejection_reason": state["rejection_reason"],
                    }
                )
                return state

            # Check for additional info needed
            if state.get("need_additional_info"):
                decision = LoanDecision(
                    decision=DecisionType.ADDITIONAL_INFO_NEEDED,
                    additional_info_description=state["additional_info_description"],
                    risk_score=None,
                    recommended_amount=None,
                    recommended_term_months=None,
                    interest_rate=None,
                    monthly_payment=None,
                )
                state["decision"] = decision
                span.set_attributes(
                    {
                        "decision": DecisionType.ADDITIONAL_INFO_NEEDED.value,
                        "additional_info_description": state["additional_info_description"],
                    }
                )
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
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** term_months) / (
                (1 + monthly_rate) ** term_months - 1
            )

            decision = LoanDecision(
                decision=DecisionType.APPROVED,
                risk_score=risk_score,
                interest_rate=Decimal(str(interest_rate)),
                monthly_payment=Decimal(str(round(monthly_payment, 2))),
                recommended_amount=request.loan_details.amount,
                recommended_term_months=term_months,
            )

            state["decision"] = decision
            span.set_attributes(
                {
                    "decision": DecisionType.APPROVED.value,
                    "risk_score": risk_score,
                    "interest_rate": interest_rate,
                    "monthly_payment": float(monthly_payment),
                }
            )
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
        """Process a loan request and return decision.

        Args:
            request: Loan application request

        Returns:
            Loan outcome with decision

        """
        start_time = time.time()
        trace_id = f"trace-{request.request_id}-{int(time.time())}"

        logger.info(f"Processing loan request {request.request_id}")

        try:
            # Start a trace for the entire loan processing workflow
            with (
                self.metrics_tracker.start_run(run_name=f"loan-{request.request_id}"),
                mlflow.start_span(
                    name="loan_approval_workflow",
                    span_type="CHAIN",
                ) as trace,
            ):
                # Set trace attributes
                trace.set_attributes(
                    {
                        "request_id": request.request_id,
                        "trace_id": trace_id,
                        "loan_amount": float(request.loan_details.amount),
                        "credit_score": request.credit_history.credit_score,
                        "employment_status": request.employment.status.value,
                        "model_version": self.config.agent_version,
                    }
                )
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
                initial_state = {
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

                # Set trace outputs
                trace.set_outputs(
                    {
                        "decision": decision.decision.value,
                        "risk_score": decision.risk_score,
                        "processing_time_ms": processing_time_ms,
                    }
                )

                # Create outcome
                outcome = LoanOutcome(
                    request_id=request.request_id,
                    decision=decision,
                    processing_time_ms=processing_time_ms,
                    model_version=self.config.agent_version,
                    timestamp=datetime.now(tz=timezone.utc),
                    agent_trace_id=trace_id,
                )

                logger.info(
                    f"Loan request {request.request_id} processed: {decision.decision.value}"
                )
                return outcome

        except Exception:
            logger.exception(f"Error processing loan request {request.request_id}")
            # Re-raise the exception to let the API layer handle it with proper HTTP error codes
            raise
