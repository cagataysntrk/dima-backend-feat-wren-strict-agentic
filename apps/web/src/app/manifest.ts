import type { MetadataRoute } from "next";
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "dima — Güvenilir konuşmalı analitik",
    short_name: "dima",
    description: "Modeled business context and validated SQL for conversational analytics.",
    start_url: "/",
    display: "standalone",
    background_color: "oklch(0.985 0.003 95)",
    theme_color: "oklch(0.55 0.2 277)",
    icons: [{ src: "/icon.svg", sizes: "any", type: "image/svg+xml" }],
  };
}
