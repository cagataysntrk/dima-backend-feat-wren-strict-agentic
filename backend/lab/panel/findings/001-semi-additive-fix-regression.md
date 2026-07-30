# Panel Turu 001 — "Düzeltmenin kendi regresyonu": semi-additive as-of + sayısal hayalet-filtre + always_filter fail-closed

**Tarih:** 2026-07-24
**Senaryo tipi:** Regresyon avı (bir önceki panel P0 düzeltmesinin ikinci-derece etkileri)
**Kapsam:** commit `cb568a6` (semi-additive as-of, _value_token_hit sayısal dal, always_filter fail-CLOSED) + `6610b69` (K8 şema-guard)
**Modeller:** Haiku, Sonnet, Opus, Fable (paralel, dosya:satır kanıtlı)

## Araştırma sorusu
Dünkü panelin ürettiği 3 sessiz-yanlış düzeltmesi, DÜZELTTİĞİNDEN daha ince yeni sessiz-yanlışlar mı üretti? as-of dönüşümü tüm sorgu yollarına taşındı mı? fail-closed yeni hata modu açtı mı? sayısal dışlama gerçek filtreleri kaçırıyor mu?

---

## (a) UZLAŞILAR (yüksek güven — çoklu model + orkestratör doğruladı)

### U1 — [P0] KABLOSUZ MOTOR: cube derleyicisi semi_additive'i HİÇ okumuyor (Sonnet + Opus doğruladı, orkestratör onayladı)
`wren-core/core/src/mdl/cube.rs` (Sonnet: satır 125-392) ölçü ifadesini literal SELECT'e koyuyor; `additive`/`semi_additive`/`window`/`LAST_VALUE`/`OVER(PARTITION BY)` içeren **hiçbir dal yok**. semi-additive doğruluğu TAMAMEN `cube_router.py`'ın önden LLM'e kaçmasına (gran → None) ve as-of filtre oynatmasına bağlı. Metadata var, derleyici kör. **Filtre değişse bile SUM semantiği metadata-farkında değil** → düzeltme derleyici düzeyinde kozmetik, sadece router disiplinine dayanıyor.
- **Kanıt:** `app/cube_router.py:887` (`is_semi = measure in semi_additive`), `app/wren_service.py:177-179` (metadata üretimi), `wren-core cube.rs` (derleyici bu alanı okumuyor).

### U2 — [P0] AS-OF DÖNÜŞÜMÜ CONTINUATION YOLLARINA TAŞINMIYOR — düzeltmenin doğrudan regresyonu (Opus buldu, orkestratör KANITLADI)
route() içindeki as-of aralık→`lte` indirgemesi (`cube_router.py:892-897`) **yalnız route()'ta** var. İki paralel continuation yolu ham `date_filters` çıktısını (gte..lte aralığı) doğrudan cube_query'e yapıştırıyor, semi_additive'den habersiz:
- `app/routers/ask.py:728-730` — period-chip yolu ("bakiye" → sonra "temmuz için")
- `app/cube_router.py:517-522` — `deterministic_refine` ("bakiye" → sonra "temmuz ayı bazında")

Sonuç: takip mesajında bakiye = temmuz **net-hareketi** (dönem-içi SUM), ay-sonu bakiyesi DEĞİL. cb568a6'nın ilk turda önlediği net-hareket tuzağı takip turunda geri geliyor, cube-rozetli sessiz-yanlış. **DOĞRULANDI:** ask.py:728-730 ve cube_router.py:517-522 okundu; ikisi de `[f for f in filters if dim != tarih] + dfs` yapıyor, as-of indirgeme YOK.

### U3 — [P1] semi+gran/compare → None ama LLM'de KARŞILIK ALAN YOK (Opus + Sonnet)
`"aylara göre bakiye"` (semi+gran) → `route None` → LLM. Ama: (a) golden tek serbest-metin blob (`app/llm.py` ~107-110), vaka-başı retrieval yok; (b) `_schema_prompt` semi_additive/additivite bilgisini LLM prompt'una **hiç geçirmiyor**. LLM as-of/window'u bilmez → uydurur. Sessiz-yanlış cube-rozetinden LLM-rozetine TAŞINDI, çözülmedi. "Sorumluluğu boş kümeye atma" deseni.

### U4 — [P1] Multi-tenant always_filter ASİMETRİSİ (Sonnet buldu)
`logo-3/cubes/cari/metadata.yml` → `always_filter: "CANCELLED = 0"` VAR.
`mikro-v16/cubes/cari/metadata.yml` ve `netsis/cubes/cari/metadata.yml` → always_filter YOK.
Aynı "bakiye" sorusu Gülteks'te (Logo) iptal kayıtlarını filtreler, Atıksan'da (Mikro) filtrelemez → tenant'a göre biri doğru biri şişik. Sessiz asimetri.

---

## (b) ÇELİŞKİLER & KİM HAKLI (orkestratör doğruladı)

### Ç1 — Haiku "P0 measure-alias namespace uyuşmazlığı" iddiası → YANLIŞ (Opus + Fable haklı)
Haiku, MDL adı İngilizce ("balance") olup sinonim Türkçe ("bakiye") ise `is_semi` sessizce False kalır dedi (P0). **Orkestratör doğruladı, iddia ÇÜRÜK:** `_match_measure` (cube_router.py:376) `measure_synonyms` sözlüğünün ANAHTARINI döner; anahtar = `m["name"]` (wren_service.py:149-153); `semi_additive` de `m["name"]`'den (wren_service.py:177-179). Aynı ad-uzayı — synonym çözümü kanonik ada indirdiği için uyuşmazlık yok. Opus'un "namespace TEMİZ" ve Fable'ın bulguları doğru.

### Ç2 — Opus'un ilk hipotezi "mssql fail-closed DoS" → Opus KENDİ ÇÜRÜTTÜ (haklı)
İddia: fail-closed always_filter mssql SQL'i duckdb-parse edip patlar → tenant DoS. Opus kendi kanıtıyla çürüttü: enjeksiyon `_dialect_sql`'DEN ÖNCE, base (duckdb) lehçesinde yapılıyor (`wren_service.py:378-388`); parse edilen SQL her zaman derleyicinin duckdb çıktısı, asla kullanıcı/mssql SQL'i. DoS yolu yok. **AMA** gerçek P1 kalıntısı: `pred` (metadata'daki always_filter) `read="duckdb"` ile parse ediliyor (`wren_service.py:413`) — bir tenant always_filter'ı mssql-sözdizimiyle (`GETDATE()`, `[col]`, `ISNULL`) yazarsa o cube'un TÜM sorguları fail-closed 500.

---

## (c) HER MODELİN ÖZGÜN (diğerlerinin kaçırdığı) BULGUSU

- **Fable (dil):** `"3. ay bakiyesi"` → `filters=[islem_turu eq '3']`, period_optional=True, chip YOK. `_NUM_UNIT_AFTER` `\s*` noktayı geçemiyor (`cube_router.py:318`) → "ay" birimi görülmez → "3" değer sanılır → hayalet WHERE + yanlış dönem. Uçtan uca doğruladı. **[P0]** Ayrıca 14-char pencere çifte-tüketim: `"en yuksek bakiyeli 5 cari"` → hem `limit=5` hem `WHERE islem_turu=5` (cue-sayı arası 16 char > 14). Sözdizimsel eşdeğer `"bakiyesi en yuksek 5 cari"` doğru. **[P0/P1]**
- **Sonnet (derleyici + pack):** cube.rs literal-expr kanıtı (U1) + snapshot-tablo vs hareket-tablo ayrımının hiç doğrulanmaması (bir pack snapshot tabloyu `additive: semi` işaretlerse SUM çift sayar, lint yok) + multi-tenant always_filter asimetrisi (U4).
- **Opus (mimari):** as-of'un continuation yollarına taşınmaması (U2, en kritik) + fail-closed'ın `ask.py`'de `except Exception → LLM'e düş` ile yutulup always_filter'sız LLM SQL'e devri (iptal-kaydı korkusu LLM yolunda geri gelir) + enjeksiyon-sırası kanıtı.
- **Haiku:** doğru yönü işaret etti (derleyici as-of testi yok, snapshot ayrımı) ama namespace iddiasında spekülasyona kaydı (Ç1). Adil pay: "cube_sql çıktısını doğrulayan test YOK" gözlemi geçerli.

---

## (d) "MÜKEMMEL SENARYO" ÖNERİSİ
Semi-additive doğruluğu tek noktada (route) değil, ölçünün geçtiği HER yolda (route + is_period_only continuation + deterministic_refine + LLM prompt + derleyici lint) tutarlı olmalı. İdeal: `additive: semi` bir ölçü için (1) route as-of indirger, (2) continuation yolları aynı helper'ı çağırır, (3) LLM prompt'u additiviteyi bilir, (4) pack-lint snapshot-tablo+SUM kombinasyonunu reddeder, (5) golden as-of/window örneği taşır. Bugün yalnız (1) var.

---

## (e) SOMUT AKSİYON MADDELERİ (önem-sıralı)

1. **[P0] as-of'u ortak helper'a çıkar** — `_apply_semi_asof(cq, cube_meta)` yaz; `route()` (892-897), `ask.py:728-730` (period-chip) ve `cube_router.py:517-522` (deterministic_refine) ÜÇÜNDE de çağır. Takip turunda "temmuz için" bakiyesi net-hareket olarak toplanma regresyonunu kapatır. **En kritik.**
2. **[P0] `_NUM_UNIT_AFTER` ordinal+noktalama boşluğu** — `cube_router.py:318`: `q[m.end():]`'e match'ten önce `\s*[.\-]?\s*` atla VEYA `\b\d+\s*\.` ordinal desenini ("3. ay") ayrı dışla. "3. ay bakiyesi" hayalet filtresini kapatır.
3. **[P0/P1] 14-char pencere çifte-tüketim** — `cube_router.py:315`: pencereyi karakter yerine TOKEN tabanlı yap (önceki 2-3 token'da cue ara); ya da sayı top-N/limit olarak tüketildiyse aynı sayıyı değer adaylığından ÇIKAR. "en yuksek bakiyeli 5 cari" hem-limit-hem-WHERE hatasını kapatır.
4. **[P1] `_NUM_UNIT_AFTER` sonuna `\b`** — `cube_router.py:300-301`: `ay`/`bin`/`gun` alternatifleri "ayni/binada/ayakkabi" öneklerini yakalayıp gerçek enum filtresini düşürüyor. `(...)\b` ekle; kısa birimler için çekim: `(ay(lar|a|da|i)?)\b`.
5. **[P1] always_filter pred dialect-guard** — `wren_service.py:413`: `pred`'i `read="duckdb"` yerine metadata'da base-lehçe (duckdb) zorunlu kıl (build-time lint) ya da `dialect_sql` içinde SQL ile birlikte transpile et. mssql-sözdizimli always_filter → tüm-cube 500 riskini kapatır.
6. **[P1] LLM prompt'una additivite** — `app/llm.py _schema_prompt`: semi_additive ölçüleri + as-of/period-end talimatını prompt'a ekle; semi+gran None → LLM devrinde LLM as-of'u bilsin (U3).
7. **[P1] pack-lint: semi+snapshot** — `additive: semi` + `SUM(...)` expression + snapshot-tipi base_object kombinasyonunu build'de uyar/reddet (Sonnet). Kablosuz motorun gelecekteki suistimalini engeller.
8. **[P2] fail-closed'ı ask.py'de ayrı yakala** — `ask.py:884` `except Exception → LLM'e düş` always_filter RuntimeError'ını yutuyor; always_filter gereken cube için LLM fallback'ini engelle ya da dürüst hata dön (Opus D).
9. **[P2] multi-tenant always_filter asimetrisi** — mikro-v16/netsis cari cube'larına iptal-kaydı filtresi ekle ya da yokluğunu belgele+doğrula (U4).

---

## (f) SONRAKİ TUR (zorluk artışı)
**002 — "Continuation state machine sessiz-yanlışları":** in_convo takip yollarının (is_period_only, deterministic_refine, topic_switch, VQR replay) her biri semi-additive/entity-limit/coverage-gate korumalarını NE KADAR taşıyor? route()'ta olup continuation'da OLMAYAN her koruma bir regresyon adayı. Konuşma-durumu geçişlerinde (dönem ekle → boyut ekle → değer filtrele zinciri) hangi korumalar buharlaşıyor? cube_router.py continuation yolları × ask.py in_convo dalları matrisi çıkar, her hücrede route-paritesi denetle.
