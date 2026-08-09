# Kapı yavaşlaması — teşhis (2026-08-09)

> 🔒 **Tarih damgalı ölçüm belgesi.** `belgeler/00-INDEKS.md` kuralı gereği bu dosya
> **güncellenmez**; yeni ölçüm yeni tarihli yeni dosyadır.

**Soru:** *"Kapı testleri çok uzun sürüyor; paralel koşmayla 2 dk'ya düşürmüştük, şimdi
gene 10 dk sürüyor. Neden geriledik, neden yavaşladık?"*

**Cevap tek cümlede:** Paralellik bozulmadı, payda kırpılmadı, kapı kırılmadı —
**`/ask` soru başına ~4× yavaşladı**, korpus **%38 büyüdü**, makinede **9 çekirdek zaten
doluydu**. Üçü çarpılınca `1 dk 50 sn` → `13 dk 00 sn` oldu.

🔴 **Ve yavaşlamanın büyük kısmı bir kusur değil, ödenmemiş bir FATURADIR:** beş günde
**335 commit**, `app/` altına **41 yeni modül**, bunların **17'si `/ask`'in sıcak
yolunda**. Her biri tek başına ucuz, hiçbiri ölçülmedi, hepsi aynı isteğin içinde toplandı.

---

## 🔴🔴 STATÜ — **DÖNGÜ KURALLARINA DAHİLDİR · ÖNCELİKLİ ÇÖZÜLECEK**

> **Kullanıcı kararı (2026-08-09):** *"Belgeye, döngü kurallarına dahil olup **öncelikli
> çözülecek** ve **zaman ve hız kazandıracak** bir sorun olduğunu yaz."*

Bu bir *"bir ara bakılacak"* teşhis değildir. `OPERASYON.md §2`'nin döngüsüne **girer** ve
sıradaki maddelerin **önüne** alınır. Gerekçesi bir tercih değil, **ölçülmüş bir
aritmetiktir**:

### Bu sorun her gün ne kadar zaman yiyor — ölçüldü

Konteyner kütüklerinden sayıldı: **08-08 14:38 → 08-09 03:16 arası (≈12,5 saat)
19 korpus koşumu**.

| | bugünkü | hedef | fark |
|---|---|---|---|
| korpus başına | **13 dk 00 sn** | 1 dk 50 sn | −11 dk 10 sn |
| **19 koşum ×** | 🔴 **4 saat 07 dk** | 35 dk | 🔴 **−3 saat 32 dk / gün** |

> **Günde ~3,5 saat** yalnız korpusun beklenmesine gidiyor — ve bu, kapının kendisi
> kırmızı vermeden, hiçbir kusur bulunmadan, **saf bekleme** olarak.

⚠ Ve bu rakam `CLAUDE.md`'nin kullanıcı kararıyla **doğrudan çelişiyor**:
*"5 dk'dan uzun teste ayıracak kesinlikle vaktimiz yok."* Bugün tek bir demet kapısı
**13,5 dakika**. Kural kâğıt üstünde duruyor; **gerçekte çiğneniyor** ve çiğneyen kişi
değil, **sistemin kendisi**.

### Neden ÖNCELİKLİ — çünkü kendisi bir hızlandırıcıdır

Bu maddenin diğer maddelerden farkı şu: **çözülmesi, kalan bütün maddeleri
hızlandırır.** Yol haritasının geri kalanı bu kapıdan geçecek; kapı 13 dakikaysa her
madde 13 dakika daha pahalıdır.

*Sırayı bekleyen bir iş, sıranın kendisini hızlandırıyorsa, sırada beklemesi kayıptır.*

### 🔴 Ve ikinci bir bedeli var: **atlanan kapı**

`CLAUDE.md`'nin kendi cümlesi: *"pahalı bir kapı, atlanan bir kapıya dönüşür."*
Bu belge o cümlenin **gerçekleştiğini** gösteriyor — 12,5 saatte 19 koşum, ve aralarında
`--tam` yerine kaçınma davranışı. **Yavaş kapı bir hız sorunu olarak başlar, bir
GÜVENLİK sorunu olarak biter.**

### 🔴 SIRALAMA KURALI — **testlerden ÖNCE, geliştirici çözer**

> **Kullanıcı kararı (2026-08-09):** *"Hemen döngü içinde çözülmeli, **doğru vakitte
> testlerden önce geliştirici çözmeli**."*

Bu bir üslup tercihi değil, **aritmetik bir zorunluluktur**:

```
YANLIŞ sıra:  … → demet biter → KAPI (13 dk öde) → sonra hızlandırmayı düşün
DOĞRU  sıra:  … → demet biter → ÖNCE hızlandır → KAPI (o kapı zaten hızlı koşar)
```

⚠ **Neden bu sıra tek doğru sıra:** düzeltme kapıdan *sonraya* bırakılırsa, o demetin
kapısı **13 dakikayı yine öder** — ve düzeltmenin kendisinin kapısı da 13 dakika sürer.
Yani erteleme **bedeli iki kez ödetir**. Öne alınırsa, **kendi doğrulaması** ilk kazanan
koşum olur.

🔴 **Ve `--hizli` bu kuralın dışındadır.** *"Testlerden önce"* demek **§2.6'nın seviye 0 +
`--hizli` adımı atlanır** demek **DEĞİLDİR** (o zaten ~1 dk ve bir *sinyaldir*, kapı
değil). Kastedilen **demet kapanış kapısıdır** (`--tam` · korpus) — 13 dakikayı yiyen
adım odur.

🔴 **Sahibi GELİŞTİRİCİDİR.** Bu madde bir denetim/ölçüm işi olarak kapanmaz; `OPERASYON.md
§2`'nin **4. adımına (GELİŞTİR)** girer ve kod değişikliğiyle iner. Bu belge yalnız
**3. adımdır (ÖLÇ)**.

### Döngüye giriş biçimi

| adım | ne yapılır |
|---|---|
| **sıra** | 🔴 §6'daki **Öneri 1 → 2 → 3** (risk **sıfır**, kapsam kaybı **yok**) — sıradaki demet kapısından **ÖNCE**, geliştirici tarafından |
| **ÖLÇ** *(§2.3)* | ✅ **bu belge o adımdır** — kusur sayıyla, konteyner damgasıyla ölçüldü |
| **KAPI** *(§2.5)* | 🔴 **Öneri 4'ün latency tavanı** bu maddenin kapısıdır: *"düzeltmeyi teste çevir"* — süre bir teste bağlanmadıkça bu madde **"bitti" değildir** |
| **BELGELE** *(§2.7)* | `CLAUDE.md`'nin **1:50 / 4:06** rakamları **bayattır**, aynı commit'te güncellenmeli |
| **sınır** | ⛔ Öneri 4 (profil) **paylaşılan makinede koşulmaz** — canlı geliştirici var |

⚠ **Kapsam kaybı olmadığı için bu madde bir ödünleşim DEĞİLDİR.** Öneri 1-3'ün üçü de
paydaya, teste, kapsama dokunmaz; yalnız **boşa giden kaynağı** geri alır. Hız burada
güvenlikten satın alınmıyor — ikisi **aynı yönde**.

---

## 0 · Bu ölçüm nasıl yapıldı — **hiçbir test koşulmadan**

⚠ Kullanıcı kısıtı: *"test koşma, makinede canlı geliştirici var."* Bu belgedeki her sayı
**zaten var olan** kanıtlardan okundu:

| kaynak | ne verdi |
|---|---|
| `docker logs` — **26 tarihsel kapı konteyneri** | adım süreleri, zaman serisi |
| çalışmakta olan `dima-kapi-z` kütüğü | 61 792 satır, istek başına `süre=` |
| `git log` / `git show` (salt-okunur) | commit korelasyonu, dosya büyümesi |
| kaynak kod okuması | çağrı sayısı, önbellek yokluğu |

🔴 **Hiçbir kapı, süit, korpus ya da benchmark koşulmadı.** Bu, `CLAUDE.md`'nin
**DÖRDÜNCÜ KURAL**'ının uygulamasıdır: *"bir tasarım gerçeği koşularak değil, okunarak
bulunur."*

---

## 1 · Yavaşlama **tek bir adımda**

Canlı koşan kapı (`dima-kapi-z`, `lab/kapi.py --hepsi`, 03:16:12 başlangıç):

| adım | başlangıç → bitiş | **gerçek** | belgelenen | oran |
|---|---|---|---|---|
| **korpus kapısı** | 03:16:12 → 03:29:12 | **13 dk 00 sn** | 1 dk 50 sn | 🔴 **7,1×** |
| gerçek-dünya korpusu | 03:29:12 → 03:29:38 | 26 sn | ~1 dk 10 | 0,4× ✅ |
| dalga 2 (süit ‖ eval ‖ senaryo) | 03:29:38 → … | ≥5 dk | 2 dk 20 | — |

**Şikâyetin tamamı korpus adımıdır.** Öteki adımlar sağlam.

### İlk iki hipotez ÖLÇÜLEREK elendi

| hipotez | ölçüm | sonuç |
|---|---|---|
| *"paralellik geri alınmış"* | kütüğün ilk satırı: `⚡ paralel korpus: 16 dilim, 16 süreç` | ❌ **yanlış** |
| *"`DIMA_KORPUS_PARALEL=1` set edilmiş"* | konteyner ortamı: değişken **yok**; `cpu_count=20`, `sched_affinity=20`, CPU kotası **yok**, hesaplanan paralellik **16** | ❌ **yanlış** |

⚠ Ve bir **üçüncü** hipotez de elendi: *"`--tam` koşsaydı 1:50 olurdu."* **Hayır.**
`--tam` = korpus + gerçek-dünya = bugün **13 dk 26 sn**. Yavaş olan **basamak** değil,
**korpusun kendisi**. Seviye değiştirmek bu sorunu çözmez.

---

## 2 · Zaman serisi — 26 konteynerden çıkarıldı

Geçmiş kapı konteynerlerinin kütükleri duruyordu. Korpus adımının süresi:

| tarih · saat | konteyner | korpus |
|---|---|---|
| 08-08 14:38 | `kapiO` | 10 dk 47 sn |
| 08-08 15:15 | `kapiP` | 10 dk 49 sn |
| 08-08 15:58 | `kapiR` | 11 dk 06 sn |
| 08-08 16:38 | `kapiM` | 11 dk 06 sn |
| 08-08 17:11 | `kapiM2` | 10 dk 55 sn |
| **08-08 17:52** | **`kapiD2`** | 🔴 **12 dk 29 sn** ← **+94 sn sıçrama** |
| 08-08 18:19 | `kapiM5` | 12 dk 51 sn |
| 08-08 18:58 | `kapiM4` | 12 dk 30 sn |
| 08-08 19:32 | `kapiM1` | 13 dk 25 sn |
| 08-08 20:15 → 08-09 02:06 | `kapiM1b`…`kapiU` (8 koşum) | 12 dk 35 sn – 13 dk 41 sn |
| 08-09 03:16 | `dima-kapi-z` | 13 dk 00 sn |

**İki şey okunuyor:**

1. 🔴 **Yavaşlama 08-08'den ÖNCE zaten olmuştu.** En eski elimizdeki ölçüm (14:38)
   **10 dk 47 sn**. Yani `1:50 → 10:47` sıçraması **08-04 ile 08-08 arasında** oldu ve
   o pencerede kapı konteyneri kalmamış — **bisect edilemiyor**.
2. ⚠ 08-08 boyunca **kademeli** +2 dk daha eklendi. Gürültü değil: sıçramadan sonraki
   **hiçbir** koşum 12:29'un altına inmedi.

---

## 3 · 7,1× çarpanlarına ayrıldı

### ① Korpus BÜYÜDÜ — **×1,38**

Kapının kendi özet tablosundan:

| şirket | taban (08-04) | **bugün** | fark |
|---|---|---|---|
| boyahane | 5306 | **9413** | 🔴 **+%77** |
| atiksan | 1462 | 1447 | — *(aşağıya bak)* |
| gulteks | 1618 | 1618 | — |
| gitas | 2479 | 2479 | — |
| **toplam** | **10 865** | **14 957** | **+%38** |

✅ **`atiksan` 1462→1447 bir gerileme DEĞİL.** `CLAUDE.md` bunu zaten kaydetmiş ve A/B ile
doğrulamış (aynı kod + **eski** `features.yml` → yine 1447); fark FAZ 3.x kataloğundan
geliyor. *Bu belgenin ilk taslağında bunu bir alarm olarak yazmıştım; belgeyi okuyunca
geri aldım — güncel taban her zaman `lab/reports/nl_corpus.md`'dedir.*

⚠ **boyahane +%77 ise açıklanmamış.** Kapsam kazancı olabilir (yeni küp/ölçü → daha çok
üretilen soru), ama **hiçbir yerde ölçülmüş bir gerekçesi yok**.

### ② Soru başına maliyet ARTTI — **×3,8** ← *asıl sebep*

Kütükteki 400 isteğin **server'ın kendi ölçtüğü** `süre=` değerleri:

```
n=400    min=120 ms    medyan=177 ms    ortalama=252 ms    maks=563 ms
```

Belgelenmiş taban: **21,3 q/sn/süreç ⇒ 47 ms**.

🔴 **En hızlı istek bile 120 ms** — tabanın 2,5 katı. Bu bir kuyruk/tail sorunu değil;
**tabanın kendisi yükselmiş**.

⚠ Kıyas **muhafazakâr**: 47 ms *uçtan uca* bir bütçeydi (harness dahil), 177 ms ise
*yalnız handler içi*. Yani gerçek gerileme buradakinden **büyüktür**.

### ③ Çekirdek çekişmesi — **×1,4**

20 çekirdek, ama kapı başlamadan **yük ortalaması 8-9**:

- 🔴 **`dima-wren-engine` 3209 kez yeniden başlamış**, 44 saattir sonsuz JVM boot
  döngüsünde. Sebep: `java.io.FileNotFoundException: etc/config.properties`.
  `backend/` içinde bu konteynere **referans yok** — yetim, sadece çekirdek yakıyor.
- `supabase_*` (11 konteyner) + `upcyops_*` + `trendyol_backend` + `celery` ayakta.

> **1,38 × 3,8 × 1,4 = 7,3** ≈ gözlenen **7,1**. Hesap kapanıyor.

---

## 4 · MEKANİZMA — *neden* geriledik

### 4.1 · Sıcak yola beş günde 41 yeni modül girdi

Taban commit `eb48c40` (2026-08-04) ile bugün arasında **335 commit**. `app/` altına
eklenen yeni modüller ve bunlardan **`ask.py`'nin doğrudan import ettikleri**:

| modül | satır | modül | satır |
|---|---|---|---|
| `uyum.py` | 751 | `soz.py` | 170 |
| `yetenek.py` | 505 | `siralama.py` | 165 |
| `niyet.py` | 401 | `varlik.py` | 154 |
| `donem_capasi.py` | 281 | `belirsizlik_chipi.py` | 137 |
| `kiyas_cebiri.py` | 265 | `istek_kimligi.py` | 122 |
| `turetme.py` | 254 | `netlestirme.py` | 107 |
| `katalog_metni.py` | 225 | `butce.py` | 105 |
| `veri_araligi.py` | 199 | `islev_sozcukleri.py` | 71 |
| `niyet_tasima.py` | 176 | | |

**17 modül · ~3 700 satır**, hepsi `/ask`'in sıcak yolunda. Üstüne mevcut dosyaların
büyümesi:

| dosya | taban | bugün | artış |
|---|---|---|---|
| `routers/ask.py` | 4 070 | 5 382 | **1,3×** |
| `cube_router.py` | 3 601 | 4 571 | **1,3×** |
| `llm.py` | 1 212 | 1 551 | **1,3×** |

> Toplam: her istekte koşan **~6 000 satır yeni kod**. Hiçbiri tek başına pahalı değil.
> *Bir isteğin maliyeti, kimsenin tek başına pahalı bulmadığı kararların toplamıdır.*

### 4.2 · Sıcak yolda **HİÇ önbellek yok** — ve bu tabandan beri böyle

```
cube_router.py'de lru_cache/@cache sayısı:   taban = 0     bugün = 0
```

`route()` · `_match_cube()` · `partial_unknowns()` · `_norm()` — **hiçbirinde
memoizasyon yok**. Katalog istek içinde **defalarca baştan taranıyor**.

⚠ Bu tabanda da böyleydi; yani bir *gerileme* değil, bir **çarpan**. Yeni kod eklendikçe
maliyeti çarpan da büyüyor.

### 4.3 · `partial_unknowns` çağrı yerleri 4 → 7

`partial_unknowns()` **katalog-geneli** bir taramadır: `_match_cube()` çağırır, sonra
`schema["cubes"]` üzerinde **tam döngü** kurar. Önbelleklenmemiştir.

| dosya | taban | bugün |
|---|---|---|
| `cube_router.py` | 3 | **4** |
| `routers/ask.py` | 1 | 1 |
| `answer.py` | 0 | **1** ← yeni |
| `niyet.py` | 0 | **1** ← yeni |
| **toplam** | **4** | **7** |

⚠ `ask.py:3561`'deki çağrının yorumu *"tarama zaten aşağıda koşuyor, burada bir kez
koşup **yeniden kullanılıyor**"* diyor — ama kod `partial_unknowns()`'u **yeniden
çağırıyor**, saklanmış bir sonucu okumuyor. *Yorumun anlattığı iyileştirme kodda yok.*

### 4.4 · Vaka çalışması: **11 satır = +94 saniye**

Zaman serisindeki tek net sıçrama (17:11 → 17:52, **+94 sn**) penceresinde **tek bir
commit** var:

```
565f76b  feat(§90/mutfak demeti 1): M-6 operatör tek kaynak · M-2 varsayılan ölçü
         backend/app/cube_router.py  |  11 +++
```

`cube_router.py`'ye eklenen 11 satırın tamamı bu:

```python
from app import cube_operatorleri as _ops
if any(not _ops.gecerli(f.get("operator")) for f in filters):
    return None
```

Ama asıl maliyet o üç satırda değil — **aynı commit 8 küpe `default_measure` yazdı**
(canlı şemada **3 → 11**). Yani sekiz küp, önce **çekimser kaldığı** sorularda artık
**route hit üretiyor** ve tur **tam cevap yolunu** koşuyor.

🔴 **Bu bir kusur değil, ödenmemiş bir bedeldir.** Commit'in kendi gerekçesi kazancı
dürüstçe yazıyor: *"üçü de artık `route()` ile, LLM'siz"* — yani daha çok soru
cevaplanıyor, Discovery'ye daha az düşülüyor. **EN ÜST KURAL'ın istediği tam da budur.**
Sadece **latency tarafı hiç ölçülmedi**.

> *Bir yeteneği açmak onu bedava yapmaz; yalnız faturayı başka bir yere yazar.*

---

## 5 · Yan bulgular (hız dışı, ama bu ölçümde çıktı)

### 5.1 · 🔴 `--hepsi` kendi belgesiyle çelişiyor

`lab/kapi.py`'de `eval_llm` adımının docstring'i açıkça şunu diyor:

> *"Toplu koşuma girmez ve sebebi `garson` ile aynı: gerçek sağlayıcı + anahtar ister,
> `--hepsi` ise `--network none` ile koşar. Yeri **faz sonu**dur."*

Ama kod **yalnız `garson`'u** eliyor:

```python
adimlar = tuple(k for k, ad in zip(adimlar, ADIM_ANAHTARLARI, strict=True)
                if ad != GARSON_TOPLUDA_YOK)      # ← sadece 'garson'
```

Canlı kütükte **`▶ eval LLM dilimi` koşuyor**. Yani ağ + kota isteyen, **belirlenimsiz**
bir adım `--hepsi`'nin içinde: hem yavaşlatıyor, hem *"kapı yeşil"* cümlesini
belirlenimsiz bir ölçüme dayandırıyor.

*Bu, `kapi.py`'nin kendi `konusma_senaryolari` dersinin tekrarıdır: bir kapının bir
parçası, belgesinin söylediği şeyi yapmıyor.*

### 5.2 · Kütük hacmi

Tek kapı koşumu: **61 792 satır**, bunun **54 180'i `INFO`**. Her satır dört katmandan
geçiyor: `logging` biçimlendirme → `stdout` → docker `json-file` (JSON kodlama + disk) →
`_kos_yakala`'nın **satır satır Python okuması** ve **bellekte liste**. Korpus bu
satırların hiçbirini okumuyor.

### 5.3 · Dilim dengesi bayatladı

`lab/nl_corpus.py`:

```python
_AGIR = {"boyahane": 9, "gitas": 3, "gulteks": 2, "atiksan": 2}
```

Bu sabit **5306 turluk** boyahane'ye göre ayarlanmış ve yorumu *"en uzun dilimi ~60
sn'de tutar"* diye vaat ediyor. boyahane **9413**'e çıkınca dilim başına **589 → 1046
tur**. Üstelik aynı belge boyahane'nin soru başına **2,2× yavaş** olduğunu yazıyor ⇒ en
uzun dilim, en kısa dilimin **~2,8 katı** iş taşıyor. Ve **duvar saati = en uzun dilim**.

*Ölçülmüş bir sabit, ölçtüğü şey büyüyünce sessizce yanlışa döner.*

---

## 6 · ÇÖZÜM ÖNERİLERİ

🔴 **Sıralama ilkesi:** hiçbiri paydaya dokunmaz. `CLAUDE.md`'nin **SEYRELTME YASAK**
kuralı yürürlükte — *hız kapsamdan değil, çekirdekten ve önbellekten satın alınır.*

### Öneri 1 — Makine hijyeni · kazanç ~%30 · risk **SIFIR**

| iş | gerekçe |
|---|---|
| `dima-wren-engine` crash döngüsünü durdur | 3209 restart, 44 saat, `backend/`'de referansı yok |
| ölü kapı konteynerlerini temizle (26 adet) | disk + kütük |
| kapı koşarken **paralel iş yapma** | build/curl/canlı konteyner çekirdek yiyor |

⚠ **Bunlar paylaşılan bir makinede yapılır** — canlı geliştirici var. Yetim konteyner
silmeden önce sahibi teyit edilmeli.

### Öneri 2 — `_AGIR` dilim dağılımını yeniden ölç · kazanç ~%35 · risk **SIFIR**

Payda kırpılmaz; yalnız **iş yükü ölçülüp** dilim sayıları güncellenir. Öneri:
dilim sayısı **tur sayısına değil, ölçülen duvar-saatine** orantılansın ve **uzun dilim
önce** gönderilsin (`ProcessPoolExecutor` kuyruğu sonu düzleştirir).

⚠ Sabitin bayatlamaması için: dağılımı **`lab/reports/nl_corpus.json`'daki son ölçümden
türet**, elle yazma. *Elle yazılmış her sabit bir gelecekteki yanlıştır.*

### Öneri 3 — Korpusta kütük seviyesi `WARNING` · kazanç %5-15 · risk **SIFIR**

Korpus `INFO` satırlarını okumuyor. 54 180 satırın dört katmanlı maliyeti kaldırılır.
⚠ Kırmızı teşhisi için `--ayrintili` gibi bir geri-açma bayrağı bırakılmalı.

### Öneri 4 — 🔴 **`/ask` latency gerilemesini teşhis et** · kazanç ~%75 · risk **SIFIR**

Bu **en büyük kaldıraç** ve aynı zamanda **bir ürün sorunu** — kapı yavaş olduğu için
değil, **ürün yavaşladığı için** yavaş. Kullanıcı da bu gecikmeyi yaşıyor.

**Somut ilk adımlar (kapsam kaybı yok):**

1. **`lru_cache` ekle** — `_norm()`, `_match_cube()`, `partial_unknowns()`. Şema istek
   boyunca değişmez; katalog taraması istek başına 7 kez tekrarlanıyor.
   ⚠ `schema` bir `dict` — hashlenebilir bir anahtar (şema damgası) gerekir; **bu ayrı
   ve dikkatli bir iştir**, körlemesine `@lru_cache` konmaz.
2. **`ask.py:3561`'i gerçekten yeniden kullan** — yorumun zaten iddia ettiği şey.
3. **İstek başına bütçe kapısı** — modül büyüme tavanları gibi bir **latency tavanı**:
   *"medyan `/ask` > X ms ise kapı kırmızı."* Bu depo büyümeyi zaten tavanla
   sınırlıyor (`test_modul_buyume.py`); **süre için böyle bir tavan yok** ve tam da bu
   yüzden 47→177 ms kimseye görünmeden geçti.

🔴 **En kalıcı öneri budur:** yavaşlama görünmedi çünkü **ölçen bir kapı yoktu**.
*Ölçülmeyen bir boyut, sessizce gerileyen bir boyuttur.*

### Öneri 5 — `--hepsi`'den `eval_llm`'i çıkar · risk **SIFIR**

Kodu kendi belgesine uydurmak. `GARSON_TOPLUDA_YOK` tek elemanlı bir sabit yerine
**toplu koşuma girmeyen adımlar kümesi** olmalı.

### ⛔ Reddedilen öneri: *"korpusu küçültelim"*

`CLAUDE.md` bunu zaten ölçüp reddetmiş. Paydayı kırpmak, korpusun **tek gerçek
yakalamasını** (`gitas` düştü → payda 445→342 → doğruluk **YÜKSELDİ**) görünmez kılardı;
o sinyal tamamen payda **sabitliğine** dayanıyor. **Bu belge o kararı değiştirmiyor.**

---

## 7 · Bu ölçümün SINIRLARI — yazılı, gizli değil

⚠ *Sessiz kırpma yok* disiplini ölçüm aracının kendisine de uygulanır:

1. 🔴 **`1:50 → 10:47` sıçraması bisect EDİLEMEDİ.** 08-04 ile 08-08 14:38 arasında kapı
   konteyneri kalmamış. Yavaşlamanın **büyük kısmı** o pencerede oldu ve hangi
   commit'lerde olduğunu bu belge **söyleyemiyor**.
2. ⚠ **`565f76b` ↔ +94 sn ilişkisi korelasyondur, ispat değil.** 41 dakikalık bir
   pencerede tek commit olması güçlü bir işaret ve sonraki 12 koşumun hiçbiri eski
   seviyeye dönmedi — ama arka plan yükü de değişmiş olabilir.
3. 🔴 **`/ask`'in 177 ms'sinin NEREDE yandığı profillenmedi.** Kullanıcı kısıtı gereği
   hiçbir şey koşulmadı. §4'teki mekanizma **yapısal çıkarımdır** (çağrı sayısı,
   önbellek yokluğu, yeni kod hacmi) — **ölçülmüş bir profil değildir.**
   → **Sonraki adım:** `cProfile`'lı tek bir `/ask`, **boşta bir makinede** ya da canlı
   geliştirici yokken. O profil olmadan hangi modülün pahalı olduğu **bilinmiyor**.
4. ⚠ **boyahane +%77'nin gerekçesi bulunamadı.** Kapsam kazancı olabilir; doğrulanmadı.
5. ⚠ Koşan kapı (`dima-kapi-z`) **dalga 2 bitmeden** silindi; `--hepsi`'nin nihai
   özeti/sonucu bu belgede **yok**.

---

## 8 · Bir bakışta

| | |
|---|---|
| 🔴 **STATÜ** | **döngü kuralına dahil · ÖNCELİKLİ** — çözümü *kalan bütün maddeleri* hızlandırır |
| 🔴 **Günlük bedeli** | **~3 saat 32 dk** saf bekleme *(19 koşum × 11 dk 10 sn, ölçüldü)* |
| **Yavaşlama nerede** | yalnız **korpus adımı**: 1:50 → 13:00 (**7,1×**) |
| **Paralellik** | ✅ sağlam — 16 dilim / 16 süreç, geri alma bayrağı kapalı |
| **Payda** | ✅ kırpılmadı — tersine **%38 büyüdü** |
| **Asıl sebep** | 🔴 `/ask` **47 ms → 177 ms** (×3,8) |
| **Mekanizma** | 5 günde 335 commit · sıcak yolda **41 yeni modül** (17'si `ask.py`'de) · **sıfır** memoizasyon · `partial_unknowns` 4→7 çağrı |
| **En büyük kaldıraç** | `/ask` latency teşhisi + **bir latency tavanı kapısı** |
| **En ucuz kaldıraç** | makine hijyeni (wren crash döngüsü) + dilim dengesi |
| **Değişmeyen** | ⛔ korpus **küçültülmez** — SEYRELTME YASAK yürürlükte |

> *Kapı yavaşlamadı — ürün yavaşladı, kapı yalnız onu görünür kıldı. Ve bu görünürlük
> tesadüfen oldu: süreyi ölçen bir kapı olsaydı, 47 ms'den 177 ms'ye çıkarken
> öğrenirdik.*

---

# 9 · UYGULAMA RAPORU — *ne yapıldı, ne bilerek YAPILMADI*

> **Kullanıcı kararı (2026-08-09):** *"Sana yetki veriyorum, dikkatlice sorunları çöz —
> ama çok dikkatli ol, geliştirici çok yoğun çalışıyor."* + *"Geliştirici canlıda test
> de çalıştırıyor."*

## 9.1 · Çalışma kısıtları — ve nasıl karşılandı

| kısıt | nasıl karşılandı |
|---|---|
| geliştirici **canlı çalışıyor** (13 dk önce commit, `contribution.py` açıkken) | 🔴 **ana dizindeki tek bir `.py` dosyasına dokunulmadı** — tüm kod izole `git worktree`'de |
| geliştirici **canlıda test koşuyor** | ⛔ hiçbir kapı/süit/korpus koşulmadı |
| paylaşılan repo (hafıza kuralı) | `worktree add` yalnız **commit'lenmiş** durumu alır → açık işi yapısal olarak göremez; **iki yönlü doğrulandı** |

**İzole çalışma alanı:**

```
/home/cagataysntrk/İndirilenler/dima-kapi-hiz-worktree   dal: kapi-hizlandirma
sabitlendiği commit: 2d1fd3f          tek commit: c9a5a42
```

✅ Worktree kurulmadan önce ve sonra ana dizinin `git status`'ü **birebir aynıydı**.
⊙ Sonradan ana dizin değişti — ama **geliştiricinin kendi commit'iyle** (`d40be90`,
*§AA1*, 07:03). Benim değişikliğim değil.

## 9.2 · İnen üç kök

### ① `_AGIR` sabiti artık **yedek** — dağılım ÖLÇÜMDEN türetiliyor  *(§5.3'ün kökü)*

Sabitin bayatladığı görülmedi çünkü **rapor süre kaydetmiyordu** — doğruluğu ölçen araç
**kendi maliyetini** ölçmüyordu. Önce ölçüm eklendi, sonra dağılım ondan türetildi:

| ne | nerede |
|---|---|
| her dilim kendi `sure_sn`'ini yazar | `lab/nl_corpus.py::_calis` |
| iki ayrı süre taşınır: `sure_sn` (**toplam iş yükü**, dağılımı besler) · `sure_en_uzun_dilim_sn` (**duvar saati**, dengeyi gösterir) | `::birlestir` |
| dağılım ölçümden türetilir → yoksa tur×ağırlık → o da yoksa `_AGIR` yedeği | `::_dilim_dagilimi` |
| ağır dilim **önce** gönderilir (LPT çizelgeleme) | `::_is_listesi` |

🔴 **Ve kuru prova İLK TASARIMIMI ÇÜRÜTTÜ.** İlk yazımım payı iş yüküne *orantılı*
dağıtıyordu; gerçek korpus verisiyle koşturunca bugünkünden **%8 KÖTÜ** çıktı — orantısal
dağıtım boyahane'ye 13 dilim verip ötekilere 1'er bırakıyor ve o anda **gitas'ın tek
dilimi** en uzun dilim oluyordu.

> *Orantısal dağıtım ORTALAMAYI iyileştirir; duvar saatini EN UZUN dilim belirler.
> Yanlış büyüklüğü eniyileyen bir hızlandırma, bir yavaşlatmadır.*

Doğru hedef **makespan**, doğru araç **açgözlü bölme**:

```
bugün  {boyahane 9,  gitas 3, gulteks 2, atiksan 2}  → en uzun dilim 2301 birim
yeni   {boyahane 12, gitas 2, gulteks 1, atiksan 1}  → en uzun dilim 1726 birim   %25 ↓
```

⊙ **Çapraz doğrulama:** aynı açgözlü, **ağırlıksız** (yalnız tur sayısıyla) koşturulunca
bugünkü `_AGIR` sabitini **birebir yeniden üretiyor** — yani sabit zamanında doğru
yöntemle türetilmişti, sonra **veri altından kaydı**.

### ② `--hepsi` kendi belgesine uydu  *(§5.1'in kökü)*

`TOPLUDA_YOK = ("garson", "eval_llm")` — tek elemanlı bir **dize** yerine bir **küme**.
*Bir kuralı tek elemanlı bir dizeye yazmak, ikinci üyeyi eklemeyi unutturur.*
Ek olarak özetteki elle yazılmış *"dört adım"* (gerçekte **beş**) artık **sayılıyor**.

### ③ Korpus `INFO` yazmaz  *(§5.2'nin kökü)*

`configure_logging` artık `DIMA_LOG_LEVEL` okuyor; **varsayılan `INFO` KALDI** — bu depoda
log seviyesine bağlı dört test var (`test_ask_router_logging` · `test_llm_logging` ·
`test_sql_politikasi` · `test_kapanis_zinciri`) ve varsayılanı düşürmek onları *sessizce*
etkilerdi.

⚠ **Kendi riskimi yazarken yakaladım:** `setdefault`'u önce **modül seviyesine** koymuştum;
bu depoda testler `lab` modüllerini import ediyor, yani o dört testi etkileyebilirdi.
`main()` içine taşındı — yalnız betik olarak koşunca çalışır. *Bir hızlandırma, kendi
kapsamının dışına taşarsa hızlandırma değil risktir.*

### ④ Makine hijyeni  *(§3③'ün kökü)*

`b84deddc0a57_dima-wren-engine` **durduruldu** (silinmedi). Zararsızlığı önce kanıtlandı:

| kanıt | değer |
|---|---|
| port 8080 dinleniyor mu | ❌ **hayır** — konteyner boot edemiyor |
| restart sayısı / yaş | **3244** · 2026-07-30'dan beri |
| compose'un beklediği `dima-wren-engine` adı | ✅ **boşta** → bu konteyner compose'un tanıdığı nesne bile değil |
| `/health` onsuz | ✅ **HTTP 200** |

🔁 Geri alma: `docker start b84deddc0a57_dima-wren-engine`
🔁 Temiz kurulum: `docker compose up -d wren-engine`

⚠ **26 ölü kapı konteyneri BİLEREK SİLİNMEDİ** — bu belgedeki zaman serisinin
(§2) tek kanıt kaynağı onların kütükleri. *Ölçümün kanıtını silmek, ölçümü silmektir.*

## 9.3 · 🔴 Bilerek YAPILMAYANLAR — ve neden

| yapılmadı | gerekçe |
|---|---|
| **Öneri 4 — `lru_cache`** (`_norm` · `_match_cube` · `partial_unknowns`) | 🔴 **En büyük kaldıraç ve en büyük risk.** `schema` bir `dict`; hashlenebilir anahtar tasarımı ister ve yönlendirmenin **sıcak yolundadır**. Test koşamadan buraya dokunmak, hız için **doğruluğu** riske atmaktı |
| **`ask.py:3561` tekrar-kullanım** | aynı sınıf — sıcak yol, doğrulanamaz |
| `/ask` **profili** | boşta bir makine ister; canlı geliştirici var |
| 26 ölü konteynerin silinmesi | §2'nin kanıtı |

> *Yetki, doğrulayamadığım bir değişikliği yapma yetkisi değildir.*

## 9.4 · ⚠ Kapı yazıldı ama KOŞULMADI

`backend/tests/test_kapi_hizi.py` — **12 test**. Kapsadıkları: belirlenimsiz adım
sızıntısı · dilim sayısının süreçleri tam doldurması · **hiçbir şirketin düşmemesi
(payda)** · en uzun dilimin bayat sabitten kısa olması · üç bozuk rapor yolunda yedeğe
düşme · sürenin iki ayrı alanda taşınması.

🔴 **pytest altında koşulmadı** ve sebebi ölçüldü: host'ta `wren` modülü **yok**, süit
yalnız konteynerde koşuyor (denendi → `ModuleNotFoundError: No module named 'wren'`) ve
konteyner ayağa kaldırmak tam da kaçınılan şey.

**Bunun yerine mantık gerçek koddan izole doğrulandı** (`ast` ile fonksiyonlar çıkarılıp
sahte raporlarla çağrıldı):

| doğrulanan | sonuç |
|---|---|
| rapor yok / şirket hatalı / bozuk JSON | ✅ üçü de `_AGIR` yedeğine düşüyor, istisna yükseltmiyor |
| `sure_sn` yok, tur var (ilk koşum) | ✅ `{boyahane 12, gitas 2, gulteks 1, atiksan 1}` |
| gerçek ölçüm | ✅ aynı dağılım · toplam **tam 16 dilim** · en uzun **%25 kısa** |
| seri (`paralel=1`) | ✅ her şirkete 1 dilim |
| `birlestir` süre alanları | ✅ toplam 40,0 · en uzun 30,0 · **payda korundu** |
| `--hepsi` adım süzgeci | ✅ 5 adım; `garson`+`eval_llm` çıktı, `--sadece` ile hâlâ çağrılabiliyor |
| üç dosyanın sözdizimi | ✅ temiz |

**İlk gerçek pytest koşumu geliştiricinin kapısı olacaktır.** Bu, bu belgenin kendi
*"sessiz kırpma yok"* disiplini gereği burada yazılıdır.

## 9.5 · Devir — geliştiriciye

```bash
# 1 · gözden geçir (tek commit, 4 dosya)
git -C /home/cagataysntrk/İndirilenler/dima-kapi-hiz-worktree show c9a5a42

# 2 · kendi dalına al
git cherry-pick c9a5a42

# 3 · ilk koşum: dağılım satırını oku, sonra ölçüm devralır
python lab/kapi.py --tam        # "⚡ dilim dağılımı [YEDEK sabit `_AGIR` …]"
python lab/kapi.py --tam        # "⚡ dilim dağılımı [ÖLÇÜM …]"  ← %25 kısalma burada
```

⚠ **İki koşum gerekir.** İlk koşum `sure_sn`'i **yazar**, ikinci koşum onu **kullanır**.
Bu bir kusur değil, tasarım: *ölçmeden hızlanmayı reddediyoruz.*

## 9.6 · Beklenen sonuç — ve neyin hâlâ AÇIK olduğu

| kök | durum | beklenen |
|---|---|---|
| ③ çekirdek çekişmesi | ✅ indi | wren döngüsü durdu |
| §5.3 dilim dengesi | ✅ indi *(kapıda doğrulanacak)* | en uzun dilim **%25 ↓** |
| §5.2 günlük gürültüsü | ✅ indi *(kapıda doğrulanacak)* | %5-15 |
| §5.1 `eval_llm` sızıntısı | ✅ indi | dalga 2 kısalır + **kapı yeniden belirlenimli** |
| 🔴 ② `/ask` 47→177 ms | ⏸ **AÇIK** | **×3,8 — yavaşlamanın çoğu hâlâ burada** |
| 🔴 latency tavanı kapısı | ⏸ **AÇIK** | *ölçen kapı olmadan bu yeniden olur* |

> 🔴 **Bu commit korpusu ~13 dk'dan ~9-10 dk'ya indirmeyi hedefler; 1:50'ye DEĞİL.**
> Kalan mesafe `/ask`'in kendi gerilemesidir ve bu belgenin **Öneri 4**'üdür — ölçülmeden
> dokunulmayacak tek yer orasıdır.
