import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        surface: "var(--surface)",
        border: "var(--border)",
        pink: {
          50: "var(--pink-50)",
          100: "var(--pink-100)",
          200: "var(--pink-200)",
          300: "var(--pink-300)",
          400: "var(--pink-400)",
          500: "var(--pink-500)",
          600: "var(--pink-600)",
          700: "var(--pink-700)",
          800: "var(--pink-800)",
          900: "var(--pink-900)",
        },
        phase: {
          menstrual: {
            DEFAULT: "var(--phase-menstrual)",
            soft: "var(--phase-menstrual-soft)",
          },
          follicular: {
            DEFAULT: "var(--phase-follicular)",
            soft: "var(--phase-follicular-soft)",
          },
          ovulation: {
            DEFAULT: "var(--phase-ovulation)",
            soft: "var(--phase-ovulation-soft)",
          },
          luteal: {
            DEFAULT: "var(--phase-luteal)",
            soft: "var(--phase-luteal-soft)",
          },
        },
      },
    },
  },
  plugins: [],
};

export default config;
