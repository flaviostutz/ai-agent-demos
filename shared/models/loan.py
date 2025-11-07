"""Loan request and response data models."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, validator


class EmploymentStatus(str, Enum):
    """Employment status options."""

    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"


class LoanPurpose(str, Enum):
    """Loan purpose options."""

    HOME_PURCHASE = "home_purchase"
    HOME_REFINANCE = "home_refinance"
    AUTO = "auto"
    PERSONAL = "personal"
    BUSINESS = "business"
    EDUCATION = "education"
    DEBT_CONSOLIDATION = "debt_consolidation"


class DecisionType(str, Enum):
    """Loan decision types."""

    APPROVED = "approved"
    DISAPPROVED = "disapproved"
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"


class ApplicantInfo(BaseModel):
    """Applicant personal information."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    ssn: str = Field(..., pattern=r"^\d{3}-\d{2}-\d{4}$")
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    phone: str = Field(..., pattern=r"^\+?1?\d{10,15}$")
    address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")

    @validator("date_of_birth")
    def validate_age(cls, v: date) -> date:
        """Validate applicant is at least 18 years old."""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Applicant must be at least 18 years old")
        if age > 100:
            raise ValueError("Invalid date of birth")
        return v


class EmploymentInfo(BaseModel):
    """Employment information."""

    status: EmploymentStatus
    employer_name: str | None = Field(None, max_length=200)
    job_title: str | None = Field(None, max_length=100)
    years_employed: Decimal | None = Field(None, ge=0, le=60)
    monthly_income: Decimal = Field(..., gt=0, le=1000000)
    additional_income: Decimal | None = Field(default=Decimal(0), ge=0, le=1000000)

    @validator("employer_name", "job_title")
    def validate_employment_details(cls, v: str | None, values: dict) -> str | None:
        """Validate employment details are provided for employed applicants."""
        if values.get("status") in [EmploymentStatus.EMPLOYED, EmploymentStatus.SELF_EMPLOYED]:
            if not v:
                raise ValueError("Employer name and job title required for employed applicants")
        return v


class FinancialInfo(BaseModel):
    """Financial information."""

    monthly_debt_payments: Decimal = Field(default=Decimal(0), ge=0, le=1000000)
    checking_balance: Decimal | None = Field(None, ge=0)
    savings_balance: Decimal | None = Field(None, ge=0)
    investment_balance: Decimal | None = Field(None, ge=0)
    has_bankruptcy: bool = Field(default=False)
    bankruptcy_date: date | None = None
    has_foreclosure: bool = Field(default=False)
    foreclosure_date: date | None = None

    @validator("bankruptcy_date")
    def validate_bankruptcy_date(cls, v: date | None, values: dict) -> date | None:
        """Validate bankruptcy date if bankruptcy exists."""
        if values.get("has_bankruptcy") and not v:
            raise ValueError("Bankruptcy date required when has_bankruptcy is True")
        return v

    @validator("foreclosure_date")
    def validate_foreclosure_date(cls, v: date | None, values: dict) -> date | None:
        """Validate foreclosure date if foreclosure exists."""
        if values.get("has_foreclosure") and not v:
            raise ValueError("Foreclosure date required when has_foreclosure is True")
        return v


class CreditHistory(BaseModel):
    """Credit history information."""

    credit_score: int = Field(..., ge=300, le=850)
    number_of_credit_cards: int = Field(default=0, ge=0, le=50)
    total_credit_limit: Decimal = Field(default=Decimal(0), ge=0)
    credit_utilization: Decimal = Field(default=Decimal(0), ge=0, le=100)
    number_of_late_payments_12m: int = Field(default=0, ge=0)
    number_of_late_payments_24m: int = Field(default=0, ge=0)
    number_of_inquiries_6m: int = Field(default=0, ge=0)
    oldest_credit_line_years: Decimal | None = Field(None, ge=0, le=80)


class LoanDetails(BaseModel):
    """Loan request details."""

    amount: Decimal = Field(..., gt=0, le=10000000)
    purpose: LoanPurpose
    term_months: int = Field(..., gt=0, le=360)
    property_value: Decimal | None = Field(None, gt=0)
    down_payment: Decimal | None = Field(default=Decimal(0), ge=0)

    @validator("property_value")
    def validate_property_value(cls, v: Decimal | None, values: dict) -> Decimal | None:
        """Validate property value for home loans."""
        purpose = values.get("purpose")
        if purpose in [LoanPurpose.HOME_PURCHASE, LoanPurpose.HOME_REFINANCE]:
            if not v or v <= 0:
                raise ValueError("Property value required for home loans")
        return v

    @validator("down_payment")
    def validate_down_payment(cls, v: Decimal | None, values: dict) -> Decimal | None:
        """Validate down payment doesn't exceed loan amount."""
        if v and values.get("amount") and v >= values["amount"]:
            raise ValueError("Down payment must be less than loan amount")
        return v


class LoanRequest(BaseModel):
    """Complete loan application request."""

    request_id: str = Field(..., min_length=1)
    applicant: ApplicantInfo
    employment: EmploymentInfo
    financial: FinancialInfo
    credit_history: CreditHistory
    loan_details: LoanDetails
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        }


class LoanDecision(BaseModel):
    """Loan decision details."""

    decision: DecisionType
    risk_score: int | None = Field(None, ge=0, le=100)
    disapproval_reason: str | None = None
    additional_info_description: str | None = None
    recommended_amount: Decimal | None = Field(None, gt=0)
    recommended_term_months: int | None = Field(None, gt=0, le=360)
    interest_rate: Decimal | None = Field(None, ge=0, le=100)
    monthly_payment: Decimal | None = Field(None, gt=0)

    @validator("risk_score")
    def validate_risk_score_for_approval(cls, v: int | None, values: dict) -> int | None:
        """Validate risk score is provided for approved decisions."""
        if values.get("decision") == DecisionType.APPROVED and v is None:
            raise ValueError("Risk score required for approved loans")
        return v

    @validator("disapproval_reason")
    def validate_disapproval_reason(cls, v: str | None, values: dict) -> str | None:
        """Validate disapproval reason is provided for disapproved decisions."""
        if values.get("decision") == DecisionType.DISAPPROVED and not v:
            raise ValueError("Disapproval reason required for disapproved loans")
        return v

    @validator("additional_info_description")
    def validate_additional_info(cls, v: str | None, values: dict) -> str | None:
        """Validate additional info description is provided when needed."""
        if values.get("decision") == DecisionType.ADDITIONAL_INFO_NEEDED and not v:
            raise ValueError(
                "Additional info description required for additional_info_needed decisions"
            )
        return v


class LoanOutcome(BaseModel):
    """Complete loan application outcome."""

    request_id: str
    decision: LoanDecision
    processing_time_ms: int = Field(..., ge=0)
    model_version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_trace_id: str | None = None

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        }
