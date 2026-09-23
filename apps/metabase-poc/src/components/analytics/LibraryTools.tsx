"use client";

import { useDeferredValue, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BarChart3, Copy, LayoutDashboard, MoreHorizontal, Search, Trash2, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { gateway, type Item } from "@/lib/gateway";
import { Button } from "@dima/ui/primitives/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@dima/ui/primitives/dropdown-menu";

const href = (i: Item) => (i.kind === "dashboard" ? `/app/dashboards/${i.id}` : `/app/cards/${i.id}`);

/** Search across the company's analyses and dashboards; results replace the overview lists. */
export function LibrarySearch({ canEdit }: { canEdit: boolean }) {
  const t = useTranslations("library");
  const [q, setQ] = useState("");
  const term = useDeferredValue(q.trim());
  const results = useQuery({
    queryKey: ["search", term],
    queryFn: () => gateway.search(term),
    enabled: term.length >= 2,
    placeholderData: keepPreviousData,
  });

  return (
    <div className="space-y-4">
      <div className="surface flex items-center gap-2 px-3">
        <Search className="size-4 shrink-0 text-muted-foreground" aria-hidden />
        <label htmlFor="library-search" className="sr-only">
          Analiz ve pano ara
        </label>
        <input
          id="library-search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={t("searchPlaceholder")}
          className="h-11 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground md:text-sm"
        />
        {q && (
          <Button variant="ghost" size="icon-sm" aria-label={t("clearSearch")} onClick={() => setQ("")}>
            <X className="size-4" aria-hidden />
          </Button>
        )}
      </div>

      {term.length >= 2 && (
        <section aria-label={t("results")} className="space-y-2">
          {results.isPending && <p className="text-sm text-muted-foreground">{t("searching")}</p>}
          {results.isError && (
            <p role="alert" className="text-sm text-destructive">
              {results.error.message}
            </p>
          )}
          {results.data?.length === 0 && <p className="text-sm text-muted-foreground">{t("noResults", { term })}</p>}
          <ul className="space-y-2">
            {results.data?.map((i) => (
              <li key={`${i.kind}-${i.id}`} className="surface-sm surface-interactive flex items-center gap-3 px-3 py-2.5">
                <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-brand/10 text-brand">
                  {i.kind === "dashboard" ? (
                    <LayoutDashboard className="size-4" aria-hidden />
                  ) : (
                    <BarChart3 className="size-4" aria-hidden />
                  )}
                </span>
                <Link href={href(i)} className="min-w-0 flex-1 truncate font-medium hover:underline">
                  {i.name}
                </Link>
                {canEdit && i.kind !== "dashboard" && <ItemMenu item={i} />}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

/** Per-analysis actions: duplicate, move to trash. */
export function ItemMenu({ item }: { item: Item }) {
  const t = useTranslations("library");
  const queryClient = useQueryClient();
  const router = useRouter();
  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["search"] });
    void queryClient.invalidateQueries({ queryKey: ["trash"] });
    void queryClient.invalidateQueries({ queryKey: ["items"] });
    router.refresh();
  };
  const copy = useMutation({
    mutationFn: () => gateway.copyCard(item.id),
    onSuccess: ({ id, name }) => {
      invalidate();
      toast.success(t("created", { name }), {
        action: { label: t("open"), onClick: () => router.push(`/app/cards/${id}`) },
      });
    },
    onError: (e) => toast.error(e.message),
  });
  const archive = useMutation({
    mutationFn: () => gateway.archiveCard(item.id),
    onSuccess: () => {
      invalidate();
      toast.success(t("trashed"), {
        action: {
          label: t("undo"),
          onClick: () => gateway.restore("card", item.id).then(invalidate).catch(() => toast.error(t("undoFailed"))),
        },
      });
    },
    onError: (e) => toast.error(e.message),
  });

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label={t("actionsFor", { name: item.name })}>
          <MoreHorizontal className="size-4" aria-hidden />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onSelect={() => copy.mutate()} disabled={copy.isPending}>
          <Copy className="size-4" aria-hidden />
          {t("duplicate")}
        </DropdownMenuItem>
        <DropdownMenuItem
          onSelect={() => archive.mutate()}
          disabled={archive.isPending}
          className="text-destructive focus:text-destructive"
        >
          <Trash2 className="size-4" aria-hidden />
          {t("toTrash")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
