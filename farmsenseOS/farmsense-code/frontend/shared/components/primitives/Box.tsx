import React from 'react';

interface BoxProps {
  children: React.ReactNode;
  as?: keyof JSX.IntrinsicElements;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  border?: boolean;
  background?: 'white' | 'muted' | 'none';
}

const Box: React.FC<BoxProps> = ({
  children,
  as: Component = 'div',
  className = '',
  padding = 'md',
  border = false,
  background = 'white',
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  const backgroundClasses = {
    white: 'bg-white',
    muted: 'bg-slate-50',
    none: '',
  };

  const classes = [
    paddingClasses[padding],
    backgroundClasses[background],
    border && 'border border-slate-200 rounded-lg',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <Component className={classes}>{children}</Component>;
};

export default Box;
