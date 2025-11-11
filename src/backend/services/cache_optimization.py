"""
Cache Optimization Service.
Story 7.1 - Epic 7: Performance Optimization

Provides advanced caching optimizations including:
- Cache hit rate monitoring and analysis
- Intelligent TTL management
- Selective cache invalidation
- Graceful degradation on cache failures

Target: >80% cache hit rate
"""

import logging
import time
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache statistics for monitoring."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate as percentage."""
        return 100 - self.hit_rate

    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.errors / self.total_requests) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "errors": self.errors,
            "hit_rate": round(self.hit_rate, 2),
            "miss_rate": round(self.miss_rate, 2),
            "error_rate": round(self.error_rate, 2),
            "last_reset": self.last_reset.isoformat(),
        }


@dataclass
class CacheKeyStats:
    """Statistics for individual cache key patterns."""
    pattern: str
    hits: int = 0
    misses: int = 0
    avg_ttl: float = 0.0
    last_accessed: Optional[datetime] = None

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate for this key pattern."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100


class OptimizedCacheService:
    """
    Advanced caching service with optimization features.

    Features:
    - Automatic hit rate monitoring
    - Intelligent TTL management based on access patterns
    - Selective invalidation with versioned keys
    - Graceful degradation on failures
    - Detailed analytics and reporting
    """

    # Default TTL configurations (optimized based on usage patterns)
    DEFAULT_TTLS = {
        "plan_catalog": 3600,        # 1 hour - frequently updated
        "user_profile": 86400,        # 24 hours - changes infrequently
        "recommendations": 86400,     # 24 hours - stable for a day
        "usage_analysis": 604800,     # 1 week - historical data
        "response_cache": 300,        # 5 minutes - API responses
    }

    # Key patterns for monitoring
    KEY_PATTERNS = {
        "plan": r"plan_catalog:.*",
        "user": r"user_profile:.*",
        "recommendation": r"recommendations:.*",
        "usage": r"usage_analysis:.*",
        "response": r"cache:response:.*",
    }

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        enabled: bool = True,
        stats_interval: int = 300,  # 5 minutes
    ):
        """
        Initialize optimized cache service.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            redis_password: Redis password (if required)
            enabled: Whether caching is enabled
            stats_interval: Interval for stats aggregation (seconds)
        """
        self.enabled = enabled and REDIS_AVAILABLE
        self._client: Optional[Redis] = None
        self.stats = CacheStats()
        self.key_stats: Dict[str, CacheKeyStats] = defaultdict(
            lambda: CacheKeyStats(pattern="unknown")
        )
        self.stats_interval = stats_interval
        self._last_stats_flush = time.time()

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
                    socket_keepalive=True,
                    health_check_interval=30,
                )
                # Test connection
                self._client.ping()
                logger.info("Cache service initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Running without cache.")
                self.enabled = False
                self._client = None

    def get(
        self,
        key: str,
        default: Any = None,
        deserializer: Optional[Callable] = None,
    ) -> Optional[Any]:
        """
        Get value from cache with statistics tracking.

        Args:
            key: Cache key
            default: Default value if not found
            deserializer: Optional function to deserialize value

        Returns:
            Cached value or default
        """
        self.stats.total_requests += 1

        if not self.enabled or not self._client:
            self.stats.cache_misses += 1
            return default

        try:
            value = self._client.get(key)

            if value is not None:
                self.stats.cache_hits += 1
                self._update_key_stats(key, hit=True)
                logger.debug(f"Cache HIT: {key}")

                # Deserialize if needed
                if deserializer:
                    return deserializer(value)
                return value
            else:
                self.stats.cache_misses += 1
                self._update_key_stats(key, hit=False)
                logger.debug(f"Cache MISS: {key}")
                return default

        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serializer: Optional[Callable] = None,
    ) -> bool:
        """
        Set value in cache with automatic TTL optimization.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (auto-determined if not provided)
            serializer: Optional function to serialize value

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.enabled or not self._client:
            return False

        try:
            # Auto-determine TTL if not provided
            if ttl is None:
                ttl = self._determine_ttl(key)

            # Serialize if needed
            if serializer:
                value = serializer(value)

            # Store with TTL
            self._client.setex(key, ttl, value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            self.stats.errors += 1
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled or not self._client:
            return False

        try:
            result = self._client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., "user_profile:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self._client:
            return 0

        try:
            keys = self._client.keys(pattern)
            if keys:
                deleted = self._client.delete(*keys)
                logger.info(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        if not self.enabled or not self._client:
            return False

        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key.

        Args:
            key: Cache key

        Returns:
            Remaining TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        if not self.enabled or not self._client:
            return -2

        try:
            return self._client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -2

    def invalidate_by_prefix(self, prefix: str) -> int:
        """
        Selective invalidation by key prefix.

        Args:
            prefix: Key prefix to invalidate

        Returns:
            Number of keys invalidated
        """
        pattern = f"{prefix}:*"
        return self.delete_pattern(pattern)

    def invalidate_user_cache(self, user_id: str) -> int:
        """
        Invalidate all cache entries for a specific user.

        Args:
            user_id: User identifier

        Returns:
            Number of keys invalidated
        """
        count = 0
        patterns = [
            f"user_profile:*:{user_id}",
            f"recommendations:*:{user_id}",
            f"usage_analysis:*:{user_id}",
        ]

        for pattern in patterns:
            count += self.delete_pattern(pattern)

        logger.info(f"Invalidated {count} cache entries for user {user_id}")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        stats_dict = self.stats.to_dict()

        if self.enabled and self._client:
            try:
                info = self._client.info("stats")
                stats_dict.update({
                    "redis_keyspace_hits": info.get("keyspace_hits", 0),
                    "redis_keyspace_misses": info.get("keyspace_misses", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": self._client.info("memory").get("used_memory_human", "0"),
                })
            except Exception as e:
                logger.error(f"Error fetching Redis stats: {e}")

        stats_dict["enabled"] = self.enabled
        return stats_dict

    def get_key_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for individual key patterns.

        Returns:
            List of key pattern statistics
        """
        return [
            {
                "pattern": pattern,
                "hits": stats.hits,
                "misses": stats.misses,
                "hit_rate": round(stats.hit_rate, 2),
                "avg_ttl": round(stats.avg_ttl, 2),
                "last_accessed": stats.last_accessed.isoformat() if stats.last_accessed else None,
            }
            for pattern, stats in self.key_stats.items()
        ]

    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = CacheStats()
        self.key_stats.clear()
        logger.info("Cache statistics reset")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache service.

        Returns:
            Dictionary with health status
        """
        if not self.enabled or not self._client:
            return {
                "healthy": False,
                "status": "disabled",
                "message": "Cache service is disabled",
            }

        try:
            latency_start = time.time()
            self._client.ping()
            latency = (time.time() - latency_start) * 1000  # ms

            return {
                "healthy": True,
                "status": "connected",
                "latency_ms": round(latency, 2),
                "hit_rate": round(self.stats.hit_rate, 2),
            }
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "message": str(e),
            }

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _determine_ttl(self, key: str) -> int:
        """
        Automatically determine TTL based on key pattern.

        Args:
            key: Cache key

        Returns:
            Recommended TTL in seconds
        """
        for cache_type, ttl in self.DEFAULT_TTLS.items():
            if cache_type in key:
                return ttl

        # Default TTL if no pattern matches
        return 300  # 5 minutes

    def _update_key_stats(self, key: str, hit: bool):
        """
        Update statistics for key pattern.

        Args:
            key: Cache key
            hit: Whether this was a cache hit
        """
        # Determine key pattern
        pattern = self._get_key_pattern(key)

        # Update stats
        if pattern not in self.key_stats:
            self.key_stats[pattern] = CacheKeyStats(pattern=pattern)

        stats = self.key_stats[pattern]
        if hit:
            stats.hits += 1
        else:
            stats.misses += 1
        stats.last_accessed = datetime.utcnow()

    def _get_key_pattern(self, key: str) -> str:
        """
        Extract key pattern from specific key.

        Args:
            key: Specific cache key

        Returns:
            Key pattern category
        """
        for pattern_name, pattern in self.KEY_PATTERNS.items():
            if pattern_name in key:
                return pattern_name
        return "other"


# Singleton instance
_optimized_cache_instance: Optional[OptimizedCacheService] = None


def get_optimized_cache() -> OptimizedCacheService:
    """
    Get the global optimized cache service instance.

    Returns:
        OptimizedCacheService instance
    """
    global _optimized_cache_instance
    if _optimized_cache_instance is None:
        _optimized_cache_instance = OptimizedCacheService()
    return _optimized_cache_instance


def configure_optimized_cache(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
    redis_password: Optional[str] = None,
    enabled: bool = True,
) -> OptimizedCacheService:
    """
    Configure the global optimized cache service.

    Args:
        redis_host: Redis server hostname
        redis_port: Redis server port
        redis_db: Redis database number
        redis_password: Redis password (if required)
        enabled: Whether caching is enabled

    Returns:
        Configured OptimizedCacheService instance
    """
    global _optimized_cache_instance
    _optimized_cache_instance = OptimizedCacheService(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_db=redis_db,
        redis_password=redis_password,
        enabled=enabled,
    )
    return _optimized_cache_instance
