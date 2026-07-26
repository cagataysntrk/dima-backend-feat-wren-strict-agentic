import { getLocale } from "next-intl/server";
import { EvidenceDetailPage } from "@/components/marketing/EvidenceDetailPage";
import { PageVisualStage } from "@/components/marketing/VisualAssets";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata() { const p = getMarketingContent(await getLocale()).pages.security; return pageMetadata(p, "/security"); }
export default async function Page() { const c = getMarketingContent(await getLocale()); return <EvidenceDetailPage kind="security" page={c.pages.security} content={c} heroVisual={<PageVisualStage variant="security" locale={c.locale} />} />; }
