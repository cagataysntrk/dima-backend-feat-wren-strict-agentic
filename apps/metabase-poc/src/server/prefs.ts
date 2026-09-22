import "server-only";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { DEFAULT_MODEL } from "./chat/openrouter";
import { GatewayError } from "./metabase/errors";
import type { Role } from "./metabase/guard";

/**
 * Per-company chat settings, kept in the organization's Better Auth metadata.
 * Not env vars: two companies on one deployment can want different answers.
 */
export interface ChatPrefs {
  model: string;
  maxRows: number;
}

/** Deliberately a short allowlist: an arbitrary model id is a billing surprise. */
export const MODELS: { id: string; label: string; hint: string }[] = [
  { id: "openai/gpt-5.6-sol", label: "Sol", hint: "Hızlı ve ekonomik — günlük sorular için." },
  { id: "openai/gpt-5.6-luna", label: "Luna", hint: "Daha güçlü; karmaşık sorgularda daha isabetli." },
];
// 2.000 is the engine-side hard cap (SQL_MAX_ROWS); offering more would lie.
export const ROW_LIMITS = [500, 1_000, 2_000];

export const DEFAULT_PREFS: ChatPrefs = { model: DEFAULT_MODEL, maxRows: 2_000 };

function parse(metadata: unknown): ChatPrefs {
  const raw = (metadata ?? {}) as { chat?: Partial<ChatPrefs> };
  const model = MODELS.some((m) => m.id === raw.chat?.model) ? raw.chat!.model! : DEFAULT_PREFS.model;
  const maxRows = ROW_LIMITS.includes(Number(raw.chat?.maxRows))
    ? Number(raw.chat!.maxRows)
    : DEFAULT_PREFS.maxRows;
  return { model, maxRows };
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
  if (patch.model && !MODELS.some((m) => m.id === patch.model)) {
    throw new GatewayError(400, "Bilinmeyen model.");
  }
  if (patch.maxRows !== undefined && !ROW_LIMITS.includes(patch.maxRows)) {
    throw new GatewayError(400, "Geçersiz satır sınırı.");
  }
  const current = await chatPrefs();
  const next: ChatPrefs = { ...current, ...patch };
  const org = await auth.api.getFullOrganization({ headers: h });
  await auth.api.updateOrganization({
    headers: h,
    // Merge: metadata may hold keys this screen knows nothing about.
    body: { organizationId: orgId, data: { metadata: { ...(org?.metadata ?? {}), chat: next } } },
  });
  return next;
}
