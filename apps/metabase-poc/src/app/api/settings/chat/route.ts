import { z } from "zod";
import { chatPrefs, setChatPrefs } from "@/server/prefs";
import { withSession } from "@/server/http";

const Patch = z.object({ model: z.string().optional(), maxRows: z.number().int().optional() });

export const GET = withSession(() => chatPrefs());

export const PUT = withSession(async (req) => setChatPrefs(Patch.parse(await req.json())));
