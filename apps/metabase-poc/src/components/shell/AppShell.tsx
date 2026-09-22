"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useTheme } from "next-themes";
import { Building2, Database, LayoutGrid, LogOut, Moon, Sun, Upload } from "lucide-react";
import { toast } from "sonner";
import { authClient } from "@/lib/auth-client";
import { cn } from "@/lib/utils";
import { BrandMark } from "@/components/BrandMark";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface Props {
  user: { name: string; email: string };
  orgs: { id: string; name: string; slug: string }[];
  activeOrgId: string | null;
  canAnalyze: boolean;
  children: React.ReactNode;
}

export function AppShell({ user, orgs, activeOrgId, canAnalyze, children }: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { resolvedTheme, setTheme } = useTheme();

  const nav = [
    { href: "/app", label: "Genel bakış", icon: LayoutGrid, show: true },
    { href: "/app/sql", label: "SQL", icon: Database, show: canAnalyze },
    { href: "/app/upload", label: "Veri yükle", icon: Upload, show: canAnalyze },
  ].filter((n) => n.show);

  async function switchOrg(organizationId: string) {
    const { error } = await authClient.organization.setActive({ organizationId });
    if (error) {
      toast.error("Şirket değiştirilemedi.");
      return;
    }
    // Everything cached belongs to the previous tenant.
    queryClient.clear();
    router.push("/app");
    router.refresh();
  }

  async function signOut() {
    await authClient.signOut();
    queryClient.clear();
    router.replace("/login");
    router.refresh();
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
          <Link href="/app" aria-label="dima — genel bakış" className="shrink-0">
            <BrandMark size="sm" />
          </Link>
          <nav className="flex min-w-0 items-center gap-1 overflow-x-auto">
            {nav.map(({ href, label, icon: Icon }) => {
              const active = href === "/app" ? pathname === "/app" : pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm whitespace-nowrap transition-colors",
                    active
                      ? "bg-accent font-medium text-foreground"
                      : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
                  )}
                >
                  <Icon className="size-4" aria-hidden />
                  {label}
                </Link>
              );
            })}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            {orgs.length > 1 ? (
              <Select value={activeOrgId ?? undefined} onValueChange={switchOrg}>
                <SelectTrigger size="sm" className="h-8 gap-1.5 text-sm" aria-label="Şirket">
                  <Building2 className="size-4 text-muted-foreground" aria-hidden />
                  <SelectValue placeholder="Şirket seçin" />
                </SelectTrigger>
                <SelectContent align="end">
                  {orgs.map((o) => (
                    <SelectItem key={o.id} value={o.id}>
                      {o.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <span className="hidden items-center gap-1.5 text-sm text-muted-foreground sm:flex">
                <Building2 className="size-4" aria-hidden />
                {orgs[0]?.name}
              </span>
            )}
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Temayı değiştir"
              onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            >
              <Sun className="size-4 dark:hidden" aria-hidden />
              <Moon className="hidden size-4 dark:block" aria-hidden />
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="gap-2" aria-label="Hesap">
                  <span className="grid size-6 place-items-center rounded-full bg-brand text-[11px] font-semibold text-brand-foreground">
                    {user.name.slice(0, 1).toLocaleUpperCase("tr-TR")}
                  </span>
                  <span className="hidden text-sm md:inline">{user.name}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="text-sm font-medium">{user.name}</div>
                  <div className="truncate text-xs text-muted-foreground">{user.email}</div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={signOut}>
                  <LogOut className="size-4" aria-hidden />
                  Çıkış yap
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 md:py-8">{children}</main>
    </div>
  );
}
