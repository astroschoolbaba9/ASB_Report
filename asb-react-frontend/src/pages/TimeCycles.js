import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, RefreshCw, Sun, Moon, Clock, ArrowLeft, Sparkles, Loader2 } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { formatInterpretation } from '../utils/markdown';
import { formatDobForBackend } from '../utils/dateUtils';
import { Link } from 'react-router-dom';

const TimeCycles = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('daily');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [aiLoading, setAiLoading] = useState(false);

    // Form states
    const today = new Date();
    const [year, setYear] = useState(today.getFullYear().toString());
    const [month, setMonth] = useState((today.getMonth() + 1).toString());
    const [day, setDay] = useState(today.toISOString().split('T')[0]);

    const effectiveDob = user?.dob;

    React.useEffect(() => {
        if (effectiveDob && !result && !loading && !error) {
            handleGenerate();
        }
    }, [effectiveDob]);

    if (!effectiveDob) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-asb-purple"></div>
                    <p className="text-asb-purple font-bold text-[10px] uppercase tracking-widest">Loading Astral Alignment...</p>
                </div>
            </div>
        );
    }

    async function handleGenerate() {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const params = { dob: formatDobForBackend(effectiveDob) };
            let imgEndpoint = '';
            let apiEndpoint = '';

            if (activeTab === 'yearly') {
                imgEndpoint = '/api/numerology/yearly-triptych.png';
                apiEndpoint = '/api/ai/yearly-prediction.ai.json';
                params.year = year;
            } else if (activeTab === 'monthly') {
                imgEndpoint = '/api/numerology/monthly-triptych.png';
                apiEndpoint = '/api/ai/monthly-prediction.ai.json';
                params.year = year;
                params.month = month;
            } else if (activeTab === 'daily') {
                imgEndpoint = '/api/numerology/daily-triptych.png';
                apiEndpoint = '/api/ai/daily-interpretation.ai.json';
                const [y, m, d] = day.split('-');
                params.day = `${d}-${m}-${y}`;
            }

            // 1. Fetch Triptych Image First
            const imgBlob = await api.getBytes(imgEndpoint, params);
            const imageUrl = URL.createObjectURL(imgBlob);

            setResult({
                image: imageUrl,
                interpretation: null
            });
            setLoading(false);

            // 2. Fetch AI JSON Prediction
            setAiLoading(true);
            try {
                const effectiveName = user?.name || 'Soul';
                const response = await api.get(apiEndpoint, {
                    ...params,
                    name: effectiveName
                });
                setResult(prev => ({
                    ...prev,
                    interpretation: response.interpretation
                }));
            } catch (aiErr) {
                console.error("AI Prediction failed:", aiErr);
                setResult(prev => ({
                    ...prev,
                    interpretation: "The cosmic transmission was interrupted, but your Triptych chart is synthesized above."
                }));
            } finally {
                setAiLoading(false);
            }

        } catch (err) {
            console.error('Error generating Time Cycles:', err);
            setError('Failed to sync with the cosmic clock. Please try again.');
            setLoading(false);
        }
    }

    return (
        <div className="max-w-5xl mx-auto px-4 space-y-12 pb-24 pt-8">
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
                    <div className="inline-flex p-4 rounded-3xl bg-asb-violet/5 text-asb-violet mb-2 border border-asb-violet/5">
                        <Clock size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Time Cycles
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.3em] opacity-60">Synchronize with your astral tides</p>
                    </div>
                </motion.div>
            </div>

            {/* Controls Panel */}
            <div className="bg-white p-10 rounded-[3rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5 space-y-10">
                <div className="flex bg-asb-purple/5 p-1.5 rounded-2xl border border-asb-purple/5">
                    {['Daily', 'Monthly', 'Yearly'].map((tab) => {
                        const id = tab.toLowerCase();
                        const Icon = id === 'daily' ? Sun : id === 'monthly' ? Moon : Calendar;
                        return (
                            <button
                                key={id}
                                onClick={() => {
                                    setActiveTab(id);
                                    setResult(null);
                                    setError(null);
                                }}
                                className={`flex-1 flex items-center justify-center gap-3 py-4 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all ${activeTab === id
                                    ? 'asb-button shadow-purple-900/20'
                                    : 'text-asb-text-muted hover:text-asb-purple hover:bg-asb-purple/5'
                                    }`}
                            >
                                <Icon size={14} />
                                <span>{tab} Resonance</span>
                            </button>
                        );
                    })}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-end">
                    <div className="md:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                        {activeTab === 'daily' && (
                            <div className="md:col-span-2 space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Target Dimension (Day)</label>
                                <input
                                    type="date"
                                    value={day}
                                    onChange={(e) => setDay(e.target.value)}
                                    className="asb-input w-full bg-white"
                                />
                            </div>
                        )}

                        {activeTab === 'monthly' && (
                            <>
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Cycle Year</label>
                                    <input
                                        type="number"
                                        value={year}
                                        onChange={(e) => setYear(e.target.value)}
                                        className="asb-input w-full bg-white"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Cycle Month</label>
                                    <select
                                        value={month}
                                        onChange={(e) => setMonth(e.target.value)}
                                        className="asb-input w-full bg-white appearance-none"
                                    >
                                        {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                                            <option key={m} value={m}>
                                                {new Date(2000, m - 1, 1).toLocaleString('default', { month: 'long' })}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </>
                        )}

                        {activeTab === 'yearly' && (
                            <div className="md:col-span-2 space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Cycle Year</label>
                                <input
                                    type="number"
                                    value={year}
                                    onChange={(e) => setYear(e.target.value)}
                                    className="asb-input w-full bg-white"
                                />
                            </div>
                        )}
                    </div>

                    <div className="md:col-span-4">
                        <button
                            onClick={handleGenerate}
                            disabled={loading}
                            className="asb-button w-full py-5 rounded-2xl flex items-center justify-center gap-3"
                        >
                            {loading ? (
                                <RefreshCw className="animate-spin text-white" size={20} />
                            ) : (
                                <Sparkles size={20} />
                            )}
                            <span className="uppercase text-[11px] font-bold tracking-[0.2em]">Seek Prediction</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Error Message */}
            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="p-6 rounded-[2rem] bg-red-50 text-red-600 text-[10px] font-bold uppercase tracking-widest border border-red-100 text-center"
                    >
                        {error}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Results Area */}
            <AnimatePresence mode="wait">
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-12"
                    >
                        {result.image && (
                            <div className="flex justify-center">
                                <motion.div
                                    initial={{ scale: 0.9 }}
                                    animate={{ scale: 1 }}
                                    className="relative group p-4 bg-asb-purple/5 border border-asb-purple/5 rounded-[3rem] shadow-2xl"
                                >
                                    <div className="absolute -inset-4 bg-asb-purple/5 blur-3xl opacity-50 group-hover:opacity-100 transition-opacity" />
                                    <img
                                        src={result.image}
                                        alt="Triptych Chart"
                                        className="relative max-w-[400px] w-full h-auto rounded-[2.5rem] shadow-xl"
                                    />
                                </motion.div>
                            </div>
                        )}

                        <div className="bg-white p-12 rounded-[4rem] border border-asb-purple/5 shadow-2xl shadow-purple-900/5 space-y-10">
                            <div className="flex items-center gap-5 border-b border-asb-purple/5 pb-8">
                                <div className="p-3 rounded-2xl bg-asb-purple/5 text-asb-purple border border-asb-purple/5">
                                    <Sparkles size={24} />
                                </div>
                                <div className="space-y-1">
                                    <h2 className="text-3xl font-numerology font-bold text-asb-text uppercase tracking-tight">Vibrational Insight</h2>
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">AI Decoding of your Triptych</p>
                                </div>
                            </div>

                            <div className="prose prose-asb max-w-none">
                                {aiLoading ? (
                                    <div className="space-y-8 py-10">
                                        <div className="space-y-4 animate-pulse">
                                            <div className="h-4 bg-asb-purple/5 rounded-full w-3/4"></div>
                                            <div className="h-4 bg-asb-purple/5 rounded-full w-5/6"></div>
                                            <div className="h-4 bg-asb-purple/5 rounded-full w-1/2"></div>
                                        </div>
                                        <p className="text-[10px] font-bold text-asb-purple uppercase tracking-widest animate-pulse italic">Interpreting the celestial gearshifts...</p>
                                    </div>
                                ) : result.interpretation ? (
                                    <div className="text-asb-text-muted leading-loose font-medium text-lg">
                                        {formatInterpretation(result.interpretation)}
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center py-20 text-center opacity-40 space-y-4">
                                        <Loader2 className="animate-spin text-asb-purple" size={32} />
                                        <p className="text-sm font-medium text-asb-text-muted">Synthesizing prediction follow-through...</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default TimeCycles;
