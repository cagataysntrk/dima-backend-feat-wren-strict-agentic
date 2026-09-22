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

// Kept in step with server/prefs.ts — that file is the one that enforces them.
const MODELS = [
  { id: "openai/gpt-5.6-sol", label: "Sol", hint: "modelSolHint" },
  { id: "openai/gpt-5.6-luna", label: "Luna", hint: "modelLunaHint" },
] as const;
const ROW_LIMITS = [500, 1_000, 2_000];

export function ChatSettings({ initial, canEdit }: { initial: ChatPrefs; canEdit: boolean }) {
  const t = useTranslations("settings.chat");
  // Thousands separator follows the locale, not a hardcoded "tr-TR".
  const format = useFormatter();
  const [prefs, setPrefs] = useState(initial);
  const save = useMutation({
    mutationFn: (patch: Partial<ChatPrefs>) => gateway.setChatPrefs(patch),
    onSuccess: (next) => {
      setPrefs(next);
      toast.success(t("saved"));
    },
    onError: (e: Error, patch) => {
      // Put the control back where the server still says it is.
      setPrefs((p) => ({ ...p, ...Object.fromEntries(Object.keys(patch).map((k) => [k, initial[k as keyof ChatPrefs]])) }));
      toast.error(e.message);
    },
  });

  const model = MODELS.find((m) => m.id === prefs.model);

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="chat-model" className="text-xs">
            {t("model")}
          </Label>
          <Select
            value={prefs.model}
            disabled={!canEdit || save.isPending}
            onValueChange={(v) => {
              setPrefs((p) => ({ ...p, model: v }));
              save.mutate({ model: v });
            }}
          >
            <SelectTrigger id="chat-model" size="sm" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {MODELS.map((m) => (
                <SelectItem key={m.id} value={m.id}>
                  {m.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {model && <p className="text-xs text-muted-foreground">{t(model.hint)}</p>}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="chat-rows" className="text-xs">
            {t("maxRows")}
          </Label>
          <Select
            value={String(prefs.maxRows)}
            disabled={!canEdit || save.isPending}
            onValueChange={(v) => {
              setPrefs((p) => ({ ...p, maxRows: Number(v) }));
              save.mutate({ maxRows: Number(v) });
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
      </div>
      {!canEdit && (
        <p className="text-xs text-muted-foreground">{t("adminsOnly")}</p>
      )}
    </div>
  );
}
