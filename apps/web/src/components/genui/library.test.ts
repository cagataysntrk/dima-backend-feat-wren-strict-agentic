import { describe, expect, it } from "vitest";
import { createParser } from "@openuidev/lang-core";
import type { AskResponse } from "@dima/contracts";
import { catalogEntries, composeDashboard } from "@dima/genui";

import { dashboardLibrary } from "./library";
import { resolveKind } from "./tiles";

/**
 * ENTEGRASYON TESTİ — LLM ÇAĞRISI YOK.
 *
 * Düzenleyici `@dima/genui`'de, vokabüler burada; ikisi ayrı paketlerde yazıldı
 * ve birbirini yalnız ÜRETİLEN METİN üzerinden tanıyor. Bu test o bağın
 * gerçekten tuttuğunu kanıtlıyor: düzenleyicinin ürettiği OpenUI Lang,
 * kütüphanenin şemasına karşı hatasız ayrışıyor mu?
 *
 * Bu bağ sessizce kopabilir — düzenleyici `Grid(..., "5")` üretse ya da
 * bileşen adı değişse, tip sistemi hiçbir şey söylemez (arada dize var).
 * Yakalayacak tek şey bu test.
 */

const parser = () => createParser(dashboardLibrary.toJSONSchema(), "Dashboard");

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
      { departman: "Konfeksiyon", durus_dk: 297 },
    ],
    row_count: 3,
  },
});

describe("pano vokabüleri ↔ deterministik düzenleyici", () => {
  it("düzenleyicinin ürettiği pano kütüphaneye karşı hatasız ayrışır", () => {
    const source = composeDashboard(catalogEntries([breakdown, trend, scalar]));
    const result = parser().parse(source);

    expect(result.meta.errors).toEqual([]);
    expect(result.meta.unresolved).toEqual([]);
    // Tanımlanıp köke bağlanmayan karo kalmamalı — sessizce kaybolan karo olmaz.
    expect(result.meta.orphaned).toEqual([]);
    expect(result.root?.typeName).toBe("Dashboard");
  });

  it("tek sonuçlu sohbette de geçerli çıktı verir", () => {
    const source = composeDashboard(catalogEntries([trend]));
    expect(parser().parse(source).meta.errors).toEqual([]);
  });

  it("kütüphanede olmayan bileşeni reddeder", () => {
    const bad = `root = Dashboard("X", [c])\nc = LineChart("q1")`;
    expect(parser().parse(bad).meta.errors.length).toBeGreaterThan(0);
  });

  it("zorunlu argümanı eksik karoyu reddeder", () => {
    const bad = `root = Dashboard("X", [k])\nk = KpiTile()`;
    expect(parser().parse(bad).meta.errors.length).toBeGreaterThan(0);
  });

  /**
   * Parser enum ÜYELİĞİNİ denetlemiyor: üretilen spec yapısal tip değil, imza
   * metni taşıyor. Zorlama bu yüzden renderer'da (resolveKind) — tanınmayan
   * tür sessizce sütuna düşmez, analyze()'ın deterministik seçimine döner.
   */
  it("tanınmayan grafik türü deterministik seçime düşer", () => {
    expect(parser().parse(`root = Dashboard("X", [c])\nc = ChartTile("q1", "sankey")`).meta.errors)
      .toEqual([]);
    expect(resolveKind("sankey", "line")).toBe("line");
    expect(resolveKind("pie", "bar")).toBe("pie");
    expect(resolveKind(undefined, "bar")).toBe("bar");
  });
});
