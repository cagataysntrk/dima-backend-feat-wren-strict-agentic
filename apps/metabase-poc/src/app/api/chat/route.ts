import { z } from "zod";
import { nativeAnswerStream } from "@/server/engine/native-chat";
import { GatewayError } from "@/server/metabase/errors";
import { requireTenant } from "@/server/metabase/guard";
import { localizeError } from "@/server/http";
import { sseFrame } from "@/lib/sse";

// Streaming chat: the browser gets each real step as it happens, then the
// answer token by token. Node runtime (the gateway uses node:crypto).
export const runtime = "nodejs";
export const maxDuration = 120;

const Body = z.object({
  conversationId: z.string().uuid(),
  engineContext: z.string().max(700_000).nullable().optional(),
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
    const messages = body.data.messages.slice(-10);
    const current = messages[messages.length - 1];
    events = nativeAnswerStream(
      ctx,
      {
        productConversationId: body.data.conversationId,
        message: current.content,
        engineContext: body.data.engineContext,
        // Migration bridge only: once a native context token exists, the adapter ignores this.
        legacyHistory: messages.slice(0, -1).map((message) =>
          message.role === "user"
            ? { role: "user" as const, content: message.content }
            : { role: "assistant" as const, content: message.content },
        ),
      },
      req.signal,
    );
  } catch (e) {
    const err = e instanceof GatewayError ? e : null;
    if (err?.detail) console.warn(`[gateway] ${err.status} ${err.detail}`);
    if (!err) console.error("[gateway] unexpected", e);
    return Response.json(
      { error: await localizeError(err?.publicMessage ?? "Beklenmeyen bir hata oluştu.") },
      { status: err?.status ?? 500 },
    );
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
          send({ type: "error", message: await localizeError(err?.publicMessage ?? "Beklenmeyen bir hata oluştu.") });
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
