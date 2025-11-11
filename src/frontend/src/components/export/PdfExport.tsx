import React, { useRef } from 'react';
import { FileDown } from 'lucide-react';
import { jsPDF } from 'jspdf';
import { Button } from '@/components/design-system';
import type { GenerateRecommendationResponse } from '@/types/recommendation';
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/formatters';

export interface PdfExportProps {
  recommendation: GenerateRecommendationResponse;
  onExport?: () => void;
}

export const PdfExport: React.FC<PdfExportProps> = ({
  recommendation,
  onExport,
}) => {
  const handleExport = async () => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    let yPos = 20;

    // Helper to add text with word wrap
    const addText = (text: string, size: number = 10, isBold: boolean = false) => {
      doc.setFontSize(size);
      doc.setFont('helvetica', isBold ? 'bold' : 'normal');
      const lines = doc.splitTextToSize(text, pageWidth - 40);
      doc.text(lines, 20, yPos);
      yPos += lines.length * (size / 2) + 5;
    };

    // Header
    doc.setFillColor(59, 130, 246); // Primary blue
    doc.rect(0, 0, pageWidth, 40, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('TreeBeard Energy Recommendation Report', pageWidth / 2, 25, {
      align: 'center',
    });
    doc.setTextColor(0, 0, 0);

    yPos = 50;

    // Date
    addText(`Generated: ${new Date().toLocaleDateString()}`, 10);
    yPos += 5;

    // Executive Summary
    addText('EXECUTIVE SUMMARY', 14, true);
    const topPlan = recommendation.top_plans[0];
    if (topPlan) {
      addText(`Top Recommendation: ${topPlan.plan_name}`, 12, true);
      addText(`Supplier: ${topPlan.supplier_name}`, 10);
      addText(
        `Projected Annual Cost: ${formatCurrency(topPlan.projected_annual_cost)}`,
        10
      );
      if (topPlan.savings) {
        addText(
          `Annual Savings: ${formatCurrency(topPlan.savings.annual_savings)} (${formatPercentage(topPlan.savings.savings_percentage)}%)`,
          10,
          true
        );
      }
    }
    yPos += 10;

    // User Profile
    addText('YOUR ENERGY PROFILE', 14, true);
    addText(
      `Profile Type: ${recommendation.user_profile.profile_type.replace(/_/g, ' ')}`,
      10
    );
    addText(
      `Annual Usage: ${formatNumber(recommendation.user_profile.projected_annual_kwh)} kWh`,
      10
    );
    addText(
      `Monthly Average: ${formatNumber(recommendation.user_profile.mean_monthly_kwh)} kWh`,
      10
    );
    yPos += 10;

    // Top 3 Plans
    addText('TOP 3 RECOMMENDED PLANS', 14, true);
    recommendation.top_plans.slice(0, 3).forEach((plan, idx) => {
      if (yPos > pageHeight - 60) {
        doc.addPage();
        yPos = 20;
      }

      addText(`#${idx + 1}: ${plan.plan_name}`, 12, true);
      addText(`Supplier: ${plan.supplier_name}`, 10);
      addText(`Rate: ${plan.average_rate_per_kwh.toFixed(2)}¢/kWh`, 10);
      addText(`Monthly Cost: ${formatCurrency(plan.projected_monthly_cost)}`, 10);
      addText(`Annual Cost: ${formatCurrency(plan.projected_annual_cost)}`, 10);
      addText(`Renewable: ${formatPercentage(plan.renewable_percentage)}%`, 10);
      addText(
        `Contract: ${plan.contract_length_months === 0 ? 'Month-to-month' : plan.contract_length_months + ' months'}`,
        10
      );
      addText(`Explanation: ${plan.explanation}`, 9);
      yPos += 5;
    });

    // Footer on each page
    const totalPages = doc.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text(
        'Generated with TreeBeard • claude.com/claude-code',
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );
      doc.text(`Page ${i} of ${totalPages}`, pageWidth - 20, pageHeight - 10, {
        align: 'right',
      });
    }

    // Save
    const fileName = `treebeard-recommendation-${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(fileName);

    onExport?.();
  };

  return (
    <Button variant="primary" onClick={handleExport}>
      <FileDown className="w-4 h-4 mr-2" />
      Download PDF Report
    </Button>
  );
};

PdfExport.displayName = 'PdfExport';
