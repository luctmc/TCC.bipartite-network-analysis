import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * O build vai para `src/edugraph/api/static/`, de onde o FastAPI o serve
 * em `/` (ver `edugraph.api.app._mount_frontend`). A pasta fica fora do
 * git: quem clona roda `npm run build`.
 *
 * `base: "./"` deixa os caminhos relativos, para que a página funcione
 * tanto servida pela API quanto aberta de um diretório qualquer — útil
 * para levar as capturas do capítulo 3 num pen drive na apresentação.
 */
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "../src/edugraph/api/static",
    emptyOutDir: true,
    sourcemap: true,
  },
  server: {
    port: 5173,
    proxy: {
      // Em desenvolvimento, o Vite encaminha as chamadas para o FastAPI,
      // então o front usa caminhos relativos nos dois modos.
      "/health": "http://127.0.0.1:8000",
      "/datasets": "http://127.0.0.1:8000",
      "/openapi.json": "http://127.0.0.1:8000",
    },
  },
});
