import React from 'react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'emerald' | 'slate' | 'white';
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'emerald',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const colorClasses = {
    emerald: 'border-emerald-500',
    slate: 'border-slate-500',
    white: 'border-white',
  };

  return (
    <div
      className={`
        ${sizeClasses[size]}
        border-2 border-slate-200 ${colorClasses[color]} border-t-transparent
        rounded-full animate-spin
        ${className}
      `}
    />
  );
};

export default Spinner;
