import React from 'react';
import { Link } from 'react-router-dom';
import { Home, MoveLeft } from 'lucide-react';

const NotFound = () => {
    return (
        <div className="min-h-[70vh] flex flex-col items-center justify-center px-4 py-20 text-center">
            <div className="relative mb-8">
                <h1 className="text-9xl font-numerology font-bold text-asb-gold opacity-20">404</h1>
                <div className="absolute inset-0 flex items-center justify-center">
                    <p className="text-2xl font-serif text-asb-text">Lost in the Numbers?</p>
                </div>
            </div>

            <p className="text-asb-text-muted max-w-md mx-auto mb-10 leading-relaxed">
                The cosmic frequencies for this page are out of sync. It seems this sequence of numbers doesn't exist in our celestial grid.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-4">
                <Link
                    to="/"
                    className="asb-button flex items-center gap-2 group"
                >
                    <Home size={18} className="group-hover:scale-110 transition-transform" />
                    Back to Home
                </Link>
                <button
                    onClick={() => window.history.back()}
                    className="px-8 py-3 rounded-xl border border-asb-purple/30 text-asb-purple hover:bg-asb-purple/5 transition-all flex items-center gap-2"
                >
                    <MoveLeft size={18} />
                    Go Back
                </button>
            </div>

            <div className="mt-20 opacity-30 select-none pointer-events-none">
                <div className="grid grid-cols-3 gap-8 text-4xl font-numerology text-asb-gold">
                    <span>3</span> <span>6</span> <span>9</span>
                </div>
            </div>
        </div>
    );
};

export default NotFound;
