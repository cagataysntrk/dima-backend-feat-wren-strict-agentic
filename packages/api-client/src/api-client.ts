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
  QueryResult,
  SchemaResponse,
} from "@dima/contracts";

// --- Platform enjeksiyonu --------------------------------------------------
//
// Varsayılanlar bugünkü web davranışının BİREBİR aynısı; hiçbir çağıran
// değişmek zorunda değil. Enjeksiyon noktaları iki ihtiyaç için var:
//
// 1. ON-PREM: `NEXT_PUBLIC_*` build'e gömülür, dolayısıyla tek imaj N müşteriye
//    gidemez. Backend adresi çalışma anında verilebilmeli.
// 2. MASAÜSTÜ (Tauri/Electron): uygulamanın önünde Next sunucusu YOK, yani
//    "/api" hiçbir yere gitmez ve same-origin refresh cookie'si kurulamaz.
//    Kullanıcı kendi on-prem adresini girer.
//
// `window` erişimi bu pakette bilinçli olarak SERBEST: api-client bir taşıma
// katmanı, platformdan haberdar olabilir — platforma KİLİTLİ olmamalı. Buna
// karşılık @dima/contracts ve @dima/domain'de DOM lint ile yasak.

export interface ApiClientConfig {
  /** Backend taban adresi. Varsayılan "/api" (Next rewrite-proxy'si). */
  baseURL?: string;
  /** Oturum kurtarılamadığında çağrılır. Varsayılan: /login'e yönlendirir. */
  onSessionExpired?: () => void;
  /** Harici/gezinme URL'i açar (OAuth). Varsayılan: window.location.href. */
  openUrl?: (url: string) => void;
}

const DEFAULT_BASE_URL = "/api";
let baseURL = DEFAULT_BASE_URL;
let onSessionExpired: () => void = defaultBounceToLogin;
let openUrl: (url: string) => void = defaultOpenUrl;

export function configureApiClient(config: ApiClientConfig): void {
  if (config.baseURL !== undefined) {
    baseURL = config.baseURL;
    apiClient.defaults.baseURL = config.baseURL;
  }
  if (config.onSessionExpired) onSessionExpired = config.onSessionExpired;
  if (config.openUrl) openUrl = config.openUrl;
}

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
// Oturum düştüğünde TEK bir yönlendirme yapılır: aynı anda 401 yiyen birden çok
// istek (me/features/schema/ask) art arda location atarsa tarayıcı döngüye girer.
let redirectingToLogin = false;

// Bayat refresh cookie'si HTTP-only olduğu için JS silemez; ?expired=1 işareti
// proxy.ts'e "bu cookie'yi sil ve login'i göster" der (yoksa /login → / döngüsü).
//
// WEB VARSAYILANI: masaüstünde rota kavramı farklı olacağı için
// `configureApiClient({ onSessionExpired })` ile değiştirilebilir.
function defaultBounceToLogin() {
  if (typeof window === "undefined" || redirectingToLogin) return;
  if (window.location.pathname === "/login") return;
  redirectingToLogin = true;
  const next = encodeURIComponent(window.location.pathname + window.location.search);
  window.location.href = `/login?expired=1&next=${next}`;
}

function defaultOpenUrl(url: string) {
  if (typeof window === "undefined") return;
  window.location.href = url;
}

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
      onSessionExpired();
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

// NOT: Aşağıdaki uçlar backend sözleşmesinde HENÜZ yok (auth şu an login/refresh/logout/me).
// UI hazır; backend `POST /auth/register`, `POST /auth/forgot`, `GET /auth/oauth/<p>`
// eklediğinde çalışır. Eklenene kadar zarifçe hata döner (apiErrorMessage gösterir).
export async function register(
  email: string,
  password: string,
): Promise<AuthUser> {
  const { data } = await apiClient.post<{ access_token: string; user: AuthUser }>(
    "/auth/register",
    { email, password },
  );
  setAccessToken(data.access_token);
  return data.user;
}

export async function requestPasswordReset(email: string): Promise<void> {
  await apiClient.post("/auth/forgot", { email });
}

export type OAuthProvider = "google" | "github" | "apple";
// OAuth başlat: backend'in yönlendirme başlattığı uca git.
export function startOAuth(provider: OAuthProvider, next = "/app"): void {
  openUrl(`${baseURL}/auth/oauth/${provider}?next=${encodeURIComponent(next)}`);
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

export interface LiveSnapshot {
  synthetic: true;
  watermark: string;
  window_status: "partial" | "complete";
  department: "knitting" | "dyehouse" | "factory";
  oee: number;
  production_kg: number;
  downtime_min: number;
  freshness_seconds: number;
}

export async function getLiveSnapshot(): Promise<LiveSnapshot[]> {
  const { data } = await apiClient.get<LiveSnapshot[]>("/internal/live/snapshot");
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
