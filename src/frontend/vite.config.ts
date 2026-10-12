import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Servidor local fixo em 127.0.0.1:5173 e proxy de /api para o backend FastAPI.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: false,
      },
    },
  },
});
