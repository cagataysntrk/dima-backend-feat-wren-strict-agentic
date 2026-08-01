"use client";

// Zamanlanmış rapor YÖNETİMİ (doğrulama turu düzeltmesi, 1 Ağustos 2026 — dış yol
// haritası P1-8): `ReportPanel.tsx`'teki "🔔 zamanla" bir zamanlama OLUŞTURABİLİYORDU
// ama kullanıcı sonra onu GÖREMİYOR/SİLEMİYOR/elle ÇALIŞTIRAMIYORDU — backend uçları
// (GET/DELETE/POST-run /schedules) zaten HAZIRDI, yalnız bu panel eksikti.

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteSchedule, listSchedules, runScheduleNow } from "@/lib/api-client";
import { usePermission } from "@/lib/usePermission";

const _EVERY_TR: Record<string, string> = { hour: "her saat", day: "her gün", week: "her hafta" };

export function SchedulesPanel() {
  const qc = useQueryClient();
  const canRead = usePermission("schedule:read");
  const { data, isLoading, isError } = useQuery({
    queryKey: ["schedules"],
    queryFn: listSchedules,
    enabled: canRead,
  });
  const [error, setError] = useState<string | null>(null);
  const [runNote, setRunNote] = useState<Record<string, string>>({});

  const del = useMutation({
    mutationFn: (id: string) => deleteSchedule(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["schedules"] }),
    onError: () => setError("Zamanlama silinemedi. Lütfen tekrar dener misin?"),
  });
  const run = useMutation({
    mutationFn: (id: string) => runScheduleNow(id),
    onSuccess: (r, id) => setRunNote((m) => ({ ...m, [id]: r.notification.message })),
    onError: () => setError("Koşum başarısız oldu. Lütfen tekrar dener misin?"),
  });

  if (!canRead) {
    return (
      <p className="font-mono text-[12px] leading-relaxed text-neutral-400">
        Zamanlanmış raporları görüntülemek için yetkiniz yok.
      </p>
    );
  }

  const list = data ?? [];

  return (
    <div className="space-y-2">
      {error && (
        <p className="border-l-2 border-red-500/50 bg-red-500/[0.04] px-2 py-1 font-mono text-[11px] text-red-500">
          {error}
        </p>
      )}
      {isLoading ? (
        <p className="font-mono text-[12px] text-neutral-400">yükleniyor…</p>
      ) : isError ? (
        <p className="font-mono text-[12px] text-red-500">Zamanlamalar yüklenemedi.</p>
      ) : list.length === 0 ? (
        <p className="font-mono text-[12px] leading-relaxed text-neutral-400">
          henüz zamanlanmış rapor yok — bir raporun üstündeki{" "}
          <span className="text-foreground">🔔 zamanla</span> ile oluştur.
        </p>
      ) : (
        <ul className="space-y-1.5">
          {list.map((s) => (
            <li key={s.id} className="border border-hairline px-2 py-1.5">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="truncate font-mono text-[12px] text-foreground">{s.label}</p>
                  <p className="font-mono text-[10px] text-neutral-400">
                    {_EVERY_TR[s.every] ?? s.every}
                    {s.at ? ` · ${s.at}` : ""}
                    {s.period ? ` · ${s.period}` : ""}
                    {s.threshold ? " · alarmlı" : ""}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <button
                    onClick={() => run.mutate(s.id)}
                    disabled={run.isPending}
                    title="Şimdi çalıştır"
                    aria-label="Şimdi çalıştır"
                    className="font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
                  >
                    ▶ şimdi çalıştır
                  </button>
                  <button
                    onClick={() => del.mutate(s.id)}
                    disabled={del.isPending}
                    title="Zamanlamayı sil"
                    aria-label="Zamanlamayı sil"
                    className="font-mono text-[13px] text-neutral-400 transition-colors hover:text-red-500"
                  >
                    ×
                  </button>
                </div>
              </div>
              {runNote[s.id] && (
                <p className="mt-1 border-t border-hairline pt-1 font-mono text-[10px] text-accent">
                  {runNote[s.id]}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
