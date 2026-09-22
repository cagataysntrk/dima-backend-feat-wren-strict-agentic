import { z } from "zod";
import { addMember, listMembers, removeMember, setRole } from "@/server/members";
import { withSession } from "@/server/http";

const Add = z.object({
  email: z.string().min(3).max(200),
  name: z.string().min(2).max(120),
  role: z.enum(["admin", "member"]),
});
const Patch = z.object({ memberId: z.string().min(1), role: z.enum(["admin", "member"]) });
const Remove = z.object({ memberId: z.string().min(1) });

export const GET = withSession(() => listMembers());

export const POST = withSession(async (req) => addMember(Add.parse(await req.json())));

export const PATCH = withSession(async (req) => {
  const { memberId, role } = Patch.parse(await req.json());
  await setRole(memberId, role);
  return { ok: true };
});

export const DELETE = withSession(async (req) => {
  const { memberId } = Remove.parse(await req.json());
  await removeMember(memberId);
  return { ok: true };
});
