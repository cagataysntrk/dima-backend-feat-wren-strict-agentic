// dima-backend response/request types (kept in sync with app/schemas.py).

export interface ColumnMeta {
  name: string;
  type: string;
  // Düşük kardinaliteli kolonların olası değerleri (filtre chip'i seçenekleri).
  values?: string[] | null;
}

export interface ModelMeta {
  name: string;
  columns: ColumnMeta[];
}

export interface RelationshipMeta {
  name: string;
  models: string[];
  join_type: string;
  condition: string;
}

export interface CubeMeta {
  name: string;
  measures?: string[];
  dimensions?: string[];
  time_dimensions?: string[];
  // Türev boyutlar dahil olası değerler (chip alternatifleri): {hafta_gunu: [Pzt..Paz]}
  dimension_values?: Record<string, string[]>;
}

export interface SchemaResponse {
  catalog: string | null;
  schema_name: string | null;
  models: ModelMeta[];
  relationships: RelationshipMeta[];
  cubes?: CubeMeta[];
  db_online?: boolean; // veri kaynağı TCP erişilebilir mi → çevrimiçi/çevrimdışı rozeti
}

export type Row = Record<string, unknown>;

export interface QueryResult {
  columns: string[];
  rows: Row[];
  row_count: number;
}

export type CubeQuery = Record<string, unknown>;

export interface AskResponse {
  question: string;
  sql: string;
  planned_sql: string | null;
  result: QueryResult | null;
  // Provenance: SQL'i kim üretti — "cube" (deterministik 🥇) | "llm:<sağlayıcı>" | "rule".
  source: string | null;
  // Rapor cube ile üretildiyse yapısal durum — takip mesajlarında geri gönderilir (ADR-0007).
  cube_query: CubeQuery | null;
  // Rapor üretilmediğinde dürüst açıklama (alan modelde yok / anlaşılamadı) — rapor değişmez.
  note?: string | null;
  // Sorgunun nasıl çözüldüğü — pipeline adımları ("?" ile gösterilir).
  trace?: string[];
  // Tıklanır chip'ler — meta örnek sorgular / dönem clarification seçenekleri.
  suggestions?: { label: string; query: string }[];
  // Görünüm isteği ("grafik ver") — client mevcut raporun görünümünü değiştirir.
  view_hint?: string | null;
  // Query Contract (ADR-0010): raporun kanıt kaydı kimliği
  contract_id?: string | null;
  // Cross-cube KPI kartı (CCC / likidite oranları): tek skaler + bileşenleri (DSO/DIO/DPO,
  // dönen varlık/KV kaynak…). Cube tablosu değil bileşke — KPI kartı olarak render edilir.
  kpi?: KpiCard | null;
  // EVRENSEL ÇIKTI YORUMU (feature flag: cikti_yorumlama) — her tablo/grafik/rapor/KPI için
  // DETERMİNİSTİK data-güdümlü yorum. Bayrak kapalıysa null (admin panelden kim görür kararlaşır).
  interpretation?: Interpretation | null;
  // K2 (rehberli analitik, feature flag: next_steps) — rapordan DETERMİNİSTİK sonraki adım
  // chip'leri: kırılım (boyut) / ölçek (measure) / zaman granülerliği. Her chip TAM cube_query
  // taşır → tıklanınca /cube ile LLM'siz koşar (mevcut chip düzenleme yolu).
  next_steps?: NextStep[];
  // K4 (karar motoru) — K3 sinyallerinden aksiyon önerileri: "neye bakmalısın" + opsiyonel
  // tıklanır drill (action). action varsa /cube ile LLM'siz koşar (K2 mekanizması).
  recommendations?: Recommendation[];
  // VİZ ÖNERİSİ (ADR-0024) — grafik/tablo/pivot KARARI backend'de (app/viz.py) deterministik
  // üretilir (Show Me + Cleveland-McGill + çok-birim politikası). Varsa FE yerel analyze() yerine
  // bunu render eder; view_hint + kullanıcı toggle üstüne biner. Yoksa null (FE analyze()'e düşer).
  viz?: VizSpec | null;
  // Faz 3 (31 Temmuz 2026) — birleşik açıklama: `trace`/`source`'un ÜSTÜNE biner, onları
  // SİLMEZ (SourceBadge/trace render'ı kırılmaz — kademeli geçiş). Rapor üretmeyen yanıtlarda
  // (netleştirme/chip) null.
  explain?: Explain | null;
  // Faz 4.1 (31 Temmuz 2026) — yalnız backend'de `ask_async_discovery` bayrağı açıkken dolar:
  // Discovery arka-plan işine kuyruklandığında (result/source HENÜZ yok). `api-client.ts::ask()`
  // bunu GÖRÜNMEZ şekilde poll'lar (mutation.isPending zaten doğru davranır) — normal şartlarda
  // bu alan bileşenlere HİÇ ULAŞMAZ, yalnız api-client içinde tüketilir.
  job_id?: string | null;
}

// Faz 4.1 — GET /ask/jobs/{id} yanıtı (yalnız api-client.ts::ask()'in dahili poll döngüsü kullanır).
// `trace` (Faz 4.12) iş HENÜZ tamamlanmadan da (pending/running) BİRİKEREK dolar.
export interface AskJobStatus {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  question?: string | null;
  response?: AskResponse | null;
  error?: string | null;
  trace?: string[];
}

// Faz 3 birleşik açıklama nesnesi (bkz. backend app/schemas.py::Explain).
export interface Explain {
  path: string;
  confidence: number | null;
  assumptions: string[];
}

// VizSpec — backend viz.recommend() çıktısı (ADR-0024). FE `chart.ts` Analysis'ine adapte edilir.
export interface VizSpec {
  kind: string; // kpi|bar|line|pie|heatmap|facet|facet_measure|scatter|stacked|treemap|pivot|table
  measures: string[];
  dims: string[];
  time_col: string | null;
  primary_dim: string | null;
  heat: { row: string; col: string } | null;
  heat_any: { row: string; col: string } | null;
  facet: { dim: string; x: string; series: string } | null;
  facet_measure: { measures: string[]; x: string; series: string | null } | null;
  scatter: { x: string; y: string; color?: string; size?: string } | null;
  pivot: { rows: string[]; cols: string[]; measures: string[] } | null;
  series_dim: string | null;
  units: Record<string, string>;
  unit_count: number;
  dual_axis: boolean;
  stackable: boolean;
  partition: boolean;
  alternatives: string[]; // kullanıcı-toggle önerileri (ör. ["pie"] / ["treemap"])
  table_mode: "table" | "pivot";
  lower_set?: string[];
}

export interface NextStep {
  label: string;
  kind: "dimension" | "measure" | "time";
  cube_query: CubeQuery;
}

export interface Recommendation {
  text: string;
  action?: NextStep | null;
}

export interface Interpretation {
  summary: string; // deterministik Türkçe özet (en yüksek/düşük, % değişim, trend, pay)
  facts?: { type: string; text: string }[]; // yapısal bulgular (ileride chip/rozet)
  // K3 (rehberli analitik) — PROAKTİF sinyaller: anomali / yön endişesi / yoğunlaşma.
  // Nötr özetten ayrı; önem düzeyine göre vurgulanır (info/warning/critical).
  signals?: { severity: "info" | "warning" | "critical"; kind: string; text: string }[];
}

// Sohbet geçmişi (backend'de kalıcı, per-user).
export interface Conversation {
  id: string;
  title: string;
  session_id: string;
  message_count: number;
  updated_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string;
  session_id: string;
  messages: AskResponse[]; // seq sırası (eski→yeni); resume için render edilir
}

// Panolar (§9 canlı-izleme) — widget = kayıtlı cube_query + göreli dönem.
export interface DashboardListItem {
  id: string;
  title: string;
  visibility: "private" | "tenant";
  widget_count: number;
  own: boolean;
  updated_at: string;
}

export interface DashboardWidget {
  id: string;
  title: string;
  cube_query: CubeQuery;
  view_hint: string | null;
  period: string | null;
  pos: { x: number; y: number; w: number; h: number } | null;
  refresh: string;
}

export interface DashboardDetail {
  id: string;
  title: string;
  visibility: "private" | "tenant";
  own: boolean;
  widgets: DashboardWidget[];
}

// /dashboards/{id}/data — her widget'ın canlı koşum sonucu (dönem çözülmüş).
export interface DashboardWidgetData {
  id: string;
  result: QueryResult | null;
  viz?: VizSpec | null; // ADR-0024: backend grafik/tablo/pivot kararı (chat ile aynı)
  error: string | null;
}

// Çok-blok / çok-SAYFA rapor (ADR-0024) — /report çıktısı. Her blok kendi viz kararını taşır;
// bloklar sayfalara bölünür (yazdırma/PDF dostu). Web/e-posta/PDF aynı kompozisyonu render eder.
export interface ReportBlock {
  title: string | null;
  cube_query: CubeQuery;
  period: string | null;
  view_hint?: string | null; // widget'ın kayıtlı görünümü (rapor onu onurlandırır)
  result: QueryResult | null;
  viz?: VizSpec | null;
  error: string | null;
}

export interface Report {
  title: string;
  pages: ReportBlock[][];
  block_count: number;
}

export interface ReportBlockInput {
  cube_query: CubeQuery;
  title?: string | null;
  period?: string | null;
  view_hint?: string | null;
}

// Chat-scoped Excel/CSV yükleme yanıtı (base modu).
export interface UploadResponse {
  dataset: string;
  row_count: number;
  columns: { orig: string; name: string; type: string; role: string }[];
  suggestions: { label: string; query: string }[];
}

export interface KpiCard {
  kpi: string;
  label: string;
  unit?: string | null;
  lower_is_better?: boolean;
  formula?: string | null;
  explain?: string | null;
  value: number | null;
  components: { key: string; label: string; unit?: string | null; value: number | null }[];
  // Dönem-serisi ("aylara göre ccc"): her kova için KPI değeri + bileşenleri → trend grafiği
  // (bileşenler aynı birimdeyse ayrı çizgi: CCC → DSO/DIO/DPO). Evrensel kova (gün/hafta/ay/
  // çeyrek/yıl); value = SON dönem (as-of başlık).
  granularity?: string | null;
  series?: {
    bucket: string;
    value: number | null;
    components?: { key: string; label: string; unit?: string | null; value: number | null }[];
  }[] | null;
}

export interface AskRequest {
  question: string;
  limit?: number;
  execute?: boolean;
  // Konuşmasal daraltma: önceki mesajlar + o anki raporun CubeQuery durumu.
  history?: string[];
  cube_query?: CubeQuery | null;
  // Strict-agentic (wren_sql) takip bağlamı: bir önceki AskResponse.sql. cube_query'den
  // BİLEREK ayrı — cube_query scheduling/dashboard/verify gibi gerçek CubeQuery şekli
  // varsayan özelliklerin de gate'i (bkz. ReportPanel.tsx); onu ham SQL taşımak için
  // yeniden kullanmak o özellikleri wren_sql cevaplarında da yanlışlıkla açardı.
  prev_sql?: string | null;
  // Sohbet oturumu kimliği — kalıcı logda chat'i gruplamak için.
  session_id?: string;
}

// Discovery→Promote (Faz 2d) — Discovery (ham-SQL LLM) yolunun ürettiği bir cevabın
// taslak "ölçü adayı" olarak yakalanmış hâli. `/measures/candidates*` bunları taşır.
export interface MeasureCandidate {
  id: string;
  status: "draft" | "pending_review" | "approved" | "rejected" | "deprecated";
  company: string;
  tenant_id: string | null;
  question: string;
  sql: string;
  sample_rows: { columns: string[]; rows: unknown[][] } | null;
  cube: string | null;
  measure_name: string | null;
  expression: string | null;
  measure_type: string;
  label: string | null;
  synonyms: string[];
  lower_is_better: boolean | null;
  golden_case_id: string | null;
  review_note: string | null;
  created_at: string;
  updated_at: string;
  name_conflict?: boolean | null;
}

export interface MeasureApproveInput {
  cube: string;
  measure_name: string;
  expression: string;
  type?: string;
  label?: string | null;
  synonyms?: string[];
  lower_is_better?: boolean | null;
  golden_case: {
    id: string;
    q: string;
    tags?: string[];
    expect?: string;
    shape?: Record<string, unknown>;
  };
}

export interface BlastRadius {
  verified_query: number;
  dashboard_widget: number;
  contract_log_structured: number;
  contract_log_raw_sql_text_match: number;
  note: string;
}

// Faz 4.5 (31 Temmuz 2026) — tenant-kendi-hizmeti DB bağlama sihirbazı.
export interface TenantConnectionCreateInput {
  datasource?: string; // yalnız "postgres" desteklenir bu sürümde
  host: string;
  port?: number;
  database: string;
  user: string;
  password: string;
}

export interface TenantConnectionOut {
  id: string;
  datasource: string;
  host: string;
  port: number;
  database: string;
  user: string;
  has_secret: boolean;
}

export interface ConnectionTestResult {
  ok: boolean;
  detail?: string | null;
}

export interface DraftCube {
  name: string;
  include: boolean;
  measures: string[];
  dimensions: string[];
  time_dimensions: string[];
  primary_key?: string | null;
}

export interface DraftRelationship {
  name: string;
  join_type: string;
  models: string[];
  condition: string;
}

export interface ConnectionDraft {
  cubes: DraftCube[];
  relationships: DraftRelationship[];
}

export interface ConnectionConfirmResult {
  written_cubes: string[];
  written_relationships: number;
}

// Faz 4.10 (1 Ağustos 2026) — dış yol haritası 2.5+2.15 "dallı kök-neden analizi".
// Kullanıcı senaryosu: bir metrik düşük/yüksek çıktığında NEDEN olduğunu bulmak için
// tıklaya tıklaya dallanıp GERÇEK verilerle (ilişkili cube'lar dahil) en alttaki ham
// satırlara kadar inebilmek.
export interface DrillDimension {
  name: string;
  label: string;
}

export interface DrillAnomaly {
  value: string;
  amount: number;
  direction: "above" | "below";
  z_score: number;
}

export interface DrillRelatedCube {
  cube: string;
  label: string;
  shared_dimensions: string[];
}

export interface DrillKpiComponent {
  name?: string | null;
  label: string;
  value?: number | null;
  unit?: string | null;
}

export interface RawRowResult {
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
}

export type DrillAction = "explain" | "expand" | "select" | "raw" | "related";

export interface DrillRequestInput {
  cube_query: CubeQuery | null;
  result?: QueryResult | null;
  kpi?: Record<string, unknown> | null;
  session_id?: string | null;
  action: DrillAction;
  dimension?: string | null;
  filter_value?: string | null;
  target_cube?: string | null;
  limit?: number;
}

export interface DrillResponse {
  cube_query: CubeQuery | null;
  formula_explanation: string;
  available_dimensions: DrillDimension[];
  related_cubes: DrillRelatedCube[];
  anomalies: DrillAnomaly[];
  result: QueryResult | null;
  raw_rows: RawRowResult | null;
  kpi_components: DrillKpiComponent[] | null;
  contract_id?: string | null;
  note?: string | null;
  // Doğrulama düzeltmesi (1 Ağustos 2026) — dış yol haritası UC-2.18/2.19 "kanıt paneli":
  // bu adımı üreten GERÇEK SQL + çalışma süresi (ms). `explain` yeni sorgu çalıştırmadığından
  // duration_ms orada null'dır ama sql yine de (derlenmiş, çalıştırılmamış olarak) doludur.
  sql?: string | null;
  duration_ms?: number | null;
}

// Faz 4.13c (1 Ağustos 2026) — son-kullanıcı meta-güven özeti (GET /stats/today).
export interface StatsToday {
  total: number;
  llm_free: number;
  llm_free_pct: number | null;
  message: string;
}
