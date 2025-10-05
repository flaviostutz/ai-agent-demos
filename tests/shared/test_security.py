"""Tests for shared security utilities."""

import pytest
from shared.security import (
    ContextPermissionManager,
    DataLeakagePreventor,
    SecurityContext,
)


class TestSecurityContext:
    """Test security context functionality."""

    def test_security_context_creation(self):
        """Test creating a security context."""
        context = SecurityContext(
            user_id="user123",
            roles=["loan_officer"],
            permissions={"tool:loan_approval"},
            allowed_data_domains={"public"},
        )

        assert context.user_id == "user123"
        assert "loan_officer" in context.roles
        assert "tool:loan_approval" in context.permissions


class TestDataLeakagePreventor:
    """Test data leakage prevention."""

    def test_mask_ssn(self):
        """Test masking of SSN."""
        context = SecurityContext(
            user_id="user123", roles=[], permissions=set(), allowed_data_domains=set()
        )

        text = "The SSN is 123-45-6789"
        masked = DataLeakagePreventor.mask_sensitive_data(text, context)

        assert "123-45-6789" not in masked
        assert "[REDACTED_SSN]" in masked

    def test_mask_credit_card(self):
        """Test masking of credit card numbers."""
        context = SecurityContext(
            user_id="user123", roles=[], permissions=set(), allowed_data_domains=set()
        )

        text = "Card number: 4532-1234-5678-9010"
        masked = DataLeakagePreventor.mask_sensitive_data(text, context)

        assert "4532-1234-5678-9010" not in masked
        assert "[REDACTED_CREDIT_CARD]" in masked

    def test_no_mask_with_pii_access(self):
        """Test that data is not masked with PII access permission."""
        context = SecurityContext(
            user_id="user123",
            roles=[],
            permissions={"pii_access"},
            allowed_data_domains=set(),
        )

        text = "The SSN is 123-45-6789"
        masked = DataLeakagePreventor.mask_sensitive_data(text, context)

        assert "123-45-6789" in masked  # Not masked

    def test_validate_tool_access_allowed(self):
        """Test tool access validation - allowed."""
        context = SecurityContext(
            user_id="user123",
            roles=[],
            permissions={"tool:loan_approval"},
            allowed_data_domains=set(),
        )

        assert DataLeakagePreventor.validate_tool_access("loan_approval", context)

    def test_validate_tool_access_denied(self):
        """Test tool access validation - denied."""
        context = SecurityContext(
            user_id="user123", roles=[], permissions=set(), allowed_data_domains=set()
        )

        assert not DataLeakagePreventor.validate_tool_access("loan_approval", context)

    def test_validate_tool_access_admin_role(self):
        """Test tool access with admin role."""
        context = SecurityContext(
            user_id="admin123",
            roles=["admin"],
            permissions=set(),
            allowed_data_domains=set(),
        )

        assert DataLeakagePreventor.validate_tool_access("any_tool", context)

    def test_sanitize_output_recursive(self):
        """Test recursive sanitization of output."""
        context = SecurityContext(
            user_id="user123", roles=[], permissions=set(), allowed_data_domains=set()
        )

        output = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "contact": {"email": "john@example.com", "phone": "555-123-4567"},
            "cards": ["4532-1234-5678-9010"],
        }

        sanitized = DataLeakagePreventor.sanitize_output(output, context)

        assert "[REDACTED_SSN]" in sanitized["ssn"]
        assert "[REDACTED_EMAIL]" in sanitized["contact"]["email"]
        assert "[REDACTED_PHONE]" in sanitized["contact"]["phone"]


class TestContextPermissionManager:
    """Test context permission manager."""

    def test_can_access_allowed_domain(self):
        """Test access to allowed data domain."""
        context = SecurityContext(
            user_id="user123",
            roles=[],
            permissions=set(),
            allowed_data_domains={"public", "internal"},
        )

        manager = ContextPermissionManager(context)

        assert manager.can_access_data_domain("public")
        assert manager.can_access_data_domain("internal")
        assert not manager.can_access_data_domain("confidential")

    def test_admin_can_access_all_domains(self):
        """Test admin can access all domains."""
        context = SecurityContext(
            user_id="admin123",
            roles=["admin"],
            permissions=set(),
            allowed_data_domains=set(),
        )

        manager = ContextPermissionManager(context)

        assert manager.can_access_data_domain("any_domain")

    def test_filter_documents_by_domain(self):
        """Test document filtering by domain."""
        context = SecurityContext(
            user_id="user123",
            roles=[],
            permissions=set(),
            allowed_data_domains={"public"},
        )

        manager = ContextPermissionManager(context)

        documents = [
            {"content": "Public doc", "domain": "public"},
            {"content": "Internal doc", "domain": "internal"},
            {"content": "Confidential doc", "domain": "confidential"},
        ]

        filtered = manager.filter_documents(documents)

        assert len(filtered) == 1
        assert filtered[0]["domain"] == "public"

    def test_can_execute_tool(self):
        """Test tool execution permission."""
        context = SecurityContext(
            user_id="user123",
            roles=[],
            permissions={"tool:loan_approval"},
            allowed_data_domains=set(),
        )

        manager = ContextPermissionManager(context)

        assert manager.can_execute_tool("loan_approval")
        assert not manager.can_execute_tool("admin_tool")
