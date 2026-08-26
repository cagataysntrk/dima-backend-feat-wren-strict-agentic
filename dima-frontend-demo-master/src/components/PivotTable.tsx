"use client";

import { fmtTemporal, fmtValue } from "@/lib/format";
import type { QueryResult } from "@/lib/types";

// JENERİK çapraz tablo (pivot): VARLIK satır × ZAMAN-KOVA sütun × ÖLÇÜ hücre. "N ürün × ay ×
// ortalama fiyat" gibi uzun (N×kova satır) sonuçları okunur matrise çevirir. Zaman kovaları
// ham değerle sıralanır (etiket Türkçeye çevrilir); varlıklar ölçü toplamına göre (büyük üstte).
/** 🔴 FAZ 7.10 (hata 3) — **BİLEŞİK ANAHTAR AYRACI.**
 *
 * Burada ayraç olarak **gömülü bir NUL baytı** (`\x00`) kullanılıyordu. Teşhis
 * *"dosya binary/BOM"* diye konmuştu ve **yanlıştı**: dosya UTF-8 olarak tamamen
 * geçerliydi, bu yüzden hiçbir linter, hiçbir derleyici, hiçbir kod incelemesi görmedi.
 * Yalnız bayt düzeyinde bakan bir kapı yakalayabildi.
 *
 * ⚠ *Görünmez bir ayraç, kendisini bir kodlama sorunu gibi gösterir ve kimse veri
 * modeline bakmaz.* Ayraç artık **görünür** (`U+241F`, "unit separator" sembolü) ve
 * **adı olan bir fonksiyonun içinde** — çünkü asıl sorun karakterin kendisi değil,
 * bileşik anahtarın **dört ayrı yerde elle kurulmasıydı**: biri bir gün başka bir
 * ayraç kullanır ve `get` `set`'i bulamaz.
 *
 * ⚠ Ayraç, veride geçebilecek bir karakter **olmamalı**: `-` ya da `|` seçilseydi
 * `"A-B" + "C"` ile `"A" + "B-C"` **aynı anahtarı** üretirdi ve iki farklı hücre
 * sessizce birbirini ezerdi.
 */
const AYRAC = "␟";

function anahtar(entity: string, kova: string): string {
  return `${entity}${AYRAC}${kova}`;
}

export function PivotTable({
  result,
  timeCol,
  entityDim,
  measure,
}: {
  result: QueryResult;
  timeCol: string;
  entityDim: string;
  measure: string;
}) {
  const buckets = [...new Set(result.rows.map((r) => String(r[timeCol])))].sort();
  const totals = new Map<string, number>();
  const cell = new Map<string, unknown>();
  // 🔴🔴 `§K13` — SESSİZ ÇÖKÜŞ TESPİTİ. Ölçüldü (canlı, Playwright kampanyası, `liste_niyeti`
  // S10): sonuçta satırları AYIRT EDEN bir boyut varken (ör. 16 boyutlu bir listeleme) bu
  // bileşen yalnız İKİ boyutla (satır×sütun) matris kuruyor — geri kalan boyutlar aynı
  // (entity, kova) anahtarına düşüyor ve `cell.set()` SESSİZCE üstüne yazıyor: 1000 satır
  // görünürde 1 hücreye çöküyor, kullanıcı hiç uyarı görmüyor. Domain-agnostik: hangi
  // boyutun kaybolduğuna bakmaz, yalnız aynı anahtara BİRDEN FAZLA satır düşüp
  // düşmediğine (çarpışma) bakar — bu, `entityDim`/`timeCol` ne olursa olsun aynı.
  let carpisma = 0;
  for (const r of result.rows) {
    const e = String(r[entityDim]);
    const k = anahtar(e, String(r[timeCol]));
    if (cell.has(k)) carpisma += 1;
    totals.set(e, (totals.get(e) ?? 0) + (Number(r[measure]) || 0));
    cell.set(k, r[measure]);
  }
  const entities = [...totals.keys()].sort((a, b) => (totals.get(b) ?? 0) - (totals.get(a) ?? 0));

  return (
    <div className="overflow-auto border border-hairline">
      {carpisma > 0 && (
        <div className="border-b border-amber-500/30 bg-amber-500/10 px-3 py-2 text-[12px] text-amber-700 dark:text-amber-400">
          ⚠ Bu çapraz tablo veriye tam uymuyor: {result.rows.length} satırdan{" "}
          {carpisma} tanesi aynı hücreye düşüp üzerine yazıldı (görünmeyen veri
          var) — sonucu <strong>tablo</strong> görünümünde kontrol edin.
        </div>
      )}
      <table className="w-full border-collapse font-mono text-[12px]">
        <thead>
          <tr className="border-b border-hairline bg-neutral-500/[0.04]">
            <th className="sticky left-0 z-10 bg-background px-3 py-2 text-left font-normal text-neutral-500">
              {entityDim}
            </th>
            {buckets.map((b) => (
              <th key={b} className="whitespace-nowrap px-3 py-2 text-right font-normal text-neutral-500">
                {fmtTemporal(b, timeCol) ?? b}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {entities.map((e) => (
            <tr key={e} className="border-b border-hairline/60 hover:bg-neutral-500/[0.03]">
              <td className="sticky left-0 z-10 whitespace-nowrap bg-background px-3 py-1.5 text-left text-foreground">
                {e}
              </td>
              {buckets.map((b) => {
                const v = cell.get(anahtar(e, b));
                return (
                  <td key={b} className="px-3 py-1.5 text-right tabular-nums text-neutral-700 dark:text-neutral-300">
                    {v == null ? "—" : fmtValue(v, measure)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
