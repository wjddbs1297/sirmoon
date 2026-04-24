/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#F0F4FF",
          100: "#DDE8FF",
          500: "#3A86FF",
          700: "#1A3A8F",
          900: "#0D1F5C",
        },
      },
    },
  },
  plugins: [],
};
