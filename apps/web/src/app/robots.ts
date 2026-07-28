import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dima.upcytech.com";
  const indexable = process.env.VERCEL_ENV === "production" || process.env.NEXT_PUBLIC_INDEXING_ENABLED === "true";
  return indexable
    ? { rules: { userAgent: "*", allow: "/", disallow: ["/app", "/app/", "/api/"] }, sitemap: `${base}/sitemap.xml` }
    : { rules: { userAgent: "*", disallow: "/" } };
}
