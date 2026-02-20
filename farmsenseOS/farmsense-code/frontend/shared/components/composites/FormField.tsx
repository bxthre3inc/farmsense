import React from 'react';
import { Label, Input, Stack, Text } from '../primitives';

interface FormFieldProps {
  id: string;
  label: string;
  type?: 'text' | 'password' | 'email' | 'number';
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
  required?: boolean;
}

const FormField: React.FC<FormFieldProps> = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  error,
  required = false,
}) => {
  return (
    <Stack gap="sm">
      <Label htmlFor={id}>
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      <Input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
      />
      {error && (
        <Text size="sm" color="error">
          {error}
        </Text>
      )}
    </Stack>
  );
};

export default FormField;
