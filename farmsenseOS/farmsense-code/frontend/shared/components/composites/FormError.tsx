import React from 'react';
import { Text } from '../primitives';

interface FormErrorProps {
  message: string;
}

const FormError: React.FC<FormErrorProps> = ({ message }) => {
  return (
    <Text size="sm" color="error" className="mt-1">
      {message}
    </Text>
  );
};

export default FormError;
