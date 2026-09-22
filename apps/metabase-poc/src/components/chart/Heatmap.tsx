// POC COPY of apps/web/src/components/chart/Heatmap.tsx — unchanged. Follow-up: extract to packages/ui.
"use client";

import { useMemo } from "react";
import type { QueryResult } from "@dima/contracts";
import { buildHeatGrid, fmtValue, type Analysis } from "@dima/domain";
import { cn } from "@/lib/utils";

/**
 * Isı haritası — Recharts'ta primitifi yok, kendi ızgaramızla çiziyoruz.
 *
 * dataviz kuralı: MAGNİTÜD = sıralı (sequential) rampa — TEK hue, açıktan koyuya.
 * Gökkuşağı YASAK (renk sırası okunmaz, renk körlüğünde çöker). Bu yüzden marka
 * hue'sunun opaklığını 0.08 → 1.0 arası ölçekliyoruz: tek hue, monoton parlaklık.
 *
 * Yön semantiği: metadata'dan gelen `lowerIsBetter` ölçüde rampa TERS çevrilir
 * (fire/duruş gibi ölçülerde yüksek = kötü → koyu = kötü olmalı, iyi değil).
 *
 * KENAR ORTALAMALARI (marj): son sütun satır ortalamasını, son satır sütun
 * ortalamasını, köşe genel ortalamayı taşır. Matris okurken asıl soru "bu hücre
 * neye göre yüksek?" — marj o referansı hücrenin yanına koyar. Marjlar kesikli
 * kenarlıkla ayrılır ve renk rampasını SIKIŞTIRMAZ (uçlar yalnız veri
 * hücrelerinden hesaplanır — bkz. buildHeatGrid).
 */
export function Heatmap({
  result,
  analysis,
  measure,
  lowerIsBetter = false,
  className,
}: {
  result: QueryResult;
  analysis: Analysis;
  measure: string;
  lowerIsBetter?: boolean;
  className?: string;
}) {
  const grid = useMemo(
    () => buildHeatGrid(result, analysis, measure),
    [result, analysis, measure],
  );

  if (!grid) return null;
  const { rowLabels, colLabels, cells, min, max, grand } = grid;
  const span = max - min || 1;
  const R = rowLabels.length;
  const C = colLabels.length;

  // Marj hücreleri veri uçlarının dışına taşabilir (ortalama tek bir uç değerden
  // küçük/büyük olamaz ama satır ortalaması sütun uçlarını aşabilir) → kırp.
  const shade = (v: number) => {
    let t = Math.min(1, Math.max(0, (v - min) / span));
    if (lowerIsBetter) t = 1 - t;
    return { alpha: 0.08 + t * 0.92, dark: t > 0.55 };
  };

  const cellStyle = (v: number) => {
    const { alpha, dark } = shade(v);
    return {
      backgroundColor: `color-mix(in srgb, var(--chart-1) ${(alpha * 100).toFixed(0)}%, transparent)`,
      // koyu hücrede metin zemin rengine döner (kontrast korunur)
      color: dark ? "var(--brand-foreground)" : "var(--foreground)",
    };
  };

  return (
    <div className={cn("space-y-2", className)}>
      {/* Ölçek başlığı — matrise bakmadan önce "neye göre" sorusunu yanıtlar. */}
      {grand != null && (
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
          <span>
            Ortalama{" "}
            <span className="font-mono font-medium tabular-nums text-foreground">
              {fmtValue(grand, grid.measure)}
            </span>
          </span>
          <span className="text-muted-foreground/70">
            en düşük {fmtValue(min, grid.measure)} · en yüksek {fmtValue(max, grid.measure)}
          </span>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full border-separate border-spacing-[2px] text-xs">
          <thead>
            <tr>
              <th className="sticky left-0 bg-card" />
              {colLabels.map((c) => (
                <th
                  key={c}
                  className="px-1 pb-1 text-center font-medium whitespace-nowrap text-muted-foreground"
                >
                  {c}
                </th>
              ))}
              <th className="px-1 pb-1 text-center font-medium whitespace-nowrap text-muted-foreground/70">
                Ort.
              </th>
            </tr>
          </thead>
          <tbody>
            {rowLabels.map((r, ri) => (
              <tr key={r}>
                <th className="sticky left-0 bg-card pr-2 text-right font-medium whitespace-nowrap text-muted-foreground">
                  {r}
                </th>
                {colLabels.map((c, ci) => {
                  const v = cells[ri][ci];
                  if (v == null) return <td key={c} className="rounded-sm bg-muted/40" />;
                  return (
                    <td
                      key={c}
                      title={`${r} · ${c}: ${fmtValue(v, grid.measure)}`}
                      className="rounded-sm px-2 py-1.5 text-center tabular-nums transition-colors"
                      style={cellStyle(v)}
                    >
                      {fmtValue(v, grid.measure)}
                    </td>
                  );
                })}
                <MarginCell
                  value={cells[ri][C]}
                  measure={grid.measure}
                  title={`${r} · ortalama`}
                  style={cells[ri][C] != null ? cellStyle(cells[ri][C]!) : undefined}
                />
              </tr>
            ))}

            {/* sütun ortalamaları + köşede genel ortalama */}
            <tr>
              <th className="sticky left-0 bg-card pr-2 text-right font-medium whitespace-nowrap text-muted-foreground/70">
                Ort.
              </th>
              {colLabels.map((c, ci) => (
                <MarginCell
                  key={c}
                  value={cells[R][ci]}
                  measure={grid.measure}
                  title={`${c} · ortalama`}
                  style={cells[R][ci] != null ? cellStyle(cells[R][ci]!) : undefined}
                />
              ))}
              <MarginCell
                value={cells[R][C]}
                measure={grid.measure}
                title="genel ortalama"
                emphasis
                style={cells[R][C] != null ? cellStyle(cells[R][C]!) : undefined}
              />
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** Marj (ortalama) hücresi — kesikli kenarlıkla veri hücrelerinden ayrılır. */
function MarginCell({
  value,
  measure,
  title,
  style,
  emphasis = false,
}: {
  value: number | null;
  measure: string;
  title: string;
  style?: React.CSSProperties;
  emphasis?: boolean;
}) {
  if (value == null) return <td className="rounded-sm bg-muted/40" />;
  return (
    <td
      title={`${title}: ${fmtValue(value, measure)}`}
      className={cn(
        "rounded-sm border border-dashed border-border px-2 py-1.5 text-center tabular-nums",
        emphasis && "border-solid border-foreground/30 font-medium",
      )}
      style={style}
    >
      {fmtValue(value, measure)}
    </td>
  );
}
