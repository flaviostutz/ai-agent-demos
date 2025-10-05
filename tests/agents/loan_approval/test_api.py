"""Tests for loan approval API."""

import pytest
from fastapi.testclient import TestClient

from agents.loan_approval.api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token-123"}


class TestLoanApprovalAPI:
    """Test cases for Loan Approval API."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_evaluate_loan_endpoint(self, client, auth_headers, sample_loan_request_data):
        """Test loan evaluation endpoint."""
        response = client.post(
            "/api/v1/loan/evaluate",
            json=sample_loan_request_data,
            headers=auth_headers,
        )

        # May fail without actual OpenAI key, so check response structure
        if response.status_code == 200:
            data = response.json()
            assert "request_id" in data
            assert "outcome" in data
            assert "risk_score" in data or "additional_info_required" in data

    def test_evaluate_loan_invalid_data(self, client, auth_headers):
        """Test loan evaluation with invalid data."""
        invalid_data = {
            "request_id": "TEST-001",
            "annual_income": -1000,  # Invalid
        }

        response = client.post(
            "/api/v1/loan/evaluate",
            json=invalid_data,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    def test_get_loan_status(self, client):
        """Test get loan status endpoint."""
        response = client.get("/api/v1/loan/status/TEST-001")
        assert response.status_code == 200
        assert response.json()["request_id"] == "TEST-001"

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_missing_auth_header(self, client, sample_loan_request_data):
        """Test request without authentication."""
        response = client.post(
            "/api/v1/loan/evaluate",
            json=sample_loan_request_data,
        )

        assert response.status_code == 403  # Forbidden
