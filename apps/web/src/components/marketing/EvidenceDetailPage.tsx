import Link from "next/link";
import { ArrowDown, ArrowRight, Check, Sparkles } from "lucide-react";
import { MarketingEditorialImage, type MarketingAssetKey } from "@/components/marketing/MarketingAssets";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Container, Eyebrow, FinalCta, StatusBadge } from "@/components/marketing/MarketingPrimitives";
import { ProductProof } from "@/components/marketing/ProductProof";
import type { MarketingContent, PageContent } from "@/content/marketing";

type PageKind = "product" | "how" | "solutions" | "textile" | "security" | "integrations" | "about";

const pageVisuals: Record<PageKind, { hero: MarketingAssetKey; sections: MarketingAssetKey[] }> = {
  product: { hero: "hero", sections: ["quality", "floor", "review", "quality", "review", "floor", "review", "floor"] },
  how: { hero: "review", sections: ["review", "floor", "quality", "review", "floor", "quality", "floor", "review", "quality", "floor"] },
  solutions: { hero: "review", sections: ["review", "floor", "quality", "floor", "quality", "review"] },
  textile: { hero: "floor", sections: ["floor", "quality", "review", "floor", "quality", "review"] },
  security: { hero: "review", sections: ["review", "floor", "quality", "review", "floor", "quality"] },
  integrations: { hero: "floor", sections: ["floor", "review", "quality", "floor", "review"] },
  about: { hero: "review", sections: ["review", "quality", "floor", "review"] },
};

const railLabels: Record<PageKind, { tr: string[]; en: string[] }> = {
  product: { tr: ["Soru", "Tanım", "Cevap"], en: ["Question", "Definition", "Answer"] },
  how: { tr: ["Anlam", "Kontrol", "Kaynak"], en: ["Meaning", "Guard", "Source"] },
  solutions: { tr: ["Öncelik", "Operasyon", "Karar"], en: ["Priority", "Operations", "Decision"] },
  textile: { tr: ["Parti", "Reçete", "Termin"], en: ["Batch", "Recipe", "Deadline"] },
  security: { tr: ["Kapsam", "Yetki", "İz"], en: ["Scope", "Access", "Trace"] },
  integrations: { tr: ["Kaynak", "Model", "Bağlantı"], en: ["Source", "Model", "Connection"] },
  about: { tr: ["Merak", "Açıklık", "Hesap verebilirlik"], en: ["Curiosity", "Clarity", "Accountability"] },
};

function EditorialHero({ page, content, kind }: { page: PageContent; content: MarketingContent; kind: PageKind }) {
  const tr = content.locale === "tr";
  const visual = pageVisuals[kind];
  return (
    <section className="relative overflow-hidden border-b bg-foreground text-background">
      <div aria-hidden="true" className="marketing-grid absolute inset-0 opacity-20 [mask-image:linear-gradient(to_bottom,black,transparent_90%)]" />
      <Container className="relative grid gap-10 py-16 sm:py-24 lg:min-h-[42rem] lg:grid-cols-[0.78fr_1.22fr] lg:items-center lg:gap-16 lg:py-28">
        <Reveal>
          <Eyebrow>{page.eyebrow}</Eyebrow>
          <h1 className="mt-5 max-w-3xl text-balance font-display text-5xl leading-[0.94] tracking-[-0.045em] sm:text-6xl lg:text-7xl">{page.title}</h1>
          <p className="mt-7 max-w-xl text-pretty text-lg leading-8 text-background/68">{page.description}</p>
          <Link className="mt-8 inline-flex min-h-11 items-center gap-2 rounded-md bg-background px-5 py-3 text-sm font-semibold text-foreground transition-transform duration-200 hover:-translate-y-0.5 focus-visible:-translate-y-0.5" href="/contact">{page.cta}<ArrowRight aria-hidden="true" className="size-4" /></Link>
        </Reveal>
        <Reveal delay={0.08} y={18}>
          <EditorialFigure asset={visual.hero} priority label={tr ? "Dima çalışma sahnesi" : "Dima working scene"} caption={tr ? "İşin içinden gelen cevaplar" : "Answers grounded in the work"} dark />
        </Reveal>
      </Container>
    </section>
  );
}

function EditorialFigure({ asset, label, caption, priority = false, dark = false, compact = false }: { asset: MarketingAssetKey; label: string; caption: string; priority?: boolean; dark?: boolean; compact?: boolean }) {
  return (
    <figure className={`group relative overflow-hidden border ${dark ? "border-background/15 bg-background/5" : "border-border bg-card"} ${compact ? "rounded-lg" : "rounded-[1.15rem]"}`}>
      <MarketingEditorialImage asset={asset} alt={label} className={`marketing-editorial-image transition-transform duration-700 ease-out group-hover:scale-[1.025] ${compact ? "aspect-[4/3]" : "aspect-[16/10]"}`} priority={priority} sizes={compact ? "(min-width: 1024px) 36vw, 100vw" : "(min-width: 1024px) 58vw, 100vw"} />
      <div aria-hidden="true" className={`absolute inset-0 bg-gradient-to-t ${dark ? "from-foreground/70 via-foreground/5 to-transparent" : "from-foreground/45 via-transparent to-transparent"}`} />
      <figcaption className="absolute inset-x-4 bottom-4 flex items-end justify-between gap-4 sm:inset-x-6 sm:bottom-6">
        <span className="max-w-[75%] text-sm font-medium text-background">{caption}</span>
        <span className="shrink-0 font-mono text-micro uppercase tracking-[0.16em] text-background/65">{dark ? "dima / field" : "dima / scene"}</span>
      </figcaption>
    </figure>
  );
}

function StoryRail({ content, kind }: { content: MarketingContent; kind: PageKind }) {
  const labels = railLabels[kind][content.locale];
  return (
    <section className="border-b bg-foreground text-background" aria-label={content.locale === "tr" ? "Sayfa akışı" : "Page sequence"}>
      <Container>
        <ol className="grid divide-y divide-background/15 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
          {labels.map((label, index) => <li className="flex items-center gap-4 px-1 py-5 sm:px-6 sm:first:pl-0" key={label}><span className="font-mono text-micro text-chart-2">0{index + 1}</span><span className="text-sm text-background/72">{label}</span><ArrowRight aria-hidden="true" className="ml-auto size-4 text-background/28" /></li>)}
        </ol>
      </Container>
    </section>
  );
}

function StorySection({ page, content, kind, index }: { page: PageContent; content: MarketingContent; kind: PageKind; index: number }) {
  const section = page.sections[index];
  const visual = pageVisuals[kind].sections[index % pageVisuals[kind].sections.length];
  const tr = content.locale === "tr";
  const reversed = index % 2 === 1;
  return (
    <section className="scroll-mt-24 border-b py-16 sm:py-24" id={section.id}>
      <Container>
        <div className="grid gap-9 lg:grid-cols-[0.12fr_0.63fr_1.25fr] lg:items-center lg:gap-10">
          <Reveal className="flex items-start gap-3 lg:block">
            <span className="font-mono text-xs tabular-nums text-brand">{String(index + 1).padStart(2, "0")}</span>
            <div className="mt-0 lg:mt-5"><StatusBadge status={section.status} content={content} /></div>
          </Reveal>
          <Reveal delay={0.04} className={reversed ? "lg:order-3" : undefined}>
            <h2 className="max-w-2xl text-balance text-3xl font-semibold tracking-[-0.025em] sm:text-4xl" id={`${kind}-${section.id}-title`}>{section.title}</h2>
            <p className="mt-5 max-w-xl leading-7 text-muted-foreground">{section.body}</p>
            {section.points?.length ? <ul className="mt-6 flex max-w-xl flex-wrap gap-x-5 gap-y-3 text-sm text-muted-foreground">{section.points.map((point) => <li className="flex items-start gap-2" key={point}><Check aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-brand" />{point}</li>)}</ul> : null}
          </Reveal>
          <Reveal delay={0.1} y={18} className={reversed ? "lg:order-2" : undefined}>
            <EditorialFigure asset={visual} label={section.title} caption={section.visual?.caption ?? (tr ? "Sanitized çalışma sahnesi" : "Sanitized working scene")} compact />
          </Reveal>
        </div>
      </Container>
    </section>
  );
}

function QuietSignal({ page, content }: { page: PageContent; content: MarketingContent }) {
  const tr = content.locale === "tr";
  return (
    <section className="border-b bg-muted/25 py-14 sm:py-20">
      <Container className="grid gap-8 lg:grid-cols-[0.6fr_1.4fr] lg:items-center">
        <Reveal><div className="flex items-center gap-3"><Sparkles aria-hidden="true" className="size-5 text-brand" /><Eyebrow>{tr ? "Tek bir zincir" : "One visible chain"}</Eyebrow></div><h2 className="mt-4 max-w-xl text-balance font-display text-3xl leading-tight sm:text-4xl">{tr ? "İş sorusu, kontrol ve dayanak aynı hikâyede." : "Question, guard, and source stay in the same story."}</h2></Reveal>
        <Reveal delay={0.08}><div className="grid border-y sm:grid-cols-3">{page.sections.slice(0, 3).map((section, index) => <div className="border-b py-5 last:border-b-0 sm:border-b-0 sm:border-r sm:px-5 sm:first:pl-0 sm:last:border-r-0" key={section.id}><span className="font-mono text-micro text-brand">0{index + 1}</span><p className="mt-3 text-sm font-medium">{section.title}</p></div>)}</div></Reveal>
      </Container>
    </section>
  );
}

export function EvidenceDetailPage({ page, content, kind }: { page: PageContent; content: MarketingContent; kind: PageKind }) {
  return (
    <>
      <EditorialHero content={content} kind={kind} page={page} />
      <StoryRail content={content} kind={kind} />
      {kind === "product" ? <section className="border-b py-16 sm:py-24" aria-labelledby="product-proof-title"><Container><Reveal><Eyebrow>{content.locale === "tr" ? "Ürünün içi" : "Inside the product"}</Eyebrow><h2 id="product-proof-title" className="mt-4 max-w-3xl text-balance font-display text-4xl leading-tight sm:text-5xl">{content.locale === "tr" ? "Cevabın içini adım adım inceleyin." : "Inspect the answer, step by step."}</h2></Reveal><Reveal delay={0.08} className="mt-10"><ProductProof locale={content.locale} /></Reveal></Container></section> : null}
      <div>{page.sections.map((section, index) => <StorySection content={content} index={index} kind={kind} key={section.id} page={page} />)}</div>
      <QuietSignal content={content} page={page} />
      {kind === "textile" ? (
        <Container className="py-12 sm:py-16">
          <nav aria-label={content.locale === "tr" ? "İlgili dima sayfaları" : "Related dima pages"} className="grid gap-3 border-y py-6 sm:grid-cols-4">
            {[[content.nav.product, "/product"], [content.nav.how, "/how-it-works"], [content.nav.security, "/security"], [content.footer.contact, "/contact"]].map(([label, href]) => <Link className="group inline-flex min-h-11 items-center justify-between border-b py-3 text-sm font-medium transition-colors hover:text-brand focus-visible:text-brand sm:border-b-0" href={href} key={href}>{label}<ArrowDown aria-hidden="true" className="size-4 -rotate-90 text-brand transition-transform group-hover:translate-x-1" /></Link>)}
          </nav>
        </Container>
      ) : null}
      <FinalCta content={content} label={page.cta} />
    </>
  );
}
