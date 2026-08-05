# TEST ORTAMI KILAVUZU — *ne var, nasıl çalışır, ne zaman koşar*

> **Kime:** bu depoda test koşacak / test yazacak herkese.
> **Ne değil:** bu bir denetim raporu değil; **kullanım kılavuzu** ve **kural seti**.
> **Kesit:** `@defb0e7` · 2026-08-05.
> **Kardeş belgeler:** `belgeler/denetim/2026-08-05_TEST-ORTAMI-RAPORU.md` (durum ölçümü) ·
> `belgeler/denetim/2026-08-05_TEST-ORTAMI-ARASTIRMA.md` (literatür) · `backend/CLAUDE.md` (kapı politikası).

---

## 0 · TEK CÜMLE

Bu ortam **iki farklı soruyu** ayrı aletlerle sorar — *"erişim var mı"* (ucuz, her
demette) ve *"cevap doğru mu"* (pahalı, örneklemli) — ve **hiçbir alet ötekinin yerine
geçmez.**

---

## 1 · 🔴 EN ÖNEMLİ KURAL: SÜRE

> Kullanıcı kararı: *"geliştirmede teste **max 1-2 dk** süre ayırabiliriz"* ve
> *"kapsam kaybetmeden güvenlice"*.

Bu iki cümle çelişkili görünür ama değil. **Hız kapsamdan değil, üç yerden satın
alınır** — ve üçü de bu ortamda kurulu:

| kaynak | nasıl | ölçülen kazanç |
|---|---|---|
| **çekirdek** | `route()` çağrıları 16 sürece dağıtılır (`lab/kosut.py`) | korpus **13:18 → 1:50**, sayılar **birebir aynı** |
| **tekrar** | deterministik üretim ve kapsam ölçümü önbelleklenir | soğuk → sıcak koşum farkı |
| **anlamsız kombinasyon** | etkileşmeyen eksenler çaprazlanmaz (dönem **sınıfı**) | pairwise ikilisi **11 070 → 945**, korpus **10 732 → 2 311** |

⚠ Korpusun küçülmesi bir **kırpma değil, doyma**: pairwise tüm ikilileri kapattığında
kendiliğinden durur. 82 dönem değeriyle 10,7 bin vakaya şişen şey, 7 dönem **sınıfıyla**
2,3 binde doyuyor — ve `dil_ozellikleri` kapısı 71 dilsel özelliğin hâlâ hepsinin
üretildiğini her koşumda sınıyor.

> ⚠ **Kapsamdan ödün verilen tek bir yer yok.** Payda **bölünür**, azaltılmaz.
> `dil_ozellikleri` kapısı 71 dilsel özelliğin **hepsinin** hâlâ üretildiğini her
> koşumda sınar — yani hız kazancı kapsamı düşürdüyse **test kırmızı verir**.

### 🔴 Neden bu kural bu kadar önemli

*Uzun bir kapı, atlanan bir kapıya dönüşür.* Bu depo bunu ölçtü: bir turda `--hizli`
**dört kez** koşuldu, `motor_cls` sorusu için **üç tam süit** (~7 dk) koşuldu ve
cevap tek satırlık bir **okuma** işiydi. Kapı pahalı olduğunda insan onu atlamaya
başlar; ve atlanan bir kapı, olmayan bir kapıdan **daha kötüdür** — çünkü varlığı
güvence sanılır.

---

## 2 · NE ZAMAN NE KOŞULUR — üç seviye, başka seviye YOK

| # | ne zaman | komut | süre |
|---|---|---|---|
| **1** | 🟢 **bir dosya düzenledikten sonra** | `pytest tests/test_<o_dosya>.py` | **3-15 sn** |
| **1b** | 🟢 **ortam kapılarının tamamı** | `pytest tests/test_gercek_dunya_korpusu.py tests/test_metamorfik.py tests/test_konusma_uretec.py tests/test_ekili_olaylar.py tests/test_kosut_deseni.py tests/test_ortam_butunlugu.py tests/test_belge_duzeni.py -q` | 🟢 **7 sn soğuk · 6 sn sıcak** *(ölçüldü)* |
| **2** | 🟡 **demet sonunda, BİR KEZ** | `python lab/kapi.py --tam` | **~2 dk 10 sn** |
| **3** | 🔴 **gecelik CI** *(insan beklemez)* | `python lab/kapi.py --hepsi` | **~4-5 dk** |

> 🟢 **Seviye 1b, kullanıcının 1-2 dakikalık bütçesinin çok altında** — yedi kapı
> dosyası, 94 test, **7 saniye**. Soğuk/sıcak farkı **1 saniye**: önbellek kurulumu
> artık ölçülebilir bir maliyet değil.

🔴 **Seviye 3 YEREL OLARAK KOŞULMAZ.** Ne demet sonunda, ne commit öncesi, ne
*"bir de şuna bakayım"* diye.

### Dört pekiştirici kural (`backend/CLAUDE.md`'den)

| kural | ne der |
|---|---|
| **K1** | *Bir tasarım gerçeği **koşularak** değil **okunarak** bulunur.* Süit *"kod ne yapıyor"* sorusunun cevabı değildir; *"değişiklik bir şeyi bozdu mu"* sorusunun cevabıdır. |
| **K2** | Düzelt-koş döngüsünde **yalnız hedef dosya** koşulur (3-15 sn). Geniş seçim commit'ten önce **bir kez**. |
| **K3** | Merkezî dosyalarda (`ask.py`·`cube_router.py`·`wren_service.py`·`ReportCard.tsx`) hızlı seçim kapının kendisinden pahalı → **doğrudan `--tam`**. |
| **K4** | **Demet başına bir korpus.** |

### 🔴 Değişmeyen üç koşum kuralı

1. **Kapı koşarken repoya YAZILMAZ** — mount canlıdır, ölçüm karışır.
2. **Koşum hijyeni:** `--rm` değil **`-d`**, `--name` ver, `docker wait` + `docker logs`
   ile oku, sonda `docker rm -f`. *(`--rm` konteyner çıkınca kütüğü siler; bu operasyonda
   iki koşumun özeti böyle kayboldu.)*
3. **Canlı-LLM koşumları yerel kapıda ASLA** — kota sınırı ölçülü: **10 istek / 10 sn**.

---

## 3 · ORTAMIN PARÇALARI — *hangisi neyi ölçer*

```
                          ┌─ KAPI (her demette, ucuz) ─────────────────┐
  soru üretimi            │  nl_corpus      → kataloğun sözlüğü        │
  ├── nl_corpus.py        │  gercek_dunya   → KULLANICININ sözlüğü     │
  ├── senaryo_uretec.py   └────────────────────────────────────────────┘
  └── konusma_uretec.py   ┌─ TEŞHİS (örneklemli, gecelik) ─────────────┐
                          │  metamorfik     → tutarlılık               │
  ölçüm araçları          │  konusma_uretec → çok turlu bağlam         │
  ├── dil_ozellikleri.py  │  deneyim.py     → CANLI LLM turları        │
  ├── metamorfik.py       └────────────────────────────────────────────┘
  └── kosut.py  (koşut altyapı — üçünün ortak sahibi)
```

### 3.1 · `lab/senaryo_uretec.py` — **soru üreteci**

Elle vaka yazımı burada bitti. Kataloğa bağlı, **pairwise covering array**.

| eksen | değer | not |
|---|---|---|
| `olcu` | ~135 | kataloğun **kendi** ölçü sinonimlerinden (kullanıcı dili tercih edilir) |
| `niyet` | 17 | değer·kırılım·üstünlük·kıyas·trend·katkı·neden·eşik·karar·tahmin·yetenek·gürültü·**etki**·**kompozisyon**·**olumsuz**·**çoklu soru**·**çok kırılım** |
| `kayit` | 6 | resmî · konuşma · kısaltma · **yazım hatası** · eksiltili · **saha argosu** |
| `donem_sinifi` | 7 | yok · göreli · ay yalın · **ay çekimli** · çeyrek · yıl · aralık |

📊 **Üretilen korpus: 2 311 vaka** *(kapı bunun tamamını kullanır; `KAPI_ORNEK=2500`
üst sınırı katalog büyüdüğünde devreye girecek bir emniyet valfidir)*.

⚠ **Dönem ekseni neden SINIF:** *"`şubata` çekimi tanınıyor mu"* sorusu hangi ölçüyle
sorulduğuna **bağlı değildir** — dönem çözümlemesi ölçü eşleştirmesinden **ayrı bir
mekanizmadır**. 135 ölçünün her biriyle 60 ay çekimini denemek, aynı mekanizmayı 8 100
kez sınamaktı. Somut biçimler sınıf içinden **döngüsel** seçilir, yani 60 çekimin
**hepsi** yine üretilir.
| `dolgu` | 4 | yok · önek (`yani`,`peki`) · **emir kipi** (`ölç`) · ikisi |
| `bicim` | 5 | düz · boşluk hatası · büyük harf · noktalama · sayı biçimi |

**Neden tam çarpım değil:** NIST'in hata-etkileşim bulgusu — kusurların çoğu **en çok
iki** parametrenin etkileşiminden doğar. Her **ikiliyi** kapsayan dizi, tam çarpımın
kapsamını pratikte yakalar ama boyu `O(v²)`.

🔴 **Beklenen davranış KURALDAN türetilir**, elle etiketlenmez:

| koşul | beklenen |
|---|---|
| ölçü adı ≥2 cube'un sinonimi | `netlestirme` — belirsizlik **deterministik olarak biliniyor** |
| niyet = karar/tahmin/etki | `durust_ret` — v1'de bu yetenekler **YOK** (beyan edilmiş sınır) |
| gürültü / kapsam dışı | `durust_ret` |
| tek sahipli ölçü + dönem | `dogru` |

*Elle etiketlenen bir beklenti yazarın o günkü kanaatidir; kuraldan türetilen beklenti
kataloğun kendi gerçeğidir ve katalog değişince **kendiliğinden** güncellenir.*

### 3.2 · `lab/dil_ozellikleri.py` — **"ne eksik" ölçüsü**

71 dilsel özellik / 8 aile, her birine **dedektör**. Kapsanmayan özellik = test
ortamının deliği.

| aile | özellik | küme |
|---|---|---|
| ad çekimi | 7 | 🔒 **kapalı** — Türkçede altı durum, hepsi burada |
| iyelik | 6 | 🔒 kapalı |
| fiil | 10 | 🔒 kapalı |
| dönem | 9 | 🔒 kapalı |
| söylem | 7 | ⚠ açık |
| semantik | 20 | ⚠ açık |
| yazım | 8 | ⚠ açık |
| jargon | 4 | ⚠ açık |

> 🔴 **Kapalı kümenin değeri:** Türkçenin durum/iyelik/kip ekleri **sonludur**. Yani bu
> ailelerde *"acaba unuttuğum bir biçim var mı"* sorusu **kapanmıştır**. Açık aileler
> kapanmaz ve dosya bunu **saklamaz** (`ACIK_AILELER`).
> *Bir taksonominin dürüstlüğü, neyi kapsamadığını söylemesindedir.*

**İlk koşumda 10 delik buldu** ve onunun da onu kapatıldı: yalın ay adı · olumsuzluk ·
çoklu soru · iki kırılım · sayısal aralık · boşluk hatası · büyük harf · noktalama ·
sayı biçimi · yalın hâl.

⚠ *"Yalın ay"* deliği **kendi düzeltmemden** doğmuştu: çekimli hâlleri eklerken yalını
düşürmüşüm. **Bir eksiği kapatırken komşusunu açmak, ancak kapsam ölçülürse görülür.**

### 3.3 · `lab/metamorfik.py` — **altın cevap gerektirmeyen ölçü**

Anlamı koruyan dönüşüm uygulanır; beklenen sonuç **cevabın değişmemesidir**.

| aile | bağıntı | beklenti |
|---|---|---|
| **yüzey** (7) | Türkçe Q klavye komşusu · harf takası/düşmesi · büyük-küçük · boşluk · noktalama · aksan | **aynı** |
| **dilsel** (5) | eşdeğer ikame · öge sırası · nezaket · dolgu · söz edimi | **aynı** |
| 🔴 **zıt** (3) | olumsuzlama · dönem değişimi · kırılım ekleme | **FARKLI** |

> 🔴 **Zıt aile olmadan ölçüm bir totolojidir:** her soruya `durust_ret` diyen bir ürün
> tüm *"aynı kalmalı"* bağıntılarını **%100** geçer. *Bir tutarlılık ölçüsü, sabit bir
> cevabı mükemmel sanır.*

**⊘ ÜÇÜNCÜ HÂL:** taban zaten `PES` ise bir *"değişmeli"* bağıntısının arayacağı fark
yoktur → **ÖLÇÜLEMEDİ**, kusur sayılmaz, paydadan çıkar. *(İlk koşum `z.olumsuz`
51/51 kusur vermişti; şüpheli bütünlüğün sebebi buydu.)*

### 3.4 · `lab/konusma_uretec.py` — **çok turlu sohbet**

17 tur türü × 8 tur = **~7 milyar** dizi. Tekli soruda çözüm pairwise idi; dizide
karşılığı **geçiş kapsamı**: her ardışık tur çifti en az bir sohbette görünür.

📊 **Ölçüldü:** **169 sohbet · 810 tur · 289/289 geçiş (%100) · 2 saniye.**
Yani yedi milyarlık uzay, iki saniyede ve yüz altmış dokuz sohbetle **kanıtlı** biçimde
kapsanıyor.

**Tur türleri:** açılış · daraltma · genişletme · kırılım ekle · ölçü ekle · dönem değiş ·
atıf · neden · normal mi · ne yapmalı · anlat · konu değiş · geri dönüş · sosyal ·
öz-düzeltme · belirsiz · **iç içe**.

⚠ **Derinlik ayrı eksen** (2·3·5·8): *"beşinci turda bağlam hâlâ duruyor mu"* sorusu
iki turlu bir sohbette sorulamaz.

**Altı sohbet-metamorfik bağıntı** (altın cevap gerektirmez):

| bağıntı | beklenen | neyi yakalar |
|---|---|---|
| bağlam sürer | aynı | bağlam kaybı |
| sosyal tur bozmaz | aynı | *"teşekkürler"* raporu düşürüyor mu |
| 🔴 konu değişince DEĞİŞİR | **farklı** | bağlamın yapışması |
| geri dönüşte geri gelir | aynı | dallanma kaybı |
| 🔴 **sıra önemli** (A→B ≠ B→A) | **farklı** | sıra körlüğü |
| idempotens | aynı | kararsızlık |

### 3.5 · `demo/olaylar.py` — **ground truth bir sorgu**

6 **kasıtlı ve kayıtlı** ekilmiş olay. Ground truth *ekilen olayın kendisidir*; elle
altın cevap yazılmaz — *elle yazılmış bir altın cevap, verinin değiştiği gün sessizce
yalan olur.*

| olay | kök neden (doğru cevap) |
|---|---|
| `M07-KADEMELI-BOZULMA` | RAM-2'de kalibrasyon kayması |
| `TEDARIKCI-KALITE-DUSUSU` | T001 hammadde kalitesi |
| `ENERJI-FIYAT-SOKU` | fiyat şoku (**hacim değişmez** → PVM ayrıştırılabilir) |
| `MUSTERI-KAYBI-M1003` | müşteri kaybı |
| `GECE-VARDIYASI-DEVIR` | vardiya personel devri |
| `BUTCE-SAPMASI-ENERJI` | enerji kalemi bütçe aşımı |

Her olay taşır: **belirti** (kullanıcı neyi fark eder) · **kok_neden** (doğru cevap) ·
**dogrulama_sql** (cevabın veride kanıtı) · **sorular** · **zincir** (çok turlu
senaryoda hangi turda ortaya çıkmalı).

⚠ **Büyüklük eşiği ≥2,0×:** InsightBench eğimi 0,1 altındaki trendlerin hiçbir modelce
yakalanamadığını ölçmüş. Küçük ekilen bir olay *"sistem bulamadı"* değil **"ölçüm
kurulamadı"** demektir — ve bu ikisini karıştırmak ürünü kendi kusuru olmayan bir şey
için suçlar.

### 3.6 · `lab/kosut.py` — **koşut altyapı, tek sahipli**

`route()` çağrılarını çekirdeklere dağıtır. Üç yere ayrı ayrı yazılsaydı *"aynı kuralın
iki sahibi"* sınıfı üçe katlanırdı.

- `spawn`, **`fork` DEĞİL** — `fork` ile dilimler `conftest`'in SQLite'ını paylaşıp
  çöküyordu (ölçüldü: payda 445→255).
- Geri alma **tek env** ve korpusla **aynı**: `DIMA_KORPUS_PARALEL=1` → seri.
- Dilim sayısı `n*2` — **ölçülerek** seçildi (`n*4` → 1:12, `n*1` → 1:08).

---

## 4 · SEED — *ne var ve neden böyle*

| | |
|---|---|
| tablo | **80** (47 taban + 33 genişletme) |
| sütun | **745** *(Spider 2.0'ın kurumsal ortalaması ~800)* |
| satır | ~460 000 |
| dönem | türetilmiş tablolar 2024-01→2026-06 · bağımsızlar **2022-01→2026-08** |
| cube | **23** · ölçü **135** |

🔴 **Tasarım kuralı: TÜRETİLİR, UYDURULMAZ.**

| yeni tablo | neyden türetilir |
|---|---|
| `musteri_sikayetleri` | `partiler.uretim_dE > musteri_tolerans_dE` |
| `satis_siparisleri` | `partiler.siparis_no` |
| `urun_maliyetleri` | `partiler`in gerçek enerji/kimyasal tüketimi |
| `bakim_is_emirleri` | `ariza_kayitlari` |
| `sevkiyat_emirleri` | `irsaliyeler` |

*Rastgele üretilmiş bir şikâyet tablosu kök-neden sorusunu **cevaplanamaz** yapar:
sistem doğru cevabı bulsa bile veri onu doğrulamaz.*

⚠ **Genişletme mevcut 47 tabloya DOKUNMAZ** — `nl_corpus`'un %93,1 paydası korunur,
yoksa *"genişleme mi gerileme mi"* ayırt edilemezdi. Bir kapı bunu sınıyor
(`test_GENISLETME_yalniz_EKLER`).

---

## 5 · KAPILAR — *ne kırmızı verir*

📊 **Ölçüldü: 94 test geçiyor, 7 atlanıyor, 0 kalıyor — 7 saniyede.**

| dosya | neyi korur |
|---|---|
| `test_gercek_dunya_korpusu.py` | kopya yok · **71 dilsel özelliğin hepsi üretiliyor** · zayıf (<5) yok · kapalı aileler tam · canlı iki kusur sınıfı üretilir |
| `test_metamorfik.py` | zıt aile var · dilsel aile var · Türkçe klavye · imza doğru · **⊘ üçüncü hâl** |
| `test_konusma_uretec.py` | geçiş kapsamı tam · derinlik · negatif bağıntı · iç içe istek |
| `test_ekili_olaylar.py` | büyüklük eşiği · çakışma yok · SQL kanıtı · zincir senaryosu |
| `test_ortam_butunlugu.py` | **yetim cube** · **payda** · **kaynak yanlılığı** · taban commit'lenebilir · **kapı dekor değil** |
| `test_kosut_deseni.py` | koşut desen uygulanmış · muafiyetler gerekçeli · spawn |
| `test_belge_duzeni.py` | kök üç dosyalık · denetim adları tarih damgalı · her belge git'te · indeks bağları sağlam |

⚠ **7 atlama beklenen davranıştır, kusur değil:** `test_belge_duzeni.py` **repo kökünü**
denetliyor ama test konteynerine yalnız `backend/` bağlanıyor ve imajda `git` yok.
Atlamalar **sessiz değil** — her biri neden ölçülemediğini ve nerede koşulması
gerektiğini yazıyor (bkz. §7).

### 🔴 İki "dekor" tuzağı — ikisi de kapılı

1. **Kırmızı veremeyen kapı.** `konusma_senaryolari` bayraksız koşumda her yolda `0`
   dönüyordu; *"dört bileşenli bir kapının dörtte biri sessizce dekordu"*.
   → `test_KAPI_kirmizi_VEREBILIR_dekor_degil` bunu **çağırarak** kanıtlar.
2. **Kendi tabanıyla kıyaslanan kapı.** Taban dosyası commit edilmezse her koşum onu
   yeniden yazar ve kapı hiçbir zaman kırmızı veremez.
   → taban yazıldığında büyük harfle **COMMIT ET** uyarısı basılır, iki test sınar.

---

## 6 · YENİ BİR TESTER İÇİN — *ilk gün*

```bash
# 0 · ortam
cd /home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic
# (backend Docker'da koşar; belgeler/kilavuz/SERVER_COMMANDS.md'ye bak — port 8001, frontend pnpm)

# 1 · bir dosyayı düzenledin → YALNIZ onun testi   (3-15 sn)
docker run -d --name t1 --user "$(id -u):$(id -g)" --network none \
  -v "$PWD/backend:/app" -w /app -e DIMA_VQR_EMBEDDER=off dima-test \
  python -m pytest tests/test_<dosya>.py -q -p no:warnings
docker wait t1 && docker logs t1 && docker rm -f t1

# 1b · ortam kapılarının TAMAMI                     (ölçüldü: 7 sn soğuk)
... python -m pytest tests/test_gercek_dunya_korpusu.py tests/test_metamorfik.py \
      tests/test_konusma_uretec.py tests/test_ekili_olaylar.py \
      tests/test_kosut_deseni.py tests/test_ortam_butunlugu.py \
      tests/test_belge_duzeni.py -q -p no:warnings

# 2 · demet bitti → KAPI, bir kez                   (~2 dk 10 sn)
#     İKİ korpus koşar: nl_corpus (kataloğun sözlüğü) + gercek_dunya (kullanıcının)
... python lab/kapi.py --tam

# 3 · gecelik CI (yerelde KOŞMA)                    (~4-5 dk)
... python lab/kapi.py --hepsi

# ⚠ Belge düzeni denetimi REPO KÖKÜNDEN koşulur (konteynerde ⊘ atlanır):
cd backend && python -m pytest tests/test_belge_duzeni.py -q
```

### Yeni bir test yazacaksan

| soru | cevap |
|---|---|
| Ürünün **davranışını** mı sınıyorsun? | `lab/` altına koşucu yaz, `lab/kosut.degerlendir()` kullan |
| Ortamın **kendi bütünlüğünü** mü? | `tests/test_ortam_butunlugu.py`'ye ekle |
| Döngüde `route()` çağıracak mısın? | 🔴 **`lab.kosut` zorunlu** — yoksa `test_kosut_deseni` kırmızı verir |
| Canlı LLM mi çağıracak? | `_MUAF`'a **gerekçesiyle** ekle; yerel kapıya **koyma** |
| Yeni bir dilsel sınıf mı ölçüyorsun? | `dil_ozellikleri.OZELLIKLER`'e **dedektörüyle** ekle |

⚠ **Muafiyet gerekçesiz yazılırsa**, listeye girmek paralelleştirmekten kolay olur ve
**liste kuralın kendisini yer.**

---

## 7 · ORTAMIN BİLİNEN SINIRLARI — *saklanmıyor*

| sınır | ne demek |
|---|---|
| Ölçülen katman **`route()`** — sıfır-LLM | `durust_ret` *"deterministik yol pes etti"* demektir, *"kullanıcı cevapsız kaldı"* **değil**; `/ask` orada durmaz |
| `netlestirme` sınıfı **üretilemiyor** | `route()` düzeyinde netleştirme ile dürüst ret **ayırt edilemez** — tablodaki `0` bir ürün ölçümü değil, **aracın sınırı** |
| Sohbet bağıntıları **koşulmuyor** | üreteç ve bağıntılar kurulu; ürüne karşı koşum takip yolunu (`/ask` + bağlam) gerektirir |
| *"Cevap doğru mu"* ölçülmüyor | onu ancak LLM yolu ölçer: **10 istek/10 sn** kota → örneklemli, gecelik |
| `lab/reports/` **gitignore'da** | rapor yerel; **taban** commit'lenir (`lab/gercek_dunya_baseline.json`) |
| `test_belge_duzeni.py` **konteynerde ölçemez** | repo kökü + `git` ister; standart konteynerde **⊘ atlanır**, sebebiyle. Repo kökünden koşulmalı |

> *Bir ölçüm aracının değeri, ölçtüğü şey kadar **ölçmediğini söylemesindedir**.*

---

## 8 · ÖLÇÜLEN SÜRELER

> 📷 **2026-08-05 · `@6760241` · 20 çekirdek.** *Bir belgeye yazılmış sayı, yazıldığı
> anın fotoğrafıdır* — yeniden ölçmeden taban diye okuma.

| # | ne | süre | hedef | sonuç |
|---|---|---|---|---|
| **A** | 7 kapı dosyası, hepsi bir arada, **SOĞUK** | 🟢 **7 sn** | ≤30 | 94 geçti · 7 atlandı · **0 kaldı** |
| **B** | aynısı **SICAK** | 🟢 **6 sn** | ≤15 | aynı |
| **C** | `lab/gercek_dunya.py --kapi` | 🟢 **20 sn** | ≤40 | kapı yeşil · **2 311 vaka** |
| **D** | `lab/metamorfik.py --ornek 300` | 🟢 **32 sn** | ≤40 | 342 soru · 3 823 türev · %98,0 |
| **E** | `lab/konusma_uretec.py` | 🟢 **2 sn** | ≤15 | 169 sohbet · 810 tur · 289/289 |
| | **TOPLAM** | 🟢 **67 sn** | | zaman aşımı **yok** |

**Kıyas için:** `nl_corpus --kapi` **1 dk 50 sn** (16 süreç; seri hâli 13 dk 18 sn idi).
`--tam` ikisini birlikte koşar → **~2 dk 10 sn**.

### Soğuk/sıcak farkı: **1 saniye**

Önbellek artık ölçülebilir bir maliyet değil. ⚠ Bu **her zaman böyle değildi**:
önbellek `lab/reports/` altındayken (o dizin `.gitignore`'da) her yeni makinede ve her
CI koşumunda **soğuk** başlıyordu. *Her koşumda silinen bir önbellek, önbellek değildir.*

### 🔴 Ve bir sayı: **180 saniyenin 174'ü tek bir bozuk testteydi**

İlk doğrulama koşumu 180 saniyede **zaman aşımına uğradı**. Düzeltme sonrası aynı küme
**7 saniye**. Aradaki fark bir optimizasyon değil, **bir kusurun kaldırılmasıydı** —
ayrıntısı §9'da.

---

## 9 · 🔴 KAPILARIN KENDİSİ DE DENETLENİR

Bu turda **üç kusur** bulundu. Üçü de **ölçüm aracının kendisindeydi** — ürün kodunda
değil. Ve üçü de sessizdi: koşulsa bile ya hiç bitmiyor ya da yanlış sonuç veriyordu.

| kusur | nerede | belirti | sınıf |
|---|---|---|---|
| **sonsuz döngü** | `gecis_kapsami()` | 6+ dk tek çekirdekte asılı | ilerleme garantisi yok |
| **determinizm kaybı** | `pairwise()` | *(sessiz)* — aynı tohum, farklı korpus | küme sırasına dayanan karar |
| **felaket geri-izleme** | `test_kosut_deseni.py` | test **hiç bitmiyor** | iç içe niceleyici |

> 🔴 Sonuncusunun acı yanı: *"yavaş test kalmasın"* diye yazdığım kapı, ortamın **en
> yavaş şeyi** oldu. **Bir kuralı uygulayan aracın, o kurala uyması gerekir.**

### Üç denetim sorusu — yeni bir araç yazarken

| # | soru | neden |
|---|---|---|
| **1** | Her `while` döngüsünün ilerlemesi **inşa gereği** garanti mi? | *Rastgele arama, aradığına ulaşacağını garanti etmez; yalnız ulaşabileceğini gösterir.* Bir kapsam algoritması ihtimalle değil, inşayla ilerlemeli — ve bir **üst sınırı** olmalı. |
| **2** | Hiçbir karar **küme sırasına** dayanmıyor mu? | `next(iter(küme))` Python'un karma tohumuna bağlıdır (`PYTHONHASHSEED` rastgele). Sabit RNG tohumuna rağmen sonuç her süreçte değişir → önbellek anahtarı yalan söyler, *"dün geçti bugün kaldı"* teşhis edilemez. **`sorted()` kullan.** |
| **3** | Hiçbir regex'te **iç içe niceleyici** var mı? | `(\s+.*){0,12}?` gibi desenler üstel patlar. Metin taraması gerekiyorsa **satır tabanlı** yaz: O(n), geri-izleme yok. |

### Ve bir dördüncüsü — koşum hijyeni

Yavaşlığın **ilk** sebebi hiçbir koda ait değildi: **dört pytest konteyneri aynı anda**
koşuyordu, ikisi 52 ve 58 dakikadır asılı kalmış öksüzlerdi.

```bash
# 🔴 DOĞRU: -d + --name + docker wait + docker rm -f
docker run -d --name t1 --user "$(id -u):$(id -g)" --network none \
  -v "$PWD:/app" -w /app -e DIMA_VQR_EMBEDDER=off dima-test <komut>
docker wait t1 && docker logs t1 && docker rm -f t1
```

⚠ `--rm` **kullanma**: konteyner çıkınca kütüğü siler ve bu operasyonda **iki koşumun
özeti böyle kayboldu**. Ve **iki ajanı aynı repo üzerinde** koşturma — biri önbelleği
silerken öteki onu kullanır.
