# HANDOFF #6 — Temel denetimi ve agentic mimariye geçiş

**Tur:** 2 Ağustos 2026 · **Kapsam:** `bu-proje-dima-wrenai` yol haritası (Faz A–I)
**Sonuç:** 63 commit · 843 → **1364 test** · eval sapmasız · frontend üretim derlemesi ✅

---

## 0. Bu turun tek cümlesi

> Yeni yetenek eklemekten çok, **beyan edilmiş ama yapılmayan şeyleri gerçekten yapmak**
> ve **yapılanları denetlenebilir kılmak** işiydi. Turun en değerli bulgularının hepsi
> koda bakarak değil **çalıştırıp çıktısına bakarak** çıktı.

Tekrar eden kusur sınıfı — **on kez** ölçüldü: *"beyan var, kod onu tanımıyor."* Bir
belge/yorum/metadata bir garanti iddia ediyor, kod o iddiayı bilmiyor, ve **hiçbir test
tutmuyor**. Bu yüzden turun ana ürünü kod değil **kapı**: her yeni garanti bir testle
kilitlendi, kapatılamayan her boşluk **açıkça işaretlendi**.

---

## 1. Faz faz ne yapıldı

### FAZ A — dürüstlük borcu (P0)

| | Ne bulundu | Ne yapıldı |
|---|---|---|
| **A1** | `llm._schema_prompt` her modelin her VARCHAR kolonundan **1391 gerçek değer** prompt'a yazıyordu (ad-soyad · SGK · IBAN). `cube_router.build_catalog` **daha dar** bir politika uyguluyordu (358): aynı LLM'e **iki farklı gizlilik politikası** | `sensitivity` sınıflandırması + tek prompt politikası + **CI testi** (`test_llm_veri_sizintisi.py`). MIMARI §4-1 iki katmana (T1/T2) ayrıldı |
| **A2** | `/ask/drill action="raw"` → `SELECT *` ≤500 satır: **`always_filter` yok · PII yok · audit yok** — üç değişmez aynı 30 satırda kırılıyordu | Üçü de bağlandı (`ask.py:2634-2678`), kolonlar beyan edilenlerle sınırlandı |
| **A3** | `WrenConfig(strict_mode)` ve `policy.py` (45 dosya-okuyucu TVF) **ölü koddu**: `WrenEngine`'e `config` hiç geçirilmiyordu | Politika **gölge modda** açıldı; bugünkü savunmanın **tesadüfi** olduğu MIMARI §3.4'e kaydedildi |
| **A4** | `_try_kpi` kapanış zincirini atlıyordu (contract/audit/PII yok); üç ayrı contract kaydedici vardı, biri `except: pass` ile yutuyordu | **`app/answer.py`** — tek kapanış zinciri. Beş ihlal tek hamlede kapandı ve Faz F'nin ön koşulu kuruldu |
| **A5** | Dockerfile pin sapması · `rule_fallback` varsayılan açık · MIMARI §2.3 yanlış · ölü kod | Hepsi düzeltildi; **kod belgeden iyiydi**, belge düzeltildi |

### FAZ B — Wren kaldıracı (seçici benimseme)

- **`type_mapping`** alındı: elle tutulan tip kümeleri **17 gerçek yazımın 13'ünü yanlış
  sınıflıyordu** — `numeric(18,2)` (bir **para tutarı**) boyut oluyordu, `timestamptz`
  zaman ekseninden düşüyordu. Motorun kanonikleştiricisi devreye alındı.
- **`validate_project`** alındı: compose çıktısı **hiç** şema doğrulamasından geçmiyordu.
- **`statement_timeout`** alındı — ve **motorun kendi boşluğu** bulundu:
  `get_connection_info()` zaman aşımını yalnız postgres/clickhouse/trino/bigquery'ye
  enjekte ediyor, **mssql dalı yok**. Üretim tenant'larımız mssql: **kilitlenmiş bir
  sorgu süresiz asılabiliyordu.** Motor yolu **ve ham konnektör** ikisi de kapatıldı.
- **Boyut sırası**: plan *"drill.py'nin elle yazdığı sırayı beyan et"* diyordu; ölçünce
  **elle yazılmış bir sıra bile yoktu** (YAML beyan sırası). `hierarchies` **bilinçle
  beyan edilmedi** (uydurulmuş hiyerarşi = güvenle yanlış drill yolu); sıra **zaten
  üretilen** beyanlardan okunuyor: hop sayısı + fan-out sertifikası.
- **B1**: `schema()` 2277 → **694 ms** (3,3×), içerik birebir aynı.

### FAZ C — tek gerçeklik

| Kusur | Sonuç |
|---|---|
| `interpret` ve `viz` kolon rollerini **bağımsız** çıkarıyordu, zaman-adı sözlükleri farklıydı (11 vs 10) — **grafik zaman serisi çizerken cümle onu kategori sanabiliyordu**, ikisi de "deterministik" rozetliydi | `app/result_shape.py` — tek sınıflandırma |
| Aynı sayı iki yüzeyde farklı görünüyordu (`150,5` sohbette `151`, e-postada `150,50`) | `app/fmt.py` + `app/stats.py` |
| **MoM hizalaması sessizce bozuktu**: `_gecen` zaman serilerinde her zaman `None` (boyut kırılımlarında çalışıyordu, bu yüzden fark edilmemişti) | `test_yoy.py` (15) önce yazıldı, sonra düzeltildi |

### FAZ D — kapsam tavanı

- **`lab/nl_corpus.py` — planın "asıl metrik" aracı — Faz B1'den beri BOZUKTU**
  (eklediğim bir parametre yüzünden). pytest yeşil, eval düz, **ama ana metrik ölüydü**.
  Onarıldı.
- **`_syn_hit` altdizi körlüğü**: `"yas" ⊂ "kıyasla"`. `route()`'ta kapsam kapısı
  maskeliyordu; hasar **takip yollarındaydı** — `deterministic_refine("kıyaslama yap")`
  sorguya `yas_grubu` GROUP BY'ı ekliyordu. Kelime-sınırı disiplini `\b` ile **değil**
  (`_` Python'da kelime karakteri) `(?<![a-z0-9])` ile kuruldu.
- **Fan-out sertifikası** build artefaktı oldu (`app/fanout.py`, 31 ilişki ölçüldü).
- **`_select_consistent`**: `consistency_k=3` yazılmış ama **sıfır tüketicisi** vardı → bağlandı.
- **Dürüst kayıt:** Faz D'nin hedefi (%64 → %80) **TUTMADI**. Erişim %64'te kaldı,
  doğru-cube %86,6 → %86,3. MIMARI'ye böyle yazıldı.

### FAZ F — agentic çekirdek

- **F1 araç kaydı** (`app/tools.py`): 12 yetenek tipli araca dönüştü — determinizm ·
  maliyet · yan etki · **izin** · **ürettiği makbuz**. Kayıt üç yüzeyin ortak kaynağı.
- **F2 planlayıcı** (`app/planner.py`): dört kapı (kayıt · yetki · **deterministik-önce**
  · bütçe), bütçe tavanında **dürüst kısmi cevap**.
- **F3 kompozisyon**: `contribution.arastir()` HTTP'den ayrıldı. İki kazanç birden:
  kayda girebildi (`dis_adim(gated:false)` **itirafı kalktı**) ve **arka plan işleri onu
  çağırabildi** → uyarının nedeni (aşağıda).

### FAZ G — konuşma katmanı

- **G1 üçüncü sınıf**: *"bu neden böyle?"* / *"normal mi?"* / *"ne yapmalıyız?"* artık
  Discovery'ye düşmüyor; mevcut makbuza çapalanıp **var olan araçları kompoze ediyor**.
- **G2 grafik çapası**: tıklanan hücre **yapısal bir seçime** dönüyor.
- **G3 reçete** (`app/prescribe.py`): yalnız **üç ölçülebilir boyut** — etki (ölçülür) ·
  yön (**beyan**) · yoğunlaşma (hesaplanır). Kontrol edilebilirlik/maliyet/risk
  **bilinçle dışarıda**: onlar veride yok, uydurmak reçeteyi güvenle yanlış yapardı.
- **G3 eşik kıyası**: cube'larda `target:` beyanı **hiç yok** (ölçüldü) → hedef
  **uydurulmadı**. Gerçek, beyan edilmiş kaynak: **kullanıcının kendi kurduğu alarmlar.**
- **G4 anlatım doğrulayıcı** (`app/narration_guard.py`): *"doğrulanamayan sayı içeren
  cümle yayımlanmaz"* — 31 test. **Tüketicisi yok ve bu kayıtlı** (§4'e bak).
- **G5 bağlam çözücü** (`app/context.py`): sunucunun artık bir bağlam modeli var ve
  **her cevap çözdüğü bağlamı + GEREKÇESİNİ** makbuzuna yazıyor.

### FAZ E — çekirdek ürün

- **E-1**: telemetrinin **yazma yolunun sıfır testi vardı** (okuma tarafı elle eklenen
  satırlarla test ediliyordu) → kapatıldı.
- **E-4 Karar Kaydı** (`app/decision.py`): Query Contract *"bu sayı nasıl hesaplandı"*a
  cevap verir; Karar Kaydı **bir üst soruya**: *"bu sayıya bakarak ne karar verdik?"*
  `content_hash` bir imza değil **kurcalama tespiti**; `verified` **üç değerli**
  (doğru / kurcalanmış / hash yok). Başka tenant **404 döner, 403 değil** (403 varlığı sızdırır).

### FAZ I — görselleştirme

- **I1**: `viz.py` cube metadata'sından **yalnız `units`** okuyordu. `additive: semi`
  **beyan edilmişti** ve `recommend()` onu **hiç almıyordu** → `bakiye` yığılabiliyordu.
- **I2 şelale**: PVM'nin matematiği vardı, **görseli yoktu**. Kural bir tercih değil
  **kapı**: bileşenler toplamı net değişime varmıyorsa grafik **üretilmez**.
- **I3 `VIZ_STANDARDS.md`**: belge yazılmadan **önce ölçüldü** — beş karar zaten **49
  testle** zorlanıyordu; zorlanmayan tek karar (`lower_is_better` → renk) **gerçek bir
  sapma** çıkardı (§3).
- **I4 sadakat**: aynı `cube_query` için ekran/e-posta/rapor **aynı VizSpec** — sözleşme
  kodda iddia ediliyordu ama **iki kez kırılmıştı**.

---

## 2. Frontend: neyin görünür olduğu

Kural (MIMARI §14.1): **yeni yetenek yeni PANEL doğurmaz.** Ölçüldü — panel sayısı tur
başında ve sonunda **11**; eklenen üç şey **katman**:

| Yetenek | Nerede görünür | Yeni panel? |
|---|---|---|
| Katkı ayrıştırması + PVM şelalesi | `ContributionLayer` — cevabın kartında, **kapalı başlar**, tıklanmadan sorgu koşmaz | Hayır |
| Reçete (*"ne yapmalıyız?"*) | `PrescriptionLayer` — yön rozeti + yoğunlaşma + Karar Kaydı kaydet/doğrula | Hayır |
| Köken + fan-out sertifikası | `InterpretationBar`'da `⇱✓ / ⇱⚠ / ⇱?` rozeti | Hayır |
| Uyarının **nedeni** | `NotificationsPanel`'de katlanır `⤵ neden?` | Hayır |
| Eşik kıyası | `OutputInsight`'ta 🎯 sinyali (mevcut sinyal şeridi) | Hayır |
| Grafik çapası | `ResultView` tıklaması → sohbet çapası şeridi | Hayır |
| Diff önizlemesi | `ReviewPanel` — onay butonu **diff görülmeden aktifleşmez** | Hayır |

**Ölçülen ve düzeltilen üç UI kusuru:**

1. Konuşma cevabının **gövdesi** `next_steps`'e konuyordu ve UI onu **"sonraki adım"**
   başlığıyla gösteriyordu — Δ tutarları, % paylar, kırpma uyarısı **kayboluyordu**.
2. `⤵ kök neden` ve `𝚫 neden değişti?` yan yana duruyordu — ikisi de "neden" diyor ama
   biri **seviye**, öteki **değişim** analizi. Adlandırma ayrıştırıldı.
3. Reçete **düz metne** çevriliyordu: yön/yoğunlaşma/etki üçü de kayboluyordu.

**Şerit sayısı ölçüldü:** normal rapor 3 (2'si kapalı) · *"bu neden böyle?"* **1** ·
*"ne yapmalıyız?"* **2** (cevap → dayanak) · *"normal mi?"* 3.

---

## 3. Turun en pahalı bulguları (hepsi ÇALIŞTIRARAK bulundu)

| # | Bulgu | Neden tehlikeliydi |
|---|---|---|
| 1 | **Ölçüm aracının kendisi bozuktu** (`nl_corpus`, Faz B1'den beri) | pytest yeşil, eval düz — ama planın "asıl metriği" ölçülemiyordu. **Ölçüm aracı da bir bağımlılıktır.** |
| 2 | **MoM hizalaması sessizce yanlıştı** | Boyut kırılımlarında çalışıyordu; yalnız zaman serilerinde bozuktu — bu yüzden kimse görmedi |
| 3 | **LLM'e 1391 gerçek değer gidiyordu** | Demo'daki TCKN maskesi **kodda değil verinin kendisindeydi**; gerçek müşteride gerçek TCKN giderdi |
| 4 | **13/17 DB tipi yanlış sınıflanıyordu** | `numeric(18,2)` — bir para tutarı — **gruplama anahtarı** oluyordu ve bu kullanıcıya *"şemanı çıkardım"* diye sunuluyordu |
| 5 | **`toplam_dogalgaz_sm3` ısı paleti ters** | FE `lower_is_better`'ı **tüm cube'ların birleşimi** olarak okuyordu; ölçü bir cube'da düşük-iyi, ötekinde değil → **aynı sayı yanlış cube'da yanlış renkle** |
| 6 | **MSSQL'de sorgu zaman aşımı yoktu** | Motor postgres/clickhouse/trino/bigquery'ye enjekte ediyor, mssql'i **atlıyor** — ve üretimimiz mssql |
| 7 | **`_syn_hit` altdizi körlüğü** | `route()`'ta kapsam kapısı maskeliyordu; hasar takip yollarındaydı ve **fazladan GROUP BY** üretiyordu |
| 8 | **`recommend()`'in 6 çağıranı argümanları elle topluyordu** | Biri `measure_units` diye **yanlış anahtar** geçiyordu; `semi_additive`'i **hiçbiri** geçmiyordu |
| 9 | **Eşik ihlali aksiyonsuz tek sinyaldi** | Sistem kendi bulduğu aykırılığa *"hangi makine sürüklüyor?"* derken **kullanıcının kendi alarmına** sessiz kalıyordu |
| 10 | **Ölü yetki yardımcısı** (`require_superadmin`) | Birisi "hazır" sanıp kullanır ve **yanlış plane'in** kontrolünü uygulardı |

---

## 4. Bilinçle YAPILMAYANLAR (ve neden)

Bunlar eksik değil **karar**. Hepsi MIMARI'de gerekçesiyle kayıtlı **ve artık testle
kilitli** (`tests/test_beyanlar_curumesin.py`) — biri bağlanırsa CI kırılır ve beyanın
güncellenmesini zorlar.

| Ne | Neden yapılmadı |
|---|---|
| **`narration_guard` bağlanmadı** | Sistemde **LLM-üretimi düz metin hiç yok** — `interpret` deterministik, sayıları sonuçtan geliyor. Guard'ın koruyacağı bir yüzey yok. **Test o günü yakalar**: LLM'den düz metin üreten bir yöntem belirirse CI kırılır |
| **`hierarchies` beyan edilmedi** | Demo için hiyerarşi uydurmak (*makine→bölüm*) **güvenle yanlış bir drill yolu** üretirdi. Sıra **ölçülebilir maliyetten** okunuyor |
| **Cube `target:` beyanı eklenmedi** | Hedef uydurmak *"hedefin %12 altındasın"* gibi sorgulanmayan bir yalan üretirdi. Kullanıcının **kendi alarmı** gerçek bir beyandır |
| **Pareto grafiği** | Backend yoğunlaşmayı **zaten ölçüyor**, ama FE `ChartKind`'ında pareto yok. Yarısını yapmak **yetim bir alternatif** üretirdi |
| **Sonuç cache'i (E-2)** | Plan: *"ölçülen tekrar oranı eşiği aşmadan kurma"*. Tekrar oranı **üretim telemetrisi ister** — çevrimdışı ölçülemez |
| **Plan seçimi (F4)** | Aynı gerekçe: telemetri (E-1) verisi gerekiyor |
| **17 konnektör** | Her biri yeni bir sürücü bağımlılığı; `--network none` altında **test edilemez**. Test edilemeyen bir konnektör listesi *"beyan var, kod tanımaz"*ın yenisi olurdu |
| **`cube_query_hash`** | Primitif hazır, tüketicisi E-2 cache'i |
| **`tools.llm_araclari`** | Primitif hazır, tüketicisi F4 |

---

## 5. Doğrulama komutları

```bash
R=/home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic

# Testler + eval + asıl metrik (frontend MUTLAKA mount edilmeli: yetim-uç kapısı yoksa sessizce atlanır)
docker run --rm --network none \
  -v "$R/backend:/app" -v "$R/dima-frontend-demo-master:/dima-frontend-demo-master:ro" \
  -w /app -e DIMA_VQR_EMBEDDER=off dima-test \
  sh -c "python -m pytest -q | tail -3; python -m eval.run | tail -2; python lab/nl_corpus.py | tail -6"

# Frontend
cd "$R/dima-frontend-demo-master" && npx tsc --noEmit && npx eslint src && npx next build
```

> **ASLA iki test konteynerini paralel koşturma** — compose kilidi süreç-içidir, ikisi
> `metadata.yml`de çakışır (bu turda yaşandı).

**Son ölçüm:** 1364 test · 1 skip · eval sapmasız · tsc temiz · eslint 2 uyarı (ikisi de
önceden var) · `next build` başarılı.

---

## 6. Sıradaki tur için

**Ölçüm gerektirenler** (önce veri, sonra kod — plan kuralı #7):
1. **Telemetriyi üretimde bir hafta koştur** → tekrar oranı, Intent/Discovery payı,
   strict_mode gölge modunun kaç sorguyu reddedeceği. **E-2 · F4 · A3'ün açılması** buna bağlı.
2. `nl_corpus` erişimi **%64'te sabit** — Faz D hedefi tutmadı. Bir sonraki kapsam turu
   **hangi soruların düştüğünü** tek tek okumakla başlamalı, yeni kural yazmakla değil.

**Ölçüm gerektirmeyenler:**
3. **E-3 kurumsal hafıza** — bugün hiç yok; ajanın bağlam enjeksiyonunun kaynağı.
4. **E-5 tahmin/what-if** — sıfır. Deterministik bir temel (mevsimsel naif / doğrusal
   trend) yazılabilir ve **seçim kuralıyla** gelmelidir.
5. **E-6 görev motoru + sabah brifingi.**
6. **Kalan grafik dağarcığı** — her biri `VIZ_STANDARDS.md` §1'in kapı kuralıyla.

**Bir sonraki geliştiriciye tek uyarı:** bir şey eklerken önce
`tests/test_beyanlar_curumesin.py`, `tests/test_uc_yetim_degil.py` ve
`tests/test_viz_sadakat.py`'yi oku. Üçü de aynı şeyi söylüyor: **bu depoda bir garanti,
onu tutan bir test kadar gerçektir.**
