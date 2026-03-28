import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { Sparkles, Activity, FileText, Download, ShieldAlert, Briefcase, HeartPulse, HeartHandshake, Calendar, BookOpen, Star, ArrowRight, User as UserIcon } from 'lucide-react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import { formatInterpretation } from '../utils/markdown';
import { formatDobForBackend } from '../utils/dateUtils';

const Dashboard = () => {
    const { user, token } = useAuth();
    const [reportData, setReportData] = useState(null);
    const [aiSummary, setAiSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [aiLoading, setAiLoading] = useState(false);
    const [downloading, setDownloading] = useState(false);
    const [downloadProgress, setDownloadProgress] = useState(0);
    const [error, setError] = useState('');

    const fetchPersonalData = React.useCallback(async () => {
        const effectiveDob = user?.dob;
        const effectiveName = user?.name || 'User';

        if (!effectiveDob) {
            setLoading(false);
            return;
        }

        setError('');
        setLoading(true);
        setAiSummary(null);

        try {
            const triangleRes = await api.get('/api/numerology/mystical-triangle.report.json', {
                dob: formatDobForBackend(effectiveDob)
            });
            setReportData(triangleRes);
            setLoading(false);

            setAiLoading(true);
            try {
                const aiRes = await api.get('/api/ai/summary', {
                    dob: formatDobForBackend(effectiveDob),
                    name: effectiveName
                });
                setAiSummary(aiRes.interpretation);
            } catch (err) {
                console.error("Failed to load AI summary:", err);
                setAiSummary("AI interpretation is temporarily unavailable, but your core numerical data is ready below.");
            } finally {
                setAiLoading(false);
            }
        } catch (err) {
            console.error("Failed to load numerical report:", err);
            setError("Could not load your cosmic blueprint. Please refresh the connection.");
            setLoading(false);
        }
    }, [user?.dob, user?.name]);

    useEffect(() => {
        if (user?.dob) {
            fetchPersonalData();
        }
    }, [user?.dob, user?.name, fetchPersonalData]);

    const handleDownloadReport = async () => {
        const effectiveDob = user?.dob;
        const effectiveName = user?.name || 'User';
        const effectiveGender = user?.gender || 'male';

        if (!effectiveDob) return;

        setDownloading(true);
        setDownloadProgress(0);
        try {
            const pdfBlob = await api.getBytes('/api/ai/master-report.pdf', {
                dob: formatDobForBackend(effectiveDob),
                name: effectiveName,
                gender: effectiveGender,
            });

            const url = window.URL.createObjectURL(new Blob([pdfBlob]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `ASB_Report_${effectiveName.replace(/\s+/g, '_')}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            console.error("PDF Download Error:", error);
            alert('Failed to generate your PDF report.');
        } finally {
            setDownloading(false);
            setDownloadProgress(0);
        }
    };

    if (loading) {
        return (
            <div className="min-h-[70vh] flex items-center justify-center">
                <div className="flex flex-col items-center space-y-6">
                    <div className="relative">
                        <div className="w-20 h-20 border-2 border-asb-purple/20 rounded-full animate-ping absolute inset-0"></div>
                        <Activity className="w-20 h-20 text-asb-purple animate-pulse" />
                    </div>
                    <p className="text-asb-purple font-numerology font-bold tracking-[0.2em] uppercase animate-bounce">Synchronizing Soul Frequencies...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-xl mx-auto mt-20 bg-white p-10 border border-red-100 rounded-[2.5rem] text-center shadow-xl space-y-8">
                <ShieldAlert className="w-20 h-20 text-red-400 mx-auto" />
                <div className="space-y-2">
                    <h2 className="text-3xl font-numerology font-bold text-asb-text uppercase">Vibrational Mismatch</h2>
                    <p className="text-asb-text-muted font-medium italic opacity-80">{error}</p>
                </div>
                <button
                    onClick={fetchPersonalData}
                    className="asb-button px-10 py-4 flex items-center gap-3 mx-auto uppercase tracking-widest text-xs font-bold"
                >
                    <Activity className="w-4 h-4" /> Reset Frequency
                </button>
            </div>
        );
    }

    const { EF_core, core_meaning } = reportData?.interpretations?.core || {};
    const G_obj = reportData?.interpretations?.core?.G;
    const G = typeof G_obj === 'object' ? G_obj?.value : G_obj;

    const E_obj = EF_core?.E_details_ref;
    const E = typeof E_obj === 'object' ? E_obj?.value : E_obj;

    const F_obj = EF_core?.F_details_ref;
    const F = typeof F_obj === 'object' ? F_obj?.value : F_obj;

    return (
        <div className="max-w-6xl mx-auto px-4 space-y-16 pb-24">
            {/* Hero Profile Section */}
            <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="relative bg-white border border-asb-purple/5 p-1 rounded-[3.5rem] overflow-hidden shadow-2xl shadow-purple-900/5"
            >
                <div className="bg-asb-purple/5 backdrop-blur-xl rounded-[3.25rem] p-10 md:p-14 flex flex-col md:flex-row items-center gap-10 relative overflow-hidden">
                    {/* Background Accents */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-asb-purple/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
                    <div className="absolute bottom-0 left-0 w-48 h-48 bg-asb-purple/5 rounded-full blur-3xl -ml-16 -mb-16"></div>

                    <div className="relative group">
                        <div className="absolute inset-0 bg-asb-purple rounded-full blur-[2px] opacity-10 group-hover:opacity-20 transition-opacity"></div>
                        <div className="w-40 h-40 md:w-52 md:h-52 rounded-full border-[12px] border-white overflow-hidden shadow-inner relative z-10 flex items-center justify-center bg-asb-purple/5">
                            <UserIcon className="w-24 h-24 text-asb-purple opacity-40" />
                        </div>
                        <div className="absolute -bottom-2 -right-2 bg-asb-purple p-3 rounded-2xl shadow-lg z-20 border-4 border-white">
                            <Sparkles className="w-6 h-6 text-white" />
                        </div>
                    </div>

                    <div className="flex-1 text-center md:text-left space-y-6 relative z-10">
                        <div className="space-y-1">
                            <p className="text-asb-purple font-bold text-xs uppercase tracking-[0.3em] ml-1">Universal Blueprint</p>
                            <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase leading-none">
                                {user?.name || 'Seeker'}
                            </h1>
                        </div>
                        <div className="flex flex-wrap justify-center md:justify-start gap-4">
                            <span className="px-6 py-2 rounded-full bg-white border border-asb-purple/5 text-asb-text-muted text-[10px] font-bold uppercase tracking-widest flex items-center gap-2">
                                <Calendar size={14} className="text-asb-purple" /> Born: {user?.dob || '--/--/----'}
                            </span>
                            <span className="px-6 py-2 rounded-full bg-asb-purple/10 text-asb-purple text-[10px] font-bold uppercase tracking-widest flex items-center gap-2">
                                <Star size={14} /> Numerology Level 1
                            </span>
                        </div>
                        <p className="text-asb-text-muted font-medium italic opacity-70 max-w-xl">
                            "The universe is not outside of you. Look inside yourself; everything that you want, you already are." — Rumi
                        </p>
                    </div>

                    <div className="md:border-l border-asb-purple border-opacity-10 md:pl-10 flex flex-col items-center md:items-start space-y-4">
                        <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-[0.2em]">Profile Health</p>
                        <div className="flex gap-1.5">
                            {[1, 2, 3, 4, 5].map(i => (
                                <div key={i} className={`h-1.5 w-6 rounded-full ${i <= 4 ? 'bg-asb-purple' : 'bg-asb-purple/20'}`}></div>
                            ))}
                        </div>
                        <button onClick={fetchPersonalData} className="text-[10px] font-bold text-asb-purple uppercase tracking-widest hover:opacity-70 transition-opacity flex items-center gap-2">
                            <Activity size={12} /> Sync Cosmic Records
                        </button>
                    </div>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:items-start">

                {/* Left: Core Numbers & Insights */}
                <div className="lg:col-span-8 space-y-10">

                    {/* Daily Oracle */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="bg-white border border-asb-purple/5 p-10 md:p-14 rounded-[3rem] relative overflow-hidden shadow-xl shadow-purple-900/5"
                    >
                        <div className="flex items-center gap-5 mb-10 border-b border-asb-purple/5 pb-6">
                            <div className="p-3 rounded-2xl bg-asb-purple/5 text-asb-purple">
                                <Sparkles size={28} />
                            </div>
                            <div>
                                <h2 className="text-3xl font-numerology font-bold text-asb-text tracking-tight uppercase">Daily Oracle</h2>
                                <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Personalized AI Interpretation</p>
                            </div>
                        </div>

                        {aiLoading ? (
                            <div className="space-y-6 py-4">
                                <div className="h-4 bg-asb-purple/5 rounded-full w-full animate-pulse"></div>
                                <div className="h-4 bg-asb-purple/5 rounded-full w-11/12 animate-pulse"></div>
                                <div className="h-4 bg-asb-purple/5 rounded-full w-10/12 animate-pulse"></div>
                                <div className="h-4 bg-asb-purple/5 rounded-full w-full animate-pulse"></div>
                                <p className="text-asb-purple text-[10px] font-bold uppercase tracking-[0.3em] text-center mt-10 animate-pulse">Channelling Etheric Intelligence...</p>
                            </div>
                        ) : aiSummary ? (
                            <div className="prose prose-asb max-w-none text-asb-text-muted font-medium leading-relaxed first-letter:text-5xl first-letter:font-numerology first-letter:float-left first-letter:mr-3 first-letter:text-asb-purple">
                                {formatInterpretation(aiSummary)}
                            </div>
                        ) : (
                            <p className="text-asb-text-muted italic text-center py-10 opacity-60">Manifesting your core vibration analysis...</p>
                        )}
                    </motion.div>

                    {/* Numeric Pillars */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <motion.div
                            whileHover={{ y: -5 }}
                            className="bg-white border border-asb-purple/5 p-10 rounded-[2.5rem] relative group cursor-default shadow-xl shadow-purple-900/5"
                        >
                            <div className="absolute top-6 right-8 text-asb-purple/5 font-numerology text-7xl select-none group-hover:scale-110 transition-transform">1</div>
                            <div className="space-y-6 relative z-10">
                                <p className="text-[10px] font-bold text-asb-purple uppercase tracking-[0.4em]">Mulank (Psychic)</p>
                                <div className="text-8xl font-numerology font-bold text-asb-text leading-none">{reportData?.mulank_bhagyank?.mulank || '--'}</div>
                                <p className="text-xs font-bold text-asb-text-muted uppercase leading-relaxed opacity-70">
                                    Defines your inherent talents, character, and mental frequency since birth.
                                </p>
                            </div>
                        </motion.div>

                        <motion.div
                            whileHover={{ y: -5 }}
                            className="bg-white border border-asb-purple/5 p-10 rounded-[2.5rem] relative group cursor-default shadow-xl shadow-purple-900/5"
                        >
                            <div className="absolute top-6 right-8 text-asb-purple/5 font-numerology text-7xl select-none group-hover:scale-110 transition-transform">2</div>
                            <div className="space-y-6 relative z-10">
                                <p className="text-[10px] font-bold text-asb-purple uppercase tracking-[0.4em]">Bhagyank (Destiny)</p>
                                <div className="text-8xl font-numerology font-bold text-asb-purple leading-none">{reportData?.mulank_bhagyank?.bhagyank || '--'}</div>
                                <p className="text-xs font-bold text-asb-text-muted uppercase leading-relaxed opacity-70">
                                    Represents the cosmic purpose and path you are destined to walk in this lifetime.
                                </p>
                            </div>
                        </motion.div>

                        {reportData?.mulank_bhagyank?.pair_meaning && (
                            <div className="md:col-span-2 bg-asb-purple/5 p-10 rounded-[2.5rem] border border-asb-purple/5">
                                <h3 className="text-[10px] font-bold text-asb-purple uppercase tracking-[0.3em] mb-4 flex items-center gap-3">
                                    <ShieldAlert size={16} /> Cosmic Alignment
                                </h3>
                                <p className="text-asb-text font-bold leading-relaxed text-sm opacity-80">
                                    {reportData.mulank_bhagyank.pair_meaning?.combined?.summary}
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Mystical Triangle & Download */}
                <div className="lg:col-span-4 space-y-10">
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="bg-white border border-asb-purple/5 p-1 rounded-[3rem] shadow-2xl shadow-purple-900/5 sticky top-24"
                    >
                        <div className="bg-asb-purple/5 rounded-[2.85rem] p-10 space-y-10 relative overflow-hidden">
                            {/* Mystical Triangle Visual */}
                            <div className="relative group">
                                <div className="absolute inset-0 bg-asb-gold/5 blur-3xl rounded-full"></div>
                                <img
                                    src={`${api.instance.defaults.baseURL}/api/numerology/mystical-triangle.png?dob=${formatDobForBackend(user?.dob)}`}
                                    alt="Mystical Triangle"
                                    className="w-full h-auto object-contain relative z-10 drop-shadow-2xl group-hover:scale-105 transition-transform duration-700"
                                />
                            </div>

                            <div className="space-y-8">
                                <div className="flex items-center gap-3">
                                    <Activity className="text-asb-purple" size={20} />
                                    <h3 className="text-xl font-numerology font-bold text-asb-text uppercase">Core Vibration</h3>
                                </div>

                                <div className="flex justify-center py-6">
                                    <div className="w-36 h-36 rounded-full border-2 border-asb-purple/10 flex flex-col items-center justify-center bg-white shadow-lg relative overflow-hidden">
                                        <div className="absolute inset-0 bg-asb-purple/5 animate-pulse"></div>
                                        <span className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest relative z-10">Root (G)</span>
                                        <span className="text-6xl font-numerology font-bold text-asb-text relative z-10 leading-none mt-1">{G || '--'}</span>
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div className="bg-white p-5 rounded-3xl border border-asb-purple/5 shadow-sm">
                                        <p className="text-[10px] font-bold text-asb-purple uppercase tracking-widest mb-2">Meaning</p>
                                        <p className="text-xs font-bold text-asb-text-muted leading-relaxed opacity-70 italic">"{typeof G_obj === 'object' ? G_obj?.meaning : (reportData?.interpretations?.core?.core_meaning || '')}"</p>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-white p-4 rounded-3xl border border-asb-purple/5 shadow-sm text-center">
                                            <p className="text-[9px] font-bold text-asb-text-muted uppercase tracking-widest mb-1">Outer (E)</p>
                                            <span className="text-2xl font-numerology font-bold text-asb-text">{E || '-'}</span>
                                        </div>
                                        <div className="bg-white p-4 rounded-3xl border border-asb-purple/5 shadow-sm text-center">
                                            <p className="text-[9px] font-bold text-asb-text-muted uppercase tracking-widest mb-1">Inner (F)</p>
                                            <span className="text-2xl font-numerology font-bold text-asb-purple">{F || '-'}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-6 border-t border-asb-purple/10">
                                    {downloading ? (
                                        <div className="space-y-4">
                                            <div className="h-2 w-full bg-asb-purple/5 rounded-full overflow-hidden">
                                                <motion.div
                                                    initial={{ x: '-100%' }}
                                                    animate={{ x: '100%' }}
                                                    transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}
                                                    className="h-full w-1/2 bg-asb-purple rounded-full"
                                                />
                                            </div>
                                            <p className="text-[10px] font-bold text-asb-purple text-center uppercase tracking-[0.2em] animate-pulse">Printing Cosmic Manuscript...</p>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={handleDownloadReport}
                                            className="asb-button w-full py-5 rounded-2xl flex items-center justify-center gap-3 uppercase tracking-widest text-xs font-extrabold shadow-xl"
                                        >
                                            <FileText className="w-5 h-5" /> Download Master PDF
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Expansion Modules */}
            <div className="space-y-12">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-asb-purple/10 pb-8">
                    <div className="space-y-3">
                        <h2 className="text-4xl font-numerology font-bold text-asb-text uppercase tracking-tight">Cosmic Spheres</h2>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-widest opacity-60">Explore specific sectors of your vibrational blueprint</p>
                    </div>
                    <div className="flex items-center gap-3 text-asb-purple font-bold text-[10px] uppercase tracking-widest bg-asb-purple/5 px-6 py-3 rounded-2xl border border-asb-purple/5">
                        <ShieldAlert size={16} /> Data Fully Personalized
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {[
                        { to: "/profession", icon: Briefcase, color: "asb-gold", title: "Profession & Career", desc: "Discover career paths aligned with your psychic and destiny frequencies." },
                        { to: "/health", icon: HeartPulse, color: "asb-purple", title: "Health & Wellness", desc: "Understand physical vulnerabilities and energetic health indicators." },
                        { to: "/swot", icon: Star, color: "asb-gold", title: "Vibrational SWOT", desc: "Analyze spiritual Strengths, Weaknesses, and Cosmic Opportunities." },
                        { to: "/relationship", icon: HeartHandshake, color: "asb-purple", title: "Energetic Bonds", desc: "Compare soul frequencies and check compatibility with significant others." },
                        { to: "/time-cycles", icon: Calendar, color: "asb-gold", title: "Temporal Cycles", desc: "Plan according to your Daily, Monthly, and Yearly cosmic tides." },
                        { to: "/consult", icon: BookOpen, color: "asb-purple", title: "Divine Guidance", desc: "Connect with masters for remedies and deeper spiritual consultation." },
                    ].map((module, idx) => (
                        <Link
                            key={idx}
                            to={module.to}
                            className="group bg-white p-10 rounded-[2.5rem] border border-asb-purple/5 hover:border-asb-purple/20 transition-all shadow-xl shadow-purple-900/5 hover:shadow-purple-900/10 flex flex-col justify-between"
                        >
                            <div className="space-y-6">
                                <div className={`p-5 bg-asb-purple/5 rounded-3xl w-fit group-hover:scale-110 transition-transform`}>
                                    <module.icon className="w-8 h-8 text-asb-purple" />
                                </div>
                                <div className="space-y-2">
                                    <h3 className="text-2xl font-numerology font-bold text-asb-text uppercase tracking-tight">{module.title}</h3>
                                    <p className="text-asb-text-muted text-sm font-bold leading-relaxed opacity-70">{module.desc}</p>
                                </div>
                            </div>
                            <div className="mt-10 pt-6 border-t border-asb-purple/5 flex items-center justify-between">
                                <span className="text-[10px] font-bold text-asb-purple uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Explore Sphere</span>
                                <ArrowRight className="w-5 h-5 text-asb-purple transform translate-x-0 group-hover:translate-x-2 transition-transform" />
                            </div>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
