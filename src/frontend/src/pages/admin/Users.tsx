import React, { useEffect, useState } from 'react';
import { useAdminUsers } from '@/hooks/useAdminUsers';
import { DataTable } from '@/components/admin/DataTable';
import { ConfirmDialog } from '@/components/admin/ConfirmDialog';
import { Badge } from '@/components/design-system/Badge';
import { Button } from '@/components/design-system/Button';
import { Input } from '@/components/design-system/Input';
import type { AdminUser, UserDetails, UserFilters } from '@/types/admin';
import type { ColumnDef } from '@/types/admin';

/**
 * Users Page
 *
 * User management interface with list, search, view details, update roles, and soft delete.
 */

export const Users: React.FC = () => {
  const { users, loading, fetchUsers, fetchUserDetails, updateUserRole, deleteUser } = useAdminUsers();

  const [filters, setFilters] = useState<UserFilters>({
    search: '',
    role: 'all',
    status: 'all',
    page: 1,
    limit: 50,
    sort_by: 'registration_date',
    sort_order: 'desc',
  });

  const [pagination, setPagination] = useState({
    total: 0,
    totalPages: 1,
  });

  const [selectedUser, setSelectedUser] = useState<UserDetails | null>(null);
  const [userDetailsOpen, setUserDetailsOpen] = useState(false);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    loadUsers();
  }, [filters]);

  const loadUsers = async () => {
    try {
      const result = await fetchUsers(filters);
      setPagination({ total: result.total, totalPages: result.total_pages });
    } catch (error) {
      showToast('Failed to load users');
    }
  };

  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleViewDetails = async (user: AdminUser) => {
    try {
      const details = await fetchUserDetails(user.id);
      setSelectedUser(details);
      setUserDetailsOpen(true);
    } catch (error) {
      showToast('Failed to load user details');
    }
  };

  const handleRoleUpdate = async () => {
    if (!selectedUser) return;

    setActionLoading(true);
    try {
      const newRole = selectedUser.role === 'admin' ? 'user' : 'admin';
      await updateUserRole(selectedUser.id, newRole);
      showToast(`User role updated to ${newRole}`);
      setRoleModalOpen(false);
      loadUsers();
    } catch (error) {
      showToast('Failed to update user role');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedUser) return;

    setActionLoading(true);
    try {
      await deleteUser(selectedUser.id);
      showToast('User deleted successfully');
      setDeleteModalOpen(false);
      loadUsers();
    } catch (error) {
      showToast('Failed to delete user');
    } finally {
      setActionLoading(false);
    }
  };

  const columns: ColumnDef<AdminUser>[] = [
    {
      key: 'email',
      label: 'Email',
      sortable: true,
      render: (value) => <span className="font-medium text-gray-900">{value}</span>,
    },
    {
      key: 'full_name',
      label: 'Full Name',
      sortable: true,
    },
    {
      key: 'role',
      label: 'Role',
      sortable: true,
      render: (value) => (
        <Badge variant={value === 'admin' ? 'info' : 'neutral'}>
          {value}
        </Badge>
      ),
    },
    {
      key: 'registration_date',
      label: 'Registration Date',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'last_login',
      label: 'Last Login',
      sortable: true,
      render: (value) => (value ? new Date(value).toLocaleDateString() : 'Never'),
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      render: (value) => (
        <Badge variant={value === 'active' ? 'success' : 'neutral'}>
          {value}
        </Badge>
      ),
    },
    {
      key: 'id',
      label: 'Actions',
      render: (_, user) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleViewDetails(user);
            }}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            View
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedUser(user as any);
              setRoleModalOpen(true);
            }}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            Edit Role
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedUser(user as any);
              setDeleteModalOpen(true);
            }}
            className="text-danger hover:text-danger-dark text-sm font-medium"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <p className="text-gray-600 mt-1">Manage users, roles, and permissions</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <Input
              placeholder="Search by email or name..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
            />
          </div>

          <select
            value={filters.role}
            onChange={(e) => setFilters({ ...filters, role: e.target.value as any, page: 1 })}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Roles</option>
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value as any, page: 1 })}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <DataTable
        columns={columns}
        data={users}
        loading={loading}
        emptyMessage="No users found"
        currentPage={filters.page}
        totalPages={pagination.totalPages}
        totalItems={pagination.total}
        itemsPerPage={filters.limit}
        onPageChange={(page) => setFilters({ ...filters, page })}
        onSort={(key, direction) => setFilters({ ...filters, sort_by: key as any, sort_order: direction })}
        sortKey={filters.sort_by}
        sortDirection={filters.sort_order}
        getRowKey={(user) => user.id}
      />

      {/* User Details Modal */}
      {userDetailsOpen && selectedUser && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setUserDetailsOpen(false)} />
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
                <button
                  onClick={() => setUserDetailsOpen(false)}
                  className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <h2 className="text-2xl font-bold text-gray-900 mb-6">User Details</h2>

                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Basic Information</h3>
                    <dl className="grid grid-cols-2 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Email</dt>
                        <dd className="text-sm text-gray-900 mt-1">{selectedUser.email}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                        <dd className="text-sm text-gray-900 mt-1">{selectedUser.full_name}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Role</dt>
                        <dd className="mt-1">
                          <Badge variant={selectedUser.role === 'admin' ? 'info' : 'neutral'}>
                            {selectedUser.role}
                          </Badge>
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Status</dt>
                        <dd className="mt-1">
                          <Badge variant={selectedUser.status === 'active' ? 'success' : 'neutral'}>
                            {selectedUser.status}
                          </Badge>
                        </dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Usage Statistics</h3>
                    <dl className="grid grid-cols-2 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Total Recommendations</dt>
                        <dd className="text-sm text-gray-900 mt-1">{selectedUser.usage_statistics.total_recommendations}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Avg Recs/Month</dt>
                        <dd className="text-sm text-gray-900 mt-1">{selectedUser.usage_statistics.avg_recommendations_per_month.toFixed(1)}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Total Feedback</dt>
                        <dd className="text-sm text-gray-900 mt-1">{selectedUser.usage_statistics.total_feedback_submitted}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Last Recommendation</dt>
                        <dd className="text-sm text-gray-900 mt-1">
                          {selectedUser.usage_statistics.last_recommendation_date
                            ? new Date(selectedUser.usage_statistics.last_recommendation_date).toLocaleDateString()
                            : 'Never'}
                        </dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Activity</h3>
                    <div className="space-y-2">
                      {selectedUser.activity_history.slice(0, 5).map((activity) => (
                        <div key={activity.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm text-gray-900">{activity.action_type}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(activity.timestamp).toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Role Update Modal */}
      <ConfirmDialog
        open={roleModalOpen}
        title="Update User Role"
        message={`Are you sure you want to ${selectedUser?.role === 'admin' ? 'demote' : 'promote'} ${selectedUser?.email} to ${selectedUser?.role === 'admin' ? 'user' : 'admin'}?`}
        variant="warning"
        confirmText="Update Role"
        loading={actionLoading}
        onConfirm={handleRoleUpdate}
        onCancel={() => setRoleModalOpen(false)}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        open={deleteModalOpen}
        title="Delete User"
        message={`Are you sure you want to delete ${selectedUser?.email}? This action cannot be undone.`}
        variant="danger"
        confirmText="Delete"
        loading={actionLoading}
        onConfirm={handleDelete}
        onCancel={() => setDeleteModalOpen(false)}
      />

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-4 right-4 bg-gray-900 text-white px-6 py-3 rounded-lg shadow-lg z-50">
          {toastMessage}
        </div>
      )}
    </div>
  );
};
