import type { AskResponse } from "@dima/contracts";

import type { CatalogEntry } from "./catalog";

/**
 * TEZGÂH VERİSİ — gerçek değil, gerçek ŞEKİLDE.
 *
 * Bunlar `dima-backend`'in `/ask` ucundan dönen `AskResponse` nesnelerinin
 * birebir yapısında uydurma kayıtlardır. Amaçları vokabüleri ve renderer'ı
 * gerçek tiplerle sınamak; ürüne girmezler.
 *
 * Sayıların uydurma olması burada MEŞRU, çünkü fixture olduklarını hem dosya
 * adı hem bu not söylüyor. Yasak olan, modelin ÜRETİM sırasında sayı
 * uydurmasıydı — o yolu katalog tasarımı kapatıyor (bkz. catalog.tsx).
 */

/**
 * Yanıt tipi, varsayılanı olan alanları ZORUNLU tutuyor — ve bu doğru: sunucu
 * Pydantic varsayılanlarını da serileştirip gönderir, yani `note` gerçek bir
 * yanıtta her zaman vardır (değeri null olsa bile). Fixture'ın da bunu
 * karşılaması gerekiyor; eksik bırakmak gerçek yanıtı taklit etmemek olurdu.
 */
const cube = (over: Partial<AskResponse>): AskResponse => ({
  question: "",
  sql: "SELECT …",
  planned_sql: null,
  result: null,
  source: "cube",
  cube_query: { measures: [], dimensions: [] },
  note: null,
  view_hint: null,
  contract_id: null,
  ...over,
});

export const fixtures: CatalogEntry[] = [
  {
    id: "q1",
    response: cube({
      question: "Bu ay toplam üretim",
      contract_id: "ctr_8841",
      result: {
        columns: ["uretim_kg"],
        rows: [{ uretim_kg: 184_320 }],
        row_count: 1,
      },
    }),
  },
  {
    id: "q2",
    response: cube({
      question: "Ortalama OEE",
      contract_id: "ctr_8842",
      result: {
        columns: ["oee"],
        rows: [{ oee: 0.762 }],
        row_count: 1,
      },
    }),
  },
  {
    id: "q3",
    response: cube({
      question: "Aylara göre üretim",
      contract_id: "ctr_8843",
      result: {
        columns: ["ay", "uretim_kg"],
        rows: [
          { ay: "2026-02", uretim_kg: 151_900 },
          { ay: "2026-03", uretim_kg: 168_400 },
          { ay: "2026-04", uretim_kg: 172_050 },
          { ay: "2026-05", uretim_kg: 165_700 },
          { ay: "2026-06", uretim_kg: 179_800 },
          { ay: "2026-07", uretim_kg: 184_320 },
        ],
        row_count: 6,
      },
      interpretation: {
        summary:
          "Üretim son altı ayda %21 arttı; en yüksek ay Temmuz (184.320 kg), en düşük ay Şubat (151.900 kg).",
        facts: [
          { type: "max", text: "En yüksek: Temmuz 2026" },
          { type: "trend", text: "Kesintisiz artış eğilimi (Mayıs hariç)" },
        ],
      },
    }),
  },
  {
    id: "q4",
    response: cube({
      question: "Departmana göre duruş süresi",
      contract_id: "ctr_8844",
      result: {
        columns: ["departman", "durus_dk"],
        rows: [
          { departman: "Örme", durus_dk: 428 },
          { departman: "Boyahane", durus_dk: 613 },
          { departman: "Konfeksiyon", durus_dk: 297 },
        ],
        row_count: 3,
      },
    }),
  },
  {
    id: "q5",
    response: cube({
      question: "Vardiya bazında fire oranı",
      contract_id: "ctr_8845",
      result: {
        columns: ["vardiya", "departman", "fire_oran"],
        rows: [
          { vardiya: "1. Vardiya", departman: "Örme", fire_oran: 0.021 },
          { vardiya: "1. Vardiya", departman: "Boyahane", fire_oran: 0.038 },
          { vardiya: "2. Vardiya", departman: "Örme", fire_oran: 0.026 },
          { vardiya: "2. Vardiya", departman: "Boyahane", fire_oran: 0.044 },
          { vardiya: "3. Vardiya", departman: "Örme", fire_oran: 0.031 },
          { vardiya: "3. Vardiya", departman: "Boyahane", fire_oran: 0.052 },
        ],
        row_count: 6,
      },
    }),
  },
  {
    id: "q6",
    response: cube({
      question: "Nakit dönüşüm süresi",
      contract_id: "ctr_8846",
      kpi: {
        kpi: "ccc",
        label: "Nakit Dönüşüm Süresi",
        unit: "gün",
        lower_is_better: true,
        value: 47.3,
        components: [
          { key: "dso", label: "Tahsilat Süresi (DSO)", unit: "gün", value: 62.1 },
          { key: "dio", label: "Stok Devir Süresi (DIO)", unit: "gün", value: 38.4 },
          { key: "dpo", label: "Ödeme Süresi (DPO)", unit: "gün", value: 53.2 },
        ],
      },
    }),
  },
];
