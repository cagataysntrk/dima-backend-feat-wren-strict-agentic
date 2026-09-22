import { describe, expect, it } from "vitest";
import { describeSchema, summarizeForModel, systemPrompt } from "./prompt";

describe("chat prompt", () => {
  it("lists tables sorted and schema-qualified, so the prompt prefix is stable", () => {
    const text = describeSchema([
      { schema: "tenant_x", name: "b", columns: [{ name: "id", type: "int4" }] },
      { schema: "tenant_x", name: "a", columns: [{ name: "tarih", type: "date" }, { name: "kg", type: "float8" }] },
    ]);
    expect(text).toBe("tenant_x.a(tarih date, kg float8)\ntenant_x.b(id int4)");
  });

  it("names the company and embeds the schema; never names the engine", () => {
    const p = systemPrompt("Demo Boyahane", "tenant_x.a(id int4)");
    expect(p).toContain("Demo Boyahane");
    expect(p).toContain("tenant_x.a(id int4)");
    expect(p).not.toMatch(/metabase/i);
  });

  it("bounds what the model sees from large results", () => {
    const rows = Array.from({ length: 100 }, (_, i) => ({ n: i }));
    const out = JSON.parse(summarizeForModel({ columns: ["n"], rows, row_count: 100 }));
    expect(out.rows).toHaveLength(40);
    expect(out.row_count).toBe(100);
    expect(out.note).toContain("40");
  });
});
