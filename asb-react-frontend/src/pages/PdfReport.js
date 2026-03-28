import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, FileText, UserPlus, FileDown, ArrowLeft, Calendar, Loader2, Sparkles } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { formatDobForBackend } from '../utils/dateUtils';
import { Link } from 'react-router-dom';

const PdfReport = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const today = new Date();
    const [reportDate, setReportDate] = useState(today.toISOString().split('T')[0]);
    const [year, setYear] = useState(today.getFullYear().toString());
    const [month, setMonth] = useState((today.getMonth() + 1).toString());
    const [day, setDay] = useState(today.toISOString().split('T')[0]);
    const [addPartner, setAddPartner] = useState(false);
    const [partnerDate, setPartnerDate] = useState('');

    const handleDownload = async () => {
        setLoading(true);
        setError(null);

        try {
            const [y, m, d] = day.split('-');
            const formattedDay = `${d}-${m}-${y}`;

            const [ry, rm, rd] = reportDate.split('-');
            const formattedReportDate = `${rd}-${rm}-${ry}`;

            const effectiveDob = user?.dob;
            const effectiveName = user?.name || 'User';

            const params = {
                dob: formatDobForBackend(effectiveDob),
                name: effectiveName,
                mobile: user?.phone || '',
                report_date: formattedReportDate,
                year: parseInt(year),
                month: parseInt(month),
                day: formattedDay,
                gender: user?.gender || 'male',
                include_images: true
            };

            if (addPartner && partnerDate) {
                const [py, pm, pd] = partnerDate.split('-');
                params.partner = `${pd}-${pm}-${py}`;
            }

            const pdfBlob = await api.getBytes('/api/ai/master-report.pdf', params);
            const url = window.URL.createObjectURL(new Blob([pdfBlob]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `ASB-Master-Report-${effectiveName}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (err) {
            console.error('Error generating PDF:', err);
            setError('The cosmic record is currently being updated. Please try again shortly.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto px-4 space-y-12 pb-24">
            {/* Navigation & Header */}
            <div className="space-y-8 pt-10">
                <Link
                    to="/dashboard"
                    className="inline-flex items-center gap-2 text-asb-purple font-bold text-xs uppercase tracking-widest hover:opacity-70 transition-opacity"
                >
                    <ArrowLeft size={16} /> Back to Dashboard
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center space-y-6"
                >
                    <div className="inline-flex p-4 rounded-3xl bg-asb-purple/5 text-asb-purple mb-2">
                        <FileText size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Master Scroll
                        </h1>
                        <p className="text-asb-text-muted font-bold text-xs uppercase tracking-[0.3em]">Generate Complete PDF Dossier</p>
                    </div>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                {/* Configuration Panel */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="lg:col-span-7 space-y-8"
                >
                    <div className="glass p-10 rounded-[3rem] space-y-10 shadow-2xl shadow-purple-900/5">
                        <div className="flex items-center gap-4 border-b border-asb-purple/5 pb-6">
                            <FileDown className="text-asb-purple" size={24} />
                            <h2 className="text-2xl font-numerology font-bold text-asb-text uppercase">Parameters</h2>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted px-1">Issue Date</label>
                                <input
                                    type="date"
                                    value={reportDate}
                                    onChange={(e) => setReportDate(e.target.value)}
                                    className="w-full bg-asb-bg/50 border border-asb-purple/10 rounded-xl px-4 py-3 text-asb-text focus:ring-2 focus:ring-asb-purple/20 outline-none"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted px-1">Target Analysis Day</label>
                                <input
                                    type="date"
                                    value={day}
                                    onChange={(e) => setDay(e.target.value)}
                                    className="w-full bg-asb-bg/50 border border-asb-purple/10 rounded-xl px-4 py-3 text-asb-text focus:ring-2 focus:ring-asb-purple/20 outline-none"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted px-1">Prediction Year</label>
                                <input
                                    type="number"
                                    value={year}
                                    onChange={(e) => setYear(e.target.value)}
                                    className="w-full bg-asb-bg/50 border border-asb-purple/10 rounded-xl px-4 py-3 text-asb-text focus:ring-2 focus:ring-asb-purple/20 outline-none"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted px-1">Prediction Month</label>
                                <select
                                    value={month}
                                    onChange={(e) => setMonth(e.target.value)}
                                    className="w-full bg-asb-bg/50 border border-asb-purple/10 rounded-xl px-4 py-3 text-asb-text focus:ring-2 focus:ring-asb-purple/20 outline-none"
                                >
                                    {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                                        <option key={m} value={m}>
                                            {new Date(2000, m - 1, 1).toLocaleString('default', { month: 'long' })}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="space-y-6 pt-6 border-t border-asb-purple/5">
                            <div className="flex items-center justify-between">
                                <div className="space-y-1">
                                    <h3 className="text-lg font-numerology font-bold text-asb-text uppercase">Relationship Data</h3>
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Include compatibility analysis</p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={addPartner}
                                        onChange={(e) => setAddPartner(e.target.checked)}
                                    />
                                    <div className="w-11 h-6 bg-asb-purple/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-asb-purple"></div>
                                </label>
                            </div>

                            <AnimatePresence>
                                {addPartner && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="p-6 rounded-3xl bg-asb-purple/5 border border-asb-purple/10 space-y-4"
                                    >
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-asb-purple opacity-70 px-1">Partner's Birth Date</label>
                                            <input
                                                type="date"
                                                value={partnerDate}
                                                onChange={(e) => setPartnerDate(e.target.value)}
                                                className="w-full bg-white border border-asb-purple/10 rounded-xl px-4 py-3 text-asb-text focus:ring-2 focus:ring-asb-purple/20 outline-none"
                                            />
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </motion.div>

                {/* Summary & Actions */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="lg:col-span-5 space-y-8"
                >
                    <div className="glass p-10 rounded-[3rem] space-y-8 text-asb-text shadow-2xl shadow-purple-900/5">
                        <div className="space-y-4">
                            <h2 className="text-3xl font-numerology font-bold uppercase tracking-tight">Ready for Transmission</h2>
                            <p className="text-sm font-medium text-asb-text-muted leading-relaxed">
                                Your Master Report includes 40+ pages of detailed analysis covering your Core Numbers, Health Vibrations, Career Path, and specific Yearly/Monthly/Daily predictions.
                            </p>
                        </div>

                        <div className="space-y-4 pt-4">
                            <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-asb-purple">
                                <Sparkles size={16} />
                                <span>High-Resolution Graphics</span>
                            </div>
                            <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-asb-purple">
                                <Sparkles size={16} />
                                <span>AI-Powered Logic</span>
                            </div>
                            <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-asb-purple">
                                <Sparkles size={16} />
                                <span>Sacred Geometry Design</span>
                            </div>
                        </div>

                        {error && (
                            <div className="p-4 rounded-2xl bg-red-50 text-red-500 text-[10px] font-bold uppercase tracking-widest border border-red-100">
                                {error}
                            </div>
                        )}

                        <button
                            onClick={handleDownload}
                            disabled={loading || (addPartner && !partnerDate)}
                            className="asb-button w-full py-6 rounded-2xl flex flex-col items-center justify-center gap-2 group relative overflow-hidden"
                        >
                            {loading ? (
                                <Loader2 className="animate-spin" size={24} />
                            ) : (
                                <Download size={24} />
                            )}
                            <span className="uppercase text-[11px] font-bold tracking-[0.2em]">Generate Full Report</span>
                        </button>
                        <p className="text-[9px] text-center text-asb-text-muted uppercase font-bold tracking-widest opacity-60">PDF format • Optimized for printing</p>
                    </div>

                    <div className="glass p-8 rounded-[2.5rem] flex items-center gap-4 shadow-xl shadow-purple-900/5">
                        <div className="p-3 rounded-2xl bg-asb-purple/5 text-asb-purple">
                            <UserPlus size={20} />
                        </div>
                        <div>
                            <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Identity Verified</p>
                            <p className="text-sm font-bold text-asb-text uppercase">{user?.name}</p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default PdfReport;
