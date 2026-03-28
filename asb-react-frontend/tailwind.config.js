/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'asb-purple': '#8b5cf6',
        'asb-magenta': '#d946ef',
        'asb-gold': '#D4AF37',
        'asb-bg': '#fdf8f4', // Light Cream Background
        'asb-surface': '#ffffff', // White Surface
        'asb-text': '#1e1b4b', // Deep Indigo Text
        'asb-text-muted': '#64748b', // Slate Text
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'serif': ['Playfair Display', 'serif'],
        'numerology': ['Cinzel', 'serif'], // Added for numbers and headers
      },
      backgroundImage: {
        'gradient-asb': 'linear-gradient(135deg, #fffaf3 0%, #ffffff 100%)',
        'gradient-accent': 'linear-gradient(90deg, #c84cff 0%, #6a5cff 100%)',
        'gradient-gold': 'linear-gradient(135deg, #e6c87a 0%, #b8860b 100%)',
        'sacred-pattern': "url('https://www.transparenttextures.com/patterns/cubes.png')", // Or similar subtle pattern
      },
      boxShadow: {
        'glass': '0 14px 30px rgba(17, 24, 39, 0.08)',
        'glass-hover': '0 20px 40px rgba(17, 24, 39, 0.12)',
        'glow-pink': '0 0 20px rgba(236, 72, 153, 0.3)',
        'glow-purple': '0 0 20px rgba(168, 85, 247, 0.3)',
        'glow-gold': '0 0 20px rgba(230, 200, 122, 0.3)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
