// Just a standard component, nothing fancy here.

import React from 'react';
import type { Report } from '../../lib/types';

export const SummaryCards: React.FC<{ report: Report }> = ({ report }) => {
  // Define the configuration for the 4 cards
  const cards = [
    {
      label: 'Total Tests',
      value: report.total_tests,
      icon: (
        <svg className="w-7 h-7 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      ),
      bgClass: 'bg-primary-50 dark:bg-primary-900/20', // Blue tint
    },
    {
      label: 'Normal',
      value: report.normal_count,
      icon: (
        <svg className="w-7 h-7 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      bgClass: 'bg-emerald-100 dark:bg-emerald-900/40', // Green tint
    },
    {
      label: 'Low',
      value: report.low_count,
      icon: (
        <svg className="w-7 h-7 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13l-3 3m0 0l-3-3m3 3V8m0 13a9 9 0 110-18 9 9 0 010 18z" />
        </svg>
      ),
      bgClass: 'bg-amber-100 dark:bg-amber-900/40', // Yellow tint
    },
    {
      label: 'High',
      value: report.high_count,
      icon: (
        <svg className="w-7 h-7 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 11l3-3m0 0l3 3m-3-3v8m0-13a9 9 0 110 18 9 9 0 010-18z" />
        </svg>
      ),
      bgClass: 'bg-rose-100 dark:bg-rose-900/40', // Red tint
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => (
        <div key={idx} className="card-hover p-5 flex items-center transform transition-all duration-300 hover:scale-[1.02] hover:shadow-xl animate-fade-in" style={{ animationDelay: `${idx * 100}ms` }}>
          <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${card.bgClass} flex-shrink-0`}>
            {card.icon}
          </div>
          <div className="ml-4">
            <h4 className="text-3xl font-bold text-navy-700 dark:text-white leading-none mb-1">{card.value}</h4>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{card.label}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
