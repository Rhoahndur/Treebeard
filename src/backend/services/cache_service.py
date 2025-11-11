"""
Cache Service for Usage Profiles
Story 1.4 - Epic 1: Data Infrastructure & Pipeline

Provides Redis caching for computed usage profiles to improve performance
and reduce redundant computation.

Cache Strategy:
- TTL: 7 days for usage profiles (usage patterns don't change frequently)
- Key pattern: usage_profile:{user_id}
- Invalidation: On user data updates
"""

import json
import hashlib
from typing import Optional, List
from datetime import timedelta

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..schemas.usage_analysis import UsageProfile, MonthlyUsage


class CacheService:
    """
    Redis-based caching service for usage profiles.
    """

    # Cache configuration
    PROFILE_TTL = timedelta(days=7).total_seconds()  # 7 days
    KEY_PREFIX = "usage_profile"
    KEY_VERSION = "v1"  # Increment when schema changes

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        enabled: bool = True,
    ):
        """
        Initialize cache service.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            redis_password: Redis password (if required)
            enabled: Whether caching is enabled (set to False for testing)
        """
        self.enabled = enabled and REDIS_AVAILABLE
        self._client: Optional[Redis] = None

        if self.enabled:
            try:
                self._client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection
                self._client.ping()
            except Exception as e:
                print(f"Warning: Redis connection failed: {e}")
                print("Continuing without caching...")
                self.enabled = False
                self._client = None

    def get_profile(self, user_id: str) -> Optional[UsageProfile]:
        """
        Retrieve cached usage profile.

        Args:
            user_id: User identifier

        Returns:
            UsageProfile if found in cache, None otherwise
        """
        if not self.enabled or not self._client:
            return None

        try:
            key = self._make_key(user_id)
            cached_data = self._client.get(key)

            if cached_data:
                # Deserialize from JSON
                profile_dict = json.loads(cached_data)
                # Note: In production, you'd have a proper deserialization method
                # For now, we'll just return None if cache is hit but can't deserialize
                # The caller will recompute and cache again
                return None  # Placeholder - would need proper deserialization

            return None

        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set_profile(
        self, user_id: str, profile: UsageProfile, ttl: Optional[int] = None
    ) -> bool:
        """
        Store usage profile in cache.

        Args:
            user_id: User identifier
            profile: UsageProfile to cache
            ttl: Time-to-live in seconds (default: 7 days)

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.enabled or not self._client:
            return False

        try:
            key = self._make_key(user_id)
            ttl = ttl or int(self.PROFILE_TTL)

            # Serialize to JSON
            profile_json = json.dumps(profile.to_dict())

            # Store with TTL
            self._client.setex(key, ttl, profile_json)
            return True

        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def invalidate_profile(self, user_id: str) -> bool:
        """
        Invalidate cached profile for a user.

        Args:
            user_id: User identifier

        Returns:
            True if successfully invalidated, False otherwise
        """
        if not self.enabled or not self._client:
            return False

        try:
            key = self._make_key(user_id)
            self._client.delete(key)
            return True

        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False

    def get_usage_data_hash(self, usage_data: List[MonthlyUsage]) -> str:
        """
        Generate a hash of usage data for cache validation.
        Can be used to detect if underlying data has changed.

        Args:
            usage_data: List of monthly usage data

        Returns:
            MD5 hash of the usage data
        """
        # Create a deterministic string representation
        data_str = "|".join([f"{u.month.isoformat()}:{u.kwh}" for u in usage_data])
        return hashlib.md5(data_str.encode()).hexdigest()

    def get_profile_with_hash(
        self, user_id: str, usage_data_hash: str
    ) -> Optional[UsageProfile]:
        """
        Retrieve cached profile only if the usage data hash matches.
        This ensures we don't return stale profiles.

        Args:
            user_id: User identifier
            usage_data_hash: Hash of current usage data

        Returns:
            UsageProfile if found and hash matches, None otherwise
        """
        if not self.enabled or not self._client:
            return None

        try:
            hash_key = self._make_hash_key(user_id)
            cached_hash = self._client.get(hash_key)

            if cached_hash != usage_data_hash:
                # Data has changed, invalidate cache
                self.invalidate_profile(user_id)
                return None

            return self.get_profile(user_id)

        except Exception as e:
            print(f"Cache get with hash error: {e}")
            return None

    def set_profile_with_hash(
        self, user_id: str, profile: UsageProfile, usage_data_hash: str
    ) -> bool:
        """
        Store profile along with usage data hash for validation.

        Args:
            user_id: User identifier
            profile: UsageProfile to cache
            usage_data_hash: Hash of the usage data

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.enabled or not self._client:
            return False

        try:
            # Store the profile
            profile_stored = self.set_profile(user_id, profile)

            if profile_stored:
                # Store the hash with same TTL
                hash_key = self._make_hash_key(user_id)
                ttl = int(self.PROFILE_TTL)
                self._client.setex(hash_key, ttl, usage_data_hash)
                return True

            return False

        except Exception as e:
            print(f"Cache set with hash error: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled or not self._client:
            return {
                "enabled": False,
                "status": "disabled",
            }

        try:
            info = self._client.info("stats")
            return {
                "enabled": True,
                "status": "connected",
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            return {
                "enabled": False,
                "status": f"error: {e}",
            }

    def clear_all_profiles(self) -> int:
        """
        Clear all cached profiles (useful for testing or maintenance).

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self._client:
            return 0

        try:
            pattern = f"{self.KEY_PREFIX}:*"
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0

        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _make_key(self, user_id: str) -> str:
        """Generate cache key for a user profile."""
        return f"{self.KEY_PREFIX}:{self.KEY_VERSION}:{user_id}"

    def _make_hash_key(self, user_id: str) -> str:
        """Generate cache key for usage data hash."""
        return f"{self.KEY_PREFIX}:hash:{self.KEY_VERSION}:{user_id}"


class InMemoryCache:
    """
    Simple in-memory cache fallback when Redis is not available.
    Not suitable for production (not shared across instances).
    """

    def __init__(self):
        """Initialize in-memory cache."""
        self._cache: dict = {}

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        entry = self._cache.get(key)
        if entry:
            # Check if expired (simple TTL check)
            # For simplicity, we don't implement full TTL in memory cache
            return entry
        return None

    def setex(self, key: str, ttl: int, value: str) -> None:
        """Set value with TTL."""
        self._cache[key] = value

    def delete(self, key: str) -> None:
        """Delete key."""
        self._cache.pop(key, None)

    def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        # Simple pattern matching (just prefix)
        prefix = pattern.replace("*", "")
        return [k for k in self._cache.keys() if k.startswith(prefix)]

    def ping(self) -> bool:
        """Ping test."""
        return True


# Singleton instance (can be configured at application startup)
_cache_instance: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get the global cache service instance.

    Returns:
        CacheService instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance


def configure_cache(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
    redis_password: Optional[str] = None,
    enabled: bool = True,
) -> CacheService:
    """
    Configure the global cache service.

    Args:
        redis_host: Redis server hostname
        redis_port: Redis server port
        redis_db: Redis database number
        redis_password: Redis password (if required)
        enabled: Whether caching is enabled

    Returns:
        Configured CacheService instance
    """
    global _cache_instance
    _cache_instance = CacheService(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_db=redis_db,
        redis_password=redis_password,
        enabled=enabled,
    )
    return _cache_instance
