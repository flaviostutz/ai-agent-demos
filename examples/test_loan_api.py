"""Sample script to test the loan approval API with an approved request.

This is a demonstration/example script for testing purposes.
"""
# ruff: noqa: T201

import json
from pathlib import Path

import httpx

# API configuration
API_URL = "http://localhost:8000"
SAMPLE_FILE = (
    Path(__file__).parent.parent
    / "agents"
    / "loan_approval"
    / "datasets"
    / "sample_approved_request.json"
)


def test_loan_approval_api() -> None:
    """Test the loan approval API with a sample approved request."""
    # Load sample request
    with SAMPLE_FILE.open() as f:
        loan_request = json.load(f)

    print("Testing Loan Approval API")
    print("=" * 50)
    print()

    # Check API health
    print("Checking API health...")
    try:
        response = httpx.get(f"{API_URL}/health", timeout=5.0)
        response.raise_for_status()
        print(f"✓ API is healthy: {response.json()}")
    except httpx.HTTPError as e:
        print(f"✗ API health check failed: {e}")
        print("Make sure the API is running with: make run")
        return

    print()

    # Submit loan request
    print("Submitting loan application...")
    print(f"Request ID: {loan_request['request_id']}")
    print(f"Applicant: {loan_request['applicant']['first_name']} {loan_request['applicant']['last_name']}")
    print(f"Loan Amount: ${loan_request['loan_details']['amount']:,.2f}")
    print(f"Credit Score: {loan_request['credit_history']['credit_score']}")
    print()

    try:
        response = httpx.post(
            f"{API_URL}/api/v1/loan/evaluate",
            json=loan_request,
            timeout=30.0,
        )
        response.raise_for_status()
        outcome = response.json()

        print("=" * 50)
        print("LOAN DECISION")
        print("=" * 50)
        print(f"Decision: {outcome['decision']['decision'].upper()}")
        
        if outcome['decision']['decision'] == 'approved':
            print(f"✓ Risk Score: {outcome['decision']['risk_score']}/100")
            print(f"✓ Interest Rate: {outcome['decision']['interest_rate']}%")
            print(f"✓ Monthly Payment: ${outcome['decision']['monthly_payment']:,.2f}")
            print(f"✓ Approved Amount: ${outcome['decision']['recommended_amount']:,.2f}")
            print(f"✓ Term: {outcome['decision']['recommended_term_months']} months")
        elif outcome['decision']['decision'] == 'disapproved':
            print(f"✗ Reason: {outcome['decision']['disapproval_reason']}")
        elif outcome['decision']['decision'] == 'additional_info_needed':
            print(f"⚠ Additional Info Required: {outcome['decision']['additional_info_description']}")

        print()
        print(f"Processing Time: {outcome['processing_time_ms']}ms")
        print(f"Model Version: {outcome['model_version']}")
        print()
        print("Full Response:")
        print(json.dumps(outcome, indent=2))

    except httpx.HTTPError as e:
        print(f"✗ API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")


if __name__ == "__main__":
    test_loan_approval_api()
