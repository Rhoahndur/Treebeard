/**
 * TypeScript types for the TreeBeard Recommendation API
 * Based on Epic 3 API Contract
 */

export interface UsageData {
  month: string;  // ISO date (first day of month)
  kwh: number;    // >= 0
}

export interface UserData {
  zip_code: string;        // 5-10 digits
  property_type: 'residential' | 'commercial';
}

export interface Preferences {
  cost_priority: number;           // 0-100
  flexibility_priority: number;    // 0-100
  renewable_priority: number;      // 0-100
  rating_priority: number;         // 0-100
}

export interface CurrentPlan {
  plan_name?: string;
  supplier_name?: string;
  current_rate?: number;           // cents per kWh
  contract_end_date?: string;      // ISO date
  early_termination_fee?: number;  // >= 0
  plan_start_date?: string;        // ISO date
}

export interface GenerateRecommendationRequest {
  user_data: UserData;
  usage_data: UsageData[];  // 3-24 months
  preferences: Preferences;
  current_plan?: CurrentPlan;
}

export interface UserProfile {
  profile_type: string;              // baseline, seasonal, high_user, etc.
  projected_annual_kwh: number;
  mean_monthly_kwh: number;
  has_seasonal_pattern: boolean;
  confidence_score: number;          // 0-1
}

export interface PlanScores {
  cost_score: number;              // 0-100
  flexibility_score: number;       // 0-100
  renewable_score: number;         // 0-100
  rating_score: number;            // 0-100
  composite_score: number;         // 0-100
}

export interface Savings {
  annual_savings: number;
  savings_percentage: number;
  monthly_savings: number;
  break_even_months?: number;
}

export interface RankedPlan {
  rank: number;                      // 1-3
  plan_id: string;                   // UUID
  plan_name: string;
  supplier_name: string;
  plan_type: string;
  scores: PlanScores;
  projected_annual_cost: number;
  projected_monthly_cost: number;
  average_rate_per_kwh: number;
  savings?: Savings;
  contract_length_months: number;    // 0 = month-to-month
  early_termination_fee: number;
  renewable_percentage: number;      // 0-100
  monthly_fee?: number;
  explanation: string;               // AI-generated explanation
  key_differentiators: string[];
  trade_offs: string[];
}

export interface GenerateRecommendationResponse {
  recommendation_id: string;  // UUID
  user_profile: UserProfile;
  top_plans: RankedPlan[];
  generated_at: string;                // ISO timestamp
  total_plans_analyzed: number;
  warnings: string[];
}

export interface MonthlyTotal {
  month: string;  // ISO date
  total_cost: number;
}

export interface SavingsAnalysis {
  annual_savings: number;
  savings_percentage: number;
  monthly_breakdown: MonthlyTotal[];
  break_even_months: number;
}

// UI-specific types
export type SavingsLevel = 'high' | 'medium' | 'low' | 'none';

export interface UIState {
  isLoading: boolean;
  error: string | null;
  recommendation: GenerateRecommendationResponse | null;
}
