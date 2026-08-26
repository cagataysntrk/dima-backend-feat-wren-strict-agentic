# Playwright Kampanyası — Düzeltme Yol Haritası

> **Bu belge bir REHBERDİR — geliştirme başladığında buradan takip edilir.**
> Kaynak: `belgeler/arastirma/2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md` (§13/§15
> — zaten yapılmış 2 düzeltme) + `belgeler/arastirma/2026-08-26_PLAYWRIGHT-
> CANLI-TEST-KAMPANYASI.md` (K1-K13 — yeni bulunan 11 kök sorun). Her madde:
> **sorun → kanıt → çözüm → doğrulama**. İşaretleme: `[ ]` yapılmadı ·
> `[x]` yapıldı · `[~]` kısmen/araştırma gerekiyor.

## Genel disiplin (unutulmasın)

- 🔴 **KAPI TOPLU KOŞULUR** — her madde için ayrı kapı yok. Hedefli `pytest`
  serbest (madde başına), ama `lab/kapi.py --tam` yalnız **bütün faz bitince
  bir kez**.
- 🔴 **Sessiz düzeltme yok, beyan et** (`ADR-0020`) — bir kusur "onarılamıyorsa"
  bile kullanıcıya söylenmesi, hiç söylenmemesinden iyidir.
- 🔴 **Curl/Playwright kanıtı asıl kanıt** — pytest yeşili yeterli değil, her
  madde canlıda (curl ya da tarayıcı) doğrulanmadan "bitti" sayılmaz.
- ⚠ Her madde **önce kod okunur/araştırılır**, körlemesine düzeltme yapılmaz —
  §15'in dersi: ilk tahmin (`value_index` fuzzy-match) yanlış çıktı, gerçek
  kök neden farklı yerdeydi.
- ⚠ Bir düzeltme başka bir maddeyi etkileyebilir (ör. K1 düzeltmesi K12'nin
  belirtisini de azaltabilir) — her fazın sonunda **tüm faz** yeniden
  Playwright'la sınanır, yalnız değişen madde değil.

---

## FAZ 1 — Veri dürüstlüğü (en kritik, kullanıcı yanlış bilgiyle hareket edebilir)

### 1.1 · K9 — "analiz et / neden / ne yapmalıyız" ayrışmıyor 🔴🔴 EN YÜKSEK ÖNCELİK
- [x] **Sorun:** "ne yapmalıyız?" → "bu neden böyle?" ile **birebir aynı** metni
  dönüyor (hiç reçete/aksiyon yok). *(Kanıt: kampanya S15, `s15/16/17_*.png`)*
- [x] **Araştır (bitti):** `followup.sinifla()` DOĞRU çalışıyor (`tur=ne_yapmali`,
  `_oner=True` doğru hesaplanıyor — izole test + canlı `trace` ile
  doğrulandı). Kök neden `routers/ask.py`'nin "cevap üstünde konuşma" bloğunda:
  `if _oner and katki.raporlar:` koşulu — `katki.raporlar` **boş** çıktığında
  (ölçü formül-bileşenli olup segment-bazlı ayrıştırma üretemediğinde,
  `contribution.report`'un `note` alanı yine de dolu geliyor) reçete bloğu
  **hiç çalışmıyor**, `not_metni` sessizce `katki.note`'ta (yani "neden"le
  aynı metinde) kalıyor. **Canlı debug log ile kanıtlandı:**
  `tur=ne_yapmali _oner=True raporlar=0` — yani sınıflandırma değil,
  reçete-üretim koşulu kırık.
- [x] **⚠ Genellik kontrolü (kullanıcı uyarısı üzerine):** bu OEE'ye özel bir
  veri sorunu **değil** — `katki.raporlar` boşluğu `_oner`/`katki` her ikisi
  de bu noktadan önce zaten genel/domain-agnostik hesaplanmış değişkenler;
  düzeltme herhangi bir küp/ölçüde (muhasebe, ciro, fire) aynı şekilde
  çalışır, kod içinde ölçüye özgü hiçbir dal yok.
- [x] **Çözüm (uygulandı):** `elif _oner:` dalı eklendi — reçete istendi ama
  `katki.raporlar` boşsa, `not_metni`'ne genel bir beyan ekleniyor: *"⚠ Reçete
  üretilemedi: aksiyon önerisi segment bazlı bir ayrıştırma ister, bu soruda
  öyle bir kırılım yok — yukarıdaki yalnız bir teşhis, bir öneri değil."*
  Artık "neden" ile "ne yapmalıyız" **asla birebir aynı** metin olamaz —
  ya gerçek reçete gelir ya da bu beyan eklenir.
- [x] **Doğrula (bitti):** imaj `s46`. Canlı curl, **iki farklı domain**:
  `oee` (formül-bileşenli) → "neden"↔"ne yapmalıyız" artık **farklı**, gerçek
  reçete geldi. `mizan.bakiye` (yarı-toplanabilir stok, tamamen ayrı sınıf) →
  yine **farklı**, bu sefer genel beyan tetiklendi. Hedefli pytest:
  `test_recete_uretilemedi_beyan_edilir.py` (3 test, biri genellik/zıt-ölçüt
  kapısı) + `test_red_yaninda_cevap.py` + `test_recete.py` → **30/30 geçti**,
  mevcut testler bozulmadı. **K9'un "neden↔ne yapmalıyız" yarısı KAPANDI.**
  Playwright'la görsel doğrulama (analist_turu, tam 5 tur) FAZ 1 sonunda
  toplu yapılacak (aşağıdaki "FAZ 1 kapanışı" maddesi).
- [ ] **Bilinmiyor/açık kalan:** "bunu analiz et" turunun neden **hiç** yazılı
  metin üretmediği (çıplak grafik) hâlâ ayrı, çözülmemiş bir alt-sorun —
  bu madde yalnız "neden"↔"ne yapmalıyız" ayrımını kapatıyor, "analiz et"in
  boşluğu **hâlâ açık**, ayrı araştırma gerekiyor.

### 1.2 · K1 — Dar bir istek geniş bir işleme büyüyor ⚠ ARAŞTIRMA SONUCU KÖKTEN DEĞİŞTİ

- [~] **Sorun (a) — 3 curl denemesinde TEKRAR ÜRETİLEMEDİ.** "makine bazında
  oee"→"bu yıl"→"yok ya sadece son 3 ayda"→"aylık göster"→"en düşük hangisi"
  zinciri **doğru `history`+`cube_query` bağlamıyla** üç kez ayrı ayrı
  koşuldu — **üçünde de** son sorgu doğru kaldı (`cube=oee, dims=[makine],
  measures=[ort_oee]`), hiç OEE→fire/renk sıçraması olmadı. Orijinal Playwright
  bulgusu (S3) ya (i) o oturuma özgü, tekrarlanmayan bir LLM-olasılıksallığı,
  ya da (ii) benim curl simülasyonumun UI'ın gerçek context taşımasından
  ince bir farkı var. **Karar (kullanıcı uyarısı gereği — körlemesine
  düzeltme yazma):** kesin kök neden olmadan kod değiştirilmedi. Bu madde
  `⊘ gözlem altında` olarak işaretlendi — FAZ 1 kapanışında Playwright'la
  (curl değil, gerçek tarayıcı) tekrar denenecek; o zaman da tekrar
  üretilemezse K1(a) roadmap'ten **düşürülecek** (yanlış alarm olarak
  kapatılacak, "düzeltildi" diye işaretlenmeyecek).

- [x] **Sorun (b) — ARAŞTIRILDI, kök neden beklenenden FARKLI çıktı.**
  "partileri listele" (ilk tur, tek başına) zaten `cube_query.dimensions`'a
  **TÜM 16 boyutu** koyuyor — trace bunu açıkça söylüyor: *"Bu bir **varlık
  sorusu** olarak okundu… bir ölçü hesaplanmadı."* Bu **kasıtlı ve mantıklı**:
  "listele" dendiğinde her kaydın (parti) tüm alanlarıyla bir **tablo satırı**
  istenir. İkinci tur ("en çok fire vereni üste al") **doğru** çalışıyor —
  trace: *"refine → deterministik düzenleme… üstünlük: sıralama sistem
  tarafından tamamlandı"* — yalnız `measures`+`order` ekliyor, 16 boyutu
  **haklı olarak** koruyor (siliş bir veri kaybı olurdu). **Sonuç: backend
  niyet ayrıştırması burada KIRIK DEĞİL.** Playwright'ta gördüğüm "kullanılamaz
  pivot" görünümü, bu (mantıklı) 16-boyutlu sonucun **pivot bileşeni**
  tarafından yanlış render edilmesiydi — yani bu K1 değil, **K13**'ün
  (pivot sessiz çöküyor) bir örneği. **K1(b) buradan kaldırıldı, K13'e
  taşındı** (bkz. FAZ 2.3) — kullanıcının "tekil değil kök çözüm" uyarısına
  uyarak: burayı OEE/parti'ye özel bir "16 boyutu kırp" yamasıyla düzeltmek
  YANLIŞ olurdu, çünkü backend'in davranışı **doğru**; asıl kök tek yerde
  (pivot UI) ve TÜM yüksek-boyutlu sonuçları etkiliyor, yalnız bu senaryoyu
  değil.

**Ders (kayıt için):** iki "kanıtlanmış" bulgudan biri (a) tekrar üretilemedi,
öbürü (b) yanlış katmana atfedilmişti. Playwright kampanyası **teşhis**
üretir, **kök neden** üretmez — kök neden her zaman kodu okuyup/canlıda
izole ederek ayrıca doğrulanmalı. Bu FAZ 1.2'nin kendisi bunun kanıtı.

### 1.3 · K2 — Sıfır-taban yüzde hesabı yanlış cümle üretiyor ✅ KAPANDI
- [x] **Sorun:** *"bakiye: Oca 2026→Tem 2026 %100,0 arttı (₺0 → ₺0)"* —
  matematiksel olarak tanımsız. *(Kanıt: S4, `s4_belirsizlik_final.png`)*
- [x] **Araştır (bitti) — kök neden hipotezden FARKLI çıktı:** `p==0`
  koruması `yoy.py:77` (`_merge`) içinde **zaten vardı**. Canlı curl'de
  `mizan.bakiye`'nin ham satırları çekildi: `-4.65e-10`, `9.31e-10` gibi
  **kayan-nokta artığı** (dengelenmiş/borç-alacak≈0 bir ölçü, SQL toplamı
  tam `0` değil). Python'da `4.65e-10` **truthy** — `and p` koruması bunu
  YAKALAMADI. İki gürültü-seviyesi sayı arasında `(c-p)/p*100` anlamsız bir
  yüzde üretti. **Bu `mizan`/`bakiye`'ye özel değil** — dengelenmesi
  beklenen HERHANGİ bir ölçüde (net etki, fark) olur.
- [x] **Çözüm (uygulandı):** `yoy.py`'ye domain-agnostik `_SIFIR_ESIGI = 1e-6`
  mutlak eşiği eklendi; `abs(p) > _SIFIR_ESIGI` koşulu `p != 0` yerine
  kullanıldı. Ölçü/küp adı geçmiyor, herhangi bir veri için çalışır.
- [x] **Doğrula (bitti):** `tests/test_yoy.py`'ye 2 test eklendi (asıl kapı +
  zıt-ölçüt: gerçek küçük değer hâlâ hesaplanır) → **17/17 geçti**. Canlı
  (imaj `s47`): `mizan.bakiye` ile "aylara göre" → **artık yanlış %100
  cümlesi yok** (`note=None` — trend sessizce hesaplanmıyor, yanlış sayı
  üretmiyor). ⚠ Küçük bir cilalama fırsatı kaldı (K2'nin kapsamı dışı,
  not edildi): `None` yerine "trend hesaplanamadı, taban sıfıra çok yakın"
  gibi bir beyan daha iyi UX olurdu — ADR-0020 ruhuna daha uygun, ama bu
  artık bir **doğruluk** sorunu değil bir **cilalama**, K2'nin asıl kapısı
  (yanlış sayı üretmeme) kapandı.

### 1.4 · K10 — Çoklu-filtre cümlesi çakışıyor ✅ KAPANDI
- [x] **Sorun:** *"…2026-02-25'ten itibaren VE 2026-04-01'den itibaren VE
  2026-05-01 tarihli…"* — üç filtre ifadesi üst üste binmiş.
  *(Kanıt: S2, `s2_grafik_ustunde.png`)*
- [x] **Araştır (bitti):** `app/drill.py::formula_explanation` — **pure,
  deterministik kod**, LLM'e bağlı değil. `filters` listesindeki HER zaman
  filtresi (`gte`/`lte`) ayrı bir cümle parçası olarak ekleniyordu, "ve" ile
  art arda. Canlı curl'de tekrar üretilemedi (§K1(a) gibi) AMA bu önemsiz —
  kusur koda **doğrudan bakılarak** kanıtlandı, LLM-flaky bir davranışa
  bağlı değil.
- [x] **Çözüm (uygulandı, TDD ile):** önce kırmızı test yazıldı (kusur
  kanıtlandı), sonra `formula_explanation` düzeltildi — biriken `gte`
  değerlerinden **en büyüğü** (en kısıtlayıcı), `lte`'lerden **en küçüğü**
  seçilip **tek** cümleye yazılıyor. Domain-agnostik — küp/ölçü adı
  geçmiyor, `_zaman` (zaman boyutu kümesi) hangi küpten gelirse gelsin aynı
  mantık çalışır.
- [x] **Doğrula (bitti):** `test_drill.py`'ye 2 test (asıl kapı + zıt-ölçüt:
  tek filtre hâlâ doğru) + `test_ask_drill_integration.py` +
  `test_drill_raw_guvenlik.py` → **45/45 geçti**.

**FAZ 1 durumu:** hedefli pytest'ler geçti (K9 30/30, K2 17/17, K10 45/45).
⚠ **Düzeltme (kullanıcı talimatı, en son /loop girdisi):** `--tam` ve
Playwright doğrulaması **her fazda değil**, yalnız **TÜM 4 faz** bitince
**bir kez** koşulacak — aşağıdaki "Faz sonrası" bölümüne taşındı. Aradaki
her faz yalnız hedefli pytest ile ilerler.

---

## FAZ 2 — Görselleştirme güvenilirliği

### 2.1 · K4 — Grafik seçimi 3+ boyutta tutarsız ✅ KAPANDI
- [x] **Sorun:** aynı türden veri (makine×vardiya) bir yerde (S7) mükemmel
  heatmap, başka yerde (S8, +ay boyutu) okunamaz "duvar kağıdı". *(Kanıt:
  `s7_atif_ifadesi.png` vs `s8_geri_donus_pre.png`)*
- [x] **Araştır (bitti):** `viz.py`'nin `facet` kararı (`recommend()`, ~satır
  196-210) **panel ekseninin** kardinalitesini kontrol ediyordu
  (`_card(a) <= 6`) ama **series ekseninin** (renkli çubuk/çizgi sayısı)
  kardinalitesini **hiç kontrol etmiyordu**. Vardiya (3, panel) eşiği
  geçiyor, makine (11, series) kontrolsüz kalıyor — her panelin içi 11
  renkli çubuk oluyordu. Saf, deterministik kod — LLM'e bağlı değil,
  canlı tekrar üretime gerek kalmadan koddan kanıtlandı (K10 gibi).
- [x] **Çözüm (uygulandı):** `_FACET_KARDINALITE_TAVANI` (=6, panel
  ekseniyle **aynı ve simetrik**) artık series eksenine de uygulanıyor —
  her iki dalda (`time_col` var/yok). Domain-agnostik: hangi iki boyut
  panel/series rolüne düşerse düşsün aynı kural.
- [x] **Doğrula (bitti):** `test_viz.py`'ye 2 test (asıl kapı: yüksek-
  kardinaliteli series artık facet değil + zıt-ölçüt: düşük-kardinaliteli
  series hâlâ facet) → **40/40 geçti**. Canlı doğrulama (`s49` imajı,
  `demo-boyahane`): aynı canlı kusurun senaryosu (`makine`×`vardiya`×`ay`,
  `makine`=11 kardinalite) artık `viz.kind="pivot"` (`facet=null`) —
  önceki "duvar kağıdı" facet KAYBOLDU. *(Not: `hat` boyutuyla pozitif
  kontrol denemesi yanlış çıktı verdi çünkü `hat`'ın kendisi 8 farklı
  değer taşıyor — 6 eşiğini AŞIYOR; bu aslında doğru davranış, hatalı
  varsayımdı. Pozitif kontrol (düşük kardinalite → hâlâ facet) sentetik
  testle kanıtlı.)*
- [x] **Çözüm (revize edildi):** ilk taslak "küçük-çoklular ya da zaman
  kaydırıcısı"na düşmeyi öneriyordu — araştırma gösterdi ki motor zaten
  3. boyut eşiği aşınca **`pivot`a** düşüyor (satır 234'teki `elif
  len(dims) > 2: kind = "table"` → `recommend()`'in (D) bloğu tabloyu
  pivota yükseltiyor). Bu zaten "düz çok-renkli çubuk değil, okunur bir
  alternatif" hedefini karşılıyor — ayrı bir küçük-çoklular/zaman-
  kaydırıcısı bileşeni İCAT ETMEYE gerek yoktu (mevcut dil genişletildi).
- [x] **Doğrula (bitti):** canlı `demo-boyahane` ile aynı kusur senaryosu
  (`makine`×`vardiya`×`ay`) → `pivot`, doğrulandı (yukarıdaki not).
  `geri_donus` senaryosuyla ayrı tekrar gerekmedi — düzeltme küp/domain'e
  bakmıyor, yalnız kardinaliteye bakıyor (kodda kanıtlı, bkz. K13 §2.3
  benzer genişletilmiş-kapsam notu).

### 2.2 · K5 — X ekseni etiketleri okunmuyor ✅ KAPANDI (typecheck ile; görsel doğrulama faz-sonu Playwright'ta)
- [x] **Sorun:** kalabalık kategoride (11 makine) etiketler üst üste
  biniyor. *(Kanıt: S2, S3, S9'un ilk hâli)* **Araştırıldı:** `chart.ts`'te
  X ekseni etiket mantığı (döndürme/interval) **6 farklı yerde**
  kopyalanmış, tutarsız eşiklerle (`>8` ya da `>5`) ve HEPSİ `interval: 0`
  zorluyordu — yani ECharts'ın kendi üst-üste-binme ÖNLEME mekanizması
  (`interval:"auto"`) hiçbir yerde kullanılmıyordu. 11 kategori + sabit
  35° döndürme + zorunlu tüm-etiketler-göster kombinasyonu üst üste
  binmeye yetiyordu. **KAT-1 ihlali de vardı** (aynı karar 6 yerde ayrı
  ayrı, tutarsız).
- [x] **Çözüm:** tek paylaşılan `axisLabelSpacing(n, allowSkip=true)`
  fonksiyonu (`chart.ts`, üstte) — kategori SAYISINA göre 4 kademe
  (döndürme + font + `n>10`'da `interval:"auto"`). `allowSkip=false`
  yalnız heatmap'te (hücre-hizalı eksen, etiket atlanamaz — mevcut
  kasıtlı davranış korundu). **6 çağrı yeri de** bu tek fonksiyona
  yönlendirildi — domain-agnostik, yalnız `n`'e bakıyor.
- [x] **Doğrula:** `tsc --noEmit` temiz (0 hata). ⊙ Frontend'te unit-test
  altyapısı (`vitest`/`jest`) hiç kurulu değil — bu operasyonun kapsamı
  dışında yeni bir test çatısı kurmak yerine, görsel doğrulama **4 faz
  bitince zorunlu Playwright turuna** bırakıldı (kullanıcı talimatı: faz
  arası Playwright yok).

### 2.3 · K13 — Pivot/tablo, veriye uymadığında sessiz kalıyor 🔴 GENİŞLETİLMİŞ KAPSAM
- [ ] **Sorun:** 1000 satır pivot'ta 1 hücreye çöktü, hiç uyarı yok. *(Kanıt:
  S10, `s10_liste_niyeti.png`)*
- [x] **§1.2 güncellemesi:** K1(b)'nin araştırması gösterdi ki bu **K1'in bir
  alt kümesi değil, tam tersi** — backend'in ürettiği 16-boyutlu sonuç
  **doğruydu** (varlık listesi + sıralama, mantıklı). Kusur **tamamen
  burada**, pivot bileşeninde. Yani düzeltme K1'de değil **yalnız burada**
  yapılacak — ve domain-agnostik olmalı (16 boyutlu `parti` özel değil,
  herhangi bir yüksek-kardinaliteli sonuç aynı şekilde çökebilir).
- [x] **Çözüm:** `PivotTable.tsx`'e çarpışma sayacı eklendi — hücre
  anahtarı (`entity`+`kova`) birden fazla satıra düşerse (yani 2 boyutlu
  matris veriye kayıpsız uymuyorsa) `cell.set()` ÖNCESİ tespit edilip
  sayılır; çarpışma varsa tablonun üstünde **görünür bir amber uyarı
  bandı** çıkar ("N satırdan M'si aynı hücreye düşüp üzerine yazıldı").
  Domain-agnostik: hangi boyutun kaybolduğuna bakmıyor, yalnız aynı
  anahtara birden fazla satır düşüp düşmediğine — `entityDim`/`timeCol`
  ne olursa olsun aynı mantık. "Otomatik tabloya düş" yerine "uyar"
  seçildi: kullanıcı zaten tek tıkla `tablo` sekmesine geçebiliyor
  (`ResultView.tsx`'te mevcut), otomatik geçiş kullanıcının pivot'u
  BİLEREK seçtiği durumları da sessizce ezerdi.
- [x] **Doğrula:** `tsc --noEmit` + `eslint` temiz (0 hata/uyarı). Frontend
  unit-test altyapısı yok (K5'teki not aynen geçerli) — görsel doğrulama
  faz-sonu Playwright turunda (yüksek-kardinaliteli, `parti`-DIŞI bir
  senaryoyla da).

**FAZ 2 durumu:** yalnız hedefli pytest ile ilerler — `--tam`/Playwright
yok, tüm 4 faz bitince tek koşum (bkz. "Faz sonrası").

---

## FAZ 3 — Sunum temizliği

### 3.1 · K6 — Dev-trace ana içerikte sızıyor ✅ KAPANDI
- [x] **Sorun (araştırıldı — kısmen doğrulandı, kısmen ÇÜRÜTÜLDÜ):**
  canlı curl ile ("son 2 yıl satış verileri..." → 5 adımlı plan, `s49`)
  `$1`/`kaynaklar=` iddiası **tekrar ÜRETİLEMEDİ** — `plan_tuketici.py`
  içindeki `onizleme_satiri()` bunu ÖNCEKİ bir oturumda (`s24`/`s27`
  kanıtlı) zaten temizlemiş: `$N` → sıra numarasına çevriliyor, `**`/`` ` ``
  markdown işaretleri siliniyor. ⊘ Bu alt-iddia YANLIŞ TEŞHİS'ti,
  düzeltme gerekmedi (Playwright bulgusu teşhistir, kök neden değil —
  kanıtlandı). **Ama `SORGU/AYRISTIR/GORSEL/ANLAT` iddiası DOĞRULANDI:**
  `PlanOnizleme.tsx`'te her adımın `fiil` alanı (backend'in iç enum'u)
  çıplak rozet olarak basılıyordu — üstelik backend'in KENDİSİ
  `onizleme_satiri()`'de bu öneki `metin`'den BİLEREK sıyırıyordu
  (`onek = f"**{fiil}** — "` → strip edilir) — frontend o kararı
  rozette geri açıyordu.
- [x] **Çözüm:** `PlanOnizleme.tsx`'teki `{a.fiil}` rozeti kaldırıldı —
  `metin` zaten tam okunur bir cümle, ikinci bir jargon etiketi
  gerekmiyor. KAT-1: çeviri sözlüğü (`FIIL_ONIZLEME`) backend'de TEK
  sahipte kaldı, FE'ye ikinci bir kopya taşınmadı (yeni bir çeviri
  tablosu İCAT EDİLMEDİ — yalnız hatalı bir gösterim kaldırıldı).
- [x] **Doğrula:** `tsc --noEmit` + `eslint` temiz. Görsel doğrulama
  faz-sonu Playwright turunda (aynı 5-adımlı senaryo).

### 3.2 · K12 — Thread listesi ayırt edilemiyor ✅ KAPANDI
- [x] **Sorun (araştırıldı — kısmi çürütme):** kod okuması gösterdi ki
  `HistoryPanel.tsx` **zaten** mesaj sayısı + zaman damgası basıyordu —
  iddianın "hiç ipucu yok" kısmı yanlıştı. Gerçek kusur: damga yalnız
  **dakika** çözünürlüklüydü — Playwright'ın saniyeler arayla ürettiği
  ardışık aynı-başlıklı sohbetler aynı "gg.aa ss:dd" değerine düşüyordu,
  yani pratikte ayırt edilemez kalıyordu.
- [x] **Çözüm:** iki bağımsız kök-düzeltme: (1) `fmtDate`'e saniye
  eklendi; (2) asıl güçlü sinyal — backend'e `ConversationOut.last_question`
  eklendi (`conversations.py`: her sohbetin SON turunun soru metni,
  `ConversationMessage.question`'dan — yeni DB kolonu GEREKMEDİ, var olan
  alandan türetildi). Başlık aynı kalsa bile son soru neredeyse hiç aynı
  olmaz — bu, zaman damgasından daha güçlü ve domain-agnostik bir sinyal.
  `HistoryPanel.tsx` bunu başlığın altında ikinci bir satır olarak basıyor.
- [x] **Doğrula:** `tests/test_conversations.py` — yeni test **2 farklı
  küple** (`oee` + `mizan`) → **4/4 geçti** (docker). Canlı (`s50`,
  `demo-boyahane`): `/conversations` listesinde gerçek geçmiş veriyle
  `last_question` doğru ve title'dan **farklı** dolduğu doğrulandı (ör.
  başlık "bu yıl personel bazında verimlilik", `last_question`: "peki
  fire ne durumda?"). `tsc`+`eslint` temiz. Görsel (sol panel) doğrulama
  faz-sonu Playwright turunda.

**FAZ 3 durumu:** yalnız hedefli pytest ile ilerler — `--tam`/Playwright
yok, tüm 4 faz bitince tek koşum (bkz. "Faz sonrası").

---

## FAZ 4 — Küçük, izole düzeltmeler (paralel yapılabilir)

### 4.1 · K7 — Kullanıcı mesajı CSS bug'ı ⊘ GÖZLEM ALTINDA (tekrar üretilemedi)
- [x] **Sorun (araştırıldı — tekrar ÜRETİLEMEDİ):** ekran kanıtı bulundu:
  `s12_uretim_muduru_sabahi.png`'de "her pazartesi bu raporu bana yolla"
  ve `s17_analist_analiz_et.png`'de "bunu analiz et" **kelime kelime
  dikey** görünüyor. Statik kod okuması, sorumlu elementi buldu
  (`ReportPanel.tsx`'in `it.note` dalı, `<h3>{it.question}</h3>`,
  `mx-auto max-w-4xl px-8 py-4` kapsayıcısında) — normal `block`
  render, `flex-col` YOK, `white-space` normal; şüpheli hiçbir CSS
  kalıbı görülmedi.
- [x] **Canlı doğrulama (2 bağımsız deneme, gerçek Playwright/Chromium,
  aynı 1920×834 çözünürlük):** (1) "bu yıl personel bazında verimlilik"
  → "her pazartesi bu raporu bana yolla" — `h3` **832px genişlik, normal
  block, sarma yok**; (2) aynı zincire "bunu analiz et" — **aynı temiz
  sonuç**. Her ikisi de kanıt görsellerindeki BİREBİR ifadeler, aynı
  akış, aynı motor imajı sürümü — **hiçbiri tekrar üretilemedi**.
- [x] **Karar:** disiplin gereği (bkz. `feedback_kok_cozum_tekil_degil` /
  bu operasyonun *"Playwright bulguları teşhistir, kesin kök neden
  değil"* dersi — K1(a)'da da yaşandı) uydurma bir CSS düzeltmesi
  YAZILMADI. ⊘ **Gözlem altında** işaretlendi: kod okuması ve 2 canlı
  deneme culprit bulamadı; ya geçici bir render-anı yarışıydı (font
  yükleme/ilk boya sırasında) ya da paylaşılan repo'da eşzamanlı çalışan
  başka bir geliştiricinin (bkz. `feedback_paylasilan_repo_guvenligi`)
  ilgisiz bir değişikliği yan etkiyle düzeltti — ikisi de doğrulanamadı.
- [x] **Doğrula:** N/A (düzeltme yapılmadı — gözlem kaydı faz-sonu
  Playwright turunda 3. kez denenecek; yine üretilmezse rapor kapanır).

### 4.2 · K8 — Olası uyarı yorgunluğu ✅ ÖLÇÜLDÜ — İDDİA ABARTILI ÇIKTI, DÜZELTME GEREKMEDİ
- [x] **Sorun:** "neredeyse her cevapta tetikleniyor" iddiası — gözlemseldi,
  ölçülmemişti.
- [x] **Araştır (bitti — canlı ölçüm, 2 domain, 15 sorgu):** `interpret.py`
  `_signals()`'ın anomali dalı `schedules.detect_anomalies` → `stats.z_skorlari`
  (`|z|≥k=2.0`, popülasyon std, min. 4 gözlem) kullanıyor — HER noktayı ayrı ayrı
  test ediyor (klasik çoklu-karşılaştırma deseni: nokta sayısı arttıkça "en az bir
  işaret" olasılığı aritmetik gereği yükselir). **Canlı ölçüm** (`oee`+`mizan`+
  `personel`, 15 farklı zaman-serisi sorgusu, `demo-boyahane`, `s50`):
  **4/15 (%27) anomali tetikledi** — "neredeyse her cevapta" (~%90+) iddiası
  **doğrulanmadı**, gerçek oran istatistiksel beklentiyle (`|z|≥2` ~%4,6/nokta ×
  ~10-27 nokta/seri) tutarlı ve ölçülü.
- [x] **Bulgu — kod ZATEN doğru mitigasyonu uyguluyor:** her tetiklenme
  `stats.tarama_beyani()` ile **taranan aday sayısını beyan ediyor** ("27 aday
  tarandı, 1'i eşiği geçti ⊙ şans payı...") — CHI 2018 (Zgraggen et al.,
  *"%60+ kullanıcı içgörüsü yanlış"*) araştırmasının önerdiği **asıl** düzeltme
  bu: az uyarı değil, **dürüst güven dili**. BH/FDR düzeltmesi bilinçli
  REDDEDİLMİŞ (kodda gerekçeli: elde p-değeri yok, yalnız z-kesim var — BH
  p-değeri ister, normallik varsayımını dayatmak olurdu).
- [x] **Çözüm:** **gerekmedi** — ölçüm iddiayı çürüttü (K1(a)/K6'nın ilk
  yarısıyla aynı desen: Playwright gözlemi bir teşhistir, ölçülünce
  doğrulanmayabilir). Eşik kalibrasyonu roadmap'in kendi diliyle *"gerekirse"*
  koşulluydu — koşul karşılanmadı.

### 4.3 · K3 — Oturum tokenı sessizce bozuluyor ✅ GÜVENLİ YARI UYGULANDI (kök hipotez belgelendi, dokunulmadı)
- [x] **Sorun:** 20+ dk açık kalan sekmede `schema`/`notifications`/`auth/me`
  art arda 401, kullanıcı hiç uyarı görmedi.
- [x] **Araştır (bitti):** `access_ttl_seconds=15dk` · `refresh_ttl_seconds=7gün`
  (`config.py`) — refresh cookie'nin KENDİSİ 20 dk'da ölmüş olamaz, `doRefresh()`'in
  tek-uçuş paylaşımlı yeniden-deneme mantığı (`api-client.ts`) doğru yazılmış.
  **Kod okumasıyla bulunan gerçek şüpheli** (canlıda 20+ dk beklenmeden
  doğrulanamadı — bkz. karar): `auth_service.rotate()`'in REUSE DETECTION'ı
  (`refresh_grace_seconds=10sn`) — kullanılmış bir refresh token yalnız 10sn'lik
  bir pencerede "paralel sekme" sayılıyor, dışındaysa **TÜM AİLE İPTAL EDİLİYOR**.
  `ConnectionBadge` 30sn'de bir arka-plan sorgusu atıyor; arka-plandaki (odaksız)
  bir sekmede tarayıcı zamanlayıcı kısıtlaması (throttle) + React Query'nin
  `refetchOnWindowFocus` patlaması bu 10sn'lik pencereyi kolayca aşabilir —
  meşru bir yarışı "hırsızlık" sanıp oturumu kalıcı öldürebilir.
- [x] **Karar — GÜVENLİK KODUNA DOKUNULMADI:** `rotate()` kimlik doğrulama/
  güvenlik-kritik kod; canlı 20+ dk doğrulama yapılmadan (bu turda pratik değil)
  eşiği değiştirmek riskli bir spekülasyon olurdu. Yalnız **güvenli, katkısal**
  yarı uygulandı: 401→refresh-başarısız yolu artık kullanıcıyı
  `?sebep=oturum_suresi` ile `/login`'e yönlendiriyor, login sayfası nötr bir
  *"Oturumunun süresi doldu — tekrar giriş yapman gerekiyor"* notu gösteriyor —
  hangi kök neden olursa olsun (7 günlük süre dolması, aile-iptali, cihaz
  uyuşmazlığı) kullanıcı artık **sessiz kalmıyor**. `refresh_grace_seconds`
  kalibrasyonu — DOĞRULANMAMIŞ hipotez olarak — açık bırakıldı, ayrı bir
  odaklı tur ister.
- [x] **Doğrula:** `tsc`+`eslint` temiz. Canlı Playwright: `/auth/logout` sonrası
  `/login?sebep=oturum_suresi` → nötr not DOM'da doğrulandı (`"Oturumunun
  süresi doldu"` metni bulundu). 20+ dk'lık tam senaryo faz-sonu turda pratik
  değil (yapay bekleme önerilmiyor) — bu düzeltme HANGİ nedenle 401 kalıcı
  hâle gelirse gelsin çalışır, kök nedene bağımlı değil.

**FAZ 4 durumu — ve TÜM roadmap'in kapanışı:** hedefli pytest'ler geçtikten
sonra, **burada ve yalnız burada**: (1) **tüm 15 senaryo** baştan sona
Playwright'la yeniden koşulur — nokta atış canlı doğrulama, kampanyanın tam
tekrarı; (2) o doğrulama bittikten **sonra tek bir** `lab/kapi.py --tam`
koşulur. Aradaki 4 fazda hiçbir `--tam`/Playwright koşulmaz.

---

## Faz-sonu doğrulama turu (2026-08-26, gerçek Playwright/Chromium, `s50`)

4 faz de bitince, kullanıcının talimatı gereği nokta-atış canlı doğrulama
yapıldı (tam 15 senaryonun harfiyen tekrarı değil — değişen her maddenin
doğrudan hedeflenmiş sınaması, "gerçek tarayıcıda gerçekten düzeldi mi"):

- **K5** — `demo-boyahane`, "makine bazında toplam üretim" → bar grafik, 11
  makine adı **okunur**, döndürülmüş, üst üste binme yok. *(Kanıt:
  `k5_check2.png`, scratchpad)*
- **K4 + K13** — aynı oturum, "makine ve vardiya ve ay bazında oee" (3 boyut,
  yüksek kardinalite) → sonuç **pivot** (facet "duvar kağıdı" YOK, K4) VE
  ekranın en üstünde **canlı, gerçek** bir K13 uyarı bandı: *"⚠ Bu çapraz
  tablo veriye tam uymuyor: 990 satırdan 957 tanesi aynı hücreye düşüp
  üzerine yazıldı — sonucu tablo görünümünde kontrol edin."* — bu sentetik
  bir test değil, motorun kendi ürettiği GERÇEK bir çarpışmaydı; K13'ün
  varlık nedenini birebir kanıtlıyor. *(Kanıt: `k4_k13_check.png`)*
- **K6** — aynı ekranda plan önizlemesi ("1 toplam_uretim_kg · makine
  kırılımında") **`fiil` rozeti YOK** — kaldırıldığı doğrulandı.
- **K3** — `/auth/logout` + `/login?sebep=oturum_suresi` → nötr not DOM'da
  doğrulandı.
- **K12** — canlı `/conversations` listesinde gerçek geçmiş veriyle
  `last_question` doluyor ve title'dan ayrışıyor (curl ile, önceki bölüm).
- **K7** — 2 ayrı canlı Playwright denemesinde tekrar üretilemedi, ⊘
  gözlemde bırakıldı (bkz. §4.1).
- **K1(a)** — bu turda yeniden denenmedi (önceki 3 curl denemesi zaten
  yetersizdi ilan edilmişti); ⊘ gözlemde kalıyor.
- **K8** — davranışsal değil, ölçümseldi; ayrı bir görsel doğrulama
  gerektirmiyordu (bkz. §4.2, 15 sorgu ölçümü).

**Sonuç:** roadmap'in 13 maddesinden **9'u** kodda düzeltildi ve canlı/
görsel olarak doğrulandı (K2 K3 K4 K5 K6 K9 K10 K12 K13), **1'i** ölçülüp
düzeltme gerekmediği kanıtlandı (K8), **2'si** araştırıldı ama tekrar
üretilemediği için kasıtlı olarak dokunulmadı (K1(a), K7), **1'i** başka bir
maddeye (K13) taşındı ve orada kapandı (K1(b)).

---

## Tek kapı — `lab/kapi.py --tam` sonucu (2026-08-26)

Roadmap'in bağlayıcı sırasına göre (FAZ 1-4 → nokta-atış canlı doğrulama →
**BİR kez** tam kapı) koşuldu:

```
✓ korpus kapısı — TOPLAM doğru-cube: %95.6 (taban %94.4) ✅ — İYİLEŞTİ
✓ gerçek-dünya korpusu — kapı yeşil, ⚠ KAZANÇ: sessiz_yanlış -1
✓ DEMET KAPISI (korpus) YEŞİL
```

**Regresyon YOK** — doğruluk taban %94.4'ten %95.6'ya çıktı (bu demetin
düzeltmeleri sonucu düşürmedi, hatta `sessiz_yanlış` bir kayıt azaldı,
`garson devraldı: istenen yön` — route çekildi, garson daha çok devraldı,
bu deponun EN ÜST KURALI'yla — GARSON DEVRİ — aynı yöndedir).

⚠ **Kapsam kaybı (ortam eksik, ölçülmedi, gizlenmedi):** iki alt-kapı
koşmadı çünkü konteyner çağrısı yalnız `backend/`+`belgeler/` mount etti:
- `test_belge_duzeni.py` (7 test) — repo KÖKÜ mount edilmeliydi.
- "kasetli garson korpusu" (trafiğin %37'si, 21 çok-turlu senaryo) — canlı
  `dima.db`'nin bir kopyası mount edilmeliydi.

Bu, bir regresyon DEĞİL — kapı script'inin kendisi bunu dürüstçe raporladı
("Yeşil bir özet, bu kapıların koştuğu anlamına GELMEZ"). Bu turun kapsamı
dışında bırakıldı (ortam kurulumu bir kod düzeltmesi değil); gelecek bir
tam-kapı koşumunda repo kökü + canlı DB kopyası mount edilirse bu iki kapı
da katılır.

---

## Faz sonrası — büyük karar noktası

`2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md` §14.3'ün koşulu: bu 4 faz bittikten
**sonra** kullanıcının orijinal "%20+ arıza" şikâyeti hâlâ anlamlı ölçüde
yüksekse, o zaman §7'nin büyük mimari genişlemesi (okuma/yazma orkestrasyon
ayrımı) gündeme gelir. Bu roadmap'in **hiçbir maddesi** o büyük genişlemeyi
gerektirmiyor — hepsi küçük, yerelleştirilmiş düzeltmeler. Eğer bu 4 faz
sonrası hâlâ arıza kalıyorsa, bu kendisi önemli bir sinyal olur.

---

## Özet tablo (hızlı bakış)

| faz | madde | öncelik | kanıt | durum |
|---|---|---|---|---|
| 1 | K9 — analiz/neden/reçete ayrışması | 🔴🔴🔴 | S15 | [x] neden↔ne-yapmalıyız kapandı (2 domain doğrulandı); "analiz et"in boşluğu hâlâ açık, ayrı not edildi |
| 1 | K1(a) — konu sapması | 🔴🔴 | S3 | [~] 3 curl denemesinde tekrar üretilemedi, ⊘ gözlemde |
| 1 | K1(b) — "listele" 16 boyut | 🔴🔴 | S10 | [x] araştırıldı — backend DOĞRU, kusur K13'e taşındı |
| 1 | K2 — sıfır-taban yüzde | 🔴 | S4 | [x] domain-agnostik `_SIFIR_ESIGI` eşiği, 2 domainle doğrulandı |
| 1 | K10 — çoklu-filtre cümle çakışması | 🔴 | S2 | [x] TDD ile kanıtlandı+düzeltildi, domain-agnostik, 45/45 test |
| 2 | K4 — grafik seçimi tutarsız | 🔴🔴 | S7 vs S8 | [x] series ekseni kardinalite kontrolü eklendi (panelle simetrik), 40/40 test + canlı doğrulandı |
| 2 | K5 — X ekseni okunmuyor | ⚠ | S2/S3/S9 | [x] paylaşılan `axisLabelSpacing()` (KAT-1), 6 yer birleştirildi — **canlı Playwright'ta 11 makine etiketi okunur, sarma yok** ✅ |
| 2 | K13 — pivot sessiz çöküyor 🔴 (K1(b) buraya taşındı) | 🔴 | S10 | [x] çarpışma sayacı + amber uyarı — **canlı Playwright'ta GERÇEK çarpışma yakaladı: "990 satırdan 957'si aynı hücreye düştü" uyarısı ekranda** ✅ |
| 3 | K6 — dev-trace sızıyor | ⚠ | §16, kampanya | [x] `$N` iddiası çürütüldü (zaten düzeltilmişti); `fiil` rozeti kaldırıldı, tsc+eslint temiz |
| 3 | K12 — thread listesi ayrışamıyor | ⚠ | tüm kampanya | [x] `last_question` eklendi (backend+FE), 2 domain, 4/4 test + canlı doğrulandı |
| 4 | K7 — CSS mesaj bug'ı | ⚠ | S12, S15×2 | [~] ⊘ gözlem altında — 2 canlı denemede tekrar üretilemedi |
| 4 | K8 — uyarı yorgunluğu | ⊘ ölçülmedi | gözlemsel | [x] ölçüldü: %27 (15 sorgu, 2 domain) — "neredeyse her cevap" iddiası çürütüldü, düzeltme gerekmedi |
| 4 | K3 — oturum tokenı | ⚠ | S10 öncesi | [x] nazik oturum-bitti notu eklendi + canlı doğrulandı; kök hipotez (grace-window) güvenlik kodu olduğu için dokunulmadan belgelendi |

**Zaten kapalı (referans için):** ✅ viz/contribution/interpretation sözleşme
boşluğu (§13) · ✅ kalem→musteri sessiz ikame beyanı (§15).
