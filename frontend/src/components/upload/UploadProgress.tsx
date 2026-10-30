// Just a standard component, nothing fancy here.

import React from 'react';
import type { ProcessingStage } from '../../lib/types';

// The different steps in the processing pipeline
const steps = [
  { id: 'uploading', label: 'Uploading', icon: '📤' },
  { id: 'reading', label: 'Reading Report', icon: '📖' },
  { id: 'extracting', label: 'Extracting Results', icon: '🔍' },
  { id: 'comparing', label: 'Comparing Values', icon: '⚖️' },
  { id: 'explaining', label: 'Generating Explanation', icon: '🤖' },
  { id: 'complete', label: 'Dashboard Ready', icon: '✨' },
];

interface Props {
  currentStage: ProcessingStage;
  uploadPercent?: number;
  error?: string;
  onRetry?: () => void;
}

export const UploadProgress: React.FC<Props> = ({ currentStage, uploadPercent = 0, error, onRetry }) => {
  // Find which step number we are currently on
  const currentIndex = steps.findIndex(s => s.id === currentStage);
  
  return (
    <div className="w-full max-w-lg mx-auto py-8">
      {/* If there is an error, show the error box */}
      {error ? (
        <div className="bg-rose-50 dark:bg-rose-900/30 p-6 rounded-2xl text-center border border-rose-200 dark:border-rose-800">
          <div className="text-rose-500 mb-4 flex justify-center">
            <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-rose-800 dark:text-rose-300 mb-2">Processing Error</h3>
          <p className="text-rose-600 dark:text-rose-400 mb-6">{error}</p>
          {onRetry && (
            <button onClick={onRetry} className="btn-primary bg-gradient-to-r from-rose-600 to-rose-500 shadow-rose-500/25">
              Try Again
            </button>
          )}
        </div>
      ) : (
        // Otherwise, show the progress list
        <div className="space-y-6 relative">
          {/* Vertical line connecting the steps */}
          <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-gray-200 dark:bg-gray-700 z-0"></div>
          
          {steps.map((step, idx) => {
            const isCompleted = currentIndex > idx || currentStage === 'complete';
            const isCurrent = currentStage === step.id;
            
            return (
              <div key={step.id} className="relative z-10 flex items-center">
                {/* Step Icon Circle */}
                <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 transition-colors duration-300 ${
                  isCompleted ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/50 dark:text-emerald-400' :
                  isCurrent ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/50 dark:text-primary-400 shadow-[0_0_0_4px_rgba(12,184,182,0.1)]' :
                  'bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-500'
                }`}>
                  {isCompleted ? (
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-xl">{step.icon}</span>
                  )}
                </div>
                
                {/* Step Label and Loading Bar (if current) */}
                <div className="ml-4 flex-1">
                  <h4 className={`font-medium ${isCurrent ? 'text-primary-600 dark:text-primary-400 font-semibold' : isCompleted ? 'text-navy-700 dark:text-white' : 'text-gray-500 dark:text-gray-400'}`}>
                    {step.label}
                  </h4>
                  {isCurrent && (
                    <div className="mt-2 w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-300 ease-out" 
                        // If it's uploading, use the actual percent, otherwise fake it at 60%
                        style={{ width: step.id === 'uploading' ? `${uploadPercent}%` : '60%' }} 
                      ></div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
