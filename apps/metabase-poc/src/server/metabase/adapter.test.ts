import { describe, expect, it } from "vitest";
import { columnRefs, toQueryResult, type EngineDataset } from "./adapter";
import { GatewayError } from "./errors";

// Shapes recorded from the engine (v0.58.34): POST /api/card/:id/query.
const categorical: EngineDataset = {
  status: "completed",
  row_count: 2,
  data: {
    cols: [
      { name: "makine", display_name: "Makine", base_type: "type/Text", field_ref: ["field", 94, null] },
      { name: "oee_yuzde", display_name: "OEE (%)", base_type: "type/Float", field_ref: ["aggregation", 0] },
    ],
    rows: [
      ["RAM-1", 56.15],
      ["SANTEX", 61.2],
    ],
  },
};

const monthly: EngineDataset = {
  status: "completed",
  row_count: 1,
  data: {
    cols: [
      { name: "tarih", base_type: "type/Date", field_ref: ["field", 93, { "temporal-unit": "month" }] },
      { name: "uretim_kg", base_type: "type/Float", field_ref: ["aggregation", 0] },
    ],
    rows: [["2024-01-01T00:00:00+03:00", 233838.9]],
  },
};

describe("toQueryResult", () => {
  it("maps column-major engine rows to the dima-backend QueryResult contract", () => {
    expect(toQueryResult(categorical)).toEqual({
      columns: ["makine", "oee_yuzde"],
      rows: [
        { makine: "RAM-1", oee_yuzde: 56.15 },
        { makine: "SANTEX", oee_yuzde: 61.2 },
      ],
      row_count: 2,
    });
  });

  it("trims midnight timestamps of date buckets to YYYY-MM-DD", () => {
    expect(toQueryResult(monthly).rows[0].tarih).toBe("2024-01-01");
  });

  it("keeps real timestamps and non-date strings untouched", () => {
    const ds: EngineDataset = {
      data: {
        cols: [
          { name: "ts", base_type: "type/DateTime" },
          { name: "code", base_type: "type/Text" },
        ],
        rows: [["2024-01-01T13:45:00+03:00", "2024-01-01T00:00:00Z"]],
      },
    };
    expect(toQueryResult(ds).rows[0]).toEqual({ ts: "2024-01-01T13:45:00+03:00", code: "2024-01-01T00:00:00Z" });
  });

  it("suffixes duplicate column names so no value is lost", () => {
    const ds: EngineDataset = {
      data: { cols: [{ name: "id" }, { name: "id" }], rows: [[1, 2]] },
    };
    expect(toQueryResult(ds)).toMatchObject({ columns: ["id", "id_2"], rows: [{ id: 1, id_2: 2 }] });
  });

  it("drops engine-internal columns such as the upload row id", () => {
    const ds: EngineDataset = {
      data: { cols: [{ name: "_mb_row_id" }, { name: "urun" }, { name: "adet" }], rows: [[1, "A", 3]] },
    };
    expect(toQueryResult(ds)).toEqual({ columns: ["urun", "adet"], rows: [{ urun: "A", adet: 3 }], row_count: 1 });
  });

  it("turns a failed query into a public error without engine wording", () => {
    const failed: EngineDataset = {
      status: "failed",
      error: 'ERROR: permission denied for schema tenant_tenant2\n  Position: 133 (metabase.driver.sql-jdbc)',
    };
    try {
      toQueryResult(failed);
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(GatewayError);
      expect((e as GatewayError).status).toBe(403);
      expect((e as GatewayError).publicMessage).not.toMatch(/metabase|tenant_tenant2/i);
    }
  });
});

describe("columnRefs", () => {
  it("indexes field refs by output column name (used for drill-down)", () => {
    expect(columnRefs(categorical).get("makine")).toEqual(["field", 94, null]);
  });
});
