"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@dima/ui/utils";
import { useConversations } from "@/stores/conversations";

/**
 * Chat title in the top bar. Double-click (or Enter on the button) turns it
 * into an input; Enter saves, Escape cancels — the same flow as apps/web.
 */
export function ChatTitle({ convId, className }: { convId: string | null; className?: string }) {
  const title = useConversations((s) => s.conversations.find((c) => c.id === convId)?.title ?? "");
  const rename = useConversations((s) => s.rename);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  if (!convId || !title) return null;

  const start = () => {
    setDraft(title);
    setEditing(true);
  };
  const commit = () => {
    const next = draft.trim();
    if (next && next !== title) rename(convId, next);
    setEditing(false);
  };

  if (editing) {
    return (
      <input
        ref={inputRef}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
          if (e.key === "Escape") setEditing(false);
        }}
        aria-label="Sohbet adı"
        maxLength={80}
        className={cn(
          "min-w-0 max-w-64 rounded-md border border-input bg-card px-2 py-1 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring/40",
          className,
        )}
      />
    );
  }

  return (
    <button
      type="button"
      onDoubleClick={start}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === "F2") start();
      }}
      title="Yeniden adlandırmak için çift tıklayın"
      className={cn(
        "truncate rounded-md px-2 py-1 text-sm text-muted-foreground transition-colors hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none",
        className,
      )}
    >
      {title}
    </button>
  );
}
