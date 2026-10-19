/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#070b14",
          panel: "#0e1626",
          line: "#1c2a44",
          accent: "#3ee0b0",
          warn: "#f5c542",
          high: "#ff5d73",
        },
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "Segoe UI", "sans-serif"],
        mono: ["IBM Plex Mono", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};
