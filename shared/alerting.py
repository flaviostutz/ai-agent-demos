"""MS Teams alerting integration."""

import os
from typing import Dict, Any, Optional
import pymsteams


class TeamsAlerter:
    """Send alerts to MS Teams channel."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("TEAMS_WEBHOOK_URL")

    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an alert to Teams channel.

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error)
            metadata: Additional metadata to include

        Returns:
            bool: True if alert sent successfully
        """
        if not self.webhook_url:
            return False

        try:
            teams_message = pymsteams.connectorcard(self.webhook_url)
            teams_message.title(title)
            teams_message.text(message)

            # Set color based on severity
            color_map = {"info": "00FF00", "warning": "FFA500", "error": "FF0000"}
            teams_message.color(color_map.get(severity, "0078D7"))

            # Add metadata section
            if metadata:
                section = pymsteams.cardsection()
                for key, value in metadata.items():
                    section.addFact(key, str(value))
                teams_message.addSection(section)

            teams_message.send()
            return True
        except Exception as e:
            print(f"Failed to send Teams alert: {e}")
            return False

    def send_agent_error(
        self,
        agent_name: str,
        error_message: str,
        request_id: str,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send agent error alert."""
        metadata = {
            "Agent": agent_name,
            "Request ID": request_id,
            "Timestamp": str(additional_info.get("timestamp")) if additional_info else "",
        }
        if additional_info:
            metadata.update(additional_info)

        return self.send_alert(
            title=f"🚨 Agent Error: {agent_name}",
            message=error_message,
            severity="error",
            metadata=metadata,
        )

    def send_performance_alert(
        self,
        agent_name: str,
        metric: str,
        threshold: float,
        actual_value: float,
    ) -> bool:
        """Send performance degradation alert."""
        return self.send_alert(
            title=f"⚠️ Performance Alert: {agent_name}",
            message=f"{metric} exceeded threshold",
            severity="warning",
            metadata={
                "Agent": agent_name,
                "Metric": metric,
                "Threshold": str(threshold),
                "Actual Value": str(actual_value),
            },
        )


def get_teams_alerter() -> TeamsAlerter:
    """Get Teams alerter instance."""
    return TeamsAlerter()
