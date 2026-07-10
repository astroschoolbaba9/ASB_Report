import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Phone, Lock, ArrowRight, ShieldCheck, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const [phone, setPhone] = useState('');
    const [otp, setOtp] = useState('');
    const [step, setStep] = useState('phone'); // 'phone' or 'otp'
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    const { login, API_BASE } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleSSO = React.useCallback(async (token) => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_BASE}/api/auth/me`, {
                headers: { 'X-Auth-Token': token }
            });
            if (response.data.success) {
                login(token, response.data.user);
                checkRedirect(token, response.data.user);
            } else {
                setError('SSO Login failed. Invalid token.');
            }
        } catch (err) {
            setError('SSO Error: Unable to verify session.');
        } finally {
            setLoading(false);
        }
    }, [API_BASE, login, navigate]);

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const ssoToken = params.get('sso_token');
        if (ssoToken) {
            handleSSO(ssoToken);
        }
    }, [location, handleSSO]);

    const checkRedirect = (tokenVal, userObj) => {
        const params = new URLSearchParams(location.search);
        const redirectUrl = params.get('redirect');

        if (redirectUrl) {
            try {
                const url = new URL(redirectUrl);
                url.searchParams.set('token', tokenVal);
                window.location.href = url.toString();
                return;
            } catch (e) {
                console.error("Invalid redirect URL:", e);
            }
        }

        const from = location.state?.from?.pathname || '/dashboard';
        navigate(from);
    };

    const validatePhone = (p) => {
        return /^\+[1-9]\d{7,14}$/.test(p.trim().replace(/\s/g, ''));
    };

    const handleSendOTP = async (e) => {
        e.preventDefault();
        if (!validatePhone(phone)) {
            setError('Please enter a valid phone number with country code (e.g., +919999999999)');
            return;
        }

        setError('');
        setLoading(true);
        try {
            await axios.post(`${API_BASE}/api/auth/send-otp`, {
                identifier: phone.trim()
            });
            setStep('otp');
            setMessage('Secure OTP sent to your mobile.');
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to send OTP. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOTP = async (e) => {
        e.preventDefault();
        if (!otp || otp.length < 4) {
            setError('Please enter a valid OTP.');
            return;
        }

        setError('');
        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE}/api/auth/verify-otp`, {
                identifier: phone.trim(),
                otp: otp.trim(),
                code: otp.trim()
            });

            const token = res.data.token || res.data.accessToken;
            if (token) {
                const me = await axios.get(`${API_BASE}/api/auth/me`, {
                    headers: { 'X-Auth-Token': token }
                });
                if (me.data.success) {
                    login(token, me.data.user);
                    checkRedirect(token, me.data.user);
                }
            } else {
                setError('Verification failed. No token returned.');
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Invalid OTP. Please check and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 relative overflow-hidden">
            {/* Background elements */}
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-asb-purple/5 rounded-full blur-[100px] -z-10"></div>
            <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-asb-purple/5 rounded-full blur-[100px] -z-10"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="max-w-md w-full bg-white p-10 space-y-8 relative border border-asb-purple/5 shadow-2xl shadow-purple-900/5 rounded-[2.5rem]"
            >
                <div className="text-center space-y-4">
                    <div className="inline-flex p-4 rounded-2xl bg-asb-purple/5 mb-2 border border-asb-purple/5">
                        <Sparkles className="w-8 h-8 text-asb-purple" />
                    </div>
                    <h2 className="text-4xl font-numerology font-bold text-asb-text tracking-tight uppercase">Welcome Back</h2>
                    <p className="text-asb-text-muted text-[10px] font-bold tracking-widest uppercase opacity-70">Enter your cosmic credentials</p>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center space-x-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                    >
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span className="font-medium">{error}</span>
                    </motion.div>
                )}

                {message && (
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center space-x-3 p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-sm"
                    >
                        <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                        <span className="font-medium">{message}</span>
                    </motion.div>
                )}

                <AnimatePresence mode="wait">
                    {step === 'phone' ? (
                        <motion.form
                            key="phone-step"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            onSubmit={handleSendOTP}
                            className="space-y-6"
                        >
                            <div className="space-y-2">
                                <label htmlFor="mobile-input" className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest ml-1">Mobile Number</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-asb-text-muted group-focus-within:text-asb-purple transition-colors">
                                        <Phone className="h-5 w-5" />
                                    </div>
                                    <input
                                        id="mobile-input"
                                        type="tel"
                                        required
                                        placeholder="+91 00000 00000"
                                        className="block w-full pl-12 pr-4 py-4 bg-asb-bg/30 border border-asb-purple/10 rounded-2xl text-asb-text placeholder:text-asb-text-muted/40 focus:outline-none focus:ring-2 focus:ring-asb-purple/20 focus:border-asb-purple transition-all font-medium"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value)}
                                    />
                                </div>
                                <p className="text-[10px] text-asb-text-muted font-bold opacity-60 uppercase tracking-widest">Include country code (e.g. +91)</p>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="asb-button w-full disabled:opacity-50 disabled:cursor-not-allowed group"
                            >
                                {loading ? <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mx-auto" /> : (
                                    <span className="flex items-center justify-center gap-2 font-bold uppercase tracking-widest py-1 text-xs">
                                        Get Secure OTP
                                        <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                                    </span>
                                )}
                            </button>
                        </motion.form>
                    ) : (
                        <motion.form
                            key="otp-step"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            onSubmit={handleVerifyOTP}
                            className="space-y-6"
                        >
                            <div className="space-y-2 text-center">
                                <label htmlFor="otp-input" className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Verify Access Code</label>
                                <div className="relative group mt-4">
                                    <input
                                        id="otp-input"
                                        type="text"
                                        required
                                        maxLength="6"
                                        placeholder="0 0 0 0 0 0"
                                        className="block w-full py-4 bg-asb-bg/30 border border-asb-purple/10 rounded-2xl text-asb-text focus:outline-none focus:ring-2 focus:ring-asb-purple/20 focus:border-asb-purple transition-all tracking-[0.5em] text-center text-2xl font-black font-mono"
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value)}
                                    />
                                </div>
                            </div>

                            <div className="flex flex-col gap-4">
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="asb-button w-full disabled:opacity-50 disabled:cursor-not-allowed py-4 font-bold uppercase tracking-widest text-xs"
                                >
                                    {loading ? <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mx-auto" /> : 'Enter Sanctuary'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setStep('phone')}
                                    className="text-[10px] font-bold text-asb-text-muted hover:text-asb-purple transition-colors py-2 uppercase tracking-widest"
                                >
                                    Use Different Number
                                </button>
                            </div>
                        </motion.form>
                    )}
                </AnimatePresence>

                <div className="pt-8 border-t border-asb-purple/5 text-center">
                    <div className="flex items-center justify-center space-x-2 text-[10px] text-asb-text-muted font-bold uppercase tracking-widest">
                        <ShieldCheck className="w-4 h-4 text-asb-purple" />
                        <span>Cosmically Secured Connection</span>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Login;
