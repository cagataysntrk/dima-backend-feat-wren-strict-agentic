"use client";

import type { AskV2CoreResponse } from "@/lib/types";

export function V2CoreCard({
  data,
  onClarification,
}: {
  data: AskV2CoreResponse;
  onClarification?: (token: string, label: string) => void;
}) {
  const response = data.response;

  return (
    <article className="mx-auto max-w-4xl px-8 py-5">
      <div className="border border-hairline bg-background px-4 py-4">
        <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
          <span>{data.status === "research_brief" ? "V2 Research" : "V2 Core"}</span>
          <span>·</span>
          <span>{response.kind}</span>
          {response.official_verified && (
            <>
              <span>·</span>
              <span className="text-emerald-600 dark:text-emerald-400">doğrulandı</span>
            </>
          )}
        </div>

        <p className="whitespace-pre-wrap text-[14px] leading-6 text-foreground">
          {response.text}
        </p>

        {data.research_brief && (
          <div className="mt-4 border-t border-hairline pt-3">
            <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              <span>ResearchBrief</span>
              <span>·</span>
              <span>{data.research_brief.status}</span>
            </div>
            {data.research_brief.scope.time_surfaces.length > 0 && (
              <div className="mb-2 font-mono text-[11px] text-neutral-500">
                Dönem: {data.research_brief.scope.time_surfaces.join(" · ")}
              </div>
            )}
            <div className="space-y-1.5">
              {data.research_brief.questions.map((question) => (
                <div
                  key={question.goal_id}
                  className="flex items-start gap-2 font-mono text-[11px] text-neutral-500"
                >
                  <span className="shrink-0">[{question.priority}]</span>
                  <span className="min-w-0 flex-1">{question.source_text}</span>
                  <span className="shrink-0">{question.status}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {response.scope_chips.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {response.scope_chips.map((chip, index) => (
              <span
                key={`${chip.kind}-${chip.canonical_ref ?? chip.label}-${index}`}
                className="border border-hairline px-2 py-1 font-mono text-[10px] text-neutral-500"
              >
                {chip.label}
              </span>
            ))}
          </div>
        )}

        {response.clarification_chips.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {response.clarification_chips.map((chip) => (
              <button
                key={chip.candidate_id}
                type="button"
                onClick={() => onClarification?.(chip.token, chip.label)}
                className="border border-accent/40 px-2.5 py-1.5 font-mono text-[11px] text-accent transition-colors hover:border-accent"
              >
                {chip.label}
              </button>
            ))}
          </div>
        )}

        {response.tables.map((table) => (
          <div key={table.execution_id} className="mt-4 overflow-x-auto border-t border-hairline pt-3">
            <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              {table.role === "comparison_reference" ? "referans" : "sonuç"}
              {" · "}
              {table.row_count} satır
              {table.truncated ? " · görünüm kırpıldı" : ""}
            </div>
            {table.rows.length > 0 ? (
              <table className="min-w-full border-collapse font-mono text-[11px]">
                <thead>
                  <tr>
                    {table.columns.map((column) => (
                      <th key={column} className="border-b border-hairline px-2 py-1 text-left font-medium">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {table.rows.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {table.columns.map((column) => (
                        <td key={column} className="border-b border-hairline/60 px-2 py-1.5 align-top">
                          {String(row[column] ?? "—")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="font-mono text-[11px] text-neutral-400">sonuç satırı yok</div>
            )}
          </div>
        ))}

        {response.evidence_refs.length > 0 && (
          <div className="mt-3 border-t border-hairline pt-2 font-mono text-[10px] text-neutral-400">
            Kanıt: {response.evidence_refs.map((ref) => ref.contract_id).join(" · ")}
          </div>
        )}

        {data.failure && (
          <div className="mt-3 border-l-2 border-amber-500/60 pl-3 font-mono text-[11px] text-neutral-500">
            {data.failure.stage}: {data.failure.message}
          </div>
        )}
      </div>
    </article>
  );
}
