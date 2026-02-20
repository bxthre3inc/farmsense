import { useState } from 'react';
import { Leaf, Droplets, Sun, Wind, Activity } from 'lucide-react';
import { 
  Login, 
  Card, 
  Button, 
  MetricCard, 
  TelemetryCard, 
  NetworkStatus, 
  CompressionStats,
  EmptyState,
  useAuth,
  useTelemetry,
  Badge,
  StatusIndicator 
} from '../../shared/components';
import AgriMap from './components/map/AgriMap';

function Dashboard() {
  const { logout } = useAuth();
  const [selectedField, setSelectedField] = useState('field_01');
  const { data: telemetryData, isLoading, error } = useTelemetry({ 
    fieldId: selectedField,
    refreshInterval: 30000 
  });

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <Leaf className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">FarmSense</h1>
                <p className="text-xs text-emerald-600">Farmer Dashboard</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <StatusIndicator status="online" size="sm" />
                <span className="text-sm text-slate-500">Connected</span>
              </div>
              <Button variant="ghost" size="sm" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Optimization Stats Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <CompressionStats
            originalBytes={150000000}
            compressedBytes={35714285}
            ratio={4.2}
            deviceCount={15600}
            batteryExtension={250}
          />
          <NetworkStatus />
          <Card title="System Health" icon={<Activity className="w-5 h-5 text-emerald-600" />}>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Database</span>
                <StatusIndicator status="online" label="Healthy" />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Kriging Engine</span>
                <StatusIndicator status="online" label="Running" />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Satellite Uplink</span>
                <StatusIndicator status="online" label="Connected" />
              </div>
            </div>
          </Card>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Avg Surface Moisture"
            value="32.5"
            unit="%"
            change={-2.1}
            changeLabel="vs last hour"
            icon={<Droplets className="w-5 h-5 text-blue-600" />}
            trend="down"
          />
          <MetricCard
            title="Avg Root Moisture"
            value="28.3"
            unit="%"
            change={-1.5}
            changeLabel="vs last hour"
            icon={<Droplets className="w-5 h-5 text-cyan-600" />}
            trend="neutral"
          />
          <MetricCard
            title="Field Temperature"
            value="24.8"
            unit="°C"
            change={1.2}
            changeLabel="vs yesterday"
            icon={<Sun className="w-5 h-5 text-amber-600" />}
            trend="up"
          />
          <MetricCard
            title="Wind Speed"
            value="12.4"
            unit="km/h"
            change={0}
            changeLabel="steady"
            icon={<Wind className="w-5 h-5 text-slate-600" />}
            trend="neutral"
          />
        </div>

        {/* Map and Telemetry */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map */}
          <div className="lg:col-span-2">
            <Card title="Field Map" icon={<Leaf className="w-5 h-5 text-emerald-600" />}>
              <div className="h-96 rounded-lg overflow-hidden">
                <AgriMap fieldId={selectedField} />
              </div>
            </Card>
          </div>

          {/* Recent Telemetry */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Recent Readings</h3>
              <Badge variant="success">Live</Badge>
            </div>
            {isLoading ? (
              <Card className="h-64 flex items-center justify-center">
                <div className="animate-spin w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full" />
              </Card>
            ) : error ? (
              <Card className="p-4">
                <EmptyState 
                  icon="alert"
                  title="Connection Error"
                  description={error}
                />
              </Card>
            ) : telemetryData.length === 0 ? (
              <Card className="p-4">
                <EmptyState 
                  icon="inbox"
                  title="No Data Available"
                  description="No sensor readings found for this field. Data will appear once devices are deployed and connected."
                />
              </Card>
            ) : (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {telemetryData.map((reading) => (
                  <TelemetryCard key={reading.deviceId} data={reading} />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function App() {
  const { isAuthenticated, login, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Login
        onLogin={(key) => login(key, 'farmer')}
        variant="farmer"
        demoCredentials={[
          { label: 'Demo Farmer', key: 'demo-farmer-key' },
        ]}
      />
    );
  }

  return <Dashboard />;
}

export default App;
