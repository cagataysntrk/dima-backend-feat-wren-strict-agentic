import type { Metadata } from "next";
import { getLocale } from "next-intl/server";
import { LegalPage } from "@/components/marketing/LegalPage";
import { getMarketingContent } from "@/content/marketing";
import { legalMetadata } from "@/lib/marketing/metadata";
export async function generateMetadata(): Promise<Metadata> {
  const page = getMarketingContent(await getLocale()).legal.privacy;
  return legalMetadata(page, "/privacy");
}
export default async function Page() { const c = getMarketingContent(await getLocale()); return <LegalPage page={c.legal.privacy} content={c} />; }
