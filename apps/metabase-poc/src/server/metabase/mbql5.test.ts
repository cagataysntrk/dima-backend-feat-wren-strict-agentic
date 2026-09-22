import { describe, expect, it } from "vitest";
import { field5, periodRange, toMbql5 } from "./mbql5";

const seq = () => {
  let i = 0;
  return () => `u${++i}`;
};

describe("toMbql5", () => {
  it("converts comparison clauses and their field refs", () => {
    expect(toMbql5(["between", ["field", 93, null], "2026-03-01", "2026-03-31"], seq())).toEqual([
      "between",
      { "lib/uuid": "u1" },
      ["field", { "lib/uuid": "u2" }, 93],
      "2026-03-01",
      "2026-03-31",
    ]);
    expect(toMbql5(["=", ["field", 94, null], "RAM-1", "RAM-2"], seq())).toEqual([
      "=",
      { "lib/uuid": "u1" },
      ["field", { "lib/uuid": "u2" }, 94],
      "RAM-1",
      "RAM-2",
    ]);
  });

  it("moves time-interval options into the clause options map", () => {
    expect(toMbql5(["time-interval", ["field", 93, null], -3, "month", { "include-current": true }], seq())).toEqual([
      "time-interval",
      { "include-current": true, "lib/uuid": "u1" },
      ["field", { "lib/uuid": "u2" }, 93],
      -3,
      "month",
    ]);
  });

  it("keeps field options such as temporal-unit", () => {
    expect(field5(["field", 93, { "temporal-unit": "month" }], seq())).toEqual([
      "field",
      { "temporal-unit": "month", "lib/uuid": "u1" },
      93,
    ]);
  });
});

describe("periodRange", () => {
  it.each([
    ["2026-03-01", "month", ["2026-03-01", "2026-03-31"]],
    ["2024-02-01", "month", ["2024-02-01", "2024-02-29"]],
    ["2025-01-01", "year", ["2025-01-01", "2025-12-31"]],
    ["2025-04-01", "quarter", ["2025-04-01", "2025-06-30"]],
    ["2026-03-02T00:00:00+03:00", "week", ["2026-03-02", "2026-03-08"]],
  ] as const)("%s (%s)", (value, unit, range) => {
    expect(periodRange(value, unit)).toEqual(range);
  });

  it("rejects values that are not dates", () => {
    expect(periodRange("RAM-1", "month")).toBeNull();
  });
});
