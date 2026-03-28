import React from 'react';

const Privacy = () => {
    return (
        <div className="container mx-auto px-4 py-20 max-w-4xl">
            <div className="glass p-8 md:p-12">
                <h1 className="text-4xl font-numerology font-bold asb-gradient-text mb-8 text-center border-b border-asb-purple/10 pb-8">Privacy Policy</h1>

                <div className="space-y-8 text-asb-text-muted leading-relaxed font-medium">
                    <section>
                        <h2 className="text-xl font-bold text-asb-text mb-4 font-numerology">1. Information We Collect</h2>
                        <p>To provide accurate numerology reports, we collect specific personal identifiers including your <strong>Full Name</strong>, <strong>Date of Birth</strong>, and <strong>Phone Number</strong> (via ASB Crystal SSO). We do not collect sensitive data like passwords or credit card numbers directly on this platform.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-asb-text mb-4">2. How We Use Your Data</h2>
                        <ul className="list-disc pl-6 space-y-2">
                            <li><strong>Calculations:</strong> Your name and DOB are used solely to generate your core destiny reports.</li>
                            <li><strong>Personalization:</strong> To tailor the dashboard and AI-driven insights to your specific vibration.</li>
                            <li><strong>Communication:</strong> Your phone number is used for authentication and sending report links.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-asb-text mb-4">3. Data Security & Encryption</h2>
                        <p>Your data is stored in secured MongoDB databases and transmitted via SSL encryption. We take the protection of your personal vibrational data seriously. We do not sell or trade your personal information to third-party marketing companies.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-asb-text mb-4">4. Third-Party Integration</h2>
                        <p>Our authentication is handled by ASB Crystal's specialized security layer. Their privacy policies also apply to the authentication phase. Our AI analysis uses advanced LLM processing, but personal identifiers are stripped or anonymized before processing.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-asb-text mb-4">5. Your Rights</h2>
                        <p>You have the right to update your profile data via the Profile page at any time. If you wish to delete your account and all associated number-data, please contact our support team at asbcrystal.in.</p>
                    </section>

                    <div className="pt-8 border-t border-asb-gold border-opacity-20 text-sm italic text-center">
                        Dedicated to protecting your digital and spiritual identity.
                        <br />
                        Last Updated: March 27, 2026
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Privacy;
