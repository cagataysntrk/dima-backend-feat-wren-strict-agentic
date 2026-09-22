"use client";

import { useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronRight, Play, Save, Table2, WrapText } from "lucide-react";
import { toast } from "sonner";
import { formatSql } from "@dima/domain";
import { gateway } from "@/lib/gateway";
import { parseVariables } from "@/lib/sql-vars";
import { cn } from "@dima/ui/utils";
import { ResultView } from "@dima/ui/result/ResultView";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Label } from "@dima/ui/primitives/label";
import { SqlEditor } from "@dima/ui/report/SqlEditor";

const EXAMPLE = `-- Yalnızca SELECT. {{değişken}} yazarsanız altta bir alan açılır;
-- [[ ... ]] içine alınan koşul, değişken boşsa sorgudan düşer.
SELECT makine, round(avg(oee)::numeric, 1) AS oee_yuzde
FROM tenant_boyahane.oee_vardiya
WHERE 1 = 1
  [[AND makine = {{makine}}]]
  [[AND tarih >= {{baslangic}}]]
GROUP BY makine
ORDER BY oee_yuzde DESC`;

/** Word being typed at the cursor (letters, digits, underscore, dot). */
function wordAt(text: string, caret: number): { word: string; start: number } {
  const before = text.slice(0, caret);
  const m = /[\w.]+$/.exec(before);
  return { word: m?.[0] ?? "", start: m ? caret - m[0].length : caret };
}

export function SqlRunner() {
  const queryClient = useQueryClient();
  const editor = useRef<HTMLTextAreaElement>(null);
  const [sql, setSql] = useState(EXAMPLE);
  const [name, setName] = useState("");
  const [values, setValues] = useState<Record<string, string>>({});
  const [caret, setCaret] = useState(0);
  const tables = useQuery({ queryKey: ["tables"], queryFn: gateway.tables, staleTime: 10 * 60_000 });

  const vars = useMemo(() => parseVariables(sql), [sql]);
  const run = useMutation({ mutationFn: () => gateway.runSql(sql, values) });
  const save = useMutation({
    mutationFn: () => gateway.saveSql(name.trim(), sql, values),
    onSuccess: ({ id }) => {
      void queryClient.invalidateQueries({ queryKey: ["items"] });
      toast.success("Analiz kaydedildi.", {
        action: { label: "Aç", onClick: () => window.location.assign(`/app/cards/${id}`) },
      });
      setName("");
    },
    onError: (e) => toast.error(e.message),
  });

  // Table/column name suggestions for the word at the cursor.
  const suggestions = useMemo(() => {
    const { word } = wordAt(sql, caret);
    const term = word.split(".").pop() ?? "";
    if (term.length < 2 || !tables.data) return [];
    const hits: { text: string; hint: string }[] = [];
    for (const t of tables.data) {
      if (t.name.toLowerCase().startsWith(term.toLowerCase())) hits.push({ text: t.name, hint: "tablo" });
      for (const c of t.columns) {
        if (c.toLowerCase().startsWith(term.toLowerCase())) hits.push({ text: c, hint: t.name });
      }
    }
    return [...new Map(hits.map((h) => [h.text, h])).values()].slice(0, 6);
  }, [sql, caret, tables.data]);

  const insert = (text: string, replaceWord = false) => {
    const el = editor.current;
    const at = el?.selectionStart ?? sql.length;
    const { start } = wordAt(sql, at);
    const from = replaceWord ? start : at;
    const next = `${sql.slice(0, from)}${text}${sql.slice(at)}`;
    setSql(next);
    requestAnimationFrame(() => {
      el?.focus();
      const pos = from + text.length;
      el?.setSelectionRange(pos, pos);
      setCaret(pos);
    });
  };

  const submit = () => sql.trim() && run.mutate();

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">SQL</h1>
        <p className="text-sm text-muted-foreground">
          Şirketinizin verisi üzerinde salt-okunur sorgular çalıştırın; sonucu analiz olarak kaydedin.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[1fr_16rem]">
        <div className="space-y-3">
          <Label htmlFor="sql" className="sr-only">
            SQL sorgusu
          </Label>
          <SqlEditor
            id="sql"
            ref={editor}
            value={sql}
            onChange={setSql}
            onCaret={setCaret}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
                e.preventDefault();
                submit();
              }
              if (e.key === "Tab" && suggestions.length > 0) {
                e.preventDefault();
                insert(suggestions[0].text, true);
              }
            }}
          />

          {suggestions.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs text-muted-foreground">Tab ↹</span>
              {suggestions.map((s) => (
                <button
                  key={s.text}
                  type="button"
                  onClick={() => insert(s.text, true)}
                  className="inline-flex items-center gap-1.5 rounded-md border border-dashed px-2 py-1 text-xs transition-colors hover:bg-accent"
                >
                  <span className="font-medium">{s.text}</span>
                  <span className="text-muted-foreground">{s.hint}</span>
                </button>
              ))}
            </div>
          )}

          {vars.length > 0 && (
            <div className="surface space-y-3 p-4">
              <p className="text-xs font-medium text-muted-foreground">Değişkenler</p>
              <div className="grid gap-3 sm:grid-cols-2">
                {vars.map((v) => (
                  <div key={v.name} className="space-y-1.5">
                    <Label htmlFor={`var-${v.name}`} className="text-xs">
                      {v.label}
                      <span className="ml-1 font-mono text-[11px] text-muted-foreground">{`{{${v.name}}}`}</span>
                    </Label>
                    <Input
                      id={`var-${v.name}`}
                      type={v.type === "date" ? "date" : v.type === "number" ? "number" : "text"}
                      value={values[v.name] ?? ""}
                      onChange={(e) => setValues((prev) => ({ ...prev, [v.name]: e.target.value }))}
                      className="h-8"
                    />
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground">
                Boş bırakılan değişkenin [[ … ]] koşulu sorgudan düşer. Kaydederken mevcut değerler varsayılan olur.
              </p>
            </div>
          )}

          <div className="flex flex-wrap items-center gap-2">
            <Button variant="brand" onClick={submit} disabled={run.isPending}>
              <Play className="size-4" aria-hidden />
              {run.isPending ? "Çalışıyor…" : "Çalıştır"}
            </Button>
            <Button variant="ghost" onClick={() => setSql(formatSql(sql))} disabled={!sql.trim()}>
              <WrapText className="size-4" aria-hidden />
              Biçimlendir
            </Button>
            <span className="text-xs text-muted-foreground">⌘/Ctrl + Enter · en fazla 2.000 satır</span>
          </div>
        </div>

        <SchemaBrowser tables={tables.data} loading={tables.isPending} onPick={(text) => insert(`${text} `)} />
      </div>

      {run.isError && (
        <p
          role="alert"
          className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive"
        >
          {run.error.message}
        </p>
      )}

      {run.data && (
        <section className="surface space-y-4 p-5" aria-label="Sonuç">
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

/** Company tables and columns; clicking a name drops it into the query. */
function SchemaBrowser({
  tables,
  loading,
  onPick,
}: {
  tables?: { name: string; columns: string[] }[];
  loading: boolean;
  onPick: (text: string) => void;
}) {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <aside className="surface h-fit max-h-[32rem] overflow-y-auto p-2 lg:sticky lg:top-2" aria-label="Tablolar">
      <p className="px-2 py-1.5 text-xs font-medium text-muted-foreground">Tablolar</p>
      {loading && <p className="px-2 py-1.5 text-sm text-muted-foreground">Yükleniyor…</p>}
      <ul className="space-y-0.5">
        {tables?.map((t) => (
          <li key={t.name}>
            <div className="flex items-center">
              <button
                type="button"
                aria-expanded={open === t.name}
                onClick={() => setOpen(open === t.name ? null : t.name)}
                className="flex min-w-0 flex-1 items-center gap-1.5 rounded-md px-2 py-1.5 text-left text-sm transition-colors hover:bg-accent"
              >
                <ChevronRight
                  className={cn("size-3.5 shrink-0 text-muted-foreground transition-transform", open === t.name && "rotate-90")}
                  aria-hidden
                />
                <Table2 className="size-3.5 shrink-0 text-muted-foreground" aria-hidden />
                <span className="truncate">{t.name}</span>
              </button>
              <button
                type="button"
                onClick={() => onPick(t.name)}
                aria-label={`${t.name} tablosunu sorguya ekle`}
                className="rounded-md px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                ekle
              </button>
            </div>
            {open === t.name && (
              <ul className="mb-1 ml-6 space-y-0.5">
                {t.columns.map((c) => (
                  <li key={c}>
                    <button
                      type="button"
                      onClick={() => onPick(c)}
                      className="w-full truncate rounded-md px-2 py-1 text-left font-mono text-[12px] text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                    >
                      {c}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </aside>
  );
}
