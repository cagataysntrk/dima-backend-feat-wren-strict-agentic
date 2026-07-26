import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  Braces,
  CheckCircle2,
  GitBranch,
  Search,
  ShieldCheck,
} from "lucide-react";
import { getLocale } from "next-intl/server";
import {
  BentoGrid,
  BorderBeam,
  MagicCard,
  Marquee,
  Particles,
  ProgressiveBlur,
  WordRotate,
} from "@/components/marketing/MagicUI";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import {
  Float,
  Reveal,
  Stagger,
  StaggerItem,
} from "@/components/marketing/MarketingMotion";
import { Container, Eyebrow, FinalCta } from "@/components/marketing/MarketingPrimitives";
import { ProductProof } from "@/components/marketing/ProductProof";
import {
  IntegrationFlowVisual,
  MiniSignal,
  ProductWorkbenchVisual,
  SecurityFlowVisual,
  SemanticMapVisual,
  ValidationPipelineVisual,
  WorkflowPipeline,
} from "@/components/marketing/VisualAssets";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { getMarketingContent } from "@/content/marketing";

export async function generateMetadata(): Promise<Metadata> {
  const content = getMarketingContent(await getLocale());
  return {
    title: { absolute: `dima — ${content.home.eyebrow}` },
    description: content.home.description,
    alternates: { canonical: "/" },
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
        <Particles className="hidden opacity-70 sm:block" quantity={38} />
        <Container className="relative grid min-h-[calc(100svh-4rem)] gap-12 py-16 lg:grid-cols-[0.9fr_1.1fr] lg:items-center lg:py-20">
          <Reveal className="relative z-10">
            <Eyebrow>{h.eyebrow}</Eyebrow>
            <h1 className="mt-6 max-w-3xl text-balance font-display text-5xl leading-[0.96] tracking-[-0.045em] sm:text-7xl lg:text-[5.15rem]">
              {h.title}
              <br />
              <WordRotate className="text-brand" words={h.rotateWords} />
            </h1>
            <p className="mt-7 max-w-xl text-pretty text-lg leading-8 text-muted-foreground">
              {h.description}
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Button asChild variant="brand" size="lg" className="min-h-11">
                <Link href="/contact">
                  {content.common.demo}
                  <ArrowRight aria-hidden="true" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="min-h-11">
                <Link href="/product">{content.nav.product}</Link>
              </Button>
            </div>
            <div className="mt-12 grid max-w-xl grid-cols-2 gap-px overflow-hidden rounded-lg border bg-border sm:grid-cols-4">
              {h.process.map((step, index) => (
                <div className="group bg-background px-3 py-4 transition-colors duration-300 hover:bg-brand/5" key={step}>
                  <span className="font-mono text-[9px] tabular-nums text-brand">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <p className="mt-2 text-xs font-medium leading-5 transition-transform duration-300 group-hover:translate-x-0.5">{step}</p>
                </div>
              ))}
            </div>
          </Reveal>

          <Reveal delay={0.12} y={18} className="relative">
            <div className="relative aspect-[4/3] overflow-hidden rounded-[1.15rem] border bg-card shadow-xl">
              <BorderBeam duration={9} />
              <MarketingEditorialImage
                asset="hero"
                className="marketing-editorial-image"
                priority
                sizes="(min-width: 1024px) 54vw, 100vw"
              />
              <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/35 via-transparent to-transparent" />
              <ProgressiveBlur />
            </div>
            <Float className="absolute -left-3 top-[12%] sm:-left-8" distance={7}>
              <EvidenceChip icon={Braces} label={tr ? "Ortak iş tanımları" : "Shared business definitions"} meta={tr ? "tanımlar / hazır" : "definitions / ready"} />
            </Float>
            <Float className="absolute -right-2 bottom-[28%] sm:-right-7" distance={6} duration={6.3} delay={0.4}>
              <EvidenceChip icon={ShieldCheck} label={tr ? "Ön kontroller tamam" : "Pre-checks complete"} meta={tr ? "güvenli / hazır" : "safe / ready"} />
            </Float>
            <Float className="absolute bottom-4 left-[8%] sm:bottom-6" distance={5} duration={6.8} delay={0.8}>
              <EvidenceChip icon={GitBranch} label={tr ? "Cevabın kaynağı görünür" : "Answer source visible"} meta={tr ? "kaynak / bağlı" : "source / linked"} />
            </Float>
          </Reveal>
        </Container>
      </section>

      <section className="relative overflow-hidden border-b bg-muted/20 py-8">
        <div aria-hidden="true" className="pointer-events-none absolute inset-y-0 left-0 z-10 w-20 bg-gradient-to-r from-background to-transparent sm:w-36" />
        <div aria-hidden="true" className="pointer-events-none absolute inset-y-0 right-0 z-10 w-20 bg-gradient-to-l from-background to-transparent sm:w-36" />
        <Marquee className="[--duration:36s] [--gap:0.75rem]">
          {h.useCases.map((item) => (
            <div className="group flex w-80 shrink-0 items-start gap-3 rounded-xl border bg-card/90 p-4 shadow-sm transition-[border-color,transform] duration-300 hover:-translate-y-1 hover:border-brand/35" key={`${item.title}-${item.question}`}>
              <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-brand/10 text-brand">
                <Search className="size-3.5" aria-hidden="true" />
              </span>
              <span>
                <span className="block text-[10px] font-semibold text-brand">{item.title}</span>
                <span className="mt-1 block text-sm leading-5">{item.question}</span>
              </span>
            </div>
          ))}
        </Marquee>
      </section>

      <section className="border-b py-18 sm:py-24">
        <Container>
          <Reveal className="grid gap-5 md:grid-cols-[0.9fr_1.1fr] md:items-end">
            <div>
              <Eyebrow>{tr ? "Ürün içinde görün" : "See it in the product"}</Eyebrow>
              <h2 className="mt-4 max-w-2xl text-balance font-display text-4xl leading-tight sm:text-5xl">
                {h.proofTitle}
              </h2>
            </div>
            <p className="max-w-xl leading-7 text-muted-foreground">{h.proofBody}</p>
          </Reveal>
          <Reveal className="mt-10" delay={0.08}>
            <ProductProof locale={content.locale} />
          </Reveal>
        </Container>
      </section>

      <section className="border-b bg-muted/20 py-18 sm:py-24">
        <Container>
          <Reveal className="max-w-3xl">
            <Eyebrow>{tr ? "Bir cevabın içinde ne var?" : "What is inside an answer?"}</Eyebrow>
            <h2 className="mt-4 text-balance font-display text-4xl sm:text-5xl">
              {tr
                ? "Soru, kontrol ve sonuç birbirinden kopuk kalmaz."
                : "The question, checks, and result stay connected."}
            </h2>
          </Reveal>
          <Stagger className="mt-12">
            <BentoGrid>
            <StaggerItem className="min-h-0 md:col-span-4 md:row-span-2">
              <div className="h-full [&>figure]:h-full">
                <ProductWorkbenchVisual locale={content.locale} />
              </div>
            </StaggerItem>
            <StaggerItem className="md:col-span-2">
              <SignalCard
                icon={Search}
                title={tr ? "Soru doğru tanımlarla eşleşir" : "The question matches the right definitions"}
                body={tr ? "Brüt kâr, ürün grubu ve dönem aynı anlamda buluşur." : "Gross margin, product group, and period meet in one shared meaning."}
              >
                <MiniSignal index={1} />
              </SignalCard>
            </StaggerItem>
            <StaggerItem className="md:col-span-2">
              <SignalCard
                icon={CheckCircle2}
                title={tr ? "Her kontrol görünür kalır" : "Every check stays visible"}
                body={tr ? "Yalnızca okuma, ön kontrol ve cevap kaynağı tek akışta görünür." : "Read-only access, pre-checks, and the answer source share one flow."}
              >
                <MiniSignal index={4} />
              </SignalCard>
            </StaggerItem>
            <StaggerItem className="md:col-span-3">
              <div className="h-full overflow-hidden rounded-xl [&>figure]:h-full">
                <SemanticMapVisual locale={content.locale} />
              </div>
            </StaggerItem>
            <StaggerItem className="md:col-span-3">
              <div className="h-full overflow-hidden rounded-xl [&>figure]:h-full">
                <ValidationPipelineVisual locale={content.locale} />
              </div>
            </StaggerItem>
            </BentoGrid>
          </Stagger>
        </Container>
      </section>

      <section className="border-b py-18 sm:py-24">
        <Container>
          <Reveal>
            <Eyebrow>{tr ? "Sorudan rapora" : "Question to report"}</Eyebrow>
            <h2 className="mt-4 max-w-3xl text-balance font-display text-4xl sm:text-5xl">
              {h.workflowTitle}
            </h2>
          </Reveal>
          <Reveal delay={0.08}>
            <WorkflowPipeline items={h.workflow} />
          </Reveal>
        </Container>
      </section>

      <EditorialFeature
        eyebrow={tr ? "Ekiplerin ortak dili" : "One language for every team"}
        title={h.operationsTitle}
        body={h.operationsBody}
        href="/solutions"
        content={content}
        visual={
          <div className="relative aspect-[16/10] overflow-hidden rounded-xl border shadow-xl">
            <MarketingEditorialImage asset="decisions" className="marketing-editorial-image" />
          </div>
        }
      />
      <EditorialFeature
        eyebrow={tr ? "Her istekte güven" : "Protection on every request"}
        title={h.trustTitle}
        body={h.trustBody}
        href="/security"
        content={content}
        visual={<SecurityFlowVisual locale={content.locale} />}
        reverse
      />
      <EditorialFeature
        eyebrow={tr ? "Kaynaklardan rapora" : "Sources to reports"}
        title={h.integrationTitle}
        body={h.integrationBody}
        href="/integrations"
        content={content}
        visual={<IntegrationFlowVisual locale={content.locale} />}
      />

      <section className="border-t py-18 sm:py-24">
        <Container className="grid gap-10 lg:grid-cols-[0.7fr_1.3fr]">
          <Reveal>
            <Eyebrow>FAQ</Eyebrow>
            <h2 className="mt-4 font-display text-4xl">{h.faqTitle}</h2>
          </Reveal>
          <Reveal delay={0.06}>
            <Accordion type="single" collapsible className="border-y">
              {h.faq.map((item, index) => (
                <AccordionItem key={item.question} value={`faq-${index}`}>
                  <AccordionTrigger className="py-5 text-base">{item.question}</AccordionTrigger>
                  <AccordionContent className="max-w-2xl pb-5 leading-7 text-muted-foreground">
                    {item.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </Reveal>
        </Container>
      </section>
      <FinalCta content={content} />
    </>
  );
}

function EvidenceChip({
  icon: Icon,
  label,
  meta,
}: {
  icon: typeof Braces;
  label: string;
  meta: string;
}) {
  return (
    <div className="marketing-surface flex min-w-44 items-center gap-3 rounded-lg border bg-card/95 px-3 py-3 shadow-lg backdrop-blur-sm">
      <span className="flex size-8 shrink-0 items-center justify-center rounded-md border bg-background text-brand">
        <Icon className="size-4" aria-hidden="true" />
      </span>
      <span>
        <span className="block text-[11px] font-semibold">{label}</span>
        <span className="mt-1 block font-mono text-[8px] text-muted-foreground">{meta}</span>
      </span>
    </div>
  );
}

function SignalCard({
  icon: Icon,
  title,
  body,
  children,
}: {
  icon: typeof Search;
  title: string;
  body: string;
  children: React.ReactNode;
}) {
  return (
    <MagicCard className="h-full p-5">
      <div className="flex items-center gap-2">
        <Icon className="size-4 text-brand" aria-hidden="true" />
        <h3 className="text-sm font-semibold">{title}</h3>
      </div>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{body}</p>
      {children}
    </MagicCard>
  );
}

function EditorialFeature({
  eyebrow,
  title,
  body,
  href,
  content,
  visual,
  reverse = false,
}: {
  eyebrow: string;
  title: string;
  body: string;
  href: string;
  content: ReturnType<typeof getMarketingContent>;
  visual: React.ReactNode;
  reverse?: boolean;
}) {
  return (
    <section className="border-b py-18 sm:py-24">
      <Container className={`grid gap-10 lg:grid-cols-2 lg:items-center ${reverse ? "lg:[&>*:first-child]:order-2" : ""}`}>
        <Reveal>
          <Eyebrow>{eyebrow}</Eyebrow>
          <h2 className="mt-4 text-balance font-display text-4xl sm:text-5xl">{title}</h2>
          <p className="mt-5 max-w-xl leading-7 text-muted-foreground">{body}</p>
          <Link href={href} className="mt-7 inline-flex items-center gap-2 text-sm font-semibold text-brand underline-offset-4 hover:underline focus-visible:underline">
            {content.common.learnMore}
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </Reveal>
        <Reveal delay={0.08}>{visual}</Reveal>
      </Container>
    </section>
  );
}
