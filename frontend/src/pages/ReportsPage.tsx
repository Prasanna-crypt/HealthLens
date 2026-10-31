// Just a standard component, nothing fancy here.

import React, { useEffect, useState } from 'react';
import { reportsAPI } from '../lib/api';
import type { ReportListItem, ReportComparison as ReportComparisonType } from '../lib/types';
import { ReportList } from '../components/reports/ReportList';
import { ReportComparison } from '../components/reports/ReportComparison';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Array storing the IDs of the reports the user has checked to compare
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  // Holds the result of comparing two reports
  const [comparisonData, setComparisonData] = useState<ReportComparisonType | null>(null);
  const [comparing, setComparing] = useState(false);

  // Fetch all reports on page load
  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await reportsAPI.list();
      setReports(Array.isArray(res?.data) ? res.data : []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  // Handles checking/unchecking a report for comparison
  const handleToggleSelect = (id: number) => {
    setSelectedIds(prev => {
      // If already selected, remove it
      if (prev.includes(id)) return prev.filter(i => i !== id);
      // If 2 are already selected and we click a 3rd, replace the oldest selection
      if (prev.length >= 2) return [prev[1], id];
      // Otherwise just add it
      return [...prev, id];
    });
  };

  // Calls API to compare the 2 selected reports
  const handleCompare = async () => {
    if (selectedIds.length !== 2) return;
    setComparing(true);
    try {
      const res = await reportsAPI.compare(selectedIds[0], selectedIds[1]);
      setComparisonData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to compare reports');
    } finally {
      setComparing(false);
    }
  };

  const handleDelete = async (id: number) => {
    // Browser confirmation popup
    if (!window.confirm('Are you sure you want to delete this report? This action cannot be undone.')) return;
    try {
      await reportsAPI.delete(id);
      // Remove from UI without needing to refresh from server
      setReports(prev => prev.filter(r => r.id !== id));
      setSelectedIds(prev => prev.filter(i => i !== id));
    } catch (err: any) {
      alert('Failed to delete report');
    }
  };

  if (loading) return <LoadingSpinner text="Loading reports..." />;
  if (error && !comparisonData) return <ErrorMessage message={error} onRetry={fetchReports} />;

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">My Reports</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Manage and compare your uploaded medical reports.</p>
        </div>
      </div>

      {comparing ? (
        <LoadingSpinner text="Comparing reports..." />
      ) : (
        <ReportList 
          reports={reports} 
          selectedIds={selectedIds} 
          onToggleSelect={handleToggleSelect} 
          onCompare={handleCompare} 
          onDelete={handleDelete}
        />
      )}

      {/* Show the comparison modal if we have data */}
      {comparisonData && (
        <ReportComparison data={comparisonData} onClose={() => setComparisonData(null)} />
      )}
    </div>
  );
};
