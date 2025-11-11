import React, { useState } from 'react';
import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import { mockLogout } from '@/components/auth/RequireAdmin';

/**
 * AdminLayout Component
 *
 * Main layout for the admin dashboard with sidebar navigation,
 * header with user profile, and breadcrumbs.
 */

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

/**
 * Navigation items for sidebar
 */
const navItems: NavItem[] = [
  {
    name: 'Dashboard',
    path: '/admin/dashboard',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
  },
  {
    name: 'Users',
    path: '/admin/users',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
  },
  {
    name: 'Recommendations',
    path: '/admin/recommendations',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
  },
  {
    name: 'Plans',
    path: '/admin/plans',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
  {
    name: 'Audit Logs',
    path: '/admin/audit-logs',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
];

/**
 * Generate breadcrumbs from current path
 */
const getBreadcrumbs = (pathname: string): { name: string; path: string }[] => {
  const parts = pathname.split('/').filter(Boolean);

  if (parts.length === 1) {
    return [{ name: 'Admin', path: '/admin' }];
  }

  const breadcrumbs: { name: string; path: string }[] = [
    { name: 'Admin', path: '/admin' },
  ];

  let currentPath = '';
  for (let i = 1; i < parts.length; i++) {
    currentPath += '/' + parts[i];
    const name = parts[i].charAt(0).toUpperCase() + parts[i].slice(1).replace(/-/g, ' ');
    breadcrumbs.push({ name, path: '/admin' + currentPath });
  }

  return breadcrumbs;
};

/**
 * AdminLayout Component
 */
export const AdminLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  // Get current user from localStorage (mock)
  const authData = localStorage.getItem('treebeard_auth');
  const user = authData ? JSON.parse(authData) : null;

  const breadcrumbs = getBreadcrumbs(location.pathname);

  const handleLogout = () => {
    mockLogout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 bg-gray-900 text-white">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-gray-800">
          <svg className="w-8 h-8 text-primary-400 mr-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" />
          </svg>
          <span className="text-xl font-bold">TreeBeard</span>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center px-3 py-2.5 mb-1 rounded-lg transition-colors duration-200',
                  'text-sm font-medium',
                  isActive
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                )
              }
            >
              {item.icon}
              <span className="ml-3">{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="ml-64">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 fixed top-0 right-0 left-64 z-10">
          <div className="h-full px-6 flex items-center justify-between">
            {/* Breadcrumbs */}
            <nav className="flex items-center space-x-2 text-sm">
              {breadcrumbs.map((crumb, index) => (
                <React.Fragment key={crumb.path}>
                  {index > 0 && (
                    <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                  {index === breadcrumbs.length - 1 ? (
                    <span className="font-medium text-gray-900">{crumb.name}</span>
                  ) : (
                    <button
                      onClick={() => navigate(crumb.path)}
                      className="text-gray-500 hover:text-gray-700 transition-colors"
                    >
                      {crumb.name}
                    </button>
                  )}
                </React.Fragment>
              ))}
            </nav>

            {/* User Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                aria-label="User menu"
                aria-expanded={userMenuOpen}
              >
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user?.full_name?.charAt(0) || 'A'}
                </div>
                <div className="text-left">
                  <div className="text-sm font-medium text-gray-900">{user?.full_name || 'Admin'}</div>
                  <div className="text-xs text-gray-500">{user?.email || 'admin@treebeard.com'}</div>
                </div>
                <svg className={clsx('w-4 h-4 text-gray-400 transition-transform', userMenuOpen && 'rotate-180')} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {userMenuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setUserMenuOpen(false)}
                    aria-hidden="true"
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        // Navigate to settings (not implemented)
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Settings
                    </button>
                    <div className="border-t border-gray-200 my-1" />
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        handleLogout();
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-danger hover:bg-danger-light flex items-center"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Logout
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="pt-16 min-h-screen">
          <div className="p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
