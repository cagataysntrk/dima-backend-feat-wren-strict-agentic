"use client";

import { useEffect, useRef, useState } from "react";
import { getNotifications, type Notification } from "@/lib/api-client";

// Bildirim zili (ADR-0011): zamanlanmış rapor/alarm bildirimleri — 60sn'de bir yoklanır.
// Okunmamış sayacı localStorage'daki son-görülme zamanına göre hesaplanır.
// Buton yalnız rozet taşır; liste, ayarlar/yardım gibi sağ SHEET'te açılır
// (NotificationsPanel, SettingsDrawer içinde render edilir).
const SEEN_KEY = "dima.notifications.seen";

export function NotificationsBell({ onOpen }: { onOpen: () => void }) {
  const [items, setItems] = useState<Notification[]>([]);
  const [seenTs, setSeenTs] = useState<string>("");
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    setSeenTs(localStorage.getItem(SEEN_KEY) ?? "");
    const poll = () => getNotifications(20).then(setItems).catch(() => {});
    poll();
    timer.current = setInterval(poll, 60_000);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, []);

  const unread = items.filter((n) => !seenTs || n.ts > seenTs).length;
  const markSeen = () => {
    const latest = items[0]?.ts ?? new Date().toISOString();
    localStorage.setItem(SEEN_KEY, latest);
    setSeenTs(latest);
  };

  const btn =
    "relative flex h-8 w-8 items-center justify-center border border-hairline bg-background/70 text-muted backdrop-blur-sm transition-colors hover:text-foreground hover:border-neutral-400 dark:hover:border-neutral-600";

  return (
    <button
      onClick={() => {
        markSeen();
        onOpen();
      }}
      aria-label="Bildirimler"
      className={btn}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
      {unread > 0 && (
        <span className="absolute -right-1 -top-1 flex h-3.5 min-w-3.5 items-center justify-center bg-accent px-0.5 font-mono text-[9px] leading-none text-white">
          {unread > 9 ? "9+" : unread}
        </span>
      )}
    </button>
  );
}

// Sheet içeriği: açılışta taze liste çeker (rozet yoklaması butonda kalır).
export function NotificationsPanel() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    getNotifications(50)
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  if (loaded && items.length === 0) {
    return (
      <div className="px-1 py-4 font-mono text-[11px] text-neutral-400">
        bildirim yok — bir rapora 🔔 zamanla ekleyebilirsin
      </div>
    );
  }
  return (
    <ul>
      {items.map((n) => (
        <li key={n.id} className="border-b border-hairline px-1 py-2 last:border-b-0">
          <div
            className={`font-mono text-[11px] leading-snug ${
              n.kind === "alert" ? "text-red-500" : "text-neutral-600 dark:text-neutral-300"
            }`}
          >
            {n.message}
          </div>
          <div className="mt-0.5 flex items-center justify-between font-mono text-[9px] text-neutral-400">
            <span>{n.ts.replace("T", " ").slice(0, 16)}</span>
            {n.contract_id && <span title="Kanıt kaydı (Query Contract)">{n.contract_id}</span>}
          </div>
        </li>
      ))}
    </ul>
  );
}
