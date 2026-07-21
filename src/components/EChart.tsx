"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts";

// ECharts için ince React sarmalayıcı: init/setOption/dispose + otomatik resize.
// (echarts-for-react yerine doğrudan echarts — React 19 uyumu için sürtünmesiz.)
export function EChart({
  option,
  height = 380,
  onSeriesClick,
}: {
  option: echarts.EChartsOption;
  height?: number;
  // Seri tıklaması (panel öne çıkarma vb.) — seriesIndex geri verilir.
  onSeriesClick?: (seriesIndex: number) => void;
}) {
  const el = useRef<HTMLDivElement>(null);
  const chart = useRef<echarts.ECharts | null>(null);
  const clickRef = useRef(onSeriesClick);
  clickRef.current = onSeriesClick;

  useEffect(() => {
    if (!el.current) return;
    const c = echarts.init(el.current, undefined, { renderer: "canvas" });
    chart.current = c;
    c.on("click", (params) => {
      const si = (params as { seriesIndex?: number }).seriesIndex;
      if (typeof si === "number") clickRef.current?.(si);
    });
    const ro = new ResizeObserver(() => c.resize());
    ro.observe(el.current);
    return () => {
      ro.disconnect();
      c.dispose();
      chart.current = null;
    };
  }, []);

  useEffect(() => {
    chart.current?.setOption(option, true);
  }, [option]);

  return <div ref={el} style={{ width: "100%", height }} />;
}
