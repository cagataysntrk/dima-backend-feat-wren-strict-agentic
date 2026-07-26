import type { Metadata } from "next";
import { ArrowDown, Braces, Database, Mail, MessageSquareText } from "lucide-react";
import { getLocale } from "next-intl/server";
import { ContactForm } from "@/components/marketing/ContactForm";
import { AnimatedList, MagicCard, Particles } from "@/components/marketing/MagicUI";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import { Reveal } from "@/components/marketing/MarketingMotion";
import { Container, Eyebrow } from "@/components/marketing/MarketingPrimitives";
import { getMarketingContent } from "@/content/marketing";

export async function generateMetadata(): Promise<Metadata> {
  const tr = getMarketingContent(await getLocale()).locale === "tr";
  return {
    title: tr ? "Demo talep et" : "Request a demo",
    description: tr ? "dima ürününü kendi veri ve rapor ihtiyacınızla değerlendirin." : "Evaluate dima with your own data and reporting need.",
    alternates: { canonical: "/contact" },
  };
}
export default async function ContactPage() {
  const content = getMarketingContent(await getLocale());
  const tr = content.locale === "tr";
  return (
    <section className="relative overflow-hidden py-16 sm:py-24">
      <div aria-hidden="true" className="marketing-grid absolute inset-0 opacity-45 [mask-image:linear-gradient(to_bottom,black,transparent)]" />
      <Particles className="hidden opacity-50 sm:block" quantity={24} />
      <Container className="relative grid gap-12 lg:grid-cols-[0.92fr_1.08fr] lg:items-start">
        <Reveal>
          <Eyebrow>{tr ? "İletişim" : "Contact"}</Eyebrow>
          <h1 className="mt-5 text-balance font-display text-5xl leading-[1.02] tracking-[-0.04em] sm:text-6xl">{tr ? "Gerçek bir iş sorusuyla tanışalım." : "Let’s meet through a real business question."}</h1>
          <p className="mt-6 max-w-lg text-lg leading-8 text-muted-foreground">{tr ? "Veri kaynağınızı, mevcut rapor akışınızı ve yanıtlamak istediğiniz ilk soruyu paylaşın." : "Tell us about your data source, reporting flow, and the first question you want to answer."}</p>
          <a className="mt-8 inline-flex items-center gap-2 text-sm underline-offset-4 hover:underline focus-visible:underline" href="mailto:contact@upcytech.com"><Mail className="size-4 text-brand" />contact@upcytech.com</a>
          <div className="relative mt-10 aspect-[16/10] overflow-hidden rounded-xl border shadow-lg">
            <MarketingEditorialImage asset="archive" className="marketing-editorial-image" />
            <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/20 to-transparent" />
          </div>
          <MagicCard className="mt-12" tilt={false}>
            <p className="border-b px-4 py-3 font-mono text-[9px] uppercase tracking-[0.16em] text-muted-foreground">{tr ? "Demo kapsamı" : "Demo scope"}</p>
            <AnimatedList className="grid gap-px bg-border sm:grid-cols-3">
              {[[Database, tr ? "Veri kaynağı" : "Data source"], [MessageSquareText, tr ? "İlk iş sorusu" : "First question"], [Braces, tr ? "Doğrulama akışı" : "Validation flow"]].map(([Icon, label], index) => { const StepIcon = Icon as typeof Database; return <div className="relative bg-background p-4" key={String(label)}><StepIcon className="size-4 text-brand" /><p className="mt-6 text-xs font-semibold">{String(label)}</p><span className="absolute right-3 top-3 font-mono text-[8px] text-muted-foreground">0{index + 1}</span>{index < 2 ? <ArrowDown className="absolute -bottom-2 left-1/2 z-10 hidden size-3 -rotate-90 text-brand sm:block" /> : null}</div>; })}
            </AnimatedList>
          </MagicCard>
        </Reveal>
        <Reveal delay={0.1} y={16} className="lg:sticky lg:top-24">
          <div className="marketing-surface rounded-xl border bg-card p-6 shadow-lg sm:p-9"><ContactForm locale={content.locale} /></div>
        </Reveal>
      </Container>
    </section>
  );
}
