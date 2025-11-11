import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
} from 'recharts';
import { ChartWrapper } from './ChartWrapper';
import { ChartTooltip } from './ChartTooltip';
import { chartColors } from './ChartTheme';
import type { RankedPlan } from '@/types/recommendation';
import { formatCurrency, formatPercentage } from '@/utils/formatters';

export interface CostBreakdownChartProps {
  plan: RankedPlan;
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}

interface CostComponent {
  name: string;
  value: number;
  color: string;
  percentage: number;
}

export const CostBreakdownChart: React.FC<CostBreakdownChartProps> = ({
  plan,
  isLoading = false,
  error = null,
  height = 350,
}) => {
  const chartData = useMemo(() => {
    const monthlyCost = plan.projected_monthly_cost;

    // Estimate cost breakdown
    // Base energy cost (rate * usage)
    const baseEnergyCost = monthlyCost * 0.75; // ~75% is energy cost

    // Monthly fees
    const fees = plan.monthly_fee || monthlyCost * 0.05; // ~5%

    // Taxes (estimated at ~10%)
    const taxes = monthlyCost * 0.10;

    // Renewable premium (if high renewable %)
    const renewablePremium =
      plan.renewable_percentage >= 50
        ? monthlyCost * (plan.renewable_percentage / 100) * 0.10
        : 0;

    const total = baseEnergyCost + fees + taxes + renewablePremium;

    const components: CostComponent[] = [
      {
        name: 'Base Energy Cost',
        value: baseEnergyCost,
        color: chartColors.baseCost,
        percentage: (baseEnergyCost / total) * 100,
      },
      {
        name: 'Fees',
        value: fees,
        color: chartColors.fees,
        percentage: (fees / total) * 100,
      },
      {
        name: 'Taxes',
        value: taxes,
        color: chartColors.taxes,
        percentage: (taxes / total) * 100,
      },
    ];

    if (renewablePremium > 0) {
      components.push({
        name: 'Renewable Premium',
        value: renewablePremium,
        color: chartColors.renewable,
        percentage: (renewablePremium / total) * 100,
      });
    }

    return components;
  }, [plan]);

  const totalCost = chartData.reduce((sum, item) => sum + item.value, 0);

  const renderCustomLabel = (entry: CostComponent) => {
    if (entry.percentage < 5) return null; // Don't show label for small slices
    return `${entry.percentage.toFixed(0)}%`;
  };

  return (
    <ChartWrapper
      title="Cost Breakdown"
      subtitle={`Monthly cost components for ${plan.plan_name}`}
      isLoading={isLoading}
      error={error}
      height={height}
      ariaLabel="Pie chart showing breakdown of monthly cost components"
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="45%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={100}
            innerRadius={60}
            fill="#8884d8"
            dataKey="value"
            paddingAngle={2}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
            <Label
              value={formatCurrency(totalCost)}
              position="center"
              style={{
                fontSize: '20px',
                fontWeight: 'bold',
                fill: '#111827',
              }}
            />
          </Pie>
          <Tooltip
            content={
              <ChartTooltip
                formatter={(value, name) => {
                  const item = chartData.find((d) => d.name === name);
                  return `${formatCurrency(Number(value))} (${formatPercentage(
                    item?.percentage || 0
                  )}%)`;
                }}
              />
            }
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry: any) => {
              const item = chartData.find((d) => d.name === value);
              return `${value}: ${formatCurrency(item?.value || 0)}`;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
};

CostBreakdownChart.displayName = 'CostBreakdownChart';
