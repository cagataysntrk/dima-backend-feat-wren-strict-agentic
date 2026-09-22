"use client";

import { useQuery } from "@tanstack/react-query";
import { CalendarRange, X } from "lucide-react";
import { gateway, type Filters, type Parameter } from "@/lib/gateway";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const ALL = "__all__";

interface Props {
  dashboardId: number;
  parameters: Parameter[];
  filters: Filters;
  onChange: (next: Filters) => void;
}

/** Dashboard filters. State lives in the URL (owned by the caller). */
export function FilterBar({ dashboardId, parameters, filters, onChange }: Props) {
  const set = (slug: string, values: string[]) => {
    const next = { ...filters };
    if (values.length) next[slug] = values;
    else delete next[slug];
    onChange(next);
  };
  const active = Object.keys(filters).length > 0;

  return (
    <div className="flex flex-wrap items-end gap-x-4 gap-y-3 rounded-xl border bg-card px-4 py-3">
      {parameters.map((p) =>
        p.kind === "date" ? (
          <DateRange key={p.slug} param={p} value={filters[p.slug]?.[0]} onChange={(v) => set(p.slug, v ? [v] : [])} />
        ) : (
          <Category
            key={p.slug}
            dashboardId={dashboardId}
            param={p}
            value={filters[p.slug]?.[0]}
            onChange={(v) => set(p.slug, v ? [v] : [])}
          />
        ),
      )}
      {active && (
        <Button variant="ghost" size="sm" className="ml-auto" onClick={() => onChange({})}>
          <X className="size-4" aria-hidden />
          Filtreleri temizle
        </Button>
      )}
    </div>
  );
}

function yearPresets(): { label: string; value: string }[] {
  const y = new Date().getFullYear();
  return [y, y - 1, y - 2].map((year) => ({ label: String(year), value: `${year}-01-01~${year}-12-31` }));
}

function DateRange({
  param,
  value,
  onChange,
}: {
  param: Parameter;
  value?: string;
  onChange: (v: string | null) => void;
}) {
  const [from = "", to = ""] = value?.split("~") ?? [];
  const update = (f: string, t: string) => {
    if (f && t) onChange(f <= t ? `${f}~${t}` : `${t}~${f}`);
    else if (!f && !t) onChange(null);
  };
  return (
    <fieldset className="flex flex-wrap items-end gap-2">
      <legend className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        <CalendarRange className="size-3.5" aria-hidden />
        {param.name}
      </legend>
      <div>
        <Label htmlFor={`${param.slug}-from`} className="sr-only">
          Başlangıç
        </Label>
        <Input
          id={`${param.slug}-from`}
          type="date"
          className="h-8 w-[9.5rem] text-base md:text-sm"
          value={from}
          onChange={(e) => update(e.target.value, to || e.target.value)}
        />
      </div>
      <span className="pb-1.5 text-muted-foreground" aria-hidden>
        –
      </span>
      <div>
        <Label htmlFor={`${param.slug}-to`} className="sr-only">
          Bitiş
        </Label>
        <Input
          id={`${param.slug}-to`}
          type="date"
          className="h-8 w-[9.5rem] text-base md:text-sm"
          value={to}
          onChange={(e) => update(from || e.target.value, e.target.value)}
        />
      </div>
      <div className="flex gap-1">
        {yearPresets().map((p) => (
          <Button
            key={p.value}
            size="sm"
            variant={value === p.value ? "secondary" : "ghost"}
            className="h-8 px-2 text-xs tabular-nums"
            onClick={() => onChange(value === p.value ? null : p.value)}
          >
            {p.label}
          </Button>
        ))}
      </div>
    </fieldset>
  );
}

function Category({
  dashboardId,
  param,
  value,
  onChange,
}: {
  dashboardId: number;
  param: Parameter;
  value?: string;
  onChange: (v: string | null) => void;
}) {
  const q = useQuery({
    queryKey: ["param-values", dashboardId, param.slug],
    queryFn: () => gateway.parameterValues(dashboardId, param.slug),
    staleTime: 5 * 60_000,
  });
  return (
    <div className="space-y-1.5">
      <Label className="text-xs text-muted-foreground" htmlFor={`${param.slug}-select`}>
        {param.name}
      </Label>
      <Select value={value ?? ALL} onValueChange={(v) => onChange(v === ALL ? null : v)}>
        <SelectTrigger id={`${param.slug}-select`} size="sm" className="h-8 min-w-44 text-sm">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ALL}>Tümü</SelectItem>
          {(q.data ?? []).map((v) => (
            <SelectItem key={v} value={v}>
              {v}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
