// Just a standard component, nothing fancy here.

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';

export const LoginForm: React.FC = () => {
  // Store the user's input
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  // Store any error messages from the server
  const [error, setError] = useState('');
  // Show a loading spinner while waiting for the server
  const [isLoading, setIsLoading] = useState(false);
  
  // Get the login function from our AuthContext
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Don't refresh the page
    setIsLoading(true);
    setError(''); // Clear previous errors
    
    try {
      await login(username, password);
      // If successful, go to the dashboard
      window.location.href = '/dashboard';
    } catch (err: any) {
      // If failed, show the error message
      setError(err.response?.data?.detail || 'Failed to login');
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 card shadow-lg">
      <div className="flex justify-center mb-6">
        <div className="w-14 h-14 rounded-2xl bg-primary-500 flex items-center justify-center">
          <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </div>
      </div>
      <h2 className="text-2xl font-bold text-center mb-1 text-navy-700 dark:text-white">Welcome Back</h2>
      <p className="text-center text-sm text-gray-400 mb-6">Sign in to your HealthLens account</p>
      
      {/* Show error message box if there's an error */}
      {error && <div className="mb-4 p-3 bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-xl text-sm">{error}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="login-email" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">Email</label>
          {/* onChange updates the 'username' state every time the user types a character */}
          <input id="login-email" type="email" value={username} onChange={(e) => setUsername(e.target.value)} className="input-field" placeholder="you@example.com" required autoComplete="email" />
        </div>
        <div>
          <label htmlFor="login-password" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">Password</label>
          <input id="login-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" placeholder="••••••••" required autoComplete="current-password" />
        </div>
        <button type="submit" disabled={isLoading} className="btn-primary w-full flex justify-center items-center py-3">
          {isLoading ? (
            <div className="flex items-center"><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>Signing in...</div>
          ) : 'Sign In'}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-gray-500">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary-500 font-semibold hover:underline">Register</Link>
      </p>
    </div>
  );
};
