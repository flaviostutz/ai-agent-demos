"""REST API for loan approval agent."""

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from agents.loan_approval.src.agent import LoanApprovalAgent
from agents.loan_approval.src.config import config
from shared.models.loan import LoanOutcome, LoanRequest
from shared.monitoring import get_logger, setup_logging

# Setup logging
setup_logging(level=config.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Loan Approval Agent API",
    description="AI Agent for automated loan application processing",
    version=config.agent_version,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent: LoanApprovalAgent | None = None
agent_health_status: dict = {}


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize agent on startup."""
    global agent, agent_health_status  # noqa: PLW0603
    logger.info("Starting Loan Approval Agent API")

    agent = LoanApprovalAgent()
    logger.info("Agent initialized successfully")

    # Perform health check with LLM
    logger.info("Performing startup health check...")
    agent_health_status = agent.health_check()

    if not agent_health_status.get("llm_responsive", False):
        error_msg = agent_health_status.get("error", "LLM not responsive")
        logger.error(f"Startup health check failed: {error_msg}")
        raise RuntimeError(f"LLM health check failed: {error_msg}")

    logger.info("Startup health check passed - system fully operational")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutting down Loan Approval Agent API")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": "Loan Approval Agent",
        "version": config.agent_version,
        "status": "running",
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint.

    Returns:
        Dictionary with comprehensive health status including LLM connectivity

    """
    if agent is None:
        return {
            "status": "unhealthy",
            "agent_initialized": False,
            "error": "Agent not initialized",
        }

    # Get latest health status
    current_health = agent_health_status.copy() if agent_health_status else {}

    # Determine overall status
    is_healthy = (
        current_health.get("llm_responsive", False)
        and current_health.get("workflow_ready", False)
        and current_health.get("policies_loaded", False)
    )

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "agent_initialized": agent is not None,
        "llm_responsive": current_health.get("llm_responsive", False),
        "llm_response_time_ms": current_health.get("llm_response_time_ms"),
        "policies_loaded": current_health.get("policies_loaded", False),
        "workflow_ready": current_health.get("workflow_ready", False),
        "error": current_health.get("error"),
    }


@app.post("/api/v1/loan/evaluate")
async def evaluate_loan(request: LoanRequest) -> LoanOutcome:
    """Evaluate a loan application.

    Args:
        request: Loan application request

    Returns:
        Loan outcome with decision

    Raises:
        HTTPException: If agent is not initialized or processing fails

    """
    if agent is None:
        logger.error("Agent not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    try:
        logger.info(f"Received loan evaluation request: {request.request_id}")
        outcome = agent.process_loan_request(request)
        logger.info(
            f"Loan evaluation completed: {request.request_id} - {outcome.decision.decision.value}"
        )
        return outcome
    except Exception as e:
        logger.exception(f"Error processing loan request {request.request_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing loan request: {e!s}",
        ) from e


@app.get("/api/v1/metrics")
async def get_metrics() -> dict:
    """Get agent metrics.

    Returns:
        Dictionary with agent metrics

    """
    # In production, this would return actual metrics from MLFlow/Databricks
    return {
        "agent_version": config.agent_version,
        "environment": config.environment,
        "mlflow_experiment": config.mlflow_experiment_name,
    }


def main() -> None:
    """Main entry point for the API server."""
    logger.info(f"Starting API server on {config.api_host}:{config.api_port}")
    uvicorn.run(
        "api:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.environment == "development",
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
