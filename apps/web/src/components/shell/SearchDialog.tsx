"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { Database, HelpCircle, MessageSquarePlus, MessagesSquare } from "lucide-react";
import { useConversations } from "@/stores/conversations";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@dima/ui/primitives/command";

/**
 * ⌘K komut paleti — sohbetlerde ara + hızlı aksiyonlar. Ortada açılır (Dialog),
 * arkasını karartır. Kısayolu burada bağlıyoruz ki tek yerden yönetilsin.
 */
export function SearchDialog({
  open,
  onOpenChange,
  onNewChat,
  onSelectConversation,
  onOpenSchema,
  onOpenHelp,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onOpenSchema: () => void;
  onOpenHelp: () => void;
}) {
  const t = useTranslations();
  const conversations = useConversations((s) => s.conversations);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onOpenChange(!open);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onOpenChange]);

  const run = (fn: () => void) => {
    onOpenChange(false);
    fn();
  };

  return (
    <CommandDialog
      open={open}
      onOpenChange={onOpenChange}
      title={t("common.search")}
      description={t("common.searchHint")}
    >
      <CommandInput placeholder={t("common.searchHint")} />
      <CommandList>
        <CommandEmpty>{t("common.noResults")}</CommandEmpty>

        <CommandGroup heading={t("common.actions")}>
          <CommandItem onSelect={() => run(onNewChat)}>
            <MessageSquarePlus className="size-4" />
            {t("common.newChat")}
          </CommandItem>
          <CommandItem onSelect={() => run(onOpenSchema)}>
            <Database className="size-4" />
            {t("chat.dataSources")}
          </CommandItem>
          <CommandItem onSelect={() => run(onOpenHelp)}>
            <HelpCircle className="size-4" />
            {t("common.help")}
          </CommandItem>
        </CommandGroup>

        {conversations.length > 0 && (
          <>
            <CommandSeparator />
            <CommandGroup heading={t("chat.conversations")}>
              {conversations.map((c) => (
                <CommandItem
                  key={c.id}
                  value={`${c.title} ${c.id}`}
                  onSelect={() => run(() => onSelectConversation(c.id))}
                >
                  <MessagesSquare className="size-4" />
                  <span className="truncate">{c.title || t("common.newChat")}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  );
}
