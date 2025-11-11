import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  saveOnboardingData,
  loadOnboardingData,
  clearOnboardingData,
  hasSavedData,
  getLastSavedTime,
} from '../localStorage';
import type { OnboardingState } from '@/types/onboarding';

describe('localStorage Utilities', () => {
  const mockData: OnboardingState = {
    currentStep: 2,
    completedSteps: [1],
    user: {
      email: 'test@example.com',
      zip_code: '78701',
      property_type: 'residential',
    },
    current_plan: {
      supplier_name: 'TXU Energy',
      current_rate: 12.5,
      contract_end_date: '2025-12-31',
      early_termination_fee: 150,
      monthly_fee: 9.95,
    },
    usage_data: [],
    preferences: {
      cost_priority: 25,
      flexibility_priority: 25,
      renewable_priority: 25,
      rating_priority: 25,
    },
  };

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('saveOnboardingData', () => {
    it('should save data to localStorage', () => {
      saveOnboardingData(mockData);
      expect(localStorage.setItem).toHaveBeenCalled();
    });
  });

  describe('loadOnboardingData', () => {
    it('should return null if no data', () => {
      const data = loadOnboardingData();
      expect(data).toBeNull();
    });

    it('should return data if not expired', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 1);

      const storedData = {
        data: mockData,
        expiry: futureDate.toISOString(),
        lastSaved: new Date().toISOString(),
      };

      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(JSON.stringify(storedData));

      const data = loadOnboardingData();
      expect(data).toEqual(mockData);
    });

    it('should return null if data expired', () => {
      const pastDate = new Date();
      pastDate.setDate(pastDate.getDate() - 10);

      const storedData = {
        data: mockData,
        expiry: pastDate.toISOString(),
        lastSaved: new Date().toISOString(),
      };

      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(JSON.stringify(storedData));

      const data = loadOnboardingData();
      expect(data).toBeNull();
    });
  });

  describe('clearOnboardingData', () => {
    it('should clear data from localStorage', () => {
      clearOnboardingData();
      expect(localStorage.removeItem).toHaveBeenCalled();
    });
  });

  describe('hasSavedData', () => {
    it('should return false if no data', () => {
      expect(hasSavedData()).toBe(false);
    });

    it('should return true if valid data exists', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 1);

      const storedData = {
        data: mockData,
        expiry: futureDate.toISOString(),
        lastSaved: new Date().toISOString(),
      };

      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(JSON.stringify(storedData));

      expect(hasSavedData()).toBe(true);
    });
  });

  describe('getLastSavedTime', () => {
    it('should return null if no data', () => {
      expect(getLastSavedTime()).toBeNull();
    });

    it('should return last saved time', () => {
      const lastSaved = new Date().toISOString();
      const storedData = {
        data: mockData,
        expiry: new Date().toISOString(),
        lastSaved,
      };

      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(JSON.stringify(storedData));

      expect(getLastSavedTime()).toBe(lastSaved);
    });
  });
});
