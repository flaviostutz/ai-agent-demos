"""Unit tests for loan approval agent."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from agents.loan_approval.src.agent import LoanApprovalAgent
from agents.loan_approval.src.config import AgentConfig
from agents.loan_approval.src.tools import RiskCalculator
from shared.models.loan import (
    ApplicantInfo,
    CreditHistory,
    EmploymentInfo,
    EmploymentStatus,
    FinancialInfo,
    LoanDetails,
    LoanPurpose,
    LoanRequest,
)


@pytest.fixture
def sample_loan_request() -> LoanRequest:
    """Create a sample loan request for testing."""
    return LoanRequest(
        request_id="test-123",
        applicant=ApplicantInfo(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1985, 6, 15),
            ssn="123-45-6789",
            email="john.doe@email.com",
            phone="+15551234567",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
        ),
        employment=EmploymentInfo(
            status=EmploymentStatus.EMPLOYED,
            employer_name="Tech Corp",
            job_title="Engineer",
            years_employed=Decimal("5.0"),
            monthly_income=Decimal(8000),
            additional_income=Decimal(0),
        ),
        financial=FinancialInfo(
            monthly_debt_payments=Decimal(1500),
            checking_balance=Decimal(10000),
            savings_balance=Decimal(25000),
            has_bankruptcy=False,
            has_foreclosure=False,
        ),
        credit_history=CreditHistory(
            credit_score=720,
            number_of_credit_cards=3,
            total_credit_limit=Decimal(40000),
            credit_utilization=Decimal(30),
            number_of_late_payments_12m=0,
            number_of_late_payments_24m=0,
            number_of_inquiries_6m=1,
            oldest_credit_line_years=Decimal(10),
        ),
        loan_details=LoanDetails(
            amount=Decimal(300000),
            purpose=LoanPurpose.HOME_PURCHASE,
            term_months=360,
            property_value=Decimal(350000),
            down_payment=Decimal(50000),
        ),
    )


@pytest.fixture
def config() -> AgentConfig:
    """Create test configuration."""
    return AgentConfig(
        openai_api_key="test-key",
        environment="test",
        policies_directory="./policies",
    )


@pytest.fixture
def risk_calculator(config: AgentConfig) -> RiskCalculator:
    """Create risk calculator instance."""
    return RiskCalculator(config)


class TestRiskCalculator:
    """Tests for risk calculator."""

    def test_excellent_credit_low_risk(
        self, risk_calculator: RiskCalculator, sample_loan_request: LoanRequest
    ) -> None:
        """Test that excellent credit results in low risk score."""
        # Excellent credit score
        sample_loan_request.credit_history.credit_score = 800
        dti_ratio = 0.20

        risk_score = risk_calculator.calculate_risk_score(sample_loan_request, dti_ratio)

        assert 0 <= risk_score <= 30
        assert isinstance(risk_score, int)

    def test_poor_credit_high_risk(
        self, risk_calculator: RiskCalculator, sample_loan_request: LoanRequest
    ) -> None:
        """Test that poor credit results in high risk score."""
        # Poor credit score
        sample_loan_request.credit_history.credit_score = 580
        sample_loan_request.credit_history.number_of_late_payments_12m = 3
        sample_loan_request.credit_history.credit_utilization = Decimal(85)
        dti_ratio = 0.42

        risk_score = risk_calculator.calculate_risk_score(sample_loan_request, dti_ratio)

        assert risk_score >= 60
        assert risk_score <= 100

    def test_high_dti_increases_risk(
        self, risk_calculator: RiskCalculator, sample_loan_request: LoanRequest
    ) -> None:
        """Test that high DTI ratio increases risk score."""
        low_dti_score = risk_calculator.calculate_risk_score(sample_loan_request, 0.20)
        high_dti_score = risk_calculator.calculate_risk_score(sample_loan_request, 0.42)

        assert high_dti_score > low_dti_score

    def test_bankruptcy_increases_risk(
        self, risk_calculator: RiskCalculator, sample_loan_request: LoanRequest
    ) -> None:
        """Test that bankruptcy increases risk score."""
        sample_loan_request.financial.has_bankruptcy = True
        sample_loan_request.financial.bankruptcy_date = date(2022, 1, 1)
        dti_ratio = 0.30

        risk_score = risk_calculator.calculate_risk_score(sample_loan_request, dti_ratio)

        # Should have additional risk from recent bankruptcy
        assert risk_score > 40

    def test_late_payments_increase_risk(
        self, risk_calculator: RiskCalculator, sample_loan_request: LoanRequest
    ) -> None:
        """Test that late payments increase risk score."""
        no_late_score = risk_calculator.calculate_risk_score(sample_loan_request, 0.30)

        sample_loan_request.credit_history.number_of_late_payments_12m = 3
        with_late_score = risk_calculator.calculate_risk_score(sample_loan_request, 0.30)

        assert with_late_score > no_late_score

    def test_risk_score_bounded(
        self, risk_calculator: RiskCalculator, sample_loan_request: LoanRequest
    ) -> None:
        """Test that risk score is always between 0 and 100."""
        # Worst case scenario
        sample_loan_request.credit_history.credit_score = 300
        sample_loan_request.credit_history.number_of_late_payments_12m = 10
        sample_loan_request.credit_history.credit_utilization = Decimal(100)
        sample_loan_request.financial.has_bankruptcy = True
        sample_loan_request.financial.bankruptcy_date = date(2023, 1, 1)
        dti_ratio = 0.50

        risk_score = risk_calculator.calculate_risk_score(sample_loan_request, dti_ratio)

        assert 0 <= risk_score <= 100


class TestLoanRequestValidation:
    """Tests for loan request validation."""

    def test_valid_loan_request(self, sample_loan_request: LoanRequest) -> None:
        """Test that valid loan request passes validation."""
        # Should not raise any exceptions
        assert sample_loan_request.request_id == "test-123"
        assert sample_loan_request.applicant.first_name == "John"

    def test_invalid_ssn_format(self) -> None:
        """Test that invalid SSN format raises validation error."""
        with pytest.raises(ValidationError, match=r"String should match pattern"):
            ApplicantInfo(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1985, 6, 15),
                ssn="invalid",  # Invalid format
                email="john.doe@email.com",
                phone="+15551234567",
                address="123 Main St",
                city="Springfield",
                state="IL",
                zip_code="62701",
            )

    def test_underage_applicant(self) -> None:
        """Test that underage applicant raises validation error."""
        with pytest.raises(ValueError, match="at least 18 years old"):
            ApplicantInfo(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(2020, 1, 1),  # Too young
                ssn="123-45-6789",
                email="john.doe@email.com",
                phone="+15551234567",
                address="123 Main St",
                city="Springfield",
                state="IL",
                zip_code="62701",
            )

    def test_negative_income(self) -> None:
        """Test that negative income raises validation error."""
        with pytest.raises(ValueError, match=r"income|positive"):
            EmploymentInfo(
                status=EmploymentStatus.EMPLOYED,
                employer_name="Company",
                job_title="Job",
                years_employed=Decimal(1),
                monthly_income=Decimal(-1000),  # Negative
                additional_income=Decimal(0),
            )

    def test_credit_score_bounds(self) -> None:
        """Test that credit score must be within valid range."""
        # Too low
        with pytest.raises(ValueError, match=r"credit score|300|850"):
            CreditHistory(
                credit_score=250,  # Below 300
                number_of_credit_cards=1,
            )

        # Too high
        with pytest.raises(ValueError, match=r"credit score|300|850"):
            CreditHistory(
                credit_score=900,  # Above 850
                number_of_credit_cards=1,
            )


@pytest.mark.unit
class TestDataModels:
    """Tests for data model functionality."""

    def test_loan_request_serialization(self, sample_loan_request: LoanRequest) -> None:
        """Test that loan request can be serialized to JSON."""
        json_data = sample_loan_request.model_dump_json()
        assert isinstance(json_data, str)
        assert "test-123" in json_data

    def test_loan_request_deserialization(self, sample_loan_request: LoanRequest) -> None:
        """Test that loan request can be deserialized from JSON."""
        json_data = sample_loan_request.model_dump_json()
        reconstructed = LoanRequest.model_validate_json(json_data)
        assert reconstructed.request_id == sample_loan_request.request_id
        assert reconstructed.applicant.first_name == sample_loan_request.applicant.first_name


@pytest.mark.unit
class TestAgentHealthCheck:
    """Tests for agent health check functionality."""

    @patch("agents.loan_approval.src.agent.config")
    @patch("agents.loan_approval.src.agent.ChatOpenAI")
    @patch("agents.loan_approval.src.agent.PDFLoader")
    def test_health_check_success(
        self,
        mock_pdf_loader: MagicMock,
        mock_chat_openai: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test health check with successful LLM response."""
        # Configure mock config
        mock_config.use_azure_openai = False
        mock_config.openai_api_key = "test-key-123"
        mock_config.openai_model = "gpt-4"
        mock_config.openai_temperature = 0.0
        mock_config.policies_directory = "./policies"
        mock_config.mlflow_experiment_name = "test"
        mock_config.enable_llm_logging = False
        mock_config.agent_version = "0.1.0"
        mock_config.environment = "test"

        # Mock policy loading
        mock_pdf_loader.load_directory.return_value = "mock policy content"

        # Create mock LLM
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "OK"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        # Create agent
        agent = LoanApprovalAgent()

        # Perform health check
        health_status = agent.health_check()

        # Verify health status
        assert health_status["agent_initialized"] is True
        assert health_status["llm_responsive"] is True
        assert health_status["llm_configured"] is True
        assert health_status["workflow_ready"] is True
        assert "llm_response_time_ms" in health_status
        assert health_status["error"] is None

    @patch("agents.loan_approval.src.agent.config")
    @patch("agents.loan_approval.src.agent.ChatOpenAI")
    @patch("agents.loan_approval.src.agent.PDFLoader")
    def test_health_check_llm_failure(
        self,
        mock_pdf_loader: MagicMock,
        mock_chat_openai: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test health check with LLM failure."""
        # Configure mock config
        mock_config.use_azure_openai = False
        mock_config.openai_api_key = "test-key-123"
        mock_config.openai_model = "gpt-4"
        mock_config.openai_temperature = 0.0
        mock_config.policies_directory = "./policies"
        mock_config.mlflow_experiment_name = "test"
        mock_config.enable_llm_logging = False
        mock_config.agent_version = "0.1.0"
        mock_config.environment = "test"

        # Mock policy loading
        mock_pdf_loader.load_directory.return_value = "mock policy content"

        # Create mock LLM that raises an exception
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")
        mock_chat_openai.return_value = mock_llm

        # Create agent
        agent = LoanApprovalAgent()

        # Perform health check
        health_status = agent.health_check()

        # Verify health status shows error
        assert health_status["agent_initialized"] is True
        assert health_status["llm_responsive"] is False
        assert "LLM health check failed" in health_status["error"]

    @patch("agents.loan_approval.src.agent.config")
    @patch("agents.loan_approval.src.agent.ChatOpenAI")
    @patch("agents.loan_approval.src.agent.PDFLoader")
    def test_health_check_invalid_response(
        self,
        mock_pdf_loader: MagicMock,
        mock_chat_openai: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        """Test health check with invalid LLM response."""
        # Configure mock config
        mock_config.use_azure_openai = False
        mock_config.openai_api_key = "test-key-123"
        mock_config.openai_model = "gpt-4"
        mock_config.openai_temperature = 0.0
        mock_config.policies_directory = "./policies"
        mock_config.mlflow_experiment_name = "test"
        mock_config.enable_llm_logging = False
        mock_config.agent_version = "0.1.0"
        mock_config.environment = "test"

        # Mock policy loading
        mock_pdf_loader.load_directory.return_value = "mock policy content"

        # Create mock LLM with invalid response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = None
        mock_chat_openai.return_value = mock_llm

        # Create agent
        agent = LoanApprovalAgent()

        # Perform health check
        health_status = agent.health_check()

        # Verify health status shows error
        assert health_status["llm_responsive"] is False
        assert "LLM returned invalid response" in health_status["error"]
