"""Security utilities for context-based permissioning."""

from typing import Set, Optional, Any, Dict
from enum import Enum
from shared.monitoring.logger import get_logger

logger = get_logger(__name__)


class Permission(str, Enum):
    """Available permissions."""

    READ_PII = "read_pii"
    READ_FINANCIAL = "read_financial"
    READ_CREDIT = "read_credit"
    WRITE_DECISION = "write_decision"
    ACCESS_EXTERNAL_API = "access_external_api"
    READ_POLICIES = "read_policies"


class SecurityContext:
    """Security context for agent operations."""

    def __init__(
        self,
        agent_id: str,
        permissions: Set[Permission],
        environment: str = "production",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize security context.

        Args:
            agent_id: Unique identifier for the agent
            permissions: Set of permissions granted to this context
            environment: Execution environment (development, test, production)
            metadata: Optional metadata dictionary
        """
        self.agent_id = agent_id
        self.permissions = permissions
        self.environment = environment
        self.metadata = metadata or {}
        logger.info(
            f"Security context created for {agent_id} with {len(permissions)} permissions"
        )

    def has_permission(self, permission: Permission) -> bool:
        """
        Check if context has a specific permission.

        Args:
            permission: Permission to check

        Returns:
            True if permission is granted, False otherwise
        """
        has_perm = permission in self.permissions
        if not has_perm:
            logger.warning(
                f"Permission denied: {self.agent_id} attempted {permission.value}"
            )
        return has_perm

    def require_permission(self, permission: Permission) -> None:
        """
        Require a specific permission, raise exception if not granted.

        Args:
            permission: Required permission

        Raises:
            PermissionError: If permission is not granted
        """
        if not self.has_permission(permission):
            error_msg = f"Permission denied: {permission.value} required for {self.agent_id}"
            logger.error(error_msg)
            raise PermissionError(error_msg)

    def require_any_permission(self, *permissions: Permission) -> None:
        """
        Require at least one of the specified permissions.

        Args:
            permissions: Required permissions (at least one must be granted)

        Raises:
            PermissionError: If none of the permissions are granted
        """
        if not any(self.has_permission(p) for p in permissions):
            perm_names = [p.value for p in permissions]
            error_msg = (
                f"Permission denied: one of {perm_names} required for {self.agent_id}"
            )
            logger.error(error_msg)
            raise PermissionError(error_msg)

    def require_all_permissions(self, *permissions: Permission) -> None:
        """
        Require all specified permissions.

        Args:
            permissions: Required permissions (all must be granted)

        Raises:
            PermissionError: If any permission is not granted
        """
        missing = [p for p in permissions if not self.has_permission(p)]
        if missing:
            perm_names = [p.value for p in missing]
            error_msg = f"Permission denied: {perm_names} required for {self.agent_id}"
            logger.error(error_msg)
            raise PermissionError(error_msg)


class PermissionChecker:
    """Utility class for permission checks with data filtering."""

    @staticmethod
    def filter_sensitive_data(
        data: Dict[str, Any], context: SecurityContext
    ) -> Dict[str, Any]:
        """
        Filter sensitive data based on security context permissions.

        Args:
            data: Data dictionary to filter
            context: Security context

        Returns:
            Filtered data dictionary
        """
        filtered_data = data.copy()

        # PII fields
        pii_fields = ["ssn", "email", "phone", "address", "date_of_birth"]
        if not context.has_permission(Permission.READ_PII):
            for field in pii_fields:
                if field in filtered_data:
                    filtered_data[field] = "[REDACTED]"
                    logger.debug(f"Redacted PII field: {field}")

        # Financial fields
        financial_fields = [
            "monthly_income",
            "monthly_debt_payments",
            "checking_balance",
            "savings_balance",
            "investment_balance",
        ]
        if not context.has_permission(Permission.READ_FINANCIAL):
            for field in financial_fields:
                if field in filtered_data:
                    filtered_data[field] = "[REDACTED]"
                    logger.debug(f"Redacted financial field: {field}")

        # Credit fields
        credit_fields = [
            "credit_score",
            "credit_utilization",
            "number_of_late_payments_12m",
            "number_of_late_payments_24m",
        ]
        if not context.has_permission(Permission.READ_CREDIT):
            for field in credit_fields:
                if field in filtered_data:
                    filtered_data[field] = "[REDACTED]"
                    logger.debug(f"Redacted credit field: {field}")

        return filtered_data

    @staticmethod
    def create_loan_agent_context(agent_id: str, environment: str = "production") -> SecurityContext:
        """
        Create a security context for loan approval agent.

        Args:
            agent_id: Agent identifier
            environment: Execution environment

        Returns:
            Security context with appropriate permissions
        """
        permissions = {
            Permission.READ_PII,
            Permission.READ_FINANCIAL,
            Permission.READ_CREDIT,
            Permission.WRITE_DECISION,
            Permission.READ_POLICIES,
        }

        # In development/test, allow external API access
        if environment in ["development", "test"]:
            permissions.add(Permission.ACCESS_EXTERNAL_API)

        return SecurityContext(
            agent_id=agent_id,
            permissions=permissions,
            environment=environment,
            metadata={"agent_type": "loan_approval"},
        )