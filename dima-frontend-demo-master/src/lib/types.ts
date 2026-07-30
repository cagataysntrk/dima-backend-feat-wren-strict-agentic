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
  // Sohbet oturumu kimliği — kalıcı logda chat'i gruplamak için.
  session_id?: string;
}
