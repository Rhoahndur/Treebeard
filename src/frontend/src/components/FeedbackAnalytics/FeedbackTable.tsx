/**
 * FeedbackTable Component
 *
 * Displays plan-level feedback aggregation in a sortable table.
 *
 * Story 8.3: Feedback Analytics Dashboard
 */

import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { clsx } from 'clsx';
import type { PlanFeedbackAggregation } from '@/types/feedback';

interface FeedbackTableProps {
  plans: PlanFeedbackAggregation[];
  className?: string;
}

type SortKey = 'plan_name' | 'total_feedback' | 'average_rating';
type SortDirection = 'asc' | 'desc';

export const FeedbackTable: React.FC<FeedbackTableProps> = ({ plans, className }) => {
  const [sortKey, setSortKey] = useState<SortKey>('total_feedback');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('desc');
    }
  };

  const sortedPlans = [...plans].sort((a, b) => {
    let aValue: string | number = a[sortKey];
    let bValue: string | number = b[sortKey];

    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
    }
    if (typeof bValue === 'string') {
      bValue = bValue.toLowerCase();
    }

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  const SortIcon = ({ columnKey }: { columnKey: SortKey }) => {
    if (sortKey !== columnKey) {
      return <ArrowUpDown className="w-4 h-4 text-gray-400" aria-hidden="true" />;
    }
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4 text-primary-600" aria-hidden="true" />
    ) : (
      <ArrowDown className="w-4 h-4 text-primary-600" aria-hidden="true" />
    );
  };

  return (
    <div className={clsx('bg-white rounded-lg shadow-sm border border-gray-200', className)}>
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Plan Feedback Summary</h3>
        <p className="text-sm text-gray-600">Most reviewed plans and their ratings</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('plan_name')}
                  className={clsx(
                    'flex items-center gap-2 text-xs font-medium text-gray-700',
                    'hover:text-gray-900 transition-colors',
                    'focus:outline-none focus:underline'
                  )}
                >
                  Plan Name
                  <SortIcon columnKey="plan_name" />
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">
                Supplier
              </th>
              <th className="px-6 py-3 text-right">
                <button
                  onClick={() => handleSort('total_feedback')}
                  className={clsx(
                    'flex items-center gap-2 text-xs font-medium text-gray-700 ml-auto',
                    'hover:text-gray-900 transition-colors',
                    'focus:outline-none focus:underline'
                  )}
                >
                  Total Feedback
                  <SortIcon columnKey="total_feedback" />
                </button>
              </th>
              <th className="px-6 py-3 text-right">
                <button
                  onClick={() => handleSort('average_rating')}
                  className={clsx(
                    'flex items-center gap-2 text-xs font-medium text-gray-700 ml-auto',
                    'hover:text-gray-900 transition-colors',
                    'focus:outline-none focus:underline'
                  )}
                >
                  Avg Rating
                  <SortIcon columnKey="average_rating" />
                </button>
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-700">
                Feedback Split
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">
                Last Updated
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedPlans.map((plan) => {
              const satisfactionRate =
                plan.total_feedback > 0
                  ? ((plan.thumbs_up_count / plan.total_feedback) * 100).toFixed(0)
                  : '0';

              const lastUpdated = plan.most_recent_feedback
                ? new Date(plan.most_recent_feedback).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })
                : 'N/A';

              return (
                <tr key={plan.plan_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{plan.plan_name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-700">{plan.supplier_name}</div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {plan.total_feedback}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div
                      className={clsx(
                        'inline-flex items-center px-2 py-1 rounded text-sm font-medium',
                        plan.average_rating >= 4
                          ? 'bg-green-100 text-green-800'
                          : plan.average_rating >= 3
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      )}
                    >
                      {plan.average_rating.toFixed(2)}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-center gap-3">
                      <div className="flex items-center gap-1 text-green-600">
                        <ThumbsUp className="w-4 h-4" aria-hidden="true" />
                        <span className="text-sm font-medium">{plan.thumbs_up_count}</span>
                        <span className="text-xs text-gray-500">({satisfactionRate}%)</span>
                      </div>
                      <div className="flex items-center gap-1 text-red-600">
                        <ThumbsDown className="w-4 h-4" aria-hidden="true" />
                        <span className="text-sm font-medium">{plan.thumbs_down_count}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-600">{lastUpdated}</div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {sortedPlans.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No feedback data available yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

FeedbackTable.displayName = 'FeedbackTable';
