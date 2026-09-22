// The ONLY browser-side HTTP surface of this app (same rule as @dima/api-client
// in apps/web). Talks same-origin to /api/*; the server gateway does the rest.

import type { QueryResult } from "@dima/contracts";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, { ...init, credentials: "same-origin" });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(res.status, body.error ?? "Beklenmeyen bir hata oluştu.");
  return body as T;
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export type Filters = Record<string, string[]>;

function qs(filters: Filters, extra: Record<string, string> = {}): string {
  const p = new URLSearchParams(extra);
  for (const [k, vs] of Object.entries(filters)) for (const v of vs) p.append(k, v);
  const s = p.toString();
  return s ? `?${s}` : "";
}

export interface Item {
  kind: "card" | "dashboard" | "model";
  id: number;
  name: string;
  description: string | null;
  display: string | null;
}

export interface CardPayload {
  card: { id: number; name: string; description: string | null; display: string };
  result: QueryResult;
  drillable: boolean;
}

export interface Parameter {
  slug: string;
  name: string;
  kind: "date" | "category";
}

export interface Widget {
  id: number;
  cardId: number;
  title: string;
  display: string;
  row: number;
  col: number;
  sizeX: number;
  sizeY: number;
}

export interface DashboardMeta {
  id: number;
  name: string;
  description: string | null;
  parameters: Parameter[];
  widgets: Widget[];
}

export interface WidgetData {
  id: number;
  result: QueryResult | null;
  error: string | null;
}

export interface DrillScope {
  dashboardId: number;
  dashcardId: number;
  filters: Filters;
}

export const gateway = {
  items: () => api<{ items: Item[] }>("/api/items").then((r) => r.items),
  card: (id: number) => api<CardPayload>(`/api/cards/${id}/data`),
  dashboard: (id: number) => api<DashboardMeta>(`/api/dashboards/${id}`),
  dashboardData: (id: number, filters: Filters) =>
    api<{ widgets: WidgetData[] }>(`/api/dashboards/${id}/data${qs(filters)}`).then((r) => r.widgets),
  parameterValues: (id: number, slug: string) =>
    api<{ values: string[] }>(`/api/dashboards/${id}/params/${encodeURIComponent(slug)}/values`).then(
      (r) => r.values,
    ),
  drill: (cardId: number, column: string, value: string, scope?: DrillScope) =>
    api<{ result: QueryResult }>(`/api/cards/${cardId}/drill`, json({ column, value, scope })).then(
      (r) => r.result,
    ),
  runSql: (sql: string) => api<{ result: QueryResult }>("/api/sql/run", json({ sql })).then((r) => r.result),
  saveSql: (name: string, sql: string) => api<{ id: number }>("/api/sql/save", json({ name, sql })),
  upload: (file: File) => {
    const form = new FormData();
    form.set("file", file);
    return api<{ id: number }>("/api/uploads", { method: "POST", body: form });
  },
  /** Export is a plain download link (the browser handles the attachment). */
  exportUrl: (cardId: number, format: "csv" | "xlsx", scope?: DrillScope) =>
    `/api/cards/${cardId}/export${qs(
      scope?.filters ?? {},
      scope
        ? { format, dashboardId: String(scope.dashboardId), dashcardId: String(scope.dashcardId) }
        : { format },
    )}`,
};
