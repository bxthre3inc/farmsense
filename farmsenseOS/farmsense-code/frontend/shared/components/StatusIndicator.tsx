import React from 'react';
import type { StatusIndicatorProps } from './types';

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  pulse = true,
  size = 'md',
}) => {
  const statusConfig = {
    online: { color: 'bg-emerald-500', label: 'Online' },
    offline: { color: 'bg-slate-500', label: 'Offline' },
    warning: { color: 'bg-amber-500', label: 'Warning' },
    error: { color: 'bg-red-500', label: 'Error' },
    busy: { color: 'bg-blue-500', label: 'Busy' },
  };

  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  const config = statusConfig[status];

  return (
    <div className="flex items-center gap-2">
      <span className="relative flex h-3 w-3">
        {pulse && status === 'online' && (
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.color} opacity-75`} />
        )}
        <span className={`relative inline-flex rounded-full ${sizeClasses[size]} ${config.color}`} />
      </span>
      {label && <span className="text-sm text-slate-300">{label}</span>}
      {!label && <span className="text-sm text-slate-300">{config.label}</span>}
    </div>
  );
};

export default StatusIndicator;
