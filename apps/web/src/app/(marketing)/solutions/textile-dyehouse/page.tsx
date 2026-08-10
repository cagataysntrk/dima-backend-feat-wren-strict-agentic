import { getLocale } from "next-intl/server";
import { EvidenceDetailPage } from "@/components/marketing/EvidenceDetailPage";
import { getMarketingContent } from "@/content/marketing";
import { pageMetadata } from "@/lib/marketing/metadata";

export async function generateMetadata() {
  const page = getMarketingContent(await getLocale()).pages.textile;
  return pageMetadata(page, "/solutions/textile-dyehouse");
}

export default async function TextileDyehousePage() {
  const content = getMarketingContent(await getLocale());
  return <EvidenceDetailPage content={content} kind="textile" page={content.pages.textile} />;
}
