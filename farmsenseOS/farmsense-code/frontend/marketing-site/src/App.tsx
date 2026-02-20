import React, { useState } from 'react';





import { Routes, Route, Link, useLocation } from 'react-router-dom';
import {
    Menu, X, Check, ArrowRight, Shield, Database,
    Layers, Map, BarChart3, Users, Mail, Globe,
    Cpu, Zap, Award
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper for Tailwind classes
function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// --- Components ---

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();

    const navLinks = [
        { name: 'Features', href: '/#features' },
        { name: 'Technology', href: '/#tech' },
        { name: 'Pricing', href: '/pricing' },
        { name: 'About', href: '/about' },
    ];

    return (
        <nav className="glass-nav px-6 py-4 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
                <div className="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center glow-active">
                    <Globe className="text-white w-6 h-6" />
                </div>
                <span className="farmsense-headings text-2xl font-bold text-white tracking-tight">FarmSense</span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-8">
                {navLinks.map((link) => (
                    <a key={link.name} href={link.href} className="text-sm font-medium text-slate-400 hover:text-emerald-400 transition-colors">
                        {link.name}
                    </a>
                ))}
                <button className="glass-button-primary scale-90 px-6">
                    Get Started <ArrowRight className="w-4 h-4" />
                </button>
            </div>

            {/* Mobile Toggle */}
            <button className="md:hidden text-white" onClick={() => setIsOpen(!isOpen)}>
                {isOpen ? <X /> : <Menu />}
            </button>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="absolute top-full left-0 w-full bg-slate-900/95 backdrop-blur-xl p-6 flex flex-col gap-4 md:hidden border-b border-white/10"
                    >
                        {navLinks.map((link) => (
                            <a key={link.name} href={link.href} onClick={() => setIsOpen(false)} className="text-lg font-medium text-slate-300">
                                {link.name}
                            </a>
                        ))}
                        <button className="glass-button-primary w-full mt-4">Get Started</button>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

const Footer = () => (
    <footer className="bg-slate-950 border-t border-white/5 py-16 px-6">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
            <div className="space-y-4">
                <div className="flex items-center gap-2">
                    <Globe className="text-emerald-500 w-6 h-6" />
                    <span className="farmsense-headings text-xl font-bold text-white">FarmSense</span>
                </div>
                <p className="text-slate-500 text-sm leading-relaxed">
                    The global standard in institutional precision agriculture. Fusing ground-truth telemetry with hyper-res satellite intelligence.
                </p>
            </div>
            <div>
                <h4 className="text-white font-bold mb-6">Platform</h4>
                <ul className="space-y-4 text-slate-500 text-sm">
                    <li><a href="#" className="hover:text-emerald-400">Precision Maps</a></li>
                    <li><a href="#" className="hover:text-emerald-400">Sensor Fusion</a></li>
                    <li><a href="#" className="hover:text-emerald-400">Compliance Reporting</a></li>
                    <li><a href="#" className="hover:text-emerald-400">Documentation</a></li>
                </ul>
            </div>
            <div>
                <h4 className="text-white font-bold mb-6">Support</h4>
                <ul className="space-y-4 text-slate-500 text-sm">
                    <li><a href="#" className="hover:text-emerald-400">Help Center</a></li>
                    <li><a href="#" className="hover:text-emerald-400">API Reference</a></li>
                    <li><a href="#" className="hover:text-emerald-400">Community</a></li>
                    <li><a href="#" className="hover:text-emerald-400">Contact Us</a></li>
                </ul>
            </div>
            <div>
                <h4 className="text-white font-bold mb-6">Newsletter</h4>
                <div className="flex gap-2">
                    <input type="email" placeholder="Email" className="glass-input flex-1 py-2" />
                    <button className="bg-emerald-500 text-white p-2 rounded-xl"><Mail className="w-5 h-5" /></button>
                </div>
                <p className="text-slate-600 text-[10px] mt-4 uppercase tracking-widest font-bold">
                    © 2026 FarmSense Inc. All rights reserved.
                </p>
            </div>
        </div>
    </footer>
);

// --- Pages ---

const Home = () => (
    <div className="space-y-24 pb-24">
        {/* Hero */}
        <section className="relative overflow-hidden pt-20 pb-32">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-emerald-500/10 rounded-full blur-[120px] -z-10" />
            <div className="max-w-7xl mx-auto px-6 text-center space-y-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-badge mx-auto"
                >
                    v1.0.0-PRO Now Live
                </motion.div>
                <motion.h1
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="farmsense-headings text-6xl md:text-8xl font-black text-white leading-tight"
                >
                    Precision <span className="text-gradient">Agriculture</span><br />
                    at Institutional Scale.
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-slate-400 text-xl max-w-3xl mx-auto"
                >
                    Hardware-grade accuracy at software-only costs. Fusing Sentinel Constellation data with ground-truth telemetry into a single 1m virtual grid.
                </motion.p>
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="flex flex-wrap items-center justify-center gap-4 py-4"
                >
                    <button className="glass-button-primary px-10 py-5 text-lg">Start Free Trial</button>
                    <button className="glass-button-secondary px-10 py-5 text-lg">Request Demo</button>
                </motion.div>

                {/* Mockup Preview */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5, duration: 1 }}
                    className="relative mt-20 max-w-5xl mx-auto animate-float"
                >
                    <div className="glass-card p-1">
                        <div className="bg-slate-900 rounded-xl overflow-hidden aspect-video relative group">
                            <img
                                src="https://images.unsplash.com/photo-1574943320219-553eb213f72d?q=80&w=2000"
                                className="w-full h-full object-cover opacity-60 grayscale group-hover:grayscale-0 transition-all duration-700"
                                alt="Dashboard Preview"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
                            <div className="absolute bottom-8 left-8 text-left">
                                <div className="glass-badge mb-2">Real-time Map</div>
                                <h3 className="text-2xl font-bold text-white">1m Virtual Sensor Grid</h3>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>

        {/* Features Grid */}
        <section id="features" className="max-w-7xl mx-auto px-6 space-y-16">
            <div className="text-center space-y-4">
                <h2 className="farmsense-headings text-4xl font-bold text-white">Platform Capabilities</h2>
                <p className="text-slate-400 text-lg">Enterprise features designed for modern agronomists and institutional investors.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                    { icon: <Layers />, title: 'Multi-Constellation Fusion', desc: 'Synthesizing Sentinel-1 SAR (Radar) and Sentinel-2 (Optical) for 100% cloud-free monitoring.' },
                    { icon: <Database />, title: 'Headless Integration', desc: 'Standardized API for third-party soil sensors, weather stations, and robotics telemetry.' },
                    { icon: <Shield />, title: 'Compliance Automation', desc: 'Automated SLV 2026 reporting and regulatory audit data generation.' },
                    { icon: <Zap />, title: 'Adaptive Recalculation', desc: 'Dynamic update scheduling triggered by detected field stress or weather events.' },
                    { icon: <BarChart3 />, title: 'Stakeholder Portals', desc: 'Role-based dashboards for Farmers, Auditors, Researchers, and Investors.' },
                    { icon: <Cpu />, title: '1m Precision Grid', desc: 'High-resolution synthetic interpolation for precision robotics and irrigation.' },
                ].map((f, i) => (
                    <div key={i} className="glass-card p-8 space-y-4 hover:border-emerald-500/50 transition-colors group">
                        <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                            {f.icon}
                        </div>
                        <h3 className="farmsense-headings text-xl font-bold text-white">{f.title}</h3>
                        <p className="text-slate-500 text-sm leading-relaxed">{f.desc}</p>
                    </div>
                ))}
            </div>
        </section>

        {/* Social Proof / Stats */}
        <section className="bg-white/5 border-y border-white/5 py-20">
            <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-12 text-center">
                <div className="space-y-2">
                    <div className="farmsense-headings text-4xl font-black text-white">1.2M+</div>
                    <div className="text-slate-500 text-sm uppercase tracking-widest font-bold">Acres Monitored</div>
                </div>
                <div className="space-y-2">
                    <div className="farmsense-headings text-4xl font-black text-white">94.2%</div>
                    <div className="text-slate-500 text-sm uppercase tracking-widest font-bold">Compliance Rate</div>
                </div>
                <div className="space-y-2">
                    <div className="farmsense-headings text-4xl font-black text-white">150+</div>
                    <div className="text-slate-500 text-sm uppercase tracking-widest font-bold">Hardware Integrations</div>
                </div>
                <div className="space-y-2">
                    <div className="farmsense-headings text-4xl font-black text-white">1m</div>
                    <div className="text-slate-500 text-sm uppercase tracking-widest font-bold">Grid Resolution</div>
                </div>
            </div>
        </section>
    </div>
);

const Pricing = () => (
    <div className="max-w-7xl mx-auto px-6 py-24 space-y-16">
        <div className="text-center space-y-4">
            <h2 className="farmsense-headings text-5xl font-black text-white">Plans that scale with you</h2>
            <p className="text-slate-400 text-xl">From single-field monitoring to multi-region agribusiness.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
                { name: 'Free', price: '$0', desc: 'Baseline satellite monitoring', features: ['50m Grid Resolution', 'Sentinel-2 Optical', 'Standard Dashboard', 'Manual Reports'] },
                { name: 'Basic', price: '$29', desc: 'Precision field management', features: ['20m Grid Resolution', 'Sentinel-1/2 Fusion', 'Mobile App Access', 'Automated Recalculation'], highlight: false },
                { name: 'Pro', price: '$99', desc: 'The institutional standard', features: ['1m Precision Grid', 'Full Hardware Integration', 'Compliance Automation', 'Expert Support'], highlight: true },
                { name: 'Enterprise', price: 'Custom', desc: 'Unparalleled infrastructure', features: ['Private Edge Compute', 'Custom Branding', 'SLA Guarantees', 'On-site Training'] },
            ].map((plan, i) => (
                <div key={i} className={cn(
                    "glass-card p-8 flex flex-col space-y-8 relative overflow-hidden",
                    plan.highlight && "border-emerald-500/50 shadow-emerald-500/10 ring-1 ring-emerald-500/20"
                )}>
                    {plan.highlight && <div className="absolute top-0 right-0 bg-emerald-500 text-black text-[10px] font-black px-4 py-1 rounded-bl-xl uppercase tracking-widest">Recommended</div>}
                    <div className="space-y-2">
                        <h3 className="farmsense-headings text-2xl font-bold text-white">{plan.name}</h3>
                        <p className="text-slate-500 text-sm">{plan.desc}</p>
                    </div>
                    <div className="flex items-baseline gap-1">
                        <span className="text-4xl font-black text-white">{plan.price}</span>
                        {plan.price !== 'Custom' && <span className="text-slate-500">/mo</span>}
                    </div>
                    <ul className="flex-1 space-y-4">
                        {plan.features.map(f => (
                            <li key={f} className="flex items-center gap-3 text-slate-300 text-sm">
                                <Check className="w-4 h-4 text-emerald-500" /> {f}
                            </li>
                        ))}
                    </ul>
                    <button className={cn(
                        "w-full py-4 rounded-xl font-bold transition-all",
                        plan.highlight ? "bg-emerald-500 text-slate-950 hover:bg-emerald-400" : "bg-white/5 text-white hover:bg-white/10"
                    )}>
                        {plan.name === 'Enterprise' ? 'Contact Sales' : 'Get Started'}
                    </button>
                </div>
            ))}
        </div>
    </div>
);

const About = () => (
    <div className="max-w-7xl mx-auto px-6 py-24 space-y-24">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
                <h2 className="farmsense-headings text-5xl font-black text-white leading-tight">Solving the <span className="text-gradient">Data Gap</span> in Modern Farming.</h2>
                <div className="space-y-4 text-slate-400 text-lg leading-relaxed">
                    <p>Founded in 2024, FarmSense was born from a simple observation: modern farming is drowning in data but starving for actionable intelligence.</p>
                    <p>Standard satellite monitoring is too coarse for precision robotics, and hardware deployment is too expensive for wide-area coverage. Our "Validated Synthesizer" tech bridges this gap.</p>
                </div>
                <div className="grid grid-cols-2 gap-8 pt-8">
                    <div className="glass-card p-6 border-l-4 border-emerald-500">
                        <Award className="text-emerald-500 w-8 h-8 mb-4" />
                        <h4 className="text-white font-bold mb-2">Scientific Pedigree</h4>
                        <p className="text-slate-500 text-xs uppercase font-bold tracking-widest">CSU Validated</p>
                    </div>
                    <div className="glass-card p-6 border-l-4 border-orange-500">
                        <Map className="text-orange-500 w-8 h-8 mb-4" />
                        <h4 className="text-white font-bold mb-2">Global Scale</h4>
                        <p className="text-slate-500 text-xs uppercase font-bold tracking-widest">12+ Countries</p>
                    </div>
                </div>
            </div>
            <div className="relative">
                <div className="glass-card p-2 rotate-3 animate-float">
                    <img
                        src="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?q=80&w=1200"
                        className="rounded-xl w-full grayscale opacity-80"
                        alt="Farmscape"
                    />
                </div>
                <div className="absolute -bottom-10 -left-10 glass-card p-8 pr-16 bg-slate-900 shadow-2xl z-10 hidden md:block">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-emerald-500 rounded-full flex items-center justify-center font-black text-slate-950">94%</div>
                        <div>
                            <div className="text-white font-bold">Accuracy Rating</div>
                            <div className="text-slate-500 text-xs uppercase tracking-widest font-bold">CSU SLV RC 2026</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
);

function App() {
    return (
        <div className="min-h-screen bg-[#0b1120]">
            <Navbar />
            <main>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/pricing" element={<Pricing />} />
                    <Route path="/about" element={<About />} />
                </Routes>
            </main>
            <Footer />
        </div>
    );
}

export default App;
