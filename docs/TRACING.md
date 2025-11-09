# MLflow Tracing for Loan Approval Agent

## Overview

The loan approval agent now includes comprehensive MLflow tracing to help you monitor and debug the entire loan approval workflow. Each step of the agent's decision-making process is tracked as a span within MLflow, providing detailed visibility into the agent's behavior.

## Features

### Trace Hierarchy

The tracing implementation creates a hierarchical view of the loan approval process:

```
loan_approval_workflow (CHAIN)
├── validate_input
├── check_basic_eligibility
├── calculate_risk
├── check_policies
└── make_decision
```

### Captured Information

#### Root Trace (loan_approval_workflow)
- **Attributes:**
  - `request_id`: Unique identifier for the loan request
  - `trace_id`: Internal trace identifier
  - `loan_amount`: Amount requested
  - `credit_score`: Applicant's credit score
  - `employment_status`: Employment status of applicant
  - `model_version`: Agent version

- **Outputs:**
  - `decision`: Final decision (APPROVED/DISAPPROVED/ADDITIONAL_INFO_NEEDED)
  - `risk_score`: Calculated risk score
  - `processing_time_ms`: Total processing time in milliseconds

#### Individual Spans

1. **validate_input**
   - Tracks input validation
   - Records request details and validation status

2. **check_basic_eligibility**
   - Logs credit score checks
   - Records DTI (Debt-to-Income) ratio calculations
   - Captures eligibility decisions and rejection reasons

3. **calculate_risk**
   - Records the calculated risk score
   - Shows risk assessment metrics

4. **check_policies**
   - Logs policy compliance checks
   - Records compliance status and any policy notes

5. **make_decision**
   - Captures final decision details
   - Records interest rates, monthly payments, and approval terms

## Viewing Traces in MLflow

### Local MLflow UI

1. Start the MLflow UI:
   ```bash
   cd agents/loan_approval/src
   mlflow ui --backend-store-uri ./mlruns
   ```

2. Open your browser to `http://localhost:5000`

3. Navigate to the "Traces" tab to view all traces

4. Click on a specific trace to see:
   - The complete trace hierarchy
   - Timing information for each span
   - All attributes and outputs
   - Any errors that occurred

### Trace Details

Each trace includes:
- **Timeline View**: Visual representation of span durations
- **Span Attributes**: Detailed metadata for each step
- **Input/Output**: Request and response data
- **Errors**: Any exceptions that occurred during processing

## Configuration

Tracing is controlled by the `enable_tracing` configuration option:

```python
# In .env file or environment variables
ENABLE_TRACING=true
```

## Integration with Existing Monitoring

The tracing feature integrates seamlessly with:
- **MLflow Runs**: Each trace is associated with an MLflow run
- **LangChain Autologging**: LLM calls are automatically logged
- **Metrics Tracking**: Performance metrics are recorded alongside traces

## Benefits

1. **Debugging**: Quickly identify which step in the workflow is causing issues
2. **Performance Analysis**: See exactly how long each step takes
3. **Audit Trail**: Complete record of all decision-making steps
4. **Model Comparison**: Compare behavior across different agent versions
5. **Production Monitoring**: Track agent behavior in production environments

## Example Trace

When processing a loan request, you'll see a trace like:

```
Trace: loan_approval_workflow (2.3s)
│
├─ validate_input (0.05s)
│  └─ request_id: REQ-001
│  └─ validation_passed: true
│
├─ check_basic_eligibility (0.1s)
│  └─ credit_score: 720
│  └─ dti_ratio: 0.35
│  └─ eligible: true
│
├─ calculate_risk (0.5s)
│  └─ risk_score: 25
│
├─ check_policies (1.5s)
│  └─ policy_compliant: true
│
└─ make_decision (0.15s)
   └─ decision: APPROVED
   └─ interest_rate: 5.75
   └─ monthly_payment: 1847.63
```

## Troubleshooting

If traces aren't appearing:

1. Verify `enable_tracing=true` in configuration
2. Check that MLflow is properly initialized
3. Ensure the MLflow tracking URI is correctly set
4. Check logs for any tracing-related errors

## Next Steps

- Explore the MLflow UI to familiarize yourself with the trace visualization
- Set up alerts based on trace metrics
- Integrate with Databricks for centralized trace storage
- Use traces to optimize agent performance
