# Faz 0-d: `cube_router.route()` Zemin-Gerçeği Kapsam Ölçümü

**Tarih:** 31 Temmuz 2026. **Yöntem:** `eval/cases.yaml`'daki 119 altın vakadan 111'i
(8 çok-adımlı "flow"/takip vakası hariç — `route()` tek-soru modeli, bağlamsız takip
sorularıyla adil kıyaslanamaz) doğrudan `app.cube_router.route(question, schema)`'dan
geçirildi. Gerçek derlenmiş demo MDL şeması kullanıldı (`compose_and_build` + canlı
`WrenService.schema()`), sahte/mock veri değil. Ham veri: `ground_truth_cube_router_coverage.json`.
Çalıştırma script'i: bu ölçüm tek seferlik, repo'da script olarak bırakılmadı (izole /tmp venv'de
koştu) — tekrarlanmak istenirse `route(q, schema)`'yı `eval/cases.yaml` üzerinde dönmek yeterli.

## Sonuç

**`route()` TEK BAŞINA, standalone (bağlamsız) sorularda %80.2 (89/111) deterministik kapsam
sağlıyor.** Bu, Faz 1'in ("Intent-first yönlendirme") üzerine inşa edeceği zeminin beklenenden
GÜÇLÜ olduğunu gösteriyor — mevcut `cube_router.py` zaten çoğunluk vakayı LLM'siz çözüyor;
sorun kapsamın küçük olması değil, bu kapsamın `/ask`'e hiç bağlanmamış olması (önceki iki
oturumda zaten kısmen düzeltildi: meta/katalog kapısı, VQR).

## Kapsanmayan 22 vakanın kırılımı (ÖNEMLİ — hepsi "route() eksik" anlamına gelmiyor)

**`expect=chip` olan 12 vaka**: bunlar zaten TANIM GEREĞİ tam bir CubeQuery beklemiyor —
netleştirme chip'i veya meta/selam yanıtı bekleniyor. `route()`'un bunlar için `None` dönmesi
÷ **hata değil, doğru davranış** — bu vakalar `route()`'un DEĞİL, ayrı deterministik
mekanizmaların (meta-tespiti, kısmi-eşleşme→chip mantığı, çapraz-konu tespiti — hepsi
`cube_router.py` içinde `route()`'un ÇAĞIRANI tarafında, eski `/ask` akışında) kapsamı.
Yani gerçek "LLM'e muhtaç" oran daha da düşük olabilir; bu 12 vaka ayrı ölçülmeli (gelecek iş:
bu mekanizmaları da izole test eden bir ikinci ölçüm).

**`expect=answer` olan 10 vaka — bunlar gerçek boşluklar:**
- **YoY/dönemsel kıyas (4 vaka, `yoy`/`kiyas` etiketi)**: "geçen yıla göre ciro" gibi sorular.
  `route()` bunları BİLEREK atlıyor (`_COMPARE_HINTS` kontrolü) çünkü bu, AYRI bir deterministik
  mekanizma olan `app/yoy.py`'nin işi — yani bu 10 içindeki 4'ü de aslında zaten BAŞKA bir
  deterministik yolla (LLM'siz) çözülüyor olabilir, `route()`'un kapsamadığı ≠ sistemin
  kapsamadığı. Faz 1 tasarımı bunu Intent-JSON şemasına `compare: yoy|mom` alanı olarak
  (zaten CubeQuery'de var) doğal şekilde almalı.
- **Typo/yazım hatası toleransı (3 vaka)**: "Siyh"→"Siyah", "beyz"→"beyaz", "vardya"→"vardiya".
  Gerçek bir kapsam boşluğu — `route()`'un değer/sözlük eşleştirmesi yazım hatalarına karşı
  kırılgan. Faz 1'in "kapsamı genişlet" iş listesinde somut, ucuz bir kazanım adayı (bulanık
  eşleştirme/edit-distance eklemek gibi).
- **Gerçekten LLM gerektiren (3 vaka, `llm` etiketi)**: "hangi makine daha iyi çalışıyor"
  (parafraz/çıkarım gerektirir — "iyi çalışmak" hiçbir ölçüye doğrudan eşlenmiyor), "önceki
  dönemle karşılaştır" (LAG serbest ifadesi), kompozit çapraz-cube raporu. Bunlar Faz 1
  sonrasında da muhtemelen Discovery (ham-SQL) yoluna düşmeye devam edecek — DOĞRU davranış,
  DSL'in bilinçli sınırı.
- **Diğer 3 vaka** (`bilanço`, `duruş nedenleri`): finansal tablo (`app/statements.py`, ayrı
  mekanizma) ve "neden" kırılımı — muhtemelen ayrı deterministik modüllerin kapsamında,
  `route()`'un değil.

## Faz 1/2 için çıkarımlar

1. `route()`'un zaten sağladığı %80.2'lik zemin, "LLM'i niyet-seçiciye indirgeme" hedefinin
   sanıldığından daha ucuz olacağını gösteriyor — büyük bir yeniden-yazım değil, BAĞLAMA işi.
2. Gerçek, dar bir iyileştirme listesi çıktı: (a) typo-toleranslı değer/sözlük eşleştirme,
   (b) YoY/statement gibi "route() dışı ama zaten deterministik" mekanizmaların Intent-JSON
   şemasına doğal alanlar olarak entegrasyonu — YENİ mekanizma değil, VAR OLANI birleştirme.
3. `llm` etiketli 3 vaka, Discovery yolunun KALICI olarak var olması gerektiğinin somut kanıtı
   — "%100 Intent-JSON'a geç" hedefi yanlış; %80-90 bandı + iyi bir Discovery yolu gerçekçi hedef.
4. Bu ölçüm TEK SEFERLİK bir zemin — Faz 1 ilerledikçe (typo toleransı, YoY-entegrasyonu
   eklendikçe) tekrar koşulup `eval/baseline.json`'a benzer şekilde takip edilebilir.
