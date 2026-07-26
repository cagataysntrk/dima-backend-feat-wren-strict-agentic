import { getLocale } from "next-intl/server";
import { DetailPage } from "@/components/marketing/MarketingPrimitives";
import { PageVisualStage } from "@/components/marketing/VisualAssets";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata() { const p = getMarketingContent(await getLocale()).pages.how; return pageMetadata(p, "/how-it-works"); }
export default async function Page() { const c = getMarketingContent(await getLocale()); return <DetailPage page={c.pages.how} content={c} visual={<PageVisualStage variant="validation" locale={c.locale} />} />; }
