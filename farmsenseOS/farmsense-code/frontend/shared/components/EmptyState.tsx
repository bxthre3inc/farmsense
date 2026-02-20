import React from 'react';
import { Search, FileX, Inbox } from 'lucide-react';
import Button from './Button';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: 'search' | 'file' | 'inbox' | React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No data found',
  description = 'There is no data to display at this time.',
  icon = 'inbox',
  actionLabel,
  onAction,
}) => {
  const iconMap = {
    search: Search,
    file: FileX,
    inbox: Inbox,
  };

  const IconComponent = typeof icon === 'string' ? iconMap[icon] : null;

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mb-4">
        {IconComponent ? (
          <IconComponent className="w-8 h-8 text-slate-400" />
        ) : (
          icon
        )}
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-400 max-w-sm mb-6">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="secondary">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
