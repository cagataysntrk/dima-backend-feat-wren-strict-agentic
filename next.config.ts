import type { NextConfig } from "next";

// Backend origin SERVER-SIDE'da tutulur (browser'a sızmaz). Browser same-origin `/api/*`'e
// konuşur; Next bunu backend'e proxy'ler. Böylece: refresh cookie same-origin (middleware
// okuyabilir), CORS gerekmez, backend URL gizli (ADR-0012 rewrite-proxy alternatifi).
const backend = process.env.BACKEND_ORIGIN ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  // localtld ile dev server'a proxy'lenmiş bir origin'den (ör. frontend.dima.localtld
  // veya frontend.dima.localtld.sh) erişildiğinde Next dev runtime'ının/HMR'ın bu origin'i
  // kabul etmesi için gerekli. Aksi halde client hydrate olmaz (istekler bloklanır).
  // Kanonik domain `.localtld`; bazı kurulumlar `.localtld.sh` sunar — ikisi de eklidir.
  allowedDevOrigins: [
    "frontend.dima.localtld",
    "*.localtld",
    "frontend.dima.localtld.sh",
    "*.localtld.sh",
  ],
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/:path*` }];
  },
};

export default nextConfig;
