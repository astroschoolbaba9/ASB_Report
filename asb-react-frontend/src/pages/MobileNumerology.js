import React from 'react';
import { motion } from 'framer-motion';
import { Smartphone, Sparkles, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const MobileNumerology = () => {
    return (
        <div className="max-w-4xl mx-auto px-4 py-20 min-h-[80vh] flex flex-col justify-center">
            <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 text-asb-purple font-bold text-xs uppercase tracking-widest hover:opacity-70 transition-opacity mb-12"
            >
                <ArrowLeft size={16} /> Back to Dashboard
            </Link>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass p-16 rounded-[4rem] text-center space-y-8 relative overflow-hidden shadow-2xl shadow-purple-900/5"
            >
                <div className="absolute top-0 right-0 w-64 h-64 bg-asb-purple/5 blur-3xl rounded-full -mr-32 -mt-32" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-asb-purple/5 blur-3xl rounded-full -ml-32 -mb-32" />

                <div className="relative z-10 space-y-8">
                    <div className="inline-flex p-6 rounded-[2rem] bg-asb-purple/5 text-asb-purple shadow-xl shadow-purple-900/5">
                        <Smartphone size={48} />
                    </div>

                    <div className="space-y-4">
                        <h1 className="text-4xl md:text-5xl font-numerology font-bold text-asb-text uppercase tracking-tight">
                            Digital Cycles
                        </h1>
                        <p className="text-asb-text-muted font-bold text-[10px] uppercase tracking-[0.4em]">Mobile Frequency Analysis</p>
                    </div>

                    <p className="text-asb-text-muted text-lg max-w-md mx-auto leading-relaxed font-medium">
                        Calculating the impact of your telecommunication vibrations. The digital ether is being mapped to your numerological core.
                    </p>

                    <div className="inline-flex items-center gap-3 bg-asb-purple/5 text-asb-purple border border-asb-purple/10 px-6 py-3 rounded-2xl">
                        <Sparkles size={18} />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Synthesizing Signal</span>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default MobileNumerology;
