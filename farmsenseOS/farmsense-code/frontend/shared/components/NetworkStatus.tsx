import React, { useEffect, useState } from 'react';
import { Wifi, Activity, Zap, Database, Server } from 'lucide-react';
import Card from './Card';
import Badge from './Badge';
import type { NetworkStats } from './types';

interface NetworkStatusProps {
  stats?: NetworkStats;
  refreshInterval?: number;
  showDetails?: boolean;
}

const NetworkStatus: React.FC<NetworkStatusProps> = ({
  stats: initialStats,
  refreshInterval = 5000,
  showDetails = true,
}) => {
  const [stats, setStats] = useState<NetworkStats>(initialStats || {
    latencyMs: 0,
    packetLossPct: 0,
    bandwidthKbps: 0,
    compressionRatio: 1,
    activeConnections: 0,
    lastUpdated: new Date().toISOString(),
  });

  useEffect(() => {
    if (initialStats) return;

    // Simulate fetching network stats
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/v1/edge/network-stats');
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        // Use mock data if API not available
        setStats({
          latencyMs: Math.random() * 100 + 20,
          packetLossPct: Math.random() * 2,
          bandwidthKbps: Math.random() * 500 + 100,
          compressionRatio: 4.2,
          activeConnections: 15600,
          lastUpdated: new Date().toISOString(),
        });
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, refreshInterval);
    return () => clearInterval(interval);
  }, [initialStats, refreshInterval]);

  const getNetworkQuality = () => {
    if (stats.latencyMs < 50 && stats.packetLossPct < 0.1) return { label: 'Excellent', variant: 'success' as const };
    if (stats.latencyMs < 100 && stats.packetLossPct < 1) return { label: 'Good', variant: 'success' as const };
    if (stats.latencyMs < 300 && stats.packetLossPct < 5) return { label: 'Fair', variant: 'warning' as const };
    return { label: 'Poor', variant: 'error' as const };
  };

  const quality = getNetworkQuality();

  return (
    <Card title="Network Status" icon={<Wifi className="w-5 h-5 text-blue-400" />} glass>
      <div className="space-y-4">
        {/* Quality Badge */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">Network Quality</span>
          <Badge variant={quality.variant}>{quality.label}</Badge>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/5 rounded-xl p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Activity className="w-4 h-4" />
              <span className="text-xs">Latency</span>
            </div>
            <span className="text-xl font-semibold text-white">{stats.latencyMs.toFixed(1)}ms</span>
          </div>

          <div className="bg-white/5 rounded-xl p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Zap className="w-4 h-4" />
              <span className="text-xs">Bandwidth</span>
            </div>
            <span className="text-xl font-semibold text-white">{(stats.bandwidthKbps / 1000).toFixed(1)} Mbps</span>
          </div>

          <div className="bg-white/5 rounded-xl p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Database className="w-4 h-4" />
              <span className="text-xs">Compression</span>
            </div>
            <span className="text-xl font-semibold text-emerald-400">{stats.compressionRatio.toFixed(1)}:1</span>
          </div>

          <div className="bg-white/5 rounded-xl p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Server className="w-4 h-4" />
              <span className="text-xs">Active Devices</span>
            </div>
            <span className="text-xl font-semibold text-white">{stats.activeConnections.toLocaleString()}</span>
          </div>
        </div>

        {/* Details */}
        {showDetails && (
          <div className="pt-4 border-t border-white/10">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Packet Loss</span>
                <span className={stats.packetLossPct > 1 ? 'text-amber-400' : 'text-emerald-400'}>
                  {stats.packetLossPct.toFixed(2)}%
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full transition-all ${stats.packetLossPct > 1 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                  style={{ width: `${Math.min(stats.packetLossPct * 10, 100)}%` }}
                />
              </div>
            </div>

            <p className="text-xs text-slate-500 mt-4">
              Last updated: {new Date(stats.lastUpdated).toLocaleTimeString()}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default NetworkStatus;
