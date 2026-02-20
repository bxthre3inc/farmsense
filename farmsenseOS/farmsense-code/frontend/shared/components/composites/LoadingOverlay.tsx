import React from 'react';
import { Spinner, Text, Stack } from '../primitives';

interface LoadingOverlayProps {
  message?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = 'Loading...',
}) => {
  return (
    <div className="flex items-center justify-center py-12">
      <Stack direction="horizontal" gap="sm" align="center">
        <Spinner size="md" />
        <Text color="muted">{message}</Text>
      </Stack>
    </div>
  );
};

export default LoadingOverlay;
