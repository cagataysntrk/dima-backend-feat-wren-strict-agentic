"use client";

import { Suspense, createContext, useContext, useState } from "react";
import { createPortal } from "react-dom";
import { usePathname } from "next/navigation";
import { PanelLeft, Search } from "lucide-react";
import { SidebarInset, SidebarProvider, useSidebar } from "@dima/ui/primitives/sidebar";
import { useTranslations } from "next-intl";
import { CommandPalette, OPEN_PALETTE } from "./CommandPalette";
import { ShortcutsDialog } from "./ShortcutsDialog";
import { Button } from "@dima/ui/primitives/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@dima/ui/primitives/tooltip";
import { AppSidebar, type ShellOrg, type ShellUser } from "./AppSidebar";

// Two-rail shell, same pattern as apps/web: left = account-wide navigation +
// chats, centre = page, right = a panel about the open chat (rendered by the
// chat page). Pages can put controls in the top bar via <TopbarActions>.

const TopbarSlot = createContext<HTMLElement | null>(null);
const TopbarLeftSlot = createContext<HTMLElement | null>(null);

/** Render children into the right side of the shell's top bar. */
export function TopbarActions({ children }: { children: React.ReactNode }) {
  const slot = useContext(TopbarSlot);
  return slot ? createPortal(children, slot) : null;
}

/** Render children next to the sidebar toggle (chat arrows, chat title). */
export function TopbarLead({ children }: { children: React.ReactNode }) {
  const slot = useContext(TopbarLeftSlot);
  return slot ? createPortal(children, slot) : null;
}

interface Props {
  user: ShellUser;
  orgs: ShellOrg[];
  activeOrgId: string | null;
  canAnalyze: boolean;
  children: React.ReactNode;
}

export function AppShell({ user, orgs, activeOrgId, canAnalyze, children }: Props) {
  const pathname = usePathname();
  const [slot, setSlot] = useState<HTMLElement | null>(null);
  const [leftSlot, setLeftSlot] = useState<HTMLElement | null>(null);
  // The chat owns its full-height layout (message column + right panel);
  // every other page gets the standard padded content column.
  const fullBleed = pathname.startsWith("/app/chat");

  return (
    <SidebarProvider className="h-svh min-h-0 overflow-hidden">
      {/* AppSidebar reads search params (active chat); Suspense keeps that client-only. */}
      <Suspense>
        <AppSidebar user={user} orgs={orgs} activeOrgId={activeOrgId} canAnalyze={canAnalyze} />
      </Suspense>
      {activeOrgId && <CommandPalette orgId={activeOrgId} canAnalyze={canAnalyze} />}
      <ShortcutsDialog />
      <SidebarInset className="flex min-h-0 flex-col overflow-hidden">
        <TopBar setSlot={setSlot} setLeftSlot={setLeftSlot} />
        <TopbarSlot.Provider value={slot}>
          <TopbarLeftSlot.Provider value={leftSlot}>
          <div className="min-h-0 flex-1 overflow-hidden">
            {fullBleed ? (
              children
            ) : (
              <div className="h-full overflow-y-auto">
                <div className="mx-auto max-w-7xl px-4 pt-2 pb-8 md:px-6">{children}</div>
              </div>
            )}
          </div>
          </TopbarLeftSlot.Provider>
        </TopbarSlot.Provider>
      </SidebarInset>
    </SidebarProvider>
  );
}

/** Discoverability: the palette is a keystroke, but not everyone guesses it. */
function PaletteButton() {
  const t = useTranslations("palette");
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          type="button"
          onClick={() => window.dispatchEvent(new Event(OPEN_PALETTE))}
          className="ml-1 inline-flex h-7 items-center gap-1.5 rounded-full border border-[var(--surface-edge)] px-2.5 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        >
          <Search className="size-3.5" aria-hidden />
          <span className="hidden sm:inline">{t("short")}</span>
        </button>
      </TooltipTrigger>
      <TooltipContent side="bottom">{t("title")}</TooltipContent>
    </Tooltip>
  );
}

function TopBar({
  setSlot,
  setLeftSlot,
}: {
  setSlot: (el: HTMLElement | null) => void;
  setLeftSlot: (el: HTMLElement | null) => void;
}) {
  const { toggleSidebar } = useSidebar();
  const t = useTranslations("nav");
  return (
    <div className="flex h-12 shrink-0 items-center gap-1 px-2">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t("toggleSidebar")}
            onClick={toggleSidebar}
            className="text-muted-foreground hover:text-foreground"
          >
            <PanelLeft className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">{t("toggleSidebar")}</TooltipContent>
      </Tooltip>
      <div ref={setLeftSlot} className="flex min-w-0 items-center gap-0.5" />
      <div ref={setSlot} className="ml-auto flex items-center gap-0.5" />
      <PaletteButton />
    </div>
  );
}
