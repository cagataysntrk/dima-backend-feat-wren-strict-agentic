import type { Metadata } from "next";
import { getLocale } from "next-intl/server";
import { LegalPage } from "@/components/marketing/LegalPage";
import { getMarketingContent } from "@/content/marketing";
export async function generateMetadata(): Promise<Metadata> {
  const page = getMarketingContent(await getLocale()).legal.privacy;
  return { title: page.title, description: page.description, alternates: { canonical: "/privacy" } };
}
export default async function Page() { const c = getMarketingContent(await getLocale()); return <LegalPage page={c.legal.privacy} content={c} />; }
