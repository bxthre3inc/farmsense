
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
        <div className="flex items-center justify-center min-h-screen bg-neutral-950 p-4">
            <div className="bg-neutral-900 p-8 rounded-2xl shadow-2xl max-w-md w-full border border-neutral-800">
                <div className="text-center mb-8">
                    <span className="text-5xl mb-4 block">📈</span>
                    <h2 className="text-3xl font-bold text-white tracking-tight">Investor Access</h2>
                    <p className="text-neutral-500 mt-2">FarmSense Executive Dashboard</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-neutral-400 mb-2">
                            Investor API Credential
                        </label>
                        <input
                            type="password"
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                            className="w-full bg-neutral-800 px-4 py-3 rounded-xl border border-neutral-700 text-white focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                            placeholder="Enter investor key..."
                            required
                        />
                        {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-3 rounded-xl shadow-lg transition-all active:scale-[0.98]"
                    >
                        Authenticate
                    </button>
                </form>

                <div className="mt-8 pt-6 border-t border-neutral-800 text-center">
                    <p className="text-xs text-neutral-500 font-medium uppercase tracking-wider mb-2">Demo Credentials</p>
                    <div className="flex flex-col gap-1 text-xs text-neutral-400">
                        <code>Investor: demo-investor-key</code>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
