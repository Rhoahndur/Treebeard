// Onboarding form types based on API contract

export type PropertyType = 'residential' | 'commercial';

export interface MonthlyUsage {
  month: string; // ISO date (first day of month)
  kwh: number;
}

export interface UserInfo {
  email: string;
  zip_code: string;
  property_type: PropertyType;
}

export interface CurrentPlan {
  supplier_name: string;
  current_rate: number; // cents per kWh
  contract_end_date: string; // ISO date
  early_termination_fee: number;
  monthly_fee: number;
}

export interface Preferences {
  cost_priority: number; // 0-100
  flexibility_priority: number; // 0-100
  renewable_priority: number; // 0-100
  rating_priority: number; // 0-100
}

export interface OnboardingData {
  user: UserInfo;
  current_plan: CurrentPlan;
  usage_data: MonthlyUsage[];
  preferences: Preferences;
}

// Form step types
export type OnboardingStep = 1 | 2 | 3 | 4;

export interface OnboardingState extends OnboardingData {
  currentStep: OnboardingStep;
  completedSteps: OnboardingStep[];
  lastSaved?: string; // ISO timestamp
}

// Preset profile types
export type PresetProfile = 'budget' | 'eco' | 'flexible' | 'balanced';

export interface PresetConfig {
  name: string;
  description: string;
  preferences: Preferences;
}
