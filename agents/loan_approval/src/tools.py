"""Tools and utilities for loan approval agent."""

import json
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

    def _format_property_info(self, property_info: Any) -> str:
        """Format property information for display."""
        if not property_info:
            return "Not provided"

        return f"""- Address: {property_info.address or "Not provided"}
- Property Type: {property_info.property_type or "Not provided"}
- Appraised Value: ${property_info.appraised_value or 0:,.2f}
- Appraisal Date: {property_info.appraisal_date or "Not provided"}
- Comparable Sales: {property_info.comparable_sales or "Not provided"}
- Property Condition: {property_info.property_condition or "Not provided"}
- Inspection Completed: {property_info.inspection_completed or "Not provided"}
- Title Review: {property_info.title_review or "Not provided"}"""

    def _format_documentation_info(self, doc_info: Any) -> str:
        """Format documentation information for display."""
        if not doc_info:
            return "Not provided"

        pay_stubs = f"{doc_info.pay_stubs_verified or 'Not provided'}"
        pay_stubs += f" ({doc_info.pay_stubs_months or 0} months)"
        tax_returns = f"{doc_info.tax_returns_verified or 'Not provided'}"
        tax_returns += f" ({doc_info.tax_returns_years or 0} years)"
        w2_forms = f"{doc_info.w2_forms_verified or 'Not provided'}"
        w2_forms += f" ({doc_info.w2_years or 0} years)"
        bank_stmts = f"{doc_info.bank_statements_verified or 'Not provided'}"
        bank_stmts += f" ({doc_info.bank_statements_months or 0} months)"

        return f"""- Application Signed: {doc_info.application_signed or "Not provided"}
- Pay Stubs Verified: {pay_stubs}
- Tax Returns Verified: {tax_returns}
- W-2 Forms Verified: {w2_forms}
- Bank Statements Verified: {bank_stmts}
- Employment Verification: {doc_info.employment_verification or "Not provided"}
- Credit Reports: {doc_info.credit_reports or "Not provided"}
- Appraisal Report: {doc_info.appraisal_report or "Not provided"}
- Title Report: {doc_info.title_report or "Not provided"}"""

    def check_compliance(self, request: LoanRequest, risk_score: int) -> dict[str, Any]:
        """Check loan request compliance with policies.

        Args:
            request: Loan application request
            risk_score: Calculated risk score

        Returns:
            Dictionary with compliance result

        """
        logger.info("Checking policy compliance with LLM")

        # Calculate total assets
        total_assets = (
            (request.financial.checking_balance or 0)
            + (request.financial.savings_balance or 0)
            + (request.financial.investment_balance or 0)
        )

        # Format as readable text
        loan_summary = f"""
Loan Application Summary:

LOAN DETAILS:
- Amount: ${request.loan_details.amount:,.2f}
- Purpose: {request.loan_details.purpose.value}
- Term: {request.loan_details.term_months} months
- Property Value: ${request.loan_details.property_value or 0:,.2f}
- Down Payment: ${request.loan_details.down_payment or 0:,.2f}
- LTV Ratio: {request.loan_details.loan_to_value or "Not provided"}%
- Front-end DTI: {request.loan_details.front_end_dti or "Not provided"}%
- Back-end DTI: {request.loan_details.back_end_dti or "Not provided"}%

CREDIT HISTORY:
- Credit Score: {request.credit_history.credit_score}
- Risk Score: {risk_score}
- Credit Utilization: {request.credit_history.credit_utilization}%
- Payment History: {request.credit_history.payment_history or "Not provided"}
- Credit Mix: {request.credit_history.credit_mix or "Not provided"}
- Public Records: {request.credit_history.public_records or "Not provided"}

EMPLOYMENT:
- Status: {request.employment.status.value}
- Years Employed: {request.employment.years_employed or "N/A"}
- Industry: {request.employment.industry or "Not provided"}
- Industry Outlook: {request.employment.industry_outlook or "Not provided"}
- Monthly Income: ${request.employment.monthly_income:,.2f}

FINANCIAL:
- Monthly Debt Payments: ${request.financial.monthly_debt_payments:,.2f}
- Debt Breakdown: {request.financial.monthly_debt_breakdown or "Not provided"}
- Asset Reserves (months): {request.financial.asset_reserves_months or "Not calculated"}
- Total Assets: ${total_assets:,.2f}

PROPERTY INFORMATION:
{self._format_property_info(request.property)}

DOCUMENTATION:
{self._format_documentation_info(request.documentation)}
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
    "notes": "Detailed explanation of the decision (be thorough and complete)",
    "reason": "Specific reason if not compliant (empty if compliant)",
    "missing_information": ["list of any required information missing from the application"]
}}

Be strict in your evaluation and ensure all policy requirements are met.
If the application is missing required information, list all missing fields in \
the missing_information array.
Provide complete and detailed notes - do not truncate your explanation.
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

            logger.info(f"Policy check response: {result_text}")

            # Parse response - try JSON first, fallback to text parsing
            try:
                # Try to extract JSON from response (it might be wrapped in markdown)
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result_text[json_start:json_end]
                    parsed = json.loads(json_str)

                    if parsed.get("compliant", False):
                        return {
                            "compliant": True,
                            "notes": parsed.get("notes", "Application complies with all policies"),
                        }
                    # Not compliant - return detailed information
                    return {
                        "compliant": False,
                        "reason": parsed.get("reason", "Policy compliance check failed"),
                        "notes": parsed.get("notes", result_text),
                        "missing_information": parsed.get("missing_information", []),
                    }
            except (json.JSONDecodeError, ValueError):
                # Fallback to text parsing
                logger.warning("Could not parse JSON response, using text parsing")

            # Fallback text parsing
            if "true" in result_text.lower() and '"compliant": true' in result_text:
                return {
                    "compliant": True,
                    "notes": "Application complies with all policies",
                }

            # Extract reason from response
            reason = "Policy compliance check failed"
            missing_info = []

            if '"reason"' in result_text:
                try:
                    parts = result_text.split('"reason"')[1].split('"')
                    if len(parts) > 1:
                        reason = parts[1]
                except IndexError:
                    pass

            if '"missing_information"' in result_text:
                try:
                    # Extract the array portion
                    parts_str = result_text.split('"missing_information"')[1]
                    array_start = parts_str.find("[")
                    array_end = parts_str.find("]") + 1
                    if array_start >= 0 and array_end > array_start:
                        array_str = parts_str[array_start:array_end]
                        missing_info = json.loads(array_str)
                except (IndexError, json.JSONDecodeError):
                    pass

            return {
                "compliant": False,
                "reason": reason,
                "notes": result_text,  # Return full text, not truncated
                "missing_information": missing_info,
            }

        except Exception:
            logger.exception("Error in policy compliance check")
            # Re-raise the exception instead of silently returning compliant
            raise
