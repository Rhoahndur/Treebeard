# Runbook: High API Latency

**Alert**: API P95 latency exceeded threshold
**Severity**: Critical (>3s) / Warning (>2s)
**Response Time**: Immediate for critical, <15 minutes for warning

## Overview

This alert fires when the API P95 latency exceeds 3 seconds (critical) or 2 seconds (warning).

## Symptoms

- Slow API responses
- Users reporting timeouts
- Increased request duration in dashboards
- Elevated P95/P99 latency metrics

## Potential Causes

1. **Database Performance**
   - Slow queries
   - Missing indexes
   - Lock contention
   - Connection pool saturation

2. **External API Delays**
   - Claude API slow responses
   - Third-party service latency
   - Network issues

3. **Application Code**
   - N+1 queries
   - Inefficient algorithms
   - Blocking I/O operations
   - Memory pressure causing GC pauses

4. **Infrastructure**
   - High CPU usage
   - Memory exhaustion
   - Network congestion
   - Insufficient resources

5. **Cache Issues**
   - Low cache hit rate
   - Cache unavailable
   - Cache stampede

## Investigation Steps

### 1. Identify Slow Endpoints (2 minutes)

```bash
# Check latency by endpoint in DataDog
# Query: p95:treebeard.api.request.duration{*} by {endpoint}

# Look for:
# - Which endpoints are slowest?
# - Is it all endpoints or specific ones?
# - When did the slowdown start?
```

### 2. Check Database Performance (3 minutes)

```bash
# Check for slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       query, state
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '2 seconds'
ORDER BY duration DESC;

# Check for locks
SELECT
  blocked_locks.pid AS blocked_pid,
  blocked_activity.query AS blocked_query,
  blocking_locks.pid AS blocking_pid,
  blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
  ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
  AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
  AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

# Check connection pool usage
SELECT count(*) as connections, state
FROM pg_stat_activity
WHERE datname = 'treebeard'
GROUP BY state;

# Check cache hit ratio
SELECT
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit) as heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_ratio
FROM pg_statio_user_tables;
```

### 3. Check External API Performance (2 minutes)

```bash
# Check Claude API response times
# DataDog: p95:treebeard.external_api.duration{api:claude}

# Check if Claude API is slow
curl -w "@curl-format.txt" -o /dev/null -s https://api.anthropic.com/v1/health

# Create curl-format.txt:
# time_total: %{time_total}s\n
```

### 4. Check Application Performance (3 minutes)

```bash
# Check distributed traces for slow requests
# Look at APM traces in DataDog/New Relic
# Identify bottlenecks:
# - Database queries
# - External API calls
# - CPU-bound operations

# Check for N+1 queries in logs
# Look for repeated similar queries in trace

# Check for blocking operations
# Look for synchronous calls that should be async
```

### 5. Check Infrastructure Resources (2 minutes)

```bash
# Check CPU usage
kubectl top pods -n treebeard-production

# Check memory usage
kubectl describe pod <pod-name> -n treebeard-production | grep -A 5 "Limits"

# Check if pods are being throttled
kubectl get hpa -n treebeard-production

# Check network latency
ping -c 5 $DB_HOST
```

### 6. Check Cache Performance (2 minutes)

```bash
# Check cache hit rate
# DataDog: avg:treebeard.cache.hit_rate{*}

# Check Redis performance
redis-cli -h $REDIS_HOST --latency

# Check Redis memory
redis-cli -h $REDIS_HOST info memory

# Check slow Redis commands
redis-cli -h $REDIS_HOST slowlog get 10
```

## Resolution Steps

### If Database is Slow

```bash
# Kill long-running queries
SELECT pg_cancel_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - pg_stat_activity.query_start > interval '30 seconds';

# Add missing indexes (if identified)
# Example:
# CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

# Increase connection pool size (temporary)
# Update config: database_pool_size=20

# Enable read replicas for read queries
# Route SELECT queries to read replica

# Vacuum and analyze if needed
VACUUM ANALYZE;
```

### If External API is Slow

```bash
# Enable caching for Claude API responses
# Increase cache TTL temporarily

# Implement timeout and retry logic
# Default timeout should be < 5 seconds

# Enable circuit breaker
# If Claude API is consistently slow, fall back to templates

# Scale up workers to handle backlog
kubectl scale deployment/treebeard-api --replicas=8 -n treebeard-production
```

### If Application Code Issue

```bash
# Check for N+1 queries
# Add eager loading:
# query.options(selectinload(Model.relationship))

# Check for blocking I/O
# Convert to async operations

# Check for expensive computations
# Move to background jobs if possible

# Enable response caching
# Cache expensive recommendations
```

### If Infrastructure Resource Constrained

```bash
# Scale horizontally
kubectl scale deployment/treebeard-api --replicas=8 -n treebeard-production

# Scale vertically (increase resource limits)
kubectl set resources deployment/treebeard-api \
  --limits=cpu=2000m,memory=4Gi \
  --requests=cpu=1000m,memory=2Gi \
  -n treebeard-production

# Enable autoscaling
kubectl autoscale deployment/treebeard-api \
  --min=3 --max=10 --cpu-percent=70 \
  -n treebeard-production
```

### If Cache Issues

```bash
# Increase cache TTL for hot keys
# Recommendation cache: 24h -> 48h

# Implement cache warming
# Pre-populate cache with common queries

# Add cache stampede protection
# Use lock/queue to prevent thundering herd

# Scale Redis
# Add more Redis replicas or upgrade instance
```

## Quick Wins (Immediate Actions)

1. **Scale Up**: Add more API replicas
   ```bash
   kubectl scale deployment/treebeard-api --replicas=6 -n treebeard-production
   ```

2. **Increase Cache TTL**: Give more breathing room
   ```bash
   # Update cache TTL in config
   RECOMMENDATION_CACHE_TTL=172800  # 48 hours
   ```

3. **Enable Connection Pooling**: If not already enabled
   ```bash
   # Update database pool size
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=10
   ```

4. **Add Request Timeout**: Prevent runaway requests
   ```bash
   # Add timeout to external API calls
   CLAUDE_API_TIMEOUT=5000  # 5 seconds
   ```

## Prevention

- **Query Optimization**: Regular query performance reviews
- **Indexes**: Ensure proper indexing on all query paths
- **Caching Strategy**: Aggressive caching of expensive operations
- **Load Testing**: Regular load tests to identify bottlenecks
- **APM Monitoring**: Distributed tracing for all requests
- **Auto-scaling**: Configure HPA for automatic scaling
- **Circuit Breakers**: Implement for all external dependencies

## Performance Targets

- **P50 Latency**: < 500ms
- **P95 Latency**: < 2000ms
- **P99 Latency**: < 3000ms
- **Database Queries**: < 100ms average
- **Cache Hit Rate**: > 80%
- **External API Calls**: < 2000ms

## Escalation

- **15 minutes**: If no improvement, escalate to senior engineer
- **30 minutes**: Escalate to engineering manager
- **1 hour**: Consider scaling incident

## Communication Template

```
🐌 INCIDENT: High API Latency

Status: Investigating
Severity: [Critical/Warning]
Impact: API response times elevated to [X]ms (P95)

Affected Endpoints:
- [Endpoint 1]
- [Endpoint 2]

Current Actions:
- [Action 1]
- [Action 2]

Expected Resolution: [TIME]
```

## Post-Incident Actions

1. Review APM traces for slowest transactions
2. Identify optimization opportunities
3. Add indexes or optimize queries
4. Update caching strategy
5. Adjust resource allocation
6. Update alert thresholds if needed

## Useful Queries

### DataDog Queries

```
# Latency by endpoint
p95:treebeard.api.request.duration{*} by {endpoint}

# Database query performance
p95:treebeard.database.query.duration{*} by {table}

# External API latency
p95:treebeard.external_api.duration{*} by {api}

# Cache hit rate
avg:treebeard.cache.hit_rate{*}
```

### SQL Queries

```sql
-- Slowest queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Table bloat
SELECT schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Useful Links

- APM Dashboard: [Application Performance]
- Database Dashboard: [Database Performance]
- Trace Explorer: [Distributed Traces]
- Slack: #performance channel
