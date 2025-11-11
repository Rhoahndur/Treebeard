import { useState, useCallback } from 'react';
import type { DashboardData } from '@/types/admin';

/**
 * useAdminStats Hook
 *
 * Custom hook for fetching dashboard statistics and charts data.
 *
 * NOTE: This is a mock implementation. In production, replace with actual API calls.
 */

export const useAdminStats = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch dashboard data
   */
  const fetchDashboardData = useCallback(async (): Promise<DashboardData> => {
    setLoading(true);
    setError(null);

    try {
      await new Promise((resolve) => setTimeout(resolve, 800));

      const mockData: DashboardData = {
        stats: {
          total_users: 1247,
          active_users: 1123,
          inactive_users: 124,
          total_recommendations: 3456,
          total_feedback: 892,
          avg_recommendations_per_user: 2.77,
          cache_hit_rate: 94.5,
          api_p95_latency_ms: 245,
        },
        charts: {
          recommendations_over_time: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(2025, 9, i + 1).toISOString().split('T')[0],
            value: Math.floor(80 + Math.random() * 40),
          })),
          user_growth: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(2025, 9, i + 1).toISOString().split('T')[0],
            value: 1000 + i * 8 + Math.floor(Math.random() * 10),
          })),
          feedback_sentiment: {
            positive: 645,
            neutral: 187,
            negative: 60,
          },
        },
        recent_activity: [
          {
            id: 'act-1',
            user_email: 'john.doe@example.com',
            action: 'Generated recommendation',
            timestamp: new Date(2025, 10, 10, 14, 30).toISOString(),
            details: 'Baseline profile',
          },
          {
            id: 'act-2',
            user_email: 'jane.smith@example.com',
            action: 'Submitted feedback',
            timestamp: new Date(2025, 10, 10, 14, 15).toISOString(),
            details: 'Positive feedback',
          },
          {
            id: 'act-3',
            user_email: 'bob.wilson@example.com',
            action: 'Generated recommendation',
            timestamp: new Date(2025, 10, 10, 13, 45).toISOString(),
            details: 'Seasonal high summer',
          },
          {
            id: 'act-4',
            user_email: 'alice.johnson@example.com',
            action: 'User registered',
            timestamp: new Date(2025, 10, 10, 13, 20).toISOString(),
          },
          {
            id: 'act-5',
            user_email: 'charlie.brown@example.com',
            action: 'Generated recommendation',
            timestamp: new Date(2025, 10, 10, 12, 55).toISOString(),
            details: 'Consistent high',
          },
          {
            id: 'act-6',
            user_email: 'david.lee@example.com',
            action: 'Submitted feedback',
            timestamp: new Date(2025, 10, 10, 12, 30).toISOString(),
            details: 'Neutral feedback',
          },
          {
            id: 'act-7',
            user_email: 'emma.davis@example.com',
            action: 'Generated recommendation',
            timestamp: new Date(2025, 10, 10, 12, 10).toISOString(),
            details: 'Baseline profile',
          },
          {
            id: 'act-8',
            user_email: 'frank.miller@example.com',
            action: 'User registered',
            timestamp: new Date(2025, 10, 10, 11, 45).toISOString(),
          },
          {
            id: 'act-9',
            user_email: 'grace.taylor@example.com',
            action: 'Generated recommendation',
            timestamp: new Date(2025, 10, 10, 11, 20).toISOString(),
            details: 'Seasonal high winter',
          },
          {
            id: 'act-10',
            user_email: 'henry.anderson@example.com',
            action: 'Submitted feedback',
            timestamp: new Date(2025, 10, 10, 11, 0).toISOString(),
            details: 'Positive feedback',
          },
        ],
      };

      setData(mockData);
      return mockData;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard data';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    data,
    loading,
    error,
    fetchDashboardData,
  };
};
