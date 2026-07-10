import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Chatbot from './components/Chatbot';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import CompleteProfile from './pages/CompleteProfile';
import ProfessionReport from './pages/ProfessionReport';
import HealthReport from './pages/HealthReport';
import RelationshipReport from './pages/RelationshipReport';
import SwotAnalysis from './pages/SwotAnalysis';
import TimeCycles from './pages/TimeCycles';
import PdfReport from './pages/PdfReport';
import Consult from './pages/Consult';
import MobileNumerology from './pages/MobileNumerology';
import NameNumerology from './pages/NameNumerology';
import TarotCard from './pages/TarotCard';
import About from './pages/About';
import Terms from './pages/Terms';
import Privacy from './pages/Privacy';
import NotFound from './pages/NotFound';
import ScrollToTop from './components/ScrollToTop';
import { AuthProvider, useAuth } from './context/AuthContext';
import asb_logo from './assets/asb_logo.jpg';

// Protected Route Component
const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-asb-bg">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-asb-purple"></div>
    </div>
  );

  if (!user) return <Navigate to="/login" />;

  return children;
};

// Profile Required Wrapper
const ProfileRequiredRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-asb-bg">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-asb-purple"></div>
    </div>
  );

  if (!user) return <Navigate to="/login" />;

  // Mandatory profile check - block missing or default SSO dummy values
  const isDummyName = !user.name || user.name === "User" || user.name.toLowerCase().includes("dummy");
  const isDummyDob = !user.dob || user.dob === "01-01-1970";
  const pendingName = localStorage.getItem('pending_name');
  const pendingDob = localStorage.getItem('pending_dob');

  if (isDummyName || isDummyDob || (pendingName && pendingDob)) {
    return <Navigate to="/complete-profile" />;
  }

  return children;
};

const AppContent = () => {
  return (
    <div className="min-h-screen flex flex-col bg-asb-bg relative overflow-x-hidden text-asb-text">
      <Navbar />
      <ScrollToTop />

      <main className="flex-grow pt-20 px-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/complete-profile" element={<PrivateRoute><CompleteProfile /></PrivateRoute>} />

          <Route path="/dashboard" element={<ProfileRequiredRoute><Dashboard /></ProfileRequiredRoute>} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />

          <Route path="/profession" element={<ProfileRequiredRoute><ProfessionReport /></ProfileRequiredRoute>} />
          <Route path="/health" element={<ProfileRequiredRoute><HealthReport /></ProfileRequiredRoute>} />
          <Route path="/relationship" element={<ProfileRequiredRoute><RelationshipReport /></ProfileRequiredRoute>} />
          <Route path="/swot" element={<ProfileRequiredRoute><SwotAnalysis /></ProfileRequiredRoute>} />
          <Route path="/time-cycles" element={<ProfileRequiredRoute><TimeCycles /></ProfileRequiredRoute>} />
          <Route path="/pdf-report" element={<ProfileRequiredRoute><PdfReport /></ProfileRequiredRoute>} />

          <Route path="/consult" element={<Consult />} />
          <Route path="/mobile-numerology" element={<MobileNumerology />} />
          <Route path="/name-numerology" element={<NameNumerology />} />
          <Route path="/tarot" element={<TarotCard />} />

          <Route path="/about" element={<About />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />

          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </main>

      <Chatbot />

      <footer className="bg-white py-24 border-t border-asb-purple/5">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between gap-12 lg:gap-24">
            <div className="max-w-sm space-y-8">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 overflow-hidden rounded-full flex-shrink-0 border border-asb-purple/10 shadow-sm bg-white">
                  <img src={asb_logo} alt="ASB Logo" className="w-full h-full object-contain p-1.5" />
                </div>
                <span className="text-2xl font-numerology font-bold asb-gradient-text tracking-wider uppercase">ASB NUMEROLOGY</span>
              </div>
              <p className="text-asb-text-muted text-sm leading-relaxed font-medium">
                Empowering your journey through the sacred intersection of ancient numerology and modern artificial intelligence.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-16">
              <div className="flex flex-col gap-4">
                <h4 className="font-bold text-xs uppercase tracking-widest text-asb-text mb-2">Explore</h4>
                <a href="/mobile-numerology" className="text-asb-text-muted hover:text-asb-purple transition-all text-sm font-medium">Mobile Numerology</a>
                <a href="/name-numerology" className="text-asb-text-muted hover:text-asb-purple transition-all text-sm font-medium">Name Numerology</a>
                <a href="/tarot" className="text-asb-text-muted hover:text-asb-purple transition-all text-sm font-medium">Tarot Reading</a>
                <a href="/consult" className="text-asb-text-muted hover:text-asb-purple transition-all text-sm font-medium">Book Consult</a>
                <a href="/about" className="text-asb-text-muted hover:text-asb-purple transition-all text-sm font-medium">About US</a>
              </div>
              <div className="flex flex-col gap-4">
                <h4 className="font-bold text-xs uppercase tracking-widest text-asb-text mb-2">Legal</h4>
                <a href="/terms" className="text-asb-text-muted hover:text-asb-purple transition-all text-sm font-medium">Terms</a>
                <a href="/privacy" className="text-asb-text-muted hover:text-asb-purple transition-all text-sm font-medium">Privacy</a>
              </div>
            </div>
          </div>
          <div className="border-t border-asb-purple/5 mt-20 pt-10 text-center">
            <p className="text-asb-text-muted/60 text-[10px] font-bold uppercase tracking-widest">
              © {new Date().getFullYear()} ASB Numerology. Crafted for your Spiritual Growth.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
