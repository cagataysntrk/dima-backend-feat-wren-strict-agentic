"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import {
  BarChart3,
  Boxes,
  Database,
  LayoutDashboard,
  LayoutGrid,
  MessageSquare,
  Plus,
  Share2,
  Table2,
  Upload,
} from "lucide-react";
import { gateway } from "@/lib/gateway";
import { useConversations } from "@/stores/conversations";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@dima/ui/primitives/command";

/** The top bar's button opens the palette without prop-drilling through the shell. */
export const OPEN_PALETTE = "dima:open-palette";

/** ⌘K anywhere (the browser's own find-in-page is left alone: that is ⌘F). */
function useHotkey(open: boolean, setOpen: (v: boolean) => void) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(!open);
      }
    };
    const onOpen = () => setOpen(true);
    window.addEventListener("keydown", onKey);
    window.addEventListener(OPEN_PALETTE, onOpen);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener(OPEN_PALETTE, onOpen);
    };
  }, [open, setOpen]);
}

/**
 * ⌘K palette over the company's analyses, dashboards and this browser's chats,
 * plus the pages themselves. Search hits the same /api/search the library uses.
 */
export function CommandPalette({ orgId, canAnalyze }: { orgId: string; canAnalyze: boolean }) {
  const router = useRouter();
  const t = useTranslations("nav");
  const tp = useTranslations("palette");
  const [open, setOpen] = useState(false);
  const [term, setTerm] = useState("");
  useHotkey(open, setOpen);

  const conversations = useConversations((s) => s.conversations);
  const chats = conversations
    .filter((c) => c.orgId === orgId && c.entries.length > 0)
    .sort((a, b) => b.updatedAt - a.updatedAt)
    .slice(0, 8);

  // Only search once there is something to search for; the empty term would
  // return the whole library on every open.
  const results = useQuery({
    queryKey: ["search", term],
    queryFn: () => gateway.search(term),
    enabled: open && term.trim().length > 1,
    staleTime: 30_000,
  });

  const go = (href: string) => {
    setOpen(false);
    setTerm("");
    router.push(href);
  };

  const pages = [
    { href: "/app", label: t("overview"), icon: LayoutGrid, show: true },
    { href: "/app/chat", label: t("newChat"), icon: Plus, show: true },
    { href: "/app/data", label: t("data"), icon: Table2, show: true },
    { href: "/app/sql", label: t("sql"), icon: Database, show: canAnalyze },
    { href: "/app/model", label: t("model"), icon: Boxes, show: canAnalyze },
    { href: "/app/schema", label: t("schema"), icon: Share2, show: true },
    { href: "/app/upload", label: t("upload"), icon: Upload, show: canAnalyze },
    { href: "/app/settings", label: t("settings"), icon: LayoutGrid, show: true },
  ].filter((p) => p.show);

  return (
    <CommandDialog
      open={open}
      onOpenChange={setOpen}
      title={tp("title")}
      description={tp("description")}
      // cmdk's own filter would hide server results that matched on the
      // description; the query already decided what matches.
      commandProps={{ shouldFilter: false }}
    >
      <CommandInput placeholder={tp("placeholder")} value={term} onValueChange={setTerm} />
      <CommandList>
        <CommandEmpty>{results.isFetching ? tp("searching") : tp("empty")}</CommandEmpty>

        {results.data && results.data.length > 0 && (
          <CommandGroup heading={tp("library")}>
            {results.data.map((i) => (
              <CommandItem
                key={`${i.kind}-${i.id}`}
                value={`${i.kind}-${i.id}`}
                onSelect={() => go(i.kind === "dashboard" ? `/app/dashboards/${i.id}` : `/app/cards/${i.id}`)}
              >
                {i.kind === "dashboard" ? <LayoutDashboard /> : <BarChart3 />}
                <span className="truncate">{i.name}</span>
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        {chats.length > 0 && (
          <CommandGroup heading={t("chats")}>
            {chats
              .filter((c) => !term.trim() || c.title.toLocaleLowerCase("tr").includes(term.toLocaleLowerCase("tr")))
              .map((c) => (
                <CommandItem key={c.id} value={`chat-${c.id}`} onSelect={() => go(`/app/chat?c=${c.id}`)}>
                  <MessageSquare />
                  <span className="truncate">{c.title || t("newChat")}</span>
                </CommandItem>
              ))}
          </CommandGroup>
        )}

        <CommandGroup heading={tp("pages")}>
          {pages
            .filter((p) => !term.trim() || p.label.toLocaleLowerCase("tr").includes(term.toLocaleLowerCase("tr")))
            .map(({ href, label, icon: Icon }) => (
              <CommandItem key={href} value={href} onSelect={() => go(href)}>
                <Icon />
                {label}
              </CommandItem>
            ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
