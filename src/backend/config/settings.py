"""
Application settings and configuration.

Uses Pydantic Settings for environment variable management.
"""

import contextlib
import json

from pydantic import Field, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


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


class _RawListEnvSourceMixin:
    """Let field validators parse list-like env vars instead of forcing JSON."""

    raw_list_fields = {"cors_origins", "openrouter_fallback_models"}

    def prepare_field_value(self, field_name: str, field, value, value_is_complex: bool):
        if field_name in self.raw_list_fields and isinstance(value, str):
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class _EnvSettingsSource(_RawListEnvSourceMixin, EnvSettingsSource):
    pass


class _DotEnvSettingsSource(_RawListEnvSourceMixin, DotEnvSettingsSource):
    pass


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set in .env file or system environment.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            _EnvSettingsSource(settings_cls),
            _DotEnvSettingsSource(settings_cls),
            file_secret_settings,
        )

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
    admin_api_enabled: bool = Field(default=False, description="Expose unfinished admin API routes")

    # Security
    secret_key: str = Field(
        default="development-secret-key-change-in-production", description="Secret key for JWT and encryption"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=60 * 24, description="JWT expiration in minutes (24 hours)")
    rate_limit_per_user: int = Field(
        default=100, description="Authenticated user rate limit count per one-minute window"
    )
    rate_limit_per_ip: int = Field(default=1000, description="IP rate limit count per one-hour window")
    recommendation_rate_limit_per_minute: int = Field(
        default=10, description="Authenticated user rate limit count for recommendation generation per minute"
    )

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
    # routing alone. Accepts either a JSON-array or comma-separated env var.
    openrouter_fallback_models: list[str] = Field(
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

    @field_validator("rate_limit_per_user", "rate_limit_per_ip", "recommendation_rate_limit_per_minute", mode="before")
    @classmethod
    def validate_rate_limit_count(cls, v) -> int:
        """Parse integer rate-limit env vars, accepting legacy '100/minute' style values."""
        if isinstance(v, str):
            value = v.strip()
            if "/" in value:
                value = value.split("/", 1)[0].strip()
            return int(value)
        return v

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

    @model_validator(mode="after")
    def validate_deployment_safety(self) -> "Settings":
        """Fail fast on unsafe production defaults while keeping local setup easy."""
        if self.environment != "production":
            return self

        unsafe_secret_keys = {
            "",
            "development-secret-key-change-in-production",
            "your-production-secret-key-here",
        }
        if self.secret_key in unsafe_secret_keys or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be set to a non-development value when ENVIRONMENT=production")

        localhost_origins = {
            origin
            for origin in self.cors_origins
            if "localhost" in origin or "127.0.0.1" in origin or origin.startswith("http://0.0.0.0")
        }
        if localhost_origins:
            raise ValueError(
                "CORS_ORIGINS must not include localhost-only origins when ENVIRONMENT=production: "
                + ", ".join(sorted(localhost_origins))
            )

        return self


# Create global settings instance
settings = Settings()  # type: ignore[call-arg]
