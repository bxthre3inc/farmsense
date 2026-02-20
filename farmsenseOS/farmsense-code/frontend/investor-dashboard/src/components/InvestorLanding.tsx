
import React, { useState, useEffect } from 'react';
import { ShieldCheck, TrendingUp, Users, Lock, ChevronRight, Activity, Building2, Zap, Award, Mail } from 'lucide-react';
import { api } from '../services/api';

export const InvestorLanding: React.FC<{ onExplore: () => void }> = ({ onExplore }) => {
    const [publicLetters, setPublicLetters] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // In a real app, fetch from /api/v1/public/letters
        setPublicLetters([
            { id: 1, sender_name: "Zack Czernecki", sender_organization: "CSU SLV RC", status: "SIGNED" },
            { id: 2, sender_name: "Regional Ag-Board", sender_organization: "Subdistrict 1", status: "SIGNED" }
        ]);
        setLoading(false);
    }, []);

    return (
        <div className="min-h-screen bg-black text-white selection:bg-green-500 selection:text-black">
            {/* Visual Header / Hero */}
            <div className="relative h-[80vh] overflow-hidden flex items-center justify-center">
                <div className="absolute inset-0 bg-gradient-to-b from-green-500/10 via-black to-black z-0" />
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&q=80&w=2000')] bg-cover bg-center mix-blend-overlay opacity-30" />

                <div className="max-w-5xl mx-auto px-6 relative z-10 text-center space-y-8">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full text-green-500 text-xs font-black uppercase tracking-[0.2em] animate-pulse">
                        <Lock className="w-3 h-3" /> Seed Round Open: Gated Group 100
                    </div>
                    <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-none text-white">
                        farmsense<span className="text-green-500">OS</span>
                        <div className="text-2xl md:text-3xl font-light text-neutral-400 mt-4 tracking-normal">The Deterministic Farming Operating System</div>
                    </h1>
                    <p className="max-w-2xl mx-auto text-neutral-400 text-lg md:text-xl font-medium leading-relaxed">
                        Join the Seed Round. Funding the Monte Vista HQ, ag-robotics manufacturing, and the DJI Mavic 3 Multispectral edge.
                    </p>
                    <div className="flex flex-col md:flex-row items-center justify-center gap-4 pt-10">
                        <button
                            onClick={onExplore}
                            className="w-full md:w-auto px-10 py-5 bg-white text-black rounded-2xl font-black text-lg hover:bg-green-500 transition-all flex items-center justify-center gap-3 shadow-2xl shadow-white/5 active:scale-95"
                        >
                            Enter Investor Vault <ChevronRight className="w-5 h-5" />
                        </button>
                        <a href="#clout" className="w-full md:w-auto px-10 py-5 bg-neutral-900 text-white border border-neutral-700 rounded-2xl font-black text-lg hover:bg-neutral-800 transition-all flex items-center justify-center gap-3 active:scale-95">
                            Review Institutional Clout
                        </a>
                    </div>
                </div>
            </div>

            {/* Wall of Clout */}
            <div id="clout" className="max-w-7xl mx-auto px-6 py-24 border-t border-neutral-900">
                <div className="text-center space-y-4 mb-20">
                    <h2 className="text-4xl font-black">The Wall of <span className="text-green-500">Clout</span></h2>
                    <p className="text-neutral-500 max-w-xl mx-auto font-medium">Verified endorsements from government, research, and institutional partners.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {publicLetters.map(letter => (
                        <div key={letter.id} className="bg-neutral-900 border border-neutral-800 p-8 rounded-3xl hover:border-green-500/40 transition-all group relative overflow-hidden">
                            <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-20 transition-opacity">
                                <Award className="w-24 h-24 text-green-500" />
                            </div>
                            <div className="flex items-center gap-2 text-green-500 font-bold text-[10px] uppercase tracking-widest mb-6">
                                <ShieldCheck className="w-4 h-4" /> Digitally Attested
                            </div>
                            <h4 className="text-xl font-black text-white">{letter.sender_name}</h4>
                            <div className="text-neutral-400 font-bold text-sm underline mb-6">{letter.sender_organization}</div>
                            <p className="text-neutral-500 text-sm italic line-clamp-3">"Formal support for the FarmSense initiative... recognized critical need for soil telemetry..."</p>
                            <div className="mt-8 pt-8 border-t border-neutral-800 flex justify-between items-center">
                                <span className="text-[10px] font-black uppercase text-neutral-600">ID: FS-LOS-{letter.id}00X</span>
                                <span className="text-green-500/80 font-black text-[10px] uppercase tracking-tighter">Status: {letter.status}</span>
                            </div>
                        </div>
                    ))}

                    {/* Placeholder for more */}
                    <div className="bg-neutral-900/40 border border-dashed border-neutral-800 p-8 rounded-3xl flex flex-col items-center justify-center text-center opacity-60">
                        <Users className="w-10 h-10 text-neutral-700 mb-4" />
                        <div className="text-neutral-600 font-bold text-sm">Awaiting Final CSU Verification</div>
                    </div>
                </div>
            </div>

            {/* Strategic Pillars */}
            <div className="bg-neutral-900/30 py-24 border-y border-neutral-900">
                <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-20 items-center">
                    <div className="space-y-10">
                        <h3 className="text-5xl font-black tracking-tighter">The Monte Vista <span className="text-green-500">Nexus</span></h3>

                        <div className="space-y-8">
                            <div className="flex gap-6">
                                <div className="p-4 bg-green-500 text-black rounded-2xl h-fit">
                                    <Zap className="w-6 h-6" />
                                </div>
                                <div className="space-y-2">
                                    <h5 className="text-xl font-bold">Multispectral Advantage</h5>
                                    <p className="text-neutral-500 text-sm leading-relaxed">Securing DJI Mavic 3M hardware for HD fallow land analysis—closing enterprise contracts before full deployment.</p>
                                </div>
                            </div>

                            <div className="flex gap-6">
                                <div className="p-4 bg-neutral-800 text-green-500 rounded-2xl h-fit">
                                    <Building2 className="w-6 h-6" />
                                </div>
                                <div className="space-y-2">
                                    <h5 className="text-xl font-bold">R&D Campus</h5>
                                    <p className="text-neutral-500 text-sm leading-relaxed">Modular manufacturing and engineering tunnels for ag-robotics R&D and general tech innovation.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="aspect-square bg-green-500/5 border border-green-500/10 rounded-full absolute -top-10 -left-10 w-full animate-pulse" />
                        <img
                            src="https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&q=80&w=1000"
                            className="rounded-3xl shadow-2xl relative z-10 border border-neutral-800"
                            alt="Robotics Lab"
                        />
                    </div>
                </div>
            </div>

            {/* Footer / Funnel CTA */}
            <footer className="py-20 text-center border-t border-neutral-900">
                <div className="text-neutral-600 text-[10px] font-black uppercase tracking-[0.4em] mb-10 px-6">
                    farmsenseOS - The Deterministic Farming Operating System
                </div>
                <div className="flex flex-col items-center gap-4 text-xs font-bold text-neutral-500">
                    <div className="flex gap-6">
                        <a href="mailto:invest@farmsense.ai" className="hover:text-white transition-colors">Contact Relations</a>
                        <a href="#" className="hover:text-white transition-colors">Legal Disclosures</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};
