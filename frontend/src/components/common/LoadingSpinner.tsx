// Just a standard component, nothing fancy here.

import React from 'react';

export const LoadingSpinner: React.FC<{ text?: string }> = ({ text }) => (
  <div className="flex flex-col items-center justify-center p-8">
    <div className="w-12 h-12 border-4 border-primary-200 dark:border-primary-900 border-t-primary-600 rounded-full animate-spin"></div>
    {/* Only show the text paragraph if the text prop was provided */}
    {text && <p className="mt-4 text-gray-600 dark:text-gray-400 font-medium">{text}</p>}
  </div>
);
