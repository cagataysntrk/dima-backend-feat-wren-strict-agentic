"use client";

// Query Contract keşif/replay paneli (doğrulama turu düzeltmesi, 1 Ağustos 2026 — dış yol
// haritası P1-9/P1-10). `contract_id` daha önce ekranda küçük, TIKLANAMAZ bir metindi —
// bu panel onu gerçek bir kanıt-inceleme yüzeyine çevirir: soru+SQL+sonuç özeti + "bugün
// yeniden çalıştır" (replay) ile o kaydın hâlâ AYNI sonucu verip vermediğini gösterir.
// ReportPanel VE DrillDownPanel'den AYNI bileşen çağrılır (tek, tutarlı kanıt-inceleme UI'ı).

import {  } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { exportAudit, getContract, listContracts, replayContract } from "@/lib/api-client";
import { useOdakTuzagi } from "@/lib/odakTuzagi";

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
  // 🔴 FAZ 7.5 · A11Y-3/A11Y-6: Esc **ve** odak tuzağı artık `useOdakTuzagi`'nin —
  // burada elle yazılmış Esc dinleyicisi, aynı kuralın üç ayrı sahibinden biriydi ve
  // üçü de odağı hiç tutmuyordu.
  const kutuRef = useOdakTuzagi<HTMLDivElement>(true, onClose);

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

  // FAZ 1.12 · AI ACT Md.13 — DENETLEYİCİ-OKUNABİLİR İHRAÇ.
  //
  // 🔴 YENİ PANEL AÇILMADI (tavan 13/13, pay 0) ve bu yer TESADÜF DEĞİL: ihracın yetkisi
  // `contract:read` — yani tam olarak bu panelin yetkisi. Kanıt kaydının incelendiği yüzey,
  // kanıt defterinin indirildiği yüzeydir; ayrı bir yere koymak denetçiyi ikinci bir
  // ekranda aratırdı.
  //
  // ⚠ İndirilen dosya `zincir_bulgulari` (bütünlük raporu) TAŞIR — bir kanıt defterini
  // bütünlük raporu olmadan teslim etmek, "işte kayıtlarım" deyip EKSİK OLUP OLMADIĞINI
  // söylememektir. Kırpma da sessiz değildir (`kirpildi`/`toplam`).
  const ihrac = useMutation({
    mutationFn: () => exportAudit(500),
    onSuccess: (veri) => {
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(veri, null, 2)], { type: "application/ld+json" }),
      );
      const a = document.createElement("a");
      a.href = url;
      a.download = "dima-denetim-kaydi.jsonld";
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  const gecmisGorunumu = !contractId && (
    <div>
      {gecmisQ.isLoading && (
        <p className="font-mono text-[12px] text-neutral-400">yükleniyor…</p>
      )}
      <div className="mb-2 flex items-center justify-between gap-2 border-b border-hairline pb-2">
        <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
          son 20 kayıt
        </span>
        <button
          onClick={() => ihrac.mutate()}
          disabled={ihrac.isPending}
          title="Tüm denetim kaydını JSON-LD / PROV-O biçiminde indir (AB Yapay Zekâ Yasası Md.13). Dosya, kaydın kopuk/bozuk olup olmadığını söyleyen bütünlük raporunu da taşır."
          className="border border-hairline px-2 py-[3px] font-mono text-[11px] text-neutral-500 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
        >
          {ihrac.isPending ? "hazırlanıyor…" : "⇩ denetim kaydı (JSON-LD)"}
        </button>
      </div>
      {ihrac.isError && (
        <p className="mb-2 font-mono text-[11px] text-red-500">
          İhraç edilemedi — bu kayda erişim yetkiniz olmayabilir.
        </p>
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
        ref={kutuRef}
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

            {/* FAZ 1.6 — KOLON KÖKENİ. Cümleler BACKEND'de üretilir (`app/lineage.py::
                cumleler`); burada ikinci bir şablon kümesi yazmak "aynı kuralın iki
                sahibi" olurdu. Teknik GRAF gösterilmez (KD-13): kullanıcının sorusu
                "bu sayı nereden geldi"dir ve cevabı bir CÜMLEDİR. */}
            {Array.isArray(
              (contractQ.data as { provenance?: { koken_cumleleri?: string[] } })
                .provenance?.koken_cumleleri,
            ) && (
              <div className="border-t border-hairline pt-3">
                <p className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                  bu sayı nereden geldi
                </p>
                <ul className="space-y-1">
                  {(
                    contractQ.data as unknown as {
                      provenance: { koken_cumleleri: string[] };
                    }
                  ).provenance.koken_cumleleri.map((c, i) => (
                    <li key={i} className="text-[12px] leading-relaxed text-neutral-300">
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="border-t border-hairline pt-3">
              <button
                onClick={() => replay.mutate()}
                disabled={replay.isPending}
                className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
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
