import "server-only";
import { mbGet, mbPost } from "./client";
import { assertCard, requireAnalyst, type TenantContext } from "./guard";

// Analysis history (feature 14): the engine keeps a revision per change.
// Every write from this app goes out with the company's API key, so revisions
// are attributed to the company rather than to the individual user — the UI
// says so instead of implying otherwise.

export interface Revision {
  id: number;
  at: string;
  what: string;
  current: boolean;
}

interface EngineRevision {
  id: number;
  timestamp: string;
  description?: string | null;
  message?: string | null;
  is_creation?: boolean;
}

export async function cardHistory(ctx: TenantContext, cardId: number): Promise<Revision[]> {
  await assertCard(ctx, cardId);
  const revs = await mbGet<EngineRevision[]>(ctx.tenant, `/api/revision?entity=card&id=${cardId}`);
  return revs.map((r, i) => ({
    id: r.id,
    at: r.timestamp,
    what: r.description ?? r.message ?? (r.is_creation ? "oluşturuldu" : "değiştirildi"),
    current: i === 0,
  }));
}

export async function revertCard(ctx: TenantContext, cardId: number, revisionId: number) {
  requireAnalyst(ctx);
  await assertCard(ctx, cardId);
  await mbPost(ctx.tenant, "/api/revision/revert", { entity: "card", id: cardId, revision_id: revisionId });
  return { ok: true };
}
