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

> ⚠️ `demo/companies/demo-boyahane/views/parti_zengin/metadata.yml:2`'deki
> *"calc field'lar cube_query_to_sql'de JOIN'lenmiyor → demografiyi VIEW'da denormalize ederiz"*
> yorumunun **ilk yarısı doğru, çıkarılan sonuç yanlıştır.** Bu yanlış inanç 4 cube'u elle bakım
> gerektiren view'lara mahkûm etti. Bu belge o kaydı düzeltmek için var.

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

1. **LLM ham veri görmez.** Yalnız şema/metrik/boyut *adları* ve (sınırlı) enum değerleri gider.
   Hücre değeri asla. → *Bu bir CI testi olmalı, niyet beyanı değil.* KVKK'nın yurt-dışına-aktarım
   sorusunu kökten çözen kontrol budur.
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
| **NL-benzerlik cevap cache'i** | Yapısal olarak benzer ama anlamsal olarak farklı Türkçe sorular yanlış cevabı **güvenle** döndürür. Cache anahtarı **kanonik CubeQuery hash'i** olmalı (`tenant ⊕ cube ⊕ ölçü ⊕ boyut ⊕ aralık ⊕ filtre ⊕ RLS ⊕ mdl_version`). |
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
- **`_uncovered` herhangi-konum substring kullanıyor** (`cube_router.py:1160-1173`).
  `kar⊂ankara`, `mal⊂imalat`, `fire⊂firesiz`, `son⊂personel`, `gun⊂uygun`.
  Sonuç: `"firesiz partilerin cirosu"` → **fire toplamı** döndürüyor (tam tersi metrik).
  `_STOP_STEMS` prefix'i de yutuyor: `ver→veresiye`, `tek→tekstil`, `turu→turuncu`.
  `[a-z]+` regex'i yüzünden **sayılar kapsam kapısına görünmüyor**.
- **`_syn_hit` aynı hastalıkta** (`:333-336`) ve **boyut seçimini** bozuyor: `"yas" ⊂ "kıyasla"` →
  `"önceki ay ile kıyasla"` rapora istenmeyen bir `yas_grubu` GROUP BY ekliyor.
- **`_match_dims` tahkim yapmıyor** (`:592-637`): `"yaş grubu bazında fire oranı"` →
  `['ham_grup','yas_grubu']`. Fazla kolon = farklı grain = farklı sayı.
- **Olumsuzluk hiç ifade edilemiyor**: Rust **12** filtre operatörü destekliyor
  (`eq neq in not_in gt gte lt lte contains starts_with is_null is_not_null` — çalıştırılarak
  doğrulandı), Python **4** üretiyor (`eq in gte lte`). `"reddedilmeyen partilerin cirosu"` →
  reddedilenler **dahil**. `parse_cube_query` operatörü hiç denetlemiyor, `cube_sql` iletiyor,
  Rust uyguluyor — **eksik olan yalnız NL→operatör köprüsü.**

### 6.2 Yapısal boşluklar
- **`route()`'ta güven skoru yok.** Dört skor hesaplanıp **atılıyor** (`_match_cube:514-516`,
  `:550-562` — marj literal `4` ile karşılaştırılıp düşürülüyor; `_match_measure:577-583`;
  `_match_dims:596-613`). Bugün **belirsizlik en kötü kararı tetikliyor** (en az yönetilen katmana
  düşüş); tetiklemesi gereken bir netleştirme sorusudur.
- **Çapraz-alan soruları `cube_router.py:1502`'de ölüyor** — `_match_cube`'da değil. 13 probun
  12'si orada; 8'inde cube ve ölçü zaten doğru çözülmüş. (Bu satır `cube["dimensions"]` okuyor.)
- **4 cube view-tabanlı** (`parti`, `ik`, `mizan`, `enerji_tesis` = kataloğun %31'i, en zengin
  ikisi dahil) → ilişki zenginleştirmesinden **sıfır kazanç** alırlar.
- **3 cube'un hiç giden ilişkisi yok**: `cari`, `ticaret`, `enerji_sapma` — bu bir
  `relationships.yml` eksiğidir.
- **`models_enrich.yml` mekanizması var ama öksüz**: 31 ilişkiden 2'sinde kullanılıyor (%6,5) ve
  **ürettiği 7 calc kolonu hiçbir cube okumuyor.**

### 6.3 Güvenlik / doğruluk
- **`always_filter` baypasları**: Discovery ham SQL'i (`ask.py:2180,2209`), VQR ham-SQL replay'i
  (`:1529-1530` — cube'a sonradan eklenen filtre öğrenilmiş kayda uygulanmıyor), drill raw leaf
  (`drill.py:260`), ve manifest okunamadığında `wren_service.py:599-602`'deki
  `except Exception: return sql` **filtreyi sessizce düşürüyor**. Ayrıca *filtreli bir modele
  join'lemek* de baypas ediyor (ölçüldü: 34M TL `alis` verisi `tur='satis'` filtresini geçti).
- **`compose()` kilitsiz `rmtree` yapıyor** (`compose.py:77-86`). Build boyunca (~130-160 ms)
  `target/mdl.json` **yok**; bu pencerede gelen sorgu ya `FileNotFoundError` alır ya da yukarıdaki
  `always_filter` yutmasına düşer. `company_registry`'nin per-slug kilidi var ama
  `compose_and_build` (`main.py:55`, `materialize.py:122`, `measures.py:284`) **onu kullanmıyor**.
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
| pytest | **526 geçti / 0 hata**, 81–96 sn |

> ⚠️ **Bu %100'ü yanlış okuma.** 111 cevabın 111'i intent yolundan geliyor, çünkü eval korpusu
> **zaten çalışan şeye göre kuratörlenmiş** — çapraz-alan boşluğuna hiç dokunmuyor. Boşluğun bu
> kadar uzun görünmez kalmasının sebebi de tam olarak budur. Gerçek tavan `lab/nl_corpus.py`
> (~1000 soru × 4 şirket) ile ölçülür; eval bir *regresyon kilididir*, kapsam ölçüsü değil.

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
 └─▶ route()  →  (CubeQuery, confidence)          ← kalibre skor, binary değil
        ├─ yüksek  → source=cube            (0 token)
        ├─ orta    → Intent-JSON, aday setiyle → source=cube+llm
        ├─ düşük   → NETLEŞTİRME CHIP'İ     ← belirsizlik en İYİ kararı tetikler
        └─ en düşük→ Discovery              ← istisna, ve her biri bir terfi adayı
                        └─▶ terfi kuyruğu → YAML diff → insan onayı → pack'e PR

Cube boyutları = kendi base_object'i
               ⊕ ilişki grafiğinden MEKANİK türetilmiş boyutlar
                 · yalnız MANY→ONE · ≤2 sıçrama
                 · FAN-OUT SERTİFİKALI (ölçülmüş tekillik, MDL sürümüne mühürlü)
                 · provenance taşır: {model, kolon, ilişki, hop, doğrulama_tarihi}

Her cevap → yeniden çalıştırılıp hash eşlenebilen bir MAKBUZ
```

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
- **CubeQuery olarak ifade edilmiş katkı/mix ayrıştırması.** Snowflake `TOP_INSIGHTS`, Power BI
  Key Influencers, Tableau Pulse — hepsi semantic layer'ın **dışında**, dolayısıyla sonuçları
  yeniden-tarihlenebilir/kırılabilir/sözleşmeli değil.
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
