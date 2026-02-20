import React from 'react';
import type { BadgeProps } from './types';

const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral' }) => {
  const classes = {
    neutral: 'bg-slate-100 text-slate-600',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    error: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700'
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${classes[variant]}`}>
      {children}
    </span>
  );
};

export default Badge;
