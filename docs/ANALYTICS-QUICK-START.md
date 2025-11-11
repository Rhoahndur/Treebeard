# Analytics Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Frontend Setup

#### 1. Initialize Analytics (1 minute)
```typescript
// src/frontend/src/main.tsx
import analytics from './utils/analytics';

analytics.initialize({
  enabled: true,
  platform: 'ga4',
  ga4MeasurementId: 'G-XXXXXXXXXX',
  cookieConsent: true,
  debug: import.meta.env.DEV,
});
```

#### 2. Add Cookie Consent (1 minute)
```typescript
// src/frontend/src/App.tsx
import CookieConsent from './components/CookieConsent';

function App() {
  return (
    <>
      <CookieConsent showSettings={true} />
      {/* Your app */}
    </>
  );
}
```

#### 3. Track Events (2 minutes)
```typescript
// In your components
import analytics from './utils/analytics';

// Page views (automatic with router)
analytics.trackPageView({
  page_path: location.pathname,
  page_title: document.title,
});

// Onboarding
analytics.trackOnboardingStarted();
analytics.trackOnboardingStepCompleted(1, 'welcome', 30);

// Recommendations
analytics.trackRecommendationGenerated(3, 'budget_conscious', 1250);
analytics.trackPlanCardExpanded('plan-123', 'Green Energy Plus', 1);
```

#### 4. Set Environment Variables (1 minute)
```bash
# .env
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
VITE_ANALYTICS_ENABLED=true
```

---

### Backend Setup

#### 1. Initialize Service (1 minute)
```python
# src/backend/api/main.py
from services.analytics_service import init_analytics, AnalyticsBackend

@app.on_event("startup")
async def startup():
    init_analytics(
        backend=AnalyticsBackend.MIXPANEL,
        mixpanel_token=settings.MIXPANEL_TOKEN,
        enabled=True
    )
```

#### 2. Add Middleware (30 seconds)
```python
# src/backend/api/main.py
from api.middleware.analytics import AnalyticsMiddleware

app.add_middleware(AnalyticsMiddleware)
# Now all API requests are automatically tracked!
```

#### 3. Track Custom Events (2 minutes)
```python
# In your endpoints
from services.analytics_service import get_analytics_service

analytics = get_analytics_service()

await analytics.track_recommendation_generated(
    user_id=user.id,
    profile_type="budget_conscious",
    num_plans=3,
    duration_ms=1250,
    total_savings=245.50
)
```

#### 4. Set Environment Variables (30 seconds)
```bash
# .env
ANALYTICS_ENABLED=true
ANALYTICS_BACKEND=mixpanel
MIXPANEL_TOKEN=your_token
```

---

## 📊 View Dashboards

### Access Grafana
```bash
# Start Grafana
docker run -d -p 3000:3000 grafana/grafana

# Open browser
http://localhost:3000
# Login: admin / admin
```

### Import Dashboards
```bash
# Import each dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/user_engagement.json
```

---

## 🎯 Common Use Cases

### Track User Journey
```typescript
// 1. User starts onboarding
analytics.trackOnboardingStarted();

// 2. User completes each step
analytics.trackOnboardingStepCompleted(1, 'welcome', 25);
analytics.trackOnboardingStepCompleted(2, 'current_plan', 45);

// 3. User uploads file
analytics.trackFileUploadAttempted('csv', 250, 'drag_drop');
analytics.trackFileUploadSucceeded('csv', 250);

// 4. User completes onboarding
analytics.trackOnboardingCompleted(180);

// 5. User gets recommendations
analytics.trackRecommendationGenerated(3, 'budget_conscious', 1200);

// 6. User interacts with plans
analytics.trackPlanCardExpanded('plan-1', 'Green Energy', 1);
analytics.trackCostBreakdownViewed('plan-1');
analytics.trackPlanCardClicked('plan-1', 'Green Energy', 1);
```

### Track Performance
```python
# Automatic via middleware - no code needed!
# Or track specific operations:

async with PerformanceTimer("recommendation_generation", user_id):
    recommendations = await generate_recommendations()
```

### Handle Errors
```python
# Automatic via middleware
# Or track custom errors:

try:
    result = await risky_operation()
except Exception as e:
    await analytics.track_error(
        endpoint="/api/custom",
        error_type=type(e).__name__,
        status_code=500,
        error_message=str(e)
    )
    raise
```

---

## 🔍 Debugging

### Enable Debug Mode
```typescript
// Frontend
analytics.initialize({
  debug: true,
  // ...
});
// Now see all events in browser console
```

```python
# Backend
analytics = init_analytics(
    backend=AnalyticsBackend.LOGGING,  # Uses console logging
    enabled=True
)
```

### Verify Events in GA4
1. Go to GA4 Admin → DebugView
2. Enable debug mode in browser
3. Perform actions in app
4. See events in real-time

### Check Event Queue
```python
# In backend
analytics = get_analytics_service()
print(f"Queued events: {len(analytics.event_queue)}")
```

---

## ✅ Quick Checklist

### Frontend
- [ ] Analytics initialized in main.tsx
- [ ] Cookie consent banner added
- [ ] Page view tracking on route changes
- [ ] Onboarding events tracked
- [ ] File upload events tracked
- [ ] Recommendation events tracked
- [ ] Environment variables set

### Backend
- [ ] Analytics service initialized
- [ ] Middleware added to app
- [ ] Custom events tracked in endpoints
- [ ] Environment variables set
- [ ] Database table created

### Dashboards
- [ ] Grafana installed
- [ ] PostgreSQL data source configured
- [ ] Dashboards imported
- [ ] Alerts configured

### Compliance
- [ ] Cookie consent working
- [ ] No PII being tracked
- [ ] IP anonymization enabled
- [ ] 90-day retention configured

---

## 📚 Full Documentation

- **Setup Guide:** `/docs/analytics-setup.md`
- **Metrics Definitions:** `/docs/metrics-definitions.md`
- **Dashboard Guide:** `/docs/dashboard-guide.md`
- **Integration Examples:** `/docs/analytics-integration-examples.md`
- **SQL Queries:** `/sql/dashboard_queries.sql`

---

## 🆘 Need Help?

### Common Issues

**Events not showing in GA4?**
- Check GA4 Measurement ID is correct
- Verify cookie consent is granted
- Enable debug mode and check console
- Use GA4 DebugView

**Backend events not tracked?**
- Check analytics is initialized
- Verify environment variables
- Check event queue: `print(analytics.event_queue)`
- Enable logging backend for debugging

**Dashboard shows no data?**
- Verify PostgreSQL connection
- Check analytics_events table exists
- Run sample query in Grafana
- Check time range settings

---

## 💡 Pro Tips

1. **Use Debug Mode in Development**
   ```typescript
   debug: process.env.NODE_ENV === 'development'
   ```

2. **Debounce Frequent Events**
   ```typescript
   const trackChange = debounce((val) => analytics.track..., 1000);
   ```

3. **Never Send PII**
   ```typescript
   // ❌ BAD
   analytics.setUserProperties({ email: user.email });

   // ✅ GOOD
   analytics.setUserProperties({ property_type: 'residential' });
   ```

4. **Use Consistent Event Names**
   ```typescript
   // Use snake_case consistently
   analytics.trackEvent('button_clicked');
   analytics.trackEvent('form_submitted');
   ```

5. **Include Context**
   ```typescript
   analytics.trackEvent('button_clicked', {
     button_name: 'submit',
     page: '/onboarding',
     step: 2,
   });
   ```

---

## 🎉 You're Ready!

Analytics is now tracking user behavior, system performance, and business metrics. Check your dashboards to see insights in real-time!

**Next Steps:**
1. Review dashboards daily for anomalies
2. Set up alerts for critical metrics
3. Use insights to improve the product
4. Track your product success metrics (from PRD)

Happy analyzing! 📊
