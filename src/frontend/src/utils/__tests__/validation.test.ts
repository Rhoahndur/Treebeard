import { describe, it, expect } from 'vitest';
import {
  emailSchema,
  zipCodeSchema,
  rateSchema,
  preferencesSchema,
  userInfoSchema,
  currentPlanSchema,
} from '../validation';

describe('Validation Schemas', () => {
  describe('emailSchema', () => {
    it('should validate correct email', () => {
      expect(() => emailSchema.parse('test@example.com')).not.toThrow();
      expect(() => emailSchema.parse('user.name+tag@example.co.uk')).not.toThrow();
    });

    it('should reject invalid email', () => {
      expect(() => emailSchema.parse('invalid-email')).toThrow();
      expect(() => emailSchema.parse('@example.com')).toThrow();
      expect(() => emailSchema.parse('test@')).toThrow();
    });
  });

  describe('zipCodeSchema', () => {
    it('should validate 5-digit ZIP code', () => {
      expect(() => zipCodeSchema.parse('78701')).not.toThrow();
      expect(() => zipCodeSchema.parse('12345')).not.toThrow();
    });

    it('should validate ZIP+4 format', () => {
      expect(() => zipCodeSchema.parse('78701-1234')).not.toThrow();
    });

    it('should reject invalid ZIP codes', () => {
      expect(() => zipCodeSchema.parse('1234')).toThrow(); // Too short
      expect(() => zipCodeSchema.parse('123456')).toThrow(); // Too long
      expect(() => zipCodeSchema.parse('abcde')).toThrow(); // Letters
    });
  });

  describe('rateSchema', () => {
    it('should validate positive rates', () => {
      expect(() => rateSchema.parse(12.5)).not.toThrow();
      expect(() => rateSchema.parse(0)).not.toThrow();
      expect(() => rateSchema.parse(50)).not.toThrow();
    });

    it('should reject negative rates', () => {
      expect(() => rateSchema.parse(-5)).toThrow();
    });

    it('should reject rates over 100', () => {
      expect(() => rateSchema.parse(150)).toThrow();
    });
  });

  describe('preferencesSchema', () => {
    it('should validate preferences that sum to 100', () => {
      const preferences = {
        cost_priority: 25,
        flexibility_priority: 25,
        renewable_priority: 25,
        rating_priority: 25,
      };
      expect(() => preferencesSchema.parse(preferences)).not.toThrow();
    });

    it('should reject preferences that do not sum to 100', () => {
      const preferences = {
        cost_priority: 30,
        flexibility_priority: 30,
        renewable_priority: 30,
        rating_priority: 30,
      };
      expect(() => preferencesSchema.parse(preferences)).toThrow();
    });

    it('should reject preferences with negative values', () => {
      const preferences = {
        cost_priority: -10,
        flexibility_priority: 40,
        renewable_priority: 40,
        rating_priority: 30,
      };
      expect(() => preferencesSchema.parse(preferences)).toThrow();
    });
  });

  describe('userInfoSchema', () => {
    it('should validate complete user info', () => {
      const userInfo = {
        email: 'test@example.com',
        zip_code: '78701',
        property_type: 'residential' as const,
      };
      expect(() => userInfoSchema.parse(userInfo)).not.toThrow();
    });

    it('should reject invalid property type', () => {
      const userInfo = {
        email: 'test@example.com',
        zip_code: '78701',
        property_type: 'invalid',
      };
      expect(() => userInfoSchema.parse(userInfo)).toThrow();
    });
  });

  describe('currentPlanSchema', () => {
    it('should validate complete current plan', () => {
      const plan = {
        supplier_name: 'TXU Energy',
        current_rate: 12.5,
        contract_end_date: '2025-12-31',
        early_termination_fee: 150,
        monthly_fee: 9.95,
      };
      expect(() => currentPlanSchema.parse(plan)).not.toThrow();
    });

    it('should reject empty supplier name', () => {
      const plan = {
        supplier_name: '',
        current_rate: 12.5,
        contract_end_date: '2025-12-31',
        early_termination_fee: 150,
        monthly_fee: 9.95,
      };
      expect(() => currentPlanSchema.parse(plan)).toThrow();
    });
  });
});
