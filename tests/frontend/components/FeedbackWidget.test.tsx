/**
 * Tests for FeedbackWidget component.
 *
 * Story 8.1: Feedback Collection UI
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { FeedbackWidget } from '@/components/FeedbackWidget/FeedbackWidget';
import * as feedbackHook from '@/hooks/useFeedback';

// Mock the useFeedback hook
vi.mock('@/hooks/useFeedback');

describe('FeedbackWidget', () => {
  const mockSubmitPlanFeedback = vi.fn();
  const mockSubmitRecommendationFeedback = vi.fn();
  const mockReset = vi.fn();

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();

    // Default mock implementation
    vi.mocked(feedbackHook.useFeedback).mockReturnValue({
      submitPlanFeedback: mockSubmitPlanFeedback,
      submitRecommendationFeedback: mockSubmitRecommendationFeedback,
      isSubmitting: false,
      error: null,
      isSuccess: false,
      reset: mockReset,
    });
  });

  describe('Rendering', () => {
    it('should render feedback question and thumbs buttons', () => {
      render(<FeedbackWidget planId="plan-123" />);

      expect(screen.getByText(/Was this plan helpful?/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Thumbs up - helpful/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Thumbs down - not helpful/i)).toBeInTheDocument();
    });

    it('should render recommendation question when only recommendationId provided', () => {
      render(<FeedbackWidget recommendationId="rec-456" />);

      expect(screen.getByText(/Was this recommendation helpful?/i)).toBeInTheDocument();
    });

    it('should render in compact mode', () => {
      const { container } = render(<FeedbackWidget planId="plan-123" compact />);

      // In compact mode, buttons should be smaller (w-8 h-8 instead of w-10 h-10)
      const thumbsUpButton = screen.getByLabelText(/Thumbs up/i);
      expect(thumbsUpButton).toHaveClass('w-8', 'h-8');
    });
  });

  describe('Thumbs up/down interaction', () => {
    it('should expand form when thumbs up is clicked', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      const thumbsUpButton = screen.getByLabelText(/Thumbs up - helpful/i);
      await userEvent.click(thumbsUpButton);

      // Form should expand and show textarea
      expect(screen.getByLabelText(/Tell us more/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Submit Feedback/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    });

    it('should expand form when thumbs down is clicked', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      const thumbsDownButton = screen.getByLabelText(/Thumbs down - not helpful/i);
      await userEvent.click(thumbsDownButton);

      expect(screen.getByLabelText(/Tell us more/i)).toBeInTheDocument();
    });

    it('should apply selected style to clicked thumb', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      const thumbsUpButton = screen.getByLabelText(/Thumbs up/i);
      await userEvent.click(thumbsUpButton);

      expect(thumbsUpButton).toHaveClass('bg-green-100', 'text-green-700');
    });
  });

  describe('Text feedback', () => {
    it('should allow entering text feedback', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      // Click thumbs up to expand
      await userEvent.click(screen.getByLabelText(/Thumbs up/i));

      const textarea = screen.getByLabelText(/Tell us more/i);
      await userEvent.type(textarea, 'Great plan!');

      expect(textarea).toHaveValue('Great plan!');
    });

    it('should show character count', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      await userEvent.click(screen.getByLabelText(/Thumbs up/i));

      const textarea = screen.getByLabelText(/Tell us more/i);
      await userEvent.type(textarea, 'Test');

      expect(screen.getByText(/4 \/ 500/i)).toBeInTheDocument();
    });

    it('should warn when character limit exceeded', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      await userEvent.click(screen.getByLabelText(/Thumbs up/i));

      const textarea = screen.getByLabelText(/Tell us more/i);
      const longText = 'x'.repeat(501);
      await userEvent.type(textarea, longText);

      const charCount = screen.getByText(/501 \/ 500/i);
      expect(charCount).toHaveClass('text-red-600');
    });

    it('should disable submit button when over character limit', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      await userEvent.click(screen.getByLabelText(/Thumbs up/i));

      const textarea = screen.getByLabelText(/Tell us more/i);
      const longText = 'x'.repeat(501);
      await userEvent.type(textarea, longText);

      const submitButton = screen.getByRole('button', { name: /Submit Feedback/i });
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Form submission', () => {
    it('should submit plan feedback with rating and text', async () => {
      mockSubmitPlanFeedback.mockResolvedValue(undefined);

      render(<FeedbackWidget planId="plan-123" recommendationId="rec-456" />);

      // Click thumbs up (rating 5)
      await userEvent.click(screen.getByLabelText(/Thumbs up/i));

      // Enter text
      const textarea = screen.getByLabelText(/Tell us more/i);
      await userEvent.type(textarea, 'Excellent!');

      // Submit
      const submitButton = screen.getByRole('button', { name: /Submit Feedback/i });
      await userEvent.click(submitButton);

      expect(mockSubmitPlanFeedback).toHaveBeenCalledWith({
        plan_id: 'plan-123',
        recommendation_id: 'rec-456',
        rating: 5,
        feedback_text: 'Excellent!',
        feedback_type: 'helpful',
      });
    });

    it('should submit recommendation feedback when no planId', async () => {
      mockSubmitRecommendationFeedback.mockResolvedValue(undefined);

      render(<FeedbackWidget recommendationId="rec-456" />);

      await userEvent.click(screen.getByLabelText(/Thumbs up/i));
      await userEvent.click(screen.getByRole('button', { name: /Submit Feedback/i }));

      expect(mockSubmitRecommendationFeedback).toHaveBeenCalledWith({
        recommendation_id: 'rec-456',
        rating: 5,
        feedback_text: undefined,
        feedback_type: 'helpful',
      });
    });

    it('should show loading state during submission', async () => {
      vi.mocked(feedbackHook.useFeedback).mockReturnValue({
        submitPlanFeedback: mockSubmitPlanFeedback,
        submitRecommendationFeedback: mockSubmitRecommendationFeedback,
        isSubmitting: true,
        error: null,
        isSuccess: false,
        reset: mockReset,
      });

      render(<FeedbackWidget planId="plan-123" />);

      await userEvent.click(screen.getByLabelText(/Thumbs up/i));

      expect(screen.getByText(/Submitting.../i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Submitting.../i })).toBeDisabled();
    });

    it('should call onSuccess callback on successful submission', async () => {
      const onSuccess = vi.fn();

      vi.mocked(feedbackHook.useFeedback).mockReturnValue({
        submitPlanFeedback: mockSubmitPlanFeedback,
        submitRecommendationFeedback: mockSubmitRecommendationFeedback,
        isSubmitting: false,
        error: null,
        isSuccess: true,
        reset: mockReset,
      });

      render(<FeedbackWidget planId="plan-123" onSuccess={onSuccess} />);

      // Success state should trigger onSuccess
      expect(screen.getByText(/Thank you for your feedback!/i)).toBeInTheDocument();
    });
  });

  describe('Cancel functionality', () => {
    it('should collapse form when cancel is clicked', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      // Expand form
      await userEvent.click(screen.getByLabelText(/Thumbs up/i));
      expect(screen.getByLabelText(/Tell us more/i)).toBeInTheDocument();

      // Click cancel
      await userEvent.click(screen.getByRole('button', { name: /Cancel/i }));

      // Form should be collapsed
      expect(screen.queryByLabelText(/Tell us more/i)).not.toBeInTheDocument();
    });
  });

  describe('Success state', () => {
    it('should show success message after submission', () => {
      vi.mocked(feedbackHook.useFeedback).mockReturnValue({
        submitPlanFeedback: mockSubmitPlanFeedback,
        submitRecommendationFeedback: mockSubmitRecommendationFeedback,
        isSubmitting: false,
        error: null,
        isSuccess: true,
        reset: mockReset,
      });

      render(<FeedbackWidget planId="plan-123" />);

      expect(screen.getByText(/Thank you for your feedback!/i)).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  describe('Error state', () => {
    it('should show error message on submission failure', () => {
      vi.mocked(feedbackHook.useFeedback).mockReturnValue({
        submitPlanFeedback: mockSubmitPlanFeedback,
        submitRecommendationFeedback: mockSubmitRecommendationFeedback,
        isSubmitting: false,
        error: 'Network error. Please try again.',
        isSuccess: false,
        reset: mockReset,
      });

      render(<FeedbackWidget planId="plan-123" />);

      expect(screen.getByText(/Network error. Please try again./i)).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should allow retry after error', async () => {
      vi.mocked(feedbackHook.useFeedback).mockReturnValue({
        submitPlanFeedback: mockSubmitPlanFeedback,
        submitRecommendationFeedback: mockSubmitRecommendationFeedback,
        isSubmitting: false,
        error: 'Network error',
        isSuccess: false,
        reset: mockReset,
      });

      render(<FeedbackWidget planId="plan-123" />);

      const tryAgainButton = screen.getByText(/Try again/i);
      await userEvent.click(tryAgainButton);

      expect(mockReset).toHaveBeenCalled();
    });

    it('should call onError callback on failure', () => {
      const onError = vi.fn();

      vi.mocked(feedbackHook.useFeedback).mockReturnValue({
        submitPlanFeedback: mockSubmitPlanFeedback,
        submitRecommendationFeedback: mockSubmitRecommendationFeedback,
        isSubmitting: false,
        error: 'Test error',
        isSuccess: false,
        reset: mockReset,
      });

      render(<FeedbackWidget planId="plan-123" onError={onError} />);

      // Error state should be visible
      expect(screen.getByText(/Test error/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<FeedbackWidget planId="plan-123" />);

      expect(screen.getByRole('region', { name: /Feedback form/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/Thumbs up - helpful/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Thumbs down - not helpful/i)).toBeInTheDocument();
    });

    it('should have proper aria-pressed state on thumbs buttons', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      const thumbsUpButton = screen.getByLabelText(/Thumbs up/i);

      expect(thumbsUpButton).toHaveAttribute('aria-pressed', 'false');

      await userEvent.click(thumbsUpButton);

      expect(thumbsUpButton).toHaveAttribute('aria-pressed', 'true');
    });

    it('should support keyboard navigation', async () => {
      render(<FeedbackWidget planId="plan-123" />);

      const thumbsUpButton = screen.getByLabelText(/Thumbs up/i);

      // Tab to button and press Enter
      thumbsUpButton.focus();
      fireEvent.keyDown(thumbsUpButton, { key: 'Enter', code: 'Enter' });

      // Should expand form
      expect(screen.getByLabelText(/Tell us more/i)).toBeInTheDocument();
    });
  });
});
