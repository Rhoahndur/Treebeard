import React, { useMemo } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from 'recharts';
import { ChartWrapper } from './ChartWrapper';
import { ChartTooltip } from './ChartTooltip';
import { chartColors, chartGridStyle, chartAxisStyle } from './ChartTheme';
import type { RankedPlan } from '@/types/recommendation';
import type { UsageData } from '@/types/recommendation';
import { formatCurrency } from '@/utils/formatters';

export interface CostComparisonChartProps {
  recommendedPlan: RankedPlan;
  currentPlanCost?: number; // Current monthly cost
  usageData: UsageData[];
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}

interface MonthlyComparison {
  month: string;
  monthLabel: string;
  currentCost: number;
  recommendedCost: number;
  savings: number;
}

export const CostComparisonChart: React.FC<CostComparisonChartProps> = ({
  recommendedPlan,
  currentPlanCost,
  usageData,
  isLoading = false,
  error = null,
  height = 300,
}) => {
  const chartData = useMemo(() => {
    if (!usageData || usageData.length === 0) return [];

    // Get last 12 months of usage
    const last12Months = usageData.slice(-12);

    return last12Months.map((data, index) => {
      const date = new Date(data.month);
      const monthLabel = date.toLocaleDateString('en-US', {
        month: 'short',
        year: '2-digit',
      });

      // Calculate recommended plan cost for this month's usage
      const recommendedCost = (data.kwh * recommendedPlan.average_rate_per_kwh) / 100;
      const monthlyFee = recommendedPlan.monthly_fee || 0;
      const totalRecommendedCost = recommendedCost + monthlyFee;

      // Use provided current cost or estimate from usage
      const currentCost = currentPlanCost || recommendedPlan.projected_monthly_cost * 1.15;

      const savings = currentCost - totalRecommendedCost;

      return {
        month: data.month,
        monthLabel,
        currentCost,
        recommendedCost: totalRecommendedCost,
        savings: Math.max(0, savings),
      };
    });
  }, [usageData, recommendedPlan, currentPlanCost]);

  const totalSavings = useMemo(() => {
    return chartData.reduce((sum, month) => sum + month.savings, 0);
  }, [chartData]);

  if (chartData.length === 0 && !isLoading && !error) {
    return (
      <ChartWrapper
        title="Cost Comparison"
        subtitle="Current plan vs recommended plan"
        error="No usage data available for comparison"
        height={height}
      />
    );
  }

  return (
    <ChartWrapper
      title="Cost Comparison"
      subtitle={`Current plan vs ${recommendedPlan.plan_name} • Total savings: ${formatCurrency(totalSavings)}`}
      isLoading={isLoading}
      error={error}
      height={height}
      ariaLabel="Line chart comparing monthly costs between current plan and recommended plan"
    >
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <defs>
            <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColors.success} stopOpacity={0.3} />
              <stop offset="95%" stopColor={chartColors.success} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid {...chartGridStyle} />
          <XAxis
            dataKey="monthLabel"
            {...chartAxisStyle}
            angle={-45}
            textAnchor="end"
            height={60}
            interval={0}
          />
          <YAxis
            {...chartAxisStyle}
            label={{
              value: 'Monthly Cost ($)',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12 },
            }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip
            content={
              <ChartTooltip
                formatter={(value, name) => formatCurrency(Number(value))}
                labelFormatter={(label) => `Month: ${label}`}
              />
            }
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          {/* Shaded area showing savings */}
          <Area
            type="monotone"
            dataKey="savings"
            name="Monthly Savings"
            fill="url(#savingsGradient)"
            stroke="none"
            fillOpacity={1}
          />
          {/* Current plan cost line */}
          <Line
            type="monotone"
            dataKey="currentCost"
            name="Current Plan"
            stroke={chartColors.tertiary}
            strokeWidth={3}
            dot={{ r: 4, fill: chartColors.tertiary }}
            activeDot={{ r: 6 }}
          />
          {/* Recommended plan cost line */}
          <Line
            type="monotone"
            dataKey="recommendedCost"
            name="Recommended Plan"
            stroke={chartColors.success}
            strokeWidth={3}
            dot={{ r: 4, fill: chartColors.success }}
            activeDot={{ r: 6 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
};

CostComparisonChart.displayName = 'CostComparisonChart';
