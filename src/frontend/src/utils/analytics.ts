/**
 * Analytics Utility for TreeBeard Energy Plan Recommendation Agent
 *
 * Supports Google Analytics 4 (GA4) and Mixpanel
 * GDPR Compliant - No PII, IP anonymization, cookie consent required
 */

// Analytics Configuration
export interface AnalyticsConfig {
  enabled: boolean;
  platform: 'ga4' | 'mixpanel' | 'both';
  ga4MeasurementId?: string;
  mixpanelToken?: string;
  debug?: boolean;
  anonymizeIp?: boolean;
  cookieConsent?: boolean;
}

// Event Properties Interface
export interface EventProperties {
  [key: string]: string | number | boolean | undefined;
}

// User Properties Interface
export interface UserProperties {
  property_type?: string;
  zip_code?: string;
  user_segment?: string;
  session_id?: string;
}

// Page View Properties
export interface PageViewProperties {
  page_path: string;
  page_title: string;
  page_location?: string;
}

// Onboarding Event Properties
export interface OnboardingEventProperties {
  step?: number;
  step_name?: string;
  time_spent_seconds?: number;
  completion_percentage?: number;
  abandonment_reason?: string;
}

// File Upload Event Properties
export interface FileUploadEventProperties {
  file_type?: string;
  file_size_kb?: number;
  upload_method?: 'drag_drop' | 'file_picker';
  error_message?: string;
}

// Recommendation Event Properties
export interface RecommendationEventProperties {
  num_plans?: number;
  user_profile_type?: string;
  generation_time_ms?: number;
  total_savings?: number;
}

// Plan Interaction Event Properties
export interface PlanInteractionEventProperties {
  plan_id?: string;
  plan_name?: string;
  plan_type?: string;
  position?: number; // 1, 2, or 3
  action?: 'expand' | 'click' | 'compare';
}

class AnalyticsService {
  private config: AnalyticsConfig;
  private sessionId: string;
  private userProperties: UserProperties;
  private isInitialized: boolean = false;

  constructor() {
    // Default configuration
    this.config = {
      enabled: false,
      platform: 'ga4',
      debug: false,
      anonymizeIp: true,
      cookieConsent: false,
    };

    this.sessionId = this.generateSessionId();
    this.userProperties = {};
  }

  /**
   * Initialize analytics with configuration
   */
  initialize(config: Partial<AnalyticsConfig>): void {
    this.config = { ...this.config, ...config };

    // Check for cookie consent
    if (this.config.cookieConsent === false && !this.hasUserConsent()) {
      console.log('[Analytics] Cookie consent not granted, analytics disabled');
      this.config.enabled = false;
      return;
    }

    // Initialize GA4
    if ((this.config.platform === 'ga4' || this.config.platform === 'both') && this.config.ga4MeasurementId) {
      this.initializeGA4();
    }

    // Initialize Mixpanel
    if ((this.config.platform === 'mixpanel' || this.config.platform === 'both') && this.config.mixpanelToken) {
      this.initializeMixpanel();
    }

    this.isInitialized = true;
    this.log('Analytics initialized', this.config);
  }

  /**
   * Initialize Google Analytics 4
   */
  private initializeGA4(): void {
    if (!this.config.ga4MeasurementId) return;

    // Load gtag.js script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${this.config.ga4MeasurementId}`;
    document.head.appendChild(script);

    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(...args: any[]) {
      window.dataLayer.push(args);
    }
    (window as any).gtag = gtag;

    gtag('js', new Date());
    gtag('config', this.config.ga4MeasurementId, {
      anonymize_ip: this.config.anonymizeIp,
      cookie_flags: 'SameSite=None;Secure',
      cookie_expires: 7776000, // 90 days
    });

    this.log('GA4 initialized');
  }

  /**
   * Initialize Mixpanel
   */
  private initializeMixpanel(): void {
    if (!this.config.mixpanelToken) return;

    // Load Mixpanel library
    (function(e: any, a: any) {
      if (!a.__SV) {
        const b = window;
        try {
          let c, l, i;
          const f = 'load';
          const p = b.location;
          const n = b.document;
          const s = n.getElementsByTagName('script')[0];
          const h = n.createElement('script');
          h.type = 'text/javascript';
          h.async = true;
          h.defer = true;
          h.src = 'https://cdn.mxpnl.com/libs/mixpanel-2-latest.min.js';
          s.parentNode?.insertBefore(h, s);
          h.addEventListener(f, function() {
            a.init(e);
          });
        } catch (g) {}
      }
    })(this.config.mixpanelToken, (window as any).mixpanel);

    this.log('Mixpanel initialized');
  }

  /**
   * Track a custom event
   */
  trackEvent(eventName: string, properties?: EventProperties): void {
    if (!this.config.enabled || !this.isInitialized) {
      this.log('Event not tracked (analytics disabled):', eventName, properties);
      return;
    }

    // Add session ID to all events
    const enrichedProperties = {
      ...properties,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
    };

    // Track in GA4
    if (this.config.platform === 'ga4' || this.config.platform === 'both') {
      this.trackGA4Event(eventName, enrichedProperties);
    }

    // Track in Mixpanel
    if (this.config.platform === 'mixpanel' || this.config.platform === 'both') {
      this.trackMixpanelEvent(eventName, enrichedProperties);
    }

    this.log('Event tracked:', eventName, enrichedProperties);
  }

  /**
   * Track page view
   */
  trackPageView(properties: PageViewProperties): void {
    if (!this.config.enabled) return;

    const eventProperties: EventProperties = {
      page_path: properties.page_path,
      page_title: properties.page_title,
      page_location: properties.page_location || window.location.href,
    };

    this.trackEvent('page_view', eventProperties);
  }

  /**
   * Track onboarding events
   */
  trackOnboardingStarted(): void {
    this.trackEvent('onboarding_started', {
      timestamp: new Date().toISOString(),
    });
  }

  trackOnboardingStepCompleted(stepNumber: number, stepName: string, timeSpentSeconds: number): void {
    this.trackEvent('onboarding_step_completed', {
      step: stepNumber,
      step_name: stepName,
      time_spent_seconds: timeSpentSeconds,
      completion_percentage: (stepNumber / 4) * 100,
    });
  }

  trackOnboardingAbandoned(stepNumber: number, stepName: string, reason?: string): void {
    this.trackEvent('onboarding_abandoned', {
      step: stepNumber,
      step_name: stepName,
      abandonment_reason: reason || 'unknown',
    });
  }

  trackOnboardingCompleted(totalTimeSeconds: number): void {
    this.trackEvent('onboarding_completed', {
      total_time_seconds: totalTimeSeconds,
      completion_percentage: 100,
    });
  }

  /**
   * Track file upload events
   */
  trackFileUploadAttempted(fileType: string, fileSizeKb: number, method: 'drag_drop' | 'file_picker'): void {
    this.trackEvent('file_upload_attempted', {
      file_type: fileType,
      file_size_kb: fileSizeKb,
      upload_method: method,
    });
  }

  trackFileUploadSucceeded(fileType: string, fileSizeKb: number): void {
    this.trackEvent('file_upload_succeeded', {
      file_type: fileType,
      file_size_kb: fileSizeKb,
    });
  }

  trackFileUploadFailed(fileType: string, errorMessage: string): void {
    this.trackEvent('file_upload_failed', {
      file_type: fileType,
      error_message: errorMessage,
    });
  }

  /**
   * Track preference changes
   */
  trackPreferencesChanged(preferences: Record<string, any>): void {
    this.trackEvent('preferences_changed', {
      ...preferences,
    });
  }

  /**
   * Track recommendation events
   */
  trackRecommendationGenerated(numPlans: number, profileType: string, generationTimeMs: number): void {
    this.trackEvent('recommendation_generated', {
      num_plans: numPlans,
      user_profile_type: profileType,
      generation_time_ms: generationTimeMs,
    });
  }

  trackPlanCardExpanded(planId: string, planName: string, position: number): void {
    this.trackEvent('plan_card_expanded', {
      plan_id: planId,
      plan_name: planName,
      position,
    });
  }

  trackPlanCardClicked(planId: string, planName: string, position: number): void {
    this.trackEvent('plan_card_clicked', {
      plan_id: planId,
      plan_name: planName,
      position,
    });
  }

  trackCostBreakdownViewed(planId: string): void {
    this.trackEvent('cost_breakdown_viewed', {
      plan_id: planId,
    });
  }

  trackComparisonViewed(planIds: string[]): void {
    this.trackEvent('comparison_viewed', {
      plan_count: planIds.length,
      plan_ids: planIds.join(','),
    });
  }

  /**
   * Set user properties
   */
  setUserProperties(properties: UserProperties): void {
    this.userProperties = { ...this.userProperties, ...properties };

    if (this.config.platform === 'ga4' || this.config.platform === 'both') {
      if ((window as any).gtag) {
        (window as any).gtag('set', 'user_properties', {
          property_type: properties.property_type,
          zip_code: properties.zip_code,
          user_segment: properties.user_segment,
        });
      }
    }

    if (this.config.platform === 'mixpanel' || this.config.platform === 'both') {
      if ((window as any).mixpanel) {
        (window as any).mixpanel.people.set(properties);
      }
    }

    this.log('User properties set:', properties);
  }

  /**
   * Identify user (use anonymous ID, not PII)
   */
  identifyUser(anonymousUserId: string): void {
    if (this.config.platform === 'mixpanel' || this.config.platform === 'both') {
      if ((window as any).mixpanel) {
        (window as any).mixpanel.identify(anonymousUserId);
      }
    }

    if (this.config.platform === 'ga4' || this.config.platform === 'both') {
      if ((window as any).gtag) {
        (window as any).gtag('config', this.config.ga4MeasurementId, {
          user_id: anonymousUserId,
        });
      }
    }

    this.log('User identified:', anonymousUserId);
  }

  /**
   * Track GA4 event
   */
  private trackGA4Event(eventName: string, properties: EventProperties): void {
    if ((window as any).gtag) {
      (window as any).gtag('event', eventName, properties);
    }
  }

  /**
   * Track Mixpanel event
   */
  private trackMixpanelEvent(eventName: string, properties: EventProperties): void {
    if ((window as any).mixpanel) {
      (window as any).mixpanel.track(eventName, properties);
    }
  }

  /**
   * Check if user has granted cookie consent
   */
  private hasUserConsent(): boolean {
    // Check localStorage for consent
    const consent = localStorage.getItem('cookie_consent');
    return consent === 'granted';
  }

  /**
   * Grant cookie consent
   */
  grantConsent(): void {
    localStorage.setItem('cookie_consent', 'granted');
    this.config.cookieConsent = true;
    this.config.enabled = true;

    // Re-initialize if needed
    if (!this.isInitialized) {
      this.initialize(this.config);
    }
  }

  /**
   * Revoke cookie consent
   */
  revokeConsent(): void {
    localStorage.setItem('cookie_consent', 'revoked');
    this.config.cookieConsent = false;
    this.config.enabled = false;

    // Clear cookies
    this.clearAnalyticsCookies();
  }

  /**
   * Clear analytics cookies
   */
  private clearAnalyticsCookies(): void {
    // Clear GA4 cookies
    document.cookie.split(';').forEach(cookie => {
      const name = cookie.split('=')[0].trim();
      if (name.startsWith('_ga') || name.startsWith('_gid')) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
      }
    });
  }

  /**
   * Generate session ID
   */
  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Debug logging
   */
  private log(message: string, ...args: any[]): void {
    if (this.config.debug) {
      console.log(`[Analytics] ${message}`, ...args);
    }
  }
}

// Create singleton instance
const analytics = new AnalyticsService();

// Export singleton and types
export default analytics;
export { AnalyticsService };

// Extend window interface for gtag
declare global {
  interface Window {
    dataLayer: any[];
    gtag: (...args: any[]) => void;
    mixpanel: any;
  }
}
