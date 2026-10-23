// Le navigateur n'appelle que Next : /api/* est relayé à FastAPI, donc pas de CORS à régler.
const API = process.env.PULS_API ?? "http://127.0.0.1:8000";

/** @type {import('next').NextConfig} */
export default {
  devIndicators: false,
  poweredByHeader: false,
  // la compression retient le flux SSE jusqu'à la fin : la réponse ne s'écrirait plus au fil de l'eau
  compress: false,
  async rewrites() {
    return [{ source: "/api/:chemin*", destination: `${API}/api/:chemin*` }];
  },
};
