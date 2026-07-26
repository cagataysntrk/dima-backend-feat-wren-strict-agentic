"use client";

import { useState } from "react";
import { CheckCircle2, Database, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { MarketingLocale } from "@/content/marketing";

const copy = {
  tr: {
    question: "Brüt kârı hedefin altında kalan ürün grupları hangileri?",
    context: "Brüt kâr hedefi ≥ %32 · dönem: bu çeyrek · boyut: ürün grubu",
    tabs: ["Sonuç", "SQL", "Çözüm izi"],
    result: "3 ürün grubu eşik altında",
    columns: ["Ürün grubu", "Brüt kâr", "Fark"],
    rows: [["Kurumsal", "%24,8", "−7,2 puan"], ["Standart", "%28,1", "−3,9 puan"], ["Hizmet", "%31,3", "−0,7 puan"]],
    trace: ["Semantic ölçü eşleşti: gross_margin", "SELECT-only guard geçti", "Dry-plan başarıyla tamamlandı"],
  },
  en: {
    question: "Which product groups are below gross-margin target?",
    context: "Gross-margin target ≥ 32% · period: this quarter · dimension: product group",
    tabs: ["Result", "SQL", "Resolution trace"],
    result: "3 product groups below threshold",
    columns: ["Product group", "Gross margin", "Delta"],
    rows: [["Enterprise", "24.8%", "−7.2 pts"], ["Standard", "28.1%", "−3.9 pts"], ["Services", "31.3%", "−0.7 pts"]],
    trace: ["Semantic measure matched: gross_margin", "SELECT-only guard passed", "Dry plan completed"],
  },
} as const;

export function ProductProof({ locale }: { locale: MarketingLocale }) {
  const c = copy[locale];
  const [tab, setTab] = useState(0);
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
          <div role="tablist" aria-label="Product proof views" className="flex overflow-x-auto border-b p-2">
            {c.tabs.map((label, index) => (
              <Button key={label} role="tab" aria-selected={tab === index} variant={tab === index ? "secondary" : "ghost"} size="sm" onClick={() => setTab(index)}>
                {label}
              </Button>
            ))}
          </div>
          <div className="min-h-72 p-5 sm:p-7">
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
            {tab === 1 && <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-6 text-muted-foreground"><code>{`SELECT product_group,\n  ROUND(100 * SUM(gross_profit) /\n    NULLIF(SUM(net_revenue), 0), 1) AS margin_pct\nFROM sales_performance\nWHERE booked_at >= DATE_TRUNC('quarter', CURRENT_DATE)\nGROUP BY product_group\nHAVING SUM(gross_profit) /\n  NULLIF(SUM(net_revenue), 0) < 0.32\nORDER BY margin_pct ASC;`}</code></pre>}
            {tab === 2 && <ol className="space-y-4">{c.trace.map((item, index) => <li className="flex gap-4" key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-xs text-brand">{index + 1}</span><span className="pt-1 text-sm">{item}</span></li>)}</ol>}
          </div>
        </div>
      </div>
    </div>
  );
}
