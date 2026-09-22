import "server-only";
import type { QueryResult } from "@dima/contracts";
import { toQueryResult, type EngineDataset } from "./adapter";
import { browseTables } from "./browse";
import { mbGet, mbPost } from "./client";
import { GatewayError } from "./errors";
import type { TenantContext } from "./guard";
import { insightTitle } from "@/lib/insight-title";

// Automatic insights (feature 12): the engine proposes a set of questions for a
// table; we run them with the tenant key and render the results ourselves.

const MAX_CARDS = 8;

export interface Insight {
  title: string;
  display: string;
  result: QueryResult | null;
  error: string | null;
}

interface XrayCard {
  card?: { name?: string; display?: string; dataset_query?: unknown };
}

export async function tableInsights(ctx: TenantContext, tableId: number): Promise<{ table: string; insights: Insight[] }> {
  const table = (await browseTables(ctx)).find((t) => t.id === tableId);
  if (!table) throw new GatewayError(404, "Tablo bulunamadı.");

  const xray = await mbGet<{ dashcards?: XrayCard[] }>(ctx.tenant, `/api/automagic-dashboards/table/${tableId}`);
  const cards = (xray.dashcards ?? []).filter((c) => c.card?.dataset_query).slice(0, MAX_CARDS);

  const insights = await Promise.all(
    cards.map(async (c): Promise<Insight> => {
      const title = insightTitle(c.card?.name ?? "", table.name);
      try {
        const ds = await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", c.card!.dataset_query);
        return { title, display: c.card?.display ?? "bar", result: toQueryResult(ds), error: null };
      } catch (e) {
        return {
          title,
          display: c.card?.display ?? "bar",
          result: null,
          error: e instanceof GatewayError ? e.publicMessage : "Sorgu çalıştırılamadı.",
        };
      }
    }),
  );
  return { table: table.name, insights };
}
