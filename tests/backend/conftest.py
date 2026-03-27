"""Shared fixtures for backend unit tests."""

import pytest

from services.cache_optimization import OptimizedCacheService


@pytest.fixture
def disabled_cache():
    """An OptimizedCacheService with caching disabled (no Redis needed)."""
    return OptimizedCacheService(enabled=False)
