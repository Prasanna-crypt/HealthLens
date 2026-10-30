// Just a standard component, nothing fancy here.

import React, { useState } from 'react';

export const Disclaimer: React.FC = () => {
  // Track if the banner is currently visible
  const [visible, setVisible] = useState(true);
  
  // If not visible, return nothing (don't render)
  if (!visible) return null;

  return (
    <div className="bg-primary-50 dark:bg-primary-900/20 border-t border-primary-100 dark:border-primary-800 p-3 sm:p-4 flex items-start sm:items-center justify-between">
      <div className="flex items-start">
        <svg className="w-5 h-5 text-primary-500 mt-0.5 sm:mt-0 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-xs sm:text-sm text-primary-700 dark:text-primary-300 leading-snug">
          This application provides informational interpretation of laboratory results and is not a substitute for professional medical advice, diagnosis, or treatment.
        </p>
      </div>
      
      {/* Dismiss button - sets visible to false */}
      <button onClick={() => setVisible(false)} className="ml-4 text-primary-400 hover:text-primary-600 dark:hover:text-primary-300">
        <span className="sr-only">Dismiss</span>
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};
