
import React, { useState } from 'react';
import { setApiKey } from '../services/api';

interface LoginProps {
    onLogin: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
    const [key, setKey] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (key.trim().length < 5) {
            setError('Please enter a valid API key');
            return;
        }
        setApiKey(key.trim());
        onLogin();
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-purple-50 p-4">
            <div className="bg-white p-8 rounded-xl shadow-xl max-w-md w-full border-b-4 border-purple-600">
                <div className="text-center mb-8">
                    <span className="text-5xl mb-4 block">🔬</span>
                    <h2 className="text-3xl font-bold text-slate-800">Researcher Portal</h2>
                    <p className="text-slate-500 mt-2">CSU Partner Access</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Research Access Key
                        </label>
                        <input
                            type="password"
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                            placeholder="Enter research key..."
                            required
                        />
                        {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg shadow-md transition-all active:scale-[0.98]"
                    >
                        Authenticate
                    </button>
                </form>

                <div className="mt-8 pt-6 border-t border-slate-100 text-center">
                    <p className="text-xs text-slate-400 font-medium uppercase tracking-wider mb-2">Demo Credentials</p>
                    <div className="flex flex-col gap-1 text-xs text-slate-500">
                        <code>Researcher: demo-research-key</code>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
