import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Leaf, Zap, Calendar, DollarSign } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/design-system';
import { FeedbackWidget } from '@/components/FeedbackWidget';
import type { RankedPlan } from '@/types/recommendation';
import {
  formatCurrency,
  formatPercentage,
  getSavingsLevel,
  getSavingsBadgeVariant
} from '@/utils/formatters';
import { clsx } from 'clsx';

export interface PlanCardProps {
  plan: RankedPlan;
  onSelect?: (plan: RankedPlan) => void;
  isSelected?: boolean;
  showRank?: boolean;
  recommendationId?: string;
}

export const PlanCard: React.FC<PlanCardProps> = ({
  plan,
  onSelect,
  isSelected = false,
  showRank = true,
  recommendationId,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const savingsLevel = plan.savings 
    ? getSavingsLevel(plan.savings.savings_percentage) 
    : 'none';
  const savingsBadgeVariant = getSavingsBadgeVariant(savingsLevel);

  const rankBadgeColor = {
    1: 'bg-primary-600 text-white',
    2: 'bg-primary-500 text-white',
    3: 'bg-primary-400 text-white',
  }[plan.rank] || 'bg-gray-400 text-white';

  const contractText = plan.contract_length_months === 0 
    ? 'Month-to-month' 
    : plan.contract_length_months + ' months';

  return (
    <Card
      hoverable
      className={clsx(
        'relative overflow-hidden transition-all',
        isSelected && 'ring-2 ring-primary-600 ring-offset-2'
      )}
      role="article"
      aria-label={'Plan recommendation ' + plan.rank + ': ' + plan.plan_name}
    >
      {showRank && (
        <div
          className={clsx(
            'absolute top-0 right-0 px-3 py-1 rounded-bl-lg font-bold text-sm',
            rankBadgeColor
          )}
          aria-label={'Ranked ' + plan.rank}
        >
          #{plan.rank}
        </div>
      )}

      <CardHeader>
        <div className="flex items-start justify-between pr-12">
          <div className="flex items-start gap-3 flex-1">
            {plan.supplier_logo_url && (
              <img
                src={plan.supplier_logo_url}
                alt={plan.supplier_name + ' logo'}
                className="w-12 h-12 object-contain rounded flex-shrink-0"
                onError={(e) => {
                  // Hide image on error
                  e.currentTarget.style.display = 'none';
                }}
              />
            )}
            <div className="flex-1 min-w-0">
              <CardTitle>{plan.plan_name}</CardTitle>
              <p className="text-sm text-gray-600 mt-1">{plan.supplier_name}</p>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Savings Badge */}
        {plan.savings && plan.savings.annual_savings > 0 && (
          <div className="mb-4">
            <Badge variant={savingsBadgeVariant} size="lg">
              Save {formatCurrency(plan.savings.annual_savings)}/year ({formatPercentage(plan.savings.savings_percentage)})
            </Badge>
          </div>
        )}

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-gray-400" aria-hidden="true" />
            <div>
              <p className="text-xs text-gray-500">Monthly Cost</p>
              <p className="font-semibold text-gray-900">
                {formatCurrency(plan.projected_monthly_cost)}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-400" aria-hidden="true" />
            <div>
              <p className="text-xs text-gray-500">Contract</p>
              <p className="font-semibold text-gray-900">{contractText}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-gray-400" aria-hidden="true" />
            <div>
              <p className="text-xs text-gray-500">Rate</p>
              <p className="font-semibold text-gray-900">
                {(typeof plan.average_rate_per_kwh === 'string'
                  ? parseFloat(plan.average_rate_per_kwh)
                  : plan.average_rate_per_kwh).toFixed(2)}¢/kWh
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Leaf className="w-5 h-5 text-renewable-700" aria-hidden="true" />
            <div>
              <p className="text-xs text-gray-500">Renewable</p>
              <p className="font-semibold text-renewable-700">
                {formatPercentage(plan.renewable_percentage)}
              </p>
            </div>
          </div>
        </div>

        {/* Plan Type & ETF */}
        <div className="flex gap-2 mb-4">
          <Badge variant="neutral" size="sm">
            {plan.plan_type}
          </Badge>
          {plan.renewable_percentage >= 50 && (
            <Badge variant="renewable" size="sm">
              Green Energy
            </Badge>
          )}
          {plan.early_termination_fee > 0 && (
            <Badge variant="warning" size="sm">
              ETF: {formatCurrency(plan.early_termination_fee)}
            </Badge>
          )}
        </div>

        {/* Expandable Explanation */}
        <div className="border-t border-gray-200 pt-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={clsx(
              'w-full flex items-center justify-between text-left',
              'text-primary-600 font-medium hover:text-primary-700',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded',
              'p-2 -m-2 min-h-[44px]'
            )}
            aria-expanded={isExpanded}
            aria-controls={'plan-explanation-' + plan.plan_id}
          >
            <span>Why this plan?</span>
            {isExpanded ? (
              <ChevronUp className="w-5 h-5" aria-hidden="true" />
            ) : (
              <ChevronDown className="w-5 h-5" aria-hidden="true" />
            )}
          </button>

          {isExpanded && (
            <div
              id={'plan-explanation-' + plan.plan_id}
              className="mt-3 text-sm text-gray-700 animate-fade-in"
            >
              <p className="mb-3">{plan.explanation}</p>

              {plan.key_differentiators.length > 0 && (
                <div className="mb-3">
                  <h4 className="font-medium text-gray-900 mb-1">Key Benefits:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {plan.key_differentiators.map((diff, idx) => (
                      <li key={idx}>{diff}</li>
                    ))}
                  </ul>
                </div>
              )}

              {plan.trade_offs.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-1">Trade-offs:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {plan.trade_offs.map((tradeOff, idx) => (
                      <li key={idx}>{tradeOff}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Select Button */}
        {onSelect && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => onSelect(plan)}
              className={clsx(
                'w-full min-h-[44px] px-4 py-2 rounded-lg font-medium',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                isSelected
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-primary-50 text-primary-600 hover:bg-primary-100'
              )}
              aria-pressed={isSelected}
            >
              {isSelected ? 'Selected' : 'Select This Plan'}
            </button>
          </div>
        )}

        {/* Feedback Widget */}
        <FeedbackWidget
          planId={plan.plan_id}
          recommendationId={recommendationId}
          compact={false}
        />
      </CardContent>
    </Card>
  );
};

PlanCard.displayName = 'PlanCard';
