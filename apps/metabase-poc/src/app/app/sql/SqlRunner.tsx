"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Play, Save } from "lucide-react";
import { toast } from "sonner";
import { gateway } from "@/lib/gateway";
import { ResultView } from "@/components/ResultView";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

const EXAMPLE = `-- Yalnızca SELECT. Şirketinizin şeması arama yolunda değilse tablo adını şemayla yazın.
SELECT makine, round(avg(oee)::numeric, 1) AS oee_yuzde
FROM tenant_boyahane.oee_vardiya
GROUP BY makine
ORDER BY oee_yuzde DESC`;

export function SqlRunner() {
  const queryClient = useQueryClient();
  const [sql, setSql] = useState(EXAMPLE);
  const [name, setName] = useState("");
  const run = useMutation({ mutationFn: (q: string) => gateway.runSql(q) });
  const save = useMutation({
    mutationFn: () => gateway.saveSql(name.trim(), sql),
    onSuccess: ({ id }) => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
      toast.success("Analiz kaydedildi.", {
        action: { label: "Aç", onClick: () => window.location.assign(`/app/cards/${id}`) },
      });
      setName("");
    },
    onError: (e) => toast.error(e.message),
  });

  const submit = () => sql.trim() && run.mutate(sql);

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">SQL</h1>
        <p className="text-sm text-muted-foreground">
          Şirketinizin verisi üzerinde salt-okunur sorgular çalıştırın; sonucu analiz olarak kaydedin.
        </p>
      </header>
      <div className="space-y-2">
        <Label htmlFor="sql" className="sr-only">
          SQL sorgusu
        </Label>
        <Textarea
          id="sql"
          value={sql}
          onChange={(e) => setSql(e.target.value)}
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
              e.preventDefault();
              submit();
            }
          }}
          spellCheck={false}
          className="min-h-56 font-mono text-base leading-relaxed md:text-[13px]"
        />
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="brand" onClick={submit} disabled={run.isPending}>
            <Play className="size-4" aria-hidden />
            {run.isPending ? "Çalışıyor…" : "Çalıştır"}
          </Button>
          <span className="text-xs text-muted-foreground">⌘/Ctrl + Enter · en fazla 2.000 satır</span>
        </div>
      </div>

      {run.isError && (
        <p role="alert" className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {run.error.message}
        </p>
      )}

      {run.data && (
        <section className="space-y-4 rounded-xl border bg-card p-4" aria-label="Sonuç">
          <ResultView
            key={run.submittedAt}
            result={run.data}
            meta={
              <span className="text-xs text-muted-foreground tabular-nums">
                {run.data.row_count.toLocaleString("tr-TR")} satır
              </span>
            }
          />
          <form
            className="flex flex-wrap items-end gap-2 border-t pt-4"
            onSubmit={(e) => {
              e.preventDefault();
              if (name.trim()) save.mutate();
            }}
          >
            <div className="w-full min-w-0 flex-1 space-y-1.5 sm:w-auto sm:min-w-64">
              <Label htmlFor="card-name" className="text-xs text-muted-foreground">
                Analiz adı
              </Label>
              <Input id="card-name" value={name} onChange={(e) => setName(e.target.value)} maxLength={120} />
            </div>
            <Button type="submit" variant="outline" disabled={!name.trim() || save.isPending}>
              <Save className="size-4" aria-hidden />
              Kaydet
            </Button>
            {save.data && (
              <Link href={`/app/cards/${save.data.id}`} className="pb-2 text-sm text-brand hover:underline">
                Kaydedilen analizi aç
              </Link>
            )}
          </form>
        </section>
      )}
    </div>
  );
}
