import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, ArrowRight, Shield, Clock, BookOpen, User, ShoppingCart, Star, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Home = () => {
    const { user, token } = useAuth();
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [dob, setDob] = useState('');

    const getSubdomainUrl = (subdomain, devPort) => {
        const tokenParam = token ? `?token=${token}` : '';
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return `http://${window.location.hostname}:${devPort}${tokenParam}`;
        }
        return `https://${subdomain}.asbreports.in${tokenParam}`;
    };

    const handleCalculate = (e) => {
        e.preventDefault();

        if (!name || !dob) {
            alert("Please enter both your name and date of birth to reveal your destiny.");
            return;
        }

        // Always store the input so complete-profile can auto-sync
        localStorage.setItem('pending_name', name);
        localStorage.setItem('pending_dob', dob);

        if (!user) {
            navigate('/login');
            return;
        }

        // If logged in, redirect to complete-profile to sync the new details
        navigate('/complete-profile');
    };

    const cards = [
        {
            title: 'ASB Numerology',
            desc: 'Get your full 100-page personalized cosmic blueprint based on your birth date.',
            icon: <Sparkles className="w-8 h-8 text-asb-purple" />,
            link: '/dashboard'
        },
        {
            title: 'Mobile Numerology',
            desc: 'Discover how your phone number influences your energy and success.',
            icon: <Clock className="w-8 h-8 text-asb-purple" />,
            link: getSubdomainUrl('mobile', '3003'),
            isExternal: true
        },
        {
            title: 'Name Numerology',
            desc: 'Analyze the vibration of your name and its impact on your destiny.',
            icon: <User className="w-8 h-8 text-asb-purple" />,
            link: getSubdomainUrl('name', '3002'),
            isExternal: true
        },
        {
            title: 'Tarot Card',
            desc: 'Get spiritual guidance and clarity through symbolic tarot readings.',
            icon: <BookOpen className="w-8 h-8 text-asb-purple" />,
            link: '/tarot'
        }
    ];

    return (
        <div className="space-y-24 pb-20">
            {/* Hero Section */}
            <section className="relative pt-10 md:pt-20">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-6xl aspect-square bg-asb-purple/5 rounded-full blur-3xl pointer-events-none -z-10"></div>

                <div className="text-center space-y-10">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.8 }}
                        className="space-y-6"
                    >
                        <div className="inline-flex items-center justify-center p-4 rounded-full bg-asb-purple/5 border border-asb-purple/10 mb-4">
                            <Star size={32} className="text-asb-purple/30" />
                        </div>
                        <h1 className="text-5xl md:text-8xl font-numerology font-bold tracking-tight text-asb-text leading-tight">
                            Unlock Your <span className="text-asb-purple">Cosmic Blueprint</span>
                        </h1>
                        <p className="text-lg text-asb-text-muted max-w-3xl mx-auto leading-relaxed font-medium">
                            Step into the world of ASB Numerology. Discover the ancient secrets hidden in your numbers and align your life with the cosmic vibrations of the universe.
                        </p>
                    </motion.div>

                    {/* Main Form Container */}
                    <div className="max-w-3xl mx-auto mt-12 relative">
                        <div className="relative bg-white p-8 md:p-12 rounded-[2.5rem] border border-asb-purple/5 shadow-2xl shadow-purple-900/5 overflow-hidden">
                            <form onSubmit={handleCalculate} className="grid grid-cols-1 md:grid-cols-12 gap-6 items-end relative z-10 text-left">
                                <div className="md:col-span-4 space-y-3">
                                    <label htmlFor="full-name" className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest ml-1">Your Full Name</label>
                                    <input
                                        id="full-name"
                                        type="text"
                                        placeholder="E.g. John Doe"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="w-full bg-asb-bg/30 border border-asb-purple/10 rounded-xl px-5 py-4 focus:ring-2 focus:ring-asb-purple/20 focus:border-asb-purple outline-none transition-all placeholder:text-asb-text-muted/40 text-asb-text font-medium"
                                        required
                                    />
                                </div>
                                <div className="md:col-span-4 space-y-3">
                                    <label htmlFor="dob-input" className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest ml-1">Date of Birth</label>
                                    <input
                                        id="dob-input"
                                        type="date"
                                        value={dob}
                                        placeholder="dd-mm-yyyy"
                                        onChange={(e) => setDob(e.target.value)}
                                        className="w-full bg-asb-bg/30 border border-asb-purple/10 rounded-xl px-5 py-4 focus:ring-2 focus:ring-asb-purple/20 focus:border-asb-purple outline-none transition-all text-asb-text font-medium"
                                        required
                                    />
                                </div>
                                <div className="md:col-span-4">
                                    <button
                                        type="submit"
                                        className="asb-button w-full py-4 text-sm font-bold flex items-center justify-center gap-3 active:scale-95"
                                    >
                                        Reveal My Destiny
                                        <ArrowRight size={18} />
                                    </button>
                                </div>
                            </form>
                            <div className="mt-4 text-center">
                                <p className="text-[10px] text-asb-text-muted/60 font-bold italic">
                                    ✨ Takes 30 seconds to generate your 50-page personalized blueprint.
                                </p>
                            </div>
                        </div>

                        <div className="mt-12">
                            <a
                                href="https://asbcrystal.in"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-asb-purple font-bold text-sm hover:underline flex items-center justify-center gap-2"
                            >
                                Explore Divine Remedies <ArrowRight size={16} />
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="container mx-auto px-4 max-w-7xl">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {cards.map((card, idx) => (
                        <motion.div
                            key={card.title}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: idx * 0.1 }}
                        >
                            {card.isExternal ? (
                                <a href={card.link} className="asb-card block h-full group p-10 bg-white border border-asb-purple/5">
                                    <div className="mb-8 p-5 rounded-2xl bg-asb-purple/5 group-hover:bg-asb-purple transition-all duration-300 w-fit">
                                        <div className="group-hover:text-white transition-colors">
                                            {card.icon}
                                        </div>
                                    </div>
                                    <h3 className="text-xl font-bold mb-4 text-asb-text font-numerology uppercase tracking-tight">{card.title}</h3>
                                    <p className="text-asb-text-muted leading-relaxed text-sm font-medium">{card.desc}</p>
                                </a>
                            ) : (
                                <Link to={card.link} className="asb-card block h-full group p-10 bg-white border border-asb-purple/5">
                                    <div className="mb-8 p-5 rounded-2xl bg-asb-purple/5 group-hover:bg-asb-purple transition-all duration-300 w-fit">
                                        <div className="group-hover:text-white transition-colors">
                                            {card.icon}
                                        </div>
                                    </div>
                                    <h3 className="text-xl font-bold mb-4 text-asb-text font-numerology uppercase tracking-tight">{card.title}</h3>
                                    <p className="text-asb-text-muted leading-relaxed text-sm font-medium">{card.desc}</p>
                                </Link>
                            )}
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* Marketplace CTA Section */}
            <section className="container mx-auto px-4 max-w-7xl">
                <div className="relative overflow-hidden rounded-[3rem] bg-white border border-asb-purple/5 p-8 md:p-16 flex flex-col md:flex-row items-center justify-between gap-12 shadow-2xl shadow-purple-900/5">
                    <div className="relative z-10 max-w-2xl space-y-8">
                        <div className="space-y-4">
                            <h2 className="text-3xl md:text-5xl font-numerology font-bold text-asb-text uppercase">Enhance Your <br /><span className="asb-gradient-text">Vibrational energy</span></h2>
                            <p className="text-asb-text-muted text-lg leading-relaxed font-medium">
                                Pair your numerological insights with high-vibration healing stones. Every destiny can be amplified by the right natural frequencies.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-4">
                            <div className="flex items-center gap-3 bg-asb-bg/50 px-4 py-2 rounded-full border border-asb-purple/5">
                                <Shield className="w-5 h-5 text-asb-purple" />
                                <span className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Certified Crystals</span>
                            </div>
                            <div className="flex items-center gap-3 bg-asb-bg/50 px-4 py-2 rounded-full border border-asb-purple/5">
                                <Clock className="w-5 h-5 text-asb-purple" />
                                <span className="text-[10px] font-bold text-asb-text-muted uppercase tracking-widest">Global Delivery</span>
                            </div>
                        </div>
                        <a
                            href="https://asbcrystal.in"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="asb-button flex items-center gap-3 group w-fit"
                        >
                            <ShoppingCart size={20} />
                            Visit official ASB Store
                            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                        </a>
                    </div>

                    <div className="relative w-full md:w-1/3 flex justify-center">
                        <div className="relative w-64 h-64">
                            <div className="absolute inset-0 rounded-full border-2 border-dashed border-asb-purple/10 animate-spin-slow"></div>
                            <div className="absolute inset-4 rounded-full border border-asb-purple/5 animate-reverse-spin-slow"></div>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <Sparkles className="w-24 h-24 text-asb-purple opacity-20 cosmic-float" />
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Simple Testimonial Section */}
            <section className="container mx-auto px-4 max-w-5xl text-center">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                    <div className="space-y-4">
                        <div className="text-4xl font-numerology font-bold text-asb-purple">10k+</div>
                        <p className="text-asb-text-muted text-[10px] uppercase tracking-widest font-bold">Reports Generated</p>
                    </div>
                    <div className="space-y-4">
                        <div className="text-4xl font-numerology font-bold text-asb-purple">98.4%</div>
                        <p className="text-asb-text-muted text-[10px] uppercase tracking-widest font-bold">Accuracy Rating</p>
                    </div>
                    <div className="space-y-4">
                        <div className="text-4xl font-numerology font-bold text-asb-purple">24/7</div>
                        <p className="text-asb-text-muted text-[10px] uppercase tracking-widest font-bold">AI Support</p>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Home;
