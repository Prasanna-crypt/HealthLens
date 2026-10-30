// Just a standard component, nothing fancy here.

import React from 'react';
import { ThemeToggle } from '../common/ThemeToggle';
import { useAuth } from '../../context/AuthContext';

export const Header: React.FC<{ onMenuClick: () => void }> = ({ onMenuClick }) => {
  const { user } = useAuth(); // Get user information to display their name
  
  return (
    <header className="h-16 bg-white/60 dark:bg-gray-900/50 backdrop-blur-xl border-b border-white/40 dark:border-white/10 flex items-center px-4 sm:px-6 lg:px-8 sticky top-0 z-30">
      
      {/* Mobile Menu Button (Hamburger icon) */}
      <button
        onClick={onMenuClick}
        className="lg:hidden mr-4 p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      
      {/* App Title (hidden on very small screens) */}
      <div className="flex-1">
        <h1 className="text-lg font-semibold text-navy-700 dark:text-white hidden sm:block">Health Report Analyzer</h1>
      </div>

      {/* Right side controls (Theme Toggle + User Info) */}
      <div className="flex items-center space-x-3">
        <ThemeToggle />
        
        {/* User Info Section (hidden on very small screens) */}
        <div className="hidden sm:flex items-center pl-3 border-l border-gray-200 dark:border-gray-700">
          <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-600 dark:text-primary-300 font-bold text-xs">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <span className="ml-2 text-sm font-medium text-navy-700 dark:text-gray-300">{user?.full_name}</span>
        </div>
      </div>
    </header>
  );
};
