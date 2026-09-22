// Engine → Dima contract adapter. Pure (no I/O), unit-tested.
//
// The engine returns column-major metadata + row arrays:
//   { data: { cols: [{name, display_name, base_type, field_ref}], rows: [[…]] }, row_count }
// Dima UI components consume the dima-backend contract:
//   QueryResult { columns: string[], rows: Record<string, unknown>[], row_count }
// Keeping the contract identical means ResultView/Chart work unchanged.

import type { QueryResult } from "@dima/contracts";
import { fromQueryFailure } from "./errors";

export interface EngineCol {
  name: string;
  display_name?: string;
  base_type?: string;
  field_ref?: unknown;
}

export interface EngineDataset {
  status?: string;
  error?: unknown;
  row_count?: number;
  data?: { cols: EngineCol[]; rows: unknown[][] };
}

// "2024-01-01T00:00:00+03:00" → "2024-01-01" (month/day buckets). Real timestamps keep their time.
const INTERNAL_COL = /^_mb_/i;

const MIDNIGHT = /^(\d{4}-\d{2}-\d{2})T00:00:00(?:\.000)?(?:Z|[+-]\d{2}:\d{2})?$/;

function normalize(v: unknown, col: EngineCol): unknown {
  if (typeof v === "string" && col.base_type?.startsWith("type/Date")) {
    const m = MIDNIGHT.exec(v);
    if (m) return m[1];
  }
  return v;
}

/** Convert an engine dataset to a Dima QueryResult, throwing a public error on query failure. */
export function toQueryResult(ds: EngineDataset): QueryResult {
  if (ds.status && ds.status !== "completed") throw fromQueryFailure(ds.error);
  if (!ds.data) throw fromQueryFailure(ds.error ?? "no data");
  // Engine-internal columns (e.g. the row id added to uploaded tables) are not user data.
  const keep = ds.data.cols.flatMap((c, i) => (INTERNAL_COL.test(c.name) ? [] : [i]));
  const cols = keep.map((i) => ds.data!.cols[i]);
  // Column names must be unique object keys; suffix duplicates (e.g. joined "id").
  const seen = new Map<string, number>();
  const names = cols.map((c) => {
    const n = seen.get(c.name) ?? 0;
    seen.set(c.name, n + 1);
    return n === 0 ? c.name : `${c.name}_${n + 1}`;
  });
  const rows = ds.data.rows.map((r) => {
    const o: Record<string, unknown> = {};
    names.forEach((name, j) => {
      o[name] = normalize(r[keep[j]], cols[j]);
    });
    return o;
  });
  return { columns: names, rows, row_count: ds.row_count ?? rows.length };
}

/** Column metadata keyed by output column name — used to build drill-down filters. */
export function columnRefs(ds: EngineDataset): Map<string, unknown> {
  return new Map((ds.data?.cols ?? []).map((c) => [c.name, c.field_ref]));
}
