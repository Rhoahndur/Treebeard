/**
 * Tests for Analytics Service
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import analytics, { AnalyticsService } from './analytics';

describe('AnalyticsService', () => {
  let analyticsService: AnalyticsService;

  beforeEach(() => {
    // Reset analytics instance
    analyticsService = new AnalyticsService();

    // Mock window objects
    (window as any).dataLayer = [];
    (window as any).gtag = vi.fn((...args: any[]) => {
      window.dataLayer.push(args);
    });
    (window as any).mixpanel = {
      init: vi.fn(),
      track: vi.fn(),
      identify: vi.fn(),
      people: {
        set: vi.fn(),
      },
    };

    // Mock localStorage
    Storage.prototype.getItem = vi.fn();
    Storage.prototype.setItem = vi.fn();
  });

  describe('initialization', () => {
    it('should initialize with default config', () => {
      expect(analyticsService).toBeDefined();
    });

    it('should initialize GA4 when configured', () => {
      analyticsService.initialize({
        enabled: true,
        platform: 'ga4',
        ga4MeasurementId: 'G-XXXXXXXXXX',
        cookieConsent: true,
      });

      expect((window as any).gtag).toBeDefined();
    });

    it('should not track events when disabled', () => {
      analyticsService.initialize({
        enabled: false,
      });

      analyticsService.trackEvent('test_event', { test: 'data' });
      expect((window as any).gtag).not.toHaveBeenCalledWith('event', 'test_event', expect.anything());
    });
  });

  describe('consent management', () => {
    it('should check for user consent', () => {
      (Storage.prototype.getItem as any).mockReturnValue('granted');

      analyticsService.initialize({
        enabled: true,
        platform: 'ga4',
        ga4MeasurementId: 'G-XXXXXXXXXX',
      });

      expect(Storage.prototype.getItem).toHaveBeenCalledWith('cookie_consent');
    });

    it('should grant consent', () => {
      analyticsService.grantConsent();
      expect(Storage.prototype.setItem).toHaveBeenCalledWith('cookie_consent', 'granted');
    });

    it('should revoke consent', () => {
      analyticsService.revokeConsent();
      expect(Storage.prototype.setItem).toHaveBeenCalledWith('cookie_consent', 'revoked');
    });
  });

  describe('event tracking', () => {
    beforeEach(() => {
      analyticsService.initialize({
        enabled: true,
        platform: 'ga4',
        ga4MeasurementId: 'G-XXXXXXXXXX',
        cookieConsent: true,
        debug: true,
      });
    });

    it('should track custom events', () => {
      analyticsService.trackEvent('test_event', { key: 'value' });

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'test_event',
        expect.objectContaining({
          key: 'value',
          session_id: expect.any(String),
          timestamp: expect.any(String),
        })
      );
    });

    it('should track page views', () => {
      analyticsService.trackPageView({
        page_path: '/onboarding',
        page_title: 'Onboarding',
      });

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'page_view',
        expect.objectContaining({
          page_path: '/onboarding',
          page_title: 'Onboarding',
        })
      );
    });

    it('should track onboarding started', () => {
      analyticsService.trackOnboardingStarted();

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'onboarding_started',
        expect.objectContaining({
          timestamp: expect.any(String),
        })
      );
    });

    it('should track onboarding step completed', () => {
      analyticsService.trackOnboardingStepCompleted(2, 'current_plan', 45);

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'onboarding_step_completed',
        expect.objectContaining({
          step: 2,
          step_name: 'current_plan',
          time_spent_seconds: 45,
          completion_percentage: 50,
        })
      );
    });

    it('should track onboarding abandoned', () => {
      analyticsService.trackOnboardingAbandoned(3, 'preferences', 'too_complex');

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'onboarding_abandoned',
        expect.objectContaining({
          step: 3,
          step_name: 'preferences',
          abandonment_reason: 'too_complex',
        })
      );
    });

    it('should track file upload attempted', () => {
      analyticsService.trackFileUploadAttempted('csv', 250, 'drag_drop');

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'file_upload_attempted',
        expect.objectContaining({
          file_type: 'csv',
          file_size_kb: 250,
          upload_method: 'drag_drop',
        })
      );
    });

    it('should track file upload succeeded', () => {
      analyticsService.trackFileUploadSucceeded('csv', 250);

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'file_upload_succeeded',
        expect.objectContaining({
          file_type: 'csv',
          file_size_kb: 250,
        })
      );
    });

    it('should track file upload failed', () => {
      analyticsService.trackFileUploadFailed('csv', 'Invalid format');

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'file_upload_failed',
        expect.objectContaining({
          file_type: 'csv',
          error_message: 'Invalid format',
        })
      );
    });

    it('should track preferences changed', () => {
      analyticsService.trackPreferencesChanged({
        cost_priority: 80,
        renewable_priority: 60,
      });

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'preferences_changed',
        expect.objectContaining({
          cost_priority: 80,
          renewable_priority: 60,
        })
      );
    });

    it('should track recommendation generated', () => {
      analyticsService.trackRecommendationGenerated(3, 'budget_conscious', 1250);

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'recommendation_generated',
        expect.objectContaining({
          num_plans: 3,
          user_profile_type: 'budget_conscious',
          generation_time_ms: 1250,
        })
      );
    });

    it('should track plan card expanded', () => {
      analyticsService.trackPlanCardExpanded('plan-123', 'Green Energy Plus', 1);

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'plan_card_expanded',
        expect.objectContaining({
          plan_id: 'plan-123',
          plan_name: 'Green Energy Plus',
          position: 1,
        })
      );
    });

    it('should track plan card clicked', () => {
      analyticsService.trackPlanCardClicked('plan-456', 'Budget Saver', 2);

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'plan_card_clicked',
        expect.objectContaining({
          plan_id: 'plan-456',
          plan_name: 'Budget Saver',
          position: 2,
        })
      );
    });

    it('should track cost breakdown viewed', () => {
      analyticsService.trackCostBreakdownViewed('plan-789');

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'cost_breakdown_viewed',
        expect.objectContaining({
          plan_id: 'plan-789',
        })
      );
    });

    it('should track comparison viewed', () => {
      analyticsService.trackComparisonViewed(['plan-123', 'plan-456', 'plan-789']);

      expect((window as any).gtag).toHaveBeenCalledWith(
        'event',
        'comparison_viewed',
        expect.objectContaining({
          plan_count: 3,
          plan_ids: 'plan-123,plan-456,plan-789',
        })
      );
    });
  });

  describe('user properties', () => {
    beforeEach(() => {
      analyticsService.initialize({
        enabled: true,
        platform: 'ga4',
        ga4MeasurementId: 'G-XXXXXXXXXX',
        cookieConsent: true,
      });
    });

    it('should set user properties', () => {
      analyticsService.setUserProperties({
        property_type: 'residential',
        zip_code: '77002',
        user_segment: 'budget_conscious',
      });

      expect((window as any).gtag).toHaveBeenCalledWith(
        'set',
        'user_properties',
        expect.objectContaining({
          property_type: 'residential',
          zip_code: '77002',
          user_segment: 'budget_conscious',
        })
      );
    });

    it('should identify user with anonymous ID', () => {
      analyticsService.identifyUser('anon-user-12345');

      expect((window as any).gtag).toHaveBeenCalledWith(
        'config',
        'G-XXXXXXXXXX',
        expect.objectContaining({
          user_id: 'anon-user-12345',
        })
      );
    });
  });

  describe('Mixpanel integration', () => {
    beforeEach(() => {
      analyticsService.initialize({
        enabled: true,
        platform: 'mixpanel',
        mixpanelToken: 'YOUR_MIXPANEL_TOKEN',
        cookieConsent: true,
      });
    });

    it('should track events to Mixpanel', () => {
      analyticsService.trackEvent('test_event', { key: 'value' });

      expect((window as any).mixpanel.track).toHaveBeenCalledWith(
        'test_event',
        expect.objectContaining({
          key: 'value',
          session_id: expect.any(String),
        })
      );
    });

    it('should set user properties in Mixpanel', () => {
      analyticsService.setUserProperties({
        property_type: 'commercial',
        zip_code: '90210',
      });

      expect((window as any).mixpanel.people.set).toHaveBeenCalledWith(
        expect.objectContaining({
          property_type: 'commercial',
          zip_code: '90210',
        })
      );
    });

    it('should identify user in Mixpanel', () => {
      analyticsService.identifyUser('anon-user-67890');

      expect((window as any).mixpanel.identify).toHaveBeenCalledWith('anon-user-67890');
    });
  });
});
