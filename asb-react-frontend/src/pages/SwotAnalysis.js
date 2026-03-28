import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, TrendingUp, Zap, Star, Loader2, ArrowLeft, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { formatInterpretation } from '../utils/markdown';
import { formatDobForBackend } from '../utils/dateUtils';

const SwotAnalysis = () => {
    const { user } = useAuth();
    const [aiLoading, setAiLoading] = useState(false);
    const [data, setData] = useState(null);

    const fetchSwot = React.useCallback(async () => {
        const effectiveDob = user?.dob;
        if (!effectiveDob) return;

        try {
            setAiLoading(true);
            const effectiveName = user?.name || 'User';
            const response = await api.get('/api/ai/swot.ai.json', {
                dob: formatDobForBackend(effectiveDob),
                name: effectiveName
            });
            setData(response);
        } catch (err) {
            console.error("Error fetching SWOT:", err);
        } finally {
            setAiLoading(false);
        }
    }, [user?.dob, user?.name]);

    useEffect(() => {
        if (user?.dob) {
            fetchSwot();
        }
    }, [user?.dob, fetchSwot]);

    if (!user?.dob) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-asb-bg">
                <div className="flex flex-col items-center gap-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-asb-purple"></div>
                    <p className="text-asb-purple font-bold text-[10px] uppercase tracking-widest">Profiling Soul Grid...</p>
                </div>
            </div>
        );
    }

    const apiSwot = data?.swot || {};

    const swotContent = {
        strengths: apiSwot.Strengths || apiSwot.strengths || ["Natural resonance and strong latent intuition."],
        weaknesses: apiSwot.Weaknesses || apiSwot.weaknesses || ["Periods of vibrational noise or hesitancy."],
        opportunities: apiSwot.Opportunities || apiSwot.opportunities || ["Upcoming shift for significant internal growth."],
        threats: apiSwot.Threats || apiSwot.threats || ["External frequencies disrupting core focus."],
        fullText: data?.interpretation || data?.fullText
    };

    const renderList = (content) => {
        if (Array.isArray(content)) {
            return (
                <ul className="space-y-4">
                    {content.map((item, i) => (
                        <li key={i} className="flex items-start gap-3">
                            <div className="w-1.5 h-1.5 rounded-full bg-asb-gold mt-2 shrink-0" />
                            <span className="text-sm font-medium leading-relaxed">{item}</span>
                        </li>
                    ))}
                </ul>
            );
        }
        return <p className="text-sm font-medium leading-relaxed">{content}</p>;
    };

    const items = [
        {
            title: 'Strengths',
            icon: <Zap className="text-green-500" size={24} />,
            content: swotContent.strengths,
            color: 'bg-green-500/5',
            accent: 'border-green-500/20',
            text: 'text-green-700'
        },
        {
            title: 'Weaknesses',
            icon: <AlertTriangle className="text-red-500" size={24} />,
            content: swotContent.weaknesses,
            color: 'bg-red-500/5',
            accent: 'border-red-500/20',
            text: 'text-red-700'
        },
        {
            title: 'Opportunities',
            icon: <TrendingUp className="text-asb-gold" size={24} />,
            content: swotContent.opportunities,
            color: 'bg-asb-gold/5',
            accent: 'border-asb-gold/20',
            text: 'text-asb-gold'
        },
        {
            title: 'Threats',
            icon: <Shield className="text-asb-violet" size={24} />,
            content: swotContent.threats,
            color: 'bg-asb-violet/5',
            accent: 'border-asb-violet/20',
            text: 'text-asb-violet'
        }
    ];

    return (
        <div className="max-w-6xl mx-auto px-4 space-y-12 pb-24 pt-8">
            {/* Navigation & Header */}
            <div className="space-y-8">
                <div className="flex items-center justify-between">
                    <Link
                        to="/dashboard"
                        className="inline-flex items-center gap-2 text-asb-purple font-bold text-[10px] uppercase tracking-widest hover:opacity-70 transition-opacity"
                    >
                        <ArrowLeft size={16} /> Back to Dashboard
                    </Link>
                    <button
                        onClick={fetchSwot}
                        className="p-3 rounded-2xl bg-asb-purple/5 border border-asb-purple/10 text-asb-purple hover:bg-asb-purple/10 transition-colors"
                        title="Refresh Analysis"
                    >
                        <Loader2 className={`w-5 h-5 ${aiLoading ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center space-y-6"
                >
                    <div className="inline-flex p-4 rounded-3xl bg-asb-purple/5 text-asb-purple mb-2 border border-asb-purple/5">
                        <Zap size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Cosmic SWOT
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.3em] opacity-60">Strategic astral mapping</p>
                    </div>
                </motion.div>
            </div>

            {/* SWOT Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {items.map((item, idx) => (
                    <motion.div
                        key={item.title}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`p-8 rounded-[2.5rem] border ${item.accent} ${item.color} shadow-xl shadow-purple-900/5 space-y-6 flex flex-col`}
                    >
                        <div className="flex items-center justify-between">
                            <h3 className={`text-lg font-numerology font-bold uppercase tracking-tight ${item.text}`}>{item.title}</h3>
                            <div className="p-2.5 rounded-2xl bg-white shadow-sm border border-asb-purple/5">
                                {item.icon}
                            </div>
                        </div>
                        <div className="flex-grow">
                            {aiLoading && !data ? (
                                <div className="space-y-3 animate-pulse">
                                    <div className="h-3 bg-asb-purple/5 rounded-full w-full"></div>
                                    <div className="h-3 bg-asb-purple/5 rounded-full w-4/5"></div>
                                </div>
                            ) : (
                                <div className="text-asb-text-muted font-medium">
                                    {renderList(item.content)}
                                </div>
                            )}
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Detailed Analysis */}
            <AnimatePresence>
                {swotContent?.fullText && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white p-12 rounded-[4rem] border border-asb-purple/5 shadow-2xl shadow-purple-900/5 space-y-10"
                    >
                        <div className="flex items-center gap-5 border-b border-asb-purple/5 pb-8">
                            <div className="p-3 rounded-2xl bg-asb-purple/5 text-asb-purple border border-asb-purple/5">
                                <Sparkles size={24} />
                            </div>
                            <div className="space-y-1">
                                <h2 className="text-3xl font-numerology font-bold text-asb-text uppercase tracking-tight">Full AI Spectrum</h2>
                                <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Deep dive into your strategic alignment</p>
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
                                    <p className="text-[10px] font-bold text-asb-purple uppercase tracking-widest animate-pulse italic">Scanning soul dimensions...</p>
                                </div>
                            ) : (
                                <div className="text-asb-text-muted leading-loose font-medium text-lg">
                                    {formatInterpretation(swotContent.fullText)}
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* CTAs */}
            <div className="flex flex-col md:flex-row gap-6 justify-center pt-8">
                <Link
                    to="/consult"
                    className="asb-button px-12 py-5 rounded-2xl text-[11px] font-bold uppercase tracking-[0.2em]"
                >
                    Book Astral Consult
                </Link>
                <Link
                    to="/dashboard"
                    className="asb-button-secondary px-12 py-5 rounded-2xl text-[11px] font-bold uppercase tracking-[0.2em]"
                >
                    Return to Void
                </Link>
            </div>
        </div>
    );
};

export default SwotAnalysis;
