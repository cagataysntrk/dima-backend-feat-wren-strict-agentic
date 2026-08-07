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

*Ölçüm kaynakları: `app/cube_router.py` (anahtar taraması · `parse_cube_query` ·
`_measure_threshold` · `_top_n` · marjinler `:908`·`:932`·`:937`·`:947`) ·
`app/intent_semasi.py` (şema alanları) · `app/llm.py` (`_cube_select_system` ↔
`_cube_refine_user`) · `app/uyum.py:212` · `app/routers/ask.py:2080`·`2194`·`2509`·`2734`·`2895` ·
`demo/packs/starters.yml` (10 chip, route ölçümü) · `lab/reports/gercek_dunya.md`
(2285 vaka · kademe kırılımı) · canlı Intent turu (9 çağrı).*
