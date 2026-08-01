"use client";

// Query Contract keşif/replay paneli (doğrulama turu düzeltmesi, 1 Ağustos 2026 — dış yol
// haritası P1-9/P1-10). `contract_id` daha önce ekranda küçük, TIKLANAMAZ bir metindi —
// bu panel onu gerçek bir kanıt-inceleme yüzeyine çevirir: soru+SQL+sonuç özeti + "bugün
// yeniden çalıştır" (replay) ile o kaydın hâlâ AYNI sonucu verip vermediğini gösterir.
// ReportPanel VE DrillDownPanel'den AYNI bileşen çağrılır (tek, tutarlı kanıt-inceleme UI'ı).

import { useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getContract, replayContract } from "@/lib/api-client";

export function ContractDetailPanel({
  contractId,
  onClose,
}: {
  contractId: string;
  onClose: () => void;
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
  });
  const replay = useMutation({ mutationFn: () => replayContract(contractId) });

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
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-mono text-[13px] uppercase tracking-wide text-muted">
            Kanıt kaydı — {contractId}
          </h2>
          <button onClick={onClose} aria-label="Kapat" className="text-muted hover:text-foreground">
            ✕
          </button>
        </div>

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
