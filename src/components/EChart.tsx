"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts";

// ECharts için ince React sarmalayıcı: init/setOption/dispose + otomatik resize.
// (echarts-for-react yerine doğrudan echarts — React 19 uyumu için sürtünmesiz.)
export function EChart({
  option,
  height = 380,
}: {
  option: echarts.EChartsOption;
  height?: number;
}) {
  const el = useRef<HTMLDivElement>(null);
  const chart = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!el.current) return;
    const c = echarts.init(el.current, undefined, { renderer: "canvas" });
    chart.current = c;
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
