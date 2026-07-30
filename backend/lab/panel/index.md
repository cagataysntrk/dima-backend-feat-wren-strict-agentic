# dima 4-Model Karşılaştırma Paneli — Canlı Özet

**Son güncelleme:** 2026-07-24
**Tamamlanan tur:** 5
**Toplam açık aksiyon:** 47 (çok sayıda P0; biri güvenlik regresyonu, biri KVKK cross-tenant, biri eşzamanlılık-bozulma). Ortak çözüm eksenleri: ortak-koruma-helper, niyet-imza-katmanı, ek-farkında-kapsam, güvenlik-simetrisi, tenant-izolasyon-arka-plana-genişletme

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
