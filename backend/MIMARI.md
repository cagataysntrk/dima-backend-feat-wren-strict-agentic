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

**Tek çıkış noktası `_finish()`** — yorum, next_steps, öneriler, `explain`, PII maskesi, sohbet
kaydı, `interaction_log` ve **fail-closed audit** oradan geçer. *Bilinen sapma: `_try_kpi()` bugün
`_finish()`'i atlıyor — düzeltilmeli.*

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
başarısızsa `rule`. Intent-JSON için ayrı ve **daha ucuz** bir model kullanılabilir
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
kalıbın dördüncü örneğidir, yeni bir desen değildir.

Cube ifadeleri **DuckDB/ANSI** yazılır; DuckDB dışı datasource'ta `WrenService._dialect_sql`
hedef lehçeye çevirir (T-SQL: `GROUP BY` ordinal genişletme, `DATE_TRUNC → DATEADD/DATEDIFF`,
Türkçe için `COLLATE Latin1_General_CI_AI` enjeksiyonu).

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
| **`dry_plan`'ı doğrulama kapısı sanma** | Dima hiç `WrenConfig` kurmuyor → `strict_mode=False` → `dry_plan` **kolon varlığını denetlemiyor** (ölçüldü: uydurma kolon plandan geçti, çalıştırmada `BinderException`). `CLAUDE.md`'nin *"motor doğrular"* ifadesi **tablo** doğrulaması için geçerlidir, kolon için değil. |
| **`except Exception` ile motoru sarma** | Kendine-referanslı ilişki + calc kolon → Rust'ta **PANIC** (`lineage.rs:146`, `unwrap() on None`). `PanicException` MRO'su `(PanicException, BaseException, object)` — **`except Exception` yakalamaz.** Hesap planı parent, BOM parent, org şeması: ERP'lerde standart. |
| **Kelimeye özel regex/keyword yaması** | Kayıtlı desen: aynı kök neden (`_uncovered`'ın substring körlüğü) defalarca kelimeye özel yamayla geçiştirildi, kök neden hiç düzeltilmedi. **Kural: kök nedeni düzelt, örneği değil.** (ADR-0008 disiplini) |
| **NL-benzerlik cevap cache'i** | Yapısal olarak benzer ama anlamsal olarak farklı Türkçe sorular yanlış cevabı **güvenle** döndürür. Anahtar `contracts.cube_query_hash()` olmalı (Faz 4.3'te yazıldı: `cq ⊕ mdl_version ⊕ company ⊕ tenant`). **Sonuç cache'inin kendisi bilerek KURULMADI** — tekrar oranı ölçülmedi; ölçülmemiş ihtiyaç için altyapı kurulmaz. Hash'in sözleşmesi *"aynı hash ⇒ aynı ÇIKTI"*dır: `filters` sıraya duyarsız (saf AND), `measures`/`dimensions` sıraya **duyarlı** (kolon ve GROUP BY sırasını belirler), akış bayrakları (`period_confirmed`) düşürülür. `result_hash` ile karıştırma — o *"sayılar değişti mi"* sorar ve satır sırasını umursamaz. |
| **Simetrik agregat (Looker/Omni deseni)** | Lehçe-bağımlı (Looker 40 lehçelik destek tablosu yayınlıyor), `DECIMAL(38,0)` taşması, yalnız sum/avg/count, ve hata **sorgu anında** kullanıcının yüzüne çıkıyor. Anahtar tekilliği ölçülebiliyorken kalıcı vergi ödemek anlamsız. |
| **Tenant başına forklanmış MDL'i varsayılan yapma** | N-yollu şema bakımı. Varsayılan: paylaşılan model + motor-seviyesi RLS; fork yalnız istisna. |
| **Grafik üretimini LLM'e verme** | `viz.py`'nin iki katmanlı deterministik `analyze()`/`recommend()` tasarımı bilinçli bir karardır (Show-Me / Cleveland-McGill, ADR-0024) ve upstream kaynak okunarak doğrulanmıştır. LLM'e Vega üretimi determinizm felsefesiyle çelişir. |
| **Bir cevabın `source`'unu gizlemek/eşitlemek** | `cube` ile `llm:*` **farklı garantiler** taşır. Rozet UI süsü değil, sözleşmedir. `_llm_source()` bilinmeyen sağlayıcıda bile `:` içeren bir değer döndürür ki LLM cevabı asla deterministik görünmesin. |
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
- **`_syn_hit` aynı hastalıkta** (`:333-336`) ve **boyut seçimini** bozuyor: `"yas" ⊂ "kıyasla"` →
  `"önceki ay ile kıyasla"` rapora istenmeyen bir `yas_grubu` GROUP BY ekliyor. **Henüz
  düzeltilmedi** — `_uncovered`'dan daha geniş etki alanı var (her boyut/ölçü eşleşmesi ondan
  geçiyor), ayrı bir tur olarak ele alınacak.
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
- **Çapraz-alan soruları `cube_router.py:1502`'de ölüyor** — `_match_cube`'da değil. 13 probun
  12'si orada; 8'inde cube ve ölçü zaten doğru çözülmüş. (Bu satır `cube["dimensions"]` okuyor.)
- ✅ **4 cube view-tabanlıydı** (`parti`, `ik`, `mizan`, `enerji_tesis` = kataloğun %31'i, en
  zengin ikisi dahil) → ilişki zenginleştirmesinden **sıfır kazanç** alıyorlardı. Faz 2'de üçü
  modele taşındı; `enerji_tesis` bileşik anahtar nedeniyle **bilinçli olarak** view kaldı (§3.2).
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
  - ❌ **drill raw leaf** (`drill.py`) — açık.
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
- **Telemetri kalıcı değil**: `docker inspect dima-backend-core` → `Mounts: []`,
  `DIMA_DATABASE_URL=sqlite:////app/logs/dima.db` konteyner katmanında. **Her build geçmişi siler.**
  `interaction_log`'da bugün **7 satır** var.

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
- **Test koşum reçetesi** (host'ta bağımlılık yok, prod imajda pytest yok):
  `docker build -t dima-test` = prod imaj + `pytest pyyaml httpx ruff`; sonra
  `docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python -m pytest -q`.
  Bind-mount sayesinde kod değişikliğinde imaj yeniden build edilmez. `--network none`
  hermetikliği garanti eder — testlerin ağa çıkmaya çalışması bir hatadır, yavaşlık değil.

---

## 7. Ölçüm sözleşmesi

| Ne | Nereden | Hedef |
|---|---|---|
| Intent / cache / Discovery payı | `GET /sadmin/interactions/route-distribution?days=N` (`admin_app/routers/interactions.py:144`) | **Intent ≥ %70 · Discovery < %30** |
| LLM'siz cevap oranı (tenant) | `GET /stats/today` (`app/routers/stats.py:39`) | artan |
| Cevap doğruluğu | `python -m eval.run` → `answered_precision` (Wilson CI) + `coverage` | baseline'ın **altına düşmez** (`tests/test_eval_gate.py`) |
| Deterministik tavan | `python lab/nl_corpus.py` (~1000 soru × 4 şirket, LLM'siz) | artan |
| Doğru cube/ölçü/boyut | `python lab/nl_accuracy.py` | artan |

**Ölçülen baseline (2026-08-02, `--network none`):**

| Metrik | Değer |
|---|---|
| eval `det` dilimi | 129 adım · **answered-precision %100** · **coverage %100** · chip %100 |
| **deterministik pay** | **%100** — yol dağılımı `intent=111` |
| pytest | **579 geçti / 0 hata**, ~95 sn |
| **`lab/nl_corpus.py` — GERÇEK deterministik tavan** | **8984 turda ~%64** (boyahane %64 · atiksan %67 · gulteks %62 · gitas %65) |

> ⚠️ **Eval'in %100'ünü kapsam sanma.** 111 cevabın 111'i intent yolundan geliyor, çünkü eval
> korpusu **zaten çalışan şeye göre kuratörlenmiş** — çapraz-alan boşluğuna hiç dokunmuyor.
> Boşluğun bu kadar uzun görünmez kalmasının sebebi de budur. **Gerçek tavan %64'tür**
> (`lab/nl_corpus.py`, 8984 tur, 4 şirket). Eval bir *regresyon kilididir*, kapsam ölçüsü değil.
> Aradaki 36 puan, planın tamamının dayandığı "kapsam, zekâ değil" tezinin sayısal karşılığıdır.

**Faz 0.4'ün ölçülen etkisi** (aynı korpus, öncesi/sonrası): OK **+6**, yanlış-cube/Discovery
(`CUBE-SAPMA`) **−25**, dürüst ret/netleştirme **+15**. Yani kapsam kapısının sıkılaştırılması
25 soruyu yanlış yerden çıkmaktan alıkoydu; bunların 6'sı doğru cevaba, 15'i dürüst
netleştirmeye gitti. Toplam OK payında net etki **−%0,25** — sessiz-yanlış sınıfını kapatmanın
bedeli olarak bilinçli kabul edildi (ADR-0008 yönü).

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
- Anlamlı bir Intent/Discovery oranı için **gerçek kullanım** gerekiyor; telemetri artık kalıcı
  (Faz 0.1) ama tablo pratikte hâlâ boş (7 satır).

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
| `backend/lab/panel/` | 4-model düşman denetimi (2026-07-24), 47 açık aksiyon. **Bulguları hâlâ büyük ölçüde geçerli** (§6). Çürütülmüş iddiaları da listeliyor — tekrar açma. |
| `Dima-0-100-Gorev-Takip-Dosyasi (2).md` | **ÜRÜN şartnamesi. Mimari otorite DEĞİL** — §8.3. |

### 8.2 ADR'ler fiziksel olarak YOK
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
- **Ölçülmüş fan-out güvenlik sertifikası** build artefaktı olarak. Snowflake, Cube, LookML,
  MetricFlow — hepsi modelciye *beyan ettiriyor*, sonra sonuçlarına karşı savunma yapıyor.
  Databricks açıkça *"runtime'da doğrulanmaz"* diyor.
- **Doğrulanabilir makbuz olarak Query Contract** (SQL + MDL sürümü + parametre + sonuç hash'i +
  join sertifikası + `always_filter` parmak izi). BI'da kimse üçüncü tarafın yeniden çalıştırıp
  hash eşleyebileceği bir makbuz vermiyor.
- **Güven-kapılı merdiven + risk-kapsam eğrisi.** Hiçbir sevk edilmiş BI ürünü abstention kapısı
  ya da risk-kapsam eğrisi yayınlamıyor.
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
- **View'lar ilişkilere katılamaz** — bir cube'un join alabilmesi için `base_object`'i **model**
  olmalıdır.
- **Bileşik anahtarlı ilişkiler ifade edilemez** (MDL `condition` tek kolonludur) → `enerji_tesis`
  gibi vakalar meşru view kullanımıdır.

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
