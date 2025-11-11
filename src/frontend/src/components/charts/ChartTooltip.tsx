import React from 'react';
import { chartTooltipStyle } from './ChartTheme';

export interface ChartTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color?: string;
    unit?: string;
    payload?: any;
  }>;
  label?: string;
  formatter?: (value: number, name: string) => string;
  labelFormatter?: (label: string) => string;
}

export const ChartTooltip: React.FC<ChartTooltipProps> = ({
  active,
  payload,
  label,
  formatter,
  labelFormatter,
}) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const formattedLabel = labelFormatter ? labelFormatter(label || '') : label;

  return (
    <div
      style={chartTooltipStyle}
      className="chart-tooltip"
      role="tooltip"
      aria-live="polite"
    >
      {formattedLabel && (
        <p className="font-semibold text-gray-900 mb-2 text-sm">
          {formattedLabel}
        </p>
      )}
      <div className="space-y-1">
        {payload.map((entry, index) => {
          const formattedValue = formatter
            ? formatter(entry.value, entry.name)
            : `${entry.value}${entry.unit || ''}`;

          return (
            <div key={`item-${index}`} className="flex items-center gap-2 text-xs">
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: entry.color }}
                aria-hidden="true"
              />
              <span className="text-gray-600">{entry.name}:</span>
              <span className="font-semibold text-gray-900">{formattedValue}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

ChartTooltip.displayName = 'ChartTooltip';
