import type { Metadata } from "next";
import { Mail } from "lucide-react";
import { getLocale } from "next-intl/server";
import { ContactForm } from "@/components/marketing/ContactForm";
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
    <section className="marketing-grid py-20 sm:py-28">
      <Container className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
        <div><Eyebrow>{tr ? "İletişim" : "Contact"}</Eyebrow><h1 className="mt-5 text-balance font-display text-5xl leading-tight sm:text-6xl">{tr ? "Gerçek bir iş sorusuyla tanışalım." : "Let’s meet through a real business question."}</h1><p className="mt-6 max-w-lg text-lg leading-8 text-muted-foreground">{tr ? "Veri kaynağınızı, mevcut rapor akışınızı ve doğrulanması gereken ilk soruyu paylaşın." : "Tell us about your data source, reporting flow, and the first question that needs validation."}</p><a className="mt-8 inline-flex items-center gap-2 text-sm hover:underline" href="mailto:contact@upcytech.com"><Mail className="size-4 text-brand" />contact@upcytech.com</a></div>
        <div className="rounded-xl border bg-card p-6 shadow-lg sm:p-9"><ContactForm locale={content.locale} /></div>
      </Container>
    </section>
  );
}
