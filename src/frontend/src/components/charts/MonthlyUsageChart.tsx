import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ChartWrapper } from './ChartWrapper';
import { ChartTooltip } from './ChartTooltip';
import {
  chartColors,
  chartGridStyle,
  chartAxisStyle,
  chartLegendStyle,
  getSeasonalColor,
} from './ChartTheme';
import type { UsageData } from '@/types/recommendation';
import { formatNumber } from '@/utils/formatters';

export interface MonthlyUsageChartProps {
  usageData: UsageData[];
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}

interface ChartDataPoint {
  month: string;
  monthLabel: string;
  kwh: number;
  season: string;
  color: string;
  isOutlier: boolean;
}

export const MonthlyUsageChart: React.FC<MonthlyUsageChartProps> = ({
  usageData,
  isLoading = false,
  error = null,
  height = 300,
}) => {
  const chartData = useMemo(() => {
    if (!usageData || usageData.length === 0) return [];

    // Calculate statistics for outlier detection
    const kwhValues = usageData.map((d) => d.kwh);
    const mean = kwhValues.reduce((a, b) => a + b, 0) / kwhValues.length;
    const variance =
      kwhValues.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / kwhValues.length;
    const stdDev = Math.sqrt(variance);

    return usageData
      .map((data) => {
        const date = new Date(data.month);
        const monthNum = date.getMonth();
        const monthLabel = date.toLocaleDateString('en-US', {
          month: 'short',
          year: '2-digit',
        });

        // Determine season
        let season = 'Winter';
        if (monthNum >= 3 && monthNum <= 5) season = 'Spring';
        else if (monthNum >= 6 && monthNum <= 8) season = 'Summer';
        else if (monthNum >= 9 && monthNum <= 11) season = 'Fall';

        // Detect outliers (±2 standard deviations)
        const isOutlier = Math.abs(data.kwh - mean) > 2 * stdDev;

        return {
          month: data.month,
          monthLabel,
          kwh: data.kwh,
          season,
          color: getSeasonalColor(monthNum),
          isOutlier,
        };
      })
      .slice(-12); // Last 12 months
  }, [usageData]);

  const averageUsage = useMemo(() => {
    if (chartData.length === 0) return 0;
    return chartData.reduce((sum, d) => sum + d.kwh, 0) / chartData.length;
  }, [chartData]);

  if (chartData.length === 0 && !isLoading && !error) {
    return (
      <ChartWrapper
        title="Monthly Usage"
        subtitle="Last 12 months of energy consumption"
        error="No usage data available"
        height={height}
      />
    );
  }

  return (
    <ChartWrapper
      title="Monthly Usage"
      subtitle="Last 12 months of energy consumption by season"
      isLoading={isLoading}
      error={error}
      height={height}
      ariaLabel="Bar chart showing monthly energy usage over the last 12 months, color-coded by season"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
        >
          <defs>
            {/* Pattern for outliers */}
            <pattern
              id="outlier-pattern"
              patternUnits="userSpaceOnUse"
              width="8"
              height="8"
            >
              <path
                d="M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4"
                stroke="#EF4444"
                strokeWidth="1"
              />
            </pattern>
          </defs>
          <CartesianGrid {...chartGridStyle} />
          <XAxis
            dataKey="monthLabel"
            {...chartAxisStyle}
            angle={-45}
            textAnchor="end"
            height={80}
            interval={0}
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
                labelFormatter={(label) => `Usage for ${label}`}
              />
            }
          />
          <Legend
            {...chartLegendStyle}
            wrapperStyle={{ paddingTop: '20px' }}
            content={
              <div className="flex flex-wrap items-center justify-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: chartColors.winter }}
                  />
                  <span>Winter</span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: chartColors.spring }}
                  />
                  <span>Spring</span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: chartColors.summer }}
                  />
                  <span>Summer</span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: chartColors.fall }}
                  />
                  <span>Fall</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-px h-3 border-l-2 border-dashed border-gray-400" />
                  <span>Average</span>
                </div>
              </div>
            }
          />
          <ReferenceLine
            y={averageUsage}
            stroke={chartColors.neutral}
            strokeDasharray="5 5"
            strokeWidth={2}
            label={{
              value: `Avg: ${formatNumber(averageUsage)} kWh`,
              position: 'right',
              fill: chartColors.neutral,
              fontSize: 11,
            }}
          />
          <Bar dataKey="kwh" name="Usage" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.isOutlier ? 'url(#outlier-pattern)' : entry.color}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
};

MonthlyUsageChart.displayName = 'MonthlyUsageChart';
