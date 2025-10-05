"""Tests for loan approval agent."""

import pytest
from agents.loan_approval import LoanRequest
from agents.loan_approval.agent import LoanApprovalAgent, LoanOutcome


class TestLoanApprovalAgent:
    """Test cases for LoanApprovalAgent."""

    @pytest.fixture(autouse=True)
    def setup(self, security_context, mock_openai_key):
        """Set up test environment."""
        self.security_context = security_context

    def test_approved_loan_low_risk(self, sample_loan_request_data, security_context):
        """Test approval of a low-risk loan."""
        request = LoanRequest(**sample_loan_request_data)
        agent = LoanApprovalAgent(security_context=security_context)

        # Mock the vector store and LLM to avoid external dependencies
        decision = agent._make_decision(
            {
                "request": request,
                "decision": None,
                "risk_factors": [],
                "messages": [],
                "documents_checked": True,
                "security_context": security_context,
            }
        )

        assert decision["decision"] is not None
        assert decision["decision"].outcome == LoanOutcome.APPROVED
        assert decision["decision"].risk_score is not None
        assert decision["decision"].risk_score < 40

    def test_disapproved_high_risk_loan(self, high_risk_loan_request_data, security_context):
        """Test disapproval of a high-risk loan."""
        request = LoanRequest(**high_risk_loan_request_data)
        agent = LoanApprovalAgent(security_context=security_context)

        # Assess risk
        state = {
            "request": request,
            "decision": None,
            "risk_factors": [],
            "messages": [],
            "documents_checked": True,
            "security_context": security_context,
        }

        state = agent._assess_risk(state)
        state = agent._make_decision(state)

        assert state["decision"] is not None
        assert state["decision"].risk_score >= 40  # Should be high risk

    def test_missing_information_request(self, missing_info_loan_request_data, security_context):
        """Test handling of request with missing information."""
        request = LoanRequest(**missing_info_loan_request_data)
        agent = LoanApprovalAgent(security_context=security_context)

        state = {
            "request": request,
            "decision": None,
            "risk_factors": [],
            "messages": [],
            "documents_checked": False,
            "security_context": security_context,
        }

        state = agent._validate_request(state)

        assert state["decision"] is not None
        assert state["decision"].outcome == LoanOutcome.ADDITIONAL_INFO_NEEDED
        assert state["decision"].additional_info_required is not None
        assert "credit_score" in state["decision"].additional_info_required

    def test_risk_assessment_dti_ratio(self, sample_loan_request_data, security_context):
        """Test risk assessment considers DTI ratio."""
        # Modify to have high DTI
        sample_loan_request_data["existing_debts"] = 50000.0
        sample_loan_request_data["loan_amount"] = 300000.0
        sample_loan_request_data["annual_income"] = 60000.0

        request = LoanRequest(**sample_loan_request_data)
        agent = LoanApprovalAgent(security_context=security_context)

        state = {
            "request": request,
            "decision": None,
            "risk_factors": [],
            "messages": [],
            "documents_checked": True,
            "security_context": security_context,
        }

        state = agent._assess_risk(state)

        assert len(state["risk_factors"]) > 0
        assert any("debt-to-income" in factor.lower() for factor in state["risk_factors"])

    def test_risk_assessment_credit_score(self, sample_loan_request_data, security_context):
        """Test risk assessment considers credit score."""
        # Low credit score
        sample_loan_request_data["credit_score"] = 560

        request = LoanRequest(**sample_loan_request_data)
        agent = LoanApprovalAgent(security_context=security_context)

        state = {
            "request": request,
            "decision": None,
            "risk_factors": [],
            "messages": [],
            "documents_checked": True,
            "security_context": security_context,
        }

        state = agent._assess_risk(state)

        assert len(state["risk_factors"]) > 0
        assert any("credit score" in factor.lower() for factor in state["risk_factors"])

    def test_employment_stability_risk(self, sample_loan_request_data, security_context):
        """Test risk assessment for employment stability."""
        sample_loan_request_data["employment_status"] = "unemployed"

        request = LoanRequest(**sample_loan_request_data)
        agent = LoanApprovalAgent(security_context=security_context)

        state = {
            "request": request,
            "decision": None,
            "risk_factors": [],
            "messages": [],
            "documents_checked": True,
            "security_context": security_context,
        }

        state = agent._assess_risk(state)

        assert len(state["risk_factors"]) > 0
        assert any("unemployed" in factor.lower() for factor in state["risk_factors"])

    def test_loan_request_validation(self, sample_loan_request_data):
        """Test loan request model validation."""
        request = LoanRequest(**sample_loan_request_data)

        assert request.request_id == "REQ-TEST-001"
        assert request.annual_income == 75000.0
        assert request.loan_amount == 200000.0

    def test_loan_request_invalid_credit_score(self, sample_loan_request_data):
        """Test validation of invalid credit score."""
        sample_loan_request_data["credit_score"] = 900  # Invalid

        with pytest.raises(Exception):  # Pydantic validation error
            LoanRequest(**sample_loan_request_data)

    def test_loan_request_negative_income(self, sample_loan_request_data):
        """Test validation of negative income."""
        sample_loan_request_data["annual_income"] = -5000

        with pytest.raises(Exception):  # Pydantic validation error
            LoanRequest(**sample_loan_request_data)
