/**
 * FeedbackDashboard Page
 *
 * Admin-only dashboard displaying comprehensive feedback analytics.
 *
 * Story 8.3: Feedback Analytics Dashboard
 */

import React, { useState, useEffect } from 'react';
import {
  Download,
  AlertCircle,
  Loader2,
  MessageSquare,
  Search,
  Filter,
} from 'lucide-react';
import { clsx } from 'clsx';
import { FeedbackStats, FeedbackChart, FeedbackTable } from '@/components/FeedbackAnalytics';
import { apiClient } from '@/api/client';
import type {
  FeedbackAnalyticsResponse,
  FeedbackRecord,
  SentimentType,
} from '@/types/feedback';

export const FeedbackDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<FeedbackAnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState<SentimentType | 'all'>('all');
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiClient.get<FeedbackAnalyticsResponse>(
        '/admin/feedback/analytics'
      );
      setAnalytics(response.data);
    } catch (err: any) {
      console.error('Failed to fetch analytics:', err);
      setError(
        err.response?.status === 403
          ? 'You do not have permission to view this dashboard.'
          : 'Failed to load feedback analytics. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      setIsExporting(true);
      const response = await apiClient.get('/admin/feedback/export', {
        responseType: 'blob',
      });

      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `feedback_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Failed to export CSV:', err);
      alert('Failed to export feedback data. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const filteredTextFeedback = analytics?.recent_text_feedback.filter((feedback) => {
    // Search filter
    const matchesSearch =
      !searchTerm ||
      feedback.feedback_text?.toLowerCase().includes(searchTerm.toLowerCase());

    // Sentiment filter
    const matchesSentiment =
      sentimentFilter === 'all' ||
      (sentimentFilter === 'positive' && (feedback.sentiment_score ?? 0) > 0.3) ||
      (sentimentFilter === 'neutral' &&
        (feedback.sentiment_score ?? 0) >= -0.3 &&
        (feedback.sentiment_score ?? 0) <= 0.3) ||
      (sentimentFilter === 'negative' && (feedback.sentiment_score ?? 0) < -0.3);

    return matchesSearch && matchesSentiment;
  });

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-primary-600 animate-spin" aria-hidden="true" />
            <span className="ml-3 text-lg text-gray-700">Loading analytics...</span>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <div
            className="bg-white rounded-lg shadow-sm border border-red-200 p-8 text-center"
            role="alert"
          >
            <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" aria-hidden="true" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Dashboard</h2>
            <p className="text-gray-700 mb-6">{error}</p>
            <button
              onClick={fetchAnalytics}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Feedback Analytics</h1>
              <p className="text-gray-600 mt-1">
                Monitor user feedback and satisfaction metrics
              </p>
            </div>
            <button
              onClick={handleExportCSV}
              disabled={isExporting}
              className={clsx(
                'inline-flex items-center gap-2 px-4 py-2 text-sm font-medium',
                'text-white bg-primary-600 hover:bg-primary-700 rounded-lg',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
              )}
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  <span>Exporting...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" aria-hidden="true" />
                  <span>Export CSV</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <FeedbackStats stats={analytics.stats} className="mb-8" />

        {/* Time Series Chart */}
        <FeedbackChart data={analytics.time_series} className="mb-8" />

        {/* Plan Feedback Table */}
        <FeedbackTable plans={analytics.top_plans} className="mb-8" />

        {/* Recent Text Feedback */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  Recent Text Feedback
                </h3>
                <p className="text-sm text-gray-600">Latest comments from users</p>
              </div>
              <div className="flex items-center gap-3">
                {/* Search Input */}
                <div className="relative">
                  <Search
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
                    aria-hidden="true"
                  />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search feedback..."
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Sentiment Filter */}
                <select
                  value={sentimentFilter}
                  onChange={(e) =>
                    setSentimentFilter(e.target.value as SentimentType | 'all')
                  }
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="all">All Sentiment</option>
                  <option value="positive">Positive</option>
                  <option value="neutral">Neutral</option>
                  <option value="negative">Negative</option>
                </select>
              </div>
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {filteredTextFeedback && filteredTextFeedback.length > 0 ? (
              filteredTextFeedback.map((feedback) => {
                const sentiment = feedback.sentiment_score
                  ? feedback.sentiment_score > 0.3
                    ? 'positive'
                    : feedback.sentiment_score < -0.3
                    ? 'negative'
                    : 'neutral'
                  : 'neutral';

                const sentimentStyles = {
                  positive: 'bg-green-50 text-green-700 border-green-200',
                  neutral: 'bg-gray-50 text-gray-700 border-gray-200',
                  negative: 'bg-red-50 text-red-700 border-red-200',
                };

                return (
                  <div key={feedback.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span
                          className={clsx(
                            'px-2 py-1 text-xs font-medium rounded border',
                            sentimentStyles[sentiment]
                          )}
                        >
                          {sentiment}
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          Rating: {feedback.rating}/5
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(feedback.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {feedback.feedback_text}
                    </p>
                  </div>
                );
              })
            ) : (
              <div className="p-12 text-center">
                <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-3" aria-hidden="true" />
                <p className="text-gray-500">No text feedback found.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

FeedbackDashboard.displayName = 'FeedbackDashboard';
