import { getLocale } from "next-intl/server";
import { DetailPage } from "@/components/marketing/MarketingPrimitives";
import { PageVisualStage } from "@/components/marketing/VisualAssets";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata() { const p = getMarketingContent(await getLocale()).pages.product; return pageMetadata(p, "/product"); }
export default async function Page() { const c = getMarketingContent(await getLocale()); return <DetailPage page={c.pages.product} content={c} visual={<PageVisualStage variant="product" locale={c.locale} />} />; }
