# ÇEVİRİ SÖZLEŞMESİ — *"LLM anlıyor; SÖYLEYEMİYOR"*

> **Sorular:** (1) LLM ile sistem diline çeviri neden başarılı değil — sistem dili mi net
> değil, neyin ne yaptığı mı karışık? (2) Kesin olanda deterministik, şüphede LLM — bu
> nasıl birleşir?
>
> **Kapsam:** araştırma + rapor. Bu belgede **kod değişikliği önerilir, yapılmaz.**
> Her sayı bu depoda yerinde ölçüldü; kaynağı satır numarasıyla yazılı.

---

## 0 · ÜÇ CÜMLELİK CEVAP

1. **Sistem dili net.** Karışıklık çevirinin **sözleşmesinde**: mutfak on iki şey
   pişirebiliyor, garsonun sipariş fişinde **yedi** satır var.
2. **İstenen merdiven zaten kurulu** (`VQR → route() → LLM → Discovery`) — eksik olan
   mimari değil, `route()`'un *"eminim"* kararının **kalibrasyonu**.
3. Ve bir yerde *neyin ne yaptığı* **gerçekten karışık**: sorgunun sahibi LLM, ama
   *"kullanıcı ne istedi"* iddiasının sahibi **deterministik** katman.

---

## 1 · MERDİVEN GERÇEĞİ — *"her şey LLM'e mi gidiyor?"*

### 1.1 · Sıra deterministik-önce, ve bu doğrulandı

`ask.py:2895` birebir:

```python
if route_hit is None and "ask_intent_first" in resolve_for(settings, principal):
```

🔴 **LLM ancak `route()` PES EDERSE çağrılıyor** (`route()` `:2734`). Bayrağın adı
yanıltıcı (*"intent first"*), davranışı değil. Ve LLM devreye girse bile **sayıyı küp
koyuyor**: model JSON'u `parse_cube_query`'nin katı beyaz listesinden geçiyor, sonra
`cube_sql` derliyor. **Model hiçbir koşulda sayıya dokunmuyor.**

Tam merdiven:

| # | basamak | LLM | ne zaman |
|---|---|---|---|
| 1 | **VQR** — doğrulanmış soru deposu (`ask.py:2509-2558`) | **0** | soru daha önce `/verify` ile onaylandıysa |
| 2 | **`route()`** — deterministik eşleştirme | **0** | katalog eşleşmesi kırılırsa |
| 3 | **Intent-JSON** — *garson* | ✅ | `route()` pes ederse |
| 4 | **Discovery** — ham SQL | ✅ | Intent de pes ederse |

⚠ VQR bile *"eşleşti, gönder"* demiyor: dönerken `parse_cube_query` **ve**
`_period_gate`'ten geçiyor — bayat bir eşleşme sessizce sunulmuyor.

### 1.2 · Chip'ler — ölçüldü, LLM'e gitmiyorlar

| chip türü | uç | LLM |
|---|---|---|
| **refine** (kırılım · dönem · kıyas · granülerlik) | `POST /cube` | **0 — her zaman** |
| **açılış** (starter) | `POST /ask` *(metin taşır)* | `route()` çözerse **0** |

⊙ **Açılış chip'leri ölçümü: 10 chip · 9'unu `route()` çözüyor → %90 deterministik.**

🔴 Düşen tek chip: `duruş nedenlerine göre toplam süre bu ay` → **`R10`**. İronik ve
öğretici: bu liste `starters.yml`'in kendi şerhinde *"BİLEREK önceden test edilmiş/kanıtlı
ifadeler"* diye tanımlı — yani **kanıtlanmış bir ifade bayatlamış**. Muhtemel sebep `göre`
belirsizliği (§5.1).

> *Gözlemin doğru ama sebebi başka: chip'ler LLM'e gitmiyor; **serbest yazdığın metinler**
> gidiyor — çünkü `route()` gerçek dilde zaten konuşmuyor (§2).*

---

## 2 · 🔴 BİRİNCİ BOŞLUK: `route()`'un *"EMİNİM"*İ KALİBRE DEĞİL

Senin şartın: *"%100 kesinse, dilsel olarak anlamı bariz ise, LLM'e gitmeden küp
çalışsın."* Bu şartın bugünkü karşılığı ölçüldü — **2285 gerçek kullanıcı sorusu**:

| kademe | toplam | **konuştu** | doğru | 🔴 sessiz-yanlış | ⚠ beyanlı kısmi | **etiketsiz** | 🔴 **hata** |
|---|---|---|---|---|---|---|---|
| K1 *(kolay)* | 386 | 43 | 30 | 1 | 12 | 31 | **%3,2** |
| K2 | 549 | 63 | 21 | **9** | 33 | 30 | 🔴 **%30,0** |
| K3 | 537 | 37 | 11 | 2 | 24 | 13 | **%15,4** |
| K4 | 543 | **0** | 0 | 0 | 0 | 0 | — |
| K5 | 270 | 10 | 7 | 0 | 3 | 7 | %0,0 |
| **TOPLAM** | **2285** | **153** | **69** | **12** | **72** | **81** | 🔴 **%14,8** |

Üç oran, üç farklı soruya cevap veriyor:

| soru | oran |
|---|---|
| `route()` gerçek dilde ne sıklıkla konuşuyor? | **%6,7** (153/2285) |
| Konuştuğunda ne sıklıkla sessizce yanılıyor? | **%7,8** (12/153) |
| 🔴 **Etiketsiz** konuştuğunda — yani *"eminim"* dediğinde? | 🔴 **%14,8** (12/81) |

> 🔴 **Senin şartın bugün karşılanmıyor.** `route()` çekincesiz cevap verdiğinde **her 7
> sorudan 1'inde** yanılıyor — ve yanıldığında `◆ CUBE` rozetiyle, yüksek güvenle
> yanılıyor. K2 kademesinde bu oran **%30**.

### 2.1 · Sebep: `route()`'un DERECE kavramı yok

İçeride **çok sinyalli bir marjin sistemi var** — ölçü-sinonim uzunluğu (`:908`) ·
alt-dize spesifikliği (`:932`) · boyut kanıtı (`:937`) · 4-harf cube marjini (`:947`) ·
`value_index` `AUTO_MARGIN=0.08`. Kıramazsa `None` dönüyor.

🔴 **Ama çıktısı ikili: bir `cube_query` ya da `None`.** *"Kıl payı kazandım"* ile
*"tartışmasız kazandım"* **aynı kapıdan** çıkıyor.

Senin istediğin ayrım tam burada duruyor ve **hesap zaten yapılıyor, sadece atılıyor**:

| bugün | istenen |
|---|---|
| eşleşti → **cevapla** | **tartışmasız** eşleşti → cevapla (0 LLM, anında) |
| — | **kıl payı** eşleşti → **LLM'e sor** *(bugün yanlış cevaplıyor: 12 vaka)* |
| eşleşmedi → LLM | eşleşmedi → LLM |

⚠ **Karşı maliyet ölçülmeli:** eşiği yükseltmek 12 sessiz-yanlışı kapatırken doğru
cevapların bir kısmını da LLM'e yollar (yavaşlar). Bu takas bugün **ölçülemiyor** (§8).

---

## 3 · 🔴 İKİNCİ BOŞLUK: GARSONUN FİŞİ EKSİK

### 3.1 · Mutfak 12 şey pişiriyor, fişte 7 satır var

`route()`'un bir `cube_query`'ye yazabildiği **tüm** anahtarlar (kaynak taraması) ile
Intent-JSON şemasının modele **sunduğu** alanlar:

| alan | ne yapar | mutfak | **şema** |
|---|---|---|---|
| `cube` | konu | ✅ | ✅ |
| `measures` | ölçü(ler) | ✅ | ✅ |
| `dimensions` | kırılım | ✅ | ✅ |
| `timeDimensions` | zaman kovası (aylık/haftalık) | ✅ | ✅ |
| `filters` | boyut filtresi | ✅ | ✅ |
| `compare` | `yoy`/`mom` dönemsel kıyas | ✅ | ✅ *(yeni)* |
| `blend` | çapraz-cube harman | ✅ | ✅ *(yeni)* |
| `period_expr` | dönem ifadesi *(Python çözer)* | ✅ | ✅ *(yeni)* |
| 🔴 `order` | sıralama (`asc`/`desc`) | ✅ | **❌** |
| 🔴 `limit` | ilk N satır | ✅ | **❌** |
| 🔴 `entity_limit` | *"en yüksek **5 makine**"* | ✅ | **❌** |
| 🔴 `measure_having` | **ölçü eşiği** — *"10 milyon üzeri"* (SQL `HAVING`) | ✅ | **❌** |
| 🔴 `ayrik_aylar` | **ayrık** dönemler — *"ocak **ve** haziran"*, aradakiler HARİÇ | ✅ | **❌** |
| 🔴 `referans` | adlandırılmış dönem kıyası `{eksen, kaynak, hedef}` | ✅ | **❌** |

⊙ **12 üretilebilir anahtar · 7 sunulan alan.**

🔴 Bu, *"sistemde yoksa hata versin"* ilkesinin **ihlalidir**: sistem o altı şeyi
**yapabiliyor**, ama LLM onları ifade edemediği için sonuç *"yapamadım"* diye çıkıyor.
*Bir yeteneği söyleyememek, ona sahip olmamakla aynı sonucu verir.*

### 3.2 · Ve mutfak, garsonun hiç bilmediği yemekleri de yapıyor

Bunlar `cube_query` alanı değil — ayrı yollar, LLM'in tetikleyebileceği bir yüzeyleri
**yok**:

| yetenek | modülü | LLM erişimi |
|---|---|---|
| katkı ayrıştırması (*"neden değişti?"*) | `contribution.py` | ⊘ |
| kök-neden kırılımı (drill) | `drill.py` | ⊘ |
| çapraz-cube KPI | `kpi.py` | ⊘ |
| gelir tablosu / bilanço | `statements.py` | ⊘ |
| hedef kıyası (*"hedefimin altında mıyım"*) | `hedef.py` | ⊘ |
| görünüm seçimi (grafik/tablo/panel) | `viz.py` · `view` | ◐ **yalnız takip yolunda** |

---

## 4 · 🔴 ÜÇÜNCÜ BOŞLUK: SÖZLEŞME RED'E YANLI

### 4.1 · Model, KOLAY işte ZOR işten daha yetkili

Aynı model iki prompt görüyor:

| | `select_cube` — **taze soru** *(zor iş)* | `refine_cube` — **rapor düzenle** *(kolay iş)* |
|---|---|---|
| görevi | ham Türkçeyi sıfırdan çevir | tek bir alanı değiştir |
| verilen alanlar | 8 çekirdek alan | + **`action`** · **`order`** · **`direction`** · **`limit`** · **`view`** · **`reason`** |
| örnek sayısı *(`→` sayımı)* | **5** | **21** |
| *"yapamıyorum"* kanalı | `{"cube":null}` — **sebepsiz bir hayır** | `action:"unavailable"` **+ `reason`** |

🔴 **Zor işi yapana daha az alan, daha az örnek, daha kaba bir red kanalı verilmiş.**

### 4.2 · Metin üç kez *"reddet"*, bir kez *"yorumla"* diyor

| yönlendirme | kaç kez |
|---|---|
| **reddet** — metinde *"KESİNLİKLE `{"cube":null}`"* · şemanın **ilk** dalı red · araç açıklamasında bir kez daha | 🔴 **3** |
| **yorumla** — *"günlük Türkçeyi ölçüye çevirmek senin işin"* | 1 *(bu turda eklendi; öncesinde **0**)* |

⊙ **Canlı sonuç (öncesi):** *"verimlilik"* içeren bir soruda **9/9 Intent çağrısı
`{"cube":null}`**.

> 🔴 Bu bir **yanlış anlama değil, bir REDDİR.** Bugün elimizde *"LLM niyeti yanlış
> anlıyor"* diye bir ölçüm **yok**; elimizdeki ölçüm *"LLM'in konuşmasına izin
> verilmiyor"*.

### 4.3 · Bağlam hiç gitmiyor

`select_cube` çağrısı `(system=katalog, user=ham soru)`'dan ibaret. Gitmeyenler:

* `body.history` — konuşma geçmişi
* önceki `cube_query` — kullanıcının **baktığı** rapor
* `G2` diyalog belleği — *sistemin az önce sorduğu soru*

⚠ Bunlar **tahmin değil olgu**; göndermenin çapa (anchoring) riski yok. Bugün model çok
turlu bir konuşmada **her turda sıfırdan** başlıyor.

### 4.4 · Katalog eşanlamsız gidiyordu *(bu turda kapatıldı)*

23 cube'un **23'ünde** Türkçe eşanlam beyan edilmiş (`oee` → *verim · randiman ·
performans*); LLM'e giden katalogda `verim` **0 kez** geçiyordu. `route()` o katmanı tam
kullanıyordu.

⊙ Kazanç dürüst ve **küçük**: 107 içerik kelimesinde eşleşmeyen **94 → 81**. Kalanların
çoğu katalogda **hiç olamaz** (`nasil` · `gidiyor` · `kaybediyoruz`) — bunlar terim değil
**analiz niyeti** (§6).

---

## 5 · 🔴 DÖRDÜNCÜ BOŞLUK: İKİ NİYET AYRIŞTIRICI *(karışıklığın yeri)*

LLM sorguyu üretse bile cevap **`_answer_from_cube_query`**'den geçiyor (`ask.py:2080`) ve
orada `uyum.denetle` çalışıyor (`ask.py:2194`). `uyum` ise niyeti **`app/niyet.py`'nin
deterministik ayrıştırıcısından** okuyor (`uyum.py:212`).

> 🔴 **Sorgunun sahibi LLM, ama *"kullanıcı ne istemişti"* iddiasının sahibi deterministik
> katman.** İkisi aynı cümlede farklı şey anlarsa, kullanıcı **deterministik olanın
> fikrini** LLM'in cevabına iliştirilmiş görüyor.

### 5.1 · Canlı vaka — kullanıcının kendi örneği

`şubatta ciro ocağa göre nasıl değişti`

| katman | ne anladı |
|---|---|
| deterministik `Niyet` | `tür=**kirilim**+trend` · dönem=**1** (yalnız şubat) |
| gerçek niyet | **kıyas** (şubat ↔ ocak) |
| kullanıcının gördüğü | *"Sayı doğru ama eksik: bir **kırılım** istedin ama boyut taşıyamadım"* |

🔴 Kullanıcı kırılım **istemedi.** Sistem ona **söylemediği bir şeyi söylediğini** söyledi.

İki kök neden, ikisi de deterministik tarafta:

1. **`gore` üç yönlü aşırı yüklü** (kırılım · granülerlik · dönem aralığı) — ve bu tam
   olarak *LLM'in anında anladığı* ayrım.
2. **`ocağa` hiç tanınmıyordu**: `ocak` + ünlüyle başlayan ek → `k`→`ğ` yumuşaması.
   `app/ek.py` (G7) ek **üretiyor** ama **sökmüyor**.

⚠ İkisi de bu turda kapatıldı — **ama tedavi semptoma yapıldı.** Asıl soru duruyor:
*deterministik katmanın, LLM'in cevapladığı bir soru hakkında ikinci bir fikir beyan
etmesi doğru mu?*

---

## 6 · SİSTEM DİLİNDE GERÇEKTEN OLMAYANLAR — dürüst sınır

Bunlar için hata vermek **doğrudur**; eksik olan hatanın **kalitesi**:

| istek | karşılığı | bugün ne oluyor |
|---|---|---|
| *"işler nasıl gidiyor"* · *"iyi miyiz"* | ⊘ yargı/eşik yok | `{cube:null}` → *"anlayamadım"* |
| *"ne yapmalıyız"* | ⊘ öneri motoru yok | aynı |
| ölçü→ölçü **ilişki/korelasyon** | ⊘ (v2) | *"yan yana koyabilirim, ilişkiyi hesaplayamam"* ✅ |
| adlandırılmış **indirgenemez** kıyas (*"mart ↔ haziran"*) | ◐ `referans` var, derleyicisi yalnız `donem` | etiketli kısmi cevap |
| tahmin / forecast | ⊘ | yetenek sınırı ✅ |

🔴 Ölçülen nüfus: `R11` (*"anlaşıldı ama **ifade edilemez**"*) sınıfı **30/408**. Kod
yazıldı, ölçüldü ve **geri alındı** (gerçek red kodunu örtüyordu) — ama **kullanıcıya
bakan yarısı hiç yapılmadı.** Bu sınıf bugün *"anlamadım"* diye çıkıyor; doğru cümle
*"anladım, bunu **söyleyemiyorum**"*.

⚠ Ayrıca ölçüm sırasında **27 katalog sızıntısı** kaydedildi (`bakiye` · `kar` ·
`dogalgaz` · `sapma`) — vaka korpusa girmedi. Bu terimler kataloğun kendi kapsam
boşluğudur, çevirinin değil.

---

## 7 · YAPILACAKLAR — **bağımlılık** sırasına göre

> Sıra maliyet/getiri değil, **bağımlılık** sırasıdır: 0 olmadan hiçbirinin etkisi
> ölçülemez.

### 0 · ÖNCE ALET *(her şeyin ön koşulu)*

| # | iş | neden |
|---|---|---|
| **0.1** | `eval --slice llm` **4 → ~200 vaka**, gerçek sağlayıcıyla | `nl_corpus` tanımı gereği `rule` ile koşar → **LLM yolunu göremez** |
| **0.2** | İki redi **ayır** | `cq is None` bugün hem *"model reddetti"* hem *"model uydurdu, beyaz liste düşürdü"* demek → **hangi düzeltmenin işe yaradığı bilinemez** |
| **0.3** | 🔴 **Yer gerçeğini gözden geçir** | 42 gerçek vakanın **20'sinde cevap vermek YASAK** (kabul: yalnız *sor* ya da *reddet*). Mimari LLM'e kayarsa korpus her iyileşmeyi **gerileme** raporlar — bu depoda tam bu sınıftan bir olay yaşandı (`gitas` düştü, doğruluk **yükseldi**) |

### 1 · MARJİNİ DIŞARI VER *(senin "%100 kesin" şartın)*

| # | iş | kanıt |
|---|---|---|
| **1.1** | `route()` bir **marjin/güven** de döndürsün — hesap zaten yapılıyor, atılıyor | etiketsiz cevapların **%14,8'i yanlış**; K2'de **%30** |
| **1.2** | Eşiğin **altında** kalan eşleşme cevap değil **LLM'e devir** olsun | 12 sessiz-yanlışın kapanma yolu |
| **1.3** | Eşiği **ölç**, seçme — kapsam↓ / doğruluk↑ takası sayıyla kararlaştırılsın | 0.1'e bağlı |

⚠ Bu, mimariyi değiştirmez: merdiven aynı kalır, yalnız 2. basamağın *"eminim"* eşiği
görünür ve ayarlanabilir olur.

### 2 · SİPARİŞ FİŞİNİ TAMAMLA — *"sistemde olanı söyleyebilsin"*

| # | iş |
|---|---|
| **2.1** | `order` + `limit` + `entity_limit` şemaya *(mutfak yapıyor, garson söyleyemiyor)* |
| **2.2** | `measure_having` şemaya *(“10 milyon üzeri”)* |
| **2.3** | `ayrik_aylar` şemaya. ⚠ `blend` ile birlikte **yasak** (fail-closed) — açıklamada yazılmalı |
| **2.4** | `referans` şemaya *(`parse_cube_query` kabul ediyor, şema sunmuyor)* |
| **2.5** | `view` taze yola *(takip yolunda **var**)* |
| **2.6** | 🔴 **`reason`** — model *"yapamıyorum, **çünkü**…"* diyebilsin *(takip yolunda **var**)* |

⚠ Ortak kural: alan şemaya **girer**, `parse_cube_query` onu **doğrular**. Beyaz liste
gevşetilmez — *"model geçersiz bir ad üretemez"* garantisi korunur.

### 3 · SÖZLEŞMENİN DİLİNİ DENGELE

| # | iş |
|---|---|
| **3.1** | Örnek sayısı taze yolda **5 → ~20** *(takip yolunda 21 var)* |
| **3.2** | `{"cube":null}` = *"gerçekten yanıtlanamıyorsa"*, *"emin değilsen"* değil *(başlandı)* |
| **3.3** | 🔴 **Kısmi anlama yolu:** *"cube'u seçebiliyorum, ölçüden emin değilim"*. Bugün ya **tam** bir `CubeQuery` ya **hiç** — ve netleştirme tam o aradadır |

### 4 · BAĞLAMI DEVRET *(tahmin değil, olgu)*

`body.history` · önceki `cube_query` · `G2` diyalog durumu → prompt.

🔴 **GÖNDERİLMEYECEK:** `route()`'un kısmi **tahmini**. Ölçüldü: tahmin **%74 vakada
yok**, olan 11 vakanın **2'si yanlış** (`ne kadar fire verdik` → sistem `oee` diyor,
doğrusu `parti`). *Bir tahmini paylaşmak, onu doğrulamak değil yaymaktır.*

### 5 · İKİ AYRIŞTIRICI KARARINI VER

| seçenek | ne demek |
|---|---|
| **A** | LLM cevabında `uyum` **yalnız sorguyu** denetlesin, soruyu değil |
| **B** | `uyum`'un niyet kaynağı LLM'in kendi beyanı olsun *(`reason` → 2.6'ya bağlı)* |

⚠ Bugünkü hâl **ölçülmüş bir yanlış beyan** üretti (§5.1). Bu bir tercih değil,
kapatılması gereken bir **ikinci sahip** (`KAT-1`).

### 6 · SINIRI DÜRÜSTÇE SÖYLE

*"Anlamadım"* ile *"anladım ama söyleyemiyorum"* ayrı cümleler olmalı — nüfus **30/408**.
Zemin hazır: `yetenek.py` + `soz.py` + `iddia.py` üçü de duruyor.

### 7 · VQR'ı BESLE *(bedava hız)*

Doğrulanmış soru deposu **zaten merdivenin ilk basamağı** ve **0 LLM**. Eksik olan
mekanizma değil, **dolması** — ve `/verify` geri bildiriminden besleniyor. Her onaylanan
cevap, o sorunun bir daha asla LLM'e gitmemesi demek.

---

## 8 · ÖLÇÜM ENGELİ — bu belgede ÜÇÜNCÜ kez

`§2`'nin eşiği, `§7/2`'nin alanları ve `§7/3`'ün prompt'u — **hiçbirinin kazancı bugünkü
aletlerle ölçülemez**:

| alet | ölçtüğü | LLM yolunu görür mü |
|---|---|---|
| `lab/nl_corpus.py` | `route()` tavanı, **`rule`** sağlayıcıyla | ❌ tanımı gereği kör |
| `lab/gercek_dunya.py` | `route()`, tek turlu | ❌ aynı sebep |
| `eval --slice llm` | uçtan uca, **gerçek sağlayıcı** | ◐ **4 vaka** |

> *Bir düzeltmeyi ölçemeden uygulamak, kusurun yerini değiştirmenin pahalı bir biçimidir.*

---

## 9 · KULLANICININ TEZİNE KARŞI TEK ÖLÇÜLMÜŞ İTİRAZ

> *"Deterministik burada sadece kafa karıştırıyor olabilir."*

Karıştırdığı yer **gerçek ve ölçülü** (§5). Ama *"kaldıralım"* için ölçüm **yok**:

| | ölçülen |
|---|---|
| `route()` gerçek dilde | konuşuyor **%6,7** · sessiz-yanlış **%0,53** *(korpus geneli)* |
| LLM aynı sorularda | **9/9 `{cube:null}`** |

🔴 Deterministik katman **zaten yoldan çekiliyor**. Onu kaldırmak çalışan %6,7'yi
kaldırır ve **bozuk olan yere hiç dokunmaz**.

⚠ Ve bir ayrım kritik:

| | kaldırılabilir mi | neden |
|---|---|---|
| **`route()`** — niyet ayrıştırıcı | ✅ evet *(maliyeti %6,7)* | bir hızlandırıcıdır |
| **`CubeQuery` IR** — yürütme dili | 🔴 **hayır** | `/cube` chip yolu (0 LLM) · `dashboards` · `schedules` · **Query Contract** ona bağlı. LLM her gün farklı SQL üretirse zamanlanmış her rapor **sahte "tanım değişti" alarmı** verir |

> **Doğru sıra:** önce aleti kur (§7/0), sonra marjini dışarı ver (§7/1) ve fişi tamamla
> (§7/2), *sonra* `route()`'un niyet rolünü tartış. Bugün *"LLM anlamıyor"* diye bir kanıt
> yok — çünkü LLM'e daha **hiç sorulmadı**.

---

## 10 · ÖZET

| soru | cevap |
|---|---|
| Sistem dili net mi? | ✅ **Net** — ama **dar**, ve darlığı kullanıcıya söylenmiyordu |
| Model o dili tam kullanabiliyor mu? | 🔴 **Hayır** — **12** yetenek, **7** sunulan alan |
| Model yanlış mı anlıyor? | ⊘ **Bilinmiyor** — ölçülen davranış **red** (9/9), yanlış anlama değil |
| *"Kesinse deterministik, şüphede LLM"* kurulu mu? | ✅ **Kurulu** (`VQR → route → LLM → Discovery`) |
| Peki `route()` gerçekten *"kesin"* mi? | 🔴 **Hayır** — etiketsiz cevaplarının **%14,8'i yanlış**; K2'de **%30** |
| Chip'ler LLM'e mi gidiyor? | ❌ **Hayır** — refine %100 `/cube`; açılış **9/10** deterministik |
| Neyin ne yaptığı karışık mı? | 🔴 **Evet, bir yerde:** sorgunun sahibi LLM, *"ne istendi"* iddiasının sahibi deterministik `Niyet` |
| Bugün ölçebiliyor muyuz? | 🔴 **Hayır** — `eval --slice llm` **4 vaka**; her şeyin ön koşulu bu |

---

## 11 · 🔴 CANLI ŞİKÂYETİN İZİ — *"makine bazında oee son 3 ay bile LLM'e gidiyor"*

### 11.1 · Lab'da bu soru LLM'e GİTMİYOR — ölçüldü

| soru | `route()` sonucu | teshis | ihlal |
|---|---|---|---|
| `makine bazında oee son 3 ay` | ✅ `cube=oee` · `ort_oee` · `dimensions=[makine]` · `tarih ≥ 2026-05-07` | `None` | `[]` |
| `makine bazinda oee son 3 ay` *(şapkasız)* | ✅ aynı | `None` | `[]` |
| `makine bazında oee` | ✅ aynı *(dönemsiz)* | `None` | `[]` |
| `son 3 ay oee` | ✅ `cube=oee` · `ort_oee` | `None` | `[]` |

🔴 **`route()` bu soruyu tam çözüyor.** Ve merdivenin sırası kaynaktan çıkarıldı — **NLP
önce**:

```
ask() gövdesi (1490–3862), karar noktaları sırayla:
  2527  🟢 VQR                    ← 0 LLM
  2734  🟢 route()                ← NLP intent      ◀ BURADA ÇÖZÜLÜYOR
  2801  🟡 cube_tie chip          ← 0 LLM, ama KESER
  2840  🔴 prompt_enhance         ← LLM
  2953  🔴 select_cube (Intent)   ← LLM
  ...
  3434  🟢 deterministic_refine   ← NLP takip
  3460  🟢 cross_cube_add         ← NLP
  3545  🔴 refine_cube            ← LLM
  3859  🔴 Discovery              ← LLM
```

`ask.py:2895` koşulu birebir: `if route_hit is None and "ask_intent_first" in …` —
**LLM ancak `route()` pes ederse.**

### 11.2 · O hâlde canlıda LLM'e gidiyorsa sebep DİLSEL DEĞİL

Kalan üç aday — ve ayırt edici kanıtları:

| # | hipotez | nasıl ayırt edilir |
|---|---|---|
| **A** | 🔴 **Soru bir THREAD içinde gönderiliyor.** O zaman istek `cube_query`/`history` taşır ve **takip dalına** girer (`:3434`). `deterministic_refine` **dar düzenleme** için yazılmıştır (*"aylara göre"*, *"temmuzu çıkar"*); **tam yeni bir soru** ona uymaz → `refine_cube`'e (**LLM**, `:3545`) düşer | İstek gövdesinde `cube_query` var mı? Boş bir thread'de aynı soru 0 LLM mi? |
| **B** | Farklı tenant kataloğu — `oee`/`makine` o şirkette eşleşmiyor | `source` ve `trace` hangi cube diyor? |
| **C** | LLM çağrısı **başka** bir soruya ait *(`consistency_k=3` → tek soruda 3 çağrı)* | Log'daki soru metni ile chip metni aynı mı? |

🔴 **En güçlü aday A** ve o gerçek bir tasarım boşluğu: **bir thread'in içinde, tamamen
deterministik bir soru bile LLM'e düşebiliyor** — çünkü takip dalı *"bu bir düzenleme mi"*
diye soruyor, *"bu kendi başına çözülebilir mi"* diye sormuyor.

> *Bir sorunun kendi başına çözülebilir olması, bağlam içinde sorulduğunda unutuluyor.*

**Öneri (7.1'in kardeşi):** takip dalında `deterministic_refine` başarısız olduğunda,
`refine_cube`'e (LLM) düşmeden **önce** soruyu **taze** `route()`'a bir kez daha sor.
Maliyeti sıfır (0 LLM, ~1 ms), kazancı: thread içindeki her deterministik soru anında
döner. ⚠ Sıra önemli — taze `route()` **düzenleme** niyetini ezmemeli: yalnız
`deterministic_refine` **ve** `cross_cube_add` ikisi de pes ettiyse denenir.

### 11.3 · Ve kullanıcının kuralı, sayıyla

> *"Aşçı tam duyarsa sorun yok; azıcık bile şüpheye düşerse hemen garson yollamalıdır."*

Bugün aşçı şüphesini **dışarı vermiyor** (§2.1): çıktısı ikili. Ölçülen sonuç —
**etiketsiz cevaplarının %14,8'i yanlış** (K2'de %30). Yani aşçı bugün *"tam duymadığı"*
12 vakada da yemeği çıkarıyor.

**Kuralın kodu tam olarak §7/1'dir:** `route()` marjini döndürsün, eşiğin altı garsona
gitsin. Hesap zaten yapılıyor — sadece atılıyor.

---

## 12 · MANUEL DOĞRULAMA SETİ — 10 THREAD *(kolaydan zora)*

> ⚠ **Bu bölüm ÇALIŞTIRILMADI ve neden çalıştırılmadığı yazılı:** canlı örneğe
> (`:8001`) giriş **reddedildi** — `owner@dima.local`, üç lab hesabı ve tenant hesabı
> (`demo-boyahane@usedima.com`) denendi, hepsi `401`. Aşağıdaki set **elle koşulmak
> üzere** hazır; her turun beklenen basamağı deterministik katmanın **ölçülmüş**
> davranışından yazıldı.

**Koşum biçimi** *(fronttan yazıyor gibi — pytest YOK)*:

```bash
TOK=$(curl -s -X POST localhost:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"<kullanıcı>","password":"<parola>"}' | jq -r .access_token)

# T1 — açılış (thread YOK: cube_query gönderme)
curl -s -X POST localhost:8001/ask -H "Authorization: Bearer $TOK" \
  -H 'Content-Type: application/json' \
  -d '{"question":"<soru>","execute":true,"session_id":"m1"}' \
  | jq '{source, note, eksik_niyet, cube_query, trace, explain}'

# T2 — takip (T1'in cube_query'sini AYNEN yankıla — frontend böyle yapıyor)
curl -s -X POST localhost:8001/ask -H "Authorization: Bearer $TOK" \
  -H 'Content-Type: application/json' \
  -d '{"question":"<takip>","execute":true,"session_id":"m1",
       "cube_query":<T1.cube_query>,"history":["<soru>"]}' \
  | jq '{source, note, eksik_niyet, cube_query, trace}'
```

🔴 **Her turda bakılacak dört şey:** `source` *(`cube` = 0 LLM · `cube+llm` = garson
devrede · `vqr` = önbellek)* · `note` *(beyan var mı)* · `eksik_niyet` *(sistem neyi
yapamadığını söylüyor mu)* · `trace` *(hangi basamak)*.

| # | T1 — açılış | T2 — takip | beklenen T1 | neyi sınar |
|---|---|---|---|---|
| **1** | `makine bazında oee son 3 ay` | `aylara göre` | 🟢 `cube` *(ölçüldü)* | **§11.2/A**: T1 0 LLM iken T2 de 0 LLM mi? Takip dalı deterministik kalıyor mu |
| **2** | `bu ay toplam üretim` | `hat bazında` | 🟢 `cube` | En basit hat — chip'lerin de yolu |
| **3** | `son 3 ay fire` | `bir de ciro ekle` | 🟢 `cube` | `cross_cube_add` (0 LLM) çalışıyor mu — **çapraz-cube harman** |
| **4** | `duruş nedenlerine göre toplam süre bu ay` | `en yüksek 5` | 🔴 `cube+llm` *(ölçüldü: `R10`)* | **Kendi açılış chip'imiz bayatlamış.** T2: `entity_limit` şemada YOK (§3.1) |
| **5** | `şubatta ciro ocağa göre nasıl değişti` | `peki mart nasıldı` | 🟡 kıyas, **beyanlı** | `göre` ayrımı + ay çekimi (§5.1). Yanlış *"kırılım istedin"* beyanı **gitti mi** |
| **6** | `yılbaşından bugüne hasılat` | `çeyreklere böl` | 🟢 `cube` *(YTD onarıldı)* | Onarılan **sessiz-yanlış**: eskiden `gte bugün` (ileriye) bakıyordu |
| **7** | `10 milyon üzeri ciro yapan müşteriler` | `sırala en yüksekten` | 🟡 `route` çözerse `cube` | 🔴 `measure_having` + `order` **şemada yok** — `route()` pes ederse LLM **ifade edemez** |
| **8** | `ocak ve haziran cirosunu karşılaştır` | `neden bu kadar fark var` | 🟡 **indirgenemez kıyas** → etiketli | `ayrik_aylar` şemada yok · T2 `contribution` LLM'e kapalı (§3.2) |
| **9** | `personel verimliliklerini kıyasla` | `o zaman sadece üretim bölümü` | 🔴 sınır beyanı | *"Verimlilik = OEE"* biliniyor ama `personel` yok → **doğru** sınır mı, yoksa *"anlamadım"* mı |
| **10** | `işler nasıl gidiyor bu ay` | `iyi mi kötü mü` | 🔴 `{cube:null}` → *"anlamadım"* | **§6'nın kalbi**: sistemde karşılığı **yok**. Doğru cevap *"anladım, söyleyemiyorum"* — bugün *"anlamadım"* diyor |

⊙ **Beklenen dağılım:** 1·2·3·6 → **0 LLM** · 5·7·8 → **beyanlı/kısmi** · 4·9·10 → **LLM
ya da sınır**. Gerçekleşen dağılım bundan **saparsa**, sapan satır §11.2'nin A/B/C
hipotezlerinden hangisinin doğru olduğunu söyler.

⚠ Thread 1 **kritik**: T1'de `source=cube` ama T2'de `cube+llm` çıkarsa **hipotez A
doğrulanmış** olur ve §11.2'nin önerisi (takip dalında taze `route()` denemesi) doğrudan
uygulanabilir.


---

## 13 · 🔴🔴 CANLI KOŞUM — TEŞHİS DEĞİŞTİ: LLM **INTENT'TE DEĞİL, ANLATIDA**

> Canlı örneğe (`:8001`, tenant `boyahane`) **gerçek HTTP** ile iki tur atıldı ve
> konteyner logları satır satır izlendi. Aşağıdaki her sayı o koşumdan.

### 13.1 · Tur 1 — `makine bazında oee son 3 ay` *(taze, thread YOK)*

```
13:42:52  BAĞLAM  kural=taze:capa-yok  cube=None  eksen=()
13:42:52  İSTEK   q='makine bazında oee son 3 ay'  followup=False
13:42:54  yayilim: perdeleme: 2 metin · 5 yer tutucu     ← ANLATI maskeleme
13:42:57  dima.llm: openrouter BAŞARILI (deepseek-v4-flash, 2936ms)   ← 🔴 LLM
13:42:58  CEVAP   source=cube  satır=11  süre=5420ms
```

| ölçüt | değer |
|---|---|
| `source` | **`cube`** |
| `explain.path` | *"cube (`route()` — **LLM'siz, sıfır maliyet**)"* · güven **1.0** |
| `trace` | *"Intent-path: `cube_router.route()` (LLM'siz)"* · *"niyet: tür=kirilim · kırılım=makine,donem"* |
| LLM çağrısı | **1** — ve **intent'ten SONRA**, `yayilim.perdele`'nin hemen ardından |

🔴 **Intent için LLM ÇAĞRILMADI.** Tek LLM çağrısı **anlatıcı** (T2) — ve toplam sürenin
**%54'ü** (2936/5420 ms).

### 13.2 · Tur 2 — `aylara göre` *(aynı thread, `cube_query` yankılanmış)*

```
13:43:18  BAĞLAM  kural=yapisal:cube_query  cube=oee  eksen=('makine',)
13:43:18  İSTEK   q='aylara göre'  followup=True(yapısal=True)
13:43:19  yayilim: perdeleme: 1 metin · 1 yer tutucu     ← ANLATI maskeleme
13:43:41  dima.llm: openrouter BAŞARILI (deepseek-v4-flash, 22564ms)  ← 🔴🔴 LLM
13:43:42  CEVAP   source=cube  satır=22  süre=24285ms
```

| ölçüt | değer |
|---|---|
| `source` | **`cube`** |
| `trace` | *"refine → **deterministik** düzenleme"* — `deterministic_refine`, 0 LLM |
| cevabın kendisi | ~**1 saniye** (istek → 22 satır) |
| 🔴 anlatıcı LLM | **22 564 ms** — toplam sürenin **%93'ü** |

### 13.3 · 🔴 SONUÇ — hipotez A ÇÜRÜDÜ, gerçek sebep başka

| iddia | ölçüm |
|---|---|
| *"Thread içinde deterministik soru LLM'e düşüyor"* (§11.2/A) | ❌ **ÇÜRÜDÜ** — `deterministic_refine` çalıştı, 0 LLM |
| *"Intent LLM'e gidiyor"* | ❌ **ÇÜRÜDÜ** — iki turda da `route()`/`refine` çözdü |
| 🔴 *"Her istekte LLM çağrısı var"* | ✅ **DOĞRU** — ama **anlatıcı**, intent değil |

> 🔴 **Kullanıcının gördüğü LLM çağrısı gerçek; attığı yer yanlıştı.** Garson siparişi
> **almıyor** — garson tabağı **anlatıyor**. Ve anlatmak, yemeği pişirmekten **20 kat**
> uzun sürüyor.

### 13.4 · Ve deterministik özet ZATEN ORADA — yeterli

Aynı cevapta iki metin birden üretiliyor:

| kaynak | metin | maliyet |
|---|---|---|
| 🟢 `interpret()` — **deterministik** | *"En yüksek makine: DİJİTAL BASKI (0,63 %). En düşük: RAM-3 (0,55 %); 11 kalem."* | **0 LLM · 0 ms** |
| 🔴 `t2_anlatici` — **LLM** | *"Geçen 3 aylık dönemde en yüksek OEE değerine sahip makine DİJİTAL BASKI oldu ve 0,63% seviyesinde gerçekleşti. En düşük OEE ise RAM-3 makinesinde 0,55%…"* | **2 936 ms** *(T2'de 22 564 ms)* |

🔴 **İkisi aynı üç olguyu söylüyor.** LLM'in kattığı şey **üslup**, bilgi değil — ve bu
vakada üslubun fiyatı cevabın kendisinin **20 katı**.

### 13.5 · YAPILACAK — anlatı merdiveni *(§7'ye 1.5 olarak girer, en yüksek öncelik)*

Bu, canlı denetimin ilk turunda da bulunmuştu (*"anlatıda deterministik ilk basamak
yok"*) ve şimdi **fiyatlandı**:

| # | iş |
|---|---|
| **1.5a** | 🔴 **Basit vakada anlatı `interpret()`'in `summary`'sinden gelsin** — tek ölçü · ≤1 kırılım · kıyas yok. Ölçülen kazanç: **−2,9 sn** (T1) · **−22,6 sn** (T2) |
| **1.5b** | LLM anlatıcısı yalnız **karmaşık** vakaya kalsın (çok ölçü · kıyas + segment · katkı ayrıştırması) — *"ne yüksek ne düşük"* zaten şablonla söylenebiliyor |
| **1.5c** | Karmaşıklık ölçütü **yapıdan** okunsun (`measures` · `dimensions` · `compare` · `blend` sayısı), metinden değil — ikinci bir dil ayrıştırıcısı doğmasın |
| **1.5d** | ⚠ Sağlayıcı gecikmesi ayrıca bakılmalı: `deepseek-v4-flash` **22,5 sn** sürdü. *"Flash"* bir modelde bu bir sapma; failover/zaman aşımı eşiği ölçülmeli |

⚠ Ve `narration_guard` korunur: deterministik özet zaten **sayıyı sistemden** alıyor,
yani guard'ın koruduğu şey **yapısal olarak** garanti — LLM anlatısında olmayan bir güvence.

*Bir cevabı süslemek için, cevabın kendisinden yirmi kat uzun beklemek, süslemek değil
geciktirmektir.*


---

## 14 · CANLI THREAD KOŞUMU — 6 thread · 12 tur · tek tek API üzerinden

> Tenant `boyahane` · `:8001` · gerçek HTTP · her turun logu izlendi.
> Sağlayıcı: `openrouter / deepseek-v4-flash`.

| # | tur | soru | `source` | satır | **süre** | anlatı | not |
|---|---|---|---|---|---|---|---|
| 1 | T1 | `makine bazında oee son 3 ay` | 🟢 `cube` | 11 | **5 420 ms** | LLM | intent 0 LLM |
| 1 | T2 | `aylara göre` | 🟢 `cube` | 22 | 🔴 **24 285 ms** | LLM | `deterministic_refine` |
| 2 | T1 | `bu ay toplam üretim` | 🟢 `cube` | 1 | **602 ms** | LLM | ⚠ *"«uretim» birden fazla yerde tanımlı"* — **belirsizlik beyanı** ✅ |
| 2 | T2 | `hat bazında` | 🟢 `cube` | **0** | **568 ms** | — | boş sonuç **dürüstçe** anlatıldı ✅ |
| 3 | T1 | `son 3 ay fire` | 🟢 `cube` | 1 | **10 109 ms** | LLM | *"«fire» birden fazla yerde"* ✅ |
| 3 | T2 | `bir de ciro ekle` | 🟢 `cube` | 1 | **12 098 ms** | LLM | **çapraz-cube harman** 0 LLM ✅ |
| 4 | T1 | `duruş nedenlerine göre toplam süre bu ay` | 🔴 `cube+llm` | 0 | 🔴 **16 687 ms** | — | **kendi açılış chip'imiz** |
| 4 | T2 | `en yüksek 5` | 🟢 `cube` | 0 | **655 ms** | — | `entity_limit` takipte **çalışıyor** |
| 5 | T1 | `şubatta ciro ocağa göre nasıl değişti` | 🟡 **`vqr`** | 30 | **434 ms** | LLM | 🔴 `eksik_niyet=['kiyas','trend']` |
| 6 | T1 | `yılbaşından bugüne hasılat` | 🔴 `cube+llm` | 1 | 🔴 **24 269 ms** | LLM | |
| 6 | T2 | `çeyreklere böl` | 🔴 `cube+llm` | 2 | 🔴🔴 **69 399 ms** | LLM | *"Takip: **LLM-destekli** yapısal düzenleme"* |

### 14.1 · 🔴 Süre dağılımı — asıl bulgu

| yol | süre aralığı |
|---|---|
| 🟢 intent 0 LLM **+ anlatı yok** | **434 – 655 ms** |
| 🟢 intent 0 LLM **+ anlatı LLM** | **5 420 – 24 285 ms** |
| 🔴 intent LLM **+ anlatı LLM** | **16 687 – 69 399 ms** |

> 🔴 **Anlatıcıyı kapatmak, en hızlı turu 434 ms'de tutuyor; açmak aynı işi 24 saniyeye
> çıkarıyor.** Ve 0 satır dönen turlarda anlatı **zaten çalışmıyor** (T2.2 · T4.1 · T4.2)
> — yani mekanizma **zaten koşullu**, koşulu **yanlış** (boş-mu? diye soruyor,
> **karmaşık-mı?** diye sormuyor).

### 14.2 · 🔴🔴 69 saniyelik tur — `çeyreklere böl`

`deterministic_refine` bu düzenlemeyi **çözemedi** → `refine_cube`'e (LLM) düştü
(*"Takip: LLM-destekli yapısal düzenleme"*), sonra üstüne anlatı LLM'i bindi.

⚠ Oysa *"çeyreklere böl"* bir **granülerlik** düzenlemesidir ve `_time_gran` `quarter`'ı
tanıyor. Yani **iki LLM çağrısı**, deterministik olarak çözülebilecek bir istek için.

### 14.3 · 🔴 VQR EKSİK BİR CEVABI ÖNBELLEKLİYOR

Thread 5 · `source=vqr` · **434 ms** — ve beraberinde:

```
eksik_niyet : ['kiyas', 'trend']
note        : ⚠ Sayı doğru ama eksik —
              · iki dönemi kıyaslamanı istedin ama tek bir toplam üretebildim
              · değişimi/trendi istedin …
```

🔴 **Doğrulanmış soru deposu, *"beyanlı kısmi"* bir cevabı dondurmuş.** Yani bu soru
artık **her seferinde** eksik cevaplanacak ve deterministik yol iyileşse bile VQR onu
**es geçecek** — merdivenin ilk basamağı olduğu için.

⚠ Kapı önerisi: VQR'a yazma koşuluna *"`eksik_niyet` boş olmalı"* eklenmeli.
*Bir önbellek, doğruladığı şeyin eksik olduğunu bilmiyorsa, eksikliği kalıcılaştırır.*

### 14.4 · İYİ ÇALIŞAN ÜÇ ŞEY — kayda geçsin

| ne | kanıt |
|---|---|
| **Belirsizlik beyanı** | *"«uretim» birden fazla yerde tanımlı — bu cevap **OEE** tanımıyla; diğerleri: uretim (parti)"* — sessiz seçim **yok** |
| **Boş sonuç dürüstlüğü** | *"Rapor doğru kuruldu — elimdeki veri 01.01.2024–30.06.2026"* — *"veri yok"* demiyor, **sınırı** söylüyor |
| **Çapraz-cube harman** | `bir de ciro ekle` → iki ölçü tek tabloda, **0 LLM** (`cross_cube_add`) |

### 14.5 · ⚠ CANLI ÖRNEK ESKİ KOD KOŞUYOR

`yılbaşından bugüne hasılat` canlıda **`cube+llm`** (24,3 sn) — oysa depodaki onarılmış
`route()` bunu **deterministik** çözüyor (§ YTD onarımı). Yani canlı konteyner
(`dima-backend-core`, ~1 saattir ayakta) bu turdaki düzeltmeleri **taşımıyor**.

🔴 Ölçüm okunurken bu ayrım korunmalı: **canlı sayılar bugünkü kodun değil, dünkü kodun
faturasıdır.** Yeniden derleme sonrası aynı 12 tur tekrarlanmalı.

### 14.6 · ⚠ SAĞLAYICI GECİKMESİ AYRI BİR BULGU

`deepseek-v4-flash` tek çağrıda **2,9 sn → 22,6 sn → 69,4 sn** aralığında salındı.
*"Flash"* sınıfı bir modelde bu bir **sapma**; zaman aşımı eşiği ve failover sırası
ayrıca ölçülmeli. ⚠ Ölçümlerin bir kısmı sağlayıcıya ait olabilir — anlatı merdiveni
kararı bundan **bağımsız** olarak doğrudur (0 satırda zaten çalışmıyor).


---

## 15 · RUNBOOK — düzeltmelerden SONRA aynı usulle nasıl koşulur

> Bu bölüm §14'ün **birebir tekrarı** içindir. Aynı adımlar, aynı okunacak alanlar,
> aynı log satırları — ki *"düzeldi mi"* sorusu **aynı ölçüyle** yanıtlansın.
> ⚠ Test koşucusu (`pytest`) **kullanılmaz**: amaç ürünün gerçek HTTP yüzeyini,
> kullanıcının yazdığı gibi sınamaktır.

### 15.0 · 🔴 ÖNCE KONTEYNERİ TAZELE — yoksa dünkü kodu ölçersin

§14.5'te ölçüldü: canlı konteyner düzeltmeleri **taşımıyordu** (`yılbaşından bugüne`
canlıda `cube+llm`, depoda deterministik). Kaynak bind-mount **edilmiyor**.

```bash
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}' | grep dima-backend
# → dima-backend-core  Up X  0.0.0.0:8001->8000/tcp
curl -s localhost:8001/health        # → {"status":"ok"}
```

🔴 **KOD DEĞİŞTİYSE `restart` YETMEZ — YENİDEN DERLE.** Kaynak bind-mount edilmiyor;
`docker restart` **aynı imajı** yeniden başlatır, yani dünkü kodu ölçmeye devam edersin
(§14.5'te tam bu oldu). Doğru komut:

```bash
export DOCKER_BUILDKIT=0 && export COMPOSE_DOCKER_CLI_BUILD=0 && \
docker-compose build dima-backend && \
docker rm -f dima-backend-core && \
docker-compose up -d dima-backend
```

⚠ Derleme sonrası **`/health` 200 dönene kadar bekle** (VQR embedder soğuk açılışta
dakikalarca askıda kalabiliyor — bilinen kusur):

```bash
until curl -sf localhost:8001/health >/dev/null; do sleep 3; done && echo "hazır"
```

⚠ `:8000` **başka bir uygulamadır** (`akis-main`); Dima `:8001`.

### 15.1 · Kimlik

Parola kodda sabit: `backend/control_plane/seed.py` → `DEMO_OWNER_PASSWORD`.
E-posta kalıbı: `{tenant-slug}@usedima.com` (`seed.py:150`).

```bash
TK=$(curl -s -X POST localhost:8001/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
echo "${#TK} karakter"
```

🔴 **Hız sınırı vardır.** Yanlış parola denemeleri
`{"detail":"Çok fazla deneme — bir süre bekleyin"}` üretir ve pencere kapanana kadar
**doğru parola da reddedilir** (ölçüldü: ~30–60 sn). Parolayı önce koddan **oku**, deneme
yapma.

### 15.2 · Tek turluk çağrı — kopyala/yapıştır

```bash
ask(){ # ask <session> <soru> [cube_query_json] [history_json]
  local sid="$1" q="$2" cq="$3" hist="$4" body
  if [ -n "$cq" ]; then
    body="{\"question\":\"$q\",\"execute\":true,\"session_id\":\"$sid\",\"cube_query\":$cq,\"history\":[$hist]}"
  else
    body="{\"question\":\"$q\",\"execute\":true,\"session_id\":\"$sid\"}"
  fi
  local T0=$(date +%s%3N)
  curl -s --max-time 120 -X POST localhost:8001/ask \
       -H "Authorization: Bearer $TK" -H 'Content-Type: application/json' \
       -d "$body" -o /tmp/cur.json
  local T1=$(date +%s%3N)
  python3 -c "
import json
d=json.load(open('/tmp/cur.json')); i=d.get('interpretation') or {}
print(f\"  src={str(d.get('source')):9} satır={str((d.get('result') or {}).get('row_count')):4} ${T1}-${T0}ms\")
print('  eksik_niyet:', d.get('eksik_niyet'))
print('  note       :', (d.get('note') or '—')[:180])
print('  explain    :', json.dumps(d.get('explain'), ensure_ascii=False))
print('  iz         :'); [print('     -', x) for x in (d.get('trace') or [])]
print('  anlatı     :', 'LLM' if i.get('narration') else '—', '| özet:', (i.get('summary') or '—')[:100])
"
  python3 -c "import json;print(json.dumps(json.load(open('/tmp/cur.json')).get('cube_query'),ensure_ascii=False))" > /tmp/cq.json
}
```

**Thread kurmak** — frontend'in yaptığının aynısı: T1'in `cube_query`'sini T2'ye **aynen**
yankıla.

```bash
ask t1 "makine bazında oee son 3 ay"                       # T1 — taze
CQ=$(cat /tmp/cq.json)
ask t1 "aylara göre" "$CQ" '"makine bazında oee son 3 ay"' # T2 — thread içi
```

### 15.3 · 🔴 HER TURDA OKUNACAK ALTI ALAN

| alan | ne söyler | 🟢 iyi | 🔴 kötü |
|---|---|---|---|
| `source` | hangi basamak cevapladı | `cube` · `vqr` | `cube+llm` *(intent LLM'e gitti)* |
| `explain.path` | **aynı şeyin doğrulaması** | *"route() — LLM'siz"* | *"LLM Intent-JSON"* |
| `trace[0]` | ilk basamak | *"cube_router.route()"* · *"refine → **deterministik** düzenleme"* | *"Takip: **LLM-destekli** yapısal düzenleme"* |
| `eksik_niyet` | sistem neyi **yapamadığını** söylüyor mu | `None` | dolu → cevap **kısmi** |
| `note` | beyan kanalı | belirsizlik/boş-sonuç açıklaması | sessizlik |
| `interpretation.narration` | anlatıcı LLM koştu mu | `—` *(basit vaka)* | `LLM` *(basit vakada = israf)* |

⚠ `source` ile `explain.path` **birbirini doğrular**; ayrışırlarsa biri bayattır — bu
depoda bir kez oldu (Intent-JSON cevabı `route()` güveniyle rozetlenmişti).

### 15.4 · LOGU İZLE — sürenin nereye gittiği YALNIZ orada görünür

```bash
docker logs --since 10m dima-backend-core 2>&1 \
  | grep -E "İSTEK|CEVAP|BAĞLAM|dima\.llm|yayilim|Discovery|vqr"
```

Okunuşu — §14'ten gerçek bir tur:

```
13:43:18  BAĞLAM  kural=yapisal:cube_query cube=oee eksen=('makine',)   ← thread ALGILANDI
13:43:18  İSTEK   q='aylara göre'  followup=True(yapısal=True)          ← takip dalı
13:43:19  yayilim: perdeleme: 1 metin · 1 yer tutucu                    ← ANLATI maskeleme
13:43:41  dima.llm: openrouter BAŞARILI (…, 22564ms)                    ← 🔴 anlatı LLM
13:43:42  CEVAP   source=cube  satır=22  süre=24285ms
```

🔴 **Ayrıştırma kuralı — bu raporun bütün teşhisi buna dayanıyor:**

| log deseni | ne demek |
|---|---|
| `dima.llm` satırı **`yayilim: perdeleme`'den SONRA** | çağrı **ANLATICIDIR** (intent değil) |
| `dima.llm` satırı `İSTEK` ile `CEVAP` arasında, **perdeleme YOK** | çağrı **INTENT**'tir |
| `dima.llm` **hiç yok** | tur tamamen deterministik |
| `süre` − `dima.llm ms` | **cevabın kendi maliyeti** *(ölçüldü: ~1 sn)* |

### 15.5 · 🔴 KABUL TABLOSU — düzeltmeler sonrası beklenen

| # | soru | bugün *(ölçüldü)* | düzeltme sonrası **beklenen** |
|---|---|---|---|
| 1·T1 | `makine bazında oee son 3 ay` | `cube` · 5 420 ms · anlatı **LLM** | `cube` · **< 1 sn** · anlatı **şablon** *(§13.5a)* |
| 1·T2 | `aylara göre` | `cube` · **24 285 ms** | `cube` · **< 1 sn** |
| 2·T1 | `bu ay toplam üretim` | `cube` · 602 ms · anlatı LLM *(özet: **"1 satırlık sonuç"**)* | anlatı **YOK** — özeti boş olan vakada LLM çağrılmamalı |
| 4·T1 | `duruş nedenlerine göre toplam süre bu ay` | 🔴 `cube+llm` · 16 687 ms | 🟢 `cube` — **kendi açılış chip'imiz** deterministik olmalı |
| 5·T1 | `şubatta ciro ocağa göre nasıl değişti` | `vqr` · `eksik_niyet=['kiyas','trend']` | 🔴 **VQR'dan DÜŞMELİ** *(§14.3)* → `compare=mom` ile tam cevap |
| 6·T1 | `yılbaşından bugüne hasılat` | 🔴 `cube+llm` · 24 269 ms | 🟢 `cube` — YTD onarımı **canlıya inince** |
| 6·T2 | `çeyreklere böl` | 🔴🔴 `cube+llm` · **69 399 ms** | 🟢 `cube` · *"refine → **deterministik**"* — `_time_gran` `quarter`'ı tanıyor |

### 15.6 · Koşum disiplini

1. **Tur tur ilerle.** Bir turun `cube_query`'si sonrakinin girdisidir; toplu koşmak
   thread'i bozar.
2. **Her turdan sonra logu oku.** `source=cube` görüp geçmek yetmez — §14'ün bütün
   bulgusu *"`source=cube` ama yine de LLM çağrısı var"* satırındaydı.
3. **Süreyi iki parçaya ayır** (§15.4). Toplam süre tek başına hangi katmanın yavaş
   olduğunu **söylemez**.
4. ⚠ **Sağlayıcı gecikmesini karıştırma.** `deepseek-v4-flash` aynı oturumda
   2,9 → 22,6 → 69,4 sn salındı. Şüpheliyse aynı turu **iki kez** koş; fark büyükse sorun
   mimaride değil sağlayıcıdadır (`KURAL G-1`'in aynı ilkesi).
5. **Boş sonuç bir kusur değildir.** Demo verisi **30.06.2026**'da bitiyor; *"bu ay"*
   soruları 0 satır döner ve sistem bunu **dürüstçe** söyler — bu ✅ bir davranıştır.


---

## 16 · 🔴🔴 UZUN THREAD KOŞUMU — İKİ YENİ KUSUR, biri AĞIR

### 16.1 · Thread 7 — *"bu neden düşük"* zinciri (4 tur)

| tur | soru | `source` | satır | süre | iz |
|---|---|---|---|---|---|
| 1 | `mayıs ayında hat bazında oee` | 🟢 `cube` | 8 | 7 626 ms | `route()` — LLM'siz |
| 2 | `en düşük hangisi` | 🟢 `cube` | 8 | 11 638 ms | `refine → deterministik düzenleme` |
| 3 | `peki bu neden düşük` | 🔴🔴 **`meta`** | — | **371 ms** | 🔴 **`sosyal sınıf (kapanis)`** |
| 4 | `nisanla kıyasla` | 🔴 `cube+llm` | 1 | 19 783 ms | `eksik_niyet=['kiyas']` |

### 16.2 · 🔴🔴 KUSUR A — kök-neden sorusu **VEDA** sanıldı

```
soru : "peki bu neden düşük"
iz   : sosyal sınıf (kapanis) → deterministik yanıt (LLM'siz, sıfır maliyet)
cevap: "Görüşürüz! İstediğin zaman buradayım."
süre : 371 ms
```

🔴 **Kullanıcı bir kök-neden sorusu sordu; sistem hoşça kal dedi.** Ve bunu **0 LLM ile,
371 ms'de, kendinden emin** yaptı — yani en ucuz, en hızlı, en yanlış cevap.

**Tetikleyici izole edildi** — beş varyant, tek tek:

| soru | `source` | cevap | yargı |
|---|---|---|---|
| `peki bu neden düşük` | 🔴 `meta` | *"Görüşürüz!"* | **YANLIŞ** |
| `peki neden böyle` | 🔴 `meta` | *"Görüşürüz!"* | **YANLIŞ** |
| `neden düşük` | 🟢 `None` | *"ort oee çıkarabilirim — hangi dönem için?"* | ✅ netleştirme |
| `peki bu ay ciro` | 🟢 `cube` | rapor | ✅ |
| `bu neden düşük` | ⚠ — | **bozuk JSON** *(§16.3)* | ⚠ |

⊙ **Teşhis:** tetikleyici **`peki`**. Ama tek başına değil — `peki bu ay ciro` **doğru**
çalışıyor. Yani sosyal sınıf kapısı (`D1`) şöyle davranıyor:

> `peki` sosyal sözlükte **var** *(kapanış ailesi)*; cümlede **veri sinyali** bulunmazsa
> sosyal sınıf kazanıyor. `bu neden düşük` bir katalog terimi taşımadığı için veri sinyali
> **sayılmıyor** → *"peki"* kapanış diye okunuyor.

🔴 Kusur `peki`'nin sözlükte olmasında değil, **veri sinyalinin tanımında**: bir **takip
sorusu** (`bu`, `neden`, `düşük`) katalog terimi taşımaz — ama bir thread'in ortasında
gelmiştir ve önceki turun `cube_query`'si **elde durmaktadır**. Kapı ona bakmıyor.

> *Bir cümlenin veri sorusu olup olmadığı, yalnız kendi kelimelerinden okunamaz —
> bağlamı elde tutan bir sistem için bu bilgi zaten mevcuttur.*

⚠ Ve bu, `D1`'in kendi kapı cümlesiyle **çelişiyor**: *"veri sinyali varsa sosyal kelime
kapıyı AÇMAZ"*. Kural doğru; **sinyalin tanımı** thread bağlamını kapsamıyor.

### 16.3 · ⚠ KUSUR B — bozuk JSON yanıtı

`bu neden düşük` → istemci tarafında:

```
json.decoder.JSONDecodeError: Invalid control character at: line 1 column 415
```

🔴 Yanıt gövdesinde **kaçırılmamış bir kontrol karakteri** var (muhtemelen bir metin
alanına giren ham `\n`). Bu, `curl | jq` ya da herhangi bir katı JSON çözücüsünde
**yanıtın tamamını** düşürür — ön yüz bunu *"sunucu hatası"* diye gösterir.

⚠ Ayrı bir bulgu ve `§16.2`'den bağımsız: aynı soru `peki` olmadan sorulduğunda ortaya
çıktı.

### 16.4 · Thread 7'nin öteki iki dersi

| bulgu | kanıt |
|---|---|
| 🟢 `en düşük hangisi` **deterministik** çözüldü | `refine → deterministik düzenleme`, 0 LLM intent |
| 🔴 `nisanla kıyasla` **kıyas kuramadı** | `cube+llm` · `eksik_niyet=['kiyas']` · *"iki dönemi kıyaslamanı istedin ama tek bir toplam üretebildim"* — §3.1'in `referans`/`ayrik_aylar` boşluğunun canlı hâli |

### 16.5 · Bu iki kusurun `§15` runbook'una eklenmesi

| # | soru | bugün | beklenen |
|---|---|---|---|
| 7·T3 | `peki bu neden düşük` | 🔴 `meta` — *"Görüşürüz!"* | thread içinde **asla sosyal** olmamalı; `contribution`/netleştirme |
| — | `peki neden böyle` | 🔴 `meta` | aynı |
| — | `bu neden düşük` | ⚠ bozuk JSON | geçerli JSON |
| 7·T4 | `nisanla kıyasla` | 🔴 `eksik_niyet=['kiyas']` | `compare=mom` ile tam kıyas |

⚠ **Regresyon kapısı önerisi:** sosyal sınıf kapısına *"istekte `cube_query` varsa sosyal
sınıf kapalıdır"* şartı. Bir thread'in içinde veda edilmez.


---

*Ölçüm kaynakları: `app/cube_router.py` (anahtar taraması · `parse_cube_query` ·
`_measure_threshold` · `_top_n` · marjinler `:908`·`:932`·`:937`·`:947`) ·
`app/intent_semasi.py` (şema alanları) · `app/llm.py` (`_cube_select_system` ↔
`_cube_refine_user`) · `app/uyum.py:212` · `app/routers/ask.py:2080`·`2194`·`2509`·`2734`·`2895` ·
`demo/packs/starters.yml` (10 chip, route ölçümü) · **canlı koşum** (`:8001`, tenant `boyahane`, 2 tur, konteyner logları) · `lab/reports/gercek_dunya.md`
(2285 vaka · kademe kırılımı) · canlı Intent turu (9 çağrı).*
