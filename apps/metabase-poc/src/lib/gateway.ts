// The ONLY browser-side HTTP surface of this app (same rule as @dima/api-client
// in apps/web). Talks same-origin to /api/*; the server gateway does the rest.

import type { QueryResult } from "@dima/contracts";
import { frameData, splitFrames } from "@/lib/sse";

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

export interface Insight {
  title: string;
  display: string;
  result: QueryResult | null;
  error: string | null;
}

export interface Revision {
  id: number;
  at: string;
  what: string;
  current: boolean;
}

export interface BrowseTable {
  id: number;
  name: string;
  displayName: string;
  fields: { id: number; name: string; label: string }[];
}

export interface ModelField {
  id: number;
  name: string;
  displayName: string;
  type: string;
  category: boolean;
  hidden: boolean;
  fkTargetFieldId: number | null;
}

export interface ModelTable {
  id: number;
  name: string;
  displayName: string;
  fields: ModelField[];
}

export interface SchemaColumn {
  id: number;
  name: string;
  type: string;
  fkTargetFieldId: number | null;
}

export interface SchemaTable {
  id: number;
  name: string;
  displayName: string;
  columns: SchemaColumn[];
}

export interface SchemaEdge {
  id: string;
  from: string;
  fromColumn: string;
  to: string;
  toColumn: string;
}

export interface SchemaGraph {
  tables: SchemaTable[];
  edges: SchemaEdge[];
}

export interface Item {
  kind: "card" | "dashboard" | "model";
  id: number;
  name: string;
  description: string | null;
  display: string | null;
}

export interface CardPayload {
  card: { id: number; name: string; description: string | null; display: string; goal: number | null };
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
  width: WidgetWidth;
  filtered: boolean;
  goal: number | null;
}

export type WidgetWidth = "kpi" | "half" | "full";

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

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface ChatAnswer {
  answer: string;
  sql: string | null;
  result: QueryResult | null;
  /** Opaque, authenticated native Metabot history/state. Never interpreted by the browser. */
  engineContext?: string;
}

export type Role = "owner" | "admin" | "member";

export interface Member {
  id: string;
  userId: string;
  name: string;
  email: string;
  role: Role;
  createdAt: string;
}

export interface ChatPrefs {
  maxRows: number;
}

export type ChatStreamEvent =
  | { type: "step"; id: number; text: string; done: boolean }
  | { type: "token"; text: string }
  | {
      type: "done";
      answer: string;
      sql: string | null;
      result: QueryResult | null;
      steps: string[];
      durationMs: number;
      engineContext: string;
    }
  | { type: "error"; message: string };

export const gateway = {
  browseTables: () => api<{ tables: BrowseTable[] }>("/api/browse").then((r) => r.tables),
  previewTable: (tableId: number, sort?: { fieldId: number; dir: "asc" | "desc" }) =>
    api<{ result: QueryResult }>(
      `/api/browse/${tableId}${sort ? `?sort=${sort.fieldId}&dir=${sort.dir}` : ""}`,
    ).then((r) => r.result),
  tableInsights: (tableId: number) =>
    api<{ table: string; insights: Insight[] }>(`/api/browse/${tableId}/insights`),
  dataModel: () => api<{ tables: ModelTable[] }>("/api/model").then((r) => r.tables),
  updateField: (fieldId: number, patch: { displayName?: string; category?: boolean; hidden?: boolean }) =>
    api<{ field: ModelField }>(`/api/model/fields/${fieldId}`, { ...json(patch), method: "PATCH" }).then((r) => r.field),
  tables: () => api<{ tables: { name: string; columns: string[] }[] }>("/api/tables").then((r) => r.tables),
  schemaGraph: () => api<SchemaGraph>("/api/schema"),
  setForeignKey: (fieldId: number, targetFieldId: number | null) =>
    api<{ field: ModelField }>(`/api/model/fields/${fieldId}/fk`, {
      ...json({ targetFieldId }),
      method: "PUT",
    }).then((r) => r.field),
  /**
   * Streamed chat: yields each event as it arrives. Abort the signal to stop —
   * the server sees the disconnect and stops generating too.
   */
  chatStream: async function* (
    messages: ChatTurn[],
    signal: AbortSignal,
    native: { conversationId: string; engineContext?: string | null },
  ): AsyncGenerator<ChatStreamEvent> {
    const res = await fetch("/api/chat", {
      ...json({ messages, conversationId: native.conversationId, engineContext: native.engineContext ?? null }),
      signal,
      credentials: "same-origin",
    });
    if (!res.ok || !res.body) {
      const body = await res.json().catch(() => ({}) as { error?: string });
      throw new ApiError(res.status, body.error ?? "Beklenmeyen bir hata oluştu.");
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const { frames, rest } = splitFrames(buffer);
      buffer = rest;
      for (const frame of frames) {
        const data = frameData(frame);
        if (data) yield JSON.parse(data) as ChatStreamEvent;
      }
    }
  },
  members: () => api<{ members: Member[]; myRole: Role; myMemberId: string }>("/api/settings/members"),
  addMember: (body: { email: string; name: string; role: "admin" | "member" }) =>
    api<{ password: string | null }>("/api/settings/members", json(body)),
  setMemberRole: (memberId: string, role: "admin" | "member") =>
    api<{ ok: true }>("/api/settings/members", { ...json({ memberId, role }), method: "PATCH" }),
  removeMember: (memberId: string) =>
    api<{ ok: true }>("/api/settings/members", { ...json({ memberId }), method: "DELETE" }),
  chatPrefs: () => api<ChatPrefs>("/api/settings/chat"),
  setChatPrefs: (patch: Partial<ChatPrefs>) => api<ChatPrefs>("/api/settings/chat", { ...json(patch), method: "PUT" }),
  search: (q: string) => api<{ items: Item[] }>(`/api/search?q=${encodeURIComponent(q)}`).then((r) => r.items),
  trash: () => api<{ items: Item[] }>("/api/trash").then((r) => r.items),
  restore: (kind: "card" | "dashboard", id: number) => api<{ ok: true }>("/api/trash", json({ kind, id })),
  copyCard: (cardId: number) => api<{ id: number; name: string }>(`/api/cards/${cardId}/copy`, { method: "POST" }),
  archiveCard: (cardId: number) => api<{ ok: true }>(`/api/cards/${cardId}`, { method: "DELETE" }),
  items: () => api<{ items: Item[] }>("/api/items").then((r) => r.items),
  card: (id: number) => api<CardPayload>(`/api/cards/${id}/data`),
  dashboard: (id: number) => api<DashboardMeta>(`/api/dashboards/${id}`),
  dashboardData: (id: number, filters: Filters) =>
    api<{ widgets: WidgetData[] }>(`/api/dashboards/${id}/data${qs(filters)}`).then((r) => r.widgets),
  parameterValues: (id: number, slug: string) =>
    api<{ values: string[] }>(`/api/dashboards/${id}/params/${encodeURIComponent(slug)}/values`).then(
      (r) => r.values,
    ),
  parameterSearch: (id: number, slug: string, q: string) =>
    api<{ values: string[] }>(
      `/api/dashboards/${id}/params/${encodeURIComponent(slug)}/search?q=${encodeURIComponent(q)}`,
    ).then((r) => r.values),
  drill: (cardId: number, column: string, value: string, scope?: DrillScope) =>
    api<{ result: QueryResult }>(`/api/cards/${cardId}/drill`, json({ column, value, scope })).then(
      (r) => r.result,
    ),
  cardHistory: (cardId: number) =>
    api<{ revisions: Revision[] }>(`/api/cards/${cardId}/history`).then((r) => r.revisions),
  revertCard: (cardId: number, revisionId: number) =>
    api<{ ok: true }>(`/api/cards/${cardId}/history`, json({ revisionId })),
  updateCard: (cardId: number, patch: { display?: string; goal?: number | null; name?: string }) =>
    api<{ ok: true }>(`/api/cards/${cardId}`, { ...json(patch), method: "PATCH" }),
  zoom: (cardId: number, value: string, scope?: DrillScope) =>
    api<{ result: QueryResult; unit: string; range: [string, string] }>(
      `/api/cards/${cardId}/zoom`,
      json({ value, scope }),
    ),
  breakouts: (cardId: number) =>
    api<{ fields: { id: number; name: string; label: string }[] }>(`/api/cards/${cardId}/breakouts`).then((r) => r.fields),
  breakout: (cardId: number, value: string, fieldId: number, scope?: DrillScope) =>
    api<{ result: QueryResult; by: string }>(`/api/cards/${cardId}/breakout`, json({ value, fieldId, scope })),
  runSql: (sql: string, values?: Record<string, string>) =>
    api<{ result: QueryResult }>("/api/sql/run", json({ sql, values })).then((r) => r.result),
  saveSql: (name: string, sql: string, values?: Record<string, string>) =>
    api<{ id: number }>("/api/sql/save", json({ name, sql, values })),
  amendUpload: (cardId: number, file: File, mode: "append" | "replace") => {
    const form = new FormData();
    form.set("file", file);
    return api<{ ok: true }>(`/api/uploads/${cardId}?mode=${mode}`, { method: "POST", body: form });
  },
  removeUpload: (cardId: number) => api<{ ok: true }>(`/api/uploads/${cardId}`, { method: "DELETE" }),
  upload: (file: File) => {
    const form = new FormData();
    form.set("file", file);
    return api<{ id: number }>("/api/uploads", { method: "POST", body: form });
  },
  /** Export is a plain download link (the browser handles the attachment). */
  createDashboard: (name: string) => api<{ id: number }>("/api/dashboards", json({ name })),
  updateDashboard: (id: number, patch: { name?: string; description?: string | null }) =>
    api<{ ok: true }>(`/api/dashboards/${id}`, { ...json(patch), method: "PATCH" }),
  archiveDashboard: (id: number) => api<{ ok: true }>(`/api/dashboards/${id}`, { method: "DELETE" }),
  addToDashboard: (id: number, cardId: number) =>
    api<{ wired: boolean }>(`/api/dashboards/${id}/cards`, json({ cardId })),
  saveLayout: (id: number, widgets: { id: number; width: WidgetWidth }[]) =>
    api<{ ok: true }>(`/api/dashboards/${id}/layout`, { ...json({ widgets }), method: "PUT" }),
  exportUrl: (cardId: number, format: "csv" | "xlsx", scope?: DrillScope) =>
    `/api/cards/${cardId}/export${qs(
      scope?.filters ?? {},
      scope
        ? { format, dashboardId: String(scope.dashboardId), dashcardId: String(scope.dashcardId) }
        : { format },
    )}`,
};
