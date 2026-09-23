import type { QueryResult } from "@dima/contracts";

export type NativeHistoryEntry =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string }
  | {
      role: "assistant";
      tool_calls: { id: string; name: string; arguments?: string }[];
    }
  | { role: "tool"; content: unknown; tool_call_id: string };

export interface NativeEngineContext {
  version: 1;
  tenantSlug: string;
  productConversationId: string;
  engineConversationId: string;
  history: NativeHistoryEntry[];
  state: Record<string, unknown>;
}

export type NativeDataPart = {
  type: string;
  version?: number;
  value?: unknown;
};

export type NativeChatEvent =
  | { type: "step"; id: number; text: string; done: boolean }
  | { type: "token"; text: string }
  | {
      type: "done";
      answer: string;
      sql: string | null;
      result: QueryResult | null;
      steps: string[];
      durationMs: number;
      engineContext: string;
    }
  | { type: "error"; message: string };
