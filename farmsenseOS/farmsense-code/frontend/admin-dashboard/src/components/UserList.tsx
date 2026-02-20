
import React, { useState, useEffect } from 'react';
import { Users, Shield, Award, RefreshCw, Search, Filter, MoreHorizontal, UserCheck, UserPlus, Mail, Phone, Building2 } from 'lucide-react';
import { api } from '../services/api';
import { UserModal } from './UserModal';

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

export const UserList: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [roleFilter, setRoleFilter] = useState('ALL');
    const [selectedUser, setSelectedUser] = useState<User | null>(null);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const data = await api.getUsers();
            setUsers(data);
            setFilteredUsers(data);
            setError('');
        } catch (err: any) {
            setError(err.message || 'Failed to load users');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    useEffect(() => {
        let result = users;

        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            result = result.filter(u =>
                u.email.toLowerCase().includes(query) ||
                (u.name && u.name.toLowerCase().includes(query)) ||
                (u.organization && u.organization.toLowerCase().includes(query))
            );
        }

        if (roleFilter !== 'ALL') {
            result = result.filter(u => u.role === roleFilter);
        }

        setFilteredUsers(result);
    }, [searchQuery, roleFilter, users]);

    return (
        <div className="p-8 max-w-7xl mx-auto">
            {/* Header Area */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
                <div>
                    <h2 className="text-3xl font-extrabold text-slate-900 flex items-center gap-3">
                        <div className="p-2 bg-indigo-100 rounded-lg text-indigo-600">
                            <Users className="w-8 h-8" />
                        </div>
                        User Relationship Management
                    </h2>
                    <p className="text-slate-500 mt-2 font-medium">Manage stakeholder access, tiers, and regional coordination.</p>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={fetchUsers}
                        className="p-3 bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 rounded-xl transition-all shadow-sm flex items-center gap-2 group"
                        title="Refresh Synchronized Data"
                    >
                        <RefreshCw className={`w-5 h-5 group-hover:rotate-180 transition-transform duration-500 ${loading ? 'animate-spin' : ''}`} />
                        <span className="text-sm font-bold">Sync</span>
                    </button>
                    <button className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all flex items-center gap-2 active:scale-95">
                        <UserPlus className="w-5 h-5" />
                        Add Node User
                    </button>
                </div>
            </div>

            {/* CRM Controls */}
            <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 mb-6 flex flex-col md:flex-row gap-4 items-center">
                <div className="relative flex-1 w-full">
                    <Search className="absolute left-4 top-3.5 w-5 h-5 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search by email, name, or organization..."
                        className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>

                <div className="flex items-center gap-2 w-full md:w-auto">
                    <Filter className="w-5 h-5 text-slate-400 ml-2" />
                    <select
                        className="bg-slate-50 border border-slate-200 text-slate-700 px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500 font-bold text-sm min-w-[140px]"
                        value={roleFilter}
                        onChange={(e) => setRoleFilter(e.target.value)}
                    >
                        <option value="ALL">All Roles</option>
                        <option value="ADMIN">Administrators</option>
                        <option value="FARMER">Farmers</option>
                        <option value="RESEARCHER">Researchers</option>
                        <option value="INVESTOR">Investors</option>
                        <option value="AUDITOR">Auditors</option>
                    </select>
                </div>

                <div className="text-sm font-bold text-slate-400 px-4 border-l border-slate-100 hidden md:block">
                    {filteredUsers.length} Users Found
                </div>
            </div>

            {/* Premium Table */}
            <div className="bg-white shadow-xl shadow-slate-200/50 rounded-2xl overflow-hidden border border-slate-100 relative min-h-[400px]">
                {loading && (
                    <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] flex items-center justify-center z-10 font-bold text-slate-400">
                        <div className="flex flex-col items-center gap-2">
                            <RefreshCw className="w-8 h-8 animate-spin text-indigo-500" />
                            Fetching Vault Data...
                        </div>
                    </div>
                )}

                <table className="min-w-full">
                    <thead>
                        <tr className="bg-slate-50 border-b border-slate-100">
                            <th className="px-8 py-5 text-left text-xs font-extrabold text-slate-400 uppercase tracking-widest">Stakeholder Identity</th>
                            <th className="px-8 py-5 text-left text-xs font-extrabold text-slate-400 uppercase tracking-widest">Role & Tier</th>
                            <th className="px-8 py-5 text-left text-xs font-extrabold text-slate-400 uppercase tracking-widest">Status</th>
                            <th className="px-8 py-5 text-left text-xs font-extrabold text-slate-400 uppercase tracking-widest">Metadata</th>
                            <th className="px-8 py-5 text-right text-xs font-extrabold text-slate-400 uppercase tracking-widest">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filteredUsers.map((user) => (
                            <tr key={user.id} className="hover:bg-indigo-50/30 transition-colors group">
                                <td className="px-8 py-5">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 bg-slate-100 group-hover:bg-indigo-100 rounded-xl flex items-center justify-center text-slate-600 group-hover:text-indigo-600 font-bold transition-colors">
                                            {user.email[0].toUpperCase()}
                                        </div>
                                        <div>
                                            <div className="text-sm font-extrabold text-slate-900">{user.name || 'Anonymous'}</div>
                                            <div className="text-xs font-medium text-slate-400 flex items-center gap-1">
                                                <Mail className="w-3 h-3" /> {user.email}
                                            </div>
                                            {user.organization && (
                                                <div className="text-[10px] font-bold text-indigo-500 mt-1 flex items-center gap-1 uppercase tracking-tighter">
                                                    <Building2 className="w-3 h-3" /> {user.organization}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </td>
                                <td className="px-8 py-5">
                                    <div className="flex flex-col gap-2">
                                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider w-fit
                                            ${user.role === 'ADMIN' ? 'bg-purple-100 text-purple-700 border border-purple-200' :
                                                user.role === 'AUDITOR' ? 'bg-amber-100 text-amber-700 border border-amber-200' :
                                                    'bg-emerald-100 text-emerald-700 border border-emerald-200'}`}>
                                            <Shield className="w-3 h-3" /> {user.role}
                                        </span>
                                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-slate-400 ml-1">
                                            <Award className="w-3 h-3" /> {user.tier}
                                        </span>
                                    </div>
                                </td>
                                <td className="px-8 py-5">
                                    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase
                                        ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-rose-100 text-rose-700'}`}>
                                        <div className={`w-1.5 h-1.5 rounded-full ${user.is_active ? 'bg-green-500 animate-pulse' : 'bg-rose-500'}`} />
                                        {user.is_active ? 'Operational' : 'Restricted'}
                                    </span>
                                </td>
                                <td className="px-8 py-5 whitespace-nowrap">
                                    <div className="text-[10px] space-y-1">
                                        <div className="text-slate-400 font-bold uppercase tracking-tighter">Joined: {new Date(user.created_at).toLocaleDateString()}</div>
                                        <div className="text-slate-500 font-mono">UID: {user.id.substring(0, 8)}</div>
                                    </div>
                                </td>
                                <td className="px-8 py-5 text-right">
                                    <button
                                        onClick={() => setSelectedUser(user)}
                                        className="px-4 py-2 bg-slate-100 hover:bg-slate-900 hover:text-white text-slate-600 rounded-lg text-xs font-black uppercase tracking-widest transition-all active:scale-95"
                                    >
                                        Manage
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {!loading && filteredUsers.length === 0 && (
                    <div className="p-20 flex flex-col items-center justify-center text-slate-400">
                        <Users className="w-16 h-16 opacity-20 mb-4" />
                        <p className="font-bold text-lg">No matching stakeholders found.</p>
                        <p className="text-sm">Try adjusting your filters or search query.</p>
                    </div>
                )}
            </div>

            {selectedUser && (
                <UserModal
                    user={selectedUser}
                    onClose={() => setSelectedUser(null)}
                    onUpdate={() => {
                        setSelectedUser(null);
                        fetchUsers();
                    }}
                />
            )}
        </div>
    );
};
