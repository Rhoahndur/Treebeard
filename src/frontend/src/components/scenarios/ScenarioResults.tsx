import React from 'react';
import { AlertCircle, TrendingUp } from 'lucide-react';
import type { GenerateRecommendationResponse } from '@/types/recommendation';
import { formatCurrency } from '@/utils/formatters';

export interface ScenarioResultsProps {
  originalResults: GenerateRecommendationResponse;
  scenarioResults?: GenerateRecommendationResponse;
  isLoading?: boolean;
}

export const ScenarioResults: React.FC<ScenarioResultsProps> = ({
  originalResults,
  scenarioResults,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Scenario Results</h2>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (!scenarioResults) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Scenario Results</h2>
        <p className="text-gray-600">Adjust parameters and run scenario to see updated recommendations</p>
      </div>
    );
  }

  const originalTop = originalResults.top_plans[0];
  const scenarioTop = scenarioResults.top_plans[0];
  const topPlanChanged = originalTop?.plan_id !== scenarioTop?.plan_id;

  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Scenario Results</h2>

      {topPlanChanged && (
        <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <div className="flex items-start gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <p className="font-medium text-blue-900">Top Plan Changed</p>
              <p className="text-sm text-blue-700 mt-1">
                From <strong>{originalTop?.plan_name}</strong> to{' '}
                <strong>{scenarioTop?.plan_name}</strong>
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Original Top Plan</h3>
          <p className="font-semibold text-gray-900">{originalTop?.plan_name}</p>
          <p className="text-sm text-gray-600">{formatCurrency(originalTop?.projected_annual_cost || 0)}/year</p>
        </div>

        <div className="p-4 bg-primary-50 rounded-lg">
          <h3 className="text-sm font-medium text-primary-700 mb-2">Scenario Top Plan</h3>
          <p className="font-semibold text-gray-900">{scenarioTop?.plan_name}</p>
          <p className="text-sm text-gray-600">{formatCurrency(scenarioTop?.projected_annual_cost || 0)}/year</p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Top 3 Plans in Scenario</h3>
        <div className="space-y-2">
          {scenarioResults.top_plans.slice(0, 3).map((plan, idx) => (
            <div key={plan.plan_id} className="flex justify-between items-center text-sm">
              <span className="text-gray-900">
                #{idx + 1} {plan.plan_name}
              </span>
              <span className="font-medium text-gray-700">
                {formatCurrency(plan.projected_annual_cost)}/year
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

ScenarioResults.displayName = 'ScenarioResults';
