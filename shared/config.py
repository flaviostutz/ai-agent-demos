"""Configuration management for agents."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration."""

    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.0)
    max_tokens: int = Field(default=4096)
    api_key: str | None = Field(default=None)


class VectorStoreConfig(BaseModel):
    """Vector store configuration."""

    provider: str = Field(default="chroma")
    collection_name: str = Field(default="documents")
    persist_directory: str = Field(default="./data/chroma")


class AgentConfig(BaseModel):
    """Base agent configuration."""

    name: str
    version: str = Field(default="0.1.0")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    max_iterations: int = Field(default=10)
    verbose: bool = Field(default=False)


class Config:
    """Global configuration manager."""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path or os.getenv(
            "CONFIG_PATH", str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file) as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get agent-specific configuration."""
        agent_config = self._config.get("agents", {}).get(agent_name, {})
        agent_config["name"] = agent_name

        # Override with environment variables
        if api_key := os.getenv("OPENAI_API_KEY"):
            if "llm" not in agent_config:
                agent_config["llm"] = {}
            agent_config["llm"]["api_key"] = api_key

        return AgentConfig(**agent_config)


# Global config instance
_config_instance: Config | None = None


def get_config() -> Config:
    """Get global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
