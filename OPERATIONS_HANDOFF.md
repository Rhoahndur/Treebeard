# TreeBeard AI Energy Plan Recommendation Agent
## Operations Team Handoff Documentation

**Version**: 1.0
**Date**: November 10, 2025
**Document Owner**: Engineering Team
**Operations Team**: [To be assigned]

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Summary](#2-architecture-summary)
3. [Access & Credentials](#3-access--credentials)
4. [Daily Operations](#4-daily-operations)
5. [Monitoring & Alerting](#5-monitoring--alerting)
6. [Incident Response](#6-incident-response)
7. [Common Issues & Troubleshooting](#7-common-issues--troubleshooting)
8. [Maintenance Procedures](#8-maintenance-procedures)
9. [Scaling & Capacity Planning](#9-scaling--capacity-planning)
10. [Backup & Recovery](#10-backup--recovery)
11. [Change Management](#11-change-management)
12. [Contacts & Escalation](#12-contacts--escalation)

---

## 1. System Overview

### 1.1 What is TreeBeard?

TreeBeard is an AI-powered energy plan recommendation system that helps users find optimal electricity plans based on their usage patterns and preferences. The system analyzes historical usage data, scores available plans, calculates potential savings, and provides AI-generated explanations.

### 1.2 Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Backend API** | REST API for all business logic | Python, FastAPI, PostgreSQL, Redis |
| **Frontend Web App** | User-facing React application | React, TypeScript, Tailwind CSS |
| **Admin Dashboard** | Administrative interface | React, TypeScript (embedded in web app) |
| **Database** | Persistent data storage | PostgreSQL 15+ (RDS Multi-AZ) |
| **Cache** | Performance optimization | Redis 7+ (ElastiCache) |
| **AI Service** | Plan explanation generation | Anthropic Claude API |
| **CDN** | Static asset delivery | CloudFront |
| **Load Balancer** | Traffic distribution | Application Load Balancer (ALB) |

### 1.3 Critical Metrics

| Metric | Normal Range | Alert Threshold |
|--------|--------------|-----------------|
| **Uptime** | 99.9%+ | <99.5% |
| **API P95 Latency** | <2s | >5s |
| **Error Rate** | <0.5% | >2% |
| **Cache Hit Rate** | >80% | <50% |
| **Active Users** | Varies | Monitor trends |
| **Database Connections** | 10-15 avg | >18 (90% of pool) |

### 1.4 Service Level Objectives (SLOs)

- **Availability**: 99.9% uptime (allow ~43 minutes downtime/month)
- **Performance**: P95 recommendation generation <2s
- **Data Durability**: 99.999999999% (11 nines) - RDS multi-AZ + backups
- **Support Response**: Critical incidents <1 hour, non-critical <24 hours

---

## 2. Architecture Summary

### 2.1 High-Level Architecture

```
                                   ┌─────────────┐
                                   │  CloudFront │
                                   │     CDN     │
                                   └──────┬──────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
          ┌─────────▼──────────┐ ┌───────▼────────┐  ┌────────▼────────┐
          │   Static Assets    │ │   React SPA    │  │   Backend API   │
          │   (S3 + CF)        │ │  (S3 + CF)     │  │      (ALB)      │
          └────────────────────┘ └────────────────┘  └────────┬────────┘
                                                               │
                                           ┌───────────────────┼───────────────────┐
                                           │                   │                   │
                                  ┌────────▼────────┐ ┌────────▼────────┐ ┌───────▼───────┐
                                  │  Backend App    │ │   PostgreSQL    │ │     Redis     │
                                  │   Servers       │ │      RDS        │ │ ElastiCache   │
                                  │  (EC2/ECS)      │ │   (Multi-AZ)    │ │               │
                                  └─────────────────┘ └─────────────────┘ └───────────────┘
                                           │
                                  ┌────────▼────────┐
                                  │   Claude API    │
                                  │   (Anthropic)   │
                                  └─────────────────┘
```

### 2.2 Data Flow

**User Recommendation Request**:
1. User uploads usage data via frontend
2. Frontend sends POST /api/v1/recommendations/generate to backend
3. Backend analyzes usage patterns (UsageAnalysisService)
4. Backend scores and ranks plans (ScoringService, RecommendationEngine)
5. Backend calculates savings (SavingsCalculator)
6. Backend generates AI explanation (ExplanationService → Claude API)
7. Backend caches result in Redis
8. Backend returns recommendation to frontend
9. Frontend displays results to user

**Typical Response Time**: 1.5-2.5 seconds

### 2.3 Network Architecture

**VPC Configuration**:
- VPC CIDR: 10.0.0.0/16
- Public Subnets (2): 10.0.1.0/24, 10.0.2.0/24 (for ALB)
- Private Subnets (2): 10.0.10.0/24, 10.0.11.0/24 (for app servers, RDS, ElastiCache)
- NAT Gateway in each AZ for outbound internet from private subnets

**Security Groups**:
- `alb-sg`: Allow 80/443 from 0.0.0.0/0
- `app-sg`: Allow 8000 from ALB only
- `db-sg`: Allow 5432 from app servers only
- `cache-sg`: Allow 6379 from app servers only

---

## 3. Access & Credentials

### 3.1 AWS Console Access

**URL**: https://console.aws.amazon.com/
**Account ID**: [To be provided]
**IAM Users**: Operations team members should have individual IAM users with MFA enabled

**Roles**:
- `TreeBeardOperator`: Read-only access to all resources + EC2 instance access
- `TreeBeardAdmin`: Full access (use with caution)

### 3.2 Application Access

**Production Admin Dashboard**:
- URL: https://treebeard.energy/admin
- Credentials stored in 1Password/LastPass vault: "TreeBeard Production Admin"
- Access restricted to authorized personnel only

**Monitoring Dashboards**:
- DataDog: https://app.datadoghq.com/dashboard/treebeard-prod
  - Credentials: SSO via Okta or individual API keys
- Sentry: https://sentry.io/organizations/treebeard/
  - Credentials: SSO via Okta

**PagerDuty**:
- URL: https://treebeard.pagerduty.com/
- Mobile app required for on-call engineers
- Credentials: Email login + MFA

### 3.3 Database Access

**PostgreSQL Production Database**:
- Endpoint: [RDS endpoint from AWS]
- Port: 5432
- Database: `treebeard_production`
- Username: Stored in AWS Secrets Manager: `prod/db/username`
- Password: Stored in AWS Secrets Manager: `prod/db/password`

**Connecting via psql**:
```bash
# From bastion host
psql -h <rds-endpoint> -U <username> -d treebeard_production
```

**⚠️ Important**:
- Never run DELETE or UPDATE queries without WHERE clause
- Always test queries on staging first
- Take manual backup before any data modifications
- No DDL changes (ALTER, DROP) without change management approval

### 3.4 Redis Access

**ElastiCache Cluster**:
- Endpoint: [ElastiCache endpoint from AWS]
- Port: 6379
- No authentication (protected by security group)

**Connecting via redis-cli**:
```bash
# From app server
redis-cli -h <elasticache-endpoint>
```

**Common Commands**:
```bash
# Check cache hit rate
INFO stats

# View keys (use with caution, blocks Redis)
KEYS *

# Flush cache (emergency only, causes temporary performance degradation)
FLUSHALL

# View memory usage
INFO memory
```

### 3.5 Secret Management

All secrets stored in **AWS Secrets Manager** with automatic rotation:
- `prod/db/credentials` - Database username/password
- `prod/redis/auth-token` - Redis auth token (if enabled)
- `prod/api/jwt-secret` - JWT signing secret
- `prod/api/claude-api-key` - Anthropic Claude API key
- `prod/monitoring/datadog-api-key` - DataDog API key
- `prod/monitoring/sentry-dsn` - Sentry DSN

**Accessing Secrets**:
```bash
aws secretsmanager get-secret-value --secret-id prod/db/credentials --query SecretString --output text
```

---

## 4. Daily Operations

### 4.1 Daily Health Checks (10 minutes)

**Recommended Time**: 9:00 AM local time, Monday-Friday

1. **Review Dashboard Metrics** (DataDog)
   - [ ] Overall system health: Green
   - [ ] Error rate: <0.5%
   - [ ] API latency P95: <2s
   - [ ] Cache hit rate: >80%
   - [ ] Database connections: <90% of pool

2. **Check for Alerts** (PagerDuty, Email)
   - [ ] Review any alerts from last 24 hours
   - [ ] Verify all resolved
   - [ ] If unresolved, follow incident response procedure

3. **Review Error Logs** (Sentry)
   - [ ] Check for new error patterns
   - [ ] Review top 5 errors by frequency
   - [ ] Create tickets for recurring issues

4. **Check Resource Utilization** (AWS CloudWatch)
   - [ ] EC2 CPU: <70%
   - [ ] EC2 Memory: <80%
   - [ ] RDS CPU: <70%
   - [ ] RDS Storage: <80%
   - [ ] ElastiCache memory: <80%

5. **Verify Backups** (AWS RDS Backups)
   - [ ] Last automated backup completed successfully
   - [ ] Backup size reasonable (check for anomalies)

**Actions if Issues Found**:
- Minor issues: Create ticket, monitor
- Moderate issues: Investigate immediately, escalate if needed
- Critical issues: Follow incident response procedure (Section 6)

### 4.2 Weekly Operations Tasks (30 minutes)

**Recommended Time**: Monday 10:00 AM

1. **Review Weekly Metrics**
   - [ ] User growth trend
   - [ ] Recommendation volume trend
   - [ ] Cost analysis (AWS bill to date)
   - [ ] Performance trends (latency, error rate)

2. **Capacity Planning Review**
   - [ ] Database storage growth rate
   - [ ] Projected time to reach 80% capacity
   - [ ] Request rate trend (are we approaching scaling thresholds?)

3. **Security Review**
   - [ ] Review failed login attempts
   - [ ] Check for unusual admin actions (via audit logs)
   - [ ] Verify SSL certificates >30 days to expiration

4. **Update Runbooks**
   - [ ] Add any new issues encountered to runbooks
   - [ ] Update contact information if changed

### 4.3 Monthly Operations Tasks (2 hours)

**Recommended Time**: First Monday of month, 10:00 AM

1. **Security Patch Review**
   - [ ] Review and apply OS patches (plan maintenance window)
   - [ ] Review and update application dependencies
   - [ ] Review security advisories for all components

2. **Cost Optimization Review**
   - [ ] Analyze AWS cost breakdown
   - [ ] Identify unused resources
   - [ ] Review Reserved Instance utilization
   - [ ] Review third-party service costs (Claude API, DataDog, etc.)

3. **Backup Testing**
   - [ ] Perform backup restoration drill (to staging environment)
   - [ ] Verify restoration time within RTO (4 hours)
   - [ ] Document any issues

4. **Disaster Recovery Drill**
   - [ ] Simulate failure scenario
   - [ ] Follow DR runbook
   - [ ] Measure recovery time
   - [ ] Update DR documentation based on findings

5. **Documentation Update**
   - [ ] Review and update this operations handoff document
   - [ ] Update runbooks with new lessons learned
   - [ ] Update contact information
   - [ ] Update architecture diagrams if changes made

---

## 5. Monitoring & Alerting

### 5.1 Monitoring Tools

**DataDog** (Primary APM):
- **URL**: https://app.datadoghq.com/dashboard/treebeard-prod
- **Key Dashboards**:
  1. **System Overview**: High-level metrics (uptime, requests, errors)
  2. **Application Performance**: API latency breakdown, endpoint performance
  3. **Infrastructure**: CPU, memory, disk, network
  4. **Business Metrics**: User signups, recommendations generated, revenue (if applicable)

**Sentry** (Error Tracking):
- **URL**: https://sentry.io/organizations/treebeard/
- **Projects**:
  - `treebeard-backend` (Python backend errors)
  - `treebeard-frontend` (React frontend errors)

**AWS CloudWatch** (Infrastructure Monitoring):
- **URL**: https://console.aws.amazon.com/cloudwatch/
- **Key Metrics**:
  - EC2 metrics (CPUUtilization, NetworkIn/Out)
  - RDS metrics (DatabaseConnections, ReadLatency, WriteLatency)
  - ALB metrics (RequestCount, TargetResponseTime, HTTPCode_Target_5XX_Count)
  - ElastiCache metrics (CurrConnections, CacheHits, CacheMisses)

### 5.2 Alert Severity Levels

**Critical** (PagerDuty, immediate response):
- System down or unavailable
- Error rate >5%
- Data loss or corruption
- Security breach detected

**Warning** (Email/Slack, response within 1 hour):
- Performance degradation (latency >5s)
- Error rate 2-5%
- Resource utilization >80%
- Cache hit rate <50%

**Info** (Email, response within 24 hours):
- Deployment completed
- Scaling event occurred
- SSL certificate renewal
- Backup completed

### 5.3 Key Alerts & Responses

| Alert | Trigger | Severity | Response |
|-------|---------|----------|----------|
| **Application Down** | Health check fails 3+ times | Critical | Check ALB target health, restart app servers, check logs |
| **High Error Rate** | >5% errors for 5 min | Critical | Check Sentry for error details, check recent deployments, consider rollback |
| **High Latency** | P95 >5s for 10 min | Warning | Check database slow queries, check Claude API latency, check cache hit rate |
| **Database Connection Pool Exhausted** | >90% of pool for 2 min | Critical | Check for connection leaks, restart app if needed, scale up connections |
| **Cache Cluster Down** | ElastiCache unavailable | Critical | Check AWS service health, failover to read replica if configured |
| **SSL Certificate Expiring** | <7 days to expiration | Warning | Renew certificate via ACM, verify auto-renewal configured |

### 5.4 Runbook Links

All runbooks located in `/docs/runbooks/`:

1. **High Error Rate**: `/docs/runbooks/high-error-rate.md`
2. **High Latency**: `/docs/runbooks/high-latency.md`
3. **Database Issues**: `/docs/runbooks/database-issues.md`
4. **Cache Failure**: `/docs/runbooks/cache-failure.md`
5. **Claude API Issues**: `/docs/runbooks/claude-api-issues.md`

---

## 6. Incident Response

### 6.1 Incident Response Procedure

**Step 1: Detection**
- Alert received via PagerDuty, monitoring dashboard, or user report

**Step 2: Acknowledgment** (within 5 minutes)
- Acknowledge incident in PagerDuty
- Post in #incidents Slack channel: "Incident detected: [brief description]"

**Step 3: Assessment** (within 10 minutes)
- Determine severity (Critical, High, Medium, Low)
- Determine impact (users affected, services impacted)
- Find relevant runbook

**Step 4: Communication** (within 15 minutes)
- Update #incidents channel with assessment
- If Critical/High, notify:
  - Engineering Manager
  - Product Manager
  - On-call engineer (if not already)
- Post status page update (if public-facing)

**Step 5: Mitigation** (as quickly as possible)
- Follow runbook procedures
- Engage additional help if needed
- Consider quick wins (e.g., scaling up resources, rollback)
- Document all actions in incident ticket

**Step 6: Resolution**
- Verify issue resolved
- Monitor for 30 minutes to ensure stability
- Update #incidents channel: "Incident resolved"
- Update PagerDuty: Mark as resolved
- Update status page (if applicable)

**Step 7: Post-Mortem** (within 3 business days)
- Schedule post-mortem meeting (1 hour)
- Document:
  - Timeline of events
  - Root cause analysis
  - What went well
  - What could be improved
  - Action items to prevent recurrence
- Share post-mortem with team
- Implement action items

### 6.2 Incident Severity Definitions

**Critical (SEV-1)**:
- Complete system outage
- Data loss or corruption
- Security breach
- Revenue impact >$10k/hour (if applicable)

**Response Time**: Immediate
**Escalation**: Immediately notify all stakeholders

**High (SEV-2)**:
- Significant performance degradation (>50% slower)
- Single critical component down (e.g., database read replica)
- High error rate (>5%)
- Major feature unavailable

**Response Time**: <1 hour
**Escalation**: Notify manager if not resolved in 1 hour

**Medium (SEV-3)**:
- Minor performance degradation
- Non-critical feature unavailable
- Moderate error rate (2-5%)

**Response Time**: <4 hours
**Escalation**: Notify manager if not resolved in 4 hours

**Low (SEV-4)**:
- Minor issues with workarounds
- Cosmetic bugs
- Low error rate (<2%)

**Response Time**: Next business day
**Escalation**: None unless becomes recurring

### 6.3 Communication Templates

**Incident Detected**:
```
🚨 INCIDENT DETECTED
Severity: [Critical/High/Medium/Low]
Service: [TreeBeard Backend API / Frontend / Database / etc.]
Impact: [X users affected / Y% requests failing / etc.]
Started: [Timestamp]
Status: Investigating

Updates will be posted every 15 minutes.
```

**Incident Update**:
```
UPDATE: [Brief description of progress]
Actions Taken: [What we've done so far]
Next Steps: [What we're doing next]
ETA to Resolution: [Best estimate]
```

**Incident Resolved**:
```
✅ INCIDENT RESOLVED
Duration: [X minutes/hours]
Root Cause: [Brief explanation]
Fix: [What was done to resolve]
Monitoring: [What we're watching to ensure stability]

Post-mortem will be conducted within 3 business days.
```

### 6.4 Escalation Path

**Level 1: On-Call Engineer**
- First responder
- Follows runbooks
- Resolves 80% of incidents

**Level 2: Engineering Manager**
- Escalated if L1 can't resolve in:
  - 15 minutes (Critical)
  - 1 hour (High)
  - 4 hours (Medium)
- Can authorize emergency changes

**Level 3: CTO / VP Engineering**
- Escalated for:
  - Multi-hour outages
  - Data loss/corruption
  - Security breaches
  - Regulatory issues

**External Support**:
- AWS Support (Business/Enterprise): 1-800-xxx-xxxx
- Anthropic Support: support@anthropic.com
- DataDog Support: support@datadoghq.com

---

## 7. Common Issues & Troubleshooting

### 7.1 High API Latency

**Symptoms**:
- API P95 latency >5s
- Users complaining of slow response

**Common Causes & Fixes**:

1. **Claude API Slow**
   - Check: DataDog APM → External Services → Claude API latency
   - Fix: Temporary, wait for API to recover. If prolonged (>30 min), consider enabling template fallback

2. **Database Slow Queries**
   - Check: AWS RDS Performance Insights → Top SQL
   - Fix: Identify slow query, check if index is missing, consider query optimization

3. **Cache Miss Rate High**
   - Check: Redis INFO stats → hit rate
   - Fix: Run cache warming script: `python scripts/warm_cache.py --mode full`

4. **High Traffic Spike**
   - Check: ALB metrics → RequestCount
   - Fix: Scale up backend servers (Auto Scaling will handle automatically if configured)

**Detailed Runbook**: `/docs/runbooks/high-latency.md`

### 7.2 High Error Rate

**Symptoms**:
- Error rate >2%
- Sentry showing many errors

**Common Causes & Fixes**:

1. **Recent Deployment Bug**
   - Check: Deployment time vs error spike time
   - Fix: Rollback deployment (see Section 7.7)

2. **Third-Party Service Down**
   - Check: Sentry errors mentioning Claude API, database, cache
   - Fix: Verify service status, implement circuit breaker or fallback

3. **Database Connection Pool Exhausted**
   - Check: AWS RDS → DatabaseConnections metric
   - Fix: Restart application servers to reset connections, investigate connection leaks

4. **Invalid User Input**
   - Check: Sentry error details
   - Fix: Improve input validation, add error handling

**Detailed Runbook**: `/docs/runbooks/high-error-rate.md`

### 7.3 Database Issues

**Symptoms**:
- Database errors in Sentry
- High database latency
- Connection timeouts

**Common Causes & Fixes**:

1. **Storage Almost Full**
   - Check: AWS RDS → FreeStorageSpace
   - Fix: Delete old data, expand storage size

2. **Connection Pool Exhausted**
   - Check: DatabaseConnections vs MaxConnections
   - Fix: Increase connection pool size, fix connection leaks

3. **Long-Running Queries**
   - Check: RDS Performance Insights → Top SQL
   - Fix: Kill query if needed (`SELECT pg_terminate_backend(pid)`), optimize query

4. **Replication Lag** (if using read replicas)
   - Check: AWS RDS → ReplicaLag
   - Fix: Reduce write load, scale up replica instance

**Detailed Runbook**: `/docs/runbooks/database-issues.md`

### 7.4 Cache Failure

**Symptoms**:
- Redis connection errors
- Cache hit rate 0%
- Latency spike

**Common Causes & Fixes**:

1. **ElastiCache Node Failure**
   - Check: AWS ElastiCache → Node health
   - Fix: Automatic failover if Multi-AZ, otherwise provision new node

2. **Memory Eviction High**
   - Check: Redis INFO memory → evicted_keys
   - Fix: Increase cache size or adjust TTL policies

3. **Network Issue**
   - Check: Security group rules, VPC network ACLs
   - Fix: Verify connectivity from app servers, check security group allows port 6379

**Detailed Runbook**: `/docs/runbooks/cache-failure.md`

### 7.5 Frontend Issues

**Symptoms**:
- Page not loading
- JavaScript errors
- Broken UI

**Common Causes & Fixes**:

1. **CDN Issue**
   - Check: CloudFront distribution status
   - Fix: Invalidate cache, verify origin (S3 bucket) is accessible

2. **API Connectivity**
   - Check: Browser console for API errors
   - Fix: Verify CORS configuration, check API endpoint availability

3. **Build Issue**
   - Check: Sentry for JavaScript errors
   - Fix: Rollback frontend deployment, rebuild with fixes

4. **Browser Caching Old Version**
   - Fix: Clear browser cache, verify cache-control headers correct

### 7.6 Admin Dashboard Issues

**Symptoms**:
- Admin can't log in
- Admin features not working
- Audit logs not recording

**Common Causes & Fixes**:

1. **Authentication Failure**
   - Check: JWT token validity, user `is_admin` flag in database
   - Fix: Verify user has admin role, check JWT secret matches

2. **RBAC Permission Denied**
   - Check: User role in database, API logs
   - Fix: Update user role to admin if needed

3. **Audit Log Not Recording**
   - Check: Database audit_logs table, backend logs
   - Fix: Verify audit middleware enabled, check for errors in audit service

### 7.7 Rollback Procedure

**When to Rollback**:
- Critical bugs in new deployment
- Performance regression >50%
- Data corruption detected
- Security vulnerability introduced

**Steps**:

1. **Identify Previous Stable Version**
   - Check deployment history in GitHub/CI-CD tool
   - Confirm version number (e.g., v1.2.3)

2. **Rollback Database** (if migrations were run):
   ```bash
   # SSH to bastion host
   ssh bastion.treebeard.energy

   # Connect to database
   psql -h <rds-endpoint> -U <username> -d treebeard_production

   # Check current migration
   SELECT * FROM alembic_version;

   # Rollback one migration
   alembic downgrade -1

   # Or rollback to specific version
   alembic downgrade <revision_id>
   ```

3. **Rollback Backend**:
   ```bash
   # If using ECS/Fargate
   aws ecs update-service --cluster treebeard-prod --service backend --task-definition treebeard-backend:42

   # If using Kubernetes
   kubectl set image deployment/backend backend=<account>.dkr.ecr.us-east-1.amazonaws.com/treebeard-backend:v1.2.3

   # If using EC2 directly
   # SSH to each server and pull previous Docker image
   docker pull <account>.dkr.ecr.us-east-1.amazonaws.com/treebeard-backend:v1.2.3
   docker stop treebeard-backend
   docker run -d --name treebeard-backend <image>
   ```

4. **Rollback Frontend**:
   ```bash
   # Re-upload previous build to S3
   aws s3 sync ./build-v1.2.3 s3://treebeard-production-frontend --delete

   # Invalidate CloudFront cache
   aws cloudfront create-invalidation --distribution-id <dist-id> --paths "/*"
   ```

5. **Verify Rollback**:
   - Check health endpoints: `curl https://api.treebeard.energy/api/v1/health`
   - Check error rate in Sentry (should decrease)
   - Run smoke tests
   - Monitor for 30 minutes

6. **Post-Rollback**:
   - Notify team in #incidents channel
   - Update incident ticket with rollback details
   - Schedule post-mortem to identify root cause

---

## 8. Maintenance Procedures

### 8.1 Scheduled Maintenance Windows

**Frequency**: Monthly (first Sunday of month, 2:00 AM - 6:00 AM local time)

**Maintenance Tasks**:
- OS security patches
- Application dependency updates
- Database maintenance (VACUUM, ANALYZE)
- SSL certificate renewal (if not auto-renewed)
- Backup restoration testing
- Performance optimization

**Communication**:
- Notify users 7 days in advance (email, status page)
- Post reminder 24 hours in advance
- Update status page during maintenance
- Send completion notification

### 8.2 Database Maintenance

**Weekly Tasks** (automated via cron):
```sql
-- Run VACUUM ANALYZE to reclaim space and update statistics
VACUUM ANALYZE;

-- Check for bloated tables
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

**Monthly Tasks**:
```sql
-- Reindex heavily used tables
REINDEX TABLE users;
REINDEX TABLE recommendations;
REINDEX TABLE usage_history;

-- Check for missing indexes (slow queries)
-- Review RDS Performance Insights → Top SQL
```

### 8.3 Cache Maintenance

**Weekly Tasks**:
```bash
# Connect to Redis
redis-cli -h <elasticache-endpoint>

# Check memory usage
INFO memory

# Check fragmentation ratio (should be < 1.5)
INFO stats | grep mem_fragmentation_ratio

# If fragmentation high, consider restart during low-traffic period
```

**Monthly Tasks**:
```bash
# Review cache keys pattern
KEYS * | head -100

# Check for keys without TTL (potential memory leak)
SCAN 0 MATCH * COUNT 100

# For each key without TTL
TTL <key>
# If TTL is -1 (no expiration), investigate and set TTL
```

### 8.4 Log Management

**Log Rotation**:
- Application logs rotated daily (retain 30 days)
- Access logs rotated daily (retain 90 days)
- Audit logs retained indefinitely (compliance requirement)

**Log Archival**:
- Logs older than retention period archived to S3 Glacier
- Archive retention: 7 years

**Log Review**:
- Weekly review of ERROR-level logs
- Monthly review of WARNING-level logs
- Quarterly security audit of access logs

### 8.5 SSL Certificate Management

**Monitoring**:
- AWS Certificate Manager auto-renewal enabled
- Alerts set for certificates expiring in <30 days

**Manual Renewal** (if needed):
1. Request new certificate in ACM
2. Validate via DNS (add CNAME record)
3. Attach new certificate to ALB
4. Attach new certificate to CloudFront
5. Verify HTTPS working
6. Delete old certificate (after 7 days)

---

## 9. Scaling & Capacity Planning

### 9.1 Auto-Scaling Configuration

**Backend Application Servers**:
- **Min Instances**: 2
- **Max Instances**: 10
- **Desired Capacity**: 2 (normal load)
- **Scale Out**: CPU >70% for 5 minutes → add 1 instance
- **Scale In**: CPU <30% for 10 minutes → remove 1 instance

**Monitoring Auto-Scaling Events**:
- Check CloudWatch Alarms: `backend-autoscale-high-cpu`, `backend-autoscale-low-cpu`
- Review Auto Scaling Group activity history in AWS Console

### 9.2 Manual Scaling Procedures

**Scale Up Backend** (emergency, high traffic):
```bash
# Increase desired capacity
aws autoscaling set-desired-capacity --auto-scaling-group-name treebeard-backend-asg --desired-capacity 5
```

**Scale Up Database** (requires downtime or read replica promotion):
```bash
# Via AWS Console:
# RDS → Modify → Instance Class → db.m5.large (example)
# Apply Immediately: Yes (if emergency)
# Downtime: ~5-10 minutes

# Monitor during scale-up:
# CloudWatch → RDS → CPUUtilization
```

**Scale Up Cache**:
```bash
# Via AWS Console:
# ElastiCache → Modify → Node Type → cache.m5.large (example)
# Apply Immediately: Yes (if emergency)
# Downtime: None (if Multi-AZ replication)
```

### 9.3 Capacity Thresholds

**When to Scale**:

| Resource | Metric | Threshold | Action |
|----------|--------|-----------|--------|
| **Backend Instances** | CPU | >70% sustained | Auto-scale adds instance |
| **Database** | CPU | >70% for 1 hour | Plan manual scale-up |
| **Database** | Storage | >80% | Expand storage |
| **Database** | Connections | >90% of max | Increase pool size or scale up |
| **Cache** | Memory | >80% | Scale up or optimize TTLs |
| **Cache** | Eviction Rate | >10% | Scale up memory |

### 9.4 Capacity Forecasting

**Monthly Review**:
- Plot user growth rate
- Plot recommendation volume growth rate
- Calculate projected capacity needs for next 3 months
- Plan scale-up if approaching limits

**Example Calculation**:
```
Current: 1,000 requests/day, 2 backend instances (500 req/day per instance)
Growth Rate: 20% per month
Projected (3 months): 1,000 * 1.2^3 = 1,728 requests/day

Capacity needed: 1,728 / 500 = 3.5 instances → Plan for 4 instances
Action: No immediate action, monitor. Scale when reaching 1,500 req/day.
```

---

## 10. Backup & Recovery

### 10.1 Backup Strategy

**Database Backups** (Automated via RDS):
- **Frequency**: Daily automated backups
- **Retention**: 7 days
- **Backup Window**: 3:00 AM - 4:00 AM (low traffic period)
- **Location**: Same region + cross-region replica (optional)

**Point-in-Time Recovery**:
- Enabled on RDS
- Can restore to any second within retention period

**Manual Backups** (before major changes):
```bash
# Create manual snapshot
aws rds create-db-snapshot --db-instance-identifier treebeard-prod --db-snapshot-identifier manual-backup-2025-11-10
```

**Application Backups**:
- Code: Git repository (GitHub provides backups)
- Configuration: Stored in version control
- Secrets: AWS Secrets Manager (encrypted, versioned)
- Logs: Archived to S3 (versioned, encrypted)

### 10.2 Recovery Procedures

**Scenario 1: Accidental Data Deletion**

**Recovery Steps**:
1. Determine exact time of deletion
2. Create new RDS instance from point-in-time restore:
   ```bash
   aws rds restore-db-instance-to-point-in-time \
     --source-db-instance-identifier treebeard-prod \
     --target-db-instance-identifier treebeard-recovery \
     --restore-time 2025-11-10T14:30:00Z
   ```
3. Wait for restore to complete (~30 minutes for small DB)
4. Connect to restored database, export deleted data:
   ```sql
   COPY (SELECT * FROM users WHERE deleted_at >= '2025-11-10 14:00:00') TO '/tmp/recovered_users.csv' CSV HEADER;
   ```
5. Import data to production database
6. Verify data integrity
7. Delete recovery instance

**RTO**: ~2 hours
**RPO**: <1 hour (point-in-time recovery)

**Scenario 2: Complete Database Failure**

**Recovery Steps**:
1. If Multi-AZ: Automatic failover to standby (RTO: ~1 minute, RPO: 0)
2. If Single-AZ: Restore from latest automated backup:
   ```bash
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier treebeard-prod-new \
     --db-snapshot-identifier rds:treebeard-prod-2025-11-10-03-00
   ```
3. Update backend connection string to new endpoint
4. Restart backend application
5. Verify system operational

**RTO**: ~4 hours
**RPO**: <24 hours (last automated backup)

**Scenario 3: Complete Region Failure (Disaster Recovery)**

**Prerequisites**:
- Cross-region database replica in secondary region (e.g., us-west-2)
- CloudFront serves traffic (multi-region by default)
- Failover DNS configured (Route 53 health checks + failover routing)

**Recovery Steps**:
1. Promote read replica to master in secondary region
2. Update Route 53 DNS to point to secondary region ALB
3. Deploy backend application in secondary region (if not already running)
4. Monitor traffic failover (DNS TTL: 60 seconds)
5. Verify system operational in secondary region

**RTO**: ~1 hour
**RPO**: <5 minutes (replication lag)

### 10.3 Backup Testing

**Monthly Backup Restoration Drill**:
1. Restore latest backup to staging environment
2. Verify database integrity (`SELECT COUNT(*) FROM users;`)
3. Run application smoke tests against restored database
4. Measure restoration time
5. Document any issues
6. Update DR documentation

---

## 11. Change Management

### 11.1 Change Request Process

**Types of Changes**:
1. **Standard Change**: Pre-approved, low-risk (e.g., scaling up instances)
2. **Normal Change**: Requires approval (e.g., code deployment, configuration change)
3. **Emergency Change**: Critical fix, expedited approval (e.g., security patch, rollback)

**Normal Change Approval**:
- **Requester**: Engineer submits change request (Jira/ServiceNow)
- **Details**: Include description, risk assessment, rollback plan, testing evidence
- **Approval**: Engineering Manager or Change Advisory Board (CAB)
- **Timeline**: Submit 48 hours before planned change

**Emergency Change Approval**:
- **Verbal Approval**: Engineering Manager or CTO (can approve verbally)
- **Documentation**: Backfill change request ticket within 24 hours
- **Post-Mortem**: Required for all emergency changes

### 11.2 Deployment Process

**Pre-Deployment**:
- [ ] Code reviewed and approved
- [ ] Tests passing (unit, integration, E2E)
- [ ] Change request approved
- [ ] Deployment scheduled (low-traffic window if possible)
- [ ] Rollback plan prepared
- [ ] Stakeholders notified

**Deployment**:
- [ ] Run deployment via CI/CD pipeline or manual script
- [ ] Monitor deployment progress
- [ ] Run smoke tests
- [ ] Monitor error rates and latency for 30 minutes

**Post-Deployment**:
- [ ] Verify deployment successful
- [ ] Update change request ticket (status: Deployed)
- [ ] Notify stakeholders of completion
- [ ] Monitor for 24 hours for issues

**Rollback Criteria**:
- Error rate >5%
- P95 latency >2x baseline
- Critical functionality broken
- Security vulnerability introduced

### 11.3 Maintenance Window Schedule

**Regular Maintenance Windows**:
- **Frequency**: First Sunday of each month
- **Time**: 2:00 AM - 6:00 AM local time (low traffic)
- **Duration**: Up to 4 hours
- **Advance Notice**: 7 days

**Ad-Hoc Maintenance**:
- Scheduled based on urgency
- Minimum 48 hours notice (unless emergency)

---

## 12. Contacts & Escalation

### 12.1 Team Roster

**On-Call Rotation**:

| Week Starting | Primary On-Call | Secondary On-Call |
|---------------|-----------------|-------------------|
| Nov 10, 2025  | [Name] | [Name] |
| Nov 17, 2025  | [Name] | [Name] |
| Nov 24, 2025  | [Name] | [Name] |

**Update**: Rotation schedule maintained in PagerDuty

**Engineering Team**:

| Role | Name | Email | Phone | Availability |
|------|------|-------|-------|--------------|
| **Engineering Manager** | [Name] | [email] | [phone] | Business hours + escalations |
| **Senior Backend Engineer** | [Name] | [email] | [phone] | On-call rotation |
| **Senior Frontend Engineer** | [Name] | [email] | [phone] | Business hours |
| **DevOps Engineer** | [Name] | [email] | [phone] | On-call rotation |
| **CTO** | [Name] | [email] | [phone] | Critical escalations only |

**Product Team**:

| Role | Name | Email | Availability |
|------|------|-------|--------------|
| **Product Manager** | [Name] | [email] | Business hours |
| **Customer Support Lead** | [Name] | [email] | Business hours |

### 12.2 External Vendor Contacts

**AWS Support**:
- **Phone**: 1-800-xxx-xxxx (Business/Enterprise Support)
- **Support Level**: Business (response time: <12 hours)
- **Account Manager**: [Name, email, phone]

**Anthropic (Claude API)**:
- **Support Email**: support@anthropic.com
- **Documentation**: https://docs.anthropic.com/
- **Status Page**: https://status.anthropic.com/

**DataDog**:
- **Support Email**: support@datadoghq.com
- **Phone**: 1-866-329-4466
- **Documentation**: https://docs.datadoghq.com/

**Sentry**:
- **Support Email**: support@sentry.io
- **Documentation**: https://docs.sentry.io/

**PagerDuty**:
- **Support Email**: support@pagerduty.com
- **Phone**: 1-844-700-3889
- **Documentation**: https://support.pagerduty.com/

### 12.3 Escalation Matrix

**Level 1**: On-Call Engineer (First Responder)
- Responds to alerts
- Follows runbooks
- Resolves routine issues

**Escalate to Level 2 if**:
- Unable to resolve in 1 hour (Critical), 4 hours (High)
- Issue requires architecture/design decisions
- Issue requires emergency change approval

---

**Level 2**: Engineering Manager
- Provides technical guidance
- Approves emergency changes
- Coordinates multi-team response

**Escalate to Level 3 if**:
- Incident duration >2 hours
- Data loss or corruption
- Security breach
- Regulatory implications

---

**Level 3**: CTO / VP Engineering
- Executive decision-making
- External communication (customers, partners, regulators)
- Resource allocation (emergency contractor support, etc.)

---

**External Support**:
- Engaged in parallel with internal escalation for vendor-specific issues
- AWS Support for infrastructure issues
- Anthropic Support for Claude API issues

---

## Appendix

### A. Quick Reference Commands

**Check System Health**:
```bash
# API health
curl https://api.treebeard.energy/api/v1/health

# Database connection
psql -h <rds-endpoint> -U <user> -d treebeard_production -c "SELECT 1;"

# Cache connection
redis-cli -h <elasticache-endpoint> PING
```

**View Logs**:
```bash
# Backend application logs (if using EC2)
ssh <backend-server>
tail -f /var/log/treebeard/backend.log

# Backend logs (if using ECS/Fargate)
aws logs tail /ecs/treebeard-backend --follow

# Database logs
# AWS Console → RDS → Logs
```

**Database Quick Queries**:
```sql
-- Check user count
SELECT COUNT(*) FROM users;

-- Check recent recommendations
SELECT COUNT(*) FROM recommendations WHERE created_at > NOW() - INTERVAL '24 hours';

-- Check for errors in recent recommendations
SELECT id, error FROM recommendations WHERE error IS NOT NULL ORDER BY created_at DESC LIMIT 10;

-- Check database size
SELECT pg_size_pretty(pg_database_size('treebeard_production'));
```

### B. Key URLs

**Production**:
- **Frontend**: https://treebeard.energy
- **API**: https://api.treebeard.energy
- **Admin**: https://treebeard.energy/admin
- **API Docs**: https://api.treebeard.energy/docs

**Monitoring**:
- **DataDog**: https://app.datadoghq.com/dashboard/treebeard-prod
- **Sentry**: https://sentry.io/organizations/treebeard/
- **AWS Console**: https://console.aws.amazon.com/

**Documentation**:
- **GitHub Repo**: https://github.com/org/treebeard
- **Runbooks**: `/docs/runbooks/` (in repo)
- **API Docs**: https://api.treebeard.energy/docs

### C. Glossary

- **ALB**: Application Load Balancer (AWS service for distributing traffic)
- **APM**: Application Performance Monitoring (DataDog, New Relic)
- **CRUD**: Create, Read, Update, Delete
- **DR**: Disaster Recovery
- **ETL**: Extract, Transform, Load
- **JWT**: JSON Web Token (authentication method)
- **ORM**: Object-Relational Mapping (SQLAlchemy)
- **P95/P99**: 95th/99th percentile latency
- **PITR**: Point-In-Time Recovery (database restore capability)
- **RBAC**: Role-Based Access Control
- **RDS**: Relational Database Service (AWS managed PostgreSQL)
- **RPO**: Recovery Point Objective (acceptable data loss)
- **RTO**: Recovery Time Objective (acceptable downtime)
- **SLA**: Service Level Agreement
- **SLO**: Service Level Objective
- **TTL**: Time To Live (cache expiration)
- **VPC**: Virtual Private Cloud (AWS network isolation)

---

**Document Version**: 1.0
**Last Updated**: November 10, 2025
**Next Review**: December 10, 2025
**Document Owner**: Engineering Team
**Questions**: Contact Engineering Manager at [email]

