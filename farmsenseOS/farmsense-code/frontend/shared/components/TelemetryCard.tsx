import React from 'react';
import { Droplets, Thermometer, Battery, Activity } from 'lucide-react';
import Card from './Card';
import Badge from './Badge';
import StatusIndicator from './StatusIndicator';
import type { TelemetryData } from './types';

interface TelemetryCardProps {
  data: TelemetryData;
  showDeviceId?: boolean;
}

const TelemetryCard: React.FC<TelemetryCardProps> = ({ data, showDeviceId = true }) => {
  const getQualityBadge = (flag: string) => {
    switch (flag) {
      case 'valid':
        return <Badge variant="success">Valid</Badge>;
      case 'suspect':
        return <Badge variant="warning">Suspect</Badge>;
      case 'invalid':
        return <Badge variant="error">Invalid</Badge>;
      default:
        return <Badge variant="neutral">Unknown</Badge>;
    }
  };

  const getBatteryStatus = (voltage?: number) => {
    if (!voltage) return 'unknown';
    if (voltage > 3.4) return 'online';
    if (voltage > 3.2) return 'warning';
    return 'error';
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card glass className="hover:bg-white/10 transition-all">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          {showDeviceId && (
            <div>
              <p className="text-xs text-slate-500">Device</p>
              <p className="text-sm font-medium text-white font-mono">{data.deviceId}</p>
            </div>
          )}
          <div className="flex items-center gap-2">
            {getQualityBadge(data.qualityFlag)}
            <span className="text-xs text-slate-500">{formatTime(data.timestamp)}</span>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white/5 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Droplets className="w-4 h-4 text-blue-400" />
              <span className="text-xs">Surface Moisture</span>
            </div>
            <p className="text-lg font-semibold text-white">
              {(data.moistureSurface * 100).toFixed(1)}%
            </p>
          </div>

          <div className="bg-white/5 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Droplets className="w-4 h-4 text-cyan-400" />
              <span className="text-xs">Root Moisture</span>
            </div>
            <p className="text-lg font-semibold text-white">
              {(data.moistureRoot * 100).toFixed(1)}%
            </p>
          </div>

          <div className="bg-white/5 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Thermometer className="w-4 h-4 text-amber-400" />
              <span className="text-xs">Temperature</span>
            </div>
            <p className="text-lg font-semibold text-white">
              {data.temperature.toFixed(1)}°C
            </p>
          </div>

          <div className="bg-white/5 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Battery className="w-4 h-4 text-emerald-400" />
              <span className="text-xs">Battery</span>
            </div>
            <div className="flex items-center gap-2">
              <p className="text-lg font-semibold text-white">
                {data.batteryVoltage ? `${data.batteryVoltage.toFixed(2)}V` : '—'}
              </p>
              {data.batteryVoltage && (
                <StatusIndicator
                  status={getBatteryStatus(data.batteryVoltage) as any}
                  size="sm"
                  pulse={false}
                />
              )}
            </div>
          </div>
        </div>

        {/* Signal Strength */}
        {data.signalStrength !== undefined && (
          <div className="flex items-center gap-2 text-sm">
            <Activity className="w-4 h-4 text-slate-400" />
            <span className="text-slate-400">Signal:</span>
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  data.signalStrength > 70
                    ? 'bg-emerald-500'
                    : data.signalStrength > 40
                    ? 'bg-amber-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${data.signalStrength}%` }}
              />
            </div>
            <span className="text-white font-medium">{data.signalStrength}%</span>
          </div>
        )}
      </div>
    </Card>
  );
};

export default TelemetryCard;
