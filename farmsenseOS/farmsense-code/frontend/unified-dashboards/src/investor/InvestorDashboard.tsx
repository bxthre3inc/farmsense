import { useState, useEffect } from 'react';
import { Users, DollarSign, Activity, LogOut, Zap, Building2, Target, ArrowUpRight } from 'lucide-react';
import { getApiKey, removeApiKey } from '../shared/api';
import Login from './Login';

function InvestorDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [view, setView] = useState<'dashboard' | 'equity' | 'breakroom'>('dashboard');
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    const auth = !!getApiKey();
    setIsAuthenticated(auth);
    if (auth) {
      fetchMetrics();
    }
  }, []);

  const fetchMetrics = async () => {
    try {
      setMetrics({
        total_acreage: 15420,
        enterprise_clients: 42,
        total_users: 15420,
        arr_usd: 2680000,
        growth_pct: 15.4,
        retention_rate: 94.2,
        water_saved_liters: 1250000,
        co2_reduced_tons: 450.5,
        yield_increase_pct: 14.8,
      });
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const handleLogout = () => {
    removeApiKey();
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={() => {
      setIsAuthenticated(true);
      fetchMetrics();
    }} />;
  }

  return (
    <div className="min-h-screen bg-neutral-900 text-white flex flex-col font-sans">
      <header className="bg-neutral-800 border-b border-neutral-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Zap className="text-green-400 w-6 h-6" />
            farmsenseOS <span className="text-neutral-400 font-light">• Investor Portal</span>
          </h1>
          <div className="flex items-center gap-8">
            <nav className="flex gap-6">
              <button
                onClick={() => setView('dashboard')}
                className={`text-[10px] font-black uppercase tracking-[0.2em] transition-all ${view === 'dashboard' ? 'text-green-500 border-b-2 border-green-500 pb-1' : 'text-neutral-500 hover:text-white'}`}
              >
                Intelligence
              </button>
              <button
                onClick={() => setView('equity')}
                className={`text-[10px] font-black uppercase tracking-[0.2em] transition-all ${view === 'equity' ? 'text-green-500 border-b-2 border-green-500 pb-1' : 'text-neutral-500 hover:text-white'}`}
              >
                Equity
              </button>
              <button
                onClick={() => setView('breakroom')}
                className={`text-[10px] font-black uppercase tracking-[0.2em] transition-all ${view === 'breakroom' ? 'text-green-500 border-b-2 border-green-500 pb-1' : 'text-neutral-500 hover:text-white'}`}
              >
                Nexus
              </button>
            </nav>
            <button onClick={handleLogout} className="text-neutral-500 hover:text-red-400 transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-10 overflow-hidden">
        {view === 'dashboard' ? (
          <div className="space-y-12">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-neutral-800 p-6 rounded-2xl border border-neutral-700">
                <div className="flex items-center justify-between mb-4">
                  <DollarSign className="text-green-400 w-5 h-5" />
                  <span className="text-xs text-green-400 font-bold">+{metrics?.growth_pct || 0}%</span>
                </div>
                <p className="text-3xl font-bold text-white">${(metrics?.arr_usd || 0) / 1000000}M</p>
                <p className="text-xs text-neutral-500 mt-1">Annual Recurring Revenue</p>
              </div>
              <div className="bg-neutral-800 p-6 rounded-2xl border border-neutral-700">
                <div className="flex items-center justify-between mb-4">
                  <Users className="text-blue-400 w-5 h-5" />
                  <span className="text-xs text-blue-400 font-bold">Active</span>
                </div>
                <p className="text-3xl font-bold text-white">{metrics?.total_users || 0}</p>
                <p className="text-xs text-neutral-500 mt-1">Total Users</p>
              </div>
              <div className="bg-neutral-800 p-6 rounded-2xl border border-neutral-700">
                <div className="flex items-center justify-between mb-4">
                  <Building2 className="text-purple-400 w-5 h-5" />
                  <span className="text-xs text-purple-400 font-bold">Enterprise</span>
                </div>
                <p className="text-3xl font-bold text-white">{metrics?.enterprise_clients || 0}</p>
                <p className="text-xs text-neutral-500 mt-1">Enterprise Clients</p>
              </div>
              <div className="bg-neutral-800 p-6 rounded-2xl border border-neutral-700">
                <div className="flex items-center justify-between mb-4">
                  <Activity className="text-orange-400 w-5 h-5" />
                  <span className="text-xs text-orange-400 font-bold">Healthy</span>
                </div>
                <p className="text-3xl font-bold text-white">{metrics?.retention_rate || 0}%</p>
                <p className="text-xs text-neutral-500 mt-1">Retention Rate</p>
              </div>
            </div>

            <div className="bg-neutral-800 p-8 rounded-2xl border border-neutral-700">
              <h3 className="text-lg font-bold text-white mb-6 uppercase tracking-tighter">Environmental Impact</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-neutral-900 p-6 rounded-xl">
                  <p className="text-xs text-neutral-500 font-bold uppercase mb-2">Water Saved</p>
                  <p className="text-2xl font-bold text-blue-400">{(metrics?.water_saved_liters || 0) / 1000}K L</p>
                </div>
                <div className="bg-neutral-900 p-6 rounded-xl">
                  <p className="text-xs text-neutral-500 font-bold uppercase mb-2">CO₂ Reduced</p>
                  <p className="text-2xl font-bold text-green-400">{metrics?.co2_reduced_tons || 0} Tons</p>
                </div>
                <div className="bg-neutral-900 p-6 rounded-xl">
                  <p className="text-xs text-neutral-500 font-bold uppercase mb-2">Yield Increase</p>
                  <p className="text-2xl font-bold text-orange-400">{metrics?.yield_increase_pct || 0}%</p>
                </div>
              </div>
            </div>

            <div className="bg-green-500 p-8 rounded-3xl text-black flex flex-col justify-between aspect-square lg:aspect-auto">
              <div className="space-y-2">
                <div className="font-black text-3xl tracking-tighter leading-none">$26.8M</div>
                <div className="text-[10px] font-black uppercase tracking-widest opacity-60">Basis Valuation</div>
              </div>
              <div className="pt-8 flex justify-between items-end">
                <Activity className="w-10 h-10 opacity-20" />
                <div className="text-right">
                  <div className="text-xs font-black uppercase tracking-tighter">Series A Target</div>
                  <div className="text-lg font-black leading-none">$150M</div>
                </div>
              </div>
            </div>
          </div>
        ) : view === 'equity' ? (
          <div className="space-y-8">
            <div className="bg-green-500 p-8 rounded-3xl text-black flex flex-col justify-between aspect-square lg:aspect-auto">
              <div className="space-y-2">
                <div className="font-black text-3xl tracking-tighter leading-none">$26.8M</div>
                <div className="text-[10px] font-black uppercase tracking-widest opacity-60">Basis Valuation</div>
              </div>
              <div className="pt-8 flex justify-between items-end">
                <Activity className="w-10 h-10 opacity-20" />
                <div className="text-right">
                  <div className="text-xs font-black uppercase tracking-tighter">Series A Target</div>
                  <div className="text-lg font-black leading-none">$150M</div>
                </div>
              </div>
            </div>
            <button className="w-full bg-green-500 hover:bg-green-600 text-black font-bold py-4 rounded-2xl transition-colors flex items-center justify-center gap-2">
              <ArrowUpRight className="w-5 h-5" />
              Buy Additional Equity
            </button>
          </div>
        ) : (
          <div className="bg-black/40 rounded-[3rem] border border-white/5 overflow-hidden shadow-2xl h-[85vh] flex items-center justify-center">
            <div className="text-center">
              <Target className="text-green-400 w-16 h-16 mx-auto mb-4" />
              <p className="text-neutral-500 text-sm">Nexus Breakroom</p>
              <p className="text-neutral-600 text-xs">Coming Soon</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default InvestorDashboard;