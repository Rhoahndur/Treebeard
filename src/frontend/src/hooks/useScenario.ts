import { useState, useCallback, useEffect } from 'react';
import type { Preferences } from '@/types/recommendation';

export interface ScenarioParams {
  usageAdjustment: number; // -50 to +50 (percentage)
  costPriority: number; // 0-100
  renewablePriority: number; // 0-100
  flexibilityPriority: number; // 0-100
}

export interface SavedScenario {
  id: string;
  name: string;
  params: ScenarioParams;
  createdAt: string;
}

export interface UseScenarioReturn {
  currentScenario: ScenarioParams;
  updateScenario: (params: Partial<ScenarioParams>) => void;
  resetScenario: () => void;
  savedScenarios: SavedScenario[];
  saveScenario: (name: string) => void;
  loadScenario: (id: string) => void;
  deleteScenario: (id: string) => void;
  getShareUrl: () => string;
  loadFromUrl: (url: string) => boolean;
}

const DEFAULT_SCENARIO: ScenarioParams = {
  usageAdjustment: 0,
  costPriority: 50,
  renewablePriority: 50,
  flexibilityPriority: 50,
};

const STORAGE_KEY = 'treebeard_scenarios';

export const useScenario = (initialPreferences?: Preferences): UseScenarioReturn => {
  const [currentScenario, setCurrentScenario] = useState<ScenarioParams>(() => {
    if (initialPreferences) {
      return {
        usageAdjustment: 0,
        costPriority: initialPreferences.cost_priority,
        renewablePriority: initialPreferences.renewable_priority,
        flexibilityPriority: initialPreferences.flexibility_priority,
      };
    }
    return DEFAULT_SCENARIO;
  });

  const [savedScenarios, setSavedScenarios] = useState<SavedScenario[]>([]);

  // Load saved scenarios from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setSavedScenarios(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Failed to load saved scenarios:', error);
    }
  }, []);

  const updateScenario = useCallback((params: Partial<ScenarioParams>) => {
    setCurrentScenario((prev) => ({ ...prev, ...params }));
  }, []);

  const resetScenario = useCallback(() => {
    setCurrentScenario(DEFAULT_SCENARIO);
  }, []);

  const saveScenario = useCallback(
    (name: string) => {
      const newScenario: SavedScenario = {
        id: `scenario-${Date.now()}`,
        name,
        params: { ...currentScenario },
        createdAt: new Date().toISOString(),
      };

      const updated = [...savedScenarios, newScenario];
      setSavedScenarios(updated);

      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (error) {
        console.error('Failed to save scenario:', error);
      }
    },
    [currentScenario, savedScenarios]
  );

  const loadScenario = useCallback(
    (id: string) => {
      const scenario = savedScenarios.find((s) => s.id === id);
      if (scenario) {
        setCurrentScenario(scenario.params);
      }
    },
    [savedScenarios]
  );

  const deleteScenario = useCallback(
    (id: string) => {
      const updated = savedScenarios.filter((s) => s.id !== id);
      setSavedScenarios(updated);

      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (error) {
        console.error('Failed to delete scenario:', error);
      }
    },
    [savedScenarios]
  );

  const getShareUrl = useCallback(() => {
    const params = new URLSearchParams({
      usage: currentScenario.usageAdjustment.toString(),
      cost: currentScenario.costPriority.toString(),
      renewable: currentScenario.renewablePriority.toString(),
      flexibility: currentScenario.flexibilityPriority.toString(),
    });
    return `${window.location.origin}/scenario?${params.toString()}`;
  }, [currentScenario]);

  const loadFromUrl = useCallback((url: string): boolean => {
    try {
      const urlObj = new URL(url);
      const params = new URLSearchParams(urlObj.search);

      const usage = params.get('usage');
      const cost = params.get('cost');
      const renewable = params.get('renewable');
      const flexibility = params.get('flexibility');

      if (usage && cost && renewable && flexibility) {
        setCurrentScenario({
          usageAdjustment: Number(usage),
          costPriority: Number(cost),
          renewablePriority: Number(renewable),
          flexibilityPriority: Number(flexibility),
        });
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to load scenario from URL:', error);
      return false;
    }
  }, []);

  return {
    currentScenario,
    updateScenario,
    resetScenario,
    savedScenarios,
    saveScenario,
    loadScenario,
    deleteScenario,
    getShareUrl,
    loadFromUrl,
  };
};
