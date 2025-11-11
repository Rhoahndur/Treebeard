import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Home, LogOut, Zap } from 'lucide-react';
import { clsx } from 'clsx';

export interface HeaderProps {
  title?: string;
  showBack?: boolean;
  showHome?: boolean;
  showLogout?: boolean;
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  showBack = true,
  showHome = true,
  showLogout = false,
  className,
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleBack = () => {
    navigate(-1);
  };

  const handleHome = () => {
    navigate('/onboarding');
  };

  const handleLogout = () => {
    // Clear auth token
    localStorage.removeItem('token');
    navigate('/login');
  };

  // Don't show back button on login or first page
  const canGoBack = showBack && location.pathname !== '/login' && location.pathname !== '/onboarding';

  return (
    <header
      className={clsx(
        'bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left section - Back button or logo */}
          <div className="flex items-center gap-4">
            {canGoBack && (
              <button
                onClick={handleBack}
                className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors p-2 -ml-2 rounded-lg hover:bg-gray-100 min-h-[44px]"
                aria-label="Go back"
              >
                <ArrowLeft className="w-5 h-5" aria-hidden="true" />
                <span className="hidden sm:inline font-medium">Back</span>
              </button>
            )}

            {/* Logo/Brand */}
            <div className="flex items-center gap-2">
              <Zap className="w-6 h-6 text-primary-600" aria-hidden="true" />
              <h1 className="text-xl font-bold text-gray-900">
                TreeBeard
              </h1>
            </div>
          </div>

          {/* Center - Page title (optional) */}
          {title && (
            <div className="hidden md:block">
              <h2 className="text-lg font-semibold text-gray-700">{title}</h2>
            </div>
          )}

          {/* Right section - Navigation buttons */}
          <div className="flex items-center gap-2">
            {showHome && location.pathname !== '/onboarding' && (
              <button
                onClick={handleHome}
                className="inline-flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors min-h-[44px]"
                aria-label="Go to home"
              >
                <Home className="w-5 h-5" aria-hidden="true" />
                <span className="hidden sm:inline font-medium">Home</span>
              </button>
            )}

            {showLogout && (
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-danger hover:bg-danger-light rounded-lg transition-colors min-h-[44px]"
                aria-label="Logout"
              >
                <LogOut className="w-5 h-5" aria-hidden="true" />
                <span className="hidden sm:inline font-medium">Logout</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

Header.displayName = 'Header';
