import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import Inspect from 'vite-plugin-inspect';
import vitePluginImp from 'vite-plugin-imp';

export default defineConfig({
  plugins: [
    tailwindcss(),
    reactRouter(),
    tsconfigPaths(),
    Inspect(),
    vitePluginImp({
      libList: [
        {
          libName: '@mui/icons-material',
          libDirectory: '',
          camel2DashComponentName: false,
        },
      ],
    }),
  ],
});
