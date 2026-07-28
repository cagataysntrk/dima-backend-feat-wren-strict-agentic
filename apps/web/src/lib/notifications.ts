"use client";

// Bildirim beslemesi + okunmamış sayacı, tek yerden.
// Sidebar rozeti ile /notifications sayfası AYNI veriyi paylaşsın diye burada:
// iki ayrı poll'la iki farklı sayı göstermek en kötü sonuç olurdu.

import { useCallback, useEffect, useState } from "react";
import { getNotifications, type Notification } from "@/lib/api-client";

const SEEN_KEY = "dima.notifications.seen";
const POLL_MS = 60_000;

export function useNotifications() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [seenTs, setSeenTs] = useState(() =>
    typeof window !== "undefined" ? (localStorage.getItem(SEEN_KEY) ?? "") : "",
  );

  useEffect(() => {
    let alive = true;
    const poll = () =>
      getNotifications(50)
        .then((n) => {
          if (alive) setItems(n);
        })
        .catch(() => {})
        .finally(() => {
          if (alive) setLoaded(true);
        });
    poll();
    const id = setInterval(poll, POLL_MS);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  /** En yeni bildirimi "görüldü" işaretle (rozet sıfırlanır). */
  const markSeen = useCallback(() => {
    setItems((cur) => {
      if (cur.length) {
        localStorage.setItem(SEEN_KEY, cur[0].ts);
        setSeenTs(cur[0].ts);
      }
      return cur;
    });
  }, []);

  return {
    items,
    loaded,
    unread: items.filter((n) => n.ts > seenTs).length,
    markSeen,
  };
}
