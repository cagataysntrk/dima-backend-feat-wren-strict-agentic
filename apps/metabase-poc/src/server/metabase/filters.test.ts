import { describe, expect, it } from "vitest";
import { categoryClause, dateClause } from "./filters";

const F = ["field", 93, null];

describe("dateClause", () => {
  it.each([
    ["2025-01-01~2025-03-31", ["between", F, "2025-01-01", "2025-03-31"]],
    ["2025-01-01~", [">=", F, "2025-01-01"]],
    ["~2024-12-31", ["<=", F, "2024-12-31"]],
    ["2025-02-10", ["=", F, "2025-02-10"]],
    ["2025-03", ["between", F, "2025-03-01", "2025-03-31"]],
    ["thisyear", ["time-interval", F, "current", "year"]],
    ["past3months", ["time-interval", F, -3, "month"]],
    ["past3months~", ["time-interval", F, -3, "month", { "include-current": true }]],
    ["next7days", ["time-interval", F, 7, "day"]],
  ])("%s", (value, expected) => {
    expect(dateClause(F, value)).toEqual(expected);
  });

  it("returns null for invalid values", () => {
    expect(dateClause(F, "yesterday")).toBeNull();
  });
});

describe("categoryClause", () => {
  it("matches any of the selected values", () => {
    expect(categoryClause(F, ["RAM-1", "RAM-2"])).toEqual(["=", F, "RAM-1", "RAM-2"]);
  });
});
