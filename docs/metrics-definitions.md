# Metrics Definitions

## Overview

This document defines all metrics tracked in the TreeBeard Analytics system, including calculation methods, business context, and interpretation guidelines.

---

## User Engagement Metrics

### Total Users
**Definition:** Total number of unique users who have interacted with the platform.

**Calculation:**
```sql
COUNT(DISTINCT user_id) FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '30 days'
```

**Target:** Steady growth (5-10% month-over-month)

**Interpretation:**
- Measures overall platform reach
- Indicates marketing effectiveness
- Base metric for calculating rates

---

### Daily Active Users (DAU)
**Definition:** Number of unique users who performed at least one action in the last 24 hours.

**Calculation:**
```sql
COUNT(DISTINCT user_id) FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '24 hours'
```

**Target:** > 20% of MAU

**Interpretation:**
- Measures daily engagement
- High DAU indicates strong product-market fit
- Use for detecting usage patterns and trends

---

### Weekly Active Users (WAU)
**Definition:** Number of unique users who performed at least one action in the last 7 days.

**Calculation:**
```sql
COUNT(DISTINCT user_id) FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '7 days'
```

**Target:** > 50% of MAU

**Interpretation:**
- Balances daily volatility with monthly trends
- Good indicator of regular usage

---

### Monthly Active Users (MAU)
**Definition:** Number of unique users who performed at least one action in the last 30 days.

**Calculation:**
```sql
COUNT(DISTINCT user_id) FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '30 days'
```

**Target:** Steady growth (10-15% MoM)

**Interpretation:**
- Primary growth metric
- Used for calculating stickiness ratios

---

### Stickiness Ratio (DAU/MAU)
**Definition:** Percentage of monthly active users who use the product daily.

**Calculation:**
```sql
(DAU / MAU) * 100
```

**Target:** > 20%

**Industry Benchmarks:**
- Excellent: > 25%
- Good: 15-25%
- Average: 10-15%
- Poor: < 10%

**Interpretation:**
- Measures product engagement and habit formation
- Higher ratio = more engaged user base
- Indicates product value and retention

---

### Onboarding Completion Rate
**Definition:** Percentage of users who complete the entire onboarding process.

**Calculation:**
```sql
(COUNT(onboarding_completed) / COUNT(onboarding_started)) * 100
```

**Target:** > 70% (PRD target: +20% improvement)

**Interpretation:**
- Measures onboarding effectiveness
- Low rate indicates friction points
- Direct impact on activation rate

---

### Average Time to Complete Onboarding
**Definition:** Mean time from onboarding start to completion.

**Calculation:**
```sql
AVG(total_time_seconds) FROM onboarding_completed events
```

**Target:** < 5 minutes

**Interpretation:**
- Shorter is generally better (less friction)
- Too short might indicate rushed experience
- Benchmark against completion rate

---

### Onboarding Abandonment Rate
**Definition:** Percentage of users who start but don't complete onboarding.

**Calculation:**
```sql
(COUNT(onboarding_abandoned) / COUNT(onboarding_started)) * 100
```

**Target:** < 30%

**By Step:**
- Step 1 (Welcome): < 10%
- Step 2 (Current Plan): < 15%
- Step 3 (Usage Upload): < 25%
- Step 4 (Preferences): < 20%

**Interpretation:**
- Inverse of completion rate
- High abandonment at specific step = UX issue
- Track reasons for abandonment

---

## Conversion Metrics

### Recommendation Generation Rate
**Definition:** Number of successful recommendations generated per time period.

**Calculation:**
```sql
COUNT(recommendation_generated) per hour/day
```

**Target:** > 100 per day (scales with user growth)

**Interpretation:**
- Indicates successful onboarding completion
- Core product usage metric
- Should correlate with new users

---

### Plans Viewed per User
**Definition:** Average number of recommended plans shown to each user.

**Calculation:**
```sql
AVG(num_plans) FROM recommendation_generated events
```

**Target:** 3.0 (as per design)

**Interpretation:**
- Should be consistently 3 (top 3 recommendations)
- Variance indicates edge cases or errors

---

### Plan Card Expansion Rate
**Definition:** Percentage of users who expand at least one plan card after seeing recommendations.

**Calculation:**
```sql
(COUNT(DISTINCT user_id with plan_card_expanded) /
 COUNT(DISTINCT user_id with recommendation_generated)) * 100
```

**Target:** > 80%

**Interpretation:**
- Measures recommendation engagement
- High rate = users interested in details
- Low rate = recommendations not compelling

---

### Cost Breakdown View Rate
**Definition:** Percentage of users who view detailed cost breakdowns.

**Calculation:**
```sql
(COUNT(DISTINCT user_id with cost_breakdown_viewed) /
 COUNT(DISTINCT user_id with recommendation_generated)) * 100
```

**Target:** > 60%

**Interpretation:**
- Indicates trust and interest in recommendations
- Higher rate = users doing due diligence
- Critical for conversion to selection

---

### Comparison View Rate
**Definition:** Percentage of users who use side-by-side comparison feature.

**Calculation:**
```sql
(COUNT(DISTINCT user_id with comparison_viewed) /
 COUNT(DISTINCT user_id with recommendation_generated)) * 100
```

**Target:** > 40%

**Interpretation:**
- Advanced feature usage
- Indicates engaged, analytical users
- Correlates with higher satisfaction

---

### Average Savings Shown
**Definition:** Mean dollar amount of savings displayed to users.

**Calculation:**
```sql
AVG(total_savings) FROM recommendation_generated events
```

**Target:** > $150/year

**Business Impact:**
- Key value proposition metric
- Used in marketing messaging
- Validates recommendation algorithm

**Interpretation:**
- Higher savings = better recommendations
- Track by user segment
- Compare to actual realized savings (if available)

---

## System Performance Metrics

### API Response Time (P50, P95, P99)
**Definition:** Time to respond to API requests at various percentiles.

**Calculation:**
```sql
percentile_cont(0.50/0.95/0.99) WITHIN GROUP (ORDER BY duration_ms)
```

**Targets (from PRD):**
- P50: < 500ms
- P95: < 2000ms
- P99: < 3000ms

**Interpretation:**
- P50: Typical user experience
- P95: Experience of 19 in 20 users
- P99: Worst-case acceptable performance

**Industry Benchmarks:**
- Excellent: P95 < 1000ms
- Good: P95 < 2000ms
- Poor: P95 > 3000ms

---

### Error Rate
**Definition:** Percentage of API requests that result in errors.

**Calculation:**
```sql
(COUNT(error_occurred) / COUNT(api_request)) * 100
```

**Target:** < 1% (PRD target)

**By Severity:**
- 4xx errors: < 2% (client errors)
- 5xx errors: < 0.5% (server errors)

**Interpretation:**
- Primary reliability metric
- Spikes indicate bugs or infrastructure issues
- Track by endpoint to isolate problems

---

### Cache Hit Rate
**Definition:** Percentage of requests served from cache vs. database.

**Calculation:**
```sql
(COUNT(cache_hit) / (COUNT(cache_hit) + COUNT(cache_miss))) * 100
```

**Target:** > 80%

**Interpretation:**
- High rate = better performance and cost efficiency
- Low rate = cache invalidation issues or cold cache
- Track by cache type (plan catalog, recommendations, etc.)

---

### Recommendations per Hour
**Definition:** Number of recommendations generated per hour.

**Calculation:**
```sql
COUNT(recommendation_generated) per hour
```

**Target:** Scales with users; monitor for anomalies

**Interpretation:**
- Peak hours: 10am-2pm, 6pm-9pm
- Off-peak: 2am-6am
- Use for capacity planning

---

### Peak Usage Times
**Definition:** Hours of day with highest request volume.

**Calculation:**
```sql
GROUP BY EXTRACT(hour FROM timestamp)
ORDER BY COUNT(*) DESC
```

**Interpretation:**
- Informs maintenance windows
- Helps scale infrastructure
- Guides feature release timing

---

## Business Intelligence Metrics

### Most Popular Plan Types
**Definition:** Distribution of plan types selected/viewed by users.

**Categories:**
- Fixed Rate
- Variable Rate
- Time-of-Use
- Indexed
- Renewable/Green

**Calculation:**
```sql
COUNT(plan_card_clicked) GROUP BY plan_type
```

**Interpretation:**
- Indicates user preferences
- Guides supplier negotiations
- Informs recommendation algorithm weights

---

### Risk Warnings Frequency
**Definition:** Number and types of risk warnings triggered.

**Risk Types:**
- High Early Termination Fee (ETF > $150)
- Marginal Savings (< 5%)
- Insufficient Data Confidence
- Variable Rate Volatility
- Supplier Reliability Concerns

**Calculation:**
```sql
COUNT(risk_warning_triggered) GROUP BY risk_type
```

**Target:** < 30% of recommendations

**Interpretation:**
- High frequency = conservative algorithm (good)
- Very low frequency = potential missed warnings
- Track user response to warnings

---

### User Property Type Distribution
**Definition:** Breakdown of users by property type.

**Categories:**
- Residential
- Small Business
- Commercial
- Industrial

**Calculation:**
```sql
COUNT(user_created) GROUP BY property_type
```

**Interpretation:**
- Validates target market
- Guides product development priorities
- Informs segmentation strategy

---

### Geographic Usage Patterns
**Definition:** User distribution by ZIP code.

**Calculation:**
```sql
COUNT(user_created) GROUP BY zip_code
ORDER BY count DESC
```

**Interpretation:**
- Identifies geographic concentrations
- Validates deregulated market coverage
- Guides marketing spend allocation

---

### User Preferences Distribution
**Definition:** Distribution of user priority settings.

**Dimensions:**
- Cost Priority (0-100)
- Flexibility Priority (0-100)
- Renewable Energy Priority (0-100)
- Supplier Ratings Priority (0-100)

**Calculation:**
```sql
AVG(preferences->>'cost_priority')
AVG(preferences->>'renewable_priority')
AVG(preferences->>'flexibility_priority')
AVG(preferences->>'ratings_priority')
```

**Expected Ranges:**
- Cost: 60-80 (most users prioritize savings)
- Flexibility: 40-60
- Renewable: 30-50 (growing trend)
- Ratings: 50-70

**Interpretation:**
- Shifts over time indicate market trends
- Segment users by preference profiles
- Validate recommendation algorithm weights

---

### Return User Rate
**Definition:** Percentage of users who return after first visit.

**Calculation:**
```sql
(COUNT(users with > 1 session day) / COUNT(total users)) * 100
```

**Target:** > 30%

**Industry Benchmarks:**
- Excellent: > 40%
- Good: 25-40%
- Average: 15-25%
- Poor: < 15%

**Interpretation:**
- Indicates product value beyond initial use
- High rate = potential for annual renewals
- Track time between sessions

---

## Product Success Metrics (from PRD)

### Conversion Rate Improvement
**Definition:** Increase in plan sign-ups vs. baseline.

**Target:** +20% (from PRD)

**Calculation:**
```sql
((Current Conversion Rate - Baseline) / Baseline) * 100
```

**Interpretation:**
- Primary product success metric
- Requires integration with supplier data
- Long-term tracking metric

---

### Net Promoter Score (NPS)
**Definition:** User likelihood to recommend (scale: -100 to +100).

**Target:** +10 points improvement (from PRD)

**Calculation:**
```
NPS = % Promoters (9-10) - % Detractors (0-6)
```

**Industry Benchmarks:**
- Excellent: > 50
- Good: 30-50
- Average: 0-30
- Poor: < 0

**Interpretation:**
- Measures customer satisfaction
- Requires user survey implementation
- Leading indicator of retention

---

### Support Inquiry Reduction
**Definition:** Decrease in plan-selection related support tickets.

**Target:** -30% (from PRD)

**Calculation:**
```sql
((Baseline Tickets - Current Tickets) / Baseline Tickets) * 100
```

**Interpretation:**
- Validates recommendation clarity
- Cost savings metric
- Requires support system integration

---

### User Engagement Time
**Definition:** Average time spent in application per session.

**Target:** +15% increase (from PRD)

**Calculation:**
```sql
AVG(session_duration_seconds)
```

**Interpretation:**
- More time = deeper engagement
- Too much time might indicate confusion
- Balance with completion rates

---

## Advanced Metrics

### Time to First Recommendation
**Definition:** Time from onboarding start to first recommendation.

**Calculation:**
```sql
AVG(first_recommendation_timestamp - onboarding_start_timestamp)
```

**Target:** < 5 minutes

**Interpretation:**
- Measures onboarding efficiency
- Shorter = less friction
- Track abandonment correlation

---

### Session Duration
**Definition:** Length of user session from first to last event.

**Calculation:**
```sql
MAX(timestamp) - MIN(timestamp) per session
```

**Target:** 5-15 minutes (optimal range)

**Interpretation:**
- Too short: Users not exploring
- Too long: Potential confusion
- Segment by user type

---

### Events per Session
**Definition:** Average number of events in a user session.

**Calculation:**
```sql
COUNT(events) / COUNT(DISTINCT sessions)
```

**Target:** 10-20 events

**Interpretation:**
- Higher = more engaged
- Track by event type
- Compare completers vs. abandoners

---

### Cohort Retention
**Definition:** Percentage of users from a cohort who return in subsequent weeks.

**Calculation:**
```sql
Weekly cohort retention table (see dashboard queries)
```

**Targets:**
- Week 1: > 40%
- Week 2: > 30%
- Week 4: > 20%

**Interpretation:**
- Measures long-term engagement
- Identifies retention drop-off points
- Guides re-engagement campaigns

---

## Metric Relationships

### Funnel Metrics
```
Users Started Onboarding
    ↓ (Completion Rate)
Users Completed Onboarding
    ↓ (Generation Rate)
Recommendations Generated
    ↓ (Expansion Rate)
Plan Cards Expanded
    ↓ (View Rate)
Cost Breakdowns Viewed
    ↓ (Conversion Rate)
Plans Selected
```

### Health Score Formula
```
Health Score = (
    Onboarding Completion Rate * 0.3 +
    Plan Expansion Rate * 0.2 +
    DAU/MAU Ratio * 0.2 +
    (1 - Error Rate) * 0.15 +
    Cache Hit Rate * 0.15
) * 100

Target: > 70
```

---

## Data Quality Checks

### Event Completeness
- All events have required properties
- No null user_ids (when expected)
- Timestamp within reasonable range

### Data Consistency
- Onboarding completed ≤ Onboarding started
- Plan clicks ≤ Plan views
- Session events in chronological order

### Anomaly Detection
- Sudden spikes/drops (> 50% change)
- Zero events for > 1 hour
- Unusual geographic patterns
- Outlier session durations (> 1 hour)

---

## Metric Review Cadence

### Daily
- DAU
- Error Rate
- API Response Times
- Recommendations Generated

### Weekly
- WAU
- Onboarding Completion Rate
- Conversion Funnel Metrics
- Top Issues

### Monthly
- MAU
- Stickiness Ratio
- Cohort Retention
- NPS
- Product Success Metrics

### Quarterly
- Business Goals Progress
- User Segmentation Analysis
- Geographic Expansion
- Feature Usage Trends
