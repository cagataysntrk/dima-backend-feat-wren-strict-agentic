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

  const setGran = (g: string) => {
    const next = clone();
    next.timeDimensions = [{ dimension: "tarih", granularity: g }];
    onEdit({ cq: next, label: `chip: kova → ${g}` });
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

  // Kırılımdan tek değere GERİ dönüş: boyutu kaldır, o değere filtrele
  // (ör. cinsiyet kırılımı → yalnız Kadın).
  const dimToFilter = (dim: string, value: string) => {
    const next = clone();
    next.dimensions = dims.filter((x) => x !== dim);
    if (!(next.dimensions as string[]).length) delete next.dimensions;
    next.filters = [
      ...filters.filter((f) => f.dimension !== dim),
      { dimension: dim, operator: "eq", value },
    ];
    onEdit({ cq: next, label: `chip: kırılım → ${dim} = ${value}` });
  };

  // Chip YORUMU gösterir, ham tarihi değil: preset ("Bu yıl"), ay ("Temmuz 2026") ya da
  // okunur aralık ("1 Oca – 31 Mar 2026"). Ham değerler tooltip'te şeffaf kalır.
  const MONTHS_TR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                     "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
  const parseIso = (s: string) => {
    const [y, m, d] = s.split("-").map(Number);
    return { y, m, d };
  };
  const fmtShort = (s: string) => {
    const { y, m, d } = parseIso(s);
    return `${d} ${MONTHS_TR[m - 1].slice(0, 3)} ${y}`;
  };
  const periodLabel = (): string => {
    const gte = dateFilters.find((f) => f.operator === "gte")?.value;
    const lte = dateFilters.find((f) => f.operator === "lte")?.value;
    if (!gte && !lte) return "tümü";
    if (gte && !lte) {
      const preset = periodPresets().find((p) => p.start === gte);
      if (preset) return preset.label;
      return `${fmtShort(gte)}'den beri`;
    }
    if (gte && lte) {
      const g = parseIso(gte);
      const l = parseIso(lte);
      const lastDay = new Date(l.y, l.m, 0).getDate();
      if (g.d === 1 && g.m === l.m && g.y === l.y && l.d === lastDay) {
        return `${MONTHS_TR[g.m - 1]} ${g.y}`; // tam ay: "Temmuz 2026"
      }
      return `${fmtShort(gte)} – ${fmtShort(lte)}`;
    }
    return `≤ ${fmtShort(lte!)}`;
  };

  // Dönem hazır seçenekleri — client tarafında deterministik tarih (backend chip'leriyle aynı).
  // DİKKAT: toISOString() UTC'ye çevirir (TR'de 1 Ocak 00:00 → 31 Aralık!) — YEREL formatla.
  const iso = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const periodPresets = (): { label: string; start: string | null }[] => {
    const t = new Date();
    const monday = new Date(t);
    monday.setDate(t.getDate() - ((t.getDay() + 6) % 7));
    return [
      { label: "Bugün", start: iso(t) },
      { label: "Bu hafta", start: iso(monday) },
      { label: "Bu ay", start: iso(new Date(t.getFullYear(), t.getMonth(), 1)) },
      { label: "Bu yıl", start: iso(new Date(t.getFullYear(), 0, 1)) },
      { label: "Tümü", start: null },
    ];
  };

  const setPeriod = (label: string, start: string | null) => {
    const next = clone();
    const rest = filters.filter((f) => f.dimension !== "tarih");
    next.filters = start
      ? [...rest, { dimension: "tarih", operator: "gte", value: start }]
      : rest;
    if (!(next.filters as Filter[]).length) delete next.filters;
    onEdit({ cq: next, label: `chip: dönem → ${label}` });
  };

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

      {tds.map((t) => {
        const GRAN_TR: Record<string, string> = { day: "gün", week: "hafta", month: "ay", quarter: "çeyrek", year: "yıl" };
        const open = openFilter === "kova";
        return (
          <span key={t.dimension} className={`relative ${chip}`} title="Zaman kovası — tıkla: değiştir">
            <button
              onClick={() => setOpenFilter(open ? null : "kova")}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              kova: <span className="text-accent">{GRAN_TR[t.granularity] ?? t.granularity}</span> ▾
            </button>
            <button onClick={removeGran} className={xBtn} aria-label="Zaman kovasını kaldır">×</button>
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {(Object.entries(GRAN_TR) as [string, string][]).map(([g, label]) => (
                  <button
                    key={g}
                    onClick={() => { setOpenFilter(null); if (g !== t.granularity) setGran(g); }}
                    className={`px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06] ${g === t.granularity ? "text-accent" : ""}`}
                  >
                    {label}
                  </button>
                ))}
              </span>
            )}
          </span>
        );
      })}

      {dims.map((d) => {
        const opts = valuesFor(d);
        const open = openFilter === `dim:${d}`;
        if (!opts.length) {
          return (
            <span key={d} className={chip} title="Kırılım">
              kırılım: {d}
              <button onClick={() => removeDim(d)} className={xBtn} aria-label={`${d} kırılımını kaldır`}>×</button>
            </span>
          );
        }
        // Kategorik kırılım — tıkla: tek değere geri dön (filtre) ya da kaldır.
        return (
          <span key={d} className={`relative ${chip}`} title="Kırılım — tıkla: tek değere filtrele">
            <button
              onClick={() => setOpenFilter(open ? null : `dim:${d}`)}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              kırılım: {d} ▾
            </button>
            <button onClick={() => removeDim(d)} className={xBtn} aria-label={`${d} kırılımını kaldır`}>×</button>
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {opts.map((v) => (
                  <button
                    key={v}
                    onClick={() => { setOpenFilter(null); dimToFilter(d, v); }}
                    className="px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06]"
                  >
                    sadece {v}
                  </button>
                ))}
              </span>
            )}
          </span>
        );
      })}

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

      {(() => {
        const open = openFilter === "tarih";
        const raw = dateFilters.map((f) => `${f.operator} ${f.value}`).join(" · ");
        return (
          <span className={`relative ${chip}`} title={raw ? `Dönem (${raw}) — tıkla: değiştir` : "Dönem — tıkla: değiştir"}>
            <button
              onClick={() => setOpenFilter(open ? null : "tarih")}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              dönem:{" "}
              {dateFilters.length > 0 ? (
                <span className="text-accent">{periodLabel()}</span>
              ) : (
                "tümü"
              )}{" "}
              ▾
            </button>
            {dateFilters.length > 0 && (
              <button onClick={removeDateFilters} className={xBtn} aria-label="Dönem filtresini kaldır">×</button>
            )}
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {periodPresets().map((p) => (
                  <button
                    key={p.label}
                    onClick={() => { setOpenFilter(null); setPeriod(p.label, p.start); }}
                    className="whitespace-nowrap px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06]"
                  >
                    {p.label}
                  </button>
                ))}
              </span>
            )}
          </span>
        );
      })()}
    </div>
  );
}
