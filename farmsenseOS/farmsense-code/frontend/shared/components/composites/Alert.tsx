import React from 'react';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';
import { Stack, Text, IconWrapper } from '../primitives';

interface AlertProps {
  children: React.ReactNode;
  variant?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
}

const Alert: React.FC<AlertProps> = ({
  children,
  variant = 'info',
  title,
}) => {
  const config = {
    success: {
      icon: CheckCircle,
      iconVariant: 'success' as const,
      borderClass: 'border-green-200 bg-green-50',
    },
    error: {
      icon: AlertCircle,
      iconVariant: 'error' as const,
      borderClass: 'border-red-200 bg-red-50',
    },
    warning: {
      icon: AlertCircle,
      iconVariant: 'warning' as const,
      borderClass: 'border-yellow-200 bg-yellow-50',
    },
    info: {
      icon: Info,
      iconVariant: 'primary' as const,
      borderClass: 'border-blue-200 bg-blue-50',
    },
  };

  const { icon: Icon, iconVariant, borderClass } = config[variant];

  return (
    <div className={`border rounded-lg p-4 ${borderClass}`}>
      <Stack direction="horizontal" gap="md" align="start">
        <IconWrapper size="sm" variant={iconVariant}>
          <Icon className="w-4 h-4" />
        </IconWrapper>
        <div className="flex-1">
          {title && (
            <Text weight="semibold" className="mb-1">
              {title}
            </Text>
          )}
          <Text size="sm" color="default">
            {children}
          </Text>
        </div>
      </Stack>
    </div>
  );
};

export default Alert;
