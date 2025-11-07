"""MS Teams notifications for alerts and monitoring."""

from typing import Optional
import pymsteams
from shared.monitoring.logger import get_logger

logger = get_logger(__name__)


class TeamsNotifier:
    """Send notifications to MS Teams channel."""

    def __init__(self, webhook_url: str) -> None:
        """
        Initialize Teams notifier.

        Args:
            webhook_url: MS Teams webhook URL
        """
        self.webhook_url = webhook_url

    def send_message(
        self,
        title: str,
        text: str,
        color: str = "0078D4",
        facts: Optional[dict] = None,
    ) -> bool:
        """
        Send a message to Teams channel.

        Args:
            title: Message title
            text: Message text
            color: Hex color code (default: blue)
            facts: Optional dictionary of facts to include

        Returns:
            True if successful, False otherwise
        """
        try:
            message = pymsteams.connectorcard(self.webhook_url)
            message.title(title)
            message.text(text)
            message.color(color)

            if facts:
                section = pymsteams.cardsection()
                for key, value in facts.items():
                    section.addFact(key, str(value))
                message.addSection(section)

            message.send()
            logger.info(f"Teams notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Teams notification: {e}")
            return False

    def send_success(self, title: str, details: Optional[dict] = None) -> bool:
        """
        Send a success notification.

        Args:
            title: Success message title
            details: Optional details dictionary

        Returns:
            True if successful, False otherwise
        """
        return self.send_message(
            title=f"✅ {title}",
            text="Operation completed successfully",
            color="28A745",
            facts=details,
        )

    def send_warning(self, title: str, message: str, details: Optional[dict] = None) -> bool:
        """
        Send a warning notification.

        Args:
            title: Warning message title
            message: Warning message
            details: Optional details dictionary

        Returns:
            True if successful, False otherwise
        """
        return self.send_message(
            title=f"⚠️ {title}",
            text=message,
            color="FFC107",
            facts=details,
        )

    def send_error(self, title: str, error: str, details: Optional[dict] = None) -> bool:
        """
        Send an error notification.

        Args:
            title: Error message title
            error: Error message
            details: Optional details dictionary

        Returns:
            True if successful, False otherwise
        """
        return self.send_message(
            title=f"❌ {title}",
            text=error,
            color="DC3545",
            facts=details,
        )

    def send_deployment_notification(
        self,
        environment: str,
        version: str,
        status: str,
        details: Optional[dict] = None,
    ) -> bool:
        """
        Send a deployment notification.

        Args:
            environment: Deployment environment (test, acceptance, production)
            version: Version being deployed
            status: Deployment status
            details: Optional details dictionary

        Returns:
            True if successful, False otherwise
        """
        color_map = {
            "success": "28A745",
            "failed": "DC3545",
            "in_progress": "0078D4",
        }

        facts_dict = {"Environment": environment, "Version": version, "Status": status}
        if details:
            facts_dict.update(details)

        return self.send_message(
            title=f"🚀 Deployment to {environment.upper()}",
            text=f"Version {version} deployment status: {status}",
            color=color_map.get(status.lower(), "0078D4"),
            facts=facts_dict,
        )

    def send_performance_alert(
        self,
        agent_name: str,
        metric_name: str,
        current_value: float,
        threshold: float,
        details: Optional[dict] = None,
    ) -> bool:
        """
        Send a performance alert.

        Args:
            agent_name: Name of the agent
            metric_name: Metric that triggered alert
            current_value: Current metric value
            threshold: Threshold value
            details: Optional details dictionary

        Returns:
            True if successful, False otherwise
        """
        facts_dict = {
            "Agent": agent_name,
            "Metric": metric_name,
            "Current Value": f"{current_value:.2f}",
            "Threshold": f"{threshold:.2f}",
        }
        if details:
            facts_dict.update(details)

        return self.send_message(
            title=f"📊 Performance Alert: {agent_name}",
            text=f"{metric_name} exceeded threshold",
            color="FFC107",
            facts=facts_dict,
        )