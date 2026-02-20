import React, { useState } from 'react';
import {
  Box,
  Stack,
  Text,
  Button,
  FormField,
  FormError,
  Divider,
} from './index';

interface LoginProps {
  onLogin: (apiKey: string) => void;
  variant?: 'farmer' | 'admin' | 'investor' | 'regulatory' | 'grant' | 'research';
  demoCredentials?: { label: string; key: string }[];
}

const Login: React.FC<LoginProps> = ({
  onLogin,
  variant = 'farmer',
  demoCredentials,
}) => {
  const [key, setKey] = useState('');
  const [error, setError] = useState('');

  const config = {
    farmer: { title: 'FarmSense', subtitle: 'Farmer Dashboard' },
    admin: { title: 'FarmSense', subtitle: 'Admin Control' },
    investor: { title: 'FarmSense', subtitle: 'Investor Portal' },
    regulatory: { title: 'FarmSense', subtitle: 'Regulatory Portal' },
    grant: { title: 'FarmSense', subtitle: 'Grant Portal' },
    research: { title: 'FarmSense', subtitle: 'Research Portal' },
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (key.trim().length < 5) {
      setError('Please enter a valid API key');
      return;
    }
    onLogin(key.trim());
  };

  const { title, subtitle } = config[variant];

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <Stack gap="lg" className="w-full max-w-md">
        {/* Header */}
        <div className="text-center">
          <Text as="h1" size="2xl" weight="bold">
            {title}
          </Text>
          <Text color="muted">{subtitle}</Text>
        </div>

        {/* Form Card */}
        <Box border background="white">
          <form onSubmit={handleSubmit}>
            <Stack gap="md">
              <FormField
                id="api-key"
                label="API Key"
                type="password"
                value={key}
                onChange={setKey}
                placeholder="Enter your API key"
                error={error}
                required
              />

              <Button type="submit" variant="primary" className="w-full">
                Sign In
              </Button>
            </Stack>
          </form>
        </Box>

        {/* Demo Credentials */}
        {demoCredentials && (
          <div className="text-center">
            <Text size="xs" color="muted" className="uppercase tracking-wide">
              Demo Credentials
            </Text>
            <Stack gap="xs" className="mt-2">
              {demoCredentials.map((cred) => (
                <code
                  key={cred.key}
                  className="text-sm text-slate-500 font-mono"
                >
                  {cred.label}: {cred.key}
                </code>
              ))}
            </Stack>
          </div>
        )}
      </Stack>
    </div>
  );
};

export default Login;
