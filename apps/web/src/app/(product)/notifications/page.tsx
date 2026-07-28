"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Bell, BellRing, FileBarChart, Search } from "lucide-react";
import { useNotifications } from "@/lib/notifications";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

/** Bildirimler — sidebar rozetinin tam sayfa, aranabilir hâli (/chats gibi). */
export default function NotificationsPage() {
  const { items, loaded, markSeen } = useNotifications();
  const [q, setQ] = useState("");

  // Sayfayı açmak "okundu" demektir — rozet burada sıfırlanır.
  useEffect(() => {
    if (loaded && items.length) markSeen();
  }, [loaded, items.length, markSeen]);

  const shown = useMemo(() => {
    const needle = q.trim().toLocaleLowerCase("tr-TR");
    if (!needle) return items;
    return items.filter((n) =>
      `${n.message} ${n.label ?? ""}`.toLocaleLowerCase("tr-TR").includes(needle),
    );
  }, [items, q]);

  const fmt = (ts: string) => {
    const d = new Date(ts);
    return Number.isNaN(d.getTime())
      ? ts
      : new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeStyle: "short" }).format(d);
  };

  return (
    <main className="dima-page-in mx-auto max-w-3xl space-y-6 px-6 py-10">
      <header className="space-y-3">
        <Button variant="ghost" size="sm" asChild className="-ml-2 gap-1.5">
          <Link href="/app">
            <ArrowLeft className="size-4" />
            Sohbete dön
          </Link>
        </Button>
        <h1 className="text-2xl font-semibold tracking-tight">Bildirimler</h1>
      </header>

      <div className="relative">
        <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Bildirimlerde ara…"
          aria-label="Bildirimlerde ara"
          className="pl-9"
        />
      </div>

      {!loaded ? (
        <div className="space-y-2">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      ) : shown.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border py-14 text-center">
          <Bell className="size-5 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {items.length === 0 ? "Bildirim yok." : "Eşleşen bildirim yok."}
          </p>
          {items.length === 0 && (
            <p className="max-w-xs text-xs text-muted-foreground/80">
              Bir rapora <strong className="font-medium">zamanla</strong> ekle — koşumlar
              buraya düşer.
            </p>
          )}
        </div>
      ) : (
        <ul className="space-y-2">
          {shown.map((n) => {
            const alert = n.kind === "alert";
            const Icon = alert ? BellRing : FileBarChart;
            return (
              <li key={n.id}>
                <Card className="gap-1.5 p-3">
                  <div className="flex items-center gap-2">
                    <Icon
                      className={
                        alert ? "size-3.5 shrink-0 text-brand" : "size-3.5 shrink-0 text-muted-foreground"
                      }
                    />
                    <Badge variant={alert ? "brand-subtle" : "outline"} className="text-[10px]">
                      {alert ? "uyarı" : "rapor"}
                    </Badge>
                    {n.label && (
                      <span className="min-w-0 truncate text-xs text-muted-foreground">
                        {n.label}
                      </span>
                    )}
                    <time
                      dateTime={n.ts}
                      className="ml-auto shrink-0 text-xs text-muted-foreground tabular-nums"
                    >
                      {fmt(n.ts)}
                    </time>
                  </div>
                  <p className="text-sm text-foreground">{n.message}</p>
                  {n.contract_id && (
                    <span className="font-mono text-[10px] text-muted-foreground">
                      {n.contract_id}
                    </span>
                  )}
                </Card>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
