"use client";

import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getSchema } from "@/lib/api-client";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

// Veri kaynağı (tenant DB) çevrimiçi/çevrimdışı durum noktası.
// SchemaPanel ile AYNI ["schema"] query'sini paylaşır (çift-fetch yok); 30sn'de bir
// tazelenir → DB tekrar açıldığında rozet kendiliğinden yeşile döner. db_online backend'in
// TCP erişilebilirlik kontrolünden gelir (ulaşılamaz DB → /schema asılmaz).
//
// NOT: eskiden `fixed bottom-14 right-2` ile sağ ikon rail'ine yapışıktı; o rail
// kaldırıldığı için artık akış içinde duran bir nokta — sidebar altbilgisine gömülü.
export function ConnectionBadge({ className }: { className?: string }) {
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
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          aria-label={label}
          role="status"
          className={cn("flex size-7 items-center justify-center", className)}
        >
          <span
            className={cn(
              "inline-block size-2 rounded-full",
              isLoading
                ? "bg-muted-foreground"
                : online
                  ? "bg-emerald-500"
                  : "animate-pulse bg-destructive",
            )}
          />
        </span>
      </TooltipTrigger>
      <TooltipContent side="top">{label}</TooltipContent>
    </Tooltip>
  );
}
