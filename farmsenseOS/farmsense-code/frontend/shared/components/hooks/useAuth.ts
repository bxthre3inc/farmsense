import { useState, useEffect, useCallback } from 'react';

interface AuthState {
  isAuthenticated: boolean;
  apiKey: string | null;
  userRole: string | null;
  isLoading: boolean;
}

export const useAuth = () => {
  const [auth, setAuth] = useState<AuthState>({
    isAuthenticated: false,
    apiKey: null,
    userRole: null,
    isLoading: true,
  });

  useEffect(() => {
    // Check for stored API key
    const storedKey = localStorage.getItem('farmsense_api_key');
    const storedRole = localStorage.getItem('farmsense_user_role');
    
    if (storedKey) {
      setAuth({
        isAuthenticated: true,
        apiKey: storedKey,
        userRole: storedRole,
        isLoading: false,
      });
    } else {
      setAuth(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  const login = useCallback((apiKey: string, role?: string) => {
    localStorage.setItem('farmsense_api_key', apiKey);
    if (role) {
      localStorage.setItem('farmsense_user_role', role);
    }
    setAuth({
      isAuthenticated: true,
      apiKey,
      userRole: role || null,
      isLoading: false,
    });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('farmsense_api_key');
    localStorage.removeItem('farmsense_user_role');
    setAuth({
      isAuthenticated: false,
      apiKey: null,
      userRole: null,
      isLoading: false,
    });
  }, []);

  const getAuthHeaders = useCallback(() => {
    if (!auth.apiKey) return {};
    return {
      'Authorization': `Bearer ${auth.apiKey}`,
      'Content-Type': 'application/json',
    };
  }, [auth.apiKey]);

  return {
    ...auth,
    login,
    logout,
    getAuthHeaders,
  };
};
