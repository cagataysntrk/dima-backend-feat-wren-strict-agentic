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
    twitter: {
      card: "summary_large_image",
      title: page.title,
      description: page.description,
    },
  };
}

export function legalMetadata(page: PageContent, path: string): Metadata {
  return {
    ...pageMetadata(page, path),
    robots: process.env.DIMA_LEGAL_APPROVED === "true"
      ? undefined
      : { index: false, follow: false },
  };
}
