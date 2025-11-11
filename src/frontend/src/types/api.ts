// API types based on Epic 3 API contract

export interface GenerateRecommendationRequest {
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
  current_plan?: {
    plan_name?: string;
    supplier_name?: string;
    current_rate?: number;
    contract_end_date?: string;
    early_termination_fee?: number;
    plan_start_date?: string;
  };
}

export interface PlanScores {
  cost_score: number;
  flexibility_score: number;
  renewable_score: number;
  rating_score: number;
  composite_score: number;
}

export interface PlanSavings {
  annual_savings: number;
  savings_percentage: number;
  monthly_savings: number;
  break_even_months?: number;
}

export interface RecommendedPlan {
  rank: number;
  plan_id: string;
  plan_name: string;
  supplier_name: string;
  plan_type: string;
  scores: PlanScores;
  projected_annual_cost: number;
  projected_monthly_cost: number;
  average_rate_per_kwh: number;
  savings?: PlanSavings;
  contract_length_months: number;
  early_termination_fee: number;
  renewable_percentage: number;
  monthly_fee?: number;
  explanation: string;
  key_differentiators: string[];
  trade_offs: string[];
}

export interface UserProfile {
  profile_type: string;
  projected_annual_kwh: number;
  mean_monthly_kwh: number;
  has_seasonal_pattern: boolean;
  confidence_score: number;
}

export interface GenerateRecommendationResponse {
  recommendation_id: string;
  user_profile: UserProfile;
  top_plans: RecommendedPlan[];
  generated_at: string;
  total_plans_analyzed: number;
  warnings: string[];
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: any;
  request_id?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
}
