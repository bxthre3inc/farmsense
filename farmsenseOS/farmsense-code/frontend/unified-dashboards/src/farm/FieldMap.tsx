import React from 'react';
import { Layers, Crosshair } from 'lucide-react';
import { Field } from '../shared/types';

interface FieldMapProps {
  selectedField: Field;
  onFieldSelect: (field: Field) => void;
}

const mockFields: Field[] = [
  { id: 'field_01', name: 'North Quarter', acres: 45, crop: 'Corn', moisture: 32.4, temp: 28.5, health: 'optimal', lat: 40.7128, lon: -74.0060, lastIrrigation: '2h ago', nextIrrigation: 'Tomorrow 6AM' },
  { id: 'field_02', name: 'East Section', acres: 32, crop: 'Soybeans', moisture: 28.1, temp: 29.2, health: 'warning', lat: 40.7130, lon: -74.0050, lastIrrigation: '6h ago', nextIrrigation: 'Today 4PM' },
  { id: 'field_03', name: 'West Pasture', acres: 68, crop: 'Alfalfa', moisture: 35.2, temp: 27.8, health: 'optimal', lat: 40.7125, lon: -74.0070, lastIrrigation: '1d ago', nextIrrigation: 'In 2 days' },
];

const FieldMap: React.FC<FieldMapProps> = ({ selectedField, onFieldSelect }) => {
  return (
    <div className="h-[calc(100vh-180px)] bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden flex">
      {/* Map Area - Simulated */}
      <div className="flex-1 relative bg-slate-950">
        {/* Simulated Map Grid */}
        <div className="absolute inset-0 grid grid-cols-6 grid-rows-4 gap-1 p-4">
          {Array.from({ length: 24 }).map((_, i) => {
            const isField1 = i >= 0 && i < 8;
            const isField2 = i >= 8 && i < 14;
            const isField3 = i >= 14 && i < 24;
            let bgClass = 'bg-slate-800/30';
            if (isField1) bgClass = 'bg-emerald-500/20 border-2 border-emerald-500/40';
            if (isField2) bgClass = 'bg-amber-500/20 border-2 border-amber-500/40';
            if (isField3) bgClass = 'bg-emerald-500/20 border-2 border-emerald-500/40';
            
            return (
              <div
                key={i}
                className={`rounded-lg ${bgClass} flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity`}
              >
                {isField1 && i === 3 && <span className="text-emerald-400 text-xs font-bold">N</span>}
                {isField2 && i === 10 && <span className="text-amber-400 text-xs font-bold">E</span>}
                {isField3 && i === 18 && <span className="text-emerald-400 text-xs font-bold">W</span>}
              </div>
            );
          })}
        </div>

        {/* Map Controls */}
        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <button className="w-10 h-10 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700">
            <Layers className="w-5 h-5" />
          </button>
          <button className="w-10 h-10 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700">
            <Crosshair className="w-5 h-5" />
          </button>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-slate-800/90 backdrop-blur border border-slate-700 rounded-xl p-4">
          <h4 className="text-white font-bold text-sm mb-3">Field Status</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-emerald-500/40 border border-emerald-500 rounded" />
              <span className="text-slate-300 text-xs">Optimal</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-amber-500/40 border border-amber-500 rounded" />
              <span className="text-slate-300 text-xs">Attention Needed</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500/40 border border-red-500 rounded" />
              <span className="text-slate-300 text-xs">Critical</span>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className="w-80 bg-slate-900 border-l border-slate-800 p-4 overflow-y-auto">
        <h3 className="text-white font-bold mb-4">Field Details</h3>
        <div className="space-y-3">
          {mockFields.map((field) => (
            <button
              key={field.id}
              onClick={() => onFieldSelect(field)}
              className={`w-full text-left p-4 rounded-xl border transition-all ${
                selectedField.id === field.id
                  ? 'bg-emerald-500/10 border-emerald-500/50'
                  : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{field.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  field.health === 'optimal' ? 'bg-emerald-500/20 text-emerald-400' :
                  field.health === 'warning' ? 'bg-amber-500/20 text-amber-400' :
                  'bg-red-500/20 text-red-400'
                }`}>
                  {field.health}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-slate-500 text-xs">Crop</p>
                  <p className="text-slate-300">{field.crop}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Acres</p>
                  <p className="text-slate-300">{field.acres}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Moisture</p>
                  <p className="text-slate-300">{field.moisture}%</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Temp</p>
                  <p className="text-slate-300">{field.temp}°C</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FieldMap;
