
import React, { useState, useEffect } from 'react';
import { ScrollText, CheckCircle, Clock, AlertTriangle, LogOut, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Login from './components/Login';
import SupportLetters from './components/SupportLetters';
import SignLetter from './components/SignLetter';
import { getApiKey, removeApiKey, api } from './services/api';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [impact, setImpact] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    // Simple routing check
    const query = new URLSearchParams(window.location.search);
    const signLetterId = query.get('sign');

    useEffect(() => {
        const auth = !!getApiKey();
        setIsAuthenticated(auth);
        if (auth && !signLetterId) {
            fetchImpact();
        }
    }, [signLetterId]);

    const fetchImpact = async () => {
        setLoading(true);
        try {
            const data = await api.getGrantImpact('FS-2025-X82');
            setImpact(data);
        } catch (error) {
            console.error('Failed to fetch impact:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        removeApiKey();
        setIsAuthenticated(false);
    };

    if (signLetterId) {
        return <SignLetter letterId={signLetterId} />;
    }

    if (!isAuthenticated) {
        return <Login onLogin={() => {
            setIsAuthenticated(true);
            fetchImpact();
        }} />;
    }

    const impactData = impact ? [
        { name: 'Water Saved', value: impact.water_saved_m3, unit: 'm³' },
        { name: 'Yield Gain', value: impact.yield_gain_pct * 100, unit: '%' },
        { name: 'C02 Redux', value: impact.carbon_offset_tons, unit: 'ton' },
        { name: 'Sustainability', value: impact.sustainability_score, unit: 'score' },
    ] : [];

    return (
        <div className="min-h-screen bg-stone-50 text-stone-900 font-serif">
            <header className="bg-white border-b border-stone-200 shadow-sm">
                <div className="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="bg-orange-700 p-2 rounded-md">
                            <ScrollText className="text-white w-6 h-6" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-stone-800 tracking-tight">Grant Oversight</h1>
                            <p className="text-xs text-stone-500 uppercase tracking-widest font-sans">Federal Dept. of Agriculture</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-6 font-sans">
                        <div className="text-sm text-stone-500">
                            Grant ID: <span className="font-mono text-stone-900 font-bold">FS-2025-X82</span>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="text-stone-400 hover:text-red-700 transition-colors"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto w-full px-8 py-10 font-sans">
                <div className="flex justify-between items-center mb-12">
                    <h2 className="text-2xl font-bold text-stone-800 font-serif">Financial & Impact Status</h2>
                    <button onClick={fetchImpact} className="text-stone-500 hover:text-stone-800 transition-colors">
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div className="bg-white p-6 rounded-lg shadow-sm border-t-4 border-green-600">
                        <div className="flex items-center gap-2 mb-2 text-green-700 font-semibold">
                            <CheckCircle className="w-5 h-5" /> Disbursement Status
                        </div>
                        <p className="text-3xl font-bold text-stone-900">$2.4M</p>
                        <p className="text-sm text-stone-500 mt-2">FY2025 Grant Funds</p>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border-t-4 border-blue-600">
                        <div className="flex items-center gap-2 mb-2 text-blue-700 font-semibold">
                            <Clock className="w-5 h-5" /> Reported Since
                        </div>
                        <p className="text-3xl font-bold text-stone-900">
                            {impact ? impact.reporting_period_days : '---'} Days
                        </p>
                        <p className="text-sm text-stone-500 mt-2">Active Data Pipeline</p>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border-t-4 border-yellow-500">
                        <div className="flex items-center gap-2 mb-2 text-yellow-700 font-semibold">
                            <AlertTriangle className="w-5 h-5" /> Data Integrity
                        </div>
                        <p className="text-3xl font-bold text-stone-900">100%</p>
                        <p className="text-sm text-stone-500 mt-2">Verified via Blockchain</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                    {/* Impact Report */}
                    <div className="bg-white p-8 rounded-lg shadow-sm border border-stone-100">
                        <h2 className="text-xl font-bold text-stone-800 mb-6 font-serif">Environmental Impact</h2>
                        <div className="h-80 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={impactData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                    <XAxis type="number" />
                                    <YAxis dataKey="name" type="category" width={100} />
                                    <Tooltip />
                                    <Bar dataKey="value" fill="#c2410c" radius={[0, 4, 4, 0]} barSize={20} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Support Letters */}
                    <SupportLetters />
                </div>

                {/* Audit Submissions */}
                <div className="mt-10 bg-white p-8 rounded-lg shadow-sm border border-stone-100">
                    <h2 className="text-xl font-bold text-stone-800 mb-6 font-serif">Recent Audit Submissions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {impact?.audit_log?.map((log: any, idx: number) => (
                            <div key={idx} className="flex justify-between items-center p-4 border border-stone-100 rounded-md hover:bg-stone-50 transition-colors">
                                <div>
                                    <p className="font-semibold text-stone-800">{log.event}</p>
                                    <p className="text-xs text-stone-500">{log.timestamp}</p>
                                </div>
                                <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full uppercase">
                                    {log.status}
                                </span>
                            </div>
                        )) || <p className="text-stone-400 italic font-sans text-sm">No recent logs.</p>}
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
