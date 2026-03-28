import React from 'react';
import { Target, Users, Sparkles, BookOpen } from 'lucide-react';

const About = () => {
    return (
        <div className="container mx-auto px-4 py-20 max-w-4xl">
            <div className="text-center mb-16">
                <h1 className="text-4xl md:text-5xl font-numerology font-bold asb-gradient-text mb-6">About ASB Numerology</h1>
                <p className="text-xl white/60 italic">"Numbers are the language of the Universe."</p>
            </div>

            <div className="space-y-16">
                <section className="asb-card">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="p-3 bg-asb-gold bg-opacity-10 rounded-xl text-asb-gold">
                            <Target size={28} />
                        </div>
                        <h2 className="text-2xl font-numerology font-bold">Our Mission</h2>
                    </div>
                    <p className="white/60 leading-relaxed">
                        Founded by Bhaskar Joshi, ASB Numerology aims to bridge the gap between ancient wisdom and modern technology. We believe that every individual is born with a unique vibrational code. Our mission is to help you decode that frequency to find your true purpose, optimize your career path, and enhance your personal relationships.
                    </p>
                </section>

                <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="asb-card-dark">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="p-3 bg-asb-purple bg-opacity-10 rounded-xl text-asb-purple">
                                <Sparkles size={28} />
                            </div>
                            <h2 className="text-2xl font-numerology font-bold">Methodology</h2>
                        </div>
                        <p className="white/60 leading-relaxed">
                            We use the Pythagorean system of numerology, combined with deep AI analysis of traditional Vedic principles. This hybrid approach ensures that our reports are both mathematically accurate and spiritually resonant.
                        </p>
                    </div>

                    <div className="asb-card-dark">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="p-3 bg-asb-magenta bg-opacity-10 rounded-xl text-asb-magenta">
                                <Users size={28} />
                            </div>
                            <h2 className="text-2xl font-numerology font-bold">Community</h2>
                        </div>
                        <p className="white/60 leading-relaxed">
                            With over 10,000 satisfied users across the globe, ASB Numerology is more than just a website; it's a growing community of individuals seeking self-actualization through the power of numbers.
                        </p>
                    </div>
                </section>

                <section className="text-center py-10">
                    <div className="inline-block p-10 glass border-asb-gold border-opacity-30 rounded-3xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <BookOpen size={100} />
                        </div>
                        <h2 className="text-3xl font-numerology font-bold mb-6">The Essence of ASB</h2>
                        <p className="text-white max-w-2xl mx-auto leading-relaxed">
                            "When you understand your numbers, you stop fighting against the current of life and start sailing with the wind of destiny."
                        </p>
                        <div className="mt-8">
                            <span className="font-numerology text-asb-gold font-bold">— Bhaskar Joshi</span>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default About;
