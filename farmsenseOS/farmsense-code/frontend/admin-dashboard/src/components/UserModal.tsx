
import React, { useState } from 'react';
import { X, Mail, Phone, Building2, Shield, Award, Calendar, CheckCircle, AlertCircle, FileText, Key } from 'lucide-react';
import { api } from '../services/api';

interface User {
    id: string;
    email: string;
    role: string;
    tier: string;
    is_active: boolean;
    name?: string;
    organization?: string;
    phone?: string;
    notes?: string;
    created_at: string;
    last_login?: string;
    api_key: string;
}

interface UserModalProps {
    user: User;
    onClose: () => void;
    onUpdate: () => void;
}

export const UserModal: React.FC<UserModalProps> = ({ user, onClose, onUpdate }) => {
    const [formData, setFormData] = useState({
        name: user.name || '',
        organization: user.organization || '',
        phone: user.phone || '',
        notes: user.notes || '',
        role: user.role,
        tier: user.tier,
        is_active: user.is_active
    });
    const [isSaving, setIsSaving] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await api.updateUser(user.id, formData);
            setSuccess(true);
            setTimeout(() => {
                setSuccess(false);
                onUpdate();
            }, 1500);
        } catch (error) {
            console.error('Update failed:', error);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="bg-slate-800 p-6 text-white flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-indigo-500 rounded-xl flex items-center justify-center text-xl font-bold">
                            {user.email[0].toUpperCase()}
                        </div>
                        <div>
                            <h3 className="text-xl font-bold">{formData.name || 'Anonymous User'}</h3>
                            <p className="text-slate-400 text-sm">{user.email}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-700 rounded-full transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="flex-1 overflow-auto p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* CRM Details */}
                    <div className="md:col-span-2 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Full Name</label>
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                        placeholder="John Doe"
                                    />
                                    <X className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Organization</label>
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={formData.organization}
                                        onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                        placeholder="Farm / Entity Name"
                                    />
                                    <Building2 className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Phone Number</label>
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={formData.phone}
                                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                        placeholder="+1 (555) 000-0000"
                                    />
                                    <Phone className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                                </div>
                            </div>
                            <div className="space-y-1 flex flex-col justify-end">
                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Account Status</label>
                                <button
                                    onClick={() => setFormData({ ...formData, is_active: !formData.is_active })}
                                    className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${formData.is_active ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-red-100 text-red-700 hover:bg-red-200'}`}
                                >
                                    {formData.is_active ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                                    {formData.is_active ? 'Active Account' : 'Deactivated'}
                                </button>
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">CRM Notes & Internal Briefing</label>
                            <div className="relative">
                                <textarea
                                    rows={4}
                                    value={formData.notes}
                                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                    className="w-full p-4 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
                                    placeholder="Add internal notes about this client's field requirements, grant status, or logistics..."
                                />
                                <FileText className="absolute right-3 bottom-3 w-5 h-5 text-slate-300 pointer-events-none" />
                            </div>
                        </div>
                    </div>

                    {/* Meta & Controls */}
                    <div className="space-y-6 bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <div className="space-y-4">
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                                    <Shield className="w-3 h-3" /> System Role
                                </label>
                                <select
                                    value={formData.role}
                                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                                    className="w-full p-2 bg-white border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                                >
                                    <option value="FARMER">Farmer</option>
                                    <option value="AUDITOR">Auditor</option>
                                    <option value="ADMIN">Administrator</option>
                                    <option value="RESEARCHER">Researcher</option>
                                    <option value="INVESTOR">Investor</option>
                                    <option value="REVIEWER">Reviewer</option>
                                </select>
                            </div>

                            <div className="space-y-1">
                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                                    <Award className="w-3 h-3" /> Subscription Tier
                                </label>
                                <select
                                    value={formData.tier}
                                    onChange={(e) => setFormData({ ...formData, tier: e.target.value })}
                                    className="w-full p-2 bg-white border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500"
                                >
                                    <option value="FREE">Free Tier</option>
                                    <option value="BASIC">Basic</option>
                                    <option value="PRO">Pro</option>
                                    <option value="ENTERPRISE">Enterprise</option>
                                </select>
                            </div>
                        </div>

                        <div className="pt-4 border-t border-slate-200 space-y-3">
                            <div className="flex justify-between items-center text-xs">
                                <span className="text-slate-500 font-medium">Created:</span>
                                <span className="text-slate-700 font-bold">{new Date(user.created_at).toLocaleDateString()}</span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                                <span className="text-slate-500 font-medium">Last Login:</span>
                                <span className="text-slate-700 font-bold">{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                                <span className="text-slate-500 font-medium">API Key:</span>
                                <span className="text-slate-400 font-mono">{user.api_key.substring(0, 8)}...</span>
                            </div>
                        </div>

                        <button
                            disabled={isSaving}
                            onClick={handleSave}
                            className={`w-full py-3 rounded-xl font-bold transition-all shadow-lg active:scale-[0.98] ${success ? 'bg-green-500 text-white' : 'bg-indigo-600 text-white hover:bg-indigo-700'}`}
                        >
                            {isSaving ? 'Synchronizing...' : success ? 'Successfully Saved' : 'Commit Changes'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
