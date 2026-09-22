// Date filter values (shared by UI and gateway). Pure, unit-tested.
//
// Values use the engine's dashboard-parameter grammar so they pass through
// unchanged; they are also what we keep in the URL:
//   2025-01-01~2025-03-31   range        2025-01-01~ / ~2024-12-31   open range
//   past3months / past3months~  last N complete units (~ = include current)
//   next7days               next N units   thisyear / thismonth …   current unit
//   2025-03                 one month      Q1-2025   one quarter    2025-02-10  one day

export type DateUnit = "day" | "week" | "month" | "quarter" | "year";

const RANGE = /^(\d{4}-\d{2}-\d{2})?~(\d{4}-\d{2}-\d{2})?$/;
const RELATIVE = /^(past|next)(\d{1,4})(day|week|month|quarter|year)s(~)?$/;
const CURRENT = /^this(day|week|month|quarter|year)$/;
const MONTH = /^(\d{4})-(\d{2})$/;
const QUARTER = /^Q([1-4])-(\d{4})$/;
const DAY = /^\d{4}-\d{2}-\d{2}$/;

export type ParsedDate =
  | { kind: "range"; from: string | null; to: string | null }
  | { kind: "relative"; dir: "past" | "next"; n: number; unit: DateUnit; includeCurrent: boolean }
  | { kind: "current"; unit: DateUnit }
  | { kind: "day"; day: string };

const isDate = (s: string) => !Number.isNaN(Date.parse(`${s}T00:00:00Z`));
const pad = (n: number) => String(n).padStart(2, "0");
const lastDay = (y: number, m: number) => new Date(Date.UTC(y, m, 0)).getUTCDate();

export function parseDateFilter(value: string): ParsedDate | null {
  let m = RANGE.exec(value);
  if (m) {
    const [, from = null, to = null] = m;
    if (!from && !to) return null;
    if ((from && !isDate(from)) || (to && !isDate(to))) return null;
    if (from && to && from > to) return null;
    return { kind: "range", from, to };
  }
  if ((m = RELATIVE.exec(value))) {
    const n = Number(m[2]);
    if (n < 1) return null;
    return { kind: "relative", dir: m[1] as "past" | "next", n, unit: m[3] as DateUnit, includeCurrent: !!m[4] };
  }
  if ((m = CURRENT.exec(value))) return { kind: "current", unit: m[1] as DateUnit };
  if ((m = MONTH.exec(value))) {
    const y = Number(m[1]);
    const mo = Number(m[2]);
    if (mo < 1 || mo > 12) return null;
    return { kind: "range", from: `${y}-${pad(mo)}-01`, to: `${y}-${pad(mo)}-${pad(lastDay(y, mo))}` };
  }
  if ((m = QUARTER.exec(value))) {
    const q = Number(m[1]);
    const y = Number(m[2]);
    const endMonth = q * 3;
    return { kind: "range", from: `${y}-${pad(endMonth - 2)}-01`, to: `${y}-${pad(endMonth)}-${pad(lastDay(y, endMonth))}` };
  }
  if (DAY.test(value) && isDate(value)) return { kind: "day", day: value };
  return null;
}

export const isDateFilter = (value: string) => parseDateFilter(value) !== null;

const UNIT_TR: Record<DateUnit, string> = { day: "gün", week: "hafta", month: "ay", quarter: "çeyrek", year: "yıl" };
const CURRENT_TR: Record<DateUnit, string> = {
  day: "Bugün",
  week: "Bu hafta",
  month: "Bu ay",
  quarter: "Bu çeyrek",
  year: "Bu yıl",
};

const fmtDay = (d: string) =>
  new Date(`${d}T00:00:00Z`).toLocaleDateString("tr-TR", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });

/** Short Turkish label for a filter value, e.g. "Son 3 ay", "1 Oca 2025 – 31 Mar 2025". */
export function describeDateFilter(value: string): string {
  const preset = DATE_PRESETS.find((p) => p.value === value);
  if (preset) return preset.label;
  const p = parseDateFilter(value);
  if (!p) return value;
  switch (p.kind) {
    case "current":
      return CURRENT_TR[p.unit];
    case "relative":
      return `${p.dir === "past" ? "Son" : "Sonraki"} ${p.n} ${UNIT_TR[p.unit]}${p.includeCurrent ? " (bugün dahil)" : ""}`;
    case "day":
      return fmtDay(p.day);
    case "range":
      if (p.from && p.to) return `${fmtDay(p.from)} – ${fmtDay(p.to)}`;
      return p.from ? `${fmtDay(p.from)} sonrası` : `${fmtDay(p.to!)} öncesi`;
  }
}

/** Quick picks shown in the date filter menu (engine semantics: "past" = complete units). */
export const DATE_PRESETS: { value: string; label: string }[] = [
  { value: "past7days~", label: "Son 7 gün" },
  { value: "past30days~", label: "Son 30 gün" },
  { value: "past3months~", label: "Son 3 ay" },
  { value: "past12months~", label: "Son 12 ay" },
  { value: "thismonth", label: "Bu ay" },
  { value: "thisquarter", label: "Bu çeyrek" },
  { value: "thisyear", label: "Bu yıl" },
  { value: "past1years", label: "Geçen yıl" },
];
