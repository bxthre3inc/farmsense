import React from 'react';
import { ArrowDown, Battery, Wifi, HardDrive } from 'lucide-react';
import Card from './Card';
import type { CompressionStatsProps } from './types';

const CompressionStats: React.FC<CompressionStatsProps> = ({
  originalBytes,
  compressedBytes,
  ratio,
  deviceCount,
  batteryExtension,
}) => {
  const savingsPct = ((1 - 1 / ratio) * 100).toFixed(0);
  const originalGB = (originalBytes / 1e9).toFixed(1);
  const compressedGB = (compressedBytes / 1e9).toFixed(1);

  return (
    <Card
      title="Delta Compression Active"
      icon={<ArrowDown className="w-5 h-5 text-emerald-400" />}
      glass
      glow
    >
      <div className="space-y-6">
        {/* Main Ratio Display */}
        <div className="text-center py-4">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border-2 border-emerald-500/30">
            <div>
              <span className="text-3xl font-bold text-emerald-400">{ratio.toFixed(1)}</span>
              <span className="text-sm text-emerald-400/70">:1</span>
            </div>
          </div>
          <p className="text-emerald-400 font-medium mt-3">{savingsPct}% Data Reduction</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/5 rounded-xl p-3 text-center">
            <Wifi className="w-5 h-5 text-blue-400 mx-auto mb-2" />
            <p className="text-xs text-slate-400">Original</p>
            <p className="text-lg font-semibold text-white">{originalGB} GB</p>
          </div>

          <div className="bg-white/5 rounded-xl p-3 text-center">
            <HardDrive className="w-5 h-5 text-emerald-400 mx-auto mb-2" />
            <p className="text-xs text-slate-400">Compressed</p>
            <p className="text-lg font-semibold text-white">{compressedGB} GB</p>
          </div>

          <div className="bg-white/5 rounded-xl p-3 text-center">
            <Battery className="w-5 h-5 text-amber-400 mx-auto mb-2" />
            <p className="text-xs text-slate-400">Battery</p>
            <p className="text-lg font-semibold text-white">+{batteryExtension}%</p>
          </div>
        </div>

        {/* Device Count */}
        <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-xl p-4 border border-emerald-500/20">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-300">Optimized Devices</span>
            <span className="text-xl font-bold text-emerald-400">{deviceCount.toLocaleString()}</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            All LRZ nodes using delta encoding
          </p>
        </div>

        {/* Benefits List */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span className="text-slate-300">96% airtime reduction on 900MHz mesh</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span className="text-slate-300">Extended battery life to 12+ years</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span className="text-slate-300">70% reduction in storage requirements</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default CompressionStats;
