import React from 'react';
import { Box, Stack, IconWrapper, MetricValue, MetricTrend } from './index';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  loading?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  change,
  icon,
  trend = 'neutral',
  loading = false,
}) => {
  return (
    <Box border background="white">
      <Stack direction="horizontal" justify="between" align="start">
        <IconWrapper size="md" variant="default">
          {icon}
        </IconWrapper>
        {change !== undefined && <MetricTrend value={change} direction={trend} />}
      </Stack>

      <div className="mt-4">
        <MetricValue
          value={value}
          unit={unit}
          label={title}
          loading={loading}
        />
      </div>
    </Box>
  );
};

export default MetricCard;
