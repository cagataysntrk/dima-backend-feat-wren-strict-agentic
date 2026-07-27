"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Mic, Paperclip, Plus, Square } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Attachment } from "@/components/ai/attachment";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Kbd, KbdGroup } from "@/components/ui/kbd";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useSpeech } from "@/hooks/use-speech";
import { cn } from "@/lib/utils";

/**
 * Chat composer, Claude-style: an elevated rounded card with the textarea on top
 * and a toolbar below (attachment "+" menu on the left, send on the right).
 * Attachments are collected client-side (chips with remove); the backend `/ask`
 * is text-only for now, so they're cleared on send.
 */
export const MAX_FILES = 20;

export function Composer({
  value,
  onChange,
  onSubmit,
  busy,
  autoFocus,
  placeholder,
  size = "inline",
}: {
  value: string;
  onChange: (v: string) => void;
  /** Ekler gönderimle birlikte taşınır — mesajın altında görünürler. */
  onSubmit: (files: File[]) => void;
  busy?: boolean;
  autoFocus?: boolean;
  placeholder?: string;
  size?: "hero" | "inline";
}) {
  const t = useTranslations("chat");
  const locale = useLocale();
  const ref = useRef<HTMLTextAreaElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);

  // dikte: tanınan metni imlecin sonuna ekle
  const {
    listening,
    supported: voiceSupported,
    toggle: toggleVoice,
  } = useSpeech(locale, (text) => onChange(value ? `${value} ${text}` : text));

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, size === "hero" ? 240 : 180)}px`;
  }, [value, size, files.length]);

  const canSend = (value.trim().length > 0 || files.length > 0) && !busy;

  function send() {
    if (!canSend) return;
    onSubmit(files);
    setFiles([]);
  }

  function addFiles(list: FileList | null) {
    if (!list?.length) return;
    setFiles((prev) => [...prev, ...Array.from(list)].slice(0, MAX_FILES));
  }

  return (
    // shadow-lg: içerik altından aktığı için komut satırı yüzeyden KALKMALI
    <div className="rounded-2xl border border-input bg-card shadow-lg transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/25">
      {/* Ekler — sarmak yerine YATAY kaydırır: 20 dosyada sarma komut satırını
          ekranın yarısına çıkarıyordu. Şerit sabit yükseklikte kalır. */}
      {files.length > 0 && (
        <div className="flex items-center gap-2 px-3 pt-3">
          <div className="flex min-w-0 flex-1 items-center gap-2 overflow-x-auto pb-1">
            {files.map((f, i) => (
              <Attachment
                key={`${f.name}-${f.lastModified}-${i}`}
                file={f}
                className="shrink-0"
                onRemove={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
              />
            ))}
          </div>
          <span className="shrink-0 text-xs text-muted-foreground tabular-nums">
            {files.length}/{MAX_FILES}
          </span>
        </div>
      )}

      <textarea
        ref={ref}
        value={value}
        autoFocus={autoFocus}
        rows={1}
        placeholder={placeholder ?? t("placeholder")}
        // Grammarly vb. eklentiler textarea'ya overlay (<grammarly-extension>) enjekte edip
        // hydration mismatch üretiyor; veri sorusu yazılan alanda dilbilgisi denetimi zaten istenmiyor.
        data-gramm="false"
        data-gramm_editor="false"
        data-enable-grammarly="false"
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            send();
          }
        }}
        className={cn(
          "block w-full resize-none bg-transparent px-4 pt-3.5 leading-relaxed text-foreground outline-none placeholder:text-muted-foreground",
          size === "hero" ? "text-base" : "text-sm",
        )}
      />

      {/* toolbar */}
      <div className="flex items-center justify-between gap-2 px-2.5 pt-1 pb-2.5">
        <DropdownMenu>
          <Tooltip>
            <TooltipTrigger asChild>
              <DropdownMenuTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  aria-label={t("attach")}
                  className="size-8 rounded-full text-muted-foreground hover:text-foreground"
                >
                  <Plus className="size-4" strokeWidth={1.75} />
                </Button>
              </DropdownMenuTrigger>
            </TooltipTrigger>
            <TooltipContent side="top">{t("addFiles")}</TooltipContent>
          </Tooltip>
          {/* w-auto + nowrap: sabit genişlik etiketi iki satıra kırıp menüyü
              devleştiriyordu; artık içeriğine göre daralıyor. */}
          <DropdownMenuContent align="start" side="top" className="w-auto min-w-0">
            <DropdownMenuItem
              disabled={files.length >= MAX_FILES}
              onSelect={() => fileRef.current?.click()}
              className="gap-2 text-xs whitespace-nowrap"
            >
              <Paperclip className="size-3.5" />
              {t("addFiles")}
              <DropdownMenuShortcut className="ml-3">
                <KbdGroup>
                  <Kbd>⌘</Kbd>
                  <Kbd>U</Kbd>
                </KbdGroup>
              </DropdownMenuShortcut>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <input
          ref={fileRef}
          type="file"
          multiple
          hidden
          onChange={(e) => {
            addFiles(e.target.files);
            e.target.value = "";
          }}
        />

        <div className="flex min-w-0 items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                aria-label={listening ? t("voiceStop") : t("voice")}
                onClick={toggleVoice}
                disabled={!voiceSupported}
                className={cn(
                  "size-8 rounded-full text-muted-foreground hover:text-foreground",
                  listening && "text-brand",
                )}
              >
                {listening ? (
                  <Square className="size-3.5 fill-current" />
                ) : (
                  <Mic className="size-4" strokeWidth={1.75} />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top">
              {voiceSupported ? (listening ? t("voiceStop") : t("voice")) : t("voiceUnsupported")}
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                type="button"
                variant="brand"
                size="icon"
                disabled={!canSend}
                aria-label={t("send")}
                onClick={send}
                className="rounded-full"
              >
                <ArrowUp className="size-4.5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top" className="flex items-center gap-1.5">
              {t("send")}
              <Kbd className="bg-background/20 text-background dark:bg-background/15">⏎</Kbd>
            </TooltipContent>
          </Tooltip>
        </div>
      </div>
    </div>
  );
}
