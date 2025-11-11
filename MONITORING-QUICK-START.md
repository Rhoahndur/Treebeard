# TreeBeard Monitoring - Quick Start Guide

## Overview

This guide will get you up and running with TreeBeard's monitoring and alerting system in under 30 minutes.

## Prerequisites

- Python 3.10+
- Docker (for DataDog agent)
- Access to DataDog, Sentry, PagerDuty, and Slack accounts

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install ddtrace datadog sentry-sdk[fastapi] prometheus-client
```

### 2. Set Environment Variables

Create `.env` file:

```bash
# Monitoring
MONITORING_ENABLED=true
APM_PROVIDER=datadog
METRICS_BACKEND=datadog

# DataDog
DD_AGENT_HOST=localhost
DD_TRACE_AGENT_PORT=8126
DD_SERVICE=treebeard-api
DD_ENV=production
DD_VERSION=1.0.0

# Sentry
SENTRY_DSN=https://your-key@sentry.io/project
SENTRY_ENVIRONMENT=production

# Alerting
PAGERDUTY_INTEGRATION_KEY=your-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
```

### 3. Start DataDog Agent

```bash
docker run -d \
  --name dd-agent \
  -e DD_API_KEY=${DD_API_KEY} \
  -e DD_SITE="datadoghq.com" \
  -e DD_APM_ENABLED=true \
  -e DD_APM_NON_LOCAL_TRAFFIC=true \
  -p 8125:8125/udp \
  -p 8126:8126/tcp \
  gcr.io/datadoghq/agent:7
```

### 4. Start Application

```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

Monitoring will automatically initialize on startup!

## Verify Setup

### 1. Check Logs

```bash
# Look for initialization messages
tail -f logs/app.log | grep -i "monitoring\|sentry\|apm"
```

Expected output:
```
INFO - Sentry error tracking initialized
INFO - APM initialized with provider: datadog
INFO - Metrics initialized with backend: datadog
```

### 2. Check DataDog

Visit https://app.datadoghq.com/apm/traces
- You should see traces appearing within 1-2 minutes

### 3. Check Sentry

Visit https://sentry.io
- Errors will appear automatically when they occur

### 4. Test Metrics

```python
# Test custom metric
curl http://localhost:8000/api/v1/recommendations
# Check DataDog for "treebeard.api.requests" metric
```

## What's Monitored

### Automatically Tracked

- ✅ All API requests (latency, status, errors)
- ✅ Database queries (duration, errors)
- ✅ Cache operations (hits, misses)
- ✅ External API calls (Claude API)
- ✅ System resources (CPU, memory)
- ✅ All exceptions and errors

### Available Dashboards

1. **Service Health**: `/infrastructure/dashboards/service-health-dashboard.json`
2. **Infrastructure**: `/infrastructure/dashboards/infrastructure-dashboard.json`
3. **Application Performance**: `/infrastructure/dashboards/application-performance-dashboard.json`
4. **Business Metrics**: `/infrastructure/dashboards/business-metrics-dashboard.json`

### Alert Rules

- 8 Critical alerts (PagerDuty + Slack)
- 8 Warning alerts (Slack)
- 2 Info alerts (Email)

See `/infrastructure/alerting-config.yml` for details.

## Common Issues

### Issue: "No traces appearing in DataDog"

**Solution:**
```bash
# Check DataDog agent status
docker logs dd-agent

# Verify agent connectivity
curl http://localhost:8126/info
```

### Issue: "Sentry not capturing errors"

**Solution:**
```bash
# Test Sentry manually
python -c "import sentry_sdk; sentry_sdk.init('YOUR_DSN'); sentry_sdk.capture_message('test')"

# Check Sentry DSN
echo $SENTRY_DSN
```

### Issue: "Metrics not showing"

**Solution:**
```bash
# Test StatsD connectivity
echo -n "test.metric:1|c" | nc -u -w1 localhost 8125

# Check DataDog agent logs
docker logs dd-agent | grep -i statsd
```

## Next Steps

1. **Import Dashboards**
   ```bash
   # Import dashboard definitions to DataDog
   python scripts/import_dashboards.py
   ```

2. **Configure Alerts**
   ```bash
   # Create alert monitors
   python scripts/create_monitors.py
   ```

3. **Set Up On-Call Rotation**
   - Configure PagerDuty schedules
   - Set up escalation policies

4. **Review Runbooks**
   - Read `/docs/runbooks/` for incident response
   - Train team on procedures

## Resources

- **Full Setup Guide**: `/docs/monitoring-setup.md`
- **Incident Response**: `/docs/incident-response.md`
- **Runbooks**: `/docs/runbooks/`
- **Slack**: #monitoring, #alerts
- **Support**: devops@treebeard.com

## Quick Reference

### Add Custom Metric

```python
from backend.monitoring import get_metrics_collector

metrics = get_metrics_collector()
metrics.increment('my.custom.metric', tags=['tag:value'])
```

### Add Distributed Trace

```python
from backend.monitoring import trace_async_function

@trace_async_function('my.operation')
async def my_function():
    # Your code here
    pass
```

### Capture Error

```python
from backend.monitoring.sentry_init import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={'user_id': user_id})
```

## Support

- **Documentation**: `/docs/monitoring-setup.md`
- **Issues**: GitHub Issues
- **Slack**: #monitoring channel
- **Email**: devops@treebeard.com

---

**Ready to go!** Your monitoring is now active and tracking everything.
