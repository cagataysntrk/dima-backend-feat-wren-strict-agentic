import "server-only";
import { GatewayError } from "../metabase/errors";

// Minimal OpenRouter client (OpenAI-compatible chat completions + tool calling).
// Plain fetch on purpose: one endpoint, no SDK dependency. Key and model are
// server-side env vars and never reach the browser.

const ENDPOINT = "https://openrouter.ai/api/v1/chat/completions";
const TIMEOUT_MS = 120_000;
// Lightweight, cheap and tool-capable; pinned (not a "~latest" alias) so behaviour is stable.
export const DEFAULT_MODEL = "openai/gpt-5.6-luna";

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
    const detail = `openrouter ${res.status}: ${body.error?.message ?? "no choices"}`;
    if (res.status === 429) throw new GatewayError(429, "Çok fazla istek; biraz sonra tekrar deneyin.", detail);
    if (res.status === 402) {
      throw new GatewayError(503, "Sohbet servisinin kullanım kredisi tükendi; yöneticinize bildirin.", detail);
    }
    if (res.status === 401) throw new GatewayError(503, "Sohbet servisi yapılandırması geçersiz.", detail);
    throw new GatewayError(502, "Sohbet servisi şu anda yanıt vermiyor.", detail);
  }
  return body.choices[0];
}
