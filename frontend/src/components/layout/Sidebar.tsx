import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Upload,
  FileText,
  Activity,
  Settings,
  Clock,
  ArrowRightLeft,
  Network,
  Bot,
  User,
  ShieldCheck
} from 'lucide-react';

export const Sidebar: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth(); // Get user details and logout function

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/upload', label: 'Upload Report', icon: Upload },
    { to: '/reports', label: 'My Reports', icon: FileText },
    { to: '/insights', label: 'Health Insights', icon: Activity },
    { to: '/timeline', label: 'Timeline', icon: Clock },
    { to: '/changes', label: 'Changes', icon: ArrowRightLeft },
    { to: '/patterns', label: 'Patterns', icon: Network },
    { to: '/assistant', label: 'AI Assistant', icon: Bot },
    { to: '/profile', label: 'Profile', icon: User },
    { to: '/privacy', label: 'Privacy', icon: ShieldCheck },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop - closes sidebar when clicked outside */}
      {isOpen && (
        <div className="fixed inset-0 z-40 bg-black/30 lg:hidden" onClick={onClose} />
      )}

      {/* Sidebar container */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white/60 dark:bg-gray-900/50 backdrop-blur-xl border-r border-white/40 dark:border-white/10 transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'} flex flex-col shadow-[0_8px_32px_0_rgba(31,38,135,0.05)]`}>
        
        {/* App Logo */}
        <div className="h-16 flex items-center px-6 border-b border-white/40 dark:border-white/10">
          <div className="w-9 h-9 rounded-xl bg-primary-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <span className="ml-3 text-xl font-bold text-navy-700 dark:text-white">Health<span className="text-primary-500">Lens</span></span>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => { if (window.innerWidth < 1024) onClose(); }} // Auto-close on mobile
                // Change style based on whether this is the active page
                className={({ isActive }) =>
                  `flex items-center px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-white/50 dark:bg-gray-800/50 text-primary-600 dark:text-primary-400 shadow-sm border border-white/60 dark:border-white/10'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-white/40 dark:hover:bg-gray-800/40 hover:text-gray-900 dark:hover:text-white'
                  }`
                }
              >
                <Icon className="w-5 h-5 mr-3 flex-shrink-0" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* User Profile Section at bottom */}
        <div className="p-4 border-t border-white/40 dark:border-white/10">
          <div className="flex items-center">
            {/* User Avatar Initials */}
            <div className="w-9 h-9 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-600 dark:text-primary-300 font-bold text-sm">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="ml-3 min-w-0 flex-1">
              <p className="text-sm font-semibold text-navy-700 dark:text-white truncate">{user?.full_name}</p>
              <button onClick={logout} className="text-xs text-gray-400 hover:text-red-500 transition-colors">Sign Out</button>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
