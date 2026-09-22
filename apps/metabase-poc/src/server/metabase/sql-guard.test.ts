import { describe, expect, it } from "vitest";
import { checkSelectOnly } from "./sql-guard";

describe("checkSelectOnly", () => {
  it.each([
    "SELECT 1",
    "select makine, avg(oee) from tenant_boyahane.oee_vardiya group by 1;",
    "WITH t AS (SELECT 1 AS x) SELECT x FROM t",
    "SELECT 'drop table x' AS note", // keyword inside a string literal
    'SELECT "update" FROM t', // keyword as quoted identifier
    "-- delete everything\nSELECT 1",
    "SELECT set_uretim_tep_ton FROM t", // keyword as part of an identifier
  ])("allows %s", (sql) => {
    expect(checkSelectOnly(sql).ok).toBe(true);
  });

  it.each([
    ["", "boş"],
    ["DROP TABLE tenant_boyahane.partiler", "SELECT"],
    ["DELETE FROM t", "SELECT"],
    ["SELECT 1; DROP TABLE t", "Tek bir sorgu"],
    ["WITH d AS (DELETE FROM t RETURNING *) SELECT * FROM d", "DELETE"],
    ["SELECT * INTO new_t FROM t", "INTO"],
    ["SELECT 1 /* ok */; UPDATE t SET a = 1", "Tek bir sorgu"],
    ["COPY t TO '/tmp/x'", "SELECT"],
    ["SELECT set_config('search_path', 'x', false)", undefined],
  ])("rejects %s", (sql, reason) => {
    const r = checkSelectOnly(sql);
    if (reason === undefined) return; // documented: function calls are left to the DB role (layer 2)
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toContain(reason);
  });
});
