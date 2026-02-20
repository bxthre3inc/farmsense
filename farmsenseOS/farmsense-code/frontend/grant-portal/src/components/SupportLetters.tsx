
import React, { useState, useEffect } from 'react';
import { FileText, Plus, CheckCircle, Clock, Send, X, ExternalLink } from 'lucide-react';
import { api } from '../services/api';

interface SupportLetter {
    id: string;
    grant_id: string;
    sender_name: string;
    sender_email: string;
    sender_organization: string;
    content: string;
    status: 'pending' | 'signed' | 'verified';
    created_at: string;
    signed_at?: string;
    verified_at?: string;
}

const SupportLetters: React.FC = () => {
    const [letters, setLetters] = useState<SupportLetter[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [loading, setLoading] = useState(false);
    const [newLetter, setNewLetter] = useState({
        sender_name: '',
        sender_email: '',
        sender_organization: '',
        content: ''
    });

    const fetchLetters = async () => {
        try {
            const data = await api.getSupportLetters('grant_001'); // Mocking grant_id for now
            setLetters(data);
        } catch (error) {
            console.error('Failed to fetch letters:', error);
        }
    };

    useEffect(() => {
        fetchLetters();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.requestSupportLetter('grant_001', {
                ...newLetter,
                grant_id: 'grant_001'
            });
            setShowModal(false);
            setNewLetter({ sender_name: '', sender_email: '', sender_organization: '', content: '' });
            fetchLetters();
        } catch (error) {
            console.error('Failed to request letter:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleVerify = async (id: string) => {
        try {
            await api.verifySupportLetter(id);
            fetchLetters();
        } catch (error) {
            console.error('Failed to verify letter:', error);
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 h-full">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <FileText className="w-6 h-6 text-indigo-600" />
                    <h2 className="text-xl font-bold text-gray-800">Letters of Support</h2>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                >
                    <Plus className="w-4 h-4" /> Request Letter
                </button>
            </div>

            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                {letters.length === 0 ? (
                    <div className="text-center py-10 text-gray-400">
                        <Send className="w-12 h-12 mx-auto mb-3 opacity-20" />
                        <p>No support letters requested yet.</p>
                    </div>
                ) : (
                    letters.map((letter) => (
                        <div key={letter.id} className="p-4 rounded-lg border border-gray-100 bg-gray-50 flex flex-col gap-3">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h3 className="font-bold text-gray-800">{letter.sender_name}</h3>
                                    <p className="text-xs text-gray-500">{letter.sender_organization}</p>
                                    <p className="text-[10px] text-gray-400">{letter.sender_email}</p>
                                </div>
                                <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${letter.status === 'verified' ? 'bg-green-100 text-green-700' :
                                        letter.status === 'signed' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'
                                    }`}>
                                    {letter.status === 'verified' ? <CheckCircle className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                                    {letter.status}
                                </div>
                            </div>

                            <div className="text-sm text-gray-600 line-clamp-2 italic">
                                "{letter.content}"
                            </div>

                            <div className="flex items-center justify-between pt-2 border-t border-gray-200 mt-1">
                                <span className="text-[10px] text-gray-400">
                                    {new Date(letter.created_at).toLocaleDateString()}
                                </span>
                                <div className="flex gap-2">
                                    {letter.status === 'signed' && (
                                        <button
                                            onClick={() => handleVerify(letter.id)}
                                            className="text-[10px] font-bold text-green-600 hover:underline"
                                        >
                                            Verify Signature
                                        </button>
                                    )}
                                    <button className="text-[10px] font-bold text-indigo-600 hover:underline flex items-center gap-1">
                                        <ExternalLink className="w-3 h-3" /> View Detail
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="p-6 border-b border-gray-100 flex items-center justify-between">
                            <h3 className="text-lg font-bold text-gray-800">Request Support Letter</h3>
                            <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-6 h-6" />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Full Name</label>
                                    <input
                                        required
                                        type="text"
                                        value={newLetter.sender_name}
                                        onChange={(e) => setNewLetter({ ...newLetter, sender_name: e.target.value })}
                                        placeholder="John Doe"
                                        className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                                    />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Email Address</label>
                                    <input
                                        required
                                        type="email"
                                        value={newLetter.sender_email}
                                        onChange={(e) => setNewLetter({ ...newLetter, sender_email: e.target.value })}
                                        placeholder="john@organization.com"
                                        className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                                    />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Organization</label>
                                <input
                                    type="text"
                                    value={newLetter.sender_organization}
                                    onChange={(e) => setNewLetter({ ...newLetter, sender_organization: e.target.value })}
                                    placeholder="Green Earth Foundation"
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Letter Content (Unsigned)</label>
                                <textarea
                                    required
                                    rows={4}
                                    value={newLetter.content}
                                    onChange={(e) => setNewLetter({ ...newLetter, content: e.target.value })}
                                    placeholder="We fully support the FarmSense initiative because..."
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-none"
                                />
                            </div>
                            <div className="pt-4 flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold py-2 rounded-lg transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 rounded-lg shadow-lg shadow-indigo-200 transition-all flex items-center justify-center gap-2"
                                >
                                    {loading ? 'Sending...' : <><Send className="w-4 h-4" /> Send Request</>}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SupportLetters;
