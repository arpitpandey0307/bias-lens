/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Clinical Lens Design System
        primary: '#003d9b',
        'primary-container': '#0052cc',
        surface: '#f8f9ff',
        'surface-container-low': '#eff4ff',
        'surface-container-lowest': '#ffffff',
        'surface-container-high': '#e3e8f5',
        'surface-container-highest': '#d7dce9',
        'surface-variant': '#e1e6f0',
        'on-surface': '#0b1c30',
        'on-surface-variant': '#44474f',
        'on-primary': '#ffffff',
        'on-primary-container': '#001a41',
        'error': '#ba1a1a',
        'error-container': '#ffdad6',
        'on-error-container': '#410002',
        'tertiary': '#7b2600',
        'tertiary-container': '#ffdbd0',
        'on-tertiary-fixed-variant': '#5f1900',
        'outline-variant': '#c3c6d6',
        'border-tertiary': '#e5e7eb',
        'border-secondary': '#d1d5db',
        'border-info': '#93c5fd',
        'text-primary': '#0b1c30',
        'text-secondary': '#6b7280',
        'text-success': '#065f46',
        'text-info': '#1e40af',
        'text-danger': '#ba1a1a',
        'background-primary': '#ffffff',
        'background-secondary': '#f3f4f6',
        'background-success': '#d1fae5',
        'background-info': '#dbeafe',
        'background-danger': '#fef2f2',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'display-lg': '3.5rem',
        'display-md': '2.75rem',
        'headline-sm': '1.5rem',
        'body-md': '0.875rem',
        'label-sm': '0.6875rem',
      },
      borderRadius: {
        'md': '0.375rem',
        'lg': '0.5rem',
      },
      boxShadow: {
        'ambient': '0 12px 40px rgba(11, 28, 48, 0.06)',
      },
    },
  },
  plugins: [],
}
