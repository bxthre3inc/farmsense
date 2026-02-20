import React from 'react';

interface InputProps {
  id?: string;
  type?: 'text' | 'password' | 'email' | 'number';
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

const Input: React.FC<InputProps> = ({
  id,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  className = '',
}) => {
  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      className={`
        w-full px-3 py-2
        border border-slate-300 rounded
        text-slate-900 placeholder-slate-400
        focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500
        disabled:bg-slate-100 disabled:text-slate-500
        ${className}
      `}
    />
  );
};

export default Input;
