import { getLocale } from "next-intl/server";
import { DetailPage } from "@/components/marketing/MarketingPrimitives";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata() { const p = getMarketingContent(await getLocale()).pages.textile; return pageMetadata(p, "/solutions/textile-dyehouse"); }
export default async function Page() { const c = getMarketingContent(await getLocale()); return <DetailPage page={c.pages.textile} content={c} />; }
