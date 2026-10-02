import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppShell } from './components/layout/AppShell';

// Pages
import { LoginPage } from './pages/Auth/LoginPage';
import { SignupPage } from './pages/Auth/SignupPage';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { AnalyzeEmailPage } from './pages/AnalyzeEmail/AnalyzeEmailPage';
import { HistoryPage } from './pages/History/HistoryPage';
import { FeedbackPage } from './pages/Feedback/FeedbackPage';
import { AnalyticsPage } from './pages/Analytics/AnalyticsPage';
import { UserManagement } from './pages/Admin/UserManagement';
import { SettingsPage } from './pages/Settings/SettingsPage';
import { InboxScanPage } from './pages/InboxScan/InboxScanPage';

// Security route wrappers
interface ProtectedRouteProps {
  children: React.ReactNode;
  minRole?: string;
}

const isRoleAtLeast = (required: string, current: string): boolean => {
  const roles = ['user', 'analyst', 'ml_engineer', 'admin', 'super_admin'];
  const reqIndex = roles.indexOf(required);
  const currIndex = roles.indexOf(current);
  return currIndex >= reqIndex;
};

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, minRole = 'user' }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-slate-500 font-bold tracking-widest uppercase animate-pulse">Initializing operations Console</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (minRole && !isRoleAtLeast(minRole, user.role)) {
    return <Navigate to="/" replace />;
  }

  return <AppShell>{children}</AppShell>;
};

const PublicOnlyRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-slate-500 font-bold tracking-widest uppercase animate-pulse">Initializing operations Console</p>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Auth Routes */}
          <Route
            path="/login"
            element={
              <PublicOnlyRoute>
                <LoginPage />
              </PublicOnlyRoute>
            }
          />
          <Route
            path="/signup"
            element={
              <PublicOnlyRoute>
                <SignupPage />
              </PublicOnlyRoute>
            }
          />

          {/* Secure Operator Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute minRole="user">
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analyze"
            element={
              <ProtectedRoute minRole="user">
                <AnalyzeEmailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute minRole="user">
                <HistoryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/feedback"
            element={
              <ProtectedRoute minRole="user">
                <FeedbackPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute minRole="analyst">
                <AnalyticsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute minRole="admin">
                <UserManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute minRole="user">
                <SettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inbox"
            element={
              <ProtectedRoute minRole="user">
                <InboxScanPage />
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
