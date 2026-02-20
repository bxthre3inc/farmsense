import { useState } from 'react';
import { Shield, Users, Settings, Activity, BarChart3, Bell } from 'lucide-react';
import { 
  Login, 
  Card, 
  Button, 
  MetricCard, 
  NetworkStatus, 
  CompressionStats,
  StatusIndicator,
  Badge,
  useAuth,
  Alert,
  Loading 
} from '../../shared/components';

// Mock admin data
const mockUsers = [
  { id: '1', email: 'farmer@example.com', role: 'Farmer', tier: 'Pro', status: 'active' },
  { id: '2', email: 'auditor@example.com', role: 'Auditor', tier: 'Enterprise', status: 'active' },
  { id: '3', email: 'investor@example.com', role: 'Investor', tier: 'Enterprise', status: 'pending' },
];

function Dashboard() {
  const { logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800">
      {/* Header */}
      <header className="bg-white/5 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-slate-500/20 rounded-xl">
                <Shield className="w-6 h-6 text-slate-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Admin Control</h1>
                <p className="text-xs text-slate-400">System Management</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <StatusIndicator status="online" size="sm" />
                <span className="text-sm text-slate-400">System Healthy</span>
              </div>
              <Button variant="ghost" size="sm" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white/5 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-1 py-2">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'users', label: 'Users', icon: Users },
              { id: 'network', label: 'Network', icon: Activity },
              { id: 'settings', label: 'Settings', icon: Settings },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white/10 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <>
            {/* Optimization Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              <CompressionStats
                originalBytes={150000000}
                compressedBytes={35714285}
                ratio={4.2}
                deviceCount={15600}
                batteryExtension={250}
              />
              <NetworkStatus />
              <Card title="System Alerts" icon={<Bell className="w-5 h-5 text-amber-400" />} glass>
                <div className="space-y-3">
                  <Alert variant="success" title="Delta Encoding Active">
                    All 15,600 LRZ devices using delta compression. 94% bandwidth reduction achieved.
                  </Alert>
                  <Alert variant="info" title="Adaptive Sampling">
                    Winter dormancy mode active. Sampling interval increased to 6 hours.
                  </Alert>
                </div>
              </Card>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Total Users"
                value="15,420"
                change={12.5}
                changeLabel="vs last month"
                icon={<Users className="w-5 h-5 text-blue-400" />}
                trend="up"
              />
              <MetricCard
                title="Active Devices"
                value="19,466"
                change={0.8}
                changeLabel="vs yesterday"
                icon={<Activity className="w-5 h-5 text-emerald-400" />}
                trend="up"
              />
              <MetricCard
                title="System Uptime"
                value="99.98"
                unit="%"
                change={0}
                changeLabel="stable"
                icon={<Shield className="w-5 h-5 text-slate-400" />}
                trend="neutral"
              />
              <MetricCard
                title="Daily Ingestion"
                value="2.8M"
                unit="readings"
                change={-5.2}
                changeLabel="due to compression"
                icon={<BarChart3 className="w-5 h-5 text-purple-400" />}
                trend="neutral"
              />
            </div>
          </>
        )}

        {activeTab === 'users' && (
          <Card title="User Management" icon={<Users className="w-5 h-5 text-blue-400" />} glass>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Email</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Role</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Tier</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Status</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {mockUsers.map((user) => (
                    <tr key={user.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-3 px-4 text-white">{user.email}</td>
                      <td className="py-3 px-4">
                        <Badge variant="info">{user.role}</Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-300">{user.tier}</td>
                      <td className="py-3 px-4">
                        <StatusIndicator 
                          status={user.status === 'active' ? 'online' : 'warning'} 
                          size="sm"
                        />
                      </td>
                      <td className="py-3 px-4">
                        <Button variant="ghost" size="sm">Edit</Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {activeTab === 'network' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <NetworkStatus showDetails />
            <Card title="Network Topology" icon={<Activity className="w-5 h-5 text-blue-400" />} glass>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-2 border-b border-white/10">
                  <span className="text-slate-400">LRZ Devices</span>
                  <div className="flex items-center gap-2">
                    <span className="text-white">15,600</span>
                    <StatusIndicator status="online" size="sm" />
                  </div>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-white/10">
                  <span className="text-slate-400">VFA Anchors</span>
                  <div className="flex items-center gap-2">
                    <span className="text-white">1,280</span>
                    <StatusIndicator status="online" size="sm" />
                  </div>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-white/10">
                  <span className="text-slate-400">DHU Hubs</span>
                  <div className="flex items-center gap-2">
                    <span className="text-white">25</span>
                    <StatusIndicator status="online" size="sm" />
                  </div>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-white/10">
                  <span className="text-slate-400">RSS Stations</span>
                  <div className="flex items-center gap-2">
                    <span className="text-white">1</span>
                    <StatusIndicator status="online" size="sm" />
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'settings' && (
          <Card title="System Settings" icon={<Settings className="w-5 h-5 text-slate-400" />} glass>
            <div className="space-y-6">
              <div>
                <h4 className="text-white font-medium mb-2">Delta Compression</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Configure compression levels for different device types.
                </p>
                <div className="flex gap-2">
                  <Button variant="primary" size="sm">Light</Button>
                  <Button variant="secondary" size="sm">Standard</Button>
                  <Button variant="secondary" size="sm">Aggressive</Button>
                </div>
              </div>
              
              <div className="border-t border-white/10 pt-6">
                <h4 className="text-white font-medium mb-2">Adaptive Sampling</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Enable dynamic sampling rate adjustment based on field conditions.
                </p>
                <StatusIndicator status="online" label="Enabled" />
              </div>
              
              <div className="border-t border-white/10 pt-6">
                <h4 className="text-white font-medium mb-2">Forward Error Correction</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Redundancy for unreliable mesh networks. Current: 10% overhead.
                </p>
                <StatusIndicator status="online" label="Active" />
              </div>
            </div>
          </Card>
        )}
      </main>
    </div>
  );
}

function App() {
  const { isAuthenticated, login, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Loading fullScreen={false} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Login
        onLogin={(key) => login(key, 'admin')}
        variant="admin"
        demoCredentials={[
          { label: 'Admin', key: 'demo-admin-key' },
        ]}
      />
    );
  }

  return <Dashboard />;
}

export default App;
