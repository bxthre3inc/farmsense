import React from 'react';

interface IconWrapperProps {
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'muted' | 'primary' | 'success' | 'warning' | 'error';
  className?: string;
}

const IconWrapper: React.FC<IconWrapperProps> = ({
  children,
  size = 'md',
  variant = 'default',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3',
  };

  const variantClasses = {
    default: 'bg-slate-100 text-slate-600',
    muted: 'bg-slate-50 text-slate-400',
    primary: 'bg-emerald-100 text-emerald-600',
    success: 'bg-green-100 text-green-600',
    warning: 'bg-yellow-100 text-yellow-600',
    error: 'bg-red-100 text-red-600',
  };

  return (
    <div
      className={`
        inline-flex items-center justify-center rounded
        ${sizeClasses[size]} ${variantClasses[variant]}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

export default IconWrapper;
