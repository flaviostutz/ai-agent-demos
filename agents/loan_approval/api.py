"""FastAPI REST API for loan approval agent."""

import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from agents.loan_approval import LoanApprovalAgent, LoanDecision, LoanRequest
from shared.alerting import get_teams_alerter
from shared.datasets import DatasetManager
from shared.logging_utils import get_logger
from shared.model_evaluation import ModelEvaluator
from shared.security import SecurityContext

logger = get_logger(__name__)
security = HTTPBearer()


class EvaluationRequest(BaseModel):
    """Request schema for model evaluation."""

    dataset_name: str
    target_field: str = "expected_outcome"
    prediction_field: str = "outcome"


class EvaluationResponse(BaseModel):
    """Response schema for model evaluation."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    avg_latency_ms: float
    error_rate: float
    mlflow_run_id: str | None = None


# Initialize on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    logger.info("Starting Loan Approval Agent API")
    yield
    logger.info("Shutting down Loan Approval Agent API")


app = FastAPI(
    title="Loan Approval Agent API",
    description="AI Agent for automated loan approval decisions with MLFlow tracking",
    version="0.2.0",
    lifespan=lifespan,
)


def get_security_context(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> SecurityContext:
    """Extract security context from request."""
    # In production, validate token and extract real user info
    # For now, using a simplified version
    return SecurityContext(
        user_id="user_123",
        roles=["loan_officer"],
        permissions={"tool:loan_approval", "pii_access"},
        allowed_data_domains={"public", "internal"},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "loan-approval-agent"}


@app.post("/api/v1/loan/evaluate", response_model=LoanDecision)
async def evaluate_loan(
    request: LoanRequest,
    security_context: SecurityContext = Depends(get_security_context),
):
    """Evaluate a loan application.

    Args:
        request: Loan application request
        security_context: Security context from authentication

    Returns:
        LoanDecision with outcome and details
    """
    logger.info(f"Received loan evaluation request: {request.request_id}")

    try:
        # Initialize agent with security context
        agent = LoanApprovalAgent(security_context=security_context)

        # Process request
        decision = agent.process_request(request)

        # Send alert for high-risk or disapproved loans
        if decision.outcome == "disapproved" or (decision.risk_score and decision.risk_score >= 70):
            alerter = get_teams_alerter()
            alerter.send_alert(
                title=f"High Risk Loan: {request.request_id}",
                message=f"Loan request {request.request_id} - Outcome: {decision.outcome}",
                severity="warning" if decision.outcome == "approved" else "error",
                metadata={
                    "Request ID": request.request_id,
                    "Amount": f"${request.loan_amount:,.2f}",
                    "Risk Score": str(decision.risk_score),
                    "Outcome": decision.outcome.value,
                },
            )

        return decision

    except Exception as e:
        logger.error(f"Error evaluating loan: {e}")

        # Send error alert
        alerter = get_teams_alerter()
        alerter.send_agent_error(
            agent_name="loan_approval",
            error_message=str(e),
            request_id=request.request_id,
        )

        raise HTTPException(
            status_code=500, detail=f"Error processing loan request: {str(e)}"
        ) from e


@app.get("/api/v1/loan/status/{request_id}")
async def get_loan_status(request_id: str):
    """Get status of a loan request.

    This is a placeholder - in production, you'd query a database.
    """
    return {
        "request_id": request_id,
        "status": "processing",
        "message": "Status tracking not yet implemented",
    }


@app.post("/api/v1/loan/evaluate_dataset", response_model=EvaluationResponse)
async def evaluate_on_dataset(
    eval_request: EvaluationRequest,
    security_context: SecurityContext = Depends(get_security_context),
):
    """Evaluate agent performance on a test dataset.

    Args:
        eval_request: Evaluation request with dataset name
        security_context: Security context from authentication

    Returns:
        Evaluation metrics
    """
    logger.info(f"Starting evaluation on dataset: {eval_request.dataset_name}")

    try:
        # Create agent wrapper for evaluation
        def agent_func(request_data: dict) -> dict:
            agent = LoanApprovalAgent(security_context=security_context)
            loan_request = LoanRequest(**request_data)
            decision = agent.process_request(loan_request)
            return {
                "outcome": decision.outcome.value,
                "risk_score": decision.risk_score,
                "reason": decision.reason,
            }

        # Initialize evaluator
        from shared.datasets import DatasetManager
        from shared.model_evaluation import ModelEvaluator

        dataset_manager = DatasetManager()
        evaluator = ModelEvaluator(
            agent_name="loan_approval",
            agent_func=agent_func,
            dataset_manager=dataset_manager,
        )

        # Run evaluation
        metrics = evaluator.evaluate_dataset(
            dataset_name=eval_request.dataset_name,
            target_field=eval_request.target_field,
            prediction_field=eval_request.prediction_field,
            log_to_mlflow=True,
        )

        # Get MLFlow run ID if available
        run_id = evaluator.tracker.run_id

        return EvaluationResponse(
            accuracy=metrics.accuracy,
            precision=metrics.precision,
            recall=metrics.recall,
            f1_score=metrics.f1_score,
            avg_latency_ms=metrics.avg_latency_ms,
            error_rate=metrics.error_rate,
            mlflow_run_id=run_id,
        )

    except FileNotFoundError as e:
        logger.error(f"Dataset not found: {e}")
        raise HTTPException(status_code=404, detail=f"Dataset not found: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
