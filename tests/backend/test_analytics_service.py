"""
Unit Tests for Analytics Service

Tests analytics event tracking, batching, flushing, and convenience methods
without any database or external service dependencies.
"""

import hashlib
from uuid import uuid4

import pytest

import services.analytics_service as analytics_module
from services.analytics_service import (
    AnalyticsBackend,
    AnalyticsService,
    EventType,
    get_analytics_service,
    init_analytics,
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def service():
    """Create a fresh analytics service with logging backend."""
    return AnalyticsService()


@pytest.fixture
def disabled_service():
    """Create a disabled analytics service."""
    return AnalyticsService(enabled=False)


@pytest.fixture
def small_batch_service():
    """Create an analytics service with a small batch size for flush testing."""
    return AnalyticsService(batch_size=3)


@pytest.fixture
def user_id():
    """Generate a random user UUID."""
    return uuid4()


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the module-level singleton before each test."""
    analytics_module.analytics_service = None
    yield
    analytics_module.analytics_service = None


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestInitialization:
    """Test AnalyticsService initialization."""

    def test_default_backend_is_logging(self, service):
        """Default backend should be LOGGING."""
        assert service.backend == AnalyticsBackend.LOGGING

    def test_default_enabled_is_true(self, service):
        """Service should be enabled by default."""
        assert service.enabled is True

    def test_default_batch_size(self, service):
        """Default batch size should be 100."""
        assert service.batch_size == 100

    def test_default_flush_interval(self, service):
        """Default flush interval should be 60 seconds."""
        assert service.flush_interval == 60

    def test_empty_queue_on_init(self, service):
        """Event queue should be empty on initialization."""
        assert service.event_queue == []

    def test_custom_backend(self):
        """Service should accept a custom backend."""
        svc = AnalyticsService(backend=AnalyticsBackend.DATABASE)
        assert svc.backend == AnalyticsBackend.DATABASE

    def test_custom_batch_size(self):
        """Service should accept a custom batch size."""
        svc = AnalyticsService(batch_size=50)
        assert svc.batch_size == 50

    def test_disabled_service_init(self, disabled_service):
        """Disabled service should have enabled=False."""
        assert disabled_service.enabled is False


# ============================================================================
# DISABLED SERVICE TESTS
# ============================================================================

class TestDisabledService:
    """Test that a disabled service does nothing."""

    async def test_track_event_noop_when_disabled(self, disabled_service):
        """track_event should not queue events when disabled."""
        await disabled_service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
        assert len(disabled_service.event_queue) == 0

    async def test_convenience_methods_noop_when_disabled(self, disabled_service):
        """Convenience methods should not queue events when disabled."""
        uid = uuid4()
        await disabled_service.track_api_request("/test", "GET", 200, 10.0)
        await disabled_service.track_error("/test", "ValueError", 500)
        await disabled_service.track_cache_hit("key", True)
        await disabled_service.track_file_upload(uid, "pdf", 100.0, True)
        assert len(disabled_service.event_queue) == 0


# ============================================================================
# EVENT TRACKING TESTS
# ============================================================================

class TestEventTracking:
    """Test core event tracking behavior."""

    async def test_event_queued(self, service):
        """Tracking an event should add it to the queue."""
        await service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
        assert len(service.event_queue) == 1

    async def test_event_has_correct_type(self, service):
        """Queued event should have the correct event type string."""
        await service.track_event(EventType.CACHE_HIT, {"cache_key": "abc"})
        event = service.event_queue[0]
        assert event["event"] == "cache_hit"

    async def test_event_properties_include_custom_data(self, service):
        """Queued event properties should include the provided data."""
        await service.track_event(EventType.API_REQUEST, {"endpoint": "/plans", "method": "GET"})
        props = service.event_queue[0]["properties"]
        assert props["endpoint"] == "/plans"
        assert props["method"] == "GET"

    async def test_event_properties_include_timestamp(self, service):
        """Queued event properties should include a timestamp."""
        await service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
        props = service.event_queue[0]["properties"]
        assert "timestamp" in props

    async def test_event_properties_include_environment(self, service):
        """Queued event properties should include environment."""
        await service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
        props = service.event_queue[0]["properties"]
        assert "environment" in props
        assert props["environment"] == "production"

    async def test_event_with_user_id(self, service, user_id):
        """Event with user_id should have an anonymized distinct_id."""
        await service.track_event(EventType.USER_CREATED, {}, user_id=user_id)
        event = service.event_queue[0]
        assert event["distinct_id"] is not None
        assert event["distinct_id"] != str(user_id)

    async def test_event_without_user_id(self, service):
        """Event without user_id should have distinct_id as None."""
        await service.track_event(EventType.CACHE_HIT, {"cache_key": "abc"})
        event = service.event_queue[0]
        assert event["distinct_id"] is None

    async def test_multiple_events_queued(self, service):
        """Multiple tracked events should all be queued."""
        for i in range(5):
            await service.track_event(EventType.API_REQUEST, {"endpoint": f"/test/{i}"})
        assert len(service.event_queue) == 5


# ============================================================================
# USER ID ANONYMIZATION TESTS
# ============================================================================

class TestUserIdAnonymization:
    """Test user ID anonymization."""

    def test_anonymized_id_is_deterministic(self, service):
        """Same user ID should always produce the same hash."""
        uid = uuid4()
        hash1 = service._anonymize_user_id(uid)
        hash2 = service._anonymize_user_id(uid)
        assert hash1 == hash2

    def test_anonymized_id_is_16_chars(self, service):
        """Anonymized ID should be exactly 16 characters."""
        uid = uuid4()
        result = service._anonymize_user_id(uid)
        assert len(result) == 16

    def test_anonymized_id_matches_sha256(self, service):
        """Anonymized ID should match first 16 chars of SHA256 hex digest."""
        uid = uuid4()
        expected = hashlib.sha256(str(uid).encode()).hexdigest()[:16]
        assert service._anonymize_user_id(uid) == expected

    def test_different_users_produce_different_hashes(self, service):
        """Different user IDs should produce different hashes."""
        uid1 = uuid4()
        uid2 = uuid4()
        assert service._anonymize_user_id(uid1) != service._anonymize_user_id(uid2)

    def test_anonymized_id_is_hex_string(self, service):
        """Anonymized ID should be a valid hex string."""
        uid = uuid4()
        result = service._anonymize_user_id(uid)
        int(result, 16)  # Raises ValueError if not valid hex


# ============================================================================
# AUTO-FLUSH TESTS
# ============================================================================

class TestAutoFlush:
    """Test automatic flushing when batch size is reached."""

    async def test_auto_flush_at_batch_size(self, small_batch_service):
        """Queue should be flushed when it reaches batch_size."""
        svc = small_batch_service  # batch_size=3
        await svc.track_event(EventType.API_REQUEST, {"n": 1})
        await svc.track_event(EventType.API_REQUEST, {"n": 2})
        assert len(svc.event_queue) == 2  # Not yet flushed
        await svc.track_event(EventType.API_REQUEST, {"n": 3})
        assert len(svc.event_queue) == 0  # Flushed

    async def test_no_auto_flush_below_batch_size(self, small_batch_service):
        """Queue should not flush before reaching batch_size."""
        svc = small_batch_service  # batch_size=3
        await svc.track_event(EventType.API_REQUEST, {"n": 1})
        await svc.track_event(EventType.API_REQUEST, {"n": 2})
        assert len(svc.event_queue) == 2


# ============================================================================
# MANUAL FLUSH TESTS
# ============================================================================

class TestManualFlush:
    """Test manual flushing of events."""

    async def test_flush_clears_queue(self, service):
        """Flushing should clear the event queue."""
        await service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
        assert len(service.event_queue) == 1
        await service._flush_events()
        assert len(service.event_queue) == 0

    async def test_flush_empty_queue_is_noop(self, service):
        """Flushing an empty queue should not error."""
        assert len(service.event_queue) == 0
        await service._flush_events()
        assert len(service.event_queue) == 0


# ============================================================================
# LOGGING BACKEND TESTS
# ============================================================================

class TestLoggingBackend:
    """Test the logging backend."""

    async def test_logging_backend_no_errors(self, service):
        """Flushing events through logging backend should not raise."""
        await service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
        await service._flush_events()

    async def test_logging_backend_logs_events(self, service, caplog):
        """Flushing should produce log messages."""
        import logging
        with caplog.at_level(logging.INFO, logger="backend.services.analytics_service"):
            await service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
            await service._flush_events()
        assert any("Analytics Event" in record.message for record in caplog.records)

    async def test_logging_backend_logs_event_type(self, service, caplog):
        """Log messages should contain the event type."""
        import logging
        with caplog.at_level(logging.INFO, logger="backend.services.analytics_service"):
            await service.track_event(EventType.CACHE_HIT, {"key": "x"})
            await service._flush_events()
        assert any("cache_hit" in record.message for record in caplog.records)


# ============================================================================
# CONVENIENCE METHOD TESTS
# ============================================================================

class TestTrackApiRequest:
    """Test track_api_request convenience method."""

    async def test_queues_api_request_event(self, service):
        """Should queue an API_REQUEST event."""
        await service.track_api_request("/plans", "GET", 200, 45.0)
        assert len(service.event_queue) == 1
        assert service.event_queue[0]["event"] == EventType.API_REQUEST

    async def test_includes_request_properties(self, service):
        """Should include endpoint, method, status_code, and duration_ms."""
        await service.track_api_request("/plans", "POST", 201, 120.5)
        props = service.event_queue[0]["properties"]
        assert props["endpoint"] == "/plans"
        assert props["method"] == "POST"
        assert props["status_code"] == 201
        assert props["duration_ms"] == 120.5

    async def test_with_user_id(self, service, user_id):
        """Should anonymize and attach user_id."""
        await service.track_api_request("/plans", "GET", 200, 10.0, user_id=user_id)
        assert service.event_queue[0]["distinct_id"] is not None


class TestTrackError:
    """Test track_error convenience method."""

    async def test_queues_error_event(self, service):
        """Should queue an API_ERROR event."""
        await service.track_error("/plans", "ValueError", 400)
        assert len(service.event_queue) == 1
        assert service.event_queue[0]["event"] == EventType.API_ERROR

    async def test_includes_error_properties(self, service):
        """Should include endpoint, error_type, status_code, and error_message."""
        await service.track_error("/plans", "NotFound", 404, error_message="Plan not found")
        props = service.event_queue[0]["properties"]
        assert props["endpoint"] == "/plans"
        assert props["error_type"] == "NotFound"
        assert props["status_code"] == 404
        assert props["error_message"] == "Plan not found"


class TestTrackCacheHit:
    """Test track_cache_hit convenience method."""

    async def test_queues_cache_hit_event(self, service):
        """Should queue a CACHE_HIT event when hit=True."""
        await service.track_cache_hit("user:123:plans", hit=True)
        assert len(service.event_queue) == 1
        assert service.event_queue[0]["event"] == EventType.CACHE_HIT

    async def test_queues_cache_miss_event(self, service):
        """Should queue a CACHE_MISS event when hit=False."""
        await service.track_cache_hit("user:123:plans", hit=False)
        assert service.event_queue[0]["event"] == EventType.CACHE_MISS

    async def test_cache_key_is_anonymized(self, service):
        """Cache key in properties should be an MD5 hash prefix, not the raw key."""
        await service.track_cache_hit("user:123:plans", hit=True)
        props = service.event_queue[0]["properties"]
        assert props["cache_key"] != "user:123:plans"
        assert len(props["cache_key"]) == 8


class TestTrackFileUpload:
    """Test track_file_upload convenience method."""

    async def test_queues_file_uploaded_on_success(self, service, user_id):
        """Should queue a FILE_UPLOADED event on success."""
        await service.track_file_upload(user_id, "pdf", 250.0, success=True)
        assert len(service.event_queue) == 1
        assert service.event_queue[0]["event"] == EventType.FILE_UPLOADED

    async def test_queues_file_upload_failed_on_failure(self, service, user_id):
        """Should queue a FILE_UPLOAD_FAILED event on failure."""
        await service.track_file_upload(user_id, "csv", 500.0, success=False, error_message="Too large")
        assert service.event_queue[0]["event"] == EventType.FILE_UPLOAD_FAILED

    async def test_includes_file_properties(self, service, user_id):
        """Should include file_type and file_size_kb."""
        await service.track_file_upload(user_id, "pdf", 250.0, success=True)
        props = service.event_queue[0]["properties"]
        assert props["file_type"] == "pdf"
        assert props["file_size_kb"] == 250.0

    async def test_error_message_only_on_failure(self, service, user_id):
        """error_message should be None on success, present on failure."""
        await service.track_file_upload(user_id, "pdf", 100.0, success=True)
        assert service.event_queue[0]["properties"]["error_message"] is None

        await service.track_file_upload(user_id, "pdf", 100.0, success=False, error_message="Bad format")
        assert service.event_queue[1]["properties"]["error_message"] == "Bad format"


class TestTrackRecommendationGenerated:
    """Test track_recommendation_generated convenience method."""

    async def test_queues_recommendation_event(self, service, user_id):
        """Should queue a RECOMMENDATION_GENERATED event."""
        await service.track_recommendation_generated(user_id, "residential", 5, 350.0)
        assert len(service.event_queue) == 1
        assert service.event_queue[0]["event"] == EventType.RECOMMENDATION_GENERATED

    async def test_includes_recommendation_properties(self, service, user_id):
        """Should include profile_type, num_plans, duration_ms, total_savings."""
        await service.track_recommendation_generated(user_id, "residential", 5, 350.0, total_savings=120.50)
        props = service.event_queue[0]["properties"]
        assert props["profile_type"] == "residential"
        assert props["num_plans"] == 5
        assert props["duration_ms"] == 350.0
        assert props["total_savings"] == 120.50


class TestTrackRiskWarning:
    """Test track_risk_warning convenience method."""

    async def test_queues_risk_warning_event(self, service):
        """Should queue a RISK_WARNING_TRIGGERED event."""
        await service.track_risk_warning("variable_rate", "high")
        assert service.event_queue[0]["event"] == EventType.RISK_WARNING_TRIGGERED

    async def test_includes_risk_properties(self, service):
        """Should include risk_type and severity."""
        await service.track_risk_warning("variable_rate", "high")
        props = service.event_queue[0]["properties"]
        assert props["risk_type"] == "variable_rate"
        assert props["severity"] == "high"


class TestTrackUserCreated:
    """Test track_user_created convenience method."""

    async def test_queues_user_created_event(self, service, user_id):
        """Should queue a USER_CREATED event."""
        await service.track_user_created(user_id, property_type="residential", zip_code="77001")
        assert service.event_queue[0]["event"] == EventType.USER_CREATED

    async def test_includes_user_properties(self, service, user_id):
        """Should include property_type and zip_code."""
        await service.track_user_created(user_id, property_type="commercial", zip_code="90210")
        props = service.event_queue[0]["properties"]
        assert props["property_type"] == "commercial"
        assert props["zip_code"] == "90210"


class TestTrackPreferencesUpdated:
    """Test track_preferences_updated convenience method."""

    async def test_queues_preferences_event(self, service, user_id):
        """Should queue a USER_PREFERENCES_UPDATED event."""
        await service.track_preferences_updated(user_id, {"cost_priority": 50})
        assert service.event_queue[0]["event"] == EventType.USER_PREFERENCES_UPDATED

    async def test_includes_preferences(self, service, user_id):
        """Should include the preferences dict."""
        prefs = {"cost_priority": 50, "renewable_priority": 30}
        await service.track_preferences_updated(user_id, prefs)
        props = service.event_queue[0]["properties"]
        assert props["preferences"] == prefs


# ============================================================================
# SHUTDOWN TESTS
# ============================================================================

class TestShutdown:
    """Test service shutdown."""

    async def test_shutdown_flushes_events(self, service):
        """Shutdown should flush all remaining events."""
        await service.track_event(EventType.API_REQUEST, {"endpoint": "/test"})
        await service.track_event(EventType.CACHE_HIT, {"key": "x"})
        assert len(service.event_queue) == 2
        await service.shutdown()
        assert len(service.event_queue) == 0

    async def test_shutdown_on_empty_queue(self, service):
        """Shutdown on empty queue should not error."""
        await service.shutdown()
        assert len(service.event_queue) == 0


# ============================================================================
# SINGLETON / MODULE-LEVEL HELPER TESTS
# ============================================================================

class TestSingleton:
    """Test module-level singleton helpers."""

    def test_get_analytics_service_returns_instance(self):
        """get_analytics_service should return an AnalyticsService."""
        svc = get_analytics_service()
        assert isinstance(svc, AnalyticsService)

    def test_get_analytics_service_returns_same_instance(self):
        """Calling get_analytics_service twice should return the same object."""
        svc1 = get_analytics_service()
        svc2 = get_analytics_service()
        assert svc1 is svc2

    def test_init_analytics_creates_new_instance(self):
        """init_analytics should create a new singleton instance."""
        svc1 = get_analytics_service()
        svc2 = init_analytics(backend=AnalyticsBackend.DATABASE, enabled=False)
        assert svc2 is not svc1
        assert svc2.backend == AnalyticsBackend.DATABASE
        assert svc2.enabled is False

    def test_init_analytics_replaces_singleton(self):
        """After init_analytics, get_analytics_service should return the new instance."""
        init_analytics(backend=AnalyticsBackend.DATABASE)
        svc = get_analytics_service()
        assert svc.backend == AnalyticsBackend.DATABASE

    def test_init_analytics_default_backend(self):
        """init_analytics with defaults should use LOGGING backend."""
        svc = init_analytics()
        assert svc.backend == AnalyticsBackend.LOGGING
        assert svc.enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
