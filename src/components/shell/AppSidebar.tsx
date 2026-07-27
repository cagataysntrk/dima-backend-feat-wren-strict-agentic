"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import {
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  Database,
  LayoutDashboard,
  ListFilter,
  MessageSquarePlus,
  MessagesSquare,
  Search,
  SquarePen,
} from "lucide-react";
import { useConversations } from "@/stores/conversations";
import { BrandMark } from "@/components/BrandMark";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Kbd } from "@/components/ui/kbd";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { NotificationsPopover } from "./NotificationsPopover";
import { AccountMenu } from "./AccountMenu";
import { Onboarding } from "./Onboarding";

/**
 * ChatGPT-style left nav. `collapsible="offcanvas"`: it collapses AWAY entirely —
 * no icon rail — so the reading column gets the whole viewport. The icons come
 * back on hover at the left edge (see AppShell's HoverRail).
 */
type ChatFilter = "all" | "named" | "empty";

export function AppSidebar({
  onNewChat,
  onSelectConversation,
  onOpenSchema,
  onOpenHelp,
  onOpenDashboards,
  onOpenSearch,
  onOpenShortcuts,
}: {
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onOpenSchema: () => void;
  onOpenHelp: () => void;
  onOpenDashboards: () => void;
  onOpenSearch: () => void;
  onOpenShortcuts: () => void;
}) {
  const t = useTranslations();
  const conversations = useConversations((s) => s.conversations);
  const activeId = useConversations((s) => s.activeId);
  const [filter, setFilter] = useState<ChatFilter>("all");

  const shown = conversations.filter((c) =>
    filter === "named" ? !!c.title : filter === "empty" ? !c.title : true,
  );

  // Sohbetler arası gezinme: aktifin bir öncesi/sonrası (filtrelenmiş listede).
  const idx = shown.findIndex((c) => c.id === activeId);
  const go = (delta: number) => {
    if (!shown.length) return;
    const next = idx < 0 ? 0 : Math.min(shown.length - 1, Math.max(0, idx + delta));
    onSelectConversation(shown[next].id);
  };

  return (
    <Sidebar collapsible="offcanvas">
      <SidebarHeader className="gap-2 pt-0">
        {/* h-12 + pt-0: logo satırının merkezi, ana paneldeki üst barın (h-12)
            ikonlarıyla aynı yatay eksende dursun */}
        <div className="flex h-12 items-center justify-between px-2">
          {/* logo — sadece marka; harf-harf hover açıklamaları kapalı (pillars) */}
          <BrandMark size="sm" />
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={t("common.search")}
                onClick={onOpenSearch}
                className="text-muted-foreground hover:text-foreground"
              >
                <Search className="size-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="flex items-center gap-1.5">
              {t("common.search")}
              <Kbd className="bg-background/20 text-background dark:bg-background/15">⌘K</Kbd>
            </TooltipContent>
          </Tooltip>
        </div>

        <SidebarMenu>
          <SidebarMenuItem className="flex items-center gap-1">
            <SidebarMenuButton onClick={onNewChat} className="min-w-0 flex-1">
              <MessageSquarePlus className="size-4" />
              <span>{t("common.newChat")}</span>
            </SidebarMenuButton>
            {/* Sohbetler arası gezinme — listeye gitmeden bir önceki/sonraki */}
            <div className="flex shrink-0 items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Önceki sohbet"
                    disabled={idx <= 0}
                    onClick={() => go(-1)}
                    className="size-6 text-muted-foreground transition-transform hover:-translate-x-0.5 hover:text-foreground"
                  >
                    <ChevronLeft className="size-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">Önceki sohbet</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Sonraki sohbet"
                    disabled={idx < 0 || idx >= shown.length - 1}
                    onClick={() => go(1)}
                    className="size-6 text-muted-foreground transition-transform hover:translate-x-0.5 hover:text-foreground"
                  >
                    <ChevronRight className="size-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">Sonraki sohbet</TooltipContent>
              </Tooltip>
            </div>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={onOpenSchema}>
              <Database className="size-4" />
              <span>{t("chat.dataSources")}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={onOpenDashboards}>
              <LayoutDashboard className="size-4" />
              <span>Panolar</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup className="group/recents">
          {/* başlık şeridi — ikonlar yalnız hover'da (ChatGPT "Recents") */}
          <div className="flex items-center justify-between gap-1 pr-1">
            <SidebarGroupLabel className="gap-1">
              {t("chat.conversations")}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link
                    href="/chats"
                    aria-label="Tüm sohbetler"
                    className="rounded p-0.5 text-muted-foreground transition-transform hover:-translate-y-px hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none"
                  >
                    <ArrowUpRight className="size-3.5" />
                  </Link>
                </TooltipTrigger>
                <TooltipContent side="bottom">Tüm sohbetler</TooltipContent>
              </Tooltip>
            </SidebarGroupLabel>
            <div className="flex shrink-0 items-center opacity-0 transition-opacity group-hover/recents:opacity-100 focus-within:opacity-100">
              <DropdownMenu>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        aria-label="Filtrele"
                        className="size-6 text-muted-foreground hover:text-foreground"
                      >
                        <ListFilter className="size-4" />
                      </Button>
                    </DropdownMenuTrigger>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Filtrele</TooltipContent>
                </Tooltip>
                <DropdownMenuContent align="end" className="w-40">
                  <DropdownMenuRadioGroup
                    value={filter}
                    onValueChange={(v) => setFilter(v as ChatFilter)}
                  >
                    <DropdownMenuRadioItem value="all">Tümü</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="named">Adlandırılmış</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="empty">Boş</DropdownMenuRadioItem>
                  </DropdownMenuRadioGroup>
                </DropdownMenuContent>
              </DropdownMenu>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label={t("common.newChat")}
                    onClick={onNewChat}
                    className="size-6 text-muted-foreground hover:text-foreground"
                  >
                    <SquarePen className="size-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">{t("common.newChat")}</TooltipContent>
              </Tooltip>
            </div>
          </div>

          <SidebarGroupContent>
            <SidebarMenu>
              {shown.length === 0 && (
                <div className="px-2 py-1.5 text-xs text-muted-foreground">—</div>
              )}
              {shown.map((c) => (
                <SidebarMenuItem key={c.id} className="group/row">
                  <SidebarMenuButton
                    isActive={c.id === activeId}
                    onClick={() => onSelectConversation(c.id)}
                    title={c.title || t("common.newChat")}
                  >
                    <MessagesSquare className="size-4" />
                    {/* uzun ad: hover'da kayar, aksi halde kırpılır */}
                    <span className="min-w-0 flex-1 overflow-hidden">
                      <span className="dima-marquee dima-marquee-run">
                        {c.title || t("common.newChat")}
                      </span>
                    </span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <Onboarding />
          </SidebarMenuItem>
          {/* -mx-2: SidebarFooter'ın p-2'sini iptal edip çizgiyi kenarlara birleştirir */}
          <SidebarSeparator className="-mx-2 my-1 w-auto" />
          <SidebarMenuItem className="flex items-center gap-1">
            <div className="min-w-0 flex-1">
              <AccountMenu onOpenHelp={onOpenHelp} onOpenShortcuts={onOpenShortcuts} />
            </div>
            <NotificationsPopover />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
