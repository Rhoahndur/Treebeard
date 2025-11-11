/**
 * FeedbackChart Component
 *
 * Time-series visualization of feedback volume and ratings.
 *
 * Story 8.3: Feedback Analytics Dashboard
 */

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { clsx } from 'clsx';
import type { FeedbackTimeSeriesPoint } from '@/types/feedback';

interface FeedbackChartProps {
  data: FeedbackTimeSeriesPoint[];
  className?: string;
}

const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
      {payload.map((entry: any, index: number) => (
        <p key={index} className="text-xs text-gray-700">
          <span className="font-medium">{entry.name}:</span>{' '}
          <span style={{ color: entry.color }}>
            {entry.name === 'Average Rating' ? entry.value.toFixed(2) : entry.value}
          </span>
        </p>
      ))}
    </div>
  );
};

export const FeedbackChart: React.FC<FeedbackChartProps> = ({ data, className }) => {
  // Transform data for display
  const chartData = data.map((point) => ({
    date: new Date(point.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    fullDate: point.date,
    'Feedback Count': point.count,
    'Average Rating': point.average_rating,
  }));

  return (
    <div className={clsx('bg-white rounded-lg shadow-sm border border-gray-200 p-6', className)}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Feedback Trends</h3>
        <p className="text-sm text-gray-600">Daily feedback volume and ratings (last 30 days)</p>
      </div>

      <div className="space-y-8">
        {/* Feedback Volume Bar Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Feedback Volume</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={{ stroke: '#d1d5db' }}
              />
              <YAxis
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={{ stroke: '#d1d5db' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar
                dataKey="Feedback Count"
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
                maxBarSize={40}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Average Rating Line Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Average Rating Over Time</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={{ stroke: '#d1d5db' }}
              />
              <YAxis
                domain={[0, 5]}
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={{ stroke: '#d1d5db' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="Average Rating"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981', r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

FeedbackChart.displayName = 'FeedbackChart';
