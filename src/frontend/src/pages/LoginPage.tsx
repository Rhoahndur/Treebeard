import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { authApi } from '@/api/auth';

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await authApi.login(email, password);
      // Redirect to onboarding after successful login
      navigate('/onboarding');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(
        err.response?.data?.detail ||
        'Login failed. Please check your credentials and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header showBack={false} showHome={false} showLogout={false} />
      <div className="flex items-center justify-center py-8 px-4">
      <div className="bg-white p-8 rounded-lg shadow-card max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">TreeBeard Energy</h1>
          <p className="text-gray-600">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="you@example.com"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-3">Demo accounts:</p>
          <div className="space-y-2 text-xs">
            <div className="p-3 bg-gray-50 rounded">
              <div className="font-semibold text-gray-900">Admin Account</div>
              <div className="text-gray-600">admin@treebeard.com / admin123</div>
            </div>
            <div className="p-3 bg-gray-50 rounded">
              <div className="font-semibold text-gray-900">Demo Account</div>
              <div className="text-gray-600">demo@treebeard.com / demo123</div>
            </div>
            <div className="p-3 bg-gray-50 rounded">
              <div className="font-semibold text-gray-900">User Account</div>
              <div className="text-gray-600">user@treebeard.com / user123</div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
