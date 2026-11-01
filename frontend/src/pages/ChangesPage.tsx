import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { StatusBadge } from '../components/common/StatusBadge';
import { ArrowDown, ArrowUp, Minus } from 'lucide-react';

interface ChangeRow {
  test_name: string;
  previous_value: number;
  current_value: number;
  absolute_change: number;
  percentage_change: number;
  direction: 'Increased' | 'Decreased' | 'Stable';
  status?: string;
  current_status?: string;
  previous_status?: string;
}

// Utility to ensure clean 3 decimal places without long floating point noise
const formatDecimals = (val: number | null | undefined): string => {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return Number(val.toFixed(3)).toString();
};

export const ChangesPage: React.FC = () => {
  const [changes, setChanges] = useState<ChangeRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchChanges = async () => {
      try {
        const res = await api.get('/results/changes');
        setChanges(Array.isArray(res?.data) ? res.data : []);
      } catch (err: any) {
        // Fallback mock data if API is not ready
        if (err.response?.status === 404 || err.code === 'ERR_NETWORK') {
          console.warn("API not ready, using mock data for /api/changes");
          setChanges([
            { test_name: 'Hemoglobin', previous_value: 13.5, current_value: 12.1, absolute_change: -1.4, percentage_change: -10.37, direction: 'Decreased', status: 'LOW', current_status: 'LOW' },
            { test_name: 'Cholesterol', previous_value: 180, current_value: 210, absolute_change: 30, percentage_change: 16.67, direction: 'Increased', status: 'HIGH', current_status: 'HIGH' },
            { test_name: 'Vitamin D', previous_value: 30, current_value: 32, absolute_change: 2, percentage_change: 6.67, direction: 'Stable', status: 'NORMAL', current_status: 'NORMAL' },
          ]);
        } else {
          setError(err.response?.data?.detail || 'Failed to load changes');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchChanges();
  }, []);

  if (loading) return <LoadingSpinner text="Detecting changes..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="p-6 animate-fade-in max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Health Change Detector</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-6">Comparing your latest report with your previous results.</p>
      
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50/50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                <th className="px-6 py-3 font-medium">Test Name</th>
                <th className="px-6 py-3 font-medium text-right">Previous</th>
                <th className="px-6 py-3 font-medium text-right">Current</th>
                <th className="px-6 py-3 font-medium text-right">Change</th>
                <th className="px-6 py-3 font-medium text-center">Direction</th>
                <th className="px-6 py-3 font-medium text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700/50">
              {changes.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">No changes detected or insufficient data.</td>
                </tr>
              ) : (
                changes.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900 dark:text-white">{row.test_name}</td>
                    <td className="px-6 py-4 text-sm text-right text-gray-500 dark:text-gray-400">{formatDecimals(row.previous_value)}</td>
                    <td className="px-6 py-4 text-sm text-right font-medium text-gray-900 dark:text-white">{formatDecimals(row.current_value)}</td>
                    <td className="px-6 py-4 text-sm text-right font-medium">
                      <span className={row.percentage_change > 0 ? 'text-rose-600 dark:text-rose-400' : row.percentage_change < 0 ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500 dark:text-gray-400'}>
                        {row.absolute_change > 0 ? '+' : ''}{formatDecimals(row.absolute_change)} ({row.percentage_change > 0 ? '+' : ''}{formatDecimals(row.percentage_change)}%)
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-center">
                      {row.direction === 'Increased' ? <ArrowUp className="w-4 h-4 text-rose-500 mx-auto" /> :
                       row.direction === 'Decreased' ? <ArrowDown className="w-4 h-4 text-amber-500 mx-auto" /> :
                       <Minus className="w-4 h-4 text-gray-400 mx-auto" />}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <StatusBadge status={row.current_status || row.status || 'Normal'} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
