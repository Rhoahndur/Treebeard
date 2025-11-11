# Runbook: High Error Rate

**Alert**: API error rate exceeded threshold
**Severity**: Critical
**Response Time**: Immediate (< 5 minutes)

## Overview

This alert fires when the API error rate exceeds 5% (critical) or 2% (warning) for a sustained period.

## Symptoms

- Error rate dashboard shows elevated errors
- Users reporting 500 errors or timeouts
- PagerDuty/Slack alerts firing
- Increased error logs in monitoring

## Potential Causes

1. **Application Issues**
   - Code bugs or exceptions
   - Unhandled edge cases
   - Memory leaks causing crashes

2. **Infrastructure Issues**
   - Database connection failures
   - Redis cache unavailable
   - Network connectivity problems

3. **External Dependencies**
   - Claude API failures
   - Third-party service outages
   - Rate limiting on external APIs

4. **Resource Exhaustion**
   - Out of memory
   - CPU saturation
   - Connection pool exhaustion

## Investigation Steps

### 1. Check Service Health (2 minutes)

```bash
# Check if services are running
kubectl get pods -n treebeard-production
# or
systemctl status treebeard-api

# Check recent logs
kubectl logs -n treebeard-production deployment/treebeard-api --tail=100
# or
tail -f /var/log/treebeard/api.log
```

### 2. Identify Error Types (3 minutes)

```bash
# Check error breakdown in DataDog/monitoring
# Look for most common error types:
# - Database errors
# - External API errors
# - Validation errors
# - Authentication errors

# Query recent errors
# DataDog: sum:treebeard.api.errors{*} by {error_type}
```

### 3. Check Dependencies (2 minutes)

```bash
# Check database connectivity
psql -h $DB_HOST -U $DB_USER -d treebeard -c "SELECT 1;"

# Check Redis
redis-cli -h $REDIS_HOST ping

# Check external APIs
curl -I https://api.anthropic.com/v1/health
```

### 4. Review Recent Changes (3 minutes)

```bash
# Check recent deployments
kubectl rollout history deployment/treebeard-api -n treebeard-production

# Review recent commits
git log --oneline --since="1 hour ago"

# Check if there was a recent config change
```

### 5. Analyze Specific Errors (5 minutes)

```bash
# Look at error details in Sentry
# Check for:
# - Stack traces
# - Error frequency
# - Affected users
# - Request context

# Look for patterns:
# - Specific endpoints failing
# - Specific user actions causing errors
# - Time-based patterns
```

## Resolution Steps

### If Database Issues

```bash
# Check database connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'treebeard';

# Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

# Check slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '1 second';

# If connection pool exhausted, restart app or increase pool size
kubectl rollout restart deployment/treebeard-api -n treebeard-production
```

### If Redis/Cache Issues

```bash
# Check Redis memory
redis-cli -h $REDIS_HOST info memory

# Check Redis connections
redis-cli -h $REDIS_HOST info clients

# Clear cache if corrupted
redis-cli -h $REDIS_HOST FLUSHDB

# Restart Redis if needed
kubectl rollout restart statefulset/redis -n treebeard-production
```

### If External API Issues (Claude)

```bash
# Check Claude API status
curl https://status.anthropic.com/api/v2/status.json

# If rate limited, implement backoff or reduce calls
# Check current rate limit usage in monitoring

# If Claude is down, enable graceful degradation:
# - Return cached explanations
# - Use template-based explanations
# - Queue requests for later processing
```

### If Application Bug

```bash
# Rollback to previous version
kubectl rollout undo deployment/treebeard-api -n treebeard-production

# Or rollback to specific version
kubectl rollout undo deployment/treebeard-api --to-revision=<revision> -n treebeard-production

# Monitor error rate after rollback
# If errors decrease, the issue was in recent deployment
```

### If Resource Exhaustion

```bash
# Check resource usage
kubectl top pods -n treebeard-production

# Scale up replicas temporarily
kubectl scale deployment/treebeard-api --replicas=6 -n treebeard-production

# Restart pods to clear memory leaks
kubectl delete pod -l app=treebeard-api -n treebeard-production
```

## Mitigation Steps

1. **Immediate** (< 5 minutes)
   - Identify the root cause category
   - If recent deployment, consider rollback
   - Scale up resources if needed

2. **Short-term** (< 30 minutes)
   - Fix immediate issue (restart, scale, etc.)
   - Enable feature flags to disable problematic features
   - Route traffic away from failing instances

3. **Long-term** (< 24 hours)
   - Deploy proper fix
   - Add tests to prevent regression
   - Update monitoring/alerts if needed
   - Post-mortem analysis

## Prevention

- **Automated Testing**: Ensure comprehensive test coverage
- **Gradual Rollouts**: Use canary deployments
- **Circuit Breakers**: Implement circuit breakers for external APIs
- **Rate Limiting**: Proper rate limiting on endpoints
- **Monitoring**: Set up alerts for early warning signs
- **Capacity Planning**: Regular load testing

## Communication

### Internal

```
🚨 INCIDENT: High Error Rate

Status: Investigating
Severity: Critical
Started: [TIME]
Impact: [X]% of API requests failing

Current Actions:
- [Action 1]
- [Action 2]

Updates will be posted every 15 minutes.
```

### External (if user-facing)

```
We are currently experiencing elevated error rates on our API.
Our team is actively working to resolve the issue.
We will provide updates as we have more information.
```

## Escalation

- **15 minutes**: If no progress, escalate to senior engineer
- **30 minutes**: Escalate to engineering manager
- **1 hour**: Escalate to CTO/VP Engineering

## Post-Incident

1. Create incident report
2. Schedule post-mortem meeting
3. Document lessons learned
4. Create action items to prevent recurrence
5. Update runbook based on learnings

## Useful Links

- DataDog Dashboard: [Service Health Dashboard]
- Sentry: [Error Tracking]
- PagerDuty: [Incident Management]
- Slack: #alerts channel
- Status Page: status.treebeard.com

## Contact Information

- **On-Call Engineer**: Check PagerDuty
- **Engineering Manager**: [Contact]
- **DevOps Team**: #devops-alerts
