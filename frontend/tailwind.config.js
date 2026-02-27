/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class", // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        "risk-low": "#10B981",
        "risk-medium": "#F59E0B",
        "risk-high": "#EF4444",
        "risk-critical": "#7C2D12",
        primary: "#1E40AF",
        secondary: "#64748B",
      },
    },
  },
  plugins: [],
};
