"use client";

import { Fragment, type KeyboardEvent, useRef, useState } from "react";
import { AnimatePresence, m } from "motion/react";
import { BarChart3, CheckCircle2, Database, ShieldCheck } from "lucide-react";
import { AnimatedList, NumberTicker } from "@/components/marketing/MagicUI";
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
    trace: ["Brüt kâr tanımı eşleşti", "Yalnızca okuma kontrolü tamamlandı", "Çalıştırma öncesi kontrol tamamlandı"],
    chartLabel: "Ürün gruplarının brüt kâr oranları: Kurumsal yüzde 24,8; Standart yüzde 28,1; Hizmet yüzde 31,3.",
  },
  en: {
    question: "Which product groups are below gross-margin target?",
    context: "Gross-margin target ≥ 32% · period: this quarter · dimension: product group",
    tabs: ["Result", "Chart", "SQL", "Resolution trace"],
    result: "3 product groups below threshold",
    columns: ["Product group", "Gross margin", "Delta"],
    rows: [["Enterprise", "24.8%", "−7.2 pts"], ["Standard", "28.1%", "−3.9 pts"], ["Services", "31.3%", "−0.7 pts"]],
    trace: ["Gross-margin definition matched", "Read-only access check completed", "Pre-execution check completed"],
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
    <div className="@container/proof overflow-hidden rounded-xl border bg-card shadow-xl transition-shadow duration-500 focus-within:shadow-2xl focus-within:shadow-brand/5">
      <div className="flex items-center gap-2 border-b px-4 py-3 font-mono text-xs text-muted-foreground">
        <span className="visual-pulse size-2 shrink-0 rounded-full bg-brand" />
        {locale === "tr" ? "Yerel örnek çalışma" : "Local sample workspace"}
      </div>
      <div className="grid @3xl/proof:grid-cols-[0.85fr_1.35fr]">
        <div className="border-b p-5 @3xl/proof:border-b-0 @3xl/proof:border-r @3xl/proof:p-6">
          <p className="text-lg font-medium leading-7">{c.question}</p>
          <div className="mt-6 space-y-3 text-sm text-muted-foreground">
            <p className="flex gap-3"><Database className="size-4 shrink-0 text-brand" />{c.context}</p>
            <p className="flex gap-3"><ShieldCheck className="size-4 shrink-0 text-brand" />{locale === "tr" ? "yalnızca okuma · ortak tanımlar · ön kontrol" : "read-only · shared definitions · pre-checked"}</p>
          </div>
        </div>
        <div className="@container/panel">
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
          {/* min-h-56 (224px): AnimatePresence mode="wait" olduğu için taban
              tamamen kalkarsa sekme değişiminde panel zıplıyor. Taban artık
              gerçek en uzun sekmeye (SQL, 9 satır × 1.5rem = 216px) göre;
              eskiden min-h-72 (288px) idi, yani her sekmede ~70-155px ölü boşluk. */}
          <div id="proof-panel" role="tabpanel" aria-labelledby={`proof-tab-${tab}`} tabIndex={0} className="min-h-56 p-5 @3xl/proof:p-6">
            <AnimatePresence mode="wait" initial={false}>
              <m.div
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 6 }}
                initial={{ opacity: 0, y: 8 }}
                key={tab}
                transition={{ duration: 0.24 }}
              >
            {tab === 0 && (
              <>
                <p className="mb-5 flex items-center gap-2 text-sm font-medium"><CheckCircle2 className="size-4 shrink-0 text-chart-2" /><NumberTicker value={3} />{locale === "tr" ? " ürün grubu eşik altında" : " product groups below threshold"}</p>
                <div className="grid gap-2 @md/panel:hidden">
                  {c.rows.map((row) => (
                    <div className="rounded-lg border bg-background p-4" key={row[0]}>
                      <div className="flex items-center justify-between gap-3"><span className="text-xs font-medium">{row[0]}</span><span className="shrink-0 font-mono text-xs">{row[1]}</span></div>
                      <p className="mt-2 font-mono text-micro text-muted-foreground">{c.columns[2]} · {row[2]}</p>
                    </div>
                  ))}
                </div>
                <div className="hidden overflow-x-auto border @md/panel:block">
                  <table className="w-full min-w-md text-left text-sm">
                    <thead className="sticky top-0 bg-muted font-mono text-xs uppercase tracking-wider text-muted-foreground"><tr>{c.columns.map((col) => <th className="px-4 py-3 font-medium" key={col}>{col}</th>)}</tr></thead>
                    <tbody>{c.rows.map((row) => <tr className="border-t" key={row[0]}>{row.map((cell) => <td className="px-4 py-3" key={cell}>{cell}</td>)}</tr>)}</tbody>
                  </table>
                </div>
              </>
            )}
            {tab === 1 && (
              <div role="img" aria-label={c.chartLabel}>
                <div aria-hidden="true" className="flex items-center gap-2 text-sm font-medium"><BarChart3 className="size-4 shrink-0 text-brand" />{locale === "tr" ? "brüt kâr / hedef %32" : "gross margin / 32% target"}</div>
                <div aria-hidden="true" className="mt-7 space-y-5">
                  {/* Sabit 80px sütun + truncate gerçek etiketleri kesiyordu;
                      minmax ile büyüyebilen bir sütun ve `auto` değer sütunu. */}
                  {c.rows.map((row, index) => (
                    <div className="grid grid-cols-[minmax(5rem,8rem)_1fr_auto] items-center gap-3" key={row[0]}>
                      <span className="min-w-0 text-xs">{row[0]}</span>
                      <div className="relative h-7 overflow-hidden rounded-sm bg-muted">
                        <div className="marketing-bar-rise h-full bg-brand/65" style={{ width: `${[78, 88, 98][index]}%`, "--bar-delay": `${index * 0.08}s` } as React.CSSProperties} />
                        <span className="absolute inset-y-0 right-[2%] border-r border-dashed border-foreground/40" />
                      </div>
                      <span className="text-right font-mono text-xs tabular-nums">{row[1]}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* whitespace-pre (pre-wrap değil): SQL zaten anlamlı yerlerden elle
                kırılmış; ifade ortasından sarmak yatay kaydırmaktan daha kötü okunur.
                pre-wrap ile overflow-x-auto zaten birbirini iptal ediyordu. */}
            {tab === 2 && <pre className="overflow-x-auto whitespace-pre font-mono text-xs leading-6 text-muted-foreground"><code>{`SELECT product_group,\n  ROUND(100 * SUM(gross_profit) /\n    NULLIF(SUM(net_revenue), 0), 1) AS margin_pct\nFROM sales_performance\nWHERE booked_at >= DATE_TRUNC('quarter', CURRENT_DATE)\nGROUP BY product_group\nHAVING SUM(gross_profit) /\n  NULLIF(SUM(net_revenue), 0) < 0.32\nORDER BY margin_pct ASC;`}</code></pre>}
            {tab === 3 && <AnimatedList as="ul" className="space-y-4" itemClassName="flex gap-4">{c.trace.map((item, index) => <Fragment key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-xs text-brand">{index + 1}</span><span className="min-w-0 pt-1 text-sm">{item}</span></Fragment>)}</AnimatedList>}
              </m.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
