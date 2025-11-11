import type { Preferences, PresetProfile, PresetConfig } from '@/types/onboarding';

/**
 * Preset preference configurations
 */
export const PRESET_CONFIGS: Record<PresetProfile, PresetConfig> = {
  budget: {
    name: 'Budget Focus',
    description: 'Minimize costs above all else',
    preferences: {
      cost_priority: 60,
      flexibility_priority: 15,
      renewable_priority: 15,
      rating_priority: 10,
    },
  },
  eco: {
    name: 'Eco-Conscious',
    description: 'Prioritize renewable energy',
    preferences: {
      cost_priority: 15,
      flexibility_priority: 10,
      renewable_priority: 60,
      rating_priority: 15,
    },
  },
  flexible: {
    name: 'Flexible',
    description: 'Value contract flexibility',
    preferences: {
      cost_priority: 15,
      flexibility_priority: 60,
      renewable_priority: 15,
      rating_priority: 10,
    },
  },
  balanced: {
    name: 'Balanced',
    description: 'Equal weight on all factors',
    preferences: {
      cost_priority: 25,
      flexibility_priority: 25,
      renewable_priority: 25,
      rating_priority: 25,
    },
  },
};

/**
 * Normalize preferences to sum to 100
 */
export function normalizePreferences(preferences: Preferences): Preferences {
  const sum =
    preferences.cost_priority +
    preferences.flexibility_priority +
    preferences.renewable_priority +
    preferences.rating_priority;

  if (sum === 0) {
    // If all are 0, return balanced
    return PRESET_CONFIGS.balanced.preferences;
  }

  // Normalize to 100
  const factor = 100 / sum;

  return {
    cost_priority: Math.round(preferences.cost_priority * factor),
    flexibility_priority: Math.round(preferences.flexibility_priority * factor),
    renewable_priority: Math.round(preferences.renewable_priority * factor),
    rating_priority: Math.round(preferences.rating_priority * factor),
  };
}

/**
 * Adjust preferences when one slider changes
 * Distributes the difference among other sliders proportionally
 */
export function adjustPreferences(
  preferences: Preferences,
  changedKey: keyof Preferences,
  newValue: number
): Preferences {
  const oldValue = preferences[changedKey];
  const difference = oldValue - newValue;

  // If difference is 0, no adjustment needed
  if (difference === 0) {
    return preferences;
  }

  const otherKeys = (Object.keys(preferences) as Array<keyof Preferences>).filter(
    (key) => key !== changedKey
  );

  // Calculate total of other preferences
  const otherTotal = otherKeys.reduce((sum, key) => sum + preferences[key], 0);

  const newPreferences = { ...preferences, [changedKey]: newValue };

  if (otherTotal === 0) {
    // If others are all 0, distribute equally
    const equalShare = Math.floor(difference / otherKeys.length);
    const remainder = difference % otherKeys.length;

    otherKeys.forEach((key, index) => {
      newPreferences[key] = equalShare + (index === 0 ? remainder : 0);
    });
  } else {
    // Distribute proportionally
    let remainingDifference = difference;

    otherKeys.forEach((key, index) => {
      if (index === otherKeys.length - 1) {
        // Last key gets the remainder to ensure sum = 100
        newPreferences[key] = preferences[key] + remainingDifference;
      } else {
        const proportion = preferences[key] / otherTotal;
        const adjustment = Math.round(difference * proportion);
        newPreferences[key] = preferences[key] + adjustment;
        remainingDifference -= adjustment;
      }
    });
  }

  // Ensure all values are within 0-100 and sum to 100
  return normalizePreferences(newPreferences);
}

/**
 * Get preset by profile type
 */
export function getPreset(profile: PresetProfile): Preferences {
  return { ...PRESET_CONFIGS[profile].preferences };
}
