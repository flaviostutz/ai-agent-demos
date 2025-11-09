"""Example demonstrating MLflow tracing for the loan approval agent."""

import os
from datetime import datetime, timezone
from decimal import Decimal

# Configure for testing
os.environ["OPENAI_API_KEY"] = "test-key"

from agents.loan_approval.src.agent import LoanApprovalAgent
from shared.models.loan import (
    CreditHistory,
    Employment,
    EmploymentStatus,
    Financial,
    LoanDetails,
    LoanPurpose,
    LoanRequest,
    PersonalInfo,
)
from shared.monitoring import get_logger

logger = get_logger(__name__)


def create_sample_loan_request() -> LoanRequest:
    """Create a sample loan request for testing tracing."""
    return LoanRequest(
        request_id="TRACE-DEMO-001",
        personal_info=PersonalInfo(
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1985, 5, 15, tzinfo=timezone.utc),
            ssn="123-45-6789",
            email="john.doe@example.com",
            phone="555-0100",
        ),
        loan_details=LoanDetails(
            amount=Decimal("250000.00"),
            purpose=LoanPurpose.HOME_PURCHASE,
            term_months=360,
        ),
        employment=Employment(
            status=EmploymentStatus.FULL_TIME,
            employer_name="Tech Corp",
            job_title="Software Engineer",
            years_employed=Decimal("5.0"),
            monthly_income=Decimal("8000.00"),
        ),
        financial=Financial(
            monthly_debt_payments=Decimal("1500.00"),
            total_assets=Decimal("50000.00"),
            total_liabilities=Decimal("25000.00"),
        ),
        credit_history=CreditHistory(
            credit_score=720,
            late_payments_count=0,
            bankruptcies_count=0,
            foreclosures_count=0,
        ),
    )


def main():
    """Demonstrate MLflow tracing with the loan approval agent."""
    print("=" * 70)
    print("MLflow Tracing Demonstration - Loan Approval Agent")
    print("=" * 70)
    print()

    try:
        # Note: This is a demonstration showing the tracing structure
        # In a real scenario with a valid OpenAI API key, this would work
        print("Creating sample loan request...")
        request = create_sample_loan_request()
        print(f"✓ Created request ID: {request.request_id}")
        print()

        print("Agent initialization would happen here with valid API key...")
        print("When running with a valid OpenAI API key, you would see:")
        print()
        print("Expected Trace Structure:")
        print("━" * 70)
        print("loan_approval_workflow (CHAIN)")
        print("│")
        print("├─ Attributes:")
        print("│  ├─ request_id: TRACE-DEMO-001")
        print("│  ├─ loan_amount: 250000.00")
        print("│  ├─ credit_score: 720")
        print("│  └─ employment_status: FULL_TIME")
        print("│")
        print("├─ Spans:")
        print("│  ├─ validate_input")
        print("│  │  └─ validation_passed: true")
        print("│  │")
        print("│  ├─ check_basic_eligibility")
        print("│  │  ├─ credit_score: 720")
        print("│  │  ├─ dti_ratio: 0.1875")
        print("│  │  └─ eligible: true")
        print("│  │")
        print("│  ├─ calculate_risk")
        print("│  │  └─ risk_score: ~25")
        print("│  │")
        print("│  ├─ check_policies")
        print("│  │  ├─ policy_compliant: true")
        print("│  │  └─ policy_notes: (from LLM)")
        print("│  │")
        print("│  └─ make_decision")
        print("│     ├─ decision: APPROVED")
        print("│     ├─ risk_score: ~25")
        print("│     └─ interest_rate: ~5.75%")
        print("│")
        print("└─ Outputs:")
        print("   ├─ decision: APPROVED")
        print("   ├─ risk_score: ~25")
        print("   └─ processing_time_ms: varies")
        print("━" * 70)
        print()

        print("To view traces in MLflow:")
        print("1. Run: cd agents/loan_approval/src && mlflow ui")
        print("2. Open: http://localhost:5000")
        print("3. Navigate to: Traces tab")
        print("4. Click on a trace to see the detailed hierarchy")
        print()

        print("Note: Set a valid OPENAI_API_KEY to run the actual agent")
        print()

    except Exception as e:
        logger.exception("Error in tracing demonstration")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
