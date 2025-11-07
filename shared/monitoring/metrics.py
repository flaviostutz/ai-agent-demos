"""Metrics tracking with MLFlow integration."""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import mlflow

from shared.monitoring.logger import get_logger

logger = get_logger(__name__)


class MetricsTracker:
    """Track metrics and send to MLFlow and Databricks Mosaic AI."""

    def __init__(self, experiment_name: str, run_name: str | None = None) -> None:
        """Initialize metrics tracker.

        Args:
            experiment_name: MLFlow experiment name
            run_name: Optional run name

        """
        self.experiment_name = experiment_name
        self.run_name = run_name
        self._setup_mlflow()

    def _setup_mlflow(self) -> None:
        """Setup MLFlow experiment."""
        try:
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"MLFlow experiment set to: {self.experiment_name}")
        except Exception as e:
            logger.warning(f"Failed to setup MLFlow experiment: {e}")

    @contextmanager
    def start_run(self, run_name: str | None = None) -> Iterator[None]:
        """Start an MLFlow run context.

        Args:
            run_name: Optional run name

        Yields:
            None

        """
        name = run_name or self.run_name
        try:
            with mlflow.start_run(run_name=name):
                logger.info(f"Started MLFlow run: {name}")
                yield
        except Exception as e:
            logger.error(f"Error in MLFlow run: {e}")
            raise
        finally:
            logger.info(f"Ended MLFlow run: {name}")

    def log_metric(self, key: str, value: float, step: int | None = None) -> None:
        """Log a metric to MLFlow.

        Args:
            key: Metric name
            value: Metric value
            step: Optional step number

        """
        try:
            mlflow.log_metric(key, value, step=step)
            logger.debug(f"Logged metric: {key}={value}")
        except Exception as e:
            logger.warning(f"Failed to log metric {key}: {e}")

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        """Log multiple metrics to MLFlow.

        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number

        """
        try:
            mlflow.log_metrics(metrics, step=step)
            logger.debug(f"Logged {len(metrics)} metrics")
        except Exception as e:
            logger.warning(f"Failed to log metrics: {e}")

    def log_param(self, key: str, value: Any) -> None:
        """Log a parameter to MLFlow.

        Args:
            key: Parameter name
            value: Parameter value

        """
        try:
            mlflow.log_param(key, value)
            logger.debug(f"Logged param: {key}={value}")
        except Exception as e:
            logger.warning(f"Failed to log param {key}: {e}")

    def log_params(self, params: dict[str, Any]) -> None:
        """Log multiple parameters to MLFlow.

        Args:
            params: Dictionary of parameter names and values

        """
        try:
            mlflow.log_params(params)
            logger.debug(f"Logged {len(params)} params")
        except Exception as e:
            logger.warning(f"Failed to log params: {e}")

    def log_artifact(self, local_path: str, artifact_path: str | None = None) -> None:
        """Log an artifact to MLFlow.

        Args:
            local_path: Local file path
            artifact_path: Optional artifact path in MLFlow

        """
        try:
            mlflow.log_artifact(local_path, artifact_path)
            logger.debug(f"Logged artifact: {local_path}")
        except Exception as e:
            logger.warning(f"Failed to log artifact {local_path}: {e}")

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag in MLFlow.

        Args:
            key: Tag name
            value: Tag value

        """
        try:
            mlflow.set_tag(key, value)
            logger.debug(f"Set tag: {key}={value}")
        except Exception as e:
            logger.warning(f"Failed to set tag {key}: {e}")

    def set_tags(self, tags: dict[str, str]) -> None:
        """Set multiple tags in MLFlow.

        Args:
            tags: Dictionary of tag names and values

        """
        try:
            mlflow.set_tags(tags)
            logger.debug(f"Set {len(tags)} tags")
        except Exception as e:
            logger.warning(f"Failed to set tags: {e}")

    @contextmanager
    def track_time(self, metric_name: str) -> Iterator[None]:
        """Context manager to track execution time.

        Args:
            metric_name: Name of the metric to log

        Yields:
            None

        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            self.log_metric(metric_name, elapsed_ms)
            logger.info(f"{metric_name}: {elapsed_ms:.2f}ms")
