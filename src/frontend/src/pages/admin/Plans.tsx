import React, { useEffect, useState } from 'react';
import { useAdminPlans } from '@/hooks/useAdminPlans';
import { DataTable } from '@/components/admin/DataTable';
import { ConfirmDialog } from '@/components/admin/ConfirmDialog';
import { Badge } from '@/components/design-system/Badge';
import { Button } from '@/components/design-system/Button';
import { Input } from '@/components/design-system/Input';
import type { AdminPlan, PlanFilters, PlanFormData, ColumnDef } from '@/types/admin';

/**
 * Plans Page
 *
 * Plan catalog management with CRUD operations.
 */

export const Plans: React.FC = () => {
  const { plans, loading, fetchPlans, createPlan, updatePlan, deletePlan } = useAdminPlans();

  const [filters, setFilters] = useState<PlanFilters>({
    search: '',
    plan_type: 'all',
    status: 'all',
    page: 1,
    limit: 50,
    sort_by: 'plan_name',
    sort_order: 'asc',
  });

  const [pagination, setPagination] = useState({ total: 0, totalPages: 1 });
  const [formOpen, setFormOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<AdminPlan | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [formData, setFormData] = useState<PlanFormData>({
    plan_name: '',
    supplier_name: '',
    plan_type: 'fixed',
    base_rate: 0.1,
    contract_length_months: 12,
    early_termination_fee: 0,
    renewable_percentage: 0,
    regions: [],
    available_from: new Date().toISOString().split('T')[0],
    supplier_rating: 4.0,
    customer_service_rating: 4.0,
  });

  useEffect(() => {
    loadPlans();
  }, [filters]);

  const loadPlans = async () => {
    try {
      const result = await fetchPlans(filters);
      setPagination({ total: result.total, totalPages: result.total_pages });
    } catch (error) {
      showToast('Failed to load plans');
    }
  };

  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);

    try {
      if (selectedPlan) {
        await updatePlan(selectedPlan.id, formData);
        showToast('Plan updated successfully');
      } else {
        await createPlan(formData);
        showToast('Plan created successfully');
      }
      setFormOpen(false);
      loadPlans();
    } catch (error) {
      showToast('Failed to save plan');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedPlan) return;

    setActionLoading(true);
    try {
      await deletePlan(selectedPlan.id);
      showToast('Plan deleted successfully');
      setDeleteModalOpen(false);
      loadPlans();
    } catch (error) {
      showToast('Failed to delete plan');
    } finally {
      setActionLoading(false);
    }
  };

  const columns: ColumnDef<AdminPlan>[] = [
    {
      key: 'plan_name',
      label: 'Plan Name',
      sortable: true,
      render: (value) => <span className="font-medium text-gray-900">{value}</span>,
    },
    {
      key: 'supplier_name',
      label: 'Supplier',
      sortable: true,
    },
    {
      key: 'plan_type',
      label: 'Type',
      sortable: true,
      render: (value) => <Badge variant="info">{value}</Badge>,
    },
    {
      key: 'base_rate',
      label: 'Base Rate',
      sortable: true,
      render: (value) => `$${value.toFixed(4)}/kWh`,
    },
    {
      key: 'contract_length_months',
      label: 'Contract',
      sortable: true,
      render: (value) => `${value} months`,
    },
    {
      key: 'renewable_percentage',
      label: 'Renewable %',
      sortable: true,
      render: (value) => `${value}%`,
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
      render: (_, plan) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedPlan(plan);
              setFormData({ ...plan, tiered_rates: JSON.stringify(plan.tiered_rates || [], null, 2), time_of_use_rates: JSON.stringify(plan.time_of_use_rates || [], null, 2) } as any);
              setFormOpen(true);
            }}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Edit
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedPlan(plan);
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Plan Catalog</h1>
          <p className="text-gray-600 mt-1">Manage energy plans</p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            setSelectedPlan(null);
            setFormData({
              plan_name: '',
              supplier_name: '',
              plan_type: 'fixed',
              base_rate: 0.1,
              contract_length_months: 12,
              early_termination_fee: 0,
              renewable_percentage: 0,
              regions: [],
              available_from: new Date().toISOString().split('T')[0],
              supplier_rating: 4.0,
              customer_service_rating: 4.0,
            });
            setFormOpen(true);
          }}
        >
          Add New Plan
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            placeholder="Search by plan or supplier..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
          />

          <select
            value={filters.plan_type}
            onChange={(e) => setFilters({ ...filters, plan_type: e.target.value as any, page: 1 })}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Types</option>
            <option value="fixed">Fixed</option>
            <option value="variable">Variable</option>
            <option value="tiered">Tiered</option>
            <option value="time_of_use">Time of Use</option>
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

      {/* Table */}
      <DataTable
        columns={columns}
        data={plans}
        loading={loading}
        emptyMessage="No plans found"
        currentPage={filters.page}
        totalPages={pagination.totalPages}
        totalItems={pagination.total}
        itemsPerPage={filters.limit}
        onPageChange={(page) => setFilters({ ...filters, page })}
        onSort={(key, direction) => setFilters({ ...filters, sort_by: key as any, sort_order: direction })}
        sortKey={filters.sort_by}
        sortDirection={filters.sort_order}
        getRowKey={(plan) => plan.id}
      />

      {/* Form Modal */}
      {formOpen && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => !actionLoading && setFormOpen(false)} />
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {selectedPlan ? 'Edit Plan' : 'Add New Plan'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <Input
                    label="Plan Name"
                    value={formData.plan_name}
                    onChange={(e) => setFormData({ ...formData, plan_name: e.target.value })}
                    required
                  />
                  <Input
                    label="Supplier Name"
                    value={formData.supplier_name}
                    onChange={(e) => setFormData({ ...formData, supplier_name: e.target.value })}
                    required
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Plan Type</label>
                    <select
                      value={formData.plan_type}
                      onChange={(e) => setFormData({ ...formData, plan_type: e.target.value as any })}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base"
                      required
                    >
                      <option value="fixed">Fixed</option>
                      <option value="variable">Variable</option>
                      <option value="tiered">Tiered</option>
                      <option value="time_of_use">Time of Use</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Base Rate ($/kWh)"
                      type="number"
                      step="0.0001"
                      value={formData.base_rate}
                      onChange={(e) => setFormData({ ...formData, base_rate: parseFloat(e.target.value) })}
                      required
                    />
                    <Input
                      label="Contract Length (months)"
                      type="number"
                      value={formData.contract_length_months}
                      onChange={(e) => setFormData({ ...formData, contract_length_months: parseInt(e.target.value) })}
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Renewable %"
                      type="number"
                      min="0"
                      max="100"
                      value={formData.renewable_percentage}
                      onChange={(e) => setFormData({ ...formData, renewable_percentage: parseInt(e.target.value) })}
                      required
                    />
                    <Input
                      label="Early Term Fee ($)"
                      type="number"
                      value={formData.early_termination_fee}
                      onChange={(e) => setFormData({ ...formData, early_termination_fee: parseFloat(e.target.value) })}
                      required
                    />
                  </div>

                  <div className="flex items-center justify-end space-x-3 mt-6">
                    <Button variant="outline" onClick={() => setFormOpen(false)} disabled={actionLoading}>
                      Cancel
                    </Button>
                    <Button type="submit" variant="primary" loading={actionLoading}>
                      {selectedPlan ? 'Update' : 'Create'} Plan
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Delete Modal */}
      <ConfirmDialog
        open={deleteModalOpen}
        title="Delete Plan"
        message={`Are you sure you want to delete ${selectedPlan?.plan_name}? This action cannot be undone.`}
        variant="danger"
        loading={actionLoading}
        onConfirm={handleDelete}
        onCancel={() => setDeleteModalOpen(false)}
      />

      {/* Toast */}
      {toastMessage && (
        <div className="fixed bottom-4 right-4 bg-gray-900 text-white px-6 py-3 rounded-lg shadow-lg z-50">
          {toastMessage}
        </div>
      )}
    </div>
  );
};
