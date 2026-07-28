"use client";

import { useState } from "react";
import { Bell, Check, X } from "lucide-react";
import type { AskResponse } from "@dima/contracts";
import { createSchedule, verifyReport } from "@dima/api-client";
import { useFeature, usePermission } from "@/lib/access";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { CopyIcon } from "@/components/ai/copy-icon";
import { cn } from "@/lib/utils";

const SCHEDULE_PRESETS = [
  { name: "her sabah 08:00 · dünün verisi", every: "day" as const, at: "08:00", period: "dün" },
  { name: "her saat · bugünün verisi", every: "hour" as const, period: "bugün" },
  {
    name: "her pazartesi 08:00 · geçen hafta",
    every: "week" as const,
    at: "08:00",
    weekday: 1,
    period: "geçen hafta",
  },
];

/**
 * Cevabın ALTINDAKİ aksiyon şeridi (ChatGPT/Claude tarzı): doğru · yanlış ·
 * zamanla · kopyala. Görünürlük backend'den gelir — özellik bayrağı (`useFeature`)
 * ⊕ izin (`usePermission`); rol matrisi UI'a kopyalanmaz. Eskiden sağ paneldeydi.
 */
export function MessageActions({
  data,
  verifyLabel,
  sessionId,
  className,
}: {
  data: AskResponse;
  verifyLabel?: string | null;
  sessionId?: string;
  className?: string;
}) {
  const [scheduled, setScheduled] = useState(false);
  const [fb, setFb] = useState<"ok" | "bad" | null>(null);
  const [copied, setCopied] = useState(false);

  const schedStage = useFeature("scheduled_reports");
  const verifyStage = useFeature("verify_button");
  const canSchedule = usePermission("schedule:create");
  const canVerify = usePermission("vqr:write");

  // Raporu üreten son GERÇEK soru (chip etiketi değil) — verify bu metinle öğrenir.
  const vLabel = data.question.startsWith("chip:") ? (verifyLabel ?? data.question) : data.question;
  const verified = fb === "ok";
  const flagged = fb === "bad";

  const showSchedule = schedStage && canSchedule && data.cube_query && data.source;
  const showVerify = verifyStage && canVerify && data.cube_query && data.source;

  const schedule = (preset: (typeof SCHEDULE_PRESETS)[number]) => {
    if (!data.cube_query) return;
    const cq = {
      ...data.cube_query,
      filters: ((data.cube_query.filters as { dimension: string }[] | undefined) ?? []).filter(
        (f) => f.dimension !== "tarih",
      ),
    };
    if (!(cq.filters as unknown[]).length) delete (cq as Record<string, unknown>).filters;
    createSchedule({
      label: vLabel,
      cube_query: cq,
      period: preset.period,
      every: preset.every,
      at: preset.at,
      weekday: preset.weekday,
    })
      .then(() => setScheduled(true))
      .catch(() => {});
  };

  const doVerify = () => {
    if (!data.cube_query) return;
    verifyReport(data.cube_query, vLabel, { undo: verified || undefined, session_id: sessionId })
      .then(() => setFb(verified ? null : "ok"))
      .catch(() => {});
  };

  const doFlag = () => {
    if (!data.cube_query || flagged) return;
    verifyReport(data.cube_query, vLabel, { verdict: "wrong", session_id: sessionId })
      .then(() => setFb("bad"))
      .catch(() => {});
  };

  const copy = () => {
    const text = data.sql ?? data.note ?? data.question;
    void navigator.clipboard?.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  if (!showSchedule && !showVerify && !data.sql) return null;

  return (
    <div className={cn("flex flex-wrap items-center gap-0.5 pt-0.5", className)}>
      {showVerify && (
        <>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={doVerify}
                aria-label="doğru"
                className={cn(
                  "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                  verified && "text-emerald-600 dark:text-emerald-400",
                )}
              >
                <Check className="size-3.5" />
                {verified ? "öğrenildi" : "doğru"}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              {verified
                ? "Doğrulamayı geri al"
                : "Doğru olarak işaretle — aynı soru bundan sonra LLM'siz cevaplanır"}
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={doFlag}
                aria-label="yanlış"
                className={cn(
                  "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                  flagged && "text-destructive",
                )}
              >
                <X className="size-3.5" />
                {flagged ? "kaydedildi" : "yanlış"}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              Yanlış — kayda geçer; öğrenilmiş yakın çift varsa silinir
            </TooltipContent>
          </Tooltip>
        </>
      )}

      {showSchedule && (
        <DropdownMenu>
          <Tooltip>
            <TooltipTrigger asChild>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  aria-label="zamanla"
                  className={cn(
                    "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                    scheduled && "text-brand",
                  )}
                >
                  <Bell className="size-3.5" />
                  {scheduled ? "zamanlandı" : "zamanla"}
                </Button>
              </DropdownMenuTrigger>
            </TooltipTrigger>
            <TooltipContent side="bottom">Bu raporu düzenli olarak çalıştır</TooltipContent>
          </Tooltip>
          <DropdownMenuContent align="start">
            {SCHEDULE_PRESETS.map((pr) => (
              <DropdownMenuItem key={pr.name} onClick={() => schedule(pr)}>
                {pr.name}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      {data.sql && (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              onClick={copy}
              aria-label="SQL'i kopyala"
              className="h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground"
            >
              <CopyIcon copied={copied} />
              {copied ? "kopyalandı" : "kopyala"}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">SQL&apos;i panoya kopyala</TooltipContent>
        </Tooltip>
      )}
    </div>
  );
}
