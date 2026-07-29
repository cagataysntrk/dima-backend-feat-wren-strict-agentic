// Single axios client for the dima-backend. Per saka-standards: all HTTP goes
// through this module (no scattered fetch calls).
//
// Auth (saka-standards 02): access token MEMORY'de (Bearer interceptor), refresh token
// HTTP-only cookie'de. baseURL="/api" → Next rewrite backend'e proxy'ler (same-origin:
// cookie middleware'e görünür, CORS yok, backend URL gizli). 401 → /auth/refresh → retry.

import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import type {
  Analysis,
  AskRequest,
  AskResponse,
  CubeQuery,
  Preference,
  QueryResult,
  Report,
  SchemaResponse,
  UploadResponse,
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

/**
 * Chat'e bağlı Excel/CSV yükleme (D1/D2/D36 — "kurulum = konuşma").
 *
 * Dosya base64 gövdede gider: backend `python-multipart` istemiyor, sözleşme
 * `UploadRequest{session_id, filename, content_b64}`. Veri OTURUM DuckDB'sine
 * iner (ephemeral) → oto-cube → mevcut NL hattı; yani yükledikten hemen sonra
 * aynı sohbette sorgulanabilir.
 *
 * Ham dosya buluta/LLM'e GİTMEZ — yerel DuckDB'ye ingest edilir.
 */
export async function uploadDataset(
  file: File,
  sessionId: string,
): Promise<UploadResponse> {
  const content_b64 = await fileToBase64(file);
  const { data } = await apiClient.post<UploadResponse>("/ask/upload", {
    session_id: sessionId,
    filename: file.name,
    content_b64,
  });
  return data;
}

/** FileReader → saf base64 (data: URL öneki kırpılır). */
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error ?? new Error("Dosya okunamadı"));
    reader.onload = () => {
      const out = String(reader.result ?? "");
      const comma = out.indexOf(",");
      resolve(comma >= 0 ? out.slice(comma + 1) : out);
    };
    reader.readAsDataURL(file);
  });
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

// K1 (rehberli analitik) — rol/sektör bazlı başlangıç soruları. Küratörlü (pack
// zinciri, rol-filtreli); küratör boşsa backend katalog otomatiğine düşer, o da
// erişilemezse boş liste döner (çağıran yerel yedeğini gösterir). Deterministik.
export interface Starter {
  label: string;
  query: string;
}
export async function getStarters(): Promise<Starter[]> {
  const { data } = await apiClient.get<{ starters: Starter[] }>("/starters");
  return data.starters ?? [];
}

// "✓ doğru" / "✗ yanlış" (beta): kullanıcı geri bildirimi. right → çift VQR'a yazılır
// (aynı soru bir daha LLM'siz); undo → geri alınır; wrong → yakın öğrenilmiş çift
// silinir + negatif sinyal loglanır (eval/log madenciliği).
//
// `comment`: "✗ yanlış"ta OPSİYONEL gerekçe ("yanlış ölçü", "dönem hatalı"…).
// Backend bunu etkileşim kaydının note'una yazar → log madencisini besler.
// "Neden yanlış" bilgisi olmadan negatif sinyal yalnız "bir şey bozuk" der.
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
/** Sabit EŞİK alarmı — ölçü bir sınırı geçince bildirim düşer. */
export interface ThresholdAlarm {
  measure: string;
  op: "gt" | "gte" | "lt" | "lte";
  value: number;
}
/** ANOMALİ alarmı — sabit sınır yok; z-skoru ile "olağandışı" değer yakalanır. */
export interface AnomalyAlarm {
  measure: string;
  method: "zscore";
  k?: number;
}

export interface ScheduleSpec {
  label: string;
  cube_query: CubeQuery;
  period?: string | null; // GÖRELİ dönem ("dün") — koşum anında çözülür
  every?: "hour" | "day" | "week";
  at?: string;
  weekday?: number;
  // Alarm (opsiyonel). Backend aynı `threshold` alanında iki şekli de kabul eder
  // ve check_alert içinde ayrıştırır — bu yüzden burada da tek alan, birleşim tipi.
  threshold?: ThresholdAlarm | AnomalyAlarm | null;
  // Ek teslim kanalları (opsiyonel). Uygulama içi bildirim (zil) HER ZAMAN düşer;
  // burası onun yerine değil ÜSTÜNE e-posta ekler.
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

// --- Panolar (§9 canlı izleme) ---------------------------------------------
//
// Widget = KAYITLI SORGU (cube_query + GÖRELİ dönem), sonuç değil. Dönem her
// `/data` çağrısında yeniden çözülür ("dün" bugün başka bir gündür) — schedule
// ve VQR ile aynı "kayıtlı sorgu" soyutlaması. Bu yüzden pano bayatlamaz ve
// satırlar hiçbir zaman istemcide saklanmaz.
export interface DashboardListItem {
  id: string;
  title: string;
  visibility: "private" | "tenant";
  widget_count: number;
  /** Sahibi ben miyim — tenant'a açık panolar başkasına SALT-OKUNUR görünür. */
  own: boolean;
  updated_at: string;
}
export interface DashboardWidget {
  id: string;
  title: string;
  cube_query: CubeQuery;
  view_hint?: string | null;
  period?: string | null;
  pos?: Record<string, number> | null;
  refresh: string;
}
export interface DashboardDetail {
  id: string;
  title: string;
  visibility: "private" | "tenant";
  own: boolean;
  widgets: DashboardWidget[];
}
/** Widget başına sonuç. `error` doludur → o karo hata gösterir, pano ayakta kalır. */
export interface WidgetData {
  id: string;
  result: QueryResult | null;
  error: string | null;
}

export async function listDashboards(): Promise<{
  dashboards: DashboardListItem[];
  max_per_user: number;
}> {
  const { data } = await apiClient.get<{
    dashboards: DashboardListItem[];
    max_per_user: number;
  }>("/dashboards");
  return { dashboards: data.dashboards ?? [], max_per_user: data.max_per_user ?? 10 };
}

export async function createDashboard(title?: string): Promise<{ id: string; title: string }> {
  const { data } = await apiClient.post<{ id: string; title: string }>("/dashboards", {
    title: title ?? "",
  });
  return data;
}

export async function getDashboard(id: string): Promise<DashboardDetail> {
  const { data } = await apiClient.get<DashboardDetail>(`/dashboards/${id}`);
  return data;
}

export async function updateDashboard(
  id: string,
  patch: { title?: string; visibility?: "private" | "tenant" },
): Promise<void> {
  await apiClient.patch(`/dashboards/${id}`, patch);
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
    refresh?: string;
  },
): Promise<{ id: string }> {
  const { data } = await apiClient.post<{ id: string }>(`/dashboards/${id}/widgets`, widget);
  return data;
}

export async function deleteDashboardWidget(id: string, widgetId: string): Promise<void> {
  await apiClient.delete(`/dashboards/${id}/widgets/${widgetId}`);
}

/** Tüm widget'ları KOŞAR (göreli dönemler yeniden çözülür). Canlı görünüm budur. */
export async function getDashboardData(id: string): Promise<WidgetData[]> {
  const { data } = await apiClient.get<{ widgets: WidgetData[] }>(`/dashboards/${id}/data`);
  return data.widgets ?? [];
}

// --- CEO demo — backend sözleşmesi hazır, uçlar henüz gelmedi ---------------
//
// Şekiller `docs/contracts/ceo-demo.md`'de sabit. Bu fonksiyonlar
// feature flag açılmadan çağrılmaz (web'de ReportBuilder / AnalystStudio
// geçitli); böylece olmayan bir endpoint için kullanıcıya 404 deneyimi yaşatmak
// yerine yetenek tamamen karanlıkta kalır.

export type ReportTemplate = "uretim_ozeti" | "surdurulebilirlik" | "yonetim" | "gunluk";

export interface ReportRequest {
  template: ReportTemplate;
  period?: string | null;
  locale?: string;
  session_id?: string;
  cube_queries?: CubeQuery[];
}

export async function generateReport(request: ReportRequest): Promise<Report> {
  const { data } = await apiClient.post<Report>("/report", request);
  return data;
}

export type AnalysisKind = "swot" | "scorecard" | "plan" | "risk" | "breakeven";

export interface AnalysisRequest {
  kind: AnalysisKind;
  period?: string | null;
  session_id?: string;
  cube_queries?: CubeQuery[];
}

export async function runAnalysis(request: AnalysisRequest): Promise<Analysis> {
  const { data } = await apiClient.post<Analysis>("/analysis", request);
  return data;
}

export interface CreatePreferenceRequest {
  scope: Preference["scope"];
  value: string;
  source_question: string;
}

export async function listPreferences(): Promise<Preference[]> {
  const { data } = await apiClient.get<{ preferences: Preference[] }>("/preferences");
  return data.preferences ?? [];
}

export async function createPreference(request: CreatePreferenceRequest): Promise<Preference> {
  const { data } = await apiClient.post<Preference>("/preferences", request);
  return data;
}

export async function deletePreference(id: string): Promise<void> {
  await apiClient.delete(`/preferences/${id}`);
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
