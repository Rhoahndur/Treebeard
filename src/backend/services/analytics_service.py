"""
Analytics Service for TreeBeard Energy Plan Recommendation Agent

Tracks backend events for business metrics and monitoring.
Supports multiple analytics backends (Mixpanel, custom logging, etc.)
"""

import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
import json
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Analytics event types"""
    # API Events
    API_REQUEST = "api_request"
    API_ERROR = "error_occurred"

    # Recommendation Events
    RECOMMENDATION_GENERATED = "recommendation_generated"
    RECOMMENDATION_CACHED = "recommendation_cached"

    # Cache Events
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"

    # Risk Events
    RISK_WARNING_TRIGGERED = "risk_warning_triggered"

    # User Events
    USER_CREATED = "user_created"
    USER_PREFERENCES_UPDATED = "user_preferences_updated"

    # File Upload Events
    FILE_UPLOADED = "file_uploaded"
    FILE_UPLOAD_FAILED = "file_upload_failed"


class AnalyticsBackend(str, Enum):
    """Supported analytics backends"""
    MIXPANEL = "mixpanel"
    LOGGING = "logging"
    DATABASE = "database"
    CUSTOM = "custom"


class AnalyticsService:
    """
    Service for tracking analytics events.

    Features:
    - Async event tracking (non-blocking)
    - Multiple backend support
    - Event batching for performance
    - Automatic user anonymization
    - GDPR compliant (no PII)
    """

    def __init__(
        self,
        backend: AnalyticsBackend = AnalyticsBackend.LOGGING,
        mixpanel_token: Optional[str] = None,
        batch_size: int = 100,
        flush_interval: int = 60,
        enabled: bool = True
    ):
        self.backend = backend
        self.mixpanel_token = mixpanel_token
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.enabled = enabled

        self.event_queue: List[Dict[str, Any]] = []
        self.last_flush_time = time.time()

        # Initialize backend
        if backend == AnalyticsBackend.MIXPANEL and mixpanel_token:
            self._init_mixpanel()

    def _init_mixpanel(self):
        """Initialize Mixpanel client"""
        try:
            from mixpanel import Mixpanel
            self.mixpanel = Mixpanel(self.mixpanel_token)
            logger.info("Mixpanel analytics initialized")
        except ImportError:
            logger.warning("Mixpanel library not installed. Using logging backend.")
            self.backend = AnalyticsBackend.LOGGING

    async def track_event(
        self,
        event_type: EventType,
        properties: Dict[str, Any],
        user_id: Optional[UUID] = None
    ):
        """
        Track an analytics event.

        Args:
            event_type: Type of event
            properties: Event properties (must not contain PII)
            user_id: Optional anonymized user ID
        """
        if not self.enabled:
            return

        # Anonymize user ID if provided
        anonymous_user_id = self._anonymize_user_id(user_id) if user_id else None

        # Create event
        event = {
            "event": event_type.value,
            "properties": {
                **properties,
                "timestamp": datetime.utcnow().isoformat(),
                "environment": "production"  # Could be configurable
            },
            "distinct_id": anonymous_user_id,
        }

        # Add to queue
        self.event_queue.append(event)

        # Check if we should flush
        if len(self.event_queue) >= self.batch_size:
            await self._flush_events()
        elif time.time() - self.last_flush_time >= self.flush_interval:
            await self._flush_events()

    async def _flush_events(self):
        """Flush events to backend"""
        if not self.event_queue:
            return

        events_to_send = self.event_queue.copy()
        self.event_queue.clear()
        self.last_flush_time = time.time()

        # Send to backend
        if self.backend == AnalyticsBackend.MIXPANEL:
            await self._send_to_mixpanel(events_to_send)
        elif self.backend == AnalyticsBackend.LOGGING:
            await self._send_to_logging(events_to_send)
        elif self.backend == AnalyticsBackend.DATABASE:
            await self._send_to_database(events_to_send)

    async def _send_to_mixpanel(self, events: List[Dict[str, Any]]):
        """Send events to Mixpanel"""
        try:
            for event in events:
                self.mixpanel.track(
                    event["distinct_id"],
                    event["event"],
                    event["properties"]
                )
        except Exception as e:
            logger.error(f"Failed to send events to Mixpanel: {e}")

    async def _send_to_logging(self, events: List[Dict[str, Any]]):
        """Send events to logging"""
        for event in events:
            logger.info(
                f"Analytics Event: {event['event']}",
                extra={"analytics": event}
            )

    async def _send_to_database(self, events: List[Dict[str, Any]]):
        """Send events to database"""
        # TODO: Implement database storage
        pass

    def _anonymize_user_id(self, user_id: UUID) -> str:
        """
        Anonymize user ID using one-way hash.

        Args:
            user_id: User UUID

        Returns:
            Anonymized hash string
        """
        # Use SHA256 to create one-way hash
        return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]

    # Specific event tracking methods

    async def track_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[UUID] = None
    ):
        """Track API request"""
        await self.track_event(
            EventType.API_REQUEST,
            {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
            user_id
        )

    async def track_recommendation_generated(
        self,
        user_id: UUID,
        profile_type: str,
        num_plans: int,
        duration_ms: float,
        total_savings: Optional[float] = None
    ):
        """Track recommendation generation"""
        await self.track_event(
            EventType.RECOMMENDATION_GENERATED,
            {
                "profile_type": profile_type,
                "num_plans": num_plans,
                "duration_ms": duration_ms,
                "total_savings": total_savings,
            },
            user_id
        )

    async def track_error(
        self,
        endpoint: str,
        error_type: str,
        status_code: int,
        error_message: Optional[str] = None,
        user_id: Optional[UUID] = None
    ):
        """Track error occurrence"""
        await self.track_event(
            EventType.API_ERROR,
            {
                "endpoint": endpoint,
                "error_type": error_type,
                "status_code": status_code,
                "error_message": error_message,
            },
            user_id
        )

    async def track_cache_hit(
        self,
        cache_key: str,
        hit: bool
    ):
        """Track cache hit/miss"""
        event_type = EventType.CACHE_HIT if hit else EventType.CACHE_MISS
        await self.track_event(
            event_type,
            {
                "cache_key": hashlib.md5(cache_key.encode()).hexdigest()[:8],  # Anonymize key
            }
        )

    async def track_risk_warning(
        self,
        risk_type: str,
        severity: str,
        user_id: Optional[UUID] = None
    ):
        """Track risk warning triggered"""
        await self.track_event(
            EventType.RISK_WARNING_TRIGGERED,
            {
                "risk_type": risk_type,
                "severity": severity,
            },
            user_id
        )

    async def track_user_created(
        self,
        user_id: UUID,
        property_type: Optional[str] = None,
        zip_code: Optional[str] = None
    ):
        """Track user creation"""
        await self.track_event(
            EventType.USER_CREATED,
            {
                "property_type": property_type,
                "zip_code": zip_code,
            },
            user_id
        )

    async def track_preferences_updated(
        self,
        user_id: UUID,
        preferences: Dict[str, Any]
    ):
        """Track preference updates"""
        await self.track_event(
            EventType.USER_PREFERENCES_UPDATED,
            {
                "preferences": preferences,
            },
            user_id
        )

    async def track_file_upload(
        self,
        user_id: UUID,
        file_type: str,
        file_size_kb: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Track file upload"""
        event_type = EventType.FILE_UPLOADED if success else EventType.FILE_UPLOAD_FAILED
        await self.track_event(
            event_type,
            {
                "file_type": file_type,
                "file_size_kb": file_size_kb,
                "error_message": error_message if not success else None,
            },
            user_id
        )

    async def shutdown(self):
        """Shutdown analytics service and flush remaining events"""
        await self._flush_events()


# Global analytics instance
analytics_service: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """Get or create analytics service instance"""
    global analytics_service
    if analytics_service is None:
        analytics_service = AnalyticsService()
    return analytics_service


def init_analytics(
    backend: AnalyticsBackend = AnalyticsBackend.LOGGING,
    mixpanel_token: Optional[str] = None,
    enabled: bool = True
) -> AnalyticsService:
    """
    Initialize analytics service.

    Args:
        backend: Analytics backend to use
        mixpanel_token: Mixpanel token (if using Mixpanel)
        enabled: Whether analytics is enabled

    Returns:
        AnalyticsService instance
    """
    global analytics_service
    analytics_service = AnalyticsService(
        backend=backend,
        mixpanel_token=mixpanel_token,
        enabled=enabled
    )
    return analytics_service
