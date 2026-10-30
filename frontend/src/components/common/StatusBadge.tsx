import React from 'react';

export type StatusType = 
  | 'Normal'
  | 'Borderline / Near Reference Limit'
  | 'Outside Reference Range'
  | 'Unknown'
  | string;

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  let colorClass = 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'; // Default / Unknown

  if (!status) {
    status = 'Unknown';
  }

  const s = status.toLowerCase();
  
  if (s === 'normal') {
    colorClass = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800/30';
  } else if (s.includes('borderline') || s.includes('near')) {
    colorClass = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800/30';
  } else if (s.includes('outside') || s.includes('high') || s.includes('low') || s.includes('abnormal')) {
    colorClass = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800/30';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass} ${className}`}>
      {status}
    </span>
  );
};
