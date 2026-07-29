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
  // K3 (rehberli analitik) — PROAKTİF sinyaller: anomali (z-score) / yön endişesi
  // (lower_is_better ölçü artıyor) / yoğunlaşma (tek kalem payı ≥%50). Nötr
  // özetten AYRI tutulur çünkü dikkat çekmesi gerekir; önem düzeyine göre vurgulanır.
  signals?: Signal[];
}

export interface Signal {
  severity: "info" | "warning" | "critical";
  kind: string; // anomaly | trend | concentration — FE ikon/gruplama için
  text: string;
}

/* ─────────────────────────────────────────────────────────────────────────────
 * CEO DEMO — HENÜZ BACKEND'DE OLMAYAN YETENEKLER
 *
 * Aşağıdakiler `dima-backend` HEAD'de YOK. Sözleşmesi
 * `docs/contracts/ceo-demo.md`'de yazılı; backend o şekle göre yazılınca
 * bu bloklar SİLİNİR ve karşılıkları `generated.ts`'ten gelir — types.ts'in
 * kuralı bu (yalnız backend'in tiplemediği şeyler burada durur).
 *
 * Şimdiden yazılmalarının sebebi: ekranlar bir şekle bağlanmak zorunda ve o şekli
 * iki tarafın ayrı ayrı icat etmesi entegrasyonda çakışır.
 * ────────────────────────────────────────────────────────────────────────────*/

/** Rapor bölümü (D12/D34/D62). `commentary` AYRI alan — ekranda "yorumdur"
 *  etiketiyle işaretlenir; sayı içermez, sayılar `body`/`result`'tan gelir. */
export interface ReportSection {
  title: string;
  body?: string | null;
  commentary?: string | null;
  result?: unknown | null; // QueryResult — index.ts'te daraltılır
  cube_query?: CubeQuery | null;
  view_hint?: string | null;
}

export interface Report {
  title: string;
  period_resolved?: string | null;
  sections: ReportSection[];
  contract_id?: string | null;
  generated_at: string;
}

/** Analizin tek iddiası (D44/D47/D63). Her iddia kanıta bağlıdır: `evidence`
 *  tıklanınca `/cube` ile koşan cube_query'dir. */
export interface AnalysisClaim {
  text: string;
  kind: "strength" | "weakness" | "opportunity" | "threat" | "action" | (string & {});
  metric?: string | null;
  value?: number | null;
  unit?: string | null;
  evidence?: CubeQuery | null;
  /** deterministic = katalogdan hesaplandı · estimated = referans parametreli
   *  · model = LLM üretti. Demo kuralı: `estimated` varsa `assumptions` DOLU olmalı. */
  confidence: "deterministic" | "estimated" | "model" | (string & {});
}

export interface Analysis {
  kind: "swot" | "scorecard" | "plan" | "risk" | "breakeven" | (string & {});
  title: string;
  summary: string;
  claims: AnalysisClaim[];
  /** Tahmin/projeksiyon içeren analizin parametreleri — boşsa tahmin gösterilmez. */
  assumptions?: string[];
  contract_id?: string | null;
}

/** Sözle kurulan kalıcı tercih (D30/D58). */
export interface Preference {
  id: string;
  scope: "default_period" | "currency" | "granularity" | "summary_style" | (string & {});
  value: string;
  source_question: string;
  created_at: string;
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
