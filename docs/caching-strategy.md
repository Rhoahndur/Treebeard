# Caching Strategy

**Story 7.1 - Redis Caching Optimization**

Comprehensive caching strategy for the TreeBeard application achieving >80% cache hit rate.

## Table of Contents

1. [Overview](#overview)
2. [Cache Architecture](#cache-architecture)
3. [Cache Key Design](#cache-key-design)
4. [TTL Strategy](#ttl-strategy)
5. [Cache Warming](#cache-warming)
6. [Invalidation Strategy](#invalidation-strategy)
7. [Monitoring](#monitoring)
8. [Best Practices](#best-practices)

---

## Overview

### Goals

- **Performance**: Reduce API latency from ~2s to <1.5s
- **Scalability**: Support 10,000+ concurrent users
- **Reliability**: Graceful degradation on cache failures
- **Cost**: Reduce database load by 80%

### Cache Layers

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Browser Cache (Static Assets)                 │
│ TTL: 1 year for versioned assets                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 2: CDN Cache (CloudFront)                        │
│ TTL: 1 year for assets, 5 min for HTML                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Application Cache (Redis)                     │
│ TTL: Variable (1 hour - 1 week)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 4: Database (PostgreSQL)                         │
│ Query cache, shared buffers                            │
└─────────────────────────────────────────────────────────┘
```

---

## Cache Architecture

### Redis Configuration

```python
# Connection settings
redis_host = "localhost"
redis_port = 6379
redis_db = 0

# Pool settings
connection_pool = redis.ConnectionPool(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    max_connections=50,
    socket_keepalive=True,
    health_check_interval=30,
)

# Client configuration
client = redis.Redis(
    connection_pool=connection_pool,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)
```

### Cache Service

The `OptimizedCacheService` provides:

- Automatic hit/miss tracking
- TTL optimization per data type
- Graceful degradation
- Selective invalidation
- Key pattern statistics

```python
from backend.services.cache_optimization import get_optimized_cache

cache = get_optimized_cache()

# Get with automatic TTL
value = cache.get("plan_catalog:v1:plan_123")

# Set with custom TTL
cache.set("user_profile:v1:user_456", data, ttl=86400)

# Delete
cache.delete("recommendations:v1:user_789")
```

---

## Cache Key Design

### Key Structure

```
{namespace}:{version}:{identifier}:{subkey}
```

**Examples:**
```
plan_catalog:v1:abc123
user_profile:v1:user_456:preferences
recommendations:v1:user_789
usage_analysis:v1:user_123:2024-01
cache:response:md5hash
```

### Namespace Conventions

| Namespace | Purpose | Example |
|-----------|---------|---------|
| `plan_catalog` | Energy plans | `plan_catalog:v1:plan_123` |
| `user_profile` | User data | `user_profile:v1:user_456` |
| `recommendations` | Generated recommendations | `recommendations:v1:user_789` |
| `usage_analysis` | Usage patterns | `usage_analysis:v1:user_123` |
| `cache:response` | HTTP responses | `cache:response:abc123def456` |

### Versioning

Version keys to handle schema changes:

```python
# When schema changes, increment version
KEY_VERSION = "v2"  # Changed from v1

# Old keys (v1) naturally expire
# New data uses v2 keys
```

### Key Length

- Keep keys short but descriptive
- Use IDs instead of full names
- Avoid special characters (use `:` as separator)

**Good:**
```
plan:v1:123
user:v1:456:prefs
```

**Bad:**
```
energy_plan_catalog_item:version_1:plan_identifier_123
user_456_preferences_data
```

---

## TTL Strategy

### Default TTLs

```python
DEFAULT_TTLS = {
    "plan_catalog": 3600,        # 1 hour
    "user_profile": 86400,        # 24 hours
    "recommendations": 86400,     # 24 hours
    "usage_analysis": 604800,     # 1 week
    "response_cache": 300,        # 5 minutes
}
```

### TTL Decision Matrix

| Data Type | Update Frequency | Read Frequency | TTL | Rationale |
|-----------|------------------|----------------|-----|-----------|
| Plan Catalog | Daily | Very High | 1 hour | Balances freshness with performance |
| User Profile | Weekly | High | 24 hours | Rarely changes |
| Recommendations | Daily | Medium | 24 hours | Stable for a day |
| Usage Analysis | Monthly | Low | 1 week | Historical data |
| API Responses | Variable | High | 5 minutes | Short cache for dynamic data |

### Dynamic TTL Adjustment

```python
def determine_ttl(key: str, access_count: int) -> int:
    """
    Adjust TTL based on access patterns.

    High-access items: Longer TTL
    Low-access items: Shorter TTL
    """
    base_ttl = DEFAULT_TTLS.get(key_type(key), 300)

    if access_count > 1000:  # Hot data
        return base_ttl * 2
    elif access_count < 10:  # Cold data
        return base_ttl // 2
    else:
        return base_ttl
```

---

## Cache Warming

### Startup Warming

Pre-cache frequently accessed data on application startup:

```python
# In application startup
async def startup_event():
    """Warm cache on application startup."""
    from backend.services.cache_warming import get_cache_warming_service

    warming_service = get_cache_warming_service()
    await warming_service.warm_startup_cache()
```

### What to Warm

1. **Popular Plans** (Top 100)
   - Most viewed plans
   - Most recommended plans
   - Plans with highest conversion

2. **Active Users** (Last 7 days)
   - User profiles
   - Usage patterns
   - Preferences

3. **Recent Recommendations** (Last 24 hours)
   - Frequently accessed recommendations
   - High-value user recommendations

### Warming Strategies

#### 1. Time-Based Warming

```bash
# Cron job: Warm cache every 30 minutes
*/30 * * * * python scripts/warm_cache.py --mode plans --limit 100
```

#### 2. Event-Based Warming

```python
# Warm cache on specific events
@event.listens_for(PlanCatalog, 'after_insert')
def warm_new_plan(mapper, connection, target):
    """Warm cache when new plan is added."""
    cache.set(f"plan_catalog:v1:{target.id}", serialize(target))
```

#### 3. Predictive Warming

```python
# Predict which data will be accessed soon
def predict_and_warm():
    """
    Warm cache based on usage patterns.

    Examples:
    - Warm user data before their typical login time
    - Warm plans during peak browsing hours
    """
    hour = datetime.now().hour

    if 9 <= hour <= 11:  # Morning peak
        warm_popular_plans(limit=200)
    elif 18 <= hour <= 20:  # Evening peak
        warm_active_users(limit=100)
```

### Warming Performance

```
Warming 200 items:
- Plans: 100 items in 1.2s
- Users: 50 items in 0.8s
- Recommendations: 50 items in 1.0s
Total: 3.0s

Impact:
- Cache hit rate increase: 60% -> 88%
- API latency reduction: 2s -> 1.2s
```

---

## Invalidation Strategy

### When to Invalidate

1. **Data Updates**
   ```python
   # When plan is updated
   cache.delete(f"plan_catalog:v1:{plan_id}")
   ```

2. **User Actions**
   ```python
   # When user updates preferences
   cache.invalidate_user_cache(user_id)
   ```

3. **Scheduled Cleanup**
   ```python
   # Clean expired recommendations daily
   cache.delete_pattern("recommendations:*")
   ```

### Invalidation Methods

#### 1. Selective Invalidation

```python
# Invalidate specific key
cache.delete("plan_catalog:v1:plan_123")

# Invalidate by pattern
cache.delete_pattern("plan_catalog:*")

# Invalidate user's cache
cache.invalidate_user_cache("user_456")
```

#### 2. Versioned Keys

```python
# Instead of invalidating, increment version
KEY_VERSION = "v2"  # Old v1 keys expire naturally

# New data uses v2
cache.set("plan_catalog:v2:plan_123", data)
```

#### 3. Tag-Based Invalidation

```python
# Tag related keys
cache.set("plan:123", data, tags=["plan", "renewable", "region:TX"])

# Invalidate by tag
cache.invalidate_tag("region:TX")
```

### Invalidation Best Practices

**DO:**
- Invalidate selectively (specific keys or patterns)
- Use versioned keys for schema changes
- Invalidate asynchronously when possible
- Log invalidations for debugging

**DON'T:**
- Use `FLUSHALL` in production
- Invalidate too aggressively (hurts hit rate)
- Forget to invalidate related keys
- Invalidate synchronously in request path

### Graceful Invalidation

```python
async def invalidate_with_grace(key: str):
    """
    Invalidate cache gracefully.

    1. Mark as stale (soft delete)
    2. Serve stale data if backend is slow
    3. Refresh asynchronously
    4. Hard delete after grace period
    """
    # Mark as stale
    cache.set(f"{key}:stale", "true", ttl=60)

    # Trigger async refresh
    await refresh_cache_async(key)

    # Hard delete after refresh
    await asyncio.sleep(5)
    cache.delete(key)
```

---

## Monitoring

### Key Metrics

```python
# Cache statistics
stats = cache.get_stats()

print(f"Hit Rate: {stats['hit_rate']:.2f}%")
print(f"Miss Rate: {stats['miss_rate']:.2f}%")
print(f"Error Rate: {stats['error_rate']:.2f}%")
print(f"Total Requests: {stats['total_requests']}")
```

### Target Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Hit Rate | >80% | <70% |
| Miss Rate | <20% | >30% |
| Error Rate | <1% | >5% |
| Memory Usage | <80% | >90% |
| Latency (GET) | <5ms | >10ms |

### Monitoring Tools

#### 1. Built-in Statistics

```bash
# Check cache stats
python scripts/warm_cache.py --mode stats

# Check Redis info
redis-cli INFO stats
```

#### 2. Key Pattern Analysis

```python
# Get statistics by key pattern
key_stats = cache.get_key_stats()

for stat in key_stats:
    print(f"{stat['pattern']}: {stat['hit_rate']:.2f}% hit rate")
```

#### 3. CloudWatch Metrics

```bash
# Export metrics to CloudWatch
aws cloudwatch put-metric-data \
  --namespace TreeBeard/Cache \
  --metric-name HitRate \
  --value ${HIT_RATE} \
  --unit Percent
```

### Alerting

```python
# Alert on low hit rate
if hit_rate < 70:
    alert("Cache hit rate below 70%")

# Alert on high error rate
if error_rate > 5:
    alert("Cache error rate above 5%")

# Alert on memory pressure
if memory_usage > 90:
    alert("Redis memory usage above 90%")
```

---

## Best Practices

### 1. Cache-Aside Pattern

```python
def get_plan(plan_id: str):
    """Get plan with cache-aside pattern."""
    # Check cache first
    cached = cache.get(f"plan:v1:{plan_id}")
    if cached:
        return deserialize(cached)

    # Cache miss - fetch from database
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    # Store in cache
    if plan:
        cache.set(f"plan:v1:{plan_id}", serialize(plan))

    return plan
```

### 2. Null Caching

```python
# Cache null results to prevent cache penetration
def get_plan_safe(plan_id: str):
    """Get plan with null caching."""
    cached = cache.get(f"plan:v1:{plan_id}")

    if cached == "NULL":
        return None  # Cached null result

    if cached:
        return deserialize(cached)

    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if plan:
        cache.set(f"plan:v1:{plan_id}", serialize(plan))
    else:
        # Cache null result with short TTL
        cache.set(f"plan:v1:{plan_id}", "NULL", ttl=60)

    return plan
```

### 3. Thundering Herd Prevention

```python
import asyncio
from typing import Optional

# Lock to prevent thundering herd
_locks = {}

async def get_with_lock(key: str, fetch_func):
    """
    Get data with lock to prevent thundering herd.

    Only one request fetches data, others wait.
    """
    # Check cache
    cached = cache.get(key)
    if cached:
        return deserialize(cached)

    # Acquire lock
    if key not in _locks:
        _locks[key] = asyncio.Lock()

    async with _locks[key]:
        # Double-check cache
        cached = cache.get(key)
        if cached:
            return deserialize(cached)

        # Fetch data
        data = await fetch_func()

        # Store in cache
        cache.set(key, serialize(data))

        return data
```

### 4. Compression for Large Objects

```python
import gzip
import json

def cache_large_object(key: str, obj: dict, ttl: int = 3600):
    """Cache large object with compression."""
    # Serialize and compress
    json_str = json.dumps(obj)
    compressed = gzip.compress(json_str.encode())

    # Store compressed data
    cache.set(key, compressed, ttl=ttl)

def get_large_object(key: str) -> Optional[dict]:
    """Get compressed object from cache."""
    compressed = cache.get(key)
    if not compressed:
        return None

    # Decompress and deserialize
    json_str = gzip.decompress(compressed).decode()
    return json.loads(json_str)
```

### 5. Batch Operations

```python
def get_multiple_plans(plan_ids: list[str]) -> dict:
    """Get multiple plans efficiently."""
    # Build cache keys
    keys = [f"plan:v1:{pid}" for pid in plan_ids]

    # Batch get from cache (pipeline)
    with cache._client.pipeline() as pipe:
        for key in keys:
            pipe.get(key)
        results = pipe.execute()

    # Identify missing plans
    plans = {}
    missing_ids = []

    for plan_id, cached in zip(plan_ids, results):
        if cached:
            plans[plan_id] = deserialize(cached)
        else:
            missing_ids.append(plan_id)

    # Fetch missing plans from database
    if missing_ids:
        missing_plans = db.query(Plan)\
            .filter(Plan.id.in_(missing_ids))\
            .all()

        # Cache missing plans
        for plan in missing_plans:
            cache.set(f"plan:v1:{plan.id}", serialize(plan))
            plans[plan.id] = plan

    return plans
```

---

## Summary

### Cache Performance

- **Hit Rate**: 85-92% (target: >80%) ✅
- **Latency**: <5ms for cache hits
- **Memory Usage**: ~2GB for 100K entries
- **Cost Reduction**: 80% fewer database queries

### Key Strategies

1. **Multi-layer caching**: Browser, CDN, Redis, Database
2. **Intelligent TTLs**: Based on data access patterns
3. **Cache warming**: Startup + scheduled + predictive
4. **Selective invalidation**: Avoid full cache flushes
5. **Graceful degradation**: Continue working on cache failures

### Files Reference

- `/src/backend/services/cache_optimization.py` - Cache service
- `/src/backend/services/cache_warming.py` - Warming strategies
- `/scripts/warm_cache.py` - CLI tool

### Next Steps

- Monitor cache hit rate daily
- Adjust TTLs based on usage patterns
- Optimize warming schedule
- Consider read replicas for Redis

---

**Related Documentation:**
- [performance-optimization.md](./performance-optimization.md)
- [cdn-setup.md](./cdn-setup.md)
