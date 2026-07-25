"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Check, Globe, Link2, Share } from "lucide-react";
import { selectActive, useConversations } from "@/stores/conversations";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

/**
 * Sohbeti paylaş — ChatGPT'deki "Share public link to chat" karşılığı.
 *
 * NOT: Backend'de HENÜZ bir paylaşım ucu yok (sözleşme: /ask /cube /verify /query
 * /schedules /notifications /contracts). Bu yüzden "bağlantı oluştur" gerçek bir
 * genel link ÜRETMEZ; uç eklenene kadar buton devre dışı ve bunu açıkça söylüyoruz.
 * Sahte bir URL göstermek, paylaşıldığını sanmaya yol açardı.
 */
export function ShareDialog() {
  const t = useTranslations();
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const conv = useConversations(selectActive);

  const title = conv?.title || t("common.newChat");
  const hasChat = (conv?.items.length ?? 0) > 0;

  const copyTitle = () => {
    void navigator.clipboard?.writeText(title).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Tooltip>
        <TooltipTrigger asChild>
          <DialogTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              disabled={!hasChat}
              className="h-8 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground"
            >
              <Share className="size-4" />
              {t("common.share")}
            </Button>
          </DialogTrigger>
        </TooltipTrigger>
        <TooltipContent side="bottom">{t("share.tooltip")}</TooltipContent>
      </Tooltip>

      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("share.title")}</DialogTitle>
          <DialogDescription>{t("share.subtitle")}</DialogDescription>
        </DialogHeader>

        <div className="flex items-center gap-3 rounded-xl border border-border bg-muted/40 p-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-background text-muted-foreground">
            <Globe className="size-4" />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-medium text-foreground">{title}</span>
            <span className="block text-xs text-muted-foreground">{t("share.scope")}</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative min-w-0 flex-1">
            <Link2 className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              readOnly
              value=""
              placeholder={t("share.placeholder")}
              className="pl-9 text-sm"
              aria-label={t("share.title")}
            />
          </div>
          <Button variant="brand" disabled className="gap-1.5">
            {copied ? <Check className="size-4" /> : <Link2 className="size-4" />}
            {t("share.create")}
          </Button>
        </div>

        <p className="text-xs leading-relaxed text-muted-foreground">{t("share.pending")}</p>

        <div className="flex justify-end">
          <Button variant="ghost" size="sm" onClick={copyTitle}>
            {copied ? t("share.copied") : t("share.copyTitle")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
