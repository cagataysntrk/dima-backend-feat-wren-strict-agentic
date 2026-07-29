"use client";

import type { AskResponse } from "@dima/contracts";
import { cn } from "@/lib/utils";

/**
 * YOL DAĞILIMI (D60) — "bugün gösterdiklerinin ne kadarında yapay zekâ karar verdi?"
 *
 * Bu ürünün iddiası "LLM otorite değil, çevirmen". İddia bir slogan olarak değil
 * SAYIYLA kanıtlanmalı; veri zaten elimizde — her cevabın `source` alanı hangi
 * yoldan geldiğini söylüyor. Üç kademe:
 *
 *   ALTIN   cube / kpi / kural → LLM HİÇ karar vermedi (deterministik katalog)
 *   GÜMÜŞ   cube+llm           → LLM yalnız soruyu eşledi; sorgu ve doğrulama motorun
 *   BRONZ   llm:*              → SQL'i model üretti (denetlenmiş ama model kaynaklı)
 *
 * Renk TEK HUE'nun üç koyuluğu, gökkuşağı değil: koyuluk "determinizm" ekseninde
 * monoton okunur ve renk körlüğünde de sıralama korunur. Yüzdenin yanında ham
 * sayı da var — 3 cevaplık bir sohbette "%33" tek başına yanıltıcıdır.
 */

export type Tier = "gold" | "silver" | "bronze";

export function tierOf(source: string | null): Tier | null {
  if (!source) return null;
  if (source.startsWith("llm:")) return "bronze";
  if (source === "cube+llm") return "silver";
  // cube · kpi · kural — hepsi deterministik yol
  return "gold";
}

const TIER = {
  gold: { label: "altın", hint: "LLM'siz — deterministik katalog", alpha: 1 },
  silver: { label: "gümüş", hint: "LLM yalnız eşleme; sorgu motorun", alpha: 0.55 },
  bronze: { label: "bronz", hint: "SQL'i model üretti (denetlendi)", alpha: 0.24 },
} as const;

export function AiShare({ items, className }: { items: AskResponse[]; className?: string }) {
  const counts: Record<Tier, number> = { gold: 0, silver: 0, bronze: 0 };
  let total = 0;
  for (const item of items) {
    const t = tierOf(item.source);
    if (!t) continue;
    counts[t] += 1;
    total += 1;
  }
  if (total === 0) return null;

  const pct = (n: number) => Math.round((n / total) * 100);
  const order: Tier[] = ["gold", "silver", "bronze"];

  return (
    <section className={cn("space-y-2", className)}>
      <h3 className="text-xs font-medium text-muted-foreground">Yol dağılımı</h3>

      {/* Yığılmış tek şerit — oranı bir bakışta okutur. */}
      <div
        className="flex h-2 w-full overflow-hidden rounded-full bg-muted"
        role="img"
        aria-label={order
          .filter((t) => counts[t] > 0)
          .map((t) => `${TIER[t].label} %${pct(counts[t])}`)
          .join(", ")}
      >
        {order.map((t) =>
          counts[t] > 0 ? (
            <span
              key={t}
              style={{
                width: `${(counts[t] / total) * 100}%`,
                backgroundColor: `color-mix(in srgb, var(--brand) ${TIER[t].alpha * 100}%, transparent)`,
              }}
            />
          ) : null,
        )}
      </div>

      <ul className="space-y-1">
        {order.map((t) => (
          <li key={t} className="flex items-center gap-2 text-xs">
            <span
              className="size-2 shrink-0 rounded-[2px]"
              style={{
                backgroundColor: `color-mix(in srgb, var(--brand) ${TIER[t].alpha * 100}%, transparent)`,
              }}
              aria-hidden
            />
            <span className="font-medium text-foreground">%{pct(counts[t])}</span>
            <span className="text-muted-foreground">{TIER[t].label}</span>
            <span className="font-mono text-[10px] text-muted-foreground/70 tabular-nums">
              {counts[t]}/{total}
            </span>
            <span className="ml-auto truncate text-[11px] text-muted-foreground/80">
              {TIER[t].hint}
            </span>
          </li>
        ))}
      </ul>

      <p className="text-[11px] leading-relaxed text-muted-foreground">
        LLM burada <span className="font-medium text-foreground">otorite değil çevirmen</span>:
        soruyu kataloğa çevirir, sorguyu motor kurar ve doğrular. Altın satırda model
        hiç karar vermedi.
      </p>
    </section>
  );
}
