import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "abs-blue-dark":   "#0051A1",
        "abs-blue-dark2":  "#00529F",
        "abs-blue-light":  "#009FE3",
        "abs-blue-light2": "#009FE0",
        "abs-red":         "#E41720",
      },
      gridTemplateColumns: {
        "12": "repeat(12, minmax(0, 1fr))",
      },
    },
  },
  plugins: [],
};

export default config;
