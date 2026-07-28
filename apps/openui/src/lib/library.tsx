import { createLibrary, defineComponent } from "@openuidev/react-lang";
import { z } from "zod/v4";

import { useResult } from "./catalog";
import { Chart } from "@/components/tiles/chart";
import { Kpi } from "@/components/tiles/kpi";
import { Table } from "@/components/tiles/table";
import { Insight, Missing, Provenance } from "@/components/tiles/shared";

/**
 * dima PANO VOKABÜLERİ.
 *
 * TASARIM KURALI — bileşenlerin propları VERİ DEĞİL, REFERANSTIR:
 *
 *   ⛔ ChartTile(data: [{ay: "Ocak", ciro: 1240000}, …])   model sayı yazıyor
 *   ✅ ChartTile("q2", "bar", "toplam_ciro")               model yalnız kompoze ediyor
 *
 * `resultId`, backend'in GERÇEKTEN çalıştırdığı bir sorgunun kimliği (bkz.
 * catalog.tsx). Model o sonucun yalnız şeklini görür; satırları göremez,
 * yazamaz, değiştiremez.
 *
 * SERBEST METİN BİLEŞENİ YOK — bilinçli. Model düzyazı yazabiliyorsa veri
 * hakkında yanlış iddiada bulunabilir. Yorum metni yalnız backend'in
 * deterministik `interpretation`'ından gelir (InsightNote). Modele bırakılan
 * tek metin BAŞLIK: "Satış Özeti" bir kompozisyon kararıdır, veri hakkında
 * bir iddia değil. Sınır tam orada.
 *
 * OpenUI Lang pozisyonel argüman kullanır ve sıra Zod anahtar sırasından
 * gelir — zorunlu/ayırt edici proplar önce, opsiyoneller sonda.
 */

const RESULT_ID = z
  .string()
  .describe("Katalogdaki sonuç kimliği (ör. \"q1\"). Yalnız katalogda LİSTELENEN kimlikler kullanılabilir.");

// --- Yerleşim ---------------------------------------------------------------

const Dashboard = defineComponent({
  name: "Dashboard",
  description:
    "Panonun kökü. Başlık ve sıralı bloklar (Section, Grid veya tek karo) alır. Her panoda tam olarak bir tane bulunur.",
  props: z.object({
    title: z.string().describe("Panonun Türkçe başlığı."),
    blocks: z.array(z.unknown()).describe("Sırayla dizilecek bloklar."),
  }),
  component: ({ props, renderNode }) => (
    <section className="dima-dashboard">
      <h1>{props.title}</h1>
      {props.blocks.map((b, i) => (
        <div key={i}>{renderNode(b)}</div>
      ))}
    </section>
  ),
});

const Section = defineComponent({
  name: "Section",
  description:
    "Başlıklı bir grup. İlgili karoları bir arada tutmak için kullanılır (ör. \"Satış\", \"Üretim\").",
  props: z.object({
    title: z.string().describe("Bölüm başlığı, Türkçe."),
    blocks: z.array(z.unknown()).describe("Bölümdeki bloklar."),
  }),
  component: ({ props, renderNode }) => (
    <section className="dima-section">
      <h2>{props.title}</h2>
      {props.blocks.map((b, i) => (
        <div key={i}>{renderNode(b)}</div>
      ))}
    </section>
  ),
});

const Grid = defineComponent({
  name: "Grid",
  description:
    "Karoları yan yana dizer. KPI karolarını üst sıraya almak veya grafik ile tabloyu yan yana koymak için kullanılır.",
  props: z.object({
    blocks: z.array(z.unknown()).describe("Yan yana dizilecek karolar."),
    columns: z
      .enum(["2", "3", "4"])
      .optional()
      .describe("Kolon sayısı. Varsayılan 2. KPI satırları için 3 veya 4 uygundur."),
  }),
  component: ({ props, renderNode }) => (
    <div
      className="dima-grid"
      style={{ gridTemplateColumns: `repeat(${props.columns ?? "2"}, minmax(0, 1fr))` }}
    >
      {props.blocks.map((b, i) => (
        <div key={i}>{renderNode(b)}</div>
      ))}
    </div>
  ),
});

// --- Karolar ----------------------------------------------------------------

const KpiTile = defineComponent({
  name: "KpiTile",
  description:
    "Tek bir sayısal göstergeyi büyük puntoyla gösterir. Katalogda \"KPI:\" ile işaretlenmiş sonuçlar veya tek satırlık sonuçlar için kullanılır.",
  props: z.object({ resultId: RESULT_ID }),
  component: ({ props }) => <TileHost resultId={props.resultId} render={(r) => <Kpi response={r} />} />,
});

const ChartTile = defineComponent({
  name: "ChartTile",
  description:
    "Sonucu grafik olarak gösterir. Grafik türü verilmezse dima veri şeklinden kendisi seçer — ÖNERİLEN bu, katalogdaki \"önerilen\" değeri zaten en uygun türdür. Türü yalnız kullanıcı açıkça istediyse ver.",
  props: z.object({
    resultId: RESULT_ID,
    kind: z
      .enum(["bar", "line", "area", "pie", "bar-stacked", "bar-h", "scatter", "radial", "radar"])
      .optional()
      .describe("Grafik türü. Boş bırakılırsa veri şeklinden otomatik seçilir."),
    measure: z
      .string()
      .optional()
      .describe("Gösterilecek ölçü adı. Katalogda o sonuç için listelenen ölçülerden biri olmalı."),
  }),
  component: ({ props }) => (
    <TileHost
      resultId={props.resultId}
      render={(r) => <Chart response={r} kind={props.kind} measure={props.measure} />}
    />
  ),
});

const TableTile = defineComponent({
  name: "TableTile",
  description:
    "Sonucu tablo olarak gösterir. Satır sayısı fazla olduğunda veya kesin değerler gerektiğinde grafiğe tercih edilir.",
  props: z.object({
    resultId: RESULT_ID,
    limit: z
      .number()
      .int()
      .positive()
      .optional()
      .describe("Gösterilecek en fazla satır. Varsayılan 10."),
  }),
  component: ({ props }) => (
    <TileHost resultId={props.resultId} render={(r) => <Table response={r} limit={props.limit} />} />
  ),
});

const InsightNote = defineComponent({
  name: "InsightNote",
  description:
    "Sonucun dima tarafından ÜRETİLMİŞ deterministik yorumunu gösterir. Metni sen yazmazsın — yalnız hangi sonucun yorumunun gösterileceğini seçersin. Katalogda \"yorum var\" yazmayan sonuçlar için kullanma.",
  props: z.object({ resultId: RESULT_ID }),
  component: ({ props }) => (
    <TileHost resultId={props.resultId} render={(r) => <Insight response={r} />} />
  ),
});

/**
 * Her karonun ortak kabuğu: kimliği katalogda çözer, bulunamazsa AÇIKÇA hata
 * gösterir.
 *
 * Bulunamayan kimlikte sessizce boş dönmek ya da örnek veri uydurmak en kötü
 * davranış olurdu: kullanıcı gerçek bir pano gördüğünü sanır. Eksik olan
 * görünür olmalı.
 */
function TileHost({
  resultId,
  render,
}: {
  resultId: string;
  render: (response: NonNullable<ReturnType<typeof useResult>>) => React.ReactNode;
}) {
  const response = useResult(resultId);
  if (!response) return <Missing resultId={resultId} />;
  return (
    <article className="dima-tile">
      {render(response)}
      <Provenance response={response} />
    </article>
  );
}

export const library = createLibrary({
  root: "Dashboard",
  components: [Dashboard, Section, Grid, KpiTile, ChartTile, TableTile, InsightNote],
});

/**
 * CLI istem seçeneklerini KÜTÜPHANE MODÜLÜNDEN okur (`promptOptions`, `options`
 * ya da `*PromptOptions` ile biten bir dışa aktarım arar). Ayrı dosyada
 * bırakılırsa sessizce yok sayılır ve üretilen istem dima kurallarını
 * içermez — bu sessiz başarısızlık, `scripts/genui-prompt.mjs` tarafından
 * denetlenir.
 */
export { promptOptions } from "./prompt-options";

export default library;
