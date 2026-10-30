// Just a standard component, nothing fancy here.

import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Disclaimer } from '../common/Disclaimer';

export const DashboardLayout: React.FC = () => {
  // State to track if the sidebar is open on mobile devices
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-transparent flex">
      {/* The side navigation menu */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Main content area (takes up remaining space) */}
      <div className="flex-1 flex flex-col lg:pl-64 transition-all duration-300 min-h-screen">
        {/* The top navigation bar */}
        <Header onMenuClick={() => setSidebarOpen(true)} />
        
        {/* The actual page content goes here */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 pb-24">
          <div className="max-w-7xl mx-auto animate-fade-in">
            {/* React Router will inject the current page component here */}
            <Outlet />
          </div>
        </main>
        
        {/* The medical disclaimer pinned to the bottom */}
        <div className="fixed bottom-0 right-0 w-full lg:w-[calc(100%-16rem)] z-20">
          <Disclaimer />
        </div>
      </div>
    </div>
  );
};
