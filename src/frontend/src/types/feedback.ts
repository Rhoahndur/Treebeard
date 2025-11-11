/**
 * TypeScript interfaces for feedback system.
 *
 * Story 8.1: Feedback Collection UI
 */

export type FeedbackRating = 1 | 2 | 3 | 4 | 5;

export type FeedbackType =
  | 'helpful'
  | 'not_helpful'
  | 'selected'
  | 'did_not_select'
  | 'other';

export type SentimentType = 'positive' | 'neutral' | 'negative';

/**
 * Plan feedback submission data.
 */
export interface PlanFeedbackData {
  plan_id: string;
  recommendation_id?: string;
  rating: FeedbackRating;
  feedback_text?: string;
  feedback_type: FeedbackType;
}

/**
 * Recommendation feedback submission data.
 */
export interface RecommendationFeedbackData {
  recommendation_id: string;
  plan_id?: string;
  rating: FeedbackRating;
  feedback_text?: string;
  feedback_type: FeedbackType;
}

/**
 * Feedback submission response.
 */
export interface FeedbackSubmissionResponse {
  success: boolean;
  message: string;
  feedback_id: string;
}

/**
 * Single feedback record.
 */
export interface FeedbackRecord {
  id: string;
  user_id: string | null;
  recommendation_id: string | null;
  plan_id: string | null;
  rating: FeedbackRating;
  feedback_text: string | null;
  feedback_type: FeedbackType;
  sentiment_score: number | null;
  created_at: string;
}

/**
 * Aggregated feedback statistics.
 */
export interface FeedbackStats {
  total_feedback_count: number;
  average_rating: number;
  thumbs_up_count: number;
  thumbs_down_count: number;
  neutral_count: number;
  text_feedback_count: number;
  sentiment_breakdown: {
    positive: number;
    neutral: number;
    negative: number;
  };
}

/**
 * Plan-level feedback aggregation.
 */
export interface PlanFeedbackAggregation {
  plan_id: string;
  plan_name: string;
  supplier_name: string;
  total_feedback: number;
  average_rating: number;
  thumbs_up_count: number;
  thumbs_down_count: number;
  most_recent_feedback: string | null;
}

/**
 * Time-series data point for charts.
 */
export interface FeedbackTimeSeriesPoint {
  date: string;
  count: number;
  average_rating: number;
}

/**
 * Comprehensive analytics response.
 */
export interface FeedbackAnalyticsResponse {
  stats: FeedbackStats;
  time_series: FeedbackTimeSeriesPoint[];
  top_plans: PlanFeedbackAggregation[];
  recent_text_feedback: FeedbackRecord[];
}

/**
 * Feedback search parameters.
 */
export interface FeedbackSearchParams {
  plan_id?: string;
  min_rating?: FeedbackRating;
  max_rating?: FeedbackRating;
  has_text?: boolean;
  sentiment?: SentimentType;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

/**
 * Feedback search results.
 */
export interface FeedbackSearchResponse {
  results: FeedbackRecord[];
  total_count: number;
  limit: number;
  offset: number;
}

/**
 * Props for FeedbackWidget component.
 */
export interface FeedbackWidgetProps {
  /** ID of the plan being reviewed (for plan-specific feedback) */
  planId?: string;
  /** ID of the recommendation session (for overall feedback) */
  recommendationId?: string;
  /** Callback fired after successful submission */
  onSuccess?: () => void;
  /** Callback fired on error */
  onError?: (error: string) => void;
  /** Compact mode with minimal UI */
  compact?: boolean;
  /** Custom CSS class */
  className?: string;
}

/**
 * State for feedback widget.
 */
export interface FeedbackWidgetState {
  rating: FeedbackRating | null;
  feedbackText: string;
  isExpanded: boolean;
  isSubmitting: boolean;
  isSubmitted: boolean;
  error: string | null;
}
