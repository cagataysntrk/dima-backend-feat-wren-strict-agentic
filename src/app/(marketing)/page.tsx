import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { getLocale } from "next-intl/server";
import { BrandLockup } from "@/components/BrandMark";
import { Container, Eyebrow, FinalCta } from "@/components/marketing/MarketingPrimitives";
import { ProductProof } from "@/components/marketing/ProductProof";
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
  return (
    <>
      <section className="marketing-grid overflow-hidden border-b py-20 sm:py-28 lg:py-32">
        <Container>
          <Eyebrow>{h.eyebrow}</Eyebrow>
          <h1 className="mt-6 max-w-5xl text-balance font-display text-5xl leading-[0.98] tracking-[-0.045em] sm:text-7xl lg:text-[5.8rem]">{h.title}</h1>
          <p className="mt-8 max-w-2xl text-pretty text-lg leading-8 text-muted-foreground sm:text-xl">{h.description}</p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Button asChild variant="brand" size="lg" className="min-h-11"><Link href="/contact">{content.common.demo}<ArrowRight /></Link></Button>
            <Button asChild variant="outline" size="lg" className="min-h-11"><Link href="/product">{content.nav.product}</Link></Button>
          </div>
          <ol className="mt-16 grid border-y sm:grid-cols-2 lg:grid-cols-4">
            {h.process.map((step, index) => (
              <li key={step} className="flex min-h-20 items-center gap-4 border-b px-4 last:border-b-0 sm:border-r sm:nth-[2]:border-r-0 lg:border-b-0 lg:nth-[2]:border-r">
                <span className="font-mono text-xs text-brand">{String(index + 1).padStart(2, "0")}</span>
                <span className="text-sm font-medium">{step}</span>
              </li>
            ))}
          </ol>
        </Container>
      </section>

      <section className="border-b py-20 sm:py-28">
        <Container>
          <div className="mb-10 grid gap-5 md:grid-cols-2 md:items-end">
            <div><Eyebrow>product evidence</Eyebrow><h2 className="mt-4 font-display text-4xl sm:text-5xl">{h.proofTitle}</h2></div>
            <p className="max-w-xl leading-7 text-muted-foreground">{h.proofBody}</p>
          </div>
          <ProductProof locale={content.locale} />
        </Container>
      </section>

      <section className="border-b bg-muted/25 py-20 sm:py-28">
        <Container>
          <div className="max-w-3xl"><Eyebrow>D · I · M · A</Eyebrow><h2 className="mt-4 text-balance font-display text-4xl sm:text-5xl">{h.pillarsTitle}</h2><p className="mt-5 leading-7 text-muted-foreground">{h.pillarsBody}</p></div>
          <div className="mt-12"><BrandLockup locale={content.locale} /></div>
        </Container>
      </section>

      <section className="border-b py-20 sm:py-28">
        <Container>
          <Eyebrow>workflow</Eyebrow><h2 className="mt-4 font-display text-4xl sm:text-5xl">{h.workflowTitle}</h2>
          <div className="mt-12 grid gap-px overflow-hidden rounded-lg border bg-border md:grid-cols-2 lg:grid-cols-4">
            {h.workflow.map((item, index) => (
              <article key={item.title} className="bg-background p-6 sm:p-8">
                <span className="font-mono text-xs text-brand">{String(index + 1).padStart(2, "0")}</span>
                <h3 className="mt-8 text-xl font-semibold">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.body}</p>
              </article>
            ))}
          </div>
        </Container>
      </section>

      <section className="border-b py-20 sm:py-28">
        <Container>
          <Eyebrow>use cases</Eyebrow><h2 className="mt-4 font-display text-4xl sm:text-5xl">{h.useCasesTitle}</h2>
          <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {h.useCases.map((item) => <article key={item.title} className="rounded-lg border p-6 transition-colors hover:border-brand/50"><p className="font-mono text-xs uppercase tracking-wider text-brand">{item.title}</p><h3 className="mt-5 text-lg font-medium leading-7">“{item.question}”</h3></article>)}
          </div>
        </Container>
      </section>

      <EditorialFeature eyebrow="textile / dyehouse" title={h.textileTitle} body={h.textileBody} href="/solutions/textile-dyehouse" content={content} />
      <EditorialFeature eyebrow="security / governance" title={h.trustTitle} body={h.trustBody} href="/security" content={content} reverse />
      <EditorialFeature eyebrow="integrations / deployment" title={h.integrationTitle} body={h.integrationBody} href="/integrations" content={content} />

      <section className="border-t py-20 sm:py-28">
        <Container className="grid gap-10 lg:grid-cols-[0.7fr_1.3fr]">
          <div><Eyebrow>FAQ</Eyebrow><h2 className="mt-4 font-display text-4xl">{h.faqTitle}</h2></div>
          <div className="divide-y border-y">
            {h.faq.map((item) => <details key={item.question} className="group py-5"><summary className="cursor-pointer list-none pr-8 font-medium marker:hidden">{item.question}<span className="float-right text-brand group-open:rotate-45">+</span></summary><p className="mt-4 max-w-2xl text-sm leading-7 text-muted-foreground">{item.answer}</p></details>)}
          </div>
        </Container>
      </section>
      <FinalCta content={content} />
    </>
  );
}

function EditorialFeature({ eyebrow, title, body, href, content, reverse = false }: { eyebrow: string; title: string; body: string; href: string; content: ReturnType<typeof getMarketingContent>; reverse?: boolean }) {
  return (
    <section className="border-b py-20 sm:py-28">
      <Container className={`grid gap-10 lg:grid-cols-2 lg:items-center ${reverse ? "lg:[&>*:first-child]:order-2" : ""}`}>
        <div><Eyebrow>{eyebrow}</Eyebrow><h2 className="mt-4 text-balance font-display text-4xl sm:text-5xl">{title}</h2><p className="mt-5 max-w-xl leading-7 text-muted-foreground">{body}</p><Link href={href} className="mt-7 inline-flex items-center gap-2 text-sm font-semibold text-brand hover:underline">{content.common.learnMore}<ArrowRight className="size-4" /></Link></div>
        <div aria-hidden="true" className="marketing-grid flex aspect-[4/3] items-center justify-center rounded-xl border bg-muted/30 p-10"><div className="w-full max-w-sm space-y-3">{[78, 54, 86, 64].map((width, i) => <div key={width} className="flex items-center gap-4"><Check className="size-4 text-brand" /><div className="h-2 flex-1 rounded-full bg-border"><div className="h-full rounded-full bg-brand/70" style={{ width: `${width}%` }} /></div><span className="font-mono text-[10px] text-muted-foreground">0{i + 1}</span></div>)}</div></div>
      </Container>
    </section>
  );
}
