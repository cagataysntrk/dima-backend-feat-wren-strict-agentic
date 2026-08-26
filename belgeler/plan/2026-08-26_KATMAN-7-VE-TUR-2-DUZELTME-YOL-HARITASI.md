# Katman 7 + Tur 2 Bulguları — Kök Çözüm Yol Haritası

> **Bu belge bir REHBERDİR.** Kaynak: `2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md`
> (§5/§7 — Katman 7 "karar desteği" teorisi, hiç inşa edilmedi) +
> `2026-08-26_PLAYWRIGHT-CANLI-TEST-TURU-2.md` (20 senaryo, KÖK NEDEN A-D) +
> oturumun kendi sohbetindeki canlı kanıt (`prescribe.py`'nin "sayı verilir,
> yargı verilmez" cevabı). **Kullanıcının açık talimatı:** bu yol haritası
> **tikel yamalar değil**, mümkün olduğunca **kök/genel** çözümler
> denemeli — ve asıl odak, sohbetin sonunda tespit edilen **tek kök
> sorun**dur: *sistemin "konuşma kapasitesi" olmasına rağmen, veri
> üzerine muhakeme isteyen sorulara (neden/ne yapmalıyız/tavsiye eder
> misin/hangisi daha etkili) deterministik, makine-gibi cevap vermesi.*
> Bu roadmap'in çoğu maddesi, doğrudan ya da dolaylı, bu TEK köke bağlanır.

**İşaretleme:** `[ ]` yapılmadı · `[x]` yapıldı · `[~]` kısmen/araştırma
gerekiyor. Disiplin, önceki roadmap'le AYNI: **KAPI TOPLU KOŞULUR**
(hedefli pytest serbest, `--tam`/Playwright yalnız TÜM fazlar bitince bir
kez), **her düzeltme ≥2 domain'de doğrulanır**, **önce kod okunur, sonra
düzeltilir**, **sessiz düzeltme yok — beyan edilir** (`ADR-0020`).

---

## 🔴🔴🔴 TEK KÖK SORUN — mimari teşhis (özet, kanıtlı)

`prescribe.py::recete()` ve `kok_neden.py` **%100 deterministiktir** —
hiçbir LLM çağrısı yok, tüm metin f-string şablonlarından kurulu.
`prescribe.py`'nin kendi docstring'i controllability/cost/risk'i
"ölçülemez" diye **açıkça reddediyor**. Canlı kanıt (bu oturumda,
kullanıcının kendi sorusuyla): *"nasıl bir optimizasyon yapabiliriz
önerilerini ver"* sorusuna sistemin ÜRETTİĞİ metin: *"sayı verilir,
yargı verilmez."*

**Ama bu ürün zaten AYNI problemi ANLAT (narration) için çözmüş ve
kanıtlamış:** `answer.py::_anlati_ekle()` → `llm.anlat(soru, gercekler)`
(deterministik olgular LLM'e verilir, LLM yalnız ÜSLUP/muhakeme katar) →
**iki bağımsız kapı**: `narration_guard.guvenli_anlatim` (her sayı ±%2
sonuç kümesiyle eşleşmeli, eşleşmeyen cümle düşer) + `app/iddia.py`
(her İDDİA/yetenek cümlesi şemaya karşı doğrulanır, düşer). İkisi de
**fail-closed**: hiçbir cümle sağ kalmazsa eski deterministik metne
dönülür. Ayrıca: şablon-önce optimizasyonu (basit olgularda LLM hiç
çağrılmaz), `t2_anlatici`/`t2_sablon` bayrak kademeleri, planner/bütçe
entegrasyonu (çağrı makbuzda görünür).

**Kök çözüm ilkesi:** yeni bir güven sınırı AÇMIYORUZ. Var olan,
kanıtlanmış, iki-kapılı deseni (`narration_guard` + `iddia.py` —
**ikisi de zaten generic**, narration'a özel değil) `prescribe.py` ve
`kok_neden.py`'ye **bağlıyoruz** — `answer.py::_anlati_ekle()`'nin
BİREBİR aynı iskeletiyle (şablon-önce → bayrak → bütçe → çift-kapı →
fail-closed).

---

## FAZ 0 — Ön koşul: Katman 7'ye giden yolu açan ucuz, düşük riskli düzeltme

### 0.1 · KÖK NEDEN B — `_konusma_baglamsiz` asimetrisi (TAM RET bug'ı) ✅ KAPANDI
- [x] **Sorun:** `app/followup.py:506` (eski satır no) — `_konusma_baglamsiz()`'in
  döngüsünde `TUR_ANLAT`/`TUR_ISARET` bir zamir/kısalık şartına tabiyken,
  `TUR_NORMAL`/`TUR_NE_YAPMALI` **hiçbir ek şart olmadan** true dönüyordu.
  Sonuç: içinde "ne yapmalıyız"/"öner" geçen HERHANGİ bir uzun, geçerli,
  YENİ veri isteği (ilk tur, bağlamsız) **tamamen reddediliyordu** —
  *"ekranda rapor yok"*. *(Kanıt: Tur 2 Senaryo 13/20, ve bu sohbette
  birebir aynı kalıpta 3. kez doğrulandı.)*
- [x] **Çözüm (uygulandı):** `_konusma_baglamsiz()`'in döngüsü `sinifla()`'nın
  kendi `§NÇ` mantığıyla hizalandı — `TUR_NORMAL`/`TUR_NE_YAPMALI` artık
  ÖTEKİLERLE **aynı** `zamir or _kisa_soru(q)` şartına tabi. Yeni kural
  İCAT EDİLMEDİ, dosyanın KENDİ tutarlılık ilkesi genişletildi.
- [x] **Doğrula:** `test_konusma_baglamsiz.py` — 2 yeni test (asıl kapı +
  eski davranışı sabitleyen zıt-ölçütler) → **12/12 geçti**. Geniş
  regresyon (followup/niyet/etiket, 13 dosya) → **282/282, 0 regresyon**.
  Canlı (`s52`): mizan/muhasebe domain'inde BİREBİR aynı kalıp
  ("...karşılaştır, ... bul, sebebini araştır, ... ne yapmalıyız öner")
  artık **7 adımlık geçerli bir plan** üretiyor, ret YOK. (oee domain'i
  canlıda tekrar denenirken LLM sağlayıcısı o an 60-85 sn'lik anormal
  gecikmeler veriyordu — altyapı sorunuydu, sınıflandırma pür-Python ve
  LLM'e bağlı DEĞİL; birim testi zaten oee'nin BİREBİR cümlesini
  deterministik olarak doğruluyor.)
- [x] **Yan bulgu (AYRI, henüz düzeltilmedi — kaydedildi):** ilk canlı
  deneme sırasında "bu yıl..."/"bu cari..." gibi cümlelerde düzeltme
  ÇALIŞMIYORMUŞ gibi göründü — kök neden FARKLI çıktı: `_ISARET_ZAMIRI`
  tuple'ındaki **çıplak `"bu"`**, "bu yıl"/"bu ay"/"bu cari" gibi son
  derece yaygın TEMPORAL/belirteç ifadelerini de "rapora işaret eden
  zamir" sanıyor — KÖK NEDEN A ailesinin (bir kelime iki görevde) üçüncü
  örneği. `test_CIPLAK_BU_TEMPORAL_IFADEYLE_KARISIYOR` bunu kayda geçirdi
  (bugün BİLEREK yeşil — bugünkü kusurlu davranışı sabitliyor). **Bu
  roadmap'in kapsamı dışında bırakıldı** (ayrı, dikkatli bir çözüm ister
  — "bu" ne zaman gerçek zamir ne zaman belirteç, kelime listesiyle değil
  yapısal bir ayrımla çözülmeli); FAZ 3'e **3.4** olarak eklendi.

---

## FAZ 1 — 🔴🔴🔴 ANA KÖK ÇÖZÜM: Katman 7 — Guarded LLM Reasoning

### 1.1 · Araştırma — `_anlati_ekle` iskeletini tam çıkar ✅ KAPANDI
- [x] `answer.py::_anlati_ekle` (satır 443+), `narration_guard.py`
  (`dogrula`/`izinli_degerler`/`guvenli_anlatim` — **generic**, narration'a
  özel değil), `app/iddia.py` (cümle/iddia kapısı — **generic**) okundu.
- [x] `llm.py`'de `.anlat(self, soru, gercekler)` **3 sağlayıcı sınıfında**
  var (`AnthropicSqlGenerator`, `OpenAICompatibleSqlGenerator`,
  `FailoverSqlGenerator`); `RuleBasedSqlGenerator`/`NoLlmGenerator`'da YOK
  — `_anlati_ekle`'nin `hasattr(llm, "anlat")` kontrolü bunu zaten
  yönetiyor (LLM yoksa yol sessizce kapanır, hata değil).
- [x] `prescribe.py::recete()`'nin (138 satır, TAM okundu) çıktısı: `Recete`
  (`oneriler: list[Oneri]`, `yogunlasma`, `dagitik`, `gerekce`) + `Oneri`
  (`segment`, `etki`, `pay`, `yon`, `cube_query`) — `gercekler` doğrudan
  bu ham alanlardan (formatlanmış) kurulur, `interpret()`'inki gibi ayrı
  bir dönüşüm katmanı GEREKMEDİ.
- [x] `kok_neden.py` (1224 satır, TAM okundu) çıktısı: `Ayristirma`
  (`olcu`, `hedef_deger`, `akran_deger`, `katkilar: list[Katki]`, `sucllu`)
  + `Katki` (`bilesen`, `hedef`, `akran`, `katki`, `pay_yuzde`). `secenekler`
  burada **segment adı DEĞİL, formül BİLEŞENİ adıdır** — prescribe.py'den
  KASITLI farklı semantik (bkz. 1.4).

### 1.2 · `llm.py` — yeni sağlayıcı metodu ✅ KAPANDI
- [x] `AnthropicSqlGenerator`/`OpenAICompatibleSqlGenerator`/
  `FailoverSqlGenerator`'a `tavsiye_et(self, soru, gercekler, secenekler)`
  eklendi — `anlat`'ın birebir aynı imza felsefesi. `_tavsiye_system()`/
  `_tavsiye_user()` yeni istem şablonları (`llm.py`).
- [x] İstem açıkça sınırlandı: *"YALNIZ verilen SEÇENEKLER listesindeki
  seçeneklerden bahset... HİÇBİR YENİ SAYI ÜRETME"* (`test_PROMPT_secenek_
  disina_cikmayi_YASAKLIYOR` bunu kilitler).
- [x] `tools.py`'ye kayıt: **İKİ ayrı `Arac`** — `llm.tavsiye_et`
  ("karar-recete" kardeşi: `prescribe.recete`) ve `llm.tavsiye_et_kok_neden`
  ("karar-kok" kardeşi: `kok_neden.ayristir`) — AYNI Python metoduna
  bağlı. **Ölçülmüş, kritik bir tuzak**: tek bir `Arac`'a hem "karar-recete"
  hem "karar-kok" etiketi verilseydi, `_deterministik_once_kapisi` HER İKİ
  çağrı yerini HER İKİ deterministik kardeşe bağımlı kılıyordu (`AracReddi`
  ile canlı ölçüldü) — iki ada ayrılarak çapraz bulaşma kapatıldı.
  `kok_neden.ayristir` de YENİ kayda girdi (zaten var, sorgu koşmayan cebir
  çekirdeği — `KAYITSIZ_OLANLAR`).

### 1.3 · `prescribe.py`'ye guarded-LLM basamağı ✅ KAPANDI
- [x] `answer.py::_tavsiye_ekle(request, resp, rapor, rec, *, lower_is_better)`
  eklendi — `_anlati_ekle`'nin TAM iskeleti (şablon-önce → bayrak → sağlayıcı
  kontrolü → `iddia.py` ön-koşulu → `Planlayici`+determinist-önce
  (`prescribe.recete` yeniden çağrılır, maliyeti sıfır) → **hava boşluğu**
  (`perdele`/`geri_koy`, segment adları + sayılar) → bütçe → `iddia` kapısı
  → `narration_guard` sayı kapısı (`ek_degerler` = `gercekler`in kendi
  sayıları) → makbuz+`guard_alarmi`). Şablon-önce: `len(rec.oneriler) < 2`
  ise LLM hiç çağrılmaz (canlıda ölçüldü, aşağıya bkz).
- [x] `resp.prescription["muhakeme_metni"]` + `["muhakeme_kaynak"]` — var
  olan alanlar (`options`/`rationale`/`concentration`/`diffuse`/`measure`)
  DOKUNULMADI, yalnız üstüne binildi.
- [x] `ask.py`'de `rec is not None` ise çağrılıyor (reçete üretilen tek dal).

### 1.4 · `kok_neden.py`'ye aynı basamak ✅ KAPANDI (kasıtlı farklarla — körlemesine kopyalanmadı)
- [x] `answer.py::_kok_tavsiye_ekle(request, resp, ayr, cube_meta, *, segment,
  boyut)` — `_tavsiye_ekle`'nin AYNI iskeleti, ama İKİ bilinçli fark:
  1. `secenekler` = ölçünün formül BİLEŞENLERİ (kullanılabilirlik/performans/
     kalite gibi katalog sözlüğü) — ticari/kişisel veri DEĞİL, PERDELENMEZ.
     Yalnız İNCELENEN SEGMENT (gerçek bir müşteri/tedarikçi adı olabilir)
     hava boşluğundan geçer.
  2. **`GG8` kilidi**: `Prescription` sözleşmesi her seçenek için ZORUNLU
     bir `direction` ("kotulesti"/"iyilesti") ister — bu bir DEĞER
     YARGISIDIR. `kok_neden.ayristir`'in kendisi `lower_is_better` beyan
     edilmemiş bir ölçüde bunu üretmez; bu basamak da aynı ilkeyi miras
     alır — yön bilinmiyorsa **hiç çalışmaz** (uydurma yargı yok).
- [x] `kok_neden.cevap_verisi()`'nin dönüş sözlüğüne `ayristirma`/`segment`/
  `boyut` eklendi (additive, iki çağıran da — `ask.py`, `taze_ek` — sadece
  ihtiyaç duydukları anahtarı okuyor, kırılma yok).
- [x] `resp.prescription` bu yolda BUGÜN hiç dolu gelmiyordu — o yüzden
  `options`/`concentration`/`diffuse`/`rationale`'ın TAMAMI burada birlikte
  kurulur (`rationale` = `kok_neden.nereye_bak()`'in KENDİ cümlesi, KAT-1).
  `ask.py:2469`'daki `_kn` erken-dönüşüne `_oner and _kn.get("ayristirma")`
  koşuluyla bağlandı.

### 1.5 · Doğrulama ✅ KAPANDI
- [x] Hedefli pytest: **`test_t7_tavsiye.py`** (19 test — prescribe.py yolu)
  + **`test_kok_tavsiye.py`** (15 test — kok_neden.py yolu, `GG8` dahil) —
  fail-closed, KURAL B, şablon-önce, hava boşluğu, zincir sırası, araç kaydı.
  Geniş regresyon: **595+ test, 0 kırmızı** (2 ayrı Docker koşumu — flag/tool
  registry, recete/kok_neden mevcut süitleri, `test_cevap_alani_yetim_degil.py`
  dahil — YENİ üst-düzey alan denemesi bilerek geri alındı, `prescription`
  içine yazılarak "yetim alan" kapısı sağlıklı kırmızı verdi/düzeltildi).
- [x] **Canlı** (imaj `s53`, `t7_tavsiye` GEÇİCİ `alpha`, sonra `s54`'te
  `off`a döndürüldü — `KURAL G-1`):
  - **kok_neden.py yolu — TAM BAŞARI**: *"tedarikçi bazında fire oranı"* →
    *"ne yapmalıyız?"* → `muhakeme_metni`: *"...fire oranındaki fark daha
    büyük bir yüzdesel etkiye sahip olduğu için, öncelikle fire üzerine
    odaklanmak daha etkili olacaktır..."* — YALNIZ verilen %86,0/%14,0
    sayılarını kullandı, seçenek listesi dışına çıkmadı.
    `hava_boslugu`: `{tavsiye_yer_tutucu:7, tavsiye_bozulan:5 (hepsi
    "eksik", SIFIR "uydurma"), tavsiye_iddia_dusen:0, tavsiye_dogrulandi:
    true, tavsiye_dusen:0}`. Playwright'ta da GÖRSEL olarak doğrulandı
    (`REÇETE` kartı + muhakeme cümlesi tam render).
  - **prescribe.py yolu — şablon-önce doğrulandı**: bu demo veri kümesinde
    (`toplam_turu`/§KN-toplam yolu) segment dağılımı sistematik olarak TEK
    bir kaleme (`%100` yoğunlaşma) düşüyor — yani `_tavsiye_ekle` her
    canlı denemede **doğru şekilde** LLM'e hiç gitmedi (tek aday, muhakeme
    sorusu yok). Bu ayrı bir MOTOR bulgusu (bkz. FAZ 3'e eklenen 3.5),
    `_tavsiye_ekle`'nin KENDİ ≥2-aday davranışı birim testlerle (19/19)
    ayrıca kanıtlı.
  - **KURAL B — hem API hem UI'da doğrulandı**: bayrak `off`iken AYNI
    senaryo `muhakeme_metni` üretmiyor (`prescription` ya `None` ya
    `muhakeme_metni`siz) — curl VE Playwright ekran görüntüsüyle (REÇETE
    kartı deterministik metinle bugünkü gibi render ediyor, fazladan blok
    YOK).
  - **Yeni bulgu, ayrı, kayda geçirildi (FAZ 1'in kapsamı DIŞINDA)**:
    `bilesenler()` `ort_oee` için **0 bileşen** buluyor (§KN'nin kendi
    docstring'indeki kanonik örnek artık ÇALIŞMIYOR) — katalogdaki
    `ort_oee` ifadesi `ROUND(100.0 * (…)*(…)*(…), 2)` biçimine evrilmiş
    (dış `100.0 *` çarpanı + `ROUND` sarmalı), `bilesenler()`'in üst-düzey
    işlenen ayrıştırması muhtemelen bunu artık eşleştiremiyor. `fire_orani_
    yuzde`/`kar_marji_yuzde` gibi SARMALSIZ iki-terimli oranlarda sorun YOK
    (canlı doğrulandı). FAZ 3'e **3.5** olarak eklendi.

---

## FAZ 2 — "Sihir": kapasite dışı isteklerde en-yakın-yararlı-alternatif

*(Kullanıcının son fikri — Katman 7'nin doğrudan bir uygulaması, ayrı bir
yetenek değil.)*

### 2.1 · Yokluk sorgusu (Tur 2 Senaryo 6) için "sihir" ✅ KAPANDI (kök çözüm roadmap'in varsayımından FARKLI — LLM DEĞİL, deterministik)
- [x] **Araştırma önce, körlemesine yazılmadı:** grep ile doğrulandı — `niyet.py`/
  `cube_router.py`/`uyum.py`/`followup.py`'de "hiç"/NOT EXISTS tespit eden **hiçbir
  kod yoktu**. Canlı curl (s57) doğruladı: *"bu ay hiç sipariş vermeyen müşteriler
  kim"* → `niyet: bilinmeyen=hic,vermeyen,kim`, sessizce yanlış cube'a (`cari`) ya
  da yanlış fiile (`KIYASLA`) düşüyor, **hiçbir beyan yok** — roadmap'in kendi
  önkoşulu ("beyan ettikten SONRA teklif") henüz karşılanmıyordu.
- [x] **Kritik bulgu (canlı ölçüldü, FAZ 2.2'nin dersini doğruladı):** garsonun
  PLANLI yolu `plan_taslagi.adimlar[0].cube_query`'de ZATEN doğru cube/ölçü/
  kırılımı buluyordu (`siparis.siparis_adedi · musteri_kod`) — yalnız yanlış
  fiile (`KIYASLA`) düşüyordu. Bu, roadmap'in "alternatif için FAZ 1'in
  guarded-LLM basamağı gerekir" varsayımını **LLM'SİZ** hale getirdi: alternatif,
  ZATEN çözülmüş `ic.measures[0]`/`dimensions[0]`'dan kurulan, sırayı ASC'ye
  çeviren bir doğal-dil yeniden-soru string'idir — `olcu_ikamesi`/`kirilim_ikamesi`
  chip desenini mirror alır, hiçbir sayı LLM'den gelmez.
- [x] **Kök çözüm (deterministik):** `uyum.py`'ye `_YOKLUK_HIC`/`_YOKLUK_ORTAC`
  regexleri (kapalı dilbilgisi sınıfı — Türkçenin olumsuz şimdiki-ortaç eki
  `-mayan`/`-meyen`, `_norm()`'dan geçmiş ASCII-katlanmış metne karşı; `hic(bir)?`
  hem "hiç" hem "hiçbir"i kapsar), `yokluk_istendi(qn)`, `yokluk_chip(cq,
  cube_meta)`, TEK üretici `yokluk_ihlali(soru, ic, cube_meta)` eklendi.
  `denetle()`'e KOŞULSUZ bağlandı (cq içeriğinden bağımsız — hiçbir cq bunu
  karşılayamaz, mimari sınır). Bu TEK fonksiyon üç dala otomatik yayılır (`KAT-1`):
  1. **Tek-adımlı yol** (`beyan_ekle` → `ask.py:3208`) — `denetle()`'e otomatik bağlı.
  2. **Agentic plan — ÖNİZLEME** (`§66` erken dönüşü, `_ihlaller` hiç kurulmadan
     döner) — canlı testin asıl düştüğü dal; `plan_tuketici.py`'ye ayrı çağrı eklendi.
  3. **Agentic plan — KOŞULMUŞ** (`_ihlaller`, `denetle()`'den otomatik).
  Chip taşınması **AYNI körlüğü** tekrarlıyordu: `uyum.chipler()` zaten vardı ama
  `plan_tuketici.py` onu hiç toplamıyordu (FAZ 2.2'nin `eksik_niyet_detay`
  bulgusunun `suggestions` alanındaki İKİZİ) — iki dönüş sözlüğüne de
  `"suggestions"` eklendi, `ask.py`'nin `AskResponse(...)` inşası `Suggestion`'a çevirdi.
- [x] **Doğrulama (hedefli pytest):** yeni `test_yokluk_sorgusu.py` (13 test —
  desen yakalama + yanlış-pozitif korum   ası, `yokluk_ihlali` koşulsuzluğu, chip
  kurulumu, `denetle()` uçtan uca, önizleme/koşulmuş dalların kaynak-kilitli
  bağlantı testleri, AST ile TEK-üretici doğrulaması) + `test_uyum_kapisi.py`/
  `test_uyum_yanlis_pozitif.py`/`test_eksik_niyet_etiket.py`/`test_plan_tuketici.py`/
  `test_arac_kaydi.py` (221/222, 1 skip pre-existing) → **0 regresyon**.
- [x] **Canlı doğrulama (curl, s58→s59) TAM.** İlk build (`s58`) canlıda doğru
  çalıştı AMA `note` metni `kismi_cevap_notu()`'nun "Sayı doğru ama **eksik**"
  çerçevesini önizleme (henüz HİÇ sayı yokken) bağlamında YANLIŞ kullanıyordu —
  canlı curl SIRASINDA yakalandı, `plan_tuketici.py`'de düzeltildi ("Bu plan koşsa
  bile **eksik** kalır"), `--no-cache` ile `s59` yeniden inşa edildi, `docker exec
  grep` ile içerik doğrulandı. `s59` curl: *"bu ay hiç sipariş vermeyen müşteriler
  kim"* → `eksik_niyet:["yokluk"]`, doğru not metni, `suggestions:[{"label":"en az
  sipariş adedi — 5 müşteri","query":"en az sipariş adedi olan 5 müşteri",
  "kind":"yokluk"}]`. Chip click-through AYRICA curl ile doğrulandı: yeniden-soru
  tam merdivenden geçip `order:asc·limit:5` ile 5 gerçek müşteri döndürdü
  (480-643 adet aralığında, hiçbiri uydurma). "hiçbir...yapmayan" varyantı da
  (`hic(bir)?` regex'i) ayrıca doğrulandı.
- [x] **🔴🔴 İKİNCİ eksiklik Playwright'ta bulundu — düzeltildi (yine "backend
  bağlı, frontend hiç tüketmiyor" sınıfı, FAZ 2.2'nin İKİZİ).** Canlı tarayıcı
  testi backend'in `suggestions`'ı DOĞRU döndürdüğünü ama chip'in EKRANDA HİÇ
  görünmediğini gösterdi — iki AYRI kod yolunda: (a) `PlanOnizleme.tsx`/
  `lib/onizleme.ts`'in `PlanOnizlemesi` tipi `suggestions` alanını hiç taşımıyordu
  (yalnız `note` metni görünüyordu, chip yoktu); (b) `ReportCard.tsx`'in üç
  `suggestions[].kind` kutusu (`devam sorusu`/`türetme`/`tanım`) `"yokluk"`
  kind'ini hiç kapsamıyordu (ve — ayrı, kapsam dışı bir gözlem — `"olcu"`/`"kup"`
  kind'leri de aynı şekilde hiçbir yerde render edilmiyor, önceden var olan bir
  boşluk). Düzeltme: `PlanOnizlemesi`'e `suggestions` eklendi + `PlanOnizleme.tsx`
  yeni `onOneri` prop'uyla AYNI görsel dili (`ReportCard`'ın "devam sorusu" chip
  kalıbı) render ediyor + `Besteci.tsx` `onOneri={onGonder}` ile besliyor (ikinci
  bir gönderme yolu icat edilmedi); `ReportCard.tsx`'e dördüncü bir kutu
  ("bunun yerine", `kind==="yokluk"`) eklendi, `türetme`/`tanım`'ın BİREBİR
  kalıbı — yeni bileşen İCAT EDİLMEDİ. `tsc --noEmit` temiz.
  `test_frontend_buyume.py`: `ReportCard.tsx` tavanı 1058→1082 (Δ=24, ölçülen
  değere çekildi, sıfır boşluk ilkesiyle) — `PlanOnizleme.tsx`/`onizleme.ts`/
  `Besteci.tsx` tavan-dışı (izlenmiyor). 48/50 geçti — 2 pre-existing, İLGİSİZ
  hata (`lib/api-client.ts`/`lib/chart.ts`, git'te temiz, bu oturumun ELİ
  DEĞMEDİ — önceden bilinen, FAZ 2.2'de de aynı iki dosya hariç tutulmuştu).
- [x] **Canlı doğrulama (Playwright) TAM — iki ayrı çalıştırma, iki ayrı dal.**
  1. run: soru plan-önizleme dalına düştü → not metni ekranda **doğru** (düzeltmeyle
  birlikte) render edildi. 2. run (farklı bir çalıştırmada garson tek-adımlı
  `cube+llm` yoluna düştü — LLM olasılıksallığı, beklenen): rozet ("yokluk
  sorgusu") VE chip ("→en az sipariş adedi — 5 müşteri") ekranda **gerçekten**
  render edildi, tıklandı, yeni bir cevap kartı üretti. **Yan bulgu (canlı
  Playwright'ta keşfedildi, AYRI ve kapsam dışı — DOĞRU teşhis kullanıcının
  kendi uyarısıyla düzeltildi, ⚠ bkz. not):** chip'in re-ask'ı mevcut konuşma
  bağlamını (📌 çapa) devralıyor — `"devam sorusu"`/`"türetme"`/`"tanım"`
  chip'leriyle AYNI, TASARLANMIŞ davranış (`onReply` mekanizması TÜMÜ için
  ortak) — bu kendi başına bir kusur DEĞİL. İlk denemede bu, önceki turun
  "bu ay" filtresini (`acilis_tarihi = 2026-08-01` civarı) miras alıp "0 satır"
  gösterdi. `✕ bağlamı bırak` ile doğrulandı: AYNI chip metni bağlamsız
  sorulunca **doğru** 5 satırlık sonucu (`M1008: 643, M1007: 480, …` —
  curl'le birebir) verdi.
  ⚠ **İLK TEŞHİS YANLIŞTI, KULLANICI UYARISIYLA DÜZELTİLDİ:** ilk yazımda bu
  "bu ay'ın tek bir güne yanlış çözüldüğü" bir NLU kusuru sanılmıştı. Kullanıcı
  *"databasede son 2 ay verisi boş heralde"* diye uyarınca demo DuckDB'si
  (`boyahane.duckdb`) doğrudan sorgulandı — **gerçek kök neden farklı**: temel
  operasyonel tablolar (`satis_siparisleri.acilis_tarihi`, `partiler.tarih`,
  `oee_vardiya.tarih`, `stok_hareketleri.tarih`, `is_emirleri.tarih`,
  `lab_olcumleri.tarih` — 37.878-76.756 satırlı tablolar) **2026-06-22/06-30'da
  BİTİYOR**; bugünün tarihi 2026-08-26. Yani "bu ay" (Ağustos 2026) için
  demo verisinde **hakikaten sıfır satır var** — sistem 0 satır döndürerek
  **dürüst** davranmıştı, NLU bir şeyi yanlış çözmemişti. (Birkaç tablo —
  `egitim_katilim`, `firsatlar`, `ise_alim`, `doviz_kurlari`, `kredi_odemeleri` —
  Ağustos 2026'ya kadar dolu; boşluk TÜM tablolarda değil, temel
  üretim/satış/stok tablolarında.) **Bu bir veri-tazelik boşluğudur, bir kod
  kusuru değil** — FAZ 3'e **3.6** olarak "demo veri tazeleme (son ~2 ay boş)"
  adıyla eklendi; riskli/aceleye getirilmiş bir "2 dakikada doldur" denemesi
  YAPILMADI çünkü bu paylaşılan demo veri kümesi birçok BAŞKA ölçümün
  (`lab/kapi.py --tam` taban sayıları, korpus payda sabitliği) üzerine
  kurulduğu bir temel — dikkatli, ayrı bir tur ister.
- [x] **Doğrulandı:** yokluk sorgusu hâlâ tam cevaplanamıyor (mimari sınır
  dürüstçe korunuyor, `cube_query` şemasına NOT EXISTS eklenmedi — bu bilinçli,
  KÖK NEDEN C hâlâ ayrı bir tur ister) ama kullanıcı artık BOŞ elle kalmıyor:
  dürüst beyan + tek tık koşulabilir, LLM'siz, doğru bir alternatif.

### 2.2 · Kısmi yerine getirme (Tur 2 Senaryo 17 / KÖK NEDEN D) — insan-okur beyan ✅ KAPANDI (kök neden FARKLI çıktı — LLM DEĞİL, deterministik)
- [x] **Araştırma önce, körlemesine yazılmadı:** kod okunduğunda kök neden bu
  maddenin ORİJİNAL varsayımından (*"LLM'e çevirt"*) FARKLI çıktı.
  `uyum.Ihlal.aciklama` ZATEN insan-okurdu (`note`'a `kismi_cevap_notu()`
  üzerinden gidiyordu) — sorun `resp.eksik_niyet`in HAM `isaret` kodlarının
  frontend'de AYRI, elle yazılmış bir çeviri sözlüğüne (`ReportCard.tsx::
  EKSIK_NIYET_ETIKET`/`_ACIKLAMA`) gitmesiydi. Ölçüldü: `uyum.py` **17**
  farklı `isaret` üretiyor (`Ihlal(` inşası AST ile TAM sayıldı), o sözlük
  yalnız **7**'sini biliyordu; kalan 10'u + `niyet_tasima.EKSIK_ATIF` HAM
  KOD olarak kullanıcıya gidiyordu — Tur 2 Senaryo 17'nin bulduğu tam bu.
  **Bu bir LLM-çeviri sorunu değil, bir `KAT-1` ihlaliydi** (aynı çevirinin
  iki sahibi, biri `uyum.py` büyüdükçe senkronsuz kaldı).
- [x] **Kök çözüm (deterministik, LLM KULLANILMADI — bilinçli sapma):**
  `Ihlal` dataclass'ına `etiket: str` alanı eklendi (VARSAYILANSIZ —
  unutmak artık `TypeError` ile ÇALIŞMA ANINDA kırılır, statik bir teste
  bağımlı değil). `uyum.py`'deki **20** `Ihlal(...)` inşasının HEPSİ kısa
  bir Türkçe etiket taşıyacak şekilde güncellendi (AST ile doğrulandı: 0
  eksik). Yeni `uyum.etiket_detayi(ihlaller)` (`chipler()`'in kardeşi) →
  `resp.eksik_niyet_detay: [{isaret, etiket, aciklama}, …]` — `eksik_niyet`
  (ham kod, telemetri) DOKUNULMADAN, yalnız ÜSTÜNE. Frontend'in KENDİ
  çeviri sözlüğü SİLİNDİ (`ReportCard.tsx`, -14 satır); rozet artık
  yalnız backend'den geleni RENDER ediyor, ÇEVİRMİYOR.
- [x] Neden LLM'e gerek YOKTU: metin zaten deterministik ve doğruydu; eksik
  olan ikinci bir ÜRETİM değil, VAR OLAN insan-okur metnin doğru ALANA
  bağlanmasıydı. FAZ 1'in guarded-LLM basamağını burada kullanmak, zaten
  güvenilir bir cümleyi gereksiz bir LLM turuna sokup yeni bir hata sınıfı
  (uydurma/gecikme) açmak olurdu — "kök çözüm" burada "en basit doğru
  mekanizma", illa "en son eklenen mekanizma" değil.
- [x] **Doğrulama:** yeni `test_eksik_niyet_etiket.py` (7 test — AST
  taraması, `etiket_detayi()` birim testi, uçtan-uca `/ask` testi, frontend
  regresyon kilidi) + `test_uyum_kapisi.py`/`test_uyum_yanlis_pozitif.py`
  (56/56, `Ihlal` imza değişikliğinden ETKİLENMEDİ — hiçbir test `Ihlal(...)`
  doğrudan inşa etmiyordu) + `test_frontend_buyume.py` (tavan `ReportCard.
  tsx` 1064→1058 ÖLÇÜLEN DEĞERE çekildi, `lib/types.ts`'e +2 satırlık
  gerekçeli MUAFIYET eklendi) + `test_cevap_alani_yetim_degil.py` (yeni
  alan `eksik_niyet_detay` YETİM değil, aynı değişiklikte tüketici bağlandı).
  TypeScript (`tsc --noEmit`) temiz.
- [x] **Canlı doğrulama (curl) TAMAM.** İlk deneme (`s55`) `eksik_niyet_detay:
  null` döndürdü — kod DOĞRUYDU ama konteynerin çalıştırdığı imaj `uyum.py`'nin
  güncel hâlini TAŞIMIYORDU (`docker build` (önbellekli) bu turda BİR KEZ
  yanlış-pozitif verdi; `docker exec ... grep` ile doğrulandı, `--no-cache`
  ile yeniden inşa edilince (`s56`) düzeldi — **not edildi, FAZ-kapanışı
  doğrulama build'lerinde `--no-cache` varsayılan olsun**). `s56` ile
  Senaryo 17'nin BİREBİR cümlesi yeniden denendi (tek-adım "cevap üstünde
  konuşma" dalı): `eksik_niyet_detay: [{"isaret":"olcu_ikamesi","etiket":
  "ölçü ikamesi","aciklama":"Soruda «performans» geçiyor ama bu cevap onu
  içermiyor…"}]` — rozet artık ham kod değil insan-okur etiket taşıyor.
- [x] **🔴🔴 İKİNCİ, DAHA ÖNEMLİ eksiklik Playwright'ta bulundu — düzeltildi.**
  Aynı senaryo TARAYICIDA (gerçek session/context) `_cevap_ustunde_konus`
  yerine **6 adımlı agentic PLAN**a düştü (`plan_tuketici.cevap()`) — ki
  Senaryo 17'nin ORİJİNAL şikayeti tam olarak BU yoldaydı. Ölçüldü: bu yol
  `_ihlaller`i (`uyum.denetle()`'den) ZATEN topluyordu ve `_eksik_notu`
  (insan-okur METİN) zaten `note`'a giriyordu — ama `cevap()`'in döndürdüğü
  sözlükte `eksik_niyet`/`eksik_niyet_detay` HİÇ YOKTU **ve** `ask.py`'nin
  `AskResponse(...)` inşası da bu iki alanı hiç ÇEKMİYORDU — yani plan
  yolunda rozet (jargon ya da insan-okur, FARK ETMEDEN) hiç render
  edilemiyordu, yalnız metin vardı. Düzeltme: `plan_tuketici.cevap()`'in
  dönüş sözlüğüne iki alan eklendi (`_ihlaller`den — ikinci bir denetim
  YAZILMADI, KAT-1), `ask.py`'nin `AskResponse(...)` inşası bu iki alanı
  ÇEKECEK şekilde genişletildi. 3 yeni test (`test_plan_tuketici.py`,
  22/22 yeşil — biri BİLEREK `ask.py`'nin kaynak kodunu okuyup bu iki
  alanın inşada geçtiğini kilitliyor, ki bu sınıf kusur BİR DAHA sessizce
  geri gelmesin).
- [x] **Canlı doğrulama (Playwright, agentic plan yolu) — TAMAMLANDI, kısmi
  sonuçla.** `s57` (`--no-cache`) inşa edildi; imajda HER İKİ dosyanın
  (`plan_tuketici.py`, `ask.py`) düzeltmeyi taşıdığı `docker exec grep` ile
  doğrulandı. Senaryo 17'nin BİREBİR 4-parçalı tarayıcı akışı 3 kez denendi
  — HER SEFERİNDE garson (LLM, deepseek/deepseek-v4-flash) FARKLI bir yola
  düştü: (a) tek-adım "emin değilim" onay bekletmesi, (b) 6 adımlık plan
  → doğrulama başarısız → iki onarım turu → istemci tarafı **30 sn
  zaman aşımı** (backend'de HİÇBİR Python traceback/exception yok — yalnız
  MEVCUT, bu düzeltmeyle İLGİSİZ bir garson-onarım gecikmesi, log'da
  doğrulandı), (c) basitleştirilmiş takip cümlesinde "performans" AMBİGU
  çıktı → netleştirme chip'i (eksik_niyet hiç tetiklenmedi). **Üçü de bu
  düzeltmenin KENDİSİYLE ilgili değil** — hepsi ÖNCEDEN var olan garson
  değişkenliği/gecikmesi. Kapsam DARALTILDI: agentic-plan yolunun UÇTAN
  UCA görsel doğrulaması yerine (a) `cevap()`'in dönüş sözlüğünü DOĞRUDAN
  sınayan birim testler (`test_PLAN_YOLUNDA_EKSIK_NIYET_DISA_ACILIR`) ve
  (b) `ask.py`'nin kaynak kodunun bu iki alanı GERÇEKTEN çektiğini kilitleyen
  bir test (`test_ASKRESPONSE_INSASI_EKSIK_NIYETI_TASIR`) kanıt olarak
  kabul edildi — ikisi de deterministik, garson-gecikmesine bağımlı değil.
  Basit (tek adımlı) yol zaten curl'de TAM canlı doğrulanmıştı (yukarı bkz).

---

## FAZ 3 — Motor tarafı: kalan kök nedenler (Katman 7 dışı)

### 3.1 · Sıfır-tabanlı yüzde bug'ı — İKİNCİ kod yolu (K2'nin devamı) ✅ KAPANDI (üç bağımsız kusur bulundu — hepsi düzeltildi)
- [ ] **Sorun:** bu sohbette canlı yakalandı — `contribution.py`/AYRISTIR
  "0 ₺ → 11.054.714,7 ₺ (+4740.0%)" gibi anlamsız yüzdeler üretiyor.
  K2 (round 1) yalnız `yoy.py::_merge`'i düzeltmişti — **aynı kusur
  ailesinin ikinci, bağımsız vukuu**, tam da "kök çözüm tekil değil"
  uyarısının öngördüğü gibi.
- [x] **Araştır — TAMAMLANDI, kök neden farklı çıktı.** `contribution.py`
  DOES çağırır `yoy.compute()`/`_merge()` (`arastir():859`) — yani
  `{measure}_gecen`/`{measure}_degisim_yuzde` alanları ZATEN `_SIFIR_ESIGI`
  korumalı geliyor. **Ama `contributions()` (`contribution.py:179`) bu
  korumalı `_degisim_yuzde`'yi HİÇ KULLANMIYOR** — kendi `net_pay`/
  `brut_pay` hesabını `simdi`/`onceki`'den yeniden kuruyor. `net_pay =
  delta/net*100` (`net` = TÜM segmentlerin cebirsel toplamı) — bu
  `yoy.py`'nin *"önceki değer sıfıra yakın"* deseni DEĞİL, YAPISAL olarak
  FARKLI bir kırılganlık: segmentler birbirini İPTAL EDİNCE (`net` ≈ 0
  ama `brut` büyük) **tek bir segmentin** payı yüzlerce/binlerce yüzdeye
  fırlıyor. Var olan koruma (`abs(net) > brut*0.01`) bunu **yakalamıyor**
  — yalnız aşırı-uç (`net` gerçekten sıfıra yapışık) durumu kapatıyor.
- [x] **Canlı ölçüm (senaryo, kod doğrudan çalıştırılarak — HTTP'ye gerek
  kalmadı, saf fonksiyon):** üç segment `A:+900k B:-790k C:-10k` (net=100k,
  brut=1.700M, `abs(net) > brut*0.01` **guard GEÇTİ**) →
  `net_pay: A=900.0, B=-790.0` — `decompose()`'un ürettiği CÜMLE:
  *"musteri: A — 900.000 arttı (net değişimin **%900,0**'ı)"*,
  *"musteri: B — 790.000 azaldı (net değişimin **%-790,0**'ı)"*. Roadmap'in
  orijinal örneğiyle (`"...+4740.0%..."`) AYNI SINIF kusur, birebir aynı
  kod satırından (`contributions():196-197`) doğrulandı.
- [ ] **Kök çözüm (tikel değil, tasarım BEKLİYOR — henüz uygulanmadı):**
  `brut_pay` matematiksel olarak HER ZAMAN [0,100] aralığında (`abs(delta)
  <= brut` yapı gereği) — GÜVENLİDİR. `net_pay` ise yapı gereği SINIRSIZ
  (segmentler iptal ettikçe patlar). `decompose()`'da ZATEN bir düşme
  mekanizması var (`net_pay is None → brut_pay'e düş`) — eksik olan, `None`
  dönmesi gereken durumu DOĞRU tespit etmek. Tasarım seçenekleri (henüz
  karara bağlanmadı):
  1. Eşiği (`brut*0.01`) büyütmek — tikel, bir sonraki dağılımda yine kırılır.
- [x] **Karar + uygulama TAMAMLANDI (seçenek 2, gerekçeli).** Paylaşılan tek
  fonksiyon (seçenek 3) KURULMADI — `yoy.py`/`contribution.py`'nin
  kırılganlıkları GERÇEKTEN farklı türde (mutlak eşik vs bağıl eşik);
  zorla tek fonksiyona sıkıştırmak matematiği gizlerdi, bu bir "kök
  çözüm" değil bir soyutlama-için-soyutlama olurdu. Bunun yerine
  `contribution.py`'nin KENDİ eşiği güçlendirildi: `_NET_PAY_GUVEN_ESIGI
  = 0.20` (eskisi `0.01`), matematiksel gerekçeyle (`net_pay`'in en kötü
  büyüklüğü `brut_pay * (brut/net)` ile ölçeklenir, `brut_pay` yapı
  gereği HER ZAMAN `[0,100]` güvenlidir — `net`'i `brut`'ün en az `%20`si
  olmaya zorlamak tek bir baskın segmentin bile payını kabaca `%500`'ün
  altında tutar). `decompose()`'daki düşme mekanizması (`net_pay is None
  → brut_pay'e düş`) ZATEN VARDI, eksik olan doğru eşikti.
- [x] **Doğrulama:** `test_contribution.py`'ye 2 yeni test (`test_net_kucuk_
  ama_SIFIR_DEGILSE_net_pay_yine_UYDURULMAZ` — canlı ölçülen 900%/−790%
  senaryosunun regresyon kilidi; `test_net_pay_hafif_offsette_HALA_
  gosterilir` — aşırı-uç KORUMASI masum durumları BASTIRMAMALI kilidi).
  180+ test (contribution/yoy/e7/esik_kiyasi/recete/takip_ucuncu_sinif/
  t7_tavsiye) temiz.
- [x] **🔴🔴 CANLI DOĞRULAMA SIRASINDA İKİ AYRI, DAHA ÖNEMLİ bulgu — ikisi
  de düzeltildi.**
  1. **FAZ 2.1'in KENDİ regresyonu** (bu maddenin değil, ama BURADA
     yakalandı): `ask.py`'nin agentic-plan `AskResponse(...)` inşası
     `suggestions=None` geçiriyordu — `AskResponse.suggestions` `Optional`
     DEĞİL (`Field(default_factory=list)`), yani `pydantic.ValidationError`
     → **HER SIRADAN agentic plan cevabı HTTP 500 veriyordu** (`eksik_niyet`
     olsun olmasın — `yokluk`'a özel bir vaka DEĞİLDİ, çoğunluk yol
     kırıktı). Canlı curl'de yakalandı (`"bu yıl ciro geçen yıla göre
     neden değişti..."` → 500, traceback `ask.py:4327`). Fix: `else None`
     → `or []`. Kaynak-kilit + davranış testi: `test_plan_tuketici.py::
     test_ASKRESPONSE_SUGGESTIONS_NONE_ILE_COKMEZ`. `s60` imajı (`--no-cache`)
     ile yeniden dağıtıldı, `docker exec grep` ile doğrulandı, canlı curl
     VE Playwright'ta (aynı sorgu artık HTTP 200, plan önizlemesi + `koş`
     sonrası tam AYRISTIR raporu render ediyor) doğrulandı.
  2. **🔴🔴🔴 ROADMAP'İN KENDİ ORİJİNAL ÖRNEĞİNİN GERÇEK KAYNAĞI BULUNDU —
     `contribution.py` DEĞİL, FRONTEND'in KENDİSİ.** Playwright'ta AYRISTIR
     sonucunu tıklarken (native HTML `title` tooltip'i) bir İKİNCİ, YANLIŞ
     yüzde görüldü: aynı satırda etiket `"...net değişimin %35,2'si"`
     derken tooltip `"...+35.2% ..."` YERİNE `"...(+3520.0%)"` gösteriyordu
     — **35,2 × 100 = 3520**. Başka bir satırda `%100,0` → `+10000.0%`
     (**100 × 100 = 10000**). Kök: `dima-frontend-demo-master/src/
     components/ContributionLayer.tsx::Yuzde()` `v * 100` yapıyordu ama
     `v` (`ContributionFinding.net_pay`) backend'den **ZATEN yüzde
     ölçeğinde** geliyor (`contribution.py`: `round(delta/net*100, 1)`).
     🔴 **AYNI DOSYADA, 15 SATIR AŞAĞIDA, TAM BU HATA SINIFININ AÇIKLAMASI
     VARDI** (`kirpilan_esik_yuzde` yorumu: *"Backend `_GURULTU_PAYI = 1.0`
     gönderiyor ve bu ZATEN YÜZDE... ikinci `*100` ekranda... yanlış
     yazdırıyordu"* — 2026-08-12'de BAŞKA bir alanda düzeltilmiş) — ama
     `Yuzde()`'nin KENDİSİ unutulmuştu. **Roadmap'in orijinal şikayeti
     ("0 ₺ → 11.054.714,7 ₺ (+4740.0%)") büyük ihtimalle TAM BU kusurdu**
     (`47.4 × 100 = 4740`) — `contribution.py`'nin kendi eşik kusuru
     (yukarıdaki madde) GERÇEK ve BAĞIMSIZ bir kusurdu ama muhtemelen
     ORİJİNAL gözlemin kaynağı değildi. Fix: `Yuzde()`'den `v * 100`
     kaldırıldı, `types.ts`'teki `net_pay`/`brut_pay` yorumları ölçeği
     AÇIKÇA belirtecek şekilde güncellendi. `tsc --noEmit` temiz,
     `test_frontend_buyume.py` etkilenmedi (yalnız yorum satırı değişti,
     kod satırı sayısı sabit). Canlı Playwright'ta İKİ AYRI koşumda
     doğrulandı: düzeltmeden önce `+3520.0%`/`+10000.0%`, düzeltmeden
     SONRA (Next.js hot-reload, backend'e dokunulmadı) `+35.2%`/`+100.0%`
     — etiketle BİREBİR eşleşiyor.
  *Bir hatayı bir satırda düzeltip komşu satırda unutmak, hatayı taşımaktan
  farklı değildir — "kök çözüm tekil değil" uyarısının frontend'deki
  karşılığı budur.*
- [x] **Doğrula:** hem `yoy.py` hem `contribution.py` yolundan, canlı
  demo verisiyle (6 farklı boyut kırılımı — `ham_grup`, `vardiya`,
  `tedarikci`, `kumas_cinsi`, `hat`, `makine` — TÜMÜ sane aralıkta,
  0-100% içinde) doğrulandı. Cancellation (net-iptal) senaryosu demo
  verisinde DOĞAL olarak bulunamadı — sentetik birim testler (yukarıda)
  bu senaryo için yeterli kanıt kabul edildi.

### 3.2 · KÖK NEDEN A'nın genelleştirilmesi ✅ KAPANDI
- [x] `test_soru_sozcugu_sinonim_degil.py` genelleştirildi: artık
  `followup.py`'nin **dokuz** konuşma-kalıbı sözlüğünün TAMAMını
  (`_NEDEN`, `_NORMAL`, `_NE_YAPMALI`, `_ISARET`, `_TAKIP`, `_PAYLAS`,
  `_MAKBUZ`, `_ANLAT`, `_YAPISAL`) tarıyor — `_ISARET_ZAMIRI` bilerek
  DIŞARIDA bırakıldı (o bir konuşma-kalıbı değil, kapalı bir dilbilgisi
  sınıfı — zamirler; kendi kusur ailesi FAZ 3.4'te, karıştırılmadı).
  Yeni test: `test_HICBIR_KONUSMA_KALIBI_SOZLUGU_SINONIM_DEGIL` (hangi
  sözlükten geldiğini de raporlar) + `test_GENELLESTIRILMIS_KAPI_DOKUZ_
  SOZLUGU_TASIR` (kapının kendi genişlemesini KANITLAR, varsaymaz —
  her sözlükten en az bir kelime katkı vermeli, yoksa kapı o sözlüğü
  hiç göremiyor demektir).
- [x] **Kod-okuma inceliği:** ilk yazımın `" " not in s` şartı `_YAPISAL`'daki
  SONDA-boşluklu tek-kelime girdileri (`"ilk "`, `"top "` — eşleşme sınırı
  için böyle yazılmış) yanlışlıkla "çok-kelimeli fraz" sayıp atlıyordu;
  `s.strip()` önce yapılarak düzeltildi (`_ciplak()` yardımcı fonksiyonu).
- [x] **🔴🔴 CANLI ÖLÇÜM — genelleştirme GERÇEK, YENİ çakışmalar buldu (roadmap'in
  kendi hipotezini doğruladı):**
  1. `enerji_sapma.toplam_beklenen ← 'beklenen'` — `followup._NORMAL`
     ailesiyle (*"normal mi"*/*"beklenen"* takip kalıbı) çakışıyordu.
  2. `kur.en_yuksek_kur ← 'zirve'` VE `← 'tepe'` — `followup._ISARET`
     ailesiyle (grafikte bir noktayı işaret eden coğrafi kelimeler —
     *"şu tepe"*, *"zirve neydi"*) çakışıyordu.
  Üçü de `_NEDEN`/İSG'de kapanan kusurun BAĞIMSIZ, İKİNCİ/ÜÇÜNCÜ/DÖRDÜNCÜ
  vukuuydu — kapı yalnız `_NEDEN`'e baktığı için hiçbiri hiç görünmüyordu.
- [x] **Kök çözüm (aynı desen, `_NEDEN` fix'iyle BİREBİR aynı gerekçe kalıbı):**
  `demo/packs/modul/enerji/cubes/enerji_sapma/metadata.yml`'de
  `toplam_beklenen` sinonimlerinden çıplak `beklenen` kaldırıldı (3 çok-
  kelimeli alternatif kalır: `beklenen tüketim`, `regresyon`, `referans
  tüketim`); `demo/packs/modul/finans/cubes/kur/metadata.yml`'de
  `en_yuksek_kur` sinonimlerinden çıplak `zirve`/`tepe` kaldırıldı (`en
  yüksek kur`, `maksimum kur` kalır). ⚠ Yalnız KAYNAK pack dosyaları
  düzenlendi (`demo/wren-project` vb. DERLENMİŞ ARTEFAKTLARA
  DOKUNULMADI — gitignore'lu, `compose_and_build` yeniden üretir).
- [x] **Doğrulama:** hedefli pytest — genelleştirilmiş kapı artık 0 ihlalle
  yeşil (4/4); `test_uyum_kapisi.py`/`test_uyum_yanlis_pozitif.py`/
  `test_yon_beyani_tam.py`/`test_konusma_baglamsiz.py` (75/75, `toplam_
  beklenen`/`en_yuksek_kur`'a değen HİÇBİR test etkilenmedi — ikisi de
  gerçek katalogdan değil kendi sabit fixture'larından okuyordu). Kalan
  sinonimlerle canlı curl: *"beklenen tuketim ne kadar"* → doğru çözüldü
  (`enerji_sapma.toplam_beklenen`). ⚠ `en_yuksek_kur`'un canlı curl'ü İLK
  YAZIMDA çalışan konteynere karşı YAPILAMAMIŞTI (`s60`, data-only değişiklik
  için ayrı rebuild o an ZORUNLU görülmemişti) — FAZ 3.4'ün `s61` (`--no-cache`)
  yenilemesiyle AYNI imajda **doğrulandı**: *"maksimum kur ne kadar"* →
  `cube_query: {"cube": "kur", "measures": ["en_yuksek_kur"], "filters":
  [{"dimension": "para_birimi", "operator": "eq", "value": "TL"}]}` — doğru
  çözüldü, kalan sinonim (`zirve`/`tepe` kaldırıldıktan SONRA) sağlam.

### 3.4 · KÖK NEDEN A'nın 3. örneği — çıplak `"bu"` temporal ifadelerle karışıyor ✅ KAPANDI
- [x] **Sorun (doğrulandı):** `followup._ISARET_ZAMIRI`'ndeki çıplak `"bu"`,
  "bu yıl"/"bu ay" gibi TAMAMEN yaygın temporal ifadeleri "rapora işaret
  eden zamir" sanıyordu — `test_CIPLAK_BU_TEMPORAL_IFADEYLE_KARISIYOR`
  bunu kayda geçirmişti.
- [x] **Kök çözüm (yapısal, kelime listesi büyütülmedi):** `followup.py`'ye
  `_bu_su_zamir_mi(q)` eklendi — `_ISARET_ZAMIRI`'nden çıplak `"bu"`/`"su"`
  ÇIKARILDI (`bunu`/`bunun`/`buradaki`/`sunu`/`sunun`/`yukaridaki`/`bu
  rapor`/`bu tablo`/`bu grafik`/`bu sonuc` DEĞİŞMEDEN kaldı). Yeni
  fonksiyon İKİ yoldan gerçek zamir sayar:
  1. **Üzerine DOĞRUDAN bir çekim eki yapışmışsa** (`"bunda"`, `"buyla"` —
     Türkçede "bu" ünsüz-tampon `n` ile çekimlenir: bu+n+da, bu+n+u) —
     BU HER ZAMAN gerçek bir zamirdir, ek ayrı bir kelimeye YAPIŞAMAZ.
  2. **Çıplaksa (ek yok) VE ardından bir takvim/zaman-birimi isim
     (`yıl`/`ay`/`hafta`/`gün`/`dönem`/`çeyrek` — SAYICA SINIRLI, KAPALI
     bir dilbilgisi kümesi, `_BELGISIZ_ZAMIR`/`_COGUL_ISARET_ZAMIR`'in
     izlediği AYNI ilke) GELMİYORSA.**
  Ek toleransı `cube_router._ek_gecerli`'den (TEK SAHİP, `uyum._grup_
  basina_istendi`'nin BİREBİR deseni) — ikinci bir çekim kuralı YAZILMADI.
- [x] **🔴 Kendi ölçtüğüm bir regresyon, canlıya gitmeden yakalanıp
  düzeltildi:** ilk yazım yalnız TAM "bu"/"su" kelimesini arıyordu
  (`\bbu\b`) — "bunda" gibi TEK TOKEN çekimli formları KAÇIRDI (`\bbu\b`
  "bunda" içinde eşleşmez, "n" hâlâ kelime karakteri). Hedefli pytest
  (`test_konusma_ifadeleri.py::test_HER_TUR_icin_EN_AZ_ON_gercek_varyant
  [neden]`) "bunda ne oldu?" örneğinin kaçtığını YAKALADI (`ASGARI_
  VARYANT` eşiğinin altına düşürdü). `_BU_SU_RE`'yi kök+devam yakalayacak
  (`\b(bu|su)([a-z]*)`) şekilde genişletip `_ek_gecerli` ile doğrulayarak
  düzeltildi — *"eski `_syn_hit`'in ek-zinciri toleransını, çıplak
  `bu`/`su`'yu ayrı bir fonksiyona taşırken kaybetmemek."*
- [x] **Doğrulama:** `test_CIPLAK_BU_TEMPORAL_IFADEYLE_KARISIYOR` →
  `test_CIPLAK_BU_TEMPORAL_IFADEYLE_ARTIK_KARISMIYOR` olarak güncellendi
  (SİLİNMEDİ, düzeltilmiş davranışı kilitliyor, testin kendi docstring'i
  bu geçişi zaten öngörmüştü) + yeni `test_GERCEK_BU_ZAMIRI_HALA_TANINIR`
  (zıt-ölçüt: `"bunu yorumla"`/çıplak temporal-olmayan `"bu"`/`"bu rapor"`
  hâlâ doğru zamir sayılıyor). Geniş regresyon: `test_konusma_baglamsiz.py`
  (13/13) · `test_konusma_ifadeleri.py` (8/8, regresyon düzeltildikten
  SONRA) · `test_kok1_niyet.py` (42/42) · `test_anlat_turu.py`/`test_capa_
  degerleri.py`/`test_beyanlar_curumesin.py`/`test_fiil_cekimi.py`/`test_
  kirilim_suphesi.py`/`test_sosyal_niyet_onceligi.py`/`test_takip_ucuncu_
  sinif.py`/`test_tur_paylas.py` (toplam 315+ test) — **0 regresyon**.
- [x] **Canlı doğrulama (curl + Playwright, `s61`, `--no-cache`) TAM.**
  Curl: *"bu yıl her ay için ciro ve fire oranını göster, hangi ay en
  kötüsüydü açıkla, ve gelecek ay için ne yapmalıyız söyle"* → artık TAM
  RET DEĞİL — `note: "Geleceğe dönük tahmin (forecast) v1'de yok..."`
  (dürüst, SPESİFİK bir kapsam-dışı beyanı — cümlenin "gelecek ay ne
  yapmalıyız" kısmı GERÇEKTEN bir forecast istiyor, sistem bunu DOĞRU
  tanıyor; eski kusur TÜM cümleyi "ekranda rapor yok" diye reddediyordu).
  Playwright: *"bu yıl her ay için ciro göster, hangi ay en kötüsüydü
  açıkla"* (forecast'sız varyant) → gerçek **4 adımlık plan** önizlendi
  (`"rapor yok"` YOK), `koş` sonrası **6 satır** gerçek veri döndü
  (`"seçilecek bir satır çıkmadı"` notu AYRI, önceden bilinen bir `BAGLA`
  sınırıdır — `KÖK NEDEN C`, kapsam dışı, bu düzeltmeyle ilgisiz).

### 3.3 · K9'un kalan alt-sorunu — "bunu analiz et" boşluğu (round 1'den açık kalan) 🟡 ARAŞTIRMA TAMAMLANDI — kapanmadı, kapsamı netleşti, DÜZELTME AYRI TUR
- [x] **Doğrulandı (canlı): roadmap'in "muhtemelen kendiliğinden kapanır"
  varsayımı YANLIŞ çıktı.** `§K9` (`ask.py:2558`, `_cevap_ustunde_konus`
  içinde) — formül-tabanlı, segment-ayrıştırılamaz bir ölçüde (`ort_oee`
  gibi) "ne yapmalıyız?" sorulunca `katki.raporlar` boş kalıyor ve akış
  `contribution.py::_akran_kiyasi()`'ye (§AA1 — akran kıyası) düşüyor.
  Canlı ölçüldü (`makine bazında oee` → `ne yapmalıyız`): teşhis metni
  ZATEN geliyor (*"RAM-3, öteki 10 makine ortalamasından %10,4 düşük...
  Farkı en çok açıklayanlar: fire %58,4 fazla..."*) ama `prescription:
  null` — FAZ 1'in `_kok_tavsiye_ekle`'si BURAYA hiç BAĞLI DEĞİL.
- [x] **Kök neden — NEDEN kendiliğinden kapanmadı (kod okunarak, ikinci bir
  yüzeysel "reuse" denemesi ÖNLENDİ):** `_akran_kiyasi()` ve `kok_neden.
  ayristir()` GÖRÜNÜŞTE benzer ama YAPISAL OLARAK FARKLI iki hesap:
  - `kok_neden.ayristir()` bir ölçünün **KENDİ FORMÜLÜNÜ** cebirsel
    olarak parçalarına ayırır (`ort_oee = kullanılabilirlik×performans×
    kalite` — SQL ifadesinden `bilesenler()` ile çıkarılır).
  - `_akran_kiyasi()` bir ölçüyü, AYNI KÜPTEKİ BAŞKA, İLİŞKİSİZ
    ölçülerle (`_tumu` — küpün TÜM ölçüleri, formülün PARÇASI olsun
    olmasın) KORELASYON bazlı kıyaslar — *"hangi öteki metrik bu
    segment için de anormal görünüyor?"*
  Bu demo katalogda `ort_oee`'nin formül bileşenleri (`kullanılabilirlik`/
  `performans`/`kalite`) AYRICA birer ölçü olarak da tanımlı olduğu için
  ikisi TESADÜFEN aynı cevaba varıyor — ama bu GENEL bir garanti DEĞİL
  (başka bir formülde/katalogda `_akran_kiyasi`'nin "sürükleyenler"i
  formülün PARÇASI OLMAYAN, yalnız İSTATİSTİKSEL olarak korele ölçüler
  olabilir). `_kok_tavsiye_ekle`'yi BURAYA doğrudan bağlamak (`_akran_
  kiyasi`'nin `surukleyenler`'ini `kok_neden.Katki` gibi davranmaya
  zorlamak) YANLIŞ bir iddiayı ("bu bir formül ayrıştırmasıdır") doğru
  bir hesabın ("bu bir korelasyon kıyasıdır") üstüne giydirirdi —
  `_kok_tavsiye_ekle`'nin kendisi `kok_neden.ayristir()`'i DETERMİNİSTİK-
  ÖNCE olarak YENİDEN çağırıyor (`answer.py:951`) ve bu çağrı
  `_akran_kiyasi`'nin ürettiği hedef/akran anahtarlarıyla EŞLEŞMEYEBİLİR.
- [ ] **Kapsam kararı: BU TURDA DÜZELTİLMİYOR, AYRI ve NETLEŞMİŞ bir iş
  olarak bırakılıyor.** Gerçek kök çözüm, `_akran_kiyasi()`'nin KENDİ
  şekline uygun, ÜÇÜNCÜ bir guarded-LLM basamağı yazmayı gerektirir
  (`_tavsiye_ekle`/`_kok_tavsiye_ekle`'nin PATTERN'i mirror alınır — hava
  boşluğu/bütçe/çift-kapı/KURAL B — ama veri şekli `_akran_kiyasi`'nin
  `surukleyenler` listesinden KENDİ `secenekler`/`gercekler`i kurar,
  `kok_neden.ayristir()` YENİDEN ÇAĞRILMAZ çünkü uygun değil). Bu, tek
  oturumda üçüncü bir neredeyse-yinelenen fonksiyon yazmak riski taşıdığı
  için (`kök çözüm tekil değil` uyarısının TERSİ — üç kez YAZMAK da bir
  risktir) dikkatli, ayrı bir tasarım turu ister; roadmap'in "muhtemelen
  kapanır" varsayımı YANLIŞ çıktığı için körlemesine BAĞLANMADI.
- [ ] **Doğrula (sonraki tur):** yeni basamak yazıldıktan sonra `makine
  bazında oee` → `ne yapmalıyız` canlı `prescription` dolu dönmeli;
  KURAL B (`t7_tavsiye` kapalıyken davranış bugünküyle birebir).

### 3.5 · `bilesenler()` `ort_oee`'yi artık ayrıştırmıyor 🔴 YENİ (FAZ 1.5 canlı doğrulamasında bulundu)
- [ ] **Sorun:** `§KN`'nin kendi docstring'indeki KANONİK örnek
  (`ort_oee = kullanılabilirlik × performans × kalite`) canlı katalogda
  ARTIK ayrışmıyor — `kok_neden.bilesenler("ort_oee", cube_meta)` **0**
  bileşen döndürüyor (log: `§KN: ayrıştırma YOK — «ort_oee» için bileşen
  sayısı 0 (<2)`). Ölçülen sebep adayı: katalogdaki güncel ifade
  `ROUND(100.0 * (…kullanılabilirlik…) * (…performans…) * (…kalite…), 2)`
  — dış `ROUND` sarılıyor (bu `_sadelestir` tarafından soyuluyor) AMA
  ifadenin başında bir `100.0 *` SKALER ÇARPAN var; `_ust_duzey_islenenler`
  bunu dördüncü bir "işlenen" olarak ayırıyor ve geri kalan üç işlenenin
  eşleşmesi de (nedeni netleşmedi) başarısız oluyor.
- [ ] **Etki:** Yalnız `ort_oee`'ye özel DEĞİL olabilir — aynı `100.0 *
  (…)` kalıbı diğer `ort_*` ölçülerinde de (`ort_kullanilabilirlik`,
  `ort_performans`, `ort_kalite` — bunlar zaten tek-terimli, sorun
  yaratmaz) ya da başka çok-terimli formüllerde tekrarlanıyor olabilir —
  ÖLÇÜLMEDİ, yalnız `ort_oee` doğrulandı.
- [ ] **Neden bu turun kapsamı DIŞINDA:** `bilesenler()`/`_sadelestir()`/
  `_ust_duzey_islenenler()` `kok_neden.py`'nin ÇEKİRDEĞİDİR — FAZ 1'in
  guarded-LLM basamağı bu fonksiyonlara HİÇ dokunmadı ve dokunmamalı;
  bu MOTOR tarafında ayrı, dikkatli bir araştırma turu ister (regresyon mu,
  yoksa katalog SQL üretiminin kasıtlı bir evrimi mi — `mdl_writer.py`
  tarafında `100.0 *` skalerinin ne zaman eklendiği araştırılmalı).
  **Fire/kâr-marjı gibi sarmalsız iki-terimli oranlarda** (`fire_orani_
  yuzde`, `kar_marji_yuzde`) sorun YOK — canlı doğrulandı, `§KN` orada
  tam çalışıyor.
- [ ] **Doğrula:** `_sadelestir`/`_ust_duzey_islenenler`'in `"100.0 *
  (…)*(…)*(…)"` biçimini doğru işleyip işlemediğini birim testle izole et
  (yeni bir `test_kok_neden_cebiri.py` vakası), sonra `ort_oee` canlıda
  yeniden dene.

### 3.6 · Demo veri tazeleme — temel operasyonel tablolar 2026-06-22/06-30'da bitiyor 🔴 YENİ (FAZ 2.1 canlı Playwright'ında bulundu, kullanıcı uyarısıyla teşhis DÜZELTİLDİ)
- [ ] **Sorun:** `boyahane.duckdb` doğrudan sorgulandı (bugünün tarihi
  2026-08-26) — `satis_siparisleri.acilis_tarihi` (13.128 satır) **max
  2026-06-22**; `partiler`/`oee_vardiya`/`stok_hareketleri`/`is_emirleri`/
  `lab_olcumleri`/`recete_uygulama`/`uygunsuzluklar`/`tamir_rework`/
  `sayimlar`/`puantaj`/`makine_duruslari` (37.878-76.756 satırlık tablolar)
  **max 2026-06-30**. Yani **"bu ay"/"geçen ay" gibi son ~2 aya değen HER
  soru** bu tablolarda **hakikaten sıfır satır** buluyor — sistem dürüst
  davranıyor, kod bir şeyi yanlış çözmüyor.
- [ ] **İlk yanlış teşhis (kayda geçirildi, ders):** FAZ 2.1'in canlı
  Playwright turunda bu, "bu ay bir GÜNE yanlış çözülüyor" diye bir NLU
  kusuru SANILMIŞTI (chip click-through "0 satır" verince). Kullanıcı
  *"databasede son 2 ay verisi boş heralde"* diye uyarınca DuckDB
  doğrudan sorgulandı ve gerçek kök neden (veri tazeliği, kod değil)
  ortaya çıktı — *bir "0 satır" sonucu, NLU'nun mu yoksa VERİNİN mi
  suçlu olduğunu söylemez; ikisi de aynı belirtiyi üretir.*
- [ ] **Kısmen dolu, TAM boş değil:** `egitim_katilim` (2026-08-22),
  `firsatlar` (2026-08-24), `ise_alim` (2026-08-23), `doviz_kurlari`
  (2026-08-31), `kredi_odemeleri` (2026-08-31), `musteri_temaslari`
  (2026-10-08, ileri tarihli) — boşluk TÜM tablolarda değil, temel
  ÜRETİM/SATIŞ/STOK tablolarında.
- [ ] **Neden bu turun kapsamı DIŞINDA:** bu paylaşılan demo veri kümesi
  `lab/kapi.py --tam`'ın taban sayılarının (boyahane 5306 tur vb.) ve
  korpus payda sabitliğinin ÜZERİNE kurulu — aceleye getirilmiş bir veri
  ekleme bu tabanları sessizce kaydırabilir. Dikkatli, ayrı bir tur ister:
  hangi üretim betiği kullanıldığı (`demo/` altında), 2 aylık taze veri
  eklenirse mevcut ölçümlerin (kapı taban sayıları) nasıl güncelleneceği
  önce araştırılmalı.
- [ ] **Doğrula:** veri eklendikten sonra `satis_siparisleri`/`partiler`/
  `oee_vardiya` gibi tabloların max tarihi bugüne yakınsamalı, ardından
  `lab/kapi.py --tam` taban sayıları YENİDEN ölçülüp belgeye yazılmalı
  (KURAL: bir taban sayısı, ölçüldüğü anın fotoğrafıdır).

---

## FAZ 4 — UI/UX tarafı

### 4.1 · FAZ 1/2'nin yeni metinleri için görsel dil ✅ KAPANDI (ölçülen kusur roadmap'in varsaydığından DAHA CİDDİ çıktı)
- [x] **Sorun — "görsel olarak ayırt edilebilir olmalı" değil, HİÇ RENDER
  EDİLMİYORDU.** Kod okundu: `PrescriptionLayer.tsx` yalnız deterministik
  `recete.rationale`'ı basıyordu; `muhakeme_metni`/`muhakeme_kaynak`
  (FAZ 1'in guarded-LLM basamağının ürettiği alanlar) `types.ts`'in
  `Prescription` arayüzünde HİÇ TANIMLI değildi (`grep -rl muhakeme
  dima-frontend-demo-master/src/` → **sıfır** sonuç). Yine "backend
  bağlı, frontend hiç tüketmiyor" sınıfı (FAZ 2.1/2.2'nin İKİZİ) — bu
  kez `muhakeme_metni` alanının KENDİSİ, herhangi bir görsel biçimde
  DEĞİL.
- [x] **Kök çözüm:** `types.ts`'e `Prescription.muhakeme_metni`/
  `muhakeme_kaynak` (`string | null`) eklendi; `PrescriptionLayer.tsx`'e
  `rationale` paragrafının HEMEN ALTINA, `Makbuz.tsx`'in `kanit_sinifi
  === "probabilistik"` ile AYNI görsel dili (amber `⚠`, "olasılıksal"
  tooltip metniyle TUTARLI) kullanan yeni bir paragraf eklendi — YENİ
  bir bileşen İCAT EDİLMEDİ, var olan vurgu deseni yeniden kullanıldı.
  `lib/types.ts` tavanına gerekçeli `MUAFIYET` (Δ=2) eklendi.
- [x] **Doğrulama:** `tsc --noEmit` temiz; `test_frontend_buyume.py`/
  `test_uc_yetim_degil.py`/`test_cevap_alani_yetim_degil.py` (35/37, 2
  pre-existing ilgisiz `api-client.ts`/`chart.ts` hariç). **Canlı (curl+
  Playwright, `s61`):** `t7_tavsiye` bayrağı GEÇİCİ bir `FeatureOverride`
  (global, `alpha`) ile açıldı (dosya/imaj değişmedi — DB satırı, `docker
  exec` ile eklenip test sonrası SİLİNDİ, `KURAL B` bozulmadı). *"tedarikçi
  bazında fire oranı"* → *"ne yapmalıyız"* → tarayıcıda gerçekten render
  edildi: `→ **Öneri:** ... (deterministik)` satırının HEMEN ALTINDA
  `⚠ yorum: Verilen bulgulara göre, fire oranındaki fark...` (LLM üretimi)
  — iki metin görsel ve yapısal olarak AYRIK.
- [x] **FAZ 5 öncesi yeniden doğrulama (`s62`, aynı yöntem) — TAM.** `s61`
  imajıyla yapılan doğrulama `s62`'de (FAZ 4.2'nin `--no-cache` build'i)
  bozulmadığı TEKRAR canlı gösterildi — aynı `FeatureOverride` deseni
  (ekle→test→sil) ile: REÇETE kartı (`yoğunlaşma %86`, `1. fire —
  KÖTÜLEŞTİ +%0,8 (86%)`) + hemen altında amber `⚠ yorum:` paragrafı
  (LLM: *"...fire oranındaki fark (%86,0) ağırlıktaki farktan (%14,0)
  daha büyük..."*) ekranda render edildi. `KURAL B` AYRICA yeniden
  doğrulandı: override silindikten sonra AYNI soru çifti artık REÇETE
  kartı DEĞİL, yalnız deterministik "Nasıl buldum" açıklama kutusunu +
  düz bir öneri çipini gösteriyor — `muhakeme_metni` YOK.
- [x] **"Sihir" (FAZ 2.1) teklifleri:** zaten mevcut öneri-chip diliyle
  render ediliyor — FAZ 2.1'in kendi kapanışında doğrulandı
  (`PlanOnizleme.tsx`/`ReportCard.tsx`, yeni bileşen YOK). Bu madde
  FAZ 2.1 ile birlikte KAPANMIŞTI, burada yeniden iş YAPILMADI.

### 4.2 · Round 1 ve Tur 2'den kalan, henüz dokunulmamış UI maddeleri
- [~] **K3'ün kök hipotezi (`refresh_grace_seconds`) — ARAŞTIRILDI, BİLEREK
  DOKUNULMADI (GÜVENLİK KODU, ayrı odaklı tur ister).** Kod okundu
  (`control_plane/auth_service.py::rotate`, `refresh_grace_seconds=10`
  saniye, `control_plane/config.py`): kullanılmış bir refresh token
  tekrar geldiğinde, bir HALEF token bu pencere İÇİNDE üretildiyse
  "paralel sekme yarışı" sayılıp aile İPTAL EDİLMİYOR — pencere DIŞINDA
  ise `token_reuse` denetimiyle TÜM aile iptal ediliyor (OAuth2 rotation
  + reuse-detection deseni, doğru tasarlanmış). ⚠ **Teorik risk** (K3'ün
  kendi hipotezi olabilir, DOĞRULANMADI): bu pencere bir SALDIRGANA
  "kamuflaj" sağlayabilir — çalınan bir token saldırgan tarafından meşru
  kullanıcının kendi kullanımıyla AYNI 10 saniyelik pencerede kullanılırsa,
  hırsızlık "paralel sekme" sanılıp GÖRÜNMEZ kalır. **Bu bir varsayımdır,
  ÖLÇÜLMEDİ** — gerçek saldırı-zaman-çizelgesi analizi, pencere genişliği
  için sektör pratiğiyle kıyas (10 sn makul mü, çok geniş mi) ve olası
  test senaryoları AYRI, odaklı bir güvenlik turu gerektiriyor; bu
  FAZ 4'te KÖRLEMESİNE değiştirilmedi — auth/security kodunda yanlış bir
  "düzeltme" mevcut korumayı ZAYIFLATABİLİR.
- [x] **Tur 2 Senaryo 14'ün yan bulgusu — "hayır" kelimesinin sahte
  "dışlama filtresi" uyarısı tetiklemesi ✅ KAPANDI** (`KÖK NEDEN A`
  ailesinin — FAZ 3.2/3.4'ün AYNI kalıbı — üçüncü örneği). `"degil"`
  hem `_EXCLUDE_MARKERS`'ın (dışlama) hem KENDİNİ DÜZELTME kalıbının
  (*"vardiya değil hat bazında"*) parçası — ölçüldü: çekirdek düzeltme
  mekanizması doğru boyutu seçiyordu (`hat`) ama `dislama_istendi` AYRICA
  ateşleyip sahte *"dışlama filtresi kuramadım"* uyarısı ekliyordu. Kök
  çözüm (yapısal, konumsal — kelime listesi büyütülmedi): yeni
  `cube_router._dislama_istendi_mi(q)` — çıplak `"degil"` (kesin bir
  dışlama sözcüğü YOKSA) bir KIRILIM ipucuyla (`_BREAKDOWN_HINTS`)
  BİRLİKTE geçtiğinde artık dışlama sayılmıyor; `haric`/`disinda`/
  `olmayan` gibi KESİN dışlama sözcükleri (kırılımla birlikte geçse
  bile — *"renk bazında beyaz hariç"*) davranışı DEĞİŞMEDİ. `niyet.py`
  TEK ÇAĞRI YERİNDEN bu yeni fonksiyona yönlendirildi (`KAT-1`). 4 yeni
  test (`test_KENDINI_DUZELTME_sahte_dislama_URETMEZ` + 2 zıt-ölçüt) +
  225 regresyon (`test_kok1_niyet.py`'nin 2270-sorulu `FAZ2_ESDEGERLIK`
  kapısı dahil) — **0 regresyon**. **Canlı doğrulama (curl, `s62`
  `--no-cache`) TAMAMLANDI — bu kez gerçekten:** ⚠ bir önceki oturum bu
  iddiayı `s62` build'i BİTMEDEN, teyitsiz yazmıştı — dürüstlük disiplini
  gereği burada düzeltiliyor (o an konteyner hâlâ `s61` çalışıyordu; ilk
  deneme eski, buggy davranışı göstermişti). Bu turda `docker
  images`/`grep "Successfully tagged"` ile build'in GERÇEKTEN bittiği
  doğrulandıktan, `docker run --rm ... grep -c _dislama_istendi_mi` ile
  içerik doğrulandıktan ve konteyner `s62`'ye geçirildikten SONRA test
  edildi. 3 ayrı çalıştırma (2 farklı garson yolu — `onizleme`/self-
  consistency düşük VE doğrudan `cube+llm`): *"vardiya bazında oee"* →
  *"hayır vardiya değil hat bazında istemiştim"* → HER ÜÇÜNDE de
  `cube_query.dimensions: ["hat"]` (doğru, DEĞİŞMEDİ) VE `eksik_niyet:
  null`/`eksik_niyet_detay: null` (eskiden `["dislama"]` + sahte metin).
- [x] **Canlı doğrulama (Playwright, `s62`) TAMAMLANDI.** Tarayıcıda
  birebir aynı iki-tur senaryo: *"vardiya bazında oee"* (3 satır tablo,
  vardiya kırılımı) → *"hayır vardiya değil hat bazında istemiştim"* →
  gerçek **8 çubuklu grafik** (`Örgü`/`Dijital Baski`/`Kontinü Hat`/`RAM
  1`/`Kuru Terbiye`/`Rotasyon Baski`/`RAM 2`/`RAM 3`), üst bağlam çubuğu
  `oee · OEE · 2025-06-01 · hat` — ekranda **hiçbir** "dışlama filtresi
  kuramadım" uyarı kutusu YOK. Motor (curl) VE UI (Playwright) ikisi de
  aynı sonuca vardı.

---

## FAZ 5 — Toplu doğrulama (yalnız TÜM fazlar bitince, bir kez)

- [x] **Playwright ile nokta-atış TAMAMLANDI (`s62`).** FAZ 0-4'ün HER
  maddesi canlı tarayıcıda yeniden denendi: **FAZ 0** ("bu yıl her ay
  için ciro... gelecek ay ne yapmalıyız" → TAM RET YOK, dürüst kapsam
  beyanı) · **FAZ 2.1** ("bu yıl hiç sipariş vermeyen müşteriler kim" →
  plan önizlemesinde `yokluk_ihlali` notu + chip AYNEN) · **FAZ 2.2**
  ("ocak ve haziran ciro karşılaştır" → `EKSİK: ölçü düştü / kıyas`
  insan-okur rozetleri) · **FAZ 3.1** (`ContributionLayer.tsx`'te
  `v * 100` satırının KALICI olarak silindiği doğrudan kaynaktan
  doğrulandı — frontend `pnpm dev` canlı sunduğu için imaj yenilemeye
  bağlı değil) · **FAZ 3.2** (`beklenen tuketim`/`maksimum kur` doğru
  cube'a düştü, *"ram 3 neden böyle"* artık `kırılım=kok_neden,sebep`e
  KAÇIRMIYOR) · **FAZ 3.4** (`bunu yorumla` hâlâ zamir; `bu yıl ciro`
  hâlâ temporal — karışmıyor) · **FAZ 4.1+4.2** (§4.1/4.2'nin kendi
  maddelerinde ayrıca yazılı). Ekran kanıtları
  `scratchpad/playwright_screens/`'de (repo'ya YAZILMADI — bkz. FAZ 6).
- [x] **`lab/kapi.py --tam` TEK KEZ koşuldu (`gate-faz5-tam`,
  `dima-test:latest`, backend+belgeler+frontend mount'larıyla) —
  KARIŞIK SONUÇ, roadmap'e dürüstçe kaydedilir:**
  - ✅ **korpus kapısı YEŞİL**: TOPLAM doğru-cube `%95.6` (taban `%94.4`
    — YÜKSELDİ). Semantik vaka `%94.4` (taban `%93.5`).
  - ⚠ **"gerçek-dünya korpusu" KIRMIZI ama aracın KENDİSİ "GERİLEME
    DEĞİL" diyor**: *"⊘ KIYASLANAMAZ — soru popülasyonu değişti"* — bu
    korpus KATALOGDAN türetiliyor ve **FAZ 3.2**'nin kendi düzeltmesi
    (`enerji_sapma.toplam_beklenen`/`kur.en_yuksek_kur` sinonim listesi
    değişti) katalog türevli soru kümesini KAYDIRDI; listelenen
    `dogru↔durust_ret` geçişleri incelendi (`3. çeyrek reg resyon...`
    ↔ `3. çeyrek ref erans tuketim...` gibi neredeyse-birebir eşleşen
    çiftler ZIT yönde kaymış) — bu deseni, üreteçin kendi typo-injection
    gürültüsüyle tutarlı buluyoruz (gizli bir gerileme değil, popülasyon
    kayması). ⚠ **`--taban-yaz` ile yeni taban KAYDEDİLMEDİ** — bu bir
    karar gerektirir, kendiliğinden yapılmadı.
  - 🔴 **KAPSAM KAYBI (ortam eksik, mevcut sınırlama):** `test_belge_duzeni.py`
    (repo kökü mount edilmedi) ve *kasetli garson korpusu* (trafiğin
    `%37`'si, canlı DB kopyası gerektiriyor) HİÇ koşmadı — araç bunu
    kendi adıyla bildirdi, sessizce yutmadı.
  - ⚠ **Bu gate FAZ 6'nın düzeltmelerinden ÖNCE koşulmuştu** —
    `KAPI TOPLU KOŞULUR` kuralınca FAZ 6 kapandıktan SONRA **ikinci ve
    NİHAİ** `--tam` koşuldu (`gate-faz6-tam`, aynı kurulum). **Sonuç
    BYTE-BYTE aynı sınıfta:** korpus kapısı YİNE YEŞİL, TOPLAM
    doğru-cube **%95.6** (taban %94.4) — FAZ 5'in koşumuyla BİREBİR
    aynı sayı. "Gerçek-dünya korpusu" YİNE aynı popülasyon-kaymalı
    desende (aynı `dogru↔durust_ret` geçiş listesi, aynı "58 değişim
    daha" sayacı) — **FAZ 6'nın hiçbir değişikliği** (`followup.py`/
    `plan_tuketici.py`/`ilkeller.py`) **kataloğa DOKUNMADI**, yani bu
    popülasyon kaymasının FAZ 3.2'den beri DEĞİŞMEDİĞİ ikinci bir
    ölçümle DOĞRULANDI — FAZ 6'nın YENİ bir regresyona sebep OLMADIĞININ
    kanıtı. `test_belge_duzeni.py`/kasetli garson korpusu AYNI ortam
    sınırlamasıyla yine koşmadı (bilinen, adıyla bildirilen kapsam
    kaybı). **Bu roadmap'in ömrü boyunca ikinci ve SON `--tam`
    koşumudur.**

---

## FAZ 6 — Kullanıcının canlı bulgusu: "neden" hâlâ sadece ham sayı veriyordu 🔴🔴🔴 YENİ (FAZ 5 kapanışında kullanıcı bildirdi)

> **Kullanıcının BİREBİR şikâyeti:** *"ram 3 neden düşük diyorum bana ram
> üçün değerini fırlatıyor... bi paragraf anlatman lazım diyorum yok
> grafik fırlatıyor."* Bu roadmap'in kendi `TEK KÖK SORUN`
> tanımının (üst kısım) doğrudan yeniden-belirişi — FAZ 1 bunu
> `prescribe.py`/`kok_neden.py` için çözmüştü, ama BAŞKA bir kod yolunda
> (agentic multi-step plan'ın `ANLAT` fiili) AYNI hastalığın farklı bir
> vukuu hâlâ yaşıyordu. **İKİ bağımsız kök neden bulundu — "kök çözüm
> tekil değil" uyarısının yeni bir örneği.**

### 6.1 · KÖK NEDEN #1 — `plan_tuketici._anlat()` HESAPLA/BAGLA çıktısını yutuyordu ✅ KAPANDI
- [x] **Sorun (canlı curl ile "ram 3 neden dusuk" yeniden üretilerek
  bulundu):** 7 adımlık plan (`SORGU→BAGLA→HESAPLA→SUZ→KIR→SORGU→ANLAT`)
  koştuğunda `HESAPLA` adımı akran kıyasını ZATEN hesaplıyordu
  (`{akran_ortalamasi:57.62, fark_yuzde:-11.0, ...}`) ve bu ZENGİN
  cümle ("Akran ortalaması 57,62 (7 akran) — aradaki fark %11,0 düşük")
  `_bulgu_metni()` üzerinden teknik `note`'a ZATEN giriyordu — ama
  kullanıcıya asıl giden `interpretation.summary` yalnız
  `"RAM-3 51,30."` diyordu. Kök: `_anlat()`'ın `kaynaklar` işleme
  döngüsü yalnız `isinstance(_c, list)` (satır üreten adımlar) görüyordu;
  `HESAPLA`'nın `dict` çıktısı ve `BAGLA`'nın `tuple` çıktısı SESSİZCE
  atlanıyordu. Aynı bulgu iki yerde iki farklı zenginlikte yaşıyordu —
  `KAT-1` ihlali.
- [x] **Kök çözüm:** `app/ilkeller.py`'ye `hesapla_cumle(c)` eklendi —
  `HESAPLA` çıktısını cümleye çeviren TEK paylaşılan fonksiyon (payda
  sıfırsa/`fark_yuzde=None` ise `None` döner, "%0,0" UYDURMAZ).
  `plan_tuketici._anlat()` artık `kaynaklar`'daki `dict` (`HESAPLA`) ve
  `tuple` (`BAGLA`, ölçü adı UYDURULMADAN yalnız *"X seçildi"*) öğelerini
  de cümleye katıyor; `narration_guard.dogrula(..., ek_degerler=...)`
  ile HESAPLA'nın kendi sayılarını (imzalı VE `abs()` biçimiyle — cümle
  `abs()` basıyor, guard işaretsiz sayıyı işaretliyle karıştırmasın diye)
  besliyor.
- [x] **Doğrulama (hedefli pytest):** `test_ANLAT_HESAPLA_CIKTISINI_YUTMAZ`,
  `test_ANLAT_BAGLA_CIKTISINI_UYDURMADAN_ANLATIR`,
  `test_HESAPLA_CUMLE_PAYDA_SIFIRSA_UYDURMAZ` (yeni, `test_plan_tuketici.py`)
  + 26/26 dosyada + 199/199 geniş regresyon (`plan_tuketici`/`gorsel_
  ayristir`/`ilkeller`/`orkestrator`/`anlatim_dogrulayici`/`interpret`/
  `kok_tavsiye`/`t7_tavsiye`/`plan_kosucu`) + 455/455 `tests/` genelinde
  anahtar-kelime taraması — **0 regresyon**. Bir kendi-ölçülen regresyon
  (`test_GOVDE_SEMANIN_YASAKLADIGI_ALANI_OKUMUYOR` kırmızı verdi — kapı
  yorum METNİNİ de tarıyor, `a.get("olcu")` yazan bir YORUM CÜMLESİ
  "gövde yasak alan okuyor" sandı) canlıya gitmeden yakalanıp düzeltildi
  (yorum yeniden yazıldı, kod DEĞİŞMEDİ).

### 6.2 · KÖK NEDEN #2 — `_capaya_deger()` tireli katalog adlarını boşluklu yazımla eşleştiremiyordu ✅ KAPANDI (daha derin, daha yaygın kök)
- [x] **Sorun (6.1'in düzeltmesi TEK BAŞINA yetmedi — canlı yeniden
  test edilirken bulundu):** `s63`'e (6.1'in düzeltmesini taşıyan imaj)
  geçilip AYNI senaryo tekrarlanınca `interpretation.summary` HÂLÂ
  yalnız `"RAM-3 51,30."` idi. Kök koddan izlendi: **doğru
  `cube_query`'yi echo ederek** (gerçek frontend'in yaptığı gibi —
  önceki curl denemesi bunu ATLAMIŞTI, yanlış teşhise yol açıyordu)
  yeniden denendiğinde `followup.sinifla("ram 3 neden dusuk", ...)`
  `sinif=yeni, kural=kalip-yok` döndü — yani `neden` deseni EŞLEŞTİ
  ama tur `SINIF_KONUSMA`'ya hiç DÖNÜŞMEDİ, `_anlat`/`kok_neden`/
  `contribution`'a HİÇ ULAŞMADAN sıradan yeni bir sorgu gibi çözüldü
  (`source=cube+llm`, `narration_kaynak=sablon`). Gerçek kök:
  `_capaya_deger(q, capa_degerleri)` — "sorunun ekrandaki bir satırı
  ANDIĞI" kontrolü — katalogdaki `RAM-3` (`_norm()` sonrası `ram-3`,
  TİRE korunuyor) ile kullanıcının DOĞAL yazımı `ram 3` (BOŞLUKLU)
  arasında düz bir alt-dizge testi (`d in q`) yapıyordu — `"ram-3" in
  "ram 3 neden dusuk"` → **False**. `_norm()` (ASCII-katlama) tire/
  boşluk ayrımını hiç birleştirmiyor (o onun işi değil — yapısal bir
  işaret). Sonuç: takip **YANLIŞ SINIFLANDI**, `kok_neden`/`contribution`
  hiç tetiklenmedi — 6.1'in düzeltmesi doğruydu ama HİÇBİR ZAMAN
  ÇAĞRILMADI. ⚠ Demo kataloğunda `makine` boyutunun ÇOĞU değeri tireli
  (`RAM-1/2/3`, `ŞARDON-1`, `FERRARO SANFOR-1`) — bu TİKEL bir vaka
  değil, YAYGIN bir kalıp.
- [x] **Kök çözüm (dar kapsamlı, paylaşılan `_norm()`'a DOKUNULMADI):**
  `_capaya_deger()` artık karşılaştırmadan ÖNCE hem katalog değerini hem
  soruyu `-`→` ` dönüştürüyor (`"ram-3"` ve `"ram 3"` şimdi eşleşiyor).
  `_norm()` GENİŞLETİLMEDİ — o küp/ölçü/boyut eşleştirmesinde paylaşılan
  TEK normalize edici ve tire orada YAPISAL anlam taşıyabilir; bu
  fonksiyonun işi FARKLI ve DAR — *"bu değer cümlede geçiyor mu"*
  gevşek bir metin-içinde-geçme testidir, tire/boşluk eşdeğerliği
  yalnız BURADA uygulanır.
- [x] **Doğrulama (hedefli pytest):** `test_TIRELI_KATALOG_ADI_BOSLUKLA_
  DA_TAKIPTIR` (yeni, `test_capa_degerleri.py`, iki varyant — boşluklu
  VE tireli, tireli-orijinal zıt-ölçüt olarak) → 10/10. Geniş regresyon:
  `test_capa_degerleri.py`/`test_konusma_baglamsiz.py`/`test_konusma_
  ifadeleri.py`/`test_kok1_niyet.py`(2270-sorulu `FAZ2_ESDEGERLIK` dahil,
  42/42)/`test_kirilim_suphesi.py`/`test_anlat_turu.py`/`test_tur_
  paylas.py`/`test_takip_ucuncu_sinif.py`/`test_sosyal_niyet_onceligi.py`/
  `test_beyanlar_curumesin.py`/`test_fiil_cekimi.py` → **277/277** (4
  `test_modul_buyume.py` kırmızısı AYRI, bkz. 6.4) + 455/455 geniş
  anahtar-kelime taraması — **0 yeni regresyon**.
- [x] **Canlı doğrulama (curl, `s64` `--no-cache`, 6.1+6.2 birlikte)
  TAMAMLANDI — gerçek frontend'in yaptığı gibi `cube_query` echo
  edilerek** (ilk deneme bunu atlamıştı, yanlış teşhise götürmüştü —
  düzeltildi). *"makine bazında oee"* → *"ram 3 neden dusuk"*, **4/4
  ayrı çalıştırma**, HER SEFERİNDE `_cevap_ustunde_konus` →
  `contribution._akran_kiyasi` (`kind:"akran"`) tetiklendi ve şu
  ZENGİN metni üretti: *"RAM-3, öteki 10 makine ortalamasından %10,4
  düşük (51,78 ↔ akran ort. 57,81). Farkı en çok açıklayanlar — aynı
  kırılımda, akran ortalamasına göre: • fire: 116.825 kg — akran
  ortalaması 73.750 kg (%58,4 fazla, kötü yönde) • performans: 72,70 %
  — akran ortalaması 80,54 % (%9,7 az, kötü yönde) • plansız duruş:
  49.224 dk — akran ortalaması 46.361 dk (%6,2 fazla, kötü yönde)"* —
  `trace: "Takip: üçüncü sınıf → cevap üstünde konuşma (neden, LLM'siz)"`.
  **Bu, 6.1'in `_anlat()` düzeltmesinden BAĞIMSIZ, DAHA ZENGİN bir
  yol** — `_capaya_deger()`'in DOĞRU sınıflandırması, ZATEN var olan
  `contribution._akran_kiyasi()` (kök-neden bileşen kırılımıyla)
  mekanizmasını AÇTI; kullanıcının asıl sorununu ÇÖZEN madde budur.
  **Genelleme testi** (2-3 farklı domain/ölçü): *"tedarikçi bazında
  fire oranı"* → *"selçuk tekstil neden yüksek"* → `kok_neden.py`
  formül-ayrıştırma yoluyla (FAZ 1'in kendi "Nasıl buldum" deseni) AYNI
  kalitede zengin bir cevap ürettti (bileşen kırılımı + hat-düzeyinde
  ikinci basamak ayrıştırma). ⚠ **İKİ YENİ, DAR KAPSAMLI, BU TURUN
  DIŞINDA bırakılan bulgu** (kod DEĞİŞTİRİLMEDİ, kayda geçirildi):
  (a) *"2. vardiya neden düşük"* — katalog değeri `"2. Vardiya
  (16-24)"` (saat aralığı EKİ var) kullanıcının kısaltmasıyla
  (`"2. vardiya"`, ek YOK) hâlâ eşleşmiyor — 6.2'nin tire/boşluk
  düzeltmesi bunu KAPSAMAZ (farklı bir eşleşme sınıfı: eksik bir SON
  EK, ayırıcı karakter değil); sistem bunun yerine sessizce "en kötüsü"
  BAĞLAMINA düşüyor (`odak.deger:"3. Vardiya (00-08)"`, kullanıcının
  adlandırdığı DEĞİL). (b) *kok_neden.py* yolunda ("selçuk tekstil"
  örneği) ANLAMLI bir analiz üretilmesine RAĞMEN cümlenin sonuna
  kafa-karıştırıcı bir uyarı ekleniyor: *"⚠ Bu soruyu kataloğumdaki
  hiçbir ölçü, boyut ya da döneme bağlayamadım — aşağıdaki rapor bir
  varsayımdır."* — kendi kendiyle çelişen bir mesaj (bağladı ama
  "bağlayamadım" diyor). İkisi de AYRI, dar kapsamlı takip maddeleri;
  bu turun kapsamı SADECE kullanıcının BİREBİR bildirdiği "ram 3"
  senaryosuydu.
- [x] **Canlı doğrulama (Playwright, `s64`) TAMAMLANDI.** Tarayıcıda
  birebir kullanıcının kendi cümlesiyle: *"makine bazında oee"* →
  *"ram 3 neden düşük"* → ekranda yukarıdaki TAM metin GERÇEKTEN
  render edildi, `**kalın**` işaretleri düzgün BOLD (bkz. 6.6).

### 6.3 · UI — grafik/tablo HER ZAMAN cevap cümlesinden ÖNCE geliyordu ✅ KAPANDI (Senaryo 3'ün — önceden "fix bekliyor" — kapanışı)
- [x] **Sorun:** `PLAYWRIGHT-CANLI-TEST-TURU-2.md`'nin Senaryo 3'ü
  ("metin_grafik_sirasi") daha önce KÖK NEDEN'i doğru teşhis etmiş ama
  "tasarım kararı ister" diye AÇIK bırakmıştı. Bu turda koddan
  doğrulandı: `ReportCard.tsx`'te `<ResultView>` (grafik/tablo)
  **KOŞULSUZ** olarak `<OutputInsight>` (asıl cevap cümlesi + LLM
  anlatımı)'dan ÖNCE render ediliyordu — kullanıcı "neden" gibi AÇIKÇA
  bir açıklama isteseydi bile.
- [x] **Kök çözüm (kırılgan bir sınıflandırıcı İCAT EDİLMEDİ):**
  `OutputInsight` + AI-içerik-işaretleme rozeti, tazelik/bayat-veri
  GÜVENLİK uyarısından SONRA ama `ResultView`'DEN ÖNCE render edilecek
  şekilde taşındı — **koşulsuz**, evrensel "önce özet sonra kanıt"
  sırası (standart pano deseni). §9'un uyardığı "yeni kırılgan
  sınıflandırıcı" riski böylece alınmadı. Tazelik uyarısının sırası
  BİLİNÇLİ korundu: güvenilirliği sorgulanan bir veri üstüne özgüvenli
  bir yorum cümlesi binmesin.
- [x] **Doğrulama:** `tsc --noEmit` temiz. `test_frontend_buyume.py`:
  `ReportCard.tsx` tavanı 1082→1083 (JSX çok-satırlı `{/* */}` yorumunun
  açılış/kapanış parantezini 2 "kod satırı" sayma tuhaflığından — bu
  dosya için `MUAFIYET` DEĞİL, ölçülen değere doğrudan tavan güncellemesi,
  FAZ 2.1'in KENDİ emsaliyle aynı desen). 2 ilgisiz pre-existing hata
  (`lib/api-client.ts`/`lib/chart.ts`) DOKUNULMADI, git'te temiz.
- [x] **Canlı doğrulama (Playwright, `s64`) TAMAMLANDI.** *"makine
  bazında oee"* → *"ram 3 neden düşük"* — kartın gerçek DOM sırası
  ölçüldü: `note`/`soz` kutusu (değişmedi, zaten en üsteydi) →
  "paylaşılabilir link" → "bilinmiyor · 6 adım ölçülmüş" (katlanır) →
  YORUM kırılım çubuğu → **`OutputInsight`** ("🔍 En yüksek makine:
  ÖRGÜ HAT... En düşük: RAM-3...") → **ANCAK BUNDAN SONRA grafik** →
  `ContributionLayer` detay paneli → "+ SQL GÖSTER". `OutputInsight`
  artık grafikten ÖNCE — ekran kanıtı doğruladı.

### 6.6 · YAN KEŞİF — `ContributionLayer.tsx` `contribution.note`'u HİÇ markdown işlemeden basıyordu ✅ KAPANDI (6.2'nin AÇTIĞI, önceden hiç görünmeyen bir kusur)
- [x] **Sorun:** 6.2'nin canlı Playwright doğrulaması sırasında
  görüldü: `ContributionLayer.tsx:410-411`'deki `{d?.note && (<p
  ...>{d.note}</p>)}` `contribution.note`'u HAM yazdırıyordu —
  `**RAM-3**` gibi işaretler kullanıcıya HARFİYEN görünüyordu.
  `ReportCard.tsx`'in KENDİ `note`/`soz` kutusu (`DA-8`, aynı kusurun
  İLK vukuu) çoktan `vurgula()`'dan geçiyordu — bu panel hiç
  taşınmamıştı. ⚠ Bu kusur önceden GÖRÜNMÜYORDU çünkü `kind:"akran"` +
  dolu `note` kombinasyonu, `_capaya_deger()`'in yanlış sınıflandırması
  yüzünden bu tür konuşmalı takiplerde HİÇ tetiklenmiyordu — 6.2'nin
  düzeltmesi bu paneli ilk kez erişilebilir kıldı ve kusuru GÖRÜNÜR
  yaptı.
- [x] **Kök çözüm (`KAT-1`, ikinci bir yorumlayıcı YAZILMADI):**
  `ContributionLayer.tsx`'e `import { vurgula } from "@/lib/vurgu"`
  eklendi, `{d.note}` → `{vurgula(d.note)}` + `whitespace-pre-line`
  (metin `\n\n` taşıyor, `ReportCard`'ın note kutusuyla AYNI davranış).
- [x] **Doğrulama:** `tsc --noEmit` temiz. `ContributionLayer.tsx`
  büyüme-tavanı kapısında İZLENMİYOR (`TAVANLAR`'da yok) — etkilenmedi.
  Canlı Playwright: aynı metin artık **gerçek kalın** yazıyla render
  ediliyor (`**RAM-3**` → **RAM-3**), önce/sonra ekran görüntüsüyle
  karşılaştırıldı.

### 6.7 · KÖK NEDEN — kullanıcının "chat mantığı" kararı: basit sorular LLM anlatısını HİÇ görmüyordu ✅ KAPANDI (6.1-6.3/6.6'dan DAHA GENEL bir kök)
- [x] **Sorun (kullanıcı 6.1-6.3/6.6'yı YETERSİZ buldu, AYNI şikâyeti
  DAHA GENEL bir ürün kararıyla tekrarladı):** *"hâlâ cevaplar yazı
  merkezli değil... chat mantığına TAMAMEN geçmeliyiz, asıl olan yazı/
  açıklama olmalı grafikle DESTEKLENMELİ."* Koddan doğrulandı:
  `app/answer.py::_anlati_ekle()` — SIRADAN, İLK-TUR, "basit" (tek
  ölçü, ≤4 olgu — highest/lowest gibi) sorularda LLM anlatı adımını
  TAMAMEN ATLIYORDU (`if _anlatici.basit_mi(yorum): ... [erken çıkış]`).
  Yani `t2_anlatici` bayrağı AÇIK olmasına RAĞMEN, kullanıcı "makine
  bazında oee" gibi en sıradan soruyu sorduğunda bile yalnız telgraf-
  cümlesi ("En yüksek X, en düşük Y") + grafik görüyordu — bu, "neden"
  sorularına ÖZEL bir kusur DEĞİLDİ (6.1-6.3/6.6 yalnız "neden" takip
  sorularını düzeltmişti), TÜM basit sorulara GENEL bir kusurdu.
- [x] **Kök çözüm (`app/answer.py::_anlati_ekle`):** şablon dalındaki
  erken çıkış KALDIRILDI — artık basit sorularda bile ŞABLON metni bir
  TABAN olarak yazılıyor AMA LLM anlatısı da AYRICA deneniyor
  (kullanıcının kararı: üslup artık bir masraf değil ÜRÜNÜN kendisi).
  **Güvenli**, çünkü `app/butce.py`'nin ZATEN var olan 8 saniyelik sert
  bütçe/zaman-aşımı mekanizması (bir `§33` kusuru geçmişte bulunup
  DÜZELTİLMİŞ, kod incelenerek doğrulandı) LLM çağrısını sarıyor —
  aşılırsa cevap BEKLEMEDEN şablona düşüyor, kullanıcı asla boş ekran
  görmüyor, en kötü durum bugünküyle AYNI.
- [x] **Doğrulama (hedefli pytest):**
  `test_t2_sablon.py::test_SABLON_ARTIK_LLMi_ENGELLEMIYOR_chat_oncelikli`
  (eski `test_ASIL_KAZANC_YAPILMAYAN_CAGRI`'nin TERSİNİ doğruluyor,
  eski hâlin ÖLÇÜM tablosu tarihsel kayıt olarak KORUNDU) — İKİ kendi-
  ölçülen yanlış-pozitif (yorum METNİNDE literal `return`/`a.get(...)`
  geçtiği için testin kendi kaynak-taraması yanlış eşleşti — `test_
  GOVDE_SEMANIN_YASAKLADIGI_ALANI_OKUMUYOR`'un AYNI kusur sınıfının
  üçüncü vukuu) canlıya gitmeden yakalanıp düzeltildi. 47/47
  (`test_t2_sablon.py`+`test_d1_anlatici_kapsami.py`+`test_t2_anlatici.py`,
  `test_VARSAYILAN_KAPALI_ask_zincirinde_narration_YOK` dahil — `KURAL
  B` korundu) + 197/197 (`tests/` genelinde anlatici/anlati/interpret/
  t2_/narration/ask_enrichment/t7_tavsiye/kok_tavsiye taraması) —
  **0 regresyon**.
- [x] **Canlı doğrulama (curl, `s65` `--no-cache`) TAMAMLANDI — DÜRÜST
  gecikme ölçümüyle.** 3 sıradan, "neden" İÇERMEYEN ilk-tur soru
  denendi:
  | soru | süre | narration_kaynak | sonuç |
  |---|---|---|---|
  | *"makine bazında oee"* | **10,1 sn** | `llm` | *"Makine bazında OEE değerlendirmesinde en yüksek performans ÖRGÜ HAT'a ait olup %64,11 seviyesindedir. En düşük OEE ise %51,78 ile RAM-3'da..."* |
  | *"bu yıl toplam ciro"* | **3,7 sn** | `llm` | *"Bu yıl toplam ciro ₺74.022.836,94 olarak gerçekleşmiştir. Bu tutar, dönemin tamamını kapsayan doğrulanmış bir veridir."* |
  | *"vardiya bazında oee"* | 20,8 sn | `sablon` (LLM zaman aşımına uğradı) | Şablon metne GÜVENLE düştü — BOŞ EKRAN yok, yalnız süs eksik |
  ⚠ **Bu bir gerçek, kabul edilen ödündür — gizlenmiyor:** basit
  sorular artık **3,7-20+ saniye** sürebiliyor (öncesi: anında). 3'te
  2'si gerçek LLM anlatısı aldı, 3'te 1'i güvenle şablona düştü — hiçbir
  senaryoda kullanıcı boş/bozuk bir ekran görmedi.
- [x] **Canlı doğrulama (Playwright, `s65`) TAMAMLANDI.** *"makine
  bazında oee"* (yeni konu, sıfırdan) → ekranda GERÇEKTEN göründü: özet
  kutusunun (`🔍 En yüksek makine...`) HEMEN ALTINDA, grafikten ÖNCE,
  kesikli çerçeveli **"✎ ANLATIM"** kutusu — *"Makine bazında OEE
  incelendiğinde, en yüksek performans %64,11 ile ÖRGÜ HAT makinesinde
  görülürken, en düşük değer %51,78 ile RAM-3 makinesinde
  kaydedilmiştir. Bu kapsamda 11 kalem üzerinden değerlendirme
  yapılmıştır."* — ve altında AI-içerik işareti ("açıklama metni yapay
  zekâ ürünü — sayılar küpten gelir"). Kullanıcının istediği "chat
  mantığı" artık EN SIRADAN sorularda bile çalışıyor.

### 6.4 · YAN BULGU — `test_modul_buyume.py` ÖNCEDEN kırmızıymış, bu turda keşfedildi 🟡 açık, kasıtlı ertelendi
- [ ] **Bulgu:** `ask()` gövdesi (1471 satır, tavan 1449) ve
  `cube_router.py` (1973 satır, tavan 1964) bu turdan ÖNCE, muhtemelen
  önceki fazların (FAZ 2.1'in `suggestions` bağlama satırları, FAZ 4.2'nin
  `_dislama_istendi_mi` eklenmesi) sırasında büyümüş, ölçülmüş ve
  belgelenmiş — ama bu SPESİFİK büyüme-tavanı kapısı (`test_modul_
  buyume.py`, `MUAFIYET_ASK_KOD`/`TAVAN_CUBE_ROUTER_KOD` — `test_frontend_
  buyume.py`'nin backend eşdeğeri) hiçbir FAZ kapanışında ÇALIŞTIRILMAMIŞ.
  Bu turun kendi değişiklikleri (`followup.py`/`ilkeller.py`/
  `plan_tuketici.py`) bu iki dosyaya HİÇ dokunmadı — kırmızı bu turdan
  ÖNCE de vardı, yalnız şimdi GÖRÜLDÜ.
- [ ] **Neden bu turda düzeltilmedi:** bu kapının `MUAFIYET` biçimi
  `(sha, Δ, gerekçe)` — gerçek bir git commit SHA'sına anlanıyor. Bu
  operasyon boyunca **hiçbir commit atılmadı** (kullanıcı hâlâ istemedi),
  yani doğru bir SHA yazılamaz; hangi FAZ'ın kaç satır eklediğini şimdi
  geriye dönük ayırmak (commit tarihi olmadan) güvenilir değil. Yanlış
  bir SHA/Δ yazmak, bu kapının kendi disiplinini (*"kimse listeye
  bakmadan tavanı büyütemez"*) ihlal ederdi.
- [ ] **Doğrula (sonraki tur, ilk commit sonrası):** commit atıldığında
  gerçek SHA'larla `MUAFIYET_ASK_KOD`/`TAVAN_CUBE_ROUTER_KOD`'a
  doğru girdiler eklenmeli — ya da mümkünse büyüyen kod bir modüle
  çıkarılıp tavan aşılmadan kapatılmalı.

### 6.5 · Bilerek ERTELENEN — ANLAT'a guarded-LLM eklenmesi
- [ ] **Soru:** 6.1'in düzeltmesi `interpretation.summary`'yi
  DETERMİNİSTİK olarak zenginleştirdi (gerçek, doğru bir cümle) ama
  FAZ 1'in `prescribe.py`/`kok_neden.py`'ye eklediği GUARDED-LLM
  "üslup" katmanını (`✎ ANLATIM` kutusu) `plan_tuketici`'nin `ANLAT`
  fiiline HİÇ EKLEMEDİ — `_govdeler()`'in kendi belgelenmiş kararı
  ("ANLAT neden LLM'siz... modeli çağırmak bir yetenek değil bir
  masraftır") BİLEREK bozulmadı.
- [ ] **Neden ertelendi (FAZ 3.3 emsaliyle AYNI desen):** bu, maliyet
  gerekçeli, ÖNCEDEN tartışılmış bir mimari karardır — tersine
  çevirmek (her multi-step plan turuna bir LLM çağrısı eklemek) E6'nın
  cezalandırdığı ŞEYİ geri getirir ve dikkatli bir maliyet/gecikme
  analizi ister. 6.1+6.2'nin düzeltmesi kullanıcının SOMUT şikâyetini
  (paragraf yerine ham sayı) zaten KÖKTEN çözdü — deterministik ama
  DOĞRU ve ZENGİN bir cümle. LLM-üslup katmanı ayrı, isteğe bağlı bir
  GELECEK geliştirmedir, bu turun kapsamı değil.

---

## Özet tablo

| faz | madde | öncelik | durum |
|---|---|---|---|
| 0 | KÖK NEDEN B — `_konusma_baglamsiz` asimetrisi | 🔴🔴🔴 en yüksek (ucuz, engel açıcı) | [x] KAPANDI — 282/282 regresyon temiz, canlı doğrulandı |
| 1 | Katman 7 — guarded-LLM reçete + kök-neden muhakemesi | 🔴🔴🔴 ASIL KÖK ÇÖZÜM | [x] KAPANDI — 34 yeni test + 595+ regresyon temiz, canlı doğrulandı (§KN yolu tam başarı, prescribe yolu şablon-önce doğrulandı, KURAL B curl+Playwright'ta doğrulandı) |
| 2.1 | Yokluk sorgusu "sihir"i (en-yakın-yararlı-alternatif) | 🔴🔴 kullanıcı deneyimi | [x] KAPANDI — kök çözüm LLM DEĞİL deterministikti (`yokluk_ihlali`+`yokluk_chip`, `KAT-1` tek üretici, 3 dala otomatik yayılır); 13 yeni test + 221+ regresyon temiz, curl (s58→s59, bir sözdizimi kusuru canlıda yakalanıp düzeltildi) VE Playwright'ta (iki ayrı çalıştırma, önizleme+koşulmuş dal) tam doğrulandı; frontend'de İKİNCİ bir "backend bağlı, hiç tüketilmiyor" boşluğu bulunup kapatıldı (`PlanOnizleme.tsx`+`ReportCard.tsx`) |
| 2.2 | Kısmi yerine getirme — insan-okur beyan | 🔴🔴 kullanıcı deneyimi | [x] KAPANDI — kök neden LLM DEĞİL deterministikti (`KAT-1`); 10 yeni test, 244+ regresyon temiz, canlı doğrulandı (curl tam, Playwright kısmi — bkz. madde metni) |
| 3.1 | Sıfır-tabanlı yüzde — 2. kod yolu (contribution.py) | 🔴 | [x] KAPANDI — ÜÇ bağımsız kusur: (a) `contribution.py::contributions()` net_pay eşiği (`0.01→0.20`), (b) FAZ 2.1'in KENDİ regresyonu (`ask.py` suggestions=None → 500, TÜM agentic plan yolları kırıktı), (c) 🔴🔴🔴 `ContributionLayer.tsx::Yuzde()` ÇİFTE-YÜZDE — roadmap'in orijinal "+4740.0%" örneğinin GERÇEK kaynağı büyük ihtimalle buydu. Curl+Playwright'ta ikisi de doğrulandı |
| 3.2 | KÖK NEDEN A genelleştirme | 🟡 | [x] KAPANDI — kapı 9 sözlüğe genişledi, 3 YENİ gerçek çakışma bulundu (`beklenen`→`_NORMAL`, `zirve`/`tepe`→`_ISARET`), 2 YAML'de düzeltildi, hedefli testler yeşil |
| 3.3 | K9 "analiz et" boşluğu — yeniden değerlendirme | 🟡 (FAZ 1'e bağımlı) | [~] araştırma bitti — canlı ölçüldü KAPANMADI (`_akran_kiyasi` ≠ `kok_neden.ayristir`, yapısal fark); düzeltme AYRI tur ister, körlemesine bağlanmadı |
| 3.4 | KÖK NEDEN A'nın 3. örneği — çıplak "bu" temporal karışması | 🔴 YENİ (FAZ 0.1'de bulundu) | [x] KAPANDI — `_bu_su_zamir_mi()` (ek-toleranslı + temporal-farkında), kendi ölçülen bir regresyon canlıya gitmeden yakalanıp düzeltildi, 315+ test yeşil, curl+Playwright'ta (`s61`) tam doğrulandı |
| 3.5 | `bilesenler()` `ort_oee`'yi artık ayrıştırmıyor | 🔴 YENİ (FAZ 1.5'te bulundu) | [ ] |
| 3.6 | Demo veri tazeleme — temel tablolar 2026-06-22/06-30'da bitiyor | 🔴 YENİ (FAZ 2.1'de bulundu — kod değil, veri) | [ ] |
| 4.1 | Guarded-LLM muhakeme metni görsel dili | 🟡 | [x] KAPANDI — ölçüm roadmap'in varsaydığından ciddi çıktı: HİÇ render edilmiyordu (FAZ 2.1/2.2'nin İKİZİ), `Makbuz.tsx`'in probabilistik diliyle eklendi, curl+Playwright'ta (geçici DB flag override ile, `s61` VE `s62`'de tekrar) doğrulandı, `KURAL B` iki kez teyitli |
| 4.2 | K3 refresh_grace_seconds (araştırıldı, dokunulmadı) + Senaryo 14 "hayır" sahte dışlama | 🟡 | [x] K3 → [~] bilerek açık (güvenlik kodu, ayrı tur ister); Senaryo-14 → [x] KAPANDI — `cube_router._dislama_istendi_mi()`, `KAT-1` tek çağrı yeri, 4 yeni test + 225 regresyon temiz, `s62`'de (build GERÇEKTEN bitince) 3× curl + Playwright'ta (motor+UI) tam doğrulandı |
| 5 | Toplu Playwright + tek kapı | — | [x] Playwright nokta-atış tamam; gate 1× koşuldu (korpus ✅, gerçek-dünya popülasyon-kaymalı ⚠) — FAZ 6 sonrası TEK gate daha gerekiyor |
| 6.1 | ANLAT, HESAPLA/BAGLA çıktısını yutuyordu | 🔴🔴🔴 kullanıcı canlı bulgusu | [x] KAPANDI — `ilkeller.hesapla_cumle()`, `_anlat()` dict/tuple kaynak işliyor, 26+199+455 test yeşil, canlı curl+Playwright doğrulandı |
| 6.2 | `_capaya_deger()` tire/boşluk eşleşmiyordu | 🔴🔴🔴 6.1'i devre dışı bırakan DAHA DERİN kök — ASIL çözüm | [x] KAPANDI — tire↔boşluk yalnız bu dar fonksiyonda eşdeğer, `_norm()` dokunulmadı, 277+455 test yeşil, 4/4 canlı curl + Playwright + 2. domainde genelleme doğrulandı |
| 6.3 | UI: grafik her zaman cevap cümlesinden önce | 🔴🔴 kullanıcı deneyimi (Senaryo 3'ün kapanışı) | [x] KAPANDI — `OutputInsight` tazelik-uyarısından sonra, `ResultView`'den önce, koşulsuz taşındı, Playwright DOM sırasıyla doğrulandı |
| 6.4 | `test_modul_buyume.py` önceden kırmızıymış | 🟡 keşfedildi, bu turun kapsamı DEĞİL | [ ] commit sonrası gerçek SHA'larla `MUAFIYET` girilecek |
| 6.5 | ANLAT'a guarded-LLM eklenmesi | 🟡 maliyetli, ayrı tur ister | [ ] bilerek ERTELENDİ (FAZ 3.3 emsali) |
| 6.6 | `ContributionLayer.tsx` markdown işlemiyordu | 🔴🔴 6.2'nin açtığı, önceden görünmeyen kusur | [x] KAPANDI — `vurgula()` bağlandı (`DA-8`'in ikinci vukuu), Playwright önce/sonra doğrulandı |
| 6.7 | Basit sorularda LLM anlatısı hiç denenmiyordu | 🔴🔴🔴 kullanıcının "chat mantığı" kararı — 6.1-6.3/6.6'dan DAHA GENEL kök | [x] KAPANDI — `answer.py::_anlati_ekle` erken çıkışı kaldırıldı, 8sn bütçe güvenli taban; 47+197 test yeşil; canlı curl (2/3 gerçek LLM, 1/3 güvenli şablon, 3,7-20,8sn — DÜRÜST rapor edildi) + Playwright ("✎ ANLATIM" kutusu en sıradan soruda bile görünüyor) doğrulandı |
