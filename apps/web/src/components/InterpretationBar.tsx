"use client";

import { useQuery } from "@tanstack/react-query";
import { ChevronDown, Plus, X } from "lucide-react";
import { getSchema } from "@dima/api-client";
import type { CubeQuery } from "@dima/contracts";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

// Yorum çubuğu: sistemin sorudan çıkardığı YORUM (ölçü/kırılım/filtre/dönem) chip'ler
// olarak görünür ve OYNANABİLİR. Her düzenleme deterministik /cube ucuna gider (LLM yok).

interface Filter {
  dimension: string;
  operator: string;
  value: string | string[]; // in-filtre: liste
}

type Edit = { cq: CubeQuery; label: string };

const wrap =
  "inline-flex items-center rounded-md border border-border bg-card text-xs";
const trigger =
  "flex items-center gap-1 rounded-md px-2 py-0.5 text-muted-foreground outline-none transition-colors hover:text-foreground data-[state=open]:text-foreground";
const removeBtn = "pr-1.5 pl-0.5 text-muted-foreground transition-colors hover:text-brand";

export function InterpretationBar({
  cq,
  onEdit,
}: {
  cq: CubeQuery;
  onEdit: (edit: Edit) => void;
}) {
  const { data: schema } = useQuery({ queryKey: ["schema"], queryFn: getSchema });

  const measures = (cq.measures as string[]) ?? [];
  // CROSS-CUBE BLEND: başka cube'lardan katılan ölçüler (cq.blend). "kâr da ekle" tek
  // raporda ticaret + karlilik ölçüsünü birleştirir; burada cube etiketiyle gösterilir.
  const blend = (cq.blend as { cube: string; measures: string[] }[]) ?? [];
  const dims = (cq.dimensions as string[]) ?? [];
  const filters = (cq.filters as Filter[]) ?? [];
  const tds = (cq.timeDimensions as { dimension: string; granularity: string }[]) ?? [];

  const catFilters = filters.filter((f) => f.dimension !== "tarih");
  const dateFilters = filters.filter((f) => f.dimension === "tarih");

  const valuesFor = (dim: string): string[] => {
    for (const m of schema?.models ?? []) {
      for (const c of m.columns) {
        if (c.name === dim && c.values) return c.values;
      }
    }
    return [];
  };

  const clone = (): CubeQuery => JSON.parse(JSON.stringify(cq));

  // Ölçü kaldırma (canlı 2026-07-25: kırılım/filtre/kova/dönem chip'lerinde × vardı ama
  // ÖLÇÜde yoktu → kullanıcı çok-ölçülü rapordan ölçü düşüremiyordu). Son ölçü korunur
  // (raporun en az bir ölçüsü olmalı); sıralama o ölçüye bağlıysa düşer. Deterministik /cube.
  const removeMeasure = (m: string) => {
    const next = clone();
    next.measures = measures.filter((x) => x !== m);
    const ord = next.order as { measure?: string } | undefined;
    if (ord?.measure === m) delete next.order;
    onEdit({ cq: next, label: `chip: ölçü − ${m}` });
  };

  // Blend ölçüsü kaldırma: cq.blend'den düşür; o cube'un ölçüsü kalmazsa entry'i at,
  // hiç blend kalmazsa alanı sil (tek-cube rapora döner). Deterministik /cube.
  const removeBlendMeasure = (cubeName: string, m: string) => {
    const next = clone();
    const nb = ((next.blend as { cube: string; measures: string[] }[]) ?? [])
      .map((b) => (b.cube === cubeName ? { ...b, measures: b.measures.filter((x) => x !== m) } : b))
      .filter((b) => b.measures.length > 0);
    if (nb.length) next.blend = nb;
    else delete next.blend;
    onEdit({ cq: next, label: `chip: ölçü − ${m}` });
  };

  const removeDim = (d: string) => {
    const next = clone();
    next.dimensions = dims.filter((x) => x !== d);
    if (!(next.dimensions as string[]).length) delete next.dimensions;
    next.filters = filters.filter((f) => f.dimension !== d);
    if (!(next.filters as Filter[]).length) delete next.filters;
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

  // KIRILIM ALTINDA ÇOKLU DEĞER SEÇİMİ: tümü = filtresiz; tek = eq; birden çok = in.
  const setDimSelection = (dim: string, selected: string[], all: string[]) => {
    const next = clone();
    const others = filters.filter((f) => f.dimension !== dim);
    if (selected.length === 0 || selected.length === all.length) {
      next.filters = others;
    } else if (selected.length === 1) {
      next.filters = [...others, { dimension: dim, operator: "eq", value: selected[0] }];
    } else {
      next.filters = [...others, { dimension: dim, operator: "in", value: selected }];
    }
    if (!(next.filters as Filter[]).length) delete next.filters;
    onEdit({
      cq: next,
      label: `chip: ${dim} seçimi → ${selected.length && selected.length < all.length ? selected.join(", ") : "hepsi"}`,
    });
  };

  // ── dönem yorumu (ham tarih değil): preset / ay / okunur aralık ──
  const MONTHS_TR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
  const parseIso = (s: string) => {
    const [y, m, d] = s.split("-").map(Number);
    return { y, m, d };
  };
  const fmtShort = (s: string) => {
    const { y, m, d } = parseIso(s);
    return `${d} ${MONTHS_TR[m - 1].slice(0, 3)} ${y}`;
  };
  const periodLabel = (): string => {
    const gte = dateFilters.find((f) => f.operator === "gte")?.value as string | undefined;
    const lte = dateFilters.find((f) => f.operator === "lte")?.value as string | undefined;
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
        return `${MONTHS_TR[g.m - 1]} ${g.y}`;
      }
      return `${fmtShort(gte)} – ${fmtShort(lte)}`;
    }
    return `≤ ${fmtShort(lte!)}`;
  };
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

  const GRAN_TR: Record<string, string> = { day: "gün", week: "hafta", month: "ay", quarter: "çeyrek", year: "yıl" };

  // ── "+" ile yorum ekleme ────────────────────────────────────────────────
  // Aday alanlar şemadan gelir; zaten çubukta olanlar listelenmez.
  const cols = (schema?.models ?? []).flatMap((m) => m.columns);
  const addableDims = [
    ...new Set(
      cols
        .filter((c) => c.type !== "number" && c.name !== "tarih")
        .map((c) => c.name)
        .filter((n) => !dims.includes(n)),
    ),
  ];
  const addableMeasures = [
    ...new Set(
      cols
        .filter((c) => c.type === "number")
        .map((c) => c.name)
        .filter((n) => !measures.includes(n)),
    ),
  ];

  const addDim = (d: string) => {
    const next = clone();
    next.dimensions = [...dims, d];
    onEdit({ cq: next, label: `chip: kırılım + ${d}` });
  };
  const addMeasure = (m: string) => {
    const next = clone();
    next.measures = [...measures, m];
    onEdit({ cq: next, label: `chip: ölçü + ${m}` });
  };

  const canAdd = addableDims.length > 0 || addableMeasures.length > 0 || tds.length === 0;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {/* ölçüler — birden fazlaysa (ya da blend varsa) kaldırılabilir */}
      {measures.map((m) => (
        <span
          key={m}
          title="Ölçü"
          className={cn(
            "inline-flex items-center gap-1 rounded-md border border-brand/20 bg-brand/5 py-0.5 pl-2 text-xs text-foreground",
            measures.length > 1 || blend.length > 0 ? "pr-1" : "pr-2",
          )}
        >
          <span className="text-brand">◆</span> {m}
          {(measures.length > 1 || blend.length > 0) && (
            <button
              type="button"
              onClick={() => removeMeasure(m)}
              aria-label={`${m} ölçüsünü kaldır`}
              className="rounded-full p-0.5 text-muted-foreground transition-colors hover:text-brand"
            >
              <X className="size-3" />
            </button>
          )}
        </span>
      ))}

      {/* CROSS-CUBE BLEND ölçüleri — cube etiketiyle ("◆ brut_kar ·karlilik"): tek
          raporda birden çok cube. "kâr da ekle" bunları katar; × ile kaldırılır. */}
      {blend.flatMap((b) =>
        b.measures.map((m) => (
          <span
            key={`${b.cube}:${m}`}
            title={`Ölçü · ${b.cube}`}
            className="inline-flex items-center gap-1 rounded-md border border-brand/20 bg-brand/5 py-0.5 pr-1 pl-2 text-xs text-foreground"
          >
            <span className="text-brand">◆</span> {m}
            <span className="text-[10px] text-muted-foreground">·{b.cube}</span>
            <button
              type="button"
              onClick={() => removeBlendMeasure(b.cube, m)}
              aria-label={`${m} ölçüsünü kaldır`}
              className="rounded-full p-0.5 text-muted-foreground transition-colors hover:text-brand"
            >
              <X className="size-3" />
            </button>
          </span>
        )),
      )}

      {/* zaman kovası */}
      {tds.map((t) => (
        <span key={t.dimension} className={wrap} title="Zaman kovası">
          <DropdownMenu>
            <DropdownMenuTrigger className={trigger}>
              kova: <span className="text-brand">{GRAN_TR[t.granularity] ?? t.granularity}</span>
              <ChevronDown className="size-3" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="[&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
              {Object.entries(GRAN_TR).map(([g, label]) => (
                <DropdownMenuItem
                  key={g}
                  onSelect={() => g !== t.granularity && setGran(g)}
                  className={g === t.granularity ? "text-brand" : ""}
                >
                  {label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <button onClick={removeGran} className={removeBtn} aria-label="Zaman kovasını kaldır">
            <X className="size-3" />
          </button>
        </span>
      ))}

      {/* kırılımlar */}
      {dims.map((d) => {
        const opts = valuesFor(d);
        if (!opts.length) {
          return (
            <span key={d} className={wrap} title="Kırılım">
              <span className={cn(trigger, "cursor-default hover:text-muted-foreground")}>
                kırılım: {d}
              </span>
              <button onClick={() => removeDim(d)} className={removeBtn} aria-label={`${d} kırılımını kaldır`}>
                <X className="size-3" />
              </button>
            </span>
          );
        }
        const dimFilter = catFilters.find((f) => f.dimension === d);
        const selected = dimFilter
          ? Array.isArray(dimFilter.value)
            ? dimFilter.value
            : [dimFilter.value]
          : opts;
        const label =
          dimFilter && selected.length < opts.length
            ? `kırılım: ${d} · ${selected.length}/${opts.length}`
            : `kırılım: ${d}`;
        return (
          <span key={d} className={wrap} title="Kırılım — değerleri seç">
            <DropdownMenu>
              <DropdownMenuTrigger className={trigger}>
                {label}
                <ChevronDown className="size-3" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="max-h-72 overflow-auto [&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
                {opts.map((v) => {
                  const on = selected.includes(v);
                  return (
                    <DropdownMenuCheckboxItem
                      key={v}
                      checked={on}
                      onSelect={(e) => e.preventDefault()}
                      onCheckedChange={() => {
                        // TÜMÜ seçiliyken tıklama = "sadece bu"; kısmi seçimde aç/kapa.
                        const allOn = selected.length === opts.length;
                        const nextSel = allOn ? [v] : on ? selected.filter((x) => x !== v) : [...selected, v];
                        if (!nextSel.length) return;
                        setDimSelection(d, nextSel, opts);
                      }}
                    >
                      {v}
                    </DropdownMenuCheckboxItem>
                  );
                })}
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={() => setDimSelection(d, opts, opts)}>
                  hepsi
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <button onClick={() => removeDim(d)} className={removeBtn} aria-label={`${d} kırılımını kaldır`}>
              <X className="size-3" />
            </button>
          </span>
        );
      })}

      {/* kategorik filtreler (kırılımda olmayan) */}
      {catFilters
        .filter((f) => !dims.includes(f.dimension))
        .map((f) => {
          const opts = valuesFor(f.dimension);
          return (
            <span key={f.dimension} className={wrap} title="Filtre">
              <DropdownMenu>
                <DropdownMenuTrigger className={trigger}>
                  {f.dimension} {Array.isArray(f.value) ? "∈" : "="}{" "}
                  <span className="text-brand">
                    {Array.isArray(f.value) ? f.value.join(", ") : f.value}
                  </span>
                  <ChevronDown className="size-3" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="max-h-72 overflow-auto [&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
                  {opts.map((v) => (
                    <DropdownMenuItem
                      key={v}
                      onSelect={() => v !== f.value && setFilterValue(f.dimension, v)}
                      className={v === f.value ? "text-brand" : ""}
                    >
                      {v}
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onSelect={() => filterToDim(f.dimension)}>
                    ◫ hepsi ayrı (kırılım)
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <button onClick={() => removeFilter(f.dimension)} className={removeBtn} aria-label="Filtreyi kaldır">
                <X className="size-3" />
              </button>
            </span>
          );
        })}

      {/* dönem */}
      <span className={wrap} title="Dönem">
        <DropdownMenu>
          <DropdownMenuTrigger className={trigger}>
            dönem:{" "}
            {dateFilters.length > 0 ? <span className="text-brand">{periodLabel()}</span> : "tümü"}
            <ChevronDown className="size-3" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="[&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
            {periodPresets().map((p) => (
              <DropdownMenuItem key={p.label} onSelect={() => setPeriod(p.label, p.start)}>
                {p.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        {dateFilters.length > 0 && (
          <button onClick={removeDateFilters} className={removeBtn} aria-label="Dönem filtresini kaldır">
            <X className="size-3" />
          </button>
        )}
      </span>

      {/* yorum ekle — yuvarlak "+", açılır menüden ölçü/kırılım/zaman kovası */}
      {canAdd && (
        <DropdownMenu>
          <Tooltip>
            <TooltipTrigger asChild>
              <DropdownMenuTrigger
                aria-label="Yorum ekle"
                className="inline-flex size-6 items-center justify-center rounded-full border border-dashed border-border text-muted-foreground outline-none transition-colors hover:border-brand/50 hover:text-brand focus-visible:ring-[3px] focus-visible:ring-ring/25 data-[state=open]:border-brand/50 data-[state=open]:text-brand"
              >
                <Plus className="size-3.5" />
              </DropdownMenuTrigger>
            </TooltipTrigger>
            <TooltipContent side="top">Yorum ekle</TooltipContent>
          </Tooltip>
          <DropdownMenuContent align="start" className="w-48 [&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
            {addableMeasures.length > 0 && (
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>Ölçü ekle</DropdownMenuSubTrigger>
                <DropdownMenuSubContent className="max-h-72 overflow-auto [&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
                  {addableMeasures.map((m) => (
                    <DropdownMenuItem key={m} onSelect={() => addMeasure(m)}>
                      {m}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuSubContent>
              </DropdownMenuSub>
            )}
            {addableDims.length > 0 && (
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>Kırılım ekle</DropdownMenuSubTrigger>
                <DropdownMenuSubContent className="max-h-72 overflow-auto [&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
                  {addableDims.map((d) => (
                    <DropdownMenuItem key={d} onSelect={() => addDim(d)}>
                      {d}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuSubContent>
              </DropdownMenuSub>
            )}
            {tds.length === 0 && (
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>Zaman kovası</DropdownMenuSubTrigger>
                <DropdownMenuSubContent className="[&_[data-slot=dropdown-menu-item]]:text-xs [&_[data-slot=dropdown-menu-checkbox-item]]:text-xs [&_[data-slot=dropdown-menu-sub-trigger]]:text-xs">
                  {Object.entries(GRAN_TR).map(([g, label]) => (
                    <DropdownMenuItem key={g} onSelect={() => setGran(g)}>
                      {label}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuSubContent>
              </DropdownMenuSub>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  );
}
