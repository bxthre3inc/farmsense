import React from 'react';

interface DividerProps {
  direction?: 'horizontal' | 'vertical';
  className?: string;
}

const Divider: React.FC<DividerProps> = ({
  direction = 'horizontal',
  className = '',
}) => {
  const classes =
    direction === 'horizontal'
      ? `w-full h-px bg-slate-200 ${className}`
      : `w-px h-full bg-slate-200 ${className}`;

  return <div className={classes} />;
};

export default Divider;
