# Playwright Canlı Test Turu 2 — Kök Neden Devamı

> Bu belge **ayrı** tutuluyor — `2026-08-26_PLAYWRIGHT-CANLI-TEST-KAMPANYASI.md`
> (tur 1, K1-K13) ve `2026-08-26_PLAYWRIGHT-BULGULARI-YOL-HARITASI.md` (tur 1'in
> düzeltme kaydı) değişmeden kalıyor. Bu belge **tur 2**: kullanıcının tur 1'in
> bazı kapanışlarını sorgulaması üzerine açıldı — özellikle K9 ve K7'nin "kapandı"
> denilen hâlleri canlıda **yeniden** kırıldı, gösteriyor ki geçen turun bazı
> "gözlem altında, tekrar üretilemedi" kararları **erken** verilmişti.

**Yöntem:** her senaryo TEK TEK, script/otomasyon DEĞİL, gerçek Playwright/
Chromium ile elle sürülüyor; her bulgu **önce** koddan/curl'den kök nedene
indiriliyor, **sonra** (kök neden netse) düzeltiliyor, **sonra** canlı yeniden
doğrulanıyor. Ölçüt: **tekrarsız, özgün, gerçek-insan senaryoları** — sistemi
zorlayan, önceki turun kelimesi kelimesine tekrarı olmayan sorular.

**Kurulum:** backend `dima-oneri-8002` (imaj `s51`), frontend `pnpm dev`
(`:3000`), hesap `demo-boyahane@usedima.com`.

---

## Önceki turun denetimi (kullanıcı talebiyle)

Kullanıcı, FAZ 2'den itibaren yol haritasının context-compact sonrası yanlış
uygulanmış olabileceğini işaret etti. İki kaynak belge tam okunup satır satır
karşılaştırıldı:

- **K4, K5, K13, K12, K2, K10, K6, K3, K8**: kampanya metniyle (Ç3-Ç13)
  birebir örtüşüyor, gerçek koddan kanıtlanmış, canlı doğrulanmış. **Sorun
  bulunamadı.**
- **K7**: yol haritası "⊘ gözlem altında, tekrar üretilemedi" diyordu. **Bu
  YANLIŞTI** — bkz. Senaryo 1 altta, bu turda gerçek kök neden bulundu ve
  düzeltildi. Önceki turda yalnız 2 dar senaryo denenmişti (az rozetli
  kartlar); rozetin ÇOK olduğu bir kart hiç test edilmemişti.
- **K9**: "neden↔ne yapmalıyız" yarısı doğru kapatılmıştı. Ama kampanyanın
  ASIL S15 bulgusunun 1. maddesi ("analiz et" boş) **açıkça açık bırakılmıştı**
  — ve bu turda gösterdi ki o açık bırakılan boşluk, kullanıcının doğal
  kullanım deseninde (analiz-et turu olmadan doğrudan "neden" sormak) çok
  daha ciddi bir arızaya (sessiz niyet kaybı) büyüyor. Bkz. Senaryo 2.

---

## Senaryo sonuçları

| # | senaryo | ne test edildi | motor/veri | UI/UX | durum |
|---|---|---|---|---|---|
| 1 | **kalabalık_rozet_karti** | "bu yıl oee" (tek satır KPI, çok rozet) | — | 🔴 kullanıcı mesajı "kelime kelime dikey" (K7'nin ta kendisi) | ✅ KÖK NEDEN BULUNDU + DÜZELTİLDİ |
| 2 | **dogrudan_neden_zinciri** | "makine bazında oee" → "ram 3 neden böyle" | 🔴🔴 ÜÇ ayrı kök neden (altta) | 🔴 hiç analiz yok, sessiz | ✅ 1/3 DÜZELTİLDİ, 2/3 TEŞHİS EDİLDİ (fix bekliyor) |
| 3 | **metin_grafik_sirasi** | "neden"/"analiz et" sonrası ekran sırası | — | 🔴 grafik HER ZAMAN üstte, yazı HER ZAMAN altta (koşulsuz) | ✅ KÖK NEDEN BULUNDU, tasarım kararı bekliyor |
| 4 | **entity_zamir_referansi** | "en çok fire veren müşteri kim" → "ona ne kadar borcumuz var" | 🔴🔴 "ona" bir ENTİTY'ye değil hiçbir yere bağlanmıyor — filtre YOK, TÜM şirketin borcu (₺359M) dönüyor, YANLIŞ kapsamlı sayı sessizce sunuluyor | ⚠ aynı yanlış sonuç görsel olarak da doğrulandı | ✅ KÖK NEDEN BULUNDU, fix bekliyor |
| 5 | **mobil_genişlik** | 414px (iPhone) genişlikte tam akış | — | ✅ **TEMİZ** — rozetler sarıyor, tek sütun, alt gezinme okunur | ✅ SORUN YOK (dengelemek için kayıtlı) |
| 6 | **yokluk_sorgusu** | "bu ay hiç sipariş vermeyen müşteriler kim" | 🔴🔴 yanlış cube (`cari` değil `siparis`/anti-join gerekir) — sistemde "hiç X yapmayan" (NOT EXISTS) sorgusu için **hiçbir birincil ifade yok**, `KIYASLA`(akran-kıyası)'na sessizce düşüyor | — | 🔴 KÖK NEDEN BULUNDU — mimari düzeyde eksik yetenek, fix bekliyor |
| 7 | **pano_ekleme_akışı** | "+ panoya ekle" → "+ yeni pano" → isim → tamam | — | ✅ **TEMİZ** — çalışıyor, `✓ panoda` durumuna geçiyor | ✅ SORUN YOK |
| 8 | **yanlış_geri_bildirim** | "✗ yanlış" → yorum yaz → gönder | — | ✅ **TEMİZ** — `✗ kaydedildi` durumuna geçiyor, VQR'a kaydediliyor | ✅ SORUN YOK |
| 9 | **bilesik_soru_delta_secim** | "geçen ay ile bu ay arasında en çok değişen makine hangisi ve muhtemel sebebi ne olabilir" | 🟡 `BAGLA` (varlık seçme fiili) iki dönemli bir MATRIS'ten DELTA'ya göre seçim yapamıyor — ama **dürüstçe beyan ediyor**, hayal kurmuyor | — | 🟡 kapasite eksik, ADR-0020 uyumlu dürüst arıza (silinmez, iyileştirilebilir) |
| 10 | **kalite_orani_basit** | "kalite oranımız kaç" | ✅ temiz | ✅ temiz | ✅ SORUN YOK |
| 11 | **devam_sorusu_chip** | "bu yıl" hızlı-dönem çipi | ✅ temiz | ✅ temiz | ✅ SORUN YOK |
| 12 | **kirilima_in_drill_zinciri** | "kırılıma in" → "makine" → çok-ölçülü tablo + "ilişkili veri" çipleri | ✅ **etkileyici** — 8+ ölçü, çapraz-cube "katkı adayı" önerileri | ✅ temiz, epistemik olarak dürüst ("nedensellik iddiası değildir") | ✅ SORUN YOK (güçlü özellik) |
| 13 | **agentic_uzun_bilesik_reddedildi** | "...göster, ... açıkla, ... bul, ... ne yapmalıyız söyle" (tek cümle, TEK tur, bağlamsız) | 🔴🔴 **TAM RET** — geçerli veri isteği "ekranda rapor yok" diye reddedildi | — | 🔴🔴 KÖK NEDEN KESİN (kod satırıyla) — en yüksek öncelik |
| 14 | **kendini_duzeltme** | "vardiya bazında oee" → "hayır vardiya değil hat bazında istemiştim" | ✅ düzeltme İŞLEDİ (doğru boyut değişti) ama 🟡 "hayır" kelimesi sahte bir "dışlama filtresi" uyarısı tetikledi | — | 🟡 küçük, yan bulgu — aynı "kelime çift görev" ailesi (Senaryo 2a) |
| 15 | **esik_filtreli_liste** | "500 kg üstü fire veren partiler" | 🔴 plan `parti_sayisi`'ni (bir ÖLÇÜ) boyut sanıp kırıldı — ama dürüstçe beyan etti | — | 🟡 ölçü/boyut karışıklığı, dürüst arıza |
| 16 | **argo_gundelik_dil** | "napıyoz bu ay nbr yapmışız kardeşim bi ciroya bak" | ✅ **çok sağlam** — ağır argoya rağmen doğru cube+ölçü | — | ✅ SORUN YOK (güçlü dayanıklılık) |
| 17 | **hat_fire_zincir + karmasik_takip** | "...fire oranlarına bakar mısın, en yüksek fireli hattı bul" → "...performansını göster, ... sorumlu tespit et, geçen yıl kıyasla, ... bakım geçmişini kontrol et" | ✅ ilk tur temiz (BAGLA tek-dönem seçimi ÇALIŞIYOR); 2. tur 🔴 4 istekten yalnız 1'i (kıyas) uygulandı, kalan 3'ü (performans, sorumlu-tespit, bakım-geçmişi) **belirsiz bir "EKSİK" etiketiyle** sessizce düştü | — | 🔴 kısmi yerine getirme + belirsiz beyan |
| 18 | **jargon_Q2_donem** | "KDV dahil toplam faturalı satış Q2de ne oldu" | 🟡 "Q2" dönem ifadesi çözülemedi (son 12 aya düştü) — küçük, kabul edilebilir bir sınır | — | 🟡 düşük öncelik |
| 19 | **acil_ton_ozet** | "ACİL yarın toplantı var hemen lazım geçen çeyrek performansı özetle" | ✅ aciliyet kelimeleri doğru `bilinmeyen` sayıldı, çekirdek istek anlaşıldı (9 adım, TAM bütçe 8/8 sorgu) | — | ✅ SORUN YOK (dayanıklı) — ama bütçe kullanımı not edildi |
| 20 | **final_agentic_dogrulama** | "vardiya bazında oee ve fire karşılaştır, en kötü vardiyayı bul, sebebini araştır, ve bu vardiya için somut 3 aksiyon öner" | 🔴🔴 **Senaryo 13'ün AYNI kökünün İKİNCİ, BAĞIMSIZ doğrulaması** — "3 aksiyon öner" yine TAM RET tetikledi | — | 🔴🔴 doğrulandı — sistemik, tek-seferlik değil |

**20/20 senaryo tamamlandı.** Aşağıda toplu kök-neden sentezi.

---

## Senaryo 1 — `kalabalık_rozet_karti` (K7'nin gerçek kök nedeni)

**Soru:** "bu yıl oee" (tek başına, tek satırlık KPI cevabı — ama rozet
çubuğu kalabalık: 🔔 zamanla · + panoya ekle · ✓ doğru · ✗ yanlış · ◆ CUBE ·
ANLADIĞIM(oee/OEE/2026-01-01) · ⤵ kırılıma in · ↳ yanıtla).

**Gözlem (canlı ekran):** başlık ("bu yıl oee") tek kelime tek satır halinde
dikey sıralandı — `bu` / `yıl` / `oee`, her biri kendi satırında.

**Kök neden (koddan kanıtlandı, DOM ölçümüyle doğrulandı):**
`ReportCard.tsx`'te başlık+rozet-çubuğu bir flex satırında (`items-start
justify-between gap-3`). Başlık kapsayıcısı `min-w-0 flex-1` (taban genişlik
**0%**, yalnız "büyüme"den pay alıyor); rozet çubuğu `shrink-0 flex-wrap`
(asla küçülmüyor, kendi doğal tek-satır genişliğini — ölçülen: **787px** —
her zaman talep ediyor). Rozet sayısı arttıkça satırda kalan pay eriyor;
ölçülen canlı vaka: konteyner **832px**, çubuk **787px** aldı, başlığa
**33px** kaldı — üç harften uzun HİÇBİR kelime o genişliğe sığmıyor, her
kelime kendi satırına düşüyor.

⚠ Önceki turda BU tam senaryo (çok rozetli tek-satır KPI) hiç denenmemişti
— yalnız az-rozetli 2 senaryo denendi, ikisi de temiz çıktı, "tekrar
üretilemedi" denip kapatıldı. **Ders: 2 senaryo "tekrar üretilemedi" demek
için yeterli değildi — rozet SAYISI değişkeniydi, denenmemişti.**

**Kök çözüm (uygulandı, `ReportCard.tsx`):**
1. `shrink-0` rozet çubuğundan kaldırıldı — `flex-wrap` zaten vardı ama
   `shrink-0` onun hiç devreye girmesini engelliyordu (satıra bir genişlik
   ATANMADAN `flex-wrap` sarma yapamaz).
2. Başlık kapsayıcısına gerçek bir taban genişlik verildi (`min-w-[200px]`)
   — `flex-1`'in taban değeri `0%`'di, "büyüyecek" bir taban olmayınca
   büyüme de olmuyordu.

**Doğrulama:** canlı Playwright, aynı soru — başlık artık **200px, tek
satır, normal**; rozet çubuğu artık **2 satıra sarıyor**. Ekran kanıtı:
`r2_k7_fixed.png` (scratchpad).

---

## Senaryo 2 — `dogrudan_neden_zinciri` (kullanıcının bildirdiği tam vaka)

**Sorular (gerçek insan sırası, analiz-et ATLANARAK):** "makine bazında
oee" → **"ram 3 neden böyle"** (2. tur, doğrudan — önceki turun kampanyası
hep "analiz et"i ARADA bırakıyordu, bu tur ONU atladı).

**Gözlem (canlı ekran + curl):** cevap geldi ama **hiç analiz yok** —
yalnız `%55,82 ORT_OEE / RAM-3` ve şablon bir cümle ("Bu değer OEE
ölçüsünün … kırılımıdır"). "Neden" sorusu tamamen görmezden gelinmiş gibi.

Kullanıcının AYRICA bildirdiği ikinci varyant ("ram 3 neden düşük" —
çökme/cevapsız) bu turda birebir tekrar edilemedi (muhtemelen LLM-bağımlı
bir zamanlama yarışı), ama KÖK MEKANİZMA aşağıda üçüncü maddede zaten
kanıtlandı ve o da aynı zincirin bir parçası olabilir — ayrı işaretlendi.

### 2a — Kök neden #1: ÇIPLAK "neden"/"sebep" küp-sinonimi olarak kayıtlı ✅ DÜZELTİLDİ

**Kanıt (curl, trace):** `"niyet: tür=kirilim · kırılım=kok_neden,sebep ·
bilinmeyen=boyle"` — sistem "neden" kelimesini bir SORU ZARFI değil bir
**alan adı** sandı ve `isg.kok_neden` + `kalite.sebep` boyutlarını
"kırılım" olarak eşleştirmeye çalıştı.

**Neden bu oldu:** üç ayrı cube'un `metadata.yml`'inde **çıplak** "neden"/
"sebep" kelimeleri sinonim listesinde kayıtlıydı:
- `isg.kok_neden`: `[kök neden, sebep, neden, kaza nedeni]`
- `kalite.sebep`: `[sebep, neden, hata sebebi, hata nedeni, rework sebebi, gerekçe]`
- `sikayet.konu`: `[konu, şikayet konusu, sebep, tür, şikayet türü]`

Bu iki kelime Türkçe'de birer **soru sözcüğüdür** ("neden böyle?"), bir
ürün/alan adı değil — ama sinonim listesine girince ürünün **her yerinde**
her nedensel takip sorusu bu dar alanlara yanlış eşleşiyordu.

⚠ **Bu, `followup.py`'nin AYNI kusuru zaten ÜÇ KEZ düzelttiği** bir örüntü
(`§NÇ` tarihçesi — "aylık neden düştü" gibi vakalar) — ama o düzeltmeler
yalnız `followup.py`'nin KENDİ soru-sınıflandırmasındaydı. Şemanın
BAĞIMSIZ bir eşleştirme yolu (`niyet.py::_kirilimlar` →
`cube_router._match_dims`) bu dersi hiç görmemişti — **aynı kök kusurun
ikinci, bağımsız vukuu.**

**Kök çözüm (uygulandı — TİKEL DEĞİL, YAPISAL):**
1. Üç YAML'den çıplak "neden"/"sebep" kaldırıldı (yalnız veri düzeltmesi).
2. **Asıl yapısal fark:** `wren_service.py::_etiket_belirsizligini_ayikla`'ya
   yeni bir kural eklendi — bir boyutun ETİKETİ kelimelere bölününce
   (`_label_tokens`) üretilen HER token, `followup._NEDEN` (zaten var olan,
   ölçümle büyütülmüş TEK sözlük — `KAT-1`, yeni bir liste İCAT
   EDİLMEDİ) ile karşılaştırılıyor; eşleşirse token **düşer** — pack'in
   AÇIKÇA beyan ettiği bir sinonim değilse. Yani "kök neden" etiketi
   "neden" token'ını YİNE üretecekti (`isg.kok_neden`'in kendi adı bunu
   gerektiriyor) — o üretilen token da artık otomatik elenir.
3. **Yapısal gate (kalıcı, kod-seviyesi test):**
   `tests/test_soru_sozcugu_sinonim_degil.py` — ŞEMADAKİ TÜM cube'ları
   tarar, hiçbirinin sinonim listesinde çıplak bir soru sözcüğü kalmadığını
   doğrular. **Bu bugünkü 3 cube'a özel değil** — yarın 4. bir cube aynı
   hatayı (bir LLM-destekli katalog üretim aracı ya da elle yazan biri)
   tekrarlarsa bu kapı onu **hemen** yakalar.

**Doğrulama:** `test_soru_sozcugu_sinonim_degil.py` 2/2 geçti; ilgili
regresyon paketi (followup/niyet/etiket, 12 dosya) **280/280 geçti, 0
regresyon**. Canlı curl (`s51`): "ram 3 neden böyle" artık `niyet:
tür=toplam` (kırılım hijacki YOK); "kaza nedeni bazında kaza adedi" (İSG
cube'unun MEŞRU çok-kelimeli sinonimi) hâlâ doğru çalışıyor —
`dimensions: ["kok_neden"]`. Domain-agnostik: 3 farklı cube'da (`isg`,
`kalite`, `sikayet`) aynı kalıp bulundu ve TEK kod değişikliğiyle üçü
birden kapandı.

### 2b — Kök neden #2: "yapısal öncelik" nedensel soruyu SESSİZCE düşürüyor 🔴 TEŞHİS EDİLDİ, DÜZELTME BEKLİYOR

2a düzeltildikten SONRA bile "ram 3 neden böyle" hâlâ analiz ÜRETMEDİ
(`niyet: tür=toplam`, `contribution: yok`). Kök neden koddan kanıtlandı:
`followup.py::sinifla()`'da `_YAPISAL` deseni, `TUR_NEDEN`/`§NÇ` mantığından
ÖNCE kontrol ediliyor (satır ~595-600) ve kod bunu **bilerek** yapıyor —
kendi yorumu: *"'aylık neden düştü?' hem düzenleme hem konuşma gibi
görünür; kullanıcı yeni sayılar bekliyorsa önce onları vermek gerekir."*

Bu KARAR doğru olabilir (yanlış sayı vermemek → doğru sayı + eksik açıklama,
haklı bir öncelik) AMA **sessizce** oluyor — ADR-0020'nin ("sessiz düzeltme
yok, beyan et") **doğrudan** ihlali: kullanıcı "neden" sorusunun HİÇ
işlenmediğini bilmiyor, yalnız boş bir cevap alıyor.

**Doğrulandı (canlı curl, 3. tur):** AYNI soruyu ("neden böyle") RAM-3'e
zaten filtrelenmiş context'te TEKRAR sorunca, sistem gerçekten
`"Takip: üçüncü sınıf → cevap üstünde konuşma (neden, LLM'siz)"`'e düşüyor
— yani mekanizma ÇALIŞIYOR, yalnız 1. turda yapısal öncelik onu ele
geçiriyor ve kullanıcıya bunu SÖYLEMİYOR.

**Önerilen kök çözüm (uygulanmadı — tasarım kararı ister):** `sinifla()`
`_YAPISAL` kazandığında AYNI zamanda `_NEDEN` deseni de eşleşiyorsa
(`kanit`'e ek bir alan/işaret), `ask.py`'de bu turun `not_metni`'ne
BEYAN eklensin: *"Bu turda önce filtrelenmiş sayıyı verdim; nedenini
öğrenmek için 'neden' diye tekrar sorabilirsin."* — mevcut mimariyi
BOZMADAN (yapısal öncelik kalır, doğru sayı önceliği korunur), yalnız
ADR-0020'yi burada da uygulayarak.

### 2c — Kök neden #3: "neden" ulaştığında bile YANLIŞ analiz motoru seçiliyor 🔴 TEŞHİS EDİLDİ, DAHA DERİN ARAŞTIRMA GEREKİYOR

2b'nin 3. turunda "neden" mekanizması NİHAYET tetiklendiğinde bile
sonuç yine metinsiz kaldı — ama bu sefer DÜRÜST bir gerekçeyle: *"ort_oee
toplanabilir değil (non_additive) — katkı payı matematiksel olarak
tanımsız."* Bu `contribution.py` (AYRIŞTIR/decompose motoru) — DOĞRU bir
red, çünkü ortalamaların "katkısı" gerçekten tanımsızdır.

Ama önceki turun kampanyasında AYNI şekle benzer bir soru ("bu neden
böyle?", `oee` cube'u) **ÇOK İYİ** bir cevap üretmişti: *"RAM-3 öteki 10
makine ort'dan %10,7 düşük; en çok açıklayanlar: fire +%62,3, performans
−%9,1…"* — bu bir AYRIŞTIRMA değil bir **AKRAN KIYASI** (muhtemelen
`kok_neden.py` modülü, `contribution.py` değil). Yani ürünte İKİ farklı
"neden" motoru var (decompose vs peer-comparison) ve hangisinin
seçileceği **query şekline** bağlı — bu turda `contribution.py`'ye
düşülmüş olması muhtemelen bir YÖNLENDİRME sorunu, `kok_neden.py`'nin
"non-additive ölçüde de çalışabilecek" yeteneği hiç denenmemiş olabilir.

**Durum:** kök neden TAM netleşmedi — hangi query şeklinin hangi motoru
tetiklediği ayrı bir araştırma turu ister (routing mantığı `answer.py`/
`ask.py`'de aranmalı). **Uydurma bir düzeltme yazılmadı** (disiplin: önce
kesin kök neden).

---

## Senaryo 3 — `metin_grafik_sirasi` (kullanıcının UX gözlemi — koddan doğrulandı)

**Kullanıcı gözlemi:** "yazı/açıklama kullanıcı ne istiyorsa üste o
gelmeli — grafik mi istiyor, açıklama mı?"

**Kök neden (statik kod okumasıyla kanıtlandı, canlı tekrara gerek
kalmadan — saf JSX yerleşimi, LLM'e bağlı değil):** `ReportCard.tsx`'te
render sırası **SABİT ve KOŞULSUZ**:
1. `<ResultView>` (grafik/tablo) — satır ~872
2. `item.ai_generated_prose` (yazılı anlatı) — satır ~1011, HER ZAMAN
   grafikten SONRA.

Kullanıcı "neden"/"açıkla"/"yorumla"/"analiz et" gibi AÇIKÇA bir anlatı
istese bile, grafik/tablo HER ZAMAN üstte, yazı HER ZAMAN altta basılıyor
— soru niyetine göre hiçbir koşullu sıralama yok.

**Durum:** kök neden NET ve kanıtlı, ama **düzeltme bir tasarım kararı
ister** (hangi sinyal "bu turda anlatı asıl istenendir" desin — `explain`/
`trace`'teki hangi alan bu ayrımı güvenilir taşıyor, henüz belirlenmedi).
Uydurma bir sinyal seçip acele bir düzeltme yazılmadı. **Fix bekliyor.**

---

---

## Senaryo 5 — `entity_zamir_referansi` (🔴🔴 en ciddi yeni bulgu — yanlış kapsamlı sayı, sessizce)

**Sorular:** "en çok fire veren müşteri kim" → **"ona ne kadar borcumuz var"**
(gerçek insan konuşması: "ona" = bir önceki cevapta adı geçen MÜŞTERİYE,
"bunu"/"şunu" gibi RAPORA değil).

**Gözlem (curl + canlı ekran, ikisi de aynı sonuca vardı):**
1. tur: "en çok fire veren müşteri kim" → doğru, `EGE KNIT DIŞ TİCARET
   LTD. ŞTİ.` (149.777 kg / 297.982 kg — iki ayrı koşumda hafif farklı
   dönem yorumu, önemsiz).
2. tur: "ona ne kadar borcumuz var" → **entity FİLTRESİ YOK**. Canlı
   ekranda kullanıcıya *"Hangi kırılımı istiyorsun?"* diye soruldu,
   "kırılımsız (toplam)" seçilince sonuç: **₺359.409.922,79** —
   bu şirketin **TÜM müşterilerine olan TOPLAM borcu**, "EGE KNIT"e özel
   bir sayı DEĞİL. Hiçbir uyarı, hiçbir beyan yok — kullanıcı bu sayıyı
   "EGE KNIT'e olan borcumuz" sanabilir (gerçek iş riski: yanlış bir
   rakamla üçüncü bir tarafla konuşma).

**Kök neden (curl trace'i kanıtladı):**
`"niyet: tür=toplam · ölçü=2 · bilinmeyen=ona,var"` — **"ona" `bilinmeyen`
(tanınmayan) bir jeton olarak işaretleniyor ve SESSİZCE düşüyor.** Sistemin
zaten çalışan bir "rapora işaret eden zamir" mekanizması var
(`followup._ISARET_ZAMIRI` — "bunu"/"şunu" gibi, RAPORUN kendisine işaret
eder) ve ayrıca bir "cümlede geçen VARLIK adını filtreye çevir" mekanizması
var (`niyet._varlik_filtreleri`, `§51` — "ram 3" gibi YAZILAN adları
yakalar). Ama **üçüncü bir yetenek — "önceki turun SONUCUNDA öne çıkan bir
varlığa işaret eden zamiri (ona/onun/onu) O VARLIĞA çöz" — hiç yok.**
"ona" ne rapora işaret eden bir zamir (öyle sayılmıyor, `_ISARET_ZAMIRI`
listesinde değil) ne de yazılan bir varlık adı (`ram 3` gibi harfi harfine
yazılmadı) — ikisinin ARASINDA bir boşlukta kalıyor ve **hiçbir mekanizma
sahiplenmiyor.**

**Neden bu ÖNEMLİ (tikel değil, genel):** bu üç cube'a özel değil — HER
"varlık listesi → o varlığa devam et" konuşma deseninde (müşteri, makine,
tedarikçi, personel, ürün… hangi entity olursa olsun) aynı şekilde
kırılacaktır. Kanıt zaten iki FARKLI domainde (parti/fire → cari/borç)
gözlendi tek turda — domain'e özel bir kalıp değil, **anaphora (zamir-
varlık) çözümlemesinin kendisi eksik.**

**Durum:** kök neden net, ama düzeltme (bir önceki turun SONUÇ satırından
öne-çıkan-varlığı-çıkarıp-zamire-bağlama) `niyet.py`/`context.py` katmanına
yeni, dikkatli tasarlanmış bir yetenek ister — aceleye getirilip
**uydurulmadı**. **En yüksek öncelikli açık bulgu — bir sayı YANLIŞ
kapsamla, uyarısız sunuluyor.**

---

## Senaryo 6 — `mobil_genişlik` (dengeleme kaydı — sorun YOK)

**Test:** 414×896 (iPhone genişliği) viewport'ta aynı akış (kırılımsız
borç sonucu) yeniden ekranda görüldü.

**Gözlem:** **temiz.** Üst çubuk kompakt bir "sohbet" sekmesine düşüyor,
rozet çubuğu 2 satıra düzgün sarıyor, ANLADIĞIM pilleri kendi satırında,
sonuç kartı tek sütunda okunur, alt gezinme ikonları bir sırada. K7'nin
flex-satırı düzeltmesi (Senaryo 1) mobilde de **doğru** davranıyor —
ayrı bir mobil-özel kırılma bulunamadı.

---

## Senaryo 6 — `yokluk_sorgusu` (🔴🔴 mimari düzeyde eksik yetenek)

**Soru:** "bu ay hiç sipariş vermeyen müşteriler kim" — gerçek, sık sorulan
bir iş sorusu ("kim bize BU AY hiç sipariş vermedi, arayalım").

**Gözlem (curl, iki farklı koşum — biri direkt, biri planlı, ikisi de AYNI
kök hataya varıyor):**
- Direkt koşum: cube **`cari`** seçildi (bakiye/alacak/borç), `siparis`
  cube'una hiç bakılmadı. "0 satır" döndü — ama bu YANLIŞ sorunun
  tesadüfen boş cevabı, "hiç sipariş vermeyen" sorusunun cevabı DEĞİL.
- Planlı koşum (4 adım): 1. adım DOĞRU cube'u buldu (`siparis.siparis_adedi
  · musteri_kod kırılımında`) ama sonra **`KIYASLA`** (akran ortalamasıyla
  karşılaştır) fiiline geçti — yani "SIFIR sipariş verenler" yerine
  "ortalamadan SAPAN'lar" hesaplayacaktı. Trace: `bilinmeyen=hic,vermeyen,kim`
  — sistem "hiç"/"vermeyen" kelimelerini **tanımıyor**, atıyor.

**Kök neden:** Cube Query DSL'in (`cube_query` sözleşmesi — `dimensions`/
`measures`/`filters`/`order`) hiçbir yerinde bir **"count=0"/"NOT EXISTS"/
anti-join** ifadesi yok. "Hiç X yapmayan Y" sorusu SQL'de klasik bir
LEFT JOIN…WHERE NULL ya da NOT IN alt-sorgusu ister — bu birincil, temel
bir SQL kalıbı ama şu anki sorgu şeması bunu **hiç temsil edemiyor**. Garson
bunu göremeyince en yakın BİLDİĞİ şeye ("akran kıyası" ya da "ilgisiz bir
cube'un boş sonucu") düşüyor.

**Neden bu tikel değil:** bu yalnız "sipariş" için değil — "hiç ödeme
yapmayan", "hiç şikayet açmayan", "hiç bakım görmeyen makine", "hiç
üretilmeyen ürün kodu"… HER "hiç X yapmayan Y" kalıbı aynı duvara çarpar,
çünkü eksik olan sorgu ŞEMASININ KENDİSİ, bir cube'un metadata'sı değil.

**Durum:** düzeltme `cube_query` şemasına yeni bir birincil kavram (ör.
`having: {measure, op: "count_eq", value: 0}` ya da `anti_join` alanı)
eklemeyi gerektirir — bu bir mimari genişleme, aceleye getirilmedi.
**Fix bekliyor, ayrı bir tasarım turu ister.**

---

## Senaryo 7-8 — UI akışları: pano ekleme + yanlış geri bildirimi (✅ SORUN YOK — dengeleme kaydı)

İki UI alt-sistemi baştan sona test edildi, ikisi de **temiz**:
- **"+ panoya ekle" → "+ yeni pano"**: isim girme kutusu (`Panom`
  varsayılan) doğru açıldı, "tamam" ile kaydedildi, buton `✓ panoda`
  durumuna geçti — çalışıyor.
- **"✗ yanlış" → yorum yaz → gönder**: popover doğru açıldı
  ("NEDEN YANLIŞ? (OPSİYONEL)"), yorum yazılınca buton metni "yorumsuz
  gönder"den "yorumla gönder"e değişti (küçük ama doğru bir UX detayı),
  gönderilince buton `✗ kaydedildi` durumuna geçti — VQR'a kaydedildiği
  doğrulandı.

Bu ikisi **daha önce hiç test edilmemiş** iki ayrı alt-sistemdi (pano +
geri bildirim); ikisi de sağlam çıktı — rapor dengeli kalsın diye
kaydedildi.

---

## Senaryo 9 — `bilesik_soru_delta_secim` (🟡 kapasite eksik ama DÜRÜST — dengeleme + gerçek bulgu bir arada)

**Soru:** "geçen ay ile bu ay arasında en çok değişen makine hangisi ve
muhtemel sebebi ne olabilir" — bir kullanıcının gerçekten sorabileceği,
delta (değişim) + causal (sebep) birleşik bir soru.

**Gözlem (canlı, curl + tarayıcı — ikisi de aynı sonuca vardı):** sistem
akıllıca bir **7 adımlık plan** kurdu: iki dönem için `ort_oee · makine`
sorgula → `MATRIS` (iki dönemi yan yana koy) → `BAGLA` (en dikkat çeken
makineyi seç) → `SUZ` (o makineye daralt) → tekrar sorgula → `ANLAT`.
Kurgu doğru yönde ama **`BAGLA` iki-dönemli bir matristen "en çok
DEĞİŞEN"i seçemedi** — ekranda:

> ⚠ `ort_oee` için seçilecek bir satır çıkmadı — bu adım bir varlık
> seçemedi.
> ⚠ İstenen kırılım(lar) bu cevaba yansımadı: donem, varis_il — seçilen
> veri kümesinde yok, onun yerine makine kullanıldı.

Sonuç: `ORT_OEE: —` (boş) — **1 satırlık ama DEĞERSİZ bir "sonuç".**

**Kök neden (curl trace'i zaten kendi kendine işaretlemişti):** `niyet:`
satırında `🔴temsil-yok=kiyas` — sistem KENDİSİ "kıyas" (dönemler arası
delta) kavramının bu plan dilinde **temsili olmadığını** biliyor.
`BAGLA` fiili "satırlar arasından bir varlık SEÇER — «en kötü hangisi»
sorusunun cevabı" — yani TEK bir ölçü sütununda EN KÖTÜ/EN İYİ değeri
seçmek için tasarlanmış, İKİ dönemin FARKINI (delta) hesaplayıp ona göre
seçim yapmak için DEĞİL. "En çok değişen" sorusu bu fiil setinde
**temsil edilemiyor**.

**Neden bu Ç10/Senaryo-6'dan (yokluk) FARKLI bir bulgu, aynı ailenin
üyesi:** ikisi de "plan dilinde eksik bir birincil kavram" (Senaryo 6:
`NOT EXISTS`, burada: `delta'ya göre seçim`) — ama BURADA sistem
**sessiz kalmadı**, dürüstçe *"bir varlık seçemedi"* dedi ve boş bir
sonuç gösterdi, YANLIŞ bir makine adı UYDURMADI. **Bu ADR-0020'nin tam
istediği davranış** — kayıt için dengeleme amaçlı not edildi.

**Durum:** kapasite eksik (fix bekliyor, `BAGLA`'ya delta-farkındalı bir
mod eklenebilir), ama mevcut davranış **güvenli** (yanlış bilgi
üretmiyor). Öncelik Senaryo 6'dan (sessiz/yanlış) daha DÜŞÜK.

---

## Senaryo 13 + 20 — 🔴🔴 EN CİDDİ BULGU: uzun/bileşik sorular TAM RET alıyor

**Sorular:** (13) *"bu yıl her ay için ciro ve fire oranını göster, hangi
ay en kötüsüydü açıkla, o ayda hangi müşteri en çok etkiledi bul, ve
gelecek ay için ne yapmalıyız söyle"* — (20) *"vardiya bazında oee ve
fire karşılaştır, en kötü vardiyayı bul, sebebini araştır, ve bu vardiya
için somut 3 aksiyon öner"* — ikisi de **fresh session, ilk tur, bağlam
yok.**

**Gözlem:** ikisi de **TAM RET** aldı — sistem sanki kullanıcı BOŞ bir
ekranı yorumlamaya çalışıyormuş gibi davrandı:

> Yorumlayabileceğim bir rapor **ekranda yok** — henüz bir sonuç
> üretmedim. Önce bir soru sor…

Bu **YANLIŞ** — her iki cümle de baştan sona geçerli, yeni, kendi
kendine yeten bir veri isteğiydi (A/B testiyle kanıtlandı: cümlenin
**yalnız ilk kısmı**, örn. *"bu yıl her ay için ciro ve fire oranını
göster"*, TEK BAŞINA sorulunca **doğru çalışıyor**, `cube_query` üretiyor).

**Kök neden (kod satırıyla kanıtlandı — `app/followup.py:506`):**

```python
def _konusma_baglamsiz(q: str) -> str | None:
    ...
    for tur, kaliplar in ((TUR_ANLAT, _ANLAT), (TUR_NORMAL, _NORMAL),
                          (TUR_NE_YAPMALI, _NE_YAPMALI), (TUR_ISARET, _ISARET)):
        if not _hit(q, kaliplar):
            continue
        if tur in (TUR_NORMAL, TUR_NE_YAPMALI) or zamir or _kisa_soru(q):
            return tur
    return None
```

`TUR_ANLAT` ve `TUR_ISARET` **doğru** korunuyor — yalnız bir zamir
("bunu") VARSA ya da cümle KISAYSA "bağlamsız konuşma" sayılıyorlar
(dosyanın kendi örneği: *"fire analizini yap"* — uzun, zamirsiz — bu
yüzden YENİ KONU sayılır, doğru). **Ama `TUR_NORMAL` ve `TUR_NE_YAPMALI`
bu korumadan MUAF** — `tur in (TUR_NORMAL, TUR_NE_YAPMALI)` şartı
**HİÇBİR ek koşul olmadan** true dönüyor. Yani cümle 30 kelime de olsa,
başında tam teşekküllü bir veri isteği de olsa, İÇİNDE bir yerde *"ne
yapmalıyız"* ya da *"normal mi"* kalıbı geçtiyse **TÜM cümle** bağlamsız
konuşma sayılıp reddediliyor.

⚠ **Bu dosyanın KENDİ tarihçesi bu TAM HATAYI zaten tarif ediyor**
(`§NÇ`, satır 651-671, ayrı bir fonksiyonda): *"Bir dosyada iki kural
aynı ayrımı yapıyorsa, biri ötekini sormak zorundadır; sormadığı gün,
ikisi ayrı şeyler söyler."* `_konusma_baglamsiz` (satır 488) ile
`sinifla`'nın kendi döngüsü (satır 605+, `§NÇ`) **AYNI ayrımı** yapıyor
ama `_konusma_baglamsiz` `§NÇ`'nin öğrendiği dersi (zamir/kısalık şartı)
YALNIZCA `TUR_ANLAT`/`TUR_ISARET` için almış, `TUR_NORMAL`/
`TUR_NE_YAPMALI` için almamış.

**Neden bu tikel değil, genel:** "veri getir + bir şeyi bul/tespit et +
ne yapmalıyız söyle" kalıbı **gerçek bir yöneticinin EN DOĞAL sorusu**
— Senaryo 20 tamamen FARKLI bir cümleyle (vardiya/oee/fire, aksiyon)
AYNI kökü **bağımsız** doğruladı. Domain'e, cube'a, ölçüye bakmıyor —
yalnız cümlenin İÇİNDE `_NE_YAPMALI`/`_NORMAL` kalıbı geçip
geçmediğine.

**Önerilen kök çözüm (uygulanmadı — bu turun disiplini: önce teşhis):**
`_konusma_baglamsiz`'deki satır 506'yı `sinifla`'nın **kendi**
düzeltilmiş halinin izlediği kuralla hizala — `TUR_NORMAL`/
`TUR_NE_YAPMALI`'yı da `zamir or _kisa_soru(q)` şartına tabi tut (tıpkı
`TUR_ANLAT`/`TUR_ISARET` gibi). Bu, dosyanın KENDİ içindeki bir
tutarsızlığı gideriyor — yeni bir kural İCAT ETMİYOR, var olanı
genişletmiyor bile, yalnız EŞİTLİYOR. Düşük risk, yüksek etki.

---

## Senaryo 14-19 — kısa notlar (root cause'ları bulundu, ayrıntı yukarıda özet tabloda)

- **14 (kendini düzeltme):** çekirdek mekanizma SAĞLAM (`hayır X değil
  Y` doğru anlaşıldı) — ama "hayır" kelimesi AYRI bir yerde (dışlama-
  filtresi sezgisi) de dinleniyor ve boşuna tetikleniyor. Senaryo 2a'daki
  "kelime iki farklı katmanda iki farklı iş yapıyor, çakışıyor" ailesinin
  ÜÇÜNCÜ örneği.
- **15 (eşik filtreli liste):** `parti_sayisi` bir ÖLÇÜ iken plan onu
  BOYUT sanıp kırıldı — ama dürüstçe. Ölçü/boyut karışıklığı ailesi.
- **17 (kısmi yerine getirme):** 4 parçalı bir isteğin yalnız 1 parçası
  uygulandı, kalanı **"EKSİK: olcu_ikamesi, sıralama"** gibi teknik/kısa
  bir etiketle geçiştirildi — kullanıcı hangi 3 isteğinin YOK sayıldığını
  AÇIKÇA göremiyor. ADR-0020 "beyan et" ilkesi TEKNİK olarak uygulanıyor
  ama İNSAN-OKUR değil.
- **18 (Q2 jargon):** düşük öncelik, kabul edilebilir sınır.
- **16, 19 (argo + aciliyet tonu):** **iki güçlü pozitif bulgu** — dil
  sağlamlığı yüksek, duygusal/aciliyet dolgu kelimeleri doğru
  `bilinmeyen` sayılıp çekirdek istek bozulmuyor.

---

## 🔴🔴 TOPLU KÖK-NEDEN SENTEZİ (20 senaryo sonrası)

Kullanıcının talimatı gereği: **tikel değil, genel.** Aşağıdaki kök
nedenler TEK bir cube/senaryoya değil, ürünün MİMARİ katmanlarına
bağlanıyor.

### KÖK NEDEN A — "Bir kelime iki görevde": sinonim/kalıp sözlükleri global, bağlamsız

**Kanıt:** Senaryo 2a (neden/sebep → 3 cube'da çıplak sinonim), 14
(hayır → dışlama-filtresi sezgisi), 18'in kuzeni olan Q2 gibi durumlar.

**Kök:** Bu ürün **iki AYRI dilbilim katmanı** taşıyor —
(1) `followup.py`'nin konuşma-kalıbı sözlükleri (`_NEDEN`, `_YAPISAL`,
vb.) ve (2) her cube'un KENDİ `metadata.yml`'indeki `synonyms` listeleri
— ve BU İKİ KATMAN birbirinden **habersiz**. Bir kelime birinde
"konuşma sinyali", ötekinde "alan adı sinyali" olabiliyor ve HİÇBİR
YERDE bu çakışma önceden kontrol edilmiyor (bu turda 3 cube'da + 1
konuşma-kalıbında canlı çakışma bulundu — muhtemelen daha fazlası var,
taranmadı).

**Genel kök çözüm önerisi (mimari):** `followup.py`'nin konuşma-kalıbı
sözlükleri ile TÜM cube'ların sinonim sözlükleri arasında **kesişim
kontrolü yapan bir kapı** (test_soru_sozcugu_sinonim_degil.py'nin
YAPTIĞI TAM OLARAK BU — bu turda zaten inşa edildi ve genişletilebilir
bir örnek oluşturdu). Bu kapı ŞU AN yalnız `followup._NEDEN`'e bakıyor;
TÜM konuşma-kalıbı sözlüklerini (`_YAPISAL`, `_NORMAL`, `_ISARET`, vb.)
kapsayacak şekilde genelleştirilebilir.

### KÖK NEDEN B — "Yapısal öncelik" kuralı ASİMETRİK ve SESSİZ

**Kanıt:** Senaryo 2b (neden sessizce düşüyor), Senaryo 13+20 (TAM RET
— aynı ailenin en şiddetli üyesi).

**Kök:** `followup.py`'de "kullanıcı yeni sayı bekliyorsa önce onu ver"
felsefesi **iki farklı yerde iki farklı titizlikte** uygulanmış:
`sinifla()`'nın ana döngüsünde (`§NÇ`, iyi kalibre edilmiş, zamir/
kısalık şartlı) ve `_konusma_baglamsiz()`'de (aynı fikir ama şartsız,
kalibrasyonsuz). **İkisi de "yapısal önceliğin ne zaman geçerli olduğu"
sorusuna cevap veriyor ama FARKLI cevaplar veriyor** — dosyanın kendi
sözleriyle: *"bir dosyada iki kural aynı ayrımı yapıyorsa, biri ötekini
sormak zorundadır."*

**Genel kök çözüm önerisi (mimari, ORTA vadeli):** bu iki fonksiyonun
"hangi tur'lar ek bir zamir/kısalık şartına tabi" kararı **TEK bir
merkezi tabloya** taşınmalı (ör. `_BAGLAMSIZ_ISTISNA_SARTLI = {TUR_ANLAT,
TUR_NORMAL, TUR_NE_YAPMALI, TUR_ISARET}` gibi TEK bir küme, HER iki
fonksiyon da BU kümeyi okur) — bugün olduğu gibi iki fonksiyonun kendi
kopyasını elle senkron tutması yerine. Bu, KAT-1'in ("bir kararın tek
sahibi olmalı") bu dosya İÇİNDE bile ihlal edildiğinin somut kanıtı.

### KÖK NEDEN C — Plan/sorgu dilinde eksik birincil kavramlar

**Kanıt:** Senaryo 6 (yokluk/NOT EXISTS yok), Senaryo 9 (delta'ya göre
seçim yok, `BAGLA` yalnız tek-ölçü sıralar), Senaryo 15 (ölçü/boyut
ayrımı plan kurulumunda karışabiliyor).

**Kök:** `cube_query`/makro fiil seti (`SORGU/KIR/SUZ/BAGLA/HESAPLA/
MATRIS/KIYASLA/ANLAT`…) zengin ama **tam değil** — iki KLASİK SQL
kalıbı (anti-join/NOT EXISTS, iki-serili delta-sıralama) hiç temsil
edilmiyor. Sistem bunu FARK EDİYOR (`🔴temsil-yok=kiyas` kendi
trace'inde) ama kullanıcıya YALNIZ dolaylı yoldan (boş sonuç, "bir
varlık seçemedi") yansıyor.

**Genel kök çözüm önerisi (mimari, UZUN vadeli — büyük iş):** plan
diline iki yeni birincil fiil/kavram eklenmesi düşünülebilir:
(1) bir `having: {op: "count_eq"|"not_exists", ...}` ya da yeni bir
`YOKLUK` fiili, (2) `BAGLA`'nın bir `delta` modu (iki kaynaklı MATRIS
girdisini FARK'a göre sıralayabilen). İkisi de KAT-1 ilkesine uygun
şekilde TEK yerde (fiil kataloğu, `plan_semasi.py`) tanımlanmalı — cube
başına değil.

### KÖK NEDEN D — Kısmi yerine getirme, İNSAN-OKUR olmayan beyanla örtülüyor

**Kanıt:** Senaryo 17 ("EKSİK: olcu_ikamesi, sıralama").

**Kök:** ADR-0020 ("sessiz düzeltme yok, beyan et") TEKNİK olarak
uygulanıyor (kod alanları/etiketler var) ama beyanın KENDİSİ jargon —
kullanıcı "olcu_ikamesi" kelimesinin KENDİ 4 isteğinden HANGİSİNE
karşılık geldiğini bilemez.

**Genel kök çözüm önerisi:** beyan metninin ÜRETİLDİĞİ yerde (muhtemelen
`ask.py`'nin "EKSİK" bloğu), her düşen özelliğin orijinal SORU
PARÇASIYLA eşleştirilip insan-okur bir cümleye çevrilmesi — ör.
*"⚠ 'makine performansı' ve 'bakım geçmişi' isteklerini bu turda
işleyemedim — ayrı ayrı sorarsan bakarım."*

### Öncelik sıralaması (kullanıcının "tikel değil kök" ölçütüyle)

1. **KÖK NEDEN B → Senaryo 13/20 fix'i** — en şiddetli (TAM RET), en
   düşük riskli fix (tek satır, mevcut deseni genişletiyor), en yüksek
   etki (gerçek yönetici sorularının doğal bir kalıbını kırıyor).
2. **KÖK NEDEN A → sinonim/kalıp kesişim kapısı genelleştirilmesi** —
   zaten bir örneği var (K9-devam), genelleştirmek görece ucuz.
3. **KÖK NEDEN D → beyan metni okunabilirliği** — orta risk/emek, yüksek
   UX kazancı.
4. **KÖK NEDEN C → plan diline yeni fiiller** — en yüksek emek/risk
   (yeni birincil kavramlar), ama en yüksek potansiyel etki (iki
   YAYGIN SQL kalıbı şu an tamamen kapalı). Ayrı bir tasarım turu ister.

---

*(20/20 tamamlandı. Kullanıcı onayıyla düzeltme fazına geçilebilir.)*
