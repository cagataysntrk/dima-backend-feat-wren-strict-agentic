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
import { ShareDialog } from "./ShareDialog";
import { ArtifactPanel } from "./ArtifactPanel";

/**
 * Two-rail Claude/ChatGPT-style shell: collapsible left nav · center chat ·
 * collapsible right artifact panel. Charts render inline in the center; heavy
 * objects (schema, help, later dashboards) open in the artifact panel.
 */
export function AppShell({
  onNewChat,
  onSelectConversation,
  onOpenSchema,
  onOpenHelp,
  onOpenSearch,
  onToggleArtifact,
  artifactOpen,
  artifactTitle,
  onArtifactClose,
  artifact,
  children,
}: {
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onOpenSchema: () => void;
  onOpenHelp: () => void;
  onOpenSearch: () => void;
  onToggleArtifact: () => void;
  artifactOpen: boolean;
  artifactTitle: string;
  onArtifactClose: () => void;
  artifact: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider>
      <AppSidebar
        onNewChat={onNewChat}
        onSelectConversation={onSelectConversation}
        onOpenSchema={onOpenSchema}
        onOpenHelp={onOpenHelp}
        onOpenSearch={onOpenSearch}
      />
      <SidebarInset className="flex min-h-0 flex-row overflow-clip">
        {/* relative: üst bar ve komut satırı içeriğin ÜSTÜNDE yüzer */}
        <div className="relative flex min-w-0 flex-1 flex-col">
          <TopBar
            onNewChat={onNewChat}
            onOpenSearch={onOpenSearch}
            onToggleArtifact={onToggleArtifact}
            artifactOpen={artifactOpen}
          />
          {/* overflow-clip (hidden DEĞİL): hidden bir kap, odak görünür alana
              alınırken tarayıcı tarafından kaydırılabilir ve geri dönmez —
              ek gönderdikten sonra komut satırının kayıp kalmasının sebebi buydu. */}
          <div className="min-h-0 flex-1 overflow-clip">{children}</div>
        </div>
        <ArtifactPanel open={artifactOpen} title={artifactTitle} onClose={onArtifactClose}>
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
  onNewChat,
  onOpenSearch,
  onToggleArtifact,
  artifactOpen,
}: {
  onNewChat: () => void;
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
          </motion.div>
        )}
      </AnimatePresence>

      {/* sağ küme: paylaş + artifacts */}
      <div className="ml-auto flex items-center gap-0.5">
        <ShareDialog />
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
