// Single axios client for the dima-backend. Per saka-standards: all HTTP goes
// through this module (no scattered fetch calls).
//
// Auth (saka-standards 02): access token MEMORY'de (Bearer interceptor), refresh token
// HTTP-only cookie'de. baseURL="/api" → Next rewrite backend'e proxy'ler (same-origin:
// cookie middleware'e görünür, CORS yok, backend URL gizli). 401 → /auth/refresh → retry.

import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import type {
  AskRequest,
  AskResponse,
  CubeQuery,
  DashboardDetail,
  DashboardListItem,
  DashboardWidgetData,
  QueryResult,
  Report,
  ReportBlockInput,
  SchemaResponse,
} from "./types";

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
  // Backend authorize matrisinden gelen izinli aksiyonlar (ör. "vqr:write").
  // UI buton görünürlüğü BUNDAN okunur — rol semantiği frontend'e kopyalanmaz.
  permissions?: string[];
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

// Chat-scoped Excel/CSV yükleme (base modu): dosya base64 → oturum DuckDB'sine ingest →
// oto-cube. Sonraki ask'ler aynı session_id ile yüklenen veriyi sorgular (ephemeral).
export async function uploadDataset(body: {
  session_id: string;
  filename: string;
  content_b64: string;
}): Promise<import("./types").UploadResponse> {
  const { data } = await apiClient.post<import("./types").UploadResponse>("/ask/upload", body);
  return data;
}

// Sohbet geçmişi (per-user, backend'de kalıcı) — liste / getir (resume) / soft-delete.
export async function listConversations(): Promise<import("./types").Conversation[]> {
  const { data } = await apiClient.get<import("./types").Conversation[]>("/conversations");
  return data;
}

export async function getConversation(id: string): Promise<import("./types").ConversationDetail> {
  const { data } = await apiClient.get<import("./types").ConversationDetail>(`/conversations/${id}`);
  return data;
}

export async function deleteConversation(id: string): Promise<void> {
  await apiClient.delete(`/conversations/${id}`);
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
  opts?: { undo?: boolean; verdict?: "right" | "wrong"; session_id?: string; comment?: string },
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
  // Alarm (opsiyonel): sabit EŞİK {measure, op, value} VEYA ANOMALİ {measure, method:"zscore", k?}.
  // Aynı threshold alanı iki şekli de taşır (backend check_alert dispatch eder).
  threshold?:
    | { measure: string; op: string; value: number }
    | { measure: string; method: "zscore"; k?: number }
    | null;
  // Ek teslim kanalları (opsiyonel): e-posta alıcıları. In-app bell her zaman düşer.
  delivery?: { email?: { to: string[] } } | null;
}
export interface Notification {
  id: string;
  ts: string;
  kind: "alert" | "report" | "anomaly";
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

// K1 (rehberli analitik) — rol/sektör bazlı başlangıç soruları (küratörlü; yoksa katalog).
export async function getStarters(): Promise<{ label: string; query: string }[]> {
  const { data } = await apiClient.get<{ starters: { label: string; query: string }[] }>(
    "/starters",
  );
  return data.starters ?? [];
}

// --- Panolar (§9 canlı-izleme) --------------------------------------------
export async function listDashboards(): Promise<{
  dashboards: DashboardListItem[];
  max_per_user: number;
}> {
  const { data } = await apiClient.get<{
    dashboards: DashboardListItem[];
    max_per_user: number;
  }>("/dashboards");
  return data;
}

export async function createDashboard(title: string): Promise<{ id: string }> {
  const { data } = await apiClient.post<{ id: string }>("/dashboards", { title });
  return data;
}

export async function getDashboard(id: string): Promise<DashboardDetail> {
  const { data } = await apiClient.get<DashboardDetail>(`/dashboards/${id}`);
  return data;
}

export async function deleteDashboard(id: string): Promise<void> {
  await apiClient.delete(`/dashboards/${id}`);
}

export async function addDashboardWidget(
  id: string,
  widget: {
    title?: string;
    cube_query: CubeQuery;
    view_hint?: string | null;
    period?: string | null;
  },
): Promise<{ id: string }> {
  const { data } = await apiClient.post<{ id: string }>(`/dashboards/${id}/widgets`, widget);
  return data;
}

export async function deleteDashboardWidget(id: string, wid: string): Promise<void> {
  await apiClient.delete(`/dashboards/${id}/widgets/${wid}`);
}

// Widget görünüm durumunu KAYDET (pano'da tip/görünüm/dönem değişince) → yeniden yüklemede korunur.
export async function patchDashboardWidget(
  id: string,
  wid: string,
  body: { view_hint?: string; period?: string; title?: string },
): Promise<void> {
  await apiClient.patch(`/dashboards/${id}/widgets/${wid}`, body);
}

export async function getDashboardData(id: string): Promise<DashboardWidgetData[]> {
  const { data } = await apiClient.get<{ widgets: DashboardWidgetData[] }>(
    `/dashboards/${id}/data`,
  );
  return data.widgets ?? [];
}

// Çok-blok / çok-SAYFA rapor derleme (ADR-0024) — bloklar deterministik koşar + viz kararı alır.
export async function postReport(body: {
  title?: string;
  page_size?: number;
  blocks: ReportBlockInput[];
  session_id?: string;
}): Promise<Report> {
  const { data } = await apiClient.post<Report>("/report", body);
  return data;
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
