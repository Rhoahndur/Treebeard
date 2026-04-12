"""
Application settings and configuration.

Uses Pydantic Settings for environment variable management.
"""

import contextlib
import json
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _parse_list_env(v: object, default: list[str] | None = None) -> list[str]:
    """Parse a list-of-strings from JSON-array, comma-separated, or list input.

    Strips whitespace and drops empty items. Returns `default` (or []) when the
    value is None or empty. Shared by the CORS origins and OpenRouter fallback
    model list validators.
    """
    if v is None or v == "":
        return list(default) if default is not None else []
    if isinstance(v, list):
        return [str(item).strip() for item in v if str(item).strip()]
    if isinstance(v, str):
        parsed: object = None
        with contextlib.suppress(json.JSONDecodeError):
            parsed = json.loads(v)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in v.split(",") if item.strip()]
    return list(default) if default is not None else []


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set in .env file or system environment.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow")

    # Application
    app_name: str = Field(default="TreeBeard Energy Recommendation API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment: development, staging, production")

    # Database
    database_url: str = Field(
        default="postgresql://treebeard:treebeard@localhost:5432/treebeard", description="PostgreSQL database URL"
    )
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Maximum number of overflow connections")
    database_echo: bool = Field(default=False, description="Echo SQL queries (for debugging)")

    # Redis Cache
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    cache_ttl_seconds: int = Field(default=86400, description="Default cache TTL (24 hours)")

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API version 1 prefix")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], description="Allowed CORS origins"
    )
    max_upload_size_mb: int = Field(default=10, description="Maximum upload size in MB")

    # Security
    secret_key: str = Field(
        default="development-secret-key-change-in-production", description="Secret key for JWT and encryption"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=60 * 24, description="JWT expiration in minutes (24 hours)")

    # Recommendation Engine
    recommendation_cache_ttl_seconds: int = Field(default=86400, description="Recommendation cache TTL (24 hours)")
    max_recommendations: int = Field(default=3, description="Maximum number of recommendations to return")

    # External APIs — OpenRouter (preferred for demo, free tier)
    openrouter_api_key: str | None = Field(None, description="OpenRouter API key (free tier available)")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    # `openrouter/free` is OpenRouter's routing pseudo-model — it auto-selects an
    # available free-tier backend per request, which is why it's the safest default
    # for a demo that doesn't want to track the rotating free model catalog by hand.
    openrouter_model: str = Field(default="openrouter/free", description="OpenRouter primary model (free tier)")
    # Optional explicit fallback list; leave empty to let `openrouter_model` handle
    # routing alone. `NoDecode` skips pydantic-settings' source-level JSON parsing
    # so the field validator can accept both JSON-array and comma-separated env
    # var formats (without it the source layer errors on non-JSON strings).
    openrouter_fallback_models: Annotated[list[str], NoDecode] = Field(
        default_factory=list, description="Ordered fallback model IDs for OpenRouter"
    )

    # External APIs — OpenAI (fallback if OpenRouter not configured)
    openai_api_key: str | None = Field(None, description="OpenAI API key for explanation generation")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")

    # Data Processing
    min_usage_months: int = Field(default=3, description="Minimum months of usage data required")
    preferred_usage_months: int = Field(default=12, description="Preferred months of usage data")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")

    # Monitoring & Observability
    # Defaults off so local and default Railway deploys don't spam startup with
    # ImportError noise from uninstalled ddtrace. Opt in via env vars in envs that
    # actually have DataDog/Prometheus wired up.
    monitoring_enabled: bool = Field(default=False, description="Enable monitoring and metrics")
    apm_provider: str = Field(default="none", description="APM provider: datadog, newrelic, opentelemetry, none")
    metrics_backend: str = Field(default="logging", description="Metrics backend: datadog, prometheus, logging")

    # DataDog
    datadog_agent_host: str = Field(default="localhost", description="DataDog agent host")
    datadog_agent_port: int = Field(default=8125, description="DataDog agent port")

    # Sentry
    sentry_dsn: str | None = Field(None, description="Sentry DSN for error tracking")
    sentry_traces_sample_rate: float = Field(default=1.0, description="Sentry traces sample rate (0.0-1.0)")
    sentry_profiles_sample_rate: float = Field(default=1.0, description="Sentry profiles sample rate (0.0-1.0)")

    # Alerting
    pagerduty_integration_key: str | None = Field(None, description="PagerDuty integration key")
    pagerduty_routing_key: str | None = Field(None, description="PagerDuty routing key")
    slack_webhook_url: str | None = Field(None, description="Slack webhook URL for alerts")
    slack_bot_token: str | None = Field(None, description="Slack bot token")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, v) -> list[str]:
        """Parse CORS origins from JSON array, comma-separated, or list input."""
        return _parse_list_env(v, default=["http://localhost:3000"])

    @field_validator("openrouter_fallback_models", mode="before")
    @classmethod
    def validate_openrouter_fallback_models(cls, v) -> list[str]:
        """Parse fallback model list from JSON array, comma-separated, or list input."""
        return _parse_list_env(v)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = ["development", "staging", "production", "test"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper


# Create global settings instance
settings = Settings()  # type: ignore[call-arg]
