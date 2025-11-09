#!/usr/bin/env python3
"""Example demonstrating LLM interaction logging with MLflow and LangChain.

This script shows how all LLM interactions are automatically logged when
processing a loan application.

Run with:
    python examples/llm_logging_demo.py

Then view logs in MLflow UI:
    cd agents/loan_approval/src
    mlflow ui --port 5000
"""

import os
from decimal import Decimal

# Set up environment for demo
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")
os.environ["ENABLE_LLM_LOGGING"] = "true"
os.environ["LOG_LLM_PROMPTS"] = "true"
os.environ["LOG_LLM_RESPONSES"] = "true"

from agents.loan_approval.src.agent import LoanApprovalAgent
from agents.loan_approval.src.config import config
from shared.models.loan import (
    CreditHistory,
    Employment,
    EmploymentStatus,
    Financial,
    LoanDetails,
    LoanPurpose,
    LoanRequest,
)
from shared.monitoring import get_logger

logger = get_logger(__name__)


def create_sample_loan_request() -> LoanRequest:
    """Create a sample loan request for testing."""
    return LoanRequest(
        request_id="demo-12345",
        applicant_name="John Doe",
        loan_details=LoanDetails(
            amount=Decimal("50000.00"),
            purpose=LoanPurpose.HOME_IMPROVEMENT,
            term_months=36,
        ),
        employment=Employment(
            status=EmploymentStatus.EMPLOYED,
            employer="Tech Corp",
            years_employed=Decimal("3.5"),
            monthly_income=Decimal("8000.00"),
        ),
        credit_history=CreditHistory(
            credit_score=720,
            has_late_payments=False,
            has_collections=False,
        ),
        financial=Financial(
            monthly_debt_payments=Decimal("1500.00"),
            has_bankruptcy=False,
            has_foreclosure=False,
        ),
    )


def main() -> None:
    """Run the LLM logging demonstration."""
    logger.info("=" * 80)
    logger.info("LLM Logging Demonstration")
    logger.info("=" * 80)

    # Initialize agent with LLM logging enabled
    logger.info("\n1. Initializing LoanApprovalAgent with LLM logging...")
    agent = LoanApprovalAgent()

    # Verify LLM logging is enabled
    assert config.enable_llm_logging, "LLM logging should be enabled"
    assert agent.llm_callback is not None, "LLM callback should be initialized"
    logger.info("✓ LLM logging is enabled")
    logger.info(f"  - Log prompts: {config.log_llm_prompts}")
    logger.info(f"  - Log responses: {config.log_llm_responses}")
    logger.info(f"  - MLflow autologging: enabled")

    # Create sample loan request
    logger.info("\n2. Creating sample loan request...")
    loan_request = create_sample_loan_request()
    logger.info(f"✓ Loan request created: {loan_request.request_id}")
    logger.info(f"  - Applicant: {loan_request.applicant_name}")
    logger.info(f"  - Amount: ${loan_request.loan_details.amount:,.2f}")
    logger.info(f"  - Credit Score: {loan_request.credit_history.credit_score}")

    # Process loan with LLM logging
    logger.info("\n3. Processing loan application...")
    logger.info("   (All LLM interactions will be logged automatically)")
    logger.info("   " + "-" * 70)

    with agent.metrics_tracker.start_run(run_name=f"demo-{loan_request.request_id}"):
        result = agent.process_loan(loan_request)

    logger.info("   " + "-" * 70)
    logger.info("✓ Loan processing completed")

    # Display results
    logger.info("\n4. Results:")
    logger.info(f"  - Decision: {result.decision.value}")
    if result.risk_score is not None:
        logger.info(f"  - Risk Score: {result.risk_score}")
    if result.recommended_amount:
        logger.info(f"  - Approved Amount: ${result.recommended_amount:,.2f}")
    if result.interest_rate:
        logger.info(f"  - Interest Rate: {result.interest_rate:.2%}")

    # Show how to view logs
    logger.info("\n" + "=" * 80)
    logger.info("LLM Interaction Logs")
    logger.info("=" * 80)
    logger.info("\nAll LLM interactions have been logged! You can view them:")
    logger.info("\n1. MLflow UI:")
    logger.info("   cd agents/loan_approval/src")
    logger.info("   mlflow ui --port 5000")
    logger.info("   Open: http://localhost:5000")
    logger.info("\n2. MLflow Artifacts:")
    logger.info(f"   Location: {config.get_mlflow_tracking_uri()}")
    logger.info("   Contains:")
    logger.info("   - prompts/llm_call_*.txt  (input prompts)")
    logger.info("   - responses/llm_call_*.txt (LLM responses)")
    logger.info("\n3. MLflow Metrics:")
    logger.info("   - llm_call_*_latency_sec")
    logger.info("   - llm_call_*_total_tokens")
    logger.info("   - llm_call_*_prompt_tokens")
    logger.info("   - llm_call_*_completion_tokens")
    logger.info("\n4. Application Logs:")
    logger.info("   Check the console output above for detailed LLM logs")
    logger.info("\n" + "=" * 80)

    # Show callback stats
    if agent.llm_callback:
        logger.info(f"\nLLM Callback Statistics:")
        logger.info(f"  - Total LLM calls: {agent.llm_callback.call_count}")

    logger.info("\n✓ Demo completed successfully!")


if __name__ == "__main__":
    main()
