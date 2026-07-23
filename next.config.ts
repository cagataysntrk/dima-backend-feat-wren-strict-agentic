import type { NextConfig } from "next";

// Backend origin SERVER-SIDE'da tutulur (browser'a sızmaz). Browser same-origin `/api/*`'e
// konuşur; Next bunu backend'e proxy'ler. Böylece: refresh cookie same-origin (middleware
// okuyabilir), CORS gerekmez, backend URL gizli (ADR-0012 rewrite-proxy alternatifi).
const backend = process.env.BACKEND_ORIGIN ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  // localtld ile dev server'a proxy'lenmiş bir origin'den (ör. frontend.dima.localtld)
  // erişildiğinde Next dev runtime'ının/HMR'ın bu origin'i kabul etmesi için gerekli.
  // Aksi halde client hydrate olmaz (istekler bloklanır). Domain `.localtld`.
  allowedDevOrigins: [
    "frontend.dima.localtld",
    "*.localtld",
  ],
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/:path*` }];
  },
};

export default nextConfig;
