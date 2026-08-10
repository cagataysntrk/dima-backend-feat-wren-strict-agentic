import { getLocale } from "next-intl/server";
import { EvidenceDetailPage } from "@/components/marketing/EvidenceDetailPage";
import { MarketingEditorialImage } from "@/components/marketing/MarketingAssets";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";

export async function generateMetadata() {
  const page = getMarketingContent(await getLocale()).pages.textile;
  return pageMetadata(page, "/solutions/textile-dyehouse");
}

export default async function TextileDyehousePage() {
  const content = getMarketingContent(await getLocale());
  return (
    <EvidenceDetailPage
      content={content}
      heroVisual={
        <div className="relative aspect-[16/10] overflow-hidden rounded-xl border bg-card shadow-xl">
          <MarketingEditorialImage asset="decisions" className="marketing-editorial-image" priority sizes="(min-width: 1024px) 54vw, 100vw" />
          <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-foreground/35 via-transparent to-transparent" />
          <div className="absolute inset-x-4 bottom-4 rounded-lg border border-background/20 bg-background/90 p-4 text-sm shadow-lg backdrop-blur-sm sm:inset-x-6 sm:bottom-6">
            <span className="font-mono text-micro uppercase tracking-[0.16em] text-brand">{content.locale === "tr" ? "Sanitized demo" : "Sanitized demo"}</span>
            <span className="mt-2 block font-medium">{content.locale === "tr" ? "Parti · makine · reçete · termin" : "Batch · machine · recipe · deadline"}</span>
          </div>
        </div>
      }
      kind="textile"
      page={content.pages.textile}
    />
  );
}
