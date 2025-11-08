"""Configuration management for loan approval agent."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseSettings):
    """Agent configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Agent settings
    agent_name: str = "loan-approval"
    agent_version: str = "0.1.0"
    environment: str = "development"

    # LLM settings
    openai_api_key: str = "test-key"  # Default for testing
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.0
    openai_max_tokens: int = 2000

    # MLFlow settings
    mlflow_tracking_uri: str | None = None
    mlflow_experiment_name: str = "loan-approval-agent"

    # Databricks settings
    databricks_host: str | None = None
    databricks_token: str | None = None

    # Monitoring
    teams_webhook_url: str | None = None
    enable_tracing: bool = True
    enable_metrics: bool = True
    log_level: str = "INFO"

    # Policy documents
    policies_directory: str = "./policies"

    # API settings
    # Binding to 0.0.0.0 allows container networking
    # Restrict in production via firewall/security groups
    api_host: str = "0.0.0.0"  # noqa: S104
    api_port: int = 8000

    # Risk scoring thresholds
    min_credit_score: int = 580
    max_dti_ratio: float = 0.43
    min_employment_months: int = 6
    bankruptcy_years_threshold: int = 7
    foreclosure_years_threshold: int = 7

    # Loan limits
    max_loan_amount: int = 10000000
    min_loan_amount: int = 1000

    def get_mlflow_tracking_uri(self) -> str:
        """Get MLFlow tracking URI, fallback to local if not configured."""
        return self.mlflow_tracking_uri or "./mlruns"


# Global config instance
config = AgentConfig()
