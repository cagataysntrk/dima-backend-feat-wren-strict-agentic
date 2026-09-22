// Server-sent-event plumbing for the streaming chat. Pure and unit-tested:
// the network is the caller's problem, the parsing is here.
//
// Two jobs:
//   1. Frame a byte stream into SSE events (they arrive split at any offset).
//   2. Re-assemble OpenAI-style tool calls, whose JSON arguments are streamed
//      character by character across many deltas and are only parseable whole.

/** Split what we have so far into complete frames, keeping the incomplete tail. */
export function splitFrames(buffer: string): { frames: string[]; rest: string } {
  const parts = buffer.split(/\r?\n\r?\n/);
  const rest = parts.pop() ?? "";
  return { frames: parts.filter((f) => f.trim() !== ""), rest };
}

/** The `data:` payload of one frame, or null for comments/keep-alives. */
export function frameData(frame: string): string | null {
  const lines = frame.split(/\r?\n/).filter((l) => l.startsWith("data:"));
  if (lines.length === 0) return null;
  return lines.map((l) => l.slice(5).trim()).join("\n");
}

export interface ToolCallDelta {
  index: number;
  id?: string;
  function?: { name?: string; arguments?: string };
}

export interface StreamedToolCall {
  id: string;
  name: string;
  arguments: string;
}

/**
 * Merge a round's tool-call deltas. Later chunks append to `arguments` and may
 * fill in an id or name that the first chunk omitted.
 */
export function mergeToolCalls(acc: StreamedToolCall[], deltas: ToolCallDelta[] | undefined): StreamedToolCall[] {
  if (!deltas?.length) return acc;
  const out = acc.slice();
  for (const d of deltas) {
    const at = d.index ?? 0;
    const cur = out[at] ?? { id: "", name: "", arguments: "" };
    out[at] = {
      id: d.id || cur.id,
      name: d.function?.name || cur.name,
      arguments: cur.arguments + (d.function?.arguments ?? ""),
    };
  }
  return out;
}

/** Tool calls that are complete enough to run (id, name and parseable JSON). */
export function usableToolCalls(calls: StreamedToolCall[]): StreamedToolCall[] {
  return calls.filter((c) => {
    if (!c.id || !c.name) return false;
    try {
      JSON.parse(c.arguments || "{}");
      return true;
    } catch {
      return false;
    }
  });
}

/** One SSE line for our own stream to the browser. */
export function sseFrame(event: unknown): string {
  return `data: ${JSON.stringify(event)}\n\n`;
}
