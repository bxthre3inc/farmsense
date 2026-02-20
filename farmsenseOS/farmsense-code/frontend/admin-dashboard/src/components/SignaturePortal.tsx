
import React, { useRef, useState, useEffect } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { FileCheck, PenTool, X, CheckCircle2, ShieldLine, Download, Mail } from 'lucide-react';
import { api } from '../services/api';

export const SignaturePortal: React.FC<{ token: string }> = ({ token }) => {
    const sigPad = useRef<any>(null);
    const [letter, setLetter] = useState<any>(null);
    const [isSigned, setIsSigned] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [agreed, setAgreed] = useState(false);

    useEffect(() => {
        // Mock fetch letter by token
        setLetter({
            id: "los_csu_001",
            sender_name: "Zack Czernecki",
            sender_organization: "CSU SLV RC",
            content: "On behalf of the Colorado State University San Luis Valley Research Center (CSU SLV RC), I am writing to express our formal support for the FarmSense - The Deterministic Farming Operating System initiative...",
            created_at: new Date().toISOString()
        });
    }, [token]);

    const clear = () => sigPad.current.clear();

    const save = async () => {
        if (sigPad.current.isEmpty()) return;
        setIsProcessing(true);
        try {
            const signature = sigPad.current.getTrimmedCanvas().toDataURL('image/png');
            await api.signLetter(token, signature);
            setIsSigned(true);
        } catch (error) {
            console.error('Signing failed:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    if (isSigned) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
                <div className="bg-white rounded-3xl shadow-2xl p-12 max-w-lg w-full text-center border border-slate-100">
                    <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
                        <CheckCircle2 className="w-10 h-10" />
                    </div>
                    <h2 className="text-3xl font-black text-slate-900 mb-2">Signature Verified</h2>
                    <p className="text-slate-500 font-medium mb-8">Your support for Project FarmSense has been recorded and synchronized with the grant audit chain.</p>
                    <div className="bg-slate-50 rounded-xl p-4 text-left border border-slate-100 mb-8">
                        <div className="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-1">Legal Reference</div>
                        <div className="text-xs font-mono text-slate-500 break-all">FS-LOS-{Math.random().toString(36).substring(7).toUpperCase()}</div>
                    </div>
                    <button onClick={() => window.close()} className="w-full bg-slate-900 text-white py-4 rounded-xl font-bold hover:bg-slate-800 transition-all">
                        Exit Portal
                    </button>
                </div>
            </div>
        );
    }

    if (!letter) return <div className="flex items-center justify-center min-h-screen">Loading secure document...</div>;

    return (
        <div className="min-h-screen bg-slate-100 flex flex-col md:flex-row">
            {/* Document Viewer */}
            <div className="flex-1 p-8 md:p-12 overflow-auto">
                <div className="max-w-3xl mx-auto bg-white shadow-2xl rounded-sm p-12 border border-slate-200 min-h-[1000px] relative">
                    <div className="flex justify-between items-start mb-12">
                        <div className="bg-slate-900 text-white px-4 py-2 font-black text-xs uppercase tracking-tighter">Official Instrument</div>
                        <FileCheck className="text-slate-200 w-16 h-16" />
                    </div>

                    <div className="space-y-8 text-slate-800 leading-relaxed font-serif">
                        <div className="text-right text-sm text-slate-400 mb-12">{new Date(letter.created_at).toLocaleDateString()}</div>

                        <div className="font-bold">To the Colorado Water Conservation Board,</div>

                        <div className="whitespace-pre-line text-lg italic text-slate-700">
                            {letter.content}
                        </div>

                        <div className="pt-12">
                            <div className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">Stakeholder Identity</div>
                            <div className="text-xl font-black">{letter.sender_name}</div>
                            <div className="text-slate-500 font-bold underline">{letter.sender_organization}</div>
                        </div>
                    </div>

                    <div className="absolute top-0 left-0 w-full h-1 bg-indigo-600" />
                </div>
            </div>

            {/* Signature Pad Sidebar */}
            <div className="w-full md:w-[450px] bg-white border-l border-slate-200 p-8 shadow-2xl flex flex-col">
                <div className="flex-1 text-center space-y-8">
                    <div className="space-y-2">
                        <h3 className="text-2xl font-black text-slate-900">Authorize Support</h3>
                        <p className="text-slate-500 text-sm">Please provide your handwritten signature below to verify this instrument.</p>
                    </div>

                    <div className="bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 overflow-hidden relative group">
                        <SignatureCanvas
                            ref={sigPad}
                            penColor="black"
                            canvasProps={{ width: 386, height: 250, className: 'sigCanvas' }}
                        />
                        <button
                            onClick={clear}
                            className="absolute right-4 top-4 p-2 bg-white/80 hover:bg-white rounded-lg shadow-sm text-slate-400 hover:text-rose-500 transition-all opacity-0 group-hover:opacity-100"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>

                    <div className="space-y-4 pt-4">
                        <label className="flex items-start gap-3 cursor-pointer group text-left">
                            <input
                                type="checkbox"
                                checked={agreed}
                                onChange={(e) => setAgreed(e.target.checked)}
                                className="mt-1 w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                            />
                            <span className="text-xs text-slate-500 font-medium group-hover:text-slate-700 leading-tight">
                                I confirm that I am the authorized representative of {letter.sender_organization} and this signature constitutes formal institutional support for FarmSense - The Deterministic Farming Operating System.
                            </span>
                        </label>
                    </div>

                    <button
                        disabled={!agreed || isProcessing}
                        onClick={save}
                        className={`w-full py-5 rounded-2xl font-black text-lg transition-all shadow-xl flex items-center justify-center gap-3 active:scale-[0.98] ${agreed ? 'bg-indigo-600 text-white shadow-indigo-200 hover:bg-indigo-700' : 'bg-slate-100 text-slate-400 grayscale cursor-not-allowed'}`}
                    >
                        {isProcessing ? <RefreshCw className="animate-spin" /> : <PenTool className="w-5 h-5" />}
                        Attest & Push Signature
                    </button>
                </div>

                <div className="pt-8 border-t border-slate-100 mt-8 flex justify-center gap-6 grayscale opacity-40">
                    <Download className="w-5 h-5" />
                    <ShieldLine className="w-5 h-5" />
                    <Mail className="w-5 h-5" />
                </div>
            </div>
        </div>
    );
};
