"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { PanelLeft } from "lucide-react";
import { SidebarInset, SidebarProvider, useSidebar } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Kbd } from "@/components/ui/kbd";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useConversations } from "@/stores/conversations";
import { AppSidebar } from "./AppSidebar";
import { ChatNav } from "./ChatNav";
import { SearchDialog } from "./SearchDialog";
import { ShortcutsDialog } from "./ShortcutsDialog";

/**
 * Hesap kapsamlı sayfaların kabuğu (Veri kaynakları · Paneller · Belgeler ·
 * Sohbetler · Bildirimler · Ayarlar): SOL sidebar durur, sağ panel DURMAZ —
 * bu sayfaların açık bir sohbeti yok, sağ panel de yalnız sohbet hakkındadır.
 */
export function SecondaryShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const newConversation = useConversations((s) => s.newConversation);
  const select = useConversations((s) => s.select);
  const [searchOpen, setSearchOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);

  const goPanel = (panel: string) => router.push(`/app?panel=${panel}`);

  return (
    <>
      <SearchDialog
        open={searchOpen}
        onOpenChange={setSearchOpen}
        onNewChat={() => {
          newConversation();
          router.push("/app");
        }}
        onSelectConversation={(id) => {
          select(id);
          router.push("/app");
        }}
        onOpenSchema={() => router.push("/data-sources")}
        onOpenHelp={() => goPanel("help")}
      />
      <ShortcutsDialog open={shortcutsOpen} onOpenChange={setShortcutsOpen} />

      <SidebarProvider className="h-svh min-h-0 overflow-hidden">
        <AppSidebar
          onNewChat={() => {
            newConversation();
            router.push("/app");
          }}
          onSelectConversation={(id) => {
            select(id);
            router.push("/app");
          }}
          onOpenHelp={() => goPanel("help")}
          onOpenSearch={() => setSearchOpen(true)}
          onOpenShortcuts={() => setShortcutsOpen(true)}
        />
        <SidebarInset className="flex min-h-0 flex-col overflow-hidden">
          <SecondaryTopBar
            onSelectConversation={(id) => {
              select(id);
              router.push("/app");
            }}
          />
          <div className="min-h-0 flex-1 overflow-auto">{children}</div>
        </SidebarInset>
      </SidebarProvider>
    </>
  );
}

function SecondaryTopBar({
  onSelectConversation,
}: {
  onSelectConversation: (id: string) => void;
}) {
  const t = useTranslations();
  const { toggleSidebar } = useSidebar();
  return (
    <div className="flex h-12 shrink-0 items-center px-2">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t("common.toggleSidebar")}
            onClick={toggleSidebar}
            className="text-muted-foreground transition-transform hover:scale-105 hover:text-foreground"
          >
            <PanelLeft className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="flex items-center gap-1.5">
          {t("common.toggleSidebar")}
          <Kbd className="bg-background/20 text-background dark:bg-background/15">⌘B</Kbd>
        </TooltipContent>
      </Tooltip>
      <ChatNav onSelect={onSelectConversation} />
    </div>
  );
}
