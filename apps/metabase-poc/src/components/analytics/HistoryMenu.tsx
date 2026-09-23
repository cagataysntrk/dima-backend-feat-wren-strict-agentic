"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { History, Undo2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { gateway } from "@/lib/gateway";
import { Button } from "@dima/ui/primitives/button";
import { Popover, PopoverContent, PopoverTrigger } from "@dima/ui/primitives/popover";

const when = (iso: string) =>
  new Date(iso).toLocaleString("tr-TR", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });

/** Change history of one analysis, with restore for owner/admin. */
export function HistoryMenu({ cardId, canEdit }: { cardId: number; canEdit: boolean }) {
  const t = useTranslations("history");
  const tCommon = useTranslations("common");
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const history = useQuery({
    queryKey: ["history", cardId],
    queryFn: () => gateway.cardHistory(cardId),
    enabled: open,
  });
  const revert = useMutation({
    mutationFn: (revisionId: number) => gateway.revertCard(cardId, revisionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["card", cardId] });
      void queryClient.invalidateQueries({ queryKey: ["history", cardId] });
      toast.success(t("reverted"));
      setOpen(false);
    },
    onError: (e) => toast.error(e.message),
  });

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm">
          <History className="size-4" aria-hidden />
          {t("title")}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-80 p-0">
        <p className="border-b px-3 py-2 text-xs text-muted-foreground">
          {t("scope")}
        </p>
        <ul className="max-h-72 overflow-y-auto p-1">
          {history.isPending && <li className="px-2 py-1.5 text-sm text-muted-foreground">{tCommon("loading")}</li>}
          {history.isError && (
            <li role="alert" className="px-2 py-1.5 text-sm text-destructive">
              {history.error.message}
            </li>
          )}
          {history.data?.length === 0 && (
            <li className="px-2 py-1.5 text-sm text-muted-foreground">{t("empty")}</li>
          )}
          {history.data?.map((r) => (
            <li key={r.id} className="flex items-start gap-2 rounded-md px-2 py-1.5 hover:bg-accent/50">
              <div className="min-w-0 flex-1">
                <p className="text-sm">{r.what}</p>
                <p className="text-xs text-muted-foreground tabular-nums">
                  {when(r.at)}
                  {r.current && t("current")}
                </p>
              </div>
              {canEdit && !r.current && (
                <Button
                  variant="ghost"
                  size="xs"
                  onClick={() => revert.mutate(r.id)}
                  disabled={revert.isPending}
                  aria-label={t("revertTo")}
                >
                  <Undo2 className="size-3.5" aria-hidden />
                  {t("revert")}
                </Button>
              )}
            </li>
          ))}
        </ul>
      </PopoverContent>
    </Popover>
  );
}
