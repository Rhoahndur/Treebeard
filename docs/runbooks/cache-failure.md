# Runbook: Cache Failure (Redis)

**Alert**: Redis cache unavailable or connection errors
**Severity**: Critical
**Response Time**: Immediate (< 5 minutes)

## Overview

This runbook covers Redis cache failures including connection issues, memory exhaustion, and performance degradation.

## Symptoms

- Redis connection errors in application logs
- Cache operations failing
- Degraded application performance
- Increased database load
- Users experiencing slow response times

## Impact

When Redis is unavailable:
- Application falls back to database for all queries
- Recommendation generation becomes slower
- Database load increases significantly
- API response times degrade
- User experience suffers

## Investigation Steps

### 1. Check Redis Availability (1 minute)

```bash
# Test Redis connectivity
redis-cli -h $REDIS_HOST -p 6379 ping
# Expected: PONG

# Check if Redis is running (Kubernetes)
kubectl get pods -n treebeard-production | grep redis

# Check Redis logs
kubectl logs -n treebeard-production statefulset/redis --tail=100

# Check application logs for Redis errors
kubectl logs -n treebeard-production deployment/treebeard-api --tail=100 | grep -i redis
```

### 2. Check Redis Health (2 minutes)

```bash
# Connect to Redis
redis-cli -h $REDIS_HOST -p 6379

# Check server info
INFO server

# Check memory usage
INFO memory

# Check stats
INFO stats

# Check clients
INFO clients

# Check for slow commands
SLOWLOG GET 10

# Check replication status (if using replication)
INFO replication
```

### 3. Check Redis Metrics (2 minutes)

```bash
# Memory usage
redis-cli -h $REDIS_HOST INFO memory | grep used_memory_human

# Connected clients
redis-cli -h $REDIS_HOST INFO clients | grep connected_clients

# Hit rate
redis-cli -h $REDIS_HOST INFO stats | grep -E "keyspace_hits|keyspace_misses"

# Evicted keys (memory pressure)
redis-cli -h $REDIS_HOST INFO stats | grep evicted_keys

# Rejected connections
redis-cli -h $REDIS_HOST INFO stats | grep rejected_connections

# Check for blocking operations
redis-cli -h $REDIS_HOST INFO persistence | grep rdb_bgsave_in_progress
```

### 4. Check Network Connectivity (1 minute)

```bash
# Test network latency
redis-cli -h $REDIS_HOST --latency
# Should be < 1ms for local network

# Check from application pod
kubectl exec -it -n treebeard-production deployment/treebeard-api -- redis-cli -h $REDIS_HOST ping

# Check network policies
kubectl get networkpolicies -n treebeard-production

# Check service endpoints
kubectl get endpoints redis -n treebeard-production
```

## Resolution Steps

### Redis Completely Down

#### Restart Redis

```bash
# Kubernetes
kubectl rollout restart statefulset/redis -n treebeard-production

# Verify restart
kubectl get pods -n treebeard-production | grep redis

# Wait for ready status
kubectl wait --for=condition=ready pod/redis-0 -n treebeard-production --timeout=60s

# Test connectivity
redis-cli -h $REDIS_HOST ping

# Check if data persisted (if using persistence)
redis-cli -h $REDIS_HOST DBSIZE
```

#### If Restart Fails

```bash
# Check pod events
kubectl describe pod redis-0 -n treebeard-production

# Check persistent volume
kubectl get pvc -n treebeard-production | grep redis

# Check resource limits
kubectl describe statefulset redis -n treebeard-production

# Check Redis configuration
kubectl get configmap redis-config -n treebeard-production -o yaml

# Force delete pod if stuck
kubectl delete pod redis-0 -n treebeard-production --force --grace-period=0
```

### Redis Out of Memory

```bash
# Check memory usage
redis-cli -h $REDIS_HOST INFO memory | grep used_memory_human

# Check eviction policy
redis-cli -h $REDIS_HOST CONFIG GET maxmemory-policy
# Should be: allkeys-lru or volatile-lru

# Immediate: Flush LRU keys
redis-cli -h $REDIS_HOST MEMORY PURGE

# Clear specific databases if needed
redis-cli -h $REDIS_HOST -n 0 FLUSHDB

# Or clear all (use with caution)
redis-cli -h $REDIS_HOST FLUSHALL

# Increase memory limit (Kubernetes)
kubectl edit statefulset redis -n treebeard-production
# Update resources.limits.memory

# Or scale to larger instance
# Update helm values or manifest with more memory
```

### Redis Performance Issues

#### Too Many Connections

```bash
# Check current connections
redis-cli -h $REDIS_HOST INFO clients | grep connected_clients

# Check max connections
redis-cli -h $REDIS_HOST CONFIG GET maxclients

# Increase if needed
redis-cli -h $REDIS_HOST CONFIG SET maxclients 10000

# Check for connection leaks in application
# Review connection pool settings in application
```

#### Slow Commands

```bash
# Check slow log
redis-cli -h $REDIS_HOST SLOWLOG GET 20

# Common slow operations:
# - KEYS * (never use in production!)
# - Large SMEMBERS, HGETALL
# - Complex Lua scripts

# If using KEYS, replace with SCAN
redis-cli -h $REDIS_HOST SCAN 0 MATCH "pattern:*" COUNT 100

# Check for blocking operations
redis-cli -h $REDIS_HOST INFO persistence | grep rdb_bgsave_in_progress

# Disable persistence temporarily if causing issues
redis-cli -h $REDIS_HOST CONFIG SET save ""
```

#### High Latency

```bash
# Check latency
redis-cli -h $REDIS_HOST --latency

# Check intrinsic latency
redis-cli -h $REDIS_HOST --intrinsic-latency 100

# Check if persistence is causing delays
redis-cli -h $REDIS_HOST INFO persistence

# Optimize persistence settings
redis-cli -h $REDIS_HOST CONFIG SET save "900 1 300 10"
redis-cli -h $REDIS_HOST CONFIG SET stop-writes-on-bgsave-error no
redis-cli -h $REDIS_HOST CONFIG SET rdbcompression yes
```

### Application Fallback Mode

If Redis cannot be restored immediately, enable fallback mode:

```python
# Application should already have this logic
# Verify it's working:

# 1. Disable cache in application (environment variable)
kubectl set env deployment/treebeard-api CACHE_ENABLED=false -n treebeard-production

# 2. Scale up API instances to handle increased database load
kubectl scale deployment/treebeard-api --replicas=8 -n treebeard-production

# 3. Enable database read replicas for load distribution
# Update database connection strings to use read replicas for SELECT queries

# 4. Monitor database performance closely
# Watch for database connection pool exhaustion
```

## Recovery Steps

### After Redis is Restored

```bash
# 1. Verify Redis is healthy
redis-cli -h $REDIS_HOST ping
redis-cli -h $REDIS_HOST INFO server

# 2. Check memory usage is normal
redis-cli -h $REDIS_HOST INFO memory

# 3. Warm up cache with critical data
# Run cache warming script
python scripts/warm_cache.py --critical-only

# 4. Re-enable cache in application
kubectl set env deployment/treebeard-api CACHE_ENABLED=true -n treebeard-production

# 5. Scale API back to normal replica count
kubectl scale deployment/treebeard-api --replicas=3 -n treebeard-production

# 6. Monitor cache hit rate
# Should gradually increase to 60-80%
```

### Cache Warming

```python
# Example cache warming script
# scripts/warm_cache.py

import asyncio
import redis
from app.services.cache_service import CacheService

async def warm_critical_caches():
    cache = CacheService()

    # Warm plan catalog cache
    await cache.warm_plan_catalog()

    # Warm user profiles for active users
    active_users = await get_active_users()
    for user_id in active_users:
        await cache.warm_user_profile(user_id)

    # Warm common recommendations
    await cache.warm_popular_recommendations()

    print("Cache warming complete")

if __name__ == "__main__":
    asyncio.run(warm_critical_caches())
```

## Prevention

### Redis Configuration Best Practices

```bash
# Optimal Redis configuration
# redis.conf or ConfigMap

# Memory management
maxmemory 4gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence (balance performance vs durability)
save 900 1       # After 900 sec if at least 1 key changed
save 300 10      # After 300 sec if at least 10 keys changed
save 60 10000    # After 60 sec if at least 10000 keys changed

# Performance
tcp-backlog 511
timeout 0
tcp-keepalive 300
loglevel notice

# Security
requirepass ${REDIS_PASSWORD}
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""

# Limits
maxclients 10000
```

### Application Connection Pool

```python
# Optimal connection pool settings
REDIS_POOL_SIZE = 10
REDIS_POOL_MAX_CONNECTIONS = 50
REDIS_SOCKET_TIMEOUT = 5
REDIS_SOCKET_CONNECT_TIMEOUT = 5
REDIS_RETRY_ON_TIMEOUT = True
REDIS_HEALTH_CHECK_INTERVAL = 30
```

### Monitoring

```yaml
# Key metrics to monitor
metrics:
  - used_memory_percentage    # Alert if > 80%
  - connected_clients         # Alert if near maxclients
  - evicted_keys              # Alert if > 100/min
  - rejected_connections      # Alert if > 0
  - keyspace_hit_rate        # Alert if < 60%
  - replication_lag          # Alert if > 1 second
  - command_latency_p95      # Alert if > 10ms
```

### High Availability Setup

```yaml
# Redis Sentinel or Cluster for HA
# Example Sentinel configuration

sentinel:
  enabled: true
  replicas: 3
  quorum: 2

redis:
  master:
    replicas: 1
  slave:
    replicas: 2

# Automatic failover
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000
```

## Escalation

- **5 minutes**: If Redis is completely down, escalate immediately
- **15 minutes**: If cannot restore, engage senior DevOps
- **30 minutes**: Consider enabling maintenance mode

## Communication Template

```
🔴 INCIDENT: Redis Cache Failure

Status: [Investigating/Identified/Resolving]
Started: [TIME]
Severity: Critical

Impact:
- Cache unavailable, falling back to database
- API response times elevated
- Users may experience slower performance

Current Actions:
- [Action 1]
- [Action 2]

Estimated Resolution: [TIME]

Updates: Every 10 minutes in #alerts
```

## Post-Incident

1. **Review Redis logs** for root cause
2. **Check for memory leaks** in application
3. **Review cache key patterns** for optimization
4. **Update monitoring** thresholds if needed
5. **Consider Redis Cluster** for better availability
6. **Update cache warming** scripts
7. **Review eviction policy** effectiveness

## Useful Commands

```bash
# Redis CLI cheat sheet

# Get all info
INFO all

# Monitor real-time commands
MONITOR

# Get current config
CONFIG GET *

# Get key info
TYPE key
TTL key
OBJECT ENCODING key

# Memory analysis
MEMORY USAGE key
MEMORY STATS

# Client list
CLIENT LIST

# Check key distribution
redis-cli --bigkeys

# Memory analysis
redis-cli --memkeys

# Export/backup
redis-cli --rdb /tmp/dump.rdb

# Check replication
INFO replication
```

## Contact Information

- **DevOps On-Call**: Check PagerDuty
- **Redis Admin**: [Contact]
- **Slack**: #redis-alerts
- **Vendor Support**: Redis Labs (if using Redis Enterprise)
