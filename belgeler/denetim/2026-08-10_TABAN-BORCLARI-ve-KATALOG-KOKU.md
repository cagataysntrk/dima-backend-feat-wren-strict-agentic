# TABAN BORÇLARI ve KATALOĞUN KÖKÜ — *orkestratör bir tavandı, taban yerinde duruyor*

> 🔴🔴 **BU BELGE DÖNGÜYE SUNULMUŞ BİR RAPORDUR.** İçindeki **yedi borç**, döngünün
> her demetinde **kontrol edilir, denetlenir ve geliştirilir** — bu bir öneri listesi
> değil, `OPERASYON.md §2c`'ye bağlanmış **bağlayıcı bir denetim listesidir**.
> Bir borcun kapandığı **ölçümle** yazılmadan demet kapanmaz.

| | |
|---|---|
| **Tarih** | 2026-08-10 |
| **HEAD** | `f9cd3cb` — *feat(§AR/Ö): KURAL YETMEDİ, ÖRNEK ÇÖZDÜ* |
| **Yöntem** | statik ölçüm: `demo/packs/**/cubes/*/metadata.yml` ayrıştırıldı · `app/` · `lab/` · `eval/` okundu · git kütüğü tarandı |
| **Ne KOŞULMADI** | 🔴 **hiçbir test, hiçbir kapı, hiçbir canlı tur.** Bu bir *okuma* denetimidir; aşağıdaki her sayı **statik kaynaktan** alınmıştır ve canlı derlenmiş şemadan **farklı olabilir** (bkz. `B-0`) |
| **Tür** | 🔒 `denetim/` — tarih damgalı fotoğraf, **değiştirilmez**. Yeni ölçüm **yeni tarihli yeni dosyadır** |

---

## 0 · TEK CÜMLE

> Orkestratör sistemin **ne söyleyebileceğini** genişletti; sistemin **ne anladığını**
> belirleyen şey hâlâ `route()` + **katalog**, ve o iki yerde kalan borçlar sığ değil
> — ama bu borçların **hepsinin tek bir adresi var**: kataloğun kendisi.

---

## 1 · TEŞHİS — neden *"tavan açıldı, taban yükselmedi"*

Orkestratör (`planner` · `plan_kosucu` · `plan_garson`) bir **yürütme** katmanıdır:
`SORGU → BAGLA → SUZ → ANLAT` gibi adımları dizip tek soruda birden çok tur koşabilir.
Ama zincirin **girdisi** değişmedi: her adım yine aynı `route()`'a ve aynı katalog
metnine bakıyor. Bir orkestratör **ifade edebildiğinden fazlasını anlayamaz**.

⊙ **Kanıt — bu turun iki sessiz-yanlışı da orkestratörden gelmedi:**

| soru | ne oldu | rozet | kök |
|---|---|---|---|
| *«bir **de** gecikme ekle»* | `ort_renk_sapmasi` eklendi (`dE!` → `de`) | `cube` | **katalog**: ölçü sinonimi bir Türkçe bağlaç ekiyle çakıştı (`§SY`, `006a824`) |
| *«**renk grubuna** göre fire»* | `ham_grup, renk, yas_grubu` döndü | `cube` | **katalog**: etiketten *makinenin kendi ürettiği* token iki boyuta birden gitti (`§EB`, `3f6d144`) |

İkisinde de rozet `source=cube` — yani **garson hiç çağrılmadı**. Kusur garsonun
anlayışında değil, route'un **yanlış kesinliğinde**ydi; ve o kesinliği route'a veren
şey katalogdu.

⊙ **Ve düzeltmeden sonra ne olduğu, mimarinin çalıştığının kanıtıdır:**
*«renk grubuna göre fire»* → route **çekildi** → garson devraldı → **doğru cevap**
(yalnız `renk`, 5 satır). Yani hedeflenen mimari zaten işliyor; işlemesini engelleyen
tek şey, route'a çürütülemez bir kesinlik veren katalogdu.

---

## 2 · KULLANICININ TEZİ — nerede haklı, nerede eksik

> *"Biz zaten garsonu güvenilir kılarak, sisteme intent/sinonim hiçbir şey eklemesek de
> çalışsın demedik mi? Route sadece kesin doğruluk içeren sorularda bir kolaylık;
> azıcık bile şüphe olsa garson girer ve çözer."*

### ✅ Tezin DOĞRU olduğu yer — ve ölçülmüş karşılığı

**Route'un kesinliği çürütülebilir olmalıdır.** Bir token birden çok sahibe işaret
ediyorsa route emin **olamaz**; emin olamadığında **çekilmelidir**. `§EB` bunu
*makinenin ürettiği* belirsizlikler için yapısal olarak kurdu (`belirsiz_boyut_tokenlari`
→ `wren_service.py:826` → `cube_router.py:3494`) ve sonuç yukarıdaki tabloda: route
çekildi, garson çözdü.

🔴 **Ama bu kural bugün YALNIZ boyut türevleri için var.** Ölçüler için yok
(`B-2`), beyan edilmiş çok-sahiplilik için yok (`B-4`).

### ⚠ Tezin EKSİK olduğu yer — ve bu ayrım pahalıya mal oldu

**Katalog route'un sözlüğü değil, garsonun MENÜSÜDÜR.** Garsonun iş terimleri hakkında
**tek** bilgi kaynağı `build_catalog`'un ürettiği metindir. Sinonimler oradan çıkarsa
route yavaşlamaz — **garson körleşir**.

⊙ Ölçülmüş kanıt (`belgeler/denetim/2026-08-07_CANLI-ARIZA-TESHISI.md`): katalog LLM'e
yalnız teknik kolon adları yazdığı dönemde, *"verimlilik"* soran bir kullanıcı için
**9/9 Intent çağrısı `{"cube":null}`** döndü. Oylama uyuşmazlığı değil — **aday
yokluğu**. Model Türkçe biliyordu; `fire`ye bu şirkette `zayiat` dendiğini bilmiyordu.
`katalog_sozlugu` bayrağı açılınca o körlük kapandı.

> **Sonuç:** sinonim, route için bir **hız** aracıdır; garson için bir **varlık
> şartıdır**. Tez *"sinonim gereksiz"* biçiminde okunursa, kapatılan körlük geri açılır.
> Tez *"route sahte kesinlik üretmesin"* biçiminde okunursa **doğrudur ve uygulanabilir**
> — bu raporun `B-2`'si tam olarak odur.

---

## 3 · BUGÜN ALINAN ÖLÇÜMLER *(statik, 2026-08-10)*

### 3.1 · Katalog gövdesi

| ölçüm | depo geneli *(tüm pack'ler)* | `boyahane + logo-3` bileşimi |
|---|---|---|
| küp tanımı | **28** | **22** |
| ölçü tanımı | **173** | **139** |
| benzersiz ölçü **adı** | **141** | **132** |
| 🔴 **çok sahipli** ölçü adı | **13** | **7** |
| 🔴 **yön beyanı yok** (`lower_is_better`) | **125 / 173** *(%72)* | **93 / 139** *(%67)* |

**Çok sahipli ölçüler (depo geneli, 13):**

```
alim_miktari            → mal | ticaret
alim_tutari             → mal | ticaret
ilk_seferde_tamam_yuzde → oee | parti
net_miktar              → mal | ticaret
ort_alis_fiyati         → mal | ticaret
ort_satis_fiyati        → mal | ticaret
satis_miktari           → mal | ticaret
satis_tutari_hareket    → mal | ticaret
toplam_dogalgaz_sm3     → enerji_makine | surdurulebilirlik
toplam_durus_dakika     → bakim | oee
toplam_fire_kg          → oee | parti
toplam_tep              → enerji_makine | surdurulebilirlik
toplam_uretim_kg        → maliyet | oee
```

### 3.2 · Müşteri ekseni — **beş ad, üç ayrık aile**

| boyut adı | hangi küplerde |
|---|---|
| `cari_adi` | `cari` · `mal` · `ticaret` · `yaslandirma` |
| `cari_kodu` | `cari` · `mal` · `ticaret` · `yaslandirma` |
| `cari_ref` | `cari` · `mal` · `ticaret` |
| `musteri` | `kalite` · `parti` · `surdurulebilirlik` |
| `musteri_kod` | `firsat` · `sevkiyat` · `sikayet` · `siparis` |

🔴 Üç aile **kesişmiyor**. `blend_sql` paylaşılan **boyut ADLARI** üzerinden
`FULL OUTER JOIN` kurar (`wren_service.py:1525-1528`) — dolayısıyla *«şikâyeti olan
müşterinin cirosu»* gibi bir soru **yapısal olarak** kurulamaz. Orkestratör bunu iki
ayrı bölümle telafi edebilir; o bir **çare değil köprüdür**.

### 3.3 · Ölçüm aletlerinin kapsamı

| alet | payda | sağlayıcı |
|---|---|---|
| `lab/nl_corpus.py` *(demet kapısı)* | ~10.800 soru / 4 şirket | 🔴 **`rule` — LLM YOK** (`nl_corpus.py:10`) |
| `eval/cases.yaml` `--slice det` | **115** vaka | LLM yok |
| `eval/cases.yaml` `--slice llm` | 🔴 **4** vaka | canlı LLM |

---

## 4 · YEDİ AÇIK BORÇ

> Her borç: **teşhis · kanıt · kök · neden bugüne kadar kapanmadı · kök çözüm.**
> Sıra §5'te, gerekçesiyle.

---

### 🔴🔴 `B-0` · KATALOĞUN KAÇ ÖLÇÜSÜ OLDUĞUNUN TEK CEVABI YOK

**Teşhis.** Aynı soruya üç kaynak üç sayı veriyor.

| kaynak | sayı |
|---|---|
| `app/katalog_metni.py` docstring *(2026-08-09, canlı derlenmiş şema)* | 127 ölçü / **9** çok sahipli |
| bu raporun statik pack ölçümü, `boyahane+logo-3` | 132 / **7** |
| bu raporun statik pack ölçümü, depo geneli | 141 / **13** |

**Kök.** Katalog **derlenmiş** bir üründür: `compose()` modül + sektör + kaynak + türev
katmanlarını birleştirir, ilişki-türevi boyutlar ekler, overlay uygular. Statik
pack'ler o ürünün **girdisidir**, kendisi değil. Ne kadar sapma olduğunu söyleyen
hiçbir kapı yok.

**Neden kapanmadı.** Kimse iki sayıyı yan yana koymadı — her ölçüm kendi yüzeyinde
doğruydu.

⚠ Bu, bu depoda ölçülmüş sınıfın **üçüncü** örneği: *"ölçüm aracı bayat şemadan
okuyordu"* (`demo/wren-project` artefaktı) ve *"kapı yavaşlaması"* raporundaki bayat
`_AGIR` dilim sabiti. **Beklenmedik bir sayıda önce ölçüm yüzeyinden şüphelen.**

**Kök çözüm.** Kataloğun **tek beyan edilmiş sayacı**: derlenmiş şemadan üretilen
`katalog_envanteri()` (küp · ölçü · benzersiz ad · çok sahipli · yön beyanı oranı) +
bir kapı ki envanter beklenenden saparsa kırmızı versin. *Sayısı olmayan bir
katalogda, hiçbir borcun ilerlediği kanıtlanamaz.*

---

### 🔴🔴 `B-1` · GARSON YOLUNUN KORPUSU YOK — **her karar route'un gözüyle veriliyor**

**Teşhis.** Demet kapısının kalite çıtası (`nl_corpus`, ~10.800 soru) **`rule`
sağlayıcıyla** koşar: içinde **hiç LLM yoktur**. Korpus *%95,1* dediğinde ölçtüğü şey
**yalnız route**. Doktrinin *"ikincil"* dediği yol, kalitenin **tek** ölçüsü.

**Kanıt — ve maliyeti üç kez ödendi:**

| olay | ne oldu |
|---|---|
| `G3` (*"cevapsız dal cevaplı yolu kesemez"*) | korpus `%95,1 → %93,5` dedi, değişiklik **geri alındı**. Kaybın gerçek anlamı *"turu mutfağın en aptal yedeğine devretmenin maliyeti"*ydi — üretimde orada gerçek bir LLM var |
| `§EB/A` (`18c90c8`) | korpus **haklı çıktı** (`sessiz_yanlis` 12→18) — çünkü o bir **kapsam** değişikliğiydi ve kapsamın ölçüsü korpustur |
| bu turun beş düzeltmesi | kapı **hiç görmedi**; yalnız canlı curl gördü |

Yani alet bazen haklı bazen kör, ve hangisinde olduğu **ancak canlı koşarak**
anlaşılıyor. Karşı ağırlık `eval --slice llm`: **4 vaka**.

⚠ Ve `OPERASYON-DURUM.md` bunu zaten yazmış: *"korpus bugün «sistem kendi kelimelerini
tanıyor mu» sorusunu ölçüyor (≥%97,1 katalog türevi) — kullanıcının kelimelerini
değil."* Yani bu borç **teşhis edilmiş ama ödenmemiştir**.

**Neden kapanmadı.** Canlı LLM dilimi **kotalıdır ve yavaştır**; bedava koşan bir
aletin yanında hep ertelendi.

**Kök çözüm — üç kademeli, hepsi bugün kurulabilir:**

1. **`--slice llm` paydasını anlamlı bir sayıya çıkar** (4 → ≥60): her `§`-kodlu canlı
   bulgu (bu turun `§SY` · `§EB` · `§HB` · `§AR/Ö` · `§AT` · `§W-C` vakaları) bir
   vakaya dönüşür. Bunlar **zaten ölçüldü**; yazılmadıkları için tekrar edebilirler.
2. **Kayıt-ve-tekrar (kaset)**: canlı LLM cevapları diske yazılır, sonraki koşumlar
   kasetten koşar → kotasız, deterministik bir **garson korpusu**. `lab/kasetler/`
   dizini bu amaçla **zaten var**.
3. **Payda ayrımı beyan edilir**: kapı çıktısı tek bir *%* yerine
   **`route: %X (n=…)` · `garson: %Y (n=…)`** iki satır basar. *Tek sayı, iki yolun
   ortalamasıdır ve hangi yolun bozulduğunu gizler.*

---

### 🔴 `B-2` · ROUTE'UN KESİNLİĞİ ÇÜRÜTÜLEBİLİR DEĞİL

**Teşhis.** `route()` bir eşleşme bulduğunda **emin** olur; eşleştiği şeyin *sahte bir
kesinlik* olup olmadığını sınayan genel bir kural yok.

**Kanıt.** Bu turun iki sessiz-yanlışı (§1 tablosu). İkisinde de rozet `source=cube`,
garson **hiç çağrılmadı**.

**Kök.** `§EB` çürütülebilirliği **yalnız bir sınıf için** kurdu: makinenin etiketten
türettiği boyut token'ları (*«Ham Grubu»* → `ham`, `grubu`). Üç sınıf açıkta:

| sınıf | bugün | olması gereken |
|---|---|---|
| makine-türevi **boyut** token'ı | ✅ belirsizse düşer (`§EB`) | — |
| makine-türevi **ölçü** token'ı | 🔴 sınanmıyor | aynı kural |
| **beyan edilmiş** çok sahipli ölçü | ◐ ifşa var, **çekilme yok** | sahip beyanı yoksa → çekil |
| Türkçe **dilbilgisi** ile çakışan sinonim (`de` · `ki` · `mi`) | 🔴 sınanmıyor | kapalı-sınıf ek listesi ile ayrıştır |

**Neden kapanmadı.** Her vaka tek tek yakalandı; **sınıf** olarak adlandırılmadı.

**Kök çözüm.** `route()`'un dönüş sözleşmesine bir **çürütme adımı** eklenir:
*"bu eşleşmeyi tek sahipli yapan kanıt nedir?"* Kanıt yoksa route **çekilir** — hata
vermez, garsona devreder. Ölçüsü hazır: `sessiz_yanlis` sayacı ve `source` dağılımı.

> ⚠ **Ölçüm uyarısı:** çekilme oranı artınca `nl_corpus` **düşer** (LLM'siz koştuğu
> için devir bir kayıptır). Bu değişikliğin ölçüsü `B-1` kurulmadan **okunamaz** —
> `G3`'ün geri alınma sebebi birebir buydu. **Bu yüzden `B-1` sırada `B-2`'den
> öncedir.**

---

### 🔴🔴 `B-3` · KANONİK VARLIK EKSENİ YOK — *«müşteri» beş ad, üç ayrık aile*

**Teşhis.** §3.2 tablosu. `blend` üç aile arasında **kurulamaz**.

**Kök — ve tam olarak nerede eksik olduğu ölçüldü:** `demo/packs/cekirdek/` katmanı
bir **anlam** katmanıdır ve `base_object` taşımaz; içinde `metrikler` (10 kalem) ve
`grain_sozlesmeleri` var. 🔴 **`varliklar` YOK.** Yani ölçülerin kanonik bir sözlüğü
var, **varlıkların (müşteri · malzeme · makine · tedarikçi) yok.**

**Neden kapanmadı.** Bu bir **pack kararıdır**, kod kusuru değil — ve karar hiç
sahiplenilmedi. `OPERASYON-DURUM.md` borç #19 aynı sınıfı (`bakiye`) *"bu bir motor
kusuru değil **katalog kararıdır**"* diye zaten adlandırmış.

**Kök çözüm.** `cekirdek/varlik_sozlugu.yml`: her varlık için **kanonik ad + kimlik
alanı + ad alanı + sinonimler**, küp boyutları ona **bağlanır** (`cekirdek_varlik:
musteri`). `blend`'in eşleşme anahtarı ham boyut adı yerine **kanonik varlık** olur.
`cekirdek_metrik` mekanizması (`app/cekirdek.py`) bunun **ölçü tarafındaki eşleniğidir**
— yani desen zaten kanıtlanmış, ikinci ekseni yok.

⚠ **Bu, açılan borçların en pahalısıdır**: kapanmadan çapraz-küp müşteri sorularının
hiçbiri tam cevaplanamaz ve orkestratör bunu köprüyle **gizlemeye** devam eder.

---

### 🔴 `B-4` · ÇOK SAHİPLİ ÖLÇÜLERDE SAHİP BEYANI BOŞ

**Teşhis.** 13 (canlıda 9) çok sahipli ölçü adı var; katalog bunu modele **ifşa
ediyor** (`_belirsizlik_bloku`) ama *"hangisi doğru"* sorusunun cevabı hiçbir yerde
yazılı değil. `sahiplenilen_terimler` alanı **var**, dolu değil.

**Kanıt.** `katalog_metni.py`'nin kendi ölçümü: *"modelin kararsızlığının **tamamı** bu
dokuzun etrafında dönüyor"* — aynı soru iki kez sorulduğunda üretim yolu 8'de 1,
ham çağrı 8'de 2 farklı `cube_query` üretiyor.
`OPERASYON-DURUM.md` borç #19: `bakiye` iki küpte, fark **₺11,86 milyon**, seçim sessiz.

**Neden kapanmadı.** Ölçüldü ki karar **araca bırakılınca** korpus `%93,2 → %92,6`
düşüyor (`r1_envanteri`). Doğru sonuç çıkarıldı — *karar alan bilgisidir* — ama
**alan kararı da alınmadı**; borç ifşa katmanında bekliyor.

**Kök çözüm.** 13 kalem için **tek oturumluk bir sahiplik turu**: her ad için ya
(a) varsayılan sahip beyan edilir, ya (b) *"beyan yok → route çekilir, garson sorar"*
işaretlenir. **Boş bırakmak üçüncü bir seçenek değildir** — bugün olan da odur ve
maliyeti ₺11,86 milyonluk bir sessiz seçimdi.

---

### 🔴 `B-5` · YÖN BEYANI EKSİK — *«en kötü» bir yöndür ve 125 ölçüde yazmıyor*

**Teşhis.** 173 ölçü tanımının **125'inde** `lower_is_better` beyanı yok (%72).
Beyan yoksa sistem *"çok olan iyidir"* varsayar.

**Kanıt.** `§W-C` (`katalog_metni.py`): *«karbon ayak izini **en kötüden iyiye**
sırala»* → `direction: asc`, yani **en düşük karbon en üste** kondu. Sistem kullanıcıya
tam tersini verdi ve **verdiğini söylemedi**. Aynı sınıf bu turda `ort_gecikme_gun`'de
tekrar üretildi.

**Neden kapanmadı.** `§W-C` **taşıma** işini yaptı (yön işareti `↓` artık katalog
metnine giriyor), ama **doldurma** işini yapmadı: taşınacak veri 173'ün 48'inde var.

**Kök çözüm.** İki adım, ikisi de mekanik:
1. **Kapı**: yeni bir ölçü `lower_is_better` beyanı olmadan pack'e giremez (aynı
   kapı `default_measure` için zaten var).
2. **Toplu doldurma**: 125 kalem birimlerine göre ayrılır (`fire` · `durus` · `sapma` ·
   `gecikme` · `maliyet` · `tuketim` → `true`; `uretim` · `ciro` · `oee` · `verim` →
   `false`), belirsizler **elle**. Bu bir liste icadı değil, **beyan edilmemiş bir
   alanın doldurulmasıdır** (ADR-0008 sınırı içinde).

---

### ◐ `B-6` · İFADE EDİLEMEZLER — *menüde olmayan yemek istenemez*

| kalem | durum @`f9cd3cb` | kalan iş |
|---|---|---|
| `pencere:pay` (*«yüzde kaçı»*) | ✅ **ÇÖZÜLDÜ** (`f9cd3cb`) — kural vardı, **örnek** yoktu; örnek eklenince canlıda `_p_pay_toplam_ciro=%18,12` üretti | 🔴 **kazanç ölçülmedi**: iki canlı soru, **korpus yok** → `B-1` |
| `her <boyut>` (grup başına üstünlük) | ◐ **BEYAN EDİLDİ** (`9f5c2c2`, `§HB`) — sistem artık *«tek satır ürettim»* diyor | 🔴 **yetenek yok**: pencere fonksiyonu (`ROW_NUMBER OVER PARTITION`) `CubeQuery`'de yok |
| `sira` ↔ `order+limit` karışması | ✅ kural sertleştirildi (`§V6`) | ölçülmedi |
| `compare` **alan** değil **enum** | 🔴 açık (`B-G4`) | `5.6` (peer kıyası) hâlâ bloke |

**Kök — ve bu depo aynı dersi üç kez ödedi:** *mutfak o yemeği yapabiliyorsa menüde de
yazmalı; yoksa garson isteyemez ve niteleme cevaptan **sessizce** düşer.*
`§M-6` (`pencere`/`turev`) · `§W-C` (yön) · `§AR/Ö` (örnek) — üçü de aynı sınıf.
`2026-08-07_CEVIRI-SOZLESMESI.md` bunu sayıyla yazmış: `route()` **12 anahtar**
üretebiliyor, şema modele **7** alan sunuyor.

**Kök çözüm.** Bir **yetenek envanteri kapısı**: mutfağın (`wren_service` +
`cube_router`) ürettiği her alan, garsonun şemasında (`intent_semasi`) ya **var**
olmalı ya **bilerek dışarıda** diye beyan edilmeli. Sessiz fark kırmızı verir.
*Bugün bu fark bir belgede yazılı; bir kapıda değil.*

---

### 🔴 `B-7` · ODAK VARLIĞI YOK — diyalog bir şey seçtiğini bilmiyor

**Teşhis.** *«o makinede»* gibi bir takip sorusu, önceki cevabın **hangi satırını**
kastettiğini sisteme söyleyemiyor.

**Kanıt (`4917714` — üç yerleşim ölçüldü, üçü de başarısız):**

| deneme | sonuç |
|---|---|
| yalnız `refined` atlandı | `dim_switch` devraldı → küp `parti` → `oee`, **ölçü değişti** |
| ilk dört basamak atlandı | ölçü doğru, **aynı 33 satır** + bir LLM çağrısı israfı |
| `refine_cube` de atlandı | yine `oee`'ye kaydı |

**Kök (`app/routers/ask.py:4462`).** *"Eksik olan bir kanca değil bir **kavram**:
diyalog durumunda **odak varlığı** yok."* `prev_cq` `order desc` taşır, **seçilmiş
varlığı** taşımaz — zincirdeki hiçbir basamak onu bilemez. Yüklem
(`niyet_tasima.EKSIK_ATIF`) kurulu ve kapılı, ama besleyecek veri yok.

**Neden kapanmadı.** Üç kez **yerleşim** olarak denendi ve üçü de geri alındı; kökün
*bilgi eksikliği* olduğu ancak üçüncü denemeden sonra yazıldı.

**Kök çözüm.** Diyalog durumuna **odak varlığı** alanı: son cevabın satırlarından
kullanıcının işaret ettiği (ya da tek satırsa kendiliğinden) varlık —
`{boyut: "makine", deger: "RAM-2", kaynak: "onceki_cevap_satir_1"}`. Orkestratör bunu
`SORGU → BAGLA → SUZ` ile **zaten ifade edebiliyor**; eksik olan **girdi**.

---

### 🔴🔴 `B-8` · TERS YÖN — *«LLM zaten eşanlamları biliyor, sinonim yazmakla iş bitmez»*

**Kullanıcının önerisi.** Katalogda her terime sinonim yazmak yerine, **LLM'in zaten
bildiği** dil bilgisini kullan: kullanıcının kelimesini **kanonik** terime o çevirsin.

### ⊙ Bu mekanizma ZATEN VAR — ve `off` duruyor

`prompt_enhancer` (`app/routers/ask.py:244` · `demo/packs/features.yml:112`):
`route()` **boş dönerse** ucuz model soruyu katalog terimleriyle yeniden yazar ve
**aynı deterministik yol** tekrar denenir.

🔴 **Ve tasarımı yapısal olarak güvenli** — bu, önerinin en güçlü yanıdır:

> *"LLM YAPI SEÇMEZ. Çıktı bir METİNDİR ve `route()` ona sıfırdan karar verir; model
> uydurma bir terim üretse bile `route()` onu yine reddeder. Enhancer en kötü ihtimalle
> **işe yaramaz**, yanlış cevap **üretemez**."*

### 🔴 AMA HİÇ DÜRÜST ÖLÇÜLMEDİ — üç kez ölçüldü, üçü de bir şey ölçmedi

| # | koşum | sonuç | gerçekte ne oldu |
|---|---|---|---|
| 1 | korpus **katalog sinonimlerinden** üretildi | `0/12` kurtarma | **yanlış nüfus**: katalog sinonimleri `route()`'ta *belirsizlikten* (R1) düşer, ve *"yeniden yazmak belirsizliği çözmez"* |
| 2 | `--ab-kurtarma` **`--live` olmadan** koşuldu | `0/14` kurtarma | `tests.conftest` sağlayıcıyı `rule`'a sabitledi → **enhancer'ın LLM'i yoktu**. *"Ölçüm «ölçmedim» diyordu"* |
| 3 | tek koşumla karar verildi | ✔ | **ikinci sağlayıcıda tersine döndü** (`14/15 → 15/15`, `lab/garson.py:33`) |

> Yani **kullanıcının önerdiği mekanizma, bu depoda hiç ölçülmemiştir** — üç *"kazanç
> yok"* kaydının hiçbiri bir kazanç ölçümü değildir. Bu, `B-1`'in en pahalı somut hâli.

### ⊙ ÖLÇÜM — sinonim korpusu ikiye ayrılıyor *(1.432 beyan, statik)*

| sınıf | sayı | LLM türetebilir mi | sahibi kim OLMALI |
|---|---|---|---|
| **A · yazım/çekim varyantı** — teknik ad veya etiketle **kök paylaşıyor** (`şikayet`↔`şikâyet`, `hasilat`↔`hasılat`, `renkler`↔`renk`, `hattı`↔`hat`) | **788** *(%55)* | ✅ — aslında LLM'e bile gerek yok, bir **normalleştirici** işi | ❌ **elle yazılmamalı** |
| **B · kök paylaşmıyor** — bilgi gerekiyor | **644** *(%45)* | ⚖ **ikiye ayrılır** ↓ | |
| **B1 · genel dil eşanlamı** (`tezgah`↔`makine`, `statü`↔`durum`, `firma`↔`müşteri`, `ciddiyet`↔`şiddet`, `neden`↔`sebep`, `çevre`↔`sürdürülebilirlik`) | | ✅ **LLM bilir** | ❌ elle yazılmamalı |
| **B2 · YEREL SÖZLEŞME** (`zayiat`↔`fire` · `iade`↔`şikâyet` · `ham`↔`kumaş cinsi` · `dE` · `TEP` · `RFT`) | | 🔴 **BİLEMEZ** | ✅ **beyan ŞART** |

### 🔴 Kırılma noktası — ve neden *"hepsini LLM yapsın"* çalışmaz

**LLM Türkçeyi bilir, senin şirketini bilmez.** `fire`ye burada `zayiat` denmesi bir
**dil** olgusu değil, bir **yerel sözleşmedir**. Daha da net bir örnek `sikayet`
küpünde duruyor: `iade` → `şikâyet` eşlemesi bir eşanlam **değil**, bir **iş
kuralıdır** (*bu işletmede iade, şikâyet olarak kaydedilir*). Hiçbir genel model bunu
türetemez; **hiçbir yerde yazmazsan hiçbir şey bilemez.**

⊙ Ve bu **ölçülmüş bir olaydır**, varsayım değil: sözlüksüz dönemde **9/9 `cube:null`**.
Model Türkçe biliyordu; *bu şirkette* `fire`ye ne dendiğini bilmiyordu.

> **Ters yön listeyi KALDIRMAZ, KÜÇÜLTÜR — ama çok küçültür.**
> Bugün elle taşınan **1.432** beyanın **%55'i** (sınıf A) hiç yazılmamalıydı ve
> sınıf B1'in tamamı da yazılmamalıydı. Geriye kalan **B2**, kataloğun **gerçek**
> içeriğidir ve o zaten *"sinonim"* değil **kurum bilgisidir**.

### 🔴 Ve *"iş bitmez"*in gerçek cevabı: LİSTEYİ KULLANIM YAZSIN

Altyapı **zaten kurulu**, yalnız **bağlanmamış**:

| parça | durum |
|---|---|
| `_apply_synonym_overlays` (`wren_service.py:925`) | ✅ control-plane DB'den **onaylı** overlay'leri şemaya **deploy'suz** bindiriyor; **aday kuyruğu canlıya inmiyor** |
| terfi kuralı (`cube_router.py:11`) | ✅ *"Yeni ifadeler önce LLM yolunda yaşar; buraya terfi ancak (1) log kanıtı, (2) tam-parse ile"* |
| 🔴 **eksik halka** | enhancer'ın **başarılı** yeniden yazımları aday kuyruğuna **yazılmıyor** |

**Kök çözüm — üç adım, üçü de mevcut parçaları bağlıyor:**

1. **Sınıf A'yı elden al.** `route()` ve katalog, teknik ad + `label` üzerinden
   **kök/çekim normalleştirmesi** yapsın. 788 beyan elle bakımdan çıkar.
2. **`prompt_enhancer`'ı `off`'tan çıkar — ama KURTARMA yolu olarak kalsın.**
   Birincil yapmak her soruya bir LLM çağrısı bindirir (`P-1`: `/ask` zaten 47→177 ms).
   Kurtarma yolu, route'un **zaten çözdüğü** sorulara sıfır maliyet bindirir ve
   değerinin tamamı **route'un çözemediği** nüfustadır.
   🔴 **Ön koşul: dürüst ölçüm** — `--ab-kurtarma --live`, **iki koşum** (`KURAL G-1`).
3. **Başarılı yeniden yazımı ADAY SİNONİM olarak hasat et.** `zayiat → fire` bir kez
   çözüldüğünde kanıtıyla (soru · sıklık · çözülen küp) kuyruğa düşer; onaylanınca
   overlay'e biner ve **sonsuza kadar deterministik ve bedava** olur.
   → *Liste elle yazılmaz, **kullanımdan hasat edilir**.*

### ⚠ İKİ SERT SINIR — bunlar olmadan ters yön sessiz-yanlış üretir

| sınır | gerekçe |
|---|---|
| 🔴 **Enhancer BELİRSİZLİK ÇÖZMESİN** | Çıplak `bakiye`yi *«cari bakiye»* diye yeniden yazarsa, **₺11,86 milyonluk sessiz seçimi metne gömer** ve netleştirme chip'i onu artık göremez. Zaten ölçülmüş: *"katalog sinonimleri route'ta belirsizlikten düşer ve **yeniden yazmak belirsizliği çözmez**."* Enhancer **normalleştirir**, karar **vermez** |
| 🔴 **Yeniden yazılan metin İZDE görünsün** | Bugün doğru yapılıyor (`provenance_soru`: `question_original` + `question_normalized`). Kullanıcının görmediği bir yeniden yazım, cevabın sahibini gizler |

---

### 🔴🔴 `B-9` · PLAN SÜREKLİ REDDEDİLİYOR — *ve sebep modelin beceriksizliği değil, **fişin eksikliği***

**Kullanıcının canlı kaydı (2026-08-10 03:33):**

```
plan REDDEDİLDİ (adım 1: `oee`'de süzülemeyecek alan(lar): `None`
                       · tanınmayan süzgeç operatörü: `equals`) → bir kez düzeltme isteniyor
```

Bu **tek satırda iki ayrı kusur** var ve ikisi de **`§AR`'nin üçüncü tekrarıdır**.

#### (a) 🔴 `equals` — operatör sözlüğü GARSONA HİÇ VERİLMİYOR

⊙ **Ölçüldü, dört tüketici karşılaştırıldı:**

| tüketici | operatör bilgisi |
|---|---|
| `intent_semasi.py:297` — Intent **şeması** | ✅ `enum: MOTOR_OPERATORLERI` → model geçersiz ad **üretemez** |
| `llm.py:365` — Intent **istemi** | ✅ örnek: `{"dimension":…,"operator":"eq","value":…}` · `:489` *«X hariç»→`neq`* |
| 🔴 `plan_semasi.py` — **PLAN İSTEMİ** | **`operator` kelimesi 0 (SIFIR) kez geçiyor** — ne enum, ne kural, ne örnek |
| ◐ `plan_onarim.gerekce` — **onarım turu** | *«tanınmayan operatörü: `equals`»* der, **geçerlisini SÖYLEMEZ** |

**Kök.** `MOTOR_OPERATORLERI` bir **tek sahip** olarak kuruldu (`§M-6`, motorun kendi
hata mesajından birebir ölçülerek: `eq neq in not_in gt gte lt lte contains starts_with
is_null is_not_null`) — ama **plan istemi o sahibin müşterisi değil**. Model `equals`
yazıyor; İngilizcede son derece makul bir tahmin, ve onu düzeltecek hiçbir işaret yok.

⚠ **Bu, `§AR`'nin birebir tekrarıdır** ve `§AR` **dün** kapandı: `pencere`/`turev` alan
rehberi yalnız Intent isteminde yazılıydı, plan istemi onu **hiç görmüyordu**. Rehber
`ALAN_REHBERI` olarak tek sahibe taşındı — **ama operatör sözlüğü taşınmadı.**
*Bir sınıf hatayı bir örnekte kapatmak, sınıfı kapatmaz.*

#### (b) 🔴 `None` — süzgecin BİÇİMİ hiç gösterilmiyor

`gerekce()` `f.get("dimension")` okuyor; alan **yok** → `None` basılıyor.
`plan_semasi.py`'de `filters` yalnız **bir kez** geçiyor (`:588`) ve orada da sadece
*"`filters` `cube_query`'nin **içine** yazılır"* deniyor — **süzgeç nesnesinin şekli
(`dimension`/`operator`/`value`) plan istemine hiç yazılmamış.**

⚠ Ve mesajın kendisi de kusurlu: **`None` bir alan adı değildir**, *"alan hiç
yazılmamış"* demektir. Model red mesajını okuyup *«`None` diye bir alan mı aramışım?»*
diye düşünür — teşhis, teşhis olmayı burada bırakıyor.

#### (c) ◐ Onarım turu *"neyin yanlış olduğunu"* söylüyor, *"doğrusunu"* söylemiyor

🔴 **Ve bu dersin çözümü AYNI FONKSİYONDA, dört satır yukarıda duruyor.**
`gerekce()`'nin kendi docstring'i şunu yazmış:

> *⊙ Ölçüldü (canlı `II14`·`D2`): «`parti` sorgusu beyaz listeden geçmedi» içeriksiz bir
> teşhisti ve **onarım turu da onu okuyordu** — model neyin olmadığını biliyor, neyin
> **olduğunu** bilmiyordu; **ikinci deneme de düştü**.*

Çözüm boyutlar için **uygulandı** (`bilinen_boyutlar()` → *«var olanlar: makine, renk,
vardiya…»*). **Operatör dalına uygulanmadı.** Yani ders öğrenildi, yazıldı, bir dalda
uygulandı — komşu dalda uygulanmadı.

#### (d) ⚠ Ve bu red, **onarım katmanının kendi ölçütüne göre** yanlış katmanda

`plan_onarim.py`'nin üç-seviye doktrini: *seviye 1 istem · seviye 3 mekanik onarım ·
seviye 2 LLM düzeltme turu (en pahalı)*. `equals → eq` **mekanik olarak tek anlamlıdır**
— motorun 12 operatöründen `equals`ın kastedebileceği tam olarak bir tane var.
Yani bugün **bilinen bir cevap ikinci kez satın alınıyor**; modülün kendi cümlesiyle:
*"Eşlemeyi karar merciine göndermek, karar merciini meşgul eder ve kararı ucuzlatır."*

🔴 **Ve uyarı sistemi zaten kurulu, kimse okumamış:**
> *"İzde bir onarım sık görünüyorsa istem (seviye 1) yetersiz demektir. Sessiz bir
> onarım, düzeltilmesi gereken bir istemi süresiz olarak gizler."*

Kullanıcının loglarda gördüğü tam olarak bu sinyaldir ve *"istem yetersiz"* diyor.

#### Kök çözüm — dört adım, üçü mekanik

| # | iş | katman |
|---|---|---|
| 1 | **`ALAN_REHBERI`'ne süzgeç bölümü ekle** — operatör listesi `_ops.MOTOR_OPERATORLERI`'nden **üretilerek** (elle yazılmış bir kopya `§M-6`'nın ölçtüğü kusuru geri getirir) + `{"dimension","operator","value"}` **örneği** | seviye 1 · istem |
| 2 | **`gerekce()`'ye operatör kuyruğu**: *«tanınmayan: `equals` — geçerliler: eq, neq, in, …»*. `bilinen_boyutlar()`'ın birebir eşleniği | seviye 2 · onarım girdisi |
| 3 | **`None` mesajını düzelt**: alan eksikse *«süzgeçte `dimension` alanı hiç yazılmamış»* — `None` bir ad değildir | teşhis |
| 4 | **Mekanik eşlemeleri seviye 3'e al**: `equals→eq` · `not_equals`/`ne`→`neq` · `>`→`gt` … **beyan ederek** onar; LLM turu harcanmasın | seviye 3 · onarım |

#### ⚠ ÖLÇÜLMEYEN — ve ilk yapılması gereken

🔴 **Red oranı bir sayı değil, bir izlenim.** `plan_garson.SAYAC` (`onarildi` · red)
zaten var; **hiçbir kapı okumuyor** ve `lab/` hiçbir aleti *"kaç plan reddedildi,
kaçı onarıldı, red sebepleri neydi"* diye sormuyor. Kullanıcı bunu **loglardan gözle**
tespit etti — yani sistem kusuru **anlatıyor** ama **saymıyor**.

**Önce sayaç yayımlanır** (red sayısı · onarım tutma oranı · sebep dağılımı), sonra
düzeltmeler ölçülebilir. *Sebep dağılımı olmadan hangi düzeltmenin kaç redde
dokunduğu bilinemez.*

---

### 🔴🔴 `B-10` · BAYRAK ENVANTERİ — **49 bayrak, `on` olan SIFIR**

⊙ **Ölçüldü (`demo/packs/features.yml` + `app/features.py`, 2026-08-10):**

| durum | sayı |
|---|---|
| 🟢 `on` | **0** |
| ◐ `beta` | **21** |
| ⭘ `off` | **28** |
| 🔴 kayıtta var, `features.yml`'de **YOK** *(tenant açamaz)* | **5** — `diyalog_bellegi` · `niyet_izi` · `sosyal_sinif` · `t2_anlatici` · `ayni_grain_gocu` |

🔴 **Merdivenin çıkışı yok.** Ödenmiş, testli, belgelenmiş **49** yetenekten hiçbiri
*"burası son"* diyebileceğimiz bir duruma ulaşmadı. `off → beta` geçişleri var,
`beta → on` geçişi **hiç yok** — ve hiçbir bayrağın yazılı bir **`on` şartı** yok.

⚠ Ve dördü (`diyalog_bellegi` · `niyet_izi` · `sosyal_sinif` · `t2_anlatici`) **çalışma
zamanı davranışıdır ama rollout yüzeyi yoktur**: hiçbir kiracı onları açamaz. `niyet_izi`
bu haftanın işi (`KÖK-1 Faz 1`); `diyalog_bellegi` garson fazının ana teslimatı (`G2`).
*Bir kill-switch yalnız kodda varsa yarımdır* kuralı yazıldı — **açma anahtarı** için
aynısı yazılmadı.

### 🔴 ÖLÇÜLMÜŞ SORUNLARIMIZI ÇÖZEN, AMA KAPALI DURAN YETENEKLER

Aşağıdakiler *"ilerisi için güzel fikir"* değil — **kendi ölçümümüzle** bir borcumuza
karşılık gelen, **kodu inmiş** yeteneklerdir.

| bayrak | durum | ne çözer — ve ölçüsü | hangi borç |
|---|---|---|---|
| 🔴🔴 **`varsayilan_donem`** | `off` | **Korpusun %13,7'si** dönem netleştirmesi. Canlı turlarda **on kez** ölçü·kırılım·sıralama çözülmüşken **yalnız dönem** yüzünden cevap gelmedi. Açıkken verinin son 12 ayı alınır ve **görünür biçimde söylenir** | *«anlamadım» yok* kuralı · kapsam |
| 🔴🔴 **`oylama_paydasi`** | `off` | **Kalibrasyon yalanı**: bugün *1 cevap + 2 «bilmiyorum»* → uyum **%100** görünüyor. *"Şüphenin en yüksek olduğu durum en emin görünür."* | `T-2` |
| 🔴🔴 **`netlestirme_onceligi`** | `off` | Gerçekten belirsiz ölçüde (`bakiye` → `cari｜mizan`) netleştirme chip'i Intent'ten **ÖNCE** gelir. **`T-2`'nin çalışma-zamanı yarısı zaten yazılmış** | `T-2` · `T-4` |
| 🔴 **`katalog_belirsizlik`** | `off` | Çok sahipli ölçüler katalogda ayrı bölümde. Ölçüldü: aynı soru iki kez → **8'de 1** farklı sorgu | `T-4` |
| 🔴 **`cekirdek_katman`** | `off` *(+iki sahipli)* | Evrensel metrik sözlüğü + **grain sözleşmesi**. `ticaret` üç ERP'de aynı ad/sinonim **farklı grain** → karşılaştırılamaz sayı, beyan yok. **Kanonik varlık ekseninin evi burasıdır** | `T-3` |
| 🔴 **`prompt_enhancer`** | `off` | Ters yön — bkz. `B-8` | `T-8` |
| 🔴 **`llm_sema_kisitli`** | `beta` | Ad **enum**'a bağlanır → model geçersiz ad **üretemez**. `T-9`'un yapısal çözümü. ⚠ **Mevcut sağlayıcıda NO-OP** (`oneOf` yok) — yani bugün `beta` ama **etkisiz** | `T-9` |
| 🔴 **`oylama_cekirdek`** | `beta` | *"Oylama zenginliği CEZALANDIRIYORDU"* — `order`/`limit`/`pencere` yazmayan iki oy bedavaya uyuşuyor, yazan tek oy yalnız kalıyor. **Kazanan 1 oy → 7 kez** | `T-6` |
| 🔴 **`tazelik`** | `off` | Veri sonu tarihi **hiç söylenmiyor**; kullanıcı üç turunu bunu keşfetmeye harcadı (borç #16e) | §C ölçüt 12 |
| ◐ **`hedef_kiyasi`** | `off` | Grafikteki referans çizgisi **hedef değil ortalama** — *"kod bunu `interpret.py`'de itiraf ediyor"* | sessiz-yanlış |
| ◐ **`tur_takip`** · **`tur_paylas`** | `off` | *"Çalışan, testli bir yetenek **BİR KELİME** yüzünden kullanıcıya kapalıydı"* — motor yazılmıyor, yalnız **erişim** açılıyor | ucuz kapsam |
| ◐ **`hizli_derin`** | `beta` | UI'da anahtar **vardı**, sunucu alanı **yok sayıyordu** — ölü kontrol. Açmak **sıfır** yeni davranış | dürüstlük |

⚠ **Dışarıda tutulanlar meşru:** `embed` (P0 — `motor_cls` kapalı, güvenlik sınırı
ölçülemiyor) · `kanal_kimlik` (kimliği çıkarımla kurmak RLS'i çıkarımla kurmaktır) ·
`public_api` · `ossie_*` · `mcp_yuzeyi` (genişleme, taban değil).

---

## 4b · 🔴🔴 KORPUS BU KARARLARDA HAKEM DEĞİLDİR — ve düşüş bazen BAŞARIDIR

Yukarıdaki bayrakların çoğu *"korpus düştü"* denerek `off` bırakıldı ya da geri alındı.
**Bu gerekçe, bu bayrak sınıfı için yapısal olarak geçersizdir.**

### Neden — üç ayrı sebep aynı sayıyı düşürür

`nl_corpus` **`rule` sağlayıcıyla** koşar: içinde **hiç LLM yoktur**. Dolayısıyla:

| # | korpus düşüşünün sebebi | üretimdeki karşılığı |
|---|---|---|
| **(a)** | 🔴 **gerçek gerileme** — sistem bir şeyi bozdu | ✅ kötü, geri al |
| **(b)** | 🟢 **route çekildi, tur garsona devredildi** | ✅ **KAZANÇ** — üretimde orada gerçek bir LLM var ve **doğru cevaplıyor** (`renk grubuna göre fire` bunu birebir gösterdi). Korpusta LLM olmadığı için bu **kayıp** görünür |
| **(c)** | 🟢 **totolojik doğrular düştü** — korpus sorularının **≥%97,1'i katalog türevidir**: soru da beklenen cevap da **aynı kaynaktan** üretiliyor. Route'un kendine emin biçimde yanlış eşleştiği bir vaka, beklenen cevap da aynı eşleşmeden türediği için **DOĞRU sayılabilir**. Bu vakalar garsona geçince korpus düşer — çünkü **sessiz-yanlış sayılmayı bırakır** | ✅ **KAZANÇ** |

> 🔴 **Yani korpustaki bir düşüş, üç farklı olayın toplamıdır ve ayrıştırılmadan hiçbir
> karar verilemez.** Bugün ayrıştırılmıyor: tek bir yüzde basılıyor.

⊙ **Ödenmiş fatura:** `G3` (*"cevapsız dal cevaplı yolu kesemez"*) korpus `%95,1→%93,5`
dedi diye **geri alındı**. O `%1,6`'nın **(a)** mı **(b)** mi olduğu **hiç sorulmadı** —
ve mekanizma olarak **(b)** idi.

⊙ **Karşı örnek — korpusun HAKLI olduğu yer:** `§EB/A` (`18c90c8`) `sessiz_yanlis`
12→18 dedi ve **haklıydı**, çünkü o bir **kapsam** değişikliğiydi. Kapsamın ölçüsü
korpustur; **yol dağılımının** ölçüsü değildir.

### 🔴 Bunun yapısal düzeltmesi — kapı çıktısı ikiye ayrılır

Kapı tek bir *%* yerine şunu basmalı:

```
route  : %X   (n=…)     ← kapsam ölçüsü — korpus BURADA hakemdir
garson : %Y   (n=…)     ← T-1'in konusu; bugün n=4
devir  : %Z             ← route→garson devredilen oran (kayıp DEĞİL, DEVİR)
sessiz_yanlış: N        ← doğruluk vetosu — HER ZAMAN hakem
```

*Tek sayı, iki yolun ortalamasıdır ve hangi yolun bozulduğunu gizler.*

---

## 4c · 🔴🔴 KESİN EMİR — BAYRAK GELİŞTİRME DOKTRİNİ

> Kullanıcı kararı (2026-08-10): *"bir özellik sorun çözecekse geliştirmesi emirdir,
> o bayrak `on` olana kadar devam edilir; korpusla/kapıyla vazgeçmeyiz."*

**`E-1` · Bir bayrak ölçülmüş bir sorunu çözüyorsa, geliştirmek EMİRDİR.**
`off` bırakmak bir karar değil bir **erteleme**dir ve ertelemenin de bir sahibi ve
gerekçesi olmak zorundadır. *Ödenmiş, testli, kapalı duran bir yetenek, harcanmış bir
emektir.*

**`E-2` · Hiçbir bayrak `nl_corpus` (rule) tek başına düştü diye reddedilemez.**
Red ancak şu üçlü ile verilir: **(1)** korpus, **(2)** `--slice llm` ya da canlı tur,
**(3)** düşüşün `(a)/(b)/(c)` ayrımı. Ayrım yapılmadıysa karar **verilmez** — `⊘` yazılır.

**`E-3` · `sessiz_yanlis` mutlak vetodur, korpus yüzdesi değildir.**
Bir bayrak kapsamı düşürüp `sessiz_yanlis`'ı da düşürüyorsa bu bir **kazançtır**:
*bir soruyu cevaplamamak, yanlış cevaplamaktan iyidir* — ve tersi asla doğru değildir.

**`E-4` · Her bayrağın yazılı bir `on` ŞARTI olmalı.**
`on` şartı olmayan bir bayrak `beta`'da süresiz yaşar — bugün **21 bayrak** o durumda ve
**hiçbiri** `on` olmadı. Şart bayrak kaydına (`app/features.py`) yazılır.

**`E-5` · İki koşum kuralı (`KURAL G-1`) LLM'li her kararda geçerlidir.**
Ölçüldü: `prompt_enhancer` kararı tek koşumla verildi ve **ikinci sağlayıcıda tersine
döndü** (14/15 → 15/15). Tek koşum karar değildir.

**`E-6` · Bir bayrağın rollout yüzeyi yoksa, o bayrak yoktur.**
Bugün **5** yetenek `features.yml`'de değil; dördü çalışma-zamanı davranışı ve hiçbir
kiracı açamıyor. *Bir kill-switch yalnız kodda varsa yarımdır* — **açma anahtarı** için
de aynısı geçerlidir.

**`E-7` · Sıcak yola maliyet eklemek ayrı bir karardır ve ölçülür.**
`/ask` **47 → 177 ms** (×3,8) ve **latency tavanı kapısı yok** (`P-2`). Bir bayrak
kaliteyi artırıp gecikmeyi ikiye katlıyorsa bu bir takastır, kazanç değil — ikisi
**birlikte** raporlanır.

---

## 4d · ⚠ SİNONİM İÇİN MALİYETSİZ YOL — *ayrı LLM turu YOK*

Kullanıcı uyarısı: *"belki bunu sorgu içinde çözeriz, ayrı LLM sorgusu olmayacak —
dikkat, çok vakit ve maliyet kaybı olur."* **Doğru ve `E-7`'nin birebir uygulaması.**

Bugünkü `prompt_enhancer` **ikinci bir LLM turudur** (yeniden yaz → route'u tekrar dene).
Ama Intent çağrısı **zaten** kataloğu görüyor ve **zaten** koşuyor. O yüzden:

| yol | ek LLM çağrısı | ne verir |
|---|---|---|
| bugünkü enhancer | 🔴 **+1 tur** | route boş dönerse kurtarma |
| 🟢 **önerilen: Intent'in İÇİNDE** | **0** | Intent şemasına tek bir alan eklenir — `eslesen_terim: {"kullanicinin_sozu": "zayiat", "katalog_adi": "toplam_fire_kg"}`. Model **zaten** bu eşlemeyi yapıyor; yalnız **söylemesi** isteniyor |

Kazanç iki katlı:
1. **Sıfır ek maliyet** — aynı çağrı, bir alan daha.
2. **Hasat** — `zayiat → toplam_fire_kg` eşlemesi kanıtıyla **aday sinonim kuyruğuna**
   düşer; onaylanınca `_apply_synonym_overlays` ile deploy'suz canlıya biner ve
   **bir daha hiç LLM gerektirmez**.

> Yani ters yön bir **çağrı** olarak değil, bir **alan** olarak eklenir; ve sistem
> kendi sözlüğünü **kullanımdan** yazar. Enhancer o zaman yalnız gerçek kurtarma
> vakalarına (route boş **ve** Intent de çözemedi) kalır.

⚠ `B-8`'in iki sert sınırı burada da aynen geçerlidir: **belirsizlik çözülmez**
(`bakiye` eşlemesi kuyruğa **düşmez**), ve eşleme **izde görünür**.

---

## 5 · SIRA — ve neden bu sıra

| # | borç | neden bu sırada |
|---|---|---|
| **1** | `B-1` garson korpusu | 🔴 **kilit taşı.** Bu kurulmadan `B-2`'nin kazancı **okunamaz**; `G3` tam bu yüzden haksız yere geri alındı. Ayrıca `B-6`'nın çözülen kaleminin (`pencere:pay`) kazancı da bugün ölçüsüz |
| **2** | `B-0` katalog envanteri | ucuz, mekanik ve **sonraki her borcun ilerleme ölçüsü**. Sayısı olmayan borç kapanamaz |
| **3** | `B-2` çürütülebilir kesinlik | kullanıcının tezinin **doğrudan** uygulanması; `B-1` hazır olunca ölçülebilir hâle gelir |
| **4** | `B-3` kanonik varlık ekseni | **en yüksek tavan** ama en büyük iş; pack kararı + göç. `blend`i yapısal olarak açan tek şey |
| **5** | `B-4` sahip beyanı | tek oturumluk alan kararı; ₺11,86 milyonluk sessiz seçimi kapatır |
| **6** | `B-5` yön beyanı | mekanik + kapı; *«en kötü»* sorularındaki sessiz-yanlışı bitirir |
| **7** | `B-6`/`B-7` | `B-7` orkestratörün **elindeki** yeteneği kullanılabilir kılar; `B-6`'nın kalanı (`her <boyut>`, `compare` alan) motor işidir |

⚠ **`B-9` (plan reddi) bu sıranın DIŞINDA ve ÖNÜNDEDİR.** Sebebi: dört adımının üçü
**mekanik** (bir istem eki · bir mesaj kuyruğu · bir eşleme tablosu), hiçbiri karar
gerektirmiyor, ve **her red bir LLM çağrısı + gecikme** demek — yani bedeli her gün
ödeniyor. `B-8` ise `B-1`'e bağımlıdır: enhancer'ın kazancı, garson korpusu olmadan
**üçüncü kez** ölçülemez.

> ⚠ **`B-3` bilinçli olarak dörde kondu, bire değil.** En büyük kazanç orada ama
> ölçülemeyen bir kazanç, bu depoda üç kez geri alınmış bir kazançtır.

---

## 6 · 🔴 BU BELGENİN DÖNGÜDEKİ YERİ — **bağlayıcı**

1. Bu yedi borç `OPERASYON.md §2c`'de listelidir ve **her demet kapanışında** gözden
   geçirilir: *hangisi kıpırdadı, hangisi ölçüldü, hangisi hâlâ ölçüsüz.*
2. Bir borcun **kapandığı**, ancak `OPERASYON-DURUM.md`'ye **sayıyla + HEAD damgasıyla**
   yazıldığında geçerlidir. *Ölçülmemiş bir kapanış, kapanış değildir.*
3. Bu dosya `denetim/` altındadır → **değiştirilmez**. Durum takibi
   `OPERASYON-DURUM.md`'de yürür; yeni ölçüm **yeni tarihli yeni dosyadır**.
4. Bir borç *"geçersiz"* bulunursa **silinmez** — çürüten ölçümle birlikte
   `OPERASYON-DURUM.md`'de işaretlenir (`MIMARI.md §10`).

---

## 7 · BU RAPORUN SINIRLARI — *ölçülmeyenler*

| ⊘ | ne ölçülmedi | sonucu |
|---|---|---|
| ⊘ | **hiçbir test/kapı koşulmadı** | buradaki hiçbir sayı bir kapı çıktısı değildir |
| ⊘ | **canlı derlenmiş şema okunmadı** | §3.1 sayıları statiktir; canlıdan sapması `B-0`'ın konusudur |
| ⊘ | `B-1`…`B-7` düzeltmelerinin **kazancı** | hiçbiri denenmedi; hepsi teşhis + tasarım |
| ⊘ | orkestratörün kendi katkısı | *"tavan açtı"* iddiası bu turun canlı gözlemine dayanıyor, **sayıya değil** |
| ⚠ | `2026-08-09_KAPI-YAVASLAMASI-TESHISI.md` | indekste *"DÖNGÜ KURALINA DAHİL"* yazıyor ama `OPERASYON.md`'de **hiç geçmiyordu** — bu turda `§2c`'ye bağlandı. *Bir belgeyi «döngüye dahil» ilan etmek, onu döngüye koymak değildir.* |

---

*Bir mimari, en çok güvendiği basamağı en kör hâliyle koşturuyorsa, kusur o basamakta
değil onu besleyen menüdedir.*
