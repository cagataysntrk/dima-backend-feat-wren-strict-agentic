# LLM YOLU — teşhis ve **geri dönülebilir deney planı**

> **Tarih:** 2026-08-07 · **Tür:** denetim (yazıldığı anın fotoğrafı, değiştirilmez)
> **Soru:** *"Sistem %100 eminse deterministik, biraz bile şüpheliyse LLM"* kuruldu mu?
> **Cevap:** Hayır — ama sebebi sanıldığı yerde değil.

---

## 0 · ⚠ BU RAPORUN KENDİ ÖLÇÜM SINIRI — önce bu okunmalı

Aşağıdaki sayıların bir kısmı `lab/nl_corpus.py` ve `lab/gercek_dunya.py`'den geliyor.
🔴 **O araçların ikisi de `rule` sağlayıcıyla koşar — içlerinde gerçek LLM YOKTUR.**
`nl_corpus.py`'nin kendi başlığı: *"LLM yok (rule provider): deterministik çekirdeğin
tavanı ölçülür."*

Yani bu korpuslar **`route()`'u ölçer, ürünü değil.** Kullanıcı canlıda *"çalışmıyor"*
dediğinde, o korpuslar **o şeyi göremez**. Bu raporda korpus sayıları yalnız
`route()` hakkında kanıt sayılmıştır; LLM yolu hakkında **kanıt sayılmamıştır**.

> *Bir aletin ölçmediği şeyi, o aletin sayısıyla savunmak, ölçümü bir kalkan olarak
> kullanmaktır.*

---

## 1 · Yaygın iki inanış — ikisi de ÖLÇÜMLE ÇÜRÜDÜ

### ⊘ *"Deterministik katman kesiyor, o yüzden LLM'e ulaşılmıyor"*

42 elle toplanmış **gerçek kullanıcı sorusu** (`lab/gercek_dunya.py::VAKALAR`):

| basamak | vaka | oran |
|---|---|---|
| `route()` çözdü (LLM'e gitmez) | **0** | **%0** |
| kesildi: cube beraberliği → netleştirme | 0 | %0 |
| kesildi: yetenek sınırı | 1 | %2,4 |
| **LLM'e gidiyor** | **41** | **%97,6** |

Geniş korpusta (2285 gerçek-dünya vakası) aynı yön:

| | vaka | oran |
|---|---|---|
| `route()` **cevapladı** | 69 | **%3,0** |
| `route()` **pes etti** → LLM basamağına devretti | 2132 | **%93,3** |
| sessiz-yanlış | 12 | %0,53 |

🔴 **Deterministik katman gerçek dilde niyeti anlamıyor — ve kesmiyor da.** %93'ü
devrediyor. Darboğaz devirden **sonra**.

⚠ Yardımcı olgular, aynı yönde: `netlestirme_onceligi` bugün **`off`** (yani
netleştirme LLM'i öncelemiyor), `raw_followup` tuzağı **düzeltilmiş**
(`ask.py:3605`), yetenek kapısı `route()` **ve** Intent-JSON'dan **sonra** duruyor
(`ask.py:3654`) — yani yalnız Discovery'yi kesebiliyor.

### ⊘ *"LLM yanlış anlıyor"*

Canlı denetimde ölçülen şey **yanlış anlama değil**: *"verimlilik"* sorusunda **9/9
Intent çağrısı `{"cube":null}`** döndü. Model anlamaya çalışıp yanılmadı — **reddetti**.

> Bugün elimizde *"LLM yanlış anlıyor"* diye bir kanıt **yok**; elimizdeki kanıt
> *"LLM'in konuşmasına izin verilmiyor"*.

---

## 2 · LLM çağrısı ANINDA ne gidiyor, ne gitmiyor

`ask.py:2923` → `_select_consistent(llm, body.question, catalog_text, …)`
→ `llm.select_cube(system, question)`

Modelin gördüğü **tam olarak iki şey**:

| | içerik |
|---|---|
| `system` | katalog metni + 8 kural |
| `user` | **ham kullanıcı sorusu** *(normalize bile edilmemiş — burada kayıp YOK)* |

**Gitmeyenler** (hiçbiri, hiçbir koşulda):

* konuşma geçmişi (`body.history`)
* önceki `cube_query`
* diyalog durumu (`G2`'nin belleği — sistemin az önce ne sorduğu)
* sistemin o soruda **kendi çözdüğü** her şey

Son maddenin somut hâli:

```
"vardiyasi bazinda randiman kotu mu"
  sistem BİLİYOR : cube=oee · ölçü=ort_oee ("randiman" eşleşti)
                   tanınmayan=['kotu'] · niyet=kırılım
  LLM'e GİDEN    : ham soru + 23 cube'luk katalog dökümü
```

---

## 3 · 🔴 Ve o bilgi **gönderilMEMELİ** — çünkü çapa riski ÖLÇÜLDÜ

Bu raporun ilk taslağında *"sistemin anladığını da gönder"* önerisi vardı.
**Ölçüldü ve kısmen yanlış çıktı.** 42 vakada, `route()` pes ettiğinde:

| | vaka | oran |
|---|---|---|
| kısmi tahmin **hiç yok** | 31 | **%74** |
| tahmin var, yer gerçeği cube demiyor | 9 | %21 |
| 🔴 tahmin var, **YANLIŞ cube** | 2 | **%5** *(tahmin taşıyanların %18'i)* |

Somut: `"ne kadar fire verdik"` → sistem `oee.toplam_fire_kg` diyor, doğrusu `parti`.
Bunu modele *"ben şunu anladım"* diye vermek, onu **ölçülmüş bir hataya çapalamak**tı.

**Ayrım nettir:**

| bilgi | gönderilmeli mi | neden |
|---|---|---|
| ham soru | ✅ zaten gidiyor | — |
| katalog + eşanlamlar | ✅ **evet** | ipucu değil, **hedef dilin sözlüğü** |
| 🔴 `route()`'un tahmini | ❌ **hayır** | %18 yanlış · %74 vakada zaten yok |
| geçmiş · önceki `cube_query` · diyalog durumu | 🔴 **evet, ama bugün HİÇ gitmiyor** | tahmin değil **olgu**, çapa riski yok |

---

## 4 · LLM mantığında eksik olan BEŞ ŞEY

### 4.1 · İFADE BOŞLUĞU — dönem söylenemiyor *(en ağır)*

`refine_cube` prompt'unda `period_expr` alanı var:
*"dönem ifadesini AYNEN kopyala — hesabı sistem yapar."*
`select_cube`'de **yok** — ne prompt'ta, ne şemada (`intent_semasi` alanları:
`dimensions · timeDimensions · compare · blend · filters`). Üstüne prompt *"TARİH
filtresi ASLA yazma"* diyor.

🔴 Yani taze bir soruda dönemi `route()` çözemediyse, model onu **hiçbir yere
yazamaz**. Tutarlı tek davranışı ya dönemi sessizce düşürmek ya `{"cube":null}`.
**Takip yolunda çözülmüş problem, taze yolda çözülmemiş.**

### 4.2 · Kaçış kapısı tek yönlü

> *"Soru tek bir cube ile yanıtlanamıyorsa (liste, çapraz-cube, **karmaşık**, tanımsız)
> **KESİNLİKLE** `{"cube":null}` döndür."*

`karmaşık` sınırsız bir kelime ve **karşı ağırlığı yok**. Prompt'ta *"günlük Türkçeyi
ölçüye çevirmek senin işin"* diyen tek satır yok; şemada red **ilk** dal. Model üç kez
reddetmeye davet ediliyor, bir kez bile yorumlamaya değil.

### 4.3 · Yorumlayan prompt'ta sıfır örnek

`refine_cube`'de **4 örnek** var (*"aylara göre"→timeDimensions*, *"sadece
erkek"→filters*…). `select_cube`'de **0**. Dar düzenleme yapana örnek verilmiş, doğal
dili yorumlayana verilmemiş.

### 4.4 · Oylamanın paydası yanlış — güven sinyali ŞİŞİK

`_select_consistent`: `cands = [c for c in ... if c]` → `agreement = len(best)/len(cands)`.
`{"cube":null}` oyları **paydadan düşüyor**.

> 3 çağrının 1'i cevap, 2'si *"bilmiyorum"* ise → **agreement = 1,0**

Modül kendini *"KALİBRE güven sinyali"* diye tanımlıyor; **değil**. Ve hata yönü tam
tersine: **en şüpheli durum en emin görünüyor.**

### 4.5 · İki farklı red aynı koda düşüyor

`cq is None` iki şeyi birden anlatıyor: model **reddetti** (`cube:null`) ve model
**uydurdu** (beyaz liste düşürdü). Aynı log satırı, aynı akış. Hangisinin kaç kez
olduğu bilinmiyor → **4.1–4.4'ten hangisini düzeltmenin işe yaradığı ölçülemez.**

---

## 5 · Katalog sözlüğü ne kadarını çözdü — ölçüldü

42 sorunun 107 içerik kelimesi üzerinde:

| | katalogda bulunmayan |
|---|---|
| sözlüksüz | 94 (%87,9) |
| **sözlüklü** *(`katalog_sozlugu: beta`)* | **81 (%75,7)** |

Kazanç **13 kelime** — gerçek ama küçük. Kalanlar **iki ayrı sınıf**:

| sınıf | örnek | çözümü |
|---|---|---|
| **analiz niyeti** — katalogda hiç olamaz | `nasil` · `gidiyor` · `miyiz` · `kaybediyoruz` · `yapmaliyiz` · `yavasladi` | 🔴 **LLM'in işi** — §4.1–4.3 |
| **çekimli katalog terimi** | `vardiyasi` · `ceyrek` · `ucuncu` · `yilbasindan` · `bugune` | `app/ek.py` ek **üretiyor**, **sökmüyor** |

---

## 6 · 🔴 ÖLÇÜM KORPUSU, ÖNERİLEN MİMARİNİN TERSİNİ KODLUYOR

42 vakanın kabul ölçütleri:

| kabul | kaç vaka |
|---|---|
| `netlestirme` (sor) | 38 |
| `durust_ret` (reddet) | 19 |
| `dogru` (cevap ver) | 22 |
| 🔴 **yalnız sor/reddet — cevap vermek YASAK** | **20 / 42** |

Birebir korpustan:

```
"işler nasıl gidiyor"        → kabul = [netlestirme, durust_ret]
                               yasak = "rastgele bir ölçü seçip kendinden emin sayı vermek"
"bu ay iyi miyiz kötü müyüz" → yasak = "iyi/kötü yargısını bir eşik uydurarak vermek"
```

🔴 *"LLM niyeti seçsin"* mimarisine geçilirse, bugünkü yer gerçeği **42 vakanın 20'sini
başarısız sayar** — LLM yanıldığı için değil, **kabul ölçütü başka bir mimariye göre
yazıldığı için.**

⚠ Bu depoda tam bu sınıftan bir olay yaşandı: `gitas` korpustan düştü, payda 445→342
indi ve **doğruluk yükseldi**. *Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden
çıkmasıyla da olur.*

**Sonuç:** mimari değişmeden **önce** kabul ölçütleri elden geçirilmeli — yoksa her
iyileşme gerileme, her gerileme iyileşme diye okunur.

---

## 7 · GERİ DÖNÜLEBİLİR DENEY — *"promptu çeviren LLM tek eleman olsun"*

### 7.0 · 🔴 ÖNCE BİR AYRIM — bu rapor onu bir kez bulandırdı

**İki ayrı LLM rolü var ve karıştırılmaları bu deneyin sonucunu okunamaz kılar:**

| | **LLM #1 — ÇEVİRMEN** | **Discovery — HAM SQL** |
|---|---|---|
| çağrı | `llm.select_cube(soru, katalog, şema)` | `llm.generate_sql(...)` |
| ürettiği | **CubeQuery** (sistem dili) | **ham SQL** |
| sayıyı kim hesaplar | 🔴 **küp** | LLM'in yazdığı SQL |
| doğrulama | `parse_cube_query` beyaz listesi | `dry_plan` |
| `source` | `cube+llm` | `llm:anthropic` · `llm:gemini` … |
| küp katmanı | **kullanılır** | **atlanır** |

🔴 **Test edilmek istenen şey LLM #1'dir**: promptu **sistem diline çevirip küpleri
çalıştıran** basamak. Discovery onun yedeği değil, **bambaşka bir cevap sınıfıdır** — ve
deney sırasında **açık kalırsa**, LLM #1'in her başarısızlığını gizler ve sonuç
okunamaz hâle gelir.

> *Bir basamağı ölçmek istiyorsan, altındaki basamağı kapatmalısın; yoksa ölçtüğün şey
> ikisinin toplamıdır.*

### 7.1 · ⚠ Yarısı BUGÜN VAR — kod değişikliği istemiyor

`AskRequest.yol_siniri` üç seviye tanıyor:

| değer | `route()` | **Intent-JSON (LLM #1)** | Discovery |
|---|---|---|---|
| `"deterministik"` | ✅ | ❌ | ❌ |
| **`"llm"`** | ✅ | ✅ | 🔴 **KAPALI** |
| `null` / `"kesif"` *(varsayılan)* | ✅ | ✅ | ✅ |

🔴 **`yol_siniri: "llm"` zaten *"Discovery yok, ham SQL yok"* demek.** Yedek kapalı,
sayıyı küp koyuyor. Yani deneyin *"fallback olmasın"* şartı **bugün karşılanabiliyor.**

**Bugün, sıfır kod ile yapılabilecek test:**

```
POST /ask  {"question": "<soru>", "yol_siniri": "llm", "execute": true}
```

`route()` gerçek-dünya dilinde vakaların **%93,3'ünde zaten pes ediyor** (§1) — yani o
sorularda `route()` bir engel değil, **kendiliğinden devre dışı**. Bu istekle:

* soru LLM #1'e düşer,
* cevabı **küp** hesaplar,
* LLM #1 çözemezse **Discovery kurtarmaz** → sınır beyanı döner.

⚠ Yani *"promptu çeviren LLM tek eleman"* senaryosunun **canlı ölçümü bugün mümkün** ve
bir dağıtım gerektirmiyor. **Deneyin ilk turu bu olmalı** — çünkü kod değiştirmeden
alınan bir ölçüm, geri alınacak hiçbir şey bırakmaz.

### 7.2 · Eksik olan tek şey — `route()`'un ATLANMASI

Kalan boşluk dar: `route()` **çözebildiği** sorularda (gerçek-dünya dilinde %3,0) hâlâ
önce koşuyor ve LLM #1'e sıra gelmiyor. Tam deney bunu da kapatmak ister.

**Yeni dördüncü değer:** `yol_siniri: "yalniz_intent"`

| | davranış |
|---|---|
| `route()` | 🔴 **atlanır** *(hiç çağrılmaz)* |
| Intent-JSON (LLM #1) | ✅ **tek çalışan basamak** |
| Discovery | ❌ kapalı *(`"llm"` ile aynı kural)* |
| `POST /cube`, chip, refine, pano | **dokunulmaz** — 0-LLM yürütme yolu |

Değişiklik iki parçadan ibaret:

1. `_yol_izinli`: `("deterministik", "llm")` listesine `"yalniz_intent"` eklenir ve
   `intent` için `True`, `discovery` için `False` döner — **mevcut `"llm"` dalının
   aynısı**, ikinci bir kural yazılmaz.
2. `ask()` içinde **tek** bir yerel sarmalayıcı: `yalniz_intent` ise `route()` yerine
   `None`.

⚠ **Tek sahip kuralı:** `ask.py`'de `cube_router.route()` **8 yerde** çağrılıyor;
taze-soru yolunda olan **dördü** (`2734` ana · `2754` yazım-düzeltmeli · `2780`
kıyas-sökülmüş · `3490` `_try_fresh_intent`). Dördü ayrı ayrı sarılmaz, **tek**
sarmalayıcıya bağlanır — aksi hâlde bir gün üçü sarılır, biri unutulur ve *"deney
kapalı"* sanılan kod deterministik cevap vermeye devam eder.

Kalan dört çağrı **taze yol değil** (bağlam çapası `1646` · önceki soru `3261` · `2474`
· `281`) ve deneyde **dokunulmaz** — konuşma bağlamını bozmamak için.

### 7.3 · Deneyin DIŞINDA kalanlar — bilerek

| dokunulmaz | neden |
|---|---|
| `POST /cube` (chip · refine · pano · zamanlama) | 0-LLM **yürütme** yolu; kullanıcı bir chip'e tıkladığında LLM çağırmak deneyin konusu değil |
| takip turu (`refine_cube`) | zaten LLM #1 ailesinden; ve `period_expr`'i **olan** tek yol |
| `narration_guard` · `iddia.py` · beyaz liste | 🔴 **doğruluk vetosu** — deney **niyet seçimini** değiştirir, **sayı güvencesini değil** |

### 7.4 · Deney sırasında ne KAYDEDİLMELİ

*"Olmadı"* kararı da *"oldu"* kararı da bir sayıya dayanmalı; yoksa ikinci denemede aynı
tartışma sıfırdan başlar. Her turda:

1. 🔴 `{"cube":null}` **mı**, beyaz liste reddi **mi** — §4.5: bugün **ayrılmıyor**.
   ⚠ **Deneyin ön koşuludur**: ayrılmadan *"LLM anlamadı"* ile *"LLM uydurdu"*
   birbirine karışır ve deneyin cevabı okunamaz.
2. `agreement` **ve** `k` — kaç çağrının kaçı cevap verdi (§4.4'ün şişik paydası).
3. LLM #1'in seçtiği `cube.measure` ↔ kullanıcının kastettiği.
4. Gecikme ve token. Bugün `consistency_k=3` → soru başına **üç** çağrı; deney için
   `k=1` düşünülmeli, yoksa üç kat maliyetle tek bir soru ölçülür.

### 7.5 · GERİ ALMA

| ne yapıldı | nasıl geri alınır |
|---|---|
| **7.1 — istek alanı** (`yol_siniri: "llm"`) | **göndermeyi bırak.** Kod hiç değişmedi → geri alınacak bir şey yok |
| **7.2 — `"yalniz_intent"`** | alanı göndermeyi bırak; kod yerinde kalır ve davranış **bayt bayt bugünkü** (`KURAL B`) |
| deney tamamen iptal | tek commit `revert` — bir yerel sarmalayıcı + `_yol_izinli`'de bir dize |

### 7.6 · ⚠ ÖNCEDEN BİLİNEN SONUÇLAR — *"gerileme"* SANILMASIN

1. 🔴 **Korpus kapıları kırmızıya döner.** `nl_corpus` ve `gercek_dunya` `route()`'u
   ölçer; `route()` atlanınca doğru-cube **çöker**. Bu bir gerileme **değil**, *ölçülen
   şeyin kapatılmasıdır*. Deney sırasında o kapılar **kanıt sayılmaz** (ve §0).
2. **Query Contract** (`contracts.py`) soru → SQL → sonuç hash'i mühürlüyor. Niyeti LLM
   #1 seçerse aynı soru farklı günlerde farklı CubeQuery → farklı SQL üretebilir ve
   *"TANIM DEĞİŞTİ"* teşhisi **yanlış alarm** verir.
3. **Maliyet ve gecikme:** deterministik yol ~100–800 ms ve **0 token**; LLM #1 canlıda
   **2,8–5,5 sn** ve `k=3`. Deneyde her soru bu bedeli öder.
4. **`%3`'lük deterministik cevap kaybolur** — küçük ama sıfır değil, ve o %3 çoğunlukla
   kullanıcının sistemin sözlüğünü öğrendikten sonra sorduğu sorulardır.
5. ⚠ **Sayı güvencesi DEĞİŞMEZ:** LLM #1 yalnız *hangi cube/ölçü/boyut* seçer; sayıyı
   yine küp hesaplar ve `parse_cube_query` katalog dışı hiçbir adı geçirmez. Deney
   *"LLM sayı uydurur mu"* sorusunu **açmaz**.

## 8 · SIRA

| # | iş | neden bu sırada |
|---|---|---|
| **1** | §4.5 — `cube:null` ile beyaz-liste reddini **ayır** | ⚠ **ön koşul**: ayrılmadan hiçbir iyileştirmenin işe yarayıp yaramadığı görülemez |
| **2** | §7 deneyi — `yalniz_llm`, manuel | asıl soruyu **canlı** yanıtlar; korpuslar yanıtlayamaz |
| **3** | §4.1 — `period_expr`'i taze yola taşı | tasarım **zaten var** (`refine_cube`), kopyalanacak |
| **4** | §4.2 · §4.3 — prompt çerçevesi + örnekler | en ucuzu, yalnız metin |
| **5** | §4.4 — oy paydası | güven sinyali bugün ters yönde yanıltıyor |
| **6** | §6 — kabul ölçütlerini gözden geçir | mimari kararı **kalıcı** olursa zorunlu |

🔴 **Ve hepsinin üstündeki engel:** `eval --slice llm` **4 vaka**, korpuslar sağlayıcıdan
kör. Bu altı maddenin hiçbirinin kazancı **bugünkü aletlerle ölçülemez**.
1–5'i uygulamak kolay; **doğru olduğunu göstermek bugün imkânsız.**

> *Ölçemediğimiz bir şeyi geliştiremeyiz — ve bu fazın tamamı, tam olarak bunun bir kez
> daha olmasını engellemek için dizilmişti.*
