import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useParams } from 'react-router-dom';
import { OnboardingPage } from '@/pages/OnboardingPage';
import { ResultsPage } from '@/pages/ResultsPage';
import { ComparisonPage } from '@/pages/ComparisonPage';
import { ScenarioPage } from '@/pages/ScenarioPage';
import { recommendationsApi } from '@/api/recommendations';
import type { GenerateRecommendationResponse } from '@/types/recommendation';
// Admin routes disabled for demo — re-enable by uncommenting these imports + the /admin block below
// import { RequireAdmin } from '@/components/auth/RequireAdmin';
// import { AdminLayout } from '@/components/admin/AdminLayout';
// import { Dashboard } from '@/pages/admin/Dashboard';
// import { Users } from '@/pages/admin/Users';
// import { Recommendations } from '@/pages/admin/Recommendations';
// import { Plans } from '@/pages/admin/Plans';
// import { AuditLogs } from '@/pages/admin/AuditLogs';
// import { FeedbackDashboard } from '@/pages/FeedbackDashboard';
import '@/styles/index.css';

// Wrapper component to read navigation state and pass to ResultsPage
type ResultsLocationState = {
  recommendation?: GenerateRecommendationResponse;
  userEmail?: string;
};

function ResultsPageWrapper() {
  const location = useLocation();
  const { recommendationId } = useParams();
  const state = location.state as ResultsLocationState | null;
  const stateRecommendation =
    state?.recommendation && (!recommendationId || state.recommendation.recommendation_id === recommendationId)
      ? state.recommendation
      : null;
  const [recommendation, setRecommendation] = useState<GenerateRecommendationResponse | null>(
    stateRecommendation
  );
  const [isLoading, setIsLoading] = useState(Boolean(recommendationId && !stateRecommendation));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (stateRecommendation) {
      setRecommendation(stateRecommendation);
      setIsLoading(false);
      setError(null);
      return;
    }

    if (!recommendationId) {
      setRecommendation(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    recommendationsApi
      .getRecommendation(recommendationId)
      .then((data) => {
        if (isMounted) {
          setRecommendation(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setError('This recommendation could not be loaded. It may have expired or the link may be incorrect.');
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [recommendationId, stateRecommendation]);

  return <ResultsPage recommendation={recommendation} isLoading={isLoading} error={error} />;
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/onboarding" replace />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/results" element={<ResultsPageWrapper />} />
          <Route path="/results/:recommendationId" element={<ResultsPageWrapper />} />
          <Route path="/comparison" element={<ComparisonPage />} />
          <Route path="/scenarios" element={<ScenarioPage />} />

          {/* Admin Routes — disabled for demo. Re-enable by uncommenting the imports above
              and the block below.

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
            <Route path="feedback" element={<FeedbackDashboard />} />
          </Route>

          */}

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
