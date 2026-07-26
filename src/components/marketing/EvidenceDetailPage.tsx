import {
  ArrowDown,
  BarChart3,
  Braces,
  Check,
  CircleGauge,
  Database,
  Fingerprint,
  KeyRound,
  Layers3,
  LockKeyhole,
  MessageSquareText,
  Network,
  RefreshCw,
  ShieldCheck,
  Table2,
  Timer,
} from "lucide-react";
import { MagicCard } from "@/components/marketing/MagicUI";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Container, FinalCta, PageHero, StatusBadge } from "@/components/marketing/MarketingPrimitives";
import type { MarketingContent, MarketingLocale, PageContent } from "@/content/marketing";

type PageKind = "product" | "how" | "solutions" | "security" | "integrations" | "about";

const ui = {
  tr: {
    synthetic: "Sentetik ürün kanıtı",
    question: "Brüt kârı hedefin altında kalan gruplar hangileri?",
    modeled: "Onaylı semantic bağlam",
    verified: "dry-plan doğrulandı",
    target: "hedef",
    current: "güncel",
    evidence: "kanıt görünümü",
  },
  en: {
    synthetic: "Synthetic product evidence",
    question: "Which groups are below gross-margin target?",
    modeled: "Approved semantic context",
    verified: "dry plan verified",
    target: "target",
    current: "current",
    evidence: "evidence view",
  },
} as const;

function EvidenceFrame({
  locale,
  code,
  children,
  summary,
}: {
  locale: MarketingLocale;
  code: string;
  children: React.ReactNode;
  summary: string;
}) {
  const t = ui[locale];
  return (
    <figure className="overflow-hidden bg-card">
      <div className="flex items-center justify-between gap-3 border-b px-4 py-3">
        <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground">{code}</span>
        <span className="flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.12em]">
          <span className="size-1.5 rounded-full bg-chart-2" aria-hidden="true" />
          {t.synthetic}
        </span>
      </div>
      <div aria-hidden="true">{children}</div>
      <figcaption className="border-t bg-muted/20 px-4 py-3 text-xs leading-5 text-muted-foreground">
        {summary}
      </figcaption>
    </figure>
  );
}

function AskVisual({ locale }: { locale: MarketingLocale }) {
  const t = ui[locale];
  return (
    <div className="space-y-3 p-4 sm:p-5">
      <div className="max-w-[88%] rounded-lg border bg-background p-4 text-sm font-medium">{t.question}</div>
      <div className="ml-auto max-w-[92%] rounded-lg border border-brand/30 bg-brand/5 p-4">
        <div className="flex items-center gap-2 font-mono text-[9px] uppercase text-brand"><Layers3 className="size-3" />{t.modeled}</div>
        <div className="mt-3 flex flex-wrap gap-2">
          {["gross_margin", "product_group", "quarter"].map((tag) => <span className="rounded-full border bg-background px-2 py-1 font-mono text-[8px]" key={tag}>{tag}</span>)}
        </div>
      </div>
      <div className="flex gap-2">
        {["↳ target", "↳ quarter", "↳ group"].map((item) => <span className="rounded-md border px-2 py-1 text-[9px] text-muted-foreground" key={item}>{item}</span>)}
      </div>
    </div>
  );
}

function SemanticVisual() {
  return (
    <div className="marketing-grid relative grid gap-4 p-5 sm:grid-cols-[1fr_1.2fr_1fr] sm:items-center">
      <div className="space-y-3">{["sales", "customers"].map((item) => <Node label={item} meta="source" key={item} />)}</div>
      <div className="rounded-xl border border-brand/40 bg-background p-5 text-center shadow-md">
        <Network className="mx-auto size-5 text-brand" />
        <p className="mt-2 text-sm font-semibold">Semantic model</p>
        <p className="mt-2 font-mono text-[8px] text-muted-foreground">measure × dimension × relation</p>
      </div>
      <div className="space-y-3">{["gross margin", "period"].map((item) => <Node label={item} meta="business term" key={item} />)}</div>
    </div>
  );
}

function Node({ label, meta }: { label: string; meta: string }) {
  return <div className="rounded-lg border bg-background p-3"><p className="font-mono text-[8px] uppercase text-muted-foreground">{meta}</p><p className="mt-1 text-xs font-semibold">{label}</p></div>;
}

function ValidationVisual({ locale }: { locale: MarketingLocale }) {
  const labels = locale === "tr"
    ? [["LLM önerisi", "aday SQL"], ["Semantic eşleşme", "metric + dimension"], ["Read-only guard", "SELECT / WITH"], ["Dry-plan", "motor doğrulaması"]]
    : [["LLM proposal", "candidate SQL"], ["Semantic match", "metric + dimension"], ["Read-only guard", "SELECT / WITH"], ["Dry plan", "engine validated"]];
  return (
    <div className="grid gap-px bg-border sm:grid-cols-2">
      {labels.map(([title, detail], index) => (
        <div className="relative min-h-28 bg-background p-4" key={title}>
          <span className="font-mono text-[9px] text-brand">0{index + 1}</span>
          {index > 0 ? <Check className="absolute right-4 top-4 size-3 text-chart-2" /> : null}
          <p className="mt-6 text-xs font-semibold">{title}</p><p className="mt-1 font-mono text-[8px] text-muted-foreground">{detail}</p>
        </div>
      ))}
    </div>
  );
}

function ExploreVisual({ locale }: { locale: MarketingLocale }) {
  const t = ui[locale];
  return (
    <div className="grid gap-px bg-border sm:grid-cols-[0.8fr_1.2fr]">
      <div className="grid grid-cols-2 gap-px bg-border">
        {[["31.4%", "margin"], ["12", "groups"], ["3", "below"], ["Q3", t.current]].map(([value, label]) => (
          <div className="bg-background p-4" key={label}><p className="font-display text-2xl">{value}</p><p className="mt-1 text-[9px] text-muted-foreground">{label}</p></div>
        ))}
      </div>
      <div className="bg-background p-5">
        <div className="flex h-32 items-end gap-2">
          {[72, 48, 86, 61, 93, 67].map((height, index) => <div className="relative flex h-full flex-1 items-end" key={index}><div className="w-full rounded-t-sm bg-brand/25" style={{ height: `${height}%` }} /></div>)}
        </div>
        <div className="mt-3 flex justify-between font-mono text-[8px] text-muted-foreground"><span>{t.target}</span><span>{t.current}</span></div>
      </div>
    </div>
  );
}

function TraceVisual({ locale }: { locale: MarketingLocale }) {
  const items = locale === "tr" ? ["ölçü eşleşti", "guard geçti", "dry-plan tamamlandı", "sonuç üretildi"] : ["measure matched", "guard passed", "dry plan completed", "result produced"];
  return <div className="p-5">{items.map((item, index) => <div className="flex gap-4 border-b py-3 last:border-0" key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-[9px] text-brand">{index + 1}</span><div><p className="text-xs font-medium">{item}</p><p className="mt-1 font-mono text-[8px] text-muted-foreground">trace/{String(index + 1).padStart(2, "0")} · PASS</p></div></div>)}</div>;
}

function ReuseVisual() {
  return <div className="grid gap-px bg-border sm:grid-cols-3">{[[RefreshCw, "Replay", "same definition"], [Timer, "Schedule", "Beta"], [CircleGauge, "Notify", "Beta"]].map(([Icon, title, meta]) => { const VisualIcon = Icon as typeof RefreshCw; return <div className="bg-background p-5" key={String(title)}><VisualIcon className="size-4 text-brand" /><p className="mt-8 text-sm font-semibold">{String(title)}</p><p className="mt-1 font-mono text-[8px] text-muted-foreground">{String(meta)}</p></div>; })}</div>;
}

function GovernVisual() {
  return <div className="grid gap-px bg-border sm:grid-cols-3">{[[Fingerprint, "session", "memory token"], [KeyRound, "permission", "backend source"], [ShieldCheck, "tenant", "scoped request"]].map(([Icon, title, meta]) => { const VisualIcon = Icon as typeof Fingerprint; return <div className="bg-background p-5" key={String(title)}><VisualIcon className="size-4 text-brand" /><p className="mt-7 text-xs font-semibold">{String(title)}</p><p className="mt-1 font-mono text-[8px] text-muted-foreground">{String(meta)}</p></div>; })}</div>;
}

function SolutionVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  if (id === "sales") return <div className="grid grid-cols-4 gap-px bg-border p-px">{Array.from({ length: 12 }, (_, i) => <span className={`aspect-square ${i % 5 === 0 ? "bg-brand/35" : i % 3 === 0 ? "bg-chart-2/25" : "bg-background"}`} key={i} />)}</div>;
  if (id === "inventory") return <div className="space-y-4 p-5">{[82, 48, 27].map((width, i) => <div key={width}><div className="mb-1 flex justify-between font-mono text-[8px]"><span>SKU-0{i + 1}</span><span>{width}%</span></div><div className="h-3 bg-muted"><div className={`h-full ${width < 30 ? "bg-destructive/70" : "bg-brand/45"}`} style={{ width: `${width}%` }} /></div></div>)}</div>;
  if (id === "data") return <GovernVisual />;
  return <ExploreVisual locale={locale} />;
}

function SecurityVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  if (id === "session") return <div className="grid gap-px bg-border sm:grid-cols-4">{[[MessageSquareText, "request"], [LockKeyhole, "401"], [RefreshCw, "refresh"], [ShieldCheck, "retry"]].map(([Icon, label], i) => { const VisualIcon = Icon as typeof MessageSquareText; return <div className="bg-background p-4" key={String(label)}><span className="font-mono text-[8px] text-brand">0{i + 1}</span><VisualIcon className="mt-8 size-4 text-brand" /><p className="mt-2 text-xs font-semibold">{String(label)}</p></div>; })}</div>;
  if (id === "flow") return <ValidationVisual locale={locale} />;
  if (id === "deployment") return <div className="grid gap-4 p-5 sm:grid-cols-2"><Node label="Cloud topology" meta="available" /><div className="rounded-lg border border-dashed p-3"><p className="font-mono text-[8px] uppercase text-muted-foreground">planned</p><p className="mt-1 text-xs font-semibold">Hybrid / thin-agent</p></div></div>;
  return <GovernVisual />;
}

function IntegrationVisual({ id }: { id: string }) {
  if (["duckdb", "postgres", "engine"].includes(id)) {
    const rows = [["DuckDB", "demo"], ["Postgres", "validated"], ["MSSQL / Oracle", "engine-capable"]];
    return <div className="space-y-2 p-5">{rows.map(([name, status]) => <div className="flex items-center justify-between rounded-lg border bg-background p-3" key={name}><span className="flex items-center gap-2 text-xs font-semibold"><Database className="size-3.5 text-brand" />{name}</span><span className="font-mono text-[8px] uppercase text-muted-foreground">{status}</span></div>)}</div>;
  }
  return <div className="grid gap-px bg-border sm:grid-cols-5">{[[Database, "source"], [Table2, "schema"], [Network, "model"], [Braces, "validate"], [BarChart3, "access"]].map(([Icon, label], i) => { const VisualIcon = Icon as typeof Database; return <div className="bg-background p-4" key={String(label)}><VisualIcon className="size-4 text-brand" /><p className="mt-8 font-mono text-[8px]">0{i + 1} / {String(label)}</p></div>; })}</div>;
}

function AboutVisual({ id }: { id: string }) {
  if (id === "principles") return <div className="grid grid-cols-2 gap-px bg-border sm:grid-cols-4">{["D", "I", "M", "A"].map((letter, i) => <div className="bg-background p-5" key={letter}><span className="font-display text-4xl text-muted-foreground/50">{letter.toLowerCase()}</span><p className="mt-8 font-mono text-[8px] text-brand">0{i + 1} / mechanism</p></div>)}</div>;
  return <div className="flex flex-col items-center gap-3 p-6 sm:flex-row"><Node label="Business question" meta="clarity" /><ArrowDown className="size-4 rotate-0 text-brand sm:-rotate-90" /><Node label="dima" meta="modeled + validated" /><ArrowDown className="size-4 rotate-0 text-brand sm:-rotate-90" /><Node label="Auditable answer" meta="evidence" /></div>;
}

function SectionVisual({ kind, id, locale }: { kind: PageKind; id: string; locale: MarketingLocale }) {
  if (kind === "product") {
    if (id === "ask") return <AskVisual locale={locale} />;
    if (id === "model") return <SemanticVisual />;
    if (id === "validate") return <ValidationVisual locale={locale} />;
    if (id === "explore") return <ExploreVisual locale={locale} />;
    if (id === "verify") return <TraceVisual locale={locale} />;
    if (id === "reuse") return <ReuseVisual />;
    return <GovernVisual />;
  }
  if (kind === "how") {
    if (id === "raw-llm" || id === "semantics") return <SemanticVisual />;
    if (id === "execute") return <TraceVisual locale={locale} />;
    if (id === "planned") return <SecurityVisual id="deployment" locale={locale} />;
    return <ValidationVisual locale={locale} />;
  }
  if (kind === "solutions") return <SolutionVisual id={id} locale={locale} />;
  if (kind === "security") return <SecurityVisual id={id} locale={locale} />;
  if (kind === "integrations") return <IntegrationVisual id={id} />;
  return <AboutVisual id={id} />;
}

export function EvidenceDetailPage({ page, content, kind, heroVisual }: { page: PageContent; content: MarketingContent; kind: PageKind; heroVisual?: React.ReactNode }) {
  const fallbackHero = kind === "solutions"
    ? (
      <div className="relative aspect-[16/10] overflow-hidden rounded-xl border bg-card shadow-xl">
        <MarketingEditorialImage asset="decisions" className="marketing-editorial-image" />
        <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/25 via-transparent to-transparent" />
      </div>
    )
    : kind === "about"
      ? (
        <div className="relative aspect-[4/3] overflow-hidden rounded-xl border bg-card shadow-xl">
          <MarketingEditorialImage asset="archive" className="marketing-editorial-image" />
        </div>
      )
      : undefined;

  return (
    <>
      <PageHero page={page} media={heroVisual ?? fallbackHero} />
      <Container className="py-16 sm:py-24">
        <div className="space-y-20 sm:space-y-28">
          {page.sections.map((section, index) => (
            <section className="scroll-mt-24" id={section.id} key={section.id}>
              <div className={`grid items-center gap-8 lg:grid-cols-2 lg:gap-16 ${index % 2 ? "lg:[&>*:first-child]:order-2" : ""}`}>
                <Reveal>
                  {kind === "how" ? <span className="font-mono text-xs text-brand">{String(index + 1).padStart(2, "0")}</span> : null}
                  <div className="mt-5"><StatusBadge status={section.status} content={content} /></div>
                  <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight sm:text-4xl">{section.title}</h2>
                  <p className="mt-5 max-w-xl leading-7 text-muted-foreground">{section.body}</p>
                  {section.points ? <ul className="mt-6 grid gap-2">{section.points.map((point) => <li className="flex gap-3 text-sm" key={point}><Check className="mt-0.5 size-4 shrink-0 text-brand" />{point}</li>)}</ul> : null}
                </Reveal>
                <Reveal delay={0.08} y={18}>
                  <MagicCard>
                    <EvidenceFrame locale={content.locale} code={`${kind} / ${String(index + 1).padStart(2, "0")}`} summary={`${section.title}: ${section.body}`}>
                      <SectionVisual kind={kind} id={section.id} locale={content.locale} />
                    </EvidenceFrame>
                  </MagicCard>
                </Reveal>
              </div>
            </section>
          ))}
        </div>
      </Container>
      <FinalCta content={content} label={page.cta} />
    </>
  );
}
