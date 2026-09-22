"use client";

import { useDeferredValue, useState } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { CalendarRange, Check, ChevronDown, ListFilter, Search } from "lucide-react";
import { gateway, type Filters, type Parameter } from "@/lib/gateway";
import { DATE_PRESETS, describeDateFilter, parseDateFilter } from "@/lib/date-filter";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

interface Props {
  dashboardId: number;
  parameters: Parameter[];
  filters: Filters;
  onChange: (next: Filters) => void;
}

/**
 * Dashboard filters as a quiet chip row. The URL owns the state (caller);
 * active chips carry a low-opacity brand tint and say what they filter, so
 * the applied scope stays visible next to the numbers it changes.
 */
export function FilterBar({ dashboardId, parameters, filters, onChange }: Props) {
  const set = (slug: string, values: string[]) => {
    const next = { ...filters };
    if (values.length) next[slug] = values;
    else delete next[slug];
    onChange(next);
  };
  const active = parameters.some((p) => (filters[p.slug] ?? []).length > 0);

  return (
    <div role="toolbar" aria-label="Filtreler" className="flex flex-wrap items-center gap-2">
      {parameters.map((p) =>
        p.kind === "date" ? (
          <DateFilter key={p.slug} param={p} value={filters[p.slug]?.[0]} onChange={(v) => set(p.slug, v ? [v] : [])} />
        ) : (
          <CategoryFilter
            key={p.slug}
            dashboardId={dashboardId}
            param={p}
            values={filters[p.slug] ?? []}
            onChange={(vs) => set(p.slug, vs)}
          />
        ),
      )}
      {active && (
        <button
          type="button"
          onClick={() => onChange({})}
          className="rounded px-1 text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none"
        >
          Filtreleri temizle
        </button>
      )}
    </div>
  );
}

function Chip({
  active,
  icon: Icon,
  label,
  value,
  ...rest
}: React.ComponentProps<"button"> & {
  active: boolean;
  icon: typeof CalendarRange;
  label: string;
  value?: string;
}) {
  return (
    <button
      type="button"
      {...rest}
      className={cn(
        "inline-flex h-8 max-w-full items-center gap-1.5 rounded-md border px-2.5 text-sm transition-colors",
        "focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none",
        active
          ? "border-brand/30 bg-brand/10 text-foreground"
          : "border-dashed text-muted-foreground hover:bg-accent hover:text-foreground",
      )}
    >
      <Icon className={cn("size-3.5 shrink-0", active && "text-brand")} aria-hidden />
      <span className="shrink-0">{label}</span>
      {value && (
        <>
          <span className="h-3.5 w-px shrink-0 bg-border" aria-hidden />
          <span className="truncate font-medium">{value}</span>
        </>
      )}
      <ChevronDown className="size-3.5 shrink-0 opacity-60" aria-hidden />
    </button>
  );
}

// ── Date ─────────────────────────────────────────────────────────────────────

function DateFilter({
  param,
  value,
  onChange,
}: {
  param: Parameter;
  value?: string;
  onChange: (v: string | null) => void;
}) {
  const [open, setOpen] = useState(false);
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const pick = (v: string | null) => {
    onChange(v);
    setOpen(false);
  };
  const customValid = Boolean(from || to) && (!from || !to || from <= to);

  return (
    <Popover
      open={open}
      onOpenChange={(o) => {
        // Re-sync the custom range with the applied filter each time the menu opens.
        if (o) {
          const r = value ? parseDateFilter(value) : null;
          setFrom(r?.kind === "range" ? (r.from ?? "") : "");
          setTo(r?.kind === "range" ? (r.to ?? "") : "");
        }
        setOpen(o);
      }}
    >
      <PopoverTrigger asChild>
        <Chip active={!!value} icon={CalendarRange} label={param.name} value={value ? describeDateFilter(value) : undefined} />
      </PopoverTrigger>
      <PopoverContent align="start" className="w-80 p-0">
        <div className="grid grid-cols-2 gap-1 p-2">
          {DATE_PRESETS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => pick(p.value)}
              aria-pressed={value === p.value}
              className={cn(
                "flex items-center justify-between rounded-md px-2.5 py-1.5 text-left text-sm transition-colors hover:bg-accent",
                value === p.value && "bg-brand/10 font-medium",
              )}
            >
              {p.label}
              {value === p.value && <Check className="size-3.5 text-brand" aria-hidden />}
            </button>
          ))}
        </div>
        <form
          className="space-y-2 border-t p-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (customValid) pick(`${from}~${to}`);
          }}
        >
          <p className="text-xs font-medium text-muted-foreground">Özel aralık</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <Label htmlFor={`${param.slug}-from`} className="text-xs text-muted-foreground">
                Başlangıç
              </Label>
              <Input
                id={`${param.slug}-from`}
                type="date"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${param.slug}-to`} className="text-xs text-muted-foreground">
                Bitiş
              </Label>
              <Input
                id={`${param.slug}-to`}
                type="date"
                value={to}
                onChange={(e) => setTo(e.target.value)}
                className="h-8"
              />
            </div>
          </div>
          {from && to && from > to && (
            <p role="alert" className="text-xs text-destructive">
              Bitiş tarihi başlangıçtan önce olamaz.
            </p>
          )}
          <div className="flex items-center justify-between pt-1">
            <button
              type="button"
              disabled={!value}
              onClick={() => {
                setFrom("");
                setTo("");
                pick(null);
              }}
              className="text-sm text-muted-foreground hover:text-foreground disabled:opacity-40"
            >
              Temizle
            </button>
            <Button type="submit" size="sm" variant="brand" disabled={!customValid}>
              Uygula
            </Button>
          </div>
        </form>
      </PopoverContent>
    </Popover>
  );
}

// ── Category (multi-select + search) ─────────────────────────────────────────

function CategoryFilter({
  dashboardId,
  param,
  values,
  onChange,
}: {
  dashboardId: number;
  param: Parameter;
  values: string[];
  onChange: (vs: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const query = useDeferredValue(q.trim());
  const options = useQuery({
    queryKey: ["param-values", dashboardId, param.slug, query],
    queryFn: () =>
      query ? gateway.parameterSearch(dashboardId, param.slug, query) : gateway.parameterValues(dashboardId, param.slug),
    enabled: open,
    staleTime: 5 * 60_000,
    placeholderData: keepPreviousData,
  });
  const selected = new Set(values);
  const toggle = (v: string) => onChange(selected.has(v) ? values.filter((x) => x !== v) : [...values, v]);
  const summary = values.length === 0 ? undefined : values.length === 1 ? values[0] : `${values[0]} +${values.length - 1}`;
  // Selected values first so they stay reachable while searching.
  const list = [...values.filter((v) => !(options.data ?? []).includes(v)), ...(options.data ?? [])];

  return (
    <Popover
      open={open}
      onOpenChange={(o) => {
        setOpen(o);
        if (!o) setQ("");
      }}
    >
      <PopoverTrigger asChild>
        <Chip active={values.length > 0} icon={ListFilter} label={param.name} value={summary} />
      </PopoverTrigger>
      <PopoverContent align="start" className="w-72 p-0">
        <div className="flex items-center gap-2 border-b px-3">
          <Search className="size-4 shrink-0 text-muted-foreground" aria-hidden />
          <label htmlFor={`${param.slug}-search`} className="sr-only">
            {param.name} ara
          </label>
          <input
            id={`${param.slug}-search`}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={`${param.name} ara…`}
            autoComplete="off"
            className="h-10 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground md:text-sm"
          />
        </div>
        <div role="listbox" aria-multiselectable aria-label={param.name} className="max-h-64 overflow-y-auto p-1">
          {options.isPending && <p className="px-2 py-1.5 text-sm text-muted-foreground">Yükleniyor…</p>}
          {options.isError && <p className="px-2 py-1.5 text-sm text-destructive">Değerler yüklenemedi.</p>}
          {options.isSuccess && list.length === 0 && (
            <p className="px-2 py-1.5 text-sm text-muted-foreground">Eşleşen değer yok.</p>
          )}
          {list.map((v) => {
            const on = selected.has(v);
            return (
              <button
                key={v}
                type="button"
                role="option"
                aria-selected={on}
                onClick={() => toggle(v)}
                className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors hover:bg-accent"
              >
                <span
                  className={cn(
                    "grid size-4 shrink-0 place-items-center rounded-[4px] border",
                    on ? "border-brand bg-brand text-brand-foreground" : "border-input",
                  )}
                  aria-hidden
                >
                  {on && <Check className="size-3" />}
                </span>
                <span className="truncate">{v}</span>
              </button>
            );
          })}
        </div>
        {values.length > 0 && (
          <div className="flex items-center justify-between border-t px-3 py-2 text-xs text-muted-foreground">
            <span className="tabular-nums">{values.length} seçili</span>
            <button type="button" onClick={() => onChange([])} className="hover:text-foreground">
              Temizle
            </button>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
