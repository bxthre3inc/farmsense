import React, { useState } from 'react';
import {
  LayoutDashboard,
  Search,
  Bell,
  LogOut,
  ShieldCheck,
  ClipboardList,
  TrendingUp,
  FlaskConical,
  Download,
  Filter,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Leaf,
  FileText,
  Users,
  Globe,
  Lock,
  Eye
} from 'lucide-react';
import { removeApiKey } from '../shared/api';
import Login from './Login';

interface ComplianceReport {
  id: string;
  field: string;
  farmer: string;
  period: string;
  waterUsage: string;
  compliance: 'compliant' | 'violation' | 'pending';
  score: number;
  submitted: string;
}

interface ResearchDataset {
  id: string;
  name: string;
  type: string;
  records: number;
  size: string;
  updated: string;
  access: 'public' | 'restricted' | 'private';
}

const mockReports: ComplianceReport[] = [
  { id: 'RPT-2026-001', field: 'North Quarter', farmer: 'John Doe', period: 'Jan 2026', waterUsage: '2,400 m³', compliance: 'compliant', score: 98.5, submitted: '2026-02-01' },
  { id: 'RPT-2026-002', field: 'East Section', farmer: 'Jane Smith', period: 'Jan 2026', waterUsage: '3,100 m³', compliance: 'violation', score: 72.3, submitted: '2026-02-01' },
  { id: 'RPT-2026-003', field: 'West Pasture', farmer: 'Mike Johnson', period: 'Jan 2026', waterUsage: '1,800 m³', compliance: 'compliant', score: 95.8, submitted: '2026-02-02' },
  { id: 'RPT-2026-004', field: 'South Fields', farmer: 'Sarah Lee', period: 'Jan 2026', waterUsage: '2,950 m³', compliance: 'pending', score: 0, submitted: '2026-02-03' },
];

const mockDatasets: ResearchDataset[] = [
  { id: 'DS-001', name: 'Water Usage Patterns 2025', type: 'Time Series', records: 2500000, size: '4.2 GB', updated: '2026-01-15', access: 'public' },
  { id: 'DS-002', name: 'Soil Health Analysis', type: 'Spatial', records: 450000, size: '12.8 GB', updated: '2026-01-20', access: 'restricted' },
  { id: 'DS-003', name: 'Yield Prediction Models', type: 'ML Training', records: 120000, size: '2.1 GB', updated: '2026-02-01', access: 'private' },
  { id: 'DS-004', name: 'Climate Impact Study', type: 'Climate', records: 890000, size: '8.5 GB', updated: '2026-02-05', access: 'public' },
];

const OversightDashboard: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  const getComplianceIcon = (status: string) => {
    switch (status) {
      case 'compliant': return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case 'violation': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'pending': return <AlertTriangle className="w-5 h-5 text-amber-400" />;
      default: return <AlertTriangle className="w-5 h-5 text-slate-400" />;
    }
  };

  const getComplianceClass = (status: string) => {
    switch (status) {
      case 'compliant': return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
      case 'violation': return 'bg-red-500/10 border-red-500/30 text-red-400';
      case 'pending': return 'bg-amber-500/10 border-amber-500/30 text-amber-400';
      default: return 'bg-slate-500/10 border-slate-500/30 text-slate-400';
    }
  };

  const getAccessIcon = (access: string) => {
    switch (access) {
      case 'public': return <Globe className="w-4 h-4 text-emerald-400" />;
      case 'restricted': return <Eye className="w-4 h-4 text-amber-400" />;
      case 'private': return <Lock className="w-4 h-4 text-red-400" />;
      default: return <Lock className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-xl">
                <ShieldCheck className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-800">Oversight Portal</h1>
                <p className="text-xs text-slate-500">Government • Audit • Research</p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search reports, datasets..."
                  className="pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                />
              </div>
              <button className="relative p-2 text-slate-400 hover:text-slate-600">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <div className="flex items-center gap-3 border-l border-slate-200 pl-6">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-900">Officer Demo</p>
                  <p className="text-xs text-slate-500">SLV Agency</p>
                </div>
                <button
                  onClick={() => { removeApiKey(); setIsAuthenticated(false); }}
                  className="p-2 text-slate-400 hover:text-red-500 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="border-t border-slate-200">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex gap-8 h-12">
              {[
                { id: 'overview', label: 'Overview', icon: LayoutDashboard },
                { id: 'compliance', label: 'Compliance Reports', icon: ClipboardList },
                { id: 'research', label: 'Research Data', icon: FlaskConical },
                { id: 'impact', label: 'Economic Impact', icon: TrendingUp },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-1 border-b-2 text-sm font-medium transition-all ${
                    activeTab === item.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-slate-500 hover:text-slate-700'
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-4 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100">
                <div className="flex items-center justify-between mb-4">
                  <ClipboardList className="w-8 h-8 text-blue-500" />
                  <span className="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">94.2%</span>
                </div>
                <p className="text-slate-500 text-sm">Compliance Rate</p>
                <p className="text-2xl font-bold text-slate-900">1,247 farms</p>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100">
                <div className="flex items-center justify-between mb-4">
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                  <span className="text-sm font-medium text-red-600 bg-red-50 px-2 py-1 rounded-full">3</span>
                </div>
                <p className="text-slate-500 text-sm">Critical Violations</p>
                <p className="text-2xl font-bold text-slate-900">Action needed</p>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100">
                <div className="flex items-center justify-between mb-4">
                  <FlaskConical className="w-8 h-8 text-purple-500" />
                  <span className="text-sm font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded-full">4.2 TB</span>
                </div>
                <p className="text-slate-500 text-sm">Research Data</p>
                <p className="text-2xl font-bold text-slate-900">12 datasets</p>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100">
                <div className="flex items-center justify-between mb-4">
                  <Leaf className="w-8 h-8 text-emerald-500" />
                  <span className="text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">-12%</span>
                </div>
                <p className="text-slate-500 text-sm">Water Saved</p>
                <p className="text-2xl font-bold text-slate-900">4.2M gallons</p>
              </div>
            </div>

            {/* Recent Reports & Quick Actions */}
            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-2 bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                  <h3 className="font-bold text-slate-800">Recent Compliance Reports</h3>
                  <button className="text-blue-600 text-sm hover:text-blue-700">View All</button>
                </div>
                <div className="divide-y divide-slate-100">
                  {mockReports.slice(0, 3).map((report) => (
                    <div key={report.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
                      <div className="flex items-center gap-4">
                        {getComplianceIcon(report.compliance)}
                        <div>
                          <p className="font-medium text-slate-800">{report.id}</p>
                          <p className="text-sm text-slate-500">{report.field} • {report.farmer}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getComplianceClass(report.compliance)}`}>
                          {report.compliance}
                        </span>
                        {report.score > 0 && (
                          <p className="text-sm text-slate-500 mt-1">Score: {report.score}%</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
                  <h3 className="font-bold text-slate-800 mb-4">Quick Actions</h3>
                  <div className="space-y-2">
                    <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 text-left transition-colors">
                      <Download className="w-5 h-5 text-blue-500" />
                      <span className="text-slate-700">Export Monthly Report</span>
                    </button>
                    <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 text-left transition-colors">
                      <FileText className="w-5 h-5 text-emerald-500" />
                      <span className="text-slate-700">Generate Certificate</span>
                    </button>
                    <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 text-left transition-colors">
                      <Users className="w-5 h-5 text-purple-500" />
                      <span className="text-slate-700">Request Inspection</span>
                    </button>
                  </div>
                </div>

                <div className="bg-blue-600 rounded-xl shadow-sm p-4 text-white">
                  <h3 className="font-bold mb-2">SLV 2026 Compliance</h3>
                  <p className="text-blue-100 text-sm mb-4">Water usage regulations and sustainable agriculture standards.</p>
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4" />
                    <span>98.5% aligned</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50">
                  <Filter className="w-4 h-4" />
                  Filter
                </button>
                <input
                  type="text"
                  placeholder="Search reports..."
                  className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                <Download className="w-4 h-4" />
                Export All
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left p-4 text-sm font-medium text-slate-600">Report ID</th>
                    <th className="text-left p-4 text-sm font-medium text-slate-600">Field</th>
                    <th className="text-left p-4 text-sm font-medium text-slate-600">Farmer</th>
                    <th className="text-left p-4 text-sm font-medium text-slate-600">Period</th>
                    <th className="text-left p-4 text-sm font-medium text-slate-600">Water Usage</th>
                    <th className="text-left p-4 text-sm font-medium text-slate-600">Status</th>
                    <th className="text-left p-4 text-sm font-medium text-slate-600">Score</th>
                    <th className="text-left p-4 text-sm font-medium text-slate-600"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {mockReports.map((report) => (
                    <tr key={report.id} className="hover:bg-slate-50">
                      <td className="p-4 font-medium text-slate-800">{report.id}</td>
                      <td className="p-4 text-slate-600">{report.field}</td>
                      <td className="p-4 text-slate-600">{report.farmer}</td>
                      <td className="p-4 text-slate-600">{report.period}</td>
                      <td className="p-4 text-slate-600">{report.waterUsage}</td>
                      <td className="p-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getComplianceClass(report.compliance)}`}>
                          {report.compliance}
                        </span>
                      </td>
                      <td className="p-4">
                        {report.score > 0 ? (
                          <span className={`font-bold ${
                            report.score >= 90 ? 'text-emerald-600' :
                            report.score >= 70 ? 'text-amber-600' :
                            'text-red-600'
                          }`}>
                            {report.score}%
                          </span>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="p-4">
                        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'research' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
              <h3 className="font-bold text-slate-800 mb-2">Research Data Repository</h3>
              <p className="text-slate-500">Access anonymized agricultural data for research and policy analysis.</p>
            </div>

            <div className="grid grid-cols-2 gap-6">
              {mockDatasets.map((dataset) => (
                <div key={dataset.id} className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                        <FlaskConical className="w-6 h-6 text-purple-600" />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-800">{dataset.name}</h4>
                        <p className="text-sm text-slate-500">{dataset.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-slate-500">
                      {getAccessIcon(dataset.access)}
                      <span className="capitalize">{dataset.access}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-slate-500 text-xs">Records</p>
                      <p className="font-medium text-slate-800">{(dataset.records / 1000000).toFixed(1)}M</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Size</p>
                      <p className="font-medium text-slate-800">{dataset.size}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Updated</p>
                      <p className="font-medium text-slate-800">{dataset.updated}</p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button className="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
                      Access Data
                    </button>
                    <button className="py-2 px-4 border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50">
                      Documentation
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default OversightDashboard;
