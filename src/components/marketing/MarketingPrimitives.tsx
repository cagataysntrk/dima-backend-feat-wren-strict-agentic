import Link from "next/link";
import { ArrowRight } from "lucide-react";
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
