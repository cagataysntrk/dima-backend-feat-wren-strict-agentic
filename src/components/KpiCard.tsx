"use client";

import type { KpiCard } from "@/lib/types";

// Cross-cube KPI kartı (CCC / likidite oranları): tek headline skaler + bileşenleri
// (DSO/DIO/DPO, dönen varlık/KV kaynak…) + formül + açıklama. Cube tablosu değil bileşke.

function fmt(v: number | null | undefined, unit?: string | null): string {
  if (v === null || v === undefined) return "—";
  const s = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 2 }).format(v);
  if (!unit) return s;
  if (unit === "%") return `%${s}`;
  if (unit === "₺") return `${s} ₺`;
  return `${s} ${unit}`;
}

export function KpiCardView({ card }: { card: KpiCard }) {
  return (
    <div className="border border-hairline bg-background p-5">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">KPI</span>
        {card.lower_is_better && (
          <span className="font-mono text-[10px] tracking-wider text-neutral-400" title="Düşük değer daha iyi">
            ↓ düşük iyi
          </span>
        )}
      </div>

      <div className="mt-1 flex items-baseline gap-3">
        <span className="text-3xl font-semibold tabular-nums text-foreground">
          {fmt(card.value, card.unit)}
        </span>
        <span className="text-sm text-neutral-500">{card.label}</span>
      </div>

      {card.components?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-3 border-t border-hairline pt-4">
          {card.components.map((c) => (
            <div key={c.key} className="flex flex-col">
              <span className="text-[11px] text-neutral-400">{c.label}</span>
              <span className="font-mono text-sm tabular-nums text-neutral-700 dark:text-neutral-300">
                {fmt(c.value, c.unit)}
              </span>
            </div>
          ))}
        </div>
      )}

      {card.formula && (
        <div className="mt-3 font-mono text-[11px] text-neutral-400">= {card.formula}</div>
      )}
      {card.explain && (
        <p className="mt-3 max-w-prose whitespace-pre-line text-xs leading-relaxed text-neutral-500">
          {card.explain}
        </p>
      )}
    </div>
  );
}
