import "server-only";
import { randomBytes } from "node:crypto";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { GatewayError } from "./metabase/errors";
import type { Role } from "./metabase/guard";

export interface Member {
  id: string;
  userId: string;
  name: string;
  email: string;
  role: Role;
  createdAt: string;
}

const ROLES: Role[] = ["owner", "admin", "member"];
export const isRole = (v: unknown): v is Role => typeof v === "string" && ROLES.includes(v as Role);

/** The caller's session, organization and role — every members call starts here. */
async function context() {
  const h = await headers();
  const session = await auth.api.getSession({ headers: h });
  const orgId = session?.session.activeOrganizationId;
  if (!session || !orgId) throw new GatewayError(401, "Oturum bulunamadı.");
  const me = await auth.api.getActiveMember({ headers: h }).catch(() => null);
  if (!me) throw new GatewayError(403, "Bu şirkete erişiminiz yok.");
  return { h, orgId, userId: session.user.id, role: me.role as Role, memberId: me.id };
}

/** Only owners change who is in the company — admins can analyse, not administer. */
async function requireOwner() {
  const ctx = await context();
  if (ctx.role !== "owner") throw new GatewayError(403, "Bu işlem için şirket sahibi olmanız gerekir.");
  return ctx;
}

export async function listMembers(): Promise<{ members: Member[]; myRole: Role; myMemberId: string }> {
  const { h, role, memberId } = await context();
  const res = await auth.api.listMembers({ headers: h });
  const members = res.members.map((m) => ({
    id: m.id,
    userId: m.userId,
    name: m.user?.name ?? m.user?.email ?? "—",
    email: m.user?.email ?? "",
    role: (isRole(m.role) ? m.role : "member") as Role,
    createdAt: new Date(m.createdAt).toISOString(),
  }));
  // Owners first, then alphabetical — the list reads as a hierarchy.
  members.sort((a, b) => ROLES.indexOf(a.role) - ROLES.indexOf(b.role) || a.name.localeCompare(b.name, "tr"));
  return { members, myRole: role, myMemberId: memberId };
}

/** A password the owner reads out once. No mailer in the POC, so no invite link. */
function tempPassword() {
  // 18 URL-safe chars — comfortably over the 10-char minimum in auth.ts.
  return randomBytes(14).toString("base64url");
}

/**
 * Add a member. Public sign-up stays off, so a brand-new user is created
 * through the same internals the sign-up route uses (hash → user → credential
 * account) rather than by turning sign-up on.
 */
export async function addMember(input: { email: string; name: string; role: Role }) {
  const { orgId } = await requireOwner();
  const email = input.email.trim().toLowerCase();
  const name = input.name.trim();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new GatewayError(400, "Geçerli bir e-posta girin.");
  if (name.length < 2) throw new GatewayError(400, "Ad en az 2 karakter olmalı.");
  if (input.role === "owner") throw new GatewayError(400, "Şirket sahibi bu ekrandan eklenemez.");

  const ctx = await auth.$context;
  const existing = await ctx.internalAdapter.findUserByEmail(email);
  let userId = existing?.user.id;
  let password: string | null = null;

  if (!userId) {
    password = tempPassword();
    const hash = await ctx.password.hash(password);
    const created = await ctx.internalAdapter.createUser(
      { email, name, emailVerified: false },
      { method: "email-password" },
    );
    if (!created) throw new GatewayError(500, "Kullanıcı oluşturulamadı.");
    userId = created.id;
    await ctx.internalAdapter.linkAccount({
      userId: created.id,
      providerId: "credential",
      accountId: created.id,
      password: hash,
    });
  }

  const already = await auth.api
    .listMembers({ headers: await headers() })
    .then((r) => r.members.some((m) => m.userId === userId));
  if (already) throw new GatewayError(409, "Bu kişi zaten ekipte.");

  await auth.api.addMember({ body: { userId, organizationId: orgId, role: input.role } });
  // `password` is null for an existing user — they keep the one they have.
  return { password };
}

export async function setRole(memberId: string, role: Role) {
  const { orgId, memberId: mine } = await requireOwner();
  if (memberId === mine) throw new GatewayError(400, "Kendi rolünüzü değiştiremezsiniz.");
  await auth.api.updateMemberRole({
    headers: await headers(),
    body: { memberId, role, organizationId: orgId },
  });
}

export async function removeMember(memberId: string) {
  const { orgId, memberId: mine } = await requireOwner();
  if (memberId === mine) throw new GatewayError(400, "Kendinizi ekipten çıkaramazsınız.");
  await auth.api.removeMember({
    headers: await headers(),
    body: { memberIdOrEmail: memberId, organizationId: orgId },
  });
}
