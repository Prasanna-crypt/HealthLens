import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { authAPI } from '../../lib/api';
import { Link } from 'react-router-dom';

export const LoginForm: React.FC = () => {
  // Store the user's input
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  // Store any error/success messages
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  // Show loading spinners
  const [isLoading, setIsLoading] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  // Forgot / Reset password mode toggle
  const [isResetMode, setIsResetMode] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  
  // Get auth functions from our AuthContext
  const { login, loginDemo } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');
    
    try {
      if (isResetMode) {
        if (newPassword.length < 6) {
          setError('Password must be at least 6 characters');
          setIsLoading(false);
          return;
        }
        await authAPI.resetPassword(username, newPassword);
        await login(username, newPassword);
        window.location.href = '/dashboard';
      } else {
        await login(username, password);
        window.location.href = '/dashboard';
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to authenticate';
      setError(msg);
      setIsLoading(false);
    }
  };

  const handleDemoSignIn = async () => {
    setIsDemoLoading(true);
    setError('');
    try {
      await loginDemo();
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start demo session');
      setIsDemoLoading(false);
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
      <h2 className="text-2xl font-bold text-center mb-1 text-navy-700 dark:text-white">
        {isResetMode ? 'Reset Your Password' : 'Welcome Back'}
      </h2>
      <p className="text-center text-sm text-gray-400 mb-6">
        {isResetMode ? 'Enter your email and a new password' : 'Sign in to your HealthLens account'}
      </p>
      
      {/* Feedback Messages */}
      {error && (
        <div className="mb-4 p-3 bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-xl text-sm flex items-start gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-xl text-sm">
          {success}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="login-email" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">Email</label>
          <input 
            id="login-email" 
            type="email" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            className="input-field" 
            placeholder="you@example.com" 
            required 
            autoComplete="email" 
          />
        </div>

        {isResetMode ? (
          <div>
            <label htmlFor="reset-new-password" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">New Password</label>
            <input 
              id="reset-new-password" 
              type="password" 
              value={newPassword} 
              onChange={(e) => setNewPassword(e.target.value)} 
              className="input-field" 
              placeholder="Minimum 6 characters" 
              required 
              autoComplete="new-password" 
            />
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label htmlFor="login-password" className="block text-sm font-medium text-gray-600 dark:text-gray-300">Password</label>
              <button 
                type="button" 
                onClick={() => { setIsResetMode(true); setError(''); }}
                className="text-xs text-primary-500 hover:underline"
              >
                Forgot password?
              </button>
            </div>
            <input 
              id="login-password" 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              className="input-field" 
              placeholder="••••••••" 
              required 
              autoComplete="current-password" 
            />
          </div>
        )}

        <button type="submit" disabled={isLoading || isDemoLoading} className="btn-primary w-full flex justify-center items-center py-3">
          {isLoading ? (
            <div className="flex items-center"><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>{isResetMode ? 'Updating...' : 'Signing in...'}</div>
          ) : isResetMode ? 'Update Password & Sign In' : 'Sign In'}
        </button>

        {isResetMode && (
          <button
            type="button"
            onClick={() => { setIsResetMode(false); setError(''); }}
            className="w-full text-center text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 mt-2"
          >
            ← Back to regular sign in
          </button>
        )}
      </form>

      {!isResetMode && (
        <>
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200 dark:border-gray-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white dark:bg-navy-800 px-3 text-gray-400">or</span>
            </div>
          </div>

          <button
            type="button"
            disabled={isLoading || isDemoLoading}
            onClick={handleDemoSignIn}
            className="w-full py-2.5 px-4 rounded-xl border border-primary-500/40 text-primary-500 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-950/30 transition-all font-medium text-sm flex items-center justify-center gap-2"
          >
            {isDemoLoading ? (
              <div className="flex items-center"><div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mr-2"></div>Starting Demo Session...</div>
            ) : (
              <>
                <span>⚡</span> Explore with Preloaded Demo Account
              </>
            )}
          </button>

          <p className="mt-6 text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-500 font-semibold hover:underline">Register</Link>
          </p>
        </>
      )}
    </div>
  );
};
