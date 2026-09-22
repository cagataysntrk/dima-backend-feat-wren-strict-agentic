// Engine query helpers for exploration (zoom / break out). Pure, unit-tested.
//
// v0.58 stores card queries as MBQL 5 ("stages", clauses carry an options map
// with a "lib/uuid"). Our filter helpers (filters.ts) speak the legacy shape
// ["op", ["field", id, opts], ...args]; `toMbql5` converts them.

export type Uuid = () => string;
type Opts = Record<string, unknown>;

/** Legacy ["field", id, opts|null] → MBQL 5 ["field", {lib/uuid, ...opts}, id]. */
export function field5(ref: unknown, uuid: Uuid): unknown[] {
  if (!Array.isArray(ref) || ref[0] !== "field") throw new Error("not a field ref");
  const [, id, opts] = ref as [string, number | string, Opts | null];
  return ["field", { ...(opts ?? {}), "lib/uuid": uuid() }, id];
}

/** Legacy filter clause → MBQL 5 (fields converted, options map inserted). */
export function toMbql5(clause: unknown[], uuid: Uuid): unknown[] {
  const [op, ...rest] = clause as [string, ...unknown[]];
  if (op === "time-interval") {
    const [field, n, unit, opts] = rest as [unknown, unknown, unknown, Opts | undefined];
    return ["time-interval", { ...(opts ?? {}), "lib/uuid": uuid() }, field5(field, uuid), n, unit];
  }
  const [field, ...args] = rest;
  return [op, { "lib/uuid": uuid() }, field5(field, uuid), ...args];
}

export type TimeUnit = "year" | "quarter" | "month" | "week" | "day";

/** Next finer granularity for a zoom, or null when already at the finest. */
export const ZOOM_TO: Record<TimeUnit, TimeUnit | null> = {
  year: "month",
  quarter: "month",
  month: "day",
  week: "day",
  day: null,
};

const iso = (d: Date) => d.toISOString().slice(0, 10);

/** [start, end] (inclusive, YYYY-MM-DD) of the period that starts at `value`. */
export function periodRange(value: string, unit: TimeUnit): [string, string] | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  if (!m) return null;
  const start = new Date(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3])));
  if (Number.isNaN(start.getTime())) return null;
  const end = new Date(start);
  if (unit === "year") end.setUTCFullYear(end.getUTCFullYear() + 1);
  else if (unit === "quarter") end.setUTCMonth(end.getUTCMonth() + 3);
  else if (unit === "month") end.setUTCMonth(end.getUTCMonth() + 1);
  else if (unit === "week") end.setUTCDate(end.getUTCDate() + 7);
  else end.setUTCDate(end.getUTCDate() + 1);
  end.setUTCDate(end.getUTCDate() - 1);
  return [iso(start), iso(end)];
}
