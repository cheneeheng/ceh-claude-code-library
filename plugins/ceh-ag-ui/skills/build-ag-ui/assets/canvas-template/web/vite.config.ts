import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The browser calls /agent on the dev server; Vite forwards it to the agent, so no CORS setup.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/agent": process.env.AGENT_ORIGIN ?? "http://localhost:8000" },
  },
});
