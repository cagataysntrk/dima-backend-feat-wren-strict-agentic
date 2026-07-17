"use client";

import { useQuery } from "@tanstack/react-query";
import { getSchema } from "@/lib/api-client";

export function SchemaPanel() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["schema"],
    queryFn: getSchema,
  });

  return (
    <aside className="w-64 shrink-0 border-r border-neutral-200 dark:border-neutral-800 p-4 overflow-auto">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-neutral-500 mb-3">
        Veri Modeli
      </h2>
      {isLoading && <p className="text-sm text-neutral-400">Yükleniyor…</p>}
      {isError && (
        <p className="text-sm text-red-500">
          {"Backend'e ulaşılamadı. dima-backend çalışıyor mu?"}
        </p>
      )}
      <ul className="space-y-4">
        {data?.models.map((model) => (
          <li key={model.name}>
            <p className="font-mono text-sm font-semibold text-neutral-800 dark:text-neutral-200">
              {model.name}
            </p>
            <ul className="mt-1 space-y-0.5">
              {model.columns.map((col) => (
                <li key={col.name} className="flex justify-between text-xs text-neutral-500">
                  <span className="font-mono">{col.name}</span>
                  <span className="text-neutral-400">{col.type}</span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </aside>
  );
}
