// Just a standard component, nothing fancy here.

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LoadingSpinner } from '../common/LoadingSpinner';

export const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  // If we are still checking local storage for a token, show a loading spinner
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center gradient-bg"><LoadingSpinner text="Checking authentication..." /></div>;
  }

  // If logged in, show the requested page (<Outlet/>). If not, redirect to /login
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};
