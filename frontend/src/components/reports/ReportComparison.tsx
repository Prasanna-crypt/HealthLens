// Just a standard component, nothing fancy here.

import React from 'react';
import type { ReportComparison as ReportComparisonType } from '../../lib/types';
import { StatusBadge } from '../dashboard/StatusBadge';

export const ReportComparison: React.FC<{ data: ReportComparisonType; onClose: () => void }> = ({ data, onClose }) => {
  const { report1, report2, comparisons } = data;

  return (
    // Modal Overlay
    <div className="fixed inset-0 z-50 overflow-y-auto bg-gray-50 dark:bg-gray-900 flex flex-col">
      
      {/* Top Header Bar */}
      <div className="sticky top-0 z-10 card !rounded-none !border-x-0 !border-t-0 px-4 py-4 sm:px-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center">
          <svg className="w-6 h-6 mr-2 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          Report Comparison
        </h2>
        {/* Close Button */}
        <button onClick={onClose} className="p-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full text-gray-500 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex-1 max-w-5xl mx-auto w-full p-4 sm:p-6 lg:p-8">
        
        {/* File Name Headers (Report 1 vs Report 2) */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="card p-4 sm:p-6 text-center sm:text-left">
            <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-semibold tracking-wider mb-1">Previous Report</p>
            <h3 className="font-bold text-gray-900 dark:text-white truncate" title={report1.filename}>{report1.filename}</h3>
            <p className="text-sm text-gray-500 mt-1">{report1.report_date || report1.upload_date?.split('T')[0]}</p>
          </div>
          <div className="card p-4 sm:p-6 border-2 border-primary-500 text-center sm:text-left">
            <p className="text-xs text-primary-600 dark:text-primary-400 uppercase font-semibold tracking-wider mb-1">Latest Report</p>
            <h3 className="font-bold text-gray-900 dark:text-white truncate" title={report2.filename}>{report2.filename}</h3>
            <p className="text-sm text-gray-500 mt-1">{report2.report_date || report2.upload_date?.split('T')[0]}</p>
          </div>
        </div>

        {/* Comparison Table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50/50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                  <th className="px-4 sm:px-6 py-4 font-medium">Test Name</th>
                  <th className="px-4 sm:px-6 py-4 font-medium text-center">Previous Value</th>
                  <th className="px-4 sm:px-6 py-4 font-medium text-center">Latest Value</th>
                  <th className="px-4 sm:px-6 py-4 font-medium text-center">Change</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700/50">
                {comparisons.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                      No common tests found between these reports.
                    </td>
                  </tr>
                ) : (
                  comparisons.map((comp, idx) => {
                    // Logic to see if the value went up or down
                    const isIncrease = comp.change > 0;
                    const isSame = comp.change === 0;

                    return (
                      <tr key={idx} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                        <td className="px-4 sm:px-6 py-4 text-sm font-semibold text-gray-900 dark:text-white">
                          {comp.test_name}
                        </td>
                        
                        <td className="px-4 sm:px-6 py-4 text-center">
                          <div className="font-medium text-gray-900 dark:text-white mb-1">{comp.report1_value} <span className="text-gray-500 text-xs font-normal">{comp.report1_unit}</span></div>
                          <StatusBadge status={comp.report1_status as any} />
                        </td>
                        
                        <td className="px-4 sm:px-6 py-4 text-center bg-primary-50/20 dark:bg-primary-900/10">
                          <div className="font-bold text-gray-900 dark:text-white mb-1">{comp.report2_value} <span className="text-gray-500 text-xs font-normal">{comp.report2_unit}</span></div>
                          <StatusBadge status={comp.report2_status as any} />
                        </td>
                        
                        <td className="px-4 sm:px-6 py-4 text-center">
                          {isSame ? (
                            <span className="text-gray-400 dark:text-gray-500 text-sm font-medium">— No change</span>
                          ) : (
                            // Render arrow icon and change amount
                            <div className={`inline-flex items-center space-x-1 text-sm font-bold ${isIncrease ? 'text-rose-500' : 'text-emerald-500'}`}>
                              <svg className={`w-4 h-4 ${isIncrease ? '' : 'transform rotate-180'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                              </svg>
                              <span>{Math.abs(comp.change).toFixed(2)}</span>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
