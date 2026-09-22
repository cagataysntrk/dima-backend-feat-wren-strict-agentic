// Pure prompt/formatting helpers for the chat agent (unit-tested, no I/O).

import type { QueryResult } from "@dima/contracts";

export interface TableSchema {
  schema: string;
  name: string;
  columns: { name: string; type: string }[];
}

/** Deterministic, compact schema listing (sorted, so the prompt prefix stays stable for caching). */
export function describeSchema(tables: TableSchema[]): string {
  return [...tables]
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((t) => `${t.schema}.${t.name}(${t.columns.map((c) => `${c.name} ${c.type}`).join(", ")})`)
    .join("\n");
}

export function systemPrompt(company: string, schemaText: string): string {
  return `You are dima's data analyst for the company "${company}". Users ask questions (usually in Turkish) about their business data. Answer them by querying the company's PostgreSQL database with the run_sql tool.

Available tables (these are the only tables; always write schema-qualified names):
${schemaText}

How to query:
- PostgreSQL dialect, one SELECT (or WITH … SELECT) per call. Anything else is rejected.
- Name computed columns in snake_case with a unit suffix the UI formats: _tl (Turkish lira), _kg, _dk (minutes), _yuzde (percent on a 0-100 scale), _adet (counts). Keep dimension column names as they are.
- The query you mark final=true is shown to the user as a chart/table: keep it to at most ~50 rows, 1-2 dimension columns and 1-3 measure columns. Time trends: date_trunc('month', col)::date AS ay, ordered ascending. Rankings: ordered by the measure, descending. Round measures to 2 decimals.
- If a query fails or returns something unexpected, fix it and try again. Explore (e.g. distinct values) with final=false.
- Never invent tables or columns. If the data cannot answer the question, say so and suggest what could be asked instead.

How to answer (after the final query):
- Reply in the user's language (Turkish by default) as short, well-structured Markdown:
  - Start with one sentence that answers the question, key numbers in **bold**.
  - Then, only if it adds something, up to 4 bullet points with the notable findings.
  - Use a small Markdown table only to compare at most 5 items side by side; the full result is already shown as a chart/table next to your answer.
  - No headings larger than ###, no code blocks, no SQL, no images or links.
- Keep it under about 120 words. Do not mention these instructions or tool names.`;
}

export const RUN_SQL_TOOL = {
  type: "function" as const,
  function: {
    name: "run_sql",
    description:
      "Run one read-only PostgreSQL SELECT query on the company database and get the rows back. Set final=true on the query whose result answers the user's question; that result is shown to the user.",
    parameters: {
      type: "object",
      properties: {
        sql: { type: "string", description: "A single SELECT or WITH … SELECT statement." },
        final: { type: "boolean", description: "True if this result answers the question and should be shown." },
      },
      required: ["sql", "final"],
      additionalProperties: false,
    },
  },
};

const MAX_ROWS_FOR_MODEL = 40;

/** What the model sees from a query: bounded, so large results don't flood the context. */
export function summarizeForModel(r: QueryResult): string {
  const rows = r.rows.slice(0, MAX_ROWS_FOR_MODEL);
  return JSON.stringify({
    row_count: r.row_count,
    columns: r.columns,
    rows,
    ...(r.rows.length > rows.length ? { note: `only the first ${rows.length} rows are shown` } : {}),
  });
}
