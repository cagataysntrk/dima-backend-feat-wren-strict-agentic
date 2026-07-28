import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Workspace paketleri ham TypeScript dışa aktarır (build adımsız "JIT paket");
  // derlemesini tüketen uygulama yapar.
  transpilePackages: ["@dima/contracts", "@dima/domain"],
  // localtld dev sunucusunu bir alan adının arkasına proxy'ler
  // (genui.dima.localtld). Next'in bu origin'i kabul etmesi gerekiyor; aksi
  // halde HMR istekleri bloklanır ve istemci hydrate olmaz.
  allowedDevOrigins: ["genui.dima.localtld", "*.localtld"],
};

export default nextConfig;
