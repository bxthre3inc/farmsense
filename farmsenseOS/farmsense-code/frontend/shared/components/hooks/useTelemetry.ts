import { useState, useEffect, useCallback } from 'react';
import type { TelemetryData } from '../types';

interface UseTelemetryOptions {
  fieldId?: string;
  deviceId?: string;
  refreshInterval?: number;
  limit?: number;
}

export const useTelemetry = (options: UseTelemetryOptions = {}) => {
  const { fieldId, deviceId, refreshInterval = 30000, limit = 100 } = options;
  
  const [data, setData] = useState<TelemetryData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (fieldId) params.append('field_id', fieldId);
      if (deviceId) params.append('device_id', deviceId);
      params.append('limit', limit.toString());

      const response = await fetch(`/api/v1/sensors/readings?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch telemetry');
      
      // Use mock data for development
      setData([
        {
          deviceId: 'LRZ-001',
          fieldId: fieldId || 'field_01',
          timestamp: new Date().toISOString(),
          moistureSurface: 0.32,
          moistureRoot: 0.28,
          temperature: 24.5,
          batteryVoltage: 3.45,
          signalStrength: 85,
          qualityFlag: 'valid',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [fieldId, deviceId, limit]);

  useEffect(() => {
    fetchData();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchData, refreshInterval]);

  const refresh = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    lastUpdated,
    refresh,
  };
};
