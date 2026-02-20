import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { IconWrapper, Text } from '../primitives';

interface MetricTrendProps {
  value: number;
  direction: 'up' | 'down' | 'neutral';
}

const MetricTrend: React.FC<MetricTrendProps> = ({ value, direction }) => {
  const config = {
    up: {
      icon: TrendingUp,
      variant: 'success' as const,
      prefix: '+',
    },
    down: {
      icon: TrendingDown,
      variant: 'error' as const,
      prefix: '',
    },
    neutral: {
      icon: Minus,
      variant: 'muted' as const,
      prefix: '',
    },
  };

  const { icon: Icon, variant, prefix } = config[direction];

  return (
    <div className="flex items-center gap-1">
      <IconWrapper size="sm" variant={variant}>
        <Icon className="w-3 h-3" />
      </IconWrapper>
      <Text size="sm" weight="medium" className={
        direction === 'up' ? 'text-green-600' : 
        direction === 'down' ? 'text-red-600' : 
        'text-slate-500'
      }>
        {prefix}{value}%
      </Text>
    </div>
  );
};

export default MetricTrend;
