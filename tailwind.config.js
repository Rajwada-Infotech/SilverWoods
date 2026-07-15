/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        cream: { 50:'#faf7f2', 100:'#f5f0e8', 200:'#ece5d9', 300:'#e0d5c5', 400:'#c9b99e' },
        brown: { 50:'#f9f5f0', 100:'#f0e8dc', 200:'#d4c4ac', 300:'#b09a7c', 400:'#8b6b4a', 500:'#6d4f32', 600:'#5c4a3a', 700:'#3d2b1f', 800:'#2a1f14', 900:'#1a130c' },
        gold:  { 400:'#e8d48b', 500:'#c9a84c', 600:'#a08338', 700:'#8b6b4a' },
        dark:  { 800:'#161616', 900:'#0d0d0d', 950:'#080808' },
      },
      fontFamily: {
        display: ['Playfair Display', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    }
  },
  plugins: [],
}
