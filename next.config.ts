import type { NextConfig } from "next";

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
};

export default nextConfig;
