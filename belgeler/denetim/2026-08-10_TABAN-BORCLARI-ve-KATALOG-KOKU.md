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

1. 🔴 **KASET ÖNCE, PAYDA SONRA** — ⟵ ⚠ **sıra DÜZELTİLDİ (kullanıcı, 2026-08-10):**
   *"binlerce canlı test API'yi tıkar."* Doğru. Payda **canlı çağrıyla** büyütülmez:
   canlı yanıt **bir kez** kaydedilir (`lab/garson.py --live --kaset`), sonraki her
   koşum **diskten** koşar → **koşum başına sıfır API**. Ayrıntı `§4g`.
2. **Paydayı kasetle büyüt** (4 → ~40-60): bu turun her `§`-kodlu canlı bulgusu
   (`§SY` · `§EB` · `§HB` · `§AR/Ö` · `§AT` · `§W-C` · `§V6`) bir kasete dönüşür.
   Bunlar **zaten canlı koşuldu**; kaydedilmedikleri için tekrar edebilirler.
   ⚠ Kaset **(soru + istem sürümü)** ile anahtarlanır — istem değişince **bayattır**.
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
2. 🔴🔴 **`prompt_enhancer` BUGÜNKÜ BİÇİMİYLE AÇILMAZ — ve sebep ölçüm değil, MİMARİ.**
   ⟵ ⚠ **Bu madde DÜZELTİLDİ (kullanıcı, 2026-08-10):** ilk yazımı *"ölçülmedi, ölç ve
   aç"* diyordu. Kullanıcının hatırlattığı gerçek gerekçe **bayrağın kendi yorumunda
   yazılı**: *«`off` — sıcak yola LLM çağrısı ekliyor»*. Ve ölçtüm: **haklı, üstelik
   sandığımızdan ağır** — bkz. aşağıdaki `§4e`. Enhancer **ikinci bir SERİ tura**
   dayanıyor; borç *"ölçülmemiş bir bayrak"* değil, **yanlış biçimde tasarlanmış bir
   mekanizmadır**. Doğru iş onu ölçmek değil, **turu ortadan kaldırmaktır** (`§4d`).
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

**`E-8` · 🔴🔴 SICAK YOLA SERİ İKİNCİ LLM TURU EKLENEMEZ — ölçümle bile açılmaz.**
Bu bir takas değil bir **sınırdır**. `consistency_k=3` örnekleri paralel koştuğu için
Intent yolu **tek turdur**; girdisi bir öncekinin çıktısı olan her mekanizma
**paralelleştirilemez** ve kullanıcıyı ikinci kez bekletir. Ölçüldü: `llm` bütçesi
**20.000 ms**, Discovery **12.567 ms**, ve gerçek dilde route **%93,3** pes ediyor —
yani *"yalnız route boş dönünce"* bir güvence değil. 🔴 **Böyle bir bayrak `off`
bırakılmaz, YENİDEN TASARLANIR:** yetenek var olan turun **içine bir alan** olarak
girer (`§4d`). *Fikir doğruysa taşıyıcısı değişir, fikir atılmaz.*

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

### 🔴🔴 VE SORUNUN BİÇİMİ DE DEĞİŞMELİ — *açık üretim değil, NOKTA ATIŞI*

> Kullanıcı (2026-08-10): *"LLM de tüm eş anlamlıları bulmayacak; **katalogdaki
> kelimelerden birinin eş anlamlısı var mı** diye bakacak — yani nokta atışı."*

**Bu, `§4d`'nin ilk yazımından daha iyi ve sebebi yapısal.** İki soru biçimi
karşılaştırıldığında:

| | ❌ **açık üretim** *(«soruyu kanonik Türkçeye çevir»)* | ✅ **kapalı seçim** *(«bu kelimenin katalogda karşılığı var mı?»)* |
|---|---|---|
| çıktı | serbest **metin** | katalogdan **bir ad** ya da **«hiçbiri»** |
| doğrulanabilir mi | 🔴 **hayır** — ancak `route()`'u tekrar koşarak anlaşılır | ✅ **evet** — dönen ad beyaz listede **deterministik** sınanır |
| *«bilmiyorum»* diyebilir mi | 🔴 **hayır** — her zaman *bir* yeniden yazım üretir | ✅ **evet**, ve `zayiat` gerçekten eşanlam değilse doğru cevap **odur** |
| hasat birimi | bir **cümle** — eşlemeyi ayrıca çıkarman gerekir | ✅ **(kelime → katalog_adı)** çifti — kuyruğa **doğrudan** girer |
| deponun doktrini | — | ✅ `llm_sema_kisitli`: *"model var olmayan bir adı **ÜRETEMEZ**"* · *«hiçbiri» dalı korunur* |

🔴 **Ve girdisi ZATEN VAR, üretmeye gerek yok.**
`cube_router.partial_unknowns(q, schema)` tam olarak şunu döndürüyor: *"hiçbir cube
sözlüğünde karşılığı olmayan kelimeler"*. Yani *nokta atışının* hedef listesi
**deterministik olarak** hazır — modele bütün soruyu vermeye gerek yok, **artakalan
kelimeleri** vermek yeter.

### 🟢 VE BU YÜZDEN SICAK YOLDA HİÇ KOŞMASI GEREKMEZ — en büyük kazanç

`uncovered_words` **zaten kütüğe yazılıyor** ve `§M7` ile **yeni düzeltildi** (eskiden
Türkçe harflerden bölünüp `nda` 36 · `baz` 29 · `duru` 16 kaydediyordu; 769 turluk
ölçümde **196 satırın 115'i (%58,7)** parçaydı).

> Yani elimizde, **kullanım tarafından yazılan**, sıklık sıralı bir *"sistemin
> bilmediği kelimeler"* listesi var.

**Doğru yerleşim — üç katman:**

| # | katman | ne zaman koşar | maliyet | ne verir |
|---|---|---|---|---|
| 🟢 **1** | **ÇEVRİMDIŞI HASAT** *(birincil)* | günde/haftada bir, **toplu** | 🔴 **sıcak yolda SIFIR** — tek bir toplu çağrı | en sık `uncovered_words` → kapalı seçim → **aday kuyruğu** |
| 🟢 **2** | **TUR İÇİ ALAN** (`eslesen_terim`) | var olan Intent turunun **içinde** | **0 ek tur** | route'un kaçırdığı ama Intent'in çözdüğü eşleme |
| ⭘ **3** | enhancer *(ikinci seri tur)* | — | 🔴 `E-8` **yasak** | — |

⊙ **Sonuç:** sistem sözlüğünü **kullanımdan** öğrenir, kullanıcı **hiç beklemez**, ve
API maliyeti soru başına değil **kelime başına bir kez**dir. Ne kadar çok kullanılırsa
o kadar deterministikleşir — *ters yönün asıl kazancı hız değil, **birikim**.*

### ⚠ Üç sert şart

| şart | gerekçe |
|---|---|
| 🔴 **Çok eşleşme → kuyruğa GİRMEZ** | Bir kelime ≥2 katalog terimine işaret ediyorsa bu bir sinonim değil bir **belirsizliktir**; `netlestirme_onceligi`'nin konusu. Sinonim yazmak `bakiye`'nin ₺11,86 milyonluk seçimini **kalıcı** yapardı |
| 🔴 **Onaysız canlıya inmez** | `_apply_synonym_overlays` yalnız `approved=True` satırları uygular, **aday kuyruğu canlıya inmez** — yani bir LLM hatası kataloğu sessizce değiştiremez. Mekanizma **zaten kurulu** |
| 🔴 **«hiçbiri» bir başarısızlık değildir** | `zayiat` gerçekten hiçbir şeyin eşanlamı değilse doğru cevap *«hiçbiri»*dir ve o kelime bir **menü boşluğu** sinyalidir (`B-6`), sinonim borcu değil |

---

## 4e · 🔴🔴 SICAK YOLDA SERİ İKİNCİ TUR — *ölçüldü, kullanıcı haklı, rakam daha ağır*

> Kullanıcı (2026-08-10): *"prompt enhancer meselesinde biz **çift LLM çağrısı olur**
> diye `off` bırakmıştık."* · *"**iki tur olamaz**, LLM başta yoksa 30 sn bekletir."*

**Doğru — ve gerekçe bayrağın kendi yorumunda zaten yazılıydı:**
`demo/packs/features.yml:112` → *«`off` — sıcak yola LLM çağrısı ekliyor; açılması
bilinçli karar olmalı.»* Raporun ilk yazımı bu gerekçeyi atlayıp *"ölçülmedi"* dedi;
**ölçüm eksikliği ayrı bir borçtur, ama açmama kararının sebebi bu değildi.**

### ⊙ ÖLÇÜM — tur sayısı, çağrı sayısı DEĞİL

| yol | **seri LLM turu** | gecikme |
|---|---|---|
| Intent yolu (bugün) | **1** — `consistency_k=3` örnekleri **paralel** koşar (`ask.py:3672`: *"örnekler paralel koşar → gecikme ~tek çağrı"*) | 1 tur |
| 🔴 **enhancer açık** | **2** — `route` → `prompt_enhance` (**bekle**) → `route` → çözemezse **Intent** (**bekle**) | **2 tur** |

🔴 **Yani mesele token maliyeti değil, SERİ TUR.** Üç paralel örnek bir turdur; bir
ucuz enhancer çağrısı **ayrı bir turdur**. Paralelleştirilemez, çünkü ikinci turun
girdisi birincinin çıktısıdır.

### 🔴 Ve nüfus, bayrağın kendi yorumundakinden ÇOK daha büyük

| kaynak | route'un **pes etme** oranı | dolayısıyla enhancer kaç soruda ateşler |
|---|---|---|
| bayrak yorumu (`features.yml:110`) | *"%64'lük sıfır-maliyet çoğunluk dokunulmadan kalır"* → %36 | ⚠ bu sayı **katalog türevi korpustan** |
| 🔴 `2026-08-07_LLM-YOLU-TESHISI` §1 — **gerçek dünya dili** | **%93,3** *(2132 vaka)* | **neredeyse HER gerçek soruda** |

> Yani *"yalnız route boş dönünce tetiklenir"* güvencesi, **gerçek kullanıcı dilinde bir
> güvence değildir**: route zaten %93,3'ünde pes ediyor. Enhancer pratikte **istisna
> değil, kural** olurdu.

### ⊙ Bunun saniye karşılığı — ölçülmüş

`app/routers/stats.py:93` gecikme bütçesi: **`llm: 20.000 ms`**; Discovery ölçümü
**12.567 ms**; deterministik `cube` **145–434 ms** (**30–85×** fark). İkinci bir seri
tur, kullanıcının beklediği süreyi **ikiye katlar** — kullanıcının *"30 sn"* sezgisi
bir abartı değil, **aritmetiğin kendisi**.

⚠ Ve `stats.py` bunun **tek bir bayrağın hikâyesi olmadığını** yazıyor:
*"kapalı dört LLM bayrağının `features.yml`'deki gerekçesi **üç kez aynı cümle**:
«sıcak yola LLM çağrısı ekliyor», yani **gecikme**."* → `agent_plan_secimi` de aynı
sınıfta ve aynı kural onun için de geçerlidir.

🔴 **Ve karar verecek kapı hâlâ yok:** *"30–85× fark **ölçülmüş, bütçeye
çevrilmemiş**"* — `P-2` (latency tavanı kapısı) bu yüzden `B-10`'un ön koşuludur.

### 🔴 SONUÇ — borcun sınıfı DEĞİŞTİ

`prompt_enhancer` *"ölçülmemiş bir bayrak"* değil, **yanlış biçimde tasarlanmış bir
mekanizmadır**. Doğru iş onu ölçüp açmak değil:

| ❌ yapılmayacak | ✅ yapılacak |
|---|---|
| enhancer'ı `on`'a çekmek | `§4d` — kanonikleştirmeyi **var olan Intent turunun İÇİNE** bir **alan** olarak koymak (`eslesen_terim`). **0 ek tur, 0 ek gecikme** |
| ikinci tur eklemek | Eşlemeyi **hasat edip** aday sinonim kuyruğuna yazmak → onaylanınca `_apply_synonym_overlays` ile **deterministik ve bedava** |
| — | Enhancer `off` **kalır** — yalnız *"Intent de çözemedi"* dalında, **kullanıcı bekletmeyen** (asenkron/öğrenme) bir yol olarak düşünülebilir |

> ⚠ Ve bu, `E-1`'in (*"çözüyorsa geliştirmek emirdir"*) bir istisnası **değil**,
> `E-7`'nin (*"sıcak yola maliyet eklemek ayrı bir karardır"*) uygulanmasıdır:
> **fikir doğru, taşıyıcısı yanlış.** Fikir korunur, taşıyıcı değişir.

---

## 4f · 🔴🔴 KAPININ FATURASI — *"20 dakika bize ne katıyor?"*

> Kullanıcı (2026-08-10): *"artık kapı koşmak ne işe yarıyor, bu kadar beklemek bize ne
> katıyor, hatalı kararlar verdirmekten öteye?"*

**Soru meşru ve cevabı iki parçalı: kapı bir şey ölçüyor — ama ölçtüğü şey, onu
kullandığımız kararların çoğu DEĞİL.**

### ⊙ Kapının kendi hesabı *(`OPERASYON.md §3`, bu operasyonda ölçüldü)*

| adım | kaç kez **kırmızı** verdi | süre |
|---|---|---|
| `eval.run` | **0** *(her koşum `+0,0/+0,0/+0,0`)* | ~1,5 dk |
| konuşma senaryoları | **0** *(dokuz sınıf tabanda sabit)* | ~1,5 dk |
| tam süit | birkaç — **aynı kusurları seviye 1 de yakaladı** | ~8,5 dk |
| **korpus** | **2** | 1:57 → 🔴 **13:00** |

**Korpusun iki gerçek yakalaması — ve ikisi de AYNI eksende:**

| # | ne yakaladı | eksen |
|---|---|---|
| 1 | `gitas` compose yarışı: payda **445 → 342** düşerken doğruluk **%93,2 → %94,3 ÇIKTI** — *sistem bozulurken sayı iyileşti*. Süit · `eval` · senaryolar **üçü de yeşildi** | **PAYDA** (kapsam) |
| 2 | `§EB/A`: `sessiz_yanlis` **12 → 18** | **SESSİZ-YANLIŞ** |

**Ve bir de yanlış kırmızısı:** `G3` — korpus `%95,1→%93,5` dedi, değişiklik geri
alındı; düşüş **(b) sınıfıydı** (route çekildi, tur garsona devredildi) ve üretimde bir
**kazançtı**. Sorulmadı.

### 🔴 TEŞHİS — kapı iyi bir SAYAÇ, kötü bir HAKEM

| korpus şunu ölçerken | güvenilir mi |
|---|---|
| **payda** — *"kaç soru cevaplanabiliyor"* | ✅ **evet, ve bunu ondan başka hiçbir şey görmüyor** |
| **`sessiz_yanlis`** — *"kaç cevap kendinden emin biçimde yanlış"* | ✅ **evet** — `E-3`'ün vetosu buradan gelir |
| **doğruluk %** — *"kalite arttı mı"* | 🔴 **HAYIR** — LLM'siz koşuyor, route→garson devri **kayıp** görünüyor, ve soruların **≥%97,1'i katalog türevi** olduğu için totolojik doğrular sayılıyor |

> **Yani 13–20 dakika, iki gerçek sinyal (payda · sessiz-yanlış) için ödeniyor; ama o
> sürenin sonunda okunan sayı, kararların çoğunda (bayrak · route/garson dengesi ·
> ifade yeteneği) hakem sayılıyor — ve orada YANILIYOR.** `G3` bunun faturasıdır.

### ⚠ Ve 20 dakikanın sebebi kapı DEĞİL, ÜRÜN

`2026-08-09_KAPI-YAVASLAMASI-TESHISI`: kapı **1:50 → 13:00 (7,1×)**, paralellik sağlam,
payda kırpılmadı (tersine **+%38**). Yavaşlayan şey `/ask`: **47 → 177 ms (×3,8)**.
🔴 **Kapıyı kısaltmak yanlış hedef** — ürünü hızlandırmak doğru hedef, ve onu görecek
**latency tavanı kapısı yok** (`P-2`).

### 🔴 KARAR — kapı kaldırılmaz, YETKİSİ DARALTILIR

| | |
|---|---|
| ✅ **kalır** | payda · `sessiz_yanlis` — bu iki sayı **veto** yetkisini korur (`E-3`) |
| 🔴 **kaldırılır** | *"doğruluk yüzdesi düştü"*nün **tek başına** red yetkisi (`E-2`) |
| 🔨 **eklenir** | çıktı ikiye ayrılır: `route %X (n)` · `garson %Y (n)` · `devir %Z` · `sessiz_yanlış N` |
| 🔨 **eklenir** | **kapı defteri**: her koşumda *ne yakaladı / hangi kararı yanlış verdirdi*. Bugün 2 gerçek yakalama ↔ 1 yanlış geri alma — ve bu tally **hiçbir yerde tutulmuyor** |

*Bir ölçüm aracının değeri, kaç kez kırmızı verdiğiyle değil, kaç kez **haklı** kırmızı
verdiğiyle ölçülür — ve bu depoda o sayı hiç tutulmadı.*

---

## 4g · 🔴 GARSON KORPUSU BİNLERCE CANLI ÇAĞRI DEĞİLDİR — *ve olamaz*

> Kullanıcı (2026-08-10): *"garson korpusu LLM'e gidecekse ve binlerce test olacaksa API
> maliyeti çok yükselir, belki API tıkanıp yanıt bile gelmez — biz o yüzden curl ile tek
> tek test yapıyoruz, döngü kuralları o yüzden çok sert."*

**Doğru, ve `T-1`'in ilk yazımı bu kısıtı yeterince öne almamıştı.** Düzeltilmiş tasarım
— **iki katman, ikisi de var, ikisi rakip değil**:

| katman | ne ölçer | maliyet | sıklık |
|---|---|---|---|
| 🟢 **`C` · CURL DÖNGÜSÜ** *(bugünkü disiplin — değişmez)* | **GERÇEK**: ürün ne yapıyor, insan yargısıyla | canlı API — **pahalı** | **az sayıda, tek tek, sırayla** |
| 🟢 **`K` · KASET** *(kayıt-ve-tekrar)* | **GERİLEME**: dün çözülen bugün de çözülüyor mu | 🔴 **SIFIR** — diskten koşar, API'ye **hiç** gitmez | her demet |

⊙ **Altyapı zaten var:** `lab/garson.py --live --kaset` sağlayıcı yanıtlarını
`lab/kasetler/`e yazıyor (bugün **1 kaset**: `garson-g1c.json`).

🔴 **Yani garson korpusu «binlerce canlı çağrı» değil, «bir kez kaydedilmiş N vaka»dır.**
Maliyet **N × bir kez**, koşum başına **sıfır**. `--slice llm` paydası 4 → ~40-60'a
bu yolla çıkar: **bu turun her `§`-kodlu canlı bulgusu bir kasete dönüşür** (`§SY` ·
`§EB` · `§HB` · `§AR/Ö` · `§AT` · `§W-C` · `§V6` …). Onlar **zaten canlı koşuldu**;
kaydedilmedikleri için **tekrar edebilirler**.

### ⚠ Kasetin sınırı — ve depo bunu ZATEN yazmış

> *"Kaset **kaliteyi ölçmez**, yalnız **tesisatı** ölçer. Bir kaset yeşilken ürün kötü
> olabilir; bu yüzden `C` katmanı (`--live`) **kaldırılmaz, seyrekleştirilir**."*
> — `lab/garson.py:475`

Buna bir ek şart gerekir: **kaset (soru + istem sürümü) ile anahtarlanmalı.** İstem
değiştiğinde kaset **bayattır** ve yeniden kaydedilmelidir — yoksa `§AR/Ö` gibi bir
istem düzeltmesi, eski kasetle **yeşil** görünür.

> **Sonuç:** curl döngüsü **gerçeği**, kaset **gerilemeyi** ölçer. Curl disiplini
> aynen kalır — kaset onun yerine geçmez, onun bulduğunun **bir daha sessizce geri
> gelmesini** engeller. *Sert döngü kuralının sebebi API kısıtıdır ve o kısıt gerçektir;
> çözüm turu ucuzlatmak değil, **bulduğunu kalıcı kılmaktır**.*

---

## 4h · 🔴🔴 BAYRAK AÇMA FAZLARI — *kapalı yetenekler için araştırma + plan*

> Kullanıcı (2026-08-10): *"kapalı duran yetenekler için de araştırma yapıp geliştirme
> fazları planlayalım, sinonim meselesi gibi — böylece ciddi ivme kazanabilir, birçok
> sorunu kökten çözebiliriz."*

### ⊙ ÖNCE EN ÖNEMLİ BULGU: **ÖLÇÜM ALETİ ZATEN VAR**

`lab/nl_accuracy.py` iki kip taşıyor ve **ikisi de yazılmış, testli**:

| kip | ne ölçer |
|---|---|
| `--ab <bayrak>` | **GERİLEME** — etiketli vakalarda bayrak kapalı ↔ açık; *"çalışan bir vakayı bozuyor mu"* |
| `--ab-kurtarma <bayrak> --n N` | **KAZANÇ** — `route()`'un **çözemediği** doğal ifadelerde kaç soru kurtarılıyor, **ve doğru mu** |

🔴 **Bu, aşağıdaki fazların çoğunu haftalık iş olmaktan çıkarıp SAATLİK işe indiriyor.**
*Aletin var olduğunu bilmemek, olmamasıyla aynı maliyeti üretir.*

---

### `F1` · **`varsayilan_donem`** — 🔴 EN YÜKSEK KALDIRAÇ

| | |
|---|---|
| **kod** | ✅ **tam** — `donem_capasi.py:226` (bayrak dalı) · `veri_araligi.py` (kaynak) · `ask.py:2597` (kapı) · 1 test dosyası |
| **ölçülen sorun** | **korpusun %13,7'si** dönem netleştirmesi; canlı turlarda **on kez** ölçü·kırılım·sıralama çözülmüşken **yalnız dönem** yüzünden cevap gelmedi |
| **yazılı `on` şartı** | ✅ var: *"kazancı (kapsam) ile bedeli (`sessiz_yanlis`) **ölçülmeden açılmaz**"* |
| **engel** | 🔴 **yalnız ölçüm** — kod, kapı, fail-closed dalı ve beyan metni hazır |

**Faz planı:**

| # | iş | alet | çıktı |
|---|---|---|---|
| `F1.1` | Gerileme ölç | `nl_accuracy --ab varsayilan_donem` | bozulan vaka **0 olmalı** |
| `F1.2` | Kazanç ölç | korpus, iki koşum: **kapsam Δ** ve **`sessiz_yanlis` Δ** | kapsam ↑ · `sessiz_yanlis` **artmamalı** |
| `F1.3` | Beyanı canlıda doğrula | **curl**, 5 senaryo | *"Dönem belirtmedin — verinin son 12 ayı alındı (…)"* cümlesi **görünüyor mu** |
| `F1.4` | Kaset al | `garson.py --live --kaset` | gerileme kalkanı |
| `F1.5` | `beta` → iki koşum → **`on`** | `KURAL G-1` | |

🔴 **Durdurma şartı (`E-3`):** `sessiz_yanlis` artarsa faz **durur** — kapsam kazancı
sessiz-yanlışla satın alınmaz.

---

### `F2` · **`oylama_paydasi`** — en ucuz doğruluk kazancı, ve `K` doktrininin İLK SINAVI

| | |
|---|---|
| **kod** | ✅ 2 kod + 1 test dosyası |
| **ölçülen sorun** | *1 cevap + 2 «bilmiyorum» → uyum **%100** görünüyor.* Kendi kaydının cümlesi: *"şüphenin en yüksek olduğu durum **en emin** görünür"* |
| **engel** | 🔴 **hiçbiri** — yalnız *"kapsam düşer"* korkusu |

**Faz planı:** `F2.1` kaç cevabın netleştirmeye düştüğünü ölç → `F2.2` düşenlerin
**kaçının `sessiz_yanlis` olduğunu** say → `F2.3` kasetle sabitle → `F2.4` `beta`.

🔴 **Bu faz `E-2`/`K` doktrininin ilk gerçek sınavıdır:** korpus bunu **kayıp** olarak
gösterecek (kapsam ↓). Karar `sessiz_yanlis` ekseninden verilir. *Yanlış bir cevabı
netleştirmeye çevirmek bir kayıp değil, bir **düzeltmedir**.*

---

### `F3` · **`netlestirme_onceligi` + `katalog_belirsizlik`** — BİRLİKTE, çünkü aynı kusurun iki yarısı

| bayrak | test dosyası | rolü |
|---|---|---|
| `netlestirme_onceligi` | 3 | **çalışma zamanı** — belirsiz ölçüde chip Intent'ten **önce** gelir |
| `katalog_belirsizlik` | 🔴 **0** | **katalog** — çok sahipli ölçüler modele ifşa edilir |

**Ölçülen sorun:** `bakiye` iki küpte → `cari` **₺11.859.052,65** ↔ `mizan` **₺0**; sistem
kura ile seçti, sormadı, seçtiğini yazmadı. Ve *"aynı soru iki kez → **8'de 1** farklı
sorgu"*.

**Faz planı:**

| # | iş |
|---|---|
| `F3.0` | 🔴 **`katalog_belirsizlik`'e KAPI yaz** — bugün **testsiz**; kapısız bir bayrak açılmaz |
| `F3.1` | Yazılı şartı yerine getir: *"AÇILMADAN ÖNCE **kapsam kaybı ölçülmeli**"* → `nl_accuracy --ab netlestirme_onceligi` |
| `F3.2` | **`T-4` ile birlikte**: 13 çok sahipli ad için sahip beyanı ya da *"beyan yok → sor"* işareti |
| `F3.3` | İkisini **aynı demette** aç — biri açık öteki kapalı, belirsizliği görünür kılıp çözümsüz bırakır |

---

### `F4` · **`cekirdek_katman`** — `T-3`'ün EVİ *(en büyük iş, en büyük tavan)*

| | |
|---|---|
| **kod** | 3 kod + 3 test |
| **engel** | 🔴 **iki sahipli** (`OPERASYON-DURUM` · açık kalanlar) · derleme-zamanı kademesi, tenant bayrağı değil |
| **neden önemli** | `metrikler` (10) + `grain_sozlesmeleri` var; **`varliklar` YOK** → kanonik müşteri ekseni buraya yazılır |

**Faz planı:** `F4.1` iki sahipliliği çöz → `F4.2` `varlik_sozlugu.yml` (kanonik ad · kimlik
alanı · ad alanı · sinonim) → `F4.3` küp boyutlarını `cekirdek_varlik:` ile bağla →
`F4.4` `blend`in eşleşme anahtarını ham addan **kanonik varlığa** çevir → `F4.5` ölç
*(bugün kurulamayan çapraz-aile soru artık kuruluyor mu)*.

⚠ Ötekilerden **sonra**: kazancı büyük ama ölçülmesi `T-1`'e (kaset) bağlı.

---

### `F5` · **`tazelik`** — en çok yatırım yapılmış KAPALI bayrak

**8 test dosyası · 7 kod dosyası** — ve hâlâ `off`. §C ölçüt 12'nin konusu; canlı turda
kullanıcı **üç turunu** veri sonu tarihini keşfetmeye harcadı (borç #16e).

🔴 **Araştırma borcu:** *neden* kapalı olduğu **hiçbir yerde yazılı değil.** İlk iş
gerekçeyi bulmak; gerekçe yoksa bu bayrak **bugün açılabilir** ve 15 dosyalık bir
yatırım kullanıcıya ulaşır.

---

### `F6` · UCUZ DEMET — *dördü bir demette*

| bayrak | durum | iş |
|---|---|---|
| `hizli_derin` | `beta` | **sıfır yeni davranış** — `hizli` ≡ `yol_siniri="deterministik"`; UI'daki ölü kontrol canlanır |
| `hedef_kiyasi` | `off`, 🔴 **0 test** | önce **kapı**, sonra aç. Referans çizgisi bugün **hedef değil ortalama** — *"kod bunu itiraf ediyor"* |
| `tur_takip` | `off` | *"yeni motor yazılmadı, yalnız **erişim**"* — `zamanla.olustur` zaten var |
| `tur_paylas` | `off` | *"çalışan, testli bir yetenek **BİR KELİME** yüzünden kullanıcıya kapalıydı"* |

Dördü de **motor yazmıyor**; ikisi sıfır davranış değişikliği. Tek demet, tek kapı.

---

### `F7` · **`oylama_cekirdek`** — 🔴 `beta` AMA **0 TEST DOSYASI**

*"Oylama zenginliği **cezalandırıyordu**"*: `order`/`limit`/`pencere` yazmayan iki oy
birbiriyle **bedavaya** uyuşuyor, yazan tek oy yalnız kalıyor → **kazanan 1 oy: 7 kez**.
Canlı bedeli `V13` (*«azalan sırada ilk 5»* → 11 satır) ve `V14` (*«yüzde kaçını»* →
`pencere:pay` düştü).

🔴 **Bu bayrak `beta`'da testsiz duruyor** — yani bir gerilemeyi hiçbir kapı görmez.
`F7.1` **kapı yaz** (öncelik) → `F7.2` kasetle doğrula → `F7.3` `on` şartını yaz.

---

### `F8` · **`llm_sema_kisitli`** — `beta` ama **NO-OP**, ve ~10.000 token BOŞA GİDİYOR

Aktif sağlayıcı (`openrouter`) `oneOf` desteklemiyor; şema **her istekte üretilip
atılıyordu** — 23 küplük demoda **~10.000 token**. `B5` bunu `sema_kullanir` beyanıyla
kapattı, ama bayrak hâlâ *"açık ama etkisiz"* durumda.

🔴 Bu bir **bayrak işi değil sağlayıcı işidir** ve `T-9`'un yapısal çözümüdür (enum'a
bağlı ad → geçersiz operatör/ölçü **üretilemez**). `F8.1` bugün ne kadar token'ın boşa
gittiğini ölç → `F8.2` şema-yetenekli bir sağlayıcı dilimi ile `T-9`'un kaç reddi
kapattığını ölç → `F8.3` sağlayıcı kararı.

---

### 📋 Faz sırası — ivme sırasına göre

```
F6 (ucuz demet)  →  F2 (oylama_paydasi)  →  F1 (varsayilan_donem)  →  F7 (kapı)
     ↓                                              ↓
F5 (tazelik: önce gerekçe ara)              F3 (netleştirme ikilisi + T-4)
                                                    ↓
                                            F8 (sağlayıcı)  →  F4 (çekirdek + T-3)
```

⚠ **`F1` ve `F2` `T-1`'e (kaset) bağımlıdır** — ikisi de korpusta **kayıp** gösterecek
ve o kaybın `(a)` mı `(b)/(c)` mi olduğu kasetsiz ayrılamaz.

---

## 4i · 🔴🔴 KAPININ YENİ MERKEZİ: **KASETLİ GARSON KORPUSU**

> Kullanıcı (2026-08-10): *"belki kapıda sadece her tur sonunda kapsamlı bir **garson
> korpusu** koşulur — o zaten aslında tam kapının yaptığını da yapar, route için de.
> Route korpusu çok daha az sıklıkta ya da **çok kritik değişiklik** olursa koşulur."*

### ✅ Mimari olarak DOĞRU — ve sebebi ölçülmüş

`/ask` yolunda **`route()` her zaman denenir** — bayraktan bağımsız
(`features.yml:107`: *"route()'un kendisi bu bayraktan **BAĞIMSIZ** her zaman
çalışır"*). Dolayısıyla **tam `/ask` yolundan koşan bir garson korpusu, route'u da
koşturur** ve bugünkü LLM'siz korpusun ölçtüğü her şeyi **artı devri** ölçer:

| ölçü | bugünkü korpus (LLM'siz) | **garson korpusu** (tam yol) |
|---|---|---|
| route kapsamı | ✅ | ✅ (`source=cube` sayısı) |
| garson kapsamı | 🔴 **hiç** | ✅ (`source=llm` / `cube+llm`) |
| **devir oranı** | 🔴 **görünmez** — kayıp sanılıyor | ✅ **doğrudan** |
| `sessiz_yanlis` | ✅ ama yalnız route dalında | ✅ **iki dalda birden** |
| `(a)/(b)` ayrımı | 🔴 imkânsız | ✅ **rozet farkından hesaplanır** |

> 🔴 **Yani bugünkü korpus, garson korpusunun LLM'i sökülmüş hâlidir.** Doğru olan
> ikisini yan yana koymak değil, **doğrusunu koşup ötekini özel bir amaca indirmektir.**

### ⚠ AMA TEK BAŞINA OLMAZ — ve sınırı kullanıcının kendi kısıtı çiziyor

*"Binlerce canlı test API'yi tıkar."* Doğru. O yüzden garson korpusu **kasetten** koşar
(`§4g`): canlı yanıt **bir kez** kaydedilir, sonraki her koşum **diskten** → API'ye
**hiç** gitmez.

🔴 **Kasetin iki sert sınırı ve bunlar kapının parçası olmalı:**

| sınır | sonucu |
|---|---|
| Kaset yalnız **kaydedilmiş** soruları taşır | Payda **kayıt kümesidir** — ilan edilir, sürümlenir. *«Korpus %»* demek **onun hakkı değildir** |
| Kaset **istem sürümüne** bağlıdır | İstem değişince (`§AR/Ö` gibi) kaset **BAYAT** — küçük bir canlı tur ile **yeniden kaydedilir**. Yoksa kapı **eski kanıtla yeşil** verir |

*Bir kaset, kaydedildiği günün modelini ölçer — bugünün modelini değil.*

### 🔴 KARAR — iki korpus, iki amaç, iki tetik

| korpus | ne ölçer | maliyet | **ne zaman** |
|---|---|---|---|
| 🟢 **GARSON (kasetli)** — *yeni merkez* | **KALİTE**: route + garson + devir + `sessiz_yanlis`, **tam `/ask` yolu** | 🔴 **sıfır API** | **her tur/demet sonunda** |
| 🔵 **ROUTE (tam payda, LLM'siz)** — *özel amaç* | **KAPSAM**: ~10.800 sorunun kaçı cevaplanabiliyor — `gitas`ı yakalayan tek şey | ~13–20 dk CPU | 🔴 **DEĞİŞİKLİK TETİKLİ**: `cube_router` · katalog · `demo/packs/**` dokunulduysa **+** günde 1 |
| 🟠 **CURL (canlı)** | **GERÇEK**: ürün ne yapıyor, insan yargısıyla | canlı API | döngü kuralına göre — **değişmez** |

⚠ **Tetik mekanizması zaten var:** `kapi.py --hizli --degisen <dosyalar>` değişen
dosyaya göre kapı seçiyor. Route korpusunu *"kritik değişiklikte"* koşturmak **aynı
mekanizmanın bir kuralı**, yeni bir alet değil.

🔴 **Ve bu düzen `K-2`'yi tamamlıyor:** korpusun *doğruluk yüzdesi* veto yetkisini
kaybetmişti çünkü LLM'siz koşuyordu. Kasetli garson korpusunda **LLM var** — yani o
eksen **veto yetkisini geri kazanır**. *Bir sayıya güvenmemek onu atmak değil, ölçtüğü
şeyi düzeltmektir.*

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

## 6b · ✅ YAPILACAKLAR — **SON KONTROL LİSTESİ**

> 🔴 **Bu liste bu raporun ÇIKIŞ ÖLÇÜTÜDÜR.** Her kalem tek tek işaretlenebilir olmalı;
> *"yaptık mı?"* sorusu **bu tabloya bakılarak** cevaplanır. Bir kalem **ölçümle +
> HEAD damgasıyla** `OPERASYON-DURUM.md`'ye yazılmadan **işaretlenmez**.
> ⚠ Kalem *"geçersiz"* çıkarsa **silinmez**, çürüten ölçümle işaretlenir.

### A · ÖLÇÜM ALTYAPISI *(önce bunlar — ötekilerin hepsi buna bakıyor)*

| ☐ | # | iş | biten sayılır: |
|---|---|---|---|
| ✅ | `A1` | **Kaset katmanı** — `app/kaset.py`, sağlayıcının **TAŞIMA** metodunu (`_chat`/`_ask`) sarar | anahtar `(istem, model, kaçıncı_kez)` — istem değişince kaset **kendiliğinden** bayat. ⚠ İlk tasarım **anlam** yüzeylerini sarıyordu ve canlıda **0 kayıt** verdi: `llm.py`'de 11+ anlam yüzeyi var, ağa çıkan yer **2**. *Bir kaset anlamı değil TELİ dinlemelidir* |
| ✅ | `A2` | **Kasetli garson korpusu** — `lab/garson_korpusu.py`, tam `/ask` yolu, 21 senaryo (3 ve 5 turluk thread'ler dâhil) | `route · garson · orkestra · netleştirme · sosyal · 🥡discovery` dökümü, **`--network none` altında koşuyor**. Ölçülen: `route 9 · orkestra 9 · garson 1 · discovery 0`. ⚠ 1 anlatı ıskası açık — sınıflandırmayı değiştirmiyor |
| ✅ | `A3` | **Kapı çıktısı ayrıştırılır** — `doğru · devir · netleştirme · beyanlı_kısmi · 🔴sessiz_yanlış · payda` | `gercek_dunya._ozet` beş sınıfın **üçünü** sayıyordu; `netlestirme`+`durust_ret` yalnız toplu `kabul` içindeydi → her devir *«düştü»* diye okunuyordu |
| ✅ | `A4` | 🔴 **`(a)/(b)` otomatik etiketleme** — `_degisim_sinifi` → `GERILEME · DEVIR · KAZANC · SABIT · BILINMIYOR` | `sessiz_yanlis↓ + devir↑` = **KAZANÇ**; `dogru↓` karşılığı varsa **DEVİR** (fiyatı basılır), yoksa **GERİLEME**. Eski tabanda etiket **uydurulmaz** |
| ✅ | `A5` | **Değişen soruların listesi** — iki yönde, `_sapma_haritasi` + `_degisim_listesi` | harita yalnız `dogru` OLMAYANLARI tutar (yokluk = `dogru`): temsil eksiksiz, git gürültüsü yok. Kırpma **sessiz olamaz** |
| ⊘ | `A6` | ~~**NABIZ kademesi** — sabit tohumlu alt küme, ~2 dk~~ → **GEÇERSİZ ÇIKTI, ÖLÇÜMLE İŞARETLENDİ** (`§6.4`: *kalem silinmez, çürüten ölçümle işaretlenir*) | ⊙ `A6` **`A2`'den önce** tasarlanmıştı: amacı *«hızlı bir nabız»*dı ve karşılığı ~2 dk'lık bir **route alt kümesiydi**. `A2` (kasetli garson korpusu) ölçüldü: **26 saniye**, `--network none`, ve route alt kümesinin göremediği **üç şeyi** de görüyor (garson · orkestra · devir). 🔴 Üçüncü bir kademe kurmak, aynı soruya **iki sahip** yaratmak olurdu — bu deponun 1 numaralı kusur sınıfı. *Bir ihtiyacı gideren şey çıktığında, o ihtiyaç için tasarlanmış plan bir borç olmaktan çıkar; onu yine de yapmak, planı işten üstün tutmaktır.* ⚠ Nabız ihtiyacı **kapanmadı, sahibi değişti**: artık `A2`'dir |
| ✅ | `A7` | **Route korpusu değişiklik-tetikli** — `kapi.py --tetik --degisen …`; tetikleyiciler `cube_router` · `wren_service` · `compose` · `katalog_metni` · **`demo/packs/`** (dizin öneki) | ⊙ Gerekçe: korpus **iki eksen** görür (payda · `sessiz_yanlis`) ve ikisi de ancak route ya da katalog değişince kıpırdar; bir anlatı düzeltmesinden sonra 13 dk beklemek *ölçmediğini ölçmek*tir. 🔴 Liste **verilmezse KOŞAR** — bilinmeyen değişiklik en kötüsü sayılır; *ölçmediğini güvenli saymak bu deponun üç kez ödediği hatadır*. Liste elle değil **desenle**: yeni bir pack kendiliğinden kapsanır |
| ✅ | `A8` | **KAPI DEFTERİ** — `belgeler/denetim/KAPI-DEFTERI.md`; *haklı ↔ haksız* kırmızı tally'si, ekleme yapılır **satır silinmez** | ⊙ Ve defter raporun kendi teşhisini **kısmen çürüttü**: `§4f` *«tam süit: aynı kusurları seviye 1 de yakaladı»* diyordu — 2026-08-10'da süit **4 haklı kırmızı** verdi ve dördü de seviye 1'in göremeyeceği sınıflardandı. En değerlisi: `A4`'ü kurarken **kapının kırmızı verme yeteneğini bozmuşum** ve bunu yakalayan şey o altyapının kendi kapısıydı. *Bir aletin değeri ölçüldüğü güne aittir; bir kez ölçülüp kapatılan bir hüküm değil* |
| ✅ | `A9` | **`plan_garson.SAYAC` yayımlanır** — red sayısı · onarım tutma oranı · **sebep dağılımı** | red oranı bir izlenim değil **sayı** · **KAPANDI** `sha=892de28`: `/stats/plan` ucu + `red_nedenleri` sınıflandırıcısı (16 kapalı sınıf, **kendi mesajlarımızdan**). İlk ölçüm: `red_orani=%19` · `onarim_tutma=%100` · `boyut_yok 3 · ad_yok 1 · ulasilmaz 1` — ve **`operator`/`suzgec_alani` reddi SIFIR**, yani `B1`–`B4` ölçülebilir biçimde tuttu |
| ✅ | `A10` | **Latency tavanı kapısı** (`P-2`) — `test_gecikme_tavani.py`, bütçenin tek sahibi `stats.GECIKME_BUTCESI_MS`; yalnız **LLM'siz** yollar (ağa çıkmaz → bedava ve tekrarlanabilir) | ⊙ Kurulur kurulmaz **gerçek bulgu** verdi: `meta` p95 **320 ms**, `catalog` **401 ms** — oysa bütçenin kendi yorumu *«sabit metin»* diyordu. Sebep yol değil **önündeki boru hattı**: bir selamlaşma bile şema+route+niyet zincirinin tamamını ödüyor. Yani `meta`, `E-1`'in (47→177 ms) **en saf göstergesi** — kendi işi ~0 olduğu için okuduğu şey yalnız hazırlık. Tavan ölçülen gerçeğe çekildi **ama gerekçesiyle**; *«sosyal cevap tam boru hattı bedelini ödüyor»* açık borç. ⚠ Kapı kendi kusurunu da gösterdi: ilk hâli `n=1` ile p95 hesaplıyordu — *bir örnek bir yüzdelik değildir*; artık `n<5` **ÖLÇÜLEMEDİ** diye raporlanır, geçmiş sayılmaz |
| ✅ | `A11` | **Katalog envanteri tek kaynaktan** — `katalog_metni.envanter` + `/stats/katalog` | çelişki bir kusur DEĞİLDİ, **adsızlıktı**: canlı **23 küp · 136 ölçü tanımı · 127 benzersiz · 9 çok sahipli · 121/58 boyut · 72 yön beyansız**. `127/132/141` bitti |

### B · TABAN BORÇLARI

| ☐ | # | iş | biten sayılır: |
|---|---|---|---|
| ✅ | `B1` | **`T-9` plan reddi** — `ALAN_REHBERI`'ne süzgeç bölümü (operatör listesi `_ops`'tan **üretilerek**) + `{"dimension","operator","value"}` örneği | `plan_semasi`'de `operator` **geçiyor** · **KAPANDI** `sha=d58b5b2`: `plan_semasi`'de `operator` **geçiyor**; liste `MOTOR_OPERATORLERI`'nden **üretiliyor** (12 ad, elle kopya yok) + süzgeç biçimi örneği. Kapı: `test_PLAN_ISTEMI_OPERATOR_SOZLUGUNU_TASIYOR` |
| ✅ | `B2` | `gerekce()`'ye **geçerli operatör kuyruğu** (`bilinen_boyutlar()`'ın eşleniği) | red mesajı *"doğrusu şu"* diyor · **KAPANDI** `sha=d58b5b2`: red artık *«tanınmayan: `equals` — geçerliler: eq, neq, in, …»* diyor. Kapı: `test_TANIMSIZ_OPERATOR_TESHISI_DOGRUSUNU_SOYLER` |
| ✅ | `B3` | **`None` mesajı** düzeltilir → *«süzgeçte `dimension` alanı hiç yazılmamış»* | `None` bir ad gibi basılmıyor · **KAPANDI** `sha=d58b5b2`: alan eksikse *«süzgeçte `dimension` alanı hiç yazılmamış»*; `None` **basılmıyor**. Kapı: `test_ALAN_YAZILMAMISSA_NONE_BASILMAZ` |
| ✅ | `B4` | **Mekanik eşlemeler seviye 3'e** (`equals→eq`, `ne→neq`, `>→gt`…), **beyan ederek** | LLM turu harcanmıyor · **KAPANDI** `sha=d58b5b2`: 24 takma ad seviye 3'te, **beyan ederek** (`equals→eq` …); hedefler `MOTOR_OPERATORLERI`'ne karşı kapıda doğrulanıyor. Kapı: 2 test |
| ◐ | `B5` | **`T-2` çürütülebilir kesinlik** — çok sahipli / dilbilgisiyle çakışan token'da route **çekilir** | `sessiz_yanlis` ↓ ve devir etiketli · **KISMİ** `sha=d58b5b2`: `§EB` **makinenin ürettiği** belirsizliği yapısal kapattı (6 çarpışma → 0) — *«renk grubuna göre fire»* route'tan çekildi, garson doğru cevapladı. Kalan: beyan edilmiş çok sahiplilik zaten ifşayla cevaplanıyor |
| ✅ | `B6` | **`T-4` sahip beyanı** — canlı 9 çok sahipli ölçünün **6'sının kararı yoktu**; yazıldı: `tek_sahip` 3 (`dogalgaz`→`enerji_makine` · `tep`→`surdurulebilirlik` · `uretim`→`oee` · `fire`→`parti`) · `belirsiz` 2 (`alacak` · `ilk seferde tamam`) | **boş kalem 0**, kapı `test_sahiplik_turu_tam.py`. ⊙ `uretim` kararı **zaten kodda** yazılıydı (`wren_service`: *«maliyet.uretim kg-başına maliyetin PAYDASIDIR»*) ama katalogda değildi — beyan edildi ki bir daha kod yorumundan okunmasın. ⚠ Pack kararı **ÖNERİDİR**: uygulayan tenant'ın kendi kararıdır (ölçülmüş gerekçe: global uygulama korpusu %93,2→%92,6 düşürüyordu). `olculer:` alanı eklendi — karar↔ölçü bağı **beyan edilir**, alt-dizeyle tahmin edilmez |
| ◐ | `B7` | **`T-5` yön beyanı** — 125 kalem + **yeni ölçü kapısı** | `lower_is_better` beyansız oran ↓, kapı var · **KISMİ** `sha=d58b5b2`: adı **kesin olumsuz** 11 ölçüye `lower_is_better` eklendi **ve** kök kusur bulundu — beyan vardı, `route()` onu `_direction`'a **geçirmiyordu**. Curl: *«en kötü bakım maliyeti»* 15.161 ₺ (en ucuz) → **74.754 ₺** (en pahalı). Kalan: adı belirsiz ölçüler. Kapı: `test_yon_beyani_zorunlu.py` |
| ◐ | `B8` | **`T-3` kanonik varlık ekseni** — `cekirdek/varlik_sozlugu.yml` **YAZILDI** (faz 1: **beyan**); `blend` anahtarı **faz 2** ve bilinçli olarak ertelendi | ⊙ Ölçüm borcu **daralttı**: 58 boyutun 27'si çok küplü ama çoğu **zaten kanonik** (`makine` **10** küpte · `hat` 6 · `bolum` 6 · `vardiya` 5). Gerçekten kırık **tek eksen**: müşteri, **üç aile**. 🔴 Ve rapor `§3.2` burada da **bayat** çıktı: `cari_adi`·`cari_ref` ile `mal`·`yaslandirma` bu bileşimde **yok** — beş ad değil **üç**, on bir küp değil **dokuz**. *Bu turda dördüncü kez: beklenmedik bir sayıda önce **ölçüm yüzeyinden** şüphelen.* ⚠ Faz 2 (`blend` anahtarı) **grain sözleşmesi** ister — `cari` hesap düzeyinde, `parti` sipariş veren müşteri düzeyinde; *adları eşitlemek tek başına «birleşti» yanılsaması üretir*. Kapı `test_varlik_sozlugu.py` faz 2'nin **sessizce yarım inmesini** engelliyor |
| ✅ | `B9` | **Odak varlık** — `diyalog.odak_belirle` (yazar) + `odak_suzgeci` (okur) | canlıda İKİ thread'de ölçüldü ve ikisi de kapandı: A/3 *«peki neden düşük»* → RAM-3 · B/5 *«o ayda»* → 66 satır→**11**. Zaman odağı **yarı açık aralık** |
| ✅ | `B10` | **`T-6` yetenek envanteri kapısı** — `test_yetenek_envanteri.py`; mutfak yüzeyi `cq.get("…")` çağrılarından **taranarak üretilir** (elle liste yok — o, kapının kapatmaya çalıştığı kusurun ta kendisi olurdu) | ⊙ Rapor yazıldığında fark **12 ↔ 7** idi; ölçüldü, garson şeması artık **12 alan** sunuyor — fark bir **belgede** kapanmıştı, bir kapıda değil. Kapı kurulunca **6 sessiz fark** çıktı ve ikiye ayrıldı: **4 sistem taşıyıcısı** (`adhoc`·`kirpilmis`·`provenance_soru`·`referans` — sipariş değil **makbuz**) ve 🔴 **2 gerçek borç**: `blend` (çapraz-küp — `B-3`'e bağlı) · `ayrik_aylar`. *Bir alanın menüde olmaması iki ayrı sebeple olabilir — biri borç, öteki tasarım; ikisini ayırmayan bir liste borcu gizler* |

### C · SİNONİM / TERS YÖN *(`T-8`)*

| ☐ | # | iş | biten sayılır: |
|---|---|---|---|
| ☐ | `C1` | **Kapalı seçim** biçimi — *«bu kelimenin katalogda karşılığı var mı, yoksa hiçbiri mi?»*; girdi `partial_unknowns()` | açık yeniden-yazım **yok** |
| ✅ | `C2` | **Çevrimdışı hasat** — `lab/sinonim_hasadi.py`; kütükten sıklık sıralı aday kuyruğu, **sıcak yolda sıfır**, sıfır LLM | ⊙ Canlı: **aday 287 · belirsizlik 1 · zaten_var 5**. 🔴 Ve alet **kendi girdisinin kusurunu** buldu: `nda` 38 · `baz` 29 · `duru` 16 — bunlar kelime değil **parça**, kaynağı `partial_unknowns`'ın `§M7` öncesi hâli. Yani hasat, düzeltilmiş bir sistemin **düzeltilmeden önceki** çıktısını okuyordu. ⚠ İlk çözümüm bir **tarih penceresiydi** ve yanlıştı — parçalar sürdü, ve pencereyi sayılar güzelleşene kadar kaydırmak **ölçümü cevaba uydurmak** olurdu. Doğru kök: kütük **soruyu da** saklıyor → `partial_unknowns` **bugünkü kuralla yeniden koşulur**; parçalar tamamen gitti ve bir sonraki morfoloji düzeltmesi bu aleti **kendiliğinden** düzeltir. *Bir kaydı yeniden hesaplayabiliyorsan, ona güvenmek bir tercihtir — ve bayat olabilecek bir tercihtir* |
| ☐ | `C3` | **`eslesen_terim` alanı** Intent turunun **içine** | **0 ek tur** |
| ⊘ | `C4` | ~~**Sınıf A elden alınır** — 788 beyan elle bakımdan çıkar~~ → 🔴 **ÖLÇÜLDÜ ve KARAR TERSİNE DÖNDÜ** (`§6.4`: çürüten ölçümle işaretlenir) | ⊙ **(1) Sayı yanlıştı:** rapor **788/1432 (%55)** diyordu; o statik bir sayım ve *göz kararı* bir sınıflandırmaydı. Canlı: ölçü sinonimi **677**, **kanıtlanabilir** fazlalık **113 (%17)**. ⊙ **(2) Silmek YANLIŞ olurdu:** raporun kendi `B-8`'i uyarıyor — *«sinonimler çıkarsa route yavaşlamaz, **garson körleşir**»* (ölçüldü: 9/9 `{"cube":null}`). Bir beyan route için gereksiz olabilir, **katalog metni** için değildir. ⊙ **(3) Ve kapı beni düzeltti:** `hattı → hat` **çözülmüyor** — Türkçe **ünsüz ikizleşmesi** `_ek_gecerli`'nin erişemediği yerde (o bir çekim doğrulayıcı, kök çözümleyici değil). Yani beyanların bir kısmı fazlalık değil **zorunluluk**. **Doğru hedef:** silmek değil **elle yazmayı bırakmak**; kapı `test_sinonim_fazlaligi.py` fazlalık oranının **artmasını** yasaklıyor — artması biri elle çekim yazıyor demektir |
| ✅ | `C5` | ⚠ **Çok eşleşen kelime kuyruğa GİRMEZ** · onaysız canlıya inmez · *«hiçbiri»* **menü boşluğu** olarak kaydedilir | Üçü de `sinonim_hasadi.siniflandir`'da **kod**: `belirsizlik` (≥2 sahip — *sinonim yazmak `bakiye`'nin ₺11,86 milyonluk seçimini KALICI yapardı*) · `zaten_var` · `aday`. Hiçbiri **sessizce elenmez**: her kelime bir **sınıf** alır — *elenen bir kelime, elendiği söylenmediği sürece kaybolmuş bir sinyaldir*. Kuyruk yalnız **kuyruktur**; `_apply_synonym_overlays` yalnız `approved=True` uygular |
| ✅ | `C6` | 🔴 **`prompt_enhancer` AÇILMAZ** (`E-8`) | bayrak `off`, ve gerekçesi belgede · **DOĞRULANDI** `sha=d58b5b2`: bayrak `off`; `E-8` gerekçesi ölçümle sağlandı — k=3 örnekleri `ThreadPoolExecutor` ile **paralel** (tek tur), enhancer **seri ikinci tur**, ve route gerçek dilde **%93,3** pes ediyor (2132 vaka) → enhancer istisna değil **kural** olurdu |

### D · BAYRAK FAZLARI *(`§4h`)*

| ☐ | # | faz | biten sayılır: |
|---|---|---|---|
| ✅ | `D1` | **`F6` ucuz demet** — `hedef_kiyasi` · `tur_takip` · `tur_paylas` → **`beta`**; `hizli_derin` zaten `beta`. Dördü **tek kapıda** (65 test) | ⊙ `hedef_kiyasi` için rapor şartı *«önce KAPI, sonra aç»* yerine getirildi: `test_hedef_kiyasi.py` **9 kapı** — sözleşmenin üç sert kuralı kilitli (*beyan yoksa uydurma yok* · **`None ≠ 0`**: sıfır hedef **ulaşılmış** bir hedeftir, hedefsizlik **ölçülemezliktir** · `gerceklesen` sonuçtan okunur). 🔴 Açmanın bedeli **kanıtlandı, tahmin edilmedi**: `hedefler:` beyan eden küp sayısı **0** → yanıt bayt-bayt aynı. ⚠ Ön koşulu `B-5`: yön yanlışsa *«hedefe ulaşıldı»* **ters** çıkar. Üçünün de yazılı **`on` şartı** var (`E-4`); durum kilidi testleri gerekçeleriyle güncellendi — *bir bayrağın durumunu teste bağlamak, değiştirmeyi zorlaştırmak için değil; değiştirenin gerekçe yazmasını zorunlu kılmak içindir* |
| ☐ | `D2` | **`F2` `oylama_paydasi`** | kalibrasyon yalanı bitti; kararı `sessiz_yanlis` verdi |
| ☐ | `D3` | **`F1` `varsayilan_donem`** — `--ab` + kapsam/`sessiz_yanlis` + **curl beyan doğrulaması** + kaset | korpusun %13,7'lik netleştirme yükü ↓, `sessiz_yanlis` **artmadı** |
| ✅ | `D4` | **`F7` `oylama_cekirdek` KAPISI** — `test_oylama_cekirdek.py` (5 kapı); bayrak `beta`'daydı ve **0 testi** vardı, yani bir gerilemeyi hiçbir kapı göremezdi | ⊙ Kilitlenen sözleşme: kapalıyken anahtar **tam `cq`** (`KURAL B`) · açıkken **çekirdek** (zenginlik farkı oyu bölmez) · kazanan **birleştirilmiş** zenginliği taşır (yoksa **en fakir** aday kazanır ve düzeltme **tersine döner**) · oturmayan zenginlik **taşınmaz** (başka adayın ölçüsüne işaret eden `order`, kazanana uymaz → *doğru görünen, çalışmayan bir cevap*). *Zengin cevabın kaybetmesi bir oylama kazası değil, oylamanın **yanlış şeyi saymasıydı*** |
| ✅ | `D5` | **`F5` `tazelik`** — 🔴 *«önce **neden kapalı** gerekçesini ara»* | ⊙ **ARANDI VE BULUNDU** (ölçüm): `DbConnection` **0 satır** · `SyncState` **0 satır**. Tazelik `SyncState.last_synced_at`'ten okunur; kayıt yoksa kademe `bilinmiyor` olur ve o kademede tasarım gereği **sayı gösterilmez** → bayrak açılsaydı ürün **hiçbir sayı göstermezdi**. Bir gerileme değil bir **karartma**. 🔴 Ve asıl kusur bulundu: bayrak *«senkron bilinmiyor»* ile *«veri bayat»*ı **aynı kademeye** koyuyor; dosya-tabanlı kiracıda senkron diye bir kavram **yoktur** — bilinmemesi bir bayatlık işareti değil **sorunun geçersizliğidir**. `B4` doğru bir kural ama **bağlanabilir** kiracılar için yazılmış; dosya kiracısına uygulanınca *ölçülemeyeni kötü varsaymaya* dönüşüyor — o da bir uydurma, yalnız ters yönde. Gerekçe + `on` şartı yazıldı, kapı: `test_tazelik_kapali_gerekcesi.py`. *Bir yeteneğin kapalı olması bazen bir unutulmuşluk, bazen tek yazılmamış bir gerekçedir; ikisini ayırmanın tek yolu **aramaktır*** |
| ☐ | `D6` | **`F3` netleştirme ikilisi** — `katalog_belirsizlik` **kapısı** + `netlestirme_onceligi` kapsam ölçümü, **birlikte** | `bakiye` ₺11,86M vakası kapandı |
| ☐ | `D7` | **`F8` `llm_sema_kisitli`** — boşa giden token ölçülür, sağlayıcı kararı | `T-9` yapısal olarak kapandı **ya da** karar yazıldı |
| ☐ | `D8` | **`F4` `cekirdek_katman`** — iki sahiplilik çözülür, `B8` buraya oturur | `T-3` kapandı |
| ✅ | `D9` | **Her bayrağa yazılı `on` şartı** (`E-4`) — `test_bayrak_on_sarti.py` (4 kapı) | ⊙ Rapor **21** diyordu; ölçüm **9**: 24 `beta` bayrağın **15'inin** şartı YAML yorumunda zaten yazılıydı. *Rapordaki sayı bayattı — raporun kendi kuralının (**ölçüm yüzeyinden şüphelen**) bir örneği.* Kalan 9'a yapısal `on_sarti` alanı yazıldı, her biri **kendi kanıtından** türetildi (ör. `llm_sema_kisitli` → *«etkisiz bir bayrağı `on` yapmak, çalıştığını ilan etmektir»*; `orkestrator_plan` → *«kurulup koşamayan bir plan, kullanıcıya makbuz gösterip boş dönmektir»*). ⚠ Şartlar yorumdan **alana** taşındı: ilk taslağım `"ŞARTI" in blok` diye **metin arıyordu** ve böyle bir kapı yeniden yazılan her yorumda **sessizce yeşile döner**. Muafiyet listesi yalnız **küçülebilir** ve bayatlarsa kırmızı verir |
| ✅ | `D10` | **Rollout yüzeyi olmayan 5 bayrak** (`E-6`) | ⊙ Ölçüldü: **4'ünün yüzeyi artık var** (`diyalog_bellegi`·`niyet_izi`·`sosyal_sinif`·`t2_anlatici`), biri (`ayni_grain_gocu`) **bilerek** dışarıda — *derleme-zamanı beyanı, tenant açıp kapayamaz*. 🔴 Ama **kapısı yoktu** ve kapısı olmayan bir kapanış bir sonraki bayrakta sessizce geri gelir: `test_bayrak_rollout_yuzeyi.py` (4 kapı). ⚠ Gerekçe `description` **düzyazısındaydı**; yapısal bir alana (`rollout_yuzeyi_yok`) taşındı — *bir gerekçeyi düzyazıda saklamak onu bir gün silinebilir kılar; bir alana yazmak, silinince kapının bağırmasını sağlar*. Ters yön de kapılı: `features.yml`'de olup kayıtta olmayan ad bir **yazım hatasıdır** ve *açıldığı sanılan* bir yetenek üretir |

### E · PERFORMANS *(`§2c/P`)*

| ☐ | # | iş |
|---|---|---|
| ✅ | `E1` | `/ask` **47→177 ms** gerilemesinin kökü | 🎯 **BULUNDU ve ÖLÇÜLDÜ.** cProfile (10 istek, hepsi *«teşekkürler»* — ürün ~hiçbir iş yapmıyor): `ask()` **903 ms/istek**, `%65`'i `_niyet_izi`, içinde `_syn_hit` **istek başına 5.094** çağrı ve `re._compile` **60.720** kez → **5,66 s**. ⊙ Sebep: `_syn_hit` deseni her çağrıda **yerinde** kuruyordu; Python'un 512'lik desen önbelleği yüzlerce sinonimle **her turda çöpe dönüyordu**. Rapor bunu adıyla yazmıştı (*«sıfır memoizasyon»*) — teşhis doğruydu, **ölçüsü yoktu**. `_syn_desen` (`lru_cache`) eklendi: **903 → 316 ms (2,9×)**, davranış **birebir aynı**. *Bir kuralı her sorduğunda yeniden yazmak, kuralı değiştirmez — yalnız sormayı pahalı yapar* |
| ✅ | `E2` | Latency tavanı kapısı *(= `A10`)* | `A10` ile kapandı: `test_gecikme_tavani.py`, bütçenin tek sahibi `stats.GECIKME_BUTCESI_MS`, yalnız LLM'siz yollar. ⊙ Ve o kapı `E1`'in **ölçüsünü** verdi — *bir kökü aramak için önce onu görecek bir alet gerekir* |
| ✅ | `E3` | Kapı süresi ve düşüşün **ürün hızlanmasından** geldiğinin doğrulanması | ⊙ Bugünkü koşum: **454 sn (7,6 dk)** ve **payda DEĞİŞMEDİ** — `gercek_dunya` **2286**, semantik vaka **591** (ikisi de tabanla birebir). 🔴 `E3`'ün asıl sorusu buydu: *«kapsam kırpılarak mı?»* — **hayır**. Aradaki tek değişiklik `E1`'in memoizasyonu ve korpus **yalnız `route()`** koşuyor; yani hızlanan şey ölçüm aleti değil **ürünün kendisi**. ⚠ Dürüstlük kaydı: kapının **izole** bir önce/sonra ölçümü koşulmadı (memoizasyon bu koşumdan önce indi); kanıt **payda sabitliği + ürünün profilde ölçülmüş 2,9× hızlanması**dır. *Bir sürenin kısalması iki sebepten olabilir ve ikisi zıttır: ölçüm daha az şey görüyordur, ya da sistem daha hızlıdır — paydaya bakmadan hangisi olduğu bilinemez* |

---

### 🔴 ÇIKIŞ ÖLÇÜTÜ — *"her şeyi yaptık mı?"*

Bu rapor ancak şu üçü birden doğruysa kapanır:

1. **A bölümünün tamamı** ✅ — ölçüm altyapısı olmadan B/C/D'nin hiçbiri **kanıtlanamaz**
2. **B + C + D'nin her kalemi** ya ✅ ya **çürüten ölçümle** işaretli — *boş kalem yok*
3. `OPERASYON-DURUM.md`'de her kalem için **sayı + HEAD damgası** var

*Bir kontrol listesi, kalemleri işaretlenebilir olduğu kadar kontrol listesidir;
«iyileştirildi» diye işaretlenen bir kalem, işaretlenmemiş bir kalemdir.*

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


---

## EK — 2026-08-10 turlarının ölçülmüş sayıları (`A3` çıktısı)

`gercek_dunya` tabanı yeni şemayla yazıldı ve merdivenin şekli **ilk kez** sayıya döndü:

| sınıf | sayı | pay |
|---|---|---|
| payda (vaka) | **2286** | — |
| `dogru` (route bildi) | **96** | **%4,2** |
| `devir` (route çekildi → garson) | **2141** | **%93,7** |
| 🔴 `sessiz_yanlis` | **8** | %0,35 |
| `beyanli_kismi` | 41 | %1,8 |
| `netlestirme` | **0** | %0 |

⚠ Bu korpus bilerek **kullanıcının kendi kelimeleriyle** yazılmıştır; düşük route payı
bir kusur değil, merdivenin ölçülmüş şeklidir. Ama artık bir **sayı**, bir izlenim değil.

🔴 `netlestirme = 0` yeni bir borçtur: route ya biliyor ya çekiliyor, **ara ton yok**.

## EK — bu turda kapanan kusurlar (rapor dışı, canlı curl'den)

| # | kusur | akıbet |
|---|---|---|
| `R1` | `$2` yer tutucusu SQL'e sızıyordu → 0 satır + makbuz | ✅ doğrulayıcı reddediyor · `A9` sınıfı eklendi |
| `R2` | `peki ne yapmalıyız` → *«Görüşürüz!»* | ✅ tanınmış niyet artık veri sinyali (iki kanatta da) |
| `R3` | doğru cevabın yanında *«bu küpte tanımlı değil»* yalanı | ✅ beyan ad değil **kapsam** kıyaslıyor |
| `D1` | dönem kapısı **orkestratörün önünde** | ⚠ **açık borç — sıradaki turun konusu** |
| `B8` | `toplam_sure_dk` ≡ `toplam_durus_dakika` (aynı kavram, iki ad) | ⚠ açık borç (katalog) |
