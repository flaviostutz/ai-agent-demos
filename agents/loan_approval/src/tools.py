"""Tools and utilities for loan approval agent."""

from datetime import date, datetime, timezone
from typing import Any

from langchain_openai import AzureChatOpenAI, ChatOpenAI

from agents.loan_approval.src.config import AgentConfig
from shared.models.loan import LoanRequest
from shared.monitoring import get_logger

logger = get_logger(__name__)


class RiskCalculator:
    """Calculate risk scores for loan applications."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize risk calculator.

        Args:
            config: Agent configuration

        """
        self.config = config

    def calculate_risk_score(self, request: LoanRequest, dti_ratio: float) -> int:  # noqa: PLR0915
        """Calculate comprehensive risk score (0-100, where 100 is highest risk).

        Args:
            request: Loan application request
            dti_ratio: Debt-to-income ratio

        Returns:
            Risk score from 0 to 100

        """
        risk_score = 0.0

        # Credit score factor (0-30 points)
        credit_score = request.credit_history.credit_score
        if credit_score < 600:
            risk_score += 30
        elif credit_score < 650:
            risk_score += 25
        elif credit_score < 700:
            risk_score += 20
        elif credit_score < 750:
            risk_score += 15
        elif credit_score < 800:
            risk_score += 10
        else:
            risk_score += 5

        # DTI ratio factor (0-25 points)
        if dti_ratio > 0.40:
            risk_score += 25
        elif dti_ratio > 0.35:
            risk_score += 20
        elif dti_ratio > 0.30:
            risk_score += 15
        elif dti_ratio > 0.25:
            risk_score += 10
        else:
            risk_score += 5

        # Employment stability (0-15 points)
        if request.employment.years_employed:
            years = float(request.employment.years_employed)
            if years < 1:
                risk_score += 15
            elif years < 2:
                risk_score += 12
            elif years < 5:
                risk_score += 8
            else:
                risk_score += 3

        # Credit utilization (0-10 points)
        utilization = float(request.credit_history.credit_utilization)
        if utilization > 80:
            risk_score += 10
        elif utilization > 60:
            risk_score += 8
        elif utilization > 40:
            risk_score += 5
        elif utilization > 20:
            risk_score += 3

        # Late payments (0-10 points)
        late_12m = request.credit_history.number_of_late_payments_12m
        late_24m = request.credit_history.number_of_late_payments_24m
        if late_12m > 2:
            risk_score += 10
        elif late_12m > 0:
            risk_score += 7
        elif late_24m > 3:
            risk_score += 5

        # Bankruptcy/Foreclosure (0-10 points)
        if request.financial.has_bankruptcy:
            years_since = self._years_since(request.financial.bankruptcy_date)
            if years_since and years_since < 3:
                risk_score += 10
            elif years_since and years_since < 5:
                risk_score += 7
            elif years_since and years_since < 7:
                risk_score += 5

        if request.financial.has_foreclosure:
            years_since = self._years_since(request.financial.foreclosure_date)
            if years_since and years_since < 3:
                risk_score += 10
            elif years_since and years_since < 5:
                risk_score += 7
            elif years_since and years_since < 7:
                risk_score += 5

        # Loan to value ratio for home loans (0-10 points)
        if request.loan_details.property_value:
            ltv = float(request.loan_details.amount) / float(request.loan_details.property_value)
            if ltv > 0.95:
                risk_score += 10
            elif ltv > 0.90:
                risk_score += 8
            elif ltv > 0.85:
                risk_score += 6
            elif ltv > 0.80:
                risk_score += 4

        # Cap at 100
        final_score = min(int(risk_score), 100)
        logger.info(f"Calculated risk score: {final_score}")
        return final_score

    def _years_since(self, past_date: date | None) -> float | None:
        """Calculate years since a past date."""
        if not past_date:
            return None
        delta = datetime.now(tz=timezone.utc).date() - past_date
        return delta.days / 365.25


class PolicyChecker:
    """Check loan applications against policy documents."""

    def __init__(self, llm: ChatOpenAI | AzureChatOpenAI, policy_content: str) -> None:
        """Initialize policy checker.

        Args:
            llm: Language model for policy analysis (supports OpenAI or Azure OpenAI)
            policy_content: Loaded policy document content

        """
        self.llm = llm
        self.policy_content = policy_content

    def check_compliance(self, request: LoanRequest, risk_score: int) -> dict[str, Any]:
        """Check loan request compliance with policies.

        Args:
            request: Loan application request
            risk_score: Calculated risk score

        Returns:
            Dictionary with compliance result

        """
        logger.info("Checking policy compliance with LLM")

        # Prepare loan summary for LLM
        loan_summary = f"""
Loan Application Summary:
- Amount: ${request.loan_details.amount:,.2f}
- Purpose: {request.loan_details.purpose.value}
- Term: {request.loan_details.term_months} months
- Credit Score: {request.credit_history.credit_score}
- Risk Score: {risk_score}
- Employment Status: {request.employment.status.value}
- Monthly Income: ${request.employment.monthly_income:,.2f}
- Has Bankruptcy: {request.financial.has_bankruptcy}
- Has Foreclosure: {request.financial.has_foreclosure}
"""

        prompt = f"""You are a loan policy compliance expert. Review the following loan \
application against the provided policy documents and determine if it complies with all policies.

POLICY DOCUMENTS:
{self.policy_content[:3000]}  # Truncate for token limits

LOAN APPLICATION:
{loan_summary}

Analyze this application and respond in the following JSON format:
{{
    "compliant": true/false,
    "notes": "Brief explanation of the decision",
    "reason": "Specific reason if not compliant (empty if compliant)"
}}

Be strict in your evaluation and ensure all policy requirements are met.
"""

        try:
            # LLM invocation - callbacks configured in the LLM instance will automatically
            # log prompts, responses, tokens, and timing to MLflow and logs
            response = self.llm.invoke(prompt)
            result_text = response.content

            # Ensure result_text is a string for processing
            if isinstance(result_text, list):
                result_text = " ".join(str(item) for item in result_text)
            else:
                result_text = str(result_text)

            # Parse response (simplified - in production use more robust parsing)
            if "true" in result_text.lower() and '"compliant": true' in result_text:
                return {
                    "compliant": True,
                    "notes": "Application complies with all policies",
                }
            # Extract reason from response
            reason = "Policy compliance check failed"
            if "reason" in result_text.lower():
                # Simple extraction - in production use JSON parsing
                parts = result_text.split('"reason"')
                if len(parts) > 1:
                    parts[1].split('"')[1] if '"' in parts[1] else reason

            return {
                "compliant": False,
                "reason": reason,
                "notes": result_text[:200],
            }

        except Exception:
            logger.exception("Error in policy compliance check")
            # Re-raise the exception instead of silently returning compliant
            raise
