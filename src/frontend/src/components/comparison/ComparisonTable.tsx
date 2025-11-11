import React, { useMemo } from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import type { RankedPlan } from '@/types/recommendation';
import { formatCurrency, formatPercentage } from '@/utils/formatters';

export interface ComparisonTableProps {
  plans: RankedPlan[];
}

interface ComparisonRow {
  label: string;
  values: Array<{
    planId: string;
    value: string | number;
    rawValue: number;
    isBest: boolean;
    isWorst: boolean;
  }>;
  lowerIsBetter: boolean;
}

export const ComparisonTable: React.FC<ComparisonTableProps> = ({ plans }) => {
  const rows = useMemo(() => {
    if (plans.length === 0) return [];

    const getMinMax = (values: number[], lowerIsBetter: boolean) => {
      const min = Math.min(...values);
      const max = Math.max(...values);
      return { best: lowerIsBetter ? min : max, worst: lowerIsBetter ? max : min };
    };

    // Annual cost
    const annualCosts = plans.map((p) => p.projected_annual_cost);
    const annualMinMax = getMinMax(annualCosts, true);

    // Monthly cost
    const monthlyCosts = plans.map((p) => p.projected_monthly_cost);
    const monthlyMinMax = getMinMax(monthlyCosts, true);

    // Rate
    const rates = plans.map((p) => p.average_rate_per_kwh);
    const rateMinMax = getMinMax(rates, true);

    // Contract
    const contracts = plans.map((p) => p.contract_length_months);
    const contractMinMax = getMinMax(contracts, false); // Longer isn't necessarily better

    // Renewable
    const renewables = plans.map((p) => p.renewable_percentage);
    const renewableMinMax = getMinMax(renewables, false);

    // ETF
    const etfs = plans.map((p) => p.early_termination_fee);
    const etfMinMax = getMinMax(etfs, true);

    // Savings
    const savings = plans.map((p) => p.savings?.annual_savings || 0);
    const savingsMinMax = getMinMax(savings, false);

    const comparisonRows: ComparisonRow[] = [
      {
        label: 'Annual Cost',
        lowerIsBetter: true,
        values: plans.map((p) => ({
          planId: p.plan_id,
          value: formatCurrency(p.projected_annual_cost),
          rawValue: p.projected_annual_cost,
          isBest: p.projected_annual_cost === annualMinMax.best,
          isWorst: p.projected_annual_cost === annualMinMax.worst,
        })),
      },
      {
        label: 'Monthly Average',
        lowerIsBetter: true,
        values: plans.map((p) => ({
          planId: p.plan_id,
          value: formatCurrency(p.projected_monthly_cost),
          rawValue: p.projected_monthly_cost,
          isBest: p.projected_monthly_cost === monthlyMinMax.best,
          isWorst: p.projected_monthly_cost === monthlyMinMax.worst,
        })),
      },
      {
        label: 'Rate (¢/kWh)',
        lowerIsBetter: true,
        values: plans.map((p) => ({
          planId: p.plan_id,
          value: `${p.average_rate_per_kwh.toFixed(2)}¢`,
          rawValue: p.average_rate_per_kwh,
          isBest: p.average_rate_per_kwh === rateMinMax.best,
          isWorst: p.average_rate_per_kwh === rateMinMax.worst,
        })),
      },
      {
        label: 'Contract Length',
        lowerIsBetter: false,
        values: plans.map((p) => ({
          planId: p.plan_id,
          value: p.contract_length_months === 0 ? 'Month-to-month' : `${p.contract_length_months} months`,
          rawValue: p.contract_length_months,
          isBest: false, // Subjective
          isWorst: false,
        })),
      },
      {
        label: 'Renewable Energy',
        lowerIsBetter: false,
        values: plans.map((p) => ({
          planId: p.plan_id,
          value: `${formatPercentage(p.renewable_percentage)}%`,
          rawValue: p.renewable_percentage,
          isBest: p.renewable_percentage === renewableMinMax.best,
          isWorst: p.renewable_percentage === renewableMinMax.worst,
        })),
      },
      {
        label: 'Early Termination Fee',
        lowerIsBetter: true,
        values: plans.map((p) => ({
          planId: p.plan_id,
          value: p.early_termination_fee === 0 ? 'None' : formatCurrency(p.early_termination_fee),
          rawValue: p.early_termination_fee,
          isBest: p.early_termination_fee === etfMinMax.best,
          isWorst: p.early_termination_fee === etfMinMax.worst && p.early_termination_fee > 0,
        })),
      },
      {
        label: 'Annual Savings',
        lowerIsBetter: false,
        values: plans.map((p) => ({
          planId: p.plan_id,
          value: p.savings?.annual_savings ? formatCurrency(p.savings.annual_savings) : 'N/A',
          rawValue: p.savings?.annual_savings || 0,
          isBest: p.savings?.annual_savings === savingsMinMax.best && (p.savings?.annual_savings || 0) > 0,
          isWorst: false,
        })),
      },
    ];

    return comparisonRows;
  }, [plans]);

  return (
    <div className="bg-white rounded-lg shadow-card overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          Feature Comparison
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Side-by-side comparison of key plan attributes
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Attribute
              </th>
              {plans.map((plan) => (
                <th
                  key={plan.plan_id}
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {plan.plan_name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rows.map((row) => (
              <tr key={row.label}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {row.label}
                </td>
                {row.values.map((cell) => (
                  <td
                    key={cell.planId}
                    className={`px-6 py-4 whitespace-nowrap text-sm ${
                      cell.isBest
                        ? 'bg-green-50 text-green-900 font-semibold'
                        : cell.isWorst
                        ? 'bg-red-50 text-red-900'
                        : 'text-gray-900'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {cell.isBest && (
                        <CheckCircle className="w-4 h-4 text-green-600" aria-label="Best value" />
                      )}
                      {cell.isWorst && (
                        <AlertTriangle className="w-4 h-4 text-red-600" aria-label="Worst value" />
                      )}
                      <span>{cell.value}</span>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex gap-6 text-xs text-gray-600">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span>Best value</span>
          </div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span>Worst value</span>
          </div>
        </div>
      </div>
    </div>
  );
};

ComparisonTable.displayName = 'ComparisonTable';
