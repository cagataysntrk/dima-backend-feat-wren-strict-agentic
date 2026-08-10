import { getLocale } from "next-intl/server";
import { EvidenceDetailPage } from "@/components/marketing/EvidenceDetailPage";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata() { const p = getMarketingContent(await getLocale()).pages.how; return pageMetadata(p, "/how-it-works"); }
export default async function Page() { const c = getMarketingContent(await getLocale()); return <EvidenceDetailPage kind="how" page={c.pages.how} content={c} />; }
