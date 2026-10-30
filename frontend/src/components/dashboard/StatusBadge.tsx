import React from 'react';

export const StatusBadge: React.FC<{ status: 'NORMAL' | 'LOW' | 'HIGH' | 'UNKNOWN' }> = ({ status }) => {
  const styles = {
    NORMAL: 'badge-normal',
    LOW: 'badge-low',
    HIGH: 'badge-high',
    UNKNOWN: 'badge-unknown'
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${styles[status]}`}>
      {status}
    </span>
  );
};
