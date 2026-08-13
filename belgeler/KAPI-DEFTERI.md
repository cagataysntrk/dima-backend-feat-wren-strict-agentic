# 🔴 KAPI DEFTERİ — *bir kapının değeri, kaç kez **haklı** kırmızı verdiğidir*

> `A8`. Rapor `§4f`'in kapanış cümlesi: *"Bir ölçüm aracının değeri, kaç kez kırmızı
> verdiğiyle değil, kaç kez **haklı** kırmızı verdiğiyle ölçülür — ve bu depoda o sayı
> **hiç tutulmadı**."*
>
> Bu dosya o sayıyı tutar. **Ekleme yapılır, satır silinmez.**

## Neden bir defter — ve neden otomatik olamaz

Bir kırmızının **haklı** olup olmadığı bir ölçüm değil bir **yargıdır**: aynı düşüş
(`%95,1 → %93,5`) bir gerileme de olabilir, bir devir de. `A4` bu ayrımı artık
otomatik **etiketliyor**, ama etiketin doğru olup olmadığını ancak sonraki olay söyler.

⊙ Bu yüzden defter iki sütun taşır ve ikisi **farklı zamanlarda** doldurulur:
*ne yakaladı* (koşum anında) ve *sonradan haklı çıktı mı* (olay kapandığında).

> *Kendi geçmişini tutmayan bir kapı, her seferinde ilk kez konuşuyormuş gibi dinlenir.*

---

## Tally

| | korpus (`--tam`) | tam süit | `eval.run` | konuşma senaryoları |
|---|---|---|---|---|
| ✅ **haklı kırmızı** | **2** | **4** *(2026-08-10)* | 0 | 0 |
| 🔴 **haksız kırmızı** *(yanlış karar verdirdi)* | **1** | 0 | 0 | 0 |
| ⏱ koşum başına maliyet | 1:57 → **13:00** | ~7 dk | ~1,5 dk | ~1,5 dk |

🔴 **Ve bu tablo raporun `§4f` teşhisini KISMEN çürütüyor.** Rapor *"tam süit: birkaç —
aynı kusurları seviye 1 de yakaladı"* diyordu. **2026-08-10'da süit 4 haklı kırmızı
verdi ve dördü de seviye 1'in görmediği sınıflardandı** (aşağıda). Yani süitin değeri
o gün ölçüldüğünde düşük görünmüştü; bugün ölçüldüğünde değil.

*Bir aletin değeri, ölçüldüğü güne aittir; bir kez ölçülüp kapatılan bir hüküm değil.*

---

## Kayıtlar

### 2026-08-04 · korpus · ✅ HAKLI

`gitas` compose yarışıyla korpustan **tamamen düştü**; payda **445 → 342** inerken
doğruluk **%93,2 → %94,3 ÇIKTI**. Sistem bozulurken sayı **iyileşti**.
⚠ Süit · `eval` · senaryolar **üçü de yeşildi** — bu kusuru başka hiçbir şey göremezdi.
**Eksen:** payda (kapsam).

### 2026-08-06 · korpus · ✅ HAKLI

`§EB/A` (`18c90c8`): `sessiz_yanlis` **12 → 18**. Kapsam değişikliğiydi ve kapsamın
ölçüsü korpustur. Değişiklik geri alındı, doğru karar.
**Eksen:** sessiz-yanlış.

### 2026-08-?? · korpus · 🔴 HAKSIZ — *ve faturası bir yeteneğin geri alınması oldu*

`G3` (*"cevapsız dal cevaplı yolu kesemez"*): korpus **%95,1 → %93,5** dedi, değişiklik
**geri alındı**. Düşüş **(b) sınıfıydı** — route çekilmiş, tur garsona devredilmişti ve
üretimde orada gerçek bir LLM var. Yani düşüş bir **kazançtı**.
🔴 **Sorulmadı.** `(a)/(b)` ayrımı o tarihte yoktu; `A4` tam olarak bunun için yazıldı.
**Eksen:** doğruluk yüzdesi — ve o eksen `E-2` ile **veto yetkisini kaybetti**.

### 2026-08-10 · tam süit · ✅ HAKLI ×4 *(hepsi aynı turda, hepsi benim kusurum)*

| # | kapı | ne yakaladı | seviye 1 görür müydü |
|---|---|---|---|
| 1 | `test_COZULMEYEN_ISIM_YOK` | `diyalog.py`'de `datetime` çözülemiyordu — o satır koştuğu an `NameError` | 🔴 **hayır** (statik ad çözümü) |
| 2 | `test_KAPI_kirmizi_VEREBILIR_dekor_degil` | 🔴🔴 **`A4`'ü kurarken kapının kırmızı verme yeteneğini bozmuşum**: eski şemalı tabanda `sessiz_yanlis` 0→7 artarken kapı **yeşil** veriyordu | 🔴 **hayır** — ve bu, kapının *kendi kendini* koruduğu tek satır |
| 3 | `test_modul_buyume` | `ask()` tavanı — ve *"tavanı yükseltme, modüle çıkar"* dedi; `B9` uygulaması `diyalog.py`'ye taşındı, `ask()`te 20 satır yerine **2** kaldı | 🔴 hayır |
| 4 | `test_uc_yetim_degil` | `/stats/plan` + `/stats/katalog` yetim uçtu — `API_ONLY` beyanı gerektirdi | 🔴 hayır |

⊙ **İkincisi bu defterin en değerli satırıdır:** ölçüm altyapısını iyileştirirken
**ölçüm altyapısını bozdum**, ve bunu yakalayan şey o altyapının kendi kapısıydı.
*Kırmızı veremeyen bir kapı bir dekordur* kuralı, kuralı yazanı yakaladı.

### 2026-08-10 · `A10` gecikme tavanı · ✅ HAKLI *(kurulduğu ilk koşumda)*

`meta` p95 **320 ms** · `catalog` **401 ms** (bütçe 300). Bütçenin kendi yorumu *"sabit
metin"* diyordu. Sebep yol değil **önündeki boru hattı**: bir selamlaşma bile şema +
`route()` + niyet zincirinin tamamını ödüyor.
**Eksen:** gecikme — ve bu eksen o güne kadar **hiç ölçülmüyordu**.

### 2026-08-10 · `eval.run` · ⚪ NÖTR

`ny-dE-musteri` `answer → chip`. Ölçüldü ve **devir** olduğu görüldü: route çekildi,
garson `kalite.ort_dE` ile **doğru** cevapladı. `A4`'ün sınıfı; geri alınmadı.
⚠ Bu satır bir *"haksız kırmızı"* değil çünkü kırmızı **vermedi** (tolerans içinde) —
ama vermiş olsaydı `G3`'ün tekrarı olurdu.

### 2026-08-10 · korpus (`A7` tetikli) · ⚪ YEŞİL — *ve bir hızlanmanın kanıtı*

`E1` memoizasyonundan sonra koşuldu: **454 sn**, korpus **%94,9** (taban %94,4) ✅,
semantik **%93,9** (taban %93,5) ✅, `sessiz_yanlis` **8** (değişmedi).

⊙ Bu satır bir *yakalama* değil bir **kanıt**: 2,9× hızlanan bir kod yolunun hiçbir
gerileme üretmediğini gösteriyor. Ve `A3`'ün ayrıştırılmış çıktısı ilk kez kapının
kendi özetinde: `doğru=96 · devir=2141 · netleştirme=0 · beyanlı_kısmi=41 ·
🔴 sessiz_yanlış=8 · payda=2286`.

⚠ **Payda sabit** (2286 · 591) — yani süre düşüşü kapsam kırpılmasından değil.
*Bir sürenin kısalması iki sebepten olabilir ve ikisi zıttır.*

### 2026-08-10 · korpus (`§DK` demeti) · ⚪ YEŞİL — *ve `A4` ilk kez KENDİ KARARINI yazdı*

`§DK` (katalog enum'u ifadeden) + `§DK-3` (route ile garson aynı menü) + `§DK-2` (süzgeç
değeri çapası) tek demette indi. Sonuç: korpus **%95,0** (taban %94,4) ✅ · semantik
**%93,9** · `sessiz_yanlis` **8** (değişmedi) · payda **2286** (sabit).

⊙ **Tek hareket:** `dogru 96 → 95`, `devir 2141 → 2142`. Ve kapı bunu **kendisi
sınıflandırdı**:

> *"⚠ DEVİR (gerileme DEĞİL): dogru −1 ama devir+netleştirme +1 — kayıp değil DEVİR.
> ⚠ fiyatı: 1 soru artık bir LLM turu ödüyor."*

🔴 **Bu satır `A4`'ün varlık sebebidir ve `G3`'ün tam tersidir.** `G3`'te aynı şekildeki
bir düşüş **sorulmadan** gerileme sayılmış ve bir yetenek geri alınmıştı. Bugün aynı
şekil geldi, etiket **otomatik** kondu ve **fiyatı da yazıldı** — bir LLM turu.
*Bir ölçüm aracının olgunluğu, verdiği sayıda değil, o sayının ne anlama geldiğini
söyleyebilmesindedir.*

**Eksen:** doğruluk yüzdesi — ve `E-2` gereği o eksenin **veto yetkisi yok**.

### 2026-08-10 · korpus · 🟡 YAN BULGU — *kapı bir MUTFAK kusuru gösterdi*

Koşum kütüğünde tekrar eden bir uyarı: `veri_araligi okunamadı: cube=enerji_sapma` ve
`cube=cusum` — `donem_tarih` kolonu kaynakta **yok** (`Binder Error: Referenced column
"donem_tarih" not found`).

⊙ İki küp, katalogda **var olmayan bir zaman ekseni beyan ediyor**. `varsayilan_donem`
bunu doğru karşıladı (ölçemedi → **hiçbir şey varsaymadı**, fail-closed) — yani bayrağın
tasarımı canlıda sınandı ve tuttu. Ama beyanın kendisi bir borç: o küplerde dönem
soruları **hiç** çalışamaz.

⚠ Bir *"haklı kırmızı"* değil (kapı yeşil verdi) — ama defterin amacı yalnız kırmızıları
saymak değil, kapının **ne gösterdiğini** kaydetmek. *Bir aletin en ucuz bulgusu, aramadığı
şeyi yolda görmesidir.*

---

### 2026-08-10 · korpus · ✅ HAKLI ×3 — *aynı değişiklikte, üst üste, ve her biri BAŞKA bir şey öğretti*

`D8` (kanonik müşteri anahtarı) üç biçimde denendi; kapı üçünde de **kırmızı** verdi ve
üçü de **haklıydı**. Bu satır defterin en öğretici kaydı, çünkü kırmızıların **sırası**
bir teşhis zinciri kurdu:

| # | denenen biçim | kapının ölçtüğü | öğrettiği |
|---|---|---|---|
| 1 | `label: müşteri kodu` + geniş sinonim | `doğru 95→80` · `sessiz 8→10` · `payda +11` | `_with_label` etiketi **kelimelerine de ayırıyor** → `musteri` belirsiz token oldu |
| 2 | etiket **ve** sinonim yok | `doğru 79` · `payda 2288` | boyut **adlandırılamaz** oldu; üreteç ham adıyla sordu, route **kendi boyutunu tanımadı** |
| 3 | etiket yok, sinonim = teknik ad | `doğru 79` — **2 ile BİREBİR aynı** | 🎯 sorun sinonimde **değil**, boyutun **varlığında** |

⊙ **Üçüncü kırmızı en değerlisiydi: iki koşumun AYNI sayıyı vermesi bir teşhistir.**
Sinonim biçimini değiştirmek hiçbir şeyi kıpırdatmayınca aranacak yer daraldı.

⟳ **VE İLK TEŞHİSİM YANLIŞTI — kendi ölçümüm çürüttü.** `_match_cube`'un
`dim_owners == 1` tie-break'ini suçlamış ve bunu **doğrulamadan** deftere yazmıştım.
Sonra in-process A/B koştum (aynı şema, tek fark üç boyut): **1072 gerçek korpus
sorusunda DEĞİŞEN: 0**. Route davranışı kanıtlanabilir biçimde **aynı**.

🎯 Yani kapı haklıydı ama **gösterdiği yer** ürünün cevapları değil, **korpusun
ürettiği soru kümesiydi** — üreteç soruları da beklentileri de katalogdan türetiyor.
🔴 Bu, bu defterin ilk kaydının **ayna görüntüsü**: `gitas`'ta sistem bozulurken sayı
**iyileşmişti**; burada sistem değişmedi, sayı **kötüleşti**.
*Bir metriğin kıpırdaması, ölçtüğü şeyin kıpırdadığı anlamına gelmez.*

**Eksen:** sessiz-yanlış — ve `E-2` gereği **veto yetkisi olan tek eksen**.

⚠ **Bir yanlış-pozitif değildi ve bu önemli:** yetenek **gerçekti** (7 küp tek anahtarda,
orkestratör `{M1001 · ciro ₺40.480.479 · şikayet 928}` üretti). Kapı *«bu çalışmıyor»*
demedi, *«bunun bedeli şu»* dedi. Karar geri almaktı çünkü `F1.1` bağlayıcı:
**kapsam kazancı sessiz-yanlışla satın alınmaz.**

### 2026-08-10 · korpus · ⚪ YEŞİL — *ve bir izolasyonun kanıtı*

Geri alma sonrası: `doğru=95 · devir=2142 · 🔴sessiz_yanlış=8 · payda=2286` — son yeşil
tabanla **birebir**. ⊙ Bu koşum aynı zamanda `C3-D` ve `§FÇ`'nin (kapısız commit edilmiş
iki demet) **korpus-nötr** olduğunu kanıtladı; yani gerilemenin **tamamı** pack
değişikliğiydi. *Bir değişikliği geri almak bir kayıp değildir; neyin ne yaptığını
öğrenmenin en kesin yoludur.*

⚠ Ve bir maliyet kaydı: bu teşhis **dört kapı koşumu** (≈32 dk) tuttu. Üçü zorunluydu
(her biri yeni bilgi verdi), dördüncüsü kapısız commit edilmiş iki demetin **ertelenmiş**
kapısıydı. *Kapıyı ertelemek onu ödememek değildir; faizli ödemektir.*

---

### 2026-08-10 · korpus (`§D2/K` + `§DK-4`) · ⚪ YEŞİL — *ve `A12` ilk kez KONUŞTU*

`§D2/K` (oylama eşiği kısayolu) + `§DK-4` (zaman ekseni ifadesi) demeti:
**%95.1** (taban %94.4) ✅ · `doğru=95 · devir=2142 · 🔴sessiz_yanlış=8 · payda=2286`
— taban **birebir**, doğruluk **yükseldi** (%95,0 → %95,1).

⊙ Ve koşum kütüğünde bu satır çıktı:

> *⚠ taban `_nufus` taşımıyor (bu alandan önce yazılmış) → `A12` KIYASLANABİLİRLİK ÖN
> KOŞULU bu koşumda **ATIL**.*

🎯 **`A12` daha ilk koşumunda kendi eksikliğini ilan etti.** Yeni bir kapının en tehlikeli
hâli *«yazıldı ama hiç ateşlemiyor»*tur; bu satır o hâli **görünür** kıldı. ⚠ Ama
görünür-atıl da hâlâ atıldır: taban `--taban-yaz` ile yenilenerek kapı canlandırıldı.

*Bir kapının neyi sınamadığını söylemesi, sınadıklarını saymasından önemlidir — ama
söylemek yapmanın yerine geçmez.*

---

### 2026-08-10 · korpus · ⚪ YEŞİL — *ve `A12` İLK KEZ GERÇEKTEN ÇALIŞTI*

`§UY/K` + `§D2/K` + `§DK-4` + **203 satırlık refactor** (iki yeni modül) tek demette:

```
kapı yeşil · ✅ sabit: dogru +0 · sessiz_yanlis 0 · devir +0
%95.1 (taban %94.4) · payda 2286 · nüfus imzası TUTTU — «ATIL» uyarısı YOK
```

⊙ **Bu koşumun değeri sayıda değil, sayının ANLAMINDA.** Önceki koşumlarda kapı
*«değişmedi»* diyordu ve bu bir **varsayımdı**: soru kümesinin aynı kaldığını kimse
sınamıyordu. Bugün imza tuttu, yani *«aynı soruları sordum ve aynı cevapları aldım»*
cümlesi **kanıtlandı**.

🔴 Ve aynı gün bu kapının **yokluğu** dört koşuma mal olmuştu (`D8`): katalog büyüyünce
sayılar kaydı, kapı **GERİLEME** dedi, ben üç ayrı düzeltme denedim — ve sonunda
in-process A/B *«1072 soruda DEĞİŞEN: 0»* dedi. Aynı gün içinde bir kapı **eksikliğiyle**
ve **varlığıyla** ölçüldü.

*Bir ölçümün değeri, verdiği sayıda değil, o sayının neyi ölçtüğünü bilmesindedir.*

### 2026-08-10 · modül büyüme tavanı · ✅ HAKLI — *ve tavan YÜKSELTİLMEDİ*

Günün birikimi üç tavanı birden aştı: `ask()` **1369>1345** · `cube_router`
**1964>1893** · `ask.py` **2792>2758**.

⊙ Kapının kendi mesajı yolu gösterdi: *«yeni davranışı MODÜLE ÇIKAR, tavanı yükseltme.
Tavanı yükseltmek kapıyı kapının kendisiyle çürütür.»* → **203 satır** iki yeni modüle
çıkarıldı (`ters_yon` 141 · `deger_eslesme` 62) ve `huni_karari` ile `ask()`ten 17 satır
daha indi. Taşınamaz kalan **4 kalem** `sha + Δ + gerekçe` ile yazıldı.

⚠ **Bu kapı bir «stil» kapısı değil bir MİMARİ kapısıdır:** çıkarma sırasında ayrımlar
kendiliğinden doğru yere düştü — `cube_router` *«bu soru hangi sorguya çevrilir»*
sorusunu **cevaplar**, `ters_yon` *«kullanıcının sözü hangi ada karşılık gelir»*
sorusunu **kaydeder**. Biri çalışır, öteki öğrenir.

*Bir tavanı yükseltmek bir kazanç değildir; ölçülmeden yükseltmek bir borçtur.*

---

### 2026-08-10 · korpus (`§ÜK` + `§ÖB`) · ⚪ YEŞİL — *ve BEKLENTİM TUTMADI, bu bir bilgi*

Üç yanlış-pozitif beyan düzeltmesinden (`§UY/K` · `§ÜK` · `§ÖB`) sonra **beklentim
`beyanli_kismi`'nin düşmesiydi** — çünkü o sınıf tam da bu beyanlardan sayılıyor.

```
kapı yeşil · ✅ sabit: dogru +0 · sessiz_yanlis 0 · devir +0
doğru=95 · beyanlı_kısmi=41 (DEĞİŞMEDİ) · payda=2286 · nüfus imzası TUTTU
```

🔴 **Tahmin tutmadı ve bu bir kusur değil bir ÖLÇÜM:** korpusun 41 beyanlı-kısmi vakası,
düzeltilen üç sınıfın **hiçbirinden** değil. Yani o üç kusur **canlı kullanıcı yolunda**
vardı, korpusta **yoktu**.

⊙ Sebep deponun kendi yazılı körlüğü (`CLAUDE.md`): *«Korpus soruları katalogdan
üretiliyor, yani hepsi doğru yazılmış… gerçek kullanıcı deneyimi kırık olabilir — sayı
yalan söylemiyor, o yolu GÖRMÜYOR.»* Bugün o cümle **üç kez** doğrulandı: üç kusur da
curl turunda bulundu, korpusta değil.

⚠ Ve bu, kapı sıklığı kuralının **gerekçesidir**: korpus bir gerileme kalkanıdır, bir
kusur bulucu değil. *Bir aleti, görmediği şeyi araması için koşturmak, onu koşturmamakla
aynı bilgiyi verir — yalnız daha pahalıya.*

---

---

## Nasıl eklenir

Bir kapı koşumu kırmızı verdiğinde **aynı gün** bir satır açılır: *hangi kapı · ne
yakaladı · hangi eksen · seviye 1 görür müydü*. **Haklı/haksız sütunu boş bırakılır**
ve olay kapandığında (düzeltme kabul edildi ya da geri alındı) doldurulur.

⚠ Boş bırakılan bir yargı bir eksiklik değil, **henüz bilinmeyen** bir şeydir — ama
sonsuza kadar boş kalırsa o kapı hakkında hiçbir şey öğrenilmemiş demektir.
