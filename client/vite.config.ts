import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  plugins: [tailwindcss()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000", // Use 127.0.0.1 instead of localhost
        changeOrigin: true,
        secure: false,
      },
      "/socket.io": {
        target: "http://127.0.0.1:5000", // Use 127.0.0.1 instead of localhost
        ws: true,
        changeOrigin: true,
      },
    },
  },
});

