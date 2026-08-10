import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Database, Search, ShieldCheck } from "lucide-react";
import { getLocale } from "next-intl/server";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Container, Eyebrow, FinalCta } from "@/components/marketing/MarketingPrimitives";
import { ProductProof } from "@/components/marketing/ProductProof";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { getMarketingContent } from "@/content/marketing";

export async function generateMetadata(): Promise<Metadata> {
  const content = getMarketingContent(await getLocale());
  return {
    title: { absolute: `dima — ${content.home.eyebrow}` },
    description: content.home.description,
    alternates: { canonical: "/" },
    openGraph: { title: content.home.title, description: content.home.description, url: "/", type: "website" },
    twitter: { card: "summary_large_image", title: content.home.title, description: content.home.description },
  };
}

export default async function MarketingHome() {
  const content = getMarketingContent(await getLocale());
  const h = content.home;
  const tr = content.locale === "tr";

  return (
    <>
      <section className="relative overflow-hidden border-b bg-foreground text-background">
        <div aria-hidden="true" className="marketing-grid absolute inset-0 opacity-20 [mask-image:linear-gradient(to_bottom,black,transparent_92%)]" />
        <Container className="relative grid gap-10 py-10 sm:py-16 lg:min-h-[calc(100svh-4rem)] lg:grid-cols-[0.84fr_1.16fr] lg:items-center lg:gap-16 lg:py-20">
          <Reveal>
            <Eyebrow>{h.eyebrow}</Eyebrow>
            <h1 className="mt-5 max-w-3xl text-balance font-display text-5xl leading-[0.91] tracking-[-0.05em] sm:text-6xl lg:text-[clamp(4.5rem,7vw,7.25rem)]">{h.title}</h1>
            <p className="mt-7 max-w-xl text-pretty text-lg leading-8 text-background/68">{h.description}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild variant="brand" size="lg" className="min-h-11"><Link href="/contact">{content.common.demo}<ArrowRight aria-hidden="true" /></Link></Button>
              <Button asChild variant="outline" size="lg" className="min-h-11 border-background/25 bg-transparent text-background hover:bg-background/10 hover:text-background"><Link href="/product">{content.nav.product}</Link></Button>
            </div>
            <ol aria-label={tr ? "Dima akışı" : "Dima flow"} className="mt-12 grid max-w-xl grid-cols-2 border-y border-background/15 sm:grid-cols-4 sm:border-x">
              {h.process.map((step, index) => <li className="border-b border-background/15 px-3 py-4 last:border-b-0 sm:border-b-0 sm:border-r sm:last:border-r-0" key={step}><span className="font-mono text-micro tabular-nums text-chart-2">{String(index + 1).padStart(2, "0")}</span><p className="mt-2 text-xs font-medium leading-5 text-background/75">{step}</p></li>)}
            </ol>
          </Reveal>
          <Reveal delay={0.08} y={18}>
            <figure className="group relative overflow-hidden rounded-[1.35rem] border border-background/15 bg-background/5">
              <MarketingEditorialImage asset="homeHero" alt={tr ? "Boyahane operatörü kumaşı kontrol ediyor" : "Textile operator inspecting fabric in a dyehouse"} className="marketing-editorial-image aspect-[4/3] transition-transform duration-700 ease-out group-hover:scale-[1.025] lg:aspect-[5/4]" priority sizes="(min-width: 1024px) 58vw, 100vw" />
              <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/80 via-foreground/5 to-transparent" />
              <figcaption className="absolute inset-x-5 bottom-5 sm:inset-x-7 sm:bottom-7"><span className="font-mono text-micro uppercase text-chart-2">{tr ? "Saha notu" : "Field note"}</span><span className="mt-2 block max-w-sm text-lg font-medium text-background">{tr ? "Cevap, işin gerçek bağlamında başlar." : "The answer starts in the context of the work."}</span></figcaption>
            </figure>
          </Reveal>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="proof-title">
        <Container>
          <Reveal className="grid gap-5 md:grid-cols-[0.75fr_1.25fr] md:items-end">
            <div><Eyebrow>{tr ? "İlk kanıt" : "The first proof"}</Eyebrow><h2 id="proof-title" className="mt-4 max-w-2xl text-balance font-display text-4xl leading-tight sm:text-5xl">{h.proofTitle}</h2></div>
            <p className="max-w-xl leading-7 text-muted-foreground">{h.proofBody}</p>
          </Reveal>
          <Reveal className="mt-10" delay={0.08}><ProductProof locale={content.locale} /></Reveal>
        </Container>
      </section>

      <section className="border-b bg-muted/25 py-16 sm:py-24" aria-labelledby="pillars-title">
        <Container>
          <Reveal className="max-w-3xl"><Eyebrow>D-I-M-A</Eyebrow><h2 id="pillars-title" className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.pillarsTitle}</h2><p className="mt-5 max-w-2xl leading-7 text-muted-foreground">{h.pillarsBody}</p></Reveal>
          <div className="mt-12 border-y">
            {h.pillars.map((pillar, index) => <Reveal key={pillar.letter} delay={index * 0.04}><article className="grid gap-4 border-b py-7 last:border-b-0 sm:grid-cols-[5rem_0.7fr_1.3fr] sm:items-start sm:gap-8"><span className="font-display text-6xl leading-none text-brand sm:text-7xl">{pillar.letter}</span><h3 className="text-xl font-semibold sm:pt-2">{pillar.title}</h3><p className="max-w-xl leading-7 text-muted-foreground sm:pt-2">{pillar.body}</p></article></Reveal>)}
          </div>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="questions-title">
        <Container className="grid gap-10 lg:grid-cols-[0.72fr_1.28fr] lg:items-start">
          <Reveal><h2 id="questions-title" className="max-w-xl text-balance font-display text-4xl sm:text-5xl">{h.useCasesTitle}</h2><p className="mt-5 max-w-md leading-7 text-muted-foreground">{h.operationsBody}</p><div className="mt-8"><MarketingEditorialImage asset="homeQuality" alt={tr ? "Kumaş kalite kontrolü" : "Fabric quality inspection"} className="aspect-[4/3] rounded-lg" sizes="(min-width: 1024px) 32vw, 100vw" /></div></Reveal>
          <Reveal delay={0.08}><ul className="border-y">{h.useCases.map((item, index) => <li className="group border-b py-5 last:border-b-0" key={`${item.title}-${item.question}`}><Link href="/product" className="grid min-h-11 grid-cols-[2.5rem_0.7fr_1.3fr_auto] items-center gap-3 transition-colors hover:text-brand focus-visible:text-brand"><span className="font-mono text-micro text-brand">{String(index + 1).padStart(2, "0")}</span><span className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground"><Search className="size-3.5" aria-hidden="true" />{item.title}</span><span className="text-sm leading-6 text-foreground">{item.question}</span><ArrowRight aria-hidden="true" className="size-4 text-brand transition-transform group-hover:translate-x-1" /></Link></li>)}</ul></Reveal>
        </Container>
      </section>

      <section className="border-b bg-foreground py-16 text-background sm:py-24" aria-labelledby="workflow-title">
        <Container>
          <Reveal><h2 id="workflow-title" className="max-w-3xl text-balance font-display text-4xl sm:text-5xl">{h.workflowTitle}</h2></Reveal>
          <div className="mt-12 grid border-y border-background/15 sm:grid-cols-4 sm:border-x">
            {h.workflow.map((item, index) => <Reveal key={item.title} delay={index * 0.05}><article className="relative border-b border-background/15 px-4 py-6 last:border-b-0 sm:border-b-0 sm:border-r sm:px-5 sm:last:border-r-0"><span className="font-mono text-micro text-chart-2">0{index + 1}</span><h3 className="mt-8 text-base font-semibold text-background">{item.title}</h3><p className="mt-3 text-sm leading-6 text-background/58">{item.body}</p>{index < h.workflow.length - 1 ? <ArrowRight aria-hidden="true" className="absolute bottom-6 right-4 hidden size-4 text-background/25 sm:block" /> : null}</article></Reveal>)}
          </div>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="textile-title">
        <Container className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <Reveal><div className="relative overflow-hidden rounded-[1.2rem] border"><MarketingEditorialImage asset="homeFloor" alt={tr ? "Boyahane üretim hattı" : "Textile dyehouse production floor"} className="aspect-[16/10]" sizes="(min-width: 1024px) 60vw, 100vw" /><div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/55 via-transparent to-transparent" /><div className="absolute inset-x-5 bottom-5 text-background sm:inset-x-7 sm:bottom-7"><span className="text-lg font-medium">{tr ? "Parti · makine · reçete · termin" : "Batch · machine · recipe · deadline"}</span></div></div></Reveal>
          <Reveal delay={0.08}><h2 id="textile-title" className="text-balance font-display text-4xl sm:text-5xl">{h.textileTitle}</h2><p className="mt-5 max-w-xl leading-7 text-muted-foreground">{h.textileBody}</p><Link className="mt-7 inline-flex min-h-11 items-center gap-2 font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline" href="/solutions/textile-dyehouse">{content.common.learnMore}<ArrowRight className="size-4" aria-hidden="true" /></Link></Reveal>
        </Container>
      </section>

      <section className="border-b bg-muted/25 py-16 sm:py-24" aria-labelledby="trust-title">
        <Container className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <Reveal><div className="flex items-center gap-3 text-sm font-medium"><ShieldCheck className="size-5 text-brand" aria-hidden="true" />{tr ? "Güven ve yönetişim" : "Trust and governance"}</div><h2 id="trust-title" className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.trustTitle}</h2><p className="mt-5 max-w-xl leading-7 text-muted-foreground">{h.trustBody}</p><Link className="mt-7 inline-flex min-h-11 items-center gap-2 font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline" href="/security">{content.common.learnMore}<ArrowRight className="size-4" aria-hidden="true" /></Link></Reveal>
          <Reveal delay={0.08}><div className="relative overflow-hidden rounded-lg border"><MarketingEditorialImage asset="homeTrust" alt={tr ? "Operasyon ekibi kumaş ve analiz notlarını inceliyor" : "Operations team reviewing fabric and analysis notes"} className="aspect-[16/10]" sizes="(min-width: 1024px) 54vw, 100vw" /><div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/60 to-transparent" /><div className="absolute inset-x-5 bottom-5 flex items-center justify-between gap-4 text-background sm:inset-x-6 sm:bottom-6"><span className="font-mono text-micro uppercase tracking-[0.16em] text-chart-2">{tr ? "Sınırlar görünür" : "Boundaries in view"}</span><span className="text-sm font-medium">{tr ? "yalnızca okuma · kaynak · yetki" : "read-only · source · access"}</span></div></div></Reveal>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="integration-title">
        <Container className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <Reveal><div className="relative overflow-hidden rounded-lg border"><MarketingEditorialImage asset="homeConnections" alt={tr ? "Veriyle birlikte çalışan üretim sahası" : "Production floor connected to operational data"} className="aspect-[16/10]" sizes="(min-width: 1024px) 58vw, 100vw" /><div aria-hidden="true" className="absolute inset-0 bg-gradient-to-tr from-foreground/50 via-transparent to-transparent" /><div className="absolute left-5 top-5 rounded-full border border-background/25 bg-background/85 px-3 py-2 font-mono text-micro uppercase tracking-[0.14em] text-foreground sm:left-6 sm:top-6">{tr ? "kaynak → tanım → cevap" : "source → definition → answer"}</div></div></Reveal>
          <Reveal delay={0.08}><div className="flex items-center gap-3 text-sm font-medium"><Database className="size-5 text-brand" aria-hidden="true" />{tr ? "Veri kaynakları" : "Data sources"}</div><h2 id="integration-title" className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.integrationTitle}</h2><p className="mt-5 max-w-xl leading-7 text-muted-foreground">{h.integrationBody}</p><div className="mt-8 flex flex-wrap gap-2 font-mono text-xs text-muted-foreground"><span className="border px-3 py-2">DuckDB / örnek</span><span className="border px-3 py-2">Postgres / doğrulandı</span><span className="border border-dashed px-3 py-2">MSSQL / Oracle / teknik olarak mümkün</span></div><Link className="mt-7 inline-flex min-h-11 items-center gap-2 font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline" href="/integrations">{content.common.learnMore}<ArrowRight className="size-4" aria-hidden="true" /></Link></Reveal>
        </Container>
      </section>

      <section className="py-16 sm:py-24" aria-labelledby="faq-title">
        <Container className="grid gap-10 lg:grid-cols-[0.7fr_1.3fr]"><Reveal><h2 id="faq-title" className="font-display text-4xl sm:text-5xl">{h.faqTitle}</h2></Reveal><Reveal delay={0.06}><Accordion type="single" collapsible className="border-y">{h.faq.map((item, index) => <AccordionItem key={item.question} value={`faq-${index}`}><AccordionTrigger className="min-h-11 py-5 text-left text-base">{item.question}</AccordionTrigger><AccordionContent className="max-w-2xl pb-5 leading-7 text-muted-foreground">{item.answer}</AccordionContent></AccordionItem>)}</Accordion></Reveal></Container>
      </section>
      <FinalCta content={content} asset="homeCta" />
    </>
  );
}
