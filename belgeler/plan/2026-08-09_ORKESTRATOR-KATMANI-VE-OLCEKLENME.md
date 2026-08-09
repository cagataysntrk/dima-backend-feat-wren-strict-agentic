# ORKESTRATÖR KATMANI — teşhis, cebir, erozyon denetimi ve faz haritası

**Tarih:** 2026-08-09 · **Dal:** `wren-bağımsız` · **Taban commit:** `a8d9c0a`
**Belge türü:** araştırma + yol haritası. **Kod değişikliği içermez.**

---

## 🔴 BU PLAN DÖNGÜNÜN İÇİNDE UYGULANIR

> Bu belge **ana döngünün yan dosyasıdır**, onun yerine geçmez. Buradaki her faz, klasik
> **20-senaryo döngü kurallarına** tabidir ve o kurallar **değişmez**:
>
> 1. Her turda **20 özgün senaryo** — öncekileri tekrar etmeyen, thread/follow-up
>    mantığıyla, basitten karmaşığa.
> 2. **curl ile TEK TEK**, loglar anbean okunarak. Bulk test yok.
> 3. Her tur ilgili denetim belgesine **yazılır**.
> 4. 🔴 **20 senaryo bitmeden teşhise geçilmez.**
> 5. Sonra **TÜM** kök teşhisler → **TÜM** kök çözümler **topluca** (tekil çözüm işe yaramaz).
> 6. Aralarında **kapı yok** (yalnız hedefli `pytest`).
> 7. Sonra **BİR** docker tazeleme → **BİR** curl doğrulama → **BİR** kapı.
> 8. Sonra başa dön, **yeni 20** senaryo.
>
> **EN ÜST KURAL yürürlükte:** route'a Türkçe öğretilmez; şüphede **garson** gider;
> *«anlamadım» yoktur*. Discovery bir **kaçış kapağıdır**, hedef oranını **sıfıra**
> yaklaştırmaktır. Yabancı dil bir ürün hedefi değil, garson yolunun çalışıp çalışmadığını
> gösteren bir **ampuldür** — turda 1-2 yeterlidir, ağırlık **Türkçe**.
>
> 🔴 **VE BU BELGENİN KENDİ KURALI:** bir faz test edilip beklendiği gibi çalışmazsa bu
> *"demek ki yapılmayacakmış"* anlamına **gelmez**. Eksiklik gerçekse **kapatılacaktır**;
> test yalnız *"henüz yeterince gelişmedi"* der. **Vazgeçme yok — ölçüp geliştirme var.**

---

## 📋 KANIT DÜZEYİ ETİKETLERİ

Bu belgedeki her iddia etiketlidir. Kullanıcının uyarısı gereği (*"her dediğim doğru
olmayabilir, iyi araştır kontrol et"*) **kendi iddialarımdan ikisini bu turda çürüttüm**
ve düzeltilmiş hâlleriyle bıraktım.

| etiket | anlamı |
|---|---|
| ✅ **OKUNDU** | kaynaktan doğrulandı (`§83.4`), dosya/satır belirtildi |
| 📊 **ÖLÇÜLDÜ** | bu oturumun canlı curl turlarından, tur kodu belirtildi |
| ⚠ **ÇIKARIM** | mantıksal sonuç, koşularak doğrulanmadı — **fazın ilk işi doğrulamak** |
| ⟳ **DÜZELTİLDİ** | önce yanlış yazdım, denetimde çürüdü, düzeltilmiş hâli burada |

---

## 0 · TEK CÜMLE

Bugün LLM **tek atışlık bir çevirmen**: bir soru → bir `CubeQuery`. Gerçek iş sorularının
çoğu **çok adımlıdır** ve adımların her birini mutfak zaten yapabiliyor; eksik olan, onları
**sıraya dizecek akıl** ile o aklın eline verilecek **ilkel, bileşebilir aletlerdir**.
Altyapının çoğu **yazılmış ve bayrağı kapalı** (`agent_plan_secimi`); eksik olan **plan
parametreleri** ve **zinciri kuran iki halkadır**.

🔴 **VE PLANLAYICI, GARSONUN KENDİSİDİR — ayrı bir çağrı değil** *(kullanıcı düzeltmesi,
`E6`'da ayrıntılı)*: tek adımlı bir plan zaten bugünkü `CubeQuery`'dir, dolayısıyla
`plan_kur` `select_cube`'un **yerine geçer**. Bir soru için hâlâ **tek** LLM turu koşulur;
değişen tek şey o turun çıktısının **1-N adımlı** olabilmesidir. Bu, belgenin en büyük
riskini (`E6` · gecikme) **ölçümle değil tasarımla** yarıya indirir.

*Bir riski azaltmanın en ucuz yolu, onu doğuran tasarım tercihini değiştirmektir.*

---

## 1 · SORUNUN DOĞUŞU

> **(1)** *"RAM 3 diğerlerine göre neden düşük dedim… LLM düşünse … bir orkestratör gibi
> davranabilir. Her şeyi öğretmek zorunda kalmayız. Sonsuz ihtimal var; yüzlerce sektör,
> fabrika, insan. Hepsinin arzusunu menüye eklemek imkânsız."*
>
> **(2)** 🔴 *"Orkestratörün elinde kullanacağı aletler iyice olmalı ki — **dört işlem**
> gibi düşün: dört işlemi eline versen **integral** bile yapabilir."*

İkinci cümle bu belgenin **omurgasıdır**.

### 1.1 · Sorunun ölçülmüş hâli 📊 *(AA turu)*

```
soru : «RAM-3 neden diğerlerinden düşük»
cevap: «ort_oee toplanabilir değil (non_additive) — katkı payı tanımsız olur»
```

`§AA1` bunu **elle** çözdü — iki deterministik sorgu, sıfır LLM. Canlı sonuç 📊:

```
RAM-3, öteki 10 makine ortalamasından %10,7 düşük (0,5245 ↔ akran ort. 0,5876).
• fire: 63.452 kg — akran ort. 39.103 kg (%62,3 fazla, kötü yönde)
```

🔴 **Ölçeklenme sorunu tam burada:** `§AA1` bir **şeklin** elle yazılmış tek örneğidir.
*"Neden arttı"*, *"bu ikisi neden farklı"*, *"kim en çok kötüleşti"* için **ayrı ayrı**
yazmak gerekir. Ve `§AA1`'i yazmak bu oturumda **üç sondaj hatası** üretti 📊 (`_sayi` ad
çakışması · `ContributionResponse` sabit alanları · kayan-nokta biçimi). Her reçete yalnız
pahalı değil, **riskli**.

---

## 2 · MERKEZ FİKİR — DÖRT İŞLEM İLKESİ

### 2.1 · Neden reçete değil ilkel

| | **Reçete takımı** | **İlkel takım** |
|---|---|---|
| kaç soru şeklini karşılar | **yazıldığı kadarını** | **bileşimlerinin tamamını** |
| yeni şekil gelince | yeni fonksiyon + test + kapı | **hiçbir şey** — plan farklı dizilir |
| LLM'in yanılma alanı | hangi reçeteyi çağıracağı | hangi sırayla dizeceği |

⊙ Benzetme teknik olarak da doğru: `+ − × ÷` sonludur ama **kapanış** (closure) sayesinde
sonsuz ifade üretir. Bir takımı güçlü yapan **büyüklüğü değil, bileşebilirliğidir**.

### 2.2 · Kapanış şartı

Evrende üç nesne var: `CQ` (koşmamış soru) · `SATIR` (koşmuş cevap) · `DEĞER` (skaler).

| alet | girdi → çıktı |
|---|---|
| `COZ` | metin → **CQ** |
| `SEC·KIR·SUZ·SIRALA·PENCERE·TUREV·ESIK·KIYAS·HARMANLA` | **CQ** → **CQ** |
| `CALISTIR` | **CQ** → **SATIR** |
| `BAGLA` | **SATIR** → **DEĞER** |
| `HESAPLA` | **SATIR** → **SATIR/DEĞER** |
| `ANLAT` | **SATIR** → metin |

🔴 **Zincir ancak `BAGLA` varsa kurulur.**

### 2.3 · Cebrin envanteri — ✅ OKUNDU, iki düzeltmeyle

Kaynaklar: `intent_semasi.py` (props) · `wren_service.cube_sql` (pop'lananlar) ·
`cube_operatorleri.py` (kip kümeleri).

| ilkel | alan | kapsam | durum |
|---|---|---|---|
| **SEC** | `measures` | katalogdaki her ölçü | ✅ |
| **KIR** | `dimensions` · `timeDimensions` | boyut + granülerlik | ✅ |
| **SUZ** | `filters` | **12 operatör** (`cube_operatorleri.MOTOR_OPERATORLERI`) | ✅ |
| **SIRALA/KES** | `order` · `limit` | yön + top-N | ✅ |
| **PENCERE** | `pencere` | **6 kip** (`kumulatif·hareketli_ort·sira·onceki·degisim_yuzde·pay`) | ✅ |
| **TUREV** | `turev` | **3 kip** (`yuzde·oran·fark`) | ✅ |
| **ESIK** | `measure_having` | ölçü üstü eşik | ✅ |
| **HARMANLA** | `blend` | çok-küp CTE (`wren_service.blend_sql`) | ✅ |
| **CALISTIR** | `cube_sql` → `query` | | ✅ |
| **KIYAS** | `compare` | `yoy·mom` — **yalnız bitişik dönem** | ◐ eksik (G4) |
| ⟳ **entity_limit** | — | | ⟳ **DÜZELTİLDİ ↓** |
| ⟳ **BAGLA** | — | | ⟳ **DÜZELTİLDİ ↓** |
| 🔴 **HESAPLA** | ⊘ yok | satırlar üstünde saf aritmetik | 🔴 **eksik** |

#### ⟳ DÜZELTME 1 — `entity_limit`'i "✅ var" diye yazmıştım, **yanlış**

`entity_limit` `wren_service.py:1265`'te **yalnız bir yorumda** geçiyor ve
`intent_semasi.py`'nin `props` kümesinde **yok**. Yani garson onu **üretemez**; `route()`
yolunda kalan bir alandır. Cebir tablosunda ✅ diye durması yanıltıcıydı.

⊙ Sonuç: `SIRALA/KES` ilkeli **top-N** için tam, **varlık-N** (*"her müşteri için ilk 3
ürün"*) için değil. Bu, `PENCERE(sira)` + `ESIK` ile ifade edilebilir ⚠ **ÇIKARIM** —
faz O-3'ün ilk işi bunu doğrulamaktır.

#### ⟳ DÜZELTME 2 — `BAGLA` "hiç yok" demiştim, **yarı yanlış**

`tools.py::drill.select` ✅ OKUNDU: *"Bir hücreyi/segmenti tek başına gösteren CubeQuery
üretir (grafikten seçim)"*, `determinizm=deterministik`.

⊙ Yani `BAGLA`'nın **şekli var** — ama tetikleyicisi **kullanıcının tıklamasıdır**, bir
önceki adımın sonucu değil. Eksik olan **programatik** bağlamadır: *"en kötü satırı bul,
onu bir sonraki adıma taşı"*.

🔴 Bu düzeltme **işi kolaylaştırıyor**: sıfırdan bir ilkel değil, var olan bir ilkelin
**ikinci tetikleyicisi** yazılacak. Risk ve satır sayısı düşüyor.

### 2.4 · Yeterlilik sınavı ⚠ ÇIKARIM

`akran_kiyasi` bir reçete değil, bir **bileşim** olarak yazılabilir:

```
1. CALISTIR( KIR(makine) ∘ SEC(ort_oee) ∘ SUZ(bu yıl) )   → SATIR
2. BAGLA( en kötü satır, "makine" )                        → "RAM-3"
3. HESAPLA( SATIR, akran_farki, hedef )                    → %10,7
4. CALISTIR( KIR(makine) ∘ SEC(küpün öteki ölçüleri) )     → SATIR
5. HESAPLA( SATIR, oransal_sapma, hedef )                  → sıralı liste
```

Ve **yazılmamış kardeşleri** aynı ilkellerle çıkar:

| soru | bileşim |
|---|---|
| *"kim geçen aya göre en çok kötüleşti"* | `PENCERE(degisim_yuzde)∘SIRALA∘BAGLA` |
| *"en iyi ile en kötü arasındaki fark kaç kg"* | `SIRALA∘BAGLA×2∘HESAPLA(fark)` |
| *"ilk 3'ün payı yüzde kaç"* | `SIRALA∘KES∘PENCERE(pay)` |
| *"hangi vardiyada bu makine akranlarından kötü"* | `SUZ∘KIR∘HESAPLA(sapma)` |

⚠ **Bu bir çıkarımdır, ölçüm değil.** Faz O-3'ün kabul ölçütü tam olarak bunu koşarak
doğrulamaktır. Doğrulanmazsa takım eksiktir ve **eksik ilkel eklenir** — plan iptal edilmez.

---

## 3 · KRİTİK AYRIM — orkestratör Discovery DEĞİLDİR

> 🔴 **Orkestratör hiçbir sayıya dokunmaz.** Çıktısı SQL değil, **fiş dizisidir**.

| | 🥡 Discovery | 🧭 Orkestratör | 🗣 Garson |
|---|---|---|---|
| ne üretir | **ham SQL** | **plan** | tek `CubeQuery` |
| sayıyı kim koyar | LLM'in sorgusu | **her zaman küp** | **her zaman küp** |
| katalog kısıtı | ⊘ | ✅ beyaz liste | ✅ |
| uydurabilir mi | evet | **yapısal olarak hayır** | hayır |
| güven sınıfı | *hiç güvenmediğimiz* | **garsonun yanı** | *asıl hakem* |

*Bir aracı tehlikeli yapan onu kimin kullandığı değil, neye dokunabildiğidir.*

---

## 4 · BULGU — bu iş yarım değil, çoğu bitmiş ✅ OKUNDU

Kullanıcının *"yarım duran agent plan seçici ile birleştirelim"* sezgisi **doğrudur**:
tarif edilen orkestratör **zaten `Planlayici.sec()`'tir**.

| bileşen | yer | durum |
|---|---|---|
| Plan önerici | `planner.py::sec()` | ✅ |
| Araç kaydı — **23 araç** | `tools.py::KAYIT` | ✅ |
| Yetki süzgeci | `tools.py::izinli_araclar` → `control_plane.authorize.can` | ✅ |
| Dört kapı | `planner.py::calistir()` | ✅ |
| Bütçe · makbuz · strateji değişimi · adım doğrulama | `planner.py` | ✅ |
| LLM ucu | `llm.py::plan_sec()` (üç sağlayıcı) | ✅ |
| Tüketici | `ask.py::_capraz_alan_pilotu()` | ◐ **tek dar kapı** |
| Bayrak | `features.yml::agent_plan_secimi` | 🔴 **`off`** |

### 4.1 · `sec()`'in kendi docstring'i güvenlik argümanını kurmuş ✅

> *"Dönen liste bir **öneridir**… **LLM'in uydurduğu bir araç adı KAYIT kapısında ölür**,
> yetkisiz bir araç YETKİ kapısında ölür… Yani seçicinin yanılması **yeni bir risk
> açmaz**."*

### 4.2 · Gerçek boşluklar

| # | boşluk | kanıt |
|---|---|---|
| **B1** | Plan **parametresiz** — yalnız araç adı taşıyor | ✅ `sec()` çıktısı `{"arac": ad}` |
| **B2** | Kayıt ilkel değil — **10 reçete** taşıyor | ✅ `KAYIT` sınıflandırması ↓ |
| **B3** | `BAGLA`'nın programatik tetikleyicisi + `HESAPLA` yok | ⟳ düzeltilmiş hâl |
| **B4** | Tek tüketici (`other_topic` dalı) | ✅ |

**B2 sınıflandırması** ✅ OKUNDU — 23 aracın dağılımı:

| sınıf | sayı | örnek |
|---|---|---|
| giriş | 3 | `route` · `llm.select_cube` · `llm.prompt_enhance` |
| CQ→CQ | 4 | `deterministic_refine` · `cross_cube_add` · `drill.expand` · `drill.select` |
| çıkış | 1 | `cube_sql` |
| **reçete** | **10** | `yoy.compute` · `contribution.*`(3) · `stats.*`(2) · `kpi.resolve` · `statements.resolve` · `prescribe.recete` · `schedules.uyari_nedeni` |
| sunum | 5 | `interpret` · `viz.recommend` · `report.compose` · `llm.anlat` · `narration_guard.dogrula` |

⚠ Ve `§AA1`'in `_akran_kiyasi`'sı **kayıtlı bile değil** — bir dal olarak yazıldı.

---

## 5 · 🔴 EROZYON DENETİMİ — bu planın sistemi bozma riskleri

> Kullanıcının açık uyarısı: *"şu anki sistemi devasa bir erozyona sürüklemeyelim… bunu da
> düşündüğünü ve kontrol ettiğini söyle ki emin olalım."*
>
> Aşağıdakiler **gerçek** risklerdir. Her biri için karşı önlem **fazın kabul ölçütüne**
> yazılıdır; önlem yoksa faz **koşulmaz**.

### 🔴 E1 · İlkeller daha ifade gücü verir ama **daha opaktır**

Yanlış bir **reçete** çağrısı adıyla belli olur (`akran_kiyasi` — insan görür). Yanlış bir
**ilkel zinciri** sekiz adımlık `SUZ/KIR/HESAPLA` dizisidir; hatası **birkaç adım sonra**
görünür ve hangi adımdan geldiği belirsizdir.

**Karşı önlem:** her adımın **kendi makbuzu** (`Kosum.makbuza()` zaten üretiyor) ve her
`CALISTIR`'ın **tıklanır `CubeQuery`'si**. Adım görünmezse faz **kabul edilmez** (FAZ O-5
bu yüzden **zorunlu**, isteğe bağlı değil).

### 🔴 E2 · Araç listesi büyürse seçim **kötüleşir**

12 ilkel + 23 mevcut = 35 kalem. Ölçülmüş emsal: `§99.1` — *geniş sinonim küpü açgözlü
yapar*; `kalite.default_measure` bunu bir kez ölçtü 📊 (`'hatali': oee → kalite` çakışması,
geri alındı).

**Karşı önlem:** ilkeller kayda girerken **10 reçete `llm_araclari`'ndan çıkarılır** —
liste **büyümez, yer değiştirir**. Ve reçeteler **silinmez** (`MIMARI §10`: kapananlar
işaretlenir), yalnız ajanın görüş alanından çıkar; HTTP uçları ve mevcut dallar
**dokunulmadan** çalışmaya devam eder.

### 🔴 E3 · Doğruluk vetosu — `sessiz_yanlis` sekiz turdur **10**

📊 V·W·X·Y·Z·AA·BB turlarında `sessiz_yanlis` **hiç oynamadı**; korpus %94,9; gerçek-dünya
{2287·1145·90·38} birebir aynı.

🔴 **Bir LLM-planlı yolu deterministik bir yolun önüne koymak, tam olarak bu sayıyı
tehdit eder.**

**Karşı önlem — üç katmanlı:**
1. `deterministik-önce` kapısı **zaten var** ve değişmez: `route()` denenmeden bir LLM
   aracı seçilemez.
2. Orkestratör **yalnız route+garson çözemediğinde** devreye girer — merdivenin yerini
   almaz, **boşluğunu** doldurur.
3. `sessiz_yanlis` **yükselirse faz geri alınır** (doğruluk vetosu). ⚠ Ama *"geri alınır"*
   = *"vazgeçilir"* değil: kök bulunur, düzeltilir, yeniden ölçülür.

### 🔴 E4 · `§AA1` **bugün çalışıyor** — mimari saflık için bozulmamalı

📊 Canlıda iki kez doğrulandı (RAM-3 ve `fire_orani_yuzde`/OSMAN ÇELİK).

**Karşı önlem:** `§AA1` **yerinde kalır**. Orkestratörün görevi onu *"ifade edebilmek"*tir;
elle yazılmış sürüm ancak bileşim **aynı canlı senaryolarda birebir aynı sonucu** verdikten
sonra emekliye ayrılır. *Çalışan bir şeyi, daha güzel bir mimari için bozmayız.*

### 🔴 E5 · Büyüme tavanları — her faz kod ekliyor

📊 Bu oturumda kapı büyüme tavanlarını **beş kez** yakaladı; her biri gerekçeli muafiyet
istedi. `ask()` iç fonksiyon tavanı (**19**) için muafiyet listesi **boştur ve boş kalması
bir başarıdır** — kapının kendi cümlesi.

**Karşı önlem:** orkestratör gövdesi **`ask()` içine yazılmaz**. Yeni kod `planner.py` ve
yeni bir `app/ilkeller.py` modülüne gider; `ask.py`'de kalan yalnız **çağrı** olur.

### 🔴 E6 · Gecikme çarpılır — ve taban **zaten gerilemiş**

📊 `/ask` soru başına 47 ms → **177 ms** (bağımsız ajan raporu). Bir plan 3-8 sorgu koşar.

**Karşı önlem:** **FAZ O-0 ön koşuldur** — latency kapısı orkestratörden **önce** gelir.
Ve `Butce(adim, saniye, sorgu)` zaten yazılı; aşımda **kısmi cevap + gerekçe** döner.

#### ⟳ **E6 DÜZELTİLDİ — riskin YARISI bir tasarım tercihinden doğuyordu** *(kullanıcı sorusu, 2026-08-09)*

> *"Planlayıcı ile LLM intent yani garson **aynı kişi olabilir** — çünkü LLM'e iki istek
> yerine tek cevapta bunu halledebiliriz."*

⊙ **Doğru, ve bu belgenin kurgusunu düzeltiyor.** Yukarıdaki *"gecikme 3-5× çarpılır"*
cümlesi örtük bir varsayıma dayanıyordu: **plan, garsona EK bir çağrı**. Oysa:

🔴 **TEK ADIMLI BİR PLAN, ZATEN BUGÜNKÜ `CubeQuery`'DİR.**

Yani `plan_kur`, `select_cube`'un **yerine geçer** — üstüne eklenmez. Bir soru için hâlâ
**tek** garson turu koşulur (`k=3` öz-tutarlılık örneklemiyle birlikte); değişen tek şey o
turun çıktısının bir `CubeQuery` yerine **1-N adımlı bir plan** olmasıdır.

| | **iki çağrı** *(bu belgenin ilk kurgusu)* | **tek çağrı** *(düzeltilmiş)* |
|---|---|---|
| basit soru (*«bu yıl fire»*) | garson + planlayıcı = **2 tur** | **1 tur** — bugünkü maliyetin birebir aynısı |
| çok adımlı soru | 2 tur + N sorgu | **1 tur** + N sorgu |
| çarpanın yeri | **LLM turu** ⚠ | **sorgu** ✅ |

⊙ Ayrım önemli çünkü ikisi **aynı fiyatta değil**: canlıda bir Intent turu `k=3` ile
**~8-20 sn** (log: `openrouter API başarılı … 8045ms`), bir küp sorgusu **~150-600 ms**.
Yani LLM turunu çarpmak, sorguyu çarpmaktan **bir mertebe** pahalıdır. Riski sorgu
tarafına taşımak, E6'nın büyük kısmını **tasarımla** çözer — ölçümle değil.

⚠ Ve bu, `O-2`'nin kabul ölçütünü **doğal olarak** karşılıyor: *"bayrak kapalıyken bayt
bayt aynı"* — çünkü tek adımlı plan **tam olarak** bugünkü çıktıdır. Yani geçiş bir
davranış değişikliği değil, bir **temsil genişlemesi**.

🔴 **O-0 yine de ön koşul kalır** ama gerekçesi değişir: artık *"planın kendi maliyetini
karşılamak için"* değil, **zaten var olan ×3,8 gerilemeyi** kapatmak için. O gerileme
plandan bağımsız bir borçtur ve orkestratör olmasa da ödenmelidir.

*Bir riski azaltmanın en ucuz yolu, onu doğuran tasarım tercihini değiştirmektir.*

### 🔴 E7 · Yeni yüklemler kendi yanlış-pozitiflerini üretir

📊 Bu oturumda **üç kez** oldu: `§V5.1` (çoğul eki), `§BB-B` (`kpi` alanı unutuldu),
`§Z2` (iç içe sinonim). Üçü de **sondajla** yakalandı, sevk edilmedi.

**Karşı önlem:** `§101.1` — her yeni yüklem, ilan ettiği kusurdan **daha sık yanılmadığı**
sondajla gösterilmeden sevk edilmez.

### ⚠ E8 · Bu belgenin kendi çıkarımları

§2.4'ün *"her şey bileşimle ifade edilebilir"* iddiası ⚠ **ÇIKARIM**dır. Yanlışsa takım
eksiktir.

**Karşı önlem:** FAZ O-3'ün kabul ölçütü **tam olarak budur**. Doğrulanmazsa **eksik ilkel
eklenir** — plan iptal edilmez, düzeltilir.

---

## 6 · DİĞER ÖLÇEKLENME BOŞLUKLARI

### 🔴 G1 · Menü, yazarın kelimesini taşıyor 📊 *(dört kanıt)*

| tur | soru | mutfakta var | eksik |
|---|---|---|---|
| `Y6` | *«tamir süresi»* | `ort_durus_dakika` (`mttr` sinonimi **var**) | *«tamir süresi»* yazılı değil |
| `AA13` | *«üretim miktarı»* | `parti.toplam_agirlik_kg` | *«miktar»* yazılı değildi |
| `X8` | *«mesai ücreti»* | `ik.toplam_mesai_ucreti` | ifade eşleşmedi |
| `Z12` | *«bölgelere göre»* | `sikayet`+`bolge` | çekim eşleşmedi |

**Kök çözüm — sinonim şişirmek DEĞİL** (`§99.1`). Bir **ölçüm aleti**:
`interaction_log` → cevapsız soru / katalog terimi eşleme raporu. **Menü ölçümle büyür.**

### 🔴 G2 · Yokluk ile yarımlık ayırt edilemiyor 📊 *(üç kanıt)*

| soru | mutfakta | yaptığı | doğrusu |
|---|---|---|---|
| `Y4` *«bakım maliyeti»* | yalnız `toplam_yedek_parca_maliyet` | en yakınını verdi | *«yalnız yedek parça, işçilik yok»* |
| `BB14` *«zamanında teslim»* | yalnız `gecikmeli_sevkiyat_yuzde` | konu daralttı | *«tümleyeni var»* |
| `W13` *«çalışma saati»* | yalnız `egitim.toplam_egitim_saati` | 🔴 **eğitim saatini verdi** | *«çalışma saati yok»* |

🔴 `W13` bir **sessiz yanlıştır**.

**Kök çözüm:** pack-düzeyi **yakınlık beyanı** (*"parçası"* / *"tümleyeni"*). MDL alanları
sabit → MDL'e yeni alan **değil**, `cube_synonyms.yml` deseninde pack beyanı.
⚠ Genel bir yüklem **denendi ve reddedildi** (`§101.1`): her yabancı dilli soruda
yanlış-pozitif (`W12` Almanca).

### 🔴 G3 · Çok-küp kompozisyonu 📊 · G4 · Kıyas temsili 📊 *(dokuz kanıt)*

`AA6`/`AA7` (kullanıcının literal örneği) → daraltma / Discovery 25 sn.
`V12·X2·X11·X13·AA9·BB10` → `🔴temsil-yok=kiyas`.

`CubeQuery` **iki ayrık dönemi taşıyamıyor**. Sistem bunu **sayabiliyor**
(`donem_sayisi`), **temsil edemiyor**.
**Kök çözüm:** `kiyas_donemleri: [{gte,lte},{gte,lte}]` — `KIYAS` ilkelinin tamamlanması.

### 🔴 G5 · Latency ×3,8 · G6 · Discovery 7 turda **4 ateşleme** 📊

`§0.0`: her ateşleme bir **mutfak eksikliği raporudur**. Orkestratör bu sayıyı düşürmenin
en güçlü aracıdır — bugün Discovery'ye düşenlerin çoğu *"tek CQ ile ifade edilemez"*
sınıfındandır.

### ◐ G7 · Onaylı yazma — **v1 dışı**, ayrı risk sınıfı

---

## 7 · FAZ HARİTASI

> Her faz **20-senaryo döngüsünün içinde** geliştirilir. Her fazın **kendi bayrağı** vardır
> ve **kapalı doğar** (`KURAL B`: kapalıyken davranış **bayt bayt** bugünkü).
> Her fazın **kabul ölçütü** ve **erozyon koruması** yazılıdır.

| faz | ne | erozyon koruması | kabul ölçütü |
|---|---|---|---|
| **O-1** | `BAGLA`(programatik) + `HESAPLA` *(B3)* — 🔴 **İLK FAZ** | iki **saf fonksiyon**, LLM yok, SQL yok; `ask()` dışında | `§AA1` çıktısı bu ikisi **çağrılarak** birebir üretiliyor |
| **O-0** | Latency tavanı *(G5)* — **ön koşul, `O-2`'den önce** | `lru_cache` **ölçmeden** eklenmez | medyan `/ask` kapıya bağlı ve **düşüyor** |
| **O-2** | Plan parametreleşsin *(B1)* — 🔴 **ve `select_cube`'un YERİNE geçer** *(E6 düzeltmesi)* | şema-kısıtlı (`oneOf`); `$değişken` yalnız **adım referansı**; dört kapı değişmez; **ikinci bir LLM turu AÇILMAZ** | katalog dışı adım **düşer**, tur düşmez; tek adımlı plan bugünkü `CubeQuery` ile **bayt bayt** aynı; **LLM turu sayısı ARTMIYOR** |
| **O-3** | İlkeller kayda, **10 reçete `llm_araclari`'ndan çıkar** *(B2)* | reçeteler **silinmez**, uçları çalışır; liste **büyümez, yer değiştirir** *(E2)* | §2.4'ün **beş bileşimi** kod yazmadan koşuyor *(E8 sınavı)* |
| **O-4** | Tüketici genişlesin *(B4)* | orkestratör merdivenin **yerine geçmez**, boşluğunu doldurur *(E3)* | `AA6`/`AA7` cevap üretiyor **ya da** neden üretemediğini **adım adım** söylüyor |
| **O-5** | Makbuz kullanıcıya — **zorunlu** *(E1)* | — | her `CALISTIR` tıklanır, `/cube` ile **sıfır LLM** koşar |
| **O-6** | `KIYAS` ilkelini tamamla *(G4)* | | *«ocak ile haziranı kıyasla»* iki dönemi yan yana veriyor |
| **O-7** | Yokluk/yarımlık beyanı *(G2)* | pack beyanı, MDL'e alan **eklenmez** | `W13` 🔴 **eğitim saati VERMİYOR** |
| **O-8** | Menü ölçüm aleti *(G1)* | sinonim **şişirilmez** | ✅ `lab/menu.py`. ⟳ Ölçüm iki beklentiyi düzeltti: `X8` **kapanmış**, `AA13`'ün beklentisi bayattı. 🔴 Ve `Y6` *cevapsız* değil **yanlış** çıktı (`kalite` veriyor) — `G1` sessizce `G2`'ye dönüşmüş |
| **O-9** | Discovery oranı A/B *(G6)* | payda **kutsal** — eşit değilse karşılaştırma reddedilir | ✅ `lab/discovery_orani.py`. Ölçüldü: %55 → 🔴%65 (yanlış yerleşim) → **%55** (düzeltilmiş). Kural uygulandı: faz **geliştirilir, iptal edilmez** |
| **O-10** | Onaylı yazma *(G7)* | **v1 dışı** | — |

#### 🔴🔴 ⟳ `E6` DÜZELTMESİ **ÖLÇÜMLE GERİ ALINDI** *(EE turu, 2026-08-09)*

Yukarıdaki `O-2` satırı *"`select_cube`'un **YERİNE** geçer · LLM turu ARTMAZ"* diyor.
Uygulandı, canlı A/B koşuldu ve **çürüdü**. Satır artık okunmalı ama **uygulanmamalıdır**;
doğru hâli aşağıdadır.

| koşum | 🗣 `cube+llm` | 🥡 Discovery/adhoc | **arıza oranı** |
|---|---|---|---|
| **A** · bayrak kapalı | **%35** | %10 | **%55** |
| **B** · plan `select_cube` YERİNE | %25 | 🔴 %25 | 🔴 **%65** *(+10 puan)* |
| **B2** · plan **yalnız boşlukta** | **%35** | %5 | **%55** *(+0,0)* |

⊙ **Mekanizma:** `_select_consistent` `k` örneği **aynı** süreçten çeker ve oylar. Plan
araya girince örneklerin bir kısmı plandan, bir kısmı `select_cube` yedeğinden geliyordu —
oy artık **aynı dağılımdan** çekilmiyordu. *Bir oylamanın geçerliliği örneklerin
özdeşliğine dayanır; iki farklı süreci aynı sandığa atmak, oylamayı gürültüye çevirir.*

Somut kayıplar: `EE6` *«hiç iş kazası oldu mu»* A'da `{kaza_adedi: 0}` → B'de **cevapsız**
· `EE14` *«ciromuz büyüdü mü»* → **İK'ya** düştü · `EE4` 10 satır → cevapsız.

**Doğru yerleşim `E3`'ün lafzıydı:** plan yalnız **boşlukta** (route boş **ve** garsonun
tek-cube cevabı yok). Böylece cevaplanan hiçbir soruya bir çağrı bile eklenmez — yani
`E6`'nın riski **tasarımla sıfırlanır**, `E6` düzeltmesinin aradığı şey de zaten buydu;
yalnız yeri yanlış seçilmişti.

⚠ **Ve kazanç henüz SIFIR.** Canlı iki plan denemesinde de şema-geçerli plan çıkmadı:
(1) `TREND`·`AYRISTIR`·`KIYASLA`·`ANLAT` çalıştırıcıları bağlı değil, (2) serbest-JSON
sağlayıcı adım **sözleşmesine** uymuyor (fiili doğru yazıp parametrelerini uyduruyor) ve
`ZORUNLU_ALANLAR` onları düşürüyor — **doğru davranış**. Karar, raporun kendi kuralıyla:
bayrak `off`, faz **geliştirilir, iptal edilmez**.

*Bir tasarım kararının doğruluğu, onu yazan aklın gücüyle değil, ölçüldüğü koşumla
belirlenir.*

#### ⟳ SIRA DEĞİŞTİ — `O-1` başa alındı *(2026-08-09)*

İlk yazımda `O-0` (latency) mutlak ön koşuldu. Ama `O-1`'in **hiçbir latency etkisi yok**:
iki **saf fonksiyon** yazılıyor, LLM çağrılmıyor, sorgu koşulmuyor, ve kabul ölçütü bir
**davranış denkliği** — *«`§AA1`'in bugünkü çıktısı bu ikisi çağrılarak birebir
üretilebiliyor»*.

⊙ Yani `O-1` bir **yetenek eklemesi değil, denkliği kanıtlanan bir refactor**. Riski
sıfıra yakın, kazancı ise büyük: planlayıcının zemini kurulur ve `§AA1` **kaybolmadan**
ilkellere taşınmış olur (`E4`'ün istediği tam da bu).

🔴 `O-0` yine ön koşuldur ama **`O-2`'nin** ön koşulu: plan **koşmaya** başladığı anda
gecikme ölçülebilir olmalı. `O-1`'i beklemesi için bir sebep yok.

*Bir ön koşul, ancak koşulladığı şeyin önünde durmalıdır.*

🔴 **Her fazın sonunda, döngü kuralı gereği:** tüm kökler → tek kapı → docker tazele →
curl doğrulama. Ve her kapıda `sessiz_yanlis` **10'da kalmalı** *(E3)*.
⚠ **Ara kapı YOK:** fazlar bir demet olarak geliştirilir, kapı **demetin sonunda bir kez**
koşar (`SIFIRINCI KURAL`). Bir fazın bitişi kapı gerektirmez; **demetin** bitişi gerektirir.

---

## 8 · CURL THREAD SENARYOLARI

> Bunlar **faz kabul senaryolarıdır**; 20'lik turların içine dağıtılacak, turun kalan
> senaryoları her zamanki gibi **özgün** olacak.

### O-1/O-2 — zincir kurulabiliyor mu

```
T1.1  bu yıl makine bazında ortalama oee
T1.2  ↳ RAM-3 neden diğerlerinden düşük                       [BAGLA + HESAPLA]
T1.3  ↳ bu farkın hangi vardiyada yoğunlaştığını göster       [4. ADIM — BUGÜN YOK]
T1.4  ↳ o vardiyada duruş nedenlerinin dökümünü ver           [5. adım]
T1.5  ↳ bu analizi kaç adımda yaptın, hangi sorguları koştun  [MAKBUZ]
```

### O-3 — **E8 sınavı**: reçetesi olmayan sorular

```
T2.1  bu yıl kim geçen aya göre en çok kötüleşti              [PENCERE∘SIRALA∘BAGLA]
T2.2  en iyi ile en kötü hat arasındaki fark kaç kg           [SIRALA∘BAGLA×2∘HESAPLA]
T2.3  ilk 3 müşteri toplam cironun yüzde kaçı                 [SIRALA∘KES∘PENCERE(pay)]
T2.4  bu düşüş hangi müşteriden geliyor                       [KIR∘KIYAS∘HESAPLA]
T2.5  hangi vardiyada RAM-3 akranlarından daha kötü           [SUZ∘KIR∘HESAPLA]
T2.6  her müşteri için en çok aldığı 3 ürün                   [⟳ entity_limit düzeltmesinin sınavı]
```

🔴 **Altısı da bugün yazılmamış reçete gerektiriyor.** Kabul: **kod yazılmadan** cevap.

### O-3 — bileşenlere ayırma *(açık kök u5)*

```
T3.1  bu yıl hat bazında ortalama oee
T3.2  ↳ bunu bileşenlerine ayır       [ort_kullanilabilirlik/performans/kalite]
T3.3  ↳ en düşük bileşen hangi hatta en kötü
T3.4  ↳ bu üç bileşen nasıl çarpılıyor  [MAKBUZ — tam OEE formülü]
```

### O-4 — kullanıcının literal örnekleri

```
T4.1  makine verimliliklerinin bu yılki kârlılığa etkisini analiz et
T4.2  ↳ en verimsiz makinenin kârlılığa etkisini rakamla göster
T4.3  personel çalışma süreleri ve verimliliklerini kıyasla ve listele
T4.4  ↳ en düşüğün neden diğerlerinden düşük olduğunu bul
T4.5  ciromun en büyük 3 kaynağı olan müşterilerimi bul
T4.6  ↳ bunlara en çok neler sattığımı üçü için ayrı ayrı karşılaştır
```

### O-5 — makbuz, güven, geri dönüş

```
T5.1  bu yıl kısım bazında fire oranı
T5.2  ↳ en kötüsü neden geride
T5.3  ↳ ikinci adımın sorgusunu tek başına koştur   [CHECKPOINT — SIFIR LLM]
T5.4  ↳ bu sayı kaç kayıttan hesaplandı             [MAKBUZ · HACİM — HİÇ SORULMADI]
T5.5  ↳ bu sonuca güvenebilir miyim
```

### O-6 — kıyas temsili

```
T6.1  ocak ile haziranı fire açısından kıyasla
T6.2  1. çeyrek ile 3. çeyreği enerji yoğunluğunda kıyasla
T6.3  ↳ aradaki farkın kaç kg üretime denk geldiğini hesapla
T6.4  ↳ bu kıyas hangi tarih aralıklarını kapsıyor   [MAKBUZ]
```

### O-7 — yokluk/yarımlık dürüstlüğü

```
T7.1  bu yıl bölüm bazında bakım maliyeti          [YARIM]
T7.2  bu yıl kaç sevkiyat zamanında teslim edildi  [TÜMLEYEN]
T7.3  bu yıl personel bazında çalışma saati        [🔴 YOK — eğitim saati VERMEMELİ]
T7.4  bu yıl kapasite kullanım oranı               [envanter]
T7.5  bu yıl stok devir hızı                       [envanter]
```

### Ampul *(turda 1-2 — dil hedef değil, gösterge)*

```
A1  [EN] why is RAM-3 lower than the other machines this year?
A2  [AR] لماذا انخفض معدل OEE لهذا القسم؟
```

### 🔴 Gerileme koruması — **her turda zorunlu** *(E3/E4)*

```
R1  bu yıl bölüm bazında elektrik tüketimi   [LLM'siz KALMALI]
R2  ↳ bu nasıl hesaplandı                     [makbuz — 15 turdur isabetli]
R3  en kötü vardiya neden geride              [§BB-A üstünlük çapası]
R4  bunlara en çok neler sattım               [§AA4 çoğul zamir]
R5  bu yıl vardiya bazında fire oranı         [sessiz_yanlis 10'da KALMALI]
```

---

## 9 · NE YAPMIYORUZ

| yapılmayacak | gerekçe |
|---|---|
| Serbest plan dili | İlkel icat eden LLM, SQL yazan LLM'den az denetlenebilir *(E1)* |
| Orkestratörün sayı üretmesi | `MIMARI §4.4` |
| Nedensellik iddiası | Elimizdeki **sapma**; korelasyon bile değil |
| Sinonim şişirmek | `§99.1` |
| Sayısal güven eşiği | Kalibre edilmemiş sayı güven değil **süstür** |
| Reçete araçlarını **silmek** | `MIMARI §10` — işaretlenir, silinmez *(E2)* |
| `§AA1`'i baştan yazmak | **Çalışıyor** — bileşim eşitliği kanıtlanana kadar dokunulmaz *(E4)* |
| Orkestratör gövdesini `ask()` içine koymak | İç fonksiyon tavanı; muafiyet listesi **boş kalmalı** *(E5)* |
| Discovery'yi kaldırmak | Bir **kaçış kapağıdır**; hedef oranını **sıfıra yaklaştırmak** |

---

## 10 · ÖZET — beş cümle

1. Orkestratör **zaten yazılmış**: `Planlayici` + `KAYIT` + dört kapı + makbuz. Bayrağı
   kapalı, tüketicisi dar, planı **parametresiz**.
2. 🔴 Asıl mesele **alet takımıdır**: kayıt **10 reçete** taşıyor, orkestratöre *"integral
   almayı"* değil *"şu üç integrali"* veriyor.
3. Cebrin **dokuzu zaten var**; eksik olan **`HESAPLA`**, **`BAGLA`'nın programatik
   tetikleyicisi** ⟳ *(şekli `drill.select`'te mevcut)* ve `KIYAS`'ın ayrık dönem hâli.
4. ⟳ **Kendi iki iddiam bu turda çürüdü** (`entity_limit` şemada yok; `BAGLA` yarı var) —
   ikisi de düzeltildi ve ikincisi işi **kolaylaştırdı**.
5. 🔴 **Erozyon riski ciddiye alındı:** sekiz risk adıyla sayıldı, her birinin karşı önlemi
   fazın **kabul ölçütüne** yazıldı. En önemlisi: `sessiz_yanlis` **10'da sabit** kalmalı,
   `§AA1` **bozulmamalı**, ve orkestratör merdivenin **yerine değil boşluğuna** girmeli.

> *Bir sistemi akıllı yapan, LLM'e daha çok şey yaptırmak değil; ona daha az şeye
> dokunarak daha çok şey söyletmektir. Ve bunu sağlayan aletlerin çokluğu değil,
> ilkelliğidir.*

---

## 🔎 BAĞIMSIZ KONTROL — döngü ajanı, 2026-08-09

Belge **okundu, iddiaları kaynaktan sınandı ve iki noktada geliştirildi.** Kontrolün
kendisi de `§83.4` disipliniyle yapıldı: koşarak değil, **kaynaktan**.

### Doğrulanan iddialar ✅

| iddia | kontrol |
|---|---|
| `B1` — plan **parametresiz** | ✅ `planner.sec()` gerçekten `[{"arac": ad, "neden": …}]` döndürüyor (`:411`, `:419`, `:425`) |
| `B2` — kayıtta **23 araç** | ✅ sayıldı: 23 |
| dört kapı yazılı | ✅ `sec()`'in docstring'i kayıt·yetki·deterministik-önce·bütçe kapılarını **adıyla** kuruyor |
| `E4` — `§AA1` bugün çalışıyor | ✅ canlıda dört turda doğrulandı (`AA2`·`BB2`·`CC4`·`BB1`) |
| `E7` — üç yanlış-pozitif | ✅ üçü de bu oturumun kaydında (`§V5.1`·`§BB-B`·`§Z2`) — ve **dördüncüsü** eklendi: `§CC-A` (`§BB-A`'nın kenar etkisi) |

### İki geliştirme ⟳

1. **`E6` yarıya indi** — planlayıcı garsonun **kendisi**, ayrı çağrı değil. Riskin
   kaynağı ölçüm değil **tasarım tercihiydi**; tercih değişince risk sorgu tarafına kaydı.
2. **Sıra değişti** — `O-1` başa alındı. Latency ön koşulu `O-2`'nin önünde durmalı,
   `O-1`'in değil: `O-1` LLM de sorgu da çalıştırmıyor.

### Eklenen risk 🔴 E9 · BU BELGE DE BİR YÜKLEM ÜRETİYOR

`E7` yeni **yüklemlerin** yanlış-pozitifini sayıyor. Ama bu belgenin kendisi de bir
yüklem öneriyor: *«bu soru çok adımlıdır»*. O yüklem yanılırsa bedeli `E7`'dekilerden
**farklı**: tek adımlık bir soruya üç adımlık bir plan kurulursa cevap **yanlış olmaz,
pahalı olur** — ve pahalılık `E6`'nın kapısına takılır, doğruluk vetosuna değil.

**Karşı önlem:** `O-2`'de plan uzunluğu **bir ölçüdür**: tek adımlı plan oranı korpusta
izlenir. Oran düşerse (plan gereksiz yere uzuyorsa) istem daraltılır.
*Bir aklın fazla düşünmesi, az düşünmesi kadar ölçülmelidir.*

### Kabul

🟢 **Belge uygulanabilir.** Sıra: `O-1` → `O-0` → `O-2` → … Demet **tek kapıyla** kapanır;
fazlar arasında ara kapı koşulmaz (`SIFIRINCI KURAL`).
