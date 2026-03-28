import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { HeartPulse, Shield, Activity, Sparkles, Calendar, Sun, Moon, Loader2, ArrowLeft, Star, Zap } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { formatInterpretation } from '../utils/markdown';
import { formatDobForBackend } from '../utils/dateUtils';

const HealthReport = () => {
    const { user, token } = useAuth();
    const [activeTab, setActiveTab] = useState('generic');
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [numData, setNumData] = useState(null);
    const [aiLoading, setAiLoading] = useState(false);

    // Form states
    const today = new Date();
    const [year, setYear] = useState(today.getFullYear().toString());
    const [month, setMonth] = useState((today.getMonth() + 1).toString());
    const [day, setDay] = useState(today.toISOString().split('T')[0]);

    const fetchHealthData = useCallback(async () => {
        const effectiveDob = user?.dob;
        if (!effectiveDob) return;

        try {
            setLoading(true);
            setError('');

            const params = {
                dob: formatDobForBackend(effectiveDob),
                gender: user?.gender || 'male',
                name: user?.name
            };

            if (activeTab === 'generic') {
                try {
                    const numRes = await api.get('/api/numerology/health-triangle.report.json', params);
                    setNumData(numRes);
                } catch (nErr) {
                    console.warn("Numerical health data unavailable:", nErr);
                }
            }

            setAiLoading(true);
            let endpoint = '';
            if (activeTab === 'generic') {
                endpoint = '/api/ai/health-summary';
            } else if (activeTab === 'yearly') {
                endpoint = '/api/ai/health/yearly.ai.json';
                params.year = year;
            } else if (activeTab === 'monthly') {
                endpoint = '/api/ai/health/monthly.ai.json';
                params.year = year;
                params.month = month;
            } else if (activeTab === 'daily') {
                endpoint = '/api/ai/health/daily.ai.json';
                const [y, m, d] = day.split('-');
                params.day = `${d}-${m}-${y}`;
            }

            if (endpoint) {
                const aiRes = await api.get(endpoint, params);
                setReport(aiRes.interpretation || aiRes);
            }
        } catch (err) {
            console.error("Failed to fetch health report:", err);
            setError("The celestial healing energies are temporarily inaccessible.");
        } finally {
            setAiLoading(false);
            setLoading(false);
        }
    }, [user?.dob, user?.gender, activeTab, year, month, day, user?.name]);

    useEffect(() => {
        if (user?.dob) {
            fetchHealthData();
        }
    }, [user?.dob, activeTab, fetchHealthData]);

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
                        <HeartPulse size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Vitality Matrix
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.3em] opacity-60">Celestial Wellness & Energy Alignment</p>
                    </div>
                </motion.div>
            </div>

            {/* Controls Section */}
            <div className="bg-white p-2 rounded-[2.5rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {[
                        { id: 'generic', label: 'Overall', icon: Shield },
                        { id: 'yearly', label: 'Yearly', icon: Calendar },
                        { id: 'monthly', label: 'Monthly', icon: Moon },
                        { id: 'daily', label: 'Daily', icon: Sun },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => {
                                setActiveTab(tab.id);
                                setReport(null);
                            }}
                            className={`flex items-center justify-center gap-3 py-4 rounded-2xl text-[10px] font-bold uppercase tracking-widest transition-all ${activeTab === tab.id
                                ? 'asb-button shadow-asb-purple/20'
                                : 'text-asb-text-muted hover:bg-asb-purple/5'
                                }`}
                        >
                            <tab.icon size={16} />
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </div>

                {/* Dynamic Inputs */}
                {(activeTab !== 'generic') && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-asb-purple/5 mt-2"
                    >
                        {activeTab === 'daily' && (
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Target Date</label>
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
                                    <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Month</label>
                                    <select
                                        value={month}
                                        onChange={(e) => setMonth(e.target.value)}
                                        className="asb-input w-full bg-white"
                                    >
                                        {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                                            <option key={m} value={m}>
                                                {new Date(2000, m - 1, 1).toLocaleString('default', { month: 'long' })}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Year</label>
                                    <input
                                        type="number"
                                        value={year}
                                        onChange={(e) => setYear(e.target.value)}
                                        className="asb-input w-full bg-white"
                                    />
                                </div>
                            </>
                        )}
                        {activeTab === 'yearly' && (
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Target Year</label>
                                <input
                                    type="number"
                                    value={year}
                                    onChange={(e) => setYear(e.target.value)}
                                    className="asb-input w-full bg-white"
                                />
                            </div>
                        )}
                    </motion.div>
                )}
            </div>

            {loading && !numData ? (
                <div className="flex flex-col items-center justify-center min-h-[400px] space-y-8">
                    <div className="relative">
                        <div className="w-24 h-24 border-2 border-asb-magenta/10 rounded-full animate-ping absolute inset-0"></div>
                        <Activity className="w-24 h-24 text-asb-magenta animate-pulse opacity-40" />
                    </div>
                    <p className="text-asb-magenta tracking-[0.4em] uppercase text-[10px] font-bold animate-pulse">Syncing Vital Frequencies...</p>
                </div>
            ) : error ? (
                <div className="bg-white p-12 border border-asb-purple/5 shadow-xl shadow-purple-900/5 rounded-[3rem] text-center max-w-2xl mx-auto space-y-6">
                    <Zap className="w-12 h-12 text-asb-purple mx-auto" />
                    <p className="text-asb-text font-bold italic opacity-80">{error}</p>
                    <button onClick={fetchHealthData} className="asb-button px-8 py-3 uppercase text-[10px] font-bold tracking-widest">Retry Alignment</button>
                </div>
            ) : (
                <div className="space-y-12">
                    {/* Numerical Highlights */}
                    {activeTab === 'generic' && numData && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            {[
                                { label: "Vitality Source", val: numData?.mulank, icon: Star },
                                { label: "Resilience Rhythm", val: numData?.bhagyank, icon: Zap },
                                { label: "Energy Center", val: numData?.core_vibration || "Solar", icon: Sparkles }
                            ].map((item, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="bg-white border border-asb-purple/5 p-8 rounded-[2.5rem] text-center space-y-4 group hover:border-asb-purple/20 transition-all shadow-xl shadow-purple-900/5"
                                >
                                    <item.icon className="w-5 h-5 text-asb-purple mx-auto opacity-40 group-hover:opacity-100 transition-opacity" />
                                    <div>
                                        <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60 mb-1">{item.label}</p>
                                        <p className="text-4xl font-numerology font-bold text-asb-text uppercase">{item.val}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}

                    {/* Main Content */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white border border-asb-purple/5 p-1 rounded-[3.5rem] shadow-2xl shadow-purple-900/5"
                    >
                        <div className="bg-asb-purple/5 backdrop-blur-sm rounded-[3.25rem] p-10 md:p-16 space-y-12 relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-96 h-96 bg-asb-magenta/10 rounded-full blur-3xl -mr-32 -mt-32"></div>

                            <div className="flex items-center gap-5 border-b border-asb-purple/5 pb-8 relative z-10">
                                <div className="p-3 rounded-2xl bg-asb-magenta/10 text-asb-magenta">
                                    <Shield size={28} />
                                </div>
                                <div className="relative z-10">
                                    <h2 className="text-3xl font-numerology font-bold text-asb-text uppercase tracking-tight">{activeTab} Insight</h2>
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Celestial Wellness Protocol</p>
                                </div>
                            </div>

                            <div className="prose prose-asb max-w-none relative z-10">
                                {aiLoading ? (
                                    <div className="space-y-6 py-6 animate-pulse">
                                        {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-4 bg-asb-purple/5 rounded-full w-full"></div>)}
                                        <p className="text-asb-magenta text-[10px] font-bold uppercase tracking-[0.3em] text-center mt-12">Decoding Bio-Celestial Data...</p>
                                    </div>
                                ) : report ? (
                                    <div className="text-asb-text-muted font-medium space-y-6">
                                        {formatInterpretation(report)}
                                    </div>
                                ) : (
                                    <p className="text-asb-text-muted italic text-center py-20 opacity-60">Channelling wellness frequencies...</p>
                                )}
                            </div>

                            {/* Disclaimer */}
                            <div className="mt-10 pt-10 border-t border-asb-purple/5 flex items-start gap-4">
                                <Sparkles className="w-5 h-5 text-asb-purple flex-shrink-0 mt-1" />
                                <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest leading-relaxed opacity-60">
                                    Numerology wellness reports are intended for spiritual guidance and energy awareness. They do not constitute medical advice or diagnosis. Always consult a licensed healthcare professional for medical concerns.
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

export default HealthReport;
