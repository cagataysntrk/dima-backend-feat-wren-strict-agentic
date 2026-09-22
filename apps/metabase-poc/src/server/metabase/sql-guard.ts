// SELECT-only guard for the ad-hoc SQL runner. Pure, unit-tested.
//
// Defence in depth — this is layer 1. Layer 2 is the tenant's Postgres role,
// which has SELECT on its own schema only (writes/other schemas fail there too).

const FORBIDDEN =
  /\b(insert|update|delete|merge|upsert|drop|alter|create|truncate|grant|revoke|copy|call|do|vacuum|analyze|reindex|cluster|set|reset|lock|listen|notify|unlisten|refresh|comment|security|execute|prepare|deallocate|discard|load|import|into)\b/i;

/** Strip comments and quoted literals/identifiers so keywords inside them don't count. */
function stripNoise(sql: string): string {
  return sql
    .replace(/--[^\n]*/g, " ")
    .replace(/\/\*[\s\S]*?\*\//g, " ")
    .replace(/\$([A-Za-z_]*)\$[\s\S]*?\$\1\$/g, "''")
    .replace(/'(?:[^']|'')*'/g, "''")
    .replace(/"(?:[^"]|"")*"/g, '""');
}

export type SqlCheck = { ok: true; sql: string } | { ok: false; reason: string };

export function checkSelectOnly(input: string): SqlCheck {
  const sql = input.trim().replace(/;\s*$/, "");
  if (!sql) return { ok: false, reason: "Sorgu boş." };
  if (sql.length > 20_000) return { ok: false, reason: "Sorgu çok uzun." };
  const bare = stripNoise(sql);
  if (bare.includes(";")) return { ok: false, reason: "Tek bir sorgu çalıştırılabilir." };
  if (!/^\s*(select|with)\b/i.test(bare)) {
    return { ok: false, reason: "Yalnızca SELECT sorguları çalıştırılabilir." };
  }
  const bad = FORBIDDEN.exec(bare);
  if (bad) return { ok: false, reason: `İzin verilmeyen ifade: ${bad[1].toUpperCase()}` };
  return { ok: true, sql };
}
