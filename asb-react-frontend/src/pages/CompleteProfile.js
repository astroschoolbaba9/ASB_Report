import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Calendar, ArrowRight, Sparkles, Loader2, AlertCircle, CheckCircle2, Heart, ShieldCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const CompleteProfile = () => {
    const { user, token, API_BASE, fetchUser } = useAuth();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        name: user?.name === 'User' ? '' : (user?.name || ''),
        dob: '',
        gender: 'male'
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [step, setStep] = useState(1); // 1: Name, 2: DOB/Gender, 3: Success, 4: Auto-Syncing

    // Auto-fill from localStorage if guest data exists
    useEffect(() => {
        const pendingName = localStorage.getItem('pending_name');
        const pendingDob = localStorage.getItem('pending_dob');

        if (pendingName || pendingDob) {
            setFormData(prev => ({
                ...prev,
                name: pendingName || prev.name,
                dob: pendingDob || prev.dob
            }));

            // Auto-submit if both are present for a seamless flow
            if (pendingName && pendingDob) {
                setStep(4); // Show syncing state
                handleAutoSubmit(pendingName, pendingDob);
            }
        }
    }, []);

    const handleAutoSubmit = async (pName, pDob) => {
        setLoading(true);
        try {
            await submitProfile(pName, pDob, 'male');
            localStorage.removeItem('pending_name');
            localStorage.removeItem('pending_dob');
        } catch (err) {
            setStep(1); // Fallback to manual if auto fails
            setError('Could not automatically sync your data. Please complete manually.');
        } finally {
            setLoading(false);
        }
    };

    const submitProfile = async (name, dob, gender) => {
        // Backend expects DD-MM-YYYY
        let formattedDob = dob;
        if (dob.includes('-') && dob.split('-')[0].length === 4) {
            const [y, m, d] = dob.split('-');
            formattedDob = `${d}-${m}-${y}`;
        }

        const data = await api.post('/api/auth/complete-profile', {
            name: name.trim(),
            dob: formattedDob,
            gender: gender.toLowerCase()
        });

        // Backend proxy might return the user directly, or {success: true}
        if (data.success !== false) {
            await fetchUser();
            setStep(3); // Success
            setTimeout(() => navigate('/dashboard'), 2000);
        } else {
            throw new Error(data.message || 'Failed to update profile via API.');
        }
        return data;
    };

    const handleNext = () => {
        if (step === 1 && !formData.name.trim()) {
            setError('Please enter your full name');
            return;
        }
        setError('');
        setStep(step + 1);
    };

    const handleBack = () => {
        setError('');
        setStep(step - 1);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.dob) {
            setError('Please select your date of birth');
            return;
        }
        setLoading(true);
        setError('');
        try {
            await submitProfile(formData.name, formData.dob, formData.gender);
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to update profile. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 relative overflow-hidden">
            {/* Cosmic Background */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none -z-10 bg-asb-bg">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-asb-purple/5 rounded-full blur-[120px] animate-pulse"></div>
                <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-asb-purple/5 rounded-full blur-[120px] animate-pulse delay-1000"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="max-w-lg w-full bg-white p-10 md:p-12 space-y-8 relative border border-asb-purple border-opacity-5 shadow-2xl shadow-purple-900/10 rounded-[3rem]"
            >
                <div className="text-center space-y-4">
                    <div className="inline-flex p-4 rounded-2xl bg-asb-purple/5 mb-2 border border-asb-purple border-opacity-5">
                        <Sparkles className="w-8 h-8 text-asb-purple" />
                    </div>
                    <h2 className="text-4xl font-numerology font-bold text-asb-text tracking-tight uppercase">Complete Profile</h2>
                    <p className="text-asb-text-muted text-sm font-semibold tracking-wide uppercase opacity-70">Aligning your cosmic energy</p>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start gap-3"
                    >
                        <AlertCircle className="h-5 w-5 shrink-0" />
                        <p className="font-medium">{error}</p>
                    </motion.div>
                )}

                <AnimatePresence mode="wait">
                    {step === 4 && (
                        <motion.div
                            key="auto-sync"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center py-12 space-y-8"
                        >
                            <div className="relative flex justify-center">
                                <div className="absolute inset-0 animate-ping bg-asb-gold rounded-full opacity-5"></div>
                                <Loader2 className="h-16 w-16 animate-spin text-asb-gold relative z-10" />
                            </div>
                            <div className="space-y-3">
                                <h3 className="text-2xl font-numerology font-bold text-asb-text uppercase">Fulfilling Your Destiny</h3>
                                <p className="text-asb-text-muted font-medium tracking-wide">Syncing your data from the cosmic gateway...</p>
                            </div>
                        </motion.div>
                    )}

                    {step === 1 && (
                        <motion.div
                            key="step1"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div className="space-y-3">
                                <label className="text-xs font-bold text-asb-text-muted uppercase tracking-widest ml-1 flex items-center gap-2">
                                    <User size={14} className="text-asb-purple" /> Your Full Name
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full bg-asb-purple/5 border border-asb-purple/5 rounded-2xl py-5 px-6 text-asb-text placeholder:text-asb-text/20 focus:outline-none focus:ring-2 focus:ring-asb-purple focus:border-transparent transition-all font-medium text-lg"
                                    placeholder="Enter birth name"
                                    required
                                />
                                <p className="text-[10px] text-asb-text-muted font-bold opacity-60 uppercase tracking-tighter">Use your full legal name for maximum vibrational accuracy</p>
                            </div>

                            <button
                                onClick={handleNext}
                                className="asb-button w-full py-5 text-base font-bold flex items-center justify-center gap-3 uppercase tracking-widest"
                            >
                                Continue Path <ArrowRight className="h-5 w-5" />
                            </button>
                        </motion.div>
                    )}

                    {step === 2 && (
                        <motion.div
                            key="step2"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div className="space-y-3">
                                <label className="text-xs font-bold text-asb-text-muted uppercase tracking-widest ml-1 flex items-center gap-2">
                                    <Calendar size={14} className="text-asb-purple" /> Date of Birth
                                </label>
                                <input
                                    type="date"
                                    value={formData.dob}
                                    onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
                                    className="w-full bg-asb-purple/5 border border-asb-purple/5 rounded-2xl py-5 px-6 text-asb-text focus:outline-none focus:ring-2 focus:ring-asb-purple focus:border-transparent transition-all font-medium text-lg"
                                    required
                                />
                            </div>

                            <div className="space-y-3">
                                <label className="text-xs font-bold text-asb-text-muted uppercase tracking-widest ml-1 flex items-center gap-2">
                                    <Heart size={14} className="text-asb-purple" /> Vital Energy
                                </label>
                                <div className="grid grid-cols-2 gap-4">
                                    {['Male', 'Female'].map((g) => (
                                        <button
                                            key={g}
                                            type="button"
                                            onClick={() => setFormData({ ...formData, gender: g.toLowerCase() })}
                                            className={`py-4 rounded-2xl border-2 font-bold uppercase tracking-widest text-xs transition-all ${formData.gender === g.toLowerCase()
                                                ? 'bg-asb-purple/5 border-asb-purple text-asb-purple shadow-sm'
                                                : 'bg-asb-purple/5 border-asb-purple/5 text-asb-text-muted opacity-60 hover:opacity-100 hover:border-asb-purple/20'
                                                }`}
                                        >
                                            {g}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button
                                    onClick={handleBack}
                                    className="flex-1 bg-asb-purple/5 border border-asb-purple/5 text-asb-text-muted font-bold py-5 rounded-2xl hover:bg-asb-purple/10 transition-all uppercase tracking-widest text-xs"
                                >
                                    Back
                                </button>
                                <button
                                    onClick={handleSubmit}
                                    disabled={loading}
                                    className="asb-button flex-[2] py-5 font-bold uppercase tracking-widest"
                                >
                                    {loading ? <Loader2 className="h-6 w-6 animate-spin mx-auto text-white" /> : 'Finalize Connection'}
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {step === 3 && (
                        <motion.div
                            key="step3"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="text-center py-12 space-y-6"
                        >
                            <div className="inline-flex items-center justify-center h-24 w-24 rounded-full bg-green-500/10 text-green-400 mb-2 border border-green-500/20 shadow-sm animate-bounce">
                                <CheckCircle2 className="h-12 w-12" />
                            </div>
                            <div className="space-y-3">
                                <h3 className="text-3xl font-numerology font-bold text-asb-text uppercase">Universe Aligned</h3>
                                <p className="text-asb-text-muted font-medium tracking-wide">
                                    Your profile is complete. The numbers are speaking. <br />Redirecting to your sanctuary...
                                </p>
                            </div>
                            <div className="flex justify-center mt-8">
                                <Loader2 className="h-8 w-8 animate-spin text-asb-gold" />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {step < 3 && step !== 4 && (
                    <div className="pt-10 border-t border-asb-purple border-opacity-10">
                        <div className="flex justify-between items-center px-2">
                            <div className="flex gap-3">
                                {[1, 2].map((i) => (
                                    <div
                                        key={i}
                                        className={`h-2 rounded-full transition-all duration-500 ${step === i ? 'w-10 bg-asb-purple' : 'w-3 bg-asb-purple/20'}`}
                                    />
                                ))}
                            </div>
                            <div className="flex items-center gap-2 text-[10px] text-asb-text-muted font-bold uppercase tracking-widest opacity-60">
                                <ShieldCheck size={12} className="text-asb-purple" />
                                End-to-End Encryption
                            </div>
                        </div>
                    </div>
                )}
            </motion.div>
        </div>
    );
};

export default CompleteProfile;
