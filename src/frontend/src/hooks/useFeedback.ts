/**
 * Custom hook for feedback submission.
 *
 * Handles feedback submission with error handling, retry logic, and rate limiting.
 *
 * Story 8.1: Feedback Collection UI
 */

import { useState, useCallback } from 'react';
import { apiClient } from '@/api/client';
import type {
  PlanFeedbackData,
  RecommendationFeedbackData,
  FeedbackSubmissionResponse,
  FeedbackRating,
  FeedbackType,
} from '@/types/feedback';

interface UseFeedbackOptions {
  /** Callback fired after successful submission */
  onSuccess?: (response: FeedbackSubmissionResponse) => void;
  /** Callback fired on error */
  onError?: (error: string) => void;
  /** Maximum retry attempts on failure */
  maxRetries?: number;
}

interface UseFeedbackReturn {
  /** Submit feedback on a specific plan */
  submitPlanFeedback: (data: PlanFeedbackData) => Promise<void>;
  /** Submit feedback on overall recommendation */
  submitRecommendationFeedback: (data: RecommendationFeedbackData) => Promise<void>;
  /** Whether a submission is in progress */
  isSubmitting: boolean;
  /** Error message if submission failed */
  error: string | null;
  /** Whether submission was successful */
  isSuccess: boolean;
  /** Reset the state */
  reset: () => void;
}

/**
 * Hook for managing feedback submission.
 *
 * @example
 * ```tsx
 * const { submitPlanFeedback, isSubmitting, error } = useFeedback({
 *   onSuccess: (response) => console.log('Feedback submitted!', response),
 *   onError: (error) => console.error('Failed:', error),
 * });
 *
 * const handleSubmit = async () => {
 *   await submitPlanFeedback({
 *     plan_id: 'plan-123',
 *     rating: 5,
 *     feedback_text: 'Great plan!',
 *     feedback_type: 'helpful',
 *   });
 * };
 * ```
 */
export function useFeedback(options: UseFeedbackOptions = {}): UseFeedbackReturn {
  const { onSuccess, onError, maxRetries = 2 } = options;

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  /**
   * Reset submission state.
   */
  const reset = useCallback(() => {
    setError(null);
    setIsSuccess(false);
  }, []);

  /**
   * Submit feedback with retry logic.
   */
  const submitWithRetry = useCallback(
    async <T>(
      submitFn: () => Promise<T>,
      retryCount = 0
    ): Promise<T | undefined> => {
      try {
        const result = await submitFn();
        return result;
      } catch (err: any) {
        // Don't retry on rate limit or validation errors
        if (
          err.response?.status === 429 ||
          err.response?.status === 400 ||
          err.response?.status === 422
        ) {
          throw err;
        }

        // Retry on network/server errors
        if (retryCount < maxRetries) {
          // Exponential backoff: 1s, 2s, 4s...
          const delay = Math.pow(2, retryCount) * 1000;
          await new Promise((resolve) => setTimeout(resolve, delay));
          return submitWithRetry(submitFn, retryCount + 1);
        }

        throw err;
      }
    },
    [maxRetries]
  );

  /**
   * Submit feedback on a specific plan.
   */
  const submitPlanFeedback = useCallback(
    async (data: PlanFeedbackData) => {
      setIsSubmitting(true);
      setError(null);
      setIsSuccess(false);

      try {
        const response = await submitWithRetry(async () => {
          const result = await apiClient.post<FeedbackSubmissionResponse>(
            '/feedback/plan',
            data
          );
          return result.data;
        });

        if (response) {
          setIsSuccess(true);
          onSuccess?.(response);
        }
      } catch (err: any) {
        const errorMessage = getErrorMessage(err);
        setError(errorMessage);
        onError?.(errorMessage);
      } finally {
        setIsSubmitting(false);
      }
    },
    [submitWithRetry, onSuccess, onError]
  );

  /**
   * Submit feedback on overall recommendation.
   */
  const submitRecommendationFeedback = useCallback(
    async (data: RecommendationFeedbackData) => {
      setIsSubmitting(true);
      setError(null);
      setIsSuccess(false);

      try {
        const response = await submitWithRetry(async () => {
          const result = await apiClient.post<FeedbackSubmissionResponse>(
            '/feedback/recommendation',
            data
          );
          return result.data;
        });

        if (response) {
          setIsSuccess(true);
          onSuccess?.(response);
        }
      } catch (err: any) {
        const errorMessage = getErrorMessage(err);
        setError(errorMessage);
        onError?.(errorMessage);
      } finally {
        setIsSubmitting(false);
      }
    },
    [submitWithRetry, onSuccess, onError]
  );

  return {
    submitPlanFeedback,
    submitRecommendationFeedback,
    isSubmitting,
    error,
    isSuccess,
    reset,
  };
}

/**
 * Extract user-friendly error message from error object.
 */
function getErrorMessage(error: any): string {
  if (error.response?.status === 429) {
    return 'You have exceeded the feedback submission limit. Please try again later.';
  }

  if (error.response?.status === 400 || error.response?.status === 422) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail[0].msg || 'Invalid feedback data.';
    }
    return 'Invalid feedback data. Please check your input.';
  }

  if (error.response?.status === 500) {
    return 'Server error. Please try again later.';
  }

  if (error.request && !error.response) {
    return 'Network error. Please check your connection and try again.';
  }

  return error.message || 'An unexpected error occurred. Please try again.';
}

/**
 * Helper hook for simple thumbs up/down feedback.
 *
 * @example
 * ```tsx
 * const { submitThumbsFeedback, isSubmitting } = useThumbsFeedback({
 *   planId: 'plan-123',
 *   recommendationId: 'rec-456',
 * });
 *
 * <button onClick={() => submitThumbsFeedback(true)}>👍</button>
 * <button onClick={() => submitThumbsFeedback(false)}>👎</button>
 * ```
 */
export function useThumbsFeedback(options: {
  planId?: string;
  recommendationId?: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}) {
  const { planId, recommendationId, onSuccess, onError } = options;

  const { submitPlanFeedback, submitRecommendationFeedback, isSubmitting, error } =
    useFeedback({
      onSuccess,
      onError,
    });

  const submitThumbsFeedback = useCallback(
    async (isPositive: boolean, feedbackText?: string) => {
      const rating: FeedbackRating = isPositive ? 5 : 1;
      const feedbackType: FeedbackType = isPositive ? 'helpful' : 'not_helpful';

      if (planId) {
        await submitPlanFeedback({
          plan_id: planId,
          recommendation_id: recommendationId,
          rating,
          feedback_text: feedbackText,
          feedback_type: feedbackType,
        });
      } else if (recommendationId) {
        await submitRecommendationFeedback({
          recommendation_id: recommendationId,
          rating,
          feedback_text: feedbackText,
          feedback_type: feedbackType,
        });
      }
    },
    [planId, recommendationId, submitPlanFeedback, submitRecommendationFeedback]
  );

  return {
    submitThumbsFeedback,
    isSubmitting,
    error,
  };
}
