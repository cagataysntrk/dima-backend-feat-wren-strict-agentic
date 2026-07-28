"use client";

import { createLibrary, defineComponent } from "@openuidev/react-lang";
import { z } from "zod/v4";

import { ChartTileView, InsightTileView, KpiTileView, TableTileView } from "./tiles";

/**
 * dima PANO VOKABÜLERİ — web bağlaması.
 *
 * Prop sözleşmeleri VERİ DEĞİL, REFERANSTIR:
 *
 *   ⛔ ChartTile(data: [{ay: "Ocak", ciro: 1240000}, …])   üreten taraf sayı yazıyor
 *   ✅ ChartTile("q2", "bar", "toplam_ciro")               yalnız kompozisyon
 *
 * SERBEST METİN BİLEŞENİ YOK — bilinçli. Düzyazı yazabilen bir üretici veri
 * hakkında yanlış iddiada bulunabilir. Yorum metni yalnız backend'in
 * deterministik `interpretation`'ından gelir. Üreten tarafa bırakılan tek metin
 * BAŞLIK: "Satış Özeti" bir kompozisyon kararı, veri hakkında iddia değil.
 *
 * OpenUI Lang pozisyonel argüman kullanır; sıra Zod anahtar sırasından gelir —
 * zorunlu/ayırt edici proplar önce, opsiyoneller sonda.
 */

const RESULT_ID = z
  .string()
  .describe('Bu sohbetteki sonucun kimliği (ör. "q1"). Yalnız katalogdakiler.');

const Dashboard = defineComponent({
  name: "Dashboard",
  description: "Panonun kökü: başlık + sıralı bloklar. Her panoda tam olarak bir tane.",
  props: z.object({
    title: z.string().describe("Panonun Türkçe başlığı."),
    blocks: z.array(z.unknown()).describe("Sırayla dizilecek bloklar."),
  }),
  component: ({ props, renderNode }) => (
    <section className="space-y-4">
      <h2 className="text-sm font-semibold text-foreground">{props.title}</h2>
      {props.blocks.map((b, i) => (
        <div key={i}>{renderNode(b)}</div>
      ))}
    </section>
  ),
});

const Section = defineComponent({
  name: "Section",
  description: "Başlıklı grup — ilgili karoları bir arada tutar.",
  props: z.object({
    title: z.string().describe("Bölüm başlığı, Türkçe."),
    blocks: z.array(z.unknown()).describe("Bölümdeki bloklar."),
  }),
  component: ({ props, renderNode }) => (
    <section className="space-y-2">
      <h3 className="text-xs font-medium text-muted-foreground">{props.title}</h3>
      {props.blocks.map((b, i) => (
        <div key={i}>{renderNode(b)}</div>
      ))}
    </section>
  ),
});

const Grid = defineComponent({
  name: "Grid",
  description:
    "Karoları yan yana dizer. KPI'ları üst şeride almak veya grafik ile tabloyu yan yana koymak için.",
  props: z.object({
    blocks: z.array(z.unknown()).describe("Yan yana dizilecek karolar."),
    columns: z
      .enum(["2", "3", "4"])
      .optional()
      .describe("Kolon sayısı, varsayılan 2. KPI şeritleri için 3-4 uygundur."),
  }),
  component: ({ props, renderNode }) => (
    // Sağ panel dar olabilir: sabit kolon yerine minimum genişlikli auto-fit,
    // böylece panel daraldığında karolar sıkışmak yerine alt satıra iner.
    <div
      className="grid gap-2"
      style={{
        gridTemplateColumns: `repeat(auto-fit, minmax(${
          { "2": 180, "3": 140, "4": 120 }[props.columns ?? "2"]
        }px, 1fr))`,
      }}
    >
      {props.blocks.map((b, i) => (
        <div key={i} className="min-w-0">
          {renderNode(b)}
        </div>
      ))}
    </div>
  ),
});

const KpiTile = defineComponent({
  name: "KpiTile",
  description: "Tek sayısal göstergeyi büyük puntoyla gösterir. KPI ve tek satırlık sonuçlar için.",
  props: z.object({ resultId: RESULT_ID }),
  component: ({ props }) => <KpiTileView resultId={props.resultId} />,
});

const ChartTile = defineComponent({
  name: "ChartTile",
  description:
    "Sonucu grafik olarak gösterir. Tür verilmezse dima veri şeklinden kendisi seçer — önerilen bu.",
  props: z.object({
    resultId: RESULT_ID,
    kind: z
      .enum(["bar", "line", "area", "pie", "bar-stacked", "bar-h", "scatter", "radial", "radar"])
      .optional()
      .describe("Grafik türü. Boş bırakılırsa veri şeklinden otomatik seçilir."),
    measure: z.string().optional().describe("Gösterilecek ölçü adı."),
  }),
  component: ({ props }) => (
    <ChartTileView resultId={props.resultId} kind={props.kind} measure={props.measure} />
  ),
});

const TableTile = defineComponent({
  name: "TableTile",
  description: "Sonucu tablo olarak gösterir. Kesin değerler veya çok satır gerektiğinde.",
  props: z.object({
    resultId: RESULT_ID,
    limit: z.number().int().positive().optional().describe("En fazla satır, varsayılan 10."),
  }),
  component: ({ props }) => <TableTileView resultId={props.resultId} limit={props.limit} />,
});

const InsightNote = defineComponent({
  name: "InsightNote",
  description:
    "Sonucun dima tarafından üretilmiş DETERMİNİSTİK yorumunu gösterir. Metni sen yazmazsın.",
  props: z.object({ resultId: RESULT_ID }),
  component: ({ props }) => <InsightTileView resultId={props.resultId} />,
});

export const dashboardLibrary = createLibrary({
  root: "Dashboard",
  components: [Dashboard, Section, Grid, KpiTile, ChartTile, TableTile, InsightNote],
});
