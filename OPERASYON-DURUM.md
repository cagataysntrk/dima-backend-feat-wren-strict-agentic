# OPERASYON DURUMU — *nerede kaldık*

> 🔴 **BAĞLAM SIFIRLANDIYSA BURADAN BAŞLA.** Sırayla oku:
> 1. **`OPERASYON.md`** — kural seti (nasıl çalışılır)
> 2. **bu dosya** — nerede kaldık
> 3. **`~/.claude/plans/DIMA-V1-YOL-HARITASI.md`** — ne yapılacak *(§10'daki sıra)*
> 4. `backend/MIMARI.md` — mimari değişmezler
>
> Bu dört dosya operasyonun **tam durumunu** taşır. Sohbet geçmişine ihtiyaç YOKTUR.

**Son güncelleme:** 2026-08-04 · HEAD → **FAZ 0 · adım 1** *(0.22 · 0.2 · 0.23)*

---

## 🔵 ŞU AN

| | |
|---|---|
| **Aktif faz** | **FAZ 0** — temizlik ve kapılar *(25 madde; sıra **numara DEĞİL**, FAZ 0 girişindeki bağlayıcı koşum sırası)* |
| **Sıradaki madde** | **adım 2:** `0.1` — yeniden ölçüm turu *(`lab/reports/faz0_taban.md`, her satır `<sayı> @<sha> · <komut>`)* |
| **Ondan sonra** | `0.16` → `0.14` → `0.19` → `0.18` → `0.4/0.5/0.5b` → kalan *(0.3 dâhil)* → `0.21` |
| **v1 bitiş ölçütü** | §C'nin **16 ölçütü** yeşil |

---

## ✅ BİTEN

### FAZ −2 · Belge onarımı *(kod yok — 2026-08-04)*
Yol haritası **4881 → 5213 satır**. Yedek: `~/.claude/plans/.yedek/` *(md5 doğrulandı)*.

| # | Ne | Nerede |
|---|---|---|
| **#5** | **`§G.6f`** — `N`=3 (simetri şartıyla) · hakem protokolü (2 hakem · 10 vaka · ayrışma→`⊘`) · 🔴 **`⊘ KOŞULAMADI` ≠ «kaybetti»** · kısmi benimseme | §G.6f |
| **#1** | v2 giriş **döngüsel kilidi** kırıldı: *"teyitli"* → **"kararı bağlanmış"**; v3'e ait 2 madde kapıdan çıkarıldı | §B · Bölüm II girişi · II-0 |
| **#4** | FAZ 0'ın **dört `KAT-3` ihlali** + **bağlayıcı koşum sırası**; `0.23`'ün *"bağımlı değil"* çelişkisi kapatıldı | FAZ 0 girişi · 0.23 |
| **#3** | **`6.0` YENİ MADDE** — *"D9 ters uygulanmış · yapılanı geri al"*; `6.1`'in çelişkili `KAPI` bloğu kaldırıldı | 6.0 · 6.1 |
| **#2** | Bölüm II şablon borcu: **18 bayraklı maddenin 17'sinde `GERİ AL` yok** + kök neden (denetim regex'i `II-X.N` başlıklarını kapsamıyordu) kapıya çevrildi | Bölüm II girişi |
| **+** | **VK-5 üç kalıntısı** düzeltildi *(aşağıdaki ölçümle)* | §G.6e |

### FAZ −1 · `MIMARI.md` ön hazırlığı *(kod yok — 2026-08-04)*

| Kutu | Ne indi | Kanıt |
|---|---|---|
| **A** (`−1.1`) | MIMARI'de **12 satır** düzeltildi (A1…A13; **A6 geri çekildi**) | `MIMARI.md` diff |
| **B** (`−1.2`) | **`§0 · ⟳ YÜRÜRLÜKTE` toplu indeksi** — 13 satır. 🔴 Blok **kural BEYAN ETMEZ**, yalnız **otorite işaret eder** | `MIMARI.md §0` |
| **C** (`−1.3`) | Her `⟳` satırı için **tuzak** + 2 meta-test → `test_beyanlar_curumesin.py` **27 yeşil** | dosya |
| **KAPI** | **yeni** `tests/test_MIMARI_dosya_atiflari_var.py` — MIMARI'de anılan her `tests/test_*.py` var olmalı | 12 ✅ · 2 ⊘ |

> 🔴 **Kutu C'nin dersi — üç kırmızının ÜÇÜ DE tuzakların değil BENİM BELİRTECİMİN kusuruydu.**
> Tam olarak *"ölçüm aracının kendisi de bir bağımlılıktır"* sınıfı; her biri **metni** ölçüyordu, **kodu** değil:
> · `§3.4-osi` gevşek alt-dize (`"ossie" in <tüm app kaynağı>`) **yorum satırını** yakaladı → **dosya varlığına** indirildi
> · `§4` alt-dize taraması `tools.py`'nin **docstring'ini** yakaladı → **AST**'ye indirildi (`_yazan_arac_sayisi`)
> · kural-beyanı kapısı bloğun **kendi açıklamasını** ihlal sandı → yalnız **tablo satırlarını** tarar
> **Yasağı anlatmak, yasağı çiğnemek değildir.**

**Yol haritasında kapanan borçlar** *(5213 → 5239 satır; yedek + md5 doğrulandı)*:
`A5` → **D2 biçimi** (sabit sayı silindi, `A5-KOMUT` kutusu yazıldı; **6 kalem bayatlamıştı**,
4 kalem doğruydu) · `A6` → geri çekildi + kütük · `KAPI` atfı → dosya değil **fonksiyon**
(`test_beyanlar_curumesin.py::test_MIMARI_TEST_SAYILARI_gercekle_uyusuyor`) · *"altı satır"* ↔
13 satır çelişkisi *(açık borç #3'ün bir kalemi)*.

> ⛔ **A6 neden düştü:** *"`tests/test_member_sweep.py` YOK"* iddiasının kanıtı
> (`grep -rl member_sweep` → boş) **hiç koşulmamıştı**. Dosya **VAR**: 113 satır, 5 test,
> commit `f5f4048`. **Kanıt cümlesi de kanıt ister.**

### FAZ 0 · adım 1 — `0.22` · `0.2` · `0.23` *(2026-08-04)*

| Madde | Ne indi | Kapı |
|---|---|---|
| **0.22** | `migration_trace` **fonksiyon gövdesine** taşındı *(tanım `if structural_followup:` bloğunun içindeydi, 4b dalı blok DIŞINDA okuyordu)* | `test_agent_plan_secimi_yapisal_olmayan_turda_cokmez` + `test_MIGRATION_TRACE_blok_disinda_TANIMLI` |
| **0.2** | `sec()` reddi `kapisiz=True · dis_maliyet="sifir" · notlar` ile kaydedilir; **ayrıca** `Kosum.sorgu_sayisi` **fail-safe** oldu | `test_uydurma_arac_makbuzu_dusurmez` + `test_MAKBUZ_bilinmeyen_arac_adinda_da_AYAKTA_kalir` |
| **0.23** | `raporlanabilir()` **tek sahip**; `ReportPanel`'in İKİ kapısı ona bağlandı; **saf-not dalına `next_steps`** | `test_cevap_alani_yetim_degil.py` **+4 test** · `tsc --noEmit` 0 · `eslint .` 0 hata |

> 🔴 **HER İKİ HATA DA «ÖNCE ÖLÇ» ile kanıtlandı** — hatalar koda geri konup kapılar
> **kırmızıya** düşürüldü, sonra düzeltmeyle yeşile: `UnboundLocalError: ... 'migration_trace' ...`
> @ `ask.py:3217` · `KeyError` @ `planner.py` `sorgu_sayisi`.

> ⚠️ **0.22'nin kapısını ÜÇ KEZ yanlış yazdım, üçünü de ölçerek yakaladım:**
> (1) soru `route()` ile cevaplanıyordu → test **boşa koşuyordu**;
> (2) doğru soru **yanlış çağrı yerini** vuruyordu — pilotun `[]` literali geçen ikinci
> çağrı yeri hatalı kodda bile çökmüyor, yani test **hatayla birlikte yeşil kalıyordu**;
> (3) `code_context` tek satır verdiği için iki satıra yayılan çağrıyı göremiyordu.
> Kapı artık **çağrı yerini de** iddia ediyor. *Bir kapı, ölçmediği şeyi «geçti» diyemez.*

> 🔴 **VE DÖRDÜNCÜ KEZ AYNI SINIF — kapı turunda:** `⟳` sayacı `mimari.count("⟳ UYGULANMADI")`
> idi; §0'a bloğun kendi kapılarını anlatan paragraf eklenince o **ifade düzyazıda** da geçti
> → sayaç **14**, tablo **13**. Belge doğruydu, **sayaç yanlıştı**. Kök neden: satır
> ayrıştırma **tek sahibe** alındı (`_yururlukte_satirlari`) — üç test de artık düzyazıyı hiç
> görmeden tablo satırı üzerinden ölçüyor, kaçışlı `\|` tek yerde ele alınıyor.

### Taban ölçümü · `lab/vk_taban.py` *(commit `8f87e40`)*
VK-1…VK-6 **yapısal ve canlı** (gemini) ölçüldü. `§G.6e`'nin *"Bugün"* sütunu artık
**yeniden üretilebilir**. Üç satır düzeltilmesi gerekti (VK-4 · VK-5 · VK-6).

> 🔴 **OPERASYONUN EN ÖNEMLİ SAYISI:** **13 turun DÖRDÜNDE** yazım-benzerliği kısa devresi
> öldürüyor → **`AJ0` §G'nin tek en yüksek kaldıraçlı maddesi**; VK-1 · VK-5 · VK-6'yı
> **ilk kapıda** kesiyor, `AJ2`/`AJ5b` sıraya bile gelmiyor.

> ✅ **Çürütülen iddia:** *"`verimlilik` katalogda YOK"* **yanlıştı** — `verim` + geçerli ek
> zinciriyle kapsanıyor (`oee.ort_oee`). Asıl eksik **ÜRÜN BOYUTU** (`R9`), ve o
> **tenant-özel** (`stok_adi` gitas'ta VAR).

---

## 📋 AÇIK BORÇLAR — unutulmayacak

| # | Borç | Nerede kapanır |
|---|---|---|
| 1 | `0.23` **kapısız iner** (düzeltmesi bağımsız, `KAPI`'sı `K2/(c)`) | **FAZ 0.14** — geriye dönük |
| 2 | Bölüm II'nin **17 maddesinde `GERİ AL` yok** | Madde **sıraya alındığında** (kapı: 0.14'ün `test_yol_haritasi_butunlugu.py`) |
| 3 | Belgede **8 kusur** kaldı *(FAZ −1'de `−1.1` 6↔13 ve `A6` kapandı)*: sayı çelişkileri (v2 kapsamı · §G aralığı · `KAT-1…4` başlığı · EK K 24↔29) · **4 ölü bayrak** · `II-D.1b` tanımsız · **iki biçim hatası** (`GERİ AL` blokları yanlış faz başlığı altında) · FAZ 7 kapsamı (Plan 2 dalı) | İlgili faza gelindiğinde — **ayrı tur AÇILMAZ** |
| 4 | `is_period_only` hâlâ **0 çağıran** | 0.14/K2 |
| 5 | Deneyim süitinin **bilerek açık kırmızısı**: *"o ayı makine bazında aç"* | II-D *(satır çapası)* |
| 6 | **`A13` yarım indi:** `§1.5 · §2.1 · §3.2 · §4.4` düzeltildi, **`§1.6` + `§1.7` atıfları duruyor** — `MIMARI.md` satır **559 · 621 · 663 · 886 · 916 · 1298 · 1844 · 1965 · 2001 · 2079 · 2092 · 2582** *(denetim A/(a)1 · kendi ölçümüm doğruladı)* | FAZ 0.14'ün belge kapısı |
| 7 | **`A11` yarım indi:** uzlaştırma bloğu yazıldı ama **sabit sayılar yerinde** — `93` → `MIMARI.md:605 · 737 · 738`, `105` → `2762 · 2765`. Bir kısmı **tarihli olay kaydı** (meşru), bir kısmı **bugünü anlatıyor** (D2 ihlali); ayrımı madde sırası gelince yap | FAZ 0.1 *(yeniden ölçüm turu)* |
| 8 | **`D1` beyanı FAZ −1'in üç maddesinde YOK** — `backend·sözleşme·frontend` üçlüsü de `api-only`/`belge` muafiyeti de yazılmamış *(muafiyet meşru, **beyan** eksik)* | FAZ 0.14 |
| 9 | **Yol haritası `−1.2` tablosu (12 satır) ↔ `MIMARI §0` (13 satır) ayrıştı**, D5 kütüğü bırakılmadan: MIMARI'de **eklenen** `§5/18. yasak → §G/AJ0`; **değişen otoriteler** §8.2 `4.7→4.6` · §9 `2.2→0.18·2.1` · §12 `6./7./8.→6./7.` · §7 `FAZ 4→0.15·FAZ 4` · §4 `6.1→6.0→6.1→6.2`. 🔴 **Beşinde de MIMARI DOĞRU, yol haritası bayat** | FAZ 0.14 |
| 10 | **`A9`/`A12`'nin kanıt satır numaraları bayat** — `A9` *"2567·2571·2630"* diyor, gerçek `2804·2808·2867`; `A12` notu *"1309. satır"* diyor, bugün `1348`. *(A6'nın düştüğü hatanın aynısı; ikisi de **zararsız** çünkü düzeltmeler indi)* | FAZ 0.1 |
| 11 | 🔴 **KENDİ BULGUM (0.23'ü koşarken ölçüldü): raporlanabilirlik kuralının BEŞ sahibi varmış, 0.23 yalnız İKİSİNİ kapatıyor.** Kalan üç sahip: `page.tsx:100` (`latestReportable` — tuvale ekle hedefi) · `page.tsx:114` (`addToCanvas`) · `page.tsx:139` (`lastReport` — **resume çapası**) · `ChatPanel.tsx:196` (thread listesi önizlemesi). **Neden AYNI TURDA kapatılmadı:** ikisi (tuval) `AnalysisCanvas.tsx:82`'nin `it.cube_query && it.result` kapısına bağlı — genişletmek **sessizce boş bir tuval kartı** doğururdu; o yüzey **`0.3`'ün konusu** (K4 `test_yuzey_sadakati.py`). Diğer ikisi (`page.tsx:139` · `ChatPanel.tsx:196`) **serbest ve güvenli**, ama `0.23`'ün `NE`'si açıkça yalnız `ReportPanel` diyor → kapsam sessizce genişletilmedi. `raporlanabilir()` **export edildi**, üçü de ona bağlanacak | **FAZ 0.3** *(aynı fazda, «kalan» adımı)* |

---

## 🤖 ARKA PLAN DENETİMİ

Her faz commit'inden sonra **üç ajan paralel** koşar *(`OPERASYON.md` §7)*:
**A** plan denetçisi · **B** bütünlük denetçisi · **C** canlı kullanıcı *(tek tek, insan gibi)*.
Raporları **bir sonraki fazın girdisidir**; kritik bulgu sıradaki maddeden **önce** işlenir.

**Son denetim turu:** **FAZ −1 · `c3fcfe7`** *(2026-08-04)*.
⚠ **Düzeltme (denetim kendi buldu):** bu satır `c3fcfe7`'de *"koştu"* diye yazılmıştı,
oysa tur **commit'ten sonra** koşuyordu — *"olmuş gibi yazmak"* tam da bu operasyonun
yasakladığı şey. Fiilî durum: **A koştu** *(rapor işlendi, aşağı bak)* · **B API hatasıyla
düştü → FAZ 0/adım-1'de yeniden koşuyor** · **C (canlı kullanıcı) FAZ 0/adım-1'e ertelendi**
*(FAZ −1 belge turudur; canlı kullanıcının deneyeceği davranış değişikliği İÇERMEZ)*.

**A'nın işlenen bulguları** *(kritik olanlar sıradaki maddeden ÖNCE kapatıldı)*:

| Bulgu | Ne yapıldı |
|---|---|
| `§3.4-osi` tuzağı **yanlış-NEGATİF** — faz indiğinde susardı (belirteç `ossie_import.py` arıyordu, FAZ 3.4 ise `POST /connections/{id}/import-semantic` + `ossie_ithal` bayrağı vaat ediyor) | belirteç **fazın kendi vaadine** bağlandı (uç ∨ bayrak ∨ modül) |
| Kural-beyanı kapısı hâlâ **METİN** ölçüyordu (üç birebir Türkçe ifade) | **yapısal kapı** eklendi: her satır **dört hücreli işaretçi** + `Durum == ⟳ UYGULANMADI` + otorite fazı; ifade taraması artık *"tel tuzağı"* olarak **sınırı yazılı** duruyor |
| `test_MIMARI_ANILAN_MODULLER_VAR` **biçim körlüğü** — MIMARI `cube_router`'ı 18 kez anıyor, hep `app/` öneksiz → deponun en merkezî modülü `skip` ediliyordu | çıplak modül adı da (kelime sınırıyla) sayılır → **12 ✅ · 2 ⊘** yerine **14 ✅** |
| Yeni kapının `MUAF` listesi **ölü doğmuştu** (üç girdinin üçü de MIMARI'de hiç geçmiyor) | liste **boşaltıldı**, gerekçesi yazıldı |
| `A9` üçüncü satırı (`MIMARI.md` *"8984 turda ~%64"*) ve `A5`'in MIMARI tarafı (*"pytest 1016 geçti"*) **D2 ihlali olarak duruyordu** | ikisi de **komuta çevrildi** |
| Yeni kapı dosyası MIMARI'de anılmıyordu (D4) | §0'a **kendi kapıları** satırı eklendi |
| `test_orkestrator.py` MIMARI'de **25**, gerçek **29** | ⚠ **kapı kendi kendini yakaladı** — düzeltildi |

---

## 📌 ÖLÇÜM TABANI *(D2: sayı + damga + komut)*

| Ölçüt | Değer | Damga | Komut |
|---|---|---|---|
| Test | **2056** *(2056 ✅ · **0 ⊘**)* | FAZ 0/adım 1 | `pytest -q --collect-only` |
| eval | `+0,0 / +0,0 / +0,0` | FAZ 0/adım 1 | `python -m eval.run` |
| Korpus doğru-cube | **%93,2** *(taban %93,2)* | FAZ 0/adım 1 | `python lab/nl_corpus.py --kapi` |
| Konuşma senaryoları | **düşürülen 0** · 1 ⊘ (`vqr_kalicilik`) | FAZ 0/adım 1 | `python lab/kapi.py --tam` |
| Frontend | `tsc --noEmit` **0** · `eslint .` **0 hata** *(4 eski uyarı)* | FAZ 0/adım 1 | `./node_modules/.bin/tsc --noEmit` |
| Deneyim süiti (canlı) | **41 ✅ · 1 ❌ · 63 ⊘** | `88bde2a` | `python lab/deneyim.py --live` |
| VK taban | **§G.6e kutusu** | `8f87e40` | `python lab/vk_taban.py --live` |
| Motor-RLS | **0** | `8f87e40` | `grep -rc rowLevelAccessControl backend/app/` |
| Bayrak | `FLAG_REGISTRY` **16** ↔ `features.yml` **14** | `8f87e40` | — |
| Panel export | **13** *(tavan DOLU)* | `88bde2a` | `grep -rE "export (default )?function [A-Za-z]+Panel" src/ \| wc -l` |
| Konuşma türü | **5** *(v1 hedefi 7)* | `8f87e40` | `grep -cE "^TUR_[A-Z_]+ = " backend/app/followup.py` |
