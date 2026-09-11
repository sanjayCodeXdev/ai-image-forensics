/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        ai:   { DEFAULT: '#ef4444', light: '#fef2f2', dark: '#991b1b' },
        real: { DEFAULT: '#22c55e', light: '#f0fdf4', dark: '#15803d' },
        inconclusive: { DEFAULT: '#f59e0b', light: '#fffbeb', dark: '#92400e' },
        surface: {
          DEFAULT: '#0f172a',
          card:    '#1e293b',
          border:  '#334155',
        },
      },
      animation: {
        'fade-in':    'fadeIn 0.4s ease-out',
        'slide-up':   'slideUp 0.4s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'spin-slow':  'spin 3s linear infinite',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 },                to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(20px)' },
                   to:   { opacity: 1, transform: 'translateY(0)' } },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-pattern':
          'radial-gradient(ellipse at 70% 30%, rgba(99,102,241,0.15) 0%, transparent 60%), ' +
          'radial-gradient(ellipse at 30% 70%, rgba(139,92,246,0.10) 0%, transparent 60%)',
      },
    },
  },
  plugins: [],
}
