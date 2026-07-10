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

        brand: {
          primary: "var(--color-primary)",
          blush: "var(--color-blush)",
          deep: "var(--color-deep)",
        },

        "on-accent": "var(--on-accent)",
        "on-deep": "var(--on-deep)",

        // Current active phase theme (set by PhaseThemeProvider). Use these
        // for anything that should follow whatever phase is active right
        // now; use `phase.*` below to reference a specific phase regardless
        // of which one is active (e.g. the insights chart legend).
        accent: "var(--accent)",
        "accent-2": "var(--accent-2)",

        phase: {
          menstrual: {
            DEFAULT: "var(--phase-menstrual)",
            soft: "var(--phase-menstrual-soft)",
            text: "var(--phase-menstrual-text)",
          },
          follicular: {
            DEFAULT: "var(--phase-follicular)",
            soft: "var(--phase-follicular-soft)",
            text: "var(--phase-follicular-text)",
          },
          ovulatory: {
            DEFAULT: "var(--phase-ovulatory)",
            accent: "var(--phase-ovulatory-accent)",
            soft: "var(--phase-ovulatory-soft)",
            text: "var(--phase-ovulatory-text)",
            "accent-text": "var(--phase-ovulatory-accent-text)",
          },
          luteal: {
            DEFAULT: "var(--phase-luteal)",
            "accent-2": "var(--phase-luteal-accent-2)",
            soft: "var(--phase-luteal-soft)",
            text: "var(--phase-luteal-text)",
          },
        },

        // Placeholder scale from the initial scaffold. login/signup already
        // reference these classes; left untouched so those pages don't
        // shift underneath them. New work should use brand.*/phase.* above.
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
      },
      backgroundImage: {
        "phase-gradient": "var(--gradient)",
      },
      fontFamily: {
        sans: ["var(--font-nunito-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
