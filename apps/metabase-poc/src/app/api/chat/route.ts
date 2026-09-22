import { z } from "zod";
import { answer } from "@/server/chat/agent";
import { GatewayError } from "@/server/metabase/errors";
import { withTenant } from "@/server/http";

// Model calls + several queries can take a while.
export const maxDuration = 120;

const Body = z.object({
  messages: z
    .array(z.object({ role: z.enum(["user", "assistant"]), content: z.string().min(1).max(24_000) }))
    .min(1)
    .max(20)
    .refine((m) => m[m.length - 1].role === "user", "last message must be the user's"),
});

export const POST = withTenant(async (ctx, req) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  // Keep the conversation short: the last few turns carry the context that matters.
  return answer(ctx, body.data.messages.slice(-10));
});
