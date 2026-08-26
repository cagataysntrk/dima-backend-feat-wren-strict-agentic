# Mimari Çıkmaz Araştırması

> Bu belge bir **geliştirme** kaydı değil — mimarinin çıkmaza girip girmediğini
> objektif olarak değerlendirmek için başlatılan bir **araştırma/eleştiri**
> oturumunun kaydıdır. Aşamalar sırayla eklenir: önce vizyon (ne yapılmak
> isteniyor), sonra ona karşı ölçülen sorunlar, sonra tartışma.

---

## §1 — ÜRÜN VİZYONU: TEMEL ÖZELLİKLER (inşa durumundan bağımsız, "ne yapar")

İnşa edilmiş/edilmemiş ayrımı yok — burada yalnız **DİMA'nın olmak istediği şey**.

1. **Doğal dilde soru-cevap** — kullanıcı Türkçe soru sorar (*"geçen ay RAM-3'te
   fire ne kadar?"*), sistem cevabı **semantik küpten** üretir. Rakamı LLM asla
   yazmaz; LLM yalnız soruyu anlar, sayıyı hiçbir zaman.

2. **Kök neden / derinlemesine analiz** — bir sayı "neden öyle çıktı" sorusuna
   kırılım ve katkı analiziyle cevap verir (drill-down, contribution).

3. **Kişisel dashboard** — kullanıcı kendi gösterge panelini kurar, widget
   ekler/çıkarır, geri alabilir; sabit rapor değil, kendi çalışma alanı.

4. **Öngörü ve karar desteği (agentic)** — sistem yalnız geçmişi anlatmaz,
   *"şunu yaparsan ne olur"* türü çok adımlı plan üretir, kullanıcı onaylar
   (bir tık), sistem uygular. Karar **kullanıcıda** kalır, sistem tahmin eder.

5. **Proaktif öneri motoru** — kullanıcı her seferinde soru yazmak zorunda
   değil; sistem bir sonraki anlamlı soruyu/aksiyonu kendisi önerir (pill'ler).

6. **Kendi veriyle anında başlama** — kullanıcı kendi Excel/CSV'sini veya
   veritabanını bağlar, aynı gün üstünde soru sorabilir (oturum-scoped
   oto-cube veya kalıcı bağlantı sihirbazı).

7. **Zamanlanmış / otomatik raporlama** — düzenli aralıklarla rapor üretir,
   ilgili kişiye bildirir; kullanıcı her seferinde sormak zorunda kalmaz.

8. **Paylaşım ve işbirliği** — bir bulguyu link ile başka birine gösterebilme
   (yönetici, ekip arkadaşı) — DİMA'nın dışına çıkmadan.

9. **Denetlenebilirlik / kanıt** — her cevabın nereden geldiği, hangi sorguyla
   üretildiği kayıt altında ve **tekrar oynatılabilir** (audit trail,
   query contract). Kullanıcı sisteme güvenmek zorunda değil, doğrulayabilir.

10. **Metrik yönetişimi** — yeni bir iş metriği önce "aday" olarak denenir,
    etkisi (blast-radius) görülür, sonra resmileştirilir. Metrik tanımı
    keyfi değil, denetimli bir süreçten geçer.

11. **Güvenlik ve erişim katmanı** *(vizyon)* — kimin neyi görebileceğinin
    satır/kolon seviyesinde kontrolü; kurumsal ortamda "herkes her şeyi
    görür" olmaz.

12. **Çoklu şirket / çoklu sektör ölçeklenme** *(vizyon)* — aynı motorun farklı
    şirketler ve sektörler için yeniden kullanılabilmesi (tek kod tabanı,
    çok kiracı).

13. **Konuşma hafızası ve takip** *(vizyon)* — "bunu takip et", benzer
    dönemleri/şirketleri karşılaştır, önemli bir KPI'ı sabitle (pin);
    oturum tek seferlik değil, süregelen bir çalışma ilişkisi.

14. **Kanal genişlemesi** *(vizyon)* — DİMA'ya yalnız kendi arayüzünden değil,
    zaten kullanılan araçlardan (Slack/WhatsApp) erişilebilmesi.

15. **Optimizasyon motoru** *(vizyon)* — "ne oldu"nun ötesinde "en iyisi ne
    yapılmalı" sorusuna cevap verir: kısıt altında optimum kaynak/karar
    önerisi çıkarır (fiyat, stok, kapasite, kaynak dağılımı).

16. **McKinsey-düzeyi stratejik analiz** *(vizyon)* — ham veriyi değil,
    yönetim kurulu seviyesinde karar gerektiren sentezlenmiş içgörü üretir:
    fırsat/risk haritası, rakip kıyası, büyüme kaldıraçları.

17. **Yol haritası üretimi** *(vizyon)* — bir hedefe (büyüme, maliyet,
    verimlilik) ulaşmak için adım adım, önceliklendirilmiş bir eylem planı
    çıkarır — tek cevap değil, çok adımlı bir strateji.

18. **Senaryo simülasyonu** *(vizyon)* — "eğer X olursa" sorularını çok
    değişkenli koşturup sonuç aralığını gösterir (what-if, duyarlılık
    analizi), tek nokta tahmin değil.

19. **Kurumsal hafıza — şirketin beyni** *(vizyon)* — geçmiş kararları,
    sonuçlarını ve bağlamı kalıcı tutar; DİMA tek seferlik soru-cevap aracı
    değil, şirketin biriken bilgisini taşıyan **sürekli** bir hafıza
    katmanıdır — her yeni soru bu hafızanın üstüne kurulur.

20. **Ticari/danışmanlık katmanı** *(vizyon — ürünün ötesinde, iş modeli)* —
    DİMA'nın kendisini bir yazılım ürünü olarak satmanın ötesinde, veriye
    dayalı strateji/danışmanlık sunan bir katman olması.

---

---

## §2 — KÖK TEORİK SORUN: DETERMİNİZM İLE DOĞAL DİL ANLAMA ARASINDAKİ GERİLİM

*(Kod taraması değil — bu bölüm düşünsel/teoriktir. §3'teki kod bulguları
buradaki gerilimin **gölgesidir**, sebebi değil.)*

**Temel iddia:** DİMA'nın gerçek sorunu bir uç nokta eksikliği değil, şudur —
**insan dili ile deterministik makine dili arasında, ilke gereği, kayıpsız bir
eşleme yoktur.** Bu proje bu gerginliği çözmedi, **taraf seçti**: her zaman
doğru olmayı (soundness), her şeyi anlayabilmenin (completeness) önüne koydu.
Bu doğru bir seçimdi — ama bir seçim olduğu için, doğası gereği bir **bedeli**
var ve o bedel §1'in en iddialı maddelerinde ödeniyor.

**Neden kayıpsız eşleme yok — üç ayrı sebep:**

1. **Açık dünya ↔ kapalı dünya.** Doğal dil sınırsız üretkendir — kullanıcı
   şeması olmayan herhangi bir şeyi sorabilir. Küp ise tanım gereği **kapalı**
   bir dünyadır: yalnız önceden tanımlanmış ölçü/boyut/fiil kümesi vardır.
   Kapalı bir sistemi açık bir girdiye karşı **tam** kapsamlı yapmak, sonlu
   kural kümesiyle **imkânsızdır** — her yeni kural yeni bir istisna yüzeyi
   açar (proje bunu ampirik olarak zaten üç kez ölçtü: `cube_router` büyümesi,
   "yazılmış ama bağlanmamış" beş kez tekrar eden kusur, Türkçe morfoloji
   silahlanma yarışı — `backend/CLAUDE.md`'nin *"morfoloji kuralı
   `cube_router`'a eklenmez"* maddesi bu yarıştan çekilme kararıdır, çözüm
   değil).

2. **Sembol-referans kopukluğu (symbol grounding).** "Fire" kelimesi bir
   şirkette bir tanıma, başka bir şirkette başka bir tanıma karşılık gelir;
   "geçen ay" kelimesinin referansı konuşma anına, kullanıcının zihnindeki
   takvime bağlıdır. Kelimeler kendi başlarına anlam taşımaz, **bağlamla**
   taşır. Sistem bu bağlamı sabit bir kural listesiyle (`KURAL_*` —
   `context.py`'nin kendi tabiriyle *"anlama değil muhasebe"*) yakalamaya
   çalışıyor; ama bağlam sonsuz, kural listesi sonlu. Bu, madde 12'de
   (`cube_router` şirket-körü) somut olarak ölçüldü — teorik sebebi budur.

3. **Anlama üretkendir, hesaplama değildir.** "Neden," "en iyisi ne,"
   "olsaydı ne olurdu" gibi sorular **sentez** ister — birden fazla olguyu
   birleştirip yeni, önceden var olmayan bir yargı üretmek. Deterministik bir
   sistem yalnız **önceden tanımlı** bir işlemi (toplama, kırılım, kural
   eşleştirme) çalıştırabilir; sentez üretmez, arar/hesaplar. LLM'i bu işe
   koşmak sentezi mümkün kılar ama determinizmi anında kırar — bu yüzden
   `ANLAT` fiili "LLM YOK" diyor ve `§2.0.3` `iki_cube`'u reddediyor: bunlar
   birer eksiklik değil, **teoremin doğal sonucu**.

**Vizyondaki tezahürleri (madde numarasıyla, gerilim şiddetine göre):**

| şiddet | madde | tezahür |
|---|---|---|
| 🔴🔴🔴 en yüksek | 15-18 (optimizasyon, strateji, yol haritası, senaryo) | doğrudan **sentez** istiyor — deterministik sistemin tanım gereği yapamayacağı şey |
| 🔴🔴🔴 en yüksek | 19 (şirket beyni) | hem sentez (madde 4/16 gerilimi) HEM kalıcı bağlam (aşağıdaki 13) — ikisinin **kesişimi** |
| 🔴🔴 yüksek | 4 (agentic karar desteği) | plan üretimi sentez istiyor; proje bunu zaten sezip **O2/O3** ile "tahminci, karar verici değil" diyerek sınırlamış — doktrin, gerilimin **itirafıdır** |
| 🔴🔴 yüksek | 13 (konuşma takibi) | "bunu," "geçen sefer" gibi gönderim (anaphora) çözümü bağlam ister; sunucu bilerek durumsuz — zaman ekseninde aynı kapalı-dünya sorunu |
| 🔴 orta | 12 (çoklu şirket/sektör) | aynı ambiguite sorunu, **N şirket** için aynı anda — sonlu kural × sonsuz bağlam çarpımı |
| 🔴 orta | 5 (öneri motoru) | "sıradaki anlamlı soru" bir **alaka** yargısıdır (fuzzy); RRF/leksik-vektör füzyonuyla yaklaşık taklit ediliyor — §77-85'in bitmeyen ayar ihtiyacı bu yaklaşıklığın belirtisidir |
| 🔴 orta | 2 (kök neden) | "neden" kelimesi hem **istatistiksel** kırılımı hem **nedensel** mekanizmayı çağrıştırır; sistem yalnız birincisini verir, kullanıcı beklentisiyle sessiz bir uyumsuzluk var |
| 🟡 düşük | 6 (veri bağlama), 10 (metrik yönetişimi) | şema/metrik **anlamını** ham başlıktan çıkarmak küçük ölçekli aynı problem — bu yüzden hâlâ insan onayı (candidate→approve) araya giriyor |
| ⚪ yok/az | 3, 7, 8, 9, 11, 14, 20 | dil-anlama sorunu değil, mühendislik/erişim/iş modeli sorunu |

**Kritik gözlem:** Proje bu gerilimi hiç isimlendirmeden **iki kez** kendiliğinden
keşfetmiş ve doğru tepki vermiş — (a) §3.1'in rol değişikliği doktrini ("route
ve garson TAHMİNCİ, kullanıcı KARARI VERİR") ve (b) "morfoloji kuralı
`cube_router`'a eklenmez" kararı. İkisi de aslında şunu söylüyor: *"tam
kapsamı/tam sentezi biz üretemeyiz, o zaman onu insana bırakırız."* Bu doğru
bir mühendislik refleksi ama bir **çözüm değil** — sorunu insana devrederek
**erteliyor**. §1'in en iddialı maddeleri (15-19) tam olarak insana devredilen
o kısmı otomatikleştirmek istiyor; yani vizyon, projenin şimdiye kadar kaçınarak
çözdüğü sorunun **tam da kalbine** gidiyor.

---

## §3 — DIŞSAL DOĞRULAMA (repoyu hiç bilmeyen 3 taze ajan, yalnız WebSearch)

*(§2'nin çerçevesini kör biçimde sınamak için: hiçbiri DİMA'yı, kodu, hatta bu
belgeyi bilmiyor. Sonuç: §2'nin "imkânsız" dili kısmen fazla güçlüydü —
gerçek biçimsel sonuç başka bir yerde duruyor, ve bu daha umutlu bir sonuç.)*

### 3.1 İfade gücü tavanı gerçek — ama §2'nin işaret ettiği yerde değil
Levesque & Brachman (1987, kanıtlanmış teorem): bir temsil dilinin ifade gücü
arttıkça üzerindeki çıkarımın hesaplama karmaşıklığı kaçınılmaz artar.
Reiter (1978, CWA): kapalı bir şema açık-uçlu bir kümeyi (doğal dili) tam
kapsayamaz — bu **analitik**, kanıtlanmış bir sonuç, sadece ampirik zorluk
değil. Ama bu sonuç yalnız **MONOLİTİK** mimari için geçerli: tek bir kapalı
şemanın hem açık dili anlaması HEM kesin karar vermesi isteniyorsa (1980
uzman sistemleri — XCON'un 17.500 kuralı, "bilgi edinme darboğazı",
Winograd&Flores'in "arka plan" eleştirisi). **İKİ AŞAMALI** (üret + doğrula)
mimari farklı bir problem sınıfına düşüyor.

### 3.2 Üret-doğrula deseni endüstri standardı — ve DİMA zaten bu desende
Lean/Coq+LLM (DeepMind AlphaProof, Nature 2025): üretici sınırsız/sezgisel,
doğrulayıcı (kernel) küçük ve deterministik — "de Bruijn kriteri": güven
aramaya değil doğrulayıcıya duyulur. **7 gerçek endüstri ürünü** (Snowflake
Cortex Analyst, ThoughtSpot Spotter, Amazon Q, Power BI Copilot, Looker+
Gemini, dbt Semantic Layer, AtScale) **7'si de aynı desene yakınsamış**:
semantik katman + kısıtlı üretim, LLM asla nihai rakamı üretmiyor (dbt'nin
2026 kıyaslaması: saf text-to-SQL %84-90 → semantik katmanla %98-100).
**DİMA'nın "garson Intent-JSON üretir, küp hesaplar" mimarisi zaten bu
endüstri-standart desenin bir örneği** — §1'in madde 1-3, 5-14'ü aslında
tehlikede değil, endüstriyle aynı hizada.

### 3.3 Ama kör nokta gerçek: "sonuç doğru mu" ile "niyeti doğru yakaladı mı" ayrı şey
Autoformalization kör noktası: kernel biçimsel önermenin ispatlandığını
garanti eder, kullanıcının **kastettiği** önerme olduğunu garanti etmez.
Text-to-SQL literatüründe şema-halüsinasyonu hatalarının **>%80'i** tam bu
kör noktadan. DİMA'da bu `O3` (garson kararsızsa onaya düşer) ile kısmen ele
alınmış — ama residual risk kalıcı. Bu bilinen, sınırlı, aktif araştırılan bir
problem (insan-onayı, çoklu-örnekleme) — 1980'lerin çözümsüz kırılganlığından
**niteliksel olarak farklı**.

### 3.4 Madde 15-19'un gerçek engeli: verification-generation ASİMETRİSİ yok
Üret-doğrula deseni yalnız doğrulama **ucuz/asimetrik** olduğunda işler (SQL
sonucunu kontrol etmek ucuz, ispat type-check etmek polinom-zamanlı). "Bu
strateji optimal mi" sorusunun ucuz bir doğrulayıcısı **yok** — optimalliği
kontrol etmek optimizasyonun kendisi kadar pahalı, asimetri yok. Ve
doğrulanacak hedef (fayda fonksiyonu) veride yok: **Arrow'un İmkânsızlık
Teoremi** çoklu kriterin aksiyomatik olarak tutarlı tek bir "objektif"
tercihe indirgenemeyeceğini matematiksel kanıtlıyor. 7 endüstri ürününün
7'si de bu tavana çarpmış (Snowflake: *"geniş iş sorularına içgörü
üretmez"*; ThoughtSpot: *"modelde tanımlı olanla sınırlı"*; Power BI:
*"stratejik önerilerde analistin yerini alamaz"*).

### 3.5 Yakınsayan çözüm — üç bağımsız, birbirinden habersiz kaynak aynı örüntüye varıyor
- **MCDA/OR:** tam fayda fonksiyonu yerine ucuz tercih sinyali (sıralama/
  swing-weight) → "surrogate weights", tam elicitation'a göre **~%98**
  performans (Roberts 2002, SMARTER).
- **LLM-ajan literatürü** (MAVIS, CHI 2026): seçenek üret → insandan ucuz
  tercih sinyali al → o sinyale göre hesapla. Taranan literatürde "otonom,
  insan girdisiz optimal strateji" iddiasına **hiç rastlanmadı**.
- **OR endüstrisi** (Gurobi/CPLEX FAQ): amaç/kısıt her zaman insan tanımlar,
  solver yalnız o sabit amaç için kanıtlanmış-en-iyiyi arar.

**Üçü de aynı örüntüde:** sistem birkaç seçenek/senaryo üretir → insan ucuz
bir tercih sinyali verir (tam ağırlık değil) → sistem o sinyale göre
deterministik hesaplar.

### 3.6 Sonuç: bu, DİMA'nın doktrinini KIRMAZ — GENİŞLETİR
Bu örüntü zaten DİMA'nın **O2/O3** ilkesiyle (çok adımlı plan önizlenir,
kullanıcı bir tık onaylar) aynı iskelet. Madde 15-18'i "otonom optimizasyon"
değil **"sınırlı-seçenek üretimi + ucuz tercih sinyali + deterministik
hesaplama"** olarak çerçevelemek, "sayıyı küp koyar" ilkesini bozmadan
genişletir. §2'deki "doktrin çatışması" tanısı yumuşuyor: çatışma yok,
**eksik bir genişletme** var — ama küçük değil; amaç-elicitation kalitesi,
seçenek üretim kalitesi, çoklu-senaryo tutarlılık doğrulaması gibi ciddi,
çözülmemiş alt problemler hâlâ duruyor. Madde 19 (şirket beyni) ise hâlâ en
ağır madde — hem bu genişlemeyi HEM §2'nin kalıcı-hafıza reddini (madde 13)
aynı anda gerektiriyor.

---

## §4 — VİZYONA KARŞI ÖLÇÜLEN ENGELLER (yalnız engel, çözüm bu aşamada değil)

⚠ **Düzeltme:** Önceki envanterde (bu araştırmanın ilk taslağı) madde 11 ve 12
"planlanmış ama yok" (kategori C) sayılmıştı — **yanlış ölçüm**. `backend/app/rls.py`
(380 satır, FAZ 1.1, 7 dondurulmuş test) ve `backend/app/company_registry.py`
(251 satır, ADR-0016) gerçek, çalışan implementasyonlar. Bu, ölçüm aracının/ilk
taramanın körlüğüne bir örnek daha.

### Küme A — Agentic karar desteği · optimizasyon · strateji · yol haritası · senaryo (madde 4, 15-18)
**🔴 EN DERİN GERİLİM — "henüz yok" değil, "bilinçli olarak yasak".**

1. **`iki_cube` reddi (`MIMARI.md §2.0.3`)** — optimizasyon/strateji doğası gereği
   çoklu küp arası ilişki ister. Belgenin kendi sözü: *"`forecast`·`yargı`·
   `olumsuzluk` bir ÇIKTI BİÇİMİ eksikliği değil bir YETENEK eksikliğidir; plan
   da yapamaz."* Ertelenmiş değil, kayıtlı bir sınır.
2. **Kapalı fiil kümesi, bağımlılık grafiği yok** (`plan_kosucu.py`) — adımlar
   sabit enum'a bağlı (`SORGU·TREND·RAPOR·MATRIS·ANLAT·BAGLA·SUZ`), `depends_on`
   yok. Optimizasyon yapısal olarak yinelemeli aramadır; şema dallanma/döngü
   izin vermiyor.
3. **`ANLAT` fiili "LLM YOK"** — deterministik `interpret()` + `narration_guard`.
   Stratejik sentez ise doğası gereği üretici bir LLM işi — doktrin ters yönde.
4. **`narration_guard` yalnız rakamı doğrular** (±%2), cümlenin mantıksal/
   stratejik tutarlılığını hiç denetlemiyor (`G5.4`).
5. **Öz-düzeltme yasağı** (`G5.6`, ICLR 2024 referanslı ölçülmüş negatif sonuç)
   — senaryo simülasyonunun "dene/karşılaştır/rafine et" mantığıyla çelişiyor.
6. **Sabit tavanlar** — `AZAMI_SORGU=8`, `AZAMI_ADIM=12`, paralellik 4. Gerçek
   bir duyarlılık analizi onlarca-yüzlerce kombinasyon ister.
7. **Plan tek atımlık, durumsuz** (`O2`) — onayda aynı plan geri döner, adımlar
   arası durum taşınmaz. Optimizasyon/simülasyon çok turlu ve keşiflidir.
8. **§63-85'in 22 bölümünün tamamı** (`ONGORU-DURUM.md`) sıralama/kalibrasyon
   kalitesine gitti — hiçbiri yeni bir yetenek sınıfı eklemedi.

### Küme B — Kurumsal hafıza · konuşma takibi (madde 13, 19)
**🔴 Reddin gerekçesi vizyonun temel varsayımıyla doğrudan çatışıyor.**

1. **Sunucu hiçbir konuşma durumu saklamaz — bilinçli karar.** `MIMARI.md:2394`:
   *"sessiz sunucu-yanı oturum deposu bilerek reddedildi."* Bağlam istemciden
   istemciye "yankı" ile taşınır.
2. **Bu yankı mekanizması üretimde hiç çalışmadı** — `KURAL_DEVAM` hiç
   ateşlenmedi (`AskRequest`'te ilgili alan yoktu).
3. **Ret gerekçesi tam olarak vizyonun istediği şey** — *"thread/UI
   gruplamasının semantik sınır taşıması"* kusur sayılıp kapatılmış; ama
   "sürekli çalışma ilişkisi"/"şirket beyni" tam olarak thread-bağımsız,
   sunucu-yanı, kalıcı durum ister.
4. **Kalıcı olan tek şey `DecisionRecord`** — düz denetim satırı
   (question/chosen/options/rationale), zengin/sorgulanabilir hafıza değil.
5. **Slot hafızasının ufku bir netleştirme turu** (saniye-dakika), ay/yıl değil.
6. **"Muhasebe, anlama değil" felsefesi hafızayı kural-kapalı tutuyor** —
   her yeni hafıza türü yeni bir adlandırılmış `KURAL_*` ister; açık uçlu
   hatırlama bu mimariyle yapısal olarak uyuşmuyor.
7. **Sunucu kendi thread/oturum modelini tutmuyor** — *"bu kullanıcıyla son
   6 ayda ne konuştuk"* sorusuna karşılık verecek bir veri yapısı yok.
8. **Aynı kusur sınıfı ikinci kez** — `KURAL_CAPA` vakasının tekrarı olduğu
   belgenin kendisinde itiraf edilmiş; tekrarlayan bir zayıflık.

### Küme C — Ölçek · çoklu-kiracı · kanal · ticari (madde 6, 11, 12, 14, 20)
**Daha hafif — mühendislik/kapsam sınıfı, derin mimari çelişki değil.**

1. **Madde 12 (çoklu şirket/sektör):** veri izolasyonu çözülmüş (RLS+tenant
   registry) ama NLU/eşleştirme katmanı şirket-körü — `cube_router.py`'de
   `sirket|company|sektor|vertical` **sıfır** eşleşme (ölçüldü). Her yeni
   şirket/sektör aynı paylaşılan 5.077 satırlık dosyaya düşüyor, izole değil
   — terim çakışması riski.
2. **Madde 11 (güvenlik):** engel bulunamadı — RLS iki ölçülmüş baypası (JOIN,
   Discovery ham SQL) kapatıyor, büyük ölçüde teslim edilmiş.
3. **Madde 6 (veri bağlama):** ayrı bir engel çıkmadı, mevcut A-kategorisi
   uçlarla zaten örtüşüyor.
4. **Madde 14 (kanal genişlemesi):** `ask.py`'de 88 fonksiyon, 141 kez
   `Request|Response|fastapi|HTTPException` — iş mantığı HTTP taşımayla iç
   içe, kanal-agnostik çekirdek yok. Yeni kanal = router'ı kopyalamak veya
   söküp çıkarmak.
5. **Madde 20 (ticari katman):** kod sorunu değil — paketleme/fiyatlama/satış;
   ayrı bir engel **sınıfı** (iş modeli kararı, mimari kısıt değil).

---

**Sentez:** Küme A ve B'nin ortak noktası — bunlar "henüz inşa edilmedi" değil,
**MIMARI.md'nin kendi metninde adıyla reddedilmiş/kapatılmış**. Vizyonun en
iddialı 7 maddesi (4, 13, 15-19), bugünkü mimarinin **bilinçli sınırlarıyla
doğrudan çatışıyor** — bu, bir yapılacaklar listesi açığı değil, bir **doktrin
çatışması**. Küme C ise gerçek ama sıradan mühendislik borcu.

---

## §5 — SOMUT ÇERÇEVE (hâlâ teorik: "nasıl kodlanır" değil, "hangi çözüm sınıfına düşer")

§3.6'nın bulduğu örüntüyü (seçenek üret → ucuz tercih sinyali → deterministik
hesapla) madde 15-19'a uygulayınca, bunların **hepsi aynı zorlukta olmadığı**
ortaya çıkıyor. Üç ayrı alt-tabaka var — karıştırmak yanlış teşhise götürür.

### 5.1 Tabaka (a) — Parametrik what-if — EN KOLAY, çoğunlukla mühendislik
Madde 18'in (senaryo simülasyonu) çoğu aslında şu: *"aynı sorguyu, bir girdi
varsayımını değiştirerek yeniden hesapla"* ("fiyat %10 artarsa ne olur").
Bu, LLM'in **üretmesi** gereken yeni bir şey değil — küpün zaten bildiği bir
hesabı, parametre değiştirerek tekrar çalıştırmak. Teorik risk yok, çünkü
sayı hâlâ küpten geliyor; tek soru küpün "varsayımsal girdi" alıp alamadığı
— bu bir **mühendislik** sorusu, mimari bir çıkmaz değil. ⚠ Sınır: varsayım
küpün **zaten modellediği** bir parametreyse (fiyat, hacim, oran) kolay;
küpün **hiç modellemediği** yapısal bir şeyse ("yeni pazara girersek" — yeni
bir varlık/ilişki gerektirir) bu tabakadan (c)'ye düşer.

### 5.2 Tabaka (b) — Sınırlı-seçenek optimizasyonu — ORTA, O2/O3'ün doğal genişlemesi
Madde 15 (optimizasyon), 17 (yol haritası) ve madde 4'ün üst ucu burada.
§3.5'in bulduğu örüntü tam olarak uyuyor: sistem N adet (2-4) **somut,
deterministik olarak hesaplanmış** senaryo üretir ("A: maliyet -%10, teslimat
+%5 gecikme" / "B: maliyet aynı, teslimat -%3"), kullanıcı **tam ağırlık değil,
ucuz bir tercih sinyali** verir (sırala/seç — tıpkı O2'deki "bir tık onay"
gibi), sistem o sinyale göre deterministik hesaplamaya devam eder. Bu,
mevcut `O2`/`O3` doktrininin **kırılması değil, kapsamının genişlemesi**:
tek-plan-önizle yerine çok-senaryo-önizle.

Yeni, henüz var olmayan iki denetim türü gerekir (ikisi de **tanımlanabilir**,
imkânsız değil):
- **Seçenek çeşitlilik denetimi** — üretilen N senaryonun kozmetik değil
  **anlamlı farklı** olduğunu doğrulamak (`narration_guard`'ın rakam
  denetimine benzer ama hedefi farklı — çeşitlilik, doğruluk değil).
- **Senaryo iç-tutarlılık denetimi** — her senaryonun kendi adımlarının
  gerçek veriyle çelişmediğini doğrulamak (`plan_kosucu`'nun şema
  denetiminin bir uzantısı).

**Madde 17 (yol haritası)** aslında bu tabakanın en kolay ucu: kullanıcı
tercihini bildirdikten SONRA, birden çok kararı zaman içinde sıralamak
klasik bir **kısıt/çizelgeleme** problemidir (OR/CP alanında iyi çözülmüş) —
"en iyi hangi sırada" sorusu, "en iyi ne" sorusundan çok daha ehlileştirilmiş.

### 5.3 Tabaka (c) — Açık uçlu stratejik sentez — EN ZOR, tavan gerçekten burada
Madde 16 (McKinsey-düzeyi analiz) ve madde 19'un "anlama/yorumlama" kısmı bu
tabakada. Burada **sınırlı bir seçenek menüsü doğal olarak yok** — "bize
büyüme fırsatlarını anlat" sorusunun N=3 kutuya sığan bir yapısı yoktır, açık
uçludur. §3.3'ün kör noktası (doğrulayıcı "sonucun doğru mu" der,
"anlamlı/tutarlı mı" demez) burada tam güçle geçerli ve **büyütülmüş**
haliyle: tek bir sayı değil, bütün bir **anlatının** stratejik tutarlılığını
denetleyecek ucuz bir doğrulayıcı yok. §3.4'ün asimetri-yokluğu argümanı da
aynen geçerli. Bu tabaka için §3-§5'in bulduğu hiçbir desen tam çözüm
sunmuyor — **yönetilebilir ama çözülmüş değil**: gerçekçi çerçeveleme
"sistem taslak/hipotez üretir, insan editörlük yapar" (bugünkü danışmanlık
analistinin taslak-gözden-geçir iş akışına benzer) — otomasyon değil,
**hızlandırma**.

### 5.4 Hafıza ikiye ayrılıyor — madde 13 ≠ madde 19
§2/§3'te tek başlık altında toplanmıştı ama teorik olarak **farklı** sorunlar:

- **Madde 13 (konuşma takibi, "bunu takip et")** — bu bir **anaphora
  çözümü**, oturum-içi, kısa ufuklu. Sunucu-yanı kalıcı durum GEREKTİRMEZ;
  mevcut "istemciden istemciye yankı" deseni yeterli **eğer eksiksiz
  çalışırsa** (§2'nin bulduğu `KURAL_DEVAM` arızası bir **mühendislik**
  eksikliği, doktrin çelişkisi değil).
- **Madde 19 (şirket beyni)** — asıl gerilim burada, ama çözümü de burada:
  eğer "hafıza" bir **konuşma durumu** olarak değil, `DecisionRecord`'un
  genişletilmiş hali olan **yapılandırılmış, sorgulanabilir bir veri**
  (karar + sonuç + tarih + gerekçe) olarak çerçevelenirse, o veri **başka
  bir küp gibi** deterministik yoldan sorgulanabilir. Reddedilen şey
  "sessiz oturum deposu"ydu (`MIMARI.md:2394`) — "yapılandırılmış karar
  defteri" **aynı şey değil**. Bu çerçeveleme değişikliği, madde 19'u (c)
  tabakasından çıkarıp kısmen (b)'ye, kısmen zaten var olan altyapıya
  (`decisions.py`) taşır.

### 5.5 Özet ilke
Vizyonun en iddialı 6 maddesi (15-19, +4'ün üst ucu) tek bir "imkânsız" yığın
değil — üç farklı zorluk seviyesine ayrışıyor: **(a) bugün bile mühendislik
sorunu, (b) mevcut doktrinin doğal genişlemesi, (c) gerçekten açık, yalnızca
insan-destekli hızlandırmaya indirgenebilir.** Doğru sıralama muhtemelen bu
sırayla ilerlemek — (c)'yi (a) veya (b) gibi çözmeye çalışmak, ya
başarısızlıkla ya da doktrin ihlaliyle (sayıyı LLM'e yazdırmakla) sonuçlanır.

---

---

## §6 — CANLI TEŞHİS + İSTİŞARE MECLİSİ (özet)

*(Kullanıcının somut şikâyeti: "son 2 yıl satış → en ağırlıklı kalemler →
etkileri → grafik" gibi 3-4 adımlık, SAF OKUMA amaçlı basit bir zincir bile
~%20+ oranında başarısız oluyor. Bu, §5'in "zaten canlı/kolay" saydığı madde
1-3 alanında — yani asıl endişe optimizasyonun zor olması değil, **temelin
kırılgan olması**.)*

**Teşhis:** İki farklı hata sınıfı karışıyor olabilir — (i) **anlama hatası**
(garson/`cube_router` cümleyi yanlış çözüyor, §2'nin açık-dünya sorunu) vs
(ii) **orkestrasyon hatası** (`plan_kosucu`'nun kapalı fiil kümesi + `depends_on`
yokluğu + sabit tavanlar rutin bir çok-adımlı zinciri kıramıyor bile). Bunlar
**farklı fatura** çıkarır, ölçülmeden ayırt edilemez.

**5 karakterli münazaranın vardığı sonuç** (Muhafazakar Mimar · Ajan Mimarı ·
Denetim/Güvenlik Sorumlusu · Ürün Sözcüsü · Ölçüm Disiplini Temsilcisi):

- **Oybirliği:** rakam üretiminde katılık kalmalı — bu hiç tartışılmadı.
- **Kırılma noktası:** "rakam hâlâ küpten geliyor" yetmez — *hangi sorgunun
  sorulacağına karar veren şey* de bir karardır; statik planda bu **görünür**,
  gevşek döngüde **görünmez/hızlı** olur ("doğru rakamla yanlış hikaye").
- **Çözüm:** onayı **ön-kontrolden (gate) son-kontrole (audit)** kaydırmak —
  yalnız **önceden ilan edilmiş, salt-okuma/yan-etkisiz** sınıf için, her
  adım iz bırakmak şartıyla.
- **Çözülmeyen açık soru:** "okuma" ile "bir kararın girdisi olan okuma"
  arasındaki sınır nerede çizilir (Muhafazakar Mimar'ın "yamaç" endişesi).
- **Sıralama:** (1) önce ölç — kullanıcının örneğini canlıya at, anlama mı
  orkestrasyon mu kırılıyor gör; (2) yalnız orkestrasyon çıkarsa, **küçük bir
  pilot** olarak sınırlı/bütçeli/iz bırakan döngüyü dene; (3) **tek kesin
  "asla":** rakam üretimini gevşetmek veya okuma-döngüsünü sınır
  belirsizliğiyle yazma/eylem akışına sızdırmak.

---

## §7 — NİHAİ TEORİK UÇTAN UCA MİMARİ HARİTA

*(Bu bölüm §1-§6'nın vardığı sentezdir — artık teori değil, **hedef durum**.
Kod değil; hangi katmanda ne kadar katılık/serbestlik olması gerektiğinin
tam haritası.)*

### 7.0 Tek yönetişim ilkesi (her katmana uygulanan üst-kural)

> **Kaplin sıkılığı RİSKE göre ayarlanır, "bu bir LLM mi değil mi" sorusuna
> göre değil.** Doğru soru: *bu adım geri döndürülebilir mi, yanlışsa kim
> zarar görür, iz bırakıyor mu.* Geri döndürülemez/yüksek-etkili olan her şey
> sıkı kalır; geri döndürülebilir/düşük-etkili olan gevşeyebilir — ama
> sınıfı **önceden ilan edilmiş** ve **iz bırakan** olmak şartıyla.

### 7.1 Katman katman harita

| # | Katman | Bugünkü durum | Hedef durum | Değişiklik sınıfı |
|---|---|---|---|---|
| 0 | **Girdi** — kullanıcı ifadesi | Serbest Türkçe | Değişmez — kısıtlanamaz | — |
| 1 | **Niyet ayrıştırma** (garson→Intent-JSON) | LLM serbest, çıktı yapısal | **Aynı kalır** — §3.2'nin doğruladığı endüstri-standardı. Kapalı-dünya sınırı çözülmez, **yönetilir**: belirsizlikte onaya düş (`O3`), "anlamadım" her zaman açık kapı | değişmez ilke |
| 2a | **Orkestrasyon — okuma/keşif** | Yok (madde 1-3 bile statik plan mantığına zorlanıyor) | Kapalı-döngü, yinelemeli (ReAct-tarzı): önceki adımın **gerçek** sonucuna bakıp sıradaki adıma karar ver. Sabit adım tavanı değil **bütçe**. Onay **sonrası** (audit), öncesi (gate) değil | **YENİ katman** |
| 2b | **Orkestrasyon — yazma/eylem** | `plan_kosucu`: statik plan + toplu onay | **Aynı kalır** — §11'in gerçek endişesi burada, doğru kalibre edilmiş | değişmez ilke |
| 3 | **Hesaplama** — deterministik küp | Sayı her zaman buradan | **Değişmez** — hiç tartışılmadı, tartışılmayacak | değişmez ilke (§0) |
| 4 | **Doğrulama (guard)** | Yalnız rakam ±%2 | + **kompozisyon tutarlılığı** (çeşitlilik + iç-tutarlılık denetimi, §5.2) + niyet-yakalama denetimi (çoklu-örnekleme/onay, autoformalization kör noktasının kısmi çaresi, §3.3) | genişleme |
| 5 | **Sunum** — anlatı/görsel | `ANLAT`: "LLM YOK", deterministik `interpret()` | Madde 1-14 için değişmez. Madde 16 (McKinsey-düzeyi) için bu katmanın **ötesi**: otomasyon değil, insan-editörlüklü taslak (§5.3, tabaka c) | tabaka-bağımlı |
| 6 | **Hafıza/bağlam** | Sunucu durumsuz, istemci-yankı (`KURAL_DEVAM` arızalı) | Kısa-ufuk (madde 13): yankı deseni **tamamlanır** (mühendislik). Uzun-ufuk (madde 19): konuşma durumu **değil**, `DecisionRecord`'un genişlemesi — **yapılandırılmış veri**, kendisi bir küp gibi sorgulanır (§5.4) | ikiye ayrılır |
| 7 | **Karar desteği** — optimizasyon/strateji | Yok / `O2` tek-atımlık | (a) parametrik what-if → katman 3'ün uzantısı; (b) sınırlı-seçenek → katman 2a + ucuz-tercih-sinyali toplama (Arrow-bilinçli: sıralama/seç, tam ağırlık değil); (c) açık uçlu sentez → insan-editörlüklü hızlandırma, "tam otomatik" iddia edilmez (§5) | tabaka-bağımlı |
| 8 | **Denetim/izlenebilirlik** | Query contract + audit export | Katman 2a ve 7'nin iz bırakma ihtiyacını da kapsayacak şekilde genişler | genişleme |

### 7.2 Vizyon maddeleri (§1) haritaya nasıl oturuyor

| madde | katman(lar) | durum haritada |
|---|---|---|
| 1, 2, 3, 5, 6, 8, 9, 10 | 1, 2a, 3, 4, 5 | çekirdek — endüstriyle hizalı, asıl iş katman 2a'nın **YENİ** olması |
| 4, 15, 17 | 2a, 7b, 8 | O2/O3'ün genişlemesi — doktrin ihlali yok |
| 18 | 3, 7a | çoğunlukla mühendislik, teorik engel yok |
| 16 | 5 (tabaka c), 7c | otomasyon değil hızlandırma — dürüstçe sınırlı iddia |
| 19 | 6 (uzun-ufuk), 7c | reddedilen "oturum deposu" değil, **veri** olarak çerçevelenirse mümkün |
| 13 | 6 (kısa-ufuk) | mühendislik eksikliği, doktrin sorunu değil |
| 11, 12, 20 | katman-dışı | §2 Küme C — ölçek/güvenlik/iş modeli, ayrı sınıf |

### 7.3 Oraya giden sıra (tek doğru sıralama, §6'nın uzlaşısı)

1. **Ölç** — canlı örneklerle anlama/orkestrasyon ayrımını sınıflandır (bahis yok).
2. **Katman 2a'yı küçük bir pilot olarak dene** — yalnız önceden ilan edilmiş, salt-okuma sınıfı, bütçeli, iz bırakan.
3. Pilot doğrulanırsa katman 7b (sınırlı-seçenek) katman 2a'nın üstüne inşa edilir — yeni bir temel gerekmez.
4. Katman 6 (hafıza) ayrımı (kısa/uzun ufuk) **bağımsız** ilerleyebilir — 2a'yı beklemez.
5. Katman 7c (madde 16, 19'un sentez kısmı) **kasıtlı olarak en son** — çünkü hiçbir bulgu (§3, §5) burada tam bir çözüm önermiyor; erken girişim ya doktrin ihlaline (LLM sayı/karar üretir) ya boş vaade düşer.

### 7.4 Değişmeyecek olanlar (tek liste, hiçbiri müzakereye açık değil)

- Sayıyı **her zaman küp koyar**, LLM asla.
- Yazma/eylem akışları (katman 2b) **statik plan + açık onay** kalır.
- Okuma-sınıfı gevşeme (katman 2a), sınırı **önceden ilan edilmemiş** hiçbir akışa sızmaz.
- "Tam otomatik optimal strateji" iddiası hiçbir katmanda yapılmaz (Arrow teoremi, §3.4) — en fazla "seçenek üret + ucuz tercih sinyali al".
- Madde 16/19'un sentez kısmı **"hızlandırma"** olarak kalır, **"otomasyon"** olarak sunulmaz.

---

---

## §8 — ARAŞTIRMA SÜRECİNDE NE HATA ETTİK (öz-eleştiri)

Bu bölümü yazmadan önce sormamız gereken soruydu — dürüst cevap:

1. **İlk ajan 0 araç çağrısıyla döndü, fark edilmeden kabul edilebilirdi.**
   Ürün envanteri için gönderilen ilk fork, hiçbir dosya okumadan/hiç araç
   çağırmadan, sanki görevi yapmış gibi bir cevap üretti (5 saniyede, 0
   `tool_uses`). Bunu `ListAgents` ile fark edip zorla yeniden çalıştırmak
   gerekti. **Ders:** bir ajanın "bitti" demesi kanıt değildir; `tool_uses`
   sayısı kontrol edilmeden sonuç güvenilir sayılmamalı.
2. **İlk envanterde gerçek bir faktüel hata vardı.** RLS (`app/rls.py`, 380
   satır) ve çoklu-şirket katmanı (`app/company_registry.py`, 251 satır)
   "planlanmış ama yok" (kategori C) diye yanlış sınıflandı — ikisi de gerçek
   ve çalışıyordu. Farklı bir ajan bunu ancak bir sonraki turda yakaladı.
3. **§2'nin ilk teorik dili fazla güçlüydü** ("imkânsız"). §3'ün dışsal,
   repo-kör doğrulaması bunu düzeltti: gerçek biçimsel sonuç yalnız
   *monolitik* mimari için geçerliydi, DİMA'nın iki-aşamalı (üret+doğrula)
   mimarisi için değil. Kendi kendine yazılan teori, dışsal sınama olmadan
   **abartıya** kayabiliyor.
4. **İki farklı sorun (dil-anlama ↔ karar-teorisi "en iyi ne demek") başta
   tek sorunmuş gibi ele alındı** — kullanıcının "gerçekten hazır mıyız"
   sorusu bunu ortaya çıkardı, ayrı ele alınınca (§3.4-3.5) çözüm yolu
   netleşti.
5. **En büyük yapısal boşluk: bütün bu teorik/dışsal araştırma, bu turdan
   önce CANLI SİSTEME hiç dokunmadı.** Kullanıcının somut "%20 arıza"
   iddiası hiçbir zaman ölçülmedi, yalnız kabul edilip üzerine teori
   kuruldu. §10 bunu düzeltiyor — ama bu düzeltmenin bu kadar geç gelmesi,
   kendi başına bir derstir: teori ölçümün **yerine** geçmeye başlamıştı.

---

## §9 — §7'NİN ZAYIF KARINLARI (nihai mimari haritanın öz-eleştirisi)

§7'nin kendisini kendine karşı sınama — kullanıcının doğrudan sorusu üzerine:

1. **Yeni tek kritik nokta: okuma↔yazma sınıflandırması.** Bugün her istek
   aynı ağır muameleyi görüyor — kaba ama güvenli. Harita uygulanınca,
   garson'un "bu istek salt okuma mı, karar girdisi mi" kararı sistemin
   **yeni en kırılgan tek noktası** olur. §6'nın meclisi bu sınırı
   çizemedi (Muhafazakar Mimar'ın "yamaç" endişesi çözümsüz kaldı).
2. **Katman 4'ün genişlemesi (kompozisyon tutarlılık + çeşitlilik
   denetimi) hiç tasarlanmadı.** "N senaryo anlamlı farklı mı" sorusunu
   deterministik olarak kim yanıtlayacak — bu kendisi bir yargı işi,
   çözülmeye çalışılan sorunu denetim katmanında yeniden doğurabilir.
3. **"Bütçe tabanlı adım sınırı" belirsiz.** Sabit tavan (`AZAMI_ADIM=12`)
   en azından öngörülebilir bir arıza veriyordu; bütçe tükenince ne
   olacağı (sessiz kes / "bulduğum kadarıyla" dön) tasarlanmadan aynı
   brittle-truncation sorununu farklı bir kılıfla geri getirebilir.
4. **Katman 7b'nin "ucuz tercih sinyali" arayüzü tasarlanmadı** — kaç
   seçenek, nasıl sunulur, kullanıcı gerçekten mi seçiyor yoksa rastgele mi
   tıklıyor; bu saf backend sorunu değil, ürün/UX sorunu.
5. **Katman 6 (uzun-ufuk hafıza) — "bu bir karardı, kaydet" kararını kim,
   ne zaman verir?** Otomatikse yeni bir sınıflandırıcı (yine yargı) gerekir;
   manuelse "şirket beyni" büyük ölçüde boş kalır.
6. **Tabaka (c) (madde 16/19) — "otomasyon değil hızlandırma" teoride
   temiz ama kullanıcı güveni pratikte ayrım yapmayabilir** (akıcı/emin
   görünen taslak metne aşırı güvenme, bilinen bilişsel önyargı).
7. **Gecikme/maliyet çözülmedi, yalnız ertelendi** — yinelemeli döngü daha
   fazla LLM turu demektir, meclis bunu "ölçmeden bilinmez" diye bıraktı.
8. **Genel:** haritadaki her "YENİ"/"genişleme" hücresi **hiçbir yerde bir
   kez bile prototiplenmedi** — teorik olarak tutarlı, inşa edilebilirliği
   doğrulanmamış.

---

## §10 — CANLI KANIT (ilk ölçüm, §6/§9'un "önce ölç" ilkesi uygulanıyor)

**Kurulum:** `dima-oneri-8002` (imaj `s39`, kod değişmedi) ayağa kaldırıldı,
`demo-boyahane` tenant'ıyla giriş yapıldı. Kullanıcının şikâyet ettiği örnek
ve parçaları `/ask`'e gerçekten gönderildi.

### 10.1 Tekil sorgu (madde 1) — ÇALIŞIYOR
*"son 2 yıl ciro ne kadar"* → 0.8s, doğru SQL
(`SUM(ciro_tl) WHERE tarih >= '2024-08-25'`), doğru sonuç
(₺218.696.729,01), `kanit_sinifi: olculmus`. **Temel katman sağlam.**

### 10.2 Kırılım sorgusu (madde 2), boyut belirtmeden — AÇIK BİR ANLAMA AÇIĞI
*"ciroya en çok katkı yapan kalemler neler"* → 21.8 saniye (LLM turu) sonunda
`"note": "Hangi kırılımı istiyorsun?"` — **cevap yok, soru geri geldi.**
Kullanıcı gerçek dünyada hangi iç boyut adlarının (`musteri`, `renk`,
`makine`...) var olduğunu bilmeden bu soruyu asla doğru soramaz. Bu, §2'nin
"açık dünya↔kapalı şema" teşhisinin **birebir canlı örneği**: sistem varsayılan
bir kırılım sunmak yerine kullanıcıyı kendi şema bilgisiyle sınıyor.

### 10.3 Kullanıcının BİREBİR cümlesi — ne beklenip ne bulundu
*"son 2 yıl satış verileri ve bunun üzerinde ağırlığı en fazla olan kalemler
ve bunların etkilerini araştır, grafiğe dök"* → 23.5s, sonuç:

```
"note": "4 adım (tavan 12) · 1 sorgu (bütçe 8) — koşmadan önce gözden geçir."
trace: ["orkestratör: 4 adımlık plan önizlendi (§28.3 — onay bekliyor)",
        "niyet: tür=kirilim+ustunluk · dönem=1 ·
         kırılım=kalem,satis_temsilcisi · bilinmeyen=verileri,bunun,uzerinde"]
```

**Beklenenin aksine, bu ORKESTRASYON kırılması DEĞİL.** Sistem 4 adımı
(`SORGU→AYRISTIR→GORSEL→ANLAT`) doğru sırayla kurdu, `GORSEL` adımı `$1`'e
doğru referans verdi — §2 Küme A'nın "kapalı fiil kümesi, `depends_on` yok"
tespiti bu örnekte **kompozisyonu engellemedi**. Sistem `O2` doktrinine tam
uyarak önizlemede durdu.

**Ama gerçek, daha ciddi bir kusur burada gizli:** `niyet` alanı kırılımı
**`kalem,satis_temsilcisi`** olarak doğru okumuş (kullanıcı "kalemler" dedi) —
ama üretilen `cube_query`'nin 3 adımının **hepsinde** kullanılan gerçek
boyut **`musteri`** (müşteri)! Yani sistem "kalem" boyutunun küpte
karşılığı olmadığını görüp **sessizce** "müşteri"ye geçmiş — kullanıcıya
hiçbir yerde *"kalem diye bir kırılımım yok, en yakını müşteri, onu
kullanıyorum"* denmemiş. Bu, `backend/CLAUDE.md`'nin *"beyan kültürü:
yapılamayan şey söylenir"* (`ADR-0020`) ilkesinin **doğrudan ihlali** —
teorik değil, ölçülmüş, tek bir isteğin içinde.

### 10.2/10.3 sentezi — asıl teşhis değişiyor

Beklenen teşhis (§6): "orkestrasyon kırılıyor, katılık yanlış katmanda."
Ölçülen teşhis: **orkestrasyon aslında ayakta duruyor; asıl kırık olan
katman 1 (niyet ayrıştırma)'nin sessiz-ikame davranışı** — bilinmeyen bir
kavramı en yakın bilinen kavrama **beyansız** eşliyor. İkinci bir kırık:
**onay-gate'in bedeli** — 23.5 saniye LLM gecikmesi sonunda kullanıcı hâlâ
hiçbir sonuç görmüyor, yalnız "onaylar mısın" sorusu — tam olarak §6'nın
"okuma-sınıfı işe yazma-sınıfı sürtünme uygulanıyor" teşhisiyle örtüşüyor,
ama sebep tahmin edilenden (kırılan kompozisyon) farklı (yavaş+sessiz
belirsiz önizleme).

**Doğrulanan:** madde 1 (temel) sağlam. **Kısmen doğrulanan:** okuma-sınıfına
yazma-sınıfı sürtünme uygulanıyor (gecikme + gereksiz onay adımı). **Yeni
bulunan, önceden hiç teorileşmemiş:** sessiz boyut ikamesi — `ADR-0020`
ihlali, orkestrasyon değil **niyet ayrıştırma + beyan disiplini** kusuru.
**Test edilmedi (açık kalan):** onaylanmış planın gerçek çalıştırma sonucu —
grafiğin fiilen "müşteri" kırılımıyla mı üretildiği, kullanıcıya nasıl
sunulduğu.

---

*Bu belge şu an araştırma açısından NİHAİ hâlindedir: §1 vizyon → §2-3
teorik+dışsal teşhis → §4-5 engel haritası → §6 canlı teşhis+münazara → §7
mimari harita → §8 öz-eleştiri (süreç) → §9 öz-eleştiri (harita) → §10 ilk
canlı kanıt. Kanıt, teoriyi kısmen doğruladı, kısmen yön değiştirdi: asıl
öncelik artık "orkestrasyonu gevşet" değil, "sessiz ikameyi beyan et + gate
gecikmesini okuma-sınıfında hafiflet." Sonraki adım artık araştırma değil
**geliştirme**dir.*

---

## §11 — KÖK NEDEN, KODDA DOĞRULANDI (§10'un devamı — onaylanan plan fiilen koşturuldu)

**Yöntem:** §10.3'teki önizlenen plan `POST /plan/kos`'a fiilen gönderildi (kullanıcının
onay tıkının birebir karşılığı). Sonuç `HTTP 200`, 3.0s.

### 11.1 Ölçülen çıktı

```json
{
  "source": "cube", "adim_sayisi": 4,
  "result": {"columns": ["musteri","toplam_ciro"], "rows": [8 satır]},
  "bolumler": [ {1 bölüm} ],
  "note": "Bu cevap 4 adımda üretildi: 1. SORGU… 2. AYRISTIR… 3. GORSEL… 4. ANLAT…"
}
```

**Yok olanlar:** `viz` (grafik) alanı **hiç yok**. `contribution`/`interpretation` de
yok. `bolumler` dizisi **1** eleman taşıyor — plan 4 adımlıydı.

### 11.2 Kod düzeyinde kesin sebep

`backend/app/plan_tuketici.py`:

- **`_gorsel()`** (satır 172-183) `GORSEL` adımı için `viz.recommend(...)`'i **gerçekten
  çağırıyor** — grafik kararı hesaplanıyor, kaybolmuyor **hesaplamada**.
- **`bolumlere_cevir()`** (satır 190-233) bölümleri **`CIKTI_TIPI`ye göre** topluyor —
  yalnız `"satirlar"` üreten adımlar (`SORGU` gibi) `bolumler`'e girer. `GORSEL`/`ANLAT`
  çıktı tipleri farklı olduğu için **elenir** — bu, yorumun kendi ifadesiyle bilinçli bir
  kural (*"Bölümler FİİLE göre değil ÇIKTI TİPİNE göre toplanır"*).
- **`kosum_yaniti()`** (satır 1440-1468) — `/plan/kos`'un **HTTP cevabının tek sahibi** —
  şu alanları kurar: `source, question, adim_sayisi, result, cube_query, bolumler, note`.
  🔴 **Bu sözleşmede `viz` alanı YOK.** `/ask`'ın tek-adımlı yolu `viz`'i doğrudan
  taşıyor (§10.1'de ölçüldü — `kpi` tipi görsel geldi); ama `/plan/kos`'un çok-adımlı
  yolu, `kosum_yaniti` yazıldığından beri, **hiçbir zaman** bir `viz` alanı taşımamış.

**Sonuç:** `GORSEL` fiili içeren HER çok-adımlı plan, hesaplanan grafiği **hesaplar ama
hiç göndermez**. Bu olasılıksal (~%20) bir NLU arızası değil — **%100 tekrarlanabilir bir
sözleşme boşluğu**. Kullanıcı "grafiğe dök" dediğinde, plan çok-adımlı olduğu sürece
(GORSEL bir SORGU'nun peşine dizildiği her durumda), grafik **hiçbir zaman** gelmeyecek —
sistem versiyonundan, sorunun tam ifadesinden bağımsız, **yapısal**.

`ANLAT` da aynı mekanizmayla düşüyor: gerçek `interpretation` yerine, `note` alanı yalnız
`cevap_notu()`'nun ürettiği **statik şablon metni** ("Bu cevap 4 adımda üretildi: …") —
`ANLAT` adımının gerçekte ürettiği anlatı cevaba hiç ulaşmıyor.

### 11.3 §10'un "sessiz ikame" bulgusuyla ilişkisi

İki kusur **bağımsız** ve **ikisi de gerçek**:
- **Niyet katmanı:** "kalem" boyutu sessizce "musteri"ye ikame edildi (`ADR-0020` ihlali).
- **Sunum katmanı (bu bölüm):** `GORSEL`/`ANLAT` çıktıları hesaplanıyor ama HTTP
  sözleşmesinde hiç yer almıyor.

Kullanıcı ikisini birden tek bir "%20+ arıza" deneyimi olarak yaşıyor, ama teşhis
ayrılınca **ikisi de küçük, kesin, yerel düzeltmesi olan** kusurlar — mimari bir
çıkmaz **değil**.

---

## §12 — TEŞHİS ÖZETİ VE KARAR NOKTASI

**Baştaki hipotez** (§6): "katılık orkestrasyon katmanında yanlış yerde, gevşetme
gerekiyor" — büyük, riskli, mimari bir müdahale.

**Ölçülen gerçek** (§10-§11): orkestrasyon **çalışıyor** (4 adım doğru sıralandı, `$1`
referansı doğru kuruldu, `O2` doktrini doğru işledi). Kırık olan iki **yerel, küçük**
şey:

| # | kusur | katman | kanıt | risk sınıfı |
|---|---|---|---|---|
| 1 | "kalem" → "musteri" sessiz ikame, beyansız | niyet ayrıştırma (garson) | `trace` alanı: niyet doğru okundu, `cube_query` farklı boyut kullandı | `ADR-0020` ihlali — **beyan disiplini** |
| 2 | `GORSEL`/`ANLAT` çıktıları hesaplanır, `kosum_yaniti` sözleşmesinde yok | sunum (`plan_tuketici.py`) | kod okundu: `viz.recommend()` çağrılıyor, `kosum_yaniti`'nin döndürdüğü sözleşmede `viz` alanı yok | **sözleşme boşluğu**, mimari değil |

**Karar noktası (kullanıcıya):** İkisi de küçük, yerelleştirilmiş, düşük riskli
düzeltmeler — §7'nin büyük "katman 2a" gevşetmesini **gerektirmiyor**. Olası sıralama:
(a) önce bu iki somut kusuru düzelt, gerçek etkisini ölç; (b) §7'nin daha büyük mimari
genişlemesi (okuma/yazma orkestrasyon ayrımı) yalnız bu iki düzeltme sonrası **hâlâ**
arıza kalırsa gündeme gelsin. Bu, meclisin (§6) "önce ölç, büyük bahis oynama" ilkesiyle
birebir uyumlu — ölçüm, teorinin öngördüğünden **daha küçük, daha ucuz** bir sorun
buldu.

**Ek kesinlik (`backend/app/schemas.py`):** `AskResponse`'da `viz`, `contribution`,
`interpretation` alanlarının **üçü de zaten var** (ADR-0024, Faz G1/H, `cikti_yorumlama`)
— yani bu bir eksik şema değil, **eksik doldurma**. `plan_semasi.CIKTI_TIPI`
(`plan_semasi.py:206`) `GORSEL→bulgular`, `AYRISTIR→bulgular`, `ANLAT→metin` diye
tanımlıyor; `bolumlere_cevir` yalnız `"satirlar"` tipini topluyor. Yani üçü de
(`_gorsel`, `_ayristir`, `_anlat` — hepsi hesaplanıyor, kodda doğrulandı) `kosum_yaniti`'ye
hiç ulaşmıyor çünkü `bolumlere_cevir` onları süzüyor. **Düzeltme yeri tek ve dar:**
`kosum_yaniti()` (`plan_tuketici.py:1440`), `out["ciktilar"]`'dan `plan["adimlar"]` ile
hizalı şekilde son `GORSEL`/`AYRISTIR`/`ANLAT` çıktısını `viz`/`contribution`/
`interpretation` alanlarına yazmalı — yeni bir alan icat etmeden, var olan sözleşmeyi
doldurarak.

---

## §13 — DÜZELTME DENENDİ (kullanıcı onayıyla, araştırmadan geliştirmeye geçiş)

### 13.1 Değişiklik

`backend/app/plan_tuketici.py`'ye `_bulgu_ve_metin_cikar()` eklendi — `out["ciktilar"]`'ı
`plan["adimlar"]`'la hizalayıp son `GORSEL`/`AYRISTIR`/`ANLAT` çıktısını bulur.
`kosum_yaniti()` artık bu üçünü, doluysa, `viz`/`contribution`/`interpretation`
alanlarına yazıyor — `AskResponse`'da zaten var olan alanlar (yeni alan icat
edilmedi). Boşsa (`{}`/boş metin) alan hiç eklenmiyor — "hesapladım ama boş" ile
"hiç hesaplamadım" karışmasın diye.

Yeni dosya: `backend/tests/test_gorsel_ayristir_anlat_cevaba_ulasir.py` (6 test —
her üç alanın taşındığını, boşken eklenmediğini, tek-adımlı eski davranışın
bozulmadığını doğruluyor).

### 13.2 Hedefli test — 341/342 geçti, 1 kırmızı **ilgisiz**

`plan_tuketici`'ye dokunan 25 dosya (342 test) toplu koşuldu. **1 kırmızı** —
ama benim değişikliğimle **hiç ilgisi yok**, önceden var olan bir kusur:

> `test_b1_b2_garson_yolu_besleniyor.py::test_GARSON_YOLUNDAKI_HER_CAGRI_SORU_TASIYOR`
> — `routers/oneri.py:560`'daki `plan_kos()`, `metin_ve_indeks(schema, principal)`'i
> `soru=` **vermeden** çağırıyor. Bu çağrı, ben dokunmadan **önce** de oradaydı
> (§11'de okunan kodun birebir aynısı). `MUAF` listesine gerekçesiyle eklenmeli ya
> da `soru=` verilmeli — **ayrı bir kusur, ayrı bir karar gerektirir**, bu bültende
> düzeltilmedi.

### 13.3 Canlı doğrulama — imaj `s40`, kullanıcının BİREBİR cümlesi

```
preview (10.2s): "4 adım (tavan 12) · 1 sorgu (bütçe 8) — koşmadan önce gözden geçir."
plan_kos (6.2s) → keys: [...,"viz","contribution"]   ← ÖNCEDEN YOKTU, ARTIK VAR
viz: {"kind":"bar","measures":["toplam_ciro"],"dims":["kumas_cinsi"],
      "units":{"toplam_ciro":"₺"},"reference_line":{"kind":"average",...}, ...}
contribution: {"measure":"toplam_ciro","mode":"yoy","kind":"segment",
                "tarama_beyani":"24 aday arasından 6 kırılım arasından en
                açıklayıcısı seçildi — ⚠ bu bir eşik testi değil, bir seçimdir…"}
interpretation: null   ← bu turda ANLAT gerçek özet üretmedi, boş bırakıldı (doğru davranış)
```

**Doğrulandı: kullanıcının "grafiğe dök" isteği artık gerçek bir grafik (bar chart,
birim ₺, ortalama referans çizgisi) döndürüyor — §11'de ölçülen boşluk kapandı.**

⚠ İlginç yan gözlem: bu turda garson kırılımı `kumas_cinsi` (kumaş cinsi) seçti —
§10.3'teki `musteri` değil. Yani "kalem"in sessiz ikamesi **her seferinde aynı
boyuta düşmüyor**, çalıştırma çalıştırma değişebiliyor (LLM olasılıksallığı). §12'nin
1 numaralı kusuru (sessiz ikame, beyansız) **hâlâ düzeltilmedi** — yalnız 2 numaralı
kusur (sözleşme boşluğu) kapandı.

### 13.4 Bekleyen: korpus kapısı (arka planda, KAPI TOPLU KOŞULUR kuralına göre)

Bundle sonu tek kapı (`lab/kapi.py --tam`) arka planda koşuyordu; **kullanıcı
tarafından durduruldu** (sessiz ikame düzeltmesiyle birlikte tek koşumda tekrar
koşulacak — `KAPI TOPLU KOŞULUR` kuralına uygun, iki ayrı kapı yerine bir).

---

## §14 — NİHAİ KARARLAR VE YOL HARİTASI

### 14.1 Bu operasyonda kesinleşen kararlar

| # | karar | gerekçe | durum |
|---|---|---|---|
| 1 | §7'nin büyük mimari genişlemesi (okuma/yazma orkestrasyon ayrımı, **katman 2a**) **ERTELENDİ** | §10-§11 ölçümü: orkestrasyon zaten çalışıyor (4 adım doğru sıralandı, `$1` referansı doğru kuruldu, `O2` doktrini doğru işledi) — büyük, riskli bir mimari müdahaleyi haklı çıkaran bir kanıt **bulunamadı** | ⊘ askıda — yalnız §14.3'teki koşul gerçekleşirse gündeme gelir |
| 2 | Sözleşme boşluğu (`viz`/`contribution`/`interpretation` kayboluyordu) **DÜZELTİLDİ** | §11'in kesin kod teşhisi → §13'te tek fonksiyonluk, dar kapsamlı düzeltme → canlıda doğrulandı | ✅ kapandı |
| 3 | Sessiz ikame kusuru (`ADR-0020` ihlali — "kalem" sessizce başka bir boyuta düşüyor) **DÜZELTİLECEK** | §10.3 + §13.3'te **iki ayrı çalıştırmada iki farklı boyuta** düştüğü ölçüldü (`musteri`, sonra `kumas_cinsi`) — kararsız VE beyansız, bileşik risk | 🔴 sıradaki iş (bu bölümün planı §14.2) |
| 4 | Garson-katalog-budama kapısının atlanması (`plan_kos`, `soru=` eksik) **AYRI BİR KARAR** | §13.2'de bulundu, benim değişikliğimden önce de vardı; kapsamı (LLM'siz bir yolda katalog budamasının gerçek maliyeti nedir) netleşmeden düzeltmek riskli bir varsayım olurdu | ❓ kullanıcı kararı bekliyor — bu bültende **kapsam dışı** |

### 14.2 Sessiz ikame düzeltmesi — plan (uygulanmadan önce yazılı)

**Bilinen (ölçülmüş):**
- Garson'un `trace` alanı niyeti **doğru** okuyor (`kırılım=kalem,satis_temsilcisi`).
- Üretilen `cube_query.dimensions` bunun yerine gerçekte var olan bir boyuta
  (`musteri` ya da `kumas_cinsi`, çalıştırma çalıştırma değişiyor) düşüyor.
- Kullanıcıya bu ikamenin yapıldığı **hiçbir yerde söylenmiyor** — ne `trace`'te,
  ne `note`'ta, ne `interpretation`'da.

**Bilinmeyen (bu bölüm yazılırken henüz kod okunmadı — sıradaki adım budur,
körlemesine düzeltme yapılmayacak):**
- İkame **nerede** oluyor — en olası adaylar `backend/CLAUDE.md`'nin yapı
  tablosundaki `value_index.py`/`archetypes.py`/`synonyms` (bulanık eşleşme
  katmanı, `ADR-0018`) ya da garson'un Intent-JSON'ı gerçek bir `cube_query`'ye
  çeviren adım (`plan_garson.py` ya da `cube_router.py`'nin ilgili fonksiyonu).
- İkame bir **niyet/tercih** mi (LLM'in kendisi "kalem yok, en yakını böyle"
  diye seçiyor) yoksa deterministik bir **fuzzy-match** mi (`value_index`) —
  ikisinin düzeltmesi farklıdır: birincisi bir **istem** değişikliği ister
  (LLM'e ikameyi `trace`'e yazdırmayı öğretmek), ikincisi bir **kod** değişikliği
  (fuzzy-match sonucu, çözüm yoluna otomatik bir beyan cümlesi ekletmek).

**Sıralı plan:**
1. Kod okunacak: garson Intent-JSON → `cube_query.dimensions` çevrimi tam
   olarak nerede oluyor, ikame o adımda mı yapılıyor, `_neden_dustu`/
   `plan_onarim.onar` gibi zaten var olan "onarım beyanı" mekanizması (§13.1'in
   incelediği `calistir()` içinde görüldü — `onarimlar` listesi, `iz`'e
   ekleniyor) bu ikameyi de kapsayacak şekilde **genişletilebilir mi**, yoksa
   yeni bir beyan noktası mı gerekiyor.
2. Eğer `plan_onarim` zaten "sessiz düzeltme yoktur" ilkesiyle çalışıyorsa
   (docstring'i böyle söylüyordu, §14.2 hazırlanırken görüldü) — bu, ikamenin
   **o mekanizmadan geçmediğinin** kanıtıdır; ikame büyük olasılıkla daha
   erken, garson'un kendi Intent-JSON üretiminde ya da `value_index`'in
   sessiz bir fuzzy-match'inde oluyor.
3. Düzeltme, `plan_onarim`'in zaten kurduğu **"sessiz düzeltme yoktur, beyan
   edilir"** disiplinine **katılmalı** — yeni bir disiplin icat edilmeyecek,
   var olanın kapsamı genişletilecek (`KAT-1`).
4. Test: en az 2 senaryo — (a) istenen boyut gerçekten yoksa ikame + beyan,
   (b) istenen boyut varsa ikame **yapılmaz**, ikisi de `trace`/`note`'ta
   görünür kanıt bırakmalı.
5. Hedefli pytest → tek bir bundle-sonu kapı (§13'ün düzeltmesiyle **birlikte**,
   `KAPI TOPLU KOŞULUR` kuralına göre tek koşum).

### 14.3 §7'nin büyük mimari genişlemesi ne zaman gündeme gelir

Bu operasyonun en önemli metodolojik sonucu: **teorinin öngördüğü mimari çıkmaz
(§6, katman 2a gevşetmesi), ölçümle iki küçük, yerel kusura indirgendi.** Bu
tesadüf değil — meclisin (§6) kendi ilkesiydi ("önce ölç, büyük bahis oynama").

§7'nin katman 2a genişlemesi (okuma/yazma orkestrasyon ayrımı) **iptal
edilmedi** — yalnız önceliği düştü. Gündeme gelme koşulu netleştirildi:

> Her ikisi de (§14.1 madde 2 VE 3) düzeltilip yeniden ölçüldükten **sonra**,
> kullanıcının orijinal şikâyetindeki (~%20+ arıza) oran **hâlâ** anlamlı
> ölçüde yüksekse, o zaman kalan arızanın kaynağı gerçekten orkestrasyon
> katmanı demektir — ve §7 devreye girer. O ana kadar §7 bir **hazır plan**
> olarak durur, bir **taahhüt** değil.

### 14.4 Genel değerlendirme — bu operasyonun cevapladığı asıl soru

Operasyon *"mimari çıkmazlarımız var, bunlar çözülemiyor"* hipoteziyle başladı
(bu belgenin ilk cümlesi). §1-§9 bu hipotezi teorik olarak **derinleştirdi**
(gerçek bir doktrin çatışması var — madde 15-19). Ama §10-§13'ün canlı ölçümü
gösterdi ki **kullanıcının somut, günlük şikâyetinin** (grafik gelmiyor) kaynağı
o derin çatışma **değildi** — iki sıradan, yerelleştirilmiş, düzeltilebilir
kod kusuruydu. **İkisi de doğru:** mimarinin uzun vadeli, iddialı vizyon
maddeleri (§1'in 15-19'u) gerçekten teorik bir tavana çarpıyor; ama bugünün
günlük arızası o tavandan değil, sıradan bir sözleşme boşluğundan ve bir
beyan disiplini eksikliğinden geliyordu. **Teori doğruydu ama yanlış katmanı
suçluyordu** — ve bunu yalnız ölçüm gösterebildi.

---

## §15 — SESSİZ İKAME DÜZELTMESİ (§14.2 planının uygulanması)

### 15.1 Kod okundu — kök neden `§14.2`'nin ilk tahmininden FARKLI çıktı

`plan_onarim.py` (sessiz-onarım disiplininin sahibi) okundu: üç şartı var — (1) yazılan
değer geçersiz, (2) **tam olarak bir** geçerli yer var, (3) anlam değişmiyor. "kalem"in
ikamesi 2. şartı **sağlamıyor** (aşağıda görüldüğü gibi birden fazla, farklı boyuta
düşebiliyor) — yani bu modülün kapsamı **doğru** dışladığı doğrulandı.

Asıl kaynak `backend/app/niyet.py` — ve buradaki keşif planlanandan daha kesindi:
**"kalem" ve "satis_temsilcisi" UYDURULMUŞ değil, GERÇEK boyut adları** — yalnız
`parti` küpünde değil, `butce` ve `siparis`/`firsat` küplerinde (`grep` ile doğrulandı,
`butce/metadata.yml:78: - name: kalem`). Yani bu **klasik bir `iki_cube` durumu**
(`MIMARI §2.0.3`, §2/§3'ün teorik bulgusu): kullanıcının istediği kırılım ile seçilen
küpün ölçüsü (`toplam_ciro`) farklı küplerde yaşıyor; plan yalnız `parti`'yi koşabildi,
ötekini sessizce düşürdü.

### 15.2 Düzeltme — beyan, onarım değil

`plan_tuketici.py`'ye iki fonksiyon eklendi:
- `_kullanilan_boyutlar(out, plan)` — planın fiilen koştuğu tüm sorguların boyutları.
- `_kirilim_beyani(schema, soru, out, plan)` — `niyet.coz(soru, schema)`'nın (LLM'siz,
  saf şema-eşleştirme) bulduğu `kirilimlar` listesini kullanılan boyutlarla kıyaslar;
  kayıp varsa `⚠ İstenen kırılım(lar) bu cevaba yansımadı: … — … onun yerine … kullanıldı`
  cümlesini `kosum_yaniti`'nin `note`'unun **sonuna** ekler (`plan_onarim`'in "beyanlar
  sona eklenir" ilkesiyle aynı sıra).

### 15.3 Bir regresyon canlıda yakalandı ve düzeltildi — ilk yazım sessiz kaldı

İlk yazım `n.kirilim_istendi` (metinde "göre"/"bazında" gibi klasik bir **kalıp** var mı)
alanını da şart koşuyordu. Canlı test bunun **False** çıktığını gösterdi — kullanıcının
cümlesi klasik bir kırılım kalıbı taşımıyor — oysa `kirilimlar` (şema eşleştirmesi) YİNE
DE `['kalem','satis_temsilcisi']` buluyordu. Yani ilk yazım, **tam düzeltmek istediği
kusuru tekrarladı**: sessiz kaldı. `niyet.py`'nin kendi ayrımını (§121-124 — "kalıp var
mı" ≠ "boyut eşleşti mi") doğru okuyup yalnız `kirilimlar`'a bakacak şekilde düzeltildi.
Bu regresyon `test_kirilim_beyani.py`'ye adıyla test olarak eklendi.

### 15.4 Canlı doğrulama — imaj `s44`, kullanıcının BİREBİR cümlesi, 2 tekrar

```
note: …(4 adım)…

⚠ İstenen kırılım(lar) bu cevaba yansımadı: kalem, satis_temsilcisi
  — seçilen veri kümesinde yok, onun yerine musteri kullanıldı.
viz present: True
```

İki ayrı çalıştırmada da **aynı, tutarlı** beyan geldi (§13.3'teki çalıştırma-arası
kararsızlığın aksine — beyan mekanizması kendisi deterministik, çünkü `niyet.coz`
LLM'siz).

### 15.5 Test durumu

- Hedefli: `test_kirilim_beyani.py` (6 test, biri canlı-yakalı regresyon) +
  `test_gorsel_ayristir_anlat_cevaba_ulasir.py` (6) + `test_kosum_notu_cumledir.py`
  (4) + `plan_tuketici`'ye dokunan 25 dosyalık demet (396 test) → **395 geçti, 1
  kırmızı** — `§13.2`'de bulunan, **aynı, ilgisiz** garson-katalog-budama kusuru.
- Bundle-sonu korpus kapısı (`lab/kapi.py --tam`) **arka planda koşuyor** —
  `KAPI TOPLU KOŞULUR` kuralına göre iki düzeltme (§13+§15) için **tek** koşum.
  Sonuç gelince buraya eklenecek.

### 15.6 §14.1 karar tablosunun güncellenmiş hâli

| # | karar | durum |
|---|---|---|
| 2 | Sözleşme boşluğu | ✅ kapandı (§13) |
| 3 | Sessiz ikame | ✅ kapandı (§15) — **beyan edildi, `iki_cube` yeteneği eklenmedi** (bilerek: `§3.4`'ün Arrow-teoremi bulgusu hâlâ geçerli, bu iki farklı küpü birleştirmiyor, yalnız düşüşü görünür kılıyor) |
| 4 | Garson-katalog-budama | ❓ hâlâ kullanıcı kararı bekliyor |

§14.3'ün koşulu hâlâ geçerli: §7'nin büyük mimari genişlemesi ancak korpus/canlı
ölçüm bu iki düzeltme sonrası **hâlâ** anlamlı bir arıza oranı gösterirse gündeme
gelecek.

---

## §16 — GÖRSEL DOĞRULAMA (Playwright/Chromium, gerçek tarayıcı, gerçek ekran)

Şimdiye kadarki tüm doğrulama `curl`/API seviyesindeydi. Bu bölüm son adımı
tamamlıyor: **kullanıcının gerçekten göreceği ekranda**, gerçek bir tarayıcıda
(Playwright'ın kendi Chromium'u — sistem Chrome'u değil, başka bir ajanın
kullanımıyla çakışmasın diye).

**Yöntem:** frontend (`pnpm dev`, `:3000`) ayağa kaldırıldı, `demo-boyahane`
hesabıyla giriş yapıldı, kullanıcının **birebir cümlesi** soru kutusuna yazıldı,
gelen 5 adımlık plan önizlemesi "koş" ile onaylandı.

**Sonuç — iki ekran görüntüsüyle doğrulandı:**

1. **Grafik gerçekten render ediliyor** — gerçek bir çubuk grafik, `toplam_ciro`
   ölçüsü, "kırılım: musteri ▾" etiketli seçilebilir dropdown, ortalama referans
   çizgisi (kesikli "Ort" çizgisi). §13'ün düzeltmesinin ekran kanıtı.
2. **Beyan metni ekranda, tam görünür, gerçek DOM içinde** (`display:block`,
   `visibility:visible`, gerçek yükseklik — collapsed/gizli değil):
   > *"⚠ İstenen kırılım(lar) bu cevaba yansımadı: kalem, satis_temsilcisi —
   > seçilen veri kümesinde yok, onun yerine musteri kullanıldı."*
   §15'in düzeltmesinin ekran kanıtı — kullanıcı artık bunu **kendi gözüyle**
   görebiliyor, yalnız API cevabında gömülü değil.

**Sonuç:** §13 ve §15'in düzeltmeleri yalnız API seviyesinde değil, **kullanıcının
fiilen kullandığı arayüzde de** doğrulandı. Bu operasyonun ampirik döngüsü
(§10 canlı teşhis → §13/§15 düzeltme → §16 görsel doğrulama) burada kapanıyor.

⚠ Not: aynı ekranda "İPLİK GRUBU"/"KUMAŞ CİNSİ"/"MAKİNE"/"VARDİYA" başlıklı,
çok daha zengin bir **çoklu-boyut kırılım paneli** de görüldü (`contribution`
alanının frontend'de zaten var olan geniş gösterimi) — bu operasyonun kapsamı
dışında ama kayda değer: `AYRISTIR`'in çıktısı, benim eklediğim tek-boyutlu
`contribution` alanının ötesinde, frontend'de zaten çok daha zengin bir bileşen
tarafından tüketiliyor. Bu, §13'ün "yalnız var olan sözleşmeyi doldur" seçiminin
doğru olduğunu bir kez daha doğruluyor — frontend zaten bu veriyi bekliyordu.
