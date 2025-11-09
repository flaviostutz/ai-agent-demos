# API Testing Examples

This directory contains sample requests and test scripts for the Loan Approval API.

## Quick Start

### 1. Start the API

```bash
# From the project root
make run
```

The API will be available at `http://localhost:8000`

### 2. Test with an Approved Request

#### Using Python Script:
```bash
# From the project root
uv run python examples/test_loan_api.py
```

#### Using Bash Script:
```bash
# From the project root
./agents/loan_approval/test_api.sh
```

#### Using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/loan/evaluate" \
  -H "Content-Type: application/json" \
  -d @agents/loan_approval/datasets/sample_approved_request.json
```

## Sample Request Details

The `sample_approved_request.json` file contains an application that should result in an **APPROVED** decision with the following characteristics:

- **Applicant**: Sarah Johnson
- **Credit Score**: 780 (Excellent)
- **Monthly Income**: $12,000 + $1,000 additional
- **DTI Ratio**: ~15% (healthy)
- **Loan Amount**: $400,000
- **Purpose**: Home Purchase
- **Down Payment**: $100,000 (20%)
- **Employment**: 5.5 years with current employer
- **No bankruptcies or foreclosures**
- **Strong financial profile**: $140,000 in liquid assets

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Evaluate Loan
```bash
POST /api/v1/loan/evaluate
Content-Type: application/json
```

### Get Metrics
```bash
curl http://localhost:8000/api/v1/metrics
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Expected Response Format

```json
{
  "request_id": "approved-001",
  "decision": {
    "decision": "approved",
    "risk_score": 25,
    "disapproval_reason": null,
    "additional_info_description": null,
    "recommended_amount": 400000,
    "recommended_term_months": 360,
    "interest_rate": 3.75,
    "monthly_payment": 1852.46
  },
  "processing_time_ms": 1234,
  "model_version": "0.1.0",
  "timestamp": "2025-11-09T12:00:00.000000",
  "agent_trace_id": "trace-id-here"
}
```

## Creating Custom Test Requests

To create your own test requests, use the following JSON structure:

```json
{
  "request_id": "unique-id",
  "applicant": {
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "ssn": "XXX-XX-XXXX",
    "email": "user@example.com",
    "phone": "+1XXXXXXXXXX",
    "address": "string",
    "city": "string",
    "state": "XX",
    "zip_code": "XXXXX"
  },
  "employment": {
    "status": "employed|self_employed|unemployed|retired|student",
    "employer_name": "string",
    "job_title": "string",
    "years_employed": 0.0,
    "monthly_income": 0.0,
    "additional_income": 0.0
  },
  "financial": {
    "monthly_debt_payments": 0.0,
    "checking_balance": 0.0,
    "savings_balance": 0.0,
    "investment_balance": 0.0,
    "has_bankruptcy": false,
    "bankruptcy_date": null,
    "has_foreclosure": false,
    "foreclosure_date": null
  },
  "credit_history": {
    "credit_score": 300-850,
    "number_of_credit_cards": 0,
    "total_credit_limit": 0.0,
    "credit_utilization": 0.0,
    "number_of_late_payments_12m": 0,
    "number_of_late_payments_24m": 0,
    "number_of_inquiries_6m": 0,
    "oldest_credit_line_years": 0.0
  },
  "loan_details": {
    "amount": 0.0,
    "purpose": "home_purchase|home_refinance|auto|personal|business|education|debt_consolidation",
    "term_months": 0,
    "property_value": 0.0,
    "down_payment": 0.0
  }
}
```

## Approval Criteria

For a loan to be approved, it typically needs to meet:

- **Credit Score**: ≥ 580 (configurable via `MIN_CREDIT_SCORE`)
- **DTI Ratio**: ≤ 43% (configurable via `MAX_DTI_RATIO`)
- **Employment**: ≥ 6 months (configurable via `MIN_EMPLOYMENT_MONTHS`)
- **Bankruptcy**: > 7 years ago (if any)
- **Foreclosure**: > 7 years ago (if any)
- **Policy Compliance**: Passes LLM-based policy check

Note: Configuration values can be adjusted in the `.env` file.
