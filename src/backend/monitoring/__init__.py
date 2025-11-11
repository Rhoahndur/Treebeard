"""
Monitoring and observability package for TreeBeard API.

This package provides comprehensive monitoring, tracing, metrics collection,
error tracking, and alerting capabilities.

Components:
- APM (Application Performance Monitoring) with distributed tracing
- Custom metrics collection for business and application metrics
- Error tracking with Sentry
- Alert rules and notifications
"""

from .apm import (
    get_tracer,
    init_apm,
    trace_async_function,
    trace_database_query,
    trace_external_api,
    track_recommendation_generation,
)
from .metrics import (
    MetricsCollector,
    get_metrics_collector,
    init_metrics,
    track_api_request,
    track_cache_operation,
    track_error,
    track_recommendation,
)
from .sentry_init import init_sentry, sanitize_pii

__all__ = [
    # APM
    "init_apm",
    "get_tracer",
    "trace_async_function",
    "trace_database_query",
    "trace_external_api",
    "track_recommendation_generation",
    # Metrics
    "init_metrics",
    "get_metrics_collector",
    "MetricsCollector",
    "track_api_request",
    "track_cache_operation",
    "track_error",
    "track_recommendation",
    # Sentry
    "init_sentry",
    "sanitize_pii",
]
