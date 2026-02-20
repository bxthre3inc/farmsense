import { useState, useEffect } from 'react';
import {
  FileText, CheckCircle, AlertTriangle, Users, Droplets, Shield,
  Map, Activity, BarChart3, Download, Calendar, Search, Filter,
  ChevronDown, TrendingUp, Award, Leaf, Droplet, LogOut
} from 'lucide-react';
import { removeApiKey } from '../shared/api';
import Login from './Login';

// Types
interface GrantProgram {
  id: string;
  name: string;
  agency: string;
  total_funding: number;
  allocated: number;
  status: 'active' | 'pending' | 'closed';
  start_date: string;
  end_date: string;
}

interface Grantee {
  id: string;
  name: string;
  type: 'farm' | 'research' | 'consortium';
  award_amount: number;
  water_saved: number;
  compliance_score: number;
  status: 'approved' | 'in_progress' | 'completed';
}

interface ImpactMetric {
  metric: string;
  value: number;
  unit: string;
  change: number;
  period: string;
}

const mockGrants: GrantProgram[] = [
  { id: 'GRT-2025-001', name: 'WaterSMART Initiative', agency: 'Bureau of Reclamation', total_funding: 2500000, allocated: 1850000, status: 'active', start_date: '2025-01-15', end_date: '2027-01-14' },
  { id: 'GRT-2025-002', name: 'Sustainable Ag Research', agency: 'USDA NRCS', total_funding: 1800000, allocated: 920000, status: 'active', start_date: '2025-03-01', end_date: '2026-12-31' },
  { id: 'GRT-2025-003', name: 'Aquifer Recharge Program', agency: 'Colorado Water Conservation Board', total_funding: 3200000, allocated: 0, status: 'pending', start_date: '2025-06-01', end_date: '2028-05-31' },
];

const mockGrantees: Grantee[] = [
  { id: 'GRA-001', name: 'San Luis Valley Research Center', type: 'research', award_amount: 450000, water_saved: 12500, compliance_score: 96, status: 'in_progress' },
  { id: 'GRA-002', name: 'Rio Grande Conservation District', type: 'consortium', award_amount: 320000, water_saved: 8900, compliance_score: 94, status: 'in_progress' },
  { id: 'GRA-003', name: 'Valley Farms Cooperative', type: 'farm', award_amount: 180000, water_saved: 5400, compliance_score: 98, status: 'approved' },
  { id: 'GRA-004', name: 'CSU Extension - Alamosa', type: 'research', award_amount: 275000, water_saved: 7200, compliance_score: 92, status: 'in_progress' },
];

const mockImpactMetrics: ImpactMetric[] = [
  { metric: 'Water Conserved', value: 34000, unit: 'acre-ft', change: 12.5, period: 'YTD' },
  { metric: 'Aquifer Level Change', value: 0.8, unit: 'ft', change: 15.2, period: 'YoY' },
  { metric: 'Farmers Trained', value: 284, unit: 'producers', change: 8.3, period: 'YTD' },
  { metric: 'Technology Deployed', value: 42, unit: 'systems', change: 35.0, period: 'YTD' },
];

const GrantDashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="text-amber-400 w-6 h-6" />
            Grant Portal
          </h1>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'programs', label: 'Programs', icon: Award },
            { id: 'grantees', label: 'Grantees', icon: Users },
            { id: 'impact', label: 'Impact Metrics', icon: BarChart3 },
            { id: 'compliance', label: 'SLV Compliance', icon: Shield },
            { id: 'reports', label: 'Reports', icon: FileText },
          ].map((item) => (
            <button key={item.id} onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === item.id ? 'bg-amber-500/10 text-amber-400' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}>
              <item.icon className="w-5 h-5" />
              <span className="font-medium text-sm">{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800">
          <button onClick={() => { removeApiKey(); setIsAuthenticated(false); }}
            className="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-xl">
            <LogOut className="w-5 h-5" />
            <span className="font-medium text-sm">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white capitalize">{activeTab}</h2>
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input type="text" placeholder="Search..." className="bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 w-64" />
              </div>
              <button className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center text-white font-bold">G</button>
            </div>
          </div>
        </header>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Active Programs</p>
                  <p className="text-2xl font-bold text-white mt-1">3</p>
                  <span className="text-amber-400 text-xs">$7.5M total funding</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Active Grantees</p>
                  <p className="text-2xl font-bold text-white mt-1">12</p>
                  <span className="text-emerald-400 text-xs">+3 new this quarter</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Water Conserved</p>
                  <p className="text-2xl font-bold text-emerald-400 mt-1">34K acre-ft</p>
                  <span className="text-emerald-400 text-xs">+12.5% YTD</span>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                  <p className="text-slate-400 text-sm">Avg Compliance</p>
                  <p className="text-2xl font-bold text-amber-400 mt-1">95%</p>
                  <span className="text-emerald-400 text-xs">Above SLV threshold</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-white font-bold mb-4">Program Funding Status</h3>
                  <div className="space-y-4">
                    {mockGrants.map((g) => (
                      <div key={g.id} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-white text-sm">{g.name}</span>
                          <span className="text-slate-400 text-xs">${(g.allocated / 1000000).toFixed(1)}M / ${(g.total_funding / 1000000).toFixed(1)}M</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${(g.allocated / g.total_funding) * 100}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-white font-bold mb-4">Impact Summary</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {mockImpactMetrics.slice(0, 4).map((m) => (
                      <div key={m.metric} className="bg-slate-800/50 p-4 rounded-xl">
                        <p className="text-slate-400 text-xs">{m.metric}</p>
                        <p className="text-white font-bold text-lg">{m.value.toLocaleString()} {m.unit}</p>
                        <span className="text-emerald-400 text-xs">+{m.change}% {m.period}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'programs' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-white font-bold">Grant Programs</h3>
                <button className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg">
                  <Download className="w-4 h-4" />
                  Export
                </button>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="text-left p-4 text-slate-400 text-sm">Program</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Agency</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Total Funding</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Allocated</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Status</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Period</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockGrants.map((g) => (
                      <tr key={g.id} className="border-t border-slate-800">
                        <td className="p-4">
                          <p className="text-white font-medium">{g.name}</p>
                          <p className="text-slate-500 text-sm">{g.id}</p>
                        </td>
                        <td className="p-4 text-slate-300">{g.agency}</td>
                        <td className="p-4 text-white">${(g.total_funding / 1000000).toFixed(2)}M</td>
                        <td className="p-4 text-slate-300">${(g.allocated / 1000000).toFixed(2)}M</td>
                        <td className="p-4">
                          <span className={`text-xs px-2 py-1 rounded-full ${g.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : g.status === 'pending' ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-500/20 text-slate-400'}`}>{g.status}</span>
                        </td>
                        <td className="p-4 text-slate-400 text-sm">{g.start_date} to {g.end_date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'grantees' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-white font-bold">Grant Recipients</h3>
                <div className="flex items-center gap-2">
                  {['all', 'farm', 'research', 'consortium'].map((f) => (
                    <button key={f} className="px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-slate-300 text-xs capitalize">{f}</button>
                  ))}
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="text-left p-4 text-slate-400 text-sm">Recipient</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Type</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Award</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Water Saved</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Compliance</th>
                      <th className="text-left p-4 text-slate-400 text-sm">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockGrantees.map((g) => (
                      <tr key={g.id} className="border-t border-slate-800">
                        <td className="p-4">
                          <p className="text-white font-medium">{g.name}</p>
                          <p className="text-slate-500 text-sm">{g.id}</p>
                        </td>
                        <td className="p-4 text-slate-300 capitalize">{g.type}</td>
                        <td className="p-4 text-white">${(g.award_amount / 1000).toFixed(0)}K</td>
                        <td className="p-4 text-emerald-400">{g.water_saved.toLocaleString()} acre-ft</td>
                        <td className="p-4">
                          <span className={`text-sm ${g.compliance_score >= 95 ? 'text-emerald-400' : g.compliance_score >= 90 ? 'text-amber-400' : 'text-red-400'}`}>{g.compliance_score}%</span>
                        </td>
                        <td className="p-4">
                          <span className={`text-xs px-2 py-1 rounded-full ${g.status === 'approved' ? 'bg-emerald-500/20 text-emerald-400' : g.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-500/20 text-slate-400'}`}>{g.status.replace('_', ' ')}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'impact' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                {mockImpactMetrics.map((m) => (
                  <div key={m.metric} className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-white font-bold">{m.metric}</h4>
                      <span className={`text-sm ${m.change > 0 ? 'text-emerald-400' : 'text-red-400'}`}>{m.change > 0 ? '+' : ''}{m.change}% {m.period}</span>
                    </div>
                    <p className="text-4xl font-bold text-white">{m.value.toLocaleString()}</p>
                    <p className="text-slate-400 text-sm mt-1">{m.unit}</p>
                  </div>
                ))}
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-white font-bold mb-4">Environmental Impact Dashboard</h3>
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-slate-800/50 rounded-xl">
                    <Leaf className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                    <p className="text-white font-bold text-2xl">1,247</p>
                    <p className="text-slate-400 text-sm">Acres under conservation</p>
                  </div>
                  <div className="text-center p-4 bg-slate-800/50 rounded-xl">
                    <Droplet className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                    <p className="text-white font-bold text-2xl">18%</p>
                    <p className="text-slate-400 text-sm">Irrigation efficiency gain</p>
                  </div>
                  <div className="text-center p-4 bg-slate-800/50 rounded-xl">
                    <Users className="w-8 h-8 text-amber-400 mx-auto mb-2" />
                    <p className="text-white font-bold text-2xl">284</p>
                    <p className="text-slate-400 text-sm">Producers trained</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'compliance' && (
            <div className="space-y-6">
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-2">
                  <Shield className="w-6 h-6 text-emerald-400" />
                  <h3 className="text-white font-bold">SLV 2026 Compliance Status</h3>
                </div>
                <p className="text-emerald-400 text-lg font-bold">95% Average Compliance Score</p>
                <p className="text-slate-400 text-sm">All grantees currently meeting or exceeding SLV sustainability requirements</p>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <h4 className="text-white font-bold mb-4">Compliance by Grantee</h4>
                  <div className="space-y-3">
                    {mockGrantees.map((g) => (
                      <div key={g.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <span className="text-white text-sm">{g.name}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 bg-slate-700 rounded-full h-2">
                            <div className={`h-2 rounded-full ${g.compliance_score >= 95 ? 'bg-emerald-500' : g.compliance_score >= 90 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${g.compliance_score}%` }} />
                          </div>
                          <span className={`text-sm w-10 ${g.compliance_score >= 95 ? 'text-emerald-400' : g.compliance_score >= 90 ? 'text-amber-400' : 'text-red-400'}`}>{g.compliance_score}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <h4 className="text-white font-bold mb-4">SLV Requirements Checklist</h4>
                  <div className="space-y-2">
                    {[
                      { req: 'Annual water reporting', status: 'complete' },
                      { req: 'Aquifer level monitoring', status: 'complete' },
                      { req: 'Conservation plan submission', status: 'complete' },
                      { req: 'Technology deployment verification', status: 'complete' },
                      { req: 'Producer training completion', status: 'in_progress' },
                    ].map((item, i) => (
                      <div key={i} className="flex items-center gap-3 p-2">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center ${item.status === 'complete' ? 'bg-emerald-500' : 'bg-amber-500'}`}>
                          {item.status === 'complete' ? <CheckCircle className="w-3 h-3 text-white" /> : <span className="text-white text-xs">!</span>}
                        </div>
                        <span className="text-slate-300 text-sm">{item.req}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default GrantDashboard;
