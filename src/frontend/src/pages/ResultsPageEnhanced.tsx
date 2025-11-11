import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Sparkles, Download, BarChart3, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PlanCard } from '@/components/PlanCard/PlanCard';
import { CostBreakdown } from '@/components/CostBreakdown/CostBreakdown';
import { FeedbackWidget } from '@/components/FeedbackWidget';
import { SkeletonCard, Button } from '@/components/design-system';
import { MonthlyUsageChart, SeasonalPatternChart, UsageProfileBadge, CostComparisonChart } from '@/components/charts';
import { PdfExport, CsvExportUsage } from '@/components/export';
import { useComparison } from '@/hooks/useComparison';
import type { GenerateRecommendationResponse, RankedPlan, UsageData } from '@/types/recommendation';
import { formatCurrency, formatNumber } from '@/utils/formatters';

export interface ResultsPageProps {
  recommendation: GenerateRecommendationResponse | null;
  usageData?: UsageData[];
  isLoading?: boolean;
  error?: string | null;
}

export const ResultsPage: React.FC<ResultsPageProps> = ({
  recommendation,
  usageData = [],
  isLoading = false,
  error = null,
}) => {
  const navigate = useNavigate();
  const [selectedPlan, setSelectedPlan] = useState<RankedPlan | null>(null);
  const { selectedPlans, addPlan, removePlan, isPlanSelected, canAddMore } = useComparison(3);

  useEffect(() => {
    if (recommendation?.top_plans && recommendation.top_plans.length > 0) {
      setSelectedPlan(recommendation.top_plans[0]);
    }
  }, [recommendation]);

  const handlePlanCheckbox = (plan: RankedPlan, checked: boolean) => {
    if (checked) {
      const added = addPlan(plan);
      if (!added) {
        alert('Maximum 3 plans can be compared at once');
      }
    } else {
      removePlan(plan.plan_id);
    }
  };

  const handleCompare = () => {
    navigate('/comparison', { state: { selectedPlans } });
  };

  const handleScenarios = () => {
    navigate('/scenarios', { state: { recommendation } });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4 animate-pulse-soft">
              <Sparkles className="w-8 h-8 text-primary-600" aria-hidden="true" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Finding Your Best Plans...
            </h1>
            <p className="text-lg text-gray-600">
              Analyzing energy plans based on your preferences
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <div
            className="bg-white rounded-lg shadow-card p-8 text-center"
            role="alert"
            aria-live="polite"
          >
            <AlertCircle className="w-16 h-16 text-danger mx-auto mb-4" aria-hidden="true" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Unable to Load Recommendations
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (!recommendation || !recommendation.top_plans || recommendation.top_plans.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-card p-8 text-center">
            <AlertCircle className="w-16 h-16 text-warning mx-auto mb-4" aria-hidden="true" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              No Matching Plans Found
            </h2>
            <p className="text-gray-600 mb-6">
              We couldn't find any plans that match your criteria. Try adjusting your preferences or location.
            </p>
            <button
              onClick={() => window.history.back()}
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Adjust Preferences
            </button>
          </div>
        </div>
      </div>
    );
  }

  const topPlans = recommendation.top_plans.slice(0, 3);
  const totalSavings = topPlans[0]?.savings?.annual_savings || 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header Section with Actions */}
        <header className="text-center mb-8" role="banner">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
            <CheckCircle className="w-8 h-8 text-primary-600" aria-hidden="true" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
            Your Personalized Plan Recommendations
          </h1>
          {totalSavings > 0 && (
            <p className="text-lg sm:text-xl text-gray-600">
              Save up to <span className="text-primary-600 font-bold">{formatCurrency(totalSavings)}</span> per year
            </p>
          )}
          <p className="text-sm text-gray-500 mt-2">
            Based on your usage patterns and preferences • {formatNumber(recommendation.total_plans_analyzed)} plans analyzed
          </p>

          {/* Action Buttons */}
          <div className="flex flex-wrap justify-center gap-3 mt-6 no-print">
            <PdfExport recommendation={recommendation} />
            {usageData.length > 0 && (
              <CsvExportUsage usageData={usageData} profile={recommendation.user_profile} />
            )}
            {selectedPlans.length >= 2 && (
              <Button variant="primary" onClick={handleCompare}>
                <BarChart3 className="w-4 h-4 mr-2" />
                Compare {selectedPlans.length} Plans
              </Button>
            )}
            <Button variant="outline" onClick={handleScenarios}>
              <Settings className="w-4 h-4 mr-2" />
              Explore Scenarios
            </Button>
          </div>
        </header>

        {/* Warnings */}
        {recommendation.warnings && recommendation.warnings.length > 0 && (
          <div
            className="mb-6 bg-warning-light border-l-4 border-warning rounded-lg p-4"
            role="alert"
            aria-live="polite"
          >
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-warning-dark mr-2 flex-shrink-0 mt-0.5" aria-hidden="true" />
              <div>
                <h3 className="text-sm font-medium text-warning-dark mb-1">
                  Important Notes:
                </h3>
                <ul className="text-sm text-warning-dark list-disc list-inside space-y-1">
                  {recommendation.warnings.map((warning, idx) => (
                    <li key={idx}>{warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* User Profile Summary with Badge */}
        <div className="mb-8">
          <UsageProfileBadge profile={recommendation.user_profile} />
        </div>

        {/* Usage Visualizations */}
        {usageData.length > 0 && (
          <section aria-labelledby="usage-analysis-heading" className="mb-8">
            <h2 id="usage-analysis-heading" className="text-2xl font-bold text-gray-900 mb-4">
              Usage Analysis
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <MonthlyUsageChart usageData={usageData} />
              <SeasonalPatternChart usageData={usageData} />
            </div>
          </section>
        )}

        {/* Top 3 Plan Cards */}
        <section aria-labelledby="top-plans-heading" className="mb-8">
          <h2 id="top-plans-heading" className="text-2xl font-bold text-gray-900 mb-4">
            Top Recommendations for You
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Select up to 3 plans to compare side-by-side
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {topPlans.map((plan) => (
              <div key={plan.plan_id} className="relative">
                <div className="absolute top-4 right-4 z-10 no-print">
                  <input
                    type="checkbox"
                    checked={isPlanSelected(plan.plan_id)}
                    onChange={(e) => handlePlanCheckbox(plan, e.target.checked)}
                    disabled={!isPlanSelected(plan.plan_id) && !canAddMore}
                    className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    aria-label={`Select ${plan.plan_name} for comparison`}
                  />
                </div>
                <PlanCard
                  plan={plan}
                  onSelect={setSelectedPlan}
                  isSelected={selectedPlan?.plan_id === plan.plan_id}
                  showRank={true}
                />
              </div>
            ))}
          </div>
        </section>

        {/* Cost Comparison Chart */}
        {selectedPlan && usageData.length > 0 && (
          <section aria-labelledby="cost-comparison-heading" className="mb-8">
            <h2 id="cost-comparison-heading" className="text-2xl font-bold text-gray-900 mb-4">
              Cost Comparison
            </h2>
            <CostComparisonChart
              recommendedPlan={selectedPlan}
              usageData={usageData}
            />
          </section>
        )}

        {/* Cost Breakdown for Selected Plan */}
        {selectedPlan && (
          <section aria-labelledby="cost-breakdown-heading" className="mb-8">
            <h2 id="cost-breakdown-heading" className="text-2xl font-bold text-gray-900 mb-4">
              Detailed Cost Analysis
            </h2>
            <CostBreakdown plan={selectedPlan} />
          </section>
        )}

        {/* Overall Recommendation Feedback */}
        <div className="bg-white rounded-lg shadow-card p-6 mb-8 no-print">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            How was your experience?
          </h3>
          <FeedbackWidget
            recommendationId={recommendation.recommendation_id}
            compact={false}
          />
        </div>

        {/* Next Steps CTA */}
        <div className="bg-primary-50 rounded-lg p-6 text-center">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Ready to Switch?
          </h3>
          <p className="text-gray-600 mb-4">
            Contact the supplier directly to sign up for your chosen plan
          </p>
          <button
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 min-h-[44px]"
            onClick={() => {
              if (selectedPlan) {
                alert('Contact: ' + selectedPlan.supplier_name);
              }
            }}
          >
            Get Started
          </button>
        </div>
      </div>
    </div>
  );
};

ResultsPage.displayName = 'ResultsPage';
