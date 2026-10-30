import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportsAPI } from '../lib/api';
import type { ReportListItem, Report, TestResult } from '../lib/types';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { FileText, Activity, AlertCircle, ArrowUpRight, ArrowRightLeft, Network } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [latestReportDetails, setLatestReportDetails] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const listRes = await reportsAPI.list();
        const reportList: ReportListItem[] = listRes.data;
        setReports(reportList);

        if (reportList.length > 0) {
          // Find latest report by upload_date
          const latest = [...reportList].sort(
            (a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()
          )[0];

          // Fetch full report details to get test results for the table
          const fullReportRes = await reportsAPI.get(latest.id);
          setLatestReportDetails(fullReportRes.data);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) return <LoadingSpinner text="Loading dashboard..." />;
  if (error) return <ErrorMessage message={error} />;

  if (reports.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center animate-fade-in">
        <div className="w-24 h-24 bg-primary-50 dark:bg-primary-900/20 rounded-full flex items-center justify-center mb-6">
          <Activity className="w-12 h-12 text-primary-500" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Welcome to HealthLens</h2>
        <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-md">
          You don't have any reports yet. Upload your first medical report to see your dashboard.
        </p>
        <div className="space-x-4">
          <button onClick={() => navigate('/upload')} className="btn-primary">Upload Report</button>
        </div>
      </div>
    );
  }

  // Aggregate stats across all reports
  const totalReports = reports.length;
  const totalTests = reports.reduce((acc, r) => acc + r.total_tests, 0);
  const totalNormal = reports.reduce((acc, r) => acc + r.normal_count, 0);
  const totalLow = reports.reduce((acc, r) => acc + r.low_count, 0);
  const totalHigh = reports.reduce((acc, r) => acc + r.high_count, 0);
  const totalAbnormal = totalLow + totalHigh;

  // Donut chart color scheme matching the mockup
  const COLOR_NORMAL = '#2dd4bf'; // Teal / Cyan
  const COLOR_LOW = '#facc15';    // Yellow
  const COLOR_HIGH = '#fb7185';   // Soft Red / Pink

  const pieData = [
    { name: 'High', value: totalHigh, color: COLOR_HIGH },
    { name: 'Low', value: totalLow, color: COLOR_LOW },
    { name: 'Normal', value: totalNormal, color: COLOR_NORMAL },
  ].filter(d => d.value > 0);

  const testResults: TestResult[] = latestReportDetails?.test_results || [];

  return (
    <div className="animate-fade-in space-y-6">
      {/* Aggregate Quick Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4 flex items-center space-x-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-full dark:bg-blue-900/30 dark:text-blue-400">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Total Reports</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">{totalReports}</p>
          </div>
        </div>

        <div className="card p-4 flex items-center space-x-4">
          <div className="p-3 bg-indigo-100 text-indigo-600 rounded-full dark:bg-indigo-900/30 dark:text-indigo-400">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Total Tests</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">{totalTests}</p>
          </div>
        </div>

        <div className="card p-4 flex items-center space-x-4">
          <div className="p-3 bg-teal-100 text-teal-600 rounded-full dark:bg-teal-900/30 dark:text-teal-400">
            <ArrowUpRight className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Normal Results</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">{totalNormal}</p>
          </div>
        </div>

        <div className="card p-4 flex items-center space-x-4">
          <div className="p-3 bg-rose-100 text-rose-600 rounded-full dark:bg-rose-900/30 dark:text-rose-400">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Abnormal Results</p>
            <p className="text-xl font-bold text-gray-900 dark:text-white">{totalAbnormal}</p>
          </div>
        </div>
      </div>

      {/* Main Hero Section: Left Table + Right Donut Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: Test Results Table (7 cols) */}
        <div className="lg:col-span-7 xl:col-span-8 card p-5 bg-white/70 dark:bg-slate-900/80 backdrop-blur-lg border border-gray-200 dark:border-slate-800 shadow-xl rounded-2xl overflow-hidden">
          <div className="flex items-center justify-between mb-4 px-1">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">Test Results</h2>
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {testResults.length > 0 ? `${testResults.length} tests` : `${totalTests} tests`}
            </span>
          </div>

          <div className="overflow-x-auto max-h-[460px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-slate-700">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 z-10 bg-gray-100/90 dark:bg-[#132237] text-gray-500 dark:text-gray-400 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4 rounded-tl-lg">TEST NAME</th>
                  <th className="py-3 px-4">RESULT</th>
                  <th className="py-3 px-4">UNIT</th>
                  <th className="py-3 px-4">RANGE</th>
                  <th className="py-3 px-4 text-right rounded-tr-lg">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200/60 dark:divide-slate-800/80 text-sm">
                {testResults.length > 0 ? (
                  testResults.map((t) => {
                    const isAbnormal = t.status === 'HIGH' || t.status === 'LOW';
                    const rangeStr =
                      t.reference_low !== null && t.reference_high !== null
                        ? `${t.reference_low} - ${t.reference_high}`
                        : '—';

                    return (
                      <tr key={t.id} className="hover:bg-gray-50/70 dark:hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-4 font-medium text-gray-900 dark:text-slate-100">
                          {t.test_name}
                        </td>
                        <td className={`py-3 px-4 font-bold ${isAbnormal ? 'text-rose-500 dark:text-rose-400' : 'text-gray-900 dark:text-slate-200'}`}>
                          {t.value}
                        </td>
                        <td className="py-3 px-4 text-gray-500 dark:text-slate-400 font-mono text-xs">
                          {t.unit || '—'}
                        </td>
                        <td className="py-3 px-4 text-gray-500 dark:text-slate-400 text-xs font-mono">
                          {rangeStr}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded-md text-xs font-bold tracking-wider ${
                              t.status === 'HIGH'
                                ? 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30'
                                : t.status === 'LOW'
                                ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                                : 'bg-teal-500/15 text-teal-600 dark:text-teal-400 border border-teal-500/30'
                            }`}
                          >
                            {t.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-500 dark:text-gray-400">
                      No test results found in the latest report.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Side: Results Distribution Donut Chart */}
        <div className="lg:col-span-5 xl:col-span-4 card p-6 bg-white/70 dark:bg-slate-900/80 backdrop-blur-lg border border-gray-200 dark:border-slate-800 shadow-xl rounded-2xl flex flex-col justify-between min-h-[460px]">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2 tracking-tight">
              Results Distribution
            </h2>
            <p className="text-xs text-gray-500 dark:text-slate-400">
              Overview of all biomarker classifications
            </p>
          </div>

          {/* Donut Chart with Center Text */}
          <div className="relative flex items-center justify-center my-6">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={72}
                  outerRadius={98}
                  paddingAngle={4}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    color: '#fff',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                  }}
                  itemStyle={{ color: '#fff' }}
                  formatter={(val: any) => [`${val} tests`, '']}
                />
              </PieChart>
            </ResponsiveContainer>

            {/* Total Count centered inside the donut hole */}
            <div className="absolute flex flex-col items-center justify-center pointer-events-none text-center">
              <span className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
                {totalTests}
              </span>
              <span className="text-xs font-semibold text-gray-400 dark:text-slate-400 uppercase tracking-widest mt-0.5">
                Total
              </span>
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-center space-x-6 pt-2">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-[#fb7185] inline-block shadow-sm"></span>
              <span className="text-xs font-medium text-gray-700 dark:text-slate-300">High</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-[#facc15] inline-block shadow-sm"></span>
              <span className="text-xs font-medium text-gray-700 dark:text-slate-300">Low</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-[#2dd4bf] inline-block shadow-sm"></span>
              <span className="text-xs font-medium text-gray-700 dark:text-slate-300">Normal</span>
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        <div className="card p-6 flex flex-col justify-between hover:border-primary-500/50 transition-all">
          <div>
            <div className="p-3 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-xl w-fit mb-4">
              <ArrowRightLeft className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Important Changes</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Compare your latest results with previous reports to spot shifts.
            </p>
          </div>
          <button onClick={() => navigate('/changes')} className="text-primary-600 dark:text-primary-400 hover:underline text-sm font-semibold flex items-center gap-1">
            Analyze Changes &rarr;
          </button>
        </div>

        <div className="card p-6 flex flex-col justify-between hover:border-primary-500/50 transition-all">
          <div>
            <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-xl w-fit mb-4">
              <Network className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Biomarker Patterns</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Explore AI-detected patterns across your organ systems & parameters.
            </p>
          </div>
          <button onClick={() => navigate('/patterns')} className="text-primary-600 dark:text-primary-400 hover:underline text-sm font-semibold flex items-center gap-1">
            View Pattern Alerts &rarr;
          </button>
        </div>
      </div>
    </div>
  );
};
