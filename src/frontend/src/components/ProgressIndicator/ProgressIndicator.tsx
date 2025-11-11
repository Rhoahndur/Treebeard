import React from 'react';
import clsx from 'clsx';
import type { OnboardingStep } from '@/types/onboarding';

interface ProgressIndicatorProps {
  currentStep: OnboardingStep;
  completedSteps: OnboardingStep[];
  className?: string;
}

const STEPS = [
  { number: 1, label: 'Your Info' },
  { number: 2, label: 'Current Plan' },
  { number: 3, label: 'Usage Data' },
  { number: 4, label: 'Preferences' },
] as const;

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  currentStep,
  completedSteps,
  className,
}) => {
  const getStepStatus = (stepNumber: OnboardingStep) => {
    if (completedSteps.includes(stepNumber)) return 'completed';
    if (stepNumber === currentStep) return 'active';
    return 'pending';
  };

  return (
    <div className={clsx('w-full', className)}>
      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Step {currentStep} of {STEPS.length}
          </span>
          <span className="text-sm text-gray-500">
            {Math.round((completedSteps.length / STEPS.length) * 100)}% complete
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-300 ease-in-out"
            style={{ width: `${(completedSteps.length / STEPS.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Step indicators */}
      <div className="hidden md:flex items-center justify-between">
        {STEPS.map((step, index) => {
          const status = getStepStatus(step.number as OnboardingStep);
          const isLast = index === STEPS.length - 1;

          return (
            <React.Fragment key={step.number}>
              <div className="flex flex-col items-center">
                <div
                  className={clsx(
                    'w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all duration-300',
                    {
                      'bg-primary-600 text-white': status === 'completed',
                      'bg-primary-500 text-white ring-4 ring-primary-100': status === 'active',
                      'bg-gray-200 text-gray-500': status === 'pending',
                    }
                  )}
                >
                  {status === 'completed' ? (
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={3}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    step.number
                  )}
                </div>
                <span
                  className={clsx('mt-2 text-xs font-medium text-center whitespace-nowrap', {
                    'text-primary-700': status === 'active',
                    'text-gray-900': status === 'completed',
                    'text-gray-500': status === 'pending',
                  })}
                >
                  {step.label}
                </span>
              </div>

              {!isLast && (
                <div
                  className={clsx('flex-1 h-0.5 mx-2 transition-all duration-300', {
                    'bg-primary-600': completedSteps.includes(step.number as OnboardingStep),
                    'bg-gray-200': !completedSteps.includes(step.number as OnboardingStep),
                  })}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Mobile step indicator */}
      <div className="md:hidden flex items-center justify-center gap-2 mt-4">
        {STEPS.map((step) => (
          <div
            key={step.number}
            className={clsx('h-2 flex-1 rounded-full transition-all duration-300', {
              'bg-primary-600': completedSteps.includes(step.number as OnboardingStep),
              'bg-primary-400':
                step.number === currentStep &&
                !completedSteps.includes(step.number as OnboardingStep),
              'bg-gray-200':
                step.number !== currentStep &&
                !completedSteps.includes(step.number as OnboardingStep),
            })}
          />
        ))}
      </div>
    </div>
  );
};
