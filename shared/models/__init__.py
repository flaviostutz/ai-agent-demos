"""Shared data models."""

from shared.models.loan import (
    LoanRequest,
    LoanOutcome,
    LoanDecision,
    ApplicantInfo,
    EmploymentInfo,
    FinancialInfo,
    LoanDetails,
    CreditHistory,
)

__all__ = [
    "LoanRequest",
    "LoanOutcome",
    "LoanDecision",
    "ApplicantInfo",
    "EmploymentInfo",
    "FinancialInfo",
    "LoanDetails",
    "CreditHistory",
]