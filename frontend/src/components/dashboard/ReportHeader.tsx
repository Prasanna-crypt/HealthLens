// Just a standard component, nothing fancy here.

import React from 'react';
import type { Report } from '../../lib/types';

export const ReportHeader: React.FC<{ report: Report }> = ({ report }) => {
  return (
    <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
      <div>
        <h2 className="text-2xl font-bold text-navy-700 dark:text-white mb-2 flex items-center">
          {/* Default to 'Unknown Patient' if OCR couldn't read the name */}
          {report.patient_name || 'Unknown Patient'}
          
          {/* Show a DEMO badge if this is dummy data */}
          {report.is_demo && (
            <span className="ml-3 px-2 py-0.5 bg-primary-100 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300 rounded text-xs font-bold tracking-wider uppercase border border-primary-200 dark:border-primary-800">
              DEMO DATA
            </span>
          )}
        </h2>
        
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-500 dark:text-gray-400">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Report Date: {report.report_date || 'Unknown'}
          </span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            File: {report.filename}
          </span>
        </div>
      </div>
      
      <div className="text-sm text-gray-400 dark:text-gray-500">
        Uploaded: {new Date(report.upload_date).toLocaleDateString()}
      </div>
    </div>
  );
};
