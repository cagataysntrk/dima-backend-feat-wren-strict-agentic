# DİMA — REKABET, MİMARİ VE YETERLİLİK ANALİZİ

> **Belge türü:** araştırma raporu (geliştirme değil).
> **Tarih:** 2026-08-11 · **Kapsam:** rakip ürünler · mimari kıyas · ölçüm sisteminin
> kendisi · açık kaynak fırsatları · ne yapmalıyız.
>
> ⚠ Bu belgedeki her sayı **ölçülmüştür**. Ölçülmemiş bir şey *«bilinmiyor»* diye
> yazılmıştır. Bir rapor, en çok kendi bilmediğini gizlediğinde yanıltır.

---

## 0 · YÖNETİCİ ÖZETİ — üç cümlede

1. **Ürün kötü değil; ÖLÇÜM ALETİ ürünün üçte birini ölçüyor.** Gerçek trafikte
   sorulara **route %35,5**, **garson %37,0** cevap veriyor — ama tam kapının ölçtüğü
   korpus **yalnız route'u** ölçüyor. Kapının kendi yorumu bunu yazıyor:
   *«`garson` HİÇBİR TOPLU KOŞUMDA YOK — ne yerelde ne `--hepsi`'de.»*
2. **Korpus 14.957 tur gibi görünüyor, aslında 590 semantik vaka.** Kendi raporunun
   ifadesiyle *«şişme katsayısı 28,0×»*. Yani yeşil bir kapı, 590 vakanın yeşilliğidir.
   Her yeni 20'lik curl turunun 4-5 yeni kök bulması bu yüzden **beklenen** bir sonuçtur,
   bir sürpriz değil.
3. **Gerçek trafiğin %21,8'i cevapsız kalıyor** (`source=None`). Rakiplerin en zayıf
   yanı sayılan *«her soruya bir şey söyle»* bizde ölçülmüş bir açık.

---

## 1 · NEREDEYİZ — ölçülmüş tablo

### 1.1 Gerçek trafik hangi basamakta bitiyor

`interaction_log`, **3.554** kayıt (canlı kullanım):

| basamak | `source` | adet | pay | kapı ölçüyor mu? |
|---|---|---|---|---|
| **garson** (Intent-JSON) | `cube+llm` | 1.316 | **%37,0** | 🔴 **HAYIR** |
| **route** (0 LLM) | `cube` | 1.260 | **%35,5** | ✅ evet (korpus) |
| **cevapsız / netleştirme** | `None` | 776 | **%21,8** | ◐ kısmen |
| meta / katalog | `meta` `catalog` | 132 | %3,7 | ✅ |
| **Discovery** (ham SQL) | `llm:*` | 59 | %1,7 | 🔴 hayır |
| VQR · yükleme · doğrulama | — | 11 | %0,3 | ◐ |

⊙ **Sonuç:** kapı, ürünün **%35,5'ini** ölçüp *«YEŞİL»* diyor. Kullanıcının
*«her 20 soruda ciddi sorun çıkıyor»* gözlemi, ölçülmeyen **%64,5**'ten geliyor.

### 1.2 Korpusun gerçek büyüklüğü

`lab/reports/nl_corpus.md`'nin **kendi** satırları:

| şirket | ham tur | 🔴 cevapsız | **semantik vaka** | şişme |
|---|---|---|---|---|
| boyahane | 9.413 | 1.431 (%15,2) | **336** | 28,0× |
| atiksan | 1.447 | 413 (%28,5) | **68** | 21,3× |
| gulteks | 1.618 | 479 (%29,6) | **83** | 19,5× |
| gitas | 2.479 | 657 (%26,5) | **103** | 24,1× |
| **TOPLAM** | **14.957** | **2.980 (%19,9)** | **590** | **~25×** |

⚠ *«doğru=95»* manşeti bir **uçtan uca doğruluk değildir**: raporun kendi tanımıyla
*«DOĞRU CUBE: 7210/7519»* — yani **SQL üretebilmiş** turlar içinde doğru küp oranı.
Cevapsız kalan %19,9 bu paydanın **dışındadır**.

### 1.3 Sistemin büyüklüğü

| | ölçü |
|---|---|
| backend uygulama | **148 modül · 53.725 satır** (34.945 kod + 11.594 yorum + docstring) |
| test | **374 dosya · 66.546 satır** — uygulamanın **1,24 katı** |
| belge | **34 belge · 47.230 satır** |
| en büyük iki modül | `ask.py` **5.935** · `cube_router.py` **4.807** |
| `ask()` tek fonksiyon | **1.416 kod satırı** (tavan 1.414, 7 muafiyetle) |
| kod içi `§` kural işareti | **131 farklı işaret** |
| büyüme tavanı muafiyeti | **120 kayıt** (4 ayrı liste) |

⊙ Ürünün etrafındaki iskele (test + belge = 113.776 satır), ürünün kendisinin
(53.725) **2,1 katı**. Bu bir kalite işareti **de** olabilir, bir ağırlık işareti **de**.
Ayıran şey: iskele ürünün **hangi kısmını** tutuyor? Yukarıdaki tabloya göre: **%35,5'ini**.

### 1.4 Garsonun ölçümü

* `lab/reports/garson_korpusu.md` → **payda 21** ve kendi notu: *«⚠ kayıt kümesi —
  «korpus %» değil»*.
* `lab/kapi.py:375` → *«🔴 `garson` HİÇBİR TOPLU KOŞUMDA YOK»*.
* `garson_kararlilik.json` → 25 senaryo, kararlılık **1,0** (yani **tutarlı**, ama
  tutarlılık doğruluk değildir — aynı cevabı üç kez vermek onu doğru yapmaz).

🔴 **Trafiğin %37'sini taşıyan basamağın otomatik doğruluk ölçümü YOKTUR.** Bu, bu
belgedeki önemli bulgudur.

---

## 2 · GRAFİK MESELESİ — iddia ve ölçüm

**İddia:** *«biz daha grafik oluştururken binlerce hata alıyoruz.»*

**Ölçüm (canlı, 10 senaryo, tek tek):**

| soru | dönen | doğru mu |
|---|---|---|
| «bu yıl makine bazında toplam üretim» | `bar` | ✅ |
| «aylık ciro trendi» | `line` | ✅ |
| «makine ve vardiya bazında oee» | `heatmap` | ✅ |
| «bu yıl toplam ciro» | `kpi` | ✅ |
| «müşteri bazında ciro ve fire oranı» | `scatter` | ✅ |
| «aylık üretim ve enerji tüketimi» | 2 bölümlü belge + `line` | ✅ |
| «makine bazında oee ve fire oranı» | `scatter` | ✅ |
| «müşteri bazında ciro» | `bar` | ✅ |
| «vardiya bazında duruş nedeni dağılımı» | `heatmap` | ✅ |
| «aylık makine bazında üretim» | `line` | ✅ |

⊙ **10/10 doğru grafik tipi. Tek bir «çizilmedi» yok.**

⚠ Ve iki hipotezim **çürüdü**:
* *«backend `facet_measure`/`waterfall` üretiyor, ön-uç tanımıyor»* → ön-uç **ikisini de**
  tanıyor (`lib/chart.ts`, `lib/types.ts`).
* *«çizilemeyen grafik sessizce tabloya düşüyor»* → düşüyor ama **gerekçesiyle**
  (`viz.cizilmedi` → *«ⓘ grafik yerine tablo — <sebep>»*).

🔴 **Yani grafik katmanı sistemin EN SAĞLAM parçalarından biri.** Kullanıcının yaşadığı
*«grafik hatası»* deneyimi büyük olasılıkla grafiğin kendisi değil, **grafiğin gösterdiği
şeyin yanlış/eksik olması** — yani üstteki basamakların kusuru. Bir grafik, yanlış bir
sorgunun üstüne doğru çizildiğinde de yanlış görünür.

*Bir belirtiyi yanlış organa yazmak, tedaviyi de yanlış yere yapar.*

---

## 3 · «EN KÖTÜ PROMPTTA BİLE CEVAP» — ölçüm

Altı zayıf/konuşma dilinde soru, tek tek:

| soru | sonuç |
|---|---|
| «fabrika nasıl gidiyor» | ✅ 6 adımlık plan, 11 satır |
| «en kötü makine hangisi» | ✅ cevap (dönem varsayımı beyanlı) |
| «hangi müşteriyle çalışmayı bırakmalıyız» | ✅ cevap |
| «işler iyi mi» | 🔴 **cevap yok** — *«ekranda sayı yok»* |
| «bu ay ne oldu» | 🔴 **cevap yok** — *«Hangi ölçüyü istiyorsun?»* |
| «kısaca özetle» | 🔴 **cevap yok** — *«ekranda rapor yok»* |

⊙ **3/6 cevapsız.** Üçü de *bağlamsız açılış* sorusu. Rakiplerin en görünür üstünlüğü
tam burada: **bir şeyle başlarlar.** Bizim üç reddimiz de *dürüst* ama kullanıcı için
sonuç aynı: ekran boş.

⚠ Ve bu, korpusun ölçtüğü **%19,9 cevapsız** oranının canlı karşılığıdır.

---

## 4 · MİMARİ TEŞHİS — «ters yatırım»

Kullanıcının cümlesi: *«garson mantığımız, mimarimiz, logic'imiz iyi değil gibi; AI
mühendisi değiliz sonuçta.»* Bu bölüm o cümlenin **ölçümüdür**.

### 4.1 Emek nereye gitti

| basamak | trafik payı | yazılmış kod |
|---|---|---|
| **route** — deterministik Türkçe NL→CubeQuery | **%35,5** | **8.861 satır** (`cube_router` · `niyet` · `followup` · `uyum` · `deger_capasi` · `turetme` · `islev_sozcukleri`) |
| **garson** — Intent-JSON hakemi | **%37,0** | orkestratör *koşumu* dâhil 5.701 satır; ama **hakemin kendi istemi: 45 kod satırı** |

⊙ **Makineye Türkçe öğretmek için 8.861 satır yazdık; trafiğin daha büyük kısmını
taşıyan hakemi 45 satırlık bir istemle yönetiyoruz.**

Ve bu, mimarinin **kendi en üst kuralıyla** çelişiyor. `CLAUDE.md` şöyle diyor:

> *«Route'a — yani NLP'ye — Türkçe öğretmemiz gerekir ki bu gereksiz. … İntent
> algılamada asıl **LLM'e** güveniyoruz.»*

Kural doğru yazılmış, **yatırım tersine yapılmış**. 131 `§` işareti, 120 büyüme
muafiyeti ve `ask()`in 1.416 satırı bu tersliğin faturasıdır.

### 4.2 Garsonun eksik olduğu şey: **BAĞLAM**

Garsonun istemine bugün giren tek şey:

```
statik katalog dökümü (23.729 karakter · 23 küp) + kullanıcının sorusu
```

**Girmeyenler:**

| eksik | ne işe yarardı | bizde var mı |
|---|---|---|
| **örnek sorgular** (few-shot / retrieval) | modele *«bu şirkette böyle sorulur, karşılığı budur»* demek | 🔴 hayır — `vqr.py` **var** ama yalnız *replay* basamağında (ladder #2), garsona **beslenmiyor** |
| **iş sözlüğü / talimatlar** | *«biz fire'yi kg konuşuruz»*, *«gerçekleşme = …»* | 🔴 hayır (yalnız `SynonymOverride`) |
| **şema daraltma (schema linking)** | 23 küpün tamamı yerine ilgili 2-3'ünü göstermek | 🔴 hayır — **her soruda 23.729 karakterin tamamı** gidiyor |
| **çalıştır → hatayı gör → düzelt döngüsü** | üretilen sorgu patlarsa modele hatayı geri vermek | ◐ kısmen — `plan_garson`'da **tek** bir *«DÜZELTME TURU»*; `llm.py`'deki yeniden denemeler yalnız **boş yanıt** içindir |
| **kararlılık ölçümü ≠ doğruluk** | — | `garson_kararlilik.json` **1,0** diyor; ama üç kez aynı cevabı vermek onu doğru yapmaz |

🔴 **Ve en can sıkıcı olan:** kullandığımız motorun kendisi (**Wren AI**) bu katmanı
zaten sunuyor. Wren'in mimarisinde `instructions.md` (iş bilgisi) + `queries.yml`
(örnek sorgular) + **LanceDB hibrit erişim** olan bir **AI Context Layer** var. Biz
Wren'in **motorunu ve MDL'ini** aldık, **AI bağlam katmanını almadık** — ve onun yerine
8.861 satır Türkçe kural yazdık.

*Bir kütüphanenin en pahalı parçasını yeniden yazmak, onu kullanmamanın en pahalı
biçimidir.*

### 4.3 Neden her 20 soruda yeni kök çıkıyor — sayısal cevap

Son beş turun ölçümü:

| tur | senaryo | yeni kök |
|---|---|---|
| CC | 26 | 4 |
| DD | 22 | 4 |
| EE | 12 | 3 |
| FF | 5 | 1 |
| GG | 4 | 1 |

⊙ **Oran ~5 senaryoda 1 kök ve DÜŞMÜYOR.** Olgunlaşan bir sistemde bu oranın azalması
beklenir. Azalmıyorsa, sonlu bir kusur havuzu boşaltılmıyor demektir — **kombinatoryal
bir uzay örnekleniyordur**:

```
23 küp × ~8 ölçü × ~7 boyut × 6 soru türü × 4 yol × 5 tur tipi × beyan sınıfları
```

Bu uzayın büyüklüğü **on binlerce** hücredir. Elle yazılmış her kural **bir hücreyi**
kapatır. 131 işaret, on binlerce hücrenin 131'i demektir.

🔴 **Bu bir disiplin sorunu değil, bir YÖNTEM sorunudur.** Aynı hızla devam edersek
kusur bulma oranı da aynı kalır — çünkü her tur uzayın yeni bir bölgesini yokluyor.

### 4.4 Mimarinin doğru olan yanları — bunlar korunmalı

Rapor dengeli olmalı; ölçüm şunları da söylüyor:

* **Grafik katmanı sağlam** (10/10 doğru tip, gerekçeli düşüş) — bkz. §2.
* **Sayıyı her zaman küp koyar; LLM SQL yazmaz.** Bu, sektörün *«silently wrong»* diye
  adlandırdığı en pahalı hata sınıfına karşı gerçek bir savunmadır.
* **Beyan kültürü** (*«sayı doğru ama eksik»*, *«bu bir varsayımdır»*) — rakiplerin
  çoğunda **yok**; sessizce tahmin ederler.
* **Kök-neden motoru** (`§KN`) formülü katalogdan okuyup log-uzayında ayrıştırıyor ve
  en dip alt-segmente iniyor. Bu, sektörde *«contribution / mix analysis»* denen şeyin
  doğru uygulanmış hâlidir ve çoğu üründe yalnız **zamansal** karşılığı vardır.
* **Kendi kendini denetleyen kapılar** — bu oturumda dört kez kendi teşhisim çürüdü ve
  dördünü de kapılar yakaladı (JOIN budaması · `F821` · yüzde toplama · zengin gövde).

*Kötü olan mimari değil, mimarinin ağırlığının dağılımı.*
