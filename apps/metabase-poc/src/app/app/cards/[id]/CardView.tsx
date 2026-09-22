"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Check, Pencil, Target } from "lucide-react";
import { toast } from "sonner";
import { gateway } from "@/lib/gateway";
import { ResultView } from "@/components/ResultView";
import { ExportMenu } from "@/components/analytics/ExportMenu";
import { AddToDashboard } from "@/components/analytics/DashboardActions";
import { DrillSheet, type DrillTarget } from "@/components/analytics/DrillSheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Skeleton } from "@/components/ui/skeleton";

export function CardView({ id, canEdit }: { id: number; canEdit: boolean }) {
  const queryClient = useQueryClient();
  const q = useQuery({ queryKey: ["card", id], queryFn: () => gateway.card(id) });
  const [drill, setDrill] = useState<DrillTarget | null>(null);
  // Chart type the reader is looking at; offered for saving when it differs.
  const [display, setDisplay] = useState<string | null>(null);
  const [renaming, setRenaming] = useState(false);
  const [name, setName] = useState("");

  const save = useMutation({
    mutationFn: (patch: { display?: string; goal?: number | null; name?: string }) => gateway.updateCard(id, patch),
    onSuccess: (_r, patch) => {
      setDisplay(null);
      setRenaming(false);
      void queryClient.invalidateQueries({ queryKey: ["card", id] });
      void queryClient.invalidateQueries({ queryKey: ["items"] });
      toast.success(patch.name ? "Analiz adı güncellendi." : "Görünüm kaydedildi.");
    },
    onError: (e) => toast.error(e.message),
  });
  const unsaved = display != null && q.data != null && display !== q.data.card.display;

  return (
    <div className="space-y-6">
      <Link href="/app" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="size-4" aria-hidden />
        Genel bakış
      </Link>
      {q.isPending ? (
        <div className="space-y-4">
          <Skeleton className="h-8 w-72" />
          <Skeleton className="aspect-[16/7] w-full" />
        </div>
      ) : q.isError ? (
        <p role="alert" className="text-sm text-destructive">
          {q.error.message}
        </p>
      ) : (
        <>
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0 space-y-1">
              {renaming ? (
                <form
                  className="flex items-center gap-2"
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (name.trim()) save.mutate({ name: name.trim() });
                  }}
                >
                  <Label htmlFor="card-title" className="sr-only">
                    Analiz adı
                  </Label>
                  <Input
                    id="card-title"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    onKeyDown={(e) => e.key === "Escape" && setRenaming(false)}
                    maxLength={120}
                    autoFocus
                    className="h-9 max-w-md text-lg font-semibold"
                  />
                  <Button type="submit" size="sm" variant="brand" disabled={!name.trim() || save.isPending}>
                    Kaydet
                  </Button>
                  <Button type="button" size="sm" variant="ghost" onClick={() => setRenaming(false)}>
                    Vazgeç
                  </Button>
                </form>
              ) : (
                <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
                  {q.data.card.name}
                  {canEdit && (
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label="Analizi yeniden adlandır"
                      onClick={() => {
                        setName(q.data.card.name);
                        setRenaming(true);
                      }}
                    >
                      <Pencil className="size-3.5" aria-hidden />
                    </Button>
                  )}
                </h1>
              )}
              {q.data.card.description && (
                <p className="text-sm text-muted-foreground">{q.data.card.description}</p>
              )}
            </div>
            <div className="flex shrink-0 items-center gap-1">
              {canEdit && unsaved && (
                <Button variant="outline" size="sm" onClick={() => save.mutate({ display: display! })} disabled={save.isPending}>
                  <Check className="size-4" aria-hidden />
                  Görünümü kaydet
                </Button>
              )}
              {canEdit && (display ?? q.data.card.display) === "progress" && (
                <GoalSetter
                  goal={q.data.card.goal}
                  onSave={(goal) => save.mutate({ goal, display: "progress" })}
                  saving={save.isPending}
                />
              )}
              {canEdit && <AddToDashboard resolveCardId={async () => id} />}
              <ExportMenu cardId={id} />
            </div>
          </header>
          <div className="surface p-5">
            <ResultView
              result={q.data.result}
              size="wide"
              display={q.data.card.display}
              goal={q.data.card.goal}
              onTypeChange={canEdit ? setDisplay : undefined}
              meta={
                <span className="text-xs text-muted-foreground tabular-nums">
                  {q.data.result.row_count.toLocaleString("tr-TR")} satır
                </span>
              }
              onDrill={
                q.data.drillable
                  ? (column, value) => setDrill({ cardId: id, title: q.data.card.name, column, value })
                  : undefined
              }
              onZoom={
                q.data.drillable
                  ? (value) => setDrill({ cardId: id, title: q.data.card.name, column: "", value, mode: "time" })
                  : undefined
              }
            />
          </div>
          {q.data.drillable && (
            <p className="text-xs text-muted-foreground">Keşfetmek için bir sütuna ya da noktaya tıklayın: kategoriler kırılım ve satırları, dönemler günlük/aylık görünümü açar.</p>
          )}
        </>
      )}
      <DrillSheet target={drill} onClose={() => setDrill(null)} />
    </div>
  );
}

/** Goal for a progress card: the meter's 100% mark. */
function GoalSetter({
  goal,
  onSave,
  saving,
}: {
  goal: number | null;
  onSave: (goal: number | null) => void;
  saving: boolean;
}) {
  const [value, setValue] = useState(goal?.toString() ?? "");
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm">
          <Target className="size-4" aria-hidden />
          Hedef
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-64 space-y-3">
        <div className="space-y-1.5">
          <Label htmlFor="goal" className="text-xs text-muted-foreground">
            Hedef değer
          </Label>
          <Input
            id="goal"
            type="number"
            min={0}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="h-8"
          />
        </div>
        <div className="flex items-center justify-between">
          <button
            type="button"
            className="text-sm text-muted-foreground hover:text-foreground"
            onClick={() => {
              setValue("");
              onSave(null);
            }}
          >
            Kaldır
          </button>
          <Button
            size="sm"
            variant="brand"
            disabled={saving || !(Number(value) > 0)}
            onClick={() => onSave(Number(value))}
          >
            Kaydet
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
