"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts";

// ECharts için ince React sarmalayıcı: init/setOption/dispose + RESPONSIVE boyut.
// (echarts-for-react yerine doğrudan echarts — React 19 uyumu için sürtünmesiz.)
//
// Responsive (telefon/tablet/web): yükseklik SABİT değil — container GENİŞLİĞİNDEN aspect-ratio
// ile türetilir ve [minHeight, maxHeight] arasına kırpılır. Dar ekranda (telefon) grafik kısalır,
// geniş ekranda (web/pano 2-kolon) oranını korur. `height` AÇIKÇA verilirse (ör. e-posta/rapor
// sabit ölçek — resize gerekmez) o kullanılır ve genişlik-türetimi devre dışı kalır.
export function EChart({
  option,
  height,
  aspect = 0.56,
  minHeight = 240,
  maxHeight = 460,
  onSeriesClick,
  onDataPointClick,
}: {
  option: echarts.EChartsOption;
  // Açık yükseklik (px) — verilirse responsive türetim kapanır (email/rapor sabit ölçek).
  height?: number;
  aspect?: number;      // yükseklik = genişlik × aspect (min/max ile kırpılır)
  minHeight?: number;
  maxHeight?: number;
  // Seri tıklaması (panel öne çıkarma vb.) — seriesIndex geri verilir.
  onSeriesClick?: (seriesIndex: number) => void;
  // Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-2) — TEK bir veri noktasına (çubuk/dilim)
  // tıklamayı da taşır: `dataIndex` (serideki konum) + `name` (ECharts'ın x-ekseni/dilim
  // etiketi olarak zaten gösterdiği KATEGORİ DEĞERİ — ayrı bir satır-eşleme İCAT ETMEDEN
  // doğrudan kullanılabilir). `onSeriesClick`'in YANINDA, GERİYE-UYUMLU ek bir callback.
  onDataPointClick?: (info: { seriesIndex: number; dataIndex: number; name: string }) => void;
}) {
  const el = useRef<HTMLDivElement>(null);
  const chart = useRef<echarts.ECharts | null>(null);
  const clickRef = useRef(onSeriesClick);
  const pointClickRef = useRef(onDataPointClick);
  // Boyut parametreleri closure'da bayatlamasın → ref'ten okunur (RO tek sefer bağlanır).
  const sizeRef = useRef({ height, aspect, minHeight, maxHeight });
  // Ref güncellemeleri RENDER'da değil effect'te (react-compiler: no ref access during render).
  useEffect(() => {
    clickRef.current = onSeriesClick;
    pointClickRef.current = onDataPointClick;
    sizeRef.current = { height, aspect, minHeight, maxHeight };
  });

  useEffect(() => {
    if (!el.current) return;
    const c = echarts.init(el.current, undefined, { renderer: "canvas" });
    chart.current = c;
    c.on("click", (params) => {
      const p = params as { seriesIndex?: number; dataIndex?: number; name?: string };
      if (typeof p.seriesIndex === "number") clickRef.current?.(p.seriesIndex);
      if (typeof p.seriesIndex === "number" && typeof p.dataIndex === "number" && p.name) {
        pointClickRef.current?.({ seriesIndex: p.seriesIndex, dataIndex: p.dataIndex, name: p.name });
      }
    });
    const applySize = () => {
      const node = el.current;
      if (!node) return;
      const s = sizeRef.current;
      if (s.height == null) {
        const w = node.clientWidth || 0;
        const h = Math.max(s.minHeight, Math.min(s.maxHeight, Math.round(w * s.aspect)));
        node.style.height = `${h}px`;
      }
      c.resize();
    };
    const ro = new ResizeObserver(applySize);
    ro.observe(el.current);
    applySize();
    return () => {
      ro.disconnect();
      c.dispose();
      chart.current = null;
    };
  }, []);

  useEffect(() => {
    chart.current?.setOption(option, true);
  }, [option]);

  // İlk ölçümden önce 0-yükseklik sıçramasını önle: açık height ya da minHeight tabanı.
  return <div ref={el} style={{ width: "100%", height: height ?? minHeight }} />;
}
