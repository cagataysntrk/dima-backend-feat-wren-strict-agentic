# TEST ORTAMI RAPORU — *"muazzam ölçüde genişletme"* turunun **durum ölçümü**

> **Kapsam:** gerçek-dünya korpusu (`lab/gercek_dunya.py`) + ERP seed genişlemesi
> (`demo/genisletme.py`) + yeni cube kataloğu.
> **Kesit:** **`HEAD @bf5a7eb`** *(2026-08-05 · 13:46 — ana geliştirici commit'i)*;
> çalışma ağacı temiz.
> **Bu bir denetim değildir.** *"Kurduğumuz test ortamı bugün nerede duruyor, neyi
> ölçebiliyor, neyi ölçemiyor"* sorusuna cevap verir. **Bu rapor kod değiştirmez.**
> **Kardeş belge:** `belgeler/denetim/2026-08-05_TEST-ORTAMI-ARASTIRMA.md` *(literatür taraması)*.

> ⟳ **SÜRÜM NOTU.** Bu raporun ilk hâli `@23b5493` + çalışma ağacı üstünde alınmıştı ve
> **üç kopukluk** ölçmüştü *(üretici çağrılmıyor · `build()` siliyor · cube'lar
> kompozisyonda yok)*. **`@bf5a7eb` üçünü de kapattı** — commit mesajı bunu
> *"bir denetim ajanı yakaladı"* diye kaydediyor. §2 buna göre **yeniden yazıldı**;
> kapanan bulgular **silinmedi**, kapanış kanıtıyla birlikte duruyor. 🔴 **Yeni ve
> açık olan tek şey §1'in başındaki tazelik uyarısıdır.**

---

## 0 · NE ÖLÇÜLDÜ, NE ÖLÇÜLMEDİ — *önce sınır*

| | |
|---|---|
| ✅ **Okundu** | `demo/genisletme.py` (850 satır) · `demo/build_data.py` bağlantı noktası · `lab/gercek_dunya.py` (482) · `tests/test_gercek_dunya_korpusu.py` (229) · `app/compose.py` katman mantığı · `packs/sektor/boyahane/pack.yml` · 10 yeni `metadata.yml` |
| ✅ **Bağımsız sayıldı** | `genisletme.py` **33 tablo** · katalog **23 cube** · şirket modeli **80** *(commit mesajının 33 / 13→23 / 47→80 iddialarıyla **birebir uyuşuyor**)* |
| ✅ **Git'ten doğrulandı** | `boyahane.duckdb` 31 731 712 → **44 576 768 bayt** — genişleme **commit'lendi**, çalışma ağacında asılı kalmadı |
| ❌ **Test koşulmadı** | Ana makinede `duckdb` **yok** (`ModuleNotFoundError`); backend Docker'da koşuyor. Buradaki hiçbir satır *"şu test kırmızı"* demiyor |
| ❌ **DB sorgulanmadı** | **745 sütun · ~460 000 satır · 54 ölçünün 54'ü koşuyor** iddiaları **commit'in kendi ölçümü**; burada **doğrulanmadı**, aktarılıyor |
| ⚠ **`lab/reports/` git'te yok** | `backend/.gitignore:32` — korpus çıktısı **yerel**; başka bir makinede o dosya **bulunmaz**, ölçüm **yeniden koşulmalıdır** |

---

## 1 · ANA BULGU — ölçen alet farkı **görüyor**; gördüğü şey **sıfır**

### 🔴 ÖNCE TAZELİK UYARISI — *bu tablo katalog AÇILMADAN ÖNCE alındı*

| | |
|---|---|
| tablonun koşum zamanı | **12:52** — katalog **13 cube** |
| kataloğun açılma zamanı | **13:46** (`@bf5a7eb`) — katalog **23 cube**, +54 ölçü |
| katalog açıldıktan sonra korpus koşuldu mu | 🔴 **HAYIR** |

> **Aşağıdaki tablo yanlış değil — *bayat*.** Sistemin **13 cube'luk** hâlini ölçüyor.
> `siparis` · `firsat` · `maliyet` · `sikayet` · `butce` · `egitim` · `isg` · `kur` ·
> `sevkiyat` · `bakim_is_emri` cube'ları **o koşumda yoktu**. `ne kadar sattık`,
> `kim bize ne kadar borçlu`, `üçüncü çeyrek gerçekleşme nasıl` gibi vakaların
> karşılığı **artık katalogda var** — ama ölçüm bunu **henüz görmedi**.
> **Bugünkü gerçek sayıyı kimse bilmiyor.**

`lab/reports/gercek_dunya.md` · 42 vaka · 1'i katalog sızıntısıyla elendi → **41 ölçüldü**:

| Kademe | ölçülen | kabul | **doğru** | netleştirme | dürüst ret | 🔴 sessiz-yanlış |
|---|---|---|---|---|---|---|
| K1 düz | 16 | 8 | **0** | **0** | 16 | 0 |
| K2 kırılımlı | 9 | 4 | **0** | **0** | 9 | 0 |
| K3 kıyaslı | 7 | 1 | **0** | **0** | 7 | 0 |
| K4 nedensel | 6 | 3 | **0** | **0** | 6 | 0 |
| K5 kararsal | 3 | 3 | **0** | **0** | 3 | 0 |
| **toplam** | **41** | **19 (%46,3)** | **0** | **0** | **41 (%100)** | **0** |

### %46,3'ün ne olduğu — ve ne OLMADIĞI

41 sonucun **41'i** `durust_ret`. Yani kabul edilen 19 vaka, **kabul listesinde
`durust_ret` yazan** 19 vakadır — başka hiçbir şey değil.

> **Bu oran bir başarı ölçmüyor; *"kaç vakayı reddedilmeyi bekleyerek yazmışız"*
> sayısını ölçüyor.** Kanıtı K5'te: **3/3 = %100** — ve o üç vakanın üçü de
> *"v1'de forecast YOK"* diye **reddedilmeyi bekleyen** vakalardır. En yüksek puan,
> cevaplamamanın **doğru** olduğu kademeden geliyor. K3'te aynı mekanik tersine
> çalışıyor: kabul edilen tek kıyas vakası (`gecen hafta daha mi iyiydi`) yine
> `durust_ret` bekleyen yazım vakası — gerçek kıyas soranların **yedide altısı**
> karşılıksız.

### Kıyas — aynı sistem, iki farklı sözlük

| korpus | sözlük | sonuç |
|---|---|---|
| `nl_corpus` (katalog türevi, ≥%97,1) | **sistemin kendi kelimeleri** | **%93,1** |
| `gercek_dunya` (persona × kademe) | **kullanıcının kelimeleri** | **doğru 0** *(13-cube hâli)* |

Kullanıcının gözlemi — *"bayrakları hep `off` tuttuk, hiç değişiklik olmadı"* — artık
bir sezgi değil, **bir tablo**. ⚠ **Ve araştırma bunun bir istisna olmadığını söylüyor:**
BEAVER kıyas kümesinde aynı modeller Spider/BIRD'de **%81**, gerçek kurumsal ambarda
**%10,8** alıyor *(bkz. araştırma belgesi §1)*. Uçurum **beklenen** desendir.

### ⚠ Bu tablonun dürüst sınırı — başlıkta, dipnotta değil

Ölçülen katman **`route()`** — **sıfır-LLM** yol. `durust_ret` *"deterministik yol pes
etti"* demektir, *"kullanıcı cevapsız kaldı"* **değil**; `/ask` orada durmaz
(Intent-JSON → Discovery). **Ama** ürünün tezi *"LLM garson, küp aşçı"*dır: aşçı 41
siparişin 41'inde mutfaktan çıkmıyorsa, garson doğaçlama yapıyor demektir.

### ✅ Ve bir kazanç — küçültülmemeli

**Sessiz-yanlış: 0/41.** Sistem bilmediğini **uydurmuyor**. Bir GenBI ürününde bu,
doğruluk oranından **önce** gelir: yanlış cevap veren bir sistemin %93'ü, sustuğunu
bilen bir sistemin %0'ından tehlikelidir.

---

## 2 · SEED ve KATALOG — **üç kopukluk ölçüldü, üçü de `@bf5a7eb`'de kapandı**

`demo/genisletme.py` (850 satır) **33 tablo** üretiyor; mevcut 47'nin üstüne, hiçbirini
değiştirmeden. Tasarımı **türetilmiş**: şikâyet sapan partiden, iş emri gerçek arızadan,
maliyet gerçek tüketimden doğuyor — yani kök-neden sorusunun cevabı veride **SQL ile
doğrulanabilir**.

| # | ölçüldüğünde *(`@23b5493` + ağaç)* | 🔧 kapanış *(`@bf5a7eb`)* — **doğrulandı** |
|---|---|---|
| **(a)** | Üretici **hiçbir yerden çağrılmıyor**; docstring'i `build()`'den çağrıldığını **söylüyordu** | `demo/build_data.py:1165` → `from genisletme import genislet` + `build()` sonunda çağrı ✅ |
| **(b)** | `build_data.py:62` `DB.unlink()` → bir sonraki build **33 tabloyu silerdi**; veri yalnız commit'lenmemiş ikili dosyadaydı | `unlink` **duruyor** *(doğrusu da bu)*, ama genişletme artık **ondan sonra** koşuyor; `:1161`'deki yorum kusuru **adıyla** kaydediyor ✅ · DB **commit'lendi** (44,58 MB) ✅ |
| **(c)** | Üç yeni cube **hiçbir kompozisyona girmiyordu**: `moduller: [oee, bakim, ik, enerji]` | `packs/sektor/boyahane/pack.yml:8` → `[oee, bakim, ik, enerji, **butce, satis, maliyet, finans, lojistik**]` ✅ |
| **⚠ ek** | `maliyet` paketi de listede yoktu — *"muhtemelen önceden var, **doğrulanmadı**"* diye işaretlenmişti | **Gerçekmiş ve kapandı** — `maliyet` beşlinin içinde ✅ |

> 🔵 **Bu, denetimin işe yaradığı yerdir ve kayda geçmelidir.** (c) tam olarak
> `DENETIM-RAPORU §8`'in adını koyduğu **«yetim modül»** sınıfının **veri katmanındaki**
> hâliydi: *cube'lar diskte durur, katalogda görünmez.* Commit mesajı bunu kendi
> cümlesiyle yazmış: *"bu satır olmadan cube'lar diskte durur ama katalogda GÖRÜNMEZ …
> bir denetim ajanı yakaladı."*

### Genişlemenin ölçüsü

| | önce | sonra | kaynak |
|---|---|---|---|
| tablo | 47 | **80** | ✅ bağımsız sayıldı *(80 `models/*/metadata.yml`)* |
| sütun | 441 | **745** | commit'in ölçümü — *doğrulanmadı* |
| satır | 318 968 | **~460 000** | commit'in ölçümü — *doğrulanmadı* |
| cube | 13 | **23** | ✅ bağımsız sayıldı |
| yeni ölçü | — | **54** *(54/54 koşuyor, 0 boş sonuç)* | commit'in ölçümü — *doğrulanmadı* |
| DB boyu | 31,73 MB | **44,58 MB** | ✅ git'ten doğrulandı |

### 🔴 KALAN TEK KOPUKLUK — *ölçüm, kendisini büyüten commit'i görmedi*

Katalog 13→23 oldu; **korpus yeniden koşulmadı**. `lab/reports/gercek_dunya.md` hâlâ
12:52 damgalı ve `.gitignore`'da. Yani:

> **Genişlemenin kazancı bugün hiçbir sayıyla ifade edilmiyor.** *Bir genişlemeyi
> ölçmeden almak, onu almamakla aynı bilgiyi bırakır: hiç.*

---

## 3 · KORPUS — 15 → 42, ve kullanıcının iki kuralı **kapıya** çevrildi

Kullanıcı 09:43'te iki şey söyledi: *"15'ten çok daha fazla"* ve *"birbirinin aynısı
kesinlikle olmadan"*. İkisi de **mekanik kapı** olmuş — dikkat sözü değil:

| ölçüm | sonuç |
|---|---|
| vaka sayısı | **42** *(taban 15 → **2,8×**)* |
| persona dağılımı | ceo 8 · saha 8 · cfo 7 · uretim 7 · satis 7 · kalite 5 — **dengeli** |
| kademe dağılımı | K1 17 · K2 9 · K3 7 · K4 6 · **K5 3** |
| kopya kapısı | Jaccard > %70 → **bağımsız koşumla doğrulandı: 0 çift** |
| alt sınır kapısı | `assert len(VAKALAR) >= 40` — *bir daha 15'e düşmek artık **hata*** |
| test | **15 test işlevi** · parametrik koşum **25 → 56** |

### ⚠ Üç çekince

1. **Merdiven tepede inceliyor.** İlk tabanda **sıfır** alan K3/K4 artık 13 vaka taşıyor
   — doğru hamle. Ama **K5 = 3**, ve üçünün de beklentisi `durust_ret`: K5 bugün **%100
   gösteriyor ve hiçbir şey ölçmüyor**.
2. **Kaynak yanlılığı.** 42 vakanın çoğunun `kaynak`'ı `§9.6 …` — yani **korpusu yazan
   akıl ile kataloğu yazan akıl aynı**. Literatürün ölçtüğü **sözlük yanlılığı** birebir
   bu *(araştırma belgesi §2)*: yasak koymak yanlılığı kaldırmıyor, **kaynağını
   değiştiriyor**. Birincil kaynak `deneyim.py` + `REAL_PHRASINGS` + borç defteri olmalı.
3. **Küçük ama sessiz:** `_DURAK` kümesindeki **`"var mı"`** iki kelimelik girdi
   `soru.split()` ile **hiçbir zaman eşleşemez** — ölü satır. Zararsız, ama bir durak
   listesinin okunduğu gibi davranmadığı yer.

---

## 4 · SIRADAKİ İŞİN SIRASI — *`@bf5a7eb` sonrası*

| # | iş | durum · neden bu sırada |
|---|---|---|
| **0** | 🔴 **Korpusu yeniden koş** *(görev listesinde yok)* | **En ucuz, en yüksek getirili adım.** 10 cube ve 54 ölçü açıldı; kazancı ölçen tek şey bu koşum. Sıfır kod, dakikalar |
| **#34** | tabloları kataloğa aç | ✅ **`@bf5a7eb`'de kapandı** — kapatılabilir |
| **#32** | seed'i süreç-zinciriyle büyüt | ✅ **fiilen kapandı** (33 tablo, `build()`'e bağlı) — kapatılabilir |
| **#33** | ekilmiş kök-neden + manifest | 🔨 **Sıradaki gerçek iş.** Yöntem hazır: InsightBench'in **trend enjeksiyonu** — ground truth **ekilen olayın kendisi**. ⚠ eğim 0,1 altındaki trend ölçülemez |
| **#35** | kombinatoryal üreteç | 🟡 **İkiye bölünmeli**: **(a)** metamorfik bozulma üreteci — **altın cevap gerekmez**, bugünkü `doğru = 0` dünyasında bile çalışır · **(b)** desen yeniden-bileşimi — **gerçek desenlerden**. 🔴 SQL2NL paraphrase yolu **kullanılmamalı** |
| **+yeni** | netleştirmenin **içeriği** ölçülsün | Bugün *"netleştirdi mi"* soruyoruz; *"doğru şıkları mı sundu"* sormuyoruz (AmbiQT `BothInTopK`) |
| **+yeni** | vaka başına **alt görev anotasyonu** | Bugün yalnız sınıf var (`durust_ret`), **nerede koptuğu** yok (BEAVER dersi) |

---

## 5 · RİSKLER — *güncellenmiş*

| risk | durum |
|---|---|
| ~~Sessiz geri alma (`build()` siler)~~ | ✅ **kapandı** — `build_data.py:1165` |
| ~~Ölçülmeyen genişleme (cube'lar bağlı değil)~~ | ✅ **kapandı** — `pack.yml:8` |
| 🔴 **Bayat ölçüm** | **AÇIK** — tek ölçüm katalog açılmadan önce alındı; `lab/reports/` ayrıca `.gitignore`'da, yani **başka makinede yok** |
| ⚠ **Payda kayması** | `genisletme.py` *"yalnız ekler"* diye tasarlandı ve `nl_corpus`'un %93,1 tabanı korunmalı — **ama bunu sınayan bir kapı yok** |
| ⚠ **Yetim cube kapısı yok** | (c) elle yakalandı; aynı hata yarın tekrarlansa **hiçbir test kırmızı vermez** |

---

## 6 · HIZ ve KURAL — *"bunlar hızlı olacak mı?"*

### Kısa cevap: **evet, saniyeler** — ve bu bir tahmin değil, **yapısal** bir sonuç

`gercek_dunya.kos()` kendi docstring'inde ne olduğunu söylüyor: **“Sıfır-LLM,
sıfır-DB — `route()` doğrudan.”** Maliyet modeli şu:

| adım | kaç kez | maliyet |
|---|---|---|
| `svc.schema()` | **bir kez** | derlenmiş katalog yüklemesi |
| `cube_router.route(soru, schema)` | **vaka başına** | saf bellek-içi eşleme — **LLM yok, SQL yok, konteyner yok** |

**Kıyas ölçülü:** `nl_corpus` **444 vaka** için `--tam` = **1 dk 50 sn**, ve bu **16
süreçle** *(seri hâli 13 dk 18 sn idi)*. `gercek_dunya` **42 vaka**, tek şirket, yalnız
`route()` → o bütçenin **küçük bir kesri**.

⚠ Katalog **13 → 23 cube** büyüdü; vaka başına maliyet katalog boyuyla kabaca
**doğrusal** artar (~1,8×). Taban milisaniye olduğu için sonuç **hâlâ saniyeler**.

### 🔴 Ama üç şey bu hızı bitirir — ve **ikisi planda var**

| ne | neden pahalı | sınıf değişimi |
|---|---|---|
| **#33** ground-truth doğrulaması | *"doğru sebep veride **SQL ile doğrulanabilir**"* demek, **sorgu koşmak** demektir | **sıfır-DB → DB koşan** *(seed artık ~460 000 satır · 44,58 MB)* |
| **#35** kombinatoryal üreteç | vaka sayısını **çarpar** | `route()` hızında 10 000 vaka sorun değil; **execute** hızında sorundur |
| **LLM yolu** (Intent-JSON → Discovery) | *"cevap doğru mu"* sorusunu **ancak bu** ölçer | kullanıcının kendi kısıtı: **10 istek / 10 sn** → 42 vaka = **dakikalar + kota** |

### Yani ikilem doğru kurulmuş: **iki ayrı alet, iki ayrı amaç**

| alet | sorduğu soru | maliyet | ritim |
|---|---|---|---|
| **Toplu** — `route()` korpusu | *"erişim var mı"* | **saniyeler** | **her demette**, ucuz |
| **Tek tek / canlı** — LLM + execute | *"cevap doğru mu"* | dakikalar + kota | **örneklemli**, gecelik/haftalık |

> *Hızlı alet ürünün doğruluğunu ölçemez; doğru ölçen alet her demette koşturulamaz.*
> **İkisi birbirinin yerine geçmez** — biri kapı, öteki teşhistir.

### 🔴 ASIL BULGU — mesele hız değil: **bu korpus bugün KURALSIZ**

Kullanıcının *"kafasına göre test etmemeli"* endişesi **yerinde ve ölçüldü**:

| # | ölçüm | sonuç |
|---|---|---|
| 1 | `grep -rn "gercek_dunya" lab/kapi.py CLAUDE.md .github/` | 🔴 **BOŞ** — hiçbir kapı koşmuyor. `--tam`'ın *"korpus"* adımı yalnız `lab/nl_corpus.py --kapi` |
| 2 | Araç **tasarımı gereği kırmızı vermez** *(kural 6: "taban, hedef değil")* | Tasarım **doğru** — ama kapıya bağlanmayınca sonuç: **hiç koşmayan** ölçüm |
| 3 | `lab/nl_corpus_baseline.json` ✅ · `lab/konusma_senaryolari_baseline.json` ✅ · **`gercek_dunya_baseline.json`** | 🔴 **YOK** → **gerileme görülemez** |
| 4 | 56 testin tamamı | 🔴 **YAPISAL** — `read_text()` ile kaynağı okuyup `assert "cube_router.route(" in src` diyor. Korpusun **şeklini** koruyorlar, ürünün **davranışını** değil |
| 5 | `lab/reports/` | `.gitignore:32` → CI'da koşsa bile **çıktı kaybolur** |

> 🔴 **(4) hızın gerçek açıklamasıdır:** testler hızlı, çünkü **ürünü hiç
> çalıştırmıyorlar**. 56 yeşil, `route()`'un tek bir kez bile koşduğunu göstermez.

### 🔵 Önerilen kural — üç satır

1. **`gercek_dunya.py --kapi`** bayrağı + `--tam`'a **ikinci korpus adımı** *(saniyeler;
   `nl_corpus` paydasına dokunmaz)*.
   ⚠ **`konusma_senaryolari` tuzağı burada tekrarlanmasın:** bayraksız koşumda `main()`
   her yolda `0` döndüğü için o adım *"dörtte biri sessizce **dekordu**"*
   (`lab/kapi.py` kendi yorumunda kayıtlı).
2. **`gercek_dunya_baseline.json`** — **eşik değil, gerileme** kapısı: *kabul sayısı
   düşerse kırmızı*. Kural 6'yı bozmaz; *"yüzde hedefi"* koymaz, **düşüşü** yakalar.
3. **LLM'li canlı tur asla yerel kapıda olmasın** — örneklemli ve gecelik. Yerel kapı
   **5 dakikayı** aşmamalı *(kullanıcı kararı, `CLAUDE.md`'de ölçülü)*.

---

## 7 · KAPANIŞ — bir cümlede

Sabahki rapor *"alet hazır, malzeme hazır, **tesisat yok**"* diyordu. **`@bf5a7eb`
tesisatı kurdu:** 33 tablo `build()`'e, 10 cube kataloğa bağlandı — ve kopukluğu bulan
şey bir denetim turuydu.

**Geriye tek şey kaldı, ve o da ölçmenin kendisi:**

> **Tesisat kuruldu, ama sayaç hâlâ dünkü değeri gösteriyor.**
> Elimizdeki tek tablo **13 cube'luk** dünyanın tablosu; bugün **23** cube var ve
> kimse yeniden bakmadı. *Bir genişlemenin kazancı, ölçülene kadar bir iddiadır.*
