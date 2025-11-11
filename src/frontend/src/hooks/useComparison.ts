import { useState, useCallback } from 'react';
import type { RankedPlan } from '@/types/recommendation';

export interface UseComparisonReturn {
  selectedPlans: RankedPlan[];
  addPlan: (plan: RankedPlan) => boolean;
  removePlan: (planId: string) => void;
  clearAll: () => void;
  isPlanSelected: (planId: string) => boolean;
  canAddMore: boolean;
  maxPlans: number;
}

export const useComparison = (maxPlans: number = 3): UseComparisonReturn => {
  const [selectedPlans, setSelectedPlans] = useState<RankedPlan[]>([]);

  const addPlan = useCallback(
    (plan: RankedPlan): boolean => {
      if (selectedPlans.length >= maxPlans) {
        return false;
      }
      if (selectedPlans.some((p) => p.plan_id === plan.plan_id)) {
        return false;
      }
      setSelectedPlans((prev) => [...prev, plan]);
      return true;
    },
    [selectedPlans, maxPlans]
  );

  const removePlan = useCallback((planId: string) => {
    setSelectedPlans((prev) => prev.filter((p) => p.plan_id !== planId));
  }, []);

  const clearAll = useCallback(() => {
    setSelectedPlans([]);
  }, []);

  const isPlanSelected = useCallback(
    (planId: string) => {
      return selectedPlans.some((p) => p.plan_id === planId);
    },
    [selectedPlans]
  );

  const canAddMore = selectedPlans.length < maxPlans;

  return {
    selectedPlans,
    addPlan,
    removePlan,
    clearAll,
    isPlanSelected,
    canAddMore,
    maxPlans,
  };
};
