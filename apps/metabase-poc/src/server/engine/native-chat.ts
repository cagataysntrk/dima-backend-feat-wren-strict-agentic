import "server-only";
import { randomUUID } from "node:crypto";
import type { QueryResult } from "@dima/contracts";
import { toQueryResult, type EngineDataset } from "@/server/metabase/adapter";
import { GatewayError, scrub } from "@/server/metabase/errors";
import type { TenantContext } from "@/server/metabase/guard";
import { engineFetch, engineJson } from "./client";
import { openEngineContext, sealEngineContext } from "./context";
import type {
  NativeChatEvent,
  NativeDataPart,
  NativeEngineContext,
  NativeHistoryEntry,
} from "./types";

type GeneratedQuery = Record<string, unknown>;

type ParsedPart =
  | { kind: "text"; value: string }
  | { kind: "data"; value: NativeDataPart }
  | { kind: "error"; value: unknown }
  | { kind: "start"; value: unknown }
  | { kind: "finish"; value: unknown }
  | { kind: "tool_call"; value: { toolCallId?: string; toolName?: string; args?: string } }
  | { kind: "tool_result"; value: { toolCallId?: string; result?: unknown } };

const PREFIX: Record<string, ParsedPart["kind"]> = {
  "0": "text",
  "2": "data",
  "3": "error",
  f: "start",
  d: "finish",
  "9": "tool_call",
  a: "tool_result",
};

export function parseNativeLine(line: string): ParsedPart | null {
  const at = line.indexOf(":");
  if (at < 1) return null;
  const kind = PREFIX[line.slice(0, at)];
  if (!kind) return null;
  const raw = line.slice(at + 1);
  const value = JSON.parse(raw) as unknown;
  if (kind === "text") return { kind, value: String(value) };
  if (kind === "data") return { kind, value: value as NativeDataPart };
  if (kind === "tool_call") return { kind, value: value as Extract<ParsedPart, { kind: "tool_call" }>["value"] };
  if (kind === "tool_result") return { kind, value: value as Extract<ParsedPart, { kind: "tool_result" }>["value"] };
  return { kind, value } as ParsedPart;
}

function toolLabel(name: string): string {
  if (/search|retrieve|resource/i.test(name)) return "Veri kaynakları aranıyor";
  if (/construct|query|sql/i.test(name)) return "Analiz sorgusu hazırlanıyor";
  if (/chart|viz|analy/i.test(name)) return "Sonuç analiz ediliyor";
  return "Analiz yürütülüyor";
}

function queryFromData(part: NativeDataPart): GeneratedQuery | null {
  if (part.type === "generated_entity") {
    const value = part.value as { query?: { query?: unknown } } | undefined;
    const query = value?.query?.query;
    return query && typeof query === "object" ? (query as GeneratedQuery) : null;
  }
  if (part.type === "adhoc_viz") {
    const value = part.value as { query?: unknown } | undefined;
    return value?.query && typeof value.query === "object" ? (value.query as GeneratedQuery) : null;
  }
  return null;
}

function nativeSql(query: GeneratedQuery | null): string | null {
  if (!query || query.type !== "native") return null;
  const native = query.native as { query?: unknown } | undefined;
  return typeof native?.query === "string" ? native.query : null;
}

async function executeGeneratedQuery(
  ctx: TenantContext,
  query: GeneratedQuery | null,
  signal?: AbortSignal,
): Promise<QueryResult | null> {
  if (!query) return null;
  const ds = await engineJson<EngineDataset>(
    ctx.tenant,
    "/api/dataset",
    query,
    signal,
  );
  return toQueryResult(ds);
}

function initialContext(
  ctx: TenantContext,
  productConversationId: string,
  token: string | null | undefined,
): NativeEngineContext {
  return (
    openEngineContext(token, {
      tenantSlug: ctx.tenant.slug,
      productConversationId,
    }) ?? {
      version: 1,
      tenantSlug: ctx.tenant.slug,
      productConversationId,
      engineConversationId: randomUUID(),
      history: [],
      state: {},
    }
  );
}

export async function* nativeAnswerStream(
  ctx: TenantContext,
  input: {
    productConversationId: string;
    message: string;
    engineContext?: string | null;
  },
  signal?: AbortSignal,
): AsyncGenerator<NativeChatEvent> {
  const startedAt = Date.now();
  const native = initialContext(ctx, input.productConversationId, input.engineContext);
  const request = {
    profile_id: "nlq",
    message: input.message,
    context: {},
    conversation_id: native.engineConversationId,
    history: native.history,
    state: native.state,
    debug: false,
  };

  const res = await engineFetch(
    ctx.tenant,
    "/api/metabot/agent-streaming",
    {
      method: "POST",
      headers: { Accept: "text/plain" },
      body: JSON.stringify(request),
    },
    signal,
  );
  if (!res.body) throw new GatewayError(502, "Analiz servisi boş yanıt döndürdü.");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";
  let latestState = native.state;
  let generatedQuery: GeneratedQuery | null = null;
  const responseHistory: NativeHistoryEntry[] = [];
  const steps: string[] = [];
  const active = new Map<string, { id: number; label: string }>();
  let nextStepId = 0;
  let streamedError: unknown = null;

  const process = async function* (line: string): AsyncGenerator<NativeChatEvent> {
    const part = parseNativeLine(line);
    if (!part) return;

    if (part.kind === "text") {
      answer += part.value;
      const last = responseHistory.at(-1);
      if (last?.role === "assistant" && "content" in last) last.content += part.value;
      else responseHistory.push({ role: "assistant", content: part.value });
      yield { type: "token", text: part.value };
      return;
    }

    if (part.kind === "data") {
      if (part.value.type === "state" && part.value.value && typeof part.value.value === "object") {
        latestState = part.value.value as Record<string, unknown>;
      }
      generatedQuery = queryFromData(part.value) ?? generatedQuery;
      return;
    }

    if (part.kind === "tool_call") {
      const callId = String(part.value.toolCallId ?? "");
      const name = String(part.value.toolName ?? "");
      const id = ++nextStepId;
      const label = toolLabel(name);
      if (callId) active.set(callId, { id, label });
      responseHistory.push({
        role: "assistant",
        tool_calls: [{ id: callId, name, arguments: part.value.args }],
      });
      yield { type: "step", id, text: label, done: false };
      return;
    }

    if (part.kind === "tool_result") {
      const callId = String(part.value.toolCallId ?? "");
      responseHistory.push({ role: "tool", content: part.value.result, tool_call_id: callId });
      const current = active.get(callId);
      if (current) {
        steps.push(current.label);
        active.delete(callId);
        yield { type: "step", id: current.id, text: current.label, done: true };
      }
      return;
    }

    if (part.kind === "error") streamedError = part.value;
  };

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (!line) continue;
        for await (const event of process(line)) yield event;
      }
    }
    if (buffer.trim()) {
      for await (const event of process(buffer.trim())) yield event;
    }
  } catch (e) {
    if (signal?.aborted) throw e;
    throw new GatewayError(502, "Analiz akışı kesildi.", String(e));
  }

  if (streamedError) {
    throw new GatewayError(502, "Analiz servisi yanıt üretemedi.", scrub(JSON.stringify(streamedError).slice(0, 800)));
  }

  const result = await executeGeneratedQuery(ctx, generatedQuery, signal);
  const sql = nativeSql(generatedQuery);
  const next: NativeEngineContext = {
    ...native,
    history: [
      ...native.history,
      { role: "user", content: input.message },
      ...responseHistory,
    ],
    state: latestState,
  };

  yield {
    type: "done",
    answer: scrub(answer.trim()) || (result ? "Sonuç aşağıda." : "Analiz tamamlandı."),
    sql,
    result,
    steps,
    durationMs: Date.now() - startedAt,
    engineContext: sealEngineContext(next),
  };
}
