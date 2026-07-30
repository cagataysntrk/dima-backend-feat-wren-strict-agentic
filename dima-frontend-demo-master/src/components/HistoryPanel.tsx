"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteConversation, listConversations } from "@/lib/api-client";

// Sohbet geçmişi (per-user, backend kalıcı). Liste → tıkla=resume, × = soft-delete.
// Minimal: demo sağ sheet içinde render edilir (SettingsDrawer). dima-frontend'in
// elaborate AppSidebar'ı KOPYALANMADI — demo sade tutulur.
function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("tr-TR", {
      day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return "";
  }
}

export function HistoryPanel({
  onResume,
  onNewChat,
  activeSessionId,
}: {
  onResume: (id: string) => void;
  onNewChat: () => void;
  activeSessionId?: string | null;
}) {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["conversations"],
    queryFn: listConversations,
  });
  const del = useMutation({
    mutationFn: (id: string) => deleteConversation(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversations"] }),
  });

  return (
    <div className="space-y-3">
      <button
        onClick={onNewChat}
        className="w-full border border-hairline px-3 py-1.5 text-left font-mono text-[12px] text-neutral-600 transition-colors hover:border-accent/50 hover:text-foreground dark:text-neutral-300"
      >
        + yeni sohbet
      </button>

      {isLoading ? (
        <p className="font-mono text-[11px] text-neutral-400">yükleniyor…</p>
      ) : !data || data.length === 0 ? (
        <p className="font-mono text-[11px] text-neutral-400">henüz kayıtlı sohbet yok</p>
      ) : (
        <ul className="space-y-0.5">
          {data.map((c) => {
            const isActive = c.session_id === activeSessionId;
            return (
              <li
                key={c.id}
                className={`group flex items-center gap-1 border-l-2 pl-2 transition-colors ${
                  isActive ? "border-accent bg-accent/[0.06]" : "border-transparent hover:bg-neutral-500/[0.04]"
                }`}
              >
                <button onClick={() => onResume(c.id)} className="min-w-0 flex-1 py-1.5 text-left">
                  <div className="truncate text-[13px] text-foreground">
                    {c.title || "(başlıksız)"}
                  </div>
                  <div className="font-mono text-[10px] text-neutral-400">
                    {c.message_count} mesaj · {fmtDate(c.updated_at)}
                  </div>
                </button>
                <button
                  onClick={() => del.mutate(c.id)}
                  disabled={del.isPending}
                  title="Sohbeti sil"
                  className="px-1.5 font-mono text-sm text-neutral-400 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100"
                >
                  ×
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
