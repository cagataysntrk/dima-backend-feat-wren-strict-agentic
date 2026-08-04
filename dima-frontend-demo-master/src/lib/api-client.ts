// Single axios client for the dima-backend. Per saka-standards: all HTTP goes
// through this module (no scattered fetch calls).
//
// Auth (saka-standards 02): access token MEMORY'de (Bearer interceptor), refresh token
// HTTP-only cookie'de. baseURL="/api" → Next rewrite backend'e proxy'ler (same-origin:
// cookie middleware'e görünür, CORS yok, backend URL gizli). 401 → /auth/refresh → retry.

import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import type {
  AskJobStatus,
  AskRequest,
  AskResponse,
  BlastRadius,
  ConnectionConfirmResult,
  ConnectionDraft,
  ConnectionTestResult,
  CubeQuery,
  DashboardDetail,
  DashboardListItem,
  DashboardWidgetData,
  ContributionResponse,
  DecisionRecord,
  MeasureApproveInput,
  MeasureCandidate,
  MeasurePreview,
  MeasurePreviewInput,
  QueryResult,
  Report,
  ReportBlockInput,
  DrillRequestInput,
  DrillResponse,
  EylemOnayResult,
  SunumTercihi,
  SchemaResponse,
  StatsToday,
  TenantConnectionCreateInput,
  TenantConnectionOut,
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

// --- Konsol logu (1 Ağustos 2026, kullanıcı talebi: "her girdiyi net şekilde loglayalım,
// llm mi patladı api mi docker mı front mu görelim") -------------------------------------
// TEK entegrasyon noktası: her `apiClient` çağrısı (askCube/ask/uploadDataset/... hepsi bu
// dosyadan geçer, saka-standards kuralı) otomatik olarak burada loglanır — çağıran
// fonksiyonların HİÇBİRİNE ayrı log eklemek GEREKMEZ. Hassas alanlar (parola, base64 dosya
// içeriği) özetlenir, ham haliyle konsola YAZILMAZ.
type _Timed = InternalAxiosRequestConfig & { _startedAt?: number; _retry?: boolean };

function _summarizePayload(data: unknown): unknown {
  if (!data || typeof data !== "object" || Array.isArray(data)) return data;
  const clone: Record<string, unknown> = { ...(data as Record<string, unknown>) };
  if (typeof clone.password === "string") clone.password = "***";
  if (typeof clone.content_b64 === "string") {
    clone.content_b64 = `<base64 ${(clone.content_b64 as string).length} karakter>`;
  }
  return clone;
}

apiClient.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
  (config as _Timed)._startedAt = Date.now();
  console.log(
    `[dima:api] → ${(config.method ?? "get").toUpperCase()} ${config.url}`,
    _summarizePayload(config.data),
  );
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
  (r) => {
    const started = (r.config as _Timed)._startedAt;
    const ms = started !== undefined ? Date.now() - started : undefined;
    console.log(
      `[dima:api] ← ${r.status} ${(r.config.method ?? "get").toUpperCase()} ${r.config.url}` +
        (ms !== undefined ? ` (${ms}ms)` : ""),
    );
    return r;
  },
  async (error: AxiosError) => {
    const original = error.config as _Timed | undefined;
    const url = original?.url ?? "";
    const isAuthCall = url.includes("/auth/login") || url.includes("/auth/refresh");
    const started = original?._startedAt;
    const ms = started !== undefined ? Date.now() - started : undefined;
    // AYIRT EDİCİ log: `error.response` YOKSA istek backend'e hiç ULAŞMADI (ağ/CORS/Docker
    // ayakta değil) — VARSA backend cevap verdi ama hata döndü (LLM/uygulama hatası, detay
    // `error.response.data.detail`'de). Bu ikisi kullanıcının "llm mi api mi docker mı"
    // sorusunu konsol tek satırdan ayırt etmesini sağlar.
    if (!error.response) {
      console.error(
        `[dima:api] ✗ AĞ HATASI ${(original?.method ?? "?").toUpperCase()} ${url}` +
          (ms !== undefined ? ` (${ms}ms)` : "") +
          " — backend'e ulaşılamadı (sunucu/Docker çalışıyor mu, CORS?)",
        { code: error.code, message: error.message },
      );
    } else {
      console.error(
        `[dima:api] ✗ ${error.response.status} ${(original?.method ?? "?").toUpperCase()} ${url}` +
          (ms !== undefined ? ` (${ms}ms)` : ""),
        { detail: (error.response.data as { detail?: unknown } | undefined)?.detail,
          data: error.response.data, message: error.message },
      );
    }
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

// Faz 4.1 (31 Temmuz 2026) — backend'de `ask_async_discovery` bayrağı açık tenant'larda
// Discovery (LLM ham-SQL, en yavaş yol) senkron dönmez: /ask hemen bir job_id taşıyan
// yanıt döner, gerçek sonuç GET /ask/jobs/{id} poll'uyla gelir. Bayrak kapalıyken (varsayılan,
// bugünkü demo) `data.job_id` HİÇ dolmaz — bu fonksiyon aynı satırda hemen döner, hiçbir
// davranış değişmez. Poll GÖRÜNMEZDİR: page.tsx'in useMutation'ı bu Promise'in çözülmesini
// bekler, mevcut "yürütülüyor" yükleme durumu (mutation.isPending) OLDUĞU GİBİ çalışmaya
// devam eder — yeni bir UI bileşeni gerekmez.
const ASK_JOB_POLL_MS = 1500;
const ASK_JOB_MAX_POLLS = 240; // ~6 dakika üst sınır — sonsuz poll'u önler

// Faz 4.12 (1 Ağustos 2026) — dış yol haritası 2.9 "canlı düşünme adımları": her poll'da
// BİRİKEN trace'i (iş henüz tamamlanmasa da) opsiyonel bir callback'e iletir — page.tsx
// bunu görüntüleyebilir. Verilmezse davranış AYNI (yalnız nihai sonucu bekler).
async function pollAskJob(
  jobId: string,
  onProgress?: (trace: string[]) => void,
): Promise<AskResponse> {
  for (let i = 0; i < ASK_JOB_MAX_POLLS; i++) {
    await new Promise((resolve) => setTimeout(resolve, ASK_JOB_POLL_MS));
    const { data } = await apiClient.get<AskJobStatus>(`/ask/jobs/${jobId}`);
    if (data.trace && data.trace.length > 0) onProgress?.(data.trace);
    if (data.status === "completed" && data.response) {
      return data.response;
    }
    if (data.status === "failed") {
      // Dürüst ret — arka-plan işi çökse bile kullanıcıya çıplak hata yerine mevcut
      // "note" desenine uyan bir AskResponse döner (ChatPanel bunu normal notmuş gibi gösterir).
      return {
        question: data.question ?? "",
        sql: "",
        planned_sql: null,
        result: null,
        source: null,
        cube_query: null,
        note: data.error || "Bu soru için arka planda bir sorun oluştu.",
        trace: [`arka-plan işi: başarısız (${data.error || "bilinmeyen hata"})`],
      };
    }
  }
  throw new Error(
    "İşlem beklenenden uzun sürdü (arka planda hâlâ çalışıyor olabilir). Lütfen tekrar dener misin?",
  );
}

// FAZ S — AŞAMA AKIŞI. Ölçüldü (canlı): deterministik yol ~100-800 ms (akış gereksiz),
// LLM yolu 2,8-5,5 sn — sessizlik tam orada. Biriken trace bu aşamaları ZATEN taşıyordu;
// eksik olan anında iletmekti (poll 1,5 sn'de bir bakıyor, akış adım doğduğu an veriyor).
//
// ⚠ `EventSource` KULLANILMADI ve bu bir GÜVENLİK kararıdır: EventSource Authorization
// başlığı gönderemez, tek yolu token'ı URL'e koymaktır ve o token sunucu loglarına /
// tarayıcı geçmişine sızar. Bu deponun açık kuralı "access token memory'de, localStorage'a
// ASLA". Sunucu SSE BİÇİMİ üretir, taşıma `fetch` + ReadableStream'dir → Bearer aynen
// çalışır, hiçbir değişmez gevşetilmez.
//
// Akış KURULAMAZSA (eski tarayıcı, ters vekil tamponlaması, ağ) sessizce POLL'a düşülür —
// yetenek kaybı yok, yalnız güncelleme gecikmesi eski hâline döner.
async function streamAskJob(
  jobId: string,
  onProgress?: (trace: string[]) => void,
): Promise<AskResponse | null> {
  const token = getAccessToken();
  let r: Response;
  try {
    r = await fetch(`${baseURL}/ask/jobs/${jobId}/stream`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });
  } catch {
    return null;                       // ağ/CORS → poll'a düş
  }
  if (!r.ok || !r.body) return null;

  const okuyucu = r.body.getReader();
  const cozucu = new TextDecoder();
  const birikmis: string[] = [];
  let tampon = "";
  try {
    for (;;) {
      const { done, value } = await okuyucu.read();
      if (done) break;
      tampon += cozucu.decode(value, { stream: true });
      // SSE çerçevesi: olaylar boş satırla ayrılır. Yarım çerçeve tamponda BEKLER —
      // yarısını ayrıştırmak "adım" metnini ortadan kesip yanlış gösterirdi.
      const parcalar = tampon.split("\n\n");
      tampon = parcalar.pop() ?? "";
      for (const parca of parcalar) {
        const ad = /^event:\s*(.+)$/m.exec(parca)?.[1]?.trim();
        const ham = /^data:\s*(.+)$/m.exec(parca)?.[1];
        if (!ad || !ham) continue;
        const veri = JSON.parse(ham);
        if (ad === "adim") {
          birikmis.push(veri.metin);
          onProgress?.([...birikmis]);
        } else if (ad === "tamam") {
          return (veri.response as AskResponse) ?? null;
        } else if (ad === "hata") {
          return null;                 // dürüst ret üretimini poll yoluna bırak
        } else if (ad === "zaman_asimi") {
          return null;
        }
      }
    }
  } catch {
    return null;
  } finally {
    try { await okuyucu.cancel(); } catch { /* bağlantı zaten kapalı */ }
  }
  return null;
}

export async function ask(
  body: AskRequest,
  onProgress?: (trace: string[]) => void,
): Promise<AskResponse> {
  const { data } = await apiClient.post<AskResponse>("/ask", body);
  if (data.job_id) {
    // Önce AKIŞ; kurulamazsa POLL (yetenek kaybı yok, yalnız gecikme eski hâline döner).
    const akan = await streamAskJob(data.job_id, onProgress);
    if (akan) return akan;
    return pollAskJob(data.job_id, onProgress);
  }
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
  thread_id?: string | null;
}): Promise<AskResponse> {
  const { data } = await apiClient.post<AskResponse>("/cube", body);
  return data;
}

// ⚠️ FAZ 0.7 — `runQuery()` SİLİNDİ. Ölçüldü [KANIT §0.1-6]: sarmalayıcı vardı, **çağıranı
// yoktu** (sıfır tüketici). Uç kapısı bunu YEŞİL sanıyordu çünkü `/query` dizesi
// sarmalayıcının KENDİ içinde geçiyordu — kapının "ölü sarmalayıcı" boyutu (FAZ 0.14/K1)
// tam bunun için eklendi ve bu satırı o yakaladı.
//
// Uç (`POST /query`) backend'de DURUYOR ve `API_ONLY` beyanı taşıyor: ham-SQL yürütme
// yüzeyi bilinçli olarak kullanıcıya açılmamıştır (MIMARI §5: "yüklenen dosyaya serbest
// Python" ile aynı gerekçe — uydurma sayının kapısı). Sarmalayıcının kendisi ise ölü
// koddu: silinmesi, "bir gün lazım olur" diye bekleyen bir yalanı ortadan kaldırır.

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

// "✓ doğru" / "✗ yanlış" — strict-agentic (wren_sql) /ask cevapları için geri bildirim.
// verifyReport'un (CubeQuery) wren_sql karşılığı: right → VQR'a yazılır (aynı/çok benzer
// soru bir daha LLM'siz), undo → geri alınır, wrong → kayıt silinir + negatif sinyal loglanır.
export async function askVerify(
  body: {
    question: string;
    sql?: string | null;
    session_id?: string;
    verdict?: "right" | "wrong";
    undo?: boolean;
    comment?: string;
  },
): Promise<{ stored: boolean; removed: boolean }> {
  const { data } = await apiClient.post<{ stored: boolean; removed: boolean }>("/ask/verify", body);
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
  // NEDEN (Faz F3): `message` NE olduğunu söyler ("eşik ihlali — M-07: 45"), bu alan
  // NİYE olduğunu ("makine: M-07 — 12.400 kg arttı (net değişimin %61'i)"). Etiketler
  // backend'de PII-maskelidir ve tıklanabilir sorgu TAŞIMAZ: maskeli bir değere filtre
  // kuran sorgu boş döner, "tıkla" deyip boş sonuç vermek hiç tıklatmamaktan kötüdür.
  // Kanıt yolu `contract_id`'dir.
  neden?: string[];
  neden_not?: string | null;   // kırpma/tarama sınırı ya da dürüst red gerekçesi
}

// Zamanlanmış rapor kaydı (GET /schedules öğesi) — doğrulama turu düzeltmesi (1 Ağustos
// 2026): kullanıcı bir zamanlama OLUŞTURABİLİYORDU ama sonra listeleyip SİLEMİYOR/elle
// ÇALIŞTIRAMIYORDU (yalnız `createSchedule` vardı) — bu tip + aşağıdaki 3 fonksiyon o
// eksik yönetim yüzeyini kapatır.
export interface ScheduleListItem {
  id: string;
  label: string;
  cube_query: CubeQuery;
  period?: string | null;
  every: string;
  at?: string | null;
  weekday?: number | null;
  threshold?: Record<string, unknown> | null;
  enabled?: boolean;
  /** FAZ 1.1b — bu arka plan işi KİMİN ADINA koşuyor (`run_as_user_id` → `created_by`).
   *
   * `null` = SAHİPSİZ. O kayıt artık KOŞMAZ (backend fail-closed): kimliksiz bir arka
   * plan işi `authorize()`'ı hiç çağırmaz ve sahibinin yetkisi alındıktan sonra da
   * koşardı. Arayüz bunu GÖSTERMEK ZORUNDA — yoksa kullanıcı sessizce durmuş bir
   * raporu beklemeye devam eder. */
  run_as?: string | null;
}
export async function createSchedule(spec: ScheduleSpec): Promise<{ id: string }> {
  const { data } = await apiClient.post<{ schedule: { id: string } }>("/schedules", spec);
  return data.schedule;
}
// FAZ E — kalıcı sunum tercihleri. YAZMA UCU YOK ve bu bilinçli: tercih yazmak
// /ask/eylem onay kademesinden geçer (Faz H "onaysız hiçbir yazma" değişmezi).
export async function listTercihler(): Promise<SunumTercihi[]> {
  const { data } = await apiClient.get<{ tercihler: SunumTercihi[] }>("/tercihler");
  return data.tercihler ?? [];
}

export async function silTercih(anahtar: string): Promise<void> {
  await apiClient.delete(`/tercihler/${anahtar}`);
}

// FAZ H — bir eylem ÖNERİSİNİN onayı. Ayrı bir uçtur çünkü onay, kullanıcının kendi
// kimliğiyle attığı AYRI bir istektir: backend eylemi kayıttan çözer, `authorize()`'ı
// YENİDEN çağırır (öneri anındaki yetkiye güvenmek TOCTOU olurdu) ve argümanları var
// olan handler'a verir. `view_hint` burada eklenir: kullanıcının o anki CANLI görünümünü
// (tip/pivot) yalnız frontend bilir — backend onu uydurmaz.
export async function onaylaEylem(
  eylem: string,
  argumanlar: Record<string, unknown>,
): Promise<EylemOnayResult> {
  const { data } = await apiClient.post<EylemOnayResult>("/ask/eylem", { eylem, argumanlar });
  return data;
}
// Query Contract keşif/replay (doğrulama turu düzeltmesi, 1 Ağustos 2026) — `contract_id`
// ekranda küçük bir metin olarak gösteriliyordu ama TIKLANAMAZ/incelenip yeniden-
// oynatılamazdı; backend uçları (/contracts, /contracts/{cid}, /contracts/{cid}/replay)
// zaten HAZIRDI, yalnız frontend'den hiç çağrılmıyordu.
export interface ContractRecord {
  id: string;
  ts: string | null;
  session: string | null;
  question: string | null;
  cube_query: CubeQuery | null;
  sql: string | null;
  result_hash: string | null;
  row_count: number | null;
  schema_version: string | null;
  source: string | null;
}
export interface ContractReplayResult {
  contract: ContractRecord;
  replay: {
    verdict: string;
    sql?: string;
    row_count?: number;
    sql_match?: boolean;
    result_match?: boolean;
    schema_version_now?: string;
    schema_changed?: boolean;
    error?: string;
  };
}

// ⚠️ FAZ 0.6 — `GET /contracts` (liste) TÜKETİCİSİZDİ [KANIT §0.1-5] ve uç kapısı onu
// **yeşil sanıyordu**: `/contracts` dizesi hem `` `/contracts/${cid}` `` içinde hem bir
// yorum satırında geçiyordu. FAZ 0.14/K1'in tam-yol + yorumsuz taraması onu açığa
// çıkardı — kapı, kurulmasının üzerinden bir madde geçmeden iş gördü.
//
// 🔴 **YENİ PANEL AÇILMADI** (panel tavanı 13/13, pay 0 — `PK-23`): liste
// `ContractDetailPanel`'in **giriş görünümü** olur. *"Yeni özellik yeni panel doğurmaz."*
export async function listContracts(limit = 20): Promise<{ contracts: ContractRecord[] }> {
  const { data } = await apiClient.get<{ contracts: ContractRecord[] }>("/contracts", {
    params: { limit },
  });
  return data;
}

/** FAZ 1.6 — kolon kökeni cümleleri. **Şablonlar BACKEND'de** üretilir; burada
 * ikinci bir şablon kümesi yazmak "aynı kuralın iki sahibi" olurdu ve ikisi zamanla
 * ayrışıp kullanıcıya AYNI kanıtı FARKLI cümlelerle gösterirdi.
 *
 * Discovery ham SQL'inde tek bir cümle döner: köken **bilinmiyor** — ve bu `undefined`
 * ile AYNI ŞEY DEĞİLDİR (`undefined` = hiç sorulmadı, "bilinmiyor" = soruldu, cevap yok).
 * ⚠ Teknik köken GRAFİĞİ gösterilmez (KD-13): kullanıcının sorusu "bu sayı nereden
 * geldi"dir ve cevabı bir CÜMLEDİR — graf bir geliştirici artefaktıdır. */
export type KokenCumlesi = string;

export async function getContract(cid: string): Promise<ContractRecord> {
  const { data } = await apiClient.get<ContractRecord>(`/contracts/${cid}`);
  return data;
}

export async function replayContract(cid: string): Promise<ContractReplayResult> {
  const { data } = await apiClient.get<ContractReplayResult>(`/contracts/${cid}/replay`);
  return data;
}

export async function listSchedules(): Promise<ScheduleListItem[]> {
  const { data } = await apiClient.get<{ schedules: ScheduleListItem[] }>("/schedules");
  return data.schedules ?? [];
}

export async function deleteSchedule(id: string): Promise<void> {
  await apiClient.delete(`/schedules/${id}`);
}

export async function runScheduleNow(id: string): Promise<{ notification: Notification }> {
  const { data } = await apiClient.post<{ notification: Notification }>(
    `/schedules/${id}/run`,
  );
  return data;
}

export async function getNotifications(limit = 20): Promise<Notification[]> {
  const { data } = await apiClient.get<{ notifications: Notification[] }>("/notifications", {
    params: { limit },
  });
  return data.notifications ?? [];
}

// K1 (rehberli analitik) — rol/sektör bazlı başlangıç soruları (küratörlü; yoksa katalog).
// `grup` opsiyonel (Faz 4.8) — küratörlü listede departman etiketi, katalog otomatiğinde yok.
export interface Starter {
  label: string;
  query: string;
  grup?: string;
}
export async function getStarters(): Promise<Starter[]> {
  const { data } = await apiClient.get<{ starters: Starter[] }>(
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

// Panoyu yeniden adlandır / görünürlüğünü değiştir (doğrulama turu düzeltmesi, 1 Ağustos
// 2026) — `PATCH /dashboards/{id}` zaten vardı, frontend'den hiç çağrılmıyordu; kullanıcı
// bir panoyu oluşturduktan sonra ASLA adını değiştiremiyordu.
export async function patchDashboard(
  id: string,
  body: { title?: string; visibility?: "private" | "tenant" },
): Promise<{ id: string; title: string; visibility: string }> {
  const { data } = await apiClient.patch<{ id: string; title: string; visibility: string }>(
    `/dashboards/${id}`, body,
  );
  return data;
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
// `pos`/`refresh` (doğrulama turu düzeltmesi, 1 Ağustos 2026, P2-22) — backend'de zaten
// var olan (`DashboardWidget.pos_json`/`refresh`) ama YAZMA ucu hiç kabul etmediği için
// frontend'den hiç kullanılamayan iki alan; genişlik (`pos.w`) + yenileme sıklığı artık
// kaydedilebilir.
export async function patchDashboardWidget(
  id: string,
  wid: string,
  body: { view_hint?: string; period?: string; title?: string;
          pos?: { x: number; y: number; w: number; h: number } | null; refresh?: string },
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

// --- Discovery→Promote (Faz 2d) — ölçü onay iş akışı --------------------------------
export async function listMeasureCandidates(status?: string): Promise<MeasureCandidate[]> {
  const { data } = await apiClient.get<{ candidates: MeasureCandidate[] }>(
    "/measures/candidates",
    { params: status ? { status } : undefined },
  );
  return data.candidates ?? [];
}

export async function getMeasureCandidate(id: string): Promise<MeasureCandidate> {
  const { data } = await apiClient.get<MeasureCandidate>(`/measures/candidates/${id}`);
  return data;
}

export async function getMeasureBlastRadius(
  id: string,
  cube: string,
  measure_name: string,
): Promise<BlastRadius> {
  const { data } = await apiClient.get<BlastRadius>(
    `/measures/candidates/${id}/blast-radius`,
    { params: { cube, measure_name } },
  );
  return data;
}

// Faz 4.2 — ONAYIN KURU KOŞUMU: YAML'a yazmadan diff. `measure:read` yeter (bu uç
// hiçbir şey değiştirmez). ReviewPanel onay butonunu diff GÖRÜLENE kadar kilitler.
export async function previewMeasureCandidate(
  id: string,
  body: MeasurePreviewInput,
): Promise<MeasurePreview> {
  const { data } = await apiClient.post<MeasurePreview>(
    `/measures/candidates/${id}/preview`,
    body,
  );
  return data;
}

export async function approveMeasureCandidate(
  id: string,
  body: MeasureApproveInput,
): Promise<MeasureCandidate> {
  const { data } = await apiClient.post<MeasureCandidate>(
    `/measures/candidates/${id}/approve`,
    body,
  );
  return data;
}

export async function rejectMeasureCandidate(id: string, note?: string): Promise<MeasureCandidate> {
  const { data } = await apiClient.post<MeasureCandidate>(`/measures/candidates/${id}/reject`, {
    note,
  });
  return data;
}

export async function deprecateMeasureCandidate(
  id: string,
  reason?: string,
  superseded_by_measure?: string,
): Promise<MeasureCandidate> {
  const { data } = await apiClient.post<MeasureCandidate>(
    `/measures/candidates/${id}/deprecate`,
    { reason, superseded_by_measure },
  );
  return data;
}

// Faz 4.10 (1 Ağustos 2026) — dallı kök-neden analizi: her adım (explain/expand/select/
// related/raw) bu TEK ucu çağırır; backend GERÇEK sorguyu çalıştırır (mock yok) ve kendi
// Query Contract kaydını üretir (drill.py + ask.py::ask_drill).
export async function drillAsk(body: DrillRequestInput): Promise<DrillResponse> {
  const { data } = await apiClient.post<DrillResponse>("/ask/drill", body);
  return data;
}

// Faz 5.1/5.2 — "NEDEN DEĞİŞTİ?": bir cube_query'nin dönemsel değişimini KULLANILMAYAN
// boyutlara dağıtır (segment), ya da fiyat/miktar/birleşik etkiye ayrıştırır (pvm).
// Her bulgu kendi cube_query'sini taşır → tıklanınca /cube ile LLM'siz koşar.
export async function askContribution(body: {
  cube_query: CubeQuery;
  mode?: "yoy" | "mom";
  kind?: "segment" | "pvm";
  session_id?: string;
  max_dimensions?: number;
}): Promise<ContributionResponse> {
  const { data } = await apiClient.post<ContributionResponse>("/ask/contribution", body);
  return data;
}

// --- Karar Kaydı (Faz E-4) ---------------------------------------------------------
// İKİ uç, ikisinin de tüketicisi var (MIMARI §14.1): yaz + DOĞRULA. Makbuzun değeri onu
// KONTROL EDEBİLMEKTE; kaydedip bir daha bakmadığın bir kayıt tutanak değil temennidir.
export async function saveDecision(body: {
  question?: string | null;
  chosen?: unknown;
  options?: unknown;
  rationale?: string | null;
  note?: string | null;
  contract_ids?: string[];
  session_id?: string | null;
  // ⚠️ FAZ 0.11 — `supersedes` YETİMDİ: backend `DecisionIn`'de VARDI, istemci onu
  // **hiç gönderemiyordu** ([KANIT §0.1-7]). Yol haritası açık: *"`supersedes`
  // **BAĞLANIR** (silinmez — **II-E.7 ona dayanıyor**)"*.
  // Karar **silinmez** (`decision.py:35`): iptal/revizyon YENİ bir kayıt yazar ve
  // eskisini `supersedes` ile işaret eder. Bu alan olmadan revizyon zinciri kurulamaz
  // ve "karar geçmişi" bir yığın kopuk kayda dönerdi.
  supersedes?: string | null;
}): Promise<DecisionRecord> {
  const { data } = await apiClient.post<DecisionRecord>("/decisions", body);
  return data;
}

export async function verifyDecision(id: string): Promise<DecisionRecord> {
  const { data } = await apiClient.get<DecisionRecord>(`/decisions/${id}`);
  return data;
}

// Faz 4.13c — meta-güven özeti ("bugün %X soru LLM'siz cevaplandı").
export async function getStatsToday(days = 1): Promise<StatsToday> {
  const { data } = await apiClient.get<StatsToday>("/stats/today", { params: { days } });
  return data;
}

// --- DB bağlama sihirbazı (Faz 4.5) — tenant-kendi-hizmeti ------------------
export async function testTenantConnection(
  body: TenantConnectionCreateInput,
): Promise<ConnectionTestResult> {
  const { data } = await apiClient.post<ConnectionTestResult>("/connections/test", body);
  return data;
}

export async function createTenantConnection(
  body: TenantConnectionCreateInput,
): Promise<TenantConnectionOut> {
  const { data } = await apiClient.post<TenantConnectionOut>("/connections", body);
  return data;
}

export async function listTenantConnections(): Promise<TenantConnectionOut[]> {
  const { data } = await apiClient.get<TenantConnectionOut[]>("/connections");
  return data;
}

export async function deleteTenantConnection(id: string): Promise<void> {
  await apiClient.delete(`/connections/${id}`);
}

export async function getConnectionDraft(id: string): Promise<ConnectionDraft> {
  const { data } = await apiClient.get<ConnectionDraft>(`/connections/${id}/draft`);
  return data;
}

export async function confirmConnectionDraft(
  id: string,
  draft: ConnectionDraft,
): Promise<ConnectionConfirmResult> {
  const { data } = await apiClient.post<ConnectionConfirmResult>(
    `/connections/${id}/confirm`,
    draft,
  );
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
