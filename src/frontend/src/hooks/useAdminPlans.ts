import { useState, useCallback } from 'react';
import type { AdminPlan, PlanFilters, PaginatedPlanResponse, PlanFormData } from '@/types/admin';

/**
 * useAdminPlans Hook
 *
 * Custom hook for managing plan catalog in the admin dashboard.
 */

const generateMockPlans = (count: number): AdminPlan[] => {
  const types = ['fixed', 'variable', 'tiered', 'time_of_use'] as const;
  const suppliers = ['TXU Energy', 'Reliant', 'Direct Energy', 'Green Mountain', 'Constellation'];

  return Array.from({ length: count }, (_, i) => ({
    id: `plan-${i + 1}`,
    plan_name: `Energy Plan ${i + 1}`,
    supplier_name: suppliers[i % suppliers.length],
    plan_type: types[i % types.length],
    base_rate: 0.09 + Math.random() * 0.06,
    contract_length_months: [6, 12, 24, 36][i % 4],
    early_termination_fee: [0, 150, 200, 250][i % 4],
    renewable_percentage: Math.floor(Math.random() * 100),
    regions: ['75001', '75002', '75003'],
    available_from: new Date(2024, 0, 1).toISOString(),
    available_to: null,
    supplier_rating: 3.5 + Math.random() * 1.5,
    customer_service_rating: 3.0 + Math.random() * 2.0,
    status: i % 15 === 0 ? 'inactive' : 'active',
    created_at: new Date(2024, 0, i + 1).toISOString(),
    updated_at: new Date(2025, 10, i % 30).toISOString(),
    description: `Comprehensive energy plan with competitive rates.`,
  }));
};

const mockPlans = generateMockPlans(100);

export const useAdminPlans = () => {
  const [plans, setPlans] = useState<AdminPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlans = useCallback(
    async (filters: PlanFilters = {}): Promise<PaginatedPlanResponse> => {
      setLoading(true);
      setError(null);

      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        let filtered = [...mockPlans];

        if (filters.search) {
          const search = filters.search.toLowerCase();
          filtered = filtered.filter(
            (plan) =>
              plan.plan_name.toLowerCase().includes(search) ||
              plan.supplier_name.toLowerCase().includes(search)
          );
        }

        if (filters.plan_type && filters.plan_type !== 'all') {
          filtered = filtered.filter((plan) => plan.plan_type === filters.plan_type);
        }

        if (filters.status && filters.status !== 'all') {
          filtered = filtered.filter((plan) => plan.status === filters.status);
        }

        const page = filters.page || 1;
        const limit = filters.limit || 50;
        const startIndex = (page - 1) * limit;
        const paginatedPlans = filtered.slice(startIndex, startIndex + limit);

        const response: PaginatedPlanResponse = {
          plans: paginatedPlans,
          total: filtered.length,
          page,
          limit,
          total_pages: Math.ceil(filtered.length / limit),
        };

        setPlans(paginatedPlans);
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch plans';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const createPlan = useCallback(async (data: PlanFormData): Promise<AdminPlan> => {
    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      const newPlan: AdminPlan = {
        id: `plan-${mockPlans.length + 1}`,
        plan_name: data.plan_name,
        supplier_name: data.supplier_name,
        plan_type: data.plan_type,
        base_rate: data.base_rate,
        contract_length_months: data.contract_length_months,
        early_termination_fee: data.early_termination_fee,
        renewable_percentage: data.renewable_percentage,
        regions: data.regions,
        available_from: data.available_from,
        supplier_rating: data.supplier_rating,
        customer_service_rating: data.customer_service_rating,
        tiered_rates: data.tiered_rates ? JSON.parse(data.tiered_rates) : undefined,
        time_of_use_rates: data.time_of_use_rates ? JSON.parse(data.time_of_use_rates) : undefined,
        min_usage_kwh: data.min_usage_kwh,
        max_usage_kwh: data.max_usage_kwh,
        monthly_fee: data.monthly_fee,
        description: data.description,
        available_to: data.available_to || null,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      mockPlans.push(newPlan);
      setPlans((prev) => [...prev, newPlan]);
      return newPlan;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create plan';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updatePlan = useCallback(async (planId: string, data: Partial<PlanFormData>): Promise<void> => {
    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      const updates: Partial<AdminPlan> = {
        ...data,
        tiered_rates: data.tiered_rates ? JSON.parse(data.tiered_rates) : undefined,
        time_of_use_rates: data.time_of_use_rates ? JSON.parse(data.time_of_use_rates) : undefined,
        updated_at: new Date().toISOString(),
      };

      const index = mockPlans.findIndex((p) => p.id === planId);
      if (index !== -1) {
        mockPlans[index] = { ...mockPlans[index], ...updates };
      }

      setPlans((prev) => prev.map((p) => (p.id === planId ? { ...p, ...updates } : p)));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update plan';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deletePlan = useCallback(async (planId: string): Promise<void> => {
    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setPlans((prev) => prev.filter((p) => p.id !== planId));

      const index = mockPlans.findIndex((p) => p.id === planId);
      if (index !== -1) mockPlans.splice(index, 1);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete plan';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    plans,
    loading,
    error,
    fetchPlans,
    createPlan,
    updatePlan,
    deletePlan,
  };
};
