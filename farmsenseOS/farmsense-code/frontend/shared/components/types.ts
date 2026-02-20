// Minimalist Component Types

export interface LoginProps {
  onLogin: (apiKey: string) => void;
  variant?: 'farmer' | 'admin' | 'investor' | 'regulatory' | 'grant' | 'research';
  demoCredentials?: { label: string; key: string }[];
}

export interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  alt?: boolean;
  loading?: boolean;
  className?: string;
}

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit';
  className?: string;
}

export interface InputProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  type?: 'text' | 'password' | 'email';
  placeholder?: string;
  error?: string;
  required?: boolean;
}

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'neutral' | 'success' | 'warning' | 'error' | 'info';
}

export interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'warning';
  label?: string;
  size?: 'sm' | 'md';
}

export interface MetricProps {
  label: string;
  value: string | number;
  unit?: string;
  change?: number;
}

export interface TelemetryData {
  deviceId: string;
  fieldId: string;
  timestamp: string;
  moisture: number;
  temperature: number;
  battery: number;
  signalStrength: number;
}

export interface NetworkStats {
  latencyMs: number;
  packetLossPct: number;
  quicConnections: number;
  fecOverheadPct: number;
  deltaRatio: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  apiKey: string | null;
  userRole: string | null;
  isLoading: boolean;
}
