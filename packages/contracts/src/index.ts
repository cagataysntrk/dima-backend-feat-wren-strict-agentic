/**
 * dima-backend HTTP sözleşmesi.
 *
 * Bu paket React, DOM ve Node tanımaz — mobil (React Native) tarafı da aynı
 * tipleri kullanacak. Kural `@dima/eslint-config/platform-free` ile lint'te
 * zorlanır.
 *
 * İKİ KAYNAK, TEK YÜZEY:
 *
 *   generated.ts   backend'in app/schemas.py'sinden ÜRETİLİR. Yapı buradan
 *                  gelir; elle düzenlenmez. `codegen:check` CI'da güncelliğini
 *                  doğrular — "backend değişti, frontend güncellenmedi" durumu
 *                  artık sessiz kalmaz.
 *
 *   types.ts       YALNIZ backend'in `dict[str, Any]` bıraktığı alanların
 *                  kullanılabilir şekilleri.
 *
 * Aşağıdaki daraltmalar ZORUNLU, kozmetik değil: openapi-typescript,
 * özelliksiz bir `object` şemasını `Record<string, never>` diye üretiyor — yani
 * "hiçbir anahtar kabul etmeyen nesne". Daraltmasak `result.rows[0].ay`
 * derlenmezdi.
 *
 * Backend bu alanları düzgün tiplediği gün, buradaki daraltma ve types.ts'teki
 * karşılığı SİLİNİR; generated.ts tek kaynak olur.
 */

import type { components } from "./generated";
import type { CubeMeta, CubeQuery, Interpretation, KpiCard, Row } from "./types";

type Schemas = components["schemas"];

/**
 * İSTEK gövdeleri için opsiyonellik düzeltmesi.
 *
 * openapi-typescript, varsayılanı olan alanları ZORUNLU üretiyor: Pydantic'te
 * `limit: int | None = None` olan alan `limit: number | null` çıkıyor, `limit?`
 * değil. Bu YANITLAR için doğrudur — sunucu varsayılanı doldurup gönderir. Ama
 * İSTEKLER için yanlıştır: istemci o alanı atlar, sunucu doldurur.
 *
 * Bunu bir üretim bayrağıyla kapatmak yanlış olurdu; ikisi gerçekten farklı
 * yönler ve tek şema iki yönü de anlatıyor. Zorunlu olanları burada açıkça
 * yazıyoruz — şemadaki `required` listesiyle aynı.
 */
type RequestOf<T, RequiredKeys extends keyof T> = Pick<T, RequiredKeys> &
  Partial<Omit<T, RequiredKeys>>;

// --- Elle yazılanlar (backend tiplemiyor) -----------------------------------
export type { CubeMeta, CubeQuery, Interpretation, KpiCard, KpiComponent, Row } from "./types";

// --- Üretilenler: olduğu gibi kullanılabilenler ------------------------------
export type ColumnMeta = Schemas["ColumnMeta"];
export type ModelMeta = Schemas["ModelMeta"];
export type RelationshipMeta = Schemas["RelationshipMeta"];
export type Suggestion = Schemas["Suggestion"];
export type ConversationOut = Schemas["ConversationOut"];
export type ConversationDetail = Schemas["ConversationDetail"];
export type NextStep = Schemas["NextStep"];
export type Recommendation = Schemas["Recommendation"];
export type UploadResponse = Schemas["UploadResponse"];

// --- Üretilenler: `dict[str, Any]` alanları daraltılmış ----------------------

export type QueryResult = Omit<Schemas["QueryResult"], "rows"> & {
  rows: Row[];
};

export type SchemaResponse = Omit<Schemas["SchemaResponse"], "cubes"> & {
  cubes?: CubeMeta[];
};

// --- İstekler: zorunlu alanlar şemadaki `required` ile aynı -----------------

export type QueryRequest = RequestOf<Schemas["QueryRequest"], "sql">;

// Tüm alanları zorunlu — daraltmaya gerek yok.
export type UploadRequest = Schemas["UploadRequest"];

export type AskRequest = RequestOf<Omit<Schemas["AskRequest"], "cube_query">, "question"> & {
  cube_query?: CubeQuery | null;
};

export type CubeRequest = RequestOf<Omit<Schemas["CubeRequest"], "cube_query">, never> & {
  cube_query: CubeQuery;
};

export type AskResponse = Omit<
  Schemas["AskResponse"],
  "result" | "cube_query" | "kpi" | "interpretation"
> & {
  result: QueryResult | null;
  // Rapor cube ile üretildiyse yapısal durum — takip mesajlarında geri gönderilir (ADR-0007).
  cube_query: CubeQuery | null;
  kpi?: KpiCard | null;
  interpretation?: Interpretation | null;
};

// Üretilen ham tiplere erişim (nadir; daraltılmamış hali gerektiğinde).
export type { components as BackendSchemas } from "./generated";
