// Dışa aktarma (Faz 2 UX cilası, 31 Temmuz 2026): grafik → PNG/SVG, tablo → CSV, rapor →
// tarayıcının yerleşik yazdırma diyaloğu ("PDF olarak kaydet"). Yeni bağımlılık YOK:
// grafik için ECharts'ın kendi (canvas/svg) render motoru, tablo için elle CSV üretimi.

import * as echarts from "echarts";
import type { QueryResult } from "./types";

function triggerDownload(href: string, filename: string) {
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function safeFilenamePart(s: string): string {
  return s
    .normalize("NFKD")
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/\s+/g, "_")
    .slice(0, 60) || "dima";
}

// Grafiği PNG (canvas) ya da SVG (vektör) olarak indirir. Görünen (canlı) grafik
// örneğinin durumuna (zoom/pan) bağlı KALMAMAK için — daha ÖNGÖRÜLEBİLİR ve basit —
// AYNI `option`'dan GEÇİCİ, ekran-dışı bir ECharts örneği oluşturup ondan görüntü alır,
// hemen sonra `dispose` eder (canlı grafiğe hiç dokunmaz).
export function exportChartImage(
  option: echarts.EChartsOption,
  format: "png" | "svg",
  filenameBase: string,
  opts: { width?: number; height?: number; dark?: boolean } = {},
): void {
  const width = opts.width ?? 900;
  const height = opts.height ?? 480;
  const bg = opts.dark ? "#0a0a0a" : "#ffffff";

  const container = document.createElement("div");
  container.style.width = `${width}px`;
  container.style.height = `${height}px`;
  container.style.position = "fixed";
  container.style.left = "-99999px";
  container.style.top = "0";
  document.body.appendChild(container);

  const chart = echarts.init(container, undefined, {
    renderer: format === "svg" ? "svg" : "canvas",
    width,
    height,
  });
  try {
    chart.setOption({ ...option, backgroundColor: option.backgroundColor ?? bg }, true);
    const url =
      format === "svg"
        ? chart.getDataURL({ type: "svg" })
        : chart.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: bg });
    triggerDownload(url, `${safeFilenamePart(filenameBase)}.${format}`);
  } finally {
    chart.dispose();
    container.remove();
  }
}

// Tablo → CSV. UTF-8 BOM eklenir (Excel'in BOM'suz UTF-8'i yanlış kod sayfasıyla açıp
// ç/ğ/ş/ı gibi karakterleri bozması BİLİNEN bir tuzaktır). Alan içeren değerler (virgül/
// tırnak/satır sonu) RFC 4180'e göre tırnaklanır.
function csvCell(v: unknown): string {
  const s = v == null ? "" : String(v);
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function exportTableCsv(result: QueryResult, filenameBase: string): void {
  const lines = [
    result.columns.map(csvCell).join(","),
    ...result.rows.map((r) => result.columns.map((c) => csvCell(r[c])).join(",")),
  ];
  const csv = "﻿" + lines.join("\r\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  try {
    triggerDownload(url, `${safeFilenamePart(filenameBase)}.csv`);
  } finally {
    URL.revokeObjectURL(url);
  }
}

// "PDF" — üçüncü-parti bir render kütüphanesi (html2canvas/jspdf) KURMAK yerine (kırılgan,
// büyük bağımlılık) tarayıcının YERLEŞİK yazdırma diyaloğu kullanılır: kullanıcı "PDF olarak
// kaydet"i oradan seçer. `globals.css`'teki `@media print` kuralı rail/butonları gizler.
export function printReport(): void {
  window.print();
}
