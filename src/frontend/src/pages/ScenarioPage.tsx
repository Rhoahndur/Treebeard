import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { ScenarioBuilder } from '@/components/scenarios/ScenarioBuilder';
import { ScenarioResults } from '@/components/scenarios/ScenarioResults';
import { ScenarioComparison } from '@/components/scenarios/ScenarioComparison';
import { WhatIfCalculator } from '@/components/scenarios/WhatIfCalculator';
import { useScenario } from '@/hooks/useScenario';
import type { GenerateRecommendationResponse } from '@/types/recommendation';

export const ScenarioPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const originalResults = location.state?.recommendation as GenerateRecommendationResponse;

  const {
    currentScenario,
    updateScenario,
    resetScenario,
    savedScenarios,
    saveScenario,
    loadScenario,
    deleteScenario,
    getShareUrl,
  } = useScenario(originalResults ? {
    cost_priority: 50,
    renewable_priority: 50,
    flexibility_priority: 50,
    rating_priority: 50,
  } : undefined);

  const [scenarioResults, setScenarioResults] = useState<GenerateRecommendationResponse | undefined>();

  const handleBack = () => {
    navigate(-1);
  };

  if (!originalResults) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            No Recommendation Data
          </h2>
          <p className="text-gray-600 mb-6">
            Please go to the results page first to access scenario modeling.
          </p>
          <button
            onClick={() => navigate('/')}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Results
          </button>

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Scenario Modeling
          </h1>
          <p className="text-gray-600">
            Explore different scenarios to understand how changes affect your recommendations
          </p>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Scenario Builder */}
          <ScenarioBuilder
            scenario={currentScenario}
            onUpdate={updateScenario}
            onReset={resetScenario}
            onSave={saveScenario}
            onShare={getShareUrl}
          />

          {/* Scenario Results */}
          <ScenarioResults
            originalResults={originalResults}
            scenarioResults={scenarioResults}
          />
        </div>

        {/* What-If Calculator */}
        {originalResults.top_plans.length >= 1 && (
          <div className="mb-6">
            <WhatIfCalculator
              currentPlan={originalResults.top_plans[0]}
              recommendedPlan={originalResults.top_plans[0]}
            />
          </div>
        )}

        {/* Saved Scenarios */}
        <ScenarioComparison
          scenarios={savedScenarios}
          onLoad={loadScenario}
          onDelete={deleteScenario}
        />
      </div>
    </div>
  );
};

ScenarioPage.displayName = 'ScenarioPage';
