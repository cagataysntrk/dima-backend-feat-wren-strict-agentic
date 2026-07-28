"use client";

import { useEffect, useRef, useState } from "react";
import { Bell } from "lucide-react";
import { useTranslations } from "next-intl";
import { getNotifications, type Notification } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { NotificationsPanel } from "@/components/NotificationsBell";

const SEEN_KEY = "dima.notifications.seen";

/** Sidebar-footer bell → Popover with the notifications feed; polled unread badge. */
export function NotificationsPopover() {
  const t = useTranslations("notifications");
  const [items, setItems] = useState<Notification[]>([]);
  const [seenTs, setSeenTs] = useState(() =>
    typeof window !== "undefined" ? (localStorage.getItem(SEEN_KEY) ?? "") : "",
  );
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const poll = () => getNotifications(20).then(setItems).catch(() => {});
    poll();
    timer.current = setInterval(poll, 60_000);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, []);

  const unread = items.filter((n) => n.ts > seenTs).length;

  function onOpenChange(open: boolean) {
    if (open && items.length) {
      const latest = items[0].ts;
      localStorage.setItem(SEEN_KEY, latest);
      setSeenTs(latest);
    }
  }

  return (
    <Popover onOpenChange={onOpenChange}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={t("title")}
          className="relative text-muted-foreground hover:text-foreground"
        >
          <Bell className="size-4" />
          {unread > 0 && (
            <span className="absolute top-1 right-1 flex size-4 items-center justify-center rounded-full bg-brand text-[10px] font-medium text-brand-foreground tabular-nums">
              {unread > 9 ? "9+" : unread}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" side="top" className="w-80 p-0">
        <div className="border-b border-border px-3 py-2 text-sm">
          {t("title")}
        </div>
        <div className="max-h-96 overflow-auto p-1">
          <NotificationsPanel />
        </div>
      </PopoverContent>
    </Popover>
  );
}
