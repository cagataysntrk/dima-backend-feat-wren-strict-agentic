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
import { AnimatedList, MagicCard } from "@/components/marketing/MagicUI";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Container, FinalCta, PageHero, StatusBadge } from "@/components/marketing/MarketingPrimitives";
import type {
  MarketingContent,
  MarketingLocale,
  MarketingSceneKey,
  PageContent,
} from "@/content/marketing";

type PageKind = "product" | "how" | "solutions" | "security" | "integrations" | "about";

const pageScenes: Record<PageKind, Record<string, MarketingSceneKey>> = {
  product: { ask: "question", model: "definitions", validate: "checks", explore: "results", verify: "source", reuse: "reuse", govern: "access" },
  how: { onboarding: "connection", semantics: "definitions", "dry-plan": "checks", execute: "source", planned: "deployment" },
  solutions: { executive: "priority", operations: "coordination", data: "memory" },
  security: { "read-only": "checks", session: "session", tenant: "access", audit: "audit", flow: "data-flow", deployment: "deployment" },
  integrations: { duckdb: "database", postgres: "database", engine: "support", process: "connection", status: "support" },
  about: { purpose: "purpose", principles: "principles", company: "company", truth: "truth" },
};

const ui = {
  tr: {
    question: "Brüt kârı hedefin altında kalan gruplar hangileri?",
    modeled: "Onaylı iş tanımları",
    verified: "ön kontrol tamamlandı",
    target: "hedef",
    current: "güncel",
    evidence: "kanıt görünümü",
  },
  en: {
    question: "Which groups are below gross-margin target?",
    modeled: "Approved business definitions",
    verified: "pre-check complete",
    target: "target",
    current: "current",
    evidence: "evidence view",
  },
} as const;

function EvidenceFrame({
  children,
  summary,
  labelledBy,
}: {
  children: React.ReactNode;
  summary: string;
  labelledBy: string;
}) {
  return (
    <figure aria-labelledby={labelledBy} className="overflow-hidden bg-card">
      <div aria-hidden="true">{children}</div>
      <figcaption className="border-t bg-muted/20 px-4 py-3 text-xs leading-5 text-muted-foreground">
        {summary}
      </figcaption>
    </figure>
  );
}

function AskVisual({ locale }: { locale: MarketingLocale }) {
  const t = ui[locale];
  const tags = locale === "tr"
    ? ["brüt kâr", "ürün grubu", "bu çeyrek"]
    : ["gross margin", "product group", "this quarter"];
  const prompts = locale === "tr"
    ? ["↳ hedef", "↳ dönem", "↳ grup"]
    : ["↳ target", "↳ period", "↳ group"];
  return (
    <div className="space-y-3 p-4 sm:p-5">
      <div className="max-w-[88%] rounded-lg border bg-background p-4 text-sm font-medium">{t.question}</div>
      <div className="ml-auto max-w-[92%] rounded-lg border border-brand/30 bg-brand/5 p-4">
        <div className="flex items-center gap-2 font-mono text-[9px] uppercase text-brand"><Layers3 className="size-3" />{t.modeled}</div>
        <div className="mt-3 flex flex-wrap gap-2">
          {tags.map((tag) => <span className="rounded-full border bg-background px-2 py-1 font-mono text-[8px]" key={tag}>{tag}</span>)}
        </div>
      </div>
      <div className="flex gap-2">
        {prompts.map((item) => <span className="rounded-md border px-2 py-1 text-[9px] text-muted-foreground" key={item}>{item}</span>)}
      </div>
    </div>
  );
}

function SemanticVisual({ locale }: { locale: MarketingLocale }) {
  const tr = locale === "tr";
  return (
    <div className="marketing-grid relative grid gap-4 p-5 sm:grid-cols-[1fr_1.2fr_1fr] sm:items-center">
      <div className="space-y-3">
        <Node label={tr ? "Satışlar" : "Sales"} meta={tr ? "veri kaynağı" : "data source"} />
        <Node label={tr ? "Müşteriler" : "Customers"} meta={tr ? "veri kaynağı" : "data source"} />
      </div>
      <div className="rounded-xl border border-brand/40 bg-background p-5 text-center shadow-md">
        <Network className="mx-auto size-5 text-brand" />
        <p className="mt-2 text-sm font-semibold">{tr ? "Ortak iş tanımları" : "Shared business definitions"}</p>
        <p className="mt-2 font-mono text-[8px] text-muted-foreground">{tr ? "ölçü × ayrıntı × ilişki" : "metric × detail × relationship"}</p>
      </div>
      <div className="space-y-3">
        <Node label={tr ? "Brüt kâr" : "Gross margin"} meta={tr ? "iş tanımı" : "business definition"} />
        <Node label={tr ? "Dönem" : "Period"} meta={tr ? "iş tanımı" : "business definition"} />
      </div>
    </div>
  );
}

function Node({ label, meta }: { label: string; meta: string }) {
  return <div className="rounded-lg border bg-background p-3"><p className="font-mono text-[8px] uppercase text-muted-foreground">{meta}</p><p className="mt-1 text-xs font-semibold">{label}</p></div>;
}

function ValidationVisual({ locale }: { locale: MarketingLocale }) {
  const labels = locale === "tr"
    ? [["Yapay zekâ önerisi", "aday sorgu"], ["İş tanımları", "ölçü + ayrıntı"], ["Yalnızca okuma", "izin kontrolü"], ["Ön kontrol", "çalıştırılabilir"]]
    : [["AI proposal", "candidate query"], ["Business definitions", "metric + detail"], ["Read-only access", "permission check"], ["Pre-check", "ready to run"]];
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
  const items = locale === "tr"
    ? ["iş tanımı eşleşti", "yalnızca okuma kontrolü geçti", "ön kontrol tamamlandı", "sonuç üretildi"]
    : ["business definition matched", "read-only check passed", "pre-check completed", "result produced"];
  return <div className="p-5">{items.map((item, index) => <div className="flex gap-4 border-b py-3 last:border-0" key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-[9px] text-brand">{index + 1}</span><div><p className="text-xs font-medium">{item}</p><p className="mt-1 font-mono text-[8px] text-muted-foreground">{locale === "tr" ? "adım" : "step"}/{String(index + 1).padStart(2, "0")} · {locale === "tr" ? "TAMAM" : "PASS"}</p></div></div>)}</div>;
}

function ReuseVisual({ locale }: { locale: MarketingLocale }) {
  const items = locale === "tr"
    ? [[RefreshCw, "Yeniden çalıştır", "aynı tanım"], [Timer, "Zamanla", "Beta"], [CircleGauge, "Bildirim al", "Beta"]]
    : [[RefreshCw, "Run again", "same definition"], [Timer, "Schedule", "Beta"], [CircleGauge, "Get notified", "Beta"]];
  return <div className="grid gap-px bg-border sm:grid-cols-3">{items.map(([Icon, title, meta]) => { const VisualIcon = Icon as typeof RefreshCw; return <div className="bg-background p-5" key={String(title)}><VisualIcon className="size-4 text-brand" /><p className="mt-8 text-sm font-semibold">{String(title)}</p><p className="mt-1 font-mono text-[8px] text-muted-foreground">{String(meta)}</p></div>; })}</div>;
}

function GovernVisual({ locale }: { locale: MarketingLocale }) {
  const items = locale === "tr"
    ? [[Fingerprint, "Oturum", "bellekte erişim"], [KeyRound, "Yetki", "sunucu kaynağı"], [ShieldCheck, "Kurum kapsamı", "sınırlandırılmış istek"]]
    : [[Fingerprint, "Session", "in-memory access"], [KeyRound, "Permission", "server source"], [ShieldCheck, "Organization scope", "scoped request"]];
  return <div className="grid gap-px bg-border sm:grid-cols-3">{items.map(([Icon, title, meta]) => { const VisualIcon = Icon as typeof Fingerprint; return <div className="bg-background p-5" key={String(title)}><VisualIcon className="size-4 text-brand" /><p className="mt-7 text-xs font-semibold">{String(title)}</p><p className="mt-1 font-mono text-[8px] text-muted-foreground">{String(meta)}</p></div>; })}</div>;
}

function SolutionVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (id === "executive") {
    const priorities = tr
      ? [["Brüt kâr", "−7,2 puan"], ["Nakit dönüşümü", "+6 gün"], ["Stok seviyesi", "3 kritik"]]
      : [["Gross margin", "−7.2 pts"], ["Cash conversion", "+6 days"], ["Inventory level", "3 critical"]];
    return <AnimatedList className="space-y-2 p-5">{priorities.map(([label, value], index) => <div className="flex items-center justify-between rounded-lg border bg-background p-4" key={label}><span className="flex items-center gap-3 text-xs font-medium"><span className="font-mono text-[9px] text-brand">0{index + 1}</span>{label}</span><span className="font-mono text-xs">{value}</span></div>)}</AnimatedList>;
  }
  if (id === "operations") {
    const teams = tr ? ["Finans", "Satış", "Stok"] : ["Finance", "Sales", "Inventory"];
    return <div className="flex flex-col items-center gap-3 p-6 sm:flex-row">{teams.map((team, index) => <div className="contents" key={team}><Node label={team} meta={tr ? "aynı tanım" : "shared definition"} />{index < teams.length - 1 ? <ArrowDown className="size-4 text-brand sm:-rotate-90" /> : null}</div>)}</div>;
  }
  const saved = tr
    ? ["Haftalık hedef sapmaları", "Brüt kâr kırılımı", "Kritik stoklar"]
    : ["Weekly target gaps", "Gross-margin breakdown", "Critical inventory"];
  return <AnimatedList className="space-y-2 p-5">{saved.map((item, index) => <div className="flex items-center gap-3 rounded-lg border bg-background p-4" key={item}><RefreshCw className="size-4 text-brand" /><span className="text-xs font-medium">{item}</span><span className="ml-auto font-mono text-[8px] text-muted-foreground">0{index + 1}</span></div>)}</AnimatedList>;
}

function SecurityVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (id === "session") {
    const steps = tr
      ? [[MessageSquareText, "İstek"], [LockKeyhole, "Oturum kontrolü"], [RefreshCw, "Güvenli yenileme"], [ShieldCheck, "Devam"]]
      : [[MessageSquareText, "Request"], [LockKeyhole, "Session check"], [RefreshCw, "Secure refresh"], [ShieldCheck, "Continue"]];
    return <div className="grid gap-px bg-border sm:grid-cols-4">{steps.map(([Icon, label], i) => { const VisualIcon = Icon as typeof MessageSquareText; return <div className="bg-background p-4" key={String(label)}><span className="font-mono text-[8px] text-brand">0{i + 1}</span><VisualIcon className="mt-8 size-4 text-brand" /><p className="mt-2 text-xs font-semibold">{String(label)}</p></div>; })}</div>;
  }
  if (id === "flow") return <ValidationVisual locale={locale} />;
  if (id === "deployment") return <div className="grid gap-4 p-5 sm:grid-cols-2"><Node label={tr ? "Bulut kurulumu" : "Cloud deployment"} meta={tr ? "kullanılabilir" : "available"} /><div className="rounded-lg border border-dashed p-3"><p className="font-mono text-[8px] text-muted-foreground">{tr ? "planlanıyor" : "planned"}</p><p className="mt-1 text-xs font-semibold">{tr ? "Kurum içi hibrit bağlantı" : "Hybrid on-premises connection"}</p></div></div>;
  return <GovernVisual locale={locale} />;
}

function IntegrationVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (["duckdb", "postgres", "engine"].includes(id)) {
    const rows = tr
      ? [["DuckDB", "örnek kaynak"], ["Postgres", "Dima’da doğrulandı"], ["MSSQL / Oracle", "teknik olarak mümkün"]]
      : [["DuckDB", "sample source"], ["Postgres", "Verified in Dima"], ["MSSQL / Oracle", "Engine capable"]];
    return <div className="space-y-2 p-5">{rows.map(([name, status]) => <div className="flex items-center justify-between rounded-lg border bg-background p-3" key={name}><span className="flex items-center gap-2 text-xs font-semibold"><Database className="size-3.5 text-brand" />{name}</span><span className="font-mono text-[8px] text-muted-foreground">{status}</span></div>)}</div>;
  }
  const steps = tr
    ? [[Database, "kaynak"], [Table2, "tablolar"], [Network, "iş tanımları"], [Braces, "kontrol"], [BarChart3, "erişim"]]
    : [[Database, "source"], [Table2, "tables"], [Network, "definitions"], [Braces, "checks"], [BarChart3, "access"]];
  return <div className="grid gap-px bg-border sm:grid-cols-5">{steps.map(([Icon, label], i) => { const VisualIcon = Icon as typeof Database; return <div className="bg-background p-4" key={String(label)}><VisualIcon className="size-4 text-brand" /><p className="mt-8 font-mono text-[8px]">0{i + 1} / {String(label)}</p></div>; })}</div>;
}

function AboutVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (id === "principles") return <div className="grid grid-cols-2 gap-px bg-border sm:grid-cols-4">{["D", "I", "M", "A"].map((letter, i) => <div className="bg-background p-5" key={letter}><span className="font-display text-4xl text-muted-foreground/50">{letter.toLowerCase()}</span><p className="mt-8 font-mono text-[8px] text-brand">0{i + 1} / {tr ? "ilke" : "principle"}</p></div>)}</div>;
  return <div className="flex flex-col items-center gap-3 p-6 sm:flex-row"><Node label={tr ? "İş sorusu" : "Business question"} meta={tr ? "açıklık" : "clarity"} /><ArrowDown className="size-4 rotate-0 text-brand sm:-rotate-90" /><Node label="dima" meta={tr ? "tanımlı + kontrollü" : "defined + checked"} /><ArrowDown className="size-4 rotate-0 text-brand sm:-rotate-90" /><Node label={tr ? "İncelenebilir cevap" : "Reviewable answer"} meta={tr ? "kaynak" : "source"} /></div>;
}

function SectionVisual({ scene, id, locale }: { scene: MarketingSceneKey; id: string; locale: MarketingLocale }) {
  if (scene === "question") return <AskVisual locale={locale} />;
  if (scene === "definitions") return <SemanticVisual locale={locale} />;
  if (scene === "checks") return <ValidationVisual locale={locale} />;
  if (scene === "results") return <ExploreVisual locale={locale} />;
  if (scene === "source") return <TraceVisual locale={locale} />;
  if (scene === "reuse") return <ReuseVisual locale={locale} />;
  if (scene === "access") return <GovernVisual locale={locale} />;
  if (["priority", "coordination", "memory"].includes(scene)) return <SolutionVisual id={id} locale={locale} />;
  if (["session", "audit", "data-flow", "deployment"].includes(scene)) return <SecurityVisual id={id} locale={locale} />;
  if (["database", "connection", "support"].includes(scene)) return <IntegrationVisual id={id} locale={locale} />;
  return <AboutVisual id={id} locale={locale} />;
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
          {page.sections.map((section, index) => {
            const scene = section.visual?.key ?? pageScenes[kind][section.id];
            if (!scene) return null;
            return (
              <section className="scroll-mt-24" id={section.id} key={section.id}>
                <div className={`grid items-center gap-8 lg:grid-cols-2 lg:gap-16 ${index % 2 ? "lg:[&>*:first-child]:order-2" : ""}`}>
                  <Reveal>
                    {kind === "how" ? <span className="font-mono text-xs text-brand">{String(index + 1).padStart(2, "0")}</span> : null}
                    {section.status ? <div className="mt-5"><StatusBadge status={section.status} content={content} /></div> : null}
                    <h2 className="mt-3 text-balance text-3xl font-semibold tracking-tight sm:text-4xl" id={`${kind}-${section.id}-title`}>{section.title}</h2>
                    <p className="mt-5 max-w-xl leading-7 text-muted-foreground">{section.body}</p>
                    {section.points ? <AnimatedList className="mt-6 grid gap-2">{section.points.map((point) => <li className="flex gap-3 text-sm" key={point}><Check className="mt-0.5 size-4 shrink-0 text-brand" />{point}</li>)}</AnimatedList> : null}
                  </Reveal>
                  <Reveal delay={0.08} y={18}>
                    <MagicCard>
                      <EvidenceFrame labelledBy={`${kind}-${section.id}-title`} summary={section.body}>
                        <SectionVisual scene={scene} id={section.id} locale={content.locale} />
                      </EvidenceFrame>
                    </MagicCard>
                  </Reveal>
                </div>
              </section>
            );
          })}
        </div>
      </Container>
      <FinalCta content={content} label={page.cta} />
    </>
  );
}
