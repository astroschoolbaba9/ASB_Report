import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Target, Compass, ArrowLeft, Sparkles, Star, Zap } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { formatInterpretation } from '../utils/markdown';
import { formatDobForBackend } from '../utils/dateUtils';
import { Link } from 'react-router-dom';

const ProfessionReport = () => {
    const { user, token } = useAuth();
    const [report, setReport] = useState(null);
    const [numData, setNumData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [aiLoading, setAiLoading] = useState(false);
    const [error, setError] = useState('');

    const effectiveDob = user?.dob;

    useEffect(() => {
        const fetchData = async () => {
            if (!effectiveDob) {
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                const numRes = await api.get('/api/numerology/profession.report.json', { dob: formatDobForBackend(effectiveDob) });
                setNumData(numRes);
                setLoading(false);

                setAiLoading(true);
                const effectiveName = user?.name || 'User';
                const aiRes = await api.get('/api/ai/profession.ai.json', {
                    dob: formatDobForBackend(effectiveDob),
                    name: effectiveName
                });
                setReport(aiRes.interpretation);
            } catch (err) {
                console.error("Failed to fetch profession report:", err);
                setError("Could not reveal your career blueprint. The energies are temporarily clouded.");
            } finally {
                setLoading(false);
                setAiLoading(false);
            }
        };

        fetchData();
    }, [effectiveDob, token, user?.name]);

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
                    <div className="inline-flex p-4 rounded-3xl bg-asb-purple/5 text-asb-purple mb-2 border border-asb-purple/5">
                        <Briefcase size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Professional Destiny
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.3em] opacity-60">Career Alignment & Success Blueprint</p>
                    </div>
                </motion.div>
            </div>

            {loading ? (
                <div className="flex flex-col items-center justify-center min-h-[400px] space-y-8">
                    <div className="relative">
                        <div className="w-24 h-24 border-2 border-asb-purple/10 rounded-full animate-ping absolute inset-0"></div>
                        <Compass className="w-24 h-24 text-asb-purple animate-spin-slow opacity-40" />
                    </div>
                    <p className="text-asb-purple tracking-[0.4em] uppercase text-[10px] font-bold animate-pulse">Mapping Career Trajectories...</p>
                </div>
            ) : error ? (
                <div className="bg-white p-12 border border-asb-purple/5 shadow-xl rounded-[3rem] text-center max-w-2xl mx-auto space-y-6">
                    <Zap className="w-12 h-12 text-asb-purple mx-auto" />
                    <p className="text-asb-text font-bold italic opacity-80">{error}</p>
                    <button onClick={() => window.location.reload()} className="asb-button px-8 py-3 uppercase text-[10px] font-bold tracking-widest">Retry Connection</button>
                </div>
            ) : (
                <div className="space-y-12">
                    {/* Numerical Highlights */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { label: "Success Root", val: numData?.mulank, icon: Star },
                            { label: "Action Frequency", val: numData?.bhagyank, icon: Zap },
                            { label: "Dominant Trait", val: numData?.core_vibration || "Vision", icon: Sparkles }
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

                    {/* Career Recommendations */}
                    {numData?.profession?.professions?.length > 0 && (
                        <div className="space-y-6">
                            <div className="flex items-center gap-4 border-b border-asb-purple/5 pb-4">
                                <div className="p-2 rounded-xl bg-asb-purple/10 text-asb-purple">
                                    <Target size={24} />
                                </div>
                                <h2 className="text-2xl font-numerology font-bold text-asb-text uppercase tracking-tight">Aligned Career Paths</h2>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                {numData.profession.professions.map((prof, idx) => (
                                    <div key={idx} className="bg-white border border-asb-purple/10 p-5 rounded-2xl flex items-center gap-4 hover:border-asb-purple/30 transition-colors shadow-sm group">
                                        <div className="w-8 h-8 rounded-full bg-asb-purple/5 flex items-center justify-center text-asb-purple font-bold text-xs group-hover:scale-110 transition-transform">
                                            {idx + 1}
                                        </div>
                                        <p className="text-asb-text font-medium text-sm">{prof}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Main Reading */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white border border-asb-purple/5 p-1 rounded-[3.5rem] shadow-2xl shadow-purple-900/5"
                    >
                        <div className="bg-asb-purple/5 backdrop-blur-sm rounded-[3.25rem] p-10 md:p-16 space-y-12 relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-96 h-96 bg-asb-purple/10 rounded-full blur-3xl -mr-32 -mt-32"></div>

                            <div className="flex items-center gap-5 border-b border-asb-purple/5 pb-8 relative z-10">
                                <div className="p-3 rounded-2xl bg-asb-purple/10 text-asb-purple">
                                    <Target size={28} />
                                </div>
                                <div className="relative z-10">
                                    <h2 className="text-3xl font-numerology font-bold text-asb-text uppercase tracking-tight">Vibrational Blueprint</h2>
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Career Path AI Analysis</p>
                                </div>
                            </div>

                            <div className="prose prose-asb max-w-none relative z-10">
                                {aiLoading ? (
                                    <div className="space-y-6 py-6 animate-pulse">
                                        <div className="h-4 bg-asb-purple/5 rounded-full w-full"></div>
                                        <div className="h-4 bg-asb-purple/5 rounded-full w-[95%]"></div>
                                        <div className="h-4 bg-asb-purple/5 rounded-full w-[90%]"></div>
                                        <div className="h-4 bg-asb-purple/5 rounded-full w-full"></div>
                                        <div className="h-4 bg-asb-purple/5 rounded-full w-[85%]"></div>
                                        <p className="text-asb-purple text-[10px] font-bold uppercase tracking-[0.3em] text-center mt-12">Channelling Professional Insights...</p>
                                    </div>
                                ) : report ? (
                                    <div className="text-asb-text-muted font-medium space-y-6">
                                        {formatInterpretation(report)}
                                    </div>
                                ) : (
                                    <p className="text-asb-text-muted italic text-center py-20 opacity-60">Your professional energies are being calculated...</p>
                                )}
                            </div>

                            {/* Disclaimer */}
                            <div className="mt-10 pt-10 border-t border-asb-purple/5 flex items-start gap-4">
                                <Sparkles className="w-5 h-5 text-asb-purple flex-shrink-0 mt-1" />
                                <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest leading-relaxed opacity-60">
                                    Numerology reports are intended for spiritual guidance and energy awareness. They do not constitute absolute guarantees or definitive blueprints. Always consult your intuition for major career decisions.
                                </p>
                            </div>
                        </div>
                    </motion.div>

                    {/* Footer Visual */}
                    <div className="flex justify-center pt-8 opacity-40 hover:opacity-100 transition-opacity">
                        <img
                            src={`${api.instance.defaults.baseURL}/api/numerology/mystical-triangle.png?dob=${formatDobForBackend(user?.dob)}`}
                            alt="Mystical Triangle"
                            className="w-48 h-auto grayscale hover:grayscale-0 transition-all duration-700"
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProfessionReport;
