"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useTheme } from "next-themes";
import { Boxes, Building2, ChevronsUpDown, Database, LayoutGrid, LogOut, MessageSquarePlus, MessagesSquare, Moon, Settings, Share2, Sun, Table2, Trash2, Upload } from "lucide-react";
import { toast } from "sonner";
import { authClient } from "@/lib/auth-client";
import { useConversations } from "@/stores/conversations";
import { BrandMark } from "@dima/ui/brand/BrandMark";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
  useSidebar,
} from "@dima/ui/primitives/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@dima/ui/primitives/dropdown-menu";

export interface ShellUser {
  name: string;
  email: string;
}
export interface ShellOrg {
  id: string;
  name: string;
  slug: string;
}

/**
 * Left rail (apps/web pattern). Everything here is ACCOUNT-wide and opens a
 * full page; things about one chat live in the chat's right panel.
 */
export function AppSidebar({
  user,
  orgs,
  activeOrgId,
  canAnalyze,
}: {
  user: ShellUser;
  orgs: ShellOrg[];
  activeOrgId: string | null;
  canAnalyze: boolean;
}) {
  const pathname = usePathname();
  const params = useSearchParams();
  const router = useRouter();
  const { isMobile, setOpenMobile } = useSidebar();
  const conversations = useConversations((s) => s.conversations);
  const remove = useConversations((s) => s.remove);

  // Persisted chats are read after mount (skipHydration) so server and first
  // client render agree.
  useEffect(() => {
    void useConversations.persist.rehydrate();
  }, []);

  const activeChat = pathname === "/app/chat" ? params.get("c") : null;
  const chats = conversations
    .filter((c) => c.orgId === activeOrgId && c.entries.length > 0)
    .sort((a, b) => b.updatedAt - a.updatedAt);

  const nav = [
    { href: "/app", label: "Genel bakış", icon: LayoutGrid, show: true },
    { href: "/app/data", label: "Veriler", icon: Table2, show: true },
    { href: "/app/sql", label: "SQL", icon: Database, show: canAnalyze },
    { href: "/app/model", label: "Veri modeli", icon: Boxes, show: canAnalyze },
    { href: "/app/schema", label: "Şema", icon: Share2, show: true },
    { href: "/app/upload", label: "Veri yükle", icon: Upload, show: canAnalyze },
    { href: "/app/settings", label: "Ayarlar", icon: Settings, show: true },
  ].filter((n) => n.show);

  const go = (href: string) => {
    router.push(href);
    if (isMobile) setOpenMobile(false);
  };

  return (
    <Sidebar collapsible="offcanvas">
      <SidebarHeader className="gap-2 pt-0">
        <div className="flex h-12 items-center px-2">
          <Link href="/app/chat" aria-label="dima — yeni sohbet">
            <BrandMark size="sm" />
          </Link>
        </div>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={() => go("/app/chat")} isActive={pathname === "/app/chat" && !activeChat}>
              <MessageSquarePlus className="size-4" />
              <span>Yeni sohbet</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
          {nav.map(({ href, label, icon: Icon }) => {
            const active = href === "/app" ? pathname === "/app" || pathname.startsWith("/app/dashboards") || pathname.startsWith("/app/cards") : pathname.startsWith(href);
            return (
              <SidebarMenuItem key={href}>
                <SidebarMenuButton asChild isActive={active}>
                  <Link href={href} onClick={() => isMobile && setOpenMobile(false)}>
                    <Icon className="size-4" />
                    <span>{label}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Sohbetler</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {chats.length === 0 && (
                <p className="px-2 py-1.5 text-xs text-muted-foreground">Henüz sohbet yok.</p>
              )}
              {chats.map((c) => (
                <SidebarMenuItem key={c.id}>
                  <SidebarMenuButton
                    isActive={c.id === activeChat}
                    onClick={() => go(`/app/chat?c=${c.id}`)}
                    title={c.title}
                  >
                    <MessagesSquare className="size-4" />
                    <span className="truncate">{c.title || "Yeni sohbet"}</span>
                  </SidebarMenuButton>
                  <SidebarMenuAction
                    showOnHover
                    aria-label={`Sohbeti sil: ${c.title}`}
                    onClick={() => {
                      remove(c.id);
                      if (c.id === activeChat) router.replace("/app/chat");
                    }}
                  >
                    <Trash2 className="size-3.5" />
                  </SidebarMenuAction>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarSeparator className="-mx-2 w-auto" />
        <AccountMenu user={user} orgs={orgs} activeOrgId={activeOrgId} />
      </SidebarFooter>
    </Sidebar>
  );
}

/** Account + company + theme + sign-out, one menu at the bottom of the rail. */
function AccountMenu({ user, orgs, activeOrgId }: { user: ShellUser; orgs: ShellOrg[]; activeOrgId: string | null }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { resolvedTheme, setTheme } = useTheme();
  const activeOrg = orgs.find((o) => o.id === activeOrgId);

  async function switchOrg(organizationId: string) {
    if (organizationId === activeOrgId) return;
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
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton size="lg" className="data-[state=open]:bg-sidebar-accent">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand text-xs font-semibold text-brand-foreground">
                {user.name.slice(0, 1).toLocaleUpperCase("tr-TR")}
              </span>
              <span className="grid min-w-0 flex-1 text-left leading-tight">
                <span className="truncate text-sm font-medium">{user.name}</span>
                <span className="truncate text-xs text-muted-foreground">{activeOrg?.name ?? user.email}</span>
              </span>
              <ChevronsUpDown className="size-4 text-muted-foreground" aria-hidden />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent side="top" align="start" className="w-(--radix-dropdown-menu-trigger-width) min-w-56">
            <DropdownMenuLabel className="font-normal">
              <div className="text-sm font-medium">{user.name}</div>
              <div className="truncate text-xs text-muted-foreground">{user.email}</div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            {orgs.length > 1 && (
              <>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">Şirket</DropdownMenuLabel>
                <DropdownMenuRadioGroup value={activeOrgId ?? ""} onValueChange={switchOrg}>
                  {orgs.map((o) => (
                    <DropdownMenuRadioItem key={o.id} value={o.id}>
                      <Building2 className="size-4 text-muted-foreground" aria-hidden />
                      {o.name}
                    </DropdownMenuRadioItem>
                  ))}
                </DropdownMenuRadioGroup>
                <DropdownMenuSeparator />
              </>
            )}
            <DropdownMenuItem asChild>
              <Link href="/app/settings">
                <Settings className="size-4" aria-hidden />
                Ayarlar
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>
              <Sun className="size-4 dark:hidden" aria-hidden />
              <Moon className="hidden size-4 dark:block" aria-hidden />
              {resolvedTheme === "dark" ? "Açık tema" : "Koyu tema"}
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={signOut}>
              <LogOut className="size-4" aria-hidden />
              Çıkış yap
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
