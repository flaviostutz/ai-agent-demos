"""Metrics collection and reporting using MLFlow."""

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import mlflow


class MetricsCollector:
    """Collects and reports metrics for agents using MLFlow."""

    def __init__(self, agent_name: str, run_id: str | None = None):
        """
        Initialize metrics collector.

        Args:
            agent_name: Name of the agent
            run_id: Optional MLFlow run ID. If not provided, will use active run.
        """
        self.agent_name = agent_name
        self.run_id = run_id
        self._request_count = 0
        self._error_count = 0
        self._token_count = 0
        self._durations: list[float] = []

    def record_request(self, status: str) -> None:
        """Record a request with status."""
        self._request_count += 1

        # Log to MLFlow
        if self.run_id:
            with mlflow.start_run(run_id=self.run_id):
                mlflow.log_metric(f"{self.agent_name}_requests_total", self._request_count)
                mlflow.log_metric(f"{self.agent_name}_requests_{status}", 1)
        else:
            mlflow.log_metric(f"{self.agent_name}_requests_total", self._request_count)
            mlflow.log_metric(f"{self.agent_name}_requests_{status}", 1)

    def record_error(self, error_type: str) -> None:
        """Record an error."""
        self._error_count += 1

        # Log to MLFlow
        if self.run_id:
            with mlflow.start_run(run_id=self.run_id):
                mlflow.log_metric(f"{self.agent_name}_errors_total", self._error_count)
                mlflow.log_metric(f"{self.agent_name}_errors_{error_type}", 1)
        else:
            mlflow.log_metric(f"{self.agent_name}_errors_total", self._error_count)
            mlflow.log_metric(f"{self.agent_name}_errors_{error_type}", 1)

    def record_token_usage(self, model: str, tokens: int) -> None:
        """Record token usage."""
        self._token_count += tokens

        # Log to MLFlow
        if self.run_id:
            with mlflow.start_run(run_id=self.run_id):
                mlflow.log_metric(f"{self.agent_name}_tokens_total", self._token_count)
                mlflow.log_metric(f"{self.agent_name}_tokens_{model}", tokens)
        else:
            mlflow.log_metric(f"{self.agent_name}_tokens_total", self._token_count)
            mlflow.log_metric(f"{self.agent_name}_tokens_{model}", tokens)

    def record_duration(self, duration: float) -> None:
        """Record request duration."""
        self._durations.append(duration)

        # Log to MLFlow
        if self.run_id:
            with mlflow.start_run(run_id=self.run_id):
                mlflow.log_metric(f"{self.agent_name}_duration_seconds", duration)
                mlflow.log_metric(
                    f"{self.agent_name}_duration_avg", sum(self._durations) / len(self._durations)
                )
        else:
            mlflow.log_metric(f"{self.agent_name}_duration_seconds", duration)
            mlflow.log_metric(
                f"{self.agent_name}_duration_avg", sum(self._durations) / len(self._durations)
            )

    @contextmanager
    def measure_duration(self) -> Generator[None, None, None]:
        """Context manager to measure request duration."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_duration(duration)

    def get_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        return {
            "agent_name": self.agent_name,
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "total_tokens": self._token_count,
            "average_duration": (
                sum(self._durations) / len(self._durations) if self._durations else 0
            ),
            "total_duration": sum(self._durations),
        }


def get_metrics_collector(agent_name: str, run_id: str | None = None) -> MetricsCollector:
    """Get a metrics collector for an agent."""
    return MetricsCollector(agent_name=agent_name, run_id=run_id)


