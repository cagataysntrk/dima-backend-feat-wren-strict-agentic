"use client";

import { fmtValue } from "@/lib/format";
import type { CubeQuery, Prescription } from "@/lib/types";

// FAZ G3/H — REÇETE cevabın İÇİNDE bir katman, ayrı bir panel DEĞİL.
//
// Backend'de üç şey hesaplanıyor ve düz metne çevrilseydi ÜÇÜ DE kaybolurdu:
//   · segment başına YÖN (kötüleşti/iyileşti) — `lower_is_better` BEYANINDAN
//   · YOĞUNLAŞMA oranı — "tek segmente odaklanmak anlamlı mı" sorusunun cevabı
//   · etki ve pay sayıları — chip yalnız etiket taşır
//
// Yön bir RENK kararıdır ve metinden okunmaz: "fire arttı" cümlesi kötü bir haberdir,
// "ciro arttı" iyi. Ayrımı ad tahmininden değil metadata beyanından biliyoruz; UI'ın
// bunu göstermemesi, ölçülmüş bir bilgiyi çöpe atmak olurdu.

function Yon({ yon }: { yon: string }) {
  const kotu = yon === "kotulesti";
  return (
    <span
      className={`shrink-0 font-mono text-[10px] uppercase ${kotu ? "text-red-500" : "text-emerald-600"}`}
      title={
        kotu
          ? "İSTENMEYEN yönde hareket etti (cube metadata'sındaki lower_is_better beyanına göre)"
          : "İSTENEN yönde hareket etti (lower_is_better beyanına göre)"
      }
    >
      {kotu ? "▲ kötüleşti" : "▼ iyileşti"}
    </span>
  );
}

export function PrescriptionLayer({
  recete,
  onCubeEdit,
}: {
  recete: Prescription;
  onCubeEdit?: (e: { cq: CubeQuery; label: string }) => void;
}) {
  const olcu = recete.measure ?? "";
  const yogun = recete.concentration;

  return (
    <div className="mt-2 border border-hairline">
      <div className="flex items-baseline justify-between border-b border-hairline px-2 py-1">
        <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
          reçete
        </span>
        {yogun != null && (
          <span
            className="font-mono text-[10px] text-neutral-500"
            title="En büyük segmentin brüt harekete oranı. Düşükse değişim dağınıktır ve tek bir segmente odaklanmak toplamı kayda değer biçimde değiştirmez."
          >
            yoğunlaşma %{(yogun * 100).toFixed(0)}
          </span>
        )}
      </div>

      {/* DAĞINIK DEĞİŞİMDE ÖNERİ ÜRETİLMEZ — ve bu bir eksiklik değil bir KARARDIR.
          Boş bir liste göstermek yerine NEDEN boş olduğu söylenir; `contribution`ın
          "AVG'de katkı payı TANIMSIZDIR" kapısıyla aynı disiplin. */}
      {recete.diffuse ? (
        <p className="px-2 py-2 font-mono text-[11px] leading-relaxed text-amber-600">
          {recete.rationale}
        </p>
      ) : (
        <>
          <div>
            {recete.options.map((o, i) => (
              <button
                key={`${o.segment}-${i}`}
                type="button"
                disabled={!onCubeEdit || !o.cube_query}
                onClick={() =>
                  o.cube_query && onCubeEdit?.({ cq: o.cube_query, label: o.segment })
                }
                title={
                  onCubeEdit
                    ? "Bu segmenti tek başına aç — LLM'siz koşar, kendi makbuzunu üretir"
                    : undefined
                }
                className={`flex w-full items-baseline justify-between gap-3 border-b border-hairline/40 px-2 py-1 text-left font-mono text-[11px] last:border-0 ${
                  onCubeEdit && o.cube_query
                    ? "transition-colors hover:bg-foreground/[0.04]"
                    : "cursor-default"
                }`}
              >
                <span className="w-4 shrink-0 text-neutral-500">{i + 1}.</span>
                <span className="min-w-0 flex-1 truncate text-neutral-300">
                  {onCubeEdit && o.cube_query && <span className="mr-1 text-neutral-500">↗</span>}
                  {o.segment}
                </span>
                <Yon yon={o.direction} />
                <span className="shrink-0 tabular-nums">
                  <span className={o.impact >= 0 ? "text-emerald-600" : "text-red-500"}>
                    {o.impact >= 0 ? "+" : ""}
                    {fmtValue(o.impact, olcu)}
                  </span>
                  {/* `share === null` = "net değişim ~0, pay TANIMSIZ". Backend bunu
                      bilerek uydurmuyor; UI de uydurmamalı — "%0" yazmak "katkısı yok"
                      demektir ve bu YANLIŞ olur. */}
                  <span className="ml-1 text-neutral-500">
                    ({o.share == null ? "—" : `${(o.share * 100).toFixed(0)}%`})
                  </span>
                </span>
              </button>
            ))}
          </div>
          <p className="border-t border-hairline px-2 py-1 font-mono text-[10px] leading-relaxed text-neutral-500">
            {recete.rationale}
          </p>
        </>
      )}
    </div>
  );
}
