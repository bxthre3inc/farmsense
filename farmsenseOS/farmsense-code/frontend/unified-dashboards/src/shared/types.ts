export type FieldHealth = 'optimal' | 'warning' | 'critical';

export interface Field {
  id: string;
  name: string;
  acres: number;
  crop: string;
  moisture: number;
  temp: number;
  health: FieldHealth;
  lat: number;
  lon: number;
  lastIrrigation: string;
  nextIrrigation: string;
}

export type UserRole = 'farmer' | 'admin' | 'investor' | 'grant_reviewer' | 'partner' | 'auditor' | 'regulator';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  organization?: string;
}

export interface MetricCard {
  label: string;
  value: string;
  trend?: string;
  status: 'good' | 'warning' | 'critical';
}

export interface ComplianceReport {
  id: string;
  fieldId: string;
  fieldName: string;
  status: 'compliant' | 'violation' | 'pending';
  date: string;
  waterUsed: number;
  efficiency: number;
}
