// Just a standard component, nothing fancy here.

import React from 'react';
import type { TestResult } from '../../lib/types';
import { StatusBadge } from '../common/StatusBadge';

export const TestResultsTable: React.FC<{ results: TestResult[]; onSelect: (r: TestResult) => void }> = ({ results, onSelect }) => {
  return (
    <div className="card overflow-hidden flex flex-col h-full">
      {/* Table Header Area */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700/50 flex justify-between items-center bg-white/50 dark:bg-gray-800/50">
        <h3 className="text-lg font-semibold text-navy-700 dark:text-white">Test Results</h3>
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{results.length} tests</span>
      </div>
      
      {/* Scrollable Table Area */}
      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50/50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
              <th className="px-6 py-3 font-medium">Test Name</th>
              <th className="px-6 py-3 font-medium text-right">Result</th>
              <th className="px-6 py-3 font-medium">Unit</th>
              <th className="px-6 py-3 font-medium text-center">Range</th>
              <th className="px-6 py-3 font-medium text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700/50">
            {results.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                  No results available.
                </td>
              </tr>
            ) : (
              results.map((res) => (
                <tr 
                  key={res.id} 
                  onClick={() => onSelect(res)} // Opens the slide-out panel
                  className="hover:bg-primary-50/50 dark:hover:bg-gray-700/30 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-3.5 text-sm font-semibold text-navy-700 dark:text-white">{res.test_name}</td>
                  
                  {/* Result Value - colored based on status */}
                  <td className={`px-6 py-3.5 text-sm font-bold text-right ${
                    res.status === 'LOW' ? 'text-amber-600 dark:text-amber-400' :
                    res.status === 'HIGH' ? 'text-rose-600 dark:text-rose-400' :
                    'text-navy-700 dark:text-white'
                  }`}>
                    {res.value}
                  </td>
                  
                  <td className="px-6 py-3.5 text-sm text-gray-500 dark:text-gray-400">{res.unit}</td>
                  
                  {/* Reference Range formatting */}
                  <td className="px-6 py-3.5 text-sm text-gray-500 dark:text-gray-400 text-center">
                    {res.reference_low !== null && res.reference_high !== null 
                      ? `${res.reference_low} - ${res.reference_high}` 
                      : 'N/A'}
                  </td>
                  
                  <td className="px-6 py-3.5 text-center">
                    <StatusBadge status={res.status} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
