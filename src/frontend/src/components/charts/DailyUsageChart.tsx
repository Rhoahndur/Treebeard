import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { ChartWrapper } from './ChartWrapper';
import { ChartTooltip } from './ChartTooltip';
import { chartColors, chartGridStyle, chartAxisStyle, chartGradients } from './ChartTheme';
import { formatNumber } from '@/utils/formatters';

export interface DailyUsageChartProps {
  hourlyData?: Array<{ hour: number; kwh: number }>;
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}

export const DailyUsageChart: React.FC<DailyUsageChartProps> = ({
  hourlyData,
  isLoading = false,
  error = null,
  height = 300,
}) => {
  // If no hourly data provided, show fallback message
  if (!hourlyData || hourlyData.length === 0) {
    return (
      <ChartWrapper
        title="Daily Usage Distribution"
        subtitle="Energy usage throughout the day"
        height={height}
      >
        <div className="flex flex-col items-center justify-center h-full text-center py-8">
          <p className="text-gray-600 mb-2">Daily usage data not available</p>
          <p className="text-sm text-gray-500">
            Time-of-use data is needed to display hourly usage patterns
          </p>
        </div>
      </ChartWrapper>
    );
  }

  // Format chart data
  const chartData = hourlyData.map((data) => ({
    hour: data.hour,
    hourLabel: `${data.hour % 12 || 12}${data.hour >= 12 ? 'pm' : 'am'}`,
    kwh: data.kwh,
    isPeak: data.hour >= 16 && data.hour <= 20, // Peak hours: 4pm-8pm
  }));

  return (
    <ChartWrapper
      title="Daily Usage Distribution"
      subtitle="Typical energy usage throughout the day"
      isLoading={isLoading}
      error={error}
      height={height}
      ariaLabel="Area chart showing energy usage distribution throughout a 24-hour period"
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <defs>
            <linearGradient id="usageGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={chartGradients.usage.start}
                stopOpacity={chartGradients.usage.opacity.start}
              />
              <stop
                offset="95%"
                stopColor={chartGradients.usage.end}
                stopOpacity={chartGradients.usage.opacity.end}
              />
            </linearGradient>
          </defs>
          <CartesianGrid {...chartGridStyle} />
          <XAxis
            dataKey="hourLabel"
            {...chartAxisStyle}
            interval={2}
          />
          <YAxis
            {...chartAxisStyle}
            label={{
              value: 'kWh',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12 },
            }}
          />
          <Tooltip
            content={
              <ChartTooltip
                formatter={(value, name) => `${formatNumber(Number(value))} kWh`}
                labelFormatter={(label) => `At ${label}`}
              />
            }
          />
          {/* Peak hours annotation */}
          <ReferenceLine
            x="4pm"
            stroke={chartColors.danger}
            strokeDasharray="3 3"
            label={{
              value: 'Peak Start',
              position: 'top',
              fill: chartColors.danger,
              fontSize: 10,
            }}
          />
          <ReferenceLine
            x="8pm"
            stroke={chartColors.danger}
            strokeDasharray="3 3"
            label={{
              value: 'Peak End',
              position: 'top',
              fill: chartColors.danger,
              fontSize: 10,
            }}
          />
          <Area
            type="monotone"
            dataKey="kwh"
            name="Usage"
            stroke={chartColors.tertiary}
            strokeWidth={2}
            fill="url(#usageGradient)"
            activeDot={{ r: 6 }}
          />
        </AreaChart>
      </ResponsiveContainer>
      <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-600 justify-center">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded"
            style={{ backgroundColor: chartColors.tertiary }}
          />
          <span>Hourly Usage</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-px border-t-2 border-dashed border-danger" />
          <span>Peak Hours (4pm-8pm)</span>
        </div>
      </div>
    </ChartWrapper>
  );
};

DailyUsageChart.displayName = 'DailyUsageChart';
