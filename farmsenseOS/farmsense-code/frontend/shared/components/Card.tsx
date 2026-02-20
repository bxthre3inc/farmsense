import React from 'react';
import { Box, CardHeader, CardBody, LoadingOverlay } from './index';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  alt?: boolean;
  loading?: boolean;
  className?: string;
}

const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  alt = false,
  loading = false,
  className = '',
}) => {
  return (
    <Box
      border
      background={alt ? 'muted' : 'white'}
      padding="md"
      className={className}
    >
      <CardHeader title={title} subtitle={subtitle} />
      {loading ? (
        <LoadingOverlay />
      ) : (
        <CardBody>{children}</CardBody>
      )}
    </Box>
  );
};

export default Card;
