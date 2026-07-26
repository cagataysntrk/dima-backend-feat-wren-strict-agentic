"use client";

import { type KeyboardEvent, useRef, useState } from "react";
import { BarChart3, CheckCircle2, Database, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { MarketingLocale } from "@/content/marketing";

const copy = {
  tr: {
    question: "Brüt kârı hedefin altında kalan ürün grupları hangileri?",
    context: "Brüt kâr hedefi ≥ %32 · dönem: bu çeyrek · boyut: ürün grubu",
    tabs: ["Sonuç", "Grafik", "SQL", "Çözüm izi"],
    result: "3 ürün grubu eşik altında",
    columns: ["Ürün grubu", "Brüt kâr", "Fark"],
    rows: [["Kurumsal", "%24,8", "−7,2 puan"], ["Standart", "%28,1", "−3,9 puan"], ["Hizmet", "%31,3", "−0,7 puan"]],
    trace: ["Semantic ölçü eşleşti: gross_margin", "SELECT-only guard geçti", "Dry-plan başarıyla tamamlandı"],
    chartLabel: "Ürün gruplarının brüt kâr oranları: Kurumsal yüzde 24,8; Standart yüzde 28,1; Hizmet yüzde 31,3.",
  },
  en: {
    question: "Which product groups are below gross-margin target?",
    context: "Gross-margin target ≥ 32% · period: this quarter · dimension: product group",
    tabs: ["Result", "Chart", "SQL", "Resolution trace"],
    result: "3 product groups below threshold",
    columns: ["Product group", "Gross margin", "Delta"],
    rows: [["Enterprise", "24.8%", "−7.2 pts"], ["Standard", "28.1%", "−3.9 pts"], ["Services", "31.3%", "−0.7 pts"]],
    trace: ["Semantic measure matched: gross_margin", "SELECT-only guard passed", "Dry plan completed"],
    chartLabel: "Gross margin by product group: Enterprise 24.8 percent, Standard 28.1 percent, Services 31.3 percent.",
  },
} as const;

export function ProductProof({ locale }: { locale: MarketingLocale }) {
  const c = copy[locale];
  const [tab, setTab] = useState(0);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  function onTabKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const last = c.tabs.length - 1;
    const next = event.key === "Home" ? 0 : event.key === "End" ? last : event.key === "ArrowRight" ? (index + 1) % c.tabs.length : (index - 1 + c.tabs.length) % c.tabs.length;
    setTab(next);
    tabRefs.current[next]?.focus();
  }
  return (
    <div className="overflow-hidden rounded-xl border bg-card shadow-xl">
      <div className="flex items-center gap-2 border-b px-4 py-3 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
        <span className="size-2 rounded-full bg-brand" /> local sanitized simulation
      </div>
      <div className="grid lg:grid-cols-[0.85fr_1.35fr]">
        <div className="border-b p-5 lg:border-r lg:border-b-0 sm:p-7">
          <p className="text-lg font-medium leading-7">{c.question}</p>
          <div className="mt-6 space-y-3 text-sm text-muted-foreground">
            <p className="flex gap-3"><Database className="size-4 shrink-0 text-brand" />{c.context}</p>
            <p className="flex gap-3"><ShieldCheck className="size-4 shrink-0 text-brand" />read-only · modeled · dry-planned</p>
          </div>
        </div>
        <div>
          <div role="tablist" aria-label={locale === "tr" ? "Ürün kanıtı görünümleri" : "Product proof views"} className="flex overflow-x-auto border-b p-2">
            {c.tabs.map((label, index) => (
              <Button
                key={label}
                ref={(node) => { tabRefs.current[index] = node; }}
                id={`proof-tab-${index}`}
                role="tab"
                aria-controls="proof-panel"
                aria-selected={tab === index}
                tabIndex={tab === index ? 0 : -1}
                variant={tab === index ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setTab(index)}
                onKeyDown={(event) => onTabKeyDown(event, index)}
              >
                {label}
              </Button>
            ))}
          </div>
          <div id="proof-panel" role="tabpanel" aria-labelledby={`proof-tab-${tab}`} tabIndex={0} className="min-h-72 p-5 sm:p-7">
            {tab === 0 && (
              <>
                <p className="mb-5 flex items-center gap-2 text-sm font-medium"><CheckCircle2 className="size-4 text-chart-2" />{c.result}</p>
                <div className="overflow-x-auto border">
                  <table className="w-full min-w-md text-left text-sm">
                    <thead className="bg-muted font-mono text-[11px] uppercase tracking-wider text-muted-foreground"><tr>{c.columns.map((col) => <th className="px-4 py-3 font-medium" key={col}>{col}</th>)}</tr></thead>
                    <tbody>{c.rows.map((row) => <tr className="border-t" key={row[0]}>{row.map((cell) => <td className="px-4 py-3" key={cell}>{cell}</td>)}</tr>)}</tbody>
                  </table>
                </div>
              </>
            )}
            {tab === 1 && (
              <div role="img" aria-label={c.chartLabel}>
                <div aria-hidden="true" className="flex items-center gap-2 text-sm font-medium"><BarChart3 className="size-4 text-brand" />gross_margin / target 32%</div>
                <div aria-hidden="true" className="mt-7 space-y-5">
                  {c.rows.map((row, index) => (
                    <div className="grid grid-cols-[80px_1fr_54px] items-center gap-3" key={row[0]}>
                      <span className="truncate text-xs">{row[0]}</span>
                      <div className="relative h-7 overflow-hidden rounded-sm bg-muted">
                        <div className="h-full bg-brand/65" style={{ width: `${[78, 88, 98][index]}%` }} />
                        <span className="absolute inset-y-0 right-[2%] border-r border-dashed border-foreground/40" />
                      </div>
                      <span className="text-right font-mono text-[10px]">{row[1]}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {tab === 2 && <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-6 text-muted-foreground"><code>{`SELECT product_group,\n  ROUND(100 * SUM(gross_profit) /\n    NULLIF(SUM(net_revenue), 0), 1) AS margin_pct\nFROM sales_performance\nWHERE booked_at >= DATE_TRUNC('quarter', CURRENT_DATE)\nGROUP BY product_group\nHAVING SUM(gross_profit) /\n  NULLIF(SUM(net_revenue), 0) < 0.32\nORDER BY margin_pct ASC;`}</code></pre>}
            {tab === 3 && <ol className="space-y-4">{c.trace.map((item, index) => <li className="flex gap-4" key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-xs text-brand">{index + 1}</span><span className="pt-1 text-sm">{item}</span></li>)}</ol>}
          </div>
        </div>
      </div>
    </div>
  );
}
