import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { ReportsPage } from './pages/ReportsPage';
import { TestResultsPage } from './pages/TestResultsPage';
import { HealthInsightsPage } from './pages/HealthInsightsPage';
import { SettingsPage } from './pages/SettingsPage';

// Additional Pages
import { TimelinePage } from './pages/TimelinePage';
import { ChangesPage } from './pages/ChangesPage';
import { PatternsPage } from './pages/PatternsPage';
import { AIAssistantPage } from './pages/AIAssistantPage';
import { ProfilePage } from './pages/ProfilePage';
import { PrivacyPage } from './pages/PrivacyPage';

export const router = createBrowserRouter([
  // Public route for login
  {
    path: '/login',
    element: <LoginPage />,
  },
  // Public route for registration
  {
    path: '/register',
    element: <RegisterPage />,
  },
  // Protected routes - must be logged in
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        path: '/',
        element: <Navigate to="/dashboard" replace />,
      },
      {
        element: <DashboardLayout />,
        children: [
          { path: 'dashboard', element: <DashboardPage /> },
          { path: 'upload', element: <UploadPage /> },
          { path: 'reports', element: <ReportsPage /> },
          { path: 'results', element: <TestResultsPage /> },
          { path: 'insights', element: <HealthInsightsPage /> },
          { path: 'timeline', element: <TimelinePage /> },
          { path: 'changes', element: <ChangesPage /> },
          { path: 'patterns', element: <PatternsPage /> },
          { path: 'assistant', element: <AIAssistantPage /> },
          { path: 'profile', element: <ProfilePage /> },
          { path: 'privacy', element: <PrivacyPage /> },
          { path: 'settings', element: <SettingsPage /> },
        ]
      }
    ],
  },
  // Fallback route for unknown URLs (404 error)
  {
    path: '*',
    element: <div className="flex h-screen items-center justify-center text-2xl font-bold">404 Not Found</div>,
  }
]);
