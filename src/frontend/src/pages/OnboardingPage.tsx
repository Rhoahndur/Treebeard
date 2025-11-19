import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type {
  OnboardingState,
  OnboardingStep,
  UserInfo,
  CurrentPlan,
  MonthlyUsage,
  Preferences,
} from '@/types/onboarding';
import { Header } from '@/components/Header';
import { ProgressIndicator } from '@/components/ProgressIndicator/ProgressIndicator';
import { Step1UserInfo } from '@/components/OnboardingFlow/Step1UserInfo';
import { Step2CurrentPlan } from '@/components/OnboardingFlow/Step2CurrentPlan';
import { Step3UsageData } from '@/components/OnboardingFlow/Step3UsageData';
import { Step4Preferences } from '@/components/OnboardingFlow/Step4Preferences';
import { LoadingScreen } from '@/components/LoadingScreen/LoadingScreen';
import { useAutoSave } from '@/hooks/useAutoSave';
import {
  loadOnboardingData,
  clearOnboardingData,
  hasSavedData,
} from '@/utils/localStorage';
import { recommendationsApi } from '@/api/recommendations';
import type { GenerateRecommendationRequest } from '@/types/api';

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRestorePrompt, setShowRestorePrompt] = useState(false);

  const [formData, setFormData] = useState<OnboardingState>({
    currentStep: 1,
    completedSteps: [],
    user: {
      email: '',
      zip_code: '',
      property_type: 'residential',
    },
    current_plan: {
      supplier_name: '',
      current_rate: 0,
      contract_end_date: '',
      early_termination_fee: 0,
      monthly_fee: 0,
    },
    usage_data: [],
    preferences: {
      cost_priority: 25,
      flexibility_priority: 25,
      renewable_priority: 25,
      rating_priority: 25,
    },
  });

  // Auto-save hook
  const { isSaving, lastSaved } = useAutoSave(formData, {
    delay: 500,
    enabled: !isSubmitting,
  });

  // Check for saved data on mount
  useEffect(() => {
    if (hasSavedData()) {
      setShowRestorePrompt(true);
    }
  }, []);

  const handleRestoreData = () => {
    const savedData = loadOnboardingData();
    if (savedData) {
      setFormData(savedData);
    }
    setShowRestorePrompt(false);
  };

  const handleDiscardData = () => {
    clearOnboardingData();
    setShowRestorePrompt(false);
  };

  const goToStep = (step: OnboardingStep) => {
    setFormData((prev) => ({ ...prev, currentStep: step }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const markStepCompleted = (step: OnboardingStep) => {
    setFormData((prev) => ({
      ...prev,
      completedSteps: prev.completedSteps.includes(step)
        ? prev.completedSteps
        : [...prev.completedSteps, step],
    }));
  };

  const handleStep1Submit = (data: UserInfo) => {
    setFormData((prev) => ({ ...prev, user: data }));
    markStepCompleted(1);
    goToStep(2);
  };

  const handleStep2Submit = (data: CurrentPlan) => {
    setFormData((prev) => ({ ...prev, current_plan: data }));
    markStepCompleted(2);
    goToStep(3);
  };

  const handleStep3Submit = (data: MonthlyUsage[]) => {
    setFormData((prev) => ({ ...prev, usage_data: data }));
    markStepCompleted(3);
    goToStep(4);
  };

  const handleStep4Submit = async (data: Preferences) => {
    setFormData((prev) => ({ ...prev, preferences: data }));
    markStepCompleted(4);
    setIsSubmitting(true);
    setError(null);

    try {
      // Prepare request payload
      const request: GenerateRecommendationRequest = {
        user_data: {
          zip_code: formData.user.zip_code,
          property_type: formData.user.property_type,
        },
        usage_data: formData.usage_data,
        preferences: data,
        current_plan: {
          supplier_name: formData.current_plan.supplier_name,
          current_rate: formData.current_plan.current_rate,
          contract_end_date: formData.current_plan.contract_end_date,
          early_termination_fee: formData.current_plan.early_termination_fee,
        },
      };

      // Call API
      const response = await recommendationsApi.generate(request);

      // Clear saved data on successful submission
      clearOnboardingData();

      // Navigate to results page with recommendation data
      navigate('/results', {
        state: {
          recommendation: response,
          userEmail: formData.user.email,
        },
      });
    } catch (err: any) {
      console.error('Failed to generate recommendations:', err);
      setError(
        err.response?.data?.message ||
          'Failed to generate recommendations. Please try again.'
      );
      setIsSubmitting(false);
    }
  };

  if (isSubmitting) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header showBack={false} showHome={false} showLogout={false} />

      <div className="py-8">
      {/* Restore prompt */}
      {showRestorePrompt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Continue where you left off?
            </h3>
            <p className="text-gray-600 mb-6">
              We found saved data from your previous session. Would you like to continue or
              start fresh?
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleDiscardData}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Start Fresh
              </button>
              <button
                onClick={handleRestoreData}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Find Your Perfect Energy Plan
          </h1>
          <p className="text-gray-600">
            Answer a few questions to get personalized recommendations
          </p>
        </div>

        {/* Progress Indicator */}
        <ProgressIndicator
          currentStep={formData.currentStep}
          completedSteps={formData.completedSteps}
          className="mb-8"
        />

        {/* Auto-save indicator */}
        {isSaving && (
          <div className="flex items-center justify-end text-sm text-gray-500 mb-4">
            <svg
              className="animate-spin h-4 w-4 mr-1"
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
            Saving...
          </div>
        )}
        {!isSaving && lastSaved && (
          <div className="flex items-center justify-end text-sm text-green-600 mb-4">
            <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            Saved
          </div>
        )}

        {/* Form Card */}
        <div className="bg-white rounded-lg shadow-md p-6 md:p-8">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4" role="alert">
              <div className="flex">
                <svg
                  className="h-5 w-5 text-red-400 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                  <button
                    onClick={() => handleStep4Submit(formData.preferences)}
                    className="mt-2 text-sm font-medium text-red-600 hover:text-red-700 underline"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          )}

          {formData.currentStep === 1 && (
            <Step1UserInfo
              initialData={formData.user}
              onSubmit={handleStep1Submit}
            />
          )}

          {formData.currentStep === 2 && (
            <Step2CurrentPlan
              initialData={formData.current_plan}
              onSubmit={handleStep2Submit}
              onBack={() => goToStep(1)}
            />
          )}

          {formData.currentStep === 3 && (
            <Step3UsageData
              initialData={formData.usage_data}
              onSubmit={handleStep3Submit}
              onBack={() => goToStep(2)}
            />
          )}

          {formData.currentStep === 4 && (
            <Step4Preferences
              initialData={formData.preferences}
              onSubmit={handleStep4Submit}
              onBack={() => goToStep(3)}
              isSubmitting={isSubmitting}
            />
          )}
        </div>

        {/* Privacy note */}
        <p className="text-center text-sm text-gray-500 mt-6">
          Your data is encrypted and secure. We never share your information with third parties.
        </p>
      </div>
      </div>
    </div>
  );
};
