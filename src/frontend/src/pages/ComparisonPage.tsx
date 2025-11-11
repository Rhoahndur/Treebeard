import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ComparisonView } from '@/components/comparison/ComparisonView';
import { ComparisonTable } from '@/components/comparison/ComparisonTable';
import { ComparisonCharts } from '@/components/comparison/ComparisonCharts';
import { TradeOffAnalyzer } from '@/components/comparison/TradeOffAnalyzer';
import { CsvExportComparison } from '@/components/export/CsvExportComparison';
import type { RankedPlan } from '@/types/recommendation';

export const ComparisonPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Get selected plans from location state
  const selectedPlans = (location.state?.selectedPlans || []) as RankedPlan[];

  const handleRemovePlan = (planId: string) => {
    const updatedPlans = selectedPlans.filter((p) => p.plan_id !== planId);
    navigate('/comparison', { state: { selectedPlans: updatedPlans } });
  };

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <>
      <link rel="stylesheet" href="/src/styles/print.css" media="print" />
      <ComparisonView
        plans={selectedPlans}
        onRemovePlan={handleRemovePlan}
        onBack={handleBack}
      >
        {/* Export Button */}
        {selectedPlans.length > 0 && (
          <div className="flex justify-end mb-6 no-print">
            <CsvExportComparison plans={selectedPlans} />
          </div>
        )}

        {/* Comparison Table */}
        {selectedPlans.length > 0 && (
          <ComparisonTable plans={selectedPlans} />
        )}

        {/* Comparison Charts */}
        {selectedPlans.length > 0 && (
          <div className="page-break-before">
            <ComparisonCharts plans={selectedPlans} />
          </div>
        )}

        {/* Trade-Off Analyzer (for 2 plans) */}
        {selectedPlans.length === 2 && (
          <div className="page-break-before">
            <TradeOffAnalyzer
              planA={selectedPlans[0]}
              planB={selectedPlans[1]}
            />
          </div>
        )}

        {/* Multiple Trade-Off Comparisons (for 3 plans) */}
        {selectedPlans.length === 3 && (
          <div className="page-break-before space-y-6">
            <TradeOffAnalyzer
              planA={selectedPlans[0]}
              planB={selectedPlans[1]}
            />
            <TradeOffAnalyzer
              planA={selectedPlans[0]}
              planB={selectedPlans[2]}
            />
            <TradeOffAnalyzer
              planA={selectedPlans[1]}
              planB={selectedPlans[2]}
            />
          </div>
        )}
      </ComparisonView>
    </>
  );
};

ComparisonPage.displayName = 'ComparisonPage';
