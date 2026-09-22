import { describe, expect, it } from "vitest";
import { describeDateFilter, isDateFilter, parseDateFilter } from "./date-filter";

describe("parseDateFilter", () => {
  it.each([
    ["2025-01-01~2025-03-31", { kind: "range", from: "2025-01-01", to: "2025-03-31" }],
    ["2025-01-01~", { kind: "range", from: "2025-01-01", to: null }],
    ["~2024-12-31", { kind: "range", from: null, to: "2024-12-31" }],
    ["past3months~", { kind: "relative", dir: "past", n: 3, unit: "month", includeCurrent: true }],
    ["next7days", { kind: "relative", dir: "next", n: 7, unit: "day", includeCurrent: false }],
    ["thisyear", { kind: "current", unit: "year" }],
    ["2024-02", { kind: "range", from: "2024-02-01", to: "2024-02-29" }],
    ["Q3-2025", { kind: "range", from: "2025-07-01", to: "2025-09-30" }],
    ["2025-02-10", { kind: "day", day: "2025-02-10" }],
  ])("parses %s", (value, expected) => {
    expect(parseDateFilter(value)).toEqual(expected);
  });

  it.each(["", "~", "yesterday", "2025-13", "Q5-2025", "past0days", "2025-03-31~2025-01-01", "2025-02-30x", "drop table"])(
    "rejects %s",
    (value) => {
      expect(isDateFilter(value)).toBe(false);
    },
  );
});

describe("describeDateFilter", () => {
  it("labels presets and relative values in Turkish", () => {
    expect(describeDateFilter("past3months~")).toBe("Son 3 ay");
    expect(describeDateFilter("past2weeks")).toBe("Son 2 hafta");
    expect(describeDateFilter("thisquarter")).toBe("Bu çeyrek");
  });

  it("labels explicit ranges with dates", () => {
    expect(describeDateFilter("2025-01-01~2025-03-31")).toMatch(/2025.*–.*2025/);
    expect(describeDateFilter("2025-01-01~")).toMatch(/sonrası$/);
  });
});
