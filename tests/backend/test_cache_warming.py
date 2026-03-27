"""
Tests for CacheWarmingService.

Covers initialization, stats reporting, private helper methods,
and the main warming orchestration logic (with DB mocked out).
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.cache_optimization import OptimizedCacheService
from services.cache_warming import CacheWarmingService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service(disabled_cache):
    """A CacheWarmingService backed by the disabled cache."""
    return CacheWarmingService(cache_service=disabled_cache)


@pytest.fixture
def mock_db():
    """A lightweight stand-in for a SQLAlchemy Session."""
    db = MagicMock()
    db.close = MagicMock()
    return db


# ---------------------------------------------------------------------------
# 1. Initialization
# ---------------------------------------------------------------------------

class TestInitialization:
    def test_warming_stats_initial_values(self, service):
        stats = service.warming_stats
        assert stats["last_full_warm"] is None
        assert stats["last_plan_warm"] is None
        assert stats["last_profile_warm"] is None
        assert stats["total_items_warmed"] == 0
        assert stats["errors"] == 0

    def test_cache_is_assigned(self, service, disabled_cache):
        assert service.cache is disabled_cache


# ---------------------------------------------------------------------------
# 2. get_warming_stats
# ---------------------------------------------------------------------------

class TestGetWarmingStats:
    def test_returns_dict_with_expected_keys(self, service):
        result = service.get_warming_stats()
        assert isinstance(result, dict)
        expected_keys = {
            "last_full_warm",
            "last_plan_warm",
            "last_profile_warm",
            "total_items_warmed",
            "errors",
        }
        assert set(result.keys()) == expected_keys

    def test_initial_dates_are_none(self, service):
        result = service.get_warming_stats()
        assert result["last_full_warm"] is None
        assert result["last_plan_warm"] is None
        assert result["last_profile_warm"] is None

    def test_initial_counts_are_zero(self, service):
        result = service.get_warming_stats()
        assert result["total_items_warmed"] == 0
        assert result["errors"] == 0

    def test_dates_become_isoformat_after_warming(self, service):
        service.warming_stats["last_full_warm"] = datetime(2025, 1, 1, 12, 0, 0)
        result = service.get_warming_stats()
        assert result["last_full_warm"] == "2025-01-01T12:00:00"


# ---------------------------------------------------------------------------
# 3. _get_popular_plan_ids
# ---------------------------------------------------------------------------

class TestGetPopularPlanIds:
    def test_returns_list_of_strings(self, service, mock_db):
        ids = service._get_popular_plan_ids(mock_db, limit=5)
        assert isinstance(ids, list)
        assert all(isinstance(i, str) for i in ids)

    def test_count_matches_limit_when_small(self, service, mock_db):
        ids = service._get_popular_plan_ids(mock_db, limit=5)
        assert len(ids) == 5

    def test_capped_at_10(self, service, mock_db):
        ids = service._get_popular_plan_ids(mock_db, limit=200)
        assert len(ids) == 10

    def test_ids_have_plan_prefix(self, service, mock_db):
        ids = service._get_popular_plan_ids(mock_db, limit=3)
        assert ids == ["plan_0", "plan_1", "plan_2"]


# ---------------------------------------------------------------------------
# 4. _get_plan_data
# ---------------------------------------------------------------------------

class TestGetPlanData:
    def test_returns_valid_json_string(self, service, mock_db):
        data = service._get_plan_data(mock_db, "plan_42")
        assert isinstance(data, str)
        parsed = json.loads(data)
        assert parsed["id"] == "plan_42"
        assert "name" in parsed
        assert "cached_at" in parsed

    def test_returns_string_not_none(self, service, mock_db):
        assert service._get_plan_data(mock_db, "any_id") is not None


# ---------------------------------------------------------------------------
# 5. _get_active_user_ids
# ---------------------------------------------------------------------------

class TestGetActiveUserIds:
    def test_returns_list_of_strings(self, service, mock_db):
        ids = service._get_active_user_ids(mock_db, days=7, limit=5)
        assert isinstance(ids, list)
        assert all(isinstance(i, str) for i in ids)

    def test_count_capped_at_10(self, service, mock_db):
        ids = service._get_active_user_ids(mock_db, days=7, limit=100)
        assert len(ids) == 10

    def test_ids_have_user_prefix(self, service, mock_db):
        ids = service._get_active_user_ids(mock_db, days=7, limit=3)
        assert ids == ["user_0", "user_1", "user_2"]


# ---------------------------------------------------------------------------
# 6. _get_recommendation_data
# ---------------------------------------------------------------------------

class TestGetRecommendationData:
    def test_returns_dict(self, service, mock_db):
        data = service._get_recommendation_data(mock_db, "rec_7")
        assert isinstance(data, dict)

    def test_has_expected_keys(self, service, mock_db):
        data = service._get_recommendation_data(mock_db, "rec_7")
        assert "id" in data
        assert "user_id" in data
        assert "plans" in data
        assert "cached_at" in data

    def test_id_matches_input(self, service, mock_db):
        data = service._get_recommendation_data(mock_db, "rec_99")
        assert data["id"] == "rec_99"

    def test_user_id_derived_from_rec_id(self, service, mock_db):
        data = service._get_recommendation_data(mock_db, "rec_5")
        assert data["user_id"] == "user_for_rec_5"


# ---------------------------------------------------------------------------
# 7. warm_popular_plans  (SessionLocal mocked)
# ---------------------------------------------------------------------------

class TestWarmPopularPlans:
    @patch("services.cache_warming.SessionLocal")
    async def test_returns_warmed_count(self, mock_session_cls, service):
        mock_session_cls.return_value = MagicMock()
        count = await service.warm_popular_plans(limit=5)
        # The disabled cache's set() always returns False, so warmed_count
        # stays 0 because the `if plan_data` branch runs but cache.set
        # returns False and the code does not check the return value --
        # it increments unconditionally after set().
        # Re-reading the source: the code increments warmed_count += 1
        # regardless of set()'s return value.
        assert count == 5

    @patch("services.cache_warming.SessionLocal")
    async def test_calls_cache_set_per_plan(self, mock_session_cls, disabled_cache):
        mock_session_cls.return_value = MagicMock()
        disabled_cache.set = MagicMock(return_value=False)
        svc = CacheWarmingService(cache_service=disabled_cache)

        await svc.warm_popular_plans(limit=3)
        assert disabled_cache.set.call_count == 3

    @patch("services.cache_warming.SessionLocal")
    async def test_updates_last_plan_warm(self, mock_session_cls, service):
        mock_session_cls.return_value = MagicMock()
        assert service.warming_stats["last_plan_warm"] is None

        await service.warm_popular_plans(limit=2)
        assert service.warming_stats["last_plan_warm"] is not None
        assert isinstance(service.warming_stats["last_plan_warm"], datetime)

    @patch("services.cache_warming.SessionLocal")
    async def test_closes_db_session(self, mock_session_cls):
        mock_db = MagicMock()
        mock_session_cls.return_value = mock_db
        svc = CacheWarmingService(cache_service=OptimizedCacheService(enabled=False))

        await svc.warm_popular_plans(limit=1)
        mock_db.close.assert_called_once()

    @patch("services.cache_warming.SessionLocal")
    async def test_count_capped_at_ten_plans(self, mock_session_cls, service):
        mock_session_cls.return_value = MagicMock()
        count = await service.warm_popular_plans(limit=200)
        # placeholder returns min(limit, 10) IDs
        assert count == 10


# ---------------------------------------------------------------------------
# 8. warm_startup_cache  (sub-methods mocked)
# ---------------------------------------------------------------------------

class TestWarmStartupCache:
    async def test_calls_all_three_warmers(self, service):
        service.warm_popular_plans = AsyncMock(return_value=10)
        service.warm_active_user_profiles = AsyncMock(return_value=5)
        service.warm_recent_recommendations = AsyncMock(return_value=3)

        await service.warm_startup_cache()

        service.warm_popular_plans.assert_awaited_once_with(limit=100)
        service.warm_active_user_profiles.assert_awaited_once_with(days=7, limit=50)
        service.warm_recent_recommendations.assert_awaited_once_with(days=1, limit=50)

    async def test_updates_total_items_warmed(self, service):
        service.warm_popular_plans = AsyncMock(return_value=10)
        service.warm_active_user_profiles = AsyncMock(return_value=5)
        service.warm_recent_recommendations = AsyncMock(return_value=3)

        await service.warm_startup_cache()

        assert service.warming_stats["total_items_warmed"] == 18

    async def test_updates_last_full_warm(self, service):
        service.warm_popular_plans = AsyncMock(return_value=0)
        service.warm_active_user_profiles = AsyncMock(return_value=0)
        service.warm_recent_recommendations = AsyncMock(return_value=0)

        await service.warm_startup_cache()

        assert service.warming_stats["last_full_warm"] is not None
        assert isinstance(service.warming_stats["last_full_warm"], datetime)

    async def test_increments_errors_on_failure(self, service):
        service.warm_popular_plans = AsyncMock(side_effect=RuntimeError("boom"))

        await service.warm_startup_cache()

        assert service.warming_stats["errors"] == 1

    async def test_accumulates_total_items_across_calls(self, service):
        service.warm_popular_plans = AsyncMock(return_value=2)
        service.warm_active_user_profiles = AsyncMock(return_value=2)
        service.warm_recent_recommendations = AsyncMock(return_value=2)

        await service.warm_startup_cache()
        await service.warm_startup_cache()

        assert service.warming_stats["total_items_warmed"] == 12


# ---------------------------------------------------------------------------
# 9. refresh_expiring_cache  (placeholder -- just confirm no errors)
# ---------------------------------------------------------------------------

class TestRefreshExpiringCache:
    async def test_runs_without_error(self, service):
        # Should complete silently -- it's a no-op placeholder.
        await service.refresh_expiring_cache()

    async def test_accepts_custom_threshold(self, service):
        await service.refresh_expiring_cache(threshold_seconds=60)

    async def test_does_not_increment_errors(self, service):
        await service.refresh_expiring_cache()
        assert service.warming_stats["errors"] == 0
