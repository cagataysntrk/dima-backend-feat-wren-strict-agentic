import {
  Braces,
  Check,
  CircleGauge,
  Database,
  FileCode2,
  Fingerprint,
  GitBranch,
  KeyRound,
  Layers3,
  LockKeyhole,
  Network,
  ShieldCheck,
  Sparkles,
  Table2,
} from "lucide-react";
import { PILLARS } from "@/components/BrandMark";
import type { MarketingLocale } from "@/content/marketing";

type LocaleProps = { locale: MarketingLocale };

const labels = {
  tr: {
    synthetic: "Sentetik ürün görselleştirmesi",
    signalTitle: "Bir soru, dört görünür karar noktası",
    signalBody: "İş sorusu önce onaylı tanımlarla eşleşir; sorgu ancak guard ve dry-plan adımlarından sonra rapora dönüşür.",
    question: "Hangi ürün grupları hedefin altında?",
    context: "gross_margin · product_group · quarter",
    query: "SELECT · read-only",
    report: "Tablo · grafik · çözüm izi",
    semanticTitle: "Ortak tanımlar üzerinde bağlı operasyon",
    semanticBody: "Kaynak sistemler tablo isimleriyle değil; müşteri, ürün, gelir ve dönem gibi onaylı iş kavramlarıyla bağlanır.",
    securityTitle: "Her istek aynı güven zincirinden geçer",
    securityBody: "Oturum, tenant, permission ve query guard kontrolleri analitik hızlandığında ortadan kalkmaz.",
    integrationTitle: "Kaynaklardan rapora kontrollü onboarding",
    integrationBody: "Bağlantı desteği ile canlı kullanım doğrulaması ayrı durumlar olarak gösterilir.",
    workbenchTitle: "Aynı kanıt, farklı inceleme yüzeyleri",
    workbenchBody: "Sonuç, görselleştirme, SQL ve provenance tek analitik çalışma alanında kalır.",
    validationTitle: "LLM çıktısı doğrudan çalıştırılmaz",
    validationBody: "Öneri; semantic eşleşme, read-only guard ve dry-plan kararlarından geçmeden veri kaynağına ulaşmaz.",
    sources: "Kaynaklar",
    model: "Semantic model",
    consumers: "Analitik yüzeyler",
    available: "doğrulandı",
    planned: "ayrı doğrulama",
    verified: "doğrulandı",
    liveModel: "model görünümü",
    concepts: "Müşteri × Ürün × Dönem",
    customerSource: "müşteri kaynağı",
    commercialSource: "ticari kaynak",
    metricSurface: "metrik yüzeyi",
    evidenceSurface: "kanıt yüzeyi",
    securityGates: [["Oturum", "HTTP-only yenileme"], ["Tenant", "kapsamlı bağlam"], ["Yetki", "backend doğrulaması"], ["Sorgu guard", "SELECT / WITH"]],
    requestStart: "Kullanıcı → same-origin API",
    requestEnd: "doğrulanmış istek → semantic engine",
    productPerformance: "Ürün performansı",
    grossMargin: "Brüt kâr",
    productGroups: "Ürün grubu",
    belowTarget: "Hedef altında",
    periodStart: "Çeyrek başlangıcı",
    current: "güncel",
    validationSteps: [["LLM önerisi", "aday SQL"], ["Semantic eşleşme", "metrik + boyut"], ["Read-only guard", "SELECT / WITH"], ["Dry-plan", "motor doğrulaması"], ["Çalıştırma", "yetki kapsamında"]],
    workbenchNav: ["Konuşma", "Katalog", "Sözleşmeler", "Raporlar"],
  },
  en: {
    synthetic: "Synthetic product visualization",
    signalTitle: "One question, four visible decision points",
    signalBody: "A business question first matches approved definitions; only then do guard and dry-plan decisions produce a report.",
    question: "Which product groups are below target?",
    context: "gross_margin · product_group · quarter",
    query: "SELECT · read-only",
    report: "Table · chart · resolution trace",
    semanticTitle: "Connected operations over shared definitions",
    semanticBody: "Source systems connect through approved concepts such as customer, product, revenue, and period—not only table names.",
    securityTitle: "Every request follows the same trust chain",
    securityBody: "Session, tenant, permission, and query guards do not disappear when analytics gets faster.",
    integrationTitle: "Controlled onboarding from sources to reports",
    integrationBody: "Connector capability and live-use validation are shown as separate states.",
    workbenchTitle: "The same evidence across multiple inspection surfaces",
    workbenchBody: "Results, visualization, SQL, and provenance stay within one analytical workbench.",
    validationTitle: "LLM output is never executed directly",
    validationBody: "A proposal cannot reach the data source before semantic matching, read-only guards, and dry-plan decisions.",
    sources: "Sources",
    model: "Semantic model",
    consumers: "Analytical surfaces",
    available: "validated",
    planned: "separate validation",
    verified: "verified",
    liveModel: "model view",
    concepts: "Customer × Product × Period",
    customerSource: "customer source",
    commercialSource: "commercial source",
    metricSurface: "metric surface",
    evidenceSurface: "evidence surface",
    securityGates: [["Session", "HTTP-only refresh"], ["Tenant", "scoped context"], ["Permission", "backend-authorized"], ["Query guard", "SELECT / WITH"]],
    requestStart: "User → same-origin API",
    requestEnd: "validated request → semantic engine",
    productPerformance: "Product performance",
    grossMargin: "Gross margin",
    productGroups: "Product groups",
    belowTarget: "Below target",
    periodStart: "Quarter start",
    current: "current",
    validationSteps: [["LLM proposal", "candidate SQL"], ["Semantic match", "metric + dimension"], ["Read-only guard", "SELECT / WITH"], ["Dry plan", "engine validated"], ["Execution", "permission scoped"]],
    workbenchNav: ["Conversation", "Catalog", "Contracts", "Reports"],
  },
} as const;

function VisualFrame({
  eyebrow,
  title,
  body,
  children,
  statusLabel,
  className = "",
}: {
  eyebrow: string;
  title: string;
  body: string;
  children: React.ReactNode;
  statusLabel: string;
  className?: string;
}) {
  return (
    <figure className={`overflow-hidden rounded-xl border bg-card shadow-lg ${className}`}>
      <div className="flex items-center justify-between gap-4 border-b px-5 py-3">
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">{eyebrow}</span>
        <span className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.14em] text-foreground">
          <span className="visual-pulse size-1.5 rounded-full bg-chart-2" />
          {statusLabel}
        </span>
      </div>
      {children}
      <figcaption className="border-t bg-muted/25 px-5 py-4">
        <p className="text-sm font-semibold">{title}</p>
        <p className="mt-1 max-w-3xl text-xs leading-5 text-muted-foreground">{body}</p>
      </figcaption>
    </figure>
  );
}

export function AnalyticalSignalMap({ locale }: LocaleProps) {
  const t = labels[locale];
  const stages = [
    { icon: Sparkles, label: t.question, code: "01 / ask" },
    { icon: Layers3, label: t.context, code: "02 / model" },
    { icon: ShieldCheck, label: t.query, code: "03 / validate" },
    { icon: CircleGauge, label: t.report, code: "04 / inspect" },
  ];
  return (
    <VisualFrame eyebrow={t.synthetic} title={t.signalTitle} body={t.signalBody} statusLabel={t.liveModel} className="mt-10 sm:mt-14">
      <div className="relative grid gap-px bg-border lg:grid-cols-4">
        <div aria-hidden="true" className="visual-scan absolute inset-y-0 left-0 z-10 hidden w-px bg-brand shadow-[0_0_20px_var(--brand)] lg:block" />
        {stages.map((stage, index) => {
          const Icon = stage.icon;
          return (
            <div className="relative min-h-36 bg-background p-5 sm:p-6" key={stage.code}>
              <div className="flex items-start justify-between">
                <span className="flex size-10 items-center justify-center rounded-full border bg-card text-brand"><Icon className="size-4" aria-hidden="true" /></span>
                <span className="font-mono text-[10px] text-muted-foreground">{stage.code}</span>
              </div>
              <p className="mt-7 max-w-52 text-sm font-medium leading-6">{stage.label}</p>
              {index < stages.length - 1 ? <span aria-hidden="true" className="absolute -right-1 top-1/2 z-20 hidden size-2 rounded-full bg-brand ring-4 ring-background lg:block" /> : null}
            </div>
          );
        })}
      </div>
    </VisualFrame>
  );
}

function GraphNode({ label, detail, featured = false }: { label: string; detail: string; featured?: boolean }) {
  return (
    <div className={`relative z-10 rounded-lg border p-3 ${featured ? "border-brand/50 bg-brand/10 shadow-md" : "bg-card"}`}>
      <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{detail}</p>
      <p className="mt-1 text-sm font-semibold">{label}</p>
    </div>
  );
}

export function SemanticMapVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  return (
    <VisualFrame eyebrow="semantic graph / 01" title={t.semanticTitle} body={t.semanticBody} statusLabel={t.liveModel}>
      <div className="marketing-grid relative grid min-h-80 gap-8 p-6 sm:grid-cols-[1fr_1.1fr_1fr] sm:items-center sm:p-8">
        <svg aria-hidden="true" className="pointer-events-none absolute inset-0 hidden size-full text-brand/35 sm:block" viewBox="0 0 720 320" preserveAspectRatio="none">
          <path className="visual-dash" d="M150 72 C245 72 230 160 340 160 M150 248 C245 248 230 160 340 160 M380 160 C490 160 475 74 570 74 M380 160 C490 160 475 246 570 246" fill="none" stroke="currentColor" strokeDasharray="5 8" />
        </svg>
        <div className="space-y-4">
          <GraphNode label="CRM" detail={t.customerSource} />
          <GraphNode label="ERP" detail={t.commercialSource} />
        </div>
        <div className="rounded-xl border border-brand/50 bg-background p-5 text-center shadow-xl">
          <Network className="mx-auto size-6 text-brand" aria-hidden="true" />
          <p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-brand">{t.model}</p>
          <p className="mt-2 font-semibold">{t.concepts}</p>
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {["revenue", "margin", "active_customer"].map((item) => <span className="rounded-full border px-2 py-1 font-mono text-[9px]" key={item}>{item}</span>)}
          </div>
        </div>
        <div className="space-y-4">
          <GraphNode label="KPI" detail={t.metricSurface} />
          <GraphNode label={locale === "tr" ? "Rapor" : "Report"} detail={t.evidenceSurface} />
        </div>
      </div>
    </VisualFrame>
  );
}

export function SecurityFlowVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  const icons = [KeyRound, Fingerprint, LockKeyhole, ShieldCheck];
  const gates = t.securityGates.map(([label, state], index) => ({ icon: icons[index], label, state }));
  return (
    <VisualFrame eyebrow="trust topology / 02" title={t.securityTitle} body={t.securityBody} statusLabel={t.liveModel}>
      <div className="relative min-h-80 p-6 sm:p-8">
        <div aria-hidden="true" className="absolute left-10 right-10 top-1/2 hidden h-px bg-border sm:block" />
        <div className="relative grid gap-3 sm:grid-cols-4 sm:items-center">
          {gates.map((gate, index) => {
            const Icon = gate.icon;
            return (
              <div className="group relative rounded-lg border bg-background p-4 shadow-sm transition-transform hover:-translate-y-1" key={gate.label}>
                <div className="flex items-center justify-between">
                  <Icon className="size-4 text-brand" aria-hidden="true" />
                  <span className="font-mono text-[9px] text-foreground">0{index + 1} PASS</span>
                </div>
                <p className="mt-7 text-sm font-semibold">{gate.label}</p>
                <p className="mt-1 font-mono text-[9px] text-muted-foreground">{gate.state}</p>
              </div>
            );
          })}
        </div>
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t pt-5 text-xs text-muted-foreground">
          <span>{t.requestStart}</span><span className="text-brand">{t.requestEnd}</span>
        </div>
      </div>
    </VisualFrame>
  );
}

export function IntegrationFlowVisual({ locale }: LocaleProps) {
  const t = labels[locale];
  return (
    <VisualFrame eyebrow="source map / 03" title={t.integrationTitle} body={t.integrationBody} statusLabel={t.liveModel}>
      <div className="grid min-h-80 gap-px bg-border sm:grid-cols-[1fr_1.15fr_1fr]">
        <div className="bg-background p-5 sm:p-6">
          <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{t.sources}</p>
          <div className="mt-6 space-y-3">
            {[["Postgres", t.available], ["DuckDB", t.available], ["MSSQL / Oracle", t.planned]].map(([name, state]) => (
              <div className="flex items-center justify-between rounded-md border bg-card px-3 py-3" key={name}>
                <span className="flex items-center gap-2 text-xs font-medium"><Database className="size-3.5 text-brand" />{name}</span>
                <span className="font-mono text-[8px] uppercase text-foreground">{state}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="marketing-grid flex items-center justify-center bg-background p-6">
          <div className="relative w-full max-w-52 rounded-xl border border-brand/50 bg-card p-5 text-center shadow-xl">
            <div aria-hidden="true" className="visual-ring absolute -inset-3 rounded-2xl border border-dashed border-brand/25" />
            <Braces className="mx-auto size-6 text-brand" aria-hidden="true" />
            <p className="mt-3 text-sm font-semibold">{t.model}</p>
            <p className="mt-1 font-mono text-[9px] text-muted-foreground">schema → relations → metrics</p>
          </div>
        </div>
        <div className="bg-background p-5 sm:p-6">
          <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{t.consumers}</p>
          <div className="mt-6 grid grid-cols-2 gap-3">
            {[Table2, CircleGauge, GitBranch, FileCode2].map((Icon, index) => (
              <div className="flex aspect-square flex-col justify-between rounded-md border bg-card p-3" key={index}>
                <Icon className="size-4 text-brand" aria-hidden="true" />
                <span className="font-mono text-[9px] text-muted-foreground">0{index + 1}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </VisualFrame>
  );
}

export function MechanismPillars({ locale }: LocaleProps) {
  const motifs = [
    <path d="M5 15h14M8 11h8M11 7h2" key="d" />,
    <><circle cx="12" cy="12" r="6" key="i1" /><path d="M12 8v4l3 2" key="i2" /></>,
    <><path d="M5 8l7-4 7 4-7 4-7-4Z" key="m1" /><path d="m5 12 7 4 7-4M5 16l7 4 7-4" key="m2" /></>,
    <><path d="M5 18 12 5l7 13" key="a1" /><circle cx="12" cy="14" r="2" key="a2" /></>,
  ];
  return (
    <div className="grid gap-px overflow-hidden rounded-lg border bg-border sm:grid-cols-2 lg:grid-cols-4">
      {PILLARS.map((pillar, index) => (
        <article className="group bg-background p-6 transition-colors hover:bg-muted/30" key={pillar.letter}>
          <div className="flex items-start justify-between">
            <span className="font-display text-5xl text-muted-foreground/45">{pillar.letter}</span>
            <svg aria-hidden="true" className="size-10 text-brand" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24">{motifs[index]}</svg>
          </div>
          <p className="mt-10 font-mono text-[10px] uppercase tracking-[0.16em]"><span className="mr-2 text-brand">0{index + 1}</span>{pillar.word}</p>
          <p className="mt-3 text-xs leading-5 text-muted-foreground">{pillar[locale]}</p>
        </article>
      ))}
    </div>
  );
}

export function WorkflowPipeline({ items }: { items: Array<{ title: string; body: string }> }) {
  return (
    <div className="relative mt-12 grid gap-px overflow-hidden rounded-lg border bg-border md:grid-cols-2 lg:grid-cols-4">
      <div aria-hidden="true" className="visual-scan absolute inset-y-0 left-0 z-20 hidden w-px bg-brand lg:block" />
      {items.map((item, index) => (
        <article className="relative min-h-64 bg-background p-6 sm:p-8" key={item.title}>
          <div className="flex items-center justify-between">
            <span className="flex size-8 items-center justify-center rounded-full border font-mono text-[10px] text-brand">0{index + 1}</span>
            <span aria-hidden="true" className="h-px w-10 bg-brand/35" />
          </div>
          <h3 className="mt-16 text-xl font-semibold">{item.title}</h3>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.body}</p>
          <div aria-hidden="true" className="absolute bottom-0 left-0 h-1 bg-brand/70" style={{ width: `${42 + index * 17}%` }} />
        </article>
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
    <VisualFrame eyebrow={`${t.synthetic} / workbench`} title={t.workbenchTitle} body={t.workbenchBody} statusLabel={t.liveModel}>
      <div className="grid min-h-96 bg-muted/20 lg:grid-cols-[180px_1fr]">
        <div className="hidden border-r bg-background p-4 lg:block">
          <div className="h-8 rounded-md border bg-card" />
          <div className="mt-8 space-y-2">{t.workbenchNav.map((item, index) => <div className={`rounded-md px-3 py-2 text-[10px] ${index === 0 ? "border-l-2 border-brand bg-brand/10 text-foreground" : "text-muted-foreground"}`} key={item}>{item}</div>)}</div>
        </div>
        <div className="p-5 sm:p-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div><p className="font-mono text-[9px] uppercase text-muted-foreground">gross_margin / quarter</p><p className="mt-1 text-lg font-semibold">{t.productPerformance}</p></div>
            <span className="rounded-full border border-chart-2/40 bg-chart-2/10 px-3 py-1 font-mono text-[9px] text-foreground"><Check className="mr-1 inline size-3 text-chart-2" />{t.verified}</span>
          </div>
          <div className="mt-7 grid gap-4 sm:grid-cols-3">
            {[["31.4%", t.grossMargin], ["12", t.productGroups], ["3", t.belowTarget]].map(([value, label]) => <div className="rounded-lg border bg-card p-4" key={label}><p className="font-display text-3xl">{value}</p><p className="mt-2 text-[10px] text-muted-foreground">{label}</p></div>)}
          </div>
          <div className="mt-4 rounded-lg border bg-card p-5">
            <div className="flex h-32 items-end gap-3">
              {[72, 48, 86, 61, 93, 67, 78].map((height, index) => <div className="group relative flex h-full flex-1 items-end" key={index}><div className="w-full rounded-t-sm bg-brand/20 transition-colors group-hover:bg-brand/60" style={{ height: `${height}%` }} /></div>)}
            </div>
            <div className="mt-3 flex justify-between font-mono text-[8px] text-muted-foreground"><span>{t.periodStart}</span><span>{t.current}</span></div>
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
    <VisualFrame eyebrow="deterministic resolution" title={t.validationTitle} body={t.validationBody} statusLabel={t.liveModel}>
      <div className="marketing-grid p-6 sm:p-8">
        <div className="grid gap-3 lg:grid-cols-5">
          {steps.map(([title, detail], index) => (
            <div className={`relative rounded-lg border p-4 ${index === 0 ? "border-dashed bg-muted/40" : "bg-card"}`} key={title}>
              <span className="font-mono text-[9px] text-brand">0{index + 1}</span>
              <p className="mt-8 text-sm font-semibold">{title}</p>
              <p className="mt-1 font-mono text-[8px] text-muted-foreground">{detail}</p>
              {index > 0 ? <Check className="absolute right-3 top-3 size-3 text-chart-2" aria-hidden="true" /> : null}
            </div>
          ))}
        </div>
      </div>
    </VisualFrame>
  );
}

export function PageVisualStage({ variant, locale }: LocaleProps & { variant: "product" | "validation" | "security" | "integration" }) {
  return (
    <div className="mx-auto max-w-7xl px-5 pt-12 sm:px-8 sm:pt-16">
      {variant === "product" ? <ProductWorkbenchVisual locale={locale} /> : null}
      {variant === "validation" ? <ValidationPipelineVisual locale={locale} /> : null}
      {variant === "security" ? <SecurityFlowVisual locale={locale} /> : null}
      {variant === "integration" ? <IntegrationFlowVisual locale={locale} /> : null}
    </div>
  );
}
