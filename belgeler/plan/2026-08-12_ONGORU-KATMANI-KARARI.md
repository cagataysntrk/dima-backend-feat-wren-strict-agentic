# ÖNGÖRÜ KATMANI — *route ve garson, KARAR VERİCİ olmaktan çıkıp TAHMİNCİ oluyor*

> **Tarih:** 2026-08-12 · **Durum:** 🔵 KARAR TASLAĞI — ölçüm ön koşuluna bağlı
> **Sahibi:** DİMA v1 · **Otorite:** çelişkide `backend/MIMARI.md` kazanır
> **Ön koşul:** `§13.1` Türkçe gömme isabeti ölçülmeden **uygulanmaz**

---

## §0 · TEK CÜMLE

> Cevaplama merdiveninin **6. basamağının çıktısı** bir `CubeQuery` **kararı** olmaktan
> çıkıp bir `CubeQuery` **aday listesi** hâline gelir; kararı **kullanıcı bir tıkla**
> verir. Merdiven, guard'lar, makbuz, beyan kültürü **aynen kalır**.

Bu bir mimari değişiklik değil, bir **rol değişikliğidir**. Ve emsali bu deponun kendi
kararında yazılı (`MIMARI.md §2.0`, orkestratör):

> *«Bir yeteneği bir **basamak** olarak eklemek karar yüzeyini büyütür; bir **çıktı biçimi**
> olarak eklemek büyütmez.»*

Orada `CubeQuery → plan` oldu. Burada `CubeQuery → CubeQuery listesi` oluyor.
**Yeni basamak yok. Yeni karar yüzeyi yok.**

---

## §1 · BUGÜN NEREDEYİZ — ölçülmüş durum

### 1.1 Sayılar *(2026-08-12, kendi koşumlarım)*

```
KATALOG        23 küp · 136 ölçü · 816 ayrık terim
KORPUS         14.957 tur · doğru-cube %95,6 (taban %94,4 ✅)
               semantik vaka 558/591 = %94,4 (taban %93,5 ✅)
               🔴 cevapsız 2.946/14.957 = %19,7
ERİŞİM         boyahane %73 (t.69 ✅) · atiksan %54 ❌ · gulteks %53 ❌ · gitas %58 (t.72 ❌)
GECİKME        deterministik yol 145–434 ms · garson (k=3) 98 s¹ · Discovery 12,5 s
PLAN ONARIMI   denendi 16 · onarıldı 1 · düştü 3 → %25  ⚠ payda 16
BORÇ           yön beyansız 68/136 · çıplak alan 1 · «müşteri» 9 küpte 3 adla
YÜZEY          HTTP ucu 77 (8 gerekçeli yetim) · `app/` 138 modül (4 yetim) · MCP 29 araç
```

¹ *tek örnek, ortalama değil.*

### 1.2 Ölçülen ZIT hareket — ve teşhisin çekirdeği

```
        doğruluk  ▲ 94,4 ──────────→ 95,6      (+1,2 puan)
        erişim    ▼ 69   ──────────→ 54        (−15 puan)
```

🔴 **Sistem daha az TAHMİN ediyor, daha çok SORUYOR.** Bu tesadüf değil, bu oturumun
netleştirme çalışmalarının doğrudan sonucu.

Kırılım — ayırt edici tek kalem `CLARIFY:dönem`:

| şirket | `OK` | `CLARIFY:konu` | `CLARIFY:dönem` |
|---|---|---|---|
| boyahane ✅ | **%69** | %11 | **—** |
| atiksan ❌ | %51 | %11 | **%9** |
| gulteks ❌ | %50 | %11 | **%9** |
| gitas ❌ | %54 | %8 | **%9** |

⊙ `CLARIFY:konu` **dördünde de ~%11** → konu netleştirmesi bir gerileme değil, **taban
davranışı**. Yani sistem trafiğin **onda birinde** zaten *«hangisini kastettin?»* diyor.

🔴 **Ve planın kendi ölçütü bunu reddediyor:**
> *«Kapsam kaybı vs kapanan sessiz-yanlış. **Kayıp > kazanç ise açılmaz.**»*

Bugün: kazanç **+1,2 puan**, kayıp **~15 puan**. **Kayıp kazançtan büyük.**

### 1.3 Ölçülmüş sessiz-yanlış örnekleri *(bu oturum)*

| girdi | olan | olması gereken |
|---|---|---|
| *«bir **de** gecikme ekle»* | `dE!` sinonimi eşleşti → **yanlış ölçü eklendi** | ek çözümlemesi, ölçü değil |
| *«renk **grubuna** göre fire»* | personel **yaş grubu**na gitti | renk grubu |
| *«RAM-3 neden düşük»* | **cevapsız** | kıyas temeli sorulmalıydı |
| *«diğerlerine göre»* eklenince | ✅ cevaplandı | ilkiyle **aynı** cevap olmalıydı |

> 🔴 Dördü de **aynı sınıf**: route bir **karar** verdi ve yanıldı; kullanıcı fark etmedi.

---

## §2 · TEŞHİS — kusurun ortak kökü

```
BUGÜN                                    KUSUR SINIFI
─────────────────────────────────────    ────────────────────────
route()  "grubu = yas_grubu"  ── İCRA →  🔴 SESSİZ-YANLIŞ
garson   route çekilince aynı KARAR      🔴 SESSİZ-YANLIŞ + 98 s
                                          + ölçülemez (korpus route'u ölçer)
```

Kök: **karar vericinin yanılması sessizdir.** Ve sessiz olduğu için:
- düzeltmenin tek yolu **yeni kural yazmak** → route büyür (tredmill),
- hangi sinonimin eksik olduğu **bilinemez** → sözlük elle beslenir,
- garsonun kazancı **ölçülemez** → bayrak kararları kanıtla değil sezgiyle verilir.

> *Bir sistemi ölçemiyorsan geliştirebilirsin ama **iyileştiremezsin**: iyileştirme,
> iki ölçüm arasındaki farktır.*

---

## §3 · KARAR

### 3.1 Rol değişikliği

```
                ÖNCE                              SONRA
route()   →  KARAR VERİR, İCRA EDER          →  ADAY SIRALAR (icra etmez)
garson    →  route çekilince KARAR VERİR     →  aday listesini ZENGİNLEŞTİRİR
                                                 + kademe ③'te PLAN TASLAĞI çizer
kullanıcı →  cevabı alır                     →  🔴 KARARI VERİR (bir tık)
küp       →  seçileni koşar                  →  DEĞİŞMEZ
LLM       →  anlatım + Discovery             →  anlatım + kademe ③ + fallback
```

### 3.2 Kusur sınıfı değişimi — asıl kazanç

| | bugün | öngörü kipinde |
|---|---|---|
| yanlış eşleşme | **sessiz-yanlış** (sayı yanlış, kullanıcı bilmez) | **kötü sıralama** (kullanıcı 2. satırı tıklar) |
| düzeltme yolu | **yeni kural yaz** (route büyür) | **ağırlık ayarla** (route büyümez) |
| ölçüm | ⊘ *«doğru cevap»* bilinmiyor | ✅ **Recall@3 · MRR · kabul oranı** |

> *Sessiz bir hatayı gürültülü bir hataya çevirmek hatayı yok etmez — ama onu **ölçülebilir
> ve katlanılabilir** yapar.*

### 3.3 Arayüz: MENÜ DEĞİL, TAMAMLAMA

🔴 Bu ayrım kozmetik değil **mimari**:

| | menü | **tamamlama** ✅ |
|---|---|---|
| serbest metin | **kapalı** — listede yoksa yok | **açık** — öneriler görmezden gelinebilir |
| başarısızlık | **çıkmaz sokak** | kullanıcı yazmaya devam eder |
| örtük mesaj | *«ancak bunları yapabilirim»* | *«ne diyeceğini biliyorum»* |
| `KURAL B` | ⊘ alternatifsiz yol | ✅ **bayrak kapalı = bugünkü davranış** |

Menü, bu belgenin en ağır trade-off'unu (**karar yükünün kullanıcıya geçmesi**) yaratırdı.
Tamamlama yaratmıyor: **kullanıcı seçmek zorunda değil.**

---

## §4 · MİMARİ DEĞİŞİKLİK — ne kadar küçük

### 4.1 Merdiven — önce ve sonra

```
ÖNCE                                 SONRA
──────────────────────────           ──────────────────────────
1  auth / tenant                     1  auth / tenant            (aynı)
2  bağlam                            2  bağlam                   (aynı)
3  sosyal / meta                     3  sosyal / meta            (aynı)
4  takip sınıflandırma               4  takip sınıflandırma      (aynı)
5  VQR                               5  VQR                      (aynı)
6  route → CubeQuery ──┐             6  route → CubeQuery[]  ◄── TEK DEĞİŞEN SATIR
   garson → CubeQuery ─┤                garson → CubeQuery[] zenginleştirir
                       │                🔴 kullanıcı seçer ────┐
7  parse_cube_query ◄──┘             7  parse_cube_query ◄──────┘  (aynı beyaz liste)
8  compose / motor                   8  compose / motor          (aynı)
9  guard · makbuz · beyan            9  guard · makbuz · beyan   (aynı)
10 Discovery (son çare)              10 Discovery (son çare)     (aynı)
```

### 4.2 `MIMARI.md` diff'i — bir paragraf

> **§2.0'a eklenecek:** *Basamak 6'nın çıktısı bir `CubeQuery` **ya da** bir `CubeQuery`
> **aday listesi** olabilir. Liste kipinde kararı kullanıcı verir; seçilen aday aynı
> `parse_cube_query` beyaz listesinden geçer. `oneri_katmani` bayrağı kapalıyken davranış
> bugünküyle **bayt bayt** aynıdır (`KURAL B`).*

### 4.3 Ama bayrağın arkasında BEDAVA OLMAYAN üç şey

| # | ne | neden bedava değil |
|---|---|---|
| ① | **vektörel indeks** (şirket başına) | üretim + **tazeleme yaşam döngüsü** (⚠ `demo/wren-project` tuzağı) |
| ② | **kısmi girdi sıralayıcısı** | `route()` **tam cümle** için yazıldı; önek/yarım kelime **yeni iş**, gecikme bütçeli |
| ③ | **öneri ucu + ön uç şeridi** | `§G` kapısı: tüketicisiz uç **kırmızı** verir → ikisi **aynı demette** |

> **Mimariye bir bayrak; işletmeye bir artefakt.**

---

## §5 · ARAYÜZ — üç mekanizma

### 5.1 Görünür ÇAPA — bağlam gizli durum olmaktan çıkar

```
┌─ 📌 RAM-3 · toplam_fire_kg · bu ay              [✕ bağlamı bırak] ─┐
└────────────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────┐
  │ fire ki▌                                             │
  └──────────────────────────────────────────────────────┘
   ↳ BU RAPOR ÜZERİNDE
     • RAM-3'ün fire oranı — bu ay
     • fire ekle (aynı kırılım · aynı dönem)
     • fire neden bu seviyede?                    ← makro
   ↳ YENİ KONU
     • makineye göre toplam fire (kg) — bu ay
```

🔴 Kayıtlı ilkeye **birebir** uyar: *bir thread/UI gruplaması semantik bağlam sınırı
taşımaz; yeni bağlam yalnız **açık kullanıcı eylemiyle** doğar.*

⊙ Çapa aynı zamanda `§D4` checkpoint'idir: her karttan *«buradan devam et»* → çapa o karta
geçer. **Bedava**, çünkü `POST /cube` bir `cube_query`'yi **sıfır LLM** ile koşuyor.

### 5.2 PILL satırı — `Niyet` nesnesinin GÖRÜNÜR HÂLİ

`app/niyet.py::Niyet` alanları ↔ pill'ler **birebir**:

```
   olcu_adaylari      donemler        kirilimlar       turler
        │                │                │               │
   [toplam_fire_kg] [bu ay]    [makineye göre]    [+ ölçü ▾]
```

🔴 **Yeni model kurulmuyor, mevcut model çiziliyor.** `frozen` bir okumadır, pill'ler onu
üretir — ikinci bir temsil doğmaz (`KAT-1`).

⚠ **`+` TİPLİ OLMALI.** Tek bir `+` üç ayrı anlama gelir ve bu deponun bir numaralı
tuzağıdır (*«göre/bazında»* üç anlamlıydı, **üç kez** ısırdı):

| `+` ne demek | sonuç |
|---|---|
| aynı sorguya **ölçü** ekle | **tek** `cube_query`, iki ölçü |
| **adım** ekle | sıralı **plan** |
| **ayrı rapor** | **iki** kart |

→ `[+ ölçü] [+ kırılım] [+ dönem] [+ adım]` — dördü de **kapalı gramerin alanları**.

### 5.3 Pill CANLI doğrulanır — imkânsız soru sorulamaz

Doğrulama **zaten var** (`dogrula` koşmadan önce · `compose` grain ihlali). Eksik olan onu
pill'e taşımak: geçersiz kombinasyonda pill **kırmızıya döner ve nedenini söyler** — koşmadan.

> *«Sayıyı küp koyar»* ilkesinin arayüz karşılığı: **imkânsız soru sorulamaz hâle gelir.**

---

## §6 · BEŞ THREAD — basitten karmaşığa

### Thread 1 · Tek tur · sıfır LLM

```
yazar:      "bu ay f"
öneriler:   • bu ay toplam fire (kg)     ← tıkladı
            • bu ay fire oranı
            • bu ay toplam ciro
pill:       [toplam_fire_kg] [bu ay]
Enter    →  cube_query koşar · 34 ms · 0 token
cevap:      "Bu ay toplam fire 12.480 kg." + makbuz + grafik
chip'ler:   [makineye göre] [geçen aya göre] [neden bu seviyede?]
```

✅ **Çalışır.** 🔴 **Kırılma:** boş girdide ne gösterilir? → *son bakılanlar · en çok
sorulanlar · dikeyin çekirdek 5 ölçüsü*. ⚠ Elle yazılmış *«örnek sorular»* listesi **olmaz** — bayatlar.

### Thread 2 · Bağlamsal zincir · makro

```
tur 1  "bu ay fire"                → 12.480 kg          [çapa: fire · bu ay]
tur 2  chip [makineye göre]        → 9 makine · RAM-3 en yüksek (3.100 kg)
tur 3  chip [neden bu seviyede?]   → 🔴 MAKRO — 4 adım, TEK tık
       └ ayrıştır → akran → sürükleyen → derinleş
       "RAM-3 sürüklüyor (%25 pay). Akranlarına göre +%40.
        Vardiya kırılımında gece vardiyası öne çıkıyor."
tur 4  "gece vardiyasında son 3 ay" → çapa taşındı, dönem değişti
tur 5  chip [normal mi?]           → dönemsel kıyas + sinyal
```

✅ **En güçlü senaryo.** 5 tur, **0 LLM**. Ölçülen kusur *«RAM-3 neden düşük → cevapsız»*
**doğmuyor**: kıyas temeli bir **chip**, cümleden çıkarılan tahmin değil.

🔴 **Kırılma:** makroyu **kim** tetikliyor? Yanlış tetikleme = gürültü (`§101.1`:
yanlış-pozitif kusurdan pahalıdır). Ölçüt **yapısal** olmalı (*tek boyutta belirgin
sürükleyen var mı*) — ve bu **zaten hesaplanıyor**.

### Thread 3 · Bağlam kopuşu ve geri dönüş

```
tur 1-2  fire zinciri                      [çapa: fire · RAM-3 · bu ay]
tur 3    "ciro"                             ← başka küp
         ↳ BU RAPOR ÜZERİNDE
             • RAM-3'ün partilerinin cirosu   ⚠ JOIN gerektirir
           ↳ YENİ KONU
             • bu ay toplam ciro              ← tıkladı → çapa DÜŞTÜ
tur 4    "müşteriye göre"                   [çapa: ciro · bu ay]
tur 5    tur 2 kartında [buradan devam et]  → çapa GERİ DÖNDÜ · 0 LLM
tur 6    "vardiya kırılımı"                 → fire zinciri kaldığı yerden
```

✅ **Yapısal olarak üstün.** Kopuş **tahmin edilmiyor**, iki şerit gösteriliyor.

🔴 **İki kırılma:**
1. *«BU RAPOR ÜZERİNDE»* önerisi **JOIN gerektiriyor** ve JOIN planlayıcı yasağı var.
   **Kural:** sunulan her öneri, sunulmadan önce **temsil edilebilir** olmalı 🆈.
2. Uzun thread'de geri dönüş **kaydırma** gerektirir → çapa geçmişi ayrı şerit:
   `[fire·RAM-3] [ciro] ←`

### Thread 4 · Belirsizlik · yazım · morfoloji · çok sahiplilik

```
tur 1  "müşteri bazında hasıl"
       ⚠ İKİ belirsizlik birden:
         · "hasıl"   → yazım/kök → vektörel yakınlık → toplam_ciro
         · "müşteri" → DOKUZ küpte ÜÇ ayrı adla
       öneriler:
         • müşteriye göre toplam ciro     (satış · cari_unvan)     ← tıkladı
         • müşteriye göre toplam ciro     (ticaret · musteri_adi)  ⚠ AYNI ETİKET
         • müşteriye göre tahsilat        (cari · musteri)
       🟢 tıklama bir ETİKET: (ham="hasıl" → toplam_ciro) aday kuyruğuna düştü
tur 2  "geçen yılla kıyasla"              → YoY
tur 3  "en kötüsü hangisi"
       🔴 ort_oee YÖN BEYANSIZ (68/136) → "en kötü" TANIMSIZ
       "«En kötü» için yön beyanı yok — en YÜKSEK mi en DÜŞÜK mü?"  [↑] [↓]
```

◐ **Çalışır ama katalog borcunu ÖNE ÇEKER.** Yazım hatası **kendiliğinden** çözülüyor —
tredmill'den bir kurtuluş.

🔴 **İki kırılma:**
1. **Aynı etiketli iki öneri** — kullanıcı ayırt edemez. Katalog tutarsızlığı görünür ama
   çözülmez. Etiket eki `(satış)`/`(ticaret)` kullanıcıya bir şey söylemiyorsa faydasız.
2. **68/136** → üstünlük sorularının **yarısı** bir ek tık istiyor.

### Thread 5 · Bileşik agentic istem — EN KIRILGAN

```
yazar (tek seferde, uzun):
  "son çeyrekte fire oranı artan makineleri bul, her biri için vardiya
   kırılımında neden arttığını çıkar ve müdüre 3 cümlelik özet hazırla"

öneri katmanı: ⊘ kısmi eşleşme yok — bu bir CÜMLE değil bir PLAN
→ garson (kademe ③) plan yazar
→ 🔴 plan KOŞMUYOR, PILL SATIRI olarak gösteriliyor:

   1 [SIRALA]    fire_orani ↑ · makine · son çeyrek       ✅
   2 [AYRIŞTIR]  $1 her makine → vardiya                  ✅
   3 [ÖZETLE]    $2 → 3 cümle · "müdür tonu"              ⚠ tanımsız parametre
                                        [düzenle] [koş] [iptal]
→ 1-2 DETERMİNİSTİK · 3 anlatım katmanı (LLM, guard'lı)
→ bütçe görünür: 3 adım/12 · 2 sorgu/12 · kalan
```

◐ **Öneri katmanı burada neredeyse hiç yardım etmiyor.** Kazanç **plan önizlemesi**:
bugün plan yazılıp **koşuyor**, 7. adımda çökerse kullanıcı **sonda** öğreniyor
(`onarım tutma %25`, payda 16). Pill kipinde plan **koşmadan** görünür ve düzeltilir.

> *Bir planı koşmadan önce görünür yapmak, onu onarmaktan ucuzdur.*

🔴 **Üç kırılma:**
1. **Uzun cümlede öneri gürültü yapar** → girdi eşiği geçince (≈8 kelime / fiil tespiti)
   öneri şeridi **sönmeli**.
2. **Garson kritik yolda.** *«Intent'i sonraki faza bırakalım»* bu thread'de **mümkün
   değil** → ya senaryo sınıfı **kapsam dışı ilan edilir**, ya garson ilk günden gelir.
3. **Serbest parametreli fiiller** (`ÖZETLE`·`PAYLAŞ`·`ZAMANLA`) katalogdan türemiyor →
   pill'in kesinliği orada biter.

### 6.6 Thread karnesi

| # | senaryo | çalışır mı | asıl kazanç | asıl kırılma |
|---|---|---|---|---|
| 1 | tek tur | ✅ | ölçü seçimi kesinleşir | boş girdi |
| 2 | bağlamsal zincir | ✅ **bugünden iyi** | kıyas temeli chip olur | makro tetikleyicisi |
| 3 | kopuş / dönüş | ✅ **yapısal üstün** | bağlam görünür nesne | temsil edilemeyen öneri |
| 4 | belirsizlik | ◐ | tıklama = etiket | aynı etiketli öneri · 68/136 |
| 5 | bileşik agentic | ◐ **kırılgan** | plan koşmadan görünür | garson kritik yolda |

---

## §7 · ÜÇ KADEME — ve karışmamalılar

| # | ne | nasıl sunulur | LLM |
|---|---|---|---|
| **①** | tek adım | doğrudan öneri (bugünkü `CubeQuery`) | ⊘ |
| **②** | **adlandırılmış makro** | **tek öneri**, arkasında N deterministik adım | ⊘ |
| **③** | özgün besteleme | garson **taslak çizer**, kullanıcı onaylar | ✅ |

🔴 **Asıl cevap ②.** Kök-neden zaten böyle: `ayrıştır → akran → sürükleyen → derinleş` —
dört adım, **tek** kullanıcı eylemi. Kapsamlı işlerin çoğu **sonsuz kombinasyon değil,
sayılı reçete**: gelir tablosu · YoY · pareto · kohort · pano.

⚠ **Makro enflasyonu riski:** her kombinasyon adlandırılırsa uzayı **saymış** olursun.
**Kural: bir makro adını olasılıkla değil SIKLIKLA kazanır** — kullanım kaydından ölçülür.

⊙ Plan da **bestelenir, sayılmaz**: kapalı fiil kümesi (**15 fiil · 31 ilkel**,
`Arac.fiil`, içe aktarmada doğrulanıyor) bir **plan grameridir**.

---

## §8 · SÖZLÜK — girdiden ÇIKTIYA

### 8.1 Karıştırılan iki şey

| | **route kuralı** | **sinonim** |
|---|---|---|
| nerede | kod (`cube_router`) | katalog (`cube_synonyms.yml`, 816 terim) |
| bugün | 🔴 **büyüyor** — her ıskalama yeni kural | elle besleniyor |
| öngörü kipinde | 🟢 **büyümesi DURUR** | 🟢 **tıklamadan HASAT EDİLİR** |

⊙ Deponun yasağı zaten var (*«route'a dil kuralı EKLEME»*) ama bugün bir **temenni**,
çünkü *«bu cümle anlaşılmalı»* baskısı var. Öngörü kipinde **uygulanabilir** olur.

### 8.2 Döngü — ve zaten kurulu olan kısım

```
kullanıcı yazar "hasıl"
      ↓
öneriler ─── tıklar → toplam_ciro
      ↓
🟢 ETİKETLİ VERİ: (ham="hasıl" → toplam_ciro)
      ↓
sinonim_onerici.oner ──→ kuyruga_koy(approved=False)  ✅ VAR
      ↓
admin_app/routers/synonyms.py  (insan onayı)          ✅ VAR
      ↓
compose YALNIZ approved=True okur (ADR-0018 1e)       ✅ VAR
      ↓
sözlük büyür → daha az tıklama → daha çok tek-tık cevap
```

🔴 **Eksik olan tek şey aday üreten SİNYALDİ.** Tıklama tam olarak o sinyal.

> *Bir sözlüğü elle beslemek bir **borçtur**; kullanımdan hasat etmek bir **faizdir**.*

### 8.3 Kaybolmayan iş — dürüstçe

Öneri kipi **çözmez**, **görünür kılar**:
- «müşteri» 9 küpte 3 adla → **katalog tutarsızlığı**, sinonimle çözülmez
- 68/136 yön beyansız → *«en kötü»* önerisi **sunulamaz**
- 1 çıplak alan → kullanıcı yazınca **eşleşmez**

> **Öneri kipi katalog kalitesi işini bitirmez — ÖNE ÇEKER.**

---

## §9 · ŞİRKET / SEKTÖR / DİKEY ÇARPIMI — zaten çözülmüş

Öneriler **derlenmiş katalogdan türer**; katalog zaten katman katman kuruluyor:

```
kaynak → modül → sektör → kesişim(kaynak∧sektör) → şirket
```

| katman | öneriye ne verir | durum |
|---|---|---|
| `packs/modul/` (oee·bakım·ik·enerji·kpi) | dikeyin ölçü/boyutları | ✅ |
| `packs/sektor/` (boyahane·geri-dönüşüm·kumaş·tarım) | **terminoloji** | ✅ |
| `packs/kaynak/` (mikro·logo·netsis) | ERP alan adları | ✅ |
| `companies/<şirket>` | şirkete özel sinonim | ✅ |
| **şablonlar (~20–30 kalıp)** | Türkçe cümle yapısı | 🔵 **ORTAK — bir kez yazılır** |

🔴 **Şablonlar şirkete göre değişmez** — Türkçe gramer şirkete göre değişmiyor. Değişen
**doldurulan yuvalar**, ve onları compose zaten dolduruyor.

**Kanıt:** korpus bu turda dört şirketin dördü için de üretti (boyahane 10.764 · gitas
3.110 · gulteks 2.079 · atiksan 1.845 tur) — elle yazılmadı, **derlendi**.

⚠ **Tek gerçek şirket-başı artefakt: vektörel indeks.** Üretilen (yazılan değil) bir şey —
ama `demo/wren-project` tuzağını taşır: katalog değişince **yenilenmeli**, yoksa bayat
indeksle öneri verirsin. **Tazelik kapısı zorunlu.**

### 9.1 «Sonsuz cümle listesi» korkusu — ölçüldü, sonsuz değil

Sonsuz olan **söyleyiş**, anlam değil:

```
(küp · ölçü · boyut · dönem · niyet türü)
  23     136   sınırlı  sınırlı    6          → ölçülen ham tur: 14.957
```

*«Bu yılki ciro»*, *«bu sene hasılat ne kadar»*, *«2026 cirosu»* — üç söyleyiş, **tek**
demet. Sözlük **söyleyişi**, gramer **anlamı** karşılar; çarpılmazlar, **ayrışırlar**.

⊙ Ve üreteç **zaten var**: `lab/nl_corpus.py` katalogdan cümle üretiyor, her kapı
koşumunda. Bugün bir **ölçüm aleti**; öneri kipinde bir **ürün yüzeyi**. Aynı üreteç.

⊙ **Korpusun bilinen körlüğü ERDEME dönüşüyor:** *«korpus soruları katalogdan üretiliyor,
hepsi doğru yazılmış; typo yolu hiç sorulmuyor»* — öneri olarak bu tam istenen şey:
kullanıcıya **kanonik yazım** sunuluyor.

---

## §10 · NE DEĞİŞMİYOR — `§38.4` dokunulmazları

```
✅ LLM SQL yazmaz (küp yolunda)        ✅ narration_guard (fail-closed)
✅ sayıyı HER ZAMAN küp koyar          ✅ beyan kültürü (kapsam·seçim·yön)
✅ grafik kararı deterministik         ✅ Türkçe morfoloji katmanı
✅ kapalı fiil kümesi                  ✅ JOIN planlayıcı yasağı
✅ KURAL B · KAT-1                     ✅ motor in-process (§F1)
✅ E-8 (sıcak yola seri 2. LLM turu YOK)          ✅ ADR-0024
```

⚠ **`E-8` özellikle güçleniyor:** garson artık sıcak yolda **kritik** değil. Yavaşsa
(ölçülen: `k=3` ile 98 s) menü **onsuz da** dolu gelir; garson geldiğinde liste zenginleşir.

⚠ **Vektör kararda değil, ADAYDA:** vektör *«hangi ölçüyü göstereyim»* sıralamasını yapar,
**kararı kullanıcı verir**. İlke korunur — ama bu **açıkça yazılmalı**, yoksa bir sonraki
turda çelişki gibi okunur.

---

## §11 · TRADE-OFF TABLOSU

| kazanç | bedel |
|---|---|
| sessiz-yanlış sınıfı **yapısal olarak** daralır | **daha çok tık** (uzman yavaşlar → serbest metin kapısı **açık kalmalı**) |
| route **büyümeyi durdurur** | kısmi girdi sıralayıcısı **yeni iş** + gecikme bütçesi |
| sözlük **girdiden çıktıya** döner | katalog borcu **bloke edici** olur (68/136 · 3 ad) |
| garson **kritik yoldan çıkar** (`E-8`) | kademe ③'te garson **hâlâ zorunlu** |
| ölçüm ilk kez **mümkün** (Recall@3) | vektörel indeks **yaşam döngüsü** |
| plan **koşmadan** görünür (%25 sorunu) | pill satırı uzun planda **okunmaz** olabilir |
| katalog tutarsızlığı **görünür** | görünür ≠ çözülmüş |

---

## §12 · RİSKLER VE ÖLÜM ŞARTLARI

### 12.1 🔴 ÖLÜM ŞARTI — Türkçe kısa alan adlarında gömme isabeti

Her şey tek ölçülmemiş varsayıma dayanıyor: `hasıl → toplam_ciro` yakınlığı **çalışıyor mu?**

- **Çalışıyorsa:** sinonim yükü düşer, tıklama-etiket döngüsü kapanır, Thread 1–4 çalışır.
- **Çalışmıyorsa:** her eşleşme için yine sinonim yazarsın → **tredmill aynen geri gelir**,
  üstüne bir de vektör altyapısı bakımı biner. **Öneri, sihirbazın YANLIŞ kartı zorlaması olur.**

⚠ `multilingual-e5-large` cümlelerde iyi; **tek kelimelik Türkçe alan adlarında** aynı
olmayabilir. Bu **ölçülmeden** hiçbir satır yazılmamalı.

### 12.2 Diğer riskler

| risk | belirti | panzehir |
|---|---|---|
| **şerit enflasyonu** | `ReportCard` **4** chip şeridi + 2 öneri = 6 | *yazarken* ↔ *cevaptan sonra* **ayrı an**; yazınca kart şeritleri söner |
| **forma dönüşme** | pill satırı 5–6 öğe | **yazmak her zaman tıklamaktan hızlı** kalmalı |
| **sınırı gizleme** | kullanıcı yapamadığımızı hiç öğrenmez | `§D4` **proaktif sınır beyanı** zorunlu |
| **temsil edilemeyen öneri** | JOIN gerektiren chip | öneri **sunulmadan önce** temsil edilebilirlik kontrolü 🆈 |
| **bayat indeks** | katalog değişti, indeks değişmedi | tazelik kapısı (`mdl_version` deseni) |
| **makro enflasyonu** | her kombinasyon adlandırılır | ad **sıklıkla** kazanılır, olasılıkla değil |
| **«UX oyunu» iç söylemi** | sıralama kalitesine yatırım yapılmaz | içeride **recall problemi** denir, *sihir* denmez |

### 12.3 Sihirbaz metaforunun testi

| | **zorlama** ❌ | **öngörü** ✅ |
|---|---|---|
| serbest metin | kapalı | **açık** |
| kabul oranı | **düşük** (kullanıcı yine yazıyor) | **yüksek** |

🔴 Bu bir UX oyunu **olamaz**: sihirbazın numarası seyirci **kontrol etmediği** için işler.
Kullanıcı **her soruda** kontrol ediyor. **Kontrol edilebilir bir numara, numara değildir.**

---

## §13 · ÖLÇÜM PLANI — hiçbir satır yazılmadan önce

### 13.1 🔴 ÖN KOŞUL ÖLÇÜMÜ *(≈1 saat, kod yazmadan)*

```
1. 136 ölçü adını + 816 terimi göm (mevcut vqr embedder yolu)
2. 30–40 GERÇEK iş ifadesi yaz (hasıl · fire · duruş · verimlilik · bakiye · sapma…)
3. Recall@3 · Recall@5 · MRR ölç
```

| eşik | karar |
|---|---|
| **Recall@3 ≥ %85** | 🟢 devam — döngü kapanır |
| %70–85 | ◐ sinonim desteğiyle devam, kapsam dar |
| **< %70** | 🔴 **DUR** — tredmill geri gelir, bu plan uygulanmaz |

### 13.2 Prototip sonrası ölçütler

| ölçüt | ne söyler | eşik |
|---|---|---|
| **kabul oranı** | öngörü mü, kılık değiştirmiş form mu | 🔴 **asıl gösterge** |
| **tek tıkla cevap oranı** | *«dürüst red başarı değil»*in sayısal hâli | 2 tıktan fazlası kusur |
| **öneri gecikmesi (p95)** | tamamlama vaadi tutuyor mu | **< 300 ms** |
| `CLARIFY:*` oranı | soru sormak mı azaldı | bugünkü %11+%9'un **altına** inmeli |
| erişim (korpus) | kapsam kaybı kapandı mı | **69/69/69/72 tabanına dönüş** |

### 13.3 Ölçülmemiş — ve kararı değiştirebilecek olanlar

| # | ne | neden önemli |
|---|---|---|
| ① | **Türkçe gömme isabeti** | 🔴 **ölüm şartı** (`§13.1`) |
| ② | her şirketin **katalog boyutu** | indeks tazeleme maliyeti |
| ③ | **gömme üretim süresi** | şirket başı artefakt maliyeti |
| ④ | pill satırı **uzunluk dağılımı** | kaç öğede okunmaz olur |
| ⑤ | takiplerin **sınıf dağılımı** (bağlamsal ↔ yeni) | şerit sırası; `followup.sinifla`'dan **hemen** çıkar |
| ⑥ | ② kademesi **kaç reçeteyle** trafiğin ne kadarını kapatır | *«çoğu iş reçetedir»* bugün bir **iddia** |
| ⑦ | `%25` onarım tutma — **payda 16** | eğilim işareti, kanıt değil |

---

## §14 · YOL HARİTASI — sıra

```
0  🔴 ÖN KOŞUL     §13.1 gömme ölçümü            ─ eşik altındaysa BURADA DURULUR
                    ↓
1  ÖLÇÜM ALTYAPISI  Recall@3/MRR koşucusu (lab/) ─ kapıya bağlanır
                    ↓
2  KIYAS TEMELİ     [akran ▾][dönem ▾][hedef ▾]  ─ TEK BAŞINA hak ediyor:
   CHIP'İ           ölçülmüş, tekrar eden, chip'le TAM çözülen kusur sınıfı
                    ↓
3  ÖNERİ ÜCÜ +      kısmi girdi sıralayıcısı     ─ ⚠ FE tüketicisi AYNI demette
   FE ŞERİDİ        + öneri ucu + iki şerit         (§G yetim uç kapısı)
                    ↓
4  ÇAPA             görünür bağlam nesnesi        ─ + [buradan devam et] (POST /cube)
                    ↓
5  PILL SATIRI      Niyet'in görünür hâli         ─ tipli `+`, canlı doğrulama
                    ↓
6  MAKRO (②)        kök-neden · YoY · pareto      ─ ad SIKLIKLA kazanılır
                    ↓
7  PLAN ÖNİZLEME    garson taslağı → pill → onay  ─ kademe ③, %25 sorununun çaresi
                    ↓
8  HASAT DÖNGÜSÜ    tıklama → aday kuyruğu        ─ §A hattına bağlanır
```

⚠ **Adım 2 bağımsız ve şimdi yapılabilir** — öneri katmanından önce değer üretir.
⚠ **Adım 3'ten itibaren** `KURAL B` bayrağı (`oneri_katmani`) altında; kapalıyken bugünkü
davranış **bayt bayt** aynı ve bu **kapıyla kanıtlanır**.

---

## §15 · SEKTÖR KONUMU — devrimsel mi?

### 15.1 Büyük firmalar guided'ı bıraktı mı?

**Hayır — iki farklı olay karıştırılıyor:**

| kim | ne oldu | kaynak |
|---|---|---|
| **Tableau Ask Data** | 🔴 **EMEKLİ** — Cloud **Şubat 2024**, Server **2024.2** | *«Tableau's Ask Data and Metrics features were retired in Tableau Cloud in February 2024 and in Tableau Server version 2024.2.»* — `help.tableau.com` |
| **Power BI Q&A** | 🔴 **EMEKLİ EDİLİYOR — Aralık 2026** | *«Q&A experiences are going away in December 2026. We recommend using Copilot for Power BI…»* — `learn.microsoft.com` (`ms.date: 2026-05-22`) |
| **ThoughtSpot** | ✅ **bırakmadı** — token motoru omurga, LLM **üstünde** | *«Spotter is **built on top of** the BI industry's leading relational search model…»* — `docs.thoughtspot.com/cloud/latest/spotter` |

⟳ **BU TABLO 2026-08-13'te DÜZELTİLDİ.** İlk yazımımda *«Power BI Q&A duruyor, öne
çıkarılmıyor»* demiştim — **yanlıştı**: resmî belge **Aralık 2026 emekliliğini** ilan
ediyor. ⚠ Ayrıca ThoughtSpot'un LLM katmanının adı **«Sage» değil «Spotter»**; `Sage`
adı erişilebilen hiçbir belgede geçmiyor.

🔴 **Ve Power BI'ın belgelenmiş çöküş sebebi TAM OLARAK bu belgenin tezidir** (birebir):
> *«One of the most basic and effective ways to improve the Q&A visual experience is
> through adding **synonyms** for the names of tables and fields… a publishing company
> trying to see 'novel sales last year' may not receive useful results **without defining
> 'novel' as a synonym for 'product'**.»*
> *«The **Teach Q&A** section allows you to train Q&A to recognize words.»*

⊙ Yani iki *«yazarken yönlendiren»* ürün de öldü ve **ikisi de yerine LLM sohbet asistanı
koydu**. Ayakta kalan ThoughtSpot, LLM'i **deterministik token motorunun yerine değil
ÜSTÜNE** koyarak kaldı. ⚠ Ve LLM sağlayıcısı **takılıp çıkarılabilir** (*«including the
GPT-series models, Google Gemini, Snowflake Cortex, and Claude»*) — yani LLM **çekirdek
değil, değiştirilebilir bir bileşen**.

🔴 Kategoride ayakta kalan, guided'ı **bırakmayan** ve LLM'i **üstüne** koyan firma.
Yani bu belgenin sırası — *önce deterministik omurga, sonra LLM kabuğu* — piyasada
**kazanan tarafın sırası**.

Ötekilerin bırakma sebebi *«guided çalışmıyor»* **değildi**: geri besleme döngüsüz elle
besleme + bütçenin copilot'a kayması. İkisi de guided'ın kendisine dair **kanıt değil**.

### 15.2 Onlardan farkımız

| | onlar | biz |
|---|---|---|
| sözlük nasıl doluyor | **kullanıcı öğretir**, döngü yok | **tıklama = etiket** → kuyruk → onay |
| eksik sinonim | ⊘ bilinmez (hata sessiz) | **tıklanmayan öneri sayılır** |
| ölçüm | ⊘ | Recall@3 · kabul oranı |
| garanti | sorgu gösterilir | 🔴 **guard + makbuz + beyan** |

⚠ **Geride olduğumuz üç şey:** bağlayıcı genişliği · kurumsal yönetişim olgunluğu · arayüz
cilası. Zamanla kapanır ama **bugün gerçek**.

### 15.3 Bizde olan, onlarda OLMAYAN

```
narration_guard  → eşleşmeyen sayı taşıyan cümle YAYIMLANMAZ (fail-closed)
makbuz           → hangi araç · kaç ms · kaç adım · REDDEDİLEN adımlar dâhil
kapsam beyanı    → "9 boyuttan 4'ü taranmadı: renk, parti, …"
seçim beyanı     → "12 aday arasından en açıklayıcısı"
yön beyanı       → "bu ölçüde yön beyan edilmemiş, yargı verilmez"
```

Hiçbir büyük BI aracı *«neye BAKMADIĞINI»* ve *«kaç aday arasından seçtiğini»* söylemiyor.
**Onlar cevabı gösterir; biz cevabın SINIRLARINI gösteriyoruz.**

### 15.4 Devrimsel mi — **hayır**, ve doğru hedef

BI'da devrimler arayüzden gelmedi: bellek-içi kolonlu motorlar · bulut ambarları ·
taşınabilir semantik katman. **Etkileşim biçimi değişiklikleri tarihsel olarak devrim
yapmadı** — Ask Data ve Q&A bunun kanıtı.

Yeni olan **birleşim**. Ve birleşimler nadiren devrimdir, sık sık **hendek**tir:

> *«Türkçe konuşan bir üretim şirketinin sorusunu **doğru** cevaplayan, **uydurmayan**,
> ve **neye bakmadığını söyleyen** tek sistem.»*

Kopyalanması zor, çünkü içinde üç yerel varlık var: **Türkçe morfoloji** · **yerel ERP
kaynak paketleri** (mikro/logo/netsis) · **dikey modüller** (OEE·bakım·enerji). Global
araçlar bu üçünü de yapmıyor ve yapmaları için sebep yok.

⊙ **Hendek guided'dan gelmiyor** — guided onu **erişilebilir** yapıyor. Hendek semantik
katmanda ve beyan kültüründe.

### 15.5 Anlatım riski — ve panzehiri

2026'da chat bekleyen bir piyasaya **2015 arayüzü** çıkarma riski gerçek.

🔴 **Panzehir plandadır: LLM kabuk olarak kalıyor.** Ürün chat gibi görünür, altında
deterministik omurga çalışır.

> **Anlatım:** *«Guided'a dönüyoruz»* **DEĞİL** — *«Sohbet ediyoruz ama uydurmuyoruz.»*

⊙ Ve arayüz geçmişe dönüyor, **motor dönmüyor**. Fark asli:
> *Aynı arayüz, **zorunluluktan** doğduğunda bir sınırdır; **tercihten** doğduğunda bir
> karardır.* Onlar guided'dı çünkü 2018'de LLM yoktu. Biz guided olacağız çünkü **seçiyoruz** —
> LLM elimizde, kabuk olarak duruyor, kademe ③'te çalışıyor.

---

## §16 · KARAR ÖZETİ

| soru | cevap |
|---|---|
| Mantıklı mı? | ✅ **Evet** — ve piyasada ayakta kalan örneğin sırası |
| Mimari değişiklik mi? | ⊘ **Hayır** — rol değişikliği; `MIMARI.md` diff'i **bir paragraf** |
| Şirket başına iş var mı? | ⊘ **Hayır** — compose zaten çözmüş; tek artefakt **vektörel indeks** |
| Sözlük yine elle mi? | ⊘ **Hayır** — tıklama bir **etiket**; hasat hattı **zaten kurulu** |
| Route büyümeye devam mı? | ⊘ **Hayır** — kusur sınıfı *sessiz-yanlış*tan *kötü sıralama*ya düşer |
| Garson kalkıyor mu? | ⊘ **Hayır** — kritik yoldan çıkıyor, kademe ③'te **taslak çiziyor** |
| Devrimsel mi? | ⊘ **Hayır** — ama **hendek** |
| Şimdi başlanır mı? | 🔴 **`§13.1` ölçümünden SONRA** |

---

## §17 · BU BELGENİN SINIRI

Buradaki her sayı bu oturumda **ölçüldü** ve kaynağı yazılı. Ama:

🔴 **Uygulama kararı `§13.1` ölçümüne bağlıdır ve o ölçüm YAPILMADI.** Türkçe kısa alan
adlarında gömme isabeti eşiğin altındaysa bu belgenin `§3`–`§14` arası **uygulanmaz** ve
`§2`'deki teşhis geçerli kalır ama çare değişir.

⊙ Ayrıca `§15.1`'deki ürün durumları **Mayıs 2026'ya kadar olan bilgiye** dayanır;
sonrasında değişmiş olabilir. Bu, kararı değiştirmez ama iddiayı yumuşatır: bu
**kanıtlanmış bir yol** değil, **kanıtlanmış bir yolun ayakta kalan örneğine benzeyen** bir yol.

> *Bir raporun sayısını kapıya bağlamazsan, o sayı bir sonraki turda bir hatıra olur.*

---

# EK — 2026-08-13 · KAYNAKLI ARAŞTIRMA

> ⚠ **Yöntem:** Bu bölüm **dört paralel ajanın `WebFetch` ile çektiği resmî belgelerden**
> derlendi. Her sayının yanında kaynak var. `WebSearch` oturum bütçesi tükendiği için
> **arama yapılmadı** — yalnız bilinen belge adresleri çekildi; dolayısıyla bu bir
> **literatür taraması değil, hedefli bir kaynak doğrulamasıdır**.
> 🔴 **Kaynakta bulunamayan hiçbir sayı yazılmadı.** *«Kaynakta yok»* diyen maddeler
> bilerek boş bırakıldı.

---

## §18 · SEMANTİK VE VEKTÖREL KATMAN — nasıl yapılır

### 18.1 🔴 Bu bir RAG problemi DEĞİL — **varlık bağlama** (entity linking)

| | RAG | **bizim işimiz** |
|---|---|---|
| girdi | serbest belge yığını | **kapalı** sözlük: 136 ölçü + 816 terim |
| çıktı | isteme konacak metin | **bir alan kimliği** |
| araçlar | chunking · reranker LLM · context stuffing | **eşleme + sıralama** |

⊘ RAG araç zinciri burada **gereksiz ve zararlı**: chunk yok, uzun belge yok, LLM
reranker gecikme bütçesini (§18.9) tek başına yer.

### 18.2 ✅ Ölçek kararı — **HNSW DEĞİL, EXACT arama**

Dört satıcı da aynı yönü gösteriyor:

| kaynak | ifade |
|---|---|
| **Weaviate** | *«**Flat index**: a simple, lightweight index that is designed for **small datasets**»* · dinamik indeks eşiği *«by default **10,000**»* |
| **Vespa** | *«**Since the dataset is small, we do not specify `index`** which would build HNSW data structures for faster (but **approximate**) vector search.»* |
| **Qdrant** | *«Use exact searches to bypass HNSW… returning results in a **stable, deterministic order**… practical only for small collections.»* |
| **Elastic** | exact kNN: *«**Best for small datasets or precise scoring**»* · *«HNSW trades perfect accuracy for speed, so results **aren't always the true k closest neighbors**.»* |

🔴 **Bizim ölçeğimiz ~1.000 vektör — Weaviate'in kendi eşiğinin ONDA BİRİ.**
1.000 × 1024 boyut × float32 ≈ **4 MB**; tek matris çarpımı milisaniye altı.

> **Karar: ANN kullanılmayacak.** HNSW bu ölçekte tek şey getirir: **kayıp recall + kararsız
> sıralama**. Ve kararsız sıralama, `ADR-0024`'ün determinizm kültürüyle **doğrudan çelişir**.

⊙ Yan fayda: exact arama **tekrarlanabilir** — aynı girdi her zaman aynı listeyi verir,
yani kapıya bağlanabilir 🆇.

### 18.3 Hibrit erişim — leksik + dense, ve **RRF tuzağı**

**Neden hibrit:** Vespa'nın ölçümü (327 sorgu, nDCG@10):

```
BM25   (leksik) 0.3210   ← LEKSİK DENSE'İ GEÇTİ
dense           0.3077
hibrit          0.3233 – 0.3423   ← ikisini de geçti (+%6,6 nispi)
```

⊙ Weaviate'in konumlandırması aynı yönde (birebir): *«**Vector search is more forgiving
semantically and keyword search is more precise.**»*
🔴 Kısa alan adlarında (`toplam_fire_kg`) ayırt edici sinyal **tam token eşleşmesidir**
(`fire`·`oee`·`kg`) — yani **leksik ayak vazgeçilmez**.

**RRF formülü** (Elastic, birebir):
```
score = Σ  1 / ( k + rank(result(q), d) )        # rank 1'den başlar
rank_constant default = 60
```
> *«RRF **requires no tuning**, and the different relevance indicators **do not have to be
> related to each other** to achieve high-quality results.»* — Elastic

🔴 **VE BURADA BİR TUZAK VAR — `k` sabiti satıcıya göre DEĞİŞİYOR:**

| satıcı | `k` | rank tabanı |
|---|---|---|
| Elastic · OpenSearch · Weaviate | **60** | **1**-tabanlı |
| **Qdrant** | **2** | **0**-tabanlı |

⚠ *«Endüstri standardı 60»* diye kopyalarsan **farklı bir sistem** kurmuş olursun: `k`
küçüldükçe ilk sıralar keskinleşir. **Autocomplete için küçük `k` aslında istenen
davranış olabilir** — ama bu **bilinçli** seçilmeli, miras alınmamalı ㉓.

⚠ **VE RRF TARTIŞMASIZ ÜSTÜN DEĞİL.** Weaviate 1.24'te varsayılanı RRF'ten skor
normalizasyonuna **çevirdi** (birebir): *«the default `relativeScoreFusion` algorithm showed
a **~6% improvement in recall** over the `rankedFusion` method»* — gerekçe: *«retains more
information from the original searches than `rankedFusion`, which **only retains the
rankings**»*. Qdrant da kabul ediyor: *«**Neither dominates the other in general**, so use
your eval set to choose.»*

> 🔴 **RRF'in tartışmasız üstünlüğü DOĞRULUK değil, AYAR GEREKTİRMEMESİDİR.**
> Bizde bir altın küme yokken doğru başlangıç **RRF**; küme kurulunca ikisi **ölçülür**.

**Ağırlık kalibrasyonu** — Qdrant'ın protokolü (birebir, tek kaynaklı yöntem):
> *«**Split your eval queries in two. Try different weights on the first half, then measure
> on the second half.** Measuring on the same queries you tuned on **inflates** the result.»*
> *«Without an eval set: **leave weights at the default (1.0, 1.0)**.»*

⚠ Ve **kullanım sıklığı** (popülerlik) üçüncü sinyal olarak eklenecekse (birebir uyarı):
> *«RRF scores are small (sums of `1/(k+rank)`), while decay functions return `[0,1]`, so an
> unweighted decay term **will dominate** the fused score unless you multiply it by a
> smaller coefficient.»*

### 18.4 Model seçimi — **E5 prefix tuzağı** vs **BGE-M3**

🔴 **`multilingual-e5-large` PREFIX ZORUNLU** (model kartı, birebir):
> *«Each input text should start with **"query: "** or **"passage: "**, even for non-English texts.»*
> SSS: *«Do I need to add the prefix…? **Yes, this is how the model is trained, otherwise you
> will see a performance degradation.**»*

⚠ **VE BİZİM İŞİMİZ SİMETRİK:** kart *«Use `'query: '` prefix for **symmetric** tasks such
as semantic similarity»* diyor. `hasıl` ↔ `toplam_fire_kg` bir belge arama değil, bir
**terim eşlemesi** → **iki tarafa da `query: `** konur.
🔴 `query:`/`passage:` ayrımını burada kullanmak **sessiz bir kalite kaybıdır** —
patlamaz, sadece kötü sonuç verir. `vqr.py`'nin bugünkü kullanımı **denetlenmeli**.

⊙ **`BAAI/bge-m3` bu derdi tamamen kaldırıyor** (birebir):
> *«The BGE-M3 model **no longer requires adding instructions** to the queries.»*
> *«It can **simultaneously** perform… dense retrieval, multi-vector retrieval, and sparse retrieval.»*
> *«obtaining token weights (similar to the BM25) **without any additional cost** when
> generating dense embeddings.»*

🔴 **Bu son cümle bizim için belirleyici:** BGE-M3 **hibridin leksik ayağını bedava**
veriyor — ayrı bir BM25 indeksi kurmadan. Snake_case alan adlarında tam-token eşleşmesi
tam da ihtiyacımız olan şey.

⚠ **E5'in ikinci tuzağı** (kart SSS'i, birebir): *«**Why does the cosine similarity scores
distribute around 0.7 to 1.0?** …we use a low temperature 0.01 for InfoNCE contrastive
loss.»* → **sabit eşik (ör. «0,8 üstü kabul») E5'te anlamsızdır**; yalnız **sıralama** ve
**göreli fark** kullanılabilir.

### 18.5 🔴 Türkçe — **hiçbir büyük model kartı taahhüt etmiyor**

| model | Türkçe ifadesi |
|---|---|
| `bge-m3` | *«more than 100 working languages»* — **Türkçe adı hiç geçmiyor**, liste yok |
| `multilingual-e5-large` | *«supports 100 languages from xlm-roberta»* + ⚠ *«**low-resource languages may see performance degradation**»* |
| `paraphrase-multilingual-MiniLM-L12-v2` | ✅ YAML dil listesinde **`tr` VAR** (ama 384 boyut, 128 token, benchmark yok) |
| `gte-multilingual-base` | *«over 70 languages»* — **Türkçe geçmiyor** |
| `emrecan/bert-base-turkish-…-stsb-tr` | ✅ **Türkçe'ye özel** · STS-b (tr) **Spearman 0,830** ⚠ eğitim *«**machine translated** versions»* |

🔴 **E5'in Türkçe skorları YALNIZ SINIFLANDIRMA** (`MTOPIntent tr` acc 74,29 ·
`MassiveIntent tr` ~69–74) — **retrieval skoru yok**; `Mr. TyDi` dil listesinde Türkçe
**bulunmuyor**.

### 18.6 🔴🔴 **KISA / TEK KELİME PERFORMANSI — HİÇBİR KAYNAKTA YOK**

Beş model kartının **hiçbirinde** tek kelime / snake_case alan adı gömme hakkında uyarı ya
da ölçüm yok. En yakın ifade BGE-M3'ün *«spanning from **short sentences** to long
documents»* — *«kısa cümle»* diyor, *«tek kelime»* demiyor.

> **Bu, `§13.1` ölüm şartının literatürden DOĞRULANMASIDIR:** kart okuyarak model
> seçilemez. **Kendi ölçümümüz zorunludur.** 🆕

### 18.7 Ne gömüyoruz — **alan adını DEĞİL**

`toplam_fire_kg` ham hâliyle gömmek kötü. Gömülecek olan **çok görünümlü** temsil:

```
alan: toplam_fire_kg
 ├ görünen etiket : "toplam fire (kg)"        ← measure_synonyms_display  ✅ VAR
 ├ sinonimler     : "fire, zayiat, kayıp"     ← cube_synonyms.yml         ✅ VAR
 ├ küp bağlamı    : "üretim · kalite"
 └ birim          : "kilogram"
→ her görünüm AYRI vektör; sorgu en yakın GÖRÜNÜME eşleşir, alan o görünümden türer
```

⊙ Üç girdinin üçü de **zaten katalogda** — ek yazım işi yok.

### 18.8 Yazım hatası — **edge n-gram + fuzzy**, ve Türkçe uyarısı

Beş hibrit belgesinin **hiçbirinde** prefix/typo/autocomplete geçmiyor (kapsamları değil).
Satıcıların ayrı referanslarından:

**Elastic `search_as_you_type`** (birebir): *«Wraps the analyzer of `my_field._3gram` with an
**edge ngram token filter**»* → prefix için önerilen mekanizma **indeksleme zamanı edge
n-gram**, arama zamanı wildcard değil.

**Fuzzy eşikleri** — iki bağımsız kaynak neredeyse aynı:

| | Algolia | Typesense |
|---|---|---|
| 1 hata min. uzunluk | **4** | **4** |
| 2 hata min. uzunluk | **8** | **7** |
| maksimum hata | **2** | **2** |
| tam eşleşme varsa | *«Typo count is the **first criterion** in the ranking formula»* | `typo_tokens_threshold=1` → **hatalıya hiç bakma** |

🔴 **VE BİZİM İÇİN KRİTİK BİR TUZAK** — Elastic `fuzziness: AUTO` (birebir):
> *«`0..2` **Must match exactly**»*

⚠ Yani **3 karakterden kısa terimlerde hiç düzeltme yapılmaz**. Türkçe kısa ölçü
adlarında (`kâr`·`adet`·`OEE`) tipo toleransı isteniyorsa **eşik elle düşürülmeli**.

⚠ Ve ters yönde: *«bu eşikler Latin/İngilizce kelime uzunluğu dağılımına göre kalibre
edilmiş; **Türkçe eklemeli yapıda kelimeler uzun** olduğu için 2-hata eşiği daha erken
tetiklenir»* → **ölçmeden benimseme** 🅡.

### 18.9 Instant-search UX — **kaynaklı sayı tablosu**

| kıstas | değer | kaynak |
|---|---|---|
| **algı eşiği** | **100 ms** — *«system is reacting instantaneously»* | NN/g |
| akış kesilme eşiği | 1.000 ms | NN/g |
| motor hedefi | **< 50 ms** | Typesense |
| **debounce** | **200 ms** · *«Delays of over **300 ms** will start degrading the user experience»* | Algolia ×2 |
| yavaş ağda debounce | 400 ms | Algolia |
| *«takıldı»* göstergesi | 500 ms | Algolia |
| **öneri adedi (masaüstü)** | **≤ 10** — *«users tend to either begin to ignore suggestions»* | Baymard |
| öneri adedi (mobil) | ~8 (Amazon: **6**) | Baymard |
| kaydırma çubuğu | 🔴 **YASAK** — *«should be **avoided**»* | Baymard |
| **öneri seçilme oranı** | 🔴 **%23** (136 örnekte 31) | NN/g |

🔴🔴 **SON SATIR EN ÖNEMLİSİ.** NN/g ölçümünde öneriler **yalnızca %23 oranında**
seçiliyor. Bu bizim **kabul oranı** eşiğimizin **gerçekçi tabanı**:

> ⚠ *«Kabul oranı %20'nin altındaysa özellik başarısız»* diye bir eşik koymak **yanlış
> olurdu** — genel web aramasında taban zaten %23. **Bizim avantajımız kapalı bir uzay
> ve yapılı bir katalog olması**; hedef bunun **belirgin üstü** olmalı, ama eşik
> literatüre göre konmalı, sezgiye göre değil 🅔.

**Klavye/erişilebilirlik — W3C ARIA APG Combobox zorunlu:** `role="combobox"` ·
`aria-expanded` · `aria-controls` · `aria-activedescendant` (DOM odağı **input'ta kalır**) ·
↓↑ seçenek gezinme · `Enter` kabul · `Esc` kapat.
⚠ Çelişki: APG *«son seçenekte dur»*, Baymard *«başa dön»* diyor → **APG kazanır**.

### 18.10 🔴🔴 KARŞI KANIT — *«Schema Linking'in Ölümü»*

**Lehimize olan kanıt** önce:

| bulgu | kaynak |
|---|---|
| BIRD hata analizi: **%41,6 «Wrong Schema Linking»** — en büyük tek kategori | `arxiv 2305.03111` Ek B.6 |
| *«schema linking… continues to be a **significant obstacle** for models»* | aynı |
| **Spider 2.0**: gerçek kurumsal şemalarda (*«over 1,000 columns»*) doğruluk **%91,2 → %21,3** | `arxiv 2411.07763` |
| İnsan **%92,96** ↔ en iyi model **%81,95** (BIRD, 2026-08) | `bird-bench.github.io` |
| Databricks Genie: *«support up to **30 tables**… **prejoin** related tables into views»* | `docs.databricks.com` |

🔴 **AMA CİDDİ BİR KARŞI KANIT VAR** — *«The Death of Schema Linking? Text-to-SQL in the
Age of Well-Reasoned Language Models»* (`arxiv 2408.07702`), birebir:
> *«**We find empirically that newer models are adept at utilizing relevant schema elements
> during generation even in the presence of large numbers of irrelevant ones.** As such, our
> Text-to-SQL pipeline **entirely forgoes schema linking**… Our approach **ranks first on the
> BIRD benchmark** achieving an accuracy of **71.83%**.»*

**Bu bizi üç yerden vurur:**
1. **%41,6 rakamı 2023 ChatGPT'ye ait** — güncel model kırılımı **bulunamadı**.
2. Makale, **filtrelemenin KENDİSİNİN** hata kaynağı olduğunu söylüyor: gerekli sütunu
   eleyip atmak. 🔴 **Kullanıcı tıklaması da bir filtredir** — yanlış tıklama, geri
   dönüşü olmayan bir hatadır.
3. Şema bağlam penceresine sığıyorsa *«hiç bağlama yapma»* BIRD'de **1. sırayı** almış.

**Karşı-karşı argüman:** Makale açıkça koşul koyuyor — *«in cases where the schema **fits
within the model's context window**»*. Spider 2.0'ın *«over 1,000 columns»* şemaları bu
koşulu sağlamıyor ve orada doğruluk **%21,3**.

> 🔴 **SAVUNULABİLİR EN GÜÇLÜ FORMÜLASYON (üç kanıtı birden karşılar):**
> *«Şema bağlama, **şema büyükken** baskın hata kaynağıdır; küçük şemalarda modern
> modeller kendi başına başa çıkıyor. Tıklama tasarımımız **büyük/gerçek kurumsal
> şemalar** için doğru; küçük şemalarda **gereksiz sürtünme** yaratabilir.»*

⊙ **Bizim kataloğumuz hangisi?** 23 küp · 136 ölçü · 816 terim — **sınırda**. Tek bir
küpün şeması bağlam penceresine rahat sığar; **23 küpün tamamı + değerler** sığmaz.
🔴 Bu, öneri katmanının **küp seçiminde** haklı, **küp içi alan seçiminde** tartışmalı
olduğunu söyler. → `§20`'de karar satırı.

**İkinci karşı kanıt:** BIRD-Interact'ta **etkileşimli** modda SOTA modeller yalnız
**%16–24**. *«Kullanıcıya sor»* tek başına sihirli değnek **değil** — sorulanın **doğru
şey** olması ve seçeneklerin **doğru üretilmiş** olması gerekiyor.

**Üçüncü karşı kanıt — ve bir UX riski:** Cortex Analyst'ta `suggestion` içerik tipi
**yalnız son çare** (birebir): *«only included in a response **if** the user question was
ambiguous **and** Cortex Analyst **could not** return a SQL statement»*. Genie'de
netleştirme **elle yazılan bir talimat**.
🔴 **Hiçbir ürün tıklamayı BİRİNCİL akış yapmamış.** Endüstri *«önce çıkarım dene, olmazsa
sor»* düzenini seçmiş. Bizim önerimiz bunun **tersi** — ve bunun **doğrudan ürün örneği
yok**. Bu bir yenilik olabilir; bir uyarı da olabilir.

### 18.11 Endüstri doğrulaması — semantik katman tarafı **bizim lehimize**

| ürün | birebir ifade |
|---|---|
| **Snowflake Cortex Analyst** | *«Generic AI solutions often struggle with text-to-SQL… as **schemas lack critical knowledge** like business process definitions and metrics handling.»* · VQR: *«leverages relevant SQL queries from the repository when answering similar questions»* |
| **Cube** | *«agents writing SQL against a warehouse end up with **inconsistent metrics and ungoverned access** — numbers that don't match how your business defines them»* · *«Every query passes through the semantic layer runtime, where it's validated… **deterministically**»* |
| **dbt MetricFlow** | *«Rather than capturing arbitrary join logic, MetricFlow **captures the types of each identifier** and then helps users navigate to appropriate joins. This allows us to **avoid the construction of fan out and chasm joins**»* |

🔴 **Üçü de aynı şeyi söylüyor: ham şema üzerinde LLM'e SQL yazdırmak çalışmıyor** —
SQL üretimi LLM'den alınıp **deterministik bir motora** veriliyor, LLM'e kalan iş yalnız
*«hangi metrik + hangi boyut»*.

⊙ **Bu tam olarak bizim `küp + garson` mimarimizdir** ve `VQR`'ımız Cortex Analyst'ın
*«Verified Query Repository»*siyle **aynı fikir** — üstelik bizde **daha önce** vardı.
⚠ Cortex Analyst'ın kendi uyarısı bizim için de geçerli: *«**Invalid or inaccurate queries
can negatively impact** Cortex Analyst's performance and accuracy.»* → VQR'a giren her
kayıt **onaylı** olmalı.

---

## §19 · TEK TUŞLA AÇ/KAPA — ve bayraklama

### 19.1 ✅ Birbirine mani değiller — **yapısal sebep**

Öneri katmanı `cube_query`'yi **ÜRETMENİN** yeni bir yolu; **KOŞMANIN** değil.

```
öneri katmanı  ─┐
                ├─→ cube_query ──→ parse_cube_query ──→ compose ──→ motor ──→ makbuz
serbest metin  ─┘        ▲               ▲                              ▲
                    AYNI NESNE      AYNI BEYAZ LİSTE              AYNI GUARD
```

🔴 İki giriş kapısı, **tek koridor**. Bu yüzden aynı anda var olabilirler ve bu yüzden
`KURAL B` **kanıtlanabilir**.

### 19.2 Üç kademe — ve üçü de **zaten mevcut mekanizma**

| kademe | ne | mekanizma | durum |
|---|---|---|---|
| ① **bayrak** | `oneri_katmani: off\|alpha\|beta\|on` | `demo/packs/features.yml` | ✅ desen var |
| ② **kapsam** | `global < sector < tenant < role < **user**` | `features.py` çözüm sırası | ✅ **var** |
| ③ **ekran tuşu** | kullanıcı kapsamında override yazar | `FeatureOverride` | ✅ **var** |

🔴 **Yani ekrandaki tuş yeni bir kavram değil** — `features.py`'nin **en spesifik kapsamı**
olan `user`'a bir override yazmak. Kod tarafında **yeni bir mekanizma gerekmiyor**.

```
[ ⚡ Öngörü  ●━━ ]   ← açık: öneriler + çapa + pill
[ ⚡ Öngörü ━━●  ]   ← kapalı: BUGÜNKÜ davranış, bayt bayt (KURAL B)
```

### 19.3 🟢 Bedava gelen: **A/B kontrol grubu**

Kullanıcı-kapsamlı bir tuş, **ölçüm için bir hediyedir**: kapatanlar **kontrol grubu**
olur. Aynı katalog, aynı korpus, aynı motor — tek fark giriş kapısı.

⊙ Bu, `§13.2`'nin *«kabul oranı»* ölçütünü **karşılaştırmalı** hâle getirir: *«açık
kullanıcılar tek tıkla cevaba daha çok mu ulaşıyor?»* — ve bu, bir **kanıttır**, bir
izlenim değil.

### 19.4 ⚠ Dört tuzak

**① Thread ortasında kapatma.** Çapa ve pill'ler ne olacak? **Zarif düşüş** şart:
çapa → düz metin bağlam · pill'ler → normal `cube_query`. **Veri kaybı olmamalı**;
kullanıcı geri açtığında aynı yerden devam etmeli.

**② 🆀 BAYRAK ARKASINDAKİ KAPI SUSAR.** Bu deponun ölçülmüş kusuru. Öneri kapıları
**yalnız bayrak açıkken** koşarsa, kapalı kip sessizce çürür. → **Her iki kipte de koşan**
kapı gerekir; `KURAL B` yüklemi ikisini **kıyaslamalı**.

**③ Öğrenme asimetrisi.** Kapalı kullanıcılardan **tıklama etiketi gelmez** — çünkü
kapalıyken hiçbir şey değişmiyor (`KURAL B`). ⊘ Bu **kabul edilir**: alternatifi,
kapalı kipte gizlice veri toplamaktır ve o `KURAL B`'yi çiğner.

**④ Tuşun yeri bir vaattir 🆈.** *«Öngörü»* yazan bir tuş, kapatıldığında ürünün
**bozulmadığını** garanti etmeli. Kapalı kipte cevap kalitesi düşerse tuş bir **tuzağa**
dönüşür.

### 19.5 Kapı sözleşmesi

```
test_oneri_katmani_kural_b.py
  ① bayrak KAPALI → yanıt gövdesi bugünküyle BAYT BAYT aynı        (mutasyonlu)
  ② bayrak AÇIK   → aynı cube_query seçilirse yanıt AYNI           (öneri yalnız GİRİŞ)
  ③ her iki kipte de guard/makbuz/beyan alanları DEĞİŞMEZ
  ④ öneri ucu var ise FE tüketicisi de var                          (§G yetim uç kapısı)
  ⑤ öneri listesindeki her aday TEMSİL EDİLEBİLİR                   (JOIN yasağı vb.)
```

---

## §20 · KARAR MATRİSİ — her ihtimal, önceden verilmiş karar

### 20.1 Ön koşul ölçümü (`§13.1`) sonucuna göre

| Recall@3 | karar | gerekçe |
|---|---|---|
| **≥ %85** | 🟢 **tam uygula** | tıklama-etiket döngüsü kapanır |
| %70–85 | ◐ **dar kapsamla uygula** | öneri **yalnız** sinonimi olan alanlarda; hasat döngüsü kapsamı büyütür |
| **< %70** | 🔴 **DUR** | tredmill geri gelir; `§2` teşhisi geçerli kalır, **çare değişir** |
| ölçüm koşulamıyor | 🔴 **DUR** | 🆆 *hesaplayamadığını söylemek de bir ölçümdür* |

### 20.2 Prototip sonrası

| gözlem | karar |
|---|---|
| kabul oranı **NN/g tabanının (%23) belirgin üstü** | 🟢 devam |
| kabul oranı ~%23 civarı | ◐ **sıralama** sorunu — model/füzyon değiştir, tasarımı değil |
| kabul oranı **%23 altı** | 🔴 öneri **gürültü**; chip'lere geri dön, öneri katmanını kapat |
| p95 gecikme **> 300 ms** | ⚠ debounce 200→400 · model küçült · **yalnız leksik** kipe düş |
| p95 gecikme **> 500 ms** | 🔴 *«takıldı»* göstergesi **zorunlu** (Algolia eşiği) |
| `CLARIFY:*` oranı **düşmedi** | 🔴 öneri, cevapsızlığı **gizliyor** — `§12.2/③` gerçekleşti |
| erişim tabanı **geri gelmedi** (69/69/69/72) | 🔴 kapsam kaybı kapanmadı → **kazanç yok** |

### 20.3 Katalog gerçekleriyle karşılaşınca

| durum | karar |
|---|---|
| **iki öneri aynı etikete** sahip (Thread 4) | 🔴 katalog tutarlılık borcu **açılır**; etiket eki **anlamlı** olmalı, `(satış)` yetmez |
| ölçü **yön beyansız** (68/136) | üstünlük önerisi **sunulmaz**; `[↑]/[↓]` sorulur — ve bu bir **borç sayacına** yazılır |
| alan **çıplak** (sinonimsiz, 1 adet) | öneride **görünmez**; hasat kuyruğuna **otomatik** düşer |
| öneri **temsil edilemiyor** (JOIN) | 🔴 **sunulmaz** — 🆈 chip'in açıklaması bir vaattir |

### 20.4 Mimari sınırlarda

| durum | karar |
|---|---|
| öneri **küp seçiminde** yanılıyor | 🟢 tasarım doğru — büyük şema, `§18.10` lehimize |
| öneri **küp içi alan seçiminde** sürtünme yaratıyor | ◐ `§18.10` karşı kanıtı geçerli → küp içinde **çıkarıma güven**, yalnız **çok sahipli** alanda sor |
| kullanıcı **uzun cümle** yazıyor (>8 kelime / fiil var) | öneri şeridi **söner**; kademe ③ (garson taslağı) |
| kademe ③ **v1 kapsamında olmayacaksa** | 🔴 **ilan edilir** — sessizce kapsam dışı bırakmak `§12.2/③`'tür |
| pill satırı **6+ öğe** | adımlar **dikey**, yuvalar **yatay**; ikisi aynı şeritte **olmaz** |

### 20.5 Teknik seçimler — önceden verilmiş kararlar

| soru | karar | gerekçe |
|---|---|---|
| ANN mi exact mi | ✅ **exact** | ~1.000 vektör; `ADR-0024` determinizmi |
| füzyon | ✅ **RRF** başlangıçta, altın küme kurulunca **ölç ve seç** | *«RRF requires no tuning»*; ama *«neither dominates»* |
| `k` sabiti | 🔴 **bilinçli seç, miras alma** | 60 (Elastic) ↔ 2 (Qdrant) aynı ad, farklı sistem |
| ağırlık | ✅ **1.0 / 1.0** (altın küme yokken) | Qdrant: *«hand-tuned weights without measurement are unlikely to beat the default»* |
| model | ◐ **BGE-M3 önde** ama **ölçümle** seçilir | prefix derdi yok + sparse bedava; ⚠ Türkçe taahhüdü **yok** |
| E5 kullanılacaksa | 🔴 **iki tarafa da `query: `** | simetrik görev; kart birebir söylüyor |
| eşik tabanlı kabul | ⊘ **kullanılmaz** | E5 kosinüsü 0,7–1,0'da sıkışıyor → **sıralama** kullan |
| prefix mekanizması | ✅ **edge n-gram** (indeksleme zamanı) | Elastic `search_as_you_type` deseni |
| fuzzy eşiği | ≥4 krk → 1 hata · ≥7 krk → 2 hata · maks **2** | Algolia + Typesense **aynı** · ⚠ Türkçe'de **ölçmeden benimseme** |
| öneri adedi | **5–7** (tavan 10) · **kaydırma YOK** | Baymard |
| debounce | **200 ms** | Algolia ×2 |

---

## §21 · BU EKİN SINIRI

⚠ **`WebSearch` bütçesi tükendiği için literatür taraması yapılmadı** — yalnız bilinen
adresler çekildi. Dolayısıyla:
- Bulunamayan bir kanıt, **var olmadığı anlamına gelmez** 🅣.
- MTEB liderlik tablosu **okunamadı** (JS kabuğu) → model karşılaştırması **kart
  düzeyinde** kaldı.
- Snowflake'in sayısal doğruluk iddiası (blog) **404** → **kullanılmadı**.
- Power BI emeklilik blogu **403** → tarih yalnız `learn.microsoft.com`'dan doğrulandı.

🔴 **Ve en önemlisi:** `§18.6` literatürün **bize cevap veremediği** yeri işaretliyor —
kısa/tek kelime gömme performansı. **`§13.1` ölçümü bu yüzden ertelenemez.**

> *Bir kaynağın söylemediği şey, senin ölçmen gereken şeydir.*
