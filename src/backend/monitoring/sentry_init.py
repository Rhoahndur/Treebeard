"""
Sentry Error Tracking Integration.

This module provides Sentry error tracking with:
- Exception capture and grouping
- User context (anonymized)
- Request context
- Performance monitoring
- PII sanitization
"""

import logging
import re
from typing import Any, Dict, Optional

from config.settings import settings

logger = logging.getLogger(__name__)

# Patterns for PII detection
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}

# Keys that should be redacted
SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "access_token",
    "auth_token",
    "private_key",
    "client_secret",
    "credit_card",
    "ssn",
    "social_security",
}


def sanitize_pii(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sanitize PII from Sentry events.

    Args:
        event: Sentry event dictionary
        hint: Additional context

    Returns:
        Sanitized event or None to drop the event
    """
    try:
        # Sanitize request data
        if "request" in event:
            event["request"] = _sanitize_dict(event["request"])

        # Sanitize extra data
        if "extra" in event:
            event["extra"] = _sanitize_dict(event["extra"])

        # Sanitize breadcrumbs
        if "breadcrumbs" in event:
            for breadcrumb in event["breadcrumbs"]:
                if "data" in breadcrumb:
                    breadcrumb["data"] = _sanitize_dict(breadcrumb["data"])

        # Sanitize user data (keep only non-PII)
        if "user" in event:
            sanitized_user = {}
            if "id" in event["user"]:
                # Hash the user ID for privacy
                sanitized_user["id"] = _hash_value(str(event["user"]["id"]))
            if "username" in event["user"]:
                sanitized_user["username"] = _hash_value(event["user"]["username"])
            event["user"] = sanitized_user

        # Sanitize exception messages
        if "exception" in event:
            for exception in event["exception"].get("values", []):
                if "value" in exception:
                    exception["value"] = _sanitize_string(exception["value"])

        return event

    except Exception as e:
        logger.error(f"Error sanitizing PII from Sentry event: {e}")
        return event


def _sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize a dictionary.

    Args:
        data: Dictionary to sanitize

    Returns:
        Sanitized dictionary
    """
    sanitized = {}

    for key, value in data.items():
        # Check if key is sensitive
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [_sanitize_dict(item) if isinstance(item, dict) else _sanitize_value(item) for item in value]
        else:
            sanitized[key] = _sanitize_value(value)

    return sanitized


def _sanitize_value(value: Any) -> Any:
    """
    Sanitize a single value.

    Args:
        value: Value to sanitize

    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        return _sanitize_string(value)
    return value


def _sanitize_string(text: str) -> str:
    """
    Sanitize PII from a string.

    Args:
        text: String to sanitize

    Returns:
        Sanitized string
    """
    sanitized = text

    # Replace email addresses
    sanitized = PII_PATTERNS["email"].sub("[EMAIL]", sanitized)

    # Replace phone numbers
    sanitized = PII_PATTERNS["phone"].sub("[PHONE]", sanitized)

    # Replace SSNs
    sanitized = PII_PATTERNS["ssn"].sub("[SSN]", sanitized)

    # Replace credit card numbers
    sanitized = PII_PATTERNS["credit_card"].sub("[CREDIT_CARD]", sanitized)

    # Replace IP addresses (optional - may be needed for debugging)
    # sanitized = PII_PATTERNS['ip_address'].sub('[IP]', sanitized)

    return sanitized


def _hash_value(value: str) -> str:
    """
    Hash a value for anonymization.

    Args:
        value: Value to hash

    Returns:
        Hashed value (first 8 characters of SHA256)
    """
    import hashlib

    return hashlib.sha256(value.encode()).hexdigest()[:8]


def init_sentry(dsn: Optional[str] = None, environment: Optional[str] = None) -> None:
    """
    Initialize Sentry error tracking.

    Args:
        dsn: Sentry DSN (Data Source Name)
        environment: Environment name ('development', 'staging', 'production')
    """
    dsn = dsn or getattr(settings, "sentry_dsn", None)
    environment = environment or settings.environment

    if not dsn:
        logger.info("Sentry DSN not configured, error tracking disabled")
        return

    if environment == "test":
        logger.info("Sentry disabled in test environment")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        # Determine sampling rate based on environment
        traces_sample_rate = 1.0 if environment == "production" else 0.1
        profiles_sample_rate = 1.0 if environment == "production" else 0.0

        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=f"treebeard@{settings.app_version}",
            # Performance monitoring
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above as breadcrumbs
                    event_level=logging.ERROR,  # Send errors as events
                ),
                SqlalchemyIntegration(),
            ],
            # PII sanitization
            before_send=sanitize_pii,
            # Additional options
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send PII by default
            max_breadcrumbs=50,
            debug=settings.debug,
        )

        logger.info(f"Sentry initialized for environment: {environment}")

    except ImportError:
        logger.error("sentry-sdk not installed. Install with: pip install sentry-sdk[fastapi]")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def capture_exception(exception: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Manually capture an exception in Sentry.

    Args:
        exception: Exception to capture
        context: Additional context to attach
    """
    try:
        import sentry_sdk

        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_context(key, value)
                sentry_sdk.capture_exception(exception)
        else:
            sentry_sdk.capture_exception(exception)

    except ImportError:
        logger.error("sentry-sdk not installed, cannot capture exception")
    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")


def capture_message(message: str, level: str = "info", context: Optional[Dict[str, Any]] = None) -> None:
    """
    Capture a message in Sentry.

    Args:
        message: Message to capture
        level: Severity level ('debug', 'info', 'warning', 'error', 'fatal')
        context: Additional context to attach
    """
    try:
        import sentry_sdk

        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_context(key, value)
                sentry_sdk.capture_message(message, level=level)
        else:
            sentry_sdk.capture_message(message, level=level)

    except ImportError:
        logger.error("sentry-sdk not installed, cannot capture message")
    except Exception as e:
        logger.error(f"Failed to capture message in Sentry: {e}")


def set_user_context(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
    """
    Set user context for Sentry events.

    Args:
        user_id: User ID (will be hashed)
        email: User email (will be sanitized)
        username: Username (will be hashed)
    """
    try:
        import sentry_sdk

        user_data = {"id": _hash_value(user_id)}

        if username:
            user_data["username"] = _hash_value(username)

        # Don't include email for privacy
        # if email:
        #     user_data['email'] = '[EMAIL]'

        sentry_sdk.set_user(user_data)

    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to set user context in Sentry: {e}")


def add_breadcrumb(
    category: str,
    message: str,
    level: str = "info",
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Add a breadcrumb to Sentry.

    Args:
        category: Breadcrumb category
        message: Breadcrumb message
        level: Severity level
        data: Additional data
    """
    try:
        import sentry_sdk

        sentry_sdk.add_breadcrumb(
            category=category,
            message=message,
            level=level,
            data=_sanitize_dict(data) if data else None,
        )

    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to add breadcrumb in Sentry: {e}")
