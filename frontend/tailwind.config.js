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
          950: '#080d1a', // Main page deep navy canvas
          900: '#0b1329', // Sidebar & Topbar navy
          850: '#0e1838', // Standard panel & card background
          800: '#122046', // Hover cards & active rows
          750: '#182956', // Highlight panels
          700: '#223872', // Active borders & outlines
        },
        border: {
          subtle: '#19284d',
          muted: '#14203e',
          accent: '#233869',
        },
        brand: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          blue: '#2563eb',
        },
      },
    },
  },
  plugins: [],
}

