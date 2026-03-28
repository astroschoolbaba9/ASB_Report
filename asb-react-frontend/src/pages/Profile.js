import React, { useState, useEffect } from 'react';
import { User, Calendar, Users, Save, CheckCircle2, AlertCircle, Info, Sparkles, Loader2, Star, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Profile = () => {
    const { user, token, API_BASE, login, fetchUser } = useAuth();
    const [formData, setFormData] = useState({
        name: user?.name || '',
        dob: user?.dob || '',
        gender: user?.gender || 'male'
    });
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (user) {
            setFormData({
                name: user.name || '',
                dob: user.dob || '',
                gender: user.gender || 'male'
            });
        }
    }, [user]);

    const [bulletins, setBulletins] = useState(null);
    const [bulletinsLoading, setBulletinsLoading] = useState(false);

    useEffect(() => {
        const fetchBulletins = async () => {
            if (!user?.dob) return;
            try {
                setBulletinsLoading(true);
                const [triangle, prof] = await Promise.all([
                    api.get('/api/numerology/mystical-triangle.report.json', { dob: user.dob }),
                    api.get('/api/numerology/profession.report.json', { dob: user.dob })
                ]);
                setBulletins({
                    mulank: triangle?.mulank_bhagyank?.mulank,
                    bhagyank: triangle?.mulank_bhagyank?.bhagyank,
                    coreG: triangle?.interpretations?.core?.G?.value,
                    profRating: prof?.profession?.rating_short || prof?.profession?.rating_text,
                    topProfs: prof?.profession?.professions?.slice(0, 3) || []
                });
            } catch (err) {
                console.error("Failed to fetch bulletins:", err);
            } finally {
                setBulletinsLoading(false);
            }
        };

        if (user?.dob) {
            fetchBulletins();
        }
    }, [user, token, API_BASE]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setSuccess(false);
        setError('');

        try {
            const data = await api.post('/api/auth/complete-profile', {
                name: formData.name.trim(),
                dob: formData.dob,
                gender: formData.gender.toLowerCase()
            });

            if (data.success) {
                setSuccess(true);
                await fetchUser();
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to update profile. Please try again.');
        } finally {
            localStorage.removeItem('pending_name');
            localStorage.removeItem('pending_dob');
            setLoading(false);
        }
    };

    const isProfileComplete = user?.name && user?.dob && user?.gender;

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
                        <User size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Cosmic Identity
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.3em] opacity-60">Manage your vibrational data</p>
                    </div>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
                {/* Form Panel */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="lg:col-span-6 space-y-8"
                >
                    <div className="bg-white p-10 rounded-[3rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5 space-y-8">
                        <div className="flex items-center justify-between border-b border-asb-purple/5 pb-6">
                            <h2 className="text-2xl font-numerology font-bold text-asb-text uppercase tracking-tight">Profile Essence</h2>
                            {isProfileComplete ? (
                                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20">
                                    <CheckCircle2 size={14} />
                                    <span className="text-[10px] font-bold uppercase tracking-widest">Verified</span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-asb-purple/5 text-asb-purple border border-asb-purple/5">
                                    <Info size={14} />
                                    <span className="text-[10px] font-bold uppercase tracking-widest">Incomplete</span>
                                </div>
                            )}
                        </div>

                        {success && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="p-4 rounded-2xl bg-green-500/10 text-green-400 text-[10px] font-bold uppercase tracking-widest border border-green-500/20 flex items-center gap-3"
                            >
                                <CheckCircle2 size={16} />
                                Profile updated successfully!
                            </motion.div>
                        )}

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="p-4 rounded-2xl bg-red-500/10 text-red-400 text-[10px] font-bold uppercase tracking-widest border border-red-500/20 flex items-center gap-3"
                            >
                                <AlertCircle size={16} />
                                {error}
                            </motion.div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Full Name</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-1 flex items-center pointer-events-none text-asb-purple/40 group-focus-within:text-asb-purple transition-colors">
                                        <User size={18} />
                                    </div>
                                    <input
                                        type="text"
                                        required
                                        className="asb-input w-full pl-8 bg-white"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="Name is vibrations..."
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Date of Birth</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-1 flex items-center pointer-events-none text-asb-purple/40 group-focus-within:text-asb-purple transition-colors">
                                        <Calendar size={18} />
                                    </div>
                                    <input
                                        type="date"
                                        required
                                        className="asb-input w-full pl-8 bg-white"
                                        value={formData.dob}
                                        onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-asb-text-muted opacity-60 px-1">Divine Gender</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-1 flex items-center pointer-events-none text-asb-purple/40 group-focus-within:text-asb-purple transition-colors">
                                        <Users size={18} />
                                    </div>
                                    <select
                                        className="asb-input w-full pl-8 appearance-none bg-white"
                                        value={formData.gender}
                                        onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                                    >
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="asb-button w-full py-5 rounded-2xl flex items-center justify-center gap-3"
                            >
                                {loading ? (
                                    <Loader2 className="animate-spin text-white" size={20} />
                                ) : (
                                    <Save size={20} />
                                )}
                                <span className="uppercase text-[11px] font-bold tracking-[0.2em]">Save Essential Data</span>
                            </button>
                        </form>
                    </div>

                    <div className="p-8 rounded-[2.5rem] bg-asb-purple/5 border border-asb-purple/5 flex items-center gap-5">
                        <div className="p-4 rounded-2xl bg-asb-purple/5 text-asb-purple border border-asb-purple/5">
                            <Star size={24} />
                        </div>
                        <div className="space-y-1">
                            <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Linked Security</p>
                            <p className="text-lg font-bold text-asb-text font-mono">{user?.phone}</p>
                        </div>
                    </div>
                </motion.div>

                {/* Bulletins Panel */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="lg:col-span-6 space-y-8"
                >
                    <div className="bg-white p-10 rounded-[3rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5 space-y-10 min-h-[400px]">
                        <div className="flex items-center gap-4 border-b border-asb-purple/5 pb-6">
                            <Sparkles className="text-asb-purple" size={24} />
                            <h2 className="text-2xl font-numerology font-bold text-asb-text uppercase tracking-tight">Active Bulletins</h2>
                        </div>

                        {bulletinsLoading ? (
                            <div className="flex flex-col items-center justify-center py-20 space-y-4">
                                <Loader2 className="w-12 h-12 text-asb-purple animate-spin" />
                                <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Re-calculating Soul Math...</p>
                            </div>
                        ) : bulletins ? (
                            <div className="space-y-8">
                                <div className="grid grid-cols-2 gap-6">
                                    <div className="p-6 rounded-3xl bg-asb-purple/5 border border-asb-purple/5 space-y-3">
                                        <p className="text-[10px] font-bold text-asb-purple uppercase tracking-[0.2em]">Mulank</p>
                                        <p className="text-5xl font-numerology font-bold text-asb-text">{bulletins.mulank}</p>
                                    </div>
                                    <div className="p-6 rounded-3xl bg-asb-purple/5 border border-asb-purple/5 space-y-3">
                                        <p className="text-[10px] font-bold text-asb-purple uppercase tracking-[0.2em]">Bhagyank</p>
                                        <p className="text-5xl font-numerology font-bold text-asb-text">{bulletins.bhagyank}</p>
                                    </div>
                                </div>

                                <div className="p-8 rounded-3xl bg-asb-magenta/5 border border-asb-magenta/5 space-y-4">
                                    <div className="flex items-center justify-between">
                                        <p className="text-[10px] font-bold text-asb-magenta uppercase tracking-[0.2em]">Vibration Level</p>
                                        <p className="text-4xl font-numerology font-bold text-asb-text">{bulletins.coreG}</p>
                                    </div>
                                    <p className="text-xs font-medium text-asb-text-muted leading-relaxed italic">
                                        "Your core frequency is currently oscillating at a {bulletins.coreG} level resonance."
                                    </p>
                                </div>

                                <div className="p-8 rounded-3xl bg-asb-purple/5 border border-asb-purple/5 space-y-6">
                                    <div className="space-y-1">
                                        <p className="text-[10px] font-bold text-asb-purple uppercase tracking-[0.2em]">Profession Alignment</p>
                                        <p className="text-lg font-bold text-asb-text uppercase tracking-tight">{bulletins.profRating}</p>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {bulletins.topProfs.map(p => (
                                            <span key={p} className="text-[10px] font-bold uppercase tracking-widest bg-asb-purple/5 px-4 py-2 rounded-full border border-asb-purple/5 text-asb-purple">
                                                {p}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-20 text-center space-y-6 opacity-40">
                                <div className="p-6 rounded-full border border-dashed border-asb-purple/20">
                                    <Star size={40} className="text-asb-purple" />
                                </div>
                                <p className="text-sm font-medium text-asb-text-muted max-w-[200px]">Save your profile to activate your live bulletins.</p>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default Profile;
