import "server-only";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { mbGet } from "./client";
import { forbidden, notFound, unauthorized } from "./errors";
import { tenantBySlug, type Tenant } from "./tenants";

export type Role = "owner" | "admin" | "member";

export interface TenantContext {
  tenant: Tenant;
  role: Role;
  userId: string;
  orgId: string;
}

/**
 * Resolve the caller's tenant from the Better Auth session:
 * session → active organization → membership role → tenant (by org slug).
 * Every gateway route starts here; no tenant, no data.
 */
export async function requireTenant(): Promise<TenantContext> {
  const h = await headers();
  const session = await auth.api.getSession({ headers: h });
  if (!session) throw unauthorized();
  const orgId = session.session.activeOrganizationId;
  if (!orgId) throw forbidden();
  const [org, member] = await Promise.all([
    auth.api.getFullOrganization({ headers: h, query: { organizationId: orgId } }),
    auth.api.getActiveMember({ headers: h }),
  ]);
  if (!org || !member) throw forbidden();
  const tenant = tenantBySlug(org.slug);
  if (!tenant) throw forbidden();
  return { tenant, role: member.role as Role, userId: session.user.id, orgId };
}

export function requireAnalyst(ctx: TenantContext): void {
  if (ctx.role !== "owner" && ctx.role !== "admin") throw forbidden();
}

/**
 * The engine already enforces collection permissions per tenant API key; this is
 * the second check, and it also hides existence (404) of other tenants' ids.
 */
export async function assertCard(ctx: TenantContext, cardId: number) {
  const card = await mbGet<EngineCard>(ctx.tenant, `/api/card/${cardId}`);
  if (card.archived || card.collection_id !== ctx.tenant.collectionId) throw notFound();
  return card;
}

export async function assertDashboard(ctx: TenantContext, dashboardId: number) {
  const dash = await mbGet<EngineDashboard>(ctx.tenant, `/api/dashboard/${dashboardId}`);
  if (dash.archived || dash.collection_id !== ctx.tenant.collectionId) throw notFound();
  return dash;
}

export interface EngineCard {
  id: number;
  name: string;
  description: string | null;
  display: string;
  collection_id: number | null;
  database_id: number;
  table_id: number | null;
  query_type: string;
  archived: boolean;
  updated_at: string;
  visualization_settings?: Record<string, unknown>;
}

export interface EngineParameter {
  id: string;
  name: string;
  slug: string;
  type: string;
}

export interface EngineDashcard {
  id: number;
  card_id: number | null;
  row: number;
  col: number;
  size_x: number;
  size_y: number;
  card: { id: number; name: string; display: string; visualization_settings?: Record<string, unknown> } | null;
  parameter_mappings: { parameter_id: string; card_id: number; target: unknown }[];
  visualization_settings?: Record<string, unknown>;
}

export interface EngineDashboard {
  id: number;
  name: string;
  description: string | null;
  collection_id: number | null;
  archived: boolean;
  parameters: EngineParameter[];
  dashcards: EngineDashcard[];
}
