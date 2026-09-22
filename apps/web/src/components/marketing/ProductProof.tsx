"use client";

import { type CSSProperties, type KeyboardEvent, useRef, useState } from "react";
import { AnimatePresence, m } from "motion/react";
import { ArrowRight, BarChart3, Check, CheckCircle2, Database, Layers3, ShieldCheck } from "lucide-react";
import { Button } from "@dima/ui/primitives/button";
import type { MarketingLocale } from "@/content/marketing";
import { trackMarketingEvent } from "@/lib/marketing/analytics";

const copy = {
  tr: {
    kicker: "Yerel örnek çalışma",
    steps: ["Sor", "Bağlam", "Koru", "Cevap"],
    question: "Makine bazında OEE ve fire oranı nedir?",
    context: "Örnek veri · dönem: bu vardiya · boyut: makine",
    result: "3 makine incelendi",
    columns: ["Makine", "OEE", "Fire"],
    rows: [["Jet 01", "%82", "%3,4"], ["Jet 02", "%76", "%5,1"], ["Jet 03", "%89", "%2,2"]],
    questionNote: "Günlük iş dilinden başlar.",
    contextNote: "İş terimleri ve kaynak tabloları eşleşir.",
    guardNote: "Sorgu çalışmadan önce sınırları görünür.",
    answerNote: "Sonuç, grafik ve kaynak aynı yerde.",
    definition: "Makine + OEE + fire",
    source: "dyehouse_shift_summary",
    trace: ["Makine ve OEE tanımı eşleşti", "Yalnızca okuma kontrolü tamamlandı", "Çalıştırma planı kontrol edildi", "Sonuç kaynağı görünür tutuldu"],
    chartLabel: "Örnek makine görünümü: Jet 01 OEE yüzde 82 ve fire yüzde 3,4; Jet 02 OEE yüzde 76 ve fire yüzde 5,1; Jet 03 OEE yüzde 89 ve fire yüzde 2,2.",
    viewHint: "Bir adım seçin",
  },
  en: {
    kicker: "Local sample workspace",
    steps: ["Ask", "Context", "Guard", "Answer"],
    question: "What are OEE and waste by machine?",
    context: "Sample data · period: this shift · dimension: machine",
    result: "3 machines reviewed",
    columns: ["Machine", "OEE", "Waste"],
    rows: [["Jet 01", "82%", "3.4%"], ["Jet 02", "76%", "5.1%"], ["Jet 03", "89%", "2.2%"]],
    questionNote: "It starts in the language of the work.",
    contextNote: "Business terms and source tables are matched.",
    guardNote: "The boundaries are visible before execution.",
    answerNote: "Result, chart, and source stay together.",
    definition: "Machine + OEE + waste",
    source: "dyehouse_shift_summary",
    trace: ["Machine and OEE definition matched", "Read-only access check completed", "Execution plan checked", "Result source kept visible"],
    chartLabel: "Sample machine view: Jet 01 OEE 82 percent and waste 3.4 percent; Jet 02 OEE 76 percent and waste 5.1 percent; Jet 03 OEE 89 percent and waste 2.2 percent.",
    viewHint: "Choose a step",
  },
} as const;

export function ProductProof({ locale }: { locale: MarketingLocale }) {
  const c = copy[locale];
  const [step, setStep] = useState(0);
  const stepRefs = useRef<Array<HTMLButtonElement | null>>([]);

  function selectStep(next: number) {
    setStep(next);
    trackMarketingEvent("product_proof_view_changed", { view: c.steps[next] });
  }

  function onStepKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const last = c.steps.length - 1;
    const next = event.key === "Home" ? 0 : event.key === "End" ? last : event.key === "ArrowRight" ? (index + 1) % c.steps.length : (index - 1 + c.steps.length) % c.steps.length;
    selectStep(next);
    stepRefs.current[next]?.focus();
  }

  return (
    <div className="proof-canvas overflow-hidden rounded-[1.25rem] border border-foreground/15 bg-foreground text-background shadow-2xl shadow-foreground/10">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-background/15 px-5 py-4 sm:px-7">
        <div className="flex items-center gap-3 font-mono text-xs uppercase text-background/65">
          <span aria-hidden="true" className="visual-pulse size-2 rounded-full bg-chart-2" />
          {c.kicker}
        </div>
        <span className="font-mono text-micro uppercase text-background/45">{c.viewHint}</span>
      </div>

      <div className="border-b border-background/15 px-4 py-4 sm:px-7">
        <div role="tablist" aria-label={locale === "tr" ? "Kanıt akışı" : "Proof sequence"} className="grid grid-cols-4 gap-1">
          {c.steps.map((label, index) => (
            <Button
              key={label}
              ref={(node) => { stepRefs.current[index] = node; }}
              id={`proof-step-${index}`}
              role="tab"
              aria-controls="proof-step-panel"
              aria-selected={step === index}
              tabIndex={step === index ? 0 : -1}
              variant="ghost"
              className={`group min-h-12 justify-start rounded-md border px-3 text-left text-background transition-colors hover:bg-background/10 hover:text-background focus-visible:bg-background/10 focus-visible:text-background ${step === index ? "border-background/35 bg-background/12" : "border-transparent text-background/55"}`}
              onClick={() => selectStep(index)}
              onKeyDown={(event) => onStepKeyDown(event, index)}
            >
              <span className={`mr-2 font-mono text-micro ${step === index ? "text-chart-2" : "text-background/35"}`}>{String(index + 1).padStart(2, "0")}</span>
              <span className="text-xs font-medium sm:text-sm">{label}</span>
              {index < c.steps.length - 1 ? <ArrowRight aria-hidden="true" className="ml-auto hidden size-3 text-background/25 sm:block" /> : null}
            </Button>
          ))}
        </div>
      </div>

      <div id="proof-step-panel" role="tabpanel" aria-labelledby={`proof-step-${step}`} tabIndex={0} className="grid min-h-[22rem] lg:grid-cols-[0.7fr_1.3fr]">
        <div className="border-b border-background/15 p-6 sm:p-8 lg:border-b-0 lg:border-r">
          <p className="font-mono text-micro uppercase text-chart-2">{String(step + 1).padStart(2, "0")} / {c.steps[step]}</p>
          <p className="mt-5 max-w-sm text-2xl font-medium leading-tight sm:text-3xl">{step === 0 ? c.question : step === 1 ? c.definition : step === 2 ? c.guardNote : c.result}</p>
          <p className="mt-5 max-w-sm text-sm leading-6 text-background/60">{step === 0 ? c.questionNote : step === 1 ? c.contextNote : step === 2 ? c.guardNote : c.answerNote}</p>
          <div className="mt-8 flex flex-wrap gap-2 font-mono text-micro uppercase text-background/45">
            <span className="rounded-full border border-background/15 px-3 py-1.5">{locale === "tr" ? "anonim örnek" : "anonymized sample"}</span>
            <span className="rounded-full border border-background/15 px-3 py-1.5">{locale === "tr" ? "yalnızca okuma" : "read-only"}</span>
          </div>
        </div>

        <div className="min-w-0 p-4 sm:p-7">
          <AnimatePresence mode="wait" initial={false}>
            <m.div
              key={step}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              initial={{ opacity: 0, y: 8 }}
              transition={{ duration: 0.24 }}
              className="h-full"
            >
              {step === 0 ? <QuestionStep locale={locale} question={c.question} /> : null}
              {step === 1 ? <ContextStep locale={locale} definition={c.definition} source={c.source} /> : null}
              {step === 2 ? <GuardStep locale={locale} trace={c.trace} /> : null}
              {step === 3 ? <AnswerStep locale={locale} c={c} /> : null}
            </m.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function QuestionStep({ locale, question }: { locale: MarketingLocale; question: string }) {
  return (
    <div className="flex h-full min-h-64 flex-col justify-between rounded-lg border border-background/15 bg-background/[0.04] p-5 sm:p-6">
      <div>
        <p className="font-mono text-micro uppercase tracking-[0.16em] text-background/45">{locale === "tr" ? "iş sorusu" : "business question"}</p>
        <p className="mt-5 max-w-xl text-xl leading-8 sm:text-2xl">“{question}”</p>
      </div>
      <div className="mt-10 flex flex-wrap gap-2">
        {(locale === "tr" ? ["makine", "OEE", "fire", "bu vardiya"] : ["machine", "OEE", "waste", "this shift"]).map((item) => <span className="rounded-full border border-background/15 px-3 py-2 font-mono text-xs text-background/65" key={item}>{item}</span>)}
      </div>
    </div>
  );
}

function ContextStep({ locale, definition, source }: { locale: MarketingLocale; definition: string; source: string }) {
  return (
    <div className="flex h-full min-h-64 flex-col justify-center gap-3">
      <ContextRow icon={<Database className="size-4" />} label={locale === "tr" ? "Kaynak" : "Source"} value={source} />
      <div className="hidden h-5 w-px bg-chart-2/70 sm:block sm:ml-5" />
      <ContextRow icon={<Layers3 className="size-4" />} label={locale === "tr" ? "İş tanımı" : "Definition"} value={definition} />
      <div className="hidden h-5 w-px bg-chart-2/70 sm:block sm:ml-5" />
      <ContextRow icon={<Check className="size-4" />} label={locale === "tr" ? "Bağlam" : "Context"} value={locale === "tr" ? "bu vardiya × makine" : "this shift × machine"} />
    </div>
  );
}

function ContextRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return <div className="flex items-center gap-4 rounded-lg border border-background/15 bg-background/[0.04] p-4 sm:p-5"><span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-brand text-background">{icon}</span><div className="min-w-0"><p className="font-mono text-micro uppercase tracking-[0.14em] text-background/45">{label}</p><p className="mt-1 truncate font-medium">{value}</p></div></div>;
}

function GuardStep({ locale, trace }: { locale: MarketingLocale; trace: readonly string[] }) {
  return (
    <div className="min-h-64 rounded-lg border border-background/15 bg-background/[0.04] p-5 sm:p-6">
      <div className="flex items-center justify-between gap-3 border-b border-background/15 pb-4"><p className="font-mono text-micro uppercase tracking-[0.16em] text-background/45">{locale === "tr" ? "ön kontrol" : "pre-check"}</p><ShieldCheck className="size-5 text-chart-2" aria-hidden="true" /></div>
      <ol className="mt-3">
        {trace.map((item, index) => <li className="flex gap-4 border-b border-background/10 py-4 last:border-b-0" key={item}><span className="flex size-6 shrink-0 items-center justify-center rounded-full border border-chart-2/60 font-mono text-micro text-chart-2">{index + 1}</span><span className="min-w-0 text-sm leading-6 text-background/75">{item}</span><CheckCircle2 className="ml-auto size-4 shrink-0 text-chart-2" aria-hidden="true" /></li>)}
      </ol>
    </div>
  );
}

function AnswerStep({ locale, c }: { locale: MarketingLocale; c: (typeof copy)[MarketingLocale] }) {
  return (
    <div className="min-h-64 rounded-lg border border-background/15 bg-background/[0.04] p-5 sm:p-6">
      <div className="flex items-center gap-2 text-sm font-medium"><CheckCircle2 className="size-4 text-chart-2" />{c.result}</div>
      <div className="mt-5 overflow-x-auto border border-background/15">
        <table className="w-full min-w-[26rem] text-left text-sm">
          <thead className="sticky top-0 bg-background/[0.06] font-mono text-xs uppercase tracking-wider text-background/55"><tr>{c.columns.map((col) => <th className="px-4 py-3 font-medium" key={col}>{col}</th>)}</tr></thead>
          <tbody>{c.rows.map((row) => <tr className="border-t border-background/10" key={row[0]}>{row.map((cell) => <td className="px-4 py-3" key={cell}>{cell}</td>)}</tr>)}</tbody>
        </table>
      </div>
      <div className="mt-6" role="img" aria-label={c.chartLabel}>
        <div aria-hidden="true" className="flex items-center gap-2 text-xs text-background/65"><BarChart3 className="size-4 text-chart-2" />{locale === "tr" ? "OEE görünümü" : "OEE view"}</div>
        <div aria-hidden="true" className="mt-4 space-y-3">{c.rows.map((row, index) => <div className="grid grid-cols-[minmax(4rem,6rem)_1fr_auto] items-center gap-3" key={row[0]}><span className="text-xs text-background/60">{row[0]}</span><div className="h-2 overflow-hidden rounded-full bg-background/10"><div className="marketing-bar-rise h-full rounded-full bg-chart-2" style={{ width: `${[78, 88, 98][index]}%`, "--bar-delay": `${index * 0.08}s` } as CSSProperties} /></div><span className="font-mono text-xs tabular-nums text-background/70">{row[1]}</span></div>)}</div>
      </div>
    </div>
  );
}
