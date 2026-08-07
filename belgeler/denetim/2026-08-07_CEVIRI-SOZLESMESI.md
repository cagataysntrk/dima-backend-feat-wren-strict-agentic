# ÇEVİRİ SÖZLEŞMESİ — *"LLM anlıyor; söyleyemiyor"*

> **Soru:** LLM ile sistem diline çeviri neden başarılı değil? Sistem dili mi net değil,
> neyin ne yaptığı mı karışık?
>
> **Kapsam:** araştırma + rapor. Bu belgede **kod değişikliği önerilir, yapılmaz.**
> Her sayı bu depoda yerinde ölçüldü; kaynağı satır numarasıyla yazılı.

---

## 0 · TEK CÜMLELİK CEVAP

Sistem dili **net**. Karışıklık **çevirinin sözleşmesinde**: mutfak on iki şey pişirebiliyor,
garsonun sipariş fişinde **yedi** satır var — ve fişin üstünde *"emin değilsen boş bırak"*
yazıyor.

> **Ölçülen:** `route()` bir `cube_query`'ye **12 anahtar** yazabiliyor
> (`cube_router.py`, tarama). LLM'e sunulan şema **7** alan tanıyor
> (`intent_semasi.py`). Aradaki **5 yetenek mutfakta çalışıyor ve garson onları
> söyleyemiyor.**

Bu, *"sistemde yoksa hata versin"* ilkesinin **ihlalidir**: bugün sistem o beş şeyi
**yapabiliyor**, ama LLM onları ifade edemediği için sonuç *"yapamadım"* diye çıkıyor.

---

## 1 · SİSTEM DİLİ NE KADAR GENİŞ — ölçüm

### 1.1 · Mutfağın anladığı (kabul tarafı)

`parse_cube_query` (`cube_router.py:3800+`) şu alanları **kabul edip taşıyor**:

| alan | ne yapar | şemada var mı |
|---|---|---|
| `cube` | konu | ✅ |
| `measures` | ölçü(ler) | ✅ |
| `dimensions` | kırılım | ✅ |
| `timeDimensions` | zaman kovası (aylık/haftalık) | ✅ |
| `filters` | boyut filtresi | ✅ |
| `compare` | `yoy`/`mom` dönemsel kıyas | ✅ *(yeni)* |
| `blend` | çapraz-cube harman | ✅ *(yeni)* |
| `period_expr` | dönem ifadesi (Python çözer) | ✅ *(yeni)* |
| 🔴 `order` | sıralama (`asc`/`desc`) | **❌** |
| 🔴 `limit` | ilk N satır | **❌** |
| 🔴 `referans` | adlandırılmış dönem kıyası `{eksen, kaynak, hedef}` | **❌** |
| 🔴 `ayrik_aylar` | **ayrık** dönemler (*"ocak ve haziran"* — aradaki aylar HARİÇ) | **❌** |
| 🔴 `provenance_soru` | soru kökeni izi | **❌** *(makbuz işi, model yazmamalı)* |

Ve `route()`'un ayrıca yazdığı, şemada **hiç bulunmayan** ikisi:

| alan | ne yapar |
|---|---|
| 🔴 `measure_having` | **ölçü eşiği** — *"10 milyon üzeri"*, *"100 bin altında"* (SQL `HAVING`) |
| 🔴 `entity_limit` | *"en yüksek **5 makine**"* — varlık sayısı sınırı |

⊙ **Sayım: 12 üretilebilir anahtar · 7 sunulan alan.**

### 1.2 · 🔴 Ve mutfak, garsonun hiç bilmediği yemekleri de yapıyor

Bunlar `cube_query` alanı **değil**, ayrı yollar — LLM'in bir cümleyle tetikleyebileceği
bir yüzeyleri **yok**:

| yetenek | modülü | LLM erişimi |
|---|---|---|
| katkı ayrıştırması (*"neden değişti?"*) | `contribution.py` | ⊘ |
| kök-neden kırılımı (drill) | `drill.py` | ⊘ |
| çapraz-cube KPI | `kpi.py` | ⊘ |
| gelir tablosu / bilanço | `statements.py` | ⊘ |
| hedef kıyası (*"hedefimin altında mıyım"*) | `hedef.py` | ⊘ |
| görünüm seçimi (grafik/tablo/panel) | `viz.py` · `view` | ◐ **yalnız takip yolunda** |

---

## 2 · 🔴 EN ÇARPICI ÖLÇÜM: model, KOLAY işte ZOR işten daha çok yetkili

Aynı model iki prompt görüyor:

| | `select_cube` *(taze soru — **zor** iş)* | `refine_cube` *(mevcut raporu düzenle — **kolay** iş)* |
|---|---|---|
| görevi | ham Türkçeyi sıfırdan çevir | tek bir alanı değiştir |
| verilen alanlar | `cube`·`measures`·`dimensions`·`timeDimensions`·`filters`·`compare`·`blend`·`period_expr` | + **`action`** · **`order`** · **`direction`** · **`limit`** · **`view`** · **`reason`** |
| örnek sayısı *(ölçüldü: `→` sayımı)* | **5** | **21** |
| *"yapamıyorum"* diyebileceği yapılandırılmış yol | yalnız `{"cube":null}` | `action:"unavailable"` **+ `reason`** |

🔴 **Zor işi yapana daha az alan, daha az örnek ve daha kaba bir red kanalı verilmiş.**

Ve fark yalnız alanlarda değil: takip yolunda model *"yapamıyorum, **çünkü**…"* diyebiliyor
(`reason`); taze yolda diyebileceği tek şey `{"cube":null}` — yani **sebepsiz bir hayır**.

> *Bir çeviriciye sözlüğün yarısını verip tam çeviri beklemek, çeviriyi değil sözlüğü
> sınamaktır.*

---

## 3 · SÖZLEŞMENİN KENDİSİ RED'E YANLI

`_cube_select_system` (`llm.py`) — ölçülen metin:

| yönlendirme | kaç kez |
|---|---|
| **reddet** (*"KESİNLİKLE `{"cube":null}` döndür"*, şemanın **ilk** dalı red, araç açıklamasında bir kez daha) | 🔴 **3** |
| **yorumla** (*"günlük Türkçeyi ölçüye çevirmek senin işin"*) | ⊙ 1 *(bu turda eklendi; öncesinde **0**)* |

⊙ **Canlı sonuç (öncesi):** *"verimlilik"* içeren bir soruda **9/9 Intent çağrısı
`{"cube":null}`**. Bu bir **yanlış anlama değil, bir REDDİR.**

🔴 Bugün elimizde *"LLM niyeti yanlış anlıyor"* diye bir ölçüm **yok**. Elimizdeki ölçüm
*"LLM'in konuşmasına izin verilmiyor"*.

### 3.1 · İkinci sınıf: bağlam hiç gitmiyor

`select_cube` çağrısı `(system=katalog, user=ham soru)`'dan ibaret. Gitmeyenler:

* `body.history` — konuşma geçmişi
* önceki `cube_query` — kullanıcının **baktığı rapor**
* `G2`'nin diyalog belleği — *sistemin az önce ne sorduğu*

⚠ Bunlar **tahmin değil olgu**: göndermenin çapa (anchoring) riski yok. Bugün model çok
turlu bir konuşmada **her turda sıfırdan** başlıyor.

### 3.2 · Üçüncü sınıf: katalog eşanlamsız gidiyordu *(bu turda kapatıldı)*

23 cube'un **23'ünde** Türkçe eşanlam beyan edilmiş (`oee` → *verim · randiman ·
performans*), ve LLM'e giden katalogda `verim` **0 kez** geçiyordu. `route()` o katmanı
tam kullanıyordu.

⊙ Ölçülen kazanç dürüst ve **küçük**: 107 içerik kelimesinde eşleşmeyen **94 → 81**.
Kalanların çoğu katalogda **hiç olamaz** (`nasil`·`gidiyor`·`kaybediyoruz`) — bunlar terim
değil **analiz niyeti**.

---

## 4 · 🔴 "NEYİN NE YAPTIĞI KARIŞIK" — evet, ve yeri belli: İKİ NİYET AYRIŞTIRICI

Ölçülen akış: LLM sorguyu üretse bile cevap **`_answer_from_cube_query`**'den geçiyor
(`ask.py:2080`) ve orada `uyum.denetle` çalışıyor (`ask.py:2194`). `uyum` ise niyeti
**`app/niyet.py`'nin deterministik ayrıştırıcısından** okuyor (`uyum.py:212`).

> **Yani sorgunun sahibi LLM, ama *"kullanıcı ne istemişti"* iddiasının sahibi
> deterministik katman.** İkisi aynı cümlede farklı şeyler anlıyorsa, kullanıcı
> **deterministik olanın fikrini** LLM'in cevabına iliştirilmiş görüyor.

### Canlı vaka — kullanıcının kendi örneği

`şubatta ciro ocağa göre nasıl değişti`

| katman | ne anladı |
|---|---|
| deterministik `Niyet` | `tür=**kirilim**+trend` · dönem=1 (yalnız şubat) |
| gerçek niyet | **kıyas** (şubat ↔ ocak) |
| kullanıcının gördüğü | *"Sayı doğru ama eksik: bir **kırılım** istedin ama boyut taşıyamadım"* |

🔴 Kullanıcı kırılım **istemedi**. Sistem ona **söylemediği bir şeyi söylediğini** söyledi.

İki kök neden, ikisi de deterministik tarafta:
1. `gore` bu depoda **üç yönlü aşırı yüklü** (kırılım · granülerlik · dönem aralığı) — ve
   bu tam olarak *"LLM'in anında anladığı"* ayrım.
2. `ocağa` **hiç tanınmıyordu**: `ocak` + ünlüyle başlayan ek → `k`→`ğ` yumuşaması.

⚠ İkisi de bu turda kapatıldı — **ama tedavi semptoma yapıldı.** Asıl soru duruyor:
*deterministik katmanın, LLM'in cevapladığı bir soru hakkında ikinci bir fikir beyan
etmesi doğru mu?*

---

## 5 · SİSTEM DİLİNDE GERÇEKTEN OLMAYANLAR — dürüst sınır

Bunlar için *"hata vermek"* **doğrudur**; eksik olan hatanın **kalitesi**:

| istek | sistemde karşılığı | bugün ne oluyor |
|---|---|---|
| *"işler nasıl gidiyor"* · *"iyi miyiz"* | ⊘ yargı/eşik yok | `{cube:null}` → *"anlayamadım"* |
| *"ne yapmalıyız"* | ⊘ öneri motoru yok | aynı |
| ölçü→ölçü **ilişki/korelasyon** | ⊘ (v2) | *"yan yana koyabilirim, ilişkiyi hesaplayamam"* ✅ |
| adlandırılmış **indirgenemez** kıyas (*"mart ↔ haziran"*) | ◐ `referans` var, derleyicisi yalnız `donem` | etiketli kısmi cevap |
| tahmin / forecast | ⊘ | yetenek sınırı ✅ |

🔴 Ölçülen nüfus: `R11` (*"anlaşıldı ama **ifade edilemez**"*) sınıfı **30/408**. Kod
yazıldı, ölçüldü ve **geri alındı** (gerçek red kodunu örtüyordu) — ama **kullanıcıya
bakan yarısı hiç yapılmadı.** Yani bu sınıf bugün *"anlamadım"* diye çıkıyor, oysa doğru
cümle *"anladım, bunu **söyleyemiyorum**"*.

---

## 6 · YAPILACAKLAR — sıralı, gerekçeli

> Sıra **maliyet/getiri** değil, **bağımlılık** sırasıdır: 0 olmadan hiçbirinin etkisi
> ölçülemez.

### 0 · ÖNCE ALET *(her şeyin ön koşulu)*

| # | iş | neden |
|---|---|---|
| **0.1** | `eval --slice llm` **4 → ~200 vaka**, gerçek sağlayıcıyla | `nl_corpus` tanımı gereği `rule` ile koşar → **LLM yolunu göremez**. Bugün 1–4'ün hiçbirinin kazancı ölçülemez |
| **0.2** | İki redi **ayır**: `cq is None` bugün hem *"model reddetti"* hem *"model uydurdu, beyaz liste düşürdü"* demek | Ayrılmadan **hangi düzeltmenin işe yaradığı bilinemez** |
| **0.3** | 🔴 **Yer gerçeğini gözden geçir** | 42 gerçek vakanın **20'sinde cevap vermek YASAK** (kabul: yalnız *sor* ya da *reddet*). Mimari *"LLM niyeti seçsin"* yönüne giderse korpus her iyileşmeyi **gerileme** raporlar — bu depoda tam bu sınıftan bir olay yaşandı (`gitas` düştü, doğruluk **yükseldi**) |

### 1 · SİPARİŞ FİŞİNİ TAMAMLA — *"sistemde olanı söyleyebilsin"*

| # | iş | kanıt |
|---|---|---|
| **1.1** | `order` + `limit` + `entity_limit` şemaya | mutfak **yapıyor**, garson söyleyemiyor. *"En yüksek 5 makine"* bugün yalnız `route()` çözerse çalışıyor |
| **1.2** | `measure_having` şemaya (*"10 milyon üzeri"*) | aynı — `route()` üretiyor, şemada yok |
| **1.3** | `ayrik_aylar` şemaya (*"ocak ve haziran"*, aradakiler **hariç**) | aynı. ⚠ `blend` ile birlikte **yasak** (fail-closed, `wren_service`) — şema açıklamasında yazılmalı |
| **1.4** | `referans` şemaya *(adlandırılmış dönem kıyası)* | `parse_cube_query` **kabul ediyor**, şema sunmuyor |
| **1.5** | `view` taze yola *(takip yolunda **var**)* | *"grafik olarak göster"* taze soruda ifade edilemiyor |
| **1.6** | 🔴 **`reason` alanı** — model *"yapamıyorum, **çünkü**…"* diyebilsin | Bugün taze yolda tek red kanalı `{"cube":null}`: **sebepsiz bir hayır**. `refine_cube`'de bu alan **zaten var** |

⚠ Hepsinin ortak kuralı: alan şemaya **girecek**, `parse_cube_query` onu **doğrulayacak**.
Beyaz liste gevşetilmez — *"model geçersiz bir ad üretemez"* garantisi korunur.

### 2 · SÖZLEŞMENİN DİLİNİ DENGELE

| # | iş |
|---|---|
| **2.1** | Örnek sayısını taze yolda **5 → ~20**'ye çıkar (takip yolunda **21** var) |
| **2.2** | `{"cube":null}`'ı *"emin değilsen"* değil *"gerçekten yanıtlanamıyorsa"* olarak çerçevele *(bu turda başlandı)* |
| **2.3** | 🔴 **Kısmi anlama yolu aç:** *"cube'u seçebiliyorum ama ölçüden emin değilim"* diyebileceği bir biçim. Bugün ya **tam** bir `CubeQuery` ya **hiç** — arası yok, ve netleştirme tam o aradadır |

### 3 · BAĞLAMI DEVRET *(tahmin değil, olgu)*

| # | iş |
|---|---|
| **3.1** | `body.history` (son N tur) → prompt |
| **3.2** | önceki `cube_query` → prompt *(kullanıcının **baktığı** rapor)* |
| **3.3** | `G2` diyalog durumu → prompt *(**sistemin az önce sorduğu** soru)* |

🔴 **GÖNDERİLMEYECEK:** `route()`'un kısmi **tahmini**. Ölçüldü: tahmin **%74 vakada yok**,
olan 11 vakanın **2'si yanlış** (`ne kadar fire verdik` → sistem `oee` diyor, doğrusu
`parti`). *Bir tahmini paylaşmak, onu doğrulamak değil yaymaktır.*

### 4 · İKİ NİYET AYRIŞTIRICI SORUNUNU KARARA BAĞLA

| # | iş |
|---|---|
| **4.1** | `intent_source == "cube+llm"` iken `uyum`'un beyanı **kimin adına** konuşuyor — karar yazılmalı |
| **4.2** | Seçenek A: LLM cevabında `uyum` **yalnız sorguyu** denetlesin (soruyu değil) |
| **4.3** | Seçenek B: `uyum`'un niyet kaynağı LLM'in kendi beyanı olsun (`reason` alanı → 1.6'ya bağlı) |

⚠ Bugünkü hâl (deterministik niyet + LLM sorgusu) **ölçülmüş bir yanlış beyan** üretti
(§4). Bu bir tercih değil, kapatılması gereken bir **ikinci sahip** (`KAT-1`).

### 5 · SINIRI DÜRÜSTÇE SÖYLE *(`R11`'in kullanıcıya bakan yarısı)*

*"Anlamadım"* ile *"anladım ama söyleyemiyorum"* **ayrı cümleler** olmalı — ölçülen nüfus
**30/408**. Zemin hazır: `yetenek.py` (*"yapamıyorum/yapmıyorum"* ayrımı) + `soz.py`
(tek-ses kataloğu) + `iddia.py` (vaat kapısı) **üçü de duruyor**.

---

## 7 · KULLANICININ TEZİNE KARŞI TEK ÖLÇÜLMÜŞ İTİRAZ

> *"Deterministik burada sadece kafa karıştırıyor olabilir."*

Karıştırdığı yer **gerçek ve ölçülü** (§4). Ama *"kaldıralım"* için ölçüm **yok**:

| | ölçülen |
|---|---|
| `route()` gerçek kullanıcı dilinde (2285 soru) | **cevapladı %3,0** · pes etti %93,3 · 🔴 sessiz-yanlış **%0,53** |
| LLM aynı sorularda | **9/9 `{cube:null}`** |

🔴 Yani deterministik katman **zaten yoldan çekiliyor**; kestiği %3, yanıldığı %0,53.
Onu kaldırmak **çalışan %3'ü** kaldırır ve **bozuk olan yere hiç dokunmaz**.

⚠ Ve bir ayrım kritik: **`route()` (niyet ayrıştırıcı)** kaldırılabilir; **`CubeQuery` IR
(yürütme dili)** kaldırılamaz — ona `/cube` chip yolu (0 LLM), `dashboards`, `schedules`
ve **Query Contract** (*"SQL farklı → tanım değişti"*) bağlı. LLM her gün farklı SQL
üretirse zamanlanmış her rapor **sahte alarm** verir.

> **Doğru sıra:** önce garsonun fişini tamamla (§6/1–2), sonra ölç (§6/0), *sonra*
> `route()`'un niyet rolünü tartış. Bugün *"LLM anlamıyor"* diye bir kanıt yok — çünkü
> LLM'e daha **hiç sorulmadı**.

---

## 8 · ÖZET TABLO

| soru | cevap |
|---|---|
| Sistem dili net mi? | ✅ **Net** — ama **dar**, ve darlığı kullanıcıya söylenmiyordu |
| Model o dili tam kullanabiliyor mu? | 🔴 **Hayır** — 12 yetenek, **7** sunulan alan |
| Model yanlış mı anlıyor? | ⊘ **Bilinmiyor** — ölçülen davranış **red** (9/9), yanlış anlama değil |
| Neyin ne yaptığı karışık mı? | 🔴 **Evet, bir yerde:** sorgunun sahibi LLM, *"ne istendi"* iddiasının sahibi deterministik `Niyet` |
| Bugün ölçebiliyor muyuz? | 🔴 **Hayır** — `eval --slice llm` **4 vaka**; her şeyin ön koşulu bu |

---

*Ölçüm kaynakları: `app/cube_router.py` (anahtar taraması · `parse_cube_query` ·
`_measure_threshold` · `_top_n`) · `app/intent_semasi.py` (şema alanları) · `app/llm.py`
(`_cube_select_system` ↔ `_cube_refine_user`) · `app/uyum.py:212` · `app/routers/ask.py:2080,2194` ·
`lab/reports/gercek_dunya.md` (2285 vaka) · canlı Intent turu (9 çağrı).*
