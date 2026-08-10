import type { Metadata } from "next";
import { Mail } from "lucide-react";
import { getLocale } from "next-intl/server";
import { ContactForm } from "@/components/marketing/ContactForm";
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
    <section className="relative overflow-hidden border-b bg-foreground py-16 text-background sm:py-24">
      <div aria-hidden="true" className="marketing-grid absolute inset-0 opacity-20 [mask-image:linear-gradient(to_bottom,black,transparent)]" />
      <Container className="relative grid gap-12 lg:grid-cols-[0.92fr_1.08fr] lg:items-start">
        <Reveal>
          <Eyebrow>{tr ? "İletişim" : "Contact"}</Eyebrow>
          <h1 className="mt-5 text-balance font-display text-5xl leading-[1.02] tracking-[-0.04em] sm:text-6xl">{tr ? "Gerçek bir iş sorusuyla tanışalım." : "Let’s meet through a real business question."}</h1>
          <p className="mt-6 max-w-lg text-lg leading-8 text-background/68">{tr ? "Veri kaynağınızı, mevcut rapor akışınızı ve yanıtlamak istediğiniz ilk soruyu paylaşın." : "Tell us about your data source, reporting flow, and the first question you want to answer."}</p>
          <a className="mt-8 inline-flex items-center gap-2 text-sm text-background underline-offset-4 hover:underline focus-visible:underline" href="mailto:contact@upcytech.com"><Mail className="size-4 shrink-0 text-chart-2" /><span className="break-anywhere">contact@upcytech.com</span></a>
          <div className="relative mt-10 overflow-hidden rounded-[1.15rem] border border-background/15">
            <MarketingEditorialImage asset="contactHero" alt={tr ? "İki kişinin mor kumaş numunesi üzerinden konuşması" : "Two people discussing a purple textile sample"} className="marketing-editorial-image aspect-[16/10]" priority sizes="(min-width: 1024px) 44vw, 100vw" />
            <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/70 to-transparent" />
            <span className="absolute inset-x-5 bottom-5 text-sm font-medium text-background sm:inset-x-6 sm:bottom-6">{tr ? "İlk soruyu, verinin gerçek bağlamını ve beklenen çıktıyı birlikte netleştirelim." : "Let’s clarify the first question, its real context, and the output you need."}</span>
          </div>
          <div className="mt-10 border-y border-background/15"><p className="py-4 font-mono text-micro uppercase tracking-[0.16em] text-background/45">{tr ? "Demo kapsamı" : "Demo scope"}</p><ol className="grid border-t border-background/15 sm:grid-cols-3">{[tr ? "Veri kaynağı" : "Data source", tr ? "İlk iş sorusu" : "First question", tr ? "Doğrulama akışı" : "Validation flow"].map((label, index) => <li className="border-b border-background/15 py-4 last:border-b-0 sm:border-b-0 sm:border-r sm:px-4 sm:first:pl-0 sm:last:border-r-0" key={label}><span className="font-mono text-micro text-chart-2">0{index + 1}</span><p className="mt-2 text-sm text-background/75">{label}</p></li>)}</ol></div>
        </Reveal>
        <Reveal delay={0.1} y={16} className="lg:sticky lg:top-24">
          <div className="marketing-surface rounded-xl border border-background/10 bg-background p-6 text-foreground shadow-2xl sm:p-8"><ContactForm locale={content.locale} /></div>
        </Reveal>
      </Container>
    </section>
  );
}
