
import React, { useState, useEffect } from 'react';
import { Microscope, Database, Download, LogOut, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Login from './components/Login';
import { getApiKey, removeApiKey, api } from './services/api';

const mockChartData = [
    { name: 'Jan', nutrientA: 4000, nutrientB: 2400 },
    { name: 'Feb', nutrientA: 3000, nutrientB: 1398 },
    { name: 'Mar', nutrientA: 2000, nutrientB: 9800 },
    { name: 'Apr', nutrientA: 2780, nutrientB: 3908 },
    { name: 'May', nutrientA: 1890, nutrientB: 4800 },
    { name: 'Jun', nutrientA: 2390, nutrientB: 3800 },
    { name: 'Jul', nutrientA: 3490, nutrientB: 4300 },
];

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [datasets, setDatasets] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const auth = !!getApiKey();
        setIsAuthenticated(auth);
        if (auth) {
            fetchDatasets();
        }
    }, []);

    const fetchDatasets = async () => {
        setLoading(true);
        try {
            const data = await api.getDatasets();
            setDatasets(data);
        } catch (error) {
            console.error('Failed to fetch datasets:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        removeApiKey();
        setIsAuthenticated(false);
    };

    if (!isAuthenticated) {
        return <Login onLogin={() => {
            setIsAuthenticated(true);
            fetchDatasets();
        }} />;
    }

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col">
            <header className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <div className="bg-purple-600 p-2 rounded-lg">
                                <Microscope className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-slate-800">CSU Research Portal</h1>
                                <p className="text-xs text-slate-500">Agricultural Data Analysis</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-6">
                            <div className="flex items-center gap-4">
                                <button className="flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-lg text-sm font-medium hover:bg-purple-100">
                                    <Database className="w-4 h-4" /> Lab Connect
                                </button>
                                <button className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800">
                                    <Download className="w-4 h-4" /> Export All
                                </button>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="text-gray-400 hover:text-red-500 transition-colors"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">Soil Nutrient Trends</h3>
                            <div className="h-80 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={mockChartData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Line type="monotone" dataKey="nutrientA" stroke="#8884d8" activeDot={{ r: 8 }} />
                                        <Line type="monotone" dataKey="nutrientB" stroke="#82ca9d" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                    <div className="space-y-6">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-semibold text-gray-800">Latest Datasets</h3>
                                <button onClick={fetchDatasets} className="text-purple-600 hover:text-purple-800">
                                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                                </button>
                            </div>
                            <ul className="space-y-3">
                                {datasets.map(ds => (
                                    <li key={ds.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer border border-transparent hover:border-purple-200 transition-all">
                                        <div className="flex items-center gap-3">
                                            <Database className={`w-4 h-4 ${ds.type === 'satellite' ? 'text-blue-400' : 'text-purple-400'}`} />
                                            <div>
                                                <span className="text-sm font-medium text-gray-700 block">{ds.name}</span>
                                                <span className="text-[10px] text-gray-400 uppercase tracking-tighter">{ds.type} • {ds.size_mb}MB</span>
                                            </div>
                                        </div>
                                        <Download className="w-4 h-4 text-gray-400" />
                                    </li>
                                ))}
                                {!loading && datasets.length === 0 && (
                                    <p className="text-gray-400 text-sm text-center py-4 italic">No datasets available.</p>
                                )}
                            </ul>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
