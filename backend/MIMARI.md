# Dima — Mimari Referansı

> **Bu belge KANONİKTİR ve NORMATİFTİR.** Mimari bir soruda çelişki çıkarsa bu belge kazanır.
> `HANDOFF_DOCS/*` tarihsel kayıttır, normatif değildir.
> `Dima-0-100-Gorev-Takip-Dosyasi (2).md` bir ÜRÜN şartnamesidir, mimari otorite değildir (§8).
> `backend/CLAUDE.md` ajan/geliştirici için kısa kural indeksidir; bu belgeye işaret eder.
>
> Son güncelleme: 2026-08-02 · Dal: `wren-bağımsız` · Doğrulama yöntemi: bu belgedeki her
> "ölçüldü/kanıtlandı" ifadesi gerçek `wren_core` 0.7.3 wheel'i, gerçek derlenmiş MDL ve gerçek
> DuckDB verisi üzerinde **çalıştırılarak** üretildi. Varsayım olanlar açıkça öyle işaretlidir.

---

## §0 · ⟳ YÜRÜRLÜKTE — YOL HARİTASININ OTORİTE ALDIĞI BAŞLIKLAR  *(FAZ −1/Kutu B)*

> 🔴 **BU BLOK BİR KURAL BEYAN ETMEZ — YALNIZ OTORİTE İŞARET EDER.**
> Her satır tek bir şey söyler: *"bu başlıkta `DIMA-V1-YOL-HARITASI.md` §X kazanır,
> **ve henüz UYGULANMADI**."* Buradaki hiçbir satır *"yeni kural şudur"* demez —
> aksi hâlde okuyucu **yapılmış zanneder**, ki `§10`'un `✅` = *"ölçüldü ve YAPILDI"*
> tanımının ihlali olurdu.
>
> **Yaşam döngüsü:** ilgili faz indiği gün → satır **silinir**, yerine ilgili bölüme
> **ölçümlü `✅`** yazılır, ve `tests/test_beyanlar_curumesin.py`'deki **tuzak testi ters
> çevrilerek** korunur. *Belge güncellemesi böylece bir CI zorunluluğu olur.*
>
> **Yol haritası:** `~/.claude/plans/DIMA-V1-YOL-HARITASI.md` · **operasyon:**
> `OPERASYON.md` (kural seti) + `OPERASYON-DURUM.md` (nerede kaldık)
>
> > ✅ **§14 İNDİ — BEŞ ENTEGRASYON KAPISI** *(`45b5c6a`, FAZ 0.14)*. Ortak iskelet
> **tek sahipte**: `tests/kapi_ortak.py` (yorum ayıklayıcı · tam-yol deseni · tüketim
> kontrolü). **K1** `test_uc_yetim_degil` — tam yol + yorumsuz tarama + ölü sarmalayıcı ·
> **K2** `test_cevap_alani_yetim_degil` — iç içe alan · diğer sözleşmeler · **erişilebilirlik** ·
> **K3** `test_ters_yetim` — FE'nin beklediği ama backend'in vermediği alan ·
> **K4** `test_yuzey_sadakati` — aynı `source` her yüzeyde aynı rozet (§5) ·
> **K5** `test_panel_sayisi` — **export 13 / tavan 13, pay 0** ·
> **D5** `test_yol_haritasi_butunlugu` — belge kapısı.
>
> 🔴 **İkisi kurulduğu gün av yaptı:** K1 `GET /contracts`'ı yakaladı — alt-dize taraması
> onu hem `` `/contracts/${cid}` `` içinde hem bir **yorum satırında** buluyordu
> ([KANIT §0.1-5] kapı tarafından **yeniden üretildi**); D5 ise 130 maddenin **birinde**
> `NE`/`KAPI` eksiği buldu. Kapıların **kendi premisleri iki kez kusurlu** çıktı
> (referans ≠ çağrı · plan ≠ envanter) — ikisi de **ölçülerek** düzeltildi.

**Bu bloğun kendi kapıları** *(D4: her artefakt kanonik belgede anılır)*:
> `tests/test_beyanlar_curumesin.py` — her satır için bir **tuzak** + tablonun **yapısal
> işaretçi biçimi** (dört hücre · `⟳ UYGULANMADI` · otorite fazı) ·
> `tests/test_MIMARI_dosya_atiflari_var.py` — **bu belgede anılan her `tests/test_*.py`
> ve omurga modülü gerçekten mevcut** olmalı *(FAZ −1'de kuruldu; ilk avı `A6` oldu)*.

| MIMARI § | Konu | Otoriteyi alan faz | Durum |
|---|---|---|---|
> ⟳ **FAZ 2.1 İNDİ — iki satır buradan ÇIKTI, ölçümleri aşağıda (2026-08-04).**
>
> * **`§3 · §3.3`** — çekirdek katman + compose **birleştirme semantiği**: `packs/cekirdek/`
>   metrik sözlüğü + `compose._merge_cube_metadata` (**beşinci** üreteç, anahtar düzeyinde).
>   Ölçüldü `@f263820`: `python lab/mdl_diff.py` → **dört şirkette de sayı-etkisi 0 fark**,
>   sözlük zenginleşmesi **7 · 14 · 9 · 11**.
> * **`§5-grain`** — grain sözleşmesi **fail-closed**: `cekirdek.grain_denetle` +
>   `compose` reddi. `cari` metrikleri sözleşme beyan ediyor ve **üç ERP'nin üçü de uyuyor**
>   (`python -m pytest tests/test_cekirdek_katman.py` → **29 test**). ⚠ `ticaret` **bilerek
>   uymuyor**: `satis_tutari`'nın kanonik grain'i (fatura ↔ stok hareketi) **adım (c)**'nin
>   kararıdır ve bugün beyan etmek üç ERP'den ikisini derleme zamanında reddetmek olurdu.
>
> Tuzaklar **silinmedi, TERS ÇEVRİLDİ**: `test_TERS_TUZAK_FAZ_2_1_CEKIRDEK_KATMAN_AYAKTA`.

| **§3.4** | **`SessionProperty` TÜM çağrı sitelerinde** — bugün 36 `query`/`dry_plan` çağrısı kimlik geçmiyor *(CLS `off`, bkz. §6.3c)* | **FAZ 1.2 kuyruğu** | ⟳ UYGULANMADI |
| **§5** | **18. yasak**: *"cevapsız bir dal, cevaplı bir yolu KESEMEZ"* (`KAT-2`) | **§G/AJ0** | ⟳ UYGULANMADI |
| **§9** | hedef mimari — **metrik katmanı** merdivene giriyor | **FAZ 0.18 · 2.1** | ⟳ UYGULANMADI |
| **§11** | agentic — **onaylı yazma aksiyonları** | **FAZ 6.1** | ⟳ UYGULANMADI |

> ⛔ **BU LİSTEDE OLMAYAN ama sorulabilecek bir satır — kayda geçiyor:**
> *"§9.2 — ölçü + başka cube'un BOYUTU ifade edilemez"* bir ⟳ satırı **DEĞİLDİR**, çünkü
> öyle bir olmayan-hedef **artık yoktur**: `0a1a087`'de `⟳ FAZ B1` bloğuyla açıkça geri
> çekildi (*"bu satırla çelişiyordu ve yanlıştı"*). §9.2'de duran madde *"Ölçü-A × Ölçü-B
> tek CubeQuery'de olamaz"* — **farklı bir şey**. *Var olmayan bir satıra ⟳ konulamaz.*

---

## 1. Sistem nedir, ne DEĞİLDİR

Dima, bir şirketin kendi veritabanına bağlanıp **Türkçe** soru sorulabilen, cevabı grafik ve
yorumla veren, **her sayının kaynağını kanıtlayabilen** bir karar merkezidir. Bir BI aracı değil,
"denetlenebilir karar ve kontrol merkezi" olarak konumlanır.

### 1.1 Ne DEĞİL — sık yapılan üç hata

**(a) "WrenAI grafiği/yorumu/router'ı zaten yapıyor, biz onu kullanalım."** Hayır.
Bugünkü WrenAI **yalnız bir semantik SQL motorudur**: Rust `wren-core` → MDL → DataFusion → hedef
lehçe SQL. Eski `wren-ui` ve `wren-ai-service` upstream'de `legacy/v1`'e taşındı ve **bu repoda
yok**. `grep -i "chart\|viz" app/wren_service.py` → **0 sonuç**. Grafik (`viz.py`), yorum
(`interpret.py`), chip/kırılım (`cube_router.py`), drill (`drill.py`), router — **hepsi Dima'nındır**.
Upstream'in "GenBI" özelliği ayrı bir CLI ajanıdır, statik dashboard uygulaması üretir, `/ask` ile
mimari ilgisi yoktur.

**(b) "Bu bir text-to-SQL ürünü."** Hayır — text-to-SQL **istisna yoludur** (§3, Discovery).
Varsayılan yol LLM'in *yapı doldurduğu* yoldur. Bu, sektörün 2026'daki olgun tarafıdır: dbt Labs'in
kendi karşılaştırması (Nisan 2026) aynı modellenmiş veride text-to-SQL %84–90, semantic layer
%98,2–100 veriyor. Kritik fark doğruluk değil **hata biçimi**: text-to-SQL'de hata *makul ama
yanlış bir cevap*, semantic layer'da hata *bir hata mesajı*.

**(c) "Bir önceki `strict-agentic` denemesine dönelim."** Hayır — o deneme HER soruyu ham-SQL LLM
üretimine yönlendiriyordu ve `cube_router.py`'yi silme planı vardı. **Kesin olarak terk edildi**
(pahalı · sessiz-yanlış riski · şema değişince kırılgan). Dal adı `feat-wren-strict-agentic`
o terk edilmiş planın fosilidir; adına bakıp yön çıkarma.

### 1.2 Üç düzlem

| Düzlem | Süreç | Kimlik | Rol |
|---|---|---|---|
| **public** | `app/` (FastAPI, `uvicorn app.main:app`) | `app/auth/`, kendi JWT çifti | Son kullanıcı: `/ask`, `/cube`, `/report`, dashboard, schedule |
| **admin** | `admin_app/` (**AYRI süreç**, Wren'siz) | AYRI JWT secret çifti + `sa` claim + zorunlu 2FA | `/sadmin/*`, tenant klonlama/senkron, etkileşim görüntüleyici |
| **control-plane** | `control_plane/` (kütüphane, ikisi de kullanır) | — | SQLModel entity'ler, `authorize()` matrisi, kripto, Alembic |

Ortak auth kodu **yalnız** `control_plane/`'de yaşar (ADR-0015 K1). Admin düzlemi ayrı secret'la
imzalar; ağ izolasyonu deploy katmanındadır.

### 1.3 Veri akışı

```
Müşteri DB (duckdb | mssql | postgres | …)
        ▲ read-only, guard_sql (SELECT/WITH), dialect transpile
        │
   WrenEngine (in-process, subprocess YOK)  ← target/mdl.json (base64)
        ▲
   compose()  ⟵  packs/kaynak ⊕ packs/modul ⊕ packs/sektor ⊕ kesişim ⊕ companies/<slug>
        ▲
   materialize()  ⟵  control-plane DB (TenantConfig)      [DB→dosya TEK YÖNLÜ]
```

---

## 2. Cevaplama merdiveni — normatif akış

`app/routers/ask.py::ask()`. **Sıra bağlayıcıdır**; yeni basamak eklemek bu belgenin
güncellenmesini gerektirir.

| # | Basamak | `source` | LLM? | Taşıdığı garanti |
|---|---|---|---|---|
| 1 | meta / katalog / gelir-tablosu-bilanço | `meta` `catalog` `statement` | yok | sabit içerik |
| 2 | VQR replay (öğrenilmiş soru) | `vqr` | yok (yalnız embedder) | öğrenildiği andaki yapı |
| 3 | **`cube_router.route()`** — sıfır-LLM deterministik NL→CubeQuery | **`cube`** | **YOK** | tam yapısal · chip · kırılım · drill · Query Contract |
| 4 | `deterministic_refine()` — yapısal takip | `cube` | yok | aynı |
| 5 | `cross_cube_add` / `cross_cube_dim_switch` | `cube` | yok | aynı (blend, gerçek JOIN değil) |
| 6 | **Intent-JSON** — LLM *yapı doldurur*, **SQL YAZMAZ** | **`cube+llm`** | evet (küçük model) | tam yapısal · chip · kırılım · drill · Query Contract |
| 7 | **Discovery** — LLM ham SQL yazar | `llm:<sağlayıcı>` | evet | **tek atımlık düz tablo. Chip YOK, kırılım YOK, drill YOK.** |
| 8 | dürüst red | `null` | — | "anlamadığını bil" — yanlış öneri, önerisizlikten kötüdür |

**Tek çıkış noktası `app/answer.py::seal()`** — yorum, next_steps, öneriler, `explain`,
PII maskesi (+ görüldüyse ayrı audit), sohbet kaydı, `interaction_log` ve **fail-closed
audit** oradan geçer. Makbuz kaydı da tek uygulamadır: `answer.record_contract()`.

> ✅ **Faz A4'te (2026-08-02) modül düzeyine çıkarıldı.** Önceden `ask()` içinde bir
> **closure**'dı ve bu, belgede *"bilinen sapma"* diye tek satırla geçilen şeyin aslında
> **beş ihlalin ortak kök nedeni** olduğunu gizliyordu: closure `body`/`request`/`principal`/
> `t0`'a kapandığı için dışarıdan çağrılamıyordu, bu yüzden (a) `/cube` **paralel bir zincir**
> yazmıştı ve `is_new_topic`/`thread_id`/`reply_to_label` set etmiyordu, (b) contract kaydını
> `except Exception: pass` ile **sessizce yutuyordu** (ADR-0020 ihlali — 20 satır aşağıda
> audit *bilerek* sarılmamışken), (c) `_try_kpi()` zinciri **tamamen atlıyordu** (belgede
> yalnız "yorum" yazıyordu; gerçekte **contract + audit + PII** üçü birden eksikti),
> (d) üç ayrı contract kaydedici vardı, (e) hiçbiri **izole test edilemiyordu**.
>
> `seal()` aynı zamanda **Faz F'nin (agentic araç kaydı) taşıyıcısıdır**: bir ajan aracının
> çıktısı, kullanıcının bir sorusundan daha az denetlenebilir olamaz. Araç ne üretirse
> üretsin buradan geçer — makbuz/iz/maskeleme garantisi böyle **yapısal** olur, her araca
> ayrı ayrı eklenen bir alışkanlık değil. Kilit: `tests/test_kapanis_zinciri.py`.

### 2.1 Basamak 3 ve 6 neden aynı garantiyi taşıyor
İkisi de aynı **yapısal `CubeQuery`** üretir ve aynı **deterministik derleyici** SQL'e çevirir.
LLM'in katkısı yalnız *alan seçimi*dir. `parse_cube_query()` katı bir whitelist'tir: bilinmeyen
cube/ölçü/boyut/zaman-boyutu/filtre-boyutu → tüm sorgu `None`. LLM uydurduğunda cevap üretilmez.

### 2.2 Discovery neden ölü ve neden istisna
`cube_query` üretmez → `next_steps`, `recommendations`, `calculation_explanation` boş kalır;
`/ask/drill` dallanmayı **dürüstçe reddeder** (sahte dallanma uydurmaz). Araştırma bunu doğruluyor:
*durumsuz çok-turlu text-to-SQL 3. turda sıfır doğruluğa çöküyor* (EnterpriseMem-Bench, 2026-05).
Ölçülen prod maliyeti: **12.567 ms · 24.352 input token**, aynı tenant'ın cube yolu **145–434 ms ·
0 token**. **Her Discovery cevabı, belgelenmiş bir kapsam boşluğudur ve bir terfi adayıdır.**

### 2.3 LLM sağlayıcıları
`DIMA_LLM_PROVIDER = auto | anthropic | xai | gemini | groq | ollama | rule`.
`auto` → `FailoverSqlGenerator`, sıra: `anthropic → gemini → groq → xai → ollama`, hepsi
başarısızsa **dürüst red** — zincir tükenince `FailoverSqlGenerator` `RuntimeError` fırlatır
ve `ask.py` bunu cevapsızlığa çevirir. (⚠️ Bu satır 2026-08-02'de düzeltildi: eskiden
*"hepsi başarısızsa `rule`"* yazıyordu — **kod belgeden iyiydi**, `rule` zincirde DEĞİL ve
varsayılanı da artık kapalı, çünkü demo şemasına özel sabit kodlanmış kolon adları başka
tenant'ta makul-ama-yanlış SQL üretir.) Intent-JSON için ayrı ve **daha ucuz** bir model kullanılabilir
(`*_select_model`). `rule` yalnız demo/CI içindir; `_llm_source()` onu asla deterministik gibi
etiketlemez.

---

## 3. Semantik katman anatomisi — asıl karışıklık kaynağı

| Kavram | Nedir | Ne YAPAMAZ |
|---|---|---|
| **model** | Fiziksel bir tabloya bağlı mantıksal varlık (`table_reference` + kolonlar) | — |
| **view** | MDL içinde SQL `statement` taşıyan sanal varlık | **İlişkilere katılamaz.** MDL relationship'leri yalnız modellere bağlanır. |
| **relationship** | `{name, join_type, models: [A,B], condition}` | `join_type` **motor tarafından okunmaz** (§5) |
| **handle kolonu** | Adı **hedef model adına eşit** olmak zorunda; `{name: B, type: B, relationship: R}` | Rol-oynatma yok → **(A,B) çifti başına en fazla 1 ilişki** ifade edilebilir |
| **is_calculated kolon** | `{name: X, is_calculated: true, expression: "B.kolon"}` | — |
| **cube** | `base_object` (TEK model **veya** view) + ölçü/boyut/zaman-boyutu **whitelist**'i + sinonimler | `base_object` tektir; cube'un kendisi JOIN üretmez |
| **CubeQuery** | `{cube, measures[], dimensions[], timeDimensions[], filters[], order, limit, blend, entity_limit, measure_having}` | Tek cube'a bağlıdır; **iki cube'un ölçüsü aynı sorguda olamaz** (o `blend` işidir) |

### 3.1 Kritik eşleme: bir Dima `cube`'u, Cube.dev'in `view`'ıdır

Cube.dev'de `cube` = tek tablo + kendi join'leri; `view` = bir join ağacı üzerinden seçilmiş üyeler.
Dima'nın `base_object` + boyut whitelist'i tam olarak ikincisidir. Bu eşlemeyi bilmeden Cube.dev
dokümanını okuyup Dima'ya uyarlamaya çalışmak **sistematik olarak yanlış sonuç verir.**

### 3.2 JOIN gerçekte NEREDE oluyor — belgenin en önemli paragrafı

| Katman | JOIN üretir mi? |
|---|---|
| `wren_core.cube_query_to_sql` (**cube derleyicisi**) | **HAYIR.** Düz `SELECT … FROM <base_object>`. Bildirilmemiş boyutu **reddeder**. |
| `SessionContext.transform_sql` = `WrenEngine.dry_plan` (**model katmanı**) | **EVET.** İlişki grafiğini otomatik, **çok-sıçramalı** gezer. |

Mekanizma: modele bir **handle kolonu** + ifadesi `<handle>.<kolon>` olan bir **`is_calculated`
kolon** eklersen, cube boyutu o calc kolonu gösterdiğinde motor JOIN'i **altına kendisi enjekte
eder.**

**Ölçülen kanıtlar (çalıştırıldı):**
- `oee` cube'u (base `oee_vardiya`) × `makineler.bolum` → **1 join**, toplam `8.514.320,1` =
  baseline'la **birebir**. ISO-22400 oran ölçüsü + aylık kova + join'li kolonda `IN` filtresi
  birlikte doğru çalıştı.
- `partiler → personel → personel_ozluk` (2 sıçrama) → **2 join**, toplamlar tam.
- **Join pruning çalışıyor**: istenmeyen calc kolon → **0 join**. Manifesti zenginleştirmek sorgu
  maliyeti doğurmaz.
- Dotted path'i **doğrudan** cube boyut ifadesine yazmak (`expression: "personel.cinsiyet"`)
  **çalışmaz** — önceden bildirilmiş calc kolon zorunludur.

> ⚠️ Silinen `parti_zengin` view'ının başlığındaki
> *"calc field'lar cube_query_to_sql'de JOIN'lenmiyor → demografiyi VIEW'da denormalize ederiz"*
> yorumunun **ilk yarısı doğru, çıkarılan sonuç yanlıştı.** Bu yanlış inanç 4 cube'u elle bakım
> gerektiren view'lara mahkûm etti. Bu belge o kaydı düzeltmek için yazıldı.
>
> ✅ **Faz 2'de kapatıldı** (2 Ağustos 2026): `parti` → `partiler`, `mizan` → `yevmiye_satirlari`,
> `ik` → `bordro`. Üç view de silindi. Her göçün kabul kriteri aynıydı ve **uygulamadan önce**
> ölçüldü: her ölçü × her boyut kombinasyonu view sürümüyle **birebir aynı** sonuç vermeli
> (sırasıyla 26 / 21 / 73 kombinasyon — hepsi tuttu). Geriye tek meşru view kaldı:
> `enerji_tesis`, çünkü bileşik `(yil, ay)` anahtarıyla join'liyor ve MDL ilişkileri tek
> kolonludur. **Bu bir hedef değil, ifade edilemeyen bir şeyin meşru çözümüdür.**

### 3.3 Compose katman sırası

`packs/kaynak/<erp>` → `packs/modul/<dikey>` → `packs/sektor/<sektor>` →
`packs/kaynak/<erp>/sektor/<sektor>` (kesişim) → `companies/<slug>` — **en spesifik kazanır.**

Çıktı dizini (`demo/wren-projects/<slug>/`) **türetilmiş artefakttır**, gitignore'ludur, elle
düzenlenmez. `compose()` sadece kopyalamaz; **zaten semantik YAML sentezler**:
`_compose_derived_metrics` yeni view+cube üretir, `_merge_cube_synonyms` mevcut cube metadata'sını
yeniden yazar, `_compose_kpis` çapraz-cube KPI'ları yükler. Yeni bir üretim adımı eklemek bu
kalıbın **beşinci** örneğidir, yeni bir desen değildir.
> ⟳ **DÜZELTME (FAZ −1/A7, ölçüldü @`81ad10b`):** burada üç üreteç sayılıyordu ama
> `compose()` **dört** tanesini çağırıyor — `_compose_relationship_dimensions` (`:179`)
> sayılmamıştı. Ölçüm: `grep -cE '^\s+(_merge_cube_synonyms|_compose_derived_metrics|_compose_relationship_dimensions|_compose_kpis)\(' app/compose.py` → **4**.

Cube ifadeleri **DuckDB/ANSI** yazılır; DuckDB dışı datasource'ta `WrenService._dialect_sql`
hedef lehçeye çevirir (T-SQL: `GROUP BY` ordinal genişletme, `DATE_TRUNC → DATEADD/DATEDIFF`,
Türkçe için `COLLATE Latin1_General_CI_AI` enjeksiyonu).

### 3.4 Motorun verdiği ama kullanmadıklarımız (2026-08-02 denetimi)

**Ölçüm:** `wren` paketi 69 dosya / 738 KB; Dima ondan **3 sembol** kullanıyor (`WrenEngine`,
`context.build_json`, `wren_core.cube_query_to_sql`) — yaklaşık **%4**. Bu tablo olmadan her
tur aynı keşfi sıfırdan yapıyor. **Yeni bir kontrol/garanti yazmadan önce buraya bakılır.**

| Motor yeteneği | Ne verir | Durum |
|---|---|---|
| **`WrenConfig` + `wren/policy.py`** | **Kaynak konumunda (`FROM`/`JOIN`) fail-closed:** MDL-dışı ya da bilinmeyen HER TVF reddedilir. **Kaynak-DIŞI konumlarda** (projeksiyon · alt sorgu · iç argüman) **adlandırılmış 45 okuyucu** bloklanır — bu bir **blocklist**tir, fail-closed bir allowlist DEĞİL (§5, 1.3c) | ✅ **alındı (Faz A3)** — `strict_sql_policy=off\|shadow\|on`, varsayılan `shadow`. 🔴 **Güvenlik SINIRI olarak yazılmaz/satılmaz** |
| **`rowLevelAccessControls` + `SessionProperty` + `dry_plan(properties=)`** | RLS'i **mantıksal planın içine** gömer; SQL'i kim yazarsa yazsın (insan/LLM/ajan) atlatılamaz | ◐ **FAZ 1.1 İNDİ (2026-08-04)** — `always_filter` → RLAC çevirisi, `motor_rls=off\|shadow\|on` (varsayılan **`shadow`**). `15 test: `tests/test_motor_rls.py`` + `7 test: `tests/test_motor_rls_onkosul.py``. ⏳ **SessionProperty henüz YOK** ve bu bilinçli: `always_filter` **sabit** yüklemdir, session'a bağlı bir kural doğmadan `oturum_ozellikleri()` yazmak **çağıranı olmayan bir yetenek** (K3 · ters yetim) olurdu — bkz. §6.3b |
| **`columnLevelAccessControl`** (`requiredProperties`/`operator`/`threshold`) | Kolonu **plandan düşürür**; çıktıya hiç gelmez | ◐ **FAZ 1.2 İNDİ (2026-08-04)** — `sensitivity` → eşik eşlemesi + `motor_cls=off\|shadow\|on` (varsayılan **`off`**, gerekçesi §6.3c). `16 test: `tests/test_motor_cls.py``. ⏳ **`on` KİLİTLİ:** 36 çağrı sitesi hâlâ kimlik geçmiyor; kapı bayrağın o güne kadar açılmasını **engelliyor**. `app/pii.py` son savunma olarak KALIR |
| **Cube `hierarchies`** | Drill sırasını motora beyan eder | ⏸ **bilinçle beyan EDİLMEDİ** — uydurulmuş bir hiyerarşi güvenle yanlış bir drill yolu üretir; sıra ölçülebilir maliyetten okunuyor, bkz. §3.4c |
| **`type_mapping.parse_type/translate_type`** | sqlglot tam tip grameri + lehçeler arası tip çevirisi | ✅ **ALINDI** (2026-08-02, Faz B): `classify_column` artık ham tipi `parse_type` ile **kanonikleştirip** öyle sınıflıyor. Ölçüldü — elle küme **17 gerçek yazımın 13'ünü kaçırıyordu** ve hepsi sessizce `dimension`'a düşüyordu: `numeric(18,2)` (bir PARA TUTARI) gruplama anahtarı, `timestamptz` zaman DEĞİL sayılıyordu. Bir müşteri DB'sini introspect ettiğimizde taslak MDL tutarları boyut yapıp tarihleri zaman ekseninden düşürürdü — kullanıcıya *"şemanı çıkardım"* diye sunularak. Kanonik küme ile **geriye uyum kuyruğu AYRI durur** (`_ESKI_YAZIMLAR`): karışık bir küme, hangi adın kanonik hangisinin yama olduğunu gizler. Motor erişilemezse ham değere düşülür — fail-closed değil, çünkü bilinmeyen tip için doğru varsayılan zaten *boyut*tur. `BIT`/`BOOLEAN` bilinçle dışarıda: bayrakların toplamı bir ölçü değildir. |
| **12 kullanılmayan konnektör** *(⟳ FAZ −1/A8: «17» idi; backend'de hiç geçmeyen sayı **12**)* | BigQuery/Snowflake/Databricks/Trino + `s3_file`/`minio_file` | ❌ yeni müşteri = **kod yazmadan** bağlanma |
| **`context.validate_project()`** | 9 yapısal kural (PK var mı, `table_reference` XOR `ref_sql`, ilişki hedefi…) | ✅ **ALINDI** (2026-08-02, Faz B): `compose_and_build` artık `build()`'den **önce** çağırıyor. `error` → **fail-closed**, MDL üretilmez (bozuk zeminden üretilen MDL, hatayı sorgu anında kullanıcının yüzüne çıkarır — `dry_plan` kolon varlığını denetlemez, §5); `warning` → loglanır, akışı durdurmaz. Kendi doğrulayıcımız YAZILMADI, motorunki **çağrıldı** (test kural adlarının gövdeye kopyalanmadığını kilitler). Ölçüldü: dört demo projesinin **dördü de 0 hata / 0 uyarı** — açmak hiçbir meşru yolu kırmıyor. |
| **`data_source` statement_timeout** | Per-datasource sorgu zaman aşımı | ✅ alındı — **ama motorun kendisi mssql'i unutmuş**, bkz. §3.4b |
| **`migrate_manifest_json` / `is_backward_compatible`** | MDL layout göçü ve geriye uyum | ❌ hiç çağrılmıyor |

**Bilerek ALINMAYANLAR** (gerekçeleri kalıcı): `wren.memory` — `app/vqr.py` bu iş için üstün
(Türkçe'de e5-large > MiniLM; depo Postgres'te ve tenant-kapsamlı, LanceDB dosya deposu
Railway'de kalıcı değil). `mcp_server.py` — Dima'nın HTTP API'si işlevsel üst kümesi; ajan
yüzeyi kendi araç kaydımız üstüne kurulur.
✅ **MCP YÜZEYİ İNDİ** (FAZ 4.5 · `app/mcp.py` + `app/routers/mcp.py`, bayrak
`mcp_yuzeyi=off`): **ince çevirici**, kendi kaydını kurmuyor — `tools.llm_araclari()`'yi
ve `authorize()` süzgecini okuyor. 🔴 Değişmez kapıyla kilitlendi
(`tests/test_mcp.py`, 9 test): MCP'den çağrılan araç `Planlayici.calistir()`'in **aynı
dört kapısından** (`KAYIT · yetki · deterministik-önce · bütçe`) geçiyor ve **aynı
`Adim` makbuzunu** üretiyor; `importlib`/`arac.cagir` MCP'de **AST ile yasak**.
`genbi`/`dbt`/`profile` — bugün müşteri
senaryosu yok. **`_dialect_sql` duplicate DEĞİL**: `cube_query_to_sql` DuckDB verir, `dry_plan`
hedef lehçe bekler; aradaki köprüyü wren sunmuyor.

### 3.4b Sorgu zaman aşımı — motorun kendisi MSSQL'i unutmuş (Faz B) ✅

*"Motor zaten yapıyorsa yazma"* (§5) kuralının **sınırının** ölçüldüğü yer. Motorun
`DataSource.get_connection_info()`'su `statement_timeout`'u **yalnız dört** datasource için
enjekte ediyor — `match` dalları okundu:

```
case DataSource.postgres:      # -c statement_timeout=180s
case DataSource.clickhouse:    # max_execution_time=180
case DataSource.trino:         # query_max_execution_time=180s
case DataSource.bigquery:
```

**`mssql` dalı YOK.** Konnektör onu *onurlandırıyor* (`connector/mssql.py`:
`connection.timeout = statement_timeout`) ama **kimse geçmiyordu** — ve üretimdeki
tenant'larımız (gitas, atiksan) tam olarak **mssql**. Yani kilitlenmiş bir sorgu **süresiz**
asılabiliyor ve isteği de kendisiyle askıya alıyordu. postgres'te ise 180 sn: bir toplu iş
için makul, **etkileşimli bir BI cevabı için değil**.

`WrenService._zaman_asimli_baglanti()` (`DIMA_DB_STATEMENT_TIMEOUT`, varsayılan **60 sn**):
mssql → `kwargs.statement_timeout` + ODBC `Connect Timeout`; postgres → `options -c
statement_timeout` (motorun `if not in options` kapısı bizimkini geçirir) + `connect_timeout`.
**Diğer datasource'lara zaman aşımı UYDURULMAZ**: konnektörün beklemediği bir anahtar
bağlantıyı kırabilir — motorun kendi varsayılanı geçerli kalır ve bu **sessiz değil** (log).

**Motor yolu VE ham konnektör** ikisi de alır. Canlı olayda (2026-07-25) `/schema`'yı asan
sorgular tam olarak `_connector()` üzerinden giden **değer indeksi** sorgularıydı; motor
yolunu korurken ham konnektörü korumasız bırakmak kapıyı kilitleyip pencereyi açık unutmak
olurdu.

**`_db_reachable` KALDIRILMADI.** Plan bu maddeyi *"TCP ping'in YERİNE"* diye yazmıştı;
ölçünce ikisinin farklı şeyleri yakaladığı görüldü:

| | TCP ping (3 sn) | statement timeout |
|---|---|---|
| Tünel düşmüş (canlı olay) | ✅ yakalar | ❌ hiç bağlanamaz, bu kapı hiç açılmaz |
| DB ayakta, sorgu kilitli | ❌ **anında "erişilebilir" der** | ✅ yakalar |

Birini ötekinin yerine saymak, kapanmamış bir boşluğu kapanmış göstermek olurdu.
17 test: `tests/test_sorgu_zaman_asimi.py`.
### 3.4c Boyut sırası: `hierarchies` yerine ÖLÇÜLEBİLİR maliyet (Faz B)

Plan *"`drill.py`'nin ELLE YAZDIĞI drill sırasını motora beyan et (`hierarchies`)"*
diyordu. Ölçünce görüldü ki **elle yazılmış bir sıra bile yoktu**: `available_dimensions`
boyutları **YAML beyan sırasında** döndürüyordu — hiçbir anlamı olmayan bir sıra.

Faz F3'e kadar bu zararsızdı (`/ask/contribution` 6 boyutun **hepsini** tarıyor). Uyarının
nedeni (§11.6e, arka plan işi) ise yalnız **2** tarayabilir — ve `parti` cube'unda **15
boyut** var (`kalite` 11). Yani beyan sırası, kullanıcının gördüğü gerekçeyi **belirler**
hale geldi.

**`hierarchies` BEYAN EDİLMEDİ ve bu bilinçlidir.** Demo cube'ları için bir hiyerarşi
(*"makine → bölüm"*, *"il → ilçe"*) uydurmak, `pvm:` eşleştirmesinde ve `target:` hedefinde
reddedilen şeyin aynısı olurdu: **yanlış bir hiyerarşi, güvenle yanlış bir drill yolu**
üretir ve kullanıcı onu sorgulamaz.

Onun yerine sıra **zaten üretilen beyanlardan** okunur — `dimension_origin` (hop sayısı) ve
**fan-out sertifikası** (Faz D2):

| Öncelik | Kural | Gerekçe |
|---|---|---|
| 1 | Kendi tablosundaki boyut (hops=0) | JOIN yok: hem ucuz hem fan-out riski yok |
| 2 | Az sıçramalı | Her sıçrama bir maliyet ve bir risk |
| 3 | `olculdu:saglikli` → `olculmedi` → `olculdu:riskli` | **Ölçülmemiş bir ilişki BİLİNMEZDİR; riskli ölçülmüş bir ilişki BİLİNEN bir sorundur** (fan-out toplamları şişirir) — bilinmeyeni bilinen-bozuğun önüne koymak doğrudur |

Bu sıra **açıklayıcılık hakkında bir iddia DEĞİLDİR** — onu `contribution.rank_dimensions`
sorguyu koştuktan **sonra** ölçer. **Maliyet ve güven** hakkındadır: kesme yapılacaksa,
denenmeye önce ucuz ve güvenilir olanlar değer. Sıra **kararlıdır** (eşitlikte beyan sırası
korunur), yoksa aynı soru iki kez sorulduğunda farklı chip'ler görünürdü.

**Atlananlar ADIYLA raporlanır** (`taranmayan_adlar`): bir sayı (*"3 boyut taranmadı"*)
kullanıcıya hangi soruyu sorabileceğini söylemez; ad söyler (*"peki renk bazında?"*).
Bildirimde, `/ask/contribution` yanıtında ve `ContributionLayer`'da görünür.


---

## 4. DEĞİŞMEZLER — "bunu bozarsan sistem yalan söyler"

1. **LLM'e KİŞİSEL VERİ gitmez.** ✅ *CI testi var:* `tests/test_llm_veri_sizintisi.py`.

   > ⚠️ **Bu madde 2 Ağustos 2026'da DÜZELTİLDİ.** Eski metin *"LLM ham veri görmez … hücre
   > değeri asla"* diyordu ve **doğru değildi**: `llm._schema_prompt` her modelin her VARCHAR
   > kolonundan örneklenmiş **1391 gerçek değeri** prompt'a yazıyordu — çalışanların tam
   > ad-soyadı, SGK numaraları, IBAN'lar dahil. `cube_router.build_catalog` ise daha dar bir
   > politika uyguluyordu (358 değer): **aynı LLM'e iki farklı gizlilik politikası.** Demo'daki
   > TCKN maskesi de kodda değil **verinin kendisindeydi**. Maddenin kendi cümlesi
   > (*"bu bir CI testi olmalı"*) yıllardır yerine getirilmemişti.

   Doğru ve uygulanan kural **iki katmanlıdır**:

   | Katman | LLM ne görür | Ne göremez |
   |---|---|---|
   | **T1 — sorgu üretimi** (Intent-JSON / Discovery) | Şema/metrik/boyut adları + `sensitivity: normal` kolonların enum değerleri | Hücre verisi, `person`/`special` kolon değerleri, ham satır |
   | **T2 — yorum/sohbet** (planlı, Faz G) | Kullanıcının zaten yetkiyle sorduğu ve gördüğü, PII maskeli **agrege sonuç** | Ham satır, alttaki tablolar, başka kiracı, **SQL yazma yetkisi** |

   Sınır *"veriyi kim görüyor"* değil **"veri nereye gidiyor"**dur: `cube_router.route()`
   süreç içinde çalıştığı için değerleri görmeye **devam eder** (*"Aylin Bulut'un firesi"*
   deterministik çözülebilsin diye); süzgeç **prompt sınırındadır**
   (`app/sensitivity.py::prompt_safe_values`).

   Sınıflandırma **beyanla** yapılır (`sensitivity: person|special|normal`, model YAML'ında);
   ad-tabanlı tanıma yalnız bir **emniyet ağıdır** ve `operator`/`sorumlu` gibi şemaya özgü
   adları yakalayamaz — onlar beyan edilir. Üreteç calc kolonları hassasiyeti **miras alır**
   (yoksa `partiler.operator` → `tamir_rework.partiler_operator` olarak yeniden doğup sızar).
2. **Yalnız read-only.** `guard_sql` `SELECT`/`WITH` dışını reddeder; DDL/DML asla çalıştırılmaz.
3. **LLM SQL yazmaz.** Varsayılan yol Intent-JSON'dur. Ham SQL **yalnız** Discovery'de, son çare.
4. **Her cevap bir Query Contract üretir**: SQL + `mdl_version` + parametreler + sonuç hash'i +
   zaman. Yeniden çalıştırılabilir olmalıdır.
5. **`always_filter` fail-closed'dır.** Sessizce düşmesi **P0 hatadır** (`CANCELLED = 0` gibi iş
   filtrelerini taşır).
6. **Deterministik yol sayı uydurmaz.** Belirsizlikte **sorar** (chip), tahmin etmez. Tek
   tanınmayan kelime → cevap yok **ve öneri de yok** (ADR-0008: *yanlış öneri, önerisizlikten
   kötüdür*).
7. **Auth her zaman zorunlu**, kapatma bayrağı yoktur. Güvenlik sınırı `authorize()`'dır; feature
   flag onu **gevşetemez**.
8. **DB→dosya tek yönlü.** `TenantConfig` satırı olan tenant'ın `company.yml`'i TÜRETİLMİŞTİR;
   elle düzenleme materializer'da ezilir.
9. **Kanıt silinmez.** Deprecate edilen ölçü NL'den gizlenir ama silinmez; soft-delete her yerde
   (ADR-0019).
10. **MDL kaynağı wren-projesidir.** Şema `target/mdl.json`'dan okunur; elle uydurma yok.

---

## 5. YAPILMAYACAKLAR — gerekçesiyle

> Bu tablo, geçmişte yapılmış ya da yapılmak üzere olan hataların kaydıdır. Her satırın arkasında
> ya çalıştırılmış bir deney ya da doğrulanmış bir sektör emsali vardır.

| Yapma | Neden |
|---|---|
| **Join planlayıcı yazma** | `wren_core` "önceden-bildirilmiş adlandırılmış geçiş" ailesinde (Looker explore, Malloy `join_one`, Cube *views*, Snowflake semantic views). Bu ailenin çözümü bir **üreteçtir**, planlayıcı değil. Cube Dijkstra'yı yazdı, sonra kendi dokümanında *"views should be used where possible"* dedi. MetricFlow 2 sıçramada kapattı ve fan-out'u **yasakladı**. Planlayıcı = denetlenemez tie-break = Query Contract'ın varlık sebebine aykırı. |
| **`join_type`'a güvenme** | Motor onu **okumuyor** (ölçüldü): MANY_TO_ONE / ONE_TO_MANY / ONE_TO_ONE / MANY_TO_MANY → **aynı SQL**. Yön `condition`'dan türetilir, güvenlik **ölçülen anahtar tekilliğinden** gelir. `relationships.yml`'deki cardinality bir **yorumdur**. |
| **Ters yön (ONE_TO_MANY) handle üretme** | Join pruning kompozisyonelliği bozar: aynı cube, aynı boyut, yalnız ölçü listesi farklı → makine sayısı **3 → 7.038**, kapasite **4.700 → 11.026.200** (ölçüldü). Bir ölçünün değerinin SELECT'teki *diğer* ölçülere bağlı olması, "her cevap kanıtlanabilir" tezi için mümkün en kötü hata sınıfıdır. |
| **`dry_plan`'ı doğrulama kapısı sanma** | `dry_plan` **kolon varlığını denetlemiyor** (ölçüldü: uydurma kolon plandan geçti, çalıştırmada `BinderException`) — `strict_mode` bunu da **çözmez**, o tablo/fonksiyon politikasıdır. *"Motor doğrular"* ifadesi **tablo** için geçerlidir, kolon için değil. Kolon doğrulaması `tests/test_member_sweep.py`'nin **üye taramasıdır** — her ölçü/boyut **gerçekten derlenip çalıştırılır** (`LIMIT 0` değil: dosyada öyle bir kısayol yok, sorgular **koşar**; ⟳ FAZ −1/A6'da ölçüldü, 113 satır · 5 test); **terfi onayı o taramayı hâlâ çalıştırmıyor** (§6.2). ⚠️ 2026-08-02'de düzeltildi: `WrenConfig` artık kuruluyor (aşağı bak) ama bu, kolon boşluğunu kapatmaz — iki ayrı mesele. |
| **`guard_sql`'i güvenlik politikası sanma** | O bir **SELECT-only kapısıdır**, iki regex'ten ibarettir ve `SELECT * FROM read_csv('/etc/passwd')`'i **geçirir** (ölçüldü). Politika motoru `wren/policy.py`'dir. 2026-08-02'ye kadar **ölü koddu** çünkü `WrenEngine`'e `config` hiç geçirilmiyordu. Bugün o saldırıların yine de patlaması **DataFusion'ın fonksiyonu tanımamasındandır** — yani savunma **tesadüfi**. Bkz. §3.4. |
| 🔴 **`strict_sql_policy=on`'u bir GÜVENLİK SINIRI sanma** *(FAZ 1.3c — motorun **kendi kaynağından** doğrulandı)* | Motor iki ayrı rejim uyguluyor ve ikisi aynı şey değil: **kaynak konumu (`FROM`/`JOIN`) gerçekten fail-closed** (`_check_tables` bilinmeyen HER TVF'yi reddeder), ama **kaynak-dışı konumlarda** (projeksiyon · alt sorgu · iç argüman) güvenlik sınırı **adlandırılmış bir listedir** (`_DATA_READER_NAMES`, **45** ad). `wren/policy.py`'nin kendi yorumu: *"you cannot allowlist every scalar function that may appear in a projection or WHERE clause… a reader that is **not enumerated** here **will pass**… The list must therefore be **MAINTAINED PER-CONNECTOR**."* → **Sınır şudur:** `motor_rls` (1.1) **+** `enforce_query` (1.3b) **+** `denied_functions`. 🔴 **ÖLÇÜLDÜ (2026-08-04):** 45 adın **0'ı** SQL Server okuyucusu — ve `wren_service.py:143` *"üretimdeki tenant'larımız (gitas, atiksan) tam olarak **mssql**"* diyor. Yani motorun *"konnektör başına bakımlı tutulmalı"* uyarısı **ana konnektörümüzde hiç uygulanmamış**. Kapı: `tests/test_blocklist_tazeligi.py`. |
| **`except Exception` ile motoru sarma** | Kendine-referanslı ilişki + calc kolon → Rust'ta **PANIC** (`lineage.rs:146`, `unwrap() on None`). `PanicException` MRO'su `(PanicException, BaseException, object)` — **`except Exception` yakalamaz.** Hesap planı parent, BOM parent, org şeması: ERP'lerde standart. |
| **Kelimeye özel regex/keyword yaması** | Kayıtlı desen: aynı kök neden (`_uncovered`'ın substring körlüğü) defalarca kelimeye özel yamayla geçiştirildi, kök neden hiç düzeltilmedi. **Kural: kök nedeni düzelt, örneği değil.** (ADR-0008 disiplini) |
| **NL-benzerlik cevap cache'i** | Yapısal olarak benzer ama anlamsal olarak farklı Türkçe sorular yanlış cevabı **güvenle** döndürür. Anahtar `contracts.cube_query_hash()` olmalı (Faz 4.3'te yazıldı: `cq ⊕ mdl_version ⊕ company ⊕ tenant`). **Sonuç cache'inin kendisi bilerek KURULMADI** — tekrar oranı ölçülmedi; ölçülmemiş ihtiyaç için altyapı kurulmaz. ⟳ **Primitifin İLK TÜKETİCİSİ geldi (FAZ 5.13a @`ade92bb`): `ContractStore.find_previous()` — "hayalet seri".** ⚠ Hayalet seri bir cache **DEĞİLDİR**: bir sonucu **döndürmez**, bir öncekinin **var olduğunu** söyler (`{contract_id, ts, row_count, result_hash}`). Aradaki fark, cevabın **nereden geldiğidir** — ve cache kararı hâlâ ölçüme bağlı. Hash'in sözleşmesi *"aynı hash ⇒ aynı ÇIKTI"*dır: `filters` sıraya duyarsız (saf AND), `measures`/`dimensions` sıraya **duyarlı** (kolon ve GROUP BY sırasını belirler), akış bayrakları (`period_confirmed`) düşürülür. `result_hash` ile karıştırma — o *"sayılar değişti mi"* sorar ve satır sırasını umursamaz. |
| **Simetrik agregat (Looker/Omni deseni)** | Lehçe-bağımlı (Looker 40 lehçelik destek tablosu yayınlıyor), `DECIMAL(38,0)` taşması, yalnız sum/avg/count, ve hata **sorgu anında** kullanıcının yüzüne çıkıyor. Anahtar tekilliği ölçülebiliyorken kalıcı vergi ödemek anlamsız. |
| **Tenant başına forklanmış MDL'i varsayılan yapma** | N-yollu şema bakımı. Varsayılan: paylaşılan model + motor-seviyesi RLS; fork yalnız istisna. |
| **Grafik üretimini LLM'e verme** | `viz.py`'nin iki katmanlı deterministik `analyze()`/`recommend()` tasarımı bilinçli bir karardır (Show-Me / Cleveland-McGill, ADR-0024) ve upstream kaynak okunarak doğrulanmıştır. LLM'e Vega üretimi determinizm felsefesiyle çelişir. |
| **Bir cevabın `source`'unu gizlemek/eşitlemek** | `cube` ile `llm:*` **farklı garantiler** taşır. Rozet UI süsü değil, sözleşmedir. `_llm_source()` bilinmeyen sağlayıcıda bile `:` içeren bir değer döndürür ki LLM cevabı asla deterministik görünmesin. |
| **Aynı kararı iki motorda ayrı ayrı verme** | Ölçüldü (Faz C): `interpret._classify` ile `viz.analyze` kolon rollerini **bağımsız** çıkarıyordu — `viz` `cube_query`'den otorite alıyor, `interpret` almıyordu; zaman-adı sözlükleri de farklıydı. Aynı cevapta grafik zaman serisi çizerken cümle onu kategori sanabiliyordu ve **ikisi de "deterministik" rozetliydi**. Aynı sınıf: `_is_num` **7 kopya / 3 semantik** (`"1,5"` bir motorda ölçü, diğerinde kategori), Türkçe biçimleme **2 farklı eşik** (`150,5` sohbette `151`, e-postada `150,50`), ay kısaltmaları 3 kopya, z-skoru `drill.py`'de *"yeniden kullanıyorum"* denip elle kopyalanmış. Tek kaynak: `app/result_shape.py` · `app/fmt.py` · `app/stats.py`. |
| **Zaman kolonunu sabit kodlama** | `kpi.py` üç yerde `"tarih"` yazıyordu, oysa `yoy.time_dim_of` cube'un zaman boyutunu **zaten çözüyor**. `donem_tarih` kullanan cube'da sorgu ya patlar ya — ad tesadüfen varsa — **sessizce yanlış pencere** kurar. Zaman boyutu her zaman **beyandan** okunur. |
| **Aynı sınır tanımını iki mekanizmada ayrı yazma** | `_uncovered` kelimeleri `[a-z]+` ile ayırıyor, `_syn_hit` ise `\b` kullanıyordu — ve Python'da `_` bir KELİME KARAKTERİDİR. Sonuç: kapsam kapısı kendi eşleşmelerini tanımıyordu (*"yas_grubu bazında işlenen kg"* reddedildi). Kelime sınırı tek tanımdan gelir: `(?<![a-z0-9])`. |
| **Tanımadığın kelimeyi yazım hatası varsayma** | Soru bir cube'a çözüldüğünde "bilinmeyen" yalnız O CUBE'a görelidir. Kelime BAŞKA bir cube'un gerçek terimiyse bu bir yazım hatası değil **çapraz-konu sinyalidir**; düzeltme önermek anlamsız chip üretir (ölçüldü: *"«verimlilikleri» yerine «derinligi» mi?"*). |
| **`Dima-0-100` dosyasını mimari otorite sayma** | §8. |

---

## 6. Bilinen açık kusurlar (2026-08-02 itibarıyla, hepsi doğrulandı)

Bunlar "belki" değil, **ölçüldü**. Yeni gelen biri bunları keşfedip "acaba ben mi yanlış anladım"
diye zaman kaybetmesin.

### 6.1 Sessiz-yanlış üretenler (en tehlikeli sınıf — cube rozetiyle geliyorlar)
- ✅ **düzeltildi (2026-08-02, Faz 0.4)** — **`_uncovered` herhangi-konum substring kullanıyordu**
  (`cube_router.py`). `kar⊂ankara`, `mal⊂imalat`, `mal⊂maliyeti`, `fire⊂firesiz`, `son⊂personel`,
  `gun⊂uygun`, `kar⊂kargo`, `reddedil⊂reddedilmeyen`. Sonuç: `"firesiz partilerin cirosu"`
  **fire toplamını** döndürüyordu — sorulanın tam tersi metrik, `source="cube"` rozetiyle.
  Yerine iki ayrı mekanizma: `_covers()` (önek + olumsuzluk-eki reddi + geçerli Türkçe ek
  zinciri) ve `_STOP_EXACT` (dolgu köklerinden gerçek iş kelimesi yutanlar: `ver→veresiye`,
  `tek→tekstil`, `turu→turuncu`, `sana→sanayi`, `getir→getiri`). 48 regresyon testi.
  **Yan etki (iyileştirme):** `"personel bazlı verimlilikleri karşılaştır son 6 ay"` artık
  Discovery yerine çapraz-konu netleştirmesi veriyor (`oee` / `İK / bordro` / `parti` chip'leri) —
  çünkü `"son"` kelimesi `"personel"`i sahte kapsıyordu.
  **Ders:** iki tasarım denemesi test tarafından düşürüldü ve ikisi de kodda kayıtlı —
  (a) uzunluk-oranı sezgisi meşru çekimleri kesti (`verim→verimliliği`, `renk→renklerine`);
  (b) elle kısaltılmış dolgu köklerine (`grafi`) biçimbirim kuralı uygulamak grafik isteyen
  her soruyu kapıya takıyor. **Ayrım uzunlukta değil biçimde; ve iki farklı sorun iki farklı
  mekanizma ister.**
- ✅ **düzeltildi (2026-08-02, Faz D3)** — **`_syn_hit` aynı hastalıktaydı** ve `_uncovered`'dan
  **daha geniş** bir yüzeyi vardı: her cube/ölçü/boyut eşleşmesi ondan geçiyor.
  **`route()`'a bakarak görünmüyordu** — orada kapsam kapısı zaten çekiliyordu. Zarar, kapsam
  kapısından GEÇMEYEN takip yollarındaydı (`deterministic_refine`, `cross_cube_add`,
  `cross_cube_dim_switch`; takip sorusu eksik cümledir, kapsam kapısı uygulanamaz):

  | Takip sorusu | Eklenen boyut | Kök |
  |---|---|---|
  | *"kıyaslama yap"* | `ik.yas_grubu` | `yas` ⊂ `kıyaslama` |
  | *"önceki ay ile kıyasla"* | `ik.donem` + `ik.yas_grubu` | `ay` ⊂ …, `yas` ⊂ `kıyasla` |
  | *"neden arttı"* | `bakim.mudahale_eden` | `eden` ⊂ `neden` |
  | *"detay ver"* | `ik.donem` | `ay` ⊂ `detay` |

  Fazla bir GROUP BY kolonu **her hücredeki sayıyı değiştirir** ve cevap `source="cube"`
  rozetiyle gelir. Faz 0.5'in `_match_dims` tahkimi bunu kurtaramaz — tahkim *hangi eşleşme
  kazanır* sorusunu çözer, *bu eşleşme gerçek mi* sorusunu değil.
  Kural `_covers`'ınkiyle **tek kaynağa** indirildi (`_ek_gecerli`): kelime başı çapası +
  olumsuzluk eki reddi + geçerli ek zinciri. Ölçülen katalog: 449 boyut sinoniminin 64'ü
  ≤4 harf ve tam-kelime işaretsizdi.
  **Sınır `\b` DEĞİL:** Python'da `_` bir kelime karakteridir, dolayısıyla `\b` `yas_grubu`
  içinde `grubu`'nun önünde sınır görmez — `_uncovered` ise o metni `[a-z]+` ile ZATEN iki
  kelimeye ayırıyordu. İki mekanizma aynı sınırı görmezse kapsam kapısı **kendi eşleşmelerini
  tanımaz** hale gelir (canlı test vakası: *"yas_grubu bazında işlenen kg"* reddedildi).
  Sınır bu yüzden `(?<![a-z0-9])`.
  **Yan etkiler (ikisi de iyileştirme, ölçülerek doğrulandı):** (a) `ik` cube'u kimlik sinonimi
  `"ik"` ile `verimlil**ik**leri` içinden eşleşmeyi bıraktı; (b) *"personel bazlı verimlilikleri
  karşılaştır"* artık `"personel"` yerine **`"verimlilikleri"`** kelimesini işaretliyor — çünkü
  personel kırılımı `parti`de gerçekten VAR, cevaplanamayan şey `verimlilik` ölçüsüdür.
- ✅ **düzeltildi (2026-08-02, Faz D3)** — **çapraz-konu terimi "yazım hatası" sanılıyordu.**
  Soru bir cube'a çözüldüğünde `partial_unknowns` yalnız O CUBE'a göre bilinmeyenleri döndürür;
  bulanık eşleştirici bunları düzeltilecek yazım hatası sanıyordu. Ölçülen çıktı:
  *"«verimlilikleri» yerine «derinligi» mi demek istedin?"* — `renk_derinlik` boyutundan gelen
  anlamsız bir öneri. Artık kelime TÜM katalogda gerçek bir terimin çekimiyse (burada `verim`
  → `oee`) düzeltme **denenmez**; bu bir yazım hatası değil bir **çapraz-konu sinyalidir**.
  Aynı gerekçeyle `cube_only_match` da *"hangi ölçüyü istiyorsun?"* demeyi bırakır — kullanıcı
  ölçüyü zaten söylemiştir, yalnız o ölçü orada yoktur.
  **Kapı GİRDİDE değil ÇIKTIDA:** `leftover`'ı filtrelemek denendi ve `value_index`in
  KOMŞU KELİME İKİLEMESİNİ (*"kontinu kasr"* → *"kontinu kasar"*) kırdı — doğru yazılmış
  komşuyu havuzdan çıkarmak ikilemenin kurulmasını imkânsız kılıyor.
- ✅ **düzeltildi (2026-08-02, Faz C4)** — **`yoy.py`'nin MoM hizalaması kırıktı.** 93 satır,
  **sıfır doğrudan test**, dört üretim tüketicisi (`report.py`, `routers/dashboards.py`, `/ask`
  iki yerde) + `contribution.py` çıktı şekline bağımlı. Şüpheyi doğuran satır tek başına
  yeterliydi: `shift = 1 if mode == "yoy" else 1` — **iki dal aynı**. `_merge` önceki dönem
  anahtarının **yılını** kaydırıyordu; YoY'da doğru (2025-03 → 2026-03), MoM'da **imkânsız**
  (2026-02 → 2027-02, cari 2026-03 ile hiç eşleşmez). Ölçüldü: zaman kolonlu MoM'da `_gecen`
  **her zaman `None`** — yani *"geçen aya göre aylık ciro"* sessizce **boş kıyas kolonu**
  döndürüyordu. Boyut kırılımında (zaman kolonu yokken) çalıştığı için kusur gözden kaçmıştı.
  Yerine mod-farkında dönem aritmetiği (`_ileri`, ay indeksi üzerinden — yıl devrini yönetir).
  **Önce test yazıldı** (3 kırmızı), sonra dokunuldu: `tests/test_yoy.py`, 15 test.
- ✅ **düzeltildi (2026-08-02, Faz C3)** — **`kpi.py` zaman kolonunu `"tarih"` diye sabit
  kodluyordu** (üç yerde: aralık taraması ve iki pencere `WHERE`'i). Artık `spec["time_column"]`
  beyanından okunur, yoksa `"tarih"` (geriye uyum). **Kapsam sınırı dürüstçe kaydedilir:**
  `resolve_kpi_series`'in bugün **üretimde çağıranı yok** (`_try_kpi` yalnız skaler kart
  döndürüyor) ve demo-boyahane'de **KPI tanımı yok** — düzeltme SQL düzeyinde test edildi,
  uçtan uca gösterilemedi.
- **Sayılar kapsam kapısına görünmüyor** (`[a-z]+`). Faz 0.4'te bilinçli olarak ele alınmadı:
  düzeltmek için dönem/gran sözlüklerinin sayıları da `known`'a eklemesi gerekir, yoksa
  `"son 3 ay"` gibi çalışan sorular kırılır. Aynı sınıfta 2 harflik kökler (`ay`, `kg`) de
  `known`'dan eleniyor — `tests/test_coverage_gate_affix.py` bunu bir sınır kaydı olarak tutuyor.
- ✅ **düzeltildi (2026-08-02, Faz 0.5)** — **`_match_dims` tahkim yapmıyordu**:
  `"yaş grubu bazında fire oranı"` → `['ham_grup','yas_grubu']`, `"ham grubu…"` → **üç** boyut.
  Kök neden: `ham_grup` ve `yas_grubu` ortak `"grubu"` sinonimini taşıyor. Fazla kolon GROUP
  BY'ı böler — satır sayısı da her hücredeki **sayı** da değişir, ve cevap `source="cube"`
  rozetiyle gelir. `_match_measure`'ın zaten uyguladığı **en-spesifik-eşleşme-kazanır** kuralı
  boyut tarafına da eklendi. **Eşit eşleşmeler** (iki boyut aynı sinonimle) bilinçli olarak
  çözülmedi — o gerçek bir belirsizliktir ve Faz 3.1'de `route()`'un chip sorması gerekir.
- **kısmen düzeltildi (2026-08-02, Faz 3.3)** — **olumsuzluk ifade edilemiyordu**: Rust **12**
  filtre operatörü destekliyor (`eq neq in not_in gt gte lt lte contains starts_with is_null
  is_not_null` — çalıştırılarak doğrulandı, geçersiz operatör gürültülü reddediliyor), Python
  **4** üretiyordu. `parse_cube_query` operatörü denetlemiyor, `cube_sql` iletiyor, Rust
  uyguluyor — eksik olan yalnız NL→operatör köprüsüydü.
  - ✅ **DIŞLAMA** (`neq`/`not_in`) açıldı: *"beyaz hariç rework"* artık beyazı **eler**, eskiden
    beyazın rework'ünü `source="cube"` rozetiyle **döndürüyordu**. Kural kelime listesi değil
    **konumsaldır**: Türkçe son-çekim edatı tümlecini izler, o yüzden edatın eşleşen değerden
    SONRA gelmesi aranır; aradaki çekim ekleri (Faz 0.4'ün `_SUFFIX_CHAIN_RE`'si yeniden
    kullanılır), bağlaçlar ve aynı koordinasyona giren diğer değerler yutulur. Karma ifade
    (*"beyaz hariç siyah"*) **dürüst red** — hangi değerin hangi tarafta olduğu çıkarılamaz.
  - ✅ **ÖNEK/İÇERME** açıldı ama **operatöre değil, değer indeksine** bağlandı: motorun
    `starts_with`/`contains`'i **harf duyarlıdır** (ölçüldü: `starts_with('B')` → `['Beyaz']`,
    `starts_with('b')` → `[]`) ve Dima'nın NL katmanı `_norm` ile küçültür. Doğrudan bağlamak
    kullanıcı "beyaz" yazdığında **güvenle boş** sonuç döndürmek olurdu — `None`dan kötü, çünkü
    boş sonuç "veri yok" gibi okunur. Bunun yerine önek gerçek değerlere çözülüp `in` kurulur;
    boyut da **kelimesinden değil** değerlerin nerede bulunduğundan gelir.
  - ❌ **`is_null` / eşik-tabanlı olumsuzluk açık**: *"firesiz partilerin cirosu"*,
    *"maliyeti girilmemiş partiler"*. Bunlar kategorik DEĞER dışlaması değil, bir ÖLÇÜ ya da
    var-olmayan bir kolon üzerinde koşuldur; bu katalogda tutamak yoktur (`maliyet` ne boyut
    ne ölçü). Faz 0.4 sayesinde en azından **sessiz-yanlış değil dürüst red** üretiyorlar:
    `-sIz`/`-mAyAn` ekleri `_covers`ta izinli çekim sayılmadığı için kapsam kapısına takılıyorlar.

### 6.1b Çoklu-ay dönem ayrıştırması KAPANDI (Faz -0.5a/d) ✅

**Ölçülen kusur (canlı örnek):** *"ocak şubat mart ayları için ciro değişim trendi nedir"*
→ dönem **"tümü"** alındı. Kod okununca **dört bağımsız mekanizmanın** aynı anda kırıldığı
görüldü. İkisi bu turda kapandı:

**(1) Çözücü tek ay çözüyordu.** `_month_range_filters` `re.search` kullanıyordu — yalnız
İLK ayı yakalıyordu. Asıl tehlike gözlemlenen "tümü" hatası DEĞİLDİ: kapsam kapısı geçilmiş
olsaydı sistem **sessizce Ocak-only** bir cevap verirdi, `source="cube"` rozetiyle — §6.1'in
*"en tehlikeli sınıf"* tanımının aynısı.

**Asimetri kodda kayıtlıydı:** `_period_hit_words` 1 Ağustos'ta `finditer`'a geçirilmişti
(kendi yorumu bunu yazıyor) — **KAPI** çoklu ay görüyordu, **ÇÖZÜCÜ** görmüyordu. Sonuç:
*"kullanıcı NE KADAR çok dönem detayı verirse, kapı O KADAR az soru soruyor."*

Bugün: **bitişik** aylar tek bir `gte/lte` aralığına çevrilir (mevcut AND-zinciri
sözleşmesinde ifade edilebilir); **ayrık** aylar (`"ocak ve mart"`) çözülmez ve
`cozulemeyen_ay_listesi()` ile dönem kapısına **haber verilir** — kapı sorar, sessizce Ocak
alınmaz. Ayrık kümenin kendisi bir OR/küme operatörü gerektirir; o bir **sözleşme
genişletmesidir** ve burada VAAT EDİLMEDİ.

**Netleştirme cevaplanabilir bir soru sorar.** Jenerik dönem chip'leri ("Bugün · Bu hafta ·
Bu ay") iki belirli ay isteyen kullanıcıya hiçbir şey söylemez. `ay_netlestirme()` onun
**kendi saydığı ayları** + **kapsayan aralığı** sunar; her chip'in sorgusu gerçekten
çözülebiliyor (testle kilitli). Yeni yüzey açılmadı — aynı `suggestions` alanı.

**(2) Fresh Intent yolunda dönemi hesaplayan yoktu.** `llm.py`'nin prompt'u LLM'e tarih
yazmayı AÇIKÇA yasaklıyor (*"sistem hesaplar"*) ama "sistem" o beyanı yalnız İKİ yolda
uyguluyordu: `route()` kendi içinde, ve takip-düzenleme dalı (`_resolve_period`). **Taze
Intent-JSON (`cube+llm`) yolunda hesaplayan kimse yoktu** — LLM yazmıyor, sistem de
hesaplamıyor, sonuç sessizce tüm zamanlar. Bu bir politika değil bir **asimetriydi**: beyan
verilmiş, bir yol uyguluyor, öteki uygulamıyor. `date_filters` **tek kaynaktır** ve artık üç
yol da onu çağırır; kural ikinci kez yazılmadı.

`_resolve_period` doğrudan çağrılmadı — o `"tarih"` adını **sabit kodluyor** ve zaman boyutu
farklı adlı bir cube'da var olmayan bir kolona filtre yazardı. Cube'un kendi beyan ettiği
zaman boyutu kullanılıyor (`route()` ile aynı).

**Hâlâ AÇIK (§1.6'nın kalan iki maddesi):** `_period_gate`'in dört-yollu ilk baypası
(`period_confirmed | period_optional | not time_dims | timeDimensions`) ve takip
düzeltmesinin çapasızlığı (`context.Baglam` kullanıcının **çözülemeyen ham ifadesini**
saklamıyor). İkisi de POLİTİKA kararıdır ve ölçüme (Faz 0.5) bağlıdır.

**Ölçüm dürüstlüğü:** `lab/nl_corpus.py` korpusunda çoklu-ay sorusu **YOK** (`PERIODS`/
`STEP_PERIOD` taraması: sıfır ay listesi). Yani korpus bu düzeltmenin **kazancını göremez**;
gösterdiği tek şey **gerileme olmadığıdır** (6237/7225 = %86,3, dondurulmuş tabana birebir).
Kazanç 28 birim testiyle kanıtlanıyor. Korpusun bu sınıfı kazanması Faz 0.5'in işidir.

Taban artefaktı: `lab/nl_corpus_baseline.json` (`eval/baseline.json` ile aynı disiplin —
`lab/reports/` gitignore'da olduğu için ham rapor değil **kapı değerleri** saklanır).

### 6.12z CANLI TUR — üç sessiz kırık daha: şema sürüklenmesi · VQR benzerliği · yetim alan ✅

#### (1) ŞEMA SÜRÜKLENMESİ — üç özellik sessizce ölüydü

Çalışan konteynerde `alembic_version` tablosu **hiç yoktu**: migration'lar o DB'de **hiç
koşmamıştı**. `create_all` yalnız **eksik TABLOYU** yaratır, var olan tabloya **kolon
eklemez** — ve `docker-compose.yml` 2 Ağustos'ta `dima_logs:/app/logs` **named volume**
kazandığı için DB rebuild'ler arası **hayatta kalıyor**. Yani `create_all` onu bir daha
hiç yeniden yaratmadı ve şema, model ilerledikçe geride kaldı. Her yazma yolu bilinçli
olarak best-effort (`try/except` + WARNING) olduğu için hasar **görünmedi**:

| tablo | eksik kolon | sessiz sonuç |
|---|---|---|
| `verified_query` | `verified_at` | **VQR tamamen ölü** (ne okuma ne yazma) |
| `interaction_log` | `reject_reason` | **Faz 0'ın telemetrisi yazılamıyor** |
| `contract_log` | `provenance_json` | makbuz DB yerine spool'a |
| `notification_log` | `neden_json` | uyarı **nedeni** kaydedilemiyor |

**Ve bir düzeltme:** daha önce *"`interaction_log` 0 satır → telemetri akmıyor"* diye
kaydetmiştim. **Yanlıştı** — o, test konteynerinin boş DB'siydi. Çalışan ortamda **78
satır** vardı; akmayan telemetri değil, **ölçmek için eklediğim kolondu**.

> ⟳ **FAZ 9.10 — ÜÇ ÇELİŞKİLİ SAYININ UZLAŞTIRILMASI (2026-08-03).** Bu belgede
> `interaction_log` için **üç ayrı sayı** duruyordu ve hiçbiri hangi ORTAMI ölçtüğünü
> söylemiyordu: **78** (burası) · **7** (§6.4 dağıtım notu) · **0** (§6.10z, dikey
> modüllerin ertelenme gerekçesi). Üçü de kendi anında doğruydu; birlikte okunduklarında
> **çelişkili** görünüyorlardı — ve bir okuyucu hangisine dayanacağını bilemezdi.
>
> | ortam | ne zaman | satır |
> |---|---|---|
> | test konteyneri (`--network none`, boş DB) | her koşum | **0** — beklenen |
> | çalışan konteyner (`dima-backend-core`) | 2 Ağustos | 78 |
> | çalışan konteyner | 2 Ağustos, dağıtım notu yazılırken | 7 (build sonrası sıfırlanmıştı) |
> | **çalışan konteyner** | **3 Ağustos, ölçüldü** | **93** · `reject_reason` **dolu: 1** |
>
> **Kural:** bu belgedeki her telemetri sayısı **ortamıyla birlikte** yazılır. Ortamsız bir
> sayı, sayı değildir — bu oturumda beş kez ölçüm aracının kendisi yanlış ölçtü ve hepsi
> "hangi ortamda?" sorusu sorulmadığı için gözden kaçmıştı.
>
> `reject_reason`'ın **1** satırda dolu olması beklenen davranıştır: kolon 3 Ağustos'ta
> eklendi, ondan önceki 92 satır NULL kalır ve cevaplanan sorularda zaten NULL olmalıdır
> (kolonun doluluğu = *"deterministik yoldan çıkamayan sorular"* kümesi).

`init_db()` artık SQLite'ta **modelde olup tabloda olmayan kolonları ekliyor** — yalnız
`ADD COLUMN`, yalnız SQLite (Postgres'te sahip Alembic, ADR-0015), ve **her eklenen kolon
WARNING ile loglanıyor**: sessiz bir şema onarımı, onardığı sorunun aynısı olurdu.
`NOT NULL` + varsayılansız bir kolon eklenemiyorsa **sessizce geçilmiyor**, gürültülü
uyarı basılıyor.

#### (2) §1.7'NİN RİSKİ GERÇEK ÇIKTI — ve plandakinden DAHA KÖTÜ

Kullanıcı *"geçen ay toplam **FİRE**"* sordu. VQR embedding benzerliğiyle *"geçen ay
toplam **CİRO**"* kaydını eşleştirdi ve `SELECT SUM(ciro_tl)` döndürdü — `source="vqr"`,
`confidence=0.95`, *"önceden doğrulanmış sorgu"* rozetiyle. **Sorulanın ZIDDI bir ölçü.**

İki soru **tek kelime** farklıydı ve o kelime **ölçünün kendisiydi**: beş token'ın dördü
eşleşince kosinüs 0,92 eşiğini aşıyor. Embedding için bu bağlamda "fire" ile "ciro"
neredeyse aynı; **anlamca zıt** oldukları görülmüyor.

**§6.6z'nin kararı doğruydu ama YETERSİZDİ:** `auto_cube`'u replay'den çıkarmak doğruydu —
ama bu kayıt **`user_verified`**'dı, yani **insan onaylıydı**. Risk kaynağın güveninde
değil, **benzerlik eşiğinin kendisinde**. Plan §1.7'yi *"auto_cube güven listesinde"* diye
çerçevelemişti; ölçüm çerçeveyi genişletti.

**Kural (ADR-0008'in "deterministik-önce"si merdivene uygulanmış):** **birebir** eşleşme
replay'i **korur** (aynı soruyu tekrar soran kullanıcı tahmin değil aynı cevabı alır);
**benzerlik** eşleşmesi `route()` bir cevap üretebiliyorsa **ona yenilir**. `route()`
çözemezse kayıt yine devrededir — **kapsam kaybedilmez, yalnız sıra düzeltilir.**

**Neden hiçbir test yakalamamıştı:** CI `DIMA_VQR_EMBEDDER=off` koşuyor → eşik leksik
(0,85) ve **seed'siz bir depoda hiç tetiklenmiyor**. Risk yalnız *embedder AÇIK + depoda
kayıt VARKEN* görünür. Faz 0.5'in VQR senaryosu bu yüzden *"replay tetiklenmedi"* demişti
ve ben onu **riski çürütmez** diye kaydetmiştim — **doğru kayıtmış.**

#### (3) YETİM CEVAP ALANI — kendi kodumda

Denetimde iki şey çıktı: `Planlayici.sec()` **hiçbir yerden çağrılmıyordu** (Faz 4'ün
*"çapraz-alan pilotu"* kabul ölçütü karşılanmamıştı) ve `agent_run` alanının **frontend
tüketicisi yoktu**. İkisi de bu oturumda on bir kez eleştirilen sınıfın kendi kodumdaki
hâliydi. `sec()` `_capraz_alan_pilotu` ile zincire bağlandı (dört kapı yerinde, makbuz
üretiliyor); `agent_run` `ReportCard`'ın *"nasıl çözüldü"* bloğunda render ediliyor —
**reddedilen adımlar dahil**, çünkü sessizce kaybolan bir adım yapılmamış bir adım gibi
okunur.

Ve bu bir **kapıya** çevrildi: `tests/test_cevap_alani_yetim_degil.py` artık
`AskResponse`'un **her** alanı için frontend'de bir okuma arıyor; muafiyet listesi **kısa
ve gerekçeli** (gerekçesiz muafiyet kapıyı eritir).

#### Test ortamı senaryolara göre genişletildi

`seed_demo` artık **senaryo fixture'ları** da kuruyor: eşik alarmı (Faz G3'ün kıyas yolunu
açar) · **VQR ÇİFTİ** (`user_verified` + `auto_cube`, aynı yapı farklı kaynak — §1.7'nin
kararını **doğrudan gözlemlenebilir** kılar) · sinonim adayı (terfi kuyruğu boş kalmasın).
Bu çift olmasaydı yukarıdaki (2) numaralı bulgu **hiç görünmezdi**.

> ⚠️ Fixture'ların ilk sürümü `company` alanını `slug.replace("demo-","")` ile yazıyordu;
> `settings.company` ise `demo-boyahane`. Kayıtlar **hiç eşleşmiyordu** — fixture "var"
> görünüyor, hiçbir şey ölçmüyordu. **Kapsam adı TAHMİN EDİLMEZ.**

### 6.11z CANLI TUR — `cube+llm` cevabı "LLM kullanılmadı" diye rozetleniyordu ✅

**Gerçek bir sağlayıcıyla (Gemini) ilk canlı istekte çıktı.** Test ortamı CI reçetesi
gereği `--network none` koşuyor (MIMARI §7), dolayısıyla **`cube+llm` orada HİÇ
üretilmiyor** — 1651 testin **hiçbiri** bu yolu koşturmuyordu. **Kapsam yüksekti, YOL
yoktu.**

`_build_explain` `next((k for k in _EXPLAIN_PATH if s.startswith(k)), None)` ile **İLK**
eşleşen öneki alıyordu. Sözlükteki sıra `cube` → `cube+llm` ve
`"cube+llm".startswith("cube")` **True**. Sonuç **iki katlı bir yanlış beyan**:

| alan | gösterilen | olması gereken |
|---|---|---|
| `explain.confidence` | **1.0** | **0.85** |
| `explain.path` | *"cube (route() — **LLM'siz, sıfır maliyet**)"* | *"cube + LLM-destekli alan seçimi"* |

Yani Intent-JSON cevabı saf deterministik `route()` cevabıyla **aynı güven rozetini**
alıyor **ve** kullanıcıya *"LLM kullanılmadı"* deniyordu — oysa `consistency_k=3` ile LLM
**üç kez** çağrılmıştı. Bu bir sayı hatası değil, **kullanıcıya yanlış bir beyandır** ve
tam olarak bu planın §1'inde açılış konusu yapılan **rozet dürüstlüğünün** ihlalidir.

Sözlüğün kendi yorumu ayrımı zaten **beyan ediyordu**: *"cube/cube+llm AYRIMI KORUNUR …
güvenleri farklı olduğundan burada AYRI tutulur."* Kod onu uygulamıyordu — §6.1'in
*"beyan var, kod onu tanımıyor"* sınıfı, bu oturumda **on birinci** kez.

**Düzeltme: en uzun önek kazanır.** Canlıda doğrulandı: `confidence 1.0 → 0.85`, path
artık LLM katkısını söylüyor. 13 test (`tests/test_rozet_durustlugu.py`) — biri de önek
çakışmalarını **görünür** tutuyor: yeni bir önek eklendiğinde tuzak sessizce geri gelmesin.

> **Ders:** bir yolun testi yoksa kapsam sayısı onu göstermez. `--network none` reçetesi
> doğru bir CI kararıdır ama **LLM yollarını kör bırakır**; `--live` turu bu yüzden
> planda vardı ve ilk koşusunda kendini amorti etti.

### 6.10z FAZ 6 — offline sinonim önericisi YAPILDI; dikey modüller ÖLÇÜLDÜ, YAZILMADI ✅

#### Yapılan: offline, insan-onaylı sinonim önericisi (`app/sinonim_onerici.py`)

`mdl_writer` bilerek *"TAHMİNİ sinonim UYDURULMAZ"* diyor — **doğru bir karar**, çünkü
tahmini bir sinonim `route()`'un **canlı** davranışını değiştirir. Ama sonuç **çıplak** bir
cube: tablo adından başka etiketi yok ve `route()` onu neredeyse hiç eşleştiremez. **plan** §2.1'in
ölçtüğü darboğaz tam bu — **mekanizma üretiliyor, sözlük üretilmiyor** (`compose.py`'nin
kendi üreteci de itiraf ediyor: *"sözlük kürasyonu işin indirgenemez insan kısmıdır"*).

**LLM'in meşru olduğu tek yer: offline, insan-onaylı öneri.** Üç değişmez testle kilitli:

1. Öneri **hiçbir `/ask` yolundan** tetiklenmez (tüm `app/` taranıyor).
2. Çıktı **doğrudan yazılmaz** — `SynonymOverride(approved=False)` kuyruğuna aday düşer.
3. **`approved=False` SABİTTİR, parametre değil.** Dışarı açılsaydı bir çağıran `True`
   geçebilir ve LLM önerisi **insan görmeden canlıya inerdi** — modülün tüm gerekçesi
   çökerdi. `source="llm_oneri"` de ayrı tutuluyor: `manual`/`mined` ile aynı kutuya
   koymak, onaylayanın önerinin **nereden geldiğini** görmesini engellerdi.

Yalnız **gerçekten çıplak** alanlara öneri üretilir; zaten sinonimi olan bir alana öneri
küratörlü sözlüğü **gürültüyle sulandırırdı**. En fazla 6 öneri — uzun liste onaylayanı
*"hepsini kabul et"*e iter ve onay kalitesini düşürür.

> ⚠️ **TESTİM GERÇEK BİR AÇIK ARADI VE KENDİ HATASINI BULDU.** Onay kapısının
> `compose.py`'de olduğunu **varsaydım**; test kırıldı — kapı orada değil,
> `materialize.py:103` ve `wren_service.py:578`'de. **Yanlış dosyaya bakan bir kapı, kapı
> DEĞİLDİR**: yeşil kalır ve hiçbir şeyi korumaz. Test artık `SynonymOverride`'ı **okuyan
> her dosyayı** tarıyor ve her birinde `approved` filtresi arıyor (admin onay ekranı
> gerekçesiyle muaf) — kapının **yeri varsayılmıyor**.

#### Yapılmayan: dikey modüller (`packs/modul/muhasebe|satis`) — gerekçesi ÖLÇÜM

Plan: *"Faz 0'ın verisi **sırayı söyler**."* Faz 0 ölçtü: `interaction_log` **0 satır**
(⚠️ **test konteynerinde** — çalışan ortamda 93; bkz. §6.3 ⟳ FAZ 9.10). Karar değişmiyor:
93 satırın tamamı bu oturumun kendi denemeleridir, **gerçek kullanıcı trafiği değildir** —
**sıra girdisi hâlâ YOK**. Ve muhasebe ailesi demo katalogda **zaten var** (`mizan` · `cari` ·
`statements`). Sırasız ve kaynak-tablosuz cube yazmak, planın sektör küpleri için açıkça
yasakladığı **spekülasyonun** aynısı olurdu (*"gerçek müşteri talebi gelene kadar
ertelenir"*). Altyapı hazır: `db_introspect` → `mdl_writer` → **bu fazın önericisi** →
insan onayı. Eksik olan **veri**, kod değil.

12 test: `tests/test_sinonim_onerici.py`.

### 6.13z FAZ 9 — DENETİM ONARIMI: "yapıldı" denen ama yapılmamış/kırık olanı kapatmak ✅

On dört faz bittikten **sonra** iki şey oldu: (1) sistem ilk kez **gerçek bir LLM
sağlayıcıyla** koşuldu, (2) üç bağımsız ajan fazları bölüşüp denetledi. İkisi birden
**1678 testin göremediği** kusurlar buldu. Ortak sebep tek cümle: **CI reçetesi
`--network none` + `DIMA_VQR_EMBEDDER=off` koşuyor** — yani `cube+llm`, VQR benzerliği ve
LLM yolları test ortamında **hiç üretilmiyor**. Kapsam yüksekti, **yol yoktu**.

Her madde için disiplin aynıydı: **(1) önce ÖLÇ** (mevcut davranışı göster), (2) düzelt,
(3) **kapıya çevir**, (4) tam süit + `eval` + `nl_corpus` gerilemesin.

#### Ölçüm iddiayı ÇÜRÜTTÜĞÜNDE: 9.2

Denetim *"beş kardeş netleştirme dalı **kırık** chip üretiyor"* dedi ve gerekçesi
inandırıcıydı (2a-2'de gerçekten **39 chip kırıktı**). Düzelttim: `route()` çözemeyen
etiketi düşürdüm. **Üç golden test kırıldı** ve haklıydılar. Ölçüm:

| katalogdan türeyen 85 benzersiz etiket | adet |
|---|---|
| tıklanınca **doğrudan cevap** | 2 |
| **daraltan chip** üretti (huni) | 83 |
| **çıkmaz sokak** | **0** |

`route()` = `None` bir chip'i **kırık yapmıyor**: *"sürdürülebilirlik"* R4 verir ama `/ask`
*"hangi ölçüyü istiyorsun?"* + **6 çalışan chip** döndürür — duvar değil **huni**.
*"makine"* ise route'suz olduğu hâlde doğrudan cevaplanıyor.

**2a-2'deki 39 kırık chip neydi?** Katalog etiketi değil, **sentezlenmiş** dizeler
(*"mizan (hesap bakiyeleri) borç"*). Kural bu ayrımda ve artık iki ayrı ölçüt var:

* `chip_kullanisli_mi` — **katalog etiketi** için: route ∨ cube hunisi ∨ ölçü hunisi ∨
  boyut hunisi (dördünden biri tutarsa chip bir yere varır).
* `chip_cozuluyor_mu` — **sentezlenmiş sorgu** için: tam çözüm şartı.

Kapı KALDI (sentezlenmiş sorgu hâlâ elenebilir), ama **doğru şeyi ölçüyor**. Denetim
iddiası 2a-1'in `elektrik` kararıyla aynı disiplinle **ölçülerek reddedildi**.

**Ve düzeltmenin kendisi bir kusur açtı:** ilk sürüm `route()`'u `ask.py`'den doğrudan
çağırdı; her `route()` girişte `reddi_sifirla()` yapar ve `answer.py` red gerekçesini
**seal anında** — chip'ler kurulduktan SONRA — okur. Ölçüldü: **R4 → R1**. Yani bu turda
bir kez kapatılan kusur başka bir kapıdan yeniden açıldı. Çözüm yama değil **kapı**:
sonda yalıtımı `chip_kullanisli_mi`'nin **içinde**; çağıran sarmalı hatırlamak zorunda değil.

#### Gizlilik: 9.1

`answer.py`'nin modül değişmezi *"**her** yanıt buradan geçer"* iki uçta **geçerli
değildi**: `/ask/drill` (**9** dönüş noktası, yalnız `raw` dalı audit'li, **hiçbirinde PII
maskesi yok**) ve `/ask/contribution` (ikisi de yok). Taşıdıkları veri hassas —
`musteri` · `operator` · `calisan` bu katalogda **gerçek boyutlardır**. Aynı kırılım
`/ask`'ten maskeli, `/ask/drill`'den **maskesiz** dönüyordu.

**Gövde SARMALANDI, sekiz dönüş noktası yamanmadı**: yamamak, dokuzuncuyu ekleyenin
unutmasına açık kalırdı — tam olarak bu kusurun doğuş biçimi. `pii.muhurle(...)` satırları
ve boyut değerlerini maskeler, `pii:view` yetkilisi maskesiz görür ve bu **ayrı bir audit
satırıdır**; `query` audit'i **her zaman** yazılır (*"başarı audit'siz raporlanamaz"*).

#### Ölçüm bütünlüğü: 9.4 · 9.5 · 9.6 · 9.7

* **9.4** `reject_reason`'ın DB'ye yazıldığı hiç doğrulanmamıştı: tek kapı kaynak
  METNİNDE string arıyordu. Canlı tur kolonun **yok olduğunu** ve best-effort `except`'in
  hatayı **yuttuğunu** ölçtü — iki kapı da yeşildi. Artık satırın kendisi ölçülüyor;
  ayrıca *"cevap geldi ama deterministik yoldan gelmedi"* sınıfı da (R1 kümesi, 99/470)
  kapıya bağlandı — kolon yalnız cevapsızları kaydetseydi **en büyük küme** görünmezdi.
* **9.5** `nl_corpus_baseline.json` sürüm kontrolündeydi ve **hiçbir tüketicisi yoktu**:
  KURAL A'nın *"taban dondurulur"* maddesi bir **nottu**, kapı değil. `eval` tarafı kapılı,
  korpus tarafı değildi — yani bu planın **ana metriği** geriler ve kimse fark etmezdi.
  `lab/nl_corpus.py --kapi` eklendi. **En ince tuzak:** kapı **son tura** bakmalı, köke
  değil — köke bakan bir kapı %93,2 → %86,3 düşüşünü **yeşil** raporlardı.
* **9.6 / 9.7** ölçüm aracının kendisi (§6.5z'nin ⟳ bloğu).

#### Beyan/kod uyuşmazlığı: 9.8 · 9.9 · 9.10

9.8 (§12.6b ⟳) ve 9.9 (§6.2z ⟳) kendi bölümlerinde. **9.10 bu belgenin kendi
sayılarıydı:**

* `interaction_log` için **üç çelişkili sayı** (78 · 7 · 0) — hiçbiri hangi ORTAMI
  ölçtüğünü söylemiyordu. Uzlaştırıldı (§6.3 ⟳) ve kural yazıldı: **ortamsız bir sayı,
  sayı değildir.**
* **Test sayıları çürümüştü.** Denetim bir satırı (*"18 test"* → 17) buldu; hepsi ölçüldü:
  **13 iddianın 10'u yanlıştı** (15→17 · 18→25 · 16→20 …). Tek tek düzeltmek yetmez —
  sebep yapısal: test eklemek doğal, belgeyi güncellemek unutulur. **Kapıya çevrildi**
  (`test_MIMARI_TEST_SAYILARI_gercekle_uyusuyor`).
  ⚠️ Kapının **ilk sürümü yanlış birimi saydı** (yalnız `def test_*`; pytest
  `parametrize` genişlemelerini ayrı sayar) ve **çalışan** dört satırı "çürük" raporladı.
  Ölçüm birimi tanımlanmadan yapılan kıyas, kıyas değildir — bu turda ölçüm aracının
  kendisi **altıncı** kez yanlış ölçtü (§6.4).

#### Kapı eksikleri: 9.11 · 9.12 · 9.13 · 9.14 · 9.15

* **9.11** Bu oturumun **altı fazı** `FLAG_REGISTRY`'de yoktu → admin panelde açıklamasız
  `snake_case`, kategori *"Diğer"*. Bir kill-switch yalnız KOD'da varsa **yarım**dır.
* **9.12** YAML boolean tuzağının kapısı yalnız `demo/packs/features.yml`'yi tarıyordu;
  `features.py` aynı dönüşümü sektör/şirket dosyalarına da uygular. Bugün boş → ısırmıyor;
  yarın `oee_ozel: off` yazan **aynı sessiz-AÇIK** kapanına düşer ve CI yeşil kalır.
* **9.13** `llm_sema_kisitli` bayraklı altı fazın **KURAL B testi olmayan tek istisnasıydı**
  — üstelik varsayılanı `beta` (**açık**). En az korunan bayrak, en geniş açık olandı.
* **9.14** `-0.5c` tuzağının regex'i noktalı çağrıyı **göremiyordu** (`(?<![\w.])`), oysa bu
  depoda kullanılan tek biçim `cube_router.needs_period(...)`. Kapı yeşildi çünkü çağrı
  yok — **koruma iddiası yanlış, sonuç tesadüfen doğru**.
  ⟳ **GÜNCELLEME (Faz X, 3 Ağustos 2026): tuzak KAPIYA dönüştü ve tam da tasarlandığı gibi
  patladı.** `needs_period` artık üretimde **bir** çağırana sahip
  (`ask.py::_learn_chip_completion`) — ama **klarifikasyon kapısı olarak DEĞİL**:

  | ad | üretimde | rolü |
  |---|---|---|
  | `needs_period` | **1 çağıran** | CEVAPLANABİLİRLİK yordayıcısı — *"önceki mesaj tek başına cevaplanabiliyor muydu?"* |
  | `is_period_only` | **0 çağıran** | ADR-0007 K3 klarifikasyon politikası hâlâ bağlı DEĞİL |

  `_period_gate`'in davranışı **değişmedi** (ayrı bir davranışsal test bunu kilitler:
  dönemsiz soru hâlâ *"hangi dönem?"* diye sorulur). Bağlanan şey politikanın kendisi
  değil **yordayıcısı**dır; ayrım kaybolursa biri *"ADR-0007 K3 canlıya alındı"* sanır.
* **9.15** `_takilan_kelimeler`, `known` kümesine yalnız dolgu sözlüğünü veriyordu; katalog
  sinonimleri **hiç** eklenmiyordu. Ölçüldü: *"bu yil ciro"* → aday **`ciro`** — `ciro`
  `parti.toplam_ciro`'nun **zaten** sinonimi. Triyaj kuyruğu, kapsam boşluğu göstermek
  yerine kataloğun var olan sözlüğünü tekrar öneriyor, gerçek boşluklar gürültüde
  kayboluyordu. Düzeltildikten sonra: *"bu yil ciro"* → **[]**,
  *"personel bazli calisma sureleri"* → **['sureleri']** (**plan** §1.5'in gerçek katalog boşluğu).

**Kapsam dışı (kayıt için):** MCP yüzeyi, Skills/Memories, VQR'yi tümden ipucu yoluna alma.
> ⟳ **DÜZELTME (FAZ −1/A2):** bu satır *"sosyal sınıf"* ve *"konuşma belleği
> (`Baglam.ham_ifade`)"*'ni kapsam dışı sayıyordu — **ikisi de İNDİ**: sosyal sınıf
> `e1bde3f` (`tests/test_sosyal_sinif.py`), `Baglam.ham_ifade` `71b542e`
> (`tests/test_atif_baglami.py`). *Kapsam-dışı kaydı, kapsam içine alındığında silinir.* Faz 9 yalnız
*"yapıldı denen ama yapılmamış/kırık"* olanı kapatır.

#### CANLI DOĞRULAMA (rebuild + seed + gerçek Gemini + embedder AÇIK, 3 Ağustos)

CI'ın **hiç üretemediği** yolları ölçmek için P0 maddeleri canlı konteynerde koşuldu.
Hız sınırı **10 sn'de 10 istek** ve bir Intent-yolu `/ask` `consistency_k=3` ile **üç**
LLM çağrısı yapar → istekler **5 sn aralıkla, tek tek** gönderildi.

| ölçüm | sonuç |
|---|---|
| **9.1** `/ask/drill` audit satırı | ✅ `query \| drill:parti` — önceden yalnız `raw` dalı yazıyordu |
| **9.1** `/ask/contribution` audit satırı | ✅ `query \| contribution:parti` |
| **9.2/9.3** altı netleştirme chip'i tıklandı | ✅ **6/6 daraltan chip**, **0 çıkmaz sokak** |
| **canlı tur düzeltmesi** `cube+llm` rozeti | ✅ `confidence=0.85`, yol *"LLM-destekli alan seçimi"* (eskiden `1.0` + *"LLM'siz"*) |
| **VQR benzerlik kapısı** | ✅ log: *"benzerlik eşleşmesi ATLANDI — route() deterministik cevap üretiyor (kayıt='geçen ay toplam **ciro**', soru='geçen ay toplam **fire**')"* → `source=cube`, `toplam_fire_kg` |
| **9.4** `reject_reason` | ✅ `bu yıl bakiye` → **cevap geldi** (`cube+llm`) ama red **R1** kayıtlı; `personel…kıyasla` → **R4** |
| **§1.7 VQR kalıcılığı** | ✅ **ÖLÇÜLDÜ** (offline ⊘ olan madde) |

**Faz 8'in `--live` turu da koşuldu** (izole konteyner, ayrı DB — kullanıcının canlı
verisine fixture yazılmadı): sekiz ölçülebilir sınıf tam, `vqr_kalicilik` ⊘.

> ⛔ **DÜZELTME — O KOŞUM "CANLI" DEĞİLDİ (canlı thread turunda bulundu, 3 Ağustos).**
> Yukarıdaki cümlede *"gerçek sağlayıcı"* yazıyordu; **yanlıştı**. `lab/konusma_
> senaryolari.py` env kurulumu için `tests.conftest`'i import ediyor ve `conftest.py:15`
> **koşulsuz** `DIMA_LLM_PROVIDER="rule"`, `:26` `DIMA_VQR_EMBEDDER="off"` yazıyor.
> `--live` bayrağı yalnız monkeypatch'leri (dry_plan/enrich) atlıyordu; **sağlayıcıyı
> hiç değiştirmiyordu.**
>
> Yani `--live` **hiçbir zaman canlı olmadı**: o modda `cube+llm` üretilemez, VQR
> benzerliği tetiklenemez, red gerekçesi yazılamaz — yani modun var olma sebebi olan
> yolların **hiçbiri** koşmuyordu. Bu, §6.4'ün dersinin bu turdaki **en pahalı** hâli:
> ölçüm aracı çalışıyor görünüyor ve ölçtüğünü iddia ettiği şeyi hiç görmüyordu.
>
> **Kök neden düzeltildi:** gerçek ortam değerleri conftest import'undan **ÖNCE**
> yakalanır, `--live`'da geri yüklenir; gerçek sağlayıcı yoksa mod **koşmaz**
> (fail-closed — sessizce `rule` ile koşan bir "canlı" tur, hiç koşmamaktan kötüdür).
> DB/VQR izolasyonu **korunur**: canlı bir ölçüm kullanıcının verisini kirletmemelidir.
> 4 kapı: `tests/test_senaryo_araci_durustlugu.py`.

**`vqr_kalicilik` neden `--live`'da bile ⊘ kaldı — ve bu neden DOĞRU.** Senaryonun sorusu
`route()` tarafından **deterministik** çözülüyordu, yani `cube+llm` yoluna hiç düşmüyordu;
soru artık **katalogdan**, route'un çözemediklerinden seçiliyor. Seçilen soru da cevapsız
kalırsa senaryo yine ⊘ der — çünkü ön koşulun sağlanmaması bir **ürün hatası değildir**.
(İlk düzeltmemde bunu `False` sayıyordum: **sahte bir kırmızı, sahte bir yeşil kadar
yanıltıcıdır.**)

**§1.7 — offline ÖLÇÜLEMEYEN madde, ölçülebildiği tek yerde ölçüldü.** İki `cube+llm`
cevabı VQR'a **`auto_cube` olarak yazıldı** (ön koşul sağlandı), sonra parafraz soruldu:
embedder AÇIK ve neredeyse birebir bir kayıt varken **replay EDİLMEDİ** — cevap yine
`cube+llm` yolundan geldi. **Faz 2b-2'nin kararı (auto_cube replay'den çıkar, few-shot'ta
kalır) canlıda doğrulandı.**

⚠️ **Ölçüm aracı bu turda iki kez daha yanıldı** (§6.4'ün dersi, toplam sekiz):
(a) `/ask`'i **8000** portunda aradım — servis **8001**'de; gelen 401 başka bir servistendi.
(b) VQR kaydını `order_by(id.desc())` ile aradım — `id` bir **UUID**, sıralaması anlamsız;
"yazılmamış" sonucunu üretti. Tam liste alınınca **yazılmış** olduğu görüldü. Her iki
hatada da yanlış sonuç **inandırıcıydı** — bu yüzden her canlı iddia ikinci bir kanıtla
(log satırı / tam tablo) doğrulandı.

Testler: `tests/test_gizlilik_muhru.py` (9) · `tests/test_dogrulanmis_chip.py` (16) ·
`tests/test_korpus_taban_kapisi.py` (10) · `tests/test_senaryo_araci_durustlugu.py` (13) ·
`tests/test_bayrak_kaydi.py` (6).

### 6.14z CANLI THREAD TURU — 10 senaryo, gerçek Gemini, thread mantığı ✅

Rehberin (**plan** §3.2) zincir sözleşmesiyle **10 senaryo THREAD olarak** koşuldu: her tur bir
öncekinin `cube_query`'sini taşır, tur arası 5 sn. Sekizi ilk denemede temiz:

| # | faz | ölçülen |
|---|---|---|
| S3 | 2a-4 | ayrık ay → `ayrik_aylar` işareti + `gte/lte` zarfı, 2 satır ✅ |
| S4 | 2a-5 | liste niyeti → `dims=[musteri]` + `view_hint=table` ✅ |
| S5 | -0.5a | bitişik çoklu ay → tek `gte 01-01 / lte 03-31`, 3 satır (Ocak-only sessiz-yanlışı KAPALI) ✅ |
| S6 | -1 | ölü uç → 13 değil **6** daraltılmış chip + dürüst not ✅ |
| S9 | 5 | bayrak kapalı → `narration` YOK, `summary` sağlam (KURAL B) ✅ |
| S10 | 0.5/8 | **4 turlu thread**: sor → `renk bazında` → `sadece son 3 ay` → `pasta grafik`; dördü de `source=cube` (**sıfır LLM**), yapı hiç silinmedi ✅ |

**Bayraklar açıldığında (izole kopya, gerçek sağlayıcı):**

* **Faz 3b ✅ CANLI ÇALIŞIYOR** — *"hasılatımız bu yıl ne kadar oldu"* → soru
  `toplam_ciro bu yıl ne kadar oldu` diye yeniden yazıldı, cevap **`source=cube`**
  (deterministik!) ve `provenance_soru` makbuza yazıldı. Tasarımın tam karşılığı:
  **LLM ifadeyi düzeltir, cevabı KÜP verir.**
* **Faz 5 ✅ CANLI ÇALIŞIYOR** — anlatı üretildi, guard geçti, sayılar sonuçla eşleşti
  (*"en yüksek OEE 0,65 … ÖRGÜ HAT"*), `agent_run` **2 adım** (`interpret` → `llm.anlat`)
  — 9.8'in planlayıcı kapısı canlıda görünür.
* **Faz 4 ⚠️ — KABUL ÖLÇÜTÜ MİMARİYE AYKIRI BİR SORU SEÇMİŞ.** Pilot ateşlemiyordu ve
  **iki** bağımsız sebebi var:
  1. **Sıra**: çapraz-konu netleştirmesi (`other_topic`) pilottan **önce** dönüyordu →
     bayrak açıkken bile pilot hiç çağrılmıyordu. Bu, **plan** §1.5'in dersinin kardeş daldaki
     hâli (*"truthy bir netleştirme daha yetenekli bir adımı sessizce öldürür"*).
     **Düzeltildi**: `other_topic` dalında pilot önce denenir, `None` dönerse netleştirme
     aynen döner (kapsam kaybı yok, bayrak kapalıyken blok hiç koşmaz).
  2. **Soru**: planın pilot örneği (*"personel bazlı verimlilik"*) başka cube'un
     **BOYUTUNU** istiyor — MIMARI §9.2'nin *"tek CubeQuery'de ifade edilemez"* dediği
     şey; `cross_cube_add` ise **ölçü** harmanlar ve **ekleme niyeti** ister (kendi
     sözleşmesi). Yani o soru iki adımda da ifade edilemez.

  **Yetenek YERİNDE ve ÇALIŞIYOR — ama fresh soruda değil, TAKİPTE:** canlı thread
  ölçümü, `bu yıl makine bazında oee` → *"bir de fire ekle"* zincirinin raporu
  genişlettiğini gösterdi (`measures=['ort_oee','toplam_fire_kg']`, 11 satır). Whitelist
  de tuttu: `toplam_fire_kg` **oee cube'unda da tanımlı** — sessiz-yanlış yok.

  → **Üçüncü kez bir KABUL ÖLÇÜTÜNÜN kendisi kusurluydu** (3a'nın metriği · vqr
  senaryosunun sorusu · 4'ün pilot sorusu). Ders: *ölçüt de bir beyandır ve çürüyebilir.*

### 6.15z FAZ D1 — SOSYAL SINIF: veri niyeti olmayan ifade SQL üretemez ✅

**Ölçülen kusur (3 Ağustos 2026).** Sistemde *"veri niyeti olmayan ifade"* diye bir sınıf
**yoktu**. 16 sosyal ifade ölçüldü:

| ifade | önce | sonra |
|---|---|---|
| `merhaba` · `selam` | `meta` ✅ (`_META_HINTS`'te **tesadüfen** vardı) | `meta` |
| `teşekkürler` · `sağol` · `günaydın` · `görüşürüz` · `tamam` · `peki` · `ok` · `süper` · `anladım` · `eyvallah` · `iyi çalışmalar` · `çok iyi` | **`rule` → SQL ÜRETTİ** (12 adet) | `meta`, 0 SQL |
| `teşekkür ederim` | *"«ederim» yerine «**verim**» mi demek istedin?"* | `meta` |
| `harika` | *"«harika» yerine «**ariza**» mi demek istedin?"* | `meta` |

Üretimde bunların **her biri bir LLM çağrısıdır** (ölçülen sınır: 10 sn'de 10 istek). Son
iki satır aynı kökün ikinci belirtisi: sınıf olmadığı için boru hattı sosyal kelimeyi
**yanlış yazılmış bir katalog terimi** sanıyor.

**İKİNCİ, TERS YÖNLÜ KUSUR — kibar kullanıcı cezalandırılıyordu.** Aynı ölçümde çıktı:

    "merhaba bu yıl makine bazında oee"        → R10   (kapsam kapısı)
    "iyi çalışmalar, geçen ay fire nedir"      → R1    (kimlik çakışması)

İkincisinin kökü daha ince: `oee`'nin cube sinonimlerinden biri **`calisma`**; *"iyi
çalışmalar"* kalıbı rakip bir kimlik enjekte ediyor ve `_match_cube` iki adayı çözemiyordu.

#### Neden `_META_HINTS`'e kelime EKLENMEDİ

O liste bir **torbaydı** (ürün soruları + selamlaşma karışık). `teşekkür` eklemek
ADR-0008'in tam olarak yasakladığı şeydir — bir sonraki kelimede kusur tekrarlar. Kök neden
**sınıfın yokluğudur**. Liste **büyümedi, KÜÇÜLDÜ**: selamlaşma oradan çıkıp sınıfa taşındı
(18 → 14 girdi) ve bu bir **kapıyla** kilitlendi.

#### Üç mekanizma, TEK sözlük

| Mekanizma | Ne yapar |
|---|---|
| `veri_niyeti_var(q, schema)` | **YAPISAL** kapı: cube/boyut ∨ ölçü ∨ dönem ∨ kıyas ∨ liste sinyali. Beşi de **ZATEN VAR** olan fonksiyonlar — yenisi yazılmadı, çağrıldı |
| `sosyal_edim(q)` | **SINIF**: tür + **tam kaplama** bayrağı |
| `sosyal_ayikla(q)` | Kalıp ifadenin sözcüklerini **katalog eşleşmesinden çıkarır** |

Sözlüğün **tek sahibi** `cube_router`'dır — **dört** tüketicisi var (sosyal cevap ·
`route()` kapsam kapısı · `deterministic_refine` · `partial_unknowns`) ve ayrı liste tutmak
iki tarafı ayrıştırırdı; `_period_hit_words`/`_misc_hit_words` için verilen kararın aynısı.

#### İki ilke — istisna listesi değil

**1 · TAM KAPLAMA.** *"iyi çalışmalar"* bir **kalıp ifadedir**; `çalışma` katalogda gerçek
bir terim olsa da kalıbın parçasıdır. Ölçüt: eşleşen kalıp ifadenin **tamamını** kaplıyorsa
sosyaldir.

    "iyi calismalar"            → kalıp = tüm ifade      → SOSYAL
    "tesekkurler bu yil ciro"   → `ciro` kalıp dışında   → VERİ

**2 · AYIKLAMA ≠ DOLGU.** Dolgu saymak *"bu kelime açıklandı"* der (R10'u çözer);
**ayıklamak** *"bu kelime konu hakkında hiçbir şey söylemiyor"* der (R1'i çözer). Çakışmada
gereken ikincisidir ve `route()` girişinde uygulanır. Ayıklama **kalıba** bağlıdır,
kelimeye değil: `"calismalar bazında oee"` sorusunda kalıp eşleşmez, `calisma` dokunulmadan
kalır ve `oee` kimliğini korur.

⚠️ **İlk sürüm virgülü hesaba katmıyordu.** `_norm` noktalamayı KORUYOR; `"calismalar,"`
token'ı ayıklanamıyordu ve kusur virgüllü cümlede aynen sürüyordu. Eleme artık token
**çekirdeğine** göre (noktalama korunur).

**Ölçüm:** test **1762 → 1795** · eval `+0,0/+0,0/+0,0` · korpus kapısı **yeşil**
(doğru-cube %93,2 sabit; erişim %69/%69/%69/%73 — dördü de tabanda ya da üstünde).
32 test: `tests/test_sosyal_sinif.py`.

### 6.16z FAZ D2 — BEŞİNCİ KONUŞMA TÜRÜ: *"bunu analiz et / yorumla / özetle"* ✅

**Ölçülen ölü uç (3 Ağustos 2026), bir `oee` raporu üstünde.** `followup.py` konuşma
sınıfını **dört** türle tanımlıyordu; kullanıcının **en doğal** cümlesi hiçbirine
girmiyordu — altı ifadenin **beşi** duvara çarptı:

| ifade | önce | sonra |
|---|---|---|
| *"bunu analiz et"* | *"«bunu» yerine «**gunu**» mi demek istedin?"* | `source=cube`, rapor açıldı |
| *"değerlendir"* | *"«degerlendir» yerine «**degree**» mi?"* | aynı |
| *"yorumlar mısın"* · *"özetle"* · *"bu grafiği açıkla"* | *"Bu takip mesajını önceki raporla ilişkilendiremedim"* | aynı |
| *"bu neden böyle?"* | ✅ (`TUR_NEDEN` zaten vardı) | değişmedi |

Yani bu dosyanın **kendi docstring'inde tarif ettiği** ölü uç, bir tür eksik olduğu için
yaşamaya devam ediyordu.

**Sınıfın tanımı DEĞİŞMEDİ:** *"YENİ CEVAP ÜRETMEZ, VAR OLANI AÇAR."* Dal `prev_cq`'yu
**aynen** yeniden çalıştırır (`cube_query` değişmez — deneyim sözleşmesi #1) ve `seal()`
yorumu, `t2_anlatici` açıkken guard'lı anlatıyı, chip'leri kendisi ekler.

**Konuşma kendini besler:** cevaba *"Neden böyle?"* · *"Normal mi?"* · *"Ne yapmalıyız?"*
chip'leri iliştirilir — üçü de **zaten çalışan** konuşma türleri.

#### Üç kusur ölçülerek bulundu — üçü de göndermeden önce

1. **Konu değişimi çalınıyordu.** `analizini` kalıbı *"fire analizini yap"*ı da yakalıyordu
   (eldeki raporu açmak değil, YENİ konu). Dosyanın kendi zamir/kısalık disiplini
   (`TUR_NEDEN`/`TUR_ISARET`) bu türe de uygulandı: yanlış-negatif normal zincire düşer
   (zarar yok), yanlış-pozitif kullanıcının sorusunu **yutardı**.
2. **ÇİFT MÜHÜR.** İlk sürüm `_answer_from_cube_query` çağırıyordu; o `_finish`'i **kendi
   içinde** uygular ve çağıran da uygular → ölçüldü: **tek tur İKİ telemetri satırı**
   (çift audit · çift PII maskesi · çift yorum). Kardeş dal (`TUR_NORMAL`) mühürsüz
   `AskResponse` döndürür; bu dal da o sözleşmeye uyduruldu.
3. **YETİM ALAN (frontend).** `suggestions` yalnız `ReportPanel`'in **NOT** dalında render
   ediliyordu; bir RAPOR kartı geldiğinde hiç okunmuyordu → üç devam chip'i **ekranda
   görünmüyordu**. `test_cevap_alani_yetim_degil` bunu **göremez**: alan adı frontend'de
   bir yerde geçiyor. **Kapının kör noktası *"hangi RENDER YOLUNDA"* sorusudur** — bu,
   yetim-uç kapısının bugüne kadarki en ince sınırı ve kayda geçti.
   `ReportCard`'a *"devam sorusu"* bloğu eklendi; `next_steps`ten **ayrı** durur çünkü o
   sorguyu DÜZENLER (`cube_query` taşır), bu ise bir SORU sorar.

⚠️ **Kabul ölçütü yine ölçülmeden yazılmıştı.** Deneyim sözleşmesine *"≥3 olgu"* koymuştum;
`interpret()` ölçüldü: tek satırlık toplamda **1**, kırılımlı raporda **2** olgu üretiyor.
Ölçüt gerçeğe çekildi (özet + kırılımda ≥2 olgu + ≥2 devam chip'i). Bu turda **dördüncü**
kez ölçütün kendisi kusurlu çıktı.

**Ölçüm:** test **1795 → 1817** · eval `+0,0/+0,0/+0,0` · korpus kapısı **yeşil** (%93,2
sabit) · senaryo süiti dokuz sınıfta değişmedi. 22 test: `tests/test_anlat_turu.py`.

#### CANLI DOĞRULAMA — analist turu (rebuild + seed + gerçek Gemini)

**D1 canlıda:** dört sosyal ifade → `source=meta`, **0 SQL**, türe uygun sıcak cevap
(*"Merhaba! Verinle ilgili ne bakalım?"* · *"Rica ederim…"* · *"Görüşürüz!…"*).

**D2 canlıda** — dört turlu thread (`oee` raporu → *"bunu analiz et"* → *"neden böyle?"*
→ *"normal mi?"*):

| tur | sonuç |
|---|---|
| T1 rapor | `source=cube`, 11 satır |
| T2 *"bunu analiz et"* | `source=cube`, **yapı korundu** (`cube_query` birebir aynı), üç devam chip'i |
| T3 *"neden böyle?"* | **dürüst red**: *"`ort_oee` bir ortalama/oran — parçaların toplamı bütünü vermez"* (doğru davranış: katkı ayrıştırması ortalamada tanımsız) |
| T4 *"normal mi?"* | dönemsel kıyas geldi (`compare: yoy`) |

**Anlatım AÇIKKEN** (izole konteyner, `t2_anlatici: beta`): T1 ve T2 akıcı Türkçe anlatı
üretti, **guard geçti** ve sayılar sonuçla birebir eşleşti (`0,65` · `%10,1` · `0,52` ·
`11`); makbuz **2 adım** (`interpret` → `llm.anlat`) — Faz 9.8'in planlayıcı kapısı
canlıda görünür.

⚠️ **DÜRÜST BULGU — *"analiz et"* tek başına YENİ ANALİZ ÜRETMİYOR.** Anlatım kapalıyken
T2, T1'in **aynısını** döndürüyor; açıkken de anlatı aynı iki olgunun yeniden ifadesi.
Değeri **çapa + üç devam chip'i**dir. Bu, sınıfın kendi tanımının doğrudan sonucudur
(*"YENİ CEVAP ÜRETMEZ, VAR OLANI AÇAR"*) ve derin analiz **bilinçli olarak** üç chip'in
arkasındadır (`neden` → katkı · `normal mi` → dönemsel kıyas · `ne yapmalı` → reçete).
Dala `yoy` eklemek `TUR_NORMAL`'i **tekrarlardı**. Zenginleştirme kararı Faz C'nin
ölçümüne bırakıldı — bugün *"az ama dürüst"*, uydurma değil.

### 6.17z FAZ D3 + D4 — ÖLÇÜLDÜ: İKİSİ DE ZATEN YAPILMIŞ (araştırma raporu iki kez fazla saydı) ✅

Araştırma ajanının raporu (0-100 dosyası eki) devlerin yedi desenini bizimkiyle
kıyaslamıştı. Dört maddesi *"bizde yok"* diyordu; **ikisi ölçülünce yanlış çıktı.**

| Rapor iddiası | Ölçüm |
|---|---|
| **D3** *"`agent_run` makbuzu **doğrudan** kullanıcıya render ediliyor — geliştirici katmanını son kullanıcıya gösteriyoruz"* | ❌ **Yanlış.** Makbuz `showTrace` arkasında, **varsayılan kapalı**, *"?"* düğmesiyle (*"Bu sorgu nasıl çözüldü?"*) açılıyor. CHI'nin üç katmanı da yerinde: **kullanıcı** = `SourceBadge` (her zaman görünür, `source`+`confidence`) · **geliştirici** = katlanır adım listesi · **yönetişim** = audit + `contract_log` |
| **D4** *"checkpoint/geri alma **neredeyse bedava**, planda yok"* | ❌ **Yanlış — zaten var.** Her kartta **"↳ yanıtla"**: *"thread'in SONUNA eklenir, **bu kartın bağlamıyla**"*. Yani herhangi bir karta dönüp oradan devam etmek kurulu; `POST /cube` de chip'i LLM'siz yeniden koşuyor |
| **#2** akış (streaming) | ✅ **Gerçek boşluk** — `StreamingResponse`/SSE/WebSocket kodda **sıfır**; `/ask/jobs` bir **polling job**, akış değil |
| **#4** onaylı yazma aksiyonları | ✅ **Gerçek boşluk** — yazma araçları bilerek `llm_araclari` dışında; eksik olan **onay akışı** |

**Karar: D3 ve D4 YAPILMADI ve yapılmayacak** — çünkü yapılacak bir şey yok. Var olanı
"iyileştirmek" adına dokunmak, çalışan bir tasarımı bozma riskidir (2a-1'in `elektrik`
dersi: ölçmeden dokunma). Rapor **iki kez fazla saydı**; bu, dış bir raporun iddialarının
**kodla sınanmadan** plana alınmaması gerektiğinin üçüncü kanıtı (birincisi *"`/ask/jobs`
hazır"*, ikincisi *"güven eşiği ayarı"* — o da MIMARI'nin açık kararına aykırıydı).

> Ders: **bir rapor bir ölçüm değildir.** Bu turda dış rapor üç kez, kendi kabul
> ölçütlerim dört kez, ölçüm araçlarım on kez yanıldı — hepsi kodla sınanınca çıktı.

### 6.18z FAZ A — ÖLÇÜM ALETİ: kırıktı, onarıldı, kendini kanıtladı ✅

Planın sırası **ALET → ÖLÇÜT → ÖLÇÜM → KARAR**. Gerekçesi ilk adımda doğrulandı.

#### A1 · Alet SESSİZCE KIRIKMIŞ

`lab/nl_accuracy.py` — iki doğruluk aletinden biri — çalıştırıldığında:

    TypeError: <lambda>() takes 2 positional arguments but 3 were given
    === TOPLAM: 0 geçti · 2 kaldı ===

**Sıfır vaka koşuyordu.** Sebep: monkeypatch imzaları DAR yazılmıştı ve `dry_plan`
zamanla üçüncü bir argüman kazandı. Kardeş araç (`konusma_senaryolari.py`) `*a, **k` ile
toleranslı yazılmış; bu dosya eski katı hâlde kalmış ve **CI'da koşmadığı için** aylardır
görünmemişti — `lab/nl_corpus.py`'nin aylarca kırık kalmasıyla **aynı sınıf** (§6.4).
Onarıldı: **0 → 4/4**.

Ayrıca `--live` eklendi (`konusma_senaryolari.py` ile **aynı sözleşme**, kopyalama değil):
gerçek ortam conftest import'undan **önce** yakalanır, gerçek sağlayıcı yoksa **koşmaz**;
DB izolasyonu **korunur**.

#### A2 · Vaka seti 4 → **63**, dört şirket

Set bilinçli olarak **iki yarıdır** ve ayrım belgelendi:

* **Katalogdan üretilen (48):** üretilirken `route()`'un o cube'a çözdüğü doğrulandı →
  **inşa gereği** geçerler. Değeri *yargı* değil **regresyon**dur. ⚠️ Bunların %100
  geçmesi bir başarı göstergesi **değildir, tautolojidir** — bu cümle dosyaya yazıldı.
* **Zor kazanılmış (15):** bu oturumda ölçülerek düzeltilmiş kusurlar — 2a-3 (spesifik
  ölçü) · 2a-1 (`elektrik`) · 2a-5 (liste niyeti) · 2a-4 (ayrık ay) · -0.5a (bitişik ay)
  · **D1 (sosyal önek R10/R1 vermemeli)** · 1b (sızıntı kapanı). Kapının gücü buradan gelir.

⚠️ **Etiketi ÖNCE YANLIŞ YAZDIM ve alet yakaladı:** `elektrik tüketimi` için
`enerji_tesis` demiştim; katalogdan doğrulandı — `enerji_makine.toplam_elektrik_kwh`'nin
**birebir** sinonimi, `enerji_tesis`'inki **nitelikli**. Sistem doğru, beklentim yanlıştı
(bu turda **beşinci** kez). Etiketli setin değeri tam da bu: beklentiyi yazmak onu
**sınanabilir** yapar.

#### A3 · A/B koşucusu — ve aletin KENDİNİ KANITLAMASI

İki mod, çünkü **gerileme** ve **kazanç** farklı korpuslar ister:

| mod | korpus | soru |
|---|---|---|
| `--ab <bayrak>` | etiketli 63 vaka | *"bayrak çalışan bir vakayı BOZUYOR mu?"* (B2'nin ikinci yarısı) |
| `--ab-kurtarma <bayrak>` | `route()`'un **çözemediği** sorular (katalogdan üretilir) | *"kaç soruyu KURTARIYOR?"* (B2'nin birinci yarısı) |

Etiketli vakalar `route()`'un zaten çözdüğü sorulardır; bir LLM bayrağı orada kazanç
**üretemez** ama **bozabilir**. İkisini tek korpusla ölçmek, birini görünmez kılardı.

Bayrak zorlama YAML'a **dokunmaz**: `features.resolve_for` her tüketicide fonksiyon içinde
import edildiği için modül düzeyinde yamalanır ve çıkışta **geri alınır** — ölçüm,
ölçtüğü sistemi kalıcı olarak değiştirmemelidir.

**Planın A-kapısı karşılandı** (*"alet bilinen bir farkı yeniden üretebilmeli"*):
`--ab liste_niyeti` → **kurtarılan 1** (*"…10 müşteriyi listele"* bayrak kapalıyken
düşüyor, açıkken geçiyor), bozulan 0. `--ab t2_anlatici` → 0/0 (kural sağlayıcıda `anlat`
yok; beklenen). Alet bu farkı göremeseydi **hiçbir bayrak ölçümüne güvenilemezdi**.

**Ölçüm:** test **1817 → 1827** · eval `+0,0/+0,0/+0,0` · `nl_accuracy` **63/63**.
15 test: `tests/test_olcum_aleti.py` (Faz X'te +3: kopya-yok · ayar önbelleği temizleniyor · canlılık BEYAN değil ÖLÇÜM).

### 6.19z FAZ C (kısmi) — `prompt_enhancer` ÖLÇÜLDÜ: kazanç YOK, ama kota sınırına çarpıldı ⚠️

#### Gerileme yarısı — TEMİZ

`--ab prompt_enhancer` (63 etiketli vaka, **gerçek sağlayıcı**): **bozulan 0**, dört
şirkette de. B2'nin ikinci yarısı (*"doğru-cube gerilemedi"*) karşılandı.

#### Kazanç yarısı — ve KORPUS BİR KEZ YANLIŞ SEÇİLDİ

İlk ölçüm korpusu **katalog sinonimlerinden** üretiyordu ve **0/12 ↔ 0/12** verdi. Bu
*"kazanç yok"* gibi okunuyordu; oysa **yanlış nüfus** ölçülmüştü:

* Katalog sinonimleri `route()`'ta çoğunlukla **BELİRSİZLİK** (R1) yüzünden düşer
  (`bakiye` iki cube'da) — **yeniden yazmak belirsizliği çözmez**.
* Enhancer'ın hedefi **katalog DIŞI** ifadelerdir (*"hasılatımız"* → `ciro`).

Doğru korpus `lab/nl_corpus.py::REAL_PHRASINGS` (doğal iş dili → ölçü) — yeniden
yazılmadı, **çağrıldı**. Yan kazancı: beklenen ölçü bilindiği için kurtarmanın yalnız
*oluştuğu* değil **DOĞRU** olduğu da ölçülür.

⚠️ **VE KENDİ KAPIMI KULLANMAYI UNUTTUM.** Düzeltilmiş korpusla koşum yine `0/14 ↔ 0/14`
verdi — çünkü `--live` **olmadan** çalıştırmıştım: `tests.conftest` sağlayıcıyı `rule`'a
sabitledi, enhancer'ın LLM'i yoktu. Ölçüm *"kazanç yok"* değil **"ölçmedim"** diyordu.
Uyarı yeterli değildir: mod artık kendi ön koşulunu **zorunlu kılıyor** (fail-closed).

#### Gerçek ölçüm

| yapılandırma | cevaplanan |
|---|---|
| `prompt_enhancer` **KAPALI** | **13/14** |
| `prompt_enhancer` **AÇIK** | 12/14 |
| **kurtarılan** | **0** · kaybedilen **1** · ölçü değişen 1 |

**Asıl bulgu: Intent-JSON doğal ifadelerin 13/14'ünü ZATEN cevaplıyor** — yani enhancer'ın
hedef nüfusu neredeyse **boş**. Bu, Faz 3a'nın birebir tekrarı: mekanizma, başka bir
mekanizmanın çoktan kapattığı bir boşluğu hedefliyor.

⚠️ **KOTA SINIRINA ÇARPILDI** — koşum sırasında **2 × HTTP 429** (23 çağrı başarılı).
Kaybedilen tek vaka bir 429 artefaktı **olabilir**; tek koşumla ayırt edilemez. Bu yüzden:

* **Karar: `prompt_enhancer` `off` KALIYOR** — gerekçe *"kurtarma 0, hedef nüfus zaten
  kapalı"*. Faz 7 ve 3a'nın disiplini: **kazanç yoksa yazılır.**
* Bu karar **yeniden açılabilir**: kota serbest kaldığında daha büyük örneklemle
  tekrarlanmalı. *"Kaybedilen 1"* kesin bir gerileme kanıtı **değildir** ve öyle
  sunulmuyor.
* `t2_anlatici` ve `agent_plan_secimi`'nin kazanç ölçümü **⊘ ÖLÇÜLEMEDİ** — kota.
  Yeşile de kırmızıya da yuvarlanmadı.

#### İKİNCİ SAĞLAYICIYLA TEKRAR — ve ölçümün GERÇEK gürültü kaynağı

Kota duvarını aşmak için **OpenRouter** sağlayıcısı eklendi (anahtar env'de vardı, kodda
desteği **yoktu**). İkinci ölçüm, `google/gemma-4-31b-it` ile:

| sağlayıcı / model | KAPALI | AÇIK | kurtarılan |
|---|---|---|---|
| gemini-flash-lite (2 × 429'lu) | 13/14 | 12/14 | **0** · kaybedilen 1 |
| openrouter · gemma-4-31b (90 çağrı) | 14/15 | **15/15** | **1** · kaybedilen 0 |
| openrouter · nemotron-3-ultra | ⊘ | ⊘ | **54 × 429** — ücretsiz katman doydu |

**İki koşum da aynı yöne işaret ediyor:** Intent-JSON, doğal ifadelerin **13–14/15**'ini
**zaten** cevaplıyor → enhancer'ın hedef nüfusu neredeyse **boş**. Tek kurtarma da
korpus etiketinden **farklı** bir ölçü seçti (*"ne kadar borçlu"* → `toplam_borc`, etiket
`bakiye`) — ikisi de savunulabilir, bu yüzden *"yanlış"* değil **"etiketten farklı"**
diye kaydedildi.

⚠️ **ÖLÇÜMÜN GERÇEK GÜRÜLTÜ KAYNAĞI BULUNDU — ve benimdi.** Arka planda koşan ölçüm
konteynerleri, istemcileri zaman aşımına uğradıktan **sonra da yaşamaya devam ediyordu**:
üç konteyner aynı anda API'yi dövüyordu (11 · 23 · 44 dakikalık). 429'ların büyük
olasılıkla sebebi budur ve Gemini turundaki *"kaybedilen 1"* bir **artefakt** olabilir.
Durduruldu. **Operasyonel kural:** ölçüm konteynerleri adlandırılmalı ve tur sonunda
açıkça kapatılmalı — `--rm` istemci ölünce yetmiyor.

#### Karar

**`prompt_enhancer` `off` KALIYOR** — gerekçe: *"kurtarma ≤ 1 ve hedef nüfus zaten kapalı"*.
Ama karar **kapanmadı**, iki dürüst çekinceyle:

1. **Korpus fazla temiz.** `REAL_PHRASINGS` ekip tarafından yazılmış iş dilidir; gerçek
   kullanıcı çok daha dağınık yazar. Enhancer'ın değeri orada görünebilir ve bu korpus
   onu **göremez**. (Kullanıcının kendi hipotezi: *"promptların zaten iyi olduğu için
   çalışmamış olabilir; gerçek kullanıcı deneyiminde iş yapabilir."*)
2. **Ölçüm gürültülüydü** (zombi konteynerler + kota). Temiz bir tekrar gerekiyor.

`t2_anlatici` ve `agent_plan_secimi` **hâlâ ⊘** — kota serbest kalınca ölçülecek.

### 6.20z FAZ F — KATALOG BELİRSİZLİĞİ, LLM TAHMİNİNİ ÖNCELER (bayraklı, KAPALI) ✅

**Canlıda ölçülen vaka (3 Ağustos 2026):**

    "bu yıl bakiye" → source=cube+llm · cube=mizan · confidence=0.85 · chip YOK

`bakiye` katalogda **iki** cube'un ölçüsüdür (`cari` · `mizan`) ve §6.1g'nin netleştirme
chip'i tam bunun için var. CI'da (LLM yok) chip **ateşliyor**; **üretimde Intent-JSON onu
gölgeliyor** — olasılıksal bir 2/3 oyu, **deterministik olarak BİLİNEN** bir belirsizliği
eziyor. Sebep sıra: netleştirme dalı `ask.py`'de Intent-JSON bloğundan **sonra** duruyor.

Bu, §1.7'nin dersinin yeni bir kapıdan girişi (*"yapısal geçerlilik ≠ semantik doğruluk"*).
**Gerçekten belirsiz bir kelimede doğru cevap yoktur**; herhangi bir seçim yazı-turadır ve
`0.85` rozetiyle sunulması onu **daha kötü** yapar.

#### Nüfus ÖLÇÜLDÜ — LLM'siz, kotaya dokunmadan

384 ölçü sinonimi tarandı:

| durum | adet | anlamı |
|---|---|---|
| katalogda **≥2 sahip** + `route()` **çözemiyor** | **53** | bu kapının nüfusu |
| katalogda ≥2 sahip **ama** `route()` **çözüyor** | **20** | **DOKUNULMAZ** — 2a-3'ün *"en spesifik ölçü kazanır"* kuralı belirsizliği zaten kırmış |

İkinci satır kapının en önemli sınırıdır ve koşul `route_hit is None` ile bağlanmıştır.
Ölçüldü: `sapma yüzdesi` → `enerji_sapma`, `elektrik tüketimi` → `enerji_makine` — bayrak
**açıkken bile** dokunulmuyor.

#### Kural TEK YERDE yaşıyor

Netleştirme mantığı ortak bir yardımcıya (`_olcu_belirsizligi_netlestir`) çıkarıldı ve
**iki** yerden çağrılıyor: bayrak açıkken Intent'ten **önce**, kapalıyken bugünkü yerinde.
İki kopya yazmak, bu belgenin defalarca ölçtüğü *"kimlik asimetrisi"*ni üretirdi.

#### Kanıt API'ye HİÇ dokunmadan alındı

Kural-tabanlı sağlayıcıda `select_cube` **yoktur** → Intent yolu offline zaten atlanır ve
bayrak farkı **görünmez**; gerçek sağlayıcıyla ölçmek kota harcar (bu turda kota doldu).
Çözüm: **çağrıldığını sayan sahte bir seçici**. Ölçüldü:

* bayrak **KAPALI** → Intent-JSON **çağrılıyor** (bugünkü davranış, KURAL B tabanı)
* bayrak **AÇIK** → Intent-JSON **HİÇ çağrılmıyor**, ayırt edici chip'ler dönüyor
  (*"bakiye (cari hesap)"* · *"bakiye (mizan…)"*)

*"Yalnız cevabı değiştirmek yetmez — maliyet de doğmamalı"* şartı böylece kilitlendi.

#### KURAL B: varsayılan **KAPALI** ve nedeni yazılı

Kapsam kaybı **gerçektir**: bugün LLM'in cevapladığı 53 sinonimlik nüfus netleştirmeye
düşer. Kazanç (kapanan sessiz-yanlış) ile kaybın kıyası **gerçek sağlayıcıyla** ölçülmeli;
o ölçüm bu turda **kotaya takıldı**. Ölçmeden açmak, 2a-1'in `elektrik` hatasını (kimlik
silindi, **388 cevap kayboldu**) tekrarlamak olurdu.

⚠️ **Bir testim de kırılgan çıktı ve düzeltildi:** `test_kapanis_zinciri` `_try_kpi` ile
`_try_fresh_intent` **arasını** tarıyordu; araya yeni bir yardımcı eklendiği an onun
(meşru) mühürsüz dönüşünü `_try_kpi`'ninmiş gibi gösterdi. Ölçülmesi gereken şey
`_try_kpi`'**nin kendi gövdesi**dir → `ast`'a taşındı.

**Ölçüm:** test **1828 → 1841** · eval `+0,0/+0,0/+0,0` · `nl_accuracy` **63/63** · korpus
kapısı **yeşil** (%93,2 sabit). 6 test: `tests/test_netlestirme_onceligi.py`.

### 6.8z FAZ F2 — YOL SINIRI: "güven eşiği"nin DÜRÜST hâli ✅

Araştırma raporu bir *"güven eşiği ayarı"* önerdi ve bunu **rakiplerin kopyalayamayacağı
fark** diye işaretledi: *"yalnız şu yüzdenin üstünde güvenilen cevapları göster."*

**Sayısal eşik olarak UYGULANMADI** — bu belgenin kendi kararına aykırı:

> *"…kalibre edilmediği sürece o sayı bir güven değil bir **SÜStür**."*

`_build_explain`'in ürettiği `1.0 / 0.85 / None` **hesaplanmış bir olasılık değildir**; üç
değerli bir **yol etiketidir**. Bunu bir yüzde gibi sunmak, tam da yasaklanan süs olurdu —
üstelik kullanıcı onu *kalibre edilmiş* sanacağı için **daha zararlı** bir süs.

#### Kurtarılan hâli: eşik değil, MERDİVENİN KENDİSİ

Kullanıcının gerçekten istediği şey bir sayı değil, bir **güvence sınıfı**dır. Bizde o
sınıf zaten var ve **deterministik**: cevaplama merdiveninin basamağı.

| `yol_siniri` | İzin verilen | Kesilen |
|---|---|---|
| `"deterministik"` | VQR replay · `route()` | Intent-JSON · Discovery |
| `"llm"` | + Intent-JSON (**katalogdan seçim**) | Discovery (ham SQL) |
| `null` / `"kesif"` | + Discovery | — (**bugünkü varsayılan**) |

Aynı kullanıcı değeri (güvene göre süzme), **sıfır uydurma kalibrasyon**. Ve bu ayar
gerçekten kopyalanamaz: rakiplerin **yolu yok** — tek bir kutuları var, süzülecek bir
basamak üretemezler.

#### Sessiz kesme YOK (bu fazın asıl kuralı)

Bir sınır yüzünden cevapsız kalınırsa **nedeni yazılır** — hem `note` hem `trace`:

> *"Yol sınırınız 'yalnız küp' olduğu için bu soruyu ham SQL ile cevaplayabilirdim ama
> cevaplamadım."*

Aksi hâlde kullanıcı kendi koyduğu ayarı unutur ve ürünü **yeteneksiz** sanır. Bir ayarın
kullanıcıyı ürün hakkında yanıltması, ayarın kendisinden büyük kusurdur.

İkinci koruma: **tanınmayan değer sınır SAYILMAZ**. Bir yazım hatasının (`"determinstik"`)
cevabı sessizce kesmesi, sınırın kendisinden zararlıdır → bilinmeyen değer varsayılana
düşer.

#### KURAL B ölçüldü — varsayılan **birebir** aynı

    sınır=None           bu yıl makine bazında oee    source=cube   sql=True
    sınır=None           asdf qwerty zxcv             source=rule   sql=True
    sınır=llm            asdf qwerty zxcv             source=None   sql=False  + neden
    sınır=deterministik  asdf qwerty zxcv             source=None   sql=False  + neden

`route()`'un çözdüğü soru **her seviyede** cevaplanır (kapı fazla geniş değil); sınırsız
yolda hiçbir şey değişmez.

#### Frontend tüketicisi kapıda

`AskRequest`'e eklenen alanın **kullanıcı kontrolü** olmalı, yoksa özellik bitmemiştir —
bu deponun *"yetim alan"* disiplininin **istek tarafı**. `ChatPanel` üç düğmeli bir seçici
sunar (*yalnız küp · +LLM · keşif dahil*) ve test kaynakta `yol_siniri` + `onYolSiniri` +
insan-okur etiketi arar.

**Ölçüm:** test **1841 → 1851** · eval `+0,0/+0,0/+0,0` · korpus kapısı **yeşil** (%93,2
sabit) · senaryo süiti değişmedi · `tsc --noEmit` temiz. 10 test:
`tests/test_yol_siniri.py`.

### 6.8y FAZ H — ONAYLI YAZMA: yasak kaldırılmadı, KADEMELENDİ ✅

`app/tools.py` yazma araçlarını bilerek kayda almamıştı (*"Ajan YAZAMAZ"*). Karar
doğruydu ama **yarım**: kullanıcı yazma isteğini yine de söylüyor ve sistemde *"eylem
ifadesi"* diye bir sınıf olmadığı için istek bir **veri sorusu** sanılıyordu.

#### Ölçülen kusur — plandan daha kötü çıktı

    "her pazartesi bu raporu bana yolla"  → source=rule, **SQL ÜRETTİ**, 1 satır
    "bu raporu her sabah 8'de e-postala"  → source=rule, **SQL ÜRETTİ**, 1 satır
    "bunu panoya ekle"                    → *"«bunu» yerine «gunu» mi demek istedin?"*
    "şunu panoya kaydet"                  → *"«kaydet» yerine «adet» mi demek istedin?"*

Yani ajan **yazmıyordu ama UYDURUYORDU**: sorulmayan bir soruya cevap üretiyordu. `prev`
bağlamı verilmişken bile `yeni_konu=True` — istek hiç çapalanmıyordu. Kök neden D1
(sosyal) ve D2 (*"analiz et"*) ile **aynı ailedendir**: veri sorusu OLMAYAN bir ifade
sınıfının tanımsızlığı. `app/eylem.py` o sınıfı tanımlar.

#### Üç değişmez

1. **Argümanlar LLM'den GELMEZ.** Önerinin `cube_query`'si konuşmada **zaten
   doğrulanmış** sorgudur. Bir LLM'in uydurduğu sorgu bir zamanlamaya yazılsaydı o
   uydurma **her hafta** tekrar koşardı — sessiz-yanlışın kalıcılaştırılmış hâli.
2. **Öneri yeni YETKİ yaratmaz.** Onay ucu (`POST /ask/eylem`), kullanıcının kendi
   eliyle çağırabileceği ucun **ta kendisini** çağırır. Önerinin istemcide taşınması bu
   yüzden güvenlidir: kurcalanmasından **kazanılacak bir şey yoktur**. Güvenlik bir
   imzadan değil, **yetki yüzeyinin genişlememesinden** gelir.
3. **Çapa yoksa öneri de yok.** Rapor yokken *"panoya ekle"* çalıştırılamaz → sistem
   sınırını **söyler**, uydurmaz.

#### Onay ucunun üç koruması — ve neden bu sırayla

| # | Koruma | Kaçırılırsa |
|---|---|---|
| 1 | Eylem **kayıttan** çözülür (`eylem.beyan`, bilinmeyen ad → 400) | istemci eylem uydurur; yazma yüzeyi sınırsızlaşır |
| 2 | `authorize()` **yeniden** çağrılır | TOCTOU: rol öneriyle onay arasında düşmüş olabilir |
| 3 | Argümanlar **var olan handler'a** verilir | doğrulama ikinci kez yazılır ve zamanla ayrışır (bu deponun 1 numaralı kusur sınıfı) |

Bir `ast` testi (3)'ü kilitler: onay ucunda `parse_cube_query` **geçmemeli**, buna
karşılık `add_widget`/`create_schedule` **geçmelidir**.

#### Sessiz kesme yine yasak

*"her ay yolla"* → `ScheduleRequest` yalnız `hour|day|week` destekler. Sessizce
haftalığa çevirmek **kullanıcının istemediği bir zamanlama kurmak** olurdu; onun yerine
ne YAPABİLDİĞİMİZ söylenir (*"saatlik, günlük ve haftalık"*).

#### Kapı dar tutuldu — iki kanatlı

Zamanlama sınıfı için **yinelenme VE teslim fiili** birlikte aranır: *"her ay ciro"* bir
**granülerlik** sorusudur, zamanlama değil. `raporla` fiili bilerek listede **yok**
(`_syn_hit` çekime toleranslıdır ve *"raporları"* onu eşleştirirdi); çıplak `at` da yok.

#### İki ölçüm aracı kusuru daha (bu turda 11. ve 12.)

* `_norm` **kesme işaretini siler**: `09:00'da` → `09:00da`. Saat deseni dakikadan
  sonra `\b` istiyordu; kesme gidince ardından harf geldiği için çapa tutmadı ve desen
  `00da`ya kayarak saati **00:00** okudu. Çapa *"rakam değil"* (`(?!\d)`) yapıldı.
* Şemadaki `measures`/`dimensions` **dize listesidir**; etiket oradan türetilemez.
  Etiketler artık `next_step_chips`'in kullandığı **aynı** derlenmiş katalogdan gelir —
  ikinci bir etiket kaynağı açılmadı.

#### Frontend: onay kartı

`ReportCard` öneriyi bir onay kartı olarak basar (özet · *Onayla* · *Vazgeç*). Düğme
`oneri.izin` `/auth/me` `permissions` listesinde yoksa **hiç çıkmaz** — rol matrisi UI'a
kopyalanmaz. React hook sırası sabit kalsın diye kayıttaki izinler baştan çözülür ve bir
test, **kayıttaki her iznin frontend haritasında bulunduğunu** kilitler (aksi hâlde yeni
bir eylem eklenince düğme sessizce kaybolurdu).

**Ölçüm:** test **1851 → 1887** · eval `+0,0/+0,0/+0,0` · korpus kapısı **yeşil** (%93,2
sabit) · senaryo süiti değişmedi · `tsc --noEmit` temiz. 36 test:
`tests/test_eylem_onayi.py`.

⚠ **Bu turda öğrenilen bir ölçüm kuralı:** kapı konteyneri koşarken **repoya
yazılmaz**. Mount canlıdır; süit koşarken `MIMARI.md`/`lab/` düzenlediğim koşumda
`test_measure_preview` iki hata verdi, dokunulmayan koşumda **aynı kod yeşil** çıktı.
Aynı sınıf: *"ölçüm aracının kendisi de bir bağımlılıktır"* (§6.4) — ölçüm **ortamı** da
öyle.

### 6.8x FAZ E — BAĞLAM ÇAPASI + SUNUM TERCİHİ ✅

#### E1 · Atıf ifadeleri cevabı ÖLDÜRÜYORDU (ölçüldü)

**Aynı** isteğin atıflı hâli ölüyordu:

    "makine bazında ayır"                        → source=cube  dim=['makine']   ✅
    "az önce dediğin gibi makine bazında ayır"   → source=None  CEVAPSIZ         ❌
    "yukarıdaki raporu vardiya bazında ver"      → source=rule  dim=None         ❌❌

Üçüncüsü en kötüsü: cevap **verdi** ama Discovery'ye düşüp **kırılımı kaybetti** —
`source=rule` rozetli sessiz-yanlış. Beş atıflı ifadenin **dördü** ölmüştü; atıfsız
hâllerinin **beşi de** çalışıyordu, yani kayıp tamamen atıf sözcüklerindendi.

Kesen kapı `deterministic_refine`'ın **kendi** `_coverage_ok`'uydu. Sınıf D1'in
(`sosyal_ayikla`) kardeşidir: **kalıp ifadenin parçaları katalog anlamı taşımaz.**

#### Ayıklama neden SPAN tabanlı (kelime kümesi DEĞİL)

`sosyal_ayikla` eşleşen kalıbın **kelimelerini** toplayıp o çekirdeğe sahip her token'ı
düşürür. Sosyal sözcükte zararsızdır; atıfta **yıkıcı** olurdu:

    "önceki soruyu önceki aya göre"  → kalıp `onceki soru` eşleşir
                                     → kelime kümesi {onceki, soru}
                                     → DÖNEM ifadesindeki `önceki` de düşerdi

Span tabanlı silme bu sınıfı tamamen kapatır. Makine tek sahiptedir
(`cube_router.kalip_spanlari` / `span_ayikla`) — atıf sözlüğü ve sunum-tercihi işareti
**aynı** işi ister, ikinci bir kopya çekim toleransını zamanla ayrıştırırdı.

#### E2 · `history` yalnız BOOLEAN olarak okunuyordu

`context.coz` `prev_sql and history` diye bakıyor, **içeriğine hiç bakmıyordu**. Yapısal
bağlam yokken atıflı mesaj `KURAL_HAM`'a düşüp **ham SQL** üretiyordu (`source=rule`).

Yeni `KURAL_ATIF` + `Baglam.ham_ifade` (iki turluk pencere, makbuzda `raw_window`):
önceki turun metni **deterministik `route()`** ile yeniden çözülür ve çıkan sorgu yapısal
çapa yerine konur. Bundan sonrası zaten var olan takip yoludur — **ikinci bir cevap hattı
yazılmadı**. `route()` çözemezse hiçbir şey uydurulmaz.

Pencere **iki turdur** ve bu bir sınır değil bir karar: üç ve üzeri tur *"hangi tur
kastedildi"* sorusunu doğurur, o da bir **retrieval** problemidir — raporun kendi ölçümü
retrieval'ı reddetti (+14/−16) ve bu modülün kuralı açık: bağlam çözümü bir anlama değil
bir **muhasebe** işidir.

#### E3 · Kalıcı sunum tercihi — ve neden ONAYDAN geçiyor

    "hep aylık göster"                     → *"Bu takip mesajını ilişkilendiremedim"*
    "bundan sonra hep tablo olarak göster" → *"«bundan» yerine «unvan» mi demek istedin?"*

Kapsam **bilerek dar**: raporun *"Memories"* önerisinin bir yarısı bu depoda **zaten
var** (terminoloji → `SynonymOverride`). Yalnız **sunum** yarısı eklendi.

**Tercih yazmak bir yazmadır → Faz H'nin onay kademesinden geçer.** Bir faz önce
*"onaysız hiçbir yazma"* deyip burada muafiyet açmak, bu deponun tekrar tekrar ölçtüğü
kusur sınıfı olurdu: **beyan var, kod onu tanımıyor.** `POST /tercihler` ucu **yoktur**
ve bir test bunu kilitler; yeni UI da gerekmedi — Faz H'nin onay kartı çalıştı.

Üç değişmez testte kilitli: tercih **ölçü/cube seçimine karışmaz** · **sessiz
uygulanmaz** ve **açık isteği ezmez** · **takipte uygulanmaz** (kullanıcı orada canlı bir
raporu yönlendiriyordur).

#### ⚠ Kendi ölçüm disiplinim kaydı — ve kapıya çevrildi

Atıf adaylarını katalogda taradım, sonra *"tekrar ailesini"* (`tekrar`, `yeniden`…)
**taramadan** ekledim. `test_sinonim_carpismasi` yakaladı:

    YENİ sinonim çakışması doğdu: 'yeniden islenen': kalite → parti

`yeniden islenen` `kalite` cube'unun **gerçek sinonimiydi**; `yeniden` sözcüğünü
ayıklamak o kimliği yok ediyordu — 2a-1'in (`elektrik` silinince **388 cevap kayboldu**)
aynı hatası. Kural zaten yazılıydı (`_misc_hit_words`: *"`fark` BİLEREK EKLENMEDİ"*) ama
uygulanmasını **insan dikkatine** bırakmıştım. Artık kapı: `tests/
test_kalip_sozlugu_carpismiyor.py` — **koşulsuz silinen her TEK SÖZCÜKLÜ kalıp katalogda
sahipsiz olmak zorunda.** Çok sözcüklü kalıp yapısı gereği güvenlidir (`yeniden ver`
eşleşir, `yeniden islenen` dokunulmaz).

**Ölçüm:** test **1887 → 1940** · eval `+0,0/+0,0/+0,0` · korpus %93,2 (kapı yeşil) ·
senaryo süiti değişmedi · `tsc --noEmit` temiz. 53 test: `test_atif_baglami.py` (24) ·
`test_sunum_tercihi.py` (19) · `test_kalip_sozlugu_carpismiyor.py` (10).

### 6.8w FAZ X — DENEYİM SÜİTİ: bir TURU değil bir KONUŞMAYI ölçmek ✅

`lab/deneyim.py`, var olan üç aracın **sormadığı** soruyu sorar:

| araç | sorduğu soru |
|---|---|
| `eval/run.py` | *tek soruda* doğru cube seçildi mi? |
| `lab/nl_corpus.py` | dört şirkette **regresyon** var mı? |
| `lab/konusma_senaryolari.py` | bir takip **turu** doğru çözüldü mü? |
| **`lab/deneyim.py`** | **bir KONUŞMA tatmin edici miydi?** |

13 thread, ürün sözleşmesinin **yedi satırına** karşı ölçülür; her senaryo yalnız
kendisini ilgilendiren satırları ölçer, gerisi `⊘ ÖLÇÜLEMEDİ`'dir.

#### İlk koşum DÖRT kusur çıkardı — dördü de tek turluk araçların göremeyeceği cinsten

**A · Takip düzenlemesi TABAN soruyu değiştiriyordu** (sessiz-yanlış):

    1) "bu yıl makine bazında oee"  → dim=['makine']                    ✅
    2) takip: "vardiya bazında"     → dim=['makine','vardiya']          ✅
    3) AYNI taban soru tekrar       → source=vqr, ['makine','vardiya']  ❌

Kullanıcının makine kırılımı isteyen sorusu, bir daha sorulduğunda **sormadığı** ikinci
kırılımı getiriyor ve her hücredeki sayı değişiyordu — üstelik `source=vqr` rozetiyle.
Kök neden *"beyan var, kod onu tanımıyor"*: fonksiyonun adı `_learn_chip_completion` ve
docstring'i *"bir raporu TAMAMLADIĞINDA"* diyor; kod ise yalnız *"önceki mesaj konu
taşıyor mu"* diye bakıyordu. **Tamamlama ile genişletme ayrı şeylerdir.**

⚠ İlk düzeltmem fazla genişti (`route()` bir şey döndürdü mü?) ve **iki altın testi
düşürdü**. Doğru ölçüt `route()` değil **cevaplanabilirlik**tir: şekil üretilse bile dönem
eksikse ürün *"hangi dönem?"* diye SORAR, yani soru cevaplanmamıştır ve kullanıcının onu
tamamlaması **gerçek** bir tamamlamadır. Ayıran şey `needs_period` (bkz. §6.2 güncellemesi).

**B · `geçen yılla kıyasla` takipte cevapsız** — kimlik asimetrisi: mekanizma **taze**
dalda vardı, kardeşi olan **takip** dalında yoktu. Bir analistin en doğal ikinci cümlesi
dürüst rette kalıyordu. Düzeltirken gövde kopyalanmadı: `_kiyas_cevabi` tek gövde, iki
çağıran (bir `ast` testi bunu kilitler).

**C · `compare_mode` çekim varyantlarını ELLE sayıyordu** (`onceki yila`, `onceki yilla`,
`onceki yil ile`…) — `_syn_hit`'in yerine geçmek için var olduğu anti-desen. Listenin
deliği ürün kusuru üretiyordu (*"geçen yılla kıyasla"* → `None`). Yapısal kural iki
kanatlı: **dönem-geri ifadesi + kıyas işareti**, işaret ya **bitişik** (edat/araç eki) ya
da cümlede bir **kıyas fiili**. Bitişiklik şartı kritik: *"geçen yıl makineye GÖRE fire"*
kıyas DEĞİLDİR ve öyle sayılsaydı sıradan bir kırılım sorusu YoY'a çevrilirdi.

**D · Dönem ifadesinin YER-DURUM eki cevabı öldürüyordu** — Türkçede en doğal söyleyiş:

    "son 6 ay fire"    → route VAR ✅        "geçen ay fire"    → route VAR ✅
    "son 6 ayDA fire"  → route YOK ❌        "geçen ayDA fire"  → route YOK ❌

Kök neden **iki katmanlı** ve tek başına hiçbiri görünmüyordu: (1) `_REL_DATE`/`_PREV_RE`
**kökü** yakalıyor, çekimi değil; (2) `_uncovered` bilinen kelimeleri `len >= 3` ile
süzüyor → **`ay` elenir ve kendi çekimini kapsayamaz**. En sık kullanılan dönem birimi,
çekimli hâlinde hiçbir zaman kapsanamıyordu.

#### Ölçüt ÜÇ KEZ düzeltildi — ve dersi genelleştirildi

Sözleşmenin *"≥3 olgu"* şartı önce düz kırılımı, sonra düz zaman serisini haksız kırmızı
gösterdi. `interpret()` deterministiktir: `shape` bir **boyut**, `trend`/`peak` bir **zaman
ekseni** ister — üçüncü olgu ancak **ikisi birden** varken doğar.

> Ders (§6.4'ün genişletilmiş hâli): bir eşiği **tahminle ayarlama**, **üreten
> mekanizmadan türet**. Aksi hâlde araç ürünü değil kendi varsayımını ölçer.

#### Bilerek AÇIK bırakılan kırmızı

`o ayı makine bazında aç` — işaret zamirini önceki sonucun bir **satırına** çözmek gerekir.
Mekanizma var (`drill.select_cube_query`) ama yalnız **tıklamayla**; yazıyla söylenen hâli
yeni bir bağımlılık sınıfı ister (önceki sorguyu yeniden koşup satır değeri çözmek).
Kapatılmamış bir bulguyu yeşile boyamak bu süitin varlık nedenine aykırıdır — **kırmızı
kalıyor ve bir sonraki döngünün girdisidir.**

**Ölçüm:** test **1940 → 1990** · eval `+0,0/+0,0/+0,0` · korpus %93,2 (kapı yeşil) ·
senaryo süiti değişmedi · deneyim süiti **34 ✅ / 1 ❌ / 56 ⊘** (yapısal duman).
49 test: `test_faz_x_bulgular.py` (33) · `test_deneyim_araci.py` (16).

#### CANLI KOŞUM — ve `--live`'ın ÜÇÜNCÜ kez karşılıksız çıkması

Süit gerçek sağlayıcıyla koşuldu (`gemini → groq → xai → openrouter`): **33 ✅ / 2 ❌ /
56 ⊘**. Yapısal modda açık olan `grafik_ustunde` kırmızısı canlıda **yeşile döndü** —
deterministik yolun kapatamadığını Intent-JSON kapatıyor; bu, boşluğun yok olduğu değil
**LLM'e bağımlı** olduğu anlamına gelir.

Ama asıl bulgu koşumun kendisiydi. Log *"CANLI MOD"* yazarken
`LLM sağlayıcı: RuleBasedSqlGenerator` diyordu:

> **Ortamı geri yüklemek YETMİYOR — ayar önbelleği de temizlenmeli.**
> `app.config.get_settings` `@lru_cache`'lidir ve **`import app.main` onu doldurur**.
> Bu araçlar `tests.conftest`'i modül seviyesinde yükler (env kurulumu için) → önbelleğe
> `provider="rule"` girer ve sonraki env geri yüklemesi ona **hiç ulaşmaz**.

İlk düzeltme (conftest'in env'i sabitlemesi) **ortamı** onarıyordu, **ayarı** değil.
Üstelik `nl_accuracy.py` bu fonksiyonun **kendi kopyasını** taşıyordu: sahipteki sözleşme
güçlendirilirken kopya geride kaldı — yani `nl_accuracy --live` de sessizce `rule` ile
koşuyordu ve **o koşumlara dayanarak bayrak kararı alınabilirdi**.

Kök neden kapatıldı: kopya silindi (tek sahip), `get_settings.cache_clear()` eklendi ve
**beyan ölçüme çevrildi** — gerçekten canlı bir üretici kurulmuyorsa `--live` KOŞMAZ
(fail-closed) ve rapor başlığı üreticinin adını taşır (`auto (FailoverSqlGenerator)`).

#### FAZ F'in AÇIK KARARI KAPANDI — artık ertelenmiş değil ÖLÇÜLMÜŞ

`netlestirme_onceligi` *"kapsam kaybı ile kazanç kıyası gerçek sağlayıcıyla ölçülmeli;
o ölçüm kotaya takıldı"* diye kapalı bırakılmıştı. Canlı yol açılınca ölçüldü:

| ölçüm | sonuç |
|---|---|
| A/B, 63 etiketli vaka | **bozulan 0 · kurtarılan 0** |
| Kurtarma, 15 gerçek ifade | cevaplanan **12 → 8** · kurtarılan 1 (**doğru ölçüyle 0**) · kaybedilen 5 |
| Kararlılık, aynı soru ×3 | **5/6 KARARLI** (tek kararsız: *"bu yıl borçları"* → cari×2, mizan×1) |

Kararlılık ölçümü belirleyici oldu ve **kabul ölçütünün göremediğini** gösterdi: araç
*"cevaplanan"* sayıyor, bir netleştirme cevap sayılmıyor — oysa asıl soru o cevapların
**doğru olup olmadığıydı**. Ölçülebilir vekil: seçim kararlı mı? Kaybedilecek 5 cevap
**yazı-tura değil**; model tutarlı ve savunulabilir seçiyor (`cari` = müşteri defteri).

**Karar: KAPALI kalıyor.** B2 ölçütü (doğru kurtarma > 0) karşılanmıyor ve kayıp gerçek.

⚠ Ölçüm sırasında **ayrı** bir bulgu: *"bu yıl bakiye"* **kararlı** biçimde `mizan.bakiye`
seçiyor ve cevap **₺0** — mizan yapısı gereği sıfıra denkleşir. Bu bir motor kusuru değil
bir **katalog kararıdır** (çıplak `bakiye` hangi cube'un?) ve katalog sahibine aittir;
sessizce yamalanmadı, kayda geçti.

⚠ Süitin kendi muhasebesinde de bir kusur bulundu ve düzeltildi: tıklanacak chip yokken
`__CHIP__` turu boş bir *cevap* gibi listeye giriyor ve MAKBUZ satırını haksız kırmızı
yapıyordu — **aynı kusur iki satırda sayılıyordu**. Artık `olcum_disi`: bir cevap değil,
ölçüm önkoşulunun yokluğu.

### 6.8v FAZ S — AKIŞ + STEERING: dürüst fiyat ödendi, iki karar ÖLÇÜMLE verildi ✅

#### Karar 1 · Akış İKİNCİ BİR GERÇEKLİK değil, bir TAŞIMA

Plan doğruydu: SSE/WebSocket kodda **0 satır**. Ama *"canlı düşünme adımları"* deneyimi
**zaten vardı** — `AskJob.trace_json` biriken adımları taşıyor, `pollAskJob(onProgress)`
onları 1,5 sn'de bir çekiyor, `ChatPanel.liveTrace` gösteriyor. Eksik olan ikinci bir
olay hattı değil, o gerçekliğin **anında** iletilmesiydi.

Canlı süre ölçümü kararı verdi:

    deterministik yol   ~100–800 ms   → akış GEREKSİZ
    LLM (Intent) yolu   2,8–5,5 sn    → sessizlik TAM ORADA

`GET /ask/jobs/{id}/stream` poll ucuyla **aynı okuyucuyu** (`_job_durum_oku`) kullanır.
İki ayrı okuyucu olsaydı tenant izolasyonu iki yerde yazılır, biri unutulurdu — ve
*"ne yapıyor"* sorusunun iki anlatısı doğardı, biri yalan söylemeye başlardı.

#### Karar 2 · `EventSource` KULLANILMADI — bu bir güvenlik kararıdır

`EventSource` **Authorization başlığı gönderemez**; tek yolu token'ı URL'e koymaktır ve o
token sunucu loglarına / tarayıcı geçmişine sızar. Deponun açık kuralı: *"access token
memory'de, localStorage'a ASLA"*. Bu yüzden **SSE BİÇİMİ** korunur ama taşıma `fetch` +
`ReadableStream`'dir — Bearer aynen çalışır, hiçbir değişmez gevşetilmez. Format aynı
olduğu için ileride gerçek bir `EventSource` tüketicisi de eklenebilir: **karar geri
alınabilir kalır.** Akış kurulamazsa (eski tarayıcı, ters vekil tamponlaması, ağ)
sessizce **poll'a düşülür** — yetenek kaybı yok, yalnız gecikme eski hâline döner.

#### STEERING — ölçülen kusur: geç gelen cevap BAĞLAMI GERİ ALIYORDU

Komposer koşarken kilitli **değil** (bilerek: *"dur, onu değil"* diyebilmek ürünün
vaadi), dolayısıyla iki istek aynı anda uçabiliyor. Ve **yavaş olan sonra çözülünce**
`onSuccess` aktif thread'i/bağlamı/görünümü geri alıyordu — kullanıcı yön veriyor, sistem
sessizce eski cevaba dönüyordu.

Sıra numarası bunu kapattı ve **her iki yanlış çözümden de kaçındı**: geç gelen cevap
*sessizce yutulmaz* (geçmişe yazılır — plan: *"sessiz iptal YOK"*) ama aktif bağlamı da
*ele geçiremez*. Kart bunun **nedenini** söyler; söylemeseydi *"neden eski rapor geri
geldi?"* sorusu cevapsız kalırdı. `steering_golgede` **istemci kararıdır** ve backend'e
sızmadığı testle kilitlidir — sunucu, sahip olmadığı bir zamanlama bilgisini iddia etmez.

#### Kapının yakaladığı iki şey

* `StreamingResponse` yanıtı üretici çalışmadan **başlatır**; doğrulamayı üreticinin
  içinde yapmak istemciye temiz bir 400 yerine **bozuk akış** veriyordu → doğrulama
  akıştan öne alındı.
* Eklediğim davranışsal test **sıraya bağımlıydı**: *"dönem sorulmalı"* diyordu ama
  `test_ask_golden` o soruyu VQR'a öğretiyor ve dönem kapısı sonrasında **meşru biçimde**
  atlanıyor. Tek başına yeşil, süitte kırmızıydı — yani bir davranışı değil bir SIRAYI
  ölçüyordu. Sıradan bağımsız değişmez: **ya sorulur ya cevap açık dönem taşır**; yasak
  olan üçüncü ihtimal, dönemi sormadan sessizce tüm zamanları toplamaktır.

⚠ **Kendi kuralımı çiğnedim ve bedelini ölçtüm:** kapı koşarken teşhis için ikinci bir
test konteyneri açtım → compose çakışması → *"2004 errors in 73s"*. Depo kuralı
(*"iki test konteyneri ASLA paralel"*) hız için bile esnetilmez; o koşum bir ölçüm değil,
gürültüdür.

**Ölçüm:** test **1990 → 2004** · eval `+0,0/+0,0/+0,0` · korpus %93,2 (kapı yeşil) ·
senaryo süiti değişmedi · `tsc --noEmit` temiz. 10 test: `tests/test_akis_ve_steering.py` · 14 test: `tests/test_gercekci_senaryo_bulgulari.py`.

### 6.8u GERÇEKÇİ SENARYO TURU — süit "daha iyi senaryo" isteğiyle zenginleştirildi ✅

Kullanıcı isteği: *"biraz daha canlı test yap daha iyi senaryolarla daha gerçekçi."*
Senaryo **çoğaltılmadı, İYİLEŞTİRİLDİ** (beyan edilen 12–15 aralığı korundu): ince olanlar
konuşma diline çekildi, iki **gerçek iş akışı** eklendi —
`uretim_muduru_sabahi` (7 tur: selam → dünkü durum → en kötüsü → neden → geçen yılla kıyas
→ haftalık zamanla → teşekkür) ve `yazim_hatali_gercek_kullanici` (yazım hatası, eksik
cümle, küçük harf).

**Canlı sonuç: 41 ✅ / 1 ❌ / 63 ⊘.** Sabah rutini uçtan uca çalıştı ve merdivenin her
basamağını tek thread'de gösterdi: sosyal → deterministik cube → sıralama → **dürüst ret**
(*"`ort_oee` bir ortalama/oran — katkı payı matematiksel olarak tanımsız"*) → YoY kıyas →
eylem önerisi → sosyal.

#### Ve gerçekçi senaryo İKİ YENİ KUSUR çıkardı

**A · Boş sonuç SESSİZ dönüyordu.** `satır=0 · not=None · yorum=None`. Kullanıcı boş bir
tablo görüyor, nedenini bilmiyor: soru mu yanlış anlaşıldı, veri mi yok, filtre mi dar?
Bir *"şirket beyni"*nin verebileceği en kötü cevap sessiz bir boşluktur — okuyucu onu
**kendi varsayımıyla** doldurur. Not artık deterministik ve **uydurmuyor**: *"veri yok"*
demiyor, *"bu aralıkta (2026-07-27 – 2026-08-02) kayıt bulunamadı"* diyor. İkisi farklı
iddialardır ve ikincisi ölçülebilir olandır.

**B · Takvim yılı ifadesi anlaşılmıyordu.** *"2019 yılında makine bazında oee"* →
***"«yilinda» yerine «yield» mi demek istedin?"*** — D1'in absürt-öneri sınıfının aynısı,
kökü yine biçimbirim (Faz X'te kapatılan ailenin kaçan üyesi). Çıplak `2019` **bilerek**
kapsam dışı: dört haneli bir sayı bir hesap/şube/TRCODE **değeri** de olabilir
(`_value_token_hit`'in kendi notu bu tuzağı kaydediyor) — belirsizde **dönem sormak**,
uydurmaktan iyidir. En az bir yıl işareti (`yıl`/`sene` ya da hâl eki) aranır.

⚠ Testlerimden biri yine **pencereyle** ölçüyordu (*"koşulun yakınında bir yerde"*); yorum
bloğu uzadıkça kayan bir pencere, kapının doğru şeyi ölçtüğünü garanti etmez. Koşulun
**kendisi** aranır hâle getirildi.

**Ölçüm:** test **2004 → 2018** · eval `+0,0/+0,0/+0,0` · korpus %93,2 (kapı yeşil) ·
senaryo süiti değişmedi · canlı deneyim süiti **41 ✅ / 1 ❌ / 63 ⊘**.

### 6.9z FAZ 8 — SÜİT YENİDEN KOŞULDU: kalan iki "kusur"un ikisi de ÖLÇÜM ARACININDI ✅

Planın kapanış şartı: *"Faz 0.5'in **aynı** süiti yeniden koşulur — **yeni senaryo
YAZILMAZ**, önce/sonra kıyaslanır. Kaç vaka OK'e döndü, kaç **yeni sınıf** açığa çıktı
raporlanır; yeni sınıflar bir sonraki döngüye girdi olur — **döngüsel** bir kapı."*

| sınıf | Faz 0.5 (ilk) | Faz 0.5 (düzeltme sonrası) | **Faz 8** |
|---|---|---|---|
| `coklu_ay_trendli` | **0/6** | 5/6 | **5/5** |
| `gorunum_donusumu` | **0/5** | 4/5 | **4/4** |
| `konu_degisimi` | 2/5 | 2/5 | **4/4** |
| `donem_duzeltme` | 4/6 | 5/6 | **5/5** |
| `ayrik_ay` · `coklu_ay_trendsiz` · `liste_niyeti` | 4–5/5–6 | aynı | **hepsi tam** |

**Dokuz sınıfın dokuzunda da erişim = doğruluk = tam** (tek istisna aşağıda açıklanan
muhasebe artefaktı).

#### Kalan iki "kusur"un ikisi de ÜRÜN HATASI DEĞİLDİ

`konu_degisimi` **2/5** ve `donem_duzeltme`'nin kalan başarısızlığı **aynı köke** çıktı:
senaryo üreteci cube'un **ilk** ölçüsünü körlemesine alıyordu ve o ölçü `borç`a denk
geliyordu — `borç` **gerçekten belirsizdir** (`cari` + `mizan`), yani §6.1g'nin netleştirme
chip'i **doğru şekilde** ateşliyordu. Senaryo o zaman *niyet ettiği şeyi* (konu değişimi ·
dönem daraltma) değil **netleştirme yolunu** test ediyor ve "başarısız" raporluyordu.

Üreteç artık **belirsiz olmayan** ilk ölçüyü seçiyor (`route()` ile doğrulayarak); hiçbiri
yoksa o cube için senaryo **kurulmuyor** (sessizce yanlış vaka üretmektense hiç üretmemek).

> ⚠️ **BU OTURUMDA BEŞİNCİ KEZ ÖLÇÜM ARACININ KENDİSİ YANLIŞ ÖLÇTÜ.**
> (1) `nl_corpus` sinonim taraması yanlış→cevapsız dönüşümünü "iyileşme" saydı ·
> (2) `_daraldi` beklenen cube'un zaman boyutunu sabitledi · (3) `-(y)İz`'i isme ekledi ·
> (4) `-sIz`'i kayıp saydı · (5) belirsiz ölçüyle senaryo kurdu.
> MIMARI §6.4'ün dersi (*"ölçüm aracının kendisi de bir bağımlılıktır"*) bu oturumun en
> çok tekrarlanan bulgusu oldu. **Hepsi yakalandı çünkü her sayı bir vaka raporuna
> bağlıydı** — sınıf-başına rapor olmasaydı beşi de "ürün kusuru" diye kayda geçerdi.

#### Muhasebe artefaktı dürüstçe

`netlestirme_cevabi` erişim **0/1** görünüyor: o sınıfın ilk adımı **bilerek** `cube_query`
üretmez — netleştirme chip'i **geçerli ve doğru** bir cevaptır. `dogruluk` kanalı **1/1**
gerçeği söylüyor. **Sayaç bu sınıf için gevşetilmedi**: her netleştirmeyi "erişim" saymak
metriği zayıflatırdı. Sayaç değil **kayıt** düzeltildi.

#### Yeni sınıf açığa çıkmadı

Planın *"kaç yeni sınıf açığa çıktı"* sorusunun cevabı: **sıfır**. Süit döngüsel kapı
olarak yerinde — bir sonraki tur `--live` moduyla koşulmalı (Faz 3a'nın kazanç ölçümü ve
§1.7'nin embedder-açık doğrulaması oraya bağlı).

### 6.8aa FAZ 7 — ARAŞTIRMA SIÇRAMALARI: ölçüldü, ÜÇÜ DE BENİMSENMEDİ ✅
> ⟳ *(FAZ −1/A12: bu başlık `### 6.8z` idi ve **1309. satırdaki Faz F2 başlığıyla
> ÇAKIŞIYORDU**. `6.8u…6.8z` dizisi dolduğu için `6.8aa` ile devam edildi. Hiçbir yerden
> atıf almadığı ölçüldü → yeniden numaralama güvenli.)*

Planın disiplini: *"kör benimseme YOK — önce **ölçülmüş** gölge-mod spike; **kazanç yoksa
entegre EDİLMEZ**"*. `lab/golge_spike.py` kazancın **ÜST SINIRINI** ölçer: bir teknoloji
**en iyi ihtimalle** kaç soruyu kurtarabilirdi? **Üst sınır küçükse teknolojiyi denemenin
maliyeti bile gereksizdir** — ve bu, kütüphaneyi kurmadan bilinebilir.

#### (1) Türkçe morfoloji (Zeyrek/Zemberek) — **BENİMSENMEDİ**, üst sınır **%0,48**

2511 gerçekçi **isim** çekimi denendi; 228'i çözülemedi. Ama ayrıştırınca:

| kırılım | adet | yorum |
|---|---|---|
| olumsuzluk eki (`-sIz`) | **186** | **red DOĞRU** — *"firesiz"* `fire`'ın ZIDDIDIR |
| zaten `_SUFFIX_ATOMS`'ta olan ek | 30 | kayıp morfoloji değil, belirsizlik |
| **gerçek morfoloji kaybı** | **12 (%0,48)** | `-cIlIk` · `-lArImIz` · `-lArIndA` |

**Karar: entegre EDİLMEZ.** JVM bağımlılığı (Zemberek) ya da bakımı belirsiz kısmi bir
port (Zeyrek) **%0,48** için alınmaz. Whitelist gerçekçi çekimlerin **%91'ini** kapsıyor
**ve olumsuzluğu doğru reddediyor** — bir morfoloji kütüphanesinin garanti *etmediği* şey.
`lab/panel/findings/003…md:53`'ün 2026 başındaki kararı (*"ek-beyaz-listesi daha
az-invaziv ve deterministik"*) böylece **ölçümle de doğrulandı**.

> ⚠️ **ÖLÇÜM ARACIM İKİ KEZ YANLIŞ ÖLÇTÜ** (bu oturumda ÜÇÜNCÜ ve DÖRDÜNCÜ kez —
> MIMARI §6.4'ün dersi):
> 1. İlk sürüm `-(y)İz`'i **isme** ekliyordu (`agirlik+yiz` = *"agirlikyiz"*) ve **%100
>    kurtarılabilir** gibi anlamsız bir sonuç veriyordu. `-(y)İz` **fiile** eklenir; bir
>    kütüphane o diziyi "kurtarsaydı" bu kazanç değil **hata** olurdu.
> 2. İkinci sürüm `-sIz`'i kayıp sayıyordu ve Zeyrek'in kazancını **16 kat** abartıyordu.

#### (2) Semantik eşleştirme (embedding) — **BENİMSENMEDİ**, hedefi ÇÖZÜLMÜŞ problem

Embedding ancak leksik yolun **tamamen boş** olduğu yerde (R1) yeni bilgi getirebilir:
**99/470 (%21)** — kulağa büyük geliyor. Ama §6.1h ölçtü: **R1'in TAMAMI gerçek
ölçü-düzeyi belirsizliğidir** (aynı ad iki cube'da). **Embedding belirsizliği ÇÖZMEZ**,
yalnız aday üretir — ve o adaylar §6.1g'nin netleştirme chip'inde **zaten var**.
Yani hedef küme, başka bir fazın **çözdüğü** kümedir.

#### (3) SLM — **spike bile değil**

`verified_query` **0**, `measure_candidate` **0**. Plan zaten *"bugün için erken, yalnız
gözlem"* diyordu; ölçüm onu doğruladı.

#### Kısıtlar dürüstçe

`pip install zeyrek` **ağ ister** (CI: `--network none`); `DIMA_VQR_EMBEDDER=off`.
Kütüphanelerin kendisi burada koşturulamadı — ölçülen şey **onların HEDEFİDİR**. Bu bir
zayıflık değil, spike'ın **doğru biçimi**: hedef küçükse kütüphaneyi kurmak gereksizdir.

7 test: `tests/test_golge_spike.py` (gölge aracın üretimi **değiştirmediği** dahil).

### 6.7z FAZ 3b — PROMPT-ENHANCER: LLM metni düzeltir, KARAR hâlâ küpte ✅

T1'in **dördüncü, ayrı** LLM rolü. `llm.select_cube` **alan seçer**; enhancer **yapı
seçmez**, yalnız **metni** iyileştirir ve **aynı deterministik `route()`'a** geri verir.

**Hata yüzeyi yapısal olarak dardır:** çıktı bir metindir ve `route()` ona sıfırdan karar
verir. Model uydurma bir terim üretse bile `route()` onu **yine reddeder** — yani enhancer
en kötü ihtimalle *işe yaramaz*, **yanlış cevap üretemez**. Prompt da bunu pekiştiriyor:
*"katalogda karşılığı olmayan bir şey isteniyorsa soruyu OLDUĞU GİBİ döndür — uydurma bir
terime çevirmek, cevapsız kalmaktan KÖTÜDÜR."*

**Planın dört şartı:** (1) yalnız `route()` boş dönünce tetiklenir → sıfır-maliyet çoğunluk
dokunulmaz; (2) başarı **sessizdir**, iz makbuza `question_original`/`question_normalized`
olarak yazılır; (3) belirsizlik **mevcut** chip mekanizmasına devreder, **yeni UI yüzeyi
açılmaz**; (4) ucuz/seçici model.

#### Planın ZORUNLU ⟳ eklemesi: kapısız LLM çağrısı YOK

Çağrı `Planlayici.calistir()` üzerinden. Aksi halde yetkiye bağlanmaz, bütçeye sayılmaz,
makbuzda adım olarak görünmez — *"LLM ne zaman devreye girdi"* cevaplanamaz olurdu.

**Deterministik-önce kapısı ETİKETLE bağlandı**, kuralla değil: `llm.prompt_enhance`
`route` ile aynı `sorgu-uretimi` etiketini taşır, dolayısıyla `route` **planlayıcı
üzerinden** denenmeden seçilemez ve bunu **kapı kendisi zorlar**. Bu yüzden
`_prompt_enhance_dene` `route`'u planlayıcıya da çağırtır: *"denendi" demek yetmez, kapı
kendi kaydını görmelidir* — aksi halde kapı bir yorumdan ibaret kalırdı.

**Ön koşul VARSAYILMADI, ölçüldü:** planın *"enhancer belirsizlikte daraltılmış chip'e
devretmeli, yoksa Faz -1 öncesi 13-cube dump'ına devreder"* şartı bir testle sabitlendi.

> ⚠️ **BU FAZDA KENDİ KODUM AVLADIĞIM KUSUR SINIFINA DÜŞTÜ.**
>
> `features.yml`'e `prompt_enhancer: off` yazdım. **YAML 1.1 `off`/`on`/`yes`/`no`'yu
> BOOLEAN okur** — değer `"off"` string'i değil `False` oldu; `resolve_for`'un filtresi
> (`if v != "off"`) onu **elemedi** ve bayrak sonuç kümesinde **var** kaldı. İki bayrak
> (`prompt_enhancer` **ve Faz 5'in `t2_anlatici`**'si) **sessizce AÇIKTI**.
>
> Daha kötüsü: **Faz 5'in kendi testi bunu yakalayamamıştı**, çünkü kural-tabanlı
> sağlayıcıda `anlat` yok — yol zaten kapalıydı, yani *bayrak açık olduğu hâlde davranış
> doğru görünüyordu*. Tam olarak §6.1'in *"beyan var, kod onu tanımıyor"* sınıfı.
>
> Düzeltildi (`"off"` tırnaklandı) ve bir **kapıya** çevrildi: `features.yml`'deki hiçbir
> bayrak boolean OLAMAZ, hepsi `STAGES` içinden bir string olmak ZORUNDA
> (`test_YAML_off_TUZAGI_kapali`).

16 test: `tests/test_prompt_enhancer.py` · bayrak `prompt_enhancer` varsayılan `"off"`.

### 6.6z FAZ 2b — terfi kuyruğu beslendi + ÖLÇÜME BAĞLI İKİ KARAR verildi ✅

#### 2b-1 · Red gerekçesi TRİYAJA girdi (K2-ii)

Faz 0 `reject_reason`'ı ölçülebilir yapmıştı ama **tüketicisi yoktu** — bu deponun en sık
kusuru. Planın şartı literal: *"önceliği Faz 0'ın red-gerekçesi telemetrisi belirler —
**en çok hangi kelime kapıya takıldı**"*.

Aday kuyruğu (`/sadmin/synonyms/candidates`) artık her aday için `red_kodu` + insan-okur
`red_gerekcesi` + **takılan kelimeler** taşıyor. Kelimeler `cube_router`'ın kapsam
kapısıyla **aynı** dolgu sözlüğünden hesaplanır (`_period_hit_words | _misc_hit_words` →
`_uncovered`) — ayrı bir liste tutmak iki tarafı ayrıştırır ve admin'e kapının **gerçekte**
takıldığı kelimeden başka bir şey gösterirdi. R1/R10 telemetride bir **sayıydı**, burada
bir **eyleme** dönüşüyor: *"şu kelime şu cube'a sinonim olarak eklensin mi?"*

**Sıfır yeni uç açıldı** (`git diff`: 0 satır `@router`) — var olan onay akışı beslendi.
*"Yeni özellik yeni panel doğurmaz."* Uç sayısı testle sabitlendi (7).

#### 2b-2 · §1.7 KARARI: `auto_cube` replay'den ÇIKTI, few-shot'ta KALDI

Plan bunu *"ölçüm olmadan seçilmez"* diye bağlamış ve maliyetten korkmuştu: *"hızlı-öğrenme
faydasının %86'sını da götürür"*. **Bu korku bir VARSAYIMA dayanıyordu** — `auto_cube`
replay'inin gerçekten bir şey kazandırdığı varsayımına.

**Ölçüm varsayımı çürüttü.** `auto_cube` kaydı `_answer_from_cube_query`'de üretilir ve o
fonksiyon **hem saf `cube` (route) hem `cube+llm`** cevaplarına hizmet eder. Saf `cube`
cevabının replay'i **sıfır** kazandırır: `route()` onu zaten LLM'siz, sıfır maliyetle ve
**daha doğru** çözer — çünkü **router iyileşir, dondurulmuş kayıt iyileşmez**.

Bu oturumun kendi ölçümü kanıt: `elektrik tuketimi` · `toplam durus` · `sapma yüzdesi` ·
`ortalama sapma` — dördü de bu oturumda **cube DEĞİŞTİRDİ** (§6.1g/h). 2a-3 öncesi yazılmış
bir `auto_cube` kaydı, düzeltilmiş router'ın **doğru** cevabını engellerdi ve `source="vqr"`,
`confidence=0.95` rozetiyle gelirdi. **Yani replay yalnız yanlışı kalıcılaştırmaz,
düzeltmeyi de görünmez yapar.** Doğru-cube bu oturumda %86,3 → %93,2 çıktı; dondurulmuş
kayıtlar o 7 puanın tamamını geri alırdı.

**Ne kaybedilmedi:** kayıt `few_shot_block`'ta **kalıyor** (`recall` güven filtresi
uygulamıyor — testle kilitli), yani Intent-JSON prompt'unu beslemeye devam ediyor ama
**her seferinde `parse_cube_query` ile yeniden doğrulanarak**. İnsan onayı yolu açık:
`/ask/verify` kaydı `user_verified`'a terfi ettirir → replay'e girer. **Kaybedilen "hızlı
öğrenme" değil, "denetimsiz kalıcılaştırma".**

> ⚠️ **ÖLÇÜLEMEYEN kısım dürüstçe:** Faz 0'ın istediği *"50'lik örneklem denetimiyle
> ölçülen yanlış-oran"* bu checkout'ta **üretilemedi** (yerel `interaction_log` /
> `verified_query` boş). Karar o örneklem yerine **yukarıdaki yapısal argümana** ve korpus
> ölçümüne dayanıyor. Canlı örneklem `auto_cube` replay'inin bir şey kazandırdığını
> gösterirse karar **yeniden açılmalıdır** — kayıt few-shot'tan çıkarılmadığı için geri
> alma ucuz.

Ölçülen etki: **eval sapmasız**, korpus dört şirkette de **birebir sabit** (%69/%69/%68/%72).
`test_vqr_schema_version_gate` kaynak etiketini **ikinci kez** ilerletti (`auto` →
`auto_cube` → `user_verified`) ve ikisi de aynı sebeple: kullanılan etiket zamanla replay
edilemez hâle geldi.

#### 2b-3 · §1.6-5 KARAR KAPISI: ölçüldü, **AÇILMADI**

Plan: *"dönem-düzeltme sınıfında başarısızlıkların **≥%20'si** `Baglam`'ın ham ifadeyi
saklamamasına bağlanıyorsa `ham_ifade` bu fazın maddesi olur; altındaysa §8'in açık-nokta
kaydı kalır. **Tahminle taahhüt edilmez, ölçümle açılır.**"*

Ölçüldü: 6 senaryonun **5'i geçti**. Tek başarısızlık `cari-daralt` ve kökü `Baglam`
**değil** — ilk adım (`tüm zamanlar borç`) §6.1g'nin netleştirme chip'ine düşüyor
(`borç (cari hesap)` / `borç (mizan)`), yani **doğru davranış**; ikinci adımın çapası hiç
oluşmuyor. → **%0 < %20 → kapı AÇILMIYOR.** `ham_ifade` §8'in dürüst açık-nokta kaydı
olarak kalıyor.

> **Ölçüm aracının KENDİ hatası bu turda bulundu.** `_daraldi` kontrolü **beklenen**
> cube'un zaman boyutunu sabitliyordu; `route()` soruyu başka bir cube'a çözünce
> (`elektrik` → `surdurulebilirlik`, bilinen açık sahiplik kararı) **çalışan** bir
> düzeltmeyi "başarısız" sayıyordu. MIMARI §6.4'ün dersi bir kez daha: *"ölçüm aracının
> kendisi de bir bağımlılıktır."* Düzeltildi; sınıf **4/6 → 5/6**.

16 test: `tests/test_terfi_kuyrugu.py`.

### 6.5z FAZ 0.5 — KONUŞMA SENARYOSU DOĞRULAMA: süit ilk koşumunda İKİ SINIFI KIRIK buldu ✅

`lab/konusma_senaryolari.py` — senaryolar **kataloğa göre üretilir**, elle yazılmaz.
`nl_corpus.py`'ye eklenmedi: o **günlük regresyon kilididir** ve `nl_corpus_baseline.json`
ona bağlıdır; yeni sınıfları oraya karıştırmak KURAL A'nın yasakladığı taban kirlenmesi
olurdu. Aynı harness kalıbı **çağrılır**, kopyalanmaz.

**Sınır kuralı (planın ⟳ eklemesi) uygulandı:** vaka raporu **senaryo SINIFI** başına
(tur başına DEĞİL — `gen_processes` 10.865 tur üretiyor, birebir uygulamak binlerce `.md`
doğurur ve *"her vaka görünür olsun"* amacının **tam tersi** olurdu). Her sınıf raporu
**temsilci turun tam adımlarını** taşır ve temsilci **ilk BAŞARISIZ** vakadır (öğretici
olan odur). `--live` sınıf başına katmanlı örneklem koşar, **sıralı ve hız-sınırlı**
(`LIVE_BEKLE`), ve **düşürülen tur sayısını raporlar** — sessiz kırpma yok.

**ERİŞİM ve DOĞRULUK ayrı sütun** (§4.7-6): *"cevap geldi mi"* yeterli değil. Bu ayrım
zorunlu, çünkü bir düzeltmenin *çalıştığı* görünmesi DOĞRU şeyi düzelttiği anlamına
gelmez — 2a-1'de (`elektrik`) tam olarak bu oldu.

#### İlk koşum iki sınıfı TAMAMEN kırık buldu — ikisi de aynı kusur ailesi

Her ikisinde de `route()` bir boşluk bırakıyor ve boşluğu başka bir mekanizma
**kendinden emin ve yanlış** dolduruyor.

**Bulgu 1 — `coklu_ay_trendli` 0/6.** *"ocak şubat mart arıza sayısı **değişim** trendi"*
→ kapsam kapısı `değişim`i tanımıyor → `route()` `None` → `typo_correct` boşluğu
dolduruyor: ***"'değişim' yerine 'KISIM' mi demek istedin?"***. `trend` dolgu
sözlüğündeydi ama **kardeşleri yoktu**: `değişim · değişme · artış · azalış · gelişim ·
seyir · yükseliş · düşüş` — hepsi bir ölçünün zamandaki hareketini anlatan **anlatı
kelimeleri**. Bu, §6.1h'nin (`sapma yüzdesi → kar yüzdesi`) aynı sınıfı: **öneri bir
semptom**, kök neden sözlük boşluğu.
**`fark` BİLEREK EKLENMEDİ** — her aday katalogda tarandı ve `fark`
`enerji_sapma.toplam_enpg`'nin **gerçek ölçü sinonimi** çıktı; dolgu saymak onu
gölgelerdi, yani §6.1f'te ölçümle reddedilen hatanın tekrarı olurdu.

**Bulgu 2 — `gorunum_donusumu` 0/5.** *"pasta grafik"* takibi →
*"Bu takip mesajını önceki raporla ilişkilendiremedim."* **Saf görünüm değişikliği TÜM
RAPORU siliyordu.** Plan §4.7-1(e)(i) bunu *"`deterministic_refine`'ın saf görünüm
değişikliğini 'değişti' sayıp saymadığı **ÖLÇÜLMEDİ**"* diye işaretlemişti — ölçüldü:
**saymıyor.** Bu aynı zamanda **plan** §4.4'ün Faz 5 şartının doğrudan ihlaliydi (*"konuşma-modu
metni SİLMEZ, yalnız ÜSTÜNE biner"*). Düzeltme `deterministic_refine`'ın kendi `already`
(no-op) sözleşmesinin aynısı: rapor **aynen** yeniden verilir, yalnız `view_hint` değişir.
Kapı **dar**: görünüm kelimeleri söküldükten sonra geriye anlamlı kelime kalıyorsa
(*"vardiya bazında pasta grafik"*) istek **yapısaldır** ve normal zincire gider.

| sınıf | önce | sonra |
|---|---|---|
| `coklu_ay_trendli` | erişim **0/6** | **5/6** |
| `gorunum_donusumu` | erişim **0/5** | **4/5** |

**Korpus da gördü** (bu iki düzeltme `nl_corpus`'ta ölçülebilir): erişim boyahane
%68→**%69** · atiksan %68→**%69** · gulteks %67→**%68** · gitas %71→**%72**;
doğru-cube dört şirkette de **sabit** (yanlış-cube üretmedi).

**Kalan envanter — bir sonraki turun girdisi (kapatılmadı, gizlenmedi):**
`konu_degisimi` **2/5** · `netlestirme_cevabi` erişim **0/1** · `donem_duzeltme`,
`coklu_ay_trendsiz`, `liste_niyeti`, `ayrik_ay` sınıflarında **1'er vaka** başarısız.
Bunlar Faz 8'in (döngüsel kapanış) ve Faz 2b'nin girdisidir.

**§1.7 VQR-kalıcılık senaryosu koştu:** parafraz `source="vqr"` ile **gelmedi** — yani
o vakada replay tetiklenmedi. Bu **bir kez** ölçümdür, riski çürütmez (embedder kapalı,
`DIMA_VQR_EMBEDDER=off`); Faz 2b'nin kararı `--live` + embedder açık koşumu bekler.

> ⟳ **FAZ 9.6 — YUKARIDAKİ TEŞHİS EKSİKTİ ve senaryo ✅ RAPORLUYORDU.** *"Embedder kapalı"*
> tek sebep değildi; senaryo **yapısal olarak** replay üretemiyordu:
>
> 1. **Koşum** her 2. adıma önceki `cube_query`'yi iliştiriyordu → `ask.py` takip
>    sorularında `near_exact`'i **tümden atlar**. Yani senaryo, ölçmek için var olduğu
>    yolu **hiç çalıştırmadan** *"replay YOK"* diyordu. → `bagimsiz=True` eklendi.
> 2. `ask.py` `learn=(intent_source == "cube+llm")` — **saf `cube` yolu VQR'a hiç yazmaz**
>    (Faz 2b-2'nin ölçülmüş kararı). Embedder açılsa bile **yazan kimse yok**.
>
> Yani LLM'siz modda §1.7 riski **doğamaz** ve *"risk yok"* çıkarımı dayanaksızdır. Araç
> artık **üçüncü bir durum** taşıyor: `⊘ ÖLÇÜLEMEDİ` (ne geçti ne kaldı). Yeşile
> yuvarlamak *"risk yok"* yalanı, kırmızıya yuvarlamak sahte alarm üretirdi.
>
> **FAZ 9.7 — aynı dosyada iki kalıntı daha.** `_cube_dogru` **hiçbir yerden
> çağrılmıyordu**: rapor başlığı *"DOĞRULUK (doğru **cube**/dönem/yapı)"* diyordu ama
> dokuz sınıftan yalnız `konu_degisimi` cevabın cube'una bakıyordu — araç, görünür kılmak
> için var olduğu **sessiz-yanlış** sınıfına karşı kördü. `_ve_cube` sarmalıyla altı sınıfa
> bağlandı. `_bitisik` ise beklenen cube'un zaman boyutunu **sabitliyordu** — `_daraldi`'da
> düzeltilen hatanın aynı dosyadaki ikinci kopyası; artık dönem filtresi **cevabın** cube'una
> göre aranıyor. 13 test: `tests/test_senaryo_araci_durustlugu.py`.

17 test: `tests/test_faz05_bulgulari.py`.

### 6.4z FAZ 3a — ŞEMA-KISITLI ÇIKTI: hatayı sonrasında reddetmek yerine öncesinde engelle ✅ (kazanç ÖLÇÜLDÜ: YOK; mekanizma YAPISAL gerekçeyle kalıyor)

Bugünkü Intent-JSON akışı: *"serbest JSON iste, sonra `parse_cube_query` ile **REDDET**"*.
Reddedilen her sorgu bir **Discovery'ye düşüştür** — yani kayıp, hatanın **sonrasında**
kapatılıyor. Şema-kısıtlı çıktı hatayı **öncesinde** engellemeyi hedefler: cube/ölçü/boyut
adları o anki kataloğun **enum**'u olarak sağlayıcının **native tool-use** şemasına
gömülür (`cube_router.cube_query_json_schema`).

**İki tasarım kararı — ikisi de kısıtın işe yaraması için zorunlu:**

1. **Enum CUBE'A GÖRE daralır (`oneOf`).** Düz bir `{"measures": {"enum": [tüm 81 ölçü]}}`
   **çapraz sızıntı** üretirdi: model `parti` seçip `oee`'nin ölçüsünü isteyebilirdi —
   yapısal olarak "geçerli", semantik olarak saçma, `parse_cube_query` yine reddederdi.
   Yani kısıt **hiçbir işe yaramazdı**. Her cube kendi dalını taşır.
2. **`cube:null` REDDETME DALI KORUNUR — en önemli madde.** Şema-kısıtlı çıktının klasik
   tuzağı modeli **geçerli ama yanlış** bir seçime ZORLAMAKtır: seçenekler arasında
   "hiçbiri" yoksa model illa birini seçer. Bu, sistemin en pahalı hata sınıfını (§6.1
   sessiz-yanlış) **üretirdi** — yani kısıt, düzeltmeye çalıştığı şeyi büyütürdü. Dal
   listenin **başında** (sıra modele bir sinyaldir).

**Kapsam yalnız beş çekirdek alan.** `order`/`limit`/`blend` bilerek dışarıda —
`parse_cube_query` onları zaten **hoşgörüyle sessizce düşürüyor**, enum'lamak kazanç
getirmez, yalnız şemayı büyütür.

**Sağlayıcı gerçeği dürüstçe:** Anthropic `input_schema` + `tool_choice` ile taşınıyor.
OpenAI-uyumlu uçlarda şema **kabul ediliyor ama KULLANILMIYOR** — `strict` fonksiyon
şeması `oneOf`'u desteklemiyor ve **kısıtı yarım uygulamak, uygulamamaktan kötüdür**
(model geçerli ama yanlış bir dala zorlanabilirdi). İmza uyumlu kalıyor ki
`FailoverSqlGenerator` ayrım yapmasın; şemayı kabul etmeyen eski üreteçlere `TypeError`
üzerinden iki-argümanlı çağrıyla düşülüyor. Tool-use yolu herhangi bir nedenle patlarsa
**bugünkü serbest-JSON yoluna düşülüyor** — ikisi de aynı `parse_cube_query`'ye varır,
yani yedek yol zaten doğrulanmış.

**Şema her istekte kataloğun O ANKİ hâlinden üretilir** — bayat bir enum, olmayan
enum'dan kötüdür: modele var olmayan bir adı **dayatırdı**.

> ⚠️ **KABUL KAPISI KARŞILANMADI ve karşılanmış gibi gösterilmiyor.** Planın §6 ölçütü
> *"whitelist reddi oranı ölçülüp DÜŞÜŞÜ doğrulanır"*. Bu ortamda **gerçek bir LLM
> sağlayıcı yok** (`RuleBasedSqlGenerator`), dolayısıyla oran ölçülemez. Kilitlenen şey
> **mekanizmanın kendisi**: şemanın doğruluğu (üretilen her dal `parse_cube_query`'den
> GEÇİYOR — ikisi ayrışsa model şemaya uyar ama sistem yine reddederdi), yedek yolun
> çalışması, bayrağın kapatabilmesi. **Yeni:** whitelist reddi artık **loglanıyor**
> (eskiden SESSİZDİ — LLM cevap üretti, `parse_cube_query` düşürdü, geriye iz kalmadı);
> ölçülemeyen bir kazanç doğrulanamaz. Oranın önce/sonra kıyası **Faz 0.5'in `--live`
> modunun** işidir ve o faza girdi olarak taşınmıştır.

19 test: `tests/test_sema_kisitli.py` · bayrak `llm_sema_kisitli` (KURAL B).

> ⟳ **KAZANÇ ÖLÇÜLDÜ (3 Ağustos 2026, gerçek Gemini) — VE KAZANÇ YOK.**
>
> Faz 3a'nın kabul kapısı (*"whitelist reddi oranı ölçülüp **düşüşü** doğrulanır"*)
> landing anında karşılanamamıştı: o ortamda gerçek sağlayıcı yoktu. Kapatıldı.
>
> **Önce kapının kendisi yanlış tanımlanmıştı.** *"Red oranı düşmeli"* iki farklı olayı
> tek kefeye koyuyor: **dürüst red** (`cube:null` — *"bunların hiçbiri"*, Faz 3a'nın
> KENDİ tasarım kararı, düşürmek ZARARDIR) ve **geçersiz alan** (mekanizmanın hedefi).
> Doğru ölçüt: *"geçersiz alan üretimi düşmeli, dürüst red düşmemeli."*
>
> | koşum | yapılandırma | toplam red | dürüst | **GEÇERSİZ** | doğru cube |
> |---|---|---|---|---|---|
> | 8 soru | şemasız | 3 | 3 | **0** | 5/8 |
> | 8 soru | şema-kısıtlı | 2 | 2 | **0** | 4/8 |
> | 16 soru | şemasız | 6 | 6 | **0** | 6/16 |
> | 16 soru | şema-kısıtlı | 6 | 6 | **0** | 6/16 |
>
> **Şemasız yol, bugünkü prompt'uyla, ölçülen 24 soruda hiç geçersiz alan üretmedi** —
> kısıtın kaldıracağı bir şey yoktu. Faz 7 (üç sıçrama, üçü de benimsenmedi) ve 2a-1
> (`elektrik`) ile aynı disiplin: **kazanç yoksa yazılır.**
>
> **Mekanizma KALIYOR, gerekçesi ölçüm değil YAPI:** kısıtlı yolda geçersiz ad üretmek
> *"24 soruda görülmedi"* değil **imkânsızdır**. Bu, 9.3'ün kararının aynısı — *"bir
> ÖLÇÜM, yapısal garanti değildir."* Maliyeti ölçüldü: **sıfır** (red bileşimi ve
> doğru-cube iki koşumda da eşit).
>
> ⚠️ **İlk ölçümüm yanlıştı ve inandırıcıydı** (bu turda **dokuzuncu**; §6.4). Teşhis
> için reddedilen çıktıyı sınıflandırmak yerine **LLM'i yeniden çağırıyordum** — yani
> başka bir üretimi ölçüyordum ve *"3 geçersiz → 0"* diye bir kazanç raporlayacaktım.
> Araç artık sınıflamayı **aynı ham çıktı üzerinde, aynı döngüde** yapıyor; tekrar
> koşumu farkı ortaya çıkardı. Ölçüm aracı sürüm kontrolünde:
> `lab/faz3a_sema_kazanci.py`.

### 6.1j R2 (liste/döküm) — dalın YARISI haklıydı, yarısı kapsam kaybıydı (Faz 2a) ✅

`route()`'un R2 dalı koşulsuz `None` dönüyordu: *"liste/döküm istekleri cube'a uymaz →
LLM/kural"*. Plan bunu *"sıfır maliyetli kapsam kaldıracı"* diye işaretlemişti. Ölçüldü —
iddia **doğru çıktı ama bir tuzak da gösterdi.** 11 gerçekçi vaka; R2 **9'unu** kesiyordu.
Liste kelimesi sökülünce:

| soru | R2 kesince | kelime sökülünce |
|---|---|---|
| `müşteri bazında ciro listele` | cevap YOK | `parti/toplam_ciro dims=[musteri]` ✓ |
| `en çok ciro yapan 10 müşteriyi listele` | cevap YOK | `dims=[musteri]` **+ `limit=10`** ✓ |
| `makine bazında oee detay` | cevap YOK | `oee/ort_oee dims=[makine]` ✓ |
| `renk bazında fire dökümü` | cevap YOK | `parti/toplam_fire_kg dims=[renk]` ✓ |
| **`bu yıl ciro dökümü`** | cevap YOK | `dims=None` → **DEJENERE TOPLAM** ⚠ |
| **`bu ay ciro detaylı göster`** | cevap YOK | `dims=None` → **DEJENERE TOPLAM** ⚠ |

Yani cube kırılımı **üretebildiğinde** cevap tam ve doğru; **üretemediğinde** döküm isteyen
kullanıcıya **tek bir sayı** dönerdi — `source=cube` rozetiyle, yani §6.1'in *"en tehlikeli
sınıf"* tanımı. **R2'yi tümden kaldırmak bu ikinci sınıfı açardı** ve plan bunu görmüyordu.

**Kural:** liste niyeti YALNIZ gerçek bir kırılım eşleştiğinde onurlandırılır; yoksa R2
aynen kalır. Bu yeni bir ilke değil — `route()`'un `_BREAKDOWN_HINTS` için zaten uyguladığı
sessiz-yanlış korumasının buraya da uygulanması.

**Üç yan kapı, üçü de sessizce kırardı:**

1. **Kapsam kapısı.** R2 geçtikten sonra `listele`/`dökümü` kelimeleri `_uncovered`'a
   düşüp **R10** verirdi — niyet "anlaşıldı" sayılıp cevap yine kaybolurdu. Kelimeler
   **aynı `_LISTE_RE`'den** okunup dolgu sayılıyor (iki taraf ayrışamaz, testli).
2. **Red gerekçesi doğrulaşıyor.** *"müşterileri listele"* (kırılım var, ölçü yok) artık
   R2 değil **R4** veriyor — Faz 0'ın telemetrisinde doğru kümeye düşsün diye.
3. **`dokuma` tuzağı korunuyor.** `dokum` altdizisi "DOKUMa"yı (kumaş!) yakalıyordu;
   kelime sınırı yerinde, `dokuma kumaş cirosu` etkilenmiyor.

**Görünüm niyeti — R2'nin doğal UX sonucu.** *"listele"* diyen kullanıcı **satırları**
görmek ister; deterministik grafik kararı o sonuca `bar` diyor ve teknik olarak haklı, ama
kullanıcının **açıkça söylediği** şey bu değil. `view_hint` zaten bu iş için var
(*"grafik ver"*in tersi yönü) — simetriği kuruldu: liste niyeti → `view_hint="table"`.
**ADR-0024 ihlal EDİLMİYOR**: `viz` kararı deterministik kalıyor, `view_hint` yalnız açık
isteği taşıyor ve `_VIZ_MAP`'ten SONRA bakılıyor (*"dökümü pasta grafik yap"* → pasta
kazanır). Frontend tarafında **yeni tüketici gerekmedi** — `ResultView` `view_hint ===
"table"`'ı zaten onurlandırıyordu; eksik olan sinyalin kendisiydi.

**KURAL B:** `route(q, schema, *, liste_kirilimi=False)` — **anahtar-kelime** argümanı,
varsayılanı kapalı. `cube_router` istek/principal görmez, bayrağı çağıran çözer.
`ask.py`'deki **dört** `route()` çağrısının hepsine geçiriliyor (Faz -1'in *"üç çağrı
yeri"* dersi: biri atlanırsa aynı soru geldiği yola göre farklı davranır).

`tests/test_red_gerekcesi.py::test_IMZA_DEGISMEDI` **keskinleştirildi, gevşetilmedi**:
eskiden `list(sig.parameters) == ["question","schema"]` diyordu; korunmak istenen şey
**çağıranların kırılmaması**, o yüzden artık *konumsal imza aynen* + *eklenen her parametre
KEYWORD_ONLY ve varsayılanlı* olduğu kilitleniyor.

**Ölçüm dürüstlüğü:** `lab/nl_corpus.py`'nin sorgu şablonlarında **liste niyeti YOK**
(tarandı: yalnız iki meta-soruda "detay" geçiyor) — korpus bu kazancı **göremez**, tıpkı
§6.1b/§6.1i gibi. Gösterdiği tek şey **gerileme olmadığıdır** (dört şirket de birebir
sabit: %68/%68/%67/%71). Kazanç 22 birim testiyle kanıtlanıyor:
`tests/test_liste_niyeti.py`.

### 6.2z FAZ 1 (K1) — Discovery uçurumu kapandı: ad-hoc cube, ama YAPI ≠ GÜVEN ✅

`seal()` üç kapısını da **tek bir alana** bakarak açıyordu: `resp.cube_query`. Discovery
cevabı onu hiç set etmiyordu → chip · kırılım · zaman granülerliği · aksiyon önerisi ·
köken · drill · katkı · doğru grafik · rapor · pano · zamanlama · **frontend butonları**
hepsi birden kapanıyordu. Bu bir hata değil, **tasarlanmış bir uçurumdu**.

**Çözüm:** Discovery'nin **sonucundan** oturum-scoped bir cube türetilir
(`app/adhoc_cube.py`). Excel yüklemesi için yazılmış hat (`dataset._role` /
`build_mdl` / `build_service`) **çağrılır, kopyalanmaz**.

> ⟳ **FAZ 9.9 — "hepsi birden açıldı" İDDİASI YARIM KARŞILIKSIZDI (denetimde bulundu).**
> Ad-hoc cube **tenant kataloğunda yoktur**; onu bulmak için `_adhoc_kayit`'tan geçmek
> gerekir. Bu YALNIZ `_attach_next_steps`'e öğretilmişti. İki kardeş tüketici cube'u hâlâ
> tenant kataloğunda arıyordu:
>
> | tüketici | ne arıyordu | sonuç |
> |---|---|---|
> | `_attach_next_steps` | ad-hoc kaydı | ✅ çalışıyordu |
> | `_attach_recommendations` (`answer.py`) | tenant kataloğu | `spec=None` → **aksiyon önerisi YOK** |
> | `_attach_viz` (`ask.py`) | tenant kataloğu | `cube_meta=None` → **birim/köken/grafik YOK** |
>
> Yani kapı yeşildi ve **hiçbir şey açmıyordu**: aynı kural bir tüketiciye öğretilmiş,
> iki kardeşine öğretilmemişti — bu belgenin kendi *"kimlik asimetrisi"* sınıfı (§6.1h),
> bu turda dördüncü kez. Üçü de artık ad-hoc kaydını okuyor ve **dördüncü bir tüketici
> eklendiğinde aynı soruyu soran bir kapı** kondu
> (`tests/test_adhoc_cube.py::test_UC_TUKETICININ_hepsi_adhoc_kaydini_okuyor`).

**K1'in tek eksiği ölçüldü ve kapatıldı:** `wren_service.query()` Arrow **şemasını
atıyordu** — yalnız kolon *adları* dönüyordu. Tipsiz bir sonuçtan ölçü/boyut/zaman ayrımı
yapılamaz. Artık `column_types` taşınıyor (geriye uyumlu ek alan). Tip **gelmezse** cube
kurulmaz: her kolon VARCHAR olurdu → ölçüsüz cube → yapı rozeti takılmış ama içi boş bir
cevap. **Tahmin etmektense yapı vaat etmemek doğrudur.**

#### YAPI ≠ GÜVEN — bu fazın en önemli cümlesi

`source` **`llm:<sağlayıcı>` KALIR**, `explain.confidence` **`None` KALIR** (MIMARI §5).
Bu yapısal olarak garantili: `_build_explain` güveni `source`'tan okur, `cube_query`'nin
varlığından **değil**. `cube_query` `adhoc: true` + `provenance: "llm_sql'den türetildi"`
taşır ve frontend `⚡ GEÇİCİ MODEL` rozetiyle gösterir — kullanıcı `◆ CUBE` görmez.

**Kesin sınır dürüstçe:** ad-hoc cube **SQL'in seçmediği bir boyutu ekleyemez**. "Tam
kırılım" değil, **dondurulmuş görünüm üzerinde tam etkileşim**. B'yi A'nın yerine koymaz.

#### Dört risk — hepsi kapı, hiçbiri beyan

| risk | kapı |
|---|---|
| **Dondurulmuşluk** | Satırlar oturum `.duckdb`'sine materyalize edilir; sonraki chip/drill sorguları kaynak DB'ye **geri gitmez** (bu yüzden `always_filter` endişesi yok). Tasarımın tamamı buna dayanıyordu ve **hiçbir yerde yazılı değildi** — artık testle ölçülüyor. |
| **Kırpılmış görünüm** | `row_count >= limit` → `kirpilmis=true`. O görünüm üzerindeki **her** toplama (ölçü/kırılım/zaman kovası) eksik veriden hesaplanır → chip'lerin **tamamı** kapatılır, drill reddedilir, ve kullanıcı **sebebini görür**. Sessizce eksik chip, chipsizlikten kötüdür. |
| **Maskeleme sırası** | Cube **maskeli** satırlardan kurulur — aksi halde oturum `.duckdb` dosyası diskte **maskesiz PII** taşırdı. Bedeli: `Ahm** Y***` değerine kırılım kuran chip anlamsız döner → maskelenen kolonlarda chip **üretilmez** (`schedules.uyari_nedeni`'ndeki aynı karar). |
| **Kill-switch** | `adhoc_cube` bayrağı (KURAL B); kapalıyken davranış **bugünküyle birebir**, testle kilitli. |

#### İki entegrasyon tuzağı — ikisi de sessizce kırardı

1. **Ad-hoc servis AYRI depoda** (`app.state.adhoc_cubes`), `_dataset_store`'da **değil**.
   Oraya yazılsaydı (a) yüklenmiş bir Excel ezilirdi, (b) `_service_for` o oturumdaki
   **sonraki normal soruları da** ad-hoc tabloya yönlendirirdi — yani bir Discovery cevabı
   tenant'ın gerçek kataloğunu oturum boyunca **gölgelerdi**.
2. **`parse_cube_query` işaretleri korur.** Whitelist `adhoc_id`/`kirpilmis`/`provenance`'ı
   düşürseydi: `adhoc_id` kaybolur → **ikinci** chip tıklaması servisi bulamaz, zincir
   **tek adımda** kopardı; `kirpilmis` kaybolur → kırpılmış görünümde toplama chip'i geri
   gelirdi, yani 2. risk maddesi **sessizce açılırdı**.

**Ölçülen:** `next_steps` Discovery cevabında **0 → kırılım chip'leri** (kırpılmamış
görünümde, gerçek `build_mdl` şemasından) · `explain.confidence` **None** kaldı · eval
`deterministik pay` **+0.0%** · 16 test `tests/test_adhoc_cube.py`.

### 6.1i AYRIK aylar cevaplanıyor — motor ifade edemiyordu, DIŞ SARMA ile çözüldü (Faz 2a) ✅

§6.1b (-0.5a) **bitişik** ayları tek aralığa çevirmişti; **ayrık** aylar (*"ocak ve mart"*)
dürüstçe netleştirmeye düşüyordu. Plan bunu bir kapsam kalemi yaptı ve **ön koşul** koydu:
*"`cube_query_to_sql`'in bu operatörü desteklediği ÖNCE doğrulanmalı."*

**Ön koşul ölçüldü ve KARŞILANMADI:**

| deneme | sonuç |
|---|---|
| `{"operator": "in", "value": ["2026-01","2026-03"]}` | derleniyor **ama** `WHERE tarih IN (...)` — **HAM** kolona, yani yalnız o iki *gün* |
| çoklu `dateRange` | `invalid type: sequence, expected a string` |
| `tarih__month` boyutuna filtre | `Unknown filter dimension` |
| `or` bloğu | `missing field 'dimension'` |

`in` operatörünün **var olması yanıltıcıydı**: kabul ediliyor ama ay KOVASINA değil ham
tarihe uygulanıyor. Motor ayrık ayı yerel olarak ifade **edemiyor**.

**Seçilen yol:** ay granülerliğinde **grupla** → kesilmiş kolona **dışarıdan** filtrele.
Toplama gruplamadan ÖNCE bittiği için sonuç matematiksel olarak **kesindir** — bu,
`cube_sql`'in `measure_having` için zaten kullandığı sarma kalıbının aynısı.

```sql
SELECT * FROM (SELECT DATE_TRUNC('month', tarih) AS tarih__month, SUM(ciro_tl) …
               WHERE tarih >= '2026-01-01' AND tarih <= '2026-03-31' GROUP BY 1) AS _ay
WHERE tarih__month IN (DATE '2026-01-01', DATE '2026-03-01')
```

Gerçek veriyle doğrulandı: sarmalı sorgunun Ocak/Mart değerleri aylık tabanla **birebir**.

**FAIL-CLOSED — bu tasarımın omurgası.** İşaret (`cube_query["ayrik_aylar"]`) ile kapsayan
aralık **birlikte** anlamlıdır; işaret düşer de aralık kalırsa cevap **Şubat'ı da içerir**
ve `source=cube` rozetiyle gelir. Dört kapı kuruldu:

1. `cube_sql`: işaret var + ay granülerliği yok → **`ValueError`**. Derlenmeyen sorgu,
   sessizce yanlış sorgudan iyidir.
2. `blend_sql`: CTE'leri açık alanlardan yeniden kurar ve işareti **kopyalamaz** → reddeder.
3. `deterministic_refine`: `prev`'i deep-copy eder, işaret takibe **taşınır**. Dönem ya da
   granülerlik değiştiyse üç ayrı sessiz-yanlış doğar (*"tüm zamanlar"* → sarma hâlâ
   daraltır · *"geçen ay"* → boş sonuç · *"yıllık"* → derleme hatası) → **`None`**, zincir
   dürüst yola düşer.
4. **Frontend** (`InterpretationBar`): dönem chip'i filtrelerden türetiliyordu ve
   *"1 Oca – 31 Mar"* yazıyordu — **kullanıcıya yalan**. Artık işaret **önce** okunuyor:
   *"Ocak · Mart 2026"*. Dönem düzenlemesi (`setPeriod` / dönem ×) işareti **birlikte
   düşürüyor**; taşınsa yeni dönemle sessizce kesişir ve çoğu zaman boş sonuç verirdi.

**Ayrık-ay yolu bir YEDEKTİR, üst-katman değil.** Ölçülen gerileme (eval precision
**−0,9%**): *"1 ocak 31 mart arası"* iki ay ADI taşır ve saf ay-taraması onu "ayrık"
sanıyordu — oysa `_explicit_range_filters` onu zaten sürekli aralık olarak çözmüştü.
Kural: yalnız **başka hiçbir dönem çözülemediğinde** çalışır.

**Yan bulgu — düzeltme kendi içinden bir sessiz-yanlış çıkardı.** Yıl tek bir `re.search`
ile bulunup **tüm aylara** uygulanıyordu: *"2025 ocak ve 2026 mart"* → `[2025-01, 2025-03]`.
Ayrık aylar netleştirmeye düştüğü sürece zararsızdı; onları **cevaplanabilir** yapmak aynı
hatayı **kendinden emin yanlış bir sayıya** çevirirdi. Yıl artık her ay adının **kendi
komşuluğundan** okunuyor (önce/sonra), yoksa sorudaki tek yıla, o da yoksa "geçmişteki en
yakın" kuralına düşülür.

**Ölçüm dürüstlüğü:** korpusta çoklu-ay sorusu **yok**, yani kazanç oradan görülemez
(§6.1b'nin aynı kaydı) — gösterdiği tek şey **gerileme olmadığıdır**. Kazanç 20 birim
testiyle kanıtlanıyor: `tests/test_ayrik_ay.py` (SQL'in gerçekten yalnız o ayları
döndürdüğü, gerçek satır kıyasıyla).

### 6.1h Kimlik asimetrisi KAPANDI — kural bir dalda vardı, kardeşinde yoktu (Faz 2a) ✅

Bu deponun en sık tekrarlayan kusur sınıfının (*"beyan var, kod onu tanımıyor"*) en pahalı
örneği: kural **yazılmış, yorumlanmış, test edilmiş** — ama **yalnız bir dalda** koşuyordu.

`_match_cube` iki dal taşıyor. Çok-aday dalı (`len(hits) > 1`) **ölçü-kanıtı** uyguluyor ve
kendi yorumu neden var olduğunu anlatıyor: *"Cube-düzeyi kelime uzunluğu yanıltıcıydı:
jenerik cube-sinonimi ('satış'/'miktar') spesifik ölçüyü **gölgeliyordu**."* Tek-aday dalı
(`len(hits) == 1`) ise **koşulsuz `return`** ediyordu — yani aynı gölgeleme, kardeş dalda
hiç kontrol edilmeden yaşıyordu.

**Ölçülen zincir:**

```
"sapma yüzdesi"  →  `parti` kimliğinde ÇIPLAK "sapma" var          → hits=[parti]
                 →  tek aday, KOŞULSUZ dönülüyor
                 →  parti'de "yuzdesi" açıklanamıyor                → R10, cevap YOK
     oysa `enerji_sapma.sapma_yuzde`'nin sinonimi BİREBİR "sapma yuzdesi"
```

Sistem **doğru cevabı elinde tutup atıyordu**; boşluğu `typo_correct` dolduruyordu:
*"sapma yüzdesi → **kar yüzdesi** mi demek istediniz?"* — başka cube, başka ölçü, doğru
cevabın üstüne kendinden emin bir yönlendirme. Planın §2.1'i bunu *"bulanık eşleştirici
yanlış düzeltme öneriyor"* diye kaydetmişti; **öneri bir semptomdu**, kök neden bu asimetri.

**Kural (yeni değil — çok-aday dalındaki kuralın AYNISI):** kısa eşleşme uzun eşleşmenin
**alt-dizisiyse** en spesifik kazanır. Üç şart zorunlu:
* **alt-dizi** — iki AYRI ifade (*"verim VE fire oranı"*) çapraz-cube'dur, kırılmaz;
* rakip sinonim soruda **gerçekten geçiyor** (`_syn_hit`) — rakip, kullanıcının yazdığı
  kelimelerin **kesin olarak daha fazlasını** açıklıyor demektir;
* rakip **tek** — iki rakip de daha spesifikse bu bir tahmin anı değil belirsizliktir
  (ADR-0008), bugünkü davranış korunur.

**Bu, §6.1f'te ölçümle REDDEDİLEN düzeltmenin doğru biçimidir.** Orada `surdurulebilirlik`
kimliğinden ham kaynak adları **silinerek** sahiplik çözülmeye çalışıldı ve erişim
%64→%56'ya düştü. Silmek sahipliği çözmüyordu; **spesifiklik çözüyor**: kimlik yerinde
kalıyor, ama `"elektrik tuketimi"` (16) `"elektrik"`i (8) yeniyor.

**Ölçülen sonuç — dört şirketin DÖRDÜNDE de kazanç, sıfır gerileme:**

| şirket | erişim | doğru-cube |
|---|---|---|
| boyahane | %64 → **%68** | %89 → **%92** (Discovery 101 → **35**) |
| atiksan | %67 → **%68** | %98 → %98 |
| gulteks | %62 → **%67** | %95 → %95 |
| gitas | %67 → **%71** | %88 → **%89** |
| **toplam doğru-cube** | | **%91,4 → %93,2** |

Sinonim envanteri (470 ölçü sinonimi × `route()`): doğru **291 → 340** · yanlış-cube
**30 → 23** · cevapsız **149 → 107** (R10 32→5, R4 14→1, R5 2→0) · **yeni yanlış: 0**.

**Planın *"erişim %64 → artmalı"* kapısı İLK KEZ karşılandı.** Önceki iki tur (2a-1, 2a-2)
erişimi sabit bırakmıştı; kayıp cevapsız sınıfındaydı ve bu düzeltme onu açtı.

**R1 = 99 DEĞİŞMEDİ ve değişmemeli.** Onlar çıplak bir ölçü adının iki cube'da birden
iddia edildiği **gerçek** belirsizliklerdir (`bakiye`, `borç`, `fire`); daha uzun bir ifade
yok, spesifiklikle kırılamaz. `route()` tahmin etmeyi doğru reddediyor, netleştirme
§6.1g'nin chip'iyle geliyor. Kalan 23 yanlış-cube da aynı sınıf: hepsi **çıplak tek
kelime** (`elektrik · kwh · gaz · tep · fire · uretim · tahsilat`) ve gerçek **alan
kararlarıdır**.

**Yan bulgu — iki test birbiriyle çelişiyordu.** `test_bare_durus_hala_oeeye_gider` adında
*"bare"* derken listesine bare OLMAYAN bir vaka almıştı (*"makine bazında **toplam
duruş**"*). `"toplam durus"` `makine_duruslari.toplam_sure_dk`'nın **kendi** sinonimidir,
kardeş sinonimi `"toplam durus dakikasi"` zaten oraya gidiyordu, ve bir üstteki test aynı
çifti *"en-uzun-eşleşme kuralıyla bu cube kazanır"* diyerek zaten `makine_duruslari` lehine
çözmüştü. Sinonim envanteri de o satırı **yanlış-cube** olarak kaydetmişti. Vaka listesi
düzeltildi, kural değil; **çıplak** "duruş" hâlâ `oee`'ye gidiyor ve testle kilitli.

15 test: `tests/test_spesifik_olcu_sahibi.py`.

### 6.1g Netleştirme SESSİZCE atlanıyordu — belirsizliğin %61'i Discovery'ye düşüyordu (Faz 2a) ✅

§6.1f'in "netleştirme zaten çalışıyor" ara ürünü **eksik ölçülmüş** bir gözlemdi. Chip'in
üretildiği vakaya bakıldığında davranış doğru; üretilmediği vakaya kimse bakmamıştı.

**Ölçülen kusur zinciri — üç adımı da sessiz:**

1. `measure_cube_candidates` belirsizliği **doğru tespit ediyor** (`bakiye` → `cari` +
   `mizan`).
2. Chip'ler yalnız ölçünün **görünen adıyla** kuruluyordu; iki cube aynı adı taşıdığında
   (*"bakiye"* / *"bakiye"*) liste tekilleşip **1'e düşüyor**.
3. `if len(...) >= 2` kapısı chip'i **sessizce atlıyor** → soru **Discovery'ye** düşüyor →
   ham SQL, `cube_query=None`, not yok, chip yok.

Yani **netleştirme yolunun kendisi §6.1'in uçurumuna açılıyordu**: kullanıcı bir soru
yerine yapısız bir cevap alıyordu ve hiçbir sinyal bunu göstermiyordu. Ölçüldü:
**54 belirsiz sinonimin 33'ü (%61)** bu tuzaktaydı — `bakiye · borç · alacak · fire ·
ilk seferde tamam · doğalgaz` aileleri.

**Kural:** ayırt edici bilgi **ölçü adı değil CUBE'un kendisi** → *"bakiye (cari hesap)"* /
*"bakiye (mizan)"*. Çakışmayan etiket **dokunulmaz** — gereksiz niteleme chip'i uzatır ve
seçimi zorlaştırır.

**İkinci kusur, ilk düzeltmenin İÇİNDEN çıktı.** `query = f"{cube_display} {etiket}"`
kullanınca **39 chip çözülmüyordu**: `display` bir **insan etiketidir** — `mizan`'ınki
*"mizan (hesap bakiyeleri)"*, üretilen sorgu *"mizan (hesap bakiyeleri) borç"*. Cube
**sinonimleri** ise tanım gereği `_match_cube`'un **tanıdığı** kelimelerdir. Sorgu artık
`route()` ile **doğrulanıyor** (`_calisan_sorgu`): çıplak etiket çalışıyorsa ona
dokunulmaz, yoksa cube sinonimleri (kısa ad önce) denenir. Tıklanınca çalışmayan bir chip
kullanıcıyı aynı duvara ikinci kez çarptırır ve **chip olmamasından kötüdür** — aynı kural
`ay_netlestirme`'de de uygulanmıştı (§6.1b).

**Ölçülen sonuç (korpus, 10.865 tur):**

| ölçüt | önce | sonra | planın kapısı |
|---|---|---|---|
| sessiz kalan belirsizlik | 33 | **0** | — |
| kırık chip sorgusu | 39 | **0** | — |
| boyahane Discovery'ye düşen | 501 | **101** | — |
| boyahane doğru-cube | %80 | **%89** | — |
| **toplam doğru-cube** | **%86,3** | **%91,4** | *"%86,3'ün altına düşmemeli"* ✓ |
| boyahane erişim | %64 | %64 | *"artmalı"* — sabit |

**400 tur** ham-SQL cevabı yerine **cevaplanabilir bir soru** alıyor. Erişim payının
sabit kalması beklenen sonuçtur: bu turlar zaten "cevap üretildi" sayılmıyordu, Discovery'ye
düşüyorlardı — düzeltme *cevapsızı cevaba* değil, *sessiz düşüşü görünür soruya* çeviriyor.

12 test: `tests/test_olcu_netlestirme.py` (uçtan uca chip **tıklama** dahil — chip'in
`query`'si yeni bir soru olarak koşup yapısal cevap üretiyor mu).

### 6.1f Katalog sağlığı ÖLÇÜLDÜ — kayıp "yanlış cube"da değil (Faz 2a)

Planın §2.1'i boyahanenin kaybını *"üç isimlendirilmiş YAML düzeltmesine indirgeniyor"*
diye çerçeveliyordu ve birincisi `elektrik` çakışmasıydı. O özet `nl_corpus.md`'nin
**10 satırlık ÖRNEĞİNE** dayanıyordu. Doğrudan ölçüldü (470 ölçü sinonimi × `route()`):

| sonuç | adet | pay |
|---|---|---|
| doğru cube | 291 | %62 |
| yanlış cube | **30** | %6 |
| **CEVAPSIZ** | **149** | **%32** |

Cevapsızın red dağılımı — **Faz 0'ın `reject_reason` enstrümanı olmadan görülemezdi**:
**R1: 99** · R10: 32 · R4: 14 · R5: 2 · R9: 2.

**Asıl kayıp yanlış-cube'da değil.** Cevapsız sınıfı beş kat büyük ve en büyük dilimi
**R1** — katalogda **var olan** bir ölçü sinonimi, düz sorulduğunda cube'unu bile
tanıtmıyor. Rapor yalnız yanlış-cube örneği bastığı için bu sınıf hiç görünmemişti.

#### `elektrik` düzeltmesi DENENDİ ve ÖLÇÜMLE REDDEDİLDİ

`surdurulebilirlik`'in cube-düzeyi kimliğinden ham kaynak adları (`elektrik · kwh ·
doğalgaz · gaz · tep · enerji · atıksu`) çıkarıldı. Gerekçe sağlamdı: bu cube **yoğunluk**
ölçer (su/kg, enerji/kg) ve `_match_cube` ölçü eşleştirmesinden önce koştuğu için adanmış
enerji cube'larını her seferinde yeniyordu.

| ölçüt | önce | sonra | planın kapısı |
|---|---|---|---|
| boyahane erişim | %64 | **%56** | *"artmalı"* ❌ |
| doğru-cube | %80 | %79 | *"düşmemeli"* ❌ |
| yanlış cube | 245 | 135 | ✓ |
| Discovery'ye düşen | 501 | **578** | ↑ |
| `test_eval_gate` | yeşil | **KIRMIZI** (coverage −%4,5) | ❌ |

**110 sessiz-yanlış kapandı ama 388 cevap kayboldu** — 3,5:1 kötü takas. Sebep: kimliği
kaldırmak **sahipliği çözmedi**, yalnız zorlamayı kaldırdı. Ölçü düzeyinde
`enerji_makine.toplam_elektrik_kwh` ile `surdurulebilirlik.toplam_enerji_kwh` **ikisi de**
`elektrik` iddia ediyor → `_match_cube` hiçbirini seçemiyor → **R1**.

Değişiklik **geri alındı** ve geri alma bir testle korunuyor (`test_SURDURULEBILIRLIK_
kimligi_KORUNUYOR`) — aynı deneme ikinci kez yapılmasın diye. Doğru çözüm bir **sahiplik
kararıdır** (çıplak "elektrik" hangi cube'un?), kimlik silmek değil; ve bu bir **alan
bilgisi** işidir — planın `ortalama duruş` için *"karar kalemi, sahibi ve tarihi olmalı"*
dediği sınıfın aynısı.

**Ara ürün — netleştirme zaten doğru çalışıyor:** düzeltme uygulandığında `/ask` zinciri
`measure_cube_candidates` üzerinden *"Birden fazla konu anlaşıldı, hangisini istiyorsun?"*
chip'ini üretiyordu. Yani belirsizlik yüzeye çıktığında sistemin davranışı **doğru**;
sorun belirsizliğin **var olması**.

> ⚠️ **Bu ara ürün yarım doğruydu — §6.1g'ye bakın.** Netleştirme *ateşlendiğinde* doğru
> çalışıyor; ama ölçüldü ki belirsiz vakaların **%61'inde hiç ateşlenmiyordu** (etiketler
> çakışınca chip listesi tekilleşip kapının altında kalıyordu). Yani buradaki gözlem,
> chip'in **üretildiği** vakaya bakarak yapılmış bir genellemeydi.

30 çakışma + red dağılımı **envanter olarak kilitlendi** (`tests/test_sinonim_carpismasi.py`,
13 test): sessizce büyüyemez, düzelen satır listede kalamaz, doğru-sayısı düşemez.

### 6.1e Red gerekçesi ölçülebilir oldu (Faz 0) ✅

`route()` **on ayrı yerde** `None` döner ve hangisinde pes ettiği yalnız `trace` metninde /
`source=None`'da görünüyordu — **sayısal olarak gruplanamıyordu**. Deterministik tavanın
**%64** olduğu ölçülmüştü ama kalan **%36'nın nasıl dağıldığı** bilinmiyordu; hangi
kaldıraca yatırım yapılacağı (netleştirme chip'i · Intent-JSON · Discovery) o dağılım
görülmeden karar verilemez.

`cube_router.RED_KODLARI` (**R1…R10**, koddaki dallarla birebir, testle kilitli) +
`InteractionLog.reject_reason` (**ayrı, indeksli kolon** — `note`'a sıkıştırılmadı; `note`
serbest metin ve `mine_candidates` onu zaten başka amaçla okuyor). Kolon NULL ise `route()`
pes ETMEMİŞTİR: **doluluk oranı doğrudan "deterministik yoldan çıkamayan sorular" kümesidir.**

**`route()`'un imzası DEĞİŞMEDİ.** Beş çağıranı var; dönüş tipini `tuple`a çevirmek hepsini
kırar ve gerekçeyi zincirin her katmanından elle taşıtırdı. Bu deponun **kanıtlanmış**
çözümü kullanıldı: `app/llm.py`'nin `_llm_usage_var` + `reset/record/get` kalıbı (derin
fonksiyon kaydeder, sığ fonksiyon okur, aradaki imzalar sabit). Yeni mekanizma icat
edilmedi.

**Dal SIRASI anlamlıdır ve telemetriyi okuyan bunu bilmeli** (ölçüldü, testte kayıtlı):
`"zxqw plmk asdf"` → **R1** (hiç cube eşleşmedi), **R10 değil** — kapsam kapısına sıra
gelmiyor. `"bu yıl ciro zxqwplmk"` → **R10**. R1'in yüksek çıkması *"kapsam kapısı çok
sıkı"* anlamına gelmez; yanlış kaldıraca yatırım yapmamak için bu ayrım kayıtlı olmalı.

**Faz 0'ın ölçüm çıktısı** `lab/telemetri_envanteri.py` ile üretilir (dağılım · en sık 20
red gerekçesi · `auto_cube` envanteri). Araç `auto_cube` için **oran hesaplamaz**, denetim
örneklemi ÇIKARIR — otomatik bir "doğruluk" üretmek §1.7'nin eleştirdiği hatanın (yapısal
geçerlilik ≠ semantik doğruluk) tekrarı olurdu.

**Bu checkout'ta ölçülen (dürüst kayıt):** yerel DB'de `interaction_log`/`verified_query`
**tabloları YOK** — migration bu ortamda koşmamış. Bu, telemetrinin akıp akmadığı hakkında
**hiçbir şey söylemez**; araç iki durumu (`sema_yok` vs boş tablo) bilinçle ayırır, çünkü
farklı eylem gerektirirler. Raporun *"7 satır"* rakamı **devralınmadı**.

**Faz 0'ın açık kalan tek maddesi ve NEDENİ:** `route-distribution` uç noktasının UI'a
bağlanması. Uç **admin plane'de** (`/sadmin/*`, ayrı ASGI örneği + ayrı JWT — ADR-0015) ve
depoda **admin frontend YOK** (`backend/admin-dev/` yalnız bir başlatıcı `package.json`).
Tenant frontend'i onu çağıramaz. Admin arayüzü inşası ürün-deneyimi planının işidir ve o
plan ayrı bir belgeye taşındı. **Faz 0'ın ölçüm çıktısı bu panele bağımlı değildir** —
envanter aracı veriye doğrudan bakar. Telemetri kalıcılığı (`dima_logs` volume) zaten
yapılmıştı (`docker-compose.yml`).

### 6.1d Ölü uç kapandı — 13 seçenekli döküm bir cevap değildi (Faz -1) ✅

**Canlı örnek:** *"son 6 ay personel bazlı çalışma süreleri kıyasla"* → sistem **13 cube'un
her birinden 1 ölçü** döküyordu ve **kaç kez denenirse denensin bir daha LLM'e bile
düşmüyordu**. Zincir: `compare_mode` True · `_period_hit_words` True · ama `partial_unknowns`
`hits=[]` → "hiç konu yok" dalı → `_finish(...)` **doğrudan return**. `_finish` her zaman
truthy döner ve **üç** `_try_fresh_intent()` çağrı yeri de `if fresh: return fresh` yapıyor
→ Discovery'ye (adım 5) hiç sıra gelmiyordu.

**Elde sinyal VARDI, kullanılmıyordu.** "personel" `ik`/`parti`'de zaten bir sinonim. Ama o
zayıf cube/boyut taraması `if unknown and hits:` bloğunun **İÇİNDEYDİ** — `hits` boşken,
yani sistemin en çaresiz olduğu anda, **erişilemiyordu**. Tarama
`cube_router.ilgili_cubelar`'a **taşındı** (kopyalanmadı; iki çağıran da onu kullanır) ve
dal üç seviyeli bir karara dönüştü:

1. **Daralt** — zayıf sinyal varsa ilgili cube'ların ölçüleri (13 → 2-4), LLM'siz
2. **Discovery'ye izin ver** — `_match_cube(q, schema) is not None` ise `None` dönülür ve
   merdivenin 5. basamağı devralır. Bu kapı yapısal-takip zincirinde **zaten vardı**;
   fresh zincirinde yoktu — asimetri buydu, ikinci bir kural icat edilmedi
3. **Dürüstçe reddet** — hiçbir kelime tanınmıyorsa katalog dökümü kalır, ama notu artık
   *nedenini* söylüyor (*"sorunda tanıdığım bir konu geçmiyor"*)

**Bu düzeltmenin KENDİ testi bir kusur yakaladı — ve kaydedilmesi gerekiyor.** İlk sürüm
*"bu yıl tüm AYLARINI karşılaştır"* sorusunu — adı bile `test_konusuz_soru_tahmin_etmez` olan,
hiçbir konu taşımayan soruyu — `ik`e bağlıyordu: `ik.donem` boyutunun sinonimleri
`['donem','ay','periyot','period']` ve `"aylarini"` bunlara ek-uyumlu eşleşiyor. Sonuç
*"İK / bordro ile ilgili görünüyor"* — **13 seçenekli dökümden DAHA KÖTÜ**, çünkü kendinden
emin ve yanlış. §6.1'in *"en tehlikeli sınıf"* dediği şeyin bir **düzeltmenin içinden**
doğmuş hâli.

İki deneme gerekti ve ikisi de kaydedilmeli:
- **Yetmeyen:** `time_dimensions` beyanını dışlamak. Ölçüldü — `ik`in zaman boyutu
  `donem_tarih`; sorunu çıkaran boyut **kategorik** `donem`. **Beyan bu ayrımı taşımıyor.**
- **Çalışan:** dolgu sözlüğü. `_period_hit_words | _misc_hit_words` bu deponun *"bu kelime
  dönem/granülerlik ifadesidir"* **tek kaynağıdır** ve `_uncovered` zaten onu kullanıyor.
  Eşleşme yalnız **dolguyla açıklanmayan** kelimeler üzerinde aranır. Yeni liste yazılmadı.

**Dürüst sınır:** çıplak *"dönem"* kelimesi hâlâ `ik`e daraltır — ve bu **savunulabilir**:
`ik`in `donem` adında gerçek bir boyutu var ve dolgu sözlüğü onu dolgu saymıyor. O kelime
gerçekten belirsizdir; testin onu "yanlış" ilan etmesi ölçüme değil sezgiye dayanırdı.

### 6.1c İkiz `match_kpi` silindi (Faz -0.5b) ✅

`cube_router.py`'de **iki** `match_kpi` tanımı vardı (498 ve 510). Python modül seviyesinde
ikinciyi bağladığı için birincisi **sessizce gölgeleniyor ve ölü kalıyordu**. İkisinin
semantiği de farklıydı: ölü olan `_syn_hit()` ile **Türkçe ek farkındaydı**, yaşayan çıplak
`in` kullanıyor. İronik olarak yaşayan tanımın docstring'i fonksiyonun *"HİÇ
TANIMLANMAMIŞTI"* olduğunu yazıyordu — gölgelenme kazası **yazıya da geçmişti**.

Ölü tanım silindi, yanıltıcı not düzeltildi. **Ek farkındalığının kaybı bilinçli bir kabul
değil, ölçülmemiş bir borçtur**: KPI sinonimleri bugün tam-alt-dizi eşleşiyor ve `len >= 3`
tabanıyla korunuyor. Yaşayan semantik testle kilitlendi.

### 6.2 Yapısal boşluklar
- **kısmen düzeltildi (2026-08-02, Faz 3.1)** — **`route()`'ta güven skoru yoktu** ve belirsizlik
  en kötü kararı tetikliyordu (en az yönetilen katmana düşüş).
  - **Önce ölçüldü:** 5011 soruluk korpusta `route()` 1057 soruda `None` dönüyor ama bunların
    **872'sinde zaten bir netleştirme chip'i vardı** (`cube_only_match` 502,
    `measure_cube_candidates` 370). Yani tez %82 oranında çoktan çözülmüştü; gerçek boşluk 185.
  - ✅ En büyük kapsanmayan sınıf kapatıldı: `_match_cube`'un `len(hits)>1` dalında beraberliği
    kıramaması. `cube_tie_candidates` **yalnız kanıt EŞİTKEN** (cube-sinonim ve ölçü-sinonim
    uzunlukları birebir aynı) konuşur ve chip Intent-JSON'dan **önce** gelir — iki aday eşit
    kanıt taşırken LLM'e seçtirmek §4-6'nın ihlalidir. Chip metni **route() ile doğrulanır**:
    referans, katalog o cube'a daraltılıp yeniden koşularak hesaplanır ve yalnız `cube_query`si
    birebir eşleşen metin yayımlanır. Adaylardan biri ifade edilemiyorsa **hiçbiri** yayımlanmaz.
  - Kanıtın eşit OLMADIĞI dal (33 soru) bilinçli olarak **dokunulmadı** — o bir beraberlik değil
    zayıf sinyaldir ve orta güven bandı Intent-JSON'ındır.
  - **Skaler bir güven sayısı üretilmedi.** Karar noktaları ayrık ve kanıt karşılaştırması
    denetlenebilir; kalibre edilmemiş bir float aynı kararı verip gerekçesini gizlerdi.
- **Sıçrama-derinlikli cube tercihi (plan §3.2) ÖLÇÜLDÜ ve ERTELENDİ.** Planın öngörüsünün ilk
  yarısı tuttu (`dim_owners>1` artık norm: çok-adaylı soruların %66'sı), ikinci yarısı tutmadı:
  TB3'ün ölmesi maliyet doğurmuyor, çünkü `_match_cube` o 969 sorunun **%94'ünü** daha önceki
  kırıcılarla zaten çözüyor. Kalan 55 soru Faz 3.1'de chip'lenen beraberliğin ta kendisi ve
  derinlik onları **çözemez**: boyut ya iki cube'da da yerli (derinlik 0=0) ya da ikisinde de
  üretilmiş (1=1). Ayrıca katalogdaki 7 üretilen boyutun hepsi `hops=1` — merdiven iki basamaklı.
  Yeniden açılma koşulu: yayımlanmış 2-sıçramalı boyut belirmesi.
- ✅ **düzeltildi (2026-08-02, Faz D4)** — **self-consistency yazılmış ama BAĞLANMAMIŞTI.**
  `app/config.py` *"LLM cube-seçimi k kez örneklenir, kanonik CubeQuery üzerinde oylanır;
  uyuşmazlık → chip"* diye beyan ediyor ve varsayılanı `3` idi; `grep -rn "consistency_k"`
  bugüne kadar **tek bir tüketici** bulmuyordu (yalnız tanım satırı). `ask.py` tek örnek
  alıyordu: oylama yok, uyuşma ölçümü yok, chip yok. `_select_consistent` da üç testi
  olmasına rağmen üretimde hiç çağrılmıyordu. Artık Intent-JSON yolu k örneği **paralel**
  alır (gecikme ~tek çağrı), kanonik CubeQuery üzerinde oylar; uyum <2/3 ve uyuşmazlık **tek
  eksende** ise netleştirme chip'i döner (tahmin YOK), çok eksendeyse merdiven sessizce devam
  eder — anlaşılmaz bir chip, chip olmamasından kötüdür. Chip'ler `next_steps` üzerinden
  taşınır: yeni alan/panel açılmaz ve tıklama `/cube` ile **LLM'siz** koşar.
  **Agentic bağı:** uyum oranı yalnız doğruluk değil **kalibre bir güven sinyalidir** —
  Faz F planlayıcısının eskalasyon/bütçe kararının girdisi.
- ✅ **düzeltildi (2026-08-02, Faz D1)** — **`mizan`'ın tek kırılımı hesabın kendisiydi**
  (`hesap_kodu`/`hesap_adi`: 27/27, aynı grain). *"Gider hesaplarının toplamı"*, *"dönen
  varlıklar bazında bakiye"* gibi bir muhasebecinin İLK soracağı sorular deterministik yolda
  cevapsızdı — mizanın asıl ekseni hesap değil hesap SINIFIDIR. `yevmiye_satirlari →
  hesap_plani` ilişkisi zaten vardı; eksik olan `expose:` bildirimiydi. Ölçülerek iki kolon
  eklendi: `hesap_tipi` (4 farklı: aktif/pasif/gelir/gider) ve `ana_grup` (5 farklı).
  Etiketler TEK KELİME — çok kelimeli etiket kelimelerine ayrılıp `hesap` sinonimi doğurur ve
  mevcut `hesap_kodu`/`hesap_adi` sözlüğünü çalardı (ADR-0018 LABEL ⊆ SYNONYM).
  **Kalan `expose:`siz 20 ilişki ölçüldü ve bilinçli olarak açılmadı:** hedef cube boyutu
  zaten elle tanımlamış (`parti.musteri`, `enerji_makine.bolum`), ya da kolon kardinalitesi 1
  (`tedarikciler.sehir`/`tur` — daha önce denenip GERİ ÇEKİLMİŞ), ya da ilişkinin "bir" tarafı
  cube'un tabanı (expose oraya boyut üretmez). Boyut eklemek bedava değildir: sinonim çakışma
  yüzeyini ve router'ın arama uzayını büyütür.
- **Çapraz-alan soruları `cube_router.py:1502`'de ölüyor** — `_match_cube`'da değil. 13 probun
  12'si orada; 8'inde cube ve ölçü zaten doğru çözülmüş. (Bu satır `cube["dimensions"]` okuyor.)
- ✅ **4 cube view-tabanlıydı** (`parti`, `ik`, `mizan`, `enerji_tesis` = kataloğun %31'i, en
  zengin ikisi dahil) → ilişki zenginleştirmesinden **sıfır kazanç** alıyorlardı. Faz 2'de üçü
  modele taşındı; `enerji_tesis` bileşik anahtar nedeniyle **bilinçli olarak** view kaldı (**plan** §3.2).
  Bakım dışında ölçülen ikinci kazanç **join pruning**'dir: `statements.py`'nin gelir tablosu
  sorgusu 2 join yerine **0**, `ik.personel_sayisi` 3 tablo taraması yerine **0 join**.
- **3 cube'un hiç giden ilişkisi yok**: `cari`, `ticaret`, `enerji_sapma` — bu bir
  `relationships.yml` eksiğidir. (Plan 1.4'ün önerdiği `cari_hareketler → musteriler` ilişkisi
  **veriyle çürütüldü**: `cari_kodu` polimorfiktir, satırların %52,9'u öksüz kalırdı —
  `tests/test_relationship_health.py` bunu kalıcı olarak kayda geçirir.)
- ✅ **`models_enrich.yml` mekanizması vardı ama öksüzdü**: 31 ilişkiden 2'sinde kullanılıyordu
  (%6,5) ve ürettiği 7 calc kolonu hiçbir cube okumuyordu. Faz 1'de `_compose_relationship_
  dimensions` üreteci yazıldı (`relationships.yml`'de `expose:` bloğu → handle + calc kolon +
  boyut), Faz 2'de göç eden üç cube o kolonları okumaya başladı.

### 6.3 Güvenlik / doğruluk
- **`always_filter` baypasları** — kısmen kapatıldı:
  - ✅ **manifest okuma yutması** (`wren_service.py`'deki `except Exception: return sql`) —
    Faz 0.2'de fail-closed yapıldı.
  - ✅ **VQR ham-SQL replay'i** — Faz 0.6'da şema-sürüm kapısı eklendi: ham-SQL kayıtları
    `mdl_version` damgalanır; damga bayatsa (ya da yoksa) kısayol atlanır. `dry_plan` bunu
    yakalayamaz çünkü SQL sözdizimsel olarak hâlâ geçerlidir — değişen anlamdır.
  - ❌ **Discovery ham SQL'i** (`ask.py`) — açık. Kalıcı çözüm uygulama katmanında değil,
    motor seviyesindedir (session property / DB RLS); Faz 1'in G10 kapısıyla birlikte planlı.
    - ✅ **ÖĞRENİLMESİ ise Faz 4.1'de durduruldu.** Bulgu (2026-08-02): başarılı HER bağımsız
      Discovery cevabı, ham LLM SQL'iyle birlikte incelenmeden VQR'a yazılıyor ve
      `near_exact` kaynağa **bakmadan**, üstelik yalnızca BENZER (birebir değil — eşik 0,92
      embedding / 0,85 sözlüksel) bir soru için onu birebir tekrar oynatıyordu. Yani bu
      baypas kalıcılaşıyor, `source="vqr"` rozetiyle sunuluyor ve LLM'in tahmini insan
      onaylı bir kayıtla **aynı otoriteye** sahip oluyordu. Artık `_TRUSTED_SOURCES`
      izin listesi var: `auto_discovery` **replay'e girmez** (few-shot'ta kalır — orada
      çıktı yeniden doğrulanır, blast radius dolaylıdır).
  - ✅ **drill raw leaf** (`drill.py`) — **kapatıldı (2026-08-02, Faz A2)**. Bu kayıt eskiden
    yalnız `always_filter` boyutunu anıyordu; denetimde **üç** değişmezin aynı 30 satırda
    kırıldığı bulundu: (1) `always_filter` uygulanmıyordu, (2) PII maskesi çalışmıyordu,
    (3) `audit.record` yoktu — yani tenant verisinin **ham satırları iz bırakmadan** dışarı
    çıkıyordu. Kök neden `SELECT *`'tı: ham satır demek cube'un yayımlamadığı **her** kolon
    demektir (`app/pii.py`'nin kendi docstring'i `personel_ozluk.tc_kimlik`'i örnek veriyor).
    Savunma sırası bilinçli: önce **seçme** (hassas kolon sorguya hiç girmez — Faz A1'in
    sınıflandırması), sonra **maskeleme** (serbest metne gömülü PII), sonra **iz**. Maskeleme
    ilk savunma olsaydı yakalayamadığı alanlar (ad-soyad regex'le tutulamaz) sızardı.
    Ayrıca `schema()` artık `is_calculated`/`relationship` bayraklarını taşıyor — calc kolonu
    ve ilişki handle'ı fiziksel değildir ve ham sorguya giremez.
  - ❌ ***filtreli bir modele join'lemek*** — açık ve Faz 1 için **P0**: ölçüldü, 34M TL
    `alis` verisi `tur='satis'` filtresini geçti. Auto-join bu baypası "yalnız Discovery"den
    "handle üretilen her cube"a yayar (bkz. §9 G10).
- ✅ **düzeltildi (2026-08-02, Faz 0.2)** — **`compose()` kilitsiz `rmtree` yapıyordu**. Build
  boyunca (~130-160 ms) `target/mdl.json` **yoktu**; o pencerede gelen sorgu ya `FileNotFoundError`
  alıyor ya da `always_filter` yutmasına düşüyordu. Üç düzeltme: `build_lock_for(out)` süreç-geneli
  per-dizin kilidi (`compose_and_build` de artık onu alıyor), `target/` compose sırasında
  **korunuyor** (eski manifest yeni build bitene kadar geçerli kalıyor), `build()` geçici dosya +
  `os.replace` ile **atomik**.
- ⚠️ **Kilit SÜREÇ-İÇİDİR (`threading`), süreçler arası DEĞİL.** İki ayrı süreç aynı çıktı
  dizinine compose ederse yarış geri döner: `FileNotFoundError: .../models/<x>/metadata.yml`.
  Bu, 2 Ağustos 2026'da **yeniden üretilerek** teşhis edildi — iki test konteyneri aynı bind
  mount'a paralel koşturulduğunda. Üretimde tek konteyner olduğu için bugün ısırmıyor; ama
  çok-süreçli bir dağıtımda (gunicorn worker'ları, ayrı scheduler süreci) dosya kilidine
  (`fcntl.flock`) yükseltilmesi gerekir. **Testleri paralel iki konteynerde koşturma.**
- ~~**Telemetri kalıcı değil**: `docker inspect` → `Mounts: []`~~
  ⟳ **DÜZELTİLDİ ve BU KAYIT BAYATLAMIŞTI (ölçüldü, 3 Ağustos 2026).** Bugün
  `docker inspect dima-backend-core` **iki named volume** gösteriyor:
  `…_dima_logs → /app/logs` (telemetri DB'si) ve `…_dima_hf_cache → /tmp/fastembed_cache`.
  **Tam rebuild + `docker rm -f` sonrası 105 satır KORUNDU** — yani *"her build geçmişi
  siler"* artık doğru değil. Kaydın kendisi, bu turda on dört kez avlanan *"beyan var,
  gerçek başka"* sınıfının bir örneğiydi: doğru yazılmış bir cümle, dünya değişince
  kaldı. `interaction_log`: o an 7 → 3 Ağustos **105** (ortam uzlaştırması: §6.3 ⟳ FAZ 9.10).

### 6.4 Dağıtım / test altyapısı (2026-08-02'de bulundu)

- ✅ **düzeltildi (2026-08-02)** — **Dockerfile ↔ pyproject bağımlılık sapması.**
  `backend/Dockerfile` runtime bağımlılıklarını pyproject'ten türetmiyor, **elle sayıyordu** ve
  `mrml`, `jinja2`, `ruamel.yaml`, `alembic` **eksikti**. Çalışan üründeki sonucu sessiz
  çökmelerdi: `app/email_render.py:48` → **her zamanlanmış rapor e-postası** (ADR-0011),
  `app/mdl_writer.py:19` → **ölçü terfisi (Faz 2d) + bağlantı sihirbazının şema yazımı**
  (ADR-0017). Düzeltme: 4 paket eklendi, build'e import duman testi kondu, ve
  `tests/test_dependencies.py` eklendi — pyproject'i tek gerçek kaynak sayan, Docker'dan
  bağımsız bir regresyon kilidi. **Ders: bildirilen bağımlılık listesinin elle tutulan bir
  kopyası varsa, o kopyanın sapmadığını iddia eden bir test de olmalı.**
- ✅ **düzeltildi (2026-08-02)** — **Test paketi ağa bağımlıydı ve pratikte hiç bitmiyordu.**
  `vqr._embedder()` ilk çağrıda HF Hub'dan `multilingual-e5-large` (~2.2 GB ONNX) indirmeye
  çalışıyor; kimliksiz indirme oranlanıyor ve **duruyor** (ölçüldü: 20 sn'de 0 bayt ilerleme,
  `.incomplete` 67 MB'da takılı), `fastembed`/`requests` katmanında timeout **yok**. Taze bir
  konteynerde pytest **saatlerce** asılı kalıyordu (canlı bildirim: ~10 saat, hiç bitmedi) —
  yani **hiç kimse testleri koşamıyordu**, ki yukarıdaki bağımlılık sapmasının bu kadar uzun
  yaşamasının sebebi de budur. Düzeltme: `DIMA_VQR_EMBEDDER=auto|off` anahtarı; `conftest.py`
  `off` yapıyor → **507/507 test, 80 saniye, `--network none` ile**. `_embedder()`'ın sessiz
  `except Exception` yutması da ADR-0020 uyarınca loglanır hale getirildi.
  **Kalan iş (Faz 0.1):** üretimde `/tmp/fastembed_cache` bir named volume olmalı — yoksa her
  yeniden-build 2.2 GB'ı sıfırdan indirir ve ilk sorgular embeddersiz (sözlüksel) koşar.
- ✅ **düzeltildi (2026-08-02, Faz D)** — **Ölçüm aracının kendisi kırıktı ve bunu kimse
  görmedi.** `lab/nl_corpus.py` — planın *"asıl metrik"* dediği ve deterministik tavanı
  (%64) üreten araç — `WrenService`'in üç metodunu monkeypatch'liyordu:

      ws.WrenService._enrich_categorical = lambda self, models: None

  Faz B1 bu metoda **ikinci bir parametre** (fiziksel ad haritası) ekledi; lambda sessizce
  kırıldı ve araç her şirket için `TypeError` verip `HATA` raporlamaya başladı. Yani
  **B1'den bu yana deterministik tavan HİÇ ÖLÇÜLEMEDİ** — pytest yeşil, eval sapmasız, ama
  planın ana metriği ölüydü. Monkeypatch olduğu için ne tip denetimi ne test yakalar.
  Düzeltme: üç lambda da `(self, *a, **k)` imzasıyla esnetildi (gövdeleri zaten hiçbir
  argüman kullanmıyor).
  **Ders — ölçüm aracının kendisi de bir bağımlılıktır.** Üretim koduna dokunan her imza
  değişikliği, o kodu taklit eden harness'i de bozabilir; ve harness kırıldığında
  sistem *"ölçemiyorum"* demez, *"her şey hata"* der — ki bu bir süre sonra gürültü sayılır.
- ✅ **kapatıldı (2026-08-02, Faz E-1)** — **telemetrinin YAZMA yolu hiç test edilmiyordu.**
  Altyapı tamdı: `InteractionLog` (20 alan), KPI ucu (`route-distribution`), varsayılan
  **açık**. Ama `test_route_distribution.py` ve `test_candidates.py` satırları **elle
  ekleyip** yalnız OKUMA tarafını sınıyordu; `conftest.py` ise yazmayı **global olarak
  kapatıyor** (haklı olarak — testler canlı telemetriyi kirletmemeli). Sonuç: `/ask`'in
  gerçekten satır yazdığını sınayan **hiçbir test yoktu**.
  Bu, aynı fazda ölçülen `lab/nl_corpus.py` kusurunun **aynı sınıfıdır**: ölçüm aracı
  sessizce kırılırsa sistem *"ölçemiyorum"* demez — KPI **sıfır** okur ve herkes
  *"trafik yok"* sanır. Planın *"Intent ≥%70 / Discovery <%30"* hedefi tam olarak bu
  satırlara dayanıyor.
  Düzeltme: `tests/test_telemetri_yazma_yolu.py` yazmayı **yalnız kendi testleri için**
  açar (conftest'in global kapaması bozulmaz) ve zinciri uçtan uca doğrular — `/ask` yazar
  → alanlar dolu (`kind`/`source`/`duration_ms`) → `route-distribution`'ın gruplamasında
  tanınır. Ters yön de kilitli: **kapalıyken yazmamalı**, aksi halde her test koşumu canlı
  KPI'ı gürültüye boğar.
  **Ölçülen sonuç: yazma yolu ÇALIŞIYORDU** — bulgu kırıklık değil **denetimsizlikti**.
  Fark önemli: çalışan ama test edilmeyen bir ölçüm, olmayan bir ölçümden **daha kötüdür**
  çünkü yanlış bir güven verir.
- **Test koşum reçetesi** (host'ta bağımlılık yok, prod imajda pytest yok):
  `docker build -t dima-test` = prod imaj + `pytest pyyaml httpx ruff`; sonra
  `docker run --rm --network none -v "$PWD/backend:/app" \
       -v "$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro" \
       -w /app dima-test python -m pytest -q`.
  ⚠️ **Frontend mount'u zorunludur** (Faz H): `tests/test_uc_yetim_degil.py` frontend ağacını
  göremezse **atlar** — yani yalnız `backend/`'i mount eden bir koşumda yetim-uç kapısı
  sessizce devre dışı kalır ve yeşil bir koşum "kontrol edildi" gibi okunur.
  Bind-mount sayesinde kod değişikliğinde imaj yeniden build edilmez. `--network none`
  hermetikliği garanti eder — testlerin ağa çıkmaya çalışması bir hatadır, yavaşlık değil.

---

## 7. Ölçüm sözleşmesi

| Ne | Nereden | Hedef |
|---|---|---|
| Intent / cache / Discovery payı | `GET /sadmin/interactions/route-distribution?days=N` (`admin_app/routers/interactions.py:161`) | **Intent ≥ %70 · Discovery < %30** |
| LLM'siz cevap oranı (tenant) | `GET /stats/today` (`app/routers/stats.py:39`) | artan |
| Cevap doğruluğu | `python -m eval.run` → `answered_precision` (Wilson CI) + `coverage` | baseline'ın **altına düşmez** (`tests/test_eval_gate.py`) |
| Deterministik tavan | `python lab/nl_corpus.py` (~1000 soru × 4 şirket, LLM'siz) | artan |
| **Dört kapının CI koşumu** | `.github/workflows/nightly.yml` → `python lab/kapi.py --tam` | gecelik `30 2 * * *` + `workflow_dispatch`; 40 dk tavan |
| **Modül büyüme tavanı** | `10 test: `tests/test_modul_buyume.py`` | `ask()` **1147 kod satırı / 19 iç fonksiyon** · `cube_router.py` **1736** — dördünde de **boşluk 0**. ⚠ FAZ 1.12: dosya tavanı **ayrı** bir muafiyet listesine bağlandı (`MUAFIYET_ASK_DOSYA`) — modül düzeyine eklenen bir satır, `ask()` gövdesinin tavanını **yükseltmiyordu** ama eski tasarımda yükseltirdi |
| Doğru cube/ölçü/boyut | `python lab/nl_accuracy.py` | artan |
| **AI Act / NIST RMF / ISO 42001 karşılığı** | `31 test: `tests/test_ai_act_uyumu.py`` | Md.50 işareti **her** yanıtta (`ai_generated_prose` · `kanit_sinifi`) · Md.13 ihracı (`GET /audit/export`, zincir bütünlüğüyle) · Md.14 durdurma (`DELETE /ask/jobs/{id}`) · Md.12/19 saklama **beyanı**. ⚠ Yürürlük **tarihi** kapıya çevrilmedi: yol haritası onu `[DOĞRULANMADI]` işaretlemiş, kapı yükümlülüğün **kod karşılığını** ölçer |

**Ölçülen baseline (2026-08-02, `--network none`):**

| Metrik | Değer |
|---|---|
| eval `det` dilimi | 129 adım · **answered-precision %100** · **coverage %100** · chip %100 |
| **deterministik pay** | **%100** — yol dağılımı `intent=111` |
| pytest | ⟳ **D2 (FAZ −1/A5, denetimde bulundu):** sabit sayı SİLİNDİ — *"1016 geçti"* bugün **iki kat** bayattır. Komut: `python -m pytest -q --collect-only \| tail -1` *(taban ve damga: `OPERASYON-DURUM.md` ölçüm tablosu)* |
| **`lab/nl_corpus.py` — GERÇEK deterministik tavan** | ⟳ **D2 (FAZ −1/A9, denetimde bulundu):** sabit sayı SİLİNDİ — *"8984 turda ~%64"* bu satırda **bayattı** ve tam yedi satır aşağıda kendi ⟳ notu onu çürütüyordu. Güncel değer **komutla** üretilir: `python lab/nl_corpus.py --kapi` |

> ✅ **FAZ 0.15 İNDİ — ölçüm kapıları CI'da.** §0'ın `§7-CI` işaretçisi bu yüzden
> kaldırıldı (satır **daraltıldı**: risk-kapsam eğrisi hâlâ ⟳, FAZ 4.2).
> **4/4 kapı** — süit · eval · korpus · senaryo — **tek koşucudan**:
> `.github/workflows/nightly.yml` @`1732e1b` · `python lab/kapi.py --tam`.
> Ölçüm: `grep -rln "kapi.py" .github/workflows/` → **1** dosya · koşucunun kapsadığı
> kapı **4/4**.
>
> 🔴 **2/4'ü ZATEN VARDI ve bir önceki ölçüm bunu GÖREMEDİ.** `backend-ci.yml` her push'ta
> `pytest -q` koşuyor ve `tests/test_eval_gate.py` **süitin İÇİNDE** — yani süit + eval
> kapıları CI'da koşuyordu. *"Ölçüm kapısı taşıyan **0** workflow"* diyen probe, kapıyı
> **çağıran komuta** göre arıyordu ve başka yoldan koştuğunu göremiyordu. Kusur belgede
> değil **ölçüm aracındaydı** — bu turda o sınıfın kaçıncı tekrarı olduğu `OPERASYON-DURUM`'da
> yazılı. Yeni workflow eksik ikisini (korpus + senaryo) ekleyerek **4/4** yapar.
>
> ⚠️ **Eval'in %100'ünü kapsam sanma.** 111 cevabın 111'i intent yolundan geliyor, çünkü eval
> korpusu **zaten çalışan şeye göre kuratörlenmiş** — çapraz-alan boşluğuna hiç dokunmuyor.
> Boşluğun bu kadar uzun görünmez kalmasının sebebi de budur. Eval bir *regresyon
> kilididir*, kapsam ölçüsü değil.
>
> ⟳ **DÜZELTME (FAZ −1/A1+A9) — «%64» BU SATIRDA BAYAT, ve «36 puan» YANLIŞ ÇERÇEVE.**
> **(a) Sayı:** o ölçüm `8984 tur`a aitti; sonraki turlarda kapsam **büyüdü** (`2a-3`
> boyahane `%64 → %68`). ⚠ `D2` gereği **sabit sayı buraya yazılmaz** — güncel değer:
> `docker run … python lab/nl_corpus.py --kapi`.
> **(b) Çerçeve:** kalan puanların tamamı *"kapsam boşluğu"* **DEĞİLDİR.** Ölçüldü
> ([KANIT §11.1]): büyük kısmı **netleştirmedir** ve netleştirme `ADR-0007-K3`'ün
> **İSTEDİĞİ** davranıştır — bir kusur değil, bir politika. *"Kapsam, zekâ değil"* tezi
> ayakta kalır; ama o boşluğun **hepsini kapatılabilir sanmak** yanlıştır.

> 🔴 **AD ÇAKIŞMASI — bu belgede İKİ AYRI «Faz 0.4» var ve biri ötekinin kararını
> TERS gösteriyor.** Aşağıdaki paragraf **2026-08-02'nin kapsam kapısı** fazıdır
> (`475e691`; `_uncovered` alt-dizi onarımı, `_SUFFIX_CHAIN_RE`). v1 yol haritasının
> **FAZ 0.4**'ü ise bambaşka bir şeydir: `netlestirme_onceligi` bayrağının **ölçüm
> kararı** (hemen aşağıda, ayrı başlık). Sayıları karıştıran bir okuyucu, *"OK +6,
> CUBE-SAPMA −25"*e bakıp bayrağın **açılması** gerektiği sonucuna varırdı — gerçek karar
> bunun **tam tersi**. Kimlik asimetrisi bu belgenin altı kez kaydettiği sınıftır;
> burada da ad düzeyinde tekrarlamış.

**Faz 0.4 · KAPSAM KAPISI'nın ölçülen etkisi** *(2026-08-02, `475e691` — v1 yol
haritasının FAZ 0.4'ü DEĞİL)* (aynı korpus, öncesi/sonrası): OK **+6**, yanlış-cube/Discovery
(`CUBE-SAPMA`) **−25**, dürüst ret/netleştirme **+15**. Yani kapsam kapısının sıkılaştırılması
25 soruyu yanlış yerden çıkmaktan alıkoydu; bunların 6'sı doğru cevaba, 15'i dürüst
netleştirmeye gitti. Toplam OK payında net etki **−%0,25** — sessiz-yanlış sınıfını kapatmanın
bedeli olarak bilinçli kabul edildi (ADR-0008 yönü).

### FAZ 0.21 · Modül büyüme kapısı — **TAVAN, HEDEF DEĞİL**

`ask()` **tek fonksiyon**, 19 iç fonksiyon **aynı kapsamı paylaşıyor**, ve depo paylaşılan
bir dizinde: bu gövde aynı zamanda bir **çakışma jeneratörü**. `K3`'ün kusuru tam buradan
doğdu — iki bin satırlık bir gövdede bir çağrının **yanlış `if`in içinde** olduğu görünmüyor.
Kapı refactor'ü **zorlamaz** (kazancı ölçülmedi); yalnız **büyümeyi durdurur**.

🔴 **BİRİM: ham satır DEĞİL, KOD satırı** (yorum/docstring hariç) — ve bunu bir ölçüm
belirledi (`c3fcfe7` → `a41f981`): FAZ 0 `ask.py`'ye **+44 ham** satır kattı ama yalnız
**+12 kod**; %73'ü **belgeleme**. Ham satır sayan bir kapı, bu deponun **ölçülmüş kusurları
kaydettiği mekanizmayı** vergilendirir ve geliştiriciyi *"yorumu silersem yeşile döner"*
diye ödüllendirirdi. *(`cube_router.py` bugün **%52 belge**: 3592 ham ↔ 1736 kod.)*

**Tavan FAZ 0 ÖNCESİNDEN alınır** (`c3fcfe7`), FAZ 0'ın eklediği her satır **gerekçeli
muafiyet** olarak yazılır — bugünkü sayıyı doğrudan tavan yapmak **şişmiş bir tavanı**
kilitlerdi ve kapı hiç iş görmezdi:

| Ölçüt | FAZ 0 ÖNCESİ | Muafiyet | Tavan | Bugün | Boşluk |
|---|---|---|---|---|---|
| `ask()` kod satırı | 1135 | `9a138a9` +11 *(0.5 çapa zinciri)* · `98a5071` +1 *(0.12/0.13/0.6)* | **1147** | 1147 | **0** |
| `ask()` iç fonksiyon | 19 | **yok** — FAZ 0 hiç eklemedi | **19** | 19 | **0** |
| `ask.py` toplam kod | 2394 | *(yukarıdakinin taşınabilir payı)* | **2406** | 2406 | **0** |
| `cube_router.py` kod | 1723 | `9164806` +13 *(0.18 metrik kaydı)* | **1736** | 1736 | **0** |

⚠ `0619bfd` (**0.22** · `migration_trace` `UnboundLocalError`) ham satırda **+8** getirdi
ama **kod satırında 0**: bildirim `if` bloğundan gövde başına **TAŞINDI**. Bir taşıma borç
değildir ve muafiyet listesinde yeri yoktur — *neden listede olmadığı* kapıda yazılı.

⚠ Yol haritası bu maddeyi *"~1.930 satır / **20 closure** @`c4b14d1`"* diye ilan etmişti;
buradaki sayılar `c3fcfe7`'ye ve farklı bir birime ait. İkisi **çelişmiyor**, farklı şey
sayıyorlar — ve fark **sessizce benimsenmedi**, kapıda yazılı (*"ölçüm birimi tanımlanmadan
yapılan kıyas, kıyas değildir"*).

### FAZ 0.4 (v1) · `netlestirme_onceligi` — **ÖLÇÜM KARARI: `off` KALIYOR**

Yol haritası bu maddeyi bir **karar** olarak yazdı: *"Kayıp > kazanç ise `off` kalır ve
nedeni `MIMARI.md`'ye yazılır."* Karar **ölçüldü ve `off` çıktı**; gerekçe burada.

**Ne yapar:** katalogda **≥2 SAHİBİ** olan bir ölçüde (ör. `bakiye` → `cari`|`mizan`)
netleştirme chip'ini **Intent-JSON'dan ÖNCE** koyar (`ask.py:2601`). Kapalıyken aynı
netleştirici Intent'ten **sonra** çağrılır (`ask.py:2757`) — mekanizma `ff987eb`'de indi.

**Ölçüldü — CANLI sağlayıcıyla, 2026-08-03:**

| Ölçüm | Sonuç |
|---|---|
| A/B, 63 etiketli vaka *(negatif kontrol)* | **bozulan 0** · kurtarılan 0 |
| Kurtarma, 15 gerçek ifade | cevaplanan 12 → 8 · kurtarılan **1** *(doğru ölçüyle **0**)* · **kaybedilen 5** |
| Kararlılık, aynı soru ×3 | **5/6 KARARLI** — tek kararsız: *"bu yıl borçları"* (`cari`×2, `mizan`×1) |

**Karar ve gerekçesi:** kaybedilecek 5 cevap **yazı-tura değil**. Model tutarlı **ve
savunulabilir** seçiyor (`cari` = müşteri defteri). B2 kabul ölçütü (*"DOĞRU kurtarma
> 0"*) **karşılanmıyor** (0), kayıp ise **gerçek** (5). → **`off` KALIR.**

🔴 **İLAN EDİLEN KAPI BU KARARI VEREMEZDİ — ve nedeni ilkesel.** Yol haritası kapıyı
`lab/nl_corpus.py --kapi` öncesi/sonrası diye yazmıştı. İki bağımsız sebeple çalışmaz:

1. **LLM'siz koşumda A/B farkı YAPISAL OLARAK SIFIRDIR.** `:2601` ile `:2757` **aynı**
   netleştiriciyi çağırır; ikincisi Intent-JSON'dan sonradır ve LLM yoksa Intent dalı
   hiç koşmaz → iki yol **aynı cevaba** çıkar. Fark 0 çıkar ve *"gerileme yok"* diye
   okunurdu. Ölçüldü: `python lab/faz0_4_netlestirme.py` @`1732e1b`.
2. **Korpus bu nüfusa HAKEMLİK EDEMEZ.** Korpusun *"beklenen cube"*u, soruyu hangi
   cube'un sözlüğünden ürettiğidir; bu bayrağın nüfusu ise tam olarak **aynı terimi ≥2
   cube'un sahiplendiği** kümedir. Orada korpusun yer gerçeği **kendisi bir yazı-turadır**:
   LLM'in şanslı tahmini *"doğru"*, netleştirme sorusu *"kayıp"* sayılırdı — ürün
   niyetinin **tam tersi**. `ask.py`'nin kendi yorumu: *"Gerçekten belirsiz bir kelimede
   **doğru cevap yoktur**."*

→ Yer gerçeği olmayan bir nüfusta ölçülebilecek şey **doğruluk değil KARARLILIKTIR**, ve
kararlılık yer gerçeği istemez. Karar bu ölçütle verildi (5/6 kararlı → *bağlamdan
çözüyor*), ve alet karar kuralını **ölçümden ÖNCE** yazılı taşıyor (`A · kararsız` /
`B · bağlamdan çözüyor` / `C · sistematik yanlılık`): `lab/faz0_4_netlestirme.py` ·
kapı `23 test: `tests/test_faz0_4_netlestirme.py``.

**Bugün yeniden ölçülen (LLM'siz, 2026-08-04 @`1732e1b` · `python lab/faz0_4_netlestirme.py`):**

| Ölçüm | Değer |
|---|---|
| katalogda ≥2 sahibi olan terim | **62** |
| bayrak AÇIKKEN gerçekten netleştirmeye ULAŞAN | **41** |
| LLM'siz A/B farkı | **0**/41 — *ilan edilen kapının boş olduğunun kanıtı* |
| negatif kontrol (`ab_kos`, 63 etiketli vaka) | **bozulan 0** · kurtarılan 0 |

⚠ **41 ≠ `ask.py`'nin 53'ü — ve ikisi de doğru olabilir.** `ask.py:2588` *"≥2 SAHİP +
route ÇÖZEMİYOR"* sayar; buradaki 41 ise **chip'in gerçekten kurulabildiği** kümedir.
`olcu_netlestirme` iki ayırt edilebilir etiket üretemezse (`len(etiketler) < 2`) kapı
sessizce atlanır. *"Belirsiz"* ile *"belirsizliği SORULABİLİR"* aynı sayı değildir.

⚠ **Bugünkü CANLI doğrulama `⊘ ÖLÇÜLEMEDİ`** — sağlayıcıların hepsi `429`/`503` verdi
(günlük kota). Karar **2026-08-03'ün canlı turuna** dayanır; yaşı bir gündür ve LLM'siz
yapısal ölçümler (nüfus · negatif kontrol) bugün **doğrulandı**. Ölçmediğimizi ölçtük
gibi yazmak, bu maddenin engellemek için var olduğu şeyin ta kendisi olurdu.

⚠ **AYRI BULGU — katalog sahibine devredildi, sessizce yamalanmadı.** *"bu yıl bakiye"*
**kararlı** biçimde `mizan.bakiye` seçiyor ve cevap **₺0**; mizan yapısı gereği sıfıra
denkleşir. Aynı soru `cari`'de **₺11,86 milyon** verir. Bu bir **motor kusuru değil
KATALOG kararıdır** (*bare `bakiye` hangi cube'un?*) ve sahibi **FAZ 3.1'in sahiplik
turudur** — `metrik_kaydi` (FAZ 0.18) çakışmayı **görünür** kılar, kararı vermez.

### 6.3d · FAZ 1.4 · Süreç-arası derleme kilidi

Kilit **süreç-içiydi** (`threading.Lock`): yalnız bu süreçteki thread'leri sıraya sokuyordu.
*"İki süreç aynı çıktı dizinine compose ederse yarış geri döner"* — 2026-08-02'de yeniden
üretilerek teşhis edilmişti.

🔴 **2026-08-04'te İKİNCİ KEZ, kendiliğinden gözlendi ve bir KAPIYI KIRDI.** Demet 9
kapısında `gitas` korpustan **tamamen düştü** (`FileNotFoundError: demo/wren-project/
cubes/enerji_makine/metadata.yml`); dosya sonradan **yerindeydi** — okuyucu compose'un
**ortasına** denk gelmişti. Kapı **%94,3 doğruluk** raporlarken kırmızıydı çünkü payda
**445 → 342** düşmüştü: *bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla
da olur.*

**Çözüm — iki kademeli kilit** (`app/compose.py::DerlemeKilidi`):
`threading.Lock` (ucuz, süreç-içi) **+** `fcntl.flock` (süreç-arası), zaman aşımı **60 sn**,
aşımda **`RuntimeError`** — *kilitsiz devam etmek, kilidin olmamasıyla aynı şeydir ama
üstüne bir "korunuyoruz" beyanı ekler.*

🔴 **KİLİT DOSYASI ÇIKTI DİZİNİNİN İÇİNDE DEĞİL, KARDEŞİ — ve bu ölçülmüş bir tuzak.**
`compose()` çıktı dizinindeki `target` **dışındaki her çocuğu siler**. İçeriye konan bir
kilit dosyası **tutulurken unlink edilirdi**: kilidi tutan süreç silinmiş inode üzerinde
beklemeye devam eder, ikinci süreç **YENİ bir inode** açıp `flock`'u **anında** alır —
kilit **sessizce çalışmaz** hâle gelirdi. ⚠ Yol haritası `<slug>/.compose.lock` (içeride)
diyordu; sapma ölçüye dayanıyor. *Dosyayı `target` gibi bir koruma listesine eklemek,
kilidi bir listenin bakımına bağlardı; kardeş konum **yapısal olarak** bağışıktır.*

⚠ **Zaman aşımında süreç-içi kilit de bırakılır** — yoksa ilk aşım o dizini bu süreçte
**kalıcı olarak** kilitlerdi (deadlock). Ayrı bir testle kilitli.

⚠ **`fcntl` yoksa süreç-arası kademe düşer ama SESSİZCE DEĞİL:** uyarı loglanır. Sessizce
düşürmek, kilidin var olmadığı bir ortamda *"korunuyoruz"* sanmak olurdu; süreci reddetmek
ise orantısız — tek süreçli bir kurulumda iç kademe doğru ve yeterlidir.

`10 test: `tests/test_compose_kilidi.py``. **gunicorn/çok-worker dağıtımının ön koşulu**
kapandı (→ II-G.7).

### 6.3b · FAZ 1.1 · Motor RLS — `always_filter`'ın iki baypası kapanıyor

`always_filter` (LookML `sql_always_where`) bir **uygulama katmanı** yamasıdır:
`WrenService._inject_always_filter` onu **yalnız o cube'un kendi SQL'ine** ekler. İki yol
onu atlıyordu ve ikisi de **ölçülmüştü**:

1. **JOIN** — `compose.py:434` (**G10**) birebir: *"filtreli bir modele join'lemek
   `always_filter`'ı **BAYPAS EDER**"*; join `__source` seviyesinde gerçekleşir.
2. **Discovery ham SQL** — `_inject_always_filter` yalnız `cube_sql()` yolundan çağrılır;
   ham SQL o fonksiyona **hiç uğramaz**.

Motor RLS'inde koşul **her model referansına** iner. Ölçüldü (uçtan uca, `wren_core`):
join'de filtre **iki tarafa da** iniyor · ham SQL'de de uygulanıyor · property zorunluyken
eksikse **fail-closed** · kötücül değer *"allow only literal value"* ile reddediliyor.

| kademe | manifest | servis edilen cevap |
|---|---|---|
| `off` | dokunulmaz | bugünkü |
| **`shadow`** *(varsayılan)* | **dokunulmaz** | **bugünkü** — gölge yalnız **ÖLÇER** |
| `on` | RLAC yazılır | motor filtreliyor; `_inject_always_filter` o cube'da **elini çeker** |

🔴 **`shadow` MANİFESTE YAZMAZ — ve bu bir DÜZELTMEDİR.** İlk sürüm yazıyordu; o hâlde
motor filtreyi **uygular** ve ham-SQL yolundaki cevap **değişirdi** — *"gölge"* adı altında
canlı bir davranış değişikliği. Doğru desen komşuda zaten yazılıydı (`_sql_policy`'nin
gölgesi motoru gevşek kurar, katı politikayı **AYRI** motorla paralel dener).
⚠ **803 yeşil test bunu YAKALAMADI:** `alwaysFilter` yalnız **gulteks**'te var (3 cube,
logo-3 tenant'ı) ve süit o tenant'ın **ham SQL** yolunu ölçmüyor. Yeşil bir süit,
**ölçmediği** bir davranış hakkında hiçbir şey söylemez.

⚠ **`SessionProperty` bu turda GELMEDİ ve bu "unutuldu" DEĞİL.** `always_filter` **sabit**
bir yüklemdir (`CANCELLED = 0`); ölçüldü ki motor sabit koşullu kuralı `requiredProperties`
**olmadan** da uyguluyor. Session tesisatını şimdi yazmak, **çağıranı olmayan bir yetenek**
üretirdi — `K3` (ters yetim) kapısının avladığı sınıf. İlk **session'a bağlı** kural
doğduğunda (`1.2` · tek DB'de çok tenant · rol bazlı daraltma) `sql_literal()` ile birlikte
gelecek.

🔴 **`required=False` + `defaultExpr` YASAK — ölçülmüş bir FAIL-OPEN.** O yapılandırmada
property **hiç gönderilmese bile** sorgu **varsayılanla** koşar (`WHERE tenant = 'HERKES'`).
Kimlik enjeksiyonunu unuttuğumuz gün sistem hata vermez, **başka bir filtreyle** cevap
verir — filtresiz cevaptan **daha sinsi**, çünkü sonuç makul görünür. `kurallari_denetle()`
onu fail-closed reddeder.

⚠ **Gölge kaydı JSONL değil LOGGER — sapma bilinçli.** Yol haritası `logs/rls_shadow.jsonl`
diyordu; bu depoda gölge bulgularının **zaten bir sahibi var** (`_shadow_policy_check` →
`_log.warning`) ve ikinci bir kayıt mekanizması *"aynı kuralın iki sahibi"* olurdu.
7 günlük ölçüt (*"0 satır"*) aynı greple ölçülür: `RLS (gölge)` etiketi.

⚠ **`app/pii.py` KALIYOR** — RLS **satır** düşürür, PII **hücre** maskeler. İki savunmadan
birini ötekinin gerekçesiyle kaldırmak, *"aynı kuralın iki sahibi"*nin tersi kadar
tehlikelidir: **hiç sahibi olmayan bir kural**.

### 6.3c · FAZ 1.2 · Kolon düzeyi erişim — **maskelemez, PLANDAN DÜŞÜRÜR**

Motor `columnLevelAccessControl`'ü **etiketle değil EŞİKLE** tanımlıyor
(`requiredProperties` + `operator` + `threshold`, kolon başına **tek**), yani
`sensitivity` → eşik eşlemesi **beyan edilmesi gereken yeni bir iştir**. Ölçüldü
(uçtan uca, boyahane manifesti üzerinde **20 kolon**):

| seviye | sonuç |
|---|---|
| `session_gizlilik = 0` | 🔴 kolon **plandan tamamen DÜŞER** — `SELECT *` onu döndürmez |
| `session_gizlilik = 2` | gelir |
| property **yok** | **fail-closed** (planlama hatası) |

🔴 **VARSAYILAN `off` — ve `motor_rls`'ten farklı olması ölçüme dayanıyor.** CLS
`pii.py`'den **kategorik olarak farklıdır**: maskeleme kolonu **gösterir** (`123****89`),
CLS onu **yok eder** — ve yok etme **sessizdir**. Kullanıcı sorduğu kırılımın neden
gelmediğini **öğrenemez**. *Sessizce eksik bir tablo, maskeli bir tablodan daha kötüdür,
çünkü eksiklik fark edilmez.*

🔴 **`on` KADEMESİ BİR KAPIYLA KİLİTLİ.** CLS session property'yi **zorunlu** kılar;
bugün **36** `query`/`dry_plan` çağrı sitesi kimlik **geçmiyor** ve `on` açılırsa her biri
fail-closed **patlar**. `test_MOTOR_CLS_ON_OLAMAZ_TESISAT_EKSIKKEN` bayrağı ancak tesisat
tamamlandığında açılabilir kılar — *"açtım ama yarısı çalışmıyor"*, bir güvenlik katmanının
en pahalı hatasıdır. Kalan çağrı siteleri **sayıyla** raporlanır (sessiz kırpma yok).

⚠ **SEVİYELER UYDURULMADI.** `authorize.py` zaten `"pii:view": 2` (admin+) diyor;
`gizlilik_seviyesi()` o kararı **okur**. Yeni bir gizlilik merdiveni icat etmek, aynı
kuralın **ikinci sahibini** doğururdu. Ara seviye **1** eşik yapısında **yer tutuyor**
ama kimseye atanmıyor.

⚠ **HASSASİYET SINIFI TEK SAHİPTEN** (`app/sensitivity.py::classify`). `pii.py` ile CLS
farklı sözlükler okusaydı aynı kolon bir katmanda maskeli, ötekinde **görünür** olurdu.

🔴 **İKİ KATMAN, İKİ BİÇİM — ve karıştırmak üç PII testini kırmızıya düşürdü.**
`wren_core.SessionContext(properties=…)` **`frozenset`** ister; `wren.engine.WrenEngine.
dry_plan/query(properties=…)` **`dict`** ister ve dönüşümü **kendi** yapar. Ön ölçüm
probe'u `SessionContext`'i doğrudan kullandığı için `frozenset` görüldü ve **bir katman
yukarıya** taşındı → `'frozenset' object has no attribute 'items'`. *Belgelenmiş bir tuzak,
yanlış katmanda uygulanınca yine tuzaktır.* Ayrım artık `test_HANGI_KATMAN_HANGI_BICIM`'de.

### Ölçüm araçlarının GERÇEKTEN ne ölçtüğü (2026-08-02'de tek tek doğrulandı)

Bu tablo bir uyarıdır: üç aracın adı da "doğruluk" çağrıştırıyor ama üçü farklı şey ölçüyor
ve **hiçbiri ölçekte "doğru cube'u mu seçti"yi ölçmüyor**.

| Araç | Gerçekte ölçtüğü | Boyut | Not |
|---|---|---|---|
| `eval/run.py` | Şekil doğruluğu (cube/ölçü/boyut beklenen mi) | 129 vaka | Korpus **zaten çalışan şeye göre kuratörlenmiş** — 111 cevabın 111'i intent yolundan. *Regresyon kilidi*, kapsam ölçüsü değil. |
| `lab/nl_corpus.py` | **ERİŞİM** + ✅ **DOĞRULUK** (2026-08-02'de eklendi) | ~10.800 tur | Erişim = "herhangi bir yoldan SQL üretti mi". Doğruluk = "sorunun üretildiği cube'u mu seçti". Üç yollu: doğru / yanlış cube / Discovery'ye düştü. |
| `lab/nl_accuracy.py` | Doğru cube/ölçü/boyut, etiketli | **4 vaka** | Fiilen boş. `nl_corpus`'un doğruluk kanalı onun yerini büyük ölçüde aldı. |

> **Neden eklendi:** `nl_corpus` `expected` olarak TÜM cube adlarını geçiyordu, yani yanlış
> cube'a gitmek de OK sayılıyordu. Faz 1'in üreteci `"bölüm bazında ortalama oee"` sorusunu
> **yanlış cube'dan** (`enerji_makine`) **doğru cube'a** (`oee`) taşıdı ve metrik bunu
> **göremedi** (+2). Bir araç ölçmesi gereken şeyi ölçmüyorsa, verdiği güven sahtedir.

**İLK DOĞRULUK BASELINE'I** (2026-08-02, ~10.800 tur, 4 şirket, `--network none`):

| Şirket | Tur | Erişim | **Doğru cube** |
|---|---|---|---|
| boyahane | 5240 | %64 | **3014/3738 (%80)** |
| atiksan | 1462 | %67 | **926/944 (%98)** |
| gulteks | 1618 | %62 | **912/957 (%95)** |
| gitas | 2479 | %67 | **1407/1586 (%88)** |
| **toplam** | | | **6259/7225 = %86,6** |

**FAZ D SONRASI ÖLÇÜM** (2026-08-02, aynı korpus — araç onarıldıktan sonraki ilk geçerli koşum):

| Şirket | Tur | Erişim | Doğru cube | Δ |
|---|---|---|---|---|
| boyahane | 5306 (+66) | %64 | 2996/3742 (%80) | **−18** |
| atiksan | 1462 | %67 | 926/944 (%98) | 0 |
| gulteks | 1618 | %62 | 910/955 (%95) | −2 (payda da −2) |
| gitas | 2479 | %67 | 1405/1584 (%88) | −2 (payda da −2) |
| **toplam** | | | **6237/7225 = %86,3** | **−%0,3** |

> **Faz D'nin ilan edilen hedefi (%64 → %80 erişim) TUTMADI ve bu açıkça kaydedilir.**
> Erişim %64'te kaldı. Faz D'nin gerçekte teslim ettiği üç şey başkaydı:
> (1) **ölçüm aracının kendisi onarıldı** — B1'den beri tavan hiç ölçülemiyordu (§6.4);
> (2) **sessiz-yanlış bir sınıf kapatıldı** (`_syn_hit`, takip yollarında alakasız GROUP BY);
> (3) **iki beyan gerçeğe döndü** (fan-out sertifikası artefakt+makbuz oldu, `consistency_k`
> tüketici kazandı).
>
> `−18`'lik düşüş Faz 0.4'te kayda geçen aynı takasın sınıfındandır: sahte alt-dizi
> eşleşmelerinin bir kısmı **tesadüfen doğru cube'a** düşüyordu. Soru-soru izole
> EDİLMEDİ — dürüst kayıt budur; nedensellik iddia edilmiyor, korelasyon ve sınıf
> benzerliği kaydediliyor. Boyahane'nin **+66 turu** Faz D1'in iki yeni mizan
> kırılımından gelir (hepsi cevaplanabilir).
>
> **Sonuç: kapsam tavanı Faz F/G'nin her aracını sınırlar.** ⟳ *(FAZ −1/A9: burada
> «hâlâ %64» yazıyordu — o turun sayısıydı ve **güncellenmemişti**; ölçülen `2a-3`
> sonrası **%68-72** bandı. `D2`: sabit sayı yerine komut → `lab/nl_corpus.py --kapi`.)* Tavanı yükseltmek `demo-boyahane`'de `expose:` yaymakla olmuyor (ölçüldü:
> kalan 20 ilişkinin hiçbiri ayırt edici yeni boyut vermiyor); asıl kayıp yerleri korpus
> raporunda görünüyor — `elektrik` sorularının `enerji_makine` yerine `surdurulebilirlik`e
> gitmesi (cube-kimliği çakışması) ve `ortalama duruş`un Discovery'ye düşmesi. Bunlar ayrı
> bir turun konusudur ve **kapsam değil, tahkim/katalog** işidir.

**En zengin katalog (boyahane, 13 cube) EN KÖTÜ.** Belirsizlik katalog büyüdükçe artıyor —
araştırmanın öngördüğü tam buydu (daha çok boyut → daha çok sinonim çakışması). Bu, Faz 1'in
boyut üretimini yaygınlaştırırken Faz 3.1'in (güven skoru + netleştirme) neden **ön koşul**
olduğunun sayısal kanıtıdır.

Baskın başarısızlık sınıfı ölçüldü: `"arıza duruşu"` HEM `bakim`'in ölçü sözlüğünde HEM
`oee.plansiz_durus_dakika` sinonimlerinde — ikisi de meşru. `_match_cube` çoklu-adayı
kıramıyor ve soru Discovery'ye düşüyor. **Kelimeye özel yama yapılmadı** (§5 disiplini:
kök nedeni düzelt, örneği değil); doğru çözüm belirsizlikte chip sormaktır.

**Ölçüm reçetesi** (üçü de `--network none` ile koşar):
```
docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python -m pytest -q
docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python -m eval.run
docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python lab/nl_corpus.py
```

**Düzeltilenler (2026-08-02):**
- ✅ `eval/run.py` artık **source-farkında**: `expect_source` (vaka başına katman denetimi),
  `by_path`/`by_source`/`deterministic_share` metrikleri, ve `test_eval_gate.py`'de ikinci bir
  kapı — *deterministik pay baseline'ın altına düşemez*. Önceden bir soru cube yolundan
  Discovery'ye kaysa precision ve coverage aynı kalıyordu, yani **regresyon sessiz geçiyordu.**
- ✅ `eval/run.py` artık `DIMA_VQR_EMBEDDER=off` set ediyor — "ağsız koşum" iddiası embedder
  indirmesi yüzünden doğru değildi.
- ❗ **Yanlış alarm düzeltmesi:** "CI kapısı kırık" değildi. `eval/report.json` **bayattı**
  (31 Tem, precision 0,9464); taze koşum baseline ile birebir örtüşüyor. Bayat artefakta bakıp
  karar vermeyin — `python -m eval.run` koşun.

**Hâlâ açık:**
- `route-distribution` endpoint'inin **hâlâ sıfır UI tüketicisi var** (KPI artık endpoint'in
  kendisinde hesaplanıyor ve testli, ama kimse göstermiyor).
- Anlamlı bir Intent/Discovery oranı için **gerçek kullanım** gerekiyor; telemetri artık
  kalıcı (Faz 0.1) ama tablo **gerçek kullanıcı trafiği taşımıyor**.
  > ⟳ **DÜZELTME (FAZ −1/A10+A11) — `D2` UYGULANDI: SABİT SAYI SİLİNDİ.**
  > Bu belge `interaction_log` için **üç farklı sayı** taşıyordu — *"7 satır"* (burası),
  > *"93"* (§6.13z) ve *"105"* (§6.3 ⟳) — ve **üçü de bayattı**: ölçüldü @`81ad10b`
  > → **0 satır** (ortam sıfırlanmış). Bir sayının üç kez yazılıp üçünün de yanlış olması,
  > `D2`'nin (*"canlı büyüyen sayı sabit yazılmaz, komutla verilir"*) ders kitabı örneğidir.
  > **Güncel değer:**
  > `sqlite3 backend/logs/control_plane.db "select count(*) from interaction_log"`
  > ⚠ **Ve sayı tek başına yeterli değil:** satırların *"gerçek kullanıcı mı, bizim
  > denememiz mi"* olduğu ayrılmalıdır — bu ayrımın kapısı **FAZ 8.1**'dir.

---

## 8. Belge otoritesi ve belgelenmiş çelişkiler

### 8.1 Hangi belgeye ne kadar güvenilir

| Belge | Statü |
|---|---|
| **`backend/MIMARI.md`** (bu) | **KANONİK · NORMATİF** |
| `backend/CLAUDE.md` | Kural indeksi. Bilinen bayat noktaları: LLM sağlayıcı listesi (`xai`/`gemini` eksik), `app/` ağacı (viz/drill/vqr/kpi/contracts/pii/channels/stats yok), `routers/` listesi (connections/dashboards/measures/stats yok), `packs/kaynak` listesi (`netsis` yok). |
| `Wren_Hibrit_GenBI_SaaS_Strateji.md` | **Mimari niyet belgesi — hâlâ geçerli.** Katman 5'i kelimesi kelimesine *"Semantic Compiler: Intent Query → SQL; **join graph**, metric math, RLS inject"*, §2.5 *"MDL graph'ta measure'ın model'inden dimensions'a **join yolu seçilir**"*. Yani join işi yeni bir yön değil, **strateji ile kod arasındaki boşluğun kapatılmasıdır.** |
| `HANDOFF_DOCS/*` | **Tarihsel kayıt. Normatif DEĞİL.** Ne zaman ne yapıldığını anlatır; #4 (küp-LLM stratejisi) bu belgeyle çelişen §3.1/§6.C teşhisleri içerir — **bu belge kazanır.** |
| `legacy/*` | Yeniden yazım öncesi. Yalnız `mimari-akis.md`'nin özdeyişi hâlâ doğru: *"LLM anlar (yapısal, kısıtlı) · Python doğrular+hesaplar · Motor sayıyı üretir · Chip'ler kullanıcıya son sözü verir."* |
| `backend/lab/panel/` | 4-model düşman denetimi. **⟳ FAZ 1.13 (2026-08-04) yeniledi:** aksiyon sayısı **47** ölçüldü (beyan doğru); durum **✅ 6 kapandı · ◐ 3 kısmen · ⊘ 2 · ⬜ 36 açık** ve her ✅ **kodla doğrulanıyor** (`tests/test_panel_tazeligi.py`, 19 test — yanlış bir *«kapandı»* iddiası KIRMIZI verir). Durumun **tek sahibi** `index.md`; `findings/*.md` **tarihsel kayıttır**, bilerek güncellenmez. Çürütülmüş iddialar da listelidir — **tekrar açma**. |
| `Dima-0-100-Gorev-Takip-Dosyasi (2).md` | **ÜRÜN şartnamesi. Mimari otorite DEĞİL** — §8.3. |

### 8.2 ADR'ler ~~fiziksel olarak YOK~~ — **DOSYALAR ÜRETİLDİ (FAZ 4.6)**

✅ **`backend/docs/adr/` İNDİ** — 20 dosya, kapı `tests/test_adr_dosyalari.py` (25 test).
Kodda anılan **her** kimliğin dosyası var ve **yeni bir kimlik dosyasız merge edilemez**.
Ters yön de kapalı: kodda **hiç anılmayan** bir kimliğe dosya yazmak da reddediliyor
(kapının kendisi bir kayıt-uydurma aracına dönüşmesin diye).

🔴 **Dosyalar REKONSTRÜKSİYONDUR ve her biri bunu kendi başında İLAN EDER.** Çelişkide
**kod kazanır**. *Var olmayan bir belgeye atıf yapmak bir eksiklikti; onu uydurulmuş bir
tarihle doldurmak bir sahtekârlık olurdu.*

⚠ **ADR-0023 atıfsızdı** ve bu ölçüldü: karar `packs/modul/enerji/` yorumlarında ve
`test_yeni_kup_kapisi.py`'de **yaşıyordu** ama kimliğiyle hiçbir yerde anılmıyordu. Atıf,
kararın **yaşadığı yere** eklendi — kaydı meşrulaştırmak için değil, kayıt ile kodun
birbirini doğrulayabilmesi için.

⚠ **Kayıt kodun ~2 faz gerisinde:** en yüksek kimlik `ADR-0024` ve ondan sonra inen
faz-düzeyi kararların (grain sözleşmesi · çekirdek katman · kapsam merceği · mali takvim
· sahiplik hakemi · Ossie · MCP) ADR'si **yok**. Bu bir borçtur, `OPERASYON-DURUM.md`'de.

<details><summary>Rekonstrüksiyonun kaynağı (aşağıdaki tablo) — dosyalar buradan türetildi</summary>

#### ~~8.2 ADR'ler fiziksel olarak YOK~~ *(FAZ 4.6 öncesi ölçüm — kayıt için korundu)*
Kodda **20 farklı ADR kimliği** ~250 kez atıf alıyor (0003, 0004, 0005, 0007–0012, 0014–0024;
0001, 0002, 0006, 0013 hiç kullanılmamış). `docs/adr/` dizini **ne diskte ne git geçmişinde var**.
Bir ADR'ye atıf gördüğünde kaynağı arama — **kodun kendisi ve bu belge tek kanıttır.**

Rekonstrüksiyon (atıf bağlamlarından türetildi; başlıklar alıntı değil):

| ADR | Karar | En güçlü kanıt |
|---|---|---|
| 0003 | Dağıtım topolojisi: `cloud_direct` \| `agent` \| `api_sync` | `control_plane/models.py` |
| 0004 | Deterministik-önce yönlendirme + golden-set/eval regresyon ağı | `cube_router.py` docstring, `eval/run.py` |
| **0005** | **Kompozisyon**: şirket ⊕ sektör ⊕ modül → derlenmiş wren-projesi. **İçerik YAML'da, kod generic.** | `app/compose.py` |
| 0007 | Konuşmaya dayalı BI + sohbet kalıcılığı. K3: dönem eksikse **SOR**, sessizce tüm-zaman alma | `routers/conversations.py` |
| **0008** | **"Anlamadığını bil"** — tek tanınmayan kelime ⇒ cevap yok **ve öneri yok**. K3: **LLM tarih hesaplamaz** (Python takvim aritmetiği). Disiplin: **refleksle yeni regex ekleme** | `cube_router.py`, `value_index.py` |
| 0009 | Feature flag: global ⊕ sektör ⊕ şirket ⊕ DB override, en spesifik kazanır. **Bayrak ≠ yetki** | `app/features.py` |
| **0010** | **Query Contract**: SQL + MDL sürümü + parametre + sonuç hash'i, Postgres'te tek kaynak | `app/contracts.py` |
| 0011 | Birleşik bildirim/teslim kanalı mimarisi | `app/channels.py`, `app/schedules.py` |
| 0012 | Canlıya alma / hosting topolojisi | `backend/README.md:163` |
| **0014** | Kimlik/yetki: her kimlik özniteliği **token'dan** türer. K6: **her veri erişimi kanıtlanabilir iz bırakır** (KVKK). Audit satırı yazılmadan başarı raporlanmaz | `control_plane/authorize.py`, `app/audit.py` |
| **0015** | **Ayrı admin düzlemi**: farklı süreç, farklı JWT secret çifti, zorunlu 2FA. K1: ortak auth kodu `control_plane/`'de | `admin_app/main.py` |
| 0016 | **DB→dosya tek yönlü** materializer | `app/materialize.py` |
| **0017** | **Kaynak-sistem pack facet'i**: ERP parmak izi (logo-3/mikro-v16/netsis), canlı introspection, lehçe çevirisi. §9: generic clone/sync motoru | `app/compose.py`, `admin_app/clone/` |
| **0018** | **Sinonim mimarisi 3 katman**: pack YAML ⊕ arketip ⊕ **canlı öğrenilen overlay (additive, asla silmez)**. Evrensel kural: **LABEL ⊆ SYNONYM**. Adaylar otomatik canlıya çıkmaz | `app/synonyms.py`, `SynonymOverride` |
| 0019 | Her yerde soft delete (`deleted_at`) | `control_plane/models.py` |
| 0020 | **Sessiz yutma yok** — sistem/app logger + `interaction_log` | `app/logging_setup.py` |
| 0021 | Chat-scoped Excel/CSV → oturum DuckDB → oto-cube → tüm pipeline bedava | `app/dataset.py` |
| 0022 | **Deterministik evrensel çıktı yorumu** — LLM aritmetik yapmaz | `app/interpret.py` |
| 0023 | **Yeni cube kapısı**: yazılı gerekçe + başka modülün grain'ini çalmama | `packs/modul/enerji/` yorumları |
| **0024** | **Görselleştirme kararı deterministik ve backend'e ait** (Show-Me / Cleveland-McGill) | `app/viz.py`, `app/report.py` |

</details>

✅ **§4 KAPANDI — ajan yazma yasağı KADEMELENDİ** (FAZ 6.0 · 6.1 · 6.2 @`8bc2be2`):

| adım | ne indi |
|---|---|
| **6.0** | 🔴 `D9` **ters uygulanmıştı**: kapsam içi + geri alınabilir iş artık **istemsiz** koşuyor (`eylem.d9_istemsiz_mi`) |
| **6.1** | `app/onay_akisi.py` — kapalı durum makinesi · **30 dk** süre aşımı · riske göre yönlendirme · **istem oranı telemetrisi** |
| **6.2** | `app/yazma_araclari.py` — `yan_etki="yazar"` ile kayıtlı **ilk üç** araç |

🔴 **DEĞİŞMEZ GEVŞEMEDİ, KADEMELENDİ.** Üç şart birden: (a) bayrak kapalıyken araçlar
kayda **HİÇ GİRMEZ** (*geri alma "kapatmak" değil **hiç açmamaktır**;* kayda giren bir
araç, bir gün unutulacak bir engelin arkasında durur), (b) her yazma aracı
`geri_alma_ref` **taşır ya da geri alınamazlığını AÇIKÇA söyler**, (c) yalnız
**onay akışı** üzerinden çağrılabilir. `tests/test_arac_kaydi.py::test_ajan_YAZAMAZ`
**ters çevrildi** ve üçünü birden kilitliyor.

⚠ `schedules.create` **geri alınamaz** ve bu **gizlenmiyor**: kayıt silinse bile
gönderilmiş bildirim geri çekilemez.

### 8.3 `Dima-0-100` dosyasının sınırları

**İyi bir ÜRÜN şartnamesi** (240 görev, 19 faz, 361 kabul testi, ticari model, KVKK gerekçesi).
**Mimari otorite değil**, üç somut sebeple:

1. **Kavramsal çerçevesinde sorgu-anı join yok.** 240 görevin hiçbiri bunu içermiyor; `1.11c`
   açıkça *"cube tanımında join yolu sabitlensin"* diyor, `1.11b` çapraz-cube'u **aritmetik formül
   DSL**'i sanıyor. Oysa dosyanın amiral özelliği `4.8` (kök-neden ayrıştırma)
   *zaman → kategori → müşteri → kanal* gezmeyi gerektiriyor ve `4.3` araçlara serbest SQL'i
   yasaklıyor → **en değerli özellik, yazılmamış bir kısıtla tavanlı.**
2. **Faz numaralandırması ikiye ayrılmış.** Dosyanın *FAZ 4 = Agentic Analiz = %72* ile ekibin
   "faz 4 tamamlandı"sı **aynı şey değil** (ekibinki dosyanın FAZ 1/2 kalemlerinin bir kesiti).
   İkisini birlikte okuyan ürünü %72'de sanır. **Değil** — dosyanın FAZ 3, 3B, 5, 6, 6B, 8B, 9+
   fiilen sıfır uygulama. Ayrıca dosyada **hiçbir kutu işaretli değil** (PDF→MD dönüşümünde
   kayboldu); gerçek durum yalnız HANDOFF'lar ve git geçmişindedir.
3. **Teknoloji yığını uyuşmuyor ve bu hiçbir yerde karar olarak kayıtlı değil.**

| Plan diyor | Gerçek |
|---|---|
| NestJS/TypeScript ana backend + Python/FastAPI Wren sarmalayıcı | **Tek Python/FastAPI** |
| Redis · Vault · BullMQ · Temporal · Debezium · LangGraph · Novu | **Hiçbiri yok** |
| Vega-Lite (backend chart spec üretir, gerekirse LLM) | **ECharts + deterministik `viz.py`** (ADR-0024; kod okunarak alınmış bilinçli ters karar) |

✅ **§13 KAPANDI** (FAZ 5.11 · 5.12 @`9006e66`): görsel dilbilgisi iki yönden
genişledi. **5.11** — *"ne zaman grafik ÇİZİLMEZ"*: dört **daraltıcı** kural (≤2 satır
veya ≤3 kategori → cümle · >20 sıralanmamış kategori → tablo · finans cube'u → tablo),
yalnız **varsayılan `bar`**'a uygulanır ve gerekçesi (`cizilmedi`) **kullanıcıya
gösterilir**. **5.12** — dönüş sözleşmesi **`VizSpec | list[VizSpec]`**: paket her
üyesiyle *"neden bu eksende"* gerekçesini taşır, azami **3** üye, ve §15.6'nın
*"çizilmez"* kararını **ezmez**. 🔴 **Tekil dönüş her zaman geçerli** — kapı bunu
kilitliyor (`tests/test_icgoru_paketi.py`, 12 test).
| Kimlik bilgisi için Vault | **AES-256-GCM + `DIMA_CRED_KEK` env** |
| WebSocket | **`threading.Thread` + HTTP polling** (WebSocket bilinçli ertelendi) |

---

## 9. Hedef mimari — nereye gidiyoruz

Yol haritasının bittiği andaki resim (uygulama planı: `~/.claude/plans/` — bu belge *ne* olacağını
anlatır, *nasıl*ını değil):

```
Soru
 └─▶ route()  →  CubeQuery, ya da KANITIYLA BİRLİKTE bir red
        ├─ çözüldü        → source=cube            (0 token)
        ├─ kanıt EŞİT     → NETLEŞTİRME CHIP'İ     ← belirsizlik en İYİ kararı tetikler
        ├─ kanıt ZAYIF    → Intent-JSON            → source=cube+llm
        └─ kanıt YOK      → Discovery              ← istisna, ve her biri bir terfi adayı
                        └─▶ terfi kuyruğu → YAML diff → insan onayı → pack'e PR

Cube boyutları = kendi base_object'i
               ⊕ ilişki grafiğinden MEKANİK türetilmiş boyutlar
                 · yalnız MANY→ONE · ≤2 sıçrama
                 · FAN-OUT SERTİFİKALI (ölçülmüş tekillik, MDL sürümüne mühürlü)
                 · provenance taşır: {model, kolon, ilişki, hop, doğrulama_tarihi}

Her cevap → yeniden çalıştırılıp hash eşlenebilen bir MAKBUZ
```

> **Neden skaler bir `confidence` YOK** (bu diyagram Faz 3.1'de düzeltildi): merdivenin karar
> noktaları ayrıktır ve her biri **karşılaştırılabilir bir kanıta** dayanır (eşleşen sinonimin
> uzunluğu, adaylar arası fark). Bu kanıtı 0–1 arası bir sayıya sıkıştırmak aynı kararı verir
> ama **gerekçesini gizler** — ve kalibre edilmediği sürece o sayı bir güven değil bir süstür.
> Query Contract'ın varlık sebebi denetlenebilirlikse, eşik de denetlenebilir olmalıdır.

Dört ilke:
1. **Kapsam, zekâdan önemlidir.** Semantic layer'ın tek hata modu kapsamdır (dbt'nin kendi
   benchmark'ı: kapsam içinde %100, "çok fazla entity hop" kategorisinde %0). Kapsamı büyütmek
   mekanik bir üretim işidir — planlayıcı zekâsı değil.
2. **Belirsizlik netleştirme doğurur, düşüş değil.**
3. **Güvenlik ölçülür, beyan edilmez.** Fan-out sertifikası build artefaktıdır ve Query Contract'a
   geçer.
4. **Discovery bir hata değil, bir sinyaldir.** Her Discovery cevabı bir kapsam boşluğunun
   belgesidir; sistem kullandıkça ucuzlamalıdır.

### 9.1 Dünyada ilk olacak parçalar — "süs" sanılıp budanmasın
Rakip araştırması bunları **bulamadı** (satıcı dokümanları taranarak):
- ✅ **Ölçülmüş fan-out güvenlik sertifikası** build artefaktı olarak — **uygulandı**
  (2026-08-02, Faz D2: `app/fanout.py`, `target/fanout_certificate.json`, `python -m app.fanout`).
  Snowflake, Cube, LookML, MetricFlow — hepsi modelciye *beyan ettiriyor*, sonra sonuçlarına
  karşı savunma yapıyor; Databricks açıkça *"runtime'da doğrulanmaz"* diyor.
  Ölçüm zaten vardı ama **yalnız test koşumu içinde doğup ölüyordu** — iddia karşılıksızdı.
  Zincir artık uçtan uca: `relationships.yml` → `certify()` (fan-out · NULL · öksüz) →
  artefakt → `schema()` `dimension_origin[*].certified` damgası → `contract_log.provenance_json`
  (makbuz). Regresyon testi de artık kendi SQL'ini yazmaz, **aynı fonksiyonu** çağırır.
  İki tasarım kararı: (a) `schema()` sertifikayı yalnız **OKUR**, ölçmez — ölçüm 62 `COUNT`
  sorgusudur ve Faz B1'in `schema()` kazancını geri verirdi; (b) artefakt yokken damga
  `"olculmedi"`dir, sessiz *"sağlıklı"* değil — ölçülmemişi temiz göstermek olmayan bir
  garantiyi rozetlemek olurdu. Demo ölçümü: **31 ilişki · 31 ölçüldü · 0 riskli.**
- **Doğrulanabilir makbuz olarak Query Contract** (SQL + MDL sürümü + parametre + sonuç hash'i +
  join sertifikası + `always_filter` parmak izi). BI'da kimse üçüncü tarafın yeniden çalıştırıp
  hash eşleyebileceği bir makbuz vermiyor.
- **Güven-kapılı merdiven + risk-kapsam eğrisi.** Hiçbir sevk edilmiş BI ürünü abstention kapısı
  ya da risk-kapsam eğrisi yayınlamıyor.
  ✅ **EĞRİ YAYIMLANDI** (FAZ 4.2 @`71c1da5` · `python lab/risk_kapsam.py`): dört şirket,
  `lab/reports/risk_kapsam.md`. Eğri **skaler bir `confidence` üstünde DEĞİL**, ayrık
  kapılarımız üstünde tanımlı (`route → tie_chip → intent → discovery`) ve her nokta bir
  **determinizm sınıfı** taşır. ⚠ `hata_orani` **bilerek YOK** — bir kapının hata oranını
  bu araç ölçemez, yazsaydık uydurma olurdu. ⚠ `intent`/`discovery` LLM'siz koşumda
  **ölçülemez** ve `llm_gerekli` kovasında toplanır: *ölçülmeyeni bir kapıya yazmak, eğriyi
  olduğundan iyimser gösterirdi.*
- ✅ **CubeQuery olarak ifade edilmiş katkı/mix ayrıştırması** — **uygulandı** (2026-08-02,
  Faz 5.1+5.2: `app/contribution.py`, `POST /ask/contribution`). Snowflake `TOP_INSIGHTS`,
  Power BI Key Influencers, Tableau Pulse — hepsi semantic layer'ın **dışında**, dolayısıyla
  sonuçları yeniden-tarihlenebilir/kırılabilir/sözleşmeli değil. Burada **her bulgu kendi
  başına bir CubeQuery**: tıklanır, `/cube` ile LLM'siz koşar, kendi Query Contract'ını üretir.
  Üç kural bunu bir kopya olmaktan çıkarıyor:
  - **Toplanabilirlik kapısı.** Katkı payı yalnız toplanabilir ölçülerde TANIMLIDIR; `AVG`/oran/
    `COUNT(DISTINCT)` için parçaların toplamı bütünü vermez ve *"bu segment değişimin %40'ını
    açıklıyor"* cümlesi **matematiksel olarak yanlış** olur. Bu, bu araç sınıfının klasik sessiz
    hatasıdır. Kapı ada değil **kanıta** bakar (cube'un `additive:` beyanı → ölçü ifadesi) ve
    kapının kendisi **veriyle** sınanır (`test_toplanabilirlik_KANITLI`).
  - **İki ayrı pay.** Segmentler birbirini götürebilir (+100/−100 → net 0 ama hikâye var):
    `net_pay` net ~0 iken **None** döner (uydurulmaz), `brut_pay` her zaman tanımlıdır.
  - **PVM eşleştirmesi beyan edilir, tahmin edilmez.** `ciro/kg` gerçek bir TL/kg fiyatıdır;
    `tutar/fatura_sayısı` fiyat değil ortalama fatura büyüklüğüdür. Ayrım bir **içerik**
    bilgisidir; ad kalıbından çıkarmak §5'in yasakladığı yamadır ve yanlış eşleştirme
    **güvenle yanlış ekonomi** üretir. Ayrışma artıksızdır: fiyat+miktar+birleşik = ΔV birebir.
- **"LLM ham değer görmez"in zorlanmış ve tasdik edilmiş hali** (yalnız sorgu üretiminde değil,
  anlatımda da).
- **İngilizce olmayan bir dilde ilk yayınlanmış kapsam/doğruluk eğrisi.** Türkçe cezası ölçülmüş
  durumda (BIRDTurk, SIGTURK 2026: doğrudan istemde −15,05 puan, agentic ayrıştırmayla −11,87;
  ayrıştırma Türkçeye İngilizceden **2,2× daha çok** yarıyor) ama semantic layer katkısı Türkçede
  **hiç ölçülmemiş**.

### 9.2 Kabul edilen yapısal sınırlar (belgelenir, çözülmez)
- **Rol-oynayan boyut yok.** Handle adı hedef model adına eşit olmak zorunda → (kaynak, hedef)
  çifti başına en fazla 1 ilişki. Fatura-adresi/sevk-adresi, alıcı/satıcı cari, sipariş/sevk
  takvimi ikisi birden ifade edilemez. Üreteç bu durumu **tespit edip uyarmalı**, sessizce birini
  seçmemeli.
- **Ölçü-A × Ölçü-B tek CubeQuery'de olamaz** — o `blend` işidir. Join, *ölçü-A × boyut-B*'yi
  çözer; *ölçü-A × ölçü-B*'yi değil.

  > ⟳ **FAZ B1 — FAZ 4'ÜN KABUL ÖLÇÜTÜ BU SATIR YÜZÜNDEN YANLIŞ YAZILMIŞTI.** Planın pilot
  > örneği *"personel bazlı verimlilik"* (ölçü `oee`'den, boyut başka cube'dan) ve ölçüldü:
  > pilot hiçbir şey üretmiyor. Ama **sebebi yapısal değil KATALOGSAL**: join bu şekli
  > çözer — `oee`'de **personel boyutu bilinçli olarak YOKTUR** (HANDOFF #4 §3.3). Yani
  > soru *"ifade edilemez"* değil, *"bu katalogda karşılığı yok"*.
  >
  > ⚠️ Planda önce *"ölçü + başka cube'un BOYUTU ne tek CubeQuery'de ne iki adımda ifade
  > edilebilir"* diye yazmıştım — **bu satırla çelişiyordu ve yanlıştı**; bu turda altıncı
  > kez kendi beklentim kusurlu çıktı. MIMARI'yi okumadan olmayan-hedef yazmak, tam da bu
  > belgenin var olma sebebini çiğnemek olurdu.
  >
  > **Faz 4'ün DÜZELTİLMİŞ kabul ölçütü** — mimarinin gerçekten desteklediği şekil:
  > **ölçü + ölçü**, **ekleme niyetiyle**, **TAKİPTE**. `cross_cube_add`'in kendi
  > sözleşmesi budur (*"q ekleme-niyeti içermeli"*) ve canlıda ölçüldü:
  > `bu yıl makine bazında oee` → *"bir de fire ekle"* → `measures=['ort_oee',
  > 'toplam_fire_kg']`, 11 satır, whitelist tuttu.
  >
  > **Fresh soruda pilot çalışamaz** ve bu da yapısaldır: pilot `route(tüm soru)`'nun bir
  > taban üretmesini bekler, iki ölçülü bir fresh soru ise route'ta **R1/R10** verir.
  > Kompozisyonun doğal evi **takip yolu**dur (`deterministic_refine`), fresh yol değil.
- **View'lar ilişkilere katılamaz** — bir cube'un join alabilmesi için `base_object`'i **model**
  olmalıdır.
- **Bileşik anahtarlı ilişkiler ifade edilemez** (MDL `condition` tek kolonludur) → `enerji_tesis`
  gibi vakalar meşru view kullanımıdır.

---

## 11. Agentic katman sözleşmesi (Faz F1 — araç kaydı kuruldu)

> **Tez:** *Agentic katman, temelin ne ise onu ÇARPAR.* Bir insan `/ask/drill action="raw"`
> yolunu yılda bir kez bulur; 15 araçlı bir planlayıcı onu **ilk gün** bulur ve her gün
> kullanır. Bu yüzden ajan yüzeyi serbest fonksiyonlar üstüne değil, **beyan edilmiş bir
> kayıt** üstüne kurulur.

### 11.1 Araç kaydı (`app/tools.py`)

Kayıt **hiçbir yeteneği yeniden uygulamaz** — var olan fonksiyonu *işaret eder*. Gövde
kopyalamak bu depoda defalarca sapmayla sonuçlanmış bir desendir (`drill.flag_outliers` ↔
`schedules.detect_anomalies`, `interpret._fmt` ↔ `schedules._fmt_deger`, `_uncovered` ↔
`_syn_hit`); agentic ölçekte aynı hatanın bedeli çarpılırdı.

Her araç şunları **beyan eder**: ad · özet · girdi şeması · çıktı · **determinizm** ·
maliyet sınıfı · **yan etki** · **izin** (`authorize()` aksiyonu) · **ürettiği makbuz** ·
bağlanma biçimi (modül fonksiyonu / servis metodu) · sınırlar.

`baglanma` alanı olmasa kayıt yalan söylerdi: bazı yetenekler modül fonksiyonu **değil**,
istek-kapsamlı bir servisin metodudur (`WrenService.cube_sql`, LLM sağlayıcısının
`select_cube`'ü). Onları modül seviyesinde "çözülmüş" göstermek hangi tenant'ın motoruna
gidildiğini gizlerdi.

### 11.2 Planlayıcının uyacağı beş değişmez

| Değişmez | Nasıl uygulanıyor | Nasıl denetleniyor |
|---|---|---|
| **Ajan kullanıcının yetkisini AŞAMAZ** ✅ | Her araç bir `authorize()` aksiyonuna bağlı; `izinli_araclar(principal)` matristen süzer — kayıt ikinci bir kopya TUTMAZ. ✅ **FAZ 1.3 İNDİ (2026-08-04):** 15/15 `query:run` → **beş aksiyon** (`query:run` 7 · `drill:run` 2 · `contribution:run` 2 · **`contribution:scan` 1** · `llm:invoke` 3). Süzgeç artık **no-op değil**: `contribution.report` (maliyet **`pahali`**, 6 boyut tarama) viewer rütbesinin **dışında**. ⚠ Diğer dördü bilinçle **rütbe 0** — granülerlik eklendi, **davranış kıpırdamadı** (KURAL B) | `test_izin_MATRISTE_var`, `test_IZIN_GRANULER_tek_anahtar_DEGIL`, `test_PAHALI_ARAC_VIEWER_RUTBESINDE_DEGIL`, `test_RUTBE_0_ARACLARDA_DAVRANIS_BIREBIR_AYNI` |
| **Ajan YAZAMAZ** | `yan_etki="yazar"` bir araç kayda **hiç alınmadı** | `test_ajan_YAZAMAZ` |
| **Ajan ham veri GÖRMEZ** | `drill.raw` bilinçle kayıt DIŞI (T1/T2 sınırının en hassas yaprağı) | `test_ham_satir_araci_KAYITTA_YOK` |
| **DETERMİNİSTİK-ÖNCE** | Her LLM aracının aynı etiketi taşıyan deterministik bir kardeşi olmalı; planlayıcı önce onu denemek zorunda | `test_her_LLM_aracinin_DETERMINISTIK_alternatifi_var` |
| **Her adım bir MAKBUZ üretir** | `makbuz` alanı; veriye dokunup makbuz üretmeyen aracın gerekçesi zorunlu | `test_makbuz_beyani_TUTARLI` |

**Kayıtta görünmeyen şey, planlayıcının erişemediği şeydir.** Bu yüzden dışarıda
bırakılanlar da beyan edilir (yazan araçlar · `drill.raw` · `vqr.recall`) — "unutuldu" ile
"bilinçle kapatıldı" ayrımı kaydın güvenilirliğinin tamamıdır.

### 11.3 Kayıt ÜÇ yüzeyin ortak kaynağıdır

**LLM'e verilen araç listesi** (`llm_araclari`) · **MCP adaptörü** (ileride ince bir
çevirici; kendi kaydını KURMAZ) · **yetki matrisi bağı**. Üçü ayrı yazılsaydı zamanla
ayrışırlardı — bu depoda o desenin bedeli ölçüldü.

LLM'e giden **açıklama metni determinizm ve maliyeti İÇERİR**: planlayıcı ucuz/deterministik
olanı tercih edebilsin diye. Gizlenirse *"önce deterministik"* bir kural değil bir temenni
olur.

### 11.3b Yetki granülerliği — FAZ 1.3 ✅ *(2026-08-04, `f847e33` sonrası)*

| İzin | Rütbe | Araçlar | Neden bu rütbe |
|---|---|---|---|
| `query:run` | 0 | `route` · `deterministic_refine` · `cube_sql` · `interpret` · `viz.recommend` · `cross_cube_add` · `yoy.compute` | ürünün kalbi; maliyet `sifir`/`ucuz` |
| `drill:run` | 0 | `drill.expand` · `drill.select` | çekirdek okuma, maliyet `sifir` |
| `contribution:run` | 0 | `contribution.decompose` · `contribution.pvm` | deterministik, maliyet `ucuz` |
| **`contribution:scan`** | **1** | **`contribution.report`** | 🔴 maliyet **`pahali`** — 6 boyut tarama |
| `llm:invoke` | 0 | `llm.prompt_enhance` · `llm.anlat` · `llm.select_cube` | ⚠ aşağıdaki karara bakınız |

🔴 **TEK BİR DAVRANIŞ DEĞİŞİKLİĞİ, ve o da yol haritasının KAPI'sının adıyla istediği:**
*"viewer rolü `contribution.report` (maliyet `pahali`) çağıramıyor."* Diğer dördü **rütbe 0**,
yani `query:run`'ı olan herkes onlara da sahip → **birebir aynı davranış** (KURAL B).

⚠ **`llm:invoke` neden 0 — ve bu bir karar, bir ihmal değil.** LLM araçlarını analyst+
yapmak bir **güvenlik** değil bir **ÜRÜN** kararıdır (viewer'ın cevabı küple sınırlanır) ve
bu madde onu vermek için kurulmadı. Aksiyonun **var olması** yeter: ajan araç listesi artık
dürüst ve sıkılaştırma **tek satırlık** bir karara indi. Rütbe, LLM maliyeti ölçüldüğünde
(FAZ 0.17 gecikme bütçesi + kota telemetrisi) yeniden ele alınır.

⚠ **ERİŞİLEBİLİRLİK DÜRÜSTÇE:** üründe bugün yalnız `owner` kullanılıyor (`CLAUDE.md`:
*"rol matrisi uykuda"*), yani bu düzeltmenin **bugünkü kullanıcıya etkisi sıfırdır**.
Kapatılan şey bir açık değil, bir **değişmezin uygulanabilirliğidir** — roller açıldığı gün
ayrım **zaten** yerinde olur. Sonradan eklenen bir sınır, o güne kadar üretilmiş her
alışkanlığı geriye dönük kırar.

⚠ **`metric:certify` bilinçle EKLENMEDİ.** Yol haritası onu 1.3'ün `NE`'sinde anıyor ama
sertifikasyon **FAZ 1.5**'in işi ve henüz yok. Karşılığı olmayan bir aksiyonu matrise
yazmak, bu deponun avladığı *"beyan var, kod onu tanımıyor"* sınıfını **kapanın kendi
içinde** üretirdi.

### 11.4 Ölçülen sınır (dürüst kayıt)

`select_cube` **her sağlayıcıda YOKTUR**: anahtarsız `RuleBasedSqlGenerator` onu taşımaz ve
üretim yolu `hasattr` ile denetler. Planlayıcı bunun yokluğunu bir hata değil bir **yol
kapalı** sinyali saymalıdır. Bu, kayıt yazılırken keşfedildi ve aracın `notlar`ına yazıldı.

### 11.5 Planlayıcı çekirdeği (F2 — `app/planner.py`) ✅

**Ölçüldü:** `grep -rn "budget|max_steps|token_limit" app/` → **boş**. Sıfır bütçe tavanı,
sıfır plan kaydı. Şartname 4.16 bir bütçe istiyordu; hiç yoktu.

> **Bu modül bir ReAct döngüsü DEĞİLDİR** ve bilinçli değildir. *"Hangi adımı seçeyim"*
> kararı telemetriyle kalibre edilmeli (Faz E-1) ve telemetri bugün **boş**. Ölçülmemiş bir
> kararı LLM'e devretmek, bu turda altı kez ölçülen *"beyan var, kanıt yok"* sınıfının en
> pahalı örneği olurdu.
>
> **Planlayıcı zekâsı olmadan yönetişim işe yarar. Yönetişim olmadan planlayıcı zekâsı
> tehlikelidir** — sınırsız bir döngü, denetlenmeyen bir yetki, izlenmeyen bir maliyet.
> Sıra bu yüzden böyle.

**Dört kapı** — her araç çağrısı sırayla geçer:

| Kapı | Ne yapar |
|---|---|
| **Kayıt** | Araç `app/tools.py`'de yoksa red — planlayıcı araç **uyduramaz** |
| **Yetki** | `izinli_araclar(principal)` dışındaysa red — ajan kullanıcının yetkisini **aşamaz** |
| **Deterministik-önce** | Deterministik kardeşi **denenmeden** LLM aracı seçilemez |
| **Bütçe** | adım · süre · sorgu tavanı |

**Bütçe aşımı = DÜRÜST KISMİ CEVAP.** Tavan aşıldığında koşum **sessizce kesilmez**: o ana
kadarki adımlar geçerlidir ve `truncated` + `truncation_reason` ile makbuza yazılır —
`contribution`'ın `kirpilan_segment`'iyle **aynı desen**. `truncated` alanı **her zaman**
yazılır (False olsa bile): *"kısılmadı"* ile *"kısılma sorulmadı"* farklı şeylerdir.

**Başarısız adım da kaydedilir.** Sessizce kaybolan bir adım, yapılmamış bir adım gibi
okunur ve koşumun maliyeti anlaşılmaz olur; bütçe zaten tüketilmiştir.

`token` ekseni **ölçülemediği için sınırsızdır** (telemetri boş). Ölçülmemiş bir eşik
koymak, kapsamı gerekçesiz daraltmak olurdu; alan şimdiden var ki telemetri gelince
**kod değil yalnız değer** değişsin.

**Yazarken kendi testimin yakaladığı kusur:** deterministik-önce kapısı araç **adlarını**
etiket kümesine karşı sınıyordu ve `route` çalıştıktan **sonra bile** reddediyordu.
Kapının yanlış-pozitifi, kapının olmamasından **kötüdür**: meşru bir merdiven basamağını
kapatır ve kural *"işe yaramıyor"* diye sökülür.

### 11.6c Kompozisyon planlayıcıdan geçiyor (F3) ✅

Konuşma yolu (G1) artık bir `Planlayici` kurar (`Butce(adim=6, saniye=20, sorgu=8)`) ve
**kullanıcının kimliğini** ona verir — ajan yetkiyi aşamaz. Kayıtlı araçlar **dört kapıdan**
geçer ve adım makbuzu üretir. Koşumun özeti cevabın **izinde** görünür:
*"Ajan koşusu: N adım · M sorgu"* (kısıldıysa gerekçesiyle) — maliyet gizli kalmaz.

**`dis_adim` itirafı kalktı — çünkü sebebi ortadan kalktı.** Önceki tur katkı ayrıştırmasını
`gated: false` diye işaretliyordu: kayıtlı tek bir araç değildi, çünkü gövdesi
`/ask/contribution`'ın **router fonksiyonunun içindeydi** ve HTTP'ye yapışıktı (`request`,
`_service_for`, `_drill_record_contract`). İtiraf doğruydu; asıl çözüm gövdeyi ayırmaktı.

`app/contribution.py::arastir()` ile ayrıldı. Ölçülen iki kazanç:

1. **Kayda girebildi** (`contribution.report`, `maliyet="pahali"`) — dört kapıdan geçiyor,
   kendi adım makbuzunu üretiyor. Router **ince bir sarmalayıcıya** düştü ve testle
   kilitlendi: kendi boyut tarama döngüsünü yazamaz
   (`test_uyari_neden.py::test_ROUTER_govdeyi_KOPYALAMAZ`).
2. **Arka plan işleri onu çağırabildi.** `request` olmayan hiçbir yol bu motora
   erişemiyordu — zamanlanmış uyarının *"neden"* eki tam olarak bu yüzden yoktu (§11.6e).

`dis_adim()` API'si **kalır**: gerçek kayıtsız adımlar için itiraf mekanizması hâlâ doğru
şeydir. Bugün tüketicisi yok, ve bu bir eksiklik değil bir olgudur.

### 11.6e Uyarı artık NEDENİNİ de söylüyor (F3 kompozisyonu) ✅

Planın F3 tablosundaki son açık satır: `schedules.check_alert → contribution → dispatch`.

**Ölçülen boşluk:** uyarı `⚠ fire takibi: eşik ihlali — M-07: 45 (> eşik 30)` diyordu ve
orada bitiyordu. **NE olduğunu söylüyor, NİYE olduğunu söylemiyordu** — oysa cevabı üretecek
motor elimizde duruyor ve `/ask`'te *"bu neden böyle?"* sorusuna zaten cevap veriyordu.

`schedules.uyari_nedeni()` kompozisyonu kurar. Dört karar kayıtlıdır:

| Karar | Gerekçe |
|---|---|
| **Yalnız ihlalde koşar** | Rutin raporda boyut taraması, kimsenin sormadığı bir soruya para ödemektir (`arastir` maliyet sınıfı `pahali`) |
| **PII fail-closed** (`satir_donustur=mask_rows`) | Bildirimin kime ulaşacağı ÖNCEDEN BİLİNEMEZ (dağıtım listesi · bell · push) — `principal` bypass'ı YOK. `run_schedule`'ın ana sonuçta uyguladığı disiplin; atlanırsa Faz A2'de kapatılan sızıntı sınıfı arka kapıdan geri açılırdı |
| **Tıklanabilir `cube_query` TAŞINMAZ** | Maskelenmiş bir değere (`ahm**@***`) filtre kuran sorgu **boş döner**; "tıkla" deyip boş sonuç vermek hiç tıklatmamaktan kötüdür. Kanıt yolu bildirimin `contract_id`'sidir |
| **Boyut sınırı `/ask`'ten dar** (6 → 2) | Arka plan işi; 60 sn'lik scheduler penceresi paylaşımlı. Sınır **sessiz değil**: `taranmayan_boyut` bildirimde görünür |

**Dürüst red korunur:** katkı ayrıştırması yalnız TOPLANABİLİR ölçülerde tanımlıdır. `AVG`/
oran için neden ÜRETİLMEZ ve **nedeni söylenir** — boş bir sessizlik değil.

**Yüzeyler:** `NotificationEvent.neden` → e-posta (HTML **ve düz metin**, ikisi aynı bilgiyi
taşır) · in-app bell (`notification_log.neden_json`, ayrı kolon — teslim TELEMETRİSİ ile
cevabın İÇERİĞİ farklı şeylerdir) · `NotificationsPanel`'de katlanır `⤵ neden?` katmanı,
**yeni panel değil** (§14.1). 19 test: `tests/test_uyari_neden.py`.

### 11.6d ⟳ FAZ 4: plan SEÇİMİ ARTIK VAR — `Planlayici.sec()` ✅

> **BEYAN GÜNCELLENDİ (2026-08-03).** Eski metin: *"Plan **SEÇİMİ** (hangi araç, hangi
> sırayla — **telemetri gerekiyor**, Faz E-1) … henüz YOK."* Şart karşılandı: Faz 0
> telemetriyi (`reject_reason`) kurdu, Faz 2b onu triyaja bağladı. Bu beyan
> `tests/test_beyanlar_curumesin.py`'de bir **tuzaktı** ve Faz 4 landing ettiği gün
> **kırıldı** — kurulduğu iş buydu. Test yönü tersine çevrilerek korunuyor: artık
> seçicinin **süzülmüş** listeyi gördüğünü ölçüyor.

**Bu fazın omurgası: SEÇİM ≠ ÇALIŞTIRMA.** `sec()` yalnız **önerir**; her adım yine
`calistir()`'e verilir ve **aynı dört kapıdan** geçer. Sonuç: **seçicinin yanılması yeni
bir risk açmaz** — var olan kapılar zaten onu karşılar.

| seçici hatası | hangi kapı öldürür |
|---|---|
| uydurulmuş araç adı | **KAYIT** (ve `sec()` onu **kayda geçirerek** eler) |
| yetkisiz araç | **YETKİ** — ajan kullanıcıyı AŞAMAZ |
| `route` denenmeden LLM aracı | **DETERMİNİSTİK-ÖNCE** |
| sonsuz/pahalı plan | **BÜTÇE** |
| yazma yan etkili araç (`dashboards.create` …) | zaten `llm_araclari` **dışında**, beyan edilerek |

**Sessiz kırpma YOK:** geçersiz bir öneri sessizce elenmez, `Adim(hata="SEÇİM REDDİ…")`
olarak kayda geçer — sessizce elemek, seçicinin ne kadar yanıldığını **ölçülemez** yapardı.

**`route` öneride yoksa BAŞA eklenir.** Kapı zaten çalıştırmada bunu zorlar; burada eklemek
planın ilk adımda `AracReddi`'ye çarpıp hiç denememesini önler — **kapı ceza değil
yönlendirme**.

**Yedek yollar (gerileme YOK):** sağlayıcı yok · `plan_sec` taşımıyor · bozuk JSON · patladı
· boş liste → hepsi `["route"]`. Sağlayıcı yokluğu bir hata değil, **plan zaten belliydi**
demektir.

**Kalan (F3):** belirsizlikte plan seviyesinde sorma, ve kalan kompozisyonların
(rapor · pano) planlayıcıya taşınması.

**40 test**: `tests/test_orkestrator.py` *(FAZ 0.2 + 0.22 + **6.4 sertleştirmesi** @`31916d6`)*.
FAZ 6.4 ile eklenenler: **plan dondurma** (kontrol-akışı bütünlüğü — araç çıktısı planı
değiştiremez), **dört katmanlı adım doğrulama** sınır değerleriyle (`satır=0` · null
%90/%91 · mertebe 99×/100× · şema), **hata imzası** (mesajın tamamı değil **sınıfı**) ve
**plan kontrol listesi** (`adimlar_toplam`/`adimlar_tamam`).

> ⟳ **TOPLANABİLİRLİK: TEK SINIFLANDIRICI, ÜÇ POLİTİKA** *(FAZ 0 / canlı denetim + bütünlük denetimi, 2026-08-04)*
>
> **Sınıflandırma tek yerdedir:** `contribution.toplanabilirlik(measure, cube_meta)` →
> `TAM` · `YARI` · `YOK` · `BILINMIYOR`. Metadata (`non_additive`/`semi_additive`/
> `measure_expressions`) **yalnız orada** okunur. Ama **politika üçe ayrılır**, çünkü üç
> tüketici **ayrı soru** sorar:
>
> | Tüketici | Sorusu | Kabul |
> |---|---|---|
> | `contribution.ayristirilabilir_mi` | Δ segmentlere dağıtılabilir mi? | yalnız `TAM` |
> | `viz._additive` | **zaman** ekseninde yığılabilir mi? | yalnız `TAM` |
> | `interpret` dönem trendi | **zaman-DIŞI** eksende toplanabilir mi? | `TAM` + **`YARI`** |
>
> **Neden bu ayrım:** canlı bir kullanıcı turunda `makine × ay` kırılımlı fire raporunda
> aynı veriye **üç ayrı yüzde** basıldı (`+%88,1` · `−%72,3 «iyileşti»` · `+%98,3`) —
> çünkü *"ilk→son"* iki **farklı makinenin** değeriydi. **Trend bir DÖNEM ifadesidir:**
> pivot önce **döneme göre toplanır**. İlk düzeltme bu toplamayı `ayristirilabilir_mi`'ye
> sordu ve **yarı-toplanabilir yedi ölçünün** (`bakiye` · `acik_bakiye` · `acik_borc` ·
> `net_bakiye` · `net_miktar` · `stok_deger` · `vadesi_gecen`) trendini **haksız yere**
> susturdu: bir stok ölçüsü **müşteriler arasında toplanır**, toplanamadığı eksen zamandır.
>
> ⚠ **Yasak KOŞULSUZ DEĞİLDİR** *(bir denetim bu satırın koddan geniş olduğunu ölçtü)*:
> **kırılımsız** bir seride dönem başına zaten tek satır vardır, toplama yapılmaz →
> bir **oran serisinin trendi meşrudur** (*fire oranı Oca %10 → Haz %20*). Trend yalnız
> **toplama gerektiğinde** ve sınıf `YOK`/`BILINMIYOR` iken yazılmaz — nedeni yazılır.
> `BILINMIYOR` **fail-closed**tir: yanlış bir yüzde, hiç yüzdeden kötüdür.
>
> Aynı sınıflandırma *"toplamın %X'i"* payını da yönetir; **toplanamayan ölçüde
> sıralama da yapılmaz** (payı susturup gövdeyi toplamak, sayının kendisini yanlış bırakırdı).
> Kapı: `tests/test_pivot_trend_yanlis_degil.py` · ölçüm: `git show e22b2b9`.

### 11.6 Özellik = KOMPOZİSYON, endpoint değil

Kök-neden analizi, karar matrisi, rapor/dashboard üretimi, uyarılar, tahmin — bunlar **ayrı
endpoint olarak yazılmamalıdır**. Her biri bir araç kompozisyonu olursa: her adım makbuz
üretir, her adım yetkiye tabidir, her adım tek kapanış zincirinden (`answer.py`) geçer, ve
yeni bir özellik **yeni bir kompozisyon** demektir — yeni bir baypas yolu değil.

---

## 12. Konuşma sözleşmesi — thread bağlamsallığı (Faz G5 kuruldu)

> **Bu bölüm olmadan bir sonraki geliştirici "sohbet"i Discovery'ye bağlar** — bugüne kadar
> olan tam da budur.

### 12.1 Korunan değişmez (tartışmaya kapalı)

**Thread bir UI GRUPLAMASIDIR, SEMANTİK SINIR DEĞİLDİR.** Bir thread cube/bağlam sınırı
taşımaz; yeni thread **yalnız açık kullanıcı eylemiyle** doğar. Sunucu bir soruyu *"yeni
konu"* ilan ederek bağlamı **sessizce koparamaz**.

### 12.2 Ölçülen durum (2026-08-02, düzeltme öncesi)

```
thread_id, reply_to_label  →  SALT ECHO (sunucu alır, aynen geri verir)
is_new_topic               →  not is_followup   (tek boolean)
sınıflandırma              →  structural_followup | raw_followup   (İKİLİ)
```

Yani **sunucunun bir bağlam modeli yoktu** — hangi soru hangi bağlama ait, istemciye
güveniliyordu. Ve mantık `ask()` closure'larının içinde olduğu için **izole test
edilemiyordu**.

### 12.3 `app/context.py` — deterministik, gerekçeli bağlam çözücü

Saf fonksiyon (I/O yok, LLM yok). Bağlam çözümü bir *anlama* işi değil bir **muhasebe**
işidir: hangi çapa verildi, hangi sorgu taşındı, hangi eksen zaten kullanıldı. LLM'e
verilseydi aynı girdi farklı turlarda farklı bağlama bağlanabilirdi ve *"kanıtlı"* iddiası
çökerdi.

**Kural sırası (öncelik BİLİNÇLİ ve test edilir):**

| # | Kural | Ne zaman | Neden bu sırada |
|---|---|---|---|
| 1 | `capa:karta-yanit` | kullanıcı bir karta yanıt verdi | **Açık eylem, örtük durumu EZER.** Aksi halde bir karta yanıt verirken en son raporun bağlamına kayardık — ve bu sessizce olurdu. |
| 2 | `capa:coklu-kesisim` | birden çok kart seçildi, aynı cube | **Kesişim**, birleşim değil: birleşim alsaydık seçilmemiş bir ölçü sessizce rapora girerdi. |
| 3 | `capa:coklu-celiski` | birden çok kart, **farklı cube** | Farklı cube'lar farklı **grain**lerdir; sessizce birleştirmek fan-out'un diyalog seviyesindeki karşılığı olurdu. → **SOR** (ADR-0008). |
| 4 | `yapisal:cube_query` | istemci açık `cube_query` taşıdı | bugünkü `structural_followup` |
| 5 | `ham:onceki-sql` | ham-SQL zinciri | yapısal bağlam YOK — uydurulmaz |
| 6 | `taze:capa-yok` | hiçbir çapa yok | `taze` dönmek serbest, **gerekçesiz** dönmek değil |

### 12.4 "Kanıtlı olmalı" — somut karşılığı

1. **Gerekçe makbuza yazılır.** `contract_log.provenance_json` içinde `context_rule` +
   `resolved_context`. Ayrı bir kolon AÇILMADI: köken (hangi join) ile bağlam (hangi çapa)
   *"bu cevap nereden geldi"* sorusunun iki yüzüdür; ayrı kolonlar iki yarısı ayrı yerlerde
   duran bir kanıt üretirdi. **Uçtan uca test HTTP yolundan geçip bu alanı okur** — saf ve
   testli bir modül BAĞLANMAMIŞSA hiçbir şey ifade etmez (bu turda dört kez ölçülen desen).
2. **İzole test edilebilir.** 19 altın vaka; öncelik sırası, kesişim, çelişki, eksen
   birikimi, makbuz biçimi ve değişmezlik ayrı ayrı kilitli.
3. **Süreklilik ÖLÇÜLEBİLİR** (`SureklilikOlcumu`): takip bekleniyorken `taze` dönmek =
   bağlam **sessizce koptu**. Oran `None` dönebilir — `0.0` *"hep koptu"* demektir,
   `None` *"bu soru sorulamaz"* (aynı ayrım `stats.z_skorlari`'nda).

### 12.5 Kademeli bağlanma (dürüst kayıt)

`reply_to_cube_query` **henüz istemciden gelmiyor** (thread paneli §14'ün H4 kalemi).
O gelene kadar çapa listesi boş kalır ve çözücü 4–6. dalları kullanır. Bu bir eksiklik
değil kademeli bir bağlanmadır: **sunucu bugünden itibaren gerekçe üretiyor** ve istemci
hazır olduğunda çapa dalı devreye girer.

### 12.6 Anlatım doğrulayıcı (G4 — `app/narration_guard.py`) ✅

T2'nin sert kuralının uygulaması: *"üretilen metindeki her sayı sonuç kümesinde bulunmalı
ya da **beyan edilmiş** bir işlemle ondan türetilebilmeli; doğrulanamayan sayı içeren cümle
**YAYIMLANMAZ**."* Bu, *"LLM sayı uydurabilir"* riskini bir **umut meselesi** olmaktan
çıkarıp **test edilebilir bir kapıya** çevirir — `viz.py`'nin ADR-0024 disipliniyle aynı
felsefenin metin tarafı: **LLM üslubu yazar, SAYIYI sistem koyar.**

Dört tasarım kararı ve gerekçeleri:

| Karar | Neden |
|---|---|
| **Cerrahi**: yalnız kötü CÜMLE düşer, metnin tamamı değil | Bir uydurma yüzünden üç doğru cümleyi atmak bilgi kaybettirir. **Kullanılamayan kapı kapatılır** ve o zaman hiç yoktur. |
| **Göreceli tolerans** (%2), mutlak değil | LLM `15.576.000`'ı *"15,6 milyon"* diye yuvarlar; bunu uydurma saymak kapıyı kullanılamaz kılardı. |
| **Türetme listesi KAPALI** (fark · % değişim · toplam · ortalama · pay) | *"Her aritmetik kombinasyon"* serbest bırakılsaydı yeterince sayıyla her şey türetilebilir ve kapı hiçbir şeyi engellemezdi. Çarpım **izinli değildir**. |
| **Yıl ve küçük sıra sayıları doğrulanmaz** | *"2025'te"*, *"ilk 3"* veri iddiası değildir; doğrulamaya çalışmak gerçek uydurmaları **gürültüye boğardı**. |

Sonuç kümesi yoksa **fail-closed**: sayı içeren hiçbir cümle yayımlanamaz — kanıtsız sayı,
uydurma sayıdır. Tamamı düşerse deterministik yedeğe (`interpret` çıktısı) geçilir; yedek
de yoksa **boş** döner (sessizce uydurulmuş bir cümleden iyidir).

**Yazarken ölçülen kusur** (kendi testim yakaladı): ilk regex `15576000`'ı `155` + `760`
diye bölüyor ve **doğru** bir cümleyi reddediyordu. Bu kapının en tehlikeli hâlidir —
yanlış-pozitif üreten bir kapı kullanılamaz bulunup kapatılır. Gruplama dalı `*` yerine
`+` ile gerçekten gruplu sayılara sınırlandı.

> ⟳⟳ **BEYAN GÜNCELLENDİ — FAZ 5 (2026-08-03): TÜKETİCİ BAĞLANDI.**
>
> Eski metin: *"**Tüketicisi HENÜZ YOK** … bugün sistemde LLM-üretimi düz metin **hiç
> yoktur**"*. Bu beyan `tests/test_beyanlar_curumesin.py`'de bir **tuzağa** çevrilmişti ve
> Faz 5 landing ettiği gün **kırıldı** — tam olarak kurulduğu iş buydu: düzelten kişiyi ya
> guard'ı takmaya ya beyanı güncellemeye ZORLAMAK. **Üçüncü seçenek yoktu.** Guard takıldı,
> beyan burada güncelleniyor, ve test **yönü tersine çevrilerek** korunuyor: artık düz
> metin üreten her LLM yöntemi için `narration_guard`'ın **gerçekten çağrıldığını** ölçüyor.
> Ayrıca bir kapı daha eklendi: `llm.anlat(...)` ile `interpretation["narration"]` ataması
> **arasında** `guvenli_anlatim` bulunmak zorunda — LLM çıktısı guard'a **uğramadan**
> yayımlanamaz.

### 12.6b T2 ANLATICI (FAZ 5) — "LLM üslubu yazar, SAYIYI sistem koyar" ✅

**Sırası plana kesin yazılmıştı** (`-0.5 · -1 · 0 · 1 · 2a` bitmeden başlamaz) ve gerekçesi
şuydu: *"güzel ama yanlış"* bir anlatı, şablon bir doğrudan **kötüdür** — süs, hatayı
görünmez yapar. Önce cevaplar doğru geldi, sonra anlatıldı.

**Girdi DAR.** Model SQL yazmaz, sayı hesaplamaz, cube seçmez, **ham satır görmez** —
girdisi yalnız `interpret()`'in **zaten hesaplanmış** olgularıdır (`facts[].text`).
Prompt'ta *"HİÇBİR YENİ SAYI ÜRETME · hesap yapma · uydurma"* açıkça yasaklı.

**Çıkış FAIL-CLOSED.** `guvenli_anlatim` zorunlu kapıdır ve **cerrahi** davranır: her
cümledeki her sayı sonuç kümesiyle eşlenir (±%2, kapalı türetme listesi), eşleşmeyen
cümle **düşer**, temiz cümleler kalır (bir uydurma yüzünden üç doğru cümleyi atmak bilgi
kaybettirir; kullanılamayan kapı kapatılır ve o zaman hiç yoktur). Hiçbir cümle sağ
kalmazsa anlatı **hiç eklenmez**. **En kötü durum "süssüz ama doğru", asla "akıcı ama
uydurma" değildir.**

**ŞABLONU EZMEZ — üstüne biner.** Anlatı `interpretation["narration"]`'a yazılır;
`summary`/`facts` **aynen kalır** (testle kilitli: kaynak kodda `yorum["summary"] =`
yasak). Bu, kullanıcının **plan** §4.4'te açıkça istediği iki şartın doğrudan karşılığı: *"her zaman
grafik değil, bazen mesele sadece konuşmaktır"* korunur ve *"o konuşmayı grafiğe çevir"*
çalışır — çünkü altındaki yapı (`cube_query`/`result`/`summary`) **hiçbir zaman silinmez**.
Faz 0.5 bu şartın bir yerde **ihlal edildiğini** ölçüp düzeltmişti (§6.5z, `gorunum_donusumu`
0/5 → 4/5).

**Frontend ayrımı GÖRÜNÜR kılar** (`OutputInsight`): deterministik özet kendi kutusunda,
anlatı **altında, kesikli çerçevede, `✎ ANLATIM` rozetiyle**. İkisini tek bloğa
karıştırmak, LLM metnine deterministik özetin **otoritesini ödünç verirdi**. Rozet iddialı
değil, **kaynak bildirir**: *"doğrulanmış sayı"* ile *"doğrulanmış cümle"* aynı şey değildir.

**Araç kaydı (F2'nin dört kapısı).** `llm.anlat` `tools.KAYIT`'ta — planın §4.3 ⟳'sinde
prompt-enhancer için koştuğu şart (*"kapısız LLM çağrısı olmasın; makbuzda adım olarak
görünsün"*) anlatıcı için de uygulandı.

> ⟳ **FAZ 9.8 — BU CÜMLENİN İKİNCİ YARISI KARŞILIKSIZDI (denetimde bulundu).** Kayıt
> doğruydu, **çağrı değildi**: `answer.py` `llm.anlat(...)`'ı **doğrudan** çağırıyordu.
> Karşılaştır: enhancer gerçekten `Planlayici.calistir` üzerinden geçiyordu. Yani *"kapısız
> LLM çağrısı olmasın"* şartı yalnız **beyan** düzeyinde vardı — bu belgenin on dört kez
> avladığı *"beyan var, kod onu tanımıyor"* sınıfının **kendi metnindeki** hâli.
>
> Düzeltildi: çağrı `plan.calistir("llm.anlat", …)`'a alındı ve **deterministik-önce**
> kapısı kendi kaydını görsün diye `interpret` (aynı `anlatim` etiketinin LLM'siz kardeşi,
> maliyeti **sıfır**) planlayıcı üzerinden önce çalıştırılıyor. Kapıların buradaki gerçek
> karşılığı **bütçe** (sıcak yola giren LLM çağrısı sayılır) ve **makbuz**: adım
> `agent_run`'a **eklenir**, ajan koşumunun adımlarını **ezmez** — makbuz *"LLM ne zaman
> devreye girdi"* sorusunu cevaplamak için var; onu silmek yanıltmak olurdu.

**Bayrak `t2_anlatici` varsayılan `off`** (diğerleri `beta`): sıcak yola bir LLM çağrısı
ekliyor, açılması **bilinçli bir karar** olmalı. Kural-tabanlı sağlayıcı `anlat` taşımaz —
yokluğu bir hata değil **yol kapalı** sinyalidir.

20 test: `tests/test_t2_anlatici.py` (+ `test_beyanlar_curumesin.py` 4 yeni kapı).

### 12.7 Takip sorusunun ÜÇ sınıfı (G1 — `app/followup.py`) ✅

Takip soruları **iki** sınıfa ayrılıyordu: *sorguyu düzenle* ya da *yeni ham SQL yaz*.
*"Verdiğin cevap hakkında konuş"* diye bir sınıf **yoktu**. Ölçüldü — bir `parti` raporu
üstünde altı sorunun **altısı da** duvara çarpıyordu:

| Soru | Eski cevap |
|---|---|
| *"bu neden böyle?"* · *"normal mi?"* · *"ne yapmalıyız?"* · *"sence iyi mi?"* | "Bu takip mesajını önceki raporla ilişkilendiremedim." |
| *"şu düşüş ne?"* | *"«dusus» kısmını anlayamadım"* |
| *"bunu nasıl iyileştiririz?"* | *"«bunu» yerine «gunu» mi demek istedin?"* ← anlamsız |

| Sınıf | Örnek | Ne yapar |
|---|---|---|
| **yapısal düzenleme** | *"aylık"*, *"makine bazında"* | `deterministic_refine` → yeni sorgu ✅ vardı |
| **cevap üstünde konuşma** (YENİ) | *"bu neden böyle?"*, *"normal mi?"* | **Sorgu üretmez.** Mevcut makbuza çapalanır, **araç çağırır**, anlatır |
| **yeni konu** | *"peki ciro?"* | taze soru ✅ vardı |

**Sınıflandırma LLM'siz.** Sınıf kararı bir *niyet tespitidir*, anlama değil. LLM'e
verilseydi aynı soru farklı turlarda farklı sınıfa düşer ve bağlam sürekliliği (§12.4)
ölçülemez hale gelirdi. Ayrıca konuşma turları en sık turlardır — **sıfır maliyetli** olmalı.

**Üç tasarım kararı:**

1. **YAPISAL ÖNCELİĞİ.** *"aylık neden düştü?"* hem düzenleme hem konuşma gibi görünür.
   Öncelik yapısaldadır: kullanıcı yeni sayılar bekliyorsa önce onları vermek gerekir —
   konuşma bir sonraki turda hâlâ mümkündür, ama **yanlış sayı geri alınamaz**.
2. **Bağlam kapısı.** Konuşulacak bir cevap yoksa bu sınıf tanımsızdır; *"bu neden böyle?"*
   diye **başlayan** bir oturum yeni konudur (çapalanacağı makbuz yoktur).
3. **`deterministic_refine`'dan ÖNCE yakalanır.** Aksi halde *"neden"*/*"düşüş"* kelimeleri
   onun sözlük eşleşmesine karışır — Faz D3'te *"neden arttı"* → `bakim.mudahale_eden`
   sahte eşleşmesi tam buydu.

**Özellik = KOMPOZİSYON, endpoint değil** (§11.6): `/ask/konusma` diye bir uç **açılmadı**.
`neden`/`ne yapmalı` → `contribution` (gövdesi **çağrılır**, kopyalanmaz), `normal mi` →
`yoy`. Yeni bir "normallik" tanımı **uydurulmaz**: elimizdeki tek nesnel zemin geçen
dönemle kıyastır ve cevap onu böyle sunar. Araç bir şey üretemezse **normal zincir devam
eder** — gerileme yok.

**Bilinen sınır:** anlatım bugün **deterministiktir** (katkı bulguları + kıyas tablosu).
LLM üslubu devreye girdiğinde §12.6'nın doğrulayıcısı zorunlu olur; o zamana kadar
uydurma sayı riski **yapısal olarak yoktur** çünkü metni LLM yazmıyor.

### 12.8 Grafiğe çapalı diyalog (G2) ✅

*"Nisandaki sıçrama ne?"* bir **metin numarası değil YAPISAL BİR SEÇİMDİR**: kullanıcının
işaret ettiği hücrenin koordinatı `drill.select_cube_query` ile **gerçek bir alt-sorguya**
çevrilir (o boyut kırılımdan çıkar, yerine `eq` filtresi girer) ve konuşma **o sorgunun**
üstünde yürür.

`AskRequest.anchor = {dimension, value}`. Dönüşüm **yeniden yazılmadı** —
`DrillDownPanel`'in her adımının kullandığı aynı fonksiyon çağrılır. İki yol aynı
koordinat mantığını ayrı uygularsa *"grafikte tıkladığım hücre"* ile *"sohbette
konuştuğum hücre"* zamanla farklılaşırdı.

**Üç davranış ayrımı, üçü de bilinçli:**

| Durum | Davranış | Neden |
|---|---|---|
| Şeması bozuk çapa (sözlük değil) | **422** | İstemci hatası sessizce yutulmaz |
| Şeması doğru, anlamı geçersiz (olmayan boyut, eksik alan) | **sessizce yok sayılır**, konuşma tüm rapor üstünde yürür | Eşleşme başarısızlığı kullanıcı hatası değildir; uydurulmuş bir filtre, filtre olmamasından kötüdür |
| Çapa yok | bugünkü davranış | Gerileme yok |

**UI kararı — tek tıklamaya tek yorum DAYATILMAZ.** Grafikte bir hücreye tıklamak eskiden
doğrudan `DrillDownPanel`'i açıyordu; yani tıklama *"buraya inelim"* diye **yorumlanmış**
oluyordu. Oysa aynı tıklama *"bunu konuşalım"* da demek olabilir. Artık bir **çapa şeridi**
belirir (*"◎ M-01 seçildi —"*) ve kullanıcı seçer: `bu neden böyle?` · `normal mi?` ·
`⤵ kırılıma in`. Şerit yalnız tıklamadan **sonra** görünür — boşken hiçbir yer kaplamaz.

Frontend'in mevcut korumaları korundu: yalnız tek birincil kategorili basit şekillerde
(bar/line/pie) tetiklenir; ECharts'ın **biçimlendirilmiş** etiketi ham satırlarda tam
eşleşmiyorsa **sessizce atlanır**.

### 12.9 Reçeteli analiz (G3 — `app/prescribe.py`) ✅ — ve neden DAR olduğu

Bir "karar matrisi" kolayca uydurulur: seçenekler × kriterler × ağırlıklar tablosu **her
zaman** bir sayı üretir. Ama o sayıların ölçülmüş bir zemini yoksa ürün, kanıtlanabilir bir
BI aracından **kanaat üreten** bir araca dönüşür — ve bu depoda kayıtlı en temel değişmez
*"cevap bir makbuzdur"*dır.

Kullanılan **üç** boyutun üçü de ölçülmüş ya da **beyan edilmiştir**:

| Boyut | Kaynak | Uydurma payı |
|---|---|---|
| **Etki** | `contribution` deltası — ölçülmüş | yok |
| **Yön** (iyi/kötü) | `lower_is_better` — metadata **beyanı** | yok |
| **Yoğunlaşma** | en büyük segmentin brüt harekete oranı — hesaplanmış | yok |

**Kasten dışarıda:** *kontrol edilebilirlik · uygulama maliyeti · risk*. Hiçbiri veride yok
ve tahmin edilemez; bir ağırlık tablosuna konsalardı sıralama **uydurma** olurdu — üstelik
`source="cube"` rozetiyle. Gerçek bir müşteride bu boyutlar **beyan edilerek** eklenebilir
(metadata), tahmin edilerek değil. Bir test o boyutların sessizce geri gelmesini engeller.

**`lower_is_better` burada ANLAMA dönüşüyor.** §13.4'te *"`recommend()`'e ulaşıyor ama
karara dönüşmüyor"* diye kayıtlıydı: fire artışı kötüdür, ciro artışı iyidir — ve bunu ad
tahmininden değil **beyandan** biliyoruz.

#### En önemli çıktı bir öneri değil bir REDDİR

Değişim **dağınıksa** (en büyük segment brüt hareketin ⅓'ünden azını açıklıyorsa),
*"şu segmente odaklan"* **yanlış tavsiyedir**: sorun sistemiktir ve tek bir segmenti
düzeltmek toplamı kayda değer biçimde değiştirmez. Modül o durumda öneri **üretmez**,
**neden üretmediğini söyler** — `contribution`'ın toplanabilirlik kapısıyla (*"AVG'de katkı
payı TANIMSIZDIR"*) aynı disiplinin reçete seviyesindeki karşılığı.

#### Reçete YALNIZ sorulduğunda üretilir

*"Bu neden böyle?"* bir **açıklama** ister, reçete değil. İkisini karıştırmak, kullanıcının
**sormadığı** bir tavsiyeyi cevabın yerine koymak olurdu. Test her iki yönü de kilitler.

### 12.10 Eşik kıyası: hedef UYDURULMAZ, kullanıcının KENDİ sınırı okunur (G3) ✅

Plan bir *"hedef/eşik kıyası"* istiyordu. **Ölçüldü: cube metadata'sında `target:`/`hedef:`
diye bir beyan HİÇBİR cube'da yok.** Demo için hedef uydurmak, `pvm:` eşleştirmesinde
bilinçle reddedilen şeyin aynısı olurdu — GÜVENLE YANLIŞ bir sayı (*"hedefin %12
altındasın"*) ve kullanıcı onu sorgulamaz.

Ama gerçek, **beyan edilmiş** bir eşik kaynağı zaten var: **kullanıcının kendi kurduğu
alarmlar**. `fire_kg > 30` alarmını kuran kişi *"benim için kritik sınır bu"* demiş olur.
Bu uydurulmuş bir hedef değil, kullanıcının kendi ifadesidir.

`schedules.kullanicinin_esikleri()` + `schedules.esik_sinyalleri()` →
`interpret(..., esikler=)`. Dört karar:

| Karar | Gerekçe |
|---|---|
| **`_maybe_interpret`'e bağlandı**, ayrı bir uca değil | Tek kapanış zincirinin parçası: `/ask` · `/cube` · `/report` · drill · katkı **hepsi** kıyası bedava alır ve **yeni yüzey açılmaz** (sinyal zaten `OutputInsight`'ta render ediliyor) |
| **Aynı matematik** (`check_threshold` ÇAĞRILIR) | Ekrandaki uyarı ile e-postadaki alarm ayrışırsa, "e-postada uyarı gelirken ekranda gelmeyen" bir gün gelir — I4'te ölçülen sadakat kusurunun uyarı tarafındaki karşılığı |
| **Rahat alanda SUSAR** | *"Eşiğin %40 altındasın"* her cevaba eklenirse sinyal gürültüye döner ve ASIL uyarılar okunmaz olur. Sessizlik burada bir karardır |
| **Anomali alarmı eşik SAYILMAZ** | `method=zscore` bir sınır değil baseline'dan öğrenen bir istatistiktir; `interpret._signals` onu zaten koşuyor — ikisi aynı şeyi iki kez söylerdi |

**Tanımsız sayı üretilmez:** `value <= 0` eşikte "yüzde olarak yaklaşmak" tanımsızdır
(0'a %90 yaklaşmak nedir?) — yaklaşma hesaplanmaz, ihlal yine bildirilir. `contribution`ın
`net_pay = None` disiplininin aynısı.

**Tenant-RLS eşik kıyasında da geçerlidir**: başka kiracının koyduğu sınır bu kullanıcının
cevabında görünemez. 23 test: `tests/test_esik_kiyasi.py`.

**"İzleme kur" zaten vardı** (ReportCard 🔔 → `createSchedule` + `threshold`); halka şimdi
kapandı: kullanıcı eşiği kurar → **her cevapta** o eşiğe göre uyarılır → ihlalde bildirim
gelir → bildirim **nedenini** de taşır (§11.6e).

### 12.11 Henüz YOK (G3 kalanı)

Seçeneklerin **doğrudan** izleme kurulumuna dönüşmesi (reçete kartından tek tıkla
`schedules.create` — bugün kullanıcı 🔔'i kendi açıyor).

---

## 13. Görsel dilbilgisi — semantik metadata görselleştirmeyi besler (Faz I1)

### 13.1 Korunan karar

ADR-0024 — *"grafik üretimini LLM'e verme"* — **doğrudur ve korunur**. `viz.py`'nin
deterministik `analyze()`/`recommend()` tasarımı Show-Me / Cleveland-McGill temellidir.
Motor/kütüphane eklemek serbesttir; **kararı LLM'e devretmek değil.** İyileştirme LLM'den
değil **daha zengin girdiden** gelir — ve o girdi zaten elimizdedir.

### 13.2 Ölçülen sessiz-yanlış: beyan var, viz onu görmüyordu

Cube metadata'sı `additive: full | semi | non` **beyan ediyor** ve `schema()` bunu
`semi_additive`/`non_additive` olarak **zaten taşıyordu**. `recommend()` onları **hiç
almıyordu**; yerine bir ad/birim regex'i kullanıyordu:

```
viz._additive("bakiye", "₺")  →  True     ← YIĞMA ÖNERİLİR
```

`bakiye` iki cube'da (`cari`, `mizan`) `additive: semi` beyan edilmiş. Bakiye bir **STOK**
büyüklüğüdür: dönemler arasında **toplanamaz** (Ocak bakiyesi + Şubat bakiyesi bir şey
ifade etmez). Yığılmış grafik, matematiksel olarak yanlış bir görseli *"deterministik"*
rozetiyle sunardı — `viz.py`'nin varlık sebebine aykırı.

**Kural: BEYAN SEZGİYİ EZER.** Regex **yedek olarak kalır** — beyanı olmayan ölçülerde
bugünkü davranış korunur; beyanı olmayanı yasaklamak *ölçmeden kısıtlama getirmek* olurdu
(aynı disiplin `strict_mode` ve `validate_project` açılırken de uygulandı). Türetilmiş
kıyas kolonu (`bakiye_gecen`) kısıtı **miras alır**: bir stok büyüklüğünün geçen dönemi de
stok büyüklüğüdür.

Pay grafiği (pie/treemap) de **aynı kapıya tabidir**: dilimlerin toplamı bütünü vermelidir;
toplanamaz bir ölçüde pasta grafiği aynı yalanı yuvarlak çizer.

### 13.3 İkinci kusur: altı çağıran, altı elle toplanmış argüman listesi

`recommend()`'in **altı** çağıranı vardı (`/ask` ×2, `/report`, `dashboards`, `schedules`,
`conversations`) ve her biri argümanları **elle** topluyordu. Sonuç kodda zaten kayıtlı:
bir yerde anahtar `measure_units` diye **yanlış yazılmış** ve birim farkındalığı o yolda
hiç devreye girmemişti. `semi_additive` aynı sınıfın ikinci örneğiydi.

**`viz.meta_args(cube_meta)` tek kaynaktır.** Yeni bir metadata alanı görselleştirmeye
bağlandığında **tek bir yer** değişir. Bir test elle toplamanın geri gelmesini engeller
(parantez eşleyerek her çağrı yerini denetler — sabit pencere, uzun bir açıklama yorumu
yüzünden doğru kodu yanlış raporluyordu).

### 13.4 Henüz bağlanmayan metadata (dürüst kayıt)

| Metadata | Görselde ne yapmalı | Durum |
|---|---|---|
| `units` | eksen/etiket/kısaltma | ✅ |
| `semi_additive` / `non_additive` | **yığma ve pay YASAK** | ✅ (bu tur) |
| `dimension_origin` + sertifika | köken rozeti | ✅ (§14.4) |
| `lower_is_better` | **renk semantiği** — artış kırmızı/yeşil doğru yönde | ⚠️ `recommend()`'e ULAŞIYOR (`lower_set`) ama renk kararına **henüz dönüşmüyor** |
| `dimension_labels` / `measure_synonyms_display` | Türkçe başlık/lejant | kısmen |

### 13.5 İlk yeni tür: ŞELALE (I2) ✅ — ve seçim kuralının ne demek olduğu

PVM'nin matematiği Faz 5.1'de yazılmış, **görseli yoktu** (`grep -c waterfall app/viz.py`
→ **0**). Özelliğin görünen yarısı eksikti.

**Seçim kuralı bir tercih değil bir KAPIDIR.** Şelalenin tüm anlamı şudur: *"bu çubukları
üst üste koyarsan sondaki değere varırsın."* Bileşenler toplamı bitişe varmıyorsa **grafik
yalan söyler** — çubuklar bir yere çıkar, eksen başka bir yeri gösterir ve okuyan farkı
**göremez**. Bu yüzden `viz.waterfall_spec()` toplamı denetler ve tutmazsa **`None` döner**:
grafik susar, tablo konuşur.

PVM bu koşulu tam olarak sağlar (`fiyat + miktar + birleşik = net`, `test_pvm_ARTIKSIZ` ile
kilitli) — şelalenin ilk gerçek tüketicisi bu yüzden PVM'dir. Kapı geçmediği gün bu bir
**bozulma sinyalidir** ve grafiğin susması doğrudur.

Tolerans **göreceli**: `0.1 + 0.2 != 0.3` olduğu için birebir eşitlik meşru her ayrışmayı
reddederdi; mutlak eşik ise ölçek değişince anlamını yitirir (₺15.576.000 ile %2,3 aynı
eşiği paylaşamaz).

**Karar backend'de** (ADR-0024): frontend grafik türü *seçmez*, `PvmReport.viz` doluysa
render eder. Şelale **yolu** gösterir, yanındaki ızgara **sayıyı** verir — biri diğerinin
yerine değil tamamlayıcısıdır (grafikten okunan değer her zaman yaklaşıktır).

**Kütüphane kullanılmadı** ve bu bilinçlidir: ECharts'ın waterfall'ı yığılmış-bar +
görünmez taban numarasıdır, yani aynı sayıyı iki seriye bölmek gerekir. Üç-dört adımlık
bir şelalede bu, okunan değer ile gösterilen değeri ayrıştırma riski taşır.

### 13.6 Yüzeyler arası SADAKAT kilitlendi (I4/I5) ✅

> Aynı `cube_query` için ekran · e-posta · rapor · pano · resume **AYNI VizSpec
> kararlarını** üretir. `viz.recommend()` **tek** bir karar verir; yüzeyler onu
> **render eder**, yeniden karar VERMEZ.

Bu sözleşme kodda zaten iddia ediliyordu ama **hiçbir şey onu tutmuyordu** ve **iki kez
kırılmıştı** (ikisi de kodda kayıtlı): bir çağıran birim sözlüğünü `measure_units` diye
yanlış anahtarla geçiyordu; `semi_additive` ise hiçbir çağıran tarafından geçirilmiyordu.

Sapma **sessizdir ve bu yüzden tehlikelidir**: kullanıcı ekranda çizgi grafiği görür,
e-postada aynı sorunun bar grafiğini alır ve hangisinin doğru olduğunu bilemez.

Üç kilit:
- **Davranış**: aynı girdi → aynı karar; metadata atlanırsa kararın GERÇEKTEN değiştiği
  gösterilir (testin varlık sebebinin kanıtı).
- **Yapı**: her `recommend()` çağrısı `meta_args` **ve** `cube_query` geçirmeli.
  `cube_query` boyut **otoritesidir** (Faz C1) — onsuz kolon rolleri veriden tahmin edilir.
- **Yüzey**: `viz_email` ve `report` **kendi** `recommend`/`analyze`'ını yazmamalı.

### 13.7 Görsel dilbilgisi belgelendi (I3) ✅ — `backend/VIZ_STANDARDS.md`

Belge **yalnız zorlanan** kararı bağlayıcı sayar; zorlanmayan her madde açıkça
*"henüz zorlanmıyor"* diye işaretlidir. Gerekçe: denetlenmeyen bir standart, bu depoda
**sekiz kez ölçülen** desenin (*beyan var, kod tanımaz*) ta kendisi olurdu.

Belge yazılmadan **önce** ölçüldü: beş grafik kararı zaten **49 testle** zorlanıyordu
(yığma yasağı 9 · şelale kuralı 11 · sadakat 7 · kolon rolü 9 · sayı biçimi 13).
Zorlanmayan **tek** karar `lower_is_better` → renk idi — ve orada gerçek bir sapma çıktı:

**Ölçülen kusur:** frontend `lower_is_better`'ı `/schema`'dan **tüm cube'ların birleşimi**
olarak okuyordu ve backend VizSpec'in **cube-kapsamlı** `lower_set`'ini hiç kullanmıyordu.
Demo'da bir ölçü tam olarak bu şekilde çatışıyor: `toplam_dogalgaz_sm3`
`surdurulebilirlik`'te düşük-iyi, `enerji_makine`'de **değil**. Birleşim ikisinde de ısı
paletini ters çeviriyordu — **aynı sayı, yanlış cube'da yanlış renkle** okunuyordu.

Düzeltme: `VizSpec.lower_set` **otoritedir**; şema birleşimi yalnız grafik kararı FE'nin
yerel `analyze()`'ından geldiğinde **yedek** olarak kullanılır
(`ResultView.tsx` + `test_viz_sadakat.py::test_CAKISAN_olcu_cube_kapsaminda_ayrisir`).

**Hâlâ YOK ve belgede öyle işaretli:** kalan dağarcık (**pareto** — `interpret._signals`
yoğunlaşmayı zaten tespit ediyor ve `prescribe.py` onu ölçüyor, ama frontend'in
`ChartKind`'ında pareto **yok**: eklemek backend kuralı + ECharts oluşturucusu + toggle
demek, aksi halde **yetim bir alternatif** olurdu; bullet · slope · boxplot · sankey ·
combo) · renk körlüğü paleti · eksen kuralları (kesme · sıfır tabanı · eksik dönem
boşluğu) · PDF dışa aktarım · rapor katmanının anlatı+kanıt zinciri.

---

## 15. KARAR KAYDI — Query Contract'ın bir üstü (Faz E-4)

Query Contract *"bu sayı nasıl hesaplandı"* sorusunu cevaplar ve bu ürünün temel
değişmezidir. Karar Kaydı **bir üst soruyu** cevaplar:

> *"Bu sayıya bakarak NE KARAR VERDİK, hangi seçenekler arasından, hangi gerekçeyle,
> kim ve ne zaman?"*

BI ürünlerinde eksik olan halka budur: **rapor kalır, kararın kendisi kaybolur.** Altı ay
sonra *"bunu neden yapmıştık"* sorusunun cevabı kimsede olmaz — ve o cevabı üretebilen bir
sistem, rapor üreten bir sistemden **kategorik olarak** daha değerlidir.

### 15.1 Dört tasarım kararı

| Karar | Gerekçe |
|---|---|
| **Değerlendirilen TÜM seçenekler saklanır**, yalnız seçilen değil | *"Neden bu?"* ancak *"hangilerine karşı?"* bilinirse cevaplanabilir. Yalnız seçileni saklamak kararı bir **duyuruya** çevirir. |
| `content_hash` bir **imza DEĞİL, kurcalama tespiti** | Anahtarlı imza = anahtar yönetimi (rotasyon/saklama/iptal). **Ölçülmüş bir tehdide** dayanmadan o karmaşıklığı almak *"ölçülmemiş ihtiyaç için altyapı kurma"* kuralının ihlali olurdu. Tehdit netleşince **şema değişmez**, yalnız hash'i üreten fonksiyon değişir. |
| **Append-only** | Karar silinmez; revizyon `supersedes` ile yeni kayıt yazar (`ContractLog` disiplini, ADR-0019 ruhu). |
| **Fail-loud** (Contract'tan farklı) | Makbuz kaybolursa rapor yine döner — kanıt raporun kendisi değildir. Ama bir KARAR kaydedilemiyorsa kullanıcı bunu **bilmelidir**: kaydettiğini sanıp kaydedilmemiş olması en kötü sonuçtur. |

### 15.2 `verified` ÜÇ değerlidir

`True` (hash tutuyor) · `False` (**KURCALANMIŞ**) · `None` (kayıtta hash yok — eski/bozuk
satır). Üçünü ikiye sıkıştırmak *"doğrulanamadı"*yı *"kurcalanmış"* gibi göstermek olurdu:
**suçsuzu suçlu göstermek.**

### 15.3 Kanıt bağı zorunlu DEĞİL ama ÖLÇÜLÜR

Bir karar kaydı tek başına bir **cümledir**; Query Contract kimliklerine bağlandığında
**yeniden çalıştırılabilir bir iddiaya** dönüşür. Kanıtsız kayda izin verilir (kullanıcı
serbest metinle karar yazabilir) ama `evidence_count` okumada görünür — *"kanıtsız"* ile
*"kanıtlı"* aynı şey değildir.

### 15.4 UI: kaydet **ve DOĞRULA** (H1)

İki uç, ikisinin de tüketicisi var: `POST /decisions` → `PrescriptionLayer`'daki seçenek
butonları; `GET /decisions/{id}` → aynı yerdeki **"doğrula"**.

> Makbuzun değeri onu **kontrol edebilmektedir**. Kaydedip bir daha bakmadığın bir kayıt
> bir tutanak değil bir **temennidir**.

Kurcalanmış kayıt UI'da **kırmızı** ve *"⚠ kurcalanmış"* olarak görünür. Kaydetme
başarısızsa *"karar KAYBOLDU, tekrar dene"* denir — sessiz yutma yok (ADR-0020).

**Yetki:** okuma `viewer` (bir kararı görmek, dayandığı raporu görmekle eşdeğerdir),
yazma `analyst+` (karar kaydı kurumsal bir beyandır ve silinemez). Başka tenant'ın kaydı
**404** döner, 403 değil — *"yetkin yok"* cevabı kaydın **var olduğunu** sızdırır.

---

## 14. Arka–ön sözleşmesi — "Tanım Tamamlandı" = arka + ön + test

> Bu bölüm bir denetim bulgusundan doğdu (2026-08-02): **bu turda yazılan iki uç frontend'de
> HİÇ kullanılmıyordu** — `POST /ask/contribution` (katkı ayrıştırması + PVM, Faz 5.1/5.2) ve
> `POST /measures/candidates/{cid}/preview` (diff önizlemesi, Faz 4.2). İkisi de çalışıyordu,
> ikisinin de testi vardı, ikisini de hiç kimse göremiyordu.

### 14.1 Kural

Hiçbir backend yeteneği şu üçünden biri olmadan **"bitti" sayılmaz**:

1. **Frontend tüketicisi var** (hangi bileşen, hangi etkileşim), ya da
2. **`api-only` olarak BEYAN EDİLMİŞ** — gerekçesiyle, `tests/test_uc_yetim_degil.py::API_ONLY`
   sözlüğünde, ya da
3. **Aynı PR'da UI biletiyle** ve o bilet kapanmadan faz kapanmaz.

Kapı otomatiktir: **yetim uç = kırmızı CI.** OpenAPI'deki her yol frontend kaynağında aranır
ya da `API_ONLY`'de beyan edilmiş olmalıdır. *"Şimdilik böyle kalsın"* bir seçenek değildir —
kapı tam olarak onu engellemek için vardır.

**Ölçülen durum (2026-08-02, Faz H):** 47 yolun 5'i yetimdi. İkisi kapatıldı (aşağıda), üçü
gerekçesiyle `api-only` beyan edildi (`/health`, `/health/ready`, `/dry-plan`).

**Kapının bilinen sınırı:** *"frontend'de string var ama hiçbir kullanıcı etkileşimine bağlı
değil"* durumunu ayırt edemez — o bir kod okuma işidir. Kapı yalnız **hiç bahsedilmeyeni**
yakalar. Sınırın kaydedilmesi, olmayan bir garantiyi rozetlememek içindir.

**Koşum notu:** kapı frontend ağacını görmezse **atlar** (backend deposu tek başına da
klonlanabilir olmalı ve orada "kırmızı" değil "ölçülemedi" demelidir). Bu yüzden test
komutu depo KÖKÜNÜ mount etmelidir; yalnız `backend/`'i mount eden bir koşumda bu kapı
sessizce atlanır — §6.4'ün *"ölçüm aracı da bir bağımlılıktır"* dersinin aynısı.

### 14.2 Yeni yetenek yeni PANEL doğurmaz

Bugünkü desen her yetenek için bir `*Panel`'di: `DrillDownPanel`, `DashboardsPanel`,
`SchedulesPanel`, `ReportPanel`, `SchemaPanel`, `HistoryPanel`, `ContractDetailPanel`,
`ConnectionReviewPanel`, `ReviewPanel`, `HelpPanel`… Şartnamedeki özelliklerin **onda biri**
eklense arayüz kullanılamaz hale gelir.

| İlke | Karşılığı |
|---|---|
| **Tek cevap yüzeyi + kademeli açılım** | Kök neden, katkı, PVM, köken, makbuz, güven — hepsi cevabın KENDİ kartında açılır/kapanır. Yeni panel değil, yeni **katman**. |
| **Sohbet birincil, panel ikincil** | Panel yalnız **kalıcı artefaktlar** için (pano, zamanlanmış rapor, bağlantı, inceleme). |
| **Her sayının yanında kanıt kancası** | Makbuz/köken tek tıkla; `ContractDetailPanel` bir *derinleşme*, giriş noktası değil. |
| **Chip'ler = keşif** | Yeni yetenekler chip olarak sunulur — menü büyütmeden. |
| **Boş durum ≠ hata** | Dürüst red ve netleştirme chip'i birinci sınıf UX'tir, "bulunamadı" ekranı değil. |

Uygulanmış örnek: `ContributionLayer` bir **panel değil**, `ReportCard` içinde katlanan bir
şerittir; her bulgu kendi `cube_query`'sini taşır ve tıklanınca `/cube` ile **LLM'siz** koşup
kendi makbuzunu üretir.

### 14.3 Kapatılan yetimler ve nasıl kapatıldıkları

| Uç | Nereye bağlandı | Neden oraya |
|---|---|---|
| `POST /ask/contribution` | `ReportCard` içinde `ContributionLayer` (katlanır şerit) | *"Neden değişti?"* bir panel sorusu değil, **cevabın devamıdır**. Bulgular tıklanır sorgulardır — ürünün rakiplerden ayrıştığı nokta ancak tıklanabilir olunca görünür. |
| `POST /measures/candidates/{cid}/preview` | `ReviewPanel`'de "kuru koşum" bloğu; **onay butonu diff görülmeden açılmaz** | Yanlış bir ölçünün blast-radius'u kategorik olarak büyüktür; inceleme ancak **görülen** bir değişiklik üzerinde yapılabilir. Diff bayatlarsa (form değişirse) onay yeniden kilitlenir. |

### 14.3b UI/UX bütünlük denetimi (2026-08-02) — ölçülen iki kusur ve düzeltmeleri

Kullanıcı direktifi: *"arkada geliştirip önde hiç kullanılmayan ucubeler olmasın · UI/UX
çok karışmamalı · her şey üst üste binmemeli."* Bu turda eklenen her yüzey denetlendi.

**Panel sayısı DEĞİŞMEDİ: 11 → 11.** Eklenen tek bileşen `ContributionLayer` ve o bir
*Panel* değil bir **Layer** — cevabın kendi kartında katlanır. H3 kuralı korundu.

#### Kusur 1: cevabın gövdesi "sonraki adım" diye etiketleniyordu

Konuşma cevabının (G1) bulguları yalnız `next_steps` üzerinden taşınıyordu ve UI onları
**"SONRAKİ ADIM"** başlığıyla gösteriyordu. Yani kullanıcı *"bu neden böyle?"* diye
soruyor, **cevabın kendisi** bir sonraki-adım önerisi gibi etiketleniyordu — üstelik Δ
tutarları, % paylar ve kırpma uyarısı chip'e sığmadığı için tamamen **kayboluyordu**.

Düzeltme: `AskResponse.contribution` alanı (yeni **panel değil, alan**) cevabın gövdesini
taşır; `ContributionLayer` **tek render edici** olarak hem buton yolunu (kendi çeker) hem
konuşma yolunu (hazır alır) besler. İkinci bir render edici yazmak, bu depoda beş kez
ölçülen sapma desenini (`fmt` ↔ `schedules`, `drill` ↔ `schedules`, `_uncovered` ↔
`_syn_hit`, `interpret` ↔ `viz`, `test` ↔ `fanout`) altıncı kez üretirdi. Konuşma
cevabında `next_steps` bloğu **gizlenir** — aynı liste iki kez, ikincisi yanlış başlıkla
görünürdü. Buton da gizlenir: cevap zaten açıkken *"tıklasam ne olur?"* düşündürmek üst
üste binmenin ta kendisidir.

#### Kusur 2: iki farklı analiz, aynı adla yan yana

Aynı kartta `⤵ kök neden` (DrillDownPanel) ve `𝚫 neden değişti?` (ContributionLayer)
yan yana duruyordu. İkisi de Türkçe "neden" diyor ama **farklı sorular** cevaplıyor:

| Buton | Soru | Analiz |
|---|---|---|
| `⤵ kırılıma in` | *"Bu sayı hangi kırılımlardan oluşuyor?"* | **SEVİYE** — mevcut durumun yapısı, ham satıra kadar |
| `𝚫 neden değişti?` | *"Geçen döneme göre ne değişti, kim sürükledi?"* | **DEĞİŞİM** — dönemler arası hareket |

Düzeltme: drill butonu **`⤵ kırılıma in`** olarak yeniden adlandırıldı (yaptığı **eylemi**
söyler) ve iki tooltip birbirine **açıkça atıf yapar** (*"…değişim için «𝚫 neden
değişti?»"*). "Kök neden" adı bilinçli olarak **hiçbirine verilmedi**: planın kendi
tanımında (F3) kök-neden bu ikisinin **kompozisyonudur** — tek bir bileşene o adı vermek
yanıltıcıdır.

#### Kusur 3: reçete düz metne çevriliyordu (G3 sonrası ölçüldü)

Reçete yalnız `note` metnine çevriliyordu ve backend'de hesaplanan **üç şey de
kayboluyordu**: segment başına **yön** (`lower_is_better` beyanından), **yoğunlaşma**
oranı, ve etki/pay sayıları. Chip yalnız etiket taşır.

**Yön bir RENK kararıdır ve metinden okunmaz**: *"fire arttı"* kötü haberdir, *"ciro
arttı"* iyi. Ayrımı ad tahmininden değil **metadata beyanından** biliyoruz; UI'ın bunu
göstermemesi, ölçülmüş bir bilgiyi çöpe atmak olurdu.

Düzeltme: `AskResponse.prescription` (yeni **panel değil, alan**) + `PrescriptionLayer`.
Dağınık değişimde liste yerine **gerekçe** gösterilir — boş bir liste değil, *neden boş*.

#### Ölçülen sonuç: kartta kaç şerit görünüyor?



Varsayım değil **ölçüm** (canlı `/ask`, 2026-08-02):

| Cevap türü | Şerit | Neler |
|---|---|---|
| Normal rapor | **3** | sonuç+grafik · katkı katmanı (**katlı**) · sonraki adım |
| *"bu neden böyle?"* | **1** | yalnız katkı katmanı (**açık**) — cevabın kendisi |
| *"ne yapmalıyız?"* | **2** | **reçete (CEVAP)** → **katkı (DAYANAK)** |
| *"normal mi?"* | **3** | gerçek kıyas tablosu üretir → normal rapor gibi |

İki katman **üst üste binme değil İKİ KADEME**: kullanıcı önce cevabı, sonra dayanağını
görür. Sıra ters olsaydı önce ham ayrışmayı, sonra cevabı görürdü.

Konuşma cevabı tam olarak **tek şey** gösterir: cevabın kendisi. Üçüncü bir chip şeridi
(`recommendations`, K4) orada **hiç doğmaz** çünkü sinyal üretimi `interpretation`'a,
o da bir `result`'a bağlıdır — konuşma cevabında sonuç tablosu yoktur. Bu, tasarımın
şans eseri değil **yapısal** sonucudur ve ölçülerek doğrulanmıştır.

Kartın **her** üst-seviye bölümü koşulludur; koşulsuz görünen hiçbir blok yoktur
(kademeli açılım). Karşılıklı dışlamalar da yapısaldır:
`contribution` varsa `next_steps` gizlenir, buton gizlenir.

#### Yakınsama kusur DEĞİLDİR

Katkı ayrıştırmasına artık **üç** giriş var: buton · doğal dil (*"bu neden böyle?"*) ·
bulguya tıklama. Bu **üst üste binme değil yakınsamadır** — aynı yetenek, farklı
alışkanlıklardaki kullanıcılar için farklı kapılar. Kritik olan **sunumun aynı olması**;
tek render edici bunu garanti eder.

### 14.4 Köken ve sertifika UI'da görünür (H5)

`dimension_origin` API'de Faz 1.1'den beri vardı ve UI'da **hiç görünmüyordu**; Faz D2'den
beri yanında fan-out sertifikası da geliyor. `InterpretationBar`'daki her ilişki-türevi
kırılım chip'i artık bir **köken rozeti** taşır (`⇱✓` / `⇱⚠` / `⇱?`) ve üzerine gelince
*"bölüm — makineler.bolum tablosundan, 1 sıçrama (oee_vardiya_makineler); fan-out ölçüldü:
hedef anahtar benzersiz, NULL yok, öksüz satır yok"* der.

Üç durum **ayrı** gösterilir ve bu ayrım pazarlama değil doğruluk meselesidir:
`olculdu:saglikli` ≠ `olculdu:riskli` ≠ **`olculmedi`**. Ölçülmemiş bir join'i yeşil
göstermek, olmayan bir garantiyi rozetlemek olurdu.

---

## 10. Bu belge nasıl güncellenir

- Mimari bir karar değiştiğinde **aynı PR'da** burası güncellenir. Kod ile belge ayrı PR'a
  bölünmez.
- §5'e bir satır eklerken **gerekçe zorunludur** ve gerekçe ya çalıştırılmış bir deney ya da
  birincil kaynaklı bir sektör emsali olmalıdır. "Bence böyle daha iyi" §5'e girmez.
- §6'daki bir kusur düzeltildiğinde satır **silinmez**, "✅ düzeltildi (tarih, commit)" olarak
  işaretlenir — kanıt silinmez (ADR-0019 ruhu).
- Yeni bir ADR kimliği kullanılacaksa §8.2 tablosuna **aynı anda** satır eklenir; dosyalar yok,
  tek kayıt burasıdır.
