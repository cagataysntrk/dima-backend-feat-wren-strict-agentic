# MUTFAK DENETİMİ — aşçının sınırları, kökleri ve 50 zincir senaryosu

**Tarih:** 2026-08-08 · **Tür:** denetim / araştırma raporu · **Yazan:** araştırmacı-denetçi ajan
**Kapsam:** yalnız **EKSEN 2 — MUTFAK** (küpler, semantik katman, `CubeQuery` derleyicisi).
Sipariş alma (garson/`route()` dili) bu belgenin konusu **değildir**.

---

## 0 · BU BELGENİN YERİ — önce bu okunmalı

> 🔴 **ASIL TEST BELGEMİZ `belgeler/denetim/2026-08-07_CEVIRI-SOZLESMESI.md`'DİR.**
> Bu belge onun **yerine geçmez**, ona **ek bir yan belgedir**.
>
> * Test ve döngü kurallarımız **ana belgedeki gibi aynen devam etmektedir**
>   (≥20 özgün senaryo → curl ile tek tek → tüm teşhisler → tüm düzeltmeler → **bir**
>   tazeleme → **bir** curl → **bir** kapı).
> * Koşum runbook'u, kimlik, okunacak altı alan, log kuralı: **ana belge §15**.
> * Bu belge yalnızca **testleri daha iyi yapmak ve geliştirmeyi daha doğru
>   yönlendirmek** için yazılmıştır. Bir **ilham kaynağıdır**; işlevi, dağınık kusurları
>   tek bir eksende toplayıp **odaklanmayı** sağlamaktır.
>
> Bir çelişki çıkarsa **ana belge geçerlidir.**

### 0.1 · Neden ayrı bir belge

`feedback_garson_devri_kurali`'nin teşhis kuralı şudur:

> *"Garson devreye girdi ve sisteme sorunsuz, doğru bir girdi sağladı — ama yine
> çalışmadıysa: sorun küplerde, mutfaktadır."*

Son turlarda garson ekseninde ciddi yol alındı. Bu belge, **o kuralın sağ tarafını**
ölçüyor: *garson doğru sipariş getirdiğinde aşçı yemeği çıkarabiliyor mu, ve
çıkaramıyorsa neden?*

---

## 1 · YÖNTEM VE KANIT KAYNAKLARI

| # | kaynak | ne | neden güvenilir |
|---|---|---|---|
| K1 | `backend/lab/reports/nl_corpus.md` (2026-08-08 13:44) | **14 726 tur**, 4 şirket, `rule` sağlayıcı | LLM **yok** → *deterministik tavanı* ölçer, yani **mutfağın kendi kapasitesini** |
| K2 | `dima-backend-core:/app/logs/dima.db` → `interaction_log` | **769 canlı tur**, 2026-08-01 → 2026-08-08 | Gerçek curl turlarımızın kütüğü — *"önceki testlerin bulguları"* burada duruyor |
| K3 | `backend/demo/packs/**/cubes/*/metadata.yml` | **28 küp** menü kaynağı | 🔴 `demo/wren-project` **okunmadı** — `project_olcum_araci_bayat_sema`: o bir gitignore'lu **derleme artefaktıdır** |
| K4 | `app/cube_router.py` · `intent_semasi.py` · `wren_service.py` · `niyet.py` · `uyum.py` · `yetenek.py` | kod okuması | sınırların **ilan edildiği** yerler |
| K5 | canlı konteynerde doğrudan fonksiyon çağrısı | tek kusurun **tekrar üretimi** | iddia değil, **koşum** |

### 1.1 · Kanıt etiketleri — bu belgede her iddia etiketlidir

* ✅ **ÖLÇÜLDÜ** — sayı bir koşumdan/kütükten geliyor, tekrar üretilebilir.
* 🔍 **KOD OKUMASI** — kaynakta doğrulandı, ama **canlıda tetiklenmedi**.
* ⚠ **ÇIKARIM** — iki ölçümden türetildi; senaryolarla sınanmalı.

> ⚠ **Bu raporun kendi sınırı:** canlı `:8001` örneğinde tek geçerli kiracı
> `demo-boyahane` ve `demo-geri-donusum`'dur (`app_user` tablosu; `gitas`/`gulteks`/
> `atiksan` **korpus-içi** şirketlerdir, giriş hesapları yoktur). Bu yüzden aşağıdaki 50
> senaryo `demo-boyahane` üzerinde yazıldı; şirkete özel olanlar ayrıca işaretlendi.

---

## 2 · YÖNETİCİ ÖZETİ — on cümle

1. Mutfak **sayı ürettiğinde doğrudur**: 223 canlı `source=cube` turunun yalnız 3'ü boş
   satır döndü, ortalama **1,66 sn**. Sorun kalitede değil, **kapsamda**. ✅
2. Canlı 769 turun **%37,3'ü hiçbir kaynaktan cevap üretmedi** (`source=NULL`) ve bu
   turlar ortalama **11,1 saniye** sürdü. Sistemin en pahalı yolu, **hiçbir şey
   söylemeyen** yoludur. ✅
3. `route()`'un tüm pes etme gerekçelerinin **%80,7'si tek bir koddur: `R10`**
   (tanınmayan kelime). Ve `R10`'dan sonra turların **%50,3'ü cevapsız kalır**. ✅
4. Korpusta (LLM'siz, 14 726 tur) mutfak turların **%69,6'sını** cevaplıyor; **%27,5'i
   netleştirmeye**, **%2,5'i** *"anlayamadım"*a düşüyor. ✅
5. 🔴 **Baskın kök dil değil, MENÜDÜR:** 28 küpün sinonim sözlüklerinde **152 kelime
   birden çok küpte** geçiyor. `müşteri` **11** küpte, `tezgah` **9**, `cari` **8**,
   `haftanın günü` **8** küpte. Aynı malzeme 28 istasyonda ayrı ayrı duruyor; **ortak
   kiler yok**. ✅
6. Bunun doğrudan sonucu: *"bu yıl vardiya bazında fire oranı"* gibi **tek cümlelik,
   sıradan** bir iş sorusu cevapsız kalıyor — çünkü ölçü bir küpte, boyut başka küpte. ✅
7. 🔴 **Ölçü seçimi kusurlu:** 28 küpün yalnız **4'ü** `default_measure` beyan ediyor.
   Kullanıcı *"en çok enerji harcayan 3 makine"* diyor; sistem **"Hangi ölçüyü
   istiyorsun?"** diye soruyor. Niyet tamdır; eksik olan **menünün kendisidir**. ✅
8. 🔴 **Telemetrimiz kör:** *"hangi kelimeleri bilmiyoruz"* sinyali olan
   `uncovered_words`, **ham Türkçe metin** üzerinde `[a-z]+` ile bölündüğü için
   parçalanmış geliyor — `müşteri` → `teri`, `bazında` → `baz`+`nda`. Canlı kütükte
   **196 dolu satırın 115'i (%58,7)** parça içeriyor. Menüyü büyütmek için baktığımız
   pusula **bozuk**. ✅ (konteynerde tekrar üretildi)
9. 🔴 **Toplanabilirlik beyanı neredeyse yok:** 172 ölçünün yalnız **12'si** `additive:`
   beyan ediyor. `R8` (yarı-toplanabilir koruması) yalnız **6** ölçüyü koruyor; kalan
   160 ölçü zaman kovasında koşulsuz `SUM` ediliyor. Bu, deponun *"en tehlikeli sınıf"*
   dediği **küp rozetli sessiz-yanlış**ın açık kapısıdır. 🔍
10. 🔴 **Ve menü sanıldığından dar:** bir kurumsal BI mutfağının sunmak zorunda olduğu
   **24 yemek sınıfının 11'i hiç yapılamıyor**, 5'i yarım yapılıyor (§5.1). Bunların
   **altısı** tek bir eksikte buluşuyor: **pencere katmanı yok** — `app/` içinde
   `PARTITION BY` **sıfır** kez geçiyor. ✅

---

## 3 · ÖLÇÜLEN TABLO — mutfağın bugünkü fotoğrafı

### 3.1 · Canlı kütük (K2 · 769 tur · 2026-08-01→08)

| `source` | n | pay | ort. süre | okuma |
|---|---:|---:|---:|---|
| **`NULL`** *(cevap yok)* | **287** | **%37,3** | **11 101 ms** | 🔴 en büyük kova **ve** en yavaş ikinci yol |
| `cube` | 223 | %29,0 | 1 663 ms | 🟢 mutfağın kendi yolu — hızlı ve doğru |
| `cube+llm` | 186 | %24,2 | 16 448 ms | 🟡 garson devrede; **10× daha yavaş** |
| `meta` | 35 | %4,6 | 132 ms | sohbet/meta |
| `llm:openrouter` | 14 | %1,8 | **37 022 ms** | 🔴 Discovery — *her ateşlenmesi bir mutfak eksikliği raporudur* |
| `llm:gemini` | 10 | %1,3 | 6 993 ms | 🔴 aynı |
| `vqr` | 9 | %1,2 | 220 ms | önbellek |

> 🔴 **Okunması gereken asıl satır birinci satırdır.** Discovery oranı (%3,1) düşük
> görünüyor ve bu bir başarı sanılabilir. **Değildir:** Discovery'ye düşmemesinin sebebi
> mutfağın yemeği yapabilmesi değil, sistemin **hiç yemek çıkarmadan** masayı
> toplamasıdır. `NULL` + Discovery = **%40,4**.

### 3.2 · `route()` pes etme gerekçeleri ve sonrası (K2)

| kod | anlam | n | pay | → `cube+llm` | → Discovery | → **cevapsız** |
|---|---|---:|---:|---:|---:|---:|
| **`R10`** | tanınmayan kelime (kapsam kapısı) | **292** | **%80,7** | 132 | 13 | **147 (%50,3)** |
| `R1` | küp eşleşmedi / çapraz konu | 39 | %10,8 | 23 | 5 | 11 |
| `R9` | kırılım istendi, boyut eşleşmedi | 15 | %4,1 | 2 | 1 | **10 (%66,7)** |
| `R4` | ölçü eşleşmedi | 11 | %3,0 | 4 | 0 | **7 (%63,6)** |
| `R5` | "ortalama" istendi, ortalama ölçü yok | 4 | %1,1 | 3 | 0 | 1 |
| `R2` | liste/döküm niyeti | 1 | %0,3 | 0 | 0 | 1 |
| `R3` `R6` `R7` `R8` | kıyas · yarım dışlama · belirsiz boyut · yarı-toplanabilir | **0** | — | — | — | — |

> ⚠ **`R3`/`R6`/`R7`/`R8` canlıda hiç ateşlenmedi.** İki okuma mümkün ve ayırt etmek
> **gerekir**: (a) o vakalar hiç sorulmadı, (b) daha erken bir kapı (`R10`) o soruları
> zaten yutuyor. §7'deki senaryo ailelerinin **E ve F**'si tam olarak bunu ayırmak için
> yazıldı.

### 3.3 · Korpus (K1 · 14 726 tur · LLM YOK — mutfağın kendi tavanı)

| sonuç | n | pay |
|---|---:|---:|
| **OK** (tekil+süreç) | 10 250 | **%69,6** |
| CLARIFY:dönem | 2 025 | %13,7 |
| CLARIFY:konu | 1 960 | %13,3 |
| CLARIFY:ölçü | 92 | %0,6 |
| NOTE (*"anlayamadım"*) | 375 | %2,5 |
| CUBE-SAPMA(None) | 23 | %0,2 |
| YANLIŞ-OK (gürültüye SQL) | 1 | %0,0 |

**Doğru küp oranı:** 9 276 / 9 734 = **%95,3** → **458 turda yanlış küp seçildi.** ✅
Şirket kırılımı: boyahane %96 · atiksan %98 · gulteks %95 · **gitas %89**.

Yanlış küp seçimleri **rastgele değil, sistematik**:

```
`bu yıl satış`                      beklenen=karlilik      seçilen=ticaret
`geçen ay satış tutarı`             beklenen=mal           seçilen=ticaret
`geçen ay makine bazında elektrik`  beklenen=enerji_makine seçilen=surdurulebilirlik
`son 30 gün operatör bazında dE`    beklenen=kalite        seçilen=parti
```

Dördü de aynı sebebi taşıyor: **aynı kelime iki menüde birden yazılı.**

### 3.4 · Menü envanteri (K3 · `demo/packs`)

| ölçüt | değer | okuma |
|---|---:|---|
| küp | **28** | 3'ü kaynak-varyantı (`ticaret`×3, `cari`×3, `mal`×2) |
| ölçü | **172** | hepsinde `unit:` ✅ hepsinde `synonyms:` ✅ |
| boyut | **123** | ⚠ `enerji_tesis`: **12 ölçü, 0 boyut** — hiçbir kırılım yapılamaz |
| zaman boyutu | 28 | küp başına tam **1** |
| `default_measure` beyan eden küp | **4 / 28 (%14)** | 🔴 `R4` ve *"Hangi ölçüyü istiyorsun?"* duvarının doğrudan sebebi |
| `additive:` beyan eden ölçü | **12 / 172 (%7)** | 6 `full` + 6 `semi`; **160 ölçü beyansız** |
| `always_filter` beyan eden küp | 3 / 28 | |
| **çakışan sinonim (≥2 küp)** | **152 kelime** | 🔴 §4.1 |

---

## 4 · KÖK TEŞHİSLER

> Her kök için ölçüt aynı: *"aynı kök başka hangi cümleyi de öldürüyor?"* Cevabı
> yazamadığım hiçbir maddeyi kök saymadım — o maddeler §6'da **kök değil, kalem** olarak
> duruyor.

---

### 🔴 M-1 · ORTAK BOYUT KATMANI YOK — *aynı malzeme 28 ayrı istasyonda*

**Kanıt (✅ ÖLÇÜLDÜ):** `demo/packs`'teki 28 küpün sinonim sözlükleri taranınca **152
kelime birden çok küpte** çıkıyor:

| kelime | kaç küpte | küpler |
|---|---:|---|
| `müşteri` | **11** | cari · firsat · kalite · mal · parti · sevkiyat · sikayet · siparis · surdurulebilirlik · ticaret · yaslandirma |
| `tezgah` | **9** | bakim · bakim_is_emri · enerji_makine · kalite · maliyet · oee · parti · sikayet · surdurulebilirlik |
| `cari` | 8 | cari · firsat · mal · sevkiyat · sikayet · siparis · ticaret · yaslandirma |
| `haftanın günü` | 8 | bakim · cari · kalite · mal · oee · parti · surdurulebilirlik · ticaret |
| `bölüm` / `departman` / `birim` | 6 / 5 / 5 | butce · egitim · enerji_makine · ik · isg · parti |
| `vardiya` | 4 | ik · isg · kalite · oee |
| `renk` | 4 | kalite · parti · sikayet · surdurulebilirlik |

**Neden bu bir dil sorunu DEĞİL:** `müşteri` kelimesi mükemmel anlaşılıyor. Sistem onu
**11 kez** buluyor. Kusur, kelimenin **11 farklı yerde ayrı ayrı tanımlanmış olmasıdır**.
Garson dünyanın en iyi Türkçesini konuşsa da menüde 11 tane *"müşteri"* yazılıysa hangi
istasyona sipariş vereceğini bilemez — çünkü **cevap menüde yok**.

**Bu kök hangi cümleleri öldürüyor** (K2 canlı kütükten, `R10`+cevapsız):

```
bu yıl vardiya bazında fire oranı        → "İK, İSG, kalite ile ilgili görünüyor ama hangi ölçü?"
şubat ayı personel verimlilikleri        → "Eğitim, OEE, parti ile ilgili görünüyor..."
son 3 ayda hangi müşteriden kaç şikayet  → "şikayet, parti, cari ile ilgili görünüyor..."
bu yıl fire oranı en düşük vardiya       → aynı
```

Dördünde de niyet **tam**: ölçü belli, boyut belli, dönem belli. **Sığmayan şey
(ölçü, boyut) çiftidir** — ölçü bir küpte, boyut başka küpte.

**Bugünkü telafi ve neden yetmiyor:** `blend` (`wren_service.blend_sql`) çapraz-küp
harmanı yapabiliyor, ama üç kısıtla: (a) **en fazla 2 küp** (`intent_semasi.py`:
`maxItems: 2`), (b) yalnız **paylaşılan** gruplama anahtarlarında, (c) `blend_uyumlu`
kapısından geçmek şartıyla. Paylaşılan anahtar **ancak boyut ortaksa** vardır — ki bu
kökün kendisi tam da o ortaklığın **olmadığını** söylüyor. *Bir birleşimin ön koşulu, o
birleşimin çözmesi gereken şeydir.*

#### KÖK ÇÖZÜM — **UYUMLU BOYUT (conformed dimension) KATMANI**

Bir *tekil düzeltme* değil, menünün **bir kat aşağısına** yeni bir varlık koymak:

```yaml
# demo/packs/cekirdek/boyutlar/musteri.yml   (YENİ — ortak kiler)
name: musteri
label: müşteri
type: uyumlu                       # conformed
anahtar: musteri_kod               # tüm olgu tablolarında AYNI anahtar
synonyms: [müşteri, müşteriler, cari, alıcı, firma, hesap]
nitelikler:                        # boyutun KENDİ kolonları (olguda değil)
  - {name: musteri_adi,   type: VARCHAR}
  - {name: musteri_sehir, type: VARCHAR}
  - {name: musteri_segment, type: VARCHAR}
```

```yaml
# küp tarafı — sinonim TEKRARLANMAZ, boyut REFERANS EDİLİR
dimensions:
  - uses: musteri            # ← yalnız bu; sinonimler ortak tanımdan gelir
    on: musteri_kod
```

**Kazanç zinciri — ve neden bu kök:**

1. `müşteri` kelimesinin **tek sahibi** olur → §3.3'teki 458 yanlış küp seçiminin sebebi
   ortadan kalkar (kelime artık küp seçmez, **boyut seçer**).
2. `R1` (çapraz konu) ve `R9` (boyut eşleşmedi) dallarının **girdisi değişir**: soru
   *"ölçü A + uyumlu boyut B"* biçimindeyse artık **belirsiz değildir** — ölçü küpü
   seçer, boyut ona **takılır**.
3. `blend`'in ön koşulu (**paylaşılan anahtar**) yapısal olarak **garanti** olur →
   iki-küp sınırı gerçekten kullanılabilir hâle gelir, `maxItems: 2` tartışılabilir olur.
4. `vardiya bazında fire oranı` cevaplanır: `fire_orani`(parti) × `vardiya`(uyumlu).
5. `haftanın günü` 8 küpten çıkar, **takvim boyutunun niteliği** olur — tarih
   hiyerarşisi (yıl/çeyrek/ay/hafta/gün/haftanın-günü/tatil-mi) tek yerde tanımlanır.

⚠ **Kapsam uyarısı:** bu, ADR-0005 (paket mimarisi) ve ADR-0018 (3 katmanlı sinonim) ile
çakışmaz, onların **altına** bir katman ekler. Ama `mdl_writer` · `compose` ·
`_match_cube` · `_match_dims` · `blend_uyumlu` **beşi birden** etkilenir. Faz'lı inmeli:
**önce tek boyut (`musteri`), tek şirket (`demo-boyahane`), bayrak arkasında.**

---

### 🔴 M-2 · ÖLÇÜ SEÇİMİ: sistem SORUYOR, seçmiyor

**Kanıt (✅ ÖLÇÜLDÜ):** 28 küpün **4'ü** `default_measure` beyan ediyor (`oee`,
`enerji_sapma`, `enerji_tesis`, +1). Canlı kütükte bunun bedeli:

```
bu yıl en çok enerji harcayan 3 makineyi bul   → "Hangi ölçüyü istiyorsun?"   (11,1 sn sonra)
bu yıl en çok satılan 5 renk                   → "Hangi ölçüyü istiyorsun?"
bu yıl en düşük kalite puanlı 3 makine         → "Hangisini istiyorsun?"
bu yıl en uzun duruşu yaşayan hat hangisi      → "Hangisini istiyorsun?"
toplam duruş dakikasını hat bazında sırala     → "toplam sure dk çıkarabilirim — hangi dönem?"
```

🔴 Dikkat: son satırda sistem **ölçüyü bulmuş** (`toplam_sure_dk`), **kırılımı bulmuş**
(`hat`), **sıralamayı bulmuş** — ve yine cevap vermiyor, çünkü **dönem yok** (bkz. M-4).
İlk dördünde ise dönem **var**, kırılım **var**, top-N **var**; eksik olan tek şey
menünün *"bu küpte varsayılan olarak şu ölçü kastedilir"* demesi.

**Neden `R5` ile aynı aile:** *"ortalama satış"* → `R5` (ortalama ölçü tanımlı değil).
Sistem *"ortalama"* niteleyicisini **anlıyor** ama menüde `ort_*` karşılığı yok. Yani
kusur anlamada değil, **menünün eksikliğinde**.

#### KÖK ÇÖZÜM — **ÖLÇÜ ROLÜ + VARSAYILAN, katalogda beyan**

Kelime listesi değil, **beyan alanı**:

```yaml
measures:
  - name: toplam_elektrik_kwh
    rol: tuketim              # tuketim | verimlilik | maliyet | kalite | sure | oran | adet
    birincil: true            # bu ROL için bu küpteki varsayılan ölçü
  - name: ort_spesifik_enerji
    rol: verimlilik
```

Ve küp düzeyinde: `default_measure: toplam_elektrik_kwh`.

**Kural:** *"en çok X yapan"* / *"en yüksek X"* gibi **üstünlük** ifadeleri bir **rol**
işaret eder (`harcayan`→`tuketim`, `satılan`→`adet|tutar`). Rol tek bir `birincil` ölçüye
çözülüyorsa **soru sorulmaz, cevap verilir** ve seçim **beyan edilir**
(*"toplam elektrik (kWh) üzerinden"*). Rol iki `birincil`e çözülüyorsa **o zaman**
netleştirme — ve o netleştirme **anlamlıdır**, çünkü gerçekten iki ayrı iş sorusudur.

**Aynı kök başka neyi öldürüyor:** `R4` (11 tur, %63,6'sı cevapsız) · `R5` (4 tur) ·
korpusun `CLARIFY:ölçü` kovası (92 tur) · `CLARIFY:konu`nun *"…ile ilgili görünüyor ama
hangi ölçüyü istediğini anlayamadım"* biçimindeki **büyük** payı.

⚠ **Sınır — ADR-0008 uyumu:** rol sözlüğü **kapalı** ve **7 değerlidir**. Bu bir dil
kovalama değil, `yetenek.py`'nin `_YARGI`/`_FORECAST` ile aynı kalıbı: *bir ürün
kavramını adlandırmak*. Rol **kelimeden** değil, **ölçünün kendi ifadesinden ve
biriminden** doğrulanabilir olmalı (`unit: kWh` + `SUM(...)` → `tuketim`).

---

### 🔴 M-3 · TÜREV ÖLÇÜ YOK — *oran, pay, katkı ifade edilemiyor*

**Kanıt (🔍 KOD OKUMASI + ✅ canlı örnek):**
`CubeQuery`'nin ölçü alanı bir **ad listesidir** (`measures: [str]`, `intent_semasi.py`
`enum`). Ölçü **aritmetiği** için bir yer yok. `measure_having` bir **süzgeçtir**, bir
ifade değil. Canlı kütükten:

```
bu yıl toplam üretimin yüzde kaçı fire   → "Hangi ölçüyü istiyorsun?"  (cevapsız)
```

Bu soru menüde **iki ölçüye** bakıyor (`fire_kg`, `uretim_kg`) ve aralarında bir **bölme**
istiyor. Küp o bölmeyi ancak **önceden tanımlanmışsa** (`fire_orani`) yapabilir. Yani
sistemin türev ölçü kapasitesi = **birinin önceden yazmış olması**.

**Aynı kök başka neyi öldürüyor:**
* *"ciro içindeki payı"*, *"toplamın yüzde kaçı"*, *"X'in Y'ye oranı"* — tüm **pay/oran**
  ailesi.
* *"geçen aya göre yüzde kaç arttı"* — `compare` yalnız `yoy`/`mom` **iki değerlik**
  enum'dur; **yüzde değişimi bir ölçü olarak** yoktur.
* `app/contribution.py` (katkı ayrıştırma) `measure_expressions`'a bakarak *"bu ölçüde
  katkı matematiksel olarak tanımsız"* diyebiliyor — yani sistem **sınırı biliyor**, ama
  sınırın **öte tarafını** üretemiyor.
* `bakim`/`isg`/`kalite` küplerinin *"oran"* soruları (`oran` kelimesi canlı
  `uncovered_words`'te **16 kez**).

#### KÖK ÇÖZÜM — **TÜRETİLMİŞ ÖLÇÜ (`derived measure`) — katalogda, SQL'de değil**

```yaml
measures:
  - name: fire_orani_yuzde
    turev:                                   # ← ham SQL DEĞİL; ölçü cebri
      pay: fire_kg
      payda: uretim_kg
      kip: yuzde                             # yuzde | oran | fark | degisim_yuzde
    unit: "%"
    additive: non                            # türev ölçü toplanamaz — beyanı ZORUNLU
    synonyms: [fire oranı, fire yüzdesi, üretimin yüzde kaçı fire, fire payı]
```

**Neden `expression:` ile ham SQL yazmak yanlış çözüm:** bugün de `expression`
yazılabiliyor ve 172 ölçünün hepsi öyle. Ama ham SQL **toplanabilirlik bilgisini
taşımaz** — `SUM(a)/SUM(b)` ile `AVG(a/b)` arasındaki fark SQL'de görünmez, **ölçü
cebrinde görünür**. Türev beyanı üç şeyi birden verir: doğru SQL (`SUM(pay)/SUM(payda)`,
gruplamadan **sonra**), doğru `additive: non` çıkarımı, ve `contribution.py`'nin zaten
beklediği kanıt.

**Ve bu kök M-2'yi tamamlıyor:** rol katmanı `oran` rolünü zaten tanımlıyor; türev ölçü
o rolü **doldurulabilir** kılıyor.

---

### 🔴 M-4 · DÖNEM POLİTİKASI: soru sormak varsayılan davranış

**Kanıt (✅ ÖLÇÜLDÜ):** korpusun **%13,7'si** `CLARIFY:dönem`. Canlı kütükte örnek:

```
toplam duruş dakikasını hat bazında sırala   → "toplam sure dk çıkarabilirim — hangi dönem için?"
en verimsiz hattı bul ve nedenini açıkla     → "ort oee çıkarabilirim — hangi dönem için?"
```

İkisinde de ölçü, boyut ve niyet **çözülmüş**. Tek eksik dönem — ve `ADR-0007` gereği
sistem **soruyor**. Politika savunulabilir; **bedeli ölçülmedi**.

`is_period_optional()` (`cube_router.py:746`) zaten bir istisna taşıyor:
yarı-toplanabilir ve toplanamaz ölçülerde dönem sorulmuyor. Yani **mekanizma var**,
**kapsamı dar**.

#### KÖK ÇÖZÜM — **KÜPÜN BEYAN ETTİĞİ VARSAYILAN DÖNEM + görünür beyan**

```yaml
# küp düzeyinde
varsayilan_donem: son_12_ay        # yok | son_12_ay | bu_mali_yil | tum_zamanlar | veri_araligi
```

Kural: dönem yoksa **beyanla varsayılana düş** — *"Dönem belirtmediğin için **son 12 ay**
alındı."* — ve bu beyan **düzenlenebilir bir çapa** olarak dönsün (`donem_capasi` zaten
takip turunda çapayı taşıyor). Netleştirme **kalkmaz**, **ikinci** seçenek olur:
`varsayilan_donem: yok` diyen küp bugünkü gibi sorar.

**Neden bu kök, yama değil:** `app/veri_araligi.py` verinin gerçek aralığını **zaten
biliyor** (`partiler` 2026-06-30'da bitiyor). Bugün o bilgi yalnız *"bu dönemde veri
yok"* demek için kullanılıyor. Aynı bilgi **varsayılanı seçmek** için kullanılırsa
`CLARIFY:dönem`'in büyük kısmı cevaba döner ve **kullanıcı hiçbir doğruluk
kaybetmez** — çünkü beyan görünür.

⚠ **Sınır:** bu, `ADR-0027`'nin (*mali takvim bir varsayımdır, bir gerçek değil*)
ihlali **değildir** — tam tersi, aynı ilkeyi uyguluyor: varsayım yapılıyor **ve
söyleniyor**. Sessiz varsayım yasaktır; **beyanlı** varsayım deponun kendi desenidir
(`uyum.kismi_cevap_notu`).

---

### 🔴 M-5 · TOPLANABİLİRLİK BEYANI YOK — sessiz-yanlışın açık kapısı

**Kanıt (✅ ÖLÇÜLDÜ · 🔍 sonucu tetiklenmedi):** 172 ölçünün **12'si** `additive:` beyan
ediyor (6 `full`, 6 `semi`). `wren_service.py:678` `semi_additive` listesini **yalnız bu
beyandan** türetiyor. `cube_router.py:3821`'deki `R8` koruması (zaman kovalı bakiye =
running balance → küp üretemez) dolayısıyla **6 ölçü** için çalışıyor.

Kalan **160 ölçü** için varsayılan **tam toplanabilir**. `cari`/`yaslandirma`/`mal`
küplerinde `bakiye`, `borç`, `alacak`, `stok` gibi ölçüler var — bunlar doğaları gereği
**dönem-sonu snapshot**tır. Beyan edilmedikleri sürece *"aylara göre bakiye"* sorusu düz
`SUM` üretir: **`◆ CUBE` rozetli, güven 1.0, makbuz tam — ve sayı yanlış.**

🔴 Ve `R8` canlı 769 turda **hiç ateşlenmedi** (§3.2). Bu, korumanın çalıştığının kanıtı
**değildir**; korumanın **hiç sınanmadığının** kanıtıdır.

#### KÖK ÇÖZÜM — **BEYAN ZORUNLU + kapı: beyansız ölçü zaman kovasına giremez**

1. `additive:` alanı **her ölçüde zorunlu** olsun (`full` | `semi` | `non`).
2. Derleme kapısı (`mdl_writer` / `compose`): beyansız ölçü taşıyan bir küp
   **derlenmesin** — `ADR-0025`'in *fail-closed grain sözleşmesi* deseni.
3. Geçiş için tek turluk bir **çıkarım yardımcısı**: `expression` `AVG(`/`COUNT(DISTINCT`
   içeriyorsa `non`; ad/birim `bakiye|stok|borç|alacak|adet_son` kalıbındaysa **`semi`
   önerisi** üret — ama **otomatik yazma**, insana onaylat (`ADR-0028` deseni: uydurma
   yok).

**Aynı kök başka neyi öldürüyor:** `viz.py:330` (grafik seçimi `non_additive`'e bakıyor)
· `contribution.py:103` (katkı ayrıştırma) · `gorsel_ekleme.py:66`. Üçü de aynı beyandan
besleniyor ve üçü de bugün **%93 boş** bir alandan okuyor.

---

### 🔴 M-6 · SÜZGEÇ SÖZLÜĞÜ: motor 12 operatör biliyor, sipariş fişi 7

**Kanıt (🔍 KOD OKUMASI — canlıda tetiklenmedi):**

| katman | operatörler |
|---|---|
| motor (`cube_query_to_sql`, `cube_router.py:3745` yorumunda **çalıştırılarak doğrulanmış**) | `eq` `neq` `in` `not_in` `gt` `gte` `lt` `lte` `contains` `starts_with` `is_null` `is_not_null` — **12** |
| `route()`'un ürettiği | `eq` `neq` `in` `not_in` (+ tarih `gte`/`lte`) |
| **Intent-JSON şeması** (`intent_semasi.py:189`) | `eq` **`ne`** `gt` `gte` `lt` `lte` `in` — **7** |
| `parse_cube_query` doğrulaması | 🔴 **operatörü HİÇ denetlemiyor** — yalnız `dimension` beyaz listesi (`cube_router.py:4239`) |

İki ayrı kusur, aynı kökten:

1. **Garsonun fişi mutfaktan dar.** `not_in` · `contains` · `starts_with` · `is_null` ·
   `is_not_null` **sipariş fişinde yok** → garson *"beyaz hariç"*, *"adı X ile
   başlayanlar"*, *"kodu boş olanlar"* niyetlerini **ifade edemez**, ve ifade edemediği
   için Discovery'ye düşer. Mutfak o yemeği **yapabiliyor**; menüde **yazmıyor**.
   *Bu, `blend`'in başına gelenin birebir aynısı* (`intent_semasi` docstring'i o dersi
   kendisi yazıyor: *"düşürülen şey geçersiz bir değer değil, var olan bir yetenekti"*).
2. 🔴 **`ne` ≠ `neq`.** Şema modele `ne` yazdırıyor; motor `ne` **tanımıyor**;
   `parse_cube_query` operatörü **kontrol etmiyor** → değer olduğu gibi
   `cube_query_to_sql`'e gidiyor. Yorumun kendi ifadesiyle: *"geçersiz operatör Rust'ta
   gürültülü reddediliyor."* Yani garson *"beyaz olmayan"* niyetini **doğru** anlasa bile
   sorgu **derlenmez**.
   ⚠ Canlı kütükte tetiklendiğine dair kayıt **yok** — çünkü şema-kısıtlı kip
   (`llm_sema_kisitli: beta`) mevcut sağlayıcıda **`oneOf` desteklenmediği için NO-OP**
   (bkz. `project_garson_ara_fazi`). **Sağlayıcı `oneOf` destekleyen birine geçtiği gün
   bu kusur canlıya çıkar.** Senaryo **F ailesi** bunu bilerek sınıyor.

#### KÖK ÇÖZÜM — **OPERATÖR SÖZLÜĞÜ TEK KAYNAKTAN**

```python
# app/cube_operatorleri.py  (YENİ — tek sahip)
MOTOR_OPERATORLERI = ("eq","neq","in","not_in","gt","gte","lt","lte",
                      "contains","starts_with","is_null","is_not_null")
```

* `intent_semasi.cube_query_json_schema` bu demeti **enum olarak** kullansın (elle
  yazılmış 7'lik liste **silinsin**).
* `parse_cube_query` filtre operatörünü bu demete karşı **doğrulasın**; tanımadığını
  **düşürmesin — sorguyu reddetsin** (sessiz düşürme, `compare`/`measure_having`'in
  başına gelen şeydir ve bu dosya o dersi iki kez yazmış).
* Kapı testi: *"şemadaki her operatör motorun demetinde vardır"* — AST/enum karşılaştırması.

**Aynı kök başka neyi öldürüyor:** `R6` (yarım dışlama) dalının kapsamı; *"boş olanlar"*,
*"tanımsız"*, *"X ile başlayan"* ailesi; ve gelecekte eklenecek her operatörün **iki
yerde** eklenmesi zorunluluğu (yani bu kusurun **tekrar üremesi**).

---

### 🔴 M-7 · MENÜ PUSULASI BOZUK — `uncovered_words` parçalanmış geliyor

**Kanıt (✅ ÖLÇÜLDÜ — canlı konteynerde tekrar üretildi):**

```
$ docker exec dima-backend-core python -c "…cube_router.partial_unknowns('şubatta müşteri bazında fire', sch)"
['ubatta', 'teri', 'baz', 'nda', 'fire']
```

`müşteri` → `teri` · `bazında` → `baz` + `nda` · `şubatta` → `ubatta` ·
`çeyrek` → `eyrek` · `yüzde` → `zde` · `duruş` → `duru`.

**Sebep:** `_uncovered()` (`cube_router.py:3063`) `re.findall(r"[a-z]+", q)` yapıyor.
Türkçe harfler `[a-z]` dışında olduğu için **kelimeyi ortasından bölüyorlar**. Fonksiyonun
**yazılmamış bir ön koşulu** var (*"q normalize gelmeli"*) ve **hiçbir muhafız onu
denetlemiyor**.

**Çağrı yeri denetimi — sözleşme altı yerde ikiye ayrılmış:**

| çağrı yeri | ne gönderiyor | |
|---|---|---|
| `app/routers/ask.py:3484` | `q_norm` | ✅ |
| `app/cube_router.py:3571` | `_norm(q)` | ✅ |
| `app/niyet.py:357` | `cr._norm(soru)` | ✅ |
| **`app/answer.py:181`** | **`body.question` — HAM** | 🔴 |
| `app/cube_router.py:1928` · `:3350` | çağırana bağlı | ⚠ denetlenmemiş |

**Bedeli (✅ ÖLÇÜLDÜ, K2):** `uncovered_words` dolu **196 canlı satırın 115'i (%58,7)**
parça içeriyor. En sık *"bilinmeyen kelimeler"*imiz: `nda` (36) · `baz` (29) · `duru`
(16) · `nas` (13) · `teri` (7) · `ubata` (7) · `eyrek` (5) · `zde` (5).

🔴 **Bu bir görüntü kusuru değil, bir KÖRLÜK kusurudur.** Menüyü hangi yönde
büyüteceğimize karar verirken baktığımız **tek sinyal** budur. Bugün o sinyal
*"kullanıcılar en çok `nda` kelimesini soruyor"* diyor.

⚠ **Kullanıcıya giden metin ETKİLENMİYOR** (kontrol edildi): *"«…» kısmını anlayamadım"*
cümlesi `ask.py:3583`'ten çıkıyor ve o dal `q_norm` kullanıyor — korpus çıktısındaki
temiz kelimeler (`gerceklesen`, `kaynagi`, `depo`) bunu doğruluyor. Yani kusur
**telemetride ve türetme/typo besleme yolunda**, kullanıcı metninde değil.

#### KÖK ÇÖZÜM — **ÖN KOŞULU KALDIR, tek satır**

`partial_unknowns` girdisini **kendi içinde** normalize etsin. `_norm` **idempotenttir**
(konteynerde doğrulandı: `_norm(_norm(x)) == _norm(x)`) → normalize gelen çağrılar
**hiç etkilenmez**, ham gelen çağrı **düzelir**, ve yazılmamış ön koşul **ortadan
kalkar**.

```python
def partial_unknowns(q: str, schema: dict) -> tuple[list[str], list[tuple[dict, str]]]:
    q = _norm(q)          # ← ön koşulu SÖZLEŞMEYE çevir; _norm idempotent
    ...
```

**Kapı testi:** `partial_unknowns(ham, ş) == partial_unknowns(_norm(ham), ş)` — altı
çağrı yerinin hangisinin ne gönderdiği **artık önemsiz** olsun. *Bir ön koşulu belgelemek
yerine ortadan kaldırmak, onu doğrulamaktan ucuzdur.*

⚠ **Geriye dönük:** kütükteki 115 satır düzelmez; ölçüm **düzeltmeden sonra** yeniden
başlar. Bu yüzden §7'nin **G ailesi** düzeltme sonrası ilk turda koşulmalı.

---

### 🔴 M-8 · MENÜ KAYNAĞA GÖRE DEĞİŞİYOR — aynı soru bir müşteride var, ötekinde yok

**Kanıt (✅ ÖLÇÜLDÜ):** aynı adlı küp, ERP kaynağına göre farklı ölçü sayısı taşıyor:

| küp | netsis | mikro-v16 | logo-3 |
|---|---:|---:|---:|
| `ticaret` | **9 ölçü / 5 boyut** | 8 / 3 | 6 / 2 |
| `mal` | 7 / 6 | — | 6 / 2 |
| `cari` | 4 / 5 | 4 / 2 | 4 / 2 |

Korpusun şirket kırılımı bunu doğruluyor: doğru küp oranı **gitas %89**, atiksan %98.
Yani *"mutfak ne kadar iyi"* sorusunun cevabı **hangi müşteride olduğuna bağlı** ve bu
fark **hiçbir yerde beyan edilmiyor**.

#### KÖK ÇÖZÜM — **YETENEK FARKI BEYANI (`gereksinim.yml` zaten var, tüketicisi yok)**

`demo/packs/kaynak/*/gereksinim.yml` dosyaları **mevcut**. Eksik olan, o beyanın
**çalışma zamanında** okunması: bir soru bu kiracıda karşılanamıyorsa `yetenek.py`'nin
**üçüncü kutusu** (`yapamiyorum`) *"bu ölçü senin ERP'nde yok — `X` alanı gerekiyor"*
desin. Bugün aynı soru sessizce `R4`'e düşüyor ve kullanıcı **bunun bir kaynak sınırı
olduğunu** öğrenemiyor.

**Aynı kök başka neyi öldürüyor:** menü genişletme planlamasını — hangi ölçünün hangi
ERP'de eksik olduğunu **sayamıyoruz**, dolayısıyla *"menüyü genişlet"* işi
önceliklendirilemiyor.

---

## 5 · MUTFAĞIN TAM HÂLİ — aşçının yapabilmesi gereken yemek sınıfları

> 🔴 **Hedef, kusurları kapatmak değil.** Hedef şu: **mutfak muazzam bir yer olmalı, aşçı
> her şeyi yapabilmeli.** §4 *"neyin bozuk olduğunu"* söylüyor; bu bölüm *"tam hâlin ne
> olduğunu"* söylüyor — çünkü bir eksik listesi, hedefi kendiliğinden vermez.
>
> Aşağıdaki tablo **analitik yemek sınıflarının** tam listesidir. Her satır, bir kurumsal
> BI mutfağının er ya da geç sunmak zorunda olduğu bir yemektir. **Bugünkü durum
> ölçüldü**, iddia edilmedi.

### 5.1 · Yetenek matrisi — 24 yemek sınıfı

| # | yemek sınıfı | örnek soru | bugün | kanıt | kapatan kök |
|---|---|---|:---:|---|---|
| 1 | **Toplam** | `bu ay toplam üretim` | 🟢 | `route()` · %66 OK | — |
| 2 | **Kırılım** | `hat bazında fire` | 🟢 | `dimensions` | — |
| 3 | **Trend / zaman kovası** | `aylara göre ciro` | 🟢 | `timeDimensions` + 5 granülerlik | — |
| 4 | **Üstünlük (top-N)** | `en yüksek 5 müşteri` | 🟢 | `order` + `limit` | — |
| 5 | **Boyut süzgeci** | `beyaz renkte fire` | 🟢 | `filters` | — |
| 6 | **Ölçü eşiği** | `10 milyon üzeri müşteriler` | 🟢 | `measure_having` (HAVING sarma) | — |
| 7 | **Dönemsel kıyas (YoY/MoM)** | `geçen yılın aynı ayı` | 🟢 | `app/yoy.py` · `compare` enum | — |
| 8 | **Adlandırılmış iki uç kıyası** | `mart'ı şubatla kıyasla` | 🟢 | `kiyas_cebiri.referans` | — |
| 9 | **Ayrık dönemler** | `ocak ve mart` | 🟡 | `ayrik_aylar` — **sarma hilesi**, `blend` ile **yasak** | K-6 |
| 10 | **Çapraz-küp harman** | `fire ve ciro birlikte` | 🟡 | `blend_sql` — **en fazla 2 küp**, ortak anahtar şart | **M-1** |
| 11 | **Kök-neden dallanması** | `neden düştü → hangi hat → hangi vardiya → ham satır` | 🟢 | `app/drill.py` — her seviyede **gerçek sorgu**, yaprakta ham satır | — |
| 12 | **Katkı ayrıştırma / PVM** | `düşüşün ne kadarı fiyat, ne kadarı miktar` | 🟡 | `app/contribution.py` var; `pvm:` beyanı **3 küpte** | M-5 (beyan) |
| 13 | **Türev ölçü (oran/pay)** | `üretimin yüzde kaçı fire` | 🔴 | canlıda cevapsız; `measures` bir **ad listesi** | **M-3** |
| 14 | **Yüzde değişim ölçüsü** | `yüzde kaç arttı` | 🔴 | `compare` iki değerlik **enum**; değişim bir **ölçü değil** | **M-3** |
| 15 | **Kümülatif / YTD** | `yıl başından beri kümülatif` | 🔴 | `grep ytd\|kumulatif\|cumulative → 0`; YTD yalnız `yoy` **penceresi** olarak var | **M-3** + pencere |
| 16 | **Hareketli ortalama** | `3 aylık hareketli ortalama` | 🔴 | `grep hareketli\|rolling\|moving → 0` | pencere katmanı |
| 17 | **Pencere fonksiyonu (genel)** | `sıraya göre kümülatif pay`, `LAG/LEAD` | 🔴 | 🔴 `grep "OVER (" · "PARTITION BY" → app/ içinde **0**` | **yeni: pencere** |
| 18 | **Yüzdelik / medyan** | `medyan sipariş büyüklüğü`, `p90 duruş` | 🔴 | `grep percentile\|median → 0` (yalnız `lineage.py` anımsıyor) | **M-3** (ölçü cebri) |
| 19 | **Grup içi sıralama** | `her hattın en kötü 3 makinesi` | 🔴 | `RANK() OVER (PARTITION BY …)` gerektirir → yok | pencere katmanı |
| 20 | **Kohort / elde tutma** | `ocak'ta ilk alan müşteriler 6 ay sonra` | 🔴 | `grep kohort\|cohort → 0` | **M-1** + kohort |
| 21 | **Huni / dönüşüm** | `fırsat → teklif → sipariş dönüşümü` | 🔴 | `grep huni\|funnel → 0`; `firsat` küpü **var**, huni yok | **M-1** + huni |
| 22 | **Anomali / aykırı tespiti** | `bu ay olağandışı olan ne` | 🟡 | `drill.flag_outliers` **var** (yorumlayıcı); otomatik tarama **yok** | izleme |
| 23 | **Tahmin (forecast)** | `bu gidişle yılı nerede kapatırız` | 🔴 | `yetenek.KUTU_YAPMIYORUM` — **v1'de bilinçle yok** | ürün kararı |
| 24 | **Yargı / hedefe göre** | `iyi miyiz kötü müyüz` | 🔴 | `yetenek._YARGI` sınırı; `hedef.py` beyan bekliyor (`ADR-0028`) | hedef beyanı |

**Sayım:** 🟢 **8** · 🟡 **5** · 🔴 **11** — yani **24 yemek sınıfının 11'i mutfakta
yapılamıyor**, 5'i yarım yapılıyor.

### 5.2 · Bu tablonun söylediği ONUNCU kök

Yukarıdaki 🔴 satırların **altısı** (15 · 16 · 17 · 18 · 19 + kısmen 9) tek bir eksikte
buluşuyor ve bu, §4'te ayrı bir kök olarak görünmüyordu çünkü **hiç ateşlenmiyor** —
sistem o soruları o kadar erken reddediyor ki kütüğe bile düşmüyorlar:

> 🔴 **M-9 · PENCERE (WINDOW) KATMANI YOK.**
> `CubeQuery` yalnız **GROUP BY** cebri konuşuyor. `OVER (PARTITION BY … ORDER BY …)`
> ailesi — kümülatif, hareketli ortalama, grup-içi sıra, yüzdelik, `LAG`/`LEAD` —
> **hiçbir katmanda yok** (`app/` içinde `PARTITION BY` **sıfır** kez geçiyor).
> `R8`'in yorumu bunu **itiraf ediyor**: *"running balance = WINDOW → cube üretemez → LLM."*
> Yani sistem, pencere gerektiren her soruyu **tanıyor** ve **teslim ediyor**.

**Kök çözüm — `pencere` alanı, `blend`/`measure_having` ile aynı sarma deseni:**

```yaml
# ölçü düzeyinde beyan
measures:
  - name: kumulatif_uretim_kg
    pencere:
      taban: uretim_kg
      kip: kumulatif            # kumulatif | hareketli_ort | sira | yuzdelik | onceki
      pencere_boyu: 3           # hareketli_ort için
      bolum: [hat]              # PARTITION BY
      siralama: tarih           # ORDER BY
```

`wren_service.cube_sql` bunu **`measure_having` ve `ayrik_aylar` ile birebir aynı
biçimde** dışarıdan sarar: taban `cube_query_to_sql` çıktısı üretilir, pencere ifadesi
onun **üstüne** yazılır. Motor değişmez, derleyici değişmez — **bir sarma katmanı** eklenir.
Bu, deponun `ADR-0030` ilkesiyle uyumludur: *çevirici yazılır, motor yazılmaz.*

⚠ **Ve fail-closed:** pencereli bir ölçü **zorunlu olarak `additive: non`**'dur (M-5).
Beyan edilmeden pencere ölçüsü derlenmemeli — aksi hâlde kümülatif bir seri ikinci kez
toplanır ve bu, §4/M-5'in tam olarak uyardığı **küp rozetli sessiz-yanlış**tır.

### 5.3 · Menü genişliği — bir yemek sınıfı değil, bir ÖLÇÜ

Bugün *"menü ne kadar geniş"* sorusunun **sayısal bir cevabı yok**. Öneri, ölçüyü
kurmak — ve bunu bir panel değil, **korpusun bir satırı** yapmak:

```
MENÜ KAPSAMI = (cevaplanabilen yemek sınıfı × küp) / (24 × 28)
```

`lab/nl_corpus.py` her senaryoyu zaten *(cube, ölçü, niyet)* üçlüsüne çöküyor
(**şişme katsayısı 27,7×** — yani 9 182 turdan 332 semantik vaka). Aynı yere **yemek
sınıfı** ekseni eklenirse, korpus *"kaç soru cevaplanıyor"*a ek olarak **"kaç yemek
sınıfı sunuluyor"** sorusunu da cevaplar. Bu, `feedback_test_kapisi_disiplini`'nin
*"payda kutsaldır"* kuralını **bozmaz** — yeni bir **eksen** ekler, paydayı oynatmaz.

> *Bir mutfağın büyüklüğü, kaç sipariş aldığıyla değil, kaç farklı yemeği yapabildiğiyle
> ölçülür. Bugün ilkini sayıyoruz, ikincisini saymıyoruz.*

---

## 6 · KÖK DEĞİL, KALEM — ölçülmüş ama sınıfı yazılamayan bulgular

Bunlar gerçek kusurlar; ama *"aynı kök başka hangi cümleyi öldürüyor"* sorusuna net cevap
yazamadım. **Kök muamelesi görmemeliler.**

| # | bulgu | kanıt | not |
|---|---|---|---|
| K-1 | `enerji_tesis`: 12 ölçü, **0 boyut** | ✅ K3 | Hiçbir kırılım yapılamaz; *"tesis bazında"* soruları yapısal olarak cevapsız |
| K-2 | Cevapsız yol **11,1 sn** sürüyor | ✅ K2 | Netleştirme üretmek neden 11 sn? Merdivenin tamamı koşuluyor olabilir — **ölçülmeli** |
| K-3 | `cube+llm` **16,4 sn** (LLM'in kendisi 3,7 sn) | ✅ K2 | 12,7 sn LLM **dışında** geçiyor |
| K-4 | `R3`/`R6`/`R7`/`R8` canlıda **0 kez** | ✅ K2 | Kör mü, yoksa erişilmiyor mu? §7/E-F ailesi bunu ayırır |
| K-5 | `blend` en fazla **2 küp** | 🔍 K4 | M-1 inmeden bu sınır tartışılamaz |
| K-6 | `ayrik_aylar` + `blend` **birlikte yasak** | 🔍 K4 | Fail-closed, doğru karar — ama *"ocak ve mart, ciro ve fire"* cevapsız |
| K-7 | Korpusta **1** `YANLIŞ-OK` (gürültüye SQL) | ✅ K1 | Tek vaka; sessiz-yanlış sınıfı olduğu için **izlenmeli** |

---

## 7 · 50 ZİNCİR THREAD — teşhis ve doğrulama seti

### 7.1 · Nasıl koşulur

🔴 **Koşum biçimi ana belgenin §15.2'sidir; burada tekrarlanmaz.** Özet:

```bash
TK=$(curl -s -X POST localhost:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# ana belge §15.2'deki ask() fonksiyonunu tanımla, sonra:
ask s01 "<T1>"                          # taze tur — cube_query GÖNDERME
CQ=$(cat /tmp/cq.json)
ask s01 "<T2>" "$CQ" '"<T1>"'           # zincir turu — T1'in cq'sunu AYNEN yankıla
```

**Kurallar (ana belgeden, değişmedi):** tek tek koş · her turdan sonra dur · konteyner
logunu anbean oku · her turu belgele · **aralarında kapı koşma**.

**Her turda okunacak altı alan:** `source` · `explain.path` · `trace[0]` · `eksik_niyet`
· `note` · `interpretation.narration` *(ana belge §15.3)*.

### 7.2 · Kolonların anlamı

* **ŞİMDİ (beklenen):** bu belgenin teşhisine göre **bugün** ne olmalı. Farklı çıkarsa
  ya teşhis eksik ya sistem değişmiş — **ikisi de bir bulgudur, yazılmalı**.
* **SONRA (hedef):** ilgili kök çözüm indikten sonra ne olmalı. Bu kolon **kabul
  ölçütüdür**.
* 🔴 **Bir turda `source=cube` görmek başarı değildir** — `cube_query`'nin **doğru**
  olması başarıdır (ana belge / `feedback_curl_senaryo_dongusu`).

---

### A · ORTAK BOYUT (M-1) — 10 thread

| # | T1 | T2 | T3 | ŞİMDİ (beklenen) | SONRA (hedef) |
|---|---|---|---|---|---|
| A1 | `bu yıl vardiya bazında fire oranı` | `en kötü vardiya hangisi` | `o vardiyada hangi makine` | 🔴 `NULL` — *"İK, İSG, kalite ile ilgili görünüyor"* | `cube` · `parti.fire_orani` × uyumlu `vardiya` |
| A2 | `son 3 ay müşteri bazında fire` | `bir de şikayet sayısı ekle` | `en çok şikayet edeni getir` | 🟡 T1 belirsiz (11 küpte `müşteri`) | T1 `cube`, T2 `blend` (ortak `musteri` anahtarı) |
| A3 | `geçen ay makine bazında elektrik` | `en çok harcayan 3'ü` | `onların oee'si ne` | 🔴 yanlış küp: `surdurulebilirlik` (korpusta ölçüldü) | `enerji_makine`, T3 `blend`/uyumlu `makine` |
| A4 | `bu yıl renk bazında rework` | `aynı renklerde fire ne` | `ikisini yan yana` | 🟡 `renk` 4 küpte | T2/T3 tek harmanlı cevap |
| A5 | `şubat ayı personel verimlilikleri` | `en düşük 3 personel` | `onların eğitim saati` | 🔴 `NULL` — *"Eğitim, OEE, parti"* | `cube` + beyan |
| A6 | `bölüm bazında bütçe gerçekleşme` | `aynı bölümlerin enerjisi` | `sapması en yüksek bölüm` | 🟡 `bölüm` 6 küpte | `butce` × uyumlu `bolum`, T2 `blend` |
| A7 | `hat bazında duruş süresi bu ay` | `aynı hatların üretimi` | `duruş/üretim oranı` | T1 🟢, T2 🔴, T3 🔴 (M-3) | üçü de `cube`/`blend` |
| A8 | `müşteri bazında sevkiyat adedi son 3 ay` | `geciken sevkiyatlar hangi müşteride` | `o müşterinin cirosu` | T3 çapraz küp → 🔴 | T3 `blend` (`sevkiyat`×`ticaret`) |
| A9 | `haftanın gününe göre üretim` | `aynı günlerde fire` | `en kötü gün hangisi` | 🟡 `haftanın günü` 8 küpte | takvim boyutunun niteliği olarak çözülür |
| A10 | `tezgah bazında arıza sayısı` | `aynı tezgahların bakım maliyeti` | `en pahalı 3 tezgah` | 🔴 `tezgah` 9 küpte | uyumlu `makine` boyutu |

---

### B · ÖLÇÜ SEÇİMİ VE VARSAYILAN (M-2) — 7 thread

| # | T1 | T2 | T3 | ŞİMDİ | SONRA |
|---|---|---|---|---|---|
| B1 | `bu yıl en çok enerji harcayan 3 makineyi bul` | `en az harcayan 3'ü` | `aradaki fark` | 🔴 `NULL` — *"Hangi ölçüyü istiyorsun?"* (canlıda ölçüldü) | `cube` · rol=`tuketim` → `birincil` ölçü · **beyanlı** |
| B2 | `bu yıl en çok satılan 5 renk` | `en az satılan 5'i` | `ilk 5'in payı` | 🔴 `NULL` | T1/T2 `cube`; T3 M-3'e bağlı |
| B3 | `bu yıl en düşük kalite puanlı 3 makine` | `nedenleri` | `geçen yılla kıyasla` | 🔴 `NULL` — *"Hangisini istiyorsun?"* | `cube` + `compare: yoy` |
| B4 | `en uzun duruşu yaşayan hat hangisi` | `o hattın duruş nedenleri` | `en sık neden` | 🔴 `NULL` | `cube` |
| B5 | `ortalama satış` | `ortalama sipariş büyüklüğü` | `ikisinin farkı` | 🔴 T1 `R5` | T1 beyanlı ret **veya** `ort_*` ölçüsü |
| B6 | `bu ay bakım` | `plansız olanlar` | `maliyeti` | 🟡 `default_measure` yok → netleştirme | `cube` (varsayılan ölçü beyanlı) |
| B7 | `enerji` | `makine bazında` | `en yüksek` | 🟡 tek kelimelik konu | `cube` + varsayılan ölçü beyanı |

---

### C · TÜREV ÖLÇÜ (M-3) — 6 thread

| # | T1 | T2 | T3 | ŞİMDİ | SONRA |
|---|---|---|---|---|---|
| C1 | `bu yıl toplam üretimin yüzde kaçı fire` | `geçen yıl neydi` | `fark` | 🔴 `NULL` (canlıda ölçüldü) | `fire_orani_yuzde` türev ölçüsü |
| C2 | `fire'nin ciro içindeki payı` | `aylara göre` | `en yüksek ay` | 🔴 | türev + `blend` |
| C3 | `geçen aya göre ciro yüzde kaç arttı` | `fire de arttı mı` | `hangisi daha çok` | 🟡 `compare: mom` var ama **yüzde değişim ölçüsü yok** | `degisim_yuzde` kipi |
| C5 | `zamanında teslim yüzdesi` | `müşteri bazında` | `en kötü 3 müşteri` | 🟢 T1 (menüde **var**) | değişmez — **kontrol grubu** |
| C6 | `enerji maliyetinin toplam maliyete oranı` | `aylara göre` | `trend` | 🔴 | türev + `blend` |
| C7 | `kayıp iş gününün toplam iş gününe oranı` | `vardiya bazında` | `en riskli vardiya` | 🔴 | türev + uyumlu boyut (M-1'e bağımlı) |

---

### D · DÖNEM POLİTİKASI (M-4) — 4 thread

| # | T1 | T2 | T3 | ŞİMDİ | SONRA |
|---|---|---|---|---|---|
| D1 | `toplam duruş dakikasını hat bazında sırala` | `en yüksek 3` | `bu ay nasıl` | 🔴 `NULL` — *"hangi dönem için?"* (ölçüldü) | `cube` + **beyan**: *"son 12 ay alındı"* |
| D2 | `müşteri bazında şikayet sayısı` | `dönemi geçen yıl yap` | `en çok şikayet eden` | 🔴 T1 dönem sorusu | T1 varsayılanla cevap, T2 çapayı **değiştirir** |
| D3 | `güncel cari bakiye` | `müşteri bazında` | `en yüksek borçlu` | 🟢 `period_optional` çalışmalı | değişmez — **kontrol grubu** |
| D4 | `stok miktarı` | `depo bazında` | `en dolu depo` | 🟡 `period_optional` kapsamı sınanır | `cube` |

---

### E · TOPLANABİLİRLİK / SESSİZ-YANLIŞ (M-5) — 5 thread

> 🔴 **En hassas aile.** Buradaki hedef *"cevap geldi mi"* değil, **`◆ CUBE` rozetiyle
> YANLIŞ sayı gelip gelmediğidir.** Her turda `sql` alanı da okunmalı.

| # | T1 | T2 | T3 | ŞİMDİ | SONRA |
|---|---|---|---|---|---|
| E1 | `aylara göre cari bakiye` | `en yüksek ay` | `toplam` | 🔴🔴 **beklenen kusur:** `cube` rozetli **düz `SUM`** (running balance) → yanlış sayı | `R8` ateşlenir **veya** dönem-sonu snapshot |
| E2 | `aylara göre stok miktarı` | `depo bazında` | `en yüksek` | 🔴🔴 aynı sınıf | `R8` / as-of |
| E3 | `çeyreklere göre ortalama oee` | `en iyi çeyrek` | `yıl ortalaması` | 🔴 `AVG`'lerin `AVG`'i alınabilir | `non-additive` beyanı korur |
| E4 | `aylara göre benzersiz müşteri sayısı` | `toplam` | `çeyrek bazında` | 🔴 `COUNT(DISTINCT)` toplanamaz — T2 yanlış | `non` beyanı → beyanlı ret |
| E5 | `aylara göre toplam üretim` | `çeyrek bazında` | `yıllık` | 🟢 tam toplanabilir | değişmez — **kontrol grubu** |

---

### F · SÜZGEÇ / OPERATÖR (M-6) — 5 thread

| # | T1 | T2 | T3 | ŞİMDİ | SONRA |
|---|---|---|---|---|---|
| F1 | `beyaz hariç renk bazında fire` | `siyah da hariç` | `kalanların toplamı` | 🟡 T1 `not_in` üretebilir; T2 **`R6`** beklenir | üçü de `cube` |
| F2 | `müşteri adı "A" ile başlayanların cirosu` | `en yükseği` | `toplam payı` | 🔴 `starts_with` **fişte yok** → Discovery | `cube` |
| F3 | `kodu boş olan cariler` | `kaç tane` | `toplam bakiyeleri` | 🔴 `is_null` **fişte yok** | `cube` |
| F4 | `açıklamasında "acil" geçen iş emirleri` | `sayısı` | `ortalama süresi` | 🔴 `contains` **fişte yok** | `cube` |
| F5 | `10 milyon üzeri müşteriler` | `100 bin altındakiler` | `ikisinin sayısı` | 🟢 `measure_having` var | değişmez — **kontrol grubu** |

> 🔴 **F ailesi için ek koşum notu:** `llm_sema_kisitli` bu sağlayıcıda **NO-OP**
> (`oneOf` yok). Bu aile **`ne` vs `neq`** kusurunu ancak şema-kısıtlı kip gerçekten
> çalıştığında tetikler. Bu yüzden F1–F5, sağlayıcı `oneOf` destekleyen birine
> geçildiğinde **tekrar** koşulmalıdır — aksi hâlde 🟢 sonuç **yanıltıcıdır**.

---

### G · TELEMETRİ / BİLİNMEYEN KELİME (M-7) — 4 thread

> Bu ailenin doğrulaması **cevapta değil, kütükte**. Her turdan sonra:
> ```bash
> docker exec dima-backend-core python -c "
> import sqlite3;c=sqlite3.connect('/app/logs/dima.db')
> print(list(c.execute('select question,uncovered_words from interaction_log order by ts desc limit 1')))"
> ```

| # | T1 | T2 | ŞİMDİ (kütükte) | SONRA (kütükte) |
|---|---|---|---|---|
| G1 | `şubatta müşteri bazında fire` | `en yüksek müşteri` | 🔴 `['ubatta','teri','baz','nda',…]` | `[]` ya da **tam kelimeler** |
| G2 | `çeyrek bazında yüzde kaç düştü` | `hangi çeyrek` | 🔴 `['eyrek','baz','nda','zde',…]` | tam kelimeler |
| G3 | `duruş nedenlerine göre süre` | `en uzun neden` | 🔴 `['duru']` | `[]` |
| G4 | `zamanında teslim` *(ASCII kontrol)* | `müşteri bazında` | 🟢 T1 temiz | değişmez — **kontrol grubu** |

---

### H · KAYNAK/MENÜ FARKI + SINIR BEYANI (M-8 · `yetenek`) — 4 thread

| # | T1 | T2 | T3 | ŞİMDİ | SONRA |
|---|---|---|---|---|---|
| H1 | `firesiz partiler kaç tane` | `oranı` | `geçen ayla kıyasla` | 🔴 `yetenek`: *olumsuzluk yapmıyorum* — **ama `adhoc` dönmemeli** | beyanlı ret **veya** `not_in` çözümü |
| H2 | `fire ve rework birlikte` | `aylara göre` | `hangisi daha çok` | 🔴 iki küp ölçüsü → beyan **veya** `blend` | `blend` (2 küp sınırı içinde) |
| H3 | `bu gidişle yılı nerede kapatırız` | `geçen yıl ne olmuştu` | `fark` | 🔴 `yapmiyorum` (forecast v1'de yok) — T2 🟢 olmalı | T1 **net sınır beyanı**, T2 cevap |
| H4 | `bu ay iyi miyiz kötü müyüz` | `oee kaç` | `hedefe göre` | 🔴 `_YARGI` sınırı — T2 🟢, T3 `hedef.py` | T1 sınır beyanı + T2/T3 cevap |

---

### I · PENCERE VE İLERİ YEMEK SINIFLARI (M-9 · §5.1) — 5 thread

> 🔴 **Bu aile bugüne kadar hiç koşulmadı ve sebebi ölçüldü:** `app/` içinde
> `PARTITION BY` **sıfır** kez geçiyor. Beklenen sonuç *"kusur"* değil, **yokluk**tur —
> ve yokluğun **hangi basamakta** ilan edildiğini görmek bu ailenin asıl ürünüdür.
> 🔴 Bir tur `adhoc`/`llm:*` ile **sayı döndürürse** bu bir başarı değil, `yetenek.py`
> kapısının o sınıfı **tanımadığının** kanıtıdır (`feedback_garson_devri_kurali`:
> *her `adhoc` bir arıza raporudur*).

| # | T1 | T2 | T3 | ŞİMDİ | SONRA |
|---|---|---|---|---|---|
| I1 | `yıl başından beri kümülatif üretim` | `aylara göre` | `en hızlı artan ay` | 🔴 kümülatif ölçü **yok** (§5.1/15) | `pencere: kumulatif` |
| I2 | `3 aylık hareketli ortalama fire` | `hat bazında` | `en oynak hat` | 🔴 `rolling` **yok** (§5.1/16) | `pencere: hareketli_ort` |
| I3 | `her hattın en kötü 3 makinesi` | `sadece bu ay` | `toplam kaybı` | 🔴 grup-içi sıra = `RANK() OVER` **yok** (§5.1/19) | `pencere: sira` |
| I4 | `medyan sipariş büyüklüğü` | `müşteri bazında` | `p90 duruş süresi` | 🔴 yüzdelik/medyan **yok** (§5.1/18) | `pencere: yuzdelik` |
| I5 | `ocak'ta ilk sipariş veren müşteriler 6 ay sonra ne aldı` | `kaç tanesi geri döndü` | `elde tutma oranı` | 🔴 kohort **yok** (§5.1/20) | M-1 + kohort katmanı |

---

### 7.3 · Bu 50 threadin toplu okuması

| aile | thread | kök | öncelikli çıktı |
|---|---:|---|---|
| A | 10 | M-1 | *"(ölçü, boyut) çifti kaç turda küpe sığmıyor"* — **sayı** |
| B | 7 | M-2 | *"kaç turda niyet tam ama ölçü sorulmuş"* |
| C | 6 | M-3 | *"kaç türev ölçü ifadesi hiç kurulamıyor"* |
| D | 4 | M-4 | *"dönem sorusunun kaçı gereksizdi"* |
| E | 5 | M-5 | 🔴 *"kaç `◆ CUBE` rozetli yanlış sayı"* |
| F | 5 | M-6 | *"operatör sözlüğü farkı kaç turu Discovery'ye atıyor"* |
| G | 4 | M-7 | *"telemetri kaç turda parçalı"* |
| H | 4 | M-8 | *"ilan edilmiş sınırlar `adhoc` yerine beyan mı dönüyor"* |
| I | 5 | **M-9** | 🔴 *"pencere gerektiren kaç yemek sınıfı hiç sunulmuyor"* |
| **toplam** | **50** | | ~**146 curl turu** |

🔴 **Kontrol grupları (C5 · D3 · E5 · F5 · G4) atlanmamalı.** Onların görevi bir kusur
bulmak değil, **bir düzeltmenin çalışan bir şeyi bozmadığını** kanıtlamaktır. Bu belgenin
teşhislerinden biri yanlışsa, kontrol gruplarının kırmızıya dönmesi bunu ilk söyleyen şey
olacaktır.

---

## 8 · ÖNCELİK — hangi kök önce

| sıra | kök | neden bu sırada | maliyet | risk |
|---|---|---|---|---|
| **1** | **M-7** (telemetri normalizasyonu) | 🔴 **Tek satır** ve pusulayı düzeltiyor. Öteki her kökün *"ne kadar iyileşti"* ölçümü buna bağlı. **Önce pusula.** | çok düşük | çok düşük (idempotent) |
| **2** | **M-2** (ölçü rolü + varsayılan) | Canlı cevapsızların **görünür** bir dilimini doğrudan kapatıyor; menü dosyası işi, kod riski düşük | düşük–orta | düşük |
| **3** | **M-5** (toplanabilirlik beyanı) | 🔴 **Sessiz-yanlış** sınıfı — en pahalı hata türü. Kapı fail-closed olduğu için geç kalmak birikimli risk | orta | orta (derleme kapısı) |
| **4** | **M-4** (varsayılan dönem) | %13,7'lik kovayı hedefliyor; mekanizma (`veri_araligi`) **zaten var** | orta | orta (davranış değişikliği — bayrak şart) |
| **5** | **M-6** (operatör tek kaynak) | Bugün NO-OP; ama sağlayıcı değişince **canlıya çıkar**. Ucuz sigorta | düşük | düşük |
| **6** | **M-3** (türev ölçü) | Menüyü gerçekten **genişleten** madde; M-2'nin rol katmanına yaslanıyor | yüksek | orta |
| **7** | **M-9** (pencere katmanı) | 🔴 **Tek başına 6 yemek sınıfı açıyor** (kümülatif · hareketli ort. · grup-içi sıra · yüzdelik · `LAG`/`LEAD` · running balance). Motoru değiştirmez — `measure_having`/`ayrik_aylar` ile **aynı sarma deseni** | yüksek | orta |
| **8** | **M-1** (uyumlu boyut) | 🔴 **En büyük kazanç, en büyük değişiklik.** 5 modülü etkiliyor; tek boyut + tek şirket + bayrakla başlamalı | çok yüksek | yüksek |
| **9** | **M-8** (kaynak farkı beyanı) | M-1/M-3 indikten sonra anlamlı — önce menü, sonra menü farkı | düşük | düşük |

> ⚠ **Sıra bir tavsiyedir, bir karar değil.** Ölçüt şu olmalı: *bir turda 20 senaryo
> koşulup tüm düzeltmeler biriktirilecekse, hangi demet birlikte inebilir?* M-7+M-2+M-6
> **tek demette** inebilir (üçü de dar temaslı). **M-3+M-9 birlikte** inmeli — ikisi de
> aynı ölçü-cebri alanını açar ve ayrı inerlerse ikinci sahip doğar. **M-1 kendi
> demetinde** inmeli.

---

## 9 · BU RAPORUN DOĞRULANMAMIŞ YERLERİ

Dürüstlük kaydı — *"«YOK» iddiası en tehlikeli cümledir"* dersinin gereği:

1. **`R3`/`R6`/`R7`/`R8` hiç ateşlenmedi** — *"çalışmıyorlar"* **demedim**, *"sınanmadılar"*
   dedim. E ve F aileleri bunu ayıracak.
2. **`ne` vs `neq`** kod okumasıyla doğrulandı, **canlıda tetiklenmedi** — şema-kısıtlı
   kip bu sağlayıcıda NO-OP olduğu için tetiklenemezdi.
3. **`cube_router.py:1928` ve `:3350`** çağrı yerlerinin ne gönderdiğini **çağıranlarına
   kadar izlemedim**; M-7'nin çözümü bu izlemeyi **gereksiz** kıldığı için orada durdum.
4. **Korpus `rule` sağlayıcıyla koşuyor** — oradaki `CLARIFY`/`NOTE` oranları
   **kullanıcının gördüğü** oranlar değildir, **mutfağın kendi tavanıdır**. Garson devrede
   olduğunda bir kısmı kapanır; **hangi kısmı, ölçülmedi**.
5. **Menü sayıları `demo/packs`'ten**, derlenmiş MDL'den değil. Bir küp derlemede
   düşüyorsa bu rapor onu **fazla** saymış olur (`project_olcum_araci_bayat_sema`'nın ters
   yönü).
6. **`llm:*` %3,1 oranı düşük görünüyor ama yanıltıcıdır** — sistem Discovery'ye
   düşmeden **önce** çoğu turda pes ediyor. Discovery oranını *"mutfak eksikliği ölçüsü"*
   olarak okumak, ancak **cevapsız oran sıfıra yaklaştığında** geçerli olur.

---

## 10 · TEK CÜMLE

> **Aşçı yaptığı yemeği iyi yapıyor** (223 turda 3 boş sonuç, 1,66 sn) —
> **ama 24 yemek sınıfının 11'ini hiç yapamıyor, aynı malzeme 28 istasyonda ayrı
> duruyor, ve mutfak neyi yapamadığını yazdığı deftere yanlış yazıyor.**
>
> *Bir siparişi doğru almakla, doğru alıp yapabilmek aynı iş değildir; ve ikincisi
> dil öğrenerek değil, MUTFAĞI YENİDEN DÜZENLEYEREK çözülür.*

---

*Bu belge `belgeler/denetim/2026-08-07_CEVIRI-SOZLESMESI.md`'nin ekidir. Test ve döngü
kuralları o belgede tanımlıdır ve aynen yürürlüktedir.*
