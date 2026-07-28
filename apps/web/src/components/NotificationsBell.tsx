"use client";

import { useEffect, useState } from "react";
import { getNotifications, type Notification } from "@dima/api-client";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

// Bildirim listesi (ADR-0011): zamanlanmış rapor/alarm bildirimleri. Açılışta taze
// liste çeker; okunmamış rozeti çağıran (NotificationsPopover) tarafında yoklanır.
export function NotificationsPanel() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    getNotifications(50)
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  if (!loaded) {
    return (
      <div className="space-y-2 p-2">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="px-3 py-6 text-center text-xs text-muted-foreground">
        Bildirim yok — bir rapora 🔔 zamanla ekleyebilirsin.
      </div>
    );
  }

  return (
    <ul className="divide-y divide-border">
      {items.map((n) => (
        <li key={n.id} className="px-3 py-2">
          <div
            className={cn(
              "text-xs leading-snug",
              n.kind === "alert" ? "text-destructive" : "text-foreground",
            )}
          >
            {n.message}
          </div>
          <div className="mt-0.5 flex items-center justify-between font-mono text-[10px] text-muted-foreground">
            <span>{n.ts.replace("T", " ").slice(0, 16)}</span>
            {n.contract_id && (
              <span className="truncate" title="Kanıt kaydı (Query Contract)">
                {n.contract_id}
              </span>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
