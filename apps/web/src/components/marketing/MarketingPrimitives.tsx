import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Button } from "@/components/ui/button";
import type { CapabilityStatus, MarketingContent, PageContent } from "@/content/marketing";
import { cn } from "@/lib/utils";

export function Container({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("mx-auto max-w-7xl px-5 sm:px-8", className)}>{children}</div>;
}

/**
 * Kart/tile iç düzeni: üstte meta satırı, altta `mt-auto` ile tabana sabitlenen
 * içerik. Bu şekil marketing yüzeyinde defalarca tekrar ediyordu ve her seferinde
 * `mt-6/7/8/10/16` gibi sihirli bir boşlukla taklit ediliyordu — o sayılar hizalama
 * YAPMIYOR: bir hücrenin başlığı iki satıra sarıp komşusununki sarmayınca meta
 * satırları kayıyordu. `mt-auto` gerçekten alttan hizalar.
 */
export function TileBody({
  top,
  className,
  children,
}: {
  top?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("flex h-full min-h-0 flex-col gap-3", className)}>
      {top ? <div className="flex items-start justify-between gap-2">{top}</div> : null}
      <div className="mt-auto min-w-0">{children}</div>
    </div>
  );
}

export function Eyebrow({ children }: { children: React.ReactNode }) {
  return <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-brand">{children}</p>;
}

export function PageHero({ page, media }: { page: PageContent; media?: React.ReactNode }) {
  return (
    <section className="relative overflow-hidden border-b py-20 sm:py-28">
      <div aria-hidden="true" className="marketing-grid absolute inset-0 opacity-60 [mask-image:linear-gradient(to_bottom,black,transparent)]" />
      <Container className={cn("relative grid gap-12", media ? "lg:grid-cols-[0.88fr_1.12fr] lg:items-center" : "")}>
        <Reveal>
          <Eyebrow>{page.eyebrow}</Eyebrow>
          <h1 className="mt-5 max-w-4xl text-balance font-display text-5xl leading-[1.02] tracking-[-0.04em] sm:text-6xl lg:text-7xl">{page.title}</h1>
          <p className="mt-7 max-w-2xl text-pretty text-lg leading-8 text-muted-foreground">{page.description}</p>
        </Reveal>
        {media ? <Reveal delay={0.12} y={16}>{media}</Reveal> : null}
      </Container>
    </section>
  );
}

export function StatusBadge({ status, content }: { status?: CapabilityStatus; content: MarketingContent }) {
  if (!status) return null;
  return (
    <span className="inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 font-mono text-micro uppercase tracking-wider text-muted-foreground">
      {content.common[status]}
    </span>
  );
}

export function FinalCta({ content, label }: { content: MarketingContent; label?: string }) {
  return (
    <section className="relative overflow-hidden border-t bg-foreground py-16 text-background sm:py-24">
      <Container className="relative z-10 flex flex-col items-start justify-between gap-8 md:flex-row md:items-end">
        <div>
          <p className="font-mono text-xs font-medium tracking-[0.12em] text-background/80">{content.common.demo}</p>
          <h2 className="mt-4 max-w-2xl font-display text-4xl leading-tight sm:text-5xl">{content.common.finalTitle}</h2>
          <p className="mt-4 max-w-xl text-background/70">{content.common.finalBody}</p>
        </div>
        <Button asChild variant="brand" size="lg" className="min-h-11 max-w-full overflow-hidden whitespace-normal text-center shadow-lg transition-[transform,box-shadow] duration-200 hover:-translate-y-0.5 hover:shadow-xl focus-visible:-translate-y-0.5 focus-visible:shadow-xl">
          <Link href="/contact">{label ?? content.common.demo}<ArrowRight aria-hidden="true" /></Link>
        </Button>
      </Container>
    </section>
  );
}
