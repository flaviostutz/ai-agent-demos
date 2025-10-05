"""MLFlow integration for comprehensive agent tracking and model management."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import mlflow
import pandas as pd
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient

from shared.config import get_config
from shared.logging_utils import get_logger

logger = get_logger(__name__)


class AgentTracker:
    """Track agent performance, experiments, and models with MLFlow."""

    def __init__(self, agent_name: str, enable_databricks_monitoring: bool = True):
        """
        Initialize agent tracker with MLFlow.

        Args:
            agent_name: Name of the agent
            enable_databricks_monitoring: Enable Databricks/Mosaic AI monitoring features
        """
        self.agent_name = agent_name
        self.config = get_config()
        self.enable_databricks_monitoring = enable_databricks_monitoring

        # Initialize MLFlow
        mlflow_config = self.config.get("mlflow", {})
        tracking_uri = mlflow_config.get("tracking_uri", "databricks")
        experiment_name = mlflow_config.get("experiment_name", f"/Shared/ai-agents/{agent_name}")

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

        self.client = MlflowClient()
        self.run_id = None
        self._request_logs: list[dict[str, Any]] = []

    def start_run(self, run_name: str | None = None, tags: dict[str, str] | None = None) -> str:
        """
        Start a new MLFlow run.

        Args:
            run_name: Optional custom run name
            tags: Additional tags to set on the run
        """
        run_name = run_name or f"{self.agent_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        run = mlflow.start_run(run_name=run_name)
        self.run_id = run.info.run_id

        # Log agent metadata
        mlflow.set_tag("agent_name", self.agent_name)
        mlflow.set_tag("environment", os.getenv("ENVIRONMENT", "development"))
        mlflow.set_tag("mlflow.note.content", f"Agent run for {self.agent_name}")

        # Add custom tags
        if tags:
            for key, value in tags.items():
                mlflow.set_tag(key, value)

        logger.info(f"Started MLFlow run: {self.run_id}")
        return self.run_id

    def log_request(
        self,
        request_id: str,
        request_data: dict[str, Any],
        decision_data: dict[str, Any],
        duration_ms: float,
    ) -> None:
        """Log a single agent request with full context."""
        if not self.run_id:
            self.start_run()

        # Store request log for batch analysis
        self._request_logs.append(
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "duration_ms": duration_ms,
                "outcome": decision_data.get("outcome", "unknown"),
                "risk_score": decision_data.get("risk_score", 0),
                **request_data,
            }
        )

        # Log metrics
        mlflow.log_metric("request_duration_ms", duration_ms)
        if "risk_score" in decision_data:
            mlflow.log_metric("risk_score", decision_data["risk_score"])

        # Log parameters for this specific request
        mlflow.log_param(f"request_{request_id}_outcome", decision_data.get("outcome", "unknown"))

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        """Log multiple metrics at once."""
        if not self.run_id:
            self.start_run()

        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)

    def log_params(self, params: dict[str, Any]) -> None:
        """Log parameters."""
        if not self.run_id:
            self.start_run()

        for key, value in params.items():
            # Convert complex types to JSON strings
            if isinstance(value, dict | list):
                value = json.dumps(value)
            mlflow.log_param(key, value)

    def log_model(
        self,
        model: Any,
        artifact_path: str = "model",
        signature: Any = None,
        input_example: Any = None,
        registered_model_name: str | None = None,
    ) -> None:
        """
        Log a model with signature and optional registration.

        Args:
            model: Model object to log
            artifact_path: Path within the run to store the model
            signature: Model signature (input/output schema)
            input_example: Example input for the model
            registered_model_name: Name to register the model in Model Registry
        """
        if not self.run_id:
            self.start_run()

        # Infer signature if not provided
        if signature is None and input_example is not None:
            try:
                signature = infer_signature(input_example)
            except Exception as e:
                logger.warning(f"Could not infer signature: {e}")

        mlflow.pyfunc.log_model(
            artifact_path=artifact_path,
            python_model=model,
            signature=signature,
            input_example=input_example,
            registered_model_name=registered_model_name,
        )

        logger.info(f"Logged model to {artifact_path}")

    def log_dataset(
        self, dataset: pd.DataFrame, name: str, targets: str | None = None
    ) -> mlflow.data.dataset.Dataset:
        """
        Log a dataset to MLFlow.

        Args:
            dataset: Pandas DataFrame containing the dataset
            name: Name for the dataset
            targets: Column name containing target values

        Returns:
            MLFlow Dataset object
        """
        if not self.run_id:
            self.start_run()

        mlflow_dataset = mlflow.data.from_pandas(dataset, name=name, targets=targets)
        mlflow.log_input(mlflow_dataset, context="training" if targets else "evaluation")

        logger.info(f"Logged dataset '{name}' with {len(dataset)} rows")
        return mlflow_dataset

    def log_evaluation_results(
        self,
        eval_results: dict[str, float],
        dataset_name: str,
        model_type: str = "agent",
    ) -> None:
        """
        Log evaluation results for a dataset.

        Args:
            eval_results: Dictionary of metric names and values
            dataset_name: Name of the evaluation dataset
            model_type: Type of model being evaluated
        """
        if not self.run_id:
            self.start_run()

        # Log each metric with dataset context
        for metric_name, value in eval_results.items():
            mlflow.log_metric(f"eval_{dataset_name}_{metric_name}", value)

        # Log as JSON artifact
        eval_artifact_path = Path("evaluation_results") / f"{dataset_name}_results.json"
        eval_artifact_path.parent.mkdir(exist_ok=True)
        with open(eval_artifact_path, "w") as f:
            json.dump(
                {
                    "dataset": dataset_name,
                    "model_type": model_type,
                    "timestamp": datetime.now().isoformat(),
                    "metrics": eval_results,
                },
                f,
                indent=2,
            )

        mlflow.log_artifact(str(eval_artifact_path), "evaluation_results")
        eval_artifact_path.unlink()  # Clean up temp file

    def log_artifact(self, local_path: str, artifact_path: str | None = None) -> None:
        """Log an artifact file."""
        if not self.run_id:
            self.start_run()

        mlflow.log_artifact(local_path, artifact_path)

    def log_dict(self, dictionary: dict[str, Any], artifact_file: str) -> None:
        """Log a dictionary as a JSON artifact."""
        if not self.run_id:
            self.start_run()

        mlflow.log_dict(dictionary, artifact_file)

    def save_request_logs(self) -> None:
        """Save accumulated request logs as a dataset."""
        if not self._request_logs:
            logger.warning("No request logs to save")
            return

        if not self.run_id:
            self.start_run()

        # Convert to DataFrame
        df = pd.DataFrame(self._request_logs)

        # Save as CSV artifact
        csv_path = Path("request_logs.csv")
        df.to_csv(csv_path, index=False)
        mlflow.log_artifact(str(csv_path), "logs")
        csv_path.unlink()

        # Log as MLFlow dataset
        mlflow_dataset = mlflow.data.from_pandas(df, name=f"{self.agent_name}_requests")
        mlflow.log_input(mlflow_dataset, context="requests")

        logger.info(f"Saved {len(self._request_logs)} request logs")

    def end_run(self, status: str = "FINISHED") -> None:
        """End the current MLFlow run."""
        if self.run_id:
            # Save any accumulated logs
            if self._request_logs:
                self.save_request_logs()

            mlflow.end_run(status)
            logger.info(f"Ended MLFlow run: {self.run_id} with status {status}")
            self.run_id = None
            self._request_logs = []

    def log_batch_performance(
        self,
        total_requests: int,
        successful: int,
        failed: int,
        avg_duration_ms: float,
        avg_risk_score: float | None = None,
    ) -> None:
        """Log batch performance metrics."""
        if not self.run_id:
            self.start_run()

        metrics = {
            "total_requests": float(total_requests),
            "successful_requests": float(successful),
            "failed_requests": float(failed),
            "success_rate": (successful / total_requests) * 100 if total_requests > 0 else 0,
            "avg_duration_ms": avg_duration_ms,
        }

        if avg_risk_score is not None:
            metrics["avg_risk_score"] = avg_risk_score

        for key, value in metrics.items():
            mlflow.log_metric(key, value)

    def set_model_version_tag(self, model_name: str, version: str, tags: dict[str, str]) -> None:
        """
        Set tags on a registered model version.

        Args:
            model_name: Name of the registered model
            version: Model version
            tags: Dictionary of tags to set
        """
        for key, value in tags.items():
            self.client.set_model_version_tag(model_name, version, key, value)

    def transition_model_stage(
        self, model_name: str, version: str, stage: str, archive_existing: bool = True
    ) -> None:
        """
        Transition a model version to a new stage.

        Args:
            model_name: Name of the registered model
            version: Model version
            stage: Target stage (Staging, Production, Archived)
            archive_existing: Whether to archive existing models in the target stage
        """
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=archive_existing,
        )
        logger.info(f"Transitioned {model_name} v{version} to {stage}")


def get_agent_tracker(
    agent_name: str, enable_databricks_monitoring: bool = True
) -> AgentTracker:
    """Get an agent tracker instance."""
    return AgentTracker(
        agent_name=agent_name, enable_databricks_monitoring=enable_databricks_monitoring
    )

