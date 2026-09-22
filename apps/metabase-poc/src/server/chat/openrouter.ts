import "server-only";
import { GatewayError } from "../metabase/errors";
import { frameData, mergeToolCalls, splitFrames, type StreamedToolCall, type ToolCallDelta } from "@/lib/sse";

// Minimal OpenRouter client (OpenAI-compatible chat completions + tool calling).
// Plain fetch on purpose: one endpoint, no SDK dependency. Key and model are
// server-side env vars and never reach the browser.

const ENDPOINT = "https://openrouter.ai/api/v1/chat/completions";
const TIMEOUT_MS = 120_000;
// Lightweight, cheap and tool-capable; pinned (not a "~latest" alias) so behaviour is stable.
export const DEFAULT_MODEL = "openai/gpt-5.6-sol";

export interface ToolCall {
  id: string;
  type: "function";
  function: { name: string; arguments: string };
}

export type ChatMessage =
  | { role: "system"; content: string }
  | { role: "user"; content: string }
  | { role: "assistant"; content: string | null; tool_calls?: ToolCall[] }
  | { role: "tool"; tool_call_id: string; content: string };

export interface ToolSpec {
  type: "function";
  function: { name: string; description: string; parameters: Record<string, unknown> };
}

interface CompletionResponse {
  choices?: {
    finish_reason: string | null;
    message: { content: string | null; tool_calls?: ToolCall[] };
  }[];
  error?: { message?: string; code?: number };
}

/** One place for the wording of upstream failures (credits, rate limit, bad key). */
function upstreamError(status: number, message: string): GatewayError {
  const detail = `openrouter ${status}: ${message}`;
  if (status === 429) return new GatewayError(429, "Çok fazla istek; biraz sonra tekrar deneyin.", detail);
  if (status === 402) {
    return new GatewayError(503, "Sohbet servisinin kullanım kredisi tükendi; yöneticinize bildirin.", detail);
  }
  if (status === 401) return new GatewayError(503, "Sohbet servisi yapılandırması geçersiz.", detail);
  return new GatewayError(502, "Sohbet servisi şu anda yanıt vermiyor.", detail);
}

export function chatConfigured(): boolean {
  return Boolean(process.env.OPENROUTER_API_KEY);
}

/** toolChoice "none" forces a text answer while keeping tool definitions (required once history has tool calls). */
export async function complete(messages: ChatMessage[], tools: ToolSpec[], toolChoice: "auto" | "none" = "auto") {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new GatewayError(503, "Sohbet servisi henüz yapılandırılmadı.", "OPENROUTER_API_KEY is not set");
  let res: Response;
  try {
    res = await fetch(ENDPOINT, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        "X-Title": "dima",
      },
      body: JSON.stringify({
        model: process.env.OPENROUTER_MODEL || DEFAULT_MODEL,
        messages,
        tools,
        tool_choice: toolChoice,
        max_tokens: 4000,
        // Unified reasoning control: a little thinking helps SQL, "low" keeps it fast and cheap.
        reasoning: { effort: "low" },
      }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (e) {
    throw new GatewayError(504, "Sohbet servisi yanıt vermedi, tekrar deneyin.", String(e));
  }
  const body = (await res.json().catch(() => ({}))) as CompletionResponse;
  if (!res.ok || body.error || !body.choices?.[0]) {
    throw upstreamError(res.status, body.error?.message ?? "no choices");
  }
  return body.choices[0];
}

export interface StreamChunk {
  /** Answer text as it is produced. */
  text?: string;
  /** Tool calls so far this round (complete only when the round ends). */
  toolCalls?: StreamedToolCall[];
  /** Set on the last chunk of a round. */
  finish?: string | null;
}

interface StreamDelta {
  choices?: { delta?: { content?: string | null; tool_calls?: ToolCallDelta[] }; finish_reason?: string | null }[];
  error?: { message?: string };
}

/**
 * Same request as `complete`, streamed. Yields text as it arrives and the
 * re-assembled tool calls at the end of the round, so the caller can report
 * real progress instead of waiting for the whole answer.
 */
export async function* streamComplete(
  messages: ChatMessage[],
  tools: ToolSpec[],
  toolChoice: "auto" | "none" = "auto",
  signal?: AbortSignal,
): AsyncGenerator<StreamChunk> {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new GatewayError(503, "Sohbet servisi henüz yapılandırılmadı.", "OPENROUTER_API_KEY is not set");

  let res: Response;
  try {
    res = await fetch(ENDPOINT, {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json", "X-Title": "dima" },
      body: JSON.stringify({
        model: process.env.OPENROUTER_MODEL || DEFAULT_MODEL,
        messages,
        tools,
        tool_choice: toolChoice,
        max_tokens: 4000,
        reasoning: { effort: "low" },
        stream: true,
      }),
      signal: signal ?? AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (e) {
    throw new GatewayError(504, "Sohbet servisi yanıt vermedi, tekrar deneyin.", String(e));
  }
  if (!res.ok || !res.body) throw upstreamError(res.status, await res.text().catch(() => ""));

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let calls: StreamedToolCall[] = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const { frames, rest } = splitFrames(buffer);
    buffer = rest;
    for (const frame of frames) {
      const data = frameData(frame);
      if (!data || data === "[DONE]") continue;
      let parsed: StreamDelta;
      try {
        parsed = JSON.parse(data);
      } catch {
        continue; // a keep-alive or a frame we don't understand
      }
      if (parsed.error) throw new GatewayError(502, "Sohbet servisi şu anda yanıt vermiyor.", parsed.error.message);
      const choice = parsed.choices?.[0];
      if (!choice) continue;
      calls = mergeToolCalls(calls, choice.delta?.tool_calls);
      const text = choice.delta?.content ?? "";
      if (text) yield { text };
      if (choice.finish_reason) yield { toolCalls: calls, finish: choice.finish_reason };
    }
  }
}
