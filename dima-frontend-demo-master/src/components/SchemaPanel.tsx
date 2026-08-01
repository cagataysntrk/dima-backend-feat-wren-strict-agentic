"use client";

import { useQuery } from "@tanstack/react-query";
import { getSchema } from "@/lib/api-client";

// Veri modeli (şema) — artık ana yüzeyde değil, Ayarlar drawer'ı içinde gösterilir (ADR-0007 K7).
export function SchemaPanel() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["schema"],
    queryFn: getSchema,
  });

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 mb-3">
          Tablolar
        </h3>
        {isLoading && <p className="text-sm text-neutral-400">Yükleniyor…</p>}
        {isError && (
          <p className="text-sm text-red-500">
            {"Backend'e ulaşılamadı. dima-backend çalışıyor mu?"}
          </p>
        )}
        <ul className="space-y-3">
          {data?.models.map((model) => (
            <li key={model.name} className="border border-hairline p-3">
              <p className="font-mono text-[13px] font-semibold text-accent">{model.name}</p>
              <ul className="mt-1.5 space-y-0.5">
                {model.columns.map((col) => (
                  <li key={col.name} className="text-xs text-neutral-500">
                    <div className="flex justify-between gap-3">
                      <span className="font-mono truncate">{col.name}</span>
                      <span className="text-neutral-400 shrink-0">{col.type}</span>
                    </div>
                    {/* Doğrulama turu düzeltmesi (1 Ağustos 2026, P2-22) — düşük-kardinaliteli
                        kolonların olası değerleri (filtre chip'i adayları) ZATEN backend'den
                        geliyordu ama hiç GÖSTERİLMİYORDU. */}
                    {col.values && col.values.length > 0 && (
                      <p className="mt-0.5 truncate font-mono text-[10px] text-neutral-400">
                        {col.values.slice(0, 8).join(", ")}
                        {col.values.length > 8 ? ` +${col.values.length - 8}` : ""}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </section>

      {data?.cubes && data.cubes.length > 0 && (
        <section>
          <h3 className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 mb-3">
            Cube&apos;lar (soru sorabileceğin ölçü/boyutlar)
          </h3>
          <ul className="space-y-3">
            {data.cubes.map((cube) => (
              <li key={cube.name} className="border border-hairline p-3">
                <p className="font-mono text-[13px] font-semibold text-accent">{cube.name}</p>
                {(cube.measures?.length ?? 0) > 0 && (
                  <p className="mt-1 text-xs text-neutral-500">
                    <span className="text-neutral-400">ölçüler: </span>
                    {cube.measures!.join(", ")}
                  </p>
                )}
                {(cube.dimensions?.length ?? 0) > 0 && (
                  <ul className="mt-1 space-y-0.5">
                    {cube.dimensions!.map((dim) => {
                      const vals = cube.dimension_values?.[dim];
                      return (
                        <li key={dim} className="text-xs text-neutral-500">
                          <span className="font-mono">{dim}</span>
                          {vals && vals.length > 0 && (
                            <span className="ml-1.5 font-mono text-[10px] text-neutral-400">
                              ({vals.slice(0, 6).join(", ")}
                              {vals.length > 6 ? ` +${vals.length - 6}` : ""})
                            </span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {data?.relationships && data.relationships.length > 0 && (
        <section>
          <h3 className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 mb-3">
            İlişkiler
          </h3>
          <ul className="space-y-2">
            {data.relationships.map((rel) => (
              <li key={rel.name} className="text-xs text-neutral-500">
                <span className="font-mono text-neutral-700 dark:text-neutral-300">
                  {rel.models.join(" → ")}
                </span>
                <span className="block text-neutral-400">{rel.condition}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
