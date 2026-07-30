# Panel Turu 002 — Continuation state-machine route-paritesi

**Tarih:** 2026-07-24
**Senaryo tipi:** Parite denetimi (ilk-tur route() korumaları takip-turlarında buharlaşıyor mu)
**Kapsam:** `app/cube_router.py` (route 814-952, deterministic_refine 404-547, is_period_only 255-279), `app/routers/ask.py` (in_convo dalları 598-768, VQR replay 605-640, is_period_only 702-741, _cube_response 464-518), `app/schemas.py` (83-106)
**Modeller:** Haiku (semi quadrant), Sonnet (coverage/entity quadrant), Opus (state-machine quadrant), Fable (NL classification quadrant)

## Araştırma sorusu
route() ilk sorguda güçlü koruma uygular. Takip mesajları (in_convo) deterministic_refine / is_period_only / VQR replay yollarından geçer. route()'ta OLAN hangi koruma bu yollarda YOK? Konuşma zincirinde hangi state buharlaşıyor? Türkçe takip niyeti yanlış dala mı gidiyor?

---

## KÖK NEDEN (çapraz-model, orkestratör KANITLADI)
**Niyet-operatörleri kapsam-dolgusu (STOP_STEMS) sanılıyor → deterministik pozitif-birleştirici yollara sızıyor.**
`_STOP_STEMS` (cube_router.py:712-732) `"ekle", "cikar", "degil", "yerine", "karsilastir", "kiyasla"` içeriyor — DOĞRULANDI. Bunlar dolgu DEĞİL, niyet operatörü (ADD/REMOVE/NEGATE/COMPARE). Dolgu sayıldıkları için `_coverage_ok` kapısı bu niyetleri yakalayamıyor; deterministik yollar bunları görmezden gelip pozitif filtre/replace uyguluyor. Fable buldu, orkestratör STOP_STEMS içeriğini okuyarak doğruladı. Bu, aşağıdaki P0'ların çoğunun ortak kaynağı.

---

## (a) UZLAŞILAR (yüksek güven)

### U1 — [P0] SEMI-ADDITIVE koruması continuation'da TAMAMEN YOK (Haiku + Sonnet + Opus, 3 model)
route() 887-897'deki `is_semi`/gran-guard/as-of-lte indirgeme, `deterministic_refine`'da (404-547) ve `is_period_only`'de (ask.py:702-741) ve VQR replay'de (ask.py:605-640) HİÇ yok. `deterministic_refine` grep'inde `semi`/`is_semi` yok. Sonuç zinciri:
- "bakiye" → sonra "aylara göre" → deterministic_refine gran ekler (cube_router.py ~455-462), route()'un `if gran: return None` kaçışı YOK → cube-rozetli net-hareket serisi (sessiz-yanlış).
- "bakiye" → sonra "temmuz için" → is_period_only ham gte..lte yapıştırır (ask.py:730), as-of-lte indirgeme YOK → temmuz net-hareketi.
- VQR'da saklı `gran=month`+semi cq_v → replay doğrudan _cube_response, koruma çalışmadan.
Bu, **R1'in en kritik bulgusunun (as-of taşınmıyor) TAM doğrulaması + genişletmesi.**

### U2 — [P0] KAPSAM KAPISI is_period_only ve VQR replay'de YOK (Sonnet + Opus)
`_coverage_ok` yalnız route() (918) ve deterministic_refine (540) yollarında var. is_period_only (ask.py:702-733) ve VQR replay (ask.py:605-640) coverage-gate ÇAĞIRMIYOR → önceki turda LLM'in yerleştirdiği/tanınmayan içerik takip turunda sessizce taşınıyor. "ciro+istanbul" VQR hit'inde istanbul filtrelenip atlanabilir, coverage ihlali yutulur.

### U3 — [P0] entity_limit continuation'da `in`-filtreye çözülüp cube_query'den SİLİNİYOR → monotonluk kırık (Opus)
`_cube_response_unsafe` (ask.py:483-484) `el = cq.pop("entity_limit")`, ilk-N değerler `in:[...]` filtresine ÇİVİLENİR, entity_limit döndürülen cube_query'den düşer. Sonra "10 cari yap" → yeni top-N eski 5'in İÇİNDEN seçilir (genişleyemez). route() yolu (ask.py:880-883) entity_limit'i TUTAR → iki yol farklı state provenance döndürüyor. Top-N artık idempotent değil, geçmişe bağımlı.

### U4 — [P1/latent-P0] period_optional AskResponse şemasında YOK, continuation'a taşınmıyor (Opus + Haiku)
`AskResponse` (schemas.py:83-106) `period_optional` alanı taşımıyor; route() onu iç `plan` dict'inde tutup dönem-chip kapısında (ask.py:866) kullanıyor. Continuation'da kayboluyor. Bugün `not in_convo` guard'ı chip'i maskelediği için latent; dönem-kontrolü in_convo'ya açılırsa (mantıklı, çünkü "aylara göre" bakiyeyi net-harekete iter) semi bayrağı olmadan yanlış chip tetiklenir.

---

## (b) ÇELİŞKİLER & KİM HAKLI (orkestratör doğruladı)

### Ç1 — deterministic_refine "shallow copy mutasyon" tehlikesi → YANLIŞ; deepcopy kullanıyor (Opus haklı)
Opus `deterministic_refine`'ın `import copy` + `cq = copy.deepcopy(prev)` kullandığını buldu (cube_router.py:420, ~434). **Orkestratör doğruladı:** satır 420 `import copy` mevcut. deterministic_refine yolunda state DOĞRU biriktiriliyor (deepcopy, zincir korunuyor) — Opus haklı. Shallow risk yalnız ask.py:703 (`dict(body.cube_query)`) ve ask.py:483'te, ama oralarda mutasyon liste-yeniden-bağlama olduğundan bugün güvenli (kırılgan konvansiyon, P1-D).

### Ç2 — _BREAKDOWN_HINTS dejenere koruması refine'da: kısmen (Sonnet nüanslı, haklı)
route() 903-904 "bazında ama boyut yok → None". deterministic_refine'da bu kapı YOK; genelde dolaylı None ile örtüşür AMA "bu ay makine bazında" gibi BAŞKA bir değişiklik (dönem eklendi, `changed=True`) varsa boyutsuz kırılım cq döner (543-544), coverage değer-indeksine bağlı. Sonnet'in nüansı doğru: parite teknik olarak kısmi, kombinasyon-kaçağı gerçek (P1).

---

## (c) HER MODELİN ÖZGÜN BULGUSU

- **Fable (NL, en zengin özgün hasat):**
  - [P0] `"X değil Y göster"` değer düzeltmesi TERSİNE: `_value_token_hit` ikisini de eşler → `in [Beyaz, Siyah]` (dışlanan değer dahil edilir). Değer negasyonu yok, "degil" STOP_STEMS'te → coverage kurtarmaz. (cube_router.py:494-514, corr-kalıbı yalnız ÖLÇÜ için 419-425.)
  - [P0] `"makine kırılımını çıkar"` → sessiz no-op "başarı": boyut-kaldırma dalı YOK; "cikar" STOP_STEMS'te → `already=True` → aynı rapor döner, trace "refine başarılı" der. Kullanıcı kırılımın kalktığını sanır.
  - [P0] `"önceki/geçen ay İLE kıyasla"` → refine dönem-filtresine çevrilip LAG karşılaştırması yutuluyor; `_COMPARE_HINTS` yalnız route()'ta (836), refine'da yok. İroni: "geçen ayLA" (ekli) eşleşmez→LLM, "geçen ay İLE" eşleşir→sessiz-yanlış.
  - [P1] Çekimli ay adları ("temmuzu/temmuza/temmuzda") deterministik dönem yoluna uymuyor (regex `\b...\b` sonek-toleranssız); sistematik delik.
  - [P1] `"ondan önceki ay"` anaforası bugüne çıpalanıyor (`date.today()`), önceki rapor dönemine göreli değil → sessiz yanlış dönem.
  - [P2] chip/VQR dallarında time_dim `"tarih"` HARDCODED (ask.py:627-631,728), refine `time_dims[0]` — farklı adlı time-dim'li ilk cube'da çelişki/geçersiz kolon.
- **Opus (state-machine):** entity_limit monotonluk kırığı (U3), period_optional şema kaybı (U4), deepcopy doğrulaması (Ç1), `already` no-op maskesi (çok-niyette bir niyet no-op, diğeri tanınmazsa sessiz aynı-rapor).
- **Sonnet (coverage/entity):** parite tablosu (coverage/breakdown/entity/semi/needs_period × 3 continuation yolu), VQR replay'in coverage+semi'yi atlaması, breakdown kombinasyon-kaçağı.
- **Haiku (semi):** en net semi parite tablosu (koruma×route×refine×is_period_only), 3 somut P0 satırı; güçlü, odaklı, spekülasyonsuz (R1'deki namespace hatasını tekrarlamadı).

---

## (d) "MÜKEMMEL SENARYO" ÖNERİSİ
Continuation bir DURUM MAKİNESİ: her koruma (semi-additive, coverage, entity_limit, breakdown, compare, negation, undo) TEK bir yerde (route veya ortak helper) tanımlanıp HER giriş yolundan (route, deterministic_refine, is_period_only, VQR replay) geçmeli. Niyet operatörleri (ekle/çıkar/değil/kıyasla) coverage-dolgusu DEĞİL, dal-seçici sinyal olmalı. İdeal: takip mesajı önce niyet-sınıflandırmadan (ADD/REMOVE/REPLACE/NEGATE/COMPARE/PERIOD) geçer, sonra ilgili dal korumalı-ortak-helper çağırır.

---

## (e) SOMUT AKSİYON MADDELERİ (önem-sıralı)

1. **[P0] Ortak koruma helper'ı + tüm continuation yollarında çağır** — R1 aksiyon 1'i genişlet: `_apply_semi_asof` + coverage-gate'i deterministic_refine (455-522), is_period_only (ask.py:728-730), VQR replay (ask.py:626) üçünde de uygula. semi-additive net-hareket regresyonunu TÜM takip yollarında kapatır.
2. **[P0] Niyet-operatörlerini STOP_STEMS'ten çıkar, dal-seçici yap** — `"ekle/cikar/degil/yerine/kiyasla/karsilastir"` (cube_router.py:718-732) coverage-dolgusu olmaktan çıksın; bunlar geçtiğinde ilgili dal (ADD/REMOVE/NEGATE/COMPARE) seçilsin ya da (ucuz yama) coverage ✗ ile LLM'e düşsün. Fable'ın 3 P0'ının (ters-değer, sessiz-undo, yutulan-compare) ortak kökünü kapatır.
3. **[P0] `_COMPARE_HINTS` denetimini deterministic_refine başına ekle** — route:836 ile simetri; "ayla/yılla kıyasla" LAG niyeti döneme daraltılmasın (cube_router.py refine girişi).
4. **[P0] Boyut/filtre-kaldırma dalı** — "kırılımı çıkar / X filtresini kaldır" için deterministic_refine'a REMOVE dalı; sessiz no-op "başarı" yerine gerçek kaldırma ya da LLM.
5. **[P0] Değer-negasyonu** — `"X değil Y"` / "hariç" değer filtresinde dışlananı `in`'e dahil etme; corr-kalıbını değer eşleşmesine de uygula (cube_router.py:494-514).
6. **[P0] entity_limit'i continuation'da KORU** — `_cube_response_unsafe` (ask.py:483-484) entity_limit'i pop edip in-filtreye çivilemesin; route yolundaki gibi cube_query'de tutup çözümü yalnız SQL üretiminde yap. Top-N monotonluğu + route paritesi.
7. **[P1] VQR replay'e coverage + semi guard** — ask.py:626 öncesi cq_v'yi ortak-helper'dan geçir (semi as-of + coverage).
8. **[P1] period_optional'ı taşınabilir yap** — AskResponse'a alan ekle ya da cube_query'ye göm (entity_limit gibi, deepcopy taşısın).
9. **[P1] Çekimli ay/dönem toleransı + anafora** — ay regex'lerine `\w*` çekim toleransı (_OPEN_START_RE emsali); "ondan önceki" anaforasını önceki rapor dönemine çıpala.
10. **[P2] time_dim hardcode → dinamik** — ask.py chip/VQR dallarındaki `"tarih"` yerine cube'un time_dimensions[0]'ı.

---

## (f) SONRAKİ TUR (zorluk artışı)
**003 — "Niyet-sınıflandırma mimarisi: deterministik-önce yönlendirme ne zaman YANLIŞ dal seçer":** R2 kök nedeni (STOP_STEMS niyet-körlüğü) bir MİMARİ soruya işaret ediyor — dima'nın "deterministik-önce, kaçırırsa LLM" yönlendirme stratejisi (ADR-0004/0008) hangi girdi sınıflarında YANLIŞ-POZİTİF veriyor (deterministik güvenle yanlış cevap üretip LLM'e hiç düşmüyor)? Kapsam kapısının "tanınan kelime = tanınan niyet" yanılgısını sistematik haritalandır: coverage-gate'in yakalayamadığı niyet sınıfları (negasyon, karşılaştırma, geri-alma, koşul, sıralama-yönü çelişkisi, çoklu-ölçü). Yanlış-pozitif oranını düşürecek "niyet-imza" katmanı tasarla. Ayrıca deterministik-vs-LLM güven eşiğinin kalibrasyonu: nerede "emin değilsen LLM'e sor" kuralı ihlal ediliyor.
