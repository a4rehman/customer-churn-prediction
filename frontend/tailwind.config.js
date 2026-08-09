/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#0f172a",
          card: "#1e293b",
          card2: "#273449",
          border: "#334155",
        },
        brand: {
          DEFAULT: "#6366f1",
          hover: "#818cf8",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
