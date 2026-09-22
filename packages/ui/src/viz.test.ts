import { describe, expect, it } from "vitest";
import { funnelSteps, isAdditive, meter, trendSummary, waterfallSteps } from "./viz";

const R = (rows: Record<string, unknown>[]) => ({ columns: Object.keys(rows[0] ?? {}), rows, row_count: rows.length });

describe("trendSummary", () => {
  it("uses the latest period and compares it with the one before (input order does not matter)", () => {
    const t = trendSummary(
      R([
        { ay: "2026-02-01", kg: 120 },
        { ay: "2026-01-01", kg: 100 },
        { ay: "2026-03-01", kg: 90 },
      ]),
      "ay",
      "kg",
    );
    expect(t).toMatchObject({ value: 90, period: "2026-03-01", previous: 120, series: [100, 120, 90] });
    expect(t!.change).toBeCloseTo(-0.25);
  });

  it("has no change for a single period or a zero base", () => {
    expect(trendSummary(R([{ ay: "2026-01-01", kg: 5 }]), "ay", "kg")!.change).toBeNull();
    expect(trendSummary(R([{ ay: "a", kg: 0 }, { ay: "b", kg: 5 }]), "ay", "kg")!.change).toBeNull();
  });

  it("keeps at most the last 12 points for the sparkline", () => {
    const rows = Array.from({ length: 20 }, (_, i) => ({ ay: `2025-${String(i + 1).padStart(2, "0")}`, kg: i }));
    expect(trendSummary(R(rows), "ay", "kg")!.series).toHaveLength(12);
  });
});

describe("meter", () => {
  it("clamps the bar but keeps the real ratio", () => {
    expect(meter(50, 200)).toEqual({ ratio: 0.25, fill: 0.25 });
    expect(meter(300, 200)).toEqual({ ratio: 1.5, fill: 1 });
    expect(meter(10, 0)).toEqual({ ratio: 0, fill: 0 });
  });
});

describe("funnelSteps", () => {
  it("computes share of first and step conversion in query order", () => {
    const s = funnelSteps(R([{ a: "Teklif", n: 200 }, { a: "Sipariş", n: 100 }, { a: "Teslim", n: 80 }]), "a", "n");
    expect(s.map((x) => [x.label, x.ofFirst, x.ofPrevious])).toEqual([
      ["Teklif", 1, 1],
      ["Sipariş", 0.5, 0.5],
      ["Teslim", 0.4, 0.8],
    ]);
  });
});

describe("waterfallSteps", () => {
  it("stacks signed changes on a running total and ends with the total", () => {
    const s = waterfallSteps(R([{ k: "Satış", v: 100 }, { k: "Maliyet", v: -60 }, { k: "Diğer", v: 10 }]), "k", "v");
    expect(s).toEqual([
      { label: "Satış", value: 100, low: 0, high: 100, kind: "up" },
      { label: "Maliyet", value: -60, low: 40, high: 100, kind: "down" },
      { label: "Diğer", value: 10, low: 40, high: 50, kind: "up" },
      { label: "Toplam", value: 50, low: 0, high: 50, kind: "total" },
    ]);
  });
});

describe("isAdditive", () => {
  it("refuses to total ratios and averages", () => {
    expect(isAdditive("toplam_uretim_kg")).toBe(true);
    expect(isAdditive("ciro_tl")).toBe(true);
    expect(isAdditive("oee_yuzde")).toBe(false);
    expect(isAdditive("ortalama_hiz")).toBe(false);
  });
});
