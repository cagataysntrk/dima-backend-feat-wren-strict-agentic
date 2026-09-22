import "server-only";
import { z } from "zod";

// Tenant registry. Written by dima-metabase/bootstrap/setup.py into .env.local.
// Keys and ids stay server-side; the browser only ever sees the org (tenant) slug.
const Tenant = z.object({
  name: z.string(),
  apiKey: z.string().min(1),
  databaseId: z.number().int().positive(),
  collectionId: z.number().int().positive(),
  dashboardId: z.number().int().positive(),
  schema: z.string(),
});
export type Tenant = z.infer<typeof Tenant> & { slug: string };

let cache: Map<string, Tenant> | null = null;

function load(): Map<string, Tenant> {
  if (cache) return cache;
  const raw = process.env.METABASE_TENANTS;
  if (!raw) throw new Error("METABASE_TENANTS is not configured");
  const parsed = z.record(z.string(), Tenant).parse(JSON.parse(raw));
  cache = new Map(Object.entries(parsed).map(([slug, t]) => [slug, { ...t, slug }]));
  return cache;
}

/** Tenant for an organization slug, or null if the org has no analytics tenant. */
export function tenantBySlug(slug: string): Tenant | null {
  return load().get(slug) ?? null;
}

export function metabaseUrl(): string {
  const url = process.env.METABASE_URL;
  if (!url) throw new Error("METABASE_URL is not configured");
  return url.replace(/\/$/, "");
}

export function adminApiKey(): string {
  const key = process.env.METABASE_ADMIN_API_KEY;
  if (!key) throw new Error("METABASE_ADMIN_API_KEY is not configured");
  return key;
}
