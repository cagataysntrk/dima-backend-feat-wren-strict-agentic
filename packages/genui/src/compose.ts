import type { CatalogEntry } from "./catalog";
import { shapeOf } from "./catalog";

/**
 * DETERMİNİSTİK PANO DÜZENLEYİCİ — LLM YOK.
 *
 * Neden bu var: OpenUI Lang'i üretecek model çağrısı `dima-backend`'e ait
 * (sağlayıcı anahtarı Next sürecinde durmaz) ve o uç henüz yok. Renderer'ı
 * yazıp beslenecek veri olmamasını beklemek yerine, kompozisyonu kurallarla
 * üretiyoruz.
 *
 * Bu bir "geçici çözüm" değil, kalıcı bir taban:
 *
 *  - ÖZELLİK BUGÜN ÇALIŞIYOR. Kullanıcı sohbetinden gerçek veriyle pano alıyor.
 *  - MODEL GELDİĞİNDE tek değişen, bu metni kimin ürettiği. Renderer, katalog
 *    ve vokabüler aynen kalıyor.
 *  - GERİ DÜŞÜŞ HATTI. Model erişilemez, kotayı doldurmuş ya da geçersiz çıktı
 *    vermişse pano yine de gelir. Kurumsal bir üründe "LLM çalışmıyor" gerekçesi
 *    kabul edilebilir değil.
 *  - ÖLÇÜT. Modelin ürettiği düzenin bundan daha iyi olup olmadığını
 *    karşılaştıracak bir taban olmadan "generative UI işe yaradı" denemez.
 *
 * Kurallar BI okuma sırasına göre: önce özet göstergeler, sonra eğilim, en sona
 * detay tabloları.
 */

export interface ComposeOptions {
  /** Pano başlığı. Verilmezse sohbetten türetilir. */
  title?: string;
}

export function composeDashboard(entries: CatalogEntry[], options: ComposeOptions = {}): string {
  const shapes = entries.map((e) => ({ entry: e, shape: shapeOf(e) }));

  const kpis = shapes.filter((s) => s.shape.isKpi);
  const charts = shapes.filter((s) => !s.shape.isKpi && s.shape.isChartable);
  // Grafiğe uygun olmayan (ısı haritası, tek boyutlu liste, çok satırlı döküm)
  // her şey tabloya düşer. Yanlış çizmektense tablo doğru davranış.
  const tables = shapes.filter((s) => !s.shape.isKpi && !s.shape.isChartable);

  const title = options.title ?? deriveTitle(shapes.map((s) => s.shape.title));
  const lines: string[] = [];
  const blocks: string[] = [];

  // --- KPI şeridi ----------------------------------------------------------
  if (kpis.length) {
    const ids = kpis.map((s, i) => `k${i + 1}`);
    blocks.push("ozet");
    // 4'ten fazla KPI tek satırda okunmaz; kolonu içeriğe göre seç.
    const columns = Math.min(kpis.length, 4);
    lines.push(`ozet = Grid([${ids.join(", ")}], "${columns}")`);
    kpis.forEach((s, i) => lines.push(`${ids[i]} = KpiTile("${s.shape.id}")`));
  }

  // --- Grafikler + yorumları ----------------------------------------------
  charts.forEach((s, i) => {
    const block = `g${i + 1}`;
    blocks.push(block);
    const chart = `c${i + 1}`;
    // Yorum varsa grafiğin hemen altına: bulgu, grafikten kopuk olmamalı.
    if (s.shape.hasInsight) {
      const note = `y${i + 1}`;
      lines.push(`${block} = Section("${escape(s.shape.title)}", [${chart}, ${note}])`);
      lines.push(`${chart} = ChartTile("${s.shape.id}")`);
      lines.push(`${note} = InsightNote("${s.shape.id}")`);
    } else {
      lines.push(`${block} = Section("${escape(s.shape.title)}", [${chart}])`);
      lines.push(`${chart} = ChartTile("${s.shape.id}")`);
    }
  });

  // --- Detay tabloları -----------------------------------------------------
  if (tables.length) {
    const ids = tables.map((s, i) => `t${i + 1}`);
    blocks.push("detay");
    lines.push(`detay = Section("Detay", [${ids.join(", ")}])`);
    tables.forEach((s, i) =>
      // Satır sınırı: pano özet yüzeyidir, tam döküm değil.
      lines.push(`${ids[i]} = TableTile("${s.shape.id}", ${Math.min(s.shape.rowCount, 10)})`),
    );
  }

  if (!blocks.length) return "";

  // root ÖNCE gelir: OpenUI akış sırasında kabuğu hemen çizer.
  return [`root = Dashboard("${escape(title)}", [${blocks.join(", ")}])`, ...lines].join("\n");
}

/** OpenUI Lang çift tırnaklı dizge kullanır; içerikteki tırnağı kaçır. */
function escape(text: string): string {
  return text.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

/**
 * Başlığı sohbetten türetir.
 *
 * Kasıtlı olarak SIKICI: "Üretim Panosu" gibi. Başlıkta bulgu iddiası
 * ("Satışlar %12 Arttı") olmamalı — düzenleyici veriye bakmıyor, öyle bir
 * iddiada bulunamaz.
 */
function deriveTitle(titles: string[]): string {
  if (!titles.length) return "Pano";
  const words = titles[0].split(/\s+/).slice(0, 3).join(" ");
  return words ? `${words} — Pano` : "Pano";
}
