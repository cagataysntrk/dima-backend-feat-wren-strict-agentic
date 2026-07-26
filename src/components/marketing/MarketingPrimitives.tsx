import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { CapabilityStatus, MarketingContent, PageContent } from "@/content/marketing";

export function Container({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`mx-auto max-w-7xl px-5 sm:px-8 ${className}`}>{children}</div>;
}

export function Eyebrow({ children }: { children: React.ReactNode }) {
  return <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-brand">{children}</p>;
}

export function PageHero({ page }: { page: PageContent }) {
  return (
    <section className="marketing-grid border-b py-20 sm:py-28">
      <Container>
        <Eyebrow>{page.eyebrow}</Eyebrow>
        <h1 className="mt-5 max-w-4xl text-balance font-display text-5xl leading-[1.03] tracking-[-0.035em] sm:text-6xl lg:text-7xl">{page.title}</h1>
        <p className="mt-7 max-w-2xl text-pretty text-lg leading-8 text-muted-foreground">{page.description}</p>
      </Container>
    </section>
  );
}

export function StatusBadge({ status, content }: { status?: CapabilityStatus; content: MarketingContent }) {
  if (!status) return null;
  return (
    <span className="inline-flex rounded-full border px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
      {content.common[status]}
    </span>
  );
}

export function DetailPage({ page, content }: { page: PageContent; content: MarketingContent }) {
  return (
    <>
      <PageHero page={page} />
      <Container className="py-16 sm:py-24">
        <div className="divide-y border-y">
          {page.sections.map((section, index) => (
            <article key={section.id} id={section.id} className="grid gap-6 py-10 md:grid-cols-[72px_1fr_1.4fr] md:gap-10 md:py-14">
              <span className="font-mono text-xs text-brand">{String(index + 1).padStart(2, "0")}</span>
              <div>
                <StatusBadge status={section.status} content={content} />
                <h2 className="mt-3 text-balance text-2xl font-semibold tracking-tight">{section.title}</h2>
              </div>
              <div>
                <p className="leading-7 text-muted-foreground">{section.body}</p>
                {section.points && (
                  <ul className="mt-5 grid gap-2">
                    {section.points.map((point) => (
                      <li key={point} className="flex gap-3 text-sm"><Check className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden="true" />{point}</li>
                    ))}
                  </ul>
                )}
              </div>
            </article>
          ))}
        </div>
      </Container>
      <FinalCta content={content} label={page.cta} />
    </>
  );
}

export function FinalCta({ content, label }: { content: MarketingContent; label?: string }) {
  return (
    <section className="border-t bg-foreground py-16 text-background sm:py-20">
      <Container className="flex flex-col items-start justify-between gap-8 md:flex-row md:items-end">
        <div>
          <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-background/80">{content.common.demo}</p>
          <h2 className="mt-4 max-w-2xl font-display text-4xl leading-tight sm:text-5xl">{content.common.finalTitle}</h2>
          <p className="mt-4 max-w-xl text-background/70">{content.common.finalBody}</p>
        </div>
        <Button asChild variant="brand" size="lg" className="min-h-11 max-w-full whitespace-normal text-center">
          <Link href="/contact">{label ?? content.common.demo}<ArrowRight aria-hidden="true" /></Link>
        </Button>
      </Container>
    </section>
  );
}
