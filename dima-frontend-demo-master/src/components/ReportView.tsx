"use client";

// Çok-blok / çok-SAYFA rapor görünümü (ADR-0024). Backend /report bir Report döndürür
// (bloklar → sonuç + viz kararı, sayfalara bölünmüş); burada YALNIZ render edilir. Her blok
// mevcut ResultView ile çizilir (chat/pano ile AYNI viz). "yazdır / PDF" tarayıcı yazdırmasını
// açar; sayfalar arasında CSS sayfa-sonu (break-after) verilir. Rapor sabit ölçek (kullanıcı
// notu: e-posta/rapor tarafında özel responsive gerekmez).

import type { Report } from "@/lib/types";
import { ResultView } from "@/components/ResultView";

export function ReportView({ report, onClose }: { report: Report; onClose: () => void }) {
  const pages = report.pages ?? [];
  const btn =
    "flex h-[26px] items-center border border-hairline px-2 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground";

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-center justify-between border-b border-hairline px-6 py-3 print:hidden">
        <h2 className="truncate font-mono text-[15px] text-foreground">
          {report.title}
          <span className="ml-2 text-neutral-400">· {report.block_count} blok</span>
        </h2>
        <div className="flex shrink-0 items-center gap-2">
          <button onClick={() => window.print()} className={btn} title="Yazdır / PDF">
            ⎙ yazdır / PDF
          </button>
          <button onClick={onClose} className={btn}>
            ✕ kapat
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto bg-neutral-500/[0.03] p-4">
        {/* 🔴 FAZ 5.13b — SABİT YAPI: kapak → yönetici özeti → kartlar → KAYNAK LİSTESİ.
            ⚠ Hiçbiri `print:hidden` TAŞIMAZ: yol haritasının şartı *"PDF'e döküldüğünde
            bile `contract_id` altta kalır"* ve buradaki PDF yolu `window.print()`. */}
        {(report.kapak || report.yonetici_ozeti?.length) && (
          <section className="mx-auto mb-4 max-w-4xl border border-hairline bg-background p-4">
            {report.kapak && (
              <p className="font-mono text-[10px] text-neutral-400">
                {report.kapak.tarih}
                {report.kapak.yazar ? ` · ${report.kapak.yazar}` : ""}
              </p>
            )}
            {!!report.yonetici_ozeti?.length && (
              <>
                <h3 className="mt-2 font-mono text-[12px] uppercase tracking-wide text-muted">
                  yönetici özeti
                </h3>
                <ul className="mt-1 space-y-0.5">
                  {report.yonetici_ozeti.map((o) => (
                    <li key={o} className="text-[13px] leading-relaxed text-foreground">
                      · {o}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>
        )}
        {pages.map((page, pi) => (
          <section
            key={pi}
            className="mx-auto mb-4 max-w-4xl"
            style={{ breakAfter: pi < pages.length - 1 ? "page" : "auto" }}
          >
            {pi > 0 && (
              <div className="mb-2 text-center font-mono text-[10px] uppercase tracking-widest text-neutral-400">
                sayfa {pi + 1}/{pages.length}
              </div>
            )}
            {page.map((b, bi) => (
              <div
                key={bi}
                className="mb-4 border border-hairline bg-background p-4"
                style={{ breakInside: "avoid" }}
              >
                <div className="mb-3 flex items-baseline justify-between gap-2">
                  <h3 className="truncate font-mono text-[13px] text-foreground">
                    {b.title ||
                      (typeof b.cube_query.cube === "string" ? b.cube_query.cube : "blok")}
                  </h3>
                  {b.period && (
                    <span className="shrink-0 font-mono text-[11px] text-neutral-400">
                      {b.period}
                    </span>
                  )}
                </div>
                {b.error ? (
                  <p className="font-mono text-[11px] text-red-500">{b.error}</p>
                ) : b.result ? (
                  <ResultView result={b.result} viz={b.viz} viewHint={b.view_hint ?? undefined} />
                ) : (
                  <p className="font-mono text-[11px] text-neutral-400">veri yok</p>
                )}
              </div>
            ))}
          </section>
        ))}

        {/* 🔴 KAYNAK LİSTESİ — raporun ALTINDA ve BASKIDA GÖRÜNÜR.
            Yol haritasının şartı: *"PDF'e döküldüğünde bile `contract_id` altta kalır."*
            Buradaki PDF yolu `window.print()`; bu bölüm `print:hidden` TAŞIMAZ.
            ⚠ `contract_id: null` bir MAKBUZSUZLUKTUR ve gösterilir — kanıtın yokluğunu
            gizlemek, kanıtsızlıktan kötüdür. */}
        {!!report.kaynaklar?.length && (
          <section className="mx-auto max-w-4xl border-t border-hairline pt-3">
            <h3 className="font-mono text-[11px] uppercase tracking-wide text-muted">
              kaynaklar
            </h3>
            <ul className="mt-1 space-y-0.5">
              {report.kaynaklar.map((k, i) => (
                <li key={i} className="font-mono text-[10px] text-neutral-400">
                  {k.blok}
                  {k.cube ? ` · ${k.cube}` : ""} ·{" "}
                  {k.contract_id ? (
                    <span className="text-foreground">{k.contract_id}</span>
                  ) : (
                    <span className="text-amber-600">makbuzsuz</span>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}
