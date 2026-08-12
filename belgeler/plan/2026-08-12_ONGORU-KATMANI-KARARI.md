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

| kim | ne oldu | gerçek sebep |
|---|---|---|
| **Tableau Ask Data** | emekliye ayrıldı | LLM dalgası → Einstein/Pulse'a **yol haritası kayması** |
| **Power BI Q&A** | duruyor, öne çıkarılmıyor | Copilot'a kayma + *«teach Q&A»* = **elle** sinonim eğitimi |
| **ThoughtSpot** | 🔴 **bırakmadı** — search-first hâlâ omurga | LLM'i **kabuk** olarak üstüne koydu |

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
