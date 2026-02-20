
import { ShieldCheck, TrendingUp, Users, Lock, ChevronRight, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { SeedAgreementPortal } from './SeedAgreementPortal';

export const EquityBuyIn: React.FC = () => {
    const [equityStatus, setEquityStatus] = useState<any>({
        claimed_seats: 12,
        current_price: 134.50,
        total_group_interest: "1%"
    });
    const [amount, setAmount] = useState<number>(5000);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showAgreement, setShowAgreement] = useState(false);
    const [success, setSuccess] = useState<any>(null);

    const handleInitiate = () => {
        setShowAgreement(true);
    };

    const handleFinalExecution = async () => {
        setShowAgreement(false);
        setIsProcessing(true);
        try {
            const result = await api.investorBuyIn(amount);
            setSuccess(result);
            setEquityStatus(prev => ({
                ...prev,
                claimed_seats: prev.claimed_seats + 1,
                current_price: prev.current_price * 1.025
            }));
        } catch (error) {
            console.error('Purchase failed:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="bg-neutral-800 rounded-2xl border border-neutral-700 overflow-hidden shadow-2xl">
            <div className="p-8 border-b border-neutral-700 bg-neutral-900/50 flex justify-between items-start">
                <div>
                    <div className="flex items-center gap-2 text-green-400 font-bold text-xs uppercase tracking-widest mb-2">
                        <ShieldCheck className="w-4 h-4" /> Gated Stakeholder Entry
                    </div>
                    <h3 className="text-2xl font-bold text-white">The "Group 100" Equity Pool</h3>
                    <p className="text-neutral-400 text-sm mt-1">Limited to 100 accredited stakeholders for a combined 1% of FarmSense.</p>
                </div>
                <div className="bg-green-500/10 text-green-500 px-4 py-2 rounded-xl border border-green-500/20 text-sm font-black">
                    {100 - equityStatus.claimed_seats} Seats Left
                </div>
            </div>

            <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-10">
                <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700">
                            <label className="text-[10px] font-black uppercase text-neutral-500 tracking-tighter">Current Share Price</label>
                            <div className="text-xl font-bold text-white mt-1">${equityStatus.current_price.toFixed(2)}</div>
                        </div>
                        <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700">
                            <label className="text-[10px] font-black uppercase text-neutral-500 tracking-tighter">Equity Block</label>
                            <div className="text-xl font-bold text-white mt-1">10,000 Shares</div>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <label className="text-xs font-bold text-neutral-400">Investment Amount (USD)</label>
                        <div className="relative">
                            <span className="absolute left-4 top-3.5 text-neutral-500 font-bold">$</span>
                            <input
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(Number(e.target.value))}
                                className="w-full bg-neutral-900 border border-neutral-700 rounded-xl py-4 pl-10 pr-4 text-white font-bold text-xl outline-none focus:ring-2 focus:ring-green-500 transition-all"
                            />
                        </div>
                        <p className="text-[10px] text-neutral-500 font-medium leading-relaxed">
                            <TrendingUp className="w-3 h-3 inline mr-1" />
                            Note: The share price follows a dynamic curve. Every seat claimed increases the next entry price by 2.5% to reflect platform growth.
                        </p>
                    </div>

                    {success ? (
                        <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl flex items-start gap-3 animate-in fade-in slide-in-from-bottom-2">
                            <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0" />
                            <div>
                                <div className="text-green-500 font-bold text-sm">Equity Issued Successfully</div>
                                <div className="text-neutral-400 text-xs mt-1">Issued {success.shares_issued} shares. Ref ID: {success.audit_hash}</div>
                            </div>
                        </div>
                    ) : (
                        <button
                            disabled={isProcessing}
                            onClick={handlePurchase}
                            className="w-full bg-green-500 hover:bg-green-600 text-black py-4 rounded-xl font-black text-lg transition-all shadow-xl shadow-green-500/20 flex items-center justify-center gap-2 active:scale-[0.98]"
                        >
                            {isProcessing ? <RefreshCw className="animate-spin" /> : <TrendingUp className="w-5 h-5" />}
                            Execute Stock Purchase
                        </button>
                    )}
                </div>

                <div className="bg-neutral-900/50 rounded-2xl p-8 border border-neutral-700/50 flex flex-col justify-between">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-neutral-800 rounded-lg text-neutral-400">
                                <Users className="w-5 h-5" />
                            </div>
                            <div>
                                <div className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Active Stakeholders</div>
                                <div className="text-lg font-bold text-white">{equityStatus.claimed_seats} / 100</div>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-neutral-800 rounded-lg text-neutral-400">
                                <Activity className="w-5 h-5" />
                            </div>
                            <div>
                                <div className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Current Valuation Basis</div>
                                <div className="text-lg font-bold text-white">$26.8M</div>
                            </div>
                        </div>
                    </div>

                    <div className="pt-6 border-t border-neutral-800 mt-6">
                        <div className="flex items-center gap-2 text-[10px] text-neutral-500 font-bold mb-4 uppercase">
                            <Lock className="w-3 h-3" /> SEC Accredited Listing required
                        </div>
                        <div className="grid grid-cols-5 gap-1">
                            {[...Array(20)].map((_, i) => (
                                <div key={i} className={`h-1 rounded-full ${i < equityStatus.claimed_seats / 5 ? 'bg-green-500 shadow-lg shadow-green-500/20' : 'bg-neutral-800'}`} />
                            ))}
                        </div>
                        <p className="text-[10px] text-neutral-600 mt-2 font-medium">Progress to 1% Group Saturation</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
