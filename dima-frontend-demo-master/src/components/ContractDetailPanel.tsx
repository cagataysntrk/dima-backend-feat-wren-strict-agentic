"use client";

// Query Contract keşif/replay paneli (doğrulama turu düzeltmesi, 1 Ağustos 2026 — dış yol
// haritası P1-9/P1-10). `contract_id` daha önce ekranda küçük, TIKLANAMAZ bir metindi —
// bu panel onu gerçek bir kanıt-inceleme yüzeyine çevirir: soru+SQL+sonuç özeti + "bugün
// yeniden çalıştır" (replay) ile o kaydın hâlâ AYNI sonucu verip vermediğini gösterir.
// ReportPanel VE DrillDownPanel'den AYNI bileşen çağrılır (tek, tutarlı kanıt-inceleme UI'ı).

import { useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getContract, listContracts, replayContract } from "@/lib/api-client";

export function ContractDetailPanel({
  contractId,
  onClose,
  onSelect,
}: {
  // ⚠️ FAZ 0.6 — BOŞ dize = **kanıt geçmişi** giriş görünümü (yeni panel DEĞİL).
  // Kanıt kaydı ancak **bulunabiliyorsa** bir kanıttır: tek tek `contract_id` bilmek
  // gereken bir arşiv, arşiv değildir.
  contractId: string;
  onClose: () => void;
  onSelect?: (cid: string) => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const contractQ = useQuery({
    queryKey: ["contract", contractId],
    queryFn: () => getContract(contractId),
    enabled: Boolean(contractId),
  });
  // FAZ 0.6 — kanıt geçmişi: yalnız `contractId` YOKKEN çekilir (gereksiz istek yok).
  const gecmisQ = useQuery({
    queryKey: ["contracts", "gecmis"],
    queryFn: () => listContracts(20),
    enabled: !contractId,
  });
  const replay = useMutation({ mutationFn: () => replayContract(contractId) });

  const gecmisGorunumu = !contractId && (
    <div>
      {gecmisQ.isLoading && (
        <p className="font-mono text-[12px] text-neutral-400">yükleniyor…</p>
      )}
      {gecmisQ.data?.contracts?.length === 0 && (
        <p className="font-mono text-[12px] text-neutral-400">
          Henüz kanıt kaydı yok — bir rapor üretildiğinde burada belirir.
        </p>
      )}
      <ul className="divide-y divide-hairline">
        {(gecmisQ.data?.contracts ?? []).map((c) => (
          <li key={c.id}>
            <button
              onClick={() => onSelect?.(c.id)}
              className="w-full px-1 py-2 text-left transition-colors hover:bg-neutral-500/[0.06]"
            >
              <div className="truncate font-mono text-[12px] text-foreground">
                {c.question || "(soru yok)"}
              </div>
              <div className="mt-0.5 font-mono text-[10px] text-neutral-400">
                {c.ts ?? "—"} · {c.row_count ?? 0} satır · {c.source ?? "—"}
                <span className="ml-2 text-accent">{c.id}</span>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Query Contract kanıt kaydı"
    >
      <div
        className="max-h-[85vh] w-[min(640px,92vw)] overflow-auto border border-hairline bg-background p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* ⚠️ FAZ 0.6 — KANIT GEÇMİŞİ (giriş görünümü). `GET /contracts` tüketicisizdi:
            kayıtlar vardı ama **bulunamıyordu** — tek tek `contract_id` bilmek gereken
            bir arşiv, arşiv değildir. YENİ PANEL AÇILMADI (tavan 13/13, pay 0): liste
            bu panelin girişidir. */}
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-mono text-[13px] uppercase tracking-wide text-muted">
            {contractId ? `Kanıt kaydı — ${contractId}` : "Kanıt geçmişi"}
          </h2>
          <button onClick={onClose} aria-label="Kapat" className="text-muted hover:text-foreground">
            ✕
          </button>
        </div>

        {gecmisGorunumu}
        {contractQ.isLoading && <p className="font-mono text-[12px] text-neutral-400">…</p>}
        {contractQ.isError && (
          <p className="font-mono text-[12px] text-red-500">Kayıt bulunamadı ya da erişim yok.</p>
        )}

        {contractQ.data && (
          <div className="space-y-3 text-sm">
            <p className="text-[13px] text-foreground">{contractQ.data.question}</p>
            <p className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              {contractQ.data.ts ? new Date(contractQ.data.ts).toLocaleString("tr-TR") : ""}
              {contractQ.data.source ? ` · ${contractQ.data.source}` : ""}
              {contractQ.data.row_count != null ? ` · ${contractQ.data.row_count} satır` : ""}
            </p>
            {contractQ.data.sql && (
              <pre className="overflow-auto border border-hairline bg-neutral-950 p-3 font-mono text-[11px] leading-relaxed text-neutral-100">
                {contractQ.data.sql}
              </pre>
            )}

            <div className="border-t border-hairline pt-3">
              <button
                onClick={() => replay.mutate()}
                disabled={replay.isPending}
                className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent disabled:opacity-40"
              >
                {replay.isPending ? "yeniden çalıştırılıyor…" : "↻ bugün yeniden çalıştır"}
              </button>
              {replay.isError && (
                <p className="mt-2 font-mono text-[11px] text-red-500">
                  Yeniden çalıştırılamadı.
                </p>
              )}
              {replay.data && (
                <p className="mt-2 font-mono text-[11px] text-accent">
                  {replay.data.replay.verdict}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
