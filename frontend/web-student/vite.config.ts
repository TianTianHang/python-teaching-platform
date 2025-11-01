import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import Inspect from 'vite-plugin-inspect'
export default defineConfig({
  plugins: [tailwindcss(), reactRouter(), tsconfigPaths(),Inspect()],
   ssr: {
    noExternal: [
      "@emotion/react",
      "@emotion/styled",
      "@mui/material",
      "@mui/icons-material",
      "@mui/system",
      "@mui/styled-engine",
    ],
  },
});
