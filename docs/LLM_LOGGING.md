# LLM Interaction Logging

This document describes the comprehensive LLM interaction logging system implemented using MLflow and LangChain built-in capabilities.

## Overview

All LLM interactions in the loan approval agent are now automatically logged with detailed telemetry including:

- **Prompts**: Full input prompts sent to the LLM
- **Responses**: Complete LLM responses
- **Token Usage**: Prompt tokens, completion tokens, and total tokens
- **Latency**: Time taken for each LLM call
- **Model Configuration**: Model name, temperature, and other parameters
- **Error Tracking**: Any errors during LLM invocations

## Implementation

### 1. MLflow LangChain Autologging

MLflow's built-in LangChain autologging is enabled automatically when the agent initializes:

```python
mlflow.langchain.autolog(
    log_models=True,
    log_input_examples=True,
    log_model_signatures=True,
    log_inputs_outputs=True,
)
```

This captures:
- Model artifacts and configurations
- Input/output examples
- Model signatures
- All prompts and responses

### 2. Custom LLM Callback Handler

A custom `LLMCallbackHandler` provides detailed logging with granular control:

**Location**: `shared/monitoring/llm_logger.py`

**Features**:
- Logs every LLM call start/end
- Tracks token usage per call
- Records latency metrics
- Saves prompts and responses to MLflow artifacts
- Logs errors with full context

**Usage**:
```python
from shared.monitoring import get_llm_callback_handler

callback = get_llm_callback_handler(
    log_prompts=True,      # Log input prompts
    log_responses=True     # Log LLM responses
)

llm = ChatOpenAI(
    model="gpt-4",
    callbacks=[callback]
)
```

### 3. Configuration Options

Control LLM logging via environment variables or configuration:

**In `agents/loan_approval/src/config.py`**:

```python
# LLM Logging
enable_llm_logging: bool = True                    # Master switch
log_llm_prompts: bool = True                       # Log prompts (may contain sensitive data)
log_llm_responses: bool = True                     # Log responses
mlflow_log_llm_models: bool = True                 # Log model artifacts
mlflow_log_llm_inputs_outputs: bool = True         # Log inputs/outputs
```

**Environment Variables**:
```bash
ENABLE_LLM_LOGGING=true
LOG_LLM_PROMPTS=true          # Set to false in production if prompts contain PII
LOG_LLM_RESPONSES=true
MLFLOW_LOG_LLM_MODELS=true
MLFLOW_LOG_LLM_INPUTS_OUTPUTS=true
```

## What Gets Logged

### Standard Logs (Python Logger)

```
INFO - LLM call #1 started
INFO - LLM Model: gpt-4
DEBUG - LLM Prompt #1:
You are a loan policy compliance expert...

INFO - LLM call #1 completed in 2.345s
INFO - LLM tokens - Total: 1234, Prompt: 890, Completion: 344
DEBUG - LLM Response #1:
{"compliant": true, "notes": "..."}
```

### MLflow Artifacts

Each LLM call creates the following artifacts in MLflow:

```
prompts/
  llm_call_1_prompt_1.txt       # Input prompt
  llm_call_2_prompt_1.txt
  ...

responses/
  llm_call_1_response_1_1.txt   # LLM response
  llm_call_2_response_1_1.txt
  ...
```

### MLflow Metrics

Per LLM call:
```
llm_call_1_latency_sec: 2.345
llm_call_1_total_tokens: 1234
llm_call_1_prompt_tokens: 890
llm_call_1_completion_tokens: 344
```

### MLflow Parameters

```
llm_call_1_model: gpt-4
llm_call_2_model: gpt-4
...
```

## Integration Points

### LoanApprovalAgent

The agent automatically configures LLM logging on initialization:

```python
# agents/loan_approval/src/agent.py
def __init__(self, ...):
    # Enable MLflow autologging
    if self.config.enable_llm_logging:
        setup_mlflow_langchain_autologging(...)
    
    # Create callback handler
    self.llm_callback = get_llm_callback_handler(
        log_prompts=self.config.log_llm_prompts,
        log_responses=self.config.log_llm_responses,
    )
    
    # Initialize LLM with callbacks
    self.llm = ChatOpenAI(
        model=config.openai_model,
        callbacks=[self.llm_callback],
    )
```

### PolicyChecker

The PolicyChecker uses the LLM instance with callbacks already configured:

```python
# agents/loan_approval/src/tools.py
class PolicyChecker:
    def check_compliance(self, request, risk_score):
        # LLM invocation automatically logs via callbacks
        response = self.llm.invoke(prompt)
```

## Viewing Logs

### 1. Local MLflow UI

Start the MLflow UI to view logged runs:

```bash
cd agents/loan_approval/src
mlflow ui --port 5000
```

Navigate to http://localhost:5000 to see:
- All experiment runs
- Metrics (tokens, latency)
- Parameters (model configuration)
- Artifacts (prompts, responses)

### 2. Python Logs

Standard application logs show LLM interactions:

```bash
# View logs in real-time
tail -f app.log

# Or check terminal output
```

### 3. Databricks (if configured)

If `MLFLOW_TRACKING_URI` points to Databricks:
- Logs appear in Databricks Mosaic AI
- Use Databricks ML workspace to explore runs
- Query logs using Databricks SQL

## Privacy and Security Considerations

### Sensitive Data in Prompts

LLM prompts may contain:
- Customer PII (names, addresses, SSN)
- Financial information (income, debts)
- Credit scores and history

**Recommendations**:
1. **Production**: Set `LOG_LLM_PROMPTS=false` to disable prompt logging
2. **Development**: Use `LOG_LLM_PROMPTS=true` for debugging
3. **Access Control**: Restrict MLflow UI access to authorized personnel
4. **Data Masking**: Consider implementing PII masking before logging

### Configuration Examples

**Development Environment**:
```bash
ENABLE_LLM_LOGGING=true
LOG_LLM_PROMPTS=true
LOG_LLM_RESPONSES=true
```

**Production Environment**:
```bash
ENABLE_LLM_LOGGING=true
LOG_LLM_PROMPTS=false        # Disable to protect PII
LOG_LLM_RESPONSES=true       # Responses less sensitive
```

## Cost Tracking

Token usage logs enable cost tracking:

```python
# Query total tokens from MLflow
import mlflow

client = mlflow.tracking.MlflowClient()
experiment = client.get_experiment_by_name("loan-approval-agent")
runs = client.search_runs(experiment.experiment_id)

total_tokens = sum(
    run.data.metrics.get(f"llm_call_{i}_total_tokens", 0)
    for run in runs
    for i in range(100)  # Adjust based on max calls
)

# Calculate cost (example: GPT-4 pricing)
cost = (total_tokens / 1000) * 0.03  # $0.03 per 1K tokens
print(f"Total LLM cost: ${cost:.2f}")
```

## Troubleshooting

### LLM calls not logged

**Check**:
1. `ENABLE_LLM_LOGGING=true` is set
2. MLflow experiment is initialized
3. Callbacks are attached to LLM instance

**Debug**:
```python
# Verify callback is active
assert agent.llm_callback is not None
assert agent.llm.callbacks is not None
```

### Missing token metrics

**Reason**: Token usage only available for OpenAI models

**Solution**: Ensure using OpenAI API, not local models

### MLflow artifacts not saved

**Check**:
1. MLflow tracking URI is configured
2. Write permissions on mlruns directory
3. Active MLflow run context

**Debug**:
```python
import mlflow
print(mlflow.get_tracking_uri())
print(mlflow.active_run())  # Should not be None during execution
```

## Best Practices

1. **Always enable logging in development** for debugging
2. **Carefully control prompt logging in production** due to PII
3. **Monitor token usage** to control API costs
4. **Set up alerts** on MLflow metrics for anomalies
5. **Regularly archive** old MLflow runs to save storage
6. **Use sampling** in high-volume scenarios to reduce overhead

## Example Usage

```python
from agents.loan_approval.src.agent import LoanApprovalAgent
from agents.loan_approval.src.config import config
from shared.models.loan import LoanRequest

# Initialize agent (LLM logging enabled automatically)
agent = LoanApprovalAgent()

# Process loan - all LLM calls automatically logged
with agent.metrics_tracker.start_run(run_name="loan-12345"):
    result = agent.process_loan(loan_request)

# View logs in MLflow UI
# mlflow ui --port 5000
```

## References

- [MLflow LangChain Integration](https://mlflow.org/docs/latest/llms/langchain/index.html)
- [LangChain Callbacks](https://python.langchain.com/docs/modules/callbacks/)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
