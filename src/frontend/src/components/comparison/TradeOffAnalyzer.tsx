import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import type { RankedPlan } from '@/types/recommendation';
import { formatCurrency, formatPercentage } from '@/utils/formatters';

export interface TradeOffAnalyzerProps {
  planA: RankedPlan;
  planB: RankedPlan;
}

interface TradeOffItem {
  type: 'gain' | 'loss';
  label: string;
  description: string;
}

export const TradeOffAnalyzer: React.FC<TradeOffAnalyzerProps> = ({
  planA,
  planB,
}) => {
  const tradeOffs = useMemo(() => {
    const gains: TradeOffItem[] = [];
    const losses: TradeOffItem[] = [];

    // Cost comparison
    const costDiff = planA.projected_annual_cost - planB.projected_annual_cost;
    if (costDiff > 0) {
      gains.push({
        type: 'gain',
        label: 'Lower Cost',
        description: `Save ${formatCurrency(costDiff)}/year`,
      });
    } else if (costDiff < 0) {
      losses.push({
        type: 'loss',
        label: 'Higher Cost',
        description: `Pay ${formatCurrency(Math.abs(costDiff))}/year more`,
      });
    }

    // Contract flexibility
    if (planA.contract_length_months > planB.contract_length_months) {
      if (planB.contract_length_months === 0) {
        gains.push({
          type: 'gain',
          label: 'More Flexibility',
          description: 'Switch to month-to-month contract',
        });
      } else {
        gains.push({
          type: 'gain',
          label: 'Shorter Contract',
          description: `${planA.contract_length_months - planB.contract_length_months} months shorter commitment`,
        });
      }
    } else if (planA.contract_length_months < planB.contract_length_months) {
      if (planA.contract_length_months === 0) {
        losses.push({
          type: 'loss',
          label: 'Less Flexibility',
          description: `Commit to ${planB.contract_length_months}-month contract`,
        });
      } else {
        losses.push({
          type: 'loss',
          label: 'Longer Contract',
          description: `${planB.contract_length_months - planA.contract_length_months} months longer commitment`,
        });
      }
    }

    // Renewable energy
    const renewableDiff = planB.renewable_percentage - planA.renewable_percentage;
    if (renewableDiff > 10) {
      gains.push({
        type: 'gain',
        label: 'More Renewable Energy',
        description: `${formatPercentage(renewableDiff)}% more renewable energy`,
      });
    } else if (renewableDiff < -10) {
      losses.push({
        type: 'loss',
        label: 'Less Renewable Energy',
        description: `${formatPercentage(Math.abs(renewableDiff))}% less renewable energy`,
      });
    }

    // Early termination fee
    const etfDiff = planB.early_termination_fee - planA.early_termination_fee;
    if (etfDiff < 0) {
      gains.push({
        type: 'gain',
        label: 'Lower ETF',
        description: planB.early_termination_fee === 0
          ? 'No early termination fee'
          : `${formatCurrency(Math.abs(etfDiff))} lower ETF`,
      });
    } else if (etfDiff > 0) {
      losses.push({
        type: 'loss',
        label: 'Higher ETF',
        description: `${formatCurrency(etfDiff)} higher early termination fee`,
      });
    }

    // Rate stability
    const planAIsFixed = planA.plan_type.toLowerCase().includes('fixed');
    const planBIsFixed = planB.plan_type.toLowerCase().includes('fixed');
    if (!planAIsFixed && planBIsFixed) {
      gains.push({
        type: 'gain',
        label: 'Rate Stability',
        description: 'Switch to fixed-rate plan for predictable costs',
      });
    } else if (planAIsFixed && !planBIsFixed) {
      losses.push({
        type: 'loss',
        label: 'Rate Uncertainty',
        description: 'Variable rates may fluctuate with market conditions',
      });
    }

    // Monthly fees
    const feeA = planA.monthly_fee || 0;
    const feeB = planB.monthly_fee || 0;
    const feeDiff = feeB - feeA;
    if (feeDiff < -5) {
      gains.push({
        type: 'gain',
        label: 'Lower Monthly Fees',
        description: `Save ${formatCurrency(Math.abs(feeDiff))}/month in fees`,
      });
    } else if (feeDiff > 5) {
      losses.push({
        type: 'loss',
        label: 'Higher Monthly Fees',
        description: `Pay ${formatCurrency(feeDiff)}/month more in fees`,
      });
    }

    return { gains, losses };
  }, [planA, planB]);

  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-2">
        Trade-Off Analysis
      </h2>
      <p className="text-sm text-gray-600 mb-6">
        What changes when switching from <span className="font-medium">{planA.plan_name}</span> to{' '}
        <span className="font-medium">{planB.plan_name}</span>
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Gains Column */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-green-900">
              Gains ({tradeOffs.gains.length})
            </h3>
          </div>
          {tradeOffs.gains.length > 0 ? (
            <div className="space-y-3">
              {tradeOffs.gains.map((item, index) => (
                <div
                  key={index}
                  className="p-3 bg-green-50 border-l-4 border-green-500 rounded"
                >
                  <div className="font-medium text-green-900 text-sm mb-1">
                    {item.label}
                  </div>
                  <div className="text-xs text-green-700">{item.description}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">No significant gains identified</p>
          )}
        </div>

        {/* Trade-Offs Column */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingDown className="w-5 h-5 text-orange-600" />
            <h3 className="font-semibold text-orange-900">
              Trade-Offs ({tradeOffs.losses.length})
            </h3>
          </div>
          {tradeOffs.losses.length > 0 ? (
            <div className="space-y-3">
              {tradeOffs.losses.map((item, index) => (
                <div
                  key={index}
                  className="p-3 bg-orange-50 border-l-4 border-orange-500 rounded"
                >
                  <div className="font-medium text-orange-900 text-sm mb-1">
                    {item.label}
                  </div>
                  <div className="text-xs text-orange-700">{item.description}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">No significant trade-offs identified</p>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-center gap-3 text-sm">
          <span className="font-medium text-gray-700">{planA.plan_name}</span>
          <ArrowRight className="w-4 h-4 text-gray-400" />
          <span className="font-medium text-gray-700">{planB.plan_name}</span>
        </div>
        <p className="text-xs text-gray-500 text-center mt-2">
          {tradeOffs.gains.length > tradeOffs.losses.length
            ? 'This switch appears favorable overall'
            : tradeOffs.gains.length < tradeOffs.losses.length
            ? 'Consider if the trade-offs are worth the gains'
            : 'This switch has balanced trade-offs'}
        </p>
      </div>
    </div>
  );
};

TradeOffAnalyzer.displayName = 'TradeOffAnalyzer';
