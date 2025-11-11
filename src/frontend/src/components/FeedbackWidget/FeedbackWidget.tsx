/**
 * FeedbackWidget Component
 *
 * Collects user feedback on plans and recommendations with thumbs up/down
 * and optional text feedback.
 *
 * Story 8.1: Feedback Collection UI
 */

import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import { useFeedback } from '@/hooks/useFeedback';
import type { FeedbackWidgetProps, FeedbackRating, FeedbackType } from '@/types/feedback';

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({
  planId,
  recommendationId,
  onSuccess,
  onError,
  compact = false,
  className,
}) => {
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  const { submitPlanFeedback, submitRecommendationFeedback, isSubmitting, error, isSuccess, reset } =
    useFeedback({
      onSuccess: (response) => {
        onSuccess?.();
        // Auto-hide success message after 3 seconds
        setTimeout(() => {
          reset();
          setRating(null);
          setFeedbackText('');
          setIsExpanded(false);
        }, 3000);
      },
      onError: (errorMsg) => {
        onError?.(errorMsg);
      },
    });

  const handleThumbsClick = (isPositive: boolean) => {
    const newRating: FeedbackRating = isPositive ? 5 : 1;
    setRating(newRating);
    setIsExpanded(true);
  };

  const handleSubmit = async () => {
    if (!rating) return;

    const feedbackType: FeedbackType = rating >= 4 ? 'helpful' : 'not_helpful';

    if (planId) {
      await submitPlanFeedback({
        plan_id: planId,
        recommendation_id: recommendationId,
        rating,
        feedback_text: feedbackText || undefined,
        feedback_type: feedbackType,
      });
    } else if (recommendationId) {
      await submitRecommendationFeedback({
        recommendation_id: recommendationId,
        rating,
        feedback_text: feedbackText || undefined,
        feedback_type: feedbackType,
      });
    }
  };

  const handleCancel = () => {
    setRating(null);
    setFeedbackText('');
    setIsExpanded(false);
    reset();
  };

  const characterCount = feedbackText.length;
  const maxCharacters = 500;
  const isOverLimit = characterCount > maxCharacters;

  // Success state
  if (isSuccess) {
    return (
      <div
        className={clsx(
          'flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-3',
          className
        )}
        role="alert"
        aria-live="polite"
      >
        <CheckCircle className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
        <span>Thank you for your feedback!</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        className={clsx(
          'flex flex-col gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3',
          className
        )}
        role="alert"
        aria-live="polite"
      >
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
          <span>{error}</span>
        </div>
        <button
          onClick={handleCancel}
          className="text-xs text-red-600 hover:text-red-800 underline self-start"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div
      className={clsx(
        'border-t border-gray-200 pt-3',
        compact && 'pt-2',
        className
      )}
      role="region"
      aria-label="Feedback form"
    >
      {/* Question and Thumbs Buttons */}
      <div className="flex items-center justify-between gap-3">
        <p className={clsx('text-sm font-medium text-gray-700', compact && 'text-xs')}>
          {planId ? 'Was this plan helpful?' : 'Was this recommendation helpful?'}
        </p>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleThumbsClick(true)}
            disabled={isSubmitting || rating !== null}
            className={clsx(
              'inline-flex items-center justify-center rounded-lg transition-all',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              compact ? 'w-8 h-8' : 'w-10 h-10',
              rating === 5
                ? 'bg-green-100 text-green-700 hover:bg-green-200'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-green-600',
              isSubmitting && 'opacity-50 cursor-not-allowed'
            )}
            aria-label="Thumbs up - helpful"
            aria-pressed={rating === 5}
          >
            <ThumbsUp className={clsx(compact ? 'w-4 h-4' : 'w-5 h-5')} aria-hidden="true" />
          </button>

          <button
            onClick={() => handleThumbsClick(false)}
            disabled={isSubmitting || rating !== null}
            className={clsx(
              'inline-flex items-center justify-center rounded-lg transition-all',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              compact ? 'w-8 h-8' : 'w-10 h-10',
              rating === 1
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-red-600',
              isSubmitting && 'opacity-50 cursor-not-allowed'
            )}
            aria-label="Thumbs down - not helpful"
            aria-pressed={rating === 1}
          >
            <ThumbsDown className={clsx(compact ? 'w-4 h-4' : 'w-5 h-5')} aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* Expanded Feedback Form */}
      {isExpanded && rating !== null && (
        <div className="mt-3 space-y-3 animate-fade-in">
          <div>
            <label
              htmlFor="feedback-text"
              className="block text-xs font-medium text-gray-700 mb-1"
            >
              Tell us more (optional)
            </label>
            <textarea
              id="feedback-text"
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              disabled={isSubmitting}
              maxLength={maxCharacters}
              rows={3}
              className={clsx(
                'w-full px-3 py-2 text-sm border rounded-lg',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'disabled:bg-gray-100 disabled:cursor-not-allowed',
                isOverLimit ? 'border-red-300' : 'border-gray-300'
              )}
              placeholder="What could we improve?"
              aria-describedby="char-count"
            />
            <p
              id="char-count"
              className={clsx(
                'mt-1 text-xs text-right',
                isOverLimit ? 'text-red-600' : 'text-gray-500'
              )}
            >
              {characterCount} / {maxCharacters}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || isOverLimit}
              className={clsx(
                'flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium',
                'text-white bg-primary-600 hover:bg-primary-700 rounded-lg',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed transition-colors',
                'min-h-[36px]'
              )}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  <span>Submitting...</span>
                </>
              ) : (
                <span>Submit Feedback</span>
              )}
            </button>

            <button
              onClick={handleCancel}
              disabled={isSubmitting}
              className={clsx(
                'px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300',
                'hover:bg-gray-50 rounded-lg transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'min-h-[36px]'
              )}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

FeedbackWidget.displayName = 'FeedbackWidget';
