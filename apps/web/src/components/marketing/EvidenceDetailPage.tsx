import { Fragment } from "react";
import Link from "next/link";
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
import { Container, FinalCta, PageHero, StatusBadge, TileBody } from "@/components/marketing/MarketingPrimitives";
import type {
  MarketingContent,
  MarketingLocale,
  MarketingSceneKey,
  PageContent,
} from "@/content/marketing";

type PageKind = "product" | "how" | "solutions" | "textile" | "security" | "integrations" | "about";

const pageScenes: Record<PageKind, Record<string, MarketingSceneKey>> = {
  product: { ask: "question", model: "definitions", validate: "checks", explore: "results", verify: "source", reuse: "reuse", govern: "access", integrate: "connection" },
  how: { problem: "question", onboarding: "connection", semantics: "definitions", interpretation: "definitions", guard: "checks", permissions: "access", "dry-plan": "checks", execute: "source", provenance: "source", limits: "audit", planned: "deployment" },
  solutions: { executive: "priority", operations: "coordination", production: "coordination", finance: "priority", sales: "memory", inventory: "memory" },
  textile: { question: "question", production: "coordination", recipe: "definitions", quality: "checks", orders: "priority", integration: "connection" },
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
  caption,
  labelledBy,
  description,
}: {
  children: React.ReactNode;
  caption: string;
  labelledBy: string;
  description: string;
}) {
  return (
    <figure aria-labelledby={labelledBy} aria-describedby={`${labelledBy}-description`} className="flex min-h-0 flex-1 flex-col overflow-hidden">
      {/* @container/stage — iç düzenler pencereye değil bu kutunun genişliğine
          göre kırılır. Bu sütun lg'de ~448px, 1440px'te ~576px; aynı JSX ayrıca
          sayfa hero'sunda çok daha geniş render ediliyor. */}
      <p className="sr-only" id={`${labelledBy}-description`}>{description}</p>
      <div aria-hidden="true" className="@container/stage flex-1">{children}</div>
      <figcaption className="shrink-0 border-t bg-muted/20 px-5 py-3 font-mono text-micro uppercase tracking-wider text-muted-foreground">
        {caption}
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
    <div className="space-y-3 p-4 @lg/stage:p-5">
      <div className="max-w-[88%] rounded-lg border bg-background p-4 text-sm font-medium">{t.question}</div>
      <div className="ml-auto max-w-[92%] rounded-lg border border-brand/30 bg-brand/5 p-4">
        <div className="flex items-center gap-2 font-mono text-micro uppercase text-brand"><Layers3 className="size-3 shrink-0" />{t.modeled}</div>
        <div className="mt-3 flex flex-wrap gap-2">
          {tags.map((tag) => <span className="rounded-full border bg-background px-2 py-1 font-mono text-xs" key={tag}>{tag}</span>)}
        </div>
      </div>
      {/* flex-wrap: üstteki etiket şeridinde var, burada yoktu — uzun bir etiket
          dar kartta taşıyordu. */}
      <div className="flex flex-wrap gap-2">
        {prompts.map((item) => <span className="rounded-md border px-2 py-1 text-xs text-muted-foreground" key={item}>{item}</span>)}
      </div>
    </div>
  );
}

function SemanticVisual({ locale }: { locale: MarketingLocale }) {
  const tr = locale === "tr";
  return (
    <div className="marketing-grid relative grid gap-4 p-5 @2xl/stage:grid-cols-[1fr_1.2fr_1fr] @2xl/stage:items-center">
      <div className="space-y-3">
        <Node label={tr ? "Satışlar" : "Sales"} meta={tr ? "veri kaynağı" : "data source"} />
        <Node label={tr ? "Müşteriler" : "Customers"} meta={tr ? "veri kaynağı" : "data source"} />
      </div>
      <div className="rounded-xl border border-brand/40 bg-background p-5 text-center shadow-md">
        <Network className="mx-auto size-5 text-brand" />
        <p className="mt-2 text-sm font-semibold">{tr ? "Ortak iş tanımları" : "Shared business definitions"}</p>
        <p className="mt-2 font-mono text-micro text-muted-foreground">{tr ? "ölçü × ayrıntı × ilişki" : "metric × detail × relationship"}</p>
      </div>
      <div className="space-y-3">
        <Node label={tr ? "Brüt kâr" : "Gross margin"} meta={tr ? "iş tanımı" : "business definition"} />
        <Node label={tr ? "Dönem" : "Period"} meta={tr ? "iş tanımı" : "business definition"} />
      </div>
    </div>
  );
}

// w-full: sütun modunda `items-center` altında üç kutunun üç farklı genişlikte
// çıkmasını engeller; satır modunda çağıran taraf flex-1 verir.
function Node({ label, meta, className = "" }: { label: string; meta: string; className?: string }) {
  return <div className={`w-full min-w-0 rounded-lg border bg-background p-4 ${className}`}><p className="font-mono text-micro uppercase text-muted-foreground">{meta}</p><p className="mt-1 text-xs font-semibold">{label}</p></div>;
}

function ValidationVisual({ locale }: { locale: MarketingLocale }) {
  const labels = locale === "tr"
    ? [["Yapay zekâ önerisi", "aday sorgu"], ["İş tanımları", "ölçü + ayrıntı"], ["Yalnızca okuma", "izin kontrolü"], ["Ön kontrol", "çalıştırılabilir"]]
    : [["AI proposal", "candidate query"], ["Business definitions", "metric + detail"], ["Read-only access", "permission check"], ["Pre-check", "ready to run"]];
  return (
    <div className="grid gap-px bg-border @sm/stage:grid-cols-2">
      {labels.map(([title, detail], index) => (
        <div className="bg-background p-4" key={title}>
          <TileBody
            top={
              <>
                <span className="font-mono text-micro text-brand">0{index + 1}</span>
                {index > 0 ? <Check className="size-3 shrink-0 text-chart-2" /> : null}
              </>
            }
          >
            <p className="text-xs font-semibold">{title}</p>
            <p className="mt-1 font-mono text-xs text-muted-foreground">{detail}</p>
          </TileBody>
        </div>
      ))}
    </div>
  );
}

function ExploreVisual({ locale }: { locale: MarketingLocale }) {
  const t = ui[locale];
  return (
    // minmax(11rem, …): `font-display text-2xl` "31.4%" ~60px genişliğinde ve
    // bölünecek yeri yok — taban olmadan 57px'lik kutuya düşüp kırpılıyordu.
    <div className="grid gap-px bg-border @lg/stage:grid-cols-[minmax(11rem,0.8fr)_1.2fr]">
      <div className="grid grid-cols-2 gap-px bg-border">
        {[["31.4%", "margin"], ["12", "groups"], ["3", "below"], ["Q3", t.current]].map(([value, label]) => (
          <div className="bg-background p-4" key={label}><p className="font-display text-2xl">{value}</p><p className="mt-1 text-xs text-muted-foreground">{label}</p></div>
        ))}
      </div>
      <div className="bg-background p-5">
        <div className="flex h-32 items-end gap-2">
          {[72, 48, 86, 61, 93, 67].map((height, index) => <div className="relative flex h-full flex-1 items-end" key={index}><div className="w-full rounded-t-sm bg-brand/25" style={{ height: `${height}%` }} /></div>)}
        </div>
        <div className="mt-3 flex justify-between gap-2 font-mono text-micro text-muted-foreground"><span>{t.target}</span><span>{t.current}</span></div>
      </div>
    </div>
  );
}

function TraceVisual({ locale }: { locale: MarketingLocale }) {
  const items = locale === "tr"
    ? ["iş tanımı eşleşti", "yalnızca okuma kontrolü geçti", "ön kontrol tamamlandı", "sonuç üretildi"]
    : ["business definition matched", "read-only check passed", "pre-check completed", "result produced"];
  // min-w-0: flex öğesinin varsayılan min-width:auto'su yüzünden uzun etiketler
  // ("yalnızca okuma kontrolü geçti") daralamayıp karttan taşıyordu.
  return <div className="p-5">{items.map((item, index) => <div className="flex gap-4 border-b py-3 last:border-0" key={item}><span className="flex size-7 shrink-0 items-center justify-center rounded-full border font-mono text-micro text-brand">{index + 1}</span><div className="min-w-0"><p className="text-xs font-medium">{item}</p><p className="mt-1 font-mono text-micro text-muted-foreground">{locale === "tr" ? "adım" : "step"}/{String(index + 1).padStart(2, "0")} · {locale === "tr" ? "TAMAM" : "PASS"}</p></div></div>)}</div>;
}

function ReuseVisual({ locale }: { locale: MarketingLocale }) {
  const items = locale === "tr"
    ? [[RefreshCw, "Yeniden çalıştır", "aynı tanım"], [Timer, "Zamanla", "Pilot kapsamı"], [CircleGauge, "Bildirim al", "Pilot kapsamı"]]
    : [[RefreshCw, "Run again", "same definition"], [Timer, "Schedule", "Pilot scope"], [CircleGauge, "Get notified", "Pilot scope"]];
  return <div className="grid gap-px bg-border @xl/stage:grid-cols-3">{items.map(([Icon, title, meta]) => { const VisualIcon = Icon as typeof RefreshCw; return <div className="bg-background p-5" key={String(title)}><TileBody top={<VisualIcon className="size-4 shrink-0 text-brand" />}><p className="text-sm font-semibold">{String(title)}</p><p className="mt-1 font-mono text-xs text-muted-foreground">{String(meta)}</p></TileBody></div>; })}</div>;
}

function GovernVisual({ locale }: { locale: MarketingLocale }) {
  const items = locale === "tr"
    ? [[Fingerprint, "Oturum", "bellekte erişim"], [KeyRound, "Yetki", "sunucu kaynağı"], [ShieldCheck, "Kurum kapsamı", "sınırlandırılmış istek"]]
    : [[Fingerprint, "Session", "in-memory access"], [KeyRound, "Permission", "server source"], [ShieldCheck, "Organization scope", "scoped request"]];
  // ReuseVisual ile yapısal olarak aynı — orada text-sm/mt-8, burada text-xs/mt-7
  // vardı; gerekçesiz ayrışmaydı, tek biçime alındı.
  return <div className="grid gap-px bg-border @xl/stage:grid-cols-3">{items.map(([Icon, title, meta]) => { const VisualIcon = Icon as typeof Fingerprint; return <div className="bg-background p-5" key={String(title)}><TileBody top={<VisualIcon className="size-4 shrink-0 text-brand" />}><p className="text-sm font-semibold">{String(title)}</p><p className="mt-1 font-mono text-xs text-muted-foreground">{String(meta)}</p></TileBody></div>; })}</div>;
}

function SolutionVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (id === "executive") {
    const priorities = tr
      ? [["Brüt kâr", "−7,2 puan"], ["Nakit dönüşümü", "+6 gün"], ["Stok seviyesi", "3 kritik"]]
      : [["Gross margin", "−7.2 pts"], ["Cash conversion", "+6 days"], ["Inventory level", "3 critical"]];
    return <AnimatedList className="space-y-2 p-5">{priorities.map(([label, value], index) => <div className="flex items-center justify-between gap-3 rounded-lg border bg-background p-4" key={label}><span className="flex min-w-0 items-center gap-3 text-xs font-medium"><span className="shrink-0 font-mono text-micro text-brand">0{index + 1}</span>{label}</span><span className="shrink-0 font-mono text-xs">{value}</span></div>)}</AnimatedList>;
  }
  if (id === "operations") {
    const teams = tr ? ["Finans", "Satış", "Stok"] : ["Finance", "Sales", "Inventory"];
    return <div className="flex flex-col items-center gap-3 p-6 @lg/stage:flex-row">{teams.map((team, index) => <div className="contents" key={team}><Node className="@lg/stage:flex-1" label={team} meta={tr ? "aynı tanım" : "shared definition"} />{index < teams.length - 1 ? <ArrowDown className="size-4 shrink-0 text-brand @lg/stage:-rotate-90" /> : null}</div>)}</div>;
  }
  const saved = tr
    ? ["Haftalık hedef sapmaları", "Brüt kâr kırılımı", "Kritik stoklar"]
    : ["Weekly target gaps", "Gross-margin breakdown", "Critical inventory"];
  return <AnimatedList className="space-y-2 p-5">{saved.map((item, index) => <div className="flex items-center gap-3 rounded-lg border bg-background p-4" key={item}><RefreshCw className="size-4 shrink-0 text-brand" /><span className="min-w-0 text-xs font-medium">{item}</span><span className="ml-auto shrink-0 font-mono text-micro text-muted-foreground">0{index + 1}</span></div>)}</AnimatedList>;
}

function SecurityVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (id === "session") {
    const steps = tr
      ? [[MessageSquareText, "İstek"], [LockKeyhole, "Oturum kontrolü"], [RefreshCw, "Güvenli yenileme"], [ShieldCheck, "Devam"]]
      : [[MessageSquareText, "Request"], [LockKeyhole, "Session check"], [RefreshCw, "Secure refresh"], [ShieldCheck, "Continue"]];
    return <div className="grid grid-cols-2 gap-px bg-border @xl/stage:grid-cols-4">{steps.map(([Icon, label], i) => { const VisualIcon = Icon as typeof MessageSquareText; return <div className="bg-background p-4" key={String(label)}><TileBody top={<span className="font-mono text-micro text-brand">0{i + 1}</span>}><VisualIcon className="size-4 shrink-0 text-brand" /><p className="mt-2 text-xs font-semibold">{String(label)}</p></TileBody></div>; })}</div>;
  }
  if (id === "flow") return <ValidationVisual locale={locale} />;
  if (id === "deployment") return <div className="grid gap-4 p-5 @sm/stage:grid-cols-2"><Node label={tr ? "Bulut kurulumu" : "Cloud deployment"} meta={tr ? "kullanılabilir" : "available"} /><div className="rounded-lg border border-dashed p-4"><p className="font-mono text-micro text-muted-foreground">{tr ? "planlanıyor" : "planned"}</p><p className="mt-1 text-xs font-semibold">{tr ? "Kurum içi hibrit bağlantı" : "Hybrid on-premises connection"}</p></div></div>;
  return <GovernVisual locale={locale} />;
}

function IntegrationVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (["duckdb", "postgres", "engine"].includes(id)) {
    const rows = tr
      ? [["DuckDB", "örnek kaynak"], ["Postgres", "Dima’da doğrulandı"], ["MSSQL / Oracle", "teknik olarak mümkün"]]
      : [["DuckDB", "sample source"], ["Postgres", "Verified in Dima"], ["MSSQL / Oracle", "Engine capable"]];
    return <div className="space-y-2 p-5">{rows.map(([name, status]) => <div className="flex items-center justify-between gap-3 rounded-lg border bg-background p-4" key={name}><span className="flex min-w-0 items-center gap-2 text-xs font-semibold"><Database className="size-3.5 shrink-0 text-brand" />{name}</span><span className="shrink-0 font-mono text-xs text-muted-foreground">{status}</span></div>)}</div>;
  }
  const steps = tr
    ? [[Database, "kaynak"], [Table2, "tablolar"], [Network, "iş tanımları"], [Braces, "kontrol"], [BarChart3, "erişim"]]
    : [[Database, "source"], [Table2, "tables"], [Network, "definitions"], [Braces, "checks"], [BarChart3, "access"]];
  // 5'li şerit yalnızca gerçekten geniş sahnede; eskiden sm:grid-cols-5 dar
  // sütunda hücre başına ~57px bırakıp "01 / iş tanımları"nı zorla sarıyordu.
  return <div className="grid grid-cols-2 gap-px bg-border @sm/stage:grid-cols-3 @2xl/stage:grid-cols-5">{steps.map(([Icon, label], i) => { const VisualIcon = Icon as typeof Database; return <div className="bg-background p-4" key={String(label)}><TileBody top={<VisualIcon className="size-4 shrink-0 text-brand" />}><p className="font-mono text-xs">0{i + 1} / {String(label)}</p></TileBody></div>; })}</div>;
}

function AboutVisual({ id, locale }: { id: string; locale: MarketingLocale }) {
  const tr = locale === "tr";
  if (id === "principles") return <div className="grid grid-cols-2 gap-px bg-border @xl/stage:grid-cols-4">{["D", "I", "M", "A"].map((letter, i) => <div className="bg-background p-5" key={letter}><TileBody top={<span className="font-display text-4xl leading-none text-muted-foreground/50">{letter.toLowerCase()}</span>}><p className="font-mono text-micro text-brand">0{i + 1} / {tr ? "ilke" : "principle"}</p></TileBody></div>)}</div>;
  return <div className="flex flex-col items-center gap-3 p-6 @lg/stage:flex-row"><Node className="@lg/stage:flex-1" label={tr ? "İş sorusu" : "Business question"} meta={tr ? "açıklık" : "clarity"} /><ArrowDown className="size-4 shrink-0 text-brand @lg/stage:-rotate-90" /><Node className="@lg/stage:flex-1" label="dima" meta={tr ? "tanımlı + kontrollü" : "defined + checked"} /><ArrowDown className="size-4 shrink-0 text-brand @lg/stage:-rotate-90" /><Node className="@lg/stage:flex-1" label={tr ? "İncelenebilir cevap" : "Reviewable answer"} meta={tr ? "kaynak" : "source"} /></div>;
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
        <MarketingEditorialImage asset="decisions" className="marketing-editorial-image" priority />
        <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/25 via-transparent to-transparent" />
      </div>
    )
    : kind === "about"
      ? (
        <div className="relative aspect-[4/3] overflow-hidden rounded-xl border bg-card shadow-xl">
        <MarketingEditorialImage asset="archive" className="marketing-editorial-image" priority />
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
                {/* items-center YOK: stretch varsayılanı geri geldi, böylece metin
                    sütunu ile kartın üstleri her bölümde hizalanıyor (eskiden ofset
                    bölümden bölüme yön değiştiriyordu). */}
                <div className={`grid gap-8 lg:grid-cols-2 lg:gap-10 [&>*]:min-w-0 ${index % 2 ? "lg:[&>*:first-child]:order-2" : ""}`}>
                  <Reveal>
                    <div className="flex flex-wrap items-center gap-3">
                      {kind === "how" ? <span className="font-mono text-xs text-brand">{String(index + 1).padStart(2, "0")}</span> : null}
                      <StatusBadge status={section.status} content={content} />
                    </div>
                    <h2 className="mt-4 text-balance text-3xl font-semibold tracking-tight sm:text-4xl" id={`${kind}-${section.id}-title`}>{section.title}</h2>
                    <p className="mt-5 max-w-xl leading-7 text-muted-foreground">{section.body}</p>
                    {section.points ? <AnimatedList as="ul" className="mt-6 grid gap-2" itemClassName="flex gap-3 text-sm">{section.points.map((point) => <Fragment key={point}><Check className="mt-0.5 size-4 shrink-0 text-brand" />{point}</Fragment>)}</AnimatedList> : null}
                  </Reveal>
                  <Reveal delay={0.08} y={18} className="flex">
                    <MagicCard className="w-full" tilt={false}>
                      {/* caption artık section.body'yi tekrarlamıyor — aynı cümle
                          ekranda iki kez basılıyordu ve kart yüksekliğini veriye
                          bağlıyordu. Kısa, sabit bir görsel etiket kaldı. */}
                      <EvidenceFrame labelledBy={`${kind}-${section.id}-title`} caption={section.visual?.caption ?? section.title} description={section.visual?.technicalNote ?? section.body}>
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
      {kind === "textile" ? (
        <Container className="pb-16 sm:pb-24">
          <nav aria-label={content.locale === "tr" ? "İlgili dima sayfaları" : "Related dima pages"} className="grid gap-3 border-y py-6 sm:grid-cols-4">
            {[
              [content.nav.product, "/product"],
              [content.nav.how, "/how-it-works"],
              [content.nav.security, "/security"],
              [content.footer.contact, "/contact"],
            ].map(([label, href]) => <Link className="inline-flex min-h-11 items-center justify-between rounded-md border bg-card px-4 text-sm font-medium transition-colors hover:border-brand/40 hover:bg-accent focus-visible:outline-2 focus-visible:outline-ring" href={href} key={href}>{label}<ArrowDown aria-hidden="true" className="-rotate-90 text-brand" /></Link>)}
          </nav>
        </Container>
      ) : null}
      <FinalCta content={content} label={page.cta} />
    </>
  );
}
