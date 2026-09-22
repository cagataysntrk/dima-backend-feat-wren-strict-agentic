// Dashboard filter value → MBQL filter clause, used by drill-down so the detail
// rows respect the same filters as the widget. Pure, unit-tested.

import { parseDateFilter } from "@/lib/date-filter";

type Clause = unknown[];

/** Date filter on a field, or null when the value is invalid. */
export function dateClause(field: unknown, value: string): Clause | null {
  const p = parseDateFilter(value);
  if (!p) return null;
  switch (p.kind) {
    case "day":
      return ["=", field, p.day];
    case "range":
      if (p.from && p.to) return ["between", field, p.from, p.to];
      return p.from ? [">=", field, p.from] : ["<=", field, p.to];
    case "current":
      return ["time-interval", field, "current", p.unit];
    case "relative":
      return [
        "time-interval",
        field,
        p.dir === "past" ? -p.n : p.n,
        p.unit,
        ...(p.includeCurrent ? [{ "include-current": true }] : []),
      ];
  }
}

/** Category filter (one or more values). */
export function categoryClause(field: unknown, values: string[]): Clause {
  return ["=", field, ...values];
}
