import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));

import type { TenantContext } from "@/server/metabase/guard";
import { nativeAnswerStream, parseNativeLine, type NativeChatCopy } from "./native-chat";

const COPY: NativeChatCopy = {
  searching: "searching",
  constructing: "constructing",
  analyzing: "analyzing",
  working: "working",
  resultReady: "result ready",
  completed: "completed",
};

const CTX: TenantContext = {
  tenant: {
    slug: "boyahane",
    name: "Boyahane",
    apiKey: "mb_test_key",
    databaseId: 1,
    collectionId: 2,
    dashboardId: 3,
    schema: "public",
  },
  role: "owner",
  userId: "user-1",
  orgId: "org-1",
};

function stream(lines: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(lines.join("\n") + "\n"));
      controller.close();
    },
  });
}

function nativeResponse(
  {
    text,
    stateId,
    queryId,
  }: { text: string; stateId: string; queryId: string },
): Response {
  return new Response(
    stream([
      'f:{"messageId":"m1"}',
      '9:{"toolCallId":"tc1","toolName":"nlq_search","args":"{\\\"query\\\":\\\"sales\\\"}"}',
      'a:{"toolCallId":"tc1","result":{"ok":true}}',
      `2:${JSON.stringify({
        type: "state",
        version: 1,
        value: { query: { id: stateId } },
      })}`,
      `2:${JSON.stringify({
        type: "generated_entity",
        version: 1,
        value: {
          type: "card",
          id: queryId,
          title: "Sales",
          query: {
            id: queryId,
            query: {
              database: 1,
              type: "query",
              query: { "source-table": 10 },
            },
          },
        },
      })}`,
      `0:${JSON.stringify(text)}`,
      'd:{"finishReason":"stop"}',
    ]),
    { status: 202, headers: { "Content-Type": "text/event-stream" } },
  );
}

function datasetResponse(value: number): Response {
  return Response.json({
    status: "completed",
    row_count: 1,
    data: {
      cols: [{ name: "sum", display_name: "Sum", base_type: "type/Float" }],
      rows: [[value]],
    },
  });
}

async function collect(
  input: Parameters<typeof nativeAnswerStream>[1],
  signal?: AbortSignal,
) {
  const events = [];
  for await (const event of nativeAnswerStream(CTX, input, signal)) {
    events.push(event);
  }
  return events;
}

describe("native Metabot stream parser", () => {
  it("parses text/tool/state protocol without exposing reasoning", () => {
    expect(parseNativeLine('0:"Merhaba"')).toEqual({ kind: "text", value: "Merhaba" });
    expect(
      parseNativeLine('9:{"toolCallId":"t1","toolName":"nlq_search","args":"{}"}'),
    ).toEqual({
      kind: "tool_call",
      value: { toolCallId: "t1", toolName: "nlq_search", args: "{}" },
    });
    expect(
      parseNativeLine('2:{"type":"state","version":1,"value":{"query":{"id":"x"}}}'),
    ).toEqual({
      kind: "data",
      value: { type: "state", version: 1, value: { query: { id: "x" } } },
    });
  });

  it("ignores unknown protocol prefixes", () => {
    expect(parseNativeLine('x:{"private":"ignored"}')).toBeNull();
  });
});

describe("native Metabot adapter contract", () => {
  const originalSecret = process.env.BETTER_AUTH_SECRET;

  beforeEach(() => {
    process.env.BETTER_AUTH_SECRET = "native-adapter-test-secret";
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    if (originalSecret === undefined) delete process.env.BETTER_AUTH_SECRET;
    else process.env.BETTER_AUTH_SECRET = originalSecret;
  });

  it("maps native tool/text/query output to existing Dima events and QueryResult", async () => {
    const requests: { url: string; body: unknown; apiKey: string | null }[] = [];
    const fakeFetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      requests.push({
        url,
        body: typeof init?.body === "string" ? JSON.parse(init.body) : null,
        apiKey: new Headers(init?.headers).get("X-API-Key"),
      });
      if (url.endsWith("/api/metabot/agent-streaming")) {
        return nativeResponse({ text: "Toplam 120.", stateId: "state-q1", queryId: "query-q1" });
      }
      if (url.endsWith("/api/dataset")) return datasetResponse(120);
      return new Response("not found", { status: 404 });
    });
    vi.stubGlobal("fetch", fakeFetch);

    const events = await collect({
      productConversationId: "11111111-1111-4111-8111-111111111111",
      message: "Q1",
      maxRows: 500,
      copy: COPY,
    });

    expect(events.map((event) => event.type)).toEqual([
      "step",
      "step",
      "token",
      "done",
    ]);
    const done = events.at(-1);
    expect(done?.type).toBe("done");
    if (done?.type !== "done") throw new Error("missing done event");
    expect(done.answer).toBe("Toplam 120.");
    expect(done.result).toEqual({
      columns: ["sum"],
      rows: [{ sum: 120 }],
      row_count: 1,
    });
    expect(done.engineContext).toBeTruthy();

    expect(requests).toHaveLength(2);
    expect(requests[0].apiKey).toBe("mb_test_key");
    expect(requests[0].body).toMatchObject({
      profile_id: "nlq",
      message: "Q1",
      history: [],
      state: {},
      debug: false,
    });
    expect(requests[1].body).toMatchObject({
      database: 1,
      type: "query",
      constraints: {
        "max-results": 500,
        "max-results-bare-rows": 500,
      },
    });
  });

  it("carries the same native conversation id, history and state across turns", async () => {
    const nativeBodies: Record<string, unknown>[] = [];
    let turn = 0;
    const fakeFetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/api/metabot/agent-streaming")) {
        nativeBodies.push(
          typeof init?.body === "string"
            ? (JSON.parse(init.body) as Record<string, unknown>)
            : {},
        );
        turn += 1;
        return nativeResponse({
          text: turn === 1 ? "A1" : "A2",
          stateId: turn === 1 ? "state-q1" : "state-q2",
          queryId: turn === 1 ? "query-q1" : "query-q2",
        });
      }
      if (url.endsWith("/api/dataset")) return datasetResponse(turn === 1 ? 120 : 80);
      return new Response("not found", { status: 404 });
    });
    vi.stubGlobal("fetch", fakeFetch);

    const first = await collect({
      productConversationId: "22222222-2222-4222-8222-222222222222",
      message: "Q1",
      maxRows: 2_000,
      copy: COPY,
    });
    const firstDone = first.at(-1);
    if (firstDone?.type !== "done") throw new Error("Q1 missing done");

    const second = await collect({
      productConversationId: "22222222-2222-4222-8222-222222222222",
      message: "Q2",
      engineContext: firstDone.engineContext,
      maxRows: 2_000,
      copy: COPY,
    });
    expect(second.at(-1)?.type).toBe("done");

    expect(nativeBodies).toHaveLength(2);
    expect(nativeBodies[1].conversation_id).toBe(nativeBodies[0].conversation_id);
    expect(nativeBodies[1].state).toEqual({ query: { id: "state-q1" } });
    expect(nativeBodies[1].history).toEqual([
      {
        role: "assistant",
        tool_calls: [
          {
            id: "tc1",
            name: "nlq_search",
            arguments: '{"query":"sales"}',
          },
        ],
      },
      { role: "tool", content: { ok: true }, tool_call_id: "tc1" },
      { role: "assistant", content: "A1" },
      { role: "user", content: "Q1" },
    ]);
  });

  it("propagates abort to the engine request and never fabricates a fallback answer", async () => {
    const fakeFetch = vi.fn(
      (input: RequestInfo | URL, init?: RequestInit): Promise<Response> =>
        new Promise((resolve, reject) => {
          const signal = init?.signal;
          if (signal?.aborted) {
            reject(signal.reason);
            return;
          }
          signal?.addEventListener(
            "abort",
            () => reject(signal.reason ?? new DOMException("Aborted", "AbortError")),
            { once: true },
          );
          void resolve;
          void input;
        }),
    );
    vi.stubGlobal("fetch", fakeFetch);

    const controller = new AbortController();
    const generator = nativeAnswerStream(
      CTX,
      {
        productConversationId: "33333333-3333-4333-8333-333333333333",
        message: "Q1",
        maxRows: 500,
        copy: COPY,
      },
      controller.signal,
    );
    const pending = generator.next();
    controller.abort(new DOMException("Stopped", "AbortError"));

    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
    expect(fakeFetch).toHaveBeenCalledTimes(1);
  });
});
