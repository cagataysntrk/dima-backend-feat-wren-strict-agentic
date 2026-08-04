# dima 4-Model Karşılaştırma Paneli — Canlı Özet

**Son güncelleme:** **2026-08-04** *(FAZ 1.13 denetimi — panel yenilendi)* · önceki: 2026-07-24
**Tamamlanan tur:** 5
**Aksiyon sayısı:** **47** — ✅ **ölçüldü, beyan doğru**: `9+10+9+10+9`
*(`grep -c "^[0-9]*\. \*\*\[" lab/panel/findings/*.md`)*. Bu deponun *"beyan var, sayım
yok"* sınıfı burada **yakalanmadı**: sayı gerçekten 47.

**Bugünkü durum: ✅ 6 kapandı · ◐ 3 kısmen · ⊘ 2 ölçülemedi/karar değişti · ⬜ 36 açık**
*(6+3+2+36 = 47).* ⚠ İlk yazımda burada **38** yazıyordu ve tablodaki gerçek sayım
**36**'ydı — yani bu satırın kendisi, panelin yakaladığı *"beyan ≠ sayım"* sınıfına düştü.
Düzeltildi ve **kapıya çevrildi** (`tests/test_panel_tazeligi.py`): toplam artık **47'ye
eşit olmak zorunda**. Ortak çözüm eksenleri (hâlâ
geçerli): ortak-koruma-helper, niyet-imza-katmanı, ek-farkında-kapsam, güvenlik-simetrisi,
tenant-izolasyon-arka-plana-genişletme.

---

## 🔴 DURUM DENETİMİ — FAZ 1.13 (2026-08-04)

> **Kapananlar İŞARETLENİR, SİLİNMEZ** (MIMARI §10). Bir denetim panelinin değeri
> *"neyin düzeldiğini"* değil, **neyin düzeldiğini KİMİN ne zaman kanıtladığını**
> taşımasıdır. Silinen bir madde, hiç bulunmamış bir maddeyle aynı yere düşer.
>
> 🔴 **Durum YALNIZ BURADA tutulur.** `findings/*.md` dosyalarına durum sütunu
> **eklenmedi**: aynı bilginin iki sahibi olurdu ve biri güncellenip öteki unutulurdu —
> bu deponun en sık kaydettiği kusur sınıfı. Bulgu dosyaları **tarihsel kayıttır**,
> bugünkü gerçeği bu tablo söyler.
>
> ⚠ **Doğrulama yöntemi ve SINIRI yazılı:** her satır **kaynak koddan** doğrulandı
> (grep/okuma). Kod okumakla ölçülemeyen davranışsal iddialar *"kapandı"* diye
> **işaretlenmedi** — `⊘` ile ayrıldı. *Doğrulanmamış bir kapanış, açık bir maddeden
> daha tehlikelidir: kimse ona bir daha bakmaz.*

| # | Aksiyon | Durum | Kanıt (kaynak kod) |
|---|---|---|---|
| **R5-1** | [P0 KVKK] Scheduler tenant-farkında motor | ✅ **KAPANDI** | `app/schedules.py:422-442` — `registry.service_for(slug)`; `state.wren` yalnız *tenant'sız eski kayıt* dalında |
| **R5-2** | [P0] Atomik compose + per-slug lock | ✅ **KAPANDI** | `app/compose.py` `DerlemeKilidi` + `os.replace` atomik yazma · `company_registry.py:56` `build_lock_for(out)` *(FAZ 1.4 kilidi de aynı yarışı kapattı)* |
| **R3-1** | [P0] Kapsam eşleşmesini ek-farkında yap | ✅ **KAPANDI** | `cube_router._covers` — üç kural (ek SONA gelir · olumsuzluk eki YASAK · geçerli ek zinciri). Panelin kendi canlı vakası (`firesiz` ⊄ `fire`) fonksiyonun belgesinde yazılı |
| **R3-2** | [P0] Negasyon üretimi (`not_in`/`neq`) | ✅ **KAPANDI** | `cube_router.py:3021-3040` — *"2. GEÇİŞ — DIŞLAMA"*, `op = "neq" if len(matched) == 1 else "not_in"` |
| **R4-4** | [P0] `guard_sql` tablo-allowlist | ✅ **KAPANDI** | Katman B: `app/katman_b.py::zorla` (`referans_modeller` sqlglot AST + `wren.policy.resolve_model_name`) → `/query` (`routers/query.py:48`) **ve** `/ask` Discovery (`routers/ask.py:3299` `sarmala`). FAZ `1.3b` + `1.3b/2` |
| **R2-8** | [P1] `period_optional` taşınabilir | ✅ **KAPANDI** | `cube_router.py:3245` — `cube_query`'ye gömüldü (`is_period_optional`, `:639`) |
| **R4-8** | [P1] RLAC/CLAC/PII maskeleme | ◐ **KISMEN** | RLAC `app/rls.py` (FAZ 1.1) · CLAC `rls.clac_manifesti` (1.2a) · `app/pii.py` tümleyen maskeleme. ⚠ **MDL kolon metadata'sına `pii/masked` bayrağı YOK** — CLS bugün `sensitivity` eşiğiyle çalışıyor; `motor_cls=on` hâlâ **36 çağrı sitesi** borcuna kilitli |
| **R1-5** | [P1] `always_filter` pred dialect-guard | ◐ **KISMEN** | `wren_service.py:1121` yüklem'in **dialect-nötr** olması gerektiğini **belgeliyor**, ama `:1156` hâlâ `read="duckdb"` ile ayrıştırıyor ve **build-time lint YOK** — beyan var, kapı yok |
| **R5-7** | [P1] `run_due` sessiz-hata loglama | ◐ **KISMEN** | `app/schedules.py` beş ayrı `_log.warning` taşıyor (`:79/:102/:123/:144/:159`), ama `run_due` döngüsünün kendi `except Exception → continue` dalı **audit'e** düşmüyor |
| **R2-6** | [P0] `entity_limit` continuation'da korunsun | ⊘ **ÖLÇÜLEMEDİ** | `ask.py:1241` `cq.pop("entity_limit")` **hâlâ var** ama artık **gerekçeli**: *"AskResponse.cube_query GERÇEKTEN NEYİN çalıştırıldığını yansıtsın"*. Panelin iddiası (top-N monotonluğu) bir **davranış** iddiasıdır; kod okumakla çözülmez, **senaryo ölçümü** ister |
| **R3-3** | [P0] STOP_STEMS kısa-prefix'leri | ⊘ **KARAR DEĞİŞTİ** | `cube_router._is_stop_word` (`:1948`) — önek semantiği **bilerek korundu** ve **denendiğinde kırdı** (`grafi`+`k` geçerli ek zinciri değil → grafik soruları kapsam kapısına takıldı, 4 test). Kazayla yutulanlar `_STOP_EXACT` **tam-kelime** listesiyle çözülüyor. *Panelin önerdiği çözüm ölçülüp REDDEDİLDİ; sorun başka yoldan kapandı* |

### Açık kalan 36 — hangi faza ait

| Küme | Aksiyonlar | Sahibi |
|---|---|---|
| **Ortak koruma helper'ı** (semi as-of + coverage; route · refine · period-chip · VQR replay) | R1-1 · R2-1 · R2-7 | **FAZ 2** (semantik çekirdek) — `_apply_semi_asof` bugün **yok** (`grep` boş) |
| **Niyet-imza katmanı** (ADD/REMOVE/REPLACE/NEGATE/COMPARE) | R2-2 · R2-3 · R2-4 · R2-5 · R3-4 | **FAZ 2/5** |
| **Sayı/birim ayrıştırma** (ordinal · pencere · `\b`) | R1-2 · R1-3 · R1-4 · R3-8 | **FAZ 2** — `_NUM_UNIT_AFTER` (`:605`) hâlâ sondaki `\b`'siz, pencere 10 karakter |
| **LLM güvenlik ağı** (prompt kısıtları · red sebebi · self-consistency · retrieval) | R1-6 · R4-2 · R4-3 · R4-5 · R4-6 · R4-7 · R4-9 · R4-10 | **FAZ 5** (anlatım/LLM) |
| **Serbest-SQL always_filter enjeksiyonu** | R4-1 | **FAZ 1.1 kuyruğu** — RLAC motora devredildi ama `motor_rls` kademesi `on` değil |
| **Çok-tenant çalışma zamanı** (invalidate · schema lazy-fill · VQR scope · tek-yol · disk izolasyonu) | R5-3 · R5-4 · R5-5 · R5-6 · R5-8 · R5-9 | **FAZ 3/6** |
| **Pack hijyeni** (semi+snapshot lint · always_filter asimetrisi · fail-closed yutma) | R1-7 · R1-8 · R1-9 | **FAZ 2.1** (grain sözleşmesi) |
| **Belirsizlik sinyali + kalibrasyon** | R3-5 · R3-6 · R3-7 · R3-9 · R2-9 · R2-10 | **FAZ 2/5** |

### Sıradaki tur (006) — DEĞİŞMEDİ, ama ön koşulu yazıldı

006 (onboarding/semantik keşif doğruluğu) hâlâ doğru sıradaki tur. ⚠ **Ön koşul:** FAZ 2
grain sözleşmesi inmeden koşulursa panel, FAZ 2'nin **zaten planladığı** kusurları
*"yeni bulgu"* diye rapor eder — ve 47'lik liste, kapanmakta olan maddelerle **şişer**.

## En güçlü çapraz-senaryo uzlaşıları
- **[P0] KABLOSUZ MOTOR:** cube derleyicisi (wren-core `cube.rs`) `semi_additive`/`additive` metadata'sını HİÇ okumuyor. semi-additive doğruluğu tamamen `cube_router.py`'ın önden LLM'e kaçması + as-of filtre oynatmasına bağlı — derleyici düzeyinde koruma yok. (R1: Sonnet+Opus)
- **[P0] AS-OF/KORUMALAR CONTINUATION'DA YOK:** route()'taki semi-additive as-of + coverage-gate + entity_limit korumaları takip yollarına (deterministic_refine, is_period_only, VQR replay) taşınmıyor → takip turunda "temmuz için" bakiyesi net-hareket olur, tanınmayan içerik sessizce taşınır, top-N monotonluğu kırılır. (R1'de keşif, R2'de 3 model tam doğrulama + genişletme)
- **[P0] NİYET-OPERATÖRÜ KÖRLÜĞÜ (R2 kök-neden):** `_STOP_STEMS` "ekle/cikar/degil/yerine/kiyasla/karsilastir"ı kapsam-dolgusu sanıyor → negasyon/geri-alma/karşılaştırma niyetleri deterministik pozitif-birleştirici yollara sızıp sessiz-yanlış üretiyor ("değil Y"→dışlananı dahil eder, "kırılımı çıkar"→sessiz no-op, "ile kıyasla"→LAG yutulur). (R2: Fable buldu, orkestratör STOP_STEMS'i okuyarak doğruladı)
- **[P0] KAPSAM KAPISI SUBSTRING KÖRLÜĞÜ + NEGASYON EKİ YUTMA (R3, CANLI kanıt):** `_uncovered:791` `k in w` herhangi-konum substring → "kar"⊂"ankara", "fire"+"-siz"⊂"firesiz" → `"firesiz partilerin cirosu"` gerçek route()'ta FİRE TOPLAMI döndürüyor (Fable çalıştırdı). STOP_STEMS `startswith` (793) "ver"→veresiye/"tek"→tekstil/"turu"→turuncu yutuyor.
- **[P0] ÜÇLÜ İFADE BOŞLUĞU / FORK ALT-KÜMESİ (R3 taç, Opus):** Rust cube derleyicisi 12 filtre operatörü destekliyor (eq/in/gte/lte/gt/lt/neq/not_in/contains/starts_with/is_null/is_not_null) ama Python router yalnız 4 üretiyor (eq/in/gte/lte — orkestratör grep'le doğruladı). `neq`/`not_in` HAZIR ama deterministik yol negasyon üretmiyor → "hariç" niyeti filtresiz SUM. llm.py:170 LLM'e neq diyor; sadece deterministik yol kör.
- **[P0 GÜVENLİK] SERBEST-SQL KORUMASIZ (R4 taç, Opus+Sonnet, KANITLANDI):** LLM serbest-SQL (`query()`:498 / `dry_plan()`:477) yalnız `guard_sql` (SELECT-only) geçiyor; `_inject_always_filter` YALNIZ cube_sql:379'da → serbest-SQL always_filter (CANCELLED=0) + R1 fail-closed'u BAYPAS ediyor. R1-R3'ün "LLM'e düş" çözümlerinin hepsi bu korumasız yola gidiyor. Ayrıca `_schema_prompt` semi_additive/always_filter'ı LLM'e hiç geçirmiyor (LLM as-of/iptal bilmez), golden tek-blob (retrieval yok), self-consistency OpenAI-compat'ta temp=0 → sahte-güven. "LLM güvenlik ağı" büyük ölçüde kablosuz-motor.
- **[P0 KVKK] SCHEDULES CROSS-TENANT MOTOR KAÇAĞI (R5 taç, Sonnet+Fable, KANITLANDI):** `run_schedule` (schedules.py:184) `svc = state.wren` (DEFAULT tenant) — `sched["tenant_id"]` connection'da hiç kullanılmıyor. Tenant B'nin cron'u tenant A'nın DB'sini sorguluyor → B'nin raporunda A'nın verisi. RLS yalnız bildirim görünürlüğünü sınırlıyor, motoru değil.
- **[P0 EŞZAMANLILIK] REGISTRY COMPOSE RACE (R5, Opus, KANITLANDI):** `service_for` (company_registry.py:37-46) compose+build'i lock DIŞINDA çalıştırıyor; `compose` (compose.py:75-77) in-place `rmtree(out)` yapıyor → iki eşzamanlı istek/recompose aynı slug dizinini çakıştırıp bozuk `target/mdl.json` üretiyor, kalıcı tenant arızası.

## En kritik açık aksiyonlar (önem-sıralı, R1+R2 birleşik)

> ⚠ **Bu liste TUR 5'in (2026-07-24) fotoğrafıdır ve DEĞİŞTİRİLMEDİ** — bugünkü durum
> için yukarıdaki **DURUM DENETİMİ** tablosuna bak. Buradaki maddelerin yanına *"kapandı"*
> yazmak, durumun **ikinci bir sahibi** olurdu; ikisi ayrıştığında hangisinin doğru olduğu
> bilinemezdi. *Tarihsel kayıt, güncellenmediği için değerlidir.*
1. **[P0] ORTAK KORUMA HELPER'I** — `_apply_semi_asof` + coverage-gate'i TÜM yollarda çağır: route (892-897), deterministic_refine (455-522), is_period_only (ask.py:728-730), VQR replay (ask.py:626). R1+R2'nin en büyük ortak çözümü — semi net-hareket + coverage-kaçağı regresyonlarını tek hamlede kapatır.
2. **[P0] NİYET-OPERATÖRLERİNİ STOP_STEMS'ten ÇIKAR** (cube_router.py:718-732) — "ekle/cikar/degil/yerine/kiyasla/karsilastir" dal-seçici olsun; ters-değer + sessiz-undo + yutulan-compare ortak kökü.
3. **[P0] `_COMPARE_HINTS` denetimini deterministic_refine'a ekle** — LAG niyeti döneme daraltılmasın.
4. **[P0] Boyut/filtre-kaldırma (REMOVE) dalı** — "kırılımı çıkar" sessiz no-op yerine gerçek kaldırma.
5. **[P0] Değer-negasyonu** — "X değil Y"/"hariç" dışlananı `in`'e dahil etmesin.
6. **[P0] entity_limit continuation'da KORU** (ask.py:483-484 pop→in-filtre) — top-N monotonluğu + route paritesi.
7. **[P0] `_NUM_UNIT_AFTER` ordinal/noktalama** (`cube_router.py:318`) — "3. ay bakiyesi" hayalet filtresi.
8. **[P0/P1] 14-char pencere çifte-tüketim** (`cube_router.py:315`) — "en yuksek bakiyeli 5 cari". Token-tabanlı pencere.
9. **[P1] `_NUM_UNIT_AFTER` sonuna `\b`** (`:300-301`) — "ayni/binada" öneki gerçek filtreyi düşürüyor.
10. **[P1] VQR replay'e coverage + semi guard** (ask.py:626).
11. **[P1] period_optional taşınabilir** — AskResponse alanı ya da cube_query gömme.
12. **[P1] always_filter pred dialect-guard** (`wren_service.py:413`).
13. **[P1] LLM prompt'una additivite** (`llm.py _schema_prompt`).
14. **[P1] pack-lint: semi+snapshot+SUM**.
15. **[P1] Çekimli ay/dönem toleransı + "ondan önceki" anaforası**.
16. **[P2]** fail-closed'ı ask.py'de ayrı yakala; multi-tenant always_filter asimetrisi; time_dim hardcode→dinamik; dict()→deepcopy standardize.

## Ortak çözüm eksenleri (birçok aksiyon bunlara indirgenir)
- **Ortak-koruma-helper** (R1+R2): `_apply_semi_asof` + coverage'ı route + deterministic_refine + is_period_only + VQR replay'de çağır.
- **Niyet-imza katmanı** (R2+R3): tek sınıflandırıcı (ADD/REMOVE/REPLACE/NEGATE/COMPARE/FILTER/PERIOD/RANK), STOP_STEMS'ten önce; Sınıf-A niyetleri (not_in/gt/lt) deterministik üret.
- **Ek-farkında kapsam** (R3): substring yasak, tam-kelime-ya-da-izinli-çekim; negasyon ekleri izinli değil.

## Çürütülen iddialar (tekrar açma)
- Haiku "measure-alias namespace P0" (R1) → YANLIŞ; namespace kanonik ad'da tutarlı.
- Opus "mssql fail-closed DoS" (R1) → Opus kendi çürüttü; enjeksiyon dialect'ten önce base lehçede.
- "deterministic_refine shallow-copy mutasyon" (R2) → YANLIŞ; deepcopy kullanıyor (cube_router.py:420,434), state zinciri güvenli.
- Haiku R3 uydurma-kelime örnekleri (karapekte/tondaja) spekülatif; Fable GERÇEK pack sinonimleriyle (fire/mal) kanıtladı — mekanizma aynı (791), Fable vakaları operasyonel.
- Haiku "VQR cross-tenant sızıntısı P0" (R5) → Fable çürüttü; non-default tenant'ta vqr=None (require_company), bugün sızıntı yok, latent+işlevsel boşluk.
- "IDOR: başka tenant slug'ı" (R5) → YOK; slug yalnız imzalı JWT claim'inden (dependencies.py:132), overlay scope da doğru — izolasyonun auth tarafı sağlam.

## Sıradaki tur
006 — Onboarding/semantik keşif otomasyonu doğruluğu: yeni tenant pack'i canlı DB introspection'dan (ADR-0017 fingerprint, netsis/logo) ne kadar güvenilir türetiliyor? Yanlış tip/kardinalite algısı, otomatik always_filter/semi_additive işaretleme (kablosuz-motoru besler mi), enum-mining (_MAX_ENUM=25) hayalet-filtre, pack-lint boşlukları, çok-firma/dönem binding. Onboarding = tüm downstream doğruluğun temeli.
