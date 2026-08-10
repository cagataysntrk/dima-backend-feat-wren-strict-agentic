"use client";

import { forwardRef, useRef } from "react";
import {
  Braces,
  Check,
  CircleGauge,
  Database,
  FileCode2,
  Fingerprint,
  GitBranch,
  KeyRound,
  LockKeyhole,
  Network,
  ShieldCheck,
  Table2,
} from "lucide-react";
import {
  AnimatedBeam,
  AnimatedList,
  MagicCard,
  NumberTicker,
} from "@/components/marketing/MagicUI";
import { TileBody } from "@/components/marketing/MarketingPrimitives";
import type { MarketingLocale } from "@/content/marketing";

type LocaleProps = { locale: MarketingLocale };

const labels = {
  tr: {
    semanticTitle: "Ortak tanımlar üzerinde bağlı operasyon",
    semanticBody: "Kaynak sistemler tablo isimleriyle değil; müşteri, ürün, gelir ve dönem gibi onaylı iş kavramlarıyla bağlanır.",
    securityTitle: "Her istek aynı güven zincirinden geçer",
    securityBody: "Oturum, kurum kapsamı, yetki ve sorgu kontrolleri her istekte yeniden uygulanır.",
    integrationTitle: "Veri kaynaklarından anlaşılır raporlara",
    integrationBody: "Bağlantı imkânı ile Dima’da doğrulanmış kullanım birbirinden açıkça ayrılır.",
    workbenchTitle: "Aynı cevap, farklı inceleme biçimleri",
    workbenchBody: "Sonuç, grafik, sorgu ve cevabın kaynağı tek çalışma alanında kalır.",
    validationTitle: "Yapay zekâ önerisi doğrudan çalıştırılmaz",
    validationBody: "Öneri, ortak tanımlar ve güvenlik kontrollerinden geçmeden veri kaynağına ulaşmaz.",
    sources: "Kaynaklar",
    model: "Ortak iş tanımları",
    consumers: "Kullanım alanları",
    available: "Dima’da doğrulandı",
    planned: "planlanıyor",
    verified: "örnek veri",
    concepts: "Müşteri × Ürün × Dönem",
    customerSource: "müşteri kaynağı",
    commercialSource: "ticari kaynak",
    metricSurface: "performans göstergesi",
    evidenceSurface: "cevap ve kaynak",
    securityGates: [["Oturum", "güvenli yenileme"], ["Kurum", "sınırlandırılmış kapsam"], ["Yetki", "sunucu kontrolü"], ["Sorgu", "yalnızca okuma"]],
    requestStart: "Kullanıcı isteği",
    requestEnd: "kontrol edilmiş sorgu",
    productPerformance: "Makine performansı",
    grossMargin: "OEE",
    productGroups: "Makine incelendi",
    belowTarget: "Fire",
    periodStart: "Vardiya başlangıcı",
    current: "güncel",
    validationSteps: [["Yapay zekâ önerisi", "aday sorgu"], ["İş tanımları", "ölçü + ayrıntı"], ["Yalnızca okuma", "izin kontrolü"], ["Ön kontrol", "çalıştırılabilir"], ["Çalıştırma", "yetki kapsamında"]],
    workbenchNav: ["Konuşma", "Katalog", "Sözleşmeler", "Raporlar"],
  },
  en: {
    semanticTitle: "Connected operations over shared definitions",
    semanticBody: "Source systems connect through approved concepts such as customer, product, revenue, and period—not only table names.",
    securityTitle: "Every request follows the same trust chain",
    securityBody: "Session, tenant, permission, and query guards do not disappear when analytics gets faster.",
    integrationTitle: "From data sources to clear reports",
    integrationBody: "Connection capability and verified Dima support are shown as separate states.",
    workbenchTitle: "The same answer in several useful views",
    workbenchBody: "The result, chart, query, and answer source stay in one workspace.",
    validationTitle: "AI suggestions are never executed directly",
    validationBody: "A proposal cannot reach the data source before business-definition and security checks pass.",
    sources: "Sources",
    model: "Shared business definitions",
    consumers: "Reports and workflows",
    available: "Verified in Dima",
    planned: "Planned",
    verified: "sample data",
    concepts: "Customer × Product × Period",
    customerSource: "customer source",
    commercialSource: "commercial source",
    metricSurface: "performance metric",
    evidenceSurface: "answer and source",
    securityGates: [["Session", "secure renewal"], ["Organization", "limited scope"], ["Permission", "server check"], ["Query", "read-only check"]],
    requestStart: "User request",
    requestEnd: "checked query",
    productPerformance: "Machine performance",
    grossMargin: "OEE",
    productGroups: "Machines reviewed",
    belowTarget: "Waste",
    periodStart: "Shift start",
    current: "current",
    validationSteps: [["AI proposal", "candidate query"], ["Business definitions", "metric + detail"], ["Read-only access", "permission check"], ["Pre-check", "ready to run"], ["Execution", "permission scoped"]],
    workbenchNav: ["Conversation", "Catalog", "Contracts", "Reports"],
  },
} as const;

function VisualFrame({
  title,
  body,
  children,
  className = "",
}: {
  title: string;
  body: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <figure className={`flex flex-col overflow-hidden rounded-xl border bg-card shadow-lg ${className}`}>
      {/* @container/stage: bu görseller hem ~484px'lik bento hücresinde hem de
          ~654px'lik sayfa hero'sunda AYNI JSX'ten render ediliyor. Viewport
          breakpoint'i "pencere genişse" der, "ben genişsem" diyemez — 78px'lik
          kartların sebebi buydu. İç düzenler artık @{boy}/stage: ile sürülüyor.
          Container ölçeği breakpoint ölçeği DEĞİL: @sm=384 @md=448 @lg=512
          @xl=576 @2xl=672 @3xl=768 @4xl=896px. */}
      <div className="@container/stage min-h-0 flex-1 [&>*]:h-full">{children}</div>
      <figcaption className="shrink-0 border-t bg-muted/25 px-5 py-4">
        <p className="text-sm font-semibold">{title}</p>
        <p className="mt-1 max-w-3xl text-xs leading-5 text-muted-foreground">{body}</p>
      </figcaption>
    </figure>
  );
}

const GraphNode = forwardRef<
  HTMLDivElement,
  { label: string; detail: string; featured?: boolean }
>(function GraphNode({ label, detail, featured = false }, ref) {
  return (
    <div className="relative z-10 h-full" ref={ref}>
      <MagicCard className={`h-full rounded-lg p-4 ${featured ? "border-brand/50 bg-brand/10 shadow-md" : ""}`} tilt={false}>
        <p className="font-mono text-micro tracking-[0.06em] text-muted-foreground">{detail}</p>
        <p className="mt-1 text-sm font-semibold">{label}</p>
      </MagicCard>
    </div>
  );
});

export function SemanticMapVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  const containerRef = useRef<HTMLDivElement>(null);
  const crmRef = useRef<HTMLDivElement>(null);
  const erpRef = useRef<HTMLDivElement>(null);
  const modelRef = useRef<HTMLDivElement>(null);
  const metricRef = useRef<HTMLDivElement>(null);
  const reportRef = useRef<HTMLDivElement>(null);
  return (
    <VisualFrame title={t.semanticTitle} body={t.semanticBody}>
      <div
        className="marketing-grid relative grid gap-6 p-5 @3xl/stage:grid-cols-[1fr_1.15fr_1fr] @3xl/stage:gap-10 @3xl/stage:p-8"
        ref={containerRef}
      >
        <div className="relative z-10 grid grid-cols-2 gap-4 @3xl/stage:grid-cols-1 @3xl/stage:grid-rows-2">
          <GraphNode label="CRM" detail={t.customerSource} ref={crmRef} />
          <GraphNode label="ERP" detail={t.commercialSource} ref={erpRef} />
        </div>
        <div className="relative z-10 rounded-xl border border-brand/50 bg-background p-5 text-center shadow-xl @3xl/stage:self-center" ref={modelRef}>
          <Network className="mx-auto size-6 text-brand" aria-hidden="true" />
          <p className="mt-3 font-mono text-micro text-brand">{t.model}</p>
          <p className="mt-2 font-semibold">{t.concepts}</p>
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {(locale === "tr" ? ["gelir", "kâr", "aktif müşteri"] : ["revenue", "margin", "active customer"]).map((item) => <span className="rounded-full border px-2 py-1 font-mono text-micro" key={item}>{item}</span>)}
          </div>
        </div>
        <div className="relative z-10 grid grid-cols-2 gap-4 @3xl/stage:grid-cols-1 @3xl/stage:grid-rows-2">
          <GraphNode label={locale === "tr" ? "Gösterge" : "Metric"} detail={t.metricSurface} ref={metricRef} />
          <GraphNode label={locale === "tr" ? "Rapor" : "Report"} detail={t.evidenceSurface} ref={reportRef} />
        </div>
        {/* Beam'ler ref'ler arası geometrik: yalnızca 3 sütunlu düzende anlamlı. */}
        <AnimatedBeam className="hidden @3xl/stage:block" containerRef={containerRef} fromRef={crmRef} toRef={modelRef} curvature={30} duration={4.1} />
        <AnimatedBeam className="hidden @3xl/stage:block" containerRef={containerRef} fromRef={erpRef} toRef={modelRef} curvature={-30} duration={4.5} delay={0.35} />
        <AnimatedBeam className="hidden @3xl/stage:block" containerRef={containerRef} fromRef={modelRef} toRef={metricRef} curvature={-30} reverse duration={4.2} delay={0.2} />
        <AnimatedBeam className="hidden @3xl/stage:block" containerRef={containerRef} fromRef={modelRef} toRef={reportRef} curvature={30} reverse duration={4.6} delay={0.55} />
      </div>
    </VisualFrame>
  );
}

export function SecurityFlowVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  const icons = [KeyRound, Fingerprint, LockKeyhole, ShieldCheck];
  const gates = t.securityGates.map(([label, state], index) => ({ icon: icons[index], label, state }));
  return (
    <VisualFrame title={t.securityTitle} body={t.securityBody}>
      <div className="relative p-5 @2xl/stage:p-8">
        {/* Yatay ray yalnızca 4'lü satır düzeninde var. */}
        <div aria-hidden="true" className="absolute left-10 right-10 top-1/2 hidden h-px bg-border @3xl/stage:block" />
        <AnimatedList className="relative grid gap-3 @xs/stage:grid-cols-2 @3xl/stage:grid-cols-4">
          {gates.map((gate, index) => {
            const Icon = gate.icon;
            return (
              <MagicCard className="relative rounded-lg p-4 shadow-sm" key={gate.label} tilt={false}>
                <TileBody
                  top={
                    <>
                      <Icon className="size-4 shrink-0 text-brand" aria-hidden="true" />
                      <span className="whitespace-nowrap font-mono text-micro text-foreground">0{index + 1} · {locale === "tr" ? "TAMAM" : "PASS"}</span>
                    </>
                  }
                >
                  <p className="text-sm font-semibold">{gate.label}</p>
                  <p className="mt-1 font-mono text-micro text-muted-foreground">{gate.state}</p>
                </TileBody>
              </MagicCard>
            );
          })}
        </AnimatedList>
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t pt-5 text-xs text-muted-foreground">
          <span>{t.requestStart}</span><span className="text-brand">{t.requestEnd}</span>
        </div>
      </div>
    </VisualFrame>
  );
}

const BeamNode = forwardRef<
  HTMLDivElement,
  { children: React.ReactNode; className?: string }
>(function BeamNode({ children, className }, ref) {
  return (
    <div
      className={`relative z-10 rounded-lg border bg-card shadow-sm ${className ?? ""}`}
      ref={ref}
    >
      {children}
    </div>
  );
});

export function IntegrationFlowVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  const containerRef = useRef<HTMLDivElement>(null);
  const postgresRef = useRef<HTMLDivElement>(null);
  const duckRef = useRef<HTMLDivElement>(null);
  const plannedRef = useRef<HTMLDivElement>(null);
  const modelRef = useRef<HTMLDivElement>(null);
  const outputRef = useRef<HTMLDivElement>(null);
  return (
    <VisualFrame title={t.integrationTitle} body={t.integrationBody}>
      <div className="relative grid gap-px overflow-hidden bg-border @2xl/stage:grid-cols-[1fr_1.15fr_1fr]" ref={containerRef}>
        <div className="relative z-10 bg-background p-5 @2xl/stage:p-6">
          <p className="font-mono text-micro uppercase tracking-wider text-muted-foreground">{t.sources}</p>
          <div className="mt-6 space-y-3">
            {/* min-w-0 + shrink-0: "MSSQL / Oracle" ile "Dima'da doğrulandı"
                aynı satırda yer için çekişiyor; etiket sarmalı, durum sarmamalı. */}
            <BeamNode className="flex items-center justify-between gap-2 px-3 py-3" ref={postgresRef}>
              <span className="flex min-w-0 items-center gap-2 text-xs font-medium"><Database className="size-3.5 shrink-0 text-brand" />Postgres</span>
              <span className="shrink-0 font-mono text-micro text-foreground">{t.available}</span>
            </BeamNode>
            <BeamNode className="flex items-center justify-between gap-2 px-3 py-3" ref={duckRef}>
              <span className="flex min-w-0 items-center gap-2 text-xs font-medium"><Database className="size-3.5 shrink-0 text-brand" />DuckDB</span>
              <span className="shrink-0 font-mono text-micro text-foreground">{t.available}</span>
            </BeamNode>
            <BeamNode className="flex items-center justify-between gap-2 px-3 py-3" ref={plannedRef}>
              <span className="flex min-w-0 items-center gap-2 text-xs font-medium"><Database className="size-3.5 shrink-0 text-brand" />MSSQL / Oracle</span>
              <span className="shrink-0 font-mono text-micro text-muted-foreground">{t.planned}</span>
            </BeamNode>
          </div>
        </div>
        <div className="marketing-grid relative z-10 flex items-center justify-center bg-background p-6">
          <BeamNode className="w-full max-w-52 border-brand/50 p-5 text-center shadow-xl" ref={modelRef}>
            <div aria-hidden="true" className="visual-ring absolute -inset-3 rounded-2xl border border-dashed border-brand/25" />
            <Braces className="mx-auto size-6 text-brand" aria-hidden="true" />
            <p className="mt-3 text-sm font-semibold">{t.model}</p>
            <p className="mt-1 font-mono text-micro text-muted-foreground">{locale === "tr" ? "tablolar → ilişkiler → ölçüler" : "tables → relationships → metrics"}</p>
          </BeamNode>
        </div>
        <div className="relative z-10 bg-background p-5 @2xl/stage:p-6">
          <p className="font-mono text-micro uppercase tracking-wider text-muted-foreground">{t.consumers}</p>
          <BeamNode className="mt-6 grid grid-cols-2 gap-3 p-4" ref={outputRef}>
            {[Table2, CircleGauge, GitBranch, FileCode2].map((Icon, index) => (
              <div className="flex aspect-square flex-col justify-between rounded-md border bg-background p-4" key={index}>
                <Icon className="size-4 shrink-0 text-brand" aria-hidden="true" />
                <span className="font-mono text-micro text-muted-foreground">0{index + 1}</span>
              </div>
            ))}
          </BeamNode>
        </div>
        <AnimatedBeam containerRef={containerRef} fromRef={postgresRef} toRef={modelRef} curvature={36} duration={3.6} />
        <AnimatedBeam containerRef={containerRef} fromRef={duckRef} toRef={modelRef} duration={4.2} delay={0.5} />
        <AnimatedBeam containerRef={containerRef} fromRef={plannedRef} toRef={modelRef} curvature={-36} duration={4.8} delay={1} />
        <AnimatedBeam containerRef={containerRef} fromRef={modelRef} toRef={outputRef} reverse duration={3.8} delay={0.2} />
      </div>
    </VisualFrame>
  );
}

export function WorkflowPipeline({ items }: { items: Array<{ title: string; body: string }> }) {
  return (
    <div className="relative mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <div aria-hidden="true" className="visual-scan absolute inset-y-0 left-0 z-20 hidden w-px bg-brand lg:block" />
      {items.map((item, index) => (
        <MagicCard key={item.title}>
          <article className="relative h-full p-6">
            <TileBody
              className="gap-10"
              top={
                <>
                  <span className="flex size-8 shrink-0 items-center justify-center rounded-full border font-mono text-micro text-brand">0{index + 1}</span>
                  <span aria-hidden="true" className="mt-4 h-px w-16 shrink-0 origin-right scale-x-[0.625] bg-brand/35 transition-[transform,background-color] duration-300 group-focus-within:scale-x-100 group-focus-within:bg-brand" />
                </>
              }
            >
              <h3 className="text-xl font-semibold">{item.title}</h3>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.body}</p>
            </TileBody>
            <div aria-hidden="true" className="absolute bottom-0 left-0 h-1 bg-brand/70" style={{ width: `${42 + index * 17}%` }} />
          </article>
        </MagicCard>
      ))}
    </div>
  );
}

export function MiniSignal({ index }: { index: number }) {
  const paths = [
    "M2 26 18 20 34 23 50 10 66 15 82 5 98 9",
    "M2 12 18 18 34 8 50 22 66 17 82 25 98 14",
    "M2 24 18 24 34 19 50 18 66 12 82 10 98 4",
  ];
  if (index === 1) {
    return (
      <svg aria-hidden="true" className="mt-7 h-9 w-full text-brand/70" viewBox="0 0 100 30" preserveAspectRatio="none">
        {[12, 26, 43, 61, 78].map((x, i) => <rect fill="currentColor" height={6 + i * 4} key={x} opacity={0.22 + i * 0.1} width="9" x={x} y={24 - i * 4} />)}
        <path d="M0 8h100" stroke="currentColor" strokeDasharray="3 4" strokeOpacity=".45" />
      </svg>
    );
  }
  if (index === 3) {
    return (
      <svg aria-hidden="true" className="mt-7 h-9 w-full text-brand/70" viewBox="0 0 100 30" preserveAspectRatio="none">
        {Array.from({ length: 12 }, (_, i) => <rect fill="currentColor" height="7" key={i} opacity={i % 5 === 0 ? ".65" : i % 3 === 0 ? ".32" : ".12"} width="7" x={(i % 6) * 16 + 2} y={Math.floor(i / 6) * 13 + 2} />)}
      </svg>
    );
  }
  if (index === 4) {
    return (
      <svg aria-hidden="true" className="mt-7 h-9 w-full text-brand/70" viewBox="0 0 100 30" preserveAspectRatio="none">
        <rect fill="currentColor" height="8" opacity=".12" width="100" y="11" /><rect fill="currentColor" height="8" opacity=".55" width="28" y="11" />
        <path d="M35 4v22" stroke="currentColor" strokeDasharray="2 3" />
      </svg>
    );
  }
  return (
    <svg aria-hidden="true" className="mt-7 h-9 w-full text-brand/70" fill="none" preserveAspectRatio="none" viewBox="0 0 100 30">
      <path d="M0 29h100" stroke="currentColor" strokeOpacity=".18" />
      <path d={paths[index % paths.length]} stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

export function ProductWorkbenchVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  return (
    <VisualFrame title={t.workbenchTitle} body={t.workbenchBody}>
      <div className="grid bg-muted/20 @2xl/stage:grid-cols-[10rem_1fr]">
        <div className="hidden border-r bg-background p-4 @2xl/stage:block">
          <div className="h-8 rounded-md border bg-card" />
          <div className="mt-8 space-y-2">{t.workbenchNav.map((item, index) => <div className={`rounded-md px-3 py-2 text-micro ${index === 0 ? "border-l-2 border-brand bg-brand/10 text-foreground" : "text-muted-foreground"}`} key={item}>{item}</div>)}</div>
        </div>
        {/* İç içe container: bu panel sahneden 160px dar, kendi eşiğine ihtiyacı var. */}
        <div className="@container/pane p-5 @2xl/stage:p-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="min-w-0"><p className="font-mono text-micro text-muted-foreground">{locale === "tr" ? "örnek veri / bu vardiya" : "sample data / this shift"}</p><p className="mt-1 text-lg font-semibold">{t.productPerformance}</p></div>
            <span className="shrink-0 whitespace-nowrap rounded-full border border-chart-2/40 bg-chart-2/10 px-3 py-1 font-mono text-micro text-foreground"><Check className="mr-1 inline size-3 text-chart-2" />{t.verified}</span>
          </div>
          <div className="mt-7 grid gap-4 @sm/pane:grid-cols-3">
            {[
              { value: 82, suffix: "%", decimals: 0, label: t.grossMargin },
              { value: 3, suffix: "", decimals: 0, label: t.productGroups },
              { value: 3.4, suffix: "%", decimals: 1, label: t.belowTarget },
            ].map((item) => (
              <MagicCard className="rounded-lg p-4" key={item.label} tilt={false}>
                <p className="font-display text-3xl tabular-nums">
                  <NumberTicker decimals={item.decimals} locale={locale === "tr" ? "tr-TR" : "en-US"} value={item.value} />
                  {item.suffix}
                </p>
                <p className="mt-2 text-xs text-muted-foreground">{item.label}</p>
              </MagicCard>
            ))}
          </div>
          <div className="mt-4 rounded-lg border bg-card p-5">
            <div className="flex h-32 items-end gap-3">
              {[72, 48, 86, 61, 93, 67, 78].map((height, index) => (
                <div className="relative flex h-full flex-1 items-end" key={index}>
                  <div
                    className="marketing-bar-rise w-full rounded-t-sm bg-brand/30"
                    style={{ height: `${height}%`, "--bar-delay": `${index * 0.06}s` } as React.CSSProperties}
                  />
                </div>
              ))}
            </div>
            <div className="mt-3 flex justify-between gap-2 font-mono text-micro text-muted-foreground"><span>{t.periodStart}</span><span>{t.current}</span></div>
          </div>
        </div>
      </div>
    </VisualFrame>
  );
}

export function ValidationPipelineVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  const steps = t.validationSteps;
  return (
    <VisualFrame title={t.validationTitle} body={t.validationBody}>
      <div className="marketing-grid p-5 @2xl/stage:p-8">
        {/* 5 sütun aritmetiği: 5×144px min kart + 4×12px boşluk + 64px padding = 832px
            → ilk dürüst eşik @4xl (896px). Altında 3'lü, daha altında 2'li düzene düşer;
            eskiden lg:grid-cols-5 dar hücrede 78px'lik kartlar üretiyordu. */}
        <AnimatedList className="grid w-full grid-cols-1 gap-3 @xs/stage:grid-cols-2 @xs/stage:[&>*:last-child]:col-span-2 @xl/stage:grid-cols-3 @xl/stage:[&>*:last-child]:col-span-1 @4xl/stage:grid-cols-5">
          {steps.map(([title, detail], index) => (
            <MagicCard className={`relative rounded-lg p-4 ${index === 0 ? "border-dashed bg-muted/40" : ""}`} key={title} tilt={false}>
              <TileBody
                top={
                  <>
                    <span className="font-mono text-micro text-brand">0{index + 1}</span>
                    {index > 0 ? <Check className="size-3 shrink-0 text-chart-2" aria-hidden="true" /> : null}
                  </>
                }
              >
                <p className="text-sm font-semibold">{title}</p>
                <p className="mt-1 font-mono text-xs text-muted-foreground">{detail}</p>
              </TileBody>
            </MagicCard>
          ))}
        </AnimatedList>
      </div>
    </VisualFrame>
  );
}

export function PageVisualStage({ variant, locale }: LocaleProps & { variant: "product" | "validation" | "security" | "integration" }) {
  return (
    <div className="min-w-0">
      {variant === "product" ? <ProductWorkbenchVisual locale={locale} /> : null}
      {variant === "validation" ? <ValidationPipelineVisual locale={locale} /> : null}
      {variant === "security" ? <SecurityFlowVisual locale={locale} /> : null}
      {variant === "integration" ? <IntegrationFlowVisual locale={locale} /> : null}
    </div>
  );
}
