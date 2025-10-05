"""Automated model evaluation framework for agents."""

import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from shared.datasets import DatasetManager
from shared.logging_utils import get_logger
from shared.mlflow_tracking import AgentTracker

logger = get_logger(__name__)


class EvaluationMetrics:
    """Container for evaluation metrics."""

    def __init__(self):
        self.accuracy: float = 0.0
        self.precision: float = 0.0
        self.recall: float = 0.0
        self.f1_score: float = 0.0
        self.avg_latency_ms: float = 0.0
        self.p95_latency_ms: float = 0.0
        self.p99_latency_ms: float = 0.0
        self.error_rate: float = 0.0
        self.total_cost: float = 0.0
        self.avg_cost_per_request: float = 0.0
        self.custom_metrics: dict[str, float] = {}

    def to_dict(self) -> dict[str, float]:
        """Convert metrics to dictionary."""
        result = {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "avg_latency_ms": self.avg_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "error_rate": self.error_rate,
            "total_cost": self.total_cost,
            "avg_cost_per_request": self.avg_cost_per_request,
        }
        result.update(self.custom_metrics)
        return result


class ModelEvaluator:
    """Evaluate agent/model performance against datasets."""

    def __init__(
        self,
        agent_name: str,
        agent_func: Callable[[dict[str, Any]], dict[str, Any]],
        dataset_manager: DatasetManager | None = None,
    ):
        """
        Initialize model evaluator.

        Args:
            agent_name: Name of the agent being evaluated
            agent_func: Callable that takes request dict and returns response dict
            dataset_manager: Optional dataset manager (creates default if not provided)
        """
        self.agent_name = agent_name
        self.agent_func = agent_func
        self.dataset_manager = dataset_manager or DatasetManager()
        self.tracker = AgentTracker(agent_name)

    def evaluate_dataset(
        self,
        dataset_name: str,
        target_field: str = "expected_outcome",
        prediction_field: str = "outcome",
        log_to_mlflow: bool = True,
    ) -> EvaluationMetrics:
        """
        Evaluate agent performance on a dataset.

        Args:
            dataset_name: Name of the evaluation dataset
            target_field: Field name containing expected/ground truth values
            prediction_field: Field name in agent response containing predictions
            log_to_mlflow: Whether to log results to MLFlow

        Returns:
            Evaluation metrics
        """
        logger.info(f"Starting evaluation of {self.agent_name} on dataset '{dataset_name}'")

        # Load dataset
        dataset = self.dataset_manager.load_dataset(dataset_name)

        # Start MLFlow run
        if log_to_mlflow:
            run_name = f"{self.agent_name}_eval_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.tracker.start_run(
                run_name=run_name,
                tags={
                    "evaluation": "true",
                    "dataset": dataset_name,
                    "agent": self.agent_name,
                },
            )

        # Run predictions
        predictions = []
        ground_truths = []
        latencies = []
        errors = 0
        costs = []

        for i, sample in enumerate(dataset):
            try:
                # Extract ground truth
                if target_field not in sample:
                    logger.warning(f"Sample {i} missing target field '{target_field}', skipping")
                    continue

                ground_truth = sample[target_field]
                ground_truths.append(ground_truth)

                # Run agent prediction
                start_time = time.time()
                response = self.agent_func(sample)
                latency_ms = (time.time() - start_time) * 1000

                latencies.append(latency_ms)

                # Extract prediction
                prediction = response.get(prediction_field, "error")
                predictions.append(prediction)

                # Track cost if available
                if "cost" in response:
                    costs.append(response["cost"])

            except Exception as e:
                logger.error(f"Error processing sample {i}: {e}")
                errors += 1
                predictions.append("error")

        # Calculate metrics
        metrics = EvaluationMetrics()

        # Classification metrics
        if predictions and ground_truths:
            metrics.accuracy = accuracy_score(ground_truths, predictions)

            # Get classification report as dict
            report = classification_report(
                ground_truths, predictions, output_dict=True, zero_division=0
            )

            # Extract weighted averages
            if "weighted avg" in report:
                metrics.precision = report["weighted avg"]["precision"]
                metrics.recall = report["weighted avg"]["recall"]
                metrics.f1_score = report["weighted avg"]["f1-score"]

        # Latency metrics
        if latencies:
            metrics.avg_latency_ms = float(np.mean(latencies))
            metrics.p95_latency_ms = float(np.percentile(latencies, 95))
            metrics.p99_latency_ms = float(np.percentile(latencies, 99))

        # Error rate
        metrics.error_rate = errors / len(dataset) if dataset else 0.0

        # Cost metrics
        if costs:
            metrics.total_cost = float(np.sum(costs))
            metrics.avg_cost_per_request = float(np.mean(costs))

        # Custom metrics - confusion matrix
        if predictions and ground_truths:
            cm = confusion_matrix(ground_truths, predictions)
            # Store confusion matrix as custom metrics
            unique_labels = sorted(set(ground_truths + predictions))
            for i, true_label in enumerate(unique_labels):
                for j, pred_label in enumerate(unique_labels):
                    if i < len(cm) and j < len(cm[i]):
                        metrics.custom_metrics[f"cm_{true_label}_as_{pred_label}"] = int(cm[i][j])

        # Log to MLFlow
        if log_to_mlflow:
            self.tracker.log_evaluation_results(
                metrics.to_dict(), dataset_name=dataset_name, model_type="agent"
            )

            # Log dataset
            self.dataset_manager.log_dataset_to_mlflow(
                dataset_name, context="evaluation", targets=target_field
            )

            # Log predictions vs ground truth
            results_df = pd.DataFrame(
                {"ground_truth": ground_truths, "prediction": predictions, "latency_ms": latencies}
            )
            self.tracker.log_dataset(results_df, name=f"{dataset_name}_predictions")

            self.tracker.end_run()

        logger.info(
            f"Evaluation complete: accuracy={metrics.accuracy:.3f}, "
            f"avg_latency={metrics.avg_latency_ms:.2f}ms"
        )

        return metrics

    def compare_models(
        self,
        model_configs: list[dict[str, Any]],
        dataset_name: str,
        target_field: str = "expected_outcome",
    ) -> pd.DataFrame:
        """
        Compare multiple model configurations on the same dataset.

        Args:
            model_configs: List of dicts with 'name' and 'agent_func' keys
            dataset_name: Dataset to evaluate on
            target_field: Ground truth field name

        Returns:
            DataFrame with comparison results
        """
        results = []

        for config in model_configs:
            model_name = config["name"]
            agent_func = config["agent_func"]

            logger.info(f"Evaluating model: {model_name}")

            # Temporarily update agent function
            original_func = self.agent_func
            self.agent_func = agent_func

            # Evaluate
            metrics = self.evaluate_dataset(
                dataset_name, target_field=target_field, log_to_mlflow=True
            )

            # Restore original function
            self.agent_func = original_func

            # Store results
            result = {"model_name": model_name}
            result.update(metrics.to_dict())
            results.append(result)

        # Create comparison DataFrame
        comparison_df = pd.DataFrame(results)

        # Log comparison to MLFlow
        with mlflow.start_run(run_name=f"model_comparison_{dataset_name}"):
            mlflow.set_tag("comparison", "true")
            mlflow.set_tag("dataset", dataset_name)

            comparison_table = mlflow.data.from_pandas(comparison_df, name="model_comparison")
            mlflow.log_input(comparison_table, context="comparison")

        logger.info("Model comparison complete")
        return comparison_df

    def detect_drift(
        self,
        baseline_dataset: str,
        current_dataset: str,
        target_field: str = "expected_outcome",
        threshold: float = 0.05,
    ) -> dict[str, Any]:
        """
        Detect performance drift between baseline and current dataset.

        Args:
            baseline_dataset: Name of baseline dataset
            current_dataset: Name of current dataset
            target_field: Ground truth field name
            threshold: Acceptable performance degradation threshold

        Returns:
            Dict with drift detection results
        """
        logger.info(f"Detecting drift between '{baseline_dataset}' and '{current_dataset}'")

        # Evaluate on baseline
        baseline_metrics = self.evaluate_dataset(
            baseline_dataset, target_field=target_field, log_to_mlflow=False
        )

        # Evaluate on current
        current_metrics = self.evaluate_dataset(
            current_dataset, target_field=target_field, log_to_mlflow=False
        )

        # Calculate drift
        drift_results = {
            "has_drift": False,
            "baseline_dataset": baseline_dataset,
            "current_dataset": current_dataset,
            "threshold": threshold,
            "metrics": {},
        }

        metrics_to_check = ["accuracy", "precision", "recall", "f1_score"]

        for metric_name in metrics_to_check:
            baseline_value = getattr(baseline_metrics, metric_name)
            current_value = getattr(current_metrics, metric_name)
            drift = baseline_value - current_value

            drift_results["metrics"][metric_name] = {
                "baseline": baseline_value,
                "current": current_value,
                "drift": drift,
                "drift_pct": (drift / baseline_value * 100) if baseline_value > 0 else 0,
                "has_drift": abs(drift) > threshold,
            }

            if abs(drift) > threshold:
                drift_results["has_drift"] = True
                logger.warning(
                    f"Drift detected in {metric_name}: "
                    f"{baseline_value:.3f} -> {current_value:.3f} (drift: {drift:.3f})"
                )

        # Log to MLFlow
        with mlflow.start_run(run_name=f"drift_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            mlflow.set_tag("drift_detection", "true")
            mlflow.set_tag("baseline_dataset", baseline_dataset)
            mlflow.set_tag("current_dataset", current_dataset)

            mlflow.log_metric("has_drift", 1.0 if drift_results["has_drift"] else 0.0)
            mlflow.log_param("drift_threshold", threshold)

            for metric_name, metric_data in drift_results["metrics"].items():
                mlflow.log_metric(f"baseline_{metric_name}", metric_data["baseline"])
                mlflow.log_metric(f"current_{metric_name}", metric_data["current"])
                mlflow.log_metric(f"drift_{metric_name}", metric_data["drift"])

            mlflow.log_dict(drift_results, "drift_results.json")

        return drift_results

    def continuous_evaluation(
        self, dataset_name: str, target_field: str = "expected_outcome", schedule: str = "daily"
    ) -> None:
        """
        Set up continuous evaluation (placeholder for scheduled evaluation).

        Args:
            dataset_name: Dataset to evaluate on
            target_field: Ground truth field
            schedule: Evaluation schedule (daily, weekly, hourly)
        """
        logger.info(
            f"Setting up continuous evaluation for {self.agent_name} "
            f"on '{dataset_name}' with {schedule} schedule"
        )

        # In a real implementation, this would integrate with:
        # - Databricks Jobs for scheduled runs
        # - MLFlow Model Monitoring for automated checks
        # - Alerting when metrics degrade

        # For now, log the configuration
        with mlflow.start_run(
            run_name=f"continuous_eval_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):
            mlflow.set_tag("continuous_evaluation", "true")
            mlflow.set_tag("schedule", schedule)
            mlflow.log_param("dataset", dataset_name)
            mlflow.log_param("target_field", target_field)

        logger.info("Continuous evaluation configured - integrate with Databricks Jobs")


def get_model_evaluator(
    agent_name: str,
    agent_func: Callable[[dict[str, Any]], dict[str, Any]],
    dataset_manager: DatasetManager | None = None,
) -> ModelEvaluator:
    """Get a model evaluator instance."""
    return ModelEvaluator(
        agent_name=agent_name, agent_func=agent_func, dataset_manager=dataset_manager
    )
