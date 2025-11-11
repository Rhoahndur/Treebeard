import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ChartWrapper } from './ChartWrapper';
import { ChartTooltip } from './ChartTooltip';
import { chartColors, chartGridStyle, chartAxisStyle } from './ChartTheme';
import type { RankedPlan } from '@/types/recommendation';
import { Badge } from '@/components/design-system';

export interface RateStructureChartProps {
  plan: RankedPlan;
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}

export const RateStructureChart: React.FC<RateStructureChartProps> = ({
  plan,
  isLoading = false,
  error = null,
  height = 300,
}) => {
  const planType = plan.plan_type.toLowerCase();

  // For fixed rate plans, just show a simple badge
  if (planType.includes('fixed')) {
    return (
      <ChartWrapper
        title="Rate Structure"
        subtitle={`${plan.plan_name} pricing`}
        isLoading={isLoading}
        error={error}
        height={height}
      >
        <div className="flex flex-col items-center justify-center h-full">
          <div className="text-center">
            <Badge variant="primary" size="lg" className="mb-4">
              Fixed Rate Plan
            </Badge>
            <div className="text-4xl font-bold text-gray-900 mb-2">
              {plan.average_rate_per_kwh.toFixed(2)}¢
            </div>
            <div className="text-sm text-gray-600">per kWh</div>
            <p className="mt-4 text-sm text-gray-500 max-w-xs mx-auto">
              Your rate stays the same regardless of usage or time of day
            </p>
          </div>
        </div>
      </ChartWrapper>
    );
  }

  // For time-of-use plans
  if (planType.includes('time') || planType.includes('tou')) {
    const touData = [
      {
        period: 'Off-Peak',
        time: '9pm-5am',
        rate: plan.average_rate_per_kwh * 0.7, // 30% lower
        color: chartColors.success,
      },
      {
        period: 'Shoulder',
        time: '5am-4pm',
        rate: plan.average_rate_per_kwh,
        color: chartColors.primary,
      },
      {
        period: 'Peak',
        time: '4pm-9pm',
        rate: plan.average_rate_per_kwh * 1.5, // 50% higher
        color: chartColors.danger,
      },
    ];

    return (
      <ChartWrapper
        title="Rate Structure"
        subtitle="Time-of-Use pricing by period"
        isLoading={isLoading}
        error={error}
        height={height}
        ariaLabel="Bar chart showing time-of-use electricity rates by time period"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={touData}
            margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
          >
            <CartesianGrid {...chartGridStyle} />
            <XAxis
              dataKey="period"
              {...chartAxisStyle}
              label={{
                value: 'Time Period',
                position: 'insideBottom',
                offset: -10,
                style: { fontSize: 12 },
              }}
            />
            <YAxis
              {...chartAxisStyle}
              label={{
                value: 'Rate (¢/kWh)',
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 12 },
              }}
            />
            <Tooltip
              content={
                <ChartTooltip
                  formatter={(value) => `${Number(value).toFixed(2)}¢/kWh`}
                />
              }
            />
            <Bar dataKey="rate" name="Rate" radius={[8, 8, 0, 0]}>
              {touData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 text-xs text-gray-600 space-y-1">
          {touData.map((period, idx) => (
            <div key={idx} className="flex justify-between">
              <span>
                <span className="font-medium">{period.period}:</span> {period.time}
              </span>
              <span className="font-semibold">{period.rate.toFixed(2)}¢/kWh</span>
            </div>
          ))}
        </div>
      </ChartWrapper>
    );
  }

  // For tiered/variable plans
  if (planType.includes('tier') || planType.includes('variable')) {
    const tieredData = [
      {
        tier: 'Tier 1',
        range: '0-500 kWh',
        rate: plan.average_rate_per_kwh * 0.9,
        color: chartColors.success,
      },
      {
        tier: 'Tier 2',
        range: '501-1000 kWh',
        rate: plan.average_rate_per_kwh,
        color: chartColors.primary,
      },
      {
        tier: 'Tier 3',
        range: '1001+ kWh',
        rate: plan.average_rate_per_kwh * 1.2,
        color: chartColors.danger,
      },
    ];

    return (
      <ChartWrapper
        title="Rate Structure"
        subtitle="Tiered pricing by usage level"
        isLoading={isLoading}
        error={error}
        height={height}
        ariaLabel="Bar chart showing tiered electricity rates by usage level"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={tieredData}
            margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
          >
            <CartesianGrid {...chartGridStyle} />
            <XAxis
              dataKey="tier"
              {...chartAxisStyle}
              label={{
                value: 'Usage Tier',
                position: 'insideBottom',
                offset: -10,
                style: { fontSize: 12 },
              }}
            />
            <YAxis
              {...chartAxisStyle}
              label={{
                value: 'Rate (¢/kWh)',
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 12 },
              }}
            />
            <Tooltip
              content={
                <ChartTooltip
                  formatter={(value) => `${Number(value).toFixed(2)}¢/kWh`}
                />
              }
            />
            <Bar dataKey="rate" name="Rate" radius={[8, 8, 0, 0]}>
              {tieredData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 text-xs text-gray-600 space-y-1">
          {tieredData.map((tier, idx) => (
            <div key={idx} className="flex justify-between">
              <span>
                <span className="font-medium">{tier.tier}:</span> {tier.range}
              </span>
              <span className="font-semibold">{tier.rate.toFixed(2)}¢/kWh</span>
            </div>
          ))}
        </div>
      </ChartWrapper>
    );
  }

  // Default: show simple rate
  return (
    <ChartWrapper
      title="Rate Structure"
      subtitle={`${plan.plan_name} pricing`}
      isLoading={isLoading}
      error={error}
      height={height}
    >
      <div className="flex flex-col items-center justify-center h-full">
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-900 mb-2">
            {plan.average_rate_per_kwh.toFixed(2)}¢
          </div>
          <div className="text-sm text-gray-600">per kWh</div>
          <p className="mt-4 text-sm text-gray-500 max-w-xs mx-auto">
            {plan.plan_type} plan
          </p>
        </div>
      </div>
    </ChartWrapper>
  );
};

RateStructureChart.displayName = 'RateStructureChart';
