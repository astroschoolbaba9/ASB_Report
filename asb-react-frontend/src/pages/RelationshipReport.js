import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HeartHandshake, Calendar, Sparkles, AlertCircle, ArrowLeft, Star, Zap } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { formatInterpretation } from '../utils/markdown';
import { formatDobForBackend } from '../utils/dateUtils';

const RelationshipReport = () => {
    const { user } = useAuth();
    const [ownDob, setOwnDob] = useState(user?.dob || '');
    const [partnerDob, setPartnerDob] = useState('');
    const [numData, setNumData] = useState(null);
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [aiLoading, setAiLoading] = useState(false);
    const [error, setError] = useState('');

    const handleCalculate = async (e) => {
        e.preventDefault();
        if (!ownDob || !partnerDob) {
            setError('Please provide both dates of birth');
            return;
        }

        setLoading(true);
        setError('');
        setReport(null);
        setNumData(null);

        try {
            const numParams = { left: formatDobForBackend(ownDob), right: formatDobForBackend(partnerDob) };
            const numRes = await api.get('/api/numerology/relationship-triangle.report.json', numParams);
            setNumData(numRes);
            setLoading(false);

            setAiLoading(true);
            const aiRes = await api.get('/api/ai/relationship-triangle.ai.json', {
                ...numParams,
                name: user?.name || 'User'
            });
            setReport(aiRes.interpretation);
        } catch (err) {
            console.error("Failed to analyze relationship:", err);
            setError("The cosmic connection is temporarily obscured. Please try again.");
        } finally {
            setAiLoading(false);
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto px-4 space-y-12 pb-24">
            {/* Navigation & Header */}
            <div className="space-y-8">
                <Link
                    to="/dashboard"
                    className="inline-flex items-center gap-2 text-asb-purple font-bold text-[10px] uppercase tracking-widest hover:opacity-70 transition-opacity"
                >
                    <ArrowLeft size={16} /> Back to Dashboard
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center space-y-6"
                >
                    <div className="inline-flex p-4 rounded-3xl bg-asb-magenta/5 text-asb-magenta mb-2 border border-asb-magenta/5">
                        <HeartHandshake size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Cosmic Bond
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.3em] opacity-60">Compatibility & Shared Destiny Analysis</p>
                    </div>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
                {/* Input Panel */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="lg:col-span-5 space-y-8"
                >
                    <div className="bg-white p-10 rounded-[3rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5 space-y-8">
                        <div>
                            <h2 className="text-2xl font-numerology font-bold text-asb-text uppercase">Analyze Bond</h2>
                            <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Enter dates to reveal synergy</p>
                        </div>

                        <form onSubmit={handleCalculate} className="space-y-6">
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Your Birth Date</label>
                                    <input
                                        type="date"
                                        value={ownDob}
                                        onChange={(e) => setOwnDob(e.target.value)}
                                        className="asb-input w-full bg-white"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Partner's Birth Date</label>
                                    <input
                                        type="date"
                                        value={partnerDob}
                                        onChange={(e) => setPartnerDob(e.target.value)}
                                        className="asb-input w-full bg-white"
                                    />
                                </div>
                            </div>

                            {error && (
                                <div className="flex items-center gap-2 text-red-500 text-[10px] font-bold uppercase tracking-wider bg-red-500/10 p-4 rounded-2xl border border-red-500/20">
                                    <AlertCircle size={16} />
                                    <span>{error}</span>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={loading}
                                className="asb-button w-full py-5 rounded-2xl flex items-center justify-center gap-3"
                            >
                                {loading ? (
                                    <Zap className="animate-spin text-white" size={20} />
                                ) : (
                                    <Sparkles size={20} />
                                )}
                                <span className="uppercase text-[11px] font-bold tracking-[0.2em]">Reveal Synergy</span>
                            </button>
                        </form>
                    </div>
                </motion.div>

                {/* Results Panel */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="lg:col-span-7"
                >
                    <AnimatePresence mode="wait">
                        {numData ? (
                            <motion.div
                                key="results"
                                initial={{ opacity: 0, scale: 0.98 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="space-y-8"
                            >
                                {/* Triangle Visualization */}
                                <div className="bg-white p-1 rounded-[3.5rem] shadow-2xl overflow-hidden border border-asb-purple/5">
                                    <div className="bg-asb-purple/5 backdrop-blur-sm rounded-[3.25rem] p-8 space-y-8">
                                        <div className="text-center">
                                            <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-[0.3em] opacity-40 mb-6">Compatibility Triptych</p>
                                            <div className="relative group">
                                                <div className="absolute inset-0 bg-asb-magenta/5 rounded-full blur-3xl scale-75 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                                <img
                                                    src={`${api.instance.defaults.baseURL}/api/numerology/mystical-triangle-triptych.png?left=${formatDobForBackend(ownDob)}&right=${formatDobForBackend(partnerDob)}`}
                                                    alt="Connection Visual"
                                                    className="w-full h-auto object-contain relative z-10 hover:scale-[1.02] transition-transform duration-700 brightness-90 contrast-110"
                                                />
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-3 gap-4 items-center pt-8 border-t border-asb-purple/5">
                                            <div className="text-center group">
                                                <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-40 group-hover:opacity-100 transition-opacity">Left Root</p>
                                                <p className="text-3xl font-numerology font-bold text-asb-text">{numData.left_number}</p>
                                            </div>
                                            <div className="text-center p-4 rounded-3xl bg-asb-magenta/5 border border-asb-magenta/5">
                                                <p className="text-[10px] font-bold text-asb-magenta uppercase tracking-widest mb-1">Union</p>
                                                <p className="text-5xl font-numerology font-bold text-asb-text tracking-tighter">{numData.combined_number}</p>
                                            </div>
                                            <div className="text-center group">
                                                <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-40 group-hover:opacity-100 transition-opacity">Right Root</p>
                                                <p className="text-3xl font-numerology font-bold text-asb-text">{numData.right_number}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* AI Interpretation */}
                                <div className="bg-white p-10 md:p-16 rounded-[3.5rem] border border-asb-purple/5 shadow-2xl shadow-purple-900/5 space-y-12">
                                    <div className="flex items-center gap-5 border-b border-asb-purple/5 pb-8">
                                        <div className="p-3 rounded-2xl bg-asb-purple/5 text-asb-purple border border-asb-purple/5">
                                            <Star size={28} />
                                        </div>
                                        <div>
                                            <h2 className="text-3xl font-numerology font-bold text-asb-text uppercase tracking-tight">Bond Analysis</h2>
                                            <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Soul Path Convergence</p>
                                        </div>
                                    </div>

                                    <div className="prose prose-asb max-w-none text-asb-text-muted font-medium">
                                        {aiLoading ? (
                                            <div className="space-y-6 py-6 animate-pulse">
                                                {[1, 2, 3, 4].map(i => <div key={i} className="h-4 bg-asb-purple/5 rounded-full w-full"></div>)}
                                                <p className="text-asb-magenta text-[10px] font-bold uppercase tracking-[0.3em] text-center mt-12 animate-pulse">Analyzing Cosmic Synergy...</p>
                                            </div>
                                        ) : report ? (
                                            formatInterpretation(report)
                                        ) : (
                                            <p className="text-asb-text-muted italic text-center py-20 opacity-60">Waiting for soul-data transmission...</p>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="bg-white h-full min-h-[500px] rounded-[3.5rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5 flex flex-col items-center justify-center space-y-8 text-center p-12 opacity-80">
                                <div className="w-24 h-24 border border-asb-purple/10 rounded-full flex items-center justify-center text-asb-purple/40 animate-spin-slow">
                                    <Star size={40} />
                                </div>
                                <div className="space-y-4 max-w-xs">
                                    <h3 className="text-xl font-numerology font-bold text-asb-text uppercase tracking-wider">Soul-Sync Pending</h3>
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest leading-loose opacity-60">
                                        The shared destiny between two souls remains hidden until their vibrations are entered.
                                    </p>
                                </div>
                            </div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </div>
        </div>
    );
};

export default RelationshipReport;
