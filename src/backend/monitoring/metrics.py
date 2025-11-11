"""
Custom Metrics Collection.

This module provides custom metrics tracking for business and application metrics.
Supports multiple backends: DataDog StatsD, Prometheus, or simple logging.

Metrics tracked:
- API endpoint latency (P50, P95, P99)
- Request counts and error rates
- Database query performance
- External API calls (Claude API)
- Cache operations and hit rates
- Background job performance
- Business metrics (recommendations, users, etc.)
"""

import logging
import time
from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict, List, Optional

from ..config.settings import settings

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MetricsCollector:
    """
    Metrics collector that supports multiple backends.

    Backends:
    - DataDog StatsD
    - Prometheus
    - Logging (fallback)
    """

    def __init__(self, backend: str = "datadog"):
        """
        Initialize metrics collector.

        Args:
            backend: Metrics backend ('datadog', 'prometheus', 'logging')
        """
        self.backend = backend.lower()
        self.enabled = settings.environment != "test"
        self._client: Optional[Any] = None

        if self.enabled:
            self._initialize_backend()

    def _initialize_backend(self) -> None:
        """Initialize the metrics backend."""
        try:
            if self.backend == "datadog":
                self._init_datadog()
            elif self.backend == "prometheus":
                self._init_prometheus()
            elif self.backend == "logging":
                logger.info("Using logging metrics backend")
            else:
                logger.warning(f"Unknown metrics backend: {self.backend}, using logging")
                self.backend = "logging"
        except Exception as e:
            logger.error(f"Failed to initialize metrics backend: {e}")
            self.backend = "logging"

    def _init_datadog(self) -> None:
        """Initialize DataDog StatsD client."""
        try:
            from datadog import initialize, statsd

            initialize(
                statsd_host="localhost",
                statsd_port=8125,
                statsd_namespace="treebeard",
            )
            self._client = statsd
            logger.info("DataDog metrics initialized")
        except ImportError:
            logger.error("datadog not installed. Install with: pip install datadog")
            self.backend = "logging"

    def _init_prometheus(self) -> None:
        """Initialize Prometheus client."""
        try:
            from prometheus_client import Counter, Gauge, Histogram

            self._client = {
                "counter": {},
                "gauge": {},
                "histogram": {},
            }
            logger.info("Prometheus metrics initialized")
        except ImportError:
            logger.error("prometheus_client not installed. Install with: pip install prometheus-client")
            self.backend = "logging"

    def increment(
        self,
        metric_name: str,
        value: float = 1,
        tags: Optional[List[str]] = None,
        sample_rate: float = 1.0,
    ) -> None:
        """
        Increment a counter metric.

        Args:
            metric_name: Name of the metric
            value: Value to increment by
            tags: List of tags (e.g., ['endpoint:/api/v1/recommendations', 'status:200'])
            sample_rate: Sampling rate (0.0 to 1.0)
        """
        if not self.enabled:
            return

        try:
            if self.backend == "datadog":
                self._client.increment(metric_name, value=value, tags=tags, sample_rate=sample_rate)
            elif self.backend == "prometheus":
                # Prometheus counter implementation
                pass
            else:
                logger.debug(f"METRIC [counter] {metric_name}={value} tags={tags}")
        except Exception as e:
            logger.error(f"Failed to increment metric {metric_name}: {e}")

    def gauge(
        self, metric_name: str, value: float, tags: Optional[List[str]] = None, sample_rate: float = 1.0
    ) -> None:
        """
        Set a gauge metric.

        Args:
            metric_name: Name of the metric
            value: Gauge value
            tags: List of tags
            sample_rate: Sampling rate
        """
        if not self.enabled:
            return

        try:
            if self.backend == "datadog":
                self._client.gauge(metric_name, value, tags=tags, sample_rate=sample_rate)
            elif self.backend == "prometheus":
                # Prometheus gauge implementation
                pass
            else:
                logger.debug(f"METRIC [gauge] {metric_name}={value} tags={tags}")
        except Exception as e:
            logger.error(f"Failed to set gauge {metric_name}: {e}")

    def histogram(
        self, metric_name: str, value: float, tags: Optional[List[str]] = None, sample_rate: float = 1.0
    ) -> None:
        """
        Record a histogram value.

        Args:
            metric_name: Name of the metric
            value: Value to record
            tags: List of tags
            sample_rate: Sampling rate
        """
        if not self.enabled:
            return

        try:
            if self.backend == "datadog":
                self._client.histogram(metric_name, value, tags=tags, sample_rate=sample_rate)
            elif self.backend == "prometheus":
                # Prometheus histogram implementation
                pass
            else:
                logger.debug(f"METRIC [histogram] {metric_name}={value} tags={tags}")
        except Exception as e:
            logger.error(f"Failed to record histogram {metric_name}: {e}")

    def timing(
        self,
        metric_name: str,
        value: float,
        tags: Optional[List[str]] = None,
        sample_rate: float = 1.0,
    ) -> None:
        """
        Record a timing metric (in milliseconds).

        Args:
            metric_name: Name of the metric
            value: Duration in milliseconds
            tags: List of tags
            sample_rate: Sampling rate
        """
        if not self.enabled:
            return

        try:
            if self.backend == "datadog":
                self._client.timing(metric_name, value, tags=tags, sample_rate=sample_rate)
            elif self.backend == "prometheus":
                # Prometheus histogram for timing
                pass
            else:
                logger.debug(f"METRIC [timing] {metric_name}={value}ms tags={tags}")
        except Exception as e:
            logger.error(f"Failed to record timing {metric_name}: {e}")

    @contextmanager
    def timed(self, metric_name: str, tags: Optional[List[str]] = None):
        """
        Context manager for timing operations.

        Args:
            metric_name: Name of the metric
            tags: List of tags

        Example:
            with metrics.timed('api.request', tags=['endpoint:/health']):
                await process_request()
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.timing(metric_name, duration_ms, tags=tags)

    def set(self, metric_name: str, value: float, tags: Optional[List[str]] = None) -> None:
        """
        Set a metric value (similar to gauge but for unique values).

        Args:
            metric_name: Name of the metric
            value: Value to set
            tags: List of tags
        """
        if not self.enabled:
            return

        try:
            if self.backend == "datadog":
                self._client.set(metric_name, value, tags=tags)
            else:
                logger.debug(f"METRIC [set] {metric_name}={value} tags={tags}")
        except Exception as e:
            logger.error(f"Failed to set metric {metric_name}: {e}")


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def init_metrics(backend: str = "datadog") -> MetricsCollector:
    """
    Initialize the global metrics collector.

    Args:
        backend: Metrics backend to use

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    _metrics_collector = MetricsCollector(backend=backend)
    return _metrics_collector


def get_metrics_collector() -> MetricsCollector:
    """
    Get the global metrics collector instance.

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(backend="logging")
    return _metrics_collector


# Convenience functions for common metrics


def track_api_request(
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
) -> None:
    """
    Track an API request.

    Args:
        endpoint: API endpoint path
        method: HTTP method
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user ID
    """
    metrics = get_metrics_collector()

    tags = [
        f"endpoint:{endpoint}",
        f"method:{method}",
        f"status:{status_code}",
    ]

    if user_id:
        tags.append(f"user:{user_id}")

    # Request count
    metrics.increment("api.requests", tags=tags)

    # Request duration
    metrics.histogram("api.request.duration", duration_ms, tags=tags)

    # Error tracking
    if status_code >= 400:
        metrics.increment("api.errors", tags=tags)


def track_cache_operation(
    operation: str, key_pattern: str, hit: bool, duration_ms: Optional[float] = None
) -> None:
    """
    Track a cache operation.

    Args:
        operation: Cache operation ('get', 'set', 'delete')
        key_pattern: Cache key pattern
        hit: Whether the operation was a hit (for 'get')
        duration_ms: Operation duration in milliseconds
    """
    metrics = get_metrics_collector()

    tags = [f"operation:{operation}", f"key_pattern:{key_pattern}"]

    # Cache operation count
    metrics.increment("cache.operations", tags=tags)

    # Cache hit/miss
    if operation == "get":
        result_tag = "hit" if hit else "miss"
        metrics.increment("cache.result", tags=[*tags, f"result:{result_tag}"])

    # Cache operation duration
    if duration_ms is not None:
        metrics.timing("cache.operation.duration", duration_ms, tags=tags)


def track_database_query(query_type: str, table: str, duration_ms: float, success: bool = True) -> None:
    """
    Track a database query.

    Args:
        query_type: Type of query ('select', 'insert', 'update', 'delete')
        table: Table name
        duration_ms: Query duration in milliseconds
        success: Whether the query succeeded
    """
    metrics = get_metrics_collector()

    tags = [f"query_type:{query_type}", f"table:{table}", f"success:{success}"]

    # Query count
    metrics.increment("database.queries", tags=tags)

    # Query duration
    metrics.histogram("database.query.duration", duration_ms, tags=tags)

    # Slow query detection (> 1 second)
    if duration_ms > 1000:
        metrics.increment("database.slow_queries", tags=tags)


def track_external_api_call(
    api_name: str, endpoint: str, duration_ms: float, status_code: Optional[int] = None, success: bool = True
) -> None:
    """
    Track an external API call.

    Args:
        api_name: Name of the external API ('claude', 'utility-api', etc.)
        endpoint: API endpoint
        duration_ms: Call duration in milliseconds
        status_code: HTTP status code
        success: Whether the call succeeded
    """
    metrics = get_metrics_collector()

    tags = [f"api:{api_name}", f"endpoint:{endpoint}", f"success:{success}"]

    if status_code:
        tags.append(f"status:{status_code}")

    # API call count
    metrics.increment("external_api.calls", tags=tags)

    # API call duration
    metrics.histogram("external_api.duration", duration_ms, tags=tags)

    # Error tracking
    if not success or (status_code and status_code >= 400):
        metrics.increment("external_api.errors", tags=tags)


def track_recommendation(
    profile_type: str, duration_ms: float, num_recommendations: int, cached: bool = False
) -> None:
    """
    Track a recommendation generation.

    Args:
        profile_type: User profile type
        duration_ms: Generation duration in milliseconds
        num_recommendations: Number of recommendations generated
        cached: Whether the result was from cache
    """
    metrics = get_metrics_collector()

    tags = [f"profile_type:{profile_type}", f"cached:{cached}"]

    # Recommendation count
    metrics.increment("recommendations.generated", tags=tags)

    # Generation duration
    metrics.histogram("recommendations.duration", duration_ms, tags=tags)

    # Number of recommendations
    metrics.histogram("recommendations.count", num_recommendations, tags=tags)


def track_user_activity(activity_type: str, user_id: Optional[str] = None) -> None:
    """
    Track user activity.

    Args:
        activity_type: Type of activity ('registration', 'login', 'recommendation_viewed', etc.)
        user_id: Optional user ID
    """
    metrics = get_metrics_collector()

    tags = [f"activity:{activity_type}"]
    if user_id:
        tags.append(f"user:{user_id}")

    metrics.increment("user.activity", tags=tags)


def track_error(error_type: str, endpoint: Optional[str] = None, severity: str = "error") -> None:
    """
    Track an error.

    Args:
        error_type: Type of error
        endpoint: Optional endpoint where error occurred
        severity: Error severity ('warning', 'error', 'critical')
    """
    metrics = get_metrics_collector()

    tags = [f"error_type:{error_type}", f"severity:{severity}"]
    if endpoint:
        tags.append(f"endpoint:{endpoint}")

    metrics.increment("errors.count", tags=tags)


def track_resource_usage(resource_type: str, value: float, unit: str) -> None:
    """
    Track resource usage.

    Args:
        resource_type: Type of resource ('cpu', 'memory', 'disk', 'connections')
        value: Resource value
        unit: Unit of measurement ('percent', 'bytes', 'count')
    """
    metrics = get_metrics_collector()

    tags = [f"resource:{resource_type}", f"unit:{unit}"]

    metrics.gauge(f"resources.{resource_type}", value, tags=tags)
