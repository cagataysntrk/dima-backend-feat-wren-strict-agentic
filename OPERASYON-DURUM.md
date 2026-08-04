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
| **Aktif faz** | **FAZ 1 · GÜVENCE** — *"temel neyse ajan onu çarpar"* (17 madde) |
| **Sıradaki madde** | `1.3b/2` Discovery çağrı yolu (risk sınırı → kendi kapısı) · `1.13` **EN SON** |
| **Demet** | ✅ **`1.12` kapısı 4/4 YEŞİL** (süit **2477**) — risk sınırı olduğu için demete girmedi · demet 13 açık: `1.10`+`1.11` (o kapıya da dahil oldular) |
| 🔴 **Açık borç** | **36 çağrı sitesi kimlik geçmiyor** → `motor_cls=on` KİLİTLİ (kapı engelliyor) |
| **Ondan sonra** | `1.2`·`1.2b` → `1.4` → 🔴 **`1.6` ÖNCE, `1.5` SONRA** *(sıra düzeltmesi, aşağıda)* → `1.7` → `1.8`-`1.12` → `1.13` **EN SON** |
| **Demet** | ✅ **demet 7 kapandı** — FAZ 0 kapanış kapısı **4/4 YEŞİL** (süit **2199**) · demet 8 açık: `1.3c` · `1.3` |
| 🔴 **Kota** | **GÜNLÜK KOTA DOLDU** (2026-08-04 ~11:40; `429`/`503`, tüm sağlayıcılar). Bugün başka **canlı** koşum YOK — LLM'siz ölçümler serbest |
| **Tempo** | 🔴 **DEMET disiplini yürürlükte** (`OPERASYON.md §3`): commit ≠ kapı; tam kapı **demet sonunda bir kez**. Risk sınırındaki dosyalara dokunan madde demete girmez |
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

### FAZ 0 · adım 3 — `0.16` ölçüm bütçesi + koşum hijyeni *(2026-08-04)*

| Parça | Ne indi | Kapı |
|---|---|---|
| **Ayrılmış anahtar** | `DIMA_MEASURE_KEY` (+ `DIMA_MEASURE_PROVIDER`) — ürün trafiğiyle **kota rekabeti biter**. Tanımsızsa davranış **birebir bugünkü** *(GERİ AL)* | `test_OLCUM_ANAHTARI_AYARDA_var` · `test_TANIMSIZSA_BUGUNKU_DAVRANIS` |
| **Kota ön uçuşu** | *"Sağlayıcı kuruldu"* ≠ *"cevap veriyor"*. Tek ucuz çağrı; **429 ya da boş cevap → KOŞMAZ** (fail-closed), hata mesajı çözümü gösterir | `test_KOTA_DOLUYSA_KOSMAZ` · `test_BOS_CEVAP_da_KOSMAZ` |
| **Kaçış kapağı** | Ağ arızası bir turu kilitlemesin diye kapatılabilir — ama **sessiz değil**, *"KORUMASIZ"* diye bağırır | `test_ON_UCUS_KAPATILABILIR_ama_SESSIZ_DEGIL` |
| **Koşum hijyeni** | `--rm` **yasak**, `-d` + `--name` + `docker wait` + `docker rm -f`. *Ölçüldü: `--rm` kütüğü siler ve kabuk ölürse özet **tamamen kaybolur** — bu operasyonda **iki kapı özeti böyle kayboldu*** | `test_KOSUM_HIJYENI_KURALI_YAZILI` |

**Tek sahip:** üçü de `konusma_senaryolari._canli_ortami_geri_yukle`'de — `--live` koşan
**dört aracın dördü de** oradan geçiyor (`deneyim` · `vk_taban` · `nl_accuracy` · kendisi);
tüketicilere tek tek yazmak, dördüncüsünü unutmak demekti. *(Ölçüldü: `faz3a_sema_kazanci`
`--live` yalnız docstring'de geçiyor — içi boş bir canlı mod **yok**.)*

> ⚠ **Kapının kendi kusuru da düzeltildi:** hijyen testi `OPERASYON.md`'yi repo kökünde
> arıyordu ve kapı konteynerine kök **mount edilmediği** için her koşumda `skip` oluyordu.
> **Atlanan bir kapı, kapı değildir** → kural `backend/CLAUDE.md`'ye de yazıldı (her zaman
> mount edilir) ve test iki kaynağı da okuyor.

### 🔵 TEMPO KARARI — **commit ≠ kapı** *(ölçülerek benimsendi)*

Bir turda FAZ 0'ın ~4 maddesi indi ve tam kapı **6 kez** koştu (~90 dk). Ama sürenin
**%75'i kapıda değildi**; madde başına tekrarlanan 10 adımlık döngüdeydi. Ve `--tam`'ın
**dört bileşeninin üçü** o turda **hiç kıpırdamadı**, çünkü onları besleyen dosyalara
dokunulmamıştı. → **Her madde kendi commit'ini alır; tam kapı demet sonunda bir kez.**
**Risk sınırı** (`cube_router · interpret · answer · followup · routers/ask · contribution ·
demo/packs`) demete girmez, kendi kapısını hemen koşar.

**İkinci ağ ölçüldü:** `.github/workflows/backend-ci.yml` her push'ta `pytest -q` koşuyor
ve `tests/test_eval_gate.py` süitin içinde → **eval + süit kapıları CI'da ZATEN VAR**
(`2/4`). 🔴 Bu, önceki turun *"ölçüm kapısı taşıyan 0 workflow"* ölçümünü **çürütür** —
o probe kapıyı **çağıran komuta göre** arıyordu ve başka yoldan koştuğunu göremiyordu
*(ölçüm aracının kusuru, düzeltildi)*. `FAZ 0.15`'in gerçek kapsamı: sıfırdan kurulum
**değil**, mevcut workflow'a **korpus + senaryo** eklemek.

### FAZ 0 · adım 4 — `0.14` beş entegrasyon kapısı *(2026-08-04)*

Kapılar artık **güvenilir**: bu belgenin 100+ maddesi onlara dayanacak.
Ortak iskelet **tek sahipte** (`tests/kapi_ortak.py`) — `0.14`'ün `NASIL`'ı zaten
*"ikinci tarayıcı yazılmaz"* diyordu.

| Kapı | Ne indi | İlk av |
|---|---|---|
| **K1** uç yetimi | **tam yol** eşleştirme (`(?![\w/-])`) + **yorumsuz** tarama + *"sarmalayıcı var, çağıranı yok"* | 🔴 **`GET /contracts`** — alt-dize taraması onu `` `/contracts/${cid}` `` içinde VE bir **yorum satırında** buluyordu. `[KANIT §0.1-5]` kapı tarafından **yeniden üretildi** → FAZ 0.6 |
| **K2** alan yetimi | **(a)** iç içe alanlar · **(b)** `DrillResponse`/`ContributionResponse`/`DecisionIn`/`AskRequest` · **(c)** 🔴 **erişilebilirlik** — *"geçiyor mu"* değil *"ULAŞILABİLİR mi"* | `AskRequest.limit`'in *"tüketiliyor"* sanılması: tek isabet `DrillDownPanel`'deki `limit: 50` = **DrillRequest**; sayaç **sınıf ayrımı yapmıyordu** |
| **K3** ters yetim | **YENİ** — FE'nin okuduğu ama backend'in **vermediği** alan; TypeScript bunu yakalamaz (`types.ts` elle yazılmış bir **beyandır**) | bugün temiz — *kapı temiz kalsın diye kuruldu* |
| **K4** yüzey sadakati | **YENİ** — aynı cevap her yüzeyde **aynı rozeti** basar (MIMARI §5: `source` gizlenemez) | `AnalysisCanvas` rozetsiz → **FAZ 0.3** *(muafiyet SAHİBİYLE, «KALKAR» tarihiyle)* |
| **K5** panel sayısı | **YENİ** — 🔴 **önce TANIM** (export sayımı, `export default` dâhil), sonra sayı, sonra test | **export 13 / tavan 13 · pay 0** — bir panel daha eklenirse anında kırılır |
| **D5** belge kapısı | **YENİ** — `NE`/`KAPI` zorunluluğu · bayraklı maddede `GERİ AL` · *"zaten var"* denen dosya · planlanan kapı sayısı **73** dondurdu | 🔴 **130 maddenin biri** (`−1.2`) `NE`/`KAPI` taşımıyordu — düzeltildi |

> 🔴 **D5'in `GERİ AL` testi `xfail(strict=True)`** — 54 bayraklı maddenin **17'sinde**
> `GERİ AL` yok, **hepsi `II-*`** (v2/v3, bu döngünün dışında). `0.14`'ün kendi kuralı:
> *"Kapı testi geri alınmaz — `xfail` işaretlenir. Bir kapının kırmızısı bir **bilgidir**;
> kaldırıldığında o bilgi de kaybolur."* `strict=True`: 17'si kapandığı gün test
> **beklenmedik geçiş** verir ve işaret kaldırılır.

> ⚠ **Kapı kurarken kapının kendi premisi iki kez kusurluydu** — ikisi de ölçülerek yakalandı:
> · `test_SARMALAYICI_VAR_CAGIRANI_YOK` `ad(` arıyordu → `queryFn: listConversations` gibi
>   **referans** kullanımlarını göremedi, **dört canlı** sarmalayıcıyı *"ölü"* ilan etti.
> · `test_D5_PLANLANAN_DOSYALAR_SAHIPSIZ_DEGIL` *"her planlanan dosyanın bir `KAPI` satırı
>   olmalı"* diyordu ve **metni kovalamaya** başladı (73 → 5 yanlış-pozitif). Ölçülemeyen
>   bir iddiayı zorlamak, kapıyı **yanlış-kırmızı üretecine** çevirir → iddia
>   *"sessizce ARTMAZ"*a daraltıldı.

### FAZ 0 · adım 5 — `0.19` semantik-vaka paydası *(2026-08-04)*

🔴 **ŞİŞME ÖLÇÜLDÜ: 16,2×.** Ham tur paydası bir **kartezyen üründür**
(`ölçü × 11 dönem × boyut`) — yani `elektrik`in **TEK** sahiplik hatası ham paydada
**16 ayrı başarısızlık** olarak sayılıyor. Semantik vaka `(cube, ölçü, niyet)`; dönem ve
boyut çarpımı **tek vakaya çöker**.

| Payda | Değer @`f1050e6` | Not |
|---|---|---|
| **Ham tur** | **%93,2** (6720/7213) | `KURAL A`: **korunur**, geçmiş tabanlar ona bağlı |
| **Semantik vaka** | **%92,1** (410/445) | 🔴 ham sayı **iyimserdi** |

**Sayım KATI (AND):** bir vakanın varyantlarından biri bile yanlış cube'a giderse vaka
**yanlıştır**; Discovery'ye düşmek de bir başarısızlıktır. Gevşek sayım, tek doğru
varyantla bir sahiplik hatasını **gizlerdi**.

> 🔴 **ASIL KAPI — iki payda TERS YÖNE giderse KIRMIZI.** *"Birkaç terimi düzelttim, sayı
> uçtu"* yanılsamasının kapanı: tek bir terimi düzeltmek ham yüzdeyi birkaç puan
> zıplatabilir, **hiçbir yeni semantik vaka kazanılmadan**. **Kanıtlandı:** taban
> ayrıştırıldığında `ÇIKIŞ KODU 1`.

### FAZ 0 · adım 6 — `0.18` METRİK KAYDI = HAKEM *(2026-08-04)*

🔴 **Belgenin tek en büyük ölçülmüş kazancı.** `CLARIFY:konu` %11,5 + yanlış-cube %6,8
≈ **turların ~%18'i**, ve ikisinin de **kanıtlanmış baskın kökü aynı**: bir iş terimi
**iki cube tarafından sahiplenilmiş, hakem yok**. Korpus: boyahane yanlış-cube listesinin
**ilk 10'unun 10'u** `elektrik`; atiksan'ın (**%98, en iyi şirket**) **ilk 9'unun 9'u**
`satış`. Canlı tur aynı sınıfı **bağımsız** buldu: *"bu yıl bakiye"* → `cari` **₺11,86M**,
`mizan` **₺0**.

| Parça | Ne indi |
|---|---|
| **Sınıflandırma** | `app/metrik_kaydi.py` — çakışma envanteri · taslak üretimi · hakem · çift-sahiplik denetimi. **Tek sahip.** |
| **`_match_cube`'un İLK SATIRI** | Paralel yol **değil**: kayıt bir sahip beyan etmişse o kazanır, etmemişse bugünkü zincir **aynen** koşar |
| **Çift sahiplik reddi** | **fail-closed** — iki sahip, hakemsizlikten *daha kötüdür*: hakem yine yoktur ama üstüne *"hakem var"* beyanı eklenir |
| **Sözleşme** | `GET /metrics` — kayıt + çakışan terim envanteri. *(Sahiplik **ekranı** 2.2b'de)* |
| **Bayrak** | `metrik_kaydi = off` → kayıt şemaya **hiç yazılmaz** → `cube_router` görmez → **birebir bugünkü** |

> 🔴 **`cube_router` SAF kaldı.** Bayrak, ayarların erişilebilir olduğu **derleme
> sınırında** (`wren_service.schema()`) durur; sıcak yolda değil. `cube_router` hiçbir
> bayrak okumaz ve bu testle kilitli — sıcak yola bayrak sızarsa determinizm iddiası çürür.

> ✅ **Madde kendi kendine güvenli:** taslak `sahiplenilen_terimler: []` ile gelir, yani
> *"bu terim çakışıyor"* der ama *"sahibi şudur"* **demez**. Karar **FAZ 3.1'in sahiplik
> turudur**. Bu madde **çakışmayı görünür kılar** — görünmeyen bir çakışma düzeltilemez.

> 🔴 **K1 yeni ucu KURULDUĞU ANDA yakaladı:** `GET /metrics` tüketicisiz → `api-only`
> beyanı gerekçesiyle yazıldı. Kapı, kurulmasının üzerinden bir madde geçmeden iş gördü.

### FAZ 0 · adım 7 — `0.5` ÇAPA ZİNCİRİ UYANDI *(2026-08-04)*

**19 altın vakalı, testli bir modül üretimde ÖLÜYDÜ.** `KURAL_CAPA`/`COKLU`/`CELISKI`
hiç ateşlenmiyordu; ölçüldü: `grep -n "capalar=" routers/ask.py` → **0 isabet**.

🔴 **Kök neden engel değil, DÜZLEŞTİRMEYDİ.** `ask.py`'nin yorumu *"thread paneli Faz
H4'te yeniden kurulacak"* diyordu — panel **2026-08-01'de kuruldu**. İstemci çapayı
**zaten biliyordu**, onu **genel `cube_query` yuvasına düzleştiriyordu**; sunucu bu yüzden
hep `KURAL_YAPISAL` görüyordu. *Bayat bir gerekçe kodda kilitli kalmıştı* — madde inerken
yorum da güncellendi ve bu **testle kilitlendi**.

| Parça | Ne indi |
|---|---|
| **sözleşme** | `AskRequest.reply_to_cube_query` + `reply_to_extra_cube_queries` — çapa **kimliğiyle** taşınır; `cube_query` DEĞİŞMEDEN durur |
| **backend** | `coz(..., capalar=…)` bağlandı; tek kart → yanıt, çok kart → **kesişim**, farklı cube → **SOR** |
| **frontend** | `page.tsx` çapayı ve çok-kart seçimini gönderiyor *(`extra_context` insan-okur özet; bu ise **yapısal** sorgu — ayrı alanlar, ayrı iş)* |
| **bayrak** | `capa_zinciri = off` → liste boş → **birebir bugünkü** |

> 🔴 **KAPI KENDİ BOŞLUĞUNU YAKALADI.** İlk koşumda log `kural=capa:karta-yanit` yazıyordu
> ama cevap *"bu takip mesajını ilişkilendiremedim"* diyordu: `coz()` doğru kuralı
> üretiyor, **takip zinciri hâlâ `body.cube_query`'yi okuyordu** — yani çapa **çözülüp
> yok sayılıyordu**. Kullanıcı için sonucu: işaret ettiği karta yanıt verirken cevap
> **başka bir raporun** bağlamına kayıyor, üstelik **sessizce**. Düzeltildi: çözülen çapa
> `KURAL_CAPA`/`KURAL_COKLU`'da **uygulanıyor**; `KURAL_CELISKI`'de **uygulanmıyor** —
> ADR-0008, belirsizlikte tahmin yok.

### FAZ 0 · adım 8 — **ÖLÇÜLMÜŞ YETİMLER KAPANDI** *(0.3 · 0.7 · 0.8 · 0.9 · 0.11)*

[KANIT §0.1]'in envanterinden **beş yetim** kapandı — ve her biri bir **muafiyeti
sildi**. *Yaşayan bir muafiyet, kapının kendisini eritir.*

| Madde | Yetim | Ne yapıldı | Kalkan muafiyet |
|---|---|---|---|
| **0.3** | `AnalysisCanvas` rozetsiz *(SourceBadge 0)* — aynı cevap sohbette `▚ LLM`, tuvalde **rozetsiz** (§5 ihlali) | `ChatPanel.SourceBadge` **yeniden kullanıldı**, ikinci render edici yazılmadı | **K4** `ROZETSIZ_MUAF` → **boş** |
| **0.7** | `runQuery()` sarmalayıcı var, **çağıranı yok** | **Silindi.** Uç duruyor + `api-only` *(ham-SQL yürütme bilinçli olarak kullanıcıya kapalı)* | **K1** `SARMALAYICI_MUAF` → **boş** |
| **0.8** | `agent_run.steps[].receipt` yalnız `types.ts`'te | Adım satırına **⛓ makbuz** — tıklanınca `/contracts/{id}` | `IC_ICE_MUAF` |
| **0.9** | `explain.path` tip var, render yok | Trace bloğuna **yol:** satırı *(rozet «ne» der, yol «nereden»)* | `IC_ICE_MUAF` |
| **0.11** | `DecisionIn.supersedes` **yazılamıyor** | **BAĞLANDI** (silinmedi — II-E.7 ona dayanıyor): revizyon zinciri `PrescriptionLayer`'da | `IC_ICE_MUAF` |

> ⚠ **`AskRequest.execute`/`limit` muafiyeti KALDI — ama gerekçesi DEĞİŞTİ.** Artık
> *"yetim, 0.11'de bağlanacak"* değil: ikisi de `lab/` araçları ve `/ask/verify` için
> **gerçekten kullanılıyor** (SQL üretip **çalıştırmadan** doğrulama). Kaldırmak o yolu
> kırardı. 🔴 Ve K2/(b) burada bir **ölçüm hatası** açığa çıkardı: ham alt-dize taraması
> `AskRequest.limit`'i *"tüketiliyor"* sanmıştı — tek isabet `DrillDownPanel`'deki
> `limit: 50`, yani **DrillRequest**. Sayaç **sınıf ayrımı yapmıyordu**.

### FAZ 0 · adım 9 — `0.12` · `0.13` · `0.6` *(2026-08-04)*

| Madde | Ne indi | Kalkan muafiyet |
|---|---|---|
| **0.12** taban tazeliği | Bugünkü tur tabana eklendi *(kök **dokunulmadı** — KURAL A)* · kapı artık tabanın **yaşını** ve **iki paydayı** kontrol ediyor | — |
| **0.13** sosyal sınıf | 🔴 **Kill-switch GERÇEK oldu:** bayrak `FLAG_REGISTRY` + `features.yml` (`prod`) **ve** `ask.py` gerçekten ona bakıyor. Ad↔iddia çelişkisi + tüketici sayısı (3→**4**) düzeltildi | — |
| **0.6** kanıt geçmişi | `GET /contracts` bağlandı — **`ContractDetailPanel`'in giriş görünümü**, yeni panel **DEĞİL** *(tavan 13/13, pay 0)* | **K1** `/contracts` |

> 🔴 **`0.12` kurulurken KAPI KENDİ KUSURUNU BULDU.** Tabana **şirket rakamı taşımayan**
> bir tur eklenince `_taban_beklenen()` şirket değerlerini **köke (%64)** düşürüyordu —
> yani *bir tur eklemek tabanı SESSİZCE geriletiyordu* ve sonraki kapı 5 puanlık bir
> gerilemeyi **yeşil** görürdü. Kök neden: yalnız **son** tur birleştiriliyordu.
> Artık **tüm turlar sırayla** birleşir (son **beyan eden** kazanır) ve bu
> `test_TUR_EKLEMEK_TABANI_GERILETMEZ` ile kilitli.

> 🔴 **`0.13`'ün asıl borcu bayrağın KENDİSİYDİ.** MIMARI §6.13z/9.11: *"bir kill-switch
> yalnız KOD'da varsa **YARIMDIR**."* Sınıf çalışıyordu ama **geri alma yolu yoktu**.
> Kapı `cube_router`'a değil **çağırana** kondu — `cube_router` hiçbir bayrak okumaz
> (FAZ 0.18'in değişmezi); sıcak yola bayrak sızarsa determinizm iddiası çürür.

> ✅ **Dört muafiyetin dördü de kalktı** (`K1` × 2 · `K4` · `IC_ICE` × 3). Bir muafiyetin
> metni *"…'de KALKAR"* diyorsa, o faz indiğinde **silinmesi** gerekir; yaşayan muafiyet
> kapının kendisini eritir.

### FAZ 0 · adım 10 — `0.10` + `0.10b` GÖRÜNEN ADLAR *(2026-08-04)*

🔴 **Canlı kullanıcı turunun şikâyeti kapandı.** Ekranda şu görünüyordu:
*"En yüksek **tarih__year: 2026-01-01 00:00:00** (454.477,90, toplamın %100,0'i)"* —
kullanıcı: *"Ben yıl sordum, bana **veritabanı sütun adı** ve **saat 00:00** gösteriliyor."*

| Parça | Ne indi |
|---|---|
| **0.10** | `FACT_ICON`'a **`top`** — `interpret` bu fact'i üretiyordu ama sözlükte olmadığı için filtre onu **sessizce eliyordu**. *"En yüksek makine: RAM-2"* bir raporun en çok işe yarayan cümlesidir ve rozet listesinde hiç görünmüyordu |
| **0.10b** | `interpret(..., etiketler=…)` — fact metinleri **görünen ad** basıyor; sözlükte yoksa `tarih__year` → `tarih · year` |

> 🔴 **İKİNCİ ETİKET KAYNAĞI AÇILMADI.** Etiketler `build_catalog`'dan gelir —
> `eylem._rapor_adi` ve `cube_router.next_step_chips` ile **aynı kaynak**.
> `eylem.py:241`'in kendi uyarısı: *"bu depoda «ikinci bir etiket kaynağı» deseni
> **beş kez** ayrışmayla sonuçlandı."* Testle kilitli: `interpret.py` kendi etiket
> kaynağını kuramaz.

> ✅ **`t2_anlatici`'nin SERT ÖN KOŞULU karşılandı.** Bu metin `answer._anlati_ekle`'de
> LLM'e `gercekler` **girdisi** oluyor; `0.10b` inmeden bayrak açılsaydı model
> `toplam_fire_kg` **etrafında cümle kurardı** — akıcı ama iç adlı bir cümle robotikliği
> kaldırmaz, **üstüne para ödetir**.

> ⚠ **Geriye uyum testle kilitli:** `etiketler=None` iken metin **birebir bugünkü**.
> Bir iyileştirme, kendi yokluğunda davranışı değiştirmemelidir.

### FAZ 0 · adım 11 — `0.15` CI KAPILARI · **§C/8 hedefine ulaştı** *(2026-08-04)*

🔴 **Sıralama hatası düzeltildi.** Bu madde başta **FAZ 4.1**'di: regresyon ağı,
belgenin kendi ifadesiyle *"en yüksek etki alanlı faz"* olan **FAZ 2**'nin semantik
ameliyatından **SONRA** kurulacaktı. Oysa `elektrik` deneyi tam orada erişimi
**%64 → %56** düşürmüştü — doktrin (*"düzelt → kapıya çevir"*) **tersine** işliyordu.

**Yeni kod YOK.** Koşucu (`lab/kapi.py --tam`) zaten yazılmıştı; eksik olan onu
**çağıran workflow**du. `.github/workflows/nightly.yml`: gecelik + elle tetik, raporlar
`if: always()` ile yükleniyor *(kırmızıda kanıt kaybolmaz)*.

| §C/8 | Önce | Sonra |
|---|---|---|
| Ölçüm kapıları CI'da | **2/4** *(eval + süit — `pytest -q` içinde)* | ✅ **4/4** |

> 🔴 **Bu maddenin en öğretici kısmı ölçüm aracının kendisiydi.** `olcut_8_ci` probe'u
> **iki kez** yanıldı ve ikisi de aynı sınıftan: *"bir kapıyı, onu ÇAĞIRAN KOMUTA göre
> aramak."*
> · İlk sürüm yalnız `eval.run|nl_corpus|kapi.py` dizelerini arıyordu → `pytest -q`
>   içinde koşan `test_eval_gate.py`'yi göremedi, **"0 kapı"** dedi.
> · Düzeltilince bu kez `kapi.py --tam`'ın **dördünü birden** koştuğunu göremedi,
>   **"korpus eksik"** dedi.
> Doğru ölçüm: **koşucunun NE KAPSADIĞINI** bilmek. `--tam` dört kapının **tek sahibidir**.

> ⚠ **Gecelik, her push'ta DEĞİL** — ve bu testle kilitli. Tam kapı ~15 dk; her commit'e
> bağlamak, demet disiplinini **araç seviyesinde** çiğnemek olurdu.

### FAZ 1 · adım 17 — `1.12` **AI Act / NIST RMF / ISO 42001 karşılığı** *(2026-08-04)*

**Kendi tam kapısı: 4/4 YEŞİL** — süit **2477** (7 atlanan · 3 xfail, 8 dk 42 sn) ·
eval **±%0** · korpus **%93,1** (taban %93,2) · senaryolar **düşürülen 0** · 1 ⊘ (`vqr_kalicilik`).
Kapı: **31 test** (`tests/test_ai_act_uyumu.py`), hızlı sinyal **949**.
🔴 **Risk sınırı** (`answer.py` · `routers/ask.py`) → demete girmedi, **kendi kapısını hemen** koştu.

> ⚠ **Yürürlük TARİHİ kapıya çevrilmedi.** Yol haritası *"Md.50 2 Ağustos 2026'dan
> yürürlükte"* derken yanına **kendi eliyle** `[DOĞRULANMADI — birincil kaynak EK F'ye
> eklenecek]` yazmış. Kapı **tarihi doğrulamaz**, yükümlülüğün **kod karşılığının var
> olduğunu** doğrular ve bunu **kendi içinde** yazılı tutar. *Doğrulanmamış bir tarihi
> kapıya çevirmek, ölçmediğimiz bir şeyi ölçtük gibi göstermek olurdu.*

> **Md.50 · içerik işareti:** `ai_generated_prose` — 🔴 **sayı değil, ÜSLUP.** Sayıyı bu
> üründe her zaman küp koyar ve `narration_guard` eşleşmeyen sayı taşıyan cümleyi
> **düşürür**; işaretlenmesi gereken şey **metnin makine yazımı olduğudur**. Ekranda
> **anlatının yanında** durur, kartın tepesinde değil — tepedeki bir rozet *"bu cevabın
> TAMAMI yapay zekâ ürünü"* diye okunurdu ve tablo/sayı/kırılım küpten gelirken bu
> **yanlış** olurdu.

> **Kanıt sınıfı:** `kanit_sinifi ∈ {olculmus, probabilistik}` — ⚠ skaler bir *"güven"*
> **uydurulmadı** (MIMARI §5: *kalibre edilmediği sürece o sayı güven değil **süstür***).
> `cube+llm` **probabilistik** sayılıyor: sayı küpten gelse bile **alan seçimi**
> olasılıksaldır ve seçim yanlışsa **doğru sayı yanlış soruya cevap** olur. **Bugünden**
> eklendi ki geçmiş kayıtlarda *"ölçülmüş mü tahmin mi"* sorusu cevapsız kalmasın.

> **Md.14 · durdurma:** `DELETE /ask/jobs/{id}` + `DurdurDugmesi` (sol **ve** sağ panel).
> 🔴 **İptal işi ÖLDÜRMEZ, sonucunu YAYIMLATMAZ** — thread'i zorla sonlandırmak yarım
> yazılmış bir sonuç/kayıt bırakabilirdi. Koşucunun **iki dalı da** (başarı ve hata)
> durumu yazmadan önce soruyor; durduğu için `failed` **demiyor**. Akışa ayrı bir `iptal`
> olayı eklendi: dalsız bırakılsaydı düğme UI'yi **6 dk dönerken** bırakırdı.

> 🔴 **KENDİ SINAMAM KENDİ KUSURUMU GÖREMEDİ — ve bu düzeltildi.** İlk sürüm iptali
> süreç-içi bir `set()`'te tutuyor, durumu `request.app.state.ask_jobs`'tan okuyordu:
> **öyle bir depo yok** (işler `AskJob` tablosunda). Uç *"böyle bir iş yok"* demekten
> başka bir şey yapamazdı — ve sınama bunu göremezdi çünkü **o olmayan deponun sahtesini
> kuruyordu**. İki tanıdık sınıf birden: *"beyan var, kod onu tanımıyor"* + *"testler
> METNİ ölçtü, davranışı değil"*. Depo artık `AskJob` satırıdır; durum adları (`completed`
> /`failed`) modelin **kendi sözlüğünden** doğrulanıyor.

> **Md.13 · denetleyici-okunabilir ihraç:** `GET /audit/export` (JSON-LD/PROV-O) —
> ⚠ **ikinci bir eşleme yazılmadı**: standart adlara çeviri `1.8`'in `otel_nitelikleri`'nde
> zaten vardı, ikincisi iki ihracın **farklı adlar** kullanması demekti. İhraç
> `zincir_bulgulari`'yı **birlikte** taşır — *bir kanıt defterini bütünlük raporu olmadan
> teslim etmek, "işte kayıtlarım" deyip **eksik olup olmadığını söylememektir**.* Kırpma
> da sessiz değil (`toplam`/`kirpildi`). Ekran tüketicisi **yeni panel açmadan**
> `ContractDetailPanel`'e kondu — ihracın yetkisi (`contract:read`) o panelin yetkisiyle
> **aynı**; K5 tavanı 13/13, pay 0.

> **Md.12/19 · saklama:** `TenantConfig.audit_saklama_gun` — ⚠ **SİLME YAPMIYOR, POLİTİKA
> BEYAN EDİYOR.** Bir saklama süresini uygulamak geri alınamaz bir **silme** eylemidir ve
> FAZ 6'nın onay değişmezine bağlıdır. *Beyan edilmiş ama uygulanmamış bir politika,
> beyan edilmemiş bir politikadan iyidir: denetleyici ne beklediğimizi okuyabilir.*
> Göç `f8c1e3a7d259` (tek head).

> ✅ **ÖLÇÜM ARACININ KENDİSİ DÜZELTİLDİ (`0.21`).** `ask.py` dosya tavanı `TAVAN_ASK_KOD
> + 1259` idi; yani **modül düzeyine** eklenen bir satır için muafiyet yazmak `ask()`
> **gövdesinin** tavanını da yükseltirdi — ve `ask()` tam tavanında (1147/1147) duruyor.
> Dosya muafiyeti artık **ayrı liste** (`MUAFIYET_ASK_DOSYA`, Δ=9, gerekçesi satır satır
> yazılı) ve `ask()` tavanına **dokunmuyor**; yeni kapı bunu doğruluyor.
> *Bir tavanı yanlışlıkla yükselten muafiyet, muafiyet değil sessiz bir tavan artışıdır.*

> ✅ **`1.2c`'nin tümleyeni kendini kanıtladı:** `AskResponse` 29 → **31** alan oldu ve iki
> yeni alan için maskeleme tarafına **hiçbir şey yazılmadı** — yine de kapsandılar. Sayılan
> bir liste olsaydı ikisi de sessizce dışarıda kalırdı. (`pii.py`'nin ölçüm notu güncellendi;
> kapı bayat sayıyı yakaladı.)

> ⚠ **Metin tarayan kapı, kendi belgesini yakaladı — bu oturumda 6. ve 7. kez.** `"_IPTAL"
> not in kaynak` sınaması `DURUM_IPTAL` **sabitinin adını**, `"state.ask_jobs"` sınaması
> ise modülün **kendi hata anlatısını** yakaladı. İkisi de **AST'ye** çevrildi.
> *Belgeyi tarayan bir kapı, hatayı ANLATMAYI cezalandırır.*

### FAZ 1 · adım 16 — `1.10` **eskalasyon matrisi** *(2026-08-04)*

**Demet 12 kapısı: 4/4 YEŞİL** — süit **2426** · eval ±%0 · korpus **%93,1**.
Kapı: **23 test**, hızlı sinyal **564**.

> **Neden:** bir eşik aşıldığında bildirim gider — ve orada **biter**. Kimse bakmazsa
> sistem *"haber verdim"* der ve susar. Ama bir uyarının **işlevi** haber vermek değil,
> **bir karara yol açmaktır**: *on iki saat kimsenin bakmadığı bir alarm, hiç
> gönderilmemiş bir alarmla aynı sonucu üretir.*

> ✅ **YENİ CRON YOK** (yol haritası birebir). Değerlendirici **mevcut 60 sn** döngüsüne
> bindi. İkinci bir zamanlayıcı iki ayrı *"şimdi saat kaç"* sahibi yaratırdı ve ikisi
> kaydığında hangi kuralın ne zaman koştuğu **bilinemezdi**. Kapı bunu **AST ile**
> ölçüyor: `_scheduler_loop` **bir tane** ve eskalasyon onun **içinden** çağrılıyor.

> 🔴 **KİLİTLEME UYGULANMIYOR — KARAR ÜRETİLİYOR.** Bir hesabı otomatik kilitlemek
> **geri alınamaz** bir kullanıcı etkisidir ve FAZ 6'nın *"onaysız hiçbir yazma"*
> değişmezine bağlıdır. Kararı üretip **uygulamamak** bir eksiklik değil, o değişmezin
> **korunmasıdır** — ve karar `AuditLog`'a yazıldığı için **görünürdür**.
> *Uygulanmayan ama kaydedilen bir karar, uygulanan ama kaydedilmeyen bir karardan her
> zaman daha iyidir.* Kapı, modülde `suspend`/`lock`/`delete` gibi bir **eylem**
> olmadığını da doğruluyor; kararın **sahibi** (FAZ 6.1) yazılı.

> ⚠ **Üç fail-safe dal, üçü de gerekçeli:** `ilk_asim=None` → tetiklenmez (`None`'ı
> *"çok eski"* saymak hiç tetiklenmemiş bir kuralı **anında ve her 60 sn'de** yükseltirdi)
> · gelecekteki zaman → tetiklenmez (saat kayması bir gerekçe değildir) · `sure_dakika=0`
> → varsayılana düşer (kural **sürekli** tetiklenirdi).
> ⚠ **`owner`'da yükselme YOK:** kendisine yükseltmek bir **döngü** ve sonsuz audit satırı
> üretirdi; orada artık **insan kararı** bekler.
> ⚠ **Eşik mantığı bu modülün işi DEĞİL** — `asim_zamani` bir **çağrılabilir**; buraya bir
> sorgu koymak eşik mantığının **ikinci bir sahibini** doğururdu. Rol merdiveni de
> `authorize.ROLE_RANK`'ten **türetiliyor**, kopyalanmıyor (kapı ikisini karşılaştırıyor).

### FAZ 1 · adım 15 — `1.11` **kademeli düşüş: kayıt + gösterge** *(2026-08-04)*

Kapı: **16 test**, hızlı sinyal **699**.

> ✅ **YOL HARİTASI HAKLIYDI: «yeni kod YOK».** `FailoverSqlGenerator` **zaten** sırayla
> deniyordu. Eksik olan iki şeydi: **kayıt** (bir düşüş `AuditLog`'a **hiç** yazılmıyordu,
> yalnız bir `WARNING` kütüğü vardı — *kütük aranabilir değildir*; *"dün kaç kez ikinci
> seviyeye düştük"* sorusu **cevapsızdı**) ve **gösterge** (kullanıcı hangi seviyede cevap
> aldığını **göremiyordu**).

| seviye | ne | kullanıcıya |
|---|---|---|
| **1** | birincil LLM | normal (yeşil) |
| **2** | yedek LLM | *"birincil yanıt vermiyor"* (amber) |
| **3** | `rule` — **LLM YOK** | 🔴 **kategorik olarak farklı** cevap (amber + halka) |

> 🔴 **SEVİYE 3 BİR HATA DEĞİL BİR DURUMDUR.** Sistem **çalışıyor**, ama cevaplar
> **kategorik olarak farklı** bir yoldan geliyor. Kırmızı göstermek kullanıcıyı **yanlış
> eyleme** (sistemi yeniden başlatmaya) iterdi — *"çalışıyor ama LLM yok"* ile *"hiç
> çalışmıyor"* aynı şey değildir ve aynı renk kanalını paylaşamazlar.

> ⚠ **ÜÇ SEVİYE, sağlayıcı sayısı DEĞİL.** Failover beş sağlayıcı taşıyabilir; *beş
> seviyeli bir gösterge, kullanıcının kararını değiştirmeyen bir ayrımı ekrana taşırdı.*
> Seviye 2↔3 farkı **kararı değiştirir**; gemini↔groq farkı **değiştirmez** — ve o yüzden
> gemini→groq geçişi audit'e **yazılmaz**: *gürültüyle dolan bir kanıt defteri okunmaz olur.*

> ⚠ **Sıra 0 her zaman seviye 1 DEĞİLDİR:** anahtarsız bir kurulumda `rule` **birinci**
> sıradadır ve zaten seviye **3**'tür. Sırayı seviyeyle karıştırmak, LLM'siz bir kurulumu
> *"normal"* gösterirdi.

> 🔴 **KENDİ SINAMAM GİZLİ BİR VARSAYIM BULDU.** `dusus_kaydi` önceki **üreticiyi** alıp
> seviyesini `sira=0` ile hesaplıyordu — *"önceki her zaman listenin başıdır"*. Aynı
> üretici, aynı seviye, yine de bir **olay** üretiyordu. *Gizli bir varsayım, doğru olduğu
> sürece görünmez; yanlış olduğu gün açıklanamaz bir kayıt bırakır.* Taban seviye artık
> **açıkça** veriliyor.

> ⚠ **Yeni bir UÇ AÇILMADI:** rozet `/schema`'yı **zaten** yokluyor. İkinci bir poll, aynı
> bilgiyi iki kanaldan taşımak ve ikisinin **ayrışması** demekti.
> ⚠ **Kayıt hatası cevabı DÜŞÜRMÜYOR:** kademeli düşüş bir **dayanıklılık** mekanizmasıdır;
> onu **kayıt** yüzünden kırmak amacının tam tersi olurdu.

> ⚠ **Metin ölçme kusuru BEŞİNCİ kez** — bu kez `seviye === 3`'ün **ilk** geçişi (etiket
> dalı) ölçüldü, renk dalı değil. Kapı artık **renk bloğunu** soruyor.

### FAZ 1 · adım 14 — `1.9` **numeric fidelity zorlaması** *(2026-08-04)*

Kapı: **13 test**, hızlı sinyal **508**.

> 🔴 **YOL HARİTASININ SAYDIĞI ÜÇ YÜZEY BUGÜN YOK — ölçüldü.** Madde *"`izinli_degerler()`
> yeni türevleri kapsar (MASE · kırılma-noktası % · karar rozeti %)"* diyor;
> `grep` → **0 isabet**. Olmayan metrikler için türetme eklemek, bu deponun avladığı
> *"beyan var, karşılığı yok"* sınıfının **kendisi** olurdu: kapı genişler, koruduğu bir
> şey olmaz, ve genişlemenin **doğru olup olmadığı hiç ölçülemez**.
> → İnen şey maddenin **kalıcı** yarısı: **zorlama mekanizması**. Üç yüzey birer **tuzak**
> olarak dondu — doğdukları gün test **kırılır** ve beyan edilmelerini zorlar.

> ✅ `narration_guard.dogrula` **araç kaydına girdi** (`makbuz=None`, **kapıdır**).
> Kayıtta **görünmeyen** bir kapı, planlayıcının **bilmediği** bir kapıdır: yeni bir
> anlatı yüzeyi onu atladığında bu bir *"unutma"* değil, *"kaydın söylemediği bir şeyi
> bilmemek"* olur.

> 🔴 **MEVCUT KAPI GERÇEK BİR ANLAM HATASI YAKALADI.** Guard'ı `anlatim` etiketiyle
> kaydettim; planlayıcının **DETERMİNİSTİK-ÖNCE** kuralı onu `llm.anlat`'ın **alternatifi**
> sandı ve LLM aracını **reddetti** (`AracReddi: llm.anlat: DETERMİNİSTİK-ÖNCE ihlali`).
> Üç T2 testi anında kırmızı verdi. **BİR KAPI, BİR ALTERNATİF DEĞİLDİR:** guard anlatı
> **üretmez**, üretileni **doğrular**. Aynı etiketi paylaşmak `KAT-1`'in (*bir mekanizma =
> bir iş*) ihlaliydi → etiket `dogrulama` oldu.

> ⚠ **KD-21 sınırı ölçüldü ve donduruldu:** guard **rakamsız** cümlede **yetkisizdir**.
> Yeni yüzeyler **sayı taşıyan** cümleler üretmelidir, yoksa kapı onları **görmez** ve
> *"guard'dan geçti"* cümlesi **karşılıksız** kalır.

> ⚠ **Beyan kanalı iki adla anılıyor** (`izinli_degerler(ek=)` · `dogrula(ek_degerler=)`)
> — ilk yazımda yanlış adı kullandım ve test takıldı. Yeniden adlandırmak ölçülmüş bir
> kazanç getirmiyor (churn); farkın **yazılı olması** yeterli. Kanal artık **uçtan uca**
> sınanıyor (`guvenli_anlatim` → `dogrula`): yalnız iç fonksiyonu test etmek, dışa açık
> yolun kanalı **geçirdiğini** kanıtlamazdı.

### FAZ 1 · adım 13 — `1.8` **audit zinciri** *(2026-08-04)*

**Demet 11 kapısı: 4/4 YEŞİL** — süit **2376** · eval ±%0 · korpus **%93,1** (taban %93,2).
Kapı: **18 test**, hızlı sinyal **562**.

> 🔴 **«APPEND-ONLY» BİR BEYANDIR, BİR MEKANİZMA DEĞİL.** `AuditLog`'un docstring'i
> *"append-only erişim kanıtı"* diyordu; ama bir satır `DELETE` edilirse geriye **hiçbir
> iz** kalmıyordu. *Bir kanıt kaydı, eksildiğini **kendisi** söyleyemiyorsa kanıt değildir.*
> Her kayıt artık bir öncekinin hash'ini taşıyor (ilki `genesis`).

> ✅ **ÜÇ BULGU SINIFI, ÜÇÜ DE ADIYLA:** `KOPUK` (silme/değiştirme) · `BOZULMUŞ` (içerik
> hash'iyle uyuşmuyor) · `ÇATAL` (eşzamanlı yazım). Üçünü tek bir *"zincir bozuk"*
> mesajına indirmek **hangi** olayın yaşandığını gizlerdi — ve **silme** ile
> **eşzamanlılık** çok farklı şeylerdir.

> 🔴 **ZİNCİRİN ETMEDİKLERİ DE YAZILI — ve testle kilitli.**
> · Eşzamanlı yazımları **sıralamaz** (çatal mümkün) — ama çatal **tespit edilir**.
> Kilitle serileştirmek her audit yazımına kilit maliyeti bindirirdi.
> · **Son** kaydı silmek zinciri **koparmaz** (ondan sonra kimse yok). Bunu *"tespit
> ediliyor"* diye yazmak **olmayan bir garanti satmak** olurdu; harici bir çıpa (dış zaman
> damgası / WORM) gerekir ve bu maddede **yok** — o yüzden *"korunuyoruz"* denmiyor.
> Sınırın kendisi bir **testle** dondurdu.

> 🔴 **OTel GenAI: YENİ KOLON YAZILMADI, EŞLEME YAPILDI.** Ölçüldü — veri **zaten**
> oradaydı (`llm_model` · `llm_input_tokens` · `llm_output_tokens` · `llm_latency_ms` ·
> `source`). OTel adlarıyla ikinci bir kolon kümesi açmak aynı gerçeğin **iki kopyası**
> olurdu ve ikisi zamanla ayrışırdı. `otel_nitelikleri()` bir **çeviricidir**, bir depo
> değil — ve yalnız **dolu** alanları yayınlar: OTel'de eksik bir nitelik **yokluktur**,
> `gen_ai.usage.input_tokens=null` *"ölçüldü ve sıfırdı"* gibi okunur.

> ⚠ **Zincir hatası kaydı DÜŞÜRMÜYOR.** Bir kanıt kaydını *"zincir kurulamadı"* diye
> düşürmek, korumaya çalıştığı şeyi **yok etmek** olurdu — ve eksik hash zaten
> doğrulamada **görünür**.

### FAZ 1 · adım 12 — `1.7` **tazelik merdiveni** *(2026-08-04)*

`grep -rl freshness backend/app/` → **0** idi. `SyncState.last_synced_at` yalnız admin
klon yolundaydı ve `/ask`'e **hiç ulaşmıyordu**: kullanıcı *"8 gündür veri gelmiyor"*u
**göremiyordu** — ve *"bu sayı neden düşük?"* sorusunun **en sık gerçek cevabı** budur.
Kapı: **25 test**, hızlı sinyal **677**.

| kademe | sayı gösterilir mi |
|---|---|
| `taze` | ✅ işaret bile yok |
| `uyari` | ✅ **ama** dalgalı turuncu çizgiyle |
| `hata` | 🔴 **HAYIR** — yerine açıklama kartı |
| `bilinmiyor` | 🔴 **HAYIR** — `hata` ile **aynı** muamele |

> 🔴 **B4 — BİLİNMEYEN TAZELİK, TAZE DEĞİLDİR.** Kaynak planlar bunun **tersini**
> yazıyordu; yol haritası *"bugünkü davranıştan **kasıtlı bir sertleşme**"* diye
> düzeltti ve burada o düzeltme uygulandı. Ölçemediğimiz bir şeyi **iyi** varsaymak,
> `⊘ ÖLÇÜLEMEDİ` üçüncü hâlinin tam tersi olurdu. *Sekiz gün eski bir sayıyı normal gibi
> göstermek, kullanıcıyı yanlış bir karara götürür — ve o karar geri alınamaz.*

> 🔴 **TEK SAYI YAPILANDIRILIR, İKİ EŞİK TÜRETİLİR.** `warn_after` ve `error_after` ayrı
> ayrı ayarlanabilseydi biri ötekini geçebilirdi (`warn=10g`, `error=3g`) ve kullanıcı
> `uyari`'yı **hiç görmeden** `hata`'ya düşerdi. *Çelişebilen iki ayar, çelişecek
> demektir.* `TenantConfig.tazelik_periyot_saat` tek sayı; eşikler **2×** ve **5×**.

> ⚠ **`son_veri_ts` son BAŞARILI SENKRONdur, verinin kendi damgası DEĞİL** — ve ayrım
> yazılı, çünkü boru hattı çalışıp **boş** dönebilir. Keskin sinyal (zaman boyutunun
> `max()`'ı) **her soruda ek bir DB sorgusu** ister; FAZ 0.17'nin gecikme bütçesi tam
> bunun için kurulmuştu ve karar **ölçülmeden alınmadı**.

> ⚠ **Gelecekteki bir zaman damgası → `bilinmiyor`**: saat kayması bir tazelik kanıtı
> değildir; *"çok taze"* diye okumak bozuk bir saati **güvence** yapardı.
> ⚠ **`uyari` farklı bir görsel kanal** kullanıyor (dalgalı alt çizgi), güven rozetinin
> emoji kanalıyla **yarışmıyor** — iki uyarı üst üste binerse ikisi de okunmaz.

> ✅ **`1.2c`'NİN TÜMLEYEN KAPISI ATEŞLEDİ VE İŞ GÖRDÜ.** `AskResponse` **26 → 29** alana
> çıkınca `test_ASKRESPONSE_ALAN_SAYISI_KAYITLI` kırmızı verdi. Üç yeni alan **varsayılan
> olarak maskeleniyor** (doğru sınıf); tek yapılan ölçüm notunu güncellemek oldu.
> *Sayma-değil-kapat deseninin bedeli bir satır, kazancı bir sessiz sızıntı.*

### FAZ 1 · adım 11 — `1.5` **metrik sertifikasyonu** *(2026-08-04)*

`source=cube` rozeti *"deterministik bir yoldan geldi"* der — doğru ama yetersiz.
Cevaplamadığı soru: *"bu metriğin tanımını **kim onayladı**, ve o onaydan beri **tanım
değişti mi**?"* Bir metrik **doğru hesaplanıp yanlış tanımlanmış** olabilir; determinizm
onu yakalamaz. Kapı: **17 test**, hızlı sinyal **883**.

> ✅ **B8 üç kapıdan da düşüyor:** tanım (`definition_hash`) · **üst-akış kolon kümesi**
> (`lineage_set_hash`, `1.6`'dan) · TTL **90 gün**. Birden fazla neden varsa **hepsi**
> yazılır — bir kapının düşmesi ötekini gizlemez.

> 🔴 **ÇÜRÜYEN SERTİFİKA SİLİNMEZ:** seviyesi **korunur**, üstüne bayrak düşer. Silmek,
> *"hiç sertifikalanmamış"* ile *"sertifikalanmış ama tanım değişmiş"*i karıştırırdı — ve
> ikincisi kullanıcı için **daha bilgilendiricidir** (biri bu metriğe bakmış, sonra dünya
> değişmiş). Çürümüş sertifika **kademe vermez**, `⚠` verir: çürük bir onayı
> *"sertifikalı"* diye göstermek rozeti bir **süse** çevirirdi.

> ⚠ **TANIMIN KENDİSİ SAKLANMIYOR** — hash bir **parmak izidir**: değişip değişmediğini
> söyler, neyin değiştiğini değil, ve sertifikanın sorduğu soru tam olarak *"değişti mi"*.
> Tanımı kopyalamak aynı gerçeğin **ikinci bir kaynağı** olurdu.
> ⚠ **Sinonim eklemek sertifikayı DÜŞÜRMEZ:** bir eşanlamlı **tanımı** değiştirmez, yalnız
> **bulunabilirliği** artırır — hash'e katmak sertifikayı katalog bakımının **her turunda**
> düşürürdü ve *gürültüyle ateşleyen bir kapı kapatılır*.

> ⚠ **Frontend: rozetin KADEMESİ, yeni panel DEĞİL** (K5 tavanı **13/13**, boşluk 0).
> Kademe kararı **backend'de**; frontend'de ikinci bir eşik kümesi *"aynı kuralın iki
> sahibi"* olurdu — kapı frontend'de `definition_hash`/`90` gibi **sızıntı** arıyor.

> 🔴 **BİR KAPI, KENDİ ÖLÇÜM HATAMDAN DOĞDU.** `down_revision`'ları **tek tırnak**
> varsayan bir betikle **iki Alembic head'i** ölçtüm ve *"canlı bir göç engeli"* ilan
> ettim. Alembic'in **kendisine** sorunca **tek head** çıktı (`a4d8f2c6e903` çift tırnak
> kullanıyor). *Olmayan bir soruna yama yazmaktan, aracın kendisine sormak kurtardı.*
> Kapı artık Alembic'in **kendi grafiğini** kullanıyor: iki head gerçekten oluşursa
> `alembic upgrade head` patlar ve Postgres dağıtımı **göç edemez**.

> ⚠ **Metin ölçme kusuru bu oturumda DÖRDÜNCÜ kez** (`⟳` sayacı · `0.21` tavan operatörü ·
> `TODO(faz-2)` · burada *"yeni panel DEĞİL"* cümlesinin **satır sonuna bölünmesi**).
> Dördü de yapısal ölçüme çevrildi.

### FAZ 1 · adım 10 — `1.6` **kolon kökeni** *(2026-08-04)*

**Demet 10 kapısı: 4/4 YEŞİL** — süit **2308** · eval ±%0 · korpus **%93,1** (taban %93,2) ·
senaryo dokuz sınıf tabanda. Kapı: **26 test**, hızlı sinyal **577**.

> 🔴 **KİLİT İŞE YARADI — VE BİR SAYIYI DÜZELTTİ.** `gitas` korpusa **geri döndü**
> (semantik payda **342 → 445**). Bu, bir önceki turda yazdığım bir cümleyi **çürütüyor**:
> *"korpusun +1,1 puanı AJ0 düzeltmesinden"* demiştim. **Yanlış.** O artış `gitas`'ın
> düşmesinin **yarattığı şişmeydi**; `gitas` dönünce sayı %94,3 → **%93,1**'e indi.
> AJ0 düzeltmesinin korpus etkisi **≈0** (gürültü içinde) — çünkü **korpus typo yolunu
> yapısal olarak göremez** (soruları katalogdan üretilir, hepsi doğru yazılmıştır).
> *Bir sayının yükselmesi, ölçülen kümenin değişmediğini kanıtlamaz.*

`1.6` · **kolon düzeyi köken.** `answer.koken()` **ilişki** düzeyindeydi (*hangi kırılım
hangi join'den*); bu **kolon** düzeyi: *"bu sayı hangi tablonun hangi kolonundan, hangi
DÖNÜŞÜMLE geldi?"* İkisi farklı sorulardır ve biri ötekinin **yerine geçmez**.

> ✅ **YENİ BİR BEYAN YAZILMADI.** Dönüşüm tipi **manifestten türüyor** — ölçü `expression`'ı
> zaten oradaydı, yalnız **sorulmuyordu**: `SUM`/`COUNT`→`toplam` · `AVG`/bölme/`*100`→
> `oran` · `CASE WHEN`/`FILTER`→`filtre` · düz kolon→`dogrudan` · ilişki→`birlestirme`.
> Bir `lineage:` alanı beyan ettirmek **ikinci bir kaynak açmak** olurdu.

> 🔴 **«BİLİNMİYOR» ≠ «HİÇ SORULMADI».** Discovery ham SQL'inde `cube_query` yoktur;
> köken türetilemez. `"bilinmiyor"` bir eksiklik değil bir **beyandır** — `⊘ ÖLÇÜLEMEDİ`
> üçüncü hâliyle aynı disiplin.

> 🔴 **ŞABLONLARIN TEK SAHİBİ BACKEND.** Cümleleri frontend'de üretmek *"aynı kuralın iki
> sahibi"* olurdu ve ikisi ayrışıp kullanıcıya **aynı kanıtı farklı cümlelerle** gösterirdi.
> Kapı frontend'de şablon **kopyası** aramıyor — **olmadığını** doğruluyor.
> **KD-13:** ham köken **yapısı** (graf) frontend'e **basılmıyor** — kullanıcının sorusu
> *"bu sayı nereden geldi"*dir ve cevabı bir **cümledir**; graf bir geliştirici artefaktıdır
> (`D3`'ün *"geliştirici katmanı son kullanıcıda"* kusurunun tekrarı olurdu).

> ⚠ **ÜÇÜNCÜ CÜMLE BİLİNÇLE GELMEDİ.** *"Bir üst-akış tablo N gün önce değişti"* **FAZ
> 1.7**'nin verisini ister (`SyncState.last_synced_at`) ve o veri `/ask`'e **hiç ulaşmıyor**
> (`grep -rl freshness backend/app/` → **0**). Uydurma bir gün sayısı, `pvm:`/`target:`
> eşleştirmesinde **reddedilen** şeyin aynısı olurdu: **güvenle yanlış** bir sayı.

> ✅ **SIRA DÜZELTMESİ İŞE YARADI:** `1.6` önce indiği için `1.5`'in `lineage_set_hash`'i
> artık **üretilebilir**. Bugünkü sırayla `1.5` inseydi o alan ya **uydurulur** ya **hep
> `None`** olurdu.

> ⚠ Bayrak kaydını yanlış şemayla yazdım (`stage`/`owner`/`note` yerine
> `label`/`description`/`category`) — `test_bayrak_kaydi` **anında** yakaladı.

### FAZ 1 · adım 9 — `1.4` **süreç-arası derleme kilidi** *(2026-08-04)*

Kilit **süreç-içiydi** (`threading.Lock`). Artık **iki kademeli**: `threading` (ucuz,
süreç-içi) **+** `fcntl.flock` (süreç-arası), zaman aşımı **60 sn**, aşımda
**`RuntimeError`**. Kapı: **10 test**, hızlı sinyal **303**.

> 🔴 **GEREKÇESİ BU TURDA CANLIDA GÖZLENDİ — ve bir KAPIYI KIRDI.** Demet 9 kapısında
> `gitas` korpustan **tamamen düştü**; dosya sonradan **yerindeydi**, yani okuyucu
> compose'un **ortasına** denk gelmişti. `1.4`'ün gerekçesi 2026-08-02'de bir kez
> üretilmişti; bu **ikinci ve kendiliğinden** gelen gözlem.

> 🔴 **KİLİT DOSYASI DİZİNİN İÇİNDE DEĞİL, KARDEŞİ — ölçülmüş bir tuzak.** `compose()`
> çıktı dizinindeki `target` **dışındaki her çocuğu siler**. İçeriye konan bir kilit
> dosyası **tutulurken unlink edilirdi**: kilidi tutan süreç silinmiş inode üzerinde
> bekler, ikinci süreç **YENİ bir inode** açıp `flock`'u **anında** alır — kilit
> **sessizce çalışmaz** hâle gelirdi. ⚠ Yol haritası içeriyi (`<slug>/.compose.lock`)
> söylüyordu; sapma **ölçüye dayanıyor**. *Dosyayı koruma listesine eklemek kilidi bir
> listenin bakımına bağlardı; kardeş konum **yapısal olarak** bağışıktır.*

> ⚠ **Zaman aşımında süreç-içi kilit de bırakılıyor** — yoksa ilk aşım o dizini bu süreçte
> **kalıcı olarak** kilitlerdi (deadlock). Ayrı testle kilitli.
> ⚠ **Sessiz geçiş YOK:** kilidi alamadan derlemeye girmek, kilidin olmamasıyla aynı
> şeydir — üstüne bir de *"korunuyoruz"* beyanı ekler.
> ⚠ **`fcntl` yoksa** süreç-arası kademe düşer ama **gürültülü**: uyarı loglanır. Sessizce
> düşürmek, kilidin var olmadığı bir ortamda *"korunuyoruz"* sanmak olurdu; süreci
> reddetmek ise orantısız (tek süreçli kurulumda iç kademe doğru ve yeterli).

> ✅ **gunicorn/çok-worker dağıtımının ön koşulu kapandı** (→ II-G.7).

### FAZ 1 · adım 8 — `1.2c` redactor TÜMLEYENİ *(2026-08-04)*

**Demet 9b kapısı: süit 2282 geçti, 2 kırmızı — ikisi de `0.21` modül büyüme kapısı.**
Kapı **tam da kurulduğu işi** yaptı: AJ0 düzeltmesi `ask()`'e **10 kod satırı** eklemişti.

> ✅ **KAPI DOĞRU MİMARİYİ ZORLADI.** Kendi talimatı (*"yeni davranışı **modüle çıkar**,
> tavanı yükseltme"*) uygulandı: mantık `app/typo_onerisi.py`'ye taşındı, `ask()` **tek
> satırlık** bir çağrıya indi. Sonuç: `ask()` **1147/1147** · `ask.py` **2406/2406** —
> **boşluk 0**, yani fonksiyon **hiç büyümedi**. *Tavanı yükseltmek kapıyı kapının
> kendisiyle çürütürdü.*

`1.2c` · **redactor tümleyene çevrildi.** Ölçüldü: `apply_to_ask_response` yalnız **üç**
yeri maskeliyordu (`result.rows` · `facts[].text` · `summary`) — `AskResponse`'un **26**
alanı var.

> 🔴 **MASKELENMEYENLER:** `interpretation.narration` (LLM metni, **olgulardan** üretilir)
> · `contribution` (**cevabın gövdesi**, `0.23`'ün ölçtüğü alan) · `next_steps` ·
> `suggestions` (chip **etiketleri**, boyut değeri taşır) · `prescription` ·
> `recommendations` · `kpi` · `note` · `calculation_explanation`.
> **Sayılan bir liste, yeni alanı sessizce dışarıda bırakır** — `KAT-5`: *SAYMA, KAPAT*.
> Artık varsayılan **maskelemek**; muaf tutmak **açık ve gerekçeli** bir karar
> (`MUAF_ALANLAR`, `ReportPanel`'in `SAF_NOT_ALANLARI` tümleyeniyle aynı desen).

> 🔴 **YOL HARİTASININ VARSAYIMI ÖLÇÜLDÜ VE DOĞRU ÇIKTI** — ama kilitlenmemişti.
> *"Grafik etiketleri maskelenmezse §D.2/2 doğru değil"* deniyordu. Ölçüm: grafik
> `option`'ı `buildOption(effResult, …)` ile **maskeli sonuçtan** türüyor; CSV
> `exportTableCsv(result, …)` **aynı** satırlardan; PNG/SVG **aynı option**'dan; `VizSpec`
> yalnız **kolon adları** taşıyor. → **Dışa aktarım zinciri zaten maskeliydi**; asıl boşluk
> **yanıt gövdesindeydi**. Zincir yine de kapıya çevrildi: *bir doğru varsayım,
> kilitlenmemişse bir sonraki turda yanlış olabilir.*

> ⚠ **Pydantic modelleri de geziliyor:** `suggestions` bir `list[Suggestion]`'dır, sözlük
> değil. Yalnız `str`/`dict`/`list` gezen bir maskeleyici onu **sessizce** atlar ve chip
> etiketleri maskesiz kalırdı.

> ⚠ **Muafiyetler gerekçeli:** `cube_query` **yapısal bir kanıttır** (`POST /cube` onu
> birebir yeniden koşar) — maskelemek checkpoint'i (D4) kırardı: *bir kanıt,
> değiştirilirse kanıt değildir*. `sql`/`planned_sql` maskelenirse **çalıştırılamaz** olur.
> `question` kullanıcının **kendi** metnidir.

### FAZ 1 · adım 7 — `1.2b` LLM tek kapı · `AJ0/1` yazım önerisi *(2026-08-04)*

> 🔴 **DEMET 9'UN İLK KAPI KOŞUMU KIRMIZIYDI VE İKİ AYRI ŞEY ÇIKTI.**
> Korpus **%94,3** (taban %93,2) — yani doğruluk **ARTTI** — ama kapı **kırmızı**, çünkü
> `gitas` korpustan **tamamen düşmüştü**: `FileNotFoundError: demo/wren-project/cubes/
> enerji_makine/metadata.yml`. Dosya **şimdi var** ve dizin **gitignore'da** (derlenmiş
> çıktı) → bu bir **COMPOSE YARIŞI**. `1.4`'ün gerekçesi 2026-08-02'de bir kez
> üretilmişti; artık **bir kapıyı kırdığı** ikinci bir gözlem var.
> ⚠ **Payda 445 → 342 düştü ve yüzde YÜKSELDİ.** Bir metriğin iyileşmesi, ölçülemeyenlerin
> denklemden çıkmasıyla da olur — *"sayı arttı"* tek başına bir haber değildir.

`1.2b` · **LLM'e giden tek kapı.** *"Ham veri LLM'e gitmez"* kuralının **üç sahibi** vardı
(`sensitivity.prompt_safe_values` · `cube_router.build_catalog` · `ask.py`) ve üçü de
**girdi** tarafındaydı. `app/llm_guard.py::safe_call` **çıkış** tarafında durur: üç
gönderim noktası (`anthropic._ask` · `anthropic._arac_ile` · `openai-uyumlu._chat`)
artık ondan geçiyor. Kapı: **9 test** + mevcut 11.

> ⚠ **Girdi süzgeçleri KALIYOR.** `safe_call` onların **yerine** değil **arkalarına**
> durur. Ateşlerse bu bir **BULGUDUR**: üç süzgecin kapsamadığı bir yol açılmış demektir.
> ⚠ Tespit `pii.py`'den — **dördüncü bir desen sözlüğü yazılmadı**. Ve ihlalde **değerin
> kendisi loglanmaz**: bir sızıntıyı raporlarken sızdırmak, kapıyı sızıntı yüzeyi yapardı.

`AJ0/1` · **yazım önerisi cevaplı yolu kesemez.** Arka plan ölçüm turunun bıraktığı
düzeltme incelendi ve **tutuldu**: öneri artık `route()` ile doğrulanıyor (sıfır-LLM).
Ölçüldü — düzeltmeden önce **doğru yazılmış** sorular kesiliyordu (`arttı`→`parti`),
korpusun **+1,1 puanı** buradan.

> 🔴 **AMA BİR İDDİA ÇÜRÜTÜLDÜ.** O tur *"gerçek hatalar 0,833–0,909, saçmalar 0,667;
> bantlar **AYRIK**"* demiş ve *"eşiği yükselt"* sonucunu çıkarmıştı. Bağımsız ölçüm
> (geniş örneklem): saçma **0,600–0,769**, gerçek **0,714–0,923** → **ÇAKIŞIYORLAR**.
> Eşiği yükseltmek `fıre→fire` (0,750) ve `musteri→müşteri` (0,714) gibi **gerçek**
> hataları kaybettirirdi. **Kanıtlanmamış bir düzeltme sevk edilmedi**; ölçüm
> `test_BANTLAR_AYRIK_DEGIL_olculdu` ile donduruldu — *çürütülmüş bir gerekçe, yazılı
> değilse tekrar edilir.*

> ⚠ **KUSUR KAPANMADI, GÖRÜNÜR BIRAKILDI.** Saçma düzeltme de route ediyor
> (`"…parti iplik"` katalog terimlerinden oluşuyor). Üç uçtan uca vaka
> **`xfail(strict=True)`** — düzeldiği gün test **kırılır** ve işareti kaldırmaya zorlar.
> Gerçek ayırıcı sinyal benzerlik oranı değil **Türkçe fiil çekimi** (saçmaların hepsi
> fiil→isim); o iş AJ0'ın morfoloji kalemine ait.

### FAZ 1 · adım 6 — `1.2a` **kolon düzeyi erişim denetimi** *(2026-08-04)*

`sensitivity` → CLAC **eşik** eşlemesi + `motor_cls=off|shadow|on` (varsayılan **`off`**).
Kapı: **16 test**, hızlı sinyal **850**.

| seviye | sonuç *(boyahane, 20 kolon)* |
|---|---|
| `session_gizlilik = 0` | 🔴 kolon **plandan tamamen DÜŞER** — `SELECT *` onu döndürmez |
| `session_gizlilik = 2` | gelir |
| property **yok** | **fail-closed** |

> 🔴 **VARSAYILAN `off` — ve `motor_rls`'ten farkı ölçüme dayanıyor.** CLS `pii.py`'den
> **kategorik olarak farklıdır**: maskeleme kolonu **gösterir** (`123****89`), CLS onu
> **yok eder** — ve yok etme **sessizdir**. *Sessizce eksik bir tablo, maskeli bir
> tablodan daha kötüdür, çünkü eksiklik fark edilmez.*

> 🔴 **`on` KADEMESİ BİR KAPIYLA KİLİTLİ — bayrak kendi ön koşulunu biliyor.** CLS session
> property'yi **zorunlu** kılar; bugün **36** `query`/`dry_plan` çağrı sitesi kimlik
> geçmiyor ve `on` açılırsa her biri **fail-closed patlar**. Kapı bayrağı ancak tesisat
> tamamlandığında açılabilir kılıyor ve kalanı **sayıyla** raporluyor.

> ⚠ **`1.1`'de ERTELENEN session tesisatı GELDİ** — çünkü artık **gerçek tüketicisi var**.
> `1.1`'de yazsaydım `K3` (ters yetim) ihlali olurdu; sırayı doğru tutmanın karşılığı bu.

> ⚠ **Seviyeler UYDURULMADI:** `authorize.py` zaten `"pii:view": 2` diyor,
> `gizlilik_seviyesi()` o kararı **okuyor**. Hassasiyet sınıfı da tek sahipten
> (`sensitivity.classify`) — `pii.py` ile CLS ayrı sözlük okusaydı aynı kolon bir katmanda
> maskeli, ötekinde **görünür** olurdu.

> 🔴 **KENDİ BELGELEDİĞİM TUZAĞA YANLIŞ KATMANDA DÜŞTÜM.**
> `wren_core.SessionContext(properties=…)` **`frozenset`** ister;
> `wren.engine.WrenEngine.dry_plan/query(properties=…)` **`dict`** ister ve dönüşümü
> **kendi** yapar. Probe `SessionContext`'i doğrudan kullandığı için `frozenset` gördüm ve
> onu **bir katman yukarı** taşıdım → `'frozenset' object has no attribute 'items'`, **üç
> PII testi kırmızı**. *Belgelenmiş bir tuzak, yanlış katmanda uygulanınca yine tuzaktır.*
> Süit yakaladı; ayrım artık `test_HANGI_KATMAN_HANGI_BICIM`'de kilitli.

> ⟳ **`§3.4-session` TUZAĞI ATEŞLEDİ** (bu operasyonda **dördüncü** kez) ve satır
> **kuyruğa** nişanlandı: `§3.4-kuyruk` → *"SessionProperty **TÜM** çağrı sitelerinde"*.
> 36 sıfıra indiği gün yine kırılacak ve `motor_cls=on` açılabilir hâle gelecek. Sayaç
> `test_motor_cls.py`'nin sahibinde; tuzak onu **çağırıyor**, ikinci bir sayaç yazmadı.

### FAZ 1 · adım 5 — `1.1b` **arka plan işi kimliksiz koşmaz** *(2026-08-04)*

**Demet 8 kapısı: 4/4 YEŞİL** — süit **2243 geçti** · eval ±%0 · korpus **%93,2** (taban
%93,2) · senaryo dokuz sınıf tabanda.

`1.1` yalnız **istek yolunu** kapatmıştı. Zamanlayıcı döngüsü `run_schedule`'ı **kimliksiz**
çağırıyordu → `authorize()` **hiç çalışmıyordu**. Kapı: **11 test**, hızlı sinyal **325**.

> 🔴 **ZAMANLANMIŞ RAPOR, YETKİ İPTALİNİ ATLATAN KALICI BİR KANALDI.** Kullanıcı `viewer`'a
> düşürülse, hatta **silinse** bile raporu koşmaya devam ediyordu. Üç fail-closed kapısı
> kuruldu, üçü de ayrı gerekçeli: **sahip yok** · **sahip çözülemiyor** (silinmiş/pasif) ·
> **sahip artık yetkili değil**. Sonuncusunun kuralı: *yetki, verildiği an değil
> **KULLANILDIĞI AN** geçerli olmalıdır.*

> 🔴 **FAIL-CLOSED KESİNTİ ÜRETMEDEN — çünkü cevap zaten kayıttaydı.** Yol haritası
> *"`principal=None` reddedilir"* diyor; harfi harfine uygulanırsa **her zamanlanmış rapor
> durur**. Ölçüldü: kayıt **`created_by`'ı zaten taşıyor** — yani *"bu iş kimin adına
> koşuyor"* sorusunun cevabı **duruyordu, hiç sorulmuyordu**. `run_as_user_id` → yoksa
> `created_by`; ikisi de yoksa **red**. Bu bir gevşetme değil, **geriye doldurma**.

> ⚠ **Kimlik SAKLANMIYOR, her koşumda KAYNAKTAN kuruluyor** (`app_user` + `membership` +
> `role`). Token saklamak bir **sır** saklamaktır ve süresi dolar; saklanmış bir yetki,
> **iptal edilemeyen** bir yetkidir. Böylece rol değişikliği **bir sonraki koşumda** etkili.

> ⚠ **Sahipsiz kayıt bir «eski veri» DEĞİL, bir BULGUDUR.** Genel `except`e düşürmek onu
> *"tek zamanlama hatası"* diye meşrulaştırır ve delik **sessizce** açık kalırdı — özel
> yakalayıcı genel olandan **önce** duruyor ve zamanlamanın **adıyla** logluyor
> (kapı sıranın doğruluğunu da ölçüyor: sonra gelseydi hiç ateşlenmezdi).

> ✅ **ÜÇ PARÇA DA İNDİ (K1/K2):** backend *(kimlik kapısı)* · sözleşme *(`GET /schedules`
> → `run_as`)* · **frontend** *(`SchedulesPanel`: *"… adına"* / **"⚠ sahipsiz — koşmuyor"**)*.
> Sahipsiz kayıt artık **koşmuyor**; bunu göstermemek kullanıcıyı **sessizce durmuş** bir
> raporu beklemeye bırakırdı. **Görülemeyen bir yetki devri, devredilmemiş sayılır.**

### FAZ 1 · adım 4 — `1.3b` **Katman B artık var** *(2026-08-04)*

`enforce_query` bir **stub**'dı (gövde tek satır `return`, üstünde `# TODO(faz-2)`) —
ve **çağıranı da yoktu**. Yani ADR-0014 Karar 5'in beyan ettiği katman ne iş yapıyordu
ne de bağlıydı. Kapı: **12 test**. Hızlı sinyal: **407 geçti**.

> 🔴 **BEYAN VAR, KATMAN YOK — üstelik İKİ KATLI.** Bir stub'ı doldurmak yetmez; katman
> ancak **çağrıldığı yerde** vardır. `grep enforce_query app/` → **0 isabet**. Bu,
> `0.5`'in *"19 altın vakalı ölü modül"* bulgusunun **güvenlik katmanındaki** hâli.

> 🔴 **«Boş allowlist geçer» düzeltmesi göründüğü kadar basit DEĞİL.** Yol haritası
> *"fail-open → fail-closed"* diyor ve **yön doğru**; ama `ModelPermission` **her
> tenant'ta boş** — harfi harfine uygulanırsa **her sorgu reddedilir**, yani bir güvenlik
> katmanı adına **tam kesinti**. Ayrım kurtarıyor:
> **«yapılandırılmamış» ile «boş allowlist» AYNI ŞEY DEĞİL.**
>
> | tenant'ın satırı | anlamı | karar |
> |---|---|---|
> | **hiç yok** | Katman B kurulmamış | Katman A yönetir |
> | **var, model listede yok** | allowlist **aktif** | 🔴 **RED** (fail-closed) |
>
> Böylece şart **anlamlı hâliyle** sağlanır: bir kez yapılandırıldığında eksik allowlist
> **artık geçmez** — ve bugün **hiçbir davranış değişmez**, yani madde `bayraksız`
> kalabiliyor (yol haritasının sınıflandırması korunuyor).

> ⚠ **Rol köprüsü:** `Principal` rol **ANAHTARI** taşır (`["owner"]`), `ModelPermission`
> rol **KİMLİĞİ** (UUID FK). Köprü `Role` tablosundan kuruluyor. Çevirmeden tenant
> genelinde birleştirmek, allowlist'i **rol ayrımı olmadan** uygulamak olurdu — istenenden
> **geniş** bir izin, sessizce. Rol çözülemezse `None` döner: **kısmen anlaşılmış** bir
> yetki kuralını uygulamak, yanlış yönde hata yapma riskini ikiye katlar.

> ⚠ **DB ulaşılamazsa tam kesinti YOK:** ulaşılamayan bir **yetki deposunu** boş allowlist
> saymak, bir altyapı arızasını tam kesintiye çevirirdi.

> ⚠ **Model çözümü motorun KENDİ fonksiyonuyla** (`wren.policy.resolve_model_name`).
> Yetkilendirdiğimiz küme, motorun **gerçekten planladığı** küme olmalı; ikisi ayrışırsa
> *"izin verdik"* ile *"dokunuldu"* farklı şeyler olur — bir güvenlik katmanının **en
> sessiz** kırılma biçimi.

> ⚠ **İKİNCİ ÇAĞRI YOLUNUN SIRASI YAZILI:** `/ask`'in Discovery dalı ayrı turda bağlanır
> çünkü `routers/ask.py` **risk sınırındadır** (demete girmez, kendi kapısını koşar).
> Sessizce atlanmadı; kapı bunu **test ediyor** ki bir sonraki tur *"zaten bağlı"* sanmasın.

> 🔴 **METİN ÖLÇME KUSURUNA BU OTURUMDA ÜÇÜNCÜ KEZ DÜŞTÜM** (`⟳` sayacı · `0.21` tavan
> operatörü · burada `TODO(faz-2)`): kapı, fonksiyonun **kendi tarihçe yorumunu** yakalayıp
> doğru yazılmış kodu kırmızı ilan etti. Üçü de **AST**'e çevrildi. Doğru soru *"şu dizi
> geçiyor mu"* değil, **"gövde ne yapıyor"**.

### FAZ 1 · adım 3 — `1.1` **MOTOR RLS İNDİ** *(2026-08-04)*

`always_filter` → `rowLevelAccessControls` çevirisi. Bayrak **`motor_rls=off|shadow|on`**,
varsayılan **`shadow`**. Kapı: **15 test** (`test_motor_rls.py`) + **7** ön koşul.
Hızlı sinyal: **803 geçti**.

| kademe | manifest | servis edilen cevap |
|---|---|---|
| `off` | dokunulmaz | bugünkü |
| **`shadow`** *(varsayılan)* | **dokunulmaz** | **bugünkü** — gölge yalnız **ÖLÇER** |
| `on` | RLAC yazılır | motor filtreliyor; `_inject_always_filter` o cube'da **elini çeker** |

> 🔴 **KENDİ TASARIMIMDA TUTARSIZLIK BULDUM VE DÜZELTTİM.** İlk sürüm `shadow`'da da
> manifeste RLAC yazıyordu — o hâlde motor filtreyi **uygular** ve **ham-SQL yolundaki
> cevap DEĞİŞİRDİ**. Yani *"gölge"* adı altında **canlı bir davranış değişikliği** sevk
> edilecekti. Doğru desen **komşuda zaten yazılıydı**: `_sql_policy`'nin gölgesi motoru
> gevşek kurar, katı politikayı **AYRI bir motorla PARALEL** dener.
> ⚠ **803 yeşil test bunu YAKALAMADI** ve nedeni kayda değer: `alwaysFilter` yalnız
> **gulteks**'te var (3 cube, logo-3 tenant'ı) ve süit o tenant'ın **ham SQL** yolunu
> ölçmüyor. **Yeşil bir süit, ölçmediği bir davranış hakkında hiçbir şey söylemez.**

> 🔴 **`SessionProperty` BİLİNÇLE GELMEDİ.** `always_filter` **sabit** yüklemdir
> (`CANCELLED = 0`) ve ölçüldü ki motor sabit koşullu kuralı `requiredProperties`
> **olmadan** da uyguluyor. Session tesisatını şimdi yazmak **çağıranı olmayan bir
> yetenek** üretirdi — `K3` (ters yetim) kapısının avladığı sınıf. İlk session'a bağlı
> kural doğduğunda (`1.2`) `sql_literal()` ile birlikte gelecek; gerekçe `rls.py`'nin
> başında yazılı ki *"unutuldu"* sanılmasın.

> 🔴 **ÖLÇÜLMÜŞ BİR FAIL-OPEN YASAKLANDI:** `required=False` + `defaultExpr` verilirse
> property **hiç gönderilmese bile** sorgu **varsayılanla** koşar (`WHERE tenant =
> 'HERKES'`). Kimlik enjeksiyonunu unuttuğumuz gün sistem **hata vermez**, başka bir
> filtreyle cevap verir — filtresiz cevaptan **daha sinsi**, çünkü sonuç makul görünür.

> ⚠ **Gecikme bütçesi (0.17) gölgeye uygulandı:** gölge denetimi HER sorguda koşar ve
> `json.loads` 117 KB'lık manifesti her turda ayrıştırırdı. **Beş tenant'ın dördünde**
> hiç `alwaysFilter` yok → ucuz bayt taraması onları ayrıştırmadan eliyor.

> ⚠ **JSONL'dan sapma bilinçli:** yol haritası `logs/rls_shadow.jsonl` diyordu; gölge
> bulgularının bu depoda **zaten bir sahibi var** (`_shadow_policy_check` →
> `_log.warning`). İkinci bir kayıt mekanizması *"aynı kuralın iki sahibi"* olurdu; 7
> günlük ölçüt aynı greple ölçülür (`RLS (gölge)`).

> ⟳ **`§3.4-RLS` TUZAĞI ATEŞLEDİ ve TERS ÇEVRİLDİ** (bu operasyonda **üçüncü** kez).
> §0 satırı **daraltıldı** (geriye `SessionProperty` · FAZ 1.2 kaldı), ⟳ sayısı **13**.
> 🔴 **Yeni belirteç iki kez yanlış yazıldı ve ikisi de kayıtlı sınıf:** (1) alt-dize
> taraması `rls.py`'nin **YORUMUNU** yakaladı — `§3.4-osi`'nin iki kez düştüğü yer;
> (2) `_app_kaynagi(x)` bir dosyayı **DIŞLAR**, seçmez — imzayı ters kullandım. Şimdi
> **tanımın kendisi** aranıyor (`^def oturum_ozellikleri`).

### FAZ 1 · adım 2 — `1.1` **ÖN KOŞUL ÖLÇÜMÜ** *(2026-08-04)*

Bir katmanı **kanıtlanmamış** bir yeteneğin üstüne kurmak `KAT-3` ihlalidir. `1.1` motorun
`rowLevelAccessControls` + `SessionProperty` yeteneğine dayanacak — o yüzden yetenek
**önce ölçüldü**, sonra `tests/test_motor_rls_onkosul.py` ile **donduruldu** (7 test).

| # | Soru | Ölçüm |
|---|---|---|
| **1** | Koşul SQL'e enjekte oluyor mu? | ✅ modelin alt sorgusuna `WHERE … = 'değer'` |
| **2** | **JOIN** ile baypas edilebiliyor mu? | ✅ **HAYIR** — filtre join'in **iki tarafına da** iniyor |
| **3** | Property verilmezse? | ✅ **fail-closed** (planlama hatası, filtresiz sorgu DEĞİL) |
| **4** | Kötücül/kaçışsız değer? | ✅ reddediliyor — *"allow only literal value"* |
| **5** | Manifest daraltmasında RLAC düşüyor mu? | ✅ **hayır**, round-trip'te korunuyor |
| **6** | `dry_plan`/`query`/`dry_run` üçü de `properties` alıyor mu? | ✅ **üçü de** |

> 🔴 **(2) MADDENİN VARLIK SEBEBİ.** `always_filter` bir **uygulama katmanı** yamasıdır ve
> `compose.py:434` (**G10**) onun **join altında baypas edildiğini** zaten ölçmüştü: filtre
> yalnız o cube'un kendi SQL'ine ekleniyor, join `__source` seviyesinde gerçekleşiyor.
> Motor RLS'i o deliği **yapısal olarak** kapatıyor — ve bu artık bir umut değil, bir ölçüm.

> 🔴 **MOTOR HAZIR, TESİSAT YOK.** `wren_core` `RowLevelAccessControl` · `SessionProperty` ·
> `validate_rlac_rule` **taşıyor** ve `wren.engine`'in üç yolu da `properties` parametresi
> **kabul ediyor**. Ama `grep -c rowLevelAccessControl backend/app/` → **0** ve
> `WrenService.dry_plan(self, sql)` `properties`'i **hiç geçmiyor**. Yani eksik olan
> **yetenek değil, onu çağıran satırlar**.

> ⚠ **(4) BİR GÜVENLİK YÜZEYİNİ KONUMLANDIRIYOR:** session property değerleri **SQL
> literali** olarak veriliyor → tırnaklama/kaçış **bizim tarafımızda**. Motor tek literal
> dışındaki her şeyi reddederek **ikinci** savunmayı koyuyor; `1.1`'in
> `oturum_ozellikleri()`'si **birinci** savunma olacak.

> ⚠ **Ölçüm sırasında bir tuzağa düşüldü ve kilitlendi:** `properties` düz `dict` kabul
> etmiyor, `frozenset(dict.items())` istiyor (`wren.engine._plan` onu böyle kuruyor).
> Düz sözlük `TypeError` verir — ve bu hata **çalışma anında, kimlik yolunda** patlardı.

### FAZ 1 · adım 1 — `1.3c` sahte güvenlik sınırı · `1.3` yetki granülerliği *(2026-08-04)*

**FAZ 0 kapanış kapısı: 4/4 YEŞİL.** süit **2199 geçti** (2 atlandı · 1 xfail) · eval
precision/coverage **±%0** · korpus **%93,2** (taban %93,2) · senaryo dokuz sınıf tabanda.

> 🔴 **`1.3c` — MIMARI İKİ YERDE OLMAYAN BİR GARANTİ SATIYORDU.** `§3.4` tablosu ve `§5`
> *"yapılmayacaklar"* satırı ikisi de *"45 veri-okuyucu TVF'yi **her AST konumunda**
> bloklar"* diyordu. Motorun **kendi kaynağı** (`wren/policy.py`) tam tersini söylüyor ve
> alıntı birebir MIMARI'ye geçti: *"for non-source positions this named list **is** the
> security boundary: a reader that is **not enumerated** here **will pass** in a
> projection / subquery / nested-arg position. The list must therefore be **MAINTAINED
> PER-CONNECTOR**."* Kaynak konumu (`FROM`/`JOIN`) **gerçekten** fail-closed; kaynak-dışı
> konumlar **blocklist**. İkisi aynı cümle değil ve fark **güvenlik kararı** doğuruyor.

> 🔴 **VE «KONNEKTÖR BAŞINA BAKIM» ANA KONNEKTÖRÜMÜZDE HİÇ YAPILMAMIŞ.** Ölçüldü: 45 adın
> **0'ı** SQL Server okuyucusu — ve `wren_service.py:143`'ün kendi notu *"üretimdeki
> tenant'larımız (gitas, atiksan) tam olarak **mssql**"* diyor.
> ⚠ **Bu bir «sömürülebiliriz» iddiası DEĞİL ve öyle yazılmadı:** mssql'in tehlikeli
> okuyucuları ya **kaynak konumundadır** (`OPENROWSET`/`OPENQUERY` → `FROM` → zaten
> fail-closed) ya da `SELECT` bile değildir (`xp_cmdshell` → `EXEC` → `guard_sql` zaten
> reddeder). Ölçülen şey bir **kapsama boşluğudur**, bir açık değil. Boşluğu *"açık"*
> yazmak da *"yok"* yazmak kadar yanlış olurdu. Kapı: `tests/test_blocklist_tazeligi.py`
> — muafiyet **gerekçesiz olamaz** ve **bitiş koşulu** taşımak zorunda.

> ✅ **`1.3` — 15/15 `query:run` → BEŞ AKSİYON.** `query:run` 7 · `drill:run` 2 ·
> `contribution:run` 2 · **`contribution:scan` 1** · `llm:invoke` 3.
> **Tek davranış değişikliği** ve o da yol haritasının KAPI'sının adıyla istediği:
> *"viewer rolü `contribution.report` (maliyet **`pahali`**, 6 boyut tarama) çağıramıyor."*
> Diğer dördü bilinçle **rütbe 0** → birebir aynı davranış (KURAL B).
> ⚠ **`llm:invoke` = 0 bir KARARDIR:** LLM araçlarını analyst+ yapmak **güvenlik** değil
> **ÜRÜN** kararıdır (viewer'ın cevabı küple sınırlanır) ve bu madde onu vermek için
> kurulmadı. ⚠ **`metric:certify` bilinçle EKLENMEDİ** — sertifikasyon FAZ 1.5'in işi ve
> henüz yok; karşılığı olmayan bir aksiyon, kapanın kendi içinde *"beyan var, kod tanımıyor"*
> üretirdi.
> ⚠ **Erişilebilirlik dürüstçe:** üründe bugün yalnız `owner` var → **bugünkü kullanıcıya
> etkisi sıfır**. Kapatılan şey bir açık değil, bir **değişmezin uygulanabilirliği**.

> ⟳ **`§11-yetki` TUZAĞI ATEŞLEDİ ve TERS ÇEVRİLDİ** (ikinci kez bu operasyonda). §0'ın
> `§11` satırı **daraltıldı** (geriye FAZ 6.1 · onaylı yazma kaldı), belirteç
> `_yazan_arac_sayisi() > 0`'a nişanlandı, ⟳ sayısı **13'te** kaldı. Yeni kapı yalnız
> *"birden çok izin var"* demiyor — biri `contribution.report`'u `query:run`'a geri
> çekerse sayı **yeşil** kalır, kusur **geri döner**; kapı granülerliğin **işe yaradığı**
> noktayı tutuyor.

> 🔴 **FAZ 1'DE BİR SIRA İHLALİ BULDUM (`KAT-3`, FAZ 0'da dört kez çıkan sınıf):**
> `1.5` metrik sertifikasyonu alanları arasında **`lineage_set_hash`** var ve KAPI'sı
> *"**üst-akış kolon kümesi** değişince sertifika düşer"* diyor — ama o kümeyi **`1.6`
> column-level lineage** üretiyor. Bugünkü sırayla `1.5` inerse `lineage_set_hash` ya
> **uydurulur** ya **hep `None`** olur; ikisi de *"beyan var, karşılığı yok"*.
> → **`1.6` ÖNCE, `1.5` SONRA.** *(Madde numaraları D5 gereği DEĞİŞMEZ, yalnız sıra yazılır.)*

### FAZ 0 · adım 14 — `0.21` modül büyüme kapısı **(FAZ 0'IN SON MADDESİ)** *(2026-08-04)*

| Ölçüt | FAZ 0 ÖNCESİ (`c3fcfe7`) | Muafiyet | Tavan | Bugün | Boşluk |
|---|---|---|---|---|---|
| `ask()` kod satırı | 1135 | `9a138a9` **+11** *(0.5)* · `98a5071` **+1** *(0.12/0.13/0.6)* | **1147** | 1147 | **0** |
| `ask()` iç fonksiyon | 19 | **yok** | **19** | 19 | **0** |
| `ask.py` toplam kod | 2394 | *(taşınabilir pay)* | **2406** | 2406 | **0** |
| `cube_router.py` kod | 1723 | `9164806` **+13** *(0.18)* | **1736** | 1736 | **0** |

> 🔴 **BİRİMİ ÖLÇÜM SEÇTİ, TERCİH DEĞİL.** İlk niyet *"ham satır"*dı. Ölçüldü: FAZ 0
> `ask.py`'ye **+44 ham** satır kattı ama yalnız **+12 kod** — **%73'ü belgeleme**. Ham
> satır sayan bir kapı, bu deponun **ölçülmüş kusurları kaydettiği mekanizmayı**
> vergilendirir ve geliştiriciyi *"yorumu silersem yeşile döner"* diye **ödüllendirirdi**.
> Kapı, korumaya çalıştığı bilgiyi yok ederdi. *(`cube_router.py` **%52 belge**.)*

> 🔴 **`ask()` FONKSİYONU, `ask.py` DOSYASI DEĞİL.** Zarar dosyada değil gövdede: 19 iç
> fonksiyon **aynı kapsamı paylaşıyor**. Kodu `ask()`'ten çıkarıp aynı dosyada modül
> düzeyine almak **istenen** yöndür — dosya kapısı onu **cezalandırırdı**. Yine de dosya
> bütünü ayrıca sınırlı, yoksa `ask()` küçülürken gerisi sessizce şişerdi.

> ⚠ **`0619bfd` (0.22) muafiyet listesinde YOK ve bu bir karar:** ham satırda **+8**,
> kod satırında **0** — bildirim `if` bloğundan gövde başına **taşındı**. Bir taşıma borç
> değildir. *Neden listede olmadığı* kapının içinde yazılı, yoksa bir sonraki okuyucu
> eksiklik sanır.

> 🔴 **KAPI KENDİ KIRMIZISINI KANITLIYOR.** Bu operasyonda bir kapı **üç kez** yanlış
> yazıldı ve *"yeşil"* kaldığı için kusuru **taşıyarak** geçti. `test_KAPI_SAHTE_DEGIL_*`
> gerçek kaynağa **bellekte** tek bir kod satırı enjekte edip tavanın aşıldığını
> gösteriyor — ve aynı satır **yorum** olsaydı kapının **sessiz** kaldığını da. Birim
> kararının davranıştaki karşılığı budur, bir niyet beyanı değil.

> ⚠ **İki kendi kusurum daha, ikisi de metin ölçmekten:** (1) *"tavan `==` ile kilitlenmiş
> mi"* testi **kendi assert satırını** yakaladı → AST'e çevrildi (⟳ sayacının 14↔13
> kusuruyla aynı sınıf). (2) MIMARI'ye *"14 test"* yazdım, dosyada **9** vardı — 14 iki
> dosyanın toplamıydı; `test_MIMARI_TEST_SAYILARI` onu **anında** yakaladı.

### FAZ 0 · adım 13 — `§7-CI` yaşam döngüsü · `0.4` netleştirme önceliği *(2026-08-04)*

**Demet 6 kapandı.** Kapı: **3/4 yeşil**, tek kırmızı **kasten kurulmuş bir tuzağın
ateşlemesi** (`test_YURURLUKTE_satiri_HALA_dogru[§7-CI]` — FAZ 0.15 indi). Korpus
**%93,2** (taban %93,2) · semantik vaka **%92,1** · eval precision/coverage **%100** ·
senaryo dokuz sınıf tabanda · süit **2167 geçti**.

| İş | Ne indi |
|---|---|
| **`§7-CI`** | Tuzağın üç adımı: §0 satırı **daraltıldı** · MIMARI §7'ye **ölçümlü ✅** · tuzak **ters çevrildi** |
| **`0.4`** | Karar **`off` KALIYOR** — gerekçesi MIMARI'ye yazıldı · ölçüm aleti + 23 test |

> ⚠ **`§7-CI` talimatı harfi harfine uygulanmadı — ve nedeni ölçüldü.** Tuzak *"§0 satırını
> **SİL**"* diyor; ama o satır **üç şey birden** işaret ediyordu (*çerçeve · CI kapıları ·
> risk-kapsam*) ve **yalnız CI kapıları** indi. Bütünüyle silmek, **inmemiş** bir maddenin
> işaretçisini de silerdi — yani tuzağın engellemek için var olduğu şeyi, **tuzağa uyarak**
> yapardım. Satır daraltıldı, tuzak daralan iddiaya (**FAZ 4.2 · risk-kapsam**) yeniden
> nişanlandı; ⟳ sayısı **13'te** kaldı. Yol haritasının kendi §0 tablosu zaten bu satırı
> yalnız `FAZ 4` ile eşliyordu — daraltma MIMARI'yi yol haritasıyla **hizaladı**.

> 🔴 **`0.4`: İŞ ZATEN ÖLÇÜLMÜŞTÜ, ama KARARIN EVİ YOKTU.** Canlı ölçüm 2026-08-03'te
> yapılmış ve sonucu `features.yml`'nin **YORUMUNDA** duruyordu. Yol haritasının KAPI'sı
> birebir *"nedeni **`MIMARI.md`'ye yazılır**"* diyor — ve MIMARI'de bu maddeden **hiç söz
> edilmiyordu**. Bir YAML yorumu mimari otorite değildir; çelişkide MIMARI kazanır.
> Bir sonraki tur *"ölçülmemiş"* sanıp **kotayı yeniden yakardı**.

> 🔴 **AD ÇAKIŞMASI — MIMARI'de İKİ AYRI «Faz 0.4» varmış.** Eski olan 2026-08-02'nin
> **kapsam kapısı** fazı (`475e691`) ve *"OK **+6** · CUBE-SAPMA **−25**"* taşıyor — yani
> **sıkılaştırma lehine** sayılar. Yeni 0.4'ün kararı **tam tersi**. Ayrıştırılmasaydı
> okuyucu yanlış sayıya bakıp **bayrağı açardı**. Kimlik asimetrisi bu kez **ad düzeyinde**.

> 🔴 **İLAN EDİLEN KAPI BOŞ ÇIKTI — ölçüldü, tahmin edilmedi.** Yol haritası 0.4'ün
> kapısını `lab/nl_corpus.py --kapi` öncesi/sonrası diye yazmıştı. **LLM'siz A/B farkı:
> `0`/41.** Sebep yapısal: `ask.py:2601` ile `:2757` **aynı** netleştiriciyi çağırır,
> ikincisi Intent'ten sonradır ve LLM yoksa Intent dalı hiç koşmaz. Üstelik korpus bu
> nüfusa **hakemlik edemez**: beklenen cube'u soruyu üreten cube'dur, oysa nüfus tam
> olarak *"aynı terimi ≥2 cube sahiplenmiş"* kümesidir — yer gerçeğinin **kendisi
> yazı-turadır**. → Ölçüt **doğruluk değil KARARLILIK**.

> 🔴🔴 **ALETİM YANLIŞ-YEŞİL BASTI — ve kök neden ön uçuşun kendisiydi.** Canlı doğrulamada
> sağlayıcıların **hepsi** `429`/`503` verdi, ama alet **«B · bağlamdan çözüyor»** kararı
> bastı: her tur aynı deterministik düşüşe uğradığı için sonuç *"kararlı"* göründü.
> Ölçülen kararlılık, LLM'in değil **BAŞARISIZLIĞIN** kararlılığıydı.
> **Kök neden:** `_kota_on_ucusu` `generate_sql` ile ön uçuş yapıyor, koşum ise
> **`select_cube`** çağırıyor — **ayrı model, ayrı kota**. Ön uçuş, koşumun kullanmadığı
> yolu sertifikalıyordu. İki düzeltme, ikisi de tek sahipte: (a) ön uçuş artık
> `select_cube`'u **da** deniyor · (b) `karar_ver` LLM katılımını **son koşul** olarak
> arıyor (`self-consistency` izi yoksa `⊘`) — çünkü kota koşumun **ortasında** da tükenir.

> ⚠ **41 ≠ `ask.py`'nin 53'ü — ve ikisi de doğru.** `ask.py` *"≥2 sahip + route çözemiyor"*
> sayıyor; **41** ise chip'in **gerçekten kurulabildiği** küme. *"Belirsiz"* ile
> *"belirsizliği SORULABİLİR"* aynı sayı değil.

### FAZ 0 · adım 12 — `0.17` gecikme bütçesi · `0.20` bayrak profilleri *(2026-08-04)*

| Madde | Ne indi | Ölçüm |
|---|---|---|
| **0.17** | Yol başına **p50/p95** + ilan edilen bütçe (`GET /stats/gecikme`) — **yeni enstrümantasyon YOK**, `duration_ms` zaten `interaction_log`'da | EK D'de 60+ eşik vardı, **tek gecikme eşiği yoktu** |
| **0.20** | Üç profil: **`taban`** (hepsi off) · **`v1-varsayilan`** · **`v1-tam`** + **yaşam döngüsü** borç ölçümü | `taban` 0 açık · `v1-varsayilan` **11/17** · `v1-tam` **19/19** · **ölü bayrak 2** |

> 🔴 **`0.17`'nin çerçevesi DIŞ KANITLA tersine çevrildi.** 240 katılımcılı bir çalışma
> (TTFT 2s/9s/20s): **2 saniyede gelen cevap, 9 saniyede gelenden DAHA AZ** faydalı
> bulundu; **9s en faydalı** koşuldu. *"Streaming algılanan kaliteyi artırır"* iddiasının
> **hakemli çalışması yok**. → Bütçe bir **hız yarışı değil, bir SÜRPRİZ KAPANI**:
> `t2_anlatici`'yi kapalı tutan asıl soru gecikme değil **KAZANÇ** olmalı. Bütçe yalnız
> *"30-85× fark, fark edilmeden büyümesin"* diye var.

> 🔴 **`0.20`'nin asıl işi YAŞAM DÖNGÜSÜ.** `v1-varsayilan`'da **iki sürüm** açık kalan
> bayrak **silinir** (kod kalıcılaşır, bayrak gider) — yoksa §C/10'un *"ölü bayrak 0"*
> hedefi, sayı büyüdükçe **matematiksel olarak** tutturulamaz: her yeni özellik bir
> bayrak ekler, hiçbiri kaldırılmaz. **Bir bayrak bir KARAR ANIDIR, bir mülk değil.**
> ⚠ *"Sürüm"* bu depoda bir **karardır**, otomatik türetilebilir bir sayı değil —
> uydurmak, **ölçüm gibi görünen bir tahmin** üretirdi. Ölçülmemiş borç, borç değildir (`⊘`).

> 🔴 **K1 üçüncü kez yeni bir ucu kurulduğu ANDA yakaladı** (`/metrics` · `/stats/gecikme`).
> Her seferinde `api-only` beyanı **sahibiyle** yazıldı, sessizce değil.

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
| 17 | 🔴 **SESSİZ-YANLIŞ: *"değişim"* istendi, **TOPLAM** verildi.** Canlı tur t14: *"ocak ile haziran arasında makine bazında fire değişimi"* → `compare=None`, kıyas yok, ay yok, **uyarı da yok**; kendinden emin bir toplam tablosu. Kullanıcı: *"veri doğru, **cevap yanlış soruya**"*. Kök neden `cube_router.compare_mode` bu ifadeyi tanımıyor | **FAZ 0.5b / cube_router** *(kıyas ekseni)* |
| 18 | 🔴 **AJ0 canlıda DOĞRULANDI — çıkışsız yazım düzeltmesi.** t12/t13: *"…fire ne kadar arttı"* → *"«artti» yerine «parti» mi demek istedin?"*, **doğru yazınca da aynı**, ve sunulan tek şık gramersiz bir cümle (*"…fire ne kadar parti"*). Kullanıcı: *"Ben «artti» yazmadım ki… düzeltmenin yolu yok, çıkış kapısı kapalı."* VK ölçümü *"13 turun dördü buradan ölüyor"* demişti — **canlıda tekrar üretildi** | **§G/AJ0** *(operasyonun en yüksek kaldıraçlı maddesi)* |
| 19 | 🔴 **`bakiye` iki cube'ta, seçim SESSİZ — ve fark ₺11,86 MİLYON.** t11 `cari` → **₺11.859.052,65**; t15 `mizan` → **₺0**. Sistem birini kura ile seçti, sormadı, seçtiğini yazmadı; `next_steps`'in 6 şıkkının hiçbiri *"cari mi mizan mı?"* demiyor. ⚠ **SAHİP DEĞİŞTİ (2026-08-04):** `0.4` ölçüldü ve bayrak **`off` kaldı** — yani bu borcu `0.4` **KAPATMIYOR**. Ölçüm ayrıca gösterdi ki model *"bu yıl bakiye"*de **kararlı** biçimde `mizan`'ı seçiyor: bu bir motor kusuru değil **katalog kararıdır** (*bare `bakiye` hangi cube'un?*). Kapalı bir bayrağı borcun sahibi göstermek, borcu **görünmez** kılardı | **FAZ 3.1** *(sahiplik turu; `metrik_kaydi` çakışmayı görünür kılar, KARARI VERMEZ)* |
| 19b | 🔴 **AYRIŞTIRILDI (#19'dan):** mizan sorgusunda *"bu yıl"* filtresi **sessizce düştü**. Bu bir katalog kararı DEĞİL, bir **kusurdur** — ve #19 ile aynı satırda durduğu sürece sahibi `bakiye` tartışmasının altında kalıyordu. Dönem filtresinin bir cube'ta uygulanıp ötekinde düşmesi, `0.10`'un dönem ekseni işiyle aynı sınıf | **`cube_router` / dönem ekseni** *(sahip atanacak — FAZ 1 girişinde)* |
| 20 | **Üstünlük ifadesi cevaplanmıyor:** t06 *"hangi makinenin fire oranı en yüksek bu yıl"* → `source=catalog`, **satır yok**, ürün kataloğu dökümü. Ama t07 *"makine bazında fire oranı bu yıl"* → 11 satır, doğru cevap. Kullanıcı: *"Sistem kendi bildiği şeyi bana yasaklıyor… kendimi aptal hissettim"* | **cube_router** *(liste/üstünlük niyeti)* |
| 21 | **Onay kartına SÖZLE «evet» işlemiyor:** t08 kart *"…panona ekleyeyim mi?"* diye **cümleyle** soruyor; t09 *"evet ekle"* → *"geçerli bir alan veya değişiklik belirtmemektedir"*. Halka yalnız **fareyle** kapanıyor. *(Düğme yolu ✅ çalışıyor: t10 «Rapor panona eklendi».)* | **FAZ 6** *(eylem/onay akışı)* |
| 22 | **Ham kolon adı + saat damgası ekranda:** `tarih__year: 2026-01-01 00:00:00`. Kullanıcı: *"Ben yıl sordum, bana veritabanı sütun adı ve saat 00:00 gösteriliyor."* | **FAZ 0.10b** *(görünen adlar)* |
| 23 | **330 satır, sıfır içgörü:** t05'te kırılıma tıklamanın sebebi *"hangi makine kötü"* idi; dönen tek cümle sistemin **yapmadığı** işi anlatıyor. Kırılımlı oran görünümünde en azından **sıralama** verilebilmeli *(bugün toplanamadığı için susuyor — doğru ama yetersiz)* | **FAZ 5** *(anlatı) + 0.10b* |
| 24 | 🔴 **`pytest-xdist` ÖLÇÜLDÜ: 100 sn ↔ 510 sn — ama 360 hata.** Paralel koşum süiti **5 kat** hızlandırıyor, ancak `session` fixture'ları ve compose kilidi (`metadata.yml`) worker'lar arasında çakışıyor. **Bedava değil**; benimsenmeden önce izolasyon işi gerekir *(muhtemelen worker başına ayrı `DIMA_DATABASE_URL`/pack dizini)*. Kazanç büyük olduğu için borç olarak duruyor | **FAZ 0.15** *(CI kapıları — aynı izolasyon işi orada da lazım)* |

---

## ✅ DENETİM — **AJANLAR KULLANILIR** *(yanlış teşhis geri alındı, 2026-08-04)*

> 🔴 **DÜZELTİLMİŞ TEŞHİS.** Bir süre burada *"arka plan ajanları ana sohbeti sildi →
> alt-ajan KESİN YASAK, `OPERASYON-DENETIM.md` silindi"* yazıyordu. **O teşhis YANLIŞTI**
> ve dosya da **silinmemişti** (`git status`: ` M`, duruyor). Olayı inceleyen kişi ölçtü:
> sebep başarısız bir **daemon yükseltmesiydi**, arka plan işçilerini öksüz bıraktı.
> Kullanıcı: *"ben yanlış anlamışım, en güçlü yanımız olan ajanlarmış."*
>
> **Ders — teşhisin kendisi de kanıt ister.** Bir olayla **aynı anda** olmak, o olayın
> sebebi olmak değildir. Bu depo tam bu sınıfı avlıyor (`A6`'nın düşme gerekçesi) ve aynı
> hata **kural setinin kendisine** uygulandı: ölçülmemiş bir nedenle çalışan bir mekanizma
> kapatıldı. **Denetim `OPERASYON.md §7`'ye göre üç ajanla koşar** (`A` plan · `B` bütünlük ·
> `C` canlı kullanıcı); görev metinleri `OPERASYON-DENETIM.md`'de.

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
