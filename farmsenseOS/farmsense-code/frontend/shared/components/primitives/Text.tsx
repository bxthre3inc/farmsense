import React from 'react';

interface TextProps {
  children: React.ReactNode;
  as?: 'p' | 'span' | 'h1' | 'h2' | 'h3' | 'h4' | 'label';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  weight?: 'normal' | 'medium' | 'semibold' | 'bold';
  color?: 'default' | 'muted' | 'primary' | 'error';
  className?: string;
}

const Text: React.FC<TextProps> = ({
  children,
  as: Component = 'p',
  size = 'md',
  weight = 'normal',
  color = 'default',
  className = '',
}) => {
  const sizeClasses = {
    xs: 'text-xs',
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
    '2xl': 'text-2xl',
  };

  const weightClasses = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  };

  const colorClasses = {
    default: 'text-slate-900',
    muted: 'text-slate-500',
    primary: 'text-emerald-600',
    error: 'text-red-600',
  };

  const classes = [
    sizeClasses[size],
    weightClasses[weight],
    colorClasses[color],
    className,
  ].join(' ');

  return <Component className={classes}>{children}</Component>;
};

export default Text;
