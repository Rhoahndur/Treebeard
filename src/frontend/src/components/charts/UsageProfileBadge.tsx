import React from 'react';
import { TrendingUp, TrendingDown, Activity, Zap } from 'lucide-react';
import type { UserProfile } from '@/types/recommendation';

export interface UsageProfileBadgeProps {
  profile: UserProfile;
  className?: string;
}

const profileConfig = {
  baseline: {
    icon: Activity,
    color: 'blue',
    label: 'Baseline User',
    description: 'Consistent usage throughout the year',
  },
  seasonal: {
    icon: TrendingUp,
    color: 'orange',
    label: 'Seasonal User',
    description: 'Usage varies significantly by season',
  },
  high_user: {
    icon: Zap,
    color: 'red',
    label: 'High Usage',
    description: 'Above-average energy consumption',
  },
  variable: {
    icon: TrendingDown,
    color: 'purple',
    label: 'Variable User',
    description: 'Unpredictable usage patterns',
  },
  low_user: {
    icon: Activity,
    color: 'green',
    label: 'Low Usage',
    description: 'Below-average energy consumption',
  },
};

export const UsageProfileBadge: React.FC<UsageProfileBadgeProps> = ({
  profile,
  className = '',
}) => {
  const config = profileConfig[profile.profile_type as keyof typeof profileConfig] || profileConfig.baseline;
  const Icon = config.icon;

  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    green: 'bg-green-50 text-green-700 border-green-200',
  };

  const iconColorClasses = {
    blue: 'text-blue-600',
    orange: 'text-orange-600',
    red: 'text-red-600',
    purple: 'text-purple-600',
    green: 'text-green-600',
  };

  return (
    <div
      className={`inline-flex items-start gap-3 px-4 py-3 rounded-lg border-2 ${
        colorClasses[config.color as keyof typeof colorClasses]
      } ${className}`}
      role="status"
      aria-label={`Usage profile: ${config.label}`}
    >
      <div className="flex-shrink-0 mt-0.5">
        <Icon
          className={`w-5 h-5 ${iconColorClasses[config.color as keyof typeof iconColorClasses]}`}
          aria-hidden="true"
        />
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-sm mb-0.5">{config.label}</div>
        <div className="text-xs opacity-90">
          {config.description}
          {profile.has_seasonal_pattern && profile.profile_type !== 'seasonal' && (
            <span> with seasonal variations</span>
          )}
        </div>
        <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="opacity-75">Annual: </span>
            <span className="font-medium">
              {profile.projected_annual_kwh.toLocaleString()} kWh
            </span>
          </div>
          <div>
            <span className="opacity-75">Confidence: </span>
            <span className="font-medium">
              {(profile.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

UsageProfileBadge.displayName = 'UsageProfileBadge';
