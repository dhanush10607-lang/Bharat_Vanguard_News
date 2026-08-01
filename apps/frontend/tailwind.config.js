/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        /* ── Core Brand Palette ── */
        background:  '#080D1A',        /* deep navy black  */
        surface:     '#0F1629',        /* card background  */
        'surface-2': '#161E36',        /* elevated surface */
        border:      '#1E2A45',        /* subtle borders   */
        'border-2':  '#2A3A5C',        /* hover borders    */

        /* ── Accent ── */
        primary: {
          DEFAULT: '#3B82F6',          /* electric blue    */
          light:   '#60A5FA',
          dark:    '#1D4ED8',
          glow:    'rgba(59,130,246,0.15)',
        },
        emerald: {
          DEFAULT: '#10B981',          /* verified green   */
          light:   '#34D399',
          glow:    'rgba(16,185,129,0.15)',
        },
        amber: {
          DEFAULT: '#F59E0B',          /* warning / trust  */
          light:   '#FCD34D',
          glow:    'rgba(245,158,11,0.15)',
        },
        rose: {
          DEFAULT: '#F43F5E',          /* negative / alert */
          glow:    'rgba(244,63,94,0.15)',
        },

        /* ── Text ── */
        text: {
          primary:   '#F0F4FF',
          secondary: '#8B9DC3',
          muted:     '#4A5C80',
        },
      },

      fontFamily: {
        sans:   ['Inter', 'system-ui', 'sans-serif'],
        serif:  ['Newsreader', 'Georgia', 'serif'],
        mono:   ['JetBrains Mono', 'monospace'],
      },

      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },

      backgroundImage: {
        'gradient-radial':  'radial-gradient(var(--tw-gradient-stops))',
        'hero-glow':        'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59,130,246,0.15), transparent)',
        'card-shine':       'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 50%)',
        'blue-glow':        'radial-gradient(circle at center, rgba(59,130,246,0.2), transparent 70%)',
      },

      boxShadow: {
        'card':      '0 1px 3px rgba(0,0,0,0.4), 0 0 0 1px rgba(30,42,69,0.8)',
        'card-hover':'0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(59,130,246,0.3)',
        'glow-blue': '0 0 20px rgba(59,130,246,0.3)',
        'glow-green':'0 0 20px rgba(16,185,129,0.3)',
        'inner':     'inset 0 1px 0 rgba(255,255,255,0.05)',
      },

      animation: {
        'fade-in':       'fadeIn 0.4s ease-out',
        'fade-up':       'fadeUp 0.5s ease-out',
        'slide-in-right':'slideInRight 0.3s ease-out',
        'pulse-slow':    'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer':       'shimmer 2s infinite linear',
        'spin-slow':     'spin 3s linear infinite',
      },

      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%':   { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },

      borderRadius: {
        'xl':  '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },

      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
