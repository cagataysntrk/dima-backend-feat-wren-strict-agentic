"use client";

import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getSchema } from "@/lib/api-client";

// Veri kaynağı (tenant DB) çevrimiçi/çevrimdışı durum noktası — ikon rail'in EN ALTINDA,
// çıkış butonunun HEMEN ÜSTÜNDE (bottom-14, logout bottom-4 ile hizalı kolon).
// SchemaPanel ile AYNI ["schema"] query'sini paylaşır (çift-fetch yok); 30sn'de bir
// tazelenir → DB tekrar açıldığında rozet kendiliğinden yeşile döner. db_online backend'in
// TCP erişilebilirlik kontrolünden gelir (ulaşılamaz DB → /schema asılmaz).
export function ConnectionBadge() {
  const pathname = usePathname();
  const { data, isError, isLoading } = useQuery({
    queryKey: ["schema"],
    queryFn: getSchema,
    refetchInterval: 30_000,
    retry: false,
    enabled: pathname !== "/login",
  });
  if (pathname === "/login") return null;

  const online = !isError && data?.db_online !== false;
  const label = isLoading
    ? "Veri kaynağı denetleniyor…"
    : online
      ? "Veri kaynağı çevrimiçi"
      : "Veri kaynağına ulaşılamıyor — çevrimdışı";
  return (
    <div
      title={label}
      aria-label={label}
      role="status"
      className="fixed bottom-14 right-2 z-50 flex h-8 w-8 items-center justify-center"
    >
      <span
        className={`inline-block h-2.5 w-2.5 rounded-full ${
          isLoading
            ? "bg-neutral-400"
            : online
              ? "bg-emerald-500"
              : "animate-pulse bg-red-500"
        }`}
      />
    </div>
  );
}
