import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

// Backend origin SERVER-SIDE'da tutulur (browser'a sızmaz). Browser same-origin `/api/*`'e
// konuşur; proxy'yi artık bir Route Handler yapar (src/app/api/[...path]/route.ts) —
// böylece Set-Cookie normalize edilebilir (dev'de http üzerinde Secure/Domain düşer,
// oturum cookie'si düşmez). Backend URL gizli kalır, CORS gerekmez (ADR-0012).

const nextConfig: NextConfig = {
  // Workspace paketleri ham TypeScript dışa aktarır (build adımı yok — "JIT
  // paket"). Derlemesini tüketen uygulama yapar; böylece paketleri sıraya
  // dizen ayrı bir build orkestrasyonu gerekmiyor ve pakete yapılan düzenleme
  // dev'de anında yansıyor.
  transpilePackages: ["@dima/contracts", "@dima/domain", "@dima/api-client"],
  // localtld ile dev server'a proxy'lenmiş bir origin'den (ör. frontend.dima.localtld)
  // erişildiğinde Next dev runtime'ının/HMR'ın bu origin'i kabul etmesi için gerekli.
  // Aksi halde client hydrate olmaz (istekler bloklanır). Domain `.localtld`.
  allowedDevOrigins: [
    "frontend.dima.localtld",
    "*.localtld",
  ],
  // Temel güvenlik başlıkları. Tam CSP bilinçli eklenmedi: Next dev runtime'ı ve
  // Recharts/Framer Motion/Radix inline `style` attribute'ları kullanır; nonce'suz
  // sıkı `style-src` uygulamayı kırar. CSP istenirse önce Report-Only ile ölçülmeli.
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
