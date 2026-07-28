import { describe, expect, it } from "vitest";
import type { AskResponse } from "@dima/contracts";

import { catalogEntries, catalogSummary } from "./catalog";
import { composeDashboard } from "./compose";

const base = (over: Partial<AskResponse>): AskResponse => ({
  question: "",
  sql: "SELECT …",
  planned_sql: null,
  result: null,
  source: "cube",
  cube_query: null,
  note: null,
  view_hint: null,
  contract_id: null,
  ...over,
});

const scalar = base({
  question: "Toplam üretim",
  result: { columns: ["uretim_kg"], rows: [{ uretim_kg: 184_320 }], row_count: 1 },
});

const trend = base({
  question: "Aylara göre üretim",
  result: {
    columns: ["ay", "uretim_kg"],
    rows: [
      { ay: "2026-05", uretim_kg: 165_700 },
      { ay: "2026-06", uretim_kg: 179_800 },
      { ay: "2026-07", uretim_kg: 184_320 },
    ],
    row_count: 3,
  },
  interpretation: { summary: "Üretim üç ayda %11 arttı." },
});

const breakdown = base({
  question: "Departmana göre duruş",
  result: {
    columns: ["departman", "durus_dk"],
    rows: [
      { departman: "Örme", durus_dk: 428 },
      { departman: "Boyahane", durus_dk: 613 },
    ],
    row_count: 2,
  },
});

describe("deterministik pano düzenleyici", () => {
  it("KPI'yı üste, grafiği ortaya, yorumu grafiğin altına koyar", () => {
    const out = composeDashboard(catalogEntries([breakdown, trend, scalar]));

    expect(out.startsWith("root = Dashboard(")).toBe(true);
    // KPI şeridi grafiklerden önce gelmeli — BI okuma sırası.
    expect(out.indexOf("ozet")).toBeLessThan(out.indexOf("Section"));
    // Yorum, ait olduğu grafikle AYNI bölümde olmalı; kopuk durmamalı.
    expect(out).toMatch(/Section\("Aylara göre üretim", \[c\d+, y\d+\]\)/);
    expect(out).toContain("InsightNote(");
  });

  it("yorumu olmayan grafiğe InsightNote koymaz", () => {
    const out = composeDashboard(catalogEntries([breakdown]));
    expect(out).not.toContain("InsightNote");
  });

  it("katalog kimlikleri kronolojik — sohbet en yeniyi başta tutar", () => {
    // store'da en yeni önce; panoda soru sırası okunmalı.
    const entries = catalogEntries([breakdown, trend, scalar]);
    expect(entries.map((e) => e.response.question)).toEqual([
      "Toplam üretim",
      "Aylara göre üretim",
      "Departmana göre duruş",
    ]);
  });

  it("boş sohbette boş dize döner — boş pano çizilmez", () => {
    expect(composeDashboard(catalogEntries([]))).toBe("");
    expect(composeDashboard(catalogEntries([base({ question: "yanıt yok" })]))).toBe("");
  });

  it("başlıktaki tırnağı kaçırır — üretilen dil bozulmamalı", () => {
    const q = base({
      question: 'Müşteri "A" cirosu',
      result: {
        columns: ["ay", "ciro"],
        rows: [
          { ay: "01", ciro: 1 },
          { ay: "02", ciro: 2 },
        ],
        row_count: 2,
      },
    });
    expect(composeDashboard(catalogEntries([q]))).toContain('Müşteri \\"A\\" cirosu');
  });

  it("katalog özeti satır DEĞERİ sızdırmaz — yalnız şekil", () => {
    const summary = catalogSummary(catalogEntries([trend, breakdown]));

    // Kardinalite ve ad var…
    expect(summary).toContain("boyut: ay(3)");
    expect(summary).toContain("ölçü: uretim_kg");
    // …ama hiçbir satır değeri yok. Bu testin asıl işi bu.
    expect(summary).not.toContain("184320");
    expect(summary).not.toContain("Boyahane");
    expect(summary).not.toContain("2026-07");
  });
});
