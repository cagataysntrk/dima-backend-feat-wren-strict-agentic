# Playwright Canlı Test Kampanyası

> Bu belge **ayrı** tutuluyor — `2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md` (teorik
> araştırma + §13/§15 düzeltmeleri) değişmeden kalıyor. Burada: gerçek tarayıcı
> (Playwright/**Chromium**, sistem Chrome'daki başka bir ajanla çakışmasın diye),
> repodaki **gerçek, çok-turlu kullanıcı senaryoları** (`backend/lab/deneyim.py::
> SENARYOLAR`, 14 senaryo, "basitten komplekse / kısadan uzuna / zincirleme") tek
> tek koşulup hem **veri/motor** hem **UI/UX** tarafı raporlanıyor.

**Kurulum:** backend `dima-oneri-8002` (imaj `s44`, §13+§15 düzeltmeleriyle),
frontend `pnpm dev` (`:3000`), hesap `demo-boyahane@usedima.com`.

**Skala:** ✅ sorunsuz · ⚠ çalışıyor ama kusurlu/eksik · 🔴 gerçek arıza.

---

⚠ **Kapsam notu:** 14 senaryodan 13'ü koşuldu (12 tam + `analist_turu` ilk turda
atlanmış, kullanıcının uyarısıyla **sonradan tam koşuldu** — aşağıda madde 15);
`geri_donus`un checkpoint'e tıklama turu ve `kiyas_turu`nun son 2 turu (zaman
kısıtından) manuel UI etkileşimi gerektirdiği için atlandı — otomatik script
yalnız metin girişini kapsıyor. Ayrıca bir turda oturum tokenı süresi doldu
(20+ dk açık kalan sekme), yeniden giriş yapılarak devam edildi — bu kendisi
bir bulgu (§ Ortak Kök Sorunlar → K3).

🔴 **Öz-eleştiri:** İlk yazımda tam olarak *"neden böyle/ne yapmalıyız" gibi
konuşma-analiz cevaplarını arayan kullanıcılara cevap yok*du — `analist_turu`
(bu tür soruların asıl senaryosu) baştan **hiç koşulmamıştı**, yalnız başka
senaryolarda TIKLANMAMIŞ chip olarak görülmüştü. Kullanıcı bunu fark edip
sordu. Bu, kampanyanın kendi ölçütü ("gerçek kanıt, tıklanmamış bir chip'in
varlığı değil") gereği düzeltildi — §15'te.

---

## Senaryo sonuçları

| # | senaryo | turlar | veri/motor | UI/UX | görsel |
|---|---|---|---|---|---|
| 1 | **sosyal_isten_ise** | merhaba→oee→teşekkürler→iyi çalışmalar | ✅ sosyal turlar 0-maliyet, doğru | ✅ temiz | `s1_sosyal_isten_ise_v2.png` |
| 2 | **grafik_ustunde** | 6 ay fire→yorumla→en kötü ay→o ayı aç | ⚠ tarih beyanı üç filtre üst üste binip **okunmaz** cümle oldu | ⚠ | `s2_grafik_ustunde.png` |
| 3 | **donem_duzeltme** | oee→bu yıl→"yok ya son 3 ay"→aylık→en düşük | 🔴 **konu tamamen saptı** (OEE→renk/fire), süreklilik koptu | 🔴 | `s3_donem_duzeltme.png` |
| 4 | **belirsizlik** | bakiye→(chip)→aylara göre | ✅ şeffaf ("başka tanım" chip'i) ama 🔴 "₺0→₺0 iken %100 arttı" mantıksız cümle | ⚠ | `s4_belirsizlik_t1.png` / `_final.png` |
| 5 | **kompozisyon** | oee→fire ekle→analiz et | ✅ 2 ölçü doğru birleşti (scatter) | ✅ "açıklama AI ürünü, sayı küpten" notu örnek | `s5_kompozisyon.png` |
| 6 | **konu_degisimi** | oee→ciro→aylara göre→oee'ye dön→vardiya | ✅ süreklilik korundu, doğru geri döndü | ⚠ grafik üstte kesik | `s6_konu_degisimi.png` |
| 7 | **atif_ifadesi** | oee→"az önce dediğin gibi"→"yukarıdaki raporu…" | ✅ atıf doğru çözüldü | ✅ **heatmap mükemmel okunur** | `s7_atif_ifadesi.png` |
| 8 | **geri_donus** (kısmi) | oee→vardiya→aylık (checkpoint atlandı) | ✅ veri doğru | 🔴 **3-boyutlu bar chart tamamen okunamaz** ("duvar kağıdı") | `s8_geri_donus_pre.png` |
| 9 | **eylem_onerisi** | oee→zamanla→panoya ekle | ✅ SQL uydurmadı, ikisi de ONAY istedi | ✅ net onay kutuları | `s9_eylem_onerisi.png` |
| 10 | **liste_niyeti** | partileri listele→en çok fire vereni üste al→ilk 5 | 🔴 **"listele" 16-boyutlu kırılıma saptı**, 1000 satır 1 hücreye sıkıştı | 🔴 kullanılamaz pivot | `s10_liste_niyeti.png` |
| 11 | **kapsam_disi** | personel verimliliği→makine bazında? | ✅ dürüst ret ("hangi ölçü?") + doğru takip | ✅ | `s11_kapsam_disi.png` |
| 12 | **uretim_muduru_sabahi** | günaydın→…→zamanla→teşekkürler (7 tur) | ✅ 7 tur boyunca süreklilik korundu | 🔴 kullanıcı mesajı dikey/kelime-kelime render edildi (CSS) | `s12_uretim_muduru_sabahi.png` |
| 13 | **yazim_hatali_gercek_kullanici** | "bu yil makina bazinda oee"… (yazım hatalı) | ✅ hiç sorun çıkarmadı, tam doğru anlaşıldı | ✅ | `s13_yazim_hatali.png` |
| 14 | **kiyas_turu** (kısmi) | oee→(kıyasla/analiz turları atlandı) | ⊘ ölçülemedi | ⊘ | `s14_kiyas_turu.png` |
| 15 | **analist_turu** *(sonradan koşuldu)* | oee→bunu analiz et→bu neden böyle?→ne yapmalıyız?→peki fire ne durumda? | 🔴🔴 **üç ayrı arıza aynı senaryoda** — bkz. altta | 🔴 CSS tekrar | `s15/16/17/18_*.png` |

**Skor (15 senaryo):** 6 tam ✅ · 4 kısmen ⚠ · 4 gerçek 🔴 arıza · 1 ⊘ eksik ölçüm.

### Senaryo 15 detayı — "konuşma-analiz" turları (kullanıcının işaret ettiği tam nokta)

| tur | beklenen (S2_ANLAT sözleşmesi) | gerçekleşen |
|---|---|---|
| **"bunu analiz et"** | olgu + anlatı + devam chip'i | 🔴 **hiç yazılı analiz metni yok** — yalnız `▶ deterministik küp` (kapalı iz) + çıplak grafik |
| **"bu neden böyle?"** | kök-neden teşhisi | ✅ **çok iyi**: akran kıyaslı, çok değişkenli teşhis ("RAM-3 öteki 10 makine ort'dan %10,7 düşük; en çok açıklayanlar: fire +%62,3, performans −%9,1, ilk seferde tamam −%2,6") |
| **"ne yapmalıyız?"** | reçete/aksiyon önerisi | 🔴 **"bu neden böyle?" ile BİREBİR AYNI metin** — hiç reçete/aksiyon üretilmedi, soru farklı niyet sınıfına düşmedi |
| **"peki fire ne durumda?"** | konu geçişi + doğru küp | ✅ iyi: cevap geldi **ve** kendi belirsizliğini beyan etti — *"⚠ Sayı doğru ama eksik: soruda «fire» geçiyor ve bu katalogda `parti` konusudur — ama bu cevap `OEE` küpünden geldi… «fire» birden fazla yerde tanımlı, diğerleri: fire (parti)."* |

**Bu tek senaryo başlı başına üç ayrı, isimlendirilebilir arıza üretti** (K9, K10
altta) — hem veri/motor hem UI tarafında. Kullanıcının sezgisi doğruydu: bu tür
sorular gerçekten test edilmemişti ve gerçekten kırıktı.

---

## Ortak kök sorunlar

*(Önceki araştırmayla — `2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md` §10-16 —
ilişkilendirilerek.)*

### VERİ/MOTOR tarafı

**K1 — Niyet ayrıştırma, DAR bir isteği GENİŞ bir işleme büyütüyor.**
`donem_duzeltme` (konuşma-dili dönem düzeltmesi → konu tamamen değişti, OEE'den
fire'a sıçradı) ve `liste_niyeti` ("en çok fire vereni üste al" → 16 boyutlu
kırılıma büyüdü, kullanılamaz tek-hücreli pivot) **aynı ailenin** iki üyesi: kısa,
eliptik bir konuşma-dili ifadesi geldiğinde sistem onu **önceki bağlamın küçük bir
düzeltmesi** olarak değil, **yeni/geniş bir işlem** olarak okuyor. Bu, önceki
araştırmanın §10-11'de ölçtüğü "kalem→musteri sessiz ikame"siyle **aynı kök
aileden** — üçü de §2'nin teorik "açık dünya↔kapalı şema" bulgusunun canlıda
tekrar tekrar somutlaşmış hâli.

**K2 — Sıfır-taban yüzde hesapları yanlış cümle üretiyor.**
`belirsizlik` senaryosunda ölçüldü: *"bakiye: Oca 2026→Tem 2026 %100,0 arttı
(₺0 → ₺0)"* — matematiksel olarak tanımsız (0'dan 0'a "artış" yoktur), ama sistem
bunu "%100 arttı" diye **yanlış bir sayı** olarak sunuyor. Bu, tek bir vakada
görüldü ama sıfırdan başlayan HER seri için tekrarlanabilir bir hata sınıfı olma
ihtimali var — ölçülmedi, yalnız gözlendi.

**K3 — Oturum tokenı sessizce bozuluyor.**
20+ dakika açık kalan sekmede `schema`/`starters`/`auth/me`/`notifications` art
arda `401` verdi, kullanıcı hiçbir uyarı görmedi. Uzun bir çalışma oturumu
("üretim müdürünün sabahı" gibi) sırasında arka plan özelliklerinin sessizce
ölmesi riski var.

**K9 — "Konuşma-analiz" niyetleri (analiz et / neden / ne yapmalıyız) birbirinden
AYRIŞMIYOR.** 🔴🔴 En önemli yeni bulgu (S15, kullanıcının doğrudan işaret ettiği
nokta). Üç farklı niyet üç farklı davranış gerektirir — genel özet, nedensellik,
reçete — ama ölçülen:
- *"bunu analiz et"* (genel) → **boş**: yalnız grafik, hiç yazılı olgu/anlatı yok.
- *"bu neden böyle?"* (nedensellik) → **çok iyi**, gerçek çok-değişkenli teşhis.
- *"ne yapmalıyız?"* (reçete) → **"neden" ile birebir aynı metin**, hiç aksiyon/
  öneri üretilmedi — soru kendi niyet sınıfına hiç düşmedi.
Üçü de aynı görünür yüzeyde (bir metin kutusuna yazılan soru) ama arkada üç
ayrı yeteneğe bağlanıyor ve ikisi (analiz/reçete) bağlanmıyor. `AskResponse`da
zaten `prescription` diye ayrı bir alan var (§ önceki araştırma, `schemas.py`) —
yani sözleşme muhtemelen orada, doldurulması ayrı bir konu (§13/§15'teki
"eksik doldurma" deseninin üçüncü örneği olabilir, doğrulanmadı).

**K10 — Çoklu-filtre/dönem açıklaması tekilleştirilmeden art arda ekleniyor,
okunmaz cümle oluyor.** `grafik_ustunde` (S2) senaryosunda ölçüldü: *"Bu değer
fire ölçüsünün 2026-02-25 tarihinden itibaren VE 2026-04-01'den itibaren VE
2026-05-01 tarihli VE month bazında zaman kırılımlı makine bazında
kırılımıdır."* Üç farklı tarih/filtre ifadesi cümle şablonuna ARKA ARKAYA
eklenmiş, birbirini geçersiz kılan/çakışan bir cümle üretmiş — bu K2'den ayrı
bir kusur (K2 matematiksel yanlışlık, K10 dilbilgisel/mantıksal çakışma).

### UI/UX tarafı

**K4 — Grafik seçim motoru çok-boyutlu kırılımda TUTARSIZ.**
Aynı türden veri (makine×vardiya) bir bağlamda (`atif_ifadesi`, S7) **mükemmel**
bir heatmap oldu; neredeyse aynı veri başka bir bağlamda (`geri_donus`, S8 —
üçüncü boyut olarak AY eklenince) **tamamen okunamaz** bir çoklu-renkli-çubuk
"duvar kağıdı"na döndü. Motor doğru kararı **verebiliyor** (S7 kanıtı) — sorun
yetenek eksikliği değil, **tutarlılık** eksikliği: üçüncü boyut (zaman) eklenince
karar bozuluyor.

**K5 — X ekseni etiketleri yüksek kategori sayısında okunmuyor.**
En az 3 senaryoda (S2, S3, S9'un ilk hâli) tekrarlandı — 11 makine gibi kalabalık
kategorilerde etiketler üst üste biniyor. §16'da (bir önceki bulgu) da aynı desen
görülmüştü — sistemik.

**K6 — Dev-trace bazı yollarda hâlâ ana içerik.**
§16'nın bulgusu bu kampanyada da örtük doğrulandı (`+SQL GÖSTER`, `ANLAT —
kaynaklar=$1,$2` gibi ifadeler varsayılan görünümde).

**K7 — CSS/layout kırılganlığı — 🔴 SİSTEMİK, izole değil (3 bağımsız kanıt).**
İlk gözlemde ("her pazartesi bu raporu bana yolla", 6 kelime) izole bir bug
sanılmıştı. `analist_turu`da (S15) **iki kez daha** tekrarladı: *"bunu analiz
et"* (3 kelime) ve *"peki fire ne durumda?"* (4 kelime) — ÜÇÜ de kullanıcı
mesajını **kelime kelime dikey** render etti. Üç farklı uzunlukta (3, 4, 6
kelime), üç farklı senaryoda, aynı desen — bu artık bir kenar durumu değil,
kullanıcı mesajı balonunun CSS'inde **genel bir kırılma** (muhtemelen
`flex-direction`/`white-space` ile ilgili).

**K8 — Olası uyarı yorgunluğu.**
Anomali tespiti (z-score tabanlı) neredeyse **her** cevapta bir turuncu kutu
üretti. Sıklığı ölçülmedi ama gözlemsel olarak yüksek — her şey "olağandışı"
işaretlenirse hiçbir şey olağandışı görünmez.

**K12 — Sol panel (thread listesi) neredeyse-aynı başlıklarla dolup
ayrışamıyor.** Bu kampanya boyunca **"bu yıl makine bazında oee"** başlığı
**4 kez ayrı, birbirinden ayırt edilemeyen** kart olarak belirdi (satır sayısı
ve mesaj sayısı dışında hiçbir ayrım yok — ne zaman damgası, ne önizleme).
Gerçek bir kullanıcı 12+ threadlik bir günün sonunda hangi kartın hangi
konuşma olduğunu **bulamaz**. Bu, K1'in (backend'in konuyu yanlış
sınıflandırması) **UI tarafındaki yansıması** — backend sık sık yeni thread
açıyor, arayüz de bunu ayrıştırmaya yardımcı olacak hiçbir ipucu vermiyor.

**K13 — Pivot/tablo görünümü, veriye uymadığında hiç uyarmıyor.**
`liste_niyeti` (S10): 1000 satırlık bir sonuç, pivot görünümünde **tek bir
hücreye** çöktü — ve arayüz bunu **sessizce**, sanki normalmiş gibi gösterdi.
Backend'in yanlış kırılım seçmesi (K1) bir şey; UI'ın "bu görünüm bu veri için
anlamsız, tabloya geç" diye **hiç uyarmaması** ayrı, bağımsız bir kusur —
K1 düzeltilse bile UI'ın kendisi böyle bir sessiz-anlamsızlık durumuna karşı
korumasız kalır.

### Ne İYİ çalışıyor — dengelemek için (silinmesin)

Beyan kültürü (ADR-0020) fiilen çalışıyor ve iyi örnekleri var: "başka tanım"
chip'i (belirsizlik), "açıklama metni yapay zeka ürünü — sayılar küpten gelir"
notu (kompozisyon), "ort_oee toplanabilir değil, dönem trendi yazılmadı" dürüst
reddi (konu_degisimi, atif_ifadesi), "hangi ölçüyü istiyorsun" (kapsam_disi),
SQL uydurmadan ONAY isteyen eylem akışı (eylem_onerisi). Yazım hatalarına karşı
tam dayanıklılık (yazim_hatali). 7 turluk bir threadde süreklilik hiç kopmadı
(uretim_muduru_sabahi). "Bu neden böyle?" sorusuna gerçek, çok değişkenli bir
kök-neden teşhisi geldi ve *"«fire» birden fazla yerde tanımlı, bu cevap OEE
tanımıyla hesaplandı"* diye kendi belirsizliğini beyan etti (analist_turu, S15).
Bunlar **rastlantı değil**, disiplinin sonucu.

### Kapsam doğrulaması — her bulgu bir köke bağlandı mı

| kaynak | bulgu | kök |
|---|---|---|
| S2 | tarih beyanı okunmaz cümle | K10 |
| S3 | konu tamamen saptı | K1 |
| S4 | ₺0→₺0 iken %100 arttı | K2 |
| S8 | 3-boyutlu grafik okunamaz | K4 |
| S9-S12 (dev-trace görünürlüğü) | ana içerikte iz sızması | K6 |
| S2/S3/S9 | X ekseni okunmuyor | K5 |
| S10 | listele → 16 boyuta büyüdü | K1 |
| S12, S15×2 | kullanıcı mesajı dikey render | K7 |
| (gözlemsel, tüm senaryolar) | anomali kutusu sık tetikleniyor | K8 |
| S15 | "analiz et" boş / "ne yapmalıyız" kopya | K9 |
| tüm kampanya boyunca (sol panel) | "bu yıl makine bazında oee" 4 kez ayırt edilemez kart | K12 |
| S10 | pivot 1000 satırı sessizce 1 hücreye çökertti | K13 |
| §10-11 (önceki araştırma) | kalem→musteri sessiz ikame | K1 ile aynı aile |
| §13 (önceki araştırma) | viz/contribution sözleşme boşluğu | K9 ile aynı desen ("eksik doldurma") |

Kapsanmayan tek şey: `kiyas_turu`nun "geçen yılla kıyasla"/"bunu analiz et"
turlarının sonucu (zaman kısıtından ekran görüntüsü alınamadı) — bu **açık**
bırakıldı, K9'un kapsamına girip girmediği doğrulanmadı.

---

## Kök çözüm önerileri (uygulanmadı — bu belge yalnız rapor)

### Veri/motor

| # | K | öneri |
|---|---|---|
| Ç1 | K1 | Konuşma-dili "küçük düzeltme" kalıpları ("yok ya sadece…", "üste al", "ilk N'i") niyet ayrıştırmada **önceki bağlamın değişikliği** olarak önceliklendirilsin — yeni-konu/geniş-kırılım moduna düşmeden önce "bu, mevcut sorgunun küçük bir varyasyonu mu" sınaması yapılsın. |
| Ç2 | K1 | `SIRALA`/liste niyeti ile `AYRISTIR`/kırılım niyeti **ayrı sınıflandırılsın** — "üste al"/"en çok…olanı" bir sıralama operatörüdür, yeni bir kırılım boyutu değil. |
| Ç3 | K2 | `interpret()`'in yüzde-değişim hesabı sıfır-taban durumunu özel ele alsın (0→0 = "değişim yok", 0→X = "yeni ortaya çıktı" — %100/%sonsuz gibi yanlış sayı üretilmesin). |
| Ç4 | K3 | Token yenileme mekanizması canlıda test edilsin; sessiz 401 furyası yerine ya otomatik arka-plan yenileme ya da kullanıcıya nazik bir bildirim. |
| Ç10 | K9 🔴🔴 | **En yüksek öncelikli** — "analiz et" (genel özet) / "neden" (nedensellik) / "ne yapmalıyız" (reçete) ayrı niyet sınıflarına düşürülsün. Önce ölçülsün: `prescription` alanı (`schemas.py`) hiç mi doldurulmuyor yoksa yalnız bu yoldan mı ulaşılamıyor — §13/§15'teki "sözleşme var, doldurma eksik" deseninin üçüncü örneği olabilir. |
| Ç11 | K10 | Dönem/filtre açıklama cümlesi kurulurken çakışan/art arda eklenen ifadeler **tekilleştirilsin** (son geçerli filtre kazansın, ya da tek bir birleşik aralık cümlesi kurulsun). |

### UI/UX

| # | K | öneri |
|---|---|---|
| Ç5 | K4 | `viz.recommend`'in 3+ boyutlu karar kuralı gözden geçirilsin — 2 boyutta zaten doğru (S7 kanıtı); üçüncü boyut (özellikle zaman) eklendiğinde küçük-çoklular (her biri kendi heatmap'i) ya da zaman kaydırıcısına düşülsün, düz çubuğa değil. |
| Ç6 | K5 | X ekseni etiket stratejisi (döndürme/kısaltma/örnekleme) kategori sayısına göre uyarlansın. |
| Ç7 | K6 | Dev-trace (`SORGU/AYRISTIR/GORSEL/ANLAT`, `$1/$2`) varsayılan gizli olsun, yalnız isteğe bağlı "nasıl hesaplandı" panelinde görünsün — bu zaten önceki turda (§16) not edilmişti, burada bağımsız olarak tekrar doğrulandı. |
| Ç8 | K7 | Kullanıcı mesajı render'ı için görsel regresyon testi eklensin (özellikle çok kelimeli girdiler). |
| Ç9 | K8 | Anomali uyarısının tetiklenme sıklığı ölçülsün; her cevapta çıkıyorsa eşik kalibre edilsin. |
| Ç12 | K12 | Thread kartlarına zaman damgası ve/veya kısa bir sonuç önizlemesi (ör. son cevabın ilk cümlesi) eklensin — aynı başlıklı kartlar ayrışabilsin. |
| Ç13 | K13 | Pivot/tablo bileşeni, sonuç veriye "uymadığında" (ör. tek hücreye çöken bir pivot) sessiz kalmak yerine **kendi başına** uyarsın veya otomatik tabloya düşsün — K1'in backend düzeltmesinden **bağımsız**, ayrı bir UI-savunması. |

**Sıralama önerisi (güncellendi):**
1. **Ç10 (K9)** — "neden/ne yapmalıyız/analiz et" üçlüsü ürünün **omurgası**
   (analist_turu senaryosunun adı bile bunu söylüyor); "ne yapmalıyız"ın
   "neden"in kopyası olması, kullanıcının **hiç fark etmeden** yanlış bilgiyle
   hareket etmesi riski taşır — sessiz ikameden (§10-11) bile daha kritik
   çünkü burada yanlışlık hiç beyan edilmiyor.
2. **Ç1/Ç2 (K1)** — en sık karşılaşılacak arıza sınıfı (konuşma-dili düzeltme/
   liste isteği).
3. **Ç5 (K4)** — "grafik bazen okunmuyor" güveni doğrudan kırıyor.
4. Geri kalanı (Ç3/Ç4/Ç6/Ç7/Ç8/Ç9/Ç11) küçük, izole, paralel yapılabilir.
