
import React from 'react';
import { Building2, Layers, Wrench, Shield, ChevronRight, CheckCircle2, Circle } from 'lucide-react';

const MILESTONES = [
    {
        id: 1,
        name: "Modular Manufacturing Floor",
        description: "Automated assembly line for high-density subterranean node production.",
        status: "complete",
        icon: <Layers className="w-6 h-6" />,
        impact: "Increases production capacity by 400%"
    },
    {
        id: 2,
        name: "Engineering R&D Tunnels",
        description: "Specialized subterranean testing facility for next-gen robots.",
        status: "in-progress",
        icon: <Shield className="w-6 h-6" />,
        impact: "Validates hardware-agnostic robotics IP"
    },
    {
        id: 3,
        name: "Mechanic Support Garage",
        description: "High-torque facility for heavy ag-robotics maintenance.",
        status: "pending",
        icon: <Wrench className="w-6 h-6" />,
        impact: "Secures enterprise uptime SLAs"
    },
    {
        id: 4,
        name: "Nexus Hospitality Center",
        description: "AI-driven automated breakroom and social nexus.",
        status: "pending",
        icon: <Building2 className="w-6 h-6" />,
        impact: "Engineering retention and wow-factor"
    }
];

export const HQMilestones: React.FC = () => {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h3 className="text-2xl font-black text-white">Monte Vista HQ <span className="text-green-500">Milestones</span></h3>
                    <p className="text-neutral-500 text-sm font-bold uppercase tracking-widest mt-1">Industrial Build-out Tracking</p>
                </div>
                <div className="text-right">
                    <div className="text-2xl font-black text-white">35%</div>
                    <div className="text-[10px] font-black text-neutral-600 uppercase">Phase 1 Funding Complete</div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {MILESTONES.map(m => (
                    <div key={m.id} className={`p-6 rounded-3xl border transition-all ${m.status === 'complete' ? 'bg-green-500/5 border-green-500/20' : m.status === 'in-progress' ? 'bg-neutral-800 border-green-500/40 shadow-lg shadow-green-500/5' : 'bg-neutral-900/50 border-neutral-800 opacity-60'}`}>
                        <div className="flex justify-between items-start mb-6">
                            <div className={`p-3 rounded-2xl ${m.status === 'complete' || m.status === 'in-progress' ? 'bg-green-500 text-black' : 'bg-neutral-800 text-neutral-500'}`}>
                                {m.icon}
                            </div>
                            {m.status === 'complete' ? (
                                <CheckCircle2 className="w-6 h-6 text-green-500" />
                            ) : m.status === 'in-progress' ? (
                                <div className="text-[10px] font-black px-2 py-1 bg-green-500 text-black rounded-lg uppercase tracking-tighter">Active</div>
                            ) : (
                                <Circle className="w-6 h-6 text-neutral-800" />
                            )}
                        </div>

                        <h4 className="text-xl font-black text-white mb-2">{m.name}</h4>
                        <p className="text-neutral-500 text-sm font-medium mb-6 leading-relaxed">{m.description}</p>

                        <div className="pt-4 border-t border-white/5 flex items-center gap-2">
                            <div className="text-[10px] font-black uppercase text-neutral-600 tracking-widest">Impact:</div>
                            <div className="text-xs font-bold text-neutral-400">{m.impact}</div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-8 bg-neutral-900 rounded-3xl border border-neutral-800 flex flex-col md:flex-row items-center gap-6 justify-between">
                <div className="flex items-center gap-4">
                    <div className="p-4 bg-white/5 rounded-2xl">
                        <Building2 className="w-8 h-8 text-neutral-500" />
                    </div>
                    <div>
                        <div className="text-lg font-black text-white">Strategic Facility Map</div>
                        <div className="text-sm text-neutral-500 font-medium">Download the full architectural blueprints for the Monte Vista campus.</div>
                    </div>
                </div>
                <button className="px-8 py-4 bg-white text-black rounded-2xl font-black flex items-center gap-2 hover:bg-green-500 transition-all active:scale-95">
                    View Blueprint <ChevronRight className="w-5 h-5" />
                </button>
            </div>
        </div>
    );
};
