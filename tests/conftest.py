"""Test fixtures for agents."""

import pytest
from shared.security import SecurityContext


@pytest.fixture
def security_context():
    """Provide a default security context for tests."""
    return SecurityContext(
        user_id="test_user",
        roles=["loan_officer", "tester"],
        permissions={"tool:loan_approval", "pii_access"},
        allowed_data_domains={"public", "internal", "test"},
    )


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Provide a mock OpenAI API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123456789")


@pytest.fixture
def sample_config_path(tmp_path):
    """Create a temporary config file for testing."""
    config_content = """
agents:
  loan_approval:
    name: "loan_approval"
    version: "0.1.0"
    llm:
      provider: "openai"
      model: "gpt-4"
      temperature: 0.0
    vector_store:
      provider: "chroma"
      collection_name: "test_loan_rules"
      persist_directory: "./test_data/chroma"
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return str(config_file)
