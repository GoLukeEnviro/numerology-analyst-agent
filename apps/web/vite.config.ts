import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import { defineConfig } from "vitest/config";

export default defineConfig({
    build: {
        chunkSizeWarningLimit: 2_000,
    },
    server: {
        proxy: {
            "/api": "http://127.0.0.1:8000",
        },
    },
    preview: {
        proxy: {
            "/api": "http://127.0.0.1:8000",
        },
    },
    plugins: [
        react(),
        VitePWA({
            registerType: "prompt",
            manifest: {
                id: "/",
                name: "Numra – Numerologie nachvollziehbar",
                short_name: "Numra",
                description:
                    "Deterministische numerologische Berechnungen mit transparentem Rechenweg.",
                theme_color: "#0c1824",
                background_color: "#0c1824",
                display: "standalone",
                display_override: ["window-controls-overlay", "standalone"],
                lang: "de",
                start_url: "/",
                scope: "/",
                orientation: "any",
                categories: ["lifestyle", "education"],
                icons: [
                    {
                        src: "/icons/icon-192.png",
                        sizes: "192x192",
                        type: "image/png",
                        purpose: "any",
                    },
                    {
                        src: "/icons/icon-512.png",
                        sizes: "512x512",
                        type: "image/png",
                        purpose: "any",
                    },
                    {
                        src: "/icons/icon-maskable-512.png",
                        sizes: "512x512",
                        type: "image/png",
                        purpose: "maskable",
                    },
                ],
                shortcuts: [
                    {
                        name: "Neue Analyse",
                        short_name: "Analyse",
                        url: "/analyse/neu",
                        icons: [
                            { src: "/icons/icon-192.png", sizes: "192x192" },
                        ],
                    },
                    {
                        name: "Lokale Bibliothek",
                        short_name: "Bibliothek",
                        url: "/bibliothek",
                        icons: [
                            { src: "/icons/icon-192.png", sizes: "192x192" },
                        ],
                    },
                ],
            },
            workbox: {
                navigateFallback: "/index.html",
                runtimeCaching: [],
                cleanupOutdatedCaches: true,
                navigateFallbackDenylist: [/^\/api\//],
                globIgnores: ["**/profilePdf-*.js"],
            },
        }),
    ],
    test: {
        environment: "jsdom",
        exclude: ["e2e/**", "node_modules/**"],
        globals: true,
        setupFiles: "./src/test/setup.ts",
        coverage: {
            provider: "v8",
            reporter: ["text", "text-summary", "lcov", "json-summary"],
            reportsDirectory: "./coverage",
            include: ["src/**/*.{ts,tsx}"],
            exclude: [
                "src/api/schema.d.ts",
                "src/vite-env.d.ts",
                "src/test/**",
                "src/**/*.test.{ts,tsx}",
            ],
            // Thresholds: gemessene Baseline vom 2026-08-02
            // (docs/audit/web-coverage-baseline-2026-08-02.md)
            thresholds: {
                statements: 69.48,
                branches: 59.39,
                functions: 62,
                lines: 73.95,
            },
        },
    },
});
