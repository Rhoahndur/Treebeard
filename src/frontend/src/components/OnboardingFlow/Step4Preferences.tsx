import React, { useState } from 'react';
import type { Preferences } from '@/types/onboarding';
import { PreferenceSliders } from '../PreferenceSliders/PreferenceSliders';

interface Step4PreferencesProps {
  initialData?: Partial<Preferences>;
  onSubmit: (data: Preferences) => void;
  onBack: () => void;
  isSubmitting?: boolean;
}

export const Step4Preferences: React.FC<Step4PreferencesProps> = ({
  initialData,
  onSubmit,
  onBack,
  isSubmitting = false,
}) => {
  const [preferences, setPreferences] = useState<Preferences>({
    cost_priority: 25,
    flexibility_priority: 25,
    renewable_priority: 25,
    rating_priority: 25,
    ...initialData,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(preferences);
  };

  const sum =
    preferences.cost_priority +
    preferences.flexibility_priority +
    preferences.renewable_priority +
    preferences.rating_priority;

  const isValid = Math.abs(sum - 100) < 0.01;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">What matters most to you?</h2>
        <p className="text-gray-600">
          Tell us your priorities so we can recommend plans that match your values. You can use a
          preset or customize the sliders.
        </p>
      </div>

      <PreferenceSliders preferences={preferences} onChange={setPreferences} />

      {/* Info box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">How this works</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Your priorities help us rank energy plans. For example, if you prioritize cost
                savings at 60%, we'll emphasize lower rates over other factors. Don't worry - you
                can always adjust these later!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6">
        <button
          type="button"
          onClick={onBack}
          disabled={isSubmitting}
          className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Back
        </button>
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="px-6 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {isSubmitting ? (
            <>
              <svg
                className="animate-spin h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Generating Recommendations...
            </>
          ) : (
            'Get Recommendations'
          )}
        </button>
      </div>
    </form>
  );
};
