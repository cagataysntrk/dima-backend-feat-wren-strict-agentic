import { AppShell } from "@/components/shell/AppShell";
import { canAnalyze, shellContext } from "@/server/session";

export default async function ProductLayout({ children }: { children: React.ReactNode }) {
  const ctx = await shellContext();
  return (
    <AppShell
      user={ctx.user}
      orgs={ctx.orgs}
      activeOrgId={ctx.activeOrgId}
      canAnalyze={canAnalyze(ctx.role)}
    >
      {children}
    </AppShell>
  );
}
