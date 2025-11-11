import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { mockLogin, mockLogout } from './components/auth/RequireAdmin';
import './index.css';

// Expose mock auth functions to browser console for demo purposes
if (typeof window !== 'undefined') {
  (window as any).mockLogin = mockLogin;
  (window as any).mockLogout = mockLogout;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
