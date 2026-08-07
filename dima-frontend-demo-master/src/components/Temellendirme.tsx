"use client";

/**
 * 🔴 G1 — TEMELLENDİRME: *"anladığım şu…"*
 *
 * ## Neden ayrı bir bileşen
 *
 * `test_frontend_buyume.py` bu render'ı `ReportCard.tsx` içindeyken **yakaladı**:
 * tavan aşıldı. Kapının kendi talimatı: *"yeni davranışı bir **bileşene çıkar**,
 * tavanı yükseltme."* `Makbuz` · `SertifikaBandi` · `HataSeridi` tam böyle doğmuştu.
 *
 * ## Neden bu satır var
 *
 * Üretimdeki başarısızlığın **%69'u** *"SQL çalıştı, makul bir sayı döndü, ama BAŞKA
 * bir sorunun cevabıydı"* sınıfı (`WRONG_FILTER` %54,6 + `WRONG_SCOPE` %14,4).
 * Garson **siparişi tekrarlar** — hata ilk saniyede görünür olur.
 *
 * ⚠ Bu bir **garanti değil**, bir **görünürlük**: etiketi okumayan kullanıcı yanlış
 * sayıyı yine taşır. Sınır `app/temellendirme.py`'de de yazılı.
 *
 * ⚠ Ve **0 token**: kaynağı yalnız `cube_query`. LLM tamamen düşse bile bu satır gelir
 * (bozulma merdiveninin 3. basamağı).
 */

import type { AskItem } from "@/lib/types";

export function Temellendirme({ item }: { item: AskItem }) {
  const t = item.temellendirme;
  if (!t) return null;

  const rozetler = [
    t.olcu,
    t.donem,
    t.granulerlik,
    ...(t.kirilim ?? []),
    ...(t.filtreler ?? []),
  ].filter(Boolean) as string[];

  if (rozetler.length === 0) return null;

  return (
    <span className="inline-flex flex-wrap items-center gap-1">
      <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
        anladığım
      </span>
      {rozetler.map((etiket) => (
        <span
          key={etiket}
          className="border border-hairline px-1.5 py-0.5 font-mono text-[10px] text-neutral-500"
          title="Sistemin sorudan anladığı — deterministik, LLM'siz"
        >
          {etiket}
        </span>
      ))}
    </span>
  );
}
