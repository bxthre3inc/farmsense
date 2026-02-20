const API_BASE = import.meta.env.VITE_API_URL || 'https://farmsense-backend-getfarmsense.zocomputer.io';

const getHeaders = () => {
  const apiKey = localStorage.getItem('farmsense_api_key');
  return {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey || '',
  };
};

export const api = {
  get: async (endpoint: string) => {
    const res = await fetch(`${API_BASE}${endpoint}`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  },
  
  post: async (endpoint: string, data: any) => {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  },
};

export const getApiKey = () => localStorage.getItem('farmsense_api_key');
export const setApiKey = (key: string) => localStorage.setItem('farmsense_api_key', key);
export const removeApiKey = () => localStorage.removeItem('farmsense_api_key');

export type UserRole = 'FARMER' | 'ADMIN' | 'INVESTOR' | 'REVIEWER' | 'AUDITOR' | 'RESEARCHER' | 'PARTNER';
export type SubscriptionTier = 'FREE' | 'BASIC' | 'PRO' | 'ENTERPRISE';

export interface User {
  id: string;
  email: string;
  name?: string;
  role: UserRole;
  tier: SubscriptionTier;
  organization?: string;
}
