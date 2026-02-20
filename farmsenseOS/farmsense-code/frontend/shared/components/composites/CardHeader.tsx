import React from 'react';
import { Stack, Text } from '../primitives';

interface CardHeaderProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

const CardHeader: React.FC<CardHeaderProps> = ({ title, subtitle, action }) => {
  if (!title && !subtitle) return null;

  return (
    <div className="mb-4 pb-3 border-b border-slate-100">
      <Stack direction="horizontal" justify="between" align="center">
        <div>
          {title && (
            <Text as="h3" size="lg" weight="semibold">
              {title}
            </Text>
          )}
          {subtitle && (
            <Text size="sm" color="muted" className="mt-0.5">
              {subtitle}
            </Text>
          )}
        </div>
        {action}
      </Stack>
    </div>
  );
};

export default CardHeader;
