import React from 'react';
import { FileDown } from 'lucide-react';
import Papa from 'papaparse';
import { Button } from '@/components/design-system';
import type { RankedPlan } from '@/types/recommendation';
import { formatCurrency, formatPercentage } from '@/utils/formatters';

export interface CsvExportComparisonProps {
  plans: RankedPlan[];
}

export const CsvExportComparison: React.FC<CsvExportComparisonProps> = ({
  plans,
}) => {
  const handleExport = () => {
    const attributes = [
      'Plan Name',
      'Supplier',
      'Annual Cost',
      'Monthly Cost',
      'Rate (¢/kWh)',
      'Contract (months)',
      'Renewable %',
      'ETF',
      'Annual Savings',
      'Plan Type',
    ];

    const csvData = [
      attributes,
      ...plans.map((plan) => [
        plan.plan_name,
        plan.supplier_name,
        formatCurrency(plan.projected_annual_cost),
        formatCurrency(plan.projected_monthly_cost),
        plan.average_rate_per_kwh.toFixed(2),
        plan.contract_length_months.toString(),
        formatPercentage(plan.renewable_percentage),
        formatCurrency(plan.early_termination_fee),
        plan.savings
          ? formatCurrency(plan.savings.annual_savings)
          : 'N/A',
        plan.plan_type,
      ]),
    ];

    const csv = Papa.unparse(csvData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute(
      'download',
      `treebeard-comparison-${new Date().toISOString().split('T')[0]}.csv`
    );
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Button variant="secondary" onClick={handleExport}>
      <FileDown className="w-4 h-4 mr-2" />
      Download Comparison (CSV)
    </Button>
  );
};

CsvExportComparison.displayName = 'CsvExportComparison';
