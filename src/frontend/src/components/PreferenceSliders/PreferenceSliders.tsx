import React from 'react';
import clsx from 'clsx';
import type { Preferences, PresetProfile } from '@/types/onboarding';
import { adjustPreferences, PRESET_CONFIGS } from '@/utils/presets';

interface PreferenceSlidersProps {
  preferences: Preferences;
  onChange: (preferences: Preferences) => void;
  className?: string;
}

interface SliderConfig {
  key: keyof Preferences;
  label: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const SLIDERS: SliderConfig[] = [
  {
    key: 'cost_priority',
    label: 'Cost Savings',
    description: 'Minimize your monthly bill',
    color: 'bg-blue-500',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  {
    key: 'flexibility_priority',
    label: 'Contract Flexibility',
    description: 'Short-term or month-to-month options',
    color: 'bg-purple-500',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
        />
      </svg>
    ),
  },
  {
    key: 'renewable_priority',
    label: 'Renewable Energy',
    description: 'Solar, wind, and clean energy sources',
    color: 'bg-green-500',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  {
    key: 'rating_priority',
    label: 'Supplier Rating',
    description: 'Customer reviews and reliability',
    color: 'bg-amber-500',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
        />
      </svg>
    ),
  },
];

export const PreferenceSliders: React.FC<PreferenceSlidersProps> = ({
  preferences,
  onChange,
  className,
}) => {
  const handleSliderChange = (key: keyof Preferences, value: number) => {
    const adjusted = adjustPreferences(preferences, key, value);
    onChange(adjusted);
  };

  const handlePresetClick = (profile: PresetProfile) => {
    onChange(PRESET_CONFIGS[profile].preferences);
  };

  const sum =
    preferences.cost_priority +
    preferences.flexibility_priority +
    preferences.renewable_priority +
    preferences.rating_priority;

  const isValid = Math.abs(sum - 100) < 0.01;

  return (
    <div className={clsx('space-y-6', className)}>
      {/* Preset buttons */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Presets</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(Object.keys(PRESET_CONFIGS) as PresetProfile[]).map((profile) => {
            const config = PRESET_CONFIGS[profile];
            return (
              <button
                key={profile}
                type="button"
                onClick={() => handlePresetClick(profile)}
                className="px-4 py-3 text-sm font-medium text-gray-700 bg-white border-2 border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all"
              >
                <div className="font-semibold">{config.name}</div>
                <div className="text-xs text-gray-500 mt-1">{config.description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Sliders */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Or customize your priorities</h3>
        <div className="space-y-6">
          {SLIDERS.map((slider) => {
            const value = preferences[slider.key];
            return (
              <div key={slider.key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={clsx('p-1.5 rounded-lg text-white', slider.color)}>
                      {slider.icon}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">{slider.label}</div>
                      <div className="text-xs text-gray-500">{slider.description}</div>
                    </div>
                  </div>
                  <div className="text-lg font-bold text-gray-900 w-16 text-right">
                    {Math.round(value)}%
                  </div>
                </div>

                <div className="relative">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={value}
                    onChange={(e) =>
                      handleSliderChange(slider.key, parseInt(e.target.value, 10))
                    }
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    style={{
                      background: `linear-gradient(to right, ${slider.color.replace('bg-', 'rgb(var(--color-')} 0%, ${slider.color.replace('bg-', 'rgb(var(--color-')} ${value}%, rgb(229, 231, 235) ${value}%, rgb(229, 231, 235) 100%)`,
                    }}
                    aria-label={`${slider.label} priority`}
                    aria-valuenow={value}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  />
                </div>

                {/* Visual bar */}
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={clsx('h-full transition-all duration-300', slider.color)}
                    style={{ width: `${value}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sum indicator */}
      <div
        className={clsx(
          'p-4 rounded-lg border-2 transition-all',
          isValid
            ? 'bg-green-50 border-green-200'
            : 'bg-amber-50 border-amber-200'
        )}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isValid ? (
              <svg
                className="w-5 h-5 text-green-600"
                fill="currentColor"
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg
                className="w-5 h-5 text-amber-600"
                fill="currentColor"
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            <span
              className={clsx(
                'text-sm font-medium',
                isValid ? 'text-green-800' : 'text-amber-800'
              )}
            >
              {isValid
                ? 'Priorities balanced correctly'
                : 'Priorities must total 100%'}
            </span>
          </div>
          <span
            className={clsx(
              'text-lg font-bold',
              isValid ? 'text-green-900' : 'text-amber-900'
            )}
          >
            {Math.round(sum)}%
          </span>
        </div>
      </div>
    </div>
  );
};
