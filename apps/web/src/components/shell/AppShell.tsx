"use client";

import { useTranslations } from "next-intl";
import { AnimatePresence, motion } from "motion/react";
import { MessageSquarePlus, PanelLeft, PanelRight, Search } from "lucide-react";
import {
  SidebarInset,
  SidebarProvider,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Kbd } from "@/components/ui/kbd";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { railItem, railReveal } from "@/lib/motion";
import { cn } from "@/lib/utils";
import { AppSidebar } from "./AppSidebar";
import type { PanelTab } from "./ArtifactPanel";
import { ChatNav } from "./ChatNav";
import { ChatTitle } from "./ChatTitle";
import { IncognitoToggle } from "./IncognitoToggle";
import { ShareDialog } from "./ShareDialog";
import { ArtifactPanel } from "./ArtifactPanel";

/**
 * İki raylı kabuk (Claude/ChatGPT deseni): solda gezinme · ortada sohbet ·
 * sağda sohbet paneli. Grafikler sohbetin içinde çizilir.
 *
 * KAPSAM AYRIMI: sol kenar çubuğu HESAP geneline açılır (tüm veri kaynakları,
 * tüm paneller, tüm belgeler — hepsi tam sayfa). Sağ panel yalnız AÇIK SOHBET
 * hakkındadır (kaynaklar · belgeler). Aynı şeyin iki kapsamı iki yerde durur,
 * karışmaz.
 */
export function AppShell({
  onNewChat,
  onSelectConversation,
  onOpenHelp,
  onOpenSearch,
  onOpenShortcuts,
  onToggleArtifact,
  started,
  artifactOpen,
  artifactTab,
  onArtifactTabChange,
  onArtifactClose,
  artifact,
  children,
}: {
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onOpenHelp: () => void;
  onOpenSearch: () => void;
  onOpenShortcuts: () => void;
  onToggleArtifact: () => void;
  /** Sohbet başladı mı (üst bardaki Gizli↔Paylaş takası için). */
  started: boolean;
  artifactOpen: boolean;
  artifactTab: PanelTab;
  onArtifactTabChange: (tab: PanelTab) => void;
  onArtifactClose: () => void;
  artifact: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider className="h-svh min-h-0 overflow-hidden">
      <AppSidebar
        onNewChat={onNewChat}
        onSelectConversation={onSelectConversation}
        onOpenHelp={onOpenHelp}
        onOpenSearch={onOpenSearch}
        onOpenShortcuts={onOpenShortcuts}
      />
      <SidebarInset className="flex min-h-0 flex-row overflow-hidden">
        {/* relative: üst bar ve komut satırı içeriğin ÜSTÜNDE yüzer */}
        <div className="relative flex min-w-0 flex-1 flex-col">
          <TopBar
            started={started}
            onNewChat={onNewChat}
            onSelectConversation={onSelectConversation}
            onOpenSearch={onOpenSearch}
            onToggleArtifact={onToggleArtifact}
            artifactOpen={artifactOpen}
          />
          {/* overflow-hidden bir kap kaydırma ÇUBUĞU göstermez ama programatik
              olarak kaydırılabilir: tarayıcı odaklanan textarea'yı görünür tutmak
              için burayı kaydırıp bırakıyordu ("input aşağı kaydı, düzelmiyor").
              Kaydırmayı anında geri alıyoruz — bu kap asla kaymamalı. */}
          <div
            className="min-h-0 flex-1 overflow-hidden"
            onScroll={(e) => {
              const el = e.currentTarget;
              if (el.scrollTop !== 0) el.scrollTop = 0;
              if (el.scrollLeft !== 0) el.scrollLeft = 0;
            }}
          >
            {children}
          </div>
        </div>
        <ArtifactPanel
          open={artifactOpen}
          tab={artifactTab}
          onTabChange={onArtifactTabChange}
          onClose={onArtifactClose}
        >
          {artifact}
        </ArtifactPanel>
      </SidebarInset>
    </SidebarProvider>
  );
}

/**
 * Minimal top bar (ChatGPT): borderless, just the sidebar toggle. When the nav
 * is collapsed the two highest-frequency actions (yeni sohbet, arama) surface
 * here so nothing is more than one click away without the rail.
 */
function TopBar({
  started,
  onNewChat,
  onSelectConversation,
  onOpenSearch,
  onToggleArtifact,
  artifactOpen,
}: {
  /** Sohbet başladı mı — başlamadan Gizli, başlayınca Paylaş gösterilir. */
  started: boolean;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onOpenSearch: () => void;
  onToggleArtifact: () => void;
  artifactOpen: boolean;
}) {
  const t = useTranslations();
  const { open, toggleSidebar } = useSidebar();

  return (
    // Overlay ve ZEMİNSİZ: okunurluğu bar değil, ChatPanel'deki erime maskesi
    // sağlıyor. Opak/blur bir bant koyarsak maskenin yumuşaklığı kaybolur ve
    // ortaya sert bir kenar çıkar.
    <div className="pointer-events-none absolute inset-x-0 top-0 z-20 flex h-12 items-center gap-0.5 px-2 [&>*]:pointer-events-auto">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t("common.toggleSidebar")}
            onClick={toggleSidebar}
            className="text-muted-foreground hover:text-foreground"
          >
            <PanelLeft className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="flex items-center gap-1.5">
          {t("common.toggleSidebar")}
          <Kbd className="bg-background/20 text-background dark:bg-background/15">⌘B</Kbd>
        </TooltipContent>
      </Tooltip>

      {/* sohbet gezinme okları — kenar çubuğu düğmesinin SAĞINDA; sidebar açık
          da kapalı da olsa aynı yerde durur (konum değişseydi kas hafızası bozulurdu) */}
      <ChatNav onSelect={onSelectConversation} />

      {/* Sidebar AÇIKKEN başlık kenar çubuğu düğmesinin hemen sağında. */}
      {open && <ChatTitle className="min-w-0" />}

      <AnimatePresence>
        {!open && (
          <motion.div
            key="rail-actions"
            variants={railReveal}
            initial="hidden"
            animate="show"
            exit="hidden"
            className="flex items-center gap-0.5"
          >
            <motion.span variants={railItem} className="inline-flex">
              <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={t("common.newChat")}
                onClick={onNewChat}
                className="text-muted-foreground hover:text-foreground"
              >
                <MessageSquarePlus className="size-4" />
              </Button>
            </TooltipTrigger>
                <TooltipContent side="bottom">{t("common.newChat")}</TooltipContent>
              </Tooltip>
            </motion.span>
            <motion.span variants={railItem} className="inline-flex">
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
            </motion.span>
            {/* Sidebar KAPALIYKEN başlık ikonların ARASINDA değil, sol kümenin
                EN SAĞINDA — böylece sohbet sütununun soluna hizalı okunur. */}
            <motion.span variants={railItem} className="inline-flex min-w-0">
              <ChatTitle className="min-w-0" />
            </motion.span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* sağ küme: paylaş + artifacts */}
      <div className="ml-auto flex items-center gap-0.5">
        {started ? <ShareDialog /> : <IncognitoToggle />}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={t("common.artifacts")}
              aria-pressed={artifactOpen}
              onClick={onToggleArtifact}
              className={cn(
                "text-muted-foreground hover:text-foreground",
                artifactOpen && "bg-accent text-foreground",
              )}
            >
              <PanelRight className="size-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">{t("common.artifacts")}</TooltipContent>
        </Tooltip>
      </div>
    </div>
  );
}
