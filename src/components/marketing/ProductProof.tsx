"use client";

import { useState } from "react";
import { CheckCircle2, Database, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { MarketingLocale } from "@/content/marketing";

const copy = {
  tr: {
    question: "Bu hafta hedefin gerisinde kalan makineler hangileri?",
    context: "OEE hedefi ≥ %78 · dönem: son 7 gün · boyut: makine",
    tabs: ["Sonuç", "SQL", "Çözüm izi"],
    result: "3 makine eşik altında",
    columns: ["Makine", "OEE", "Fark"],
    rows: [["JET-04", "%71,8", "−6,2 puan"], ["HT-02", "%74,1", "−3,9 puan"], ["JET-01", "%77,3", "−0,7 puan"]],
    trace: ["Semantic ölçü eşleşti: oee", "SELECT-only guard geçti", "Dry-plan başarıyla tamamlandı"],
  },
  en: {
    question: "Which machines fell behind target this week?",
    context: "OEE target ≥ 78% · period: last 7 days · dimension: machine",
    tabs: ["Result", "SQL", "Resolution trace"],
    result: "3 machines below threshold",
    columns: ["Machine", "OEE", "Delta"],
    rows: [["JET-04", "71.8%", "−6.2 pts"], ["HT-02", "74.1%", "−3.9 pts"], ["JET-01", "77.3%", "−0.7 pts"]],
    trace: ["Semantic measure matched: oee", "SELECT-only guard passed", "Dry plan completed"],
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
            {tab === 1 && <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-6 text-muted-foreground"><code>{`SELECT machine_name,\n  ROUND(AVG(oee) * 100, 1) AS oee_pct\nFROM production_performance\nWHERE production_date >= CURRENT_DATE - INTERVAL '7 days'\nGROUP BY machine_name\nHAVING AVG(oee) < 0.78\nORDER BY oee_pct ASC;`}</code></pre>}
            {tab === 2 && <ol className="space-y-4">{c.trace.map((item, index) => <li className="flex gap-4" key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-xs text-brand">{index + 1}</span><span className="pt-1 text-sm">{item}</span></li>)}</ol>}
          </div>
        </div>
      </div>
    </div>
  );
}
