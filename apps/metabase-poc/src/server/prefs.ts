import "server-only";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { GatewayError } from "./metabase/errors";
import type { Role } from "./metabase/guard";

/**
 * Per-company product-side chat settings.
 *
 * Model/provider selection is intentionally absent: native Metabot configuration
 * is owned by dima-metabase-engine, not by the frontend product.
 */
export interface ChatPrefs {
  maxRows: number;
}

// 2,000 is the product-side result cap for the current UI renderer.
export const ROW_LIMITS = [500, 1_000, 2_000];

export const DEFAULT_PREFS: ChatPrefs = { maxRows: 2_000 };

function parse(metadata: unknown): ChatPrefs {
  const raw = (metadata ?? {}) as { chat?: Partial<ChatPrefs> };
  const maxRows = ROW_LIMITS.includes(Number(raw.chat?.maxRows))
    ? Number(raw.chat!.maxRows)
    : DEFAULT_PREFS.maxRows;
  return { maxRows };
}

/** Prefs for the caller's active company; defaults when nothing is stored. */
export async function chatPrefs(): Promise<ChatPrefs> {
  const h = await headers();
  const org = await auth.api.getFullOrganization({ headers: h }).catch(() => null);
  return parse(org?.metadata);
}

export async function setChatPrefs(patch: Partial<ChatPrefs>): Promise<ChatPrefs> {
  const h = await headers();
  const session = await auth.api.getSession({ headers: h });
  const orgId = session?.session.activeOrganizationId;
  if (!orgId) throw new GatewayError(401, "Oturum bulunamadı.");
  const me = await auth.api.getActiveMember({ headers: h }).catch(() => null);
  const role = me?.role as Role | undefined;
  if (role !== "owner" && role !== "admin") {
    throw new GatewayError(403, "Sohbet ayarlarını yalnızca yöneticiler değiştirebilir.");
  }
  if (patch.maxRows !== undefined && !ROW_LIMITS.includes(patch.maxRows)) {
    throw new GatewayError(400, "Geçersiz satır sınırı.");
  }

  const current = await chatPrefs();
  const next: ChatPrefs = { ...current, ...patch };
  const org = await auth.api.getFullOrganization({ headers: h });
  await auth.api.updateOrganization({
    headers: h,
    body: {
      organizationId: orgId,
      data: {
        metadata: {
          ...(org?.metadata ?? {}),
          chat: next,
        },
      },
    },
  });
  return next;
}
