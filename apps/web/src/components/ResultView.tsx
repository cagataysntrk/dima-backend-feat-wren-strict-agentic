"use client";

import { useEffect, useState } from "react";
import { getSchema } from "@dima/api-client";
import { setSchemaUnits } from "@dima/domain";
import { ResultView as UiResultView } from "@dima/ui/result/ResultView";

// Ölçü metadata'sı (/schema cubes[]) TEK okumadan iki şey besler:
//   • units            → format katmanı (₺, kg, %…)
//   • lower_is_better  → ısı haritası yön semantiği (yüksek = kötü ölçülerde rampa ters)
// Paylaşılan bileşen (@dima/ui) hiçbir API tanımaz; okuma burada, uygulamada kalır.
let _schemaLoaded = false;
let _lowerSet: ReadonlySet<string> = new Set();

function useSchemaMeta(): ReadonlySet<string> {
  const [lower, setLower] = useState<ReadonlySet<string>>(_lowerSet);
  useEffect(() => {
    if (_schemaLoaded) return;
    getSchema()
      .then((s) => {
        const cubes =
          (s as { cubes?: { units?: Record<string, string>; lower_is_better?: string[] }[] }).cubes ?? [];
        setSchemaUnits(Object.assign({}, ...cubes.map((c) => c.units ?? {})));
        _lowerSet = new Set(cubes.flatMap((c) => c.lower_is_better ?? []));
        _schemaLoaded = true;
        setLower(_lowerSet);
      })
      .catch(() => {});
  }, []);
  return lower;
}

export function ResultView(props: Omit<React.ComponentProps<typeof UiResultView>, "lowerSet">) {
  return <UiResultView {...props} lowerSet={useSchemaMeta()} />;
}
