"use client";

import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { Building2, Check } from "lucide-react";
import { toast } from "sonner";
import { authClient } from "@/lib/auth-client";
import { cn } from "@dima/ui/utils";

export function CompanySwitcher({
  orgs,
  activeOrgId,
}: {
  orgs: { id: string; name: string; slug: string }[];
  activeOrgId: string | null;
}) {
  const router = useRouter();
  const queryClient = useQueryClient();

  async function switchTo(organizationId: string) {
    if (organizationId === activeOrgId) return;
    const { error } = await authClient.organization.setActive({ organizationId });
    if (error) {
      toast.error("Şirket değiştirilemedi.");
      return;
    }
    // Everything cached belongs to the previous tenant.
    queryClient.clear();
    router.refresh();
  }

  if (orgs.length === 1) {
    return (
      <p className="text-sm">
        <span className="font-medium">{orgs[0].name}</span>{" "}
        <span className="text-muted-foreground">· başka şirkete erişiminiz yok</span>
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {orgs.map((o) => {
        const active = o.id === activeOrgId;
        return (
          <li key={o.id}>
            <button
              type="button"
              onClick={() => switchTo(o.id)}
              aria-current={active ? "true" : undefined}
              className={cn(
                "flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm transition-colors",
                active
                  ? "border-brand/40 bg-brand/10"
                  : "border-[var(--surface-edge)] hover:bg-accent",
              )}
            >
              <Building2 className="size-4 text-muted-foreground" aria-hidden />
              <span className="min-w-0 flex-1 truncate font-medium">{o.name}</span>
              {active && <Check className="size-4 text-brand" aria-hidden />}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
