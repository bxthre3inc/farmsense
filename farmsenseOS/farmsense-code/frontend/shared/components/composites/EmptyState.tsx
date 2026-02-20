import React from 'react';
import { Inbox } from 'lucide-react';
import { Stack, Text, IconWrapper, Button } from '../primitives';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No data available',
  description = 'There are no items to display at this time.',
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <IconWrapper size="lg" variant="muted" className="mb-4">
        <Inbox className="w-6 h-6" />
      </IconWrapper>
      <Text size="lg" weight="semibold" className="mb-1">
        {title}
      </Text>
      <Text size="sm" color="muted" className="mb-4 max-w-xs">
        {description}
      </Text>
      {actionLabel && onAction && (
        <Button variant="secondary" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
