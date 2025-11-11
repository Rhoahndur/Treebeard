import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { OnboardingPage } from '@/pages/OnboardingPage';
import { ResultsPage } from '@/pages/ResultsPage';
import { RequireAdmin } from '@/components/auth/RequireAdmin';
import { AdminLayout } from '@/components/admin/AdminLayout';
import { Dashboard } from '@/pages/admin/Dashboard';
import { Users } from '@/pages/admin/Users';
import { Recommendations } from '@/pages/admin/Recommendations';
import { Plans } from '@/pages/admin/Plans';
import { AuditLogs } from '@/pages/admin/AuditLogs';
import '@/styles/index.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/onboarding" replace />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/results" element={<ResultsPage recommendation={null} />} />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <AdminLayout />
              </RequireAdmin>
            }
          >
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="users" element={<Users />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="plans" element={<Plans />} />
            <Route path="audit-logs" element={<AuditLogs />} />
          </Route>

          {/* Login Page (Mock) */}
          <Route
            path="/login"
            element={
              <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="text-center bg-white p-8 rounded-lg shadow-card max-w-md w-full">
                  <h1 className="text-2xl font-bold text-gray-900 mb-4">Login</h1>
                  <p className="text-gray-600 mb-6">
                    For demo purposes, use the browser console to login:
                  </p>
                  <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-xs text-left mb-4">
                    <div>// Login as admin:</div>
                    <div>{"mockLogin('admin@treebeard.com', 'admin')"}</div>
                    <div className="mt-2">// Login as user:</div>
                    <div>{"mockLogin('user@treebeard.com', 'user')"}</div>
                  </div>
                  <a
                    href="/onboarding"
                    className="text-primary-600 hover:text-primary-700 underline"
                  >
                    Go to Onboarding
                  </a>
                </div>
              </div>
            }
          />

          {/* 404 Page */}
          <Route
            path="*"
            element={
              <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="text-center">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">404 - Page Not Found</h1>
                  <a
                    href="/onboarding"
                    className="text-primary-600 hover:text-primary-700 underline"
                  >
                    Go to Onboarding
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
