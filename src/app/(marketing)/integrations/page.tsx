import { getLocale } from "next-intl/server";
import { DetailPage } from "@/components/marketing/MarketingPrimitives";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata() { const p = getMarketingContent(await getLocale()).pages.integrations; return pageMetadata(p, "/integrations"); }
export default async function Page() { const c = getMarketingContent(await getLocale()); return <DetailPage page={c.pages.integrations} content={c} />; }
