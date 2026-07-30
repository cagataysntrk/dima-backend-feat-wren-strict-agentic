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
                  <li key={col.name} className="flex justify-between gap-3 text-xs text-neutral-500">
                    <span className="font-mono truncate">{col.name}</span>
                    <span className="text-neutral-400 shrink-0">{col.type}</span>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </section>

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
