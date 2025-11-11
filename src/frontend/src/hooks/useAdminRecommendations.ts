import { useState, useCallback } from 'react';
import type {
  AdminRecommendation,
  RecommendationDetails,
  RecommendationFilters,
  PaginatedRecommendationResponse,
} from '@/types/admin';

/**
 * useAdminRecommendations Hook
 *
 * Custom hook for managing recommendation data in the admin dashboard.
 */

const generateMockRecommendations = (count: number): AdminRecommendation[] => {
  const profileTypes = ['baseline', 'seasonal_high_summer', 'seasonal_high_winter', 'consistent_high', 'consistent_low'] as const;
  const sentiments = ['positive', 'neutral', 'negative'] as const;

  return Array.from({ length: count }, (_, i) => ({
    id: `rec-${i + 1}`,
    user_id: `user-${Math.floor(Math.random() * 150) + 1}`,
    user_email: `user${Math.floor(Math.random() * 150) + 1}@example.com`,
    generated_at: new Date(2025, 9, Math.floor(Math.random() * 30) + 1, Math.floor(Math.random() * 24)).toISOString(),
    profile_type: profileTypes[Math.floor(Math.random() * profileTypes.length)],
    plans_recommended_count: 5,
    has_feedback: Math.random() > 0.6,
    feedback_sentiment: Math.random() > 0.6 ? sentiments[Math.floor(Math.random() * sentiments.length)] : undefined,
    feedback_text: Math.random() > 0.6 ? 'Great recommendations!' : undefined,
  }));
};

const mockRecommendations = generateMockRecommendations(200);

export const useAdminRecommendations = () => {
  const [recommendations, setRecommendations] = useState<AdminRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = useCallback(
    async (filters: RecommendationFilters = {}): Promise<PaginatedRecommendationResponse> => {
      setLoading(true);
      setError(null);

      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        let filtered = [...mockRecommendations];

        if (filters.user_search) {
          const search = filters.user_search.toLowerCase();
          filtered = filtered.filter((rec) =>
            rec.user_email.toLowerCase().includes(search)
          );
        }

        if (filters.profile_type && filters.profile_type !== 'all') {
          filtered = filtered.filter((rec) => rec.profile_type === filters.profile_type);
        }

        if (filters.has_feedback !== 'all' && typeof filters.has_feedback === 'boolean') {
          filtered = filtered.filter((rec) => rec.has_feedback === filters.has_feedback);
        }

        const page = filters.page || 1;
        const limit = filters.limit || 50;
        const startIndex = (page - 1) * limit;
        const paginatedRecs = filtered.slice(startIndex, startIndex + limit);

        const response: PaginatedRecommendationResponse = {
          recommendations: paginatedRecs,
          total: filtered.length,
          page,
          limit,
          total_pages: Math.ceil(filtered.length / limit),
        };

        setRecommendations(paginatedRecs);
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch recommendations';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const fetchRecommendationDetails = useCallback(async (recId: string): Promise<RecommendationDetails> => {
    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      const rec = mockRecommendations.find((r) => r.id === recId);
      if (!rec) throw new Error('Recommendation not found');

      return {
        ...rec,
        user_profile: {
          profile_type: rec.profile_type,
          projected_annual_kwh: 12000,
          mean_monthly_kwh: 1000,
          has_seasonal_pattern: rec.profile_type.includes('seasonal'),
          confidence_score: 0.92,
        },
        user_data: { zip_code: '75001', property_type: 'residential' },
        usage_data: Array.from({ length: 12 }, (_, i) => ({
          month: `2024-${String(i + 1).padStart(2, '0')}`,
          kwh: 900 + Math.random() * 200,
        })),
        preferences: {
          cost_priority: 8,
          flexibility_priority: 5,
          renewable_priority: 7,
          rating_priority: 6,
        },
        recommended_plans: Array.from({ length: 5 }, (_, i) => ({
          rank: i + 1,
          plan_id: `plan-${i + 1}`,
          plan_name: `Energy Plan ${i + 1}`,
          supplier_name: `Supplier ${String.fromCharCode(65 + i)}`,
          plan_type: 'fixed',
          scores: {
            cost_score: 8.5 - i * 0.5,
            flexibility_score: 7.0,
            renewable_score: 8.0,
            rating_score: 7.5,
            composite_score: 8.0 - i * 0.3,
          },
          projected_annual_cost: 1200 + i * 100,
          projected_monthly_cost: 100 + i * 8,
          average_rate_per_kwh: 0.12 + i * 0.01,
          savings: { annual_savings: 300 - i * 50, savings_percentage: 20 - i * 3, monthly_savings: 25 - i * 4 },
          explanation: 'This plan offers great value for your usage pattern.',
          key_differentiators: ['Low base rate', 'No monthly fee'],
          trade_offs: ['12-month contract', 'Early termination fee'],
        })),
        warnings: [],
        total_plans_analyzed: 50,
      } as RecommendationDetails;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch details';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    recommendations,
    loading,
    error,
    fetchRecommendations,
    fetchRecommendationDetails,
  };
};
