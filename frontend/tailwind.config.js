// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        vibe: {
          bg: "#0f0f0f",
          card: "#1a1a1a",
          accent: "#e879f9",
        },
      },
    },
  },
  plugins: [],
};
