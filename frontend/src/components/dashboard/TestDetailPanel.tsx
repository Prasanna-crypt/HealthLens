// Just a standard component, nothing fancy here.

import React from 'react';
import type { TestResult } from '../../lib/types';
import { StatusBadge } from './StatusBadge';

export const TestDetailPanel: React.FC<{ result: TestResult | null; onClose: () => void }> = ({ result, onClose }) => {
  // If no result is selected, render nothing
  if (!result) return null;

  const { test_name, value, unit, reference_low, reference_high, status, category } = result;

  // --- Math to draw the visual "range" bar ---
  let posPercent = 50;
  let hasRange = reference_low !== null && reference_high !== null;
  if (hasRange) {
    const range = reference_high! - reference_low!;
    // Extend the visual range by 50% on both sides so values outside the normal range can be plotted
    const minDisplay = reference_low! - (range * 0.5);
    const maxDisplay = reference_high! + (range * 0.5);
    const totalDisplayRange = maxDisplay - minDisplay;
    // Calculate percentage (0 to 100)
    posPercent = Math.max(0, Math.min(100, ((value - minDisplay) / totalDisplayRange) * 100));
  }

  return (
    <>
      {/* Dark semi-transparent background. Clicking it closes the panel */}
      <div className="fixed inset-0 z-40 bg-gray-900/20 dark:bg-black/40 backdrop-blur-sm" onClick={onClose} />
      
      {/* The actual slide-out panel on the right */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white dark:bg-gray-900 shadow-2xl border-l border-gray-200 dark:border-gray-800 animate-slide-in-right overflow-y-auto">
        <div className="p-6">
          
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              {category && <span className="text-xs font-medium text-primary-600 dark:text-primary-400 uppercase tracking-wider mb-1 block">{category}</span>}
              <h2 className="text-2xl font-bold text-navy-700 dark:text-white">{test_name}</h2>
            </div>
            <button onClick={onClose} className="p-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full text-gray-500 transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Big Number Display */}
          <div className="card !border-none !shadow-none bg-gray-50 dark:bg-gray-800/50 p-6 mb-8 text-center">
            <div className="flex justify-center items-baseline space-x-2 mb-3">
              <span className={`text-5xl font-black ${
                status === 'LOW' ? 'text-amber-500' :
                status === 'HIGH' ? 'text-rose-500' :
                'text-navy-700 dark:text-white'
              }`}>
                {value}
              </span>
              <span className="text-xl text-gray-500 dark:text-gray-400 font-medium">{unit}</span>
            </div>
            <StatusBadge status={status} />
          </div>

          {/* Visual Range Bar (only shows if we have high/low reference numbers) */}
          {hasRange && (
            <div className="mb-8">
              <h3 className="text-sm font-semibold text-navy-700 dark:text-white mb-4">Reference Range</h3>
              <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full mb-8">
                {/* The "Normal" green zone in the middle (25% to 75% visually) */}
                <div 
                  className="absolute h-full bg-emerald-400 dark:bg-emerald-500 rounded-full"
                  style={{ left: '25%', right: '25%' }}
                />
                {/* The specific dot for the patient's value */}
                <div 
                  className={`absolute top-1/2 -mt-2.5 w-5 h-5 rounded-full border-4 border-white dark:border-gray-900 shadow-md transform -translate-x-1/2 ${
                    status === 'LOW' ? 'bg-amber-500' :
                    status === 'HIGH' ? 'bg-rose-500' :
                    'bg-emerald-500'
                  }`}
                  style={{ left: `${posPercent}%` }}
                />
              </div>
              <div className="flex justify-between text-xs font-medium text-gray-500 dark:text-gray-400 px-4">
                <span className="text-left w-1/3"></span>
                <span className="text-center w-1/3">{reference_low} - {reference_high} {unit}</span>
                <span className="text-right w-1/3"></span>
              </div>
            </div>
          )}


          <div className="text-xs text-gray-400 dark:text-gray-500 text-center border-t border-gray-200 dark:border-gray-800 pt-6">
            Consult your healthcare provider for medical advice.
          </div>
        </div>
      </div>
    </>
  );
};
