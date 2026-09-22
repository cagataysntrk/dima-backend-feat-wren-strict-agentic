import { describe, expect, it } from "vitest";
import { flow, widthOf } from "./layout";

describe("flow", () => {
  it("packs KPIs four to a row, then halves two to a row", () => {
    const placed = flow(["kpi", "kpi", "half", "half", "full", "half"]);
    expect(placed).toEqual([
      { row: 0, col: 0, size_x: 6, size_y: 3 },
      { row: 0, col: 6, size_x: 6, size_y: 3 },
      { row: 0, col: 12, size_x: 12, size_y: 6 },
      { row: 6, col: 0, size_x: 12, size_y: 6 },
      { row: 12, col: 0, size_x: 24, size_y: 6 },
      { row: 18, col: 0, size_x: 12, size_y: 6 },
    ]);
  });

  it("never overlaps: each widget starts at or after the previous row end", () => {
    const placed = flow(["half", "full", "kpi", "half", "half", "half"]);
    for (let i = 1; i < placed.length; i++) {
      const prev = placed[i - 1];
      const cur = placed[i];
      const sameRow = cur.row === prev.row;
      expect(sameRow ? cur.col >= prev.col + prev.size_x : cur.row >= prev.row).toBe(true);
    }
  });
});

describe("widthOf", () => {
  it("maps engine sizes and displays to our three widths", () => {
    expect(widthOf(6, "scalar")).toBe("kpi");
    expect(widthOf(12, "bar")).toBe("half");
    expect(widthOf(24, "line")).toBe("full");
  });
});
