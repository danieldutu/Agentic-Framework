"""Application settings and configuration."""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    app_name: str = Field(default="AI Agent Framework", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Gemini AI settings
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-pro", description="Gemini model to use")
    gemini_temperature: float = Field(default=0.7, description="Model temperature")
    gemini_max_tokens: int = Field(
        default=2048, description="Maximum tokens per response"
    )
    gemini_timeout: int = Field(default=30, description="Request timeout in seconds")

    # Agent settings
    max_agents: int = Field(
        default=10, description="Maximum number of concurrent agents"
    )
    agent_timeout: int = Field(default=60, description="Agent task timeout in seconds")
    agent_retry_attempts: int = Field(default=3, description="Number of retry attempts")

    # Communication settings
    communication_type: str = Field(
        default="redis", description="Communication backend type"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    message_queue_size: int = Field(default=1000, description="Message queue size")

    # Memory settings
    memory_backend: str = Field(default="redis", description="Memory backend type")
    memory_ttl: int = Field(default=3600, description="Memory TTL in seconds")
    max_memory_entries: int = Field(default=10000, description="Maximum memory entries")

    # FastAPI settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=False, description="API auto-reload")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")

    # Security settings
    secret_key: str = Field(default="change-me-in-production", description="Secret key")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration"
    )

    # Monitoring settings
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, description="Metrics server port")

    # Database settings (optional)
    database_url: Optional[str] = Field(None, description="Database connection URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Environment variable prefixes
        env_prefix = ""

        # Field aliases for environment variables
        fields = {
            "gemini_api_key": {"env": ["GEMINI_API_KEY", "GOOGLE_API_KEY"]},
            "redis_url": {"env": ["REDIS_URL", "REDIS_CONNECTION_STRING"]},
            "database_url": {"env": ["DATABASE_URL", "DB_URL"]},
        }

    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini-specific configuration."""
        return {
            "api_key": self.gemini_api_key,
            "model": self.gemini_model,
            "temperature": self.gemini_temperature,
            "max_tokens": self.gemini_max_tokens,
            "timeout": self.gemini_timeout,
        }

    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent-specific configuration."""
        return {
            "max_agents": self.max_agents,
            "timeout": self.agent_timeout,
            "retry_attempts": self.agent_retry_attempts,
        }

    def get_communication_config(self) -> Dict[str, Any]:
        """Get communication-specific configuration."""
        return {
            "type": self.communication_type,
            "redis_url": self.redis_url,
            "queue_size": self.message_queue_size,
        }

    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory-specific configuration."""
        return {
            "backend": self.memory_backend,
            "ttl": self.memory_ttl,
            "max_entries": self.max_memory_entries,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Application settings instance
    """
    return Settings()
