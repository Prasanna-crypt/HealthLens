// Just a standard component, nothing fancy here.

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';

export const RegisterForm: React.FC = () => {
  // Store form inputs
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }
    if (password.length < 6) {
      return setError('Password must be at least 6 characters');
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      await register(email.trim().toLowerCase(), password, fullName.trim());
      // Auto-login and go to dashboard
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register');
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 card shadow-lg">
      <div className="flex justify-center mb-4">
        <div className="w-14 h-14 rounded-2xl bg-primary-500 flex items-center justify-center">
          <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        </div>
      </div>
      <h2 className="text-2xl font-bold text-center mb-1 text-navy-700 dark:text-white">Create Account</h2>
      <p className="text-center text-sm text-gray-400 mb-6">Get started with HealthLens</p>
      
      {error && <div className="mb-4 p-3 bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-xl text-sm">{error}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="reg-name" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">Full Name</label>
          <input
            id="reg-name"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="input-field"
            placeholder="John Doe"
            required
            autoComplete="name"
          />
        </div>
        <div>
          <label htmlFor="reg-email" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">Email</label>
          <input
            id="reg-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-field"
            placeholder="you@example.com"
            required
            autoComplete="email"
          />
        </div>
        <div>
          <label htmlFor="reg-password" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">Password</label>
          <input
            id="reg-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-field"
            placeholder="••••••••"
            required
            minLength={6}
            autoComplete="new-password"
          />
        </div>
        <div>
          <label htmlFor="reg-confirm" className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1.5">Confirm Password</label>
          <input
            id="reg-confirm"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="input-field"
            placeholder="••••••••"
            required
            autoComplete="new-password"
          />
        </div>
        <button type="submit" disabled={isLoading} className="btn-primary w-full flex justify-center items-center py-3">
          {isLoading ? (
            <div className="flex items-center">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Creating account...
            </div>
          ) : 'Create Account'}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-gray-500">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-500 font-semibold hover:underline">
          Sign In
        </Link>
      </p>
    </div>
  );
};
