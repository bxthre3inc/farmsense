
import React, { useState, useEffect, useRef } from 'react';
import { Zap, MessageSquare, Plus, Trash2, RotateCcw, Brain, ChefHat } from 'lucide-react';

interface Ingredient {
    id: string;
    name: string;
    type: 'base' | 'additive' | 'topping' | 'flavor';
    color: string;
    description: string;
}

const INGREDIENTS: Ingredient[] = [
    { id: '1', name: 'Ethiopian Sidamo', type: 'base', color: '#3d2b1f', description: 'Light roast, berry notes' },
    { id: '2', name: 'Nitro Cold Brew', type: 'base', color: '#1a1a1a', description: 'Velvety, high caffeine' },
    { id: '3', name: 'Oat Milk', type: 'additive', color: '#f5f5dc', description: 'Creamy, nut-free' },
    { id: '4', name: 'Vanilla Bean', type: 'flavor', color: '#fff9e3', description: 'Madagascar origin' },
    { id: '5', name: 'Lions Mane', type: 'additive', color: '#e8e8e8', description: 'Cognitive enhancement' },
    { id: '6', name: 'Golden Honey', type: 'additive', color: '#ffd700', description: 'Local Monte Vista honey' },
];

export const NexusBreakroom: React.FC = () => {
    const [selectedIngredients, setSelectedIngredients] = useState<Ingredient[]>([]);
    const [messages, setMessages] = useState<{ role: 'user' | 'ai', text: string }[]>([
        { role: 'ai', text: 'Welcome to the Nexus. I am your Meal Architect. What are we building today?' }
    ]);
    const [input, setInput] = useState('');
    const [isPrep, setIsPrep] = useState(false);
    const [progress, setProgress] = useState(0);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const newMessages = [...messages, { role: 'user', text: input } as const];
        setMessages(newMessages);
        setInput('');

        // Simulating AI logic
        setTimeout(() => {
            let aiResponse = "Interesting combination. I've added some suggestions to your palette.";
            if (input.toLowerCase().includes('coffee') || input.toLowerCase().includes('caffeine')) {
                aiResponse = "Acknowledged. Focusing on high-performance stimulants. Recommending Nitro Cold Brew base with Lions Mane for neural clarity.";
                addIngredient(INGREDIENTS[1]);
                addIngredient(INGREDIENTS[4]);
            } else if (input.toLowerCase().includes('sweet')) {
                aiResponse = "Deploying sweetness protocols. Recommending Golden Honey and Vanilla Bean.";
                addIngredient(INGREDIENTS[5]);
                addIngredient(INGREDIENTS[3]);
            }
            setMessages(prev => [...prev, { role: 'ai', text: aiResponse }]);
        }, 1000);
    };

    const addIngredient = (ing: Ingredient) => {
        if (selectedIngredients.find(i => i.id === ing.id)) return;
        setSelectedIngredients(prev => [...prev, ing]);
    };

    const removeIngredient = (id: string) => {
        setSelectedIngredients(prev => prev.filter(i => i.id !== id));
    };

    const handleExecute = () => {
        setIsPrep(true);
        let p = 0;
        const interval = setInterval(() => {
            p += 2;
            setProgress(p);
            if (p >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    setIsPrep(false);
                    setProgress(0);
                    setMessages(prev => [...prev, { role: 'ai', text: 'Your custom creation has been materialized in Bay 4. Enjoy your break, Engineer.' }]);
                    setSelectedIngredients([]);
                }, 1000);
            }
        }, 50);
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white flex flex-col font-sans">
            {/* Nav */}
            <header className="p-6 border-b border-white/5 flex justify-between items-center bg-black/50 backdrop-blur-xl sticky top-0 z-50">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center text-black shadow-lg shadow-green-500/20">
                        <Zap className="w-6 h-6" />
                    </div>
                    <div>
                        <h1 className="text-xl font-black uppercase tracking-tighter">Nexus <span className="text-green-500">Breakroom</span></h1>
                        <p className="text-[10px] font-black text-neutral-600 uppercase tracking-widest">Monte Vista HQ • Automated Hospitality</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <div className="hidden md:flex flex-col items-end">
                        <span className="text-[10px] font-black text-neutral-500 uppercase">System Status</span>
                        <div className="flex items-center gap-2">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            <span className="text-xs font-bold">Kitchen Online</span>
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-7xl mx-auto w-full p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">
                {/* AI Architect Chat */}
                <div className="lg:col-span-4 bg-neutral-900/50 border border-white/5 rounded-3xl flex flex-col overflow-hidden shadow-2xl">
                    <div className="p-6 border-b border-white/5 bg-neutral-900/80 flex items-center gap-3">
                        <Brain className="w-5 h-5 text-green-500" />
                        <span className="font-black uppercase text-sm tracking-widest text-neutral-400">AI Meal Architect</span>
                    </div>

                    <div ref={scrollRef} className="flex-1 p-6 overflow-auto space-y-4">
                        {messages.map((m, i) => (
                            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] p-4 rounded-2xl text-sm font-medium ${m.role === 'user' ? 'bg-green-500 text-black' : 'bg-neutral-800 text-white border border-white/5'}`}>
                                    {m.text}
                                </div>
                            </div>
                        ))}
                    </div>

                    <form onSubmit={handleSendMessage} className="p-4 bg-black/50 border-t border-white/5">
                        <div className="relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Chat with the Architect..."
                                className="w-full bg-neutral-800 border-none rounded-xl py-4 pl-6 pr-14 text-sm font-bold placeholder:text-neutral-600 focus:ring-2 focus:ring-green-500 transition-all outline-none"
                            />
                            <button type="submit" className="absolute right-2 top-2 p-2 bg-green-500 rounded-lg text-black hover:bg-green-400 transition-colors">
                                <MessageSquare className="w-5 h-5" />
                            </button>
                        </div>
                    </form>
                </div>

                {/* Visual Ingredient Builder */}
                <div className="lg:col-span-8 space-y-6 flex flex-col">
                    <div className="flex-1 bg-neutral-900/50 border border-white/5 rounded-3xl p-8 flex flex-col relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent pointer-events-none" />

                        <div className="flex justify-between items-start mb-10 relative z-10">
                            <div>
                                <h3 className="text-3xl font-black tracking-tight">Active <span className="text-green-500">Materialization</span></h3>
                                <p className="text-neutral-500 font-bold text-sm">Visually combining ingredients for materialization bay.</p>
                            </div>
                            {selectedIngredients.length > 0 && (
                                <button onClick={() => setSelectedIngredients([])} className="p-2 bg-neutral-800 hover:bg-rose-500/20 text-neutral-400 hover:text-rose-500 rounded-xl transition-all">
                                    <RotateCcw className="w-5 h-5" />
                                </button>
                            )}
                        </div>

                        <div className="flex-1 flex items-center justify-center gap-6 flex-wrap relative z-10">
                            {selectedIngredients.length === 0 ? (
                                <div className="text-center space-y-4 opacity-20 group-hover:opacity-40 transition-opacity">
                                    <ChefHat className="w-20 h-20 mx-auto" />
                                    <p className="text-lg font-black uppercase tracking-widest">Awaiting Recipe Data</p>
                                </div>
                            ) : (
                                selectedIngredients.map((ing, i) => (
                                    <div key={ing.id} className="animate-in zoom-in duration-300 relative">
                                        <div
                                            className="w-24 h-24 rounded-full flex flex-col items-center justify-center border-4 border-white/10 shadow-2xl relative overflow-hidden"
                                            style={{ backgroundColor: ing.color + '40', borderColor: ing.color }}
                                        >
                                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                                            <div className="relative z-10 text-[10px] font-black uppercase text-center px-2">{ing.name}</div>
                                        </div>
                                        <button
                                            onClick={() => removeIngredient(ing.id)}
                                            className="absolute -top-2 -right-2 bg-rose-500 text-white p-1.5 rounded-full shadow-lg hover:scale-110 transition-transform"
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                        {i < selectedIngredients.length - 1 && (
                                            <div className="absolute top-1/2 -right-6 w-6 h-px bg-neutral-800" />
                                        )}
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Execution Bar */}
                        <div className="mt-10 relative z-10">
                            {isPrep ? (
                                <div className="space-y-4">
                                    <div className="flex justify-between text-xs font-black uppercase text-green-500 tracking-widest animate-pulse">
                                        <span>Materializing Creation...</span>
                                        <span>{progress}%</span>
                                    </div>
                                    <div className="h-4 bg-neutral-800 rounded-full overflow-hidden p-1 border border-white/5">
                                        <div
                                            className="h-full bg-green-500 rounded-full transition-all duration-300 shadow-[0_0_20px_rgba(34,197,94,0.5)]"
                                            style={{ width: `${progress}%` }}
                                        />
                                    </div>
                                </div>
                            ) : (
                                <button
                                    disabled={selectedIngredients.length === 0}
                                    onClick={handleExecute}
                                    className={`w-full py-6 rounded-2xl font-black text-xl uppercase tracking-tighter transition-all flex items-center justify-center gap-3 shadow-2xl ${selectedIngredients.length > 0 ? 'bg-green-500 text-black shadow-green-500/20 hover:scale-[1.01] active:scale-[0.99]' : 'bg-neutral-800 text-neutral-600 cursor-not-allowed'}`}
                                >
                                    <Zap className="w-6 h-6" /> Materialize Recipe
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Ingredient Palette */}
                    <div className="bg-neutral-900/50 border border-white/5 rounded-3xl p-6">
                        <div className="text-[10px] font-black uppercase text-neutral-500 tracking-widest mb-6">Ingredient Palette</div>
                        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                            {INGREDIENTS.map(ing => (
                                <button
                                    key={ing.id}
                                    onClick={() => addIngredient(ing)}
                                    className={`p-4 rounded-2xl border transition-all text-left flex flex-col justify-between h-28 ${selectedIngredients.find(i => i.id === ing.id) ? 'bg-green-500 border-green-500 text-black' : 'bg-neutral-800/40 border-white/5 hover:border-green-500/40 group'}`}
                                >
                                    <div className="flex justify-between items-start w-full">
                                        <Plus className={`w-4 h-4 ${selectedIngredients.find(i => i.id === ing.id) ? 'text-black' : 'text-neutral-500 group-hover:text-green-500'}`} />
                                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: ing.color }} />
                                    </div>
                                    <div className="text-[10px] font-black uppercase leading-tight line-clamp-2">{ing.name}</div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};
