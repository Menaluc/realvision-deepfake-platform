/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react()],
    server: {
        // Forward API calls to the backend during development
        // (the target moves to the FastAPI server on :8000 in Stage 9)
        proxy: {
            "/api": "http://localhost:3000"
        }
    },
    test: {
        environment: "jsdom",
        setupFiles: ["./src/test/setup.ts"]
    }
});
