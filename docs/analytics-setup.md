# Analytics Setup Guide

## Overview

TreeBeard uses a comprehensive analytics system to track user behavior, system performance, and business metrics. This guide covers the setup and configuration of the analytics infrastructure.

## Architecture

### Components

1. **Frontend Analytics** (`src/frontend/src/utils/analytics.ts`)
   - Client-side event tracking
   - Google Analytics 4 (GA4) integration
   - Mixpanel integration
   - GDPR-compliant consent management

2. **Backend Analytics** (`src/backend/services/analytics_service.py`)
   - Server-side event tracking
   - API performance monitoring
   - Error tracking
   - Business metrics collection

3. **Analytics Middleware** (`src/backend/api/middleware/analytics.py`)
   - Automatic API request tracking
   - Performance timing
   - Error capture

4. **Dashboards** (`/dashboards/`)
   - User Engagement Dashboard
   - Conversion Metrics Dashboard
   - System Performance Dashboard
   - Business Intelligence Dashboard

## Frontend Analytics Setup

### 1. Initialize Analytics

Add analytics initialization to your app entry point:

```typescript
// src/frontend/src/main.tsx
import analytics from './utils/analytics';

// Initialize analytics
analytics.initialize({
  enabled: true,
  platform: 'ga4', // or 'mixpanel' or 'both'
  ga4MeasurementId: 'G-XXXXXXXXXX', // Your GA4 measurement ID
  mixpanelToken: 'YOUR_MIXPANEL_TOKEN', // Optional
  debug: process.env.NODE_ENV === 'development',
  anonymizeIp: true,
  cookieConsent: true,
});
```

### 2. Add Cookie Consent Banner

```typescript
// src/frontend/src/App.tsx
import CookieConsent from './components/CookieConsent';

function App() {
  return (
    <>
      <CookieConsent
        showSettings={true}
        onAccept={() => console.log('Analytics enabled')}
        onDecline={() => console.log('Analytics disabled')}
      />
      {/* Your app content */}
    </>
  );
}
```

### 3. Track Events

```typescript
import analytics from './utils/analytics';

// Track page views
analytics.trackPageView({
  page_path: '/onboarding',
  page_title: 'Onboarding',
});

// Track onboarding events
analytics.trackOnboardingStarted();
analytics.trackOnboardingStepCompleted(1, 'welcome', 30);

// Track file uploads
analytics.trackFileUploadAttempted('csv', 250, 'drag_drop');
analytics.trackFileUploadSucceeded('csv', 250);

// Track recommendations
analytics.trackRecommendationGenerated(3, 'budget_conscious', 1250);
analytics.trackPlanCardExpanded('plan-123', 'Green Energy Plus', 1);

// Set user properties (NO PII!)
analytics.setUserProperties({
  property_type: 'residential',
  zip_code: '77002',
  user_segment: 'budget_conscious',
});

// Identify user with anonymous ID
analytics.identifyUser('anon-user-12345');
```

### 4. Environment Variables

Create `.env` file:

```bash
# Frontend (.env)
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
VITE_MIXPANEL_TOKEN=your_mixpanel_token
VITE_ANALYTICS_ENABLED=true
VITE_ANALYTICS_DEBUG=false
```

## Backend Analytics Setup

### 1. Initialize Analytics Service

```python
# src/backend/api/main.py
from services.analytics_service import init_analytics, AnalyticsBackend

# Initialize analytics on startup
@app.on_event("startup")
async def startup_event():
    analytics = init_analytics(
        backend=AnalyticsBackend.MIXPANEL,  # or LOGGING, DATABASE
        mixpanel_token=settings.MIXPANEL_TOKEN,
        enabled=settings.ANALYTICS_ENABLED
    )
```

### 2. Add Analytics Middleware

```python
# src/backend/api/main.py
from api.middleware.analytics import AnalyticsMiddleware

# Add middleware
app.add_middleware(AnalyticsMiddleware)
```

### 3. Track Backend Events

```python
from services.analytics_service import get_analytics_service

analytics = get_analytics_service()

# Track API requests (automatic via middleware)
# No code needed - handled by AnalyticsMiddleware

# Track recommendation generation
await analytics.track_recommendation_generated(
    user_id=user.id,
    profile_type="budget_conscious",
    num_plans=3,
    duration_ms=1250,
    total_savings=245.50
)

# Track errors
await analytics.track_error(
    endpoint="/api/v1/recommendations",
    error_type="ValidationError",
    status_code=400,
    error_message="Invalid input data",
    user_id=user.id
)

# Track cache hits/misses
await analytics.track_cache_hit(
    cache_key="recommendations:user123",
    hit=True
)

# Track risk warnings
await analytics.track_risk_warning(
    risk_type="high_etf",
    severity="warning",
    user_id=user.id
)
```

### 4. Environment Variables

```bash
# Backend (.env)
ANALYTICS_ENABLED=true
ANALYTICS_BACKEND=mixpanel  # or logging, database
MIXPANEL_TOKEN=your_mixpanel_token
ANALYTICS_BATCH_SIZE=100
ANALYTICS_FLUSH_INTERVAL=60
```

## Google Analytics 4 (GA4) Setup

### 1. Create GA4 Property

1. Go to [Google Analytics](https://analytics.google.com/)
2. Create a new GA4 property
3. Get your Measurement ID (G-XXXXXXXXXX)

### 2. Configure Data Streams

1. Select "Web" platform
2. Enter your website URL
3. Enable enhanced measurement:
   - Page views
   - Scrolls
   - Outbound clicks
   - Site search
   - Form interactions
   - File downloads

### 3. Configure Data Retention

1. Go to Admin → Data Settings → Data Retention
2. Set to **90 days** (GDPR compliance)
3. Enable "Reset user data on new activity"

### 4. Enable IP Anonymization

IP anonymization is automatic in GA4.

### 5. Set Up Custom Events

GA4 will automatically track custom events sent via `gtag('event', ...)`.

No additional configuration needed - our analytics utility handles this.

## Mixpanel Setup

### 1. Create Mixpanel Project

1. Go to [Mixpanel](https://mixpanel.com/)
2. Create a new project
3. Get your Project Token

### 2. Configure Data Retention

1. Go to Project Settings → Data & Privacy
2. Set retention to **90 days**
3. Enable IP anonymization

### 3. Set Up User Profiles

User profiles are automatically created when calling `identify()`.

### 4. Install Mixpanel Library (Backend)

```bash
pip install mixpanel
```

## Database Setup for Analytics Events

### 1. Create Analytics Events Table

```sql
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    event VARCHAR(100) NOT NULL,
    user_id UUID,  -- Anonymized
    properties JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_analytics_events_event ON analytics_events(event);
CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_timestamp ON analytics_events(timestamp);
CREATE INDEX idx_analytics_events_properties ON analytics_events USING GIN(properties);

-- Partition by month for better performance
CREATE TABLE analytics_events_2025_01 PARTITION OF analytics_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
-- Repeat for each month...
```

### 2. Data Retention Policy

Set up automatic deletion of old data (90 days):

```sql
-- Delete events older than 90 days
DELETE FROM analytics_events
WHERE timestamp < NOW() - INTERVAL '90 days';
```

Or use a cron job:

```bash
# /etc/cron.daily/analytics-cleanup
#!/bin/bash
psql -U postgres -d treebeard -c "DELETE FROM analytics_events WHERE timestamp < NOW() - INTERVAL '90 days';"
```

## Grafana Dashboard Setup

### 1. Install Grafana

```bash
# Using Docker
docker run -d -p 3000:3000 --name=grafana grafana/grafana

# Or install natively
# See: https://grafana.com/docs/grafana/latest/setup-grafana/installation/
```

### 2. Add PostgreSQL Data Source

1. Go to Configuration → Data Sources
2. Add PostgreSQL
3. Configure connection:
   - Host: `localhost:5432`
   - Database: `treebeard`
   - User: `postgres`
   - Password: your password
   - SSL Mode: require

### 3. Import Dashboards

```bash
# Import dashboard JSON files
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/user_engagement.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/conversion_metrics.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/system_performance.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/business_intelligence.json
```

### 4. Configure Alerts

Set up alerts for critical metrics:

```yaml
# System Performance Alerts
- API P95 Response Time > 2000ms
- Error Rate > 1%
- Cache Hit Rate < 80%

# User Engagement Alerts
- Onboarding Completion Rate < 50%
- DAU drops by > 20%

# Business Alerts
- Zero recommendations in last hour
- High risk warning frequency (> 50%)
```

## GDPR Compliance

### Required Measures

1. **Cookie Consent**
   - ✅ Cookie consent banner implemented
   - ✅ Opt-in required before tracking
   - ✅ Easy opt-out mechanism

2. **Data Anonymization**
   - ✅ No PII collected
   - ✅ User IDs are hashed (SHA-256)
   - ✅ IP addresses anonymized

3. **Data Retention**
   - ✅ 90-day retention policy
   - ✅ Automatic deletion of old data

4. **User Rights**
   - ✅ Right to access (view their data)
   - ✅ Right to deletion (delete cookie consent)
   - ✅ Right to opt-out (decline cookies)

5. **Transparency**
   - ✅ Clear privacy policy
   - ✅ Explanation of what data is collected
   - ✅ Purpose of data collection stated

### Implementation Checklist

- [ ] Cookie consent banner displayed on first visit
- [ ] Analytics disabled until consent granted
- [ ] IP anonymization enabled in GA4
- [ ] User IDs hashed before sending to analytics
- [ ] No PII (email, name, address) sent to analytics
- [ ] 90-day data retention configured
- [ ] Privacy policy updated
- [ ] Cookie policy published
- [ ] Settings page for managing consent

## Testing Analytics

### Frontend Testing

```typescript
// Test analytics tracking
describe('Analytics', () => {
  it('should track page view', () => {
    analytics.trackPageView({
      page_path: '/test',
      page_title: 'Test Page',
    });

    expect(window.gtag).toHaveBeenCalledWith(
      'event',
      'page_view',
      expect.objectContaining({
        page_path: '/test',
      })
    );
  });
});
```

### Backend Testing

```python
# Test analytics service
async def test_track_recommendation():
    analytics = get_analytics_service()

    await analytics.track_recommendation_generated(
        user_id=UUID('12345678-1234-1234-1234-123456789012'),
        profile_type='test',
        num_plans=3,
        duration_ms=1000
    )

    # Verify event was tracked
    assert len(analytics.event_queue) == 1
    assert analytics.event_queue[0]['event'] == 'recommendation_generated'
```

### Debug Mode

Enable debug mode to see analytics events in console:

```typescript
// Frontend
analytics.initialize({
  debug: true,
  // ... other config
});

// Backend
analytics = init_analytics(
    backend=AnalyticsBackend.LOGGING,
    enabled=True
)
```

## Monitoring Analytics Health

### Key Metrics to Monitor

1. **Event Volume**
   - Events per minute/hour
   - Event type distribution
   - User coverage (% of users tracked)

2. **Data Quality**
   - Missing required properties
   - Invalid event names
   - Duplicate events

3. **Performance**
   - Analytics overhead on app performance
   - Event queue size
   - Flush frequency

### Health Check Query

```sql
-- Analytics health check
SELECT
    COUNT(*) as total_events,
    COUNT(DISTINCT event) as unique_events,
    COUNT(DISTINCT user_id) as unique_users,
    MIN(timestamp) as oldest_event,
    MAX(timestamp) as newest_event
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '1 hour';
```

## Troubleshooting

### Events Not Appearing in GA4

1. Check GA4 Measurement ID is correct
2. Verify gtag script is loaded
3. Check cookie consent is granted
4. Enable debug mode and check console
5. Use GA4 DebugView in GA4 console

### Events Not Appearing in Mixpanel

1. Check Mixpanel token is correct
2. Verify Mixpanel library is loaded
3. Check cookie consent is granted
4. Use Mixpanel Live View to debug

### High Analytics Overhead

1. Reduce event frequency
2. Increase batch size
3. Increase flush interval
4. Sample events (track only X% of users)

### Database Performance Issues

1. Add indexes on frequently queried columns
2. Partition table by month
3. Archive old data to separate table
4. Use materialized views for dashboards

## Resources

- [Google Analytics 4 Documentation](https://support.google.com/analytics/answer/10089681)
- [Mixpanel Documentation](https://developer.mixpanel.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [CCPA Compliance Guide](https://oag.ca.gov/privacy/ccpa)
