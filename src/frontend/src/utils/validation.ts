import { z } from 'zod';

/**
 * Email validation schema
 */
export const emailSchema = z.string().email('Please enter a valid email address');

/**
 * ZIP code validation schema (US format: 5 digits or 5+4 digits)
 */
export const zipCodeSchema = z
  .string()
  .regex(/^\d{5}(-\d{4})?$/, 'ZIP code must be 5 digits (e.g., 78701) or 9 digits (e.g., 78701-1234)');

/**
 * Phone number validation (optional, US format)
 */
export const phoneSchema = z
  .string()
  .regex(/^(\+1|1)?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$/, 'Invalid phone number format')
  .optional();

/**
 * Positive number validation
 */
export const positiveNumberSchema = z.number().min(0, 'Value must be positive');

/**
 * Rate validation (cents per kWh, typically 5-50 cents)
 */
export const rateSchema = z
  .number()
  .min(0, 'Rate must be positive')
  .max(100, 'Rate seems too high (max 100 cents/kWh)');

/**
 * Date validation (ISO format)
 */
export const dateSchema = z.string().refine(
  (date) => {
    const parsed = new Date(date);
    return !isNaN(parsed.getTime());
  },
  { message: 'Invalid date format' }
);

/**
 * Future date validation
 */
export const futureDateSchema = z.string().refine(
  (date) => {
    const parsed = new Date(date);
    return parsed > new Date();
  },
  { message: 'Date must be in the future' }
);

/**
 * Preferences validation (must sum to 100)
 */
export const preferencesSchema = z
  .object({
    cost_priority: z.number().min(0).max(100),
    flexibility_priority: z.number().min(0).max(100),
    renewable_priority: z.number().min(0).max(100),
    rating_priority: z.number().min(0).max(100),
  })
  .refine(
    (data) => {
      const sum =
        data.cost_priority +
        data.flexibility_priority +
        data.renewable_priority +
        data.rating_priority;
      return Math.abs(sum - 100) < 0.01; // Allow small floating point errors
    },
    { message: 'Priorities must sum to 100%' }
  );

/**
 * User info step validation
 */
export const userInfoSchema = z.object({
  email: emailSchema,
  zip_code: zipCodeSchema,
  property_type: z.enum(['residential', 'commercial']),
});

/**
 * Current plan step validation
 */
export const currentPlanSchema = z.object({
  supplier_name: z.string().min(1, 'Supplier name is required'),
  current_rate: rateSchema,
  contract_end_date: z.string().min(1, 'Contract end date is required'),
  early_termination_fee: positiveNumberSchema,
  monthly_fee: positiveNumberSchema,
});

/**
 * Usage data validation
 */
export const usageDataSchema = z
  .array(
    z.object({
      month: dateSchema,
      kwh: positiveNumberSchema,
    })
  )
  .min(3, 'At least 3 months of usage data required')
  .max(24, 'Maximum 24 months of usage data allowed');

/**
 * Complete onboarding validation
 */
export const onboardingSchema = z.object({
  user: userInfoSchema,
  current_plan: currentPlanSchema,
  usage_data: usageDataSchema,
  preferences: preferencesSchema,
});

export type UserInfoFormData = z.infer<typeof userInfoSchema>;
export type CurrentPlanFormData = z.infer<typeof currentPlanSchema>;
export type PreferencesFormData = z.infer<typeof preferencesSchema>;
export type OnboardingFormData = z.infer<typeof onboardingSchema>;
