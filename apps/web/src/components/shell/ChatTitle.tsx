"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, Pencil, Trash2 } from "lucide-react";
import { selectActive, useConversations } from "@/stores/conversations";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

/**
 * Üst bardaki sohbet adı — kenar çubuğu düğmesinin yanında (Claude deseni).
 * Üstüne gelince chevron belirir; menüden yeniden adlandırma ve silme.
 * Ada çift tıklamak da doğrudan düzenlemeye açar.
 */
export function ChatTitle({ className }: { className?: string }) {
  const conv = useConversations(selectActive);
  const incognito = useConversations((s) => s.incognito);
  const rename = useConversations((s) => s.rename);
  const remove = useConversations((s) => s.remove);

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  // Gizli sohbetin adı yok (geçmişe yazılmıyor) — başlık göstermenin anlamı yok.
  if (incognito || !conv) return null;

  const title = conv.title || "Yeni sohbet";

  const startEdit = () => {
    setDraft(conv.title || "");
    setEditing(true);
  };

  const commit = () => {
    const next = draft.trim();
    if (next && next !== conv.title) rename(conv.id, next.slice(0, 80));
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
        className={cn(
          "min-w-0 max-w-64 rounded-md border border-input bg-card px-2 py-1 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring/40",
          className,
        )}
      />
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        onDoubleClick={startEdit}
        className={cn(
          "group/title flex min-w-0 items-center gap-1 rounded-md px-2 py-1 text-sm text-foreground transition-colors hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none",
          className,
        )}
      >
        <span className="min-w-0 truncate">{title}</span>
        {/* chevron normalde soluk; satıra gelince ya da menü açıkken belirir */}
        <ChevronDown className="size-3.5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover/title:opacity-100 group-data-[state=open]/title:opacity-100" />
      </DropdownMenuTrigger>

      <DropdownMenuContent align="start" className="w-48">
        <DropdownMenuItem onSelect={startEdit}>
          <Pencil className="size-4" />
          Yeniden adlandır
          <DropdownMenuShortcut>R</DropdownMenuShortcut>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onSelect={() => remove(conv.id)}>
          <Trash2 className="size-4" />
          Sil
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
