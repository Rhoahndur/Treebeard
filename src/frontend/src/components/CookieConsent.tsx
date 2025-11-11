/**
 * Cookie Consent Component
 *
 * GDPR and CCPA compliant cookie consent banner
 * Manages user consent for analytics cookies
 */

import React, { useState, useEffect } from 'react';
import analytics from '../utils/analytics';

export interface CookieConsentProps {
  /** Custom text for the consent message */
  message?: string;
  /** Custom text for accept button */
  acceptText?: string;
  /** Custom text for decline button */
  declineText?: string;
  /** Show settings button */
  showSettings?: boolean;
  /** Callback when consent is granted */
  onAccept?: () => void;
  /** Callback when consent is declined */
  onDecline?: () => void;
  /** Custom styling */
  className?: string;
}

const CookieConsent: React.FC<CookieConsentProps> = ({
  message = 'We use cookies to analyze site usage and improve your experience. Your data is anonymized and no personal information is collected.',
  acceptText = 'Accept',
  declineText = 'Decline',
  showSettings = false,
  onAccept,
  onDecline,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Check if user has already made a choice
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie_consent', 'granted');
    analytics.grantConsent();
    setIsVisible(false);
    onAccept?.();
  };

  const handleDecline = () => {
    localStorage.setItem('cookie_consent', 'revoked');
    analytics.revokeConsent();
    setIsVisible(false);
    onDecline?.();
  };

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg ${className}`}
      role="dialog"
      aria-label="Cookie consent"
      aria-describedby="cookie-consent-description"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          {/* Message */}
          <div className="flex-1">
            <p id="cookie-consent-description" className="text-sm text-gray-700">
              {message}
            </p>

            {showDetails && (
              <div className="mt-3 text-xs text-gray-600 space-y-2">
                <div>
                  <strong>What we collect:</strong>
                  <ul className="list-disc list-inside ml-2 mt-1">
                    <li>Page views and navigation patterns</li>
                    <li>Anonymized user interactions</li>
                    <li>Feature usage statistics</li>
                    <li>Error and performance data</li>
                  </ul>
                </div>
                <div>
                  <strong>What we DO NOT collect:</strong>
                  <ul className="list-disc list-inside ml-2 mt-1">
                    <li>Personal identifying information (PII)</li>
                    <li>Email addresses or names</li>
                    <li>Financial information</li>
                    <li>Precise location data</li>
                  </ul>
                </div>
                <div>
                  <strong>Data retention:</strong> Analytics data is retained for 90 days and then automatically deleted.
                </div>
                <div>
                  <strong>Your rights:</strong> You can revoke consent at any time in your browser settings.
                </div>
              </div>
            )}

            {showSettings && (
              <button
                onClick={toggleDetails}
                className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
              >
                {showDetails ? 'Hide details' : 'Learn more'}
              </button>
            )}
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
            <button
              onClick={handleDecline}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              aria-label="Decline cookies"
            >
              {declineText}
            </button>
            <button
              onClick={handleAccept}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              aria-label="Accept cookies"
            >
              {acceptText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;

/**
 * Cookie Settings Component
 *
 * Allows users to view and change their cookie preferences
 */
export const CookieSettings: React.FC = () => {
  const [consent, setConsent] = useState<string | null>(null);

  useEffect(() => {
    const currentConsent = localStorage.getItem('cookie_consent');
    setConsent(currentConsent);
  }, []);

  const handleGrantConsent = () => {
    localStorage.setItem('cookie_consent', 'granted');
    analytics.grantConsent();
    setConsent('granted');
  };

  const handleRevokeConsent = () => {
    localStorage.setItem('cookie_consent', 'revoked');
    analytics.revokeConsent();
    setConsent('revoked');
  };

  const handleClearConsent = () => {
    localStorage.removeItem('cookie_consent');
    setConsent(null);
    window.location.reload();
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Cookie Preferences</h2>

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Current Status</h3>
          <p className="text-sm text-gray-600">
            Analytics cookies:{' '}
            <span
              className={`font-semibold ${
                consent === 'granted'
                  ? 'text-green-600'
                  : consent === 'revoked'
                  ? 'text-red-600'
                  : 'text-gray-500'
              }`}
            >
              {consent === 'granted' ? 'Enabled' : consent === 'revoked' ? 'Disabled' : 'Not set'}
            </span>
          </p>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">About Analytics Cookies</h3>
          <p className="text-sm text-gray-600 mb-3">
            We use analytics cookies to understand how visitors interact with our website. This helps us
            improve your experience and our services.
          </p>
          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
            <li>Anonymized usage data only</li>
            <li>No personal information collected</li>
            <li>90-day data retention</li>
            <li>GDPR and CCPA compliant</li>
          </ul>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Manage Preferences</h3>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleGrantConsent}
              disabled={consent === 'granted'}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Enable Analytics
            </button>
            <button
              onClick={handleRevokeConsent}
              disabled={consent === 'revoked'}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Disable Analytics
            </button>
            <button
              onClick={handleClearConsent}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Reset & Show Banner
            </button>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Data Protection</h3>
          <p className="text-sm text-gray-600">
            Your privacy is important to us. All analytics data is:
          </p>
          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 mt-2">
            <li>Anonymized (IP addresses are masked)</li>
            <li>Encrypted in transit and at rest</li>
            <li>Never sold to third parties</li>
            <li>Automatically deleted after 90 days</li>
            <li>Subject to our Privacy Policy</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
