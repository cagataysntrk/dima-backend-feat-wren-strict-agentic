import { getLocale } from "next-intl/server";
import { MarketingFooter, MarketingHeader } from "@/components/marketing/MarketingChrome";
import { MarketingMotionProvider } from "@/components/marketing/MarketingMotion";
import { getMarketingContent } from "@/content/marketing";

export default async function MarketingLayout({ children }: { children: React.ReactNode }) {
  const content = getMarketingContent(await getLocale());
  const organization = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "UpcyTech Teknoloji Anonim Şirketi",
    url: process.env.NEXT_PUBLIC_SITE_URL ?? "https://dima.upcytech.com",
    brand: { "@type": "Brand", name: "dima" },
  };
  const software = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "dima",
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    description: content.home.description,
  };

  return (
    <MarketingMotionProvider>
      <a href="#main-content" className="fixed left-4 top-3 z-[100] -translate-y-20 rounded-md bg-foreground px-4 py-2 text-sm text-background transition-transform focus:translate-y-0">
        {content.locale === "tr" ? "Ana içeriğe geç" : "Skip to main content"}
      </a>
      <MarketingHeader content={content} />
      <main id="main-content">{children}</main>
      <MarketingFooter content={content} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(organization).replace(/</g, "\\u003c") }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(software).replace(/</g, "\\u003c") }} />
    </MarketingMotionProvider>
  );
}
