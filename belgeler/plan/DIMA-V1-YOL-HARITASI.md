# DİMA — GELİŞTİRME YOL HARİTASI (**v1 → v3**)

> 🔴 **SÜRÜM 6 — YENİ BÖLÜM: §G · AJAN KATMANI.** Kullanıcı kararı: *"Tek bir şey
> seçmeyeceğiz — **ikisini de geliştirip kıyaslayıp test edeceğiz**; geliştirme maliyetini
> de kabul ediyoruz"* + *"**plan çok iyi, bunu korumak istiyorum**."* §G o iki cümlenin
> birleşimidir: **hiçbir madde silinmez**, ikinci bir **yürütücü** A'nın **üstüne** oturur,
> ve karar **§G.6'nın kıyas sözleşmesiyle ölçülür**.
> **Kilidi açan tek karar:** bugün *"sayıyı küp koyar"* değişmezi **iki işi birden** yapıyor
> — sayıyı koruyor **ve** LLM'in konuşmasını yasaklıyor. **Ölçülmüş olan yalnız birincisi.**
> → değişmez **ikiye ayrılır**: *sayıyı küp koyar* (kurulu, dokunulmaz) ⊕ *LLM'in her
> **iddiası** şemaya karşı doğrulanır* (`app/iddia.py` — **eksik olan tek şey**).
> Ve iki ölçülmüş kusur §G'yi zorunlu kıldı: **`compare` Intent-JSON şemasında HİÇ YOK**
> (→ her yeni anlam **7 dosyada kod**) · **cevapsız bir dal cevaplı bir yolu kesiyor**
> (→ *«degisti» yerine «egitim» mi demek istedin?*, MIMARI §5'in **18. yasağı**).
>
> 🔴 **VE SÜRÜM 6'NIN İKİNCİ TURU SIRAYI DEĞİŞTİRDİ — atlanmış bir KATMAN bulundu.**
> Kullanıcı: *"**LLM olmadan bile mükemmel konuşan** Türkçe botlar var, onlar kadar bile
> konuşamıyoruz."* **Haklı, ve sebebi LLM değil: DİYALOG YÖNETİCİSİ yok** — slot durumu ·
> devam · onarım · temellendirme · inisiyatif. Beşi de **deterministik**, hiçbiri LLM
> istemiyor. Ve 🔴 **`0.5b` bu katmanı sıfırdan İCAT EDİYORDU** (çözülmüş bir problem:
> slot-filling) — madde doğru, ama **bir katmanın parçası olduğu yazılı olmadığı için**
> kardeşleri hiç yazılmamıştı. → **`AJ0b` §G'nin İLK maddesi oldu**: güven modeline hiç
> dokunmaz, şikâyetin büyük kısmını çözer, **ve AJ3'ün kıyas TABANINI kurar**.
>
> **Kuzey yıldızı (§G.0b) belgeye girdi** — kullanıcının kendi cümlesi bir **test**e
> çevrildi: *"son 6 aylık ciro ve her ürün kalemiyle mukayesesi… bir rapor yaz."*
> Dört parçaya ayrıldı ve her parçanın **bugünkü durumu ölçüldü**: ayrıştırma
> (`planner.sec()` **yazılmış, hiç açılmamış**) · dil (🔴 `compare` **ve** `blend` ifade
> edilemez) · rapor (**büyük ölçüde var**) · diyalog (**yok**).
>
> **Sürüm 5 — YEDİ bağımsız denetimden geçti.** Üçü iç (kapsama · uygulanabilirlik · olgusal
> doğruluk), **ikisi DIŞ rapor** (`u-anda-bir-plan-tingly-fox.md` → **EK L** ·
> `SOHBET-DENEYIMI-RAPORU_2026-08-03.md` → **EK M**), **ikisi de belgenin KENDİSİNE yapılan
> bütünlük denetimi** → **EK N**. Her raporun her kritik iddiası **kodla sınandı**;
> kapatılamayanlar **`[DOĞRULANMADI]`** ile işaretlidir.
>
> 🔴 **Sürüm 5 bir içerik turu değil, bir BÜTÜNLÜK turudur** — ve en sert bulgusu şuydu:
> **v1 kapısı bir v3 maddesine bağlıydı** (§C/9 sekiz konuşma türü isterken 8.'si II-F'de) →
> **v1 asla kapanamazdı**. Ayrıca **§A.2'nin kendi kuralı yine ölü beyandı**: 34 ⭐ maddenin
> yalnız **9'u** altı bloğu taşıyordu (sürüm 1'in *"113'ün 111'i"* kusurunun tekrarı).
> **Şimdi 34/34 tam ve Kademe 2'de KAPI eksiği 0.**
>
> 🔴 **Sürüm 3'ün getirdiği en sert üç şey:** (1) **`agent_plan_secimi` bugün açılırsa
> çöküyor** → **0.22** · (2) **kalibre edilmemiş güven yüzdeyle basılıyor** — MIMARI §9'un
> kendi yasağının üründe canlı ihlali → **7.8/K2 (madalya KALDIRILIR)** · (3) **ölçülmüş en
> büyük kazanç (turların ~%18'i) 40 madde geride duruyordu** → **0.18**.
>
> 🔴 **Sürüm 4'ün getirdiği en sert üç şey:** (1) **ödenmiş üç özellik ekranda YOK** —
> `contribution`+`prescription`+`next_steps` hesaplanıyor, `ReportPanel` onları render eden
> dala **hiç göndermiyor** → **0.23** · (2) **sistem sorduğunu hatırlamıyor** — netleştirme
> dallarının **10'u** cevabı bağlamıyor; kullanıcı **tıklarsa çalışır, yazarsa çalışmaz** →
> **0.5b** · (3) **`t2_anlatici` bu şikâyeti YAPISAL OLARAK çözemez** — iki kapı onu yalnız
> zaten cevaplanmış %69,8'e hapsediyor → çerçeve **§F.2**'de düzeltildi.
> ⚠ **Ve bir uyarı:** iki bağımsız kapı (**K2** ve **deneyim süiti**) **aynı körlüğü**
> paylaşıyor — *"alan var mı"* soruyorlar, *"ulaşılabilir mi"* değil. **Kapı yeşil diye iş
> bitmiş değildir.**
>
> **Bu belge üç planın yerine geçer.** `dima-backend-ozellik-implementasyon-plani.md`
> (**Plan 3**) ve `dima-ui-ux-urun-deneyimi-mimarisi.md` (**Plan 2**) eleştirel olarak
> absorbe edildi; eşleme kanıtı **EK A/EK B**, sayılmamış kural kümeleri **EK H/I/J**.
>
> **Kanıt belgesi ayrıdır ve silinmez:** `~/.claude/plans/polymorphic-tumbling-riddle.md`
> (bundan sonra **[KANIT]**). Ölçümler orada; bu belge **ne yapılacağını** söyler.
>
> **Mimari otorite `backend/MIMARI.md`'dir** — §A.1'in otorite sırası ve FAZ −1'in
> `⟳ YÜRÜRLÜKTE` mekanizması dışında.

---

# §A. BU BELGE

## §A.1 · Ne, otorite sırası, dosya yolları

Dima'yı **v1'den v3'e** (çekirdek ürünün tamamı) taşıyan uçtan uca yol haritası.

**Otorite sırası (çelişkide):**
1. `backend/MIMARI.md` — mimari değişmezler (§4) ve yasaklar (§5)
2. **bu belge** — ne, hangi sırayla, hangi kapıyla
3. `[KANIT]` — ölçümler ve gerekçeler
4. `Dima-0-100-Gorev-Takip-Dosyasi (2).md` — **ürün şartnamesi, mimari otorite DEĞİL**

> **İstisna:** FAZ −1'in `⟳ YÜRÜRLÜKTE` bloğunda listelenen `MIMARI.md` başlıklarında
> **bu belge kazanır** — ve işaret, ilgili faz indiğinde **silinip ölçümlü bir `✅` kaydına
> dönüşür**.

**Dosya yolları** (denetim bulgusu: belge her sayfada atıf veriyordu, yol vermiyordu):

| Kısaltma | Yol |
|---|---|
| **[KANIT]** | `~/.claude/plans/polymorphic-tumbling-riddle.md` |
| **Plan 3** | `~/.claude/plans/`**`arsiv/`**`dima-backend-ozellik-implementasyon-plani.md` ⚠ *(sürüm 3 kök dizini gösteriyordu — **kırık atıf**, absorbe edilince taşınmıştı; `arsiv/README.md` gerekçeyi taşıyor)* |
| **Plan 2** | `~/.claude/plans/`**`arsiv/`**`dima-ui-ux-urun-deneyimi-mimarisi.md` ⚠ *(aynı düzeltme)* |
| **Yürüyen plan** | `~/.claude/plans/calm-foraging-deer.md` |
| **Dış denetim 1** | `~/.claude/plans/u-anda-bir-plan-tingly-fox.md` → **EK L** |
| **Dış denetim 2** | `~/.claude/plans/SOHBET-DENEYIMI-RAPORU_2026-08-03.md` → **EK M** |
| **Şartname** | `<repo>/Dima-0-100-Gorev-Takip-Dosyasi (2).md` |
| **MIMARI** | `<repo>/backend/MIMARI.md` |
| **repo** | `/home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic` |

## §A.2 · Madde biçimi — **İKİ KADEMELİ** *(denetim düzeltmesi)*

> ⚠ **Sürüm 1'in ölçülmüş kusuru:** 113 maddenin **111'i** ilan edilen altı bloğu
> taşımıyordu — yani kuralın kendisi **ölü bir beyandı** ve bu, tam olarak bu deponun
> avladığı *"beyan var, kod onu tanımıyor"* sınıfıydı. **Şablon iki kademeye ayrıldı**;
> gevşetme değil, **uygulanabilir hâle getirme.**

**Kademe 1 — ⭐ maddeler (yüksek etki / yüksek risk): ALTI BLOK ZORUNLU**

```
### <FAZ.N> · ⭐ <ad>                        [bayrak: <ad>]  ya da  [bayraksız: <gerekçe>]
NEDEN    kanıt: [KANIT §x] · <dosya:satır@sha> · <ölçüm>.   Kanıt yoksa: [DOĞRULANMADI]
NE       backend: … │ sözleşme: <alan/uç + tip> │ frontend: <bileşen + etkileşim>
NASIL    hangi MEVCUT fonksiyon/modül yeniden kullanılır; yeni kod gerekçelenir
KAPI     <test dosyası>::<test adı> · eşik: <sayı> · gerileme: <nl_corpus|eval>
SONUÇ    <ölçülebilir sayı/davranış değişimi>
GERİ AL  bayrak kapalıyken davranış BİREBİR bugünkü · geri alma testle kilitli
```

**Kademe 2 — diğer maddeler: `NEDEN` + `NE` + `KAPI` ZORUNLU** (`NASIL`/`SONUÇ`/`GERİ AL`
opsiyonel; bayrak taşıyorsa `GERİ AL` da zorunlu).

**Üç bağlayıcı kural** *(sürüm 1'de `R1` adı `cube_router`'ın red koduyla çakışıyordu →
`D1/D2/D3` olarak yeniden adlandırıldı)*:

| # | Kural | Gerekçe |
|---|---|---|
| **D1** | **`NE` üç parçalıdır.** Frontend'i olmayan madde yalnız **`api-only`** beyanıyla geçer — gerekçesiyle ve `tests/test_uc_yetim_degil.py::API_ONLY`'ye yazılarak | MIMARI §14.1 · [KANIT §14] |
| **D2** | **Sayı, HEAD damgası ve yeniden ölçüm komutu olmadan yazılmaz.** Biçim: `<sayı> @<sha> · <komut>`. **Canlı büyüyen sayılar** (telemetri satır sayısı gibi) sabit yazılmaz, **komutla** verilir | Bu belge iki oturumda **üç kez** bayatladı |
| **D3** | **Kanıtsız madde `[DOĞRULANMADI]` işaretlenir**, gizlenmez | [KANIT §12.1] |
| **D4** | **Her yeni kalıcı artefakt bir MAKBUZA bağlanır** (Plan 3 B6) — cevap · tahmin · senaryo · kohort matrisi · karne · terfi kararı · zamanlanmış gönderim | MIMARI §4-4 |
| 🔴 **D5** | **TAŞINAN MADDE ESKİ YERİNDE HER ZAMAN BİR KÜTÜK BIRAKIR.** Biçim: `### <eski no> → TAŞINDI: <yeni no>  *(yönlendirme kütüğü — madde burada YOK)*` + tek satır gerekçe. **İstisnasız** — "atıf kalmadı" gerekçesi kabul edilmez, çünkü atıf sayısı **taşıma anında** sayılmaz | Ölçüldü: üç taşımanın **üçü de farklı** işlendi — `4.1` kütük bıraktı ✅ · `2.2` **hiç bırakmadı** (22 atıf boşluğa düşüyordu) · `8.2` **hem taşındı hem tam metniyle kaldı** (iki yer *"taşındı"* derken üçüncüsü maddeyi barındırıyordu). **Vakaya göre karar verilirse üçte biri kaçıyor** |

> **D5'in kapısı:** `tests/test_yol_haritasi_butunlugu.py` (FAZ 0.14 ile birlikte yazılır) —
> belgede geçen her `<FAZ>.<N>` atfı için **ya bir `### <FAZ>.<N> ·` başlığı ya bir
> `### <FAZ>.<N> → TAŞINDI` kütüğü** bulunmalı. Bu, belgenin kendi *"yetim atıf"* kapısıdır
> ve K1/K2'nin belge-içi karşılığıdır.
> ⚠ **Aynı kapı `PK-n` / `KD-n` / `A11Y-n` kod ailelerini de tarar** — sürüm 4'te `PK-24`
> atıf alıyordu ama **tanımlı değildi** (EK H `PK-23`'te bitiyor).

## §A.5 · 🔴 **DÖRT MİMARİ KURAL (`KAT-1…KAT-4`)** — kusurların SINIFINI kapatır

> **Kök teşhis (bu oturumların toplamı):** bulunan **her** kusur aynı biçimde çıktı —
> ***bir mekanizma İKİ İŞ yapıyor.*** Tek tek yamalandığında bitmiyor, çünkü yama örneği
> kapatıyor, **sınıfı** değil.

| Mekanizma | Yaptığı **iki** iş | Ölçülen sonuç |
|---|---|---|
| *"sayıyı küp koyar"* | sayıyı **korur** + LLM'in konuşmasını **yasaklar** | konuşma katmanı **hiç doğmadı** → §G.1 |
| `compare` | kıyas **ekseni** + **kapalı değer kümesi** | her yeni anlam = **7 dosyada kod** → AJ2 |
| `note` | dürüst ret · netleştirme · kırpma uyarısı · upload bildirimi | **dördü ayrılamıyor** → 5.17 |
| `R1…R10` | *"ayrıştıramadım"* + *"ifade edemiyorum"* | **eksik yetenek sayılamıyor** → `R11` |
| yazım-benzerliği chip'i | **öneri** + **merdiveni bitirme yetkisi** | Discovery'yi **kesiyor** → AJ0 |
| `ReportPanel` kapısı | *"raporlanabilir mi"* + *"render edilebilir mi"* | üç özellik **ekranda yok** → 0.23 |

**Temel kural tek cümle:** ***her katman TEK iş yapar, TEK kapısı olur, ve altındakine
yalnız o kapıdan dokunur.***

| # | Kural | Nereden geldi |
|---|---|---|
| **`KAT-1`** | **Bir mekanizma iki iş yapmaz.** İki iş yapıyorsa **ikiye ayrılır** ve **her birinin kendi kapısı** olur | Yukarıdaki altı ölçüm |
| **`KAT-2`** | **Cevapsız bir dal, cevaplı bir yolu KESEMEZ.** `source=None` dönen dal **return etmez** — kendini **aday** kaydeder, merdiven devam eder. Merdiveni yalnız **pozitif cevap** ya da kullanıcının **açık `yol_siniri`**'si bitirir | **AJ0** · MIMARI §5'in **18. yasağı** |
| 🔴 **`KAT-3`** | **Bir katman, kendisini BESLEYEN katmandan önce inşa edilmez.** | **Bu oturumlarda ÜÇ KEZ ihlal bulundu — üçü de düzeltildi**, aşağıda |
| 🔴 **`KAT-5`** | **SAYMA — KAPAT.** Kullanıcıya dönük bir anlam ekseni **literal bir kümeyle** tanımlanamaz; ya bir **kayıt/katalogdan türetilir** ya **bileşimsel bir ifadedir**. *Sayılan her küme, yeni her anlam için **kod** ister.* | **Aşağıdaki tablo: bu oturumda bulunan kusurların HEPSİ bu sınıftan** |
| **`KAT-4`** | **Kazanç ve gerileme FARKLI ALETLERLE ölçülür.** Aynı korpusta yarıştırmak `50402d3`'ün *"YANLIŞ NÜFUS ölçülmüştü"* dersinin tekrarıdır | `nl_accuracy --ab` ↔ `--ab-kurtarma` ayrımı **zaten kurulu**; §G.6 onu katman düzeyine taşır |

> 🔴 **`KAT-5` — KÖK TEŞHİSİN KÖKÜ. "Bir vaka veriyorum, bin açık çıkıyor" tam olarak budur.**
>
> **Kullanıcı (2026-08-03):** *"Ben sana bir case veriyorum, bin türlü açık çıkıyor… her
> ihtimali tek tek deneyecek miyiz? Her şeye tek tek geliştirme yaparsak ömrümüz yetmez."*
> **Haklı — ve sebebi ölçüldü:** bulunan **her** kusur, **sayılarak tanımlanmış bir küme**.
>
> | Sayılan küme | Kod | Yeni anlam gelince | Madde |
> |---|---|---|---|
> | `("yoy", "mom")` | 6 üyelik kapısı + tanımı | **7 dosyada kod** | AJ2 |
> | `it.result \|\| it.kpi` | *"raporlanabilir"* alan sayımı | **yeni dal** | 0.23 |
> | `FACT_ICON` sözlüğü | `top` **listede yok → sessizce düşüyor** | **yeni anahtar** | 0.10 |
> | `TUR_*` **5 tür** | `followup.py` | **yeni kalıp sözlüğü** | 5.3 · AJ0b |
> | `R1…R10` | red kodları — *"ifade edilemez"* **sayılamıyor** | **yeni kod** | `R11` |
> | SSE `adim\|tamam\|hata\|zaman_asimi` | **`soru` yok** | **yeni olay** | AJ3b |
> | `AskJob.status` **4 değer** | **`awaiting_input` yok** | **yeni durum** | AJ3b |
> | Intent-JSON **5 alan** | `compare`/`blend` **dışarıda** | **yeni alan** | AJ2 |
> | `Adim` — girdi/çıktı **yok** | araç **listesi**, boru hattı değil | **her bileşik elle** | AJ5b |
> | `_META_HINTS` alt-dize | yazım tahmini **merdiveni kesiyor** | **her typo bir yama** | AJ0 |
>
> 🔴 **Kodun kendi yorumları bu döngüyü ÜÇ KEZ kaydetmiş** — `bunu→gunu` · `bundan→unvan` ·
> `enerji kaynagi→enerji tep` — ve **her seferinde çağrı yerinde yamalanmış, kapının
> kendisinde hiç.** *Ömrün yetmemesinin mekanik sebebi budur.*
>
> **KURAL:** bir anlam ekseni ya **kayıttan/katalogdan türetilir** (`MetricDefinition` ·
> `tools.KAYIT` · `service.schema()`), ya **bileşimsel bir ifadedir**
> (`referans: {eksen, kaynak, hedef}`), ya da **`[SAYIM MUAF]`** olarak **gerekçesiyle**
> ilan edilir. *Üçüncü seçenek yok.*
>
> **KAPISI — `tests/test_sayim_yerine_kapanis.py` (0.14 ile birlikte yazılır):**
> kaynak taraması, **kullanıcıya dönük semantik eksenlerde** literal küme üzerinden üyelik
> kapısı (`in ("a","b")` · `dict` anahtar süzgeci · `Literal[...]`) arar; her isabet ya bir
> **kayıt kaynağına** bağlı olmalı ya **muafiyet listesinde** gerekçesiyle bulunmalı.
> ⚠ **Muafiyet meşrudur ve gereklidir:** `determinizm ∈ {deterministik, llm, karma}` gibi
> **mühendislik** eksenleri sayılabilir — kural **kullanıcının anlam uzayına** bakar,
> kodun iç sınıflandırmasına değil. *Sınır bulanıksa madde `[SAYIM MUAF]` yazar ve
> **tartışma kayda geçer**.*
>
> 🔴 **VE BU, "her ihtimali tek tek denemek" korkusunun cevabıdır:** kapı **örneği** değil,
> **sınıfı** yakalar. Yeni bir `compare` değeri, yeni bir SSE olayı, yeni bir fact türü
> eklenmek istendiğinde CI **kırmızı** verir ve *"bunu bir kayda bağla ya da muafiyetini
> yaz"* der. **Vaka sayısı sonsuz; kapı sayısı sonlu.**

> 🔴 **`KAT-3`'ün üç ihlali — ve neden kural yazılmazsa dördüncüsü gelir:**
>
> | # | Ne | Nerede duruyordu | Nereye çekildi | Kim buldu |
> |---|---|---|---|---|
> | 1 | **Metrik kaydı** (kapsamın enabler'ı) | FAZ **2.2** — 40 madde geride | **0.18** | dış denetim D4 |
> | 2 | **Gerçek kullanım penceresi** (her ölçümün enabler'ı) | **en sonda** | **FAZ 1'den sonra** (8.1) | dış denetim D5 |
> | 3 | **İş bağlamı** (II-D/II-E'nin enabler'ı) | **II-F = v3**, yani tükettiklerinden **SONRA** | **v2'nin önüne** — §B'nin notu | bu tur |
>
> *Üçü de aynı sınıf: **enabler, tüketicisinden sonra planlanmıştı**. Kural konmazsa
> dördüncüsü gelir — çünkü hiçbiri "yanlış" görünmüyor, hepsi konu başlığına göre doğru
> yerde duruyordu.*

**Bu dört kural neyi garanti eder** — ve her satırın **kapısı yazılı**:

| Ne uydurulamaz | Hangi kapı | Durum |
|---|---|---|
| başka tenant'ın verisi | **motor-RLS** (1.1) | FAZ 1 |
| bir terimin **ikinci sahibi** | `compose` **reddi** (0.18 · 2.1) | FAZ 0/2 |
| katalogda **olmayan alan** | `parse_cube_query` **beyaz listesi** | ✅ **kurulu** |
| **eşleşmeyen sayı** | `narration_guard` ±%2 | ✅ **kurulu** |
| **olmayan yetenek vaadi** | `app/iddia.py` | 🔴 **TEK EKSİK** → AJ1 |
| **onaysız yazma** | onay akışı (6.1) | FAZ 6 |

🔴 **Ve bu, "LLM'e ne kadar güvenelim" sorusunu ortadan kaldırıyor:** LLM **her katmanda
serbesttir**, çünkü **hiçbir çıktısı bir kapıdan geçmeden kullanıcıya ya da SQL'e ulaşmıyor.**
*"Anlamak"* ile *"çalıştırmak"* ayrı olduğu için **anlamayı LLM'e vermek kesinliği bozmuyor**
— MIMARI §11.6d'nin **SEÇİM ≠ ÇALIŞTIRMA** omurgası bunu zaten söylüyor, **yalnız hiç
açılmamış** (AJ5).

## §A.6 · Yedi katman — **yeni mimari DEĞİL, var olanın ayrıştırılması**

```
6 · ARTEFAKT   rapor · pano · zamanlama · karar kaydı      [onay akışı + audit]      6.1 · AJ6
5 · ANLAMA     niyet · ayrıştırma · konuşma  (LLM)         [4 kapı + iddia kapısı]   AJ1 · AJ3 · AJ5
4 · DİYALOG    slot · devam · onarım · temellendirme       [deterministik testler]   AJ0b
3 · YÜRÜTME    derle → dry_plan → koş → makbuz             [contract + fan-out sert.] ✅ kurulu
2 · DİL        CubeQuery = CEBİR (form değil)              [parse_cube_query beyaz l.] AJ2
1 · ANLAM      katalog · metrik hakemi · İŞ BAĞLAMI        [compose fail-closed]      0.18 · 2.1 · II-F↑
0 · GÜVENCE    motor-RLS · yetki · audit                   [authorize + RLS]          FAZ 1
```

⚠ **Somut olarak YENİ olan yalnız dört şey:** `app/iddia.py` · **diyalog katmanı** ·
**referans cebiri** · **`R11`**. *Geri kalan her şey ya **kurulu** ya **yazılıp kapalı**.*
Bu bölüm bir yeniden yazım **önermiyor** — var olanı **adlandırıyor**, çünkü kusurların
hepsi **katman karışmasından** doğuyor.

## §A.3 · Nasıl koşulur

```bash
# TEK SEFERLİK: test imajı (prod imaj + pytest) — MIMARI §7
docker build -t dima-test -f backend/Dockerfile.test backend/     # yoksa: MIMARI §7 reçetesi

# ⚠ Depo KÖKÜNDEN koşulur; frontend mount'u ZORUNLU (yoksa yetim-uç kapısı SESSİZCE atlanır)
docker run --rm --network none -v "$PWD/backend:/app" \
  -v "$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro" \
  -w /app -e DIMA_VQR_EMBEDDER=off dima-test python -m pytest -q
docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python -m eval.run
docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python lab/nl_corpus.py --kapi
docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python lab/konusma_senaryolari.py
docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test python lab/nl_accuracy.py
```

**Her fazın değişmez beş adımı:** (1) kusuru **önce ölç** → (2) düzelt → (3) **kapıya
çevir** → (4) tam süit + `eval` + `nl_corpus` gerilemesin → (5) **`MIMARI.md`'yi aynı PR'da
güncelle** (`⟳` → `✅`).

**Canlı doğrulama** (LLM yolunu değiştiren fazlarda): rebuild + seed + **izole** konteyner
(`-v backend:/src:ro` + kopya), **tur arası 5 sn** (ölçülen sınır 10 sn/10 istek; bir Intent
turu `consistency_k=3` ile üç çağrı).

## §A.4 · Başlangıç varsayımı ve **cevaplanmış ilk kontrol**

✅ **VARSAYIM ARTIK GERÇEK — yürüyen plan TAMAMEN BİTTİ** *(kullanıcı, 2026-08-03:
"diğer plan tamamen halledildi, tamamladık")*. Bu belge artık **varsayım üstünde değil,
kapanmış bir taban üstünde** duruyor.

| Faz | Durum | Kanıt @`88bde2a` |
|---|---|---|
| D1·D2·D3·D4 · A · B · C · H · E | ✅ bitti | önceki damgalarda doğrulandı |
| **X** (deneyim süiti) | ✅ **indi** — `a5942c7` | `lab/deneyim.py`, taban **34 ✅ / 1 ❌ / 56 ⊘** (§F.1) |
| **S** (akış + steering) | ✅ **indi** — `ce9ee43` | 🔴 **§D.1'in hükmüne UYGUN: SSE** — `StreamingResponse` + `media_type="text/event-stream"` (`ask.py:3477-3509`); WebSocket **yok**. *Hüküm tutuldu.* |
| **G** (parite kuyruğu) | ⏸ ertelendi (kullanıcı kararı) | beş maddesi bu belgede **evlerine dağıtıldı** (aşağıdaki `(b)` tablosu) |

> ⚠ **Ve iki commit daha ölçüme girdi:** `c4b14d1` (`--live` **üçüncü kez** karşılıksızdı →
> **0.16**) · `88bde2a` (gerçekçi canlı senaryolar **iki yeni kusur** çıkardı: *boş sonuç
> sessizliği* + *takvim yılı*). **Sekiz commit boyunca HEAD ilerledi ve her turda yeni kusur
> çıktı** — D2'nin (damga + yeniden ölçüm) neden zorunlu olduğunun kanıtı.

> ⚠ **DÜZELTME (2026-08-03, kullanıcı kararı — geliştiriciye bildirildi):**
> **`S` (akış) YAPILACAK · `G` (parite kuyruğu) ERTELENDİ.** Yani başlangıç durumu
> *"13 fazın tamamı"* değil, **12 faz + S**'dir. İki sonucu var:
>
> **(a) S yapılırken §D.1'in hükmü bağlayıcıdır: SSE, WebSocket DEĞİL.** SSE tek yönlü,
> mevcut HTTP üstünde, **yeni bağımlılık yok** — hükümle uyumlu. WebSocket *"bilinçle
> ertelenir"* kararını çiğner. Aşama olayları merdivenle aynı olmalı:
> `route → intent → derleme → çalıştırma → anlatım`. **Steering S'in parçası DEĞİL** —
> çift yönlü kanal ister, II-D'ye bırakılır.
> *(Ucuz ara adım, sıfır yeni kod: `ask_async_discovery` bayrağı + `/ask/jobs` polling +
> `liveTrace` **zaten yazılmış**, yalnız `features.yml`'e konmamış.)*
>
> 🔴 **DÜZELTME — bu cümle DOĞRU ama EKSİK** *(sohbet raporu M5/B7; üç madde de kod
> ölçümüyle doğrulandı @`c4b14d1`)*. *"Sıfır yeni kod"* kısmı **ancak şu üçü yapılırsa**
> gerçek olur:
>
> **(1) Bayrak YAML'de yok — ve YALNIZ DEĞİL.** `ask_async_discovery` `features.py:85`'te
> **kayıtlı**, `features.yml`'de **YOK**
> (`grep -c ask_async_discovery backend/demo/packs/features.yml` → **0**).
> ⚠ **Ve ikinci bir tane var:** `threaded_chat` de aynı durumda —
> `FLAG_REGISTRY` **16** ↔ `features.yml` **14**. İkisi de *"BİLEREK … eklenmedi"* **beyanı**
> taşıyor **ve `threaded_chat` doğrudan `ask_async_discovery`'ye atıf yapıyor**
> (*"…ile AYNI ilke"*). → **Birini YAML'e koyarken ötekinin gerekçesi bayatlar.**
> Bayrak eklenirken **her iki beyan da güncellenir**, yoksa `test_bayrak_kaydi.py` **bayat
> bir gerekçeyi kilitler**.
>
> **(2) 🔴 `liveTrace` YANLIŞ PANELE veriliyor.** `page.tsx:395` onu **yalnız `ChatPanel`'e**
> geçiriyor (`ChatPanel.tsx:239`) — ama **konuşma SAĞ panelde akıyor** ve orada sabit
> `"yürütülüyor…"` var (`ReportPanel.tsx:247`). **Bayrak açılsa bile canlı iz, konuşmanın
> olduğu yerde GÖRÜNMEZ.** `liveTrace` `ReportPanel`'e de geçirilir (~15 satır).
>
> **(3) `pollAskJob`'un ilk `setTimeout`'u döngünün BAŞINDA** (`api-client.ts`:
> `for (…) { await new Promise(r => setTimeout(r, ASK_JOB_POLL_MS)); …}`) → her Discovery
> cevabına **1,5 sn TABAN gecikme** ekliyor. Döngü **SONUNA** alınır.
>
> **KAPI — M5 KENDİ TABANINI KAYDEDER, FAZ 0.17'yi BEKLEMEZ:**
> (a) değişiklikten **önce** Discovery turu p50/p95 ölçülür ve `lab/reports/` altına yazılır ·
> (b) değişiklikten sonra p50 **kendi tabanına göre artmamalı** ·
> (c) 0.17 (yol başına gecikme bütçesi) indiğinde kapı **mutlak bütçeye bağlanır**.
> *Gerekçe: 0.17'ye bağımlı bırakmak bu işi **bloke ederdi**; oysa kendi kazancı (1,5 sn
> taban gecikmenin kalkması) 0.17'den bağımsız ve ölçülebilir.*
>
> ⛔ **KAPSAM DIŞI — deterministik aşama betiği** (*"+0ms sorunu okuyorum → +400ms katalogda
> arıyorum → +1200ms sorguyu kuruyorum"*): **EK J / KD-22.** İki gerekçe, **ikincisi
> bağlayıcı**: (i) sayılar gerçek değil — küp yolu **145–434 ms** (MIMARI §2.2), turların
> çoğu betik `+1200ms`'e varmadan biter, yani betik **algılanan gecikmeyi UZATIR**;
> (ii) 🔴 **sınıf sorunu** — kimliği *"hiçbir şey uydurulmaz"* olan bir üründe
> **senaryolanmış zamanlamayı ilerleme diye göstermek**, cümleler teknik olarak doğru olsa
> bile, **kalibre edilmemiş güven rozetiyle aynı ailedendir**. Bu depo o sınıfı avlıyor.
>
> **(b) G'nin beş maddesi bu belgede şu evlere dağıldı** — erteleme bir **karar**, unutkanlık
> değil:
>
> | G maddesi | Ev | Not |
> |---|---|---|
> | Discovery rozet dürüstlüğü | **FAZ 7.8** | ⚠ **evi yoktu, bu düzeltmeyle eklendi** |
> | MCP yüzeyi | **FAZ 4.5** | — |
> | Skills | **II-F.9** (`HafizaKaydi.tip="prosedürel"`) | ayrı varlık **yazılmaz** |
> | `stats.py` forecast/regresyon | **II-D.2** | 🔴 **G'de yapılması YASAK** — dört kapısı (aralık zorunlu · MASE<1.0 · ≥12 ay · toplanabilirlik) orada. *(`stats.trend`/`stats.ozet` **FAZ 5.15**'te ve güvenli: tanımlayıcı istatistik, tahmin değil.)* |
> | Reçete/karar ayrık gösterim | **büyük ölçüde YAPILMIŞ** (`PrescriptionLayer.tsx`, `d01b405`) | kalanı FAZ 7.8 |

> ✅ **İLK KONTROL CEVAPLANDI — ve H, BU BELGENİN ÖNERDİĞİNDEN DAHA İYİ İNDİ** (`c527613`).
>
> **Ölçüldü @`c4b14d1`:** `app/tools.py` **hâlâ 15 araç · 0 yazma aracı · 15/15
> `izin="query:run"`**; `test_ajan_YAZAMAZ` **yeşil**. Yani ajan **hâlâ yazamıyor** —
> ve H yine de teslim edildi.
>
> **Nasıl:** `app/eylem.py` (342 satır) + onay ucu. Yazma **araç kaydına girmedi**;
> öneri, **kullanıcının kendi eliyle çağırabileceği ucu** çağırıyor. Üç değişmez:
> 1. **Argümanlar LLM'den GELMEZ** — önerinin `cube_query`'si konuşmada **zaten
>    doğrulanmış** sorgudur. *(Uydurma bir sorgu zamanlamaya yazılsaydı **her hafta**
>    koşardı.)*
> 2. **Öneri yeni YETKİ yaratmaz** — *"güvenlik imzadan değil, **yetki yüzeyinin
>    genişlememesinden** geliyor."*
> 3. **Çapa yoksa öneri de yok** — sistem sınırını **söyler**, uydurmaz.
>
> 🔴 **Bu, bu belgenin FAZ 1.3 endişesini YAPISAL OLARAK ÇÖZÜYOR.** Benim teşhisim
> *"15 araç tek izin taşıyor, yazma aracı eklenince `authorize()` ayırt edemez"* idi.
> Uygulanan cevap daha iyi: **yazma aracı hiç eklenmiyor.** → **FAZ 1.3 artık H'nin ön
> koşulu DEĞİL** (gerekçesi değişti, bkz. 1.3).
>
> **Ve ölçülen kusur plandan kötü çıkmış:** *"ajan yazmıyordu ama **UYDURUYORDU**"* —
> `"her pazartesi bu raporu bana yolla"` → `source=rule`, **SQL ÜRETTİ**, 1 satır;
> `"bunu panoya ekle"` → *"«bunu» yerine «gunu» mi demek istedin?"*. Kök neden **D1 ve D2
> ile aynı aile**: veri sorusu **olmayan** bir ifade sınıfının tanımsızlığı.
>
> **Her başlangıçta tekrarlanacak kontrol:**
> `grep -c 'yan_etki="yazar"' backend/app/tools.py` → **0 bekleniyor** (yorum satırları
> hariç; `grep -c "^    Arac(" app/tools.py` → **15**).

---

# §B. SÜRÜM HARİTASI

Kaynak şartnamenin kendi çerçevesi: *"**v3 çekirdek ürünün tamamlandığı noktadır (%100);
v4–v6 nihai vizyondur**"* (L110). Bu belge şartname **FAZ 1→9**'u (**8B hariç**) kapsıyor →
teslim ettiği şey **çekirdek ürünün tamamıdır**.

| Sürüm | Fazlar | Ürün vaadi | Bittiğinde |
|---|---|---|---|
| 🔴 **§G · AJAN** | **§G** (AJ0→AJ4) — **v1'e PARALEL, ona bağımlı değil** | *"Konuşan **ortak** — ölçülerek"* | **§G.6'nın kıyas sözleşmesi** koşuldu ve **karar yazıldı** (B `beta`'ya geçti **ya da** `off` kaldı + gerekçe). ⚠ **Kararın kendisi bir teslimdir** — *"B kazanmadı"* da geçerli bir sonuçtur |
| **v1** | **Bölüm I** (FAZ −1 → 8) | *"Konuşan, kanıtlayan, güvenli şirket beyni"* | §C'nin **16 ölçütü** yeşil *(12 iç kalite + **4 kullanıcı sonucu**; sürüm 3 burada hâlâ "12" diyordu — dış denetimin eklediği 13-16 sayılmamıştı)*; satılabilir, denetlenebilir, ilk müşteriye açılabilir |
| **v2** | **II-D + II-E** | *"**Analist** ve **karar** ortağı"* | *"Ne olacak?"* ve *"Ne yapmalıyım?"* **kanıt matrisiyle** cevaplanır |
| **v3** | **II-F** *(kalanı)* **+ II-G + II-H** | *"Şirketi **tanıyan**, kendini **geliştiren** platform"* | **Çekirdek ürün %100** |

> 🔴 **`KAT-3`'ÜN ÜÇÜNCÜ İHLALİ — ve düzeltmesi (sürüm 7).** §B **II-F'i v3'e**, onu
> **tüketen** II-D (analist) ve II-E (karar) fazlarını **v2'ye** koymuştu. Yani **enabler,
> tüketicisinden SONRA** planlanmıştı — metrik kaydı (2.2→0.18) ve gerçek kullanım penceresi
> (→8.1) ile **aynı sınıf**, üçüncü kez.
>
> **Bağlam olmadan üçü de jenerikleşiyor — üçü de somut:**
> 1. 🔴 **Anomali, bağlam olmadan yalnız bir z-skorudur.** Sistem sayının 2σ oynadığını
>    bilir; **martın her yıl planlı bakım yüzünden düşük olduğunu bilmez** → yanlış alarm.
>    *(EK F'de kaynaklı: alarm literatüründe **%72-99 yanlış-alarm** — array.aami.org.
>    ⚠ Bir değerlendirme bunu `[DOĞRULANMADI]` sandı; **kaynağı var**, EK F'de.)*
> 2. 🔴 **Karar motoru, bağlam olmadan bir çerçevedir.** II-E.4'ün kanıt matrisi
>    `VERİ | VARSAYIM | BİLİNMİYOR` — ***"VARSAYIM" sütununu dolduran şey şirket
>    bilgisidir.*** II-F yoksa o sütun **boş kalır** ve matris **süse döner**.
> 3. **"Analiz", bağlam olmadan betimleyici istatistiktir** — ki `interpret.py` onu
>    **zaten yapıyor**.
>
> **KARAR — dört madde v2'nin ÖNÜNE alınır** *(II-D'den önce, madde numaraları değişmez —
> yalnız **sıra** değişir, D5'in kütük kuralı gereği taşıma yapılmaz):*
> **II-F.1** (iş bağlamı kütüğü) · **II-F.3** (kurumsal takvim) · **II-F.5** (iş terimleri
> sözlüğü) · **II-F.8** (şirket profili + bağlam enjeksiyonu).
> **Kalanı v3'te kalır:** II-F.2 · II-F.4 · II-F.6-7 · II-F.9-12 (hafıza · unutma · brifing
> · görev motoru).
| v4-v6 | — | Kurumsal Bilgi Hub'ı · Canlı Akıl · Külli Akıl | **KAPSAM DIŞI** (EK J) |

> **Sürüm sınırı bir teslim kapısıdır.** v2'ye geçiş için ek olarak **§II-0'ın 11 maddesinin
> her birine KARAR BAĞLANMIŞ** *(`[TEYİT ALINDI]` **ya da** `[TEYİT ALINMADI]` — ikisi de
> geçerli bir kapanış; bkz. §II-0'ın döngü düzeltmesi)* ve **FAZ 8.1 (gerçek kullanım
> penceresi) koşulmuş** olmalıdır.

---

# §C. v1 TANIMI — *"bitti"* ne demek, **sayıyla**

Hepsi ölçüm. **Ölçüm komutu ve payda yazılıdır** (kural D2).

> ✅ **FAZ 0.1 İNDİ (@`e22b2b9`) — «Bugün» sütunu artık ELLE YAZILMAZ.**
> *(Denetim düzeltmesi: bir ara `@0619bfd` yazıyordu; `git ls-tree 0619bfd` ile ölçüldü,
> araç o commit'te **yoktu** — yalnız çalışma ağacındaydı. **İnmemiş bir şeyi inmiş
> ilan etmek**, bu belgenin avladığı sınıfın ta kendisi.)*
> Üreteç: **`backend/lab/faz0_taban.py`** → `backend/lab/reports/faz0_taban.md`.
> Aşağıdaki sayılar o koşumdan alınmıştır; bir daha bayatladıklarında **kaynak
> düzeltilmez, araç yeniden koşulur**.
>
> ⚠ **KAPSAM AÇIKÇA YAZILIR (sessiz kırpma YOK).** Üreteç **1a…12 + süit sayısı**nı ölçer.
> **13-16 kapsam DIŞIDIR** ve bu bir eksiklik değil, **yapısal**: dördü de *"kullanıcı
> sonucu"* ölçütüdür ve ölçüm aracı bir **insan turu** ya da **tutulmuş küme** ister —
> `13` FAZ 8.1 penceresi · `14` FAZ 3.0 uçtan uca koşumu · `15` FAZ 4.3 sharding
> benchmark'ı · `16` FAZ 4.8'in yeni `lab/uctan_uca.py`'si. Dördü de aşağıda
> **`[ÖLÇÜLMEDİ]` + sahibiyle** duruyor; üreteç onları **uydurmaz**.
>
> 🔴 **Ölçüt 1'de bir TANIM BULANIKLIĞI ölçüldü ve ayrıştırıldı:** *"yanlış-cube 493"*
> aslında **458 yanlış cube + 35 Discovery'ye düşme** toplamıdır. Hedef *"azalır"*
> olduğu için hangi sayının azalacağı belirsiz kalamaz → **1a** (yalnız yanlış cube)
> ve **1b** (doğru cube üretilemedi) ayrı satırlardır.
>
> ⚠ **Aracın kendi kusuru da kayda geçsin:** ilk sürümü host'ta `pytest --collect-only`
> koşup **1806** yazıyordu (konteynerde **2056**) — eksik bağımlılık yüzünden testler
> toplanamıyor, `pytest` yine de *"collected"* diyordu. Araç artık **toplama hatası
> varsa sayı yazmıyor** (`⊘`). *Ölçüm aracının kendisi de bir bağımlılıktır.*

| # | Ölçüt | Bugün | v1 hedefi | Ölçüm |
|---|---|---|---|---|
| 1a | **Sessiz-yanlış — yanlış cube** | **458/7213 = %6,3** @`0619bfd` | **azalır** | `lab/faz0_taban.py` |
| 1b | Sessiz-yanlış — **doğru cube üretilemedi** *(yanlış 458 + Discovery 35)* | **493/7213 = %6,8** @`0619bfd` | **azalır** | aynı |
| 1c | **`YANLIS-OK`** (gürültüye SQL) | **7** @`0619bfd` | **7 → artmaz** | aynı |
| 2 | **Doğrudan cevap (OK)** | **7580/10865 = %69,8** @`0619bfd` *(değişmedi)* | **artar** — kaynağı **yalnız** `CLARIFY:konu` + yanlış-cube | aynı |
| 3 | **`CLARIFY:dönem`** | **1478/10865 = %13,6** @`0619bfd` *(değişmedi)* | **DEĞİŞMEZ (±0,5 puan)** | değişiyorsa ADR-0007 K3 politikası delinmiş → **KIRMIZI** |
| 4 | **Motor-seviyesi RLS** | **0** @`0619bfd` *(değişmedi)* | `on`; **gölge modda 7 gün · sapma 0** | `logs/rls_shadow.jsonl` satır sayısı = 0 |
| 5 | **Yetki granülerliği** | 15 araç · **15/15 `query:run`** @`0619bfd` *(değişmedi)* | araç başına **gerçek aksiyon**; viewer `contribution.report` çağıramaz | `tests/test_arac_kaydi.py::test_izin_MATRISTE_var` |
| 6 | **Onaysız yazma** | yazma aracı **0** · onay akışı **YOK** @`0619bfd` | **imkânsız** + onay başına audit satırı + **süre aşımı 30 dk** | `tests/test_onay_akisi.py` |
| 7 | **Yetim uç / alan** | **⊘ ÖLÇÜLEMEDİ** @`e22b2b9` — kapılar yeşil ama §C'nin 9'u **kapının göremediği** sınıftan; envanter **FAZ 0.14**'te (K1-K5 kör noktaları) yeniden sayılır *(sürüm 3 "8" diyordu; 9.'su B1)* | **0**; K1-K5 kapıları **kör noktasız** | `test_uc_yetim_degil` · `test_cevap_alani_yetim_degil` |
| 8 | **Ölçüm kapıları CI'da** | **1 workflow (`backend-ci.yml`) · ölçüm kapısı taşıyan 0** @`e22b2b9` | 4 kapı **gecelik otomatik** | `.github/workflows/nightly.yml` |
| 9 | **Konuşma türleri** | **5** @`0619bfd` (`NEDEN·NORMAL·NE_YAPMALI·ISARET·ANLAT`) | 🔴 **v1 = 7** (+takip +paylaş) · **8.'si (görev) v3'te** — aşağıdaki kutu | `test_takip_ucuncu_sinif` + kalıp korpusu ≥10 varyant/tür |
| 10 | **Ölü bayrak** | `FLAG_REGISTRY` **16** ↔ `features.yml` **14** @`e22b2b9`; kayıtta var YAML'de yok: **`ask_async_discovery` · `threaded_chat`** *(+ 4 `off` + 12 `ui_*` yalnız frontend'de)* | **0** — hepsi `FLAG_REGISTRY` **ve** `features.yml`'de, **ölçüm tarihli** | `tests/test_bayrak_kaydi.py` · `FLAG_REGISTRY` **16** ↔ `features.yml` **14** @`c4b14d1` |
| 11 | **Panel sayısı** | **export 13 · dosya 12** @`e22b2b9` — 🔴 tanım kutusu aşağıda | tavan **13 export**; Bölüm II'de **15** (PK-23) | `tests/test_panel_sayisi.py` — 🔴 **BU DOSYA YOK, FAZ 0.14'te YAZILIR** · ölçüm komutu **tanımla birlikte** |
| 12 | **Tazelik** | **0** @`0619bfd` *(değişmedi)* | her cevapta `taze\|uyarı\|hata\|bilinmiyor`; **`hata`/`bilinmiyor` → SAYI GÖSTERİLMEZ** | `tests/test_tazelik.py` |

> 🔴 **ÖLÇÜT 9 — DÖNGÜSEL KİLİT ÇÖZÜLDÜ (sürüm 5).** Sürüm 4 v1 hedefini **8 tür** yazmıştı;
> ama 8. tür (`TUR_GOREV_OLUSTUR`, bayrak `tur_gorev`) **II-F.6'da**, yani **v3'te**. Ve §B
> *"v2'ye geçiş için §C'nin 16 ölçütü yeşil olmalı"* diyor. → **v1'in kapanması v3'ün bir
> maddesini gerektiriyordu: döngüsel kilit, v1 asla kapanamazdı.**
>
> **KARAR: v1 = 7 tür. 8.'si motoruyla birlikte II-F'de kalır.**
> **Gerekçe belgenin kendi kuralıdır — ÖLÜ DOĞUŞ YASAĞI** (§A.2): *"bir yetenek, ilk
> tüketicisi aynı fazda yazılmadan v1'e giremez."* `tur_takip` (5.1) ve `tur_paylas` (5.2)
> motorlarını **hazır buluyor** (`schedules` · `report`/link). `tur_gorev`'in motoru ise
> **yok** — `Gorev` tablosu ve görev akışı **II-F.6'da doğuyor**. Sınıflandıran ama
> **eyleme geçemeyen** bir tür, bu belgenin avladığı *"yazılmış ama tüketicisiz"* sınıfının
> ta kendisi olurdu.
> ⚠ **Alternatif reddedildi:** *"türün yalnız konuşma-girişi yarısını FAZ 5'e al, motoru
> II-F'de kalsın."* Bu, tam olarak ölü doğuş olurdu — kullanıcı *"bunu göreve dönüştür"*
> der, sistem sınıflandırır ve **hiçbir şey yapamaz.**

> 🔴 **ÖLÇÜT 11'İN TANIMI — sayıdan ÖNCE gelir, yoksa test kırmızı doğar.**
> *(Sohbet raporu §9/1 uyardı; ben iki tanımı da koştum ve **ikisi de doğru çıktı** —
> tam da bu yüzden tanım yazılmadan test yazılamaz.)* Ölçüm @`c4b14d1`:
>
> | Tanım | Komut | Sonuç |
> |---|---|---|
> | **A · dosya** | `ls src/components/*Panel.tsx \| wc -l` | **12** |
> | **B · export** *(seçilen)* | `grep -rE "export (default )?function [A-Za-z]+Panel" src/ \| wc -l` | **13** |
>
> **Fark tek bir dosyadan geliyor:** `NotificationsPanel` **`NotificationsBell.tsx` içinde**
> yaşıyor (`:64`) — yani bir panel, adını taşımayan bir dosyada. `TercihlerPanel` ise
> `export **default**` kullanıyor ve *"`export function`"* arayan bir grep'ten kaçar
> (benim ilk ölçümüm **tam olarak buna** takıldı ve 12 dedi).
>
> **KARAR — tanım B (export):** kapı *"kaç dosya var"*ı değil, **kullanıcının kaç ayrı
> tam-yüzey bağlamıyla karşılaştığını** ölçmeli; dosya düzeni bir uygulama ayrıntısıdır.
> `export default` ve `export function` **ikisi de sayılır** — aksi hâlde kural,
> ihracat biçimi değiştirilerek sessizce delinir.
> **Payda notu:** `facetPanelValues` (`lib/chart.ts`) bir yardımcı fonksiyondur, panel
> değildir — kapının regex'i `function [A-Za-z]+Panel` **sonu** ile sınırlıdır.
>
> ⚠ **K5 (FAZ 0.14) bu tanımla hizalandı** — sürüm 3'te K5 hâlâ *"11"* diyordu, §C/11 ise
> *"12"*. **Belge kendi içinde çelişiyordu**; ölçüm ikisini birden düzeltti.

> 🔴 **DENETİM DÜZELTMESİ (dış denetim, `u-anda-bir-plan-tingly-fox.md` · D7/K4):**
> Yukarıdaki **12 ölçütün 12'si de İÇ KALİTE**. *"Kullanıcının bir işi başarıp
> başarmadığını"* ölçen **tek satır yoktu** — yani §C 12/12 yeşilken ürün **kullanılamaz**
> olabilirdi. Dört ölçüt eklendi:

| # | Ölçüt | Bugün | v1 hedefi | Ölçüm |
|---|---|---|---|---|
| **13** | **Görev başarımı** — ekip dışı kullanıcı, kendi işinden 10 soru, **yardımsız** | `[ÖLÇÜLMEDİ]` | **≥%70 kabul edilebilir cevap**, **kör** insan hakem | FAZ 8.1 penceresi + yazılı rubrik |
| **14** | **Yeni tenant'ta ilk doğru cevaba kadar** (insan-saat) | `[ÖLÇÜLMEDİ]` | **ölçülür ve yayımlanır** | FAZ 3.0'ın uçtan uca koşumu |
| **15** | **Çok-turlu dayanıklılık — `pass^k`** *(`pass@k` DEĞİL)* | `[ÖLÇÜLMEDİ]` | 5 turda yapı kaybı **0**; **`pass^5` raporlanır** | FAZ 4.3 sharding benchmark'ı |
| **16** | 🔴 **UÇTAN UCA cevap doğruluğu, BAĞIMSIZ kümede** | `[ÖLÇÜLMEDİ]` — `nl_accuracy` **n=63**, `eval` **kuratörlü** | **n≥100**, tutulmuş küme, **ilan edilmiş** puanlama kuralı | **yeni `lab/uctan_uca.py`** (FAZ 4.8) |

**Neden 16 zorunlu:** §C/1-2 **cube seçimini** ölçüyor (%93,2 = *"doğru cube"*, *"doğru
cevap"* **değil**). MIMARI §7'nin kendi ifadesiyle `eval` *"zaten çalışan şeye göre
kuratörlenmiş"* bir **regresyon kilidi**. Rakiplerin yayımladığı **tek kıyaslanabilir sayı**
budur ve bugün **elimizde ölçecek alet yok** → **FAZ 4.7'nin teknik raporu bu sayı olmadan
YAYIMLANAMAZ.**
**Puanlama kuralı** (en yakın analog, n=90 gerçek kurumsal vaka): *"bir cevap ancak **dönen
değer, varlık kapsamı ve zaman/filtre semantiği** altın cevapla eşleşiyorsa doğru sayılır"*.
**Netleştirme AYRI SATIR** olarak raporlanır — paydadan **gizlice çıkarılmaz** (rakiplerin
manşet sayılarını kıyaslanamaz yapan şey tam olarak bu).
**Neden 15 `pass^k`:** τ-bench ölçtü — `pass^1` >%60 iken **`pass^8` <%25**. Tek atımlık
başarı, **8 farklı müşteride aynı işi çözmeyi öngörmüyor**.
⚠ **Ve açık soru:** `nl_accuracy`'nin **63 etiketli vakasının etiketlerini kim doğruladı?**
BIRD/Spider'da anotasyon hata oranı **%52,8 / %62,8** ölçüldü — **10 puanın altındaki fark
gürültüdür.**

**Değişmeyen güvence:** sayıyı **her zaman küp koyar**. Anlatı guard'dan geçer; eşleşmeyen
sayı taşıyan cümle **yayımlanmaz**. En kötü durum *"süssüz ama doğru"*.

---

# §D. DEVRALINAN HÜKÜMLER — **tartışmaya kapalı 13 karar**

Plan 3 §3.1/§3.2'nin **kararlarıdır, gözlemleri değil**. Kaynak plan silinince kaybolmasın
diye buraya taşındı.

## §D.1 · Teknoloji yığını (8 hüküm)

| Şartname istiyor | Gerçek | **HÜKÜM** |
|---|---|---|
| BullMQ + Redis, WebSocket | `AskJob` + HTTP polling | **`AskJob` genişletilir, Redis EKLENMEZ.** **WebSocket bilinçle ertelenir** — polling ölçülmüş ve yeterli. ⚠ **S fazı bu hükümle UYUMLU biçimde yapılır: SSE** (tek yönlü, mevcut HTTP üstünde, yeni bağımlılık yok). WebSocket ancak **çift yönlü steering** gerektiğinde ve **ölçümle** yeniden açılır (→ II-D) |
| Vault | AES-256-GCM + `DIMA_CRED_KEK` | **Mevcut korunur**; yalnız **çok-süreçli dağıtımda** yeniden değerlendirilir (→ FAZ 1.4) |
| Vega-Lite, gerekirse LLM ile grafik | ECharts + deterministik `viz.py` (ADR-0024) | **Mevcut KAZANIR.** Vega-Lite yalnız **ara temsil (IR)** olarak değerlendirilebilir; **kararı LLM'e devretmek asla** |
| pgvector | `vqr.py` + fastembed | **Ayrı vektör deposu KURULMAZ.** *Dosya/Git = kaynak, indeks = türev* |
| LangGraph | `planner.py` (4 kapı) + `tools.py` | **Yeni framework EKLENMEZ** |
| Prophet | yok | **KULLANILMAZ** → ETS/Theta + mevsimsel-naive (**II-D.2**) |
| Z3 | yok | **Kapsam DAR**, faz sonuna (**II-H.2**) |
| OR-Tools | yok | **KABUL** — *"nicel çatışma bir **optimizasyon problemidir**, LLM tartışması değil"* (**II-H.1**) |

## §D.2 · Şartnamenin kendi 5 çelişkisi

| # | Çelişki | **HÜKÜM** | Nerede |
|---|---|---|---|
| 1 | value profiling ↔ *"ham hücre LLM'e ASLA gitmez"* | `sensitivity.prompt_safe_values()` **zaten uyguluyor**: `normal` kolonların enum'u girer, `person`/`special` girmez. **Çözüm zaten kodda** | 1.2 · 3.6 |
| 2 | PNG/CSV tarayıcıda ↔ maskeleme her çıktıda | Maskeleme **payload tarayıcıya ULAŞMADAN** (`seal()` içinde). ⚠ **Grafik etiketleri de dâhil** (bkz. 1.2/c) | 1.2 · 5.2 |
| 3 | sektör kıyası ↔ *"kıyaslamaz — v6"* | **Havuz altyapısı kurulur** (k-anonimlik kapısı), **kıyas ÇIKTISI bayrak arkasında KAPALI**. 🔴 **Beyan ile teslim AYRILIR** | II-G.1 |
| 4 | onaylı yazma ↔ *"hiçbir sisteme yazma yapmaz"* | Ayrım **onaysız/otonom** ile **insan onaylı** arasında. `tools.py`'nin yazma araçlarını kayda hiç almamış olması **bu ayrımın zaten uygulanmış hâli** | 6.1 → 6.2 |
| 5 | PDF/OCR ↔ Kanıt Sınıfı Ayrımı | Şartnamenin kendi uyarısı: *"10.1 bitmeden hiçbir parçası devreye alınmamalı"* → **`PROBABILISTIC_CONTEXT` etiketlemesi olmadan CANLIYA ALINMAZ** | 1.12 (alan) · tam hâli **v4+** |

---

# §E. AD ALANLARI ve ÇAKIŞMA SÖZLÜĞÜ  *(denetim düzeltmesi — 5 P0 çakışma)*

## §E.1 · Faz ad alanları — **DÖRT tane var, karıştırılması yasak**

| Ad alanı | Ne demek | Kullanımı |
|---|---|---|
| **`FAZ −1…8` · `II-D…II-H`** | **BU BELGENİN** fazları | varsayılan; atıf verirken **her zaman bu** |
| `şartname FAZ n` | Şartnamenin fazı (`FAZ 4 = %72` gibi) | yalnız **"şartname FAZ n"** yazılarak |
| `Plan 3 Faz A-H` | Plan 3'ün uygulama sırası | **artık kullanılmıyor** — bu belgeye taşındı |
| `MIMARI faz kodları` (`Faz 2` · `Faz D2` · `Faz G3` · `Faz I4/I5` · `2a-1` …) | **Geçmiş** turların kodları; `MIMARI.md`'de kayıtlı | yalnız **"MIMARI Faz X"** yazılarak |

> ⚠ **Sürüm 1'in hatası:** §2.1'in NASIL'ı *"Faz 2'nin kanıtlanmış deseni"* diyordu — ve o
> madde **bu belgenin FAZ 2'sinin içindeydi**. Artık **"MIMARI Faz 2"** yazılıyor.

## §E.2 · Kod aileleri — çakışmalar giderildi

| Kod | **BU BELGEDE** | Karıştırılmaması gereken |
|---|---|---|
| **`D1-D4`** | §A.2'nin **belge kuralları** | ~~R1~~ (eski ad, red koduyla çakışıyordu) |
| **`K1-K5`** | **Entegrasyon kapıları** (0.14) | **`ADR-0007-K3`** (dönem netleştirme politikası) — artık **her zaman ADR öneki ile** |
| **`PK-1…PK-24`** | **Plan 2'nin panel/katman kuralları** (EK H) | ~~P-n~~ (eski ad) |
| **`A11Y-1…A11Y-10`** | Erişilebilirlik kuralları (EK I) | — |
| **`KD-1…KD-23`** | Kapsam dışı maddeler (EK J) | — |
| **`B4…B10`** | Plan 3'ün backend değişmezleri (EK C) | — |
| **`V-1…V-7` · `E-1…E-4`** | Plan 2'nin doğrulama/birleştirme kapıları (EK C) | — |
| **`R1…R11`** | **`cube_router`'ın red kodları** (EK G'de sözlük) — 🔴 **`R11` YENİ** (*anlaşıldı ama **ifade edilemez***, §G/AJ2; bugün `R1..R10` var) | belge kuralları (artık `D1-D4`) |
| **`VK-1…VK-6`** | **Adı konmuş kabul vakaları** (§G.6e) — üçü de (T1·T2·T3) geçmeden madde inmez | `V-1…V-7` = Plan 2'nin doğrulama kapıları (EK C) |
| **`T1·T2·T3`** | **Test rejimi katmanları** (§G.6d): klasik · canlı · vaka | `D1-D5` belge kuralları · `KAT-n` mimari kurallar |
| **`KAT-1…KAT-5`** | **Mimari katman kuralları** (§A.5) | 🔴 **`K1-K5`** = entegrasyon kapıları (0.14) · **`D1-D5`** = belge kuralları (§A.2) · **`ADR-0007-K3`** = dönem politikası. *Üç ayrı `K` ailesi vardı; dördüncüsü `KAT-` önekiyle açıldı ki karışmasın* |
| **`AJ0…AJ6`** | **§G'nin ajan katmanı maddeleri** | 🔴 **`G5`/`G10`** = `compose()`'un **fail-closed kapıları** (EK G) · **`Faz G1/G3`** = MIMARI faz kodları · **`G` fazı** = yürüyen planın parite kuyruğu. *Sürüm 6'nın ilk taslağı bunlara `G0…G4` demişti ve **üç aileyle birden** çakışıyordu; ölçümle yakalandı ve `AJ`'ye çevrildi. **§E.2'nin var olma sebebi tam budur — ve kural yazarına uygulandı.*** |

> 🔴 **ÜÇÜNCÜ EKSEN (sürüm 6'da eklendi): BAYRAK ADI ↔ SÖZLEŞME ALANI ADI.**
> Bu tablo şimdiye kadar yalnız **kod ailelerini** izliyordu; bir denetim turu bu ekseni
> **hiç kapsamadığını** gösterdi ve tam da o boşlukta bir çakışma doğdu: sürüm 5'te
> `netlestirme_yaniti` **hem bayrak** (`…=off`) **hem `AskRequest` alanı** (`body.…`) olarak
> yazılmıştı.
>
> **Ölçülen zarar üç yerde:** (a) §C/10'un *"ölü bayrak → 0"* denetimi bayrak adlarını
> **grep'le** arıyor — ad her alan kullanımına da isabet edeceği için ***"bu bayrak bağlı
> mı?"* sorusu cevaplanamaz** → `test_bayrak_kaydi.py` **yanlış-pozitif** · (b) test dosyası
> adı **belirsizleşir** (*bayrağı mı alanı mı sınıyor?*) · (c) ve bu tablo **fark edemezdi**.
>
> **KURAL:** *bir bayrak adı ile bir sözleşme alanı adı **asla aynı olamaz**.* Bayrak
> **davranışı açar** (`…_kapanisi`, `…_dili`, `…_yoneticisi`), alan **veri taşır**
> (`…_yaniti`, `…_secimi`). **Uygulanan düzeltme:** bayrak `netlestirme_kapanisi`, alan
> `netlestirme_yaniti` — 0.5b.
> **Kapısı:** `tests/test_yol_haritasi_butunlugu.py` (D5) `FLAG_REGISTRY` ∩
> `{schemas.py'nin tüm alan adları}` = **∅** olduğunu doğrular.

## §E.3 · *"Kayıt"* aşırı yüklemesi — hangisi hangisi

`tools.KAYIT` = **araç kaydı** · `MetricDefinition` = **metrik kaydı** · `FLAG_REGISTRY` =
**bayrak kaydı** · `DecisionRecord` = **Karar Kaydı** · `contract_log` = **makbuz**.
Test adları bunları **açıkça** taşır (`test_arac_kaydi` · `test_metrik_kaydi` · …).

## §E.4 · *"Tazelik"* iki kavram

**veri tazeliği** (`freshness` alanı · `tazelik` bayrağı · 1.7 · II-F.4) ↔ **ölçüm artefaktı
tazeliği** (`nl_corpus_baseline.json` · 0.12). İkincisi bundan sonra **"taban tazeliği"**
diye yazılır.

---

# §F. DENEYİM: ÖLÇÜ ARACI · ERTELENEN · ÇÖZÜLMEYEN

> **Neden ayrı bir bölüm:** §C *"bitti ne demek"*i sayıyla tanımlıyor. Bu bölüm onun
> **dürüstlük yarısı**: deneyimi **hangi aletle** ölçtüğümüz (§F.1), **neyi bilerek
> ertelediğimiz ve nasıl geri döneceğimiz** (§F.2), ve **bu planın tamamı inse bile
> ÇÖZÜLMEYECEK olanlar** (§F.3). *Gizlenmiş bir varsayım, yanlış bir varsayımdan kötüdür.*

## §F.1 · Deneyim süiti — `lab/deneyim.py` *(yol haritasına İLK KEZ tanıtılıyor)*

> ⚠ **Ad alanı (§E.1):** bu araç **yürüyen planın `X` fazının** çıktısıdır — bu belgenin
> `FAZ …` numaralarından biri **değildir**. Aşağıda *"deneyim süiti"* diye anılır.

Sürüm 3 bu aracı **hiç tanımıyordu** (`grep -n "deneyim.py" DIMA-V1-YOL-HARITASI.md` →
**0**). Oysa çalışma ağacında duruyor (`backend/lab/deneyim.py`, **20.509 bayt**
@`c4b14d1`) ve **dört ölçüm aracının hiçbirinin sormadığı soruyu** soruyor:
***"bir KONUŞMA tatmin edici miydi?"*** — 13 senaryo, 7 sözleşme satırı.
**Doğru araç, doğru soru.** *(Diğer dördü: `nl_corpus` = erişim/cube · `nl_accuracy` =
etiketli doğruluk · `eval` = regresyon kilidi · `konusma_senaryolari` = tur mekaniği.)*

| Sözleşme satırı | Bu belgedeki maddesi |
|---|---|
| `S1·çapa` · `S3·süreklilik` · `S7·geri dönüş` | **0.5** + **0.5b** |
| `S2·anlat` (*≥3 olgu + anlatı + ≥2 chip*) | **0.23** — 🔴 aşağıdaki kör nokta |
| `S5·belirsizlik` (*tahmin yok, soru var*) | **0.5b** (yarısı — bkz. `S9`) |
| `S6·makbuz` | — (bu turda dokunulmuyor) |

🔴 **SÜİTİN KÖR NOKTASI — ve neden K2 ile AYNI sınıf:** `deneyim.py` **API cevabını**
ölçüyor, **render'ı değil**. `ask.py:1750`'nin cevabında `S2`'nin istediği her şey
(`contribution`, `prescription`, `next_steps`) **DOLU** → süit **YEŞİL** raporlar; kullanıcı
ise `ReportPanel.tsx:185` yüzünden **hiçbirini görmez** (**0.23**). Bu, K2 kapısının
yanlış-pozitifinin **birebir aynı sınıfıdır** — ve iki bağımsız kapının aynı körlüğü
paylaşması, körlüğün **sınıfsal** olduğunu gösterir.

**TABAN DEĞERİ — §C'nin her ölçütü *"Bugün"* taşır, bu araç da taşımalı:**

| Koşum | Sonuç | Damga |
|---|---|---|
| **Çevrimdışı** (`rule`) | **34 ✅ · 1 ❌ · 56 ⊘** | `a5942c7` |
| **Canlı** (gemini→groq→xai→openrouter) | **33 ✅ · 2 ❌ · 56 ⊘** | `c4b14d1` |

**Matris seyrek ve bu TASARIM GEREĞİ:** 13 senaryo × 7 sözleşme = 91 hücre *(S8·S9·S10 eklenince **10 satır**)*, **56'sı ⊘** —
her senaryo her satırı ölçmez. ⚠ **Bunun sonucu bağlayıcı:** *senaryosu olmayan sözleşme
satırı ölçmez.* Aşağıdaki `S8`/`S9` **ölü doğmasın** diye her biri **hangi senaryoda
koşacağını yazıyor.**

**İKİ YENİ SÖZLEŞME SATIRI — `lab/deneyim.py`'ye eklenir (`S8` → 0.23, `S9` → 0.5b ile
AYNI commit):**
```
S8·görünürlük : cevabın taşıdığı her GÖVDE alanı RENDER edilebilir bir dala düşer
S9·kapanış    : netleştirmeye verilen cevap (TIKLAMA ve YAZMA) aynı rapora çıkar
```

| Satır | **Koşacağı senaryo** *(ölü doğuş yasağı — §A.2)* | Ölçtüğü |
|---|---|---|
| **`S8`** | *"neden düşük?"* → konuşma cevabı (`contribution` dolu, `result=None`) | Cevabın **her gövde alanı** için `ReportPanel`'de bir **render dalı** var mı — API'de dolu olması **yetmez** |
| **`S9`** | *"fire"* → ölçü netleştirmesi → **(a)** chip'e tıkla **(b)** *"fire olan"* yaz | **İki yolun da AYNI** `cube_query`'ye ve **aynı rapora** çıkması |

🔴 **`S8`/`S9` eklenmeden 0.23 ve 0.5b *"bitti"* sayılmaz** — çünkü ikisinin de kusuru
**bugünkü süitte YEŞİL görünüyor** (§F.1'in kör noktası). **Sözleşme satırı olmadan inen
madde, ölçülmemiş madde sayılır.**

> ℹ **Süitin ilk koşumu dört kusur çıkardı ve dördü de kapıya çevrildi** (`a5942c7`) —
> takip düzenlemesinin **taban soruyu değiştirmesi** (sessiz-yanlış) · *"geçen yılla
> kıyasla"* takipte **kimlik asimetrisi** · `compare_mode`'un **çekim varyantlarını elle
> sayması** · **dönem ifadesinin yer-durum eki** (*"son 6 ay"* ✅ / *"son 6 ay**da***" ❌).
> **Aracın kendisi kendini kanıtladı** — ve ölçütü **üç kez düzeltti**: *"eşiği tahminle
> ayarlama, **ÜRETEN MEKANİZMADAN türet**."*

## §F.2 · EK-T · **ERTELENEN AMA UNUTULMAYACAK: `t2_anlatici`**

> **Kullanıcı kararı:** *"şimdi değil ama nasıl yapılacağı ve planı unutulmasın, mutlaka
> sonra yapılsın."* Bu bölüm o taahhüdün **tam tarifidir** — bir *"sonra bakarız"* değil.

**Bugün nerede duruyor:** `features.yml` `t2_anlatici: "off"`. Kapalı olma gerekçesi
**doğruluk DEĞİL** — dosyanın kendi yorumuyla *"sıcak yola LLM çağrısı ekliyor"*, yani
**maliyet/gecikme**. Güvenlik makinesi **HAZIR**: `narration_guard.guvenli_anlatim`
fail-closed, ±%2, 20 test; çağrı `planner.Planlayici` üzerinden
(`Butce(adim=2, saniye=15.0, sorgu=0)`), **makbuzlu**; `summary`/`facts` **asla silinmez**.

**ÜÇ SERT ÖN KOŞUL** *(sürüm 3 yalnız ikincisini biliyordu)*:
1. 🔴 **`0.10b` (görünen adlar) inmiş olmalı** — aksi hâlde LLM `toplam_fire_kg` etrafında
   cümle kurar; **akıcı ama iç adlı bir cümle robotikliği kaldırmaz, üstüne para ödetir.**
2. **`0.16` (ölçüm bütçesi) inmiş olmalı** — ücretsiz kota A/B'yi kaldırmıyor.
3. **`0.22` (`UnboundLocalError`) inmiş olmalı** — aynı orkestrasyon yolundaki duran hata.

**NASIL AÇILACAK — FAZ 0.4 deseni, birebir:**
1. `_anlati_system()` prompt'unu gözden geçir. Bugünkü hâli bir **rapor sesidir**
   (*"2-4 cümle, madde yok, başlık yok, emoji yok, belirsizlik varsa sus"*), **sohbet sesi
   değil**. **5.17**'nin ton kararlarıyla hizala.
2. Bayrağı **tek test kullanıcısında** `alpha`'ya aç — **global değil**.
3. **A/B koş:** (a) tur başına eklenen gecikme p50/p95 · (b) sağlayıcı maliyeti/tur ·
   (c) `konusma_senaryolari` + `lab/deneyim.py` gerilemesi · (d) **guard'da düşen cümle
   oranı** (`answer.py`'nin `_log.info`'su bunu **zaten yazıyor**).
4. **Kazanç/kayıp YAZILIR**, sonra global karar. Ölçmeden açmak, [KANIT §8.3]'ün kaydettiği
   `elektrik` hatasının tekrarı olur.
5. **EK E'ye işlenir** — bugün orada `MEVCUT` satırında duruyor; açıldığı gün kendi fazına
   taşınır ve **ölçüm tarihi** yazılır.

🔴 **KAPSAM SINIRI — dürüstçe (ölçüldü, §C çerçevesini düzeltir):** açıldığında bile
`answer.py`'nin iki kapısı yüzünden **yalnız** `result`/`kpi` **ve dolu `facts`** olan
turlara dokunur. **Netleştirmenin %25,9'una YAPISAL OLARAK ulaşmaz** — ve **ulaşmamalıdır**
(KD-21). Yani:

> **`t2_anlatici` *"chat akmıyor"* şikâyetini ÇÖZEN madde DEĞİLDİR.** Turların ~%69,8'inde
> *"süssüz ama doğru"*yu *"akıcı ve doğru"* yapan bir **iyileştirmedir**. Şikâyeti çözen
> maddeler **0.23 · 0.5b · 0.10b · 5.17**'dir.

Sağlayıcı kesintisinde guard fail-closed olduğu için cevap sessizce *"süssüz ama doğru"*ya
döner — **bu kasıtlıdır.**

## §F.3 · **BU PLANA RAĞMEN ÇÖZÜLMEYENLER — peşinen kabul**

> Dış denetim bu maddelerin yol haritasında **karşılığı olmadığını** söyledi; haklıydı.
> Bunlar **eksik değil, sınırdır** — ve sınırı yazmayan plan, sınırı olmadığını iddia eder.

| # | Çözülmeyen | Neden | Ev |
|---|---|---|---|
| **1** | ⟳ **KISMEN ÇÖZÜLDÜ (`ce9ee43`) — satır tazelendi.** **Aşama akışı İNDİ**: `ask.py:3509` `StreamingResponse` + `media_type="text/event-stream"` — **SSE, WebSocket değil** (§D.1'in hükmü **tutuldu**). ⚠ **Kalan boşluk daraldı:** aşama **olayı** var, **harf/token akışı** yok — *"yazıyor…"* hissi hâlâ eksik | Token akışı, cevabı **üretirken** yayımlamayı gerektirir; bugün cevap **önce tamamlanıyor**, sonra gönderiliyor | **AJ3** *(turu LLM yönetince cevap zaten parça parça oluşur — token akışı onun **yan ürünü** olur, ayrı bir iş değil)* |
| **2** | ⟳ **→ §G/AJ3 bunu ölçüme açıyor.** **Netleştirme oranı DÜŞMEZ (%25,9 sabit)** | 🔴 **Kısıt gereği, KASITLI.** Plan bunu *azaltmıyor*, **daha iyi sormaya** çeviriyor (§C/3: `CLARIFY:dönem` **değişirse KIRMIZI**) | **5.17** + **0.5b**. ⚠ Kullanıcıya **böyle anlatılmalı**, yoksa *"hâlâ soruyor"* der |
| **3** | 🔴 **→ §G/AJ4.** **Oturumlar-arası hafıza yok.** `ConversationMessage` **yazılıyor**, `/ask` **hiç okumuyor**; `Baglam` penceresi bilinçle **iki tur** | Kullanıcı ikinci gün geldiğinde sistem onu **tanımıyor** | **II-F** |
| **4** | 🔴 **→ §G'NİN KONUSU.** **Sistem hâlâ soru→rapor makinesi.**** Kendiliğinden hatırlatmaz, *"geçen hafta sorduğun şey değişti"* demez | Bir sohbet ortağının **en ayırt edici** davranışı budur ve v1'de **yok** | **5.9** (digest) + **II-F** (brifing) |
| **5** | **İki komposer ayrımının öğrenme maliyeti** | Sol panel dürüstleştirmesi **yanlış vaadi** kaldırır; **ayrımın kendisini** kaldırmaz (kullanıcının iki kez vurguladığı karar) | **FAZ 7** |
| **6** | 🔴 **K2/S2 körlüğü bir örnekten ibaret OLMAYABİLİR** | **0.23** bir **vakayı** kapatıyor; **kapının kendisini** kör noktasız yapmak **0.14**'ün tam kapsamı. İki bağımsız kapının **aynı** körlüğü paylaşması, körlüğün **sınıfsal** olduğunu gösteriyor | **0.14/K2(c)** + **§F.1/S8** |
| **7** | 🔴 **İşaret zamiri önceki sonucun bir SATIRINA çözülemiyor** — *"o ayı makine bazında aç"* | **Deneyim süitinin BİLEREK AÇIK KIRMIZI'sı** (`a5942c7`, süitin **tek ❌**'i). *"Yeni bir bağımlılık sınıfı ister"* — cevap **satır düzeyinde** çapa taşımalı. 0.5b **cevabın tamamına** çapa atar, **bir satırına değil**. ⚠ **Kapatılmamış bir bulguyu yeşile boyamak süitin varlık nedenine aykırı** — bu yüzden kırmızı **bilerek açık bırakıldı ve burada kayda geçiyor** | **II-D** *(sütun/satır çapası — `DrillResponse` ile aynı aile)*. **0.5b'nin İLAN EDİLMİŞ SINIRI:** çapa **cevap düzeyindedir** |
| **8** | ⚠ **`is_period_only` hâlâ 0 çağıran** | `a5942c7`: *"`needs_period` artık üretimde **1 çağırana** sahip ama **KLARİFİKASYON KAPISI OLARAK DEĞİL** — bir cevaplanabilirlik yordayıcısı olarak."* Yani −0.5c tuzağı **tam tasarlandığı gibi patladı** ve yarısı hâlâ açık | **0.14/K2** *(yetim fonksiyon = yetim alan ile aynı sınıf)* |

---

# §G. AJAN KATMANI — **iki yürütücü, tek zemin, ÖLÇÜLEN kıyas**

> **KULLANICI KARARI (2026-08-03, bağlayıcı):** *"Tek bir şey seçmeyeceğiz — ikisini de
> geliştirip kıyaslayıp test edeceğiz. Hem geliştirici test edecek hem de UI'da yollar
> açılıp kapanıp manuel test edilecek. **Geliştirme maliyetini de kabul ediyoruz.**"*
> Ve: *"Plan çok iyi, **bunu korumak istiyorum** — ama bu mevzuları da işlemek, geliştirmek,
> **test ederek görmek** istiyorum."*
>
> 🔴 **Bu bölüm planın hedefini genişletiyor** — *"rapor makinesini mükemmelleştir"*den
> *"konuşan ortak da OLABİLİR Mİ, ölçelim"*e. **Ama hiçbir maddeyi silmiyor.**

## §G.0 · Neden bu bölüm var — §F.3'ün dört satırının cevabı

§F.3 dürüstçe yazmıştı: *"Sistem hâlâ soru→rapor makinesi. Kendiliğinden hatırlatmaz,
uyarmaz … Bir sohbet ortağının **en ayırt edici** davranışı budur ve v1'de **yok**."*
Kullanıcının ilk isteği ise *"insan gibi konuşacak, anlayacak"* idi. **Bu bölüm o boşluğu
kapatmayı DENER ve denemenin kendisini ölçer.**

**Kullanıcının iki ayrı şikâyeti, ölçüldüğünde TEK kararın iki ucu çıktı:**

| Şikâyet | Ölçülen kusur | Sonucu |
|---|---|---|
| *"Bin bir türlü dilsel şey var, hepsini nasıl bitireceğiz?"* | **LLM makineye anladığını SÖYLEYEMİYOR** — Intent-JSON şeması `cube · measures · dimensions · filters · order · limit`; **`compare` orada HİÇ YOK** (`llm.py:307-341` @`88bde2a`) | Her yeni anlam = **7 dosyada kod** (5.6). Kural döngüsü **mekanik olarak** bitmez |
| *"Karşımda anlayan bir şey yok, hâlâ makine"* | **LLM insana serbestçe KONUŞAMIYOR** — `narration_guard` yalnız **sayılı** cümleyi koruyor; **rakamsız iddia** korumasız (KD-21) | Konuşmayı LLM yönetemiyor → her yeni ifade = **yeni kalıp sözlüğü** (5.3) |

**İkisi de tekil çözüm gibi görünüyor çünkü ikisi de aynı tekil kararın belirtisi:**
bugün **tek bir değişmez iki işi birden yapıyor** — *"sayıyı küp koyar."* Bu cümle hem sayıyı
koruyor **hem de LLM'in konuşmasını yasaklıyor**. 🔴 **Ölçülmüş olan yalnız birincisi.**

## §G.0b · 🔴 **KUZEY YILDIZI — bu bölüm bittiğinde cevaplanacak SORU**

> **Kullanıcının kendi cümlesi (2026-08-03), ve bu belgenin asıl hedefinin tanımı:**
> *"Bana **son 6 aylık ciro** ve **her bir satış üreten ürün kalemiyle mukayesesi** ve
> **bunların verimliliği ve karlılıklarını** analiz ettiğin **bir rapor yaz**."*
>
> *"Bunu **anlamadan, anlamlandırmadan** yapması mümkün değil. Sistem zaten asıl amacı bu
> noktaya varmak — **hem güvenli kesin yanıtlar hem konuşan, anlayan, yöneten agentic
> insani sistem**."*

**Bu cümle bir hedef değil, bir TESTTİR** — ve parçalandığında hangi katmanın eksik olduğunu
tam olarak gösteriyor:

| # | İstenen | Gerektirdiği | Bugün @`88bde2a` |
|---|---|---|---|
| **A** | Bunu **adımlara ayırmak** | **Ayrıştırma** — bir plan | 🟡 **YAZILMIŞ, HİÇ AÇILMAMIŞ** — `planner.Planlayici.sec()`, dört kapılı; bayrak `agent_plan_secimi` **`off`**, **hiç ölçülmedi**, ve **açılırsa çöküyor** (**0.22**) |
| **B** | Her adımı **ifade etmek** (mukayese · ölçü×ölçü · türev metrik) | **Dilin genişliği** | 🔴 **EN BÜYÜK BOŞLUK** — `karlilik` **var** (`packs/modul/turev/karlilik.yml`), `blend` **var** (CubeQuery alanı), ama 🔴 **Intent-JSON hiçbirini SÖYLEYEMİYOR** |
| **C** | Sonucu **bir rapora** dönüştürmek | Artefakt derleme | 🟢 **büyük ölçüde var** — `report.compose_report()` + **5.13b** rapor yapısı |
| **D** | Eksik bilgiyi **sorup HATIRLAMAK** (*"verimliliği adam-saat üzerinden mi?"*) | **Diyalog yönetimi** | 🔴 **YOK** — §G.0c |

> 🔴 **VE KUZEY YILDIZININ KENDİSİ, KATALOG TAVANINI ÖRNEKLİYOR — dürüstçe kayda geçiyor.**
> Ölçüldü @`88bde2a`: **`"verimlilik"` katalogda HİÇ YOK** (`grep -rl verimlilik
> demo/packs/**/*.yml` → **0 dosya**). `karlilik` **var** (`packs/modul/turev/karlilik.yml`,
> jenerik türev metrik — *"yeni ERP yalnız kanonik yapı taşlarını bağlar, kâr/marj mantığı
> OTOMATİK gelir"*), ama **verimlilik yok.**
>
> **Sonucu bağlayıcı:** §G'nin **hiçbir maddesi** bu boşluğu kapatmaz — *anlama, katalogda
> olmayanı söyletmez.* Kuzey yıldızı cümlesinin **tam olarak çalışması** için
> **`3.1` (sahiplik turu) · `3.2` (R1'i kapat) · `2.5` (`MetricTarget` + `target:`)**
> zincirinin o tenant'ın kataloğunda **verimliliği tanımlamış olması** gerekir.
> 🔴 **Yani kuzey yıldızı üç fazın KESİŞİMİDİR: §G (anlama) × FAZ 2-3 (kapsam) × 5.13b
> (rapor).** Bunu yazmamak, §G bittiğinde *"neden hâlâ olmuyor"* sorusunu doğururdu.
> *(Ve bu, `KAT-3`'ün dördüncü uygulaması: **kapsam, anlamanın enabler'ıdır**.)*

🔴 **Ve B'nin kökü `compare` ile BİREBİR AYNI ÇIKTI** — ölçüldü, `MIMARI.md:2078`:
> *"**Kapsam yalnız beş çekirdek alan.** `order`/`limit`/**`blend`** bilerek dışarıda."*

Yani `blend` **eksik değil, İFADE EDİLEMEZ**; `compare` **eksik değil, İFADE EDİLEMEZ**.
**İkisi de aynı duvarın iki tuğlası** ve **AJ2 ikisini birden kaldırıyor** — bu, AJ2'nin
kapsamını genişletmiyor, **gerçek boyutunu gösteriyor**.

## §G.0c · 🔴 **ATLANMIŞ KATMAN — ve bu, LLM eksikliği DEĞİL**

> **Kullanıcının gözlemi (ve haklı):** *"Open-source Türkçe o kadar fazla chatbot var ki…
> **LLM olmadan bile mükemmel konuşan** open-source Türkçe chatbotlar var. Onlar kadar bile
> konuşamıyoruz."*

**Teşhis:** o botların cevap uzayı **sonludur** ve her cümlesini bir insan yazmıştır —
Dima'nınki **sonsuz**, o cümleler önceden yazılamaz. **Ama onları akıcı yapan şey şablonlar
değil: DİYALOG YÖNETİCİSİ.** Ve o katman **1990'lardan beri deterministiktir** — hiçbiri LLM
istemez.

| Diyalog yeteneği | Onlarda | **Dima'da @`88bde2a`** |
|---|---|---|
| **Slot durumu** — hangi bilgi eksik, ne soruldu | var | 🔴 netleştirme dallarının **10'u** `cube_query=None` döner (**0.5b**) |
| **Devam** — cevap gelince özgün niyet **kaldığı yerden** koşar | var | 🔴 cevap **yepyeni soru sanılır** (`KURAL_TAZE`) |
| **Onarım** — *"hayır, şubat demiştim"* → slot **düzeltilir** | var | 🔴 **baştan başlar** |
| **Temellendirme** — *"Tamam, mart fire — hangi kırılımda?"* | var | 🔴 *"Neyi karşılaştırmak/görmek istediğini anlayamadım"* = **form doğrulayıcı** (**5.17**) |
| **İnisiyatif** — *"bunu her ay görmek ister misin?"* | var | 🔴 **yok** (§F.3/4) |

🔴 **Ve en can alıcı bulgu: `0.5b` aslında SLOT-FILLING'i sıfırdan icat ediyor.**
Çözülmüş bir problemi yeniden keşfediyoruz — **kötü olduğu için değil, adlandırılmadığı
için**: madde doğru, ama **bir katmanın parçası olduğu yazılı değil**, bu yüzden kardeşleri
(devam · onarım · temellendirme · inisiyatif) **hiç yazılmadı**.

> **BUNUN SIRAYA ETKİSİ — ve sürüm 6'nın ilk taslağını DÜZELTİYOR:**
> Diyalog katmanı **deterministiktir**: ne LLM çağırır, ne sayı üretir, ne şema iddiası
> kurar. Yani **güven modeline HİÇ dokunmaz** ve **kıyas turu bile gerektirmez**.
> → **AJ1'den (iddia kapısı) ÖNCE gelir.** Üç gerekçe:
> 1. **Risksiz** — gerileme yüzeyi yok
> 2. **Şikâyetin büyük kısmını O çözüyor** (*"sorduğunu hatırlamıyor" · "robotik" · "benimle
>    konuşmuyor"*)
> 3. 🔴 **Katman 3'ün ÖLÇÜM ZEMİNİ olur:** LLM yöneticiyi açtığınızda kıyaslayacağınız taban
>    *"hiç diyalog yönetimi yok"* değil, ***"iyi bir DETERMİNİSTİK diyalog yöneticisi"***
>    olur. **Doğru kıyas budur** — aksi hâlde B, A'nın en zayıf hâline karşı yarışır ve
>    kazanması bir şey kanıtlamaz.

## §G.0d · Dört katman, dört kapı — **hiçbiri ötekinden ödün istemiyor**

```
Katman 3 · LLM        →  anlar · ayrıştırır · cümle kurar        [kapı: app/iddia.py]
Katman 2 · DİYALOG    →  slot · devam · onarım · temellendirme   [kapı: deterministik testler]
                          · inisiyatif
Katman 1 · KÜP        →  SAYIYI KOYAR                            [kapı: narration_guard]
Katman 0 · DÖRT KAPI  →  kayıt · yetki · det-önce · bütçe        [kapı: planner.py]
```

| Katman | Ne yapar | Kapısı | Durum @`88bde2a` |
|---|---|---|---|
| **3 · LLM** | anlar · ayrıştırır · cümle kurar | `app/iddia.py` | 🔴 **kapı yok** → AJ1 |
| **2 · Diyalog** | slot · devam · onarım · temellendirme · inisiyatif | deterministik testler | 🔴 **katman yok** → **AJ0b** |
| **1 · Küp** | **sayıyı koyar** | `narration_guard` ±%2, 20 test | ✅ **kurulu, DOKUNULMAZ** |
| **0 · Dört kapı** | kayıt · yetki · det-önce · bütçe | `planner.py` | 🟡 **yazılmış, kapalı, kırık** → 0.22 + AJ3 |

🔴 **Ve bu, "ikisini birleştirmek" sorusunun cevabıdır: TAVİZ GEREKTİRMİYOR — çünkü farklı
katmanlarda duruyorlar.** Güvenlik ve netlik **Katman 1**'de; onu kimse tartışmıyor.
Deneyimin çoğu **Katman 2**'de ve o katman **hiç risk taşımıyor**. *"Anlamak"* ile
*"çalıştırmak"* ayrı olduğu için, **anlamayı LLM'e vermek kesinliği bozmuyor** —
MIMARI §11.6d'nin kendi tezi: ***"SEÇİM ≠ ÇALIŞTIRMA. Seçicinin yanılması yeni bir risk
açmaz."***

## §G.1 · Kilidi açan karar: **değişmez İKİYE ayrılır**

| # | Değişmez | Ne korur | Kapı | Durum @`88bde2a` |
|---|---|---|---|---|
| **1** | **Sayıyı KÜP koyar** | rakam | `narration_guard` ±%2, fail-closed, **20 test** | ✅ **kurulu — DOKUNULMAZ** |
| **2** | **LLM'in her İDDİASI şemaya karşı doğrulanır** | cümle | `app/iddia.py` | 🔴 **YOK — eksik olan tek şey** |

`narration_guard`'ın **kendi docstring'i** bu ayrımı zaten itiraf ediyor:
*"Sayı **İÇERMEYEN** cümleler geçer: bu kapı **sayı uydurmasını** engeller, **üslubu
değil**."* İkinci kapı kurulduğu an **LLM serbestçe konuşabilir ve sistem hâlâ fail-closed
kalır** — çünkü artık iki farklı şey **ayrı ayrı** korunur.

> ⚠ **Bu, MIMARI §4'ün değişmezini GEVŞETMİYOR — İKİYE BÖLÜYOR.** Sayı yolu birebir aynı
> kalır (küp → guard → seal). Değişen tek şey: *"cümleyi kim kurar"* sorusunun cevabı artık
> **ayrı bir kapıya** bağlanıyor, sayı kapısının yan ürünü olmaktan çıkıyor.
> **Bu ayrım `MIMARI.md`'ye `⟳ YÜRÜRLÜKTE` olarak işlenir** (FAZ −1 mekanizması) — çünkü §4
> bugün ikisini tek kural sayıyor ve **o hâliyle bu bölümle çelişir**.

---

### AJ0 · 🔴 **KISA DEVRE YASAĞI** — MIMARI §5'in **18. yasağı**  [bayraksız: değişmez] · **ÖNCE BU İNER**
**NEDEN** Kullanıcı *"mart ayında ciro şubata göre nasıl değişti"* yazdı; sistem
*«degisti» yerine «egitim» mi demek istedin?* dedi. **Kök neden bir yazım hatası değil, bir
MERDİVEN hatası:** `ask.py:2687`'nin yazım-benzerliği chip'i **`source=None`** ile **return
ediyor** (yani **cevap üretmiyor**), ama Discovery `:3389`'da — yani **cevap üretebilecek bir
yolun önünü kesiyor**. Eskiden bu soru merdivenden düşer, Discovery'ye varır ve **bir sayı
getirirdi**.
🔴 **Bu tek bir hata değil, bir SINIF** — beş örneği ölçüldü:

| # | Cevapsız dal (`source=None`) | Önünü kestiği |
|---|---|---|
| 1 | yazım-benzerliği chip'i (`ask.py:2687`) | **Discovery** ← kullanıcının vakası |
| 2 | `ReportPanel` `it.result \|\| it.kpi` | `contribution`+`prescription` render'ı (**0.23**) |
| 3 | `followup.sinifla` yalnız `structural_followup` içinde | ham thread'lerde konuşma türleri (**5.0/K3**) |
| 4 | `answer.py`'nin `result is None → return`'ü | `t2_anlatici`'nin netleştirmeye ulaşması (**§F.2**) |
| 5 | `next_steps` altında `!item.contribution` | gezinme chip'leri — **bu BİLİNÇLİ, ama aynı şekil** |

Ve kodun **kendi yorumları aynı hatayı üç kez kaydetmiş**: `bunu→gunu` (`:1788`) ·
`bundan→unvan` (`:2116`) · `enerji kaynagi→enerji tep` (korpus). **Her seferinde çağrı
yerinde yamalanmış, kapının kendisinde hiç.**
**NE** backend: **`MIMARI.md` §5'e 18. yasak** *(bugün 17 var — sayıldı)* │ sözleşme:
`explain.path` bir **merdiven izine** çevrilir (hangi basamak karar verdi, **hangileri
atlandı**) — alan **zaten var** (`schemas.py:240`) ve **0.9'un yetim listesinde** │
frontend: iz görünür (0.23'ün render dalında)
**NASIL** Mekaniği: **`source=None` dönen bir dal RETURN ETMEZ** — kendini bir **aday**
olarak kaydeder, merdiven devam eder, sonunda **en iyi sonuç** seçilir. Merdiveni yalnız
**iki şey** bitirebilir: **pozitif bir cevap**, ya da kullanıcının **açık `yol_siniri`**'si
(Faz F2 — **zaten var**, `AskRequest.yol_siniri`, frontend'de 3 konumlu).
🔴 **Bu nüans kritik: kural Discovery'yi herkese yeniden AÇMIYOR.** Kullanıcı *"yalnız
deterministik"* dediyse yine kesilir — **ama kullanıcı öyle dediği için, bir yazım tahmini
öyle dediği için değil.**
**KAPI** `tests/test_kisa_devre_yok.py` (**tuzak testi**, `test_beyanlar_curumesin.py`
deseni): Discovery'nin üstünde `source=None` ile **return eden her dal**, gerekçesi yazılı
bir **muafiyet listesinde** olmak zorunda; yeni bir tane eklenirse **CI kırmızı**.
\+ 🔴 **Yeni metrik: *"cevapsız kesme oranı"*** — cevap üretmeyen bir basamağın karar
verdiği **ama altında hâlâ çalışabilir basamak bulunan** turların oranı. `nl_corpus` bunu
**bugün sayabilir**, şirket başına. *Bu sayı, bu hata sınıfının kendisidir — ve bugün kimse
ölçmüyor.*
**SONUÇ** Bir hata **sınıfı** kapıya bağlanır, **örneklerine** değil — kullanıcının
*"bunları tek tek girerek nasıl bitireceğiz"* sorusunun **bu yarısı biter**.
🔴 **Ve AJ2'nin ölçüm aletini BEDAVAYA kurar:** kısa devreler kalktığı an, deterministik
yolun **ifade edemediği** her tur Discovery'ye **ulaşır ve orada kaydedilir**. MIMARI'nin
kendi cümlesi: *"Discovery bir hata değil, bir **sinyaldir** … her biri bir **terfi
adayıdır**."* → **terfi kuyruğu, AJ2'nin ihtiyaç duyduğu «ifade edilemezlik» listesinin ta
kendisi olur.**
**GERİ AL** 🔴 **Geri alınmaz — MIMARI §5'e giren bir yasaktır.** Muafiyet listesine bir dal
eklemek **geri alma değil, gerekçeli istisnadır** ve listede **görünür** kalır.

> **MIMARI §5'e girecek satır (18.):**
> ⛔ ***Cevapsız bir dalla cevaplı bir yolu kesme.*** *Bir dal `source=None` dönüyorsa
> **henüz cevap üretmemiştir**; kendisinden geniş bir yolu (Intent-JSON · planlayıcı ·
> Discovery) kesmesi kullanıcıya **daha kötü bir cevabı garanti eder**. Merdiveni yalnız
> **pozitif cevap** ya da **açık `yol_siniri`** bitirir.*
> *Ölçüldü: `değişti→eğitim` · `bunu→gunu` · `bundan→unvan` · `enerji kaynagi→enerji tep`.*

---

### AJ0b · ⭐ **DİYALOG YÖNETİCİSİ** — atlanmış katman  [bayrak: `diyalog`] · 🔴 **§G'NİN İLK MADDESİ**
**NEDEN** §G.0c'nin ölçümü: **LLM'siz Türkçe botların 1990'lardan beri sahip olduğu beş
yetenek Dima'da YOK** — ve beşi de **deterministik**. Kullanıcının *"onlar kadar bile
konuşamıyoruz"* gözlemi **haklı ve sebebi LLM değil**.
🔴 **Ve `0.5b` bu katmanı SIFIRDAN İCAT EDİYOR** — çözülmüş bir problemi (slot-filling)
yeniden keşfediyoruz. Madde **doğru**, ama **bir katmanın parçası olduğu yazılı olmadığı
için** kardeşleri hiç yazılmadı.
**NE** backend: **`app/diyalog.py`** — beş yetenek, **tek modül, saf fonksiyonlar**
(`context.py` felsefesi) │ sözleşme: `AskResponse.diyalog_durumu: dict | None`
(`{acik_slotlar, sorulan, dolu, tur_no}`) — **`bekleyen_netlestirme`'nin (0.5b) genelleşmiş
hâli** │ frontend: slot durumu **görünür** (kullanıcı *"neyi bekliyor"* görür)

| # | Yetenek | Bugünkü kusur | Bu maddede |
|---|---|---|---|
| **1** | **Slot durumu** | 10 dal `cube_query=None` | 🟢 **`0.5b` BU KATMANIN İLK PARÇASI** — taşınmıyor, **adlandırılıyor** |
| **2** | **Devam** — cevap gelince özgün niyet kaldığı yerden koşar | `KURAL_TAZE` yepyeni soru sanıyor | ➕ **YENİ** |
| **3** | **Onarım** — *"hayır, şubat demiştim"* | baştan başlar | ➕ **YENİ** |
| **4** | **Temellendirme** — *"Tamam, mart fire — hangi kırılımda?"* | form doğrulayıcı | 🟢 **`5.17`'nin metin-şekli kuralı BU KATMANIN parçası** — *"önce ne anladığını söyle, sonra sor"* |
| **5** | **İnisiyatif** — *"bunu her ay görmek ister misin?"* | yok (§F.3/4) | ➕ **YENİ** — ⚠ **`5.1` (`tur_takip`) onun motoru**; inisiyatif **öneri üretir**, `onay_akisi` (6.1) uygular |

**NASIL** 🔴 **Sıfırdan yazılmıyor — VAR OLANLAR BİR KATMAN OLARAK ADLANDIRILIYOR ve
tamamlanıyor.** `0.5b`'nin `netlestirme.birlestir` saf fonksiyonu **çekirdek**;
`context.py`'nin `Baglam`/`KURAL_*` makinesi **devam ve onarımın zemini** (19 altın vaka,
testli, bugün **ölü** — 0.5). ⚠ **Hiçbir madde silinmiyor, hiçbiri taşınmıyor** — 0.5b ve
5.17 **yerlerinde kalır**, bu madde onları **bir katman olarak birbirine bağlar** ve **üç
eksik kardeşi ekler**.
**KAPI** `tests/test_diyalog.py` (**yeni**): **devam** — netleştirme cevabı sonrası özgün
niyet **korunur** (`KURAL_TAZE` ateşlenmez) · **onarım** — *"hayır, şubat demiştim"* **slotu
düzeltir**, baştan başlamaz · **temellendirme** — her netleştirme **ne anlaşıldığını önce
söyler** (5.17'nin kapısıyla ortak) · **inisiyatif** — öneri **yalnız** `onay_akisi`'ndan
geçer, **kendiliğinden yazma YOK**.
🔴 `lab/deneyim.py`: **`S1·çapa` · `S3·süreklilik` · `S7·geri dönüş` · `S9·kapanış`** —
**dördü birden yeşile döner**; bugünkü taban **34 ✅ / 1 ❌ / 56 ⊘** (§F.1).
🔴 `lab/nl_corpus.py --kapi`: **gerileme YOK** — bu katman **cevap üretmiyor**, cevabın
**etrafını** yönetiyor.
**SONUÇ** Dima, o açık kaynak botların **konuşma mekaniğini yakalar** — üstüne **sonsuz cevap
uzayı** ve **makbuz** koyar. Ve 🔴 **Katman 3'ün ölçüm zemini kurulur**: AJ3'ün kıyası
*"hiç diyalog yönetimi yok"*a karşı değil, ***"iyi bir deterministik diyalog yöneticisi"***ne
karşı yapılır — **doğru kıyas budur**.
**GERİ AL** `diyalog=off` → 0.5b ve 5.17 kendi bayraklarıyla, üç yeni kardeş **pasif**,
davranış **birebir bugünkü**. ⚠ **Güven modeline dokunmadığı için geri alma riski en düşük
olan §G maddesi budur** — ne LLM çağırır, ne sayı üretir, ne şema iddiası kurar.

---

### AJ1 · ⭐ **İddia kapısı** — `app/iddia.py`  [bayraksız: değişmez] · **B'NİN ÖN KOŞULU**
**NEDEN** §G.1'in **2. değişmezi**nin kapısı; **B yolunun tek bloklayıcısı**. Onsuz LLM'e
serbest konuşma vermek, kullanıcıya *"akıcı ama uydurma"*yı **göstermek** olur. Ölçülmüş
hata sınıfı (KD-21): *"Fire verisi 2019'dan beri kayıtlı"* (**şema iddiası**) · *"Bu tür
sorularda genelde ay bazlı bakılır"* (**dayanaksız norm**) · 🔴 *"İstersen tedarikçi
kırılımı da ekleyebilirim"* (**YETENEK iddiası** — o boyut yoksa kullanıcı *"olsun"* der ve
**sistem çuvallar**).
**NE** backend: `app/iddia.py::dogrula(metin, schema, sonuc) -> Rapor` — metindeki **her
katalog sözcüğü** `service.schema()`'da **bulunmalı**; **izinli söz-edimi beyaz listesi**:
`sor · var olanı öner · ne yaptığını açıkla · bilmediğini söyle`. **Yasak:** olmayan yetenek
vadetmek · sonuçta olmayan bir olguyu iddia etmek │ sözleşme: — (guard gibi, **çıkış
öncesi**) │ frontend: — (`api-only`, gerekçe: **cevap kapısı**)
**NASIL** 🔴 **`narration_guard` deseniyle BİREBİR** — ikinci bir doğrulama mimarisi
**icat edilmez**: cümle cümle çalışır, **düşen cümleyi düşürür** (metnin tamamını değil),
**fail-closed**, ve düşen oranı **loglar**. `narration_guard` sayıyı, `iddia` sözcüğü
doğrular; **ikisi de `answer.py::seal()`'in önünde**.
**KAPI** `tests/test_iddia_kapisi.py` — `narration_guard`'ın **20 testlik titizliğiyle**:
katalogda olmayan boyut adı geçen cümle **düşer** · yetenek vaadi **düşer** · izinli
söz-edimi **geçer** · sağlayıcı çökerse **fail-closed** (metin yok, cevap yine döner) ·
🔴 **düşen cümle oranı ÖLÇÜLÜR ve raporlanır** (kapı çok agresifse kullanılamaz hâle gelir —
`narration_guard`'ın kendi dersi: *"kullanılamayan kapı kapatılır ve o zaman hiç yoktur"*).
**SONUÇ** *"Senin gibi bir şey"*in önündeki **tek yapısal engel** kalkar. Fiyatı:
**~3-4 gün + korpus**.
**GERİ AL** Kapı **fail-closed** olduğu için geri alma = **B yolunu kapatmak**
(`tur_yoneticisi=deterministik`). Kapının kendisi A yolunda da **zararsız** çalışır
(A'nın metinleri deterministik → hiçbir cümle düşmez; **düşerse A'da bir kusur var demektir**
— ücretsiz bir denetim).

---

### AJ2 · ⭐ **CubeQuery formdan DİLE** — `referans` bileşimsel alanı + Intent-JSON şeması  [bayrak: `referans_dili`]
**NEDEN** 🔴 **Bir formun ALANLARI vardır — sonlu. Bir dilin OPERATÖRLERİ vardır ve onlar
BİRLEŞİR — sonlu bir gramer sonsuz soruyu karşılar.** Bugün `compare` bir **enum**:
```
bugün   : compare: "yoy" | "mom"                 → her yeni anlam = 7 dosyada kod
olacak  : referans: <ifade>                      → dönem · kohort · hedef · bütçe · sabit
                                                    HEPSİ aynı alanın DEĞERİ
```
Ve 🔴 **`compare` Intent-JSON şemasında HİÇ YOK** (ölçüldü @`88bde2a`: `llm.py:307-341`
alanları `cube · measures · dimensions · filters · order · limit`) → **LLM anladığını
söyleyemiyor**, dolayısıyla **her kıyas ifadesi deterministik yönlendiricinin bir kuralı
tarafından yakalanmak zorunda**. *Sonsuz kural döngüsünün mekanik sebebi tam burasıdır ve
sürüm 5'e kadar buna dokunan **tek madde yoktu**.*
**Sektör doğrulaması:** Cube `timeDimensions: [{dimension, dateRange, **compareDateRange**,
granularity}]` — kıyas **iki tarih aralığı**, bir enum değil; *"mart vs şubat"* ile *"bu yıl
vs geçen yıl"* **aynı alandan** geçiyor. dbt MetricFlow: kıyas bir **offset penceresi**.
Pyramid: *"LLM bir **reçete** üretir, motor derler — robot ne kadar güçlüyse LLM o kadar
karmaşık reçete üretebilir"* (yatırım **dilin genişliğine**, LLM'in zekâsına değil).
🔴 **VE AYNI DUVARIN İKİNCİ TUĞLASI: `blend`.** `MIMARI.md:2078` birebir: *"**Kapsam yalnız
beş çekirdek alan.** `order`/`limit`/**`blend`** bilerek dışarıda."* Yani kuzey yıldızının
*"her bir ürün kalemiyle **mukayesesi**"* isteği **`blend` olmadığı için değil, İFADE
EDİLEMEDİĞİ için** düşüyor — `compare` ile **birebir aynı kök**. **Bu madde ikisini birden
kaldırır.**
**NE** backend: `referans: {eksen, kaynak, hedef}` — `eksen ∈ {dönem, kohort, hedef, bütçe,
sabit}`; `yoy`/`mom`/`peer` **onun değerleri** │ sözleşme: **`compare` VE `blend` Intent-JSON
şemasına GİRER** (`llm.py`'nin biçim satırı genişler) + `CubeQuery.referans` │ frontend: kıyas
chip'leri **tek şablondan** üretilir (bugün `yoy` için özel dal var)
**NASIL** 🔴 **Doğrulayıcılar ZATEN kurulu ve bu yüzden alan genişletilebilir:**
`parse_cube_query` **katı beyaz liste** · `dry_plan` · **fan-out sertifikası** ·
`always_filter` fail-closed. *"LLM'e güvenmiyoruz"* mimarisi hazır — **dar olan, güvenilmeyen
şeyin SÖYLEYEBİLDİĞİ şey.** Göç MIMARI Faz 2 reçetesiyle: `compare`'ın 7 dokunuşu
**`referans`'a çevrilir**, eski `compare` **bir süre kabul edilir** (deprecation),
`referans_dili=off` → **birebir bugünkü**.
**KAPI** `tests/test_referans_dili.py`: `yoy`/`mom` **birebir aynı SQL** (eşdeğerlik önce
ölçülür — Faz 2 deseni) · *"mart ↔ şubat"* **adlı dönem kıyası** çalışır · Intent-JSON
`referans` üretebiliyor (canlı, `--live`) · 🔴 `lab/nl_corpus.py --kapi`: doğru-cube
**%93,2'den gerilemez**.
\+ 🔴 **YENİ RED KODU `R11` — «anlaşıldı ama İFADE EDİLEMEZ»** (bugün `R1..R10` var, **R11
yok** — doğrulandı). *Bu, planın hiçbir yerinde ölçülmeyen sayıdır: **anlam eksik olduğu
için kaç tur kaybediliyor.** Rakiplerin hiçbirinin yayımlamadığı sayı da odur* — ve **AJ0
indikten sonra terfi kuyruğu onu kendiliğinden doldurmaya başlar.**
**SONUÇ** *"A'yı B'ye göre"* ailesinin **tamamı** tek alanla kapanır: mart↔şubat ·
yoy · mom · peer · hedef↔gerçekleşen · bütçe↔fiili. **5.6 küçülür** (dördüncü enum değeri
yerine bir alan değeri). Ve **ifade tarafı LLM'e geçer**.
**GERİ AL** `referans_dili=off` → `compare` enum'u bugünkü 7 dokunuşuyla çalışır, Intent-JSON
şeması eski biçimde. **Davranış birebir.** ⚠ `R11` **kapalıyken de sayılır** (yalnız ölçüm).

---

### AJ3 · ⭐ **Turu LLM yönetir** — ikinci yürütücü  [bayrak: `tur_yoneticisi` = `deterministik|ajan`]
**NEDEN** Kullanıcının *"karşımda anlayan bir şey yok"* şikâyetinin doğrudan karşılığı.
Bugün LLM'in rolü **üç şeyle sınırlı**: Intent-JSON'un boşluklarını doldurmak · bitmiş bir
cevabı anlatmak (guard altında) · son çare ham SQL. **Üçünde de LLM konuşmuyor, FORM
DOLDURUYOR.**
**NE** backend: `tur_yoneticisi` — deterministik yol **önce koşar**, sonucu LLM'e **olgu
olarak** verilir, LLM **kararı verir**: `cevapla · netleştir · araç çağır · reddet`.
🔴 **Sayı hesaplamaz, SQL yazmaz — KONUŞMAYI yönetir** │ sözleşme:
`AskResponse.tur_yoneticisi: "deterministik"|"ajan"` (**makbuzda görünür**) │
frontend: **manuel test için görünür anahtar** (kullanıcının açık isteği)
**NASIL** 🔴 **B, A'nın KOPYASI DEĞİL — A'nın ÜSTÜNE oturur.** Maliyeti 2×'ten ~1,3×'e
indiren tek kısıt budur:
```
YANLIŞ : ask() → [A merdiveni]        ask_agent() → [B merdiveni]   ← her madde İKİ KEZ
DOĞRU  : ask() → [A merdiveni] → sonuç
                      └→ tur yöneticisi: deterministik | ajan        ← yalnız KARAR farklı
```
Böylece **FAZ 0/1/2/3'ün tamamı paylaşılır** (RLS · metrik kaydı · katalog · yetki); ayrışan
tek şey **tur yöneticisi**. `planner.Planlayici`'nin **üç kapısı zaten onu denetliyor**
(`_yetki_kapisi` · `_deterministik_once_kapisi` · `_butce_kapisi`) + araç kaydı = dördüncü.
🔴 **İKİ BAYRAK, BİR TANE DEĞİL:**
```
yol_siniri      : hepsi | küp+llm | yalnız küp   ← HANGİ basamaklar açık   (VAR, Faz F2)
tur_yoneticisi  : deterministik | ajan           ← KİM karar veriyor       (YENİ)
```
⚠ **`yol_siniri`'ne dördüncü değer EKLENMEZ** — bunlar iki ayrı kavram; tek alana bindirmek
**`compare` hatasının aynısı** olurdu (AJ2, bedeli az önce ölçüldü).
**KAPI** **§G.6'nın kıyas sözleşmesi** — ve o sözleşme **ikinci satır kod yazılmadan önce**
yazılır. Ek: `tur_yoneticisi=deterministik` iken **A birebir bugünkü** (V-5/E-3) ·
`agent_run` makbuzu **her ajan turunda** üretilir (0.22 ön koşul) · **AJ1 olmadan `ajan`
değeri açılamaz** (test bunu kilitler).
**SONUÇ** Ölçülebilir bir cevap: *"konuşmayı LLM yönetince deneyim gerçekten iyileşiyor mu,
ve neyi bozuyor?"* — **bugün bu bir tahmin, o gün bir sayı.**
**GERİ AL** `tur_yoneticisi=deterministik` → **A yolu birebir bugünkü**. B'nin kodu durur
ama **hiçbir turu etkilemez**. 🔴 **Bu, tüm §G'nin geri alma yoludur** — tek bayrak.

---

### AJ3b · ⭐ 🔴 **ÇALIŞIRKEN SORMA** — *"başlıyorum… bu arada şunu anlamadım"*  [bayrak: `calisirken_sorma`]
**NEDEN** Kullanıcının tarif ettiği hedef davranış (2026-08-03), ve **bu belgenin en somut
kabul testi**:
> *"Karmaşık promptu attığımda **«şimdi bunun için çalışmaya başlıyorum, bu arada şu kısmı
> tam anlamadım, açıklar mısın»** diyecek; açıkladığımda **«ha şimdi anladım»** deyip
> **kaldığı yerden** devam edecek."*

🔴 **Bugün bu YAPISAL OLARAK imkânsız** — netleştirme bir **SON DURAK**. Ölçüldü @`88bde2a`:

| Gereken | Bugünkü kod | Boşluk |
|---|---|---|
| Anladığın kısmı **başlat** | netleştirme dalları **18 yerde** `return _finish(AskResponse(…))` — **kısmi sonuç TAŞIMIYOR** | 🔴 tur ya cevaplar **ya** sorar, **ikisi birden asla** |
| **Çalışırken** sor | SSE olayları: `adim` · `tamam` · `hata` · `zaman_asimi` — **`soru` olayı YOK** | 🔴 akış ilerlemeyi bildirir, **soramaz** |
| Cevabı **bekle**, sonra devam | `AskJob.status ∈ {pending, running, completed, failed}` — **`awaiting_input` YOK** | 🔴 iş ya koşar ya biter; **duraklayamaz** |
| **Kaldığı yerden** devam | `AJ5b`'nin `ara_sonuclar`'ı **tur ömürlü** | 🔴 netleştirme gidiş-dönüşünde **çalışma kümesi ölür** → baştan başlar |

**NE**
* backend: **`AskJob.status`'a `awaiting_input`** + `bekleyen_soru` · `ara_sonuclar`
  (iş ömürlü, **tur ömürlü değil** — `AJ5b`'nin kısıtı **bu madde için gevşer**)
* sözleşme: **SSE'ye üçüncü olay — `soru`**: `event: soru\ndata: {id, metin, secenekler[], engelledigi_adim}`
  · `POST /ask/jobs/{id}/yanit` → `{id, deger|serbest}` · `AskResponse.kismi_sonuc: bool`
* frontend: konuşma kartı **hem akan adımları hem soruyu** gösterir; cevap **aynı kartta**
  verilir (**yeni panel YOK** — PK-1)

**── BEŞ KURAL, bağlayıcı ──**

| # | Kural | Gerekçe |
|---|---|---|
| **Ç-1** | **Anlaşılan adım BEKLEMEZ.** Soru **yalnız kendi adımını** durdurur; ondan bağımsız adımlar **koşmaya devam eder** | `AJ5b`'nin DAG'ı hangi adımın hangisine bağlı olduğunu **zaten biliyor** — bekleme kümesi **hesaplanır, tahmin edilmez** |
| **Ç-2** | 🔴 **Soru, KENDİ ADIMININ dışına taşamaz.** Bir netleştirme **tüm işi** iptal edemez — engellediği adım(lar) makbuzda **adıyla** yazılır | Aksi hâlde bugünkü *"her şey durdu"* davranışı yeni bir kılıkta geri gelir |
| **Ç-3** | **Cevap gelince İŞ DEVAM EDER, YENİDEN BAŞLAMAZ.** `ara_sonuclar` korunur; tamamlanmış adımlar **yeniden koşmaz** | `AJ0b`'nin *"devam"* yeteneğinin çok-adımlı hâli. **Yeniden koşmak makbuzu da çoğaltırdı** |
| **Ç-4** | 🔴 **"Ha şimdi anladım" DETERMİNİSTİKTİR.** Sistem, anladığı şeyi **kendi cümlesiyle geri söyler** (*"tamam — verimliliği adam-saat üzerinden alıyorum"*) ve bu cümle **`iddia.py`'den geçer** | `AJ0b`'nin *"temellendirme"*si + **AJ1**. *Onaylanmamış bir "anladım", anlaşılmamış bir sorudan kötüdür* |
| **Ç-5** | **Cevap gelmezse iş DÜRÜSTÇE eksik biter.** Zaman aşımında tamamlanan adımlar **sonuçlarıyla** döner, sorulan adım *"cevap bekleniyordu"* diye **beyan edilir** | Sessiz kırpma yasağı (`taranmayan_adlar` deseni) |

**NASIL** 🔴 **Üç mekanizma da ZATEN VAR, birleştirilmemiş:** `AskJob` (durum makinesi) ·
SSE kanalı (`ce9ee43`) · `bekleyen_netlestirme` (**0.5b**, durumsuz paket). Bu madde
**dördüncü bir mekanizma yazmıyor** — `AskJob`'a **bir durum**, SSE'ye **bir olay**,
0.5b'nin paketine **bir alan** (`engelledigi_adim`) ekliyor.
⚠ **`AJ5b`'nin *"tur ömürlü"* kısıtı burada bilerek gevşiyor** ve bedeli yazılı: iş ömürlü
çalışma kümesi **TTL ister**. Sınır: `_AKIS_AZAMI_SANIYE` — **yeni bir zaman aşımı politikası
icat edilmez**.
**KAPI** `tests/test_calisirken_sorma.py` (**yeni**): bağımsız adım soru sırasında
**koşmaya devam ediyor** (Ç-1) · soru **yalnız** kendi adımını durduruyor (Ç-2) ·
cevap sonrası tamamlanmış adım **yeniden koşmuyor** (Ç-3 — makbuzda **tek** kayıt) ·
*"anladım"* cümlesi **`iddia.py`'den geçiyor** (Ç-4) · zaman aşımında **kısmi sonuç +
dürüst beyan** (Ç-5) · `off` → **birebir bugünkü** terminal netleştirme.
🔴 `lab/deneyim.py`'ye **onuncu sözleşme satırı**:
```
S10·eşzamanlılık : sistem AYNI turda hem çalışır hem sorar; cevap işi DEVAM ettirir
```
**SONUÇ** Kullanıcının tarif ettiği davranışın **tamamı**: *"başlıyorum"* → adımlar akar →
*"şu kısmı anlamadım"* → cevap → *"tamam, şöyle alıyorum"* → **kaldığı yerden** devam →
rapor. **Ve her adımın altında `contract_id` durur.**
**GERİ AL** `calisirken_sorma=off` → netleştirme **terminal** (bugünkü davranış birebir),
`AskJob` yalnız dört durumla çalışır, SSE `soru` olayı **yayımlanmaz**. **0.5b ve AJ5b
etkilenmez.**

> ⚠ **VE BİR ÖLÇÜM DÜZELTMESİ:** `ce9ee43`'ün commit mesajı *"aşama akışı **+ steering**"*
> diyor, ama `grep -niE "steering|yonlendirme_mesaji" app/routers/ask.py` → **0 isabet**
> @`88bde2a`. **Akış indi, steering inmedi** *(ya da başka adla indi)*. Bu madde başlamadan
> **doğrulanır**: steering varsa Ç-1'in kanalı **zaten kurulu** demektir; yoksa bu madde onu
> da getirir. **`[DOĞRULANMADI]`**

### AJ4 · Oturumlar-arası süreklilik  [bayrak: `oturumlar_arasi_hafiza`]
**NEDEN** §F.3/3: `ConversationMessage` **yazılıyor** (`answer.py:228`) ama 🔴 **`ask.py`
onu HİÇ OKUMUYOR** (doğrulandı @`88bde2a`: `grep ConversationMessage app/routers/ask.py` →
**boş**). `Baglam` penceresi bilinçle **iki tur**. Kullanıcı ikinci gün geldiğinde **sistem
onu tanımıyor** — *"insan gibi konuşma"*nın ikinci yarısı budur.
**NE** backend: geçmiş turlar **olgu olarak** okunur │ sözleşme: — │ frontend: *"hakkımda
bilinenler"* görünürlüğü (II-F ile ortak)
**NASIL** Araştırmanın şartıyla: **kaynak izi · bayatlık işareti · çelişki bayrağı**.
🔴 **Ve ölçü/cube seçimine ASLA karışmaz** — `SunumTercihi` bu kuralı **zaten yazmış**;
hafıza **sunumu** etkiler, **anlamı** değil. *(Retrieval'lı hafıza [KANIT]'ta ölçüldü:
+14/−16 — bu yüzden **basit** kurulur.)*
**KAPI** `tests/test_oturumlar_arasi.py`: hafızadan gelen bir bilgi **cube/ölçü seçimini
değiştiremez** (fail-closed) · bayat kayıt **işaretli** gelir · `off` → birebir bugünkü.
**SONUÇ** §F.3/3 kapanır: kullanıcı ikinci gün geldiğinde sistem **onu tanır** — ve
tanıdığı şeyin **kaynağını gösterir**. ⚠ Ölçülebilir hedef: `lab/deneyim.py`'nin
`S3·süreklilik` satırı **çok-oturumlu** senaryoda da yeşil (bugün yalnız oturum-içi).
**GERİ AL** `oturumlar_arasi_hafiza=off` → `/ask` geçmişi okumaz, bugünkü iki-tur penceresi.
Yazılan kayıtlar **silinmez**.

---

### AJ5 · ⭐ **Ayrıştırma: planlayıcıyı AÇ ve ÖLÇ + araç yüzeyi**  [bayrak: `agent_plan_secimi`] · **kuzey yıldızının A'sı**
**NEDEN** 🔴 **Kullanıcının *"temelini atmadan"* dediği temel ZATEN ATILMIŞ — kapağı hiç
açılmamış.** `planner.Planlayici.sec()` (`app/planner.py:229`) LLM'e bir **plan** önertiyor
ve **dört kapı** denetliyor — MIMARI §11.6d'nin omurgası: *"**SEÇİM ≠ ÇALIŞTIRMA.**
Seçicinin yanılması yeni bir risk açmaz"* (uydurma araç adı **KAYIT** kapısında · yetkisiz
araç **YETKİ** kapısında · LLM aracı deterministik kardeşinden önce **DET-ÖNCE** kapısında ·
sonsuz plan **BÜTÇE** kapısında ölür).
**Ölçülen durum @`88bde2a`:** tek tüketicisi `_capraz_alan_pilotu` · bayrak
`agent_plan_secimi` **`off`** · **hiç ölçülmedi** · **açılırsa çöküyor** (**0.22**).
🔴 **Ve araç kaydı bir ÇAĞRI YOLU DEĞİL, bir KATALOG:** 15 aracın **8'i** `ask.py`/`planner.py`
içinde **kayıt adıyla hiç geçmiyor** (`deterministic_refine` · `cube_sql` · `drill.expand` ·
`drill.select` · `contribution.pvm` · `interpret` · `viz.recommend` · `llm.anlat`) —
**doğrudan fonksiyon olarak** çağrılıyorlar, yani **planlayıcının göremediği** yeteneklerdir.
*(⚠ Bir dış değerlendirme bunu "yalnız 3'ü çağrılıyor" diye ölçmüştü; **gerçek 7 referanslı /
8 referanssız** — sayı düzeltildi, teşhis aynı kaldı.)*
```bash
grep -c '^    Arac(' backend/app/tools.py        # kayıtlı araç
python3 - <<'X'  # kayıt adıyla ask/planner'da geçenler
X
```
**NE** backend: `sec()` **açılır ve ölçülür**; 8 yetim araç **planlayıcıya bağlanır**
(6.3 zaten **+11 araç** ekliyor — birlikte yürür) │ sözleşme: `agent_run.steps[]` **makbuzda
görünür** (**0.8** onu render'a bağlıyor) │ frontend: **düşünme adımları** — reddedilen
adımlar **dâhil** (`SEÇİM REDDİ`)
**NASIL** 🔴 **Yeni kod neredeyse YOK** — madde bir **ölçüm turudur**: 0.22'yi düzelt →
0.16'nın bütçesiyle `alpha`'da aç → A/B koş → **kazanç/kayıp yaz**. Araç bağlama işi
`tools.KAYIT`'a **satır eklemektir**, motor yazmak değil.
**KAPI** `tests/test_planlayici_acik.py` (**yeni**): uydurma araç adı → **KAYIT kapısı**
reddeder **ve makbuz yine üretilir** (0.22'nin regresyonu) · viewer rolü
`contribution.report` **çağıramaz** (YETKİ, 1.3) · LLM aracı deterministik kardeşi varken
**seçilemez** (DET-ÖNCE) · bütçe aşımı **planı keser** · 🔴 `nl_corpus --kapi` **gerilemez**.
**SONUÇ** Kuzey yıldızının **A parçası** çalışır: *"önce cirosu olan ürünleri bul → her biri
için karlılık → mukayese → rapor derle."* Ve **8 yetim yetenek planlayıcıya görünür** olur.
**GERİ AL** `agent_plan_secimi=off` → bugünkü tek-adım yolu **birebir**. Araç kaydına eklenen
satırlar **zararsız** (kayıt bir katalogdur; bağlanmayan araç **çağrılmaz**).

---

### AJ5b · ⭐ 🔴 **ADIM ZİNCİRİ — planlayıcı araç SEÇİYOR, adımları BAĞLAMIYOR**  [bayrak: `adim_zinciri`]
**NEDEN** 🔴 **Sürüm 7'nin denetiminde bulunan EN BÜYÜK mimari boşluk — ve `AJ5` onu
kapatmıyordu.** `sec()` şunu döndürüyor (ölçüldü @`88bde2a`):
```python
[{"arac": "route", "neden": "…"}, {"arac": "contribution.decompose", "neden": "…"}]
```
**Düz bir ARAÇ LİSTESİ** — `girdi` yok, `cikti` yok, `depends_on` yok. `Adim` dataclass'ı
(`planner.py:82`) da bir **kayıt yaprağıdır**: `arac · determinizm · sure_ms · makbuz ·
hata · kapisiz`. **Bir adımın çıktısını bir sonrakine bağlayan alan YOK.**
Ve `ara_sonuc`/`calisma_kumesi`/`onceki_sonuc` kavramı **repoda hiç yok**.
🔴 **Kodun kendi itirafı bunu zaten söylüyor** (`planner.py:336`, `dis_adim`'in docstring'i):
> *"Onu `tools.KAYIT`'a tek bir araçmış gibi yazmak **yalan olurdu**: **ne girdisi tipli,
> ne çıktısı**, ne de kapılardan geçiyor."*

**KUZEY YILDIZI TAM BURADA KIRILIR.** *"…her bir satış üreten ürün kalemiyle mukayesesi…"*:
| Adım | Ne yapar | Bugün |
|---|---|---|
| 1 | *"son 6 ayda cirosu olan ürünleri bul"* | ✅ tek `cube_query` |
| **2** | *"**BU ÜRÜNLERİN** her biri için karlılık"* | 🔴 **1'in ÇIKTISINI tüketmeli — ifade edilemiyor** |
| **3** | *"her birini toplam ortalamayla mukayese"* | 🔴 **2'nin çıktısını tüketmeli** |
| 4 | rapora derle | AJ6 |

*Yani `AJ5` planlayıcıyı açsa bile, açtığı şey bir **araç seçici**dir — bir **boru hattı**
değil. Bileşik soru yine cevaplanamaz.*
**NE** backend: `Adim`'e **`girdi_ref`** (*hangi adımın çıktısı*) + **`cikti_tipi`**
(`satır kümesi | skaler | varlık listesi | cube_query`); `Kosum`'a **`ara_sonuclar: dict[int,
Any]`** (çalışma kümesi, **tur ömürlü**) │ sözleşme: `agent_run.steps[].girdi_ref` +
`cikti_tipi` **makbuzda görünür** │ frontend: adım ağacında **oklar** — *"bu adım şundan
besleniyor"*
**NASIL** 🔴 **En dar biçim seçilir — genel bir iş akışı motoru YAZILMAZ:** yalnız
**`varlık listesi → filtre`** bağı (adım 1'in döndürdüğü boyut değerleri, adım 2'nin
`filters`'ına `in` olarak girer). Bu, `entity_limit` ve `measure_having`'in **zaten kurulu**
sarma kalıbıyla aynı ailedendir.
⚠ **Fan-out ve bütçe kapıları adım zincirine de uygulanır** — `Butce(adim, saniye, sorgu)`
**zaten var**; zincir onu **aşamaz**. Ve 🔴 **`dis_adim`'in `kapisiz=True` itirafı korunur:**
tipli girdi/çıktı **kapı demektir**; zincire giren adım artık `gated=True` olur — *yani bu
madde denetim yüzeyini BÜYÜTÜR, küçültmez.*
**KAPI** `tests/test_adim_zinciri.py` (**yeni**): adım 2 **yalnız** adım 1'in **ilan ettiği
çıktı tipini** tüketebilir (tip uyuşmazlığı → **fail-closed red**) · **döngü YASAK** (DAG
kapısı) · zincir uzunluğu **bütçeyle sınırlı** · her adım **kendi `contract_id`'sini** taşır
(D4) · 🔴 **bir adım başarısızsa zincir DURUR ve kısmi sonuç DÜRÜSTÇE beyan edilir** —
sessizce kırpılmaz.
**SONUÇ** Kuzey yıldızının **A parçası GERÇEKTEN** çalışır: ayrıştırma yalnız *"hangi
araçlar"*ı değil, ***"hangi araç hangisinden besleniyor"***u da söyler. **Bu madde olmadan
AJ5 bileşik soruyu çözmez** — yalnız tek adımlık soruları daha iyi seçer.
**GERİ AL** `adim_zinciri=off` → `sec()` bugünkü **düz listeyi** döndürür, adımlar
bağımsız koşar (bugünkü davranış birebir). `ara_sonuclar` **tur ömürlü** olduğu için
kalıcı durum bırakmaz — geri alma **temizlik gerektirmez**.

---

### AJ6 · **Bileşik rapor artefaktı**  [bayrak: `bilesik_rapor`] · **kuzey yıldızının C'si**
**NEDEN** Kuzey yıldızı *"bir **rapor yaz**"* diyor — çok adımlı bir planın çıktısı **tek bir
artefakt** olmalı. Zemin **büyük ölçüde hazır**: `report.compose_report()` (`report.py:20`) +
**5.13b**'nin rapor yapısı (kapak → yönetici özeti → kartlar → kaynak listesi).
**NE** backend: `agent_run`'ın adımları **tek rapora** derlenir │ sözleşme: mevcut
`ReportRequest`/`ReportBlockSpec` **genişletilir**, yeni tip **yazılmaz** │ frontend: 5.13b'nin
rapor görünümü
**NASIL** **Yeni derleyici yazılmaz** — `compose_report` var; eklenen tek şey *"çok adımlı bir
koşumun adımlarını blok listesine çevir"*.
**KAPI** `tests/test_bilesik_rapor.py`: her blok **kendi `contract_id`'sini** taşır (D4) ·
🔴 **`contract_id` PDF'te bile altta kalır** (5.13b'nin kuralı) · bir adım **başarısızsa**
rapor **dürüstçe eksik** üretilir, sessizce kırpılmaz.
**SONUÇ** *"Analiz ettiğin bir rapor yaz"* **tek artefaktla** cevaplanır ve **her sayısı
makbuzlu** olur.
**GERİ AL** `bilesik_rapor=off` → adımlar **ayrı cevaplar** olarak döner (bugünkü davranış).

---

## §G.6 · 🔴 **KIYAS SÖZLEŞMESİ — ikinci satır kod yazılmadan ÖNCE yazılır**

> **Bu bölüm §G'nin en kritik parçasıdır.** Bu depo *"iki şeyi kıyasla"* işinde **üç kez**
> kendi ayağına bastı; `50402d3`'ün kaydı birebir: ***"YANLIŞ NÜFUS ölçülmüştü."***

### G.6a · A ve B **AYNI KORPUSTA KIYASLANAMAZ**

`nl_corpus` **10.865 tur · tek-turluk · şablonlu · `--network none`** — yani **A'nın kendi
sahası**. B'nin değeri **konuşmada**, ve korpus konuşmayı **yapısal olarak göremez**.
🔴 **İkisini orada yarıştırırsanız B kaybeder ve sonuç YANLIŞ olur.**

| Ne ölçülüyor | Alet | Kural |
|---|---|---|
| **GERİLEME** — *B bir şey bozdu mu?* | `lab/nl_corpus.py --kapi` | doğru-cube **%93,2'den düşemez** · `CLARIFY:dönem` **±0,5** (§C/3) |
| **KAZANÇ** — *B ne getirdi?* | `lab/deneyim.py` (**§F.1**, **15** thread × 7+3 sözleşme satırı @`88bde2a`) + **`pass^5`** (§C/15) | **`N` = 3** — tanımı ve simetri şartı **§G.6f/(a)** |
| **GÖREV BAŞARIMI** | §C/13'ün **kör insan hakemi** | B ≥ A |
| **FİYAT** | 0.17'nin **p50/p95 bütçesi** | bütçe içinde |

🔴 **Kazancı ölçen alet, gerilemeyi ölçenden FARKLI OLMAK ZORUNDA.** Bu ayrım yazılmadan kod
yazılırsa, üç ay sonra elde **kıyaslanamayan iki sistem** olur.

### G.6b · Kabul ölçütü — **şimdi yazılır, sonra tartışılmaz**

> **B `beta`'ya geçer ANCAK:** `nl_corpus` doğru-cube **gerilemedi** **VE** `deneyim.py`
> sözleşmesinde **≥3 satır A'dan iyi** (**`N`=3, simetri şartıyla — §G.6f/(a)**) **VE**
> kör hakem görev başarımında **B ≥ A** (**protokol: §G.6f/(b)**) **VE**
> p95 gecikme **0.17'nin bütçesi içinde**.
> **Dördü birden sağlanmazsa B `off` kalır ve GEREKÇESİ `MIMARI.md`'ye yazılır** (FAZ 0.4
> disiplini: *"kayıp > kazanç ise açılmaz ve nedeni yazılır"*).
>
> 🔴 **AMA «sağlanmadı» İKİ ANLAMA GELİR ve ayrılması ZORUNLUDUR:** her kapı **GEÇTİ ·
> KALDI · ⊘ KOŞULAMADI** üç değerinden birini alır; `⊘` taşıyan bir sonuç **karar
> değildir, borç kaydıdır.** Hüküm tablosu ve kısmi benimseme yolu **§G.6f/(c)-(d)**.

### G.6f · 🔴 **`N`'İN DEĞERİ · HAKEM PROTOKOLÜ · «KOŞULAMADI» HÜKMÜ**  *(sürüm 8 — eksik kapatıldı)*

> ⚠ **Bu alt-bölüm bir denetim turunda AÇILDI ve gerekçesi sert:** G.6b *"şimdi yazılır,
> sonra tartışılmaz"* diyordu ama **kararın tek düğmesi olan `N` boş bırakılmıştı**, kör
> hakemin **süreci hiç yazılmamıştı**, ve **«ölçülemedi» ile «ölçüldü, B kaybetti»
> ayrılmamıştı**. Üçü birlikte şu sonucu üretiyordu:
>
> 🔴 **En olası başarısızlık biçimi B'nin KAYBETMESİ değil, ölçümün HİÇ KOŞULMAMASIDIR** —
> ve dört-yönlü VE'de koşulmayan bir kapı otomatik olarak A lehine düşer. Yani kullanıcının
> *"ikisini de geliştirip kıyaslayacağız; geliştirme maliyetini de kabul ediyorum"* kararı
> **hiç tartışılmadan** ölürdü. Bu, belgenin **en pahalı tek satırıydı**.

#### (a) `N` = **3** — ve payda **taban ölçümüyle** sabitlenir

`lab/deneyim.py`'nin sözleşmesi **10 satır** (S1…S7 + S8/S9 §F.1'den + S10 AJ3b'den) ve
matris **seyrek**: her senaryo her satırı ölçmez, `⊘` **çoğunluktadır**. Bu yüzden `N` bir
**yüzde değil, mutlak sayı** olmalı — ve tabanla birlikte okunmalı.

| Ölçüm | Değer | Damga |
|---|---|---|
| A'nın tabanı (çevrimdışı) | **34 ✅ · 1 ❌ · 56 ⊘** | `a5942c7` |
| A'nın tabanı (canlı) | **33 ✅ · 2 ❌ · 56 ⊘** | `c4b14d1` |
| A'nın tabanı (canlı, **15 senaryo**) | **41 ✅ · 1 ❌ · 63 ⊘** | `88bde2a` |

**KURAL:** *B, A'nın **kırmızı ya da ⊘** bıraktığı satırlardan **en az 3'ünü yeşile
çevirmeli**, **ve A'nın yeşillerinden hiçbirini kırmızıya çevirmemeli**.*

* **Neden 3:** A'nın canlı tabanında **tek** kırmızı var (`o ayı makine bazında aç`,
  §F.3/7). Eşik 1 olsaydı B **tek bir satırla** kazanırdı — ölçüm değil, tesadüf.
  Eşik 5+ olsaydı, seyrek matriste **yapısal olarak ulaşılamaz** olurdu (63 ⊘'nin çoğu
  senaryo-kapsamı gereği, B'nin gücüyle ilgisiz).
* **Neden "⊘ → ✅" de sayılır:** `⊘` *"bu senaryo o satırı ölçmez"* demek; B yeni bir
  yetenek getirip o satırı **ölçülebilir** kılıyorsa bu **gerçek bir kazançtır**
  (ör. AJ3b'nin `S10·eşzamanlılık`'ı).
* 🔴 **Simetri şartı bağlayıcı:** *"3 kazandı, 3 kaybetti"* **geçmez**. Kaybedilen her
  yeşil satır, kazanılan üçe **ek** bir kazanç ister — aksi hâlde net değişim sıfırken
  karar B lehine düşerdi.

⚠ **Payda değiştiğinde `N` yeniden türetilmez, TABAN yeniden ölçülür.** `S8`/`S9`/`S10`
indiğinde ya da senaryo sayısı değiştiğinde: **önce A ile taban**, sonra B. (Bu, `0.19`'un
payda dersinin §G'deki karşılığıdır.)

#### (b) Kör hakem protokolü — **sayı, süreç, anlaşmazlık**

Kapı *"B ≥ A"* diyordu ama **kim, kaç kişi, kaç vaka, nasıl karar verir** yazılı değildi.
Yazılı olmayan bir insan süreci, **hiç koşulmayan** bir süreçtir.

| Parametre | Değer | Gerekçe |
|---|---|---|
| **Hakem sayısı** | **2**, ekip dışı | 1 hakem = kanaat; 3+ hakem = takvimlenemez |
| **Vaka sayısı** | **10** (§C/13'ün kendi sayısı) | Ayrı bir küme icat edilmez |
| **Kaynak** | §C/13'ün penceresi (**FAZ 8.1**) — *"kendi denemelerimiz"* payı **<%50** | Kendi yazdığımız soruyla kendimizi ölçmek §C/16'nın reddettiği şey |
| **Körlük** | Hakem **hangi cevabın A hangisinin B** olduğunu **bilmez**; sıra vaka başına rastgele | Standart |
| **Ölçek** | Vaka başına **kabul edilebilir / değil** (ikili). Puan yok | §C/13 zaten *"≥%70 kabul edilebilir"* diyor — ikinci bir ölçek ikinci bir tartışma |
| **Anlaşmazlık** | İki hakem ayrışırsa vaka **`⊘ ÖLÇÜLEMEDİ`** — üçüncü hakem YOK | Faz 9.6'nın üçüncü durumu; çoğunluk uydurmak gürültüyü karara çevirir |
| **Kabul** | **B'nin kabul sayısı ≥ A'nınki** *(eşitlik B lehine DEĞİL — bkz. (c))* | — |
| **Rubrik** | **Önce yazılır**, koşumdan sonra değiştirilmez | §C/16'nın *"ilan edilmiş puanlama kuralı"* disiplini |

#### (c) 🔴 **«KOŞULAMADI» ≠ «KAYBETTİ» — üçüncü hüküm**

Dört kapının **her biri** üç değerden birini alır: **GEÇTİ · KALDI · ⊘ KOŞULAMADI**.

```
GEÇTİ      → ölçüldü, eşik sağlandı
KALDI      → ölçüldü, eşik sağlanmadı
⊘ KOŞULAMADI → ölçüm ön koşulu yok (kota bitti · hakem bulunamadı · FAZ 8.1 penceresi
               açılmadı · S8/S10 inmediği için kazanç aleti o satırı göremiyor)
```

**HÜKÜM TABLOSU — istisnasız:**

| Durum | Karar | Kayıt |
|---|---|---|
| Dördü de **GEÇTİ** | **B `beta`** | `MIMARI.md`'ye ölçümle |
| En az biri **KALDI** | **B `off`** | Gerekçe + **hangi kapının kaldığı** yazılır |
| Hiçbiri KALDI değil ama en az biri **⊘** | 🔴 **KARAR YOK — B `off` KALIR ama bu bir SONUÇ DEĞİLDİR** | `MIMARI.md`'ye ***"ÖLÇÜLEMEDİ: &lt;hangi kapı&gt; · &lt;neden&gt; · &lt;ön koşul&gt;"*** yazılır ve **§G açık kalır** |

> 🔴 **Üçüncü satırın bağlayıcı sonucu:** *"ölçemedik"* bir **borç kaydıdır**, kapanış
> değil. `⊘` taşıyan bir §G **"B kaybetti" diye özetlenemez**, kapanış bölümüne
> *"kıyas yapıldı"* yazılamaz, ve ön koşulu düştüğü gün **ölçüm yeniden koşulur**.
> *Kullanıcının kararı ancak ÖLÇÜLEREK iptal edilebilir — ölçememekle değil.*

⚠ **Ve `⊘`'nin bir son kullanma tarihi vardır:** iki sürüm sınırı boyunca `⊘` kalan bir
kapı, **kapının kendisi** yeniden değerlendirilir (0.20'nin *"iki sürüm açık kalan bayrak
silinir"* kuralının kıyas tarafındaki hâli) — çünkü ölçülemeyen bir ölçüt, ölçüt değildir.

#### (d) Kısmi benimseme — **ikili sonuç yasağı kalkar**

G.6b B'yi `beta`|`off` ikilisine hapsediyordu. Ama gerçekçi sonuç **karma**:
*"B netleştirmede kazanıyor, tek-adım cevapta kaybediyor."* Altyapı buna **zaten uygun**:
`tur_yoneticisi` bir **bayraktır** ve bayrak kapsamı `global < sektör < tenant < rol <
kullanıcı`'dır (kurulu).

**KURAL:** kapılardan biri **satır bazında** ayrışıyorsa (bazı sözleşme satırlarında B, bazılarında A
iyi), karar **kapsamla** verilir: B, kazandığı **senaryo sınıflarında** `beta`, diğerlerinde
`off`. Bu **bir uzlaşma değil ölçümün kendisidir** — ve ayrışmanın **hangi satırlarda**
olduğu `MIMARI.md`'ye yazılır.
⚠ Kısmi benimseme **gerileme kapısını gevşetmez**: `nl_corpus` her kapsamda yeşil olmalıdır.

---

### G.6d · 🔴 **TEST REJİMİ — ÜÇ KATMAN, üçü de ZORUNLU**

> **Kullanıcı (2026-08-03):** *"Bunların çalıştığını da **çok iyi CANLI ve KLASİK testlerle,
> caselerle** test etmeli."* — Ve §G bunu **en çok gerektiren** faz ailesidir, çünkü
> **öznesi LLM yolu**. Sürüm 7'ye kadar §G'de *"canlı"* kelimesi **iki kez, tesadüfen**
> geçiyordu. **Bağlandı.**

| # | Katman | Ne yakalar | Nasıl koşulur |
|---|---|---|---|
| **T1 · KLASİK** | Deterministik süit — her maddenin `KAPI`'sı | **gerileme** · sözleşme ihlali · fail-closed davranış | `--network none`, `lab/kapi.py --tam`. **Sağlayıcı `rule`** — LLM'siz de geçmeli |
| **T2 · CANLI** | **Gerçek sağlayıcı** ile uçtan uca | *"prompt gerçekten anlaşılıyor mu"* · gecikme · maliyet · guard düşme oranı | `--live` · **izole konteyner** (§A.3) · **tur arası 5 sn** |
| **T3 · VAKA** | **Adı konmuş kabul vakaları** (aşağıda) — hem süitte hem **elle** | *"kullanıcı bunu yazınca ne oluyor"* | `lab/deneyim.py` + **manuel tur** (§G.6c'nin 6 kombinasyonu) |

🔴 **HİÇBİR §G MADDESİ ÜÇÜ DE YEŞİL OLMADAN `beta`YA GEÇMEZ.** T1 tek başına yetmez —
`c4b14d1`'in dersi tam da budur: **`--live` ÜÇ KEZ karşılıksız koştu** ve *"o koşumlara
dayanarak bayrak kararı alınabilirdi."*

**T2'nin bağlayıcı şartları** *(`c4b14d1` bunları kilitledi, §G onları devralır)*:
* **Fail-closed:** gerçek üretici kurulmuyorsa `--live` **KOŞMAZ** — sessizce `rule`'a düşmez
* **Rapor başlığı üreticinin ADINI taşır** — *"CANLI MOD"* yazıp `rule` koşmak **yasak**
* **Tek sahip:** `get_settings.cache_clear()` — ikinci bir kopya **yazılmaz**
* ⚠ **Kota:** T2 **0.16'nın ayrılmış anahtarına** bağlıdır; kota < eşik → **koşmaz**

---

### G.6e · 🔴 **ADI KONMUŞ KABUL VAKALARI (`VK-1…VK-6`)** — geliştirici bunları ATLAYAMAZ

> **Neden adı konuyor:** *"iyi konuşuyor mu"* bir kanaat, **bu altı vaka bir ölçüm**. Her
> biri **T1'de bir test**, **T2'de bir canlı koşum**, **T3'te elle bir tur** olarak koşar.
> **Üçünde de geçmeyen madde inmemiş sayılır.**

| # | Vaka (kullanıcının kendi cümlesi) | Ölçtüğü | Madde | Bugün |
|---|---|---|---|---|
| **VK-1** | *"mart ayında ciro şubat ayına göre nasıl değişti"* | **kısa devre yok** + **adlı dönem kıyası** | AJ0 · AJ2 | 🔴 *«degisti» yerine «egitim» mi demek istedin?* |
| **VK-2** | *"fire"* → sistem ölçü sorar → kullanıcı **chip'e tıklar** **VE** ayrı turda **yazar** | **kapanan söz alışverişi** (iki yol da aynı rapora) | 0.5b · AJ0b | 🔴 yazınca `KURAL_TAZE` — yeni soru sanılıyor |
| **VK-3** | *"bu neden böyle?"* → katkı ayrıştırması | **görünürlük** — gövde alanları render dalına düşüyor mu | 0.23 | 🔴 hesaplanıyor, **ekranda yok** |
| **VK-4** | *"hayır, **şubat** demiştim"* (netleştirmeden sonra) | **onarım** — slot düzeltilir, baştan başlamaz | AJ0b | 🔴 baştan başlıyor |
| **VK-5** | 🔴 **KUZEY YILDIZI:** *"son 6 aylık ciro ve her bir satış üreten ürün kalemiyle mukayesesi ve bunların verimliliği ve karlılıklarını analiz ettiğin bir rapor yaz"* | **ayrıştırma + adım zinciri + dil + rapor** — hepsi birden | AJ5 · **AJ5b** · AJ2 · AJ6 | 🔴 **KISA DEVREDE ölüyor** (`«ureten urun»→«uretim»`) — **üç katmanlı engel, aşağıdaki kutu** |
| **VK-6** | VK-5'in **konuşma hâli**: *"başlıyorum… **şu kısmı anlamadım**"* → kullanıcı açıklar → *"tamam, şöyle alıyorum"* → **kaldığı yerden** devam | **eşzamanlılık** (Ç-1…Ç-5) | **AJ3b** | 🔴 netleştirme **terminal** — imkânsız |

> 🔴 **TABAN ÖLÇÜLDÜ — *"Bugün"* sütunu artık yeniden üretilebilir** (`lab/vk_taban.py`,
> `8f87e40`; yapısal **ve** canlı gemini). Üç satır **düzeltilmesi gerekti**:
>
> | # | Belgenin hükmü | **ÖLÇÜLEN** |
> |---|---|---|
> | VK-1 | *«degisti»→«egitim»* | ✅ **birebir**; red kodu **`R9`** |
> | VK-2 | yazınca `KURAL_TAZE` | ✅ ve daha net: sistem **AYNI netleştirmeyi ÜÇÜNCÜ kez** soruyor |
> | VK-3 | hesaplanıyor, ekranda yok | ✅ `contribution` **DOLU**, `result=None` |
> | **VK-4** | *"baştan başlıyor"* | ⚠ **YAPISAL modda evet; CANLIDA `cube+llm` ile GEÇİYOR.** Tek bir *"Bugün"* yazmak yanlış — **T1 ve T2 farklı sonuç veriyor** (§G.6d'nin ayrımı VK tablosuna yansımamıştı) |
> | **VK-5** | `R1/R10` · *"`verimlilik` katalogda yok"* | ⚠ **İkisi de yanlış.** Kısa devrede ölüyor (`AJ0`); `verimlilik` **katalogda VAR** (`verim`+ek); asıl katalog eksiği **ürün BOYUTU** (`R9`). Üç katmanlı zincir: **§G.6e'nin kutusu** |
> | **VK-6** | *"netleştirme terminal — imkânsız"* | ⚠ **Tur 1 canlıda ÇALIŞIYOR** (`cube+llm`, 5 satır); ölen **tur 2**, ve yine **yazım tahmini** |
>
> 🔴 **EN YÜKSEK KALDIRAÇ ÖLÇÜLDÜ: 13 turun DÖRDÜNDE** yazım-benzerliği kısa devresi
> öldürüyor (VK-1 · VK-5 · VK-6/2 · yapısal VK-4). **`AJ0` §G'nin tek en yüksek kaldıraçlı
> maddesidir** — üç kabul vakasını **ilk kapıda** kesiyor, ve `AJ2`/`AJ5b` daha sıraya bile
> gelmiyor. *§G.8'in ağacında AJ0'ın "ucuz" işareti geliştirme maliyetidir; **değeri ucuz
> değildir**.*
>
> ⚠ **VK-5'in istisnası ÜÇE çıktı:** kırmızının sebebi *"`R11` mi · katalogda yok mu"*
> ikilisi yetmiyor — **üçüncü şık: KISA DEVRE**. Rapor bu üçünü ayırmak zorunda, aksi hâlde
> `AJ0` indikten sonra VK-5 hâlâ kırmızıysa sebep **yanlış faza** yazılır.

**Her vakanın kayıt biçimi** *(süite girerken)*: `vaka_id · girdi cümlesi · beklenen SINIF
(cevap/netleştirme/ret) · beklenen `source` · yasak davranışlar`.
🔴 **Beklenen METİN yazılmaz** — T2'de metin sağlayıcıya göre değişir; **sınıf, `source` ve
yasaklar** sabittir. *(Bu, `narration_guard`'ın ±%2 disiplininin vaka tarafındaki hâli.)*

> 🔴 **VK-5'İN ENGEL ZİNCİRİ — ÜÇ KATMAN, HER BİRİ FARKLI FAZIN İŞİ** *(sürüm 8: ölçüldü
> `lab/vk_taban.py` + doğrudan `route()` probu, **demo-boyahane** kataloğunda)*
>
> Sürüm 7 bunu **iki** sebebe indirgiyordu (*"`R11` mi · katalogda yok mu"*) ve **ikisi de
> eksikti**. Ölçülen gerçek:
>
> | # | Katman | Ölçüm | Sahibi |
> |---|---|---|---|
> | **1** | 🔴 **KISA DEVRE** | Cümle merdivene **hiç girmiyor**: *«ureten urun» yerine «uretim» mi demek istedin?* → `source=None`, erken `return` | **`AJ0`** |
> | **2** | 🔴 **BOYUT katalogda yok** | `ürün kalemi` / `stok adı` bu tenant'ta **hiçbir cube'da boyut değil** → `R9` *"kırılım istendi ama boyut eşleşmedi"*; `cross_cube_dim_switch` de **çözemiyor** | **FAZ 3.1/3.2** |
> | **3** | **Ölçü + boyut FARKLI cube'larda** | (2) çözülse bile `verimlilik`=`oee`, ürün boyutu başka cube → MIMARI **§9.2**'nin yapısal sınırı | **`AJ2`** + `cross_cube` |
>
> ✅ **VE SÜRÜM 7'NİN İDDİASI ÇÜRÜTÜLDÜ:** *"`verimlilik` katalogda YOK"* **YANLIŞTI** —
> `oee/metadata.yml:11` `synonyms: [oee, **verim**, randıman, …]` taşıyor ve `verimlilik`,
> `verim` + geçerli ek zinciriyle (`_covers`/`_syn_hit` → **True**) **kapsanıyor**. Ölçüldü:
>
> ```
> "bu yil verimlilik"                 → VAR · oee.ort_oee          ✅
> "bu yil makine bazinda verimlilik"  → VAR · oee.ort_oee ×makine  ✅
> "bu yil karlilik"                   → VAR · parti.kar_marji_yuzde ✅
> "bu yil urun bazinda verimlilik"    → YOK · R9  ← ASIL ENGEL: BOYUT
> ```
>
> **Hatanın kaynağı ölçüm aletiydi:** tam kelime (`verimlilik`) arandı, **kök + ek zinciri**
> denenmedi. *Bu deponun en sık kusuru, ve bu kez belgenin kendisinde.*
>
> 🔴 **BAĞLAYICI: kırmızının SEBEBİ üç şıktan biriyle raporlanır** — `kısa devre` ·
> `boyut katalogda yok` · `ifade edilemez (R11)`. **Sebep yazılmazsa yanlış faza yazılır:**
> `AJ0` indikten sonra VK-5 hâlâ kırmızıysa bu **§G'nin başarısızlığı değil**, FAZ 3'ün
> henüz inmemiş olmasıdır.
> ⚠ **Tenant'a bağlı:** ölçüm `demo-boyahane`'de yapıldı. `stok_adi` boyutu **başka
> tenant'larda VAR** (ör. gitas) — yani (2). katman **tenant-özeldir** ve VK-5 farklı
> tenant'ta farklı katmanda ölebilir. Rapor **hangi tenant** olduğunu yazar.

### G.6c · Manuel test yolu — **kullanıcının açık isteği**

İki bağımsız anahtar, **ikisi de UI'da**: `yol_siniri` (**zaten var**, 3 konumlu) ×
`tur_yoneticisi` (**yeni**) → **6 kombinasyon**, hepsi elle denenebilir. Bayrak kapsamı
`global < sektör < tenant < rol < kullanıcı` (**kurulu**) → **tek test kullanıcısında**
`alpha`. Ve **hangi yolun cevapladığı** `source` rozeti + `explain.path`'ten okunur
(**AJ0** onu bir **merdiven izine** çevirir).

## §G.7 · FAZ 5'e etkisi — 🔴 **HİÇBİR MADDE SİLİNMEZ**

Bir dış değerlendirme *"B kazanırsa FAZ 5'in kalıp-sözlüğü işleri gereksizleşir, yazılmaz"*
dedi. **Bu tavsiye REDDEDİLDİ** — ve gerekçesi kullanıcının kendi kararıdır:

> *"Tek bir şey seçmeyeceğiz, **ikisini de geliştirip kıyaslayıp test edeceğiz**."*
> **A'nın maddelerini şimdiden silmek, kıyası PEŞİNEN HÜKME BAĞLAMAK olur** — yani
> ölçmeden karar vermek, bu belgenin en temel kuralının ihlali.

**Yapılan bunun yerine:** hangi maddelerin **B kazanırsa** gereksizleşeceği **işaretlenir**,
ve karar **ölçüme** bırakılır:

| Madde | B kazanırsa | Karar |
|---|---|---|
| **5.3** kalıp sözlüklerini kullanıcı ifadelerinden besle | LLM ifadeyi zaten anlar → **gereksizleşebilir** | **§G.6'nın ölçümünden sonra** |
| **5.1 / 5.2** `tur_takip` · `tur_paylas` kalıpları | tür sınıflandırması LLM'e geçer | aynı ·· ⚠ **ama `5.1`'in MOTORU (`schedules.create` önerisi) AJ0b'nin «inisiyatif» yeteneğinin tüketicisidir** — yürütücüden bağımsız, **kalır** |
| **5.16** netleştirme düzeyi | bir **ayar** değil, bir **davranış** olur | aynı |
| **5.6** peer · **5.9** kanallar | gerçek **yetenek** maddeleri — yürütücüden bağımsız | **kalır** |

🔴 **VE İKİ MADDE BU TABLODAN ÇIKARILDI — çünkü artık AJ0b'nin (deterministik diyalog
katmanı) parçalarıdır, LLM'in alternatifi değil:**

| Madde | Yeni statüsü |
|---|---|
| **0.5b** bekleyen netleştirme | 🟢 **AJ0b'nin «slot durumu» yeteneği.** *Taşınmadı, silinmedi — **adlandırıldı**.* Katman kazansa da kaybetse de **kalır**, çünkü **deterministiktir** |
| **5.17** tek ses (`app/soz.py`) | 🟢 **AJ0b'nin «temellendirme» yeteneği** (*"önce ne anladığını söyle, sonra sor"*). KD-21 gereği ret/netleştirme metni **her hâlükârda deterministik** — **B kazansa bile kalır** |

*Yani sürüm 6'nın ilk taslağı bu ikisini **"B kazanırsa gereksizleşebilir"** kutusuna
koymuştu; §G.0c'nin katman bulgusu bunu düzeltti: **ikisi de Katman 2'dir ve Katman 3'ten
bağımsızdır.***

**Yani §G planı BÜYÜTMÜYOR, ağırlık merkezini kaydırma İHTİMALİNİ ölçüyor.**

## §G.8 · Ön koşullar ve sıra — **hepsi zaten planda**

| Ön koşul | Neden **artık bloklayıcı** |
|---|---|
| **0.22** `UnboundLocalError` | **Ajan yolunun tam üstünde duran hata** |
| **0.16** ölçüm bütçesi | A/B **canlı** koşum gerektirir; ücretsiz kota kaldırmıyor (`50402d3`) |
| **0.17** gecikme bütçesi | **İki yürütücü kıyaslanacak** — ölçüsüz kıyas yok. Her tura sıcak yolda LLM çağrısı ekleniyor |
| **0.20** bayrak profilleri | İki yürütücü × mevcut bayraklar → *"hangi konfigürasyon test edildi"* **profilsiz cevaplanamaz** |
| **0.23 · 0.5b · 0.10b** | B'nin çıktısı **görünmezse** manuel test anlamsız |

```
0.22 · 0.16 · 0.17 · 0.20              (ön koşul — hepsi zaten FAZ 0'da)
  │
  ├─ AJ0   kısa devre yasağı           UCUZ · güvenlik ağı · AJ2'nin ölçüm aletini kurar
  │                                     MIMARI §5'in 18. yasağı
  ├─ AJ0b  ⭐ DİYALOG YÖNETİCİSİ       🔴 §G'NİN İLK MADDESİ — deterministik, RİSKSİZ
  │          (0.5b + 5.17 bir katman olarak adlandırılır; devam · onarım · inisiyatif eklenir)
  │          ↳ şikâyetin BÜYÜK KISMINI bu çözer · ve Katman 3'ün ÖLÇÜM ZEMİNİNİ kurar
  │
  ├─ AJ2   referans dili + Intent-JSON şeması (`compare` VE `blend`) + R11
  │          ↳ "bin bir dilsel şey"i kapatan · bileşik soruyu MÜMKÜN kılan
  │          └─ 5.6 (peer)   ← AJ2'DEN SONRA, dördüncü enum değeri çakılmadan
  │
  ├─ AJ5   ⭐ planlayıcıyı AÇ ve ÖLÇ + 8 yetim aracı bağla     (0.22 · 0.16 zorunlu)
  │          └─ AJ5b ⭐ 🔴 ADIM ZİNCİRİ — girdi_ref + cikti_tipi + ara_sonuclar
  │                    ↳ AJ5 araç SEÇER; AJ5b onları BAĞLAR. Bileşik soru AJ5b'siz ÇALIŞMAZ
  │               └─ AJ6  bileşik rapor artefaktı              (5.13b ile)
  │
  └─ AJ1   iddia kapısı  ~3-4 gün      ← Katman 3'ün TEK bloklayıcısı
       └─ AJ3  turu LLM yönetir   →   §G.6'nın kıyası   (tabanı artık AJ0b)
            └─ AJ4  oturumlar-arası süreklilik
```

> 🔴 **SIRA SÜRÜM 6'NIN İLK TASLAĞINDAN DEĞİŞTİ — ve gerekçesi ölçüm:** ilk taslak
> *"AJ1 → AJ2 → AJ3"* diyordu, yani **LLM'le başlıyordu**. Atlanmış katman bulgusu (§G.0c)
> bunu düzeltti: **AJ0b önce gelir**, çünkü (a) **güven modeline hiç dokunmaz** — kıyas turu
> bile gerekmez, (b) kullanıcının şikâyetinin **büyük kısmını o çözer**, (c) 🔴 **AJ3'ün
> kıyas TABANI olur.** *LLM yöneticiyi «hiç diyalog yönetimi yok»a karşı ölçmek, B'yi
> A'nın en zayıf hâline karşı yarıştırmak olurdu — kazanması hiçbir şey kanıtlamazdı.*
>
> **Ve AJ2 · AJ5 · AJ1 birbirinden BAĞIMSIZ** — paralel yürüyebilirler. Yalnız **AJ3** üçünü
> birden bekler.

## §G.9 · Dürüst riskler — **üçü de gerçek, üçü de kayda geçiyor**

1. 🔴 **Konuşma yüzeyi deterministik olmaktan ÇIKAR.** `nl_corpus` onu ölçemez (tek-turluk,
   şablonlu). Karşılığı **kurulu**: `lab/deneyim.py` + `pass^k` (§C/15 — τ-bench ölçtü:
   `pass^1` >%60 iken **`pass^8` <%25**; çok-turlu güvenilirliğin doğru metriği budur).
2. 🔴 **İddia kapısı TEK ARIZA NOKTASIDIR.** Zayıf olursa *"akıcı ama uydurma"* geri gelir —
   **mimarinin var olma sebebi**. `narration_guard` titizliğiyle (**20 test**) kurulmalı ve
   **düşen cümle oranı ölçülmeli**.
3. **Maliyet.** Her tur LLM çağrısı. **0.17 bunu sayıya çevirir**; kullanıcı maliyeti
   **açıkça kabul etti**, ama *kabul edilen maliyet ≠ ölçülmeyen maliyet*.

**DEĞİŞMEYENLER** — §G bunların **hiçbirine dokunmaz**: sayı küpten · motor-RLS · yetki
matrisi · audit · makbuz · fan-out sertifikası · toplanabilirlik kapısı.
**Ajan katmanı bunların ÜSTÜNE oturur** — MIMARI §11'in kendi tezi: *"agentic katman temelin
ne ise onu **ÇARPAR**."* Zayıf temelde ajan zararı çarpar; bu yüzden §G **FAZ 0/1'den sonra**.

## §G.10 · Ve bu **neden gerçekten fark** — üçüncü konum

Rakipler **ikisinden birini** seçmiş durumda: **LLM SQL yazsın** (Zenlytic tezini bunun için
terk etti) ya da **LLM formu doldursun** (Dima **bugün**). Üçüncü konum —
**sayı küpten · cümle LLM'den · iddialar şemaya karşı doğrulanmış** — **kimsede yok.**

*Karşılaştırma zemini:* Zenlytic `Dynamic Fields` yönetişimli ama **iddia kapısı yok** ·
Pyramid'in *"reçete"*si doğru mimari ama **konuşmayı yönetmiyor** (30-40 sn, akış yok,
makbuzu en zayıfı) · Tellius'un netleştirme kadranı var ama **ToS'u hassas veri göndermeyin
diyor**. `[DOĞRULANMADI]` — **rakip iddiaları FAZ 4.7'nin raporundan önce birincil kaynakla
doğrulanır** (EK F disiplini).

---

# BÖLÜM I — v1'E GİDEN YOL

## FAZ −1 · `MIMARI.md` ÖN HAZIRLIĞI *(kod yok, tek oturum)*

**NEDEN** `MIMARI.md` **kanoniktir**. Bu yol haritası mimariyi değiştiriyor → çelişkide
eski mimari kazanır ve düzeltme geri çevrilir. Ama ileri-tarihli kural yazmak da yasak:
MIMARI §10 *"karar değiştiğinde **aynı PR'da** güncellenir, **kod ile belge ayrı PR'a
bölünmez**"*, ve orada `✅` **"ölçüldü ve yapıldı"** demektir. [KANIT §−1]

> **Denetim notu:** `⟳` mekanizması **zaten kurulu ve kullanımda** (`MIMARI.md`'de 15+ `⟳`
> bloğu; `tests/test_beyanlar_curumesin.py`'de *"TUZAKTAN KAPIYA dönüştü"* kayıtları).
> Gerçekten **yeni olan tek şey §1 öncesi TOPLU İNDEKS**tir — madde buna göre yazıldı.

### −1.1 · Kutu A — **bugünü yanlış anlatan satırlar**  [bayraksız: belge]
**NE** `MIMARI.md`'de aşağıdaki **on iki satır** düzeltilir *(A1…A13; **A6 geri çekildi** —
aşağıdaki kütüğe bak. Sürüm 1'de bu cümle *"altı satır"* diyordu, tablo ise 13 satırdı;
**FAZ −1'de ölçülüp düzeltildi**)*:

| # | Satır | Düzeltme | Kanıt |
|---|---|---|---|
| A1 | §7 *"gerçek tavan %64 … **aradaki 36 puan** kapsam boşluğudur"* | O 30 puanın **%25,9'u netleştirmedir** (ADR-0008'in **istediği** davranış); çözülemeyen **%0,3** | [KANIT §11.1] |
| A2 | §6.13z *"Kapsam dışı: sosyal sınıf"* (`MIMARI.md:811`) | **Yapıldı** (`e1bde3f`) | `tests/test_sosyal_sinif.py` |
| A3 | §11.2 *"ajan kullanıcının yetkisini aşamaz"* | **15/15 araç tek izin** (`query:run`) → granülerlik **efektif yok**; FAZ 1.3 kapatır | `app/tools.py:118-350` |
| A4 | §7'nin telemetri satırları + `interactions.py:144` | Uç gerçekte **:161**; telemetri sayıları **ortam + komut** ile yazılır | denetim |
| A5 | Test/ölçüm sayıları | 🔴 **D2 uygulandı: sabit sayı SİLİNDİ, yerine komut yazıldı.** Sürüm 1'in `0a1a087` damgalı listesi FAZ −1'de yeniden ölçüldü ve **altı kalemi bayatlamıştı** *(133→143 dosya · 1441→1542 fn · `nl_accuracy` 510→485 satır · `cube_router` 3276→3565 · `ask.py` 3654→3991 · `app/routers/` 52 uç/12 dosya → 56 uç/14 dosya)*; **dört kalem hâlâ doğruydu** *(63 vaka · migration 29/`e4a1c8d92f36` · `authorize` 16 izin)*. Sayılar artık **`A5-KOMUT` kutusundan** üretilir; MIMARI'ye yazılan her sayı `<sayı> @<sha> · <komut>` taşır | denetim @`81ad10b` |
| ~~**A6**~~ | ~~§5 *"kolon doğrulaması `tests/test_member_sweep.py`'nin build-time `LIMIT 0` taraması"*~~ | ⛔ **GERİ ÇEKİLDİ (FAZ −1'de ölçüldü)** — kütüğe bak | — |
| **A7** | §3.3 *"yeni üretim adımı bu kalıbın **dördüncü** örneğidir"* | Kodda **dört** üreteç var (`_compose_relationship_dimensions` sayılmamış) → yeni adım **beşincidir** | denetim |
| **A8** | §3.4 *"**17** kullanılmayan konnektör"* | Backend'de hiç geçmeyen **12** | denetim |
| **A9** | §7 *"kapsam tavanı **hâlâ %64**"* (üç ayrı satır: 2567 · 2571 · 2630) | Ölçülen **%68-72**; §7 **hiç güncellenmemiş** | dış denetim M2 · doğrulandı |
| **A10** | §7 *"telemetri pratikte hâlâ **boş (7 satır)**"* | İki ⟳ bloğu **93/105** diyor — aynı belgede | dış denetim M3 |
| **A11** | `interaction_log` **93** (§6.12z ⟳ uzlaştırma tablosu) ↔ **105** (§6.3 ⟳) | Üç sayıyı uzlaştırmak için yazılan blok **dördüncü bir sayıyla** çelişiyor. → **Kural D2 uygulanır: sabit sayı silinir, yerine ölçüm komutu yazılır** | dış denetim M1 |
| **A12** | **`### 6.8z` İKİ KEZ** kullanılmış (Faz F2 · Faz 7) | Numaralandırma çakışması — biri yeniden numaralanır | dış denetim M4 |
| **A13** | Metin **§1.5 · §1.6 · §1.7 · §2.1 · §4.4 · §3.2**'ye atıf veriyor — **MIMARI'de yoklar** | Bunlar **uygulama planlarının** bölümleri; MIMARI'yi tek başına okuyan çözemez → atıflar **kaynağıyla** yazılır (*"plan §1.5"*) ya da içeriği taşınır | dış denetim M5 |

**KAPI** `tests/test_beyanlar_curumesin.py::test_MIMARI_TEST_SAYILARI_gercekle_uyusuyor`
(**zaten var** — sürüm 1 bunu bir *dosya* sanıyordu, `tests/test_MIMARI_TEST_SAYILARI_
gercekle_uyusuyor.py` **yoktur**; FAZ −1'de düzeltildi) + **yeni**
`tests/test_MIMARI_dosya_atiflari_var.py`: MIMARI'de anılan her `tests/test_*.py`
**gerçekten mevcut** olmalı. *(Bu kapı, kurulduğu gün ilk avını yaptı: A6'yı düşürdü.)*

#### `A5-KOMUT` — sayı üreten kutu *(D2)*

```bash
cd backend
find tests -name 'test_*.py' | wc -l                    # test dosyası
grep -rhcE '^\s*def test_' tests/*.py | paste -sd+ | bc # test fonksiyonu
wc -l lab/nl_accuracy.py app/cube_router.py app/routers/ask.py
ls migrations/versions/*.py | wc -l                      # migration
grep -oE '"[a-z_]+:[a-z_]+"' control_plane/authorize.py | sort -u | wc -l   # izin
grep -rhoE '@router\.(get|post|put|patch|delete)' app/routers/*.py | wc -l # uç
ls app/routers/*.py | wc -l                              # router dosyası
```

#### ⛔ KÜTÜK — **A6 geri çekildi** *(D5: silinen madde iz bırakır)*

| | |
|---|---|
| **İddia** | *"`tests/test_member_sweep.py` **YOK** — MIMARI'nin kendi «beyan var, kod yok» satırı"*, kanıt olarak `grep -rl member_sweep → boş` |
| **Ölçüm** | Dosya **VAR**: `backend/tests/test_member_sweep.py`, **113 satır**, 5 test fn (`test_her_OLCU_gercekten_calisir` · `test_her_BOYUT_gercekten_calisir` · `test_her_ZAMAN_BOYUTU_kovalanabiliyor` · `test_ILISKI_TUREVI_boyutlar_JOIN_uretiyor` · `test_katalog_bos_degil`). Commit `f5f4048` *"faz 1.2/G8: üye taraması"* ile inmiş |
| **Yargı** | Maddenin **kanıt cümlesi yanlıştı** → madde düşer. MIMARI §5'in söylediği iş (**her üye gerçekten koşuyor mu**) o dosyada **yapılıyor**. Yalnız `LIMIT 0` ifadesi literal değil (dosyada `LIMIT 0` geçmiyor, üyeler **gerçekten** çalıştırılıyor) — bu bir **fazlalık**, boşluk değil |
| **Ders** | 🔴 *"Ölçüm aracının kendisi de bir bağımlılıktır"*: `grep -rl member_sweep` **boş dönemez**, çünkü ad hem dosya adında hem MIMARI'de geçer. Sürüm 1'in kanıtı **hiç koşulmamış** bir komuttu. **Kanıt cümlesi de kanıt ister.** |

### −1.2 · Kutu B — `⟳ YÜRÜRLÜKTE` bloğu  [bayraksız: belge]
**NE** backend: — │ sözleşme: — │ frontend: — (**`api-only`**, gerekçe: belge maddesi) │
belge: `MIMARI.md`'ye §1 öncesi **toplu `⟳` indeksi** — yol haritasının otorite aldığı
her başlık, otoriteyi alan faz ve `⟳ UYGULANMADI` damgasıyla.
**KAPI** `tests/test_beyanlar_curumesin.py` — satır başına **tuzak** + tablonun **yapısal
işaretçi biçimi** (dört hücre · `Durum == ⟳ UYGULANMADI` · otorite fazı).
> *(Denetim düzeltmesi: `D5` belge kapısı bu maddeyi **`NE`/`KAPI` taşımıyor** diye
> yakaladı — 130 maddenin **tek** eksiği buydu. Kapı kurulduğu gün ilk avını yaptı.)*

🔴 **Bağlayıcı kısıt:** `⟳` bloğu **ASLA BİR KURAL BEYAN ETMEZ; yalnız OTORİTE İŞARET
EDER.** İçinde *"yeni kural şudur"* cümlesi **bulunmaz**; *"bu başlıkta yol haritası §X
kazanır, **ve henüz uygulanmadı**"* bulunur. Yanlış anlaşılacak beyan yoksa *"yapılmış
zannetme"* riski de yoktur.

| MIMARI § | Konu | Otorite | Durum |
|---|---|---|---|
| §3 · §3.3 | semantik katman · compose birleştirme semantiği | FAZ 2.1 | ⟳ UYGULANMADI |
| §3.4 | `rowLevelAccessControls` (⏳ sıradaki) | FAZ 1.1 | ⟳ UYGULANMADI |
| **§3.4** | *"Bilerek ALINMAYANLAR: … `osi` — bugün müşteri senaryosu yok"* | **FAZ 3.4 · 4.5** — karar **geri alındı**, gerekçe [KANIT §2.1] | ⟳ UYGULANMADI |
| **§4** | **Değişmez 2/3 (read-only) — ajan yazma yasağının kademelenmesi** | **FAZ 6.1 → 6.2** | ⟳ UYGULANMADI |
| §5 | yapılmayacaklar — **hiçbir satır kaldırılmıyor**; grain sözleşmesi **yeni satır ekler** | FAZ 2.1 | ⟳ UYGULANMADI |
| §7 | ölçüm sözleşmesi — çerçeve (A1) + CI kapıları + risk-kapsam | FAZ 4 | ⟳ UYGULANMADI |
| §9 | hedef mimari — **metrik katmanı** merdivene giriyor | **FAZ 2.2** | ⟳ UYGULANMADI |
| §11 | agentic — yetki granülerliği + onaylı yazma | FAZ 1.3 · 6.1 | ⟳ UYGULANMADI |
| §12 | konuşma — **6./7./8. tür**; uyuyan çapa kuralları → **FAZ 0.5** | FAZ 0.5 · 5.1 · 5.2 | ⟳ UYGULANMADI |
| **§13** | görsel dilbilgisi — `viz.recommend()` **yeni dallar** + dönüş `VizSpec \| list[VizSpec]` | **FAZ 5.11 · 5.12** | ⟳ UYGULANMADI |
| §14 | arka-ön sözleşmesi — **iki kapının kör noktaları** | FAZ 0.14 | ⟳ UYGULANMADI |
| §8.2 | ADR'ler — **dosyalar üretilecek** | FAZ 4.7 | ⟳ UYGULANMADI |

> ⛔ **Sürüm 1'de vardı, SİLİNDİ:** *"§9.2 — ölçü + başka cube'un BOYUTU ifade edilemez"*.
> Denetim ölçtü: o olmayan-hedef `0a1a087`'de **`⟳ FAZ B1` bloğuyla açıkça geri çekildi**
> (*"bu satırla çelişiyordu ve yanlıştı"*). §9.2'de duran madde *"Ölçü-A × Ölçü-B tek
> CubeQuery'de olamaz"* — **farklı bir şey**. Var olmayan bir satıra ⟳ konulamaz.

### −1.3 · Kutu C — **tuzak testleri**  [bayraksız: kapı]
**NE** Her `⟳` satırı için `tests/test_beyanlar_curumesin.py`'ye bir tuzak.
**NASIL** Desen **kanıtlanmış**: aynı dosya, MIMARI Faz 4 indiği gün *"plan seçimi yok"*
beyanını **kırdı** — MIMARI'nin kendi kaydı: *"bu beyan bir **TUZAKTI** … kurulduğu iş buydu."*
**KAPI** Faz indiğinde test **kırılır** → `⟳` silinir, yerine ölçümlü `✅` yazılır, tuzak
**ters çevrilerek** korunur.
**SONUÇ** Belge güncellemesi **CI zorunluluğu** olur.

---

## FAZ 0 · TEMİZLİK ve KAPILAR *(**25 madde** — her şeyin ön koşulu)*

**NEDEN** Aşağıdaki maddelerin **dördü** (0.2 · 0.6 · 0.8 · 0.12) yol haritasının dayanacağı
**kapıları kör bırakıyor**. Kapılar onarılmadan yazılan 150+ madde *"kapı yeşil"* diye
**yanlış-pozitif** rapor eder.

> 🔴 **KOŞUM SIRASI — madde NUMARASI sıra DEĞİLDİR (sürüm 8, `KAT-3` denetimi).**
>
> Bir denetim turu FAZ 0'ın **kendi içinde DÖRT `KAT-3` ihlali** buldu: *"bir katman,
> kendisini besleyen katmandan önce inşa edilmez"* kuralı, kuralın **yazıldığı fazda**
> çiğnenmiş. Numaralar **konu başlığına göre** dizilmiş, **bağımlılığa göre** değil —
> ve §A.5'in kendi tablosu bu sınıfın *"hiçbiri yanlış görünmüyor"* olduğunu zaten söylüyor.
>
> | # | İhlal | Neden ağır |
> |---|---|---|
> | **1** | `0.4` ← **`0.16`** | `0.4` bir **ölçüm KARARI** (bayrağı `alpha`'ya aç, A/B koş); `0.16` **ölçüm ALETİNİ** kurar (ayrılmış kota + fail-closed). Alet **12 madde geride**. Ve bu sınıf **zaten üç kez** tekrarladı — `c4b14d1`'in *"`--live` ÜÇÜNCÜ kez karşılıksız koştu"* kaydı dâhil. Bugünkü sırayla koşulursa **dördüncüsü** olur |
> | **2** | `{0.3, 0.10b, 0.23}` ← **`0.14`** | Üçünün de **KAPI**'sı `0.14`'ün ürünü (K4 · K2/(c)). Ve belge **kendisiyle çelişiyor**: `0.23` *"hiçbir şeye bağımlı değildir — ilk inebilir"* diyor, ama kapısı `K2/(c)`. **Kapısız inen düzeltme**, bu belgenin kendi doktrininin (*düzelt → kapıya çevir*) ihlalidir |
> | **3** | `{0.4, 0.5b, 0.12, 0.18}` ← **`0.19`** | `0.19` **PAYDAYI değiştirir** (kartezyen tur → semantik vaka); dördü de eşiğini **eski paydada** ilan ediyor. 🔴 En sert sonuç: **`0.18` bugünkü sırayla kendi kazancını ABARTARAK raporlar** — *"turların ~%18'i"* doğrudan kartezyen şişmeden gelir ve `0.19`'un kendi `NEDEN`'i bunu söyler |
> | **4** | `0.21` ← `{0.2, 0.5, 0.5b, 0.18, 0.22}` | `0.21` `ask.py`'nin satır sayısını **tavan** yapar; o beş madde ona **satır ekler**. Önce inerse kapıyı kırarlar; sonra inerse **şişmiş tavanı** kilitler — yani kapı hiç iş görmez |
>
> **BAĞLAYICI KOŞUM SIRASI** *(madde numaraları DEĞİŞMEZ — `D5` gereği taşıma yapılmaz,
> yalnız **sıra** yazılır):*
>
> ```
> 1. 0.22 · 0.2 · 0.23     ← ucuz + bloklayıcı üçlü (~1 oturum): duran çökme ·
>                            kaybolan makbuz · ekranda olmayan üç özellik
> 2. 0.1                   ← taban: fazın gerçek kapsamını sayıyla belirler
> 3. 0.16                  ← ÖLÇÜM ALETİ (kota) — her "önce ölç" kapısının ön koşulu
> 4. 0.14                  ← KAPILAR (K1..K5); 0.3/0.10b/0.23'ün kapısı burada kapanır
> 5. 0.19                  ← PAYDA; eşik ilan eden her madde bundan SONRA
> 6. 0.18                  ← hakem (kazancı artık DÜRÜST paydada ölçülür)
> 7. 0.4 · 0.5 · 0.5b      ← ölçüm kararları ve bağlam maddeleri
> 8. kalan (0.3 · 0.6–0.13 · 0.15 · 0.17 · 0.20)
> 9. 0.21                  ← EN SON, ve tavanı **FAZ 0 ÖNCESİ** ölçümden alarak;
>                            FAZ 0'ın eklediği satırlar madde-madde MUAF yazılır
> ```
>
> ⚠ **`0.23` istisnası yazılı olsun:** düzeltmesi küçük ve riski sıfır olduğu için **1.
> adımda iner**, ama kapısı `0.14`'te **geriye dönük** kapanır. *Kapısız inen bir madde
> "bitti" sayılmaz* — bu istisna maddenin kendi `KAPI` satırına da işlenmiştir.

### 0.1 · Yeniden ölçüm turu  [bayraksız: ölçüm]
**NE** backend: `lab/faz0_taban.py` — [KANIT §0.1]'in 12 kusuru + §C'nin **1a…12** ölçütü
**güncel HEAD'de** yeniden ölçülür; yalnız **hâlâ açık olanlar** iş listesine girer │
sözleşme: — │ frontend: — (**`api-only`**, gerekçe: çıktısı bir **ölçüm artefaktıdır**,
kullanıcıya dönük bir yüzey doğurmaz; §C **13-16** kullanıcı-sonucu ölçütleri kapsam
dışıdır ve sahipleriyle `[ÖLÇÜLMEDİ]` kalır)
> *(Denetim düzeltmesi: `D1` beyanı ilk sürümde **yoktu** — muafiyet meşruydu ama
> **yazılmamıştı**; bu fazın diğer altyapı maddeleri (`0.15`·`0.16`·`0.17`·`0.19`)
> hepsi `api-only` gerekçesini taşıyor.)*
**KAPI** Çıktı: `lab/reports/faz0_taban.md` — her satır `<sayı> @<sha> · <komut>` (D2).
**SONUÇ** Faz 0'ın gerçek kapsamı **sayıyla** belirlenir.

### 0.2 · ⭐ Planlayıcı makbuz çöküşü  [bayraksız: hata]
**NEDEN** `sec()` uydurma araç adını `kapisiz=False` ile kaydediyor → `Kosum.sorgu_sayisi`
(`planner.py:113`) `tools.get()` (`:120`) çağırıp **`KeyError`** atıyor → `agent_run`
makbuzu **tamamen düşüyor** (`ask.py:386-388`); `_butce_kapisi` (`planner.py:215`) de aynı
yoldan patlıyor ve `ask.py:364-368` **`continue`** ile yutuyor → **bütçe kapısı sessizce
atlanıyor**. Canlı doğrulandı. [KANIT §0.1-1]
**NE** backend: `sec()` reddi `kapisiz=True, dis_maliyet="sifir"` ile kaydedilir │
sözleşme: değişmez │ frontend: değişmez (`api-only` — mevcut `agent_run` render'ı yeterli)
**NASIL** Tek satır; `Adim(hata="SEÇİM REDDİ…")` deseni zaten var.
**KAPI** `tests/test_orkestrator.py::test_uydurma_arac_makbuzu_dusurmez` — uydurma ad içeren
plan → `agent_run` **üretiliyor**, `SEÇİM REDDİ` adımı görünüyor, bütçe kapısı **atlanmıyor**.
**SONUÇ** Planlayıcının **en çok denetlenmesi gereken** anda (model yanıldı) makbuz **var**.
**GERİ AL** — (hata düzeltmesi; `git revert`).

### 0.3 · ⭐ Tuval rozet sadakatsizliği  [bayraksız: §5 ihlali]
**NEDEN** `AnalysisCanvas.tsx:314-323` `SourceBadge`/`explain` **basmıyor** (dosyada
`SourceBadge` **0**, `explain`/`confidence` **0**) → Discovery cevabı tuvalde **`▚ LLM`
rozetsiz**. MIMARI §5: *"bir cevabın `source`'unu gizlemek/eşitlemek"* **yasak** — rozet
süs değil **sözleşme**. [KANIT §0.1-2]
**NE** backend: — │ sözleşme: — │ frontend: `AnalysisCanvas`'a `SourceBadge` +
`explain.confidence` (ve **PK-24**: tuval kırpması bir daha doğmasın)
**NASIL** `ChatPanel.SourceBadge` **yeniden kullanılır**, ikinci render edici **yazılmaz**.
**KAPI** **K4** (yeni): `tests/test_yuzey_sadakati.py` — *"aynı `source` her yüzeyde aynı
rozeti üretir"*; `viz` için var olan `test_faz_I4_I5` deseni genişletilir.
**SONUÇ** Aynı cevap iki yüzeyde **aynı garantiyi** beyan eder.
**GERİ AL** — (görünürlük eklemesi).

### 0.4 · Netleştirme önceliği — **ÖLÇÜM KARARI**  [bayrak: `netlestirme_onceligi` = `off`]
> ⚠ **Denetim düzeltmesi — İŞ ZATEN İNDİ.** `ff987eb` ile bayrak (`app/features.py:147`,
> `demo/packs/features.yml:43 = "off"`), kapı (`ask.py:2378`), netleştirici (`ask.py:2171`)
> ve `tests/test_netlestirme_onceligi.py` (144 satır) **yazıldı**. Sürüm 1'in *"yapılacak"*
> maddesi ve `ask.py:2399` atfı **geçersiz**.

**NEDEN** Deterministik olarak **bilinen** ölçü belirsizliğini olasılıksal bir 2/3 oyu
eziyordu; mekanizma indi, **kazanç/kayıp ölçülmedi**.
**NE** backend: — │ sözleşme: — │ frontend: — │ **ölçüm**: bayrak tek test kullanıcısında
`alpha`'ya açılır, A/B koşulur.
**KAPI** `lab/nl_corpus.py --kapi` öncesi/sonrası: **kapanan sessiz-yanlış** (yanlış-cube
azalması) vs **kapsam kaybı** (`CLARIFY:konu` artışı). **Kayıp > kazanç ise `off` kalır ve
nedeni `MIMARI.md`'ye yazılır.**
**GERİ AL** bayrak zaten `off`.

### 0.5 · ⭐ Çapa zincirini uyandır  [bayrak: `capa_zinciri`]
**NEDEN** `Baglam`'ın `KURAL_CAPA`/`COKLU`/`CELISKI` kuralları **üretimde HİÇ ateşlenmiyor**
— `coz()`'ün tek çağıranı `ask.py:1470` ve `capalar=` **hiç geçilmiyor** (`grep -n "capalar="
backend/app/routers/ask.py` → **0 isabet** @`c4b14d1`). `SureklilikOlcumu` **hiç
çağrılmıyor**. **19 altın vakalı** (`test_baglam_cozucu.py`), testli bir modül **ölü**.
[KANIT §0.1-4]
> ⚠ **GEREKÇE GÜNCELLEMESİ (sohbet raporu B4 — doğrulandı):** `ask.py:1466`'nın yorumu
> *"thread paneli Faz H4'te yeniden kurulacak"* diyor; **panel 2026-08-01'de kuruldu**
> (`ReportPanel` + `reply`/`reply-multi` mutation'ları; `page.tsx`'te
> `anchor = t?.items[vars.anchorIndex]`). İstemci çapayı **zaten biliyor** — onu genel
> `cube_query` yuvasına **düzleştiriyor**, bu yüzden `KURAL_CAPA` değil hep `KURAL_YAPISAL`
> çalışıyor. **Engel kalktı; kalan iş TEK ALAN:** `AskRequest.reply_to_cube_query`.
> Madde **küçüldü**, kapsamı değişmedi. *(`ask.py:1466`'nın yorumu bu madde inerken
> **güncellenir** — yoksa bayat bir gerekçe kodda kilitli kalır.)*
**NE** backend: `coz(..., capalar=…)` bağlanır; `SureklilikOlcumu` `/ask`'e │
sözleşme: `AskRequest.reply_to_cube_query: dict | None` │ frontend: `ReportCard`'da karta
yanıt verirken gönderilir + **çok-kart seçimi**
**NASIL** Modül **hazır**; yalnız çağrı yolu ve istemci alanı eklenir.
**KAPI** `lab/konusma_senaryolari.py`'ye **önce KIRMIZI** bir sınıf (`capa_karta_yanit`),
sonra yeşil. `SureklilikOlcumu` oranı raporlanır.
**SONUÇ** Karta-yanıt ve çok-kart kesişimi **gerçekten** çalışır; süreklilik **ölçülebilir**.
**GERİ AL** bayrak `off` → `capalar` geçilmez, bugünkü davranış birebir.

### 0.5b · ⭐ Bekleyen netleştirme — **DURUMSUZ**  [bayrak: `netlestirme_kapanisi`] *(sohbet raporu M4/B3)*
> 🔴 **KENDİ BAYRAĞI VAR — ve bu bir düzeltmedir.** Sürüm 4 bu maddeyi 0.5 ile **aynı
> `capa_zinciri` bayrağına** bağlamıştı. **Çelişki:** M.6/4 *"0.5b **TEK BAŞINA**, kendi
> ölçüm turuyla … diğerleriyle birleşirse sapmanın **SAHİBİ bulunamaz**"* diyor, ama
> **tek bayrak iki bağımsız ölçüm turu veremez.** İki senaryo da kırıktı: (a) 0.5 önce iner,
> bayrak `on` olur → 0.5b merge edildiği an **kapısız canlıya çıkar**; (b) ikisi birlikte
> iner → **`CLARIFY:dönem` sapmasının sahibi bulunamaz.** İkisi de [KANIT §8.3]'ün
> `elektrik` dersinin ihlali. → **`netlestirme_kapanisi` ayrıldı; 0.5 `capa_zinciri`'nde kalır.**
> **Bağımlılık yönü korunuyor:** 0.5b, 0.5'in `reply_to_cube_query` alanına **dayanmaz** —
> kendi `netlestirme_kapanisi` alanını taşır. İkisi **bağımsız inebilir**.
**NEDEN** 0.5'in **kardeşi ama AYRI işi**: 0.5 çapa kuralını uyandırır, bu madde
**netleştirmeye verilen cevabı bağlar**. Ölçüldü @`c4b14d1` (kendi betiğimle, raporun
sayımından **bağımsız olarak yeniden üretildi**): netleştirme dallarından **2'si**
`cube_query` iliştiriyor (`ask.py:1903` · `:1913` — dönem kapısı, **doğru desen ZATEN
KODDA**), **10'u iliştirmiyor**. *Onda dokuzu bağlamıyor.*
Kullanıcı chip'e **TIKLARSA çalışır, YAZARSA çalışmaz**: *"fire olan"* → `cube_query=None`
→ `KURAL_TAZE` → yepyeni soru sanılır. **Sistem soruyor, cevabı anlamıyor** — şikâyetin
(*"beni anlamıyor"*) en saf, en ölçülebilir hâli budur.
**NE** sözleşme: `AskResponse.bekleyen_netlestirme: dict | None`
`{ id, soru, kismi_cube_query, secenekler[{etiket,deger,cube_query}], serbest_metin_kabul }`
\+ `AskRequest.netlestirme_yaniti: dict | None` → `{id, deger}` ya da `{id, serbest}` │
backend: `ask()` **GİRİŞİNDE**, bağlam çözümünden **ÖNCE** —
`body.question = netlestirme.birlestir(body.netlestirme_yaniti, body.question)` ve
`body.cube_query = …get("kismi_cube_query") or body.cube_query` │
frontend: `Turn`'ün **chip'leri VE komposeri** `netlestirme_kapanisi` gönderir
**NASIL** `app/netlestirme.py::birlestir` **saf fonksiyon** (~40 satır, izole testli —
`context.py` felsefesi). **İKİNCİ CEVAP HATTI YAZILMAZ:** parçalı soruyla cevabı birleştirip
**tam soruyu** kurar, sonrası var olan hat. `Suggestion` **genişletilmez** (`{label,query}`'de
`query` = *yeniden sorulacak soru*; aynı tipe *"bir soruya verilen cevap"* yüklemek iki
söz-edimini bindirirdi). ⚠ Gerçek kısmi durumu **olmayan** dala (typo, katalog dökümü)
**hiçbir şey iliştirilmez** — *uydurma bağlam, bağlamsızlıktan kötüdür.*
**DURUMSUZLUK NEDEN YETERLİ:** N+1. turu yorumlamak için gereken her şey, N. turda
**sunucunun kendi yazdığı** pakette. Sunucu-tarafı bellek TTL/eviction ister (yok),
çok-worker'da paylaşımlı store ister (yok) ve **resume'da hayatta kalmaz** —
`answer.py::_persist_message` tüm payload'ı kaydettiği için istemci-taşımalı alan sohbet
yeniden açılınca **bekleyen soruyla birlikte** geri gelir.
**KAPI** `tests/test_netlestirme_yaniti.py` (yeni): tıklama **VE** serbest metin **aynı
rapora** çıkar · `lab/netlestirme_paydasi.py`'nin döndürdüğü kümenin **HEPSİ**
`bekleyen_netlestirme` taşır — 🔴 **sabit sayı YAZILMAZ**, payda betikten gelir (yoksa payda
yanlışsa kapı **eksik kapatır**) · `yol_siniri` kümede **DEĞİL**, gerekçesi yazılı.
🔴 `lab/nl_corpus.py --kapi`: `CLARIFY:dönem` **%13,6'dan ±0,5 puan SAPMAZ** (§C/3).
Sapma → bayrak `off` kalır, gerekçe `MIMARI.md`'ye yazılır (0.4 disiplini).
**SONUÇ** Netleştirme, tek yönlü bir uyarı olmaktan çıkıp **kapanan bir söz alışverişi** olur.
**GERİ AL** `netlestirme_kapanisi=off` → iliştirme yok, frontend alanları `useFeature()`
arkasında. Davranış **birebir** bugünkü. **0.5'in `capa_zinciri`'si etkilenmez** — iki
bayrak, iki bağımsız geri alma, **iki ayrı ölçüm turu**.

> 🔴 **PAYDA ELLE SAYILMAZ — `lab/netlestirme_paydasi.py` bu maddeyle AYNI COMMIT'te iner.**
> Kriter betiğin **içine yazılır**; **maddedeki `2` ve `10` bir KAPI EŞİĞİ DEĞİL, bir
> ölçüm anlık görüntüsüdür** (damgası ve komutu bu kutuda — D2). Kapı **betiğin döndürdüğü
> kümeyi** arar, sabit sayıyı değil. Yazılı kriter: bir dal
> *bekleyen netleştirme* sayılır ⟺ `source is None` **ve** `note` var **ve**
> (`suggestions` ∪ `next_steps`) boş değil **ve** soru **kullanıcının kastettiği şeye**
> dair.
>
> **İki sınır vakası — ikisi de kümeden ÇIKAR, gerekçeleri farklı:**
> - `ask.py:2553` `yol_siniri`: chip'i var ama *"ne demek istedin?"* sormuyor, *"senin
>   ayarın engelledi"* diyor. Bekleyen bir **anlam** sorusu yok → **dışarıda**.
> - 🔴 `ask.py:1750` **konuşma dalı**: `cube_query=prev_cq` iliştiriyor, yani mekanik
>   filtreye *"iliştiren"* diye takılır — ama bu bir **netleştirme değil**, cevabın kendisi
>   (bkz. **0.23**). Betik onu **dışlamazsa payda şişer ve kapı yanlış yerde yeşil verir.**
>   *(Bu satır bu belgenin kendi ölçümünden geldi: ham filtre 3 iliştiren döndürdü, ikisi
>   gerçek.)*
>
> ```bash
> docker run --rm --network none -v "$PWD/backend:/app" -w /app dima-test \
>   python lab/netlestirme_paydasi.py      # → küme + sayı + her dalın satırı + dışlananlar
> ```

### 0.6 – 0.11 · Yetim uç/alan temizliği  [bayraksız: yetim]
**NEDEN** [KANIT §14.2]'nin envanteri; **8'i de denetimde tek tek doğrulandı**.

| # | Yetim | Eylem | KAPI |
|---|---|---|---|
| 0.6 | `GET /contracts` (liste) **tüketicisiz** | **Kanıt geçmişi** görünümü — `ContractDetailPanel`'in giriş listesi (**yeni panel değil**, PK-3) ya da `API_ONLY` beyanı | K1 |
| 0.7 | `POST /query` + `runQuery()` **ölü** (sıfır çağıran) | Sarmalayıcı **silinir** ya da uç `API_ONLY` | K1 |
| 0.8 | `agent_run.steps[].receipt` (yalnız `types.ts:74`) | Adım satırına makbuz kimliği, tıklanınca `/contracts/{id}` | K2 |
| 0.9 | `explain.path` (tip var, render yok) | Trace bloğuna eklenir ya da modelden çıkarılır | K2 |
| 0.10 | `interpret`'in `"top"` fact'i **sessizce düşüyor** (`interpret.py:113` üretiyor, `OutputInsight.tsx:24` `FACT_ICON`'da yok, `:38` filtresi eliyor) **+ 🔴 aynı dosya HAM KOLON ADI basıyor** — bkz. **0.10b** | `FACT_ICON`'a `top` **+ görünen adlar** | K2 |
| 0.11 | `DecisionIn.supersedes` **yazılamıyor** · `DrillResponse.kpi_components` · `AskRequest.execute`/`limit` | 🔴 **`supersedes` BAĞLANIR** (silinmez — **II-E.7 ona dayanıyor**); diğer ikisi bağlanır ya da modelden çıkarılır | K2 |

### 0.10b · ⭐ **Görünen adlar** — `interpret` iç ad basmayı bırakır  [bayraksız: yetim] *(sohbet raporu M2/B5)*
**NEDEN** `interpret.py` fact metnine **ham küp kolon adı** koyuyor (`{measure}` · `{dim}` ·
`{m0}` doğrudan f-string'e giriyor; ölçüldü @`c4b14d1`) → `OutputInsight.tsx:55` **aynen**
gösteriyor. Kullanıcının okuduğu satır:
> *"toplam_fire_kg: Oca→Ara %12,4 arttı (1.240 → 1.394) — olumsuz"*

**Doğrusu AYNI DEPODA var ve gerekçesi de yazılı:** `eylem.py:234-243 _rapor_adi()`
`build_catalog`'dan `measure_synonyms_display` / `dimension_labels` okuyor ve şunu söylüyor:
*"oradan etiket türetmeye çalışmak `ort_oee` gibi bir **iç ad** basardı ve kullanıcı
**onaylayacağı şeyi okuyamazdı**."* Aynı disiplin `interpret.py`'ye **uygulanmamış**.
🔴 **Kritik yan etki:** bu metin `answer.py::_anlati_ekle`'de LLM'e `gercekler` **GİRDİSİ**
oluyor → `t2_anlatici` açılırsa model `toplam_fire_kg` **etrafında cümle kurar**. Akıcı ama
iç adlı bir cümle robotikliği kaldırmaz, **üstüne para ödetir**. → **0.10b, `t2_anlatici`'nin
SERT ÖN KOŞULUDUR** (§F.2).
**NE** backend: `interpret(..., etiketler: dict[str,str] | None = None)` │
sözleşme: — (`facts[].text`'in **İÇERİĞİ** değişir, **ŞEKLİ** değil) │
frontend: `FACT_ICON`'a `top` — tek satır (0.10'un kendisi)
**NASIL** `answer.py`'deki **var olan** cube döngüsü zaten `units`/`lower_is_better`
topluyor; etiketler **oraya** eklenir. Yeni I/O yok. 🔴 **İKİNCİ ETİKET KAYNAĞI AÇILMAZ** —
`eylem.py:241`'in kendi uyarısı: *"bu depoda «ikinci bir etiket kaynağı» deseni **beş kez**
ayrışmayla sonuçlandı."*
**KAPI** `tests/test_interpret.py`: etiket verildiğinde ham ad **GEÇMEZ**; `etiketler=None`
iken metin **BİREBİR** bugünkü (geriye uyum). `tests/test_yuzey_sadakati.py` (0.14/K4)
**metin tarafına** genişler: *"aynı ölçü her yüzeyde aynı adı taşır."*
**SONUÇ** Kullanıcı **kendi sözlüğünü** okur; ve LLM anlatıcısı açıldığında **doğru
girdiyle** açılır.
**GERİ AL** Bayraksız (`etiketler=None` → bugünkü çıktı). **Bilinen maliyet:**
`test_interpret.py`'nin metin iddiaları güncellenecek.

### 0.12 · Taban tazeliği  [bayraksız: kapı]
> ⚠ **Denetim düzeltmesi:** `eval/baseline.json` **BAYAT DEĞİL** — `n=129`, `cases.yaml`'ın
> **det diliminin tamamı** (119 vaka / 133 adım, det = 129). Sürüm 1'in gerekçesi yanlıştı.
> **Gerçekten bayat olan:** `lab/nl_corpus_baseline.json` — **%86,3** taşıyor, ölçülen
> **%93,2**. Kapı **yanlış tabana** karşı koşuyor.

**NE** `nl_corpus_baseline.json` tazelenir (`_turlar`'a yeni tur eklenir, kök **dokunulmaz** —
KURAL A) · `nl_accuracy.py`'nin monkeypatch imzaları `(self, *a, **k)`'ya esnetilir
(`nl_corpus`'u haftalarca sessizce bozan sınıfın aynısı).
**KAPI** `tests/test_korpus_taban_kapisi.py` genişletilir: taban dosyasının **son turu** ile
canlı koşum arasındaki fark **tolerans içinde**; taban **kaç gün eskidiyse** raporlanır.

### 0.13 · Sosyal sınıf teslim borcu  [bayrak: `sosyal_sinif`]
**NE** `test_sosyal_sinif.py:121-123` ad↔iddia çelişkisi (`test_..._None_DEGIL_...` ama
`assert ... is None`) · tüketici sayısı yorumları (3 yerde 2/3/4; **gerçek 4**) ·
`MIMARI.md:811` düzeltmesi (−1.1/A2) · **bayrak eklenir** · faz adı çakışması çözülür.
**KAPI** `tests/test_bayrak_kaydi.py` — `sosyal_sinif` `FLAG_REGISTRY`'de.
**NEDEN** MIMARI §6.13z/9.11: *"bir kill-switch yalnız KOD'da varsa **yarımdır**."*
*(⚠ Bu bir bölüm numarası değil, §6.13z içindeki madde numarasıdır — §E.1.)*
**GERİ AL** `sosyal_sinif=off` → `sosyal_ayikla` `route()` girişine **müdahale etmez**, bugünkü
davranış birebir. ⚠ **Bayrak bu maddede EKLENİYOR** — yani geri alma yolu **şu anda yok**;
teslim borcunun asıl parçası budur (§6.13z/9.11: *"kill-switch yalnız KOD'da varsa yarımdır"*).

### 0.14 · ⭐ **Beş entegrasyon kapısı**  [bayraksız: kapı]
**NEDEN** 🔴 **K1 ve K2 bugün KÖR NOKTALARIYLA YEŞİL.** Bu belgenin 100+ maddesi bu kapılara
dayanacak; kapı yanlış-pozitifse belge boyunca *"kapı yeşil"* diye raporlanan şey bir
**yanlış-pozitif** olur — §6.4'ün (*"ölçüm aracının kendisi de bir bağımlılıktır"*) kapı
eksenindeki hâli. K5'in dosyası (`test_panel_sayisi.py`) **hiç yok**.

| Kapı | Bugün | Eylem | Dosya |
|---|---|---|---|
| **K1** yetim uç | ⚠ `_aranan()` `re.search` kullanıyor → `/contracts` ⊂ `/contracts/${cid}` | **tam yol** eşleştirme + *"sarmalayıcı var, çağıranı yok"* tespiti (`api-client.ts` export'larının çağrı sayımı) | `tests/test_uc_yetim_degil.py` |
| **K2** yetim alan | 🔴 **ÜÇ kör noktası var** — (a) yalnız `AskResponse.model_fields` (1. seviye) · (b) yalnız `AskResponse` · (c) 🔴 **YENİ: yalnız «alan adı FE kaynağında GEÇİYOR mu»** (`ad not in metin`) — *ulaşılabilir mi* diye **sormuyor** | (a) **iç içe alanlar** (`agent_run.steps[].receipt`) · (b) `DrillResponse`/`ContributionResponse`/`DecisionIn`/`AskRequest` · (c) ⭐ **ERİŞİLEBİLİRLİK boyutu** — alan, onu **üreten yanıt sınıfında** render'a ulaşabiliyor mu | `tests/test_cevap_alani_yetim_degil.py` |
| **K3** **TERS yetim** | yok | **Tanım:** frontend'in çağırdığı ama backend'in **vermediği** alan/uç. `types.ts`'teki her alan `schemas.py`'de karşılığı olmalı. Bugün temiz — **kapı temiz kalsın diye kurulur** | `tests/test_ters_yetim.py` (yeni) |
| **K4** **yüzey sadakati** | yalnız `viz` | **rozet/makbuz/`explain`**'e genişletilir (0.3) | `tests/test_yuzey_sadakati.py` (yeni) |
| **K5** **panel sayısı** | 🔴 **ölçüldü: export 13 / dosya 12** — sürüm 3 burada *"11"*, §C/11'de *"12"* diyordu (**belge kendi içinde çelişiyordu**) | **ÖNCE TANIM** (§C/11 kutusu: **export** sayımı, `export default` dahil), **SONRA** sayı, **SONRA** test. Tavan v1'de **13**, Bölüm II'de **15** (PK-23) | `tests/test_panel_sayisi.py` (yeni) |

> 🔴 **K2'nin (c) BOYUTU NEDEN AYRI BİR KEŞİF — ve neden kapının kendisi hakkında:**
> Kapı bugün *"alan adı frontend kaynağında **geçiyor mu**"* diye soruyor
> (`ad not in metin`, `test_cevap_alani_yetim_degil.py`). `contribution`, `ReportCard.tsx`'te
> **geçiyor** → kapı **yeşil**. Ama alan, onu üreten yanıt sınıfında (`result=None`)
> **ULAŞILAMAZ** — çünkü `ReportPanel` o cevabı `ReportCard`'a hiç göndermiyor (**0.23**).
> Kapı *"var mı"* soruyor; sorması gereken ***"ulaşılabilir mi"***. Bu, bu deponun kendi
> avladığı *"beyan var, kod onu tanımıyor"* sınıfının **KAPI TARAFINDAKİ** hâlidir.
>
> ⚠ **Ve körlük SINIFSAL, tek vaka değil:** aynı yanlış-pozitif **ikinci, bağımsız bir
> kapıda** da var — **deneyim süiti** (`lab/deneyim.py`, §F.1) **API cevabını** ölçüyor,
> **render'ı değil**; `S2` (*"≥3 olgu + anlatı + ≥2 chip"*) `ask.py:1750`'nin cevabında
> **hepsi dolu** bulup **YEŞİL** raporluyor, kullanıcı ise **hiçbirini görmüyor**
> (§F.1/S8). **İki bağımsız kapının aynı körlüğü paylaşması, körlüğün sınıfsal olduğunun
> kanıtıdır** — 0.23 bir **vakayı** kapatır, K2/(c) + `S8` **sınıfı** kapatır.

---

> 🔴 **AŞAĞIDAKİ SEKİZ MADDE DIŞ DENETİMDEN GELDİ** (`u-anda-bir-plan-tingly-fox.md`).
> Sekizinin de gerekçesi **bu belgenin kendi doktrinini** bana karşı kullanıyor ve **haklı**;
> her biri kod ölçümüyle **teyit edildi**.
**NE** backend: beş kapı testi (ikisi genişler, üçü yeni) │ sözleşme: — │
frontend: — (`api-only`, gerekçe: **CI kapı altyapısı**; kapılar frontend **kaynağını**
tarar ama kullanıcıya yüzey açmaz)
**NASIL** K1/K2 **var olanı genişletir**; `_fe_metni()` yardımcısı **yeniden kullanılır**,
ikinci tarayıcı **yazılmaz**. K3/K4/K5 yeni dosya ama **yeni desen değil** — üçü de aynı
*"iki tarafı karşılaştır"* iskeletini paylaşır.
**KAPI** Kapıların **kendisi** kapıdır; ek olarak **D5'in belge kapısı**
(`tests/test_yol_haritasi_butunlugu.py`) aynı turda yazılır — kod kapıları ile belge kapısı
**aynı disiplinin iki yüzü**.
**SONUÇ** Belgenin *"kapı yeşil"* raporları **güvenilir** olur; §C/7'nin *"yetim 9 → 0"*
hedefi **ölçülebilir** hâle gelir.
**GERİ AL** 🔴 **Kapı testi geri alınmaz — `xfail` işaretlenir ve gerekçesi `MIMARI.md`'ye
yazılır.** Sessizce silmek yasak (ADR-0019: kanıt silinmez). Bir kapının kırmızısı bir
**bilgi**dir; kaldırıldığında o bilgi de kaybolur.

### 0.15 · ⭐ CI kapıları — **FAZ 4.1'den BURAYA taşındı**  [bayraksız: kapı] *(D1)*
**NEDEN** 🔴 **Sıralama hatası bendeydi.** `.github/workflows/backend-ci.yml:56` tek satır
`pytest -q`; dört ölçüm kapısı CI dışında. **Ama koşucu ZATEN YAZILMIŞ:** `backend/lab/kapi.py`
`--tam` (`:154`) dördünü sırayla koşuyor (~15 dk) ve **hiçbir workflow onu çağırmıyor**
(doğrulandı: `grep -rn "kapi.py" .github/workflows/` → **boş**).
**Çelişki:** FAZ 2 bu belgenin **kendi ifadesiyle** *"en yüksek etki alanlı faz"* ve
`elektrik` deneyi tam orada **%64→%56** düşürmüştü. **Regresyon ağını en riskli
ameliyattan SONRA kurmuşum** — doktrin (*"düzelt → kapıya çevir"*) burada tersine işliyordu.
**NE** backend: `.github/workflows/nightly.yml` → `lab/kapi.py --tam` │ sözleşme: — │
frontend: — (`api-only`, gerekçe: **CI altyapısı**)
**NASIL** **Yeni kod YOK.** Koşucu var, eşikler **EK D'de zaten yazılı**.
**KAPI** Gecelik koşum; erişim **−1 puan** ya da doğru-cube **−0,5 puan** gerilerse **kırmızı**.
**SONUÇ** FAZ 2'nin semantik ameliyatı **kurulu bir ağın üstünde** yapılır.
**GERİ AL** Workflow dosyası — geri alma = `nightly.yml`'i devre dışı bırakmak (kod
değişikliği yok). ⚠ **Ama bu bir yetenek kaybıdır, davranış değişikliği değil:** kapı
kapanınca FAZ 2'nin semantik ameliyatı **ağsız** kalır. Devre dışı bırakılırsa gerekçe
`MIMARI.md`'ye yazılır.

### 0.16 · ⭐ Ölçüm bütçesi + koşum hijyeni  [bayraksız: altyapı] *(D2)*
**NEDEN** 🔴 **Tamamen kaçırdığım yapısal kırılganlık.** Geliştiricinin kendi commit'i
(`50402d3`): *"gemini-flash-lite (**2×429**) … nemotron-ultra ⊘ **54×429 — ücretsiz katman
doydu**"* ve *"ölçümün gerçek gürültü kaynağı **benimdi**: üç konteyner aynı anda API'yi
dövüyordu"*. **151 maddelik bir planın her *"önce ölç"* kapısı ücretsiz API kotasına
bağlı** — nitekim deneyimin kalbi (`t2_anlatici`) **tam bu yüzden** hâlâ ⊘.
**NE** backend: ayrılmış **ücretli** ölçüm anahtarı `DIMA_MEASURE_KEY` (ürün anahtarından
**ayrı** — kota rekabeti olmaz) + `lab/` koşucuları başlarken **kalan kotayı raporlar** │
sözleşme: — │ frontend: — (`api-only`)
**NASIL** Fail-closed deseni **zaten var**: `nl_accuracy.py` (`--live` gerçek sağlayıcı
yoksa **koşmaz**). Aynı desen kotaya uygulanır.

> 🔴 **KISMEN İNDİ — ve inişi bu maddenin gerekçesini SERTLEŞTİRDİ** (`c4b14d1`, sürüm 5'te
> eklendi). `--live` **ÜÇÜNCÜ kez karşılıksız** çıktı: log *"CANLI MOD"* yazarken sağlayıcı
> `RuleBasedSqlGenerator`'dı. **Kök neden ortam değil AYAR ÖNBELLEĞİ:**
> `app.config.get_settings` `@lru_cache`'li ve `import app.main` onu **dolduruyor**
> (ölçüldü: `currsize=1`); araçlar `tests.conftest`'i modül seviyesinde yüklediği için
> önbelleğe `provider="rule"` giriyor ve **sonraki env geri yüklemesi ona hiç ulaşmıyor.**
>
> 🔴 **Ve asıl tehlike:** `nl_accuracy.py` bu fonksiyonun **KENDİ KOPYASINI** taşıyordu →
> **`nl_accuracy --live` de sessizce `rule` ile koşuyordu** — yani commit'in kendi
> ifadesiyle *"**O KOŞUMLARA DAYANARAK BAYRAK KARARI ALINABİLİRDİ**."* Bu, §6.4'ün
> (*"ölçüm aracının kendisi de bir bağımlılıktır"*) **en pahalı örneğidir**: bu belgenin
> **151 maddesinin her *"önce ölç"* kapısı** o araca dayanıyor.
>
> **İnen:** kopya **silindi** (tek sahip) · `get_settings.cache_clear()` · **beyan ölçüme
> çevrildi** — gerçekten canlı bir üretici kurulmuyorsa `--live` **KOŞMAZ** (fail-closed) ve
> rapor başlığı **üreticinin adını taşır**.
> **0.16'da KALAN iş:** ayrılmış **kota** anahtarı (`DIMA_MEASURE_KEY`) + kalan kotanın
> raporlanması + konteyner adlandırma/kapatma hijyeni. *Yani bu madde küçüldü, ama
> **gerekçesi büyüdü**: aynı sınıf üç kez tekrarladı.*
**KAPI** Kota < eşik → **koşmaz** (sessizce `rule`'a düşmez). Ve commit'in kendi bulduğu
kural teste bağlanır: *"ölçüm konteynerleri **adlandırılır** ve tur sonunda **açıkça
kapatılır** — `--rm` istemci ölünce yetmiyor."*
**SONUÇ** Ölçüm disiplini **karar verebilir** hâle gelir; `t2_anlatici` ve
`agent_plan_secimi` ölçülebilir.
> 🔴 **KAPSAM NOTU (sohbet raporu B9 — çerçeve düzeltmesi, ölçümle doğrulandı):**
> *"Kota çözülünce `t2_anlatici` deneyimi düzeltir"* çıkarımı **yanlış olurdu.** İki kapı
> bunu **yapısal olarak** engelliyor (@`c4b14d1`):
> `answer.py` `if resp.interpretation is not None or (resp.result is None and resp.kpi is
> None): return` · `if not yorum or yorum.get("narration"): return`.
> Yani bayrak **yalnız zaten cevap verilmiş %69,8'e** dokunabiliyor; şikâyetin kaynağı olan
> **%25,9 netleştirmeye ve tüm retlere ULAŞAMIYOR.**
> **Bu maddenin gerekçesi (kota) doğru, ama vaadi daraltıldı:** 0.16 `t2_anlatici`'yi
> **ölçülebilir** yapar — *"deneyimi çözer"* demez. Tam tarifi **§F.2**'de.
**GERİ AL** `DIMA_MEASURE_KEY` tanımsızsa araçlar **bugünkü davranışa** döner —
**ama `--live` fail-closed olduğu için KOŞMAZ** (`c4b14d1` bunu zaten kilitledi). Yani geri
alma *"sessizce `rule` ile ölç"* değil, *"ölçme"*dir. **Kasıtlı:** ölçmemek, yanlış ölçmekten
iyidir — üç kez tekrarlayan sınıfın dersi budur.

### 0.17 · ⭐ Yol başına gecikme bütçesi  [bayraksız: ölçüm] *(D3)*
**NEDEN** EK D'de **60+ eşik** var, **tek gecikme eşiği yok** — oysa kapalı **dört LLM
bayrağının** `features.yml`'deki gerekçesi üç kez aynı cümle: *"sıcak yola LLM çağrısı
ekliyor"*, yani **gecikme**. MIMARI §2.2'de ölçüm **var**: Discovery **12.567 ms** ↔ cube
**145-434 ms** (**30-85×**), ve `consistency_k=3` → bir Intent turu **üç** çağrı.
**30-85× fark ölçülmüş, bütçeye çevrilmemiş.**
> ⚠ **Ve dış kanıt beklentiyi TERSİNE ÇEVİRİYOR** (240 katılımcı, TTFT 2s/9s/20s):
> **2 saniyede gelen cevap, 9 saniyede gelenden DAHA AZ** düşünülmüş ve faydalı bulundu;
> **9s en faydalı** koşuldu. *"Streaming algılanan kaliteyi artırır"* iddiasının
> **hakemli çalışması yok**. → **`t2_anlatici`'yi kapalı tutan asıl soru gecikme değil,
> KAZANÇ olmalı.**
**NE** backend: yol başına **p50/p95** yayımlanır (`cube · cube+llm · intent · discovery ·
agent`) │ sözleşme: — │ frontend: `ui_gelisim_paneli`'nin bir satırı (7.7)
**NASIL** **Yeni enstrümantasyon YOK** — `duration_ms` **zaten makbuzda**.
**KAPI** `tests/test_gecikme_butcesi.py` — ilan edilen bütçe (öneri, ölçümle düzeltilir):
`cube` p95 **<1,5 sn** · `intent` p95 **<6 sn** · `discovery` p95 **<20 sn**. Aşımda kırmızı.
🔴 **Ve bir KURAL:** bir bayrak *"gecikme"* gerekçesiyle `off` kalacaksa **gerekçe sayı
taşır**. Sayısız *"sıcak yola LLM ekliyor"* artık geçerli bir gerekçe değildir.
**SONUÇ** Dört kapalı LLM bayrağının gerekçesi (*"sıcak yola LLM çağrısı ekliyor"*) bir
**beyan** olmaktan çıkıp **sayıya** bağlanır; §F.2'nin A/B'si ölçülebilir bir eşik bulur.
**GERİ AL** Ölçüm ve eşik yayımı — davranış değiştirmez, dolayısıyla geri alma **gerekmez**.
Eşik **yanlış** çıkarsa düşürülür ve düşürme gerekçesiyle kayda geçer (eşiği silmek yasak).

### 0.18 · ⭐ **Metrik kaydı = HAKEM** — FAZ 2.2'den BURAYA taşındı  [bayrak: `metrik_kaydi`] *(D4)*
**NEDEN** 🔴 **Bu belgedeki tek en büyük ölçülmüş kazanç, 40 madde geride duruyordu.**
`CLARIFY:konu` %11,5 + yanlış-cube %6,8 ≈ **turların ~%18'i**, ve ikisinin de **kanıtlanmış
baskın kökü aynı**: bir iş terimi **iki cube tarafından sahiplenilmiş, hakem yok**.
Taze korpus raporu birebir gösteriyor: boyahane yanlış-cube listesinin **ilk 10'unun 10'u**
`elektrik`; atiksan'ın (**%98, en iyi şirket**) **ilk 9'unun 9'u** `satış`.
🔴 **Ve bağımlılık iddiam çürüktü — kendi metnimle:** 0.18'in NASIL'ı *"`mdl_writer`
**katalogdan** taslak üretir … `sahiplenilen_terimler` **boş** başlar → **boş kayıt bugünkü
davranışı değiştirmez**"* diyor. Yani 2.2 **bugünkü kataloğu** okuyor; 2.1'in çekirdek
katmanına ihtiyacı **yok**. İkisi **anlatıyla** bağlıydı, **kodla** değil.
**NE** backend: `MetricDefinition` + **`sahiplenilen_terimler`** + `_match_cube`'un
(`cube_router.py:784`) **ilk satırı** + **çift-sahiplik `compose()` reddi** │ sözleşme:
`GET /metrics` │ frontend: — *(sahiplik ekranı **2.2b'de** kalır)*
**NASIL** `MetricDefinition` **yeni tablo**, ama `_match_cube`'a eklenen **tek bir ön
bakış**: kayıt boşsa davranış **birebir bugünkü** — yani madde **kendi kendine güvenli**.
Mevcut 40+ cube için taslak `mdl_writer`'ın katalog okumasından üretilir
(`olusturulma_yontemi="otomatik_taslak"`, `sahiplenilen_terimler` **boş**); doldurma işi
**3.1'in sahiplik turudur**. İkinci bir eşleştirici **yazılmaz** — kayıt `_match_cube`'un
**ilk satırı** olur, paralel bir yol değil.
**KAPI** `tests/test_metrik_kaydi.py`: `elektrik` → **`enerji_makine`** · `satış` (atiksan) →
**`karlilik`** · çift-sahiplik → **compose reddi**.
**SONUÇ** §C'nin **2. ve 3. ölçütü v1'in BAŞINDA** ölçülebilir olur; sonraki ~100 madde bu
tabanın üstüne oturur.
**GERİ AL** `metrik_kaydi=off` → `_match_cube` kayda bakmaz, bugünkü davranış birebir.

### 0.19 · ⭐ Semantik-vaka paydası  [bayraksız: ölçüm dürüstlüğü] *(D6)*
**NEDEN** 🔴 `lab/nl_corpus.py:130-134` **üçlü iç içe döngü**: `ölçü × PERIODS(11) × boyut`.
Korpus bir **KARTEZYEN ÜRÜN** — ve **iki yönde** çarpıtıyor:
* **Yukarı:** `elektrik`'in **TEK** sahiplik hatası, 11 dönem × boyut = **10+ ayrı
  başarısızlık** olarak sayılıyor. Yanlış-cube %6,8'in içi **birkaç terimin çarpımı**.
* **Aşağı:** *"müdüre 3 cümle yaz"* korpusta **sıfır kez** görünüyor — üreteç yalnız
  **kataloğun bildiği** ifadeleri kuruyor. **5.2'nin bulduğu kusur sınıfı korpusta yapısal
  olarak GÖRÜNMEZ.**
⚠ Bu, deponun iki kez yakaladığı hatanın **korpus ölçeğindeki hâli** (`50402d3`:
*"**YANLIŞ NÜFUS ölçülmüştü**"*).
**NE** backend: `nl_corpus` her metriği **İKİ PAYDAYLA** raporlar — **ham tur** (bugünkü) ve
**semantik vaka** = `(cube, ölçü, niyet)`; dönem/boyut çarpımı **tek vakaya çöker** │
frontend: — (`api-only`)
**NASIL** **Yeni koşucu yazılmaz** — `nl_corpus` raporuna **ikinci bir payda kolonu** eklenir
(`ölçü × boyut` tekil kombinasyonu). Ham tur paydası **korunur**, çünkü geçmiş tabanlar ona
bağlı (KURAL A: kök dokunulmaz).
**KAPI** §C'nin 1. ve 2. ölçütü **semantik vaka** paydasına bağlanır; 🔴 **iki payda TERS
YÖNE giderse KIRMIZI** — *"birkaç terimi düzelttim, sayı uçtu"* yanılsamasının kapanı.
**SONUÇ** §C/1-2'nin yüzdeleri **kartezyen şişmeden arınır**; *"11 dönem varyantı tek bir
semantik vakayı 11 kez sayıyordu"* etkisi ölçülür ve **iki payda birlikte** raporlanır.
**GERİ AL** Rapor kolonu — davranış değiştirmez. 🔴 **Ama taban kırılır:** iki payda ters
yönde hareket ederse (biri artar biri azalır) bu bir **kırmızıdır**, bir yorum farkı değil.

### 0.20 · Bayrak profilleri  [bayraksız: kapı] *(D12a)*
**NEDEN** EK E'de **~70 bayrak**; §C/10 hedefi *"ölü bayrak 0"*. Her maddenin `GERİ AL`'ı
**tek tek** test ediliyor; **kombinasyonlar hiç test edilmiyor**.
**NE** Adlandırılmış profiller: **`taban`** (hepsi `off`) · **`v1-varsayilan`** ·
**`v1-tam`**; CI **profillere karşı** koşar.
**KAPI** 🔴 **Yaşam döngüsü:** `v1-varsayilan`'da **iki sürüm** açık kalan bayrak
**SİLİNİR** — yoksa §C/10 (*"ölü bayrak 0"*) sayı büyüdükçe **matematiksel olarak**
tutturulamaz.

### 0.21 · Modül büyüme kapısı  [bayraksız: kapı] *(D12b)*
**NEDEN** 🔴 **`ask()` TEK FONKSİYON, ~1.930 satır, 20 iç closure** (`ask.py:1383→3309`).
FAZ 0/2/5/6'nın neredeyse her maddesi oraya dokunuyor; depo **paylaşılan bir dizinde** —
bu fonksiyon aynı zamanda bir **çakışma jeneratörü**. Ve **K3'ün kusuru bu boyuttan
doğuyor**: 1.930 satırlık bir gövdede bir çağrının **yanlış `if`in içinde** olduğu görünmüyor.
**NE** `tests/test_modul_buyumesin.py` — `ask.py` ve `cube_router.py` **bugünkü satır
sayısını aşamaz**; yeni davranış **modül çıkarmak zorunda**.
⚠ **Bilinçle *"şimdi refactor et"* DENMİYOR** — büyük refactor'ün kazancı **ölçülmedi**
(§5 disiplini). Kapı refactor'ü **zorlamadan** borcun büyümesini durdurur; maliyeti **bir
test dosyası**.
**KAPI** `tests/test_modul_buyume.py` (yeni): `ask()`'in **satır sayısı** ve
**closure sayısı** bugünkü ölçümden (**~1.930 satır / 20 closure** @`c4b14d1`) **artmaz**;
artıyorsa PR **kırmızı** ve gerekçe **maddede** yazılır. 🔴 **Kapı bir TAVAN, bir hedef
değil** — küçültme işi ayrı bir maddedir; bu kapı yalnız **büyümeyi durdurur**.
*(Rapor bu maddeyi "kapı maddesi ama KAPI'sı yok" diye yakaladı — haklıydı.)*

### 0.22 · 🔴 **BLOKLAYICI HATA — `migration_trace` `UnboundLocalError`**  [bayraksız: hata]
**NEDEN** **Doğrulandı, satır satır:** `migration_trace: list[str] = []` **`ask.py:2878`,
girinti 8** — yani `if structural_followup:` (**`:2862`, girinti 4**) bloğunun **İÇİNDE**.
Ama `if "agent_plan_secimi" in resolve_for(settings, principal):` **`:3177`, girinti 4** —
bloğun **DIŞINDA** — ve `:3179` `migration_trace`'i `_capraz_alan_pilotu`'ya **geçiyor**.
→ **`agent_plan_secimi` = `on` VE `structural_followup = False` → `UnboundLocalError`.**
Bugün dormant çünkü bayrak `off`. Yani *"kota serbest kalınca ölçeriz"* **iyimser: önce bir
hata var.**
**NE** backend: `migration_trace` **fonksiyon gövdesinin başında** (`if`ten önce) tanımlanır
│ sözleşme: — │ frontend: — (`api-only`)
**KAPI** `tests/test_orkestrator.py::test_agent_plan_secimi_yapisal_olmayan_turda_cokmez` —
bayrak `on` + `structural_followup=False` ile `/ask` **200 döner**.
**SONUÇ** Faz C'nin kalan iki bayrağı (`agent_plan_secimi`, `t2_anlatici`) **ölçülebilir**
hâle gelir. ⚠ **0.16 ile birlikte, Faz C'nin kapanmasının iki ön koşulu bunlar.**

### 0.23 · ⭐ **Ölü render dalı — ödenmiş üç özellik ekranda yok**  [bayraksız: yetim] *(sohbet raporu M1/B1)*
**NEDEN** `ReportPanel.tsx:185@71b542e` kapısı `it.result || it.kpi`. Ama `ask.py:1750`'nin
*"cevap üstünde konuş"* dalı **`result` DÖNDÜRMEZ** — `contribution` + `prescription` +
`next_steps` **dolu**. Kodun **kendi yorumu** (`ask.py:1745`): *"Bulgular **CEVABIN
GÖVDESİDİR** — `next_steps` DEĞİL … `contribution` alanı zengin gövdeyi taşır … UI'da
farklı görünmelidir."* Yani backend yazarı gövdeyi **bilerek** `contribution`'a koymuş ve
UI'ın render etmesini beklemiş.
**Render edici ZATEN YAZILMIŞ ve DOĞRU:** `ReportCard.tsx:833` →
`item.cube_query && (item.result || item.contribution)`. **Sırası hiç gelmiyor.**
🔴 **Aynı kapı `ReportPanel.tsx:122`'de TEKRAR geçiyor**
(`thread.items.forEach((it, i) => { if (it.result || it.kpi) lastReportableIdx = i; })`) →
`lastReportableIdx`/`viewHint` de **aynı körlüğü miras alıyor**. Kapı **iki yerde** onarılır.
Aynı dal `_intent_uyusmazlik_chipi` (`ask.py:786`, dalı `:829`) netleştirmesini de
öldürüyor: `next_steps` render'ı **YALNIZ** `ReportCard.tsx:878`'de var, **not dalında
YOK** (doğrulandı: `grep -n "next_steps" ReportPanel.tsx` → **0 isabet**) → **sistem
*"Hangi ölçüyü istiyorsun?"* diye soruyor, altında tıklanacak hiçbir şey yok.**
**Sonuç:** kullanıcı *"bu neden böyle?"* yazıyor → katkı ayrıştırması (Δ tutarlar, % paylar)
ve reçete **çöpe gidiyor**; geriye sarı bir not kalıyor. **Faz D2/G1/G3'te ödenmiş üç
özellik ekranda yok.**
```bash
grep -n "it.result || it.kpi" dima-frontend-demo-master/src/components/ReportPanel.tsx
grep -n "item.result || item.contribution" dima-frontend-demo-master/src/components/ReportCard.tsx
```
**NE** backend: — (**yalnız KAPI testi genişler** — o bir backend testidir, çerçeve
dürüstleştirildi) │ sözleşme: — │ frontend: `ReportPanel`'in **İKİ ayrık render dalı TEK
yola iner**; kapı `it.result || it.kpi || it.contribution || it.prescription`; **saf-not
dalına `it.next_steps` eklenir** (`ReportCard.tsx:878`'in **AYNI** deseni, `onCubeEdit` →
`/cube`, **0 LLM**); `:122` aynı kapıyı kullanır
**NASIL** `ReportCard`'ın null-güvenliği **ZATEN var** (`:491,703,833,945` hepsi koşullu).
**Yeni bileşen yok, yeni prop yok** — `onCubeEdit` `ReportPanel`'e zaten geliyor.
🔴 **`ReportCard.tsx:878`'in `!item.contribution` koşuluna DOKUNULMAZ** — konuşma cevabında
`next_steps`'i göstermek *"aynı listeyi **İKİ KEZ**, üstelik ikincisini **YANLIŞ BAŞLIKLA**
(«sonraki adım») sunardı"* (kodun kendi gerekçesi). **Eklenen render YALNIZ not dalınadır.**
**KAPI** `tests/test_cevap_alani_yetim_degil.py` genişletilir — **K2'nin (c) boyutu**:
alanın FE kaynağında **geçmesi yetmez**, `result=None` iken **ULAŞILABİLİR** olmalı. Bugün
`contribution` `ReportCard.tsx`'te geçtiği için kapı **yanlış-pozitif yeşil**.
\+ `tsc --noEmit` **0** · `eslint .` **0**
**SONUÇ** Faz D2/G1/G3'te ödenmiş üç özellik **görünür** olur. **Yeni yetenek SIFIR** —
çalışan, testli, makbuzlu bir motor *görünmezden görünüre* geçer.
> ⚠ **DOĞRULAMA TURU İÇİN — bu uyarı okunmazsa madde «başarısız» sanılır:** konuşma
> cevabında gezinme **`ContributionLayer`'ın TIKLANABİLİR SEGMENTLERİNDEN** gelir
> (`onClick={() => onCubeEdit?.({cq, label})}`). `next_steps` bloğu `!item.contribution`
> ile **BİLEREK gizli kalır** — bu bir eksik **DEĞİL**, tasarımdır. `next_steps` kazancı
> **NETLEŞTİRME** cevabında görünür (`ask.py:829` dalı). ***"Chip'ler gelmedi" diye GERİ
> ALMAYIN.***

**GERİ AL** `git revert`. Bugünkü davranış zaten *"hiç görünmüyor"* → **geri alma riski
SIFIR**.

> **Sıra notu:** bu, **her iki dış raporun tamamındaki en yüksek etki/maliyet oranıdır** ve
> **DÜZELTMESİ** hiçbir şeye bağımlı değildir — bekletmek için sebep yok. FAZ 0 içinde
> **ilk** iner (koşum sırasının 1. adımı, `0.22` · `0.2` ile birlikte).
>
> ⚠ **DÜZELTME BAĞIMSIZ, KAPISI DEĞİL (sürüm 8 — `KAT-3` denetimi).** Sürüm 7 burada
> *"hiçbir şeye bağımlı değildir"* diyordu, ama bu maddenin **KAPI**'sı `K2`'nin **(c)
> boyutudur** ve o boyut **`0.14`'te doğar**. İkisi aynı anda doğru olamaz:
>
> * **Düzeltme** ilk gün iner (iki kapı satırı + not dalına `next_steps`) ✅
> * **Kapısı** `0.14` indiğinde **geriye dönük** kapanır — ve *o güne kadar madde
>   **"bitti" sayılmaz***, çünkü bu belgenin doktrini *"düzelt → **kapıya çevir**"*tir.
>
> 🔴 **Sebebi ölçülmüş:** bu kusuru bugün **iki bağımsız kapı da yeşil raporluyor**
> (`test_cevap_alani_yetim_degil` **ve** `lab/deneyim.py::S2`) — ikisi de *"alan var mı"*
> soruyor, *"ulaşılabilir mi"* değil. Kapısız inen bir düzeltme, **aynı körlüğün üçüncü
> kopyasını** üretirdi.
>
> 💡 **Aynı ekran, aynı dokunuş — birlikte yapılabilir:** kalibre edilmemiş güven ibaresi
> (`ChatPanel.tsx:16-27` → *"Yüksek güven (100%)"*) **tam bu kartın üstündeki satırdadır**.
> Kaldırılması **7.8/K2**'nin işidir ve **tek dokunuş**tur; 0.23 zaten o dosyaların
> yanındayken yapılırsa ikinci bir doğrulama turu gerekmez. *(Sıra zorunluluğu **değil**,
> maliyet notudur — 7.8/K2 kendi kapısını kendisi taşır.)*

---

**FAZ 0 KAPISI:** **25/25** kapalı *(0.1–0.22 = 22 numara, + `0.5b` · `0.10b` · `0.23`)*,
her biri bir teste bağlı, K1-K5 **kör noktasız**.
⚠ **0.22 bir plan maddesi değil, BUGÜN DURAN BİR HATADIR** — Faz C ölçülmeden önce iner.
⚠ **0.23 de bir plan maddesi değil, BUGÜN EKRANDA OLMAYAN ÜÇ ÖZELLİKTİR** — sıfır bağımlılık.

> 🔴 **VE FAZ 0 ÖNCELİĞİNDE BİR MADDE DAHA VAR — ama evi §G:** **`AJ0` (kısa devre yasağı)**.
> Ucuzdur, bir **güvenlik ağıdır**, MIMARI §5'e **18. yasak** olarak girer, ve bu belgede
> **zaten ölçülmüş beş kusurun** (0.23 · 5.0/K3 · §F.2 · §F.3/7 + kullanıcının
> *«degisti→egitim»* vakası) **ortak sınıfını** kapatır. §G'de duruyor çünkü **§G/AJ2'nin
> ölçüm aletini kuran madde odur** — ama **sırası FAZ 0 ile birliktedir**, §G'nin gerisini
> beklemez.

---

## FAZ 1 · GÜVENCE — *"temel neyse ajan onu çarpar"*

**NEDEN** Bölüm II'nin analist/karar motorları ve FAZ 6'nın yazma yüzeyi **otonomi**
açıyor. Ölçüldü: motor-RLS **hiç alınmamış**, Discovery ham-SQL baypası **açık**, **15/15
araç tek izin**. Bu sırayla gitmemek §11'in kendi tezini (*"agentic katman temelin ne ise
onu **ÇARPAR**"*) ters yöne çalıştırır. [KANIT §7.4]

> **Absorbe edilen:** Plan 3 **Bölüm 12'nin tamamı** + §5.2 + §13.2 + Plan 2 **§11'in
> tamamı** (Plan 2'de **hiçbir faza atanmamıştı** — [KANIT §17.1/1]).

### 1.1 · ⭐ Motor-seviyesi RLS  [bayrak: `motor_rls` = `off|shadow|on`]
**NEDEN** `grep -c rowLevelAccessControl backend/app/` → **0**. `always_filter` bir
**uygulama-katmanı yamasıdır**; Discovery ham SQL'i onu **baypas ediyor** (MIMARI §6.3 ❌).
Sektör bunu **"compile-time governance"** diye adlandırıyor ve hata modunu bizimkiyle aynı
tarif ediyor: *"doğru bir sorgu ile başka bir tenant'ın verisini açan sorgu modele **AYNI
görünür**"*, *"post-hoc filtreleme güvenilmezdir: SQL'de veriye giden çok fazla yol var"*
([KANIT §2.2]) — MIMARI §5'in `guard_sql` eleştirisinin dışarıdan doğrulanması.
**NE**
* backend: `rowLevelAccessControls` + `SessionProperty` + `dry_plan(properties=)`;
  `WrenService._session_properties(principal)` → her sorguya enjekte
* sözleşme: `Principal` → session property eşlemesi (`tenant_slug`, `role_key`, `user_id`)
* frontend: — (**`api-only`**, gerekçe: **altyapı**, `API_ONLY`'ye yazılır)
**NASIL** `strict_sql_policy`'nin **aynı disiplini**: `off|shadow|on`, varsayılan `shadow`;
gölgede **her sorgu iki kez planlanır** (RLS'li/RLS'siz) ve satır sayısı farkı
`logs/rls_shadow.jsonl`'a yazılır. `app/pii.py` **son savunma olarak KALIR**.
**KAPI** `tests/test_motor_rls.py`: (a) **çapraz-tenant** — tenant A token'ıyla tenant B
verisi **0 satır**; (b) **Discovery yolu** — ham SQL RLS'i **atlayamıyor**; (c) gölge modda
**7 gün · `rls_shadow.jsonl` 0 satır** → `on`.
**SONUÇ** Discovery ham-SQL baypası **kalıcı** kapanır; `always_filter` yaması **motorun
yerini almaz, motor devralır**.
**GERİ AL** `motor_rls=off` → bugünkü davranış birebir; `tests/test_motor_rls.py::test_off_birebir`.

### 1.1b · ⭐ **Arka plan işi kimliksiz koşmaz** *(Plan 3 B10 — kaçmıştı)*  [bayraksız: değişmez]
**NEDEN** 1.1 yalnız **istek yolunu** kapatıyor. **Zamanlayıcı yolu açık**: `schedules.py`
(763 satır), digest, brifing, bakım ajanı — hepsi `principal`'sız koşarsa RLS devreye
girmez. Plan 3 bunu *"B9'un zamanlayıcı tarafındaki karşılığı"* diye adlandırmış.
**NE** backend: her zamanlanmış/arka plan koşumu bir **`principal` + tenant** ile koşar;
`authorize()` **ve** session-property enjeksiyonu orada da uygulanır │ sözleşme: `Schedule`
kaydına `run_as_user_id` │ frontend: zamanlama kartında *"kimin adına koşuyor"*
**NASIL** `authorize()` ve session-property enjeksiyonu **zaten yazılı** (1.1); burada
yapılan onları **ikinci çağırana** bağlamak. Yeni yetki mekanizması **yok** — `run_as_user_id`
var olan `principal` çözümüne girer.
**KAPI** `tests/test_arkaplan_kimlik.py`: `principal=None` ile `run_schedule` çağrısı
**reddedilir** (fail-closed).
**SONUÇ** RLS'in **iki yolu da** kapanır; *"istek yolu güvenli, zamanlayıcı yolu açık"*
asimetrisi biter. §C/4'ün *"sapma 0"* ölçümü **arka plan koşumlarını da** kapsar.
**GERİ AL** 🔴 **Geri alınmaz — bu bir DEĞİŞMEZ onarımıdır** (§A.2/Kademe 1'in bayraksız
sınıfı). Fail-closed: `principal=None` **reddedilir**. Geri alma yolu açmak, kapatılan
deliği yeniden açmak olurdu.

### 1.2 · `columnLevelAccessControl` + **redactor genişlemesi**  [bayrak: `motor_cls`]
**NE**
* (a) backend: `columnLevelAccessControl` — hassas kolon **plandan düşer**.
  🔴 **DENETİM DÜZELTMESİ (D13a):** sürüm 2 *"`sensitivity: person|special|normal` beyanı
  **zaten var**, yeni beyan yazılmaz"* diyordu — **eksikti**. Motorun kaynağı
  (`WrenAI-main/core/wren-core-base/manifest-macro/src/lib.rs`) CLAC'ı **etiket değil EŞİK
  tabanlı** tanımlıyor: `{required_properties, operator: Equals|NotEquals|GreaterThan|…,
  threshold}` — ve manifest'te **ÇOĞUL DEĞİL** (`column_level_access_control: Option<...>`,
  **kolon başına TEK**). → **`sensitivity` → `(SessionProperty, operator, threshold)`
  eşlemesi BEYAN EDİLİR ve bu YENİ İŞTİR**; `tests/test_gizlilik_muhru.py`'de kilitlenir.
* (b) `pii.py` **son savunma** olarak kalır
* (c) 🔴 **Redactor grafik etiketlerine ve dışa aktarımlara genişletilir** *(Plan 2 §11.7 —
  kaçmıştı)*: bugün yalnız metin/tablo maskeleniyor; §D.2/2'nin *"tarayıcı zaten maskeli
  veriyi dışa aktarır"* hükmü **grafik etiketleri maskelenmezse doğru değil**
**KAPI** `tests/test_gizlilik_muhru.py` genişletilir: `person` kolonu talep eden sorgu →
kolon **çıktıya hiç gelmez**; PNG/SVG/CSV dışa aktarımında **etiketler maskeli**.
**GERİ AL** `motor_cls=off` → hassas kolon plandan **düşmez**, bugünkü davranış. 🔴 **Ama
`app/pii.py` SON SAVUNMA olarak her hâlükârda kalır** — CLS onun yerine geçmez, **önüne**
geçer. Geri alma maskelemeyi kapatmaz.

### 1.2b · **`llm_guard.safe_call()`** *(Plan 3 §5.2 — kaçmıştı)*  [bayraksız: tekilleştirme]
**NEDEN** *"Ham veri LLM'e gitmez"* kuralı bugün **üç ayrı yerde** (`sensitivity.py`,
`pii.py`, doğrudan `llm.py` çağrı siteleri). §D.2/1'in hükmü bu kurala dayanıyor ama
**tekilleştirme hiçbir maddede yoktu**.
**NE** backend: `app/llm_guard.py::safe_call(payload, principal)` — **tek sarmalayıcı**;
payload'ı **gönderim öncesi** tarar, ihlalde çağrıyı **engeller** + `AuditLog`'a yazar
**KAPI** `tests/test_llm_veri_sizintisi.py` genişletilir: `llm.py`'de `safe_call` dışından
sağlayıcı çağrısı **yok** (kaynak taraması).

### 1.3 · ⭐ Yetki granülerliği  [bayraksız: değişmez onarımı]
**NEDEN** 15 aracın **hepsi** `izin="query:run"` → `izinli_araclar()` ya **15'ini** döner ya
**hiçbirini**. §11.2'nin *"ajan kullanıcının yetkisini AŞAMAZ"* değişmezi **efektif olarak
uygulanmıyor**. [KANIT §0.1-A3]
**NE** backend: gerçek aksiyonlar (`query:run` · `drill:run` · `contribution:run` ·
`llm:invoke` · **`metric:certify`** · `decision:write` …), `authorize._ACTION_MIN_RANK`'a
eklenir │ sözleşme: `/auth/me` `permissions` (mevcut) │ frontend: `usePermission` (mevcut)
**NASIL** Matris **zaten var** (16 aksiyon); araç kaydının `izin` alanı **çeşitlendirilir**.
**KAPI** `tests/test_arac_kaydi.py::test_izin_MATRISTE_var` — her araç **ayrı aksiyon**;
**viewer rolü `contribution.report` (maliyet `pahali`) çağıramıyor**.
**SONUÇ** Ajan yetkisi **gerçekten** kullanıcınınkiyle sınırlı.

> ⚠ **GEREKÇE DEĞİŞTİ (`c527613` sonrası, §A.4).** Bu madde sürüm 2'de *"6.1 ve 6.2'nin ön
> koşulu"* diyordu. **Artık değil:** H, yazma aracını kayda **hiç almayarak** (`app/eylem.py`
> deseni) o bağımlılığı **yapısal olarak kaldırdı**.
> **Kalan gerekçe daha dar ama hâlâ geçerli:** bugün **viewer rolündeki** bir kullanıcının
> ajanı `contribution.report`'u (maliyet sınıfı **`pahali`**, 6 boyut tarama) çağırabiliyor —
> okuma tarafında da bir maliyet/yetki ayrımı yok. **Öncelik P0 → P1'e düşer.**
**GERİ AL** 🔴 **Geri alınmaz — bu bir DEĞİŞMEZ ONARIMIDIR.** İzinleri tek
`query:run`'a geri döndürmek §11.2'nin *"ajan kullanıcının yetkisini AŞAMAZ"* hükmünü
yeniden **beyan** seviyesine düşürürdü. ⚠ **Geçiş güvenliği:** yeni aksiyonlar eklenirken
`query:run` bir **süre daha** kabul edilir (deprecation), ama `test_izin_MATRISTE_var`
**her aracın kendi aksiyonunu** ister — yani geçiş **ölçülür**, süresiz kalmaz.

### 1.4 · Süreç-arası kilit  [bayraksız: altyapı]
**NEDEN** MIMARI §6.3 ⚠: kilit **süreç-içidir** (`threading`); iki süreç aynı çıktı dizinine
compose ederse yarış geri döner (2026-08-02'de **yeniden üretilerek** teşhis edildi).
**NE** backend: `threading.Lock` → **`fcntl.flock`**; kilit dosyası
`demo/wren-projects/<slug>/.compose.lock`; çakışmada **bloklar** (timeout **60 sn**, aşımda
`RuntimeError` — sessiz geçiş yok) │ sözleşme: — │ frontend: — (`api-only`)
**KAPI** `tests/test_compose_kilidi.py`: iki süreç paralel compose → MDL **bozulmuyor**,
biri bekliyor.
**SONUÇ** **gunicorn/çok-worker dağıtımının ön koşulu** kapanır (→ II-G.7).

### 1.5 · Metrik sertifikasyonu  *(Plan 3 §12.1)*  [bayrak: `metrik_sertifikasi`]
**NE** backend: `app/certification.py` + **`MetrikSertifikasi`** (`metric_ref` · `seviye`
∈ `önerilen|sertifikalı|master_veri` · **`sertifikalayan_id`** · **`sertifika_notu`** ·
`definition_hash` · **`lineage_set_hash`** · `son_gecerlilik` (TTL **90 gün**) ·
**`otomatik_iptal_nedeni`**) │ sözleşme: `AskResponse.explain.sertifika` │ frontend:
güven rozetinin **kademesi** (yeni panel **değil**)
**KAPI** `tests/test_sertifikasyon.py`: **B8** — `MetricDefinition` **ya da üst-akış kolon
kümesi** değişince sertifika **`yeniden_dogrulama_gerekli`**'ye düşüyor (canlı doğrulanır);
`metric:certify` aksiyonu **admin+** (1.3).
**GERİ AL** `metrik_sertifikasi=off` → rozet gösterilmez, `MetricDefinition` **yazılmaya devam
eder** (veri kaybı yok). ⚠ **Tanım-hash çürümesi kapalıyken de İŞLER** — aksi hâlde bayrak
açıldığında bayat sertifikalar *"geçerli"* görünürdü.

### 1.6 · Column-level lineage  *(§12.2)*  [bayrak: `lineage`]
**NE** backend: **`KolonKokeni`** — OpenLineage'ın **iç temsili benimsenir** (kütüphane
değil); **6 değerli `donusum_tipi`** (`dogrudan|toplam|oran|filtre|birlestirme|turetilmis`)
+ `maskelendi: bool`; **Discovery ham SQL'inde `lineage: "bilinmiyor"`** │ frontend:
**üç LLM'siz şablon cümle** `ContractDetailPanel`'de:
1. *"Bu sayı `<tablo>.<kolon>`'dan geldi."*
2. *"`<boyut>` = `<değer>` filtresiyle daraltıldı."*
3. *"Bir üst-akış tablo `<N>` gün önce değişti."*
**KAPI** `tests/test_lineage.py`: teknik graf **kullanıcıya gösterilmiyor** (KD-13).
**GERİ AL** `lineage=off` → köken zinciri **toplanmaz ve gösterilmez**; makbuz bugünkü hâliyle
kalır. Toplanan geçmiş **silinmez** (ADR-0019).

### 1.7 · ⭐ Tazelik merdiveni  *(§12.3 + Plan 2 §11.9)*  [bayrak: `tazelik`]
**NEDEN** `grep -rl freshness backend/app/` → **0**. `SyncState.last_synced_at`
(`admin_app/routers/clone.py:203`) **yalnız admin klon yolunda**, `/ask`'e **hiç ulaşmıyor**.
Kullanıcı *"8 gündür veri gelmiyor"*u **göremiyor**. [KANIT §19.3-4]
**NE**
* backend: zaman boyutunun `max()` + `SyncState` → cevap yoluna; **iki eşik**:
  **`warn_after` (varsayılan 2× beklenen periyot)** · **`error_after` (varsayılan 5×)**,
  `TenantConfig`'te ayarlanır
* sözleşme: **`AskResponse.freshness: taze | uyarı | hata | bilinmiyor`** + `son_veri_ts`
* frontend: `taze` → işaret yok · `uyarı` → **rakamın altına ince turuncu dalgalı çizgi**
  (rozetten **farklı görsel kanal**, yarışmaz) · `hata`/`bilinmiyor` → **sayı yerine
  açıklama kartı**
**NASIL** dbt `source freshness` kalıbı; `contract_log` zaman/`mdl_version`'ı **zaten
taşıyor**.
🔴 **KAPI (denetim düzeltmesi — sürüm 1 bunun TERSİNİ kilitliyordu):**
**`hata` kademesinde SAYI GÖSTERİLMEZ**; **`bilinmiyor`, `hata` ile AYNI muamele görür**
(**B4: bilinmeyen tazelik = taze DEĞİL**). Bu, Plan 3/Plan 2'nin *"bugünkü davranıştan
**kasıtlı bir sertleşme**"* kararıdır. `tests/test_tazelik.py::test_hata_kademesinde_sayi_yok`.
**KAPI** `tests/test_tazelik.py` (yeni): **(a)** `error_after` aşıldığında yanıt
**sayı taşımaz** (yalnız açıklama) — 🔴 kaynak planların TERSİ bir kural yazmıştım, düzeltildi ·
**(b)** `bilinmiyor` **taze DEĞİLDİR** (B4) ve `taze` gibi işlenmez ·
**(c)** eşikler `TenantConfig`'ten okunur, sabit kodlu değil ·
**(d)** K2: `freshness` ve `son_veri_ts` **frontend'de ULAŞILABİLİR** (yalnız kaynakta
geçmesi yetmez — 0.14/K2(c)).
**SONUÇ** *"Bu sayı neden düşük?"*in **en sık gerçek cevabı** ilk kez görünür olur.
**GERİ AL** `tazelik=off` → alan `None`, bugünkü davranış birebir.

### 1.8 · Audit şeması  *(§12.4)*  [bayraksız: uyum]
**NE** `AuditLog`/`InteractionLog`'a **OTel GenAI semantic conventions** alanları +
**`onceki_kayit_hash`** (SHA-256 zinciri; ilk kayıt `genesis`) + **W3C PROV-O** çerçevesi.
**KAPI** `tests/test_audit_zinciri.py`: zincir kopukluğu **tespit ediliyor**.

### 1.9 · Numeric fidelity genellemesi  *(§12.6)*  [bayraksız: kapı]
> ⚠ Plan 3'ün öncülü **yanlıştı**: `narration_guard.py` **yetim değil**, bağlı
> (`answer.py:350,383`). Genelleştirme işi **geçerli**.

**NE** `izinli_degerler()` yeni türevleri kapsar (MASE · kırılma-noktası % · karar rozeti %);
**modülün gövdesi değişmez**. **Zorlama mekanizması:** `narration_guard.dogrula` **araç
kaydına girer** (`makbuz=None`, **kapıdır**) ve `tests/test_anlati_kapisi.py` her anlatı
üreten yolun ondan geçtiğini **kaynak taramasıyla** doğrular.
**KAPI** `tests/test_numeric_fidelity.py`: her yeni anlatı yüzeyi (MASE ·
kırılma-noktası % · karar rozeti %) **`narration_guard.dogrula`'dan geçer**; guard'a
kayıtsız bir anlatı üreticisi eklenirse **kaynak taraması kırmızı** verir. ⚠ **Ve KD-21
sınırı burada da geçerli:** guard **rakamsız** cümlede yetkisizdir — yeni yüzeyler
**sayı taşıyan** cümleler üretmelidir, yoksa kapı onları **görmez**.

### 1.10 · Eskalasyon matrisi  *(§12.7)*  ·  1.11 · Kademeli düşüş  *(§12.8)*
**NE** `EskalasyonKurali` (`tetikleyici_esik` · `sure_dakika` · `hedef_rol` ·
`otomatik_kilitle`). **Değerlendirici:** mevcut **60 sn scheduler döngüsü** (yeni cron yok).
§12.8: yeni kod **yok** — `FailoverSqlGenerator` sırası zaten üç seviye; her geçiş
`AuditLog`'a *"seviye X'e düşüldü"* + `ConnectionBadge`'e **üç seviyeli gösterge**.
**KAPI** `tests/test_eskalasyon.py`: süre dolunca **bir üst kademeye** yükseliyor.

### 1.12 · AI Act / NIST RMF / ISO 42001  *(§12.9)*  [bayraksız: yasal]
**NEDEN** **AI Act Md.50 `2 Ağustos 2026`'dan yürürlükte** `[DOĞRULANMADI — birincil kaynak
EK F'ye eklenecek]`.

| Yükümlülük | Karşılık |
|---|---|
| Otomatik kayıt **≥6 ay** (Md.12/19) | `AuditLog` append-only + **saklama politikası** `TenantConfig`'te |
| Denetleyici-okunabilir log (Md.13) | **`GET /audit/export`** (admin+, JSON-LD/PROV-O) |
| Çıktı yorumlanabilirliği (Md.13) | `contract_id` → SQL drill (**zaten var**) |
| İnsan müdahale/durdurma (Md.14) | **`DELETE /ask/jobs/{id}`** — çalışan sorgu **iptal edilir** |
| Otomasyon-önyargısı (Md.14) | **skaler `confidence` yok** — zaten uyguluyoruz |
| AI içerik işaretleme (Md.50) | **`AskResponse.ai_generated_prose: bool`** — `answer.seal()` set eder (sayı DEĞİL, **anlatı**) |
| Kanıt sınıfı *(Plan 3 §13.3 — kaçmıştı)* | **`AskResponse.kanit_sinifi: Literal["olculmus","probabilistik"]`**, varsayılan `"olculmus"` — **bugünden** eklenir ki sonradan geriye dönük eklenmesin |

**KAPI** `tests/test_ai_act_uyumu.py`: `ai_generated_prose` ve `kanit_sinifi` **her** yanıtta.

### 1.3b · 🔴 `enforce_query` — **beyan edilmiş ama BOŞ bir güvenlik katmanı**  [bayraksız: değişmez]
**NEDEN** **Doğrulandı:** `control_plane/authorize.py`'de `enforce_query(principal,
referenced_models)` — docstring'i *"**Katman B kancası**: üretilen SQL'in dokunduğu MDL
modelleri, principal'ın `ModelPermission` allowlist'ine karşı doğrulanır"* diyor; **gövdesi
tek satır: `return`**, üstünde `# TODO(faz-2)`. Yani **ADR-0014 Karar 5'in beyan ettiği
katman hiçbir şey yapmıyor** ve bunu **hiçbir plan yazmamış**.
**NE** backend: `ModelPermission` doldurulur; `enforce_query` **dry-plan çıktısı üstünde**
zorlar (LLM prompt'unda **değil**) │ sözleşme: — │ frontend: — (`api-only`)
**NASIL** 1.1'in `SessionProperty` altyapısıyla **aynı turda**; iki katman birbirini
tamamlar (**A**: motor RLS satır düzeyinde · **B**: model allowlist).
**KAPI** `tests/test_enforce_query.py` — allowlist dışı bir modele dokunan SQL **reddedilir**;
🔴 **boş allowlist artık "geçer" DEMEZ** (fail-open → fail-closed).

### 1.3c · `strict_sql_policy` bir **güvenlik sınırı DEĞİLDİR** — yazıya geçer  [bayraksız: kayıt]
**NEDEN** Motorun **kendi kaynağındaki yorum** (`wren/policy.py`): *"kaynak-olmayan
pozisyonlar için bu bir **blocklist**tir, fail-closed bir allowlist değil… burada sayılmamış
bir okuyucu, bir projeksiyon / alt sorgu / iç-argüman pozisyonunda **GEÇER**. Liste bu yüzden
**KONNEKTÖR BAŞINA BAKIMLI TUTULMALIDIR**."*
Bu, MIMARI §5'in kendi teşhisinin (*"savunma **tesadüfi**"*) **motorun kaynağından
doğrulanması**.
**NE** `MIMARI.md`'ye ve bu belgeye tek cümle: 🔴 ***"`strict_sql_policy=on` bir güvenlik
sınırı olarak SATILMAZ/YAZILMAZ; sınır `motor_rls` (1.1) + `enforce_query` (1.3b) +
`denied_functions`'tır."***
**KAPI** `lab/kapi.py`'ye **konnektör başına blocklist tazeliği** kontrolü.

### 1.13 · Düşman denetim panelini yenile  [bayraksız: denetim]
**NEDEN** `lab/panel/index.md:3` **2026-07-24**, **47 açık aksiyon** (madde sayımı birebir);
en az ikisi (U1 scheduler cross-tenant, U2 compose race) o tarihten sonra **kapandı**.
**KAPI** Kapananlar **işaretlenir, silinmez** (MIMARI §10).

---

## FAZ 2 · SEMANTİK ÇEKİRDEK — **en yüksek etki alanlı faz**

**NEDEN** [KANIT §9, §10]:
* Küpler **grain** küpleridir (`oee` = `oee_vardiya`'nın **bir satırı**) — ama **adları
  departman çağrıştırıyor** ve o ad departmanın **tüm sözlüğünü kimliğe yapıştırıyor**.
* **`surdurulebilirlik` ile `parti` AYNI `base_object`** (`partiler`) — iki küp, tek grain.
  `elektrik` felaketinin kökü.
* **`cari`/`ticaret` DÖRT kez** elle yazılmış; **`ticaret` üç ERP'de FARKLI GRAIN**
  (mikro=`stok_hareketleri`, logo/netsis/company=`faturalar`) — aynı ad, aynı sinonim,
  **karşılaştırılamaz sayı**, hiçbir yerde beyan yok. *Semantic drift*, kendi pack'lerimizde.
* **`compose()` dosya düzeyinde eziyor** (`copy2`, `compose.py:165`) → çekirdek katman
  yazılsa **ERP katmanı sessizce silerdi**.
* Sektör kuralı: **grain varlıkla · metrik iş diliyle · mercek departmanla** adlandırılır.

> ⚠ **"Sadeleştirme" DENENDİ, ölçümle REDDEDİLDİ:** `surdurulebilirlik` kimliğinden ham
> kaynak adları çıkarılınca **erişim %64→%56**, `test_eval_gate` **KIRMIZI**, **110
> sessiz-yanlış kapandı ama 388 cevap kayboldu (3,5:1 kötü takas)**. Geri alındı ve
> **testle korunuyor**. Sebep: *"kimliği kaldırmak **sahipliği ÇÖZMEDİ**"*.
> → **Bu faz çıkarma değil, HAKEM EKLEME fazıdır.** [KANIT §8.3, §11.3]

### 2.1 · ⭐ Çekirdek katman + **grain sözleşmesi kapısı**  [bayrak: `cekirdek_katman` = `off|shadow|on`]
**NEDEN** Evrensel kavramlar **DÖRT kez** elle yazılmış (`cari` · `ticaret` × mikro/logo/
netsis/demo-boyahane); `cari` **saf tekrar**, `ticaret` **üç ERP'de FARKLI GRAIN**
(mikro `stok_hareketleri`, logo/netsis `faturalar`) — **aynı ad, aynı sinonim,
karşılaştırılamaz sayı, hiçbir yerde beyan yok.** Bu, Cube'un adlandırdığı *semantic drift*
hata modunun **kendi pack'lerimizin içindeki** hâli. Ve `compose()` katmanları `shutil.copy2`
ile **DOSYA düzeyinde** eziyor → bir çekirdek katman yazılsa bile **ERP katmanı onu sessizce
silerdi**. [KANIT §10.2]
**NE**
* backend: **`packs/cekirdek/`** — evrensel iş varlıkları ve **metrik sözlüğü**
  (`cari` · `satis` · `stok` · `personel` · `defter`): ölçü **adı · sinonim · birim ·
  `additive:` · GRAIN SÖZLEŞMESİ**. **`base_object` YOK** — o ERP katmanının işi.
* backend: **`_merge_cube_metadata`** — `compose()`'un **BEŞİNCİ** üreteci (kodda dört var:
  `_compose_derived_metrics` · `_merge_cube_synonyms` · `_compose_kpis` ·
  `_compose_relationship_dimensions`); dosya-düzeyi ezme yerine **anahtar düzeyinde**
  birleştirme
* backend: **grain sözleşmesi FAIL-CLOSED kapısı** — çekirdek metrik `grain: fatura` beyan
  eder; ERP onu **başka grain'e** bağlarsa `compose()` **reddeder** (**G5** harf-çakışması ve
  **G10** `always_filter` kapılarıyla aynı sınıf)
* sözleşme: — │ frontend: — (**`api-only`**, gerekçe: **derleme katmanı**)

**NASIL — göç reçetesi (MIMARI Faz 2'nin KANITLANMIŞ deseni: üç cube view'dan modele taşındı,
hiçbir sayı değişmedi):**
1. **Kabul ölçütü ÖNCE:** her cube × **her ölçü × her boyut** kombinasyonu, öncesi/sonrası
   **birebir aynı sonuç** (MIMARI Faz 2'de **26/21/73** kombinasyon — hepsi tuttu; **aynı
   harness çağrılır**).
2. **Gölge derleme:** `compose()` iki çıktı üretir, **MDL'ler diff'lenir**
   (`lab/mdl_diff.py`, yeni — karşılaştırma birimi: **cube × ölçü × boyut × ifade**).
3. **Dört şirkette** `nl_corpus --kapi` + `eval` + `validate_project()`.
   *(⚠ `test_member_sweep` **yok** — −1.1/A6; yerine `lab/member_sweep.py` build-time
   `LIMIT 0` taraması **bu fazda yazılır**.)*
4. **SİLME YOK.** ERP pack cube dosyaları **yerinde kalır**; **geri alma = bayrağı kapatmak**.
5. **Sıra:** ⚠ **denetim düzeltmesi** — `cari` *"saf tekrar"* **DEĞİL**: ölçü **adları** aynı
   ama **ifadeler farklı** (`SUM(CASE WHEN cha_tip=0…)` ↔ `SUM(BORC)`), `base_object`
   **4 farklı**, boyut sayıları 2/2/5/4. Doğru sıra: **(a) sözlük birleştirme** (sinonim +
   birim + `additive`, **ifadeye dokunmadan**) → **(b) `cari`** (ifade eşleme) →
   **(c) `ticaret`** (grain KARARI) → **(d) demo kopyaları**.

> **`ticaret` göçü bir KARAR gerektirir:** mikro'nun stok-hareketi grain'i mi kanonik,
> faturanınki mi? **İkisi de meşru olabilir** → çekirdekte **iki ayrı metrik**
> (`satis_tutari` @fatura, `satis_tutari_hareket` @stok_hareketi) ve `satış` sinonimi
> **hangisine ait** olduğu **0.18'in** metrik kaydına yazılır. **Karar kalemi, sahibi ve
> tarihi olur.**

**NASIL** **Yeni desen icat edilmiyor:** `compose()` zaten **dört** YAML üreteci taşıyor;
`_merge_cube_metadata` **beşincisidir**. Göç, MIMARI Faz 2'nin **kanıtlanmış reçetesiyle**:
kabul ölçütü **önce** (her ölçü × her boyut birebir aynı sonuç) → **gölge derleme + MDL
diff** → bayrak → dört şirkette `nl_corpus --kapi` + `eval` → **silme YOK**.
Sıra: `cari` (saf tekrar, en düşük risk) → `ticaret` (**grain kararı gerektirir**) →
`demo-boyahane`'nin kopyaları.
**KAPI** `tests/test_cekirdek_katman.py`: birebir eşdeğerlik · gölge diff **0 fark** · dört
şirkette gerileme yok · grain ihlali **compose'u reddediyor**.
**SONUÇ** Evrensel kavramlar **tek yerde**; *semantic drift* **yapısal olarak** imkânsız.
**GERİ AL** `cekirdek_katman=off` → merge devre dışı, bugünkü compose birebir.

### 2.2 → **BÖLÜNDÜ: çekirdek → FAZ 0.18 · yüzey → 2.2b**  *(yönlendirme kütüğü)*
*"Metrik kaydı = HAKEM"* maddesi dış denetim **D4** ile ikiye ayrıldı:
**hakemlik çekirdeği** (`MetricDefinition` + `sahiplenilen_terimler` + `_match_cube`'un ilk
satırı + çift-sahiplik reddi) → **FAZ 0.18** *(2.1'e bağımlı değil, bu yüzden öne alındı)* ·
**yüzey** (`/settings/metrikler` + çekirdek katman sözlüğüyle birleştirme) → **2.2b**.
**Bu numara altında iş yoktur.**
🔴 *Belge içinde **22 yerde** hâlâ *"2.2"* atfı var (⟳ tablosu · 2.1 · 3.1 · 3.2 · 3.4 ·
Bölüm II ön koşulu · II-F.6 · EK A · EK K). Hepsi **0.18**'i kasteder. Sürüm 4'e kadar bu
kütük yazılmamıştı ve atıflar **boşluğa düşüyordu** — 4.1 için yazılan kütük buraya
yazılmamıştı (§A.2/D5'in doğuş sebebi).*

### 2.2b · Metrik kaydının **YÜZEYİ**  *(çekirdeği → **0.18**)*  [bayrak: `ui_metrik_yonetimi`]

> 🔴 **BÖLÜNDÜ (dış denetim D4).** Bu maddenin **hakemlik çekirdeği** — `MetricDefinition` +
> `sahiplenilen_terimler` + `_match_cube`'un ilk satırı + çift-sahiplik reddi — **FAZ 0.18'e
> taşındı**, çünkü **2.1'in çekirdek katmanına bağımlı DEĞİL** (kendi NASIL'ı *"boş kayıt
> bugünkü davranışı değiştirmez"* diyordu). Burada kalan: **sahiplik ekranı**
> (`/settings/metrikler`) ve `MetricDefinition`'ın çekirdek katman sözlüğüyle
> **birleştirilmesi** (2.1'in `_merge_cube_metadata`'sı ile).
>
> **Aşağıdaki gerekçe ve kapı metni 0.18 için de geçerlidir — kaynak burada korunuyor.**

**NEDEN** ❌ Plan 3 §4.1 *"`cube_router`'a **DOKUNMAZ**"* diyor — bu, katmanı bir
**yönetişim tablosuna** indirger ve **ölçülen en büyük borca** (turların ~%18:
`CLARIFY:konu` %11,5 + yanlış-cube %6,8, ikisinin de kökü **hakemsizlik**) **hiç dokunmaz**.
[KANIT §12.2, §11.2]
**NE**
* backend: **`MetricDefinition`** (`cube` · `measure_name` · `display_name` ·
  `owner_user_id` · `unit` · `rounding` · `description` · `target_ref` · `definition_hash` ·
  `version` · `superseded_by`) **+ `sahiplenilen_terimler: list[str]`** (çıplak terim →
  **tek** metrik)
* backend: **`_match_cube` ÖNCE metrik kaydına bakar** — giriş noktası
  `cube_router._match_cube()`'un **ilk satırı**; terim `_norm` + `_syn_hit`'in **aynı**
  normalizasyonundan geçer (ikinci normalize edici **yazılmaz**)
* 🔴 **İki metrik aynı terimi iddia ederse:** `compose()` **reddeder** (fail-closed) —
  sahiplik **tekil olmak zorundadır**; gerçek belirsizlik **chip'e** gider, kayda değil
* sözleşme: `GET /metrics` + `PATCH /metrics/{id}` │ frontend: **sahiplik ekranı**
  (`/settings/metrikler`, `ui_metrik_yonetimi`)
**NASIL** Mevcut 40+ cube için **migration**: `mdl_writer` katalogdan taslak `MetricDefinition`
üretir (`olusturulma_yontemi="otomatik_taslak"`), `sahiplenilen_terimler` **boş** başlar →
3.1'in sahiplik turu doldurur. **Boş kayıt bugünkü davranışı değiştirmez.**
> 🔴 **YUKARIDAKİ KAPI ve GERİ AL, 0.18'E AİTTİR — 2.2b'nin DEĞİL.** Kaynak metin
> *"0.18 için de geçerlidir"* diye korunuyor; **ama 2.2b'nin kendi kapısı ayrıdır.** Sürüm
> 4'te 2.2b'nin `KAPI`'sı `test_metrik_kaydi.py`, `GERİ AL`'ı `metrik_kaydi=off` diyordu —
> **ikisi de 0.18'in**. Bir doğrulama turunda **2.2b, 0.18'in testiyle *"bitti"* sayılabilirdi:
> kapı yanlış maddeyi yeşile boyar.** Bayrağı `ui_metrik_yonetimi`, kapısı da öyle olmalı.

**2.2b'NİN KENDİ KAPISI ve GERİ AL'I** *(yüzey maddesi — çekirdek 0.18'de kapandı)*:

**NASIL** Yeni panel **AÇILMAZ** (PK-1): `/settings/metrikler`, **var olan** ayarlar
rotasının bir sekmesidir. `MetricDefinition`'ın çekirdek katman sözlüğüyle birleştirilmesi
2.1'in **`_merge_cube_metadata`**'sını kullanır — ikinci birleştirici **yazılmaz**.
**KAPI** `tests/test_metrik_yonetimi_yuzeyi.py` (**yeni**): `GET /metrics` + `PATCH
/metrics/{id}` **frontend tüketicisi var** (K1) · `PATCH` sonrası `sahiplenilen_terimler`
değişince bağlı sertifika **`yeniden_dogrulama_gerekli`**'ye düşüyor (EK C/B8) ·
`ui_metrik_yonetimi=off` iken **rota görünmüyor ve eski davranış birebir** (V-5/E-3) ·
`tests/test_panel_sayisi.py` sayı **artmıyor** (K5).
🔴 **0.18'in `test_metrik_kaydi.py`'si bu maddenin kapısı DEĞİLDİR** — o çekirdeği ölçer,
bu yüzeyi.
**SONUÇ** Sahiplik kararları **YAML yorumu değil, sahibi ve tarihi olan VERİ** olur ve
**ekrandan yönetilir**; 3.1'in sahiplik turu bir arayüz bulur.
**GERİ AL** `ui_metrik_yonetimi=off` → rota yok, `GET/PATCH /metrics` `API_ONLY` beyanıyla
kalır; **çekirdek hakemlik (0.18) etkilenmez** — iki bayrak, iki bağımsız geri alma.

### 2.3 · Departman = **MERCEK**, küp değil  [bayrak: `kapsam_mercegi`]
**NE** backend: `scope: departman | genel | portfoy` parametresi — metrik kaydı üzerinde
**seçim**, yeni `base_object` **doğurmaz** │ sözleşme: `AskRequest.scope` │ frontend:
**kapsam anahtarı** (`ui_kapsam_anahtari`, üç seviye)
**NEDEN** Plan 3 §7.8 **zaten böyle karar vermiş**: *"kapsam parametresi, yeni motor değil"*.
*"Satış küpü / pazarlama küpü"* isteğinin **meşru karşılığı** budur. [KANIT §8.1b, §9.4b]
**KAPI** `tests/test_kapsam_mercegi.py`: kapsam dışındaki metrik **görünmüyor**; `portfoy`
yalnız çok-tenant yetkisiyle.
**GERİ AL** `kapsam_mercegi=off` → departman seçimi yok, her kullanıcı bugünkü tam katalogu
görür. 🔴 **Mercek bir GÖRÜNÜRLÜK aracıdır, bir GÜVENLİK sınırı DEĞİL** — kapatmak yetki
açmaz; sınır her zaman `authorize()` + RLS'tir (§D).

### 2.4 · Aynı-grain çiftlerini merceğe indir  [bayrak: `ayni_grain_gocu`]
> ⚠ **Denetim düzeltmesi:** sürüm 1'de bu madde `cekirdek_katman` bayrağını paylaşıyordu →
> 2.4'ü geri almak 2.1'i de geri alırdı. **Ayrı bayrak.**

**NE** `surdurulebilirlik` ≡ `parti` **ilk aday**: yoğunluk ölçüleri `parti` grain'ine ait
**metriklerdir**; `surdurulebilirlik` bir **mercek** olarak yaşar, **kimliği metrik kaydına
devredilir**.
**KAPI** `nl_corpus` öncesi/sonrası — **erişim düşerse GERİ ALINIR** ve geri alma **testle
korunur** (`elektrik` dersi: `test_SURDURULEBILIRLIK_kimligi_KORUNUYOR` deseni).
**GERİ AL** `ayni_grain_gocu=off` → `surdurulebilirlik` bugünkü **cube kimliğini korur**.
🔴 **Ve geri alma bir TESTLE korunur** — `test_SURDURULEBILIRLIK_kimligi_KORUNUYOR` zaten
var; `elektrik` deneyinin (%64→%56) ikinci kez yapılmasını **o test engelliyor**.

### 2.5 · `MetricTarget` + `target:` beyanı  *(§6.3)*  [bayrak: `hedef_kiyasi`]
**NEDEN** **`target:` beyanı HİÇBİR cube'da yok** — kod bunu `interpret.py:191-195`'te
**itiraf ediyor**. Grafikteki referans çizgisi **hedef değil ORTALAMA** (`viz.py:485-501`).
**NE** backend: **`MetricTarget`** (SCD-2: `metric_ref` · **`scope`** ∈
`tenant|branch|user|sirket_ana_hedef` · `target_value` · `effective_from`/`effective_to` ·
**`set_by`** · **`supersedes`**); 🔴 **`as_of` mu `current` mi AÇIK PARAMETRE** — varsayılan
`current`, rapor yeniden-oynatmada `as_of` │ sözleşme: `AskResponse.hedef` │ frontend:
`chart.ts` **`referenceLine` hedefe bağlanır** (mekanizma zaten var) + `KpiCard` % hedef
**KURAL** **hedef UYDURULMAZ** — kullanıcının **kendi sınırı** okunur (MIMARI Faz G3).
**KAPI** `tests/test_hedef_kiyasi.py`: hedefi olmayan metrikte referans çizgisi **hâlâ
ortalama** ve **öyle etiketleniyor**.
**GERİ AL** `hedef_kiyasi=off` → `target:` okunmaz, grafikteki referans çizgisi bugünkü
anlamını (**ortalama**) korur. ⚠ **Hedef UYDURULMAZ:** beyan yoksa bayrak açık olsa bile
çizgi çizilmez — *"hedef yok"* ile *"hedef 0"* asla karıştırılmaz.

### 2.6 · Mali takvim  *(§4.4)*  [bayraksız: sessiz-yanlış]
**NEDEN** `yoy.py` *"bu yıl/geçen ay"*ı **takvim ayı varsayıyor**; mali yılı Ocak'ta
başlamayan her müşteride **sessiz-yanlış**.
**NE** `TenantConfig.mali_yil_baslangic_ay: int = 1`; `yoy.py` ve `date_filters` onu okur.
**KAPI** `tests/test_mali_takvim.py`: Nisan başlangıçlı fixture ile *"bu yıl"* → **doğru
pencere**. ⚠ **§C/3 (`CLARIFY:dönem` DEĞİŞMEZ) ile kesişim:** bu madde dönem **çözümünü**
değiştirir, **netleştirme oranını değil** — `nl_corpus`'ta `CLARIFY:dönem` payı **sabit
kalmalı**, değişirse kırmızı.

### 2.7 · Adlandırma sözleşmesi — **yalnız YENİ küplere**  [bayraksız: kural]
**NE** Bundan sonra doğan her grain küpü **olayla, tekil** adlandırılır (dbt kuralı).
**Var olan adlar KALIR** — `resolve_cube_name` (`ask.py:989-992`) ad göçünü destekliyor ama
toplu yeniden adlandırmanın **ölçülmüş maliyeti** (%64→%56) onu haklı çıkarmıyor.
**KAPI** `tests/test_yeni_kup_kapisi.py`: yeni küp açan PR'da öncesi/sonrası
`nl_corpus --kapi`; **doğru-cube gerilerse küp geri alınır**.

---

## FAZ 3 · KAPSAM — hakem kurulduktan sonra

> **Doğru hedef ([KANIT §11]'in düzelttiği çerçeveyle):** *"kapsamı artırmak"* değil,
> **kendi yarattığımız belirsizliği çözmek**. `CLARIFY:dönem` (%13,6) **dokunulmaz** —
> **ADR-0007-K3**.

### 3.0 · ⭐ **Tenant açılışı — uçtan uca zincir**  [bayraksız: eksen] *(D8)*
**NEDEN** 🔴 Onboarding sürüm 2'de **dört ayrı yere** dağılmıştı — 3.4 (Ossie ithali) · 3.6
(cold-start metrik) · 3.1 (sahiplik turu) · 8.2 (**tek satır, kapısız**) — ve dördü birlikte
tam olarak *"yeni müşteri değere nasıl ulaşır"* hikâyesi olduğu hâlde **hiçbir yerde
birlikte anlatılmıyordu**. Oysa semantik-katman kategorisinin **1 numaralı müşteri itirazı**
*"modeli kurmak aylar alıyor"*, ve [KANIT §2.1] darboğazı zaten adlandırmış:
*"mekanizma üretiliyor, **sözlük üretilmiyor**"*.
**NE** Tek başlık altında **zincir**:
`müşteri DB'si → şema keşfi (`db_introspect`) → mevcut semantik model varsa **Ossie ithali**
(3.4) → **cold-start metrik taslakları** (3.6) → **sahiplik turu** (3.1) → ilk `nl_corpus`
koşumu` │ sözleşme: mevcut `connections` uçları │ frontend: kurulum sihirbazı (7.3/g)
**NASIL** **Yeni motor yazılmıyor** — zincirin **her halkası zaten var** (`db_introspect` ·
`mdl_writer` · `sinonim_onerici` · `nl_corpus`); eksik olan **uçtan uca hiç koşulmamış
olması**. Bu madde bir **koşum** ve onun **kapısıdır**, bir geliştirme değil.
**KAPI** 🔴 **Yeni bir tenant için İNSAN-SAAT ölçülür ve raporlanır** — §C/14. Bu, zincirin
tamamının **tek kabul ölçütüdür**; alt maddeler kendi kapılarını korur.
**SONUÇ** [KANIT §2.1]'in *"Ossie ithali kapsam tavanına **küratörlük emeği olmadan**
saldıran tek yol"* cümlesi doğruysa, **3.4 bir FAZ 3 maddesi değil, ürünün ticari kilididir**
— ve bu madde onu öyle konumlandırır.
*(8.2 buraya taşındı; FAZ 8'de yalnız 8.3 kalır.)*
**GERİ AL** Koşum — geri alma **yok**. Zincir kırılırsa **kırıldığı halka raporlanır** ve
o halkanın kendi maddesi açılır. 🔴 *"Çalıştı"* demek yetmez: §C/14 (**yeni tenant'ta ilk
doğru cevaba kadar insan-saat**) bu koşumdan **ölçülür ve yayımlanır**.

### 3.1 · ⭐ Sahiplik turu  [bayraksız: alan bilgisi]
**NEDEN** MIMARI'nin kendi hükmü: *"Doğru çözüm bir **sahiplik kararıdır** (çıplak
'elektrik' hangi cube'un?), kimlik silmek değil; ve bu bir **alan bilgisi** işidir."*
Ölçüldü: boyahane yanlış-cube listesinin **ilk 10'unun 10'u** `elektrik`, atiksan'ın
**ilk 9'unun 9'u** `satış` — **aynı hastalık, iki tenant, iki terim**. Ve kimlik silme
**denendi, ölçümle reddedildi**: erişim **%64→%56**, 388 cevap kayboldu. [KANIT §8.3]
**NE** ≥2 cube'un iddia ettiği **her çıplak terim** için yazılı karar (**kalem · sahip ·
tarih**) → **0.18'in** `sahiplenilen_terimler`'ine **veri olarak** girer:

| Terim | Çakışma | Kutu |
|---|---|---|
| `elektrik` | `enerji_makine` ↔ `surdurulebilirlik` | **(1) tek sahip** — 10 varyantın 10'u yanlış cube'a gidiyor |
| `satış` | `ticaret` ↔ `karlilik` (atiksan) ↔ `mal` | **(1) tek sahip** — 9 varyantın 9'u |
| `arıza duruşu` | `bakim` ↔ `oee.plansiz_durus_dakika` | **(2) gerçek belirsizlik → chip** |
| `bakiye` / `borç` | `cari` ↔ `mizan` | **(2) gerçek belirsizlik → chip** — **ders kitabı örneği, KORUNUR** |
| `ortalama duruş` | — (Discovery'ye düşüyor) | **(3) katalog boşluğu** |
| yoğunluk ölçüleri | `surdurulebilirlik` ≡ `parti` | **(3) grain hatası** → 2.4 |

**NASIL** 🔴 **Bu bir YAML işi değil, bir ALAN-BİLGİSİ işidir** — ve çıktısı **veri**dir,
yorum değil: her karar `sahiplenilen_terimler`'e **kalem · sahip · tarih** ile girer
(0.18'in kaydı). Üç kutu: **(1) tek sahip** → kimlik orada, diğerinden çekilir ·
**(2) gerçek belirsizlik** → **chip** (`bakiye` **korunur**) · **(3) grain hatası** →
modelleme borcu (2.4).
**KAPI** her karar için `nl_corpus` öncesi/sonrası; **erişim düşerse geri alınır**. Çıktı
`MIMARI.md`'ye **karar kaydı** olarak yazılır.
**SONUÇ** R1'in 99 vakasının **büyük kısmı** kapanır; `CLARIFY:konu` **azalır** ve
**hangi terimden** azaldığı raporlanır (§C/2'nin *"kaynağı yalnız CLARIFY:konu + yanlış-cube"*
şartı).
**GERİ AL** Her karar **tek tek** geri alınabilir (kayıttan terim çıkarılır → bugünkü
davranış). 🔴 **Toplu geri alma bayrağı `metrik_kaydi`'dir** (0.18). ⚠ **Erişim düşerse
karar geri alınır ve geri alma bir TESTLE korunur** — `elektrik` dersinin aynısı.

### 3.2 · ⭐ **R1'i kapat (99 vaka)**  [bayraksız: kapsam]
**NEDEN** *"Katalogda **var olan** bir ölçü sinonimi, düz sorulduğunda cube'unu bile
tanıtmıyor."* 470 sinonimlik sondada **`R1: 99`** (doğrulandı); §6.1h ölçtü: **R1'in TAMAMI
gerçek ölçü-düzeyi belirsizliğidir**. Bu depoda ölçülmüş **tek en büyük kaldıraç** ve
**hiç çalışılmadı**. [KANIT §8.3]
**NE** backend: **0.18'in** hakemi + 3.1'in kararları R1'i kapatır │ sözleşme: — │
frontend: kalan vakalar `/settings/metrikler`'de **"sahipsiz terim"** listesi
**NASIL** Prosedür: `lab/r1_envanteri.py` (yeni) — 470 sinonimi koşar, `reject_reason=R1`
olanları `_takilan_kelimeler` ile eşler, **cube adayları + kanıt uzunluğu** ile CSV üretir;
insan karar verir; karar `sahiplenilen_terimler`'e yazılır.
**KAPI** `lab/r1_envanteri.py` çıktısı: **R1 sayısı 99 → hedef ≤ 30** (kalanlar gerçek
belirsizlik, chip'e gider). `nl_corpus` doğru-cube **artmalı**.
**SONUÇ** §C/1-2'nin ölçülmüş **en büyük tek kaldıracı** kapanır; kalan sahipsiz terimler
bir **liste** olur — *"bilinmeyen"* olmaktan çıkıp **iş kalemi** hâline gelir.
**GERİ AL** 3.1 ile aynı yol: kararlar kayıttan çıkarılır, `metrik_kaydi=off` toplu geri
almadır. `lab/r1_envanteri.py` bir **rapor aracıdır** — geri alınacak davranışı yoktur.

### 3.3 · Terfi kuyruğu **kapanış oranı**  [bayraksız: ölçüm]
**NEDEN** §9 ilke 4: *"her Discovery cevabı bir kapsam boşluğunun belgesidir"* — ama
**kaçının kapandığını kimse ölçmüyor**.
**NE** backend: haftalık *"açılan boşluk / kapanan boşluk"* raporu │ frontend:
`ui_gelisim_paneli`'nin bir satırı (7.7)
**KAPI** `lab/reports/terfi_kapanis.md` — oran **kapıya** bağlanır.

### 3.4 · ⭐ **Apache Ossie ithali**  [bayrak: `ossie_ithal`]
**NEDEN** Sektörün fiili standardı: eski adı **OSI**, **Haziran 2026'da ASF'e bağışlandı**
(Snowflake · dbt Labs · Databricks · Google · AWS · Cube · AtScale · Qlik + 50 kurum).
YAML üst-yapıları **bizim `packs/` yapımızla neredeyse birebir**. Sürüm **0.1.1** /
`0.2.0.dev0`. [KANIT §2.1]
⚠ **MIMARI §3.4 çelişkisi:** *"Bilerek ALINMAYANLAR: `osi` — bugün müşteri senaryosu yok"*.
**Karar geri alınıyor**, gerekçe: standart o tarihten sonra ASF'e geçti ve **ithal tarafı
kapsam tavanına küratörlük emeği olmadan saldıran tek kaldıraç**. ⟳ tablosunda işaretli.
**NE** backend: müşterinin semantik modeli **bir pack katmanı** olarak okunur —
`Datasets→models` · `Metrics→measures` · `Fields→dimensions` ·
`Relationships→relationships.yml` · **`AI Context`→`synonyms`** │ sözleşme:
`POST /connections/{id}/import-semantic` │ frontend: bağlantı sihirbazında **"mevcut
semantik modelini içe aktar"** adımı (`ui_ossie_ithal`)
**NASIL** **Çevirici yazılır, motor yazılmaz:** Ossie YAML → `packs/` katmanı; hedef
şekil **zaten bizimki**. 🔴 **İthal edilen her cube fail-closed kapılardan geçer:**
`validate_project()` + `test_member_sweep` (build-time `LIMIT 0`) + **fan-out sertifikası
ÖLÇÜLÜR** — ithal bir ilişki **`olculmedi` damgasıyla** gelir, sessiz *"sağlıklı"* değil.
2.1'in **çekirdek katmanına iner**, ERP katmanına değil (aksi hâlde dördüncü kopya doğar).
**KAPI** İthal edilen her cube `validate_project()` + `lab/member_sweep.py`'den geçer;
**fan-out sertifikası ölçülür** — ithal ilişki **`olculmedi`** damgasıyla gelir, sessiz
*"sağlıklı"* **değil**.
**SONUÇ** Küratörlük emeği olmadan kapsam; ve kilitlenme itirazı ölür.
**NOT** Ossie'nin **`Metrics`'i model seviyesindedir** — **0.18'in** hedeflediği şeklin ta
kendisi. Metrik katmanı ayrılmadan bu iş empedans uyuşmazlığıyla boğuşurdu.
**GERİ AL** `ossie_ithal=off` → ithal ucu kapalı.

### 3.5 · Yeni kaynak sistemler  [bayraksız: genişleme]
**NE** ⚠ **denetim düzeltmesi: 17 değil, backend'de hiç geçmeyen 12 konnektör**
(BigQuery/Snowflake/Databricks/Trino/`s3_file`/`minio_file` …) = **kod yazmadan yeni müşteri**.
**KAPI** `db_introspect → mdl_writer → sinonim önerici → insan onayı` zinciri **gerçek bir
müşteri DB'sinde uçtan uca koşulur** — bugüne kadar **hiç koşulmadı**.

### 3.6 · Cold-start metrik önerisi  *(§4.2)*  [bayrak: `coldstart_metrik`]
**NE** backend: `db_introspect.draft_mdl()` **zaten** model çıkarıyor; eksik **önem
sıralaması** (satır sayısı + kolon-adı sinyali) │ frontend: **diff-onay ekranı** —
`measures.py`'nin diff-önizleme deseni **aynen taşınır**, ikinci onay motoru **yazılmaz**;
**"görünmez kolon" göz-ikonu** *(Plan 2 §4.2/3 — kaçmıştı)*: kapatılan kolon **MDL'ye hiç
yazılmaz, LLM asla göremez** (Plane Enforcer'ın UI karşılığı)
**KAPI** `tests/test_coldstart.py`: kapatılan kolon üretilen MDL'de **yok**.

---

## FAZ 4 · ÖLÇÜM ve KANIT
**GERİ AL** `coldstart_metrik=off` → taslak metrik üretilmez, yeni tenant bugünkü boş kayıtla
başlar. Üretilmiş taslaklar **silinmez**, `onaylandi=False` ile bekler.

### 4.1 · ⭐ Ölçüm kapıları CI'ya — 🔴 **FAZ 0.15'E TAŞINDI** *(D1)*

> **Bu madde artık FAZ 0.15'tir.** Gerekçe: regresyon ağı, **en riskli ameliyattan (FAZ 2)
> ÖNCE** kurulmalı — koşucu (`lab/kapi.py --tam`) **zaten yazılmış**, maliyeti bir workflow
> dosyası. Aşağıdaki metin **kaynak olarak korunuyor**; uygulama 0.15'tedir.

**NEDEN** `.github/workflows/backend-ci.yml:56` **yalnız `pytest -q`** koşuyor.
`nl_corpus --kapi` · `konusma_senaryolari` · `nl_accuracy` · A/B koşucusu — **hiçbiri
otomatik değil**. Yürüyen planın A1/A2/A3'ü **aleti onardı** (vaka 4→63, A/B koşucusu,
canlı-yetenekli) — **ama kapıya bağlamadı**. [KANIT §0.0]
**NE** backend: `.github/workflows/nightly.yml` — dört aracı koşar │ sözleşme: — │
frontend: — (`api-only`)
**NASIL** **İnce çevirici — kayıt KURULMAZ, ÇEVRİLİR** (`tools.py`'nin kendi notu).
`llm_araclari` şemayı, `izinli_araclar` yetki süzgecini **zaten üretiyor**; MCP yüzeyi
bunları **okur**, ikinci bir araç kaydı **yazmaz**.
**KAPI** **Gerileme eşikleri:** `nl_corpus` erişim **−1 puan**, doğru-cube **−0,5 puan**
(mevcut `TOLERANS_PUAN`/`TOLERANS_DOGRULUK` değerleri) · `nl_accuracy` **hiçbir vaka
FAIL'e dönmez** · `konusma_senaryolari` **hiçbir sınıf gerilemez**. Aşımda **kırmızı**.
**SONUÇ** Ana metrik *"elle koşulmadıkça hiç ateşlenmiyor"* durumu biter.
**GERİ AL** Bayrak `off` → MCP ucu **yok**; HTTP yolu **etkilenmez**. 🔴 **Ve değişmez:**
MCP'den çağrılan araç HTTP'den çağrılanla **aynı dört kapıdan** geçer ve **aynı makbuzu**
üretir — ayrı bir yol açılırsa bu madde **yanlış yapılmış demektir**.

### 4.2 · ⭐ Risk-kapsam eğrisi  [bayraksız: kanıt]
**NEDEN** MIMARI §9.1: *"hiçbir sevk edilmiş BI ürünü … **risk-kapsam eğrisi**
yayınlamıyor."* Literatür: kara-kutu sinyaller **0,61-0,68 AUROC**'ta platoluyor;
iki-sağlayıcılı topluluk **0,822 AUROC / ECE 0,031**; pratik nokta **"%27 kapsam / %24
seçici risk"**. Bizim ölçülen noktamız **~%70 doğrudan cevap / ~%7 hata**. [KANIT §2.3]
**NE** backend: `lab/risk_kapsam.py` — eğri **ayrık kapılarımız** üzerinde (`route` →
`tie-chip` → `intent` → `discovery`); **skaler `confidence` UYDURULMAZ** │ sözleşme: — │
frontend: — (`api-only`, gerekçe: **araştırma çıktısı**)
**⚠ YAN KURAL** `consistency_k` uyumu **bir güven eşiğine dönüştürülmez** — araştırma bunu
doğrudan çürütüyor: *"bir model son derece self-consistent olup yine de **tutarlı biçimde
YANLIŞ** olabilir."*
**NASIL** **Skaler `confidence` UYDURULMAZ** — eğri bizim **ayrık kapılarımız** üzerinde
tanımlanır (`route → tie-chip → intent → discovery`). Veri **zaten var**: her cevabın
`source`'u ve `reject_reason`'ı makbuzda.
**KAPI** `lab/reports/risk_kapsam.md` + eğri **yeniden üretilebilir** (aynı sha → aynı eğri).
**SONUÇ** MIMARI §9.1'in *"hiçbir sevk edilmiş BI ürünü risk-kapsam eğrisi yayınlamıyor"*
iddiası **sayıya** döner ve yayımlanabilir olur.
**GERİ AL** Rapor — davranış değiştirmez. 🔴 **Yan kural bağlayıcı:** `consistency_k`
uyumu bir güven eşiğine **DÖNÜŞTÜRÜLMEZ**; araştırma bunu doğrudan çürütüyor (*"son derece
self-consistent ve tutarlı biçimde YANLIŞ"*).

### 4.3 · ⭐ Çok-turlu Türkçe benchmark (**sharding**)  [bayraksız: kanıt]
**NEDEN** ICLR 2026 En İyi Makale (*LLMs Get Lost In Multi-Turn Conversation*): 200.000+
simüle konuşma, 15 model → **ortalama −%39 doğruluk**, **%112 güvenilirlik çöküşü**; kök
neden *"erken turlarda varsayım yapıp erken bir nihai cevaba yapışma"*, **orta turlara atıf
%20'nin altında**. Azaltma: **recap** (+16 puan). **Bizim mimarimiz recap'in deterministik
hâlini yapısal olarak uyguluyor** — canlı: 4 turlu thread, **dördü de `source=cube`, sıfır
LLM**. [KANIT §2.4]
**NE** backend: `lab/sharding.py` — **algoritma:** her tek-turluk soru
`{ölçü, dönem, boyut, filtre, sıralama}` **atomlarına** ayrılır (`route()`'un çözdüğü
`cube_query` alanlarından türetilir, **yeni ayrıştırıcı yazılmaz**); atomlar **rastgele
sırayla** turlara dağıtılır (tohum sabit); her turda `cube_query` **birikmeli** olmalı │
frontend: — (`api-only`)
**NASIL** ICLR 2026'nın **sharding** yöntemi `nl_corpus`'un 10.865 turuna uygulanır:
tek-turluk soru atomik parçalara bölünüp turlara dağıtılır. **İkinci senaryo üreteci
yazılmaz** — deneyim süiti (§F.1) bu harness'i kullanır.
**KAPI** Ölçülen üç sayı: **yapı kaybı** (*"ilişkilendiremedim"* sayısı) · `cube_query`
**sürekliliği** (her turda dolu mu) · **tur-derinliği ↔ doğruluk eğrisi**. Hedef: 5 turda
doğruluk **−%10'dan az** düşsün (makalenin −%39'una karşı).
**SONUÇ** Faz X'in ölçek karşılığı: 9 senaryo sınıfı yerine **binlerce**. Ve **dünyada
yayınlanmamış** — makale *text-to-SQL*'de ölçtü; **semantik katmanın aynı testteki farkı hiç
ölçülmedi**.
**GERİ AL** Ölçüm harness'i — davranış değiştirmez. Sonuç kötü çıkarsa **yayımlanır**;
kötü sonucu saklamak §C/16'nın *"ilan edilmiş puanlama kuralı"* şartını çiğner.

### 4.4 · Ossie **ihracı** + `Custom Extensions`  [bayrak: `ossie_ihrac`]
**NE** `packs/` → Ossie YAML. **Farkımız `Custom Extensions` içinde**: **fan-out
sertifikası** · `always_filter` parmak izi · `additive:` beyanı · `dimension_origin`.
**KAPI** **round-trip**: ihraç → geri ithal → üretilen `cube_query` **birebir aynı SQL**.
**GERİ AL** `ossie_ihrac=off` → ihraç ucu yok; `packs/` **hiç etkilenmez** (ihraç **okuma**
işlemidir). 🔴 **Round-trip kapısı geri almadan bağımsızdır:** ihraç edilen model geri
ithal edildiğinde **birebir aynı SQL**'i vermelidir — vermiyorsa bayrak **açılmaz**.

### 4.5 · MCP yüzeyi  [bayrak: `mcp_yuzeyi`]
**NEDEN** Linux Foundation **Agentic AI Foundation** yönetiminde; kararlı spec
**2025-11-25**; dbt · Cube · AtScale MCP sunucusu yayınlıyor. `app/tools.py` **zaten** hem
şema hem yetki süzgeci üretiyor — dosyanın kendi notu: *"MCP adaptörü — ileride **ince bir
çevirici**; kendi kaydını KURMAZ."* [KANIT §2.7]
**KAPI** `tests/test_mcp.py`: MCP'den çağrılan araç, HTTP'den çağrılanla **aynı dört
kapıdan** geçer ve **aynı makbuzu** üretir. ← jenerik MCP sunucularında **olmayan fark**.
**GERİ AL** `mcp_yuzeyi=off` → MCP ucu yok, HTTP yolu **etkilenmez**. 🔴 **Değişmez:** MCP'den
çağrılan araç HTTP'den çağrılanla **aynı dört kapıdan** geçer ve **aynı makbuzu** üretir;
ayrı bir yol açılırsa madde **yanlış yapılmış demektir**.

### 4.6 · `docs/adr/`  [bayraksız: belge]
**NEDEN** **20 ADR kimliği, kod kapsamında 252 atıf, 0 dosya** (doğrulandı). Ve
**ADR-0007-K3**, §C'nin **3. çıkış ölçütünü** taşıyor — yani v1'in kırmızı çizgisi **var
olmayan bir belgeye** dayanıyor.
**NE** `backend/docs/adr/NNNN-*.md` — MIMARI §8.2'nin rekonstrüksiyonu **kaynak** olarak
kullanılır.
**KAPI** `tests/test_adr_dosyalari.py`: kodda anılan her ADR kimliği için **dosya var**;
yeni kimlik **dosya olmadan merge edilemez**.

### 4.7 · Teknik rapor  [bayraksız: yayın]
**NE** *"Türkçe'de semantik-katman tabanlı konuşan BI — kapsam, doğruluk, risk-kapsam ve
çok-turlu dayanıklılık"*, **yeniden üretilebilir harness** ile.
**KAPI** 🔴 **Rapor, §C/16 ölçülmeden YAYIMLANAMAZ** (4.8). Ek kapılar:
harness **yeniden üretilebilir** (tek komut, `--network none`, sabit tohum) · her sayı
**HEAD damgası + komut** taşır (D2) · **netleştirme AYRI SATIR** olarak raporlanır,
paydadan **gizlice çıkarılmaz** — *rakiplerin manşet sayılarını kıyaslanamaz yapan şey tam
olarak budur.*
**NEDEN** **BIRDTurk** (arXiv 2602.03633 / SIGTURK 2026) Türkçe cezasını **text-to-SQL'de**
ölçtü; **semantik katmanın Türkçe katkısı hiç ölçülmedi** — §9.1'in boş bıraktığı yer.
Kıyas zemini: Snowflake BIRD **%57→%78** `[DOĞRULANMADI — kaynak EK F'ye]`.
🔴 **ÖN KOŞUL: 4.8** — bu rapor **§C/16 olmadan YAYIMLANAMAZ.**

### 4.8 · ⭐ **Uçtan uca doğruluk aleti** *(§C/16'nın ölçüm aracı)*  [bayraksız: kanıt] *(D7)*
**NEDEN** 🔴 **Rakiplerin yayımladığı tek kıyaslanabilir sayıyı Dima ÖLÇMÜYOR.** §C/1-2
**cube seçimini** ölçüyor (%93,2 = *"doğru cube"*, *"doğru cevap"* **değil**);
`nl_accuracy` **n=63**; `eval` MIMARI §7'nin kendi ifadesiyle *"zaten çalışan şeye göre
kuratörlenmiş"* bir **regresyon kilidi**. Yani dışarıya kıyaslanabilir bir sayı vermek için
**bugün elimizde alet yok**.
**NE** backend: **`lab/uctan_uca.py`** — **tutulmuş (held-out)** küme, **n≥100**, ekip dışı
küratörlenmiş │ frontend: — (`api-only`, gerekçe: **araştırma çıktısı**)
**NASIL — puanlama kuralı İLAN EDİLİR** (en yakın analog: n=90 gerçek kurumsal vaka):
🔴 *"Bir cevap ancak **dönen değer**, **varlık kapsamı** ve **zaman/filtre semantiği** altın
cevapla eşleşiyorsa **doğru** sayılır."*
🔴 **Netleştirme AYRI SATIR** olarak raporlanır — **paydadan gizlice çıkarılmaz**.
*(Rakiplerin manşet sayılarını kıyaslanamaz yapan şey tam olarak budur: her satıcı
reddedilenleri paydadan sessizce çıkarıyor.)*
**NASIL** **Yeni küme kuratörlenmez** — `nl_corpus`'un dışında **tutulmuş** bir küme
ayrılır ve **kilitlenir**. Puanlama kuralı **önce** ilan edilir, sonra koşulur (aksi sıra
sonucu kurala uydurmaya davet eder).
**KAPI** `tests/test_uctan_uca_kapisi.py` — küme **tutulmuş** kalır (eğitim/ayar için
kullanılmaz); puanlama kuralı **kod içinde tek yerde**.
⚠ **Ve açık soru kayda geçer:** `nl_accuracy`'nin **63 etiketli vakasının etiketlerini kim
doğruladı?** BIRD/Spider'da anotasyon hata oranı **%52,8 / %62,8** ölçüldü →
**10 puanın altındaki fark GÜRÜLTÜDÜR** ve bu, yayımlanacak her sayının yanına yazılır.

---

## FAZ 5 · KONUŞMA ve DENEYİM

> **Absorbe edilen:** Plan 3 §5 · §6.1 · §6.4 · §7.9 · §8.4 · §13.1 · §15.6 + Plan 2
> §5.1/§5.3/§7.x + dışarıdan gelen özellik notunun **kod-kanıtlı** maddeleri [KANIT §19].
**SONUÇ** §C/16 ölçülebilir olur; rakiplerin yayımladığı **tek kıyaslanabilir sayı**
elde edilir. 🔴 **FAZ 4.7'nin teknik raporu bu sayı olmadan YAYIMLANAMAZ.**
**GERİ AL** Ölçüm aracı — davranış değiştirmez. ⚠ **Tutulmuş küme bir kez bakıldıktan
sonra tutulmuş değildir**; küme kirlendiyse **yenisi ayrılır**, eskisi `eval`'e devredilir.

### 5.0 · 🔴 **K3 — konuşma türleri thread'lerin bir sınıfına YAPISAL OLARAK kapalı**  [bayraksız: hata]
**NEDEN** **Doğrulandı:** `followup.sinifla`'nın **TEK** çağrı yeri `ask.py:2933` ve o,
**`if structural_followup:` (`:2862`) bloğunun İÇİNDE**. Yani istemci `cube_query`
**göndermiyorsa** (Discovery / ham thread), *"bu neden böyle?"* · *"normal mi?"* ·
*"analiz et"* — **hiçbiri sınıflanmıyor**. Beş konuşma türü de o thread'lerde **erişilemez**.
Ayrıca `baglam_var=` tek çağrıda **sabit `True`** → `followup.py`'nin *"bağlam-yok"* kuralı
**üretimde hiç ateşlenmiyor** (yalnız birim testinde yaşıyor).
⚠ **Ve bu kusur 0.21'in gerekçesidir:** 1.930 satırlık bir gövdede bir çağrının **yanlış
`if`in içinde** olduğu görünmüyor.
**NE** backend: `sinifla()` çağrısı `structural_followup` bloğundan **ÇIKARILIR**;
`baglam_var` **gerçek bağlam durumundan** hesaplanır │ sözleşme: — │ frontend: — (`api-only`)
**KAPI** `tests/test_takip_ucuncu_sinif.py` genişletilir: **`cube_query` YOKKEN** *"bu neden
böyle?"* → `SINIF_KONUSMA/TUR_NEDEN`; ve `baglam_var=False` yolu **üretimde erişilebilir**.
**SONUÇ** 6. ve 7. tür (5.1/5.2) **doğduğu andan itibaren** her thread sınıfında çalışır —
aksi hâlde yeni türler de **aynı bloğun içine** doğar.
**GERİ AL** — (hata düzeltmesi; gerileme `konusma_senaryolari` ile ölçülür).

### 5.1 · ⭐ **6. tür: *"bunu takip et"***  [bayrak: `tur_takip`]
**NEDEN** `followup.sinifla` **koşuldu**: *"bunu takip et"* → **`SINIF_YENI`** → kapsam
kapısı **R10** → dürüst red. `takip et` grep'i `followup.py` ve `cube_router.py`'de
**sıfır**. **Panoya/zamanlamaya giden HİÇBİR doğal-dil yolu yok** — kullanıcı 🔔 ve
*"+ panoya ekle"* düğmelerini **fareyle bulmak zorunda**. MIMARI §12.11 **kendisi de**:
*"**Henüz YOK** — reçete kartından tek tıkla `schedules.create`"*. [KANIT §19.2]
**NE** backend: `TUR_TAKIP` + kalıp sözlüğü (kelime sınırı disiplini) → **`schedules.create`
ÖNERİSİ** (6.1'in onay akışından geçer) │ sözleşme: `AskResponse.onay_talebi: OnayTalebi`
│ frontend: `OperatorOnayKarti` (`ui_operator`) — **yeni panel değil**, kartın şeridi
**NASIL** `followup.py`'nin dört türünün **aynı kalıbı**; `schedules.py` (763 satır) +
`uyari_nedeni()` **hazır**.
**KAPI** `tests/test_tur_takip.py`: *"bunu takip et"* → `SINIF_KONUSMA/TUR_TAKIP`;
**onaysız zamanlama oluşmuyor**; **≥10 gerçek ifade varyantı** (5.3).
**SONUÇ** Onaylı yazmanın **vitrin senaryosu**, en olgun motora bağlanır.
**GERİ AL** `tur_takip=off` → tür tanınmaz, bugünkü davranış birebir.

### 5.2 · ⭐ **7. tür: *"paylaş / müdüre 3 cümle"***  [bayrak: `tur_paylas`]
**NEDEN** 🔴 **En öğretici bulgu:** *"müdüre 3 cümle yaz"* niyet olarak `TUR_ANLAT`'a
**çok yakın** (`followup.py:110-113`: `_ANLAT = ("analiz et", … "ozetle", … "anlat", …)`),
ama sözlükte *"yaz"*/*"3 cümle"* olmadığı için **yakalanmıyor** → **çalışan bir yetenek bir
kelime yüzünden kullanıcıya kapalı**. Ve `share|public` uç **sıfır**. [KANIT §19.2]
**NE** backend: `TUR_PAYLAS` + **paylaşılabilir link ucu** (`POST /share` → imzalı, süreli
token; **maskeli payload**, §D.2/2) │ sözleşme: `AskResponse.share_url` │ frontend: paylaş
menüsü (PNG/SVG/CSV/PDF **zaten var**, link eklenir) + **rapor yapısı** (5.13b)
**NASIL** 🔴 **Yetenek ZATEN VAR ve çalışıyor** — `TUR_ANLAT` (D2'de indi). Eksik olan
**erişim**: *"müdüre 3 cümle yaz"* kalıp sözlüğünde yok. Yeni motor **yazılmaz**, kalıplar
**kullanıcı ifadelerinden** beslenir (5.3). Paylaşılabilir link `report.compose` üstüne
ince bir uç.
**KAPI** `tests/test_tur_paylas.py`: link **süreli** ve **maskeli**; ≥10 ifade varyantı.
**SONUÇ** Ölçülmüş bir **erişilemezlik** kapanır: D2'de yazılmış, testli bir yetenek
kullanıcının kendi kelimeleriyle **ulaşılabilir** olur.
**GERİ AL** `tur_paylas=off` → kalıplar eşleşmez, `TUR_ANLAT`'ın bugünkü erişimi
**birebir korunur**; link ucu `API_ONLY` beyanıyla kalır.

### 5.3 · ⭐ Kalıp sözlüklerini **kullanıcı ifadelerinden** besle  [bayraksız: kök neden]
**NEDEN** 5.2'nin kökü *"kelime eksik"* değil: kalıp sözlüğü **tasarımcının kelimelerinden**
kuruldu (*analiz et · yorumla · özetle*), **kullanıcının ifadelerinden** değil. Kelime
eklemek **ADR-0008'in yasakladığı** yamadır.
**NE** `nl_corpus`'un **`REAL_PHRASINGS`** deseni (13 ölçü × 41 gerçek ifade, etiket kelimesi
**bilinçle dışlanmış**) **konuşma türlerine** genişletilir → `lab/konusma_ifadeleri.py`.
**NASIL** 🔴 **Kelime eklemek YASAK** (ADR-0008). Kök neden: kalıp sözlüğü
**tasarımcının kelimelerinden** kuruldu (*analiz et · yorumla · özetle*), **kullanıcının
ifadelerinden** değil. Çözüm `nl_corpus`'un **`REAL_PHRASINGS`** deseninin (13 ölçü ×
gerçek kullanıcı ifadesi) **konuşma türlerine** genişletilmesi — yani **veri**, yama değil.
**KAPI** her konuşma türü için **≥10 gerçek ifade varyantı**; `konusma_senaryolari`'ye sınıf.
⚠ **Bağımlılık (denetim bulgusu S6):** varyantların **kalıcı** kaynağı FAZ 8.1'dir. **v1
kapısı ≥10 varyantla kapanır** (elle küratörlenmiş); 8.1'den sonra **otomatik beslenir**.
**SONUÇ** Her tür için **≥10 gerçek varyant** ölçülür (§C/9'un kapısı); *"bir kelime
yüzünden kapalı yetenek"* sınıfı **ölçülebilir** hâle gelir.
**GERİ AL** Kalıp korpusu — bayraksız. Bir varyant **yanlış-pozitif** üretirse korpustan
çıkarılır ve **çıkarma gerekçesiyle** kayda geçer. ⚠ Geri alma *"eski dar sözlüğe dönmek"*
değildir; o, ölçülmüş kusuru geri getirirdi.

### 5.4 · Eksik chip'ler  [bayraksız: ucuz kazanç]
**NEDEN** `mom` **motoru var, chip'i yok** (`cube_router.py:3035-3037` chip yalnız `yoy`;
`InterpretationBar.tsx:521-545` toggle yalnız `compare="yoy"`); **"dün" hiç yok**; **Top-N
NL'i tam ama chip yok** (`suggest_next_steps` order/limit üretmiyor). [KANIT §19.1, §19.3]
**NE** backend: `suggest_next_steps` → `mom` · `dün` · **Top-N** chip'leri │ sözleşme:
mevcut `next_steps` │ frontend: `InterpretationBar` render eder
**KAPI** `tests/test_chipler.py`: üç chip **üretiliyor ve tıklanınca `/cube` ile 0-LLM**.
**SONUÇ** **Sıfır motor işi** — var olan yetenek **erişilebilir** olur.

### 5.5 · Başlık Δ kartı + **streak**  [bayraksız: yorum]
**NEDEN** `interpret.py`'de **`compare`'a özel fact türü yok** → Δ yalnız kolon+grafikte.
**Ardışık dönem (streak) tespiti yok** — *"3 aydır düşüyor"* denemiyor; yalnız ilk↔son
kıyaslanıyor, **aradaki zikzak görünmez**. [KANIT §19.3-8, §19.3-13]
**NE** backend: `interpret`'e iki fact türü — **`delta`** (mutlak + %) ve **`streak`**
(ardışık aynı-yönlü dönem sayısı; **n<3 → üretilmez**) │ frontend: `OutputInsight`
`FACT_ICON`'a iki ikon
**KAPI** `tests/test_interpret.py`: `streak` yalnız **≥3 ardışık** dönemde;
**kısmi son dönem DIŞLANIR** (Plan 3 B5 — Tableau *"Ignore Last"*).

### 5.6 · ⭐ Peer karşılaştırma  [bayrak: `peer_kiyasi`] · 🔴 **ÖN KOŞUL: AJ2**
> 🔴 **BU MADDE YENİDEN ÇERÇEVELENDİ (sürüm 6) — ve gerekçesi kendi NEDEN'inde saklıydı.**
> Madde `compare`'ın **sabit kodlu bir enum** olduğunu doğru ölçtü, sonra çözüm olarak
> **üçüncü bir enum değeri** (`"peer"`) ekledi ve bunu *"üçüncü kıyas ekseni"* diye başarı
> hanesine yazdı. **Yani hastalık teşhis edildi, reçeteye hastalığın kendisi yazıldı** —
> dördüncüsü (adlı dönem ↔ adlı dönem) için aynı konuşma yeniden yapılacaktı.
> **Düzeltme:** `compare` **enum'dan ALANA** çevrilir (**AJ2**); `peer` o alanın bir
> **değeri** olur, yeni bir dal değil. **5.6 küçülür, kapsamı değişmez** — ve **AJ2'den
> SONRA** iner. *Aksi hâlde 5.6 üçüncü değeri çakar, dördüncüsü beşinci konuşmayı doğurur.*
> ⚠ **Sayı düzeltmesi:** *"dört yerde"* **yanlıştı** — ölçüldü @`88bde2a`: **6 üyelik kapısı**
> (`contribution.py:337` · `report.py:57` · `dashboards.py:180,289` · `ask.py:1007,1110`)
> \+ `cube_router.py:1312` `_ACIK_KIYAS` tanımı = **7 dokunuş**. *Her yeni eksen = 7 dosya.*

**NEDEN** Ölçüldü — **HİÇ YOK**: `compare` **yalnız zaman** (üyelik kapısı **6 yerde**,
tanımıyla **7**). En yakın şey `viz.py:485-501` `reference_line{kind:"average"}` ama (a) yalnız
**gösterilen satırların** ortalaması, **kohort tanımı yok**; (b) **hat-içi agregat
kurulmuyor**; (c) **kardinalite<4'te hiç üretilmiyor**. *"Bu makine vs hat ortalaması"*
bugün **cevaplanamıyor**. [KANIT §19.3-17]
**NE** backend: **`compare: "peer"`** + `peer_dimension` (kohort tanımı: hangi boyutta
gruplanacak) — dış sarma ile grup ortalaması │ sözleşme:
`AskResponse.peer_reference: {dimension, value, avg}` │ frontend: referans çizgisi + **Δ
kolonu**
**NASIL** `cube_sql`'in `measure_having` sarma kalıbı **yeniden kullanılır**.
**KAPI** `tests/test_peer_kiyasi.py`: makine × hat ortalaması **doğru**; kohort tanımsızsa
**dürüst red** (uydurma grup yok).
**SONUÇ** **Üçüncü kıyas ekseni** — hiçbir planda yoktu.
**GERİ AL** `peer_kiyasi=off` → `compare` yalnız zaman ekseninde (bugünkü davranış);
kohort tanımı okunmaz, `reference_line` bugünkü *"ortalama"* anlamını korur. ⚠ **Kohortun
kendisi silinmez** — kapalıyken de tanımlı kalır ki açıldığında yeniden kurulmasın.

### 5.7 · Segment A↔B Δ  ·  5.8 · Kaydet/şablonlaştır  [bayraksız]
**NE** `in` filtresi + yan yana çizim **var**, **A−B Δ kolonu yok** → eklenir.
`saveDecision` **yalnız** `PrescriptionLayer`'dan çağrılıyor → **katkı/why cevabından da**;
**şablonlaştırma** (kayıt → yeniden koşulabilir parametreli analiz) eklenir.
**KAPI** `tests/test_segment_delta.py` · `tests/test_karar_sablonu.py`.

### 5.9 · Kanal genişlemesi + **bildirim kapısı**  [bayrak: `kanal_slack` · `kanal_whatsapp` · `sabah_digest`]
**NEDEN** `channels.py` `@register("inapp")` (`:144`) ve `@register("email")` (`:189`)
**var**; **Slack yok** (yalnız `:3-4` yorumunda plan). `brief|digest` grep **sıfır** — her
schedule **ayrı bildirim** atıyor. Alarm literatüründe **%72-99 yanlış-alarm**
`[DOĞRULANMADI — kaynak EK F'ye]`.
**NE**
* backend: `@register("slack")` + **`@register("whatsapp")`** *(Plan 2 §7.4 — Türk KOBİ
  pazarında günlük iş aracı)* — desen hazır
* backend: **birleşik sabah digest'i** (N pano/KPI tek gönderide)
* backend: 🔴 **Bildirim kapısı — dört sıralı adım** *(Plan 3 §7.9 — kaçmıştı)*:
  **`dedup_key = H(kaynak_tip, kaynak_id, yon)`** → **`suppression_window`** (DB'de
  kayıtlı; **silinmez, GİZLENİR**) → **önem sıralaması** → **`correlation_group`**
  (eşzamanlı ilişkili sinyaller **TEK bildirimde**)
* backend: **`NotificationPreference`'ın ilk tüketicisi** — `channels.resolve_targets()`
  onu okur (bugün **yetim tablo**, 0 satır, router yok)
* sözleşme: `NotificationEvent.dedup_key` · `correlation_group` · gönderim durumu
  (**başarılı / tekrar denendi / başarısız**)
* frontend: `NotificationsBell` **filtreli**; zamanlamalar ekranında **gönderim durumu**
**KAPI** `tests/test_bildirim_kapisi.py`: aynı `dedup_key` pencere içinde **ikinci kez
gönderilmiyor** ama **kayıtta duruyor**; `NotificationPreference` opt-out'u **uygulanıyor**.
**GERİ AL** Her kanal **kendi bayrağını** taşır → biri kapanınca diğerleri çalışır. Hepsi `off`
→ bugünkü e-posta + in-app davranışı birebir. ⚠ **`sabah_digest=off` → her schedule KENDİ
bildirimini atar** (bugünkü davranış); digest bir **birleştirme**dir, yeni bir bildirim
kaynağı değil.

### 5.10 · KPI pin semantiği  [bayrak: `kpi_pin`]
**NE** Pano **var** (`dashboards.py:27` `_MAX_PER_USER = 10`) ama **KPI-pin semantiği ayrı
değil** ve **NL yolu yok** → 5.1 ile birlikte.
**KAPI** `tests/test_kpi_pin.py`: pin edilen KPI `dashboards`'ın **10/kullanıcı**
sınırına tabi (yeni sınır **icat edilmez**) · NL yolu (*"bunu panoya sabitle"*) 5.1'in
`tur_takip` sınıflandırmasından geçer, **ikinci bir niyet çözücü yazılmaz** ·
`kpi_pin=off` → pano bugünkü davranışta (K5: panel sayısı **artmaz**).
**GERİ AL** `kpi_pin=off` → pano bugünkü davranışında; pin edilmiş KPI'lar **silinmez**,
görünmez olur. K5: panel sayısı **artmaz** (pin bir **katman**, panel değil — PK-1).

### 5.11 · *"Ne zaman grafik ÇİZİLMEZ"*  *(§15.6)*  [bayraksız: deterministik]
**NEDEN** ~50.000 yanıtlık çalışma (arXiv:2411.07451): kullanıcılar grafiği tablodan tercih
ediyor (**%41,7 vs %36,3**) **ama karar-vericiler ve finans profesyonelleri TABLO tercih
ediyor**.
**NE** `viz.recommend()`'e **yeni dallar** (mevcut kararları **bozmaz**): tek skaler + boyut
yok → **cümle** · **≤2 satır VEYA ≤3 kategori** → cümle/KPI kartı · **>20 kategorili
sıralanmamış boyut** → **tablo** · **finans/muhasebe kapsamı** (cube `packs/modul/kpi` ya da
`mizan`/`cari` tabanlı) → **varsayılan tablo+metin**.
**KAPI** `tests/test_viz.py`: dört kural **sınır değerlerinde** (2/3 satır, 20/21 kategori).
⚠ **MIMARI §13 ⟳ işaretli** — görsel dilbilgisi değişiyor.

### 5.12 · İçgörü Paketi  *(§13.1)*  [bayrak: `ui_icgoru_paketi`]
**NE** `viz.recommend()` dönüşü **`VizSpec | list[VizSpec]`** (**geriye uyumlu** — tekil
dönüş her zaman geçerli) + **"neden bu eksende"** ipucu │ frontend: 1-2 sütun ızgara +
**tek görsel olarak birleşik dışa aktarım**
**KAPI** `tests/test_icgoru_paketi.py`: tekil dönüş **kırılmıyor**.
**GERİ AL** `ui_icgoru_paketi=off` → paket açılmaz, tekil kartlar bugünkü hâliyle görünür
(V-5/E-3: bayrak kapalıyken **birebir eski davranış**).

### 5.13 · Hayalet seri + Knowledge Center  *(§6.1, §6.4)*  [bayrak: `ui_knowledge_center`]
**NE**
* (a) **Hayalet seri**: `ContractStore.find_previous(cq_hash)` + **`AskResponse.previous_result`**
  (yeni opsiyonel alan) — `cube_query_hash()` **zaten var**, sıfır yeni motor
* (b) **Knowledge Center'ın KURAL yarısı**: `app/rules.py` — kural YAML'ı okur, 🔴 **`route()`'a
  DEĞİL**, `narration`/`prescribe`'a **"ek bağlam"** olarak girer, **asla SQL'i değiştirmez**
  (ADR-0008 sınırı). VQR/`SynonymOverride` tarafı **zaten var**
* (c) **"Bilgiye kaydet"** *(Plan 2 §7.6)* — cevap kartının alt şeridinden VQR altın-sorgusu;
  **yalnız insan onaylı kayıtlar güven sınıfına girer**
* frontend: `/settings/data` sekmesi (**yeni panel değil**, PK-5)
**KAPI** `tests/test_rules.py`: kural **SQL'i değiştirmiyor** (kaynak taraması + davranış).
**GERİ AL** `ui_knowledge_center=off` → hayalet seri ve bilgi merkezi görünmez; `/ask` cevabı
**değişmez**. Kayıtlı bilgi girdileri **silinmez**.

### 5.13b · **Rapor yapısı**  *(Plan 2 §7.2 — kaçmıştı)*  [bayraksız]
**NE** `report.compose` çıktısı **sabit yapı**: kapak (başlık/tarih/yazar) → **yönetici
özeti** (İçgörü Kartlarının birleşimi) → her kart (grafik+yorum) → **kaynak listesi**;
format **Word/PDF/Excel/zengin sayfa**; 🔴 **PDF'e döküldüğünde bile `contract_id` altta
kalır**.
**KAPI** `tests/test_rapor_yapisi.py`: dört formatta da `contract_id` **var**.

### 5.14 · **Hızlı ↔ Derin anahtarı**  *(Plan 2 §5.3 — kaçmıştı)*  [bayrak: `hizli_derin`]
**NEDEN** Ürünün *"LLM'siz cevap"* tezinin **kullanıcıya verilen kontrolü**. Plan 2'de
tanımlı, roadmap sürüm 1'de **hiç yoktu**.
**NE** backend: `AskRequest.mod: "hizli" | "derin"` — **Hızlı** = yalnız `route()` + VQR
birebir + `/cube`; **LLM yolu kapalı**. **Derin** = tam merdiven + agentic │ sözleşme: aynı
alan │ frontend: soru kutusunun yanında iki konumlu anahtar; **varsayılan Hızlı**, seçim
**thread'e değil SORUYA bağlı**, her mesajda **sıfırlanır**
**KAPI** `tests/test_hizli_derin.py`: `mod="hizli"` iken **LLM çağrısı 0** (telemetri).
**GERİ AL** bayrak `off` → alan yok sayılır, bugünkü davranış birebir.

### 5.15 · **`stats.py` tekilleştirme borcu**  *(Plan 3 §8.4 + §1.4 — kaçmıştı)*  [bayraksız: borç]
**NEDEN** Plan 3 §1.4'ün ölçülmüş borcu: `schedules.detect_anomalies` (`:357-390`) **hâlâ
kendi ortalama/std/z-skorunu satır içi hesaplıyor**, `app.stats`'ı import etmiyor. *"Anomali
işine dokunan her faz bunu tekilleştirmekle yükümlüdür"* — bu deponun **altı kez ölçülmüş**
hastalığı.
**NE** backend: `schedules.detect_anomalies` → `app.stats.z_skorlari` çağırır (kopya
**silinir**); `stats.py`'ye **`trend`** (regresyon eğimi + anlamlılık, **n<5 → yok**) ve
**`ozet`** eklenir; ikisi de **araç kaydına** girer (6.3)
**KAPI** `tests/test_stats_tekil.py`: `schedules.py`'de `**0.5` / `sum(nums)/len(nums)`
**yok** (kaynak taraması).

### 5.16 · Netleştirme **düzeyi** — bir AYAR  [bayrak: `netlestirme_duzeyi`] *(D14, **DEĞİŞTİRİLEREK** kabul)*
**NEDEN** [KANIT §11.2] bunu *"ayrı bir ürün sorusu, karar verilmedi, kayda geçti"* diye
**açık bırakmıştı**. Rakip zemininde karşılığı var: bir satıcıda `Clarification Mode`
**admin tarafından `None → High`** ayarlanabiliyor.
**NE** backend: **`TenantConfig.netlestirme_duzeyi ∈ {kapali, normal, yuksek}`**, varsayılan
**`normal` = bugünkü davranış BİREBİR** │ sözleşme: `explain.assumptions` (**zaten var**) │
frontend: `/settings` — 🔴 **yalnız tenant-admin**
🔴 **ÜÇ SERTLEŞTİRME (dış denetimin önerisini olduğu gibi kabul ETMİYORUM):** *"`kapali`
seçilirse eksik dönem **varsayılanla** cevaplanır"* önerisi, MIMARI'nin avladığı **sessiz-
yanlış sınıfının ta kendisidir**. Kabul şartlarım:
1. Varsayım **`explain.assumptions`'da DEĞİL, cevabın GÖVDESİNDE** görünür
   (*"**Dönem belirtilmedi — bu yıl varsayıldı.**"*), rozet/tooltip değil.
2. Ayar **tenant-admin'e kilitli** ve her değişiklik **`AuditLog`'a ayrı satır**.
3. `kapali` düzeyinde üretilen her cevap **`kanit_sinifi="probabilistik"`** taşır (1.12).
**KAPI** `nl_corpus`'ta **`normal` düzeyinde `CLARIFY:dönem` payı ±0,5 puan SABİT** — §C/3
korunur; diğer düzeyler **ayrı ölçülür ve ayrı raporlanır**.
**SONUÇ** Kullanıcı **kendi risk tercihini** verir — `yol_siniri` (Faz F2) ile **aynı
ailedendir**: sayısal bir güven eşiği değil, **adı konmuş bir yol seçimi**.
**GERİ AL** bayrak yok sayılırsa `normal` — bugünkü davranış birebir.

### 5.17 · ⭐ **Tek ses — `app/soz.py` metin katalogu**  [bayraksız: kök neden] *(sohbet raporu M3/B6)*
> ⚠ **NUMARA NOTU:** sohbet raporu bu maddeye `5.16` önermişti; o numara **zaten
> `netlestirme_duzeyi`nin** (yukarıda). **5.17'ye alındı** — §E.1'in ad-alanı disiplini.

**NEDEN** Kullanıcıya dönen metinlerin **hepsi satır içi f-string**: `ask.py` (`_META_TEXT`,
`_SOSYAL_METIN`, `_PERIOD_TEXT` + ~20 dal) + `eylem.py:296,322` + `contribution.py:328,417`.
**Merkezî katalog YOK.** Ölçüldü @`c4b14d1`:
- 🔴 **Hitap aynı oturumda değişiyor:** `ask.py` **"sen"** (*"istediğini"*, 15 isabet),
  `eylem.py:296` **"siz"** (*"kastettiğinizi"*)
- Aynı cümle **iki ayrı yerde birebir** tekrar: *"Bu soru için güvenilir bir sorgu
  üretemedim."*
- **Jargon sızıntısı:** `contribution.py:328` kullanıcıya *"Bu sonuç yapısal bir
  `cube_query` taşımıyor (Discovery/ham SQL)"* diyor

**Robotikliğin asıl kaynağı METNİN ŞEKLİ:** *"Neyi karşılaştırmak/görmek istediğini
anlayamadım"* bir **form doğrulayıcısıdır**, bir soru değil. Olması gereken: **önce ne
anladığını söyle, sonra sor.**
**NE** backend: `app/soz.py` — **kararlı ID'li tek sözlük** (`metin` + `kind`
(`netlestirme|ret|sosyal|bilgi`) + `hitap`). **Yeni soyutlama değil, VERİ MODÜLÜ** │
sözleşme: `AskResponse.soz: str | None` — 🔴 **`note` YENİDEN KULLANILMAZ**: bugün **DÖRT**
anlam taşıyor (dürüst ret · netleştirme · kırpılma uyarısı · upload bildirimi) **ve kalıcı
`payload_json` geçmişi ona bağlı** │ frontend: `soz ?? note` → **eski kayıtlar AYNEN
çalışır**

**── Metin şekli kuralı: ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR ──**

| Bugün | Olacak |
|---|---|
| *"Hangi dönem için?"* | *"Fire toplamını çıkarabilirim — **hangi dönem?**"* |
| *"…anlayamadım, tanıdığım konu geçmiyor"* | *"Bu soruda tanıdığım bir ölçü yakalayamadım. **Şunlardan biri mi?**"* |
| *"…önceki raporla ilişkilendiremedim"* | *"Bunu üstteki raporla bağlayamadım — **yeni bir soru olarak sorayım mı?**"* |

**NASIL** `0.10b`'nin **ön koşulu olduğu madde budur**: ham kolon adlarıyla beslenen metin
robotikliği **taşır, kaldırmaz**. Sıra **0.10b → 5.17**, tersi değil.
**KAPI** `tests/test_soz_katalogu.py` (yeni): her kayıt (a) **TEK hitap kipinde**,
(b) **ham küp kolon adı içermiyor**, (c) `kind=="netlestirme"` ise **soru işaretiyle
bitiyor**.
⚠ **İLK İŞ — maddenin gerçek maliyeti burada ölçülür:**
```bash
grep -rn "note" backend/tests | grep -iE "anlay|hangi|dönem"   # altın testler note METNİNE assert ediyorsa
```
**SONUÇ** Ürün **tek sesle** konuşur; netleştirme bir form hatası gibi değil, bir **soru**
gibi okunur.
**GERİ AL** `soz` **opsiyonel**; frontend `soz ?? note` → eski istemci **regresyon görmez**.

> ⛔ **KISIT (B8) — bu maddenin sınırı, ve neden sınır:** metinler **DETERMİNİSTİK KALIR.**
> `narration_guard`'ın kendi beyanı (@`c4b14d1`, doğrulandı): *"Sayı **İÇERMEYEN** cümleler
> geçer: bu kapı sayı uydurmasını engeller, **üslubu değil**"* — ve `izinli_degerler(None)
> == []`. Yani `result=None` olan bir **netleştirme turunda guard her rakamsız cümleyi
> KOŞULSUZ geçirir**. Netleştirme metnini LLM'e yazdırmak, bu deponun bugüne kadar hiç
> sahip olmadığı bir hata sınıfını açardı: **RAKAMSIZ UYDURMA** → **EK J / KD-21**.

---

## FAZ 6 · AGENTIC ve ONAYLI YAZMA

> ⚠ **KAPSAM DARALDI (`c527613` — H indi, §A.4).** 6.1 ve 6.2 artık **sıfırdan tasarım
> değil, `app/eylem.py`'nin GENELLEŞTİRİLMESİ**. İnen desen **bu belgenin önerdiğinden
> daha yalın ve daha güvenli** olduğu için **o kazanır**:
>
> 🔴 **DEVRALINAN KURAL — Bölüm II'nin tüm onay tüketicileri buna uyar:**
> *"Öneri **yeni yetki yaratmaz** — onay ucu, kullanıcının **kendi eliyle çağırabileceği**
> ucu çağırır."* Yani **`yan_etki="yazar"` bir araç `tools.KAYIT`'a ASLA girmez**;
> `test_ajan_YAZAMAZ` **kalıcı olarak yeşil kalır**. Plan 3 §13.2'nin `OnayDurumu` durum
> makinesi bu desenin **üstüne** gelir, **yerine** değil.
> Ve *"argümanlar LLM'den gelmez — öneri, konuşmada **zaten doğrulanmış** yapıyı taşır"*
> kuralı **her tüketiciye** genişler (profil onayı · görev onayı · copilot).
>
> **Ön koşul: FAZ 1.1 + 1.1b.** *(1.3 artık ön koşul değil — §A.4.)*

### 6.0 · ⭐ 🔴 **D9 BUGÜN TERS UYGULANMIŞ — «yapılanı geri al»**  [bayrak: `onay_akisi` ile aynı]  *(sürüm 8 — YENİ)*

> 🔴 **Bu, belgedeki HİÇBİR maddenin taşımadığı bir türdür: *yeni iş değil, İNMİŞ İŞİN
> GERİ ALINMASI*.** Ayrı madde olması şart — 6.1'in gövdesine gömülürse uygulayıcı bunu
> bir **ekleme** sanır ve `D9` hiç inmez.

**NEDEN** `D9` şunu hükme bağlıyor: *"kapsam **içi** ve **geri alınabilir** bir eylem
**İSTEMSİZ** koşar; varsayılan **SINIR**'dır, **istem** değil."* Ama yürüyen planın `H`
fazı (`c527613`) **her yazmaya istem** desenini uyguladı — yani tam olarak `D9`'un
*"ölçülmüş bir hata"* dediği şey. Ölçüldü @`8f87e40`:

| Eylem | `geri_alinabilir` | D9'un hükmü | **Bugünkü kod** |
|---|---|---|---|
| `pano.ekle` | **`True`** (soft-delete, ADR-0019) · kullanıcının **kendi** panosu | **istemsiz koşmalı** | 🔴 **her zaman istem üretiyor** (`app/eylem.py`) |
| `tercih.kaydet` | **`True`** · tek uçla silinir | **istemsiz koşmalı** | 🔴 **her zaman istem üretiyor** |
| `zamanla.olustur` | **`False`** · dışarıya e-posta çıkar | **senkron istem** ✅ | ✅ doğru |

**NE** backend: `eylem.degerlendir` **istem üretmeden önce** `D9` sınamasını yapar —
`geri_alinabilir=True` **ve** eylem **kapsam içindeyse** (kullanıcının kendi yetkisiyle,
kendi nesnesine) doğrudan çalıştırılır ve cevaba **"yapıldı" makbuzu** iliştirilir.
│ sözleşme: `AskResponse.eylem_sonucu` (yeni — *yapıldı* bildirimi; `eylem_onerisi` ile
**aynı anda dolamaz**) │ frontend: onay kartı yerine **geri-al bağlantılı bilgi satırı**.

**NASIL** Yeni modül **yazılmaz**: `app/eylem.py`'nin `EylemBeyani.geri_alinabilir` alanı
**zaten var** ve karar için yeterli. Eksik olan **kapsam** yordayıcısı — `authorize.can()`
+ nesne sahipliği (pano `user_id`, tercih `user_id`) ile **var olan** kontrollerden türer.

**KAPI** `tests/test_eylem_onayi.py` **GÜNCELLENİR** (bu bir gerileme değil, **kasıtlı
davranış değişikliği**; eski beklentiler yeni kurala göre yeniden yazılır):
`pano.ekle` ve `tercih.kaydet` **istem ÜRETMEZ ve iş YAPILIR** · `zamanla.olustur`
**istem üretir** · **her iki yol da audit'e ayrı satır yazar** · 🔴 **istem sayısı/tur
telemetriye yazılır ve `0.19`'un paydasında ARTARSA KIRMIZI**.

**SONUÇ** Geri alınabilir işlerde tur başına **bir tıklama eksilir**; `D9`'un *"%93
yorgunluk"* deseni kapanır. **Yazma yüzeyi BÜYÜMEZ** — `test_ajan_YAZAMAZ` yeşil kalır,
çünkü ajan hâlâ yazma aracı **çağırmıyor**; değişen şey yalnız **kullanıcının kendi
eyleminin kaç tıkla tamamlandığı**.

**GERİ AL** `onay_akisi=off` → bugünkü *"her yazmaya istem"* davranışına **birebir** dönülür
(eski testler bayrak-kapalı dalda korunur). ⚠ Bu maddenin geri alınması, `c527613`'ün
davranışını geri getirir — **kayıp yok**.

---

### 6.1 · ⭐ Onay akışı  *(Plan 3 §13.2)*  [bayrak: `onay_akisi`]
**NEDEN** MIMARI §4-2/3 read-only değişmezi + `tools.py:108-116`'nın **bilinçli** kararı;
ama `MIMARI.md:1072` bunu *"**gerçek boşluk** — eksik olan **onay akışı**"* diye kaydetmiş.
⟳ tablosunda **§4 ve §11 ikisi de işaretli**.
**NE**
* backend: **`app/onay_akisi.py`** — **TEK modül**. `OnayDurumu`:
  **`taslak → onay_bekliyor → onaylandı | reddedildi | geri_alindi`**
* **Beş tüketici** *(Plan 3'ün üçü + roadmap'in ikisi — denetim bulgusu)*: yazma araçları
  (6.2) · **ŞirketProfili onayı** (II-F.8) · **görev/taahhüt onayı** (II-F.6) · sistem
  copilot (II-H.3) · operatör
* sözleşme: **`OnayTalebi`** — `arac` · `argumanlar` · `kaynak` · `risk` ·
  **`son_gecerlilik`** · `geri_alma_fonksiyonu_ref`
* frontend: `OperatorOnayKarti` (`ui_operator`) — **kartın şeridi**, yeni panel değil
**NASIL — araştırmadan gelen ÜÇ zorunlu parça** (*"onay bir buton değildir"*; EU AI Act +
NIST AI RMF **gösterilebilir, ölçülebilir** insan gözetimi istiyor) [KANIT §2.6]:
1. **Onay kapsamı bir NESNEDİR** — hangi araç, hangi argümanlar, hangi kaynak: *"evet"*in
   sınırı **yazılı**
2. **Riske göre yönlendirme** — `risk="geri_alinamaz"` → **senkron onay**; `risk="orta"` →
   **kuyruk**
3. **SÜRE AŞIMI — `son_gecerlilik = now + 30 dk`** (varsayılan; `TenantConfig`'te ayarlanır);
   süresi geçmiş onayla çalıştırma **reddedilir**
🔴 **DÖRDÜNCÜ PARÇA — DENETİM DÜZELTMESİ (D9): *"her yazmaya onay"* ÖLÇÜLMÜŞ BİR HATADIR.**
Anthropic telemetrisi: **kullanıcılar izin isteklerinin ~%93'ünü onaylıyor**; *"bir kullanıcı
ne kadar çok onay görürse her birine o kadar az dikkat eder; zamanla denetimi belirgin
biçimde **gevşer**"*. **Onay yorgunluğu ölçülmüş bir olgu.** OS düzeyi izolasyon istemleri
**%84 azaltmış**. Tasarım kuralı: ***"izolasyon gücünü kullanıcının gözetim kapasitesine göre
ayarla"*** — teknik olmayan kullanıcı **daha çok diyalog** değil, **daha sert sınır** ister.
→ Sürüm 2'nin kapısı (*"onaysız **hiçbir** yazma"*) tam olarak **%93'ü üreten desendi**.
**Düzeltilmiş tasarım:**
1. **VARSAYILAN SINIR, İSTEM DEĞİL.** Yazma hedefleri **kapsamla** sınırlanır (kendi panosu ·
   kendi zamanlaması · kendi tenant'ı). Bu sınır içindeki **geri alınabilir** eylem
   **İSTEMSİZ** koşar ve **makbuza yazılır** — `eylem.py`'nin `geri_alinabilir` alanı
   **zaten var**.
2. **İstem yalnız `geri_alinamaz` + kapsam dışı** için. (`zamanla.olustur` bugün
   `geri_alinabilir=False` → istem **oraya** ayrılır.)
3. **`OnayTalebi`'nin ŞEKLİ MCP `elicitation`'a hizalanır** — aynı şekil FAZ 4.5'in MCP
   yüzeyini **bedavaya onay-yetenekli** yapar; ayrı şema yazmak onu **ikinci kez** yazmak
   olur. ⚠ Spec'in normatif kuralı: *"form modu **parola/API anahtarı/token/ödeme bilgisi**
   istemekte kullanılmamalıdır"* — `OnayTalebi`'nin alanları buna uyar.
   🔴 **`[DOĞRULANMADI]` — MCP spec sürümü ÇELİŞKİLİ:** dış denetim *"9 Aralık 2025 Linux
   Foundation · kararlı revizyon 2026-07-28"* diyor; [KANIT §2.7] *"Agentic AI Foundation ·
   2025-11-25"* diyor. **Hizalamadan ÖNCE spec sürümü doğrulanır** (EK F).

**KAPI (D9 ile güncellendi)** `tests/test_onay_akisi.py`:
onaysız **KAPSAM DIŞI** yazma **imkânsız** · `geri_alinamaz` eylem **HER ZAMAN** senkron
istem · **her onay ayrı audit satırı** · süresi geçmiş onay **reddediliyor** ·
🔴 **istem sayısı/tur telemetriye yazılır ve ARTARSA KIRMIZI** (yorgunluk göstergesi).
**NASIL** **Modül tek, tüketici üç** (Plan 3 §13.2): `app/onay_akisi.py` yazılır ve
yürüyen planın H'si onun **ilk tüketicisi** olur. 🔴 **H'nin dersi korunur:** yazma aracı
**araç kaydına GİRMEZ** — öneri, kullanıcının kendi eliyle çağırabileceği ucu çağırır;
*"güvenlik imzadan değil, yetki yüzeyinin genişlememesinden geliyor."* Araştırmadan gelen
üç zorunlu parça: onay **kapsamı bir nesnedir** · **riske göre yönlendirme** · **SÜRE AŞIMI**.
**KAPI (ek — yukarıdaki D9 bloğuyla BİRLİKTE okunur)** `tests/test_onay_akisi.py`:
🔴 **süresi geçmiş onayla çalıştırma REDDEDİLİR** (30 dk, EK D) · onay kapsamı dışında bir
argümanla çağrı **reddedilir** (*"evet"in sınırı yazılı*) · `test_ajan_YAZAMAZ` **yeşil
kalır** (araç kaydı büyümedi).
> ⚠ **Sürüm 8 düzeltmesi:** bu satır önceden *"onaysız **hiçbir** yazma"* diyordu ve
> **yukarıdaki D9 bloğuyla doğrudan çelişiyordu** (*"onaysız **KAPSAM DIŞI** yazma"*).
> D9'un kendi gerekçesi açık: *"«onaysız hiçbir yazma» tam olarak %93 yorgunluk üreten
> desendi."* İki blok arasında kalan bir uygulayıcı **yanlış olanı okuyup bugünkü davranışı
> doğru sanabilirdi** → çelişki kaldırıldı, **D9 bloğu tek otoritedir**.
**SONUÇ** Ajan *"bunu takip et"* diyebilir; **kapsam dışı hiçbir şey onaysız olmaz** —
kapsam içi ve geri alınabilir olan ise **istem üretmeden** koşar (D9).
**GERİ AL** `onay_akisi=off` → 6.2 de kapalı (yazma araçları kayda **girmez**).

### 6.2 · Yazma araçları  *(§15.4)*  [bayrak: `yazma_araclari`]
**NE** `app/yazma_araclari.py` — **`yan_etki="yazar"` ile kaydedilen İLK araç sınıfı**
(bugün **0**). Her araç **`geri_alma_fonksiyonu_ref`** taşır; 🔴 **geri alınamaz eylemler
(ERP'ye kalıcı kayıt) AÇIKÇA "geri alınamaz" işaretlenir, kullanıcıya GİZLENMEZ**.
İlk üç: `schedules.create` · `dashboards.create` · `measures.approve`.
**KAPI** `tests/test_arac_kaydi.py::test_ajan_YAZAMAZ` **ters çevrilir**: yazma aracı
kayıtta **var** ama **yalnız `onay_akisi` üzerinden** çağrılabiliyor.
**GERİ AL** `yazma_araclari=off` → yazma aracı **kayda hiç girmez** — yani geri alma
*"kapatmak"* değil, **hiç açmamaktır**. 🔴 **H'nin dersi burada değişmez olarak korunuyor:**
*"güvenlik imzadan değil, **yetki yüzeyinin genişlememesinden** geliyor"*; `test_ajan_YAZAMAZ`
bayrak kapalıyken **yeşil kalmalıdır**.

### 6.3 · Araç kaydı genişlemesi  [bayraksız]
**NE**
* **5 "zaten var ama kayıtsız"** araç — **doğrulandı**, beşi de bugünkü 15'te **yok**:
  `prescribe.recete` · `statements.resolve` · `kpi.resolve_series` · `report.compose` ·
  `schedules.uyari_nedeni` → **sıfır yeni kod**
* **+3 port**: `get_sample`/`get_distinct` (**LIMIT'li yeni sarmalayıcı — yeni kod**) ·
  `explain_plan` · `recall`
* **+`narration_guard.dogrula`** (kapı, `makbuz=None`)
* **+2** (5.15): `stats.trend` · `stats.ozet`
* 🔴 **Bölüm II motorları** *(denetim bulgusu — hiçbir maddede yazılı değildi)*:
  `forecast.tahmin_et` · `driver_graph.calistir` · `cohort.kohort_sorgusu` ·
  `causal_graph.genislet` · `decision.matris_hesapla` · `decision.kirilma_noktasi` ·
  `hafiza.yazilabilir_mi` · `certification.durum` · `terfi.aday_bul` · `brifing.olustur` ·
  `hakem.uzlas` (II-H) → **her biri kendi maddesinde `tools.KAYIT`'a girer**
* 🔴 **`Arac.ozet` dört bileşenli formata genişler** *(Plan 3 §8.2 — kaçmıştı)*:
  `[Ne yapar] + [Hangi veriye erişir] + [Ne zaman kullanılır] + [NE ZAMAN KULLANILMAZ]` —
  Snowflake'in adlandırdığı **yanlış-araç-seçimi karşı önlemi**
**Sayım:** 15 (bugün) + 5 (kayıtsız) + 3 (port) + 1 (guard) + 2 (stats) = **26 @v1**;
+11 (Bölüm II) = **37 @v3**.
**KAPI** `tests/test_arac_kaydi.py`: her aracın `ozet`'i **dört bileşeni** taşıyor.

### 6.4 · Planlayıcı sertleştirmesi  *(§8.1, §8.6-8.10)*  [bayraksız]
**NE**
* **Plan DONDURMA** *(§8.1 — kaçmıştı)*: `PlanTaslagi` **başlamadan önce** dondurulur;
  doğrulama düşerse **yalnız o noktadan** yeniden planlanır (tüm plan değil). Güvenlik
  gerekçesi: **kontrol-akışı bütünlüğü** — plan, **güvenilmeyen araç çıktısı bağlama
  girmeden** donar
* **4 katmanlı adım doğrulama** *(§8.6)*: `satır == 0` · **`null_orani > %90`** ·
  **büyüklük mertebesi sapması ≥ 100×** (medyana göre) · şema uyumsuzluğu
* **Plan kontrol listesi** *(§8.7)*: `Kosum`'a `adimlar_toplam`/`adimlar_tamam`
* **Hata sınıflandırma** *(§8.8)*: **aynı hata imzası 2. kez → strateji değiştir**
* **Refleks yayı** *(§8.10)* `[TEYİT BEKLİYOR: 4.17]`: `InteractionLog.yol_tipi ∈
  {refleks, derin}`
* **Bütçe `token` ekseni** *(§8.9)*: bugün ölçülemediği için sınırsız; **FAZ 8.1'den sonra
  yalnız DEĞER değişir**, kod değil
**KAPI** `tests/test_orkestrator.py` genişletilir: plan dondurulduktan sonra araç çıktısı
planı **değiştiremiyor**; dört doğrulama **sınır değerlerinde**.
**NOT** MIMARI §11.5 korunur: **bu modül bir ReAct döngüsü DEĞİLDİR**.

### 6.5 · Public API + async job + embed  *(§15.2, §15.3)*  [bayrak: `public_api` · `embed`]
**NE** **Yeni kuyruk KURULMAZ** — `AskJob` genellenir; **idempotency**:
`(client_idempotency_key, tenant_id)` üstünde **BENZERSİZ KISIT**. **`EmbedToken`**
(`tenant_id` · **`scope_json`** = `ModelPermission` şeması · **`kota`** · `son_kullanim` ·
**`iptal_edildi`**) → JWT claim → **`always_filter` + session property** (1.1).
🔴 **Looker'ın imzalı-URL modeli DEĞİL** *(Plan 3 hükmü)*. **Beyaz etiket** (logo/renk/domain)
`TenantConfig`'te.
**Frontend:** `api-only` (gerekçe: **dış-geliştirici yüzeyi**) — **embed paketi** ve
**portföy ekranı** 7.3'te.

> 🔴 **P0 RİSK — DENETİM BULGUSU (D13b): motor-RLS gömülü panoları KAPSAMIYOR olabilir.**
> Wren'in kendi belgesi RLS'in *asking · charts · previews · API · spreadsheets*'i
> kapsadığını, **dashboard'a gömülü grafikleri kapsamadığını** söylüyor. Bu madde
> (`embed` + `EmbedToken`) **1.1'in motor-RLS'ine yaslanıyor** — yaslanırsa **gömülü pano
> çapraz-tenant veri sızdırabilir**.
> 🔴 **ZORUNLU KAPI:** `tests/test_embed_rls.py` — gömülü yüzeyde **tenant A token'ıyla
> tenant B verisi 0 satır**. Motor kapsamıyorsa `always_filter` + session property
> **embed yolunda AYRICA** uygulanır.
> **`1.1`'in `on` olması `6.5`'i güvenli YAPMAZ.**
> ⚠ `[DOĞRULANMADI]` — belge atfı var, **bu oturumda doğrulanmadı**; 6.5 başlamadan önce
> Wren dokümanı ve davranış **birlikte** sınanır.
**KAPI** `tests/test_public_api.py`: aynı `client_idempotency_key` ile iki çağrı
**tek iş** üretir (benzersiz kısıt) · `EmbedToken` **kapsamı dışında** bir cube isteyen
gömülü çağrı **reddedilir** · `iptal_edildi` token **anında** reddedilir · kota aşımı
**429** ve makbuzda görünür.
🔴 **P0 ÖN KOŞUL — `[DOĞRULANMADI]`:** *"motor RLS'i gömülü pano grafiklerini kapsamıyor"*
iddiası bu madde başlamadan **Wren dokümanı + davranış birlikte** sınanır (EK L.4).
Kapsamıyorsa `embed` bayrağı **açılmaz**; `always_filter` tek başına yeterli sayılmaz.
**GERİ AL** `public_api=off` → dış uç yok · `embed=off` → gömme yok; **ikisi ayrı bayrak**,
ayrı geri alma. Verilmiş `EmbedToken`'lar `iptal_edildi` ile **anında** düşer.
🔴 **Wren RLS'in gömülü grafikleri kapsamadığı doğrulanırsa `embed` AÇILMAZ** —
`always_filter` tek başına yeterli sayılmaz (EK L.4).

### 6.6 · Mesajlaşma kimlik eşlemesi  *(§15.5)*  [bayrak: `kanal_kimlik`]
**NEDEN** Araştırmanın **en net uyarısı**: hiçbir satıcı sağlam bir *"sohbet-kimliği →
BI-kimliği → RLS"* eşlemesi yayımlamamış; **Microsoft'un kendi belgesi Slack e-postasının
Teams hesabına güvenilir eşlenemeyeceğini** söylüyor `[DOĞRULANMADI — kaynak EK F'ye]`.
**NE** **`KanalKimlikEslemesi`** (`kanal` ∈ `slack|teams|whatsapp` · `kanal_kullanici_id` ·
`dima_user_id` · 🔴 **`onaylayan_admin_id` ZORUNLU, e-postadan ÇIKARILAMAZ**).
**KAPI** `tests/test_kanal_kimlik.py`: **eşlemesi olmayan kanal kullanıcısının sorusuna
YANIT VERİLMEZ**.

---

## FAZ 7 · ARAYÜZ (UI/UX planının uygulanması)

> **Absorbe edilen:** Plan 2'nin tamamı + [KANIT §15, §17]. **Terk edilen dal
> birleştirilmiyor** — 28 yeni dosya (**3.968 satır**, denetim ölçümü) + 40 değişiklik
> `wren-bağımsız` üstünde **yeniden üretilir**, **dört hatası düzeltilerek**.
**GERİ AL** `kanal_kimlik=off` → kanal kimlik eşlemesi yok, bildirimler bugünkü adresleme ile
gider. Eşleme kayıtları **silinmez**.

### 7.0 · Planın **kendi 5 iç boşluğu** kapatılır  [bayraksız: plan onarımı]

| # | Boşluk | Çözüm |
|---|---|---|
| 1 | **§7 (Rapor & Panolar) ve §11 (Güven & Yönetişim) HİÇBİR FAZA ATANMAMIŞ** — 16 madde | §11 → **FAZ 1** (1.5-1.8) + **7.8**; §7 → **FAZ 5.9/5.13b + 7.3** |
| 2 | **Faz H, Plan 2'nin faz listesinde yok** | **II-H** |
| 3 | **~49 yüzeyin yalnız 4'ünün bayrak adı var** | **EK E her yüzeyin bayrağını YAZAR** (40 benzersiz `ui_*`), hepsi `FLAG_REGISTRY` + `features.yml`'ye |
| 4 | **Token göçü bayraklanamıyor** ama *"bayraksız yüzey birleştirilmez"* | **Görsel regresyon kapısı** (375/768/1024 duman testi + `no-arbitrary-tailwind` lint) bayrağın **yerine geçer** ve **açıkça beyan edilir**. Göç usulü: token'lar **önce eklenir** → **kullanım-yeri-başına küçük commit** → eskiler **sıfır kullanımda silinir** → **bu dal diğerlerinden ÖNCE birleşir** |
| 5 | `/decisions` ve `/settings` **gerekçeli istisnalar** (PK-5, PK-6) | Gerekçeler **aynen taşınır** |
**KAPI** `tests/test_yol_haritasi_butunlugu.py` (**D5'in kapısı**): Plan 2'nin
**16 fazsız maddesinin** her biri bu belgede bir **madde numarasına** bağlı · her yüzey bir
**bayrak adı** taşıyor (EK E) · `PK-n`/`KD-n`/`A11Y-n` atıflarının **hepsi tanımlı** ·
taşınan her madde bir **kütük** bırakmış. 🔴 *Bu, planın kendi boşluklarını kapatan maddenin
kendi kapısıdır — kapısız bırakılırsa boşluklar sessizce geri döner.*
### 7.1 · ⭐ `ui_*` bayrakları **backend'e kaydedilir**  [bayraksız: değişmez]
**NEDEN** Terk edilen dalda **12 bayrak** (11'i `uiFlags.ts`'de, 1'i `proxy.ts` env);
`FLAG_REGISTRY`'de `ui_*` = **0**. Bugün **ÜÇ paralel sistem**: `useFeature()` ·
`useUiFlag()` · `NEXT_PUBLIC_*`. MIMARI §6.13z/9.11: *"kill-switch yalnız KOD'da varsa
**YARIMDIR**."* [KANIT §15.3]
**NE** Tüm `ui_*` **backend kaydına** girer → **`uiFlags.ts` kaldırılır**; `ui_kayit_akisi`
**env'den de çıkarılır** → **üç sistem TEKE iner**.
**NASIL** Var olan bileşenler **zenginleşir**, yenisi doğmaz (PK-1). Katmanlı makbuzun
üç katmanı **aynı `contract_id`'ye** bağlanır — ikinci bir makbuz kaynağı **açılmaz**.
**KAPI** `tests/test_bayrak_kaydi.py`: frontend'de `useUiFlag`/`NEXT_PUBLIC_UI_` **0
eşleşme**; her `useFeature("ui_…")` çağrısı `FLAG_REGISTRY`'de **var**.
**SONUÇ** Ürünün **ayırt edici yarısı** (makbuz · `source` sözleşmesi · fan-out
sertifikası · toplanabilirlik kapısı) **görünür** olur — [KANIT §13.6]'nın ürün bulgusu:
*"rakiplerin veremediği şeyler bizde görünmez durumda."*
**GERİ AL** Görünürlük eklemesi — davranış değişmez. 🔴 **Katman 3 SİLİNMEZ, yalnız
KATLANIR** (§2.5): tam iz her zaman **açılabilir** kalır.

### 7.2 · Tasarım sistemi  [bayraksız: görsel regresyon kapısı]
**NE** `globals.css` **+194** (denetim ölçümü): accent 50-900 · semantik renkler ·
`--positive/--negative` · `--chart-1..8` · `--text-3xs…2xl` · radius/shadow/opacity ·
`:root[data-theme]` + **tema toggle**.
⚠ **Karanlık mod:** token seti `globals.css:20-28`'de **prefers-color-scheme ile var**, ama
`data-theme` **0**, `.dark` **0**, Tailwind v4 `@custom-variant dark` **0** → **class-tabanlı
katman + toggle ikisi de yazılacak** (sürüm 1 *"yalnız toggle eksik"* diyordu — eksik teşhis).
**Token göçü:** **284 keyfi `text-[Npx]` / 31 dosya** (mainline ölçümü; terk edilen dalda 345/44).
**DS kuralları:** yeni üçüncü-parti kütüphane **KURULMAZ** · 4× `window.prompt()`
(`DashboardsPanel:29,41` · `ReportCard:126` · `AnalysisCanvas:213`) → **gerçek modal** ·
**`lucide-react`** (kurulu, kullanılmıyor) işlevsel ikonlar için · **emoji yalnız dekoratif**
· sertifika ikonları `currentColor` · **`@dnd-kit` zaten kurulu**.
**KAPI** `no-arbitrary-tailwind.mjs` lint + **V-2** (375/768/1024 duman testi).

### 7.3 · Rotalar, bileşenler, **çekirdek deneyim**
**6 yeni rota:** `/register` · `/invite/[token]` · `/kurulum` · `/settings` (**çekmeceden
TAM SAYFAYA terfi**, PK-5) · `/karar-memosu` · `/decisions` (**aranabilir arşiv**, PK-6).
Hedef **4 → ~10-12** rota.

🔴 **Denetimin bulduğu ve sürüm 1'de OLMAYAN çekirdek maddeler:**

| # | Madde | Ne |
|---|---|---|
| **a** | **Cevap kartının KANONİK ANATOMİSİ** *(Plan 2 §5.1)* | Sabit **10 katmanlı sıra** + 🔴 **ZORUNLU üç şeritli İçgörü Kartı** (`NE OLUYOR / NEDEN / NE YAPMALI`); veri yoksa *"yorum için veri yetersiz"* — **asla sayı-tekrarı, asla uydurma**. Konuşma cevabında **SONUÇ bloğu yok** (1-şerit kuralı) |
| **b** | **Landing / boş-durum** *(§3.3)* | `CaretInput`'a **placeholder** (bugün yok) + **departman-gruplu, katalogdan OTOMATİK üretilen** örnek soru kartları + kurulum bitmemişse **onboarding** (ikisi asla aynı anda) |
| **c** | **Capability Explorer** *(§3.11/§4.3)* | MDL + `MetricDefinition`'dan otomatik üretilen, **komut paletinden aranabilir** yetenek kataloğu — paletin **arama motoru** budur |
| **d** | **Kök Neden ön-skorlama** *(§5.4)* | Her aday boyut için **ucuz, deterministik varyans/aykırılık skoru** (`drill.flag_outliers` z-skoru uzantısı, **sıfır-LLM**) — **PK-13'ün (sinyal ağırlıklandırma) tüm kaynağı**; koyu/soluk ayrımının **neyi ölçtüğü** |
| **e** | **Her grafik tipinden drill** *(§5.4)* | `ResultView.tsx:326`'nın facet/scatter/heatmap kısıtı **kaldırılır**; her tıklanabilir öge `{dimension, value}` çapası üretir. Backend **zaten dimension-agnostic** → **sıfır backend işi** |
| **f** | **Yol diyagramlı düğüm notu** *(§5.4)* | Not, **o ana kadar izlenen YOLUN mini diyagramıyla** reply-to-card'a iliştirilir; *"genişleme yeniden-köklenme değil **BÜYÜMEDİR**"* (dbt Explorer deseni **bilinçle reddedilir**); kök→düğüm yolu **vurgulanır**; kenar açıklaması **tıklamayla** |
| **g** | **Kurulum sonu = anında değer** *(§4.2/5)* | 2-3 grafik kartı + Şirket Portresi + **otomatik açılış panosu (4-6 widget)** aynı anda; landing'e **hiç düşülmez** |
| **h** | **E-posta doğrulama + şifre sıfırlama + davet uçları** *(§4.1)* | `/register`·`/invite` arkasındaki **backend uçları** (sürüm 1'de rota vardı, uç yoktu → mock riski, 7.9) |
| **i** | **Analiz Tuvali** *(§7.1)* | İki sabit düğme (Rapor oluştur / Panoya aktar) **her zaman görünür**; kart sırası = rapor sırası **beyan edilir** |
| **j** | **Pano genişlemesi** *(§7.3)* | Widget eklerken **iki soru** (güncelleme sıklığı + eşik uyarısı = Pulse girişi) · **global filtre şeridi + filtre durumunun paylaşılabilir bağlantıya gömülmesi** · widget veri noktasından **Kök Neden Haritası** (PK-10) |
| **k** | 🔴 **Sarı drift uyarı bandı** *(§7.3)* | Metrik tanımı değişince **etkilenen widget üstünde**; *"yeniden doğrula"* eski/yeni tanımla sonucu kıyaslar. **B8'in TEK kullanıcı-görünür yüzeyi** — FAZ 1.5/II-G.4 arkasını kuruyor, önü yoktu |
| **l** | **5 grafik tipi** *(§15.1)* | **Sankey** (veri kaynağı `SurecAdimi`, II-F.1) · **Pareto** (`stats.py`'ye tek kümülatif-% fonksiyonu) · **Bubble** (mevcut scatter'ın 3. boyutu) · **Gauge** (`MetricTarget`'ın görseli, 2.5) · **Harita** (il/ilçe sınır verisi + koordinat eşleme — **yeni veri gereksinimi**). Her biri `viz.recommend()`'e **açık, test edilebilir seçim kuralı** |
| **m** | **Embed paketi + portföy ekranı** *(§13.2/§13.5)* | iframe/web-component; **portföy**: muhasebeci/holding — tüm müşteriler tek ekran, **toplu kırmızı-uyarı listesi** (2.3'ün `portfoy` kapsamının ekranı) |

**KAPI** her madde kendi bayrağıyla (EK E) + **V-1** (uç tüketimi) + **V-5** (bayrak-kapalı
regresyon).

### 7.4 · Panel/katman disiplini — **24 kural**  [bayraksız: K5]
**NE** **Tam liste EK H'de** (sürüm 1'de yalnız 8'i yazılıydı; Plan 2 silinince kalan 16
sayılamaz hâle gelirdi). ⚠ **PK-23 (yeni):** Bölüm II'nin `WhatIfPaneli` ve
`DuyarlilikPaneli`'si **iki gerçek paneldir** → tavan v1'de **13**, v2'de **15**;
`test_panel_sayisi` **sürüme göre** kilitlenir.
🔴 **ÖNCE TANIM, SONRA SAYI** (§C/11): kapı **export** sayar (`export default` **dahil**),
dosya değil. *Sürüm 3'te bu sayı belgede **beş yerde** geçiyordu ve **üç farklı değer**
taşıyordu (11 · 11 · 12 · 11 · 11); ölçüm hepsini **13/15**'e indirdi. Tanımsız bir sayının
beş kopyası, beş ayrı bayatlama yüzeyidir.*
**KAPI** **K5** (`tests/test_panel_sayisi.py`) — §C/11'in **tanımıyla**: `export`
sayımı, `export default` **dahil**; v1 tavanı **13**, v2+ **15**. Ek olarak
`tests/test_panel_kurallari.py`: PK-1 (*yeni özellik yeni panel doğurmaz*) ve **PK-24**
(*yüzey kırpması yasağı*) **kaynak taramasıyla** kontrol edilir.

### 7.5 · a11y — **10 kural**  [bayraksız: kapı]
**NE** **Tam liste EK I'de** (sürüm 1'de 7'si yazılıydı).
**KAPI** **V-2 + a11y taraması** (`tests/test_a11y.py`): her etkileşimli öge
`aria-*` taşır · modallerde **focus trap** · **`window.prompt()` birincil yüzey DEĞİL**
(bugün **4 kullanım** var) · 🔴 **renk tek kanal olamaz** — *"soluk ama tıklanabilir"* ile
*"devre dışı"* **asla aynı token'ı paylaşmaz** (K6'nın doğrudan uygulaması).

### 7.6 · Responsive — **3 kademe**  [bayraksız: V-2]
Masaüstü **>1024** · tablet **768-1024** (sekmeli) · mobil **<768** (tek sütun + alt sekme;
rail alt çubuğa dönüşür; SWOT 2×2 → tek sütun). **Responsive GÜN-1 gereksinimidir.**
**KAPI** **V-2 duman testi: 375 / 768 / 1024** — üç kırılımda da yatay taşma
**yok** ve birincil eylem **erişilebilir**. 🔴 **Gün-1 gereksinimi olduğu için bu kapı
FAZ 7'nin sonunda değil, her frontend maddesinde koşar** — sonradan eklenen responsive,
yeniden yazım demektir.
### 7.7 · `admin_app` tüketicileri + **üç yeni panel içeriği**  [bayrak: `ui_settings_tam_sayfa`]
**NEDEN** **V-1'in kendi beyanı**: *"`admin_app`'in 13 router'ı için bu denetim **BUGÜN
KIRMIZI OLMALI** — Faz D bitince yeşile döner."* `grep sadmin src/` → **0**. `getMe()` **tek
yerde** ve yalnız `permissions` okunuyor — **e-posta/rol/isim hiç render edilmiyor**.
**NE** `/settings` **8 sekme** → 13 router'ın tüketicisi. Ve üç sekmenin **içeriği**
*(denetim bulgusu — sürüm 1'de yalnız bayrak adı vardı)*:
* **Sinonim yönetimi** *(§12.2)* — `GET /sadmin/synonyms/candidates`, **tek tıkla onay**
* 🔴 **"Dima kendini nasıl geliştiriyor"** *(§12.4)* — aylık trend: soru sayısı ·
  **LLM-free oranı** · terfi sayısı · maliyet; aylık PDF. **`GET /sadmin/interactions/
  route-distribution`'ın TEK tüketicisi** → FAZ 0'ın yetim envanteri **böyle kapanır**
* **Sağlık/teşhis skoru** *(§12.5)* — eksik tanım · kopuk kaynak · **sahipsiz metrik**
  (3.1/3.2'nin ölçüm yüzeyi) · bayat bilgi · yavaş sorgu; **her madde tıklanabilir**
**KAPI** 🔴 **V-1 BUGÜN KIRMIZI OLMALI ve bu madde onu YEŞİLE ÇEVİRİR** —
`admin_app`'in **13 router'ı** için `test_uc_yetim_degil` yeşile döner. Ek: `getMe()`'nin
**e-posta/rol/isim** alanları render edilir (K2'nin **erişilebilirlik** boyutu — yalnız
kaynakta geçmesi yetmez) · `ui_settings_tam_sayfa=off` → eski çekmece davranışı **birebir**
(V-5/E-3) · K5: `/settings` bir **rota**, yeni panel **değil** (PK-5'in gerekçeli istisnası).
**GERİ AL** `ui_settings_tam_sayfa=off` → eski çekmece davranışı **birebir** (V-5/E-3).
⚠ **Ama V-1 kırmızısı geri döner** — yani geri alma **bilinen bir yetim kümeyi** yeniden
açar ve bu, kapının **beyan edilmiş kırmızısı** olarak görünür kalır (0.14/K1 disiplini).

### 7.8 · ⭐ **Ayırt edicileri görünür kıl** + güven yüzeyleri  [bayrak: `ui_kanit_gorunurlugu`]
**NEDEN** Dışarıdan gelen özellik notu ürünün **ayırt edici yarısını hiç saymadı** — çünkü
**görünmüyor**: makbuz · `source` rozeti · **fan-out sertifikası** · **toplanabilirlik
kapısı** · netleştirme = birinci sınıf cevap. **Bir ÜRÜN BULGUSU.** [KANIT §13.6]
**NE**
* 🔴 **K1 — MAKBUZ BUGÜN KATMANLI DEĞİL, ve D3 "zaten yapılmış" diye YANLIŞ KAPATILDI**
  *(D11)*. **Doğrulandı:** `grep -rn "<details\|<summary" src/` → **tüm frontend'de 0**.
  Bugün `?` toggle'ı **üç düz listeyi aynı görsel seviyede** açıyor (`ReportCard.tsx:622·646
  ·678`), hepsi `font-mono text-[11px]`; SQL **ayrı** toggle (`:901`), `contract_id` **ayrı**
  modal, ve `agent_run.steps[].receipt` (`types.ts:74`) **hiç okunmuyor**. → **Üç kopuk
  yüzey, sıfır kademe.** Spesifikasyon:
  * **Katman 1 (varsayılan, TEK SATIR):** *"deterministik küp · 2 adım · 34 ms"* + yol rozeti
  * **Katman 2 (bir tık):** düz Türkçe *"ne yaptım"* — **hangi cube · hangi ölçü · hangi
    filtre · hangi dönem** (`cube_query`'den **deterministik olarak** üretilebilir;
    kategorinin gittiği yer bu — Databricks Genie *"Inspect"* join koşullarını,
    agregasyonları ve filtre değerlerini **cevabın içinde** gösteriyor, *"SQL göster"*
    toggle'ının altına **gömmüyor**)
  * **Katman 3 (ikinci tık):** bugünkü tam iz + **`agent_run.steps[].receipt` TIKLANABİLİR**
    (0.8'in yetim alanı **burada kapanır**) + SQL + `contract_id`
  * **KAPI:** tek kapsayıcı; `<details>` sayısı **≥1**; **ayrıntı SİLİNMEZ, yalnız katlanır**
  ⚠ **Kademelendirme zorunlu, çünkü ölçülmüş:** *"daha uzun açıklamalar, **doğruluğu
  artırmadan** kullanıcı güvenini artırıyor"* (Steyvers ve ark., *Nature Machine
  Intelligence* 7:221-231, 2025). Varsayılan **kısa**, ayrıntı **talep üzerine**.
* 🔴 **K2 — MADALYA KALDIRILIR** *(D10 — bu bir ÇIKARMA kalemidir)*. **Doğrulandı ve
  sanılandan kötü: YÜZDE olarak basılıyor.** `ChatPanel.tsx:16-27` `confidenceBadge`
  **🥇/🥈/🥉** + `Yüksek güven (${pct}%)` üretiyor; kaynağı `answer.py:84-92 _EXPLAIN_PATH`
  — **sabit kodlu bir YOL ETİKETİ** (`cube→1.0 · vqr→0.95 · cube+llm→0.85 · rule→None`),
  **hesaplanmış değil**. Yani kullanıcı **"Yüksek güven (100%)"** görüyor ve arkasında
  **hiçbir ölçüm yok** — yalnız *"bu cevap `route()`'tan geldi"*.
  🔴 **MIMARI §9'un kendi yasağının üründe canlı ihlali:** *"kalibre edilmediği sürece o sayı
  bir güven değil bir **SÜSTÜR**."*
  **Dış kanıt iki bağımsız çalışma:** kalibre edilmemiş güven **uygun güveni bozar ve karar
  etkinliğini düşürür**; **kullanıcılar kalibrasyon bozukluğunu kendi başlarına fark
  edemiyor**; ve *"bu skor kalibre değil"* demek **güveni düşürüyor ama kararı düzeltmiyor**.
  **Rakip zemini de aynı yönde:** Zenlytic'te ve Pyramid'de güven skoru **YOK**; Tellius'ta
  var ama **yalnız içgörü sıralamasında** ve **chi-kare + BH-FDR'den türetilmiş** — yani
  gerçekten kalibre, ve **NL→sorgu adımında onların da yok**.
  **→ 🥇/🥈/🥉 ve yüzde KALDIRILIR.** Yerine kalan üçü **zaten var ve ölçülmüş değeri olan**
  şeyler: **yol rozeti** (`◆ CUBE` / `▚ LLM`) · **`yol_siniri` filtresi** (Faz F2 —
  *"güven eşiğinin süssüz hâli"*, **doğru karar**) · **makbuz/atıf** (K1).
  *(Ve pozitif taraf ölçülmüş: kaynak/atıf göstermek **işe yarıyor** — temellendirme
  **+%13,83**, canlı A/B'de etkileşim **+%3-10**.)*
  **KAPI** `tests/test_yuzey_sadakati.py` (0.3'te zaten planlı) genişletilir:
  🔴 ***"hiçbir yüzeyde skaler güven render edilmiyor"*** (kaynak taraması).
* 🔴 **Çoklu-sinyal rozet çakışma kuralı** *(§11.9, Tableau — sektörün en olgun çözümü)*:
  sertifika (1.5) + tazelik (1.7) + terfi aynı kartta çakışırsa rozetler **ÇOĞALTILMAZ** —
  **TEK rozet + sinyal SAYISI + en yüksek önemin rengi**; tıklanınca hepsi listede.
  *(Tazelik `uyarı` kademesi **rozet değil**, rakamın altına **ince turuncu dalgalı çizgi** —
  farklı görsel kanal, yarışmaz.)*
* 🔴 **Red üçlüsü** *(§11.3)*: her red **teknik sebep + iş-dilinde açıklama + "şunu dene"
  düğmesi**; belirsizlik tipi (terminolojik/veri-yok/öznel/karar-gerekli) **görsel olarak
  farklı**
* **Köken rozeti** (`⇱✓`/`⇱⚠`/`⇱?`) + `taranmayan_adlar` görünürlüğü
* 🔴 **Discovery rozet dürüstlüğü** *(ertelenen G fazının 1. maddesi — buraya taşındı,
  §A.4/b)*: Discovery cevabı bugün `▚ LLM·<sağlayıcı>` rozeti taşıyor ve **yol filtresi**
  (`62557c2`) *"keşif"*i **adı konmuş bir seviye** yaptı. Eksik olan **tek satır**: cevabın
  üstünde açık **"keşif — doğrulanmamış"** ibaresi + **neyi taşımadığının** beyanı
  (**chip YOK · kırılım YOK · drill YOK** — MIMARI §2.2). *"Yapı ≠ güven"* dersinin
  kullanıcıya görünen hâli
**NASIL** **Kaldırma işi, ekleme işi değil.** `ChatPanel.tsx:16-27`'nin madalya + yüzde
üretimi **silinir**; yerine `answer.py`'nin **yol etiketi** (`cube · cube+llm · vqr · rule`)
doğrudan gösterilir — ikinci bir eşleme tablosu **yazılmaz**.
**KAPI** `tests/test_kanit_gorunurlugu.py` — `source` `llm:*` ile başlayan her cevap
*"doğrulanmamış"* ibaresi **taşıyor** ve `next_steps`/`drill` **sunmuyor**;
+ **V-4** (dürüstlük-dili taraması: *"Dima karar verdi"* **yasak**).
**SONUÇ** MIMARI §9'un *"skaler güven uydurulmaz"* yasağının **üründeki canlı ihlali**
kapanır; kullanıcı bir **yüzde** değil, cevabın **hangi yoldan geldiğini** görür.
**GERİ AL** 🔴 **Geri alınmaz — bu bir YASAK ihlalinin onarımıdır.** Madalyayı geri
getirmek MIMARI §9'u yeniden çiğnemek olurdu. Bayrak `ui_kanit_gorunurlugu` **eklenen
kanıt yüzeyini** kapatır, **kaldırılan madalyayı geri getirmez**.

### 7.9 · Mock silme kapısı  ·  7.10 · Yeniden yaparken düzeltilecek dört hata
**NE** `src/lib/mock/` Plan 3'ün **henüz olmayan** uçlarını taklit ediyor. 🔴 **Her mock,
gerçek ucu geldiğinde SİLİNİR ve silinmesi bir TESTE bağlanır** — aksi hâlde mock, yetim
uçtan **daha kötüdür**: **var olmayan bir yeteneği var gösterir**.
**Dört hata:** (1) **bayrak yüzeyle AYNI commit'te** (dalda 32 commit'in **14'ü = %43,8**
sonradan retrofit) · (2) `ui_*` backend'e (7.1) · (3) 🔴 **`PivotTable.tsx` binary —
teşhis BOM DEĞİL, gömülü NUL** (`\x00`, `:26` ve `:52`'de bileşik-anahtar ayracı); UTF-8
geçerli. Ayraç **görünür bir karaktere** çevrilir · (4) `src/lib/mock/` geçicidir (7.9).
**KAPI** `tests/test_mock_silindi.py` (yeni) + **V-6** (bayrak temizlik borcu).

### 7.11 · **DCM modu UI'ı** *(Plan 2 §11.4 — kaçmıştı)*  [bayrak: `ui_dcm_modu`]
**NEDEN** Bankalar/kamu için **tam görünürlük modu** — bir satış argümanı. Sürüm 1'de
yalnız EK D'de *"DCM 3 tık"* **sayısı** vardı; **madde yoktu** — sayı bir işi tarif etmez.
**NE** `AI_MODE=off` iken sohbet **serbest metin kabul etmez**, menü+kart akışına döner
(alan → analiz tipi → dönem → çalıştır), her ekranda sabit **"DCM Aktif"** rozeti, tüm
sonuçlar **altın rozet**.
**KAPI** `tests/test_dcm_modu.py`: `AI_MODE=off` iken **3 tıkta** cevaba ulaşılıyor; serbest
metin kutusu **yok**.

---

## FAZ 8 · AÇILMA

> 🔴 **DENETİM DÜZELTMESİ (D5) — 8.1 BİR FAZ DEĞİL, BİR MUSLUK.**
> Sürüm 2'de 8.1 **en sondaydı** — ama belgenin **kendi bağımlılık zinciri** onu en az dört
> yerin ön koşulu ilan ediyor: §B (*"v2 için 8.1 koşulmuş olmalı"*) · 5.3 (*"varyantların
> **kalıcı kaynağı** FAZ 8.1"*) · 6.4 (token bütçesi) · 8.1'in kendisi (*"plan seçimi ·
> terfi skorlaması · cache kararı … **onsuz başlamaz**"*).
> → **~130 madde hiçbir gerçek kullanıcı görmeden inşa ediliyordu.** Bu, planın kendi
> doktriniyle (*"kusuru **önce ÖLÇ**"*) çelişen tek büyük yapısal karardı.
>
> **YENİ KONUM: 8.1, FAZ 1'DEN SONRA AÇILIR ve FAZ 2-7 BOYUNCA AÇIK KALIR.**
> * **Dürüst ön koşul:** **1.1 (`motor_rls=shadow`) + 1.3 (yetki) + 1.3b (`enforce_query`) +
>   1.8 (audit)**. RLS'in **`on` olması gerekmez** — gölge mod ölçer, engellemez.
> * **≥300 gerçek tur** bir **kapı değil, SAYAÇtır**; FAZ 5'in kalıp sözlükleri (5.3) onu
>   **CANLI** tüketir.
> * **8.2 → FAZ 3.0'a taşındı**; FAZ 8'de yalnız **8.3** kalır.
> * 🔴 **Kapı:** FAZ 5'e girildiğinde `interaction_log`'un *"kendi denemelerimiz"* payı
>   **<%50**.
> ⚠ **Ve bir çekince kayda geçer:** *"ekip dışı test kullanıcısı"* ile *"gerçek müşteri
> verisi"* aynı şey değildir. İkincisine geçilecekse **1.1 `on`** ve **1.2 (CLS)** de
> kapanmış olmalıdır — bu, açılış kararının **ayrı bir onayıdır**.
**GERİ AL** `ui_dcm_modu=off` → DCM modu görünmez, mevcut akış birebir. Kaydedilmiş DCM
oturumları **silinmez**.

### 8.1 · ⭐ **GERÇEK KULLANIM PENCERESİ**  [bayraksız: KOD DEĞİL — **FAZ 1'den sonra AÇILIR**]
**NEDEN** `interaction_log`: repo `logs/control_plane.db` = **0**, çalışan konteyner
`sqlite3 … "select count(*) from interaction_log"` ile **ölçülür** (D2 — canlı büyüyen sayı
sabit yazılmaz); **hepsi bu oturumların kendi denemeleri**. **Plan 3 §1.4** kendi ifadesiyle:
plan seçimi · terfi skorlaması · cache kararı *"o veriye bağlıdır ve **onsuz başlamaz**"*.
[KANIT §7.3]
**NE** **1-2 gerçek kullanıcı, 2-4 hafta, gerçek sorular.**
**NASIL — kontrol listesi** *(denetim bulgusu: sürüm 1 "ne yapılacağını" yazmıyordu)*:
1. **Enstrümantasyon:** `DIMA_INTERACTION_LOG=true` (varsayılan) · `reject_reason` dolu ·
   `route-distribution` ucu erişilebilir · 7.7'nin paneli canlı
2. **KVKK/rıza:** kullanıcıya *"sorularınız ürünü geliştirmek için kaydediliyor"* bildirimi;
   `interaction_log` **ham sonuç satırı tutmaz** (zaten öyle)
3. **"Gerçek soru" ölçütü:** ekip dışı bir kullanıcıdan gelen, **iş amaçlı** soru
4. **Hedef hacim:** **≥300 gerçek tur** (istatistiksel olarak kalıp sözlüğünü besleyecek
   asgari)
**NASIL** 🔴 **KOD DEĞİL.** 1-2 gerçek kullanıcı, 2-4 hafta. Bu madde bir **kullanım**
işidir ve bir plan maddesi olarak yazılmasının sebebi tam olarak budur: yazılmazsa
*"bir gün olur"* diye askıda kalır — **bugüne kadar olan tam da budur** (Plan 3 §1.4 bunu
kendi ön koşulu ilan etmişti ve hiçbir plan üretmiyordu).
**KAPI** `lab/telemetri_envanteri.py` üç çıktısı da **dolu**: kaynak dağılımı · en sık 20
red gerekçesi · `auto_cube` envanteri.
**SONUÇ** **Bölüm II'nin kilidi açılır**; 5.3'ün kalıp sözlüğü **gerçek ifadelerle**
beslenir; dikey modül sırası **ölçümle** belirlenir; `token` bütçesi **değer kazanır**.
**GERİ AL** Geri alma **yok** — telemetri toplanır ya da toplanmaz. ⚠ **Ama bir kapısı
var:** pencere **açılmadan** Bölüm II'nin telemetriye bağlı maddeleri (plan seçimi ·
terfi skorlaması · cache kararı) **başlayamaz**; §C/13-14 de bu pencereden ölçülür.

### 8.2 → **TAŞINDI: FAZ 3.0**  *(yönlendirme kütüğü — madde burada YOK)*
*"Müşteri DB'sinden katalog kurma — uçtan uca ilk koşum"* **FAZ 3.0'a taşındı** (dış denetim
D8; gerekçe orada). **Bu numara altında iş yoktur** — 3.0'a bakınız.
🔴 *Sürüm 4'e kadar madde **hem 3.0'da hem burada tam metniyle** duruyordu ve iki ayrı yer
(**:1355** ve **:2128**) *"taşındı"* diyordu. **Üç kayıt, üç farklı gerçek.** Kütük kuralı
(§A.2/D5) tam olarak bunun için yazıldı.*

### 8.3 · Çok-worker dağıtım  [bayraksız: altyapı]
**NE** backend: 1.4'ün `fcntl` kilidiyle **gunicorn 4 worker** duman testi │ sözleşme: — │
frontend: — (`api-only`, gerekçe: **dağıtım altyapısı**)
**KAPI** `tests/test_cok_worker.py`: iki süreç aynı çıktı dizinine compose eder, **MDL
bozulmaz** + canlı koşum raporu.
**GERİ AL** Dağıtım yapılandırması — tek worker'a dönmek **kod değişikliği istemez**.

---

# BÖLÜM II — v2 (II-D · II-E) ve v3 (II-F · II-G · II-H)

> **Bölüm I ile AYNI madde biçimi** (§A.2). Plan 3'ün ağır katmanları; sırası ve gerekçeleri
> **Plan 3 §20'den aynen**, envanteri **çalıştırmadan önce tazelenir**.
>
> 🔴 **ŞABLON DENETİMİ — BÖLÜM II HİÇ TARANMAMIŞTI (sürüm 8, ölçüldü @`8f87e40`).**
>
> `N.4` *"Sürüm 5: **33/33 TAM** · KAPI 0 eksik · GERİ AL 0 eksik"* diye kapanış ilan etti.
> Yeniden ölçüldü — **iddia yalnız Bölüm I için doğruydu**:
>
> | Bölüm | Bayraklı/⭐ madde | Şablon ihlali | 🔴 `GERİ AL` YOK |
> |---|---|---|---|
> | **Bölüm I + §G** | — | **13** (çoğu `NEDEN`) | — |
> | **BÖLÜM II** | **18 bayraklı** | **19** | 🔴 **17 / 18** |
>
> *Eksik `GERİ AL` taşıyan 17 madde:* `II-D.2` · `II-D.3` · `II-D.4` · `II-D.5` ·
> `II-D.11` · `II-E.1` · `II-E.7` · `II-F.1` · `II-F.3` · `II-F.5` · `II-F.7` ·
> `II-F.11` · `II-G.1` · `II-G.5` · `II-G.6` · `II-H.1` · `II-H.3`
>
> **Bunun anlamı `N.4`'ün kendi cümlesiyle yazılı:** *"geri alma yolu yazılmamış madde
> **geri alınamaz**."* Yani v2/v3'ün bayraklı maddelerinin **neredeyse tamamı** bugün
> `KURAL B`'nin (*bayrak kapalıyken davranış birebir bugünkü, testle kilitli*) **dışında**.
>
> 🔴 **KÖK NEDEN — ve bu tam olarak `KAT-5`'in kendisi:** denetim betiğinin deseni
> `^### ([0-9]+\.[0-9]+|AJ[0-9])` idi; **`II-D.1` biçimindeki başlıkları kapsamıyordu.**
> Yani araç bir **kapsamı** değil bir **deseni** taradı ve *"33/33 TAM"* raporladı.
> *Sayılan her küme, kapsamadığı her şeyi görünmez kılar.*
>
> **İKİ BAĞLAYICI KARAR:**
>
> 1. **Kapı düzeltilir, 17 blok ŞİMDİ YAZILMAZ.** `D5`'in kapısı
>    (`tests/test_yol_haritasi_butunlugu.py`, **FAZ 0.14**) `### II-<X>.<N>` başlıklarını
>    da tarar ve **her bayraklı maddede `GERİ AL` arar**. ⚠ *Bugün 17 boş blok yazmak
>    **ölü doğuş** olurdu* (§A.2): henüz tasarlanmamış bir yeteneğin geri alma yolunu
>    uydurmak, bu belgenin avladığı *"beyan var, karşılığı yok"* sınıfını üretir.
> 2. 🔴 **Hiçbir Bölüm II maddesi, altı bloğu TAM olmadan SIRAYA ALINMAZ.** Blok, madde
>    **planlandığında** yazılır — teslim edildiğinde değil. Kapı bunu FAZ 0.14'ten
>    itibaren zorlar; o güne kadar liste **açık borç** olarak burada durur.
>
> ⚠ **Ve `D5` kapısının kendi şartnamesi de kırık:** kural *"her `<FAZ>.<N>` atfı için bir
> `### <FAZ>.<N> ·` başlığı"* diyor, ama ~20 madde **birleşik başlıkta** yaşıyor
> (`### 0.6 – 0.11 ·` · `### 1.10 · … · 1.11 ·` · `### II-E.8 · … II-E.11 ·` …).
> Kapı harfiyen koşulursa **~20 yanlış-pozitif yetim** verir → **kapı, birleşik başlıkları
> ayrıştırmalı** (başlık satırındaki **her** `<FAZ>.<N>` jetonunu tanımlı sayar).

> **Üç ön koşul — hiçbiri atlanamaz:**
> 1. **v1 kapanmış** (§C'nin **16** ölçütü yeşil) — bu katmanlar **metrik kaydına** (2.2),
>    **onay akışına** (6.1) ve **motor-RLS'e** (1.1) bağımlıdır.
> 2. **FAZ 8.1 koşulmuş** — Plan 3 §1.4: *"onsuz başlamaz"*.
> 3. **§II-0'ın 11 maddesinin her birine KARAR BAĞLANMIŞ** — `[TEYİT ALINDI]` **ya da**
>    `[TEYİT ALINMADI — talep gözlenmedi]`. 🔴 *"Teyitli"* **değil**: `E1` gereği talep
>    görmeyen madde **açık kalır**, dolayısıyla *"11'i teyitli"* şartı **asla sağlanamazdı**
>    (bkz. §II-0'ın döngü düzeltmesi). ⚠ Kapı **v2'ye ait 9 maddeyi** sayar; `6B.14`
>    (→II-H.1) ve `6B.16` (→II-H.2) **v3'tedir** ve v2'nin kapısında **durmaz**.

### II-0 · 🔴 `[TEYİT BEKLİYOR]` — 11 madde

Plan 3 §3.4: *"Uygulamaya geçmeden önce bu 11 madde için **KULLANICI TEYİDİ ALINMALIDIR** —
bu planın **tek bilinçli açık ucudur ve gizlenmemiştir**."* Şartname blokları PDF→MD
dönüşümünde **kaybolmuş**; R-kütüğü, UC kabul satırları ve araç-karar tablosundan
**rekonstrüksiyonla** yazılmışlar — **uydurulmuş değil, türetilmiş**.

| Şartname | Konu | Öncelik | Nerede |
|---|---|---|---|
| **4.17** | Refleks yayı (`yol_tipi ∈ {refleks, derin}`) | P0/P1 | **v1 FAZ 6.4** — madde başlığında da işaretli |
| **5.11** | **7 katmanlı hafıza ağı** | **P0** | II-F.9 |
| **5.12** | Bağlam Bakım Ajanı + tazelik SLA (**30 gün**) | **P0** | II-F.4 |
| **6.12** | Departman podları + kapsam zorlaması | **P0** | II-D.9 |
| **6.13** | **Nedensellik grafı** (TEK graf, ÜÇ tüketici) | **P0** | II-D.1 |
| **6.14** | Gelişim yol haritası | P1 | II-D.10 |
| **6.15** | Açıklanabilirlik katkı yüzdeleri (**SHAP kurulmaz**) | **P0** | II-D.1 |
| **6B.13** | Telos/OKR senkronizasyonu (Delta-KPI kapısı) | **P0** | II-E.10 |
| **6B.14** | Departman hakemi (OR-Tools CP-SAT) | P2 | II-H.1 |
| **6B.15** | Karar–sonuç kütüphanesi + counterfactual dürüstlüğü | **P0** | II-E.7 |
| **6B.16** | Anayasal kalkan (Z3) | P2 | II-H.2 |

**Kural:** teyit alınmadan uygulanmaz. Teyit alındığında **`[TEYİT ALINDI · tarih]`** olarak
işaretlenir, **silinmez**.

> 🔴 **DENETİM DÜZELTMESİ (E1) — teyit KULLANICIDAN değil, TELEMETRİDEN alınır.**
> v3 kapsamının önemli kısmı **kayıp bir belgeden yeniden kurgulanmış** bir şartnameye
> dayanıyor. Kullanıcıya *"bunu ister misiniz?"* diye sormak, **var olmayan bir talebi
> onaylatmaktır**. Doğru soru **FAZ 8.1'in telemetrisine** sorulur:
> ***"gerçek kullanıcı bunu sordu mu?"***
> Sormadıysa madde **`[TEYİT ALINMADI — talep gözlenmedi]`** olarak **açık kalır** ve
> uygulanmaz. Bu, kural **D3**'ün (*kanıtsız madde işaretlenir, gizlenmez*) doğal uzantısıdır.

> 🔴 **DÖNGÜ DÜZELTMESİ (sürüm 8) — v2 ASLA BAŞLAYAMAZDI.**
>
> §B ve Bölüm II girişi v2'ye geçiş için *"§II-0'ın 11 maddesi **teyitli**"* şartı
> koyuyordu. Ama hemen yukarıdaki `E1` düzeltmesi diyor ki: talep gözlenmezse madde
> **`[TEYİT ALINMADI]` olarak AÇIK KALIR.** İkisi birlikte şunu üretiyordu:
>
> ```
> madde talep görmez  →  asla "teyitli" olmaz  →  "11'i teyitli" şartı asla sağlanmaz
>                     →  v2 ASLA BAŞLAYAMAZ
> ```
>
> Bu, **§C/9'un `N.1`'de kapatılan döngüsel kilidiyle AYNI SINIF** — *"v1'in kapanması
> v3'ün bir maddesini gerektiriyordu"* — ve bu kez **v2'nin girişinde**, kapatılmamış.
>
> **KARAR:** kapı *"teyitli"* değil **"KARARI BAĞLANMIŞ"** ister. Her madde iki kapanıştan
> birini taşır ve **ikisi de geçerlidir**:
>
> | Durum | Anlamı | Sonuç |
> |---|---|---|
> | `[TEYİT ALINDI · <tarih>]` | telemetride talep **gözlendi** | madde **uygulanır** |
> | `[TEYİT ALINMADI — talep gözlenmedi · <tarih>]` | pencere koştu, talep **yok** | madde **uygulanmaz**, kayıt kalır |
> | *(işaretsiz)* | 🔴 pencere **koşmadı** — karar **verilmemiş** | **kapı KAPALI** |
>
> Yani kapıyı açan şey *"hepsi istendi"* değil, **"hepsine bakıldı"**. `E1`'in kendi
> mantığı zaten buydu; eksik olan **kapının o mantığa göre yazılmamış olmasıydı**.
>
> ⚠ **İkinci düzeltme — ters `KAT-3`:** 11 maddenin **ikisi** (`6B.14` → II-H.1,
> `6B.16` → II-H.2) **v3'e** aittir. v3 maddelerinin kararını **v2'nin giriş kapısında**
> beklemek, *"enabler tüketicisinden sonra"*nın **tersi** bir ihlaldir. **Kapı v2'ye ait
> dokuz maddeyi sayar**; ikisi kendi sürümlerinin kapısında karara bağlanır.

---

## II-D · ANALİST KATMANI  → **v2**

**NEDEN** **19/19 doğrulandı**: `forecast|predict` · `what.?if|simul` · `cohort|kohort` ·
`SWOT` · `scorecard|karne` → **hepsi SIFIR**. Bu katman **sıfırdan yazılacak**.
**ALT SIRA (Plan 3'ün kendi gerekçesi):** `causal_graph` → tahmin → what-if → kohort →
**karne en son** (diğerlerinin çıktısını tüketir).

> ⚠ **DENETİM DÜZELTMESİ (E3) — sıra mühendislik olarak doğru, PARİTE açısından ters.**
> Kategorinin demo ekranı **tahmin + what-if**; `causal_graph` bir **altyapıdır**.
> **Uzlaşma:** `II-D.1` **kalır ve önce gelir** — ama yalnız **ortak dataclass +
> `arithmetic` kenar** (minimal). **`causal` kenarı** (`varsayim_metni` + `kanit_gucu`)
> **`II-D.1b`'ye ayrılır** ve `ui_tahmin` ile `ui_what_if`'ten **SONRAYA** ertelenir.
> Parite ekranı **erken çıkar**, ortak yapı **bozulmaz**.

### II-D.1 · ⭐ Nedensellik grafı — **TEK graf, ÜÇ tüketici**  *(§10.6)*  [bayrak: `ui_nedensellik_grafi`] `[TEYİT: 6.13, 6.15]`
**NEDEN** Üç yetenek (what-if · kök-neden · açıklanabilirlik) **aynı veri yapısına** ihtiyaç
duyuyor. Ayrı yazmak, bu depoda **beş kez ölçülmüş** sapma deseninin altıncısı olurdu.
Plan 2 **bağımsız olarak aynı sonuca varmış** (§9.3).
**NE**
* backend: **`app/graf.py`** — 🔴 **ORTAK dataclass BURADA tanımlanır** (denetim bulgusu S3:
  sürüm 1'de II-D.1 `DriverGraph`'a dayanıyordu ama onu II-D.3 yaratıyordu):
  `SurucuDugumu{ref, ifade}` · `Graf{dugumler, kenarlar: list[tuple[kaynak,hedef,iliski_tipi]],
  dogrulama_hatasi}`. `causal_graph.py` ve `driver_graph.py` **ikisi de bunu import eder**
* **Üç düğüm sınıfı (CDD)** *(§11.1 — kaçmıştı)*: `secimler` · `ara_degiskenler` · `sonuclar`
* Kenar etiketi: **`"arithmetic"`** (what-if) vs **`"causal"`**; `causal` kenar ayrıca
  **`varsayim_metni`** + **`kanit_gucu`** (`zayıf|orta|güçlü`) taşır
* sözleşme: `Graf`; 🔴 **LLM düğüm/kenar YAZAMAZ**, yalnız değer önerir
* frontend: **ortak Şema/DAG bileşeni — TEK yapı, ÜÇ render modu**
**NASIL** Katkı yüzdeleri `contribution.py`'nin **kendi ölçtüğü** ayrıştırmadan gelir.
🔴 **SHAP KURULMAZ** (`6.15`): bir kütüphanenin açıklamasını *"nedensellik"* diye sunmak,
MIMARI §3.4c'nin `hierarchies` kararının ihlali olurdu — **uydurulmuş bir nedensellik,
güvenle yanlış bir yol üretir**.
**KAPI** `tests/test_graf.py`: aynı dataclass'ın iki etiketle **karışmadığı**;
`varsayim_metni` boş bir `causal` kenar **üretilemiyor**; `causal_graph.genislet` **araç
kaydında**.
**SONUÇ** Üç yetenek **tek grafla** doğar; ikinci graf motoru **yazılmaz**.
**GERİ AL** bayrak `off` → mevcut `DrillDownPanel` yolu birebir (strangler fig).

### II-D.2 · ⭐ Tahminleme — **ARALIK ZORUNLU**  *(§10.1)*  [bayrak: `ui_tahmin`]
**NE**
* backend: **`app/forecast.py`** + **`ForecastContract`** (`metric_ref` · `grain` ·
  `method` ∈ **`theta|ets_aan|ets_aaa|seasonal_naive`** · `train_window` ·
  **`holdout_mase`** · `empirical_coverage` · `reconciliation` ∈ `MinT|bottom_up|None` ·
  `lower/mid/upper` · **`contract_id`**)
* sözleşme: **`alt` · `orta` · `ust` · `guven_notu`** (`düşük|orta|yüksek` — **SKALER
  DEĞİL**); Plan 2 alan adlarını **birebir** benimsemiş, **ikinci çeviri katmanı YOK**
* frontend: **`TahminBandi`** — `chart.ts` `referenceLine`/alan-doldurma **zaten var**
**NASIL** **Prophet KULLANILMAZ** (§D.1). Nixtla StatsForecast **~500× hızlı**, derin
öğrenme **~25.000× maliyet** `[DOĞRULANMADI — kaynak EK F'ye]`. BigQuery TimesFM
**DEĞERLENDİRİLMEDİ** (kayıt).
🔴 **Toplanabilirlik kapısına bağlanır** *(§10.1 — kaçmıştı)*: `contribution.ayristirilabilir_mi`
**birebir aynı fonksiyon** çağrılır; `AVG`/oran ölçüsünü aggregate seviyede tahmin edip
bileşenlere bölmek **matematiksel olarak yanlıştır**. ← Plan 3'ün *"sektörde neredeyse hiç
emsali yok, **gerçek fark burada**"* dediği tek şey.
🔴 **Görsel sözleşme** *(Plan 2 §9.2 — kaçmıştı)*: aynı serinin **AÇIK TONU** (kesikli çizgi
**DEĞİL** — Tableau'nun belgelenmiş kararı) · bant kenarı **kademeli opaklık** · **gerçekleşmiş
kısım DAHA belirgin, tahmin DAHA soluk** (*"güvene görsel ağırlık ver, belirsizliğe değil"*)
· `guven_notu` **bant genişliğine** yansır · **nominal "%95 güven aralığı" İDDİA EDİLMEZ**.
**KAPI — dört sınır-değer testi**: **<12 ay → tahmin YOK** · **MASE ≥ 1.0 → yayımlanmaz** ·
**2-11 satır → `seasonal_naive`** · Holt-Winters min **m+5** (aylık **17 nokta**).
**+ kısmi son dönem DIŞLANIR** (B5, Tableau *"Ignore Last"*).
**SONUÇ** *"İleride ne olur?"* cevaplanır — **ve asla tek sayıyla**.

### II-D.3 · What-if / duyarlılık  *(§10.2)*  [bayrak: `ui_what_if`]
**NE** backend: **`app/driver_graph.py`** — II-D.1'in `Graf`'ını **import eder**;
**`Senaryo`** tablosu: **DEĞİŞMEZ overlay** (`driver_graph_id` + **`driver_graph_version`
(B8)** + `overrides` + `contract_id`) — *"overlay, **asla mutasyon değil**"*.
🔴 **Döngü reddi YAZMA anında** *(§10.2 — kaçmıştı)*: topolojik sıralama; döngü →
`dogrulama_hatasi`; **tanımsız değişken override'ı → dürüst red**.
**frontend — etkileşim kuralları** *(Plan 2 §9.3 — kaçmıştı)*: slider grafiğe **DOKUNMAZ**
(ayrı kontrol) · sürücü düğümüne **hover → formül tooltip** · bir override'a tıklayınca
**tüm aşağı-akış düğümleri vurgulanır** · senaryo seçici **sol üstte sabit**, çoklu-seçim
**sütun olarak** · 🔴 *"sürücü ekle / formül tanımla"* **yalnız insan girişine açık form**
(LLM önerisi buraya **asla yazmaz**) · kaydet dili **"yeni senaryo"**.
**KAPI** `tests/test_senaryo.py`: graf versiyonu değişince senaryo
**`yeniden_dogrulama_gerekli`**'ye düşüyor; döngü **yazma anında** reddediliyor.
**KAPSAM DIŞI** üçüncü *"karşılaştırma modu"* **icat edilmez** (PK-19) · yeni animasyon
motoru yok (KD-15) · **tam planlama modeli (Anaplan/Pigment) kapsam dışı**.

### II-D.4 · Kohort analizi  *(§10.3)*  [bayrak: `ui_kohort`]
**NE** backend: `app/cohort.py` — **Cube.dev date-spine deseni** + **`maturity_mask`**
* sözleşme — 🔴 **BEŞ zorunlu parametre** (sürüm 1'de dördü vardı): **`tur`** (n-gün |
  sınırsız | aralık) · **`olusum_modu`** (ilk-kez | ilk-pencerede | tekrarlayan) ·
  **`min_kohort_buyuklugu`** · `tamamlanmamis_donemi_disla` · **`ortalama_yontemi`**
  (`agirlikli | basit`) — *"küçük kohort ortalamayı çarpıtmasın"* (B4).
  **Backend bunları ASLA ÇIKARMAZ, kullanıcı beyan eder.**
* frontend: **`KohortIsiHaritasi`** + **parametre şeridi (beş parametre görünür ZORUNDA)**
🔴 **Normalizasyon kararı** *(Plan 2 §9.4 — kaçmıştı)*: **GENEL normalizasyon varsayılan**
(satır-içi **DEĞİL** — Mixpanel'in *"her satır kendi içinde iyi görünür"* yanıltıcılığı
**reddedilir**) + **her hücrenin ham yüzdesi HER ZAMAN görünür** (renk yalnız ikincil tarama
sinyali); olgunlaşmamış hücre = **dolgu YOK + kesikli kenarlık + soluk metin + tooltip**
(gri/çapraz-tarama **değil**).
**KAPI** `tests/test_kohort.py`: **`min_kohort_buyuklugu=30` altında üretilmiyor**;
**boş hücre UYDURULMUYOR**; a11y: metin **~%40 doygunluk üstünde beyaza dönüyor** (A11Y-10),
min opaklık **~%10**.
**KAPSAM DIŞI** kohort hücresi **yeni drill modalı icat etmez** (PK-11) → `ContractDetailPanel`.

### II-D.5 · Karne kartı + SWOT  *(§10.4)*  [bayrak: `ui_karne_karti` · `ui_swot_karti`]
**NE** **Mevcut motorların KOMPOZİSYONU — yeni hesap YOK.** 6 kritik metrik (şirket
profilinden, II-F.8) + `interpret` sinyalleri + `contribution` + `stats`.
🔴 **SWOT maddesinin `contribution` bulgusuna ZORUNLU FK'si** (UC-6.8) + **dört-çeyrek
sınıflandırmanın DETERMİNİSTİK türetimi** (`lower_is_better` + trend yönü + hedefe-göre-durum);
**LLM yalnız madde METNİNİ yazar, SINIFI değil**.
🔴 **Tableau Pulse "BAN" modeli**: **TEK, en yüksek-etkili içgörü cümlesi** (birden fazla
değil); **renk TEK ayardan (`lower_is_better`) türer**, her öge kendi renk mantığını
**icat etmez**.
frontend: **widget, yeni ekran DEĞİL** (PK-13); SWOT **2×2**, madde **≤150 karakter**,
mobilde tek sütun.
**KAPI** `tests/test_karne.py`: karne **kendi sorgusunu yazmıyor**, kayıtlı araçları
çağırıyor; FK'sız SWOT maddesi **üretilemiyor**.

### II-D.6 · Skor kartı  *(§10.5)*  ·  II-D.7 · Karbon-başabaş  *(§10.7)*
**NE** **`SkorKartiSablonu`** (`kriterler_json: [{metrik_ref, agirlik, yon}]` · `kapsam`) —
**TEK normalize edici** (min-max); `yon` **`lower_is_better` beyanından**, ad tahmininden
**değil**. **`EmisyonFaktoru`** referans tablosu — **kod içine GÖMÜLMEZ** (UC-6.12).
**KAPI** faktör tablosu yoksa **hesap üretilmez** ve **nedeni söylenir**.

### II-D.8 · Karar Kaydı v1  *(§10.8)*  ·  II-D.9 · Departman podları  *(§10.9)* `[TEYİT: 6.12]`  ·  II-D.10 · Gelişim yol haritası  *(§10.10)* `[TEYİT: 6.14]`
**NE** §10.8 **II-E'nin demo sürümüdür, YENİDEN TASARLANMAZ.**
**`DepartmanPodu`** (`ad` · `metrik_seti_json` · `anomali_kurali_json` · `oneri_sablonu` ·
**`sorumluluk_siniri_json`**) — kapsam zorlaması **`authorize()` üzerinden**, ve
**sorumluluk sınırı UI'da da uygulanır** (`ui_departman_podlari`).
**Gelişim yol haritası:** **`metrik_ref` + `sahip` + `beklenen_etki`** ZORUNLU üçlüsü —
üçü olmadan madde **yazılamaz**.
**KAPI** pod kapsamı dışındaki metriğe pod görünümünden **erişilemiyor**.

### II-D.11 · **CEO Günlüğü / Oturum sentezi** *(şartname 6.5, Plan 2 §9.5 — kaçmıştı)*  [bayrak: `ui_ceo_gunlugu`]
**NE** Tuval raporunun **TEMATİK** varyantı (kronolojik değil: finans/operasyon/satış
gruplu). 🔴 **Yeni buton EKLEMEZ** (PK-15) — aynı *"Rapor oluştur"* akışının tematik seçeneği.
**KAPI** `tests/test_ceo_gunlugu.py`: yeni uç **yok**, `report.compose`'un parametresi.

---

## II-E · KARAR MOTORU  → **v2**

**NEDEN** `decision.py` (148 satır) + `DecisionRecord` **çalışıyor** ama Plan 3'ün ölçümüyle
**6B'nin ~%15'i**. **Sektörde emsal yok** (§11.1).
**MİMARİ KURALI** `app/decision.py` **MEVCUT modülün genişlemesidir, YENİDEN YAZILMAZ**.
Üç blok: `CerceveBlogu` / `MekanizmaBlogu` / `BeklentiSonucBlogu` — Plan 2 bu adları
**birebir** benimsemiş.

🔴 **İki hüküm** *(§11.1 — kaçmıştı)*:
1. **Decision Quality'nin EN-ZAYIF-HALKA kuralı** — karar kalitesi altı unsurun
   **minimumudur**, ortalaması değil. (Bir unsuru sıfırsa karar kalitesi sıfırdır.)
2. **DMN bilinçle REDDEDİLDİ** — hit policy yalnız II-H.2'nin dar alanında ödünç alınır.
   *(Yazılmazsa altı ay sonra yeniden tartışılır.)*

🔴 **`answer.seal()` ZORUNLULUĞU** *(Plan 2 §15-3 — kaçmıştı)*: Karar Motoru kendi
bounded-context'i olduğu için `seal()`'ı **atlaması en olası yer**. **Her karar çıktısı
`seal()`'dan geçer** — makbuz/iz/PII maskesi **yapısal** kalır.
**KAPI** `tests/test_kapanis_zinciri.py` genişletilir.

### II-E.1 · Çerçeveleme  *(§11.3)*  ·  II-E.2 · Seçenek üretimi  *(§11.4)*  ·  II-E.3 · Kriter + ağırlık  *(§11.5)*  [bayrak: `ui_karar_motoru`]
**NE**
* **Derinlik merdiveni**: **`hizli_3`** / **`tam_9`**; **soruya bağlı, thread'e değil**
* **Seçenek üretimi**: **"Hiçbir şey yapmama" HER ZAMAN İLK**. 🔴 **Sistem seçenek İCAT
  ETMEZ** *(§11.4 — kaçmıştı)*: 2-3 alternatif, **geçmiş `DecisionRecord` satırlarından
  `kriterler_agirliklar` BENZERLİĞİYLE** örneklenir. Kaynak yazılmazsa LLM'e kalır → B1 ihlali
* **Kriter + ağırlık — 🔴 DOKUZ KRİTERLİK HAVUZ** *(sürüm 1'de hiç yazılmamıştı)*, toplam
  **100 puan**, varsayılan dağılım:

| # | Kriter | Varsayılan |
|---|---|---|
| 1 | Finansal etki (net) | 20 |
| 2 | Uygulama maliyeti | 15 |
| 3 | Geri alınabilirlik | 12 |
| 4 | Zaman ufku (ne kadar sürede sonuç) | 12 |
| 5 | Operasyonel risk | 12 |
| 6 | Uyum/yasal risk | 10 |
| 7 | Müşteri/itibar etkisi | 8 |
| 8 | Ekip kapasitesi | 6 |
| 9 | Stratejik uyum (Telos/OKR, II-E.10) | 5 |

  🔴 **Kriterler seçeneklerden ÖNCE belirlenir ve GERİ DÖNÜLEMEZ** — sonradan değiştirmek,
  sonucu bilerek ağırlık ayarlamaktır.
  **frontend** *(Plan 2 §10.4 — kaçmıştı)*: ağırlık kaydırıcısında **orijinal ağırlığı
  işaretleyen sabit işaretçi** (+ "sıfırla" ona döner) ve **%0/%100 sınır işaretleriyle uç
  sonuç önizlemesi** (AHP deseni)
**KAPI** `tests/test_karar_kriterleri.py`: seçenek üretildikten sonra ağırlık değişimi
**reddediliyor**; ağırlık toplamı **100**.

### II-E.4 · ⭐ Kanıt matrisi — **VERİ | VARSAYIM | BİLİNMİYOR**  *(§11.6)*
**NEDEN** Plan 2: *"bu raporun tasarladığı **en somut yeni bileşen**"*; iki plan bağımsız
olarak **aynı isimlendirmeye** varmış.
**NE** Her kriter × seçenek hücresi **üç sınıftan biri**: gerçek veri (**makbuzlu**) · beyan
edilmiş varsayım · **bilinmiyor**. frontend: **`KanitMatrisi`**.
🔴 **KAPI** **`BİLİNMİYOR` GİZLENEMEZ** — boş hücre **yoktur** (§14.2 *"boş durum ≠ hata"* +
PK-6 *"asla gizleme"*). `tests/test_kanit_matrisi.py::test_bos_hucre_yok`.
**SONUÇ** Bir kararın **ne kadarının veriye dayandığı** ilk kez **sayılabilir**.

### II-E.5 · Tavsiye + tersine soru  *(§11.8)*  ·  II-E.6 · Duyarlılık  *(§11.6)*
**NE** 🔴 **Kırılma noktası — İKİLİ ARAMA (binary search)** ile deterministik ters-çözüm
*(§11.8 — sürüm 1 "deterministik ters-çözüm" diyordu, yöntem yoktu)*: *"X'in %kaç değişmesi
kararı çevirir?"* — arama aralığı `[-100%, +500%]`, tolerans `%0,5`, **çözülemezse dürüst
red**. Kırılganlık: **<%5 kırılgan · %5-10 orta · >%10 sağlam**.
Duyarlılık **+%10/+%20/+%30**; **`WhatIfPaneli`'ni (II-D.3) YENİDEN KULLANIR**.
frontend: gradient eğrisi **istemci tarafında** (yeni uç **yok**, KD-14); **ayrı sayfa
DEĞİL, katlanır panel** (PK-12).
**KAPI** reddedilen seçeneklerin **gerekçesi kayıtta kalıyor**.

### II-E.7 · ⭐ Karar Kaydı  *(§11.9)*  [bayrak: `ui_karar_kaydi`] `[TEYİT: 6B.15]`
**NE**
* backend: `DecisionRecord` genişlemesi — **`cerceve_json`** · **`mekanizma_graph_ref`** ·
  **`beklenti_sonuc_json`** (`content_hash`/`supersedes` **zaten var**;
  `supersedes` UI'dan **yazılabilir** — v1 FAZ 0.11'de **BAĞLANDI**, silinmedi)
* 🔴 **`imzalayan_id` NOT NULL ve İNSAN olmak zorunda** *(§11.10 — kaçmıştı)* +
  `POST /decisions`'ta **`is_agent=False` doğrulaması** + **"otomatik uygulama YOK"** +
  **`GET /decisions?q=`** liste ucu (bugün **yok**)
* 🔴 **`BeklentiSonucBlogu.forecast_contract_id`** = **ön-kayıtlı temel çizgi** *(§11.2 —
  kaçmıştı)*: tahmin sözleşmesinin karar kaydına **karar anında** çivilenmesi, Sonuç
  Skorunun ölçülebilir olmasının **ön koşulu**
* **16 alan** — sayılmış: `id` · `baslik` · `cerceve` · `secenekler` · `kriterler_agirliklar`
  · `kanit_matrisi` · `tavsiye` · `ret_gerekceleri` · **`katılanlar`** · **`varsayim_defteri`**
  · `imzalayan_id` · **`mdl_commit`** · `content_hash` · `supersedes` ·
  **`gozden_gecirme_tarihi`** · `forecast_contract_id`
🔴 **İKİ AYRI SKOR, ASLA TEK SAYIYA KARIŞTIRILMAZ:** **Karar Kalitesi** (süreç, **karar
anında**, en-zayıf-halka) ⟂ **Sonuç Skoru** (**değerlendirme ufku dolunca**). İyi bir karar
kötü sonuç verebilir; toplamak öğrenmeyi **imkânsız** kılar.
🔴 **Counterfactual dürüstlüğü:** *"şunu yapsaydık şu olurdu"* **iddia edilmez** — yalnız
**beklenti ile gerçekleşen** kıyaslanır.
**KAPI** `tests/test_karar_kaydi.py`: append-only · `imzalayan_id` **ajan olamaz** · iki
skor **ayrı alanlarda** ve **birleştiren kod yok** (kaynak taraması).

### II-E.8 · Karar Rozeti  *(§11.7)*  ·  II-E.9 · Kırmızı çizgi  *(§11.10)*  ·  II-E.10 · Telos/OKR  *(§11.12)* `[TEYİT: 6B.13]`  ·  II-E.11 · Karar şablonları  *(§11.11)*
**NE** **Karar Rozeti**: türetilmiş istatistik, **AYRI SKOR DEĞİL** — kanıt matrisinden
**ayrıştırılmış ÜÇ YÜZDE** (veri/varsayım/bilinmiyor). 🔴 **Skaler "karar güveni"
ÜRETİLMEZ** (MIMARI §9'un *"kalibre edilmemiş sayı bir güven değil bir **süstür**"*).
**Kırmızı çizgi** **kod-seviyesi kısıttır**: `Principal.is_agent` + `PolitikaKurali
(kisit_ifadesi)` — ajan kırmızı çizgiyi **öneremez bile**.
**Telos/OKR**: **`MetricTarget` + `scope="sirket_ana_hedef"`** (**ayrı tablo DEĞİL**) +
**Delta-KPI filtre kapısı** — şirket hedefine katkısı olmayan öneri **listeye girmez**.
**Karar şablonları**: Terfi Motoru'nun (II-G.5) **dördüncü kaynağı**.
**KAPI** `tests/test_kirmizi_cizgi.py`: `is_agent=True` ihlal eden seçeneği **üretemiyor**.

---

## II-F · İŞ BAĞLAMI + GLOBAL HAFIZA  → 🔴 **DÖRDÜ v2'NİN ÖNÜNE, kalanı v3**

**NEDEN** Ölçüldü: iş bağlamı kütüğü · görev motoru · şirket profili · çok katmanlı hafıza
→ **hepsi SIFIR**. Plan 3: *"motorlar bunlarsız da çalışır (biraz daha az isabetli) — ama
sabah brifinginin ve geçmiş kararlardan seçenek önerisinin **kalitesi buna bağımlı**."*

> 🔴 **SIRA DÜZELTMESİ (`KAT-3`, §B):** **II-F.1 · II-F.3 · II-F.5 · II-F.8** → **II-D'den
> ÖNCE**. Gerekçe §B'de: bağlamsız anomali **yalnız z-skorudur**, bağlamsız karar motoru
> **boş bir matristir**. *Plan 3'ün kendi cümlesi (**"biraz daha az isabetli"**) bu üç fazın
> ölçümüyle çelişiyor — düzeltme kayda geçti.*

> 🔴 **VE TOPLAMA STRATEJİSİ DEĞİŞTİ: *"SOR"* DEĞİL *"TÜRET"*.**
> II-F.1'in yolu bugün bir **sihirbaz** (`ui_is_baglami_sihirbazi`) — yani **müşteriye form
> doldurtmak**. [KANIT §2.1] darboğazı **zaten adlandırmış**: *"mekanizma üretiliyor,
> **sözlük üretilmiyor**."* Katalogda olan iş bağlamında da olur: **mekanizma iner, kimse
> doldurmaz.**
>
> **Kullanıcının *"dolaşıp öğrensin"* sezgisi doğru — ve açık web'e gitmeden karşılığı var,
> müşterinin KENDİ VERİSİNDE:**
>
> | Bağlam | Nereden **türetilir** | Altyapı |
> |---|---|---|
> | Mali takvim · dönem yapısı | ERP'nin **kendi takvim tablosu** | `db_introspect` ✅ · **2.6** (mali takvim) |
> | Ürün/müşteri/tedarikçi hiyerarşisi | ERP **kart tabloları** | `db_introspect` ✅ · II-F.2 |
> | Maliyet merkezi · organizasyon | **muhasebe hesap planı** | `mizan` cube'u ✅ |
> | Hangi metrik **kimin işi** | **query-log madenciliği** | **II-G.3 zaten planda** |
> | İş terimleri | mevcut **raporlar · prosedür dokümanları** | `sinonim_onerici` ✅ (insan onayı) |
>
> **Yani *"şirketi tanıması"* SORULMADAN türetilebilir** ve parçaların çoğu **kurulu**.
> Eksik olan, bunları birleştiren madde — ve o, **3.0'ın (tenant açılış zinciri) doğal
> devamıdır**. ⚠ **Sihirbaz KALDIRILMAZ:** türetilen her şey **taslak** gelir
> (`onay_durumu`), insan **onaylar** — `sinonim_onerici`'nin `approved=False` deseni birebir.
> *Türetme, sormanın yerine geçmez; **sorulacak soruyu 20'den 3'e indirir**.*

### II-F.1 · İş bağlamı kütüğü  *(§7.1)*  [bayrak: `ui_is_baglami_sihirbazi` · `ui_is_baglami_kartlari`]
**NE** **`ŞirketBaglami`** (append-only, versiyonlu): `alan` ∈ **`ne_satiyoruz` | `kime` |
`kritik_basari_faktoru` | `surec_akisi`** · `deger` (JSON) · `sahip` · `versiyon` ·
`onceki_versiyon_id` · `onay_durumu`. **`SurecAdimi`**: sıralı adımlar +
**`darbogaz_adayi`** (Sankey'in — 7.3/l — ve darboğaz analizinin veri kaynağı).
frontend: `IsBaglamiSihirbazi` — kurulumun doğal devamı.
**KAPI** eski kayıt **kayıp olmuyor**; 🔴 **"Bilmiyorum" üçüncü seçeneği ASLA varsayım
üretmiyor** → `belirsiz` durumu + Bakım Ajanı tetikleyicisi.

### II-F.2 · Ticari varlık kartları  *(§7.2)*
**NE** **`UrunKarti`** — **kendine-referanslı `bilesen_id` FK (BOM)**, 🔴 **derinlik sınırı
ZORUNLU**; maliyet/marj/karbon **AYNI ağacı okur**. `TedarikciKarti`/`MusteriKarti`.
**`SozlesmeKaydi`**: `vade_tarihi` · `yenileme_tarihi` · `cezai_sart_tutari`.
⚠ **MIMARI §5 UYARISI:** kendine-referanslı ilişki + calc kolon → Rust'ta **PANIC**
(`lineage.rs:146` `.unwrap()`), ve **`except Exception` YAKALAMAZ** (`PanicException` MRO'su).
BOM tam bu sınıftır → **derinlik sınırı bir tercih değil, ÇÖKME KORUMASI.**
**KAPI** `tests/test_bom_derinlik.py`: sınır aşımında **dürüst red**, motor **çağrılmıyor**.
**SONUÇ** Sözleşme vadesinden **90 gün önce** otomatik `Gorev`.

### II-F.3 · Kurumsal takvim  *(§7.3)*  [bayrak: `ui_kurumsal_takvim`]
**NE** `TenantConfig` genişlemesi: `ay_sonu_kapanis_gun` · `denetim_donemleri_json` ·
`sezon_json` · `butce_donemi_json`. **Dönem çözücü bunu okur** — v1 FAZ 2.6'nın devamı.
**KAPI** *"bu ay"* ay-sonu kapanışına göre **doğru pencere**; ⚠ `CLARIFY:dönem` payı
**sabit kalmalı** (§C/3).

### II-F.4 · Sahiplik + tazelik SLA + **Bakım Ajanı**  *(§7.4, 5.12)* `[TEYİT: 5.12]`
**NE** Her bağlam kaydına `sahip` · **`tazelik_sla_gun` (varsayılan 30)** · `son_dogrulama` ·
`bayat`. Bakım Ajanı **yeni ekran açmadan** çalışır — **bildirim olarak** (PK-17).
**KAPI** bayat bağlam **güven rozetini DÜŞÜRÜR** — v1 FAZ 1.7'nin tazelik merdiveniyle
**AYNI sözleşme** (`taze|uyarı|hata|bilinmiyor`), ikinci kavram **icat edilmez**.

### II-F.5 · İş terimleri sözlüğü  *(§7.5)*  ·  II-F.6 · Görev motoru  *(§7.6)*  [bayrak: `tur_gorev`]
**NE** **`SozlukTerimi`** = `MetricDefinition`'ın (v1 2.2) **genellemesi**, aynı onay akışı.
**`Gorev`**: `baslik` · `sorumlu_id` · `son_tarih` · `durum` ∈ `bekliyor|devam|tamamlandi|
**tikandi**|iptal` + 🔴 **`kaynak_tip` ZORUNLU** (`bulgu|anomali|karar`) + **`kaynak_id`
ZORUNLU FK**.
🔴 **Sohbet girişi — 8. konuşma türü** *(§7.6 — kaçmıştı)*: `TUR_GOREV_OLUSTUR` +
**taahhüt yakalama** (*"halledeceğim"*, *"yarın gönderirim"*); **kullanıcı onayı olmadan
görev ASLA otomatik oluşmaz** (6.1'in onay akışı). ← FAZ 5.1/5.2'nin deseninin devamı.
**Sağlık taraması:** `sahipsiz` ve `tekrar_acilmis` kuralları.
**Ritim:** **2 hafta hareketsiz → `tikandi`**; **30 gün cevapsızlık → ağırlık düşür +
eskalasyon** (v1 1.10).
🔴 **KAPI** **Kökensiz görev YARATILAMAZ** — aksi hâlde görev listesi kanıt zincirinden
kopmuş bir yapılacaklar uygulamasına döner. `tests/test_gorev_kokeni.py`.

### II-F.7 · Sabah brifingi  *(§7.7)*  [bayrak: `ui_sabah_brifingi`]
**NE** `schedules.py` + `channels.py` **kompozisyonu** — v1 5.9'un digest'inin
zenginleştirilmiş hâli: **5 slot**, **30 saniyede okunur**. **Landing'in VARYANTI, yeni ekran
DEĞİL** (PK-14). `brifing.olustur` **araç kaydında**.
**KAPI** brifing **kendi sorgusunu yazmıyor** (B7).

### II-F.8 · Şirket profili + bağlam enjeksiyonu  *(§9.1, §9.2)*
**NE** **`ŞirketProfili`**: `sektor` · `is_modeli` · `ana_departmanlar_json` ·
`kritik_metrik_adaylari_json` · `veri_kalitesi_notlari` · `versiyon` ·
**`olusturulma_yontemi`** (`otomatik_taslak|kullanici_onayli`) · **`son_taranan_tablo_hash`**.
**Bağlam enjeksiyonu: ~800 token**, öncelik **sektör > departman > kritik metrik**.
🔴 **Çelişkide VERİ KAZANIR** *(§9.2 — kaçmıştı)*: profil bir **yorumdur**, `route()`'un
sayısı **gerçektir**.
🔴 **KAPI** `otomatik_taslak` profil **kullanıcı onaylamadan** LLM prompt'una **enjekte
edilmez** (6.1'in onay akışı — **ikinci tüketici**); ADR-0018'in *"adaylar otomatik canlıya
çıkmaz"* kuralının hafıza eksenindeki karşılığı.

### II-F.9 · ⭐ Hafıza: **TEK tablo, 4 tip × 7 katman**  *(§9.5, §9.6)* `[TEYİT: 5.11]`
**NE** **`HafizaKaydi`** — tek tablo:
* **`tip`**: `semantik` | `epizodik` | `prosedürel` | `tercih` *(**`Skill` = prosedürel tiple
  AYNI varlık**, ayrı tanımlanmaz)*
* **`katman`**: `oturum` → `kişi` → `departman` → `şube` → `şirket` → `sektör-k-anonim` →
  `sistem-anonim`
* 🔴 **Dört ayrı `getirme_stratejisi`** *(§9.5 — kaçmıştı)*: `semantik`→**ad-eşleşmesi** ·
  `epizodik`→**zaman-aralığı** · `prosedürel`→**direkt-okuma** · `tercih`→**benzerlik**
* + `gozden_dustu` · `arsivlendi` · `gecersiz_kilindi_by` · `gecersiz_kilindi_neden` ·
  `deleted_at`
**NASIL** **Retrieval EKLENMEZ** — ölçülen bant **+14/−16**: *belleği kur, ama **basit** kur.*

> 🔴 **P0 RİSK — DENETİM BULGUSU (E2): bu madde, kapsam dışı bıraktığımız şeyi ARKA KAPIDAN
> geri getiriyor.** EK J *"retrieval'lı hafıza"*yı dışlıyor; ama **4 tip × 7 katman** bir
> hatırlama sistemidir. Dış kanıt **sert**:
> * **Hafıza kaynaklı yalakalık (sycophancy)** başarısızlık oranları **çoğu modelde %90'ın
>   üstünde**; hatırlanan bilgi **güncel kanıtı usulsüz eziyor**.
> * **Uydurma hafıza yerleştirme** (memory poisoning) **%99,8'e kadar** başarılı ölçüldü.
> * Kişiselleştirilmiş bağlamın **doğruluğu düşürdüğü** mühendislik raporu var.
>
> **Ayakta kalan tavsiye:** her hafıza kaydı **kaynak izi · bayatlık işareti · çelişki
> bayrağı** taşımalı; hafıza güncel kanıtla çeliştiğinde **gerilim sessizce çözülmemeli,
> GÖSTERİLMELİ**.
>
> **→ Şemaya ÜÇ ZORUNLU ALAN eklenir:** **`kaynak_ifade`** (hangi turdan doğdu) ·
> **`son_dogrulama`** · **`celiski_bayragi`**.
> **→ Ve BİR DEĞİŞMEZ:** 🔴 ***hafıza ölçü/cube seçimine ASLA karışmaz.***
> Bu kural **zaten yazılmış durumda** — çalışma ağacındaki `SunumTercihi`
> (*"tercih **ÖLÇÜ/CUBE SEÇİMİNE KARIŞMAZ**"* · *"**SESSİZ** uygulanmaz"*). **O daraltma
> II-F.9'un tamamına uygulanır.**
🔴 **KAPI — ÖNCELİK ÇÖZÜCÜ** (denetim düzeltmesi; sürüm 1 *"en spesifik kazanır"* diyordu ve
bu **kuralı tersine çeviriyordu**): **`coz_oncelik()`** — **`tercih` → KİŞİ kazanır** ·
**`tanım` → ŞİRKET kazanır** · **`kural` → POLİTİKA kazanır**. Yani *"net satış"* tanımını
**kimse kişisel tanımla EZEMEZ**. Çelişki **sessizce çözülmez**: loglanır ve **UI'a taşınır**
(Plan 2 §8.7). `tests/test_hafiza_oncelik.py`.

### II-F.10 · Seçici yazma politikası  *(§9.3 — en kritik tasarım kararı)*
**NE** **`hafiza.yazilabilir_mi`** — bir **KAPI aracı** (çıktı üretmez), `tools.KAYIT`'ta.
🔴 **Altı kriter** (sürüm 1'de üçe inmişti): (1) **tekrarlayan** (≥2 kez) · (2) kullanıcı
tarafından **doğrulanmış** · (3) kapsamı **belirli** · (4) **PII içermiyor**
(**yazma öncesi `pii.mask_text`**) · (5) **çelişki üretmiyor** (`coz_oncelik` ile sınanır) ·
(6) **kaynağı izlenebilir** (`kaynak_tip`/`kaynak_id`).
🔴 **KAPI** Bir LLM çıktısı **doğrudan** hafızaya **yazamaz** — `sinonim_onerici.py`'nin
`approved=False` **SABİT** (parametre değil!) deseninin hafıza eksenindeki karşılığı.

### II-F.11 · Unutma motoru  *(§9.7)*  ·  II-F.12 · Kişisel hafıza şeffaflığı  *(§9.8)*  [bayrak: `ui_hakkimda_bilinenler`]
**NE** Çürüme skoru + **arşiv**; **ASLA hard-delete** (ADR-0019) — **TEK istisna: KVKK
kapsamında kullanıcının kendi kişisel hafızası**. frontend: **"Hakkımda bilinenler"** —
liste + **gerçek silme** + export.
🔴 **KAPI** **Silinen kayıt SONRAKİ cevapta kullanılmıyor** — canlı doğrulanır. KVKK
zorunluluğu olduğu için **Plan 2'yi beklemeden** gerekli.

---

## II-G · ÖLÇEK ve ÖĞRENME  → **v3**

### II-G.1 · Sektör paketleri  *(§14.1)*  [bayrak: `sektor_paketi`]
**NE** **Looker Blocks deseni** — **Fabric/Databricks "as-is" modeli DEĞİL**.
**`PaketOverride`**: `katman` ∈ `sektor|kesisim|sirket` · `golgelenen_satir_ref` ·
🔴 **`sebep` ZORUNLU**.
🔴 **Kurulum akışı** *(Plan 2 §12.8 — kaçmıştı)*: kurulumda **sektör tespiti** → paket
**ÖNERİLİR** → tek tıkla kurulur → **eşleme sihirbazı** ile müşteri verisine bağlanır.
(Sürüm 1'de paket **üretiliyor ama kurulamıyordu**.)
🔴 **Sapma metriği** *(§14.1 — kaçmıştı)*: *"kaç şirket-katmanı satırı sektör-katmanını
gölgeliyor"* — **pack drift göstergesi**, ISO 42001 girdisi.
🔴 **§D.2/3 hükmü burada uygulanır:** sektör kıyası **havuz altyapısı kurulur**
(k-anonimlik kapısı) ama **çıktı bayrak arkasında KAPALI kalır**.
**KAPI** gölgeleme **gerekçesiz yapılamıyor**.

### II-G.2 · Semantik model versiyonlama  *(§14.2)*  ·  II-G.3 · Query-log madenciliği  *(§14.3)*
**NE** dbt'nin **breaking/non-breaking** sınıflandırması + 🔴 **okuma anında hesaplanan üç
durum** *(§14.2 — kaçmıştı)*: **`reproducible` | `numbers_may_differ` | `definition_removed`**
— kaydedilmiş her cevap/karar/tahmin/senaryo için.
🔴 **HÜKÜM:** *"Cube'ün `schemaVersion`'ı bir **cache anahtarıdır**, semantik sözleşme
versiyonu DEĞİL"* — yanlış model almayı önler.
**Query-log madenciliği — 7 adımlı boru hattı** *(§14.3 — tek satıra inmişti)*:
ters-indeks → literal-normalizasyon → sıralama → yenilik kontrolü → doğrulama →
🔴 **LLM YALNIZ İSİMLENDİRME** → **zorunlu insan onayı**.
**ÖN KOŞUL** 🔴 **FAZ 8.1** — madencilik yapılacak log **yok**.

### II-G.4 · VQR/terfi yönetişimi  *(§14.4)*
**NE** `VerifiedQuery`: **`verified_by`/`verified_at` NOT NULL** ·
**`verified_against_definition_hash`** · `needs_reverification` · **TTL**.
🔴 **Terfi regresyon kapısı** *(§14.4 — kaçmıştı)*: aday terfi etmeden önce `eval/run.py`
golden-set **yeniden koşulur**; önceden-doğru bir cevap artık farklı çıkıyorsa **terfi
ENGELLENİR**. ← *"terfi motorunun kendi kalitesini bozması"* riskine karşı **tek savunma**.
**NEDEN** §1.7'nin ölçülmüş felaketi (`fire` ↔ `ciro`, kosinüs 0,92) bunun kanıtı.
**KAPI** `MetricDefinition` değişince bağlı VQR **otomatik `needs_reverification`** (B8).

### II-G.5 · ⭐ Terfi Motoru — **TEK motor, DÖRT kaynak**  *(§14.5)*  [bayrak: `ui_terfi_kuyrugu`]
**NE** **`TerfiKaynagi` Protocol** — `adaylari_bul()` · **`puanla()`** · `uygula()`;
dört uygulama: ölçü · skill · karar-şablonu · hafıza.
🔴 **`puanla()` formülü** *(sürüm 1'de yoktu)* — dört kaynağın **ortak 0-100 ölçeği**:
`0.4×etki` (kaç soruyu etkiliyor, `nl_corpus`'tan) + `0.3×güven` (kaç kez doğrulandı) +
`0.2×tazelik` (son görülme) + `0.1×maliyet_tasarrufu` (LLM çağrısı azalması).
frontend: **`TerfiKuyrugu`** = `ReviewPanel`'in **GENELLEMESİ** (dört kaynak, **TEK ekran**).
🔴 **`reddedildi` ≠ `ertelendi`/`deprecated`** *(Plan 2 §12.3 — kaçmıştı)*: mevcut
`MeasureCandidate.status`'a **birebir** oturuyor, **yeni alan yok**. İkisini tek *"reddet"*e
sıkıştırmak *"iyi ama zamanı değil"* adayları *"kalıcı olarak kötü"* diye kaydeder ve
**terfi motorunun kalibrasyonunu bozar**.
🔴 **Kategori rengi ≠ güven rengi**: dört kaynağın her biri **sabit renk**; etki/güven
**yalnız** PK-13'ün **opaklık** ekseninde.
🔴 **KAPI — decision fatigue**: Snowflake dersi **50+ inceleme → karar yorgunluğu**
`[DOĞRULANMADI]`. Kuyruk **önceliklendirilir** + **toplu inceleme** (*"add to batch"*);
uzun liste onaylayanı *"hepsini kabul et"*e iter (`sinonim_onerici`'nin **en fazla 6 öneri**
kuralının genellemesi).

### II-G.6 · Kredi/maliyet muhasebesi  *(§14.6)*  [bayrak: `ui_kredi_paneli`]
**NE** **`KrediHareketi`**: `islem_tipi` (**sohbet=1 · rapor=4 · agentic=6 · artefakt=8**) ·
`basarisiz` · `model_carpani` (**×1/×2/×3**) · `gercek_token_maliyeti`.
🔴 **Başarısız işlemde kredi YAKILMAZ.** **Altın yol + önbellek = 0 kredi.**
⚠ **Bağımlılık:** *"önbellek = 0 kredi"* kuralı **bir önbelleğin varlığını gerektirir** —
**çift önbellek + isabet/tasarruf paneli** *(Plan 2 §12.9 — kaçmıştı)* bu maddenin **parçası**;
MIMARI §5'in *"sonuç cache'i bilinçle KURULMADI — tekrar oranı ölçülmedi"* kararı **FAZ 8.1
telemetrisiyle** yeniden açılır ve **`security_context_hash` günden itibaren anahtarın
parçasıdır** (B9).
**KAPI** `tests/test_kredi.py`: `source=cube` cevap **0 kredi**; iki farklı
`security_context` → **farklı `cache_key`**.

### II-G.7 · Çok-tenant ölçek  *(§14.7)*
**NE** Tenant modeli başına **10-40 MB**; **500+ tenant**'a kadar **tek süreçte derleme**
`[DOĞRULANMADI]`; `TenantConfig.derleme_grubu`.
**ÖN KOŞUL** v1 **FAZ 1.4** (`fcntl`).

---

## II-H · DIŞ BAĞIMLILIKLI PARÇALAR  → **v3**

**NEDEN (Plan 3):** *"Üçü de **aynı desen** (doğal dilden yapılandırılmış mutasyon/kısıt
çözümüne) ve **aynı turda** ele alınmalı."*

> 🔴 **DENETİM DÜZELTMESİ (E4) — bunlar MADDE değil, ZAMAN-KUTULU SPIKE.**
> İkisi de `[TEYİT BEKLİYOR]` **ve** P2 **ve** bir BI ürününde **doğrulanmamış** yetenekler.
> **Biçim:** *"**2 hafta · BİR gerçek çatışma vakası** · çözemezse **KAPATILIR**"*.
> 🔴 **Öldürme ölçütü YAZIYA GEÇER** — EK J disiplininin (*kapsam dışı, gerekçesiyle*)
> **ileriye dönük** hâli. Spike kapanırsa madde EK J'ye **gerekçesiyle** taşınır, sessizce
> ertelenmez.

### II-H.1 · Departman hakemi — **OR-Tools CP-SAT**  *(§11.13)* `[TEYİT: 6B.14]`  [bayrak: `ui_departman_hakemi`]
**NE** Nicel çatışma (**bütçe/kapasite paylaşımı**) **deterministik** çözülür — **LLM
DEĞİL**. Niteliksel çatışmada LLM **yalnız gerekçe metnini** yazar, kararı **çözücü** verir.
🔴 **Rozet** *(§11.13 — kaçmıştı)*: **"hesaplanmış uzlaşma"** ↔ **"yorumlanmış öneri"** —
nicel/niteliksel ayrımı **kullanıcıya gösterilir**.
`hakem.uzlas` **araç kaydında**.
**KAPI** aynı girdi → **aynı çözüm** (determinizm testi). frontend: **gizlenmez, soluk
gösterilir** (PK-6) — ve *"soluk ama tıklanabilir"* ile *"devre dışı"* **AYNI token'ı
paylaşmaz** (A11Y-9).

### II-H.2 · Anayasal kalkan — **Z3**  *(§11.14)* `[TEYİT: 6B.16]`
**NE** **DAR KAPSAM**: SMT **yalnız sayısal kısıtlarda**; `PolitikaKurali(kisit_ifadesi)`
basit karşılaştırma DSL'i. **Ayrı UI'ı YOKTUR** (KD-18) — yalnız v1 1.10'un eskalasyon
akışına **"ikinci C-level onayı"** olarak yansır.
**KAPI** **build-time CI kapısı** — çalışma zamanında Z3 çağrısı **yok** (gecikme eklemez).

### II-H.3 · Sistem uzmanı copilot  *(§12.6 / şartname 8.20)*  [bayrak: `ui_sistem_copilot`]
**NEDEN** Plan 3 §18'in tespit ettiği **TEK gerçek boşluk**: *"doğal dil → yapılandırılmış
mutasyon"* çevirisi; II-H.2 ile **aynı deseni** paylaşıyor.
**NE** Sohbetten ayar değişikliği **önerisi** → v1 6.1'in **`onay_akisi`**'ndan geçer
(**beşinci tüketici**). `llm.prompt_enhance` deseninin genellemesi.
🔴 **`/settings` ekranlarının YERİNE GEÇMEZ, ÜSTÜNE BİNER** (PK-18).
**KAPI** copilot'un ürettiği hiçbir mutasyon **onaysız** uygulanamıyor; her onay **ayrı
audit satırı**.

---

# EKLER

## EK A — Plan 3 ↔ bu belge **eşleme tablosu** *(iptal kanıtı)*

> ⚠ **Denetim düzeltmesi:** sürüm 1'de **6 satır `✅` diyordu ama hedef bölümün gövdesinde
> iş yoktu**. Hepsi düzeltildi ya da `⚠`ye çekildi.

| Plan 3 § | Konu | Nerede | Yargı |
|---|---|---|---|
| 0 · 1 | kapsam/yöntem · teşhis envanteri | §A · [KANIT §16.5, §12.2] | ⚠ **envanter BAYAT** — 8 sayı düzeltildi (−1.1/A5-A8) |
| 2 | değişmez backend kuralları (B1-B10) | MIMARI §4/§5 + **EK C** | ✅ **B10 (arka plan kimliği) → FAZ 1.1b** |
| **3.1** | teknoloji yığını — 8 hüküm | **§D.1** | ✅ aynen |
| **3.2** | şartname çelişkileri — 5 hüküm | **§D.2** | ✅ aynen |
| 3.3 | faz numaralandırma disiplini | **§E.1** (dördüncü ad alanı eklendi) | ✅ |
| 3.4 | kayıp blokların dürüst kaydı (11) | **§II-0** | ✅ `[TEYİT BEKLİYOR]` |
| 4.1 | `MetricDefinition` | **FAZ 2.2** | ❌→✅ *"router'a dokunmaz"* **düzeltildi** |
| 4.2 | cold-start metrik önerisi | **FAZ 3.6** | ✅ + göz-ikonu |
| 4.3 | `RouteDecision` / red gerekçesi | **zaten yapıldı** | ⚠ bayat |
| 4.4 | mali takvim | **FAZ 2.6** | ✅ |
| 5.1 | meta-güven şeridi | **zaten yapıldı** (`/stats/today` + `HelpPanel:30,66-68`) | ⚠ bayat |
| **5.2** | **`llm_guard.safe_call()` tekilleştirmesi** | **FAZ 1.2b** | ✅ *(sürüm 1'de `✅ FAZ 7` diyordu — **gövdede yoktu**)* |
| **5.3** | Pareto grafik | **FAZ 7.3/l** | ✅ *(sürüm 1'de gövdede yoktu)* |
| 6.1 | hayalet seri (`find_previous` + `previous_result`) | **FAZ 5.13/a** | ✅ |
| 6.2 | kişisel memories / sunum tercihi | **II-F.9** (`tip="tercih"`) | ✅ |
| 6.3 | hedef/plan kıyası | **FAZ 2.5** | ✅ |
| 6.4 | Knowledge Center — **kural yarısı `app/rules.py`** | **FAZ 5.13/b** | ✅ |
| 7.1 | iş bağlamı kütüğü + `SurecAdimi` | **II-F.1** | ✅ |
| 7.2 | varlık kartları + BOM + sözleşme | **II-F.2** | ✅ + **PANIC uyarısı** |
| 7.3 | kurumsal takvim | **II-F.3** | ✅ |
| 7.4 | sahiplik + tazelik SLA + Bakım Ajanı | **II-F.4** | ✅ `[TEYİT: 5.12]` |
| 7.5 · 7.6 | sözlük · **görev motoru + 8. konuşma türü** | **II-F.5 · II-F.6** | ✅ |
| 7.7 | sabah brifingi | **II-F.7** (v1 hâli: 5.9) | ✅ |
| 7.8 | departman + genel çift görünüm | **FAZ 2.3** | ✅ |
| 7.9 | bildirim yorgunluğu — **4 adımlı kapı** | **FAZ 5.9** | ✅ |
| **8.1** | orkestrasyon + **plan dondurma** | **FAZ 6.4** | ✅ *(sürüm 1'de gövdede yoktu)* |
| 8.2 | `sec()` + **`Arac.ozet` 4 bileşen** | **FAZ 6.3** | ⚠ `sec()` **zaten var** → kapsam daraldı |
| **8.3** | araç portları (`get_sample`/`explain_plan`/`recall`) | **FAZ 6.3** | ✅ |
| **8.4** | DataProcessor → **`stats.trend`/`ozet` + tekilleştirme** | **FAZ 5.15** | ✅ *(sürüm 1'de yoktu)* |
| 8.5 | kök-neden / varyans ayrıştırma | `contribution.py` **zaten var** | ✅ |
| 8.6-8.9 | 4 katmanlı doğrulama · plan listesi · hata sınıflandırma · **token ekseni** | **FAZ 6.4** | ✅ |
| 8.10 | refleks yayı | **FAZ 6.4** | ✅ `[TEYİT: 4.17]` |
| 8.11 | çok-grafikli kompozisyon | **FAZ 5.12** | ✅ |
| 9.1 · 9.2 | şirket profili · bağlam enjeksiyonu (**~800 token**) | **II-F.8** | ✅ + *"veri kazanır"* |
| 9.3 | **seçici yazma — 6 kriter** | **II-F.10** | ✅ |
| 9.4 | **öncelik çözücü** | **II-F.9 KAPI** | ❌→✅ *"en spesifik kazanır"* **tersine çevrilmişti, düzeltildi** |
| 9.5 · 9.6 | içerik tipi + **4 getirme stratejisi** · 7 katman | **II-F.9** | ✅ `[TEYİT: 5.11]` |
| 9.7 · 9.8 | unutma · **kişisel şeffaflık** | **II-F.11 · II-F.12** | ✅ |
| 10.1 | tahminleme + **toplanabilirlik kapısı** | **II-D.2** | ✅ |
| 10.2 | what-if + **döngü reddi** | **II-D.3** | ✅ |
| 10.3 | kohort — **5 parametre** | **II-D.4** | ✅ |
| 10.4 · 10.5 | karne/SWOT (**FK + BAN**) · skor kartı | **II-D.5 · II-D.6** | ✅ |
| 10.6 | **nedensellik grafı** | **II-D.1** (`app/graf.py` **ortak dataclass burada**) | ✅ `[TEYİT: 6.13, 6.15]` |
| 10.7 · 10.8 | karbon-başabaş · Karar Kaydı v1 | **II-D.7 · II-D.8** | ✅ |
| 10.9 · 10.10 | pod'lar · gelişim yol haritası | **II-D.9 · II-D.10** | ✅ `[TEYİT: 6.12, 6.14]` |
| 11.1 · 11.2 | emsal yokluğu · **üç blok + CDD + DQ en-zayıf-halka + DMN reddi** | **II-E** girişi + II-D.1 | ✅ |
| 11.3-11.5 | çerçeveleme · **seçenek İCAT ETMEZ** · **9 kriter** | **II-E.1/2/3** | ✅ |
| 11.6 | **kanıt matrisi** + duyarlılık | **II-E.4 · II-E.6** | ✅ |
| 11.7 · 11.8 | Karar Rozeti · **ikili arama** kırılma noktası | **II-E.8 · II-E.5** | ✅ |
| 11.9 | Karar Kaydı — **16 alan sayıldı** + `imzalayan_id` | **II-E.7** | ✅ `[TEYİT: 6B.15]` |
| 11.10-11.12 | kırmızı çizgi · şablonlar · Telos/OKR | **II-E.9/11/10** | ✅ `[TEYİT: 6B.13]` |
| 11.13 · 11.14 | hakem · kalkan | **II-H.1 · II-H.2** | ✅ `[TEYİT: 6B.14, 6B.16]` |
| 12.1 | metrik sertifikasyonu (+`lineage_set_hash`, `metric:certify`) | **FAZ 1.5** | ✅ |
| 12.2 | column-level lineage (**6 değerli `donusum_tipi`**, 3 şablon cümle) | **FAZ 1.6** | ✅ |
| 12.3 | freshness ladder | **FAZ 1.7** | ❌→✅ **`hata`=sayı gösterme** kuralı **tersine çevrilmişti, düzeltildi** |
| 12.4 | audit şeması (OTel + PROV-O + hash zinciri) | **FAZ 1.8** | ✅ |
| **12.5** | **RLS sertleştirmesi** | **FAZ 1.1 — ÖNE ALINDI** | ✅ sıra düzeltildi |
| 12.6 | numeric fidelity | **FAZ 1.9** | ⚠ öncül yanlış (**yetim değil**), iş geçerli |
| 12.7 · 12.8 | eskalasyon · kademeli düşüş | **FAZ 1.10 · 1.11** | ✅ `[TÜRETİLDİ]` |
| 12.9 | AI Act / NIST / ISO | **FAZ 1.12** | ✅ **Md.50 yürürlükte** |
| 13.1 | İçgörü Paketi | **FAZ 5.12** | ✅ |
| 13.2 | onay durum makinesi — **5 tüketici** | **FAZ 6.1** | ✅ + süre aşımı & risk yönlendirmesi |
| **13.3** | **kanıt sınıfı `AskResponse.kanit_sinifi`** | **FAZ 1.12** | ✅ *(sürüm 1'de "7.8 tohum" diyordu, **alan adı geçmiyordu**)* |
| 13.4 | görsel IR (Vega-Lite) | **§D.1** — ADR-0024 korunur | ✅ |
| 14.1 | sektör paketleri + `PaketOverride` + **kurulum akışı** + **sapma metriği** | **II-G.1** | ✅ |
| 14.2 · 14.3 | versiyonlama (**3 durum**) · madencilik (**7 adım**) | **II-G.2 · II-G.3** | ✅ |
| 14.4 | VQR yönetişimi + **terfi regresyon kapısı** | **II-G.4** | ✅ |
| 14.5 | **Terfi Motoru** + `puanla()` formülü | **II-G.5** | ✅ `[TÜRETİLDİ]` |
| 14.6 · 14.7 | kredi (+**önbellek**) · çok-tenant | **II-G.6 · II-G.7** | ✅ |
| **15.1** | **5 grafik tipi** (sankey/pareto/bubble/gauge/harita) | **FAZ 7.3/l + II-D** | ✅ *(sürüm 1'de gövdede yoktu)* |
| 15.2 · 15.3 | embed (`EmbedToken` alanları, **Looker DEĞİL**) · public API | **FAZ 6.5** | ✅ |
| 15.4 | yazma araçları + `geri_alma_fonksiyonu_ref` | **FAZ 6.2** | ✅ |
| 15.5 | kanal kimlik eşlemesi | **FAZ 6.6** | ✅ |
| 15.6 | **ne zaman grafik çizilmez** | **FAZ 5.11** | ✅ |
| 16 | **24 yeni tablo** | fazlara dağıtıldı — **EK K'de tam liste** | ✅ |
| **17** | araç kaydı 12→~32 | **FAZ 6.3** — taban **15**, hedef **26@v1 / 37@v3** yeniden sayıldı | ✅ *(sürüm 1'de gövdede sayım yoktu)* |
| 18 | Plan 2 sözleşme eşlemesi | **EK B** | ✅ 18/19; tek boşluk **§12.6 → II-H.3** |
| 19 | ön-hizalama (19.1-19.6) + **`openapi-typescript`** | **§A.2 + FAZ 7.0 + EK C** | ✅ |
| 20 | fazlama A-H | **§B + Bölüm II** | ✅ düzeltilerek |
| 21 | doğrulama (7 madde) | **EK C** | ✅ |
| 22 | kaynaklar | **EK F** | ⚠ **8 iddia `[DOĞRULANMADI]`** |

> **Sonuç: Plan 3'ün 22 bölümünün 22'si karşılığını buldu.** Altı madde **düzeltilerek**
> (4.1 · 9.4 · 12.3 · 12.5 sırası · 12.6 öncülü · 17 tabanı), on bir madde
> **`[TEYİT BEKLİYOR]`**, sekiz dış iddia **`[DOĞRULANMADI]`**. **Plan 3 iptal edilebilir.**

## EK B — Plan 2 ↔ bu belge

| Plan 2 § | Nerede |
|---|---|
| 3.1-3.3 rotalar · **komut paleti** · **landing/boş-durum** | **FAZ 7.3/b, 7.3** |
| 3.11 · 4.3 **Capability Explorer** | **FAZ 7.3/c** |
| 4.1 kayıt/davet/**e-posta doğrulama**/şifre sıfırlama | **FAZ 7.3/h** |
| 4.2 kurulum sihirbazı · **göz-ikonu** · **anında değer** | **FAZ 3.6 · 7.3/g** |
| **5.1 cevap kartı anatomisi + İçgörü Kartı** | **FAZ 7.3/a** |
| 5.2 düşünme adımları | mevcut `liveTrace` + FAZ 6.4 |
| **5.3 Hızlı↔Derin** | **FAZ 5.14** |
| **5.4 Kök Neden Haritası** (+ön-skorlama, her grafikten drill, yol diyagramı) | **FAZ 7.3/d,e,f** |
| 5.5 · 5.6 anlatım · **skill kaydet** | FAZ 1.9 · II-F.9 (`prosedürel`) |
| 6.1-6.4 grafik tipleri · **İçgörü Paketi** · palet | **FAZ 5.11 · 5.12 · 7.2 · 7.3/l** |
| 7.1 tuval · **7.2 rapor yapısı** · **7.3 pano + drift bandı** · 7.4 **WhatsApp + gönderim durumu** · 7.5 hedef · **7.6 Bilgiye kaydet** | **FAZ 7.3/i,j,k · 5.13b · 5.9 · 2.5 · 5.13/c** |
| 8.1-8.7 iş bağlamı · bakım ajanı · brifing · kapsam · bildirim · **hafıza şeffaflığı** · **çakışma çözücü** | **II-F** (kapsam: **FAZ 2.3**; çakışma: **II-F.9 KAPI**) |
| 9.1-9.8 karne · **tahmin görseli** · **what-if etkileşimi** · **kohort normalizasyonu** · **CEO günlüğü** · karar memosu · pod · nedensellik | **II-D** |
| 10.1-10.9 Karar Motoru (+**ağırlık kaydırıcısı**) | **II-E** |
| **11.1-11.19 güven ve yönetişim** | **FAZ 1.5-1.8 + 7.8** *(Plan 2'de **fazsızdı** — 7.0/1)* |
| **11.4 DCM modu** | **FAZ 7.11** |
| 12.1-12.9 `/settings` · sinonim · terfi · **gelişim paneli** · **sağlık skoru** · copilot · **kredi+önbellek** | **FAZ 7.7 · II-G.5 · II-G.6 · II-H.3** |
| 13.1-13.5 embed · **beyaz etiket** · operatör · sesli · **portföy** | **FAZ 6.5 · 7.3/m** |
| 14.1-14.5 tasarım sistemi · tipografi · modal · ikon · responsive | **FAZ 7.2 · 7.5 · 7.6** |
| **16.1 dal/bayrak usulü + token göçü + 7 yasak** | **§A.2 + FAZ 7.0/4 + EK C** |
| 17.1-17.3 doğrulama (V-1…V-7) | **EK C** |

## EK C — Doğrulama kapıları (birleşik)

**Backend (Plan 3 §21 · B4-B10):**
1. **Regresyon** — tam süit yeşil
2. **B4 sınır-değer testleri** — her dürüst-red eşiği: **eşik−1'de RED, eşikte ÜRETİM**
3. **B7 araç kaydı** — her yeni araç kayıtlı + **izin matrisinde tanımlı bir aksiyona bağlı**
4. **B8 tanım-hash çürümesi** — `MetricDefinition` değişince bağlı sertifika/VQR/karar
   taslağı `yeniden_dogrulama_gerekli`'ye düşüyor (**canlı** doğrulanır)
5. **B9 cache güvenlik bağlamı** — farklı `security_context` → **farklı `cache_key`**;
   **tenant A token'ıyla tenant B verisi 0 satır**
6. **B10 arka plan kimliği** — `principal=None` ile arka plan koşumu **reddediliyor**
7. **Yetim-uç kapısı** — bu planın eklediği hiçbir uç, tüketilmeden "bitti" sayılmaz
8. **Uygulama-sonrası ölçüm** — her faz **önce/sonra** karşılaştırması

**Frontend (Plan 2 §17):**
* **V-1** uç-tüketim (⚠ `admin_app` için **BUGÜN KIRMIZI OLMALI** → FAZ 7.7'de yeşile döner)
* **V-2** responsive duman testi (**375 / 768 / 1024**)
* **V-3** token sızıntı lint'i (`no-arbitrary-tailwind`)
* **V-4** dürüstlük-dili taraması (*"Dima karar verdi"* **yasak**)
* **V-5** 🔴 **bayrak-kapalı regresyon** — *"strangler fig'in **tüm güvenliği** buna dayanır
  — **gözle kontrol yeterli sayılmaz**"*
* **V-6** bayrak temizlik borcu — **kalan her kalıntı bir sonraki fazın başlama koşulu**
* **V-7** kullanıcının kendi ölçütü

**Birleştirme (E-1…E-4):** backend süiti yeşil (**salt frontend işi olsa bile**) · TS strict
+ yeni bileşenin testi · **bayrak `off` iken birebir eski davranış** · dürüstlük denetimi
(**veri yokken "veri yok" yazılır, boş grafik çizilmez**).

**Entegrasyon (K1-K5):** yetim uç (**tam yol**) · yetim alan (**iç içe + diğer modeller +
🔴 ERİŞİLEBİLİRLİK**) · **ters yetim** · **yüzey sadakati** · **panel sayısı**
(**önce TANIM**, §C/11 kutusu: *export* sayımı → v1: **13** · v2+: **15**).
⚠ *Sürüm 3'te bu satır **"v1: 11 · v2+: 13"** diyordu — §C/11 (**12**) ve 0.14/K5 (**11**)
ile birlikte **üç yerde üç farklı sayı**. Ölçümle tek tanıma indirildi.*

**Deneyim (S1-S9) — `lab/deneyim.py`, §F.1:** çapa · anlat · süreklilik · … · **`S8`
görünürlük** (*cevabın taşıdığı her gövde alanı RENDER edilebilir bir dala düşer* → **0.23**)
· **`S9` kapanış** (*netleştirmeye verilen cevap TIKLAMA ve YAZMA aynı rapora çıkar* →
**0.5b**).
🔴 **Bu süit tek başına YETMEZ:** API cevabını ölçüyor, render'ı değil — `S8`/`S9`
eklenene kadar **K2 ile aynı yanlış-pozitifi** üretir (§F.1).

**Tip sözleşmesi:** **`openapi-typescript`** ile `/openapi.json`'dan tip üretimi
(geliştirme-zamanı; **yeni çalışma-zamanı bağımlılığı DEĞİL**). `api-client.ts` **723 satır
elle yazılmış** — Plan 3 bunu *"ön-hizalamanın **en büyük riski**"* diye adlandırıyor.

## EK D — Sayısal eşikler (tek yerde)

> Kural D2: **canlı büyüyen sayılar burada yoktur** — komutla ölçülür.

**Dürüst red (B4):** trend **<5 nokta** · tahmin **<12 ay** · anomali **<4 nokta** ·
etki **<100 gözlem (durum başına <10)** · kohort **<30**.
**Tahmin:** MASE **<1.0** · Holt-Winters min **m+5** (aylık **17 nokta**) · **2-11 satır →
`seasonal_naive`** · kısmi son dönem **dışlanır**.
**Tazelik:** `warn_after` = **2× beklenen periyot** · `error_after` = **5×** ·
🔴 `hata`/`bilinmiyor` → **sayı gösterilmez**.
**Anlatı:** `narration_guard` **±%2**.
**Adım doğrulama:** `satır=0` · **`null_orani>%90`** · **mertebe sapması ≥100×** · aynı hata
imzası **2. kez → strateji değiştir**.
**Onay:** süre aşımı **30 dk** · `risk="geri_alinamaz"` → **senkron**.
**Karar:** **3 hızlı / 9 tam** · **9 kriter / 100 puan** (dağılım II-E.3) · duyarlılık
**+%10/+%20/+%30** · kırılganlık **<%5 kırılgan · %5-10 orta · >%10 sağlam** · kırılma
noktası ikili arama toleransı **%0,5**.
**Kohort:** min **30** · min opaklık **~%10** · metin beyaza dönüş **~%40 doygunluk**.
**Grafik-çizilmez:** **≤2 satır VEYA ≤3 kategori** → cümle · **>20 kategori** → tablo.
**Opaklık token'ları (PK-13):** tam belirgin **1** · soluk **0,75** (+ renk-körü-güvenli
ikinci kanal: ince sol kenarlık/glif) · devre dışı **0,38** + kap **0,12** + `not-allowed`.
**Kredi:** sohbet **1** · rapor **4** · agentic **6** · artefakt **8**; model ×1/×2/×3;
**başarısız → yakılmaz**; **altın yol + önbellek = 0**.
**Bağlam:** profil özeti **~800 token** · açılış panosu **4-6 widget** · brifing **5 slot**.
**Terfi:** `puanla()` = `0.4×etki + 0.3×güven + 0.2×tazelik + 0.1×maliyet_tasarrufu`.
**UX:** Excel **10bin/60sn** · brifing **30sn** · DCM **3 tık** · dal ömrü **≤1 hafta** ·
kök-neden kardeş sınırı **7 (+N daha)** · SWOT **150 karakter** · chip **3-5** · adım
**3-6** · karne **6 metrik** · rota **4→10-12** · panel **13 (v1) / 15 (v2+)** — 🔴 **tanım
zorunlu, §C/11** *(sürüm 4'te bu satır hâlâ "11/13" diyordu: **beşinci kopya**, ve EK D'nin
kendi iddiası "sayısal eşikler **tek yerde**" — kopya sayısı bir eşik değil, bir **bayatlama
yüzeyi** sayısıdır)*.
**Ölçek:** tenant başına **10-40 MB** · **500+ tenant** tek süreçte `[DOĞRULANMADI]`.
**CI gerileme:** `nl_corpus` erişim **−1 puan** · doğru-cube **−0,5 puan**.
🔴 **GECİKME (0.17 — sürüm 2'de HİÇ YOKTU):** `cube` p95 **<1,5 sn** · `intent` p95
**<6 sn** · `discovery` p95 **<20 sn**. Ölçülmüş taban: Discovery **12.567 ms** ↔ cube
**145-434 ms** (**30-85×**). **Kural:** bir bayrak *"gecikme"* gerekçesiyle `off` kalacaksa
**gerekçe SAYI TAŞIR**.
🔴 **ÖLÇÜM BÜTÇESİ (0.16):** `lab/` koşucusu başlarken kalan kota **raporlar**; kota < eşik
→ **koşmaz** (fail-closed). Ölçüm konteynerleri **adlandırılır ve açıkça kapatılır**.
🔴 **SEMANTİK VAKA PAYDASI (0.19):** her metrik **iki paydayla** — **ham tur** ve
**`(cube, ölçü, niyet)`**; ikisi **ters yöne giderse KIRMIZI**.
🔴 **ONAY YORGUNLUĞU (6.1):** **istem sayısı/tur** telemetriye yazılır; **artarsa kırmızı**.
🔴 **UÇTAN UCA (4.8):** **n≥100**, tutulmuş küme; **10 puanın altındaki fark gürültüdür**
(anotasyon hata oranı literatürde **%52,8-62,8**).
**Canlı sınır:** **10 sn'de 10 istek**; Intent turu **3 çağrı** → **tur arası 5 sn**.
**FAZ 8.1:** **≥300 gerçek tur**.

## EK E — Bayrak kaydı  *(faza göre — denetim düzeltmesi: sürüm 1 önek'e göre gruplamıştı)*

**Kural:** her bayrak `FLAG_REGISTRY` **ve** `demo/packs/features.yml`'de; her biri **ölçüm
tarihi** taşır; **`off` kalanların gerekçesi yazılır**. **Ölü bayrak = yetim.**

| Faz | Bayraklar |
|---|---|
| 🔴 **MEVCUT — bu belge YARATMIYOR, KARAR VERİYOR** *(sürüm 3'te **hiçbiri listede yoktu**; §C/10 *"ölü bayrak → 0"* diyor ama **evleri yazılı değildi** — sohbet raporu §10 yakaladı, ölçüm **kapsamı genişletti**)* | **`off` (4):** `t2_anlatici` → **§F.2** (ertelendi, **planı yazılı**) · `agent_plan_secimi` → **0.22 + 0.16** (önce hata, sonra ölçüm) · `prompt_enhancer` → **FAZ 2** (kapsam kaldıracıyla birlikte ölçülür) · `netlestirme_onceligi` → **0.4** (ölçüm kararı) ·· 🔴 **kayıtta var, `features.yml`'de YOK (2):** `ask_async_discovery` → **§A.4/a(1)** · `threaded_chat` → **§A.4/a(1)** *(ikisi de *"BİLEREK eklenmedi"* beyanı taşıyor ve **birbirine atıf yapıyor** — biri açılırken ötekinin gerekçesi güncellenir)* |
| **FAZ 0** | `netlestirme_onceligi` *(zaten `off` — 0.4 ölçüm kararı)* · **`capa_zinciri`** *(0.5)* · 🔴 **`netlestirme_kapanisi`** *(0.5b — **AYRILDI**, aşağıdaki kutu)* · **`metrik_kaydi`** *(0.18 — sürüm 4'te yanlışlıkla FAZ 2'deydi)* · `sosyal_sinif` |
| **FAZ 1** | `motor_rls` · `motor_cls` · `metrik_sertifikasi` · `lineage` · `tazelik` |
| **FAZ 2** | `cekirdek_katman` · **`ui_metrik_yonetimi`** *(2.2b — sürüm 4'te yanlışlıkla FAZ 3'teydi)* · **`ayni_grain_gocu`** *(ayrıldı — S7)* · `kapsam_mercegi` + `ui_kapsam_anahtari` · `hedef_kiyasi` |
| **FAZ 3** | `ossie_ithal` + `ui_ossie_ithal` · `coldstart_metrik` |
| **FAZ 4** | `ossie_ihrac` · `mcp_yuzeyi` |
| 🔴 **§G · AJAN** | **`calisirken_sorma`** *(AJ3b — **kuzey yıldızının davranış testi**)* · **`adim_zinciri`** *(AJ5b — **bileşik sorunun ön koşulu**)* · **`diyalog`** *(AJ0b — **§G'nin ilk maddesi**, deterministik)* · `referans_dili` *(AJ2)* · `agent_plan_secimi` *(AJ5 — **MEVCUT bayrak**, bu belge yaratmıyor: açıyor ve ölçüyor)* · `bilesik_rapor` *(AJ6)* · **`tur_yoneticisi`** *(AJ3 — `deterministik\|ajan`, **§G'nin tek geri alma yolu**)* · `oturumlar_arasi_hafiza` *(AJ4)* ·· **bayraksız:** `AJ0` (MIMARI §5'in 18. yasağı) · `AJ1` (iddia kapısı — fail-closed, bayrak taşımaz) ·· ⚠ `yol_siniri` **bayrak değil, kullanıcı tercihidir** (`AskRequest` alanı, Faz F2) — `tur_yoneticisi` ile **karıştırılmaz** |
| **FAZ 5** | `tur_takip` · `tur_paylas` · `peer_kiyasi` · `kanal_slack` · `kanal_whatsapp` · `sabah_digest` · `kpi_pin` · **`hizli_derin`** · `ui_icgoru_paketi` · `ui_knowledge_center` · **`netlestirme_duzeyi`** *(5.16 — varsayılan `normal` = bugünkü davranış)* |
| **FAZ 6** | `onay_akisi` + `ui_operator` · `yazma_araclari` · `public_api` · `embed` · `kanal_kimlik` |
| **FAZ 7** | `ui_komut_paleti` · `ui_landing_kesif` · `ui_kok_neden_haritasi` · `ui_kurulum_sihirbazi` · `ui_kayit_akisi` · `ui_sifre_sifirlama` · `ui_settings_tam_sayfa` · `ui_pano_surukle_birak` · `ui_pano_adi_modal` · `ui_sesli_giris` · `ui_kanit_gorunurlugu` · `ui_gelisim_paneli` · `ui_saglik_skoru` · `ui_sinonim_yonetimi` · **`ui_dcm_modu`** · `ui_embed` |
| **II-D** | `ui_nedensellik_grafi` · `ui_tahmin` · `ui_what_if` · `ui_kohort` · `ui_karne_karti` · `ui_swot_karti` · `ui_skor_karti` · `ui_surdurulebilirlik_seti` · `ui_departman_podlari` · **`ui_ceo_gunlugu`** |
| **II-E** | `ui_karar_motoru` (7 bileşen — **birlikte anlamlı**) · `ui_karar_kaydi` · `ui_karar_memosu` |
| **II-F** | `ui_is_baglami_sihirbazi` · `ui_is_baglami_kartlari` · `ui_kurumsal_takvim` · `ui_sabah_brifingi` · `ui_hakkimda_bilinenler` · **`tur_gorev`** |
| **II-G** | `sektor_paketi` · `ui_terfi_kuyrugu` · `ui_kredi_paneli` |
| **II-H** | `ui_departman_hakemi` · `ui_sistem_copilot` *(Z3'ün **UI'ı YOK** — KD-18)* |

> ⚠ **Denetim düzeltmesi (T4):** `ui_karne_karti` · `ui_karar_motoru` · `ui_karar_memosu` ·
> `ui_terfi_kuyrugu` sürüm 1'de **hem FAZ 7 hem Bölüm II** listesindeydi — §C onları
> **v1 kapsamı dışında** ilan ediyor. **Hepsi Bölüm II'ye taşındı.**
>
> ⚠ **Plan 3 §19.3'ün 5 bayrak adı bilinçle değiştirildi** (kayıt için):
> `ui_tahmin_bandi`→`ui_tahmin` · `ui_kohort_isi_haritasi`→`ui_kohort` ·
> `ui_is_baglami`→ikiye bölündü · `ui_hafiza_seffaflik`→`ui_hakkimda_bilinenler` ·
> `ui_karar_kaydi_v1`→`ui_karar_kaydi`. **Yol haritası kazanır**, ama değişiklik **kayda
> geçti** (§19.2/4'ün *"yeni bayrak açılmaz"* kuralı bu belgeden itibaren geçerlidir).

## EK F — Kaynaklar

**Doğrulanmış (bağlantılı):**
- [Apache Ossie (eski OSI) — dbt Labs](https://www.getdbt.com/blog/osi-is-now-apache-ossie)
- [Open Semantic Interchange — spesifikasyon](https://github.com/open-semantic-interchange/OSI/blob/main/docs/index.md)
- [Semantic Layer for AI Agents 2026 — Cube (*compile-time governance*)](https://cube.dev/articles/semantic-layer-for-ai-agents-2026)
- [Cube — Concepts / Views (belirsiz join yolu hakemliği)](https://cube.dev/docs/product/data-modeling/reference/view)
- [dbt — semantic models (entity adı **tekil, GRAIN'den**)](https://docs.getdbt.com/best-practices/how-we-build-our-metrics/semantic-layer-3-build-semantic-models)
- [LLMs Get Lost In Multi-Turn Conversation (ICLR 2026)](https://arxiv.org/abs/2505.06120)
- [What Predicts Correctness in Text-to-SQL? Selective-Prediction](https://arxiv.org/html/2607.06799v1)
- [TRUSTSQL](https://openreview.net/pdf?id=7ZeoPg3eTA) · [Reliable End-to-End Text-to-SQL (EDBT 2026)](https://openproceedings.org/2026/conf/edbt/paper-177.pdf)
- [BIRDTurk (SIGTURK 2026)](https://arxiv.org/abs/2602.03633)
- [HITL: onay bir buton değildir](https://digitalthoughtdisruption.com/2026/07/12/human-in-the-loop-ai-agent-approval-paths/)
- [Progressive disclosure — analitik ajanlar](https://thepipeandtheline.substack.com/p/progressive-disclosure-the-core-pattern)
- [Semantic Layer + MCP](https://www.polaranalytics.com/post/mcp-semantic-layer-ai-analytics)
- `arXiv:2411.07451` — tablo/grafik/metin tercihi (~50.000 yanıt, %41,7 vs %36,3)
- `arXiv:2509.08646` — Secure Plan-then-Execute (plan dondurma)
- `lineage.rs:146` — Rust PANIC (repo içi, `WrenAI-main/core/wren-core/core/src/mdl/`)

**Plan 3 §22'den kurtarılan kaynaklar** *(kaynak plan silineceği için buraya taşındı —
denetimin *"8 iddia öksüz kalır"* uyarısının kapatılması)*:

| İddia | Kaynak | Nerede kullanılıyor |
|---|---|---|
| **AI Act Md.12/19** (≥6 ay log) | https://artificialintelligenceact.eu/article/12/ | FAZ 1.12 |
| **AI Act Md.50** (AI içerik işaretleme) | https://artificialintelligenceact.eu/article/50/ | FAZ 1.12 |
| **dbt: semantic layer vs text-to-SQL** (8-16 puan) | https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026 | FAZ 4.7 |
| **Alarm fatigue** (%72-99 yanlış-alarm) | https://array.aami.org/doi/full/10.2345/0899-8205-46.4.268 | FAZ 5.9 |
| **LLMCompiler** (3,7× gecikme / 6,7× maliyet) | https://arxiv.org/pdf/2312.04511 | FAZ 6.4 |
| **Secure Plan-then-Execute** (plan dondurma) | https://arxiv.org/abs/2509.08646 | FAZ 6.4 |
| **Cube multitenancy** (tenant başına MB, ölçek) | https://docs.cube.dev/embedding/multitenancy | II-G.7 |
| **Snowflake Verified Query Repository** (inceleme yükü / VQR yönetişimi) | https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/verified-query-repository | II-G.4 · II-G.5 |
| **Prophet fiyaskosu** | https://valeman.medium.com/the-facebook-prophet-fiasco-a-cautionary-tale-of-data-science-hype-041384d6f119 | II-D.2 |
| **Nixtla StatsForecast vs Prophet** (~500× hız) | https://nixtlaverse.nixtla.io/statsforecast/docs/experiments/prophet_spark_m5.html | II-D.2 |
| **Hyndman & Kostenko** (minimum örnek boyutu) | https://robjhyndman.com/papers/shortseasonal.pdf | II-D.2 |
| **FPP3 — forecast reconciliation** (MinT) | https://otexts.com/fpp3/reconciliation.html | II-D.2 |
| **Cube cohort/retention recipe** | https://docs.cube.dev/recipes/data-modeling/cohort-retention | II-D.4 |
| **Mixpanel retention primer** (satır-içi normalizasyon yanıltıcılığı) | https://mixpanel.com/blog/retention-analytics-primer/ | II-D.4 |
| **OMG DMN 1.6** (bilinçle reddedildi) | https://www.omg.org/spec/DMN/1.6/Beta1/About-DMN | II-E |
| **Decision quality** (en-zayıf-halka) | https://en.wikipedia.org/wiki/Decision_quality | II-E |
| **Causal Decision Diagrams** (üç düğüm sınıfı) | https://www.theuncertaintyproject.org/tools/causal-decision-diagrams-cdd | II-D.1 · II-E.7 |
| **OpenLineage object model + column lineage facet** | https://openlineage.io/docs/spec/object-model · https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet/ | FAZ 1.6 |
| **W3C PROV-DM** | https://www.w3.org/TR/prov-dm/ | FAZ 1.8 |
| **OTel GenAI semantic conventions** | https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/ | FAZ 1.8 |
| **dbt source freshness** | https://docs.getdbt.com/reference/resource-properties/freshness | FAZ 1.7 |
| **Power BI endorsement** (sertifika kademeleri) · **Tableau Data Quality Warnings** | https://learn.microsoft.com/en-us/fabric/fundamentals/endorsement-promote-certify · https://help.tableau.com/current/server/en-us/dm_dqw.htm | FAZ 1.5 · 7.8 |
| **Snowflake row access policies** · **Cube RLS** | https://docs.snowflake.com/en/user-guide/security-row-intro · https://docs.cube.dev/docs/data-modeling/access-control/row-level-security | FAZ 1.1 |
| **MCP security best practices** | https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices | FAZ 4.5 |
| **Looker Blocks** (sektör paketi deseni) | https://docs.cloud.google.com/looker/docs/blocks | II-G.1 |
| **dbt model versions** (breaking/non-breaking) | https://docs.getdbt.com/docs/mesh/govern/model-versions | II-G.2 |
| **Snowflake — mining query history** | https://www.snowflake.com/en/blog/engineering/mining-query-history-to-build-better-semantic-models-for-ai/ | II-G.3 |
| **Snowflake Cortex Analyst doğruluk kıyası** (BIRD %57→%78) | https://atlan.com/know/snowflake/cortex-analyst-vs-text-to-sql/ | FAZ 4.7 |
| **Proof-Carrying Numbers** · **Know Your Limits (abstention survey)** | https://arxiv.org/pdf/2509.06902 · https://aclanthology.org/2025.tacl-1.26.pdf | FAZ 1.9 · 4.2 |

🔴 **Kalan `[DOĞRULANMADI]` — 2 iddia** (kural D3):
1. **Microsoft: *"Slack e-postası Teams hesabına güvenilir eşlenemez"*** — **FAZ 6.6'nın tek
   gerekçesi**. Plan 3 §22'de karşılığı yok. → **Uygulamadan önce birincil kaynak bulunmalı**;
   bulunamazsa madde *"admin onaylı eşleme"* gerekçesiyle **kendi başına** savunulur
   (kimlik eşlemesini tahmin etmemek zaten B4 disiplinidir).
2. **Tenant başına 10-40 MB / 500+ tenant tek süreçte** — Cube dokümanı ölçek ilkesini
   veriyor ama **bu iki sayıyı** doğrulamıyor. → II-G.7'de **kendi ölçümümüz** yapılır
   (`lab/tenant_bellek.py`), sayı **oradan** gelir.

## EK G — SÖZLÜK *(yeni geliştirici için)*

| Terim | Ne |
|---|---|
| **`R1`…`R10`** | `cube_router.py:2554-2566` red kodları. **R1** = cube eşleşmedi (ölçü sinonimi var ama sahibi belirsiz) · **R4** = çapraz-konu · **R10** = kapsam kapısı (tanınmayan kelime) |
| **KURAL A** | *"Taban önce alınır"* — `nl_corpus_baseline.json` dondurulur, her faz ona karşı ölçülür |
| **KURAL B** | *"Canlı cevap yolunu değiştiren her faz kendi kapatma bayrağını taşır ve bayrak kapalıyken davranış **birebir** bugünküdür (testle kilitli)"* |
| **ADR-0007-K3** | *"Dönem eksikse **SOR**, sessizce tüm-zaman alma"* — §C/3'ün kırmızı çizgisi |
| **ADR-0008** | *"Anlamadığını bil"* — tek tanınmayan kelime ⇒ cevap yok **ve öneri yok**; **kelimeye özel yama yasak** |
| **ADR-0018** | Sinonim mimarisi 3 katman; **LABEL ⊆ SYNONYM**; **adaylar otomatik canlıya çıkmaz** |
| **ADR-0019** | Her yerde **soft delete** — kanıt silinmez |
| **ADR-0024** | **Görselleştirme kararı deterministik ve backend'e ait** |
| **T1 / T2** | LLM sınırının iki katmanı: **T1** = sorgu üretimi (şema adları + `normal` enum'lar) · **T2** = yorum/sohbet (PII maskeli **agrege** sonuç) |
| **grain** | Bir tablonun **bir satırının ne olduğu** (*"bir vardiya × makine"*). Cube'un `base_object`'i **tek bir grain**'dir |
| **fan-out** | Bir join'in satırları **çoğaltması** → toplamları şişirir. **Sertifika** = ölçülmüş anahtar tekilliği (`app/fanout.py`, `target/fanout_certificate.json`); üç durum: `olculdu:saglikli` / `olculdu:riskli` / **`olculmedi`** |
| **yetim uç / alan** | Backend'de üretilen ama **frontend'de hiç tüketilmeyen** uç/alan. **TERS yetim** = frontend'in beklediği ama backend'in vermediği |
| **`YANLIŞ-OK`** | `nl_corpus`'ta **gürültüye SQL üretme** — cevap verilmemesi gereken soruya cevap |
| **`sec()` · `Kosum` · `kapisiz` · `dis_maliyet`** | `planner.py`: plan **önerici** · koşum makbuzu · *"bu adım dört kapıdan geçmedi"* itirafı · kayıtsız adımın beyan edilen maliyeti |
| **`_syn_hit` · `_uncovered` · `_covers`** | `cube_router`'ın kelime eşleştiricileri; sınır **`(?<![a-z0-9])`** (Python'da `_` kelime karakteri olduğu için `\b` **değil**) |
| **`_takilan_kelimeler`** | Kapsam kapısına takılan kelimeler — terfi kuyruğunun girdisi |
| **`always_filter`** | Cube-düzeyi zorunlu `WHERE` (LookML `sql_always_where`); **fail-closed** |
| **`strict_sql_policy`** | Motorun 45 veri-okuyucu TVF'yi bloklayan politikası; `off\|shadow\|on` — **FAZ 1.1 bu disiplini örnek alır** |
| **`consistency_k`** | Intent-JSON'ın k örnek alıp kanonik `CubeQuery` üzerinde **oylaması**; **bir güven skoru DEĞİL** |
| **G5 · G10** | `compose()`'un fail-closed kapıları: **G5** = büyük/küçük harf ad çakışması · **G10** = `always_filter` taşıyan modele join (**34M TL** sızıntı ölçüldü) |
| **`⟳`** | `MIMARI.md`'de **düzeltme/yürürlükteki değişim** işareti |
| **`api-only`** | Frontend tüketicisi olmayan uç — **gerekçesiyle** `test_uc_yetim_degil.py::API_ONLY`'ye yazılır |
| **strangler fig** | Yeni bileşen bayrak arkasında eskisinin **yanında** yaşar; `prod`'a çıkınca eski **silinir** |

## EK H — **PANEL / KATMAN KURALLARI (PK-1…PK-24)** *(Plan 2, tam liste)*

| # | Kural |
|---|---|
| **PK-1** | *"Yeni özellik yeni panel doğurmaz."* Her yetenek cevabın **KENDİ kartında**, **kademeli açılım** olarak |
| **PK-2** | Panel yalnız **KALICI ARTEFAKTLAR** için: pano · zamanlanmış rapor · bağlantı · inceleme |
| **PK-3** | Kural **FAZ 6/6B/7/8'in HER özelliği** için geçerli — karar matrisi, SWOT, güven rozeti **yeni panel AÇMAZ** |
| **PK-4** | **Gezinme minimal kalır, menü şişmez.** Keşif **komut paleti + bağlamsal chip**'lerle |
| **PK-5** | **Gerekçeli istisna 1 — `/settings`:** `admin_app`'in 13 router'ı *"kalıcı, idari, sohbet-dışı"* = PK-2'nin istisna sınıfı. Çözüm **yeni panel değil, mevcut çekmecenin TAM SAYFAYA TERFİsi** |
| **PK-6** | **Gerekçeli istisna 2 — `/decisions`:** kalıcı artefakt; gerekçe **aranabilir arşiv**. *(Ayrıca genel ilke: **asla gizleme** — düşük sinyalli öge soluk gösterilir, kaldırılmaz)* |
| **PK-7** | **Komut Paleti YENİ PANEL DEĞİLDİR** — hiçbir yüzeyin yerini almaz |
| **PK-8** | **`/onboarding` ayrı rota AÇILMAZ** — `/` içinde bir MOD'dur |
| **PK-9** | **Kök Neden Haritası MODAL DEĞİL** — cevabın altında **inline açılan ağaç**; tıklama yeni sekme/modal **açmaz**, ağacı **büyütür** |
| **PK-10** | **Panoda ayrı drill mekanizması YAZILMAZ** — AYNI `KokNedenHaritasi` |
| **PK-11** | **Kohort hücresi yeni modal İCAT ETMEZ** — mevcut `ContractDetailPanel` |
| **PK-12** | **Gradient eğrisi ayrı rapor sayfası DEĞİL** — aynı kartta katlanır panel |
| **PK-13** | **Sinyal ağırlıklandırma:** koyu/soluk **ölçülen sinyale** göre (ön-skorlama, FAZ 7.3/d). *"Soluk ama tıklanabilir"* ile *"devre dışı"* **ASLA aynı token'ı paylaşmaz** |
| **PK-14** | **Sabah brifingi yeni ekran DEĞİL** — landing'in varyantı |
| **PK-15** | **CEO Günlüğü yeni buton EKLEMEZ** — aynı *"Rapor oluştur"* akışının tematik varyantı |
| **PK-16** | **Skill kaydetme yeni panel değil** — mevcut alt-şeridin maddesi |
| **PK-17** | **Bağlam Bakım Ajanı yeni ekran açmaz** — bildirim olarak |
| **PK-18** | **Sistem copilot `/settings` ekranlarının YERİNE geçmez, ÜSTÜNE biner** |
| **PK-19** | **Senaryo karşılaştırmasında üçüncü "karşılaştırma modu" İCAT EDİLMEZ** — seçici çoklu-seçime izin verir |
| **PK-20** | **Kanıt-kökeni paneli GENİŞLEMEZ** — kasıtlı olarak **üç kısa cümle** |
| **PK-21** | **İki ayrı bileşen YAZILMAZ:** SEVİYE/DEĞİŞİM = aynı ağacın iki modu; What-if / Kök-neden / Açıklanabilirlik = **aynı grafın üç render modu** |
| **PK-22** | Rota hedefi: **4 → ~10-12** (*"hâlâ az, menü şişmez"*) |
| **PK-23** | 🔴 **(YENİ)** Panel tavanı **sürüme bağlıdır**: **v1 = 13** · **v2+ = 15** (`WhatIfPaneli` + `DuyarlilikPaneli` **gerçek panellerdir**). `test_panel_sayisi` sürüme göre kilitlenir. ⚠ **TANIM ZORUNLU** — §C/11'in kutusu: **export** sayımı (`export default` **dahil**), dosya sayımı **değil**. *(Sürüm 3'te bu satır "11/13" diyordu; ölçüm **13/15** verdi — belgede dördüncü kopyaydı, dördü de hizalandı.)* |
| 🔴 **PK-24** | **(YENİ — sürüm 5)** **YÜZEY KIRPMASI YASAĞI: bir cevabın garantisi, gösterildiği yüzeye göre değişemez.** Aynı `AskResponse` hangi yüzeyde açılırsa açılsın **`source` rozetini, `explain`'i ve makbuz erişimini** taşır; bir yüzey *"dar"*, *"gömülü"* ya da *"özet"* olduğu için bunları **düşüremez**. Düşürmek bir tasarım tercihi değil, **MIMARI §5 ihlalidir** (*"bir cevabın `source`'unu gizlemek/eşitlemek"*). **Kapısı K4** (`test_yuzey_sadakati.py`) |

> ⚠ **PK-24 sürüm 4'te ATIF ALIYORDU ama TANIMLI DEĞİLDİ** (madde 0.3 → EK H `PK-23`'te
> bitiyordu). Belgenin kendi avladığı *"beyan var, kod onu tanımıyor"* sınıfının **belge-içi
> hâli** — ve `PK-23`'ün kendi metni *"dördü de hizalandı"* derken çok-kopya kayması panel
> sayısı için çözülmüş, **burada duruyordu**. Kural artık yazılı; **D5'in kapısı** bu sınıfı
> bir daha kaçırmaz.
> **Ölçülmüş üç örneği** (üçü de aynı sınıf): `AnalysisCanvas` rozet basmıyor (**0.3**) ·
> `ReportPanel` gövde alanlarını render dalına hiç göndermiyor (**0.23**) · konuşma
> cevabında `next_steps` **bilerek** gizli ama netleştirmede **kazara** gizli (**0.23**).

## EK I — **A11Y KURALLARI (A11Y-1…10)** *(Plan 2, tam liste)*

| # | Kural |
|---|---|
| **A11Y-1** | İşlevsel kontrol **asla yalnız emoji** olamaz |
| **A11Y-2** | **Her etkileşimli öge bir `aria-*` etiketi taşır** |
| **A11Y-3** | **Modaller focus trap uygular** |
| **A11Y-4** | **Emoji · `window.prompt()` · isimsiz ikon ASLA birincil etkileşim yüzeyi olamaz** |
| **A11Y-5** | Komut paleti **tamamen klavyeyle** işletilebilir (↑/↓/Enter/Esc); fareye zorunlu bağımlılık yok |
| **A11Y-6** | **Klavye gezinme tüm çekmece/modallerde test edilir** |
| **A11Y-7** | Her **ikon-only buton** `aria-label` taşır |
| **A11Y-8** | Rail ikonları: `aria-label` + hover tooltip + masaüstünde kısayol ipucu |
| **A11Y-9** | **Renk tek kanal olamaz** — PK-13'ün soluk kademesi **ikinci, renk-körü-güvenli kanal** (kenarlık/glif) taşır |
| **A11Y-10** | Kohort hücre metni **~%40 doygunluğun üstünde beyaza döner** — kontrast otomatik |

## EK J — **KAPSAM DIŞI (KD-1…KD-23)** *(kalıcı kayıt)*

| # | Ne | Gerekçe |
|---|---|---|
| **KD-1** | **şartname FAZ 8B** — ERP sembiyozu + agentic veri girişi | **Kullanıcı kararı**: *"kendi başına büyük bir yazma-yetkisi/onay akışı konusu"* |
| **KD-2** | **şartname FAZ 9B/10/11/12/12B/13** — Kurumsal Bilgi Hub'ı · Canlı Akıl · Külli Akıl | **v4-v6 nihai vizyon** |
| **KD-3** | `/brand` sayfası | iç/pazarlama — değişmez |
| **KD-4** | Thread/composer mimarisinin yeniden tasarımı | **Zaten uygulanmış ve doğrulanmış** |
| **KD-5** | İkinci frontend klasörü/projesi | dört kopyalanamaz katman |
| **KD-6** | Yeni üçüncü-parti bileşen kütüphanesi | mevcut elle-yazılmış desen korunur |
| **KD-7** | Yeni bayrak sistemi | `app/features.py` + `FLAG_REGISTRY` kullanılır |
| **KD-8** | Yeni drill/kök-neden motoru | mevcut `drill.*` kalır, **yalnız SUNUM değişir** |
| **KD-9** | Ayrı akış-diyagramı motoru | II-D.1'in ortak grafı kullanılır |
| **KD-10** | Ayrı pano-özel drill mekanizması | aynı `KokNedenHaritasi` |
| **KD-11** | Kohort için ayrı drill-down modalı | `ContractDetailPanel` |
| **KD-12** | Üçüncü "karşılaştırma modu" | seçici çoklu-seçim |
| **KD-13** | **Teknik lineage grafiği (iş kullanıcısına)** | *"hiçbir BI ürününün iş-kullanıcısına gösterdiği iyi bir graf-görünümü yok"* → **üç kısa cümle** |
| **KD-14** | Tersine soru eğrisi için yeni backend ucu | **istemci tarafında** hesaplanır |
| **KD-15** | Yeni animasyon motoru (what-if canlı boyama) | mevcut React state yeterli |
| **KD-16** | Yeni bağımlılık (pano sürükle-bırak) | **`@dnd-kit` zaten kurulu** |
| **KD-17** | Uzun ömürlü `develop`/`ui-redesign` entegrasyon dalı | strangler fig usulü |
| **KD-18** | **Anayasal Kalkan'ın ayrı UI'ı** | dar kapsam; yalnız eskalasyona *"ikinci C-level onayı"* olarak yansır |
| **KD-19** | Şartnamenin teknoloji yığını (NestJS/Redis/Vault/BullMQ/Temporal/LangGraph/Novu/Vega-Lite) | **§D.1** — gerçek yığın tek Python-FastAPI + ECharts |
| **KD-20** | **LLM'in grafik tipi seçmesi · sürücü formülü yazması · hangi adayın önemli olduğuna karar vermesi** | hepsi **deterministik** kalır |
| ⟳ **KD-21** | ~~Netleştirme/ret metnini LLM'e yazdırmak~~ → 🔴 **KAPSAM DIŞI DEĞİL ARTIK: §G/AJ1 tam olarak bunun kapısını kuruyor** | Kayıt **silinmiyor** — *neden kapsam dışıydı* ve *hangi kapı onu kapsam içine aldı* birlikte duruyor (ADR-0019). **Kapının şartı aynen geçerli:** AJ1 olmadan LLM netleştirme yazamaz |
| 🔴 **KD-23** | **Webde dolaşıp sektör bilgisi getirmek** *(kullanıcı isteği, 2026-08-03)* | **Farklı bir GÜVEN SINIFI** — aşağıdaki kutu. **v4+**, ve *bir özellik değil, doğrulanabilirlik mimarisinin yeniden tasarımı* |
| **KD-22** | **Deterministik aşama betiği** (*"+400ms katalogda arıyorum…"*) | Sayılar gerçek değil (küp yolu **145–434 ms**, MIMARI §2.2) **ve** senaryolanmış zamanlamayı ilerleme diye göstermek **kalibre edilmemiş güven rozetiyle aynı ailedendir** → §A.4/**a** |

> 🔴 **KD-23 — WEB: neden bir özellik değil, bir mimari karar.**
>
> **İddia kapısının (AJ1) çalışma prensibi:** *metindeki her katalog sözcüğü
> `service.schema()`'da bulunmalı.* Ama **"tekstil sektörü geçen yıl %8 büyüdü"** iddiasının
> doğrulanacağı **şema yoktur**. 🔴 **Web bilgisi, sistemin TÜM doğrulama makinesinin
> dışında kalır** — `narration_guard` sayıyı küple eşleştiremez, `iddia.py` sözcüğü katalogda
> bulamaz, makbuz bir `contract_id` gösteremez.
>
> **Belge bu ayrımı zaten yapmış** (§D.2/3): sektör kıyası için *"havuz altyapısı kurulur
> (**k-anonimlik kapısı**), kıyas **ÇIKTISI bayrak arkasında KAPALI**"* — yani **beyan ile
> teslim ayrılmış**. Doğru karar.
>
> **NE GEREKİRDİ:** dış bilginin **ayrı bir kanıt sınıfı** olarak etiketlenmesi
> (`PROBABILISTIC_CONTEXT` — §D.2/5'in PDF/OCR hükmüyle aynı desen), **ayrı rozet**, ve
> *"bu sayı küpten gelmiyor"*un **cevabın gövdesinde** yazması. Bu yapılmadan web'i açmak,
> ürünün **tüm kesinlik iddiasını çürütür** — bir Discovery cevabından **çok daha kötü**,
> çünkü Discovery hiç değilse **müşterinin kendi verisini** okuyor.
> ⚠ **Yeniden açılma koşulu:** `PROBABILISTIC_CONTEXT` sınıfı **tasarlanıp kapıya
> bağlandığında** — o zaman bu kayıt `⟳`'ye döner (KD-21'in yaptığı gibi).

> 🔴 **KD-21 — RAKAMSIZ UYDURMA: bu belgenin en ince kapsam-dışı kaydı.**
>
> **NEDEN OLMAZ (ölçüldü @`c4b14d1`):** `narration_guard`'ın kendi docstring'i —
> *"Sayı **İÇERMEYEN** cümleler geçer: bu kapı **sayı uydurmasını** engeller, **üslubu
> değil**"* — ve `izinli_degerler(None) == []`. Yani `result=None` olan bir netleştirme
> turunda guard **her rakamsız cümleyi KOŞULSUZ geçirir**. Mevcut kapıya **hiçbiri
> takılmaz**:
> - *"Fire verisi 2019'dan beri kayıtlı."* → **şema iddiası** (yıllar zaten doğrulanmıyor)
> - *"Bu tür sorularda genelde ay bazlı bakılır."* → **dayanaksız norm iddiası**
> - *"İstersen tedarikçi kırılımı da ekleyebilirim."* → 🔴 **YETENEK iddiası** — o boyut
>   yoksa kullanıcı *"olsun"* der ve **sistem çuvallar**
>
> Bu, *"akıcı ama uydurma"*nın **kısıt 1'in ÖLÇMEDİĞİ** hâlidir — ve tam olarak bu ürünün
> kimliğine (*"hiçbir sayı uydurulmaz"*) saldırdığı için, sayı olmaması onu **masum
> yapmıyor**.
>
> **NE GEREKİRDİ:** ayrı bir **İDDİA KAPISI** — metindeki her küp/ölçü/boyut sözcüğü
> `service.schema()` içinde **bulunmalı** + **izinli söz-edimi beyaz listesi**.
> ~3-4 gün + korpus. **Açılacaksa KENDİ maddesi ve KENDİ kapısıyla açılır**, bir üslup
> iyileştirmesinin yan ürünü olarak değil.
> → Bağlayıcı sonucu: **FAZ 5.17 deterministik kalır** ve **§F.2**'nin `t2_anlatici` planı
> netleştirmeye **açılmaz**.

**+ Kalıcı olarak kapsam dışı (bu belgenin eklediği):** yerel LLM'i ölçü/cube seçiminde
kullanmak (ölçüldü: **ciddi gerileme**) · **sektör küpleri** (katalog büyümesi doğruluğu
**düşürüyor** — [KANIT §8.1]) · **retrieval'lı hafıza** (+14/−16) · **SHAP** ·
**Prophet** · **tam planlama modeli (Anaplan/Pigment)** · **BigQuery TimesFM
(DEĞERLENDİRİLMEDİ)** · **derin öğrenme tahmin** (~25.000× maliyet).

## EK K — 24 yeni control-plane tablosu → hangi faz

`MetricDefinition`→2.2 · `MetricTarget`→2.5 · `MetrikSertifikasi`→1.5 · `KolonKokeni`→1.6 ·
`EskalasyonKurali`→1.10 · `EmbedToken`→6.5 · `KanalKimlikEslemesi`→6.6 ·
**`OnayTalebi`**→6.1 · `ŞirketBaglami`→II-F.1 · `SurecAdimi`→II-F.1 · `UrunKarti`→II-F.2 ·
`TedarikciKarti`/`MusteriKarti`→II-F.2 · `SozlesmeKaydi`→II-F.2 · `SozlukTerimi`→II-F.5 ·
`Gorev`→II-F.6 · `ŞirketProfili`→II-F.8 · `HafizaKaydi`→II-F.9 · `Graf`/`SurucuDugumu`→II-D.1
· `ForecastContract`→II-D.2 · `Senaryo`→II-D.3 · `SkorKartiSablonu`→II-D.6 ·
`EmisyonFaktoru`→II-D.7 · `DepartmanPodu`→II-D.9 · `PaketOverride`→II-G.1 ·
`TerfiAdayi`→II-G.5 · `KrediHareketi`→II-G.6 · `PolitikaKurali`→II-E.9.
**Genişleyen mevcut tablolar:** `DecisionRecord`(II-E.7) · `VerifiedQuery`(II-G.4) ·
`InteractionLog`/`AuditLog`(1.8, 6.4) · `TenantConfig`(1.7, 2.6, II-F.3, II-G.7) ·
`AskResponse` şeması(1.7, 1.12, 5.13/a) · `Principal`(II-E.9) · `Schedule`(1.1b) ·
`NotificationPreference`(5.9 — **ilk tüketicisi**).

---

## EK L — DIŞ DENETİMİN İŞLENMESİ: kabul · değiştirme · **ret** kaydı

> Kaynak: `~/.claude/plans/u-anda-bir-plan-tingly-fox.md` (835 satır, dış gözle mimari +
> plan denetimi). **14 v1 düzeltmesi + 4 Bölüm II düzeltmesi + 6 MIMARI çelişkisi.**
> **Reddedilen madde silinmez, gerekçesiyle kayda geçer** (EK J deseni).

### L.1 · Bu oturumda **kodla doğrulanan** iddialar

| İddia | Sonuç | Kanıt |
|---|---|---|
| `agent_plan_secimi` açılırsa **`UnboundLocalError`** | ✅ **DOĞRU** | `migration_trace` `:2878` girinti **8** (blok içi) ↔ `:3177` girinti **4** (blok dışı) → `:3179` okuyor |
| **K1** makbuz katmanlı değil | ✅ | `<details\|<summary>` → **tüm frontend'de 0** |
| **K2** kalibre edilmemiş güven **yüzdeyle** basılıyor | ✅ **ve sanılandan kötü** | `ChatPanel.tsx:16-27` + `answer.py:84-92` sabit kodlu yol etiketi |
| **K3** `sinifla` yanlış blokta | ✅ | tek çağrı `:2933`, `if structural_followup:` (`:2862`) içinde |
| **K4** panel **12**, `test_panel_sayisi` **yok** | ✅ **ama sayı TANIMA BAĞLI** *(sürüm 4'te ayrıştı)* | `ls *Panel.tsx \| wc -l` → **12** (dosya) ↔ `export …Panel` → **13**; `find tests -name "*panel*"` → **boş**. §C/11'in tanım kutusu bu satırın üstündedir |
| `enforce_query` **koşulsuz `return` stub** | ✅ | `authorize.py`, `# TODO(faz-2)` |
| `lab/kapi.py --tam` var, **CI çağırmıyor** | ✅ | `grep -rn "kapi.py" .github/workflows/` → boş |
| **M2** MIMARI §7 hâlâ *"%64"* | ✅ | satır 2567 · 2571 · 2630 |

### L.2 · **Kabul edilenler** — nereye işlendi

`D1`→**0.15** · `D2`→**0.16** · `D3`→**0.17 + EK D** · `D4`→**0.18 + 2.2b** · `D5`→**FAZ 8
girişi** · `D6`→**0.19** · `D7`→**§C/13-16 + 4.8 + §C/11 onarımı** · `D8`→**3.0** ·
`D9`→**6.1'in dördüncü parçası** · `D10`→**7.8/K2** · `D11`→**7.8/K1** · `D12`→**0.20 +
0.21** · `D13a`→**1.2** · `D13b`→**6.5 P0 kapısı** · `D13c`→**1.3c** ·
`E1`→**II-0** · `E2`→**II-F.9** · `E3`→**II-D girişi** · `E4`→**II-H girişi** ·
`M1-M5`→**−1.1/A9-A13** · `K3`→**5.0** · **UnboundLocalError**→**0.22** ·
`enforce_query`→**1.3b**.

### L.3 · 🔴 **DEĞİŞTİRİLEREK kabul** — bir madde

**`D14` (netleştirme ayarı).** Öneri: *"`kapali` seçilirse eksik dönem **varsayılanla**
cevaplanır ve varsayım `explain.assumptions`'da görünür."*
**Ret gerekçem:** bu, MIMARI'nin avladığı **sessiz-yanlış sınıfının ta kendisidir** —
`explain.assumptions` bir **tooltip**tir, cevabın gövdesi değil. **Üç sertleştirmeyle kabul
edildi** (5.16): varsayım **cevabın gövdesinde**; ayar **tenant-admin'e kilitli + audit**;
`kapali` düzeyinde cevap **`kanit_sinifi="probabilistik"`** taşır.

### L.4 · ⚠ **Doğrulanmadan uygulanmayacaklar** — iki iddia

| İddia | Neden bekliyor |
|---|---|
| **MCP `elicitation` spec sürümü** (6.1/3) | Denetim *"9 Ara 2025 LF · rev 2026-07-28"*, [KANIT §2.7] *"Agentic AI Foundation · 2025-11-25"* — **ikisi birden doğru olamaz**. Hizalamadan önce doğrulanır |
| **Wren RLS gömülü panoları kapsamıyor** (6.5/D13b) | Belge atfı var, **bu oturumda doğrulanmadı**. **P0 olarak işaretlendi** ve 6.5 başlamadan önce Wren dokümanı + davranış **birlikte** sınanır |

### L.5 · Denetimin **kabul edilmeyen çerçevesi** — kayıt için

Denetim *"planlar uygulanınca **mükemmelleşmez**"* diyor ve gerekçesi doğru. **Ama bir
nokta düzeltilmeli:** denetimin `B5` maddesi (*"efor/süre tahmini sıfır"*) bir **kusur
olarak** listeleniyor. **Bu bilinçli bir karardır ve öyle kalır** — bu depo tahmin
üretmiyor, **ölçüm** üretiyor (MIMARI §5: *"beyan değil ölçüm"*). Efor tahmini eklemek,
`interpret.py`'nin *"`target:` beyanı HİÇBİR cube'da yok"* dürüstlüğünün tersini yapmak
olurdu. **Sıralama** önceliklendirmeyi **ölçülmüş kazançla** yapar (D4 tam olarak bunun
örneğidir), adam-günle değil.

---

## EK M — SOHBET DENEYİMİ RAPORUNUN İŞLENMESİ *(ikinci dış rapor)*

> Kaynak: `~/.claude/plans/SOHBET-DENEYIMI-RAPORU_2026-08-03.md` (715 satır, `@71b542e`).
> **10 bulgu (B1-B10) · 6 madde (M1-M6) · 3 kendi kusurunun düzeltmesi · 1 kesilen madde.**
> Çıkış noktası bir kullanıcı şikâyeti: *"chat akmıyor, konuşma şeklini almıyor, beni
> anlamıyor, robotik."*
>
> 🔴 **Raporun en güçlü tarafı:** kendi sayımını **iki kez düzeltmiş** ve *"payda ELLE
> SAYILMAZ"* dersini **kendi yazarına** uygulamış. Buna rağmen **hiçbir iddiası kanıtsız
> kabul edilmedi** — onu da doğruladım.

### M.1 · Kodla **yeniden ölçülen** iddialar — 10/10 doğrulandı

Hepsi @`c4b14d1`, **bu belgenin kendi ölçümüyle** (raporun sayılarına güvenilmedi):

| Bulgu | Sonuç | Bu oturumdaki kanıt |
|---|---|---|
| **B1** ölü render dalı | ✅ **DOĞRU** | `ReportPanel.tsx` `it.result \|\| it.kpi` → **2 isabet (`:122`, `:185`)** · `ReportCard.tsx:833` `item.result \|\| item.contribution` · `ask.py:1750` `source=None`, `result` **yok**, `contribution`+`prescription` **dolu** · `grep next_steps ReportPanel.tsx` → **0** |
| **B2** K2 yanlış-pozitif | ✅ **DOĞRU** | `test_cevap_alani_yetim_degil.py`: `ad not in metin` — **düz alt-dize varlığı**, erişilebilirlik **sorulmuyor** |
| **B3** netleştirme bağlanmıyor | ✅ **DOĞRU, betikle yeniden üretildi** | Kendi ayrıştırıcım: `source=None`+`note`+öneri taşıyan **14** dal → iliştiren **3**, iliştirmeyen **11**. `1750` (konuşma dalı) çıkarılınca **iliştiren 2** (`:1903`·`:1913`), `2553` (`yol_siniri`) çıkarılınca **iliştirmeyen 10**. **Raporun iki kriteri de birebir çıktı** |
| **B4** 0.5'in engeli kalktı | ✅ **DOĞRU** | `grep "capalar=" ask.py` → **0**; `reply_to_cube_query` **yalnız `:1466` yorumunda** geçiyor |
| **B5** `interpret.py` ham kolon adı | ✅ **DOĞRU** | `{measure}`/`{dim}`/`{m0}` doğrudan f-string'de; `eylem.py:234-243`'ün karşı-örneği ve gerekçesi **birebir** |
| **B6** ~25 dağınık metin, karışık hitap | ✅ **DOĞRU** | `ask.py` **"sen"** (15 isabet) ↔ `eylem.py:296` *"kastettiğ**iniz**i"* |
| **B7** `liveTrace` kurulu ve ölü | ✅ **DOĞRU (3/3)** | `features.yml`'de `ask_async_discovery` → **0** · `liveTrace` **yalnız** `page.tsx:395` → `ChatPanel` · `pollAskJob`'un `setTimeout`'u döngü **başında** |
| **B8** `narration_guard` yetkisiz | ✅ **DOĞRU** | Docstring **birebir**: *"Sayı İÇERMEYEN cümleler geçer … üslubu değil"* |
| **B9** `t2_anlatici` yapısal olarak ulaşamaz | ✅ **DOĞRU** | `answer.py`: `resp.result is None and resp.kpi is None → return` · `not yorum or yorum.get("narration") → return` |
| **B10** deneyim süiti render'ı ölçmüyor | ✅ **DOĞRU** | `lab/deneyim.py` **var** (20.509 B), yol haritasında **hiç geçmiyordu** |

### M.2 · Kabul edilenler — nereye işlendi

`M1`→**0.23** *(+ K2'nin (c) boyutu)* · `M2`→**0.10b** *(yeni madde; 0.10 satırı ona
bağlandı)* · `M3`→**5.17** *(⚠ raporun önerdiği `5.16` **doluydu** — aşağıda)* ·
`M4`→**0.5b** *(+ `lab/netlestirme_paydasi.py`)* · `M5`→**§A.4/a'nın üç maddesi + kendi
taban kapısı** · `M6`→**EK J / KD-21** · kesilen aşama betiği→**EK J / KD-22** ·
`B4`→**0.5'in NEDEN bloğu** · `B9`→**0.16'nın SONUÇ notu + §F.2** ·
`B10` + `S8`/`S9`→**§F.1** *(deneyim süiti ilk kez tanıtıldı)* · raporun §8'i→**§F.3** *(yeni
bölüm)* · `t2_anlatici`→**EK E'nin `MEVCUT` satırı + §F.2**.

### M.3 · 🔴 **Değiştirilerek kabul — üç madde**

| # | Rapor ne dedi | Ne yapıldı | Gerekçe |
|---|---|---|---|
| **1** | `M3` → **`5.16`** | **`5.17`'ye alındı** | `5.16` **zaten `netlestirme_duzeyi`** (D14'ün değiştirilerek kabulü, L.3). Numara çakışması §E.1'in ad-alanı disiplinini kırardı |
| **2** | `B3`'ün paydası: *"10 ya da 11"* | **Betik iki dışlamayı da YAZAR** | Rapor `yol_siniri`'yi (`:2553`) doğru dışlıyor ama 🔴 **`ask.py:1750`'yi görmüyor**: o dal `cube_query=prev_cq` **iliştirdiği için** mekanik filtreye *"iliştiren"* diye takılır — oysa **netleştirme değil, cevabın kendisi** (B1'in dalı). Bu belgenin **kendi ölçümünden** çıktı; betik onu dışlamazsa **payda şişer ve kapı yanlış yerde yeşil verir** |
| **3** | `§9/1`: *"§C/11 **11** diyor, ölçüm **13**"* | **Tanım kutusu yazıldı; §C/11 VE K5 birlikte düzeltildi** | Rapor **bayat okumuş** (§C/11 zaten *"12"*e çekilmişti) **ama asıl noktası haklıydı**: ben iki tanımı da koştum — **dosya 12 · export 13**, **ikisi de doğru**. Fark `NotificationsPanel`'in `NotificationsBell.tsx`'te ve `TercihlerPanel`'in `export **default**` olmasından. Ve ortaya **belgenin kendi iç çelişkisi** çıktı: §C/11 *"12"*, K5 *"11"* diyordu |

### M.4 · ⚠ Raporun **düzeltilen** iki ayrıntısı *(iddiaları değil, gerekçeleri)*

1. **`TercihlerPanel` *"çalışma ağacında"* değil, HEAD'de.** Rapor *"HEAD'de 12, TercihlerPanel
   çalışma ağacında"* diyor; ölçüm: dosya **`71b542e`'de commit'li** (Faz E commit'i).
   Yani **HEAD'de 13 export var**, geçici bir durum değil. *(Kirli dosya listesi de
   değişmişti: rapor 5 dosya ilan etmiş, ölçümde 6 — `lab/kapi.py` de değişmiş.)*
2. **`ask_async_discovery` yalnız değil.** Rapor tek bayrak sayıyor; ölçüm **iki** buldu —
   `threaded_chat` de kayıtta var, YAML'de yok, **aynı *"BİLEREK eklenmedi"* beyanını**
   taşıyor **ve doğrudan `ask_async_discovery`'ye atıf yapıyor**. → M5'in *"beyanı da
   güncelle"* uyarısı **iki dosya-bloğuna** birden uygulanır (§A.4/**a**).

### M.5 · Raporun **kabul edilen çerçeve düzeltmesi** — ve neden önemli

Rapor, şikâyetin **teşhisini** düzeltiyor ve bu belge onu benimsiyor:

> *"Şikâyet doğru, **teşhisi yanıltıcı**. Sistem çoğu zaman **anlıyor** (%69,8 doğrudan
> cevap). Robotiklik üç yerden geliyor ve üçü de **«anlamama» değil**:*
> *(1) ürünün konuşma yeteneği **hesaplanıyor ve ekrana hiç çıkmıyor** (**0.23**)*
> *(2) sistem **sorduğunu hatırlamıyor** — chip'e tıklarsan çalışır, yazarsan çalışmaz
> (**0.5b**)*
> *(3) ekranda **iç adlar** ve dağınık, hitabı karışık ~25 sabit metin (**0.10b** ·
> **5.17**)."*

**Bu, [KANIT §11]'in tavan düzeltmesinin deneyim eksenindeki karşılığıdır:** orada
*"%35 kapsam boşluğu"* çürütülmüştü; burada *"sistem beni anlamıyor"* çürütülüyor.
**Her ikisinde de kusur gerçek, ama teşhis yanlıştı — ve yanlış teşhis yanlış maddeye
para harcatır.** `t2_anlatici`'yi *"deneyimin kalbi"* sanmak (§F.2) tam olarak bu hatanın
örneğiydi.

### M.6 · Sıra — raporun önerisi **ölçümle birlikte** kabul edildi

| Sıra | Madde | Gerekçe |
|---|---|---|
| **1** | **0.23** | Hiçbir şeye bağımlı değil · backend'e **yalnız kapı testiyle** dokunuyor · geri alması `git revert` · **üç bitmiş özelliği** geri getiriyor. *Bekletmek için sebep yok.* |
| **2** | **0.10b** ∥ **§A.4/a(1-3)** | Çakışmıyorlar (backend etiket / frontend+YAML). **0.10b, 5.17'nin ön koşulu** |
| **3** | **5.17** | **0.10b'den SONRA zorunlu**: ham kolon adlarıyla beslenen metin robotikliği **taşır, kaldırmaz**. En yüksek **test** riski burada (`note` metnine assert eden altın testler) |
| **4** | **0.5b** | 🔴 **TEK BAŞINA, kendi ölçüm turuyla.** `CLARIFY:dönem` payını hareket ettirebilecek **tek madde** (netleştirmeye `cube_query` iliştirmek `structural_followup`'ı tetikleyebilir). Diğerleriyle birleşirse **sapmanın SAHİBİ bulunamaz** — [KANIT §8.3]'ün `elektrik` dersi |

**Bonus — 0.5b'nin İDDİA EDİLMEYEN kazancı:** netleştirmeye `cube_query` iliştirmek daha
çok turu `structural_followup` yapar → `followup.sinifla` (bugün **yalnız** o blokta
çağrılıyor — **5.0/K3**) daha çok turda **erişilebilir** olur. **Kazanç olarak iddia
edilmiyor**, ama **riskin kaynağı da bu** — maddenin tek başına inmesinin sebebi budur.

---

## EK N — BÜTÜNLÜK DENETİMİNİN İŞLENMESİ *(iki bağımsız rapor, belgenin KENDİSİNE)*

> Öncekilerden farkı: bu iki rapor **ürünü değil, bu belgeyi** denetledi — numara çakışması,
> yetim atıf, taşıma kaydı, şablon uyumu, defter tutarlılığı. **Bulguların neredeyse hepsi
> düşünce hatası değil, büyük bir birleştirmeden kalan defter kaymasıydı** — ve tam da bu
> yüzden tehlikeliydi: hiçbiri okurken göze çarpmıyor, hepsi uygulanırken patlıyor.
>
> 🔴 **Kabul edilmeyen bulgu: YOK.** İkisinin de her maddesi **doğrulandı**; ikisi
> **genişletildi** (aşağıda), biri **düzeltildi**.

### N.1 · 🔴 Üç kritik — hepsi doğrulandı ve kapatıldı

| # | Bulgu | Doğrulama | Kapatılış |
|---|---|---|---|
| **1** | **v1 kapısı bir v3 maddesine bağlı** — §C/9 *"8 tür"* ister, 8.'si (`tur_gorev`) **II-F.6 = v3**; §B *"v2'ye geçiş için §C'nin 16 ölçütü yeşil"* der → **döngüsel kilit, v1 asla kapanamaz** | ✅ `tur_gorev` yalnız II-F satırında; 5.1/5.2 v1'de, 8. tür **yok** | **§C/9 → v1 = 7 tür.** Gerekçe belgenin **kendi ölü doğuş yasağı**: `tur_gorev`'in motoru (`Gorev` tablosu) II-F'de doğuyor; sınıflandıran ama **eyleme geçemeyen** tür, yasağın ta kendisi olurdu. *Alternatif (türü bölmek) açıkça reddedildi* |
| **2** | **8.2 üç kayıt, üç farklı gerçek** — iki yer *"taşındı"* derken üçüncüsü maddeyi **tam metniyle** barındırıyor | ✅ `:1355` ve `:2128` *"taşındı"*; `### 8.2 · Müşteri DB'sinden…` **duruyor** | **Kütük yazıldı** + 8.3 kendi maddesine ayrıldı. Ve asıl çözüm **mekanik**: 🔴 **kural D5** — *taşınan madde eski yerinde **her zaman** bir kütük bırakır*, **kapısıyla** birlikte |
| **3** | **Deneyim süitinin BİLEREK AÇIK KIRMIZI'sı absorbe edilmemiş** — *"o ayı makine bazında aç"* | ✅ `a5942c7` commit gövdesinde birebir | **§F.3/7** — ve **0.5b'nin İLAN EDİLMİŞ SINIRI** olarak: çapa **cevap düzeyindedir, satır düzeyinde değil** |

### N.2 · 🔴 Dördüncü kritik — **ikinci rapordan, ve ilkinin görmediği**

**Paylaşılan bayrak ↔ ayrı ölçüm turu: çelişki.** EK E `capa_zinciri`'yi *"tek bayrak, iki
madde (0.5 ve 0.5b)"* diye not düşmüştü; ama EK M.6/4 *"0.5b **TEK BAŞINA**, kendi ölçüm
turuyla"* diyor. **Tek bayrak iki bağımsız ölçüm turu veremez** — iki senaryo da kırık:
0.5 önce inerse 0.5b **kapısız canlıya çıkar**; birlikte inerlerse **`CLARIFY:dönem`
sapmasının sahibi bulunamaz**. İkisi de [KANIT §8.3]'ün `elektrik` dersinin ihlali.
→ **`netlestirme_kapanisi` ayrıldı** (0.5b), `capa_zinciri` 0.5'te kaldı; **iki bayrak, iki
bağımsız geri alma, iki ayrı ölçüm turu.**

### N.3 · ⚠ Defter kaymaları — hepsi kapatıldı

| Bulgu | Ölçüm | Düzeltme |
|---|---|---|
| **FAZ 2.2 silinmiş, kütük yok** | **22 atıf** boşluğa düşüyordu | Kütük + **5 yanıltıcı atıf** (*"2.2'nin hakemi"* gibi) **0.18**'e yönlendirildi |
| **2.2b'nin KAPI/GERİ AL'ı 0.18'in kopyası** | `KAPI: test_metrik_kaydi.py` · `GERİ AL: metrik_kaydi=off` — ikisi de 0.18'in; bayrağı ise `ui_metrik_yonetimi` | 2.2b'ye **kendi NASIL/KAPI/SONUÇ/GERİ AL'ı** yazıldı. *Aksi hâlde 2.2b, 0.18'in testiyle "bitti" sayılırdı — **kapı yanlış maddeyi yeşile boyar*** |
| **EK E'de iki bayrak yanlış fazda** | `metrik_kaydi` FAZ 2'de (maddesi 0.18 = FAZ 0) · `ui_metrik_yonetimi` FAZ 3'te (maddesi 2.2b = FAZ 2) | İkisi de **evine** taşındı |
| **EK D'de panel hâlâ 11/13** | **beşinci kopya** — üstelik EK D'nin iddiası *"eşikler tek yerde"* | **13/15** + tanım atfı. *Sürüm 4'ün kapanışı "dördü de hizalandı" diyordu; **beşincisi kaçmıştı** — ve bu, D5'in kapısının neden gerektiğinin kanıtı* |
| **`PK-24` atıf alıyor, tanımlı değil** | madde **0.3**, EK H `PK-23`'te bitiyor | 🔴 **PK-24 YAZILDI** — *yüzey kırpması yasağı*, kapısı **K4**; ölçülmüş üç örneğiyle |
| **Bayat başlık sayıları** | FAZ 0 *"(14 madde)"* ↔ kapısı **25/25** · EK J *"KD-1…KD-20"* ↔ içinde **KD-22** · §E.2'de **ikinci kopya** · EK H/7.4 *"23 kural"* | Beşi de hizalandı |
| **`§A.4/b…`** | numaralı maddeler **(a)** bloğunun altında | 🔴 **7 atıf** → `§A.4/a`. *İlk tur yalnız **parantezli** biçimi taradı, **çıplak** `/b` atıflarını kaçırdı — düzeltmenin kendisi eksik kaldı: **desene göre tarama, kapsama göre değil**.* `:2465` **doğru** (Discovery rozeti gerçekten `(b)` tablosunun G maddesi) |
| **5.16 → 5.15 → 5.17 sırası** | ✅ | 5.15 **5.16'nın önüne** alındı |

### N.4 · ⚠ **En büyük tek bulgu: §A.2 yine ölü beyandı** — ve rapor **eksik saymıştı**

Rapor *"⭐ 4/11 tam"* dedi; **belgenin tamamını taradığımda gerçek çok daha kötü çıktı:**

| | Sürüm 4 | Sürüm 5 |
|---|---|---|
| **⭐ madde (altı blok zorunlu)** | **9 tam · 25 EKSİK** | **33 / 33 TAM** |
| **Kademe 2 · KAPI zorunlu** | **10 madde KAPI'sız** *(rapor yalnız 0.21'i görmüştü)* | **0 eksik** |
| 🔴 **Kademe 2 · bayraklıysa `GERİ AL` de zorunlu** | **19 madde** — *hiçbir rapor bunu görmedi; §A.2'nin kendi cümlesini maddelere karşı koşunca çıktı* | **0 eksik** |

**Eklenen: 86 blok.** Kalıp doldurulmadı — her biri maddeye özgü yazıldı; **en kritik olanı
`GERİ AL`**, çünkü *geri alma yolu yazılmamış madde geri alınamaz*. Üç sınıf çıktı ve üçü de
**ayrı ayrı yazıldı**:
- **Bayraklı** → `<bayrak>=off` → davranış birebir bugünkü (KURAL B)
- **Değişmez onarımı** (1.1b · 1.3 · 7.8) → 🔴 **geri alınmaz** ve **neden** alınmadığı yazılı
- **Kapı/ölçüm** (0.14 · 0.15 · 0.19 · 4.2) → 🔴 **test silinmez, `xfail` işaretlenir ve
  gerekçesi `MIMARI.md`'ye yazılır** (ADR-0019: kanıt silinmez)

⚠ **Ve raporun kendi teşhisi haklıydı:** iki dış raporun getirdiği **dört madde tam**,
benim getirdiklerimin **çoğu eksikti** — *kusur bende başlamış, belge kopyalamış.*

### N.5 · ℹ Damgalar — **yeniden ölçüldü, sonuç DEĞİŞMEDİ**

Rapor haklıydı: HEAD **`71b542e` → `a5942c7` → `c4b14d1`** ilerledi ve `ask.py` **+83/−22**
değişti. **13 damga tazelendi.** Ama uyarının sonucu **beklenenin tersi** çıktı — hepsini
yeni HEAD'de yeniden koştum:

| Ölçüm | @`71b542e` | @`c4b14d1` |
|---|---|---|
| Netleştirme paydası | iliştiren **3** [1750·1903·1913] · iliştirmeyen **11** | **AYNI** |
| `ask.py:1745` *"Bulgular CEVABIN GÖVDESİDİR"* | ✅ | **AYNI satır** |
| `ReportPanel` `it.result \|\| it.kpi` | 2 isabet | **AYNI** |

**Yani 0.23 ve 0.5b'nin bütün çapaları hâlâ geçerli.** *(D2'nin değeri tam olarak budur:
kural olmasaydı bunu **kontrol etmezdim** ve şansa güvenmiş olurdum.)*

### N.6 · ➕ Denetimlerin GÖRMEDİĞİ — bu turda ölçümden çıkan iki şey

1. 🔴 **`c4b14d1`: ölçüm aracı ÜÇÜNCÜ kez yalan söyledi.** `--live` *"CANLI MOD"* yazarken
   sağlayıcı `RuleBasedSqlGenerator`'dı; kök neden `get_settings`'in `@lru_cache`'i. **Ve
   `nl_accuracy.py` fonksiyonun KENDİ KOPYASINI taşıyordu** → commit'in kendi ifadesiyle
   *"**o koşumlara dayanarak bayrak kararı alınabilirdi**."* → **0.16'ya işlendi**: madde
   **küçüldü** (fail-closed indi) ama **gerekçesi büyüdü**.
2. **`is_period_only` hâlâ 0 çağıran** (`a5942c7`) — −0.5c tuzağı *"tam tasarlandığı gibi
   patladı"* ama **yarısı açık kaldı**. → **§F.3/8**.

Ayrıca deneyim süitinin **taban değeri** belgeye girdi (**34 ✅ / 1 ❌ / 56 ⊘** çevrimdışı ·
**33 / 2 / 56** canlı) ve `S8`/`S9`'un **hangi senaryoda koşacağı** yazıldı — rapor
*"senaryosu olmayan sözleşme satırı ölçmez"* diye uyarmıştı, **haklıydı**.

---

## KAPANIŞ — bu belge uygulandığında

1. **Sayı hâlâ küp koyar** — hiçbir faz bunu değiştirmez.
2. **Ajan kullanıcının yetkisini gerçekten aşamaz** (bugün *"aşamaz"* bir **beyandır**;
   FAZ 1.3'ten sonra bir **kısıttır**).
3. **Evrensel kavramlar tek yerde tanımlıdır**; *semantic drift* **yapısal olarak** imkânsız.
4. **Çıplak terimin sahibi vardır** — kalem, sahip, tarih.
5. **Her yetenek görünür**: sıfır yetim uç, sıfır yetim alan, sıfır ölü bayrak, sıfır mock.
6. **Her sayı kanıtlı ve TAZE** — ve **bayatsa sayı gösterilmez**.
7. **Sistem konuşur** — **sekiz tür**, ve **kullanıcının kendi kelimeleriyle**.
8. **Karar verilir, kaydedilir, ölçülür** — ve **iki skor asla karışmaz**.
9. **Dışarıya kanıt verir**: Türkçe kapsam/doğruluk eğrisi · risk-kapsam eğrisi · çok-turlu
   benchmark · Ossie birlikte-çalışabilirliği · MCP yüzeyi.

**En kötü durum hâlâ *"süssüz ama doğru"*; asla *"akıcı ama uydurma"*.**

---

> **Bu belgenin kendi denetim kaydı.**
>
> **Sürüm 2** — üç iç ajan denetimi: **kapsama** (62 kaçan madde → kapatıldı) ·
> **uygulanabilirlik** (113 maddenin 111'i şablonu taşımıyordu → iki kademeli şablon) ·
> **olgusal doğruluk** (25 atıfın 18'i doğru; 7 kayma + 2 yanlış düzeltildi).
>
> **Sürüm 3** — **dış denetim** (`u-anda-bir-plan-tingly-fox.md`). Sekiz kritik iddiasının
> **sekizi de bu oturumda kodla doğrulandı** (EK L.1). Getirdikleri: **bir bloklayıcı hata**
> (0.22) · **iki üründeki canlı ihlal** (K1 makbuz · K2 madalya) · **iki yapısal kusur**
> (K3 konuşma sınıfı · `enforce_query` boş stub) · **iki sıralama hatası bende**
> (CI kapıları · metrik hakemi) · **üç tamamen kaçırdığım eksen** (ölçüm bütçesi · gecikme
> bütçesi · korpusun kartezyen paydası) · **§C'ye dört kullanıcı-sonucu ölçütü**.
> **Bir madde değiştirilerek** (D14), **iki iddia doğrulama bekleyerek** (MCP spec · Wren
> embed RLS), **bir çerçeve reddedilerek** (efor tahmini — L.5) kabul edildi.
>
> **Sürüm 4** — **ikinci dış rapor** (`SOHBET-DENEYIMI-RAPORU_2026-08-03.md`), çıkış noktası
> bir **kullanıcı şikâyeti**: *"chat akmıyor, beni anlamıyor, robotik."* On bulgusunun
> **onu da bu oturumda kodla yeniden ölçüldü ve doğrulandı** (EK M.1) — payda dâhil, kendi
> ayrıştırıcımla. Getirdikleri: **üç yeni FAZ 0 maddesi** (`0.23` ölü render dalı ·
> `0.5b` bekleyen netleştirme · `0.10b` görünen adlar) · **bir FAZ 5 maddesi** (`5.17` tek
> ses) · **K2 kapısına üçüncü boyut** (erişilebilirlik) · **iki kapsam-dışı kaydı**
> (KD-21 rakamsız uydurma · KD-22 aşama betiği) · **yeni §F bölümü** (deneyim aleti ·
> ertelenen `t2_anlatici`'nin tam planı · **çözülmeyenler**).
> **Üç madde değiştirilerek** kabul edildi (numara çakışması · paydanın ikinci dışlaması ·
> panel tanımı), **raporun iki gerekçesi düzeltildi** (EK M.4).
> 🔴 **Ve belgenin kendi iç çelişkisi bu turda çıktı:** §C/11 *"panel 12"* derken K5 hâlâ
> *"11"* diyordu; ölçüm ikisini birden düzeltti ve **sayıdan önce TANIM** yazıldı.
>
> **Sürüm 5** — **belgenin KENDİSİNE yapılan iki bağımsız bütünlük denetimi** (→ **EK N**).
> Bir içerik turu değil, bir **defter** turu; ve en sert bulgusu **v1'in asla
> kapanamayacağıydı** (§C/9 → v1 = **7 tür**). Getirdikleri: **kural D5** (taşıma kütüğü,
> **kapısıyla**) · **`netlestirme_kapanisi` bayrağının ayrılması** (paylaşılan bayrak iki
> ölçüm turu veremez) · **PK-24** (yüzey kırpması yasağı) · **2.2b'nin kendi kapısı**
> (0.18'inkiyle *"bitti"* sayılıyordu) · **67 eksik blok** · **beş bayat başlık sayısı** ·
> **13 damga**. Ve iki bulgu **denetimlerin görmediği yerden**, ölçümden geldi:
> `--live`'ın üçüncü kez karşılıksız çıkması ve `is_period_only`'nin hâlâ 0 çağıranı.
>
> 🔴 **Sürüm 5'in dersi — ve bu belgenin en tekrar eden kusuru:** *"§A.2'nin kuralı yine ölü
> beyandı."* Sürüm 1'de **113'ün 111'i**, sürüm 4'te **34 ⭐'ın 25'i** şablonu taşımıyordu.
> **Aynı sınıf, iki kez, iki farklı ölçekte.** Bir kuralın yazılmış olması onun uygulandığı
> anlamına gelmiyor — **kuralın bir KAPISI olmalı.** Bu yüzden D5 kapısız yazılmadı, ve
> §A.2'nin uyumu artık `tests/test_yol_haritasi_butunlugu.py`'nin işi.
>
> **Yedi denetim boyunca HEAD sekiz kez ilerledi.** Bu, kural **D2**'nin (HEAD damgası +
> yeniden ölçüm komutu) neden var olduğunun kanıtıdır — ve bu belgenin **tek en önemli
> kuralıdır**. ⚠ **Ama sürüm 5 bir nüans ekledi:** damgalar tazelendiğinde **hiçbir sonuç
> değişmedi**. D2'nin değeri *"sayılar bayatlar"* değil, ***"bayatlayıp bayatlamadığını
> KONTROL ETMEYE zorlar"***.
>
> **Ve sürüm 4'ün kendi dersi:** iki bağımsız dış rapor, **iki farklı kapının aynı körlüğü
> paylaştığını** gösterdi (K2 ↔ deneyim süiti). *Bir kapı yeşil diye iş bitmiş değildir —
> kapının ne sorduğunu da denetlemek gerekir.* Bu, §6.4'ün *"ölçüm aracının kendisi de bir
> bağımlılıktır"* kuralının **kapı eksenine** genişletilmiş hâlidir.
