# Quick Reference: Viewing LLM Logs

## Start the Agent with LLM Debug Logging

The `make run` command automatically enables comprehensive LLM debug logging:

```bash
make run
```

This sets:
- `ENABLE_LLM_LOGGING=true` - Master switch for LLM logging
- `LOG_LLM_PROMPTS=true` - Log all prompts sent to LLM
- `LOG_LLM_RESPONSES=true` - Log all LLM responses
- `MLFLOW_LOG_LLM_MODELS=true` - Log model configurations
- `MLFLOW_LOG_LLM_INPUTS_OUTPUTS=true` - Log I/O to MLflow
- `LOG_LEVEL=DEBUG` - Enable debug-level logs

## View LLM Logs in Real-Time

### 1. Console Output

When running locally, you'll see detailed LLM logs in the terminal:

```
INFO - LLM call #1 started
INFO - LLM Model: gpt-4
DEBUG - LLM Prompt #1:
You are a loan policy compliance expert...

INFO - LLM call #1 completed in 2.345s
INFO - LLM tokens - Total: 1234, Prompt: 890, Completion: 344
DEBUG - LLM Response #1:
{"compliant": true, "notes": "Application complies with all policies"}
```

### 2. MLflow UI

**Start MLflow UI** (in a separate terminal):

```bash
cd agents/loan_approval/src
mlflow ui --port 5000
```

**Open browser**:
```bash
open http://localhost:5000
```

**Navigate to**:
1. Click on the latest run
2. View **Metrics** tab for token usage and latency
3. View **Parameters** tab for model configuration
4. View **Artifacts** tab for full prompts and responses

### 3. MLflow Artifacts Structure

```
mlruns/
└── <experiment_id>/
    └── <run_id>/
        ├── metrics/
        │   ├── llm_call_1_latency_sec
        │   ├── llm_call_1_total_tokens
        │   ├── llm_call_1_prompt_tokens
        │   └── llm_call_1_completion_tokens
        ├── params/
        │   └── llm_call_1_model
        └── artifacts/
            ├── prompts/
            │   ├── llm_call_1_prompt_1.txt
            │   └── llm_call_2_prompt_1.txt
            └── responses/
                ├── llm_call_1_response_1_1.txt
                └── llm_call_2_response_1_1.txt
```

## Test LLM Logging

### Quick Test

```bash
# 1. Start the agent
make run

# 2. In another terminal, send a test request
curl -X POST http://localhost:8000/api/v1/loan/evaluate \
  -H "Content-Type: application/json" \
  -d @agents/loan_approval/datasets/test_request.json

# 3. Check logs in the agent terminal
# 4. View in MLflow UI at http://localhost:5000
```

### Run Demo Script

```bash
# Automated demo with detailed logging
python examples/llm_logging_demo.py

# Then view results in MLflow UI
cd agents/loan_approval/src
mlflow ui --port 5000
```

## What Gets Logged

| Data | Console | MLflow Metrics | MLflow Artifacts |
|------|---------|----------------|------------------|
| Prompts | ✅ (DEBUG) | ❌ | ✅ |
| Responses | ✅ (DEBUG) | ❌ | ✅ |
| Token Usage | ✅ (INFO) | ✅ | ❌ |
| Latency | ✅ (INFO) | ✅ | ❌ |
| Model Name | ✅ (INFO) | ✅ (params) | ❌ |
| Errors | ✅ (ERROR) | ✅ (params) | ❌ |

## Filter Logs

### See Only LLM Logs

```bash
make run 2>&1 | grep -E "LLM|llm_call"
```

### Monitor Token Usage

```bash
make run 2>&1 | grep "tokens"
```

### Track Latency

```bash
make run 2>&1 | grep "completed in"
```

## Query MLflow Programmatically

```python
import mlflow

# Get latest run
client = mlflow.tracking.MlflowClient()
experiment = client.get_experiment_by_name("loan-approval-agent")
runs = client.search_runs(experiment.experiment_id, order_by=["start_time DESC"], max_results=1)

if runs:
    run = runs[0]
    
    # Get metrics
    print(f"Total tokens: {run.data.metrics.get('llm_call_1_total_tokens', 'N/A')}")
    print(f"Latency: {run.data.metrics.get('llm_call_1_latency_sec', 'N/A')}s")
    
    # Get parameters
    print(f"Model: {run.data.params.get('llm_call_1_model', 'N/A')}")
    
    # Get artifacts
    artifact_uri = run.info.artifact_uri
    print(f"Artifacts: {artifact_uri}")
```

## Disable LLM Logging (Production)

To disable for production (e.g., to protect PII):

```bash
# Edit .env file
ENABLE_LLM_LOGGING=false

# Or selectively disable prompts only
ENABLE_LLM_LOGGING=true
LOG_LLM_PROMPTS=false  # Don't log prompts with PII
LOG_LLM_RESPONSES=true # Still log responses
```

## Troubleshooting

### LLM logs not appearing

**Check**:
1. `ENABLE_LLM_LOGGING=true` in your .env
2. `LOG_LEVEL=DEBUG` to see detailed logs
3. Agent is processing requests (logs only appear on LLM calls)

### MLflow artifacts not saved

**Check**:
1. MLflow tracking URI is configured correctly
2. `mlruns/` directory has write permissions
3. Running within an MLflow run context

### Too much log output

**Adjust log level**:
```bash
# Edit .env
LOG_LEVEL=INFO  # Less verbose than DEBUG

# Or disable prompt/response logging
LOG_LLM_PROMPTS=false
LOG_LLM_RESPONSES=false
```

## Complete Documentation

For detailed information, see:
- **[docs/LLM_LOGGING.md](LLM_LOGGING.md)** - Complete implementation guide
- **[examples/llm_logging_demo.py](../examples/llm_logging_demo.py)** - Working example
