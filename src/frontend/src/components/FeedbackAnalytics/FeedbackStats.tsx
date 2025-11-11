/**
 * FeedbackStats Component
 *
 * Displays aggregated feedback statistics in cards.
 *
 * Story 8.3: Feedback Analytics Dashboard
 */

import React from 'react';
import { ThumbsUp, ThumbsDown, MessageSquare, TrendingUp, BarChart3 } from 'lucide-react';
import { clsx } from 'clsx';
import type { FeedbackStats as FeedbackStatsType } from '@/types/feedback';

interface FeedbackStatsProps {
  stats: FeedbackStatsType;
  className?: string;
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
  variant?: 'default' | 'success' | 'danger' | 'neutral';
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  value,
  subtext,
  variant = 'default',
}) => {
  const variantStyles = {
    default: 'bg-primary-50 text-primary-600',
    success: 'bg-green-50 text-green-600',
    danger: 'bg-red-50 text-red-600',
    neutral: 'bg-gray-50 text-gray-600',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div
          className={clsx(
            'w-12 h-12 rounded-lg flex items-center justify-center',
            variantStyles[variant]
          )}
        >
          {icon}
        </div>
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-1">{value}</h3>
      <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
      {subtext && <p className="text-xs text-gray-500">{subtext}</p>}
    </div>
  );
};

export const FeedbackStats: React.FC<FeedbackStatsProps> = ({ stats, className }) => {
  const satisfactionRate =
    stats.total_feedback_count > 0
      ? ((stats.thumbs_up_count / stats.total_feedback_count) * 100).toFixed(1)
      : '0.0';

  return (
    <div className={clsx('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6', className)}>
      <StatCard
        icon={<BarChart3 className="w-6 h-6" aria-hidden="true" />}
        label="Total Feedback"
        value={stats.total_feedback_count.toLocaleString()}
        subtext={`${stats.text_feedback_count} with comments`}
        variant="default"
      />

      <StatCard
        icon={<TrendingUp className="w-6 h-6" aria-hidden="true" />}
        label="Average Rating"
        value={stats.average_rating.toFixed(2)}
        subtext={`${satisfactionRate}% satisfaction`}
        variant="neutral"
      />

      <StatCard
        icon={<ThumbsUp className="w-6 h-6" aria-hidden="true" />}
        label="Positive Feedback"
        value={stats.thumbs_up_count.toLocaleString()}
        subtext={`${stats.sentiment_breakdown.positive} positive sentiment`}
        variant="success"
      />

      <StatCard
        icon={<ThumbsDown className="w-6 h-6" aria-hidden="true" />}
        label="Negative Feedback"
        value={stats.thumbs_down_count.toLocaleString()}
        subtext={`${stats.sentiment_breakdown.negative} negative sentiment`}
        variant="danger"
      />
    </div>
  );
};

FeedbackStats.displayName = 'FeedbackStats';
