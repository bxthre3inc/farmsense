
import React, { useState, useEffect } from 'react';
import { PenTool, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { api } from '../services/api';

interface SupportLetter {
    id: string;
    sender_name: string;
    sender_organization: string;
    content: string;
}

const SignLetter: React.FC<{ letterId: string }> = ({ letterId }) => {
    const [letter, setLetter] = useState<SupportLetter | null>(null);
    const [signature, setSignature] = useState('');
    const [status, setStatus] = useState<'loading' | 'signing' | 'success' | 'error'>('loading');
    const [error, setError] = useState('');

    useEffect(() => {
        // In a real app, we'd have a public endpoint to GET letter metadata by ID without auth
        // For this demo, we'll try to fetch it
        const fetchLetter = async () => {
            try {
                // Mocking fetching by ID (which might fail if auth is required on the list endpoint)
                // In the backend I implemented GET /api/v1/grants/{grant_id}/letters
                // I'll assume we can find it or mock it for the demo
                setStatus('signing');
                setLetter({
                    id: letterId,
                    sender_name: 'Dr. Sarah Chen',
                    sender_organization: 'Climate Research Lab',
                    content: 'I am writing to express my enthusiastic support for the FarmSense project. Their innovative approach to soil moisture monitoring is a game-changer for sustainable agriculture...'
                });
            } catch (err) {
                setStatus('error');
                setError('Could not find the support letter request.');
            }
        };
        fetchLetter();
    }, [letterId]);

    const handleSign = async () => {
        if (!signature.trim()) return;
        setStatus('loading');
        try {
            await api.signSupportLetter(letterId, signature);
            setStatus('success');
        } catch (err) {
            setStatus('error');
            setError('Failed to sign the letter. Please try again.');
        }
    };

    if (status === 'success') {
        return (
            <div className="min-h-screen bg-stone-50 flex items-center justify-center p-6 font-serif">
                <div className="bg-white p-10 rounded-2xl shadow-xl max-w-md w-full text-center space-y-6">
                    <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto">
                        <CheckCircle className="w-12 h-12 text-green-600" />
                    </div>
                    <h1 className="text-3xl font-bold text-stone-800">Letter Signed!</h1>
                    <p className="text-stone-600 font-sans">
                        Thank you, <strong>{letter?.sender_name}</strong>. Your letter of support has been successfully signed and sent to the Grant Reviewers for verification.
                    </p>
                    <p className="text-sm text-stone-400 font-sans pt-4">
                        You can close this window now.
                    </p>
                </div>
            </div>
        );
    }

    if (status === 'error') {
        return (
            <div className="min-h-screen bg-stone-50 flex items-center justify-center p-6 font-serif">
                <div className="bg-white p-10 rounded-2xl shadow-xl max-w-md w-full text-center space-y-6">
                    <div className="bg-red-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto">
                        <AlertCircle className="w-12 h-12 text-red-600" />
                    </div>
                    <h1 className="text-3xl font-bold text-stone-800">Error</h1>
                    <p className="text-stone-600 font-sans">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="w-full bg-stone-800 text-white font-bold py-3 rounded-lg hover:bg-stone-900 transition-all font-sans"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-stone-50 flex items-center justify-center p-6 font-serif text-stone-900">
            <div className="bg-white shadow-2xl rounded-2xl max-w-2xl w-full overflow-hidden border border-stone-200">
                <div className="bg-stone-800 p-8 text-white">
                    <div className="flex items-center gap-3 mb-2">
                        <PenTool className="w-6 h-6 text-orange-400" />
                        <h1 className="text-2xl font-bold tracking-tight">Sign Support Letter</h1>
                    </div>
                    <p className="text-stone-400 text-sm font-sans tracking-wide uppercase">FarmSense Grant Initiative</p>
                </div>

                <div className="p-10 space-y-8">
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-stone-500 font-sans text-xs font-bold uppercase tracking-widest">
                            <FileText className="w-3 h-3" /> Letter Content
                        </div>
                        <div className="bg-stone-50 p-6 rounded-xl border border-stone-100 italic text-stone-700 leading-relaxed shadow-inner">
                            "{letter?.content}"
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-8 text-sm border-b border-stone-100 pb-8">
                        <div>
                            <p className="text-stone-400 font-sans text-[10px] font-bold uppercase tracking-widest mb-1">Signer</p>
                            <p className="font-bold">{letter?.sender_name}</p>
                        </div>
                        <div>
                            <p className="text-stone-400 font-sans text-[10px] font-bold uppercase tracking-widest mb-1">Organization</p>
                            <p className="font-bold">{letter?.sender_organization}</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-stone-500 uppercase tracking-widest pl-1 font-sans">
                                Type your full name to sign
                            </label>
                            <input
                                type="text"
                                value={signature}
                                onChange={(e) => setSignature(e.target.value)}
                                placeholder={letter?.sender_name}
                                className="w-full bg-stone-50 border-2 border-stone-200 rounded-xl px-6 py-4 text-xl font-bold text-stone-800 focus:outline-none focus:border-stone-800 transition-all placeholder:text-stone-200"
                            />
                        </div>

                        <button
                            disabled={!signature.trim() || status === 'loading'}
                            onClick={handleSign}
                            className="w-full bg-orange-700 hover:bg-orange-800 disabled:bg-stone-300 text-white font-bold py-4 rounded-xl shadow-lg shadow-orange-200 transition-all flex items-center justify-center gap-2 text-lg font-sans"
                        >
                            {status === 'loading' ? 'Processing...' : <><PenTool className="w-5 h-5" /> Sign Letter</>}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SignLetter;
