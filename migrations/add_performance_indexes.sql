-- Performance Indexes Migration
-- Story 7.2 - Epic 7: Performance Optimization
--
-- Adds optimized indexes for common query patterns to achieve
-- sub-100ms query performance (P95 target).
--
-- Target: All queries < 100ms (P95)

-- ============================================================================
-- PLAN CATALOG INDEXES
-- ============================================================================

-- Composite index for region and active status filtering
-- Used in: Finding available plans by region
CREATE INDEX IF NOT EXISTS idx_plan_catalog_region_active
ON plan_catalog(available_regions, is_active)
WHERE is_active = true;

-- Partial index for active plans only (reduces index size)
-- Used in: Filtering active plans in recommendations
CREATE INDEX IF NOT EXISTS idx_active_plans
ON plan_catalog(renewable_percentage, contract_length_months)
WHERE is_active = true;

-- GIN index for JSONB rate_structure queries
-- Used in: Searching rate structures, time-of-use plans
CREATE INDEX IF NOT EXISTS idx_plan_rate_structure_gin
ON plan_catalog USING gin(rate_structure);

-- Index for supplier lookups
-- Used in: Joining plans with supplier data
CREATE INDEX IF NOT EXISTS idx_plan_supplier
ON plan_catalog(supplier_id);

-- Index for plan type filtering
-- Used in: Filtering by plan type (fixed, variable, etc.)
CREATE INDEX IF NOT EXISTS idx_plan_type
ON plan_catalog(plan_type, is_active);

-- ============================================================================
-- USER INDEXES
-- ============================================================================

-- Index for user lookup by email
-- Used in: Authentication, user retrieval
CREATE INDEX IF NOT EXISTS idx_users_email
ON users(email);

-- Index for user region/zip filtering
-- Used in: Finding users by location
CREATE INDEX IF NOT EXISTS idx_users_location
ON users(zip_code, property_type);

-- Index for user creation time
-- Used in: Filtering recent users, analytics
CREATE INDEX IF NOT EXISTS idx_users_created
ON users(created_at DESC);

-- ============================================================================
-- USAGE HISTORY INDEXES
-- ============================================================================

-- Composite index for user usage queries
-- Used in: Fetching user's usage history (most common query)
CREATE INDEX IF NOT EXISTS idx_usage_user_date
ON usage_history(user_id, usage_date DESC);

-- Index for date-based filtering
-- Used in: Analytics queries, time-series analysis
CREATE INDEX IF NOT EXISTS idx_usage_date
ON usage_history(usage_date DESC);

-- Index for data source filtering
-- Used in: Filtering by data upload method
CREATE INDEX IF NOT EXISTS idx_usage_source
ON usage_history(data_source);

-- ============================================================================
-- USER PREFERENCES INDEXES
-- ============================================================================

-- Index for user preferences lookup
-- Used in: Fetching user preferences during recommendations
CREATE INDEX IF NOT EXISTS idx_preferences_user
ON user_preferences(user_id);

-- ============================================================================
-- RECOMMENDATIONS INDEXES
-- ============================================================================

-- Composite index for user recommendations
-- Used in: Fetching active recommendations for a user
CREATE INDEX IF NOT EXISTS idx_recommendations_user_expires
ON recommendations(user_id, expires_at DESC);

-- Index for expiration cleanup
-- Used in: Background job to clean expired recommendations
CREATE INDEX IF NOT EXISTS idx_recommendations_expires
ON recommendations(expires_at)
WHERE expires_at < NOW();

-- ============================================================================
-- RECOMMENDATION PLANS INDEXES
-- ============================================================================

-- Foreign key index for recommendation lookup
-- Used in: Joining recommendation with plans
CREATE INDEX IF NOT EXISTS idx_rec_plans_recommendation
ON recommendation_plans(recommendation_id);

-- Foreign key index for plan lookup
-- Used in: Finding recommendations for a specific plan
CREATE INDEX IF NOT EXISTS idx_rec_plans_plan
ON recommendation_plans(plan_id);

-- Composite index for ranked plans
-- Used in: Ordering plans by rank within a recommendation
CREATE INDEX IF NOT EXISTS idx_rec_plans_rec_rank
ON recommendation_plans(recommendation_id, rank);

-- ============================================================================
-- CURRENT PLANS INDEXES
-- ============================================================================

-- Index for user's current plan lookup
-- Used in: Fetching user's current plan for comparison
CREATE INDEX IF NOT EXISTS idx_current_plans_user
ON current_plans(user_id);

-- Index for contract end date
-- Used in: Finding users with expiring contracts
CREATE INDEX IF NOT EXISTS idx_current_plans_contract_end
ON current_plans(contract_end_date)
WHERE contract_end_date >= NOW();

-- ============================================================================
-- FEEDBACK INDEXES
-- ============================================================================

-- Composite index for user feedback
-- Used in: Fetching user's feedback history
CREATE INDEX IF NOT EXISTS idx_feedback_user_created
ON feedback(user_id, created_at DESC);

-- Index for recommendation feedback
-- Used in: Analyzing feedback for specific recommendations
CREATE INDEX IF NOT EXISTS idx_feedback_recommendation
ON feedback(recommendation_id);

-- Index for plan feedback
-- Used in: Analyzing feedback for specific plans
CREATE INDEX IF NOT EXISTS idx_feedback_plan
ON feedback(plan_id);

-- Index for feedback type
-- Used in: Filtering by feedback type
CREATE INDEX IF NOT EXISTS idx_feedback_type
ON feedback(feedback_type, created_at DESC);

-- ============================================================================
-- SUPPLIERS INDEXES
-- ============================================================================

-- Index for supplier name lookup
-- Used in: Searching suppliers by name
CREATE INDEX IF NOT EXISTS idx_suppliers_name
ON suppliers(supplier_name);

-- Index for supplier rating
-- Used in: Filtering high-rated suppliers
CREATE INDEX IF NOT EXISTS idx_suppliers_rating
ON suppliers(average_rating DESC);

-- ============================================================================
-- ANALYZE TABLES
-- ============================================================================

-- Update table statistics for query planner
ANALYZE users;
ANALYZE usage_history;
ANALYZE user_preferences;
ANALYZE current_plans;
ANALYZE plan_catalog;
ANALYZE suppliers;
ANALYZE recommendations;
ANALYZE recommendation_plans;
ANALYZE feedback;

-- ============================================================================
-- PERFORMANCE NOTES
-- ============================================================================

-- Expected improvements:
-- 1. Plan catalog queries: 150ms -> <50ms
-- 2. User usage history: 120ms -> <30ms
-- 3. Recommendation retrieval: 200ms -> <100ms
-- 4. JOIN operations: 50% reduction in time
--
-- Index maintenance:
-- - Indexes are automatically maintained
-- - VACUUM ANALYZE should run weekly
-- - Monitor index bloat monthly
--
-- Query optimization tips:
-- 1. Always filter by indexed columns first
-- 2. Use EXPLAIN ANALYZE to verify index usage
-- 3. Avoid SELECT * - specify columns
-- 4. Use covering indexes where possible
-- 5. Consider partial indexes for filtered queries
