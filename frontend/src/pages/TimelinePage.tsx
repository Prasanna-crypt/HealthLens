import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportsAPI } from '../lib/api';
import type { ReportListItem } from '../lib/types';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { FileText, Calendar, Activity } from 'lucide-react';

export const TimelinePage: React.FC = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const res = await reportsAPI.list();
        const list = Array.isArray(res?.data) ? res.data : [];
        // Sort newest first
        setReports(list.sort((a: ReportListItem, b: ReportListItem) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()));
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load timeline');
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  if (loading) return <LoadingSpinner text="Loading timeline..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="p-6 max-w-4xl mx-auto animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Health Timeline</h1>
      
      {reports.length === 0 ? (
        <div className="text-center p-8 card text-gray-500">
          No reports found. Upload a report to start your timeline.
        </div>
      ) : (
        <div className="relative border-l border-gray-200 dark:border-gray-700 ml-3 md:ml-6 space-y-8 pb-8">
          {reports.map((report) => (
            <div key={report.id} className="relative pl-8 md:pl-10">
              <div className="absolute w-6 h-6 bg-primary-100 rounded-full -left-3 border-4 border-white dark:border-gray-900 flex items-center justify-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full" />
              </div>
              
              <div 
                className="card p-5 cursor-pointer hover:border-primary-300 dark:hover:border-primary-700 transition-colors"
                onClick={() => navigate(`/results?report=${report.id}`)}
              >
                <div className="flex flex-col md:flex-row md:justify-between md:items-start mb-2">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <FileText className="w-5 h-5 text-gray-400" />
                    {report.filename}
                  </h3>
                  <div className="flex items-center text-sm text-gray-500 mt-1 md:mt-0 gap-1">
                    <Calendar className="w-4 h-4" />
                    {new Date(report.upload_date).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
                  </div>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                  {report.total_tests} tests analyzed: {report.normal_count} normal, {report.low_count} low, {report.high_count} high.
                </p>
                
                <div className="flex gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300">
                    <Activity className="w-3 h-3 inline mr-1" />
                    View Details
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
