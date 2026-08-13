# DİMA — v1 MİMARİ HARİTASI
## 🍽 *Bir restoran olarak okunur:* **garson konuşur · aşçı pişirir · kapılar arada durur**

**Bir prompt girildiğinde arkada ne oluyor · katmanlar · tüm dallar · test edilecek her şey**
**+ §0: 🔴 RESTORAN ANALOJİSİ — her parçanın tam karşılığı, ve analojinin NEREDE KIRILDIĞI**
**+ §16–17: v2 ve v3'te bu haritanın NERESİNE NE eklenecek**

Damga: `2026-08-09` · HEAD `b1afd58` · **ORKESTRATÖR YÜRÜRLÜKTE** *(`O-0`…`O-16` · bayrak
**`beta`** · garson artık
tek bir fiş yerine bir **PLAN** çevirebiliyor — bayrak `off`, gerekçesi ölçülmüş)*
⟳ **Önceki damga:** `2026-08-08` @`761928d` · *"garson ara fazı kapandı"* — **orkestratörden
ÖNCEYDİ.** Bu turda güncellenen bölümler `⟳ 2026-08-09` işaretini taşır.
⟳ **Ondan önceki:** `2026-08-05` @`eb48c40` · *"aktif faz FAZ 4"* — **ara fazdan ÖNCEYDİ.**
`⟳ 2026-08-08` işaretli satırlar o turun deltasıdır; **özgün metin silinmedi**,
üstüne yazıldı — çünkü bir haritanın *neyi yanlış bildiği* de bilgidir.

---

## 🔴 BU BELGENİN KIYMETİ YOKTUR — ÖNCE BUNU OKU

**Bu belge bir OTORİTE DEĞİLDİR. Türetilmiş bir haritadır ve hiçbir kararın dayanağı olamaz.**

| Ne | Otorite | Bu belgeyle çelişirse |
|---|---|---|
| **Kod** (`app/`, `tests/`, `demo/packs/`) | 🥇 **Nihai gerçek** | **Kod kazanır.** Belge yanlıştır |
| `backend/MIMARI.md` | 🥈 Mimari otorite | **MIMARI kazanır** |
| `belgeler/plan/DIMA-V1-YOL-HARITASI.md` | 🥉 Plan otoritesi | **Yol haritası kazanır** |
| ⟳ `belgeler/plan/DIMA-GARSON-ARA-FAZ.md` | 🥉 **Ara faz plan otoritesi** *(garson katmanı)* | **Ara faz kazanır** |
| ⟳ `belgeler/plan/2026-08-09_ORKESTRATOR-KATMANI-VE-OLCEKLENME.md` | 🥉 **Orkestratör faz otoritesi** *(`O-0`…`O-9`)* | **Rapor kazanır** — ⚠ *ama `E6` düzeltmesi bir A/B ile GERİ ALINDI; ölçüm rapordan da üstündür* |
| `OPERASYON-DURUM.md` | Durum kaydı | **Durum kaydı kazanır** |
| **BU BELGE** | ❌ **YOK** | — |

> ⟳ **2026-08-08 — analojinin kendisi de bir otorite DEĞİLDİR.** §0'daki restoran
> haritası bir **öğretme aracıdır**; sınırları **§0.9'da yazılıdır** ve orada bilerek
> *"analoji burada kırılır"* denen dört yer var. Bir benzetmeyi mimari gerekçe yerine
> koymak, bu deponun avladığı *"beyan var, kod onu tanımıyor"* sınıfının en tatlı hâlidir.

**Neden kıymeti yok — dört somut sebep:**

1. **Anında bayatlar.** İçindeki her sayı bir `HEAD` damgasına bağlı. Bir sonraki commit'te
   yanlış olabilir ve belge bunu **kendisi fark edemez**. Bir kapısı yoktur; kimse onu
   koşmaz; kırmızı vermez.
2. **Ölçmez, ANLATIR.** Bu deponun tek kabul edilen kanıt biçimi *"`<sayı> @<sha> · <komut>`"*.
   Buradaki şemalar bir komut değildir — **yeniden üretilemezler**.
3. **Bu deponun avladığı sınıfın ta kendisi olabilir.** *"Beyan var, kod onu tanımıyor."*
   Bir şema, kodun **anlatısıdır**; kodun kendisi değildir. Aşağıda en az bir yerde
   *(§7'deki `hedef_kiyasi` satırı)* tam olarak bu ayrışma **ölçülerek** bulundu ve yazıldı.
4. **Karar mercii değildir.** Bir bayrağın açılıp açılmayacağı, bir maddenin bitip
   bitmediği buradan **okunamaz** — ölçümden okunur.

> **Tek meşru kullanımı:** yönelim. *"Sistem kabaca nasıl işliyor, nereye bakmalıyım,
> neyi elle denemeliyim."* Bunun dışında bir şey için kullanılırsa **zarar verir**.
>
> Çelişki gördüğünde: **belgeyi düzeltme, kaynağı koş.**

---

## İÇİNDEKİLER

| § | Başlık |
|---|---|
| [0](#0--restoran--analojinin-tam-haritası) | 🔴 **RESTORAN — analojinin TAM haritası** *(⟳ yeni)* |
| [1](#1-üç-düzlem--sistem-mimarisi) | Üç düzlem — sistem mimarisi |
| [2](#2-yedi-katman--v1-sonundaki-hâli) | Yedi katman — v1 sonundaki hâli |
| [3](#3-derleme-zinciri--bir-katalog-nasıl-doğar) | Derleme zinciri — bir katalog nasıl doğar |
| [4](#4-🔴-bir-prompt-girildiğinde-tam-akış-tüm-dallar) | 🔴 **Bir prompt girildiğinde — TAM AKIŞ, tüm dallar** |
| [5](#5-cevaplama-merdiveni--8-basamak-normatif) | Cevaplama merdiveni — 8 basamak |
| [6](#6-red-kodları--r1r10-ve-eksik-r11) | Red kodları — R1…R10 |
| [7](#7-bayrak-envanteri--25-bayrak-tam-durum) | 🔴 **Bayrak envanteri — tam durum** |
| [8](#8-manuel-test-edilecek-her-şey--off-bayraklar) | 🔴 **Manuel test edilecek her şey** |
| [9](#9-ab-testi-yapılacak-her-şey) | 🔴 **A/B testi yapılacak her şey** |
| [10](#10-test-kapıları--ne-ölçüyor-ne-ölçemiyor) | Test kapıları — ne ölçüyor, ne ölçemiyor |
| [11](#11-v1-bitiş-ölçütleri--16-satır) | v1 bitiş ölçütleri — 16 satır |
| [12](#12-kalan-yol--faz-48--g) | Kalan yol — FAZ 4→8 + §G |
| [13](#13-bilinen-kırıklar-ve-açık-borçlar) | Bilinen kırıklar ve açık borçlar |
| [14](#14-frontend-yüzeyi--13-panel--36-bileşen) | Frontend yüzeyi |
| [15](#15-denetim--bu-belgenin-kendi-eksikleri-ölçüldü-kapatıldı) | **DENETİM** — bu belgenin kendi eksikleri *(6 boşluk kapatıldı)* |
| [16](#16-🔴-v2de-ne-eklenecek--bölüm-bölüm-delta) | 🔴 **v2'de NE EKLENECEK** — bölüm bölüm delta |
| [17](#17-🔴-v3te-ne-eklenecek--bölüm-bölüm-delta) | 🔴 **v3'te NE EKLENECEK** — bölüm bölüm delta |
| [18](#18-tek-bakışta-v1--v2--v3-birikimi) | Tek bakışta: v1 → v2 → v3 birikimi |

---

# 0 · RESTORAN — analojinin TAM haritası

> ⟳ **2026-08-08 · YENİ BÖLÜM.** Bu belgenin önceki sürümü *ara faz öncesinde* donmuştu ve
> sistemi **yalnız mutfak metrikleriyle** anlatıyordu. Ara faz (`DIMA-GARSON-ARA-FAZ.md`,
> 113 adım) o eksiği kapattı. Aşağısı, **her mimari parçanın restorandaki tam karşılığıdır**.

## 0.1 · Tek cümle — ve üç yasak

> 🔴 **«Garson olarak LLM'e güveniyoruz KESİNLİKLE; mutfakta HİÇ güvenmiyoruz.»**
> *(Kullanıcı kararı, `DIMA-GARSON-ARA-FAZ.md` §1.1c — bu fazın en önemli cümlesi.)*

Ve bu bir benzetme olarak **sonradan** uydurulmadı: deponun kendi denetimi, bu sohbetten
bağımsız olarak aynı cümleyi kurmuştu —

> *"Ürünün tezi (**«LLM garson, küp aşçı»**) doğru — ama bugün **garson yok, siparişi aşçı
> alıyor.**"* — `belgeler/denetim/2026-08-05_ANLAMA-KATMANI.md`

**Ara fazın tanımı buydu:** çözümleme işini eşleştiriciden almak ve **ona ait olan katmana**
vermek. `route()` kötü bir eşleştirici değil; **yanlış işi yapan iyi bir eşleştiriciydi.**

```
┌─ ÜÇ YASAK — hepsi teste bağlı ────────────────────────────────────────────┐
│  1 · GARSON TENCEREYE KARIŞAMAZ                                           │
│      LLM sayı koyamaz · SQL yazamaz · motora dokunamaz · ham satır görmez │
│                                    kapı: parse_cube_query · narration_guard│
│  2 · AŞÇI SALONA ÇIKAMAZ                                                  │
│      Mutfak modülü doğal dil ayrıştıramaz · kullanıcıya cümle yazamaz     │
│                                    kapı: tests/test_alan_haritasi.py (AST)│
│  3 · İKİSİNİ BİRDEN YAPAN HER ŞEY «KAPI» OLMAK ZORUNDADIR                 │
│      Kapı olmayan bir "ikisi de", TANIMI GEREĞİ bir kusurdur    (KAT-1)   │
└───────────────────────────────────────────────────────────────────────────┘
```

## 0.2 · Bir siparişin tam yolculuğu — ana şema

```mermaid
flowchart TB
    M(["👤 <b>MÜŞTERİ</b><br/>serbest Türkçe · dağınık · eksik · yazım hatalı"])

    subgraph SALON["🪑 SALON — app/routers/ask.py · POST /ask"]
        direction TB
        KAP{"<b>KAPIDA KARŞILAMA</b><br/>🚩 sosyal_sinif <i>prod</i><br/><i>'teşekkürler' → 0 LLM · 0 SQL</i>"}
        DEF["<b>GARSONUN DEFTERİ</b> — K2 · 0 token<br/>context.coz · followup.sinifla<br/><b>diyalog.py</b> 🚩 diyalog_bellegi <i>prod</i><br/><i>slot · devam · onarım · çapa</i>"]
    end

    subgraph GARSON["🗣 GARSON — K3a · ANLAMA · 'hangi sorgu koşacak?'"]
        direction TB
        NIY["<b>niyet.py</b> — çözümleme<br/><i>şemasız · salt dilbilgisi</i>"]
        ESL["<b>cube_router.route()</b> — eşleştirme<br/>🔴 <b>hızlı yol, kapı bekçisi DEĞİL</b>"]
        SOR["<b>SORAR</b> — netleştirme chip'i<br/>eşsizlik ∨ dar marjin"]
        LLM["<b>Intent-JSON</b> — LLM yapı doldurur<br/><i>SQL YAZMAZ</i>"]
        NIY --> ESL
        NIY --> SOR
        NIY --> LLM
    end

    FIS["📋 <b>SİPARİŞ FİŞİ = CubeQuery</b><br/>cube · measures · dimensions · filters<br/>timeDimensions · <b>referans</b><br/><i>hangi daldan geldiği AŞAĞIDAN GÖRÜNMEZ</i>"]

    KAPI1["🚪 <b>SERVİS PENCERESİ</b><br/><code>parse_cube_query()</code><br/>🔴 <b>KATI BEYAZ LİSTE</b><br/><i>menüde olmayan yemek fişe yazılamaz</i>"]

    subgraph MUTFAK["🍳 MUTFAK — K1 · %100 deterministik · DOKUNULMAZ"]
        direction TB
        REC["<b>REÇETE DEFTERİ</b><br/>compose() ⟵ kaynak⊕modül⊕sektör<br/>⊕kesişim⊕çekirdek⊕şirket<br/><i>GRAIN sözleşmesi — fail-closed</i>"]
        OCAK["<b>OCAK</b> — wren-core<br/>dry_plan → SQL → lehçe"]
        TART["<b>TARTI</b> — stats · interpret<br/><i>trend · anomali · pay · eşik</i>"]
        REC --> OCAK --> TART
    end

    HIJ["🧼 <b>HİJYEN</b> — L0 GÜVENCE<br/>authorize() · RLS · CLS · always_filter<br/>audit · PII · Query Contract mührü"]

    HAVA["🔴 <b>HAVA BOŞLUĞU</b> — llm_guard.safe_call + yayilim.py<br/>ham satır ⛔ ASLA ÇIKMAZ<br/>12.430 → <code>&#123;&#123;NUM_1&#125;&#125;</code> · 'RAM 3' → <code>&#123;&#123;DIM_1&#125;&#125;</code><br/>'Ahmet Tekstil' → <code>&#123;&#123;ENT_1&#125;&#125;</code><br/><i>garsona menü ezberletilir; KASA gösterilmez</i>"]

    subgraph SERVIS["🍽 GARSON — K3b · SERVİS · 'insana ne diyeceğiz?'"]
        direction TB
        TEM["<b>SİPARİŞİ TEKRARLA</b> — temellendirme.py<br/>🔴 <b>0 token</b> — LLM düşse bile YAŞAR"]
        ANL["<b>TABAĞI ANLAT</b> — anlatici.py<br/>🚩 t2_anlatici <i>alpha</i>"]
        EK["<b>EK MOTORU</b> — ek.py<br/><i>'Mart'ta' · 'fire'yi'</i>"]
        MEN["<b>MENÜYÜ BİL</b> — yetenek.py<br/><i>yapamadığında NE yapabildiğini söyler</i>"]
    end

    subgraph PASS["🔒 PASS — üç kapı, fail-closed, çıkıştan ÖNCE"]
        direction TB
        P1["① <b>GERİ KOYMA</b> — yayilim.geri_koy<br/><code>&#123;&#123;NUM_1&#125;&#125;</code> → 12.430<br/>eksik/fazla yer tutucu → <b>cümle DÜŞER</b>"]
        P2["② <b>narration_guard</b><br/>her SAYI ±%2 → <b>cümle DÜŞER</b>"]
        P3["③ <b>iddia.py</b><br/>her İDDİA şemaya karşı"]
        P1 --> P2 --> P3
    end

    SEAL["🔒 <b>answer.py::seal()</b> — TEK ÇIKIŞ<br/><i>adisyon: makbuz · PII maskesi · audit · sözleşme</i>"]

    M --> KAP
    KAP -->|"veri niyeti VAR"| DEF
    KAP -->|"YOK"| SEAL
    DEF --> GARSON
    SOR -.->|"❓ CEVAP DEĞİL, SORU"| SEAL
    ESL --> FIS
    LLM --> FIS
    FIS --> KAPI1
    KAPI1 -->|"✅ geçti"| MUTFAK
    KAPI1 -->|"🔴 uydurulmuş ad"| RED(["<b>DÜRÜST RET</b><br/>source=null"])
    HIJ -.-> MUTFAK
    MUTFAK -->|"FACT-SHEET ~150-250 token"| HAVA
    HAVA --> SERVIS
    SERVIS --> PASS
    PASS --> SEAL
    RED --> SEAL
    SEAL --> OUT(["👤 rozet · <b>TEMELLENDİRME</b> · tablo/grafik<br/><b>ANLATI</b> · chip'ler · <b>MAKBUZ</b>"])

    style MUTFAK fill:#1b5e20,color:#fff
    style GARSON fill:#4a148c,color:#fff
    style SERVIS fill:#4a148c,color:#fff
    style KAPI1 fill:#b71c1c,color:#fff
    style HAVA fill:#7d1128,color:#fff
    style PASS fill:#b71c1c,color:#fff
    style SEAL fill:#4a148c,color:#fff
    style HIJ fill:#37474f,color:#fff
    style SALON fill:#0d3b66,color:#fff
    style FIS fill:#004d40,color:#fff
    style RED fill:#37474f,color:#fff
```

## 0.3 · 🔴 TAM KARŞILIK TABLOSU — restorandaki her şeyin DİMA'daki yeri

> **Kural:** *etiketsiz kutu yoktur.* Bir satırın **modülü** ya da **kapısı** boşsa, o parça
> ya yoktur ya da sahibi belirsizdir — ikisi de bu depoda **bulgu**dur.

### 🪑 SALON — müşterinin gördüğü yer

| Restoranda | DİMA'da | Modül / uç | Kapı | Durum |
|---|---|---|---|---|
| Kapıda karşılama | sosyal sınıf ayrımı | `ask.py` merdiven basamağı 0 | 🚩 `sosyal_sinif` **prod** | ✅ |
| Masaya oturma | oturum + JWT | `POST /ask` · `authorize()` | `query:run` | ✅ |
| Masadaki tabaklar | önceki cevap kartları | `context.coz()` çapa kuralları | `KURAL_CELISKI` → **SOR** | ✅ |
| *"Şu tabaktan bir de…"* | karta yanıt | 🚩 `capa_zinciri` | `reply_to_cube_query` | ⚫ off |
| Salonun kendisi | PUBLIC düzlem | `app/` · `uvicorn app.main:app` | JWT | ✅ |
| Müdür odası *(ayrı kapı, ayrı anahtar)* | ADMIN düzlem | `admin_app/` — **ayrı süreç, Wren'siz** | ayrı JWT secret + `sa` + **2FA** | ✅ |
| İşletme defterleri *(personel · yetki · kasa)* | CONTROL-PLANE | `control_plane/` — **kütüphane** | `authorize()` matrisi | ✅ |

### 🗣 GARSON — dil işi *(K3 · LLM'e TAM güven)*

| Restoranda | DİMA'da | Modül | Kapı | Durum |
|---|---|---|---|---|
| **Siparişi kendi dilinle almak** | NL → niyet çözümleme | `niyet.py` *(401 satır)* | — *(şemasız, salt dilbilgisi)* | ✅ ara faz |
| Menüdeki adı bilmek | terim → katalog eşleştirme | `cube_router.route()` | 🔴 **hızlı yol, bekçi DEĞİL** | ✅ |
| Ezberlediği müdavim siparişi | VQR replay | `vqr.py` | ölçü tutarlılığı | ✅ |
| **Siparişi TEKRARLAMAK** | temellendirme | `temellendirme.py` *(157)* | 🔴 **0 token** | ✅ `G1` |
| **Emin değilse SORMAK** | netleştirme chip'i | `belirsizlik_chipi.py` · `netlestirme.py` | eşsizlik ∨ **marjin** | ✅ |
| **Sorduğunu HATIRLAMAK** | diyalog belleği | `diyalog.py` *(177)* | 🚩 `diyalog_bellegi` **prod** | ✅ `G2` |
| **Düzeltilmek** *("hayır, fire demiştim")* | onarım — TEK slot düzelir | `diyalog.py` onarım dalı | deterministik test | ✅ `G2` |
| Yazım hatasını anlamak | typo önerisi | `typo_onerisi.py` | 🔴 **merdiveni KESEMEZ** (`KAT-2`) | ✅ `G3` |
| **Tabağı ANLATMAK** | T2 anlatısı | `anlatici.py` *(133)* | 🚩 `t2_anlatici` **alpha** | ◐ |
| Türkçe konuşmak *(çekim ekleri)* | ek motoru | `ek.py` *(202)* | özel ad kipi *(TDK)* | ✅ `G7` |
| **MENÜYÜ BİLMEK** | kapasite beyanı | `yetenek.py` · `katalog_metni.py` | `iddia.py` denetler | ✅ `G8` |
| Tek ses tonu | metin katalogu | `soz.py` | — | ◐ *(5.17)* |
| Kıyas dili *("geçen yıla göre")* | kıyas cebiri | `kiyas_cebiri.py` *(265)* | 🚩 `referans_dili` **beta** | ✅ `G6` |
| ⟳ **Siparişi ADIMLARA bölmek** *("önce şunu bak, sonra onu kıyasla")* | plan çevirisi — **fiş değil, fiş DİZİSİ** | `plan_garson.py` · `plan_semasi.py` | 🚩 `orkestrator_plan` **`beta` ✅** · 🔴 **kapalı fiil kümesi** — **15 fiil** *(`enum`)* | ✅ ⟳ `O-14` |

### 📋 SİPARİŞ FİŞİ — garsonla mutfağın **tek** ortak dili

| Restoranda | DİMA'da | Modül | Kapı |
|---|---|---|---|
| Fişin kendisi | `CubeQuery` — **CEBİR, form değil** | `schemas.py` · L2 DİL | — |
| Fişin şablonu | Intent şeması | `intent_semasi.py` *(`oneOf` — her cube kendi dalı)* | 🚩 `llm_sema_kisitli` ⚠ **NO-OP** |
| Fişteki *"yanına bir de…"* | `cross_cube_add` *(blend)* | `ask.py` basamak 4 | grain-**FARKINDA** |
| Fişteki *"aynısı ama X bazında"* | `deterministic_refine()` | `ask.py` basamak 3 | **LLM YOK** |
| Fişteki *"geçen seferkine göre"* | `referans` alanı | `kiyas_cebiri.py` | 🚩 `referans_dili` |
| 🔴 **Fişin mutfağa girdiği delik** | `parse_cube_query()` | `cube_router.py:3715` | 🔴 **KATI BEYAZ LİSTE** |

> 🔴 **Bu satır mimarinin bel kemiğidir:** hangi daldan geldiği *(route · Intent-JSON ·
> chip · refine)* **fişin altında görünmez**. Mutfak **kimin yazdığını bilmez**, yalnız
> **geçerli mi** ona bakar. *Sağlayıcıdan bağımsız asıl emniyet ağı budur* — model uydurma
> bir ölçü adı üretebilir; sistem onu **çalıştıramaz**.

### 🍳 MUTFAK — sayı işi *(K1 · LLM'e SIFIR güven · 🔴 DOKUNULMAZ)*

| Restoranda | DİMA'da | Modül | Kapı |
|---|---|---|---|
| **Reçete defteri** | semantik katalog | `compose()` — kaynak⊕modül⊕sektör⊕kesişim⊕çekirdek⊕şirket | **FAIL-CLOSED** |
| Reçetenin porsiyon birimi | **GRAIN sözleşmesi** | `compose.py` | 🔴 `GrainIhlali` → **iki ayrı metrik** |
| Aynı adı taşıyan iki reçete | metrik hakemi | `metrik_kaydi.py` | 🚩 `metrik_kaydi` |
| Kiler / mise-en-place | `target/mdl.json` *(base64)* | `mdl_writer.py` · `materialize()` | **DB → dosya, TEK YÖNLÜ** |
| **Ocak** | WrenEngine — in-process | `wren_service.py` | `dry_plan` — **çalıştırmadan doğrula** |
| Ocağın emniyet valfi | `guard_sql` | yalnız `SELECT`/`WITH` + lehçe çevirisi | fail-closed |
| **Tartı** | istatistik + olgu çıkarımı | `stats.py` · `interpret.py:359` | 🔴 **ham satır değil, OLGU** |
| Ayrıştırma *("artışın %kaçı kimden")* | PVM ayrıştırması | `contribution.py` | `ayristirilabilir_mi` — **`AVG` ayrıştırılamaz** |
| Dolaptaki müşteri dosyaları | ham satırlar | — | 🔴 **binadan ÇIKMAZ** |
| 🔴 **Garson mutfağa girerse** | **Discovery** — LLM ham SQL yazar | `discovery_kuyrugu.py` | ⚠ **§0.7'ye bak: bu bir İSTİSNA** |

### 🧼 HİJYEN — L0 GÜVENCE *(görünmez, ama her tabakta var)*

| Restoranda | DİMA'da | Modül | Kapı |
|---|---|---|---|
| Personel kartı | `Principal` | `control_plane/` | `authorize()` matrisi |
| *"Bu masaya yalnız bu garson bakar"* | satır seviyesi izolasyon | `rls.py` · `always_filter` | 🚩 `motor_rls` — gölge |
| *"Bu kolonu kimse görmez"* | CLS | `katman_b.py` | 🔴 **`motor_cls` KİLİTLİ** — §13/1 |
| Kişisel veri | PII maskesi | `pii.py` | `seal()` içinde + **ayrı audit** |
| **HACCP kaydı** | audit zinciri | `audit_zinciri.py` | 🔴 **FAIL-CLOSED** |
| **Adisyon mührü** | Query Contract | `contracts.py` | SHA-256 + MDL sürümü |
| Tazelik etiketi | tazelik kademesi | `tazelik.py` | 🚩 `tazelik` ⚫ off |
| Ürünün kaynağı | lineage | `lineage.py` | 🚩 `lineage` ⚫ off |
| Reçeteyi kim onayladı | metrik sertifikası | `certification.py` | 🚩 `metrik_sertifikasi` ⚫ off |

### 🔴 HAVA BOŞLUĞU — mutfakla dış dünya arasındaki **tek** geçit

| Restoranda | DİMA'da | Modül | Durum |
|---|---|---|---|
| Garsona menü ezberletirsin | soru + katalog **adları** LLM'e gider | `llm_guard.safe_call` | ✅ |
| **Kasayı gösterme** | gerçek sayı → `{{NUM_i}}` | `yayilim.py` *(198)* | ✅ `G0b` |
| **Müşteri dosyasını gösterme** | boyut değeri → `{{DIM_i}}` · varlık → `{{ENT_i}}` | `yayilim.py` · `varlik.py` | ✅ / ⚠ `S5` |
| TCKN · e-posta · telefon · IBAN | PII kalıpları | `pii.py` | ✅ |
| Çıkış kütüğü | **tür + SAYI**, değer YAZILMAZ | `llm_guard.py` | ✅ |
| Düşme oranı alarmı | guard telemetrisi | `guard_alarmi.py` + `/health/ready` | ✅ `Ö5` |

### 🔒 PASS ve ADİSYON — çıkış

| Restoranda | DİMA'da | Modül | Kapı |
|---|---|---|---|
| Yer tutucuları geri koyma | `{{NUM_1}}` → `12.430` | `yayilim.geri_koy` | 🔴 eksik/fazla → **cümle DÜŞER** |
| Şefin son kontrolü — **sayı** | anlatıdaki her sayı ±%2 | `narration_guard.py` | 🔴 fail-closed → cümle düşer |
| Şefin son kontrolü — **iddia** | *"olmayan yetenek vaadi"* | `iddia.py` *(221)* | 🔴 fail-closed | 
| **Pass — tek pencere** | `seal()` | `answer.py::seal()` | 🔒 **TEK ÇIKIŞ NOKTASI** |
| Adisyon | makbuz + `explain` | `answer.koken()` · `contracts` | Query Contract kaydı |
| *"Bugün bu yok"* | **dürüst red** | `source=null` | 🔴 *"anlamadığını bil"* |

### 🏢 İŞLETME — salonun dışında kalanlar

| Restoranda | DİMA'da | Modül |
|---|---|---|
| Şefin kural defteri | ADR'ler + `KAT-1…KAT-5` | `MIMARI.md` · `docs/adr/` ⚠ **0 dosya** |
| Yeni şube açılışı | tenant açılış zinciri | `db_introspect` → `coldstart.oner()` → `ReviewPanel` |
| Menü genişletme kuyruğu | terfi kuyruğu | `terfi_kapanis.py` · `measures` router |
| Paket servis | rapor · pano · zamanlama | `report.py` · `dashboards` · `schedules` |
| Sipariş defterinin arşivi | sohbet + `interaction_log` | `conversations` router |
| Mutfak yükü | LLM sağlayıcı zinciri | `llm.py` — ⟳ **karar: OpenRouter + NVIDIA açık kaynak** |

## 0.4 · 🔴 GÜVEN MODELİ — iki eksen, ve ikisi de bağlayıcı

**Eksen 1 — LLM neyi YAPAR:**

| İş | LLM'e güven | Gerekçe |
|---|---|---|
| **GARSON İŞİ** — anlamak · sormak · hatırlamak · anlatmak | 🟢 **TAM** | Dilde LLM `route()`'tan **açık ara** iyidir. Ölçüldü: 41 gerçek cümlenin **0'ında** `route()` cevap üretiyor |
| **MUTFAK İŞİ** — sayı · hesap · SQL · yetki | 🔴 **SIFIR** | Sayı yalnız küpten. `parse_cube_query` · `dry_plan` · RLS · sözleşme mührü — **hiçbiri LLM'e sormaz** |

**Eksen 2 — LLM neyi GÖRÜR** *(ara fazın eklediği, daha önce bu haritada HİÇ yoktu)*:

| | LLM ne **YAPAR** | LLM ne **GÖRÜR** |
|---|---|---|
| **Garson işi** | 🟢 tam güven | ⚠ **sınırlı** — soru + katalog **adları** + `{{yer tutucu}}`lar |
| **Mutfak işi** | 🔴 sıfır | 🔴 **hiç** — ham satır · gerçek değer · gerçek sayı **çıkmaz** |

> *Bir garsona menüyü ezberletirsiniz; **kasayı ve müşteri dosyalarını göstermezsiniz.***

🔴 **Ve bir yanlış okuma, bu belgenin önceki sürümünün de düştüğü hata:** *"LLM'e
güvenilmediği için ancak çok eminken LLM'siz gidiyoruz"* **DEĞİL**. Gerçek bunun tersi:
LLM'siz niyet algılamak **zordur** — güven duyulmayan `route()`'tur. `route()` yalnız
**maliyet ve hız** için, ve **yalnız kendini ispat edebildiği yerde** kullanılır.
**İspat yükü `route()`'un üzerindedir, LLM'in değil. Şüphede LLM'e düşülür.**

⚠ **Bunun ölçüm sonucu:** `doğru-cube %` bir **kalite** ölçüsü değil, bir **MALİYET**
ölçüsüdür — *"mutfak, garsona hiç uğramadan kaç siparişi karşıladı?"* **Maliyet ölçüsü
ürünü veto edemez** *(§2.3 kabul rejimi)*.

## 0.5 · 🚪 KAPILAR — hijyen bariyerlerinin tam listesi

| Kapı | Yön | Ne zorlar | Durum |
|---|---|---|---|
| `parse_cube_query` `cube_router.py:3715` | 🗣→🍳 | 🔴 **Katı beyaz liste** — şema dışı ad **çalıştırılamaz** | ✅ |
| `uyum.denetle` `uyum.py:169` | 🗣→🍳 | Niyet ↔ sorgu uyumu · **beyan-açık** | ✅ |
| ⟳ `plan_semasi` `FIILLER` + `ZORUNLU_ALANLAR` | 🗣→🍳 | 🔴 **Kapalı fiil kümesi** — plan yeni fiil **icat edemez** (`enum`); adı doğru yazıp **parametresini uyduran** adım düşürülür | ✅ ⟳ `O-2` |
| `dry_plan` `wren_service.py:1504` | 🍳 içi | Sorgu **çalıştırılmadan** motorca doğrulanır | ✅ |
| `planner` dört kapı | her araç | kayıt · yetki · **det-önce** · bütçe | ✅ |
| `interpret()` `interpret.py:359` | 🍳→🗣 | 🔴 **Ham satır değil, OLGU çıkar** | ✅ |
| `llm_guard.safe_call` | 🗣→🌐 | PII fail-closed · `_ask`/`_arac_ile`/`_chat`'i sarar | ✅ |
| `yayilim.py` **korunan yayılım** | 🍳→🌐 | Gerçek **DEĞER ve SAYI** da çıkmaz | ✅ ⟳ `G0b` |
| `narration_guard` | 🗣→👤 | Metindeki her **SAYI** ±%2 → cümle düşer | ✅ |
| `iddia.py` | 🗣→👤 | Her **İDDİA** şemaya karşı | ✅ ⟳ `G4` |
| `pii.py` | sistem→👤 | Maskeleme, tek çıkış | ✅ |
| `answer.seal()` | herkes→👤 | 🔒 **TEK ÇIKIŞ** — makbuz · audit · sözleşme | ✅ |
| `tests/test_alan_haritasi.py` | **AST** | 🗣 modülü `wren_service` import **edemez**; 🍳 modülü `llm`/`soz` import **edemez** | ✅ ⟳ |

> 🔴 **Ayrım testi — üç soru, herkes uygulayabilir:**
> ① Bu modül **doğal dil** okuyor ya da yazıyor mu? → 🗣 **GARSON**
> ② Bu modül **veri/sorgu/motor** ile mi çalışıyor? → 🍳 **MUTFAK**
> ③ **İKİSİ DE** mi? → 🔴 **O zaman KAPI olmak ZORUNDA.** Kapı olmayan bir *"ikisi de"*,
> tanımı gereği bir **KUSURDUR**.

⚠ **Üç bilinçli tehlikeli vaka:** `cube_router.py` *(4277 satır)* **iki alanı birden**
barındırır — `route()` 🗣, `parse_cube_query()` 🚪. Bu kusur değil *(kapı, koruduğu şeyin
yanında durur)* ama **risktir**: dosyayı düzenleyen **hangi tarafta olduğunu bilmek
zorundadır**. `interpret.py` ve `value_index.py` **köprüdür** — mutfak üretir, garson tüketir.

## 0.6 · 🔻 BOZULMA MERDİVENİ — *"garson hastalanırsa"*

**Her basamakta cevap hâlâ DOĞRUdur; kaybedilen tek şey AKICILIKTIR.**

| # | Ne bozuldu | Sistem ne yapar | Müşteri ne görür |
|---|---|---|---|
| **0** | — | tam akış | 🟢 **Tam garson** — anlar · sorar · hatırlar · anlatır |
| **1** | Guard bir cümleyi düşürdü | o cümle yayımlanmaz | anlatı **kısalır**, sayılar doğru |
| **2** | Guard/`iddia` **tüm** cümleleri düşürdü | anlatı hiç eklenmez | `interpret.summary` — *"süssüz ama doğru"* |
| **3** | **LLM erişilemez** *(kota · ağ · 429)* | Intent-JSON yok → `route()` tek başına | deterministik cevap **+ temellendirme** |
| **4** | `route()` de çözemedi | **dürüst red + MENÜ** | *"bunu yapamam — ama şunu yapabilirim"* |
| **5** | Katalogda hiç karşılık yok | dürüst red + terfi kuyruğuna kayıt | *"kapsam dışı"* — ve yönetici görür |

> 🔴 **Tasarımın en önemli özelliği bu tablodadır:** `temellendirme` **0 token** olduğu için
> **3. basamakta bile hayatta kalır.** *Garson hastalanırsa **mutfak yine de siparişi tekrar
> eder**.*
> ⚠ Ve **hiçbir basamakta yanlış sayı yok.** Bozulma **akıcılığı** düşürür, **doğruluğu**
> değil.

## 0.7 · Cevaplama merdiveninin restoran okuması — §5'in aynası

| # | Basamak | Restoranda ne oluyor | `source` |
|---|---|---|---|
| 0 | sosyal sınıf | *"İyi akşamlar"* — mutfağa hiç haber gitmez | `meta` |
| 1 | meta · katalog | Müşteri **menüyü okuyor** | `catalog` `statement` |
| 2 | VQR replay | *"Her zamankinden"* — garson zaten biliyor | `vqr` |
| 3 | `route()` | Garson **menüdeki adı tanıdı**, fişi hemen yazdı | `cube` |
| 4 | `deterministic_refine` | *"Aynısı ama az tuzlu"* — fiş **düzenlenir**, yeniden yazılmaz | `cube` |
| 5 | `cross_cube_add` | *"Yanına bir de X"* — ⚠ **blend, gerçek JOIN değil** | `cube` |
| — | netleştirme chip'i | 🔴 **Garson SORUYOR** — cevap değil, **SORU** | chip |
| 6 | **Intent-JSON** | Garson **fişi kendi doldurdu**, mutfağa verdi | `cube+llm` |
| 7 | ⚠ **Discovery** | 🔴 **GARSON MUTFAĞA GİRDİ, kendi tabağını yaptı** | `llm:<sağlayıcı>` |
| 8 | dürüst red | *"Bunu yapamam"* — **+ menü** *(`G8`)* | `null` |

> 🔴 **7. basamak neden bir ANOMALİDİR — analojinin en öğretici satırı:** Discovery'de
> yemek çıkar, ama **reçetesi yok, tartısı yok, fişi yok**. Kod karşılığı birebir budur:
> `cube_query` üretilmez → `next_steps` **BOŞ** · `recommendations` **BOŞ** ·
> `calculation_explanation` **BOŞ** · `/ask/drill` **dürüstçe reddeder**.
> **Ölçülen fatura:** Discovery **12.567 ms / 24.352 token** ⟷ aynı tenant'ın cube yolu
> **145–434 ms / 0 token**.
> **Her Discovery cevabı, belgelenmiş bir kapsam boşluğudur ve bir terfi adayıdır.**

## 0.8 · ⟳ ARA FAZIN BU HARİTAYA GETİRDİĞİ DELTA — *bu belge neyi yanlış biliyordu*

**Bu belgenin ara faz öncesi hâli aşağıdaki satırları yazıyordu. Sağ sütun bugün ölçülendir.**

| Bu belgenin ESKİ iddiası | ⟳ **2026-08-08 · ölçülen** | Kanıt |
|---|---|---|
| *"§2 — v1'de gerçekten yeni olan dört şey, hepsi `[YOK]`"* | 🔴 **Üçü İNDİ** — `iddia.py` **221 satır** · diyalog katmanı `diyalog.py` **177** · referans cebiri `kiyas_cebiri.py` **265** | `wc -l app/*.py` @`761928d` |
| *"`R11` yok — v1'de yazılacak"* | ⊘ **DENENDİ ve GERİ ALINDI** — gerçek gerekçe (`R9`,`R1`) zaten vardı, `R11` onu **örtüyordu** | `cube_router.py:3530-3538` |
| *"`app/iddia.py` YOK — tek kapatılmamış uydurma"* | ✅ **KAPANDI** (`G4`); ⚠ ayrıca `yetenek` beyanı bu kapıyı **atlıyordu**, o da kapatıldı (`G8.4`) | ara faz §DURUM |
| *"`AJ0` typo kısa devresi — Discovery'ye hiç gidilmiyor"* | ✅ **`G3` indi** — cırcır artık **tavan+azalma** yönünde (`<= 11` ∧ `== 11` meta-kapı) | `tests/test_kisa_devre_yok.py:190,196` |
| *"25 bayrak · 21 YAML · **ölü bayrak 2**"* | ⟳ **49 kayıt · 48 YAML · ölü bayrak 1** *(`ayni_grain_gocu` — **derleme zamanı**, bilinçli)* | `FLAG_REGISTRY` ↔ `features.yml` @`761928d` |
| *"`hedef_kiyasi` bayrağı kayıtta YOK"* *(§13/8)* | ✅ **KAPANDI** — `features.py:53` **ve** `features.yml:100` | `grep hedef_kiyasi` |
| *"66 HTTP ucu"* | ⟳ **75 uç** | `grep -rhoE '@router\.(get\|post\|put\|delete\|patch)' app/routers/*.py \| wc -l` |
| *"`ask()` = 1147 satır"* | ⟳ `app/routers/ask.py` **4938 satır** — 🔴 **tavan borcu BÜYÜDÜ** | `wc -l` |
| *(hava boşluğu kavramı **hiç yoktu**)* | 🔴 **YENİ KATMAN** — `yayilim.py` · `guard_alarmi.py` · `varlik.py` | `G0b` · `Ö5` |
| *(temellendirme kavramı **hiç yoktu**)* | 🔴 **YENİ** — `temellendirme.py`, **0 token**, bozulmanın 3. basamağında yaşar | `G1` |
| *"§10 — dört kapı, iki rejim"* | ⟳ **BEŞİNCİ ALET:** `lab/garson.py --live` — **garsonu görebilen ilk ölçüm** | `lab/reports/garson/*.md` |
| *(sağlayıcı kararı yoktu)* | ⟳ **OpenRouter + NVIDIA açık kaynak, TEK MODEL.** Sonucu: 🔴 `llm_sema_kisitli` **kalıcı NO-OP** *(OpenAI-uyumlu uçlar `oneOf` desteklemiyor)* | ara faz §7.4 |

🔴 **Ve bir uyarı, ara fazın kendi öz-eleştirisinden — bu haritayı okuyan herkes bilmeli:**

> *"Bu fazda koşulan **her kapı `route()`'u ölçtü.** Korpus `dogru_cube` · `sessiz_yanlis` ·
> `gercek_dunya` — üçü de **deterministik yolun** metriği. Sonuç: **varsayılan yolu (LLM)
> neredeyse hiç ölçmüyoruz.***
> **Bir mimaride varsayılan olan yol, en az ölçülen yol olmamalıdır — yoksa ölçüm sistemi,
> sistemin kendisinden farklı bir şeye inanmaya başlar.***"

## 0.9 · 🔴 ANALOJİ NEREDE KIRILIR — dört yer

> Bir benzetmenin en tehlikeli anı, **açıkladığı şeyin yerine geçtiği** andır. Aşağısı,
> restoran resminin **yanlış** olduğu yerlerdir; bunları bilmeden analojiyi kullanmak,
> bu deponun avladığı *"beyan var, kod onu tanımıyor"* sınıfını üretir.

| # | Restoranda | DİMA'da **BÖYLE DEĞİL** |
|---|---|---|
| **1** Discovery.** 7. basamakta LLM ham SQL yazar. Bu bir tasarım tercihi değil, **kapatılmamış bir kapsam boşluğudur** — ve her kullanımı bir **terfi adayıdır** *(§5.2)* | Aslında discovery yan dükkandan sipariş etmek demektir. Ve o durumda  mutfakta pişirmemek demektir. Sonra aşçı o yemeği yapmayı öğrenir bizim mutfağı geliştirmekle. 
| **2** | Garson **tek kişidir** | 🔴 Garson **beş sağlayıcılı bir zincirdir** *(`anthropic → gemini → groq → xai → openrouter → ollama`)*, ve `rule` sağlayıcısı **zincirde DEĞİLDİR** *(demo şemasına gömülü, kasıtlı aptal)*. ⚠ Bu ayrım bir kez **ölçümü kirletti**: kısa devre yasağının *"korpusu düşürdüğü"* bulgusu, aslında *"garsonun yerine mutfağın en aptal yedeğini koyunca"* ölçülmüştü | Garson sistemde mantık olarak tektir ama farklı kişilikleri vardır.  
| **3** | Aşçı **bir kişidir**, reçeteyi bilir | 🔴 Mutfak **altı katmanın bileşimidir** *(kaynak⊕modül⊕sektör⊕kesişim⊕çekirdek⊕şirket)* ve aynı ad **farklı grain'de** pişebilir. *"Üç şirkette karşılaştırılamaz üç sayı"* yangını tam buradan çıktı → **GRAIN sözleşmesi** |
| **4** | Müşteri **tek masada** oturur | 🔴 Aynı prompt **eş zamanlı çok tenant · çok rol · çok mercek** altında koşar. Bayrak kapsamı **beş kademelidir** *(global < sektör < tenant < rol < kullanıcı)*; *"bir müşteri, bir sipariş"* sezgisi **burada yanıltır** |

> ⚠ **Beşinci ve en sinsi kırılma — analojinin kendisi hakkında:** restoran resmi
> **anlatmakta iyi, ölçmekte kötüdür.** Hiçbir kapı bu bölümü koşmaz, hiçbir test onu
> kırmızı veremez. §0'ın tamamı **yönelimdir**; karar mercii **kod ve alettir**.

---

# 1. Üç düzlem — sistem mimarisi

> ⟳ **Restoran okuması:** 🪑 **PUBLIC = SALON** *(müşterinin girdiği yer)* ·
> 🔐 **ADMIN = MÜDÜR ODASI** *(ayrı kapı, ayrı anahtar, zorunlu 2FA)* ·
> 📚 **CONTROL-PLANE = İŞLETME DEFTERLERİ** *(personel · yetki · kasa — ikisi de okur)* ·
> ⚙ **MOTOR = MUTFAK.** Tam karşılıklar §0.3'te.

```mermaid
flowchart TB
    subgraph PUBLIC["🌐 PUBLIC DÜZLEM — app/ · uvicorn app.main:app"]
        direction TB
        FE["React SPA<br/>dima-frontend-demo-master<br/>13 panel"]
        API["FastAPI<br/>/ask · /cube · /report · /ask/drill<br/>/dashboards · /schedules · /metrics"]
        FE -->|JWT| API
    end

    subgraph ADMIN["🔐 ADMIN DÜZLEM — admin_app/ · AYRI SÜREÇ, Wren'siz"]
        SA["/sadmin/*<br/>tenant klonlama · senkron<br/>etkileşim görüntüleyici"]
        SA2["AYRI JWT secret çifti<br/>+ sa claim + ZORUNLU 2FA"]
        SA --- SA2
    end

    subgraph CP["📚 CONTROL-PLANE — control_plane/ · KÜTÜPHANE (ikisi de kullanır)"]
        M["SQLModel entity'ler<br/>TenantConfig · MetrikSahipligi<br/>MeasureCandidate · AskJob · AuditLog"]
        AZ["authorize() matrisi"]
        KR["kripto · Alembic"]
    end

    API --> CP
    SA --> CP

    subgraph ENGINE["⚙️ MOTOR — in-process, subprocess YOK"]
        WE["WrenEngine<br/>← target/mdl.json (base64)"]
        GS["guard_sql — yalnız SELECT/WITH<br/>+ dialect transpile"]
        WE --> GS
    end

    API --> ENGINE
    GS -->|read-only| DB[("Müşteri DB<br/>duckdb · mssql · postgres")]

    style PUBLIC fill:#0d3b66,color:#fff
    style ADMIN fill:#7d1128,color:#fff
    style CP fill:#2a4d14,color:#fff
    style ENGINE fill:#4a3f00,color:#fff
```

> ⚠ Ortak auth kodu **yalnız** `control_plane/`'de yaşar (ADR-0015 K1). Admin düzlemi **ayrı
> secret**la imzalar; ağ izolasyonu deploy katmanındadır.

**Veri akışı — tek yön:**

```
                 Müşteri DB (duckdb | mssql | postgres | …)
                        ▲   read-only · guard_sql (SELECT/WITH) · dialect transpile
                        │
                 WrenEngine (in-process)  ← target/mdl.json (base64)
                        ▲
                 compose()  ⟵ packs/kaynak ⊕ packs/modul ⊕ packs/sektor
                                ⊕ kesişim ⊕ packs/cekirdek ⊕ companies/<slug>
                        ▲
                 materialize()  ⟵ control-plane DB (TenantConfig)
                                    [DB → dosya, TEK YÖNLÜ]
```

---

# 2. Yedi katman — v1 sonundaki hâli

**Bu yeni bir mimari DEĞİL** — var olanın adlandırılmasıdır. Kusurların hepsi **katman
karışmasından** doğuyor; ayrıştırma bunun içindir.

```mermaid
flowchart TB
    L6["<b>6 · ARTEFAKT</b><br/>rapor · pano · zamanlama · karar kaydı<br/><i>kapı: onay akışı + audit</i>"]
    L5["<b>5 · ANLAMA</b> (LLM)<br/>niyet · ayrıştırma · konuşma<br/><i>kapı: 4 planlayıcı kapısı + iddia kapısı</i>"]
    L4["<b>4 · DİYALOG</b><br/>slot · devam · onarım · temellendirme<br/><i>kapı: deterministik testler</i>"]
    L3["<b>3 · YÜRÜTME</b> ✅ kurulu<br/>derle → dry_plan → koş → makbuz<br/><i>kapı: Query Contract + fan-out sertifikası</i>"]
    L2["<b>2 · DİL</b><br/>CubeQuery = CEBİR (form değil)<br/><i>kapı: parse_cube_query BEYAZ LİSTE</i>"]
    L1["<b>1 · ANLAM</b><br/>katalog · metrik hakemi · iş bağlamı<br/><i>kapı: compose() FAIL-CLOSED</i>"]
    L0["<b>0 · GÜVENCE</b><br/>motor-RLS · yetki · audit · CLS · PII<br/><i>kapı: authorize() + RLS</i>"]

    L6 --> L5 --> L4 --> L3 --> L2 --> L1 --> L0

    style L6 fill:#4a148c,color:#fff
    style L5 fill:#6a1b9a,color:#fff
    style L4 fill:#1a237e,color:#fff
    style L3 fill:#1b5e20,color:#fff
    style L2 fill:#004d40,color:#fff
    style L1 fill:#3e2723,color:#fff
    style L0 fill:#b71c1c,color:#fff
```

**Temel kural (`KAT-1`):** *her katman TEK iş yapar, TEK kapısı olur, altındakine yalnız
o kapıdan dokunur.*

### Katman × madde × durum

⟳ **Restoran sütunu eklendi; sağdaki durum sütunu ara faz sonrası yeniden ölçüldü.**

| # | Katman | 🍽 Restoranda | v1'deki maddeler | ⟳ Durum @`761928d` |
|---|---|---|---|---|
| **6** | ARTEFAKT | **paket servis** — kutulanıp gönderilen | `6.1` onay akışı · `6.2` yazma araçları · `AJ6` bileşik rapor | ◐ `onay_akisi.py` · `yazma_araclari.py` **indi**, FAZ 6 açık |
| **5** | ANLAMA | 🗣 **GARSONUN KULAĞI** | `AJ1` iddia kapısı · `AJ3` tur yöneticisi · `AJ5` planlayıcı | ✅ `iddia.py` **indi** *(G4)* · `AJ3`/`AJ5` 🔵 |
| **4** | DİYALOG | 🗣 **GARSONUN DEFTERİ** | `AJ0b` diyalog yöneticisi | ✅ **`diyalog.py` indi** *(G2 · 🚩 prod)* — *atlanmış katman kapandı* |
| **3** | YÜRÜTME | 🍳 **OCAK** | — | ✅ **kurulu** |
| **2** | DİL | 📋 **SİPARİŞ FİŞİNİN DİLİ** | `AJ2` referans cebiri | ✅ **`kiyas_cebiri.py` indi** *(G6 · 🚩 `referans_dili` beta)* |
| **1** | ANLAM | 🍳 **REÇETE DEFTERİ + KİLER** | `0.18` metrik hakemi · `2.1` çekirdek katman · `2.2b` yüzey | ✅ **indi** *(bayrak `off`)* |
| **0** | GÜVENCE | 🧼 **HİJYEN + KASA** | `1.1` RLS · `1.2` CLS · `1.3` yetki · `1.8` audit · `1.12` AI Act | ✅ **indi** *(CLS kilitli — §13)* |

> ⟳ **Ve ara faz yedi katmana YENİ BİR KATMAN EKLEMEDİ** — bir **SINIR** ekledi:
> 🔴 **hava boşluğu**, katman 1 ile katman 5 arasında durur *(`yayilim.py`)*. Yedi katman
> *"kim ne yapar"*ı söylüyordu; hava boşluğu *"kim ne **GÖRÜR**"*ü söylüyor. **İkinci eksen**
> *(§0.4)* bu belgede daha önce **hiç yoktu.**

### v1'de GERÇEKTEN yeni olan yalnız dört şey

```
┌──────────────────────────────────────────────────────────────────┐
│  1 · app/iddia.py        → "olmayan yetenek vaadi" kapısı  [YOK] │
│  2 · diyalog katmanı     → slot · onarım · temellendirme   [YOK] │
│  3 · referans cebiri     → compare'in bileşimsel hâli      [YOK] │
│  4 · R11 red kodu        → "ifade edemiyorum" ≠ "anlamadım"[YOK] │
└──────────────────────────────────────────────────────────────────┘
  Geri kalan her şey ya KURULU ya YAZILIP KAPALI.
```

> ⟳ **2026-08-08 — YUKARIDAKİ KUTU BAYAT. Ölçülen:**
>
> ```
> ┌──────────────────────────────────────────────────────────────────────────┐
> │  1 · app/iddia.py        221 satır                       [İNDİ · G4]     │
> │  2 · diyalog katmanı     app/diyalog.py 177 + temellendirme.py 157       │
> │                                                          [İNDİ · G2/G1]  │
> │  3 · referans cebiri     app/kiyas_cebiri.py 265         [İNDİ · G6]     │
> │  4 · R11 red kodu        DENENDİ → GERİ ALINDI            [⊘ kayıtlı]    │
> │      gerekçe: gerçek red kodu (R9·R1) zaten vardı, R11 onu ÖRTÜYORDU     │
> │                                        (cube_router.py:3530-3538)        │
> │  ⟳ 5 · BEŞİNCİSİ — plan yazılırken YOKTU:                                │
> │      hava boşluğu  app/yayilim.py 198 + guard_alarmi.py  [İNDİ · G0b]    │
> └──────────────────────────────────────────────────────────────────────────┘
> ```
> **Kanıt:** `wc -l app/*.py` @`761928d` · `grep -n R11 app/cube_router.py`

### Dört mimari kural — `KAT-1…KAT-5`

| Kural | İçerik | Neyi engeller |
|---|---|---|
| **`KAT-1`** | Bir mekanizma **iki iş yapmaz**. Yapıyorsa ikiye ayrılır, her birinin **kendi kapısı** olur | `compare` = eksen + kapalı küme → 7 dosyada kod |
| **`KAT-2`** | **Cevapsız bir dal, cevaplı bir yolu KESEMEZ.** `source=None` dönen dal `return` etmez — kendini **aday** kaydeder | yazım-benzerliği chip'i Discovery'yi kesiyordu |
| **`KAT-3`** | Bir katman, **kendisini besleyen katmandan önce** inşa edilmez | metrik kaydı 2.2'deydi → 0.18'e çekildi (3 ihlal bulundu) |
| **`KAT-4`** | **Kazanç ve gerileme FARKLI ALETLERLE** ölçülür | `--ab` ↔ `--ab-kurtarma` ayrımı |
| **`KAT-5`** | 🔴 **SAYMA — KAPAT.** Kullanıcıya dönük anlam ekseni **literal kümeyle** tanımlanamaz | *"Bir case veriyorum, bin açık çıkıyor"*ın mekanik sebebi |

> 🔴 **`KAT-5` neden kök teşhis:** bulunan **her** kusur, sayılarak tanımlanmış bir küme.
> `("yoy","mom")` · `FACT_ICON` sözlüğü · `TUR_*` 5 tür · `R1…R10` · SSE `adim|tamam|hata`
> · `AskJob.status` 4 değer · `_META_HINTS` alt-dize listesi.
> **Vaka sayısı sonsuz; kapı sayısı sonlu.**

---

# 3. Derleme zinciri — bir katalog nasıl doğar

```mermaid
flowchart LR
    A["packs/kaynak/&lt;erp&gt;<br/><i>mikro · logo · netsis</i><br/>fiziksel şema"]
    B["packs/modul/&lt;dikey&gt;<br/><i>dikey modüller</i>"]
    C["packs/sektor/&lt;sektor&gt;<br/><i>boyahane · tekstil…</i>"]
    D["packs/kaynak/&lt;erp&gt;/sektor/&lt;s&gt;<br/><b>KESİŞİM</b>"]
    E["packs/cekirdek<br/><b>FAZ 2.1</b> — evrensel metrik<br/>sözlüğü + GRAIN sözleşmesi"]
    F["companies/&lt;slug&gt;<br/><b>EN SPESİFİK KAZANIR</b>"]
    G[("demo/wren-projects/&lt;slug&gt;<br/><i>türetilmiş · gitignore'lu<br/>ELLE DÜZENLENMEZ</i>")]

    A --> B --> C --> D --> E --> F --> G

    style E fill:#4a3f00,color:#fff
    style F fill:#1b5e20,color:#fff
    style G fill:#37474f,color:#fff
```

### `compose()` sadece kopyalamaz — **DÖRT üreteç** semantik YAML sentezler

| Üreteç | Ne üretir |
|---|---|
| `_merge_cube_synonyms` | mevcut cube metadata'sını **yeniden yazar** |
| `_compose_derived_metrics` | **yeni view + cube** üretir |
| `_compose_relationship_dimensions` | ilişkiden boyut türetir |
| `_compose_kpis` | çapraz-cube KPI'ları yükler |
| **`_merge_cube_metadata`** *(FAZ 2.1 — 5.)* | **anahtar düzeyinde** birleştirir |

> 🔴 **FAZ 2.1'in çözdüğü kusur:** `compose()` katmanları `shutil.copy2` ile **dosya
> düzeyinde** eziyordu — yani bir çekirdek katman yazılsa ERP katmanı onu **sessizce
> silerdi**. Beşinci üreteç birleştirmeyi anahtar düzeyine taşıdı.
> ⚠ **Yalnız `synonyms` + `unit` birleşir — `additive` ve `expression` BİRLEŞMEZ.**

### Grain sözleşmesi kapısı — fail-closed

```mermaid
flowchart TD
    S["Çekirdek: <code>satis_tutari · grain: fatura</code>"] --> Q{"ERP cube'u<br/>hangi grain'e<br/>bağlıyor?"}
    Q -->|"fatura"| OK["✅ birleşir"]
    Q -->|"stok_hareketleri"| RED["🔴 <b>compose() REDDEDER</b><br/>GrainIhlali"]
    RED --> AYIR["İki grain de meşruysa<br/><b>İKİ AYRI METRİK</b> yazılır —<br/>tek metrik iki anlama BÜKÜLMEZ"]

    style RED fill:#b71c1c,color:#fff
    style OK fill:#1b5e20,color:#fff
```

**Ölçülen yangın:** `ticaret` üç ERP'de aynı ad, aynı sinonim, aynı ölçü adı
(`satis_tutari`) — ama mikro'da `stok_hareketleri`, logo/netsis'te `faturalar` grain'inde.
**Üç şirkette karşılaştırılamaz üç sayı, hiçbir yerde beyan yok.**

---

# 4. 🔴 Bir prompt girildiğinde — TAM AKIŞ, tüm dallar

Bu, `app/routers/ask.py::ask()`'in **tam dallanmasıdır**. Sıra **bağlayıcıdır**; yeni
basamak eklemek `MIMARI.md`'nin güncellenmesini gerektirir.

> ⟳ **2026-08-08 · BU BÖLÜM ARA FAZ ÖNCESİNİN DALLANMASIDIR ve dört parçayı GÖSTERMEZ.**
> Aşağıdaki şemalar hâlâ doğrudur *(hiçbir dal silinmedi)* ama **eksiktir**. Restorandaki tam
> yolculuk için **§0.2**'ye bakın. Eksik olanlar:
>
> | Eksik | Nerede durur | Modül |
> |---|---|---|
> | 🗣 **Diyalog belleği** *(onarım · açık slot · devam)* | merdivenden **ÖNCE**, `context.coz()`'ün yanında | `diyalog.py` 🚩 **prod** |
> | 🗣 **Temellendirme** *("anladığım şu: …")* | `seal()`'dan **önce**, **0 token** | `temellendirme.py` |
> | 🔴 **Hava boşluğu** | mutfak ile LLM arasında — **her** LLM çağrısında | `yayilim.py` · `llm_guard.safe_call` |
> | 🔒 **İddia kapısı** | çıkış kapılarının **ikincisi** | `iddia.py` |
> | 🗣 **Menü** *(kapasite beyanı)* | **8. basamağın içinde** — dürüst ret artık **sessiz değil** | `yetenek.py` |
>
> ⚠ *Bir dallanma şeması, eklenen katmanları göstermezse **kod doğru çalışırken belge yanlış
> öğretir** — bu deponun `[DOĞRULANMADI]` yazması gereken sınıf.*

## 4.1 · Üst düzey akış

```mermaid
flowchart TD
    START(["👤 Kullanıcı prompt yazdı<br/><code>POST /ask</code>"]) --> AUTH{"JWT + authorize()<br/><code>query:run</code>"}
    AUTH -->|"❌"| E401["<b>401/403</b><br/>audit'e satır"]
    AUTH -->|"✅"| NORM["<code>cube_router._norm(q)</code><br/>Türkçe normalizasyon"]

    NORM --> CTX["<b>BAĞLAM ÇÖZÜMÜ</b><br/><code>app/context.py::coz()</code><br/><i>saf fonksiyon — HER ZAMAN bir KURAL döner</i>"]

    CTX --> KURAL{"Hangi kural?"}
    KURAL -->|"KURAL_CAPA"| CAPA["Çapa uygulanır<br/><code>reply_to_cube_query</code><br/>🚩 <b>capa_zinciri</b>"]
    KURAL -->|"KURAL_COKLU"| COK["Çok kart → KESİŞİM"]
    KURAL -->|"KURAL_CELISKI"| CEL["🔴 <b>ÇAPA UYGULANMAZ</b><br/>farklı cube'lar → <b>SOR</b><br/><i>ADR-0008: belirsizlikte tahmin etme</i>"]
    KURAL -->|"KURAL_ATIF"| ATIF["<i>'az önce dediğin'</i><br/>önceki turun metni<br/><code>route()</code> ile YENİDEN çözülür"]
    KURAL -->|"KURAL_YAPISAL"| YAP["<code>body.cube_query</code> taşınır"]
    KURAL -->|"—"| FRESH["FRESH (bağımsız soru)"]

    CAPA --> MERD
    COK --> MERD
    ATIF --> MERD
    YAP --> MERD
    CEL --> MERD
    FRESH --> MERD

    MERD["<b>▼ CEVAPLAMA MERDİVENİ ▼</b><br/>§4.2"]

    style E401 fill:#b71c1c,color:#fff
    style CEL fill:#7d1128,color:#fff
    style MERD fill:#0d3b66,color:#fff
```

## 4.2 · Merdiven — 8 basamak, tüm çıkışlar

```mermaid
flowchart TD
    IN(["normalize edilmiş soru + bağlam"]) --> B0{"<b>0 · SOSYAL SINIF</b><br/>veri niyeti VAR mı?<br/>🚩 <code>sosyal_sinif=prod</code>"}
    B0 -->|"YOK — 'teşekkürler'"| S0["✅ <b>0 LLM · 0 SQL</b><br/>Discovery'ye HİÇ gitmez<br/><code>source=meta</code>"]
    B0 -->|"VAR"| B1

    B1{"<b>1 · META / KATALOG</b><br/>gelir tablosu · bilanço<br/>'neler yapabilirsin'"}
    B1 -->|"eşleşti"| S1["✅ <code>source = meta · catalog · statement</code><br/><b>LLM YOK</b> · sabit içerik"]
    B1 -->|"hayır"| B2

    B2{"<b>2 · VQR REPLAY</b><br/>öğrenilmiş soru<br/>birebir/yakın eşleşme"}
    B2 -->|"eşleşti + ölçü tutarlı"| S2["✅ <code>source=vqr</code><br/><b>LLM YOK</b> (yalnız embedder)<br/><i>öğrenildiği andaki yapı</i>"]
    B2 -->|"hayır"| B3

    B3{"<b>TAKİP Mİ?</b><br/>cube_query ∨ prev_sql"}
    B3 -->|"YAPISAL takip"| T3
    B3 -->|"HAM takip (yalnız prev_sql)"| T3B
    B3 -->|"FRESH"| B4

    T3["<b>3 · deterministic_refine()</b><br/>ölçü değişimi/çıkarma · kırılım<br/>dönem · sıralama · top-N"]
    T3 -->|"çözdü"| S3["✅ <code>source=cube</code> · <b>LLM YOK</b>"]
    T3 -->|"çözemedi"| T4

    T4["<b>4 · cross_cube_add</b> (blend)<br/><b>cross_cube_dim_switch</b><br/><i>grain-FARKINDA — borç #11</i>"]
    T4 -->|"çözdü"| S4["✅ <code>source=cube</code><br/><i>blend — gerçek JOIN DEĞİL</i>"]
    T4 -->|"çözemedi"| T5

    T5["<b>5 · llm.refine_cube()</b><br/>LLM yapısal düzenleme<br/><b>hâlâ SQL DEĞİL</b>"]
    T5 -->|"çözdü"| S5["✅ <code>source=cube+llm</code>"]
    T5 -->|"çözemedi"| B4

    T3B["<b>3b · RAW TAKİP</b><br/>_try_fresh_intent() BİR KEZ denenir<br/><i>'raw_followup tuzağı' düzeltmesi</i>"]
    T3B --> B4

    B4["<b>▼ FRESH / INTENT-FIRST ▼</b>"] --> R["<b>4a · cube_router.route()</b><br/>🔴 <b>SIFIR-LLM</b> deterministik NL→CubeQuery"]

    R -->|"eşleşti"| S6["✅ <code>source=cube</code> · <b>confidence 1.0</b><br/>tam yapısal · chip · kırılım · drill · makbuz"]
    R -->|"boş → red kodu"| RC{"<code>red_gerekcesi()</code><br/>R1…R10"}

    RC -->|"compare niyeti"| YOY["<b>4b · strip_compare + route + yoy.compute</b><br/>deterministik period-shift · <b>LLM YOK</b>"]
    YOY -->|"çözdü"| S6

    RC -->|"R7/R8 belirsizlik"| CHIP["<b>4d · NETLEŞTİRME CHIP'İ</b><br/>measure_cube_candidates<br/>partial_unknowns"]
    CHIP --> SCHIP["✅ <b>CEVAP DEĞİL — SORU</b><br/>bir tık sonrası DETERMİNİSTİK"]

    RC -->|"diğer"| PE{"🚩 <b>prompt_enhancer</b><br/><i>off</i>"}
    PE -->|"on"| PE2["LLM soruyu katalog<br/>terimleriyle YENİDEN YAZAR<br/>→ route() TEKRAR"]
    PE2 -->|"çözdü"| S6
    PE -->|"off / çözemedi"| INT

    INT{"🚩 <b>ask_intent_first</b><br/><i>beta</i>"}
    INT -->|"on"| I["<b>4c · Intent-JSON</b><br/>LLM <b>YAPI DOLDURUR</b>, SQL YAZMAZ<br/>🚩 <code>llm_sema_kisitli</code> → native tool-use enum"]
    I --> PARSE{"<code>parse_cube_query()</code><br/><b>KATI BEYAZ LİSTE</b>"}
    PARSE -->|"geçti"| S7["✅ <code>source=cube+llm</code><br/><b>confidence 0.85</b><br/>tam yapısal · chip · drill · makbuz"]
    PARSE -->|"uydurulmuş alan"| REDP["🔴 <b>TÜM SORGU None</b><br/><i>LLM uydurduğunda cevap ÜRETİLMEZ</i>"]
    REDP --> ORK
    INT -->|"off"| ORK

    ORK{"⟳ <b>6 · GARSON = ORKESTRATÖR</b> — 🚩 <code>orkestrator_plan</code> <i>beta</i><br/>🔴 <b>BASAMAK DEĞİL, ÇIKTI BİÇİMİ</b>: karar yüzeyi (route↔garson)<br/>bayt bayt AYNI — tek adımlı plan bugünkü CubeQuery'dir"}
    ORK -->|"off ∨ şema-geçerli plan yok"| D
    ORK -->|"plan çıktı"| PLAN["<b>PLAN KOŞUMU</b> — <code>plan_kosucu</code><br/>15 kapalı fiil · azami 12 adım · <code>$1</code> referansı<br/>🔴 her <code>SORGU</code> adımı <b>parse_cube_query</b>'den geçer"]
    PLAN -->|"tüm adımlar koştu"| SORK["✅ <code>source=cube+llm</code><br/>cevap + <b>adım adım makbuz</b>"]
    PLAN -->|"bir adım koşamadı"| SORKX["◐ <b>ADIM ADIM RET</b><br/><i>hangi adımda NE eksikti</i><br/>— bugünkü tek satırlık rettin YERİNE"]

    D{"<b>_yol_izinli('discovery')</b><br/>🚩 <b>yol sınırı</b> — kullanıcı seçimi"}
    D -->|"yasak"| S8
    D -->|"izinli"| DISC["<b>5 · DISCOVERY</b><br/>VQR few-shot + business_rules + golden_sql<br/>LLM <b>HAM WREN SQL</b> yazar"]

    DISC --> GUARD["<b>guard_sql</b> — yalnız SELECT/WITH<br/><b>Katman B</b> allowlist<br/><b>always_filter</b> · RLS · CLS"]
    GUARD --> DRY{"<code>dry_plan</code><br/>doğrulama"}
    DRY -->|"hata"| HEAL["<b>self-healing</b><br/>repair → tekrar dene"]
    HEAL --> DRY
    DRY -->|"geçti"| RUN["çalıştır"]
    RUN --> S9["⚠️ <code>source = llm:&lt;sağlayıcı&gt;</code><br/><b>confidence None</b><br/>🔴 <b>tek atımlık DÜZ TABLO</b><br/>chip YOK · kırılım YOK · drill YOK"]
    S9 --> ADHOC{"🚩 <b>adhoc_cube</b><br/><i>beta</i>"}
    ADHOC -->|"on"| AC["oturum-scoped ad-hoc cube<br/>→ chip/kırılım/drill AÇILIR<br/>🔴 <b>YAPI ≠ GÜVEN</b>: source llm:* KALIR"]

    DISC -.->|"tüm sağlayıcılar tükendi<br/>429/503"| S8

    S8["<b>8 · DÜRÜST RET</b><br/><code>source=null</code><br/><i>'anlamadığını bil' — yanlış öneri,<br/>önerisizlikten KÖTÜDÜR</i>"]

    S0 --> SEAL
    S1 --> SEAL
    S2 --> SEAL
    S3 --> SEAL
    S4 --> SEAL
    S5 --> SEAL
    S6 --> SEAL
    S7 --> SEAL
    SCHIP --> SEAL
    SORK --> SEAL
    SORKX --> SEAL
    S9 --> SEAL
    AC --> SEAL
    S8 --> SEAL

    SEAL["<b>🔒 TEK ÇIKIŞ: app/answer.py::seal()</b>"]

    style S6 fill:#1b5e20,color:#fff
    style S7 fill:#33691e,color:#fff
    style SORK fill:#33691e,color:#fff
    style SORKX fill:#455a64,color:#fff
    style S9 fill:#e65100,color:#fff
    style S8 fill:#37474f,color:#fff
    style REDP fill:#b71c1c,color:#fff
    style SEAL fill:#4a148c,color:#fff
    style R fill:#0d3b66,color:#fff
```

> 🔴 **⟳ `4e` neden 5'ten ÖNCE, 4c'den SONRA — `E3`.** Orkestratör merdivenin **yerine**
> geçmez, **boşluğunu** doldurur. İlk tasarım onu `select_cube`'un *yerine* koymuştu ve
> A/B **çürüttü**: `_select_consistent` `k` örneği **aynı** süreçten çekip oylar; plan
> araya girince örneklerin bir kısmı plandan, bir kısmı yedekten geliyordu — arıza oranı
> **%55 → %65**. *Bir oylamanın geçerliliği örneklerin özdeşliğine dayanır.* Bugünkü yerinde
> cevaplanan hiçbir soru **bir çağrı bile** görmez; oylama planı **hiç görmez**.

## 4.3 · Çıkış kapısı — `seal()` neden TEK

```mermaid
flowchart LR
    IN(["herhangi bir basamaktan cevap"]) --> SEAL

    subgraph SEAL["🔒 app/answer.py::seal() — TEK ÇIKIŞ NOKTASI"]
        direction TB
        A1["yorum (<code>interpret</code>)<br/>🚩 cikti_yorumlama"]
        A2["next_steps chip'leri<br/>🚩 next_steps"]
        A3["öneriler · <code>explain</code> makbuzu"]
        A4["<b>PII maskesi</b> + görüldüyse AYRI audit"]
        A5["<b>Query Contract</b> kaydı"]
        A6["sohbet kaydı + <code>interaction_log</code>"]
        A7["<b>FAIL-CLOSED AUDIT</b>"]
        A8["<code>viz.recommend</code> grafik önerisi"]
        A9["<b>hedef bloğu</b> (FAZ 2.5)<br/><i>beyan yoksa çizgi 'Ort.' KALIR</i>"]
        A10["tazelik kademesi<br/>🚩 tazelik <i>(off)</i>"]
        A11["🚩 <b>t2_anlatici</b> <i>(off)</i><br/>→ <b>narration_guard</b> ZORUNLU<br/>eşleşmeyen sayı YAYIMLANMAZ"]
    end

    SEAL --> OUT(["AskResponse"])

    style SEAL fill:#4a148c,color:#fff
```

> **Neden modül düzeyinde:** eskiden `ask()` içinde bir **closure**'dı. Bu, **beş ihlalin
> ortak kök nedeniydi** — `/cube` paralel bir zincir yazmıştı, contract kaydını
> `except: pass` ile yutuyordu, `_try_kpi()` zinciri tamamen atlıyordu, üç ayrı contract
> kaydedici vardı, hiçbiri izole test edilemiyordu.
> **Kilit:** `tests/test_kapanis_zinciri.py`

## 4.4 · LLM sağlayıcı zinciri

```mermaid
flowchart LR
    A["anthropic"] -->|"429/503"| B["gemini"]
    B -->|"429/503"| C["groq"]
    C -->|"429/503"| D["xai"]
    D -->|"429/503"| E["ollama"]
    E -->|"tükendi"| F["🔴 <b>RuntimeError</b><br/>→ ask.py <b>DÜRÜST RET</b>e çevirir"]

    R["<code>rule</code>"] -.->|"❌ ZİNCİRDE DEĞİL"| F
    R --- N["yalnız demo/CI<br/><i>demo şemasına özel sabit kodlu kolon adları<br/>başka tenant'ta makul-ama-YANLIŞ SQL üretir</i>"]

    style F fill:#b71c1c,color:#fff
    style R fill:#37474f,color:#fff
```

**Değişmez:** `_llm_source()` `rule`'u **asla deterministik gibi etiketlemez**.
Intent-JSON için ayrı ve **daha ucuz** bir model kullanılabilir (`*_select_model`).

## 4.5 · Aynı prompt, farklı ihtimaller — somut tablo

| Prompt | Beklenen dal | `source` | LLM | Chip/drill |
|---|---|---|---|---|
| `teşekkürler` | 0 · sosyal sınıf | `meta` | ❌ | — |
| `neler yapabilirsin` | 1 · katalog | `catalog` | ❌ | — |
| `gelir tablosu` | 1 · statement | `statement` | ❌ | — |
| `bu yıl satış tutarı` | 3 · route() | `cube` | ❌ | ✅ |
| `bu yıl satış tutarı cari bazında` | 3 · route() | `cube` | ❌ | ✅ |
| `geçen yıla göre ciro` | 4b · yoy | `cube` | ❌ | ✅ |
| *(kart üstünde)* `makine bazında ayır` | 3 · deterministic_refine | `cube` | ❌ | ✅ |
| *(kart üstünde)* `bir de fire ekle` | 4 · cross_cube_add | `cube` | ❌ | ✅ |
| `bu yıl bakiye` | 4d · **belirsizlik** *(cari ∣ mizan)* | chip | ❌ | soru |
| `hasılatımız` | 4c · Intent-JSON | `cube+llm` | ✅ | ✅ |
| `depo bazında satış` *(depo yok)* | 4d · **kısmi anlama** | chip | ❌ | soru |
| `acik borc` *(typo)* | ⚠ **yazım-benzerliği** — `AJ0` | `NOTE` | ❌ | 🔴 **merdiveni KESİYOR** |
| ⟳ `en kötü makine hangisi, neden akranlarından düşük` | **4e · orkestratör** 🚩 `off` → bugün **5** ∨ **8** | `cube+llm` *(bayrak açıkken)* | ✅ | ✅ + **adım makbuzu** |
| kapsam dışı serbest soru | 5 · Discovery | `llm:gemini` | ✅ | ❌ *(adhoc_cube hariç)* |
| hiçbiri | 8 · dürüst ret | `null` | — | — |

> 🔴 **`AJ0` — MIMARI §5'in 18. yasağı, HENÜZ İNMEDİ.** Yazım-benzerliği chip'i bugün
> **iki iş** yapıyor: *öneri üretmek* **ve** *merdiveni bitirme yetkisi*. Korpusta bu
> ölçüldü: `acik borc` → *"«cari borc» mi demek istedin?"* → Discovery'ye **hiç gidilmiyor**.
> Bu, `KAT-2`'nin doğrudan ihlali.
>
> ⟳ **2026-08-08 — KAPANDI (`G3`).** Yazım-benzerliği artık **aday kaydeder, merdiveni
> KESMEZ** *(`KAT-2`'nin kendi cümlesi)*. Kısa devre sayısı bir **meta-kapıyla** korunuyor:
> `assert len(kisa) <= 11` **tavan** ∧ `assert len(kisa) == 11` **cırcır** — yani sayı
> düşerse test *"bu bir KAZANÇ, tavanı bu değere çek"* diyerek kırmızı verir
> *(`tests/test_kisa_devre_yok.py:190,196`)*.
> ⚠ Bir denetim ajanı bu deseni *"cırcır ters"* diye raporladı; **bulgu reddedildi** (`DA-6`)
> — meta-kapı deseni doğrudur. *Restoranda karşılığı: garson artık **"şunu mu demek
> istediniz?"** diye sorarken **siparişi iptal etmiyor**.*

## 4.6 · ⟳ ORKESTRATÖR — *garson tek fiş yerine bir **FİŞ DİZİSİ** yazabilir*

> 🟢🟢 **⟳ YÜRÜRLÜKTE (2026-08-09 akşamı) — bayrak `beta`, canlıda koşuyor.**
>
> Aşağıdaki *"bayrak `off`"* satırları **bayattır**; neyin değiştiği burada:
>
> | | eski | **bugün** |
> |---|---|---|
> | bayrak | `off` | **`beta`** |
> | fiil | 7 (3'ü koşuyor) | **15 (15'i koşuyor)** |
> | yerleşim | merdivenin **boşluğu** | 🔴 **garsonun ÇIKTI BİÇİMİ** (yeni basamak YOK) |
> | kabul ölçütü | A/B (arıza oranı) | 🔴 **DENKLİK** — plan **0/5** · taban **1/5** |
>
> **Neden yerleşim değişti:** boşluk, mutfak iyileştikçe **küçülüyordu** (`§AA1` bir soru
> sınıfını oradan aldı) ve *"cevap var"* ≠ *"en iyi cevap verildi"*. Karar yüzeyi ise
> büyümüyor: değişen şey hangi yola gidildiği değil, **basamak 6'nın çıktısının şekli**.
> *Bir yeteneği bir basamak olarak eklemek karar yüzeyini büyütür; bir çıktı biçimi
> olarak eklemek büyütmez.*
>
> **Neden A/B değil denklik:** `EE` turunun `-10` puanı **yarım bir göçü** ölçmüştü —
> plan ve `select_cube` bir aradaydı, oy iki dağılımdan besleniyordu. Tam göç
> birlikteliği kaldırdı; simetrik ölçümde plan **daha kararlı** çıktı.
>
> **Canlı kanıt** *(`FF` turu, `belgeler/denetim/2026-08-07_CEVIRI-SOZLESMESI.md`)*:
>
> ```
> «RAM-3 neden diğerlerinden düşük»
>   6 adım → RAM-3 seçildi (0,513) · akran ort. 0,571 (10 akran) · %10,2 düşük
>
> «bu yıl fire artışını en çok hangi kırılım açıklıyor»
>   8 adım → SORGU→AYRISTIR→BOYUTSEC→SUZ→SORGU→AYRISTIR→BOYUTSEC→ANLAT
> ```
>
> ⚠ **Ve dört sınıfsal kusur canlıda bulundu, dördü de kategorisiyle kapatıldı:**
> bölümler fiile göre toplanıyordu (→ `CIKTI_TIPI`) · varlık perdesi plana geri
> konmuyordu · referans alanı referans olmayabiliyordu · modelin **tip akışını görmesinin
> hiçbir yolu yoktu** (istem artık onu da üretiyor).
>
> 🔴 **Ayrıntı `backend/MIMARI.md §2.0`'da** — orada 15 fiilin gövde tablosu, sekiz
> orkestratör değişmezi (`O1`…`O8`) ve kabul ölçütü yazılı.

> ⟳ **2026-08-09 · YENİ BÖLÜM** *(`O-0`…`O-9`)*. Kaynak plan:
> `belgeler/plan/2026-08-09_ORKESTRATOR-KATMANI-VE-OLCEKLENME.md`.
> ⟳ **Bayrak `orkestrator_plan` = `beta` *(2026-08-09 akşamı)*.** `off` idi ve o da bir
> A/B'nin sonucuydu; **açılması da öyle**: gerileme diye ölçülen −10 puanın kaynağı plan
> kalitesi değil **oylamada iki dağılımın karışmasıydı**. Tam göç karışmayı kaldırdı ve
> denklik ölçümü plan yolunu bugünkünden **daha kararlı** buldu (sapma 0/5 ↔ 1/5).
> *Bir ölçümün sonucunu, ölçüm düzeneğini düzeltmeden okumak, düzeneği ölçmektir.*

**Restoranda:** garson *"önce hangi makine en kötü, sonra onu akranlarıyla kıyasla"*
diyen bir siparişi **tek fişe** yazamaz. Orkestratör, garsona **fiş dizisi** yazdırır;
her fiş yine **aynı beyaz listeden** mutfağa girer.

### Altı modül — ve her birinin sınırı yazılı

| Modül | Ne yapar | 🔴 Ne YAPMAZ |
|---|---|---|
| `plan_semasi.py` | **Sözleşme** — kapalı fiil kümesi (`enum`) · `ZORUNLU_ALANLAR` · `$1` referansı | LLM çağırmaz, hiçbir şey koşturmaz |
| `plan_garson.py` | Planı **çevirir** — garsonun kendisi, ayrı bir kişi değil | Yalnız **boşlukta** çağrılır; oylamaya girmez |
| `plan_kosucu.py` | Adımları sırayla koşar, `$1`'i çözer, bütçe sayar | 🔴 **SQL yazmaz · aritmetik yapmaz** — sayıyı her zaman **küp** koyar |
| `plan_tuketici.py` | Planı motora bağlar, sonucu **anlatır** | Bir yerde cevap varken **hiç konuşmaz** |
| `ilkeller.py` | `bagla` *(SATIR→DEĞER)* · `hesapla` *(SATIR→SATIR)* · `matris` · `sirala` · `rapor` · `pano_taslagi` | Veriye dokunmaz, sorgu koşmaz *(saf fonksiyon)*; `PANO` bile **yazmaz** |
| ⟳ `plan_onarim.py` *(`O-15`)* | Modelin **tek anlamlı** alan kaymalarını düzeltir — istemle doğrulayıcı **arası** üçüncü seviye | 🔴 Kullanıcının cümlesini **hiç görmez** (imzası `onar(cq, spec)`); hiçbir onarım **sessiz** değil |

### ⟳ On beş fiil — liste **KAPALI** *(7 → 15, `O-5`…`O-9`)*

`SORGU` · `KIYASLA` · `AYRISTIR` · `BAGLA` · `HESAPLA` · `TREND` · `ANLAT`
*(`ANLAT` yalnız **son** adım olabilir.)*

> 🔴 **Serbest plan YASAK.** Açık bırakılırsa plan üreten LLM, SQL üreten LLM'den **daha az**
> denetlenebilir olur — hatası birkaç adım sonra, **birleşik sonuçta** görünür ve hangi
> adımdan geldiği okunamaz. Sonluluk **şema düzeyinde** kurulur: model `enum` dışına çıkamaz.
> ⚠ Ve `SORGU`'nun gövdesi `intent_semasi.cube_query_json_schema`'dır — **ikinci bir kopya
> yazılmadı** *(`KAT-1`: iki yerde tanımlanan şema, iki farklı katalogla koşar)*.
>
> ⊙ **Discovery'den farkı tek cümlede:** *Discovery'de LLM **cevabı** üretir; burada LLM
> **soruyu böler**, cevabı her parçada **küp** verir.*

### `O-3` — araç kaydı **23 → 25**, ama liste **yer değiştiriyor**

Bugünkü kaydın 10'u **REÇETEdir** (`yoy.compute` · `contribution.*` · `stats.*` · `kpi.resolve`).
Bir reçete takımı **yazıldığı kadar** soru şekli karşılar; bir **ilkel** takım
**bileşimlerinin tamamını**. İki ilkel girdi; reçeteler **silinmedi** *(uçları çalışıyor)*
ama planlayıcının seçim listesinden kademeli çıkacaklar — `§99.1`: *uzun bir liste seçimi
kötüleştirir*.

⚠ `E4` koruması: `contribution._akran_kiyasi` bu iki ilkelin **üstüne** kuruldu ve çıktısı
**bayt bayt** korundu. Yani `O-1` bir yetenek eklemesi değil, **denkliği kanıtlanan bir refactor**.

### 🔴 ÖLÇÜLDÜ — ve bayrak kapalı bırakıldı *(`EE` turu · payda 20 · `curl` ile tek tek)*

| koşum | 🍳 `cube` | 🗣 `cube+llm` | 🥡 Discovery/adhoc | 🔴 cevapsız | **arıza oranı** |
|---|---|---|---|---|---|
| **A** · bayrak kapalı | %10 | **%35** | %10 | %45 | **%55** |
| **B** · plan `select_cube`'un **YERİNE** | %10 | %25 | 🔴 %25 | %40 | 🔴 **%65** *(+10)* |
| **B2** · plan **YALNIZ boşlukta** | %10 | **%35** | %5 | %50 | **%55** *(+0,0)* |

**Okuma — iki ayrı sonuç, ikisi de yazılı:**

1. ✅ **Gerileme tamamen kapandı** *(`B` → `B2`)*: yer düzeltilince `cube+llm` %35'e döndü.
2. ⚠ **Kazanç henüz SIFIR:** canlı iki denemede de **şema-geçerli bir plan çıkmadı**.
   Sebebi tahmin değil, ölçüm:
   * `TREND` · `AYRISTIR` · `KIYASLA` · `ANLAT` fiillerinin **çalıştırıcıları bağlı değil**;
   * serbest-JSON sağlayıcı **adım sözleşmesine uymuyor** — fiili doğru yazıp parametresini
     uyduruyor (`{"fiil":"SORGU"}` · `{"fiil":"AYRISTIR","ozellik":…}`). `ZORUNLU_ALANLAR`
     bunları **düşürüyor** ve bu **doğru davranıştır**: *yarım bir planı koşmak, koşmamaktan kötüdür.*

> 🔴 **Faz iptal DEĞİL, geliştirilecek** — raporun kendi kuralı: *«oran düşmezse faz
> GELİŞTİRİLİR, iptal edilmez»*. Sıradaki iş yukarıdaki iki maddedir.
> ⚠ *Bir bayrağı «belki bir işe yarar» diye açık bırakmak, ölçmemenin kibar hâlidir.*
> Kanıt: `backend/lab/olcumler/orkestrator_ab.md`

### İkinci çıktı da bir ürün: **adım adım ret**

Plan koşamadığında bugünkü karşılık *"Bu soru için güvenilir bir sorgu üretemedim."* —
kullanıcı **neyin** eksik olduğunu öğrenemez. `plan_tuketici` bunun yerine **hangi adımda
ne eksikti** yazar. *Bir eksikliği adıyla söylemek, onu bir sonraki mutfak işine çevirir.*

---

# 5. Cevaplama merdiveni — 8 basamak (normatif)

> ⟳ **Restoran okuması §0.7'de** — her basamağın salonda karşılığı nedir, ve
> **7. basamak (Discovery) neden bir ANOMALİdir.**
> 🔴 **Ve merdivenin okunuşu ara fazda TERSİNE DÖNDÜ:** `route()` artık *"LLM'e düşmeden
> önce denenen"* değil, **ispatlı istisnadır**. `route()` yalnız **maliyet ve hız** için,
> **yalnız kendini ispat edebildiği yerde** koşar. *İspat yükü `route()`'un üzerindedir.*

| # | Basamak | `source` | LLM? | Taşıdığı garanti |
|---|---|---|---|---|
| 1 | meta · katalog · gelir tablosu/bilanço | `meta` `catalog` `statement` | ❌ | sabit içerik |
| 2 | VQR replay | `vqr` | ❌ *(yalnız embedder)* | öğrenildiği andaki yapı |
| 3 | 🔴 **`cube_router.route()`** — sıfır-LLM | **`cube`** | ❌ | **tam yapısal · chip · kırılım · drill · Query Contract** |
| 4 | `deterministic_refine()` — yapısal takip | `cube` | ❌ | aynı |
| 5 | `cross_cube_add` / `cross_cube_dim_switch` | `cube` | ❌ | aynı *(blend, gerçek JOIN değil)* |
| 6 | 🔴 **Intent-JSON** — LLM **yapı doldurur, SQL YAZMAZ** | **`cube+llm`** | ✅ *(küçük model)* | **tam yapısal · chip · kırılım · drill · Query Contract** |
| ⟳ **6** | 🚩 **GARSON = ORKESTRATÖR** *(`orkestrator_plan` = **`beta`**)* — LLM **soruyu böler**, SQL yazmaz | `cube+llm` | ✅ *(6'nın **ÇIKTI BİÇİMİ** — yeni basamak YOK)* | 6'nın garantisi **her adım için ayrı ayrı** + adım adım makbuz |
| 7 | ⚠️ **Discovery** — LLM ham SQL yazar | `llm:<sağlayıcı>` | ✅ | **tek atımlık düz tablo. Chip YOK, kırılım YOK, drill YOK** |
| 8 | dürüst red | `null` | — | *"anlamadığını bil"* |

> ⟳ **`6b` neden bir basamak DEĞİL, bir boşluk dolgusu** *(`E3` · §4.6)*: buraya yalnız
> 6 **hiçbir şey üretemediğinde** gelinir — yani bugünkü sonuç zaten 7 ya da 8. Bir basamak
> **ekleyerek** değil, iki basamak arasındaki **düşüşü** yakalayarak çalışır. Bayrak `off`;
> A/B **gerileme 0, kazanç 0** ölçtü ve faz **geliştirilecek**, iptal edilmeyecek.

### 5.1 · Basamak 3 ve 6 neden **aynı** garantiyi taşıyor

İkisi de aynı **yapısal `CubeQuery`** üretir ve aynı **deterministik derleyici** SQL'e
çevirir. LLM'in katkısı yalnız **alan seçimi**dir.

```
parse_cube_query()  =  KATI BEYAZ LİSTE
   bilinmeyen cube      ─┐
   bilinmeyen ölçü      ─┤
   bilinmeyen boyut     ─┼──►  TÜM SORGU None
   bilinmeyen zaman b.  ─┤     (LLM uydurduğunda cevap ÜRETİLMEZ)
   bilinmeyen filtre    ─┘
```

### 5.2 · Discovery neden **ölü** ve neden **istisna**

```
cube_query üretmez  →  next_steps         BOŞ
                    →  recommendations    BOŞ
                    →  calculation_explanation BOŞ
                    →  /ask/drill  DÜRÜSTÇE REDDEDER (sahte dallanma uydurmaz)
```

**Ölçülen prod maliyeti:**

| Yol | Süre | Token |
|---|---|---|
| Discovery | **12.567 ms** | **24.352 input** |
| Aynı tenant'ın **cube** yolu | **145–434 ms** | **0** |

> **Her Discovery cevabı, belgelenmiş bir kapsam boşluğudur ve bir terfi adayıdır.**
> *(Araştırma doğruluyor: durumsuz çok-turlu text-to-SQL 3. turda **sıfır doğruluğa**
> çöküyor — EnterpriseMem-Bench, 2026-05.)*

---

# 6. Red kodları — R1…R10 (ve eksik R11)

`app/cube_router.py` · `red_gerekcesi()` ile okunur.

| Kod | Anlamı | Kullanıcıya dönüşü |
|---|---|---|
| `R1` | cube eşleşmedi | Discovery ∨ dürüst ret |
| `R2` | liste/döküm niyeti *(politika: küp üretebilir ama devredildi)* | 🚩 `liste_niyeti=beta` → kırılım |
| `R3` | kıyas dili (`compare`) — cube yolu kıyası kurmuyor | `yoy.compute` dalı |
| `R4` | ölçü eşleşmedi | netleştirme ∨ Discovery |
| `R5` | ortalama istendi ama ortalama ölçü tanımlı değil | dürüst ret |
| `R6` | dışlama filtresi **kısmen** çözüldü *(yarım uygulama yapılmaz)* | dürüst ret |
| `R7` | **boyut adayı tek değil** → belirsizlik | 🔵 **netleştirme chip'i** |
| `R8` | yarı-toplanabilir ölçü + zaman kovası *(running balance = WINDOW)* | 🔵 netleştirme |
| `R9` | kırılım istendi ama boyut eşleşmedi | netleştirme |
| `R10` | **kapsam kapısı** — tanınmayan kelime (ADR-0008) | dürüst ret |
| 🔴 `R11` | **YOK — v1'de yazılacak**: *"ifade edemiyorum"* ≠ *"anlamadım"* | **eksik yetenek SAYILAMIYOR** |

> ⟳ **2026-08-08 · `R11` DENENDİ ve GERİ ALINDI** *(`G6`, kayıt: `cube_router.py:3530-3538`)*.
> **Gerekçe:** gerçek red gerekçesi zaten vardı *(`R9` · `R1` · …)* ve `R11` onu **örtüyordu**;
> geliştiriciyi **cebire** yolluyordu, oysa cebir *(`kiyas_cebiri.py`)* aynı fazda indi.
> 🔴 **Yani eksiklik bir RED KODUYLA değil, bir YETENEKLE kapandı** — ve restorandaki
> karşılığı tam olarak `G8`'dir: *"bunu ifade edemiyorum"* demek yerine garson **menüyü
> okuyor**: *"bunu yapamam — ama şunu yapabilirim."* **Sessiz red, sesli rede döndü.**

### Risk-kapsam eğrisi — kapılar üstünde, skaler `confidence` **UYDURULMADAN**

```mermaid
flowchart LR
    A["<b>route</b><br/>deterministik"] --> B["<b>tie_chip</b><br/>deterministik<br/><i>cevap değil, SORU üretir</i>"]
    B --> C["<b>intent</b><br/>llm_secim<br/><i>sayı küpten, SEÇİM olasılıksal</i>"]
    C --> D["<b>discovery</b><br/>llm_sql<br/><i>SQL'in kendisi olasılıksal</i>"]

    style A fill:#1b5e20,color:#fff
    style B fill:#33691e,color:#fff
    style C fill:#e65100,color:#fff
    style D fill:#b71c1c,color:#fff
```

> 🔴 **`hata_orani` bilerek YOK** — bir kapının hata oranını bu araç ölçemez (doğruluk
> korpusun işi). Yazsaydık **uydurma** olurdu.
> ⚠ **`consistency_k` bir güven eşiğine DÖNÜŞTÜRÜLMEZ:** *"bir model son derece
> self-consistent olup yine de **tutarlı biçimde YANLIŞ** olabilir."*
> **Araç:** `lab/risk_kapsam.py` → `lab/reports/risk_kapsam.md`

---

# 7. Bayrak envanteri — 25 bayrak, tam durum

> ⟳ **2026-08-08 · SAYI BAYAT — yeniden ölçüldü @`761928d`:**
>
> | | Bu belgenin dediği | ⟳ **Ölçülen** |
> |---|---|---|
> | `FLAG_REGISTRY` | 25 | **49** |
> | `features.yml` | 21 | **48** |
> | 🔴 **ölü bayrak** *(kayıtta var, YAML'de yok)* | **2** | **1** — yalnız `ayni_grain_gocu` |
> | Aşama dağılımı | — | `prod` **3** · `beta` **19** · `alpha` **1** · `off` **25** |
>
> **Komut:** `FLAG_REGISTRY` ↔ `yaml.safe_load(features.yml)["features"]` anahtar farkı.
> 🔴 **§C ölçüt 10 *(ölü bayrak = 0)* neredeyse kapandı:** kalan tek kayıt `ayni_grain_gocu`
> ve o **derleme-zamanı ayarıdır** — `compose()`'un `principal`'ı yok, tenant bayrağı
> **olamaz**. *§7.2'nin iki ölü bayrağı (`ask_async_discovery` · `threaded_chat`) artık
> YAML'de.*
>
> **⟳ Ara fazda doğan bayraklar** *(bu belgede hiç yoktu)*:
> `diyalog_bellegi` 🟢 **prod** · `t2_anlatici` 🔵 **alpha** · `referans_dili` 🔵 **beta** ·
> `olcu_ekleme_takibi` 🔵 **beta**.
> 🔴 **Ve bir bayrak ölü kontrole düştü:** `llm_sema_kisitli` **beta görünüyor, etkisi
> SIFIR** — seçilen sağlayıcı *(OpenRouter, OpenAI-uyumlu uç)* `oneOf` desteklemiyor ve
> intent şeması **tümüyle `oneOf` üzerine kurulu** *(`intent_semasi.py:101`)*.
> ⚠ **Kaybedilen bir GÜVENLİK garantisi değil, bir MALİYET garantisidir** — asıl emniyet
> ağı `parse_cube_query`'nin beyaz listesi ve o **sağlayıcıdan bağımsızdır**.

> ⟳ **2026-08-09 · SAYI YİNE BAYAT — yeniden ölçüldü @`7880563`:**
> `FLAG_REGISTRY` **53** · `features.yml` **52** · 🔴 **ölü bayrak yine 1** *(değişmedi —
> `ayni_grain_gocu`, derleme zamanı)* · aşama dağılımı `prod` **3** · `beta` **20** ·
> `alpha` **1** · `off` **28**.
> **⟳ Orkestratör fazının doğurduğu bayrak:** `orkestrator_plan` 🔴 **off** — *ölçüldü ve
> kapalı bırakıldı*, gerekçesi §4.6'da ve `lab/olcumler/orkestrator_ab.md`'de.

**Kapsam sırası (soldan sağa artar, en spesifik kazanır):**

```
global (demo/packs/features.yml)  <  sektör  <  şirket  <  DB-override
                                                          (global-scope < sektör < tenant < rol < kullanıcı)
```

**Aşamalar:** `off` → `alpha` → `beta` → `prod`
*`beta` = herkese kapalı DEĞİL; varsayılanda yalnız burada tanımlı, admin panelden
tenant/rol/kullanıcı override'ı ile açılır.*

## 7.1 · `features.yml`'de tanımlı 21 bayrak

| Bayrak | Durum | Faz | Ne yapar | Kapalıyken |
|---|---|---|---|---|
| `sosyal_sinif` | 🟢 **prod** | 0.13 | veri-niyeti yok → 0 LLM · 0 SQL | `teşekkürler` **uydurma SQL** üretir |
| `cikti_yorumlama` | 🔵 beta | — | her tablo/grafik/rapor/KPI için deterministik yorum | yorum yok |
| `sql_display` | 🔵 beta | — | üretilen SQL'i kullanıcıya aç | gizli |
| `verify_button` | 🔵 beta | — | ✓/✗ doğrulama → VQR öğrenmesi | öğrenme yok |
| `scheduled_reports` | 🔵 beta | — | zamanla + bildirim (ADR-0011) | uç yok |
| `dashboards` | 🔵 beta | §9 | kullanıcı panoları — canlı izleme | pano yok |
| `next_steps` | 🔵 beta | K2 | kırılım/ölçek/zaman chip'leri | chip yok |
| `ask_intent_first` | 🔵 beta | 1 | route() boşsa **Intent-JSON** doldurt | Discovery'ye düşer |
| `llm_sema_kisitli` | 🔵 beta | 3a | Intent-JSON'u **native tool-use** enum'una taşı | serbest-JSON yedeği |
| `metrik_kaydi` | 🔵 beta | **0.18** | **HAKEM** — bir terimi 2 cube sahipleniyorsa | kayıt **şemaya HİÇ yazılmaz** |
| `liste_niyeti` | 🔵 beta | 2a-5 | *"listele/dökümü"* → cube kırılımı | dejenere **tek toplam** *(sessiz-yanlış)* |
| `adhoc_cube` | 🔵 beta | 1/K1 | Discovery sonucundan **oturum-scoped cube** | Discovery'de chip/drill yok |
| 🔴 `kapsam_mercegi` | ⚫ **off** | **2.3** | departman = **mercek**, küp değil | herkes TAM katalogu görür |
| 🔴 `ossie_ithal` | ⚫ **off** | **3.4** | Apache Ossie semantik model ithali | uç **404** |
| 🔴 `agent_plan_secimi` | ⚫ **off** | **4/AJ5** | `Planlayici.sec()` planı **ÖNERİR**, 4 kapı denetler | pilot yok |
| 🔴 `prompt_enhancer` | ⚫ **off** | **3b** | route() boşsa soruyu **yeniden yaz**, route()'u tekrar dene | sıcak yolda LLM yok |
| 🔴 `capa_zinciri` | ⚫ **off** | **0.5** | karta yanıt **kimliğiyle** taşınır | `capalar` boş → bugünkü dallar |
| 🔴 `tazelik` | ⚫ **off** | **1.7** | *"bu sayı ne kadar eski?"* — 4 kademe | alanlar `None` |
| 🔴 `metrik_sertifikasi` | ⚫ **off** | **1.5** | tanımı **KİM** onayladı + o günden beri değişti mi | rozet yok *(⚠ hash çürümesi **kapalıyken de işler**)* |
| 🔴 `lineage` | ⚫ **off** | **1.6** | **KOLON** düzeyi köken | makbuz bugünküyle birebir |
| 🔴 `netlestirme_onceligi` | ⚫ **off** | **F/0.4** | ≥2 sahipli ölçüde chip Intent-JSON'u **önceler** | Intent-JSON gölgeliyor |

## 7.2 · `FLAG_REGISTRY`'de var, `features.yml`'de YOK — 4 bayrak

| Bayrak | Neden YAML'de yok | Nasıl açılır |
|---|---|---|
| `cekirdek_katman` | 🔴 **derleme-zamanı ayarı**, tenant bayrağı değil — `compose()`'un `principal`'ı yok | `app/config.py:184` · `DIMA_CEKIRDEK_KATMAN=on` + **yeniden derleme** |
| `ayni_grain_gocu` | aynı sebep — compose katmanında | `off\|shadow\|on` |
| `ask_async_discovery` | 🔴 **ÖLÜ BAYRAK** — §C/10'un ölçtüğü 2 taneden biri | kayıtta var, YAML'de yok |
| `threaded_chat` | 🔴 **ÖLÜ BAYRAK** — ikincisi | kayıtta var, YAML'de yok |

> 🔴 **§C ölçüt 10 hedefi: ölü bayrak = 0.** Bugün **2**.
> Ölçüm: `FLAG_REGISTRY` **25** ↔ `features.yml` **21**.

## 7.3 · Yol haritasında adı geçen ama **kayıtta OLMAYAN** bayraklar

| Roadmap'te yazan | `FLAG_REGISTRY` | Gerçek durum @`eb48c40` |
|---|---|---|
| `hedef_kiyasi` *(2.5)* | ⟳ ✅ **VAR** *(eskiden ❌)* | ⟳ **2026-08-08 · KAPANDI** — `app/features.py:53` **ve** `demo/packs/features.yml:100` *(`off`)*. ⚠ *Bu satır bu belgenin kendi denetiminde bulunmuştu ve **ölçüm haklı çıktı**: ayrışma gerçekti, ve kapandı. Özgün iddia kayıt için duruyor: "`app/hedef.py` indi ve `answer.py:647`'den ÇAĞRILIYOR — ama bayrak kayıtta yok."* |
| `ui_metrik_yonetimi` *(2.2b)* | ❌ yok | yüzey indi, bayrak kayıtsız |
| `coldstart_metrik` *(3.6)* | ❌ yok | `app/coldstart.py` indi, bayrak kayıtsız |
| `netlestirme_kapanisi` *(0.5b)* | ❌ yok | — |
| `motor_rls` *(1.1)* · `motor_cls` *(1.2)* | ❌ yok | env/config yoluyla |
| `onay_akisi` *(6.1)* · `yazma_araclari` *(6.2)* | ❌ yok | **FAZ 6 — yapılmadı** |
| `ossie_ihrac` *(4.4)* · `mcp_yuzeyi` *(4.5)* | ❌ yok | **FAZ 4 — sırada** |
| `tur_takip` *(5.1)* · `tur_paylas` *(5.2)* | ❌ yok | **FAZ 5** |
| `peer_kiyasi` · `kpi_pin` · `hizli_derin` · `netlestirme_duzeyi` *(FAZ 5)* | ❌ yok | **FAZ 5** |
| `kanal_slack` · `kanal_whatsapp` · `sabah_digest` *(5.9)* | ❌ yok | **FAZ 5** |
| `public_api` · `embed` *(6.5)* · `kanal_kimlik` *(6.6)* | ❌ yok | **FAZ 6** |
| `ui_settings_tam_sayfa` · `ui_kanit_gorunurlugu` · `ui_dcm_modu` *(FAZ 7)* | ❌ yok | **FAZ 7** |
| `diyalog` · `referans_dili` · `tur_yoneticisi` · `calisirken_sorma` · `oturumlar_arasi_hafiza` · `adim_zinciri` · `bilesik_rapor` *(§G)* | ❌ yok | **§G — v1'e paralel** |

## 7.4 · Bayrak profilleri (`0.20`)

| Profil | İçerik | Ölçülen |
|---|---|---|
| `taban` | **hepsi off** | **0 açık** |
| `v1-varsayilan` | v1'in önerilen hâli | **11/17** |
| `v1-tam` | hepsi açık | **19/19** |

---

# 8. 🔴 Manuel test edilecek her şey — `off` bayraklar

**Neden manuel:** aşağıdaki dokuz bayrağın hiçbirinin kazancı **korpusla ölçülemez**.
Korpus soruları **katalogdan üretiliyor** ve beklenen cevap da **katalogdan** türetiliyor —
yani sinonim zenginleşmesi, tazelik rozeti, kolon kökeni gibi şeyleri **göremez**.
*Cetveli uzatıp "bak uzamamış" demek olur.*

> 🔴 **Bu tablonun sebebi ölçülmüş bir hatadır:** `cekirdek_katman` bayrağı bir kez
> *"kazanç ölçülemedi"* diye `off` bırakıldı. Yanlış karardı — **alet o soruyu ölçemiyordu.**
> Doğru cevap *"kazanç yok"* değil, **"bu alet bu soruyu ölçemez"**di.

## 8.1 · Test protokolü — her bayrak için aynı üç kutu

```
┌─ 1 · KAZANÇ ─────────────────────────────────────────────┐
│  Açıkken NE ÇALIŞMALI? (yazılı, önceden, yanlışlanabilir)│
├─ 2 · KIRMIZI ÇİZGİ ──────────────────────────────────────┤
│  NE KESİNLİKLE DEĞİŞMEMELİ? (ihlal → bayrak ANINDA kapanır)│
├─ 3 · GİZLİ RİSK ─────────────────────────────────────────┤
│  Nereye bakmalısın ki sessiz bozulmayı yakalayasın?      │
└──────────────────────────────────────────────────────────┘
```

## 8.2 · Bayrak bayrak — ne sorulacak, ne beklenecek

### 🔴 `cekirdek_katman` *(FAZ 2.1 — derleme zamanı)*

| | |
|---|---|
| **Nasıl açılır** | `DIMA_CEKIRDEK_KATMAN=on` + **konteyner yeniden başlat** *(UI düğmesi YOK — `compose()`'un principal'ı yok)* |
| **1 · Kazanç** | `hasılat` · `hasilat` · `gelir` → satış tutarı · `kalan` · `hesap bakiyesi` → bakiye · `borç toplamı` · `toplam borç` → borç · `kaç hareket` · `işlem sayısı` → hareket sayısı. **Bugün cevapsız kalanlar açıkken CEVAPLANMALI** |
| **2 · Kırmızı çizgi** | 🔴 **HİÇBİR SAYI DEĞİŞMEMELİ.** Gölge derlemede dört şirkette **sayı-etkisi 0 fark** ölçüldü — `expression` · `base_object` · `additive`'e dokunulmuyor |
| **3 · Gizli risk** | **Genişleyen bir sinonim başka küpün eşleşmesini ÇALABİLİR.** Cevabın **sayısına değil**, **hangi küpten geldiğine** bak → rozet / `source` / `explain` |
| **Ölçülen** | gölge diff: 4 şirkette sayı-etkisi **0**, sözlük büyümesi **2/8/5/7** |

### 🔴 `kapsam_mercegi` *(FAZ 2.3)*

| | |
|---|---|
| **1 · Kazanç** | Departman kullanıcısı `/schema`'da **yalnız kendi merceğini** görür; `genel` ve `portfoy` ayrı |
| **2 · Kırmızı çizgi** | 🔴 **Mercek bir GÖRÜNÜRLÜK aracıdır, GÜVENLİK SINIRI DEĞİL.** Kapatmak **yetki AÇMAZ**. `portfoy` yalnız `is_superadmin` ile |
| **3 · Gizli risk** | Merceğin `/ask`'e sızması — **`AskRequest.scope` bilerek YOK**; mercek `/schema`'ya ait |
| ⚠ **YAML tuzağı** | `kapsam_mercegi: off` **tırnaksız yazılırsa YAML 1.1 onu BOOLEAN okur** |

### 🔴 `tazelik` *(FAZ 1.7)*

| | |
|---|---|
| **1 · Kazanç** | Her cevapta `taze \| uyarı \| hata \| bilinmiyor` kademesi |
| **2 · Kırmızı çizgi** | 🔴 **`hata` VE `bilinmiyor` kademelerinde SAYI GÖSTERİLMEZ** |
| **3 · Gizli risk** | ⚠ **Demo/DuckDB tenant'larında `SyncState` YOK** → hepsi `bilinmiyor` → **sayı gizlenir**. Açmak bir **ÜRÜN kararıdır** ve **tenant başına** ölçülmelidir |

### 🔴 `metrik_sertifikasi` *(FAZ 1.5)*

| | |
|---|---|
| **1 · Kazanç** | Rozet: metriğin tanımını **kim** onayladı |
| **2 · Kırmızı çizgi** | ⚠ **TANIM-HASH ÇÜRÜMESİ KAPALIYKEN DE İŞLER** — aksi hâlde bayrak açıldığında **bayat** sertifikalar *"geçerli"* görünürdü |
| **3 · Gizli risk** | Onaydan sonra `expression` değişmişse rozet **düşmeli**; düşmüyorsa sessiz-yanlış |

### 🔴 `lineage` *(FAZ 1.6)*

| | |
|---|---|
| **1 · Kazanç** | *"Bu sayı hangi tablonun hangi kolonundan, hangi **dönüşümle** geldi?"* |
| **2 · Kırmızı çizgi** | Kapalıyken makbuz bugünküyle **BİREBİR** |
| **3 · Gizli risk** | `answer.koken()` **İLİŞKİ** düzeyindedir (hangi kırılım hangi join'den) — bu ondan **FARKLI** bir sorudur ve **yerine geçmez**. İkisi karıştırılırsa kullanıcı sahte bir kesinlik görür |
| **Not** | Toplanan geçmiş **SİLİNMEZ** (ADR-0019) |

### 🔴 `capa_zinciri` *(FAZ 0.5)*

| | |
|---|---|
| **1 · Kazanç** | Bir **karta yanıt** verirken bağlam o kartın kimliğiyle taşınır. Çok kart → **kesişim** |
| **2 · Kırmızı çizgi** | 🔴 Farklı cube'lu kartlar seçilirse → **`KURAL_CELISKI` → SOR**. Sessizce birini seçmek yasak (ADR-0008) |
| **3 · Gizli risk** | 🔴 **Ölçülen kusur:** `coz()` doğru kuralı üretiyordu ama takip zinciri hâlâ `body.cube_query`'yi okuyordu → **çapa çözülüp yok sayılıyordu**. Kullanıcı için sonucu: işaret ettiği karta yanıt verirken cevap **başka bir raporun** bağlamına kayıyor — **sessizce**. Açtığında **buna** bak |

### 🔴 `netlestirme_onceligi` *(FAZ F / 0.4)* — **ÖLÇÜLDÜ, `off` KALIYOR**

| | |
|---|---|
| **Ölçüm (CANLI)** | A/B 63 etiketli vaka: **bozulan 0 · kurtarılan 0** · Kurtarma 15 gerçek ifade: cevaplanan **12 → 8**, kurtarılan **1** *(doğru ölçüyle **0**)*, **kaybedilen 5** · Kararlılık: **5/6 kararlı** |
| **Karar** | Kabul ölçütü *(doğru kurtarma > 0)* **karşılanmıyor** ve kayıp gerçek → **KAPALI** |
| **Kararın evi** | 🔴 **`MIMARI.md` §7** — bir YAML yorumu mimari otorite **değildir**. `test_faz0_4_netlestirme.py` iki yerin **ayrışmasını** kapıya çevirdi |
| ⚠ **Yan bulgu** | `bu yıl bakiye` kararlı şekilde `mizan.bakiye` seçiyor ve cevap **₺0** — mizan yapısı gereği sıfıra denkleşir. Bu bir **MOTOR kusuru değil KATALOG kararıdır** *(bare `bakiye` hangi cube'un?)* ve **sessizce yamalanmadı** |

### 🔴 `prompt_enhancer` *(FAZ 3b)* — **ölçüldü, kazanç YOK, kota sınırına çarpıldı**

| | |
|---|---|
| **1 · Kazanç** | route() boşken soruyu katalog terimleriyle yeniden yaz → route() tekrar |
| **2 · Kırmızı çizgi** | 🔴 **LLM YAPI SEÇMEZ, yalnız METNİ iyileştirir.** Planlayıcının **dört kapısından** geçer *(route denenmeden seçilemez)* |
| **3 · Gizli risk** | **Sıcak yola LLM çağrısı ekliyor** — gecikme + kota. Açılması **bilinçli karar** olmalı |

### 🔴 `agent_plan_secimi` *(FAZ 4 / AJ5)*

| | |
|---|---|
| **1 · Kazanç** | `Planlayici.sec()` planı **ÖNERİR**; `agent_run` makbuzu kaydedilir |
| **2 · Kırmızı çizgi** | 🔴 **SEÇİM ≠ ÇALIŞTIRMA.** Dört kapı denetler |
| **3 · Gizli risk** | Sıcak yola LLM çağrısı |

### ⟳ 🔴 `orkestrator_plan` *(FAZ `O-4`)* — **ÖLÇÜLDÜ, `off` KALIYOR**

| | |
|---|---|
| **1 · Kazanç** | Çok adımlı soru *(«en kötü makine hangisi, neden akranlarından düşük»)* bugün Discovery'ye ya da rette düşüyor; plan onu **adım adım** cevaplayabilir |
| **2 · Kırmızı çizgi** | 🔴 **`E3` — merdivenin YERİNE değil BOŞLUĞUNA.** Cevaplanan bir soruya **bir çağrı bile** eklenemez. Ve **serbest plan yasak**: fiil kümesi `enum`, her `SORGU` adımı beyaz listeden geçer |
| **3 · Gizli risk** | 🔴 **Oylamanın bozulması** — ölçüldü: plan `select_cube` ile yarışınca `_select_consistent`'ın örnekleri iki farklı süreçten gelir, arıza oranı **%55 → %65** |
| **Elle bakılacak** | Kapalıyken davranış **bayt bayt** bugünkü mi *(`sarmala()` nesnenin kendisini döndürür — testli)*; açıkken **cevaplanan** bir soru bozuluyor mu |
| **Kapalıyken** | `acik_mi()` `False` → modülün **hiçbir satırı** koşmaz |

### 🔴 `ossie_ithal` *(FAZ 3.4)*

| | |
|---|---|
| **1 · Kazanç** | Müşterinin var olan semantik modeli bir `packs/` katmanı olur; `ai_context` → `synonyms` |
| **2 · Kırmızı çizgi** | 🔴 **İthal edilen her ilişki `certified: "olculmedi"` damgasıyla gelir.** *İthal bir ilişki, sessiz "sağlıklı" DEĞİLDİR* |
| **3 · Gizli risk** | Adsız `dataset`/`metric`/`field`/`relationship` → **fail-closed REDDEDİLİR**, atlanmaz. Ve ithal **ÇEKİRDEK katmana** iner, ERP katmanına **değil** *(yoksa `cari`/`ticaret`'in dördüncü kopyası doğar)* |
| **Kapalıyken** | uç **404** döner |

## 8.3 · `beta` bayraklar — açık ama **hiç elle bakılmamış** olabilir

| Bayrak | Elle doğrulanacak |
|---|---|
| `metrik_kaydi` | Aynı terimi iki cube sahipleniyorsa **hakem** doğru mu? Tenant kararı yoksa davranış **birebir bugünkü** olmalı |
| `liste_niyeti` | *"listele/dökümü"* → gerçek boyut yoksa **dejenere tek toplam DÖNMEMELİ** |
| `adhoc_cube` | Discovery cevabında chip/drill açılıyor mu — **ve `source` hâlâ `llm:*` mi?** 🔴 **YAPI ≠ GÜVEN** |
| `llm_sema_kisitli` | Desteklenmeyen sağlayıcıda **serbest-JSON yedeğine** düşüyor mu? `cube:null` **reddetme dalı** korunuyor mu? |
| `next_steps` | Chip'ler **deterministik** mi, tıklanınca **yeni SQL üretmiyor** mu? |
| `dashboards` · `scheduled_reports` | Panel var mı, uç yetim değil mi? |

---

# 9. A/B testi yapılacak her şey

## 9.1 · 🔴 `KAT-4` — kazanç ve gerileme **FARKLI ALETLERLE** ölçülür

```mermaid
flowchart LR
    subgraph K["KAZANÇ ölçümü"]
        A1["<code>nl_accuracy --ab-kurtarma &lt;bayrak&gt;</code>"]
        A2["korpus: <b>bugün CEVAPSIZ</b> ifadeler"]
        A1 --- A2
    end
    subgraph G["GERİLEME ölçümü"]
        B1["<code>nl_accuracy --ab &lt;bayrak&gt;</code>"]
        B2["korpus: <b>etiketli 63 vaka</b>"]
        B1 --- B2
    end
    K -.->|"🔴 AYNI KORPUSTA<br/>YARIŞTIRILAMAZ"| G

    style K fill:#1b5e20,color:#fff
    style G fill:#7d1128,color:#fff
```

> **Neden:** etiketli vakalarda bir LLM bayrağı **kazanç ÜRETEMEZ**, yalnız **bozabilir**.
> Aynı korpusta yarıştırmak `50402d3`'ün *"YANLIŞ NÜFUS ölçülmüştü"* dersinin tekrarıdır.

## 9.2 · A/B kuyruğu — bayrak bayrak

| Bayrak | Kazanç aleti | Gerileme aleti | Kabul ölçütü | Durum |
|---|---|---|---|---|
| `netlestirme_onceligi` | `--ab-kurtarma` | `--ab` | doğru kurtarma **> 0** | ✅ **ölçüldü** → `off` *(kurtarma 0, kayıp 5)* |
| `prompt_enhancer` | `--ab-kurtarma` | `--ab` | kazanç > 0 | ⚠ **ölçüldü: kazanç YOK** *(kota sınırına çarpıldı)* |
| `llm_sema_kisitli` | `faz3a_sema_kazanci.py` | `--ab` | kazanç > 0 | ✅ **ölçüldü: 0 kazanç** — mekanizma **yapısal** gerekçeyle kaldı |
| ⟳ `orkestrator_plan` | `lab/discovery_orani.py --ab` | **aynı alet** *(payda kilitli)* | 🔴 **arıza oranı DÜŞMELİ**, hiçbir cevap bozulmamalı | ✅ **ölçüldü: gerileme 0, kazanç 0** → `off` *(bkz. §4.6)* |
| `cekirdek_katman` | 🔴 **korpus ÖLÇEMEZ** → **manuel tur** | `mdl_diff` gölge derleme | **sayı-etkisi 0** + daha çok soru cevaplanıyor | ⬜ **HAKEM: KULLANICI** |
| `t2_anlatici` | `narration_guard` red/yayım **oranı** | süit | **0 uydurma sayı** | ⬜ FAZ 5 |
| `agent_plan_secimi` | **§G.6 kıyas sözleşmesi** | `--ab` | §G.6b | ⬜ §G |
| `ayni_grain_gocu` | 🔴 **korpus ÖNCESİ/SONRASI ZORUNLU** | korpus | **erişim DÜŞERSE GERİ ALINIR** | ⬜ *(bkz. §9.3)* |
| `motor_rls` | — | `logs/rls_shadow.jsonl` | **gölge 7 gün · sapma 0** | ⬜ FAZ 1 |
| `ossie_ihrac` | — | **round-trip** | ihraç→ithal → **birebir aynı SQL** | ⬜ FAZ 4.4 |
| `mcp_yuzeyi` | — | `tests/test_mcp.py` | MCP = HTTP: **aynı 4 kapı, aynı makbuz** | ⬜ FAZ 4.5 |

## 9.3 · 🔴 `ayni_grain_gocu` — **bu depoda bir kez REDDEDİLMİŞ işin ta kendisi**

```
ÖLÇÜLDÜ (bir kez denendi, geri alındı):
   surdurulebilirlik kimliğinden ham kaynak adları çıkarıldı
        ↓
   erişim  %64 ──────────────► %56
   sessiz-yanlış  110 KAPANDI
   cevap          388 KAYBOLDU
        ↓
   🔴 3,5 : 1  KÖTÜ TAKAS  →  GERİ ALINDI  →  ŞİMDİ TESTLE KORUNUYOR

TEŞHİS: "kimliği kaldırmak sahipliği ÇÖZMEDİ."
```

> **Bu yüzden korpus öncesi/sonrası ölçümü zorunlu olan TEK madde budur.**
> O 388'i **hiçbir manuel tur göstermezdi.**

## 9.4 · §G kıyas sözleşmesi — **ikinci satır kod yazılmadan ÖNCE yazıldı**

| Kural | İçerik |
|---|---|
| **G.6a** | 🔴 A ve B **AYNI KORPUSTA KIYASLANAMAZ** |
| **G.6b** | Kabul ölçütü **şimdi yazılır, sonra tartışılmaz** |
| **G.6d** | 🔴 **TEST REJİMİ — ÜÇ KATMAN, üçü de ZORUNLU** |
| **G.6e** | **`VK-1…VK-6`** adı konmuş kabul vakaları — geliştirici **ATLAYAMAZ** |
| **G.6f** | `N`'in değeri · **hakem protokolü** · ***"KOŞULAMADI" hükmü*** |
| **G.6c** | **Manuel test yolu** — kullanıcının açık isteği |
| **Teslim** | 🔴 ***"B kazanmadı"* de geçerli bir sonuçtur. Kararın kendisi bir teslimdir** |

---

# 10. Test kapıları — ne ölçüyor, ne ölçemiyor

## 10.1 · Dört kapı, iki rejim

> ⟳ **2026-08-08 · BEŞİNCİ ALET İNDİ: `lab/garson.py --live`.**
> **Neden:** ölçüldü ki `konusma_senaryolari` **sekiz koşumun sekizinde de** `⊘ ÖLÇÜLEMEDİ`
> veriyordu ve `deneyim.py` kendi çıktısında *"yapısal duman — **KAPI DEĞİL**"* diyordu.
> 🔴 **Yani garsonu görebilecek iki aletin ikisi de hiç koşmamıştı; garson hakkında alınan
> HER karar yalnız mutfak metrikleriyle alınmıştı.**
>
> | Alet | Ölçtüğü | Rejim |
> |---|---|---|
> | ⟳ `lab/garson.py --live` | **§5'in sekiz satırı** — karşılar · sipariş alır · **tekrarlar** · sorar · **hatırlar** · düzeltilir · **anlatır** · **menüyü bilir** | 🔴 `--live` **zorunlu**; `--live`'sız **yeşil vermez, `⊘` verir** |
> | ⟳ kaset modu | sağlayıcısız tekrar oynatma *(`lab/kasetler/*.json`)* | belirlenimli |
>
> **Kör alet kapısı:** `t2_anlatici` açık/kapalı arasında §5/7 satırı **farklı çıkmalı**;
> çıkmıyorsa **alet kördür** ve düzeltilene kadar hiçbir faz inmez. ⚠ Bu kapı **gerçekten
> ateşledi**: `2·anlat` satırı `narration or summary` okuduğu için ayırt edici değildi
> *(`G0.12`)*.
> 🔴 **`KURAL G-1`:** belirlenimsiz bir kapı **tek koşumla karar vermez** — iki koşum
> ayrışırsa karar **verilmez**, `⊘` + borç kaydı yazılır.
>
> ⚠ **Ve yerel kapı politikası DEĞİŞMEDİ:** `--garson` yeni bir **seviye değil**, yeni bir
> **hedeftir** *(yalnız açık talep)*. `--tam` süresi **değişmedi**.

```mermaid
flowchart TB
    subgraph LOCAL["🖥️ YEREL — geliştirme"]
        H["<code>--hizli --degisen &lt;dosya&gt;</code><br/><b>SİNYAL, KAPI DEĞİL</b><br/>~30 sn – 2 dk"]
        T["<code>--tam</code> → <b>YALNIZ KORPUS</b><br/><b>1 dk 50 sn</b><br/><i>demet sonunda, BİR KEZ</i>"]
    end
    subgraph CI["🌙 GECELİK CI — nightly.yml"]
        A["<code>--hepsi</code> → 4 adım<br/><b>4 dk 06 sn</b><br/>korpus ‖ süit ‖ eval ‖ senaryo"]
    end
    LOCAL -.->|"süit · eval · senaryo<br/>SİLİNMEDİ, TAŞINDI"| CI

    style T fill:#1b5e20,color:#fff
    style A fill:#0d3b66,color:#fff
```

**Neden daraltıldı — ölçüldü:**

| Adım | Bu operasyonda kaç kez kırmızı verdi | Süre |
|---|---|---|
| `eval.run` | **0** — her koşumda `+0,0 / +0,0 / +0,0` | ~1,5 dk |
| konuşma senaryoları | **0** — dokuz sınıf tabanda sabit | ~1,5 dk |
| tam süit | birkaç kez — ama **aynı kusurları `--hizli` de yakaladı** | ~8,5 dk |
| 🔴 **korpus** | **1 kez — ve kimsenin göremeyeceği bir kusuru yakaladı** | **1 dk 57 sn** |

> **Korpusun tek yakalaması:** `gitas` korpustan **tamamen düştü**, payda **445 → 342**'ye
> indi ve doğruluk *"yükseldi"*. `eval` yeşildi, senaryolar yeşildi — çünkü hiçbiri
> ***"kaç soru cevaplanabiliyor"*** sorusunu sormuyor.

**İki dalga zorunluluğu:** korpus (10 süreç) ile süit (8 worker) **aynı anda compose**
yaptı → 20 çekirdek yetmedi → derleme kilidi **60 sn zaman aşımı** → süit **934 hata**.
`--hepsi` bu yüzden **iki dalga** koşar.

## 10.2 · Her kapı neyi ölçer — ve neyi **ÖLÇEMEZ**

| Kapı | ÖLÇER | 🔴 **ÖLÇEMEZ** |
|---|---|---|
| **korpus** (`nl_corpus.py --kapi`) | *"kaç soru cevaplanabiliyor"* · doğru cube oranı · semantik vaka | 🔴 **YANLIŞ YAZILMIŞ soruları** *(sorular katalogdan üretiliyor → hepsi doğru yazılmış → typo yolu HİÇ sorulmuyor)* · **sinonim zenginleşmesini** *(beklenen cevap da katalogdan türetiliyor)* · **cevabın DOĞRULUĞUNU** *(yalnız cube seçimi)* |
| **süit** (`pytest`, **2477+ test**, 194 dosya) | davranış regresyonu | ⚠ **METNİ ölçen testler** — bu operasyonda **10 kez** kendi belgesini/assert satırını yakaladı, hepsi **AST kontrolüne** çevrildi |
| **eval** (`eval.run`) | regresyon kilidi | 🔴 MIMARI §7'nin kendi ifadesiyle *"**zaten çalışan şeye göre kuratörlenmiş**"* — yeni kazanç göremez |
| **senaryo** (`konusma_senaryolari.py`) | dokuz konuşma sınıfı | ⚠ senaryo tümden çökse bile **hiçbir koşulda kırmızı veremez** *(ölçüldü: `returncode == 0`)* |
| **`--hizli`** | değişen modüle **import bağımlı** testler | 🔴 **BİR KAPI DEĞİL, BİR SİNYAL** — davranışa dayanan test **kaçabilir**. Merkezî dosyada küme patlar: `cube_router`+`wren_service` → **1326 test / 6 dk 15 sn** *(korpustan 3× pahalı)* |

## 10.3 · Ölçüm sözleşmesi — `D1…D5`

| Kural | İçerik |
|---|---|
| **D1** | `NE` **üç parçalıdır** *(backend · sözleşme · frontend)* ya da **`api-only` + gerekçe** |
| **D2** | Her sayı **`<sayı> @<sha> · <komut>`** taşır |
| **D3** | Kanıtlanmamış → **`[DOĞRULANMADI]`** |
| **D4** | Enabler, tüketicisinden **önce** *(`KAT-3`)* |
| **D5** | Taşınan madde **kütük bırakır**, silinmez |
| **⊘** | 🔴 **ÜÇÜNCÜ DURUM: `ÖLÇÜLEMEDİ`** — ne geçti ne kaldı |
| **KURAL A** | 🔴 **Donmuş payda dokunulamaz** *(`nl_corpus.py:141` — "ham tur paydası KORUNUR")* |
| **KURAL B** | 🔴 **Bayrak kapalı = BİREBİR aynı davranış**, ve bu **testle kilitlenir** |

## 10.4 · Koşum hijyeni — bağlayıcı

```bash
# TEK SEFERLİK: test imajı  (prod imaj + pytest)
docker build -t dima-api  -f Dockerfile      backend/
docker build -t dima-test -f Dockerfile.test backend/

# ⚠ Depo KÖKÜNDEN koşulur; frontend mount'u ZORUNLU
#   (yoksa yetim-uç kapısı SESSİZCE atlanır)
docker run -d --name dima-k1 --network none \
  -v "$PWD:/repo" -w /repo/backend \
  -e DIMA_VQR_EMBEDDER=off dima-test \
  python lab/kapi.py --tam
docker wait dima-k1 && docker logs dima-k1 && docker rm -f dima-k1
```

| 🔴 Yasak | Sebep |
|---|---|
| **İki test konteynerini paralel koşturmak** | compose kilidi `metadata.yml`'de çakışır *(per-process aynalar geldi ama "aynı ağaca iki süreç giremez" durur)* |
| **Kapı koşarken repoya yazmak** | mount **canlı** |
| `--rm` ile koşmak | log okunamaz → `-d` + `--name` + `docker wait` |
| Payda seyreltmek | **payda kutsaldır** |

---

# 11. v1 bitiş ölçütleri — 16 satır

**12 iç kalite + 4 kullanıcı sonucu.** Üreteç: `backend/lab/faz0_taban.py`.

## 11.1 · İç kalite (1–12) — üreteç ölçer

| # | Ölçüt | Bugün @`0619bfd` | v1 hedefi |
|---|---|---|---|
| 1a | Sessiz-yanlış — **yanlış cube** | **458/7213 = %6,3** | azalır |
| 1b | Sessiz-yanlış — doğru cube üretilemedi | **493/7213 = %6,8** | azalır |
| 1c | **`YANLIS-OK`** (gürültüye SQL) | **7** | **artmaz** |
| 2 | **Doğrudan cevap (OK)** | **7580/10865 = %69,8** | artar |
| 3 | **`CLARIFY:dönem`** | **1478/10865 = %13,6** | 🔴 **DEĞİŞMEZ (±0,5)** — değişirse ADR-0007 K3 **delinmiş** |
| 4 | **Motor-seviyesi RLS** | **0** | `on` · **gölge 7 gün · sapma 0** |
| 5 | **Yetki granülerliği** | 15 araç · **15/15 `query:run`** | araç başına **gerçek aksiyon** |
| 6 | **Onaysız yazma** | yazma aracı **0** · onay akışı **YOK** | **imkânsız** + audit + **30 dk süre aşımı** |
| 7 | **Yetim uç / alan** | **⊘ ÖLÇÜLEMEDİ** | **0** · K1-K5 **kör noktasız** |
| 8 | **Ölçüm kapıları CI'da** | ✅ **hedefe ulaştı** *(`nightly.yml` indi)* | 4 kapı gecelik |
| 9 | **Konuşma türleri** | **5** *(NEDEN·NORMAL·NE_YAPMALI·ISARET·ANLAT)* | 🔴 **v1 = 7** *(+takip +paylaş)* |
| 10 | **Ölü bayrak** | **2** *(`ask_async_discovery` · `threaded_chat`)* → ⟳ **1** @`761928d` *(`ayni_grain_gocu` — derleme zamanı)* | **0** |
| 11 | **Panel sayısı** | **export 13 · dosya 12** | tavan **13 export** |
| 12 | **Tazelik** | **0** | her cevapta 4 kademe |

> 🔴 **Ölçüt 9 — döngüsel kilit çözüldü:** 8. tür (`tur_gorev`) **v3'te**. §B *"v2 için §C
> yeşil olmalı"* diyordu → **v1'in kapanması v3'ün bir maddesini gerektiriyordu.**
> **KARAR: v1 = 7 tür.** Gerekçe **ÖLÜ DOĞUŞ YASAĞI**: *"bir yetenek, ilk tüketicisi aynı
> fazda yazılmadan v1'e giremez."*

> 🔴 **Ölçüt 11 — tanım sayıdan ÖNCE gelir:** `NotificationsPanel` **`NotificationsBell.tsx`
> içinde** yaşıyor; `TercihlerPanel` `export **default**` kullanıyor ve *"`export function`"*
> arayan bir grep'ten **kaçar**. **Tanım B (export) seçildi** — ikisi de sayılır.

## 11.2 · Kullanıcı sonucu (13–16) — 🔴 **hepsi `[ÖLÇÜLMEDİ]`**

| # | Ölçüt | v1 hedefi | Sahibi |
|---|---|---|---|
| **13** | **Görev başarımı** — ekip dışı kullanıcı, kendi işinden **10 soru**, **yardımsız** | **≥%70** kabul edilebilir cevap · **KÖR insan hakem** | **FAZ 8.1** penceresi |
| **14** | **Yeni tenant'ta ilk doğru cevaba kadar** (insan-saat) | **ölçülür ve yayımlanır** | **FAZ 3.0** uçtan uca |
| **15** | **Çok-turlu dayanıklılık — `pass^k`** *(`pass@k` DEĞİL)* | 5 turda yapı kaybı **0** · `pass^5` raporlanır | **FAZ 4.3** sharding |
| **16** | 🔴 **UÇTAN UCA cevap doğruluğu, BAĞIMSIZ kümede** | **n≥100** · tutulmuş küme · **İLAN EDİLMİŞ puanlama** | **FAZ 4.8** `lab/uctan_uca.py` |

> 🔴 **Neden 16 zorunlu:** §C/1-2 **cube SEÇİMİNİ** ölçüyor *(%93,1 = "doğru cube",
> "doğru cevap" **değil**)*. Rakiplerin yayımladığı **tek kıyaslanabilir sayı** budur ve
> **bugün elimizde ölçecek alet yok** → **FAZ 4.7'nin teknik raporu bu sayı olmadan
> YAYIMLANAMAZ.**
>
> **İlan edilmiş puanlama kuralı:** *"bir cevap ancak **dönen değer**, **varlık kapsamı** ve
> **zaman/filtre semantiği** altın cevapla eşleşiyorsa doğru sayılır."*
> 🔴 **Netleştirme AYRI SATIR** olarak raporlanır — **paydadan gizlice çıkarılmaz.**
> *(Rakiplerin manşet sayılarını kıyaslanamaz yapan şey tam olarak budur.)*
>
> ⚠ **Ve açık soru kayda geçer:** `nl_accuracy`'nin **63 etiketli vakasının etiketlerini
> KİM doğruladı?** BIRD/Spider'da anotasyon hata oranı **%52,8 / %62,8** ölçüldü →
> **10 puanın altındaki fark GÜRÜLTÜDÜR.**

## 11.3 · Bugünkü korpus — dört şirket @`eb48c40`

| Şirket | Ham tur | Doğru cube | Yanlış | Discovery | Semantik vaka |
|---|---|---|---|---|---|
| boyahane | 5306 | **3266** | 216 | 37 | **171/190 (%90)** |
| gitas | 1447 | **931** | 18 | — | **66/68 (%97)** |
| atiksan | 1618 | **995** | 45 | — | **78/83 (%94)** |
| gulteks | 2479 | **1517** | 179 | — | **92/103 (%89)** |
| **TOPLAM** | **10850** | **6709** | **458** | **37** | **407/444 = %91,7** |

**Doğru cube oranı: 6709 / 7204 = %93,1**

---

# 12. Kalan yol — FAZ 4→8 + §G

```mermaid
flowchart LR
    F1["<b>FAZ −1</b><br/>MIMARI ön hazırlık"] --> F2["<b>FAZ 0</b><br/>25 madde<br/>temizlik + kapılar"]
    F2 --> F3["<b>FAZ 1</b><br/>GÜVENCE<br/>19 adım"]
    F3 --> F4["<b>FAZ 2</b><br/>SEMANTİK ÇEKİRDEK<br/>13 adım"]
    F4 --> F5["<b>FAZ 3</b><br/>KAPSAM<br/>7 adım"]
    F5 --> F6["<b>FAZ 4</b><br/>ÖLÇÜM ve KANIT"]
    F6 --> F7["<b>FAZ 5</b><br/>KONUŞMA<br/>17 madde"]
    F7 --> F8["<b>FAZ 6</b><br/>AGENTIC +<br/>ONAYLI YAZMA"]
    F8 --> F9["<b>FAZ 7</b><br/>ARAYÜZ"]
    F9 --> F10["<b>FAZ 8</b><br/>AÇILMA"]

    G["<b>§G · AJAN KATMANI</b><br/>AJ0 → AJ6<br/><i>v1'e PARALEL, ona BAĞIMLI DEĞİL</i>"] -.-> F6
    F3 -.->|"🔴 8.1 BURADA AÇILIR<br/>ve FAZ 2-7 boyunca AÇIK KALIR"| W["<b>8.1 · GERÇEK<br/>KULLANIM PENCERESİ</b><br/>≥300 gerçek tur"]

    style F1 fill:#1b5e20,color:#fff
    style F2 fill:#1b5e20,color:#fff
    style F3 fill:#1b5e20,color:#fff
    style F4 fill:#1b5e20,color:#fff
    style F5 fill:#1b5e20,color:#fff
    style F6 fill:#e65100,color:#fff
    style F7 fill:#37474f,color:#fff
    style F8 fill:#37474f,color:#fff
    style F9 fill:#37474f,color:#fff
    style F10 fill:#37474f,color:#fff
    style G fill:#4a148c,color:#fff
    style W fill:#7d1128,color:#fff
```

## 12.1 · FAZ 4 — ÖLÇÜM ve KANIT *(aktif)*

| Madde | Ne | Kapı | Durum |
|---|---|---|---|
| `4.1` | → **FAZ 0.15'e taşındı** | — | ✅ |
| `4.2` | **Risk-kapsam eğrisi** | `hata_orani` **yazılmaz**; `consistency` alanına **hiç bakılmaz** | ✅ `eb48c40` |
| `4.3` | **Çok-turlu Türkçe benchmark (sharding)** | 5 turda doğruluk **−%10'dan az** düşsün *(makalenin **−%39**'una karşı)* | 🔵 **koşuluyor** |
| `4.4` | **Ossie ihracı** + `Custom Extensions` | 🔴 **round-trip: ihraç → geri ithal → BİREBİR aynı SQL** | ⬜ |
| `4.5` | **MCP yüzeyi** | MCP'den çağrılan araç HTTP'yle **aynı 4 kapıdan** geçer, **aynı makbuzu** üretir | ⬜ |
| `4.6` | **`docs/adr/`** | **20 ADR kimliği · 252 atıf · 0 dosya**. Yeni kimlik **dosya olmadan merge edilemez** | ⬜ |
| `4.7` | **Teknik rapor** | 🔴 **§C/16 ölçülmeden YAYIMLANAMAZ** | ⬜ |
| `4.8` | **Uçtan uca doğruluk aleti** | küme **tutulmuş** kalır; puanlama kuralı **kod içinde tek yerde** | ⬜ |

### `4.3` — sharding: ilk gerçek ölçüm

```
gitas · örnek 39 konuşma
| tur | tam cevaplanan | yapı kaybı | cube_query sürekliliği |
|-----|----------------|------------|------------------------|
|  1  |     %84.6      |     0      |         %84.6          |
|  2  |     %84.6      |     0      |         %84.6          |
|  3  |     %84.6      |     0      |         %84.6          |
|  4  |     %84.6      |     0      |         %84.6          |
|  5  |     %84.6      |     0      |         %84.6          |

🔴 5 turda düşüş: %0.0    (makale: −%39, 15 model, 200.000+ konuşma)
🔴 yapı kaybı:    0
```

> **Neden düz:** mimarimiz **recap'in DETERMİNİSTİK hâlini yapısal olarak** uyguluyor —
> her turda `cube_query` **geri gönderiliyor** ve `deterministic_refine` onu **düzenliyor**.
> Taşınan şey bir **metin özeti değil, yapının kendisi**.
> ⚠ **Bu fark dünyada ölçülmemiş:** makale *text-to-SQL*'de ölçtü; **semantik katmanın aynı
> testteki farkı hiç ölçülmedi.**
>
> ⚠ **Aracın kendi kusuru kayda geçti:** ilk sürüm `route()`'un **sarmalayıcısını** açmıyordu
> → `atomlar()` boş liste döndürdü → **eğri tamamen boş** çıktı ama tablo **dolu görünüyordu**.
> *Boş bir eğri, kötü bir eğriden daha tehlikelidir.*
>
> 🔴 **`GERİ AL`:** sonuç kötü çıkarsa **yayımlanır**. Kötü sonucu saklamak §C/16'nın
> *"ilan edilmiş puanlama kuralı"* şartını çiğner.

## 12.2 · FAZ 5 — KONUŞMA ve DENEYİM *(17 madde)*

| Madde | Ne | Bayrak |
|---|---|---|
| `5.0` | 🔴 **K3 — konuşma türleri thread'lerin bir sınıfına YAPISAL OLARAK kapalı** | bayraksız: **hata** |
| `5.1` | ⭐ **6. tür: *"bunu takip et"*** | `tur_takip` |
| `5.2` | ⭐ **7. tür: *"paylaş / müdüre 3 cümle"*** | `tur_paylas` |
| `5.3` | Kalıp sözlüklerini **kullanıcı ifadelerinden** besle | bayraksız — 🔴 **kaynağı FAZ 8.1** |
| `5.4`–`5.5` | Eksik chip'ler · başlık Δ kartı + **streak** | bayraksız |
| `5.6` | ⭐ **Peer karşılaştırma** — 🔴 **ÖN KOŞUL: AJ2** | `peer_kiyasi` |
| `5.9` | Kanal genişlemesi + **bildirim kapısı** | `kanal_slack` · `kanal_whatsapp` · `sabah_digest` |
| `5.11` | *"Ne zaman grafik ÇİZİLMEZ"* | bayraksız: **deterministik** |
| `5.14` | **Hızlı ↔ Derin anahtarı** | `hizli_derin` |
| `5.16` | Netleştirme **düzeyi** — bir AYAR | `netlestirme_duzeyi` |
| `5.17` | ⭐ **Tek ses — `app/soz.py` metin katalogu** | bayraksız: **kök neden** *(`note` dört iş yapıyor)* |

## 12.3 · FAZ 6 — AGENTIC ve ONAYLI YAZMA

```mermaid
flowchart LR
    A["Ajan yazma aracını<br/><b>ÖNERİ</b> olarak üretir"] --> B["👤 Kullanıcı <b>ONAYLAR</b>"]
    B --> C["<code>authorize()</code> + audit<br/><i>ikisi de ZATEN VAR</i>"]
    C --> D["çalışır"]
    B -.->|"geri alınamaz iş"| E["🔴 <b>SENKRON onay</b>"]
    B -.->|"orta risk"| F["kuyruk"]
    G["🔴 <b>KAPI:</b> onaysız HİÇBİR yazma gerçekleşmez<br/>her onay audit'e AYRI SATIR · süre aşımı <b>30 dk</b>"]

    style G fill:#b71c1c,color:#fff
```

| Madde | Ne | Bayrak |
|---|---|---|
| `6.0` | 🔴 **D9 BUGÜN TERS UYGULANMIŞ — "yapılanı geri al"** | `onay_akisi` |
| `6.1` | **Onay akışı** | `onay_akisi` |
| `6.2` | **Yazma araçları** *(bugün `llm_araclari` dışında — bilerek)* | `yazma_araclari` |
| `6.3`–`6.4` | Araç kaydı genişlemesi · planlayıcı sertleştirmesi | bayraksız |
| `6.5` | Public API + async job + embed | `public_api` · `embed` |
| `6.6` | Mesajlaşma kimlik eşlemesi | `kanal_kimlik` |

## 12.4 · FAZ 7 — ARAYÜZ

| Madde | Ne | Kapı |
|---|---|---|
| `7.0` | Planın **kendi 5 iç boşluğu** kapatılır | bayraksız |
| `7.1` | ⭐ `ui_*` bayrakları **backend'e KAYDEDİLİR** | bayraksız: **değişmez** *(12 `ui_*` bugün yalnız frontend'de)* |
| `7.2` | Tasarım sistemi | **görsel regresyon kapısı** |
| `7.4` | Panel/katman disiplini — **24 kural** | `K5` |
| `7.5` | **a11y — 10 kural** | kapı |
| `7.6` | **Responsive — 3 kademe** | `V-2` |
| `7.8` | ⭐ **Ayırt edicileri GÖRÜNÜR KIL** + güven yüzeyleri | `ui_kanit_gorunurlugu` |
| `7.9` | **Mock silme kapısı** | bayraksız |

## 12.5 · FAZ 8 — AÇILMA

| Madde | Ne | Not |
|---|---|---|
| `8.1` | 🔴 **GERÇEK KULLANIM PENCERESİ** | **KOD DEĞİL.** 1-2 gerçek kullanıcı, 2-4 hafta, **≥300 gerçek tur**. 🔴 **FAZ 1'den sonra AÇILIR, FAZ 2-7 boyunca AÇIK KALIR** |
| `8.2` | → **FAZ 3.0'a taşındı** | kütük |
| `8.3` | Çok-worker dağıtım | `gunicorn 4 worker` duman testi |

> 🔴 **`KAT-3`'ün ikinci ihlali buydu:** `8.1` en sondaydı → **~130 madde hiçbir gerçek
> kullanıcı görmeden inşa ediliyordu.** Planın kendi doktriniyle *(“kusuru önce ÖLÇ”)*
> çelişen tek büyük yapısal karardı.
>
> **Ön koşul:** `1.1` (`motor_rls=shadow`) + `1.3` (yetki) + `1.3b` (`enforce_query`) +
> `1.8` (audit). **RLS'in `on` olması gerekmez** — gölge mod ölçer, engellemez.
> 🔴 **Kapı:** FAZ 5'e girildiğinde `interaction_log`'un *"kendi denemelerimiz"* payı **<%50**.

## 12.6 · §G — AJAN KATMANI *(v1'e paralel)*

> ⟳ **2026-08-08 · §G'nin YERİNİ «GARSON ARA FAZI» ALDI.** Ara faz §G'yi **iptal etmedi**;
> *ölçülmüş gerçeklikle yeniden sıraladı* ve **dokuz maddesini** `G0…G8` olarak indirdi
> *(113 adım · 3 bilerek ertelendi)*. Karşılık:
>
> | §G maddesi | ⟳ Ara fazdaki karşılığı | Durum |
> |---|---|---|
> | `AJ0` kısa devre yasağı | **`G3` merdiven** | ✅ indi |
> | `AJ0b` diyalog yöneticisi | **`G2` diyalog belleği** *(`diyalog.py` 🚩 prod)* | ✅ indi |
> | `AJ1` iddia kapısı | **`G4`** *(`iddia.py` 221 satır)* | ✅ indi |
> | `AJ2` referans cebiri | **`G6` kıyas cebiri** *(`kiyas_cebiri.py` 265)* | ✅ indi |
> | *(§G'de yoktu)* | 🔴 **`G0` alet** · **`G0b` hava boşluğu** · **`G1` temellendirme** · **`G5` anlatıcı** · **`G7` ek motoru** · **`G8` menü** | ✅ indi |
> | `AJ3` tur yöneticisi · `AJ3b` çalışırken sorma · `AJ4` oturumlar-arası · `AJ5`/`AJ5b` planlayıcı · `AJ6` bileşik rapor | **ara fazın KAPSAMI DIŞINDA** *(gerekçesiyle)* | 🔵 açık |
>
> 🔴 **Sıra bağlayıcıydı ve sebebi tek cümleydi:** *"`G0` inmeden hiçbir kod yazılmaz —
> ölçemediğimiz bir şeyi geliştiremeyiz."*

| Madde | Ne | Bayrak | Not |
|---|---|---|---|
| **`AJ0`** | 🔴 **KISA DEVRE YASAĞI** — MIMARI §5'in **18. yasağı** | bayraksız: **değişmez** | 🔴 **ÖNCE BU İNER** — yazım-benzerliği chip'i merdiveni **kesiyor** |
| `AJ0b` | ⭐ **DİYALOG YÖNETİCİSİ** — atlanmış katman | `diyalog` | §G'nin ilk maddesi |
| `AJ1` | ⭐ **İddia kapısı** — `app/iddia.py` | bayraksız | **B'nin ÖN KOŞULU** · *"olmayan yetenek vaadi"* |
| `AJ2` | ⭐ **CubeQuery formdan DİLE** — `referans` bileşimsel alanı | `referans_dili` | `KAT-5`'in cevabı |
| `AJ3` | ⭐ **Turu LLM yönetir** — ikinci yürütücü | `tur_yoneticisi = deterministik\|ajan` | |
| `AJ3b` | ⭐ 🔴 **ÇALIŞIRKEN SORMA** | `calisirken_sorma` | SSE'ye **`soru` olayı** · `AskJob.status`'a **`awaiting_input`** |
| `AJ4` | Oturumlar-arası süreklilik | `oturumlar_arasi_hafiza` | |
| `AJ5` | ⭐ **Planlayıcıyı AÇ ve ÖLÇ** + araç yüzeyi | `agent_plan_secimi` | **kuzey yıldızının A'sı** |
| `AJ5b` | ⭐ 🔴 **ADIM ZİNCİRİ** — planlayıcı araç **seçiyor**, adımları **bağlamıyor** | `adim_zinciri` | |
| `AJ6` | **Bileşik rapor artefaktı** | `bilesik_rapor` | **kuzey yıldızının C'si** |

---

# 13. Bilinen kırıklar ve açık borçlar

## 13.1 · 🔴 Bugün açık — v1'i bloke edenler

> ⟳ **2026-08-08 · dokuz borcun DÖRDÜ kapandı.** Aşağıdaki tablo **özgün hâliyle duruyor**;
> kapananlar altına işaretlendi. *Bir borcun kapandığını yazmak, açıldığını yazmak kadar
> zorunludur — yoksa harita kendi ilerlemesini de yanlış öğretir.*

| # | Ne | Etki | Nerede kapanır |
|---|---|---|---|
| 1 | 🔴 **36 çağrı sitesi `principal` geçmiyor** | **`motor_cls=on` KİLİTLİ** — kapı engelliyor | FAZ 1.2 |
| 2 | 🔴 **`AJ0` typo kısa devresi** | Ölçüldü: 13 turun **4'ü** planlayıcıya sıra gelmeden ölüyor. Korpusta `acik borc` → *"«cari borc» mi?"* → **Discovery'ye hiç gidilmiyor**. `KAT-2` ihlali | §G / `AJ0` |
| 3 | 🔴 **`app/iddia.py` YOK** | *"olmayan yetenek vaadi"* uydurulabilir — **tek kapatılmamış uydurma** | `AJ1` |
| 4 | 🔴 **`R11` yok** | *"ifade edemiyorum"* ≠ *"anlamadım"* → **eksik yetenek sayılamıyor** | v1 |
| 5 | 🔴 **Ölü bayrak 2** | `ask_async_discovery` · `threaded_chat` kayıtta var, YAML'de yok | §C/10 |
| 6 | 🔴 **`ask()` = 1147 satır / 19 iç fonksiyon** | Katmanlar bu monolitin **etrafında** oluşuyor, içinde değil | tavan kapısı `0.21` |
| 7 | 🔴 **7 güvenlik kontrol noktası, tek cümlelik sınır tanımı YOK** | `guard_sql` · `strict_sql_policy` · `always_filter` · **Katman B** · RLS · CLS · `pii` — her biri gerekçeli ama **bileşke** yazılı değil | `1.3c` yalnız `strict_sql_policy` için yazdı |
| 8 | ⚠ **`hedef_kiyasi` bayrağı kayıtta yok** | `app/hedef.py` indi ve çağrılıyor; bayrak **`FLAG_REGISTRY`'de bulunamadı** | *bu belgenin kendi ölçümü — **kaynağı koş**, bkz. §7.3* |
| 9 | ⚠ **`docs/adr/` — 20 kimlik, 252 atıf, 0 dosya** | 🔴 **ADR-0007-K3, §C'nin 3. çıkış ölçütünü taşıyor** — yani v1'in kırmızı çizgisi **var olmayan bir belgeye** dayanıyor | `4.6` |

### ⟳ 2026-08-08 · dokuz borcun durumu — yeniden ölçüldü

| # | Özgün borç | ⟳ Bugün | Kanıt |
|---|---|---|---|
| 1 | `motor_cls=on` KİLİTLİ *(36 çağrı `principal` geçmiyor)* | 🔴 **AÇIK** | `features.py:124` hâlâ *"açılması 36 …"* diyor |
| 2 | `AJ0` typo kısa devresi | ✅ **KAPANDI** *(`G3`)* | `test_kisa_devre_yok.py:190,196` meta-kapı |
| 3 | `app/iddia.py` YOK | ✅ **KAPANDI** *(`G4`)* — **221 satır** | `wc -l app/iddia.py` |
| 4 | `R11` yok | ⊘ **DENENDİ → GERİ ALINDI**, gerekçesiyle | `cube_router.py:3530` |
| 5 | Ölü bayrak **2** | ◐ **1'e düştü** — kalan `ayni_grain_gocu` **derleme zamanı**, bilinçli | `FLAG_REGISTRY` ↔ `features.yml` |
| 6 | `ask()` monoliti | 🔴 **BÜYÜDÜ** — `app/routers/ask.py` **4938 satır** *(belge 1147 diyordu)* · ⟳ **2026-08-09: 5485** — orkestratör dalı + `§BB-B` boş-cevap guard'ı | `wc -l` |
| 7 | 7 güvenlik noktası, **bileşke tanım yok** | ◐ **§0.5 ilk bileşke listeyi yazdı** — ama bir **belge**, kapı değil; `1.3c` borcu **açık** | bu belge §0.5 |
| 8 | `hedef_kiyasi` kayıtta yok | ✅ **KAPANDI** | `features.py:53` |
| 9 | `docs/adr/` — 0 dosya | 🔴 **AÇIK** | `4.6` |

**⟳ Ve ara fazın DOĞURDUĞU yeni borçlar** *(kaynak: `DIMA-GARSON-ARA-FAZ.md` §6.Ω/b)*:

| # | Ne | Ağırlık |
|---|---|---|
| `B2` | 🔴 **LLM yolunun ilk gerçek metriği yok** — koşulan her kapı `route()`'u ölçüyor. **2 116 etiketli vaka var, ayıklanmadı** | 🔴 yüksek |
| `Ö5` | Guard **düşme oranı** agrege alarmı | ◐ `guard_alarmi.py` indi, eşik borcu açık |
| `tsc` | Frontend tip kontrolü **gecelik CI'da HİÇ koşmuyor** *(node adımı yok)* → `test_TSC_TEMIZ` **her zaman atlanıyor** | 🔴 yüksek |
| `B1·B3` | Şema budaması **ASKIYA ALINDI** — doğru nüfusta recall **%78,1 · 464 KAYIP** *(n=2 116)* | ⊘ yeni sinyal gerekiyor |
| `S5` | `{{ENT_i}}` **varlık perdesi inmedi** — hava boşluğunun eksik yarısı | orta |
| `diyalog.py` | Fazın **en büyük yeni katmanının** `MIMARI.md` kaydı **yok** | orta |
| `kapasite` | 🔴 **Plan kendi içinde çelişiyor** — `§13.5b` alanı şart koşuyor, `§13.5c` yasaklıyor; kod ikincisini seçip **testle kilitledi**, `lab/garson.py` hâlâ birincisini okuyor → **ölü dal** | orta |

**⟳ 2026-08-09 · ORKESTRATÖR FAZININ doğurduğu borçlar** *(hepsi §4.6'da ölçülerek yazıldı)*:

| # | Ne | Ağırlık |
|---|---|---|
| `O-a` | 🔴 **Dört fiilin çalıştırıcısı bağlı değil** — `TREND` · `AYRISTIR` · `KIYASLA` · `ANLAT`. Bayrağın kazancının bugün **sıfır** olmasının birinci sebebi | 🔴 yüksek |
| `O-b` | 🔴 **Serbest-JSON sağlayıcı adım sözleşmesine uymuyor** — fiili doğru, parametreyi uydurma yazıyor; `ZORUNLU_ALANLAR` düşürüyor *(doğru davranış, ama plan hiç çıkmıyor)* | 🔴 yüksek |
| `O-c` | ⚠ **Gecikme kaydı ELLE yazıldı** — `nl_corpus.py` `sure_sn`'i bir rapora yazmıyor; `test_latency_tavani.py` kayıt yoksa **atlanıyor** *(uydurma sayı üretmiyor)* | orta |
| `G1·Y6` | 🔴 **Menüdeki boşluk sınıf DEĞİŞTİRDİ:** *«tamir süresi»* artık cevapsız değil, **YANLIŞ** — `bakim` yerine `kalite.toplam_ek_sure_dk`'dan cevaplanıyor. *Bir boşluğu kapatmanın en sessiz yolu, onu yanlış bir yemekle doldurmaktır* | 🔴 yüksek |
| `G1·Z12` | *«şikayetleri bölgelere göre»* — `sikayet`+`bolge` mutfakta **var**, menüde çekim eşleşmiyor → cevapsız | orta |

## 13.2 · Yinelenen kusur sınıfları — bu operasyonda ölçüldü

```
┌─ 1 · "beyan var, kod onu tanımıyor" ──────────────────────────────────┐
│    capa_zinciri: coz() doğru kuralı üretiyordu, zincir onu OKUMUYORDU │
├─ 2 · "kimlik asimetrisi" ─────────────────────────────────────────────┤
│    kural bir dalda vardı, kardeşinde yoktu                            │
├─ 3 · "aynı kuralın iki sahibi" ───────────────────────────────────────┤
│    netlestirme_onceligi kararı hem YAML yorumunda hem MIMARI'de       │
├─ 4 · "ölçüm aracının kendisi de bir bağımlılıktır" ───────────────────┤
│    faz0_taban host'ta 1806, konteynerde 2056 sayıyordu → artık ⊘ yazıyor│
├─ 5 · 🔴 "testler METNİ ölçtü, davranışı değil" ───────────────────────┤
│    BU OPERASYONDA 10 KEZ. Hepsi AST/yapısal kontrole çevrildi.        │
│    ⟳ sayacı kendi paragrafını saydı · tavan testi kendi assert'ini    │
│    yakaladı · _IPTAL araması DURUM_IPTAL sabitinin ADINI yakaladı     │
└───────────────────────────────────────────────────────────────────────┘
```

## 13.3 · ContextVar deseni — 3 kez kanıtlandı

```
llm._llm_usage_var  ·  cube_router._reddi_var  ·  mali_takvim._ay_var

   derin fonksiyon OKUR  ←  sığ fonksiyon YAZAR  ←  imzalar DEĞİŞMEZ
```

---

# 14. Frontend yüzeyi — 13 panel · 36 bileşen

## 14.1 · Panel envanteri *(§C/11 · tanım B = export)*

| # | Panel | Dosya | Tükettiği uç |
|---|---|---|---|
| 1 | `ChatPanel` | `ChatPanel.tsx` | `/ask` · `/ask/jobs` · `/cube` |
| 2 | `ReportPanel` | `ReportPanel.tsx` | — *(kart konteyneri)* |
| 3 | `SchemaPanel` | `SchemaPanel.tsx` | `/schema` · `/metrics` · sahiplik |
| 4 | `DashboardsPanel` | `DashboardsPanel.tsx` | `/dashboards` |
| 5 | `SchedulesPanel` | `SchedulesPanel.tsx` | `/schedules` |
| 6 | `ReviewPanel` | `ReviewPanel.tsx` | terfi kuyruğu + **KapanisOrani** |
| 7 | `HistoryPanel` | `HistoryPanel.tsx` | sohbet geçmişi |
| 8 | `DrillDownPanel` | `DrillDownPanel.tsx` | `/ask/drill` |
| 9 | `ContractDetailPanel` | `ContractDetailPanel.tsx` | Query Contract makbuzu |
| 10 | `ConnectionReviewPanel` | `ConnectionReviewPanel.tsx` | bağlantı + **Ossie ithal adımı** |
| 11 | `HelpPanel` | `HelpPanel.tsx` | — |
| 12 | `NotificationsPanel` | ⚠ **`NotificationsBell.tsx` içinde** | bildirimler |
| 13 | `TercihlerPanel` | `TercihlerPanel.tsx` *(`export default`)* | `/tercihler` |

> 🔴 **Tavan: 13 export.** Bölüm II'de **15** (PK-23).
> ⚠ `facetPanelValues` *(`lib/chart.ts`)* bir **yardımcı fonksiyondur, panel değildir** —
> kapının regex'i `function [A-Za-z]+Panel` **sonu** ile sınırlıdır.

## 14.2 · Arka-ön entegrasyon değişmezi

```
🔴 Bir backend yeteneği, FRONTEND TÜKETİCİSİ OLMADAN "bitti" DEĞİLDİR.
   Yetim uç  =  CI HATASI       (test_uc_yetim_degil)
   Yetim alan =  CI HATASI      (test_cevap_alani_yetim_degil)
   Yeni özellik  YENİ PANEL DOĞURMAZ  (tavan 13)
```

**Ölçülmüş iki kez tekrarlanan kusur:**

| # | Ne oldu | Kullanıcıya sonucu |
|---|---|---|
| `0.23` | **Ölü render dalı** — `ReportPanel` kapısı *"raporlanabilir mi"* + *"render edilebilir mi"* **iki iş** yapıyordu | **Ödenmiş üç özellik EKRANDA YOKTU** |
| *(aynı sınıf)* | FAZ H'nin *"Onayla"* kartı aynı kapının arkasındaydı | **Onayla düğmesi HİÇ ÇIKMIYORDU** |

**Düzeltme deseni — `KAT-5`:** *gövde alanları **sayılmaz**; **saf-not** (yalnız açıklama)
kapatılır.* Unutulan bir gövde alanı **sessiz** kayıptı; şimdi **görünür** gerileme üretir.

---

# EK · Tek bakışta komut kartı

```bash
# ── GELİŞTİRME (sinyal, kapı değil) ────────────────────────────────
python lab/kapi.py --hizli --degisen app/eylem.py tests/test_eylem_onayi.py

# ── DEMET SONU (yerel kapı = YALNIZ KORPUS, 1 dk 50 sn) ────────────
python lab/kapi.py --tam
python lab/kapi.py --tam --sadece korpus     # yalnız kırmızı olanı

# ── GECELİK CI (dört adım, 4 dk 06 sn — YERELDE ASLA) ──────────────
python lab/kapi.py --hepsi

# ── ÖLÇÜM ALETLERİ ─────────────────────────────────────────────────
python lab/faz0_taban.py                     # §C 1a…12 taban
python lab/nl_corpus.py --kapi               # korpus
python lab/nl_accuracy.py --ab <bayrak>          # GERİLEME
python lab/nl_accuracy.py --ab-kurtarma <bayrak> # KAZANÇ
python lab/risk_kapsam.py                    # risk-kapsam eğrisi
python lab/sharding.py --tur 5               # çok-turlu benchmark
python lab/mdl_diff.py                       # gölge derleme diff
python lab/r1_envanteri.py                   # R1 envanteri
python lab/telemetri_envanteri.py            # FAZ 8.1 kapısı
python lab/bayrak_profilleri.py              # profil ölçümü

# ── CANLI (kota: 10 sn / 10 istek · Intent turu = 3 çağrı) ─────────
python lab/deneyim.py --live
python lab/konusma_senaryolari.py --live

# ── ⟳ GARSON KAPISI (2026-08-08 · beşinci alet) ────────────────────
python lab/garson.py --live          # §5'in 8 satırı — --live ZORUNLU
python lab/kapi.py --garson          # hedef, YENİ SEVİYE DEĞİL
#   ⚠ --live olmadan: yeşil vermez, ⊘ verir
#   🔴 KURAL G-1: iki koşum ayrışırsa KARAR VERİLMEZ
#   çıktı: lab/reports/garson/*.md  ·  taban: lab/garson_baseline.json

# ── ⟳ ORKESTRATÖR ALETLERİ (2026-08-09 · O-8/O-9) ──────────────────
python lab/menu.py --sirket demo-boyahane   # G1: mutfakta VAR, menüde YOK
#   🔴 KARAR VERMEZ, kanıtlı İŞ LİSTESİ üretir (§99.1 · lab/r1_envanteri.py dersi)
#   ⚠ şemayı TAZE derlemeden okur — demo/wren-project gitignore'lu bir ARTEFAKT
python lab/discovery_orani.py --ab orkestrator_plan   # arıza oranı A/B
#   🔴 PAYDA KUTSALDIR: paydalar eşitlenemezse KIYAS REDDEDİLİR
#   okuma: llm:* ∨ cevapsız ∨ cube=adhoc  →  hepsi ARIZA RAPORU
#   kayıt: lab/olcumler/{orkestrator_ab,menu,latency}.md  (lab/reports/ DEĞİL — ignore'lu)
```

---

# 15. DENETİM — bu belgenin kendi eksikleri *(ölçüldü, kapatıldı)*

Belge kendi iddiasına karşı tarandı: **26 kavramın 12'si eksikti**. Altısı v1 tarafındaydı
ve aşağıda kapatıldı; kalan altısı Bölüm II'ydi → **§16–§17**.

| # | Eksikti | Kapatıldı |
|---|---|---|
| 1 | `/ask/contribution` ucu | §15.1 |
| 2 | SSE akışı + `AskJob` durum makinesi | §15.2 |
| 3 | Eskalasyon *(1.10)* + kademeli düşüş *(1.11)* | §15.3 |
| 4 | `db_introspect` / tenant açılış zinciri *(3.0)* | §15.4 |
| 5 | **FAZ 0 ve FAZ 1 özeti** — §12 yalnız 4→8'i kapsıyordu | §15.5 |
| 6 | **Uç envanteri (66 uç)** + konuşma türü / takip sınıfı **adları** | §15.6 |

## 15.1 · `/ask` dışındaki cevap yolları — hepsi `seal()`'dan geçer

```mermaid
flowchart TD
    A["<code>POST /ask</code><br/>ana merdiven"] --> S
    B["<code>POST /cube</code><br/>doğrudan CubeQuery<br/><i>chip tıklaması</i>"] --> S
    C["<code>POST /report</code><br/>rapor derleme"] --> S
    D["<code>POST /ask/drill</code><br/><b>kırılım dallanması</b><br/>🔴 Discovery'de DÜRÜSTÇE REDDEDER"] --> S
    E["<code>POST /ask/contribution</code><br/><b>KATKI AYRIŞTIRMASI</b><br/><i>'artışın %kaçı kimden?'</i>"] --> S
    F["<code>POST /ask/eylem</code><br/>eylem önerisi"] --> S
    G["<code>POST /ask/verify</code> · <code>/verify</code><br/>✓/✗ → VQR öğrenmesi"] --> S
    H["<code>GET /dashboards/{did}/data</code><br/>pano canlı veri"] --> S
    I["<code>POST /schedules/{sid}/run</code><br/>zamanlanmış koşum"] --> S

    S["🔒 <code>answer.seal()</code>"] --> OUT(["makbuz + PII maskesi + audit"])

    style S fill:#4a148c,color:#fff
    style E fill:#0d3b66,color:#fff
```

**`/ask/contribution` — `contribution.py`:** *"toplam neden değişti"* sorusunu **PVM
ayrıştırmasıyla** (fiyat · miktar · karışım) cevaplar. 🔴 **Kapısı:**
`ayristirilabilir_mi` — **`AVG`/oran ölçüsü ayrıştırılamaz** *(matematiksel olarak yanlış
olurdu)* → dürüst red. *Bu fonksiyon v2'de `II-D.2`'nin tahmin motoru tarafından **birebir
aynı** çağrılacak.*

## 15.2 · Arka plan işi + SSE — `AskJob` durum makinesi

```mermaid
stateDiagram-v2
    [*] --> queued: "POST /ask (Discovery kuyruğa alındı)"
    queued --> running: "worker aldı"
    running --> done: "cevap üretildi"
    running --> error: "sağlayıcı tükendi"
    running --> timeout: "süre aşımı"
    running --> cancelled: "DELETE /ask/jobs/{id}"
    done --> [*]
    error --> [*]
    timeout --> [*]
    cancelled --> [*]
```

**SSE olayları** (`GET /ask/jobs/{job_id}/stream`): `adim` · `tamam` · `hata` · `zaman_asimi`

> 🔴 **`KAT-5` ihlali burada duruyor ve `AJ3b`'de kapanacak:** SSE olay kümesinde **`soru`
> yok**, `AskJob.status`'ta **`awaiting_input` yok**. Yani ajan *"başlıyorum… bu arada şunu
> anlamadım"* **diyemez** — sorabilmesi için **yeni bir olay + yeni bir durum** gerekiyor,
> ki bu tam olarak *"sayılan küme, her yeni anlam için kod ister"* deseni.
>
> ⚠ `recover_stale_ask_jobs()` — süreç yeniden başladığında **asılı kalmış** işleri
> kurtarır *(`ask.py:1249`)*.

## 15.3 · Eskalasyon *(1.10)* + kademeli düşüş *(1.11)* — FAZ 1'in son iki maddesi

```mermaid
flowchart LR
    subgraph K["app/kademeli_dusus.py — KADEMELİ DÜŞÜŞ"]
        K1["motor yavaş/düşük"] --> K2["önbellek ∨ kısmi sonuç"]
        K2 --> K3["🔴 <b>SESSİZ DÜŞMEZ</b><br/>kullanıcı hangi kademede olduğunu GÖRÜR"]
    end
    subgraph E["app/eskalasyon.py — ESKALASYON MATRİSİ"]
        E1["bulgu/anomali"] --> E2["şiddet × sahiplik"]
        E2 --> E3["kime · ne zaman · hangi kanaldan"]
    end
    style K3 fill:#b71c1c,color:#fff
```

**Değişmez:** düşüşün kendisi **cevabın rozetine** yansır — *"süssüz ama doğru"* ilkesinin
altyapı karşılığı. **v2'de `II-F.6`'nın görev motoru** `eskalasyon`'u **ikinci tüketici**
olarak kullanır *(30 gün cevapsızlık → ağırlık düşür + eskalasyon)*.

## 15.4 · Tenant açılış zinciri *(FAZ 3.0)* — `db_introspect` → ilk cevap

```
  müşteri bağlantısı        POST /test  ·  POST /{cid}/confirm
        ↓
  db_introspect             tablo · kolon · FK · kardinalite taraması
        ↓
  coldstart.oner()          🚩 metrik ADAYI üretir  —  🔴 ASLA otomatik canlıya çıkmaz
        ↓                      (ADR-0018: "adaylar otomatik canlıya çıkmaz")
  ReviewPanel               insan ONAYLAR
        ↓
  packs/companies/<slug>    şirket katmanı yazılır
        ↓
  materialize() → compose() → mdl.json → WrenEngine
        ↓
  🎯 İLK DOĞRU CEVAP        ← §C/14: "insan-saat ölçülür ve YAYIMLANIR"  [ÖLÇÜLMEDİ]
```

> Bu zincir **v2'nin `II-F.8`'inin (şirket profili) doğrudan ön koşuludur** — ve
> `II-F`'nin *"SOR değil TÜRET"* stratejisi tam olarak bu zincire binecek.

## 15.5 · FAZ 0 → FAZ 3 — inen maddeler *(§12 yalnız 4→8'i kapsıyordu)*

| Faz | Adım | İnen ana maddeler | Kapanış |
|---|---|---|---|
| **−2** | — | belge onarımı *(kod yok)* | ✅ |
| **−1** | — | `MIMARI.md` ön hazırlık · `⟳ YÜRÜRLÜKTE` indeksi · **13 tuzak KAPIYA çevrildi** | ✅ |
| **0** | 11 adım | `0.22` bloklayıcı hata · `0.2` planlayıcı makbuzu · `0.23` **ölü render dalı** · `0.1` yeniden ölçüm · `0.16` ölçüm bütçesi · `0.14` **beş entegrasyon kapısı** · `0.19` semantik payda · **`0.18` METRİK KAYDI = HAKEM** · `0.5` **çapa zinciri uyandı** · yetimler *(0.3·0.7-0.11)* · `0.12`·`0.13`·`0.6` · `0.10b` **görünen adlar** · `0.15` **CI kapıları** | ✅ **§C/8 hedefe ulaştı** |
| **1** | ~19 madde | `1.1` motor-RLS · `1.1b` **arka plan işi kimliksiz koşmaz** · `1.2`/`1.2b` CLS + `llm_guard.safe_call` · `1.3` **yetki granülerliği** · `1.3b` **`enforce_query` — beyan edilmiş ama BOŞ katman** · `1.3c` *`strict_sql_policy` güvenlik sınırı DEĞİLDİR* · `1.4` süreç-arası kilit · `1.5` sertifikasyon · `1.6` lineage · `1.7` tazelik · `1.8` audit · `1.9` numeric fidelity · `1.10`+`1.11` eskalasyon + kademeli düşüş · `1.12` **AI Act / NIST / ISO 42001** · `1.13` düşman denetim paneli | ✅ *(🔴 `motor_cls=on` **KİLİTLİ** — §13/1)* |
| **2** | 13 adım | `2.1a-d` **çekirdek katman + grain sözleşmesi** · `2.2b` metrik kaydı yüzeyi · `2.3` **departman = MERCEK** · `2.4` aynı-grain çifti · `2.5` **hedef kıyası** · `2.6` **mali takvim** *(sessiz-yanlış kapandı)* · `2.7` adlandırma sözleşmesi · **borç #11** grain-farkında geçiş | ✅ |
| **3** | 7 adım | `3.1` sahiplik turu *(🔴 **ÖLÇÜM geri aldırdı**)* · `3.1b` **pack ÖNERİR, tenant UYGULAR** · `3.2` R1 envanteri · `3.3` terfi kapanış oranı · `3.4` **Ossie ithali** · `3.5` yeni kaynaklar *(⊘ ölçülemedi)* · `3.6` **cold-start + görünmez kolon** | ✅ |

## 15.6 · Uç envanteri + adlar

**66 HTTP ucu · 16 router.** *(`grep -rhoE '@router\.(get|post|put|delete|patch)'`)*

> ⟳ **2026-08-08 · yeniden sayıldı: 75 uç** @`761928d` *(aynı komut)*. Fark **+9** ve ara
> fazın yüzeyini taşıyor. ⚠ **Yetim uç kapısı** *(`test_uc_yetim_degil`)* bu artışın
> **frontend tüketicisi olduğunu** iddia ediyor — ama 🔴 **`tsc` gecelik CI'da hiç
> koşmuyor**, yani arayüz tarafının derlendiği **doğrulanmıyor** *(§13.1 yeni borç)*.

| Router | Uç sayısı | Öne çıkan |
|---|---|---|
| `ask` | 12 | `/ask` · `/cube` · `/report` · `/ask/drill` · `/ask/contribution` · `/ask/jobs/*` |
| `dashboards` | 8 | `/dashboards/{did}/data` |
| `measures` | 7 | `/candidates/*` — terfi kuyruğu · **`/blast-radius`** |
| `connections` | 6 | `/test` · `/{cid}/confirm` · **`/{cid}/import-semantic`** *(Ossie)* |
| `schedules` · `contracts` · `metrics` · `tercihler` · `conversations` · `decisions` · `stats` · `query` · `audit_export` · `eylem` · `health` | 33 | `/contracts/{cid}/replay` · `/audit/export` · `/gecikme` |

**Konuşma türleri — bugün 5, v1 hedefi 7** *(`app/followup.py`)*:

```
TUR_NEDEN · TUR_NORMAL · TUR_NE_YAPMALI · TUR_ISARET · TUR_ANLAT
                     ┊
   v1'de +2:   tur_takip (5.1)  ·  tur_paylas (5.2)
   v3'te +1:   TUR_GOREV_OLUSTUR (II-F.6) — 🔴 motoru orada doğuyor
```

**Takip sınıfları — 3** *(`followup.py:60-62`)*: `SINIF_YAPISAL` *(sorguyu düzenle)* ·
`SINIF_KONUSMA` *(cevabın üstünde konuş)* · `SINIF_YENI` *(yeni konu)*

---

# 16. 🔴 v2'de NE EKLENECEK — bölüm bölüm delta

**v2 = `II-D` (analist) + `II-E` (karar) + `II-F`'nin dört maddesi.**
*Bu bölüm yeniden anlatmaz — yukarıdaki her §'a **ne eklenir** onu yazar.*

## 16.0 · v2'nin üç ön koşulu — hiçbiri atlanamaz

| # | Şart | Bugünkü durum |
|---|---|---|
| 1 | **v1 kapanmış** — §C'nin **16** ölçütü yeşil | 🔴 **4'ü `[ÖLÇÜLMEDİ]`** (§11.2) |
| 2 | **FAZ 8.1 koşulmuş** — Plan 3 §1.4: *"onsuz başlamaz"* | 🔴 **pencere açılmadı** |
| 3 | **§II-0'ın 9 maddesine KARAR BAĞLANMIŞ** | 🔴 **hiçbiri işaretli değil** |

> 🔴 **DÖNGÜ DÜZELTMESİ — v2 ASLA BAŞLAYAMAZDI.** Kapı önce *"11 madde **teyitli**"*
> istiyordu; ama `E1` düzeltmesi *"talep gözlenmezse madde **`[TEYİT ALINMADI]`** olarak
> **AÇIK KALIR**"* diyor. İkisi birlikte: **madde talep görmez → asla teyitli olmaz →
> şart asla sağlanmaz → v2 asla başlayamaz.** §C/9'un kilidiyle **aynı sınıf**.
>
> **KARAR:** kapı *"teyitli"* değil **"KARARI BAĞLANMIŞ"** ister. Üç durum, **ikisi geçerli**:
>
> | Durum | Sonuç |
> |---|---|
> | `[TEYİT ALINDI · <tarih>]` | madde **uygulanır** |
> | `[TEYİT ALINMADI — talep gözlenmedi · <tarih>]` | madde **uygulanmaz**, kayıt kalır |
> | *(işaretsiz)* | 🔴 pencere koşmadı → **kapı KAPALI** |
>
> **Kapıyı açan şey *"hepsi istendi"* değil, *"hepsine bakıldı"*.**
> ⚠ **Ters `KAT-3` düzeltmesi:** 11 maddenin **ikisi** (`6B.14`→II-H.1 · `6B.16`→II-H.2)
> **v3'e** aittir ve **v2'nin kapısında durmaz** → kapı **9 madde** sayar.

## 16.1 · § 2 · **Yedi katman** → v2 deltası

```
 6 · ARTEFAKT   + Karar Kaydı (16 alan) · Karne · CEO Günlüğü · Senaryo
 5 · ANLAMA     + LLM: seçenek METNİ · SWOT MADDE metni  🔴 SINIFI ASLA
 4 · DİYALOG    + karar derinlik merdiveni  hizli_3 | tam_9  (soruya bağlı)
 3 · YÜRÜTME    + ForecastContract · Senaryo overlay (DEĞİŞMEZ)
 2 · DİL        + Graf (SurucuDugumu · kenar: arithmetic | causal)
 1 · ANLAM      + ŞirketBaglami · SurecAdimi · SozlukTerimi · ŞirketProfili
 0 · GÜVENCE    + imzalayan_id NOT NULL & İNSAN · PolitikaKurali (kırmızı çizgi)
```

🔴 **Yeni katman EKLENMİYOR** — yedi katman **aynı kalıyor**, her birine içerik biniyor.

## 16.2 · § 4 · **Prompt akışı** → v2'de merdivene ne eklenir

**Merdiven basamakları DEĞİŞMEZ.** Eklenen şey `seal()`'ın **sonrası** ve chip'lerin
**hedefi**:

| Nerede | v2'de eklenir |
|---|---|
| **`seal()` çıkış kapısı** *(§4.3)* | 🔴 **`II-E`'nin ZORUNLULUĞU:** *"Karar Motoru kendi bounded-context'i olduğu için `seal()`'ı **atlaması en olası yer**"* → **her karar çıktısı `seal()`'dan geçer**. `tests/test_kapanis_zinciri.py` **genişletilir** |
| **`next_steps` chip'leri** | + *"bunu tahmin et"* · *"what-if kur"* · *"karara dönüştür"* |
| **Discovery dalı** | değişmez — ama `II-D.1`'in grafı `DrillDownPanel`'i **strangler fig** ile devralır *(bayrak `off` → bugünkü yol **birebir**)* |
| **Bağlam çözümü** *(§4.1)* | + `II-F.8` **bağlam enjeksiyonu ~800 token** *(öncelik: sektör > departman > kritik metrik)*. 🔴 **Çelişkide VERİ KAZANIR** — profil bir **yorumdur**, `route()`'un sayısı **gerçektir** |

## 16.3 · § 7 · **Bayrak envanteri** → v2'de eklenen 12 bayrak

| Bayrak | Madde | Ne açar | 🔴 `GERİ AL` yazılı mı? |
|---|---|---|---|
| `ui_nedensellik_grafi` | `II-D.1` | **TEK graf, ÜÇ tüketici** *(what-if · kök-neden · açıklanabilirlik)* | ✅ *(off → `DrillDownPanel` birebir)* |
| `ui_tahmin` | `II-D.2` | **ARALIK ZORUNLU** tahminleme | ❌ **EKSİK** |
| `ui_what_if` | `II-D.3` | Senaryo = **DEĞİŞMEZ overlay** | ❌ **EKSİK** |
| `ui_kohort` | `II-D.4` | Kohort ısı haritası — **5 zorunlu parametre** | ❌ **EKSİK** |
| `ui_karne_karti` · `ui_swot_karti` | `II-D.5` | Karne + SWOT *(kompozisyon, yeni hesap YOK)* | ❌ **EKSİK** |
| `ui_departman_podlari` | `II-D.9` | Departman podu + **sorumluluk sınırı** | — |
| `ui_ceo_gunlugu` | `II-D.11` | Raporun **TEMATİK** varyantı | ❌ **EKSİK** |
| `ui_karar_motoru` | `II-E.1-3` | Çerçeve · seçenek · **9 kriterlik havuz** | ❌ **EKSİK** |
| `ui_karar_kaydi` | `II-E.7` | `DecisionRecord` **16 alan** | ❌ **EKSİK** |
| `ui_is_baglami_sihirbazi` · `ui_is_baglami_kartlari` | `II-F.1` | İş bağlamı kütüğü | ❌ **EKSİK** |
| `ui_kurumsal_takvim` | `II-F.3` | Ay-sonu kapanış · sezon · bütçe dönemi | ❌ **EKSİK** |

> 🔴 **ŞABLON DENETİMİ — BÖLÜM II HİÇ TARANMAMIŞTI** *(ölçüldü @`8f87e40`)*:
> **18 bayraklı maddenin 17'sinde `GERİ AL` bloğu YOK.**
> Kök neden **tam olarak `KAT-5`**: denetim betiğinin deseni `^### ([0-9]+\.[0-9]+|AJ[0-9])`
> idi ve **`II-D.1` biçimini kapsamıyordu** → araç *"33/33 TAM"* raporladı.
> *Sayılan her küme, kapsamadığı her şeyi görünmez kılar.*
>
> **İki bağlayıcı karar:** ① kapı düzeltilir, **17 blok ŞİMDİ YAZILMAZ** *(uydurmak ölü
> doğuş olurdu)* · ② 🔴 **hiçbir Bölüm II maddesi, altı bloğu TAM olmadan SIRAYA ALINMAZ.**

## 16.4 · § 8 · **Manuel test** → v2'de elle bakılacak yeni şeyler

| Yetenek | 1 · Kazanç | 2 · **Kırmızı çizgi** | 3 · Gizli risk |
|---|---|---|---|
| **Tahmin** `II-D.2` | *"İleride ne olur?"* cevaplanır | 🔴 **ASLA tek sayıyla** — `alt·orta·ust` + `guven_notu` *(skaler DEĞİL)*. **Nominal "%95 güven aralığı" İDDİA EDİLMEZ** | **`AVG`/oran ölçüsünü** aggregate tahmin edip bileşene bölmek **matematiksel olarak yanlış** → `contribution.ayristirilabilir_mi` **birebir aynı fonksiyon** çağrılır |
| **What-if** `II-D.3` | Sürücü grafında override → aşağı akış | 🔴 **Overlay, ASLA mutasyon** · döngü **YAZMA anında** reddedilir | *"sürücü ekle / formül tanımla"* **yalnız insan formuna açık** — LLM önerisi buraya **asla yazmaz** |
| **Kohort** `II-D.4` | Isı haritası + olgunluk maskesi | 🔴 **`min_kohort_buyuklugu=30` altında üretilmez** · **boş hücre UYDURULMAZ** | **GENEL normalizasyon varsayılan** — Mixpanel'in *"her satır kendi içinde iyi görünür"* yanıltıcılığı **reddedilir**; ham yüzde **HER ZAMAN görünür** |
| **Karne + SWOT** `II-D.5` | 6 kritik metrik, **TEK BAN cümlesi** | 🔴 **LLM yalnız madde METNİNİ yazar, SINIFI değil** · SWOT maddesinin `contribution` bulgusuna **ZORUNLU FK'si** | Karne **kendi sorgusunu yazmaz**, kayıtlı araçları çağırır |
| **Kanıt matrisi** `II-E.4` | `VERİ ∣ VARSAYIM ∣ BİLİNMİYOR` | 🔴 **`BİLİNMİYOR` GİZLENEMEZ — boş hücre YOKTUR** | Bir kararın **ne kadarının veriye dayandığı** ilk kez sayılabilir |
| **Karar kaydı** `II-E.7` | 16 alan, append-only | 🔴 **`imzalayan_id` NOT NULL ve İNSAN** · `is_agent=False` doğrulaması · **otomatik uygulama YOK** | 🔴 **İKİ AYRI SKOR, ASLA TEK SAYIYA KARIŞMAZ:** Karar Kalitesi *(süreç, **en-zayıf-halka** — ortalama DEĞİL)* ⟂ Sonuç Skoru *(ufuk dolunca)*. Toplamak **öğrenmeyi imkânsız** kılar |
| **Kırmızı çizgi** `II-E.9` | Kod-seviyesi kısıt | 🔴 **Ajan kırmızı çizgiyi ÖNEREMEZ BİLE** | `Principal.is_agent` + `PolitikaKurali` |
| **İş bağlamı** `II-F.1` | Şirketi tanır | 🔴 ***"Bilmiyorum" üçüncü seçeneği ASLA varsayım üretmez*** → `belirsiz` + Bakım Ajanı | **Mekanizma iner, kimse doldurmaz** riski → *"SOR değil **TÜRET**"* |
| **Şirket profili** `II-F.8` | ~800 token bağlam enjeksiyonu | 🔴 **`otomatik_taslak` profil, kullanıcı ONAYLAMADAN LLM prompt'una ENJEKTE EDİLMEZ** | ADR-0018'in *"adaylar otomatik canlıya çıkmaz"* kuralının **hafıza eksenindeki** karşılığı |

## 16.5 · § 9 · **A/B** → v2'nin ölçüm kapıları

| Yetenek | Kapı | Eşik |
|---|---|---|
| Tahmin | **dört sınır-değer testi** | **<12 ay → tahmin YOK** · **MASE ≥ 1.0 → YAYIMLANMAZ** · 2-11 satır → `seasonal_naive` · Holt-Winters min `m+5` *(aylık **17 nokta**)* · **kısmi son dönem DIŞLANIR** |
| What-if | `test_senaryo.py` | graf versiyonu değişince senaryo **`yeniden_dogrulama_gerekli`**'ye düşer |
| Kohort | `test_kohort.py` | a11y: metin **~%40 doygunluk üstünde beyaza döner** · min opaklık **~%10** |
| Kanıt matrisi | `test_kanit_matrisi.py::test_bos_hucre_yok` | boş hücre **0** |
| Karar kaydı | `test_karar_kaydi.py` | iki skor **ayrı alanlarda** ve **birleştiren kod YOK** *(kaynak taraması)* |
| Kriterler | `test_karar_kriterleri.py` | 🔴 **seçenek üretildikten SONRA ağırlık değişimi REDDEDİLİR** · toplam **100** |
| Kırmızı çizgi | `test_kirmizi_cizgi.py` | `is_agent=True` ihlal eden seçeneği **üretemiyor** |
| Duyarlılık | — | kırılma noktası **İKİLİ ARAMA**: aralık `[-100%, +500%]` · tolerans **%0,5** · çözülemezse **dürüst red**. Kırılganlık: **<%5 kırılgan · %5-10 orta · >%10 sağlam** |

## 16.6 · § 14 · **Frontend** → v2'de panel tavanı

```
   v1 tavanı:  13 export          Bölüm II tavanı:  15  (PK-23)
                                                     ↑
   Yani II-D + II-E'nin TAMAMI  yalnız  +2 PANEL  ile sığmak zorunda.
```

**Bu yüzden hemen her v2 maddesi *"yeni ekran DEĞİL"* diye başlıyor:**

| Madde | Nereye biner |
|---|---|
| `II-D.1` graf | **ortak Şema/DAG bileşeni — TEK yapı, ÜÇ render modu** |
| `II-D.2` tahmin | `chart.ts`'in `referenceLine`/alan-doldurma'sı **zaten var** |
| `II-D.5` karne | **widget, yeni ekran DEĞİL** *(PK-13)* |
| `II-D.11` CEO günlüğü | 🔴 **yeni buton EKLEMEZ** *(PK-15)* — `report.compose`'un parametresi |
| `II-E.5` duyarlılık | **ayrı sayfa DEĞİL, katlanır panel** *(PK-12)* |
| `II-E.6` gradient eğrisi | **istemci tarafında** — yeni uç **YOK** *(KD-14)* |
| `II-D.4` kohort hücresi | **yeni drill modalı icat etmez** *(PK-11)* → `ContractDetailPanel` |
| `II-E.5` what-if paneli | `II-D.3`'ünkini **YENİDEN KULLANIR** |

**Tahminin görsel sözleşmesi** *(Plan 2 §9.2)*: aynı serinin **AÇIK TONU** *(kesikli çizgi
**DEĞİL** — Tableau'nun belgelenmiş kararı)* · bant kenarı **kademeli opaklık** ·
🔴 **gerçekleşmiş kısım DAHA belirgin, tahmin DAHA soluk** — *"güvene görsel ağırlık ver,
belirsizliğe değil"*.

## 16.7 · § 13 · **Borçlar** → v2'nin kendi yeni riski

| Risk | Kayıt |
|---|---|
| 🔴 **17 madde `GERİ AL`'sız** | `KURAL B`'nin **dışında** — *"geri alma yolu yazılmamış madde **geri alınamaz**"* |
| ⚠ `D5` kapısının **kendi şartnamesi kırık** | *"her `<FAZ>.<N>` atfı için bir başlık"* diyor ama **~20 madde birleşik başlıkta** yaşıyor → harfiyen koşulursa **~20 yanlış-pozitif** |
| 🔴 **SHAP KURULMAZ** | Bir kütüphanenin açıklamasını *"nedensellik"* diye sunmak, `hierarchies` kararının ihlali olurdu — **uydurulmuş nedensellik, güvenle yanlış bir yol üretir** |
| 🔴 **Prophet KULLANILMAZ** | §D.1 hükmü. Nixtla StatsForecast **~500× hızlı** `[DOĞRULANMADI]` |
| 🔴 **DMN bilinçle REDDEDİLDİ** | hit policy yalnız `II-H.2`'nin dar alanında ödünç alınır *(yazılmazsa 6 ay sonra yeniden tartışılır)* |
| ⚠ **Sistem seçenek İCAT ETMEZ** | 2-3 alternatif, geçmiş `DecisionRecord`'lardan **benzerlikle** örneklenir. Kaynak yazılmazsa **LLM'e kalır → B1 ihlali** |

---

# 17. 🔴 v3'te NE EKLENECEK — bölüm bölüm delta

**v3 = `II-F`'nin kalanı + `II-G` (ölçek/öğrenme) + `II-H` (dış bağımlılıklı spike'lar).**
Bittiğinde: **çekirdek ürün %100.**

## 17.1 · § 2 · **Yedi katman** → v3 deltası

```
 6 · ARTEFAKT   + Sabah brifingi · Terfi kuyruğu (4 kaynak TEK ekran) · Kredi paneli
 5 · ANLAMA     + Sistem copilot (NL → yapılandırılmış MUTASYON)  🔴 onay_akisi'nın 5. tüketicisi
 4 · DİYALOG    + 8. konuşma türü TUR_GOREV_OLUSTUR + TAAHHÜT YAKALAMA
 3 · YÜRÜTME    + çift önbellek (security_context_hash anahtarın parçası) · derleme_grubu
 2 · DİL        + PaketOverride · semantik model VERSİYONLAMA (3 okuma-anı durumu)
 1 · ANLAM      + HafizaKaydi (TEK tablo, 4 tip × 7 katman) · UrunKarti/BOM · Gorev
 0 · GÜVENCE    + Anayasal kalkan (Z3, build-time) · Departman hakemi (CP-SAT)
```

## 17.2 · § 4 · **Prompt akışı** → v3'te ne değişir

| Nerede | v3'te eklenir |
|---|---|
| **Bağlam çözümü** *(§4.1)* | + **hafıza getirme** — 🔴 **dört ayrı `getirme_stratejisi`**: `semantik`→ad-eşleşmesi · `epizodik`→zaman-aralığı · `prosedürel`→direkt-okuma · `tercih`→benzerlik |
| **🔴 DEĞİŞMEZ** | ***hafıza ölçü/cube seçimine ASLA karışmaz.*** Bu kural **zaten yazılı**: `SunumTercihi`'nin *"tercih **ÖLÇÜ/CUBE SEÇİMİNE KARIŞMAZ**"* + *"**SESSİZ** uygulanmaz"* daraltması **`II-F.9`'un tamamına** uygulanır |
| **Öncelik çözücü** | 🔴 **`coz_oncelik()`** — `tercih` → **KİŞİ** kazanır · `tanım` → **ŞİRKET** kazanır · `kural` → **POLİTİKA** kazanır. Yani *"net satış"* tanımını **kimse kişisel tanımla EZEMEZ**. ⚠ *Sürüm 1 "en spesifik kazanır" diyordu ve **kuralı tersine çeviriyordu**.* Çelişki **sessizce çözülmez** — loglanır ve **UI'a taşınır** |
| **Merdiven** | değişmez — ama **`0 kredi`** kuralı buraya bağlanır: **altın yol + önbellek = 0 kredi** |
| **Konuşma türü** | + **8.'si**: `TUR_GOREV_OLUSTUR` + **taahhüt yakalama** *("halledeceğim", "yarın gönderirim")*. 🔴 **Kullanıcı onayı olmadan görev ASLA otomatik oluşmaz** |

## 17.3 · § 7 · **Bayraklar** → v3'te eklenen 8 bayrak

| Bayrak | Madde | Ne açar |
|---|---|---|
| `tur_gorev` | `II-F.6` | **8. konuşma türü** + `Gorev` motoru |
| `ui_sabah_brifingi` | `II-F.7` | **5 slot, 30 saniyede okunur** — Landing'in VARYANTI *(PK-14)* |
| `ui_hakkimda_bilinenler` | `II-F.12` | Kişisel hafıza şeffaflığı + **gerçek silme** + export |
| `sektor_paketi` | `II-G.1` | **Looker Blocks deseni** *(Fabric "as-is" DEĞİL)* |
| `ui_terfi_kuyrugu` | `II-G.5` | **TEK motor, DÖRT kaynak** — `ReviewPanel`'in genellemesi |
| `ui_kredi_paneli` | `II-G.6` | `KrediHareketi` + isabet/tasarruf paneli |
| `ui_departman_hakemi` | `II-H.1` | **OR-Tools CP-SAT** — nicel çatışma **deterministik** çözülür |
| `ui_sistem_copilot` | `II-H.3` | Sohbetten ayar değişikliği **önerisi** |

*(`II-H.2` anayasal kalkanın **ayrı UI'ı YOKTUR** — KD-18.)*

## 17.4 · § 8 · **Manuel test** → v3'te elle bakılacaklar

| Yetenek | 1 · Kazanç | 2 · **Kırmızı çizgi** | 3 · Gizli risk |
|---|---|---|---|
| **Hafıza** `II-F.9` | Sistem şirketi **hatırlar** | 🔴 **hafıza ölçü/cube seçimine ASLA karışmaz** · **retrieval EKLENMEZ** *(ölçülen bant **+14/−16**: belleği kur, ama **BASİT** kur)* | 🔴 **P0 — arka kapıdan geri gelen kapsam:** hafıza kaynaklı **yalakalık başarısızlığı çoğu modelde %90'ın üstünde**; **uydurma hafıza yerleştirme %99,8'e kadar** başarılı ölçüldü → **üç zorunlu alan**: `kaynak_ifade` · `son_dogrulama` · `celiski_bayragi`. Çelişki **sessizce çözülmemeli, GÖSTERİLMELİ** |
| **Seçici yazma** `II-F.10` | Hafıza **kirlenmez** | 🔴 **Bir LLM çıktısı DOĞRUDAN hafızaya YAZAMAZ** — `sinonim_onerici`'nin `approved=False` **SABİT** *(parametre değil!)* deseni | **Altı kriter**: tekrarlayan *(≥2)* · doğrulanmış · kapsamı belirli · **PII içermiyor** *(yazma öncesi `pii.mask_text`)* · çelişki üretmiyor · kaynağı izlenebilir |
| **Unutma** `II-F.11` | Çürüme + arşiv | 🔴 **ASLA hard-delete** *(ADR-0019)* — **TEK istisna: KVKK, kullanıcının kendi kişisel hafızası** | 🔴 **Silinen kayıt SONRAKİ cevapta kullanılmıyor** — **canlı doğrulanır** |
| **Görev motoru** `II-F.6` | Bulgu → görev | 🔴 **Kökensiz görev YARATILAMAZ** — `kaynak_tip` + `kaynak_id` **ZORUNLU FK** | Aksi hâlde görev listesi kanıt zincirinden kopmuş bir **yapılacaklar uygulamasına** döner |
| **BOM / ürün kartı** `II-F.2` | Maliyet/marj/karbon **AYNI ağacı okur** | 🔴 **Derinlik sınırı ZORUNLU** | ⚠ **Kendine-referanslı ilişki + calc kolon → Rust'ta PANIC** *(`lineage.rs:146` `.unwrap()`)* ve **`except Exception` YAKALAMAZ** *(`PanicException` MRO'su)*. **Derinlik sınırı bir tercih değil, ÇÖKME KORUMASI** |
| **Terfi motoru** `II-G.5` | Dört kaynak tek kuyruk | 🔴 **`reddedildi` ≠ `ertelendi`/`deprecated`** — ikisini tek *"reddet"*e sıkıştırmak *"iyi ama zamanı değil"* adayları *"kalıcı olarak kötü"* diye kaydeder ve **kalibrasyonu bozar** | 🔴 **Karar yorgunluğu:** **50+ inceleme** `[DOĞRULANMADI]` → kuyruk **önceliklendirilir** + **toplu inceleme**. Uzun liste onaylayanı *"hepsini kabul et"*e iter |
| **Kredi** `II-G.6` | Maliyet görünür | 🔴 **Başarısız işlemde kredi YAKILMAZ** · **altın yol + önbellek = 0 kredi** | ⚠ *"önbellek = 0 kredi"* **bir önbelleğin varlığını gerektirir** — MIMARI §5'in *"sonuç cache'i bilinçle KURULMADI"* kararı **FAZ 8.1 telemetrisiyle** yeniden açılır |
| **Departman hakemi** `II-H.1` | Nicel çatışma **deterministik** | 🔴 **LLM DEĞİL** — çözücü karar verir, LLM **yalnız gerekçe metnini** yazar | **Rozet:** *"hesaplanmış uzlaşma"* ↔ *"yorumlanmış öneri"* ayrımı **kullanıcıya gösterilir**. Gizlenmez, **soluk gösterilir** *(PK-6)* — ve *"soluk ama tıklanabilir"* ile *"devre dışı"* **AYNI token'ı paylaşmaz** *(A11Y-9)* |
| **Sistem copilot** `II-H.3` | Sohbetten ayar | 🔴 **`/settings` ekranlarının YERİNE GEÇMEZ, ÜSTÜNE BİNER** *(PK-18)* | Hiçbir mutasyon **onaysız** uygulanamaz; her onay **ayrı audit satırı** |

## 17.5 · § 9 · **A/B** → v3'ün ölçüm kapıları

| Yetenek | Kapı | Eşik |
|---|---|---|
| Hafıza önceliği | `test_hafiza_oncelik.py` | `coz_oncelik()` üç ekseni **karıştırmıyor** |
| Görev kökeni | `test_gorev_kokeni.py` | kökensiz görev **yaratılamıyor** |
| BOM | `test_bom_derinlik.py` | sınır aşımında **dürüst red**, **motor ÇAĞRILMIYOR** |
| Sektör paketi | — | gölgeleme **gerekçesiz yapılamıyor** *(`sebep` ZORUNLU)* + **sapma metriği**: *"kaç şirket-katmanı satırı sektör-katmanını gölgeliyor"* → **pack drift**, ISO 42001 girdisi |
| **Terfi regresyon kapısı** | `eval/run.py` | 🔴 **Aday terfi etmeden önce golden-set YENİDEN koşulur; önceden-doğru bir cevap artık farklı çıkıyorsa terfi ENGELLENİR.** ← *"terfi motorunun kendi kalitesini bozması"* riskine karşı **tek savunma** *(kanıt: `fire` ↔ `ciro`, kosinüs **0,92**)* |
| VQR yönetişimi | — | `MetricDefinition` değişince bağlı VQR **otomatik `needs_reverification`** |
| Kredi | `test_kredi.py` | `source=cube` cevap **0 kredi** · iki farklı `security_context` → **farklı `cache_key`** |
| Departman hakemi | determinizm testi | aynı girdi → **aynı çözüm** |
| Anayasal kalkan | **build-time CI kapısı** | 🔴 çalışma zamanında Z3 çağrısı **YOK** *(gecikme eklemez)* |
| Çok-tenant | — | tenant modeli **10-40 MB** · **500+ tenant tek süreçte** `[DOĞRULANMADI]` · ön koşul **v1 FAZ 1.4** |

## 17.6 · § 12 · **Kalan yol** → v3'ün iki spike'ı ZAMAN-KUTULU

```
🔴 II-H.1 ve II-H.2  MADDE DEĞİL,  ZAMAN-KUTULU SPIKE'tır.

   ┌────────────────────────────────────────────────────┐
   │  2 hafta  ·  BİR gerçek çatışma vakası             │
   │  çözemezse  →  KAPATILIR                            │
   │  kapanırsa  →  EK J'ye GEREKÇESİYLE taşınır        │
   │                (sessizce ertelenmez)                │
   └────────────────────────────────────────────────────┘

   İkisi de [TEYİT BEKLİYOR] · P2 · bir BI ürününde DOĞRULANMAMIŞ.
   Öldürme ölçütü YAZIYA GEÇER — EK J disiplininin İLERİYE DÖNÜK hâli.
```

## 17.7 · § 15.4 · **Tenant açılışı** → v3'te *"SOR"* değil *"TÜRET"*

🔴 **Toplama stratejisi değişti.** `II-F.1`'in bugünkü yolu bir **sihirbaz** — yani
**müşteriye form doldurtmak**. Ölçülen darboğaz: *"mekanizma üretiliyor, **sözlük
üretilmiyor**."* Katalogda olan iş bağlamında da olur: **mekanizma iner, kimse doldurmaz.**

| Bağlam | Nereden **TÜRETİLİR** | Altyapı |
|---|---|---|
| Mali takvim · dönem yapısı | ERP'nin **kendi takvim tablosu** | `db_introspect` ✅ · **v1 2.6** |
| Ürün/müşteri/tedarikçi hiyerarşisi | ERP **kart tabloları** | `db_introspect` ✅ · `II-F.2` |
| Maliyet merkezi · organizasyon | **muhasebe hesap planı** | `mizan` cube'u ✅ |
| Hangi metrik **kimin işi** | **query-log madenciliği** | `II-G.3` — 🔴 **ön koşul FAZ 8.1** *(madencilik yapılacak log YOK)* |
| İş terimleri | mevcut **raporlar · prosedür dokümanları** | `sinonim_onerici` ✅ *(insan onayı)* |

> ⚠ **Sihirbaz KALDIRILMAZ:** türetilen her şey **taslak** gelir (`onay_durumu`), insan
> **onaylar**. ***Türetme, sormanın yerine geçmez — sorulacak soruyu 20'den 3'e indirir.***
>
> **Query-log madenciliği — 7 adımlı boru hattı:** ters-indeks → literal-normalizasyon →
> sıralama → yenilik kontrolü → doğrulama → 🔴 **LLM YALNIZ İSİMLENDİRME** →
> **zorunlu insan onayı**.

## 17.8 · § 14 · **Frontend** → v3'te panel tavanı ve versiyonlama

**Semantik model versiyonlama `II-G.2` — okuma anında hesaplanan ÜÇ durum:**

```
   kaydedilmiş her cevap / karar / tahmin / senaryo için:

   ┌─────────────────────┬──────────────────────┬──────────────────────┐
   │   reproducible      │  numbers_may_differ  │  definition_removed  │
   │   aynen üretilir    │  sayı DEĞİŞMİŞ OLABİLİR │ tanım KALDIRILMIŞ  │
   └─────────────────────┴──────────────────────┴──────────────────────┘

🔴 HÜKÜM: Cube'ün `schemaVersion`'ı bir CACHE ANAHTARIDIR,
          semantik sözleşme versiyonu DEĞİL.  (yanlış model almayı önler)
```

**Terfi kuyruğu görsel kuralı:** 🔴 **kategori rengi ≠ güven rengi** — dört kaynağın her
biri **sabit renk**; etki/güven **yalnız opaklık** ekseninde *(PK-13)*.

---

# 18. Tek bakışta: v1 → v2 → v3 birikimi

> ⟳ **2026-08-08 · ARADA BİR DURAK VAR ve bu belge onu bilmiyordu:**
>
> ```
>    v1  ──────────►  🍽 GARSON ARA FAZI  ──────────►  v2
>  MUTFAK              (G0…G8 · 113 adım)             ANALİST
>  kuruldu             insani katman                  + KARAR
>
>    "sayı doğru,        "…ve anlaşılır"              "ne olacak,
>     mühürlü,                                         ne yapmalıyım"
>     RLS'li, kanıtlı"
> ```
>
> **Ara faz v2'nin bir parçası DEĞİL, ön koşuludur:** *"Mutfak dünyanın en katı ucunda
> kuruldu… eksik olan, o sesin **anlaşılır** olması."* Ve hiçbir maddesi **sayıya
> dokunmadı** — bu yüzden §16–17'nin v2/v3 deltaları **aynen geçerlidir**.

```mermaid
flowchart LR
    subgraph V1["v1 — 'Konuşan, kanıtlayan, güvenli şirket beyni'"]
        A1["7 katman ADLANDIRILDI"]
        A2["8 basamaklı merdiven"]
        A3["25 bayrak · 66 uç · 13 panel"]
        A4["§C'nin 16 ölçütü"]
    end
    subgraph V2["v2 — 'Analist ve karar ortağı'"]
        B1["II-D · analist<br/>graf · tahmin · what-if · kohort · karne"]
        B2["II-E · karar<br/>kanıt matrisi · karar kaydı · kırmızı çizgi"]
        B3["II-F ×4 · iş bağlamı<br/>kütük · takvim · sözlük · profil"]
    end
    subgraph V3["v3 — 'Şirketi TANIYAN, kendini GELİŞTİREN platform'"]
        C1["II-F kalanı<br/>hafıza · unutma · görev · brifing · BOM"]
        C2["II-G · ölçek<br/>sektör paketi · versiyonlama · terfi · kredi"]
        C3["II-H · spike<br/>CP-SAT · Z3 · copilot"]
    end
    V1 -->|"16 ölçüt yeşil<br/>+ FAZ 8.1 koştu<br/>+ 9 maddeye KARAR bağlandı"| V2
    V2 -->|"II-0'ın kalan 2 maddesi<br/>kendi sürümünde karara bağlanır"| V3
    V3 --> D(["**ÇEKİRDEK ÜRÜN %100**"])

    style V1 fill:#1b5e20,color:#fff
    style V2 fill:#0d3b66,color:#fff
    style V3 fill:#4a148c,color:#fff
    style D fill:#4a3f00,color:#fff
```

| | v1 | v2 | v3 |
|---|---|---|---|
| **Cevapladığı soru** | *"Ne oldu? Neden?"* | *"Ne olacak? Ne yapmalıyım?"* | *"Şirketimi biliyor mu? Kendini geliştiriyor mu?"* |
| **Katman** | 7 katman **adlandırıldı** | aynı 7 katmana **içerik biner** | aynı 7 katmana **hafıza + ölçek biner** |
| **Yeni bayrak** | 25 *(21 YAML + 4 kayıt-dışı)* | **+12** | **+8** |
| **Panel tavanı** | **13 export** | **15** *(PK-23)* | **15** — değişmez |
| **Yeni merdiven basamağı** | 8 | 🔴 **0** | 🔴 **0** |
| **En büyük risk** | *"testler METNİ ölçtü"* | 🔴 **17 madde `GERİ AL`'sız** | 🔴 **hafıza kaynaklı yalakalık %90+ · zehirleme %99,8** |

---

## 🔴 KAPANIŞ — belgenin kendi sınırı

Buradaki **her** sayı bir koşumdan alındı ve **o koşumun damgasını** taşır. Bayatladıklarında
**bu belge düzeltilmez — araç yeniden koşulur.**

Ve bu belgenin **kendisi bir kapı değildir**: kimse onu koşmaz, kırmızı vermez, kimseyi
durdurmaz. Bir şemanın doğru görünmesi, kodun öyle çalıştığı anlamına gelmez.

> **Bu belgeye dayanarak bir karar verme.**
> Kodu oku, aleti koş, sayıyı gör.

---

## 🍽 ⟳ KAPANIŞ NOTU — analojinin kendi sınırı *(2026-08-08)*

Bu turda belgeye giren **tek yeni fikir**, sistemin **bir restoran gibi okunabileceğidir**:
garson konuşur, aşçı pişirir, kapılar arada durur, ve **hiçbir kapı gevşemez**.

Analoji iki iş yapıyor ve **ikisi de meşru**:

1. **Öğretiyor.** *"Garson tencereye karışamaz"* cümlesi, `parse_cube_query`'nin katı beyaz
   listesini bir mimarlık tartışması olmadan anlatır.
2. **Ayrım testi veriyor.** *"Bu modül dil mi okuyor, veri mi?"* — ve **ikisi de** ise
   **kapı olmak zorundadır**. Bu, `KAT-1`'in gündelik dile çevrilmiş hâlidir.

🔴 **Ama üçüncü bir iş YAPMAZ: karar vermez.** Bir benzetme kırmızı veremez, koşulamaz,
bir bayrağı açamaz. §0.9 bunun için yazıldı — **analojinin kırıldığı dört yer** orada,
ve beşincisi şudur:

> ***Restoran resmi anlatmakta iyi, ölçmekte kötüdür.***
> Ve bu belgenin en dürüst cümlesi, ara fazın kendi öz-eleştirisinden ödünç alınmıştır:
> **bir mimaride varsayılan olan yol, en az ölçülen yol olmamalıdır** — yoksa ölçüm
> sistemi, sistemin kendisinden farklı bir şeye inanmaya başlar.
>
> Bugün **varsayılan yol garsondur** *(LLM)*, ve **en az ölçülen yol da odur**.
> Bu haritanın işaret ettiği bir sonraki iş, yeni bir yetenek değil: **o ölçüm**.
