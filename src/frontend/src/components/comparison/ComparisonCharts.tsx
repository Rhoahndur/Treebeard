import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ChartWrapper } from '@/components/charts/ChartWrapper';
import { ChartTooltip } from '@/components/charts/ChartTooltip';
import { chartColors, chartGridStyle, chartAxisStyle, getSeriesColor } from '@/components/charts/ChartTheme';
import type { RankedPlan } from '@/types/recommendation';
import { formatCurrency, formatPercentage } from '@/utils/formatters';

export interface ComparisonChartsProps {
  plans: RankedPlan[];
}

export const ComparisonCharts: React.FC<ComparisonChartsProps> = ({ plans }) => {
  // 12-month cost projection for all plans
  const costProjectionData = Array.from({ length: 12 }, (_, i) => {
    const monthData: any = { month: `Month ${i + 1}` };
    plans.forEach((plan) => {
      monthData[plan.plan_id] = plan.projected_monthly_cost;
    });
    return monthData;
  });

  // Renewable energy comparison
  const renewableData = plans.map((plan) => ({
    name: plan.plan_name.length > 20 ? plan.plan_name.substring(0, 20) + '...' : plan.plan_name,
    renewable: plan.renewable_percentage,
    color: getSeriesColor(plans.indexOf(plan)),
  }));

  // Contract length comparison
  const contractData = plans.map((plan) => ({
    name: plan.plan_name.length > 20 ? plan.plan_name.substring(0, 20) + '...' : plan.plan_name,
    months: plan.contract_length_months,
    label: plan.contract_length_months === 0 ? 'M2M' : `${plan.contract_length_months}mo`,
    color: getSeriesColor(plans.indexOf(plan)),
  }));

  // Risk score radar chart
  const riskData = plans.map((plan) => {
    // Calculate risk scores (0-100, lower is better)
    const costRisk = 100 - plan.scores.cost_score;
    const flexibilityRisk = 100 - plan.scores.flexibility_score;
    const supplierRisk = 100 - plan.scores.rating_score;
    const variableRateRisk = plan.plan_type.toLowerCase().includes('variable') ? 70 : 30;
    const etfRisk = plan.early_termination_fee > 0 ? Math.min((plan.early_termination_fee / 500) * 100, 100) : 0;

    return {
      plan: plan.plan_name.length > 15 ? plan.plan_name.substring(0, 15) + '...' : plan.plan_name,
      costRisk,
      flexibilityRisk,
      supplierRisk,
      variableRateRisk,
      etfRisk,
    };
  });

  const radarCategories = [
    { key: 'costRisk', label: 'Cost Risk' },
    { key: 'flexibilityRisk', label: 'Flexibility Risk' },
    { key: 'supplierRisk', label: 'Supplier Risk' },
    { key: 'variableRateRisk', label: 'Rate Risk' },
    { key: 'etfRisk', label: 'ETF Risk' },
  ];

  return (
    <div className="space-y-6">
      {/* 12-Month Cost Projection */}
      <ChartWrapper
        title="12-Month Cost Projection"
        subtitle="Compare projected monthly costs across all plans"
        height={300}
        ariaLabel="Line chart comparing 12-month cost projections for all plans"
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={costProjectionData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid {...chartGridStyle} />
            <XAxis dataKey="month" {...chartAxisStyle} />
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
                  formatter={(value) => formatCurrency(Number(value))}
                />
              }
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            {plans.map((plan, index) => (
              <Line
                key={plan.plan_id}
                type="monotone"
                dataKey={plan.plan_id}
                name={plan.plan_name}
                stroke={getSeriesColor(index)}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </ChartWrapper>

      {/* Renewable Energy Comparison */}
      <ChartWrapper
        title="Renewable Energy Percentage"
        subtitle="Compare environmental impact across plans"
        height={250}
        ariaLabel="Bar chart comparing renewable energy percentages"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={renewableData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid {...chartGridStyle} />
            <XAxis
              dataKey="name"
              {...chartAxisStyle}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              {...chartAxisStyle}
              label={{
                value: 'Renewable %',
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 12 },
              }}
              domain={[0, 100]}
            />
            <Tooltip
              content={
                <ChartTooltip
                  formatter={(value) => `${formatPercentage(Number(value))}%`}
                />
              }
            />
            <Bar dataKey="renewable" name="Renewable Energy" radius={[8, 8, 0, 0]}>
              {renewableData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartWrapper>

      {/* Contract Length Comparison */}
      <ChartWrapper
        title="Contract Length"
        subtitle="Compare contract commitments"
        height={250}
        ariaLabel="Bar chart comparing contract lengths"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={contractData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid {...chartGridStyle} />
            <XAxis
              dataKey="name"
              {...chartAxisStyle}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              {...chartAxisStyle}
              label={{
                value: 'Months',
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 12 },
              }}
            />
            <Tooltip
              content={
                <ChartTooltip
                  formatter={(value, name, props: any) => {
                    const months = Number(value);
                    return months === 0 ? 'Month-to-month' : `${months} months`;
                  }}
                />
              }
            />
            <Bar dataKey="months" name="Contract Length" radius={[8, 8, 0, 0]}>
              {contractData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartWrapper>

      {/* Risk Score Radar */}
      <ChartWrapper
        title="Risk Analysis"
        subtitle="Compare risk factors across multiple dimensions (lower is better)"
        height={350}
        ariaLabel="Radar chart comparing risk scores across 5 dimensions"
      >
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarCategories.map((cat) => {
            const dataPoint: any = { category: cat.label };
            riskData.forEach((risk) => {
              dataPoint[risk.plan] = risk[cat.key as keyof typeof risk];
            });
            return dataPoint;
          })}>
            <PolarGrid stroke={chartColors.neutral} />
            <PolarAngleAxis dataKey="category" tick={{ fontSize: 11 }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
            <Tooltip
              content={
                <ChartTooltip
                  formatter={(value) => `${Number(value).toFixed(0)} risk score`}
                />
              }
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            {riskData.map((risk, index) => (
              <Radar
                key={risk.plan}
                name={risk.plan}
                dataKey={risk.plan}
                stroke={getSeriesColor(index)}
                fill={getSeriesColor(index)}
                fillOpacity={0.3}
                strokeWidth={2}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      </ChartWrapper>
    </div>
  );
};

ComparisonCharts.displayName = 'ComparisonCharts';
