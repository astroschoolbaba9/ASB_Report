import React from 'react';

const Terms = () => {
    return (
        <div className="container mx-auto px-4 py-20 max-w-4xl">
            <div className="glass p-8 md:p-12">
                <h1 className="text-4xl font-numerology font-bold asb-gradient-text mb-8 text-center border-b border-asb-purple/10 pb-8">Terms of Service</h1>

                <div className="space-y-8 text-asb-text-muted leading-relaxed font-medium">
                    <section>
                        <h2 className="text-xl font-bold text-asb-text mb-4 font-numerology">1. Acceptance of Terms</h2>
                        <p>By accessing and using asbnumerology.com, you agree to be bound by these Terms of Service. If you do not agree to all terms, please do not use this site. ASB Numerology provides spiritual insights based on traditional and modern numerological systems.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">2. Nature of Services</h2>
                        <p>Our reports, analysis, and consultations are for informational and self-improvement purposes only. Numerology is an interpretive science; therefore, we do not guarantee specific outcomes or 100% predictive accuracy. These services should not replace professional medical, legal, or financial advice.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">3. User Data & Authentication</h2>
                        <p>You are responsible for providing accurate information (Name and Date of Birth). Our system relies on this data for calculations. Your account is personal and should not be shared. ASB Crystal SSO credentials are used for secure authentication.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">4. Intellectual Property</h2>
                        <p>The content, algorithms, design, and methodology generated on this website are the intellectual property of ASB Numerology and Bhaskar Joshi. You may use generated reports for personal use but may not resell our data or reverse-engineer our calculation systems.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">5. Limitation of Liability</h2>
                        <p>ASB Numerology shall not be held liable for any decisions made based on the interpretations provided. Use the information with your own intuition and common sense. We are not responsible for any direct or indirect consequences resulting from the application of our advice.</p>
                    </section>

                    <div className="pt-8 border-t border-asb-gold border-opacity-20 text-sm italic">
                        Last Updated: March 27, 2026
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Terms;
