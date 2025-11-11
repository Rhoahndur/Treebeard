import React, { useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceDot,
} from 'recharts';
import { ChartWrapper } from './ChartWrapper';
import { ChartTooltip } from './ChartTooltip';
import { chartColors, chartGridStyle, chartAxisStyle, chartGradients } from './ChartTheme';
import type { RankedPlan } from '@/types/recommendation';
import { formatCurrency } from '@/utils/formatters';

export interface CumulativeSavingsChartProps {
  plan: RankedPlan;
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}

interface CumulativeData {
  month: number;
  monthLabel: string;
  cumulativeSavings: number;
  milestone?: string;
}

export const CumulativeSavingsChart: React.FC<CumulativeSavingsChartProps> = ({
  plan,
  isLoading = false,
  error = null,
  height = 300,
}) => {
  const chartData = useMemo(() => {
    if (!plan.savings) return [];

    const monthlySavings = plan.savings.monthly_savings;
    const etf = plan.early_termination_fee || 0;
    const breakEvenMonths = plan.savings.break_even_months;

    const data: CumulativeData[] = [];

    for (let month = 1; month <= 12; month++) {
      const cumulativeSavings = monthlySavings * month - etf;

      let milestone: string | undefined;
      if (month === breakEvenMonths) {
        milestone = 'Break-even';
      } else if (month === 6) {
        milestone = '6-month';
      } else if (month === 12) {
        milestone = '12-month';
      }

      data.push({
        month,
        monthLabel: `Month ${month}`,
        cumulativeSavings,
        milestone,
      });
    }

    return data;
  }, [plan]);

  const totalSavings = chartData[11]?.cumulativeSavings || 0;
  const breakEvenPoint = chartData.find((d) => d.milestone === 'Break-even');
  const sixMonthSavings = chartData[5]?.cumulativeSavings || 0;

  if (chartData.length === 0 && !isLoading && !error) {
    return (
      <ChartWrapper
        title="Cumulative Savings"
        subtitle="Total savings over time"
        error="No savings data available"
        height={height}
      />
    );
  }

  return (
    <ChartWrapper
      title="Cumulative Savings Over Time"
      subtitle={`12-month total: ${formatCurrency(totalSavings)}`}
      isLoading={isLoading}
      error={error}
      height={height}
      ariaLabel="Area chart showing cumulative savings over a 12-month period"
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <defs>
            <linearGradient id="cumulativeSavingsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={chartGradients.savings.start}
                stopOpacity={chartGradients.savings.opacity.start}
              />
              <stop
                offset="95%"
                stopColor={chartGradients.savings.end}
                stopOpacity={chartGradients.savings.opacity.end}
              />
            </linearGradient>
          </defs>
          <CartesianGrid {...chartGridStyle} />
          <XAxis
            dataKey="monthLabel"
            {...chartAxisStyle}
            interval={1}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis
            {...chartAxisStyle}
            label={{
              value: 'Cumulative Savings ($)',
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
                labelFormatter={(label) => label}
              />
            }
          />
          {/* Break-even line (if ETF exists) */}
          {plan.early_termination_fee > 0 && (
            <ReferenceLine
              y={0}
              stroke={chartColors.neutral}
              strokeDasharray="3 3"
              strokeWidth={2}
              label={{
                value: 'Break-even',
                position: 'right',
                fill: chartColors.neutral,
                fontSize: 11,
              }}
            />
          )}
          {/* 6-month milestone */}
          {sixMonthSavings > 0 && (
            <ReferenceDot
              x="Month 6"
              y={sixMonthSavings}
              r={5}
              fill={chartColors.success}
              stroke="#fff"
              strokeWidth={2}
              label={{
                value: formatCurrency(sixMonthSavings),
                position: 'top',
                fill: chartColors.success,
                fontSize: 11,
                fontWeight: 'bold',
              }}
            />
          )}
          {/* 12-month milestone */}
          {totalSavings > 0 && (
            <ReferenceDot
              x="Month 12"
              y={totalSavings}
              r={6}
              fill={chartColors.success}
              stroke="#fff"
              strokeWidth={2}
              label={{
                value: formatCurrency(totalSavings),
                position: 'top',
                fill: chartColors.success,
                fontSize: 11,
                fontWeight: 'bold',
              }}
            />
          )}
          {/* Break-even point marker */}
          {breakEvenPoint && (
            <ReferenceDot
              x={breakEvenPoint.monthLabel}
              y={breakEvenPoint.cumulativeSavings}
              r={5}
              fill={chartColors.primary}
              stroke="#fff"
              strokeWidth={2}
              label={{
                value: 'Break-even',
                position: 'bottom',
                fill: chartColors.primary,
                fontSize: 10,
              }}
            />
          )}
          <Area
            type="monotone"
            dataKey="cumulativeSavings"
            name="Cumulative Savings"
            stroke={chartColors.success}
            strokeWidth={3}
            fill="url(#cumulativeSavingsGradient)"
            activeDot={{ r: 6 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
};

CumulativeSavingsChart.displayName = 'CumulativeSavingsChart';
