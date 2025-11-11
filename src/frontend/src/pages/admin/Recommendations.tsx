import React, { useEffect, useState } from 'react';
import { useAdminRecommendations } from '@/hooks/useAdminRecommendations';
import { DataTable } from '@/components/admin/DataTable';
import { Badge } from '@/components/design-system/Badge';
import { Input } from '@/components/design-system/Input';
import type { AdminRecommendation, RecommendationDetails, RecommendationFilters, ColumnDef } from '@/types/admin';

/**
 * Recommendations Page
 *
 * Recommendation management interface with list, filters, and detail view.
 */

export const Recommendations: React.FC = () => {
  const { recommendations, loading, fetchRecommendations, fetchRecommendationDetails } = useAdminRecommendations();

  const [filters, setFilters] = useState<RecommendationFilters>({
    user_search: '',
    profile_type: 'all',
    has_feedback: 'all',
    page: 1,
    limit: 50,
    sort_by: 'generated_at',
    sort_order: 'desc',
  });

  const [pagination, setPagination] = useState({ total: 0, totalPages: 1 });
  const [selectedRec, setSelectedRec] = useState<RecommendationDetails | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    loadRecommendations();
  }, [filters]);

  const loadRecommendations = async () => {
    try {
      const result = await fetchRecommendations(filters);
      setPagination({ total: result.total, totalPages: result.total_pages });
    } catch (error) {
      console.error('Failed to load recommendations', error);
    }
  };

  const handleViewDetails = async (rec: AdminRecommendation) => {
    try {
      const details = await fetchRecommendationDetails(rec.id);
      setSelectedRec(details);
      setDetailsOpen(true);
    } catch (error) {
      console.error('Failed to load details', error);
    }
  };

  const columns: ColumnDef<AdminRecommendation>[] = [
    {
      key: 'user_email',
      label: 'User Email',
      sortable: true,
      render: (value) => <span className="font-medium text-gray-900">{value}</span>,
    },
    {
      key: 'generated_at',
      label: 'Date Generated',
      sortable: true,
      render: (value) => new Date(value).toLocaleString(),
    },
    {
      key: 'profile_type',
      label: 'Profile Type',
      sortable: true,
      render: (value) => <Badge variant="info">{value.replace(/_/g, ' ')}</Badge>,
    },
    {
      key: 'plans_recommended_count',
      label: '# Plans',
      render: (value) => value,
    },
    {
      key: 'has_feedback',
      label: 'Feedback',
      render: (value, row) =>
        value ? (
          <Badge variant={row.feedback_sentiment === 'positive' ? 'success' : row.feedback_sentiment === 'negative' ? 'danger' : 'warning'}>
            {row.feedback_sentiment}
          </Badge>
        ) : (
          <span className="text-gray-400">None</span>
        ),
    },
    {
      key: 'id',
      label: 'Actions',
      render: (_, rec) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleViewDetails(rec);
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
        <p className="text-gray-600 mt-1">View and manage all recommendations</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            placeholder="Search by user email..."
            value={filters.user_search}
            onChange={(e) => setFilters({ ...filters, user_search: e.target.value, page: 1 })}
          />

          <select
            value={filters.profile_type}
            onChange={(e) => setFilters({ ...filters, profile_type: e.target.value as any, page: 1 })}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Profile Types</option>
            <option value="baseline">Baseline</option>
            <option value="seasonal_high_summer">Seasonal High Summer</option>
            <option value="seasonal_high_winter">Seasonal High Winter</option>
            <option value="consistent_high">Consistent High</option>
            <option value="consistent_low">Consistent Low</option>
          </select>

          <select
            value={String(filters.has_feedback)}
            onChange={(e) => {
              const val = e.target.value;
              setFilters({ ...filters, has_feedback: val === 'all' ? 'all' : val === 'true', page: 1 });
            }}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Feedback Status</option>
            <option value="true">With Feedback</option>
            <option value="false">No Feedback</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={recommendations}
        loading={loading}
        emptyMessage="No recommendations found"
        currentPage={filters.page}
        totalPages={pagination.totalPages}
        totalItems={pagination.total}
        itemsPerPage={filters.limit}
        onPageChange={(page) => setFilters({ ...filters, page })}
        onSort={(key, direction) => setFilters({ ...filters, sort_by: key as any, sort_order: direction })}
        sortKey={filters.sort_by}
        sortDirection={filters.sort_order}
        getRowKey={(rec) => rec.id}
      />

      {/* Details Modal */}
      {detailsOpen && selectedRec && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setDetailsOpen(false)} />
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
                <button
                  onClick={() => setDetailsOpen(false)}
                  className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <h2 className="text-2xl font-bold text-gray-900 mb-6">Recommendation Details</h2>

                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">User Profile</h3>
                    <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded">
                      <div>
                        <span className="text-sm text-gray-600">Profile Type:</span>
                        <Badge variant="info" className="ml-2">{selectedRec.user_profile.profile_type}</Badge>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Annual kWh:</span>
                        <span className="ml-2 font-medium">{selectedRec.user_profile.projected_annual_kwh.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Monthly Avg:</span>
                        <span className="ml-2 font-medium">{selectedRec.user_profile.mean_monthly_kwh.toFixed(0)} kWh</span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Confidence:</span>
                        <span className="ml-2 font-medium">{(selectedRec.user_profile.confidence_score * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Recommended Plans ({selectedRec.recommended_plans.length})</h3>
                    <div className="space-y-3">
                      {selectedRec.recommended_plans.map((plan) => (
                        <div key={plan.plan_id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div>
                              <div className="flex items-center space-x-2">
                                <Badge variant="success">#{plan.rank}</Badge>
                                <h4 className="font-semibold text-gray-900">{plan.plan_name}</h4>
                                <span className="text-sm text-gray-600">by {plan.supplier_name}</span>
                              </div>
                              <p className="text-sm text-gray-600 mt-1">{plan.explanation}</p>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold text-gray-900">${plan.projected_monthly_cost.toFixed(2)}</div>
                              <div className="text-sm text-gray-600">per month</div>
                            </div>
                          </div>
                          {plan.savings && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <Badge variant="success">
                                Save ${plan.savings.annual_savings.toFixed(0)}/year ({plan.savings.savings_percentage.toFixed(1)}%)
                              </Badge>
                            </div>
                          )}
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
    </div>
  );
};
