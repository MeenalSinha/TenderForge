/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
      colors: {
        navy: {
          975: '#050811', // Deepest canvas background
          950: '#080d1a', // Main page deep navy canvas
          900: '#0b1329', // Sidebar & Topbar navy
          850: '#0e1838', // Standard panel & card background
          800: '#132044', // Hover cards & active rows
          750: '#182855', // Highlight panels
          700: '#223872', // Active borders & outlines
          650: '#2c478f', // Accent borders
        },
        border: {
          subtle: '#19284d',
          muted: '#14203e',
          accent: '#233869',
          glow: 'rgba(6, 182, 212, 0.25)',
        },
        brand: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          blue: '#2563eb',
          emerald: '#10b981',
          purple: '#8b5cf6',
          amber: '#f59e0b',
        },
      },
      boxShadow: {
        'card-subtle': '0 4px 20px -2px rgba(3, 7, 18, 0.45)',
        'card-hover': '0 10px 25px -5px rgba(3, 7, 18, 0.65), 0 0 15px -3px rgba(6, 182, 212, 0.08)',
        'dropdown': '0 20px 30px -10px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(25, 40, 77, 0.8)',
        'glow-cyan': '0 0 20px -5px rgba(6, 182, 212, 0.35)',
        'glow-blue': '0 0 20px -5px rgba(37, 99, 235, 0.35)',
        'glow-emerald': '0 0 20px -5px rgba(16, 185, 129, 0.35)',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-up': 'slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pulse-subtle': 'pulseSubtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
    },
  },
  plugins: [],
}

