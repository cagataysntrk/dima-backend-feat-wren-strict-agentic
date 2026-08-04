# Türkçe'de semantik-katman tabanlı konuşan BI

### kapsam · doğruluk · risk-kapsam · çok-turlu dayanıklılık

**Sürüm:** FAZ 4.7 · **HEAD** `837914a` · tüm ölçümler `--network none` altında, **LLM'siz**,
**sabit tohumlu** ve **tek komutla** yeniden üretilebilir.

---

## 0 · Bu raporun okunma kuralları — **önce bunlar**

> 🔴 **HER SAYI BİR KOMUTLA GELİR.** Komutsuz bir sayı bu raporda **yoktur**. Bir satırda
> `<sayı> @837914a · <komut>` görmüyorsanız o satır bir sayı değil, bir **cümledir**.

> 🔴 **NETLEŞTİRME AYRI SATIRDIR VE PAYDADAN ÇIKARILMAZ.** *Rakiplerin manşet sayılarını
> kıyaslanamaz yapan şey tam olarak budur: her satıcı reddedilenleri paydadan sessizce
> çıkarıyor ve geriye kalan sayıyı manşete taşıyor.* Burada üç sayı birden yayımlanır ve
> hangisinin hangisi olduğu yazılıdır.

> 🔴 **GÜRÜLTÜ TABANI: 10 PUAN.** BIRD/Spider'da anotasyon hata oranı **%52,8 / %62,8**
> ölçüldü. **Bu eşiğin altındaki hiçbir fark yorumlanmaz** — ne bizim lehimize, ne
> aleyhimize.

> ⚠ **`⊘ ÖLÇÜLEMEDİ` üçüncü bir haldir.** Ne geçti ne kaldı. Sebebi yazılmadan
> yayımlanmaz ve bir başarısızlık olarak **okunmaz**.

> ⚠ **`[DOĞRULANMADI]`** damgalı her cümle, birincil kaynağı okunmamış bir iddiadır ve
> öyle kalır. Rakip iddiaları bu damgayı taşır.

---

## 1 · Neden bu rapor — ölçülmemiş olan ne?

**BIRDTurk** (arXiv 2602.03633 / SIGTURK 2026) Türkçe cezasını **text-to-SQL'de** ölçtü.
**Semantik katmanın Türkçe katkısı hiç ölçülmedi.** Aradaki fark şudur: text-to-SQL bir
dil modelinden **SQL** ister; semantik katman ondan yalnız **hangi ölçü, hangi boyut,
hangi dönem** sorusunun cevabını ister ve SQL'i **kendisi** üretir.

İkinci düzenin Türkçe'de ne kazandırdığı — ya da kaybettirdiği — **bu rapora kadar
ölçülmedi**.

⚠ Kıyas zemini olarak sık anılan **Snowflake BIRD %57→%78** sıçraması
**`[DOĞRULANMADI]`** — birincil kaynak okunmadı ve bu raporda bir dayanak olarak
**kullanılmıyor**.

---

## 2 · Mimari — tek paragrafta

Bir soru **merdivenden** iner ve **ilk cevaplayan basamakta durur**:

    VQR replay  →  route() [SIFIR LLM]  →  Intent-JSON [cube+llm]  →  Discovery [llm:*]

🔴 **Sayıyı her zaman küp koyar.** LLM ya hiç çağrılmaz (`route`), ya yalnız **seçim**
yapar (Intent-JSON), ya da en son basamakta SQL üretir (**Discovery** — ve o cevap
*"doğrulanmamış"* rozetiyle gelir). Anlatı bir **guard**'dan geçer: eşleşmeyen sayı
taşıyan cümle **yayımlanmaz**. En kötü durum *"süssüz ama doğru"*tur.

---

## 3 · KAPSAM — kaç soru cevaplanabiliyor

**Komut** — `python lab/kapi.py --tam` *(≈1 dk 50 sn, LLM'siz, kotasız)*

| şirket | tur | erişim | **doğru-cube** |
|---|---|---|---|
| demo-boyahane | 5.306 | %69 | 3266/3519 = **%92** |
| gitas | 2.479 | %72 | 1517/1696 = **%89** |
| atiksan | 1.447 | %69 | 931/949 = **%98** |
| gulteks | 1.618 | %68 | 995/1040 = **%95** |
| **TOPLAM** | **10.850** | — | **%93,1** *(taban %93,2)* |

**Semantik vaka** *(şişme giderilmiş payda)*: **407/444 = %91,7** — şişme katsayısı
**16,2×**. Yani ham tur sayısı bir kapsam ölçüsü **değildir**; aynı semantik vaka
onlarca yüzeysel varyantla tekrar sorulur ve ham sayı kapsamı **16 kat** olduğundan
büyük gösterir. Bu rapor **her iki paydayı da** yayımlar.

🔴 **KURAL A — payda dondurulmuştur.** *"Korpus uzunsa soru azaltalım"* ölçülüp
**reddedildi**: bir defasında `gitas` bir derleme yarışıyla korpustan **tamamen düştü**,
payda **445 → 342** indi ve doğruluk **%93,2 → %94,3'e ÇIKTI**. Sistem bozulurken sayı
**iyileşti**. *Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla da olur* —
ve o sinyal yalnız **payda sabitliğine** dayanır.

⚠ **Korpusun BİLİNEN körlüğü, gizlenmiyor:** sorular **katalogdan** üretiliyor, yani hepsi
**doğru yazılmış**. **Typo yolu korpusta hiç sorulmuyor.** %93,1 yeşilken gerçek kullanıcı
deneyimi kırık olabilir — sayı yalan söylemiyor, **o yolu görmüyor**.

---

## 4 · DOĞRULUK — §C/16, uçtan uca *(bu raporun ön koşuluydu)*

**Komut** — `python lab/uctan_uca.py` · **puanlama kuralı koşumdan ÖNCE ilan edildi**

> *Bir cevap ancak **dönen değer**, **varlık kapsamı** ve **zaman/filtre semantiği** altın
> cevapla eşleşiyorsa **doğru** sayılır.*

| şirket | n | **doğru** | netleştirme *(ayrı satır)* | cevaplanan içinde |
|---|---|---|---|---|
| demo-boyahane | **155** | **%76,1** | %16,8 (26) | %91,5 |
| gitas · atiksan · gulteks | 0 | ⊘ | ⊘ | ⊘ |

⊘ **Üç şirket ölçülemedi:** 132 vakanın tamamında **altın cevap üretilemedi** (mssql lab
fixture'ları `--network none` altında tabloya erişemiyor). Bu bir sistem kusuru **değil**,
bir **ölçüm sınırıdır** ve öyle raporlanıyor.

🔴 **Manşet sayı hangisi:** **%76,1** — yani **netleştirme paydada**. *"%91,5"* de
doğrudur ama o **cevaplananlar içindeki** orandır ve manşete taşınırsa rakiplerin yaptığı
şeyin aynısı yapılmış olur.

⚠ **Bu sayının ölçmediği şey:** altın cevap da sistemin cevabı da **aynı motoru**
kullanır; yalnız **girdileri** ayrılır (biri parametreden, öteki **doğal dilden**).
Ölçülen şey **anlamadır**, motorun kendi doğruluğu **değil**.

---

## 5 · RİSK-KAPSAM — sektörde yayımlanmayan eğri

**Komut** — `python lab/risk_kapsam.py`

MIMARI §9.1: *"hiçbir sevk edilmiş BI ürünü abstention kapısı ya da risk-kapsam eğrisi
yayınlamıyor."*

🔴 **Eğri skaler bir `confidence` üstünde DEĞİL.** Literatürün kara-kutu güven sinyalleri
**0,61–0,68 AUROC**'ta platoluyor. Bizimki bir **tahmin değil bir mimari beyandır**: eğri
**ayrık kapılarımız** üstünde tanımlı (`route → tie_chip → intent → discovery`) ve her
nokta bir **determinizm sınıfı** taşır — hangi yoldan geçildiği **ölçülür**, tahmin
edilmez.

⚠ `hata_orani` **bilerek YOK**: bir kapının hata oranını o araç ölçemez (doğruluk
korpusun/§C-16'nın işi). Yazsaydık **uydurma** olurdu.
⚠ `consistency_k` uyumu bir güven eşiğine **dönüştürülmedi**: *"bir model son derece
self-consistent olup yine de **tutarlı biçimde YANLIŞ** olabilir."*

---

## 6 · ÇOK-TURLU DAYANIKLILIK — ve **hedefimizi tutturamadık**

**Komut** — `python lab/sharding.py` · sabit tohum

ICLR 2026 En İyi Makale (*LLMs Get Lost In Multi-Turn Conversation*): 200.000+ simüle
konuşma, 15 model → ortalama **−%39 doğruluk**. Azaltma önerisi **recap** (+16 puan).
Bizim mimarimiz recap'in **deterministik** hâlini yapısal olarak uyguluyor: her turda
`cube_query` **geri gönderiliyor** ve `deterministic_refine` onu **düzenliyor** — taşınan
şey bir metin özeti değil, **yapının kendisi**.

**Sonuç — `demo-boyahane`, 44 konuşmalık sabit kohort** *(tek istatistiksel geçerli kohort)*:

| tur | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| tam cevaplanan | %63,6 | %63,6 | %59,1 | %54,5 | **%45,5** |

🔴 **Düşüş −%18,2. Hedefimiz −%10'dan azdı → KALDI.** Makalenin ölçtüğü **−%39**'un
yarısından az, ama **kendi hedefimizi tutturamadık** ve bu **yayımlanıyor**.

**Kök neden isimlendirildi:** kaybedilen turların **tamamı** aynı şekle sahip — takip
mesajı **çıplak bir ikinci ölçü adı**. `deterministic_refine` ölçü eklemeyi *"bir de …
ekle"* ipucuyla tanıyor; ipuçsuz ad bir yenileme sayılmıyor. **Bu turda bilerek
düzeltilmedi:** ölçtüğü kusuru aynı turda düzelten bir alet, bir dahaki sefere neyi
ölçtüğünü bilemez.

⚠ Diğer üç şirketin kohortu **7–10**; hedef o çözünürlükte **ayırt edilemez** (`⊘`) —
`n=8`'de tek bir konuşma **%12,5 puan** oynatır.

---

## 7 · Yeniden üretilebilirlik — **tek komut, ağsız, sabit tohum**

```bash
docker build -t dima-api -f Dockerfile . && docker build -t dima-test -f Dockerfile.test .
docker run --rm --network none -v "$PWD:/repo" -w /repo/backend -e DIMA_VQR_EMBEDDER=off \
  dima-test python lab/kapi.py --tam          # kapsam
docker run --rm --network none -v "$PWD:/repo" -w /repo/backend -e DIMA_VQR_EMBEDDER=off \
  dima-test python lab/uctan_uca.py           # doğruluk (§C/16)
docker run --rm --network none -v "$PWD:/repo" -w /repo/backend -e DIMA_VQR_EMBEDDER=off \
  dima-test python lab/risk_kapsam.py         # risk-kapsam
docker run --rm --network none -v "$PWD:/repo" -w /repo/backend -e DIMA_VQR_EMBEDDER=off \
  dima-test python lab/sharding.py            # çok-turlu
```

**Hiçbiri LLM çağırmaz.** Günlük kota dolsa bile koşarlar. `--network none`, yani bir
ağ servisine gizli bağımlılık **yapısal olarak imkânsızdır**.

---

## 8 · Bu raporun kendi sınırları — **kayıt için**

| sınır | neden yazılı |
|---|---|
| Doğruluk tek şirkette ölçüldü (**n=155**) | üçü mssql fixture'ı; `⊘` bir sonuç değil bir **beyandır** |
| Korpus **typo yolunu** hiç sormuyor | sorular katalogdan üretiliyor, hepsi doğru yazılmış |
| Altın cevap ile sistem **aynı motoru** kullanır | ölçülen **anlama**dır, motorun doğruluğu değil |
| Çok-turlu hedef **tutmadı** (−%18,2 vs −%10) | kök neden isimlendirildi, borç defterinde |
| Rakip kıyas sayıları | **`[DOĞRULANMADI]`** — birincil kaynak okunmadı |
| `⊘` sayısı azımsanmaz | üç şirket · 132 vaka · sebebiyle yazılı |

🔴 **Bu tablo raporun en önemli bölümüdür.** *Sınırlarını yazmayan bir ölçüm raporu, bir
ölçüm raporu değil bir pazarlama belgesidir.*
