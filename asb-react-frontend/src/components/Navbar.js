import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Menu, X, User, LogOut, LayoutDashboard, PhoneCall, History, Phone, BookOpen } from 'lucide-react';

import asb_logo from '../assets/asb_logo.jpg';

const Navbar = () => {
    const { user, logout } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Close mobile menu on route change
    useEffect(() => {
        setIsOpen(false);
    }, [location]);

    const navLinks = [
        { name: 'Number Numerology', path: '/', icon: <History size={18} /> },
        { name: 'Mobile Numerology', path: '/mobile-numerology', icon: <Phone size={18} />, soon: true },
        { name: 'Name Numerology', path: '/name-numerology', icon: <User size={18} />, soon: true },
        { name: 'Tarot Card', path: '/tarot', icon: <BookOpen size={18} />, soon: true },
        { name: 'Consult', path: '/consult', icon: <PhoneCall size={18} /> },
    ];

    const authLinks = user ? [
        { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={18} /> },
        { name: 'Profile', path: '/profile', icon: <User size={18} /> },
    ] : [];

    const isActive = (path) => location.pathname === path;

    return (
        <nav className={`fixed w-full z-50 transition-all duration-300 ${scrolled ? 'py-2 bg-white/95 backdrop-blur-xl shadow-xl shadow-purple-900/5' : 'py-5 bg-transparent'
            }`}>
            <div className="container mx-auto px-6 flex justify-between items-center">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-3 group">
                    <div className="w-10 h-10 overflow-hidden rounded-full flex-shrink-0 border border-asb-purple/10 shadow-sm bg-white">
                        <img
                            src={asb_logo}
                            alt="ASB Logo Icon"
                            className="w-full h-full object-contain p-1.5 transition-transform group-hover:scale-110"
                        />
                    </div>
                    <span className="font-numerology font-bold text-xl text-asb-text tracking-widest uppercase mt-1">ASB Numerology</span>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden lg:flex items-center space-x-6">
                    {[...navLinks, ...authLinks].map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={`text-[12px] font-bold transition-all duration-300 flex items-center gap-1.5 ${isActive(link.path)
                                ? 'text-asb-purple'
                                : 'text-asb-text-muted hover:text-asb-purple'
                                }`}
                        >
                            <span className="whitespace-nowrap">{link.name}</span>
                            {link.soon && <span className="badge-soon">SOON</span>}
                            {isActive(link.path) && <span className="w-1 h-1 rounded-full bg-asb-purple"></span>}
                        </Link>
                    ))}

                    <a
                        href="https://asbcrystal.in"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[12px] font-bold text-asb-purple hover:opacity-80 transition-all flex items-center gap-1.5"
                    >
                        <History size={18} className="rotate-90" /> {/* Shopping cart or similar icon proxy if marketplace icon is needed */}
                        <span>Marketplace</span>
                    </a>

                    {user ? (
                        <button
                            onClick={logout}
                            className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold text-red-500 hover:bg-red-50 transition-all"
                        >
                            <LogOut size={16} />
                            Logout
                        </button>
                    ) : (
                        <Link
                            to="/login"
                            className="asb-button px-8 py-2.5 rounded-xl text-xs font-bold"
                        >
                            Login / Register
                        </Link>
                    )}
                </div>

                {/* Mobile Menu Toggle */}
                <button
                    className="lg:hidden p-2 text-asb-text hover:text-asb-purple transition-colors"
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {isOpen ? <X size={28} /> : <Menu size={28} />}
                </button>
            </div>

            <div className={`lg:hidden absolute top-full left-0 w-full overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? 'max-h-screen shadow-2xl' : 'max-h-0'
                }`}>
                <div className="bg-white px-6 py-10 flex flex-col gap-6 shadow-2xl border-t border-asb-purple/5">
                    {[...navLinks, ...authLinks].map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={`flex items-center gap-4 text-sm font-bold uppercase tracking-widest ${isActive(link.path) ? 'text-asb-purple' : 'text-asb-text'
                                }`}
                        >
                            <div className={`p-2.5 rounded-xl ${isActive(link.path) ? 'bg-asb-purple text-white' : 'bg-asb-purple/5 text-asb-purple'}`}>
                                {link.icon}
                            </div>
                            {link.name}
                        </Link>
                    ))}

                    {user ? (
                        <button
                            onClick={logout}
                            className="flex items-center gap-4 text-sm font-bold uppercase tracking-widest text-red-500 mt-4 border-t border-asb-purple/5 pt-8"
                        >
                            <div className="p-2.5 rounded-xl bg-red-50">
                                <LogOut size={18} />
                            </div>
                            Logout
                        </button>
                    ) : (
                        <Link
                            to="/login"
                            className="asb-button w-full py-4 text-center mt-4 text-sm"
                        >
                            Login / Register
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
