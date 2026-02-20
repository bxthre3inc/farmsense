import React from 'react';
import { Stack, Text } from '../primitives';

interface MetricValueProps {
  value: string | number;
  unit?: string;
  label: string;
  loading?: boolean;
}

const MetricValue: React.FC<MetricValueProps> = ({
  value,
  unit,
  label,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="w-6 h-6 border-2 border-slate-200 border-t-emerald-500 rounded-full animate-spin" />
    );
  }

  return (
    <Stack gap="sm">
      <div className="flex items-baseline gap-1">
        <Text as="span" size="2xl" weight="bold" className="text-slate-900">
          {value}
        </Text>
        {unit && (
          <Text size="sm" color="muted">
            {unit}
          </Text>
        )}
      </div>
      <Text size="sm" color="muted">
        {label}
      </Text>
    </Stack>
  );
};

export default MetricValue;
