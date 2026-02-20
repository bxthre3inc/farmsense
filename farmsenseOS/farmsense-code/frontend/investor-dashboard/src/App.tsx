import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, DollarSign, Activity, LogOut, RefreshCw, Zap } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Login from './components/Login';
import { EquityBuyIn } from './components/EquityBuyIn';
import { InvestorLanding } from './components/InvestorLanding';
import { HQMilestones } from './components/HQMilestones';
import { NexusBreakroom } from './components/NexusBreakroom';
import { getApiKey, removeApiKey, api } from './services/api';

const mockRoiData = [
    { name: 'Q1 2024', value: 1.2 },
    { name: 'Q2 2024', value: 2.5 },
    { name: 'Q3 2024', value: 4.8 },
    { name: 'Q4 2024', value: 6.3 },
    { name: 'Q1 2025', value: 9.1 },
    { name: 'Q2 2025', value: 12.5 },
];

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [showLogin, setShowLogin] = useState(false);
    const [view, setView] = useState<'dashboard' | 'breakroom'>('dashboard');
    const [metrics, setMetrics] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const auth = !!getApiKey();
        setIsAuthenticated(auth);
        if (auth) {
            fetchMetrics();
        }
    }, []);

    const fetchMetrics = async () => {
        setLoading(true);
        try {
            const data = await api.getMetrics();
            setMetrics(data);
        } catch (error) {
            console.error('Failed to fetch metrics:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        removeApiKey();
        setIsAuthenticated(false);
        setShowLogin(false);
    };

    if (!isAuthenticated) {
        if (showLogin) {
            return <Login onLogin={() => {
                setIsAuthenticated(true);
                fetchMetrics();
            }} />;
        }
        return <InvestorLanding onExplore={() => setShowLogin(true)} />;
    }

    return (
        <div className="min-h-screen bg-neutral-900 text-white flex flex-col font-sans">
            <header className="bg-neutral-800 border-b border-neutral-700 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                    <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        <Zap className="text-green-400 w-6 h-6" />
                        farmsenseOS <span className="text-neutral-400 font-light">• Nexus Ops</span>
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
                                onClick={() => setView('breakroom')}
                                className={`text-[10px] font-black uppercase tracking-[0.2em] transition-all ${view === 'breakroom' ? 'text-green-500 border-b-2 border-green-500 pb-1' : 'text-neutral-500 hover:text-white'}`}
                            >
                                Nexus
                            </button>
                        </nav>
                        <button
                            onClick={handleLogout}
                            className="text-neutral-500 hover:text-red-400 transition-colors"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-10 overflow-hidden">
                {view === 'breakroom' ? (
                    <div className="bg-black/40 rounded-[3rem] border border-white/5 overflow-hidden shadow-2xl h-[85vh]">
                        <NexusBreakroom />
                    </div>
                ) : (
                    <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <HQMilestones />

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                            <div className="lg:col-span-2">
                                <EquityBuyIn />
                            </div>
                            <div className="space-y-6">
                                <div className="bg-neutral-800 p-8 rounded-3xl border border-neutral-700">
                                    <h3 className="text-lg font-bold text-white mb-6 uppercase tracking-tighter">Seed Projections</h3>
                                    <div className="h-48 w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={mockRoiData}>
                                                <defs>
                                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <Area type="monotone" dataKey="value" stroke="#10b981" fillOpacity={1} fill="url(#colorValue)" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                    <p className="text-[10px] text-neutral-500 font-bold uppercase mt-4">Estimated Platform Growth Post-HQ Buildout</p>
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
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
