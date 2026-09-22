import "server-only";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import type { Role } from "./metabase/guard";

export interface ShellContext {
  user: { name: string; email: string };
  orgs: { id: string; name: string; slug: string }[];
  activeOrgId: string | null;
  role: Role | null;
}

/** Session + organizations for the app shell. Redirects to /login when signed out. */
export async function shellContext(): Promise<ShellContext> {
  const h = await headers();
  const session = await auth.api.getSession({ headers: h });
  if (!session) redirect("/login");
  const [orgs, member] = await Promise.all([
    auth.api.listOrganizations({ headers: h }),
    session.session.activeOrganizationId
      ? auth.api.getActiveMember({ headers: h }).catch(() => null)
      : Promise.resolve(null),
  ]);
  return {
    user: { name: session.user.name, email: session.user.email },
    orgs: orgs.map((o) => ({ id: o.id, name: o.name, slug: o.slug })),
    activeOrgId: session.session.activeOrganizationId ?? null,
    role: (member?.role as Role | undefined) ?? null,
  };
}

export const canAnalyze = (role: Role | null) => role === "owner" || role === "admin";
