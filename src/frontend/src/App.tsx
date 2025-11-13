import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
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

// Wrapper component to read navigation state and pass to ResultsPage
function ResultsPageWrapper() {
  const location = useLocation();
  const state = location.state as { recommendation?: any } | null;

  return <ResultsPage recommendation={state?.recommendation || null} />;
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/onboarding" replace />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/results" element={<ResultsPageWrapper />} />

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
