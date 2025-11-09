"""Configuration management for loan approval agent."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root (3 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class AgentConfig(BaseSettings):
    """Agent configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Agent settings
    agent_name: str = "loan-approval"
    agent_version: str = "0.1.0"
    environment: str = "development"

    # LLM settings - supports both OpenAI and Azure OpenAI
    # For OpenAI: set openai_api_key and openai_model
    # For Azure: set azure_openai_api_key, azure_openai_endpoint,
    #            azure_openai_deployment, azure_openai_api_version
    use_azure_openai: bool = False  # Set to True to use Azure OpenAI instead of OpenAI

    # OpenAI settings
    openai_api_key: str = Field(default="test-key")  # Loaded from OPENAI_API_KEY env var
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.0
    openai_max_tokens: int = 2000

    # Azure OpenAI settings
    azure_openai_api_key: str | None = None  # Loaded from AZURE_OPENAI_API_KEY env var
    azure_openai_endpoint: str | None = None  # e.g., https://your-resource.openai.azure.com/
    azure_openai_deployment: str | None = None  # Your deployment name
    azure_openai_api_version: str = "2024-02-01"  # Azure OpenAI API version

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

    # LLM Logging
    enable_llm_logging: bool = True
    log_llm_prompts: bool = True  # May contain sensitive data
    log_llm_responses: bool = True
    mlflow_log_llm_models: bool = True
    mlflow_log_llm_inputs_outputs: bool = True

    # Policy documents
    policies_directory: str = "../policies"

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
