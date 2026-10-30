// Just a standard component, nothing fancy here.

import React, { useEffect, useState } from 'react';
import { reportsAPI } from '../lib/api';
import type { Report, TestResult } from '../lib/types';
import { TestResultsTable } from '../components/dashboard/TestResultsTable';
import { TestDetailPanel } from '../components/dashboard/TestDetailPanel';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const TestResultsPage: React.FC = () => {
  // Store a lightweight list of reports just for the dropdown
  const [reports, setReports] = useState<{id: number, filename: string, date: string}[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<number | null>(null);
  
  // Store the full heavy report data currently being viewed
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Track which test row the user clicked to show the detail panel
  const [selectedTest, setSelectedTest] = useState<TestResult | null>(null);

  // 1. Get the list of all reports for the dropdown menu
  useEffect(() => {
    const fetchReports = async () => {
      try {
        const res = await reportsAPI.list();
        // Map the API data to a simpler structure needed for the dropdown
        setReports(res.data.map((r: any) => ({ 
          id: r.id, 
          filename: r.filename, 
          date: r.report_date || r.upload_date.split('T')[0] 
        })));
        
        // Auto-select the first report in the list
        if (res.data.length > 0) {
          setSelectedReportId(res.data[0].id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  // 2. Fetch the full table data whenever the user picks a different report from the dropdown
  useEffect(() => {
    if (selectedReportId) {
      const fetchReport = async () => {
        try {
          const res = await reportsAPI.get(selectedReportId);
          setReport(res.data);
        } catch (err) {
          console.error(err);
        }
      };
      fetchReport();
    }
  }, [selectedReportId]);

  if (loading) return <LoadingSpinner />;

  return (
    // Set a fixed height minus header so the table can scroll internally
    <div className="animate-fade-in h-[calc(100vh-140px)] flex flex-col">
      
      {/* Header Area with Dropdown */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">All Test Results</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Detailed view of every extracted value.</p>
        </div>
        
        {reports.length > 0 && (
          <select 
            value={selectedReportId || ''} 
            onChange={(e) => setSelectedReportId(Number(e.target.value))}
            className="input-field max-w-xs cursor-pointer"
          >
            {reports.map(r => (
              <option key={r.id} value={r.id}>{r.filename} ({r.date})</option>
            ))}
          </select>
        )}
      </div>

      {/* Main Table Area (Expands to fill space) */}
      <div className="flex-1 overflow-hidden">
        {report ? (
          <TestResultsTable results={report.test_results} onSelect={setSelectedTest} />
        ) : (
          <div className="card h-full flex items-center justify-center text-gray-500">
            No reports available.
          </div>
        )}
      </div>

      {/* Slide-out detail panel (Hidden unless a row is clicked) */}
      <TestDetailPanel result={selectedTest} onClose={() => setSelectedTest(null)} />
    </div>
  );
};
