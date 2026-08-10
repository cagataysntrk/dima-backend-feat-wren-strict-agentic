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

// Bir kırılımın KÖKENİ (Faz 1.1) + fan-out SERTİFİKASI (Faz D2). Yalnız ilişki-türevi
// boyutlar için doludur — yerel boyutlarda sözlükte hiç yer almaz ("bu join'den mi geldi"
// sorusu her boyut için "evet" olmasın diye).
export interface DimensionOrigin {
  model: string;         // boyutun geldiği tablo (ör. "makineler")
  column: string;        // o tablodaki kolon
  relationship: string;  // hangi ilişki üzerinden
  hops: number;          // kaç sıçrama
  // "olculdu:saglikli" | "olculdu:riskli" | "olculmedi".
  // ÖLÇÜLMEDİ ≠ TEMİZ: sertifika üretilmemişse temiz olduğu İDDİA EDİLMEZ.
  certified?: string;
}

export interface CubeMeta {
  name: string;
  measures?: string[];
  dimensions?: string[];
  time_dimensions?: string[];
  // Türev boyutlar dahil olası değerler (chip alternatifleri): {hafta_gunu: [Pzt..Paz]}
  dimension_values?: Record<string, string[]>;
  dimension_origin?: Record<string, DimensionOrigin>;
}

export interface SchemaResponse {
  catalog: string | null;
  schema_name: string | null;
  models: ModelMeta[];
  relationships: RelationshipMeta[];
  cubes?: CubeMeta[];
  db_online?: boolean; // veri kaynağı TCP erişilebilir mi → çevrimiçi/çevrimdışı rozeti
  /** FAZ 1.11 — kademeli düşüş: 1=birincil LLM · 2=yedek · 3=LLM YOK (kural tabanlı).
   *
   * ⚠ Seviye 3 bir HATA DEĞİL bir DURUMDUR: sistem çalışıyor ama cevaplar KATEGORİK
   * OLARAK farklı bir yoldan geliyor. Rozet bunu "çevrimdışı" gibi göstermemeli —
   * "çalışıyor ama LLM yok" ile "hiç çalışmıyor" AYNI ŞEY DEĞİLDİR.
   *
   * 🔴 Seviye kararı BACKEND'de (`app/kademeli_dusus.py`); burada ikinci bir
   * sınıflandırma yazmak rozet ile audit'in AYRIŞMASI demekti. `undefined` = bilgi yok,
   * rozet bugünküyle birebir aynı. */
  llm_seviye?: 1 | 2 | 3 | null;
  llm_seviye_etiket?: string | null;
  llm_uretici?: string | null;
}

export type Row = Record<string, unknown>;

export interface QueryResult {
  columns: string[];
  rows: Row[];
  row_count: number;
}

export type CubeQuery = Record<string, unknown>;

// FAZ 4 (K3) — AJAN KOŞUM MAKBUZU. Planlayıcı bir cevabı NASIL ürettiğini söyleyemezse
// "LLM garson oldu" bir BEYAN olarak kalır. Bu yapı onu DENETLENEBİLİR kılar: hangi
// araçlar, hangi sırayla, kaç ms, hangi adım REDDEDİLDİ, bütçe kısıldı mı.
// Reddedilen adımlar da listede kalır — bütçe tüketildi ve kullanıcı neyin DENENDİĞİNİ
// görebilmeli. Yalnız planlayıcıdan geçen cevaplarda dolu; diğerlerinde null (uydurulmaz).
export interface AgentRun {
  steps: {
    tool: string;
    determinism: string;
    ms: number;
    receipt?: string | null;
    error?: string;      // kapı reddi de dahil — "SEÇİM REDDİ" / "DETERMİNİSTİK-ÖNCE"
    gated?: boolean;     // false = kayıtsız (bileşik) adım, itiraf edilmiş
    note?: string;
  }[];
  step_count: number;
  query_count: number;
  truncated: boolean;
  truncation_reason?: string | null;
}

export interface AskResponse {
  // 🔴 FAZ 5.17 — TEK SES. `app/soz.py` katalogundan gelen metin: tek hitap kipinde,
  // jargonsuz ve *"önce ne anladığını söyle, sonra sor"* şeklinde.
  //
  // ⚠ `note` YENİDEN KULLANILMADI: bugün DÖRT anlam taşıyor (dürüst ret · netleştirme ·
  // kırpılma uyarısı · upload bildirimi) ve kalıcı `payload_json` geçmişi ona bağlı.
  // Okuma her zaman `soz ?? note` → **eski kayıtlar aynen çalışır**.
  soz?: string | null;
  // 🔴 FAZ 5.12 — İÇGÖRÜ PAKETİ: aynı sonucun BİRDEN ÇOK EKSENİ; her üye "neden bu
  // eksende" gerekçesini (`neden`) taşır.
  //
  // ⚠ `viz` alanı DEĞİŞMEZ ve paket ayrı durur: bayrak kapalıyken bu alan `null` kalır
  // ve tekil kart BUGÜNKÜ hâliyle görünür. *Tekil dönüş her zaman geçerlidir.*
  viz_paketi?: (VizSpec & { neden?: string })[] | null;
  // 🔴 FAZ 5.13a — HAYALET SERİ: aynı sorgunun BİR ÖNCEKİ koşumu.
  //
  // ⚠ Ham sonuç TAŞIMAZ (sonuç zaten spool'lanmıyor — KVKK + boyut) ve onu uydurmak
  // olmayan bir veriyi varmış gibi göstermek olurdu. *Hayalet seri bir KARŞILAŞTIRMA
  // sinyalidir, ikinci bir cevap değil* — bu yüzden UI'da bir grafik değil, bir SATIR.
  previous_result?: {
    contract_id: string;
    ts: string | null;
    row_count: number | null;
    result_hash: string | null;
  } | null;
  // FAZ 5.13b — kural motorunun EK BAĞLAMI. 🔴 Bu metin SQL'e HİÇ dokunmaz; kullanıcının
  // kendi yazdığı bilgidir ve öyle GÖSTERİLİR (sistemin hesabı gibi değil).
  kural_baglami?: string | null;
  /** 🔴 KÖK-2/KÖK-3 — **BEYANLI KISMİ CEVAP.** Sorudaki hangi niyet işaretleri sorguya
   *  TAŞINAMADI: `kiyas` · `cok_donem` · `trend` · `kirilim` · `ustunluk` · `esik` ·
   *  `dislama`. Boş/`null` = sorunun tamamı karşılandı.
   *
   *  ⚠ Bu alan **render EDİLMEK ZORUNDA**: rapor bunu *"arka-ön dikey dilim"* diye
   *  yazıyor — *etiket üretilip render edilmezse hiçbir şey değişmez*. Yetim-alan
   *  kapısı (`test_cevap_alani_yetim_degil.py`) bunu ilk günde yakaladı. */
  eksik_niyet?: string[] | null;
  // 🔴 FAZ 6.0 — D9: YAPILDI BİLDİRİMİ. Kapsam içi + geri alınabilir bir eylem İSTEMSİZ
  // koştuğunda dolar.
  //
  // ⚠ `eylem_onerisi` ile AYNI ANDA DOLAMAZ: bir iş ya YAPILDI ya ONAY BEKLİYOR. İkisini
  // birden göstermek, kullanıcıya "hem oldu hem olmadı" demektir.
  eylem_sonucu?: {
    eylem: string;
    id: string | null;
    not: string | null;
    // Geri alınabilirliği ilan edip YOLUNU göstermemek, onu bir temenniye çevirir.
    geri_al: string | null;
  } | null;
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
  /** Tıklanır chip. `kind` FE gruplaması içindir (KÖK-9):
   *  - undefined → DEVAM SORUSU (bu cevabın üstünde konuşur, yeni sorgu yazmaz)
   *  - "tanim"   → BELİRSİZLİK chip'i: aynı soruyu BAŞKA BİR TANIMLA yeniden sorar.
   *                🔴 Devam sorusu kutusuna KONAMAZ — o kutunun açıklaması
   *                ("yeni sorgu yazılmaz") bunun için yanlış olurdu.
   *  - "turetme" → TÜRETME chip'i (KÖK-7d): kullanıcı FİİL kurdu ("ne kadar sattık"),
   *                katalogda İSİM var ("satış"). Bir REDDİN yanında durur, yani bir
   *                cevabın devamı değil bir DÜZELTME önerisidir. */
  suggestions?: { label: string; query: string; kind?: string }[];
  /** FAZ 1.7 — tazelik kademesi: `taze | uyari | hata | bilinmiyor`.
   *
   * 🔴 `hata` VE `bilinmiyor`'da SAYI GÖSTERİLMEZ (B4: bilinmeyen tazelik TAZE DEĞİLDİR).
   * Kademe kararı BACKEND'de (`app/tazelik.py`); burada ikinci bir eşik kümesi yazmak
   * "aynı kuralın iki sahibi" olurdu ve ikisi ayrışınca kullanıcı bayat bir sayıyı
   * normal görürdü. `undefined` = bayrak kapalı → davranış birebir bugünkü. */
  freshness?: "taze" | "uyari" | "hata" | "bilinmiyor" | null;
  son_veri_ts?: string | null;
  tazelik_aciklama?: string | null;
  // Görünüm isteği ("grafik ver") — client mevcut raporun görünümünü değiştirir.
  view_hint?: string | null;
  // FAZ 4 — ajan koşum makbuzu (yalnız planlayıcıdan geçen cevaplarda dolu).
  agent_run?: AgentRun | null;
  // §B (Madde 4+6, 1 Ağustos 2026): bu mesaj YENİ bir konu mu (True) yoksa önceki raporun
  // takibi mi (False) — backend'in zaten hesapladığı is_followup'ın tersi. SALT
  // BİLGİLENDİRİCİ bir kart-başı breadcrumb'tır (ReportCard). §B DÜZELTMESİ (1 Ağustos
  // 2026): İLK sürümde bu alan YANLIŞLIKLA thread sınırı (yeni panel mi açılsın) kararına
  // da karıştırılmıştı — kullanıcı reddetti. ARTIK hiçbir thread-mantığına KARIŞMAZ; thread
  // sınırları YALNIZCA kullanıcının hangi komposer'ı kullandığına bağlıdır (bkz. page.tsx
  // AskMutationVars). `/cube` (chip düzenlemesi) hiç set etmez → varsayılan false doğru kalır.
  is_new_topic?: boolean;
  // §B (1 Ağustos 2026) — body.thread_id'nin AYNEN echo'su (bkz. AskRequest.thread_id).
  // Frontend bunu görüp KENDİ thread modelini (lib/threads.ts::groupIntoThreads) kurar.
  thread_id?: string | null;
  // §B düzeltmesi (1 Ağustos 2026) — bkz. backend AskResponse.reply_to_label: body'nin
  // aynen echo'su. Doluysa ReportCard bunu "◆ yeni konu"/"↳ önceki raporun devamı"
  // breadcrumb'ının YERİNE öncelikli gösterir ("↳ yanıt: {etiket}").
  reply_to_label?: string | null;
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
  // KONUŞMA CEVABININ GÖVDESİ (Faz G1). "bu neden böyle?" gibi bir takip sorusuna verilen
  // cevabın İÇERİĞİ budur — `next_steps` DEĞİL. Bulgular next_steps'e konulduğunda UI
  // onları "SONRAKİ ADIM" başlığıyla gösteriyordu ve Δ tutarları / % paylar / kırpma
  // uyarısı kayboluyordu (ölçüldü). Doluysa ReportCard `ContributionLayer`'ı HAZIR VERİYLE
  // render eder — aynı bileşen, ikinci bir istek YOK.
  contribution?: ContributionResponse | null;
  // REÇETE (Faz G3) — YALNIZ "ne yapmalıyız?" sorulduğunda dolar. "Bu neden böyle?"
  // bir AÇIKLAMA ister, reçete değil; ikisini karıştırmak kullanıcının SORMADIĞI bir
  // tavsiyeyi cevabın yerine koymak olurdu.
  prescription?: Prescription | null;
  // Faz 3 (31 Temmuz 2026) — birleşik açıklama: `trace`/`source`'un ÜSTÜNE biner, onları
  // SİLMEZ (SourceBadge/trace render'ı kırılmaz — kademeli geçiş). Rapor üretmeyen yanıtlarda
  // (netleştirme/chip) null.
  explain?: Explain | null;
  // 🔴 G0b — HAVA BOŞLUĞU makbuzu. Gerçek boyut değerleri ve sayılar sağlayıcıya
  // YER TUTUCU olarak gider (`{{DIM_1}}` · `{{NUM_1}}`); model bir rakam ÜRETEMEZ,
  // yalnız verdiğimiz yuvayı taşıyabilir. `bozulan` > 0 ise model yuvayı bozmuş ya da
  // UYDURMUŞ demektir. ⚠ Yalnız SAYI taşır — hangi değerin perdelendiği asla gelmez.
  hava_boslugu?: {
    yer_tutucu: number; bozulan: number; iddia_dusen?: number;
    // 🔴 `DA-4` — anlatı guard'ının makbuzu. `narration_guard.Rapor.makbuza()` yazılmıştı
    // ve **hiçbir yerden çağrılmıyordu**: `G5.4`'ün *"muafiyetler GÖRÜNÜR olur"* kazancı
    // yalnız log'a gidiyordu. `guard_muaf` iki sınıfı adlandırır (`yil` aralığı ·
    // `sira_esigi`) — *bir muafiyeti gizlemek, onu bir garanti gibi göstermenin en kısa
    // yoludur.*
    anlati_dogrulandi?: boolean; anlati_dusen?: number;
    guard_muaf?: { yil?: number[]; sira_esigi?: number } | null;
  } | null;
  // 🔴 G1 — TEMELLENDİRME: *"anladığım şu"*. Kaynağı YALNIZ `cube_query` — anlatı değil
  // MUHASEBE; 0 LLM · 0 token, yani LLM düşse bile gelir. ⚠ `explain` ile karıştırma:
  // o **yol** (hangi basamak), bu **anlam** (ne anlaşıldı).
  temellendirme?: {
    cube?: string; olcu?: string; donem?: string; granulerlik?: string;
    kirilim?: string[]; filtreler?: string[];
    // 🔴 `G6.3` — KIYAS. Makbuz bunu SÖYLEMİYORDU: `compare` uçtan uca akıyor, grafik
    // çiziyor, chip düzenliyor — ama *"ne anladım"* muhasebesinde hiç yoktu. `referans`
    // varsa iki UÇ yazılır (`2026-03 ↔ 2026-02`), yoksa modun insan okunuşu.
    // ⚠ Bayrağa bağlı (`referans_dili`): kapalıyken alan HİÇ gelmez.
    kiyas?: string;
  } | null;
  // 🔴 G2 — DİYALOG DURUMU. Sunucu oturum SAKLAMAZ; bu nesne cevapta gelir ve istemci
  // bir sonraki isteğe YANKILAR (`cube_query` ile aynı desen). JPMorgan 2026: tur-3
  // durumsuz %0, iki turluk pencereyle %87,6-100 — durum taşımak var olma koşuludur.
  diyalog_durumu?: DiyalogDurumu | null;
  // Madde 12 (1 Ağustos 2026) — düz-dil hesaplama açıklaması (KPI-olmayan cube raporları için;
  // KpiCard'ın `card.explain`iyle AYNI amaç). `explain` (yukarıda) ile KARIŞTIRILMAMALI — o
  // provenance/güven taşır, bu alan ÖLÇÜNÜN NASIL HESAPLANDIĞINI anlatır. cube_query yoksa null.
  calculation_explanation?: string | null;
  // Faz 4.1 (31 Temmuz 2026) — yalnız backend'de `ask_async_discovery` bayrağı açıkken dolar:
  // Discovery arka-plan işine kuyruklandığında (result/source HENÜZ yok). `api-client.ts::ask()`
  // bunu GÖRÜNMEZ şekilde poll'lar (mutation.isPending zaten doğru davranır) — normal şartlarda
  // bu alan bileşenlere HİÇ ULAŞMAZ, yalnız api-client içinde tüketilir.
  job_id?: string | null;
  // FAZ H — ONAYLI YAZMA. Ajan yazma aracını ÇALIŞTIRMAZ; bir ÖNERİ üretir ve kullanıcı
  // onaylar. Alan doluyken `sql`/`result` BOŞTUR (eylem ifadesi veri sorusu değildir).
  // `izin` alanı UI'ın düğmeyi göstereceği yetkiyi söyler — rol matrisi UI'a KOPYALANMAZ,
  // /auth/me `permissions` listesiyle karşılaştırılır (CLAUDE.md kuralı).
  eylem_onerisi?: EylemOnerisi | null;
  // FAZ S · STEERING — **İSTEMCİ TARAFINDA** set edilir (backend BU ALANI GÖNDERMEZ).
  // Kullanıcı, bu cevap hazırlanırken yeni bir soru sordu: cevap KAYBOLMAZ (geçmişe
  // yazılır) ama aktif bağlamı ele geçirmez. Kart bunu okur ve okuyucuya söyler —
  // sessizce göstermek "neden eski rapor geri geldi?" sorusunu doğururdu.
  steering_golgede?: boolean;
  /** FAZ 1.12 · AI Act Md.50 — bu cevabın ANLATISI makine üretimi mi?
   *
   * 🔴 SAYI DEĞİL, ÜSLUP işaretlenir: sayıyı her zaman küp koyar ve `narration_guard`
   * eşleşmeyen sayı taşıyan cümleyi DÜŞÜRÜR. İşaretlenen şey, metnin makine tarafından
   * yazıldığıdır. `false` (varsayılan) → gösterilecek bir şey yok. */
  ai_generated_prose?: boolean;
  /** FAZ 1.12 — KANIT SINIFI: `olculmus` | `probabilistik`.
   *
   * ⚠ Skaler bir "güven" DEĞİL (MIMARI §5: kalibre edilmemiş sayı güven değil süstür);
   * bir KATEGORİ. `cube+llm`'de sayı küpten gelse bile alan SEÇİMİ olasılıksaldır —
   * seçim yanlışsa doğru sayı YANLIŞ SORUYA cevap olur. Karar backend'de (`answer.seal`);
   * burada ikinci bir sınıflandırma yazmak "aynı kuralın iki sahibi" olurdu. */
  kanit_sinifi?: "olculmus" | "probabilistik";
  /** FAZ 2.6 — MALİ YIL PENCERESİ. Yalnız mali yıl takvim yılından FARKLIYSA dolar.
   *
   * 🔴 Takvim yılından farklı bir pencereyi "bu yıl" diye sunmak, DOĞRU sayıyı YANLIŞ
   * soruya cevap yapar. Takvim yılı kullanan tenant'ta `null`: gürültü üretmez, yalnız
   * fark varken konuşur. Pencere kararı backend'de (`app/mali_takvim.py`). */
  mali_donem?: string | null;
  /** FAZ 2.5 — HEDEF KIYASI. Yalnız cube'da `target:` BEYAN EDİLMİŞSE dolar.
   *
   * 🔴 **HEDEF UYDURULMAZ:** beyan yoksa `null` ve grafikteki çizgi bugünkü anlamını
   * (ortalama) korur. "Hedef yok" ile "hedef 0" asla karıştırılmaz — sıfır hedef
   * ULAŞILMIŞ bir hedeftir, hedefsizlik ise ÖLÇÜLEMEZLİKTİR.
   * `sapma_yuzde` sıfır hedefte `null`: tanımsızlığı ölçüm gibi göstermeyiz. */
  hedef?: {
    olcu: string;
    hedef: number;
    gerceklesen: number;
    yon: "yuksek_iyi" | "dusuk_iyi";
    ulasildi: boolean;
    sapma_yuzde: number | null;
  } | null;
  /** 🔴🔴 FAZ 6 — ÇOK ADIMLI CEVABIN YAPISI.
   *
   * `agent_run` ile KARIŞTIRILMAZ: o bir **denetim izidir** (geriye dönük, adım başına
   * sonucu yok, makbuzun içinde). Bu **cevabın kendisidir**: kaç parçadan oluştu, her
   * parça hangi sorgudan geldi.
   *
   * 🔴 Her bölüm kendi `cube_query`'sini taşır ki kart `POST /cube` ile **sıfır LLM**
   * yeniden koşulabilsin — `onCubeEdit` zaten kurulu, yeni bir uç gerekmiyor.
   *
   * `null` = tek adımlı bugünkü cevap. */
  plan?: {
    adimlar: { sira: number; fiil: string; ozet: string }[];
    bolumler: { cube_query: Record<string, unknown> | null; result: QueryResult | null }[];
  } | null;
  /** 🔴🔴 `§RP` — **AGENTIC RAPOR/PANO: çok bölümlü BELGE.**
   *
   * Orkestratörün planı `RAPOR`/`PANO` fiili taşıyorsa, koşmuş bölümler backend'de
   * `Report` biçimine dizilir (`report.bolumlerden_kur`) ve burada gelir.
   *
   * ⚠ `plan.bolumler` ile karıştırılmaz: o **ham** bölümlerdir (başlıksız, viz'siz);
   * bu, `ReportView`'in çizebildiği **belgedir** (kapak · yönetici özeti · sayfalar).
   * ⚠ Ve `viz_paketi` ile de karıştırılmaz: o **tek bir sonucun** birden çok grafiği.
   *
   * `null` = bu cevap bir belge değil. */
  rapor?: Report | null;
}

// Faz 4.1 — GET /ask/jobs/{id} yanıtı (yalnız api-client.ts::ask()'in dahili poll döngüsü kullanır).
// `trace` (Faz 4.12) iş HENÜZ tamamlanmadan da (pending/running) BİRİKEREK dolar.
export interface AskJobStatus {
  id: string;
  // `cancelled` (FAZ 1.12, AI Act Md.14) — kullanıcı DURDURDU. `failed` DEĞİLDİR:
  // kendi bastığı düğmenin sonucunu "sorun oluştu" diye okumak yanlış olurdu.
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
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
  /** 🔴 **FAZ 7.3(k) / B8 — ZİNCİR BAĞLANDI.**
   *
   * Bu alan **tipte bile yoktu**, oysa `schemas.py::Explain.sertifika` FAZ 1.5'ten beri
   * vardı ve `sertifikaRozeti()` (ChatPanel) onu okumak için yazılmıştı. Ölçüldü:
   * tablo → `certification.py` → `Explain.sertifika` → rozet — **dört halka da vardı,
   * hiçbiri diğerine dokunmuyordu.**
   *
   * `path`/`confidence` *"bu cevap hangi yoldan geldi"* der; `sertifika` **başka bir
   * soruya** cevap verir: *"bu metriğin TANIMINI kim onayladı ve o onaydan beri ne
   * değişti?"* Bir metrik **doğru hesaplanıp yanlış tanımlanmış** olabilir ve
   * determinizm onu yakalamaz.
   *
   * ⚠ `kademe` backend'de hesaplanır (`sertifika_okuma.blok`): rozet kademesi bir
   * **karardır** ve iki sahibi olursa ayrışır. Arayüz yalnız **gösterir**.
   */
  sertifika?: {
    seviye?: string | null;
    kademe?: string | null;
    gecerli?: boolean;
    yeniden_dogrulama_gerekli?: boolean;
    otomatik_iptal_nedeni?: string[] | null;
    sertifika_notu?: string | null;
    son_gecerlilik?: string | null;
    /** ⚠ Bilinen sınır, backend'den **taşınır**: çok ölçülü cevapta sertifika ilk
     *  ölçüden okunur; doğrusu en zayıf halkadır. */
    kisit?: string | null;
  } | null;
}

// VizSpec — backend viz.recommend() çıktısı (ADR-0024). FE `chart.ts` Analysis'ine adapte edilir.
export interface VizSpec {
  // 🔴 FAZ 5.11 (§15.6) — grafik ÇİZİLMEDİYSE **neden** çizilmediği. *Çizilmeyen bir
  // grafik, neden çizilmediğini söylemeli* — aksi hâlde kullanıcı ürünün onu
  // BECEREMEDİĞİNİ sanar. Dolu olduğunda `kind` `cumle` ya da `table`dır.
  cizilmedi?: string | null;
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
  reference_line: { kind: string; measure: string; value: number } | null;
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
  // FAZ 5 — T2 GUARDED LLM ANLATICI. `summary`'nin YERİNE GEÇMEZ, ÜSTÜNE biner:
  // LLM yalnız ÜSLUBU yazar, SAYIYI sistem koyar. Backend'de `narration_guard`'ın
  // fail-closed kapısından geçmiştir — her cümledeki her sayı sonuç kümesiyle eşlenmiş,
  // eşleşmeyen cümle DÜŞÜRÜLMÜŞTÜR. Alan YOKSA (bayrak kapalı · sağlayıcı `anlat`
  // taşımıyor · tüm cümleler guard'da düştü) deterministik `summary` tek başına
  // gösterilir — "süssüz ama doğru", asla "akıcı ama uydurma".
  narration?: string | null;
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
  /** 🔴 FAZ 5.10 — **KPI PİN**. `app/kpi_pin.py` (85 satır, 10 test) üretim kodunda
   *  **hiç import edilmiyordu**: semantik yazılmış, kolonu yokmuş, ekranı yokmuş.
   *  ⚠ Pin bir **katmandır, panel değil** (PK-1/K5): var olan widget'ın bir işareti.
   *  ⚠ Pinli widget'lar **üste** çıkar ve kendi aralarında oluşturma sırasını korur —
   *  sıralama `kpi_pin.sirala`'nın kararıdır, arayüz onu yeniden yazmaz. */
  pinned?: boolean;
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
  viz?: VizSpec | null;
  // KONUŞMA CEVABININ GÖVDESİ (Faz G1). "bu neden böyle?" gibi bir takip sorusuna verilen
  // cevabın İÇERİĞİ budur — `next_steps` DEĞİL. Bulgular next_steps'e konulduğunda UI
  // onları "SONRAKİ ADIM" başlığıyla gösteriyordu ve Δ tutarları / % paylar / kırpma
  // uyarısı kayboluyordu (ölçüldü). Doluysa ReportCard `ContributionLayer`'ı HAZIR VERİYLE
  // render eder — aynı bileşen, ikinci bir istek YOK.
  contribution?: ContributionResponse | null;
  // REÇETE (Faz G3) — YALNIZ "ne yapmalıyız?" sorulduğunda dolar. "Bu neden böyle?"
  // bir AÇIKLAMA ister, reçete değil; ikisini karıştırmak kullanıcının SORMADIĞI bir
  // tavsiyeyi cevabın yerine koymak olurdu.
  prescription?: Prescription | null; // ADR-0024: backend grafik/tablo/pivot kararı (chat ile aynı)
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
  // KONUŞMA CEVABININ GÖVDESİ (Faz G1). "bu neden böyle?" gibi bir takip sorusuna verilen
  // cevabın İÇERİĞİ budur — `next_steps` DEĞİL. Bulgular next_steps'e konulduğunda UI
  // onları "SONRAKİ ADIM" başlığıyla gösteriyordu ve Δ tutarları / % paylar / kırpma
  // uyarısı kayboluyordu (ölçüldü). Doluysa ReportCard `ContributionLayer`'ı HAZIR VERİYLE
  // render eder — aynı bileşen, ikinci bir istek YOK.
  contribution?: ContributionResponse | null;
  // REÇETE (Faz G3) — YALNIZ "ne yapmalıyız?" sorulduğunda dolar. "Bu neden böyle?"
  // bir AÇIKLAMA ister, reçete değil; ikisini karıştırmak kullanıcının SORMADIĞI bir
  // tavsiyeyi cevabın yerine koymak olurdu.
  prescription?: Prescription | null;
  error: string | null;
}

export interface Report {
  title: string;
  pages: ReportBlock[][];
  block_count: number;
  // 🔴 FAZ 5.13b — SABİT YAPI. Üçü de `pages`'in YANINDA durur, içinde değil: bir dışa
  // aktarıcı sayfaları atlasa/kırpsa/yeniden düzenlese bile kapak ve KAYNAK LİSTESİ
  // elinde kalır. *Bir kanıt, taşındığı kabın şekline bağlıysa kanıt değildir.*
  kapak?: { baslik: string; tarih: string; yazar: string | null };
  // Yönetici özeti `interpret()`'in olgularından DERLENİR — yeni bir anlatı motoru yok,
  // LLM çağrılmaz. Özet bir derlemedir, bir yorum değil.
  yonetici_ozeti?: string[];
  // 🔴 "PDF'e döküldüğünde bile `contract_id` altta kalır." `contract_id: null` bir
  // makbuzsuzluktur ve GÖSTERİLİR — kanıtın yokluğunu gizlemek, kanıtsızlıktan kötüdür.
  kaynaklar?: { blok: string; contract_id: string | null; cube: string | null }[];
  // ⊘ Bu formatlar depoda YOK; kapı onları ölçemiyor ve bunu ilan ediyor.
  olculemeyen_formatlar?: string[];
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

/** 🔴 `G2` — DİYALOG DURUMU. **İki yönlü**: sunucu cevapta döndürür, istemci bir
 * sonraki istekte **geri yollar**. Sunucu oturum SAKLAMAZ (`schemas.py:82-86`).
 *
 * ⚠ `kismi_cq` şarttır: `devam_edilebilir` **hem** `sorulan` **hem** `kismi_cq` ister
 * (`app/diyalog.py:133-141`). Tipte olmazsa yankıyı tipli nesneden kuran biri
 * kapattığını sanar ve yine `None` alır. */
export interface DiyalogDurumu {
  acik_slotlar: string[];
  sorulan?: string;
  dolu?: string[];
  tur_no: number;
  kismi_cq?: CubeQuery | null;
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
  // 🔴 `G2` — DİYALOG DURUMU YANKISI. Sunucu oturum SAKLAMAZ; durumu `cube_query`'nin
  // taşındığı gibi taşır: cevapta döner, istemci **geri yollar**
  // (`backend/app/schemas.py:82-86`).
  //
  // ⚠ **Bu alan bir demet boyunca EKSİKTİ ve `KURAL_DEVAM` üretimde HİÇ ateşlenmedi.**
  // Backend tarafı (`context.py::KURAL_DEVAM` · `diyalog.devam_edilebilir`) tamamen
  // yazılmış ve testliydi; tek eksik bu satırdı. Alanın backend'deki kendi şerhi kusuru
  // **önceden** yazmış: *"İstemci yankılamazsa bellek YOKTUR."*
  //
  // 🔴 Ve bu, hemen aşağıdaki `reply_to_cube_query` şerhinin anlattığı `KURAL_CAPA`
  // vakasının **birebir tekrarıdır**: sunucu tarafı hazır, istemci taşımıyor, kapı
  // yeşil. *Bir deponun defterindeki bir kusur sınıfı, okunmadıkça tekrar eder.*
  diyalog_durumu?: DiyalogDurumu | null;
  // Sohbet oturumu kimliği — kalıcı logda chat'i gruplamak için.
  session_id?: string;
  // §B (1 Ağustos 2026) — konu/thread kimliği (client üretir, backend salt echo eder,
  // is_followup mantığına karışmaz). bkz. lib/threads.ts.
  thread_id?: string | null;
  // §B düzeltmesi (1 Ağustos 2026) — "bu karta yanıt ver": backend'e AYNEN echo edilmesi
  // için gönderilen, çapa kartın kısa insan-okur etiketi (bkz. lib/threads.ts::replyAnchorLabel).
  reply_to_label?: string | null;
  // ⚠️ FAZ 0.5 — ÇAPA ZİNCİRİ. İstemci çapanın `cube_query`'sini bugüne kadar GENEL
  // `cube_query` yuvasına DÜZLEŞTİRİYORDU; sunucu bu yüzden hep `KURAL_YAPISAL`
  // görüyor, `KURAL_CAPA`/`COKLU`/`CELISKI` (19 altın vakalı, testli bir modül)
  // ÜRETİMDE HİÇ ateşlenmiyordu. Bu iki alan çapayı KİMLİĞİYLE taşır.
  // `cube_query` DEĞİŞMEDEN gönderilir — bayrak kapalıyken sunucu bu alanları hiç
  // okumaz ve davranış birebir bugünküdür (GERİ AL).
  reply_to_cube_query?: CubeQuery | null;
  reply_to_extra_cube_queries?: CubeQuery[] | null;
  // §B düzeltmesi (1 Ağustos 2026) — çoklu-seçim birleşik bağlam: DİĞER seçili kartların
  // kısa özetleri (ör. "{soru} → {N} satır"). Yalnız Discovery LLM promptuna grounding
  // metni olarak eklenir — deterministik cube-routing'e karışmaz (bkz. backend
  // AskRequest.extra_context).
  extra_context?: string[] | null;
  // GRAFİĞE ÇAPA (Faz G2) — işaret edilen HÜCRE. "Nisandaki sıçrama ne?" bir metin
  // numarası değil YAPISAL bir seçimdir: koordinat backend'de `drill.select_cube_query`
  // ile gerçek bir alt-sorguya çevrilir.
  anchor?: { dimension: string; value: string } | null;
  // YOL SINIRI (Faz F2) — "yalnız küpün KANITLADIĞI cevapları göster".
  // Sayısal güven eşiği DEĞİL (MIMARI: kalibre edilmemiş sayı "güven değil süs"):
  // merdivenin kendisine bağlı üç ayrık seviye.
  //   "deterministik" → yalnız route()      · "llm" → route + Intent-JSON
  //   null/"kesif"    → + Discovery (varsayılan, davranış DEĞİŞMEZ)
  yol_siniri?: "deterministik" | "llm" | "kesif" | null;
  // 🔴 FAZ 5.14 — HIZLI ↔ DERİN. Ürünün *"LLM'siz cevap"* tezinin kullanıcıya verilen
  // kontrolü. `hizli` sunucuda `yol_siniri="deterministik"` ile AYNI kapıdan geçer —
  // aynı davranışa iki AD vermek meşrudur, iki UYGULAMA vermek değildir.
  //
  // ⚠ Seçim **thread'e değil SORUYA** bağlıdır ve her mesajda sıfırlanır: yapışkan bir
  // ayar, unutulmuş bir ayardır.
  mod?: "hizli" | "derin" | null;
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

// Faz 4.2 — ONAYIN KURU KOŞUMU. Onaylayan kişi MDL değişikliğini OLDU BİTTİ olarak
// görüyordu; bu uç, YAML'a yazmadan ne değişeceğini gösterir. Diff'i üretimdeki
// yazıcının KENDİSİ geçici bir kopya üzerinde üretir (taklit değil).
export interface MeasurePreviewInput {
  cube: string;
  measure_name: string;
  expression: string;
  type?: string;
  label?: string | null;
  synonyms?: string[];
  lower_is_better?: boolean | null;
}

export interface MeasurePreview {
  candidate_id: string;
  cube: string;
  yaml_path: string;
  diff: string; // unified diff
  changed: boolean;
  // Diff'te GÖRÜNMEYEN ama bilinmesi gereken sonuç: onay, pack'ten gelen cube'u bu
  // tenant'ın şirket katmanına taşır (paylaşılan pack dosyasına dokunulmaz).
  creates_company_override: boolean;
}

// --- Faz 5.1/5.2 — "neden değişti?" (katkı ayrıştırması + PVM) ---------------------
// Her bulgu KENDİ BAŞINA bir CubeQuery taşır: tıklanınca /cube ile LLM'siz koşar ve
// kendi Query Contract'ını üretir. Rakiplerden ayrıştığı nokta budur — skor bir metin
// değil, doğrulanabilir bir sorgunun etiketi.
export interface ContributionFinding {
  label: string;
  kind: string;
  deger: unknown;
  simdi: number;
  onceki: number;
  delta: number;
  net_pay: number | null; // net değişime oran (net ~0 ise null — UYDURULMAZ)
  brut_pay: number | null;
  cube_query: CubeQuery;
}

export interface ContributionReport {
  dimension: string;
  dimension_label: string;
  net_degisim: number;
  brut_hareket: number;
  bulgular: ContributionFinding[];
  kirpilan_segment: number; // sessiz kesme OLMADIĞININ kaydı
  kirpilan_esik_yuzde: number;
}

export interface PvmFinding {
  label: string;
  kind: string;
  deger: unknown;
  delta: number;
  fiyat_etkisi: number;
  miktar_etkisi: number;
  birlesik_etki: number;
  baskin_etken: string;
  fiyat_simdi: number | null;
  fiyat_onceki: number | null;
  miktar_simdi: number;
  miktar_onceki: number;
  deger_simdi: number;
  deger_onceki: number;
  cube_query: CubeQuery;
}

// ŞELALE (Faz I2) — PVM'nin ARTIKSIZ ayrışmasının görseli. Karar BACKEND'de alınır
// (ADR-0024) ve bileşenler toplamı nete varmıyorsa `null` gelir: grafik SUSAR, tablo
// konuşur. Toplamı denetlemeyen bir şelale "çubukları üst üste koy, sona varırsın"
// iddiasını yalanlar.
export interface WaterfallSpec {
  kind: "waterfall";
  start: { label: string; value: number };
  steps: { label: string; value: number }[];
  end: { label: string; value: number };
  unit: string;
  net: number;
}

export interface PvmReport {
  dimension: string;
  dimension_label: string;
  value_measure: string;
  volume_measure: string;
  price_label: string;
  net_degisim: number;
  // ARTIKSIZ: fiyat + miktar + birleşik = net_degisim (birebir)
  fiyat_etkisi: number;
  miktar_etkisi: number;
  birlesik_etki: number;
  bulgular: PvmFinding[];
  kirpilan_segment: number;
  kirpilan_esik_yuzde: number;
  viz?: WaterfallSpec | null;
}

// REÇETE (Faz G3) — "ne yapmalıyız?" cevabının YAPILI gövdesi.
// Üç boyutun üçü de ölçülmüş ya da BEYAN EDİLMİŞ: etki (contribution deltası) ·
// yön (lower_is_better metadata beyanı) · yoğunlaşma (hesaplanmış oran).
// Kontrol edilebilirlik / maliyet / risk KASTEN YOK — veride bulunmuyorlar ve
// tahmin edilselerdi sıralama uydurma olurdu.
export interface PrescriptionOption {
  segment: string;
  impact: number;
  share: number | null;      // net değişime oran; net ~0 ise null — UYDURULMAZ
  direction: "kotulesti" | "iyilesti";
  cube_query?: CubeQuery;    // tıklanınca tek başına açılır, kendi makbuzunu üretir
}

export interface Prescription {
  options: PrescriptionOption[];
  concentration: number | null;
  // true = değişim DAĞINIK → öneri üretilmedi ve NEDEN üretilmediği `rationale`'da.
  // Bu bir eksiklik değil bir karardır: sorun sistemikse tek segmente odaklanmak
  // toplamı kayda değer biçimde değiştirmez.
  diffuse: boolean;
  rationale: string;
  measure?: string | null;
}

// KARAR KAYDI (Faz E-4) — Query Contract'ın BİR ÜSTÜ. Contract "bu sayı nasıl
// hesaplandı"ı, bu "bu sayıya bakarak NE KARAR VERDİK"i cevaplar. BI ürünlerinde
// eksik olan halka budur: rapor kalır, kararın kendisi kaybolur.
export interface DecisionRecord {
  id: string;
  ts: string | null;
  session_id: string | null;
  question: string | null;
  chosen: unknown;
  // Değerlendirilen TÜM seçenekler — "neden bu?" ancak "hangilerine karşı?" bilinirse
  // cevaplanabilir. Yalnız seçileni saklamak kararı bir duyuruya çevirirdi.
  options: unknown;
  rationale: string | null;
  note: string | null;
  contract_ids: string[];
  content_hash: string | null;
  // ÜÇ DEĞERLİ: true = hash tutuyor · false = KURCALANMIŞ · null = doğrulanamadı
  // (eski/hash'siz kayıt). false ile null'u birleştirmek suçsuzu suçlu göstermek olurdu.
  verified: boolean | null;
  evidence_count: number;
  supersedes: string | null;
  // 🔴 FAZ 5.8 — ŞABLON. `contract_ids` *"o gün hangi sayıya baktık"* der (donmuş
  // kanıt); şablon *"aynı analizi BUGÜN koşsak ne çıkar"* der. Biri ötekinin yerine
  // geçmez ve bu yüzden iki ayrı düğme: `doğrula` geçmişe, `bugün koş` bugüne bakar.
  sablon?: { cube_query: CubeQuery; parametreler?: string[] } | null;
  // Hangi hash sürümüyle doğrulandı — `v1` bir kayıt `sablon` alanını KORUYAMAZ
  // (alan yokken yazılmış bir imza, olmayan bir alanı koruyamaz) ve okuyucu bunu
  // bilmelidir.
  hash_surumu?: string | null;
}

export interface ContributionResponse {
  measure: string | null;
  mode: string; // "yoy" | "mom"
  kind: string; // "segment" | "pvm"
  raporlar: ContributionReport[];
  pvm_raporlar: PvmReport[];
  note: string | null; // ayrıştırma YAPILAMADIYSA nedeni
  taranmayan_boyut: number; // üst sınır yüzünden bakılmayan boyut — kapsam sessizce daralmaz
  // Atlananların ADLARI: bir SAYI ("3 boyut taranmadı") kullanıcıya hangi soruyu
  // sorabileceğini söylemez, ad söyler ("peki renk bazında?").
  taranmayan_adlar?: string[];
  contract_ids: string[];
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

// --- FAZ H · ONAYLI YAZMA AKSİYONLARI ---------------------------------------------
// Ajan yazamaz; ÖNERİR. Öneri bir yetki taşımaz — onay ucu `authorize()`'ı YENİDEN
// çağırır ve argümanları var olan uçların kendi doğrulamasından geçirir. Bu yüzden
// önerinin istemcide taşınması güvenlidir: kurcalanmasından kazanılacak bir şey yoktur.
export interface EylemOnerisi {
  eylem: "pano.ekle" | "zamanla.olustur";
  ozet: string;                 // insan-okur tek cümle — kullanıcı NEYİ onayladığını okur
  izin: string;                 // authorize() aksiyonu (permissions ile eşleşmeli)
  geri_alinabilir: boolean;     // false → UI daha ağır bir onay dili kullanır
  argumanlar: Record<string, unknown>;
  /** 🔴 **İmzalı onay bileti** — §C ölçüt 6'nın *"süre aşımı 30 dk"* şartı.
   *
   *  Ölçüldü: canlı onay yolunda **hiçbir süre kontrolü yoktu** ve üç saat önceki bir
   *  öneri onaylanıp koşabiliyordu; `VARSAYILAN_OMUR_SN` yalnız `onay_akisi.py`'de
   *  duruyordu — o modülün **hiçbir üretim tüketicisi olmadan**.
   *
   *  ⚠ İstemciden gelen düz bir zaman damgası **yetmezdi**: istemci her seferinde
   *  *"şimdi"* gönderir ve kapı bir **törene** dönüşürdü. Bilet HMAC ile imzalıdır.
   *  ⚠ Opsiyonel: anahtar yoksa sunucu bileti **üretemez** ve öneri biletsiz gelir —
   *  o durumda onay reddedilir (fail-closed), sessizce süresiz koşmaz. */
  bilet?: string;
}

export interface EylemOnayResult {
  ok: boolean;
  eylem: string;
  id: string | null;
  note: string;
}

// --- FAZ E · KALICI SUNUM TERCİHİ --------------------------------------------------
// YALNIZ görünüm: zaman kırılımı (granularity) ve tablo/grafik (view). Ölçü/cube
// seçimine ASLA karışmaz — bir tercihin "hangi ölçü" sorusuna karışması, kullanıcının
// sormadığı bir raporu onun kendi ayarı gibi göstermek olurdu.
export interface SunumTercihi {
  anahtar: "granularity" | "view";
  deger: string;
  etiket: string;               // insan-okur ("aylık")
  kaynak_ifade: string | null;  // tercihi doğuran cümle
  updated_at: string | null;
}