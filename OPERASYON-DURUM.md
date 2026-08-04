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
| **Sıradaki madde** | **adım 3:** `0.16` — ölçüm bütçesi + koşum hijyeni *(ayrılmış kota anahtarı; her «önce ölç» kapısının ön koşulu)* |
| **Ondan sonra** | `0.14` → `0.19` → `0.18` → `0.4/0.5/0.5b` → kalan *(0.3 · 0.6–0.13 dâhil)* → `0.21` |
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

### FAZ 0 · adım 2 — `0.1` yeniden ölçüm turu *(2026-08-04)*

**Teslimat:** `backend/lab/faz0_taban.py` → `backend/lab/reports/faz0_taban.md`.
§C'nin *"Bugün"* sütunu **artık elle yazılmıyor**; yol haritası bu araca işaret ediyor.

> 🔴 **Ölçüt 1'de TANIM BULANIKLIĞI ölçüldü:** *"yanlış-cube 493"* aslında
> **458 yanlış cube + 35 Discovery'ye düşme**dir. Hedef *"azalır"* olduğu için hangi
> sayının azalacağı belirsiz kalamaz → **1a / 1b / 1c** olarak ayrıştırıldı.

> ⚠ **Aracın kendi kusuru (bu turda BEŞİNCİ kez «ölçüm aracı bir bağımlılıktır»):**
> ilk sürüm host'ta `pytest --collect-only` koşup **1806** yazıyordu — konteynerde
> **2056**. Eksik bağımlılık yüzünden modüller toplanamıyor, `pytest` yine de
> *"collected"* diyor. Araç artık **toplama hatası varsa sayı yazmıyor** (`⊘`).
> İkinci kusur: markdown hücresindeki `|` kaçışlanmıyordu → tablo sessizce bozuluyordu.
> Üçüncüsü: `receipt`/`supersedes` için sayaç **1** deyip *"tüketiliyor"* okunmuştu —
> o isabet `lib/types.ts`'teki **tip beyanıydı**. **Bir tip beyanı tüketici değildir.**

**[KANIT §0.1]'in 12 kusuru @`0619bfd`** — ✅ **3 kapandı** · ◐ **3 kısmen** · 🔴 **6 açık**:

| # | Kusur | Durum | Sahibi |
|---|---|---|---|
| 1 | `sec()` → makbuz düşüyor · bütçe kapısı atlanıyor | ✅ **kapandı** | *bu operasyon, `0.2`* |
| 9 | `_META_HINTS` çıplak alt-dize | ✅ kapandı | — |
| 11 | `eval/baseline.json` bayat · katı monkeypatch | ✅ kapandı | `baseline.n` 129 ↔ `report.n` 129 |
| 2 | `AnalysisCanvas` rozet basmıyor *(SourceBadge **0**)* | 🔴 açık | **0.3** |
| 3 | Netleştirme, Intent-JSON'dan sonra | ◐ mekanizma indi, bayrak `off` | **0.4** *(ölçüm kararı)* |
| 4 | Çapa zinciri üretimde ölü *(`capalar=` **0**, `SureklilikOlcumu` **0**)* | 🔴 açık | **0.5** |
| 5 | `GET /contracts` tüketicisiz *(kapı yanlış-pozitif yeşil)* | 🔴 açık | **0.6** |
| 6 | `POST /query` + `runQuery()` ölü | 🔴 açık | **0.7** |
| 7 | Alan yetimleri — hâlâ yetim: **`receipt` · `explain.path` · `supersedes` · `execute`** *(`kpi_components` **2** tüketici ile kapandı)* | ◐ kısmen | **0.8 · 0.9 · 0.11** |
| 8 | `interpret` `"top"` fact'i UI'da yok | 🔴 açık | **0.10** *(+ 0.10b)* |
| 10 | `sinifla(baglam_var=True)` sabit kodlu | 🔴 açık | **5.0** |
| 12 | Sosyal sınıf teslim borcu — **bayrak YOK** *(MIMARI düzeltildi, test var)* | ◐ kısmen | **0.13** |

> ✅ **Sonuç: FAZ 0'ın iş listesi ÖLÇÜMLE DOĞRULANDI** — açık kalan dokuz kusurun
> **dokuzu da** zaten bir FAZ 0/5 maddesinin konusu. Yeni madde doğmadı, üç madde düştü.

### 🔴 P0 · CANLI KULLANICI TURUNUN BULDUĞU SESSİZ-YANLIŞ *(2026-08-04)*

Denetçi **C** (gerçek kullanıcı gibi, 16 tur, canlı `gemini-flash-lite`) `makine × ay`
kırılımlı fire raporunda **aynı veri için üç ayrı yüzde** gördü:
`+%88,1 arttı` → `−%72,3 azaldı — İYİLEŞTİ` → `+%98,3 arttı`.

> *"Aynı veriye üç farklı yüzde. Sarı satırı okumayı bıraktım."*
> *"Veriyi çekmek için kullanırım, ama yorumunu müdürler toplantısında ekrana
> yansıtmam — çünkü yanlış yüzdeyi bir kez okursam, o toplantıda benim itibarım gider."*

**Kök neden (kendim ölçtüm):** `interpret._series_facts` **satır başına** bir nokta
alıyordu; pivotta aynı ay onlarca kez tekrarlanır ve *"ilk→son"* **iki farklı makinenin**
değeridir. Kod pivot olduğunu **zaten fark ediyordu** (`entity`) ama sayıyı yine yayımlıyordu.

**Düzeltme iki katmanlı, ve ikinci katman asıl olan:**
1. Trend **dönem toplamları** üzerinden (`_donem_bazinda_topla`).
2. 🔴 Toplanabilirlik kuralı **zaten tek sahipteydi** — `contribution.ayristirilabilir_mi`.
   `interpret` onu **tanımıyordu**: katkı yolu *"oran → katkı payı tanımsız"* diye dürüstçe
   reddederken yorum satırı aynı ölçü için hem payı hem trendi basıyordu. **Kimlik
   asimetrisi.** Artık sahip çağrılıyor; toplanamayan ölçüde trend **hiç yazılmıyor**,
   *"toplamın %X'i"* payı da yalnız toplanabilir ölçüde yayımlanıyor.

**Önce ölçüldü:** eski kod geri konunca kapı üç kırmızı verdi — `%0.0` (doğrusu %100) ·
oran ölçüsünde trend yayımlandı · *"toplamın %55,7'si"*. Kapı: `tests/test_pivot_trend_yanlis_degil.py`.

### 🔴 P0 · DENETÇİ B'NİN BULDUĞU — onay kartı ekranda yoktu *(aynı tur)*

`raporlanabilir()` gövde alanlarını **SAYIYORDU** (`result|kpi|contribution|prescription`)
— bir **`KAT-5` ihlali**. Listede olmayan **beşinci** gövde alanı `eylem_onerisi`, yani
**FAZ H'nin *"Onayla"* kartı**; `ReportCard`'ın TEK tüketicisi bu kapının arkasında olduğu
için kullanıcı *"bundan sonra hep aylık göster"* dediğinde **sarı bir not** görüyor,
**Onayla düğmesi hiç çıkmıyordu**. 🔴 *0.23'ün düzelttiği hatanın birebir aynısı,
düzeltmenin **kendi içine** kodlanmıştı* — ve kapının testi de aynı dört adı sabitlediği
için **ölçülemezdi**.

**Düzeltme — SAYMA, KAPAT:** gövde alanları sayılmıyor; **saf-not** (yalnız açıklama/
taşıma alanı taşıyan cevap) kapatılıyor. Yeni bir gövde alanı eklendiğinde liste
güncellenmek zorunda değil. Hata yönü de tersine çevrildi: unutulan bir *taşıma* alanı
**görünür** bir gerileme üretir; unutulan bir *gövde* alanı **sessiz** kayıptı.

**B'nin diğer işlenen bulguları:**

| Bulgu | Ne yapıldı |
|---|---|
| **İhlal 1** — *"tek sahip"* kutlanırken `next_steps` chip bloğu `ReportPanel`'e **22 satır kopyalandı** (19'u birebir) | **`NextStepChips.tsx`** tek sahip olarak çıkarıldı; ikon eşlemesi de tek yerde *(backend `NextStep.kind` kısıtsız — dördüncü tür artık iki yerde birden sessizce `∑` olmuyor)* |
| **İhlal 2** — bilinmeyen araç adı makbuzda **işaretsiz**: `query_count` tahmin taşıyor, `error`/`gated` yok | `Adim.ozet()` artık işaretliyor (`tools.kayitli_mi`) — *"tahmine dayanan her sınır GÖRÜNÜR olur"* |
| **R9** — netleştirme şıkları *"sonraki adım"* başlığıyla sunuluyordu *(`ReportCard`'ın kendi yasakladığı yanlış başlık)* | başlık çağırana ait: not dalında **"şunlardan biri mi?"** |
| **R6** — `_yorumsuz_kod` yalnız tek satırlık yorumları atıyordu, **8 satır sızıyordu** | çok satırlı `{/* */}` blokları da atılıyor |
| **R7** — `test_SAF_NOT_dalinda_NEXT_STEPS_var` **dosyanın tamamını** tarıyordu (bir yorum satırı testi yeşil tutardı) | dal bulunup **yalnız o dal** ölçülüyor |
| **İhlal 4 (D2)** — ölçüm tablosunun damga sütununda sha yerine faz adı; `--collect-only` geçen/atlanan ayrımı vermez | damgalar **sha**'ya çevrildi, komutlar ayrıştırıldı |
| *(bu turda doğan)* `test_REPORTCARD_…_gizleme_KORUNDU` birebir ifade arıyordu → chip tek sahibe taşınınca **yanlış-kırmızı** | koruyucuya yapısal olarak bakıyor *(bu turda **beşinci** metin-ölçen kapı)* |

**Ertelenen (borç):** `R1` `raporlanabilir`'in ikinci işi (`viewHint` sahipliği, testsiz) ·
`R4` 0.22 kapısının metin penceresi · `R5` `_yururlukte_satirlari` biçim bağımlılığı ·
`R8` chip'lerin maskeli-boyut süzgecini paylaşmaması · `R10` `page.tsx:100`/`ChatPanel:196`.

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
| 12 | `R1` **`raporlanabilir()` İKİ İŞ yapıyor** — hem *"kart render et"* hem *"`viewHint` kime gider"*. Contribution kartı `lastReportableIdx` olunca önceki tablo kartı `viewHint={null}` alır → `ResultView` remount, hint'li görünüm sıfırlanır. **Kilitleyen test YOK** (`grep viewHint backend/tests` → 0) | **FAZ 0.14** *(K2 kapıları)* |
| 13 | `R4` **0.22 kapısı metin penceresiyle** ayırt ediyor (3 satır). Bugün doğru; 2773 civarına *"migration_trace"* geçen bir **yorum** eklendiği gün yanlış-yeşil. Yapısal alternatif: `stack()[1].frame.f_locals["migration_trace"] is <arg>` **kimlik kıyası** | **FAZ 0.14** |
| 14 | `R5` **`_yururlukte_satirlari` biçime bağlı** — `satirlar[2:]` §0'da tek tablo + tam iki başlık satırı varsayıyor; başlık metni değişirse `str.index` **ValueError**. *(Yön fail-closed, sessiz-yanlış değil)* | **FAZ 0.14** |
| 15 | `R8` **Chip'ler maskeli-boyut süzgecini paylaşmıyor** — `answer.py:441-447` maskeli kolona filtre kuran chip'leri eliyor; `_intent_uyusmazlik_chipi` kendi chip'lerini kuruyor ve `_attach_next_steps` `result is None` diye erken dönüyor. 0.23 bu chip'leri **görünür yaptı**, süzgeci paylaşmadı → *"boş dönen chip"* riski | **FAZ 0.14** |
| 16 | 🔴 **Canlı turun kalan beş bulgusu** *(C)*: (a) çelişki sorulduğunda cevap yok, aynı rapor yeniden çiziliyor → **5.0/5.3** · (b) *"ne yapmalıyız"* çıkmaz sokak, `prescription` hiç dolmuyor ve kullanıcının *"o zaman kg üzerinden bak"* düzeltmesi **yok sayılıyor** → **FAZ 5** · (c) tek kelimelik düzeltme (*"yok haziran olsun"*) arkada `Unknown filter dimension 'tarih' in cube 'enerji_tesis'` **iç hatası** + konu kaybı → **hata, 0.x'e alınmalı** · (d) chip'e tıklayınca küp değişti (`enerji_tesis` → `surdurulebilirlik`) — iki *"elektrik"* iki farklı sayı → **0.4 netleştirme** · (e) **veri sonu tarihi hiç söylenmiyor**; kullanıcı üç turunu bunu keşfetmeye harcadı → **§C ölçüt 12 (tazelik), bugün 0** |

---

## ⛔ DENETİM — **AJAN KULLANIMI KALDIRILDI** *(2026-08-04, kullanıcı kararı)*

> 🔴 **OLAY:** Arka plan ajanları çalışmanın ortasında **ana sohbeti sildi.** Bağlam
> geri getirilemedi. → **Alt-ajan kullanımı KESİN OLARAK YASAK**; `OPERASYON-DENETIM.md`
> **silindi**; `OPERASYON.md §7` **öz-denetime** çevrildi (`Ö1` plan · `Ö2` bütünlük ·
> `Ö3` kullanıcı — **aynı oturumda, sırayla, elle**).

**Disiplin korunuyor** — çünkü değeri ölçüldü: o turlar belgede **15 kusur** buldu, ölçüm
aracı **12+ kez** yanlış çıktı, ve iki **P0 sessiz-yanlış** (pivot trend · `eylem_onerisi`
kartı) yalnız **canlı kullanıcı turunda** göründü. **Aşağıdaki bulgular tarihsel kayıttır
ve silinmez** (ADR-0019).

**Geçmiş turların işlenen bulguları** *(kritik olanlar sıradaki maddeden ÖNCE kapatıldı)*:

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
| Test *(toplanan)* | **2068** | `0619bfd`+ | `python lab/faz0_taban.py` |
| Test *(geçen/atlanan)* | kapı özetinden | `0619bfd`+ | `python lab/kapi.py --tam` |
| eval | `+0,0 / +0,0 / +0,0` | `0619bfd` | `python -m eval.run` |
| Korpus doğru-cube | **%93,2** · yanlış cube **458/7213** | `0619bfd` | `python lab/nl_corpus.py --kapi` |
| Konuşma senaryoları | **düşürülen 0** · 1 ⊘ (`vqr_kalicilik`) | `0619bfd` | `python lab/kapi.py --tam` |
| TypeScript | **0 hata** | `0619bfd`+ | `./node_modules/.bin/tsc --noEmit` |
| ESLint | **0 hata** *(4 eski uyarı)* | `0619bfd`+ | `./node_modules/.bin/eslint .` |

> ⚠ **D2 düzeltmesi (denetim buldu):** damga sütununda sha yerine faz adı yazılmıştı ve
> `--collect-only` *"2056 ✅ · 0 ⊘"* iddiasını **üretemez** (geçen/atlanan ayrımı vermez).
> Tek komut iki iddiaya kaynak gösterilemez — satırlar ayrıştırıldı.
| Deneyim süiti (canlı) | **41 ✅ · 1 ❌ · 63 ⊘** | `88bde2a` | `python lab/deneyim.py --live` |
| VK taban | **§G.6e kutusu** | `8f87e40` | `python lab/vk_taban.py --live` |
| Motor-RLS | **0** | `8f87e40` | `grep -rc rowLevelAccessControl backend/app/` |
| Bayrak | `FLAG_REGISTRY` **16** ↔ `features.yml` **14** | `8f87e40` | — |
| Panel export | **13** *(tavan DOLU)* | `88bde2a` | `grep -rE "export (default )?function [A-Za-z]+Panel" src/ \| wc -l` |
| Konuşma türü | **5** *(v1 hedefi 7)* | `8f87e40` | `grep -cE "^TUR_[A-Z_]+ = " backend/app/followup.py` |
