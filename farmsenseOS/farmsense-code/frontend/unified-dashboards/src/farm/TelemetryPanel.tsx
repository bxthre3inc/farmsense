import React, { useState, useEffect } from 'react';
import { Droplets, Clock, Play, Pause, Calendar } from 'lucide-react';

interface Field {
  id: string;
  name: string;
  nextIrrigation: string;
}

interface TelemetryPanelProps {
  field: Field;
}

interface ScheduleItem {
  id: string;
  field: string;
  time: string;
  duration: string;
  volume: string;
  status: 'scheduled' | 'in_progress' | 'completed';
}

const mockSchedule: ScheduleItem[] = [
  { id: '1', field: 'East Section', time: 'Today 4:00 PM', duration: '45 min', volume: '2,400 gal', status: 'scheduled' },
  { id: '2', field: 'North Quarter', time: 'Tomorrow 6:00 AM', duration: '60 min', volume: '3,200 gal', status: 'scheduled' },
  { id: '3', field: 'West Pasture', time: 'Wed 7:00 AM', duration: '90 min', volume: '4,800 gal', status: 'scheduled' },
];

const TelemetryPanel: React.FC<TelemetryPanelProps> = ({ field }) => {
  const [activeZone, setActiveZone] = useState<string | null>(null);
  const [moistureData, setMoistureData] = useState<number[]>([30, 32, 31, 33, 32, 34, 32]);

  useEffect(() => {
    const interval = setInterval(() => {
      setMoistureData(prev => [...prev.slice(1), 30 + Math.random() * 5]);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStartIrrigation = (zoneId: string) => {
    setActiveZone(zoneId);
    setTimeout(() => setActiveZone(null), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Current Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center">
              <Droplets className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-slate-400 text-sm">Next Irrigation</p>
              <p className="text-white font-bold">{field.nextIrrigation}</p>
            </div>
          </div>
          <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2">
            <Play className="w-4 h-4" />
            Start Now
          </button>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-emerald-500/20 rounded-xl flex items-center justify-center">
              <Clock className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-slate-400 text-sm">System Status</p>
              <p className="text-white font-bold">Standby</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-emerald-400">All pumps operational</span>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-purple-500/20 rounded-xl flex items-center justify-center">
              <Calendar className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-slate-400 text-sm">This Week</p>
              <p className="text-white font-bold">3 Scheduled</p>
            </div>
          </div>
          <p className="text-slate-500 text-sm">Est. 10,400 gallons</p>
        </div>
      </div>

      {/* Zone Controls */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <h3 className="text-white font-bold mb-4">Zone Controls</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {['Zone A', 'Zone B', 'Zone C', 'Zone D'].map((zone, idx) => (
            <div key={zone} className="bg-slate-900 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-white font-medium">{zone}</span>
                <span className={`w-2 h-2 rounded-full ${idx % 2 === 0 ? 'bg-emerald-500' : 'bg-slate-600'}`} />
              </div>
              <p className="text-slate-400 text-xs mb-3">{idx % 2 === 0 ? 'Active' : 'Idle'}</p>
              <button
                onClick={() => handleStartIrrigation(zone)}
                disabled={activeZone === zone}
                className={`w-full py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeZone === zone
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {activeZone === zone ? 'Running...' : 'Start'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Schedule */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <h3 className="text-white font-bold">Irrigation Schedule</h3>
          <button className="text-emerald-400 text-sm hover:text-emerald-300">View Calendar</button>
        </div>
        <div className="divide-y divide-slate-700">
          {mockSchedule.map((item) => (
            <div key={item.id} className="p-4 flex items-center justify-between hover:bg-slate-700/30 transition-colors">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  item.status === 'in_progress' ? 'bg-emerald-500/20' : 'bg-slate-700'
                }`}>
                  {item.status === 'in_progress' ? (
                    <Pause className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <Play className="w-5 h-5 text-slate-400" />
                  )}
                </div>
                <div>
                  <p className="text-white font-medium">{item.field}</p>
                  <p className="text-slate-400 text-sm">{item.time} • {item.duration}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-white font-medium">{item.volume}</p>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  item.status === 'scheduled' ? 'bg-blue-500/20 text-blue-400' :
                  item.status === 'in_progress' ? 'bg-emerald-500/20 text-emerald-400' :
                  'bg-slate-600/50 text-slate-400'
                }`}>
                  {item.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Moisture Chart (Simple visualization) */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
        <h3 className="text-white font-bold mb-4">7-Day Moisture Trend</h3>
        <div className="flex items-end gap-2 h-32">
          {moistureData.map((val, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-blue-500/60 rounded-t"
                style={{ height: `${(val / 40) * 100}%` }}
              />
              <span className="text-xs text-slate-500">{['M', 'T', 'W', 'T', 'F', 'S', 'S'][i]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TelemetryPanel;
