import "server-only";
import { z } from "zod";
import type { QueryResult } from "@dima/contracts";
import { queryReadOnly } from "../metabase/api";
import { mbGet } from "../metabase/client";
import { GatewayError, scrub } from "../metabase/errors";
import type { TenantContext } from "../metabase/guard";
import { complete, type ChatMessage } from "./openrouter";
import { RUN_SQL_TOOL, describeSchema, summarizeForModel, systemPrompt, type TableSchema } from "./prompt";

// NL question → SQL (via the model) → engine (tenant key, SELECT-only guard,
// tenant DB role) → answer + a result the UI renders with Dima charts.
// The model can do nothing but call run_sql; every call goes through the same
// path as the SQL runner, so it cannot reach another tenant's data.

const MAX_TOOL_ROUNDS = 6;
const SCHEMA_TTL_MS = 10 * 60_000;

export interface Turn {
  role: "user" | "assistant";
  content: string;
}

export interface ChatAnswer {
  answer: string;
  sql: string | null;
  result: QueryResult | null;
}

const schemaCache = new Map<string, { at: number; tables: TableSchema[] }>();

/** The tenant's tables and visible columns (engine metadata, cached briefly). */
export async function tenantTables(ctx: TenantContext): Promise<TableSchema[]> {
  const hit = schemaCache.get(ctx.tenant.slug);
  if (hit && Date.now() - hit.at < SCHEMA_TTL_MS) return hit.tables;
  const meta = await mbGet<{
    tables: {
      schema: string;
      name: string;
      visibility_type: string | null;
      fields: { name: string; display_name: string; database_type: string; visibility_type: string }[];
    }[];
  }>(ctx.tenant, `/api/database/${ctx.tenant.databaseId}/metadata`);
  const tables: TableSchema[] = meta.tables
    .filter((t) => t.schema === ctx.tenant.schema && !t.visibility_type)
    .map((t) => ({
      schema: t.schema,
      name: t.name,
      columns: t.fields
        .filter((f) => f.visibility_type === "normal" && !/^_mb_/i.test(f.name))
        // Friendly names (data model) are appended so the model knows what a column means.
        .map((f) => ({
          name: f.name,
          type: f.database_type,
          label: f.display_name && f.display_name.toLowerCase() !== f.name.replace(/_/g, " ") ? f.display_name : undefined,
        })),
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
  schemaCache.set(ctx.tenant.slug, { at: Date.now(), tables });
  return tables;
}

/** The database's own error line (e.g. 'column "x" does not exist'), without transport noise. */
function dbMessage(e: GatewayError): string {
  const detail = e.detail ?? e.publicMessage;
  const m = /ERROR:[^\n]*/.exec(detail);
  return (m ? m[0] : e.publicMessage).slice(0, 300);
}

const RunSqlArgs = z.object({ sql: z.string().min(1).max(20_000), final: z.boolean().optional() });

export async function answer(ctx: TenantContext, history: Turn[]): Promise<ChatAnswer> {
  const messages: ChatMessage[] = [
    { role: "system", content: systemPrompt(ctx.tenant.name, describeSchema(await tenantTables(ctx))) },
    ...history,
  ];
  let shown: { sql: string; result: QueryResult } | null = null;
  let lastOk: { sql: string; result: QueryResult } | null = null;

  for (let round = 0; round <= MAX_TOOL_ROUNDS; round++) {
    const choice = await complete(messages, [RUN_SQL_TOOL], round < MAX_TOOL_ROUNDS ? "auto" : "none");
    const calls = choice.message.tool_calls ?? [];
    if (calls.length === 0) {
      const text = (choice.message.content ?? "").trim();
      const picked = shown ?? lastOk;
      return {
        answer: scrub(text) || (picked ? "Sonuç aşağıda." : "Bu soruya yanıt üretemedim; farklı sorabilir misiniz?"),
        sql: picked?.sql ?? null,
        result: picked?.result ?? null,
      };
    }
    messages.push({ role: "assistant", content: choice.message.content, tool_calls: calls });
    for (const call of calls) {
      let content: string;
      let parsedArgs: unknown = null;
      try {
        parsedArgs = JSON.parse(call.function.arguments || "{}");
      } catch {
        /* handled below */
      }
      const args = RunSqlArgs.safeParse(parsedArgs);
      if (call.function.name !== "run_sql" || !args.success) {
        content = "Error: invalid tool call. Call run_sql with {sql, final}.";
      } else {
        try {
          const result = await queryReadOnly(ctx, args.data.sql);
          lastOk = { sql: args.data.sql, result };
          if (args.data.final) shown = lastOk;
          content = summarizeForModel(result);
        } catch (e) {
          // The model gets the DB's own message so it can repair the query.
          content = `Error: ${scrub(e instanceof GatewayError ? dbMessage(e) : "query failed")}`;
        }
      }
      messages.push({ role: "tool", tool_call_id: call.id, content });
    }
  }
  throw new GatewayError(502, "Soru yanıtlanamadı; daha basit bir şekilde sormayı deneyin.");
}
