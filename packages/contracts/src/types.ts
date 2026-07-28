/**
 * ELLE YAZILAN sözleşme parçaları.
 *
 * Buradaki her tip, backend'in `dict[str, Any]` ile geçtiği bir alanın
 * kullanılabilir şeklidir. Codegen bunları üretemez — ürettiği şey
 * `Record<string, never>` olur ki bu "hiç anahtar kabul etmeyen nesne"
 * demektir; işe yaramaz değil, doğrudan yanlıştır.
 *
 * KURAL: bu dosya YALNIZ backend'in tiplemediği şeyleri içerir. Backend bir
 * alanı düzgün tiplediği anda karşılığı buradan SİLİNİR ve `generated.ts`'ten
 * gelir. Aksi halde ikinci bir doğruluk kaynağı oluşur — kaçındığımız şeyin ta
 * kendisi.
 *
 * Yapısal alanlar için: bkz. generated.ts (üretilmiş, elle düzenlenmez).
 */

/** Sonuç satırı — backend `dict[str, Any]`. */
export type Row = Record<string, unknown>;

/** Cube sorgu durumu — backend `dict[str, Any]`. Takip mesajlarında geri gönderilir. */
export type CubeQuery = Record<string, unknown>;

/** `SchemaResponse.cubes` öğesi — backend `list[dict[str, Any]]`. */
export interface CubeMeta {
  name: string;
  measures?: string[];
  dimensions?: string[];
  time_dimensions?: string[];
  // Türev boyutlar dahil olası değerler (chip alternatifleri): {hafta_gunu: [Pzt..Paz]}
  dimension_values?: Record<string, string[]>;
}

/**
 * EVRENSEL ÇIKTI YORUMU (feature flag: cikti_yorumlama) — backend
 * `dict[str, Any]`. Her tablo/grafik/rapor/KPI için DETERMİNİSTİK, data-güdümlü
 * yorum; metin LLM'den değil veriden üretilir.
 */
export interface Interpretation {
  summary: string; // deterministik Türkçe özet (en yüksek/düşük, % değişim, trend, pay)
  facts?: { type: string; text: string }[]; // yapısal bulgular (chip/rozet)
}

/**
 * Cross-cube KPI kartı (CCC / likidite oranları) — backend `dict[str, Any]`.
 * Tek skaler + bileşenleri (DSO/DIO/DPO…). Cube tablosu değil bileşke.
 */
export interface KpiCard {
  kpi: string;
  label: string;
  unit?: string | null;
  lower_is_better?: boolean;
  formula?: string | null;
  explain?: string | null;
  value: number | null;
  components: KpiComponent[];
  // Dönem-serisi ("aylara göre ccc"): her kova için KPI değeri + bileşenleri
  // (CCC → DSO/DIO/DPO). Evrensel kova (gün/hafta/ay/çeyrek/yıl);
  // value = SON dönem (as-of başlık).
  granularity?: string | null;
  series?: { bucket: string; value: number | null; components?: KpiComponent[] }[] | null;
}

export interface KpiComponent {
  key: string;
  label: string;
  unit?: string | null;
  value: number | null;
}
