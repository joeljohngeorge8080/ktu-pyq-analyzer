/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["'Syne'", "sans-serif"],
        body: ["'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      colors: {
        primary: {
          50: "#f0f4ff",
          100: "#dce6ff",
          400: "#6b8eff",
          500: "#4c6ef5",
          600: "#3a5bd9",
          700: "#2c46b0",
        },
        surface: {
          0: "#0a0c14",
          1: "#10131f",
          2: "#161a2c",
          3: "#1e2338",
          4: "#252b44",
        },
        accent: {
          gold: "#f5c542",
          teal: "#2dd4bf",
          rose: "#fb7185",
        },
      },
      backgroundImage: {
        "grid-subtle": "radial-gradient(circle, #ffffff08 1px, transparent 1px)",
      },
      backgroundSize: {
        "grid-size": "32px 32px",
      },
    },
  },
  plugins: [],
}
