# ÖNGÖRÜ KATMANI — ölçülmüş durum, hedef sistem ve şartname

> **Tarih:** 2026-08-13 · **Tür:** geliştiriciye teslim edilebilir şartname
> **Yöntem:** her iddia ya canlı sistemde ölçüldü ya kaynağı gösterildi. Ölçülmeyen
> hiçbir cümle *«öyledir»* diye yazılmadı; ölçülmeyenler **⊘ ölçülmedi** diye işaretli.
> **Kapsam:** `belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md` (ana plan) bu belgeyi
> kapsar; çelişkide **ana plan + `MIMARI.md`** kazanır, bu belge onların **eksik
> uygulanmış** kısmını sayar.

---

## §1 · TEK CÜMLE

Öngörü katmanının **motoru** büyük ölçüde yazılmış, **kabloları** takılmamıştır: cümle
üreteci, değer indeksi, pill motoru, makro reçetesi ve sıfır-LLM koşum uçları **vardır**;
ama tıklama LLM'e gider, üç dallı karar mantığı (`§28`) bağlanmamıştır, uç canlıda
**cevap vermemektedir** ve arayüz üç katmanı ayırt edilemez hâlde göstermektedir.

---

## §2 · BUGÜNKÜ DURUM — ölçümler

### 2.1 🔴 Uç canlıda ölü

```
GET /oneri?q=fire   →  42,9 sn asılı  →  HTTP 000 (curl 52: boş cevap)
docker logs | grep 'öneri indeksi ısındı'  →  satır YOK
```

Sebep ölçüldü: `oneri.terimler()` artık **422 aday · 1.359 görünüm** üretiyor (286'sı
boyut değeri). Daha önce **534 görünümde soğuk maliyet 24,8 sn** ölçülmüştü; görünüm
**2,5×** arttı ⟹ ilk istek, istek-zaman aşımını aşıyor.

⊙ Kök: `§41`'de eklenen **değer adayları** (`RAM-3` gibi) `§18.7`'nin **çok görünümlü
gömme** temsiline sokuldu. İki iyi karar çarpıştı ve ürünü durdurdu.

### 2.2 🔴 Tıklama LLM'e gidiyor — sistemin kuruluş amacına aykırı

```ts
// dima-frontend-demo-master/src/components/Besteci.tsx
onSec={onDeger}      // öngörüye TIKLAMA
onChange={onDeger}   // klavyeden HARF YAZMA   ← AYNI İŞLEYİCİ
```

`OneriSeridi.tsx:142` imzası `onSec: (etiket: string) => void`; `:249` ve `:313`
`onSec(a.metin)` çağırıyor. Yani tıklanan satırın taşıdığı **`cube_query · tur · cube ·
kimlik` atılıyor**, metin composer'a yazılıyor, `Enter` `/ask`'a gidiyor, route
tüketilmemiş token yüzünden *«şüpheli»* sayıp **garsona (LLM)** devrediyor.

⚠ Sıfır-LLM yolları **zaten var**: `postCube` (`POST /cube`) ve `/oneri/makro`
sarmalayıcıları `api-client.ts`'te mevcut; `:325` satırı bunun **nasıl** çalışması
gerektiğini yazıyor bile. **Sözleşme yazılmış, kablo takılmamış.**

### 2.3 🟡 Pill *«yok»* değil — **ayırt edilemiyor**

```
GET /oneri/pill?q=ram 3 neden
 → piller: ["kök neden kırılımı","hata sebebi kırılımı","kırılım"] · artılar: 4
```

Bu, kullanıcının *«pill yok»* dediği ekrandaki **alt sıranın birebir kendisidir**.
Bileşen bağlı (`Besteci.tsx:129 → PillSatiri`), bayrak açık (`oneri_katmani: beta`),
uç 200 dönüyor.

Sebep **görsel**: öngörü çipi `rounded border border-hairline px-2 py-0.5`, pill çipi
`border px-1.5 py-0.5` — iki katman neredeyse **aynı**, alt alta iki çip sırası hâlinde.

### 2.4 🔴 `§28`'in üç dalı hiç bağlanmamış

Plan şunu diyor:

```
route → SIRALI ADAY LİSTESİ
  marj ≥ eşik → 🟢 OTO-İCRA        pill = cevabın MAKBUZU     ⊘ LLM
  marj < eşik → 🔵 ADAY PILL'LERİ  route'un KENDİ kaybedenleri ⊘ LLM
  aday yok    → 🟣 GARSON TASLAĞI  onaya düşer                ✅ LLM
```

Ölçüm: `app/emin_miyim.py` **var** (saf karar motoru), tüketicileri `cube_router` ve
`value_index`; ama **`ask.py`'de `emin_miyim` çağrısı 0**, `ReportPanel.tsx`'te marj/üç
çıkış geçişi **0**, `features.yml`'de `marj_kapisi`/`oto_icra` bayrağı **yok**.
Planın kendi itirafı: *«bugün "iki aday var" durumu bile bir LLM turu ödetiyor.»*

### 2.5 Plan maddeleri — eksik olanlar

| faz | madde | durum | kanıt |
|---|---|---|---|
| 5.5 | sıklık önceliği (RRF'ye küçük katsayı) | 🔴 yok | `grep siklik\|frequency app/oneri.py` → 0 |
| 5.7 | `lab/oneri_indeksi.py` + tazelik damgası | 🔴 dosya yok | `ls` → yok (damga kodda var) |
| 5.9 | boş girdi: son bakılanlar · en çok sorulanlar · çekirdek 5 | 🟡 yarım | backend 0; yalnız FE'de *son bakılanlar* |
| 6.4 | **≤7 öneri** | 🔴 zorlanmıyor | `cumleler(limit=None)`, uç `limit` geçmiyor |
| 6.5 | ARIA combobox | 🔴 yok | `role="listbox\|option\|combobox"` → **0** |
| 6.6 | tuş | ✅ var | ekranda *«öneri: açık»* — fark edilmiyor |
| 6.7 | marj kapısının üç çıkışı ekranda | ⊘ ölçülmedi | — |
| **6 kapı** | `test_oneri_katmani_kural_b.py` | 🔴 **dosya yok** | fazın kendi kapısı yazılmamış |
| 7 | çapa · pill · makro | ⚠ plan *«DEMO DIŞI»* demişti, **yapıldı** | sıra dışına çıkıldı |
| 8.3 | `ε` karıştırma | 🔴 yok | `grep epsilon` → 0 |

### 2.6 Plan sözleşmesiyle çelişen arayüz

| plan | satır | uygulama |
|---|---|---|
| ARIA combobox · `↓↑ Enter Esc` · **≤7** · kaydırma yok | `1951` | yatay `flex-wrap` çip şeridi |
| *«adımlar **dikey**, yuvalar yatay; ikisi aynı şeritte **olmaz**»* | `1242` | ikisi aynı bölgede |
| *«tek adımlıysa tek satır pill, çok adımlıysa **dikey adım listesi**»* | `1560` | dikey adım listesi yok |
| pill'ler **dört başlıklı** (`ölçü · dönem · kırılım · tür`) | `285` | başlıksız düz dizi |
| `§6 Thread 1`: *«bu ay f»* → *«bu ay toplam fire (kg)»* | `320` | canlıda `fire (OEE)` |

---

## §3 · ARAŞTIRMA — sektör ne yapıyor, sayılarla

| ölçüt | sektör | kaynak |
|---|---|---|
| yanıt süresi | **50–100 ms**; Smart Compose *«ideally within 100ms»*, aksi hâlde gecikme fark edilir | System Design Sandbox · Google Research |
| gösterilen aday | **top 5** | System Design Sandbox |
| top-k | **çevrimdışı önceden**; her önek için sayaç (`n`, `ne`, `new`…), anlık hesap yok | System Design Sandbox |
| birincil sinyal | **popülerlik**; kişiselleştirme *«ancak taban doğruyken»* | System Design Sandbox |
| tazeleme | toplu, **dakika–saat** | System Design Sandbox |
| başarısızlık | *«**bayat öneri, boş açılır listeden iyidir**»* | System Design Sandbox |
| model seçimi | seq2seq *«kalitede iyiydi ama gecikme kısıtını **kat kat** aştı»* → **reddedildi**; ucuz melez + TPU ile **onlarca ms** | Google Research |
| NL-BI | ThoughtSpot: öneriler **arama token'ları + en popüler cevaplardan**, GPT ile yazılmış **tam sorular**, *«bir veri kaynağının tüm kullanıcıları aynı kümeyi görür»* | ThoughtSpot Docs |

**Bizim için üç sonuç:**

1. **Gecikme bir özellik değil bir kısıttır.** 42,9 sn ölçümümüz sektörün eşiğinin
   ~430 katı. Smart Compose'un seq2seq'i reddetmesiyle bizim değerleri gömücüye
   sokmamız **aynı hatanın** iki yüzü.
2. **Popülerlik olmadan sıralama yarımdır** — bizde hiç yok.
3. **Rakiplerin veremediği şey bizde var:** onların önerisi tıklanınca *arar*; bizimki
   tıklanınca **cevabı bilir** (`cube_query` taşır). Bu, kopyalanması en zor farktır ve
   şu an `onSec` satırında harcanmaktadır.

---

## §4 · HEDEF SİSTEM — ne hâle gelmeli

> **Kullanıcı yazarken, sistem onun cümlesini tamamlar; tamamladığı her cümle
> koşulabilir, koştuğunda sayıyı küp koyar, ve neye bakmadığını söyler.**

### 4.1 Dört katman

```
① ÖNEK KATMANI (trie · gömme YOK)                       hedef < 10 ms
   değerler (RAM-3, FERRARO SANFOR-1) + etiketler + sinonimler
   harf işi; anlam gerekmez
        │
② YUVA TAMAMLAMA (cümleyi kuran)                        hedef < 30 ms
   [dönem] [varlık] [kırılım] [ölçü] [fiil]
   eksik yuvayı doldur → TAM CÜMLE yaz → dolan her yuva bir PILL
        │
③ SIRALAMA (popülerlik + tazelik + çeşitlilik)          hedef < 10 ms
   küp başına ≤2, aynı ölçü ailesinden ≤1, toplam ≤7
        │
④ KARAR (§28 üç dal — SAYILABİLİR belirsizlikle)
   tüm token tüketildi ∧ tek sahip     → 🟢 oto-icra   (0 LLM)
   ≥2 küp ∨ ≥2 ölçü ailesi            → 🔵 aday pill  (0 LLM)
   aday yok ∨ tüketilmemiş token       → 🟣 garson     (LLM)
```

### 4.2 🔴 Marj yerine **sayılabilir belirsizlik** — gerekçeli sapma

Plan `§28`'in dalları **doğru**, ama kapısı olarak seçilen **skor marjı zayıftır**:

* Öneri skorları **RRF** ile üretiliyor (`1/(k+sıra)`); RRF'de 1. ile 2. arasındaki fark
  **her zaman aynıdır**, sistem ne kadar emin olursa olsun ⟹ marj **bilgi taşımaz**.
* `MIMARI.md`'nin kendi kuralı: *«kalibre edilmediği sürece o sayı bir güven değil bir
  **süstür**»* — `_RRF_K` de belgesinde *«kalibre edilmedi, seçildi»* diyor.

**Yerine:** kalibrasyon gerektirmeyen, **sayılabilir** olgular — ve hepsinin aracı
üründe **zaten var**:

| dal | koşul | mevcut araç |
|---|---|---|
| 🟢 | yazılan token'ların hepsi tüketildi **∧** ölçü tek sahipli | `partial_unknowns` · `measure_cube_candidates` |
| 🔵 | ölçü ≥2 küpte **∨** ≥2 farklı ölçü ailesi eşleşti | `measure_cube_candidates` (`fire` → `parti`+`oee`) |
| 🟣 | hiç aday yok **∨** tüketilmemiş token var | `route_supheli` · `eksiklik` |

⊙ Üstünlüğü: eşik yok, kalibrasyon yok, ve karar **beyan edilebilir** —
*«fire iki küpte tanımlı, ikisini de gösterdim»* bir insanın anlayacağı gerekçedir;
`0,07 marj` değildir. Bu, `§15.3`'ün *«onlar cevabı gösterir, biz cevabın sınırlarını»*
ilkesinin doğrudan uygulanışıdır.

⚠ `emin_miyim` **kaldırılmaz**: gerçekten ölçekli olan yerlerde (leksik harf farkı,
`marj=4`) kalır. Değişen, **öneri sıralamasında** ona güvenmemektir.

### 4.3 Arayüz — üç ayrı bölge

```
┌─ ÖNGÖRÜ (combobox · dikey · ≤7 · kaydırma yok) ────────────┐
│ bu ay RAM-3'ün OEE'si ne kadar?              oee · yeni    │
│ RAM-3'ün OEE'si neden bu seviyede?           makro · neden │
│ bu ay makineye göre fire ne kadar?           parti · yeni  │
└────────────────────────────────────────────────────────────┘
┌─ PILL (dört başlık) ───────────────────────────────────────┐
│ ölçü: [OEE]   dönem: [bu ay]   kırılım: [makine]  tür: [—] │
│ + ölçü   + kırılım   + dönem   + adım                      │
└────────────────────────────────────────────────────────────┘
┌─ PLAN ADIMLARI (yalnız çok adımlıysa · DİKEY) ─────────────┐
│ 1 SORGU  · oee · bu ay                                     │
│ 2 KIR    · makine                                          │
│ 3 ANLAT  · $1,$2                                           │
└────────────────────────────────────────────────────────────┘
```

Ek: **hayalet metin** — en iyi adayın devamı girdinin içinde gri, `Tab` kabul, `↓`
listeye iner. ⚠ Yalnız ① katmanından beslenmeli; gömücüye bağlanırsa Smart Compose'un
reddettiği gecikmeye düşer.

### 4.4 Seçim ≠ gönderim

Bir öngörü seçilince **koşmaz**: pill'lere dönüşür, kullanıcı `+` ile ikinci adımı
ekleyebilir, `Enter` **onaydır**. Koşum anında yol:

```
o.cube_query varsa      → POST /cube            (0 LLM)
o.tur === "neden"       → POST /oneri/makro     (0 LLM · 5 determinist adım)
ikisi de yoksa          → POST /ask             (yalnız burada LLM olabilir)
```

---

## §5 · İŞ KALEMLERİ — sıralı, dosya dosya, kabul ölçütlü

### İŞ 1 · 🔴 Ucu ayağa kaldır *(engelleyici — ürün şu an çalışmıyor)*

* **Dosya:** `backend/app/oneri.py`
* **Yap:** değer adaylarını **vektör ayağından çıkar**; yalnız leksik ayakta arat.
  (`Aday.kip` ya da ayrı bir havuz — `_vektor_sira` değer adaylarını görmesin.)
* **Kabul:** `GET /oneri?q=fire` **p95 < 300 ms** *(nihai hedef `< 100 ms`)*; ısınma
  logu **görünür**; `Recall@3` tabanı düşmemiş.
* **Kapı:** `tests/test_oneri_gorunum_tavani.py` *(yeni)* — görünüm sayısı ilan edilen
  tavanı aşarsa **kırmızı**. *Bugünkü 1.359 sessizce büyüdü; bir daha sessiz büyümesin.*

### İŞ 2 · 🔴 Tıklama sıfır-LLM

* **Dosyalar:** `OneriSeridi.tsx` (imza) · `Besteci.tsx` · `ReportPanel.tsx` ·
  `lib/api-client.ts` *(sarmalayıcılar hazır)*
* **Yap:** `onSec: (o: Oneri) => void`; `§4.4`'teki üç dal.
* **Kabul:** öngörü tıklamasında ağ sekmesinde `/ask` **görünmez**; `/cube` ya da
  `/oneri/makro` görünür; cevap süresi **< 300 ms**.
* **Kapı:** `test_ongoru_tiklamasi_llm_cagirmaz` — mutasyonla kanıtlanır
  (`onSec`'i metne düşür → kırmızı).

### İŞ 3 · Arayüz — üç bölge + combobox

* **Dosyalar:** `OneriSeridi.tsx` · `PillSatiri.tsx` · yeni `PlanAdimlari.tsx`
* **Yap:** `role="combobox"/"listbox"/"option"`, `aria-activedescendant`, ≤7, kaydırma
  yok; pill satırı **dört başlıklı**; çok adımlı planlar **dikey**.
* **Kabul:** `§40`'ın klavye sözleşmesi (`↓↑ Enter Esc`) ekran okuyucuda çalışır; üç
  bölge görsel olarak **ayırt edilir**; plan `1242`'nin *«ikisi aynı şeritte olmaz»*
  kuralı sağlanır.

### İŞ 4 · `§28` üç dal — **sayılabilir belirsizlikle**

* **Dosyalar:** `app/routers/ask.py` · `app/cube_router.py` *(mevcut araçlar çağrılır)*
* **Yap:** `§4.2` tablosundaki üç koşul; bayrak `karar_uc_dal` *(yeni, `beta`)*.
* **Kabul:** `KURAL B` — bayrak kapalıyken davranış **bayt aynı**; açıkken *«iki aday»*
  durumu **LLM turu ödetmez**.
* **Kapı:** `test_uc_dal_karari.py` — üç dalın üçü de **ayrı** ölçülür; 🔵 dalında
  `llm.select_cube` **çağrılmadığı** doğrulanır.

### İŞ 5 · Önek değişmezi *(öngörünün tanımı)*

* **Dosya:** `app/oneri_cumle.py`
* **Yap:** üretilen cümle, kullanıcının yazdığı token'ları **sırayla ve değişmeden**
  içermeli; içermiyorsa öneri değil *«bunu mu demek istedin»* bandına düşer.
* **Kabul:** `q=ram 3` → dönen her satırda `RAM 3`/`RAM-3` **geçer**; `ramak kala`
  **geçmez**.
* **Kapı:** `test_ongoru_yazilani_icerir.py`.

### İŞ 6 · Kütük döngüsü *(sistem kullanımdan öğrensin)*

* **Dosyalar:** `app/oneri.py` (sıklık) · `POST /oneri/tik` *(var)* · `lab/sozluk_hasadi.py`
* **Yap:** `5.5` sıklık katsayısı · `8.3` `ε` karıştırma · *«yazdı, tıklamadı»* negatifi.
* **Kabul:** tıklanma oranı ölçülebilir; 1. sıra kendini beslemiyor.
* **Kapı:** `test_hasat_konum_yanliligi.py` *(var — genişletilir)*.

### İŞ 7 · Eksik plan borçları

`5.7` `lab/oneri_indeksi.py` (üreteç + tazelik damgası) · `5.9` boş girdi (çekirdek 5) ·
`6.4` `≤7` sunucu tarafında · **`test_oneri_katmani_kural_b.py`** *(fazın hiç yazılmamış
kapısı)*.

---

## §6 · BAŞARI METRİKLERİ — eşikler ve nasıl ölçülür

| # | metrik | eşik | nasıl | bugün |
|---|---|---|---|---|
| M1 | `p95(GET /oneri)` | **< 100 ms** *(ara hedef 300)* | `lab/oneri_p95.py` | 🔴 42.900 ms |
| M2 | soğuk ilk istek | **< 1.500 ms** | ısınma sonrası ilk çağrı | 🔴 ölçülemiyor |
| M3 | `Recall@3` (öngörü doğru alanı ilk 3'te) | **≥ %85** | `lab/oneri_olcum.py --vektor` | 🟡 leksik %75,7 · payda 37 |
| M4 | **öngörü tıklamasında LLM çağrısı** | **= 0** | ağ sekmesi + `test_ongoru_tiklamasi_llm_cagirmaz` | 🔴 her tıklama |
| M5 | dönen satırların **tam cümle** oranı | **%100** | `test_ongoru_tam_cumle` | 🟡 kodda ✅, canlıda ⊘ |
| M6 | yazılanı **içeren** öngörü oranı | **%100** | `test_ongoru_yazilani_icerir` | 🔴 kapı yok |
| M7 | *«iki aday»* durumunda LLM turu | **= 0** | `test_uc_dal_karari` | 🔴 her seferinde |
| M8 | öneri sayısı | **≤ 7** | uç yanıtı | 🔴 sınırsız |
| M9 | görünüm sayısı (indeks boyu) | **ilan edilen tavanın altında** | `test_oneri_gorunum_tavani` | 🔴 1.359, tavan yok |
| M10 | tıklama kabul oranı *(tıklanan / gösterilen)* | **taban ölçülür, sonra artış** | `interaction_log` | ⊘ ölçülmedi |
| M11 | boş açılır liste oranı | **< %5** *(bayat sunmak yeğdir)* | uç yanıtı | ⊘ ölçülmedi |
| M12 | korpus doğru-cube | **≥ %95,6** *(gerileme yok)* | `lab/nl_corpus.py --kapi` | ✅ %95,6 |

---

## §7 · ŞARTLAR — pazarlık dışı

1. **Sayıyı küp koyar.** Öngörü metni ne derse desin, sayıyı `cube_query` üretir.
2. **Cümlede geçen dönem, sorguda da vardır.** *(«bu ay» yazıp dönemsiz koşmak yasak.)*
3. **`KURAL B`:** bayrak kapalıyken davranış **bayt bayt** bugünküyle aynı.
4. **`KAT-1`:** bir kural tek yerde savunulur; ikinci kopya yazılmaz, mevcut **çağrılır**
   (`ek.py` morfoloji · `value_index` eşleşme · `makro.py` reçete · `emin_miyim` karar).
5. **`E-8`:** sıcak yolda seri ikinci LLM turu yok.
6. **`ADR-0020`:** sessiz yutma yok — düşen her yol **loglanır**.
7. **Türkçe morfoloji `ek.py`'nindir**; öneri katmanında ek kuralı **yazılmaz**.
8. **Yetki sıralamadan önce** (`katman_b.karar`) — öneri listesi bir **envanterdir**.
9. **Kapısı olmayan faz bitmiş sayılmaz.** Her iş kalemi bir kapı doğurur.
10. **Beyan kültürü:** ne yaptığını söyle *(«fire iki küpte tanımlı»)*; ölçemediğini
    söyleme.

---

## §8 · REDDEDİLENLER — ve nedeni

| seçenek | neden reddedildi |
|---|---|
| Değerleri de gömmek (bugünkü hâl) | ölçüldü: **1.359 görünüm**, uç **42,9 sn** → ürün durdu. Smart Compose'un seq2seq'i reddetme gerekçesiyle aynı |
| Skor marjını güven sanmak | RRF'de marj **sabittir**; `MIMARI`: kalibre edilmemiş sayı **süstür** |
| Mutlak kosinüs eşiği | `FAZ 0` ölçtü: gürültü kelimesi **0,851** aldı |
| Öneriyi LLM'e yazdırmak (ThoughtSpot deseni) | bizim üstünlüğümüz **determinizm**; LLM yalnız 🟣 dalında |
| Çipleri koruyup listeye geçmemek | plan `1951` **combobox** diyor; ve kullanıcı ekranda reddetti |
| `oneriler` boşken ham `adaylar` basmak | alan adı listesi bir **öngörü değildir** — `§42`'de kapatıldı |

---

## §9 · YAPILAN — bu tura kadar teslim edilenler

`§40` tam cümle üretimi · `§41` boyut değerleri indekste + `_kapsam` ile varlıklı cümle ·
`§42` çapalı bant düzeltmesi + ham-etiket düşüşünün kapatılması · `§37` `_uuid_or_none`
tek sahip · `§38` `_norm` devri + NFD ayrışmasının kapısı · `§34` beyanın tamamlanması ·
`SERVER_COMMANDS.md`'nin gerçeğe göre yeniden yazımı.

⚠ Bunların **cümle üretimi** kısmı `s13+` imajlarıyla yayımlandı; ama `§2.1`'deki
gecikme kusuru **aynı demette** doğdu. *Bir özelliği yayımlamak, onu çalışır kılmaz.*

---

## §10 · KAYNAKLAR

* System Design Sandbox — *Search Autocomplete (Typeahead)*:
  `https://www.systemdesignsandbox.com/learn/design-autocomplete`
* Google Research — *Smart Compose: Using Neural Networks to Help Write Emails*:
  `https://research.google/blog/smart-compose-using-neural-networks-to-help-write-emails/`
* Google Research — *Gmail Smart Compose: Real-Time Assisted Writing*:
  `https://research.google/pubs/gmail-smart-compose-real-time-assisted-writing/`
* ThoughtSpot Docs — *AI-suggested searches*:
  `https://docs.thoughtspot.com/cloud/26.7.0.cl/search-ai-suggested`

<sub>⚠ Bu belgedeki canlı ölçümler `dima-oneri-8002` konteynerinde alındı; ölçüm sırasında
imaj `s12 → s17` arasında ilerledi (paralel yayım). Sayılar **11:30–11:55** aralığının
fotoğrafıdır.</sub>
