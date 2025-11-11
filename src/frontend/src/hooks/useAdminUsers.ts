import { useState, useCallback } from 'react';
import type {
  AdminUser,
  UserDetails,
  UserFilters,
  PaginatedUserResponse,
} from '@/types/admin';

/**
 * useAdminUsers Hook
 *
 * Custom hook for managing user data in the admin dashboard.
 * Provides functions for fetching, updating, and deleting users.
 *
 * NOTE: This is a mock implementation. In production, replace with actual API calls.
 *
 * @example
 * const { users, loading, fetchUsers, updateUserRole, deleteUser } = useAdminUsers();
 */

// Mock data generator
const generateMockUsers = (count: number): AdminUser[] => {
  return Array.from({ length: count }, (_, i) => ({
    id: `user-${i + 1}`,
    email: `user${i + 1}@example.com`,
    full_name: `User ${i + 1}`,
    role: i % 5 === 0 ? 'admin' : 'user',
    status: i % 10 === 0 ? 'inactive' : 'active',
    registration_date: new Date(2024, 0, i + 1).toISOString(),
    last_login: i % 3 === 0 ? null : new Date(2025, 10, 10 - (i % 10)).toISOString(),
    recommendation_count: Math.floor(Math.random() * 20),
    feedback_count: Math.floor(Math.random() * 10),
  }));
};

const mockUsers = generateMockUsers(150);

export const useAdminUsers = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch users with filters and pagination
   */
  const fetchUsers = useCallback(async (filters: UserFilters = {}): Promise<PaginatedUserResponse> => {
    setLoading(true);
    setError(null);

    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Apply filters
      let filtered = [...mockUsers];

      if (filters.search) {
        const search = filters.search.toLowerCase();
        filtered = filtered.filter(
          (user) =>
            user.email.toLowerCase().includes(search) ||
            user.full_name.toLowerCase().includes(search)
        );
      }

      if (filters.role && filters.role !== 'all') {
        filtered = filtered.filter((user) => user.role === filters.role);
      }

      if (filters.status && filters.status !== 'all') {
        filtered = filtered.filter((user) => user.status === filters.status);
      }

      // Apply sorting
      if (filters.sort_by) {
        filtered.sort((a, b) => {
          const aVal = a[filters.sort_by as keyof AdminUser];
          const bVal = b[filters.sort_by as keyof AdminUser];

          if (aVal === null) return 1;
          if (bVal === null) return -1;

          if (typeof aVal === 'string' && typeof bVal === 'string') {
            return filters.sort_order === 'asc'
              ? aVal.localeCompare(bVal)
              : bVal.localeCompare(aVal);
          }

          if (typeof aVal === 'number' && typeof bVal === 'number') {
            return filters.sort_order === 'asc' ? aVal - bVal : bVal - aVal;
          }

          return 0;
        });
      }

      // Apply pagination
      const page = filters.page || 1;
      const limit = filters.limit || 50;
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const paginatedUsers = filtered.slice(startIndex, endIndex);

      const response: PaginatedUserResponse = {
        users: paginatedUsers,
        total: filtered.length,
        page,
        limit,
        total_pages: Math.ceil(filtered.length / limit),
      };

      setUsers(paginatedUsers);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch users';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch user details by ID
   */
  const fetchUserDetails = useCallback(async (userId: string): Promise<UserDetails> => {
    setLoading(true);
    setError(null);

    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      const user = mockUsers.find((u) => u.id === userId);
      if (!user) {
        throw new Error('User not found');
      }

      const details: UserDetails = {
        ...user,
        activity_history: [
          {
            id: 'act-1',
            user_id: userId,
            action_type: 'recommendation',
            timestamp: new Date(2025, 10, 5).toISOString(),
            details: { profile_type: 'baseline' },
          },
          {
            id: 'act-2',
            user_id: userId,
            action_type: 'feedback',
            timestamp: new Date(2025, 10, 3).toISOString(),
            details: { sentiment: 'positive' },
          },
        ],
        usage_statistics: {
          total_recommendations: user.recommendation_count,
          avg_recommendations_per_month: 2.5,
          total_feedback_submitted: user.feedback_count,
          last_recommendation_date: new Date(2025, 10, 5).toISOString(),
        },
      };

      return details;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch user details';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Update user role
   */
  const updateUserRole = useCallback(async (userId: string, role: 'user' | 'admin'): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Update mock data
      const userIndex = mockUsers.findIndex((u) => u.id === userId);
      if (userIndex !== -1) {
        mockUsers[userIndex].role = role;
      }

      // Update local state
      setUsers((prevUsers) =>
        prevUsers.map((user) =>
          user.id === userId ? { ...user, role } : user
        )
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update user role';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Delete user (soft delete)
   */
  const deleteUser = useCallback(async (userId: string): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Update local state
      setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));

      // Remove from mock data
      const userIndex = mockUsers.findIndex((u) => u.id === userId);
      if (userIndex !== -1) {
        mockUsers.splice(userIndex, 1);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete user';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    users,
    loading,
    error,
    fetchUsers,
    fetchUserDetails,
    updateUserRole,
    deleteUser,
  };
};
