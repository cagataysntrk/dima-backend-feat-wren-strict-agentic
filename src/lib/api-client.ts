// Single axios client for the dima-backend. Per saka-standards: all HTTP goes
// through this module (no scattered fetch calls).

import axios from "axios";
import type { AskRequest, AskResponse, CubeQuery, QueryResult, SchemaResponse } from "./types";

const baseURL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

export async function getSchema(): Promise<SchemaResponse> {
  const { data } = await apiClient.get<SchemaResponse>("/schema");
  return data;
}

export async function ask(body: AskRequest): Promise<AskResponse> {
  const { data } = await apiClient.post<AskResponse>("/ask", body);
  return data;
}

// Yorum çubuğu (chip) düzenlemesi — CubeQuery doğrudan, deterministik çalışır (LLM yok).
export async function askCube(body: {
  cube_query: CubeQuery;
  label?: string;
  session_id?: string;
}): Promise<AskResponse> {
  const { data } = await apiClient.post<AskResponse>("/cube", body);
  return data;
}

export async function runQuery(sql: string, limit?: number): Promise<QueryResult> {
  const { data } = await apiClient.post<QueryResult>("/query", { sql, limit });
  return data;
}

// Özellik bayrakları (ADR-0009): sektör ⊕ şirket katmanlı; değerler alpha|beta|prod.
export async function getFeatures(): Promise<Record<string, string>> {
  const { data } = await apiClient.get<{ features: Record<string, string> }>("/features");
  return data.features ?? {};
}

// "✓ doğru" / "✗ yanlış" (beta): kullanıcı geri bildirimi. right → çift VQR'a yazılır
// (aynı soru bir daha LLM'siz); undo → geri alınır; wrong → yakın öğrenilmiş çift
// silinir + negatif sinyal loglanır (eval/log madenciliği).
export async function verifyReport(
  cube_query: CubeQuery,
  label: string,
  opts?: { undo?: boolean; verdict?: "right" | "wrong"; session_id?: string },
): Promise<{ stored: boolean; removed: boolean }> {
  const { data } = await apiClient.post<{ stored: boolean; removed: boolean }>("/verify", {
    cube_query,
    label,
    ...opts,
  });
  return data;
}

// Zamanlanmış raporlar + bildirimler (ADR-0011)
export interface ScheduleSpec {
  label: string;
  cube_query: CubeQuery;
  period?: string | null;   // GÖRELİ dönem ("dün") — koşum anında çözülür
  every?: "hour" | "day" | "week";
  at?: string;
  weekday?: number;
  threshold?: { measure: string; op: string; value: number } | null;
}
export interface Notification {
  id: string;
  ts: string;
  kind: "alert" | "report";
  message: string;
  label?: string;
  contract_id?: string | null;
}
export async function createSchedule(spec: ScheduleSpec): Promise<{ id: string }> {
  const { data } = await apiClient.post<{ schedule: { id: string } }>("/schedules", spec);
  return data.schedule;
}
export async function getNotifications(limit = 20): Promise<Notification[]> {
  const { data } = await apiClient.get<{ notifications: Notification[] }>("/notifications", { params: { limit } });
  return data.notifications ?? [];
}

// Normalize axios errors into a readable message (backend sends {detail}).
export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    return error.message;
  }
  return error instanceof Error ? error.message : "Bilinmeyen hata";
}
