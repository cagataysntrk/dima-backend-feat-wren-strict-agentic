# ANLAMA KATMANI RAPORU — **kapsam kapısı ve LLM basamağı**

**Tarih:** 5 Ağustos 2026 · **Dal:** `wren-bağımsız` @`bf5a7eb` · **Rol:** denetim (raporcu) — **ürün kodu değiştirilmedi**
**Kapsam:** `/ask` cevaplama merdiveninin **anlama** yarısı: `cube_router.route()`'un kapsam kapısı, dört LLM bayrağı, ve ikisinin kesişimi.

> # ⏸ ŞİMDİNİN KONUSU DEĞİL — **kullanıcı istediğinde dönülecek**
>
> Bu rapor **beklemeye alınmış bir kayıttır**, açık bir iş emri değildir. Önerilen maddelerin
> hiçbiri — **Ö1…Ö12** *(belirti düzeyi, §11 · §12.5)* ve **KÇ-0…KÇ-11** *(kök düzeyi,
> §13.3 · §14.5)* — **sıraya konmamıştır**; bu belgenin varlığı onların başlatıldığı
> anlamına gelmez.
>
> 🔴 **Buradaki hiçbir madde, kullanıcı açıkça istemeden ele alınmaz.** Operasyonun güncel
> gündemi `OPERASYON-DURUM.md`'dedir; bu belge oraya **girmez**, oradan **çağrılır**.
>
> Amaç, bulguların kaybolmamasıdır — bir sohbet kapandığında ölçümlerin de kaybolduğu bir
> kez yaşandı ve bu belge tam olarak onun tekrarını önlemek için yazıldı.

---

> ## Bu belge neden var
>
> Bu rapor bir **sohbet çıktısının kalıcılaştırılmasıdır**. Aynı bulgular 4 Ağustos'ta bir
> denetim ajanı tarafından sohbete yazıldı ve **sohbetle birlikte kayboldu**. Kaybolan şey
> yalnız metin değildi: içindeki **ölçümler** ve o ölçümlerin **çürüttüğü inanışlardı**.
>
> Bu sürüm o metnin kopyası değil, **üstüne ölçülmüş hâlidir**. Sohbetteki her sayı bu turda
> **yeniden koşuldu**; üçü **doğrulandı**, ikisi **düzeltildi**, biri **tamamen geçersiz çıktı**.

---

## 0.0 🔴 SAYILAR TARİHLİDİR — **MEKANİZMALAR KALICIDIR**

> Bu rapor **gelişmekte olan** bir sistemin **tek bir anına** bakar: `wren-bağımsız` @`bf5a7eb`,
> 5 Ağustos 2026. **Buradaki her sayı yarın değişebilir** — kod değişir, katalog büyür,
> seed genişler, korpusa vaka eklenir. *(Ör. `%68,8`, `60/60`, `55 çarpışma`, `26 R1` —
> hepsi o günün kataloğuna ve o günün kod satırlarına bağlıdır.)*
>
> ### Rapor sayıların üstüne kurulmadı. Sayılar yalnız **kanıt**tır; iddia **mekanizmadır**.
>
> | Katman | Ömrü | Örnek |
> |---|---|---|
> | 🟢 **MEKANİZMA** *(raporun asıl içeriği)* | **Kod yeniden yazılana kadar geçerli** | *"Aynı kuralın iki sahibi var"* · *"Niyet nesnesi yok, bu yüzden uyum denetlenemiyor"* · *"`route()` hem çözümleyici hem eşleştirici"* · *"katalog cube sinonimi boyut kelimesi taşıyor"* |
> | 🟡 **ORAN** *(büyüklük duygusu)* | **Katalog/kod değişince kayar** | *"%68,8 düşüyor"* · *"R1 %62"* |
> | 🔴 **SATIR NUMARASI** *(yalnız yol tarifi)* | **İlk commit'te bayatlar** | `cube_router.py:2060` |
>
> **Nasıl okunmalı:** bir sayı tutmuyorsa **bulguyu çürütmez** — yalnız *"ölçüm
> yenilenmeli"* der. Bulgu ancak **mekanizma ortadan kalkmışsa** çürür. Her mekanizma
> için **kapı ölçütü** yazılı (§11 · §12.5 · §13.3 · §14.5) ve hepsi **EK A** ile
> dakikalar içinde yeniden koşulabilir — sayıyı güncellemek pahalı değildir.
>
> ⚠ **Satır numaralarına güvenmeyin, isimlere güvenin.** Atıflar `dosya:satır` verir ama
> asıl adres **fonksiyon adıdır** (`_period_hit_words`, `_covers`, `compare_mode`);
> satır kayarsa ad kalır. EK B bu yüzden **ad + satır** birlikte listeler.

---

## 0 · Nasıl okunmalı — üç iddia sınıfı

Bu belgedeki her cümle üç kutudan birine düşer. Karıştırılmaları, bu deponun defalarca
avladığı *"beyan var, kanıtı yok"* hatasını üretir.

| İşaret | Anlamı | Doğrulama yolu |
|---|---|---|
| **⊙ ÖLÇÜLDÜ** | Bu turda `route()` **canlı çağrılarak** üretildi | Ek A'daki betik; `dima-test:latest` içinde, sıfır-LLM, sıfır-DB |
| **⊡ OKUNDU** | Koddan/belgeden **doğrudan alıntı**, satır numaralı | Verilen `dosya:satır` |
| **⚠ DEVRALINDI** | Önceki turdan gelen iddia — **bu turda doğrulanmadı** | Doğrulanana kadar karar dayanağı **sayılmaz** |

🔴 **Bu turda üç devralınmış iddia çürüdü.** §6'da tek tek yazılı. En ağırı: *"`raw_followup`
tuzağının düzeltmesi uygulanmadı"* — **uygulanmış**. Hafızadaki kayıt bayattı ve o kayda
dayanarak iş planlamak, **var olan bir düzeltmeyi ikinci kez yazmak** olurdu.

---

## 1 · Yönetici özeti — dokuz bulgu

| # | Bulgu | Kanıt | Ağırlık |
|---|---|---|---|
| **B1** | Gerçek-dünya korpusunda deterministik yol **41 vakanın 0'ında** cevap üretiyor | ⊙ `lab/gercek_dunya.py` · `HIT=0` | 🔴🔴🔴 |
| **B2** | **11/42 vakada cube ve ölçü ZATEN bulunmuştu** — cevap sonradan atıldı | ⊙ `route()` iç adımları | 🔴🔴🔴 |
| **B3** | Tanınan bir terim + gündelik fiil/soru kelimesi → **%68,8 ölüm**, hepsi R10 | ⊙ 77/112 kombinasyon | 🔴🔴🔴 |
| **B4** | Ay adı **her çekim ekinde** düşüyor: geçerli 60 çekimin **60'ı** R10 | ⊙ 60/60 · `mart`✓ `martta`✗ | 🔴🔴 |
| **B5** | Aynı kuralın **iki sahibi** var ve **farklı cevap veriyorlar**: `_covers` çekimi biliyor, `_period_hit_words` bilmiyor | ⊙ + ⊡ `cube_router.py:2060` | 🔴🔴 |
| **B6** | Dolgu sözlüğü **elle küratörlü** — `yaptık`✓ `verdik`✗, `oldu`✓ `düştü`✗ | ⊙ `_is_stop_word` matrisi | 🔴🔴 |
| **B7** | Belirsizlik **deterministik olarak biliniyor** (`bakiye` → tam 2 aday, adlarıyla) ama chip'e çevrilmiyor | ⊙ `measure_cube_candidates` | 🔴🔴 |
| **B8** | 🔴 **BUGÜN CANLI SESSİZ-YANLIŞ:** *"mart cirosunu şubat ile kıyasla"* → iki ay **toplanıp tek sayı** dönüyor, `source=cube` rozetiyle | ⊙ §12.2 | 🔴🔴🔴 **ACİL** |
| **B9** | Kullanıcının iki canlı vakası **Ö1+Ö2 ile çözülmüyor**; birinde düzeltme **sessiz-yanlış yayar** | ⊙ §12 | 🔴🔴🔴 |

**Tek cümlelik kök neden:**

> Sistem, gerçek kullanıcı cümlesinde **doğru cube'u ve doğru ölçüyü bulduktan sonra**,
> cümlede kalan bir **fiil ya da soru kelimesini** *"anlamadığım kavram"* sayıp cevabı
> **çöpe atıyor**. Bu bir sözlük eksikliği değil, bir **sınıflandırma hatasıdır**:
> *çekim eki taşıyan bir Türkçe fiil, bir iş kavramı değildir.*

> ### ⚠ Bu özet, raporun **ilk yarısınındır**. §13–14 onu genişletti:
>
> Yukarıdaki cümle **doğrudur ama dardır** — kusurların yalnız R10 kanadını (%24) anlatır.
> Sonraki denetim iki katman daha açtı:
>
> - **§13** — yedi kök neden *(iki eşleştirme rejimi · aynı kuralın çok sahibi · tek-geçiş
>   tarama · **niyet–sorgu uyum denetiminin yokluğu** · ayrık teşhis · aşırı yüklenmiş
>   kelime · eksik yapı)* ve **3 sessiz-yanlış sınıfı, 42 vaka**.
> - **§14** — R1'in (%62) kökü **kodda değil KATALOGDA**: 55 sinonim çarpışması, ve
>   Türkçe **türetme** katmanının hiç olmaması.
>
> **Ve hepsinin ortak kökü §14.4'tedir:** `route()` bir **eşleştiricidir**, ama ona
> **çözümleyici** işi yaptırılıyor. Yedi kök neden, tek bir mimari kararın yedi belirtisi.
> Ürünün tezi (*"LLM garson, küp aşçı"*) doğru — ama bugün **garson yok, siparişi aşçı
> alıyor.**

---

## 2 · Cevaplama merdiveni — bugünkü **gerçek** hâli

⊡ Kaynak: `backend/app/routers/ask.py:1376-1408` (docstring) + gövde.

```
1  · Meta/katalog sorusu ................... LLM YOK
2  · VQR replay (bağımsız soruda) .......... LLM YOK
3  · YAPISAL takip (body.cube_query) ....... deterministic_refine → cross_cube_* → llm.refine_cube
3b · RAW takip (body.prev_sql) ............. _try_fresh_intent() ÖNCE denenir   ← düzeltme İNDİ
4a · route() ............................... 🔴 SIFIR-LLM — BU RAPORUN KONUSU
4b · compare_mode (YoY/MoM) ................ LLM YOK
4c · Intent-JSON (llm.select_cube) ......... ask_intent_first: beta  → AÇIK
4d · netleştirme chip'i .................... netlestirme_onceligi: off → KAPALI
5  · Discovery (ham SQL) .................... son çare
```

Ürünün tezi **bu sıradadır**: *"LLM garson, küp aşçı."* Tezin taşıyıcı basamağı **4a**'dır.
Bu rapor, **4a'nın gerçek konuşmada nereye kadar uzandığını** ölçer.

⊙ **Ölçüm kararı:** `route()` bu raporda **ham metinle** çağrıldı — çünkü ürün de öyle
çağırıyor (⊡ `ask.py:2473` → `cube_router.route(body.question, schema, …)`). Yani buradaki
verdict'ler **ürün-sadıktır**. (`_norm`'lu metin ürün içinde yalnız *başka* tüketicilere
gider: `measure_cube_candidates`, `ilgili_cubelar`, `_olcu_belirsizligi_netlestir`.)

---

## 3 · BULGU B1+B2 — **sistem cevabı biliyor ve atıyor**

### 3.1 Gerçek-dünya korpusu, 42 vaka

⊙ `python lab/gercek_dunya.py` — bu turda koşuldu.

| Kademe | toplam | kabul | **doğru** | **netleştirme** | dürüst ret | sessiz-yanlış |
|---|---|---|---|---|---|---|
| K1 | 16 | 8 | **0** | **0** | 16 | 0 |
| K2 | 9 | 4 | **0** | **0** | 9 | 0 |
| K3 | 7 | 1 | **0** | **0** | 7 | 0 |
| K4 | 6 | 3 | **0** | **0** | 6 | 0 |
| K5 | 3 | 3 | **0** | **0** | 3 | 0 |
| **Σ** | **41** | **19** | **0** | **0** | **41** | **0** |

> 🔴 **Sıfır sessiz-yanlış bir başarıdır ve öyle okunmalıdır** — ADR-0008 çalışıyor.
> 🔴 **Ama sıfır doğru + sıfır netleştirme, tezin kendisinin ölçüsüdür.** Deterministik yol,
> gerçek kullanıcı ağzıyla sorulan **41 sorunun 41'inde** pes ediyor.

⚠ **Aşırı okumaya karşı sınır:** bu tablo **ürünün cevapsızlığını ölçmez**. `/ask` orada
durmaz — Intent-JSON ve Discovery devam eder. Ölçtüğü şey **LLM'siz yolun erişimidir**;
yani *"küp aşçı"* iddiasının gerçek kullanıcı dilindeki karşılığı. Ürün cevap veriyor
olabilir — ama **LLM'le**, ve o da §7'deki kotaya bağlı.

### 3.2 Red kodu dağılımı — kayıp nerede?

⊙ 42 vakanın tamamı, `red_gerekcesi()` ile:

| Kod | Anlamı | Adet | Pay |
|---|---|---|---|
| **R1** | cube eşleşmedi (ya da çapraz konu) | **26** | %61,9 |
| **R10** | 🔴 **kapsam kapısı — tanınmayan kelime** | **10** | %23,8 |
| **R4** | ölçü eşleşmedi ve `default_measure` yok | **5** | %11,9 |
| **R9** | kırılım istendi, boyut eşleşmedi | **1** | %2,4 |
| **HIT** | cevap üretildi | **0** | **%0** |

### 3.3 🔴 **11/42 — cube VE ölçü bulunmuştu, cevap yine de atıldı**

⊙ Her red vakasında `route()`'un iç adımları (`_match_cube` → `_match_measure` →
`default_measure`) ayrıca koşuldu:

| Kod | Persona | Soru | Bulunan cevap |
|---|---|---|---|
| R10 | cfo | `tahsilat neden yavaşladı` | `cari.toplam_alacak` |
| R10 | uretim | `gece vardiyası niye düştü` | `oee.ort_oee` |
| R10 | uretim | `randımanımız kaç` | `oee.ort_oee` |
| R10 | uretim | `hangi tezgahta duruş çok` | `oee.toplam_durus_dakika` |
| R10 | uretim | `hangi vardiya bizi aşağı çekiyor` | `oee.ort_oee` |
| R10 | kalite | `ne kadar fire verdik` | `parti.toplam_fire_kg` |
| R10 | kalite | `rework neden arttı` | `kalite.toplam_rework_kg` |
| R10 | satis | `kaç kilo sevk ettik` | `parti.toplam_agirlik_kg` |
| R10 | satis | `ciro düşüşünde kimin payı var` | `parti.toplam_ciro` |
| R10 | saha | `bu ayki fire ne kdr` | `parti.toplam_fire_kg` |
| R9 | saha | `musetri bazinda ciro` | `parti.toplam_ciro` |

> 🔴 **Bu tablonun anlamı şudur:** kullanıcı *"ne kadar fire verdik"* diye sordu. Sistem
> `parti` cube'unu buldu, `toplam_fire_kg` ölçüsünü buldu — **sorulan tam olarak buydu** —
> ve sonra cümlede `verdik` kelimesi olduğu için **cevabı attı**.
>
> Bu bir **anlama** hatası değil. Anlama **başarılı** oldu. Bu bir **teslim** hatası.

**Ölçünün sınırı, dürüstçe:** bu 11 vakanın hepsinde *route()'un bulduğu* ölçü, korpusun
*beklediği* ölçüyle aynı değildir. Örnek: `ne kadar fire verdik` için korpusun yasağı
*"fire miktarını fire ORANI sanmak"* — yani doğru cevap `fire_orani_yuzde` olabilirdi.
Dolayısıyla **kapsam kapısı açılırsa bu 11 vakanın tamamı doğru olmaz**; bir kısmı
netleştirmeye düşmelidir. Bu bir kusur değil, **kapının açılış tasarımının şartıdır**:
kapı, *"bilmiyorum"* ile *"iki adaydan hangisi?"* ayrımını korumak zorundadır.

---

## 4 · BULGU B3 — **fiil ve soru kelimesi katliamı**

### 4.1 Deney

⊙ 12 katalog terimi çıplak hâlde denendi; **HIT veren 7'si** alındı; her birine 16 gündelik
fiil/soru kelimesi eklendi. 7 × 16 = **112 kombinasyon**.

**Çıplak terim tabanı:**

| terim | sonuç | | terim | sonuç |
|---|---|---|---|---|
| `randiman` | **HIT** | | `bakiye` | R1 *(çapraz konu — §8)* |
| `fire` | **HIT** | | `kaza` | R4 *(cube var, ölçü yok)* |
| `ciro` | **HIT** | | `sikayet` | R4 |
| `rework` | **HIT** | | `siparis` | R4 |
| `oee` | **HIT** | | `sevkiyat` | R4 |
| `maliyet` | **HIT** | | | |
| `tahsilat` | **HIT** | | | |

### 4.2 Sonuç — **77/112 (%68,8) düştü, ölüm kodu %100 R10**

⊙ Ve dağılım **birebir aynı**: yedi terimin **yedisinde de aynı 11 kelime** öldürüyor.

| Öldüren *(11)* | Geçen *(5)* |
|---|---|
| `kaç` · `kaç oldu` · `verdik` · `düştü mü` · `arttı mı` · `söyle` · `durumu ne` · `ne durumda` · `iyi mi` · `kötü mü` · `var mı` | `nedir` · `ne kadar` · `yaptık` · `göster` · `bakalım` |

> Bu simetri tesadüf değil, **kanıttır**: kayıp terimden değil, **terimden sonra gelen
> kelimeden** geliyor. Terim ne olursa olsun sonuç aynı.

### 4.3 🔴 BULGU B6 — kapı bir **sözlüğe** dayanıyor, bir **kurala** değil

⊙ `_is_stop_word()` doğrudan sorgulandı:

| Kelime | dolgu? | | Kelime | dolgu? |
|---|---|---|---|---|
| `yaptık` | ✅ **True** | | `verdik` | ❌ **False** |
| `oldu` | ✅ **True** | | `düştü` | ❌ **False** |
| `göster` | ✅ **True** | | `söyle` | ❌ **False** |
| `gösterir` | ✅ **True** | | `arttı` | ❌ **False** |
| `nedir` | ✅ **True** | | `kaç` | ❌ **False** |
| `rapor` | ✅ **True** | | `analiz` | ❌ **False** |
| `listele`·`hesapla`·`getir`·`bakalım`·`kadar`·`toplam` | ✅ | | `iyi`·`kötü`·`var`·`yok`·`durum`·`durumu`·`bilgi` | ❌ |

> 🔴 **`yaptık` dolgu, `verdik` değil.** İkisi de birinci çoğul görülen geçmiş zaman.
> Aralarında **hiçbir dilbilgisel fark yok** — yalnız biri listeye yazılmış, öteki yazılmamış.
>
> ⊡ Ve bu tam olarak ADR-0008'in **yasakladığı** desendir:
> *"🔴 DİSİPLİN: REFLEKSLE YENİ REGEX EKLEME. Kayıtlı desen: `_uncovered`'ın alt-dize körlüğü
> defalarca **kelimeye özel bir yamayla** geçiştirildi ve kök neden hiç düzeltilmedi.
> **Kural: kök nedeni düzelt, örneği değil.**"*
> (`docs/adr/0008-…md`)

**Sonuç:** `verdik`'i listeye eklemek **çözüm değil, kusurun kendisidir**. Çözüm yapısal
olmalıdır — ve tam olarak bu yüzden **bugüne kadar yapılmamıştır**.

---

## 5 · BULGU B4+B5 — **aynı kuralın iki sahibi, iki farklı cevabı**

### 5.1 Ay adı çekim matrisi — ⊙ **60/60 düştü (%100)**

Ses uyumuna uygun, **gerçek** Türkçe çekimler denendi (12 ay × 5 ek):

| Soru | Sonuç | | Soru | Sonuç |
|---|---|---|---|---|
| `mart ciro` | **HIT** | | `martta ciro` | **R10** |
| `mart ayinda ciro` | **HIT** | | `marttan ciro` | **R10** |
| | | | `subata ciro` | **R10** |
| | | | `ocaktaki ciro` | **R10** |

> Çıplak ay adı çalışıyor. `ayı`/`ayında` sarmalı çalışıyor. **Ayın kendi çekimi çalışmıyor** —
> ve gerçek cümle tam olarak öyle kurulur: *"mart**ta** ne kadar sattık"*, *"şubat**a** göre"*.

### 5.2 Kök neden: iki mekanizma, aynı soru, **çelişen** cevaplar

⊙ Doğrudan sorgulandı:

| Mekanizma | `martta` | `subata` | `ayda` | `cirosunu` |
|---|---|---|---|---|
| **`_covers(kök, kelime)`** — kapsam kapısının **kendi** biçimbirim kuralı | ✅ **True** | ✅ **True** | ✅ **True** | ✅ **True** |
| **`_period_hit_words(q)`** — dönemi tanıyan taraf | ❌ **`[]`** | ❌ **`[]`** | — | — |

⊡ Neden: `cube_router.py:2060` içinde ay taraması

```python
for m in re.finditer(rf"\b({_MONTH_ALT})\b(\s+ayi\w*)?", q):
```

`\b` sınırı, ay adının **kendi ekini** dışarıda bırakır. Oysa aynı fonksiyondaki **öteki**
tarihsel regexler (`_RANGE_RE`, `_REL_DATE`, `_QUARTER_RE`, `_YEAR_RE`) `_cekimli_token()`
üzerinden **eki alıyor** — ⊡ ve o yardımcının docstring'i, bu hatanın **daha önce bir kez
düzeltildiğini** anlatıyor (`ay` → `ayda` vakası). **Aynı düzeltme ay adlarına uygulanmamış.**

> 🔴 **Yapısal teşhis:** *"bu kelime bilinen bir kökün çekimi midir?"* sorusunun bu depoda
> **iki sahibi** var. Biri (`_covers`) doğru cevaplıyor, öteki (`_period_hit_words`)
> soruyu **hiç sormuyor**. Ve kapsam kapısı ikincisinin cevabını kullanıyor.
>
> Bu, bu deponun kendi kaydettiği **tekrar eden desendir** — ⊡ `cube_router.py:2405`:
> *"İki tüketici vardı ve **aynı soruyu farklı cevaplıyorlardı**."*

### 5.3 Ölçünün sınırı

⚠ Önceki turdan devralınan *"96 ay×ek kombinasyonunun 84'ü düşüyor"* iddiası bu turda
**yeniden koşuldu ve yerini daha sert bir sayıya bıraktı**: ses uyumuna uymayan formlar
elenince (`ocakte`, `ocaka` gibi) **geçerli 60 çekimin 60'ı** düşüyor. Yani oran %87,5
değil **%100**'dür; hayatta kalan tek biçim **çıplak ay adıdır**.

---

## 6 · LLM basamağı — 🔴 **devralınan üç iddianın denetimi**

Bu bölüm, sohbette *"LLM katmanı kendini iki yerde sabote ediyor"* diye özetlenen iddiaların
**kodla karşılaştırılmasıdır**. Üçünün ikisi düzeltilmeli.

### 6.1 ❌ ÇÜRÜDÜ — *"`raw_followup` tuzağının düzeltmesi uygulanmadı"*

⊡ `app/routers/ask.py:3298`:

```python
if not is_followup or raw_followup:
    fresh = _try_fresh_intent()
    if fresh:
        return fresh
```

⊡ Ve gerekçesi `ask.py:3286-3295`'te yazılı: *"canlı bulgu, 1 Ağustos 2026 — 'raw_followup
tuzağı': bir thread'in İLK turu Discovery'ye düşerse `raw_followup` o thread'in SONRAKİ HER
turunda True kalırdı ve bu satır hiç ÇALIŞMAZDI."*

> ✅ **Düzeltme indi.** Merdiven docstring'inde de 3b adımı olarak kayıtlı (`ask.py:1390`).
>
> 🔴 **Hafıza kaydı bayat** (`project_llm_cube_architecture_audit.md` — *"fix identified,
> not yet applied"*). Bu kayda dayanarak iş planlamak, **var olan bir düzeltmeyi ikinci kez
> yazmak** olurdu. Kaydın güncellenmesi gerekiyor.

### 6.2 ⚠ DÜZELTİLDİ — *"netleştirmeyi Intent-JSON eziyor"*

**Olgu doğru, ama sebep 'kod yok' değil, 'bayrak kapalı ve kapalılığın gerekçesi ölçülmüş'.**

⊡ `ask.py:2615-2621` — netleştirme dalı Intent-JSON'dan (`:2634`) **ÖNCE** duruyor:

```python
if (route_hit is None
        and "netlestirme_onceligi" in resolve_for(settings, principal)):
    _bel = _olcu_belirsizligi_netlestir(q_norm, schema)
    if _bel is not None:
        ...
        return _finish(_bel)
```

⊡ `demo/packs/features.yml:150` → `netlestirme_onceligi: "off"`.

⊡ Kararın ölçümü (`belgeler/mimari/V1-MIMARI-HARITASI.md:712`): *A/B 63 etiketli vaka — bozulan 0, kurtarılan
0. 15 gerçek ifade — cevaplanan 12→8, kurtarılan 1 (**doğru ölçüyle 0**), kaybedilen 5.
Kabul ölçütü (doğru kurtarma > 0) **karşılanmıyor** → KAPALI.*

> Yani: **mekanizma var, sırası doğru, kapısı kapalı ve kapalılık ölçüme dayanıyor.**
> *"LLM katmanı kural motorunun bildiği bir gerçeği siliyor"* cümlesi **davranış olarak doğru**,
> ama *"düzeltme yapılmadı"* kısmı yanlış — **düzeltme yapıldı, ölçüldü, ve reddedildi**.

⚠ **Denetçi notu — ölçümün kendi sınırı, `lab/faz0_4_netlestirme.py`'nin kendi ifadesiyle:**
⊡ *"Gerçekten belirsiz bir kelimede **doğru cevap yoktur**; herhangi bir seçim yazı-turadır.
Sonuç: **doğruluk bu kararı veremez**."* Bu doğruysa, `cevaplanan 12→8` satırındaki
*"kaybedilen 5"* rakamı **işareti belirsiz bir sayıdır**: o 5 cevabın doğru olduğu
gösterilmedikçe, kaybedilmeleri bir kayıp değildir. Karar **yeniden açılmalı demiyorum** —
ama karar **`doğru kurtarma > 0`** ölçütüne dayandığı için, ölçütün ölçülebildiği bir nüfusta
(≥2 sahipli ölçüler) **yeniden koşulması gerekir**; 15 ifade dar bir paydadır.

### 6.3 ⚠ DÜZELTİLDİ — *"prompt enhancer'a sıra gelmedi"*

⊡ `belgeler/mimari/V1-MIMARI-HARITASI.md:721` → **"ölçüldü, kazanç YOK, kota sınırına çarpıldı"**.
⊡ `demo/packs/features.yml:80` → `prompt_enhancer: "off"`.

> Yani *"sıra gelmedi"* değil — **sıra geldi, ölçüldü, kazanç görülmedi.**

🔴 **Ama denetimin asıl bulgusu burada:** o ölçüm **hangi aletle** yapıldı?

⊡ `lab/gercek_dunya.py` başlığı: *"`nl_corpus.py::gen_single()` soruyu **cevabın anahtarından**
kuruyor. Ölçüldü: boyahane'nin 5077 tekil sorusunun **≥%97,1'i katalog türevi**; gerçek
kullanıcı dağarcığı **≤123 soru (≤%2,4)**."*

> 🔴 **`prompt_enhancer`'ın işi, kullanıcının kelimesini kataloğun kelimesine çevirmektir.**
> Sorularının %97,1'i **zaten katalog kelimesiyle yazılmış** bir korpusta bu bayrağın
> yapacak işi **yoktur** — dolayısıyla *"kazanç yok"* sonucu, bayrak hakkında değil,
> **aletin körlüğü** hakkında bir olgudur.
>
> **Bir A/B'nin sonucu «fark yok» ise, önce ölçen aletin o farkı görebildiği kanıtlanmalıdır.**
> Bu cümle deponun kendi cümlesidir (`lab/gercek_dunya.py`) ve bu bayrağa **uygulanmamıştır**.

**Denetim sonucu:** `prompt_enhancer`'ın `off` kararı **geçersiz değil, dayanaksızdır**.
Dayanak, o bayrağın nüfusunu içeren bir korpusta yeniden kurulmalıdır — ve o korpus artık
**var** (`lab/gercek_dunya.py`, 42 vaka, §3'te taban ölçüldü: **0 doğru**).
Bu, tabanı **0** olan bir A/B'dir; yani **gerileme riski yapısal olarak sıfırdır**.

### 6.4 Dördüncü bayrak — `agent_plan_secimi`

⊡ `features.yml:77` → `"off"`. ⊡ Tüketicisi bağlı (`ask.py:2824`, `:3315`) — bu bayrak
*"beyan var, tüketici yok"* sınıfında **değil**; ⊡ `ask.py:3305`'teki not, tüketicisizliğin
2026-08-03 denetiminde bulunup **kapatıldığını** kaydediyor. Bu raporun konusuna (anlama)
doğrudan katkısı yok; **sıcak yola LLM ekliyor** ve gecikme bütçesiyle birlikte ölçülmeli.

### 6.5 Bayrak durum tablosu — ⊡ `demo/packs/features.yml`

| Bayrak | Durum | Bu rapordaki karşılığı |
|---|---|---|
| `ask_intent_first` | **beta (AÇIK)** | Intent-JSON bugün **çalışıyor** — §6.1'deki tuzak kapatıldı |
| `llm_sema_kisitli` | **beta (AÇIK)** | Intent-JSON çıktısı katalog ENUM'una kısıtlı |
| `netlestirme_onceligi` | `off` | §6.2 — mekanizma var, ölçüm dar paydada |
| `prompt_enhancer` | `off` | §6.3 — 🔴 **dayanağı körü ölçmüş aletten geliyor** |
| `agent_plan_secimi` | `off` | §6.4 |
| `t2_anlatici` | `off` | Kapsam dışı (anlatım katmanı) |

---

## 7 · Kota — LLM'e kaçışın **gerçek** sınırı

⚠ **DEVRALINDI, bu turda doğrulanmadı:** sınır 10 saniyede 10 istek; bir Intent turu
`consistency_k=3` ile **üç çağrı**; günlük kota 4 Ağustos operasyonunda **saat 11:40'ta doldu**.

⊡ Kodda doğrulanan kısım: `ask.py:2638` — Intent-JSON'da **self-consistency** dalı bağlı
(`_select_consistent`, `consistency_k`). Yani **bir Intent turu birden fazla çağrıdır** —
çarpan gerçektir.

> **Bu, §6.3'ün önerisini zayıflatmaz, güçlendirir.** `prompt_enhancer` sıcak yola bir LLM
> çağrısı **ekler** — ama yalnız `route()` **boş döndüğünde**. §3'e göre bu, gerçek-dünya
> korpusunda **turların %100'üdür**; yani bugün o soruların **hepsi zaten** Intent-JSON'a
> (3 çağrı) ya da Discovery'ye gidiyor. `route()`'un kapsamını **kapıyı düzelterek**
> genişletmek, kota tüketimini **azaltan** tek müdahaledir — LLM eklemeden.

---

## 8 · BULGU B7 — belirsizlik **biliniyor**, chip'e çevrilmiyor

⊙ `bakiye` sorgulandı:

| Mekanizma | Çıktı |
|---|---|
| `route("bakiye")` | **R1** — *"cube eşleşmedi ya da **çapraz konu (birden çok cube)**"* |
| `measure_cube_candidates("bakiye")` | **tam 2 aday:** `cari.bakiye` · `mizan.bakiye` |
| `ilgili_cubelar("bakiye")` | `[]` |

> 🔴 Deterministik katman belirsizliği **tahmin etmiyor — biliyor**. İki adayı **adlarıyla**
> üretiyor. Sonra `netlestirme_onceligi` kapalı olduğu için o liste **kullanılmıyor** ve
> Intent-JSON olasılıksal bir seçim yapıyor.
>
> ⊡ Ve yan bulgu kayıtlı (`belgeler/mimari/V1-MIMARI-HARITASI.md:713`): *"`bu yıl bakiye` kararlı şekilde
> `mizan.bakiye` seçiyor ve cevap **₺0** — mizan yapısı gereği sıfıra denkleşir."*
>
> Yani bu vakada olasılıksal seçim yalnız *belirsiz* değil, **yapısal olarak anlamsız bir
> sayı** üretiyor. Kararın *"bu bir MOTOR kusuru değil KATALOG kararıdır"* diye kaydedilmiş
> olması doğrudur — ama **kullanıcı ₺0 görüyor** ve o ₺0'ın yanında bir güven rozeti var.

**⊙ Yan bulgu — `default_measure` boşluğu:** `kaza`, `sikayet`, `siparis`, `sevkiyat` çıplak
sorulduğunda cube **bulunuyor**, ama dördünde de `default_measure=None` → **R4**. Bu, R10'dan
**ayrı** ve daha ucuz bir kayıp sınıfıdır (5/42): katalog kararı, kod kusuru değil.

---

## 9 · Ölçüm aletinin kendi kusurları — **denetimin denetimi**

Bu bölüm, bu raporun **kendi güvenilirliğini** sınırlar.

| # | Kusur | Durum | Bu raporu etkiler mi? |
|---|---|---|---|
| **A1** | ⚠ `lab/gercek_dunya.py` `route()`'a **ham metin** veriyor | Bilinen | ❌ **Hayır.** ⊡ Ürün de ham metin veriyor (`ask.py:2473`). Verdict'ler ürün-sadık. Artefakt yalnız **türetilmiş teşhis listelerini** (§4.3'ün "engelleyen kelime" dökümü gibi) etkiler; bu raporun sayıları `red_gerekcesi()`'den gelir, dökümden değil |
| **A2** | ⊙ Korpusta **1 katalog sızıntısı** (`kapanışta bakiye tutuyor mu`) | Araç yakaladı, vaka **korpusa girmedi** | ❌ Hayır — payda 42 değil **41** olarak raporlandı |
| **A3** | ⊙ 42 vaka **elle yazılmış**; kombinatoryal üreteç yok | Açık iş (#35) | ⚠ **Evet, yönü belirsiz.** 41 vaka, gerçek dağılımın örneklemi değil; oranlar (%23,8 R10) **±geniş** okunmalı. Yön (0 doğru) ise örneklem hatasıyla açıklanamayacak kadar kesindir |
| **A4** | ⊙ §4'ün 112 probu **sentetiktir** — gerçek kullanıcı cümlesi değil | Bilinçli | ⚠ Sentetiklik burada **lehte**: değişkeni izole eder (aynı terim, tek fark son kelime) |

---

## 10 · Sentez — dört cümle

1. **Kural motoru yanlış cevap vermiyor; cevap vermiyor.** 41 gerçek-dünya sorusunun 41'inde
   pes ediyor, **sıfır sessiz-yanlışla**. ADR-0008 çalışıyor — fazla iyi çalışıyor.
2. **Kaybın en pahalı dörtte biri (10/42) tamamen kendi kendine açılmış bir yaradır:** cube ve
   ölçü **bulunmuşken**, cümledeki bir fiil yüzünden cevap atılıyor.
3. **Ve o kapı bir kurala değil bir listeye dayanıyor** (`yaptık`✓/`verdik`✗) — yani ADR-0008'in
   *kendi yasakladığı* biçimde inşa edilmiş. Bu yüzden çözüm **yapısal olmak zorunda**, ve tam
   bu yüzden bugüne kadar **yapılmamış**.
4. **LLM katmanı reddedilmedi ve sabote de etmiyor:** Intent-JSON açık, tuzağı kapalı, netleştirme
   mekanizması yazılı ve sırası doğru. Kapalı olan tek şey **bayraklar**, ve iki bayrağın
   kapalılık gerekçesi **kendi nüfusunu göremeyen bir aletle** üretilmiş.

---

## 11 · Ne yapılmalı — **kapı biçiminde** *(uygulama bu raporun kapsamı dışıdır)*

> ### ⚠ İKİ NUMARALANDIRMA VAR — karıştırılmamalı
>
> | Önek | Ne | Nerede | Nasıl okunmalı |
> |---|---|---|---|
> | **Ö1…Ö12** | **belirti düzeyi** — tek bir kusuru kapatan somut iş | §11 · §12.5 | *"bu vakayı düzeltir"* |
> | **KÇ-0…KÇ-11** | 🔴 **kök düzeyi** — bir kusur SINIFINI kapatan mekanizma | §13.3 · §14.5 | *"bu sınıfın tekrarını bitirir"* |
>
> **İkisi rakip değil, katman.** Ama sıra **KÇ tablosundan** okunmalıdır (§14.6):
> her Ö maddesi bir KÇ'nin altına düşer ve **KÇ inerse çoğu Ö kendiliğinden kapanır.**
>
> | Ö | Bağlı olduğu kök çözüm |
> |---|---|
> | Ö1 *(fiil/soru kelimesi)* · Ö2 *(ay çekimi)* | **KÇ-2** + **KÇ-3** |
> | Ö8 *(fail-closed kıyas)* · Ö9 *(mutlak dönem kıyası)* | **KÇ-1** *(+ temsil için **KÇ-0**)* |
> | Ö10 *(`göre` ayrımı)* | **KÇ-0** *(çözümleme katmanı)* + KÇ-6 |
> | Ö11 *(taze çapraz-cube)* · Ö12 *(ölçü→ölçü etki)* | **KÇ-0** + **KÇ-7** |
> | Ö4 · Ö5 *(bayrak A/B'leri)* | **KÇ-9** *(gerçek red kayıtları korpus olur)* |
> | Ö7 *(senaryo üreteci #35)* | **KÇ-9** — gerekçesini büyük ölçüde **ortadan kaldırır** |
> | Ö3 · Ö6 | bağımsız |

Denetçi olarak **öneri değil kabul ölçütü** yazıyorum: her madde, bitip bitmediği
**ölçülebilir** olacak şekilde.

| # | İş | Kabul ölçütü *(sayıyla)* | Ön koşul |
|---|---|---|---|
| **Ö8** | 🔴🔴 **ACİL — HEPSİNDEN ÖNCE.** İki adlandırılmış dönem + kıyas fiili **aralık toplamına çökmesin** *(fail-closed)*. Ayrıntı **§12.5** | ⊙ `mart cirosunu şubat ile kıyasla` tek birleşik sayı **DÖNDÜRMESİN** | — *(bugün canlı sessiz-yanlış)* |
| **Ö1** | 🔴 Kapsam kapısı **çekim eki taşıyan fiil/soru kelimesini** dolgu saysın — **kural olarak, liste olarak değil** | ⊙ §4'ün 112 probu **≥%90 HIT**; `_is_stop_word` sözlüğüne **tek kelime eklenmeden** | ADR-0008 §DİSİPLİN |
| **Ö2** | 🔴 `_period_hit_words` ay adında `_cekimli_token`/`_ek_gecerli` kullansın — **tek sahip** | ⊙ §5.1'in 60 çekiminde **60 HIT**; `mart ayakkabı` **HIT VERMESİN** (yanlış-pozitif kapısı) | — |
| **Ö3** | Ö1+Ö2 sonrası korpus yeniden koşulsun | ⊙ `lab/gercek_dunya.py`: **sessiz-yanlış hâlâ 0**; kabul >19/41 | Ö1, Ö2 |
| **Ö4** | `prompt_enhancer` A/B'si **gerçek-dünya korpusunda** yeniden koşulsun | ⊙ Taban 0 doğru → gerileme yapısal olarak imkânsız; ölçüt: **doğru + netleştirme > 0** | Ö3 *(önce ücretsiz kazanç alınsın)* |
| **Ö5** | `netlestirme_onceligi` ölçümü **≥2 sahipli ölçü nüfusunda** yeniden koşulsun | ⊙ Payda 15'ten büyük; *"kaybedilen"* sütunu **doğruluğu doğrulanmış** cevaplarla sayılsın | Ö4 |
| **Ö6** | ⚠ Hafıza kaydı düzeltilsin: `raw_followup` **düzeltildi** | `project_llm_cube_architecture_audit.md` güncel | — |
| **Ö7** | Kombinatoryal senaryo üreteci (#35) `_norm` kusurunu (A1) kapatsın | ⊙ Üretilen vakalar `_katalog_sizintisi()` kapısından geçsin | — |

> 🔴 **§12'den gelen sıra düzeltmesi:** **Ö8 önce gelir.** Ö2 (ay çekimi) kıyas kapısı
> kurulmadan inerse, `şubata göre` bugünkü **görünür reddinden** §12.2'deki **sessiz
> yanlışa** taşınır. Kapsam açmak, kıyas kapısı olmadan **iyileştirme değildir.**
> Ayrıca **Ö9…Ö12** (mutlak dönem kıyası · `göre` ayrımı · taze çapraz-cube · ölçü→ölçü
> etki) **§12.5'te** ayrı tabloda — bu tablodaki maddeler onları **kapsamaz**.
>
> 🔴 **Sıra önemlidir.** Ö1 ve Ö2 **sıfır LLM, sıfır kota** maliyetiyle kapsam açar ve
> §7'ye göre **kota tüketimini azaltır**. Bayrak tartışmasına (Ö4/Ö5) **onlardan sonra**
> girilmelidir — çünkü Ö1/Ö2'den sonra `prompt_enhancer`'ın nüfusu **değişmiş** olacaktır
> ve bugün ölçmek, yarın geçersiz olacak bir sayı üretir.

---

## 12 · 🔴 İKİ CANLI VAKANIN TAM TEŞHİSİ — **Ö1+Ö2 bunları çözmez**

Kullanıcı iki gerçek cümle sordu: *"bu düzeltmeler gelince bunlar çözülecek mi?"*
⊙ İkisi de uçtan uca ölçüldü. **Cevap: hayır — ve birinde düzeltme, dikkatsiz inerse
görünür bir reddi SESSİZ BİR YANLIŞA çevirir.**

### 12.1 VAKA 1 — `mart cirosunu şubata göre kıyasla`

Ürünün verdiği hata: *"«şubata» kısmını anlayamadım, bu yüzden rapor düşülmedi."*

⊙ Tam teşhis:

| Ölçüm | Sonuç |
|---|---|
| `route()` | **R9** — *"kırılım istendi ama boyut eşleşmedi"* · 🔴 **R10 DEĞİL** |
| `_match_cube` / `_match_measure` | `parti` / **`toplam_ciro`** — ✅ doğru bulunmuş |
| `_period_hit_words` | `['mart']` — 🔴 **`subata` yok** |
| `compare_mode` | **`None`** — 🔴 kıyas niyeti **hiç görülmemiş** |
| `partial_unknowns` | `(['subata'], …)` — **kullanıcıya giden mesajın kaynağı budur** |

**Üç ayrı katman, üst üste:**

| Katman | Kusur | Ö1/Ö2 çözer mi? |
|---|---|---|
| **1** | `şubata` → ay çekimi `_period_hit_words`'e görünmüyor (§5) | ✅ **Ö2 çözer** |
| **2** | `göre` → **kırılım işareti** sanılıyor → ay adı boyut aranıyor → **R9** | ❌ **Hayır** — bu `göre`/`bazında` üç-yönlü aşırı yüklenmesidir, ayrı iş |
| **3** | 🔴 **Mutlak iki-dönem kıyası diye bir yapı YOK** | ❌ **Hayır** — `compare_mode` yalnız **göreli** dönemi bilir |

⊡ Katman 3'ün kanıtı kodda yazılı: `_DONEM_GERI_YIL = ("gecen yil", "onceki yil", …)` ·
`_DONEM_GERI_AY = ("gecen ay", "onceki ay", …)` (`cube_router.py:1382-1383`). Yani sistem
*"geçen aya göre"*yi bilir; **"mart'ı şubat'la"** diye bir kavramı **hiç bilmez**.

### 12.2 🔴 EN AĞIR BULGU — bugün zaten bir **sessiz-yanlış** var

⊙ Aynı niyetin komşu ifadeleri denendi ve **HIT verdiler**. Ürettikleri CubeQuery:

| Soru | `route()` | Üretilen sorgu |
|---|---|---|
| `mart cirosunu **şubat ile** kıyasla` | **HIT** | `parti.toplam_ciro` · `tarih ≥ 2026-02-01` **AND** `tarih ≤ 2026-03-31` |
| `mart cirosunu **şubat cirosuyla** kıyasla` | **HIT** | *(aynı)* |
| `mart ciro` *(kontrol)* | HIT | `tarih ≥ 2026-03-01` AND `tarih ≤ 2026-03-31` |

> 🔴 **Kullanıcı iki ayı KIYASLA dedi; sistem iki ayı TOPLADI.**
> Dönen şey iki sayı değil, **şubat+mart birleşik tek bir sayıdır** — üstelik `source=cube`
> rozeti ve Query Contract'ıyla. İki ay adı bir **aralık** okunuyor, bir **kıyas** değil.
>
> ⊡ Bu, bu deponun kendi tanımıyla *"sistemin üretebileceği en kötü hata sınıfı"*dır
> (`cube_router.py:2496`, `_covers` docstring).

**Ve buradan çıkan sonuç, önceliği tersine çevirir:**

> Kullanıcının çarptığı `şubata göre` biçimi bugün **R9 ile görünür şekilde reddediliyor** —
> yani **şansı yaver gitmiş**. Ö1/Ö2 kapsam kapısını açar da **kıyas kapısı kurulmazsa**,
> bu cümle `şubat ile` varyantıyla **aynı yola** düşer ve dürüst ret, **sessiz yanlışa**
> dönüşür. Kapsam kapısını açmak, **tek başına bir iyileştirme değildir.**

⊙ Tutarsızlığın kaydı: `ocakla haziranı karşılaştır` → **R1** (reddediliyor, çünkü ölçü
kelimesi yok), `mart cirosunu şubatla karşılaştır` → **R10**. Yani aynı niyet, ifadeye göre
**üç farklı sonuç** veriyor: sessiz-yanlış · R9 · R10 · R1.

### 12.3 VAKA 2 — `son 12 aylık makinelerin … verimliliğini ciro üzerindeki etkisini ölç yani kıyasla`

Ürünün verdiği hata: *"«üzerindeki etkisini ölç yani» başka bir konu gibi görünüyor. Hangisini istiyorsun?"*

⊙ Tam teşhis:

| Ölçüm | Sonuç |
|---|---|
| `route()` | **R1** — *"cube eşleşmedi ya da **çapraz konu**"* |
| `_match_cube` | **`None`** — iki cube birden aday |
| `partial_unknowns` | **`['uzerindeki', 'etkisini', 'olc', 'yani']`** ← mesajın kaynağı |
| `ilgili_cubelar` | `oee`, `parti` *(+8)* — 🔴 sistem **iki konuyu da doğru görüyor** |
| Aday ölçüler | `oee.toplam_uretim_kg` · `parti.toplam_agirlik_kg` |

⊙ **Kademeli soyma — bilinmeyen kelimelerin HEPSİ atılınca ne oluyor?**

| Soru | Sonuç |
|---|---|
| `son 12 aylik makine bazinda verimlilik` | **HIT** |
| `son 12 ay ciro` | **HIT** |
| `verimliligin ciro uzerindeki etkisi` | **R1** |
| `verimlilik ciro etkisi` | **R1** |
| **`verimlilik ve ciro`** | 🔴 **R1** — *tek bir bilinmeyen kelime kalmamışken bile* |

> 🔴 **Kanıt kesin:** Ö1 `üzerindeki/etkisini/ölç/yani` kelimelerini dolgu saysa bile
> cümle **yine reddedilir**. Çünkü kusur kelimede değil: **`verimlilik` `oee` cube'unda,
> `ciro` `parti` cube'unda** ve taze bir soruda **iki cube'un ölçüsünü tek sorguya koyacak
> bir yapı yok**.

**İki eksik yapı, ikisi de Ö1/Ö2'nin dışında:**

1. **Taze soruda çapraz-cube birleştirme yok.** ⊡ `cross_cube_add` (`cube_router.py:632`)
   **var**, ama iki şart istiyor: bir **önceki rapor** (`prev`) ve bir **ekleme niyeti**
   (*"bir de … ekle"*). Taze soruda ikisi de yok.
2. 🔴 **"A'nın B üzerindeki etkisi" diye bir analiz türü yok.** ⊡ `app/contribution.py`
   **var** ama başka soruyu cevaplıyor: *"bu değişimi hangi **boyut** açıklıyor"* —
   tek cube, toplanabilir ölçü şartıyla. **Ölçü→ölçü etki/korelasyon** aracı yoktur.

### 12.4 Cevap tablosu — kullanıcının sorusuna doğrudan

| | Vaka 1 · `şubata göre kıyasla` | Vaka 2 · `… ciro üzerindeki etkisi` |
|---|---|---|
| **Ö1** *(fiil/soru kelimesi)* | ❌ ilgisiz *(kusur R10 değil R9)* | ⚠ **mesajı düzeltir, cevabı getirmez** |
| **Ö2** *(ay çekimi)* | ✅ **3 katmandan 1'ini** çözer | ❌ ilgisiz |
| **Kalan** | 🔴 `göre` ayrımı + **mutlak iki-dönem kıyası** | 🔴 taze çapraz-cube + **ölçü→ölçü etki analizi** |
| **Ö1+Ö2 sonrası** | 🔴 **RİSKLİ** — kıyas kapısı kurulmazsa **sessiz-yanlışa** düşer | ✅ **güvenli** — hâlâ reddeder, ama **daha iyi netleştirme chip'iyle** |

### 12.5 Bu bölümün doğurduğu yeni maddeler

| # | İş | Kabul ölçütü | Sıra |
|---|---|---|---|
| **Ö8** | 🔴 **ÖNCE BU:** iki adlandırılmış dönem + kıyas fiili → **aralık toplamına ASLA çökmesin** *(fail-closed)* | ⊙ `mart cirosunu şubat ile kıyasla` **tek birleşik sayı DÖNDÜRMESİN** — ya iki seri ya netleştirme | **Ö2'den ÖNCE** |
| **Ö9** | Mutlak iki-dönem kıyası (`compare` göreli değil **adlandırılmış** dönem alsın) | ⊙ Vaka 1 → iki seri + %değişim | Ö8, Ö2 |
| **Ö10** | `göre`'den sonra gelen **ay adı** boyut adayı sayılmasın | ⊙ `ciro şubata göre` → R9 vermesin; `ciro makineye göre` **HIT kalsın** | Ö2 |
| **Ö11** | Taze soruda çapraz-cube birleştirme *(ortak zaman ekseni)* | ⊙ `verimlilik ve ciro` → iki seri ya da netleştirme, R1 değil | — |
| **Ö12** | Ölçü→ölçü **etki/ilişki** niyeti *(yeni analiz türü — yönlendirme işi değil)* | ⊙ Vaka 2 → ya ilişki grafiği ya *"ilişki mi, iki ayrı seri mi?"* chip'i | Ö11 |

> 🔴 **Ö8, bu raporun tek ACİL maddesidir** — çünkü tek başına **bugün var olan** bir
> sessiz-yanlışı kapatır ve Ö2'nin o yanlışı **yaymasını** önler. Ö1/Ö2'nin önüne geçer.

---

# 13 · 🔴 KÖK NEDEN TARAMASI — **vaka değil, sınıf**

> **Bu bölümün gerekçesi.** Kullanıcı iki cümle verdi, ikisi de patladı. *"Bu tarz belki
> binlerce sorun vardır."* — Doğru varsayım. Vaka avlamak bu yüzden **yanlış yöntemdir**:
> vaka sonsuzdur, **kusur üreten mekanizma sayılıdır**.
>
> ⚠ **Ve prob yöntemi de tek başına yetmez:** korpus, sistemin **kendi sözlüğünden**
> türetildiği için sistemi kendi aynasında ölçüyordu (§6.3). Bu bölüm bu yüzden
> **kodun mantığını** okuyarak yazıldı; ölçüm yalnız **doğrulama** için kullanıldı.

## 13.0 Önce bir düzeltme — geri çektiğim bir sayı

İlk taramamda *"ÜSTÜNLÜK YUTULDU: 41 vaka"* çıkmıştı. **Yanlıştı.** `order` ve `limit`,
`cube_query`'nin **içinde değil kardeşidir** (`route()` → `{cube_query, measure, order,
limit, period_optional}`); ben yanlış sözlüğe bakmışım.

⊙ Doğrusu: `ciro en yüksek 5 makine` → `order=('toplam_ciro','DESC')`, `limit=5`.
**Üstünlük ifadesi doğru çalışıyor.** Sayı geri çekildi.

---

## 13.1 Yedi kök neden

Aşağıdakiler **kusur değil, kusur üreteçleridir**. Her biri sınırsız sayıda vaka doğurur.

---

### 🔴 KN-1 · **İki eşleştirme rejimi var ve hangisinin kullanılacağı her çağrı yerinde elle seçiliyor**

⊡ Depoda kelime eşleştirmenin **iki** yolu var:

| Rejim | Fonksiyon | Bilir | Kullanım |
|---|---|---|---|
| **A · yapısal** | `_syn_hit()` — kelime başı + geçerli ek zinciri (`_ek_gecerli`) | Türkçe çekimini | **18 çağrı** |
| **B · çıplak** | `w in q` — alt-dize | **hiçbir şey** | aşağıdaki listeler |

⊡ Rejim B ile taranan sözlükler:

| Sözlük | Tarama yeri | Ne kırılıyor |
|---|---|---|
| `_BREAKDOWN_HINTS` | `:866`, `:1191` — `any(w in q …)` | kırılım niyeti |
| `_COMPARE_HINTS` | `:3026` — `any(w in q …)` → **R3 kapısı** | kıyas reddi |
| `_EXCLUDE_MARKERS` | `:3090` — `{w … if w in q}` | dışlama filtresi |
| `_TH_WORDS` | `:3243` — `{w … if w in q}` | eşik/sayı ifadesi |

**Neden kök neden:** Rejim B **iki yönlü** hata üretir — çekimli biçimi **kaçırır**
(yanlış-negatif → red) ve kazara alt-dizeyi **yakalar** (yanlış-pozitif → sessiz yanlış).
Ve bu, `_covers` docstring'inde **zaten belgelenmiş** bir hata sınıfıdır
(`kar ⊂ ankara`, `fire ⊂ firesiz` …) — orada düzeltilmiş, **bu dört yerde düzeltilmemiş**.

> Bir dilde iki eşleştirme rejimi olması, **hangi kuralın geçerli olduğunun
> dosyanın hangi satırında olduğunuza bağlı olması** demektir.

---

### 🔴 KN-2 · **Aynı kuralın birden çok sahibi var ve farklı cevap veriyorlar**

⊙+⊡ Kanıtlanmış üç çift:

| # | Soru | Sahip A *(doğru cevaplayan)* | Sahip B *(kullanılan)* | Sonuç |
|---|---|---|---|---|
| 1 | *"bu kelime bilinen bir kökün çekimi mi?"* | `_covers`/`_ek_gecerli` → `martta`✅ | `_period_hit_words` ay taraması `\b…\b` → `martta`❌ | §5 · **60/60 ay çekimi ölür** |
| 2 | *"bu bir kıyas mı?"* | `compare_mode()`/`_kiyas_spanlari` — **yapısal** | `_COMPARE_HINTS` — **elle liste** (R3 kapısı) | §12 · kıyas ya reddedilir ya yutulur |
| 3 | *"bu kelime dolgu mu?"* | `_ek_gecerli` — yapısal | `_STOP_STEMS` — **elle liste** | §4.3 · `yaptık`✓ `verdik`✗ |

⊡ **Ve depo bu deseni kendisi üç kez kaydetmiş:**
- `:2405` — *"İki tüketici vardı ve **aynı soruyu farklı cevaplıyorlardı**."*
- `:1362-1370` — *"ÖNCEDEN elle sayılmış altdize listeleriydi… `_syn_hit`'in tam olarak
  yerine geçmek için var olduğu **anti-desen**."* — **ama `_COMPARE_HINTS` hâlâ orada.**
- `:2100` — *"`_misc_hit_words`/`_period_hit_words` için verilen kararın aynısı."*

> 🔴 **Desen tanınmış, tek tek düzeltilmiş, ama bir KAPIYA bağlanmamış.** Bu yüzden her
> yeni özellik onu yeniden doğuruyor. Kök neden **kusur değil, kusurun tekrarına izin
> veren boşluk**.

---

### 🔴 KN-3 · **Tek-geçiş tarama — çok varlıklı soruda ikincisi sessizce kayboluyor**

⊡ `cube_router.py`: `.search(` **34 kez**, `.finditer(` **10 kez**.
⊡ `_period_hit_words` (`:2063-2065`) yedi dönem regex'ini **`.search`** ile tarıyor — yani
**ilk eşleşme kazanır, ikincisi yok sayılır**.

⊡ Bu hata ay adları için **bir kez** bulunup düzeltilmiş (`:2076` yorumu: *"`re.search`
DEĞİL `re.finditer`: … ikinci ay adı SESSİZCE 'unknown' kalır"*) — **kalan yedi regexte
düzeltilmemiş.**

⊙ Sonucu ölçüldü:

| Soru | `_period_hit_words` | `route()` | Gerçekte ne oluyor |
|---|---|---|---|
| `2025 ve 2026 ciro` | **`[]`** | **HIT** | 🔴 **hiç tarih filtresi yok** → tüm tarihin toplamı |
| `ilk çeyrek ve ikinci çeyrek ciro` | `['ceyrek','ilk']` | **R10** | ikinci çeyrek "bilinmeyen kelime" |
| `son 3 ay ve son 6 ay ciro` | `['ay','son']` | HIT | ikinci dönem yutulmuş |

---

### 🔴🔴 KN-4 · **Niyet–sorgu uyum denetimi YOK (fail-open)**

`route()` bir CubeQuery ürettiğinde, o sorgunun **sorudaki niyet işaretlerini taşıyıp
taşımadığı hiçbir yerde denetlenmiyor.** Üretildi mi, cevap gider.

⊡ Kısmi bir koruma **var** — `_BREAKDOWN_HINTS` için, **iki** yerde (`:866`, `:1191`),
kodda adı bile *"SESSİZ-YANLIŞ koruması"*. **Ama genelleştirilmemiş:** kıyas, dönem,
dışlama, trend için karşılığı yok.

⊙ Ölçülen sonuç — üç sessiz-yanlış **sınıfı**:

| Sınıf | Vaka | Örnek → üretilen sorgu |
|---|---|---|
| **IKI_DONEM_TOPLANDI** | **14** | `ocak ve haziran ciro karşılaştır` → `tarih 2026-01-01 … 2026-06-30` **tek toplam** |
| **KIYAS_FIILI_YUTULDU** | **21** | `2025 ve 2026 ciro kıyasla` → **filters=[]** → tüm tarih toplamı |
| **TREND_YUTULDU** | **7** | `ciro değişimi son 6 ay` → `timeDimensions=[]` → **tek sayı** |

> 🔴 Üçü de aynı biçimde ölür: **kullanıcı bir yapı istedi (iki seri / zaman ekseni),
> sistem tek sayı verdi** ve üstüne `source=cube` rozeti taktı.
>
> ⚠ `TREND_YUTULDU`, borç defterindeki *"«değişim» istenip TOPLAM verildi (CANLI)"*
> kaydıyla **birebir aynı sınıftır** — yani bu sınıf canlıda **zaten görülmüş**, tekil
> vaka olarak kaydedilmiş, **sınıf olarak kapatılmamış**.

---

### 🔴 KN-5 · **Teşhis ile kullanıcıya giden mesaj ayrı mekanizmalardan geliyor**

⊙ §12.1: `route()` **R9** ("boyut eşleşmedi") diyor; kullanıcı **"«şubata» kısmını
anlayamadım"** görüyor. İki ayrı yer:

- **Red gerekçesi** → `red_gerekcesi()` (`route()` içindeki `_reddet` zinciri)
- **Kullanıcı mesajı** → `partial_unknowns()` (`ask.py`'de, ayrı hesap)

⊡ Ve `route()`'un kapı sırası bunu kaçınılmaz kılıyor: **R10 (kapsam) EN SONDA**
(`:3251`), R1…R9 ondan önce. Yani **tanınmayan kelime olduğunu bilmeden** dokuz kapı
karar veriyor ve ilki durursa gerekçe **o kapının** gerekçesi oluyor.

> Sonuç: kullanıcıya **yanlış teşhis** gidiyor, ve o teşhise göre cümlesini düzeltmeye
> çalışıyor. Kusuru gizlemekten daha kötüsü, **yanlış yeri işaret etmektir**.

---

### 🔴 KN-6 · **Aşırı yüklenmiş kelimeler tek anlama sabitlenmiş**

⊡ `gore` **aynı anda** üç sözlükte:
`_BREAKDOWN_HINTS` (kırılım) · `_BITISIK_EDAT` (kıyas edatı) · granülarite ipucu.

Kod bunu **sıraya** bağlayarak çözüyor (hangi kapı önce koşarsa o kazanır) — **belirsizlik
olarak işaretlemiyor**. §12.1'in R9'u tam olarak budur: `şubata göre` → `göre` kırılım
sayıldı → ay adı boyut arandı → bulunamadı → R9.

Aynı sınıf, katalogda da var: `tipi` hem `cari_tip` hem `evrak_tip` hem `hesap_tipi`
sinonimi; `grubu` hem `ham_grup` hem `yas_grubu` hem `ana_grup`. ⊙ `route()` bunu **R7**
("boyut adayı tek değil") ile reddediyor — **doğru davranış**, ama chip üretmeden.

---

### 🔴 KN-7 · **Bazı şeyler bozuk değil — YOK. Ve yokluk, "anlamadım" diye raporlanıyor.**

⊙ Ölçülen üç eksik yapı:

| Eksik yapı | Bugünkü davranış | Doğru davranış |
|---|---|---|
| Mutlak iki-dönem kıyası | 🔴 **iki dönemi toplar** (KN-4) | *"iki ayrı seri mi istiyorsun?"* |
| Taze soruda çapraz-cube | R1 *"başka konu gibi"* | *"verimlilik mi, ciro mu, ilişkileri mi?"* |
| Ölçü→ölçü etki/ilişki | R1 | 🔴 *"**bunu henüz yapamıyorum**"* |

> 🔴 **En sinsi kök neden bu.** Sistem *"bu analizi yapamıyorum"* ile *"bu kelimeyi
> anlamadım"*ı **ayırt edemiyor** ve ikisini de aynı mesajla veriyor. Kullanıcı, cümlesini
> düzeltirse cevap alacağını sanıyor — oysa **hangi cümleyi kursa alamayacak**.

---

## 13.2 Kök nedenlerin ürettiği kusur haritası

| Kök neden | Doğurduğu ölçülmüş kusurlar | Bulgu |
|---|---|---|
| **KN-1** iki rejim | kırılım/kıyas/dışlama/eşik işaretlerinin çekimli biçimi kaçıyor | §13.1 |
| **KN-2** çok sahip | ay çekimi (60/60) · dolgu sözlüğü (77/112) · kıyas reddi | B3·B4·B5·B6 |
| **KN-3** tek geçiş | çok-dönemli soruda ikinci dönem yutulur | KN-3 tablosu |
| **KN-4** uyum yok | **42 vaka, 3 sessiz-yanlış sınıfı** | B8 |
| **KN-5** ayrık teşhis | yanlış hata mesajı → kullanıcı yanlış yeri düzeltir | §12.1 |
| **KN-6** aşırı yükleme | `göre` → R9 · `tipi`/`grubu` → R7, chip'siz | §12.1·B7 |
| **KN-7** eksik yapı | Vaka 2 · mutlak kıyas · ölçü→ölçü | §12.3 |

**Ve iki kök neden birbirini besliyor:** KN-2 kapsam kapısını gereksiz sıkı yapıyor (red),
KN-4 ise geçen soruları denetimsiz bırakıyor (sessiz yanlış). Yani sistem **yanlış yerde
katı, yanlış yerde gevşek**. Kapsam kapısını KN-4 kurulmadan gevşetmek, **kayıpları
redden sessiz-yanlışa taşır** — §12.2'nin kanıtladığı şey budur.

---

## 13.3 🔴 KÖK ÇÖZÜMLER

> Bunlar **öneri**dir, uygulama değil. Her biri **tek tek vaka değil, bir sınıfın
> tamamını** kapatmayı hedefler ve her birinin **kapı ölçütü** yazılıdır.
> Sıra bilinçlidir: **önce fail-closed, sonra kapsam.**

### KÇ-1 · **NİYET–SORGU UYUM KAPISI** *(en yüksek getirili tek mekanizma)*

`route()` bir CubeQuery ürettiğinde, dönmeden önce **soruda bulunan her niyet işaretinin
sorguda bir karşılığı olduğu** denetlensin. Karşılığı yoksa → **cevap değil, netleştirme**.

| | |
|---|---|
| **Kapsadığı sınıf** | KN-4'ün tamamı: kıyas · çok-dönem · trend · dışlama · kırılım |
| **Neden kök** | Vaka listesi değil, **değişmez listesi**. Yeni bir niyet eklendiğinde denetimi de eklenir |
| **ADR uyumu** | ADR-0008'in **doğrudan uygulaması**: taşınamayan niyet = anlaşılmamış soru |
| **Zaten var olan çekirdek** | `_BREAKDOWN_HINTS` koruması (`:866`, `:1191`) — **genelleştirilecek**, sıfırdan yazılmayacak |
| ⊙ **Kapı ölçütü** | §13.1'in 42 vakasının **hiçbiri** tek-toplam döndürmesin; `en yüksek 5` gibi bugün DOĞRU çalışanlar **bozulmasın** |
| ⚠ **Riski** | Kapsam daralır (bugün cevaplanan bazı sorular netleştirmeye düşer) — **ölçülmeli**, §6.2'nin hatası tekrarlanmamalı |

### KÇ-2 · **TEK BİÇİMBİRİM KAPISI** — `in q` ile sözlük taraması yasaklansın

Tüm kelime-sözlüğü eşleştirmesi **tek fonksiyondan** geçsin (`_syn_hit`/`_covers` ailesi).

| | |
|---|---|
| **Kapsadığı** | KN-1 + KN-2'nin 1. ve 3. çifti |
| ⊙ **Kapı ölçütü** | Modülde `_…HINTS`/`_…MARKERS`/`_…WORDS` sözlüklerinden **hiçbiri** `in q` ile taranmasın — bu bir **grep testiyle** kilitlenebilir (kod-yapısı testi, davranış testi değil) |
| **Neden kök** | Yeni sözlük ekleyen geliştiriciyi **doğru rejime zorlar**; desenin tekrarını **kapıya** bağlar |

### KÇ-3 · **SÖZLÜK → KURAL** dönüşümü *(mevcut görev #36)*

`_STOP_STEMS`'e kelime eklemek yerine **yapısal kural**: *"katalogda karşılığı olmayan,
Türkçe çekim eki taşıyan fiil/soru token'ı dolgudur."*

| | |
|---|---|
| **Kapsadığı** | B3+B6 — §4'ün 77/112'si |
| ⊙ **Kapı ölçütü** | §4 probu **≥%90 HIT**, `_STOP_STEMS`'e **tek kelime eklenmeden** |
| ⚠ **Ön koşul** | 🔴 **KÇ-1 önce inmeli.** Aksi hâlde açılan kapsam, KN-4'ün sessiz-yanlışlarını **yayar** (§12.2) |

### KÇ-4 · **ÇOK-GEÇİŞ ZORUNLULUĞU** — varlık tarayıcıları `finditer` kullansın

| | |
|---|---|
| **Kapsadığı** | KN-3 |
| ⊙ **Kapı ölçütü** | `2025 ve 2026 ciro` → **iki dönem** görülsün; `_period_hit_words` çok-dönemli sorularda **hepsini** döndürsün |

### KÇ-5 · **TEK TEŞHİS KAYNAĞI** — kapsam denetimi kapı sırasında **başa** alınsın

R10 en sondan **öne** taşınsın; kullanıcıya giden mesaj ile `red_gerekcesi()` **aynı
hesaptan** üretilsin.

| | |
|---|---|
| **Kapsadığı** | KN-5 |
| ⊙ **Kapı ölçütü** | `mart cirosunu şubata göre kıyasla` → gerekçe **R9 değil**, kullanıcı mesajıyla **tutarlı** olsun |
| ⚠ **Yan etki** | Kapı sırası değişimi **davranış değiştirir** — bugün R1…R9 ile reddedilen sorular R10'a kayar. Ölçülmeli |

### KÇ-6 · **BELİRSİZLİK SIRAYA DEĞİL CHİP'E BAĞLANSIN**

Aşırı yüklenmiş kelime (`göre`, `tipi`, `grubu`) ve çok-sahipli ölçü (`bakiye`) tek bir
yorumda sabitlenmesin; **deterministik olarak bilinen** aday kümesi kullanıcıya sorulsun.

| | |
|---|---|
| **Kapsadığı** | KN-6 + B7 |
| **Zaten var** | `measure_cube_candidates` tam 2 aday üretiyor (§8); `netlestirme_onceligi` mekanizması yazılı |
| ⊙ **Kapı ölçütü** | §6.2'nin A/B'si **≥2 sahipli nüfusta** yeniden koşulsun; *"kaybedilen"* sütunu doğruluğu doğrulanmış cevaplarla sayılsın |

### KÇ-7 · **YETENEK BEYANI** — *"anlamadım"* ile *"yapamıyorum"* ayrılsın

Sistem desteklediği **analiz türlerini** açıkça beyan etsin; desteklenmeyen bir niyet
(ölçü→ölçü etki, mutlak dönem kıyası, çapraz-cube) **dürüstçe** öyle söylensin.

| | |
|---|---|
| **Kapsadığı** | KN-7 — Vaka 2'nin tamamı |
| **Neden kök** | Kullanıcının **boşuna cümle düzeltmesini** bitirir; yol haritasına da **eksik yetenek listesi** çıkarır |
| ⊙ **Kapı ölçütü** | Vaka 2 → *"iki ölçü arasındaki ilişkiyi henüz ölçemiyorum; ayrı ayrı gösterebilirim"* |

---

## 13.4 Uygulama sırası — **bağımlılıkla**

```
KÇ-1  NİYET–SORGU UYUM KAPISI        ← ÖNCE. Tek başına 3 sessiz-yanlış sınıfını kapatır
  │                                     ve sonrakilerin zarar vermesini önler
  ├── KÇ-4  çok-geçiş (finditer)      ← ucuz, KN-3'ü kapatır
  ├── KÇ-2  tek biçimbirim kapısı     ← KN-1 + KN-2
  │     └── KÇ-3  sözlük→kural (#36)  ← kapsamı AÇAR (bu yüzden en son)
  ├── KÇ-5  tek teşhis kaynağı        ← bağımsız, mesaj kalitesi
  ├── KÇ-6  belirsizlik → chip        ← bağımsız
  └── KÇ-7  yetenek beyanı            ← bağımsız, en ucuz, en görünür kazanç
```

> 🔴 **Tek cümlelik kural:** *kapsamı açan her iş, uyum kapısından SONRA gelir.*
> Aksi hâlde her açılan kapı, dürüst reddi sessiz yanlışa çevirir.

---

## 13.5 Bu taramanın **bulamadıkları** — dürüst sınırlar

| Sınır | Etkisi |
|---|---|
| Yalnız `cube_router.py` + `ask.py` yönlendirme yolu okundu | `interpret.py`, `answer.py`, `viz.py`, `compose.py` **taranmadı** — orada ayrı kök nedenler olabilir |
| Değişmez listesi **elle yazıldı** (7 değişmez) | Yazmadığım her niyet türü **görünmez** kaldı — liste **tam değildir**, genişletilmelidir |
| Takip (followup) yolu **taranmadı** | `deterministic_refine`, `cross_cube_*` bu raporun dışında |
| LLM basamağının **çıktı kalitesi** ölçülmedi | Kota nedeniyle; §6 yalnız **bağlanma** durumunu denetler |
| Katalog/sinonim **içerik** kalitesi ölçülmedi | R1'in 26/42'si (§3.2) buradan gelebilir — **ayrı bir denetim konusu** |

> 🔴 **En önemli sınır:** R1 (cube eşleşmedi) korpusun **%61,9'u** ve bu rapor onu
> **açıklamıyor**. Kapsam kapısı (R10) daha görünür bir kusur ama **daha küçük** paydadır.
> R1'in kökü katalog sözlüğünde mi, çapraz-konu ayrımında mı, yoksa yine KN-1'de mi —
> **ölçülmedi**. Bir sonraki denetimin ilk konusu **bu olmalıdır.**

---

# 14 · 🔴 KÖRLÜK DENETİMİ — **raporun kendisine başka açıdan bakış**

> Rapor bitince kendi kör noktalarımı aradım. **Üç tanesi ciddiydi**, biri raporun
> **ana tezini eksik bırakıyordu.** Bu bölüm onları kapatır ve §13'ü **genişletir**,
> geçersiz kılmaz.

## 14.1 Kör nokta envanteri

| # | Körlük | Ağırlık | Durum |
|---|---|---|---|
| **K1** | 🔴 **R1'i (kusurların %62'si) hiç araştırmadım** — sınır olarak yazıp geçtim | 🔴🔴🔴 | ✅ **§14.2'de kapatıldı** |
| **K2** | 🔴 **Her şeye KOD olarak baktım — KATALOG katmanına hiç bakmadım** | 🔴🔴🔴 | ✅ **§14.3'te kapatıldı** |
| **K3** | 🔴 Önerilerimin **hepsi savunmacıydı** (kapı, ret, netleştirme) — hiçbiri **yetenek artırmıyordu** | 🔴🔴 | ✅ **§14.5'te kapatıldı** |
| **K4** | `route()`'a *"bozuk"* dedim; **ne olması gerektiğini** sormadım | 🔴🔴🔴 | ✅ **§14.4 — raporun asıl tezi** |
| **K5** | Sessiz-yanlış değişmezlerini **elle** yazdım → yazmadığım niyet **görünmez** | 🔴🔴 | ⚠ açık — §13.5'te yazılı |
| **K6** | Takip (followup) yolunu, `interpret.py`/`answer.py`/`compose.py`'yi taramadım | 🔴🔴 | ⚠ açık |
| **K7** | Ürünün **uçtan uca** ne cevapladığını ölçmedim (kota) — yalnız `route()` erişimini | 🔴 | ⚠ açık, gerekçesi yazılı |

---

## 14.2 K1 KAPATILDI — **R1'in kökü tek bir şey değil, DÖRT ayrı şey**

⊙ Korpustaki 26 R1 vakası, `ilgili_cubelar()` aday sayısına göre ayrıştırıldı:

| Aday cube | Vaka | Anlamı |
|---|---|---|
| **0** | **20** | katalog **hiçbir** konu tanımadı |
| **1** | **4** | tek aday **var** ama yine R1 |
| **≥2** | **2** | yapay çapraz konu |

Ve "0 aday" grubunun içi okununca **dört ayrı sınıf** çıktı — tek bir kusur değil:

| Sınıf | Vaka | Örnek | Doğru davranış |
|---|---|---|---|
| **A · FİİL biçimi** 🔴 | 4 | `ne kadar **sattık**` · `kim bize ne kadar **borçlu**` · `en çok kim **alıyor**` · `ne kadar **alacağımız var**` | **cevap** — katalogda karşılığı VAR |
| **B · ölçüsüz soru** | 7 | `işler nasıl gidiyor` · `bu ay iyi miyiz` · `neden böyle oldu` · `ne yapmalıyız` | **netleştirme** — *"hangi ölçü?"* |
| **C · eksik cümle / bağlam** | 3 | `peki ya geçen sene` · `ocakla haziranı karşılaştır` · `dün bugüne göre nasıldı` | bağlam + ölçü chip'i |
| **D · doğru ret** ✅ | 6 | `neler yapabilirsin` · `bana bir fıkra anlat` · `asdf qwerty zxcv` · `mikatr ne kadar` | ✅ **bugünkü davranış doğru** |

### 🔴 KN-8 · **Katalog yalnız İSİM biçimini biliyor; kullanıcı FİİL kuruyor**

Sınıf A'nın kökü budur ve **yeni bir kök nedendir**:

| Kullanıcının kelimesi | Katalogdaki karşılık | `route()` |
|---|---|---|
| `sattık` *(fiil)* | `satis` *(isim)* — `parti`/`ticaret` ölçü sinonimi | ❌ |
| `borçlu` *(sıfat)* | `borc` *(isim)* — `toplam_borc` | ❌ |
| `alacağımız var` | `alacak` *(isim)* — `toplam_alacak` | ❌ |
| `fire verdik` | `fire` ✓ *(§3.3'te ölçü bulunmuştu)* | ❌ *(R10)* |

> 🔴 **Ayrım kritik:** `_ek_gecerli` **ÇEKİMİ** (satış→satışı, satışlar) çözer.
> Bu vakalar **TÜRETME**dir (sat‑→satış, borç→borçlu, al‑→alacak) — **farklı bir
> dilbilimsel işlem** ve depoda karşılığı **yok**.
>
> Türkçede türetme **üretkendir**: her isim bir fiilden, her fiil bir isimden türeyebilir.
> Bu yüzden **sözlüğe kelime eklemek bu sınıfı kapatmaz** (ADR-0008) — kural gerekir.

### 14.2.1 Yan bulgu — **tek aday var ama YANLIŞ**

⊙ 1 adaylı 4 vakanın adayları:

| Soru | `ilgili_cubelar` | Değerlendirme |
|---|---|---|
| `en çok nerede kaybediyoruz` | `['isg']` | 🔴 **yanlış** — "kayıp" iş güvenliği değil |
| `nerede artıyor bu` | `['isg']` | 🔴 **yanlış** |
| `bu gidişle yılı nerede kapatırız` | `['isg']` | 🔴 **yanlış** |
| `düşüşün sebebi ne` | `['kalite']` | ⚠ tartışmalı |

> 🔴 Bu, §8'in *"belirsizliği chip'e çevir"* önerisine **bir uyarı** ekler: chip'in
> **kaynağı `ilgili_cubelar` ise, kendinden emin ve yanlış** bir konu önerilir.
> Netleştirme chip'i açılmadan önce **chip kalitesi ölçülmelidir.**

---

## 14.3 K2 KAPATILDI — **KATALOG katmanı, kodun kendisi kadar kusur üretiyor**

§13'ün tamamı koda bakıyordu. Katalog **hiç denetlenmemişti**. ⊙ Denetlendi:

### 🔴 KN-9 · Cube-düzeyi sinonimler **boyut kelimeleri taşıyor** → yapay çapraz konu

⊙ **55 çarpışma**: bir cube'un **cube-düzeyi** sinonimi, başka bir cube'un **boyut**
sinonimi. En sıkları:

| Kelime | Çarpışma | Örnek |
|---|---|---|
| `musteri` | **×8** | `parti`'nin **cube** sinonimi ↔ `cari`'nin **boyutu** |
| `cari` | ×5 | `cari` cube ↔ `firsat` boyutu |
| `vardiya` | ×4 | `oee` cube ↔ `ik` boyutu |
| `departman` | ×4 | `parti` cube ↔ `butce` boyutu |
| `satis` · `egitim` · `renk` · `operator` | ×3-4 | … |

⊡ Somut örnek — `parti` cube'unun **cube-düzeyi** sinonim listesi:
`fire, ciro, gelir, tutar, satis, kar, marj, sapma, agirlik, kilo, parti, **musteri,
kumas, renk, asama, boyama, yikama, apre, kurutma, maliyet, operator, calisan, personel,
cinsiyet, yas, egitim, departman**`

> 🔴 Kalın yazılanların **hepsi boyut adı** — *"bu soru `parti` konusundadır"* demezler.
> `musteri` kelimesi geçen **her** soru `parti` cube'una aday oluyor; `maliyet` kelimesi
> hem `maliyet` hem `parti` cube'unu çağırıyor → `_match_cube` iki aday görüp **None**
> dönüyor → **R1**.
>
> ⊙ Ölçülen sonuç: `bunu makinelere böl` → **10 aday cube**. `zayiat durumumuz ne alemde`
> → **5 aday**, hiçbiri doğru değil.

### 🔴 KN-10 · **8 kelime ≥2 cube'un cube-düzeyi sinonimi** — gerçek sahiplik belirsizliği

⊙ `bakim`·`ariza`·`tamir`·`sapma`·`egitim`·`marj`·`maliyet`·`satis`

Bunlar **kusur değil, karar eksikliğidir** — ⊡ ADR-0029'un (`metrik_kaydi`) tam olarak
çözmek için var olduğu sınıf. `_match_cube`'un ilk satırı bu kaydı okuyor (`:2999`) ama
kayıt **boş** olduğunda karar **ölçü sinonimi uzunluğuna** düşüyor: ⊡ kodun kendi
ifadesiyle *"deterministik ama **keyfi**"*.

---

## 14.4 🔴🔴 K4 KAPATILDI — **raporun asıl tezi: `route()` bir EŞLEŞTİRİCİ, ama ona ÇÖZÜMLEYİCİ işi yaptırılıyor**

Bütün §13, `route()`'un **nasıl** bozulduğunu anlatıyor. Sormadığım soru: **neden hep aynı
biçimde bozuluyor?**

⊙ `route()` = `cube_router.py:2985-3309` — **325 satır**, **50 dallanma noktası**
*(`if`/`elif`/`for`/`while`/`try`)*, **11 `_reddet` çağrısı / 10 ayrı red kodu** — ve tek
bir fonksiyon içinde **iki bambaşka iş** yapıyor:

| İş | Doğası | Bu raporda karşılığı |
|---|---|---|
| **ÇÖZÜMLEME** *(parse)* — Türkçeyi anla: çekim, türetme, dönem ifadesi, kıyas/kırılım/üstünlük/dışlama işareti, eksiltme | **dilbilimsel** · katalogdan **bağımsız** | KN-1·2·3·6·8 |
| **EŞLEŞTİRME** *(match)* — çözümlenmiş varlıkları kataloğa bağla, CubeQuery kur | **katalogsal** · dilden **bağımsız** | KN-9·10 |

> 🔴 **Tüm kök nedenler bu iki işin AYNI yerde yapılmasından doğuyor:**
>
> - **KN-2 (çok sahip)** kaçınılmaz — çünkü *"bu bir çekim mi?"* sorusunun **ayrı bir
>   sahibi yok**, her eşleştirici kendi cevabını üretiyor.
> - **KN-1 (iki rejim)** kaçınılmaz — çünkü çözümleme bir **katman** değil, eşleştirmenin
>   içine serpiştirilmiş **yardımcı fonksiyonlar**.
> - **KN-4 (uyum denetimi yok)** kaçınılmaz — çünkü ortada denetlenecek bir **niyet
>   nesnesi yok**; niyet hiçbir yerde **temsil edilmiyor**, doğrudan CubeQuery'ye
>   çevriliyor. Karşılaştırılacak iki şey olmadan uyum denetlenemez.
> - **KN-5 (ayrık teşhis)** kaçınılmaz — çünkü *"anlamadığım kelime"* bilgisi
>   çözümlemenin çıktısı olacakken, on kapının **yan etkisi** olarak dağılmış.
>
> **Yani §13'ün yedi kök nedeni, tek bir mimari kararın yedi belirtisidir.**

⚠ **Ve bu, ürünün tezini çürütmez — tam tersine açıklar.** *"LLM garson, küp aşçı"* doğru
bir tezdir. Ama bugün **garson yok**: siparişi **aşçı alıyor**. `route()`, mutfağın
kapısında durup müşterinin Türkçesini çözmeye çalışıyor — ve doğal olarak, müşteri
menüdeki kelimeleri kullanmadığında **siparişi geri çeviriyor**.

---

## 14.5 K3 KAPATILDI — **yetenek artıran kök çözümler** *(§13.3'e ek)*

§13.3'ün yedi önerisi de savunmacıydı: kapı, ret, netleştirme. **Hiçbiri sistemin
cevaplayabildiği soru sayısını artırmıyordu.** Aşağıdakiler onu artırır.

### 🔴🔴 KÇ-0 · **ÇÖZÜMLEME ve EŞLEŞTİRME ayrılsın** *(§14.4'ün doğrudan sonucu)*

Araya **niyet nesnesi** (`Niyet`) girsin: soru → *deterministik Türkçe çözümleyici* →
`{ölçü_adayları, dönemler[], kırılımlar[], filtreler[], niyet_türü, üstünlük, bilinmeyenler[] }`
→ *eşleştirici* → CubeQuery.

| | |
|---|---|
| **Kapsadığı** | KN-1·2·3·4·5·6 — **altısı birden**, çünkü hepsi bu ayrımın yokluğunun belirtisi |
| **Neden yetenek artırır** | Niyet nesnesi **çok dönem**, **çok ölçü**, **iki cube** taşıyabilir — bugün `route()`'un **temsil edemediği** her şey |
| **KÇ-1 ile ilişkisi** | Uyum kapısı ancak bir **niyet nesnesi** varsa yazılabilir. KÇ-1, KÇ-0'ın **ilk müşterisidir** |
| ⚠ **Gerçekçilik** | Bu **büyük** bir iş. Ama **kademeli** inebilir: önce yalnız *okuyan* bir çözümleyici (davranış değişmez), sonra tüketiciler tek tek ona taşınır |
| ⊙ **Kapı ölçütü** | Faz 1: `Niyet` üretilir ve **loglanır**, `route()` davranışı **birebir aynı** kalır — sıfır gerileme, tam görünürlük |

### 🔴 KÇ-8 · **BEYANLI KISMİ CEVAP** — üçüncü seçenek

Bugün iki seçenek var: **cevapla** ya da **reddet**. Üçüncüsü yok: *"cevabın şu kısmını
verdim, şu kısmını **veremedim** ve nedeni bu."*

| | |
|---|---|
| **Neden kök çözüm** | KÇ-1'in (uyum kapısı) **kapsam daraltma riskini** ortadan kaldırır: taşınamayan niyet artık cevabı **öldürmez**, **etiketler** |
| **Örnek** | `ocak ve haziran ciro karşılaştır` → *"Ocak: ₺X · Haziran: ₺Y"* değil de yapamıyorsa: *"Ocak–Haziran toplamı ₺Z. ⚠ **Kıyas yapamadım** — iki dönemi ayrı ayrı isterseniz…"* |
| **ADR uyumu** | ADR-0008 *"yanlış cevaba güven rozeti takma"* der — **beyanlı** kısmi cevap rozetsizdir, yasağı çiğnemez |
| ⊙ **Kapı ölçütü** | §13.1'in 42 sessiz-yanlışı **etiketli** dönsün; hiçbiri çıplak `source=cube` rozeti almasın |

### 🔴 KÇ-9 · **RED KAYITLARI SÖZLÜK BOŞLUĞUNU KENDİ KEŞFETSİN**

⊡ `interaction_log` bugün `question` + `reject_reason` yazıyor (`answer.py:198`) —
ama **hangi kelimenin tanınmadığını yazmıyor**.

| | |
|---|---|
| **Öneri** | `uncovered_words` + `aday_cubelar` kolonları eklensin |
| **Neden kök çözüm** | Sözlük boşluğu **kendini bildiren** bir veri kümesine dönüşür: *"bu ay 412 soru `sattık` yüzünden düştü"* → katalog kararı **ölçüyle** verilir, tahminle değil |
| **Yan kazanç** | 🔴 Görev **#35**'in (kombinatoryal senaryo üreteci) gerekçesini **azaltır**: elle vaka yazmak yerine **gerçek red kayıtları** korpus olur — ve §6.3'ün *"kendi sözlüğünü ölçme"* tuzağına **yapısal olarak** düşemez |
| ⊙ **Kapı ölçütü** | Bir haftalık kayıttan *"en sık düşüren 20 kelime"* raporu üretilebilsin |

### 🔴 KÇ-10 · **TÜRETME (derivation) katmanı** — KN-8'in kök çözümü

Çekim (`_ek_gecerli`) var, **türetme yok**. Türkçenin üretken isim↔fiil ekleri
(`-ış/-iş`, `-ma/-me`, `-acak/-ecek`, `-lı/-li`, `-cı/-ci`) **kapalı bir kümedir** —
sözlük değil, **kural**.

| | |
|---|---|
| **Kapsadığı** | KN-8 · §14.2 sınıf A · §4'ün `verdik` sınıfının bir kısmı |
| **ADR uyumu** | ADR-0008 uyumlu: kapalı dilbilimsel sınıf, katalog dağarcığını **kovalamaz** |
| ⚠ **Riski** | 🔴 Türetme **anlamı kaydırabilir** (`al‑`→`alacak` ✓ ama `al‑`→`alıcı` boyut). **Fail-closed** olmalı: türetilmiş eşleşme **doğrudan cevap değil, chip** üretsin |
| ⊙ **Kapı ölçütü** | `ne kadar sattık` → `satis_tutari` **ya da** *"tutar mı miktar mı?"* chip'i; **sessiz yanlış üretmesin** |

### 🔴 KÇ-11 · **KATALOG ÇARPIŞMA DENETİMİ — derleme zamanında bir KAPI**

| | |
|---|---|
| **Kapsadığı** | KN-9 (55 çarpışma) + KN-10 (8 çok-sahipli kelime) |
| **Öneri** | Cube derlenirken denetlensin: *(a)* cube-düzeyi sinonim **boyut adı olamaz**; *(b)* ≥2 cube'un sahiplendiği kelime `metrik_kaydi`'nda **yazılı sahip** ister, yoksa derleme **uyarı** verir |
| **Neden kök çözüm** | Bugün katalog kusuru **çalışma zamanında** R1 olarak çıkıyor — yani **kullanıcının karşısında**. Bu kapı onu **derleme zamanına** çeker |
| ⊙ **Kapı ölçütü** | Mevcut katalogda **55 çarpışma → 0**; `ilgili_cubelar` hiçbir soruda **10 aday** döndürmesin |

---

## 14.6 Güncellenmiş sıra — **on bir kök çözüm**

```
KÇ-0  ÇÖZÜMLEME/EŞLEŞTİRME AYRIMI ......... çatı. Kademeli, önce yalnız gözlemci
  │      (KN-1·2·3·4·5·6'nın ortak kökü — ötekiler onun altında ucuzlar)
  │
  ├─ HEMEN, KÇ-0 BEKLEMEDEN (bağımsız, ucuz, yüksek getiri)
  │   ├── KÇ-9   red kayıtlarına bilinmeyen kelime yaz .... ölçüm altyapısı, sıfır risk
  │   ├── KÇ-11  katalog çarpışma kapısı ................. R1'in %62'sinin bir kısmı
  │   └── KÇ-7   yetenek beyanı .......................... "anlamadım" ≠ "yapamıyorum"
  │
  ├─ FAIL-CLOSED ÖNCE (kapsam açmadan)
  │   ├── KÇ-1   niyet–sorgu uyum kapısı ................. 3 sessiz-yanlış sınıfı
  │   └── KÇ-8   beyanlı kısmi cevap ..................... KÇ-1'in kapsam riskini alır
  │
  ├─ SONRA KAPSAM AÇANLAR
  │   ├── KÇ-4   çok-geçiş (finditer) .................... ucuz
  │   ├── KÇ-2   tek biçimbirim kapısı ................... KN-1+KN-2
  │   ├── KÇ-3   sözlük→kural (görev #36) ................ §4'ün 77/112'si
  │   └── KÇ-10  türetme katmanı ......................... §14.2 sınıf A
  │
  └─ MESAJ/KARAR KALİTESİ
      ├── KÇ-5   tek teşhis kaynağı
      └── KÇ-6   belirsizlik → chip  ⚠ önce chip KALİTESİ ölçülsün (§14.2.1)
```

> 🔴 **Değişmeyen tek kural:** *kapsamı açan hiçbir iş, uyum kapısından (KÇ-1) önce
> inmez.* §12.2 bunun bedelini ölçtü.

---

## 14.7 Denetimden sonra hâlâ açık kalanlar

| Açık | Neden kapatılmadı | Kim kapatmalı |
|---|---|---|
| **K5** — değişmez listesi elle yazıldı | Niyet taksonomisi yok *(KÇ-0'ın çıktısı olacak)* | KÇ-0 Faz 1 |
| **K6** — takip yolu, `interpret.py`, `answer.py`, `compose.py` taranmadı | Kapsam kararı; bu rapor **taze soru** yolunu denetledi | ayrı denetim |
| **K7** — uçtan uca ürün davranışı ölçülmedi | Kota (§7) | kota penceresinde |
| **Chip kalitesi** | §14.2.1'de **bulundu**, ölçülmedi | KÇ-6'dan önce |
| **`_norm` kapsamı** | `Mart Cirosu?` → `mart cirosu?` — noktalama **kalıyor**; etkisi ölçülmedi | ayrı prob |

---

## EK A — ölçümlerin yeniden üretimi

Tüm ölçümler **sıfır-LLM, sıfır-DB**, saniyeler sürer. Ürün kodu **değiştirilmedi**.

```bash
cd backend
# 1) Gerçek-dünya korpusu tabanı (§3.1)
docker run --rm -v "$PWD:/app" -w /app dima-test:latest python lab/gercek_dunya.py

# 2) §3.2/§3.3/§4/§5/§8 probları — betikler stdin'den verilir
docker run --rm -i -v "$PWD:/app" -w /app dima-test:latest python - < prob.py
```

`prob.py` iskeleti (bu turda koşulan biçim):

```python
from app import cube_router as cr
from app.config import get_settings
from app.wren_service import WrenService
s = get_settings()
svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                  connection_info=s.connection_dict())
sch = svc.schema()

def dene(q):                       # ürünle AYNI çağrı biçimi: HAM metin
    h = cr.route(q, sch)
    return h, (cr.red_gerekcesi() if h is None else None)

# §4 — fiil/soru kelimesi matrisi
for b in ["randiman", "fire", "ciro", "rework", "oee", "maliyet", "tahsilat"]:
    for e in ["kac", "verdik", "dustu mu", "artti mi", "iyi mi", "var mi", "nedir"]:
        print(b, e, dene(f"{b} {e}")[1])

# §5 — ay çekimi + iki sahip
print(cr._period_hit_words(cr._norm("martta ciro")))   # -> set()
print(cr._covers("mart", "martta"))                    # -> True

# §8 — belirsizlik deterministik olarak biliniyor mu
print([c[0]["name"] for c in cr.measure_cube_candidates(cr._norm("bakiye"), sch)])
```

**Ortam:** `dima-test:latest` imgesi + `backend/` dizini `/app`'e bind-mount.
⚠ Ürün konteyneri (`dima-backend-core`) **kaynak bind-mount taşımaz** — orada ölçüm
alınırsa **imgedeki eski kod** ölçülür.

---

## EK B — kaynak dizini

| Konu | Yer |
|---|---|
| Kapsam kapısı | `backend/app/cube_router.py` → `_coverage_ok:2541` · `_uncovered:2525` · `_covers:2487` · `_is_stop_word:2001` |
| Ay/dönem tanıma | `backend/app/cube_router.py` → `_period_hit_words:2060` · `_cekimli_token:2030` |
| Belirsizlik adayları | `backend/app/cube_router.py:1805` → `measure_cube_candidates` |
| Red kodları | `backend/app/cube_router.py:2919-2928` |
| Cevaplama merdiveni | `backend/app/routers/ask.py:1376-1408` (docstring) · `2473` (route) · `2615` (netleştirme) · `2634` (Intent-JSON) · `3298` (raw_followup düzeltmesi) |
| Bayrak durumları | `backend/demo/packs/features.yml:75-90, 150` |
| Bayrak metadata | `backend/app/features.py:472-500` |
| Bayrak ölçüm kararları | `belgeler/mimari/V1-MIMARI-HARITASI.md:705-740` |
| ADR-0008 | `backend/docs/adr/0008-anlamadığını-bil-tanınmayan-kelime-cevap-yok-ve-öneri-yok.md` |
| Gerçek-dünya korpusu | `backend/lab/gercek_dunya.py` · rapor: `backend/lab/reports/gercek_dunya.md` |
| Netleştirme A/B aleti | `backend/lab/faz0_4_netlestirme.py` |
| **İki eşleştirme rejimi** *(KN-1)* | `cube_router.py` → `_syn_hit:546` · çıplak tarama: `:866` `:1191` `:3026` `:3090` `:3243` |
| **Kıyas mekanizmaları** *(KN-2/§12)* | `cube_router.py` → `_COMPARE_HINTS:1352` · `_DONEM_GERI_*:1382` · `_kiyas_spanlari:1393` · `compare_mode:1412` · `strip_compare:1425` |
| **Tek-geçiş tarama** *(KN-3)* | `cube_router.py:2063-2065` — yedi regex `.search` ile |
| **Sessiz-yanlış koruması** *(KN-4'ün mevcut çekirdeği)* | `cube_router.py:866` · `:1191` |
| **`route()` gövdesi** *(§14.4)* | `cube_router.py:2985-3309` — 325 satır, 50 dallanma, 11 `_reddet` |
| **Katalog sinonimleri** *(KN-9/KN-10)* | cube `synonyms` / `dimension_synonyms` — `WrenService.schema()` çıktısı |
| **Metrik sahipliği** | `app/metrik_kaydi.py` · `_match_cube:807`, metrik kaydı ilk satırı `cube_router.py:823` · ADR-0029 |
| **Red kaydı** *(KÇ-9)* | `app/answer.py:198` → `InteractionLog.reject_reason` *(bilinmeyen kelime kolonu **YOK**)* |

---

*Bu belge bir **denetim raporudur**. Ürün kodu ve test kodu bu tur içinde **değiştirilmemiştir**;
yapılan tek yazma işlemi bu dosyanın kendisidir. Çelişki hâlinde **kod kazanır** — ölçümler
Ek A ile yeniden üretilebilir.*
