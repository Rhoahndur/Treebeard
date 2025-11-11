import React from 'react';
import { X, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/design-system';
import type { RankedPlan } from '@/types/recommendation';

export interface ComparisonViewProps {
  plans: RankedPlan[];
  onRemovePlan: (planId: string) => void;
  onBack?: () => void;
  children: React.ReactNode;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({
  plans,
  onRemovePlan,
  onBack,
  children,
}) => {
  if (plans.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            No Plans to Compare
          </h2>
          <p className="text-gray-600 mb-6">
            Select 2-3 plans from the results page to compare them side-by-side.
          </p>
          {onBack && (
            <Button onClick={onBack} variant="primary">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Results
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {onBack && (
              <button
                onClick={onBack}
                className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
              >
                <ArrowLeft className="w-5 h-5" />
                Back to Results
              </button>
            )}
            <div className="text-sm text-gray-600">
              Comparing {plans.length} plan{plans.length !== 1 ? 's' : ''}
            </div>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Plan Comparison
          </h1>
          <p className="text-gray-600">
            Compare features, costs, and benefits side-by-side
          </p>
        </div>

        {/* Sticky Plan Headers */}
        <div className="sticky top-0 z-10 bg-white shadow-md rounded-lg mb-6 p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {plans.map((plan) => (
              <div
                key={plan.plan_id}
                className="relative bg-gray-50 rounded-lg p-4 border-2 border-gray-200"
              >
                <button
                  onClick={() => onRemovePlan(plan.plan_id)}
                  className="absolute top-2 right-2 p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-200"
                  aria-label={`Remove ${plan.plan_name} from comparison`}
                >
                  <X className="w-4 h-4" />
                </button>
                <div className="pr-8">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {plan.plan_name}
                  </h3>
                  <p className="text-sm text-gray-600">{plan.supplier_name}</p>
                  {plan.rank && (
                    <div className="mt-2 inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-primary-100 text-primary-700">
                      Rank #{plan.rank}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Comparison Content */}
        <div className="space-y-6">{children}</div>
      </div>
    </div>
  );
};

ComparisonView.displayName = 'ComparisonView';
