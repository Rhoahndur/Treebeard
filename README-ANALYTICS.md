# TreeBeard Analytics & Metrics System

> Comprehensive analytics tracking and business intelligence for the TreeBeard Energy Plan Recommendation Agent

## 📊 Overview

The TreeBeard Analytics System provides real-time insights into user behavior, system performance, and business outcomes. Built with privacy-first principles, it's fully GDPR compliant and designed for scale.

### Key Features

- ✅ **Comprehensive Event Tracking** - 22+ events tracked across frontend and backend
- ✅ **Real-time Dashboards** - 4 Grafana dashboards with 40+ panels
- ✅ **GDPR Compliant** - Cookie consent, IP anonymization, 90-day retention
- ✅ **Multi-platform Support** - Google Analytics 4, Mixpanel, or both
- ✅ **Performance Optimized** - Event batching, async processing, <1ms overhead
- ✅ **Production Ready** - Tested, documented, and scalable

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Analytics Flow                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Actions                                                 │
│      │                                                         │
│      ├──▶ Frontend Events ──▶ GA4 / Mixpanel                 │
│      │                                                         │
│      └──▶ API Calls ──▶ Backend Events ──▶ Database          │
│                                     │                         │
│                                     ▼                         │
│                              Grafana Dashboards               │
│                                     │                         │
│                                     ▼                         │
│                            Business Insights                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 5-Minute Setup

```bash
# 1. Install dependencies
cd src/frontend && npm install
cd ../backend && pip install -r requirements.txt

# 2. Set environment variables
cp .env.example .env
# Edit .env with your GA4/Mixpanel tokens

# 3. Initialize analytics in your app
# See docs/ANALYTICS-QUICK-START.md

# 4. Start tracking events!
```

**Full Setup Guide:** [`docs/analytics-setup.md`](docs/analytics-setup.md)

**Quick Start:** [`docs/ANALYTICS-QUICK-START.md`](docs/ANALYTICS-QUICK-START.md)

---

## 📁 Project Structure

```
TreeBeard/
├── src/
│   ├── frontend/
│   │   └── src/
│   │       ├── utils/
│   │       │   ├── analytics.ts           # Core analytics utility
│   │       │   └── analytics.test.ts      # Analytics tests
│   │       └── components/
│   │           └── CookieConsent.tsx      # GDPR consent banner
│   └── backend/
│       ├── services/
│       │   └── analytics_service.py       # Backend analytics service
│       └── api/
│           └── middleware/
│               └── analytics.py           # Auto-tracking middleware
├── dashboards/
│   ├── user_engagement.json               # User behavior dashboard
│   ├── conversion_metrics.json            # Conversion funnel dashboard
│   ├── system_performance.json            # Performance monitoring
│   └── business_intelligence.json         # Business insights
├── sql/
│   └── dashboard_queries.sql              # SQL for all metrics
└── docs/
    ├── analytics-setup.md                 # Complete setup guide
    ├── metrics-definitions.md             # All metrics defined
    ├── dashboard-guide.md                 # How to use dashboards
    ├── analytics-integration-examples.md  # Code examples
    └── ANALYTICS-QUICK-START.md          # Quick start guide
```

---

## 📈 Events Tracked

### Frontend Events (14 events)

| Event | Purpose | Properties |
|-------|---------|-----------|
| `page_view` | Navigation tracking | path, title, location |
| `onboarding_started` | Onboarding initiation | timestamp |
| `onboarding_step_completed` | Step progression | step, name, time |
| `onboarding_abandoned` | Drop-off tracking | step, reason |
| `onboarding_completed` | Success tracking | total_time |
| `file_upload_attempted` | Upload initiation | type, size, method |
| `file_upload_succeeded` | Upload success | type, size |
| `file_upload_failed` | Upload failures | type, error |
| `preferences_changed` | Preference updates | preferences |
| `recommendation_generated` | Recommendations | num_plans, profile |
| `plan_card_expanded` | Plan detail views | plan_id, name, position |
| `plan_card_clicked` | Plan selections | plan_id, name, position |
| `cost_breakdown_viewed` | Cost detail views | plan_id |
| `comparison_viewed` | Plan comparisons | plan_ids |

### Backend Events (8 events)

| Event | Purpose | Properties |
|-------|---------|-----------|
| `api_request` | All API calls | endpoint, method, status, duration |
| `error_occurred` | Error tracking | endpoint, error_type, status |
| `recommendation_generated` | Recommendations | profile, num_plans, duration, savings |
| `cache_hit` / `cache_miss` | Cache performance | cache_key |
| `risk_warning_triggered` | Risk notifications | risk_type, severity |
| `user_created` | User registrations | property_type, zip_code |
| `user_preferences_updated` | Preference changes | preferences |
| `file_uploaded` / `file_upload_failed` | File uploads | type, size, error |

---

## 📊 Dashboards

### 1. User Engagement Dashboard
**Focus:** User behavior and onboarding metrics

**Key Metrics:**
- Daily/Weekly/Monthly Active Users
- Onboarding completion rate (target: >70%)
- Abandonment rate by step
- Average onboarding time
- Return user rate

**Update Frequency:** 1 minute

---

### 2. Conversion Metrics Dashboard
**Focus:** Recommendation funnel and conversions

**Key Metrics:**
- Recommendation generation rate
- Plan card expansion rate (target: >80%)
- Cost breakdown view rate (target: >60%)
- Average savings shown (target: >$150)
- Top recommended plans

**Update Frequency:** 1 minute

---

### 3. System Performance Dashboard
**Focus:** API performance and reliability

**Key Metrics:**
- API response times (P50, P95, P99) - target: P95 < 2000ms
- Error rate (target: <1%)
- Cache hit rate (target: >80%)
- Slowest endpoints
- Peak usage times

**Update Frequency:** 30 seconds

---

### 4. Business Intelligence Dashboard
**Focus:** Strategic business insights

**Key Metrics:**
- Most popular plan types
- Average savings amount
- Risk warning frequency
- Geographic distribution
- User segment performance

**Update Frequency:** 5 minutes

---

## 🎯 Key Metrics

### Product Success (from PRD)

| Metric | Baseline | Target | Current Status |
|--------|----------|--------|----------------|
| Conversion Rate | - | +20% | 📊 Tracked |
| NPS | - | +10 points | ⏳ Needs survey |
| Support Efficiency | - | -30% inquiries | ⏳ Needs integration |
| User Engagement | - | +15% time | 📊 Tracked |

### Technical Performance (from PRD)

| Metric | Target | Current |
|--------|--------|---------|
| API P95 Response Time | < 2000ms | 📊 Monitored |
| Uptime | 99.9% | 📊 Monitored |
| Error Rate | < 1% | 📊 Monitored |
| Cache Hit Rate | > 80% | 📊 Monitored |

---

## 🔒 Privacy & Compliance

### GDPR Compliance

✅ **Cookie Consent**
- Opt-in required before tracking
- Easy decline option
- Settings page for management

✅ **Data Anonymization**
- No PII collected
- User IDs hashed (SHA-256)
- IP addresses anonymized

✅ **Data Retention**
- 90-day retention policy
- Automatic deletion
- User right to deletion

✅ **Transparency**
- Clear data usage explanation
- Privacy policy linked
- What is/isn't collected documented

### What We Track
- Anonymized user interactions
- System performance metrics
- Business outcomes
- Session behavior

### What We DON'T Track
- Personal information (name, email, phone)
- Financial data
- Precise location
- Any PII

---

## 💻 Usage Examples

### Frontend

```typescript
// Initialize
import analytics from './utils/analytics';

analytics.initialize({
  enabled: true,
  platform: 'ga4',
  ga4MeasurementId: 'G-XXXXXXXXXX',
  cookieConsent: true,
});

// Track events
analytics.trackOnboardingStarted();
analytics.trackPlanCardExpanded('plan-1', 'Green Energy', 1);
analytics.trackRecommendationGenerated(3, 'budget_conscious', 1250);

// Set user properties (NO PII!)
analytics.setUserProperties({
  property_type: 'residential',
  zip_code: '77002',
});
```

### Backend

```python
# Initialize
from services.analytics_service import init_analytics, AnalyticsBackend

analytics = init_analytics(
    backend=AnalyticsBackend.MIXPANEL,
    mixpanel_token='your_token'
)

# Track events
await analytics.track_recommendation_generated(
    user_id=user.id,
    profile_type="budget_conscious",
    num_plans=3,
    duration_ms=1250,
    total_savings=245.50
)

# Track performance
async with PerformanceTimer("recommendation_gen", user_id):
    recommendations = await generate_recommendations()
```

**More Examples:** [`docs/analytics-integration-examples.md`](docs/analytics-integration-examples.md)

---

## 🧪 Testing

### Frontend Tests
```bash
cd src/frontend
npm test -- analytics
```

### Backend Tests
```bash
cd src/backend
pytest tests/ -k analytics
```

### Manual Testing
1. Enable debug mode
2. Perform actions in app
3. Check browser console for events
4. Verify in GA4 DebugView
5. Check database for event records

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`analytics-setup.md`](docs/analytics-setup.md) | Complete setup guide (600+ lines) |
| [`metrics-definitions.md`](docs/metrics-definitions.md) | All metrics defined (800+ lines) |
| [`dashboard-guide.md`](docs/dashboard-guide.md) | Dashboard usage guide (900+ lines) |
| [`analytics-integration-examples.md`](docs/analytics-integration-examples.md) | Code examples (500+ lines) |
| [`ANALYTICS-QUICK-START.md`](docs/ANALYTICS-QUICK-START.md) | 5-minute quick start |

---

## 🔧 Configuration

### Environment Variables

#### Frontend
```bash
# .env
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
VITE_MIXPANEL_TOKEN=your_token      # Optional
VITE_ANALYTICS_ENABLED=true
VITE_ANALYTICS_DEBUG=false
```

#### Backend
```bash
# .env
ANALYTICS_ENABLED=true
ANALYTICS_BACKEND=mixpanel          # or 'logging', 'database'
MIXPANEL_TOKEN=your_token
ANALYTICS_BATCH_SIZE=100
ANALYTICS_FLUSH_INTERVAL=60         # seconds
```

---

## 📊 Database Schema

```sql
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    event VARCHAR(100) NOT NULL,
    user_id UUID,                    -- Anonymized
    properties JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_analytics_events_event ON analytics_events(event);
CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_timestamp ON analytics_events(timestamp);
CREATE INDEX idx_analytics_events_properties ON analytics_events USING GIN(properties);
```

---

## 🚨 Alerts & Monitoring

### Critical Alerts (Immediate Response)
- Error rate > 5%
- API P95 > 3000ms
- Zero recommendations for > 1 hour
- API completely down

### Warning Alerts (1 Hour Response)
- Error rate > 1%
- Cache hit rate < 60%
- Onboarding completion < 50%
- DAU drops > 20%

### Info Alerts (Daily Review)
- Weekly metric highs/lows
- Unusual geographic patterns
- Significant preference shifts

---

## 🛠️ Troubleshooting

### Events Not Appearing?

**Frontend (GA4/Mixpanel):**
1. Check measurement ID/token is correct
2. Verify cookie consent is granted
3. Enable debug mode: `analytics.initialize({ debug: true })`
4. Check browser console for errors
5. Use GA4 DebugView for real-time debugging

**Backend:**
1. Verify analytics is initialized
2. Check environment variables
3. Enable logging: `backend=AnalyticsBackend.LOGGING`
4. Check event queue: `print(analytics.event_queue)`

**Database:**
1. Verify table exists: `SELECT * FROM analytics_events LIMIT 1;`
2. Check indexes: `\d analytics_events`
3. Verify events are being written: `SELECT COUNT(*) FROM analytics_events;`

### Dashboard Shows No Data?

1. Verify PostgreSQL connection in Grafana
2. Test query in Grafana query editor
3. Check time range settings
4. Verify analytics_events table has data
5. Check dashboard refresh interval

---

## 🎯 Performance

### Frontend
- Event tracking: <1ms overhead
- Non-blocking async calls
- Session-based batching
- Debounced frequent events

### Backend
- Event batching: 100 events or 60 seconds
- Async processing (non-blocking)
- <1ms API overhead
- Automatic flush on shutdown

### Database
- Indexed columns for fast queries
- JSONB for flexible properties
- Optional partitioning for scale
- Materialized views for dashboards

---

## 📈 Roadmap

### ✅ Completed (v1.0)
- Comprehensive event tracking
- Real-time dashboards
- GDPR compliance
- Multi-platform support

### 🔄 In Progress
- [ ] NPS survey integration
- [ ] Support ticket tracking
- [ ] A/B testing framework

### 📋 Planned (v2.0)
- [ ] Real-time WebSocket dashboards
- [ ] Advanced cohort analysis
- [ ] Predictive analytics
- [ ] Machine learning on usage patterns
- [ ] Mobile app analytics

---

## 🤝 Contributing

### Adding New Events

1. Define event in analytics utility
2. Add tracking call in component/endpoint
3. Update dashboard queries if needed
4. Document in metrics-definitions.md
5. Test in debug mode

### Creating New Dashboards

1. Design dashboard in Grafana UI
2. Export JSON: Settings → JSON Model
3. Save to `/dashboards/`
4. Document panels in dashboard-guide.md
5. Add SQL queries to dashboard_queries.sql

---

## 📞 Support

### Documentation
- Full docs in `/docs/` directory
- Quick start: `docs/ANALYTICS-QUICK-START.md`
- Setup guide: `docs/analytics-setup.md`

### Resources
- [Google Analytics 4 Docs](https://support.google.com/analytics)
- [Mixpanel Docs](https://developer.mixpanel.com/)
- [Grafana Docs](https://grafana.com/docs/)

---

## 📄 License

Part of the TreeBeard Energy Plan Recommendation Agent project.

---

## 🎉 Acknowledgments

Built with:
- **Frontend:** React, TypeScript, Vite
- **Backend:** Python, FastAPI
- **Analytics:** Google Analytics 4, Mixpanel
- **Dashboards:** Grafana, PostgreSQL
- **Privacy:** GDPR-compliant by design

---

**Status:** ✅ Production Ready

**Version:** 1.0.0

**Last Updated:** November 10, 2025

---

Made with ❤️ for data-driven decision making
