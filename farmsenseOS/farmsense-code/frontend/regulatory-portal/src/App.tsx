
import React, { useState, useEffect } from 'react';
import { ComplianceList } from './components/ComplianceList';
import { ScientificValidation } from './components/ScientificValidation';
import Login from './components/Login';
import { FileBadge, Search, Bell, LogOut, ShieldCheck, ClipboardList, TrendingUp } from 'lucide-react';
import { EconomicImpact } from './components/EconomicImpact';
import { getApiKey, removeApiKey } from './services/api';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [metrics, setMetrics] = useState<any>(null);
    const [activeView, setActiveView] = useState<'reports' | 'science' | 'economy'>('reports');

    useEffect(() => {
        const auth = !!getApiKey();
        setIsAuthenticated(auth);
        if (auth) {
            fetchMetrics();
        }
    }, []);

    const fetchMetrics = async () => {
        try {
            const data = await api.getMetrics();
            setMetrics(data);
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
        <div className="min-h-screen bg-slate-50 flex flex-col">
            {/* Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <div className="bg-blue-600 p-2 rounded-lg">
                                <FileBadge className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-slate-800">Regulatory Audit Portal</h1>
                                <p className="text-xs text-slate-500">Government Oversight & Compliance</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-6">
                            <div className="relative">
                                <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search reports..."
                                    className="pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                                />
                            </div>
                            <button className="relative p-2 text-gray-400 hover:text-gray-600">
                                <Bell className="w-5 h-5" />
                                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                            </button>
                            <div className="flex items-center gap-3 border-l border-gray-200 pl-6">
                                <div className="text-right">
                                    <p className="text-sm font-medium text-gray-900">Officer Demo</p>
                                    <p className="text-xs text-gray-500">Auditor Session Active</p>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="text-gray-400 hover:text-red-500 transition-colors"
                                    title="Logout"
                                >
                                    <LogOut className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Sub-header Navigation */}
            <div className="bg-white border-b border-gray-200 shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex gap-8 h-12">
                        <button
                            onClick={() => setActiveView('reports')}
                            className={`flex items-center gap-2 px-1 border-b-2 text-sm font-bold transition-all ${activeView === 'reports' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                        >
                            <ClipboardList className="w-4 h-4" /> Compliance Reports
                        </button>
                        <button
                            onClick={() => setActiveView('science')}
                            className={`flex items-center gap-2 px-1 border-b-2 text-sm font-bold transition-all ${activeView === 'science' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                        >
                            <ShieldCheck className="w-4 h-4" /> Scientific Validation
                        </button>
                        <button
                            onClick={() => setActiveView('economy')}
                            className={`flex items-center gap-2 px-1 border-b-2 text-sm font-bold transition-all ${activeView === 'economy' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
                        >
                            <TrendingUp className="w-4 h-4" /> Economic Impact & IP
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                        <p className="text-sm text-gray-500 font-medium">Compliance Rate</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">{metrics ? metrics.compliance_rate_pct + '%' : '--.-%'}</p>
                    </div>
                    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                        <p className="text-sm text-gray-500 font-medium">Critical Violations</p>
                        <p className="text-3xl font-bold text-red-600 mt-2">{metrics ? metrics.critical_violations : '--'}</p>
                    </div>
                    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                        <p className="text-sm text-gray-500 font-medium">Audits This Month</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">{metrics ? metrics.audits_this_month : '---'}</p>
                    </div>
                    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                        <p className="text-sm text-gray-500 font-medium">Total Fields Monitored</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">{metrics ? metrics.total_fields_monitored : '----'}</p>
                    </div>
                </div>

                {activeView === 'reports' ? (
                    <ComplianceList />
                ) : activeView === 'science' ? (
                    <ScientificValidation />
                ) : (
                    <EconomicImpact />
                )}
            </main>
        </div>
    );
}

export default App;
