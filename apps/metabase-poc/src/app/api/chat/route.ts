import { z } from "zod";
import { answerStream } from "@/server/chat/agent";
import { chatPrefs } from "@/server/prefs";
import { GatewayError } from "@/server/metabase/errors";
import { requireTenant } from "@/server/metabase/guard";
import { sseFrame } from "@/lib/sse";

// Streaming chat: the browser gets each real step as it happens, then the
// answer token by token. Node runtime (the gateway uses node:crypto).
export const runtime = "nodejs";
export const maxDuration = 120;

const Body = z.object({
  messages: z
    .array(z.object({ role: z.enum(["user", "assistant"]), content: z.string().min(1).max(24_000) }))
    .min(1)
    .max(20)
    .refine((m) => m[m.length - 1].role === "user", "last message must be the user's"),
});

export async function POST(req: Request) {
  let events: AsyncGenerator<unknown>;
  try {
    const ctx = await requireTenant();
    const body = Body.safeParse(await req.json().catch(() => null));
    if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
    // Keep the conversation short: the last few turns carry the context that matters.
    const prefs = await chatPrefs();
    events = answerStream(ctx, body.data.messages.slice(-10), req.signal, prefs);
  } catch (e) {
    const err = e instanceof GatewayError ? e : null;
    if (err?.detail) console.warn(`[gateway] ${err.status} ${err.detail}`);
    if (!err) console.error("[gateway] unexpected", e);
    return Response.json({ error: err?.publicMessage ?? "Beklenmeyen bir hata oluştu." }, { status: err?.status ?? 500 });
  }

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const encoder = new TextEncoder();
      const send = (event: unknown) => controller.enqueue(encoder.encode(sseFrame(event)));
      try {
        for await (const event of events) {
          // The reader went away (tab closed, Stop pressed): stop generating.
          if (req.signal.aborted) break;
          send(event);
        }
      } catch (e) {
        if (!req.signal.aborted) {
          const err = e instanceof GatewayError ? e : null;
          if (err?.detail) console.warn(`[gateway] ${err.status} ${err.detail}`);
          if (!err) console.error("[gateway] unexpected", e);
          send({ type: "error", message: err?.publicMessage ?? "Beklenmeyen bir hata oluştu." });
        }
      } finally {
        await events.return?.(undefined);
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-store, no-transform",
      Connection: "keep-alive",
    },
  });
}
