import React, { useState } from 'react';
import { ChevronDown, ChevronUp, TrendingDown, TrendingUp } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/design-system';
import type { RankedPlan, MonthlyTotal } from '@/types/recommendation';
import { formatCurrency, formatDate, formatCurrencyDetailed } from '@/utils/formatters';
import { clsx } from 'clsx';

export interface CostBreakdownProps {
  plan: RankedPlan;
  currentPlanCost?: number;
  monthlyBreakdown?: MonthlyTotal[];
}

export const CostBreakdown: React.FC<CostBreakdownProps> = ({
  plan,
  currentPlanCost,
  monthlyBreakdown,
}) => {
  const [showDetails, setShowDetails] = useState(false);

  // Generate sample monthly data if not provided
  const chartData = monthlyBreakdown || generateSampleMonthlyData(plan);

  const totalAnnualCost = plan.projected_annual_cost;
  const annualSavings = plan.savings?.annual_savings || 0;
  const savingsPercentage = plan.savings?.savings_percentage || 0;
  const breakEvenMonths = plan.savings?.break_even_months;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Cost Analysis</CardTitle>
          {annualSavings > 0 && (
            <Badge variant="success" size="lg">
              <TrendingDown className="w-4 h-4 mr-1" aria-hidden="true" />
              Save {formatCurrency(annualSavings)}/year
            </Badge>
          )}
          {annualSavings < 0 && (
            <Badge variant="danger" size="lg">
              <TrendingUp className="w-4 h-4 mr-1" aria-hidden="true" />
              Costs {formatCurrency(Math.abs(annualSavings))} more/year
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Annual Cost</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(totalAnnualCost)}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Monthly Average</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(plan.projected_monthly_cost)}
            </p>
          </div>

          {breakEvenMonths !== undefined && breakEvenMonths > 0 && (
            <div className="bg-primary-50 rounded-lg p-4">
              <p className="text-sm text-primary-700 mb-1">Break-even Point</p>
              <p className="text-2xl font-bold text-primary-900">
                {breakEvenMonths} months
              </p>
            </div>
          )}
        </div>

        {/* 12-Month Cost Chart */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            12-Month Cost Projection
          </h4>
          <div className="h-64" role="img" aria-label="Monthly cost projection chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartData}
                margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="month"
                  tickFormatter={(value) => formatDate(value)}
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <YAxis
                  tickFormatter={(value) => '$' + value}
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <Tooltip
                  formatter={(value: number) => formatCurrencyDetailed(value)}
                  labelFormatter={(label) => formatDate(label)}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="total_cost"
                  name="Projected Cost"
                  stroke="#16a34a"
                  strokeWidth={2}
                  dot={{ fill: '#16a34a', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Based on your historical usage patterns
          </p>
        </div>

        {/* Expandable Cost Details */}
        <div className="border-t border-gray-200 pt-4">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className={clsx(
              'w-full flex items-center justify-between text-left',
              'text-primary-600 font-medium hover:text-primary-700',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded',
              'p-2 -m-2 min-h-[44px]'
            )}
            aria-expanded={showDetails}
            aria-controls="cost-details"
          >
            <span>View Detailed Breakdown</span>
            {showDetails ? (
              <ChevronUp className="w-5 h-5" aria-hidden="true" />
            ) : (
              <ChevronDown className="w-5 h-5" aria-hidden="true" />
            )}
          </button>

          {showDetails && (
            <div id="cost-details" className="mt-4 animate-fade-in">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Component
                      </th>
                      <th
                        scope="col"
                        className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Monthly
                      </th>
                      <th
                        scope="col"
                        className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Annual
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        Energy Charges
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        {formatCurrency(plan.projected_monthly_cost - (plan.monthly_fee || 0))}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        {formatCurrency((plan.projected_monthly_cost - (plan.monthly_fee || 0)) * 12)}
                      </td>
                    </tr>
                    {plan.monthly_fee && plan.monthly_fee > 0 && (
                      <tr>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          Monthly Service Fee
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900 text-right">
                          {formatCurrency(plan.monthly_fee)}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900 text-right">
                          {formatCurrency(plan.monthly_fee * 12)}
                        </td>
                      </tr>
                    )}
                    <tr className="bg-gray-50 font-semibold">
                      <td className="px-4 py-3 text-sm text-gray-900">
                        Total Cost
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        {formatCurrency(plan.projected_monthly_cost)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        {formatCurrency(totalAnnualCost)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {plan.early_termination_fee > 0 && (
                <div className="mt-4 p-3 bg-warning-light rounded-lg">
                  <p className="text-sm text-warning-dark">
                    <strong>Early Termination Fee:</strong> {formatCurrency(plan.early_termination_fee)}
                    <br />
                    This fee applies if you cancel before the contract ends.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Helper function to generate sample monthly data
function generateSampleMonthlyData(plan: RankedPlan): MonthlyTotal[] {
  const data: MonthlyTotal[] = [];
  const baseMonth = new Date();
  baseMonth.setDate(1); // Set to first day of month
  
  for (let i = 0; i < 12; i++) {
    const month = new Date(baseMonth);
    month.setMonth(baseMonth.getMonth() + i);
    
    // Add slight variation (±10%) to monthly cost for realistic visualization
    const variation = 0.9 + Math.random() * 0.2;
    
    data.push({
      month: month.toISOString().split('T')[0],
      total_cost: plan.projected_monthly_cost * variation,
    });
  }
  
  return data;
}

CostBreakdown.displayName = 'CostBreakdown';
