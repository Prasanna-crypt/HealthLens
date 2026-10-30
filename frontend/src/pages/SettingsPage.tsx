// Just a standard component, nothing fancy here.

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { demoAPI } from '../lib/api';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth(); // Get currently logged in user info
  const { theme, toggleTheme } = useTheme(); // Get current theme and the function to flip it
  
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [msg, setMsg] = useState('');

  // Contacts the backend to populate the database with fake data for testing
  const handleLoadDemo = async () => {
    setLoadingDemo(true);
    setMsg('');
    try {
      await demoAPI.load();
      setMsg('Demo data loaded successfully!');
      // After success, automatically send them back to the dashboard to see the data
      setTimeout(() => window.location.href = '/dashboard', 1000);
    } catch (err) {
      setMsg('Failed to load demo data.');
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="animate-fade-in max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Settings</h2>

      <div className="space-y-6">
        
        {/* Profile Card */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Profile</h3>
          <div className="flex items-center space-x-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-primary-500 flex items-center justify-center text-white text-2xl font-bold">
              {/* Show first letter of name as avatar */}
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <p className="font-bold text-lg text-gray-900 dark:text-white">{user?.full_name}</p>
              <p className="text-gray-500">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Theme Settings Card */}
        <div className="card p-6 flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Appearance</h3>
            <p className="text-sm text-gray-500">Toggle dark/light theme</p>
          </div>
          <button 
            onClick={toggleTheme}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          </button>
        </div>

        {/* Developer / Demo Tools Card */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Development Tools</h3>
          <p className="text-sm text-gray-500 mb-4">Populate your account with sample reports to explore features.</p>
          <button 
            onClick={handleLoadDemo} 
            disabled={loadingDemo}
            className="btn-primary"
          >
            {loadingDemo ? 'Loading...' : 'Load Demo Data'}
          </button>
          {msg && <p className="mt-3 text-sm font-medium text-emerald-600 dark:text-emerald-400">{msg}</p>}
        </div>

        {/* Version Info Footer */}
        <div className="card p-6 text-center text-sm text-gray-400">
          <p>HealthLens — AI-Powered Health Report Analyzer</p>
          <p>Version 1.0.0</p>
        </div>
      </div>
    </div>
  );
};
