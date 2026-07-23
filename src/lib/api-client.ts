// Single axios client for the dima-backend. Per saka-standards: all HTTP goes
// through this module (no scattered fetch calls).
//
// Auth (saka-standards 02): access token MEMORY'de (Bearer interceptor), refresh token
// HTTP-only cookie'de. baseURL="/api" → Next rewrite backend'e proxy'ler (same-origin:
// cookie middleware'e görünür, CORS yok, backend URL gizli). 401 → /auth/refresh → retry.

import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import type { AskRequest, AskResponse, CubeQuery, QueryResult, SchemaResponse } from "./types";

// Same-origin: browser "/api/..."e konuşur, Next backend'e rewrite'ler (next.config.ts).
const baseURL = "/api";

export const apiClient = axios.create({
  baseURL,
  withCredentials: true, // refresh cookie'yi gönder/al
  headers: { "Content-Type": "application/json" },
});

// --- Auth token (memory) ---------------------------------------------------
let accessToken: string | null = null;
export function setAccessToken(t: string | null) {
  accessToken = t;
}
export function getAccessToken() {
  return accessToken;
}

apiClient.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
  return config;
});

// Eşzamanlı 401'ler tek refresh'i paylaşır.
let refreshing: Promise<string | null> | null = null;

async function doRefresh(): Promise<string | null> {
  try {
    // Raw axios (interceptor'suz) — refresh'in kendisi 401 döngüsüne girmesin.
    const { data } = await axios.post<{ access_token: string }>(
      `${baseURL}/auth/refresh`,
      {},
      { withCredentials: true },
    );
    setAccessToken(data.access_token);
    return data.access_token;
  } catch {
    setAccessToken(null);
    return null;
  }
}

apiClient.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;
    const url = original?.url ?? "";
    const isAuthCall = url.includes("/auth/login") || url.includes("/auth/refresh");
    if (error.response?.status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true;
      refreshing = refreshing ?? doRefresh();
      const token = await refreshing;
      refreshing = null;
      if (token) {
        original.headers = original.headers ?? {};
        original.headers.Authorization = `Bearer ${token}`;
        return apiClient(original);
      }
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

// --- Auth endpoints --------------------------------------------------------
export interface AuthUser {
  id: string;
  email: string;
  tenant_id: string | null;
  is_superadmin: boolean;
  roles: string[];
}

export async function login(
  email: string,
  password: string,
  otp?: string,
): Promise<AuthUser> {
  const { data } = await apiClient.post<{ access_token: string; user: AuthUser }>(
    "/auth/login",
    { email, password, ...(otp ? { otp } : {}) },
  );
  setAccessToken(data.access_token);
  return data.user;
}

export async function refresh(): Promise<string | null> {
  return doRefresh();
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post("/auth/logout");
  } finally {
    setAccessToken(null);
  }
}

export async function getMe(): Promise<AuthUser> {
  const { data } = await apiClient.get<AuthUser>("/auth/me");
  return data;
}

// --- Data endpoints --------------------------------------------------------
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
  period?: string | null; // GÖRELİ dönem ("dün") — koşum anında çözülür
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
  const { data } = await apiClient.get<{ notifications: Notification[] }>("/notifications", {
    params: { limit },
  });
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
