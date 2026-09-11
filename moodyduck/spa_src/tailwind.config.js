/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        clay: {
          50:  '#fdf6f0',
          100: '#faeade',
          200: '#f4d2ba',
          300: '#ebb48f',
          400: '#e08f62',
          500: '#d4703f',
          600: '#c05530',
          700: '#9e4226',
          800: '#803623',
          900: '#692e21',
        },
        sage: {
          50:  '#f3f8f4',
          100: '#e2ede5',
          200: '#c5dbcc',
          300: '#9bc1a7',
          400: '#6aa27f',
          500: '#488460',
          600: '#36694c',
          700: '#2b543d',
          800: '#244432',
          900: '#1e3829',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
    },
  },
}
