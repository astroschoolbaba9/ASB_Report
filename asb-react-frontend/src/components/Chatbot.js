import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, RotateCcw, Send, Calendar, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Chatbot = () => {
    const { user, token } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [inputType, setInputType] = useState('text');
    const [inputPlaceholder, setInputPlaceholder] = useState('Type here...');
    const [isTyping, setIsTyping] = useState(false);
    const [stepInfo, setStepInfo] = useState({ step: 0, total_steps: 6 });
    const chatEndRef = useRef(null);

    const API_BASE = process.env.REACT_APP_API_BASE || (
        window.location.hostname.includes('asbreports.in')
            ? 'https://api.asbreports.in'
            : `http://${window.location.hostname}:8001`
    );

    // Retrieve or create Session ID
    const getSessionId = () => {
        let sid = sessionStorage.getItem('asb_chat_session_id');
        if (!sid) {
            sid = 'sess_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
            sessionStorage.setItem('asb_chat_session_id', sid);
        }
        return sid;
    };

    // Auto-scroll to bottom of messages
    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isTyping]);

    // Restore state from LocalStorage on mount
    useEffect(() => {
        const savedHistory = localStorage.getItem('asb_chat_history');
        const savedInputMode = localStorage.getItem('asb_chat_input_mode');
        const savedStep = localStorage.getItem('asb_chat_step');

        if (savedHistory) {
            try {
                const parsed = JSON.parse(savedHistory);
                setMessages(parsed.map(msg => ({
                    ...msg,
                    text: msg.text || ''
                })));
            } catch (e) {
                console.error(e);
            }
        }
        if (savedInputMode) {
            try {
                const mode = JSON.parse(savedInputMode);
                setInputType(mode.inputType || 'text');
                setInputPlaceholder(mode.inputPlaceholder || 'Type here...');
            } catch (e) {
                console.error(e);
            }
        }
        if (savedStep) {
            try {
                setStepInfo(JSON.parse(savedStep));
            } catch (e) {
                console.error(e);
            }
        }
    }, []);

    // Save history to LocalStorage whenever it changes
    const persistState = (newMessages, newType, newPlaceholder, newStep) => {
        localStorage.setItem('asb_chat_history', JSON.stringify(newMessages));
        localStorage.setItem('asb_chat_input_mode', JSON.stringify({ inputType: newType, inputPlaceholder: newPlaceholder }));
        localStorage.setItem('asb_chat_step', JSON.stringify(newStep));
    };

    // Initialize the Chat Session (Welcome and First Question)
    const initChat = async (forceReset = false) => {
        setIsTyping(true);
        const welcomeText = `🙏 Namaste! Welcome to ASB AI Advisor.\n\nI'm your AI Numerology Expert.\n\nI'll guide you step-by-step to provide personalized numerology insights based on your details.\n\nLet's begin.`;
        
        let initialMessages = [];
        if (!forceReset) {
            initialMessages = [
                { sender: 'bot', text: welcomeText }
            ];
            setMessages(initialMessages);
        }

        try {
            const sid = getSessionId();
            
            // Build profile payload if logged in
            let userProfile = null;
            if (user && user.name && user.dob && user.name !== 'User' && user.dob !== '01-01-1970') {
                userProfile = {
                    name: user.name,
                    dob: user.dob,
                    gender: user.gender || 'Other'
                };
            }

            const response = await axios.post(`${API_BASE}/api/chatbot/chat`, {
                message: 'start',
                session_id: sid,
                user_profile: userProfile
            });

            const data = response.data;
            const updatedMessages = [
                ...initialMessages,
                {
                    sender: 'bot',
                    text: data.answer,
                    buttons: data.buttons || null,
                    type: data.type || null,
                    services: data.services || null
                }
            ];

            const newStep = { step: data.step || 0, total_steps: data.total_steps || 6 };
            setMessages(updatedMessages);
            setInputType(data.input_type || 'text');
            setInputPlaceholder(data.placeholder || 'Type here...');
            setStepInfo(newStep);
            
            persistState(updatedMessages, data.input_type || 'text', data.placeholder || 'Type here...', newStep);
        } catch (error) {
            console.error(error);
            const errorMessages = [
                ...initialMessages,
                { sender: 'bot', text: '⚠️ Unable to connect to ASB AI server. Please check your internet connection and try again.' }
            ];
            setMessages(errorMessages);
        } finally {
            setIsTyping(false);
        }
    };

    // Initialize automatically when user opens the chat for the first time
    useEffect(() => {
        if (isOpen && messages.length === 0) {
            initChat();
        }
    }, [isOpen]);

    // Reset Chat Flow
    const handleReset = () => {
        localStorage.removeItem('asb_chat_history');
        localStorage.removeItem('asb_chat_input_mode');
        localStorage.removeItem('asb_chat_step');
        sessionStorage.removeItem('asb_chat_session_id');
        setMessages([]);
        setInputType('text');
        setInputPlaceholder('Type here...');
        setStepInfo({ step: 0, total_steps: 6 });
        
        // Generate new session and restart
        setTimeout(() => {
            initChat(true);
        }, 100);
    };

    // Send chat message to backend
    const handleSendMessage = async (msgText) => {
        if (!msgText.trim()) return;

        const updatedMessages = [
            ...messages,
            { sender: 'user', text: msgText }
        ];

        setMessages(updatedMessages);
        setInputText('');
        setInputType('button_only'); // Disable input temporarily
        setIsTyping(true);

        try {
            const sid = getSessionId();
            let userProfile = null;
            if (user && user.name && user.dob) {
                userProfile = {
                    name: user.name,
                    dob: user.dob,
                    gender: user.gender || 'Other'
                };
            }

            const response = await axios.post(`${API_BASE}/api/chatbot/chat`, {
                message: msgText,
                session_id: sid,
                user_profile: userProfile
            });

            const data = response.data;
            const finalMessages = [
                ...updatedMessages,
                {
                    sender: 'bot',
                    text: data.answer,
                    buttons: data.buttons || null,
                    type: data.type || null,
                    services: data.services || null
                }
            ];

            const newStep = { step: data.step || 0, total_steps: data.total_steps || 6 };
            setMessages(finalMessages);
            setInputType(data.input_type || 'text');
            setInputPlaceholder(data.placeholder || 'Type here...');
            setStepInfo(newStep);

            persistState(finalMessages, data.input_type || 'text', data.placeholder || 'Type here...', newStep);
        } catch (error) {
            console.error(error);
            const errMessages = [
                ...updatedMessages,
                { sender: 'bot', text: '⚠️ Connection lost. Unable to fetch guidance.' }
            ];
            setMessages(errMessages);
            setInputType('text');
        } finally {
            setIsTyping(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage(inputText);
        }
    };

    // Progress Bar percentage calculation
    const progressPercent = stepInfo.step && stepInfo.total_steps
        ? (stepInfo.step / stepInfo.total_steps) * 100
        : 0;

    return (
        <>
            {/* Floating Launcher Button */}
            <motion.button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-to-r from-asb-gold via-asb-magenta to-asb-purple text-white rounded-full flex items-center justify-center shadow-lg hover:shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300 cursor-pointer group"
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.95 }}
            >
                <AnimatePresence mode="wait">
                    {isOpen ? (
                        <motion.span
                            key="close"
                            initial={{ rotate: -90, opacity: 0 }}
                            animate={{ rotate: 0, opacity: 1 }}
                            exit={{ rotate: 90, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <X size={24} />
                        </motion.span>
                    ) : (
                        <motion.span
                            key="chat"
                            initial={{ scale: 0.5, rotate: 90, opacity: 0 }}
                            animate={{ scale: 1, rotate: 0, opacity: 1 }}
                            exit={{ scale: 0.5, rotate: -90, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="relative flex items-center justify-center w-full h-full"
                        >
                            <MessageSquare size={24} />
                            <span className="absolute inline-flex h-full w-full rounded-full bg-asb-purple/20 animate-ping group-hover:animate-none"></span>
                        </motion.span>
                    )}
                </AnimatePresence>
            </motion.button>

            {/* Chat Panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 50, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 50, scale: 0.95 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed bottom-24 right-6 w-96 max-w-[calc(100vw-2rem)] h-[580px] max-h-[calc(100vh-8rem)] z-50 flex flex-col bg-white/95 backdrop-blur-xl rounded-[2rem] border border-asb-purple/10 overflow-hidden shadow-2xl shadow-purple-900/10"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-asb-purple to-asb-magenta p-4 text-white flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="p-1.5 bg-white/10 rounded-full border border-white/20">
                                    <Sparkles size={16} className="text-asb-gold animate-pulse" />
                                </div>
                                <div>
                                    <h3 className="font-numerology font-bold text-sm tracking-wide uppercase">ASB AI Advisor</h3>
                                    <p className="text-[10px] text-white/70 font-semibold flex items-center gap-1.5">
                                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-ping"></span>
                                        Online • Numerology Expert
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <button
                                    onClick={handleReset}
                                    title="Reset chat"
                                    className="p-1.5 hover:bg-white/10 rounded-lg transition-colors cursor-pointer text-white/80 hover:text-white"
                                >
                                    <RotateCcw size={16} />
                                </button>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="p-1.5 hover:bg-white/10 rounded-lg transition-colors cursor-pointer text-white/80 hover:text-white"
                                >
                                    <X size={16} />
                                </button>
                            </div>
                        </div>

                        {/* Progress Indicator */}
                        {stepInfo.step > 0 && stepInfo.step <= stepInfo.total_steps && (
                            <div className="w-full bg-asb-purple/5 h-1 relative overflow-hidden">
                                <div
                                    className="bg-gradient-to-r from-asb-gold to-asb-purple h-full transition-all duration-500 ease-out"
                                    style={{ width: `${progressPercent}%` }}
                                ></div>
                            </div>
                        )}

                        {/* Messages Box */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-asb-bg/40">
                            {messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`flex flex-col ${
                                        msg.sender === 'user' ? 'items-end' : 'items-start'
                                    } space-y-1`}
                                >
                                    {/* Step Badge */}
                                    {msg.sender === 'bot' && msg.step && msg.total_steps && msg.step <= msg.total_steps && (
                                        <span className="text-[8px] font-bold text-asb-purple bg-asb-purple/10 px-2 py-0.5 rounded-full ml-1 uppercase tracking-wider">
                                            Step {msg.step} of {msg.total_steps}
                                        </span>
                                    )}

                                    {/* Message Bubble */}
                                    <div
                                        className={`p-3.5 rounded-2xl max-w-[85%] text-xs leading-relaxed font-medium shadow-sm transition-all duration-300 ${
                                            msg.sender === 'user'
                                                ? 'bg-gradient-to-r from-asb-purple to-asb-magenta text-white rounded-tr-none'
                                                : 'bg-white border border-asb-purple/5 text-asb-text rounded-tl-none'
                                        }`}
                                        dangerouslySetInnerHTML={{
                                            __html: (msg.text || '').replace(/\n/g, '<br/>')
                                        }}
                                    ></div>

                                    {/* Option Buttons (Pills) */}
                                    {msg.buttons && (
                                        <div className="flex flex-wrap gap-1.5 pt-1.5 max-w-[90%]">
                                            {msg.buttons.map((btnText, bIdx) => (
                                                <button
                                                    key={bIdx}
                                                    onClick={() => handleSendMessage(btnText)}
                                                    className="px-3 py-1.5 bg-white text-asb-purple border border-asb-purple/10 hover:border-asb-purple/30 hover:bg-asb-purple/5 active:scale-95 text-[11px] font-bold rounded-full transition-all cursor-pointer shadow-sm"
                                                >
                                                    {btnText}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                    {/* Recommended Services Grid */}
                                    {msg.type === 'service_cards' && msg.services && (
                                        <div className="grid grid-cols-2 gap-2 pt-2 w-full max-w-[95%]">
                                            {msg.services.map((service, sIdx) => (
                                                <a
                                                    key={sIdx}
                                                    href={service.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="px-3 py-2.5 bg-white border border-asb-purple/5 hover:border-asb-purple/20 hover:bg-asb-purple/5 text-center text-[10px] font-bold rounded-xl text-asb-text hover:text-asb-purple shadow-sm transition-all flex items-center justify-center cursor-pointer active:scale-98"
                                                >
                                                    {service.title}
                                                </a>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}

                            {/* Typing Indicator */}
                            {isTyping && (
                                <div className="flex flex-col items-start space-y-1">
                                    <div className="p-3.5 bg-white border border-asb-purple/5 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-1.5">
                                        <span className="text-[10px] text-asb-text-muted/70 font-semibold italic animate-pulse mr-1">Preparing guidance</span>
                                        <div className="flex gap-1 items-center">
                                            <span className="w-1.5 h-1.5 bg-asb-purple/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                            <span className="w-1.5 h-1.5 bg-asb-purple/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                            <span className="w-1.5 h-1.5 bg-asb-purple/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div ref={chatEndRef} />
                        </div>

                        {/* Input Footer */}
                        <div className="p-3 bg-white border-t border-asb-purple/5 flex items-center gap-2">
                            {inputType === 'date' ? (
                                <div className="flex-1 relative flex items-center">
                                    <input
                                        type="date"
                                        value={inputText}
                                        onChange={(e) => setInputText(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        className="w-full pl-3 pr-8 py-2 text-xs border border-asb-purple/10 rounded-xl focus:border-asb-purple/30 outline-none font-medium text-asb-text"
                                    />
                                    <Calendar size={14} className="absolute right-3 text-asb-purple/40 pointer-events-none" />
                                </div>
                            ) : (
                                <input
                                    type="text"
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder={inputPlaceholder}
                                    disabled={inputType === 'button_only'}
                                    className="flex-grow px-4 py-2.5 text-xs border border-asb-purple/10 rounded-xl focus:border-asb-purple/30 outline-none font-medium text-asb-text disabled:bg-asb-bg/20 disabled:text-asb-text-muted/60 disabled:cursor-not-allowed"
                                />
                            )}

                            <button
                                onClick={() => handleSendMessage(inputText)}
                                disabled={inputType === 'button_only' || !inputText.trim()}
                                className="p-2.5 bg-gradient-to-r from-asb-purple to-asb-magenta text-white rounded-xl shadow-md hover:scale-103 active:scale-95 transition-all cursor-pointer disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed"
                            >
                                <Send size={14} />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
};

export default Chatbot;
