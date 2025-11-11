# TreeBeard Monitoring & Alerting Setup

## Overview

TreeBeard implements comprehensive monitoring and alerting using industry-standard tools to ensure production reliability and performance.

## Monitoring Stack

### Application Performance Monitoring (APM)

**Primary Choice: DataDog**

Alternative options:
- New Relic
- Prometheus + Grafana with OpenTelemetry

**Features:**
- Distributed tracing across all API requests
- Performance monitoring (latency, throughput, errors)
- Resource utilization tracking (CPU, memory, network)
- Custom business metrics
- Real-time dashboards

### Error Tracking

**Tool: Sentry**

**Features:**
- Automatic exception capture and grouping
- User context (anonymized)
- Request context with full traces
- Performance monitoring
- PII sanitization
- Release tracking

### Alerting

**Tools:**
- **PagerDuty**: Critical alerts requiring immediate attention
- **Slack**: Warning and informational alerts
- **Email**: Daily/weekly digest reports

## Architecture

```
┌─────────────────┐
│   Application   │
│   (FastAPI)     │
└────────┬────────┘
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
┌─────────────────┐         ┌──────────────────┐
│   DataDog APM   │         │     Sentry       │
│  (Tracing &     │         │ (Error Tracking) │
│   Metrics)      │         └──────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│              Dashboards                      │
├──────────────┬──────────────┬───────────────┤
│Service Health│Infrastructure│App Performance│
└──────────────┴──────────────┴───────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│             Alert Rules                      │
├────────────┬──────────────┬─────────────────┤
│  Critical  │    High      │     Medium      │
└────────────┴──────────────┴─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         Notification Channels                │
├────────────┬──────────────┬─────────────────┤
│ PagerDuty  │    Slack     │     Email       │
└────────────┴──────────────┴─────────────────┘
```

## Installation & Setup

### 1. Install Dependencies

```bash
# Install monitoring packages
pip install ddtrace datadog sentry-sdk[fastapi]

# Or add to requirements.txt
cat >> requirements.txt <<EOF
ddtrace>=1.20.0
datadog>=0.47.0
sentry-sdk[fastapi]>=1.39.0
EOF

pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file with monitoring configuration:

```bash
# DataDog
DD_AGENT_HOST=localhost
DD_TRACE_AGENT_PORT=8126
DD_SERVICE=treebeard-api
DD_ENV=production
DD_VERSION=1.0.0
DD_LOGS_INJECTION=true
DD_TRACE_SAMPLE_RATE=1.0
DD_PROFILING_ENABLED=true

# Sentry
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=1.0

# PagerDuty
PAGERDUTY_INTEGRATION_KEY=your-integration-key
PAGERDUTY_ROUTING_KEY=your-routing-key

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Monitoring Configuration
APM_PROVIDER=datadog
METRICS_BACKEND=datadog
MONITORING_ENABLED=true
```

### 3. Initialize Monitoring in Application

Update `src/backend/api/main.py`:

```python
from backend.monitoring import init_apm, init_metrics, init_sentry

# Initialize monitoring
init_sentry(
    dsn=settings.sentry_dsn,
    environment=settings.environment
)

init_apm(provider=settings.apm_provider)
init_metrics(backend=settings.metrics_backend)
```

### 4. Add Monitoring Middleware

The application automatically includes monitoring middleware:

```python
# Already configured in main.py
- RequestIDMiddleware: Adds request ID to all requests
- LoggingMiddleware: Logs all requests with timing
- ErrorHandlerMiddleware: Captures and reports errors
```

### 5. DataDog Agent Setup

#### Local Development

```bash
# Docker
docker run -d \
  --name dd-agent \
  -e DD_API_KEY=${DD_API_KEY} \
  -e DD_SITE="datadoghq.com" \
  -e DD_APM_ENABLED=true \
  -e DD_APM_NON_LOCAL_TRAFFIC=true \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /proc/:/host/proc/:ro \
  -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
  -p 8125:8125/udp \
  -p 8126:8126/tcp \
  gcr.io/datadoghq/agent:7
```

#### Kubernetes

```bash
# Install DataDog Operator
helm repo add datadog https://helm.datadoghq.com
helm repo update

# Create values file
cat > datadog-values.yaml <<EOF
datadog:
  apiKey: ${DD_API_KEY}
  site: datadoghq.com
  logs:
    enabled: true
    containerCollectAll: true
  apm:
    enabled: true
    port: 8126
  processAgent:
    enabled: true
  systemProbe:
    enabled: true
  kubeStateMetricsCore:
    enabled: true

agents:
  image:
    tag: 7.49.0
EOF

# Install
helm install datadog-agent datadog/datadog \
  -n datadog \
  --create-namespace \
  -f datadog-values.yaml
```

### 6. Configure Dashboards

Import dashboard configurations from `/infrastructure/dashboards/`:

1. **Service Health Dashboard**: Overall API health metrics
2. **Infrastructure Dashboard**: System resources and database
3. **Application Performance Dashboard**: Recommendations and Claude API
4. **Business Metrics Dashboard**: User activity and KPIs

#### Import to DataDog

```bash
# Using DataDog API
for dashboard in infrastructure/dashboards/*.json; do
  curl -X POST "https://api.datadoghq.com/api/v1/dashboard" \
    -H "DD-API-KEY: ${DD_API_KEY}" \
    -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
    -H "Content-Type: application/json" \
    -d @${dashboard}
done
```

### 7. Configure Alerts

Alerts are defined in `/infrastructure/alerting-config.yml`.

#### Create Monitors in DataDog

```python
# Script to create monitors
# scripts/create_monitors.py

import yaml
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor

def create_monitors():
    with open('infrastructure/alerting-config.yml') as f:
        config = yaml.safe_load(f)

    configuration = Configuration()
    with ApiClient(configuration) as api_client:
        api_instance = MonitorsApi(api_client)

        for alert in config['alerts']:
            monitor = Monitor(
                name=alert['name'],
                type="metric alert",
                query=alert['query'],
                message=alert['description'],
                tags=alert.get('tags', []),
            )
            api_instance.create_monitor(body=monitor)
            print(f"Created monitor: {alert['name']}")

if __name__ == "__main__":
    create_monitors()
```

## Usage

### Adding Custom Metrics

```python
from backend.monitoring import get_metrics_collector

metrics = get_metrics_collector()

# Increment counter
metrics.increment('recommendations.generated', tags=['profile_type:high-usage'])

# Record timing
with metrics.timed('recommendation.duration'):
    result = await generate_recommendation(user_id)

# Set gauge
metrics.gauge('cache.hit_rate', hit_rate)

# Record histogram
metrics.histogram('api.request.size', request_size)
```

### Adding Distributed Tracing

```python
from backend.monitoring import trace_async_function, trace_database_query

# Trace function
@trace_async_function('recommendation.generate', service='recommendation-engine')
async def generate_recommendation(user_id: UUID):
    # Function implementation
    pass

# Trace database query
with trace_database_query('select_user', table='users'):
    user = await db.fetch_one(query)

# Trace external API
with trace_external_api('claude', '/v1/messages'):
    response = await claude_client.create_message(...)
```

### Error Capture

```python
from backend.monitoring.sentry_init import capture_exception, capture_message

try:
    result = await risky_operation()
except Exception as e:
    # Automatically captured by Sentry middleware
    # Or manually capture with additional context
    capture_exception(e, context={
        'user_id': user_id,
        'operation': 'generate_recommendation'
    })
    raise

# Capture informational message
capture_message("Important event occurred", level="info")
```

## Monitoring Best Practices

### 1. Metric Naming

Follow consistent naming conventions:

```
<namespace>.<component>.<metric_name>

Examples:
- treebeard.api.requests
- treebeard.database.query.duration
- treebeard.cache.hit_rate
- treebeard.recommendations.generated
```

### 2. Tagging Strategy

Use tags for filtering and grouping:

```python
tags = [
    f'endpoint:{endpoint_path}',
    f'method:{http_method}',
    f'status:{status_code}',
    f'environment:{environment}',
]
```

### 3. Alert Fatigue Prevention

- Set appropriate thresholds based on historical data
- Use evaluation windows to avoid flapping
- Implement alert grouping
- Regular review of alert effectiveness
- Auto-resolve when condition clears

### 4. Dashboard Organization

- **Executive Dashboard**: High-level KPIs
- **Service Dashboard**: API health and performance
- **Infrastructure Dashboard**: System resources
- **Application Dashboard**: Feature-specific metrics
- **Business Dashboard**: User activity and conversions

### 5. Incident Response

1. **Alert fires** → PagerDuty/Slack notification
2. **On-call engineer** → Acknowledges alert
3. **Consult runbook** → Follow investigation steps
4. **Mitigate issue** → Apply resolution steps
5. **Document actions** → Update incident log
6. **Post-mortem** → Review and improve

## Key Metrics

### Service Health

- **Uptime**: 99.9% target
- **Request Rate**: requests/second
- **Error Rate**: < 1% target
- **Latency P95**: < 2 seconds target

### Application Performance

- **Recommendation Generation**: < 3 seconds P95
- **Database Query Time**: < 100ms average
- **Cache Hit Rate**: > 80% target
- **Claude API Response**: < 5 seconds P95

### Infrastructure

- **CPU Usage**: < 70% average
- **Memory Usage**: < 80% average
- **Disk Usage**: < 80%
- **Network Throughput**: monitored for anomalies

### Business Metrics

- **Active Users**: daily/monthly count
- **Recommendations Generated**: per hour/day
- **Conversion Rate**: recommendation acceptance
- **User Satisfaction**: feedback scores

## Troubleshooting

### APM Not Working

```bash
# Check DataDog agent status
docker ps | grep dd-agent

# Check agent logs
docker logs dd-agent

# Verify APM configuration
ddtrace-run python -c "from ddtrace import tracer; print(tracer)"

# Check application logs
kubectl logs -n treebeard-production deployment/treebeard-api | grep -i datadog
```

### Metrics Not Appearing

```bash
# Check StatsD connectivity
echo -n "test.metric:1|c" | nc -u -w1 localhost 8125

# Check DataDog agent
curl http://localhost:8126/info

# Verify metrics in code
# Add debug logging to see if metrics are being sent
```

### Sentry Not Capturing Errors

```python
# Test Sentry connection
import sentry_sdk
sentry_sdk.init(dsn=settings.sentry_dsn)
sentry_sdk.capture_message("Test message")

# Check Sentry DSN
echo $SENTRY_DSN

# Verify initialization
# Check logs for Sentry init message
```

## Performance Impact

Monitoring overhead:
- **APM**: < 1% CPU overhead
- **Metrics**: < 0.5% CPU overhead
- **Logging**: < 2% CPU overhead
- **Total**: < 5% overhead

Network overhead:
- **Traces**: ~1-2KB per request
- **Metrics**: ~100 bytes per metric
- **Logs**: Variable, typically 1-5KB per log line

## Cost Considerations

### DataDog

- APM: ~$31/host/month
- Infrastructure: ~$15/host/month
- Logs: ~$0.10/GB ingested
- Custom Metrics: ~$0.05/metric/month

### Sentry

- Team Plan: $26/month for 50K events
- Business Plan: $80/month for 500K events
- Custom pricing for enterprise

### PagerDuty

- Professional: $41/user/month
- Business: $61/user/month

## Security

### PII Protection

Monitoring automatically sanitizes:
- Email addresses
- Phone numbers
- Credit card numbers
- API keys and tokens
- Passwords

### Data Retention

- **Traces**: 15 days
- **Metrics**: 15 months (rollups)
- **Logs**: 30 days
- **Errors**: 90 days

### Access Control

- Use RBAC for dashboard access
- Separate read-only and admin roles
- Audit logging for configuration changes
- API key rotation every 90 days

## Resources

- [DataDog APM Documentation](https://docs.datadoghq.com/tracing/)
- [Sentry Documentation](https://docs.sentry.io/)
- [PagerDuty Best Practices](https://www.pagerduty.com/resources/learn/best-practices/)
- [SRE Book](https://sre.google/sre-book/table-of-contents/)

## Support

- **Slack**: #monitoring, #alerts
- **On-Call**: Check PagerDuty
- **DevOps Team**: devops@treebeard.com
- **Documentation**: /docs/monitoring/
