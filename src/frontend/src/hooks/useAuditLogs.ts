import { useState, useCallback } from 'react';
import type { AuditLogEntry, AuditLogFilters, PaginatedAuditLogResponse } from '@/types/admin';

/**
 * useAuditLogs Hook
 *
 * Custom hook for fetching and managing audit logs.
 */

const generateMockLogs = (count: number): AuditLogEntry[] => {
  const actions = [
    'user_role_updated',
    'user_deleted',
    'plan_created',
    'plan_updated',
    'plan_deleted',
  ] as const;

  const resourceTypes = ['user', 'plan'] as const;

  return Array.from({ length: count }, (_, i) => ({
    id: `log-${i + 1}`,
    timestamp: new Date(2025, 10, 10 - Math.floor(i / 10), 15 - (i % 24), i % 60).toISOString(),
    admin_user_id: `admin-${(i % 3) + 1}`,
    admin_email: `admin${(i % 3) + 1}@treebeard.com`,
    action: actions[i % actions.length],
    resource_type: resourceTypes[i % 2],
    resource_id: `resource-${i + 1}`,
    details: {
      previous_value: i % 2 === 0 ? 'user' : 'admin',
      new_value: i % 2 === 0 ? 'admin' : 'user',
      reason: 'Administrative action',
    },
    ip_address: `192.168.1.${(i % 255) + 1}`,
  }));
};

const mockLogs = generateMockLogs(300);

export const useAuditLogs = () => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(
    async (filters: AuditLogFilters = {}): Promise<PaginatedAuditLogResponse> => {
      setLoading(true);
      setError(null);

      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        let filtered = [...mockLogs];

        if (filters.admin_user) {
          filtered = filtered.filter((log) =>
            log.admin_email.toLowerCase().includes(filters.admin_user!.toLowerCase())
          );
        }

        if (filters.action && filters.action !== 'all') {
          if (Array.isArray(filters.action)) {
            filtered = filtered.filter((log) => filters.action!.includes(log.action));
          } else {
            filtered = filtered.filter((log) => log.action === filters.action);
          }
        }

        if (filters.resource_type && filters.resource_type !== 'all') {
          filtered = filtered.filter((log) => log.resource_type === filters.resource_type);
        }

        const page = filters.page || 1;
        const limit = filters.limit || 100;
        const startIndex = (page - 1) * limit;
        const paginatedLogs = filtered.slice(startIndex, startIndex + limit);

        const response: PaginatedAuditLogResponse = {
          logs: paginatedLogs,
          total: filtered.length,
          page,
          limit,
          total_pages: Math.ceil(filtered.length / limit),
        };

        setLogs(paginatedLogs);
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch logs';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const exportToCSV = useCallback(async (): Promise<string> => {
    try {
      const headers = ['Timestamp', 'Admin Email', 'Action', 'Resource Type', 'Resource ID', 'IP Address'];
      const rows = logs.map((log) => [
        log.timestamp,
        log.admin_email,
        log.action,
        log.resource_type,
        log.resource_id,
        log.ip_address,
      ]);

      const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');
      return csv;
    } catch (err) {
      throw new Error('Failed to export logs');
    }
  }, [logs]);

  return {
    logs,
    loading,
    error,
    fetchLogs,
    exportToCSV,
  };
};
