"""Security and context permissioning utilities."""

import hashlib
import re
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class SecurityContext(BaseModel):
    """Security context for agent operations."""

    user_id: str
    roles: List[str] = Field(default_factory=list)
    permissions: Set[str] = Field(default_factory=set)
    allowed_data_domains: Set[str] = Field(default_factory=set)


class DataLeakagePreventor:
    """Prevents data leakage in agent responses."""

    # Patterns for sensitive data
    PII_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    }

    @classmethod
    def mask_sensitive_data(cls, text: str, context: SecurityContext) -> str:
        """Mask sensitive data in text based on permissions."""
        masked_text = text

        # If user doesn't have PII access, mask sensitive data
        if "pii_access" not in context.permissions:
            for pattern_name, pattern in cls.PII_PATTERNS.items():
                masked_text = re.sub(pattern, f"[REDACTED_{pattern_name.upper()}]", masked_text)

        return masked_text

    @classmethod
    def validate_tool_access(cls, tool_name: str, context: SecurityContext) -> bool:
        """Validate if user has access to a specific tool."""
        # Check if user has permission for this tool
        required_permission = f"tool:{tool_name}"
        return required_permission in context.permissions or "admin" in context.roles

    @classmethod
    def sanitize_output(cls, output: Dict[str, Any], context: SecurityContext) -> Dict[str, Any]:
        """Sanitize agent output based on security context."""
        sanitized = output.copy()

        # Recursively sanitize string values
        for key, value in sanitized.items():
            if isinstance(value, str):
                sanitized[key] = cls.mask_sensitive_data(value, context)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_output(value, context)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.mask_sensitive_data(v, context) if isinstance(v, str) else v
                    for v in value
                ]

        return sanitized


class ContextPermissionManager:
    """Manages context-based permissions for agent operations."""

    def __init__(self, security_context: SecurityContext):
        self.context = security_context

    def can_access_data_domain(self, domain: str) -> bool:
        """Check if user can access a specific data domain."""
        return domain in self.context.allowed_data_domains or "admin" in self.context.roles

    def can_execute_tool(self, tool_name: str) -> bool:
        """Check if user can execute a specific tool."""
        return DataLeakagePreventor.validate_tool_access(tool_name, self.context)

    def filter_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter documents based on user's data domain access."""
        filtered = []
        for doc in documents:
            doc_domain = doc.get("domain", "public")
            if self.can_access_data_domain(doc_domain):
                filtered.append(doc)
        return filtered

    def get_filtered_context(self, full_context: str) -> str:
        """Get filtered context based on permissions."""
        return DataLeakagePreventor.mask_sensitive_data(full_context, self.context)


def hash_sensitive_field(value: str) -> str:
    """Hash sensitive field for logging/metrics without exposing actual value."""
    return hashlib.sha256(value.encode()).hexdigest()[:16]
