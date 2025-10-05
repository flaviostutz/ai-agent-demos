# Quick Reference: MLFlow Evaluation

## 🚀 Quick Commands

```bash
# Evaluate loan approval agent
make evaluate

# Evaluate specific agent and dataset  
make evaluate-agent AGENT_NAME=loan_approval DATASET=my_test_set

# Check for drift
make evaluate-drift BASELINE=baseline_v1 CURRENT=current_month

# View MLFlow UI (local)
mlflow ui --port 5000
```

## 📊 API Endpoints

### Evaluate Loan Request
```bash
POST /api/v1/loan/evaluate
Authorization: Bearer <token>
Content-Type: application/json

{
  "request_id": "req_123",
  "applicant_name": "John Doe",
  "annual_income": 85000,
  "credit_score": 750,
  "loan_amount": 250000,
  ...
}
```

### Evaluate on Dataset
```bash
POST /api/v1/loan/evaluate_dataset
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_name": "loan_approval_test_set",
  "target_field": "expected_outcome",
  "prediction_field": "outcome"
}
```

## 🐍 Python API

### Quick Evaluation
```python
from shared.model_evaluation import ModelEvaluator
from shared.datasets import DatasetManager

def agent_func(request: dict) -> dict:
    # Your agent logic
    return {"outcome": "approved", "risk_score": 25}

evaluator = ModelEvaluator("loan_approval", agent_func)
metrics = evaluator.evaluate_dataset("test_set", log_to_mlflow=True)

print(f"Accuracy: {metrics.accuracy:.3f}")
print(f"F1 Score: {metrics.f1_score:.3f}")
print(f"Avg Latency: {metrics.avg_latency_ms:.2f}ms")
```

### Drift Detection
```python
drift = evaluator.detect_drift(
    baseline_dataset="baseline_v1",
    current_dataset="current_month",
    threshold=0.05  # 5% degradation
)

if drift["has_drift"]:
    print("⚠️ Performance drift detected!")
    for metric, data in drift["metrics"].items():
        print(f"{metric}: {data['baseline']:.3f} → {data['current']:.3f}")
```

### Dataset Management
```python
from shared.datasets import DatasetManager

manager = DatasetManager()

# List datasets
datasets = manager.list_datasets()

# Load dataset
data = manager.load_dataset("loan_approval_test_set")

# Save new dataset
manager.save_dataset(
    dataset=my_data,
    dataset_name="new_test_set",
    description="Q4 2025 test data",
    version="1.0",
    tags={"quarter": "Q4", "year": "2025"}
)

# Log to MLFlow
manager.log_dataset_to_mlflow("test_set", context="evaluation")
```

### MLFlow Tracking
```python
from shared.mlflow_tracking import AgentTracker

tracker = AgentTracker("loan_approval")
tracker.start_run(run_name="eval_batch_001")

# Log metrics
tracker.log_metrics({
    "accuracy": 0.95,
    "latency_ms": 250.5
})

# Log parameters
tracker.log_params({
    "model": "gpt-4",
    "temperature": 0.0
})

# Log dataset
import pandas as pd
df = pd.DataFrame(data)
tracker.log_dataset(df, name="eval_set", targets="outcome")

# Log evaluation results
tracker.log_evaluation_results(
    eval_results={"accuracy": 0.95},
    dataset_name="test_set"
)

tracker.end_run()
```

## 📁 File Locations

```
data/evaluation/
├── loan_approval_test_set.json       # Main test dataset (20 cases)
└── *_metadata.json                   # Dataset metadata

scripts/
└── evaluate_agent.py                 # Evaluation CLI tool

shared/
├── datasets.py                       # Dataset management
├── model_evaluation.py               # Evaluation framework
├── mlflow_tracking.py                # MLFlow integration
└── metrics.py                        # Metrics collection

docs/
├── MLFLOW_MONITORING.md              # Full guide
└── MIGRATION_SUMMARY.md              # Migration details
```

## 🔧 Environment Setup

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional (for Databricks)
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="dapi..."

# Optional (for local MLFlow)
export MLFLOW_TRACKING_URI="http://localhost:5000"
```

## 📈 Metrics Available

- **Classification**: accuracy, precision, recall, F1-score
- **Performance**: avg_latency, p95_latency, p99_latency
- **Reliability**: error_rate, success_rate
- **Cost**: total_cost, avg_cost_per_request
- **Custom**: confusion_matrix, drift_percentage

## ⚠️ Troubleshooting

```bash
# Check datasets
python -c "from shared.datasets import DatasetManager; print(DatasetManager().list_datasets())"

# Test MLFlow connection
python -c "import mlflow; print(mlflow.get_tracking_uri())"

# Verbose logging
LOG_LEVEL=DEBUG make evaluate

# Check Databricks auth
databricks auth login
```

## 🎯 Best Practices

1. **Version datasets** with semantic versions (v1.0, v2.0)
2. **Tag runs** with environment, version, purpose
3. **Run evaluations** after code changes
4. **Monitor drift** weekly or monthly
5. **Set thresholds** for acceptable degradation (e.g., 5%)
6. **Archive baselines** for long-term comparison

## 📚 More Info

- Full guide: `docs/MLFLOW_MONITORING.md`
- Migration: `MIGRATION_SUMMARY.md`
- Developer guide: `docs/DEVELOPER_GUIDE.md`
- Creating agents: `docs/CREATING_AGENTS.md`
