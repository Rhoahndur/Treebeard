import React from 'react';
import { clsx } from 'clsx';
import { Card } from '@/components/design-system/Card';

/**
 * StatCard Component
 *
 * Displays a statistic with an icon, label, value, and optional change indicator.
 * Used in the admin dashboard overview to show key metrics.
 *
 * @example
 * <StatCard
 *   icon={<UsersIcon />}
 *   label="Total Users"
 *   value={1234}
 *   change={12.5}
 *   changeType="increase"
 * />
 */

export interface StatCardProps {
  /** Icon element to display */
  icon: React.ReactNode;
  /** Label describing the statistic */
  label: string;
  /** Main value to display (number or string) */
  value: string | number;
  /** Optional sub-value or description */
  subValue?: string;
  /** Optional change percentage */
  change?: number;
  /** Type of change (increase/decrease) */
  changeType?: 'increase' | 'decrease';
  /** Loading state */
  loading?: boolean;
}

/**
 * StatCard Component
 */
export const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  value,
  subValue,
  change,
  changeType,
  loading = false,
}) => {
  // Format value if it's a number
  const formattedValue =
    typeof value === 'number'
      ? value.toLocaleString()
      : value;

  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        {/* Icon */}
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600">
            {icon}
          </div>
        </div>

        {/* Change Indicator */}
        {change !== undefined && !loading && (
          <div
            className={clsx(
              'flex items-center text-sm font-medium px-2 py-1 rounded',
              changeType === 'increase'
                ? 'text-success-dark bg-success-light'
                : 'text-danger-dark bg-danger-light'
            )}
          >
            {changeType === 'increase' ? (
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            ) : (
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            )}
            {Math.abs(change)}%
          </div>
        )}
      </div>

      {/* Content */}
      <div className="mt-4">
        {loading ? (
          <>
            <div className="h-8 bg-gray-200 rounded animate-pulse mb-2" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
          </>
        ) : (
          <>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {formattedValue}
            </div>
            <div className="text-sm text-gray-600">
              {label}
            </div>
            {subValue && (
              <div className="text-xs text-gray-500 mt-1">
                {subValue}
              </div>
            )}
          </>
        )}
      </div>
    </Card>
  );
};
