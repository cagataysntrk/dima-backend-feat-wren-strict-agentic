import type { Metadata } from "next";
import type { PageContent } from "@/content/marketing";

export function pageMetadata(page: PageContent, path: string): Metadata {
  return {
    title: page.title,
    description: page.description,
    alternates: { canonical: path },
    openGraph: {
      title: page.title,
      description: page.description,
      url: path,
      type: "website",
    },
  };
}
