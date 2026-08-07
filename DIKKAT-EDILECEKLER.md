# 🔴 DİKKAT EDİLECEKLER — garson fazı sonrası durum, eksikler ve şema budama tasarımı

> **Kapsam:** (1) bu ana kadar planla kod arasındaki sapmalar, (2) planın kendi eksikleri,
> (3) bundan sonra dikkat edilecekler, (4) 🔴 **şema budaması** — dört ölçümle tasarlanmış
> hâli ve inmeden önce kapatılması gereken tek boşluk.
>
> **Yazılma sebebi:** üç denetim ajanı + `dima v2 v3 için mimari karar (1).md` belgesiyle
> yapılan kıyas, kodda doğrulanmış bir eksikler listesi çıkardı. Her madde bir `dosya:satır`
> ya da bir **ölçüm** taşır; taşımayan madde bu belgeye girmedi.

---

## 0 · ŞU ANDA ACİL — TAM KAPI KIRMIZI

⊙ `lab/kapi.py --hepsi` (2026-08-07, faz kapanışından **sonra**): **9 kırmızı / 4045 yeşil**
(6 dk 43 sn). Dokuzunun **dokuzu da** son iki commit'ten (`9282b1a`, `2df0f8d`) geliyor ve
hiçbiri hedefli süitlerde görünmedi.

🔴 **Bu, politikanın kendi faturasının ikinci kez kesilmesidir.** `CLAUDE.md` zaten yazmıştı:
*"Merkezî dosya + davranış değiştiren demet → demet sonunda `--hepsi`."* `ask.py` ve
`answer.py` değişti, `--hepsi` yalnız **en sonda** koşuldu ve dokuz kusur o ana kadar
görünmedi. *Bir kapıyı sona bırakmak, onu bir kapı olmaktan çıkarır: artık bir teftiştir.*

| # | Kırmızı | Kök neden | Düzeltme |
|---|---|---|---|
| 1 | `test_bayrak_kaydi::test_YAMLDAKI_HER_bayrak_KAYITTA_var` | `diyalog_bellegi` `FLAG_REGISTRY`'de **yok** → admin panelinde adsız görünür | Bayrağı kayda ekle (etiket + açıklama + kategori) |
| 2 | `test_YAML_asamalari_GECERLI` | `diyalog_bellegi: on` → YAML bunu **boolean `True`** okuyor; geçerli aşamalar `off/alpha/beta/prod` | `diyalog_bellegi: prod` *(ya da tırnakla)* |
| 3 | `test_bayrak_kaydi_butun` | (1) ile aynı kök | (1) ile birlikte kapanır |
| 4 | `test_prompt_enhancer::test_YAML_off_TUZAGI_kapali` | Aynı boolean tuzağı — kapı bunu **adıyla** anlatıyor: *"bayrak sessizce AÇIK kalır"* | (2) ile kapanır |
| 5 | `test_beyanlar_curumesin` | `MIMARI §0`'daki `⟳` satırının `Durum` hücresini `◐ KISMEN İNDİ` yaptım; biçim kapısı `⟳` satırının **yalnız** *"UYGULANMADI"* demesine izin veriyor | `⟳` işaretçisini kaldır ve satırı ✅ ölçümlü olarak ilgili bölüme taşı (§10) |
| 6 | `test_kisa_devre_yok::test_YENI_KISA_DEVRE_EKLENMEDI` | `DA-10` düzeltmesi (`_donem_soru`) **yeni bir imza** üretti; envanter onu tanımıyor | Yeni dalı envantere **gerekçesiyle** ekle — dal meşru (netleştirme), imzası yeni |
| 7 | `test_ENVANTER_BAYATLAMADI` | `_PERIOD_TEXT` artık kullanılmıyor → muafiyet listesinde **ölü imza** | Ölü satırı sil |
| 8 | `test_ASK_FONKSIYONU_TAVANI_ASMIYOR` | `ask()` **1188/1179** (+9: `DA-5` bayrak okuması + `DA-10` katalog metni) | Ya `MUAFIYET_ASK_KOD`'a gerekçeyle yaz, ya `_donem_soru` üretimini bir modüle çıkar |
| 9 | `test_ASK_PY_DOSYASI…SISMIYOR` | `ask.py` 2471/2464 | (8) ile birlikte |

⚠ **İkisi gerçek ürün kusuru, yedisi muhasebe.** (2) ve (4) aynı şeyi söylüyor: bayrak
**sessizce açık** — yani `G2`'nin kill-switch'i **çalışmıyor**, sadece var görünüyor. Bu,
kapatmak için yazılmış bir maddenin kendi kusurunu üretmesidir.

---

## 1 · PLANLA KOD ARASINDAKİ SAPMALAR *(ölçülmüş)*

### 1.1 Sessiz sapmalar — gerekçesi hiçbir yerde yazılı olmayanlar

| # | Plan ne dedi | Kod ne yaptı | Durum |
|---|---|---|---|
| S1 | `G6`: `referans: {eksen, kaynak, hedef}` **alanı** | Alan **yazılmadı**; yerine `kiyas_cebiri` indirgemesi | ⚠ Sonuç daha iyi *(motor zaten vardı)* ama **`5.6`'yı açmıyor** — `compare` hâlâ enum |
| S2 | `G6`: `blend` Intent-JSON'a girer | Girmedi | 🔴 Kayıt yok |
| S3 | `G6`: `compare`'ın **deprecation**'ı | Tersi oldu — `compare` **terfi etti** (şemaya + beyaz listeye) | ⚠ Yön değişimi doğru ama planla çelişiyor |
| S4 | `G2.9`: netleştirmenin `yuksek` düzeyi uygulanır | Yalnız `kapali` uygulanıyor (`ask.py:2620`), kodun kendi itirafı yerinde | 🔴 Kayıt yok |
| S5 | `G0b.6`: `{{ENT_i}}` varlık perdesi | İnmedi — `yayilim.py` yalnız `{{NUM_i}}`/`{{DIM_i}}` üretiyor | 🔴 `MIMARI:1359` var gibi okutuyor |
| S6 | `G1.7`: temellendirme rozetleri **tıklanabilir** (`POST /cube`, 0 LLM) | Düz `<span>` | 🔴 Kayıt yok |
| S7 | `G0.13`: `features.yml` yorumları düzeltilir | Değişmedi | düşük |

🔴 **Sınıf uyarısı:** S1–S3 ve S5 aynı desende: *plan bir **alan/mekanizma** vaat etti, kod
bir **davranış** teslim etti ve ikisinin farkı yazılmadı.* Bu deponun adıyla andığı
**"beyan var, karşılığı yok"** sınıfı — ve bu kez beyan **planın kendisinde**.

### 1.2 Belge bakımı — `§13.6`'nın bağlayıcı kuralı çiğnendi

`§13.6`: *"kod ve belge **AYNI COMMIT**'te gider."*

| kayıt | ne oldu |
|---|---|
| #1 §4'ün değişmezi ikiye bölünür (`G4`) | `G4` commit'inde **yazılmadı**; 12 commit sonra kapanışta yazıldı |
| #3 `KÇ-1` beyan-açık sapması (`G1`) | Aynı — `G1`'de değil, `b297e6c`'de |
| #4 `llm_sema_kisitli` NO-OP (`G0`) | `MIMARI`'ye **hiç girmedi**; kapanışta yazıldı |
| `app/diyalog.py` (`G2`'nin katmanı) | `MIMARI`'de **hâlâ mimari kaydı yok** — fazın en büyük yeni katmanı belgesiz |

⚠ Ve `OPERASYON-DURUM.md` başlığı **ikinci kez bayatladı**: 13 commit boyunca *"planlama
bitti, `G0` bekliyor"* yazdı. Dosyanın kendi uyarısı birincisini anlatıyor ve
*"her faz commit'inden sonra bu blok güncellenir"* diye kural koyuyor.
**Bir kuralı yazmak, onu uygulamak değildir.**

---

## 2 · PLANIN KENDİ EKSİKLERİ *(kodun değil, planın kusuru)*

| # | Eksik | Sonucu |
|---|---|---|
| P1 | `§13.6` *"beş şey"* diyor ama **altı** satır listeliyor; `Z.3` de *"beş"* diyor | Bir sayım hatası, **kayıt #4'ün düşmesini kolaylaştırdı** |
| P2 | `Z.2` *"sekiz satırın tamamı"* diyor; alet **on** satır ilan ediyor ve **dördünü hiç ölçmüyordu** | `G0.12`'nin *"alet körse `G1` başlamaz"* kırmızı çizgisi **fiilen sınanamadı** *(kapandı — `3cf56ef`)* |
| P3 | Plan **şema budamasından hiç söz etmiyor** | En büyük token kalemi hiç ele alınmadı — §4 |
| P4 | Plan **prompt caching**'i §7.1'de tartışıyor ama bir **faz maddesi** yapmıyor | Kodda `cache_control` → **0 isabet** |
| P5 | Plan `viz` dışı grafik türlerini kapsamıyor | Danışman belgesi bu maddede bizden ileride |
| P6 | Planın kabul ölçütleri **route-başarısı** nüfusunda tanımlı | Budama gibi *"route pes ettiğinde"* devreye giren şeyler **ölçülemez** — §4.4 |

---

## 3 · BUNDAN SONRA DİKKAT EDİLECEKLER *(bu turda bedeli ödenmiş kurallar)*

### K1 · Ajan raporu **ikinci el kanıttır**
Üç denetim ajanının 13 bulgusundan **biri yanlıştı** (`DA-6`: `== 11` cırcırı). Kodu
okumadan uygulasaydım **çalışan bir meta-kapıyı sökmüş** olacaktım.
> *Kodu okumadan uygulanan bir düzeltme, olmayan bir kusuru "düzelterek" gerçek bir kapıyı söker.*

### K2 · `except Exception` **yazılmamış kodu da gizler**
`NameError: wren_for_request` bir demet boyunca yutuldu; iddia kapısı **şemasız** koştu.
Yeni kural: bir `except`'in kapsadığı çağrı **testte en az bir kez gerçekten** koşmalı.

### K3 · Bir dilin derleyicisi koşulmuyorsa, o dilde yazılan her şey **denetimsizdir**
`tsc` bu operasyonda **ilk kez** `G6`'da çağrıldı; frontend `G1`'den beri derlenmiyordu.
⚠ **Açık borç:** `tsc` gecelik CI'da **hâlâ koşmuyor**.

### K4 · Her cevapta dolu olan bir alan, bir **ayrım ölçütü** olamaz
`kanit_sinifi` `raporlanabilir()`'i totolojiye çevirmişti; kapandığında altından `soz`
çıktı. **İki kusur üst üste bindiğinde, birini kapatmak ötekini bulur.**

### K5 · Bir alanın **var olması**, taşınması demek değildir
`G2`'nin bellek zinciri tamamen yazılmış ve testliydi; `types.ts`'te **tek satır** eksikti
ve `KURAL_DEVAM` üretimde **hiç ateşlenmedi**. Kapı da yeşil veriyordu (sınıf körlüğü).
→ Yeni kapı: `test_K2c_ISTEK_ALANI_GONDERILIYOR_mu`.

### K6 · Bir satırı **raporlamak**, onu ölçmek değildir
Alet on satır basıyordu, dördünü ölçmüyordu; `0|0|0` **başarısız** gibi okunuyordu.
→ Yeni kapı: kör satır artık **kırmızı test**.

### K7 · `--hepsi`'yi demet **sonuna** değil, merkezî dosya değişince **hemen** koş
Bu turda dokuz kırmızı en sona kadar görünmedi (§0). Ölçülen maliyet: 6 dk 43 sn.
*Bir kapıyı sona bırakmak, onu bir teftişe çevirir.*

### K8 · Bir kill-switch **YAML'de görünmesi** yetmez, **okunduğu** ölçülmeli
`diyalog_bellegi: on` → boolean `True` → `resolve_for` elemedi → bayrak **sessizce açık**.
Kapı bunu adıyla anlatıyordu ve yine de yazıldı.

---

## 4 · 🔴 ŞEMA BUDAMASI — dört ölçümle tasarlandı

### 4.1 Bugünkü durum: budama **yok**

`ask.py:2857` → `catalog_text, cube_index = cube_router.build_catalog(schema)` — **tam
şema**. Ölçüldü (demo, **23 cube**):

| ne | bugün giden |
|---|---|
| katalog metni (intent yolu) | **4.038 token** |
| `oneOf` intent şeması | 10.038 token — 🔴 **üretiliyor ve ATILIYOR** *(sağlayıcı `oneOf` desteklemiyor; `select_cube` docstring'i: "BU SAĞLAYICIDA KULLANILMAZ")* |
| Discovery şema prompt'u | 🔴 **16.767 token** |
| prompt caching | ❌ yok (`grep cache_control` → 0) |

⚠ Bu **23 cube'luk demo**. 100 cube'lu bir müşteride sayı ~4 katına çıkar.

### 4.2 Naif budama **TEHLİKELİ** — birinci ölçüm

Yalnız `ilgili_cubelar` ile budama, 359 yer-gerçekli soruda:

> 🔴 **%13,4'ünde doğru cube'u DÜŞÜRÜYOR.** Bazılarında **boş** dönüyor
> (`is emri adedi` → `[]`).

Doğru cube budanırsa LLM **yanlış menüyü** görür ve sessiz-yanlış üretir — bu deponun en
pahalı hata sınıfı. **Tek testle inseydi bu görünmezdi.**

### 4.3 Doğru tasarım: **BİRLEŞİM + FAIL-OPEN**

İki sinyal **farklı eksenlerden** bakıyor ve birbirini tamamlıyor:

* `ilgili_cubelar(q)` → cube kimliği **ve boyut** sinonimleri
* `measure_cube_candidates(q)` → **ölçü** sinonimleri

```
seçilen = ilgili_cubelar(q) ∪ measure_cube_candidates(q)
if not seçilen:            # 🔴 FAIL-OPEN — şüphede BUDAMA YOK
    seçilen = tüm katalog
```

⊙ **Üç bağımsız kümede ölçüldü:**

| küme | vaka | recall | kayıp | fail-open | ort. cube | tasarruf |
|---|---|---|---|---|---|---|
| katalogdan üretilmiş | 359 | **%100** | **0** | 6 | 3,9/23 | **%83,2** |
| dağınık/yazım hatalı | 122 | **%100** | **0** | 4 | 2,7/23 | **%88,2** |
| elle yazılmış, `route=None` | 2 | %100 | 0 | 0 | 2,0/23 | %91,3 |

Kıyas için tek sinyaller:

| tasarım | recall | tasarruf |
|---|---|---|
| yalnız `ilgili_cubelar` | %95,8 · **15 kayıp** | %76,6 |
| yalnız `measure_cube_candidates` | %89,7 · **37 kayıp** | %29,5 |
| 🟢 **birleşim + fail-open** | **%100 · 0 kayıp** | **%83–88** |

### 4.4 🔴 İNMEDEN ÖNCE KAPATILMASI GEREKEN TEK BOŞLUK

**Yer gerçeğim yanlış nüfustan geliyor.** Yukarıdaki 481 vakanın yer gerçeği `route()`'un
kendi başarısı — ama budama **yalnız `route()` pes ettiğinde** önemlidir (LLM ancak o zaman
çağrılır). Doğru nüfusta (etiketli **ve** `route=None`) elimizde yalnız **2 vaka** var.

> *Bir ölçümün sayısı değil, hangi nüfustan geldiği karar verir.*

**Bu yüzden budama şu üç şart olmadan `prod` olamaz:**

1. **Etiketli route-başarısızlık korpusu** — `lab/gercek_dunya.py::VAKALAR`'ın `cube`
   etiketli vakaları 42'de 2. En az ~100 vaka gerekiyor *(üreteç zaten var; etiket
   eksik)*.
2. **Bayrak arkasında** (`sema_budama: alpha`) ve **fail-open** — boş seçimde tam katalog.
3. **`KURAL G-1`** — canlı sağlayıcıyla **iki koşum**; ayrışırsa karar yok (`⊘`).

### 4.5 Uygulama sırası *(her adım ayrı ölçülür)*

| adım | ne | kapı |
|---|---|---|
| B1 | `cube_router.budanmis_index(q, schema)` — birleşim + fail-open, **saf fonksiyon** | Birim test: 3 küme, recall %100 |
| B2 | Etiketli route-başarısızlık korpusu (~100 vaka) | Yeni: `test_budama_recall.py` — **kayıp 0** şartı |
| B3 | `ask.py:2857`'de bayrak arkasında bağla | Korpus gerilemesin · `sessiz_yanlis` **artmasın** |
| B4 | Token ölçümü: gerçek çağrıda önce/sonra | `lab/` raporu — **beyan değil sayı** |
| B5 | `oneOf` şemasının boşuna üretimini kes *(sağlayıcı kullanmıyor)* | Ölçülen CPU kazancı |
| B6 | Prompt caching — **üç katmanlı önek** (§7.1): sabit kurallar · tenant kataloğu · değişken soru | ⚠ Budama **değişken** katmanda kalmalı, yoksa cache isabeti düşer |

🔴 **B6'nın gerilimi yazılı olsun:** budama her sorguda **farklı** önek üretir, caching
**sabit** önek ister. İkisi *"iki kaldıraç"* diye toplanamaz — kısmen birbirini iptal eder.
Çözüm katmanlamadır: **yarı-sabit tenant kataloğu budanmaz, budama değişken katmanda yapılır.**

---

## 5 · AÇIK BORÇ ÖZETİ *(kapanmamışlar)*

| borç | ağırlık |
|---|---|
| 🔴 Tam kapı **kırmızı** — 9 test (§0) | **acil** |
| 🔴 `diyalog_bellegi` **sessizce açık** — kill-switch çalışmıyor | **acil** |
| 🔴 Şema budaması yok — en büyük token kalemi (§4) | yüksek |
| 🔴 Etiketli route-başarısızlık korpusu yok (§4.4) | yüksek — budamanın ön koşulu |
| 🔴 `tsc` gecelik CI'da koşmuyor | yüksek |
| ⚠ `B-G4` yarım: `compare` enum→**ALAN** + `blend` → `5.6` **hâlâ bloke** | orta |
| ⚠ `app/diyalog.py`'nin `MIMARI` kaydı yok | orta |
| ⚠ `G2.9` netleştirme `yuksek` düzeyi uygulanmıyor | orta |
| ⚠ `{{ENT_i}}` varlık perdesi inmedi ama belgede var gibi | orta |
| ⚠ `Niyet.temsil_edilemeyen` izi indirgemeden habersiz — iz yanıltıcı | düşük |
| ⚠ `viz` dışı grafik türleri (danışman belgesi bizden ileride) | düşük |

---

## 6 · TEK CÜMLE

Kod tarafı planın **ötesinde** birkaç yerde *(kıyas cebiri, hava boşluğu, `R11`'in ölçülüp
geri alınması)*; ama **muhasebe** tarafı geride: dokuz kırmızı bir kapı, sessizce açık bir
kill-switch, belgesiz bir katman ve **hiç ele alınmamış** bir token kalemi.
*Bir sistemi iyi yapan şey ne yaptığı değil, ne yaptığını bilmesidir.*



yeni eklendi bunlar da analiz edilmeli kararlaştırılmalı ve fazlara gerekirse eklenmeli

Bununla birlikte, sistem canlıya alındığında veya infaz (kodlama) aşamasında tıkanıklık yaratabilecek, yol haritasına eklenmesi veya netleştirilmesi faydalı 5 somut teknik köşe vakası ve geliştirme önerisi şunlardır:1. Canlı Akış (SSE Streaming) ile narration_guard Çatışması (G5.10)G5.10 adımı, anlatı metninin kullanıcıya SSE üzerinden "token token" akıtılmasını öngörüyor. Ancak narration_guard ve iddia.py kapıları fail-closed çalışır ve bir cümlenin güvenli/doğru olup olmadığına cümle tamamlandıktan sonra karar verir.Risk: Eğer LLM'den çıkan token'lar üretildiği an istemciye (Frontend) basılırsa, narration_guard hatalı bir sayıyı veya iddia.py unhandled bir şema vaadini tespit ettiğinde o metin kullanıcının ekranında zaten görünmüş olacaktır.Daha İyi Çözüm (Cümle-Tamponlu Akış / Sentence-Buffered Streaming):SSE hattı token bazlı değil, cümle bazlı tamponlanarak (buffer) çalıştırılmalıdır. Metin \n veya nokta (.) karakterine kadar tamponda birikir; oluşan cümle narration_guard ve iddia.py testlerinden $\le 5\text{ ms}$ içinde geçer, onay alırsa istemciye bir blok halinde akar. Düşerse istemciye hiç iletilmez.2. Kümülatif Sorgu Durumu (Accumulated State) vs. 2 Turluk Bağlam Sınırı (G2)JPMorgan araştırmasına dayanarak bağlam penceresinin $\le 2$ tur ile sınırlandırılması gürültüyü (noise) engellemek için doğrudur. Ancak B2B analitik kullanımında kullanıcılar genellikle 4-5 turluk derinleşme (drill-down) sohbetleri yaparlar:"Son 3 ayın satışları" (Tur 1)"Sadece Marmara bölgesi" (Tur 2)"Bunu ürün bazında kır" (Tur 3)"Peki ya Ege bölgesinde durum neydi?" (Tur 4)Risk: Tur 4'e gelindiğinde 2 turluk strict chat penceresi kullanılırsa, sistem Tur 1'deki "Son 3 ayın satışları" bağlamını unutabilir.Daha İyi Çözüm: LLM'e giden sohbet geçmişini (Chat History) 2 turda tutarken; arkadaki Accumulated CubeQuery nesnesini uzun süreli (Long-lived State) taşımak.İstemci Tur 4'te "Peki Ege'de durum ne?" dediğinde, LLM'e giden prompt'a chat geçmişi değil, yalnızca mutfakta birikmiş olan mevcut CubeQuery karteri enjekte edilir. Böylece sohbet geçmişi şişmeden kümülatif filtreleme 10 tur boyunca bozulmadan yürür.3. Eksen 1 (Sipariş Fişi) İçin Tek Dev Model Riski (G0.1 / §7.4)Karar gereği OpenRouter üzerindeki tek bir büyük açık kaynak model (ör. NVIDIA 550B türevi) hem Eksen 1 (Intent-JSON) hem Eksen 2 (Anlatı) için tek model olarak seçilmiştir.Risk: 550B parametreli devasa bir model, Eksen 2'deki akıcı anlatım için harika bir performans gösterirken; Eksen 1'deki basit bir JSON şeması doldurma işinde yüksek TTFT (Time To First Token) ve kuyruk gecikmesi (Queue Latency) üretebilir.Daha İyi Çözüm: G0 ölçüm etabında eğer Eksen 1 gecikmesi $p95 > 1.5\text{ saniye}$ çıkarsa, mimariyi bozmadan Eksen 1 için hızlı/hafif bir SLM (14B/32B), Eksen 2 (Anlatı) için ise büyük modeli çalıştırma seçeneği $B$ planı olarak config.py seviyesinde yedekte tutulmalıdır.4. lab/garson.py İçin Sentetik Cümle Çeşitlendirmesi (G0)lab/garson.py ilk aşamada gercek_dunya.py içindeki 15 gerçek kullanıcı ifadesini taban alıyor. Ancak Garson katmanının gerçek başarısı, kullanıcının aynı isteği 50 farklı jargon ve devrik cümle yapısıyla sormasında yatar.Daha İyi Çözüm: 15 çekirdek ifadeden, bir defaya mahsus çevrimdışı (offline) bir LLM scripti ile 150+ sentetik varyasyon (Paraphrased Test Set) üretilip lab/garson_variations.json olarak kaydedilmelidir.Bu küme canlı LLM çağırmadan, K (Kaset) modunda deterministik ayrıştırma ve slot doldurma başarısını stress-test etmek için kullanılmalıdır.5. narration_guard Toplu Düşüş Alarmları (G4 / G5)G4 ve G5 kapıları, metindeki sayılar veritabanıyla uydurulamazsa veya yetenek dışı bir iddia varsa cümleyi düşürür ve sistem otomatik olarak 2. basamağa (interpret.summary - süssüz ama doğru) geçer.Eksik Nokta: Eğer model güncellenir veya prompt biçimi değişirse, sistem sessizce tüm anlatı cümlelerini düşürmeye başlayabilir. Kullanıcı yanlış sayı görmez (güvenli) ama sistem sürekli "soğuk/süssüz" yanıtlar vermeye başlar ve kimse bunun farkına varamaz.Daha İyi Çözüm: Telemetriye bir "Düşme Oranı Eşik Alarmı" (Guard Drop Rate Metric) eklenmelidir. Son 50 istekte anlatı cümlelerinin düşme oranı $\%30$'u aşarsa, sistem yöneticisine Alert: High Narrative Guard Drop Rate uyarısı düşmelidir.