import { getLocale } from "next-intl/server";
import { EvidenceDetailPage } from "@/components/marketing/EvidenceDetailPage";
import { PageVisualStage } from "@/components/marketing/VisualAssets";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata() { const p = getMarketingContent(await getLocale()).pages.product; return pageMetadata(p, "/product"); }
export default async function Page() { const c = getMarketingContent(await getLocale()); return <EvidenceDetailPage kind="product" page={c.pages.product} content={c} heroVisual={<PageVisualStage variant="product" locale={c.locale} />} />; }
