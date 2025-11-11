import type { OnboardingState } from '@/types/onboarding';

const STORAGE_KEY = 'treebeard_onboarding_data';
const EXPIRY_DAYS = 7;

/**
 * Save onboarding data to localStorage with expiry
 */
export function saveOnboardingData(data: OnboardingState): void {
  try {
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + EXPIRY_DAYS);

    const storageData = {
      data,
      expiry: expiryDate.toISOString(),
      lastSaved: new Date().toISOString(),
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(storageData));
  } catch (error) {
    console.error('Failed to save onboarding data:', error);
  }
}

/**
 * Load onboarding data from localStorage
 * Returns null if data doesn't exist or has expired
 */
export function loadOnboardingData(): OnboardingState | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    const { data, expiry } = JSON.parse(stored);

    // Check if data has expired
    const expiryDate = new Date(expiry);
    if (new Date() > expiryDate) {
      clearOnboardingData();
      return null;
    }

    return data;
  } catch (error) {
    console.error('Failed to load onboarding data:', error);
    return null;
  }
}

/**
 * Clear onboarding data from localStorage
 */
export function clearOnboardingData(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear onboarding data:', error);
  }
}

/**
 * Check if there is saved onboarding data
 */
export function hasSavedData(): boolean {
  return loadOnboardingData() !== null;
}

/**
 * Get the last saved timestamp
 */
export function getLastSavedTime(): string | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    const { lastSaved } = JSON.parse(stored);
    return lastSaved;
  } catch (error) {
    return null;
  }
}
