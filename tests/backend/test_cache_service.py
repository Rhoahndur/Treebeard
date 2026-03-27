"""
Unit Tests for Cache Service
Story 1.4 - Epic 1: Data Infrastructure & Pipeline

Tests focus on:
- Disabled service graceful degradation (no Redis required)
- Key generation helpers
- Usage data hashing (deterministic MD5)
- InMemoryCache standalone behavior
- Generic async cache methods when disabled
"""

from datetime import date

import pytest

from schemas.usage_analysis import MonthlyUsage
from services.cache_service import CacheService, InMemoryCache

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def disabled_service():
    """CacheService with caching explicitly disabled."""
    return CacheService(enabled=False)


@pytest.fixture
def memory_cache():
    """Fresh InMemoryCache instance."""
    return InMemoryCache()


# ============================================================================
# Disabled Service Tests
# ============================================================================


class TestDisabledCacheService:
    """All methods degrade gracefully when the service is disabled."""

    def test_enabled_flag_is_false(self, disabled_service):
        assert disabled_service.enabled is False

    def test_client_is_none(self, disabled_service):
        assert disabled_service._client is None

    def test_get_profile_returns_none(self, disabled_service):
        assert disabled_service.get_profile("user-1") is None

    def test_set_profile_returns_false(self, disabled_service):
        assert disabled_service.set_profile("user-1", None) is False

    def test_invalidate_profile_returns_false(self, disabled_service):
        assert disabled_service.invalidate_profile("user-1") is False

    def test_get_profile_with_hash_returns_none(self, disabled_service):
        assert disabled_service.get_profile_with_hash("user-1", "abc123") is None

    def test_set_profile_with_hash_returns_false(self, disabled_service):
        assert disabled_service.set_profile_with_hash("user-1", None, "abc123") is False

    def test_clear_all_profiles_returns_zero(self, disabled_service):
        assert disabled_service.clear_all_profiles() == 0


# ============================================================================
# Key Generation Tests
# ============================================================================


class TestKeyGeneration:
    """_make_key and _make_hash_key produce the expected patterns."""

    def test_make_key_format(self, disabled_service):
        key = disabled_service._make_key("user-42")
        assert key == "usage_profile:v1:user-42"

    def test_make_key_uses_class_constants(self, disabled_service):
        key = disabled_service._make_key("abc")
        prefix = CacheService.KEY_PREFIX
        version = CacheService.KEY_VERSION
        assert key == f"{prefix}:{version}:abc"

    def test_make_hash_key_format(self, disabled_service):
        key = disabled_service._make_hash_key("user-42")
        assert key == "usage_profile:hash:v1:user-42"

    def test_make_key_different_users_produce_different_keys(self, disabled_service):
        assert disabled_service._make_key("a") != disabled_service._make_key("b")

    def test_make_hash_key_different_users_produce_different_keys(self, disabled_service):
        assert disabled_service._make_hash_key("a") != disabled_service._make_hash_key("b")

    def test_make_key_and_hash_key_differ_for_same_user(self, disabled_service):
        assert disabled_service._make_key("user-1") != disabled_service._make_hash_key("user-1")


# ============================================================================
# Usage Data Hash Tests
# ============================================================================


class TestUsageDataHash:
    """get_usage_data_hash produces deterministic MD5 digests."""

    @pytest.fixture
    def sample_usage(self):
        return [
            MonthlyUsage(month=date(2024, 1, 1), kwh=500.0),
            MonthlyUsage(month=date(2024, 2, 1), kwh=480.0),
            MonthlyUsage(month=date(2024, 3, 1), kwh=520.0),
        ]

    def test_hash_is_deterministic(self, disabled_service, sample_usage):
        h1 = disabled_service.get_usage_data_hash(sample_usage)
        h2 = disabled_service.get_usage_data_hash(sample_usage)
        assert h1 == h2

    def test_hash_is_32_char_hex(self, disabled_service, sample_usage):
        h = disabled_service.get_usage_data_hash(sample_usage)
        assert len(h) == 32
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_data_produces_different_hash(self, disabled_service):
        data_a = [MonthlyUsage(month=date(2024, 1, 1), kwh=500.0)]
        data_b = [MonthlyUsage(month=date(2024, 1, 1), kwh=501.0)]
        assert disabled_service.get_usage_data_hash(data_a) != disabled_service.get_usage_data_hash(data_b)

    def test_different_months_produces_different_hash(self, disabled_service):
        data_a = [MonthlyUsage(month=date(2024, 1, 1), kwh=500.0)]
        data_b = [MonthlyUsage(month=date(2024, 2, 1), kwh=500.0)]
        assert disabled_service.get_usage_data_hash(data_a) != disabled_service.get_usage_data_hash(data_b)

    def test_order_matters(self, disabled_service):
        a = MonthlyUsage(month=date(2024, 1, 1), kwh=100.0)
        b = MonthlyUsage(month=date(2024, 2, 1), kwh=200.0)
        assert disabled_service.get_usage_data_hash([a, b]) != disabled_service.get_usage_data_hash([b, a])

    def test_empty_list(self, disabled_service):
        h = disabled_service.get_usage_data_hash([])
        assert len(h) == 32  # MD5 of empty string is still a valid hex digest


# ============================================================================
# Stats When Disabled Tests
# ============================================================================


class TestStatsWhenDisabled:
    """get_stats returns a predictable disabled status dict."""

    def test_returns_dict(self, disabled_service):
        stats = disabled_service.get_stats()
        assert isinstance(stats, dict)

    def test_enabled_is_false(self, disabled_service):
        stats = disabled_service.get_stats()
        assert stats["enabled"] is False

    def test_status_is_disabled(self, disabled_service):
        stats = disabled_service.get_stats()
        assert stats["status"] == "disabled"

    def test_no_extra_keys(self, disabled_service):
        stats = disabled_service.get_stats()
        assert set(stats.keys()) == {"enabled", "status"}


# ============================================================================
# Generic Async Methods When Disabled
# ============================================================================


class TestAsyncMethodsWhenDisabled:
    """Async cache helpers are safe no-ops when the service is disabled."""

    async def test_get_returns_none(self, disabled_service):
        result = await disabled_service.get("some-key")
        assert result is None

    async def test_set_is_noop(self, disabled_service):
        # Should not raise
        await disabled_service.set("key", "value", ttl=60)

    async def test_setex_is_noop(self, disabled_service):
        await disabled_service.setex("key", 60, "value")

    async def test_delete_is_noop(self, disabled_service):
        await disabled_service.delete("key")

    async def test_incr_returns_zero(self, disabled_service):
        result = await disabled_service.incr("counter")
        assert result == 0


# ============================================================================
# InMemoryCache Tests
# ============================================================================


class TestInMemoryCache:
    """InMemoryCache is a pure dict-based fallback -- no Redis needed."""

    def test_ping_returns_true(self, memory_cache):
        assert memory_cache.ping() is True

    def test_get_missing_key_returns_none(self, memory_cache):
        assert memory_cache.get("nonexistent") is None

    def test_setex_and_get(self, memory_cache):
        memory_cache.setex("k1", 300, "hello")
        assert memory_cache.get("k1") == "hello"

    def test_setex_overwrites(self, memory_cache):
        memory_cache.setex("k1", 300, "first")
        memory_cache.setex("k1", 300, "second")
        assert memory_cache.get("k1") == "second"

    def test_delete_existing_key(self, memory_cache):
        memory_cache.setex("k1", 300, "val")
        memory_cache.delete("k1")
        assert memory_cache.get("k1") is None

    def test_delete_missing_key_does_not_raise(self, memory_cache):
        memory_cache.delete("nonexistent")  # should be silent

    def test_keys_returns_matching(self, memory_cache):
        memory_cache.setex("usage_profile:v1:a", 300, "1")
        memory_cache.setex("usage_profile:v1:b", 300, "2")
        memory_cache.setex("other:key", 300, "3")
        matched = memory_cache.keys("usage_profile:*")
        assert sorted(matched) == ["usage_profile:v1:a", "usage_profile:v1:b"]

    def test_keys_no_match(self, memory_cache):
        memory_cache.setex("foo", 300, "bar")
        assert memory_cache.keys("zzz:*") == []

    def test_keys_empty_cache(self, memory_cache):
        assert memory_cache.keys("*") == []


# ============================================================================
# Class Constants
# ============================================================================


class TestClassConstants:
    """Verify hard-coded configuration values."""

    def test_profile_ttl_is_seven_days_in_seconds(self):
        assert CacheService.PROFILE_TTL == 7 * 24 * 60 * 60

    def test_key_prefix(self):
        assert CacheService.KEY_PREFIX == "usage_profile"

    def test_key_version(self):
        assert CacheService.KEY_VERSION == "v1"
