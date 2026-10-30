import React, { useEffect, useState } from 'react';
import { reportsAPI } from '../lib/api';
import type { Report, TestResult } from '../lib/types';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const HealthInsightsPage: React.FC = () => {
  const [reports, setReports] = useState<{id: number, filename: string, date: string}[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<number | null>(null);
  
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch reports for dropdown
  useEffect(() => {
    const fetchReports = async () => {
      try {
        const res = await reportsAPI.list();
        setReports(res.data.map((r: any) => ({ 
          id: r.id, 
          filename: r.filename, 
          date: r.report_date || r.upload_date.split('T')[0] 
        })));
        
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

  // Fetch selected report
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

  // Filter for irregular tests
  const irregularTests = report?.test_results.filter(
    (t: TestResult) => t.status === 'LOW' || t.status === 'HIGH'
  ) || [];

  return (
    <div className="animate-fade-in flex flex-col min-h-screen">
      {/* Header Area */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Health Insights</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Natural remedies and explanations for your irregular test results.</p>
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

      {/* Main Content Area */}
      {!report ? (
        <div className="card h-64 flex items-center justify-center text-gray-500">
          No reports available.
        </div>
      ) : irregularTests.length === 0 ? (
        <div className="card p-10 flex flex-col items-center justify-center text-center">
          <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mb-4">
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Great News!</h3>
          <p className="text-gray-500 dark:text-gray-400 max-w-md">
            None of the tests in this report came back with irregular levels. You have no specific insights or remedies to review at this time.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {irregularTests.map((test) => (
            <div key={test.id} className="card relative overflow-hidden group hover:shadow-xl transition-all duration-300">
              
              {/* Highlight bar at top based on status */}
              <div className={`absolute top-0 left-0 w-full h-1 ${test.status === 'HIGH' ? 'bg-orange-500' : 'bg-blue-500'}`} />
              
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate pr-2">
                    {test.test_name}
                  </h3>
                  <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                    test.status === 'HIGH' 
                      ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' 
                      : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  }`}>
                    {test.status}
                  </span>
                </div>
                
                <div className="flex items-baseline gap-2 mb-6 pb-4 border-b border-gray-100 dark:border-gray-800">
                  <span className="text-3xl font-black text-gray-900 dark:text-white">{test.value}</span>
                  <span className="text-gray-500 text-sm font-medium">{test.unit}</span>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-primary-600 dark:text-primary-400 uppercase tracking-wider">
                    Insight & Remedies
                  </h4>
                  <div className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                    {test.ai_explanation || "No explanation was generated for this test."}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
