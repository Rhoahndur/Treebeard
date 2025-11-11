import React, { useState } from 'react';
import { Calculator } from 'lucide-react';
import type { RankedPlan } from '@/types/recommendation';
import { formatCurrency } from '@/utils/formatters';

export interface WhatIfCalculatorProps {
  currentPlan: RankedPlan;
  recommendedPlan: RankedPlan;
}

export const WhatIfCalculator: React.FC<WhatIfCalculatorProps> = ({
  currentPlan,
  recommendedPlan,
}) => {
  const [usageIncrease, setUsageIncrease] = useState(0);
  const [rateIncrease, setRateIncrease] = useState(0);

  const calculateImpact = (plan: RankedPlan) => {
    const baseAnnualCost = plan.projected_annual_cost;
    const usageMultiplier = 1 + usageIncrease / 100;
    const rateMultiplier = 1 + rateIncrease / 100;
    return baseAnnualCost * usageMultiplier * rateMultiplier;
  };

  const currentCost = calculateImpact(currentPlan);
  const recommendedCost = calculateImpact(recommendedPlan);
  const savings = currentCost - recommendedCost;

  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Calculator className="w-5 h-5 text-primary-600" />
        <h2 className="text-lg font-semibold text-gray-900">What-If Calculator</h2>
      </div>
      <p className="text-sm text-gray-600 mb-6">See how changes affect your costs</p>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Usage Increase: {usageIncrease}%
          </label>
          <input
            type="range"
            min="0"
            max="50"
            value={usageIncrease}
            onChange={(e) => setUsageIncrease(Number(e.target.value))}
            className="w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rate Increase: {rateIncrease}%
          </label>
          <input
            type="range"
            min="0"
            max="50"
            value={rateIncrease}
            onChange={(e) => setRateIncrease(Number(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-orange-50 rounded-lg">
          <p className="text-xs text-gray-600 mb-1">Current Plan Impact</p>
          <p className="text-lg font-bold text-gray-900">{formatCurrency(currentCost)}/yr</p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-xs text-gray-600 mb-1">Recommended Plan Impact</p>
          <p className="text-lg font-bold text-gray-900">{formatCurrency(recommendedCost)}/yr</p>
        </div>
      </div>

      <div className="mt-4 p-4 bg-primary-50 rounded-lg text-center">
        <p className="text-sm text-gray-700">Projected Savings</p>
        <p className="text-2xl font-bold text-primary-600">{formatCurrency(savings)}/yr</p>
      </div>
    </div>
  );
};

WhatIfCalculator.displayName = 'WhatIfCalculator';
