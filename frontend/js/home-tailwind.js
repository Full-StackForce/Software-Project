tailwind.config = {
    theme: {
        extend: {
            colors: {
                darkBg: '#090A10',
                panelBg: '#131520',
                panelBorder: '#202434',
                pulseGreen: '#10B981',
                brandPurple: '#6366F1',
                neonBlue: '#3B82F6',
                goldAccent: '#F59E0B'
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'bounce-slow': 'bounce 2s infinite',
                'shimmer': 'shimmer 2.5s infinite linear',
            },
            keyframes: {
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' }
                }
            }
        }
    }
};