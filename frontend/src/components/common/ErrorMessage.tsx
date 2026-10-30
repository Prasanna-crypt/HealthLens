import React from 'react';

export const ErrorMessage: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div className="bg-rose-50 dark:bg-rose-900/30 border border-rose-200 dark:border-rose-800 rounded-xl p-4 flex flex-col items-center justify-center text-center">
    <svg className="w-10 h-10 text-rose-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
    <p className="text-rose-700 dark:text-rose-300 font-medium mb-4">{message}</p>
    {onRetry && (
      <button onClick={onRetry} className="btn-secondary text-sm py-1.5 px-4">
        Try Again
      </button>
    )}
  </div>
);
