# Dashboard Guide

## Overview

This guide explains how to use and interpret the TreeBeard Analytics dashboards. These dashboards provide real-time insights into user behavior, system performance, and business metrics.

---

## Dashboard Access

### Grafana URL
```
http://localhost:3000
```

**Default Credentials:**
- Username: `admin`
- Password: `admin` (change on first login)

### Dashboard Organization
- **User Engagement** - User behavior and onboarding metrics
- **Conversion Metrics** - Recommendation and plan interaction metrics
- **System Performance** - API performance and reliability metrics
- **Business Intelligence** - Business insights and trends

---

## Dashboard 1: User Engagement

**Purpose:** Monitor how users interact with the platform and track onboarding success.

**Refresh Rate:** 1 minute

**Time Range:** Last 30 days (customizable)

### Panels

#### 1. Total Users
**Type:** Stat
**Metric:** COUNT(DISTINCT user_id)
**Time Range:** Last 30 days

**What it shows:**
- Total number of unique users who have used the platform

**How to interpret:**
- Steady growth indicates successful user acquisition
- Sudden spikes may indicate marketing campaigns
- Drops may indicate technical issues or seasonal trends

**Actions:**
- Green: Continue current strategy
- Yellow/Red: Investigate user acquisition issues

---

#### 2. Daily Active Users (DAU)
**Type:** Stat
**Metric:** COUNT(DISTINCT user_id in last 24h)

**What it shows:**
- Number of users active in the last 24 hours

**How to interpret:**
- High DAU = strong daily engagement
- Compare to MAU for stickiness ratio
- Track day-of-week patterns

**Typical Patterns:**
- Weekdays: Higher (people shopping for plans)
- Weekends: Lower
- Monday/Tuesday: Peak days

---

#### 3. Weekly Active Users (WAU)
**Type:** Stat
**Metric:** COUNT(DISTINCT user_id in last 7 days)

**What it shows:**
- Number of users active in the last 7 days

**How to interpret:**
- Balances daily volatility with monthly trends
- Good indicator of regular usage
- Should be 40-60% of MAU

---

#### 4. Onboarding Funnel
**Type:** Graph (Line Chart)
**Metrics:** Started, Step 1, Step 2, Step 3, Step 4, Completed

**What it shows:**
- User progression through onboarding steps over time

**How to interpret:**
- **Steep drop-off:** Indicates friction at that step
- **Gradual decline:** Normal behavior
- **Flat sections:** High conversion between steps

**Example Analysis:**
```
Started: 100 users
Step 1: 90 users (10% drop) ← Investigate if > 15%
Step 2: 80 users (11% drop)
Step 3: 60 users (25% drop) ← Major friction point!
Step 4: 55 users (8% drop)
Completed: 50 users (9% drop)

Overall completion: 50% ← Below 70% target
```

**Actions:**
- Identify highest drop-off step
- Review UX at that step
- Check for technical errors
- Consider A/B testing improvements

---

#### 5. Onboarding Completion Rate
**Type:** Gauge
**Metric:** (Completed / Started) * 100
**Target:** > 70%

**Color Coding:**
- Green: > 70%
- Yellow: 50-70%
- Red: < 50%

**What it shows:**
- Percentage of users who complete entire onboarding

**How to interpret:**
- Primary activation metric
- Direct impact on recommendation generation
- Compare weekly trends

**Actions:**
- < 50%: Critical - investigate immediately
- 50-70%: Moderate - review UX and friction points
- > 70%: Good - maintain and optimize

---

#### 6. Abandonment Rate by Step
**Type:** Bar Gauge (Horizontal)
**Metrics:** Abandonments per step

**What it shows:**
- Which onboarding steps users abandon most

**How to interpret:**
- **Step 3 (Usage Upload):** Often highest due to complexity
- **Step 2 (Current Plan):** May be high if unclear
- **Step 1 (Welcome):** Should be lowest

**Common Issues:**
- High Step 1: Unclear value proposition
- High Step 2: Too many required fields
- High Step 3: File upload problems
- High Step 4: Preference confusion

---

#### 7. Average Onboarding Time
**Type:** Stat
**Metric:** AVG(total_time_seconds)
**Unit:** Seconds/Minutes
**Target:** < 5 minutes

**What it shows:**
- Mean time from start to completion

**How to interpret:**
- Too long: Users spending excess time (confusion?)
- Too short: Users rushing (may skip important info)
- Optimal: 3-5 minutes

**Correlation with Completion:**
- If time ↑ and completion ↓: Too complex
- If time ↓ and completion ↑: Good UX improvements

---

#### 8. Top Abandonment Reasons
**Type:** Table
**Columns:** Reason, Count, Percentage

**What it shows:**
- Why users abandon onboarding (if tracked)

**Common Reasons:**
- "too_complex"
- "no_current_plan_data"
- "privacy_concerns"
- "unclear_value"
- "technical_error"

**Actions:**
- Address top 3 reasons immediately
- Update help text for common confusions
- Fix technical errors

---

## Dashboard 2: Conversion Metrics

**Purpose:** Track user journey from recommendation to plan selection.

**Refresh Rate:** 1 minute

**Time Range:** Last 7 days (customizable)

### Panels

#### 1. Recommendation Generation Rate
**Type:** Stat
**Metric:** COUNT(recommendation_generated in last 24h)

**What it shows:**
- How many recommendations generated per day

**How to interpret:**
- Should correlate with onboarding completions
- Sudden drop: Technical issue or onboarding problem
- Gradual growth: Healthy user acquisition

**Benchmark:**
- Should equal ~70% of onboarding completions (completion rate target)

---

#### 2. Average Plans per User
**Type:** Stat
**Metric:** AVG(num_plans)
**Expected:** 3.0

**What it shows:**
- Average number of plans shown to users

**How to interpret:**
- Should always be 3 (top 3 recommendations)
- < 3: Edge case or insufficient plan catalog
- > 3: Bug in recommendation engine

**Actions:**
- Variance > 0.1: Investigate edge cases
- Consistent < 3: Review plan availability

---

#### 3. Plan Card Expansion Rate
**Type:** Stat (%)
**Metric:** (Users who expanded / Users who got recommendations) * 100
**Target:** > 80%

**What it shows:**
- Percentage of users who engage with recommendations

**How to interpret:**
- High rate: Recommendations are compelling
- Low rate: Users not interested or confused
- This is the first major conversion point

**Optimization:**
- < 60%: Review recommendation quality
- 60-80%: Good, but room for improvement
- > 80%: Excellent engagement

---

#### 4. Cost Breakdown View Rate
**Type:** Stat (%)
**Target:** > 60%

**What it shows:**
- Percentage of users who view detailed cost information

**How to interpret:**
- Indicates seriousness of intent
- Higher rate = more informed decisions
- Critical for building trust

---

#### 5. Recommendations Over Time
**Type:** Graph (Time Series)
**Time Granularity:** Hourly

**What it shows:**
- Recommendations generated by hour

**Patterns to Look For:**
- **Daily peaks:** 10am-2pm, 6pm-9pm
- **Weekly peaks:** Tuesday-Wednesday
- **Anomalies:** Sudden drops or spikes

**Use Cases:**
- Capacity planning
- Identifying outages
- Understanding user behavior patterns

---

#### 6. User Profile Type Distribution
**Type:** Pie Chart
**Segments:** budget_conscious, eco_friendly, flexibility_first, etc.

**What it shows:**
- How users are classified by recommendation engine

**How to interpret:**
- Validates targeting assumptions
- Guides product development priorities
- Informs marketing messaging

**Expected Distribution:**
- Budget Conscious: 40-50%
- Eco-Friendly: 20-30%
- Flexibility First: 15-25%
- Others: 5-15%

---

#### 7. Average Savings Shown
**Type:** Stat
**Unit:** USD
**Target:** > $150/year

**What it shows:**
- Mean annual savings displayed to users

**How to interpret:**
- Key value proposition metric
- Higher = better recommendations
- Use in marketing: "Users save an average of $X/year"

**Segmentation:**
- By property type
- By ZIP code
- By usage profile

---

#### 8. Plan Interaction by Position
**Type:** Bar Gauge
**Positions:** 1, 2, 3

**What it shows:**
- Which recommended position gets most interaction

**Expected Pattern:**
- Position 1: ~50-60% (top recommendation)
- Position 2: ~25-30%
- Position 3: ~15-20%

**How to interpret:**
- Even distribution: Algorithm not ranking well
- Heavy skew to #1: Good ranking
- #3 > #1: Users disagree with ranking

---

#### 9. Conversion Funnel Over Time
**Type:** Multi-Line Graph
**Lines:** Generated, Expanded, Viewed Breakdown, Clicked

**What it shows:**
- User progression through conversion funnel

**How to interpret:**
- Width of funnel = drop-off rate
- Parallel lines = consistent conversion
- Diverging lines = declining engagement

**Conversion Rate Calculation:**
```
Generated → Expanded: Should be > 80%
Expanded → Viewed Breakdown: Should be > 60%
Viewed Breakdown → Clicked: Should be > 40%
```

---

#### 10. Top Recommended Plans
**Type:** Table
**Columns:** Plan, Times Shown, Unique Users, Expansions, Clicks

**What it shows:**
- Most frequently recommended plans

**How to interpret:**
- Validates plan catalog coverage
- Identifies popular plans for supplier negotiations
- May indicate algorithm bias if too concentrated

**Red Flags:**
- Same plan to > 50% of users: Check diversity
- Zero clicks on top plans: Quality issue?
- High variance in expansion rates: Inconsistent UX?

---

## Dashboard 3: System Performance

**Purpose:** Monitor API health, performance, and reliability.

**Refresh Rate:** 30 seconds

**Time Range:** Last 1 hour (customizable)

### Panels

#### 1-3. API Response Time (P50, P95, P99)
**Type:** Stat
**Unit:** Milliseconds

**Targets:**
- P50: < 500ms
- P95: < 2000ms
- P99: < 3000ms

**Color Coding:**
- Green: Within target
- Yellow: Approaching threshold
- Red: Exceeding target

**What they show:**
- P50: Typical user experience
- P95: 19 out of 20 users
- P99: Worst-case acceptable performance

**How to interpret:**
- All green: System healthy
- P99 red, others green: Occasional slowness
- All red: Performance problem

**Actions:**
- Yellow: Monitor closely
- Red: Investigate immediately (check slow queries, scaling)

---

#### 4. Error Rate
**Type:** Gauge
**Unit:** Percentage
**Target:** < 1%

**Color Coding:**
- Green: < 1%
- Yellow: 1-3%
- Red: > 3%

**What it shows:**
- Percentage of failed API requests

**How to interpret:**
- Spike: Deployment issue or bug
- Gradual increase: Degrading infrastructure
- Consistent high: Systemic problem

**Error Types:**
- 4xx (Client): User errors, validation issues
- 5xx (Server): Application bugs, infrastructure issues

**Actions:**
- > 1%: Check error breakdown table
- > 3%: Emergency response
- > 5%: Consider rollback

---

#### 5. Cache Hit Rate
**Type:** Gauge
**Unit:** Percentage
**Target:** > 80%

**What it shows:**
- Percentage of requests served from cache

**How to interpret:**
- High (> 80%): Good performance and cost efficiency
- Medium (60-80%): Room for optimization
- Low (< 60%): Cache issues or cold cache

**Impact:**
- +10% hit rate ≈ -10% database load
- +10% hit rate ≈ -15% average response time

**Actions:**
- < 60%: Review cache strategy
- Sudden drop: Check cache invalidation or restarts

---

#### 6. Recommendations per Hour
**Type:** Stat
**What it shows:** Current recommendation throughput

**How to interpret:**
- Use for capacity planning
- Compare to historical peaks
- Alert if zero for > 1 hour

---

#### 7. API Response Times Over Time
**Type:** Multi-Line Graph
**Lines:** P50, P95, P99

**What it shows:**
- Performance trends over time

**Patterns:**
- Steady lines: Consistent performance
- Spikes: Traffic surges or slow queries
- Gradual increase: Need to scale

**Use Cases:**
- Correlate with deployment times
- Identify daily patterns
- Capacity planning

---

#### 8. Request Rate by Endpoint
**Type:** Stacked Area Chart
**Breakdown:** By endpoint

**What it shows:**
- Traffic distribution across endpoints

**How to interpret:**
- Highest: `/api/v1/recommendations/generate`
- Identify hotspots for optimization
- Detect unusual patterns (e.g., automated scraping)

---

#### 9. Slowest Endpoints (P95)
**Type:** Table
**Columns:** Endpoint, Requests, P95 (ms), Average (ms)
**Sort:** By P95 DESC

**What it shows:**
- Endpoints with worst performance

**How to interpret:**
- Target optimization efforts here
- High P95 with low average: Occasional slow queries
- High both: Consistently slow endpoint

**Common Slow Endpoints:**
- `/api/v1/recommendations/generate` (complex algorithm)
- `/api/v1/usage/upload` (file processing)
- `/api/v1/plans/catalog` (large dataset)

**Actions:**
- Add caching
- Optimize database queries
- Add pagination
- Implement async processing

---

#### 10. Error Breakdown by Type
**Type:** Table
**Columns:** Error Type, Endpoint, Count, Percentage

**What it shows:**
- Most common errors and where they occur

**How to interpret:**
- **ValidationError:** User input issues
- **NotFoundError:** Missing resources
- **TimeoutError:** Performance issues
- **DatabaseError:** Infrastructure issues

**Actions:**
- Top errors: Fix immediately
- Endpoint patterns: Review specific endpoint
- New errors: Recent deployment issue?

---

#### 11. Peak Usage Times
**Type:** Bar Chart
**Time Range:** Last 7 days
**Granularity:** Hourly

**What it shows:**
- Busiest times for API traffic

**Use Cases:**
- Schedule deployments during low traffic
- Plan scaling for peak times
- Identify maintenance windows

**Typical Pattern:**
- Peak: 10am-2pm, 6pm-9pm
- Low: 2am-6am
- Use for: Maintenance, deployments, batch jobs

---

#### 12. Request Distribution by Hour of Day
**Type:** Heatmap
**Axes:** Day of week × Hour of day

**What it shows:**
- Traffic patterns over week

**How to interpret:**
- Dark cells: High traffic
- Light cells: Low traffic
- Use for capacity and staffing planning

---

## Dashboard 4: Business Intelligence

**Purpose:** Strategic insights for business decisions.

**Refresh Rate:** 5 minutes

**Time Range:** Last 30 days (customizable)

### Panels

#### 1. Most Popular Plan Types
**Type:** Pie Chart
**Segments:** Fixed Rate, Variable, TOU, etc.

**What it shows:**
- User preferences for plan types

**Business Insights:**
- Guide supplier negotiations
- Inform plan catalog expansion
- Validate market assumptions

---

#### 2. Average Savings Amount
**Type:** Stat
**Unit:** USD
**Target:** > $150

**What it shows:**
- Mean annual savings shown to users

**Business Use:**
- Marketing messaging
- ROI calculations
- Value proposition validation

**Color Thresholds:**
- Green: > $200 (strong value)
- Yellow: $150-$200 (good value)
- Red: < $150 (weak value)

---

#### 3. Risk Warnings by Type
**Type:** Bar Gauge
**Categories:** High ETF, Marginal Savings, Data Quality, etc.

**What it shows:**
- Frequency of each risk warning type

**How to interpret:**
- High ETF warnings: Common, protect users
- Data quality: May indicate input issues
- Too few warnings: Algorithm may be too aggressive

**Target:** 20-30% of recommendations should have at least one warning

---

#### 4. Risk Warning Severity Distribution
**Type:** Pie Chart
**Segments:** Critical, Warning, Info

**What it shows:**
- Breakdown of warning severity

**Expected:**
- Critical: 5-10%
- Warning: 15-20%
- Info: 5-10%
- No warnings: 60-75%

---

#### 5. User Property Type Distribution
**Type:** Pie Chart
**Segments:** Residential, Small Business, Commercial, etc.

**What it shows:**
- Target market breakdown

**Business Insights:**
- Validate market focus (should be 80-90% residential)
- Identify growth opportunities
- Guide product features

---

#### 6. Geographic Usage by ZIP
**Type:** Map (if supported) or Table
**Top 50 ZIP codes**

**What it shows:**
- Geographic concentration of users

**Business Insights:**
- Marketing spend allocation
- Regional plan availability
- Expansion opportunities

**Look For:**
- Clusters in deregulated markets
- Gaps in coverage
- High-value ZIP codes

---

#### 7. Top ZIP Codes with Activation Rate
**Type:** Table
**Columns:** ZIP, Total Users, Active Users, Activation %

**What it shows:**
- Which locations have best engagement

**How to interpret:**
- High activation: Good market fit
- Low activation: May need localized improvements
- Use for targeted marketing

---

#### 8. User Preferences Trends
**Type:** Multi-Line Graph
**Lines:** Cost, Renewable, Flexibility, Ratings priorities

**What it shows:**
- How user priorities change over time

**Trends to Watch:**
- Renewable increasing: Market shift to sustainability
- Cost decreasing: Users less price-sensitive
- Use to adjust algorithm weights

---

#### 9. Return User Rate
**Type:** Stat
**Unit:** Percentage
**Target:** > 30%

**What it shows:**
- Percentage of users who come back

**How to interpret:**
- High: Product has lasting value
- Low: One-time use case
- Seasonal: Annual renewal pattern?

---

#### 10. File Upload Success Rate
**Type:** Bar Gauge
**Breakdown:** By file type (CSV, PDF, etc.)

**What it shows:**
- Upload success by file format

**How to interpret:**
- Low rate: UX or validation issues
- Variance by type: Format-specific problems

**Target:** > 90% success rate

---

#### 11. User Segment Performance
**Type:** Table
**Columns:** Segment, Users, Avg Savings, Total Recommendations

**What it shows:**
- How different user segments perform

**Business Insights:**
- Which segments have highest value
- Where to focus acquisition
- Segment-specific optimizations

---

## Using Dashboards for Decision Making

### Daily Monitoring Checklist
```
□ Check error rate (< 1%)
□ Check API P95 response time (< 2000ms)
□ Review DAU trend
□ Check for zero-recommendation periods
□ Review any red metrics
```

### Weekly Review Checklist
```
□ Analyze onboarding funnel changes
□ Review top abandonment reasons
□ Check conversion funnel trends
□ Analyze slow endpoints
□ Review cache hit rate
□ Compare week-over-week growth
```

### Monthly Business Review
```
□ MAU and growth trend
□ Stickiness ratio (DAU/MAU)
□ Average savings shown
□ User segment performance
□ Geographic expansion progress
□ Product success metrics vs. targets
```

### Incident Response
```
1. Check System Performance dashboard
2. Identify affected endpoints
3. Review error breakdown
4. Check recent deployments
5. Analyze traffic patterns
6. Review user impact (how many users affected)
```

---

## Alerting Best Practices

### Critical Alerts (Immediate Response)
- Error rate > 5%
- P95 response time > 3000ms
- Zero recommendations for > 1 hour
- API completely down

### Warning Alerts (Review Within 1 Hour)
- Error rate > 1%
- Cache hit rate < 60%
- Onboarding completion rate < 50%
- DAU drops > 20%

### Info Alerts (Review Daily)
- New weekly high/low metrics
- Unusual geographic patterns
- Significant preference shifts

---

## Tips for Effective Dashboard Use

1. **Start Broad, Then Drill Down**
   - Check overview metrics first
   - Identify anomalies
   - Drill into specific panels for details

2. **Compare Time Periods**
   - Use time range selector
   - Compare week-over-week
   - Identify trends vs. anomalies

3. **Correlate Across Dashboards**
   - High errors + slow response times = performance issue
   - Low DAU + high onboarding starts = activation problem
   - High expansion rate + low savings = quality issue

4. **Set Up Alerts**
   - Don't rely on manual checking
   - Alert on thresholds
   - Escalate based on severity

5. **Regular Reviews**
   - Daily: Performance and errors
   - Weekly: Engagement and conversion
   - Monthly: Business metrics and trends

6. **Document Findings**
   - Note unusual patterns
   - Track actions taken
   - Measure impact of changes
