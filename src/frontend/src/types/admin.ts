/**
 * Admin Dashboard TypeScript Type Definitions
 *
 * This file contains all TypeScript interfaces and types used throughout
 * the admin dashboard, including users, recommendations, plans, audit logs,
 * and statistics.
 */

// ============================================================================
// User Management Types
// ============================================================================

/**
 * User role enumeration
 */
export type UserRole = 'user' | 'admin';

/**
 * User status enumeration
 */
export type UserStatus = 'active' | 'inactive';

/**
 * Admin user interface
 */
export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  status: UserStatus;
  registration_date: string;
  last_login: string | null;
  recommendation_count: number;
  feedback_count: number;
}

/**
 * User activity history item
 */
export interface UserActivity {
  id: string;
  user_id: string;
  action_type: 'recommendation' | 'feedback' | 'login' | 'profile_update';
  timestamp: string;
  details: Record<string, any>;
}

/**
 * User details with extended information
 */
export interface UserDetails extends AdminUser {
  activity_history: UserActivity[];
  usage_statistics: {
    total_recommendations: number;
    avg_recommendations_per_month: number;
    total_feedback_submitted: number;
    last_recommendation_date: string | null;
  };
}

/**
 * User filters for search and filtering
 */
export interface UserFilters {
  search?: string;
  role?: UserRole | 'all';
  status?: UserStatus | 'all';
  page?: number;
  limit?: number;
  sort_by?: 'email' | 'full_name' | 'registration_date' | 'last_login';
  sort_order?: 'asc' | 'desc';
}

/**
 * Paginated user response
 */
export interface PaginatedUserResponse {
  users: AdminUser[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ============================================================================
// Recommendation Management Types
// ============================================================================

/**
 * Profile type enumeration
 */
export type ProfileType = 'baseline' | 'seasonal_high_summer' | 'seasonal_high_winter' | 'consistent_high' | 'consistent_low';

/**
 * Feedback sentiment enumeration
 */
export type FeedbackSentiment = 'positive' | 'neutral' | 'negative';

/**
 * Admin recommendation interface
 */
export interface AdminRecommendation {
  id: string;
  user_id: string;
  user_email: string;
  generated_at: string;
  profile_type: ProfileType;
  plans_recommended_count: number;
  has_feedback: boolean;
  feedback_sentiment?: FeedbackSentiment;
  feedback_text?: string;
}

/**
 * Full recommendation details
 */
export interface RecommendationDetails {
  id: string;
  user_id: string;
  user_email: string;
  generated_at: string;
  user_profile: {
    profile_type: ProfileType;
    projected_annual_kwh: number;
    mean_monthly_kwh: number;
    has_seasonal_pattern: boolean;
    confidence_score: number;
  };
  user_data: {
    zip_code: string;
    property_type: 'residential' | 'commercial';
  };
  usage_data: Array<{
    month: string;
    kwh: number;
  }>;
  preferences: {
    cost_priority: number;
    flexibility_priority: number;
    renewable_priority: number;
    rating_priority: number;
  };
  recommended_plans: Array<{
    rank: number;
    plan_id: string;
    plan_name: string;
    supplier_name: string;
    plan_type: string;
    scores: {
      cost_score: number;
      flexibility_score: number;
      renewable_score: number;
      rating_score: number;
      composite_score: number;
    };
    projected_annual_cost: number;
    projected_monthly_cost: number;
    average_rate_per_kwh: number;
    savings?: {
      annual_savings: number;
      savings_percentage: number;
      monthly_savings: number;
      break_even_months?: number;
    };
    explanation: string;
    key_differentiators: string[];
    trade_offs: string[];
  }>;
  warnings: string[];
  total_plans_analyzed: number;
}

/**
 * Recommendation filters
 */
export interface RecommendationFilters {
  user_search?: string;
  profile_type?: ProfileType | 'all';
  has_feedback?: boolean | 'all';
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
  sort_by?: 'generated_at' | 'user_email' | 'profile_type';
  sort_order?: 'asc' | 'desc';
}

/**
 * Paginated recommendation response
 */
export interface PaginatedRecommendationResponse {
  recommendations: AdminRecommendation[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ============================================================================
// Plan Catalog Management Types
// ============================================================================

/**
 * Plan type enumeration
 */
export type PlanType = 'fixed' | 'variable' | 'tiered' | 'time_of_use';

/**
 * Plan status enumeration
 */
export type PlanStatus = 'active' | 'inactive';

/**
 * Tiered rate structure
 */
export interface TieredRate {
  tier: number;
  kwh_min: number;
  kwh_max: number | null;
  rate: number;
}

/**
 * Time of use rate structure
 */
export interface TimeOfUseRate {
  period: 'peak' | 'off_peak' | 'shoulder';
  hours: string;
  rate: number;
  days?: string[];
}

/**
 * Admin plan interface
 */
export interface AdminPlan {
  id: string;
  plan_name: string;
  supplier_name: string;
  plan_type: PlanType;
  base_rate: number;
  tiered_rates?: TieredRate[];
  time_of_use_rates?: TimeOfUseRate[];
  contract_length_months: number;
  early_termination_fee: number;
  renewable_percentage: number;
  min_usage_kwh?: number;
  max_usage_kwh?: number;
  regions: string[];
  available_from: string;
  available_to: string | null;
  supplier_rating: number;
  customer_service_rating: number;
  monthly_fee?: number;
  status: PlanStatus;
  created_at: string;
  updated_at: string;
  description?: string;
}

/**
 * Plan form data for creating/editing
 */
export interface PlanFormData {
  plan_name: string;
  supplier_name: string;
  plan_type: PlanType;
  base_rate: number;
  tiered_rates?: string; // JSON string
  time_of_use_rates?: string; // JSON string
  contract_length_months: number;
  early_termination_fee: number;
  renewable_percentage: number;
  min_usage_kwh?: number;
  max_usage_kwh?: number;
  regions: string[];
  available_from: string;
  available_to?: string;
  supplier_rating: number;
  customer_service_rating: number;
  monthly_fee?: number;
  description?: string;
}

/**
 * Plan filters
 */
export interface PlanFilters {
  search?: string;
  plan_type?: PlanType | 'all';
  status?: PlanStatus | 'all';
  supplier?: string;
  page?: number;
  limit?: number;
  sort_by?: 'plan_name' | 'supplier_name' | 'base_rate' | 'contract_length_months' | 'renewable_percentage';
  sort_order?: 'asc' | 'desc';
}

/**
 * Paginated plan response
 */
export interface PaginatedPlanResponse {
  plans: AdminPlan[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ============================================================================
// Audit Log Types
// ============================================================================

/**
 * Audit action enumeration
 */
export type AuditAction =
  | 'user_role_updated'
  | 'user_deleted'
  | 'plan_created'
  | 'plan_updated'
  | 'plan_deleted'
  | 'plan_duplicated'
  | 'bulk_plans_activated'
  | 'bulk_plans_deactivated';

/**
 * Resource type enumeration
 */
export type ResourceType = 'user' | 'plan' | 'recommendation' | 'system';

/**
 * Audit log entry
 */
export interface AuditLogEntry {
  id: string;
  timestamp: string;
  admin_user_id: string;
  admin_email: string;
  action: AuditAction;
  resource_type: ResourceType;
  resource_id: string;
  details: Record<string, any>;
  ip_address: string;
}

/**
 * Audit log filters
 */
export interface AuditLogFilters {
  admin_user?: string;
  action?: AuditAction | AuditAction[] | 'all';
  resource_type?: ResourceType | 'all';
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
  sort_by?: 'timestamp' | 'admin_email' | 'action';
  sort_order?: 'asc' | 'desc';
}

/**
 * Paginated audit log response
 */
export interface PaginatedAuditLogResponse {
  logs: AuditLogEntry[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ============================================================================
// Statistics & Dashboard Types
// ============================================================================

/**
 * Dashboard statistics
 */
export interface DashboardStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  total_recommendations: number;
  total_feedback: number;
  avg_recommendations_per_user: number;
  cache_hit_rate: number;
  api_p95_latency_ms: number;
}

/**
 * Time series data point
 */
export interface TimeSeriesData {
  date: string;
  value: number;
}

/**
 * Feedback sentiment breakdown
 */
export interface FeedbackSentimentBreakdown {
  positive: number;
  neutral: number;
  negative: number;
}

/**
 * Dashboard charts data
 */
export interface DashboardChartsData {
  recommendations_over_time: TimeSeriesData[];
  user_growth: TimeSeriesData[];
  feedback_sentiment: FeedbackSentimentBreakdown;
}

/**
 * Recent activity item
 */
export interface RecentActivity {
  id: string;
  user_email: string;
  action: string;
  timestamp: string;
  details?: string;
}

/**
 * Complete dashboard data
 */
export interface DashboardData {
  stats: DashboardStats;
  charts: DashboardChartsData;
  recent_activity: RecentActivity[];
}

// ============================================================================
// Table & UI Types
// ============================================================================

/**
 * Sort direction
 */
export type SortDirection = 'asc' | 'desc';

/**
 * Column definition for DataTable
 */
export interface ColumnDef<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

/**
 * Confirmation dialog props
 */
export interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  variant?: 'danger' | 'warning' | 'info';
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Toast notification types
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

/**
 * Toast notification
 */
export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}
