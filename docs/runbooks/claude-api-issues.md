# Runbook: Claude API Issues

**Alert**: Claude API errors or rate limit exceeded
**Severity**: Critical (rate limit) / High (errors)
**Response Time**: < 5 minutes

## Overview

This runbook covers issues with the Claude API including rate limiting, errors, timeouts, and service degradation.

## Symptoms

- Claude API returning errors (4xx, 5xx)
- Rate limit exceeded (429 errors)
- Timeouts on Claude API calls
- Explanation generation failing
- Increased Claude API response time

## Impact

When Claude API is unavailable:
- Recommendations cannot include AI-generated explanations
- Users receive generic template explanations
- User experience degrades (less personalization)
- Potential reduction in recommendation acceptance

## Investigation Steps

### 1. Check Claude API Status (1 minute)

```bash
# Check Anthropic status page
curl https://status.anthropic.com/api/v2/status.json | jq

# Test Claude API directly
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Check application logs for Claude errors
kubectl logs -n treebeard-production deployment/treebeard-api --tail=100 | grep -i claude
```

### 2. Check Rate Limit Status (2 minutes)

```bash
# Check DataDog for Claude API metrics
# Query: sum:treebeard.external_api.calls{api:claude}.as_rate()
# Query: sum:treebeard.external_api.errors{api:claude,status:429}

# Check rate limit headers from recent requests
# Look in application logs for:
# - x-ratelimit-requests-limit
# - x-ratelimit-requests-remaining
# - x-ratelimit-requests-reset

# Calculate current usage rate
# calls_per_minute = recent_calls / time_window
```

### 3. Check Error Types (2 minutes)

```bash
# Check error breakdown in Sentry
# Look for:
# - 429: Rate limit exceeded
# - 400: Bad request (malformed input)
# - 401: Invalid API key
# - 500: Claude API internal error
# - Timeout errors

# Check error patterns
# DataDog: sum:treebeard.external_api.errors{api:claude} by {status}

# Review recent error traces
# Look at APM traces for failed Claude API calls
```

### 4. Check Claude API Performance (2 minutes)

```bash
# Check response times
# DataDog: p95:treebeard.external_api.duration{api:claude}

# Check timeout rate
# Calculate: timeouts / total_calls

# Check request sizes
# Large requests may be slow or hit limits

# Review prompt lengths
# Excessive token usage may cause rate limiting
```

## Resolution Steps

### Rate Limit Exceeded (429)

#### Immediate Actions

```python
# 1. Enable exponential backoff (should already be in code)
# Verify backoff is working:
# Check logs for retry attempts

# 2. Implement request queuing
# If hitting limits, queue non-urgent requests

# 3. Increase cache TTL for explanations
kubectl set env deployment/treebeard-api \
  EXPLANATION_CACHE_TTL=172800 \
  -n treebeard-production

# 4. Enable template fallback
kubectl set env deployment/treebeard-api \
  CLAUDE_FALLBACK_MODE=true \
  -n treebeard-production
```

#### Short-term Solutions

```python
# Reduce request rate
# 1. Batch multiple explanations into single request
# 2. Reduce explanation length (lower max_tokens)
# 3. Use cheaper model (claude-3-haiku)

# Update environment variables
kubectl set env deployment/treebeard-api \
  CLAUDE_MODEL=claude-3-haiku-20240307 \
  CLAUDE_MAX_TOKENS=500 \
  -n treebeard-production

# Enable smart caching
# Cache explanations by profile type, not individual user
```

#### Long-term Solutions

```bash
# 1. Request rate limit increase from Anthropic
# Contact: support@anthropic.com
# Provide: usage patterns, use case, expected growth

# 2. Implement multi-tier explanation system
# - Critical: Use Claude API
# - Normal: Use templates with Claude enhancement
# - Low: Use pure templates

# 3. Pre-generate common explanations
# Create explanation library for common scenarios

# 4. Use prompt caching (if available)
# Reuse common prompt components across requests
```

### API Errors (4xx/5xx)

#### Authentication Errors (401)

```bash
# Check API key validity
echo $CLAUDE_API_KEY

# Verify API key in Kubernetes secret
kubectl get secret claude-api-secret -n treebeard-production -o yaml

# Test API key
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-3-sonnet-20240229", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'

# If invalid, rotate API key
kubectl create secret generic claude-api-secret \
  --from-literal=api-key=$NEW_API_KEY \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment/treebeard-api -n treebeard-production
```

#### Bad Request Errors (400)

```bash
# Check request validation
# Review recent failed requests in logs

# Common issues:
# - Invalid message format
# - Exceeding context window
# - Invalid model name
# - Missing required fields

# Fix in code and redeploy
# Add request validation before sending to Claude

# Example validation:
# - Max message length: 100,000 tokens
# - Valid model names
# - Proper message structure
```

#### Server Errors (500)

```bash
# Check Anthropic status page
curl https://status.anthropic.com/api/v2/status.json

# If Claude is down, enable fallback mode
kubectl set env deployment/treebeard-api \
  CLAUDE_FALLBACK_MODE=true \
  -n treebeard-production

# Monitor for recovery
# Check status page every 5 minutes

# Once recovered, disable fallback
kubectl set env deployment/treebeard-api \
  CLAUDE_FALLBACK_MODE=false \
  -n treebeard-production
```

### Timeout Issues

```bash
# Check current timeout setting
# Should be 30-60 seconds for Claude API

# Increase timeout if needed
kubectl set env deployment/treebeard-api \
  CLAUDE_TIMEOUT=60000 \
  -n treebeard-production

# Check if specific prompts are slow
# Review slow requests in APM traces

# Optimize prompts:
# - Reduce max_tokens
# - Simplify instructions
# - Remove unnecessary context

# Enable streaming (if supported)
# Streaming can provide faster time-to-first-token
```

## Fallback Mode

When Claude API is unavailable, use template-based explanations:

```python
# Template-based explanation system
# src/backend/services/explanation_fallback.py

EXPLANATION_TEMPLATES = {
    "cost_savings": """
        This plan can save you ${savings} annually compared to your current plan.
        Based on your usage pattern of {usage_kwh} kWh/month, this {plan_type}
        plan offers the best value.
    """,

    "renewable_energy": """
        This plan provides {renewable_pct}% renewable energy, helping reduce
        your carbon footprint while maintaining reliable power.
    """,

    "flexibility": """
        This plan offers {contract_length}-month contract with ${etf} early
        termination fee, providing {flexibility_level} flexibility.
    """,
}

def generate_fallback_explanation(plan, user_profile):
    template = select_template(plan, user_profile)
    return template.format(
        savings=plan.projected_savings,
        usage_kwh=user_profile.avg_monthly_kwh,
        plan_type=plan.type,
        renewable_pct=plan.renewable_percentage,
        contract_length=plan.contract_length_months,
        etf=plan.early_termination_fee,
        flexibility_level=get_flexibility_level(plan),
    )
```

## Prevention

### Rate Limit Management

```python
# Implement rate limiting in application
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class RateLimiter:
    calls_per_minute: int = 50
    calls_per_hour: int = 2000

    def should_throttle(self) -> bool:
        # Check current usage against limits
        minute_calls = get_calls_last_minute()
        hour_calls = get_calls_last_hour()

        return (
            minute_calls >= self.calls_per_minute or
            hour_calls >= self.calls_per_hour
        )

    def get_wait_time(self) -> float:
        # Calculate how long to wait
        if minute_calls >= calls_per_minute:
            return 60.0
        elif hour_calls >= calls_per_hour:
            return 3600.0
        return 0.0
```

### Caching Strategy

```python
# Aggressive caching for Claude API responses
CACHE_STRATEGIES = {
    "user_specific": {
        "ttl": 86400,  # 24 hours
        "key": "explanation:{user_id}:{plan_id}"
    },
    "profile_based": {
        "ttl": 604800,  # 7 days
        "key": "explanation:{profile_type}:{plan_id}"
    },
    "plan_generic": {
        "ttl": 2592000,  # 30 days
        "key": "explanation:generic:{plan_id}"
    }
}
```

### Request Optimization

```python
# Optimize Claude API requests
OPTIMIZATION_STRATEGIES = {
    # Use cheaper models when appropriate
    "model_selection": {
        "complex": "claude-3-opus-20240229",
        "standard": "claude-3-sonnet-20240229",
        "simple": "claude-3-haiku-20240307"
    },

    # Reduce token usage
    "token_limits": {
        "max_prompt_tokens": 1000,
        "max_completion_tokens": 500
    },

    # Batch requests when possible
    "batching": {
        "enabled": True,
        "batch_size": 5,
        "wait_time": 1.0  # seconds
    }
}
```

### Monitoring

```yaml
# Claude API monitoring alerts
alerts:
  - name: claude_rate_limit
    query: "sum:treebeard.external_api.errors{api:claude,status:429}.as_count() > 0"
    severity: critical

  - name: claude_error_rate
    query: "sum:treebeard.external_api.errors{api:claude}.as_count() / sum:treebeard.external_api.calls{api:claude}.as_count() > 0.05"
    severity: high

  - name: claude_latency
    query: "p95:treebeard.external_api.duration{api:claude} > 10000"
    severity: medium

  - name: claude_usage_high
    query: "sum:treebeard.external_api.calls{api:claude}.as_rate() > 40"
    severity: warning
```

## Escalation

- **5 minutes**: If rate limited, enable fallback mode
- **15 minutes**: If persistent errors, escalate to engineering
- **30 minutes**: Contact Anthropic support if widespread issue

## Communication Template

```
⚠️ INCIDENT: Claude API Issues

Type: [Rate Limit / Errors / Timeout]
Status: [Investigating / Mitigating]
Started: [TIME]

Impact:
- Explanations using fallback templates
- User experience slightly degraded
- No functional impact on recommendations

Actions Taken:
- Enabled fallback mode
- Increased caching
- [Other actions]

Expected Resolution: [TIME]
```

## Post-Incident

1. **Review usage patterns** - Identify spike causes
2. **Optimize prompts** - Reduce token usage
3. **Improve caching** - Increase cache hit rate
4. **Request limit increase** - If needed from Anthropic
5. **Update fallback templates** - Improve quality
6. **Add circuit breaker** - Better failure handling

## Useful Monitoring Queries

```
# DataDog queries

# Call rate (per minute)
sum:treebeard.external_api.calls{api:claude}.as_rate()

# Error rate
sum:treebeard.external_api.errors{api:claude}.as_count() / sum:treebeard.external_api.calls{api:claude}.as_count()

# Response time (P95)
p95:treebeard.external_api.duration{api:claude}

# Rate limit errors
sum:treebeard.external_api.errors{api:claude,status:429}.as_count()

# Cost estimation (if tracking tokens)
sum:treebeard.claude.tokens.input{*} + sum:treebeard.claude.tokens.output{*}
```

## Contact Information

- **Anthropic Support**: support@anthropic.com
- **Engineering On-Call**: Check PagerDuty
- **Slack**: #claude-api-alerts
- **Status Page**: https://status.anthropic.com
