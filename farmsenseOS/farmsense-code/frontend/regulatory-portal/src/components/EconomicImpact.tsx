
import React from 'react';
import { TrendingUp, Award, Shield, Landmark, Scale, ArrowUpRight } from 'lucide-react';

export const EconomicImpact = () => {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* High Level Financials */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 rounded-2xl p-8 border border-white/10 shadow-xl relative overflow-hidden">
                    <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 rounded-full blur-3xl"></div>
                    <p className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-2">Blended Enterprise Value</p>
                    <p className="text-5xl font-black text-white">$21.23M</p>
                    <div className="mt-4 flex items-center gap-2 text-emerald-400 text-sm font-bold">
                        <ArrowUpRight className="w-4 h-4" /> +240% Growth (2026E)
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
                    <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-2">Intellectual Property Portfolio</p>
                    <p className="text-4xl font-black text-slate-800">$6.5M</p>
                    <p className="text-xs text-slate-400 mt-2 italic">Valued across 5 Provisional Patent Claims</p>
                </div>

                <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
                    <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-2">Grant Multiplier (ROI)</p>
                    <p className="text-4xl font-black text-blue-600">62.0x</p>
                    <p className="text-xs text-slate-400 mt-2 font-medium">Value generated per dollar of state subsidy</p>
                </div>
            </div>

            {/* Patent Deep Dive */}
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                    <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-blue-600" /> Intellectual Property Audit (Pending)
                    </h3>
                    <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-3 py-1 rounded-full uppercase">Priority State: ACTIVE</span>
                </div>
                <div className="p-0 overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50/80 text-[10px] uppercase tracking-wider text-slate-500 font-bold border-b border-slate-100">
                            <tr>
                                <th className="px-6 py-4">Innovation Claim</th>
                                <th className="px-6 py-4 text-right">Value Basis</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 text-sm">
                            <tr>
                                <td className="px-6 py-4">
                                    <p className="font-bold text-slate-800">GridRenderer Synthesis</p>
                                    <p className="text-xs text-slate-500">80% reduction in hardware CapEx needs</p>
                                </td>
                                <td className="px-6 py-4 text-right font-mono text-slate-600">$1,800,000</td>
                            </tr>
                            <tr>
                                <td className="px-6 py-4">
                                    <p className="font-bold text-slate-800">Deterministic Audit Logs</p>
                                    <p className="text-xs text-slate-500">Non-repudiable legal provenance chain</p>
                                </td>
                                <td className="px-6 py-4 text-right font-mono text-slate-600">$1,250,000</td>
                            </tr>
                            <tr>
                                <td className="px-6 py-4">
                                    <p className="font-bold text-slate-800">AdaptiveRecalc Engine</p>
                                    <p className="text-xs text-slate-500">Real-time asynchronous field calibration</p>
                                </td>
                                <td className="px-6 py-4 text-right font-mono text-slate-600">$950,000</td>
                            </tr>
                            <tr>
                                <td className="px-6 py-4 font-bold text-blue-600">Total IP Equity (Pending)</td>
                                <td className="px-6 py-4 text-right font-black text-slate-800">$6,500,000</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Strategic Impact Chart (Simulated) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6 border-b pb-4">Revenue & Adoption Velocity</h4>
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs font-bold text-slate-500">
                                <span>YEAR 1: 400 FARMS (Subsidized)</span>
                                <span className="text-slate-800">$1.2M ARR</span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                                <div className="bg-blue-500 h-full w-[10%]"></div>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs font-bold text-slate-500">
                                <span>YEAR 5: 15,000 FARMS (Projected)</span>
                                <span className="text-slate-800">$45.0M ARR</span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden shadow-inner">
                                <div className="bg-blue-600 h-full w-[85%]"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-50 rounded-2xl border border-slate-100 p-8 flex flex-col justify-center gap-6">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-white rounded-xl shadow-sm">
                            <Landmark className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-xs font-bold text-slate-500 uppercase">Institutional Grade</p>
                            <p className="text-slate-800 text-sm font-medium italic">"The grant-subsidized model has accelerated market penetration by 240% vs. unsubsidized private rollouts."</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
