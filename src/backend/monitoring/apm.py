"""
Application Performance Monitoring (APM) with Distributed Tracing.

This module provides APM integration supporting multiple providers:
- DataDog APM
- New Relic
- Prometheus with OpenTelemetry

Features:
- Distributed tracing across all API requests
- Performance monitoring for endpoints, database queries, and external APIs
- Resource utilization tracking
- Custom span creation and annotation
"""

import functools
import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

from ..config.settings import settings

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Optional[Any] = None
_apm_enabled: bool = False
_apm_provider: str = "none"


def init_apm(provider: str = "datadog") -> None:
    """
    Initialize APM provider.

    Args:
        provider: APM provider ('datadog', 'newrelic', 'opentelemetry', or 'none')
    """
    global _tracer, _apm_enabled, _apm_provider

    _apm_provider = provider.lower()

    if _apm_provider == "none" or settings.environment == "test":
        logger.info("APM disabled")
        _apm_enabled = False
        return

    try:
        if _apm_provider == "datadog":
            _init_datadog()
        elif _apm_provider == "newrelic":
            _init_newrelic()
        elif _apm_provider == "opentelemetry":
            _init_opentelemetry()
        else:
            logger.warning(f"Unknown APM provider: {provider}, APM disabled")
            _apm_enabled = False
            return

        _apm_enabled = True
        logger.info(f"APM initialized with provider: {provider}")

    except Exception as e:
        logger.error(f"Failed to initialize APM: {e}")
        _apm_enabled = False


def _init_datadog() -> None:
    """Initialize DataDog APM."""
    global _tracer

    try:
        from ddtrace import config, patch_all, tracer

        # Configure DataDog
        config.env = settings.environment
        config.service = "treebeard-api"
        config.version = settings.app_version

        # Enable analytics
        config.analytics_enabled = True

        # Patch common libraries
        patch_all(logging=True)

        _tracer = tracer
        logger.info("DataDog APM initialized")

    except ImportError:
        logger.error("ddtrace not installed. Install with: pip install ddtrace")
        raise


def _init_newrelic() -> None:
    """Initialize New Relic APM."""
    global _tracer

    try:
        import newrelic.agent

        newrelic.agent.initialize()
        _tracer = newrelic.agent
        logger.info("New Relic APM initialized")

    except ImportError:
        logger.error("newrelic not installed. Install with: pip install newrelic")
        raise


def _init_opentelemetry() -> None:
    """Initialize OpenTelemetry."""
    global _tracer

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Create resource
        resource = Resource.create(
            {
                "service.name": "treebeard-api",
                "service.version": settings.app_version,
                "deployment.environment": settings.environment,
            }
        )

        # Set up tracer provider
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        _tracer = trace.get_tracer(__name__)
        logger.info("OpenTelemetry initialized")

    except ImportError:
        logger.error(
            "opentelemetry not installed. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi"
        )
        raise


def get_tracer() -> Optional[Any]:
    """Get the global tracer instance."""
    return _tracer


@contextmanager
def trace_span(
    name: str,
    service: Optional[str] = None,
    resource: Optional[str] = None,
    span_type: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
):
    """
    Create a traced span context manager.

    Args:
        name: Span name
        service: Service name (e.g., 'postgres', 'redis', 'claude-api')
        resource: Resource being accessed
        span_type: Type of span (e.g., 'db', 'cache', 'http')
        tags: Additional tags to attach to the span

    Example:
        with trace_span('db.query', service='postgres', span_type='db'):
            result = await db.execute(query)
    """
    if not _apm_enabled or _tracer is None:
        yield
        return

    start_time = time.time()

    try:
        if _apm_provider == "datadog":
            with _tracer.trace(name, service=service, resource=resource, span_type=span_type) as span:
                if tags:
                    for key, value in tags.items():
                        span.set_tag(key, value)
                yield span
        elif _apm_provider == "opentelemetry":
            with _tracer.start_as_current_span(name) as span:
                if tags:
                    for key, value in tags.items():
                        span.set_attribute(key, value)
                if service:
                    span.set_attribute("service.name", service)
                if resource:
                    span.set_attribute("resource.name", resource)
                yield span
        else:
            yield

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error in traced span '{name}': {e} (duration: {duration:.3f}s)")
        raise


def trace_async_function(
    operation_name: Optional[str] = None,
    service: Optional[str] = None,
    resource: Optional[str] = None,
):
    """
    Decorator to trace async functions.

    Args:
        operation_name: Name of the operation (defaults to function name)
        service: Service name
        resource: Resource name

    Example:
        @trace_async_function('recommendation.generate', service='recommendation-engine')
        async def generate_recommendation(user_id: UUID):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"

            with trace_span(name, service=service, resource=resource):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def trace_database_query(query_name: str, table: Optional[str] = None):
    """
    Trace a database query.

    Args:
        query_name: Name of the query
        table: Table being queried

    Example:
        with trace_database_query('select_user', table='users'):
            user = await db.fetch_one(query)
    """
    tags = {"db.system": "postgresql"}
    if table:
        tags["db.table"] = table

    return trace_span(
        f"db.{query_name}",
        service="postgres",
        resource=table or query_name,
        span_type="db",
        tags=tags,
    )


def trace_external_api(api_name: str, endpoint: Optional[str] = None):
    """
    Trace an external API call.

    Args:
        api_name: Name of the external API (e.g., 'claude', 'utility-api')
        endpoint: API endpoint being called

    Example:
        with trace_external_api('claude', '/v1/messages'):
            response = await claude_client.create_message(...)
    """
    tags = {"http.url": endpoint} if endpoint else {}

    return trace_span(
        f"external.{api_name}",
        service=api_name,
        resource=endpoint or api_name,
        span_type="http",
        tags=tags,
    )


@contextmanager
def track_recommendation_generation(user_id: str, profile_type: Optional[str] = None):
    """
    Track recommendation generation process.

    Args:
        user_id: User ID
        profile_type: User profile type

    Example:
        with track_recommendation_generation(str(user_id), 'high-usage'):
            recommendations = await engine.generate_recommendations(user_id)
    """
    tags = {
        "user.id": user_id,
        "recommendation.stage": "generation",
    }
    if profile_type:
        tags["user.profile_type"] = profile_type

    with trace_span(
        "recommendation.generate",
        service="recommendation-engine",
        resource=f"user:{user_id}",
        tags=tags,
    ):
        yield


def add_span_tag(key: str, value: Any) -> None:
    """
    Add a tag to the current span.

    Args:
        key: Tag key
        value: Tag value
    """
    if not _apm_enabled or _tracer is None:
        return

    try:
        if _apm_provider == "datadog":
            span = _tracer.current_span()
            if span:
                span.set_tag(key, value)
        elif _apm_provider == "opentelemetry":
            from opentelemetry import trace

            span = trace.get_current_span()
            if span:
                span.set_attribute(key, value)
    except Exception as e:
        logger.debug(f"Failed to add span tag: {e}")


def add_span_error(exception: Exception) -> None:
    """
    Mark the current span as errored.

    Args:
        exception: Exception that occurred
    """
    if not _apm_enabled or _tracer is None:
        return

    try:
        if _apm_provider == "datadog":
            span = _tracer.current_span()
            if span:
                span.set_exc_info(type(exception), exception, exception.__traceback__)
        elif _apm_provider == "opentelemetry":
            from opentelemetry import trace
            from opentelemetry.trace import Status, StatusCode

            span = trace.get_current_span()
            if span:
                span.record_exception(exception)
                span.set_status(Status(StatusCode.ERROR))
    except Exception as e:
        logger.debug(f"Failed to add span error: {e}")
