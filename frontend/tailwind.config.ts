import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        accent: {
          DEFAULT: "var(--accent)",
          hover: "var(--accent-hover)",
          muted: "var(--accent-muted)",
        },
      },
      borderRadius: {
        pill: "9999px",
      },
      animation: {
        "egg-glow": "egg-glow 2.5s ease-in-out infinite",
      },
      keyframes: {
        "egg-glow": {
          "0%, 100%": { boxShadow: "0 0 8px var(--glow-egg)" },
          "50%": { boxShadow: "0 0 18px var(--glow-egg)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
