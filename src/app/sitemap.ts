import type { MetadataRoute } from "next";
import { publicRoutes } from "@/content/marketing";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dima.upcytech.com";
  return publicRoutes.map((route) => ({
    url: new URL(route, base).toString(),
    lastModified: new Date(),
    changeFrequency: route === "/" ? "weekly" : "monthly",
    priority: route === "/" ? 1 : route === "/contact" ? 0.8 : 0.7,
  }));
}
