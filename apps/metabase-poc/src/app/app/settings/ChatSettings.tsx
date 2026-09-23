"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useFormatter, useTranslations } from "next-intl";
import { toast } from "sonner";
import { gateway, type ChatPrefs } from "@/lib/gateway";
import { Label } from "@dima/ui/primitives/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@dima/ui/primitives/select";

const ROW_LIMITS = [500, 1_000, 2_000];

export function ChatSettings({ initial, canEdit }: { initial: ChatPrefs; canEdit: boolean }) {
  const t = useTranslations("settings.chat");
  const format = useFormatter();
  const [prefs, setPrefs] = useState(initial);
  const save = useMutation({
    mutationFn: (patch: Partial<ChatPrefs>) => gateway.setChatPrefs(patch),
    onSuccess: (next) => {
      setPrefs(next);
      toast.success(t("saved"));
    },
    onError: (e: Error) => {
      setPrefs(initial);
      toast.error(e.message);
    },
  });

  return (
    <div className="space-y-4">
      <div className="max-w-sm space-y-1.5">
        <Label htmlFor="chat-rows" className="text-xs">
          {t("maxRows")}
        </Label>
        <Select
          value={String(prefs.maxRows)}
          disabled={!canEdit || save.isPending}
          onValueChange={(v) => {
            const maxRows = Number(v);
            setPrefs((p) => ({ ...p, maxRows }));
            save.mutate({ maxRows });
          }}
        >
          <SelectTrigger id="chat-rows" size="sm" className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ROW_LIMITS.map((n) => (
              <SelectItem key={n} value={String(n)}>
                {format.number(n)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-xs text-muted-foreground">{t("maxRowsHint")}</p>
      </div>
      <p className="text-xs text-muted-foreground">{t("engineOwnsModel")}</p>
      {!canEdit && <p className="text-xs text-muted-foreground">{t("adminsOnly")}</p>}
    </div>
  );
}
