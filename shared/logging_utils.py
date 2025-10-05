"""Logging utilities with tracing support."""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

# Initialize OpenTelemetry
def setup_tracing(service_name: str) -> trace.Tracer:
    """Setup OpenTelemetry tracing."""
    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


class AgentLogger:
    """Enhanced logger with agent-specific context."""

    def __init__(
        self,
        name: str,
        agent_id: Optional[str] = None,
        request_id: Optional[str] = None,
        level: int = logging.INFO,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - [%(levelname)s] - "
                "agent_id=%(agent_id)s request_id=%(request_id)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.agent_id = agent_id or "unknown"
        self.request_id = request_id or "unknown"

    def _build_extra(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build extra context for logging."""
        base_extra = {"agent_id": self.agent_id, "request_id": self.request_id}
        if extra:
            base_extra.update(extra)
        return base_extra

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self.logger.info(message, extra=self._build_extra(extra))

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=self._build_extra(extra))

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error message."""
        self.logger.error(message, extra=self._build_extra(extra))

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=self._build_extra(extra))


def get_logger(
    name: str,
    agent_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> AgentLogger:
    """Get or create an agent logger."""
    level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
    return AgentLogger(name=name, agent_id=agent_id, request_id=request_id, level=level)
