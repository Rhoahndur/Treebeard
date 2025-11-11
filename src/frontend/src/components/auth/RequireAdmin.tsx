import React from 'react';
import { Navigate } from 'react-router-dom';
import { Button } from '@/components/design-system/Button';

/**
 * RequireAdmin Component
 *
 * Protects admin routes by verifying user authentication and admin role.
 * Shows an "Access Denied" page for non-admin users.
 *
 * NOTE: In a production environment, this would integrate with an AuthContext
 * that manages authentication state. For now, we'll use a mock implementation
 * that checks localStorage for demo purposes.
 *
 * @example
 * <RequireAdmin>
 *   <AdminLayout />
 * </RequireAdmin>
 */

interface RequireAdminProps {
  children: React.ReactNode;
}

/**
 * Mock function to check if user is authenticated
 * In production, this would come from AuthContext
 */
const useAuth = () => {
  // Check localStorage for mock auth data
  const authData = localStorage.getItem('treebeard_auth');

  if (!authData) {
    return { isAuthenticated: false, user: null };
  }

  try {
    const parsed = JSON.parse(authData);
    return {
      isAuthenticated: true,
      user: parsed,
    };
  } catch {
    return { isAuthenticated: false, user: null };
  }
};

/**
 * Access Denied Page Component
 */
const AccessDeniedPage: React.FC = () => {
  const handleGoHome = () => {
    window.location.href = '/onboarding';
  };

  const handleLogout = () => {
    localStorage.removeItem('treebeard_auth');
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white rounded-lg shadow-card p-8">
          {/* Lock Icon */}
          <div className="mx-auto w-16 h-16 bg-danger-light rounded-full flex items-center justify-center mb-4">
            <svg
              className="w-8 h-8 text-danger"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Access Denied
          </h1>

          {/* Message */}
          <p className="text-gray-600 mb-6">
            You do not have permission to access the admin dashboard.
            This area is restricted to administrators only.
          </p>

          {/* Actions */}
          <div className="space-y-3">
            <Button
              variant="primary"
              fullWidth
              onClick={handleGoHome}
            >
              Go to Home
            </Button>
            <Button
              variant="outline"
              fullWidth
              onClick={handleLogout}
            >
              Logout
            </Button>
          </div>

          {/* Help Text */}
          <p className="text-sm text-gray-500 mt-6">
            If you believe you should have access, please contact your system administrator.
          </p>
        </div>
      </div>
    </div>
  );
};

/**
 * RequireAdmin Component
 *
 * Wraps protected admin routes and handles authentication/authorization
 */
export const RequireAdmin: React.FC<RequireAdminProps> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Authenticated but not admin - show access denied
  if (user?.role !== 'admin') {
    return <AccessDeniedPage />;
  }

  // Authenticated and admin - render children
  return <>{children}</>;
};

/**
 * Mock login function for development/testing
 * This sets mock auth data in localStorage
 *
 * @example
 * // Login as admin
 * mockLogin('admin@treebeard.com', 'admin');
 *
 * // Login as regular user
 * mockLogin('user@treebeard.com', 'user');
 */
export const mockLogin = (email: string, role: 'admin' | 'user') => {
  const authData = {
    id: Math.random().toString(36).substr(2, 9),
    email,
    role,
    full_name: role === 'admin' ? 'Admin User' : 'Regular User',
  };

  localStorage.setItem('treebeard_auth', JSON.stringify(authData));
};

/**
 * Mock logout function for development/testing
 */
export const mockLogout = () => {
  localStorage.removeItem('treebeard_auth');
};
