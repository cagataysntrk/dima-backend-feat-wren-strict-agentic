import type { Metadata } from "next";
import { ArrowDown, Braces, Database, Mail, MessageSquareText } from "lucide-react";
import { getLocale } from "next-intl/server";
import { ContactForm } from "@/components/marketing/ContactForm";
import { AnimatedList, MagicCard } from "@/components/marketing/MagicUI";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Container, Eyebrow, TileBody } from "@/components/marketing/MarketingPrimitives";
import { getMarketingContent } from "@/content/marketing";

export async function generateMetadata(): Promise<Metadata> {
  const tr = getMarketingContent(await getLocale()).locale === "tr";
  return {
    title: tr ? "Demo talep et" : "Request a demo",
    description: tr ? "dima ürününü kendi veri ve rapor ihtiyacınızla değerlendirin." : "Evaluate dima with your own data and reporting need.",
    alternates: { canonical: "/contact" },
    openGraph: {
      title: tr ? "Demo talep et" : "Request a demo",
      description: tr ? "dima ürününü kendi veri ve rapor ihtiyacınızla değerlendirin." : "Evaluate dima with your own data and reporting need.",
      url: "/contact",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: tr ? "Demo talep et" : "Request a demo",
      description: tr ? "dima ürününü kendi veri ve rapor ihtiyacınızla değerlendirin." : "Evaluate dima with your own data and reporting need.",
    },
  };
}
export default async function ContactPage() {
  const content = getMarketingContent(await getLocale());
  const tr = content.locale === "tr";
  return (
    <section className="relative overflow-hidden py-20 sm:py-28">
      <div aria-hidden="true" className="marketing-grid absolute inset-0 opacity-45 [mask-image:linear-gradient(to_bottom,black,transparent)]" />
      <Container className="relative grid gap-12 lg:grid-cols-[0.92fr_1.08fr] lg:items-start">
        <Reveal>
          <Eyebrow>{tr ? "İletişim" : "Contact"}</Eyebrow>
          <h1 className="mt-5 text-balance font-display text-5xl leading-[1.02] tracking-[-0.04em] sm:text-6xl">{tr ? "Gerçek bir iş sorusuyla tanışalım." : "Let’s meet through a real business question."}</h1>
          <p className="mt-6 max-w-lg text-lg leading-8 text-muted-foreground">{tr ? "Veri kaynağınızı, mevcut rapor akışınızı ve yanıtlamak istediğiniz ilk soruyu paylaşın." : "Tell us about your data source, reporting flow, and the first question you want to answer."}</p>
          <a className="mt-8 inline-flex items-center gap-2 text-sm underline-offset-4 hover:underline focus-visible:underline" href="mailto:contact@upcytech.com"><Mail className="size-4 shrink-0 text-brand" /><span className="break-anywhere">contact@upcytech.com</span></a>
          <div className="relative mt-10 aspect-[16/10] overflow-hidden rounded-xl border shadow-lg">
            <MarketingEditorialImage asset="archive" className="marketing-editorial-image" priority />
            <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/20 to-transparent" />
          </div>
          <MagicCard className="@container/tile mt-12" tilt={false}>
            <p className="border-b px-4 py-3 font-mono text-micro uppercase tracking-[0.16em] text-muted-foreground">{tr ? "Demo kapsamı" : "Demo scope"}</p>
            <AnimatedList className="grid gap-px bg-border @lg/tile:grid-cols-3">
              {[[Database, tr ? "Veri kaynağı" : "Data source"], [MessageSquareText, tr ? "İlk iş sorusu" : "First question"], [Braces, tr ? "Doğrulama akışı" : "Validation flow"]].map(([Icon, label], index) => { const StepIcon = Icon as typeof Database; return (
                <div className="relative h-full bg-background p-4" key={String(label)}>
                  <TileBody
                    top={
                      <>
                        <StepIcon className="size-4 shrink-0 text-brand" aria-hidden="true" />
                        <span className="font-mono text-micro text-muted-foreground">0{index + 1}</span>
                      </>
                    }
                  >
                    <p className="text-xs font-semibold">{String(label)}</p>
                  </TileBody>
                  {/* Bağlayıcı ok sağa dönük olduğu halde hücrenin ALTINA, ortaya
                      konumlanmıştı — yatay 3'lü ızgarada yetim chevron'lar çıkıyordu.
                      Artık hücreler arası hairline'ın üzerinde, dikey ortada. */}
                  {index < 2 ? <ArrowDown aria-hidden="true" className="absolute right-0 top-1/2 z-10 hidden size-3 -translate-y-1/2 translate-x-1/2 -rotate-90 text-brand @lg/tile:block" /> : null}
                </div>
              ); })}
            </AnimatedList>
          </MagicCard>
        </Reveal>
        <Reveal delay={0.1} y={16} className="lg:sticky lg:top-24">
          <div className="marketing-surface rounded-xl border bg-card p-6 shadow-lg"><ContactForm locale={content.locale} /></div>
        </Reveal>
      </Container>
    </section>
  );
}
