"use client";

import { Fragment, type KeyboardEvent, useRef, useState } from "react";
import { AnimatePresence, m } from "motion/react";
import { BarChart3, CheckCircle2, Database, ShieldCheck } from "lucide-react";
import { AnimatedList } from "@/components/marketing/MagicUI";
import { Button } from "@/components/ui/button";
import type { MarketingLocale } from "@/content/marketing";
import { trackMarketingEvent } from "@/lib/marketing/analytics";

const copy = {
  tr: {
    question: "Makine bazında OEE ve fire oranı nedir?",
    context: "Örnek veri · dönem: bu vardiya · boyut: makine",
    tabs: ["Sonuç", "Grafik", "SQL", "Çözüm izi"],
    result: "3 makine incelendi",
    columns: ["Makine", "OEE", "Fire"],
    rows: [["Jet 01", "%82", "%3,4"], ["Jet 02", "%76", "%5,1"], ["Jet 03", "%89", "%2,2"]],
    trace: ["Makine ve OEE tanımı eşleşti", "Yalnızca okuma kontrolü tamamlandı", "Çalıştırma planı kontrol edildi", "Sonuç kaynağı görünür tutuldu"],
    chartLabel: "Örnek makine görünümü: Jet 01 OEE yüzde 82 ve fire yüzde 3,4; Jet 02 OEE yüzde 76 ve fire yüzde 5,1; Jet 03 OEE yüzde 89 ve fire yüzde 2,2.",
  },
  en: {
    question: "What are OEE and waste by machine?",
    context: "Sample data · period: this shift · dimension: machine",
    tabs: ["Result", "Chart", "SQL", "Resolution trace"],
    result: "3 machines reviewed",
    columns: ["Machine", "OEE", "Waste"],
    rows: [["Jet 01", "82%", "3.4%"], ["Jet 02", "76%", "5.1%"], ["Jet 03", "89%", "2.2%"]],
    trace: ["Machine and OEE definition matched", "Read-only access check completed", "Execution plan checked", "Result source kept visible"],
    chartLabel: "Sample machine view: Jet 01 OEE 82 percent and waste 3.4 percent; Jet 02 OEE 76 percent and waste 5.1 percent; Jet 03 OEE 89 percent and waste 2.2 percent.",
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
    trackMarketingEvent("product_proof_view_changed", { view: c.tabs[next] });
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
                className="min-h-11"
                onClick={() => { setTab(index); trackMarketingEvent("product_proof_view_changed", { view: label }); }}
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
                <p className="mb-5 flex items-center gap-2 text-sm font-medium"><CheckCircle2 className="size-4 shrink-0 text-chart-2" />{c.result}</p>
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
                <div aria-hidden="true" className="flex items-center gap-2 text-sm font-medium"><BarChart3 className="size-4 shrink-0 text-brand" />{locale === "tr" ? "OEE ve fire / makine" : "OEE and waste / machine"}</div>
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
            {tab === 2 && <pre className="overflow-x-auto whitespace-pre font-mono text-xs leading-6 text-muted-foreground"><code>{`SELECT machine_name,\n  ROUND(AVG(oee_pct), 1) AS oee_pct,\n  ROUND(AVG(waste_pct), 1) AS waste_pct\nFROM dyehouse_shift_summary\nWHERE shift_date = CURRENT_DATE\nGROUP BY machine_name\nORDER BY oee_pct ASC;`}</code></pre>}
            {tab === 3 && <AnimatedList as="ul" className="space-y-4" itemClassName="flex gap-4">{c.trace.map((item, index) => <Fragment key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-xs text-brand">{index + 1}</span><span className="min-w-0 pt-1 text-sm">{item}</span></Fragment>)}</AnimatedList>}
              </m.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
