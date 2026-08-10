import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Database, Search, ShieldCheck } from "lucide-react";
import { getLocale } from "next-intl/server";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Container, Eyebrow, FinalCta } from "@/components/marketing/MarketingPrimitives";
import { ProductProof } from "@/components/marketing/ProductProof";
import { IntegrationFlowVisual, SecurityFlowVisual, WorkflowPipeline } from "@/components/marketing/VisualAssets";
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
      <section className="relative overflow-hidden border-b">
        <div aria-hidden="true" className="marketing-grid absolute inset-0 opacity-45 [mask-image:linear-gradient(to_bottom,black,transparent_88%)]" />
        <Container className="relative grid gap-12 py-20 sm:py-28 lg:grid-cols-[0.92fr_1.08fr] lg:items-center">
          <Reveal>
            <Eyebrow>{h.eyebrow}</Eyebrow>
            <h1 className="mt-6 max-w-3xl text-balance font-display text-5xl leading-[0.98] tracking-[-0.045em] sm:text-6xl lg:text-7xl">{h.title}</h1>
            <p className="mt-7 max-w-xl text-pretty text-lg leading-8 text-muted-foreground">{h.description}</p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Button asChild variant="brand" size="lg" className="min-h-11"><Link href="/contact">{content.common.demo}<ArrowRight aria-hidden="true" /></Link></Button>
              <Button asChild variant="outline" size="lg" className="min-h-11"><Link href="/product">{content.nav.product}</Link></Button>
            </div>
            <ol aria-label={tr ? "Dima akışı" : "Dima flow"} className="mt-12 grid max-w-xl grid-cols-2 gap-px overflow-hidden rounded-lg border bg-border sm:grid-cols-4">
              {h.process.map((step, index) => <li className="bg-background px-3 py-4" key={step}><span className="font-mono text-micro tabular-nums text-brand">{String(index + 1).padStart(2, "0")}</span><p className="mt-2 text-xs font-medium leading-5">{step}</p></li>)}
            </ol>
          </Reveal>
          <Reveal delay={0.08} y={18}>
            <figure className="relative overflow-hidden rounded-[1.15rem] border bg-card shadow-xl">
              <MarketingEditorialImage asset="hero" className="marketing-editorial-image aspect-[4/3]" priority sizes="(min-width: 1024px) 54vw, 100vw" />
              <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/40 via-transparent to-transparent" />
              <figcaption className="absolute inset-x-4 bottom-4 rounded-lg border border-background/20 bg-background/90 p-4 text-sm shadow-lg backdrop-blur-sm sm:inset-x-6 sm:bottom-6">
                <span className="font-mono text-micro uppercase tracking-[0.16em] text-brand">{tr ? "Cevap izi" : "Answer trace"}</span>
                <span className="mt-2 block font-medium">{tr ? "Tanım → kontrol → sonuç → kaynak" : "Definition → check → result → source"}</span>
              </figcaption>
            </figure>
          </Reveal>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="proof-title">
        <Container>
          <Reveal className="grid gap-5 md:grid-cols-[0.9fr_1.1fr] md:items-end">
            <div><Eyebrow>{tr ? "İlk kanıt" : "The first proof"}</Eyebrow><h2 id="proof-title" className="mt-4 max-w-2xl text-balance font-display text-4xl leading-tight sm:text-5xl">{h.proofTitle}</h2></div>
            <p className="max-w-xl leading-7 text-muted-foreground">{h.proofBody}</p>
          </Reveal>
          <Reveal className="mt-10" delay={0.08}><ProductProof locale={content.locale} /></Reveal>
        </Container>
      </section>

      <section className="border-b bg-muted/20 py-16 sm:py-24" aria-labelledby="pillars-title">
        <Container>
          <Reveal className="max-w-3xl"><Eyebrow>{tr ? "D-I-M-A" : "D-I-M-A"}</Eyebrow><h2 id="pillars-title" className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.pillarsTitle}</h2><p className="mt-5 max-w-2xl leading-7 text-muted-foreground">{h.pillarsBody}</p></Reveal>
          <div className="mt-12 grid gap-px overflow-hidden rounded-xl border bg-border sm:grid-cols-2 lg:grid-cols-4">
            {h.pillars.map((pillar) => <article className="bg-background p-5 sm:p-6" key={pillar.letter}><span className="font-display text-5xl leading-none text-brand">{pillar.letter}</span><h3 className="mt-8 text-lg font-semibold">{pillar.title}</h3><p className="mt-3 text-sm leading-6 text-muted-foreground">{pillar.body}</p></article>)}
          </div>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="questions-title">
        <Container>
          <Reveal><Eyebrow>{tr ? "Gerçek sorular" : "Real questions"}</Eyebrow><h2 id="questions-title" className="mt-4 max-w-3xl text-balance font-display text-4xl sm:text-5xl">{h.useCasesTitle}</h2></Reveal>
          <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {h.useCases.map((item) => <article className="rounded-xl border bg-card p-5 transition-colors duration-200 hover:border-brand/40" key={`${item.title}-${item.question}`}><div className="flex items-center gap-2 text-xs font-semibold text-brand"><Search className="size-4" aria-hidden="true" />{item.title}</div><p className="mt-4 leading-6">{item.question}</p></article>)}
          </div>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="workflow-title">
        <Container>
          <Reveal><Eyebrow>{tr ? "Sorudan rapora" : "Question to report"}</Eyebrow><h2 id="workflow-title" className="mt-4 max-w-3xl text-balance font-display text-4xl sm:text-5xl">{h.workflowTitle}</h2></Reveal>
          <Reveal delay={0.08}><WorkflowPipeline items={h.workflow} /></Reveal>
        </Container>
      </section>

      <section className="border-b bg-muted/20 py-16 sm:py-24" aria-labelledby="textile-title">
        <Container className="grid gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
          <Reveal><Eyebrow>{tr ? "Odaklı kullanım alanı" : "Focused use case"}</Eyebrow><h2 id="textile-title" className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.textileTitle}</h2><p className="mt-5 max-w-xl leading-7 text-muted-foreground">{h.textileBody}</p><Link className="mt-7 inline-flex min-h-11 items-center gap-2 font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline" href="/solutions/textile-dyehouse">{content.common.learnMore}<ArrowRight className="size-4" aria-hidden="true" /></Link></Reveal>
          <Reveal delay={0.08}><div className="relative overflow-hidden rounded-xl border shadow-lg"><MarketingEditorialImage asset="decisions" className="marketing-editorial-image aspect-[16/10]" /><div className="absolute inset-x-4 bottom-4 rounded-lg border border-background/20 bg-background/90 p-4 text-sm shadow-lg backdrop-blur-sm sm:inset-x-6 sm:bottom-6"><span className="font-mono text-micro uppercase tracking-[0.16em] text-brand">{tr ? "Sanitized demo" : "Sanitized demo"}</span><span className="mt-2 block font-medium">{tr ? "OEE · fire · reçete · termin" : "OEE · waste · recipe · deadline"}</span></div></div></Reveal>
        </Container>
      </section>

      <section className="border-b py-16 sm:py-24" aria-labelledby="trust-title">
        <Container className="grid gap-8 lg:grid-cols-2">
          <Reveal><div className="flex items-center gap-3"><ShieldCheck className="size-5 text-brand" aria-hidden="true" /><Eyebrow>{tr ? "Güven ve yönetişim" : "Trust and governance"}</Eyebrow></div><h2 id="trust-title" className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.trustTitle}</h2><p className="mt-5 max-w-xl leading-7 text-muted-foreground">{h.trustBody}</p><Link className="mt-7 inline-flex min-h-11 items-center gap-2 font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline" href="/security">{content.common.learnMore}<ArrowRight className="size-4" aria-hidden="true" /></Link></Reveal>
          <Reveal delay={0.08}><div className="rounded-xl border bg-card p-2"><SecurityFlowVisual locale={content.locale} /></div></Reveal>
        </Container>
      </section>

      <section className="border-b bg-muted/20 py-16 sm:py-24" aria-labelledby="integration-title">
        <Container className="grid gap-8 lg:grid-cols-2 lg:items-center">
          <Reveal><div className="rounded-xl border bg-card p-2"><IntegrationFlowVisual locale={content.locale} /></div></Reveal>
          <Reveal delay={0.08}><div className="flex items-center gap-3"><Database className="size-5 text-brand" aria-hidden="true" /><Eyebrow>{tr ? "Veri kaynakları" : "Data sources"}</Eyebrow></div><h2 id="integration-title" className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.integrationTitle}</h2><p className="mt-5 max-w-xl leading-7 text-muted-foreground">{h.integrationBody}</p><Link className="mt-7 inline-flex min-h-11 items-center gap-2 font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline" href="/integrations">{content.common.learnMore}<ArrowRight className="size-4" aria-hidden="true" /></Link></Reveal>
        </Container>
      </section>

      <section className="py-16 sm:py-24" aria-labelledby="faq-title">
        <Container className="grid gap-10 lg:grid-cols-[0.7fr_1.3fr]"><Reveal><Eyebrow>FAQ</Eyebrow><h2 id="faq-title" className="mt-4 font-display text-4xl sm:text-5xl">{h.faqTitle}</h2></Reveal><Reveal delay={0.06}><Accordion type="single" collapsible className="border-y">{h.faq.map((item, index) => <AccordionItem key={item.question} value={`faq-${index}`}><AccordionTrigger className="min-h-11 py-5 text-left text-base">{item.question}</AccordionTrigger><AccordionContent className="max-w-2xl pb-5 leading-7 text-muted-foreground">{item.answer}</AccordionContent></AccordionItem>)}</Accordion></Reveal></Container>
      </section>
      <FinalCta content={content} />
    </>
  );
}
