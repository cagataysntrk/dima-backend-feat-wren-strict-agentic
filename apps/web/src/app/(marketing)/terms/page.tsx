import type { Metadata } from "next";
import { getLocale } from "next-intl/server";
import { LegalPage } from "@/components/marketing/LegalPage";
import { getMarketingContent } from "@/content/marketing";
export async function generateMetadata(): Promise<Metadata> {
  const page = getMarketingContent(await getLocale()).legal.terms;
  return { title: page.title, description: page.description, alternates: { canonical: "/terms" } };
}
export default async function Page() { const c = getMarketingContent(await getLocale()); return <LegalPage page={c.legal.terms} content={c} />; }
