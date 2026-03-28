import React from 'react';
import { motion } from 'framer-motion';
import { Phone, Mail, Clock, MapPin, Sparkles, BookOpen, Star, Sun, ArrowLeft, MessageSquare } from 'lucide-react';
import { Link } from 'react-router-dom';

const Consult = () => {
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
                    <div className="inline-flex p-4 rounded-3xl bg-asb-purple/5 text-asb-purple mb-2 border border-asb-purple/5">
                        <MessageSquare size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-6xl font-numerology font-bold text-asb-text tracking-tight uppercase">
                            Cosmic Counsel
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.3em] opacity-60">Personalized consultation & remedies</p>
                    </div>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left: Contact Info */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="lg:col-span-7 space-y-8"
                >
                    <div className="bg-white p-10 rounded-[3rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5 space-y-10">
                        <div className="flex items-center gap-4 border-b border-asb-purple/5 pb-6">
                            <Sparkles className="text-asb-purple" size={24} />
                            <h2 className="text-2xl font-numerology font-bold text-asb-text uppercase tracking-tight">Direct Access</h2>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="p-8 rounded-3xl bg-asb-purple/5 border border-asb-purple/5 space-y-4">
                                <div className="p-3 rounded-2xl bg-asb-violet/5 text-asb-violet w-fit border border-asb-violet/5">
                                    <Phone size={24} />
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">WhatsApp / Call</p>
                                    <p className="text-xl font-bold text-asb-text">+91-9911500291</p>
                                </div>
                            </div>

                            <div className="p-8 rounded-3xl bg-asb-purple/5 border border-asb-purple/5 space-y-4">
                                <div className="p-3 rounded-2xl bg-asb-magenta/5 text-asb-magenta w-fit border border-asb-magenta/5">
                                    <Mail size={24} />
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest opacity-60">Official Email</p>
                                    <p className="text-sm font-bold text-asb-text break-words">astroschoolbaba@gmail.com</p>
                                </div>
                            </div>
                        </div>

                        <div className="p-8 rounded-[2.5rem] bg-asb-purple/5 border border-asb-purple/5 space-y-6">
                            <h3 className="text-lg font-numerology font-bold text-asb-text uppercase tracking-tight flex items-center gap-3">
                                <BookOpen className="text-asb-purple" size={20} />
                                Spheres of Guidance
                            </h3>
                            <ul className="grid grid-cols-1 gap-4">
                                {[
                                    'Personal numerology & name corrections',
                                    'Career & profession direction',
                                    'Relationship insights & compatibility',
                                    'Health rhythm & lifestyle alignment',
                                    'Time-cycle based planning'
                                ].map((item, idx) => (
                                    <li key={idx} className="flex items-center gap-4 p-4 rounded-2xl bg-white border border-asb-purple/5">
                                        <div className="w-2 h-2 rounded-full bg-asb-magenta" />
                                        <span className="text-sm font-medium text-asb-text-muted">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </motion.div>

                {/* Right: Slots & Schedule */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="lg:col-span-5 space-y-8"
                >
                    <div className="bg-white p-10 rounded-[3rem] border border-asb-purple/5 shadow-xl shadow-purple-900/5 space-y-10">
                        <div className="flex items-center gap-4 border-b border-asb-purple/5 pb-6">
                            <Clock className="text-asb-purple" size={24} />
                            <h2 className="text-2xl font-numerology font-bold text-asb-text uppercase tracking-tight">Cosmic Slots</h2>
                        </div>

                        <div className="space-y-6">
                            <div className="p-6 rounded-3xl bg-asb-purple/5 border border-asb-purple/5 space-y-4">
                                <div className="flex items-center gap-3">
                                    <Sun className="text-asb-purple" size={18} />
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Weekdays</p>
                                </div>
                                <p className="text-2xl font-numerology font-bold text-asb-text">6:00 PM – 9:00 PM</p>
                                <p className="text-[10px] font-bold text-asb-purple uppercase tracking-widest opacity-60">IST Timezone</p>
                            </div>

                            <div className="p-6 rounded-3xl bg-asb-purple/5 border border-asb-purple/5 space-y-4">
                                <div className="flex items-center gap-3">
                                    <Star className="text-asb-violet" size={18} />
                                    <p className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Weekends</p>
                                </div>
                                <p className="text-2xl font-numerology font-bold text-asb-text">11:00 AM – 5:00 PM</p>
                                <p className="text-[10px] font-bold text-asb-purple uppercase tracking-widest opacity-60">IST Timezone</p>
                            </div>
                        </div>

                        <div className="p-6 rounded-2xl bg-asb-purple/5 border border-asb-purple/5">
                            <p className="text-[10px] font-bold text-asb-purple leading-relaxed uppercase tracking-widest text-center">
                                Slots are limited.
                                <br />Booking in advance is highly recommended.
                            </p>
                        </div>
                    </div>

                    <div className="p-6 text-center opacity-40">
                        <p className="text-[10px] uppercase font-bold text-asb-text-muted tracking-widest leading-relaxed">
                            Guidance is intended for reflection.
                            <br />Not a substitute for professional expertise.
                        </p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default Consult;
