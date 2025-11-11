import React, { useEffect } from 'react';
import { useAdminStats } from '@/hooks/useAdminStats';
import { StatCard } from '@/components/admin/StatCard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/design-system/Card';
import { Badge } from '@/components/design-system/Badge';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/**
 * Dashboard Page
 *
 * Admin dashboard overview with key metrics, charts, and recent activity.
 */

export const Dashboard: React.FC = () => {
  const { data, loading, fetchDashboardData } = useAdminStats();

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Format date for charts
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  // Format time for recent activity
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const COLORS = {
    positive: '#10b981',
    neutral: '#f59e0b',
    negative: '#ef4444',
  };

  const pieData = data
    ? [
        { name: 'Positive', value: data.charts.feedback_sentiment.positive },
        { name: 'Neutral', value: data.charts.feedback_sentiment.neutral },
        { name: 'Negative', value: data.charts.feedback_sentiment.negative },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of system metrics and activity</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          }
          label="Total Users"
          value={data?.stats.total_users || 0}
          subValue={`${data?.stats.active_users || 0} active, ${data?.stats.inactive_users || 0} inactive`}
          change={12.5}
          changeType="increase"
          loading={loading}
        />

        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          }
          label="Total Recommendations"
          value={data?.stats.total_recommendations || 0}
          change={8.3}
          changeType="increase"
          loading={loading}
        />

        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          }
          label="Total Feedback"
          value={data?.stats.total_feedback || 0}
          subValue={`${data ? ((data.stats.total_feedback / data.stats.total_recommendations) * 100).toFixed(1) : 0}% response rate`}
          loading={loading}
        />

        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
          label="Avg Recs per User"
          value={data?.stats.avg_recommendations_per_user.toFixed(2) || '0.00'}
          loading={loading}
        />
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          }
          label="Cache Hit Rate"
          value={`${data?.stats.cache_hit_rate.toFixed(1) || 0}%`}
          change={2.1}
          changeType="increase"
          loading={loading}
        />

        <StatCard
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          label="API P95 Latency"
          value={`${data?.stats.api_p95_latency_ms || 0}ms`}
          change={5.2}
          changeType="decrease"
          loading={loading}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommendations Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Recommendations Over Time</CardTitle>
            <p className="text-sm text-gray-600 mt-1">Last 30 days</p>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 bg-gray-200 rounded animate-pulse" />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={data?.charts.recommendations_over_time || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={formatDate} />
                  <YAxis />
                  <Tooltip labelFormatter={formatDate} />
                  <Legend />
                  <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} name="Recommendations" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* User Growth */}
        <Card>
          <CardHeader>
            <CardTitle>User Growth</CardTitle>
            <p className="text-sm text-gray-600 mt-1">Last 30 days</p>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 bg-gray-200 rounded animate-pulse" />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={data?.charts.user_growth || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={formatDate} />
                  <YAxis />
                  <Tooltip labelFormatter={formatDate} />
                  <Legend />
                  <Area type="monotone" dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.3} name="Users" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Feedback Sentiment & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Feedback Sentiment */}
        <Card>
          <CardHeader>
            <CardTitle>Feedback Sentiment</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 bg-gray-200 rounded animate-pulse" />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.name.toLowerCase() as keyof typeof COLORS]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <p className="text-sm text-gray-600 mt-1">Last 10 actions</p>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-12 bg-gray-200 rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {data?.recent_activity.map((activity) => (
                  <div key={activity.id} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">{activity.user_email}</span>
                        <Badge variant="neutral" size="sm">
                          {activity.action}
                        </Badge>
                      </div>
                      {activity.details && (
                        <p className="text-xs text-gray-600 mt-1">{activity.details}</p>
                      )}
                    </div>
                    <span className="text-xs text-gray-500 ml-4">{formatTime(activity.timestamp)}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
