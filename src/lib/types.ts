// dima-backend response/request types (kept in sync with app/schemas.py).

export interface ColumnMeta {
  name: string;
  type: string;
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

export interface SchemaResponse {
  catalog: string | null;
  schema_name: string | null;
  models: ModelMeta[];
  relationships: RelationshipMeta[];
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
