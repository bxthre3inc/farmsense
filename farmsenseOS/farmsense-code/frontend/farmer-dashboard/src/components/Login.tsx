
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
        <div className="flex items-center justify-center min-h-screen bg-green-50 p-4">
            <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full border border-green-100">
                <div className="text-center mb-8">
                    <span className="text-5xl mb-4 block">🌱</span>
                    <h2 className="text-3xl font-bold text-green-800">Welcome to FarmSense</h2>
                    <p className="text-gray-500 mt-2">Precision Agriculture Platform</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            API Access Key
                        </label>
                        <input
                            type="password"
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                            placeholder="Enter your API key..."
                            required
                        />
                        {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-green-700 hover:bg-green-800 text-white font-bold py-3 rounded-lg shadow-md hover:shadow-lg transition-all transform active:scale-[0.98]"
                    >
                        Enter Dashboard
                    </button>
                </form>

                <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                    <p className="text-xs text-gray-400 font-medium uppercase tracking-wider mb-2">Demo Credentials</p>
                    <div className="flex flex-col gap-1 text-xs text-gray-500">
                        <code>Farmer: demo-farmer-key</code>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
