# Panel Turu 003 — Niyet-sınıflandırma mimarisi: deterministik-önce yönlendirmenin yanlış-pozitifi

**Tarih:** 2026-07-24
**Senaryo tipi:** Mimari denetim (kapsam kapısının "tanınan kelime = tanınan niyet" yanılgısı + güven eşiği + ifade-uzayı boşluğu)
**Kapsam:** `app/cube_router.py` (kapsam kapısı 783-802, STOP_STEMS 712-733, kelime toplama 736-780, route 814-952, _match_* 356-416), `app/routers/ask.py` (yönlendirme sırası 407-900+, _select_consistent 240-274, chip kapsamı), wren-core `cube.rs` (operatör enum'u), `app/llm.py:170`
**Modeller:** Haiku (substring körlüğü), Sonnet (güven kalibrasyon asimetrisi), Opus (ifade-uzayı boşluğu + niyet-imza tasarımı), Fable (morfoloji ile canlı delme)

## Araştırma sorusu
dima'nın "deterministik-önce, kaçırırsa LLM" stratejisi hangi girdi sınıflarında YANLIŞ-POZİTİF (deterministik güvenle yanlış cevap üretip LLM'e hiç düşmeme) veriyor? Kapsam kapısının "tanınan kelime = tanınan niyet" yanılgısını sistematik haritala.

---

## TAÇ BULGU (Opus buldu, orkestratör KANITLADI): ÜÇLÜ İFADE BOŞLUĞU + FORK ALT-KÜMESİ
**Rust cube derleyicisi 12 filtre operatörü destekliyor; Python router yalnız 4 üretiyor.**
- Rust `FilterOperator` (Opus: `cube.rs:79-92`): eq, in, gte, lte, gt, lt, **neq, not_in**, contains, starts_with, is_null, is_not_null.
- Python router ÜRETTİĞİ (orkestratör grep'le doğruladı — cube_router.py'de yalnızca): **eq, in, gte, lte**. Başka operatör literal'i YOK.
- `app/llm.py:170` LLM'e açıkça `"X hariç"→operator=neq` diyor → neq desteklenen, kullanılan bir operatör; SADECE deterministik yol onu üretmiyor.

Üçlü boşluk: **niyet-uzayı ⊋ ifade-uzayı(Rust) ⊋ üretim-uzayı(Python) ⊋ tanıma-uzayı(kapsam kapısı).** İki boşluk sınıfı:
- **Sınıf A (unutulmuş köprü):** neq/not_in/gt/lt — derleyici HAZIR, Python köprüsü yok, kapsam kapısı niyeti dolgu sayıyor. "iptaller hariç ciro" → filtresiz SUM (cube-rozetli sessiz-yanlış) OYSA `not_in` üretilebilirdi.
- **Sınıf B (gerçek fork duvarı):** LAG/window/between/koşullu-agregasyon — derleyicide de yok.

Bu, R2 kök-nedeninin (STOP_STEMS niyet-körlüğü) mimari kanıtı: niyet VAR + ifade-uzayı VAR + tanıma-uzayı niyeti üretime BAĞLAMIYOR.

---

## (a) UZLAŞILAR (yüksek güven)

### U1 — [P0] KAPSAM KAPISI SUBSTRING KÖRLÜĞÜ — canlı sessiz-yanlış (Haiku + Fable, Fable ÇALIŞTIRDI)
`_uncovered` satır 791 `any(k in w for k in known)` HERHANGİ-KONUM substring. 3+ harfli tanınan kısa kelime yabancı kelimeyi yutar. Fable gerçek route() ile üretti:
- `"kar" ⊂ "ankara"` → "kar ... ankara için" → Ankara filtresi düşer, deterministik kar döner.
- `"mal" ⊂ "imalat"/"maliyeti"` (ticaret sinonimi) → "imalat maliyeti" kavramı yutulur.
- `"son" ⊂ "personel"`, `"gun" ⊂ "uygun"` → filtre/kırılım sessiz düşer.
Kritik: `_syn_hit_words` "!"-tam-kelime disiplinini uygular AMA kapsam aşamasında (791) kelime tekrar SINIRSIZ altdiziye dönüşür — "kar!" koruması kapsamda kaybolur.

### U2 — [P0] NEGASYON EKİ (-sIz/-mAyAn) YUTULUYOR — en retorik sessiz-yanlış (Fable ÇALIŞTIRDI, Opus mimari)
`"firesiz partilerin cirosu"` → `fire` kökü kapsanır, `-siz` negasyonu yutulur → **fire toplamı döner** (fire İSTEMEYEN soruya fire toplamı; msyn tie-break de morfoloji kurbanı). `"reddedilmeyen partiler"` → reddedilenler DAHİL. `"maliyetsiz"/"sapmasız"` aynı. Negasyon ne kapsam kapısında ne üretimde var; `not_in`/`neq` Rust'ta hazır ama Python üretmiyor (U1-taç bağlantısı).

### U3 — [P0] STOP_STEMS KISA-PREFIX gerçek kelimeleri yutuyor (Haiku + Fable ÇALIŞTIRDI)
`w.startswith(s)` (793) + kısa stem'ler: `"ver"→veresiye`, `"tek"→tekstil`, `"turu"→turuncu` (renk değeri!), `"sana"→sanayi`, `"gecti"→geçtiğimiz` (dönem yutulur → tarihsiz sonuç), `"getir"→getiri`. Hepsi canlı deterministik yanlış-pozitif üretti. Ölü girdi: `"yan yana"` boşluklu stem tek-token `w`'ye asla uymaz (yalnız "yanyana" çalışır).

### U4 — [P0] BINARY route() — GÜVEN SKORU YOK, "kısmen emin" ifade edilemiyor (Sonnet)
`route() -> dict | None`. Güven/olasılık/belirsizlik YOK. `_match_cube` "en-uzun-sinonim farkı ≥4" keyfi eşiği (cube_router.py:375); `_match_measure` eşit-uzunlukta tie'de metadata-sırası sessiz kazanır (391-396) — ne chip ne None. Kapsam geçerse %100 güvenle cevap.

### U5 — [P1] DETERMİNİSTİK-vs-LLM GÜVEN ASİMETRİSİ (Sonnet)
LLM yolu `_select_consistent` (ask.py:240-274) k-örnekli oylama + 2/3 uyuşma eşiği + uyuşmazlık ekseni chip'i taşır. Deterministik yolun HİÇBİR kalibrasyonu yok. Belirsizlik-chip'i route() DIŞI kararlarda var (cube-adayı, ölçü-belirsizliği, dönem, kısmi-anlama, LLM-uyuşmazlık) ama route() İÇİ kararlarda (cube/measure/dim seçimi, coverage) YOK.

---

## (b) ÇELİŞKİLER & KİM HAKLI

Bu turda modeller büyük ölçüde ORTOGONAL çalıştı (her biri farklı facet), doğrudan çelişki az. Doğrulanan gerilim:
- Haiku "stemmer öner" (snowball) — orkestratör notu: pratik ama ağır; ek-beyaz-listesi (Fable önerisi) daha az-invaziv ve deterministik. Fable'ın "izinli-çekim-eki whitelist" yaklaşımı tercih edilir.
- Haiku bazı örnekleri (karapekte/tondaja) uydurma-kelimelerle kurdu (spekülatif); Fable GERÇEK pack sinonimleriyle (fire/mal/reddedil) çalıştırıp kanıtladı → Fable'ın vakaları operasyonel olarak daha ağır. İkisi aynı mekanizmayı (791 substring) işaret ediyor, çelişki değil güç-farkı.

---

## (c) HER MODELİN ÖZGÜN BULGUSU

- **Opus:** ÜÇLÜ boşluk matrisi + Rust 12-op vs Python 4-op fork alt-kümesi (taç bulgu); niyet-işlemenin DAĞITIK ve ÇAKIŞIK olduğu (`kaldir` hem aktif-operatör 462 hem dolgu 718; `degil` hem swap 435 hem dolgu 719); `ORDER BY measure` + `entity_limit` derleyicide YOK, Python string-sarma + iki-adım-`in` ile emüle ediyor → niyet-imza katmanı İKİ üretim yolunu hedeflemeli; niyet-imza katmanının "eklenti değil köklü yeniden-yapı" gerektirdiği argümanı.
- **Sonnet:** güven kalibrasyon asimetrisi + belirsizlik-chip kapsam haritası (12 karar düzeyi tablosu, hangisinde chip var/yok) + "≥4 eşiği magic number, golden ile kalibre edilmeli".
- **Fable:** CANLI sessiz-yanlış üretimi (firesiz→fire, reddedilmeyen→dahil, turuncu→filtresiz) + "k→ğ yumuşaması altdiziyi kırıp yanlış-NEGATİF, sabit-kök ekler yanlış-POZİTİF: aynı satırdan iki tutarsız hata modu" + kapsandı-ama-uygulanmadı asimetrisi ("aralik" kapsanır ama `_month_range_filters` uygulamaz → tarihsiz sonuç) + sayılar kapıya görünmez (788 `[a-z]+`).
- **Haiku:** substring mekanizmasının en net izolasyonu (786-791) + ters yanlış-negatif (çekim kaçırma → gereksiz LLM maliyeti) boyutu + stemmer çözüm önerisi.

---

## (d) "MÜKEMMEL SENARYO" ÖNERİSİ
İki katmanlı düzeltme: (1) TANIMA katmanı ek-farkında olmalı — kapsam eşleşmesi tam-kelime-ya-da-izinli-çekim-eki kuralına bağlansın (substring yasak); negasyon ekleri (-sIz/-mAyAn) İZİNLİ LİSTEDE OLMASIN → uncovered kalıp doğru dala gitsin. (2) NİYET katmanı üretime bağlansın — tek niyet-sınıflandırıcı (ADD/REMOVE/REPLACE/NEGATE/COMPARE/FILTER/PERIOD/RANK) STOP_STEMS'ten ÖNCE; Sınıf A niyetleri (NEGATE→not_in, eşik→gt/lt) deterministik ÜRETİLSİN (Rust zaten destekliyor); Sınıf B için dürüst "yapamıyorum"/golden-LLM. (3) route() güven taşısın: belirsiz seçimlerde `ambiguity` alanı → ask.py chip tetiklesin.

---

## (e) SOMUT AKSİYON MADDELERİ (önem-sıralı)

1. **[P0] Kapsam eşleşmesini ek-farkında yap** — `cube_router.py:791` `k in w` → tam-kelime VEYA `w.startswith(k) and w[len(k):] in İZİNLİ_ÇEKİM_EKLERİ`. `-siz/-sız/-suz/-süz/-meyen/-mayan` (negasyon) İZİNLİ değil. `≤4` harf known kelimeler için altdizi TAMAMEN kapat. U1+U2'yi (kar→ankara, firesiz→fire) kapatır. **En kritik: canlı sessiz-yanlış.**
2. **[P0] Negasyon üretimi (not_in/neq)** — Rust hazır (llm.py:170 zaten neq diyor). Deterministik yol "hariç/değil/-sIz/-mAyAn" için `not_in`/`neq` üretsin; ya da (min) bu niyetleri uncovered bırakıp LLM'e ver. Sınıf-A köprüsü.
3. **[P0] STOP_STEMS kısa-prefix'lerini çekim-eki kuralına bağla** — `cube_router.py:793`: "ver/tek/turu/sana/gecti/getir/isi/ile" gibi ≤4 stem'ler `startswith` yerine tam-kelime-ya-da-izinli-çekim. veresiye/tekstil/turuncu/sanayi/getiri yutulmasını kapatır.
4. **[P0] Niyet-operatörlerini tek yerde tanımla, çakışmayı temizle** — `kaldir` (462 vs 718), `degil` (435 vs 719) iki rolde; tek niyet-sınıflandırıcıya taşı, STOP_STEMS'ten sök (R2 aksiyon 2 ile birleşir).
5. **[P1] route() belirsizlik sinyali** — `_match_cube` ≥4 eşiği ve `_match_measure` tie'de `ambiguity`/`confidence` döndür; ask.py düşük-güven → chip/LLM. Deterministik-vs-LLM asimetrisini kapatır (U4/U5).
6. **[P1] `_match_cube` ≥4 eşiğini golden ile kalibre et + belgele** — magic number.
7. **[P1] Kapsandı-ama-uygulanmadı asimetrisi** — kapsam kümesine yalnız `date_filters` çıktısına DÖNÜŞEN dönem kelimeleri girsin ("aralik" tek başına kapsanmasın). Fable P1-4.
8. **[P1] Sayıları kapıya görünür yap** — `cube_router.py:788` `[a-z]+`→`[a-z0-9]+`; dönem/top-N/filtre olarak tüketilmemiş sayı varsa kapı çekilsin (R1 "3. ay" ile bağlantılı).
9. **[P2] `ORDER BY measure`/`entity_limit` emülasyonunu belgele** — niyet-imza katmanı Rust+Python iki üretim yolunu hedeflemeli (Opus P1-4).

---

## (f) SONRAKİ TUR (zorluk artışı)
**004 — "Golden/LLM güvenlik ağı gerçekten yakalıyor mu: deterministik yol reddettiğinde LLM doğru mu?":** R1-R3 boyunca çözüm hep "deterministik reddet → LLM devralsın" oldu (semi+gran None, negasyon uncovered, Sınıf-B niyetler). AMA bu güvenlik ağının SAĞLAM olduğu hiç doğrulanmadı. LLM yolunu derinlemesine denetle: (1) golden SQL retrieval GERÇEKTEN var mı yoksa tek-blob mu (R1 iddia etti, kanıtla); (2) LLM prompt'u semi-additive/negasyon/as-of/always_filter kısıtlarını biliyor mu (`_schema_prompt` içeriği); (3) `_select_consistent` oylama gerçek güven mi yoksa tutarlı-yanlış mı üretiyor; (4) LLM'in ürettiği SQL always_filter/RLAC/guard_sql güvenlik katmanlarından geçiyor mu yoksa serbest-SQL mi (iptal-kaydı/PII sızıntısı); (5) deterministik-reddin LLM'e "neden reddettiğini" (as-of gerekli, negasyon var) sinyallemesi. Kısaca: "LLM'e düş" çözümünün kendisi bir kablosuz-motor mu? Güvenlik + doğruluk kesişimi.
