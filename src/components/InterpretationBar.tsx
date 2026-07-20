"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { getSchema } from "@/lib/api-client";
import type { CubeQuery } from "@/lib/types";

// Yorum çubuğu: sistemin sorudan çıkardığı YORUM (ölçü/kırılım/filtre/dönem) chip'ler
// olarak görünür ve OYNANABİLİR — UpcyBrain IntentRouter deseninin CubeQuery-natif hali.
// Her düzenleme deterministik /cube ucuna gider (LLM yok).

interface Filter {
  dimension: string;
  operator: string;
  value: string;
}

type Edit = { cq: CubeQuery; label: string };

const chip =
  "inline-flex items-center gap-1 border border-hairline px-1.5 py-0.5 font-mono text-[11px] text-neutral-600 dark:text-neutral-300";
const xBtn =
  "ml-0.5 text-neutral-400 transition-colors hover:text-accent";

export function InterpretationBar({
  cq,
  onEdit,
}: {
  cq: CubeQuery;
  onEdit: (edit: Edit) => void;
}) {
  const { data: schema } = useQuery({ queryKey: ["schema"], queryFn: getSchema });
  const [openFilter, setOpenFilter] = useState<string | null>(null);

  const measures = (cq.measures as string[]) ?? [];
  const dims = (cq.dimensions as string[]) ?? [];
  const filters = (cq.filters as Filter[]) ?? [];
  const tds = (cq.timeDimensions as { dimension: string; granularity: string }[]) ?? [];

  const catFilters = filters.filter((f) => f.dimension !== "tarih");
  const dateFilters = filters.filter((f) => f.dimension === "tarih");

  // Boyutun kategorik değerleri (şemadan) — filtre chip'i düzenlenirken seçenek olur.
  const valuesFor = (dim: string): string[] => {
    for (const m of schema?.models ?? []) {
      for (const c of m.columns) {
        if (c.name === dim && c.values) return c.values;
      }
    }
    return [];
  };

  const clone = (): CubeQuery => JSON.parse(JSON.stringify(cq));

  const removeDim = (d: string) => {
    const next = clone();
    next.dimensions = dims.filter((x) => x !== d);
    if (!(next.dimensions as string[]).length) delete next.dimensions;
    onEdit({ cq: next, label: `chip: kırılım − ${d}` });
  };

  const removeGran = () => {
    const next = clone();
    delete next.timeDimensions;
    onEdit({ cq: next, label: "chip: zaman kovası kaldırıldı" });
  };

  const removeDateFilters = () => {
    const next = clone();
    next.filters = filters.filter((f) => f.dimension !== "tarih");
    if (!(next.filters as Filter[]).length) delete next.filters;
    onEdit({ cq: next, label: "chip: dönem → tüm zamanlar" });
  };

  const setFilterValue = (dim: string, value: string) => {
    const next = clone();
    next.filters = [
      ...filters.filter((f) => f.dimension !== dim),
      { dimension: dim, operator: "eq", value },
    ];
    onEdit({ cq: next, label: `chip: ${dim} = ${value}` });
  };

  const filterToDim = (dim: string) => {
    const next = clone();
    next.filters = filters.filter((f) => f.dimension !== dim);
    if (!(next.filters as Filter[]).length) delete next.filters;
    next.dimensions = [...dims, dim];
    onEdit({ cq: next, label: `chip: ${dim} → kırılım (hepsi ayrı)` });
  };

  const removeFilter = (dim: string) => {
    const next = clone();
    next.filters = filters.filter((f) => f.dimension !== dim);
    if (!(next.filters as Filter[]).length) delete next.filters;
    onEdit({ cq: next, label: `chip: ${dim} filtresi kaldırıldı` });
  };

  const fmtDate = (f: Filter) => f.value;

  return (
    <div className="mb-4 flex flex-wrap items-center gap-1.5">
      <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
        yorum
      </span>

      {measures.map((m) => (
        <span key={m} className={chip} title="Ölçü">
          <span className="text-accent">◆</span> {m}
        </span>
      ))}

      {tds.map((t) => (
        <span key={t.dimension} className={chip} title="Zaman kovası">
          kova: {t.granularity === "month" ? "ay" : t.granularity === "week" ? "hafta" : "gün"}
          <button onClick={removeGran} className={xBtn} aria-label="Zaman kovasını kaldır">×</button>
        </span>
      ))}

      {dims.map((d) => (
        <span key={d} className={chip} title="Kırılım">
          kırılım: {d}
          <button onClick={() => removeDim(d)} className={xBtn} aria-label={`${d} kırılımını kaldır`}>×</button>
        </span>
      ))}

      {catFilters.map((f) => {
        const opts = valuesFor(f.dimension);
        const open = openFilter === f.dimension;
        return (
          <span key={f.dimension} className={`relative ${chip}`} title="Filtre — tıkla: değiştir">
            <button
              onClick={() => setOpenFilter(open ? null : f.dimension)}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              {f.dimension} = <span className="text-accent">{f.value}</span> ▾
            </button>
            <button onClick={() => removeFilter(f.dimension)} className={xBtn} aria-label="Filtreyi kaldır">×</button>
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {opts.map((v) => (
                  <button
                    key={v}
                    onClick={() => { setOpenFilter(null); if (v !== f.value) setFilterValue(f.dimension, v); }}
                    className={`px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06] ${v === f.value ? "text-accent" : ""}`}
                  >
                    {v}
                  </button>
                ))}
                <button
                  onClick={() => { setOpenFilter(null); filterToDim(f.dimension); }}
                  className="border-t border-hairline px-2 py-1 text-left font-mono text-[11px] text-neutral-500 hover:bg-neutral-500/[0.06]"
                >
                  ◫ hepsi ayrı (kırılım)
                </button>
              </span>
            )}
          </span>
        );
      })}

      {dateFilters.length > 0 && (
        <span className={chip} title="Dönem">
          tarih: {dateFilters.map(fmtDate).join(" → ")}
          <button onClick={removeDateFilters} className={xBtn} aria-label="Dönem filtresini kaldır">×</button>
        </span>
      )}
    </div>
  );
}
