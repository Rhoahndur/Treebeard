-- TreeBeard Analytics Dashboard Queries
-- These queries support the Grafana dashboards and business metrics

-- ============================================================================
-- USER ENGAGEMENT METRICS
-- ============================================================================

-- Total Users (Last 30 Days)
SELECT COUNT(DISTINCT user_id) as total_users
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '30 days';

-- Daily Active Users (DAU)
SELECT COUNT(DISTINCT user_id) as dau
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '24 hours';

-- Weekly Active Users (WAU)
SELECT COUNT(DISTINCT user_id) as wau
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- Monthly Active Users (MAU)
SELECT COUNT(DISTINCT user_id) as mau
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '30 days';

-- DAU/MAU Ratio (Stickiness Metric)
WITH dau AS (
    SELECT COUNT(DISTINCT user_id) as count
    FROM analytics_events
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
),
mau AS (
    SELECT COUNT(DISTINCT user_id) as count
    FROM analytics_events
    WHERE timestamp >= NOW() - INTERVAL '30 days'
)
SELECT ROUND((dau.count::float / NULLIF(mau.count, 0) * 100), 2) as stickiness_ratio
FROM dau, mau;

-- Onboarding Funnel (Last 30 Days)
SELECT
    date_trunc('day', timestamp) as date,
    COUNT(DISTINCT CASE WHEN event = 'onboarding_started' THEN user_id END) as started,
    COUNT(DISTINCT CASE WHEN event = 'onboarding_step_completed' AND properties->>'step' = '1' THEN user_id END) as step1,
    COUNT(DISTINCT CASE WHEN event = 'onboarding_step_completed' AND properties->>'step' = '2' THEN user_id END) as step2,
    COUNT(DISTINCT CASE WHEN event = 'onboarding_step_completed' AND properties->>'step' = '3' THEN user_id END) as step3,
    COUNT(DISTINCT CASE WHEN event = 'onboarding_step_completed' AND properties->>'step' = '4' THEN user_id END) as step4,
    COUNT(DISTINCT CASE WHEN event = 'onboarding_completed' THEN user_id END) as completed
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY date
ORDER BY date;

-- Onboarding Completion Rate
SELECT
    ROUND((COUNT(DISTINCT CASE WHEN event = 'onboarding_completed' THEN user_id END)::float /
           NULLIF(COUNT(DISTINCT CASE WHEN event = 'onboarding_started' THEN user_id END), 0) * 100), 2) as completion_rate
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- Average Time to Complete Onboarding
SELECT
    ROUND(AVG((properties->>'total_time_seconds')::float), 0) as avg_time_seconds,
    ROUND(AVG((properties->>'total_time_seconds')::float) / 60, 1) as avg_time_minutes
FROM analytics_events
WHERE event = 'onboarding_completed'
AND timestamp >= NOW() - INTERVAL '7 days';

-- Abandonment Rate by Step
SELECT
    properties->>'step_name' as step,
    properties->>'step' as step_number,
    COUNT(*) as abandonments,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'onboarding_abandoned'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY step, step_number
ORDER BY step_number::int;

-- Top Abandonment Reasons
SELECT
    properties->>'abandonment_reason' as reason,
    COUNT(*) as count,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'onboarding_abandoned'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY reason
ORDER BY count DESC
LIMIT 10;

-- ============================================================================
-- CONVERSION METRICS
-- ============================================================================

-- Recommendation Generation Rate (Last 24 Hours)
SELECT COUNT(*) as total_recommendations
FROM analytics_events
WHERE event = 'recommendation_generated'
AND timestamp >= NOW() - INTERVAL '24 hours';

-- Average Plans Shown per User
SELECT ROUND(AVG((properties->>'num_plans')::float), 1) as avg_plans
FROM analytics_events
WHERE event = 'recommendation_generated'
AND timestamp >= NOW() - INTERVAL '7 days';

-- Plan Card Expansion Rate
SELECT
    ROUND((COUNT(DISTINCT CASE WHEN event = 'plan_card_expanded' THEN user_id END)::float /
           NULLIF(COUNT(DISTINCT CASE WHEN event = 'recommendation_generated' THEN user_id END), 0) * 100), 2) as expansion_rate
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- Cost Breakdown View Rate
SELECT
    ROUND((COUNT(DISTINCT CASE WHEN event = 'cost_breakdown_viewed' THEN user_id END)::float /
           NULLIF(COUNT(DISTINCT CASE WHEN event = 'recommendation_generated' THEN user_id END), 0) * 100), 2) as view_rate
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- Average Savings Shown
SELECT
    ROUND(AVG((properties->>'total_savings')::float), 2) as avg_savings,
    ROUND(MIN((properties->>'total_savings')::float), 2) as min_savings,
    ROUND(MAX((properties->>'total_savings')::float), 2) as max_savings
FROM analytics_events
WHERE event = 'recommendation_generated'
AND properties->>'total_savings' IS NOT NULL
AND timestamp >= NOW() - INTERVAL '7 days';

-- Recommendations Generated Over Time (Last 7 Days)
SELECT
    date_trunc('hour', timestamp) as time,
    COUNT(*) as recommendations
FROM analytics_events
WHERE event = 'recommendation_generated'
AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY time
ORDER BY time;

-- User Profile Type Distribution
SELECT
    properties->>'user_profile_type' as profile_type,
    COUNT(*) as count,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'recommendation_generated'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY profile_type
ORDER BY count DESC;

-- Plan Interaction by Position
SELECT
    properties->>'position' as position,
    COUNT(*) as interactions,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event IN ('plan_card_expanded', 'plan_card_clicked')
AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY position
ORDER BY position::int;

-- Conversion Funnel Over Time
SELECT
    date_trunc('day', timestamp) as date,
    COUNT(DISTINCT CASE WHEN event = 'recommendation_generated' THEN user_id END) as generated,
    COUNT(DISTINCT CASE WHEN event = 'plan_card_expanded' THEN user_id END) as expanded,
    COUNT(DISTINCT CASE WHEN event = 'cost_breakdown_viewed' THEN user_id END) as viewed_breakdown,
    COUNT(DISTINCT CASE WHEN event = 'plan_card_clicked' THEN user_id END) as clicked
FROM analytics_events
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY date
ORDER BY date;

-- Top Recommended Plans
SELECT
    properties->>'plan_name' as plan,
    COUNT(*) as times_shown,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(CASE WHEN event = 'plan_card_expanded' THEN 1 END) as expansions,
    COUNT(CASE WHEN event = 'plan_card_clicked' THEN 1 END) as clicks
FROM analytics_events
WHERE event IN ('recommendation_generated', 'plan_card_expanded', 'plan_card_clicked')
AND properties->>'plan_name' IS NOT NULL
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY plan
ORDER BY times_shown DESC
LIMIT 10;

-- ============================================================================
-- SYSTEM PERFORMANCE METRICS
-- ============================================================================

-- API Response Time Percentiles (Last Hour)
SELECT
    ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY (properties->>'duration_ms')::float), 0) as p50,
    ROUND(percentile_cont(0.95) WITHIN GROUP (ORDER BY (properties->>'duration_ms')::float), 0) as p95,
    ROUND(percentile_cont(0.99) WITHIN GROUP (ORDER BY (properties->>'duration_ms')::float), 0) as p99
FROM analytics_events
WHERE event = 'api_request'
AND timestamp >= NOW() - INTERVAL '1 hour';

-- Error Rate (Last Hour)
SELECT
    ROUND((COUNT(CASE WHEN event = 'error_occurred' THEN 1 END)::float /
           NULLIF(COUNT(*), 0) * 100), 2) as error_rate,
    COUNT(CASE WHEN event = 'error_occurred' THEN 1 END) as total_errors,
    COUNT(*) as total_requests
FROM analytics_events
WHERE event IN ('api_request', 'error_occurred')
AND timestamp >= NOW() - INTERVAL '1 hour';

-- Cache Hit Rate (Last Hour)
SELECT
    ROUND((COUNT(CASE WHEN event = 'cache_hit' THEN 1 END)::float /
           NULLIF(COUNT(*), 0) * 100), 2) as hit_rate,
    COUNT(CASE WHEN event = 'cache_hit' THEN 1 END) as hits,
    COUNT(CASE WHEN event = 'cache_miss' THEN 1 END) as misses
FROM analytics_events
WHERE event IN ('cache_hit', 'cache_miss')
AND timestamp >= NOW() - INTERVAL '1 hour';

-- Slowest Endpoints (P95 Response Time)
SELECT
    properties->>'endpoint' as endpoint,
    COUNT(*) as requests,
    ROUND(percentile_cont(0.95) WITHIN GROUP (ORDER BY (properties->>'duration_ms')::float), 2) as p95_ms,
    ROUND(AVG((properties->>'duration_ms')::float), 2) as avg_ms
FROM analytics_events
WHERE event = 'api_request'
AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY endpoint
ORDER BY p95_ms DESC
LIMIT 10;

-- Error Breakdown by Type
SELECT
    properties->>'error_type' as error_type,
    properties->>'endpoint' as endpoint,
    COUNT(*) as count,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'error_occurred'
AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY error_type, endpoint
ORDER BY count DESC
LIMIT 10;

-- Peak Usage Times (Last 7 Days)
SELECT
    date_trunc('hour', timestamp) as time,
    COUNT(*) as requests
FROM analytics_events
WHERE event = 'api_request'
AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY time
ORDER BY requests DESC
LIMIT 20;

-- Request Distribution by Hour of Day (Last 7 Days)
SELECT
    EXTRACT(hour FROM timestamp) as hour,
    COUNT(*) as count,
    ROUND(AVG(COUNT(*)) OVER (), 0) as avg_count
FROM analytics_events
WHERE event = 'api_request'
AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY hour
ORDER BY hour;

-- ============================================================================
-- BUSINESS INTELLIGENCE METRICS
-- ============================================================================

-- Most Popular Plan Types
SELECT
    properties->>'plan_type' as plan_type,
    COUNT(*) as count,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'plan_card_clicked'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY plan_type
ORDER BY count DESC;

-- Risk Warnings by Type
SELECT
    properties->>'risk_type' as risk_type,
    COUNT(*) as count,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'risk_warning_triggered'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY risk_type
ORDER BY count DESC;

-- Risk Warning Severity Distribution
SELECT
    properties->>'severity' as severity,
    COUNT(*) as count,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'risk_warning_triggered'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY severity
ORDER BY count DESC;

-- User Property Type Distribution
SELECT
    properties->>'property_type' as property_type,
    COUNT(DISTINCT user_id) as users,
    ROUND((COUNT(DISTINCT user_id)::float / SUM(COUNT(DISTINCT user_id)) OVER () * 100), 2) as percentage
FROM analytics_events
WHERE event = 'user_created'
AND timestamp >= NOW() - INTERVAL '90 days'
GROUP BY property_type
ORDER BY users DESC;

-- Geographic Usage by ZIP Code (Top 50)
SELECT
    properties->>'zip_code' as zip,
    COUNT(DISTINCT user_id) as users
FROM analytics_events
WHERE event = 'user_created'
AND properties->>'zip_code' IS NOT NULL
AND timestamp >= NOW() - INTERVAL '90 days'
GROUP BY zip
ORDER BY users DESC
LIMIT 50;

-- Top ZIP Codes with Activation Rate
SELECT
    properties->>'zip_code' as zip_code,
    COUNT(DISTINCT user_id) as total_users,
    COUNT(DISTINCT CASE WHEN event = 'recommendation_generated' THEN user_id END) as active_users,
    ROUND((COUNT(DISTINCT CASE WHEN event = 'recommendation_generated' THEN user_id END)::float /
           NULLIF(COUNT(DISTINCT user_id), 0) * 100), 2) as activation_rate
FROM analytics_events
WHERE properties->>'zip_code' IS NOT NULL
AND timestamp >= NOW() - INTERVAL '90 days'
GROUP BY zip_code
ORDER BY total_users DESC
LIMIT 20;

-- User Preferences Trends
SELECT
    date_trunc('day', timestamp) as date,
    ROUND(AVG((properties->'preferences'->>'cost_priority')::float), 2) as avg_cost_priority,
    ROUND(AVG((properties->'preferences'->>'renewable_priority')::float), 2) as avg_renewable_priority,
    ROUND(AVG((properties->'preferences'->>'flexibility_priority')::float), 2) as avg_flexibility_priority
FROM analytics_events
WHERE event = 'user_preferences_updated'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY date
ORDER BY date;

-- Return User Rate
WITH user_sessions AS (
    SELECT
        user_id,
        COUNT(DISTINCT DATE(timestamp)) as session_days
    FROM analytics_events
    WHERE timestamp >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    ROUND((COUNT(CASE WHEN session_days > 1 THEN 1 END)::float /
           NULLIF(COUNT(*), 0) * 100), 2) as return_rate,
    COUNT(CASE WHEN session_days > 1 THEN 1 END) as return_users,
    COUNT(*) as total_users
FROM user_sessions;

-- File Upload Success Rate by Type
SELECT
    properties->>'file_type' as file_type,
    COUNT(CASE WHEN event = 'file_uploaded' THEN 1 END) as success,
    COUNT(CASE WHEN event = 'file_upload_failed' THEN 1 END) as failed,
    ROUND((COUNT(CASE WHEN event = 'file_uploaded' THEN 1 END)::float /
           NULLIF(COUNT(*), 0) * 100), 2) as success_rate
FROM analytics_events
WHERE event IN ('file_uploaded', 'file_upload_failed')
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY file_type;

-- User Segment Performance
SELECT
    properties->>'user_profile_type' as segment,
    COUNT(DISTINCT user_id) as users,
    ROUND(AVG((properties->>'total_savings')::float), 2) as avg_savings,
    COUNT(*) as total_recommendations
FROM analytics_events
WHERE event = 'recommendation_generated'
AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY segment
ORDER BY users DESC;

-- ============================================================================
-- COHORT ANALYSIS
-- ============================================================================

-- Weekly Cohort Retention
WITH cohorts AS (
    SELECT
        user_id,
        date_trunc('week', MIN(timestamp)) as cohort_week
    FROM analytics_events
    WHERE event = 'user_created'
    GROUP BY user_id
),
activity AS (
    SELECT
        user_id,
        date_trunc('week', timestamp) as activity_week
    FROM analytics_events
    GROUP BY user_id, activity_week
)
SELECT
    c.cohort_week,
    COUNT(DISTINCT c.user_id) as cohort_size,
    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week THEN c.user_id END) as week_0,
    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '1 week' THEN c.user_id END) as week_1,
    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '2 weeks' THEN c.user_id END) as week_2,
    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '3 weeks' THEN c.user_id END) as week_3,
    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '4 weeks' THEN c.user_id END) as week_4
FROM cohorts c
LEFT JOIN activity a ON c.user_id = a.user_id
WHERE c.cohort_week >= NOW() - INTERVAL '12 weeks'
GROUP BY c.cohort_week
ORDER BY c.cohort_week DESC;

-- ============================================================================
-- ADVANCED ANALYTICS
-- ============================================================================

-- Session Duration Analysis
WITH sessions AS (
    SELECT
        user_id,
        DATE(timestamp) as session_date,
        MIN(timestamp) as session_start,
        MAX(timestamp) as session_end,
        EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) as duration_seconds
    FROM analytics_events
    WHERE timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY user_id, session_date
)
SELECT
    ROUND(AVG(duration_seconds), 0) as avg_session_duration_seconds,
    ROUND(AVG(duration_seconds) / 60, 1) as avg_session_duration_minutes,
    ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY duration_seconds), 0) as median_session_duration_seconds
FROM sessions
WHERE duration_seconds > 0 AND duration_seconds < 3600; -- Filter out outliers

-- Events per Session
WITH sessions AS (
    SELECT
        user_id,
        DATE(timestamp) as session_date,
        COUNT(*) as events_count
    FROM analytics_events
    WHERE timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY user_id, session_date
)
SELECT
    ROUND(AVG(events_count), 1) as avg_events_per_session,
    ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY events_count), 0) as median_events_per_session
FROM sessions;

-- Time to First Recommendation
WITH user_first_activity AS (
    SELECT
        user_id,
        MIN(CASE WHEN event = 'onboarding_started' THEN timestamp END) as onboarding_start,
        MIN(CASE WHEN event = 'recommendation_generated' THEN timestamp END) as first_recommendation
    FROM analytics_events
    WHERE timestamp >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    ROUND(AVG(EXTRACT(EPOCH FROM (first_recommendation - onboarding_start)) / 60), 1) as avg_minutes,
    ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (first_recommendation - onboarding_start)) / 60), 1) as median_minutes
FROM user_first_activity
WHERE onboarding_start IS NOT NULL
AND first_recommendation IS NOT NULL;
