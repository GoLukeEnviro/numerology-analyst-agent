import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import { defineConfig } from "vitest/config";

export default defineConfig({
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
  plugins: [
    react(),
    VitePWA({
      registerType: "prompt",
      manifest: {
        name: "Numra – Numerologie nachvollziehbar",
        short_name: "Numra",
        description:
          "Deterministische numerologische Berechnungen mit transparentem Rechenweg.",
        theme_color: "#0c1824",
        background_color: "#0c1824",
        display: "standalone",
        lang: "de",
        start_url: "/",
      },
      workbox: {
        navigateFallback: "/index.html",
        runtimeCaching: [],
      },
    }),
  ],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
  },
});
