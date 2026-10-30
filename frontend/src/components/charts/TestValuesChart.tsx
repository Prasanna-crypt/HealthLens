// Just a standard component, nothing fancy here.

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { TestResult } from '../../lib/types';

export const TestValuesChart: React.FC<{ results: TestResult[] }> = ({ results }) => {
  // Only include tests that have numerical values and reference ranges.
  // We slice(0, 10) so the chart doesn't get squished if there are 50 tests.
  const data = results
    .filter(r => r.reference_low !== null && r.reference_high !== null && typeof r.value === 'number')
    .slice(0, 10);

  // Custom hover tooltip showing test name, value, and expected range
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700">
          <p className="font-semibold text-navy-700 dark:text-white mb-1">{data.test_name}</p>
          <p className="text-sm">
            Value: <span className="font-bold">{data.value}</span> {data.unit}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Range: {data.reference_low} - {data.reference_high}
          </p>
        </div>
      );
    }
    return null;
  };

  const getColor = (status: string) => {
    switch (status) {
      case 'LOW': return '#FCD34D'; // Soft amber
      case 'HIGH': return '#FDA4AF'; // Soft coral
      default: return '#66D1CF'; // Soft teal
    }
  };

  return (
    <div className="card p-6 w-full">
      <h3 className="text-lg font-semibold text-navy-700 dark:text-white mb-6">Test Values Overview (Sample)</h3>
      <div className="h-72 w-full">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            {/* margin handles spacing so labels aren't cut off */}
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
              {/* XAxis labels are angled (-45 deg) to prevent overlapping */}
              <XAxis dataKey="test_name" tick={{ fontSize: 10 }} tickFormatter={(val) => val.length > 10 ? val.substring(0, 10) + '...' : val} angle={-45} textAnchor="end" height={60} stroke="#9ca3af" />
              <YAxis tick={{ fontSize: 10 }} stroke="#9ca3af" />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(156, 163, 175, 0.1)' }} />
              
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {/* Color each individual bar */}
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getColor(entry.status)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            No suitable numerical data to chart.
          </div>
        )}
      </div>
    </div>
  );
};
