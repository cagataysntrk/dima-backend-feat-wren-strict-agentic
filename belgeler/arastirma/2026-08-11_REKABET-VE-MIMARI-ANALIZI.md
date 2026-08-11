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

---

# İKİNCİ KISIM — SEKTÖR

## 5 · SEKTÖR ÜÇ MİMARİ KAMPA AYRILDI

| kamp | LLM ne üretir | kim | ölçülen sonuç |
|---|---|---|---|
| **A · yapılandırılmış niyet nesnesi** (LLM **SQL yazmaz**) | arama token'ı / TML / `DataQuery` JSON | **ThoughtSpot**, **Google Looker**, dbt Semantic Layer, Qlik | en yüksek doğruluk; kapsam dışında **hata mesajı** |
| **B · semantik-model kısıtlı SQL** | SQL/DAX, doğrulayıcıdan geçerek | **Snowflake Cortex**, **Databricks Genie**, **Power BI Copilot**, Zenlytic | orta-yüksek; kapsam dışında **makul ama yanlış** |
| **C · ham şemaya serbest SQL/Python** | doğrudan SQL/Python | **Amazon Quick Sight (yeni)**, Julius AI, Hex geri-düşüşü | kurumsal şemada **%10 bandı** |

🔴 **DİMA A kampındadır** — ThoughtSpot ve Google ile aynı tarafta. ThoughtSpot bunu birebir
savunuyor: *«If relational search tokens are correct, **SQL is 100% accurate**»*. Google
`DataQuery` JSON üretir, SQL'i **Looker** derler.

⊙ **Ve bu tercihin bağımsız ölçümü var** (lkr.dev, 44 iş sorusu, 3 koşum):

| | Looker semantik katman | BigQuery doğrudan SQL |
|---|---|---|
| doğruluk | **%97** | **%80** |

**En öğretici kısmı:** Looker'ın 4 hatası **hiçbiri 3/3 koşumda** tekrarlamadı (gürültü).
BigQuery'nin **7 hatası 3/3 koşumda tekrarladı** — yani **sistematik**, prompt
iyileştirmesiyle kapanmaz.

*Bizim mimari tercihimiz sektörün kazanan tarafında. Sorun tercih değil, uygulama.*

## 6 · ON ÜÇ ÜRÜN — çapraz tablo

| ürün | LLM ne üretir | semantik katman | **yayınlanmış doğruluk** | belirsizlikte | grafik seçimi |
|---|---|---|---|---|---|
| **Snowflake Cortex** | SQL (6 ajan) | **zorunlu** | **%90+** (150 soru); BIRD **57→78** | 🟢 **reddeder** + öneri | yok (tüketiciye bırakır) |
| **Databricks Genie** | SQL (ajan topluluğu) | instructions + certified + Ontology | **%84,5** vs %52,4 — ⚠ **28 soru** | sorabilir, garanti yok | LLM; **düzenlenemez** |
| **ThoughtSpot** | **token/TML — SQL değil** | **zorunlu** | 🔴 **YOK** | token'ları gösterir | tip **korunur** |
| **Power BI Copilot** | DAX | semantik model | 🔴 **YOK** (bağımsız: **%62,5**) | 🔴 **sormaz**; kapsam dışında **LLM genel bilgisi** | LLM |
| **Tableau Pulse** | **yalnız cümle** | metrics layer | 🔴 YOK | — | **14 deterministik içgörü tipi** |
| **Looker CA** | **`DataQuery` JSON** | LookML | "**2/3 hata azalması**"; bağımsız **%97 vs %80** | 🟢 disambiguation (Mar 2026) | belgelenmemiş |
| **Amazon Quick** | **ham SQL (JOIN dâhil)** | Topics (≤12 veri seti) | 🔴 YOK | 🔴 sormaz | belgelenmemiş |
| **Qlik** | **hiçbir hesap — yalnız NLG** | Business Logic (ağır) | 🔴 YOK | 🔴 sormaz | **deterministik katalog** |
| **Sisense** | sorgu (**sonucu görmez**) | NLQ model | 🔴 YOK | 🟢 tıkla-ayrıştır UX | LLM, 10 tip |
| **Zenlytic** | **serbest SQL + sonradan doğrulama** | context layer | 🔴 YOK ("10x") | şartlı sorar | LLM |
| **Hex Magic** | SQL/Python + insan denetimi | dbt/Cube senk. | 🔴 YOK (eval altyapısı var) | 🟢 **en açık sorar** | 12 tip |
| **Julius AI** | Python | **yok** | ⚠ kaynaksız "%31" | sormaz | LLM |

### 6.1 Dört bulgu

**(a) 13 üründen yalnız ÜÇÜ doğruluk sayısı yayınlıyor.** Snowflake (%90+, 150 soru),
Databricks (%84,5, **28 soru** — ±13 puan güven aralığı), Google (dolaylı "2/3").
ThoughtSpot · Microsoft · Tableau · AWS · Qlik · Sisense · Zenlytic · Hex — **hiçbiri**.
⊙ *Ölçülmüş bir sayı yayınlamak, taklit değil öncülüktür.*

**(b) Microsoft'un en tehlikeli tasarım kararı, belgelenmiş hâliyle:**
> *«When a question is related to data in the semantic model, Copilot uses the semantic
> model… **Otherwise, it might answer from the large language model's (LLM's) general
> knowledge.**»*

Yani kapsam dışında **reddetmiyor, uyduruyor**. Uygulamacı eleştirisi birebir:
> *«**it doesn't tell you when it can't answer your actual question. It answers a
> different, easier question and presents it as if that's what you asked.**»*
> *«Copilot generated the DAX in 3 seconds. **It took me 45 minutes to fix what it got
> wrong.**»*

**(c) LLM-öncesi deterministik NLQ motorları PİYASA TARAFINDAN ÖLDÜRÜLDÜ.**
Tableau **Ask Data** → Şubat 2024'te emekli. Power BI **Q&A** → **Aralık 2026'da
kalkıyor**, *«synonyms, linguistic relationships, row labels, teach Q&A»* dâhil **tüm
dilbilimsel şema araçları** ile birlikte.
🔴 **Bu bizi doğrudan ilgilendiriyor:** *«kullanıcı sözlüğü elle beslesin»* modeli iki dev
tarafından terk edildi. Bizim 8.861 satırlık Türkçe kural yığınımız o modelin bir
akrabasıdır.

**(d) Qlik'in dersi — mükemmel motor, kullanılmayan ürün.** Motoru determinizm açısından
kusursuz (*«all analytical calculations are still generated by the trusted Qlik engine»*),
ama Business Logic kurulum vergisi benimsemeyi öldürmüş. Kendi topluluğundan:
> *«I couldn't find **a single company that was using this resource** in their day-to-day»*
> *«Business logic is too complex… **no one want to waste time on it**»*

Forrester: BI'da elle kullanım **%20 tavanında**; doğal dilin katkısı **yalnız +10 puan**.

## 7 · ÖLÇÜLMÜŞ GERÇEK — text-to-SQL nerede

### 7.1 Benchmark çöküşü

| benchmark | SOTA | insan | not |
|---|---|---|---|
| **Spider 1.0** | %91,2 | — | "çözülmüş"; liderlik tablosu 2023'ten beri donmuş |
| **BIRD** | **%81,95** | **%92,96** | 11 puanlık açık **10 aydır kapanmıyor** |
| **Spider 2.0** (ajanik) | **%21,3** (o1-preview) · GPT-4o **%10,1** | — | şema **27 → 800 sütun** |
| **BEAVER** (MIT/Stonebraker) | **%10,8** | — | gerçek **özel** veri ambarı |
| **Archer** (muhakeme) | **%6,73** | — | aynı yöntem Spider'da %85,3 |
| **BIRD-INTERACT** (çok turlu) | GPT-5 **%8,67** (konuşma) / %17,00 (ajanik) | — | belirsizlik + çok tur eklenince çöküyor |

Stonebraker (CACM, Tem 2026): *«a pure LLM generated an accuracy score of **zero**. Adding
RAG, prompt engineering, and agentic AI raised accuracy to the **10+% range**.»*

⚠ **Ve bağımsız ölçüm liderlik tablolarını düşürüyor:** AIMultiple (Ağu 2026), 759 BIRD
sorusu, ipuçsuz, sıfır-atış → en iyi model **0,551**. Liderlik tablosu %82 ↔ gerçekçi ~%55.
Üstelik **BIRD gold sorgularının %31,1'i bozuk işaretlenmiş**.

### 7.2 Hata taksonomisi — ölçülmüş dağılım

4.602 hatalı SQL elle incelendi (~840 kişi-saat, arXiv 2501.09310):

| | BIRD | Spider |
|---|---|---|
| gerçek hata içeren sorgu | **%47,8** | %26,8 |
| **semantik hata** | **%36,1** | %17,7 |
| biçim hatası | %26,0 | %25,8 |

🔴 **Çalışma-zamanı çökmeleri hataların yalnız küçük dilimi** (%18,8 sözdizimi, %81,2 şema).
**Çoğunluk sessizce çalışıp yanlış sonuç veriyor.**

**LinkedIn üretim ölçümü** (arXiv 2507.14372): **derleme %96 · geçerli tablo&sütun %99 ·
DOĞRU %53.** Aradaki **~43 puan tanımı gereği sessizdir.**

### 7.3 «Çalıştı mı?» doğrulaması işe yaramıyor — AUROC 0,500

arXiv 2607.06799, selective-prediction çalışması:

| sinyal | AUROC |
|---|---|
| **query executability** | **0,500 — tam şans** |
| execution self-consistency | 0,613 |
| string self-consistency | 0,675 |
| GPT-4o hakem | 0,770 |
| **iki-sağlayıcılı hakem topluluğu** | **0,822** (ECE 0,031) |

🔴 **Bizim `dry_plan`'ımız da bu sınıftadır: sorgunun çalışması doğruluk hakkında SIFIR
bilgi taşır.** Ve self-consistency (bizim `k=3` oylamamız) tavanı ~0,675 — CHASE-SQL'in
ölçümü: oylama %68,84, **eğitilmiş seçici %73,01**, oracle tavanı **%82,79**.
⊙ *Darboğaz aday üretimi değil, **SEÇİM**.*

**Çekimserlik gerçeği:** %20 risk hedefinde self-consistency soruların yalnız **%1'ini**
geçirebiliyor; iki-sağlayıcılı topluluk %27. Ve **AbstentionBench**: muhakeme modelleri
çekimserlikte ortalama **%24 daha KÖTÜ**; ölçek büyütmek çekimserliği **iyileştirmiyor**.

### 7.4 Semantik katman — dört bağımsız ölçüm, aynı yön

| çalışma | ham şema | semantik katman | fark |
|---|---|---|---|
| Sequeda ve ark. (2023) | %16,7 | **%54,2** | 3,2× |
| Snowflake (BIRD alt kümesi) | %57 | **%78** | +21 |
| AtScale (2024) | %20 | **%92,5** | +72,5 |
| Cube.dev (2026, n=100, p<0,002) | %45,5–50,5 | **%67,7–68,7** | +17…+23 |
| dbt Labs (2026) | %84,1–90,0 | **%98,2–100,0** | +8…+16 |

**Cube'un en önemli cümlesi:** *«**Whether the model has the semantic layer matters more
than which model it is**»* — ve o kazanç **4 KB markdown**'dan geliyor.

**dbt'nin en önemli cümlesi:**
> *«With text-to-SQL, failure looks like **a plausible but incorrect answer**. With the
> Semantic Layer, failure looks like **an error message**.»*

⚠ **Ama semantik katman doğruluk değil, KAPSAM × doğruluk takası satıyor.** dbt'nin kendi
verisi: kapsam **içinde** SL %100 / T2SQL %50; kapsam **dışında** SL **%0** / T2SQL %100.
⊙ Bu tam olarak bizim *«dürüst red»* ↔ *«cevapsız %19,9»* gerilimimizin sektördeki adıdır.

### 7.5 Belirsizlik — sormak ölçülebilir biçimde kazanıyor

* **Kullanıcı sorularının %41,1'i belirsiz** (Microsoft/CIDR 2024, KaggleDBQA).
  İki insan anotatör arasındaki uyum bile yalnız **%62**.
* Belirsiz sorularda model recall **%27–31**, belirsiz olmayanlarda **%63–66** —
  **35 puanlık uçurum** (AMBROSIA).
* **Tüm meşru yorumları bulma (AllFound): GPT-4o %0,4 · Llama3-70B %1,9.**
  🔴 Modeller belirsizliğin **farkında bile değil**; tek yoruma kilitlenip kesin sunuyorlar.
* **AmbiSQL** (netleştirme soran sistem): **%42,5 → %92,5** (+50 puan, n=40).

Hacker News'ten, bizim doktrinimizin dışarıdan ifadesi:
> *«**the answer a business user needs is rarely the answer to the question they initially
> ask.** Asking for clarification, pushing back on poorly framed asks — **that's where most
> of the value comes from.** LLMs are still **too eager to jump into the code**.»*

## 8 · TÜRKÇE — ölçülmüş vergi ve ölçülmüş hendek

### 8.1 BIRDTurk (SIGTURK 2026, ODTÜ + Roketsan) — bizim için en önemli dış kanıt

BIRD'ün tamamı Türkçeye çevrildi (**12.751 soru, 95 DB**), **şema tanımlayıcıları da**
Türkçeleştirildi, çeviri doğruluğu **%98,15**.

| yöntem | BIRD (EN) | **BIRDTurk (TR)** | kayıp |
|---|---|---|---|
| doğrudan istem (ICL) | %58,21 | %43,16 | **−15,05 puan** |
| **DIN-SQL (ajanik)** | %60,89 | %49,02 | **−11,87 puan** |

🔴 **Türkçe 12-15 puan yakıyor — ve ajanik/yapılandırılmış muhakeme bu vergiyi ~3 puan
azaltıyor.** Yani **orkestratör yatırımımız hakemli bir yayınla doğrulanmış durumda.**

**Ölçülen üç mekanizma:** (1) SOV + mantığın **eklere dağılması**; (2) kelime sayısı
**−%27,3** → sözcüksel seyreklik; (3) tokenizasyon vergisi **+%9,3**.

⊙ **Ve teşhis cümlesi bizim için kritik:** *«İngilizce benchmark'larda **MASKELENEN**
muhakeme ve grounding başarısızlıklarını ortaya çıkarıyor»* — yani **Türkçe yeni hata
üretmiyor, İngilizcede gizlenen hataları görünür kılıyor.**

⚠ Fine-tuning ölçümü: mT5 ailesi Türkçede **%2'nin altında** (pratikte çalışmıyor);
Qwen2.5-Coder-3B **%15,38**.

### 8.2 Türkçe gerçek bir hendektir — rakiplerin ölçülmüş durumu

| ürün | Türkçe |
|---|---|
| **Gemini in Looker** | 🔴 *«supports **English-language prompts and responses only**»* |
| **Fabric Data Agents** | 🔴 *«İngilizce dışı dil desteklenmiyor»* |
| **Power BI Copilot** | 🔴 *«The only supported language is English»* |
| **Qlik Answers** | 🔴 yalnız İngilizce |
| **Tableau Agent** | ◐ Türkçe prompt kabul ediyor, **İngilizce cevap veriyor** |

⊙ **Türkçe morfoloji yatırımı savunulabilir bir konumdur** — ama §4.1'deki ters yatırım
uyarısıyla birlikte okunmalı: 8.861 satır **route'a**, 45 satır **garsona**.

## 9 · GRAFİK — rakiplerin «basit grafiği tutturması» nasıl oluyor

### 9.1 Kırk yıllık tek fikir

Mackinlay APT (1986) → **expressiveness** (ifade edilebilirlik: geçersiz kodlamaları
**ele**) + **effectiveness** (algısal etkinlik: kalanları **sırala**). Tableau *Show Me*
(2007) bunun ürünleşmiş hâli. ⊙ Rakiplerin *«sihri»* yayınlanmış literatürdür.

⚠ **Ama kural setlerini SAKLIYORLAR:** Amazon AutoGraph *«uses the most appropriate visual
type»* diyor, tabloyu vermiyor. Power BI quick-create *«automatically plots meaningful
charts»* — sıfır kural. SpotIQ ve Google Sheets Explore kapalı.
🟢 **Açık ve tam tek kural seti Draco'dur** (MIT) + Observable Plot kaynağı (ISC).

### 9.2 Draco'nun HARD kısıtları — bizim doğrudan kullanabileceğimiz «kırmızı çizgiler»

```prolog
hard(stack_without_summative_agg)  % yığınlama YALNIZ count/sum/distinct ile — avg/ratio YASAK
hard(bar_area_without_zero)        % bar/area ekseni sıfırdan başlamalı
hard(area_bar_with_log)            % log ölçekli bar/area — "often misleading"
hard(size_nominal)                 % nominal veride size kanalı (sıralama ima eder)
hard(size_negative)                % negatif veride size
hard(shape_with_cardinality_gt_eight)      % shape tavanı 8
hard(color_with_cardinality_gt_twenty)     % renk tavanı 20
```

🔴 **`stack_without_summative_agg` bizim bu oturumda yaptığımız hatanın tam panzehiri:**
`§KN-toplam`'ı kapısız yazınca **yüzdeleri topladım** ve *«ilk seferde tamam toplamının
%11,8'ini taşıyor»* diye anlamsız bir cümle üretti. Draco bunu **hard hata** sayıyor.
*Bizim ölçümle bulduğumuz kuralı, literatür 2018'de yazmış.*

**Algısal sıralama (Draco-APT, makine-okunur):**
```
nicel:   x/y (1) > size (2) > color (3)
nominal: x/y (1) > color (2) > shape (3) > size (4)
```

### 9.3 Klasik arıza modları ve engelleme mekanizmaları

| arıza | mekanizma |
|---|---|
| çok fazla kategori | `horizontal_scrolling` (ağırlık 20) |
| pasta >7 dilim | Draco pastayı **hiç desteklemiyor** (kasıtlı); renk tavanı 20, shape 8 |
| zaman serisi bar olarak | `temporal_y`: zamanı x'te tercih et; Plot: `isMonotonic(X)` → **line** |
| tek eksende karışık birim | Draco'da **dual-axis yok** — layer/facet kullan |
| **yüzdelerin toplanması** | **HARD hata** |
| kesik eksenli bar | **HARD hata** |
| kova patlaması | `bin_high` ≤12 + `bin_low` >7 → **hedef 8-12** |
| spagetti çizgi | Plot: `isHighCardinality(C)` (tekil oran >%50) → seri gruplaması **kapat** |
| **sıralama kararsızlığı** | Vega-Lite varsayılanı **alfabetik**; `sort` verilmezse veri değişince sıra oynar |

⊙ **Son satır bizim bu oturumda `§SB` ile ölçüp düzelttiğimiz kusurun ta kendisi.**

### 9.4 «Kullanıcı pasta istedi ama veri zaman serisi» — literatürün üç çözümü

1. **Draco/ASP:** kullanıcı isteği **soft**, veri uyumu **hard**. Çelişkide çözücü en yakın
   geçerli alternatifi üretir.
2. **CompassQL:** kısmi spesifikasyonu sabitle, kalanı say, çelişkide gevşet + cezalandır.
3. **Show Me:** uygun olmayan tipleri **gri** göster, en iyisini turuncu çerçevele.

🟢 **Bize önerilen:** #1 + #3 karması → *«Pasta çizemiyorum: seçilen alan bir tarih ve 24
farklı değer var (pasta tavanı 7); çizgi çizdim»* — **bir red değil, gerekçeli ikame.**
*Bu, «dürüst red başarı değil» kuralımızın grafik karşılığıdır.*

### 9.5 🔴 TÜRKÇE BİÇİMLENDİRME — ölçülmüş dört tuzak

Ajan bunları **Node/ICU ile fiilen koşturarak** doğruladı:

```
Intl.NumberFormat("tr-TR",{style:"percent"}).format(0.5555)   → "%56"      ← işaret ÖNDE, 0 ondalık
Intl.NumberFormat("en-US",{style:"percent"}).format(0.5555)   → "56%"
Intl.NumberFormat("tr-TR",{notation:"compact"}).format(12345) → "12 B"     ← B = BİN (10³)
Intl.NumberFormat("tr-TR",{notation:"compact"}).format(1234567890) → "1,2 Mr"
```

| tuzak | sonuç |
|---|---|
| **yüzde işareti Türkçede ÖNE gelir** | elle `değer + "%"` yazan her kod yanlış |
| **yüzde varsayılanı 0 ondalık** | `%55,55` sessizce `%56` olur — görünmez veri kaybı |
| **kompakt `B` = «bin»**, İngilizcede «billion» | `12 B` bir İngilizce okurda **12 milyar** |
| 🔴 **`d3-format`'ta `tr-TR` locale'i YOK** | 59 locale var, Türkçe **yok** → Vega-Lite/D3/Plot **varsayılan `en-US`**: `1,234.56` |

⊙ Bizim `app/sayi_bicimi.py`'miz bu oturumda tam da bu yüzden doğdu (beş ayrı
biçimlendirici bulunmuştu). Ama **ön-uç tarafı (ECharts/Vega) ölçülmedi** — açık borç.

## 10 · KÖK-NEDEN — rakip algoritmalar ve bizim konumumuz

### 10.1 Önce ayrım: iki farklı soru

| soru | tip | algoritmalar |
|---|---|---|
| *«bu ZAMAN İÇİNDE neden değişti»* | değişim atfı | **Adtributor**, HotSpot, Squeeze/PSqueeze, iDice, **LMDI**, PVM |
| *«bu SEGMENT akranlarından neden farklı»* | kontrast | Key Influencers, Explain Data, **DIFF/MacroBase** (= Sisu), Scorpion |

🟢 **Bizde ikisi de var:** `contribution.py` (zamansal) + `kok_neden.py` (kesitsel).
Sektörde çoğu üründe **yalnız zamansal** karşılığı var.

### 10.2 Adtributor (NSDI 2014) — ve bizim eksik yarımız

**Explanatory power** `EP = (A−F)/(A_top−F_top)` + **Surprise** = Jensen-Shannon diverjansı.
Üretim eşikleri: `T_EP=%67`, `T_EEP=%10`, **top-3**. 128 gerçek anomalide **>%95 doğruluk**.

🔴 **Sürprizin neden şart olduğu — kurucu örnek (bizi doğrudan ilgilendirir):**
Gelir 100$→50$ düştü. *Veri Merkezi X* düşüşün **%94'ünü** açıklıyor (en özlü!). Ama X
zaten hem tahminin hem gerçeğin %94'ü — **dağılımı değişmedi**. Gerçek kök neden
**Mobile+Tablet** (tahminin %25'i → gerçeğin %0'ı).

> **«Yalnız explanatory power kullanan her katkı analizi, büyük segmentleri sistematik
> olarak suçlar.»** — bu, *«en büyük müşteri hep suçlu çıkıyor»* şikâyetinin matematiksel
> adıdır ve bizim `§KN-toplam`'ımız **tam olarak bu tuzaktadır**: en büyük segmenti seçiyor,
> sürpriz hesaplamıyor.

**Oran ölçüleri için Adtributor §4** — sonlu farklarla kısmi türev:
```
EP = [ (ΔA₁)·F₂ − (ΔA₂)·F₁ ] / [ F₂ · (F₂ + ΔA₂) ]
```
Sezgisel karşılığı: *«herkes tahmini yapsaydı, yalnız bu eleman gerçekleşen değerini
verseydi ne olurdu»* — bir **ceteris paribus karşı-olgusalı**.

### 10.3 Bizim `§KN`'nin sektördeki adı ve konumu

`kok_neden.py`'nin yaptığı `ln(v_hedef) − ln(v_akran) = Σ[ln(f_i,hedef) − ln(f_i,akran)]`
işleminin **üç ayrı literatürde üç adı var**:

| ad | alan | not |
|---|---|---|
| **LMDI** (Ang 2005, *Energy Policy*, **1.582 atıf**) | enerji/ekonometri | **fiili standart** |
| **PVM** (price-volume-mix variance) | FP&A | ⚠ **sıra bağımlı**, artık üretir |
| **log-uzayı çarpımsal ayrıştırma** | genel | bizim uyguladığımız |

🟢 **LMDI'nin dört özelliği bizim uygulamamızda zaten var:** artık **sıfır**, **sıra
bağımsız**, toplamsal↔çarpımsal tutarlı, zaman-tersinir.
⚠ **Eksik olan:** `LMDI-I` **alt-grup toplanabilirliği** (çok seviyeli drill-down'da
katkıların toplanması) ve **sıfır/negatif değer politikası** (`ln(0)` tanımsız; negatifte
LMDI tanımsız → Shapley'e geçilmeli).

### 10.4 🔴 Rakiplerin bizde OLMAYAN iki şeyi

**(a) Çok-boyutlu kombinasyon araması.** Adtributor **layer-1'de kilitli**; kök neden
`(İstanbul, Mobil)` gibi **bileşik** ise doğruluğu **sıfıra düşüyor**. **HotSpot** bunu
MCTS + *ripple effect* ile çözüyor: **vakaların %95'inde F-skor >%90** (Adtributor ve
iDice'ta **<%15**). Lokalizasyon >1 saat → **<20 saniye**.
⊙ **Bizim `§KN` de layer-1'de.** `derinles()` tek bir ikinci boyut açıyor, kombinasyon
araması yapmıyor.

**(b) «Dış kök neden» tespiti.** **PSqueeze** (JSS 2023) *«sorun bu boyutların hiçbirinde
değil»* diyebiliyor — F1 **0,90**. Literatürde ilk.
⊙ Bu, bizim *«§NB — açıklanamadı»* beyanımızın **ölçülebilir** hâlidir.

### 10.5 🔴🔴 EN CİDDİ UYARI — çoklu karşılaştırma problemi

Zgraggen, Zhao, Zeleznik, Kraska (Brown/MIT), **CHI 2018**:

> **«In our experiment, over 60% of user insights were false.»**

Mekanizma: analist ne kadar çok görselleştirme incelerse, **rastgele veride** ilginç
görünen örüntüye rastlama olasılığı o kadar artar.

🔴 **Bizim kök-neden motorumuz her soruda YÜZLERCE hipotezi sessizce test ediyor**
(`_en_ayristiran` aday süpürmesi, `derinles` kombinasyonları, `contribution` segment
taraması). **FDR düzeltmesi (Benjamini-Hochberg) veya keşif/doğrulama ayrımı YOK.**
⊙ Power BI'ın ham `p<0,05` Wald eşiği de bu düzeltmeyi yapmıyor — yani **sektör de
yapmıyor**, ama bu bizi haklı çıkarmaz.

*Düzeltme olmadan ürettiğimiz «kök nedenlerin» önemli bir kısmı gürültüdür.*

### 10.6 Rakiplerin belgelenmiş yöntemleri

**Power BI Key Influencers** (en şeffaf satıcı): **ML.NET** · kategorik hedefte **lojistik
regresyon**, sayısalda **doğrusal regresyon**, top segments'te **karar ağacı** · **Wald
testi, p<0,05** · Pearson/Point-Biserial doğrusallık testi → gerekirse **denetimli
binleme, en fazla 5 kova** · **en az 100 gözlem** · 10.000 örneklem.
⚠ Kısıt: DirectQuery **desteklenmiyor**, RLS ile çalışmıyor, TopN/ölçü filtrelerinde
**sessizce devre dışı**.

**Tableau Explain Data:** beklenen aralık = tahminlerin **15.–85. persentili**;
`SUM(X) = COUNT(X) × AVG(X)` **çarpımsal ayrıştırması**; sıralama *«complexity ↔
variability»* dengesiyle.
⚠ Kendi dokümanı: *«Correlation is not causation… **not a tool to prove or disprove
hypotheses**»*.

**Tableau Pulse — bizim için en iyi model:**
> *«starts by using **standardized, deterministic statistical models** to detect facts…
> These facts are used as **ground truths** to contextualize language generation.»*

**14 deterministik içgörü tipi** var ve **LLM yalnız cümleyi kuruyor**. AI kapatılsa bile
içgörüler erişilebilir kalıyor. ⊙ *Bu, bizim `§KN` + `anlatici` ayrımımızın olgun hâlidir.*

**Sisu Data'nın çekirdeği açık:** kurucusu Peter Bailis; temeli **MacroBase + DIFF
operatörü** (VLDB 2019). Varsayılanlar: `support ≥ 0,01`, `risk ratio ≥ 2,0`,
**MAX ORDER = 3**, minimality.

---

# ÜÇÜNCÜ KISIM — WREN'DE OLAN AMA KULLANMADIKLARIMIZ

## 11 · MOTORUN 15 YETENEĞİNDEN **BİRİNİ** KULLANIYORUZ

Ölçüldü (canlı konteynerde `dir(wren_core)`):

```
Manifest · ManifestExtractor · Model · RemoteFunction · RowLevelAccessControl ·
SessionContext · SessionProperty · cube_query_to_sql · is_backward_compatible ·
migrate_manifest_json · to_json_base64 · to_manifest · validate_rlac_rule · wren_core
```

**Bizim kullandığımız:** `from wren_core import cube_query_to_sql` — **tek sembol.**

### 11.1 Kullanmadıklarımız ve karşılığında kendimizin yazdıkları

| Wren'de VAR | ne yapar (kendi dokümanından) | biz ne yazdık | satır |
|---|---|---|---|
| 🔴 **`ManifestExtractor.extract_by`** | *«Given a used dataset list, **extract manifest by removing unused datasets**. If a model is related to another dataset, both datasets will be kept. **The relationship between them will be kept as well.**»* | — (hiç yok) | **0** |
| 🔴 `ManifestExtractor.resolve_used_table_names` | *«parse the given SQL and return the list of used table names»* | — | 0 |
| **`SessionContext.dry_run`** | *«Dry-run SQL (EXPLAIN) to validate without executing»* | `wren_service.dry_plan` sarmalayıcısı | ~40 |
| **`SessionContext.register_csv/parquet`** | veri kaydı | `dataset.py` | **161** |
| **`RowLevelAccessControl` + `validate_rlac_rule`** | satır düzeyi erişim | `rls.py` | **380** |
| **`Manifest` / `to_manifest` / `migrate_manifest_json` / `is_backward_compatible`** | manifest yükleme, **göç**, geriye dönük uyum | `compose.py` + `mdl_writer.py` | **1.490** |
| `SessionContext.get_available_functions` | motorun desteklediği fonksiyonlar | elle | — |
| `RemoteFunction` | özel fonksiyon | — | — |

🔴 **`ManifestExtractor.extract_by` = ŞEMA DARALTMA (schema linking).** §4.2'de *«garsona
her soruda 23.729 karakterin tamamı gidiyor»* diye ölçtüğüm boşluğun çözümü **motorun
içinde, kullanılmadan duruyor.** Ve araştırma diyor ki şema bağlama hatası:
kurumsal ölçekte SQL hatalarının **%27,6'sı** (Spider 2.0), MultiSpider 2.0'da **%33,0**.

### 11.2 MDL'de tanımlı olup kullanmadıklarımız

Canlı MDL (`demo/wren-project/target/mdl.json`):

| | adet | kullanıyor muyuz |
|---|---|---|
| `models` | **80** | ◐ dolaylı |
| **`relationships`** | **31** | 🔴 **cube_router'da sıfır anma** — çapraz-küp *«blend»* ile yapılıyor, **gerçek JOIN değil** |
| `views` | 1 | 🔴 hayır |
| `cubes` | 23 | ✅ evet |

⊙ **31 tanımlı ilişki var ve çapraz-küp özelliğimiz onları kullanmıyor.** MIMARI.md'nin
kendi notu: *«blend, gerçek JOIN değil»*. Yani join yolu **beyan edilmiş** ama
**kullanılmıyor**.

### 11.3 🔴 Wren 7 Mayıs 2026'da mimarisini değiştirdi — biz yarım geçtik

* `Canner/wren-engine` **arşivlendi** (salt-okunur): *«merged into Canner/WrenAI under
  the `core/` directory»*.
* Yeni yapı: `core/` (Rust + `wren-core-py` + `wren-core-wasm`) · **`sdk/`**
  (`wren-langchain`, `wren-pydantic`) · **`skills/`** · **`evals/`**.
* Yeni boru hattı: `sqlglot → CTE rewriter → wren-core (Rust) → connector → PyArrow`.

**Bizim durumumuz:** `pyproject.toml` **doğru** tarafta (`wrenai>=0.13,<0.14` +
`wren-core-py>=0.7.3`).
🔴 **Ama kök `docker-compose.yml` hâlâ `ghcr.io/canner/wren-engine:latest` konteynerini
ayağa kaldırıyor** — **arşivlenmiş** bir depodan gelen, bir daha güncellenmeyecek imaj,
üstelik `latest` etiketiyle.
⊙ Ve bu oturumda ölçüldü: o konteyner **`Restarting (1)` durumunda** — yani zaten sağlıklı
çalışmıyor. *İki yol paralel koşuyor ve hangisinin canlı olduğu belirsiz.*

### 11.4 🔴🔴 EN AĞIR BULGU — Wren'in artık kendi `CubeQuery`'si var

`core/wren-core/core/src/mdl/cube.rs`:

```rust
pub struct CubeQuery {
    cube: String, measures: Vec<String>, dimensions: Vec<String>,
    time_dimensions: Vec<TimeDimensionFilter>, filters: Vec<CubeFilter>,
    limit: Option<usize>, offset: Option<usize>
}
```

`Granularity`: year|quarter|month|week|day|hour|minute
`FilterOperator`: eq, neq, in, not_in, gt, gte, lt, lte, contains, starts_with, is_null, is_not_null

**CLI:** `wren cube query --cube revenue --measures total --dimensions status
--time-dimension "order_date:month:2024-01-01,2025-01-01" --filter "status:eq:completed"`
— JSON girdi de alıyor, `--sql-only` ile dry-run.

Wren bunu belgesinde *«küçük modeller için **en yüksek kaldıraçlı doğruluk primitifi**»*
diye adlandırıyor.

⊙ **Bizim `CubeQuery`'miz ile aynı isim, neredeyse aynı şekil.** `cube_router.py`'nin
**4.807 satırının** bir kısmı motorun artık kendi yaptığı işi ikinci kez yapıyor olabilir.
**Bu ölçülmeli** — `wren cube query --sql-only` ile bizim `cube_sql` çıktımız yan yana
konabilir.

### 11.5 Wren'in **AI Context Layer**'ı — almadığımız asıl parça

Wren'in mimarisi **dört katman**: MDL semantik katman · **AI Context Layer** · Engine ·
Execution/UI.

**AI Context Layer'ın içeriği:**
* `instructions.md` — **iş bilgisi ve tanımlar** (versiyonlanmış)
* `queries.yml` — **örnek sorgular**
* **LanceDB yerel bellek indeksi** — **hibrit erişim** (retrieval)

🔴 **Biz Wren'in motorunu ve MDL'ini aldık; AI bağlam katmanını ALMADIK** — ve yerine
**8.861 satır Türkçe kural** yazdık.

Ve Wren'in kendi doğruluk çerçevesi altı sütun sayıyor: *schema linking · value profiling ·
**ambiguity detection** · generation trace · **retry/repair** · eval*. Belirsizlik tespiti
için yazdığı tek şey: **«Skill orchestration by the agent»** — yani **Wren de belirsizliği
motorda çözmüyor, ajana devrediyor.** ⊙ *Bu, garson devri kuralımızın bağımsız bir
doğrulamasıdır.*

**Ayrıca `wren serve mcp` OSS'te VAR** (`pip install 'wrenai[mcp]'`): `query_cube`,
`list_cubes`, `describe_cube`, `get_context`, **`recall_queries`** araçlarıyla. Wren'in
`oss_vs_commercial.md` tablosu *«MCP ❌»* diyor ama bu **hosted** MCP'yi kastediyor —
yerel MCP açık. Belge tutarsız, **bizim lehimize**.

---

## 12 · APTALLIK ETTİĞİMİZ YERLER — dürüst liste

Bu bölüm bir suçlama değil, bir **muhasebe**. Her madde ölçülmüştür.

### 12.1 🔴 Ters yatırım
**8.861 satır route'a (trafiğin %35,5'i), 45 satır garsonun istemine (trafiğin %37'si).**
Ve `CLAUDE.md`'nin **en üst kuralı** bunun tersini söylüyor: *«route'a Türkçe öğretmemiz
gerekir ki bu gereksiz… asıl **LLM'e** güveniyoruz»*. Kural doğru yazılmış, yatırım tersine
yapılmış. **131 `§` işareti** ve **120 muafiyet** bu terslığin faturasıdır.

### 12.2 🔴 Ölçülmeyen basamağa güvenmek
Trafiğin **%37'sini** taşıyan garsonun **otomatik doğruluk ölçümü yok**. Kapının kendi
yorumu: *«`garson` HİÇBİR TOPLU KOŞUMDA YOK»*. Elimizdeki tek şey **21 senaryoluk bir
kayıt kümesi** ve bir **kararlılık** ölçümü (1,0) — ⚠ *tutarlılık doğruluk değildir; aynı
cevabı üç kez vermek onu doğru yapmaz.*

### 12.3 🔴 Kapsam yanılsaması
Korpus **14.957 tur** gibi görünüyor; kendi raporunun ifadesiyle **şişme katsayısı 28,0×**
→ gerçek **590 semantik vaka**. *«Yeşil kapı»* 590 vakanın yeşilliğidir. Her 20'lik turun
4-5 yeni kök bulması bu yüzden **beklenen**dir.

### 12.4 🔴 Motorun içindekini yeniden yazmak
`rls.py` (380) ↔ `RowLevelAccessControl` · `dataset.py` (161) ↔ `register_csv/parquet` ·
`compose.py`+`mdl_writer.py` (1.490) ↔ `Manifest`/`to_manifest`/`migrate_manifest_json`.
Ve muhtemelen `cube_router.py`'nin bir kısmı ↔ `wren cube query`.
⊙ **Ölçülmeden iddia edilmiyor** — ama ölçülmesi gereken en pahalı kalem budur.

### 12.5 🔴 Bir sayının Türkçesini BEŞ yerde yazmak
Bu oturumda ölçüldü: `contribution._b3` · `interpret` ×6 · `prescribe` ×2 ·
`plan_tuketici._b` · `kok_neden._sayi`. Beşi de ayrışmıştı (`%83.4'i` ↔ `%83,4'ü`).
⚠ Ve **ön-uç tarafı hâlâ ölçülmedi**: `d3-format`'ta **`tr-TR` locale'i yok**.

### 12.6 🔴 Ölçmeden koruma eklemek
`§KA`'nın kapısına iki kez daraltma koydum, ikisi de **düzeltmemi sessizce iptal etti**
(`not resp.suggestions` — netleştirme zaten `source=None` döner; `source == "cube+llm"` —
aynı soru sonraki koşumda Discovery'ye düştü). *Ölçmeden eklenen bir koruma, bir koruma
değil bir kör noktadır.*

### 12.7 🔴 Sürprizsiz katkı analizi
`§KN-toplam` **en büyük segmenti** seçiyor, **Jensen-Shannon sürprizi hesaplamıyor**.
Adtributor'ın kurucu örneği bunun **yanlış cevap** ürettiğini gösteriyor: en çok açıklayan
ve en özlü aday, dağılımı değişmemişse **suçlu değildir**.
⊙ *«En büyük müşteri hep suçlu çıkıyor»* şikâyeti buradan doğar.

### 12.8 🔴 Çoklu karşılaştırma düzeltmesi yok
Kök-neden motoru soru başına **yüzlerce hipotez** tarıyor; FDR düzeltmesi **yok**.
Ölçülmüş bağlam: *«**kullanıcı içgörülerinin %60'ından fazlası yanlış**»* (CHI 2018).

### 12.9 ⚠ Arşivlenmiş imaja bağlı kalmak
`docker-compose.yml` → `ghcr.io/canner/wren-engine:latest`, depo **arşivli**, konteyner
**`Restarting`**.

### 12.10 ⚠ VQR'ı garsona bağlamamak
`vqr.py` **doğrulanmış soru deposu** — ama yalnız *replay* basamağında. Garsonun istemine
**örnek sorgu beslenmiyor**. Vanna AI'ın tüm tezi, Wren'in `queries.yml`'i ve Cube'un
+17-23 puanı tam olarak bu mekanizmadır.

### 12.11 ✅ Aptallık ETMEDİĞİMİZ bir yer — kayda değer
Gömme modeli seçimi **doğru**: `intfloat/multilingual-e5-large`, **TR-MTEB birincisi**
(mean 66,82 · retrieval 60,62). Yaygın tuzak olan `all-MiniLM`/`all-mpnet` ailesi Türkçe
retrieval'da **22-23** alıyor. *Bu tuzağa düşmemişiz ve `vqr.py`'deki yorum gerekçeyi
zaten yazmış.*

---

# DÖRDÜNCÜ KISIM — YARARLANABİLECEĞİMİZ AÇIK KAYNAK

> Her satır **LICENSE ham metninden** doğrulandı. GitHub'ın lisans etiketi birden çok kez
> yanlış çıktı. Yıldız/tarih `ungh.cc` · PyPI · npm · HuggingFace API'lerinden.

## 13 · ALINACAKLAR — öncelik sırasıyla

### 13.1 ⭐⭐ Apache Ossie — en stratejik bulgu

OSI (Open Semantic Interchange), Snowflake + Salesforce + dbt + Databricks + Cube +
AtScale + **ThoughtSpot** + Sigma tarafından Eylül 2025'te duyuruldu; **9 ay içinde Apache
Software Foundation'a girdi**. 1.824★, **Apache-2.0**.

İçinde: `core-spec/osi-schema.json` (11 KB JSON Schema) · `validation/validate.py` ·
hazır dönüştürücüler (dbt, snowflake, databricks, gooddata, honeydew, omni, polaris,
salesforce).

🔴 **Bizim için asıl kanca — `ai_context` alanı spec'in HER seviyesinde var:**
```yaml
- name: total_revenue
  ai_context:
    synonyms: ["ciro", "hasılat", "gelir", "satış tutarı"]
    examples: ["Bu yıl toplam ciro ne kadar"]
```

⊙ **Bu, tam olarak *«route'a Türkçe öğretilmez»* kuralımızın KABIDIR.** Türkçe sözlük
**koda değil semantik modele** ait olur. Ve **Wren zaten okuyor**:
`wren context build --from-osi semantic_model.yaml`.

**Bir günlük iş:** bir küpümüzü `ai_context.synonyms` ile Ossie YAML'ına çevir,
`ossie validate` ile doğrula. Türkçe sözlüğü koddan modele taşır **ve** Wren'e
kilitlenme riskini düşürür.

### 13.2 ⭐⭐ `shaido987/riskloc` — kök-neden algoritmaları tek depoda

139★, **MIT** (metin doğrulandı). Altı algoritma, ortak pandas arayüzü:

| dosya | satır | algoritma |
|---|---|---|
| `adtributor.py` | **43** | Adtributor (NSDI'14) |
| `rev_rec_adtributor.py` | 74 | R-Adtributor (özyinelemeli) |
| `hotspot.py` | 260 | HotSpot (MCTS + ripple effect) |
| `riskloc.py` | 215 | RiskLoc |
| `squeeze/squeeze.py` | 364 | Squeeze |
| `utils/element_scores.py` | ~70 | **EP + JS-surprise matematiği** |

🟢 **Karar: Adtributor'ı KENDİMİZ yazalım (~85 satır), `riskloc`'u doğrulama referansı
olarak yanımıza alalım.** `generate_dataset.py` ile sentetik regresyon korpusu üretilebilir.

⊙ **Bu, `kok_neden.py`'nin dikey (formül içi) ayrıştırmasının eksik YATAY kardeşidir** —
*«hangi segment kombinasyonu bu düşüşü açıklıyor»*. Mevcut cebirimizle **çakışmıyor**.

⚠ **Lisanssız kod uyarısı:** `wanghaao/ImpAPTr` ve `kapiya/Adtributor` **LICENSE
içermiyor** → varsayılan *«tüm hakları saklı»*, ticari üründe **kullanılamaz**.

### 13.3 ⭐ Metabase deseni — `candidates` + `agent_error`

Metabase belirsizlikte **red vermiyor, tahmin de etmiyor** — `400` ile **makine-okunur bir
nesne** döndürüyor ve *«LLM callers are expected to read the message and **self-correct on
the next turn**»* diyor:

```json
{"error":"ambiguous_measure","candidates":["satis.ciro","iade.ciro"],"agent_error":true}
```

🟢 Bu, *«dürüst red başarı değil»* (red değil, **eksiklik raporu**) **ve** *«şüphede
garson»* (mutfak seçmiyor, **sayıyor**) kurallarımızı **aynı anda** karşılıyor.
⊙ Bizde `test_cube_tie_clarification.py` ve belirsizlik chip'i **zaten var** — bu, o işin
olgunlaşmış hâli. Superset'in `get_compatible_metrics/_dimensions` ucu tamamlayıcı.

### 13.4 ⭐ Grafik: AVA CKB + CompassQL etkinlik tabloları

Ajan **Draco2'yi ve AntV AVA'yı yerelde kurup ölçtü** — ikisi de elendi:

* **Draco 2:** bizim tam senaryomuz (1 ölçü + 1 zaman boyutu, 24 satır) → **çizgi değil
  `point`** önerdi (`point 12` · `bar 16` · `line 32`). Sebep: Draco'da **`temporal` scale
  tipi yok**, datetime `linear`'a düşüyor, zaman serisi *«sürekli×sürekli»* sayılıyor.
  Ayrıca `pip install draco` **Python 3.12'mizde kırılıyor** (metadata `<3.12`), ~72-150 ms
  clingo maliyeti, pie/treemap/gauge taksonomisi yok.
* **AntV AVA:** `computeScore` **çarpımsal**; `bar-series-qty` ağırlığı 0,5 olduğu için
  **sütun grafikleri 0,5 tavanının üstüne yapısal olarak çıkamıyor**. Ölçüm: *«1 ölçü +
  kardinalite 5 nominal»* → 1. öneri **`rose_chart` (4,32)**, sütun 0,5'te. `npm i @antv/ava`
  = **257 MB / 227 paket**. v4 **LLM zorunlu** hâle gelmiş.

🟢 **Önerilen bileşim (hiçbirini bağımlılık almadan):** AVA'nın `ckb/base.js`'indeki
**51 grafik tipi + `dataPres` şeması + `purpose` alanı**nı YAML'e port et (MIT) →
**CompassQL'in `effectiveness/` tablolarıyla sırala** (BSD-3; ve bunlar Draco'nun aksine
zaman serisini **doğru** yapıyor: `Q × TIMEUNIT_T` agregalı → `line: 0, area: −0.1,
bar: −0.2`) → Observable Plot'un **`isMonotonic(X)`** sezgisini al → çıktıyı **Vega-Lite
spec'i** olarak ver.

⚠ **Kalibrasyon:** `viz.py`'miz **zaten 731 satır** ve Cleveland-McGill gerekçeleriyle
yazılmış; canlı ölçümde **10/10 doğru tip** verdi. **Değiştirmeye gerek yok** — Draco'nun
**hard kısıtları** (§9.2) mevcut kurallarımızın *ilkesel türevi* olarak eklenmeli, AVA'nın
`purpose` alanı (Trend/Comparison/Rank/Proportion) ise **niyet nesnemize doğal bir kanca**.

### 13.5 ⭐ Değerlendirme — dört fikir

| kaynak | fikir | bizdeki karşılığı |
|---|---|---|
| **test-suite-sql-eval** (Apache-2.0, EMNLP 2020) | **damıtılmış çoklu mini veri seti**: `yil = 2026` ile `yil > 2025` tek DB'de aynı sonucu verir; **birden çok mini DB'de** ayrışır | 🔴 yok — *«15 gizli kırmızı, 2'si gerçek kusur»* ölçümümüzün panzehiri |
| **Dr.Spider** (Apache-2.0, ICLR 2023) | 17 pertürbasyon; **robustness gap** = `acc(orijinal) − acc(bozulmuş)` | 🔴 yok — `göre/bazında/bazlı` üçlü aşırı-yüklemesi bizi **üç kez** ısırdı, çünkü **ölçülmüyor** |
| **AmbiQT** (MIT, EMNLP 2023) | altın cevap **KÜME**dir; 4. belirsizlik tipi **precomputed aggregates** = bizim küp belirsizliğimiz | 🔴 yok — belirsiz senaryoda tekil `gold` **paydayı kirletir** |
| **EHRSQL** (CC-BY-4.0, NeurIPS 2022) | **reliability score**: kapsam-içine red **ağır negatif**, kapsam-dışına red **pozitif**, kapsam-dışına uydurma **en ağır negatif** | 🟢 *«dürüst red başarı değil»* doktrinimizin **matematiksel formu** — tek başına bir CI kapısı olabilir |

**Araç tarafı:** `syrupy` (MIT, **sıfır bağımlılık**) + `pytest-regressions` (MIT) snapshot
için · `promptfoo` (**saf MIT**, 24.1K★) **yalnız garson** için · `inspect_ai` (MIT)
alternatif.
❌ **Elenenler:** `phoenix` (**Elastic License 2.0**), `ragas` (durgun + org değişti),
`uptrain` (**ölü**, 2024-05).

⚠ **Kalibrasyon:** `eval/run.py`'miz **zaten selective prediction** uyguluyor
(coverage + answered-precision) ve `test_eval_gate.py` baseline ratchet'i var — listedeki
çoğu araçtan **olgun**. Eksik olan: snapshot katmanı, kategori kırılımı ve **standart hata**
(Inspect AI'ın `stderr`'i — *«20 senaryoluk paydada %85 ile %90 arasındaki fark gürültü
mü?»* sorusunun tek cevabı; **«payda kutsaldır»** ilkemizin doğal tamamlayıcısı).

### 13.6 Türkçe NLP — ölçülmüş kararlar

| araç | karar | gerekçe |
|---|---|---|
| **Snowball Türkçe** (BSD-3, 34,4M indirme/ay) | 🟢 **gölge ölçümde dene** | sıfır bağımlılık, mikrosaniye. ⚠ *«stems only **noun and nominal** verb suffixes»* → `arttı`yı **çözmez**, ama `satışlarımızın`/`cirodaki`/`bazında` tam kapsamda |
| **Zeyrek** (MIT) | 🔴 **RED** | `analyze('benim')` → **dört** parse; **disambiguation YOK**. Deterministik router için *«N aday lemma»* çözüm değil, **dördüncü bir belirsizlik katmanı**. §G/AJ0'daki *«arttı» bir FİİL* teşhisini **çözmezdi** |
| **Zemberek** (Apache-2.0) | ◐ **sözlüğü** al, kodu alma | README: *«slow maintenance mode»*, son sürüm **2019**, Maven Central'da **yok**. ~130k köklü sözlük değerli |
| **stanza** (Apache-2.0) | ◐ **laboratuvarda** | Türkçe lemma **%98,9** (Atis/Tourism — bizim alanımıza yakın) ama `torch` + **~500 ms**. Karşılaştırılabilir tek Türkçe NLIDB projesi Stanza'yı ölçüp **kendi regex'iyle değiştirmiş** (<10 ms) — bizimle **aynı mimari karar** |
| **VNLP** · **UDPipe 2** | 🔴 lisans engeli | AGPL-3.0 · modeller **CC BY-NC-SA** |
| **`ytu-ce-cosmos/modernbert-tr-reranker`** | ⭐ **ÖLÇ** | cross-encoder, **+5…+9 nDCG@10**; şema sütun sayımız küçük → maliyet kabul edilebilir. *Muhtemelen en yüksek getirili tek ekleme* |

**Türkçe NL→SQL veri setleri (bilinmiyordu — üç tane var):**
**TURSpider** (8.659+1.034, insan çevirisi, HF kopyası **CC BY 4.0**) · **TUR2SQL**
(10.809, ⚠ lisans belirsiz) · **BIRDTurk** (10.962, ACL Anthology).

### 13.7 Elenen ama not düşülmesi gerekenler

| proje | neden |
|---|---|
| **Chat2DB** (27.9K★) | ⚠ `LicenseRef-Chat2DB` — harici ürün/OEM/white-label **yazılı izin olmadan yasak**. **Açık kaynak değil** |
| **Vanna AI** (23.8K★, MIT) | son commit **2 Şubat 2026** — altı aydır sessiz. RLS/çok-kiracılılık **deseni** için okunmalı, bağımlılık alınmamalı |
| **DataLine** · **Steampipe** | GPL-3.0 / AGPL-3.0 — copyleft |
| **sqlcoder** · **Dataherald** | ☠️ 2024'ten beri ölü |
| **XiYan-SQL** alt projeleri | ⭐ **M-Schema** (LLM-dostu şema temsili) ve **XiYan-DBDescGen** (otomatik DB açıklaması) — MDL zenginleştirme için doğrudan ilgili |
| **LangChain SQL** | v1.x'te SQL QA öğreticisi **kaldırıldı**; toolkit *legacy* |
| **SHAP** · **PyRCA** · **EconML** · **Kats** · **Merlion** | kategori hatası / ölü / arşivli |
| **`ruptures`** (BSD-2) · **`statsforecast`** (Apache-2.0) | 🟢 *«mart'ta düştü»* iddiasını doğrulamak ve Adtributor'ın istediği `F` (baseline) için |

---

# BEŞİNCİ KISIM — NE YAPMALIYIZ

## 14 · ÖNCELİK SIRASI — ölçülmüş gerekçelerle

> Sıra **etki ÷ maliyet** ile kuruldu. Her madde bir **ölçüme** dayanıyor.

### 14.1 🔴 ÖNCE ÖLÇ — çünkü ölçmediğimiz yeri geliştiremeyiz

| # | iş | gerekçe (ölçülmüş) |
|---|---|---|
| **1** | **Garson korpusu kur.** 300-500 gerçek soru, `(soru → beklenen küp/ölçü/kırılım)` etiketli. `promptfoo` veya mevcut `eval/run.py` üstünde. | Garson trafiğin **%37'sini** taşıyor ve ölçümü **21 senaryo**. Bu tek madde, geri kalan her şeyin ön koşulu |
| **2** | **`cevapsız` oranını birinci sınıf metrik yap.** Bugün `%19,9` korpusta, `%21,8` canlıda — ve kapı manşetinde **yok**. | *«En kötü promptta bile cevap veriyorlar»* şikâyetinin sayısal karşılığı |
| **3** | **Şişme katsayısını manşete yaz.** *«doğru=95»* yerine *«590 semantik vakada %95»*. | *«Yeşil kapı»* yanılsamasını bitirir |
| **4** | **EHRSQL reliability score'u kapıya ekle.** | *«Dürüst red başarı değil»* doktrininin ölçülebilir hâli |

### 14.2 🔴 SONRA GARSONU BESLE — en yüksek getirili teknik iş

| # | iş | ölçülmüş dayanak |
|---|---|---|
| **5** | **VQR'ı garsona bağla** — istemin içine **retrieval ile seçilmiş 5-10 örnek sorgu**. | Cube: **+17…+23 puan**, ve *«varyansın tamamını semantik belge açıklıyor, model seçimi açıklamıyor»* — üstelik **4 KB markdown**'dan |
| **6** | **`ManifestExtractor.extract_by` ile şema daraltma.** Bugün her soruda **23.729 karakter** gidiyor. | Şema bağlama hatası: Spider 2.0'da **%27,6**, MultiSpider 2.0'da **%33,0** |
| **7** | **`instructions.md` karşılığı bir iş sözlüğü** (Wren AI Context Layer / Ossie `ai_context`). | Türkçe sözlüğü **koddan modele** taşır — 8.861 satırlık route yığınının varlık sebebini azaltır |
| **8** | **Çalıştır → hatayı gör → düzelt döngüsü** (bugün yalnız *boş yanıt* için yeniden deneme var). | CHASE-SQL: oylama %68,84 → **eğitilmiş seçici %73,01**, oracle **%82,79**. *Darboğaz üretim değil **seçim*** |
| **9** | **İki-sağlayıcılı LLM hakem** (sonucu doğrula, k=3 oylamanın yerine değil, **üstüne**). | AUROC: self-consistency **0,675** → tek hakem 0,770 → **topluluk 0,822** (ECE 0,031) |

### 14.3 🟡 KÖK-NEDEN'İ TAMAMLA

| # | iş | dayanak |
|---|---|---|
| **10** | **Adtributor'ı yaz (~85 satır)** — `§KN`'nin eksik **yatay** kardeşi. `riskloc` doğrulama referansı. | Layer-1'de kilitliyiz; bileşik kök nedende Adtributor bile **%0**'a düşüyor (HotSpot ölçümü) |
| **11** | **Jensen-Shannon sürprizini ekle.** | *«Yalnız explanatory power kullanan her analiz **büyük segmentleri sistematik olarak suçlar**»* — `§KN-toplam`'ımız tam bu tuzakta |
| **12** | **FDR düzeltmesi (Benjamini-Hochberg)** veya keşif/doğrulama ayrımı. | **CHI 2018: kullanıcı içgörülerinin %60'ından fazlası yanlış** |
| **13** | **LMDI-I'e geç** (alt-grup toplanabilirliği) + **sıfır/negatif politikası**. | `ln(0)` tanımsız; negatifte LMDI tanımsız → Shapley |
| **14** | *«Kök neden»* yerine **«katkı analizi»** demeyi değerlendir. | Tableau kendi dokümanında: *«not a tool to prove or disprove hypotheses»*. **İsimlendirme başlı başına bir yanıltma kaynağı** |

### 14.4 🟡 GRAFİK VE BİÇİM

| # | iş | dayanak |
|---|---|---|
| **15** | **Draco hard kısıtlarını ekle** (§9.2) — özellikle `stack_without_summative_agg`. | Bu oturumda **yüzdeleri topladım**; literatür bunu 2018'de hard hata ilan etmiş |
| **16** | **Ön-uç sayı biçimini ölç ve düzelt.** `d3-format`'ta **`tr-TR` YOK**. | `%56` vs `56%` · `12 B` = **bin** ↔ İngilizcede **milyar** |
| **17** | Grafik seçim kurallarını **belgele ve yayınla**. | Rakiplerin **hiçbiri** yayınlamıyor — **denetlenebilir kural bir rekabet avantajı** |

### 14.5 🟢 TEMİZLİK

| # | iş |
|---|---|
| **18** | `docker-compose.yml`'deki **arşivlenmiş** `ghcr.io/canner/wren-engine:latest` bağımlılığını netleştir (konteyner şu an **`Restarting`**) |
| **19** | `wren cube query --sql-only` ile `cube_router`'ın SQL üretimini **yan yana koy** — ne kadarı yeniden yazım? |
| **20** | MDL'deki **31 `relationship`**'i çapraz-küp yolunda kullan (bugün *«blend»*) |
| **21** | Apache **Ossie** pilotu — bir küp, `ai_context.synonyms` ile, `ossie validate` |
| **22** | `modernbert-tr-reranker`'ı ölç (**+5…+9 nDCG@10** potansiyeli) |

## 15 · DÜRÜST KAPANIŞ

### 15.1 Kullanıcının üç iddiası — ölçümle karşılığı

| iddia | ölçüm | yargı |
|---|---|---|
| *«Her 20 soruda ciddi sorun çıkıyor, hiç bitmiyor»* | son 5 turda **~5 senaryoda 1 kök**, oran **düşmüyor** | ✅ **DOĞRU** — ve sebebi §4.3'te: kombinatoryal uzay, 131 kural o uzayın 131 hücresi |
| *«Corpus sadece route ölçüyor, her şey garsonda bitiyor»* | route **%35,5** · garson **%37,0**; kapının kendi yorumu: *«garson HİÇBİR TOPLU KOŞUMDA YOK»* | ✅ **TAM DOĞRU** — raporun omurgası |
| *«Biz daha grafik oluştururken binlerce hata alıyoruz»* | 10 canlı senaryo → **10/10 doğru tip**, sıfır *«çizilmedi»*; iki hipotezim çürüdü | ❌ **YANLIŞ TEŞHİS** — grafik katmanı en sağlam parçalardan biri; hata **üstteki basamaklarda** doğuyor ve grafikte **görünüyor** |

*Bir belirtiyi yanlış organa yazmak, tedaviyi de yanlış yere yapar.*

### 15.2 *«Rakipler mükemmel»* — ölçümle karşılığı

Bu **doğru değil**, ve bunu bilmek moral değil **strateji** meselesi:

* **13 üründen 10'u doğruluk sayısı yayınlamıyor.**
* **Power BI Copilot** kapsam dışında **LLM genel bilgisinden uyduruyor**; bağımsız ölçüm
  **%62,5**; uygulamacı: *«3 saniyede DAX üretti, düzeltmem 45 dakika sürdü»*.
* **Databricks Genie**'nin **%84,5**'i **28 soruluk** bir sette (±13 puan).
* **Qlik Insight Advisor** 2019'dan beri var ve kendi topluluğu *«tek bir şirket
  bulamadım»* diyor.
* **Amazon** ürünü 18 ayda **dört kez** yeniden adlandırdı; The Register: *«application
  graveyard»*.
* **Gartner:** *«**Nearly every vendor claims agentic capability. Very few have moved past
  natural-language querying.**»* · agentic analitik projelerinin **%60'ı 2028'e kadar
  başarısız olacak**.
* **MIT NANDA:** kuruluşların **%95'i sıfır getiri** alıyor (⚠ örneklem tutarsızlığı
  raporun kendi metninde kabul edilmiş).
* **Forrester:** BI'da elle kullanım **%20 tavanında**; doğal dilin katkısı **+10 puan**.

⊙ **Fark şurada:** rakipler *«her soruya bir şey söyler»* (Power BI kapsam dışında bile
konuşur), biz *«bilmediğimizde susarız»*. Onların hatası **görünmez** (sessiz yanlış),
bizimki **görünür** (boş ekran). **İkisi de kusur** — ama görünür kusur ürünü kötü
gösterir, görünmez kusur **kullanıcıya zarar verir**.

*dbt'nin cümlesi bizim tarafımızı tarif ediyor: «Text-to-SQL'de başarısızlık makul ama
yanlış bir cevaptır; semantik katmanda başarısızlık bir hata mesajıdır.»*

### 15.3 Mimari mükemmel mi

**Hayır — ama yanlış da değil.** Ölçüm şunu söylüyor:

🟢 **Doğru olan:** kamp seçimi (A kampı, ThoughtSpot/Looker ile aynı) · sayıyı her zaman
küpün koyması · beyan kültürü · kesitsel kök-neden cebiri (LMDI'nin doğru uygulanmış hâli)
· gömme modeli · grafik katmanı · kendi kendini denetleyen kapılar.

🔴 **Yanlış olan mimari değil, ağırlığın dağılımı:** trafiğin %37'sini taşıyan basamak
**45 satırlık bir istemle** yönetiliyor ve **hiç ölçülmüyor**; %35,5'ini taşıyan basamağa
**8.861 satır** yazılmış. Ve o 8.861 satırın varlık sebebi olan model
(*«kullanıcı dilbilimsel şemayı elle beslesin»*) **Microsoft ve Tableau tarafından
piyasadan kaldırıldı**.

### 15.4 Tek cümle

> **Ürün, ölçtüğü yerde iyi; ölçmediği yerde bilinmiyor. Ve ölçmediği yer, kullanıcının
> yaşadığı yerin üçte ikisi.**

---

## EK · Kaynakça

**Benchmark:** [Spider 2.0](https://spider2-sql.github.io/) · [arXiv 2411.07763](https://arxiv.org/abs/2411.07763) · [BIRD](https://bird-bench.github.io/) · [BEAVER arXiv 2409.02038](https://arxiv.org/abs/2409.02038) · [BIRD-INTERACT arXiv 2510.05318](https://arxiv.org/abs/2510.05318) · [Archer arXiv 2402.12554](https://ar5iv.labs.arxiv.org/html/2402.12554) · [AIMultiple bağımsız ölçüm](https://aimultiple.com/text-to-sql) · [Stonebraker, CACM](https://cacm.acm.org/blogcacm/if-you-think-you-can-do-real-world-text-to-sql/)

**Hata/güvenilirlik:** [arXiv 2501.09310](https://arxiv.org/html/2501.09310v1) · [LinkedIn arXiv 2507.14372](https://arxiv.org/html/2507.14372v1) · [selective prediction arXiv 2607.06799](https://arxiv.org/html/2607.06799v1) · [CHASE-SQL arXiv 2410.01943](https://ar5iv.labs.arxiv.org/html/2410.01943) · [AbstentionBench arXiv 2506.09038](https://arxiv.org/html/2506.09038v1)

**Semantik katman:** [Cube paired benchmark arXiv 2604.25149](https://arxiv.org/abs/2604.25149) · [dbt 2026](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026) · [Sequeda arXiv 2311.07509](https://arxiv.org/abs/2311.07509) · [AtScale](https://www.atscale.com/press/natural-language-processing-breakthrough/) · [lkr.dev Looker benchmark](https://www.lkr.dev/articles/benchmarking-semantic-layer-conversational-analytics/) · [Apache Ossie](https://github.com/apache/ossie)

**Belirsizlik:** [Microsoft/CIDR 2024](https://www.cidrdb.org/cidr2024/papers/p74-floratou.pdf) · [AMBROSIA](https://ambrosia-benchmark.github.io/) · [AmbiQT arXiv 2310.13659](https://arxiv.org/abs/2310.13659) · [AmbiSQL arXiv 2508.15276](https://arxiv.org/html/2508.15276v1) · [NLIDB kullanıcı çalışması arXiv 2511.14718](https://arxiv.org/html/2511.14718v2)

**Türkçe:** [BIRDTurk SIGTURK 2026](https://aclanthology.org/2026.sigturk-1.13/) · [arXiv 2602.03633](https://arxiv.org/abs/2602.03633) · [depo](https://github.com/metunlp/birdturk) · [TURSpider](https://github.com/alibugra/TURSpider) · [TUR2SQL](https://github.com/alibugra/TUR2SQL) · [MultiSpider arXiv 2212.13492](https://ar5iv.labs.arxiv.org/html/2212.13492) · [MultiSpider 2.0 arXiv 2509.24405](https://arxiv.org/html/2509.24405) · [TR-MTEB](https://aclanthology.org/2025.findings-emnlp.471/)

**Grafik:** [Draco (OSF)](https://osf.io/3eg9c/download) · [uwdata/draco](https://github.com/uwdata/draco) · [Show Me, TVCG 2007](https://doi.org/10.1109/TVCG.2007.70594) · [Mackinlay APT 1986](https://doi.org/10.1145/22949.22950) · [Observable Plot](https://github.com/observablehq/plot) · [CompassQL](https://github.com/vega/compassql) · [AntV AVA](https://github.com/antvis/AVA) · [Pandey ve ark., CHI 2015](https://doi.org/10.1145/2702123.2702608)

**Kök-neden:** [Adtributor, NSDI'14](https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-bhagwan.pdf) · [HotSpot, IEEE Access 2018](https://netman.aiops.org/wp-content/uploads/2018/12/sunyq_IEEEAccess2018_HotSpot.pdf) · [Squeeze, ISSRE'19](https://netman.aiops.org/wp-content/uploads/2019/10/Squeeze-ISSRE2019_v2.pdf) · [PSqueeze, JSS 2023](https://netman.aiops.org/wp-content/uploads/2023/05/psqueeze-jss.pdf) · [riskloc](https://github.com/shaido987/riskloc) · [DIFF, VLDB 2019](https://www.vldb.org/pvldb/vol12/p419-abuzaid.pdf) · [Ang, LMDI, Energy Policy 2005](https://doi.org/10.1016/j.enpol.2003.10.010) · [Zgraggen ve ark., CHI 2018](https://www.emanuelzgraggen.com/assets/pdf/mcp.pdf)

**Değerlendirme:** [test-suite-sql-eval](https://github.com/taoyds/test-suite-sql-eval) · [Dr.Spider](https://github.com/awslabs/diagnostic-robustness-text-to-sql) · [AmbiQT](https://github.com/testzer0/AmbiQT) · [EHRSQL](https://github.com/glee4810/EHRSQL) · [promptfoo](https://github.com/promptfoo/promptfoo) · [syrupy](https://github.com/syrupy-project/syrupy)

**Rakip dokümantasyon:** [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) · [Snowflake doğruluk](https://www.snowflake.com/en/blog/engineering/cortex-analyst-text-to-sql-accuracy-bi/) · [Genie](https://docs.databricks.com/aws/en/genie/) · [ThoughtSpot Spotter](https://www.thoughtspot.com/blog/introducing-spotter-ai-analyst) · [Spotter kısıtları](https://docs.thoughtspot.com/cloud/26.7.0.cl/spotter-limitations) · [Power BI Copilot](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-ask-data-question) · [Q&A emekliliği](https://learn.microsoft.com/en-us/power-bi/natural-language/q-and-a-limitations) · [Key influencers](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-influencers) · [Tableau Pulse](https://help.tableau.com/current/online/en-us/pulse_insights_platform_insight_types.htm) · [Looker CA](https://docs.cloud.google.com/looker/docs/conversational-analytics-overview) · [Gemini dil kısıtı](https://docs.cloud.google.com/looker/docs/troubleshooting-gemini) · [Quick Sight Topics](https://docs.aws.amazon.com/quick/latest/userguide/topics-in-chat.html) · [Qlik reasoning trace](https://community.qlik.com/t5/Official-Support-Articles/Show-Your-Work-The-Architecture-of-Qlik-Answers-Reasoning-Trace/ta-p/2553267) · [Sisense AI Assistant](https://docs.sisense.com/main/SisenseLinux/ai-assistant.htm) · [Zenlytic Clarity Engine](https://docs.zenlytic.com/using-zenlytic/clarity_engine) · [WrenAI](https://github.com/Canner/WrenAI)

---

**Yöntem notu:** Yerel ölçümler bu depoda canlı sistem üzerinde curl/`docker exec`/kod
okuması ile yapıldı. Dış araştırma dört paralel alt-ajanla yürütüldü; oturumun WebSearch
bütçesi (200/200) tükendiği için tüm erişim WebFetch + GitHub/PyPI/npm/HuggingFace API'leri
üzerinden yapıldı ve lisanslar **LICENSE ham metninden** doğrulandı. Erişilemeyen kaynaklar
(Show Me 2007 PDF, APT 1986 tam metni, iDice, Ang 2005) ilgili yerlerde **açıkça
işaretlendi** ve içerikleri yalnız ikincil/doğrulanabilir kaynaklardan aktarıldı.
