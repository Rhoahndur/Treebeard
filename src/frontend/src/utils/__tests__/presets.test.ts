import { describe, it, expect } from 'vitest';
import {
  normalizePreferences,
  adjustPreferences,
  getPreset,
  PRESET_CONFIGS,
} from '../presets';
import type { Preferences } from '@/types/onboarding';

describe('Preset Utilities', () => {
  describe('normalizePreferences', () => {
    it('should normalize preferences to sum to 100', () => {
      const preferences: Preferences = {
        cost_priority: 30,
        flexibility_priority: 30,
        renewable_priority: 30,
        rating_priority: 30,
      };

      const normalized = normalizePreferences(preferences);
      const sum =
        normalized.cost_priority +
        normalized.flexibility_priority +
        normalized.renewable_priority +
        normalized.rating_priority;

      expect(sum).toBe(100);
    });

    it('should return balanced if all are 0', () => {
      const preferences: Preferences = {
        cost_priority: 0,
        flexibility_priority: 0,
        renewable_priority: 0,
        rating_priority: 0,
      };

      const normalized = normalizePreferences(preferences);

      expect(normalized.cost_priority).toBe(25);
      expect(normalized.flexibility_priority).toBe(25);
      expect(normalized.renewable_priority).toBe(25);
      expect(normalized.rating_priority).toBe(25);
    });
  });

  describe('adjustPreferences', () => {
    it('should adjust other preferences when one changes', () => {
      const initial: Preferences = {
        cost_priority: 25,
        flexibility_priority: 25,
        renewable_priority: 25,
        rating_priority: 25,
      };

      const adjusted = adjustPreferences(initial, 'cost_priority', 50);

      expect(adjusted.cost_priority).toBe(50);

      const sum =
        adjusted.cost_priority +
        adjusted.flexibility_priority +
        adjusted.renewable_priority +
        adjusted.rating_priority;

      expect(sum).toBe(100);
    });

    it('should return same if no change', () => {
      const initial: Preferences = {
        cost_priority: 25,
        flexibility_priority: 25,
        renewable_priority: 25,
        rating_priority: 25,
      };

      const adjusted = adjustPreferences(initial, 'cost_priority', 25);

      expect(adjusted).toEqual(initial);
    });
  });

  describe('getPreset', () => {
    it('should return budget preset', () => {
      const preset = getPreset('budget');
      expect(preset.cost_priority).toBe(60);
    });

    it('should return eco preset', () => {
      const preset = getPreset('eco');
      expect(preset.renewable_priority).toBe(60);
    });

    it('should return flexible preset', () => {
      const preset = getPreset('flexible');
      expect(preset.flexibility_priority).toBe(60);
    });

    it('should return balanced preset', () => {
      const preset = getPreset('balanced');
      expect(preset.cost_priority).toBe(25);
      expect(preset.flexibility_priority).toBe(25);
      expect(preset.renewable_priority).toBe(25);
      expect(preset.rating_priority).toBe(25);
    });
  });

  describe('PRESET_CONFIGS', () => {
    it('should have all presets sum to 100', () => {
      Object.values(PRESET_CONFIGS).forEach((config) => {
        const sum =
          config.preferences.cost_priority +
          config.preferences.flexibility_priority +
          config.preferences.renewable_priority +
          config.preferences.rating_priority;
        expect(sum).toBe(100);
      });
    });
  });
});
