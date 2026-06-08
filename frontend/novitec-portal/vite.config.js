import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Configura Vite para resolver aliases y servir el portal ejecutivo.
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        host: "127.0.0.1",
        port: 5173,
    },
});
