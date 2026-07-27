"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import {
  Database,
  HelpCircle,
  LayoutDashboard,
  Settings,
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
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { NotificationsPopover } from "./NotificationsPopover";
import { AccountMenu } from "./AccountMenu";
import { Onboarding } from "./Onboarding";

/**
 * ChatGPT-style left nav. `collapsible="offcanvas"`: it collapses AWAY entirely —
 * no icon rail — so the reading column gets the whole viewport. The icons come
 * back on hover at the left edge (see AppShell's HoverRail).
 */
export function AppSidebar({
  onNewChat,
  onSelectConversation,
  onOpenSchema,
  onOpenHelp,
  onOpenDashboards,
  onOpenSearch,
}: {
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onOpenSchema: () => void;
  onOpenHelp: () => void;
  onOpenDashboards: () => void;
  onOpenSearch: () => void;
}) {
  const t = useTranslations();
  const conversations = useConversations((s) => s.conversations);
  const activeId = useConversations((s) => s.activeId);

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
          <SidebarMenuItem>
            <SidebarMenuButton onClick={onNewChat}>
              <MessageSquarePlus className="size-4" />
              <span>{t("common.newChat")}</span>
            </SidebarMenuButton>
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
          <SidebarMenuItem>
            <SidebarMenuButton onClick={onOpenHelp}>
              <HelpCircle className="size-4" />
              <span>{t("common.help")}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/settings">
                <Settings className="size-4" />
                <span>{t("common.settings")}</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup className="group/recents">
          {/* başlık şeridi — ikonlar yalnız hover'da (ChatGPT "Recents") */}
          <div className="flex items-center justify-between gap-1 pr-1">
            <SidebarGroupLabel>{t("chat.conversations")}</SidebarGroupLabel>
            <div className="flex shrink-0 items-center opacity-0 transition-opacity group-hover/recents:opacity-100 focus-within:opacity-100">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label={t("common.search")}
                    onClick={onOpenSearch}
                    className="size-6 text-muted-foreground hover:text-foreground"
                  >
                    <ListFilter className="size-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">{t("common.search")}</TooltipContent>
              </Tooltip>
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
              {conversations.length === 0 && (
                <div className="px-2 py-1.5 text-xs text-muted-foreground">—</div>
              )}
              {conversations.map((c) => (
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
              <AccountMenu />
            </div>
            <NotificationsPopover />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
