
import React, { useRef, useState, useEffect } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { PenTool, X, CheckCircle2, ShieldCheck, Download, Mail, FileText, Activity, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

interface AgreementProps {
    shares: number;
    price: number;
    onSigned: () => void;
    onCancel: () => void;
}

export const SeedAgreementPortal: React.FC<AgreementProps> = ({ shares, price, onSigned, onCancel }) => {
    const sigPad = useRef<any>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [agreed, setAgreed] = useState(false);
    const [step, setStep] = useState(1);

    const total = shares * price;

    const save = async () => {
        if (sigPad.current.isEmpty()) return;
        setIsProcessing(true);
        try {
            const signature = sigPad.current.getTrimmedCanvas().toDataURL('image/png');
            // Mock API call for agreement signing
            // await api.signEquityAgreement(signature);
            setTimeout(() => {
                onSigned();
            }, 1000);
        } catch (error) {
            console.error('Signing failed:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/95 backdrop-blur-md z-[100] flex flex-col items-center justify-center p-4">
            <div className="bg-neutral-900 border border-neutral-800 rounded-3xl w-full max-w-5xl h-[90vh] overflow-hidden flex flex-col shadow-2xl">
                {/* Header */}
                <div className="p-6 bg-neutral-800 border-b border-neutral-700 flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <div className="p-2 bg-green-500 rounded-lg text-black">
                            <ShieldCheck className="w-5 h-5" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white uppercase tracking-tighter">Seed Round Execution</h3>
                            <p className="text-neutral-500 text-xs font-bold uppercase tracking-widest mt-0.5">farmsenseOS - The Deterministic Farming Operating System</p>
                        </div>
                    </div>
                    <button onClick={onCancel} className="p-2 hover:bg-neutral-700 rounded-full transition-colors text-neutral-400">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="flex-1 overflow-auto flex flex-col md:flex-row">
                    {/* Document View */}
                    <div className="flex-1 p-8 md:p-12 bg-white text-slate-800 font-serif overflow-auto">
                        <div className="max-w-2xl mx-auto space-y-8 text-sm">
                            <div className="text-center font-black text-2xl uppercase tracking-tighter border-b-2 border-slate-900 pb-4 mb-10">
                                Stock Purchase Agreement: Seed Round
                            </div>

                            <p className="font-bold">farmsenseOS - The Deterministic Farming Operating System</p>

                            <section className="space-y-4">
                                <h4 className="font-black text-xs uppercase tracking-widest text-slate-400">1. Investment Terms</h4>
                                <p>This Agreement governs the purchase of Common Stock in the Company. The Investor agrees to purchase <span className="underline font-bold text-black">{shares.toLocaleString()}</span> shares at a price of <span className="underline font-bold text-black">${price.toFixed(2)}</span> per share, for a total investment of <span className="underline font-bold text-black">${total.toLocaleString()}</span>.</p>
                            </section>

                            <section className="space-y-4">
                                <h4 className="font-black text-xs uppercase tracking-widest text-slate-400">2. Seed Objectives: Monte Vista Nexus</h4>
                                <p>The proceeds of this Seed Round are specifically earmarked for critical industrial infrastructure:</p>
                                <ul className="list-disc pl-5 space-y-2">
                                    <li><span className="font-bold">Aerial Intelligence:</span> Acquisition of DJI Mavic 3M Multispectral UAV hardware.</li>
                                    <li><span className="font-bold">Monte Vista HQ:</span> Build-out of modular automated manufacturing and subterranean robotics R&D tunnels.</li>
                                    <li><span className="font-bold">R&D Lab:</span> Development of hardware-agnostic, dual-use robotics IP for DoD and industrial sectors.</li>
                                </ul>
                            </section>

                            <section className="space-y-4">
                                <h4 className="font-black text-xs uppercase tracking-widest text-slate-400">3. The 1% Group Provision</h4>
                                <p>The Investor is part of a collective 'Group 100' buy-in representing a combined 1.0% equity stake. Shares are issued on a price-increment curve to reward early stakeholders.</p>
                            </section>

                            <section className="space-y-4">
                                <h4 className="font-black text-xs uppercase tracking-widest text-slate-400">4. Digital Handshake</h4>
                                <p>This instrument is executed digitally. The resulting signature hash shall be legally binding and recorded in the farmsenseOS governance vault.</p>
                            </section>

                            <div className="h-40 border-t-2 border-slate-100 flex items-center justify-center text-slate-200">
                                [Final Execution Block Below]
                            </div>
                        </div>
                    </div>

                    {/* Signature Panel */}
                    <div className="w-full md:w-[400px] bg-neutral-900 p-8 flex flex-col gap-8 border-l border-neutral-800">
                        <div className="space-y-2 text-center md:text-left">
                            <h4 className="text-xl font-black text-white">Attest & Sign</h4>
                            <p className="text-neutral-500 text-sm">Review the agreement above and provide your secure handwritten signature.</p>
                        </div>

                        <div className="bg-neutral-950 rounded-2xl border-2 border-dashed border-neutral-800 overflow-hidden relative group aspect-video">
                            <SignatureCanvas
                                ref={sigPad}
                                penColor="white"
                                canvasProps={{ width: 336, height: 200, className: 'sigCanvas' }}
                            />
                            <button
                                onClick={() => sigPad.current.clear()}
                                className="absolute right-3 top-3 p-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-neutral-400 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </div>

                        <div className="space-y-4 py-4">
                            <div className="flex justify-between items-center bg-neutral-800/50 p-4 rounded-xl border border-neutral-700">
                                <div className="text-xs font-bold text-neutral-400 uppercase">Total Commitment</div>
                                <div className="text-lg font-black text-green-500">${total.toLocaleString()}</div>
                            </div>

                            <label className="flex items-start gap-3 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={agreed}
                                    onChange={(e) => setAgreed(e.target.checked)}
                                    className="mt-1 w-4 h-4 rounded border-neutral-700 bg-neutral-950 text-green-500 focus:ring-green-500"
                                />
                                <span className="text-[10px] text-neutral-500 font-bold uppercase tracking-wider leading-relaxed group-hover:text-neutral-400">
                                    I hereby confirm my intent to join farmsenseOS as a Seed Round Stakeholder and agree to the terms of the Stock Purchase Agreement as outlined.
                                </span>
                            </label>
                        </div>

                        <button
                            disabled={!agreed || isProcessing}
                            onClick={save}
                            className={`w-full py-5 rounded-2xl font-black text-lg transition-all shadow-xl flex items-center justify-center gap-3 active:scale-[0.98] ${agreed ? 'bg-green-500 text-black hover:bg-green-400' : 'bg-neutral-800 text-neutral-600 cursor-not-allowed'}`}
                        >
                            {isProcessing ? <RefreshCw className="animate-spin" /> : <PenTool className="w-5 h-5" />}
                            Execute Agreement
                        </button>

                        <div className="mt-auto flex justify-center gap-6 text-neutral-700">
                            <FileText className="w-4 h-4" />
                            <Activity className="w-4 h-4" />
                            <Download className="w-4 h-4" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
