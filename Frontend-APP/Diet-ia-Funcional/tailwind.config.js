// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,jsx,ts,tsx}',   // <-- carpeta de páginas
    './components/**/*.{js,jsx,ts,tsx}',
  ],
  presets: [require('nativewind/preset')],
  darkMode: 'class',
  
  theme: {
    extend: {},
  },
  plugins: [],
};
console.log('Tailwind config cargado');