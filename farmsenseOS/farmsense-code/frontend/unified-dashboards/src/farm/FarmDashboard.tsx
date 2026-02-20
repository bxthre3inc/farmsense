import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Map as MapIcon,
  Droplets,
  Thermometer,
  CloudRain,
  Settings,
  Bell,
  LogOut,
  Sprout,
  Wind,
  Sun,
  Activity,
  AlertTriangle,
  CheckCircle,
  Mic,
  X,
  Menu,
  TrendingUp,
  Droplet
} from 'lucide-react';
import { getApiKey, removeApiKey } from '../shared/api';
import { Field } from '../shared/types';
import Login from './Login';
import FieldMap from './FieldMap';
import TelemetryPanel from './TelemetryPanel';

const mockFields: Field[] = [
  { id: 'field_01', name: 'North Quarter', acres: 45, crop: 'Corn', moisture: 32.4, temp: 28.5, health: 'optimal', lastIrrigation: '2h ago', nextIrrigation: 'Tomorrow 6AM', lat: 40.7128, lon: -74.0060 },
  { id: 'field_02', name: 'East Section', acres: 32, crop: 'Soybeans', moisture: 28.1, temp: 29.2, health: 'warning', lastIrrigation: '6h ago', nextIrrigation: 'Today 4PM', lat: 40.7130, lon: -74.0050 },
  { id: 'field_03', name: 'West Pasture', acres: 68, crop: 'Alfalfa', moisture: 35.2, temp: 27.8, health: 'optimal', lastIrrigation: '1d ago', nextIrrigation: 'In 2 days', lat: 40.7125, lon: -74.0070 },
];

const FarmDashboard: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedField, setSelectedField] = useState<Field>(mockFields[0]);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [agentResponse, setAgentResponse] = useState<string | null>(null);
  const [notifications, _setNotifications] = useState(3);
  const [showProfit, setShowProfit] = useState(false);

  useEffect(() => {
    setIsAuthenticated(!!getApiKey());
  }, []);

  const handleVoiceQuery = () => {
    setIsListening(true);
    setTimeout(() => {
      setIsListening(false);
      setAgentResponse('Field North Quarter moisture at 32.4%. No irrigation needed for 18 hours. Weather forecast shows 20% rain chance tomorrow.');
    }, 2000);
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'optimal': return 'text-emerald-500 bg-emerald-500/10';
      case 'warning': return 'text-amber-500 bg-amber-500/10';
      case 'critical': return 'text-red-500 bg-red-500/10';
      default: return 'text-slate-500 bg-slate-500/10';
    }
  };

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-slate-900 flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-950 border-r border-slate-800 transform transition-transform lg:translate-x-0 lg:static ${showMobileMenu ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
              <Sprout className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">FarmSense</h1>
              <p className="text-xs text-slate-500">Farmer Portal</p>
            </div>
          </div>
        </div>

        <nav className="p-4 space-y-1">
          {[
            { id: 'overview', label: 'Overview', icon: LayoutDashboard },
            { id: 'fields', label: 'Field Map', icon: MapIcon },
            { id: 'irrigation', label: 'Irrigation', icon: Droplets },
            { id: 'alerts', label: 'Alerts', icon: Bell, badge: notifications },
            { id: 'settings', label: 'Settings', icon: Settings },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => { setActiveTab(item.id); setShowMobileMenu(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === item.id 
                  ? 'bg-emerald-500/10 text-emerald-400' 
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
              {item.badge && (
                <span className="ml-auto bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">JD</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">John Doe</p>
              <p className="text-xs text-slate-500">Premium Plan</p>
            </div>
          </div>
          <button
            onClick={() => { removeApiKey(); setIsAuthenticated(false); }}
            className="w-full flex items-center gap-2 px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowMobileMenu(true)}
                className="lg:hidden p-2 text-slate-400 hover:text-white"
              >
                <Menu className="w-6 h-6" />
              </button>
              <h2 className="text-xl font-bold text-white">
                {activeTab === 'overview' && 'Farm Overview'}
                {activeTab === 'fields' && 'Field Map'}
                {activeTab === 'irrigation' && 'Irrigation Schedule'}
                {activeTab === 'alerts' && 'Alerts & Notifications'}
                {activeTab === 'settings' && 'Settings'}
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleVoiceQuery}
                className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                  isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                <Mic className="w-4 h-4" />
                <span className="hidden sm:inline text-sm">Ask Silas</span>
              </button>
              <div className="relative">
                <Bell className="w-5 h-5 text-slate-400" />
                {notifications > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                    {notifications}
                  </span>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Voice Agent Response */}
        {agentResponse && (
          <div className="mx-6 mt-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 flex items-start gap-3">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center flex-shrink-0">
              <Sprout className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-emerald-100 text-sm">{agentResponse}</p>
            </div>
            <button onClick={() => setAgentResponse(null)} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Stats Grid */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <Droplets className="w-5 h-5 text-blue-400" />
                    <span className="text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full">Optimal</span>
                  </div>
                  <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">Avg Moisture</p>
                  <p className="text-2xl font-black text-white mt-1">32.4%</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <Thermometer className="w-5 h-5 text-orange-400" />
                    <span className="text-xs font-bold text-orange-400 bg-orange-400/10 px-2 py-0.5 rounded-full">High</span>
                  </div>
                  <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">Temperature</p>
                  <p className="text-2xl font-black text-white mt-1">28.5°C</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <CloudRain className="w-5 h-5 text-blue-400" />
                    <span className="text-xs font-bold text-slate-400 bg-slate-400/10 px-2 py-0.5 rounded-full">20%</span>
                  </div>
                  <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">Rain Chance</p>
                  <p className="text-2xl font-black text-white mt-1">Tomorrow</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5 cursor-pointer" onClick={() => setShowProfit(!showProfit)}>
                  <div className="flex items-center justify-between mb-3">
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                    <span className="text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full">+12%</span>
                  </div>
                  <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">
                    {showProfit ? 'Est. Savings' : 'Pump Status'}
                  </p>
                  <p className="text-2xl font-black text-white mt-1">
                    {showProfit ? '$4,280' : 'Standby'}
                  </p>
                </div>
              </div>

              {/* Fields List */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                  <h3 className="text-white font-bold">Your Fields</h3>
                  <button className="text-emerald-400 text-sm hover:text-emerald-300">View All</button>
                </div>
                <div className="divide-y divide-slate-700">
                  {mockFields.map((field) => (
                    <div
                      key={field.id}
                      onClick={() => setSelectedField(field)}
                      className={`p-4 flex items-center justify-between cursor-pointer transition-colors ${
                        selectedField.id === field.id ? 'bg-emerald-500/10' : 'hover:bg-slate-700/50'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-slate-700 rounded-xl flex items-center justify-center">
                          <Sprout className="w-6 h-6 text-emerald-400" />
                        </div>
                        <div>
                          <p className="text-white font-medium">{field.name}</p>
                          <p className="text-slate-400 text-sm">{field.acres} acres • {field.crop}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-white font-bold">{field.moisture}%</p>
                          <p className="text-slate-400 text-xs">Moisture</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${getHealthColor(field.health)}`}>
                          {field.health}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <button className="bg-emerald-500 hover:bg-emerald-600 text-white p-4 rounded-2xl flex flex-col items-center gap-2 transition-colors">
                  <Droplet className="w-6 h-6" />
                  <span className="font-medium">Start Irrigation</span>
                </button>
                <button className="bg-slate-800 hover:bg-slate-700 text-white p-4 rounded-2xl flex flex-col items-center gap-2 transition-colors">
                  <Activity className="w-6 h-6" />
                  <span className="font-medium">Soil Report</span>
                </button>
                <button className="bg-slate-800 hover:bg-slate-700 text-white p-4 rounded-2xl flex flex-col items-center gap-2 transition-colors">
                  <Sun className="w-6 h-6" />
                  <span className="font-medium">Weather</span>
                </button>
                <button className="bg-slate-800 hover:bg-slate-700 text-white p-4 rounded-2xl flex flex-col items-center gap-2 transition-colors">
                  <Wind className="w-6 h-6" />
                  <span className="font-medium">Forecast</span>
                </button>
              </div>
            </div>
          )}

          {activeTab === 'fields' && (
            <FieldMap selectedField={selectedField} onFieldSelect={setSelectedField} />
          )}

          {activeTab === 'irrigation' && (
            <TelemetryPanel field={selectedField} />
          )}

          {activeTab === 'alerts' && (
            <div className="space-y-4">
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-start gap-4">
                <AlertTriangle className="w-6 h-6 text-amber-400 flex-shrink-0" />
                <div>
                  <h4 className="text-white font-bold">Low Moisture Alert</h4>
                  <p className="text-slate-300 text-sm mt-1">East Section moisture at 28.1%. Recommend irrigation within 4 hours.</p>
                  <p className="text-slate-500 text-xs mt-2">2 hours ago</p>
                </div>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 flex items-start gap-4">
                <CheckCircle className="w-6 h-6 text-emerald-400 flex-shrink-0" />
                <div>
                  <h4 className="text-white font-bold">Irrigation Complete</h4>
                  <p className="text-slate-300 text-sm mt-1">North Quarter irrigation completed successfully. 2,400 gallons used.</p>
                  <p className="text-slate-500 text-xs mt-2">2 hours ago</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default FarmDashboard;
