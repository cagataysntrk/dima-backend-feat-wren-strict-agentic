import { Container, Eyebrow } from "@/components/marketing/MarketingPrimitives";
import type { MarketingContent, PageContent } from "@/content/marketing";

export function LegalPage({ page, content }: { page: PageContent; content: MarketingContent }) {
  return (
    <>
      <section className="marketing-grid border-b py-20 sm:py-28">
        <Container>
          <Eyebrow>{page.eyebrow}</Eyebrow>
          <h1 className="mt-5 max-w-4xl text-balance font-display text-5xl leading-tight sm:text-6xl">{page.title}</h1>
          <p className="mt-6 max-w-2xl leading-7 text-muted-foreground">{page.description}</p>
          <p className="mt-6 font-mono text-xs uppercase tracking-wider text-muted-foreground">{content.legal.lastUpdated}</p>
        </Container>
      </section>
      <Container className="py-16 sm:py-24">
        <aside className="mb-12 border-l-2 border-brand bg-muted/40 p-5 text-sm leading-6 text-muted-foreground">{content.legal.notice}</aside>
        <div className="grid gap-12 lg:grid-cols-[240px_1fr]">
          <nav aria-label={page.eyebrow} className="hidden lg:block"><ol className="sticky top-24 space-y-2 text-sm text-muted-foreground">{page.sections.map((section) => <li key={section.id}><a className="hover:text-foreground hover:underline focus-visible:text-foreground focus-visible:underline" href={`#${section.id}`}>{section.title}</a></li>)}</ol></nav>
          <div className="divide-y border-y">
            {page.sections.map((section) => <section className="scroll-mt-24 py-8" id={section.id} key={section.id}><h2 className="text-xl font-semibold tracking-tight">{section.title}</h2><p className="mt-4 max-w-3xl leading-7 text-muted-foreground">{section.body}</p></section>)}
          </div>
        </div>
      </Container>
    </>
  );
}
