import React, { useEffect, useState } from 'react';
import { useAuditLogs } from '@/hooks/useAuditLogs';
import { DataTable } from '@/components/admin/DataTable';
import { JsonViewer } from '@/components/admin/JsonViewer';
import { Badge } from '@/components/design-system/Badge';
import { Button } from '@/components/design-system/Button';
import { Input } from '@/components/design-system/Input';
import type { AuditLogEntry, AuditLogFilters, ColumnDef } from '@/types/admin';

/**
 * AuditLogs Page
 *
 * Audit log viewer with filters and export functionality.
 */

export const AuditLogs: React.FC = () => {
  const { logs, loading, fetchLogs, exportToCSV } = useAuditLogs();

  const [filters, setFilters] = useState<AuditLogFilters>({
    admin_user: '',
    action: 'all',
    resource_type: 'all',
    page: 1,
    limit: 100,
    sort_by: 'timestamp',
    sort_order: 'desc',
  });

  const [pagination, setPagination] = useState({ total: 0, totalPages: 1 });
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadLogs();
  }, [filters]);

  const loadLogs = async () => {
    try {
      const result = await fetchLogs(filters);
      setPagination({ total: result.total, totalPages: result.total_pages });
    } catch (error) {
      console.error('Failed to load logs', error);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const csv = await exportToCSV();
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export', error);
    } finally {
      setExporting(false);
    }
  };

  const getActionBadgeVariant = (action: string) => {
    if (action.includes('deleted')) return 'danger';
    if (action.includes('created')) return 'success';
    if (action.includes('updated')) return 'warning';
    return 'info';
  };

  const columns: ColumnDef<AuditLogEntry>[] = [
    {
      key: 'timestamp',
      label: 'Timestamp',
      sortable: true,
      render: (value) => new Date(value).toLocaleString(),
      width: '180px',
    },
    {
      key: 'admin_email',
      label: 'Admin User',
      sortable: true,
      render: (value) => <span className="font-medium text-gray-900">{value}</span>,
    },
    {
      key: 'action',
      label: 'Action',
      sortable: true,
      render: (value) => (
        <Badge variant={getActionBadgeVariant(value)}>
          {value.replace(/_/g, ' ')}
        </Badge>
      ),
    },
    {
      key: 'resource_type',
      label: 'Resource Type',
      render: (value) => <Badge variant="neutral">{value}</Badge>,
    },
    {
      key: 'resource_id',
      label: 'Resource ID',
      render: (value) => <span className="font-mono text-xs text-gray-600">{value}</span>,
    },
    {
      key: 'ip_address',
      label: 'IP Address',
      render: (value) => <span className="font-mono text-xs text-gray-600">{value}</span>,
    },
    {
      key: 'id',
      label: 'Actions',
      render: (_, log) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setSelectedLog(log);
            setDetailsOpen(true);
          }}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          View Details
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Audit Logs</h1>
          <p className="text-gray-600 mt-1">Track all administrative actions</p>
        </div>
        <Button variant="primary" onClick={handleExport} loading={exporting}>
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            placeholder="Search by admin email..."
            value={filters.admin_user}
            onChange={(e) => setFilters({ ...filters, admin_user: e.target.value, page: 1 })}
          />

          <select
            value={filters.action}
            onChange={(e) => setFilters({ ...filters, action: e.target.value as any, page: 1 })}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Actions</option>
            <option value="user_role_updated">User Role Updated</option>
            <option value="user_deleted">User Deleted</option>
            <option value="plan_created">Plan Created</option>
            <option value="plan_updated">Plan Updated</option>
            <option value="plan_deleted">Plan Deleted</option>
          </select>

          <select
            value={filters.resource_type}
            onChange={(e) => setFilters({ ...filters, resource_type: e.target.value as any, page: 1 })}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Resources</option>
            <option value="user">User</option>
            <option value="plan">Plan</option>
            <option value="recommendation">Recommendation</option>
            <option value="system">System</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={logs}
        loading={loading}
        emptyMessage="No audit logs found"
        currentPage={filters.page}
        totalPages={pagination.totalPages}
        totalItems={pagination.total}
        itemsPerPage={filters.limit}
        onPageChange={(page) => setFilters({ ...filters, page })}
        onSort={(key, direction) => setFilters({ ...filters, sort_by: key as any, sort_order: direction })}
        sortKey={filters.sort_by}
        sortDirection={filters.sort_order}
        getRowKey={(log) => log.id}
      />

      {/* Details Modal */}
      {detailsOpen && selectedLog && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setDetailsOpen(false)} />
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full p-6">
                <button
                  onClick={() => setDetailsOpen(false)}
                  className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <h2 className="text-2xl font-bold text-gray-900 mb-6">Audit Log Details</h2>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm font-medium text-gray-500">Timestamp</span>
                      <p className="text-sm text-gray-900 mt-1">{new Date(selectedLog.timestamp).toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Admin User</span>
                      <p className="text-sm text-gray-900 mt-1">{selectedLog.admin_email}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Action</span>
                      <div className="mt-1">
                        <Badge variant={getActionBadgeVariant(selectedLog.action)}>
                          {selectedLog.action.replace(/_/g, ' ')}
                        </Badge>
                      </div>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Resource Type</span>
                      <div className="mt-1">
                        <Badge variant="neutral">{selectedLog.resource_type}</Badge>
                      </div>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Resource ID</span>
                      <p className="text-sm text-gray-900 mt-1 font-mono">{selectedLog.resource_id}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">IP Address</span>
                      <p className="text-sm text-gray-900 mt-1 font-mono">{selectedLog.ip_address}</p>
                    </div>
                  </div>

                  <div>
                    <span className="text-sm font-medium text-gray-500 block mb-2">Details</span>
                    <JsonViewer data={selectedLog.details} maxHeight="300px" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
