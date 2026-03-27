"""
Unit tests for Cache Optimization Service (Story 7.1).

Tests coverage:
- CacheStats dataclass (hit_rate, miss_rate, error_rate, to_dict)
- CacheKeyStats dataclass (hit_rate)
- Disabled OptimizedCacheService graceful defaults
- TTL determination from key patterns
- Key pattern extraction
- Stats tracking when disabled
- Health check when disabled
- Stats reset
- get_stats when disabled
"""

from datetime import datetime

from services.cache_optimization import (
    CacheKeyStats,
    CacheStats,
)

# ===== CacheStats DATACLASS TESTS =====


class TestCacheStats:
    """Tests for the CacheStats dataclass."""

    def test_hit_rate_with_requests(self):
        stats = CacheStats(total_requests=100, cache_hits=75)
        assert stats.hit_rate == 75.0

    def test_hit_rate_zero_requests(self):
        stats = CacheStats(total_requests=0, cache_hits=0)
        assert stats.hit_rate == 0.0

    def test_hit_rate_all_hits(self):
        stats = CacheStats(total_requests=50, cache_hits=50)
        assert stats.hit_rate == 100.0

    def test_miss_rate_with_requests(self):
        stats = CacheStats(total_requests=100, cache_hits=75)
        assert stats.miss_rate == 25.0

    def test_miss_rate_zero_requests(self):
        stats = CacheStats(total_requests=0, cache_hits=0)
        assert stats.miss_rate == 100.0

    def test_miss_rate_all_hits(self):
        stats = CacheStats(total_requests=50, cache_hits=50)
        assert stats.miss_rate == 0.0

    def test_error_rate_with_errors(self):
        stats = CacheStats(total_requests=200, errors=10)
        assert stats.error_rate == 5.0

    def test_error_rate_zero_requests(self):
        stats = CacheStats(total_requests=0, errors=0)
        assert stats.error_rate == 0.0

    def test_error_rate_no_errors(self):
        stats = CacheStats(total_requests=100, errors=0)
        assert stats.error_rate == 0.0

    def test_to_dict_contains_all_fields(self):
        stats = CacheStats(
            total_requests=200,
            cache_hits=150,
            cache_misses=40,
            errors=10,
        )
        result = stats.to_dict()
        assert result["total_requests"] == 200
        assert result["cache_hits"] == 150
        assert result["cache_misses"] == 40
        assert result["errors"] == 10
        assert result["hit_rate"] == 75.0
        assert result["miss_rate"] == 25.0
        assert result["error_rate"] == 5.0
        assert "last_reset" in result

    def test_to_dict_rates_are_rounded(self):
        stats = CacheStats(total_requests=3, cache_hits=1, errors=1)
        result = stats.to_dict()
        # 1/3 * 100 = 33.333... -> rounded to 33.33
        assert result["hit_rate"] == 33.33
        assert result["error_rate"] == 33.33

    def test_to_dict_last_reset_is_iso_string(self):
        stats = CacheStats()
        result = stats.to_dict()
        # Should be parseable as an ISO datetime string
        datetime.fromisoformat(result["last_reset"])

    def test_defaults(self):
        stats = CacheStats()
        assert stats.total_requests == 0
        assert stats.cache_hits == 0
        assert stats.cache_misses == 0
        assert stats.errors == 0
        assert isinstance(stats.last_reset, datetime)


# ===== CacheKeyStats DATACLASS TESTS =====


class TestCacheKeyStats:
    """Tests for the CacheKeyStats dataclass."""

    def test_hit_rate_with_activity(self):
        key_stats = CacheKeyStats(pattern="plan", hits=80, misses=20)
        assert key_stats.hit_rate == 80.0

    def test_hit_rate_zero_total(self):
        key_stats = CacheKeyStats(pattern="plan", hits=0, misses=0)
        assert key_stats.hit_rate == 0.0

    def test_hit_rate_all_hits(self):
        key_stats = CacheKeyStats(pattern="user", hits=10, misses=0)
        assert key_stats.hit_rate == 100.0

    def test_hit_rate_all_misses(self):
        key_stats = CacheKeyStats(pattern="user", hits=0, misses=10)
        assert key_stats.hit_rate == 0.0

    def test_defaults(self):
        key_stats = CacheKeyStats(pattern="test")
        assert key_stats.pattern == "test"
        assert key_stats.hits == 0
        assert key_stats.misses == 0
        assert key_stats.avg_ttl == 0.0
        assert key_stats.last_accessed is None


# ===== DISABLED OptimizedCacheService TESTS =====


class TestDisabledCacheService:
    """Tests for OptimizedCacheService when disabled (no Redis)."""

    def test_get_returns_default_none(self, disabled_cache):
        assert disabled_cache.get("some_key") is None

    def test_get_returns_custom_default(self, disabled_cache):
        assert disabled_cache.get("some_key", default="fallback") == "fallback"

    def test_set_returns_false(self, disabled_cache):
        assert disabled_cache.set("key", "value") is False

    def test_delete_returns_false(self, disabled_cache):
        assert disabled_cache.delete("key") is False

    def test_delete_pattern_returns_zero(self, disabled_cache):
        assert disabled_cache.delete_pattern("prefix:*") == 0

    def test_exists_returns_false(self, disabled_cache):
        assert disabled_cache.exists("key") is False

    def test_get_ttl_returns_negative_two(self, disabled_cache):
        assert disabled_cache.get_ttl("key") == -2

    def test_invalidate_by_prefix_returns_zero(self, disabled_cache):
        assert disabled_cache.invalidate_by_prefix("user_profile") == 0

    def test_invalidate_user_cache_returns_zero(self, disabled_cache):
        assert disabled_cache.invalidate_user_cache("user-123") == 0

    def test_enabled_is_false(self, disabled_cache):
        assert disabled_cache.enabled is False

    def test_client_is_none(self, disabled_cache):
        assert disabled_cache._client is None


# ===== _determine_ttl TESTS =====


class TestDetermineTTL:
    """Tests for the _determine_ttl private method."""

    def test_plan_catalog_ttl(self, disabled_cache):
        assert disabled_cache._determine_ttl("plan_catalog:abc") == 3600

    def test_user_profile_ttl(self, disabled_cache):
        assert disabled_cache._determine_ttl("user_profile:user-1") == 86400

    def test_recommendations_ttl(self, disabled_cache):
        assert disabled_cache._determine_ttl("recommendations:user-1") == 86400

    def test_usage_analysis_ttl(self, disabled_cache):
        assert disabled_cache._determine_ttl("usage_analysis:user-1") == 604800

    def test_response_cache_ttl(self, disabled_cache):
        assert disabled_cache._determine_ttl("response_cache:endpoint") == 300

    def test_unknown_key_returns_default_300(self, disabled_cache):
        assert disabled_cache._determine_ttl("totally_unknown:key") == 300

    def test_key_containing_pattern_substring(self, disabled_cache):
        # Key contains "plan_catalog" even as part of a longer key
        assert disabled_cache._determine_ttl("my_plan_catalog_key") == 3600


# ===== _get_key_pattern TESTS =====


class TestGetKeyPattern:
    """Tests for the _get_key_pattern private method."""

    def test_plan_pattern(self, disabled_cache):
        assert disabled_cache._get_key_pattern("plan_catalog:abc") == "plan"

    def test_user_pattern(self, disabled_cache):
        assert disabled_cache._get_key_pattern("user_profile:user-1") == "user"

    def test_recommendation_pattern(self, disabled_cache):
        assert disabled_cache._get_key_pattern("recommendation:abc") == "recommendation"

    def test_usage_pattern(self, disabled_cache):
        assert disabled_cache._get_key_pattern("usage:abc") == "usage"

    def test_response_pattern(self, disabled_cache):
        assert disabled_cache._get_key_pattern("cache:response:endpoint") == "response"

    def test_unknown_key_returns_other(self, disabled_cache):
        assert disabled_cache._get_key_pattern("completely_unknown:key") == "other"


# ===== STATS TRACKING TESTS =====


class TestStatsTracking:
    """Tests for statistics tracking when the cache is disabled."""

    def test_get_increments_total_requests(self, disabled_cache):
        disabled_cache.get("key1")
        disabled_cache.get("key2")
        assert disabled_cache.stats.total_requests == 2

    def test_get_increments_cache_misses(self, disabled_cache):
        disabled_cache.get("key1")
        disabled_cache.get("key2")
        disabled_cache.get("key3")
        assert disabled_cache.stats.cache_misses == 3

    def test_get_does_not_increment_hits_when_disabled(self, disabled_cache):
        disabled_cache.get("key1")
        assert disabled_cache.stats.cache_hits == 0

    def test_stats_accumulate_across_calls(self, disabled_cache):
        for _ in range(10):
            disabled_cache.get("key")
        assert disabled_cache.stats.total_requests == 10
        assert disabled_cache.stats.cache_misses == 10
        assert disabled_cache.stats.cache_hits == 0


# ===== HEALTH CHECK TESTS =====


class TestHealthCheck:
    """Tests for health_check when disabled."""

    def test_health_check_disabled_returns_not_healthy(self, disabled_cache):
        result = disabled_cache.health_check()
        assert result["healthy"] is False

    def test_health_check_disabled_status(self, disabled_cache):
        result = disabled_cache.health_check()
        assert result["status"] == "disabled"

    def test_health_check_disabled_has_message(self, disabled_cache):
        result = disabled_cache.health_check()
        assert "message" in result
        assert isinstance(result["message"], str)


# ===== RESET STATS TESTS =====


class TestResetStats:
    """Tests for reset_stats."""

    def test_reset_clears_request_counts(self, disabled_cache):
        disabled_cache.get("key1")
        disabled_cache.get("key2")
        assert disabled_cache.stats.total_requests == 2

        disabled_cache.reset_stats()
        assert disabled_cache.stats.total_requests == 0
        assert disabled_cache.stats.cache_hits == 0
        assert disabled_cache.stats.cache_misses == 0
        assert disabled_cache.stats.errors == 0

    def test_reset_clears_key_stats(self, disabled_cache):
        # Manually populate key_stats to simulate tracked patterns
        disabled_cache.key_stats["plan"] = CacheKeyStats(
            pattern="plan", hits=5, misses=2
        )
        assert len(disabled_cache.key_stats) == 1

        disabled_cache.reset_stats()
        assert len(disabled_cache.key_stats) == 0

    def test_reset_creates_fresh_stats_object(self, disabled_cache):
        disabled_cache.get("key")
        old_stats = disabled_cache.stats
        disabled_cache.reset_stats()
        assert disabled_cache.stats is not old_stats


# ===== GET STATS TESTS =====


class TestGetStats:
    """Tests for get_stats when disabled."""

    def test_get_stats_contains_enabled_false(self, disabled_cache):
        result = disabled_cache.get_stats()
        assert result["enabled"] is False

    def test_get_stats_contains_base_fields(self, disabled_cache):
        result = disabled_cache.get_stats()
        assert "total_requests" in result
        assert "cache_hits" in result
        assert "cache_misses" in result
        assert "errors" in result
        assert "hit_rate" in result
        assert "miss_rate" in result
        assert "error_rate" in result
        assert "last_reset" in result

    def test_get_stats_reflects_activity(self, disabled_cache):
        disabled_cache.get("a")
        disabled_cache.get("b")
        result = disabled_cache.get_stats()
        assert result["total_requests"] == 2
        assert result["cache_misses"] == 2
        assert result["cache_hits"] == 0

    def test_get_stats_does_not_contain_redis_fields_when_disabled(self, disabled_cache):
        result = disabled_cache.get_stats()
        assert "redis_keyspace_hits" not in result
        assert "redis_keyspace_misses" not in result
        assert "used_memory_human" not in result
