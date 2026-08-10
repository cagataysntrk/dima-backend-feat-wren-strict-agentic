import type { MetadataRoute } from "next";
import { publicRoutes } from "@/content/marketing";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dima.upcytech.com";
  const routes = process.env.DIMA_LEGAL_APPROVED === "true"
    ? publicRoutes
    : publicRoutes.filter((route) => route !== "/privacy" && route !== "/terms");
  return routes.map((route) => ({
    url: new URL(route, base).toString(),
    lastModified: new Date(),
    changeFrequency: route === "/" ? "weekly" : "monthly",
    priority: route === "/" ? 1 : route === "/contact" ? 0.8 : 0.7,
  }));
}
