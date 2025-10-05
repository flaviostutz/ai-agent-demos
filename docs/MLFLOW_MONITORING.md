# MLFlow & Databricks Monitoring Guide

## Overview

This project uses **MLFlow** and **Databricks** for comprehensive agent monitoring, experiment tracking, and model evaluation. Prometheus has been replaced with MLFlow's native tracking capabilities for better integration with the Databricks/Mosaic AI platform.

## Features

### 1. **MLFlow Metrics Tracking**
All agent metrics are logged to MLFlow instead of Prometheus:
- Request counts and status
- Latency measurements (avg, p95, p99)
- Error rates and types
- Token usage per model
- Risk scores and decisions

### 2. **Experiment Tracking**
Every agent run can be tracked as an MLFlow experiment:
- Automatic experiment creation per agent
- Run grouping and comparison
- Parameter logging (request details, model config)
- Artifact storage (decision logs, documents)

### 3. **Dataset Management**
Evaluation datasets are versioned and tracked in MLFlow:
- Dataset versioning with metadata
- Automatic schema validation
- Train/test splits with reproducibility
- Dataset lineage tracking

### 4. **Automated Model Evaluation**
Comprehensive evaluation framework with:
- **Classification Metrics**: Accuracy, precision, recall, F1-score
- **Performance Metrics**: Latency (avg, p95, p99), throughput
- **Cost Metrics**: Token usage, API costs
- **Drift Detection**: Automatic performance degradation alerts

### 5. **Model Registry Integration**
Register and manage agent versions:
- Semantic versioning
- Stage transitions (Staging → Production)
- Model lineage and comparison
- Rollback capabilities

## Architecture

```
┌─────────────────┐
│  Loan Agent API │
│                 │
│  ┌───────────┐ │      ┌──────────────────┐
│  │ Agent     │ │────▶ │  MLFlow Tracking │
│  │ Execution │ │      │                  │
│  └───────────┘ │      │ - Metrics        │
│                 │      │ - Parameters     │
│  ┌───────────┐ │      │ - Artifacts      │
│  │ Metrics   │ │────▶ │ - Models         │
│  │ Collector │ │      │ - Datasets       │
│  └───────────┘ │      └──────────────────┘
└─────────────────┘               │
                                  ▼
                        ┌──────────────────┐
                        │  Databricks      │
                        │  Workspace       │
                        │                  │
                        │ - Experiments    │
                        │ - Model Registry │
                        │ - Mosaic AI      │
                        └──────────────────┘
```

## Quick Start

### 1. Set Up MLFlow

```bash
# Set Databricks connection
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-token"

# Or use local MLFlow server
export MLFLOW_TRACKING_URI="http://localhost:5000"
```

### 2. Run Agent with Tracking

```python
from shared.mlflow_tracking import AgentTracker

# Initialize tracker
tracker = AgentTracker("loan_approval")

# Start a run
run_id = tracker.start_run(
    run_name="loan_eval_batch",
    tags={"environment": "production"}
)

# Log metrics during execution
tracker.log_metrics({
    "accuracy": 0.95,
    "avg_latency_ms": 250.5
})

# Log parameters
tracker.log_params({
    "model": "gpt-4",
    "temperature": 0.0
})

# End run
tracker.end_run()
```

### 3. Run Automated Evaluation

```bash
# Evaluate on test dataset
make evaluate

# Or manually:
python scripts/evaluate_agent.py \
    --agent loan_approval \
    --dataset loan_approval_test_set

# Check for drift
python scripts/evaluate_agent.py \
    --agent loan_approval \
    --dataset current_data \
    --drift-detection \
    --baseline-dataset baseline_data
```

### 4. API Evaluation Endpoint

```bash
# Trigger evaluation via API
curl -X POST http://localhost:8000/api/v1/loan/evaluate_dataset \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "dataset_name": "loan_approval_test_set",
    "target_field": "expected_outcome"
  }'
```

## Key Components

### Shared Libraries

#### `shared/metrics.py`
MLFlow-based metrics collector:
```python
from shared.metrics import get_metrics_collector

collector = get_metrics_collector("loan_approval", run_id="optional_run_id")

# Record metrics
collector.record_request(status="approved")
collector.record_duration(duration=125.5)
collector.record_token_usage(model="gpt-4", tokens=500)
collector.record_error(error_type="ValidationError")

# Get summary
summary = collector.get_summary()
```

#### `shared/mlflow_tracking.py`
Comprehensive MLFlow integration:
```python
from shared.mlflow_tracking import AgentTracker

tracker = AgentTracker("loan_approval")
tracker.start_run()

# Log individual request
tracker.log_request(
    request_id="req_123",
    request_data={"loan_amount": 250000},
    decision_data={"outcome": "approved", "risk_score": 25},
    duration_ms=150.2
)

# Log dataset
import pandas as pd
df = pd.DataFrame([...])
tracker.log_dataset(df, name="evaluation_set", targets="outcome")

# Log evaluation results
tracker.log_evaluation_results(
    eval_results={"accuracy": 0.95, "f1_score": 0.93},
    dataset_name="test_set"
)

# Log model
tracker.log_model(
    model=agent_model,
    artifact_path="models",
    registered_model_name="loan_approval_v1"
)

tracker.end_run()
```

#### `shared/datasets.py`
Dataset management:
```python
from shared.datasets import DatasetManager

manager = DatasetManager(base_path="data/evaluation")

# Load dataset
data = manager.load_dataset("loan_approval_test_set")

# Save dataset with metadata
manager.save_dataset(
    dataset=data,
    dataset_name="new_test_set",
    description="Test set for Q4 2025",
    version="1.0",
    tags={"quarter": "Q4", "year": "2025"}
)

# Log to MLFlow
manager.log_dataset_to_mlflow(
    dataset_name="loan_approval_test_set",
    context="evaluation"
)

# Split dataset
train_df, test_df = manager.split_dataset(
    dataset_name="full_dataset",
    train_ratio=0.8,
    save=True
)
```

#### `shared/model_evaluation.py`
Automated evaluation framework:
```python
from shared.model_evaluation import ModelEvaluator

def agent_wrapper(request: dict) -> dict:
    # Your agent logic
    return {"outcome": "approved", "risk_score": 25}

evaluator = ModelEvaluator(
    agent_name="loan_approval",
    agent_func=agent_wrapper
)

# Evaluate on dataset
metrics = evaluator.evaluate_dataset(
    dataset_name="test_set",
    target_field="expected_outcome",
    log_to_mlflow=True
)

print(f"Accuracy: {metrics.accuracy:.3f}")
print(f"Avg Latency: {metrics.avg_latency_ms:.2f}ms")

# Detect drift
drift_results = evaluator.detect_drift(
    baseline_dataset="baseline_v1",
    current_dataset="current_month",
    threshold=0.05  # 5% degradation threshold
)

if drift_results["has_drift"]:
    print("⚠️ Performance drift detected!")
```

## Evaluation Datasets

### Structure
```json
[
  {
    "request_id": "eval_001",
    "applicant_name": "John Doe",
    "annual_income": 85000,
    "credit_score": 750,
    "loan_amount": 250000,
    "expected_outcome": "approved"
  },
  ...
]
```

### Creating Datasets
```python
from shared.datasets import DatasetManager

manager = DatasetManager()

# Create evaluation data
evaluation_data = [
    {
        "request_id": "eval_001",
        "annual_income": 85000,
        "credit_score": 750,
        "loan_amount": 250000,
        "expected_outcome": "approved"
    },
    # ... more samples
]

# Save with metadata
manager.save_dataset(
    dataset=evaluation_data,
    dataset_name="my_test_set",
    description="Monthly evaluation dataset",
    version="2025.10",
    tags={"type": "evaluation", "month": "october"}
)
```

## Makefile Commands

```bash
# Evaluate agent on default test set
make evaluate

# Evaluate specific agent and dataset
make evaluate-agent AGENT_NAME=loan_approval DATASET=custom_test_set

# Check for drift
make evaluate-drift BASELINE=baseline_v1 CURRENT=current_month

# View MLFlow UI (if running locally)
mlflow ui --port 5000
```

## Continuous Evaluation

### Databricks Jobs
Set up scheduled evaluations:

1. Create a Databricks job that runs `scripts/evaluate_agent.py`
2. Schedule daily/weekly/monthly runs
3. Configure alerts for drift detection
4. Archive results to MLFlow

### Example Job Configuration
```yaml
name: loan_approval_evaluation
schedule: "0 0 * * *"  # Daily at midnight
cluster:
  node_type_id: "Standard_DS3_v2"
  num_workers: 2
tasks:
  - task_key: evaluate
    python_script_task:
      python_file: scripts/evaluate_agent.py
      parameters:
        - "--agent"
        - "loan_approval"
        - "--dataset"
        - "production_sample"
```

## Best Practices

### 1. **Tagging Strategy**
Use consistent tags for easy filtering:
```python
tracker.start_run(tags={
    "environment": "production",
    "version": "1.2.0",
    "data_source": "live_traffic",
    "evaluation": "false"
})
```

### 2. **Naming Conventions**
- Experiments: `/Shared/ai-agents/{agent_name}`
- Runs: `{agent_name}_{purpose}_{timestamp}`
- Models: `{agent_name}_v{version}`
- Datasets: `{agent_name}_{type}_{version}`

### 3. **Metric Logging**
Log metrics at consistent steps:
```python
for step, batch in enumerate(batches):
    # Process batch
    metrics = process_batch(batch)
    
    # Log with step
    tracker.log_metrics(metrics, step=step)
```

### 4. **Model Versioning**
Register models with semantic versioning:
```python
tracker.log_model(
    model=agent,
    registered_model_name="loan_approval",
    artifact_path="model"
)

# Transition to production
tracker.transition_model_stage(
    model_name="loan_approval",
    version="3",
    stage="Production"
)
```

### 5. **Drift Monitoring**
Set up regular drift checks:
```bash
# Weekly drift check
0 0 * * 0 cd /app && poetry run python scripts/evaluate_agent.py \
    --drift-detection \
    --baseline-dataset baseline_v1 \
    --dataset weekly_sample
```

## Databricks Integration

### Model Serving
Deploy models to Databricks Model Serving:

```python
from databricks import sql

# Register model
mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name="loan_approval_prod"
)

# Enable serving
# (Use Databricks UI or REST API)
```

### Mosaic AI Monitoring
Leverage Databricks Mosaic AI for:
- Automatic drift detection
- Data quality monitoring
- Performance degradation alerts
- Cost tracking

## Migration from Prometheus

### What Changed
- ❌ Removed: `prometheus-client` dependency
- ❌ Removed: `/metrics` endpoint
- ✅ Added: MLFlow metrics logging
- ✅ Added: Dataset evaluation framework
- ✅ Added: `/api/v1/loan/evaluate_dataset` endpoint
- ✅ Added: Automated evaluation scripts

### Code Changes
**Before (Prometheus):**
```python
from prometheus_client import Counter, Histogram

counter = Counter('requests_total', 'Total requests')
histogram = Histogram('duration_seconds', 'Request duration')

counter.inc()
histogram.observe(0.250)
```

**After (MLFlow):**
```python
from shared.metrics import get_metrics_collector

collector = get_metrics_collector("loan_approval")
collector.record_request(status="approved")
collector.record_duration(duration=250.0)
```

## Troubleshooting

### MLFlow Connection Issues
```bash
# Check Databricks connection
databricks auth login

# Test MLFlow connectivity
python -c "import mlflow; print(mlflow.get_tracking_uri())"
```

### Missing Datasets
```bash
# List available datasets
poetry run python -c "from shared.datasets import DatasetManager; print(DatasetManager().list_datasets())"
```

### Evaluation Failures
Check logs for detailed error messages:
```bash
# Run with verbose logging
LOG_LEVEL=DEBUG poetry run python scripts/evaluate_agent.py --agent loan_approval
```

## Resources

- [MLFlow Documentation](https://mlflow.org/docs/latest/index.html)
- [Databricks MLFlow Guide](https://docs.databricks.com/mlflow/index.html)
- [Mosaic AI Monitoring](https://docs.databricks.com/machine-learning/model-serving/model-serving-intro.html)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Creating Agents Guide](docs/CREATING_AGENTS.md)
