"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_loan_request_data():
    """Sample loan request data for testing."""
    return {
        "request_id": "REQ-TEST-001",
        "applicant_name": "John Doe",
        "applicant_ssn": "123-45-6789",
        "applicant_email": "john.doe@example.com",
        "annual_income": 75000.0,
        "employment_status": "employed",
        "employment_years": 5,
        "credit_score": 720,
        "existing_debts": 10000.0,
        "loan_amount": 200000.0,
        "loan_purpose": "home purchase",
        "collateral_value": 250000.0,
    }


@pytest.fixture
def high_risk_loan_request_data():
    """High-risk loan request for testing."""
    return {
        "request_id": "REQ-TEST-002",
        "applicant_name": "Jane Smith",
        "applicant_ssn": "987-65-4321",
        "applicant_email": "jane.smith@example.com",
        "annual_income": 30000.0,
        "employment_status": "self-employed",
        "employment_years": 1,
        "credit_score": 580,
        "existing_debts": 25000.0,
        "loan_amount": 150000.0,
        "loan_purpose": "business loan",
        "collateral_value": 0.0,
    }


@pytest.fixture
def missing_info_loan_request_data():
    """Loan request with missing information."""
    return {
        "request_id": "REQ-TEST-003",
        "applicant_name": "Bob Johnson",
        "applicant_ssn": "456-78-9123",
        "applicant_email": "bob.johnson@example.com",
        "annual_income": 50000.0,
        "employment_status": "employed",
        "employment_years": 3,
        "credit_score": None,  # Missing
        "existing_debts": 5000.0,
        "loan_amount": 100000.0,
        "loan_purpose": "debt consolidation",
        "collateral_value": 0.0,
    }
