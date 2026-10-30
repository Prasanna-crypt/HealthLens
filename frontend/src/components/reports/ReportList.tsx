// Just a standard component, nothing fancy here.

import React from 'react';
import type { ReportListItem } from '../../lib/types';
import { Link } from 'react-router-dom';

interface Props {
  reports: ReportListItem[];
  selectedIds: number[];
  onToggleSelect: (id: number) => void;
  onCompare: () => void;
  onDelete: (id: number) => void;
}

export const ReportList: React.FC<Props> = ({ reports, selectedIds, onToggleSelect, onCompare, onDelete }) => {
  // --- Empty State UI ---
  if (reports.length === 0) {
    return (
      <div className="card p-12 flex flex-col items-center justify-center text-center mt-6">
        <div className="w-20 h-20 bg-primary-50 dark:bg-primary-900/20 rounded-full flex items-center justify-center mb-6">
          <svg className="w-10 h-10 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No reports yet</h3>
        <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md">
          Upload your first medical report to start tracking your health data.
        </p>
        <Link to="/upload" className="btn-primary">Upload Report</Link>
      </div>
    );
  }

  // --- Grid List UI ---
  return (
    <div className="relative pb-24">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        {reports.map((report) => {
          // Check if this specific card is currently checked/selected
          const isSelected = selectedIds.includes(report.id);
          
          return (
            <div 
              key={report.id} 
              // Style changes drastically if selected to highlight it
              className={`card-hover p-6 transition-all duration-200 border-2 ${
                isSelected 
                  ? 'border-primary-500 ring-4 ring-primary-500/10 shadow-primary-500/20' 
                  : 'border-transparent hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-lg'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-start">
                  {/* Custom Checkbox */}
                  <div className="mt-1 mr-3 flex-shrink-0" onClick={() => onToggleSelect(report.id)}>
                    <div className={`w-5 h-5 rounded border flex items-center justify-center cursor-pointer transition-colors ${
                      isSelected 
                        ? 'bg-primary-500 border-primary-500 text-white' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
                    }`}>
                      {isSelected && (
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                  {/* Title & Date */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate max-w-[200px] sm:max-w-xs" title={report.filename}>
                      {report.filename}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {report.report_date || new Date(report.upload_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                
                {/* Actions: View and Delete */}
                <div className="flex space-x-2">
                  <Link to={`/dashboard?report=${report.id}`} className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded-full transition-colors" title="View Dashboard">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </Link>
                  <button onClick={() => onDelete(report.id)} className="p-2 text-gray-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded-full transition-colors" title="Delete Report">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              
              {/* DEMO Tag */}
              {report.is_demo && (
                <div className="mb-4 inline-block px-2 py-0.5 bg-violet-100 text-violet-700 dark:bg-violet-900/50 dark:text-violet-300 rounded text-xs font-bold tracking-wider uppercase border border-violet-200 dark:border-violet-800">
                  DEMO DATA
                </div>
              )}

              {/* Statistics Strip */}
              <div className="flex justify-between items-center bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3">
                <div className="text-center">
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase font-semibold">Total</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{report.total_tests}</p>
                </div>
                <div className="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>
                <div className="text-center">
                  <p className="text-xs text-emerald-600 dark:text-emerald-500 uppercase font-semibold">Normal</p>
                  <p className="text-lg font-bold text-emerald-700 dark:text-emerald-400">{report.normal_count}</p>
                </div>
                <div className="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>
                <div className="text-center">
                  <p className="text-xs text-amber-600 dark:text-amber-500 uppercase font-semibold">Low</p>
                  <p className="text-lg font-bold text-amber-700 dark:text-amber-400">{report.low_count}</p>
                </div>
                <div className="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>
                <div className="text-center">
                  <p className="text-xs text-rose-600 dark:text-rose-500 uppercase font-semibold">High</p>
                  <p className="text-lg font-bold text-rose-700 dark:text-rose-400">{report.high_count}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Floating Action Button - Only shows when exactly 2 reports are selected */}
      <div className={`fixed bottom-12 left-1/2 transform -translate-x-1/2 z-30 transition-all duration-300 ${
        selectedIds.length === 2 
          ? 'translate-y-0 opacity-100' 
          : 'translate-y-20 opacity-0 pointer-events-none'
      }`}>
        <div className="card px-6 py-4 flex items-center space-x-6 shadow-2xl border-primary-500/30">
          <span className="text-sm font-medium text-gray-900 dark:text-white">2 reports selected</span>
          <button onClick={onCompare} className="btn-primary shadow-lg shadow-primary-500/30 whitespace-nowrap">
            Compare Selected
          </button>
        </div>
      </div>
    </div>
  );
};
