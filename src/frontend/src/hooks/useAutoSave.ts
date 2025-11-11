import { useEffect, useRef, useState, useCallback } from 'react';
import type { OnboardingState } from '@/types/onboarding';
import { saveOnboardingData, getLastSavedTime } from '@/utils/localStorage';

interface UseAutoSaveOptions {
  delay?: number; // Debounce delay in milliseconds
  enabled?: boolean;
}

interface UseAutoSaveReturn {
  isSaving: boolean;
  lastSaved: string | null;
  save: () => void;
}

/**
 * Auto-save hook with debouncing
 * Automatically saves onboarding data to localStorage after a delay
 */
export function useAutoSave(
  data: OnboardingState,
  options: UseAutoSaveOptions = {}
): UseAutoSaveReturn {
  const { delay = 500, enabled = true } = options;

  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<string | null>(getLastSavedTime());

  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const previousDataRef = useRef<string>('');

  const save = useCallback(() => {
    if (!enabled) return;

    setIsSaving(true);
    try {
      saveOnboardingData(data);
      const savedTime = new Date().toISOString();
      setLastSaved(savedTime);
    } catch (error) {
      console.error('Failed to auto-save:', error);
    } finally {
      // Show saving indicator briefly
      setTimeout(() => setIsSaving(false), 500);
    }
  }, [data, enabled]);

  useEffect(() => {
    if (!enabled) return;

    // Serialize data to detect changes
    const currentData = JSON.stringify(data);

    // Skip if data hasn't changed
    if (currentData === previousDataRef.current) {
      return;
    }

    previousDataRef.current = currentData;

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout for debounced save
    timeoutRef.current = setTimeout(() => {
      save();
    }, delay);

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data, delay, enabled, save]);

  return {
    isSaving,
    lastSaved,
    save,
  };
}
