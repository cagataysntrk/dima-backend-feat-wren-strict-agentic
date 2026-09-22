import "server-only";
import { z } from "zod";
import type { QueryResult } from "@dima/contracts";
import { queryReadOnly } from "../metabase/api";
import { mbGet } from "../metabase/client";
import { GatewayError, scrub } from "../metabase/errors";
import type { TenantContext } from "../metabase/guard";
import { complete, streamComplete, type ChatMessage } from "./openrouter";
import { usableToolCalls } from "@/lib/sse";
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


// ── Streaming ────────────────────────────────────────────────────────────────

/** What the browser is told while an answer is being produced. */
export type ChatEvent =
  | { type: "step"; id: number; text: string; done: boolean }
  | { type: "token"; text: string }
  | { type: "done"; answer: string; sql: string | null; result: QueryResult | null; steps: string[]; durationMs: number }
  | { type: "error"; message: string };

const rows = (n: number) => `${n.toLocaleString("tr-TR")} satır`;

/**
 * Same pipeline as `answer`, reported as it happens: every step is a real
 * event (schema read, query written, query run, repair), and the final answer
 * streams token by token.
 */
export async function* answerStream(
  ctx: TenantContext,
  history: Turn[],
  signal?: AbortSignal,
): AsyncGenerator<ChatEvent> {
  const startedAt = Date.now();
  const steps: string[] = [];
  let stepId = 0;

  // A step is announced when it starts and confirmed when it ends, so the
  // reader sees work in progress rather than a list appearing at the end.
  const open = (text: string) => {
    const id = ++stepId;
    return {
      id,
      start: { type: "step", id, text, done: false } as ChatEvent,
      finish: (result: string) => {
        steps.push(result);
        return { type: "step", id, text: result, done: true } as ChatEvent;
      },
    };
  };

  const schemaStep = open("Veri şeması okunuyor");
  yield schemaStep.start;
  const tables = await tenantTables(ctx);
  yield schemaStep.finish(`Veri şeması okundu · ${tables.length} tablo`);

  const messages: ChatMessage[] = [
    { role: "system", content: systemPrompt(ctx.tenant.name, describeSchema(tables)) },
    ...history,
  ];
  let shown: { sql: string; result: QueryResult } | null = null;
  let lastOk: { sql: string; result: QueryResult } | null = null;

  for (let round = 0; round <= MAX_TOOL_ROUNDS; round++) {
    const writing = open(round === 0 ? "Sorgu yazılıyor" : "Sorgu düzeltiliyor");
    yield writing.start;

    let text = "";
    let calls: ReturnType<typeof usableToolCalls> = [];
    let finish: string | null | undefined;
    for await (const chunk of streamComplete(messages, [RUN_SQL_TOOL], round < MAX_TOOL_ROUNDS ? "auto" : "none", signal)) {
      if (chunk.text) {
        // The model answers only once it stops calling tools; from that point
        // the text is the answer and goes straight to the reader.
        if (!text) yield writing.finish(round === 0 ? "Sorgu yazıldı" : "Sorgu düzeltildi");
        text += chunk.text;
        yield { type: "token", text: chunk.text };
      }
      if (chunk.finish !== undefined) {
        calls = usableToolCalls(chunk.toolCalls ?? []);
        finish = chunk.finish;
      }
    }

    if (calls.length === 0) {
      if (!text) yield writing.finish("Yanıt hazırlandı");
      const picked = shown ?? lastOk;
      const answerText =
        scrub(text.trim()) || (picked ? "Sonuç aşağıda." : "Bu soruya yanıt üretemedim; farklı sorabilir misiniz?");
      yield {
        type: "done",
        answer: answerText,
        sql: picked?.sql ?? null,
        result: picked?.result ?? null,
        steps,
        durationMs: Date.now() - startedAt,
      };
      return;
    }

    if (!text) yield writing.finish(round === 0 ? "Sorgu yazıldı" : "Sorgu düzeltildi");
    messages.push({
      role: "assistant",
      content: text || null,
      tool_calls: calls.map((c) => ({ id: c.id, type: "function" as const, function: { name: c.name, arguments: c.arguments } })),
    });

    for (const call of calls) {
      const running = open("Sorgu çalıştırılıyor");
      yield running.start;
      const args = RunSqlArgs.safeParse(JSON.parse(call.arguments || "{}"));
      if (call.name !== "run_sql" || !args.success) {
        messages.push({ role: "tool", tool_call_id: call.id, content: "Error: invalid tool call. Call run_sql with {sql, final}." });
        yield running.finish("Sorgu çalıştırılamadı");
        continue;
      }
      try {
        const result = await queryReadOnly(ctx, args.data.sql);
        lastOk = { sql: args.data.sql, result };
        if (args.data.final) shown = lastOk;
        messages.push({ role: "tool", tool_call_id: call.id, content: summarizeForModel(result) });
        yield running.finish(`Sorgu çalıştı · ${rows(result.row_count)}`);
      } catch (e) {
        const message = scrub(e instanceof GatewayError ? dbMessage(e) : "query failed");
        messages.push({ role: "tool", tool_call_id: call.id, content: `Error: ${message}` });
        yield running.finish(`Sorgu hata verdi · ${message.slice(0, 80)}`);
      }
    }
    void finish;
  }
  yield { type: "error", message: "Soru yanıtlanamadı; daha basit bir şekilde sormayı deneyin." };
}
