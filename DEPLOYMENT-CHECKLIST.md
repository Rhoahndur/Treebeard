# TreeBeard API - Production Deployment Checklist

**Epic:** 3 - API Layer
**Version:** 1.0.0
**Date:** November 10, 2025

---

## Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] **Database Setup**
  - [ ] PostgreSQL 15+ installed and running
  - [ ] Database created: `treebeard`
  - [ ] User created with appropriate permissions
  - [ ] Connection tested from application server
  - [ ] DATABASE_URL configured in environment

- [ ] **Redis Setup**
  - [ ] Redis 7+ installed and running
  - [ ] Redis accessible from application server
  - [ ] REDIS_URL configured in environment
  - [ ] Memory limits configured appropriately
  - [ ] Persistence enabled (optional but recommended)

- [ ] **Environment Variables**
  - [ ] DATABASE_URL (production database)
  - [ ] REDIS_URL (production Redis)
  - [ ] SECRET_KEY (strong random key, min 32 chars)
  - [ ] CLAUDE_API_KEY (valid API key)
  - [ ] ENVIRONMENT=production
  - [ ] LOG_LEVEL=INFO
  - [ ] DEBUG=false
  - [ ] CORS_ORIGINS (production frontend URL)
  - [ ] JWT_EXPIRATION_MINUTES=1440

- [ ] **External Services**
  - [ ] Claude API key validated
  - [ ] Claude API accessible from production server
  - [ ] API rate limits understood

---

### 2. Database Migrations

- [ ] **Run Migrations**
  ```bash
  alembic upgrade head
  ```

- [ ] **Verify Tables Created**
  - [ ] users
  - [ ] user_preferences
  - [ ] current_plans
  - [ ] usage_history
  - [ ] plan_catalog
  - [ ] suppliers
  - [ ] recommendations
  - [ ] feedback

- [ ] **Seed Data**
  - [ ] Load plan catalog data
  - [ ] Load supplier data
  - [ ] Create admin user (if needed)

---

### 3. Application Testing

- [ ] **Unit Tests**
  ```bash
  pytest tests/api/test_routes.py -v
  ```

- [ ] **Integration Tests**
  ```bash
  pytest tests/integration/test_api_flow.py -v
  ```

- [ ] **Manual Testing**
  - [ ] Health check: `GET /health`
  - [ ] User registration: `POST /api/v1/auth/register`
  - [ ] User login: `POST /api/v1/auth/login`
  - [ ] Generate recommendations: `POST /api/v1/recommendations/generate`
  - [ ] All endpoints return expected responses

- [ ] **Load Testing**
  ```bash
  locust -f tests/load/locustfile.py --users 100 --spawn-rate 10
  ```

---

### 4. Security Review

- [ ] **Authentication**
  - [ ] JWT tokens working correctly
  - [ ] Password hashing verified (bcrypt)
  - [ ] Token expiration enforced
  - [ ] Refresh tokens working

- [ ] **Authorization**
  - [ ] RBAC working (user vs admin)
  - [ ] Protected routes require authentication
  - [ ] Users can only access their own data
  - [ ] Admin-only endpoints restricted

- [ ] **Rate Limiting**
  - [ ] Rate limits enforced
  - [ ] 429 responses working
  - [ ] Rate limit headers present
  - [ ] Redis storing rate limit data

- [ ] **Input Validation**
  - [ ] All endpoints validate input
  - [ ] SQL injection prevented (ORM)
  - [ ] XSS prevented (JSON responses)
  - [ ] CORS configured correctly

- [ ] **Secrets Management**
  - [ ] SECRET_KEY is strong and secret
  - [ ] CLAUDE_API_KEY not exposed
  - [ ] Database credentials secured
  - [ ] No secrets in code or logs

---

### 5. Performance Optimization

- [ ] **Caching**
  - [ ] Redis caching working
  - [ ] Cache hit rate >60%
  - [ ] Cache headers present
  - [ ] TTLs configured appropriately

- [ ] **Database**
  - [ ] Indexes created on frequently queried columns
  - [ ] Connection pool configured
  - [ ] Query performance optimized
  - [ ] Database vacuuming scheduled (PostgreSQL)

- [ ] **Response Times**
  - [ ] API response time <2s (P95)
  - [ ] Health check <100ms
  - [ ] Recommendation generation <2s

---

### 6. Monitoring & Logging

- [ ] **Logging**
  - [ ] Structured JSON logging enabled
  - [ ] Log level set to INFO
  - [ ] Request IDs in all logs
  - [ ] Error logs include stack traces
  - [ ] Logs forwarded to centralized system (optional)

- [ ] **Health Checks**
  - [ ] `/health` endpoint returns correct status
  - [ ] Database check working
  - [ ] Redis check working
  - [ ] Kubernetes probes configured:
    - [ ] Liveness: `/health/live`
    - [ ] Readiness: `/health/ready`

- [ ] **Metrics** (if using APM)
  - [ ] DataDog/New Relic integrated
  - [ ] Custom metrics configured
  - [ ] Error tracking enabled (Sentry)
  - [ ] Performance dashboards created

- [ ] **Alerts**
  - [ ] High error rate alerts
  - [ ] Slow response time alerts
  - [ ] Database connection alerts
  - [ ] Redis connection alerts
  - [ ] Rate limit threshold alerts

---

### 7. Documentation

- [ ] **API Documentation**
  - [ ] Swagger UI accessible at `/docs`
  - [ ] ReDoc accessible at `/redoc`
  - [ ] OpenAPI spec at `/openapi.json`
  - [ ] All endpoints documented
  - [ ] Examples provided

- [ ] **Developer Documentation**
  - [ ] README.md complete
  - [ ] Contract documents in `/docs/contracts/`
  - [ ] Architecture diagrams available
  - [ ] Deployment guide available

- [ ] **User Documentation**
  - [ ] API usage guide
  - [ ] Authentication flow documented
  - [ ] Error handling guide
  - [ ] Rate limiting explained

---

### 8. Infrastructure Setup

- [ ] **Web Server**
  - [ ] Uvicorn configured with workers
  - [ ] Number of workers: CPU count * 2 + 1
  - [ ] Timeout configured appropriately
  - [ ] Process manager (systemd/supervisor)

- [ ] **Reverse Proxy** (nginx/ALB)
  - [ ] HTTPS enabled
  - [ ] TLS 1.3 configured
  - [ ] SSL certificate valid
  - [ ] Request timeout configured
  - [ ] Static file serving (if needed)
  - [ ] Load balancing (if multi-instance)

- [ ] **Container/Kubernetes** (if applicable)
  - [ ] Docker image built
  - [ ] Container runs successfully
  - [ ] Resource limits configured
  - [ ] Health checks configured
  - [ ] Horizontal pod autoscaling configured
  - [ ] Persistent volumes for logs

---

### 9. Backup & Recovery

- [ ] **Database Backups**
  - [ ] Automated daily backups configured
  - [ ] Backup retention policy defined
  - [ ] Backup restoration tested
  - [ ] Point-in-time recovery available

- [ ] **Redis Backups**
  - [ ] RDB or AOF persistence enabled
  - [ ] Backup schedule defined
  - [ ] Recovery procedure tested

- [ ] **Disaster Recovery**
  - [ ] DR plan documented
  - [ ] Failover procedure tested
  - [ ] RTO and RPO defined
  - [ ] Multi-region setup (if required)

---

### 10. Compliance & Legal

- [ ] **Data Privacy**
  - [ ] GDPR compliance reviewed
  - [ ] CCPA compliance reviewed
  - [ ] Data retention policies implemented
  - [ ] User consent mechanisms in place
  - [ ] Right to deletion implemented

- [ ] **Terms of Service**
  - [ ] ToS updated
  - [ ] Privacy policy updated
  - [ ] Disclaimers in place

- [ ] **Audit Logging**
  - [ ] User actions logged
  - [ ] Admin actions logged
  - [ ] Data access logged
  - [ ] Logs retained per policy

---

## Deployment Steps

### Step 1: Pre-Deployment Validation
```bash
# Run all tests
pytest tests/ -v

# Check environment
env | grep -E 'DATABASE_URL|REDIS_URL|SECRET_KEY|CLAUDE_API_KEY'

# Verify database connection
psql $DATABASE_URL -c "SELECT 1"

# Verify Redis connection
redis-cli -u $REDIS_URL ping
```

### Step 2: Database Migration
```bash
# Backup database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Run migrations
alembic upgrade head

# Verify migrations
alembic current
```

### Step 3: Application Deployment

**Option A: Direct Deployment**
```bash
# Install dependencies
pip install -r requirements.txt

# Start application
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Option B: Docker Deployment**
```bash
# Build image
docker build -t treebeard-api:1.0.0 .

# Run container
docker run -d \
  --name treebeard-api \
  -p 8000:8000 \
  --env-file .env \
  treebeard-api:1.0.0
```

**Option C: Kubernetes Deployment**
```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n treebeard
kubectl logs -f deployment/treebeard-api -n treebeard
```

### Step 4: Post-Deployment Validation
```bash
# Health check
curl https://api.treebeard.com/health

# Test authentication
curl -X POST https://api.treebeard.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test","zip_code":"78701"}'

# Test core endpoint (with token)
curl -X POST https://api.treebeard.com/api/v1/recommendations/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### Step 5: Monitoring Setup
```bash
# Check logs
tail -f /var/log/treebeard/api.log

# Monitor metrics
curl https://api.treebeard.com/metrics

# Verify alerts
# (Check DataDog/New Relic/PagerDuty)
```

---

## Post-Deployment Monitoring

### First 24 Hours

Monitor these metrics:
- [ ] Error rate <0.1%
- [ ] API response time <2s (P95)
- [ ] CPU usage <70%
- [ ] Memory usage <80%
- [ ] Database connections healthy
- [ ] Redis connections healthy
- [ ] Cache hit rate >60%
- [ ] No critical errors in logs

### First Week

- [ ] Review all error logs
- [ ] Analyze slow queries
- [ ] Check cache effectiveness
- [ ] Review rate limit hits
- [ ] Monitor user registrations
- [ ] Track recommendation generation
- [ ] Verify data accuracy

---

## Rollback Plan

If issues are detected:

### Immediate Rollback
```bash
# Stop current version
systemctl stop treebeard-api
# or
docker stop treebeard-api
# or
kubectl rollout undo deployment/treebeard-api -n treebeard

# Restore database (if needed)
psql $DATABASE_URL < backup_YYYYMMDD.sql

# Start previous version
systemctl start treebeard-api-previous
```

### Feature Flags
- Disable problematic features via environment variables
- Monitor and fix issues
- Re-enable features after validation

---

## Success Criteria

Deployment is successful when:

- [ ] All health checks passing
- [ ] API response time <2s (P95)
- [ ] Error rate <0.1%
- [ ] Cache hit rate >60%
- [ ] All endpoints functioning
- [ ] Authentication working
- [ ] Rate limiting working
- [ ] Caching working
- [ ] Monitoring operational
- [ ] No critical errors for 24 hours

---

## Support Contacts

**Development Team:**
- Backend Dev #5 (Epic 3 - API Layer)

**Infrastructure:**
- Database Admin
- DevOps Team

**External Services:**
- Claude API Support
- Cloud Provider Support

---

## Emergency Procedures

### API Down
1. Check health endpoint
2. Review logs for errors
3. Verify database connection
4. Verify Redis connection
5. Restart application if needed
6. Rollback if restart fails

### High Error Rate
1. Check error logs
2. Identify error patterns
3. Check database performance
4. Check external service status
5. Apply hotfix or rollback

### Performance Degradation
1. Check response times
2. Review slow query logs
3. Check cache hit rate
4. Check connection pools
5. Scale horizontally if needed

---

**Deployment Prepared By:** Backend Dev #5
**Epic:** 3 - API Layer
**Date:** November 10, 2025
**Status:** Ready for Production

All checks must be completed before deploying to production.
