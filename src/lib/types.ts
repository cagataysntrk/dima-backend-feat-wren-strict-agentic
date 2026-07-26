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
}

export interface Interpretation {
  summary: string; // deterministik Türkçe özet (en yüksek/düşük, % değişim, trend, pay)
  facts?: { type: string; text: string }[]; // yapısal bulgular (ileride chip/rozet)
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
