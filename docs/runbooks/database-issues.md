# Runbook: Database Issues

**Alert**: Database connection failures or slow queries
**Severity**: Critical
**Response Time**: Immediate (< 5 minutes)

## Overview

This runbook covers database-related issues including connection failures, slow queries, and performance degradation.

## Common Alerts

- Database connection failures
- Slow database queries (>1 second)
- Connection pool exhaustion
- Database unavailable
- Replication lag (if applicable)

## Symptoms

- API returning 500 errors with database connection errors
- Timeouts on database queries
- Connection pool exhaustion warnings
- Elevated query latency
- Users unable to perform database operations

## Investigation Steps

### 1. Check Database Availability (1 minute)

```bash
# Test connection
psql -h $DB_HOST -U $DB_USER -d treebeard -c "SELECT 1;"

# Check if database is accepting connections
pg_isready -h $DB_HOST -p 5432

# Check database status (AWS RDS example)
aws rds describe-db-instances --db-instance-identifier treebeard-prod

# Check connection count from application
kubectl logs -n treebeard-production deployment/treebeard-api --tail=50 | grep -i "database\|connection"
```

### 2. Check Active Connections (2 minutes)

```sql
-- Total connections by state
SELECT state, count(*)
FROM pg_stat_activity
WHERE datname = 'treebeard'
GROUP BY state;

-- Connections by application
SELECT application_name, count(*), state
FROM pg_stat_activity
WHERE datname = 'treebeard'
GROUP BY application_name, state;

-- Check connection limit
SHOW max_connections;

-- Check current connection usage vs limit
SELECT count(*) as current_connections,
       (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections,
       round(count(*) * 100.0 / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections'), 2) as usage_percent
FROM pg_stat_activity;
```

### 3. Identify Slow Queries (2 minutes)

```sql
-- Active queries running > 2 seconds
SELECT pid,
       now() - pg_stat_activity.query_start AS duration,
       state,
       query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '2 seconds'
ORDER BY duration DESC;

-- Long-running transactions
SELECT pid,
       now() - xact_start AS transaction_duration,
       state,
       query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND state != 'idle'
  AND now() - xact_start > interval '5 seconds'
ORDER BY transaction_duration DESC;

-- Most expensive queries (requires pg_stat_statements)
SELECT substring(query, 1, 50) AS short_query,
       round(total_exec_time::numeric, 2) AS total_time,
       calls,
       round(mean_exec_time::numeric, 2) AS mean_time,
       round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) AS percentage
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### 4. Check for Locks (2 minutes)

```sql
-- Blocked queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_application
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- All locks
SELECT locktype, relation::regclass, mode, granted, pid
FROM pg_locks
WHERE NOT granted
ORDER BY pid;
```

### 5. Check Database Performance Metrics (2 minutes)

```sql
-- Table statistics
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size,
       seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Cache hit ratio (should be >99%)
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    round(sum(heap_blks_hit) * 100.0 / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2) as cache_hit_ratio
FROM pg_statio_user_tables;

-- Index usage
SELECT schemaname, tablename, indexname,
       idx_scan, idx_tup_read, idx_tup_fetch,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Resolution Steps

### Connection Failures

#### If Database is Down

```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier treebeard-prod

# If RDS, check for maintenance or automatic failover
# Check RDS events
aws rds describe-events --source-identifier treebeard-prod --duration 60

# If self-hosted, restart PostgreSQL
sudo systemctl restart postgresql
# or
kubectl rollout restart statefulset/postgres -n treebeard-production

# Verify connectivity after restart
psql -h $DB_HOST -U $DB_USER -d treebeard -c "SELECT version();"
```

#### If Connection Pool Exhausted

```bash
# Immediate: Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '10 minutes'
  AND datname = 'treebeard';

# Restart API pods to reset connection pools
kubectl rollout restart deployment/treebeard-api -n treebeard-production

# Increase connection pool size (config change)
# Update settings.py or environment variables:
# DATABASE_POOL_SIZE=20
# DATABASE_MAX_OVERFLOW=10

# Increase PostgreSQL max_connections if needed
# Edit postgresql.conf or RDS parameter group
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

### Slow Queries

#### Kill Long-Running Queries

```sql
-- Cancel query (gentle)
SELECT pg_cancel_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - pg_stat_activity.query_start > interval '30 seconds'
  AND query NOT LIKE '%pg_stat_activity%';

-- Terminate connection (forceful)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - pg_stat_activity.query_start > interval '1 minute'
  AND query NOT LIKE '%pg_stat_activity%';
```

#### Optimize Slow Queries

```sql
-- Analyze query plan
EXPLAIN ANALYZE
SELECT * FROM recommendations WHERE user_id = 'xxx';

-- If missing indexes, create them
CREATE INDEX CONCURRENTLY idx_recommendations_user_id
ON recommendations(user_id);

-- Update table statistics
ANALYZE recommendations;

-- Vacuum if needed
VACUUM ANALYZE recommendations;
```

### Lock Issues

#### Resolve Deadlocks

```sql
-- Kill blocking query
SELECT pg_terminate_backend(blocking_pid)
FROM (
    SELECT blocking_locks.pid AS blocking_pid
    FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_locks blocking_locks
        ON blocking_locks.locktype = blocked_locks.locktype
        AND blocking_locks.pid != blocked_locks.pid
    WHERE NOT blocked_locks.granted
) AS blocking_queries;

-- Or kill specific PID
SELECT pg_terminate_backend(12345);  -- Replace with actual PID
```

### Performance Degradation

#### Immediate Actions

```bash
# Vacuum analyze all tables
vacuumdb -z -d treebeard -h $DB_HOST -U $DB_USER

# Rebuild indexes if bloated
REINDEX TABLE recommendations;

# Update statistics
ANALYZE;

# Enable read replica for read-heavy operations
# Route SELECT queries to read replica endpoint
```

#### Scale Database Resources

```bash
# AWS RDS: Scale instance type
aws rds modify-db-instance \
    --db-instance-identifier treebeard-prod \
    --db-instance-class db.r6g.2xlarge \
    --apply-immediately

# Increase IOPS if I/O bound
aws rds modify-db-instance \
    --db-instance-identifier treebeard-prod \
    --iops 10000 \
    --apply-immediately

# Scale up read replicas
# Add additional read replica for load distribution
```

## Prevention

### Regular Maintenance

```sql
-- Schedule regular VACUUM
-- Add to cron or scheduled job
VACUUM ANALYZE;

-- Monitor table bloat
SELECT schemaname, tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    round((pg_total_relation_size(schemaname||'.'||tablename) -
           pg_relation_size(schemaname||'.'||tablename))::numeric /
           nullif(pg_total_relation_size(schemaname||'.'||tablename), 0) * 100, 2) AS bloat_ratio
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Index Optimization

```sql
-- Find missing indexes
SELECT schemaname, tablename, seq_scan, seq_tup_read,
       idx_scan, idx_tup_fetch,
       seq_tup_read / nullif(seq_scan, 0) AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 1000
  AND seq_tup_read / nullif(seq_scan, 0) > 10000
ORDER BY seq_tup_read DESC;

-- Remove unused indexes
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Connection Pool Configuration

```python
# Optimal settings for connection pool
DATABASE_POOL_SIZE = 5  # Per instance
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600  # Recycle connections every hour
DATABASE_POOL_PRE_PING = True  # Test connection before use
```

### Query Optimization Best Practices

1. **Use indexes wisely**
   - Index foreign keys
   - Index columns used in WHERE clauses
   - Use partial indexes for filtered queries

2. **Avoid N+1 queries**
   - Use eager loading with `selectinload()`
   - Batch queries when possible

3. **Use appropriate fetch strategies**
   - Don't SELECT * if you only need specific columns
   - Use pagination for large result sets

4. **Set timeouts**
   - Query timeout: 30 seconds
   - Connection timeout: 10 seconds

## Monitoring

### Key Metrics to Track

```
- Connection count (current / max)
- Connection pool usage
- Query latency (P50, P95, P99)
- Slow query count (>1s)
- Lock wait time
- Cache hit ratio
- Replication lag
- Disk usage
- IOPS utilization
```

### Alert Thresholds

```yaml
Critical:
  - Connection failures > 0
  - Connection usage > 90%
  - Query latency P95 > 1000ms
  - Replication lag > 10 seconds

Warning:
  - Connection usage > 75%
  - Query latency P95 > 500ms
  - Slow queries > 10/minute
  - Cache hit ratio < 95%
```

## Escalation

- **5 minutes**: If database is unreachable, escalate immediately
- **15 minutes**: If queries remain slow, escalate to database specialist
- **30 minutes**: Consider enabling read-only mode or maintenance page

## Useful Commands

```bash
# Check current database size
SELECT pg_size_pretty(pg_database_size('treebeard'));

# Check table sizes
\dt+

# Check index sizes
\di+

# Check active queries
\x
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Check database configuration
SHOW ALL;

# Check PostgreSQL version
SELECT version();

# Check for replication lag
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;
```

## Contact Information

- **Database Administrator**: [Contact]
- **DevOps On-Call**: Check PagerDuty
- **AWS Support**: [Phone/Email] (for RDS issues)
- **Slack**: #database-alerts
