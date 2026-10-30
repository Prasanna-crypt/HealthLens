// Just a standard component, nothing fancy here.

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import type { Report } from '../../lib/types';

export const NormalVsAbnormalChart: React.FC<{ report: Report }> = ({ report }) => {
  // Format data for the pie chart. We filter out any categories that have 0 tests.
  const data = [
    { name: 'Normal', value: report.normal_count, color: '#66D1CF' }, // Soft teal
    { name: 'Low', value: report.low_count, color: '#FCD34D' },      // Soft amber
    { name: 'High', value: report.high_count, color: '#FDA4AF' },    // Soft coral
  ].filter(d => d.value > 0);

  // Custom component that shows up when hovering over a pie slice
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700">
          <p className="font-semibold text-navy-700 dark:text-white" style={{ color: payload[0].payload.color }}>
            {payload[0].name}: {payload[0].value} tests
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold text-navy-700 dark:text-white mb-4">Results Distribution</h3>
      <div className="flex-1 relative min-h-[250px]">
        {data.length > 0 ? (
          // ResponsiveContainer makes the chart scale to fit its parent div
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                innerRadius={60} // Makes it a donut chart instead of full pie
                outerRadius={90}
                paddingAngle={5} // Space between slices
                dataKey="value"
                stroke="none"
              >
                {/* Apply our custom colors to each slice */}
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="bottom" height={36} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No data
          </div>
        )}
        
        {/* Large total number positioned right in the center of the donut hole */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none pb-8">
          <div className="text-center">
            <p className="text-3xl font-bold text-navy-700 dark:text-white">{report.total_tests}</p>
            <p className="text-xs text-gray-500 font-medium">Total</p>
          </div>
        </div>
      </div>
    </div>
  );
};
