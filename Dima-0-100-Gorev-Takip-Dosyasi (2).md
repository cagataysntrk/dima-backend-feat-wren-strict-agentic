> ⚠️ **ÜRÜN ŞARTNAMESİ — MİMARİ OTORİTE DEĞİLDİR.** Bu dosya ürün kapsamını, ticari modeli ve
> kabul testlerini tanımlar ve bu haliyle değerlidir. Ancak kodu tanımayan biri tarafından
> yazılmıştır ve mimari varsayımlarının bir kısmı gerçekle uyuşmuyor:
> (1) kavramsal çerçevesinde **sorgu-anı JOIN yok** — `1.11c` join'i cube tanımında sabitliyor,
> `1.11b` çapraz-cube'u aritmetik formül DSL'i sanıyor; oysa `4.8` (kök-neden) tam da bunu
> gerektiriyor; (2) buradaki **FAZ numaraları ekibin "faz N" ifadeleriyle AYNI ŞEY DEĞİL** —
> ikisini birlikte okuyup ilerleme yüzdesi çıkarma; (3) **teknoloji yığını gerçekle uyuşmuyor**
> (NestJS/Redis/Vault/BullMQ/Temporal/LangGraph/Vega-Lite ↔ tek Python-FastAPI + threading +
> ECharts). Ayrıntılı karşılaştırma ve gerekçeler: **`backend/MIMARI.md §8.3`**.
> Not: dosyadaki hiçbir kutu işaretli değil (PDF→MD dönüşümünde kayboldu) — gerçek durum
> `HANDOFF_DOCS/` ve git geçmişindedir.



## D İ M A
## 0 → 100
Faz ve Görev Takip Dosyası
Wren motoru + yeni backend · UpcyBrain mimari/logic yeniden yazımı
Vizyon gereksinim kütüğü · görev şartnameleri · faz bazlı kabul testleri
v1→v6 ürün yol haritası · pazar stratejisi · maliyet ve fiyatlandırma — tek
dosyada
240 görev · 19 faz%90 = demo hazırP0: 152 · P1: 74 · P2: 14
361 kabul testi + 52 E2E17 ticari strateji bölümü
106 vizyon gereksinimi53 açık kaynak kararı
Kapsama kontrolü: otomatik
İç kullanım · takip dosyası · 18 Temmuz 2026 · Gizlidir
DİMA · 0→100 Görev Takip Dosyası1 / 126

## Fazlar
YÖNETİCİ ÖZETİ · önce bu iki sayfaözet
GELİŞTİRİCİ ÖNSÖZÜ · teknik girişbaşlangıç
VİZYON GEREKSİNİM KÜTÜĞÜ · tam kapsamkapsam
FAZ 0 — Temel & İskelet→8%
FAZ 1 — Kurulum Sihirbazı + Excel→DB + İlk Sorgu→22%
FAZ 2 — GenBI Çekirdeği: Grafik + Yorum + Öneri→40%
FAZ 3 — Rapor + Dashboard + Bağlamsal Hafıza→56%
## FAZ 3B — İŞ BAĞLAMI, GÖREV VE RİTİM MOTORU→62%
FAZ 4 — Agentic Analiz + Chat-İçi Dashboard→72%
FAZ 5 — Otomatik Açılış Panosu + Global Şirket Hafızası→82%
FAZ 6 — Analist Katmanı: SWOT / Tahmin / What-if / Öneri→90%
FAZ 6B — KARAR MOTORU — Karar Alma Merkezi→93%
FAZ 7 — Trust & Governance (Tam Sürüm)→96%
FAZ 8 — Ölçek, Öğrenme, Sektör Paketleri→98%
## FAZ 8B — ERP SEMBİYOZU VE AGENTIC VERİ GİRİŞİ→99%
FAZ 9 — Genişleme Yüzeyleri & Cila→100%
FAZ 9B — DIŞ KATMAN — FRONTDESKdış yüzey
FAZ 10 — v4 — KURUMSAL BİLGİ HUB'I & Yapılandırılmamış Bağlamv4
FAZ 11 — v5 — CANLI AKIL: Toplantı Ajanı & Red Teamv5
FAZ 12 — v6 — KÜLLİ AKIL: Simülasyon, Proaktif Keşif, Kolektif Zekâv6
FAZ 12B — İLERİ İŞ MOTORLARIdikey zekâ
FAZ 13 — Ar-Ge / Vizyon Tier — taahhüt değil keşifAr-Ge
SEKTÖREL UÇTAN UCA SENARYOLARentegrasyon
AÇIK KAYNAK TEKNOLOJİ HARİTASIkarar kütüğü
KAPSAMA MATRİSİkontrol
ÜRÜN YOL HARİTASI · v1 → Nihai Vizyonvizyon
## T1 · Sürüm × Pazar × Fiyat Eşlemesiticari
T2 · Pazar Teşhisi ve Rekabetticari
T3 · Marka Kimliği, Konumlama ve Dilticari
T4 · Hedef Kitle, Anti-ICP ve Tetikleyicilerticari
DİMA · 0→100 Görev Takip Dosyası2 / 126

T5 · Pazara Giriş Modeli ve Kanallarticari
## T6 · Satış Oyun Kitabıticari
T7 · Pazarlama, İçerik ve Gerillaticari
## T8 · Maliyet Modeliticari
T9 · Fiyatlandırma, Paketler ve Pazarlıkticari
T10 · Hendekler ve Rekabet Savaşıticari
T11 · Kademeli Fetih ve Tekelleşmeticari
T12 · Metrikler ve Erken Uyarıticari
T13 · Riskler ve Kırmızı Çizgilerticari
## T14 · Stratejik Büyüme Motorlarıticari
T15 · Stratejik İş Birlikleri ve Ekosistemticari
## T16 · İlk 90 Gün: Haftalık İnfaz Planıticari
## T17 · Kilit Kararlar Özetiticari
DİMA · 0→100 Görev Takip Dosyası3 / 126

## YÖNETİCİ ÖZETİ
Bu belge hem bir ürün şartnamesi hem bir iş planıdır. Teknik ekip için ne inşa edileceğini, ticari ekip için kime hangi sözle
satılacağını aynı dosyada tutar — çünkü bu ikisi ayrı belgelerde yaşadığında ürün pazardan, pazar üründen kopar.
Dima nedir — bir cümlede
Dima, bir şirketin kendi veritabanına bağlanıp Türkçe soru sorulabilen, cevabı grafik ve yorumla veren, her sayının
kaynağını kanıtlayabilen ve nihayetinde kararları yöneten bir kurumsal karar merkezidir.
Marka özü: “Kurumunuzun asla yalan söylemeyen beyni.”
Çözdüğümüz problem
Orta-büyük Türk şirketlerinde veri var, cevap yok. Basit bir soru için birinin rapor çekmesi, Excel’e dökmesi, filtrelemesi
gerekir: saatler, bazen günler. Bu arada karar gecikir. Mevcut alternatifler ise üç ayrı sebeple tıkanır: BI araçları soru
sormaya izin vermez (önceden tanımlı ekranlar), genel yapay zekâ veriyi yurt dışına taşır ve uydurur, analist
istihdamı pahalı, yavaş ve kişiye bağımlıdır.
Neden şimdi
KVKK 12 Mart 2026’da Etken Yapay Zekâ rehberini yayımladı; ceza tavanı 17.092.242 TL, ihlal bildirimi 72 saat, ve
şeffaflık ilkesi gereği kararın algoritmik mantığı açıklanabilir olmalı. Bu düzenleme, Dima’nın mimarisini bir “özellik”
olmaktan çıkarıp doğrudan mevzuat cevabı hâline getirdi. Aynı anda hyperscaler’lar Türkçe/KVKK/veri-ikameti tarafında
boş; benzer model (egemenlik + deterministik katman) Almanya’da kanıtlanmış durumda. Tahmini öncelik penceresi:
12–18 ay.
Neyi farklı yapıyoruz — üç yapısal fark
Veri kurumdan çıkmaz. Yapay zekâ tablo ve kolon adlarını görür, gerçek değerleri asla — bu bir vaat değil,
mimari zorunluluktur (iki düzlem mimarisi).
Uydurmaz, kanıtlar. Tanımlı metrikler yapay zekâ hiç devreye girmeden hesaplanır; her cevabın çalışan sorgusu,
model sürümü ve zaman damgası saklanır ve yeniden koşulabilir.
Kullandıkça ucuzlar. Tekrarlayan sorular otomatik olarak deterministik metriğe terfi eder; yapay zekâ maliyeti
zamanla düşerken güven yükselir. Rakiplerin çoğunda her soru bir maliyet kalemidir.
Ürün yolculuğu — altı sürüm
SürümÜrün ne hâle gelirKime satılır
v1  Kanıt MotoruSoru sor, saniyede grafik + yorum al, kaynağını görRaporu hazırlayan + patron
v2  Proaktif AnalistKök-neden, tahmin, senaryo; sorulmadan uyarırC-Level, operasyon
v3  Karar MerkeziSeçenek kıyaslar, kanıtlar, imzalı karar kaydı tutarKurul, CFO, regüle kurumlar
v4  Bilgi HubıSözleşme, prosedür, toplantı notu, strateji notunu da bilirİK, operasyon, denetim
v5  Canlı AkılToplantıya katılır, karar çıkarır, karşıt akıl olurHolding, yönetim kurulu
v6  Külli AkılFırsat keşfeder, kriz simüle eder, sektörle kıyaslarGlobal kurumsal
v3 çekirdek ürünün tamamlandığı noktadır (%100); v4–v6 nihai vizyondur.
Ticari model — özet
KalemYaklaşım
Hedef müşteri50–500 çalışan, ERP’si olan, çok şubeli/hatlı üretici-dağıtıcı
Giriş modeliAşağıdan-yukarı: raporu hazırlayan kişiden başla, patrona çık
İlk kanallarMali müşavir · KVKK danışmanı · sektör derneği · ERP bayisi
Fiyat$190 – $1.900+/ay abonelik + $1.500 – $12.000 kurulum; fiyat çıpası analist maaşı
Brüt marjYıl-1 ~%73 · Yıl-2+ ~%80 (terfi motoru maliyeti düşürdükçe)
HendekAnlamlandırma emeği → kurumsal hafıza → denetim tarihçesi → sektör kıyas verisi
Şu anki durum ve en büyük risk
Durum: Mimari ve yol haritası hazır; motor (Wren) açık kaynak olarak mevcut; ürünün kendisi sıfırdan yazılıyor. Demo
hedefi: Faz 0–6 (%90 çizgisi).
önce bu iki sayfa
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası4 / 126

En büyük risk teknik değil ticari: henüz ödeme yapan doğrulanmış müşteri yok. Bu belgedeki her şey — mimari,
testler, strateji — ilk 2-3 referans müşteri gelene kadar varsayımdır. Bu yüzden ilk 90 gün planı inşa değil, ilk müşteriyi
bulma üzerine kuruludur.
Bu belge nasıl kullanılır
KimNereden başlarNe bulur
GeliştiriciGeliştirici Önsözü → Faz 0Her görev için amaç, adım adım nasıl, bitti sayılır kriteri
Test / QAHer fazın sonu + E2E bölümü361 kabul testi + 52 sektörel uçtan uca senaryo
Ürün yöneticisiÜrün Yol HaritasıHer sürümde ürünün ne yapıp ne yapmadığı, örnek diyaloglarla
Ürün / kapsam sahibiVizyon Gereksinim Kütüğü106 gereksinim, kaynağı ve hangi görevde karşılandığı
Kurucu / satışTicari Strateji bölümleri (T1–T17)ICP, satış oyun kitabı, itiraz bankası, fiyat, büyüme, ortaklıklar
Yatırımcı / danışmanYönetici Özeti → T1 → T9Pazar, model, ekonomi ve yol haritası
Tek cümlelik tez: Kurumsal kararı sezgiden kanıta taşımak — veriyi kurumdan çıkarmadan, uydurmadan, her
adımı denetlenebilir kılarak.
Disiplin:ENG ENGUI UILLM LLMWREN WRENVIZ VIZDATA DATAGOV GOV
Öncelik:P0P1P2  (P0 demo-kritik · P1 ürün · P2 genişleme)
Etiketler:D=demo senaryo · S=külliyat senaryo · F=mevcut/hedef özellik · Y=geliştirilecek · UX =arayüz fikri ·
BE =backend sistemi · w... =Wren motor kalemi
Kutu (☐): tamamlanınca işaretlenir · ID:  Faz.Sıra
DİMA · 0→100 Görev Takip Dosyası5 / 126

## GELİŞTİRİCİ ÖNSÖZÜ
Bu dosyayı ilk kez açıyorsan buradan başla. Projenin ne olduğunu, hangi parçalardan oluştuğunu ve görev kartlarının nasıl
okunacağını 3 dakikada anlatır.
1 · Dima nedir?
Dima, bir şirketin kendi veritabanına bağlanıp doğal dilde soru sorulabilen, cevabı grafik ve yorumla veren, ve en
önemlisi her cevabın kaynağını kanıtlayabilen bir karar destek sistemidir. Klasik BI araçlarından farkı soru
sorulabilmesi; ChatGPT gibi araçlardan farkı ise (a) verinin şirket dışına çıkmaması, (b) uydurmaması — bilmediğinde
açıkça söylemesi, (c) her sayının hangi SQL ile üretildiğinin kaydedilmesi.
2 · Sistem neyden oluşuyor?
Wren (hazır motor): Açık kaynak, Rust tabanlı semantik sorgu motoru. Bizim yazmadığımız kısım. Veri modelini (MDL)
okur, ondan doğru SQL üretir ve müşteri veritabanında çalıştırır. Biz onu bir Python servisiyle sarmalıyoruz.
Dima (bizim yazdığımız): Motorun etrafındaki her şey — arayüz, kullanıcı/yetki yönetimi, yönlendirme, yapay zekâ
orkestrasyonu, güven ve kanıt katmanı, hafıza, karar motoru. Ürünün değeri buradadır.
Teknoloji: Next.js (arayüz) · NestJS/TypeScript (ana backend) · Python/FastAPI (Wren sarmalayıcı) · PostgreSQL (Dima'nın
kendi verisi) · Redis (kuyruk ve cache) · Vault (müşteri DB şifreleri) · Git (veri modeli sürümleme).
3 · Bir soru sistemden nasıl geçer?
Kullanıcı soru yazar → Router soruyu sınıflandırır → eğer tanımlı bir metrikse doğrudan Cube'a gider (yapay zekâ hiç
devreye girmez, buna altın yol diyoruz) → değilse cache'e bakılır → yoksa LLM   devreye girer, SQL üretir, üç kademeli
kontrolden geçer → sonuç Provenance (kanıt kaydı) ile birlikte kullanıcıya döner. Amacımız zamanla soruların çoğunun
altın yoldan gitmesi: hem daha güvenilir hem bedava.
4 · Görev kartı nasıl okunur?
Her kart şu bilgileri taşır: ☐ kutu (bitince işaretle) · ID  (Faz.Sıra, ör. 2.11) · disiplin rozeti (ENG=backend, UI=arayüz,
LLM=yapay zekâ, WREN=motor bağlama, VIZ=görselleştirme, DATA=veri, GOV=güvenlik/yönetişim) · öncelik (P0=kritik,
P1=önemli, P2=sonra) · başlık    ·  etiketler (hangi senaryo/özellikten geliyor).
Altındaki gri kutuda: AMAÇ    (neden yapıyoruz), NASIL    (adım adım yapılacaklar), BİTTİ SAYILIR (bu maddeler doğruysa
görev tamamdır). Kod yazmadan önce bu üçünü oku.
5 · Sırayla mı gitmeliyim?
Fazlar bir sıra önerir ama her faz bağımsız değer üretir. Faz 0-6 arası demo için zorunludur (%90 = demo hazır). Faz
içindeki P0 görevleri önce bitir. Bazı görevlerin başında ★ ÖN ŞART yazar — o bitmeden aynı fazın devamına geçilmez (ör.
10.1 kanıt sınıfı ayrımı, 11.1 toplantı kaydı hukuki çerçevesi).
6 · Kabul testleri (use-case'ler) nasıl kullanılır?
Her fazın sonunda o faza ait kabul testleri tablosu vardır. Görevleri bitirdikten sonra bu tabloyu baştan sona geç: her
satırdaki eylemi yap, beklenen sonucun gerçekleştiğini doğrula. Hepsi geçmeden faz bitmiş sayılmaz.
Test tipleri:TEMEL = normal kullanım (mutlu yol) · SINIR = uç ve hatalı durumlar (asıl kaliteyi bunlar belirler) ·
GÜVENLİK = yetki, gizlilik, veri sızıntısı · REGRESYON = daha önce çalışan bir davranış bozulmamalı.
Bu testler aynı zamanda otomatik test yazarken şartname olarak kullanılmalıdır: her UC bir test fonksiyonuna karşılık
gelmelidir. GÜVENLİK tipindekiler CI'da her derlemede koşmalıdır.
7 · Ürünün tam kapsamı nerede yazılı?
Bir sonraki bölüm olan Vizyon Gereksinim Kütüğü, ürünün ne olacağını 106 maddede tanımlar ve her maddeyi bir
göreve bağlar. Bir özellik tartışılırken önce oraya bakın: kütükte yoksa kapsam dışıdır, varsa hangi görevde yapıldığı
yazılıdır. Kapsam tartışmaları böyle biter.
Faz harfli olanlar (3B, 6B, 8B, 9B, 12B) sonradan eklenen ama omurgaya oturan bloklardır; numaralandırma
bozulmasın diye harfle ayrıldılar, önem sırasında bir eksiklikleri yoktur.


DİMA · 0→100 Görev Takip Dosyası6 / 126

TerimNe demek
MetrikCube'un üstüne iş anlamı eklenmiş tanım: görünen ad, eşanlamlılar, birim, sahibi, hedefi.
Provenance / ContractBir cevabın kimlik kartı: çalışan SQL, kullanılan model sürümü, parametreler, sonuç özeti (hash),
zaman. Denetçi bununla doğrular.
Güven rozeti磊 altın (deterministik), 賂 gümüş (doğrulanmış), 雷 bronz (yapay zekâ tahmini). Sistem
hesaplar, LLM kendine puan vermez.
DCM (AI_MODE=off)Yapay zekânın tamamen kapatıldığı mod. Menü ve sihirbazla çalışır; banka/kamu için satış
argümanı.
RLS / CLSSatır ve kolon bazlı güvenlik. Kullanıcı yalnız yetkili olduğu satırları/kolonları görür; motor
seviyesinde uygulanır.
Plane EnforcerHam verinin LLM'e gitmesini engelleyen katman. LLM tablo/kolon adlarını ve istatistikleri görür,
gerçek değerleri asla.
Kanıt sınıfıBilginin türü: kesin veri (ERP) mi, duyum/bağlam (toplantı, haber) mı. İkisi asla karıştırılmaz.
Cortex / hafızaSistemin öğrendikleri: şirket profili, kurallar, tanımlar, kullanıcı tercihleri. Seçici kaydeder, her şeyi
değil.
Terfi motoruYapay zekâya giden tekrarlayan soruları tespit edip metrik haline getiren mekanizma. Sistem
kullandıkça ucuzlar.
Karar KaydıBir kararın değişmez kaydı: seçenekler, kriterler, kanıtlar, varsayımlar, tavsiye, karar sahibi.
Golden evalDoğruluğu ölçmek için hazırlanan soru-cevap seti. Gece çalışır, doğruluk düşerse uyarır.
DİMA · 0→100 Görev Takip Dosyası7 / 126

## VİZYON GEREKSİNİM KÜTÜĞÜ
Bu kütük ürünün tam kapsamını tek listede tutar. Her gereksinim bir veya daha fazla göreve bağlıdır ve kapsama matrisinde
ayrıca doğrulanır. Kaynak etiketi fikrin nereden geldiğini gösterir.
Kaynak dağılımı ve nasıl okunmalı
## K
47  doğrudan istenen ·
## B
30  vizyon belgelerinden ·
## E
29  bu çalışmada eklendi
En kritik grup B (İş Bağlamı): “veritabanı iş değildir”. Sistem şirketin ne sattığını, nasıl para kazandığını ve hangi
takvimde yaşadığını bilmeden ne proaktif olabilir ne isabetli. Bu grubun 11 maddesinin 8’i bu çalışmada eklendi — çünkü
“business verilerini de güncel tutmak gerekir” cümlesiyle işaret edilen ama açılmamış olan katman burasıdır. Faz 3B
tamamen bu boşluğu kapatmak için kurulmuştur.
KodGereksinimGörev(ler)
Ø · ÇEKİRDEK ÜRÜN — VERİDEN KARARA— asıl ürün budur: her şey bu zincirin üstüne kurulur
## Ç1
## K
Çoklu veri kaynağı bağlama
Veritabanı, Excel, dosya ve API kaynaklarının tek sisteme bağlanması.
## 1.1  ·  1.8  ·  9.3
## Ç2
## K
Anlamlandırma / semantik katman
Metrik, küp, boyut, eşanlamlı ve ilişki tanımları — sistemin veriyi 'anladığı' yer.
## 1.2  ·  1.10   ·  1.11a    ·  1.11c
## Ç3
## K
Türkçe doğal dilde soru sorma
Teknik bilgi gerektirmeden, kendi diliyle sorgulama.
## 1.6  ·  1.9  ·  1.13
## Ç4
## K
Deterministik metrik cevabı (altın yol)
Tanımlı metrikler yapay zekâ devreye girmeden, kesin ve tekrarlanabilir hesaplanır.
## 1.11   ·  1.11b    ·  2.11
## Ç5
## K
Otomatik grafik üretimi
Veriye uygun grafik türünün seçilmesi ve etkileşimli çizimi.
## 2.1  ·  2.2  ·  2.3  ·  9.1
## Ç6
## K
Zorunlu içgörü yorumu
Her grafiğin altında: ne oluyor / neden / ne yapmalı. Salt sayı tekrarı yasaktır.
## 2.5  ·  4.4  ·  6.15
## Ç7
## K
Tıklanabilir öneri zinciri
Derinleşme ve karşılaştırma önerileri; analiz zincir hâlinde ilerler.
## 2.6  ·  2.7  ·  2.10
## Ç8
## K
Rapor üretimi
Biriken analizlerin paylaşılabilir belgeye dönüşmesi (Excel/PDF/tablo/karşılaştırmalı).
## 3.1  ·  6.5
## Ç9
## K
Pano üretimi ve kalıcılığı
Grafiklerin canlı veriyle yenilenen, izinli, filtrelenebilir panolara sabitlenmesi.
## 2.8  ·  3.2  ·  3.4
## Ç10
## K
Kanıt zinciri
Her sayının kaynağı: formül, tablo, çalışan sorgu, model sürümü, zaman.
## 2.15   ·  7.1  ·  7.8
## Ç11
## K
Dürüst red
Bilmediğinde uydurmaz; sebebini ve çözümünü söyler.
## 2.16   ·  7.3
## Ç12
## K
Kalibre edilmiş güven rozeti
Cevabın ne kadar güvenilir olduğu sistemce hesaplanır; LLM kendine puan vermez.
## 2.17   ·  2.18   ·  7.2
## Ç13
## K
Kök-neden analizi
'Neden düştü' sorusuna yüzde katkılarıyla ayrıştırılmış cevap.
## 4.8  ·  6.9  ·  6.15
## Ç14
## K
Tahmin ve senaryo (what-if)
Aralıklı tahmin ve deterministik senaryo simülasyonu.
## 6.3  ·  6.4  ·  12.2
## Ç15
## K
Karar motoru
Seçenek üretimi, kriter-ağırlık, kanıt matrisi, ret gerekçesi, imzalı karar kaydı.
## 6.11   ·  6B.1   ·  6B.5   ·  6B.8
## Ç16
## K
Dışa aktarım
Excel, PDF, görsel ve CSV olarak paylaşılabilir çıktı.
## 2.4  ·  3.1
## Ç17
## K
Veri egemenliği ve AI-kapalı mod
Veri kurumdan çıkmaz; yapay zekâ tamamen kapalıyken de çalışır.
## 2.12   ·  4.12   ·  7.4  ·  7.10
## Ç18
## K
Çok kullanıcılı yetki (RLS/CLS)
Herkes yalnız yetkili olduğu satır ve kolonu görür.
## 7.5  ·  8.1  ·  9B.3
106 gereksinim · 11 grup
DİMA · 0→100 Görev Takip Dosyası8 / 126

KodGereksinimGörev(ler)
A · İZLEME, KORUMA VE PROAKTİFLİK— işi görmek, tehdidi yakalamak, fırsatı kaçırmamak
## R1
## K
Günlük durum görünürlüğü
İşin bugünkü hâli tek bakışta: ne bitti, ne aksadı, ne bekliyor.
## 3B.11
## R2
## K
Tehdit ve risk erken uyarısı
Sorun büyümeden haber verme; eşik ve anomali tabanlı.
## 8.10
## R3
## K
Fırsat keşfi
Sormadığınız sorunun cevabı: gece taramasıyla bulunan kazanç fırsatları.
## 12.1
## R4
## K
Gelişim yol haritası
Ay/çeyrek bazında 'şunu yaparsanız şu kadar iyileşir' planı.
## 6.14
## R5
## K
Sürekli iyileştirme önerileri
Küçük ama biriken operasyonel düzeltmeler.
## 6.14
## R6
## K
Sabah brifingi ritüeli
Dün ne oldu · bugün ne var · yarın ne gelir · fırsat · öneri.
## 3B.11
## R7
## K
Departman + genel çift görünüm
Her departmanın kendi paneli ve tüm şirketin birleşik görünümü.
## 3B.12
## R8
## K
Anomali tespiti ve bildirimi
Beklenmeyeni yakala, kime ait olduğunu bul, sahibine bildir.
## 8.10
## R9
## E
Bildirim yorgunluğu yönetimi
Uyarıların önem sırasına göre gruplanması ve susturulması; gürültü, körlüğe yol açar.
## 3B.13
B · İŞ BAĞLAMI VE GÜNCELLİK— en kritik ve en az konuşulan katman: veritabanı iş değildir
## R10
## K
İş tanımı kütüğü
Ne satıyoruz, kime, nasıl para kazanıyoruz, kritik başarı faktörü ne?
## 3B.1
## R11
## E
Süreç haritası
Sipariş→üretim→sevkiyat→tahsilat gibi uçtan uca akışların tanımı; darboğaz buradan bulunur.
## 3B.1
## R12
## E
Organizasyon ve rol/yetki matrisi
Kim neyden sorumlu, kim neyi onaylar, kim neyi görebilir.
## 3B.1
## R13
## E
Ürün/hizmet kataloğu + reçete (BOM)
Maliyet, marj ve karbon hesaplarının ortak zemini.
## 3B.2
## R14
## E
Tedarikçi ve müşteri kartları
Vade, performans, risk skoru, geçmiş davranış.
## 3B.2
## R15
## B
Sözleşme envanteri
Cezai şartlar, vade, yenileme tarihleri, riskli maddeler.
## 3B.2
## R16
## E
Kurumsal takvim ve mevsimsellik
Ay sonu kapanış, denetim, sezon, bütçe dönemi — proaktifliğin isabeti buna bağlıdır.
## 3B.3
## R17
## E
Bilgi sahipliği + tazelik SLA
Her iş bilgisinin bir sahibi ve yenilenme periyodu vardır; sahipsiz bilgi bayatlar.
## 3B.4   ·  5.12
## R18
## E
Bağlam bakım ajanı
'Bu bilgi 90 gündür güncellenmedi, hâlâ geçerli mi?' diye soran arka plan ajanı.
## 5.12
## R19
## E
İş terimleri sözlüğü
Şirketin kendi diliyle tanımlar; 'net satış' tartışması burada biter.
## 3B.5
## R20
## E
Paydaş haritası
Kim kimden ne bekliyor; iç ve dış beklenti ağı.
## 3B.3
C · KATMANLI HAFIZA AĞI— kişiden sektöre yedi katman, sürekli beslenen
## R21
## K
Kişi hafızası
Yöneticinin çalışma tarzı, format tercihi, karar alışkanlığı.
## 5.11
## R22
## K
Departman hafızası
Finans/üretim/İK'nın kendi süreç bilgisi ve geçmişi.
## 5.11
DİMA · 0→100 Görev Takip Dosyası9 / 126

KodGereksinimGörev(ler)
## R23
## K
Şube/tesis hafızası
Yerel koşullar: 'Kadıköy'ün kronik nakit sıkıntısı', 'B fabrikası hat-3 arıza geçmişi'.
## 5.11
## R24
## K
Şirket/holding hafızası
Strateji, kültür, kurumsal anayasa, kurucu ilkeleri.
## 5.11
## R25
## K
Sektör/benchmark hafızası
k-anonimlik korumalı kıyas havuzu.
## 5.11
## R26
## K
Sistem geneli hafıza
Anonimleştirilmiş çapraz-müşteri öğrenmesi.
## 5.11
## R27
## B
Çürüme ve unutma motoru
Eskiyen bilginin ağırlığı düşer, arşive iner — silinmez.
## 5.9
## R28
## E
Hafıza çelişki yönetimi
İki katman çeliştiğinde hangisi kazanır: tercihte kişi, tanımda şirket, kuralda politika.
## 5.7
## R29
## E
Hafıza şeffaflığı
Kullanıcı kendisi hakkında bilinenleri görebilir, düzeltebilir, silebilir (KVKK).
## 5.10
D · GÖREV VE AKSİYON MOTORU— konuşmadan işe, işten takibe
## R30
## K
Chat'ten görev oluşturma ve atama
'Şu tedarikçiden teklif istensin' → görev + sorumlu + tarih.
## 3B.6
## R31
## K
Görev takibi ve durum
Ne bitti, ne aksadı, ne tıkandı.
## 3B.6
## R32
## K
Görev önerisi
'Ne yapılmalı' sorusuna veriye dayalı cevap.
## 3B.7
## R33
## K
Dış görev aracı entegrasyonu
Jira, Asana, Trello, ClickUp, Monday ile çift yönlü senkron.
## 9.12
## R34
## K
İç görev tahtası
Dış araç yoksa sistemin kendi tahtası.
## 3B.6
## R35
## E
Görev–karar/bulgu bağı
Her görev bir bulguya veya karara bağlıdır; 'bu iş neden var' izlenebilir olmalı.
## 3B.8
## R36
## E
Görev sağlığı izleme
Sahipsiz, süresi geçmiş, tıkanmış, tekrar açılmış görevlerin tespiti.
## 3B.9
## R37
## E
Taahhüt yakalama
Sohbet veya toplantıda verilen sözün otomatik göreve dönüşmesi.
## 3B.10
## R38
## E
Eskalasyon matrisi
Hangi durum, ne kadar sürede, kime yükselir.
## 7.9
E · DEPARTMAN PODLARI— her departmanın kendi uzman alt beyni
## R39
## K
Üretim/operasyon podu
Kişi ve makine bazlı verimlilik, OEE, duruş, fire kök-nedeni.
## 6.12
## R40
## K
Finans/muhasebe podu
Nakit projeksiyonu, erken ödeme fırsatı, vergi/kur riski, senaryo.
## 6.12
## R41
## B
Satış/pazarlama podu
Churn riski, kanal komisyon kaybı, fiyat esnekliği, ROI eleği.
## 6.12
## R42
## B
İK/prosedür podu
Oryantasyon, SOP rehberliği, yetenek boşluğu, devir analizi.
## 6.12
## R43
## E
Satınalma/tedarik podu
Tedarikçi performansı, alternatif kaynak, fiyat endeksi takibi.
## 6.12
## R44
## E
Kalite podu
CAPA, lot izlenebilirliği, şikayet–üretim bağı.
## 6.12
## R45
## E
IT/güvenlik podu
Yetkisiz sorgu, veri sızıntısı, gölge-BT radarı.
## 6.12
DİMA · 0→100 Görev Takip Dosyası10 / 126

KodGereksinimGörev(ler)
## R46
## B
Departman hakemi
Çatışan departman hedeflerinde uzlaşma noktası bulma (oyun teorisi).
## 6B.14
## R47
## E
Pod sağlık skoru
Her departmanın kendi karnesi ve trendi.
## 6.12
F · ERP SEMBİYOZU VE VERİ GİRİŞİ— ERP rakip değil, resmî kayıt defteri
## R48
## K
ERP okuma entegrasyonu
ERP kayıt defteridir; sistem onun üstünde çalışır, yerine geçmez.
## 8B.1
## R49
## K
Agentic veri girişi
Ses, fotoğraf veya WhatsApp mesajından yapılandırılmış kayıt taslağı.
## 8B.2
## R50
## B
Şema ve politika doğrulama
Girdi ERP şemasına uygun mu, kural ihlali var mı, PII maskeli mi.
## 8B.3
## R51
## K
İnsan onaylı yazma
Tampon bölgeye yaz → onay kartı → ERP'ye işle. Onaysız yazma yok.
## 8B.4
## R52
## E
Geri alma ve tam denetim izi
Her yazma işlemi geri alınabilir ve kime ait olduğu izlenebilir.
## 8B.5
## R53
## E
ERP-agnostik adaptör
Logo, Netsis, SAP, Mikro... her biri için ayrı ürün değil, tek adaptör katmanı.
## 8B.1
## R54
## E
Giriş hızı ölçümü
'ERP formundan kaç kat hızlı' iddiasının sayısal kanıtı.
## 8B.6
G · SİSTEM UZMANI (AGENTIC YÖNETİM)— yanınızda bir uzman varmış gibi
## R55
## K
Chat'ten ayar ve yetki yönetimi
'Ahmet'e sadece Güney Bölgesi'ni göster' → yetki tanımlanır.
## 8.20
## R56
## K
Chat'ten metrik/kural öğretme
'OEE'yi şöyle hesaplıyoruz' → tanım kaydedilir.
## 8.20
## R57
## K
Yetenek keşfi
'Ne sorabilirim, ne yapabilirsin' → dinamik yetenek haritası.
## 8.20
## R58
## K
Kullanım rehberliği
Doküman okumadan, sohbetle öğrenme.
## 8.20
## R59
## E
Kendi kendini teşhis
'Neden yavaşım, hangi veri eksik, hangi bağlantı bozuk' — sistemin kendi sağlık raporu.
## 8.21   ·  8.24
## R60
## E
Kurulum kalitesi skoru
Sistemin ne kadar iyi kurulduğunun ölçümü; eksik tanım, kopuk kaynak, sahipsiz metrik.
## 8.21
H · KÖK MOTORLAR— her şeyin üstünde durduğu altı merkezî çekirdek
## R61
## B
Nedensellik grafı
Korelasyon değil neden-sonuç: makine duruşu → teslimat gecikmesi → OEE düşüşü zinciri.
## 6.13
## R62
## B
Telos/OKR senkronizasyonu
Her öneri ve görev, şirketin ana hedefine katkısıyla (Delta-KPI) tartılır.
## 6B.13
## R63
## B
Refleks yayı
Hızlı omurilik tepkisi (kural, $0) ile derin bilişsel döngü (LLM) ayrımı.
## 4.17
## R64
## B
Hakemlik çekirdeği
Çatışan alt hedeflerde optimum uzlaşmayı bulan merkezî hakem.
## 6B.14    ·  6B.16
## R65
## B
Dikkat ve bütçe motoru (nazar)
İşlem gücünü finansal risk/fırsat büyüklüğüne göre dağıtma.
## 8.22
## R66
## B
Durum çatallama
Şirket durumunu dondurup paralel senaryolarda koşturma (Git dalı gibi).
## 12.11
## R67
## E
Kök motor gözlemevi
Altı motorun kendi sağlığını ve birbirine etkisini izleyen katman.
## 12.12
DİMA · 0→100 Görev Takip Dosyası11 / 126

KodGereksinimGörev(ler)
I · DIŞ KATMAN — FRONTDESK— içeride genel müdür, dışarıda resepsiyonist
## R68
## B
Kamu şeması
Yalnız kamuya açık veri: katalog, fiyat, SSS, çalışma saati.
## 9B.1
## R69
## B
Tampon bölge (staging)
Dışarıdan doğrudan veritabanına yazma kesinlikle yasak.
## 9B.2
## R70
## B
Müşteri-RLS + OTP
Kişi kendi verisini ancak doğrulamadan sonra görebilir.
## 9B.3
## R71
## B
Üretken arayüz kataloğu
Kaydırılabilir kartlar, görseller, PDF, fiyat tabloları.
## 9B.4
## R72
## B
Kapasite-farkında randevu
Boş saati değil, gerçekten uygun saati önerme.
## 9B.5
## R73
## B
Satış niyeti skoru
Sorulardan satın alma eğilimini okuma ve sıcak müşteriyi öne çıkarma.
## 9B.6
## R74
## B
İnsana devir protokolü
Gerginlik veya karmaşıklıkta canlı temsilciye özetle birlikte aktarma.
## 9B.7
## R75
## B
Müşteri sesi → iç istihbarat
Dışarıda sorulanların anonim olarak iç beyne rapor edilmesi.
## 9B.9
## R76
## E
Omnichannel kimlik çözümleme
Aynı kişinin WhatsApp, web ve telefon izlerini tek kimlikte birleştirme.
## 9B.8
## R77
## B
Dikey paketler
Klinik, okul, fabrika, otel, servis için hazır dış-katman senaryoları.
## 9B.10
J · İLERİ İŞ MOTORLARI— sektör bağımsız, yüksek değerli dikey zekâlar
## R78
## B
Pazarlık hazırlık motoru
Tedarikçi performansı + piyasa endeksi + stok aciliyeti → pazarlık stratejisi.
## 12B.1
## R79
## B
Marj kalkanı / dinamik fiyat
Maliyet bileşeni değişince marjı koruyacak fiyat revizyon önerisi.
## 12B.2
## R80
## B
Micro-churn radarı
Sipariş sıklığı, ödeme hızı ve ton değişiminden sessiz kaybı erken görme.
## 12B.3
## R81
## B
Sözleşme risk eleği
Cezai şart, vade ve teslimat riskinin geçmiş performansla kıyası.
## 12B.4
## R82
## B
İç proje/fikir eleği
Yatırım fikrini nakit, kapasite ve strateji kısıtlarıyla test etme.
## 12B.5
## R83
## B
Görsel saha denetçisi
Fotoğraf/kameradan istif, hasar, İSG ve raf denetimi.
## 12B.6
## R84
## B
Yetenek boşluğu ve halef planı
İş yükü artışına göre kadro darboğazının önceden görülmesi.
## 12B.7
## R85
## B
Nakit arbitrajı
Atıl nakdin erken ödeme iskontosu ile alternatif getiri kıyası.
## 12B.8
## R86
## B
Suistimal ve mükerrer ödeme dedektifi
Tutar, IBAN, açıklama ve onay zinciri çapraz kontrolü.
## 12B.9
## R87
## E
Karar–sonuç kütüphanesi
Verilen kararlar ve gerçekleşen sonuçların eşleştiği arşiv — öğrenilmiş sezginin tek yakıtı.
## 6B.15    ·  8.25
## R88
## E
Playbook kütüphanesi
Tekrarlayan durumlar için hazır, onaylı iş akışları.
## 8.23
DİMA · 0→100 Görev Takip Dosyası12 / 126



## AMAÇ
Uzun süren işlerde (LLM, ağır sorgu) HTTP'yi bekletmemek; kullanıcıya anlık geri bildirim verebilmek.
## NASIL
BullMQ kur (Redis üstünde). İki kuyruk: 'analysis' (LLM/ağır) ve 'quick' (hafif).
Gateway isteği kuyruğa atar, hemen jobId döner ('işleniyor' cevabı).
Worker işi bitirince sonucu WebSocket ile ilgili kullanıcıya iletir.
Ara adımlar da (düşünme adımları) aynı kanaldan stream edilir.
## BİTTİ SAYILIR
30 saniyelik bir iş sırasında arayüz donmuyor, ilerleme görünüyor.
Worker çökerse iş kuyrukta kalıyor ve tekrar deneniyor.

Kurulum Sihirbazı + Excel→DB + İlk Sorgu
[demo D1] 'Kurulum = sohbet'. Excel atılır, sistem anlamlandırır, onaylatır, ilk grafiği verir.
1.1DATAP0Excel/CSV yükleme → şema çıkarımı → DuckDB/Postgres yazımı (Wren Excel referansı)
## AMAÇ
Kullanıcının elindeki Excel'i sorgulanabilir bir veritabanı tablosuna çevirmek. Demonun ilk 'vay' anı budur.
## NASIL
Dosya yükleme ucu (.xlsx/.csv), maksimum boyut ve satır limiti koy.
Sayfa ve başlık satırını tespit et; kolon adlarını normalize et (boşluk, Türkçe karakter, mükerrer ad).
Kolon tiplerini örnekleyerek çıkar (tarih, sayı, metin) ve kullanıcıya onaylat.
Veriyi Postgres'te tenant'a ait bir şemaya yaz (veya DuckDB dosyası olarak sakla).
Yükleme özeti göster: kaç satır, kaç kolon, hangi tipler.
## BİTTİ SAYILIR
10.000 satırlık bir Excel 60 saniyeden kısa sürede yüklenip sorgulanabiliyor.
Yanlış tip tespitinde kullanıcı düzeltebiliyor ve düzeltme kaydediliyor.
1.2WRENP0generate-mdl skill → servis: kolonlardan otomatik model üretimi
## AMAÇ
Yüklenen tablodan otomatik olarak ilk semantik modeli (MDL) üretmek; kullanıcı elle model yazmasın.
## NASIL
Wren'in generate-mdl skill kullan mantığını servis olarak yaz: tablo/kolonları tara.
Her kolona tahmini açıklama ve tip ata; birincil anahtar adayını bul.
models/{tablo}/metadata.yml dosyasını üret ve target/mdl.json'a derle.
## BİTTİ SAYILIR
Excel yüklendikten sonra kullanıcı hiçbir şey yazmadan MDL üretiliyor.
Üretilen MDL ile dry-plan başarılı çalışıyor.
1.3UIP0Kurulum Agent Chat'i: 'elinde ne var?'→Excel→anlamlandır→'doğru mu?'→onay/düzelt
## AMAÇ
Kurulumu form doldurma işi olmaktan çıkarıp sohbete dönüştürmek. Ürünün en ayırt edici deneyimi.
## NASIL
Sihirbaz sohbet akışı yaz: 'Elinizde ne var?' → dosya/DB seçimi.
Dosya gelince kolonları LLM ile anlamlandır: 'tutar = satış tutarı mı?' gibi doğrulama soruları üret.
Kullanıcı onaylar veya düzeltir; her düzeltme MDL açıklamasına ve Knowledge'a yazılır.
Adım adım ilerleme göstergesi (1/4 bağlantı, 2/4 anlamlandırma...).
Kritik: kullanıcı 'bilmiyorum' derse sistem varsayım yapmaz, alanı 'belirsiz' işaretler.
## BİTTİ SAYILIR
Teknik olmayan bir kullanıcı yardım almadan kurulumu tamamlayabiliyor (5 kişiyle test edildi).
Kullanıcının verdiği her düzeltme sonraki sorgularda kullanılıyor.
1.4WRENP0İlişki önerisi + tek-tık onay (ortak anahtardan)
## AMAÇ
Birden fazla tablo yüklendiğinde aralarındaki ilişkiyi (JOIN) sistemin kendisinin önermesi.
## NASIL
Kolon adı benzerliği + değer örtüşmesi ile aday ilişkileri bul (ör. musteri_id ↔ id).
Örtüşme oranını hesapla; %90 üstü güçlü aday sayılsın.
Kullanıcıya 'Siparişler ile Müşteriler musteri_id üzerinden bağlanıyor, doğru mu?' diye sor.
Onaylanan ilişkiyi MDL'e relationship olarak yaz.
## BİTTİ SAYILIR
İki ilişkili tablo yüklendiğinde sistem doğru ilişkiyi öneriyor.
Yanlış öneri kullanıcı tarafından reddedilebiliyor ve bir daha önerilmiyor.

1.5UIP0Onay sonrası chat-içi mini görselleştirme + 'şunları analiz edebiliriz' önerisi
## AMAÇ
Kurulumun hemen ardından değeri göstermek: kullanıcı daha soru sormadan ilk grafiği görsün.
## NASIL
Yüklenen veriden 2-3 otomatik özet üret (toplam, zaman trendi, en yüksek kategori).
Bunları chat içinde küçük grafik kartları olarak göster.
Altına tıklanabilir öneriler koy: 'Aylık kırılımı göreyim mi?'
## BİTTİ SAYILIR
Kurulum biter bitmez ekranda en az 2 anlamlı grafik var.
Öneri çipine tıklanınca yeni grafik üretiliyor.
1.6LLMP0Intent Router v1 (metrik/grafik/rapor/sohbet/belirsiz) + netleştirme
## AMAÇ
Gelen her soruyu, LLM'e gitmeden önce türüne göre sınıflandırmak. Maliyet ve güvenin temeli.
## NASIL
Intent sınıfları: FETCH_METRIC, FETCH_REPORT, CHART, GENERAL, CHITCHAT, AMBIGUOUS.
Önce kural/örüntü tabanlı sınıflandırma dene (regex + eşanlamlı sözlüğü) — bedava ve hızlı.
Kural yakalamazsa küçük/ekonomik LLM ile sınıflandır (yalnız sınıf döner, SQL değil).
AMBIGUOUS ise kullanıcıya netleştirme sorusu sor ve DUR — LLM'e gitme.
Sınıflandırma sonucunu ve güven skorunu RouteDecision'a yaz.
## BİTTİ SAYILIR
Aynı soru her seferinde aynı sınıfa düşüyor (tutarlılık testi).
Belirsiz sorularda hiçbir veritabanı sorgusu ve pahalı LLM çağrısı yapılmıyor.
1.7WRENP0dry-plan → dry-run → query ön-doğrulama zinciri
## AMAÇ
Hatalı SQL'in müşteri veritabanında çalışmasını engellemek — üç kademeli ucuz kontrol zinciri.
## NASIL
Zincir: dry-plan (bağlantısız, ücretsiz) → dry-run (DB'de satırsız) → query (gerçek çalıştırma).
Her kademede hata olursa bir sonrakine geçme, hatayı yapılandırılmış olarak döndür.
Hata mesajını kullanıcıya değil, düzeltme mekanizmasına ver (1.9).
Zincirin her adımının süresi ölçülsün.
## BİTTİ SAYILIR
Sözdizimi hatalı bir SQL asla müşteri DB'sine ulaşmıyor.
Zincir toplamda 500 ms altında tamamlanıyor (basit sorgularda).
1.8UIP0DB bağlama sihirbazı (dinamik form + dry-run test + Vault)
## AMAÇ
Excel dışında gerçek veritabanına (Postgres/MySQL) bağlanabilmek.
## NASIL
Kaynak tipine göre dinamik form üret (host, port, db, user, pass, ssl).
'Test et' butonu dry-run ile bağlantıyı doğrular; hata mesajını sadeleştirip göster.
Başarılıysa şifreyi Vault'a yaz, referansı DB'ye kaydet.
Bağlantı sonrası tablo listesini çekip kullanıcıya hangi tabloları modelleyeceğini sor.
## BİTTİ SAYILIR
Yanlış şifre girildiğinde anlaşılır Türkçe hata mesajı çıkıyor.
Başarılı bağlantı sonrası tablo listesi 10 saniye içinde geliyor.

1.9LLMP0SQL üretim döngüsü v1 (bağlam→LLM→dry-plan→self-heal)
## AMAÇ
LLM'in yazdığı SQL hatalıysa kendi kendine düzeltmesini sağlamak (kullanıcı hatayı görmesin).
## NASIL
Bağlam hazırla: şema özeti + kullanıcı sorusu + varsa geçmiş benzer sorgular.
LLM'den SQL iste → dry-plan → hata varsa hata metnini LLM'e geri ver ve düzelttir.
En fazla 2 düzeltme denemesi; hâlâ hatalıysa dürüstçe 'bu soruyu çalıştıramadım' de.
Başarılı SQL'i altın sorgu adayı olarak işaretle (Faz 8 terfi motoru için).
## BİTTİ SAYILIR
Hatalı ilk denemelerin en az yarısı ikinci denemede düzeliyor.
İki denemeden sonra sistem uydurmuyor, açıkça başarısızlığı bildiriyor.
1.10WRENP0enrich-context skill (grill + auto-pilot) → anlamlandırma motoru + 'görünmez kolon' göz-
ikonu anahtarı
## AMAÇ
Veriye iş anlamı kazandırmak: sistemin 'status=4 ne demek' gibi soruları kullanıcıya sorup öğrenmesi.
## NASIL
Wren enrich-context skill'ini servise çevir; iki mod: grill (soru sorar) ve auto-pilot (öneri üretir).
Düşük kardinaliteli kolonlarda değerleri listeleyip anlamını sor ('4 = İptal mi?').
Her kolonun yanında göz ikonu: kapatılırsa MDL'e yazılmaz → yapay zekâ o kolonu asla göremez.
Cevaplar MDL açıklamalarına, knowledge/rules ve knowledge/sql dosyalarına yazılır.
## BİTTİ SAYILIR
Anlamlandırma sonrası aynı soruya verilen cevabın doğruluğu ölçülebilir şekilde artıyor.
Gizlenen kolon hiçbir sorgu sonucunda ve hiçbir LLM prompt'unda görünmüyor.
1.11DATAP0Cube + calculated field: OEE, RFT, karbon/kg, su/kg metrik tanımları (demo sektör seti) +
referans faktör/hedef yükleme
## AMAÇ
Demo sektörünün temel metriklerini (OEE, RFT, karbon/kg, su/kg) sisteme tanımlamak.
## NASIL
Her metrik için cube tanımı yaz: measure, dimension, time-dimension, filtre.
Hesaplanmış alanlar için calculated field kullan.
Emisyon faktörleri ve hedef değerleri referans tablosundan yükle (kod içine gömme).
Her metriğe insan-okur açıklama ve birim ekle.
## BİTTİ SAYILIR
'Dün OEE kaçtı?' sorusu LLM olmadan doğru cevap veriyor.
Metrik sonucu elle Excel'de hesaplananla birebir tutuyor (doğrulama testi).
1.11aDATAP0MetricDefinition semantik katmanı: görünen ad + eşanlamlı haritası (ciro/gelir/
satış→net_sales) + sahip/onaylayan departman + birim/yuvarlama + tanım metni + hedef değer
## AMAÇ
Metriğe iş kimliği kazandırmak: sistemin 'ciro' dendiğinde neyi kastettiğini bilmesi.
## NASIL
MetricDefinition tablosu: name, displayName, synonyms[], owner, unit, rounding, currency, targetValue, description,
cubeRef.
Eşanlamlı haritası: 'ciro|gelir|satış|hasılat' → net_sales.
Sahip alanı: hangi departman onayladı (tanım tartışmasında hakem).
Metrik listesi ekranı: arama, düzenleme, sürüm geçmişi.
## BİTTİ SAYILIR
'Gelirimiz ne kadar?' ile 'ciro nedir?' aynı metriğe gidiyor.
Her metriğin bir sahibi ve tanım metni var; boş bırakılamıyor.


1.11bDATAP0Türetme motoru (Sınıf B): çok-cube bileşen çekimi + deterministik formül DSL
(OEE=K×P×K, karbon=kWh×faktör, enerji/kg) — LLM yok, altın yolda kalır
## AMAÇ
Tek bir cube ile hesaplanamayan bileşik metrikleri (OEE gibi) LLM'siz üretmek.
## NASIL
Formül DSL'i tanımla: metrik = ifade (ör. oee = availability * performance * quality).
Her bileşen bir cube sorgusuna veya başka bir metriğe referans versin.
Değerlendirici (evaluator): bileşenleri paralel çek, formülü kodda uygula, birim ve yuvarlamayı metrik tanımından al.
Sıfıra bölme, eksik bileşen, null durumlarını açıkça yönet (hata yerine 'hesaplanamadı' + sebep).
Örnekler: karbon_kg = enerji_kwh * emisyon_faktoru; enerji_kg = toplam_kwh / uretim_kg.
## BİTTİ SAYILIR
OEE sonucu üç bileşeniyle birlikte gösterilebiliyor ve elle hesapla tutuyor.
Bir bileşen eksikse sistem yanlış sayı üretmiyor, eksiği söylüyor.
1.11cDATAP0Metrik tuzak önlemleri: join fan-out tekilleştirme, kanonik metrik + çakışma çözümü, mali
takvim ('geçen ay') ve kur kuralı metrik tanımında sabitlenir
## AMAÇ
Metrik hesaplamalarında en sık yapılan dört ölümcül hatayı baştan engellemek.
## NASIL
JOIN fan-out: bir siparişin çok satırı varsa toplam şişer → cube tanımında join yolu ve tekilleştirme (distinct/pre-
aggregate) sabitlensin.
Metrik çakışması: aynı isimde iki tanım varsa sistem çalıştırmaz, kullanıcıya sorar.
Mali takvim: 'geçen ay' takvim ayı mı mali ay mı — tenant ayarı olarak tanımlansın, sorgu anında karar verilmesin.
Kur: çok para birimli veride hangi kur (işlem günü / ay sonu / sabit) metrik tanımında belirtilsin.
## BİTTİ SAYILIR
Çoklu satırlı siparişlerde ciro şişmiyor (test verisiyle doğrulandı).
Mali yılı Ocak'ta başlamayan bir tenant'ta 'geçen ay' doğru aralığı veriyor.
1.11dLLMP0Parametre çözümleyici zinciri: kullanıcı tercihi → tenant varsayılanı → sistem varsayılanı
(tarih aralığı, para birimi, granülerlik)
## AMAÇ
Kullanıcı 'ciro' dediğinde hangi tarih aralığı, para birimi ve kırılımın kullanılacağını belirlemek.
## NASIL
Öncelik zinciri: soruda açıkça belirtilen > kullanıcı tercihi > tenant varsayılanı > sistem varsayılanı.
Çözümlenen parametreleri kullanıcıya göster ('son 30 gün, TRY') ki sessiz varsayım olmasın.
Kullanıcı değiştirirse tercih olarak kaydet (Faz 3 hafıza ile bağlanır).
## BİTTİ SAYILIR
Aynı soru iki farklı kullanıcıda kendi tercihlerine göre farklı ama doğru cevap veriyor.
Kullanılan varsayımlar her cevapta görünür.
1.11eDATAP1Cold start: şemadan cube/metrik adayı önerisi → wizard'da diff + onay (sıfır metrikle boş
sistem sorununu çözer)
## AMAÇ
Yeni müşterinin boş sistemle karşılaşmaması: kurulumda metrik önerisi.
## NASIL
Şemayı tara: sayısal kolon + tarih kolonu + tablo adı örüntüsünden metrik adayı çıkar.
Adayları önem sırasına koy (satır sayısı, kolon adı sinyali).
Kullanıcıya diff ekranında sun: 'Bu 8 metriği kurayım mı?' — tek tık onay veya düzenleme.
Onaylananlar MetricDefinition + cube olarak yazılır ve commit edilir.
## BİTTİ SAYILIR
Yeni bağlanan bir veritabanında 10 dakika içinde en az 5 çalışan metrik var.
Önerilen metrikler kullanıcı tarafından düzenlenebiliyor.

1.12WRENP1value profiling + structured errors (correctness primitifleri → self-heal kalitesi)
## AMAÇ
Sorgu hatalarını azaltmak için Wren'in doğruluk ilkelbileşenlerini kullanmak.
## NASIL
value profiling: kolonların örnek değerlerini, kardinaliteyi ve null oranını çıkarıp bağlama ekle.
structured errors: DB hatasını ham metin yerine {tip, kolon, öneri} yapısına çevir.
Bu yapılandırılmış hatayı 1.9'daki düzeltme döngüsüne besle.
## BİTTİ SAYILIR
LLM'e giden bağlamda kolonların gerçek örnek değerleri bulunuyor.
Hata mesajları makine-okunur ve düzeltme döngüsünde kullanılıyor.
1.13UIP1'Ne sorabilirim?' keşif haritası (departman bazlı tıklanabilir örnek sorular)
## AMAÇ
Boş ekran korkusunu yok etmek: kullanıcı ne soracağını bilmese de başlayabilsin.
## NASIL
Kurulan metrik ve tablolardan otomatik örnek soru üret (departman bazlı gruplayarak).
Ana ekranda kategorili kartlar olarak göster: Üretim, Satış, Finans, Stok.
Tıklanınca soru doğrudan çalışsın (yazmaya gerek yok).
## BİTTİ SAYILIR
Yeni kullanıcı hiçbir şey yazmadan ilk cevabını alabiliyor.
Öneriler müşterinin gerçek verisine göre değişiyor (jenerik değil).
wPROFILE
wERRORS

✅ KABUL TESTLERİ / USE-CASE'LER 21 senaryo · TEMEL: 11 · SINIR: 9 · GÜVENLİK: 1
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-1.1TEMEL10.000 satırlık bir Excel yüklenir60 saniyeden kısa sürede yüklenir; kaç satır/kolon ve tespit
edilen tipler özet olarak gösterilir.
UC-1.2SINIRBaşlık satırı ikinci satırda olan bir Excel
yüklenir
Sistem başlık satırını doğru tespit eder veya kullanıcıya sorar;
veriyi başlık sanmaz.
UC-1.3SINIRAynı ada sahip iki kolon içeren dosya
yüklenir
Kolon adları çakışmadan normalize edilir (tutar, tutar_2);
kullanıcı bilgilendirilir.
UC-1.4SINIRTarih kolonu metin olarak algılanırKullanıcı tipi düzeltir; düzeltme kaydedilir ve sonraki
yüklemelerde hatırlanır.
UC-1.5TEMELExcel yüklendikten sonra hiçbir şey
yazılmaz
Sistem MDL'i otomatik üretir; dry-plan başarılı çalışır.
UC-1.6TEMELİki ilişkili tablo (siparişler + müşteriler)
yüklenir
Sistem ortak anahtarı bulup ilişkiyi önerir; kullanıcı tek tıkla
onaylar.
UC-1.7SINIRYanlış bir ilişki önerisi reddedilirÖneri bir daha gösterilmez; MDL'e yazılmaz.
UC-1.8TEMELTeknik olmayan bir kullanıcı kurulum
sihirbazını başlatır
Yardım almadan kurulumu tamamlar; her adımda ne yapması
gerektiğini anlar.
UC-1.9SINIRSihirbazda kullanıcı 'bilmiyorum' derSistem varsayım yapmaz; alanı 'belirsiz' işaretler ve sonra
tekrar sorar.
UC-1.10TEMELKurulum tamamlanırKullanıcı soru sormadan ekranda en az 2 anlamlı grafik ve
tıklanabilir öneriler görür.
UC-1.11TEMEL'Dün OEE kaçtı?' sorulurLLM çağrısı yapılmadan (log ile doğrulanır) doğru sonuç döner;
sonuç elle hesaplananla birebir tutar.
UC-1.12TEMEL'Gelirimiz ne kadar?' ve 'ciro nedir?' ayrı
ayrı sorulur
İkisi de aynı metriğe (net_sales) gider ve aynı sonucu verir.
UC-1.13SINIRBelirsiz bir soru sorulur ('satış nedir?')Sistem LLM'e gitmeden netleştirme sorusu sorar (net mi brüt
mü) ve durur; hiçbir sorgu çalışmaz.
UC-1.14TEMELÇok satırlı siparişler içeren veride ciro
sorulur
JOIN fan-out nedeniyle tutar şişmez; sonuç doğru çıkar.
DİMA · 0→100 Görev Takip Dosyası20 / 126

GenBI Çekirdeği: Grafik + Yorum + Öneri
[demo D1 tamamlanır] Senin '0 noktası' akışının tamamı: grafik → yorum → tıklanabilir öneri → derinleş. Demo-seviyesi güven
primitifleri de burada.
2.1VIZP0Grafik motoru (Vega-Lite): bar / çizgi / çoklu-çizgi / pasta / alan / grup-bar
## AMAÇ
Sonuçları tabloda değil grafikte göstermek. Grafik motoru tüm görsel çıktıların temeli.
## NASIL
Vega-Lite'ı frontend'e kur; backend sadece 'chart spec' (JSON) üretsin, çizimi tarayıcı yapsın.
Başlangıç seti: bar, çizgi, çoklu-çizgi, pasta, alan, gruplu bar.
Her grafik tipi için veri şekli sözleşmesi tanımla (x, y, seri kolonu).
Renk paleti ve Türkçe sayı/tarih biçimlendirmesini merkezî tut (1.234,56 ve 12 Oca 2026).
## BİTTİ SAYILIR
Aynı veri farklı grafik tiplerinde bozulmadan çiziliyor.
Sayı ve tarih formatları Türkçe standardında.
2.2LLMP0Grafik türü karar verici v1 (veriye göre uygun grafik)
## AMAÇ
Kullanıcı grafik tipi seçmek zorunda kalmasın; sistem veriye bakıp doğru tipi seçsin.
## NASIL
Kural tabanlı seçici yaz (LLM değil): zaman kolonu varsa çizgi; kategori ≤8 ise bar; oran/yüzde ve ≤5 kategori ise
pasta; iki sayısal kolon ise dağılım.
Kategori sayısı çoksa ilk N + 'diğer' grupla.
Seçimin gerekçesini sakla ('zaman serisi olduğu için çizgi') ve kullanıcıya göster.
Kullanıcı tipi değiştirirse tercihini kaydet.
## BİTTİ SAYILIR
10 farklı sorgu sonucunda seçilen grafik tipi insan yargısıyla uyumlu.
Kullanıcı tek tıkla tipi değiştirebiliyor.
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-1.15SINIRMali yılı Ocak'ta başlamayan bir
tenant'ta 'geçen ay' sorulur
Sistem tenant'ın mali takvimine göre doğru aralığı kullanır.
UC-1.16TEMELOEE bileşenleriyle birlikte istenirKullanılabilirlik, performans ve kalite ayrı ayrı gösterilir;
çarpımları toplam OEE'yi verir.
UC-1.17SINIROEE bileşenlerinden biri (ör. ideal
çevrim süresi) eksiktir
Sistem yanlış sayı üretmez; hangi verinin eksik olduğunu
söyler.
UC-1.18GÜVENLİKAnlamlandırma sırasında e-posta kolonu
'gizle' işaretlenir
Kolon MDL'e yazılmaz; hiçbir sorgu sonucunda ve hiçbir LLM
prompt'unda görünmez.
UC-1.19TEMELYeni bir veritabanı bağlanır10 dakika içinde en az 5 çalışan metrik önerilir ve
onaylanabilir.
UC-1.20SINIRDB bağlantısında yanlış şifre girilirAnlaşılır Türkçe hata mesajı gösterilir; teknik yığın izi (stack
trace) sızdırılmaz.
UC-1.21TEMELKullanıcı ilk kez giriş yapar, ne
soracağını bilmez
Departman bazlı örnek soru kartları görür; tıklayarak ilk
cevabını alır.
## FAZ 2

2.3UIP0İnteraktif grafik: yakınlaştırma / alan seçme / kaydırma / hover-detay
## AMAÇ
Grafiği canlı bir inceleme aracına dönüştürmek (statik resim değil).
## NASIL
Yakınlaştırma, kaydırma, alan seçerek büyütme (brush zoom).
Hover'da detay kutusu: tam değer, tarih, kategori.
Seride tıklama → o dilime drill-down isteği tetikle.
Mobil dokunma desteği.
## BİTTİ SAYILIR
Kullanıcı grafikte bir aralığı seçip yakınlaştırabiliyor.
Hover'da gerçek değer görünüyor (yuvarlanmış değil, tam).
2.4UIP0Grafik dışa aktarım: PNG / SVG / CSV
## AMAÇ
Kullanıcının grafiği sunuma/e-postaya taşıyabilmesi.
## NASIL
Her grafik kartına dışa aktar menüsü: PNG, SVG, altındaki veriyi CSV.
PNG'yi tarayıcıda canvas üzerinden üret (sunucuya iş yükleme).
Dosya adına metrik + tarih aralığı yaz (ciro_2026-01_2026-06.png).
CSV'de Türkçe karakter için UTF-8 BOM ekle (Excel doğru açsın).
## BİTTİ SAYILIR
İndirilen CSV Excel'de Türkçe karakterler bozulmadan açılıyor.
PNG sunum kalitesinde (min 2x çözünürlük).
2.5LLMP0Zorunlu yorum = İçgörü Kartı (ne oluyor / neden / ne yapmalı); salt sayı-tekrarı YASAK
## AMAÇ
Her grafiğin altında GERÇEK analiz yazmak. Bu ürünün kalite çizgisidir: sayıyı cümleye çevirmek yasak.
## NASIL
Zorunlu üç şerit yapısı: (1) NE OLUYOR: trend/yön/büyüklük, (2) NEDEN: kırılım, anomali, en çok katkı yapan kalem,
(3) NE YAPMALI: somut öneri veya izlenecek metrik.
İstatistikleri kod hesaplasın (trend eğimi, değişim %, z-skoru, en büyük katkı) — LLM sadece bunları cümleye çevirsin.
Yasak kalıp listesi: 'X arttı', 'Y azaldı' tek başına yeterli değil; sebep veya aksiyon içermeyen yorum reddedilir
(otomatik kontrol).
Veri yetersizse (az nokta, yüksek varyans) yorum yerine 'yorum için veri yetersiz' yaz.
LLM'e ham satır gitmez; sadece hesaplanmış istatistikler ve etiketler gider (Plane Enforcer 2.12).
## BİTTİ SAYILIR
Rastgele 20 yorum incelendiğinde hiçbiri salt sayı tekrarı değil.
Her yorumda en az bir sebep veya aksiyon önerisi var.
Veri yetersizken sistem uydurma yorum yapmıyor.
2.6UIP0Tıklanabilir öneri çipleri → aynı ekranda alta yeni grafik
## AMAÇ
Kullanıcıyı 'sonra ne sorayım' düşünmekten kurtarmak; analizi zincir haline getirmek.
## NASIL
Her cevaptan sonra 3-5 öneri çipi üret ve grafik altında göster.
Çipe tıklanınca yeni soru YAZILMADAN çalışsın ve sonucu MEVCUT ekranın altına eklensin (sayfa değişmez).
Öneri tipleri: kırılım (şubeye göre), karşılaştırma (geçen yıl), derinleşme (en düşük şubeye in), ilişkilendirme (stokla
birlikte).
Kullanılan öneriyi işaretle, tekrar önerme.
## BİTTİ SAYILIR
Kullanıcı sadece tıklayarak 5 adımlık bir analiz zinciri yapabiliyor.
Yeni grafikler üstteki grafikleri silmiyor, alta ekleniyor.
## Ç5

DİMA · 0→100 Görev Takip Dosyası22 / 126

2.7LLMP0Öneri üreteci (derinleştirme / karşılaştırma önerileri)
## AMAÇ
Öneri çiplerinin içeriğini akıllı üretmek (rastgele değil, bağlama uygun).
## NASIL
Mevcut sorgunun cube parametrelerine bak: hangi boyutlar kullanılmamış?
Kullanılmayan boyutlardan kırılım önerisi üret; zaman boyutu varsa dönem karşılaştırması ekle.
Anomali tespit edildiyse 'bu sapmanın nedenini araştır' önerisi öne çıksın.
Şirket hafızasındaki (Faz 5) öncelikli metriklerle ilişkilendir.
## BİTTİ SAYILIR
Öneriler her sorguda farklı ve konuyla ilgili.
Aynı öneri arka arkaya tekrar edilmiyor.
2.8UIP0Her grafikte sabit 'Dashboard'a aktar' butonu (hep görünür)
## AMAÇ
Kullanıcının beğendiği grafiği kalıcı hale getirmesini tek tıkla mümkün kılmak.
## NASIL
Her grafik kartının sağ üstünde SABİT 'Panoya ekle' butonu (hover'da beliren değil, hep görünür).
Tıklanınca hangi panoya ekleneceğini sor (yoksa yeni pano oluştur).
Grafiğin veri sorgusu (cube parametreleri) saklansın, ekran görüntüsü değil — pano canlı veriyle yenilensin.
## BİTTİ SAYILIR
Butona basmak 2 tıktan fazla sürmüyor.
Panoya eklenen grafik ertesi gün güncel veriyle açılıyor.
2.9UIP0Chat-içi düşünme adımları paneli (Think→Act→Observe)
## AMAÇ
Sistemin ne yaptığını gizlememek; güven şeffaflıktan doğar.
## NASIL
Cevap üretilirken adımları canlı stream et: 'Metrik çözümleniyor → sorgu hazırlanıyor → çalıştırılıyor → yorumlanıyor'.
Açılır panelde teknik detay: çalışan SQL, süre, kullanılan yol (altın/LLM).
Varsayılan kapalı, isteyen açar (kalabalık yapmasın).
Agentic modda her adım ayrı satır olarak birikir.
## BİTTİ SAYILIR
Kullanıcı isterse hangi SQL'in çalıştığını görebiliyor.
Bekleme sırasında ekran boş kalmıyor, ilerleme görünüyor.
2.10UIP0Canlı büyüyen Analiz Tuvali (sağda kart biriktiren, sürükle-bırak dizilebilen)
## AMAÇ
Analizi sohbet akışında kaybolmaktan kurtarmak; biriken kartlardan rapor oluşturabilmek.
## NASIL
Sağ tarafta kaydırılabilir tuval: her üretilen grafik/yorum bir kart olarak eklenir.
Kartlar sürükle-bırak ile sıralanabilir, silinebilir, başlık verilebilir.
Tuvalin üstünde sabit iki buton: 'Rapor oluştur' ve 'Panoya aktar'.
Tuval oturum boyunca kalıcı; sayfa yenilense de durur (Faz 3 kalıcılığıyla).
## BİTTİ SAYILIR
10 kartlık bir analiz tuvali performans kaybı olmadan çalışıyor.
Kart sırası değiştirilebiliyor ve rapor bu sıraya göre üretiliyor.
## Ç7

DİMA · 0→100 Görev Takip Dosyası23 / 126

2.11ENGP0Router+Policy Kernel v1: deterministik (cube/altın) ↔ LLM yönlendirme + model sınıfı seçimi
## AMAÇ
Router'ın gerçek karar mekanizmasını devreye almak: hangi soru LLM'e gider, hangisi gitmez.
## NASIL
Intent + metrik çözümleme sonucuna göre yol seç: metrik/rapor bulunduysa CUBE yolu (LLM YOK).
Bulunamadıysa cache'e bak; yoksa LLM yolu.
Model sınıfı seçimi: basit yorum → ekonomik; çok adımlı analiz → denge; kritik karar → premium.
Seçilen yolu, gerekçesini ve tahmini maliyeti RouteDecision'a yaz ve logla.
Ölçüm: her gün kaç isteğin LLM'siz gittiğini raporla (altın yol oranı).
## BİTTİ SAYILIR
Metrik sorularının %100'ü LLM'e gitmiyor.
Günlük altın yol oranı panelde görülebiliyor.
2.12GOVP0Plane Enforcer: her LLM çağrısı öncesi ham değer/PII sıyırma (iki-düzlem garantisi)
## AMAÇ
Ham verinin LLM'e sızmasını mimari olarak imkânsız kılmak — egemenlik iddiasının teknik temeli.
## NASIL
İki düzlem tanımla: KONTROL (LLM görebilir: soru metni, tablo/kolon ADLARI, plan, satır sayısı, hesaplanmış istatistik)
ve VERİ (LLM asla göremez: gerçek hücre değerleri, isimler, tutarlar).
Tüm LLM çağrılarını tek bir sarmalayıcıdan geçir; sarmalayıcı payload'ı tarar.
Tarama: veri düzleminden gelen alanlar prompt'a eklenmişse çağrıyı ENGELLE ve hata logla (sessiz geçme).
Yorum üretiminde LLM'e sayı değil şablon yazdır ('Ciro {deger} TL'), boşluğu kod doldursun.
İstisna gerekirse (ör. serbest metin özeti) yalnız yerel/on-prem modelle ve açık kullanıcı onayıyla.
## BİTTİ SAYILIR
Test: içinde müşteri adı geçen bir sonuç LLM'e gönderilmeye çalışıldığında sistem engelliyor.
Prompt logları incelendiğinde hiçbirinde gerçek veri değeri yok.
2.13UIP1'Hızlı cevap ↔ Derin analiz' toggle (soru-bazlı mod)
## AMAÇ
Kullanıcıya hız/derinlik seçimi vermek ve maliyeti şeffaflaştırmak.
## NASIL
Soru kutusunun yanında iki konumlu anahtar: Hızlı cevap / Derin analiz.
Hızlı: yalnız altın yol + cache, LLM yok, anında sonuç.
Derin: agentic analiz, düşünme adımları görünür, daha uzun sürer.
Seçim soru bazlı (thread'e kilitlenmez); varsayılan Hızlı.
## BİTTİ SAYILIR
Hızlı modda hiçbir LLM çağrısı yapılmıyor (logla doğrulanıyor).
Kullanıcı modu değiştirdiğinde farkı hissediyor (süre ve derinlik).
2.14WRENP1GenBI Apps yaklaşımı: agent-üretimli görünüm temeli (Preview/Code sekmeleri)
## AMAÇ
Ajanın tek promptla görsel çıktı üretebilmesinin temelini atmak.
## NASIL
Wren genbi yaklaşımını incele: ajan bir 'uygulama tanımı' üretir, tarayıcı render eder.
Preview / Code sekmeli görünüm: kullanıcı üretilen tanımı görebilsin.
Bu fazda tek grafik seviyesinde kal; çok bileşenli artifact Faz 4'te.
## BİTTİ SAYILIR
Ajanın ürettiği grafik tanımı hatasız render ediliyor.
Kod sekmesinde tanım okunabiliyor.
## BE1Ç4

DİMA · 0→100 Görev Takip Dosyası24 / 126

2.15GOVP0Kanıt-her-yerde v1: sayı/çubuk/yorum tıklanınca kaynak paneli (SQL+formül+tablo) — tam
## Contract 7.1
## AMAÇ
Her sayının kaynağını göstermek — 'uydurmuyor' iddiasının görünür kanıtı.
## NASIL
Her sonuç nesnesine kaynak bilgisi ekle: metrik adı, formül, kullanılan tablolar, filtreler, çalışan SQL, süre, MDL
sürümü.
Arayüzde sayıya/çubuğa tıklanınca yandan kanıt paneli açılsın.
Panelde 'SQL'i göster' ve 'yeniden çalıştır' butonları.
Bu fazda hafif sürüm; imzalı sözleşme (contract) Faz 7.1'de.
## BİTTİ SAYILIR
Ekrandaki her sayı için kaynak paneli açılabiliyor.
Panelde gösterilen SQL kopyalanıp DB'de çalıştırıldığında aynı sonucu veriyor.
2.16GOVP0Dürüst red v1: veri yok / kapsam dışı → uydurma, açıkla — tam Eligibility 7.3
## AMAÇ
Bilmediğini söyleyebilen sistem: uydurmanın önündeki son bariyer.
## NASIL
Cevap üretmeden önce kontrol listesi: veri var mı, metrik tanımlı mı, yetki var mı, soru net mi.
Herhangi biri başarısızsa cevap üretme; sebebi ve çözüm önerisini göster ('Bu veri sistemde yok. Şu tabloyu
bağlarsanız cevaplayabilirim').
Reddi logla (sonradan hangi verilerin eksik olduğunu analiz etmek için).
Asla 'tahmini' sayı üretme.
## BİTTİ SAYILIR
Veride olmayan bir soru sorulduğunda sistem uydurmuyor, açıkça reddediyor.
Red mesajı kullanıcıya ne yapması gerektiğini söylüyor.
2.17GOVP0Confidence badge v1 (altın/gümüş/bronz) — tam hesaplayıcı 7.2
## AMAÇ
Her cevabın ne kadar güvenilir olduğunu sistemin kendisinin hesaplaması (LLM'in kendine puan vermesi değil).
## NASIL
Kural tabanlı skor: altın yol (cube) = 100; cache = 95; LLM+doğrulanmış SQL = 70; LLM+düzeltilmiş = 55.
Düşürücü etkenler: eksik veri, geniş tarih aralığı, tanımsız metrik, yüksek varyans.
Skoru rozete çevir: 磊 90+, 賂 70-89, 雷 <70.
Rozeti her cevabın yanında göster, tıklanınca gerekçe listesi açılsın.
## BİTTİ SAYILIR
Aynı tip sorgu her zaman aynı rozeti alıyor.
Rozet gerekçesi kullanıcıya açıklanabiliyor.
2.18UIP0Meta-güven şeridi (router yol dağılımı: %X LLM'siz gitti)
## AMAÇ
Ürünün maliyet ve güven farkını kullanıcıya görünür kılmak.
## NASIL
Oturum sonunda veya panelde: 'Bugün sorularınızın %71'i yapay zekâ kullanılmadan cevaplandı.'
Yol dağılımını RouteDecision loglarından hesapla.
Aylık özet olarak da e-posta ile gönderilebilsin (Faz 8 raporuyla birleşir).
## BİTTİ SAYILIR
Yol dağılımı gerçek loglardan hesaplanıyor (sabit değer değil).
Kullanıcı bu paneli açıp anlayabiliyor.

DİMA · 0→100 Görev Takip Dosyası25 / 126

2.19GOVP0PII maskeleme v1 (TCKN/e-posta, rol-duyarlı) — tam Redactor 7.7
## AMAÇ
Kişisel verilerin ekranda ve çıktılarda görünmesini engellemek.
## NASIL
Çıkış filtresi: TCKN, e-posta, telefon, IBAN, kart numarası desenlerini tara ve maskele (12345678901 → ***TCKN***).
Rol bazlı istisna: yetkili roller maskesiz görebilir, bu erişim loglanır.
Maskeleme cevap kullanıcıya gitmeden ÖNCE, en son adımda uygulanır (hiçbir yol atlanamaz).
Dışa aktarımlarda (CSV/PNG) de aynı filtre çalışır.
## BİTTİ SAYILIR
Maskeli veri içeren bir sorgunun CSV çıktısında da maskeleme var.
Yetkili rol maskesiz görüyor ve bu erişim audit'e düşüyor.

✅ KABUL TESTLERİ / USE-CASE'LER 23 senaryo · TEMEL: 13 · SINIR: 3 · REGRESYON: 4 · GÜVENLİK: 3
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-2.1TEMELZaman serisi içeren bir sorgu yapılırSistem otomatik çizgi grafik seçer ve gerekçesini gösterir.
UC-2.2SINIR20 kategorili bir kırılım istenirİlk N kategori + 'diğer' olarak gruplanır; grafik okunabilir
kalır.
UC-2.3TEMELGrafikte bir aralık seçilerek yakınlaştırılırGrafik seçilen aralığa odaklanır; hover'da tam
(yuvarlanmamış) değer görünür.
UC-2.4TEMELGrafik CSV olarak indirilirExcel'de açıldığında Türkçe karakterler bozulmaz (UTF-8
## BOM).
UC-2.5TEMELHerhangi bir grafik üretilirAltında üç şeritli yorum çıkar: ne oluyor (trend), neden
(kırılım/anomali), ne yapmalı (öneri).
UC-2.6REGRESYON20 rastgele yorum incelenirHiçbiri salt sayı tekrarı değil; her birinde sebep veya
aksiyon var.
UC-2.7SINIR3 veri noktalı bir seride yorum istenirSistem trend uydurmaz; 'yorum için veri yetersiz' der.
UC-2.8TEMELCevap altındaki öneri çipine tıklanırYeni grafik MEVCUT ekranın altına eklenir; üstteki grafikler
silinmez.
UC-2.9REGRESYONArka arkaya 5 öneri kullanılırAynı öneri tekrar gösterilmez; her öneri konuyla ilgilidir.
UC-2.10TEMELBir grafikte 'Panoya ekle' butonuna basılırButon her zaman görünürdür (hover gerektirmez); grafik
panoya sabitlenir.
UC-2.11TEMELPanoya eklenen grafik ertesi gün açılırEkran görüntüsü değil, güncel veriyle yeniden hesaplanmış
sonuç gösterilir.
UC-2.12TEMELKarmaşık bir soru sorulurDüşünme adımları canlı akar; istenirse çalışan SQL
görülebilir.
UC-2.13TEMEL5 farklı analiz üretilirHepsi analiz tuvalinde kart olarak birikir; sürükle-bırak ile
sıralanabilir.
UC-2.14REGRESYONTanımlı bir metrik sorulurSorgu LLM'e gitmez (log kanıtı); günlük altın yol oranı
panelde artar.
UC-2.15GÜVENLİKİçinde müşteri adı geçen bir sonuç LLM'e
gönderilmeye çalışılır
Plane Enforcer çağrıyı engeller ve loglar; prompt'a ham
veri girmez.
UC-2.16GÜVENLİKTüm LLM prompt logları taranırHiçbirinde gerçek hücre değeri (isim, tutar) bulunmaz.
UC-2.17TEMEL'Hızlı cevap' modunda soru sorulurHiçbir LLM çağrısı yapılmaz; sonuç anında gelir.
UC-2.18TEMELEkrandaki bir sayıya tıklanırKanıt paneli açılır: formül, kaynak tablolar, çalışan SQL,
süre.
UC-2.19REGRESYONKanıt panelindeki SQL kopyalanıp DB'de
çalıştırılır
Ekrandaki sonucun aynısı çıkar.
UC-2.20SINIRVeride olmayan bir şey sorulur ('rakip
fiyatları')
Sistem uydurmaz; 'bu veri sistemde yok' der ve ne
yapılabileceğini söyler.

## Rapor + Dashboard + Bağlamsal Hafıza
[demo D2 tamamlanır] Biriken grafikleri rapora/panoya çevir; sohbet bağlamsallaşsın, hatırlasın, kendini tekrarı fark etsin.
3.1UIP0Rapordan-üretim: format seçimi (Excel/tablo/grafik/karşılaştırmalı) → üret; tek grafikten bile
## AMAÇ
Biriken analizleri paylaşılabilir bir belgeye dönüştürmek.
## NASIL
'Rapor oluştur' butonu tuvaldeki kartları alır, kullanıcıya format sorar: Word/PDF, Excel (veri tablolu), veya ekranda
görünen zengin sayfa.
Rapor bölümleri: kapak (başlık, tarih, hazırlayan), yönetici özeti (otomatik), her kart için grafik + yorum, kaynak
listesi.
Tek grafik varsa da rapor üretilebilsin (buton her zaman aktif).
Her sayının yanına kaynak referansı (Faz 2.15 kanıt bağlantısı) eklensin.
## BİTTİ SAYILIR
10 kartlık tuval 30 saniyede rapora dönüşüyor.
Üretilen dosya kurumsal sunumda kullanılabilecek kalitede.
3.2WRENP0Dashboard motoru (wren-core-wasm, ürün-içi kalıcı + izinli render)
## AMAÇ
Grafiklerin kalıcı olarak yaşadığı, canlı veriyle yenilenen pano sistemi.
## NASIL
Pano modeli: pano → widget'lar; her widget bir sorgu tanımı (cube parametreleri) + görsel ayar tutar.
Pano açıldığında widget'lar paralel çalışır; yavaş olanlar iskelet (skeleton) gösterir.
Wren wasm ile tarayıcı tarafı hesaplama seçeneğini değerlendir (hızlı yenileme için).
Panolar tenant + izinlere bağlıdır; herkes her panoyu göremez.
## BİTTİ SAYILIR
Bir pano 3 saniyede yükleniyor (10 widget'a kadar).
Panodaki veriler her açılışta güncel.
3.3UIP0Sabitlerken 'hangi sıklıkta güncelleyeyim?' + 'düşerse/aşarsa haber ver' (alarm-widget)
## AMAÇ
Panoyu pasif ekran olmaktan çıkarıp nöbetçiye dönüştürmek.
## NASIL
Panoya ekleme sırasında sor: 'Ne sıklıkla güncellensin?' (canlı / saatlik / günlük / haftalık).
İkinci soru: 'Bir eşiği aşarsa haber vereyim mi?' → eşik değeri ve yön (üstüne çıkarsa/altına inerse).
Eşik kaydı Pulse motoruna (Faz 8.10) iş olarak yazılır.
Bildirim kanalı seçimi: uygulama içi, e-posta, WhatsApp.
## BİTTİ SAYILIR
Eşik tanımlanan bir widget, eşik aşıldığında bildirim üretiyor.
Güncelleme sıklığı gerçekten uygulanıyor (gereksiz sorgu çalışmıyor).
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-2.21TEMELAynı tip sorgu iki kez yapılırHer ikisinde de aynı güven rozeti verilir; rozetin gerekçesi
açıklanabilir.
UC-2.22GÜVENLİKTCKN içeren bir liste sorgulanırEkranda, CSV'de ve PNG'de TCKN maskeli görünür; yetkili
rolde maskesiz ve erişim loglanır.
UC-2.23TEMELMeta-güven paneli açılırGünün yol dağılımı gerçek loglardan hesaplanmış olarak
görünür (sabit değer değil).


## FAZ 3


3.4UIP0Pano: sürükle-bırak / boyut / global filtre / drill-down / roll-up
## AMAÇ
Panoyu kullanıcının kendi düzenleyebilmesi ve derinleşebilmesi.
## NASIL
Sürükle-bırak yerleşim, yeniden boyutlandırma, kaydetme.
Pano üstünde global filtre çubuğu (tarih aralığı, şube, ürün) — tüm widget'lara uygulanır.
Widget'ta bir dilime tıklayınca alt kırılıma inme (drill-down) ve geri dönme (roll-up).
Filtre durumu paylaşılabilir bağlantıya gömülsün.
## BİTTİ SAYILIR
Global tarih filtresi tüm widget'ları aynı anda güncelliyor.
Drill-down sonrası geri dönülebiliyor.
3.5LLMP0Bağlamsal sohbet + thread hafızası + follow-up ('aynı grafiğe X ekle')
## AMAÇ
Sohbetin hafızalı olması: 'aynı grafiğe şunu da ekle' gibi takiplerin çalışması.
## NASIL
Thread modeli: mesajlar, üretilen sorgular, kullanılan parametreler kalıcı saklanır.
Her yeni soruda son N mesajın çözümlenmiş bağlamı (metrik, tarih aralığı, filtre) taşınır.
Zamir/atıf çözümleme: 'onu', 'aynı grafiğe', 'geçen aya göre' ifadeleri önceki sorgu parametrelerine bağlanır.
Bağlam çakışırsa kullanıcıya sor, varsayma.
## BİTTİ SAYILIR
'Bu ay ciro' → 'peki geçen yıl?' zinciri doğru çalışıyor.
Sayfa yenilendiğinde sohbet ve bağlam kayboluyorsa hata sayılır.
3.6DATAP0Tekrar-üretim algısı + 'önceki hâli hayaleti' kıyas gösterimi
## AMAÇ
Aynı sorunun cevabı değiştiğinde kullanıcının bunu fark etmesini sağlamak.
## NASIL
Her sonuç için imza üret: sorgu parametreleri hash'i + sonuç hash'i + zaman.
Aynı sorgu imzası tekrar geldiğinde önceki sonucu bul.
Fark varsa göster: 'Geçen sefer 1,2M TL idi; şimdi 1,45M TL (+%20)'.
Grafikte önceki değerleri soluk 'hayalet' seri olarak çiz.
Farkın sebebi veri güncellemesi mi tanım değişikliği mi ayırt et (MDL commit karşılaştırması).
## BİTTİ SAYILIR
Aynı soru iki gün arayla sorulduğunda değişim otomatik gösteriliyor.
Tanım değiştiği için oluşan farklar 'tanım değişti' olarak işaretleniyor.
3.7LLMP0Kişisel Memories (tercih sessizce uygulanır: tarih aralığı, para birimi, format)
## AMAÇ
Kullanıcının tercihlerini öğrenip sessizce uygulamak.
## NASIL
Tercih tipleri: varsayılan tarih aralığı, para birimi, sayı formatı, favori metrikler, rapor formatı.
Açık öğretme: 'bundan sonra hep son 30 gün al' → tercih olarak kaydet.
Örtük öğrenme: kullanıcı 5 kez aynı filtreyi seçtiyse öner ('bunu varsayılan yapayım mı?').
Tercihler kullanıcı bazlı; şirket tanımlarını ezemez (bkz. 5.7 öncelik kuralı).
## BİTTİ SAYILIR
Kullanıcı tercihini bir kez söyledikten sonra tekrar söylemek zorunda kalmıyor.
Tercihler ayarlar ekranında görülebiliyor ve silinebiliyor.
## F14Ç9
## 1.
## 2.
## 3.
## 4.
## •
## •
## D11F16
## 1.
## 2.
## 3.
## 4.
## •
## •
## F6UX8
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## D30F16
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası28 / 126

3.8WRENP0memory store/recall/fetch + kaynak-gerçeği kararı (pgvector↔LanceDB) + senkron
## AMAÇ
Hafıza altyapısını kurmak ve en kritik mimari kararı vermek: tek doğruluk kaynağı nerede?
## NASIL
KARAR: knowledge/ dosyaları (Git) kaynak gerçeği olsun; vektör indeksi türetilmiş kopya olsun (silinse yeniden
kurulabilir).
Vektör deposu seçimi: pgvector (mevcut Postgres, ek altyapı yok) — LanceDB yerine bunu öner.
İndeksleme işi: dosya değişince otomatik yeniden indeksle (watch).
Getirme stratejisi: küçük şemada tam metin, büyükte embedding araması (hibrit).
ASLA iki yerde bağımsız yazma yapma — çift hafıza drifti en büyük teknik borçtur.
## BİTTİ SAYILIR
Vektör indeksi silinip yeniden kurulduğunda hiçbir bilgi kaybı olmuyor.
Aynı bilgi iki farklı yerde farklı değerde bulunmuyor.
3.9UIP0Zamanlanmış rapor/abonelik (e-posta + WhatsApp)
## AMAÇ
Kullanıcı sistemi açmasa bile değerin ona gitmesi.
## NASIL
Zamanlama tanımı: rapor + alıcı + sıklık + saat + kanal.
Cron/scheduler işleri Redis üzerinde; çakışma ve tekrar koruması (idempotency).
Kanallar: e-posta (PDF ek), WhatsApp Business API (kısa özet + bağlantı).
Gönderim başarısızsa tekrar dene ve kullanıcıya bildir.
Maliyet için toplu/batch LLM kullan (gerçek zamanlı değil).
## BİTTİ SAYILIR
Pazartesi 08:00 planlanan rapor gerçekten o saatte ulaşıyor.
Aynı rapor iki kez gönderilmiyor.
3.10LLMP1Hedef/plan kıyası motoru (hedef verisi vs gerçekleşen)
## AMAÇ
Performansı yorumlayabilmek için 'hedef' kavramını sisteme sokmak.
## NASIL
Hedef modeli: metrik + dönem + kapsam (şirket/şube/kişi) + hedef değer.
Hedefler Excel'den toplu yüklenebilsin.
Sorgu sonucunda hedef varsa otomatik karşılaştır: gerçekleşen / hedef, sapma, kalan süre.
Grafiklerde hedef çizgisi göster.
## BİTTİ SAYILIR
Hedefi olan bir metrik sorulduğunda cevapta sapma otomatik geliyor.
Hedef yoksa sistem uydurmuyor, 'hedef tanımlı değil' diyor.
3.11UIP1Capability Explorer (yetenek haritası, mdl+cube'dan otomatik üretilir)
## AMAÇ
Kullanıcının 'bu sistem ne yapabilir' sorusuna somut cevap vermek.
## NASIL
Tanımlı metrikleri, raporları, veri kaynaklarını ve örnek soruları tek ekranda listele.
Bu listeyi elle değil, MDL + MetricDefinition'dan otomatik üret (bakım derdi olmasın).
Arama ve departman filtresi ekle.
Her maddeye 'bunu sor' butonu koy.
## BİTTİ SAYILIR
Yeni metrik eklendiğinde listede otomatik beliriyor.
Kullanıcı aradığı metriği 10 saniyede bulabiliyor.
## BE6
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## Y1BE9
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## Y9
## 1.
## 2.
## 3.
## 4.
## •
## •
## F24
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası29 / 126

3.12UIP1Knowledge Center (Instructions Global/soru-eşleşmeli + Soru-SQL çiftleri CRUD + 'Bilgiye
kaydet')
## AMAÇ
Sistemin iş kurallarını ve doğrulanmış sorguları yönetebileceği merkez.
## NASIL
İki sekme: Kurallar (Instructions) ve Doğrulanmış Sorular (soru-SQL çiftleri).
Kural tipleri: her sorguda geçerli (global) ve belirli kelime geçince geçerli (eşleşmeli).
Cevap ekranında 'Bilgiye kaydet' butonu → doğru cevabı altın sorgu olarak kaydeder.
Kurallar knowledge/rules dosyasına, çiftler knowledge/sql dosyasına yazılır ve commit edilir.
Her kaydın sahibi, tarihi ve kullanım sayacı tutulur.
## BİTTİ SAYILIR
Eklenen bir kural sonraki sorgularda gerçekten uygulanıyor.
Kaydedilen altın sorgu benzer soruda geri çağrılıyor.
## F15
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
✅ KABUL TESTLERİ / USE-CASE'LER 21 senaryo · TEMEL: 14 · SINIR: 4 · REGRESYON: 2 · GÜVENLİK: 1
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-3.1TEMELTuvalde 10 kart varken 'Rapor oluştur' denir30 saniye içinde kapak, yönetici özeti, grafikler ve
kaynak listesi içeren rapor üretilir.
UC-3.2SINIRTuvalde tek grafik varken rapor istenirButon aktiftir ve tek grafikli rapor üretilir.
UC-3.3TEMEL10 widget'lı bir pano açılır3 saniye içinde yüklenir; yavaş widget'lar iskelet
gösterir.
UC-3.4TEMELPanoda global tarih filtresi değiştirilirTüm widget'lar aynı anda güncellenir.
UC-3.5TEMELWidget'ta bir dilime tıklanırAlt kırılıma inilir; geri dönülebilir.
UC-3.6TEMELPanoya ekleme sırasında eşik tanımlanırEşik aşıldığında bildirim üretilir; bildirim kanalı seçilebilir.
UC-3.7TEMEL'Bu ay ciro' sorulur, ardından 'peki geçen
yıl?' denir
Sistem bağlamı taşır; yeni soruda metrik tekrar
belirtilmesine gerek kalmaz.
UC-3.8TEMEL'Aynı grafiğe doğalgazı da ekle' denirMevcut grafik güncellenir; yeni grafik açılmaz.
UC-3.9REGRESYONSayfa yenilenirSohbet geçmişi ve bağlam korunur.
UC-3.10TEMELAynı soru iki gün arayla sorulurDeğişim otomatik gösterilir: 'geçen sefer 1,2M idi, şimdi
## 1,45M (+%20)'.
UC-3.11SINIRMetrik tanımı değiştikten sonra aynı soru
sorulur
Fark 'tanım değişti' olarak işaretlenir, veri değişimi ile
karıştırılmaz.
UC-3.12TEMEL'Bundan sonra hep son 30 gün al' denirTercih kaydedilir; sonraki sorgularda tekrar söylemeye
gerek kalmaz.
UC-3.13GÜVENLİKKullanıcı ayarlardan tercihlerini görüntülerTüm kayıtlı tercihleri görebilir ve silebilir.
UC-3.14REGRESYONVektör indeksi silinip yeniden kurulurHiçbir bilgi kaybı olmaz (kaynak gerçeği Git'teki
knowledge dosyalarıdır).
UC-3.15TEMELPazartesi 08:00'e rapor planlanırRapor tam o saatte e-posta/WhatsApp ile ulaşır; iki kez
gönderilmez.
UC-3.16SINIRZamanlanmış gönderim başarısız olurTekrar denenir ve kullanıcı bilgilendirilir.
UC-3.17TEMELHedefi tanımlı bir metrik sorulurCevapta gerçekleşen/hedef, sapma ve kalan süre
otomatik gelir.
UC-3.18SINIRHedefi olmayan bir metrik sorulurSistem hedef uydurmaz; 'hedef tanımlı değil' der.
UC-3.19TEMELYeni bir metrik tanımlanırCapability Explorer listesinde otomatik belirir (elle
güncelleme gerekmez).
UC-3.20TEMELCevap ekranında 'Bilgiye kaydet' denirSoru-SQL çifti kaydedilir; benzer soruda geri çağrılır.
UC-3.21TEMELKnowledge Center'a yeni kural eklenir ('iptal
siparişleri hariç tut')
Sonraki tüm ilgili sorgularda kural uygulanır.
DİMA · 0→100 Görev Takip Dosyası30 / 126

## İŞ BAĞLAMI, GÖREV VE RİTİM MOTORU
Bu fazın tezi tek cümlede: veritabanı iş değildir. Sistem şirketin ne sattığını, nasıl para kazandığını, kimin neyden sorumlu
olduğunu ve hangi takvimde yaşadığını bilmeden ne proaktif olabilir ne isabetli. Burada iş bağlamı kütüğü kurulur, güncel
tutulur ve üstüne görev/ritim motoru bindirilir.
3B.1DATAP0İş bağlamı kütüğü ve keşif sihirbazı: ne satıyoruz, kime, nasıl para kazanıyoruz, kritik başarı
faktörü ne, süreç akışı nasıl, kim neyden sorumlu — sohbetle çıkarılır, onaylanır, versiyonlanır
3B.2DATAP0Ticari varlık kartları: ürün/hizmet kataloğu + reçete (BOM), tedarikçi ve müşteri kartları
(vade, performans, risk), sözleşme envanteri (cezai şart, vade, yenileme)
3B.3DATAP0Kurumsal takvim ve paydaş haritası: ay sonu kapanış, denetim dönemi, sezon, bütçe takvimi
+ kim kimden ne bekliyor. Proaktifliğin isabeti bu takvime bağlıdır
3B.4GOVP0Bilgi sahipliği ve tazelik SLA'sı: her iş bilgisinin bir sahibi ve yenilenme periyodu vardır; süresi
geçen bilgi 'bayat' işaretlenir ve cevaplarda güven düşürür
3B.5DATAP0İş terimleri sözlüğü: şirketin kendi diliyle kanonik tanımlar; 'net satış nedir' tartışması burada
biter ve tüm katmanlar aynı tanımı kullanır
3B.6ENGP0Görev motoru v1: chat'ten görev oluşturma, sorumlu ve tarih atama, durum takibi, iç görev
tahtası
3B.7LLMP0Görev önerisi motoru: 'ne yapılmalı' sorusuna veriye dayalı cevap; her öneri bir bulguya ve
beklenen etkiye bağlı
3B.8GOVP0Görev–bulgu/karar bağı: her görev bir bulguya, anomaliye veya karara bağlanır. 'Bu iş neden
var?' sorusu her zaman cevaplanabilir olmalı
3B.9ENGP1Görev sağlığı izleme: sahipsiz, süresi geçmiş, tıkanmış, tekrar açılmış görevlerin otomatik
tespiti ve raporlanması
3B.10LLMP1Taahhüt yakalama: sohbette veya toplantıda verilen sözün ('halledeceğim', 'yarın
gönderirim') otomatik göreve dönüşmesi — kullanıcı onayıyla
3B.11UIP0Sabah brifingi ritüeli: dün ne bitti / bugün ne var / yarın ne geliyor / fırsat / öneri. Sabit format,
30 saniyede okunur, kanaldan (uygulama, e-posta, WhatsApp) düşer
3B.12UIP0Departman + genel çift görünüm: her departmanın kendi paneli ve tüm şirketin birleşik
görünümü; aynı metrik iki kapsamda tutarlı
3B.13LLMP1Bildirim yorgunluğu yönetimi: uyarılar önem sırasına göre gruplanır, tekrar bastırılır, sessiz
saat tanımlanır. Gürültü körlüğe yol açar
## FAZ 3B
## →62%
## R10R11R12
## F27
## R13R14R15
## R16R20
## R17
## R19F15
## R30R31R34
## R32F12
## R35BE19
## R36
## R37
## R6R1Y1
## R7F14
## R9BE11
✅ KABUL TESTLERİ / USE-CASE'LER 16 senaryo · TEMEL: 10 · SINIR: 5 · GÜVENLİK: 1
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-3B.1TEMELKurulumda iş bağlamı sihirbazı
çalıştırılır
Ne satıldığı, süreç akışı ve sorumluluklar sohbetle çıkarılır ve
kullanıcı tarafından onaylanır.
UC-3B.2SINIRKullanıcı iş tanımında hata yaparSonradan düzeltilebilir; düzeltme versiyonlanır, eski hâli
kaybolmaz.
DİMA · 0→100 Görev Takip Dosyası31 / 126

Agentic Analiz + Chat-İçi Dashboard
[demo D3 analitik omurgası] Tek soruyla çok-grafikli, yorumlu, kök-nedenli analiz panosu kuran agent.
4.1LLMP0Agentic Orchestrator (ReAct): plan→araç→gözlem→sentez + iterasyon limiti + hata hafızası
## AMAÇ
Tek soruyla çok adımlı analiz yapabilen ajan döngüsünü kurmak.
## NASIL
Döngü: Düşün (plan yap) → Araç seç ve çalıştır → Sonucu gözle → Yeter mi? → Yetmezse tekrarla.
Ajan her turda yapılandırılmış çıktı üretsin (JSON): {düşünce, seçilen_araç, parametreler}.
Maksimum tur sayısı (5) ve toplam süre limiti koy.
Her turun girdisi/çıktısı loglansın; kullanıcıya düşünme adımları olarak stream edilsin.
Ajan asla doğrudan SQL yazmaz; araçları çağırır (araçlar 4.2/4.3'te tanımlı).
## BİTTİ SAYILIR
'Ciro neden düştü?' sorusu en az 3 araç çağrısıyla anlamlı cevap üretiyor.
Tur limiti aşıldığında sistem kısmi sonuç + açıklama veriyor, sonsuz dönmüyor.
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-3B.3TEMELBir ürünün reçetesi (BOM) girilirMaliyet, marj ve karbon hesapları aynı reçeteyi kullanır; iki farklı
sonuç çıkmaz.
UC-3B.4TEMELSözleşme envanterine yeni
sözleşme eklenir
Vade ve yenileme tarihi takvime düşer; 90 gün kala hatırlatma
üretilir.
UC-3B.5SINIRTazelik SLA'sı geçen bir iş bilgisi
kullanılır
Cevapta 'bu bilgi bayat' uyarısı çıkar ve güven skoru düşer.
UC-3B.6TEMELBakım ajanı çalışırSahibi belirsiz veya süresi geçmiş bilgiler için sorumluya soru
gönderilir.
UC-3B.7GÜVENLİKSahipsiz bir iş bilgisi tespit edilirSahipsiz kalamaz; sistem sahip atanmasını ister.
UC-3B.8TEMEL'Net satış' iki farklı departmanca
sorulur
İkisi de sözlükteki kanonik tanımı alır; farklı sonuç çıkmaz.
UC-3B.9TEMELChat'ten 'X tedarikçisinden teklif
istensin' denir
Görev oluşur, sorumlu ve tarih atanır, iç tahtada görünür.
UC-3B.10TEMELGörev listesi açılırHer görevin hangi bulgu veya karardan doğduğu görülebilir.
UC-3B.11SINIRBir görev 2 hafta hareketsiz kalır'Tıkanmış' olarak işaretlenir ve sahibine bildirilir.
UC-3B.12TEMELToplantıda 'yarın gönderirim' denirSistem taahhüdü yakalar ve onaya sunar; kullanıcı reddedebilir.
UC-3B.13TEMELSabah 08:00 gelirBrifing kanaldan düşer; dün/bugün/yarın/fırsat/öneri bölümleri
doludur ve 30 saniyede okunur.
UC-3B.14SINIRBrifingde söylenecek önemli bir şey
yoktur
Sistem uydurmaz; 'olağandışı bir durum yok' der ve kısa keser.
UC-3B.15TEMELAynı metrik departman ve genel
panelde açılır
İki görünümde de tutarlı sonuç verir.
UC-3B.16SINIRKısa sürede çok sayıda uyarı
tetiklenir
Gruplanır ve önem sırasına konur; kullanıcı bildirim
bombardımanına uğramaz.
## FAZ 4
## →72%
## F3
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası32 / 126

4.2ENGP0Araç kayıt sistemi (tool registry) — Wren ilkelbileşenleri üstünde
## AMAÇ
Ajanın kullanabileceği araçları kayıtlı ve şemalı hale getirmek.
## NASIL
Her araç: ad, açıklama, girdi şeması (JSON Schema), çıktı şeması, maliyet sınıfı.
Araç kaydı merkezi olsun; ajana yalnız intent'e uygun 4-6 araç gösterilsin (kalabalık prompt doğruluğu düşürür).
Araç çağrısı doğrulanmadan çalışmaz (şema kontrolü).
Her araç çağrısı ayrı loglanır ve süresi ölçülür.
## BİTTİ SAYILIR
Yeni araç eklemek tek dosya değişikliğiyle mümkün.
Şemaya uymayan çağrı çalışmadan reddediliyor.
4.3WRENP0Araç portları: query_metric→cube, rank/compare→cube, sample/distinct→query, explain→dry-
plan, recall→memory
## AMAÇ
Araçların gerçek işi Wren motorunun deterministik ilkelbileşenlerine yaptırmak.
## NASIL
query_metric → cube query (LLM'siz kesin hesap).
compare_periods / rank_entities → cube (time-dimension ve limit parametreleriyle).
get_sample / get_distinct → sınırlı query (LIMIT zorunlu).
explain_plan → dry-plan (maliyetsiz kontrol).
recall → hafızadan benzer altın sorgu getirme.
Hiçbir araç serbest SQL kabul etmez; hepsi yapısal parametre alır.
## BİTTİ SAYILIR
Araçların ürettiği sonuçlar doğrudan cube ile alınanlarla birebir aynı.
Serbest SQL enjeksiyonu denemesi araç katmanında engelleniyor.
4.4LLMP0DataProcessor: trend / anomali (Z-score) / istatistiksel özet motoru
## AMAÇ
Sayılardan otomatik anlam çıkarabilmek için istatistik motoru.
## NASIL
Trend: doğrusal regresyon eğimi + yön (yükseliyor/düşüyor/yatay) + anlamlılık.
Anomali: z-skoru (|z|>2.5) ve mevsimsellik varsa hareketli ortalamaya göre sapma.
Özet istatistik: min, max, ortalama, medyan, değişim %, en çok katkı yapan kalem.
Yetersiz veri kontrolü: 5 noktadan az ise trend hesaplama, 'yetersiz' döndür.
Bu motorun çıktısı yorum katmanına (2.5) girdi olur — LLM'e ham satır değil bu özet gider.
## BİTTİ SAYILIR
Bilinen bir anomali içeren test verisinde anomali doğru tespit ediliyor.
Az veriyle sahte trend üretilmiyor.
4.5LLMP0Chat-içi çok-grafikli analiz üretimi ('sonraki şubeyi nerede açalım' → 4-5 grafik+içgörü tek
ekran)
## AMAÇ
Tek soruya tek grafikle değil, komple analiz ekranıyla cevap vermek.
## NASIL
Ajan soruyu alt sorulara böler (ör. 'nerede şube açalım' → mevcut şube performansı, bölge potansiyeli, maliyet,
rekabet).
Her alt soru için uygun aracı çağırır, sonucu kart olarak tuvale ekler.
En sonda birleştirici özet üretir: bulgular + öneri + belirsizlikler.
Kartların sırası mantıksal olsun (durum → sebep → öneri).
## BİTTİ SAYILIR
Tek soru 4-6 kartlık tutarlı bir analiz üretiyor.
Kartlar birbirini tekrar etmiyor.
## F3
## 1.
## 2.
## 3.
## 4.
## •
## •
## 1.
## 2.
## 3.
## 4.
## 5.
## 6.
## •
## •
## F11Ç6
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## D45
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası33 / 126

4.6UIP0Analizden: rapora çevir / bir noktaya odaklan / derinleş aksiyonları
## AMAÇ
Analiz sonrası kullanıcının yönü belirleyebilmesi.
## NASIL
Analiz altında üç aksiyon: 'Rapora çevir', 'Şuna odaklan' (kart seçimi), 'Daha derine in'.
Odaklan seçildiğinde ajan yalnız o kartı genişletir (yeni analiz başlatmaz).
Derine in: seçilen bulgunun kök nedenini araştırır (4.8'i çağırır).
## BİTTİ SAYILIR
Kullanıcı analizden rapora tek tıkla geçebiliyor.
Odaklanma yeni baştan analiz yapmıyor, mevcut bağlamı kullanıyor.
4.7LLMP0Bağlamsal analiz promptu (grafik + yorum + analiz + öneri birlikte)
## AMAÇ
Grafik + yorum + öneriyi tek bütün olarak üretmek (dağınık parçalar değil).
## NASIL
Prompt şablonu: rol + şirket bağlamı (Faz 5) + soru + hesaplanmış bulgular + istenen çıktı yapısı.
Çıktı yapısı zorunlu: özet, bulgular listesi, öneri, belirsizlikler.
Şirket hafızası ve kurallar prompt'a otomatik enjekte edilsin.
Çıktı şemaya uymuyorsa bir kez düzelttir, yine uymuyorsa şablonlu yedeğe düş.
## BİTTİ SAYILIR
Üretilen cevaplar her zaman aynı yapıda (özet/bulgu/öneri/belirsizlik).
Şirket kuralları cevaplarda gerçekten uygulanıyor.
4.8LLMP0Kök-neden / varyans ayrıştırma motoru
## AMAÇ
'Neden' sorusuna sistematik cevap üretmek — ürünün en değerli yeteneklerinden biri.
## NASIL
Toplam değişimi bileşenlere ayır: hangi boyut ne kadar katkı yaptı (varyans ayrıştırma).
Sırayla dene: zaman (hangi hafta), kategori (hangi ürün/şube), müşteri, kanal.
En büyük katkı yapan 1-3 kalemi bul, gerekirse bir seviye daha derine in.
Karışım etkisini (mix effect) fiyat/miktar etkisinden ayır.
Çıktı: 'Düşüşün %70'i X şubesinden, onun da %60'ı Y ürün grubundan kaynaklanıyor.'
## BİTTİ SAYILIR
Bilinen sebebi olan test verisinde doğru kök neden bulunuyor.
Cevap yüzde katkılarıyla birlikte veriliyor, sadece 'düştü' demiyor.
4.9WRENP1Skills: tekrarlanan iş akışını kaydet/koş
## AMAÇ
Tekrarlanan analizleri kaydedip tek tıkla çalıştırmak.
## NASIL
Skill = adımlar dizisi (hangi araç, hangi parametre) + ad + açıklama + sahip.
Kullanıcı bir analizi 'skill olarak kaydet' diyebilir; sistem adımları yakalar.
Parametreler değişken olabilir (dönem, şube) — çalıştırırken sorulur.
Skills ekip içinde paylaşılabilir; kullanım sayacı tutulur.
## BİTTİ SAYILIR
Kaydedilen skill farklı dönemle tekrar çalıştırılabiliyor.
Skill çalıştırma LLM maliyeti üretmiyorsa (deterministik adımlar) bu ölçülüyor.
## D45
## 1.
## 2.
## 3.
## •
## •
## D34
## 1.
## 2.
## 3.
## 4.
## •
## •
## Y5D32Ç13
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
F17wSKILLS
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası34 / 126

4.10WRENP1wren-langchain / wren-pydantic SDK entegrasyonu (agent framework)
## AMAÇ
Ajan altyapısını standart çerçevelere bağlamak (tekerleği yeniden icat etmemek).
## NASIL
wren-langchain / wren-pydantic SDK'larını incele ve araç katmanına adapte et.
Ajan durumunu (state) kalıcı sakla ki uzun işler kesintide devam edebilsin.
Framework'e bağımlılığı tek bir adaptör dosyasında topla (değiştirmek kolay olsun).
## BİTTİ SAYILIR
Ajan çalışırken servis yeniden başlarsa iş kaldığı yerden devam ediyor.
Framework değişimi tek dosyayı etkiliyor.
4.11WRENP1functions (governed primitive) + rich retrieval bağlama
## AMAÇ
Wren'in yönetişimli çalıştırma ilkelbileşenlerini kullanmak.
## NASIL
functions: motor tarafında tanımlı güvenli fonksiyonları ajana aç.
rich retrieval: şema + örnek değer + ilişki bilgisini birlikte getir.
Satır limiti ve zaman aşımı motor seviyesinde zorunlu olsun.
## BİTTİ SAYILIR
Ajan limitsiz sorgu çalıştıramıyor.
Motor seviyesinde uygulanan limitler loglarda görünüyor.
4.12GOVP1DCM (AI_MODE=off) v1: cube+rapor menü/ActionCard akışı — tam hardening 7.4
## AMAÇ
Yapay zekâ tamamen kapalıyken de sistemin çalışması (banka/kamu için satış argümanı).
## NASIL
AI_MODE=off ayarında chat serbest metin kabul etmez; menü ve kartlar gösterilir.
Kullanıcı metrik/rapor/keşif kartlarından seçerek ilerler (3 adımlı sihirbaz).
Tüm sonuçlar cube üzerinden gelir, güven rozeti her zaman altın.
LLM çağrısı yapılmadığı loglarla ispatlanabilir olsun.
## BİTTİ SAYILIR
AI_MODE=off iken tek bir LLM çağrısı bile yapılmıyor (log kanıtı).
Kullanıcı menüden 3 tıkla metrik sonucuna ulaşabiliyor.
4.13LLMP0Denetimli döngü — 4 katmanlı adım doğrulama: dry-plan (sözdizimi) → dry-run (çalışabilirlik)
→ akıl sağlığı (satır 0 mı, null oranı, büyüklük mertebesi) → amaç (çıktı soruyu cevaplıyor mu)
## AMAÇ
Ajanın her adımını doğrulamak: hatalı adım bir sonrakine yayılmasın.
## NASIL
Katman 1 — Sözdizimi: dry-plan ile SQL geçerli mi?
Katman 2 — Çalışabilirlik: dry-run ile DB kabul ediyor mu?
Katman 3 — Akıl sağlığı: sonuç 0 satır mı, null oranı %90+ mı, büyüklük mertebesi beklenenin 100 katı mı? (şüpheli
işaretle)
Katman 4 — Amaç: dönen kolonlar sorulan soruyu cevaplıyor mu? (ör. 'hangi şube' sorusuna şube kolonu geldi mi)
Herhangi bir katman başarısızsa adımı başarısız işaretle ve düzeltme akışına gönder.
## BİTTİ SAYILIR
Boş sonuç dönen adım 'başarılı' sayılmıyor.
Mantıksız büyüklükteki sonuçlar kullanıcıya uyarıyla sunuluyor.
wSDK
## 1.
## 2.
## 3.
## •
## •
wFUNC
## 1.
## 2.
## 3.
## •
## •
## F9
## D14Ç17
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE18F3
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası35 / 126

4.14LLMP0Plan-kontrol listesi: ajan işi baştan adımlara böler, her adım tamamlandı/başarısız işaretlenir
→ '%100' ölçülebilir hale gelir; ilerleme UI'da görünür
## AMAÇ
'%100 tamamlandı' ifadesini ölçülebilir kılmak.
## NASIL
Ajan işe başlamadan önce plan üretir: 3-6 adımlık kontrol listesi.
Her adımın durumu: bekliyor / çalışıyor / tamamlandı / başarısız / atlandı.
İlerleme yüzdesi = tamamlanan adım / toplam adım.
Kullanıcı bu listeyi canlı görür; hangi adımda olduğunu bilir.
Plan çalışma sırasında değişebilir ama değişiklik kullanıcıya görünür.
## BİTTİ SAYILIR
Kullanıcı analizin hangi adımında olduğunu her an görebiliyor.
Başarısız adımlar listede kırmızı olarak kalıyor, gizlenmiyor.
4.15LLMP0İlerleme tespiti + hata sınıflandırma: aynı hata 2. kez → tekrar deneme değil strateji değiştir;
düzeltilemez hata (veri yok / yetki yok) → dürüst red, döngüye sokma
## AMAÇ
Ajanın aynı hataya takılıp para yakmasını engellemek.
## NASIL
Hata imzası tut (hata tipi + adım + parametre). Aynı imza 2. kez gelirse aynı yöntemi tekrar deneme.
Strateji değiştir: farklı araç, daha dar kapsam, veya kullanıcıya soru.
Hataları sınıflandır: DÜZELTİLEBİLİR (SQL hatası, yanlış kolon adı) → düzeltme dene. DÜZELTİLEMEZ (veri yok, yetki
yok, tablo yok) → hemen dürüst red, döngüye sokma.
Düzeltilemez hatada kullanıcıya somut çözüm öner ('bu tabloyu bağlamanız gerekiyor').
## BİTTİ SAYILIR
Yetkisiz veri istendiğinde sistem 1 saniyede reddediyor, 5 tur denemiyor.
Aynı hata üst üste 3 kez tekrarlanmıyor.
4.16ENGP0Bütçe tavanı: iterasyon + token + süre limiti; aşımda kısmi sonuç + neyin yapılamadığının
açık beyanı
## AMAÇ
Maliyetin kontrolden çıkmasını engellemek.
## NASIL
Her analiz için bütçe: maksimum tur, maksimum token, maksimum süre (ör. 5 tur / 50K token / 90 sn).
Bütçe tenant paketine göre değişebilsin.
Aşımda: o ana kadarki bulguları göster + 'şu kısmı tamamlayamadım' açıklaması + devam etme seçeneği.
Bütçe aşımlarını logla; sık aşan soru tipleri terfi motoruna (8.14) girdi olsun.
## BİTTİ SAYILIR
Hiçbir analiz belirlenen bütçeyi aşamıyor.
Bütçe aşımında kullanıcı boş ekranla değil kısmi sonuçla karşılaşıyor.
4.17ENGP0Refleks yayı: hızlı yol (kural/eşik, $0, milisaniye) ile derin bilişsel döngü (LLM, bütçeli) kesin
olarak ayrılır; her olay önce refleks halkasından geçer
## BE18F3
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE18F5
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE18BE10
## 1.
## 2.
## 3.
## 4.
## •
## •
## R63BE1
✅ KABUL TESTLERİ / USE-CASE'LER 23 senaryo · TEMEL: 8 · SINIR: 9 · REGRESYON: 4 · GÜVENLİK: 2
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-4.1TEMEL'Ciro neden düştü?' sorulurEn az 3 araç çağrısıyla çok adımlı analiz yapılır; kök neden
yüzde katkılarıyla verilir.
UC-4.2SINIRAjan 5 tur sonunda sonuca
ulaşamaz
Sonsuz döngüye girmez; kısmi sonuç + neyin yapılamadığı
açıklaması döner.
UC-4.3REGRESYONAjanın kullandığı araç sonuçları cube
ile karşılaştırılır
Birebir aynı sonuçlar çıkar (araçlar deterministik ilkelbileşenlere
bağlı).
UC-4.4GÜVENLİKAraca serbest SQL enjekte edilmeye
çalışılır
Şema doğrulaması reddeder; sorgu çalışmaz.
DİMA · 0→100 Görev Takip Dosyası36 / 126

IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-4.5TEMELBilinen anomali içeren test verisinde
analiz yapılır
Anomali doğru tespit edilir ve işaretlenir.
UC-4.6SINIR4 veri noktalı seride trend istenirSahte trend üretilmez; 'yetersiz veri' bildirilir.
UC-4.7TEMEL'Sonraki şubeyi nerede açalım?'
sorulur
4-6 kartlık tutarlı analiz üretilir (durum → sebep → öneri
sırasıyla), kartlar birbirini tekrar etmez.
UC-4.8TEMELAnaliz sonrası 'şuna odaklan' denirYeni baştan analiz başlamaz; mevcut bağlam kullanılarak o kart
genişletilir.
UC-4.9REGRESYONÜretilen 10 cevap incelenirHepsi aynı yapıda: özet, bulgular, öneri, belirsizlikler.
UC-4.10TEMELBilinen sebebi olan test verisinde
kök neden sorulur
Doğru kırılım bulunur ve yüzde katkı verilir ('düşüşün %70'i X
şubesinden').
UC-4.11TEMELBir analiz 'skill olarak kaydet' ile
saklanır
Farklı dönemle tekrar çalıştırılabilir; parametreler sorulur.
UC-4.12SINIRAjan çalışırken servis yeniden
başlatılır
İş kaldığı yerden devam eder.
UC-4.13GÜVENLİKAI_MODE=off yapılırTek bir LLM çağrısı bile yapılmaz (log kanıtı); kullanıcı menüden
3 tıkla metrik sonucuna ulaşır.
UC-4.14SINIRAjan adımı 0 satır döndürürAdım 'başarılı' sayılmaz; akıl sağlığı kontrolü yakalar.
UC-4.15SINIRSonuç beklenenin 100 katı
büyüklükte gelir
Şüpheli olarak işaretlenir ve kullanıcıya uyarıyla sunulur.
UC-4.16TEMELUzun bir analiz başlatılırKullanıcı 3-6 adımlık plan listesini görür; hangi adımda olduğunu
her an bilir.
UC-4.17SINIRBaşarısız bir adım oluşurListede kırmızı kalır, gizlenmez.
UC-4.18SINIRYetkisiz bir tabloya erişim istenir1 saniyede dürüst red verilir; 5 tur denenmez (düzeltilemez
hata sınıfı).
UC-4.19REGRESYONAynı hata üst üste alınırİkinci denemede strateji değişir; aynı yöntem 3. kez denenmez.
UC-4.20SINIRAnaliz bütçe tavanını aşarO ana kadarki bulgular gösterilir + tamamlanamayan kısım
açıklanır; boş ekran gelmez.
UC-4.21TEMELBeklentiye uyan rutin bir olay gelir
## (4.17)
Refleks halkasında milisaniyeler içinde işlenir; LLM hiç çağrılmaz
ve maliyet oluşmaz.
UC-4.22SINIRRefleks eşiğini aşan bir sapma olurDerin bilişsel döngü devreye girer; geçiş kararı ve gerekçesi
loglanır.
UC-4.23REGRESYONBir gün boyunca olay dağılımı
ölçülür
Olayların büyük çoğunluğu refleks halkasında bitmiş olmalı;
oran panelde görünür.
DİMA · 0→100 Görev Takip Dosyası37 / 126

## Otomatik Açılış Panosu + Global Şirket Hafızası
İlk günden şirketi tanıyan, boş-ekran yerine değer sunan, her analize 'bütünü bilerek' başlayan sistem.
5.1LLMP0Kurulumda şirket keşfi → şemayı+örnek veriyi tarayıp global memory'ye şirket özeti
## AMAÇ
Sistemin bağlandığı şirketi tanıması — tüm bağlamsal yorumların temeli.
## NASIL
Kurulum sonrası arka plan işi: tablo adları, kolonlar, satır sayıları, örnek değerler (maskeli) taranır.
LLM'e YALNIZ metadata gönderilir (ham satır değil, Plane Enforcer kuralı): 'bu şema hangi sektöre ait, hangi
departmanlar var?'
Çıktı: sektör, iş modeli, ana departmanlar, kritik metrik adayları, veri kalitesi notları.
Bu özet ŞirketProfili olarak saklanır ve her analiz prompt'una eklenir.
Özet kullanıcıya gösterilir ve düzeltilebilir (5.2).
## BİTTİ SAYILIR
Şirket profili 5 dakikada üretiliyor ve sektörü doğru tahmin ediyor.
Profil her analizde bağlam olarak kullanılıyor (prompt logunda görünüyor).
5.2UIP0Şirket Portresi ekranı ('şunu anladım... doğru mu?') + otomatik kişiye/şirkete özel açılış panosu
## AMAÇ
Boş ekran yerine, sistemin şirketi tanıdığını gösteren karşılama.
## NASIL
Şirket Portresi ekranı: 'Şunu anladım: tekstil üreticisisiniz, 3 tesisiniz var, AB'ye ihracat yapıyorsunuz. Doğru mu?'
Kullanıcı onaylar veya düzeltir; düzeltme ŞirketProfili'ne yazılır.
Onay sonrası otomatik açılış panosu üretilir: sektöre ve bulunan metriklere göre 4-6 widget.
Pano kullanıcıya özel değişebilir (rolüne göre farklı widget).
## BİTTİ SAYILIR
Kurulum biter bitmez dolu bir pano açılıyor (boş ekran yok).
Kullanıcı portredeki hatayı düzeltebiliyor.
5.3LLMP0Global özet güncelleme (haftalık / büyük veri değişimi)
## AMAÇ
Şirket profilinin zamanla bayatlamasını engellemek.
## NASIL
Tetikleyiciler: haftalık zamanlanmış yenileme, büyük veri yüklemesi, yeni tablo eklenmesi, metrik tanımı değişikliği.
Yenilemede sadece değişen kısmı güncelle (tam yeniden tarama pahalı).
Profil değişimi önemliyse kullanıcıya bildir ('yeni bir departman verisi tespit ettim').
## BİTTİ SAYILIR
Yeni tablo eklendiğinde profil 24 saat içinde güncelleniyor.
Gereksiz yere her gün tam tarama yapılmıyor.
5.4LLMP0Global özet her analize bağlam enjeksiyonu (resmin bütününe hâkim yorum)
## AMAÇ
Her cevabın şirketin bütününü bilerek üretilmesi.
## NASIL
ŞirketProfili özetini (kısaltılmış, token bütçeli) her analiz prompt'una ekle.
Bütçe: profil için maksimum ~800 token; öncelik sırası sektör > departmanlar > kritik metrikler.
Profil bilgisi çelişki yaratırsa veri kazanır (profil yorumdur, veri gerçektir).
Yorumlarda profil bağlamı kullanıldığında bunu belirt.
## BİTTİ SAYILIR
Aynı soru profil olmadan ve profille sorulduğunda ikincisi daha isabetli yorum üretiyor.
Prompt token bütçesi aşılmıyor.
## FAZ 5
## →82%
## BE5
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## UX4
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE5BE9
## 1.
## 2.
## 3.
## •
## •
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası38 / 126

5.5LLMP1'Beni tanıyorsun, pazartesi özetim ne?' kişisel brifing
## AMAÇ
Kullanıcıya özel, hafızadan beslenen kişisel brifing.
## NASIL
Kullanıcının rolü, geçmiş soruları ve favori metriklerinden brifing içeriği seç.
Format: 3 kritik sayı + 1 anomali + 1 öneri (kısa, taranabilir).
İstenirse zamanlanmış olarak gönderilebilsin (3.9 ile bağlanır).
## BİTTİ SAYILIR
İki farklı kullanıcı farklı brifing alıyor.
Brifing 30 saniyede okunabilecek uzunlukta.
5.6DATAP0Seçici yazma politikası: yalnız şunlar hafızaya yazılır — tekrar (N kez soruldu), kullanıcı
düzeltmesi (en değerli sinyal), açık öğretme, verilen karar, oturmuş tanım, doğrulanmış anomali. Gerisi gürültüdür,
yazılmaz
## AMAÇ
Hafızayı çöplüğe çevirmemek: neyin kaydedileceğine karar veren politika.
## NASIL
Kayıt kriterleri (yalnız bunlar yazılır): (1) tekrar — aynı bilgi N kez geçti, (2) kullanıcı düzeltmesi — en değerli sinyal,
(3) açık öğretme — 'bunu hatırla', (4) verilen karar, (5) oturmuş tanım, (6) doğrulanmış anomali.
Kriterlere uymayan hiçbir şey yazılmaz (her sohbeti kaydetme).
Her kayda kaynak, tarih, sahip ve güven notu eklenir.
Yazma öncesi PII maskeleme uygulanır.
## BİTTİ SAYILIR
Rastgele 20 hafıza kaydı incelendiğinde hepsi kriterlerden birine uyuyor.
Hafıza boyutu kullanımla orantısız büyümüyor.
5.7DATAP0Kapsam katmanları + öncelik: Kişi < Departman/DataSource < Şirket < Politika; öncelik içerik
tipine göre değişir (tercihte kişi, tanımda şirket, kuralda politika kazanır)
## AMAÇ
Çelişen bilgilerde hangisinin kazanacağını belirlemek.
## NASIL
Kapsam katmanları: Kişi < Departman/VeriKaynağı < Şirket < Politika.
AMA öncelik içerik tipine göre değişir: tercihlerde KİŞİ kazanır (para birimi, format); tanımlarda ŞİRKET kazanır (net
satış nedir); kurallarda POLİTİKA kazanır (kimse ezemez).
Bu matrisi kodda tek bir çözümleyici fonksiyonda topla.
Çelişki tespit edilirse logla ve yöneticiye bildir.
## BİTTİ SAYILIR
Kişisel tercih şirket tanımını ezemiyor.
Politika kuralı hiçbir katman tarafından geçersiz kılınamıyor.
5.8DATAP1İçerik tipi ayrımı ve ayrı geri çağırma stratejileri: semantik (tanım) / epizodik (ne oldu) /
prosedürel (nasıl yapılır) / tercih
## AMAÇ
Farklı hafıza türlerini farklı şekilde saklayıp getirmek.
## NASIL
Semantik (tanım/gerçek): 'net satış = ciro - iade' → vektör + tam metin.
Epizodik (ne oldu): 'Mart'ta X müşterisi kaybedildi' → zaman damgalı olay kaydı.
Prosedürel (nasıl yapılır): skill/SOP adımları → yapılandırılmış.
Tercih: kullanıcı ayarı → anahtar-değer.
Getirme stratejisi türe göre farklı: tanım için benzerlik, olay için zaman aralığı, prosedür için ad eşleşmesi.
## BİTTİ SAYILIR
Bir olay sorgusu ('geçen çeyrek ne olmuştu') doğru epizodik kayıtları getiriyor.
Tür karışıklığı yaşanmıyor.
## D58
## 1.
## 2.
## 3.
## •
## •
## BE20F16
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE20F16R28
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE20
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası39 / 126

5.9DATAP1Unutma motoru: çürüme skoru (tazelik × sıklık × doğrulanma) → gözden düşür → arşivle
(SİLME YOK, denetlenebilirlik); çelişkide yeni kazanır, eski 'geçersiz kılındı' bağıyla saklanır
## AMAÇ
Hafızanın zamanla çürümesi ve çelişkilerin yönetimi.
## NASIL
Çürüme skoru = tazelik × kullanım sıklığı × doğrulanma sayısı.
Skor eşiğin altına düşen kayıt önce 'gözden düşmüş' işaretlenir (getirmede düşük öncelik).
Sonra arşivlenir — ASLA SİLİNMEZ (denetlenebilirlik için).
Çelişki: yeni bilgi kazanır, eski kayıt 'geçersiz kılındı' bağıyla saklanır (kim, ne zaman, neden).
Arşiv taranabilir olsun ('bu tanım eskiden neydi?').
## BİTTİ SAYILIR
Eski tanımın ne olduğu ve ne zaman değiştiği sorgulanabiliyor.
Kullanılmayan kayıtlar aramada üste çıkmıyor.
5.10GOVP0Kişisel hafıza şeffaflığı: kullanıcı kendi hafızasını görür, düzeltir, siler (KVKK gereği)
## AMAÇ
KVKK gereği kişinin kendi hafızasını görebilmesi ve silebilmesi.
## NASIL
Ayarlar altında 'Hakkımda bilinenler' ekranı: sistemin bu kullanıcı için tuttuğu tüm kayıtlar.
Her kayıt düzenlenebilir ve silinebilir; silme talebi loglanır.
Silme gerçek silme olsun (arşive değil) — kişisel veri istisnası.
Dışa aktarma seçeneği (veri taşınabilirliği).
## BİTTİ SAYILIR
Kullanıcı kendisiyle ilgili tüm kayıtları görebiliyor ve silebiliyor.
Silinen kişisel kayıt sonraki cevaplarda kullanılmıyor.
5.11DATAP07 katmanlı hafıza ağı: oturum → kişi → departman → şube/tesis → şirket/holding → sektör (k-
anonim) → sistem geneli (anonim). Her katmanın kendi yazma kuralı ve erişim kapsamı vardır
5.12DATAP0Bağlam bakım ajanı: tazelik SLA'sı geçen iş bilgisini tespit eder, sahibine sorar ('bu hâlâ
geçerli mi?'), cevabı hafızaya işler
## BE20F6R27
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE20
## F8UX9R29
## 1.
## 2.
## 3.
## 4.
## •
## •
## R21R22R23
## R24R25R26BE20
## R17R18BE20
✅ KABUL TESTLERİ / USE-CASE'LER 22 senaryo · TEMEL: 9 · GÜVENLİK: 5 · SINIR: 6 · REGRESYON: 2
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-5.1TEMELYeni bir veritabanı bağlanır ve kurulum
tamamlanır
5 dakika içinde şirket profili üretilir; sektör doğru tahmin
edilir.
UC-5.2GÜVENLİKŞirket profili üretilirken prompt logları
incelenir
LLM'e yalnız metadata gitmiştir; hiçbir ham satır
gönderilmemiştir.
UC-5.3TEMELKurulum biterBoş ekran yerine Şirket Portresi gösterilir: 'tekstil
üreticisisiniz, 3 tesisiniz var — doğru mu?'
UC-5.4SINIRPortredeki bilgi yanlıştırKullanıcı düzeltir; düzeltme profile yazılır ve sonraki
analizlerde kullanılır.
UC-5.5TEMELPortre onaylanır4-6 widget'lı otomatik açılış panosu üretilir; kullanıcının rolüne
göre değişir.
UC-5.6TEMELYeni bir tablo eklenirŞirket profili 24 saat içinde güncellenir; her gün tam tarama
yapılmaz.
UC-5.7REGRESYONAynı soru profil olmadan ve profille
sorulur
Profille sorulan cevap belirgin şekilde daha isabetli yorum
içerir.
UC-5.8SINIRProfil bilgisi veriyle çelişirVeri kazanır; profil yorum olarak kalır, sayıyı değiştirmez.
UC-5.9TEMELİki farklı kullanıcı pazartesi brifingi isterRollerine ve geçmiş sorularına göre farklı brifing alırlar; 30
saniyede okunur.
DİMA · 0→100 Görev Takip Dosyası40 / 126

Analist Katmanı: SWOT / Tahmin / What-if / Öneri
★ DEMO HAZIR ÇİZGİSİ. 'Şirket beyni' — yorumlayan, öngören, öneren danışman. 63 demo senaryosunun tamamı buraya kadar
gösterilebilir.
★ BU FAZ SONUNDA HAFTA-İÇİ CEO DEMOSU (63 senaryo) TAM KARŞILANIR
6.1LLMP0SWOT motoru (her madde sayıya + kanıta bağlı)
## AMAÇ
Yöneticinin tek bakışta durumu görmesi.
## NASIL
6 kritik metriği (şirket profiline göre seçilmiş) tek kartta göster.
Her metriğin yanında: değer, değişim, hedefe göre durum, mini trend.
Altına üç satır yorum: iyi giden / kötü giden / izlenmesi gereken.
Yorumlar 4.4 istatistik motorundan beslenir.
## BİTTİ SAYILIR
Kart 5 saniyede yükleniyor.
Yorumlar her çeyrek değişiyor (statik metin değil).
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-5.10REGRESYON20 rastgele hafıza kaydı incelenirHepsi kayıt kriterlerinden birine uyar (tekrar, düzeltme,
öğretme, karar, tanım, anomali).
UC-5.11SINIRSıradan bir sohbet mesajı yazılırHafızaya yazılmaz; hafıza boyutu kullanımla orantısız
büyümez.
UC-5.12GÜVENLİKKullanıcı kişisel tercihiyle şirket
tanımını ezmeye çalışır
Tanımlarda şirket kazanır; kişisel tercih yalnız format/
görünüm için geçerlidir.
UC-5.13GÜVENLİKPolitika kuralı ezilmeye çalışılırHiçbir katman politikayı geçersiz kılamaz.
UC-5.14TEMEL'Geçen çeyrek ne olmuştu?' sorulurDoğru epizodik kayıtlar (olaylar) getirilir; tanım kayıtlarıyla
karıştırılmaz.
UC-5.15TEMELEskiden farklı olan bir tanım sorgulanırEski tanımın ne olduğu, ne zaman ve kim tarafından
değiştirildiği görülebilir.
UC-5.16SINIRÇelişen iki bilgi kaydedilirYeni kazanır; eski 'geçersiz kılındı' bağıyla arşivde durur,
silinmez.
UC-5.17GÜVENLİKKullanıcı 'Hakkımda bilinenler' ekranını
açar
Kendisiyle ilgili tüm kayıtları görür, düzenler ve siler; silinen
kayıt sonraki cevaplarda kullanılmaz.
UC-5.18TEMEL7 katmanlı hafızaya aynı konuda bilgi
yazılır (5.11)
Her bilgi doğru katmana düşer: kişisel tercih kişiye, şirket
tanımı şirkete, sektör kıyası anonim havuza.
UC-5.19GÜVENLİKBir kullanıcının kişisel hafızası başka
kullanıcıya sızmaya çalışır
Katman kapsamı engeller; kişi hafızası yalnız sahibinin
oturumunda kullanılır.
UC-5.20SINIRŞube hafızasındaki bilgi şirket
hafızasıyla çelişir
Öncelik kuralı uygulanır ve çelişki kullanıcıya gösterilir;
sessizce biri seçilmez.
UC-5.21TEMELTazelik SLA'sı geçmiş bir iş bilgisi
bulunur (5.12)
Bakım ajanı sahibine soru gönderir; cevap gelene kadar bilgi
'bayat' etiketiyle kullanılır.
UC-5.22SINIRBakım ajanının sorusuna 30 gün cevap
verilmez
Bilgi ağırlığı düşürülür ve yöneticiye eskalasyon yapılır;
sessizce silinmez.
## FAZ 6
## →90%
## D44
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası41 / 126

6.2LLMP0Aksiyon öneri motoru (metrik sonucuna göre önceliklendirilmiş)
## AMAÇ
Sonuçtan aksiyona geçiş: 'ne yapmalıyım' sorusunun cevabı.
## NASIL
Kural tabanlı öneri motoru: metrik + eşik + bağlam → öneri şablonu.
Öneriler önceliklendirilir (etki × aciliyet).
Her öneriye gerekçe ve beklenen etki eklenir.
Öneri kabul/ret takibi yapılır (hangi öneriler işe yaradı?).
## BİTTİ SAYILIR
Öneriler somut ve uygulanabilir ('stok artır' değil, 'X ürününde 2 haftalık stok kaldı, sipariş açın').
Kabul edilen öneriler takip ediliyor.
6.3LLMP0Tahminleme (trend + mevsimsellik, aralıklı, 'tahmindir' şerhli)
## AMAÇ
Geleceğe dair sayı üretirken dürüst olmak.
## NASIL
Yöntem: mevsimsellik + trend (basit üstel düzeltme veya Prophet benzeri); karmaşık ML gerekmez.
ÇIKTI HER ZAMAN ARALIKLI olsun: 'gelecek ay 1.2M - 1.4M TL (orta tahmin 1.3M)'.
Tahmin güven notu: veri uzunluğu ve varyansa göre düşük/orta/yüksek.
Her tahminin yanında 'bu bir tahmindir' etiketi ve dayandığı varsayımlar.
12 aydan az veri varsa tahmin üretme, 'yetersiz geçmiş' de.
## BİTTİ SAYILIR
Hiçbir tahmin tek bir kesin sayı olarak sunulmuyor.
Kısa geçmişli veride sistem tahmin uydurmuyor.
6.4LLMP0What-if / duyarlılık simülasyonu (deterministik girdiden)
## AMAÇ
'Şu değişirse ne olur' sorusunu deterministik olarak cevaplamak.
## NASIL
Model: değişken → etkilenen metrikler zinciri (ör. elektrik fiyatı → birim maliyet → marj).
Zincir kullanıcıyla birlikte tanımlanır (LLM uydurmaz).
Kullanıcı bir değişkeni değiştirir, sistem zinciri hesaplar ve etkiyi gösterir.
Duyarlılık tablosu: değişken %10, %20, %30 arttığında sonuç.
Varsayımlar açıkça listelenir.
## BİTTİ SAYILIR
Aynı girdi her zaman aynı sonucu veriyor (deterministik).
Hesaplama zinciri kullanıcıya gösterilebiliyor.
6.5UIP0Oturum sentezi ('CEO Günlüğü': konuşmadaki tüm bulgular tek rapor)
## AMAÇ
Uzun bir analiz oturumunun sonunda her şeyi tek belgede toplamak.
## NASIL
Oturum boyunca üretilen tüm kart, bulgu ve kararları topla.
Kronolojik değil tematik grupla (finans, operasyon, satış).
Her bulguya kaynak bağlantısı ekle.
Başlık ve yönetici özeti otomatik üret; kullanıcı düzenleyebilsin.
## BİTTİ SAYILIR
30 mesajlık bir oturum tek tıkla derli toplu rapora dönüşüyor.
Rapordaki her sayı kaynağına gidiyor.
## F12D63
## 1.
## 2.
## 3.
## 4.
## •
## •
## Y3D46Ç14
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## Y4D33Ç14
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## D62Ç8
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası42 / 126

6.6LLMP0Karar memosu üretici (kurul için, her sayı kaynağa bağlı)
## AMAÇ
Yönetim kuruluna sunulabilecek karar belgesi üretmek.
## NASIL
Yapı: durum, seçenekler, öneri, riskler, gerekli onay, ekler (kanıtlar).
Her sayı tıklanabilir kaynak bağlantısı taşır.
İki dilli çıktı seçeneği (TR/EN).
Şablon kurumsal olarak özelleştirilebilir.
## BİTTİ SAYILIR
Üretilen memo düzenlenmeden kurula sunulabilecek kalitede.
Kaynak bağlantıları çalışıyor.
6.7LLMP1Skor kartı motoru (şablonlu: acente / tedarikçi / temsilci)
## AMAÇ
Tekrarlayan değerlendirmeleri standartlaştırmak (tedarikçi, temsilci, şube karnesi).
## NASIL
Skor kartı tanımı: kriterler + ağırlıklar + veri kaynağı + normalizasyon yöntemi.
Şablon olarak kaydedilebilsin, farklı kapsamlarda çalıştırılabilsin.
Sonuç: sıralı liste + her kriterin katkısı + zaman içinde değişim.
Ağırlıklar kullanıcı tarafından değiştirilebilir ve etkisi anında görülebilir.
## BİTTİ SAYILIR
Aynı skor kartı her ay tekrar çalıştırılabiliyor.
Ağırlık değişimi sıralamayı doğru şekilde etkiliyor.
6.8LLMP1Kohort analizi motoru
## AMAÇ
Zaman içinde grup davranışını izlemek (müşteri, çalışan, ürün).
## NASIL
Kohort tanımı: giriş dönemi (ilk satın alma ayı) + izlenen metrik + periyot.
Kohort matrisi üret (satır: kohort, sütun: ay, hücre: değer/oran).
Isı haritası olarak görselleştir.
Kohortlar arası karşılaştırma ve trend yorumu.
## BİTTİ SAYILIR
Kohort matrisi doğru hesaplanıyor (elle doğrulandı).
Isı haritasında örüntü görsel olarak okunabiliyor.
6.9LLMP1Karbon-başabaş OEE analizi (demo özgün)
## AMAÇ
Verimlilik ile sürdürülebilirliği tek analizde birleştiren özgün metrik.
## NASIL
Her makine için: OEE seviyesi ↔ birim üretim başına karbon eğrisi çıkar.
Başabaş noktası: hangi OEE'nin altında birim karbon hedefi aşılıyor?
Makineleri iyileştirme potansiyeline göre sırala (yatırım önceliği).
Çıktı: makine listesi + mevcut OEE + hedef OEE + kazanılacak karbon/TL.
## BİTTİ SAYILIR
Analiz makine bazında somut yatırım önceliği veriyor.
Hesap elle doğrulanabiliyor.
## D53
## 1.
## 2.
## 3.
## 4.
## •
## •
## Y17
## 1.
## 2.
## 3.
## 4.
## •
## •
## Y16
## 1.
## 2.
## 3.
## 4.
## •
## •
## D47Y5Ç13
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası43 / 126

6.10LLMP1Sürdürülebilirlik analiz setleri (CBAM-tarzı emisyon dökümü, marka denetim dosyası) — Faz
8'de paketlenir
## AMAÇ
Sürdürülebilirlik raporlamasının temel analizlerini hazırlamak.
## NASIL
CBAM tarzı: sipariş/sevkiyat bazında gömülü emisyon tahsisi (üretim miktarı × birim emisyon).
Marka denetim dosyası: enerji, su, atık, kalite göstergeleri son 12 ay + hedef karşılaştırması.
Emisyon faktörleri referans tablosundan (kod içine gömme).
Çıktılar Faz 8'de sektör paketine dönüşecek şekilde şablonlansın.
## BİTTİ SAYILIR
Bir sevkiyat için emisyon dökümü üretilebiliyor.
Hesaplamada kullanılan faktörler raporda görünüyor.
6.11GOVP0Karar Kaydı v1 (demo sürümü): karar memosuna varsayım listesi + kanıt bağlantısı + sahip
alanı — tam motor Faz 6B
## AMAÇ
Karar motorunun demo için yeterli ilk sürümü.
## NASIL
Karar memosuna üç zorunlu alan ekle: varsayımlar listesi, kanıt bağlantıları, karar sahibi.
Her varsayım için 'bu doğru olmazsa ne değişir' notu.
Kayıt saklanır ve sonradan geri çağrılabilir.
Tam motor (seçenek üretimi, kıyas matrisi, takip) Faz 6B'de.
## BİTTİ SAYILIR
Demo sonunda imzalanabilir bir karar kaydı üretiliyor.
Kararın dayandığı varsayımlar açıkça listeleniyor.
6.12LLMP0Departman podları çerçevesi: üretim, finans, satış/pazarlama, İK, satınalma, kalite, IT için ayrı
metrik seti + anomali kuralı + öneri şablonu + rapor formatı + sorumluluk sınırı; her podun kendi sağlık skoru
6.13DATAP0Nedensellik grafı (DAG): korelasyon değil neden-sonuç zinciri. 'Makine duruşu → teslimat
gecikmesi → OEE düşüşü' ilişkileri yönlü kenarlarla tanımlanır; tüm podlar bu merkeze bağlanır
6.14LLMP1Gelişim yol haritası üreteci: 'önümüzdeki çeyrek verimliliği %12 artırmak için 4 adım' — her
adım metriğe, sahibe ve beklenen etkiye bağlı
6.15DATAP1Açıklanabilirlik katmanı: tahmin ve risk skorlarının altına matematiksel katkı dağılımı basılır
('churn %85 — %42 sipariş sıklığı, %28 ödeme gecikmesi'). İçgörü kartının 'neden' şeridini sayısallaştırır
## D48D49
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19D53Ç15
## 1.
## 2.
## 3.
## 4.
## •
## •
## R39R40R41R42R43R44R45R47
## R61BE15
## R4R5
## Ç6Ç13
## F11
✅ KABUL TESTLERİ / USE-CASE'LER 28 senaryo · TEMEL: 16 · REGRESYON: 3 · SINIR: 7 · GÜVENLİK: 2
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-6.1TEMELYönetici karne kartını açar6 kritik metrik + iyi giden/kötü giden/izlenecek yorumu 5
saniyede yüklenir.
UC-6.2TEMELStok kritik seviyeye düşerÖneri somut gelir: 'X ürününde 2 haftalık stok kaldı, sipariş
açın' (genel 'stok artır' değil).
UC-6.3REGRESYONHerhangi bir tahmin istenirSonuç HER ZAMAN aralıklı gelir ('1,2M–1,4M'); tek kesin sayı
verilmez.
UC-6.4SINIR8 aylık geçmişi olan veride tahmin
istenir
Sistem tahmin üretmez; 'yetersiz geçmiş' der.
UC-6.5REGRESYONAynı what-if girdisi iki kez çalıştırılırAynı sonuç çıkar (deterministik); hesaplama zinciri kullanıcıya
gösterilebilir.
DİMA · 0→100 Görev Takip Dosyası44 / 126

IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-6.6TEMEL30 mesajlık bir oturum sonunda
'CEO Günlüğü' istenir
Tüm bulgular tematik gruplanmış tek raporda toplanır; her sayı
kaynağına gider.
UC-6.7TEMELKurul için karar memosu istenirDurum/seçenekler/öneri/riskler yapısında, kaynak bağlantılı,
düzenlenmeden sunulabilir kalitede gelir.
UC-6.8TEMELSWOT analizi istenirHer madde bir sayıya bağlıdır ve tıklanınca kanıta gider; genel
ifadeler yoktur.
UC-6.9TEMELTedarikçi skor kartı çalıştırılırAğırlıklar değiştirilince sıralama doğru şekilde değişir; her
kriterin katkısı görünür.
UC-6.10TEMELKohort analizi istenirMatris elle doğrulanabilir şekilde doğru hesaplanır; ısı
haritasında örüntü okunur.
UC-6.11TEMELKarbon-başabaş OEE analizi
çalıştırılır
Makine bazında yatırım önceliği listesi çıkar; hesap elle
doğrulanabilir.
UC-6.12TEMELBir sevkiyat için emisyon dökümü
istenir
Kullanılan emisyon faktörleri raporda görünür (gizli sabit yok).
UC-6.13TEMELDemo sonunda karar kaydı üretilirVarsayımlar, kanıt bağlantıları ve karar sahibi alanları dolu
olarak gelir.
UC-6.14SINIRAynı SWOT iki kez üretilirMaddeler ve dayandıkları sayılar tutarlıdır; her seferinde farklı
'yorum' üretilmez.
UC-6.15REGRESYONSWOT maddesine tıklanırKanıta gider; dayanaksız genel ifade bulunmaz.
UC-6.16SINIRMevsimsellik içeren veride tahmin
istenir
Mevsimsellik dikkate alınır; düz trend uzatması yapılmaz.
UC-6.17SINIRWhat-if zincirinde tanımsız bir
değişken kullanılır
Sistem uydurmaz; zincirin tanımlanması gerektiğini söyler.
UC-6.18TEMELAynı skor kartı iki farklı dönemde
çalıştırılır
Sıralama değişimi ve sebebi gösterilir.
UC-6.19SINIRKohort analizinde eksik dönem
vardır
Boş hücre uydurulmaz; 'veri yok' olarak işaretlenir.
UC-6.20GÜVENLİKKarar memosu dışa aktarılırİçindeki kişisel veriler maskeleme kurallarına tabidir.
UC-6.21TEMELÜretim ve finans podları aynı anda
çalışır (6.12)
Her pod kendi metrik seti ve anomali kuralıyla çalışır; çıktı
formatları tutarlıdır.
UC-6.22GÜVENLİKBir pod kendi sorumluluk sınırının
dışına çıkmaya çalışır
Engellenir; podun kapsamı tanımlıdır ve aşılamaz.
UC-6.23TEMELPod sağlık skorları görüntülenirHer departmanın karnesi ve trendi ayrı ayrı okunabilir.
UC-6.24TEMEL'Teslimat neden gecikti' sorulur
## (6.13)
Nedensellik grafındaki yönlü zincir izlenir: makine duruşu →
üretim gecikmesi → teslimat. Korelasyon değil neden verilir.
UC-6.25SINIRNedensel graf eksik veya varsayımı
zayıftır
Sistem kesin nedensellik iddia etmez; varsayımlarını açıkça
listeler ve güveni düşürür.
UC-6.26TEMELGelişim yol haritası istenir (6.14)Her adım bir metriğe, sahibe ve beklenen etkiye bağlı olarak
üretilir; genel tavsiye çıkmaz.
UC-6.27TEMELBir risk skoru üretilir (6.15)Skorun altında matematiksel katkı dağılımı gösterilir ('%42
sipariş sıklığı, %28 ödeme gecikmesi').
UC-6.28SINIRKatkı hesaplanamayacak kadar az
veri vardır
Sistem uydurma katkı üretmez; 'açıklanabilir katkı için veri
yetersiz' der.
DİMA · 0→100 Görev Takip Dosyası45 / 126

KARAR MOTORU — Karar Alma Merkezi
Ürünün ağırlık merkezi: grafik/pano değil KARAR. Dima kararı vermez — çerçeveler, ihtimalleri üretir, kıyaslar, kanıtlar, kaydeder
ve varsayımlarını izler. İmza daima insanda. (Demo sürümü 6.11'dir; bu faz tam motordur ve demodan sonra ilk büyük
atılımdır.)
6B.1LLMP0Çerçeveleme: ne kararı, amaç, kısıtlar, süre ve GERİ DÖNDÜRÜLEBİLİR Mİ → karar tipine göre
derinlik kademesi (küçük karara 9 adım işletme)
## AMAÇ
Her karara aynı derinlikte yaklaşmamak; önce kararın ne tür bir karar olduğunu anlamak.
## NASIL
Kullanıcıdan veya bağlamdan çıkar: karar konusu, amaç, kısıtlar (bütçe/süre/kapasite), son tarih.
KRİTİK SORU: geri döndürülebilir mi? (Tek yönlü kapı mı, iki yönlü kapı mı?)
Derinlik kademesi: geri dönülebilir + düşük etki → hızlı mod (3 adım). Geri dönülemez + yüksek etki → tam mod (9
adım).
Çerçeve kullanıcıya gösterilir ve onaylatılır (yanlış soruyu doğru cevaplamamak için).
## BİTTİ SAYILIR
Küçük kararlarda sistem 9 adımlık süreci dayatmıyor.
Karar çerçevesi kullanıcı tarafından düzeltilebiliyor.
6B.2LLMP0Seçenek üretimi: kullanıcının aklına gelmeyenler dahil ihtimaller + her zaman 'hiçbir şey
yapmama' temel senaryosu
## AMAÇ
Kullanıcının aklına gelmeyen seçenekleri de masaya koymak.
## NASIL
Kullanıcının söylediği seçenekleri al; üzerine sistem 2-3 alternatif üretsin (benzer geçmiş kararlar, sektör örüntüleri).
HER ZAMAN 'hiçbir şey yapmama' temel senaryosunu ekle (çoğu karar buna karşı ölçülmelidir).
Seçenekleri birbirini dışlayan ve karşılaştırılabilir hale getir.
Her seçeneğe kısa tanım ve ön koşullar yaz.
## BİTTİ SAYILIR
Her karar analizinde en az 3 seçenek + temel senaryo var.
Seçenekler birbiriyle kıyaslanabilir formatta.
6B.3LLMP0Kriter seti ve ağırlıklandırma (maliyet / risk / nakit / kapasite / termin / karbon)
## AMAÇ
Kararın neye göre verileceğini kararın kendisinden önce belirlemek (sonradan gerekçe uydurmayı engeller).
## NASIL
Standart kriter havuzu: maliyet, gelir etkisi, risk, nakit akışı, kapasite, termin, kalite, karbon, itibar.
Kullanıcı ilgili olanları seçer ve ağırlık verir (toplam 100).
Ağırlıklar kaydedilir; benzer kararlarda tekrar önerilir.
Ağırlık seçimi karar kaydına yazılır (sonradan değiştirilirse görünür).
## BİTTİ SAYILIR
Kriterler ve ağırlıklar seçenekler değerlendirilmeden ÖNCE belirleniyor.
Ağırlık değişimi sonucu nasıl etkilediği gösterilebiliyor.
## FAZ 6B
## →93%
## BE19Ç15
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası46 / 126

6B.4DATAP0Kanıt toplama: her seçenek × kriter hücresi metrik/cube'dan doldurulur; her hücre VERİ |
VARSAYIM | BİLİNMİYOR olarak etiketlenir
## AMAÇ
Her seçenek-kriter hücresini veriyle doldurmak ve neyin bilinmediğini itiraf etmek.
## NASIL
Her hücre için önce metrik/cube'dan veri çekmeyi dene.
Hücreyi ÜÇ ETİKETTEN biriyle işaretle: VERİ (kaynağı var), VARSAYIM (kullanıcı/sistem tahmini, gerekçesi yazılı),
BİLİNMİYOR (veri yok).
Varsayım hücrelerinde kaynağı ve kimin varsaydığını sakla.
BİLİNMİYOR hücreleri gizlenmez, açıkça gösterilir (en önemli dürüstlük kuralı).
## BİTTİ SAYILIR
Matriste hangi bilginin veri hangisinin varsayım olduğu tek bakışta görülüyor.
Bilinmeyen alanlar boş bırakılmıyor, 'bilinmiyor' olarak işaretleniyor.
6B.5UIP0Kıyas matrisi ekranı: her sayı tıklanınca provenance'a iner (kanıt zinciri)
## AMAÇ
Kıyaslamayı görsel ve denetlenebilir hale getirmek.
## NASIL
Matris: satır = seçenek, sütun = kriter; hücrede değer + etiket rengi (veri/varsayım/bilinmiyor).
Ağırlıklı toplam skor sütunu; ama skor tek başına karar vermez, gerekçe gösterilir.
Her hücreye tıklanınca kanıt paneli açılır (hangi sorgu, hangi kaynak).
Ağırlıkları değiştirince skorlar canlı güncellensin.
## BİTTİ SAYILIR
Matristeki her sayının kaynağına inilebiliyor.
Ağırlık değişimi sıralamayı anında değiştiriyor.
6B.6LLMP0Tavsiye + RET GEREKÇESİ ('şunu seçme ve neden') + tersine soru: 'reddedilen seçeneğin
kazanması için neyin doğru olması gerekirdi?'
## AMAÇ
Sadece 'şunu seç' demek yetmez; neden diğerlerinin seçilmediği de yazılmalı.
## NASIL
Tavsiye + gerekçe (hangi kriterlerde öne çıktı).
HER reddedilen seçenek için ret gerekçesi yaz.
TERSİNE SORU (en değerli kısım): 'Reddedilen X seçeneğinin kazanması için neyin doğru olması gerekirdi?' → kırılma
noktasını hesapla.
Bu soru kararı sezgiden çıkarır ve varsayımları görünür kılar.
## BİTTİ SAYILIR
Her karar çıktısında ret gerekçeleri var.
Tersine soru somut bir eşik değeri veriyor ('B seçeneği ancak talep %25 artarsa kazanır').
6B.7LLMP0Duyarlılık ve eşik analizi: kararı ne bozar — 'kur X'i geçerse B seçeneği öne geçer'
## AMAÇ
Kararın hangi koşullarda yanlışa döneceğini önceden bilmek.
## NASIL
Kritik değişkenleri belirle (kur, hammadde fiyatı, talep, kapasite).
Her biri için eşik hesapla: hangi değerde sıralama değişiyor?
Duyarlılık tablosu ve 'kırılma noktaları' listesi üret.
En kırılgan varsayımı öne çıkar ('bu karar en çok kur varsayımına duyarlı').
## BİTTİ SAYILIR
Kararın en kırılgan varsayımı açıkça belirtiliyor.
Eşik değerleri sayısal olarak veriliyor.
## BE19BE15
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19BE3UX1
## Ç15
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19
## Y4
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası47 / 126

6B.8GOVP0Karar Kaydı (tam): değişmez + imzalı; varsayım defteri, sahip, gözden geçirme tarihi, kanıt
bağlantıları
## AMAÇ
Kararı zamanla kaybolmayan, denetlenebilir bir kayda dönüştürmek.
## NASIL
Karar Kaydı alanları: id, başlık, tarih, sahip, katılanlar, çerçeve, seçenekler, kriterler+ağırlıklar, matris, tavsiye, verilen
karar, ret gerekçeleri, varsayım defteri, kanıt bağlantıları, MDL commit, gözden geçirme tarihi.
Kayıt DEĞİŞMEZ (immutable): değişiklik yeni sürüm oluşturur, eskisi durur.
Elektronik imza/onay akışı: karar sahibi onaylar, kayıt kilitlenir.
Aranabilir arşiv: 'geçen yıl tedarikçi kararını neye göre vermiştik?'
## BİTTİ SAYILIR
Kayıt oluşturulduktan sonra değiştirilemiyor, yalnız yeni sürüm ekleniyor.
Geçmiş kararlar aranabiliyor ve gerekçeleriyle okunabiliyor.
6B.9LLMP1Karar takibi (kimsede yok): karar = son kullanma tarihli hipotez. Varsayımlar izlenir, gerçeklik
sapınca uyarı: 'bu kararı hammadde fiyatı sabit varsayımıyla verdiniz, varsayım bozuldu'
## AMAÇ
Kararı bir an değil, izlenmesi gereken bir hipotez olarak ele almak — rakiplerde olmayan yetenek.
## NASIL
Karar Kaydı'ndaki her varsayımı izlenebilir metriğe bağla ('hammadde fiyatı sabit' → hammadde_fiyat metriği).
Pulse motoru (8.10) bu varsayımları periyodik kontrol eder.
Sapma eşiği aşılırsa karar sahibine uyarı: 'Bu kararı X varsayımıyla verdiniz; varsayım bozuldu, kararı gözden geçirin.'
Gözden geçirme tarihi gelince otomatik hatırlatma.
Kararın sonucu da kaydedilsin (gerçekleşen etki) — öğrenme için.
## BİTTİ SAYILIR
Varsayımı bozulan bir karar için gerçekten uyarı üretiliyor.
Kararların gerçekleşen sonuçları geriye dönük görülebiliyor.
6B.10UIP0Karar Rozeti: 'bu kararın %60'ı veriye, %30'u varsayıma, %10'u bilinmeyene dayanıyor' —
sezgisel karara karşı en güçlü silah
## AMAÇ
Kararın ne kadarının veriye dayandığını dürüstçe göstermek.
## NASIL
Matristeki hücre etiketlerinden hesapla: veri / varsayım / bilinmiyor yüzdeleri (ağırlıklı).
Rozet: 'Bu kararın %60'ı veriye, %30'u varsayıma, %10'u bilinmeyene dayanıyor.'
Düşük veri oranında uyarı: 'bu karar büyük ölçüde varsayıma dayanıyor, ek veri toplamayı düşünün'.
Rozet karar kaydının kapağında yer alsın.
## BİTTİ SAYILIR
Rozet gerçek hücre dağılımından hesaplanıyor.
Varsayım ağırlıklı kararlarda kullanıcı uyarılıyor.
6B.11GOVP0Kırmızı çizgi uygulaması: Dima karar VERMEZ (çerçeveler/kanıtlar/önerir/kaydeder). UI dili,
rapor dili ve sözleşme dili bunu yansıtır
## AMAÇ
Ürünün etik ve hukuki sınırını koda ve arayüze işlemek.
## NASIL
Arayüz dili: 'Dima öneriyor', 'Dima'nın değerlendirmesi' — asla 'Dima karar verdi'.
Her karar çıktısının altında sabit ibare: 'Bu bir öneridir; karar ve sorumluluk kullanıcıdadır.'
Karar Kaydı'nda 'karar veren' alanı zorunlu ve bir insan olmalı (boş bırakılamaz).
Sözleşme ve pazarlama dili de aynı çizgiyi korusun.
Otomatik uygulama YOK: hiçbir karar sistem tarafından yürütülmez.
## BİTTİ SAYILIR
Hiçbir ekranda sistemin karar verdiği izlenimi yok.
Karar kaydı bir insan onayı olmadan tamamlanamıyor.
## BE19BE3F6Ç15
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19BE11
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE19F6
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE19F5
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası48 / 126

6B.12LLMP1Karar şablonları: tekrarlayan karar tipleri (yatırım, tedarikçi seçimi, fiyatlama, kapasite)
şablona terfi eder — Terfi Motoru kaynağı
## AMAÇ
Tekrarlayan karar tiplerini şablona dönüştürüp süreci hızlandırmak.
## NASIL
Karar tiplerini tespit et (yatırım, tedarikçi seçimi, fiyatlama, kapasite, işe alım).
Her tip için hazır kriter seti + tipik seçenekler + gerekli veri listesi.
Şablon kullanıldıkça iyileşsin (hangi kriterler gerçekten ayırt edici oldu?).
Şablon üretimi Terfi Motoru'na (8.16) kaynak olsun.
## BİTTİ SAYILIR
Aynı tip ikinci karar belirgin şekilde daha hızlı tamamlanıyor.
Şablonlar kullanım verisiyle güncelleniyor.
6B.13GOVP0Telos/OKR senkronizasyon katmanı: şirketin dönemsel ana hedefi merkeze yazılır; üretilen
her öneri, görev ve analiz 'ana iradeye katkı' skoruyla (Delta-KPI) tartılır. Katkısı olmayan öneri kullanıcıya çıkmaz
6B.14LLMP0Departman hakemi: çatışan alt hedeflerde (satış stok ister, finans nakit ister) alt ajanlar arka
planda yarıştırılır, uzlaşma noktası bulunur; kullanıcıya kavga değil tek optimize öneri sunulur
6B.15DATAP0Karar–sonuç kütüphanesi: her kararın gerçekleşen sonucu geriye dönük eşleştirilir ve
arşivlenir. ÖĞRENİLMİŞ SEZGİNİN TEK YAKITI BUDUR — ilk günden toplanmazsa sonra üretilemez
6B.16GOVP1Anayasal kalkan: politika ve sözleşme kuralları biçimsel kısıtlara çevrilir, teorem
kanıtlayıcıyla (Z3 sınıfı) çelişki taranır. Talimat ile yükümlülük çakışırsa uyarı + ikinci C-level onayı tetiklenir. KAPSAM
DAR: yalnız sayısal/mantıksal kısıtlar
## BE19BE17
## 1.
## 2.
## 3.
## 4.
## •
## •
## R62BE19
## R46R64BE19
## R87BE19
## BE20
## R64F25BE19
✅ KABUL TESTLERİ / USE-CASE'LER 26 senaryo · TEMEL: 17 · REGRESYON: 3 · GÜVENLİK: 3 · SINIR: 3
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-6B.1TEMELKüçük ve geri dönülebilir bir karar
getirilir
Sistem 9 adımlık süreci dayatmaz; hızlı modda 3 adımda
sonuçlandırır.
UC-6B.2TEMELGeri dönülemez büyük bir yatırım
kararı getirilir
Tam mod devreye girer; derinlik kademesi kullanıcıya
bildirilir.
UC-6B.3REGRESYONHerhangi bir karar analizi yapılırEn az 3 seçenek + 'hiçbir şey yapmama' temel senaryosu
bulunur.
UC-6B.4TEMELKriterler ve ağırlıklar belirlenirBu adım seçenekler değerlendirilmeden ÖNCE tamamlanır
(sonradan gerekçe uydurma engellenir).
UC-6B.5TEMELKıyas matrisi görüntülenirHer hücre VERİ / VARSAYIM / BİLİNMİYOR olarak etiketlidir;
bilinmeyen alanlar gizlenmez.
UC-6B.6TEMELMatriste bir hücreye tıklanırKanıt paneli açılır: hangi sorgu, hangi kaynak, hangi tarih.
UC-6B.7TEMELAğırlıklar değiştirilirSkorlar ve sıralama anında güncellenir.
UC-6B.8REGRESYONKarar çıktısı incelenirTavsiye kadar RET GEREKÇESİ de vardır; her reddedilen
seçenek için sebep yazılıdır.
UC-6B.9TEMEL'Reddedilen B seçeneği ne zaman
kazanır?' sorulur
Somut eşik verilir: 'talep %25 artarsa B öne geçer'.
UC-6B.10TEMELDuyarlılık analizi çalıştırılırEn kırılgan varsayım açıkça belirtilir; eşik değerleri sayısaldır.
UC-6B.11GÜVENLİKOluşturulmuş bir Karar Kaydı
değiştirilmeye çalışılır
Değiştirilemez; yalnız yeni sürüm oluşturulur, eskisi durur.
UC-6B.12TEMELGeçmiş bir karar aranırGerekçeleri, varsayımları ve kanıtlarıyla birlikte bulunur.
DİMA · 0→100 Görev Takip Dosyası49 / 126

Trust & Governance (Tam Sürüm)
UpcyBrain'in ayırt edici güven mimarisini yeni backend'de yeniden yaz — regüle satışın kilidi. (Demo-seviyesi sürümleri Faz
2/4'te; bu faz tam sürüm.)
7.1GOVP0Provenance/QueryContract motoru (SQL + MDL commit + parametre + sonuç hash + zaman)
+ yeniden koşum
## AMAÇ
Her cevabı bir denetçinin doğrulayabileceği kanıta dönüştürmek — kurumsal satışın kilidi.
## NASIL
QueryContract nesnesi: contractId, tenant, kullanıcı, soru, çözümlenmiş parametreler, çalışan SQL, kullanılan metrik,
MDL commit hash, veri kaynağı, çalışma zamanı, sonuç hash (SHA-256), güven skoru.
Her cevap üretiminde otomatik yazılır (istisna yok).
'Yeniden çalıştır' ucu: aynı contract'ı tekrar koşar, sonuç hash'ini karşılaştırır, farkı raporlar.
Contract'lar değişmez ve saklama süresi boyunca silinemez.
Arayüzde her sayıdan contract'a tıklanarak gidilir.
## BİTTİ SAYILIR
Bir denetçi ekrandaki sayıyı contract üzerinden bağımsız doğrulayabiliyor.
Aynı contract yeniden koşulduğunda hash tutuyor (veri değişmediyse).
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-6B.13TEMELKararın dayandığı varsayım bozulur (ör.
hammadde fiyatı %30 artar)
Karar sahibine uyarı gider: 'bu kararı X varsayımıyla verdiniz,
varsayım bozuldu'.
UC-6B.14TEMELGözden geçirme tarihi gelirOtomatik hatırlatma gönderilir.
UC-6B.15TEMELKarar rozeti görüntülenir'%60 veri, %30 varsayım, %10 bilinmeyen' dağılımı gerçek
hücre etiketlerinden hesaplanır.
UC-6B.16SINIRAğırlıklı olarak varsayıma dayanan bir
karar üretilir
Kullanıcı uyarılır: 'bu karar büyük ölçüde varsayıma
dayanıyor'.
UC-6B.17GÜVENLİKTüm karar ekranları ve çıktıları
denetlenir
Hiçbirinde sistemin karar verdiği izlenimi yok; 'karar veren'
alanı bir insan olmadan kayıt tamamlanmıyor.
UC-6B.18TEMELAynı tipte ikinci bir karar getirilirŞablon sayesinde belirgin şekilde daha hızlı tamamlanır.
UC-6B.19TEMELBir öneri üretilir (6B.13)Ana hedefe katkısı (Delta-KPI) hesaplanır ve gösterilir.
UC-6B.20SINIRAna hedefe katkısı olmayan bir öneri
oluşur
Kullanıcıya çıkmaz; arka planda elenir ve gerekçesi loglanır.
UC-6B.21TEMELSatış vade uzatmak, finans nakit
korumak ister (6B.14)
Hakem çalışır; kullanıcıya iki karşıt görüş değil tek optimize
uzlaşma önerisi sunulur.
UC-6B.22TEMELÇatışma nicel kısıtlardan doğar (nakit,
kapasite)
Kısıt optimizasyonu kullanılır; sonuç deterministik ve
tekrarlanabilirdir.
UC-6B.23TEMEL90 gün önceki bir kararın sonucu
gerçekleşir (6B.15)
Karar–sonuç eşleşmesi arşive yazılır ve öğrenme halkasına
girdi olur.
UC-6B.24REGRESYONKarar–sonuç kütüphanesi denetlenirHer kararın varsayımı, gerçekleşen sonucu ve sapması
izlenebilir.
UC-6B.25GÜVENLİKPatron 'tüm ödemeleri durdur' der,
sözleşmede cezai şart vardır (6B.16)
Anayasal kalkan devreye girer: talimat kaydedilir ama cezai
yükümlülük tutarıyla uyarı verilir ve ikinci onay istenir.
UC-6B.26SINIRPolitika kuralları arasında mantıksal
çelişki vardır
Teklif kullanıcıya çıkmadan önce çelişki yakalanır ve hangi iki
kuralın çakıştığı gösterilir.
## FAZ 7
## →96%
## F6BE3Ç10
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası50 / 126

7.2GOVP0Confidence Calculator (sistem-hesaplı, LLM değil) + trust badge tam
## AMAÇ
Güven skorunu tahmin değil hesap haline getirmek.
## NASIL
Girdi faktörleri: yol (cube/cache/LLM), veri tazeliği, metrik tanımlı mı, filtre kapsamı, satır sayısı, doğrulama sonuçları.
Formül kodda ve dokümante; LLM'e asla 'kendine puan ver' denmez.
Skor + gerekçe listesi birlikte döner ('altın yol +40, veri 2 gün eski -5').
Rozet eşikleri yapılandırılabilir.
## BİTTİ SAYILIR
Aynı koşullarda skor her zaman aynı (deterministik).
Skorun gerekçesi kullanıcıya açıklanabiliyor.
7.3GOVP0Eligibility Guard (susma) + red açıklaması + belirsizlik tipolojisi (terminolojik/data-void/
subjektif/karar)
## AMAÇ
Sistemin ne zaman susacağını bilmesi — tam sürüm.
## NASIL
7 kontrol: DB erişimi, veri yeterliliği, intent netliği, güven eşiği, belirsizlik, yasak işlem, LLM gerekliliği.
Başarısız kontrol → RejectionExplanation üret: teknik sebep + iş dilinde açıklama + çözüm önerisi + 'şunu dene'
butonları.
Belirsizlik tipolojisi: TERMİNOLOJİK (net mi brüt mü), VERİ_YOK, ÖZNEL ('en iyi hangisi'), KARAR_GEREKLİ.
Her red loglanır (hangi veri eksik analizi için).
Red, hata değildir — kullanıcıya güven veren bir davranıştır; dil buna göre olsun.
## BİTTİ SAYILIR
Reddedilen her sorguda kullanıcı ne yapması gerektiğini öğreniyor.
Red sebepleri raporlanabiliyor (en sık hangi veri eksik?).
7.4GOVP0DCM (AI_MODE=off) tam: air-gap, menü/wizard, her zaman altın rozet
## AMAÇ
Yapay zekâsız çalışma modunun kurumsal seviyeye çıkarılması.
## NASIL
AI_MODE=off tam izolasyon: LLM istemcisi hiç yüklenmez (kod seviyesinde garanti).
Menü/sihirbaz akışı: alan seç → analiz tipi seç → dönem seç → çalıştır.
İnternet erişimi olmadan çalışabilme (air-gapped kurulum dokümanı).
Tüm sonuçlar altın rozet; contract üretimi devam eder.
Kurumsal doğrulama için 'LLM çağrısı yapılmadı' raporu üretilebilsin.
## BİTTİ SAYILIR
Ağ tamamen kapalıyken sistem çalışıyor.
Denetime sunulabilecek 'sıfır LLM çağrısı' kanıtı üretiliyor.
7.5GOVP0RLS runtime (session-property enjeksiyonu, motorda) + CLS (Redactor + görünmez kolon)
## AMAÇ
Kullanıcının yalnız yetkili olduğu veriyi görmesi — motor seviyesinde.
## NASIL
JWT'den oturum özellikleri türet (tenantId, şube, departman, rol).
Bu özellikler sorguya PARAMETRE olarak enjekte edilir — asla string birleştirme (SQL enjeksiyonu riski).
Uygulama motor seviyesinde: LLM yanlış SQL üretse bile filtre zorunlu uygulanır.
Kolon seviyesi (CLS): MDL'de tanımsız kolon zaten görünmez + Redactor maskeler.
Test: farklı rollerle aynı sorgu farklı sonuç vermeli.
## BİTTİ SAYILIR
Şube müdürü başka şubenin verisini hiçbir yoldan göremiyor (test edildi).
SQL enjeksiyon denemesi başarısız oluyor.
## F6Ç12
## 1.
## 2.
## 3.
## 4.
## •
## •
## F5S30Ç11
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## F9Ç17
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## F7F8Ç18
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası51 / 126

7.6GOVP0Policy-as-code (YAML, tenant override, hazır KVKK paketi) + Decision/Audit log gezgini
## AMAÇ
İş kurallarını koda gömmeden, yönetilebilir hale getirmek.
## NASIL
Kurallar YAML dosyalarında: koşul + aksiyon (reddet / uyar / maskele / dönüştür / logla).
Varsayılan paket: yıkıcı işlem engelleme, LIMIT zorunluluğu, büyük tarama uyarısı, hassas tablo logu, KVKK
maskeleme.
Tenant bazlı override; hot-reload (yeniden başlatmadan devreye girsin).
Denetim gezgini: kim, ne zaman, hangi sorguyu çalıştırdı, hangi kural tetiklendi — filtrelenebilir arayüz.
## BİTTİ SAYILIR
Yeni kural dosya değişikliğiyle 1 dakikada devreye giriyor.
Denetim kayıtları tarih/kullanıcı/kural bazında aranabiliyor.
7.7GOVP1Output Redactor tam (TCKN/e-posta/kart/API-key, rol-duyarlı) son-çıkış filtresi
## AMAÇ
Kişisel verilerin son çıkış noktasında maskelenmesi.
## NASIL
Desen kütüphanesi: TCKN (11 hane + algoritma kontrolü), e-posta, telefon, IBAN, kredi kartı (Luhn), API anahtarı.
Rol bazlı politika: hangi rol neyi maskesiz görebilir.
Maskeleme cevabın en son adımında (tüm yolların ortak çıkışında) uygulanır.
Yanlış pozitifleri azaltmak için bağlam kontrolü (11 haneli her sayı TCKN değildir).
Maskesiz erişimler audit'e yazılır.
## BİTTİ SAYILIR
Metin, tablo, grafik etiketi ve dışa aktarımların hepsinde maskeleme çalışıyor.
Yanlış maskeleme oranı kabul edilebilir düzeyde (test setiyle ölçüldü).
7.8WRENP1data-flow inspector bağlama (governed execution)
## AMAÇ
Wren motorunun veri akışı denetim aracını devreye almak.
## NASIL
data-flow inspector: bir sorgunun hangi tablolardan hangi kolonları okuduğunu çıkarır.
Bu bilgiyi contract'a ekle (hangi veriye dokunuldu).
Hassas tablo/kolon dokunuşlarında otomatik uyarı.
## BİTTİ SAYILIR
Her contract'ta dokunulan tablo/kolon listesi var.
Hassas veriye erişim otomatik işaretleniyor.
7.9GOVP1Eskalasyon matrisi ve yetki sirküleri: hangi durum, hangi eşikte, ne kadar sürede kime
yükselir; imza/onay limitleri politika olarak tanımlanır ve aşım otomatik kilitlenir
7.10GOVP0Kademeli zarafetle düşüş: (1) tam bilişsel mod → (2) internet kesik: tam yerel model → (3)
LLM yok: DCM %100 deterministik. Her seviye test edilebilir ve kullanıcıya görünür olmalı; sistem asla tamamen
durmaz
## F25
## 1.
## 2.
## 3.
## 4.
## •
## •
## F8S15
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
wINSPECTÇ10
## 1.
## 2.
## 3.
## •
## •
## R38F25
## Ç17F9BE1
✅ KABUL TESTLERİ / USE-CASE'LER 20 senaryo · TEMEL: 5 · REGRESYON: 3 · SINIR: 4 · GÜVENLİK: 8
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-7.1TEMELBir denetçi ekrandaki sayıyı sorgularQueryContract üzerinden bağımsız doğrulayabilir: SQL, MDL
sürümü, parametreler, zaman.
UC-7.2REGRESYONAynı contract yeniden çalıştırılırVeri değişmediyse sonuç hash'i birebir tutar.
UC-7.3SINIRVeri değiştikten sonra contract
yeniden çalıştırılır
Fark raporlanır; sessizce farklı sonuç dönmez.
UC-7.4REGRESYONAynı koşullarda güven skoru iki kez
hesaplanır
Aynı skor çıkar (deterministik); gerekçe listesi gösterilebilir.
DİMA · 0→100 Görev Takip Dosyası52 / 126

## Ölçek, Öğrenme, Sektör Paketleri
Çok-kiracı olgunluğu, kullandıkça ucuzlama, satılabilir dikeyler. Backend'e özel motorların çoğu burada olgunlaşır.
8.1ENGP0Tam multi-tenancy + RBAC/Groups + dashboard/thread/spreadsheet izinleri
## AMAÇ
Çok müşterili yapıya tam geçiş ve yetki yönetimi.
## NASIL
Tüm sorgulara tenant filtresi zorunlu (ORM middleware ile otomatik, geliştirici unutsa bile).
Roller: sahip, yönetici, analist, izleyici + özel roller.
Gruplar ve kaynak bazlı izinler: pano, thread, rapor, veri kaynağı.
Kiracı izolasyon testi: A tenant'ının verisi B'ye hiçbir yolla sızmamalı (otomatik test).
## BİTTİ SAYILIR
Otomatik izolasyon testi geçiyor.
Yeni rol eklemek kod değişikliği gerektirmiyor.
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-7.5GÜVENLİKLLM'den 'kendine güven puanı ver'
istenir
Böyle bir mekanizma yoktur; skor yalnız sistem tarafından
hesaplanır.
UC-7.6SINIRCevaplanamayacak bir soru sorulur7 kontrolden hangisinin başarısız olduğu, iş dilinde açıklama
ve 'şunu dene' önerisiyle bildirilir.
UC-7.7TEMELRed kayıtları raporlanırEn sık hangi verinin eksik olduğu analiz edilebilir.
UC-7.8GÜVENLİKAğ tamamen kapatılır ve AI_MODE=off
yapılır
Sistem çalışmaya devam eder; 'sıfır LLM çağrısı' raporu
üretilebilir.
UC-7.9GÜVENLİKŞube müdürü başka şubenin verisini
istemeye çalışır
Hiçbir yoldan göremez; filtre motor seviyesinde uygulanır.
UC-7.10GÜVENLİKLLM kasten yanlış (filtresiz) SQL üretirRLS parametre enjeksiyonu yine de uygulanır; yetkisiz satır
dönmez.
UC-7.11GÜVENLİKSQL enjeksiyon denemesi yapılırString birleştirme olmadığı için başarısız olur.
UC-7.12TEMELYeni bir politika kuralı YAML'a eklenir1 dakika içinde yeniden başlatmadan devreye girer.
UC-7.13TEMELDenetim gezgini açılırKim, ne zaman, hangi sorguyu çalıştırdı ve hangi kural
tetiklendi filtrelenebilir.
UC-7.14GÜVENLİKMaskeleme testi: metin, tablo, grafik
etiketi ve dışa aktarım
Hepsinde maskeleme çalışır; hiçbir yol atlanmaz.
UC-7.15SINIR11 haneli bir sipariş numarası
sorgulanır
TCKN sanılıp yanlışlıkla maskelenmez (bağlam kontrolü
çalışır).
UC-7.16TEMELOnay limitini aşan bir işlem denenir
## (7.9)
Otomatik kilitlenir ve eskalasyon matrisine göre bir üst
yetkiliye yükselir.
UC-7.17SINIREskalasyon süresi dolar, kimse yanıt
vermez
Bir üst kademeye otomatik yükselir; işlem sahipsiz kalmaz.
UC-7.18GÜVENLİKİnternet bağlantısı kesilir (7.10)Sistem Seviye 2'ye (tam yerel model) düşer ve çalışmaya
devam eder; kullanıcı hangi seviyede olduğunu görür.
UC-7.19GÜVENLİKLLM sağlayıcısı tamamen erişilemez
olur
Seviye 3'e (DCM) düşülür: menü ve sihirbazla, %100
deterministik, sıfır LLM çağrısıyla çalışır.
UC-7.20REGRESYONSeviye düşüşü ve geri dönüşü test
edilir
Her geçiş loglanır; veri kaybı ve tutarsız cevap oluşmaz.
## FAZ 8
## →98%
## S91Ç18
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası53 / 126

8.2LLMP0Çift cache (semantic + deterministic) + CacheRouter (altın yol oranı↑, COGS↓)
## AMAÇ
İki cache tipini birlikte yönetmek ve maliyeti düşürmek.
## NASIL
Deterministik cache: hash tabanlı, birebir aynı sorgu (8.2a anahtarı).
Semantik cache: soru embedding'i, %90+ benzerlikte isabet.
CacheRouter: AI açıkken semantik+deterministik, AI kapalıyken sadece deterministik.
Semantik isabet kullanıcıya belirtilsin ('benzer bir soruya verilen cevap').
İsabet oranı ve tasarruf edilen maliyet ölçülsün.
## BİTTİ SAYILIR
Cache isabet oranı ve tasarruf panelde görülüyor.
Semantik cache yanlış eşleşme yapmıyor (test setiyle doğrulandı).
8.2aENGP0Cache anahtarı tasarımı: ham soru metni DEĞİL, çözümlenmiş cube-query JSON hash'i =
tenant + cube + measure + dimension + zaman aralığı + filtreler + RLS bağlamı + mdl_commit
## AMAÇ
Cache anahtarının doğru bileşenlerden üretilmesi (3.13'ün üretim sürümü).
## NASIL
Anahtar bileşenleri: tenant + metrik/cube + measure + dimension + zaman aralığı + filtreler + RLS bağlamı +
mdl_commit.
Ham metin anahtar olarak KULLANILMAZ.
Anahtar üretimi tek bir fonksiyonda toplansın (tutarlılık).
Anahtar çakışma testi yaz.
## BİTTİ SAYILIR
Farklı yetkideki kullanıcılar aynı cache kaydını paylaşmıyor.
Aynı sorgu farklı kelimelerle sorulduğunda tek kayıt kullanılıyor.
8.2bENGP0Cache geçersizleme: her kayda tablo/metrik bağımlılığı bağlanır; veri yüklenince veya MDL
commit değişince ilgili cache otomatik düşer (bayat veri = güven ölümü)
## AMAÇ
Cache'in bayat veri sunmasını engellemek.
## NASIL
Her kayda bağımlılık: kullanılan tablolar + metrikler.
ETL/veri yükleme bitince ilgili anahtarları toplu sil.
MDL commit değişince o modele bağlı tüm kayıtları sil.
Yedek güvenlik: TTL (24 saat).
Geçersizleme olaylarını logla (neden silindi).
## BİTTİ SAYILIR
Veri güncellemesinden sonra ilk sorgu taze veri getiriyor.
Bayat veri şikayeti sıfır.
8.3LLMP1Intent Learning (öğrenilen kalıp → altın SQL) + Adaptive Defaults
## AMAÇ
Sistemin sık sorulanlardan öğrenip hızlanması.
## NASIL
Sorgu loglarından örüntü çıkar: hangi ifadeler hangi metriğe gidiyor.
Yüksek frekanslı örüntüleri IntentPattern olarak kaydet (bir daha LLM'e gitmesin).
Kullanıcı tercihlerini varsayılana dönüştür (adaptive defaults).
Haftalık iş olarak çalışsın; önerileri insan onayına sunsun.
## BİTTİ SAYILIR
Zaman içinde LLM'siz cevaplanan soru oranı artıyor (ölçülüyor).
Öğrenilen örüntüler yanlış eşleşme yapmıyor.
## F10BE6
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE6F10
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE6F26
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE12BE16
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası54 / 126

8.4GOVP1Drift Detection (metrik/pattern sapması) + uyarı bandı
## AMAÇ
Metrik tanımı değiştiğinde eski raporların sessizce anlam değiştirmesini engellemek.
## NASIL
Günlük iş: metrik tanımlarının değişim zamanlarını, kullanan pano/rapor/örüntüleri karşılaştır.
Sapma bulunursa etkilenenleri listele ve sahiplerine bildir.
Etkilenen panolarda sarı uyarı bandı göster.
'Yeniden doğrula' butonu: eski ve yeni tanımla sonuçları kıyasla.
## BİTTİ SAYILIR
Metrik değişikliğinden sonra etkilenen panolar uyarı gösteriyor.
Kullanıcı farkı görebiliyor.
8.5DATAP0Sektör paketi = dosya seti: UpcySustain (OEE + karbon/su/enerji + DPP + CBAM/CSRD +
izlenebilirlik)
## AMAÇ
Sektöre özel hazır paketleri satılabilir ürün haline getirmek.
## NASIL
Paket = dosya seti: MDL modelleri + cube tanımları + metrikler + kurallar + altın sorgular + rapor şablonları.
İlk paket UpcySustain: OEE, enerji/kg, su/kg, karbon/kg, RFT, DPP alanları, CBAM/CSRD rapor şablonları.
Paket Git deposundan kurulabilsin; müşteri verisine eşleme sihirbazı olsun.
Sürümlenebilir olsun (paket v1.2 → v1.3 güncellemesi).
Kurulum sonrası doğrulama testi (paket metrikleri çalışıyor mu?).
## BİTTİ SAYILIR
Yeni bir tekstil müşterisinde paket 1 saatte kurulup çalışıyor.
Paket güncellemesi müşteri özelleştirmelerini bozmuyor.
8.6ENGP0Kredi/faturalama motoru (işlem-bazlı, başarısız=0, model çarpanı, token ölçüm)
## AMAÇ
Kullanımı ölçüp faturalandırabilmek ve kârlılığı görebilmek.
## NASIL
İşlem sayacı: sohbet 1, rapor 4, agentic 6, artifact 8 kredi; altın yol ve cache 0.
Başarısız işlem kredi yakmaz (güven veren kural).
Model sınıfı çarpanı (ekonomik ×1, denge ×2, premium ×3).
Gerçek token tüketimi ayrıca ölçülsün (kredi ≠ maliyet; ikisini karşılaştır).
Tenant bazlı kârlılık raporu: gelir - gerçek maliyet.
## BİTTİ SAYILIR
Fatura ile gerçek maliyet arasındaki fark izlenebiliyor.
Zarar ettiren müşteri tespit edilebiliyor.
8.7WRENP1Golden eval runner ürünleştir → Evaluation paneli (doğruluk trendi = satış kanıtı)
## AMAÇ
Cevap doğruluğunu sürekli ölçmek — hem kalite hem satış kanıtı.
## NASIL
Her müşteri için altın soru seti (soru + beklenen cevap) oluştur (kurulumda 20-30 soru).
Gecelik koşu: tüm setleri çalıştır, beklenenle karşılaştır, doğruluk yüzdesi üret.
Trend grafiği: doğruluk zaman içinde nasıl değişiyor.
Düşüş olursa hangi sorunun kırıldığını göster ve uyarı gönder.
Bu raporu müşteriye de sun (güven kanıtı).
## BİTTİ SAYILIR
Gecelik koşu otomatik çalışıyor ve rapor üretiyor.
Doğruluk düşüşü 24 saat içinde fark ediliyor.
## F26
## 1.
## 2.
## 3.
## 4.
## •
## •
## Y22Y23Y24Y25Y26
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE10
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## F23
BE13wEVAL
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası55 / 126

8.8ENGP0Kuyruk/worker ölçek + Dinamik bağlantı havuzu (LRU + TTL + Vault)
## AMAÇ
Binlerce müşteriye hizmet verebilecek altyapı.
## NASIL
Worker'ları ayrı ölçekle: LLM işleri (CPU/ağ yoğun) ve DB işleri (I/O yoğun) farklı havuzlarda.
Kuyruk derinliğine göre otomatik ölçekleme kuralı.
Dinamik bağlantı havuzu: LRU cache, maksimum N aktif bağlantı, 10 dk TTL, kapanınca kaynak bırak.
Bağlantı bilgisi her seferinde Vault'tan çekilir, bellekte uzun süre tutulmaz.
## BİTTİ SAYILIR
100 eşzamanlı kullanıcıda sistem yanıt veriyor.
Aktif olmayan müşteri bağlantıları otomatik kapanıyor.
8.9ENGP1Zamanlanmış iş motoru + batch API yönlendirme (%50 indirim)
## AMAÇ
Zamanlanmış işleri güvenilir ve ucuz çalıştırmak.
## NASIL
Merkezi zamanlayıcı: abonelik raporları, Pulse taramaları, hafıza tazeleme, drift kontrolü, golden eval.
Çakışma önleme (aynı iş iki kez çalışmasın) ve hata durumunda tekrar deneme.
Gerçek zamanlı olmayan LLM işlerini batch API'ye yönlendir (%50 maliyet avantajı).
İş durumu paneli: hangi iş ne zaman çalıştı, sürdü, başarılı mı.
## BİTTİ SAYILIR
Zamanlanmış işlerin durumu izlenebiliyor.
Batch'e uygun işler batch'ten geçiyor (maliyet farkı ölçülüyor).
8.10LLMP1Pulse proaktif motor (eşik/anomali → bildirim) — alarm-widget backend
## AMAÇ
Kullanıcı sormadan sistemin haber vermesi — panelden danışmana geçiş.
## NASIL
İzleme kuralları: metrik + eşik + yön + kontrol sıklığı + alıcı + kanal.
Eşik dışında anomali tespiti de (z-skoru) tetikleyici olabilsin.
Bildirim yorgunluğunu önle: aynı uyarı N saat içinde tekrar gönderilmez; önem sırasına göre grupla.
Bildirim içeriği: ne oldu + ne kadar saptı + olası sebep + önerilen aksiyon + bağlantı.
Karar takibi (6B.9) bu motoru kullanır.
## BİTTİ SAYILIR
Eşik aşımında bildirim 15 dakika içinde ulaşıyor.
Kullanıcı gereksiz bildirimden şikayet etmiyor (yorgunluk kontrolü çalışıyor).
8.11GOVP1LlmShadow (LLM çıktısı vs cube deterministik gölge-kıyas)
## AMAÇ
LLM'in ürettiği sayıları sessizce denetlemek.
## NASIL
LLM bir sayı ürettiğinde, mümkünse aynı sonucu cube'dan da hesapla (arka planda, kullanıcı beklemeden).
Sapma varsa: güven skorunu düşür, olayı logla, tekrarlanırsa uyarı üret.
Sapma oranını metrik olarak izle (halüsinasyon göstergesi).
Kullanıcıya gösterme kararı: küçük sapmada sessiz log, büyük sapmada uyarı.
## BİTTİ SAYILIR
Kasıtlı yanlış üretilen test senaryosunda sapma yakalanıyor.
Gölge kontrol kullanıcı deneyimini yavaşlatmıyor.
## BE7BE8
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE9
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE11Y2R2
## R8
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE14
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası56 / 126

8.12ENGP1rate limits (fair-use; altın-yol API bombardımanına karşı)
## AMAÇ
Sistemi kötüye kullanımdan ve maliyet patlamasından korumak.
## NASIL
Kullanıcı ve tenant bazlı istek limiti (dakika/saat).
Altın yol ücretsiz olduğu için API bombardımanına karşı ayrı limit.
Limit aşımında anlaşılır mesaj ve bekleme süresi.
Anormal kullanım desenlerinde uyarı.
## BİTTİ SAYILIR
Limit aşımında sistem çökmüyor, kibarca reddediyor.
Anormal kullanım tespit edilebiliyor.
8.13ENGP0LLM Gözlemevi: her çağrı normalize imzayla loglanır (çözümlenmiş varlıklar, dokunulan tablo/
kolon, zaman aralığı tipi, maliyet, gecikme, sonuç: başarı/hata/kullanıcı düzeltmesi) — PII yazılmadan önce
maskelenir
## AMAÇ
LLM kullanımını ölçmeden iyileştiremezsin — gözlemevi bu yüzden var.
## NASIL
Her LLM çağrısını normalize imzayla logla: çözümlenmiş varlıklar (metrik, boyut, zaman tipi), dokunulan tablo/
kolonlar, prompt boyutu, model, maliyet, gecikme, sonuç (başarı/hata/kullanıcı düzeltmesi).
HAM PROMPT METNİ SAKLANMAZ (PII riski) — sadece imza ve istatistik.
Kullanıcı düzeltmesi en değerli sinyaldir, ayrıca işaretle.
Loglar tenant bazlı ayrılsın ve saklama süresi tanımlı olsun.
## BİTTİ SAYILIR
Bir haftalık log üzerinden en pahalı 10 soru tipi çıkarılabiliyor.
Loglarda kişisel veri bulunmuyor (denetlendi).
8.14LLMP0Semantik kümeleme + terfi skoru: frekans × maliyet × deterministikleştirilebilirlik; LLM'in
yazdığı çalışan SQL çöpe atılmaz, aday metrik/cube tohumu olarak hasat edilir
## AMAÇ
Hangi soruların metriğe dönüştürülmesi gerektiğini veriyle bulmak.
## NASIL
Benzer imzaları kümele (semantik + yapısal benzerlik).
Her küme için terfi skoru = frekans × ortalama maliyet × deterministikleştirilebilirlik.
Deterministikleştirilebilirlik: bu soru cube parametrelerine çevrilebiliyor mu? (kolon/agregasyon örüntüsüne bakarak).
KRİTİK: LLM'in bu küme için yazdığı ÇALIŞAN SQL'i sakla — aday metrik tanımının tohumu olarak kullan.
Kümeleri skora göre sırala.
## BİTTİ SAYILIR
En yüksek skorlu 10 küme haftalık olarak listeleniyor.
Her küme için hazır SQL taslağı bulunuyor.
8.15UIP0Terfi kuyruğu + onay ekranı: 'net_sales tanımla → ayda 340 çağrı, LLM trafiğinin %22'si, şu
kadar maliyet düşer' → insan onayı → bronzdan altın yola terfi
## AMAÇ
İnsan onayıyla bronz cevabı altın yola terfi ettirmek.
## NASIL
Terfi kuyruğu ekranı: küme, örnek sorular, frekans, aylık maliyet, önerilen metrik tanımı, hazır SQL.
Etki tahmini göster: 'bu metriği tanımlarsanız LLM trafiğinin %22'si düşer, aylık şu kadar tasarruf'.
Tek tıkla onay → MetricDefinition + cube oluşur, commit edilir.
Reddedilenler bir daha önerilmesin (veya süre sonra tekrar).
## BİTTİ SAYILIR
Onaylanan metrik sonraki sorgularda gerçekten LLM'siz çalışıyor.
Terfi öncesi/sonrası maliyet farkı ölçülebiliyor.
wRATE
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE16F8
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE16BE17
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE17BE12
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası57 / 126

8.16ENGP1Terfi/Küratörlük Motoru (TEK motor, 4 kaynak): LLM log→cube/metrik · tekrarlayan ajan
adımı→skill · tekrarlayan karar tipi→karar şablonu · kişi hafıza→şirket→sektör paketi. Ortak kümeleme + puanlama +
onay kuyruğu + etki ölçümü
## AMAÇ
Dört ayrı öğrenme mekanizması yerine tek motor yazmak (bakım maliyetini düşürür).
## NASIL
Ortak arayüz: gözlem kaynağı → kümeleme → puanlama → onay kuyruğu → uygulama → etki ölçümü.
Kaynak 1: LLM logları → metrik/cube terfisi.
Kaynak 2: tekrarlayan ajan adımları → skill terfisi.
Kaynak 3: tekrarlayan karar tipleri → karar şablonu terfisi.
Kaynak 4: kişi hafızası → şirket hafızası → sektör paketi terfisi.
Tek onay ekranı, tek etki paneli.
## BİTTİ SAYILIR
Yeni bir terfi kaynağı eklemek mevcut kodu değiştirmeden mümkün.
Tüm terfiler tek ekrandan yönetiliyor.
8.17UIP1'Dima kendini nasıl geliştiriyor' paneli + aylık Dima Verimlilik Raporu (LLM'siz oran, maliyet
düşüşü) — hem ürün hem satış kanıtı
## AMAÇ
Sistemin kendini geliştirdiğini kullanıcıya göstermek — hem ürün hem satış aracı.
## NASIL
Panel: bu ay kaç soru soruldu, %kaçı LLM'siz gitti, kaç metrik terfi etti, maliyet nasıl değişti.
Aylık PDF raporu: 'Dima Verimlilik Raporu' — müşteriye e-postayla gider.
Trend grafikleri: altın yol oranı zaman içinde artmalı.
Rakiplerin üretemeyeceği bir belge olduğunu satışta vurgula.
## BİTTİ SAYILIR
Rapor gerçek verilerden üretiliyor.
Altın yol oranı aylar içinde yükseliş gösteriyor.
8.18GOVP1Terfi pişmanlığı metriği: tanımlanıp bir daha kullanılmayan metrik = gürültü; geri alma/
arşivleme akışı
## AMAÇ
Gereksiz metrik üretimini engellemek (terfi de çöp üretebilir).
## NASIL
Terfi edilen her metriğin kullanım sayacını izle.
30 gün kullanılmayan terfi metrikleri 'pişmanlık' olarak işaretle.
Toplu geri alma/arşivleme akışı sun.
Terfi kriterlerini bu geri bildirimle kalibre et.
## BİTTİ SAYILIR
Kullanılmayan metrikler tespit edilip temizlenebiliyor.
Terfi isabet oranı ölçülüyor.
8.19GOVP1Sektör hafızası (benchmark hendeği): yalnız toplulaştırılmış/istatistiksel, ASLA ham veri; k-
anonimlik eşiği (min N müşteri); sözleşmede anonim toplulaştırma maddesi
## AMAÇ
Sektör kıyas verisini hukuka uygun ve güvenli üretmek.
## NASIL
Yalnız toplulaştırılmış istatistik paylaş (ortalama, medyan, çeyreklik) — ASLA ham veri veya tekil müşteri değeri.
k-anonimlik: en az N (ör. 5) müşteri katkı vermeden o kırılım yayınlanmaz.
Katılım opt-in olsun ve sözleşmede anonim toplulaştırma maddesi bulunsun.
Müşteri istediği an çıkabilsin; çıkınca katkısı havuzdan düşülsün.
Kıyas çıktısında kaç firmadan hesaplandığı belirtilsin.
## BİTTİ SAYILIR
Bir müşterinin verisi tek başına geri çıkarılamıyor (anonimlik testi).
Opt-out eden müşteri havuzdan çıkarılıyor.
## BE17BE19BE20
## 1.
## 2.
## 3.
## 4.
## 5.
## 6.
## •
## •
## BE16F23
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE17
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE20Y10
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası58 / 126

8.20UIP0Sistem uzmanı copilot: ayar, yetki, kurulum, metrik/kural tanımı ve kullanım öğrenimi tamamen
sohbetten yönetilir ('Ahmet'e sadece Güney Bölgesi'ni göster', 'OEE'yi şöyle hesaplıyoruz')
8.21GOVP1Kendi kendini teşhis + kurulum kalitesi skoru: eksik tanım, kopuk kaynak, sahipsiz metrik,
bayat bilgi, yavaş sorgu — sistemin kendi sağlık raporu
8.22ENGP0Dikkat ve bütçe motoru (nazar): işlem gücü ve token bütçesi, olayın finansal risk/fırsat
büyüklüğüne göre dağıtılır; kırtasiye faturasıyla ana hammadde faturası aynı emeği görmez
8.23LLMP1Playbook kütüphanesi: tekrarlayan durumlar için onaylı hazır iş akışları (stok kritik → tedarikçi
karşılaştır → sipariş taslağı → onay)
8.24ENGP0Kendi kendini onaran şema motoru: ERP'de kolon/tablo adı değişince sistem kilitlenmez;
sorgu hatasından şema drift'i tespit edilir, eşanlamlı haritası güncellenir, MDL'e commit atılır ve sahibine bildirilir
8.25LLMP0Kapalı devre öğrenme halkası: karar mührü → varsayım defteri → süre → gerçekleşen veri →
varsayım doğruysa hissiyat skoru yükselir, yanlışsa taakkul eşiği sıkılaşır. Karar–sonuç kütüphanesini öğrenmeye
çeviren motor
8.26GOVP0Açık kaynak lisans hijyeni: her bağımlılığın lisansı taranır ve kayda geçer. GPL/AGPL/BSL
lisanslı bileşenler kapalı kaynak SaaS'ta kullanılmaz; ihlal riski CI'da otomatik yakalanır (örn. Neo4j Community
GPLv3)
## R55R56R57R58
## F24
## R59R60BE16
## R65BE1BE10
## R88F17
## R59F26BE15
## R87BE12BE17
## BE7
✅ KABUL TESTLERİ / USE-CASE'LER 37 senaryo · GÜVENLİK: 9 · TEMEL: 19 · REGRESYON: 2 · SINIR: 7
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-8.1GÜVENLİKOtomatik kiracı izolasyon testi
çalıştırılır
A tenant'ının verisi B'ye hiçbir yolla sızmaz.
UC-8.2TEMELAynı soru farklı kelimelerle sorulurSemantik cache isabet eder; kullanıcıya 'benzer soruya
verilen cevap' bilgisi gösterilir.
UC-8.3GÜVENLİKFarklı yetkideki iki kullanıcı aynı
soruyu sorar
Cache anahtarı RLS bağlamı içerdiği için birbirlerinin
sonucunu görmezler.
UC-8.4REGRESYONMDL değiştirilirO modele bağlı tüm cache kayıtları otomatik geçersizleşir.
UC-8.5TEMELETL ile yeni veri yüklenirİlgili cache silinir; ilk sorgu taze veri getirir.
UC-8.6TEMEL3 ay kullanım sonrası altın yol oranı
ölçülür
LLM'siz cevaplanan soru oranı zaman içinde artmıştır.
UC-8.7TEMELMetrik tanımı değiştirilirEtkilenen panolarda sarı drift uyarısı belirir; sahiplerine
bildirim gider.
UC-8.8TEMELYeni bir tekstil müşterisine
UpcySustain paketi kurulur
1 saat içinde kurulur ve metrikler çalışır.
UC-8.9SINIRPaket v1.2'den v1.3'e güncellenirMüşterinin özelleştirmeleri bozulmaz.
UC-8.10TEMELBir işlem başarısız olurKredi düşülmez; fatura etkilenmez.
UC-8.11TEMELTenant kârlılık raporu açılırGelir ile gerçek LLM+altyapı maliyeti karşılaştırılabilir; zarar
ettiren müşteri görünür.
UC-8.12TEMELGecelik golden eval koşusu çalışırDoğruluk raporu üretilir; düşüş 24 saat içinde fark edilir.
UC-8.13SINIR100 eşzamanlı kullanıcı sisteme
yüklenir
Sistem yanıt vermeye devam eder; kuyruk derinliğine göre
worker ölçeklenir.
UC-8.14REGRESYONAktif olmayan müşteri bağlantıları
izlenir
TTL sonunda otomatik kapanır; bağlantı havuzu şişmez.
DİMA · 0→100 Görev Takip Dosyası59 / 126

IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-8.15GÜVENLİKLLM logları denetlenirHam prompt metni saklanmamıştır; yalnız imza ve istatistik
vardır, PII yoktur.
UC-8.16TEMELHaftalık terfi kuyruğu açılırEn yüksek skorlu 10 küme, örnek sorular, frekans, maliyet ve
hazır SQL taslağıyla listelenir.
UC-8.17TEMELBir terfi önerisi onaylanırMetrik oluşur; aynı soru sonraki sefer LLM'siz cevaplanır ve
maliyet farkı ölçülebilir.
UC-8.18SINIRTerfi edilen metrik 30 gün kullanılmaz'Pişmanlık' olarak işaretlenir ve temizleme önerilir.
UC-8.19TEMELAylık Dima Verimlilik Raporu üretilirGerçek verilerden hesaplanır: soru sayısı, LLM'siz oran, terfi
sayısı, maliyet değişimi.
UC-8.20GÜVENLİKSektör kıyası yayınlanırk-anonimlik eşiği altında kırılım gösterilmez; tek müşterinin
verisi geri çıkarılamaz; örneklem büyüklüğü belirtilir.
UC-8.21GÜVENLİKBir müşteri kıyas havuzundan çıkar
## (opt-out)
Katkısı havuzdan anında düşülür.
UC-8.22TEMELEşik aşımı gerçekleşir15 dakika içinde bildirim ulaşır; içerikte sapma, olası sebep ve
önerilen aksiyon vardır.
UC-8.23SINIRAynı uyarı kısa sürede tekrar tetiklenirBildirim yorgunluğu koruması devreye girer; tekrar
gönderilmez.
UC-8.24GÜVENLİKKasten yanlış LLM cevabı üretilen test
senaryosu çalıştırılır
Gölge kıyas (LlmShadow) sapmayı yakalar; güven skoru düşer
ve olay loglanır.
UC-8.25SINIRAşırı sayıda istek gönderilirSistem çökmez; anlaşılır limit mesajı ve bekleme süresi döner.
UC-8.26TEMELSohbetten 'Ahmet'e sadece Güney
Bölgesi'ni göster' denir (8.20)
Yetki tanımlanır, doğrulama için özet gösterilir ve onaydan
sonra yürürlüğe girer.
UC-8.27GÜVENLİKYetkisiz bir kullanıcı sohbetten yetki
değiştirmeye çalışır
Reddedilir; yalnız yönetici rolü ayar değiştirebilir ve her
değişiklik audit'e yazılır.
UC-8.28TEMEL'OEE'yi şöyle hesaplıyoruz' denirMetrik tanımı kaydedilir, versiyonlanır ve sonraki sorgularda
kullanılır.
UC-8.29TEMELKurulum kalitesi skoru açılır (8.21)Eksik tanım, kopuk kaynak, sahipsiz metrik ve bayat bilgi
listelenir; her biri tıklanınca ilgili ekrana gider.
UC-8.30TEMELKırtasiye faturası ve ana hammadde
faturası aynı anda gelir (8.22)
İkisine aynı işlem gücü ayrılmaz; bütçe finansal büyüklüğe
göre dağıtılır.
UC-8.31SINIRToplam bütçe sınırına yaklaşılırDüşük öncelikli işler ertelenir; kritik olanlar aksamaz.
UC-8.32TEMELStok kritik seviyeye düşer (8.23)Kayıtlı playbook çalışır: tedarikçi karşılaştır → sipariş taslağı →
onaya sun.
UC-8.33SINIRERP'de kolon adı değiştirilir (8.24)Sistem kilitlenmez; drift tespit edilir, eşanlamlı haritası
güncellenir, MDL'e commit atılır ve sahibine bildirilir.
UC-8.34GÜVENLİKŞema onarımı yanlış eşleşme yaparOtomatik uygulanmaz; öneri olarak sunulur ve insan onayı
beklenir.
UC-8.35TEMELBir kararın varsayımı 90 gün sonra
doğru çıkar (8.25)
Hissiyat skoru yükselir; benzer gelecek kararlarda güven
artar.
UC-8.36TEMELBir kararın varsayımı yanlış çıkarTaakkul eşiği sıkılaşır; aynı tip kararda daha fazla kanıt istenir.
UC-8.37GÜVENLİKBağımlılık listesi taranır (8.26)GPL/AGPL/BSL lisanslı bileşen tespit edilirse CI derlemeyi
durdurur ve gerekçe raporlanır.
DİMA · 0→100 Görev Takip Dosyası60 / 126

## ERP SEMBİYOZU VE AGENTIC VERİ GİRİŞİ
ERP rakip değil, resmî kayıt defteridir. Bu faz ERP'nin yerine geçmez; onun en zayıf yanını — manuel form doldurma hantallığını
— çözer. Ses, fotoğraf veya tek cümlelik mesaj, insan onaylı bir ERP kaydına dönüşür.
8B.1ENGP0ERP-agnostik adaptör katmanı: Logo, Netsis, Mikro, SAP ve benzeri için tek arayüz; her ERP
ayrı ürün değil ayrı adaptördür. Okuma (kayıt defteri) her zaman açık
8B.2LLMP0Agentic veri girişi: sesli not, fatura fotoğrafı veya WhatsApp mesajından ('Ahmet A.Ş.'ye
45.000 TL kargo dahil fatura kestik') yapılandırılmış kayıt taslağı üretimi
8B.3GOVP0Şema + politika + PII doğrulaması: taslak ERP şemasına uygun mu, iş kuralı ihlali var mı,
kişisel veri maskeli mi — yazma öncesi zorunlu kontrol
8B.4UIP0Tampon bölge (staging) + onay kartı: taslak önce tampona yazılır, kullanıcıya konfigüre edilmiş
kart olarak sunulur, 'Onayla ve ERP'ye işle' ile geçer. ONAYSIZ YAZMA YOK
8B.5GOVP0Yazma, geri alma ve tam denetim izi: her işlem kime ait, hangi taslaktan geldi, geri alınabilir
mi — contract'a bağlanır
8B.6ENGP1Giriş hızı ölçümü: aynı kaydın ERP formuyla ve Dima ile giriş süresi karşılaştırılır; 'kaç kat hızlı'
iddiası sayısal kanıta bağlanır
## FAZ 8B
## →99%
## R48R53F18
## R49Y6
## R50F25F8
## R51Y8
## R52F6
## R54F23
✅ KABUL TESTLERİ / USE-CASE'LER 8 senaryo · TEMEL: 5 · GÜVENLİK: 2 · SINIR: 1
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-8B.1TEMELFarklı bir ERP'ye geçilirYalnız adaptör değişir; iş mantığı ve arayüz aynı kalır.
UC-8B.2TEMELSesli not bırakılır: 'Ahmet A.Ş.'ye 45.000
TL fatura kestik'
Yapılandırılmış fatura taslağı üretilir; eksik alanlar sorulur.
UC-8B.3TEMELFatura fotoğrafı gönderilirOCR ile alanlar çıkarılır; düşük güvenli alanlar işaretlenip
kullanıcıya doğrulatılır.
UC-8B.4GÜVENLİKTaslak iş kuralını ihlal eder (limit aşımı)Yazma engellenir; hangi kuralın ihlal edildiği açıkça bildirilir.
UC-8B.5GÜVENLİKOnaysız yazma denenirHiçbir yoldan gerçekleşmez; tampon bölgede bekler.
UC-8B.6TEMELOnay verilirKayıt ERP'ye işlenir, contract'a bağlanır ve denetim izine
yazılır.
UC-8B.7SINIRYanlış kayıt işlendi, geri alınmak isteniyorGeri alma mümkündür ve iz bırakır.
UC-8B.8TEMELHız ölçümü raporlanırAynı kaydın ERP formu ve Dima ile giriş süreleri
karşılaştırmalı olarak gösterilir.
DİMA · 0→100 Görev Takip Dosyası61 / 126

## Genişleme Yüzeyleri & Cila
Kanal, entegrasyon, ileri görselleştirme, operasyon. Tüm külliyat senaryolarının uzun kuyruğu.
9.1VIZP0Grafik türü patlaması: ısı haritası/pareto/kohort/bubble/waterfall/sankey/gauge/harita + karar
verici geliştirme
## AMAÇ
Görsel dili zenginleştirmek ve doğru grafiği doğru veriye eşlemek.
## NASIL
Yeni tipler: ısı haritası, pareto, kohort matrisi, kabarcık, şelale (waterfall), sankey, gösterge (gauge), harita.
Her tip için ne zaman uygun olduğunu belirten kural ekle (2.2 seçicisini genişlet).
Waterfall özellikle varyans ayrıştırma için, sankey akış analizi için kritik.
Harita için il/ilçe sınır verisi ve koordinat eşleme.
## BİTTİ SAYILIR
Kök-neden analizleri otomatik olarak şelale grafiğiyle sunuluyor.
Coğrafi veri haritada doğru konumlanıyor.
9.2ENGP1Embedded API + token yönetimi + Embedded Threads (ISV/beyaz-etiket kanalı)
## AMAÇ
Dima'yı başka ürünlerin içine gömülebilir hale getirmek (ISV kanalı).
## NASIL
Public API: soru sor, sonuç al, contract al; token bazlı kimlik.
Uygulama başına token yönetimi, kota ve izin kapsamı.
Embedded thread: iframe veya web bileşeni olarak sohbet arayüzü.
Beyaz etiket: logo, renk, alan adı özelleştirme.
API dokümantasyonu ve örnek entegrasyon.
## BİTTİ SAYILIR
Üçüncü parti bir uygulama 1 günde entegre olabiliyor.
Gömülü kullanımda RLS ve maskeleme aynen çalışıyor.
9.3WRENP1Konnektör genişletme + dlt-connector SaaS ELT + dbt import
## AMAÇ
Daha fazla veri kaynağına bağlanabilmek.
## NASIL
Wren'in desteklediği konnektörleri sırayla etkinleştir ve test et.
SaaS kaynakları için dlt tabanlı ELT: Shopify, Stripe, reklam platformları.
dbt projesi olan müşteriler için model import.
Her yeni konnektör için bağlantı sihirbazı formu ve doğrulama testi.
## BİTTİ SAYILIR
En az 8 farklı veri kaynağı üretimde test edilmiş.
SaaS kaynağı bağlama 15 dakikadan kısa sürüyor.
9.4LLMP1Onaylı yazma (Operator) + approval workflow bağlama + webhook/otomasyon
## AMAÇ
Sistemin sadece önermekle kalmayıp onaylı aksiyon alabilmesi (Operatör fazı).
## NASIL
Yazma araçları: e-posta taslağı, ERP kayıt güncelleme, sipariş formu, görev/bilet açma.
HER aksiyon insan onayı gerektirir — onay ekranında ne yapılacağı net gösterilir.
Geri alınabilirlik: yapılan işlem kaydedilir, mümkünse geri alma sunulur.
Yetki: hangi rol hangi aksiyonu onaylayabilir.
Tüm aksiyonlar audit'e yazılır ve contract'a bağlanır.
## BİTTİ SAYILIR
Onaysız hiçbir yazma işlemi gerçekleşmiyor.
Yapılan her işlem geriye dönük izlenebiliyor.
## FAZ 9
## →100%
## Y11Ç5
## 1.
## 2.
## 3.
## 4.
## •
## •
## F20S88
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## F18S5Ç1
## 1.
## 2.
## 3.
## 4.
## •
## •
## Y8Y12
wAPPROVE
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası62 / 126

9.5LLMP1Çok-dilli çıktı + mobil/sesli hızlı sorgu + Slack/Teams
## AMAÇ
Kullanıcıya bulunduğu yerden erişmek.
## NASIL
Çok dilli çıktı: TR/EN (rapor ve yorumlar), arayüz i18n altyapısı.
Mobil arayüz: kart bazlı, tek elle kullanılabilir, hızlı sorgu.
Sesli sorgu: konuş → metne çevir → sorgula → kısa sesli/kart cevap.
Slack/Teams botu: kanal içinde soru sor, cevabı al (RLS korunarak).
## BİTTİ SAYILIR
Sahadaki kullanıcı telefondan 3 saniyede cevap alabiliyor.
Slack cevabında da yetki filtresi çalışıyor.
9.6DATAP1Dosya alımı & yerel metin analizi (PDF/OCR/transkript, KVKK-yerel) + anonim veri seti +
unstructured knowledge (docs/wiki)
## AMAÇ
Yapılandırılmamış içerikten veri çıkarabilmek (KVKK'ya uygun, yerel).
## NASIL
PDF/Word/görsel metin çıkarma + OCR (Türkçe destekli).
Toplantı/çağrı transkriptlerini işleme.
Metin analizi YEREL modelle yapılsın (veri dışarı çıkmasın).
Anonim veri seti üretimi: k-anonimlik kontrollü dışa aktarma.
Çıkarılan bilgi PROBABILISTIC_CONTEXT olarak etiketlenir (Faz 10.1).
## BİTTİ SAYILIR
Taranmış bir PDF'ten tablo çıkarılabiliyor.
Metin işleme sırasında veri kurum dışına çıkmıyor.
9.7DATAP1Çapraz-kaynak federasyon (iki sistemi tek soruda)
## AMAÇ
İki farklı sistemi tek soruda birleştirmek.
## NASIL
Çapraz kaynak sorgu planlayıcı: hangi kaynaktan ne çekilip nerede birleştirilecek.
Birleştirme bellekte veya geçici tabloda; büyük veri için uyarı.
Kaynak bazlı yetki kontrolü ayrı ayrı uygulanır.
Performans sınırı ve zaman aşımı.
## BİTTİ SAYILIR
ERP + CRM verisi tek soruda birleştirilebiliyor.
Yetkisi olmayan kaynak sorguya dahil edilmiyor.
9.8DATAP2Dikey motorlar: IoT/yüksek-frekans + izlenebilirlik grafı + sertifika/doküman takibi +
benchmark paketleri
## AMAÇ
Sektöre özel ileri motorlar.
## NASIL
IoT/yüksek frekans: zaman serisi sıkıştırma, downsampling, gerçek zamanlı pencere.
İzlenebilirlik grafı: lot/parti zinciri, ileri ve geri iz sürme.
Sertifika/doküman takibi: geçerlilik tarihi, kapsam, hatırlatma.
Benchmark paketleri: dış referans verilerinin entegrasyonu.
## BİTTİ SAYILIR
Dakikalık sayaç verisi performans sorunu yaratmadan sorgulanabiliyor.
Bir ürünün hammadde lotuna kadar izi sürülebiliyor.
## Y20Y21UX11S75
## 1.
## 2.
## 3.
## 4.
## •
## •
Y6Y19wPDFwUNSTRUCT
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## Y7
## 1.
## 2.
## 3.
## 4.
## •
## •
## Y14Y25Y13Y10
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası63 / 126

9.9LLMP2Eğitim/sandbox modu (SQL adım-adım öğretme)
## AMAÇ
Kullanıcıların sistemi güvenle öğrenmesi.
## NASIL
Sandbox: gerçek veriye dokunmayan örnek veri seti.
Adım adım SQL açıklama modu (eğitim amaçlı).
Rehberli turlar ve alıştırmalar.
## BİTTİ SAYILIR
Yeni kullanıcı sandbox'ta pratik yapabiliyor.
Sandbox'ta yapılan işlem gerçek veriyi etkilemiyor.
9.10LLMP2Portföy/çoklu-proje görünümü
## AMAÇ
Birden çok şirketi/projeyi yöneten kullanıcılar (mali müşavir, holding).
## NASIL
Portföy görünümü: tüm müşteriler/şirketler tek ekranda, kritik metrikler yan yana.
Hızlı geçiş (context switch) ve karşılaştırma.
Toplu uyarı: hangi şirkette kırmızı var.
Yetki: her şirket için ayrı erişim kontrolü.
## BİTTİ SAYILIR
Mali müşavir 40 mükellefini tek ekranda görebiliyor.
Şirketler arası veri sızıntısı yok.
9.11WRENP2OSI (Open Semantic Interchange) desteği
## AMAÇ
Semantik model standartlarına uyum.
## NASIL
OSI (Open Semantic Interchange) formatını içe/dışa aktarma.
Diğer semantik katmanlarla (dbt, Cube.dev) eşleme.
Standart uyumu pazarlamada kullanılabilsin.
## BİTTİ SAYILIR
Model dışa aktarılıp başka bir araçta okunabiliyor.
İçe aktarım kayıpsız çalışıyor.
9.12ENGP1Dış görev aracı entegrasyonu: Jira / Asana / Trello / ClickUp / Monday ile çift yönlü senkron;
durum değişimi her iki tarafta yansır, çift kayıt oluşmaz
## Y15S51
## 1.
## 2.
## 3.
## •
## •
## Y18S26
## 1.
## 2.
## 3.
## 4.
## •
## •
wOSI
## 1.
## 2.
## 3.
## •
## •
## R33
✅ KABUL TESTLERİ / USE-CASE'LER 24 senaryo · TEMEL: 12 · GÜVENLİK: 7 · SINIR: 5
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-9.1TEMELKök-neden analizi yapılırSonuç otomatik olarak şelale (waterfall) grafiğiyle sunulur.
UC-9.2TEMELİl bazlı veri sorgulanırHarita üzerinde doğru konumlarda gösterilir.
UC-9.3TEMELÜçüncü parti bir uygulama Embedded
API ile entegre olur
1 gün içinde entegrasyon tamamlanır; gömülü kullanımda RLS
ve maskeleme aynen çalışır.
UC-9.4GÜVENLİKGömülü sohbette yetkisiz veri istenirAna üründeki tüm yetki kuralları aynen uygulanır.
UC-9.5TEMELBir SaaS kaynağı (ör. e-ticaret
platformu) bağlanır
15 dakikadan kısa sürede veri akmaya başlar.
UC-9.6GÜVENLİKOnaysız bir yazma işlemi denenirGerçekleşmez; her aksiyon insan onayı gerektirir.
UC-9.7TEMELOnaylı bir aksiyon (e-posta taslağı)
yürütülür
İşlem audit'e yazılır, contract'a bağlanır ve mümkünse geri
alınabilir.
UC-9.8TEMELSahadaki kullanıcı telefondan sesli soru
sorar
3 saniyede kart formatında cevap alır.
UC-9.9GÜVENLİKSlack üzerinden soru sorulurYetki filtresi çalışır; kullanıcı yalnız yetkili olduğu veriyi görür.
DİMA · 0→100 Görev Takip Dosyası64 / 126

## DIŞ KATMAN — FRONTDESK
İçeride genel müdür, dışarıda resepsiyonist. Aynı beyin, müşteriye/hastaya/veliye dönük bir yüz kazanır. Bu fazın tamamı tek bir
kurala dayanır: dış dünya iç veriye asla doğrudan erişemez ve asla doğrudan yazamaz.
9B.1GOVP0★ ÖN ŞART — İzolasyon duvarı ve kamu şeması: dışarıya yalnız kamuya açık veri (katalog,
fiyat, SSS, çalışma saati) görünür. İç maliyet, marj, maaş, tedarikçi adı şema seviyesinde erişilemez
9B.2GOVP0Tampon bölge: dış kanaldan gelen hiçbir istek veritabanına doğrudan yazamaz. Randevu,
sipariş, talep önce staging'e düşer, kural kontrolünden sonra iç sisteme aktarılır
9B.3GOVP0Müşteri-RLS + OTP doğrulama: kişi kendi verisini (sipariş, randevu, bakiye) ancak SMS/e-
posta doğrulamasından sonra ve yalnız kendi satırları kapsamında görebilir
9B.4UIP0Üretken arayüz kataloğu: sohbet içinde kaydırılabilir ürün/hizmet kartları, görseller, teknik föy
(PDF), fiyat tablosu, tarih-saat seçici
9B.5LLMP0Kapasite-farkında randevu motoru: boş saati değil gerçekten uygun saati önerir; hazırlık,
temizlik ve yoğunluk süreleri hesaba katılır
9B.6LLMP1Satış niyeti skoru: sorulan sorulardan ('taksit var mı', 'teslimat kaç gün') satın alma eğilimi
hesaplanır; eşik aşılınca satış ekibine sıcak fırsat düşer
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-9.10TEMELTaranmış bir PDF yüklenirOCR ile tablo çıkarılır; işlem sırasında veri kurum dışına
çıkmaz.
UC-9.11TEMELERP + CRM verisi tek soruda birleştirilirDoğru sonuç döner; yetkisi olmayan kaynak sorguya dahil
edilmez.
UC-9.12TEMELDakikalık sayaç verisi sorgulanırPerformans sorunu yaşanmaz (downsampling devrede).
UC-9.13TEMELBir ürünün hammadde lotu sorgulanırİzlenebilirlik zinciri geriye ve ileriye doğru gezinilebilir.
UC-9.14GÜVENLİKSandbox modunda işlem yapılırGerçek veri etkilenmez.
UC-9.15GÜVENLİKMali müşavir 40 mükellefini portföy
ekranında görür
Şirketler arası veri sızıntısı olmaz; her biri için ayrı erişim
kontrolü çalışır.
UC-9.16SINIRSankey/şelale grafiğinde negatif değer
bulunur
Grafik bozulmaz; negatif katkı doğru yönde çizilir.
UC-9.17GÜVENLİKEmbedded API token'ı sızdırılır ve
kötüye kullanılır
Kota ve kapsam sınırı devreye girer; token iptal edilebilir.
UC-9.18SINIRdlt ile bağlanan SaaS kaynağı şema
değiştirir
Kırılma tespit edilir ve kullanıcı uyarılır; sessizce yanlış veri
akmaz.
UC-9.19GÜVENLİKOnaylı aksiyon geri alınmak istenirGeri alma mümkündür ve audit'e yazılır.
UC-9.20SINIRSesli sorgu gürültülü ortamda yapılırAnlaşılmazsa sistem tahmin etmez, tekrar sorar.
UC-9.21SINIRÇapraz kaynak sorgusu çok büyük veri
döndürür
Zaman aşımı ve uyarı devreye girer; sistem kilitlenmez.
UC-9.22TEMELDima'da görev oluşturulur (9.12)Bağlı dış araçta (Jira/Asana vb.) da görünür; çift kayıt oluşmaz.
UC-9.23TEMELDış araçta görev kapatılırDurum Dima'da da güncellenir; iki taraf tutarlı kalır.
UC-9.24SINIRDış araç geçici olarak erişilemez olurDeğişiklikler kuyruğa alınır ve bağlantı dönünce senkronlanır;
veri kaybı olmaz.
## FAZ 9B
dış yüzey
## R68BE2
## F8
## R69Y8
## R70F7Ç18
## R71F13
## R72
## R73
DİMA · 0→100 Görev Takip Dosyası65 / 126

9B.7UIP0İnsana devir protokolü: gerginlik veya karmaşıklıkta sohbet canlı temsilciye aktarılır; temsilcinin
ekranına konuşma özeti ve müşteri sancı analizi otomatik düşer
9B.8DATAP1Omnichannel kimlik çözümleme: aynı kişinin WhatsApp, web, telefon ve kiosk izleri tek
kimlikte birleştirilir (rıza ve KVKK sınırları içinde)
9B.9LLMP1Müşteri sesi → iç istihbarat: dışarıda sorulan binlerce soru anonim olarak işlenir ve iç beyne
rapor edilir ('müşterilerin %24'ü olmayan bir hizmeti sordu')
9B.10DATAP1Dikey dış paketler: klinik/hastane, okul, fabrika-B2B, otel-restoran, servis için hazır senaryo,
akış ve arayüz setleri
## R74
## R76F8
## R75BE20
## R77F18
✅ KABUL TESTLERİ / USE-CASE'LER 10 senaryo · GÜVENLİK: 4 · TEMEL: 5 · SINIR: 1
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-9B.1GÜVENLİKDış kullanıcı 'bu ürünün size maliyeti ne?'
diye sorar
Şema seviyesinde erişim olmadığı için sistem bu veriyi hiç
göremez; sızıntı yok.
UC-9B.2GÜVENLİKDış kanaldan doğrudan veritabanı yazma
denenir
İmkânsızdır; tüm istekler tampon bölgeden geçer.
UC-9B.3GÜVENLİKMüşteri doğrulama olmadan kendi
bakiyesini sorar
OTP istenir; doğrulanmadan hiçbir kişisel veri gösterilmez.
UC-9B.4GÜVENLİKDoğrulanmış müşteri başka müşterinin
verisini istemeye çalışır
Müşteri-RLS engeller; yalnız kendi satırlarını görür.
UC-9B.5TEMELKatalog sorulurKaydırılabilir kartlar, görsel ve fiyat tablosu gelir; PDF föy
indirilebilir.
UC-9B.6TEMELRandevu istenirTakvimde boş görünen ama operasyonel olarak uygun
olmayan saat önerilmez.
UC-9B.7TEMELMüşteri taksit ve teslimat sorarSatış niyeti skoru yükselir; eşik aşılınca satış ekibine sıcak
fırsat bildirimi düşer.
UC-9B.8SINIRMüşteri gerginleşir veya sistem çözemezSohbet kilitlenmez; canlı temsilciye özet ve sancı analiziyle
devredilir.
UC-9B.9TEMELAynı kişi WhatsApp ve web'den yazarTek kimlikte birleştirilir; geçmiş bağlam korunur (rıza
sınırları içinde).
UC-9B.10TEMELGece raporu üretilirDışarıda kaç randevu alındı, ne soruldu, ne kaybedildi — iç
beyne anonim olarak raporlanır.
DİMA · 0→100 Görev Takip Dosyası66 / 126

v4 — KURUMSAL BİLGİ HUB'I & Yapılandırılmamış Bağlam
Buradan itibaren ürün çekirdeği (%100 = Karar Merkezi, v3) tamamlanmıştır; bu ve sonraki fazlar NİHAİ VİZYON'dur. Şirketin
kararlarının %80'i veritabanında değil; toplantıda, yazışmada, haberde, CEO'nun zihnindedir. Bu faz o bağlamı sisteme sokar —
ama Gold Badge'i ASLA kirletmeden.
10.1GOVP0★ ÖN ŞART — Kanıt Sınıfı Ayrımı: her bilgi parçası DETERMINISTIC_FACT (ERP/SQL → 磊 Gold)
veya PROBABILISTIC_CONTEXT (toplantı/haber/not → 'Bağlam Notu / Duyum') olarak etiketlenir; ikisi hiçbir çıktıda
karışmaz. Bu görev bitmeden 10.3+ başlamaz
## AMAÇ
Ürünün en kritik koruma kuralı: kesin veri ile duyumun karışmaması. Bu bozulursa tüm güven mimarisi çöker.
## NASIL
Her bilgi parçasına zorunlu sınıf etiketi: DETERMINISTIC_FACT (ERP/SQL/sayaç → altın rozet) veya
PROBABILISTIC_CONTEXT (toplantı, haber, not, e-posta → bağlam notu).
Etiket veri modelinde zorunlu alan olsun; etiketsiz kayıt sisteme giremesin.
Sentez kuralı: bir cevapta ikisi birlikte kullanılabilir ama AYRI BLOKLARDA ve farklı görsel dille sunulur.
Bağlam bilgisi asla sayısal metrik gibi gösterilmez (grafiğe girmez, toplama katılmaz).
Otomatik test: bir bağlam bilgisinin metrik hesabına karıştığı senaryo yakalanmalı.
BU GÖREV BİTMEDEN 10.3 ve sonrası başlamaz.
## BİTTİ SAYILIR
Hiçbir çıktıda duyum verisi kesin veri gibi gösterilmiyor (denetlendi).
Etiketsiz veri sisteme kaydedilemiyor.
Karışım denemesi otomatik testle yakalanıyor.
10.2UIP0İki düzlem sunum dili: 'ERP verisine göre ciro 10M TL (Gold). Ancak dünkü strateji toplantısına
göre bunun %20'si yatırıma ayrılmalı (Bağlam Notu)' — rozet + ayrı blok + karışım yasağı
## AMAÇ
Kullanıcının hangi bilginin kesin hangisinin yorum olduğunu bir bakışta anlaması.
## NASIL
Görsel ayrım: kesin veri altın rozetli kart; bağlam notu farklı renk + 'duyum/not' etiketi.
Sentez cümlesi kalıbı: 'ERP verisine göre X (kanıtlı). Ancak Y toplantısına göre Z (bağlam notu, doğrulanmamış).'
Bağlam notlarında kaynak ve tarih zorunlu ('12 Mart strateji toplantısı, Ahmet Y.').
Raporlarda da aynı ayrım korunur (ekler bölümünde bağlam kaynakları).
## BİTTİ SAYILIR
Kullanıcı testinde katılımcılar hangi bilginin kesin olduğunu doğru ayırt ediyor.
Bağlam notlarının kaynağı her zaman görünüyor.
10.3DATAP0Unstructured Ingestion Wizard: PDF / Word / mizan / sözleşme / SOP / şikâyet metni yükleme
+ OCR + parçalama + kullanıcı onaylı anlamlandırma
## AMAÇ
Şirketin veritabanı dışındaki bilgisini sisteme almak.
## NASIL
Desteklenen formatlar: PDF, Word, Excel, metin, e-posta dışa aktarımı, taranmış görsel (OCR).
İşlem hattı: yükle → metin çıkar → parçala (chunk) → sınıflandır (SOP mu, sözleşme mi, rapor mu) → etiketle (10.1) →
indeksle.
Kullanıcı onaylı anlamlandırma: 'bu bir tedarikçi sözleşmesi, tarafı X firması, geçerlilik Aralık 2026' — sistem çıkarır,
kullanıcı onaylar.
Büyük dosyalar için arka plan işi ve ilerleme göstergesi.
Yükleme sırasında PII taraması ve maskeleme seçeneği.
## BİTTİ SAYILIR
100 sayfalık bir PDF 5 dakikada işlenip aranabiliyor.
Yanlış sınıflandırma kullanıcı tarafından düzeltilebiliyor.
## FAZ 10
v4
## BE21F6
## 1.
## 2.
## 3.
## 4.
## 5.
## 6.
## •
## •
## •
## BE21UX1
## 1.
## 2.
## 3.
## 4.
## •
## •
BE22Y6wUNSTRUCT
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası67 / 126

10.4DATAP0Knowledge Graph: metinden çıkan varlıklar (müşteri, tedarikçi, ürün, proje, kişi) ERP
ID'leriyle bağlanır — vektör + graf hibrit; 'müşteri ne dedi' ile 'müşterinin bakiyesi' aynı düğümde
## AMAÇ
Metindeki bilgiyi veritabanındaki kayıtlarla birleştirmek — asıl değer burada.
## NASIL
Varlık çıkarma: dokümandan müşteri, tedarikçi, ürün, proje, kişi, tarih, tutar çıkar.
Varlık eşleme: çıkarılan 'ABC Tekstil' ile ERP'deki musteri_id=482 aynı mı? (bulanık eşleme + kullanıcı onayı).
Graf yapısı: düğüm (varlık) + kenar (ilişki: 'sözleşme tarafı', 'şikayet konusu', 'toplantıda bahsedildi').
Sorgu zamanında graf üzerinden ilgili bağlamı getir ('X müşterisi' sorulunca hem cirosu hem şikayeti gelsin).
Graf saklama: pgvector + ilişki tablosu (ayrı graf DB'ye gerek yok, karmaşıklık eklemesin).
## BİTTİ SAYILIR
'X müşterisi hakkında ne biliyoruz?' sorusu hem finansal veriyi hem doküman bilgisini getiriyor.
Yanlış varlık eşlemesi kullanıcı tarafından düzeltilebiliyor.
10.5GOVP0Yapılandırılmamış veri yönetişimi: doküman bazlı erişim izni (RLS'in doküman karşılığı), gizlilik
sınıfı, saklama süresi, silme akışı
## AMAÇ
Dokümanların yanlış kişiye görünmesini engellemek.
## NASIL
Her dokümana: gizlilik sınıfı (genel/departman/yönetim/gizli), sahip, erişim listesi, saklama süresi.
Arama ve cevap üretiminde kullanıcının erişemediği doküman hiç kullanılmaz (sonuçta da görünmez).
Saklama süresi dolan doküman otomatik arşiv/silme akışına girer.
Erişim logu: kim hangi dokümana ne zaman eriştiğini görebilsin.
## BİTTİ SAYILIR
Yetkisiz kullanıcı gizli dokümandan üretilen bilgiyi göremiyor.
Saklama süresi yönetimi çalışıyor.
10.6LLMP0Corporate SOP & Onboarding Hub: rol bazlı prosedür rehberliği — 'hatalı parçayı nasıl iade
alırım?' → SOP + ERP adımı + geçmiş başarılı örnek sentezi
## AMAÇ
Şirket bilgisini çalışanın işini yapabileceği rehberliğe dönüştürmek.
## NASIL
Soru tipi: 'nasıl yapılır' → SOP dokümanları + ERP ekran adımları + geçmiş örnekler sentezlenir.
Cevap formatı: numaralı adımlar + gerekli yetki + dikkat notları + ilgili doküman bağlantısı.
Rol bazlı: aynı soruya depo elemanı ile muhasebeci farklı detayda cevap alır.
Adım sonunda 'bu işe yaradı mı?' geri bildirimi topla ve rehberi iyileştir.
## BİTTİ SAYILIR
Yeni çalışan bir prosedürü sistemden öğrenip uygulayabiliyor.
Cevaplar kaynak dokümana bağlantı veriyor.
10.7UIP0Bilgi Hub arayüzü: arama, kaynak gösterimi, 'bu bilgi nereden geliyor' izi, departman/rol
filtreleri
## AMAÇ
Kurumsal bilginin aranabilir ve güvenilir olduğu tek yer.
## NASIL
Birleşik arama: dokümanlar + metrikler + kararlar + skill'ler tek arama kutusunda.
Sonuçlarda kaynak tipi rozeti (doküman/veri/karar) ve tarih.
'Bu bilgi nereden geliyor' izi her sonuçta.
Departman ve tarih filtreleri; sık kullanılanlar.
## BİTTİ SAYILIR
Kullanıcı aradığı prosedürü 30 saniyede bulabiliyor.
Her sonucun kaynağı görünüyor.
## BE22Y7
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE22F7F8
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE22Y15
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE22UX1
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası68 / 126

10.8LLMP1CEO Mind-Dump / Executive Cortex: sesli veya yazılı stratejik not → Global Strategy Policy
kuralına dönüşür → tüm analiz ve kararlarda kısıt olarak uygulanır ('kâr marjı %15'in altına inmesin')
## AMAÇ
Yöneticinin stratejik yönlendirmesini sistemin kalıcı kuralına dönüştürmek.
## NASIL
Giriş: sesli not (STT) veya yazılı serbest metin.
Sistem bunu yapılandırılmış kurala çevirir: 'kâr marjı %15 altına inmesin' → {metrik: marj, operatör: >=, değer: 15,
kapsam: yeni ürün}.
Kullanıcı onaylar (yanlış yorumlama riski için zorunlu).
Onaylanan kural Global Strategy Policy'ye yazılır ve ilgili analizlerde kısıt olarak uygulanır.
Kuralın sahibi, tarihi ve geçerlilik süresi tutulur.
## BİTTİ SAYILIR
Bir sesli not 2 dakikada uygulanabilir kurala dönüşüyor.
Kural sonraki analizlerde gerçekten uygulanıyor ve bu görünüyor.
10.9GOVP1Strateji kuralı çakışma yönetimi: CEO notu ile politika veya veri çelişirse sessizce uygulanmaz
— çelişki kullanıcıya gösterilir, sahibi karar verir
## AMAÇ
Stratejik kural ile gerçekliğin çeliştiği anı yakalamak.
## NASIL
Her analizde uygulanan strateji kurallarını kontrol et.
Çelişki tespiti: kural '%15 marj' diyor ama mevcut fiyatlama %11 veriyor.
Sessizce uygulama veya sessizce yoksayma YOK — çelişki kullanıcıya gösterilir.
Karar sahibine bildirim: 'stratejik kuralınız mevcut durumla çelişiyor'.
Kural güncellenebilir veya istisna tanımlanabilir (gerekçeyle).
## BİTTİ SAYILIR
Çelişen kural durumunda sistem sessiz kalmıyor.
İstisnalar gerekçesiyle kaydediliyor.
10.10DATAP1Dış istihbarat radarı: sektör haberleri, döviz/emtia/enflasyon beslemeleri → Knowledge
Graph varlıklarına bağlanır (hepsi PROBABILISTIC_CONTEXT)
## AMAÇ
Şirket dışı bilgiyi (haber, kur, emtia) iç veriyle ilişkilendirmek.
## NASIL
Kaynaklar: sektör haber akışları, döviz/emtia/enflasyon verileri, gerekirse resmî yayınlar.
Hepsi PROBABILISTIC_CONTEXT olarak etiketlenir (haber kesin veri değildir).
Varlık eşleme: haberdeki firma adı Knowledge Graph'taki tedarikçi/müşteri ile eşleşirse ilişkilendir.
Kullanıcıya ilgili olduğunda gösterilir ('tedarikçiniz hakkında bir haber var').
Kaynak, tarih ve bağlantı her zaman gösterilir.
## BİTTİ SAYILIR
Tedarikçiyle ilgili bir haber, o tedarikçinin analizinde bağlam olarak beliriyor.
Haber verisi hiçbir metrik hesabına karışmıyor.
## BE28F25
## BE19
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE28F25
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE22Y10BE21
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
✅ KABUL TESTLERİ / USE-CASE'LER 17 senaryo · GÜVENLİK: 5 · TEMEL: 8 · REGRESYON: 1 · SINIR: 3
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-10.1GÜVENLİKBir toplantı notu ile bir ERP metriği aynı
cevapta kullanılır
İkisi AYRI bloklarda ve farklı görsel dille sunulur; asla
karışmaz.
UC-10.2GÜVENLİKBağlam notundaki bir sayı metrik
hesabına karıştırılmaya çalışılır
Otomatik test bunu yakalar; bağlam verisi grafiğe girmez,
toplama katılmaz.
UC-10.3GÜVENLİKEtiketsiz bir bilgi sisteme kaydedilmeye
çalışılır
Reddedilir; kanıt sınıfı zorunlu alandır.
UC-10.4TEMELKullanıcı testinde katılımcılara karışık
çıktı gösterilir
Katılımcılar hangi bilginin kesin hangisinin duyum olduğunu
doğru ayırt eder.
DİMA · 0→100 Görev Takip Dosyası69 / 126

v5 — CANLI AKIL: Toplantı Ajanı & Red Team
Dima toplantıya katılır, dinler, anlar ve karar süreçlerine aktif katılır. En yüksek değer ile en yüksek hukuki riskin buluştuğu faz
— bu yüzden hukuki çerçeve ilk görevdir, teknoloji ikinci.
11.1GOVP0★ ÖN ŞART — Toplantı kaydı hukuki çerçevesi: açık rıza akışı, tüm katılımcılara bildirim, kayıt/
transkript saklama ve silme politikası, opt-out, çalışan aydınlatma metni (KVKK). Hukuk onayı olmadan 11.2+
başlamaz
## AMAÇ
Toplantı dinleme özelliğinin hukuki zeminini kurmak — bu bitmeden kod yazılmaz.
## NASIL
Aydınlatma metni ve açık rıza akışı hazırla (KVKK); tüm katılımcılar toplantı başında bilgilendirilsin.
Rıza vermeyen katılımcı için opt-out mekanizması (o kişinin konuşması işlenmez veya toplantı kaydedilmez).
Saklama politikası: ses kaydı ne kadar saklanır, transkript ne kadar, kim silebilir.
Veri sahibi hakları: erişim, düzeltme, silme talebi akışı.
Hukuk danışmanı onayı alınmadan sonraki görevler başlamaz (kapı).
Çalışan bilgilendirme ve iç politika dokümanı.
## BİTTİ SAYILIR
Yazılı hukuk görüşü ve onaylı aydınlatma metni mevcut.
Opt-out eden katılımcının verisi işlenmiyor (test edildi).
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-10.5REGRESYONBağlam notu görüntülenirKaynağı ve tarihi her zaman görünür ('12 Mart strateji
toplantısı').
UC-10.6TEMEL100 sayfalık bir PDF yüklenir5 dakika içinde işlenir ve aranabilir hale gelir.
UC-10.7SINIRDoküman yanlış sınıflandırılır (sözleşme
yerine rapor)
Kullanıcı düzeltebilir; düzeltme öğrenilir.
UC-10.8TEMEL'X müşterisi hakkında ne biliyoruz?'
sorulur
Hem finansal veri hem doküman bilgisi (sözleşme, şikayet)
birlikte gelir.
UC-10.9SINIRDokümandaki 'ABC Tekstil' ile ERP'deki
müşteri kaydı eşleşmez
Sistem tahmin dayatmaz; kullanıcıya eşleştirme onayı sorar.
UC-10.10GÜVENLİKYetkisiz kullanıcı gizli dokümanla ilgili
soru sorar
O dokümandan üretilen bilgi hiç kullanılmaz ve sonuçta
görünmez.
UC-10.11TEMELSaklama süresi dolan bir doküman
kontrol edilir
Otomatik arşiv/silme akışına girmiştir.
UC-10.12TEMELYeni çalışan 'hatalı parçayı nasıl iade
alırım?' diye sorar
Numaralı adımlar + gerekli yetki + kaynak doküman
bağlantısı gelir.
UC-10.13TEMELAynı soruyu depo elemanı ve
muhasebeci sorar
Rollerine göre farklı detay düzeyinde cevap alırlar.
UC-10.14TEMELCEO sesli not bırakır: 'kâr marjı %15
altına inmesin'
2 dakikada yapılandırılmış kurala dönüşür; kullanıcı
onayından sonra analizlerde kısıt olarak uygulanır.
UC-10.15SINIRStratejik kural mevcut durumla çelişir
## (marj %11)
Sessizce uygulanmaz veya yok sayılmaz; çelişki kullanıcıya
gösterilir ve karar sahibine bildirilir.
UC-10.16TEMELTedarikçiyle ilgili bir haber yayınlanırO tedarikçinin analizinde bağlam notu olarak belirir; kaynak
ve tarih gösterilir.
UC-10.17GÜVENLİKHaber verisi kontrol edilirHiçbir metrik hesabına karışmamıştır.
## FAZ 11
v5
## BE23F25F8
## 1.
## 2.
## 3.
## 4.
## 5.
## 6.
## •
## •
DİMA · 0→100 Görev Takip Dosyası70 / 126

11.2ENGP0Toplantı konnektörü: Teams / Zoom / Google Meet katılımı, kayıt veya canlı ses akışı alma
## AMAÇ
Toplantı platformlarına bağlanabilmek.
## NASIL
Teams / Zoom / Google Meet bot katılımı veya kayıt API'si entegrasyonu.
Katılım öncesi otomatik bildirim mesajı ('bu toplantı Dima tarafından kaydediliyor').
Toplantı meta verisi: katılımcılar, süre, başlık, takvim bağlantısı.
Bağlantı kopması ve yeniden bağlanma yönetimi.
## BİTTİ SAYILIR
Bot toplantıya katılıyor ve tüm katılımcılar bilgilendiriliyor.
Bağlantı koptuğunda kayıt kaybı olmuyor.
11.3LLMP0STT + diarization (konuşmacı ayrımı) — tercihen on-prem/yerel model; ses verisi kurum dışına
çıkmaz (egemenlik anlatısının devamı)
## AMAÇ
Sesi metne çevirmek ve kimin konuştuğunu ayırmak.
## NASIL
Türkçe destekli STT modeli; tercihen ON-PREM/yerel (ses verisi dışarı çıkmasın).
Diarization: konuşmacı ayrımı; katılımcı listesiyle eşleştirme (gönüllü).
Zaman damgalı transkript üret; terimler için şirket sözlüğü kullanılarak düzeltme.
Doğruluk ölçümü: örnek toplantılarda kelime hata oranı takibi.
## BİTTİ SAYILIR
Türkçe toplantıda anlaşılır transkript üretiliyor.
Ses verisi kurum ağı dışına çıkmıyor (ağ denetimiyle doğrulandı).
11.4LLMP0Toplantı sentezi: karar / aksiyon / sorumlu / tarih çıkarımı → Karar Kaydı'na ve görev sistemine
bağlanır; seçici hafıza politikasıyla yalnız önemli olan kaydedilir
## AMAÇ
Toplantıdan sadece özet değil, yapılandırılmış çıktı üretmek.
## NASIL
Çıkarılacaklar: alınan kararlar, aksiyon maddeleri (sorumlu + tarih), açık sorular, riskler.
Kararlar Karar Kaydı formatına (6B.8) dönüştürülüp onaya sunulur.
Aksiyonlar görev sistemine (varsa Jira/Asana, yoksa iç liste) yazılabilir.
Seçici hafıza politikası (5.6) uygulanır: her cümle değil, yalnız karar/taahhüt/tanım kaydedilir.
Toplantı çıktısı katılımcılara özet olarak gönderilir.
## BİTTİ SAYILIR
Toplantı sonrası 5 dakikada aksiyon listesi hazır oluyor.
Alınan kararlar Karar Kaydı'na aday olarak düşüyor.
11.5LLMP1Canlı müdahale: toplantıda söylenen bir iddia veriyle çelişirse anlık uyarı — 'bu karar Q3
bütçesini %12 aşar' (kanıt bağlantılı)
## AMAÇ
Toplantı sırasında veriyle çelişen ifadeyi yakalamak.
## NASIL
Canlı transkriptten sayısal iddiaları tespit et ('bu bütçeyi %10 aşmaz').
İlgili metriği sorgula ve karşılaştır.
Çelişki varsa DİSKRET uyarı (ekran kenarı veya moderatöre özel), toplantıyı bölmeden.
Uyarı kanıt bağlantılı olsun.
Yanlış alarm riskine karşı yüksek eşik ve 'emin değilim' durumunda sessiz kalma.
## BİTTİ SAYILIR
Bilinen çelişki senaryosunda uyarı üretiliyor.
Yanlış alarm oranı düşük (test toplantılarında ölçüldü).
## BE23
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE23F21
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE23BE19BE20
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE23BE21
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası71 / 126

11.6LLMP0Red Team / Şeytanın Avukatı: karara karşı ajan — geçmiş başarısızlıklar, rakip hamleleri,
makro veriler ve toplantıdaki çekinceler taranır → 'kör noktalarınız' raporu
## AMAÇ
Kararı acımasızca test eden karşıt akıl — 'evet efendimci' kültürüne panzehir.
## NASIL
Karar verildiğinde/tartışıldığında karşıt ajan çalışır.
Tarar: benzer geçmiş kararlar ve sonuçları, ilgili metriklerdeki olumsuz sinyaller, dış veriler, toplantıda dile getirilmiş
çekinceler.
Çıktı: 3-5 maddelik 'kör noktalar' listesi + her madde için kanıt.
Ton kılavuzu: kişiyi değil kararı hedefler, saygılı ama net.
Kullanıcı 'bunu dikkate aldık' işaretleyebilir (kayda geçer).
## BİTTİ SAYILIR
Karşıt ajan gerçek verilerden beslenen somut itirazlar üretiyor (genel laf değil).
İtirazlar karar kaydına ekleniyor.
11.7LLMP1Bilişsel yanılsama sensörü: batık maliyet, onaylama yanlılığı, grup düşüncesi tespiti — 'bu
karar verisel değil, batık maliyet kaynaklı görünüyor'
## AMAÇ
Kararın veriye mi duyguya mı dayandığını teşhis etmek.
## NASIL
Tespit edilecek örüntüler: batık maliyet ('zaten çok harcadık'), onaylama yanlılığı (yalnız destekleyici veri), grup
düşüncesi (itiraz yok), aşırı güven (belirsizlik yok sayılıyor).
Girdi: karar gerekçesi metni + kullanılan veri + toplantı transkripti.
Çıktı: tespit + gerekçe + öneri ('projeyi bağımsız değerlendirin').
DİKKAT: kişisel yargı içermesin, kararın gerekçesine odaklansın.
Yanlış tespit riski yüksek olduğu için yalnız güçlü sinyalde göster.
## BİTTİ SAYILIR
Test senaryolarında batık maliyet örüntüsü doğru tespit ediliyor.
Çıktı kişiyi hedef almıyor (dil denetimi).
11.8GOVP1Red Team tonu ve yetki sınırı: veto değil uyarı; kişiyi değil kararı hedefler; patron-ego
yönetimi için dil kılavuzu
## AMAÇ
Karşıt aklın kabul edilebilir ve etkili olmasını sağlamak.
## NASIL
Yetki sınırı: Dima uyarır, itiraz eder ama VETO ETMEZ; karar insanındır.
Dil kılavuzu: 'bu karar yanlış' değil, 'şu veriler dikkate alınmalı'.
Uyarı yoğunluğu ayarı (her karara mı, yalnız yüksek riskli kararlara mı).
Kullanıcı geri bildirimi: itiraz faydalı mıydı? (motoru kalibre etmek için).
## BİTTİ SAYILIR
Kullanıcılar karşıt ajanı kapatma ihtiyacı duymuyor (kabul testi).
İtirazların faydalılık oranı ölçülüyor.
## BE24Y5
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE24BE19
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE24F5
## 1.
## 2.
## 3.
## 4.
## •
## •
✅ KABUL TESTLERİ / USE-CASE'LER 15 senaryo · GÜVENLİK: 5 · TEMEL: 7 · SINIR: 2 · REGRESYON: 1
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-11.1GÜVENLİKToplantı kaydı özelliği devreye alınmadan
önce denetlenir
Yazılı hukuk görüşü ve onaylı aydınlatma metni mevcuttur;
yoksa özellik kapalıdır.
UC-11.2GÜVENLİKBir katılımcı rıza vermez (opt-out)O kişinin konuşması işlenmez veya toplantı kaydedilmez.
UC-11.3TEMELBot toplantıya katılırTüm katılımcılar otomatik bilgilendirilir ('bu toplantı
kaydediliyor').
UC-11.4SINIRToplantı sırasında bağlantı koparYeniden bağlanılır; kayıt kaybı olmaz.
UC-11.5TEMELTürkçe bir toplantı kaydedilirAnlaşılır transkript üretilir; konuşmacılar ayrılır.
UC-11.6GÜVENLİKAğ trafiği denetlenirSes verisi kurum ağı dışına çıkmaz (yerel STT).
DİMA · 0→100 Görev Takip Dosyası72 / 126

v6 — KÜLLİ AKIL: Simülasyon, Proaktif Keşif, Kolektif Zekâ
Şirketin dijital ikizi, geleceği simüle eden ve sormadığın soruların cevabını getiren katman. Nihai vizyonun zirvesi.
12.1LLMP0Hipotez & Fırsat Keşif Motoru (Inverted BI): gece veri kombinasyonlarını tarar, hipotez üretir
ve test eder → sabah 'sormadığın fırsat' bildirimi ('X alanların %34'ü Y de alıyor, paketleyelim mi?')
## AMAÇ
Kullanıcının sormadığı ama sorması gereken soruların cevabını getirmek.
## NASIL
Gece işi: metrikler arası ilişkiler, çapraz satış örüntüleri, segment davranışları, fiyat-hacim ilişkileri taranır.
Hipotez üret ve test et: istatistiksel anlamlılık kontrolü (rastlantıyı fırsat sanma).
Etki tahmini hesapla ve büyüklüğe göre sırala.
Sabah bildirimi: en yüksek etkili 1-3 bulgu, gerekçe ve önerilen aksiyonla.
Yanlış pozitifi önlemek için eşik yüksek tutulsun (haftada 1-2 kaliteli bulgu, günde 10 gürültü değil).
## BİTTİ SAYILIR
Üretilen fırsatların en az yarısı kullanıcı tarafından 'ilgi çekici' bulunuyor.
İstatistiksel olarak anlamsız bulgular filtreleniyor.
12.2DATAP0Dijital İkiz: finans + tedarik + İK + pazarlama + dış veri (kur, emtia, enflasyon) tek
simülasyon grafında birleşir
## AMAÇ
Şirketin bir bütün olarak simüle edilebilmesi.
## NASIL
Değişken grafiği: finans, tedarik, üretim, satış, İK ve dış değişkenler (kur, emtia) arasındaki bağımlılıklar.
Bağımlılıklar kullanıcıyla birlikte tanımlanır (LLM uydurmaz) ve zamanla kalibre edilir.
Simülasyon motoru: bir değişkeni değiştir, zincir boyunca etkiyi hesapla.
Kalibrasyon: geçmiş verilerle model doğrulaması (geçmişi doğru tahmin ediyor mu?).
Belirsizlik bandı her çıktıda gösterilir.
## BİTTİ SAYILIR
Model geçmiş bir dönemi makul hata payıyla yeniden üretebiliyor.
Simülasyon çıktısı her zaman belirsizlik bandıyla sunuluyor.
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-11.7TEMELToplantı biter5 dakika içinde karar, aksiyon, sorumlu ve tarih listesi
hazırdır.
UC-11.8TEMELToplantıda bir karar alınırKarar Kaydı'na aday olarak düşer ve onaya sunulur.
UC-11.9REGRESYONToplantı transkripti hafızaya yazılırken
denetlenir
Her cümle değil, yalnız karar/taahhüt/tanım kaydedilmiştir
(seçici hafıza).
UC-11.10TEMELToplantıda veriyle çelişen bir iddia
söylenir ('bütçeyi aşmaz')
Diskret, kanıt bağlantılı uyarı çıkar; toplantı bölünmez.
UC-11.11SINIRBelirsiz bir ifade söylenirSistem emin değilse sessiz kalır; yanlış alarm üretmez.
UC-11.12TEMELBir karar tartışılırRed Team 3-5 maddelik kör nokta listesi üretir; her madde
kanıta bağlıdır (genel laf değil).
UC-11.13GÜVENLİKRed Team çıktısının dili denetlenirKişiyi değil kararı hedefler; saygılı ama net.
UC-11.14TEMELZarar eden projeye ek bütçe kararı verilirBatık maliyet yanılsaması tespit edilir ve gerekçesiyle
bildirilir.
UC-11.15GÜVENLİKKarşıt ajan bir kararı engellemeye çalışırEngelleyemez; yalnız uyarır. Karar insanındır.
## FAZ 12
v6
## BE25Y2
## BE11R3
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE25Y4Ç14
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası73 / 126

12.3LLMP0Siyah Kuğu / War Room: ekstrem senaryo stres testi (kur şoku, tedarikçi iflası, iki büyük
müşteri kaybı) → dayanma süresi + hazır B planı memosu
## AMAÇ
Kriz gelmeden hazırlıklı olmak.
## NASIL
Senaryo kütüphanesi: kur şoku, ana tedarikçi kaybı, büyük müşteri kaybı, hammadde fiyat sıçraması, talep çöküşü.
Her senaryo için: nakit dayanma süresi, kritik eşikler, kırılma noktaları.
Otomatik B planı taslağı: hangi ödemeler ötelenebilir, hangi maliyetler kısılabilir.
Canlı kriz paneli: mevcut dayanıklılık göstergeleri.
Senaryolar periyodik yeniden çalıştırılır (durum değiştikçe).
## BİTTİ SAYILIR
'Kur %25 artarsa kaç gün dayanırız' sorusu sayısal cevap alıyor.
B planı taslağı somut kalemler içeriyor.
12.4LLMP1Tarihsel karşı-olgusal replay: 'şunu yapmasaydık bugün nerede olurduk' — geçmiş kararların
gerçek faturası
## AMAÇ
Geçmiş kararların gerçek faturasını ölçmek.
## NASIL
Geçmiş bir karar noktası seç; alternatif senaryoyu simüle et.
Fark analizi: gerçekleşen ile alternatifin farkı.
DİKKAT: bu bir tahmindir, kesinlik iddiası yok — belirsizlik bandıyla sun.
Amaç suçlama değil öğrenme; dil buna göre olsun.
Öğrenilen ders karar şablonlarına (6B.12) geri beslensin.
## BİTTİ SAYILIR
Karşı-olgusal analiz belirsizlik bandıyla sunuluyor.
Çıktı suçlayıcı değil öğretici dilde.
12.5GOVP1Founder Legacy Vault: kurucu/CEO ilkeleri, kriz refleksleri, kırmızı çizgileri tescillenir → yıllar
sonra vizyon sapmasını engeller (kişisel veri yönetişimi ve sahiplik izniyle)
## AMAÇ
Kurumsal aklın kişilere bağımlı olmaktan çıkarılması.
## NASIL
Kurucu/üst yönetici ile yapılandırılmış görüşmeler: ilkeler, kırmızı çizgiler, kriz refleksleri, öncelik sıralaması.
Geçmiş kararlar ve gerekçeleri arşivden toplanır.
Bu bilgi 'kurumsal ilkeler' katmanına yazılır ve kararlarda referans gösterilir.
Kişisel veri yönetişimi: ilgili kişinin açık onayı, erişim kontrolü, silme hakkı.
Kullanım: 'kurucu bu tip kararlarda şu ilkeyi uygulamıştı' şeklinde referans (taklit değil).
## BİTTİ SAYILIR
Yeni bir yönetici geçmiş karar mantığını sistemden öğrenebiliyor.
İlgili kişinin onayı ve hakları korunuyor.
12.6GOVP1Gölge Kurul Üyesi: ego ve hiyerarşiden bağımsız, risk-ağırlıklı AI görüşü + gerekçe. VETO
DEĞİL — 'yüksek risk → ikinci C-level imzası gerekir' tetikleyicisi (hukuken uygulanabilir tasarım)
## AMAÇ
Kurul kararlarına bağımsız, veri temelli bir görüş eklemek — ama hukuki sınırı aşmadan.
## NASIL
Karar oylanmadan önce sistem bağımsız değerlendirme üretir: risk skoru, geçmiş benzer kararların sonucu, finansal
etki.
Çıktı bir 'görüş' olarak sunulur, oy veya veto DEĞİL.
Yüksek risk skorunda mekanizma: 'ikinci C-level imzası gerekir' iş akışı tetiklenir (kurumsal yönetişim kuralı).
Değerlendirme ve gerekçe karar kaydına eklenir.
Sistem hiçbir koşulda kararı engellemez; yalnız süreci zorlaştırır (yönetişim aracı).
## BİTTİ SAYILIR
Yüksek riskli kararlarda ikinci onay akışı tetikleniyor.
Hiçbir yerde sistemin 'veto ettiği' ifadesi geçmiyor.
## BE25Y4Y3
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE25BE19
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE28BE20
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE24BE19
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
DİMA · 0→100 Görev Takip Dosyası74 / 126

12.7DATAP1Kolektif Sektör Zekâsı (hive benchmark): 'su tüketiminiz benzer ölçekli fabrikaların %18
üstünde' — yalnız anonim + toplulaştırılmış, k-anonimlik eşiği, opt-in ve sözleşme maddesi
## AMAÇ
Müşterilere sektör kıyası sunarken kimsenin verisini ifşa etmemek.
## NASIL
Katılım opt-in; sözleşmede anonim toplulaştırma maddesi.
Yalnız toplulaştırılmış istatistik (ortalama, medyan, çeyreklik) paylaşılır.
k-anonimlik: minimum katılımcı sayısı altında kırılım yayınlanmaz.
Çıktıda kaç firmadan hesaplandığı belirtilir.
Opt-out anında katkı havuzdan çıkarılır.
Hukuk onayı olmadan yayına alınmaz.
## BİTTİ SAYILIR
Tek bir müşterinin verisi kıyastan geri çıkarılamıyor.
Kıyas çıktısında örneklem büyüklüğü görünüyor.
12.8GOVP0Sürekli Mevzuat Kalkanı: Resmî Gazete, KVKK/BDDK kararları, AB direktifleri taranır → Policy-
as-Code ile kıyaslanır → etkilenen kural/fiyat/süreç uyarısı
## AMAÇ
Mevzuat değişikliklerini kaçırmamak.
## NASIL
Kaynaklar: Resmî Gazete, KVKK/BDDK kararları, AB direktifleri, sektör düzenlemeleri.
Tarama ve sınıflandırma: bu değişiklik hangi süreçlerimizi ilgilendiriyor?
Etki analizi: mevcut Policy-as-Code kurallarıyla ve iş süreçleriyle karşılaştır.
Uyarı: 'yeni mevzuat X kuralınızı etkiliyor, güncellenmesi gerekiyor'.
DİKKAT: hukuki tavsiye DEĞİL, bilgilendirmedir — bu ibare her çıktıda bulunmalı.
## BİTTİ SAYILIR
İlgili bir mevzuat değişikliği 48 saat içinde tespit ediliyor.
Çıktıda 'hukuki tavsiye değildir' ibaresi var.
12.9GOVP1Örgütsel sağlık radarı: departmanlar arası iletişim tonu — YALNIZ anonim + kümelenmiş, kişi
bazlı asla; çalışan aydınlatma ve hukuki dayanak zorunlu
## AMAÇ
Kurumsal iklimi ölçerken kişiyi hedef almamak.
## NASIL
YALNIZ anonim ve kümelenmiş analiz: departman düzeyinde iletişim tonu trendi.
Kişi bazlı skor, kişi bazlı rapor, kişi tespiti KESİNLİKLE YOK.
Minimum grup büyüklüğü (ör. 10 kişi) altında analiz yapılmaz.
Çalışan aydınlatma metni ve açık hukuki dayanak zorunlu; sendika/temsilci bilgilendirmesi önerilir.
Çıktı: 'X ve Y departmanları arasında iletişim tonu sertleşti' düzeyinde, isim yok.
Hukuk onayı olmadan devreye alınmaz.
## BİTTİ SAYILIR
Hiçbir çıktıdan kişi kimliği çıkarılamıyor.
Hukuki dayanak ve çalışan bilgilendirmesi tamamlanmış.
## BE26Y10BE20
## 1.
## 2.
## 3.
## 4.
## 5.
## 6.
## •
## •
## BE27F25Y13
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE24F8F25
## 1.
## 2.
## 3.
## 4.
## 5.
## 6.
## •
## •
DİMA · 0→100 Görev Takip Dosyası75 / 126

12.10DATAP2Multimodal saha katmanı: fotoğraf/görüntü (raf, hasar, rakip fiyat etiketi) + IoT akışları →
semantik katmana bağlanır
## AMAÇ
Fiziksel dünyadan gelen veriyi sisteme katmak.
## NASIL
Görsel girdi: saha fotoğrafı (raf durumu, hasar, rakip fiyat etiketi), üretim kamerası.
Görüntü analizi ile yapılandırılmış veri çıkar (fiyat, ürün, durum).
IoT akışları: sayaç, sensör verisi → zaman serisi katmanına.
Çıkarılan bilgi güven seviyesiyle etiketlenir (görüntü tanıma kesin değildir → PROBABILISTIC).
Kişisel görüntü işleme yapılmaz (yüz, plaka maskelenir).
## BİTTİ SAYILIR
Saha fotoğrafından fiyat bilgisi çıkarılıp karşılaştırma yapılabiliyor.
Görüntülerde kişisel veri maskeleniyor.
12.11DATAP1Durum çatallama (state forking): şirket durumu bir anda dondurulur ve paralel
senaryolarda koşturulur (Git dalı gibi); canlı veriye dokunmadan 'evren A / evren B' kıyası
12.12GOVP2Kök motor gözlemevi: altı çekirdek motorun (nedensellik, telos, refleks, hakem, dikkat,
çatallama) kendi sağlığını ve birbirine etkisini izleyen üst katman
## Y14Y11BE22
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## R66BE25
## R67BE16
✅ KABUL TESTLERİ / USE-CASE'LER 22 senaryo · TEMEL: 7 · REGRESYON: 3 · GÜVENLİK: 9 · SINIR: 3
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-12.1TEMELGece taraması çalışırSabah en yüksek etkili 1-3 fırsat bildirimi gelir (günde 10
gürültü değil).
UC-12.2REGRESYONÜretilen fırsatlar değerlendirilirEn az yarısı kullanıcı tarafından 'ilgi çekici' bulunur; istatistiksel
anlamsız bulgular filtrelenmiştir.
UC-12.3REGRESYONDijital ikiz geçmiş bir dönemle test
edilir
Model o dönemi makul hata payıyla yeniden üretebilir.
UC-12.4REGRESYONHerhangi bir simülasyon çıktısı
incelenir
Her zaman belirsizlik bandıyla sunulur.
UC-12.5TEMEL'Kur %25 artarsa kaç gün dayanırız?'
sorulur
Sayısal dayanma süresi + somut kalemler içeren B planı taslağı
gelir.
UC-12.6TEMELKarşı-olgusal analiz istenir ('şunu
yapmasaydık?')
Belirsizlik bandıyla ve öğretici (suçlayıcı olmayan) dille sunulur.
UC-12.7GÜVENLİKFounder Cortex kurulurken
denetlenir
İlgili kişinin açık onayı alınmış; erişim kontrolü ve silme hakkı
tanımlı.
UC-12.8TEMELYeni yönetici geçmiş bir karar
mantığını sorar
Kurucunun ilkesi referans olarak gösterilir (taklit değil, atıf).
UC-12.9GÜVENLİKGölge kurul değerlendirmesi
denetlenir
Hiçbir yerde 'veto' ifadesi yok; yüksek riskte yalnız ikinci imza
akışı tetikleniyor.
UC-12.10GÜVENLİKSektör kıyasında tek müşteri verisi
geri çıkarılmaya çalışılır
Anonimlik testi başarısız kılar; k-anonimlik eşiği korur.
UC-12.11TEMELİlgili bir mevzuat değişikliği
yayınlanır
48 saat içinde tespit edilir; etkilenen kural bildirilir.
UC-12.12GÜVENLİKMevzuat uyarısı incelenir'Hukuki tavsiye değildir' ibaresi bulunur.
UC-12.13GÜVENLİKÖrgütsel sağlık çıktısı denetlenirHiçbir çıktıdan kişi kimliği çıkarılamaz; minimum grup
büyüklüğü korunur; çalışan bilgilendirmesi tamamlanmış.
UC-12.14GÜVENLİKSaha fotoğrafı işlenirYüz ve plaka gibi kişisel veriler maskelenir.
UC-12.15SINIRFırsat motoru aynı bulguyu ikinci gün
tekrar üretir
Tekrar bildirilmez; kullanıcı 'ilgilenmiyorum' derse bir daha
gösterilmez.
UC-12.16GÜVENLİKDijital ikiz çıktısı denetlenirGirdi varsayımları ve kalibrasyon tarihi görünür; kara kutu
değildir.
DİMA · 0→100 Görev Takip Dosyası76 / 126

## İLERİ İŞ MOTORLARI
Çekirdek olgunlaştıktan sonra üstüne binen, tek başına satın alma sebebi olabilecek yüksek değerli motorlar. Hepsi mevcut
katmanların (nedensellik, telos, karar motoru, hafıza) uygulamasıdır — yeni mimari gerektirmez.
12B.1LLMP1Pazarlık hazırlık motoru: tedarikçi performansı + piyasa endeksi + stok aciliyeti + geçmiş
anlaşma şartları → pazarlık stratejisi ve karşı teklif taslağı
12B.2LLMP1Marj kalkanı / dinamik fiyat önerisi: maliyet bileşeni (enerji, hammadde, kur) değişince marjı
hedefte tutacak fiyat revizyonu önerilir — uygulama insan onayıyla
12B.3LLMP1Micro-churn radarı: sipariş sıklığı, ödeme hızı, iletişim tonu ve ürün çeşitliliğindeki daralma
birlikte izlenir; sessiz kayıp sipariş kesilmeden aylar önce görülür
12B.4LLMP1Sözleşme risk eleği: yeni sözleşmedeki cezai şart ve teslimat taahhüdü, şirketin gerçek
performans geçmişiyle kıyaslanır; yıllık risk tutarı hesaplanır
12B.5LLMP2İç proje/fikir eleği: yatırım fikri nakit akışı, kapasite, geçmiş getiri ve stratejik hedef
kısıtlarıyla test edilir; onay/erteleme gerekçesiyle döner
12B.6DATAP2Görsel saha denetçisi: saha fotoğrafı ve kamera akışından istif hatası, hasar, İSG ihlali ve
raf düzeni tespiti; iç iş emrine bağlanır
12B.7LLMP2Yetenek boşluğu ve halef planı: iş yükü artış hızı, tamamlama süreleri ve devir oranından
kadro darboğazı öngörüsü
12B.8LLMP1Nakit arbitrajı: atıl nakit, erken ödeme iskontosu ve alternatif getiri kıyaslanır; en yüksek
getirili kullanım önerilir
12B.9GOVP1Suistimal ve mükerrer ödeme dedektifi: tutar, VKN, IBAN, açıklama metni ve onay zinciri
sürekli çapraz test edilir; şüpheli işlemde ödeme durdurulur ve iç denetime düşer
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-12.17SINIRSiyah kuğu senaryosunda veri
eksiktir
Sistem 'hesaplanamıyor' der; eksik veriyi belirtir.
UC-12.18GÜVENLİKFounder Cortex kaydı sorgulanırKaynağı, tarihi ve kimin onayladığı görünür.
UC-12.19SINIRMevzuat taraması ilgisiz bir
değişiklik yakalar
Gürültü filtrelenir; yalnız şirketin süreçlerini etkileyenler
bildirilir.
UC-12.20TEMELŞirket durumu dondurulup iki
senaryo koşturulur (12.11)
Canlı veri etkilenmez; evren A ve evren B sonuçları yan yana
kıyaslanabilir.
UC-12.21GÜVENLİKÇatallanmış evrende yapılan işlem
canlıya sızmaya çalışır
İzole kalır; yalnız açık onayla ana dala uygulanabilir.
UC-12.22TEMELKök motor gözlemevi açılır (12.12)Altı çekirdek motorun sağlığı, gecikmesi ve birbirine etkisi tek
panelde görünür.
## FAZ 12B
dikey zekâ
## R78BE19
## R79Y4
## R80Y16
## R81Y13
## R82BE19
## R83Y14
## R84Y17
## R85Y3
## R86F25
✅ KABUL TESTLERİ / USE-CASE'LER 9 senaryo · TEMEL: 6 · GÜVENLİK: 3
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-12B.1TEMELTedarikçi zam bildirirStok durumu, piyasa endeksi ve geçmiş şartlar birleştirilip
pazarlık stratejisi ve karşı teklif taslağı üretilir.
UC-12B.2TEMELEnerji maliyeti gece artarEtkilenen ürünlerin marjı hesaplanır; hedefin altına düşenler için
fiyat revizyon önerisi çıkar.
DİMA · 0→100 Görev Takip Dosyası77 / 126

Ar-Ge / Vizyon Tier — taahhüt değil keşif
Bu fazdaki kalemler yol haritası taahhüdü DEĞİL, araştırma kuyruğudur: teknik olgunluğu, hukuki zemini veya ticari talebi
henüz kanıtlanmamıştır. Müşteriye vaat edilmez; fizibilite kanıtlanırsa üst fazlara terfi eder.
13.1ENGP2Zero-Knowledge B2B sözleşme mutabakatı: iki taraf ticari sırrını açmadan sözleşme şartının
gerçekleşmesini doğrular
## AMAÇ
İki şirketin ticari sırrını açmadan sözleşme şartını doğrulaması (araştırma).
## NASIL
Fizibilite: hangi ZK protokolü, hangi kütüphane, hesaplama maliyeti nedir?
Basit bir kanıtlama senaryosu prototipi (teslimat tarihi doğrulaması).
Hukuki geçerlilik araştırması: ZK kanıtı sözleşme uyuşmazlığında delil sayılır mı?
Karar: fizibil ise Faz 12'ye terfi, değilse arşivle.
## BİTTİ SAYILIR
Fizibilite raporu ve prototip sonucu mevcut.
Devam/durdur kararı verilmiş.
13.2LLMP2M&A / Due Diligence dedektifi: hedef şirketin ham finansalları çapraz kontrol → mükerrer
fatura, ilişkili taraf, gizli borç sinyalleri
## AMAÇ
Şirket satın alma incelemesini hızlandırmak (araştırma).
## NASIL
Hedef şirket verilerinin güvenli alımı ve izolasyonu (üçüncü taraf gizli verisi!).
Çapraz kontroller: mükerrer fatura, ilişkili taraf işlemleri, olağandışı büyüme, nakit-kâr uyumsuzluğu.
Çıktı: risk işaretleri listesi — SONUÇ DEĞİL, İNCELEME REHBERİ (hukuki sorumluluk).
Gizlilik sözleşmesi ve veri imha akışı zorunlu.
## BİTTİ SAYILIR
Prototip bilinen anomalileri test verisinde yakalıyor.
Hukuki çerçeve (NDA, imha) tanımlanmış.
IDTipKullanıcı ne yapar / tetikleyiciSistem ne yapmalı (beklenen sonuç)
UC-12B.3GÜVENLİKFiyat revizyonu otomatik
uygulanmaya çalışılır
Uygulanmaz; insan onayı zorunludur.
UC-12B.4TEMELMüşterinin sipariş sıklığı yavaşlarSipariş kesilmeden önce churn riski uyarısı üretilir ve benzer
geçmiş vakalarla desteklenir.
UC-12B.5TEMELYeni sözleşme yüklenirCezai şart, şirketin gerçek teslimat performansıyla kıyaslanır; yıllık
risk tutarı hesaplanır.
UC-12B.6TEMELYatırım fikri sunulurNakit, kapasite ve strateji kısıtlarıyla test edilir; onay veya
erteleme gerekçesiyle döner.
UC-12B.7GÜVENLİKSaha fotoğrafı işlenirKişisel veriler (yüz, plaka) maskelenir; yalnız operasyonel bulgu
raporlanır.
UC-12B.8TEMELAtıl nakit tespit edilirErken ödeme iskontosu ile alternatif getiri kıyaslanır; en yüksek
getirili seçenek gerekçesiyle önerilir.
UC-12B.9GÜVENLİKMükerrer fatura ve IBAN değişikliği
aynı anda görülür
Ödeme durdurulur, iç denetime bildirim düşer, olay contract'a
bağlanır.
## FAZ 13
Ar-Ge
## BE26
## 1.
## 2.
## 3.
## 4.
## •
## •
## BE25Y19
## 1.
## 2.
## 3.
## 4.
## •
## •
DİMA · 0→100 Görev Takip Dosyası78 / 126

13.3LLMP2Dinamik performans & prim adalet motoru: kârlılık, elde tutma, bölge zorluğu ve iş birliği
dahil canlı skor (İK hukuku ve iş barışı riski yüksek — önce hukuk)
## AMAÇ
Performans değerlendirmesini çok boyutlu hale getirmek (yüksek riskli, dikkatli).
## NASIL
Boyutlar: satış tutarı, kârlılık, müşteri elde tutma, bölge zorluğu, iş birliği.
Şeffaflık zorunlu: skorun nasıl hesaplandığı çalışana açık olmalı.
İŞ HUKUKU RİSKİ YÜKSEK: ücret/prim etkisi olan otomatik değerlendirme öncesi hukuk görüşü şart.
İtiraz mekanizması ve insan gözden geçirmesi zorunlu.
Ayrımcılık testi: skor belirli gruplara sistematik dezavantaj yaratıyor mu?
## BİTTİ SAYILIR
Hukuk görüşü alınmadan devreye alınmıyor.
Ayrımcılık testi yapılmış ve belgelenmiş.
13.4ENGP2ZKP tabanlı kolektif havuz: kriptografik sıfır-bilgi kanıtıyla sektör karşılaştırması
## AMAÇ
Kriptografik olarak güvenli sektör havuzu (araştırma).
## NASIL
ZKP tabanlı toplulaştırma protokolü araştırması.
Performans testi: gerçekçi veri hacminde çalışıyor mu?
12.7'deki basit anonim yaklaşımla karşılaştır: ek karmaşıklık değer katıyor mu?
Karar: değer katıyorsa terfi, katmıyorsa 12.7 yeterli.
## BİTTİ SAYILIR
Karşılaştırmalı analiz tamamlanmış ve karar verilmiş.
13.5LLMP2Tam otonom operatör: onay eşiği altındaki rutin aksiyonları insan onayı olmadan yürütme
(yalnız kanıtlanmış güven ve sözleşmesel yetkiyle)
## AMAÇ
Rutin aksiyonların insan onayı olmadan yürütülmesi (en riskli fikir — dikkatli).
## NASIL
ÖN ŞART: 6 ay kesintisiz doğru öneri geçmişi ve müşterinin yazılı yetkilendirmesi.
Yalnız düşük etkili, geri alınabilir, tutar/kapsam sınırlı aksiyonlar.
Her otomatik aksiyon anında bildirilir ve geri alınabilir.
Otomatik durdurma (kill switch) ve günlük limit.
DİKKAT: bu, 'Dima karar vermez' ilkesiyle gerilim yaratır — konumlandırma ve sözleşme dili yeniden değerlendirilmeli.
## BİTTİ SAYILIR
Yetkilendirme, limit ve geri alma mekanizmaları tanımlanmış.
İlke gerilimi üst yönetimce değerlendirilmiş ve karara bağlanmış.
## BE24Y17
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## BE26
## 1.
## 2.
## 3.
## 4.
## •
## Y8BE19
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
✅ KABUL TESTLERİ / USE-CASE'LER 5 senaryo · SINIR: 2 · GÜVENLİK: 3
IDTip
Kullanıcı ne yapar /
tetikleyici
Sistem ne yapmalı (beklenen sonuç)
UC-13.1SINIRZK sözleşme doğrulama
prototipi test edilir
Fizibilite raporu üretilir ve devam/durdur kararı verilir (taahhüt yok).
UC-13.2GÜVENLİKM&A analizi için hedef şirket
verisi yüklenir
NDA ve veri imha akışı tanımlıdır; çıktı 'sonuç' değil 'inceleme rehberi'
olarak sunulur.
UC-13.3GÜVENLİKPerformans skor motoru
değerlendirilir
Hukuk görüşü alınmadan devreye alınmaz; ayrımcılık testi yapılmış ve
belgelenmiştir.
UC-13.4SINIRZKP havuzu 12.7'deki basit
yaklaşımla karşılaştırılır
Ek karmaşıklığın değer katıp katmadığına dair karşılaştırmalı analiz
mevcuttur.
UC-13.5GÜVENLİKTam otonom aksiyon önerisi
değerlendirilir
Yetkilendirme, limit, kill switch ve geri alma tanımlanmadan açılmaz;
'Dima karar vermez' ilkesiyle gerilim üst yönetimce karara bağlanmıştır.
DİMA · 0→100 Görev Takip Dosyası79 / 126

## SEKTÖREL UÇTAN UCA KABUL SENARYOLARI
Faz testleri tek tek yeteneği doğrular; bu bölüm ürünü gerçek bir kullanıcının gerçek işi üzerinden baştan sona sınar. Her
senaryo use-case külliyatındaki bir kurguya karşılık gelir (kaynak sütunu) ve birden çok fazın birlikte çalışmasını gerektirir.
Sürüm çıkışlarında (v1, v2, v3...) ilgili senaryolar yeniden koşulmalıdır.
IDSektör/RolUçtan uca akışBeklenen sonuçKaynak
E2E-01PerakendeBölge müdürü kendi bölgesinin
karnesini ister, en zayıf şubeye
iner, personel devriyle ilişkisini
sorar
Yalnız kendi bölgesini görür (RLS); kırılım doğru;
korelasyon 'nedensellik değildir' notuyla
sunulur
## S13 · F7,F14,F3
E2E-02PerakendeMağaza müdürü AI kapalı modda
günlük kapanış raporunu
menüden alır
LLM çağrısı yapılmaz; sonuç altın rozetli ve
%100 deterministik
## S14 · F9,F2
E2E-03ÜretimGece vardiyasında fire yüksek
sorulur; makine mi operatör mü
diye derinleşilir; bakım geçmişi
istenir
Varyans ayrıştırma tek makinede yoğunlaşmayı
bulur; bakım önerisi kanıtla gelir
## S18 · Y5,F3,F12
E2E-04ÜretimOEE 4 puan düştü sorulur;
bileşen → duruş → iplik lotu →
tedarikçi zinciri izlenir
Zincirin her adımı kanıtlı; tedarikçi skor kartına
işlenir; karbon etkisi birlikte raporlanır
## S132 ·
## Y5,Y17,Y25,Y22
E2E-05MuhasebeMali müşavir 40 mükellefinde
nakit riski kırmızı olanları
sorgular
Portföy görünümü çalışır; şirketler arası veri
sızıntısı olmaz
## S26 · Y18,F7
E2E-06Muhasebe8 haftalık nakit akışı istenir, riskli
hafta işaretlenir, ödeme öteleme
senaryosu denenir
Projeksiyon aralıklı gelir; senaryo deterministik
hesaplanır; öneri tedarikçi vade geçmişine
dayanır
## S29 · Y3,Y4,F12
E2E-07BankaDenetçi ekrandaki bir rapor
sayısının kanıt zincirini ister
QueryContract açılır; yeniden koşulur; hash
tutar
## S34 · F6
E2E-08BankaRisk müdürü NPL artışını sorar,
kredi verilme çeyreğine göre
kırar, politika değişimini sorgular
Vintage/kohort eğrileri doğru; politika kaydı
bağlamla getirilir
## S35 · Y16,F3,F12
E2E-09BankaMüşteri temsilcisi liste isterTCKN/telefon otomatik maskeli; yönetici rolünde
açık ve erişim loglanır
## S36 · F8,F7
E2E-10KamuBelediye müdürü şikayet artışını
sorar, mahalle kırılımına iner,
ekip planına çevirir
Tam on-prem çalışır; vatandaş verisi maskeli;
çıktı üst yazıya hazır
## S46 · F9,F21,F8
E2E-11EğitimRehberlik erken uyarı taraması
haftalık koşar
Not+devamsızlık+katılım birleşik risk sinyali
üretir; öğrenci kimliği yetkisiz role kapalı
## S50 · F11,Y2,F17
E2E-12SağlıkBaşhekim yatak doluluğunu
sorar, taburcu darboğazını bulur,
vizit saati simülasyonu ister
Hasta verisi kurum dışına çıkmaz; simülasyon
kazanılacak yatak-günü sayısal verir
## S59 · Y5,Y4,F21
E2E-13SağlıkKritik stok + miadı yaklaşan
ilaçlar sorgulanır
Çift koşullu izleme çalışır; eşik aşımında
otomatik uyarı üretilir
## S57 · Y13,Y2,F12
E2E-14LojistikGeciken siparişlerin nedeni
sorulur, taşıyıcı karnesi çıkarılır,
sözleşme için veri özeti istenir
Neden ayrıştırma doğru; skor kartı üretilir; dışa
aktarım maskeleme kurallarına uyar
## S64 · Y5,Y17,F19
E2E-15İKDevir artışı sorulur, tek
yöneticide yoğunlaştığı bulunur,
çıkış görüşme notları taranır
Notlar yerel işlenir; tema özetleri isimsiz;
aksiyon planı taslağı üretilir
## S70 · Y6,F8,F12
E2E-16SatışSahadaki temsilci telefondan
sesle müşteri bakiyesi sorar
Yalnız kendi müşterilerini görür; cevap 3
saniyede kart formatında gelir
## S75 · Y20,F7
E2E-17PazarlamaBütçe dağıtımı sorulur, kanal
kaydırma senaryosu denenir
Marjinal getiri kıyası yapılır; projeksiyon
belirsizlik aralığıyla ve 'tahmindir' şerhiyle
sunulur
## S81 · Y4,Y3,F5
52 entegrasyon testi
DİMA · 0→100 Görev Takip Dosyası80 / 126

IDSektör/RolUçtan uca akışBeklenen sonuçKaynak
E2E-18Çağrı
merkezi
Memnuniyet düşüşü sorulur;
transkriptlerden konu dağılımı
çıkarılır; operasyona bildirim
gider
Transkript yerel işlenir; kök neden tek kargo
firmasında yoğunlaşır; webhook tetiklenir
## S85 · Y5,Y6,Y12
E2E-19SaaSNRR düşüşü segment ve pakete
göre kırılır; fiyat değişikliği
simüle edilir
Kohort analizi doğru; simülasyon riskli
varsayımları listeler
## S90 · Y4,F3
E2E-20Veri ekibiMetrik tanımı değişirDrift tespit edilir; etkilenen panolar ve
pattern'lar listelenir; yeniden doğrulama
sunulur
## S94 · F26,F23
E2E-21CEOKapasite oturumu: Q4 taşar mı →
vardiya/fason → nakit → kur
duyarlılığı → karar memosu
Zincir boyunca bağlam korunur; her adım
kanıtlı; memo 2 sayfa ve kaynak bağlantılı
## S101 ·
## Y4,Y3,F13,F6
E2E-22CEO'Bugün gösterdiklerinin ne
kadarında yapay zeka karar
verdi?' sorulur
Yol dağılımı gerçek loglardan gelir (ör. %71
altın, %22 gümüş, %7 bronz)
## S60(demo) · F6
E2E-23Tekstilkg kumaş başına CO2e sorulurKapsam 1/2 ayrımıyla, kullanılan emisyon
faktörleri görünür şekilde hesaplanır
## S111 · Y22,Y14
E2E-24TekstilZDHC atıksu limit aşımı
sorgulanır
Limit kütüphanesiyle kıyaslanır; aşım günleri ve
partileri listelenir; uyarı üretilir
## S113 · F25,Y2
E2E-25Tekstil'%40 geri dönüştürülmüş' iddiası
doğrulanır
Satın alınan GRS elyaf ile üretilen ürün bileşimi
mutabakatı yapılır; greenwashing riski kanıtla
ölçülür
## S116 · F6,F1
E2E-26TekstilAB sevkiyatı için CBAM gömülü
emisyon dökümü istenir
Sipariş bazlı tahsis yapılır; faktörler ve yöntem
raporda görünür
## S117 · Y24,Y22
E2E-27TekstilSKU için Dijital Ürün Pasaportu
veri paketi derlenir
Elyaf, üretim yeri, kimyasal sınıfı, ayak izi, geri
dönüşüm talimatı tek pakette; QR'a hazır
## S118 · Y23,F6
E2E-28TekstilDeadstock listesi ve upcycling
adayları istenir
6+ ay hareketsiz kumaşlar renk/kompozisyon/
metrajla listelenir; koleksiyon önerisi üretilir
## S122 · F12,F1
E2E-29TekstilMarka denetimi 2 hafta sonra:
denetim dosyası hazırlanır, zayıf
noktalar ve CAPA istenir
Kayıtlı skill koşar; zayıf alanlar tespit edilir; iki
dilli, her sayısı kanıt bağlantılı dosya üretilir
## S128 · F17,F6,Y21
E2E-30Tekstil/OEEKarbon-başabaş OEE eğrisi ve
yatırım önceliği istenir
Makine bazlı eğri çıkar; hangi OEE'nin altında
karbon hedefi aşıldığı sayısal verilir
## S134 · Y22,Y26
E2E-31İş bağlamıKurulumda iş tanımı sihirbazı
çalışır, süreç haritası ve
sorumluluklar çıkarılır, sonra
'teslimat neden gecikiyor' sorulur
Sistem süreç haritasındaki darboğazı bulur;
departman sorumlusunu bilir ve doğru kişiye
bildirim gider
## 3B.1 · 3B.3 · 6.13
E2E-32İş bağlamıBir tedarikçi sözleşmesi yüklenir;
60 gün sonra yenileme tarihi
yaklaşır
Takvime düşer, 90 gün kala hatırlatma üretilir,
sözleşme risk eleğinden geçirilir ve satınalma
podu bilgilendirilir
## 3B.2 · 3B.3 · 12B.
## 4
E2E-33İş bağlamıBir iş bilgisinin tazelik SLA'sı
geçer, sahibi 30 gün cevap
vermez
Bilgi 'bayat' işaretlenir, kullanan cevaplarda
güven skoru düşer, ağırlık azaltılır ve yöneticiye
eskalasyon yapılır
## 3B.4 · 5.12 · 7.9
E2E-34Görev
motoru
Anomali tespit edilir → sistem
görev önerir → chat'ten onaylanır
→ sorumlu atanır → 2 hafta
hareketsiz kalır
Görev bulguya bağlı olarak doğar, dış araca
senkronlanır, tıkanma tespit edilir ve sahibine
bildirilir
## 8.10 · 3B.7 · 3B.8
## · 3B.9 · 9.12
E2E-35Görev
motoru
Toplantıda 'yarın gönderirim'
denir
Taahhüt yakalanır, onaya sunulur, göreve
dönüşür ve ertesi sabah brifingde 'bugün
bitmesi gerekenler' altında görünür
## 11.4 · 3B.10 · 3B.
## 11
E2E-36Sabah
ritüeli
Sabah 08:00 brifingi üretilirDün biten/aksayan işler, bugünkü görevler,
yarının riskleri, gece taramasından çıkan fırsat
ve bir öneri — 30 saniyede okunur, kanaldan
düşer
## 3B.11 · 3B.12 ·
## 12.1
DİMA · 0→100 Görev Takip Dosyası81 / 126

IDSektör/RolUçtan uca akışBeklenen sonuçKaynak
## E2E-37ERP
sembiyozu
Sahadan fatura fotoğrafı
gönderilir → taslak üretilir → limit
ihlali tespit edilir → düzeltilip
onaylanır
OCR alanları çıkarır, düşük güvenli alanlar
işaretlenir, politika ihlali yazma öncesi
yakalanır, onay sonrası ERP'ye işlenir ve
contract'a bağlanır
## 8B.2 · 8B.3 · 8B.4
## · 8B.5
## E2E-38ERP
sembiyozu
Aynı kayıt hem ERP formundan
hem Dima'dan girilir
Süre karşılaştırması raporlanır; 'kaç kat hızlı'
iddiası sayısal kanıta bağlanır
## 8B.6 · 8.17
E2E-39FrontDeskMüşteri WhatsApp'tan katalog
sorar, fiyat öğrenir, randevu alır,
sonra web'den bakiyesini sorar
Kimlik iki kanalda birleştirilir; katalog kamu
şemasından gelir; randevu kapasite-farkında
verilir; bakiye ancak OTP sonrası ve yalnız
kendi satırları gösterilir
## 9B.4 · 9B.5 · 9B.8
## · 9B.3
E2E-40FrontDeskMüşteri gerginleşir ve sistem
çözemez
Canlı temsilciye devredilir; temsilcinin ekranına
konuşma özeti ve sancı analizi düşer; olay
müşteri sesi raporuna anonim olarak girer
## 9B.7 · 9B.9
E2E-41FrontDeskDış kanaldan iç maliyet verisi
sorulmaya çalışılır
Şema seviyesinde erişim olmadığı için sistem o
veriyi hiç göremez; sızıntı mimari olarak
imkânsızdır
## 9B.1 · 9B.2 · 2.12
E2E-42Kök
motorlar
Satış vade uzatmak, finans nakit
korumak ister; karar kurula gider
Hakem nicel kısıtları optimize eder, tek uzlaşma
önerisi üretir, Delta-KPI ile ana hedefe katkısı
tartılır, karar kaydına imzalanır
## 6B.14 · 6B.13 ·
## 6B.8
E2E-43Kök
motorlar
Patron 'tüm ödemeleri durdur'
talimatı verir, sözleşmede cezai
şart vardır
Anayasal kalkan çelişkiyi yakalar, cezai
yükümlülük tutarını gösterir, ikinci C-level onayı
ister; talimat sessizce uygulanmaz
## 6B.16 · 7.9
E2E-44Kök
motorlar
Kırtasiye faturası ile ana
hammadde faturası aynı anda
gelir
Dikkat bütçesi finansal büyüklüğe göre dağıtılır;
küçük olan refleks halkasında biter, büyük olan
derin analize çıkar
## 8.22 · 4.17
E2E-45Öğrenme90 gün önce 'hammadde fiyatı
sabit' varsayımıyla karar verilir;
varsayım bozulur
Varsayım izleyicisi uyarır, gerçekleşen sonuç
karar–sonuç kütüphanesine yazılır, taakkul eşiği
sıkılaşır ve benzer kararda daha fazla kanıt
istenir
## 6B.9 · 6B.15 ·
## 8.25
E2E-46ÖğrenmeAynı soru 3 ay boyunca 40 kez
LLM yolundan sorulur
Gözlemevi kümeyi yakalar, terfi kuyruğuna
düşer, onay sonrası deterministik metriğe
dönüşür ve maliyet farkı raporlanır
## 8.13 · 8.14 · 8.15
## · 8.17
E2E-47Dayanıklılıkİnternet kesilir, sonra LLM
sağlayıcısı da erişilemez olur
Sistem önce yerel modele, sonra DCM'ye düşer;
her seviye kullanıcıya görünür; rapor ve metrik
üretimi hiç durmaz
## 7.10 · 7.4
E2E-48DayanıklılıkIT ekibi ERP'de kolon adını
değiştirir
Sorgu hatası şema drift'i olarak teşhis edilir,
eşanlamlı haritası güncellenir, öneri insan
onayına sunulur ve MDL'e commit atılır
## 8.24 · 1.12
E2E-49İleri
motorlar
Tedarikçi zam bildirir; enerji
maliyeti de artar
Pazarlık stratejisi ve karşı teklif üretilir, marj
kalkanı etkilenen ürünleri bulur, fiyat revizyonu
insan onayına sunulur
## 12B.1 · 12B.2
E2E-50İleri
motorlar
Bir müşterinin sipariş sıklığı
yavaşlar ve ödemeleri gecikir
Micro-churn radarı erken uyarı verir,
açıklanabilirlik katmanı katkı dağılımını gösterir,
satış podu için görev üretilir
## 12B.3 · 6.15 · 3B.
## 7
E2E-51HafızaAynı kullanıcı farklı şubede aynı
soruyu sorar
Kişisel tercihi (format, para birimi) korunur;
şube hafızasındaki yerel koşul cevaba bağlam
olarak girer; şirket tanımı ezilmez
## 5.11 · 5.7
E2E-52Açık kaynakYeni bir bağımlılık projeye eklenirLisans taraması CI'da çalışır; GPL/AGPL/BSL
tespitinde derleme durur ve gerekçe raporlanır
## 8.26
DİMA · 0→100 Görev Takip Dosyası82 / 126

## AÇIK KAYNAK TEKNOLOJİ HARİTASI
Önerilen her araç tek tek değerlendirildi ve bir karara bağlandı. Bu bir alışveriş listesi değil, karar kütüğüdür: hangi aracın
neden seçildiği, hangisinin rolü doğru ama kendisi değiştirildiği, hangisinin ertelendiği ve listede olmadığı hâlde neyin
eklenmesi gerektiği yazılıdır.
Karar dağılımı
KABUL20  olduğu gibi benimsendi · DEĞİŞTİR10  rol doğru, araç/kapsam revize · EKLENDİ21  listede yoktu · ERTELE2
değerli ama sırası sonra
Genel değerlendirme: Öneri listesi güçlü ve isabetli. En değerli üç katkı: diferansiyel gizlilik (sektör kıyasında k-
anonimlikten daha güçlü matematiksel garanti), teorem kanıtlayıcı ile politika çelişki kontrolü (gerçekten ayırt edici
bir yetenek) ve kademeli zarafetle düşüş (satış argümanı olarak da güçlü). En kritik üç düzeltme: graf veritabanı
seçiminde lisans riski (GPLv3 tuzağı), departman hakeminde LLM tartışması yerine kısıt optimizasyonu, ve akış
işlemede V1 için aşırı mühendislik uyarısı.
Değerlendirmenin dışında kalan tek uyarı: lisans
Açık kaynak “bedava” demek değildir. GPL/AGPL lisanslı bir bileşen kapalı kaynak bir SaaS içinde kullanıldığında kaynak
açma yükümlülüğü doğurabilir; BSL   lisanslı araçlar ticari kullanımda kısıt taşır. Neo4j Community (GPLv3) bu listedeki en
net örnektir. Bu yüzden görev 8.26 eklendi: her bağımlılığın lisansı taranır, kayda geçer ve ihlal riski CI’da otomatik
yakalanır. Bu, sonradan düzeltilmesi en pahalı hatalardan biridir.
AraçKararGerekçeDima’daki karşılığı
1 · GÖZ VE KULAK — dış dünyadan veri alma
Crawl4AI
Web tarama · belgeden
KABULSayfayı temiz Markdown/JSON'a çeviren,
LLM için optimize edilmiş en olgun açık
kaynak crawler. Salt-okunur olduğu için
risk düşük.
Kanal katmanı · dış istihbarat
radarı (10.10) · fiyat/mevzuat
taraması
## Browser-use
Web otomasyonu · belgeden
DEĞİŞTİRRol doğru: API'si olmayan portalda form
doldurma. Ama LLM'in tarayıcıyı doğrudan
sürmesi kırılgan ve denetlenmesi zordur.
Karar: eylem üretimi LLM'de kalsın,
YÜRÜTME Playwright üstünde
deterministik senaryolarla yapılsın; LLM
yalnız senaryo seçsin.
Operator Core (9.4) · insan
onaylı dış icra
OpenClaw
Web/otomasyon işçisi · belgeden
DEĞİŞTİRKonumlandırma mükemmel — izole
worker, Tool Registry arkasında,
PROBABILISTIC_CONTEXT etiketiyle, insan
onaylı mutasyon. Ancak aracın olgunluğu
bağımsız doğrulanmalı. Karar: ROLÜ kabul
et, aracı seçmeden önce Crawl4AI
(okuma) + Playwright (yazma) ile
kıyaslayıp ölç.
Tool Registry (4.2) · izolasyon
proxy'si
IBM Docling
Belge/tablo ayrıştırma · belgeden
KABULKarmaşık PDF ve tabloları yapı bozmadan
çıkarmada bugünün en iyi açık kaynak
seçeneği. Mizan/bilanço/sözleşme için
doğrudan uygun.
## Unstructured Ingestion Wizard
(10.3) · 8B.2 fatura okuma
Marker / MinerU
Belge ayrıştırma (alternatif) · eklendi
EKLENDİDocling tek başına yeterli olmayabilir;
belge tipine göre başarım değişir. Karar:
üçünü aynı test setinde kıyasla, belge
tipine göre yönlendirici kur.
10.3 ayrıştırıcı havuzu
PaddleOCR
OCR · belgeden
DEĞİŞTİRTürkçe desteği var ama Türkçe el yazısı ve
düşük kaliteli taramada başarım
değişken. Karar: PaddleOCR + Surya'yı
Türkçe irsaliye/fatura setinde ölç,
kazananı varsayılan yap; her çıktı güven
payıyla etiketlensin.
Kanal-belge (1.1) · saha
fotoğrafı okuma
Faster-Whisper
Konuşma-metin · belgeden
KABULYerel, hızlı, olgun. Ses verisinin kurumdan
çıkmaması şartını tek başına karşılar.
11.3 yerel STT
53 araç · karar verilmiş
DİMA · 0→100 Görev Takip Dosyası83 / 126

AraçKararGerekçeDima’daki karşılığı
PyAnnote.audio
Konuşmacı ayrımı · belgeden
KABULDiarization'ın fiili standardı. Toplantıda
'kim söyledi' sorusunun cevabı.
11.3 diarization · 11.4 karar
çıkarımı
Ultralytics YOLO + SAM2
Görüntü analizi · eklendi
EKLENDİGörsel saha denetçisi (12B.6) için hangi
teknolojinin kullanılacağı belgede boştu.
Nesne tespiti + segmentasyon bu ikiliyle
çözülür.
12B.6 görsel saha denetçisi
## 2 · HAFIZA VE BİLGİ GRAFI
## Memgraph
Graf veritabanı · belgeden
DEĞİŞTİRÖneri mantıklı ama iki sorun var: (1)
bellek-içi mimari RAM'e bağımlıdır ve
maliyeti tenant başına hızla artar, (2)
lisans yapısı ticari kullanımda dikkat ister.
Karar: birincil olarak Apache AGE
(Postgres eklentisi) veya Kùzu (gömülü,
MIT) kullan — mevcut Postgres'in içinde
kalmak operasyon yükünü sıfırlar.
## 10.4 Knowledge Graph · 5.11
katmanlı hafıza
## Neo4j Community
Graf veritabanı (alternatif) · belgeden
ERTELEDİKKAT: Community sürümü GPLv3'tür.
Kapalı kaynak bir SaaS içinde kullanımı
ciddi lisans riski taşır. Karar: kullanma;
kullanılacaksa hukuki görüş şart.
— (lisans riski)
LightRAG / GraphRAG
Graf+vektör erişim · belgeden
DEĞİŞTİRFikir doğru ama maliyet uyarısı gerekir:
tüm metni graf'a çevirmek indeksleme
maliyetini patlatır. Karar: graf'ı ham
metinden değil, ONAYLANMIŞ
VARLIKLARDAN kur (müşteri, ürün,
sözleşme, proje); serbest metin vektörde
kalsın.
10.4 varlık grafı · Cortex
erişimi
LanceDB + DuckDB
Gömülü analitik+vektör · belgeden
KABULÖzellikle soğuk başlangıç ve Excel→sorgu
yolunda mükemmel: sunucu kurmadan
çalışır, kurulum sürtünmesini düşürür.
1.1 Excel→DB · 3.8 hafıza
indeksi
pgvector
Vektör deposu · eklendi
EKLENDİBelgede yok. Zaten Postgres varsa ayrı
vektör veritabanı kurmak gereksiz
operasyon yüküdür. Karar: varsayılan
pgvector; ölçek gerektirirse Qdrant'a geç.
3.8 kaynak-gerçeği kararı
BGE-M3 / multilingual-e5
Gömme modeli · eklendi
EKLENDİBelgede gömme modeli hiç
adlandırılmamış — oysa TÜRKÇE BAŞARIM
DOĞRUDAN BUNA BAĞLI. Karar: çok dilli
modeller Türkçe test setinde ölçülüp
seçilsin; sürüm her kayda yazılsın.
3.8 · 8.14 semantik kümeleme
MinIO
Nesne deposu · eklendi
EKLENDİHam tecrübe günlüğü (değişmez append-
only kayıt) için depolama katmanı
belgede yoktu.
Kalp-ham (3.8) · ham olay
günlüğü
## 3 · AKIŞ, İŞ AKIŞI VE ORKESTRASYON
## Temporal.io
Dayanıklı iş akışı · belgeden
KABULBelgedeki en isabetli tekniklerden biri. 3
gün insan onayı bekleyen bir ERP yazma
akışı, sunucu yeniden başlasa bile
kaybolmaz. Onay akışlarının belkemiği.
8B.4 onay akışı · 9.4 Operator
Core · 4.10 ajan durumu
LangGraph
Ajan durum makinesi · belgeden
KABULYedi aşamalı silsileyi (tahayyül→itikat)
döngüsel durum makinesi olarak
kodlamak için doğru araç.
4.1 ReAct orkestratörü
## Bytewax / Apache Flink
Akış işleme · belgeden
DEĞİŞTİRVizyon doğru (refleks yayı canlı akışla
çalışmalı) ama V1 için aşırı mühendisliktir.
Karar: V1'de CDC + uygulama içi kural
değerlendirmesi; olay hacmi eşiği aşınca
Bytewax devreye alınsın. Aşama: 4.17'de
tetikleyici, 8.x'te akış motoru.
4.17 refleks yayı · 8.10 Pulse
DİMA · 0→100 Görev Takip Dosyası84 / 126

AraçKararGerekçeDima’daki karşılığı
## Debezium
CDC · eklendi
EKLENDİBelgede canlı veri yakalama
adlandırılmamış. İşlem günlüğünden
okuma, sorgu yükü bindirmeden gerçek
zamana yakın akış sağlar — 'daima
güncel veri' vaadinin temeli.
Kanal-CDC (1.8) · 8B.1 ERP
okuma
## Novu
Bildirim altyapısı · eklendi
EKLENDİBildirim yorgunluğu (R9/3B.13) için açık
kaynak, toplama (digest) ve kanal
yönetimi hazır gelen altyapı. Sıfırdan
yazmaya değmez.
3B.13 bildirim yönetimi · 8.10
## Pulse
## Cal.com
Randevu motoru · eklendi
EKLENDİFrontDesk randevu motoru (9B.5) için açık
kaynak, kapasite/tampon süre yönetimi
olan hazır altyapı.
9B.5 kapasite-farkında
randevu
## Chatwoot
Omnichannel görüşme · eklendi
EKLENDİFrontDesk'te insana devir (9B.7) ve çok
kanallı kimlik (9B.8) için hazır açık kaynak
temel.
## 9B.7 · 9B.8
## Plane / Vikunja
Görev yönetimi · eklendi
EKLENDİİç görev tahtası (3B.6) sıfırdan yazılmak
yerine açık kaynak bir çekirdeğin üstüne
kurulabilir.
3B.6 görev motoru
## 4 · GÜVENLİK, GİZLİLİK VE YÖNETİŞİM
## Microsoft Presidio
PII tespit/maskeleme · belgeden
KABULKVKK anlatısının teknik omurgası. TCKN,
IBAN, telefon gibi Türkiye'ye özgü
desenler için özel tanıyıcı yazılabilir
olması kritik avantaj.
7.7 OutputRedactor · 2.12
## Plane Enforcer · 2.19
## Open Policy Agent
Politika motoru · belgeden
DEĞİŞTİROPA genel amaçlı politika motorudur ve
doğru bir seçim. Ancak satır/kolon yetkisi
(RLS) gibi İLİŞKİ TABANLI yetkilendirmede
OpenFGA veya Cerbos daha uygun
modeldir. Karar: Policy-as-Code için OPA,
ince taneli erişim için OpenFGA — ikisi
farklı iştir.
7.6 Policy-as-Code · 7.5 RLS/
## CLS
## Microsoft Z3
Teorem kanıtlayıcı · belgeden
DEĞİŞTİRFikir parlak ve gerçekten ayırt edici:
politikalar arası mantıksal çelişkiyi
matematiksel kesinlikle yakalamak.
UYARI: Z3 doğal dil politikayı anlamaz;
kuralların SMT formülüne çevrilmesi
gerçek bir mühendislik işidir. Karar:
kapsamı DAR tut — yalnız sayısal/
mantıksal kısıtlar (limit, eşik, çelişen emir)
için kullan.
6B.16 anayasal kalkan (yeni
görev)
PySyft / Diffprivlib
Diferansiyel gizlilik · belgeden
KABULBu, benim önceki k-anonimlik önerimden
DAHA İYİ. Diferansiyel gizlilik
matematiksel garanti sunar; k-anonimlik
sezgisel bir eşiktir. UYARI: gürültü
doğruluğu düşürür — epsilon bütçesi
yönetilmeli.
12.7 sektör kıyası (k-anonimlik
→ DP'ye yükseltildi)
PyRIT / Giskard
Red team / kalite · belgeden
KABULİkisi farklı iş yapar: PyRIT güvenlik saldırı
simülasyonu, Giskard model kalitesi/
yanlılık testi. İkisi de gerekli.
## 11.6 Red Team · 8.7 Evaluation
SDV (Synthetic Data Vault)
Sentetik veri · belgeden
DEĞİŞTİRDemo ve eğitim modu için doğru. UYARI:
sentetik veri sızdırmaz sanılır ama üyelik
çıkarımı saldırılarına açıktır. Karar: kullan
ama 'anonim' değil 'düşük riskli' diye
etiketle; gerçek PII üzerinde eğitilen
sentetik veri hukuken hâlâ
değerlendirilmelidir.
9.9 sandbox/eğitim modu
DİMA · 0→100 Görev Takip Dosyası85 / 126

AraçKararGerekçeDima’daki karşılığı
## Keycloak / Zitadel
Kimlik ve SSO · eklendi
EKLENDİBelgede kimlik katmanı yok. Kurumsal
satışta OIDC/SAML/LDAP zorunlu; sıfırdan
yazmak hem risk hem israf.
0.3 auth · 8.1 RBAC
immudb / hash-zincirli log
Değişmez denetim izi · eklendi
EKLENDİQueryContract'ın 'değiştirilemez' olma
iddiası bir teknolojiye dayanmalı; belgede
SHA-256 anılmış ama saklama katmanı
yok.
7.1 Provenance · 6B.8 Karar
## Kaydı
LLM Guard / NeMo Guardrails
Çalışma anı koruma · eklendi
EKLENDİPyRIT test eder ama çalışma anında
koruma sağlamaz. Prompt enjeksiyonu ve
zararlı çıktıya karşı runtime kalkan ayrı bir
bileşendir.
2.12 Plane Enforcer · 4.2 araç
kayıt
## 5 · ANALİTİK, NEDENSELLİK VE AÇIKLANABİLİRLİK
PyWhy (DoWhy + EconML)
Nedensel çıkarım · belgeden
KABULNedensellik grafının (6.13) hesap motoru.
Korelasyondan nedene geçişin gerçek
yolu. UYARI: nedensel çıkarım varsayım
gerektirir; yanlış grafla kesin görünen
yanlış sonuç üretir — çıktı daima
varsayımlarıyla sunulmalı.
6.13 nedensellik grafı · 4.8
kök-neden
## SHAP
Açıklanabilirlik · belgeden
KABULİçgörü kartındaki 'neden' şeridini
sayısallaştırır: 'churn %85 — katkı: %42
sipariş sıklığı, %28 ödeme gecikmesi'.
Zorunlu yorum kuralının (2.5)
matematiksel dayanağı.
2.5 içgörü kartı · 4.8 kök-neden
Nixtla StatsForecast / Prophet
Tahmin · eklendi
EKLENDİBelgede tahmin kütüphanesi
adlandırılmamış. Aralıklı tahmin (6.3) ve
mevsimsellik bunlarla yapılır; derin
öğrenmeye gerek yok.
6.3 tahminleme
PyOD / Merlion
Anomali tespiti · eklendi
EKLENDİAnomali (4.4, 8.10) için kural ve z-
skorunun ötesi gerektiğinde standart
kütüphaneler.
4.4 DataProcessor · 8.10 Pulse
Google OR-Tools
Kısıt optimizasyonu · eklendi
EKLENDİDepartman hakemi (6B.14) için ÖNEMLİ
DÜZELTME: çatışan hedefler nicelse (nakit
vs stok vs kapasite) bu bir OPTİMİZASYON
problemidir, LLM tartışması değil. OR-
Tools kesin optimum verir; LLM yalnız
niteliksel çatışmada devreye girsin.
6B.14 hakem · 9B.5 randevu
kapasitesi
NetworkX / Graphistry
Graf analitiği · belgeden
KABULSuistimal halkası ve tedarik kırılganlığı
tespiti için doğru. NetworkX hesap,
Graphistry görselleştirme.
12B.9 suistimal dedektifi · 10.4
graf
## Great Expectations / Soda
Veri kalitesi · eklendi
EKLENDİVeri kalitesi izleme (R80/8.x) belgede yok.
'Çöp veri, çöp karar' — bu katman
olmadan tüm zincir güvensizdir.
8.21 kurulum kalitesi · veri
kalitesi izleme
OpenLineage / Marquez
Veri soyağacı · eklendi
EKLENDİProvenance'ı (7.1) veritabanı düzeyinde
tamamlar: bu kolon nereden türedi, hangi
dönüşümden geçti.
7.1 Provenance · 7.8 data-flow
inspector
## 6 · MODEL, ÇIKARIM VE ÖĞRENME
vLLM / SGLang
Yerel çıkarım · belgeden
KABULOn-prem ve air-gapped kurulumun temeli.
Regüle müşteri satışının teknik ön şartı.
7.4 DCM/air-gap · 0.6 model
soyutlaması
LiteLLM
Model yönlendirici · eklendi
EKLENDİBelgede yok ama 0.6'daki 'model sınıfı
soyutlaması' görevinin hazır çözümü: tek
arayüzden bulut ve yerel model, otomatik
yedekleme, maliyet ölçümü.
0.6 LLM sağlayıcı soyutlaması ·
2.11 model seçimi
DİMA · 0→100 Görev Takip Dosyası86 / 126

AraçKararGerekçeDima’daki karşılığı
## Unsloth / Axolotl
Alan uyarlaması · belgeden
KABULMeleke inişinin (v3) model tarafındaki
karşılığı: alan tecrübesinin ağırlıklara
işlenmesi. Hekim-zihin, tekstil-zihin ayrımı
burada somutlaşır.
V3 sürekli meleke · 8.16 terfi
motoru
DSPy
Prompt derleme · belgeden
ERTELEDeğerli ama erken. Prompt yüzeyi
küçükken karmaşıklık ekler. Karar: V2'de
prompt sayısı ve düzeltme verisi
biriktikten sonra devreye alınsın.
8.3 Intent Learning (V2+)
DeepSeek-R1 sınıfı muhakeme
Yerel akıl yürütme · belgeden
KABULDüşünme adımları panelinin (2.9) yerel
çalıştırılabilmesi ve taakkul katmanının
veri çıkmadan derinleşmesi için doğru
yön.
2.9 düşünme adımları · 4.1
ReAct
E2B / Firecracker
İzole kod çalıştırma · belgeden
DEĞİŞTİRRol doğru: ajanın ürettiği kodu izole
çalıştırmak. Ancak air-gapped kurulumda
barındırılan servis kullanılamaz. Karar:
kendi altyapında Firecracker veya gVisor
tabanlı sandbox; E2B yalnız bulut
sürümünde.
4.2 araç kayıt · 12.2
simülasyon
Ragas / promptfoo
Değerlendirme · eklendi
EKLENDİGolden eval koşucusu (8.7) için hazır
çerçeveler; doğruluk trendini ölçmenin
standart yolu.
8.7 Evaluation paneli
## Langfuse
LLM gözlemevi · eklendi
EKLENDİLLM Gözlemevi (8.13) tam olarak budur
ve açık kaynaktır. Çağrı izleme, maliyet,
gecikme, sürüm karşılaştırma — sıfırdan
yazmaya gerek yok.
8.13 LLM Gözlemevi · 8.17
verimlilik raporu
7 · MİMARİ İLKELER — belgeden çıkan, araç değil desen
Kademeli zarafetle düşüş
Dayanıklılık · belgeden
KABULÜç seviye: (1) tam bilişsel (bulut LLM), (2)
tam yerel (internet kesik), (3) DCM (LLM
yok, %100 deterministik). Bu, satış
argümanı olarak da güçlüdür: 'sistem asla
durmaz'.
7.10 kademeli düşüş (yeni
görev)
Kendi kendini onaran şema
Dayanıklılık · belgeden
KABULERP'de kolon adı değişince sistemin
kilitlenmesi yerine drift'i tespit edip
eşanlamlı haritasını güncellemesi ve Git'e
commit atması. Çok isabetli.
8.24 şema drift onarımı (yeni
görev)
Çelişen emir hakemi
Yönetişim · belgeden
KABULPatronun talimatı ile sözleşme
yükümlülüğü çeliştiğinde uyarma ve ikinci
onay isteme. Z3 ile birleşince güçlü.
6B.16 anayasal kalkan (yeni
görev)
Kapalı devre evrim
Öğrenme · belgeden
KABULKarar → varsayım defteri → zaman →
gerçekleşen → hissiyat/eşik kalibrasyonu.
Bu döngü zaten mimaride vardı; belge
onu netleştirdi ve görev olarak yazıldı.
8.25 kapalı devre öğrenme
(yeni görev)
DİMA · 0→100 Görev Takip Dosyası87 / 126

## KAPSAMA MATRİSİ
Aşağıdaki matris otomatik üretildi: her senaryo F/Y kodundan, her UX fikrinden, her backend sisteminden ve her Wren bağlama
kaleminden hangi görev(ler)in sorumlu olduğunu gösterir. Senaryolar bu kodların bileşimi olduğundan, tüm kodların kapsanması
tüm senaryoların kapsandığını kanıtlar.
✔ TAM KAPSAMA: her özellik, UX fikri, backend sistemi ve Wren bağlama kalemi en az bir
göreve bağlandı. Eksik yok.
Mevcut/Hedef özellikler (F1–F27)
KodAçıklamaGörev(ler)
## F11.11   ·  1.11a
## F23.1
## F34.1  ·  4.2  ·  4.13   ·  4.14
## F41.6  ·  1.11c
## F52.16   ·  4.15   ·  6B.11    ·  7.3  ·  11.8
F62.15   ·  2.17   ·  3.6  ·  5.9  ·  6B.8   ·  6B.10    ·  7.1  ·  7.2  ·  8B.5   ·  10.1
## F77.5  ·  9B.3   ·  10.5
F81.10   ·  2.19   ·  5.10   ·  7.5  ·  7.7  ·  8.13   ·  8B.3   ·  9B.1   ·  9B.8   ·  10.5   ·  11.1   ·
## 12.9
## F94.12   ·  7.4  ·  7.10
## F108.2  ·  8.2a
## F114.4  ·  6.15
## F123B.7   ·  6.2
## F132.14   ·  3.2  ·  9B.4
## F143.4  ·  3B.12
F151.10   ·  1.11a    ·  3.12   ·  3B.5
## F161.11d    ·  3.5  ·  3.7  ·  5.6  ·  5.7
## F174.9  ·  8.23
## F188B.1   ·  9.3  ·  9B.10
## F192.4
## F209.2
## F212.12   ·  11.3
## F222.6
## F238.7  ·  8.17   ·  8B.6
## F241.13   ·  3.11   ·  8.20
F256B.16    ·  7.6  ·  7.9  ·  8B.3   ·  10.8   ·  10.9   ·  11.1   ·  12.8   ·  12.9   ·  12B.9
## F268.2b   ·  8.4  ·  8.24
F271.1  ·  1.3  ·  1.5  ·  1.8  ·  1.10   ·  1.11e    ·  3B.1
komple kontrol
DİMA · 0→100 Görev Takip Dosyası88 / 126

Geliştirilecek özellikler (Y1–Y26)
KodAçıklamaGörev(ler)
## Y13.3  ·  3.9  ·  3B.11
## Y28.10   ·  12.1
## Y36.3  ·  12.3   ·  12B.8
## Y46.4  ·  6B.7   ·  12.2   ·  12.3   ·  12B.2
## Y54.8  ·  6.9  ·  11.6
## Y68B.2   ·  9.6  ·  10.3
## Y79.7  ·  10.4
## Y88B.4   ·  9.4  ·  9B.2   ·  13.5
## Y93.10
## Y108.19   ·  9.8  ·  10.10    ·  12.7
## Y119.1  ·  12.10
## Y129.4
## Y139.8  ·  12.8   ·  12B.4
## Y149.8  ·  12.10    ·  12B.6
## Y159.9  ·  10.6
## Y166.8  ·  12B.3
## Y176.7  ·  12B.7    ·  13.3
## Y189.10
## Y199.6  ·  13.2
## Y209.5
## Y219.5
## Y221.11b    ·  8.5
## Y238.5
## Y248.5
## Y258.5  ·  9.8
## Y261.11   ·  1.11b    ·  8.5
Özel UI/UX fikirleri (UX1–UX11)
KodAçıklamaGörev(ler)
UX1Kanıt-her-yerde tıklanabilir2.15   ·  6B.5   ·  10.2   ·  10.7
UX2Hızlı/Derin toggle2.13
UX3Büyüyen analiz tuvali2.10
UX4Şirket portresi ekranı5.2
UX5"Ne sorabilirim" keşif haritası1.13
UX6Görünmez kolon anahtarı1.10
UX7İçgörü kartı (3 şerit)2.5
UX8Hayalet karşılaştırma3.6
DİMA · 0→100 Görev Takip Dosyası89 / 126

KodAçıklamaGörev(ler)
UX9Meta-güven şeridi2.18   ·  5.10
UX10Alarm-widget3.3
UX11Sesli/mobil cep CEO9.5
Özel Backend sistemleri (BE1–BE28)
KodAçıklamaGörev(ler)
BE1Router+Policy Kernel0.8  ·  2.11   ·  4.17   ·  7.10   ·  8.22
BE2Plane Enforcer (iki-düzlem)2.12   ·  9B.1
BE3Provenance & Contract motoru6B.5   ·  6B.8   ·  7.1
BE4Git-destekli MDL deposu0.4
BE5Global Şirket Hafızası5.1  ·  5.3
BE6Hafıza/cache kaynak-gerçeği
senkronu
## 3.8  ·  8.2  ·  8.2a   ·  8.2b
BE7Kuyruk + worker (BullMQ)0.1  ·  0.7  ·  8.8  ·  8.26
BE8Dinamik bağlantı havuzu (LRU)8.8
BE9Zamanlanmış iş + batch3.9  ·  5.3  ·  8.9
BE10Kredi/maliyet muhasebesi4.16   ·  8.6  ·  8.22
BE11Pulse proaktif motor3B.13    ·  6B.9   ·  8.10   ·  12.1
BE12Öğrenme döngüsü8.3  ·  8.15   ·  8.25
BE13Golden eval koşucusu8.7
BE14LlmShadow (gölge-kıyas)8.11
BE15Metrik Katmanı + Türetme Motoru
(Sınıf A/B/C)
1.11a    ·  1.11b    ·  1.11c    ·  1.11d    ·  1.11e    ·  6.13   ·  6B.4   ·  8.24
BE16LLM Gözlemevi (çağrı imzası +
kümeleme)
## 8.3  ·  8.13   ·  8.14   ·  8.17   ·  8.21   ·  12.12
BE17Terfi / Küratörlük Motoru (tek
motor, 4 kaynak)
## 6B.12    ·  8.14   ·  8.15   ·  8.16   ·  8.18   ·  8.25
BE18Denetimli Ajan Döngüsü (adım
doğrulama)
## 4.13   ·  4.14   ·  4.15   ·  4.16
BE19Karar Motoru (Decision Engine)3B.8   ·  6.11   ·  6B.1   ·  6B.2   ·  6B.3   ·  6B.4   ·  6B.5   ·  6B.6   ·  6B.7   ·  6B.8   ·  6B.9   ·
6B.10    ·  6B.11    ·  6B.12    ·  6B.13    ·  6B.14    ·  6B.15    ·  6B.16    ·  8.16   ·  10.8   ·  11.4
## ·  11.7   ·  12.4   ·  12.6   ·  12B.1    ·  12B.5    ·  13.5
BE20Seçici Hafıza / Cortex katmanları5.6  ·  5.7  ·  5.8  ·  5.9  ·  5.10   ·  5.11   ·  5.12   ·  6B.15    ·  8.16   ·  8.19   ·  9B.9   ·  11.4   ·
## 12.5   ·  12.7
BE21Kanıt Sınıfı Ayrımı (Gold ↔
## Context)
## 10.1   ·  10.2   ·  10.10    ·  11.5
BE22Yapılandırılmamış Alım +
## Knowledge Graph
## 10.3   ·  10.4   ·  10.5   ·  10.6   ·  10.7   ·  10.10    ·  12.10
BE23Toplantı Ajanı (STT + diarization)11.1   ·  11.2   ·  11.3   ·  11.4   ·  11.5
BE24Red Team / Karşıt Ajan + Bias
## Guard
## 11.6   ·  11.7   ·  11.8   ·  12.6   ·  12.9   ·  13.3
BE25Dijital İkiz & Simülasyon12.1   ·  12.2   ·  12.3   ·  12.4   ·  12.11    ·  13.2
DİMA · 0→100 Görev Takip Dosyası90 / 126

KodAçıklamaGörev(ler)
BE26Kolektif Sektör Zekâsı (anonim
hive)
## 12.7   ·  13.1   ·  13.4
BE27Sürekli Mevzuat Kalkanı12.8
BE28Founder Cortex / Yönetici Hafızası10.8   ·  10.9   ·  12.5
Wren motorundan bağlanacaklar
KodAçıklamaGörev(ler)
wGENBIGenBI Apps2.14
wSKILLSSkills4.9
wPDFPDF çıkarma9.6
wENRICHenrich-context (grill/auto-pilot)1.10
wPROFILEvalue profiling1.12
wERRORSstructured errors1.12
wFUNCfunctions (governed)4.11
wAPPROVEapproval workflow9.4
wINSPECTdata-flow inspector7.8
wRATErate limits8.12
wWASMwren-core-wasm3.2
wSDKframework SDK (langchain/
pydantic)
## 4.10
wSKILLFILESonboarding/generate-mdl/genbi
skills
## 1.2
wEVALgolden eval runner8.7
wUNSTRUCTunstructured knowledge9.6  ·  10.3
wOSIOSI9.11
Vizyon gereksinimleri (R1–R106)
KodAçıklamaGörev(ler)
Ç1Çoklu veri kaynağı bağlama1.1  ·  1.8  ·  9.3
R1Günlük durum görünürlüğü3B.11
Ç2Anlamlandırma / semantik
katman
## 1.2  ·  1.10   ·  1.11a    ·  1.11c
R2Tehdit ve risk erken uyarısı8.10
Ç3Türkçe doğal dilde soru sorma1.6  ·  1.9  ·  1.13
R3Fırsat keşfi12.1
Ç4Deterministik metrik cevabı (altın
yol)
## 1.11   ·  1.11b    ·  2.11
R4Gelişim yol haritası6.14
Ç5Otomatik grafik üretimi2.1  ·  2.2  ·  2.3  ·  9.1
R5Sürekli iyileştirme önerileri6.14
DİMA · 0→100 Görev Takip Dosyası91 / 126

KodAçıklamaGörev(ler)
Ç6Zorunlu içgörü yorumu2.5  ·  4.4  ·  6.15
R6Sabah brifingi ritüeli3B.11
Ç7Tıklanabilir öneri zinciri2.6  ·  2.7  ·  2.10
R7Departman + genel çift görünüm3B.12
Ç8Rapor üretimi3.1  ·  6.5
R8Anomali tespiti ve bildirimi8.10
Ç9Pano üretimi ve kalıcılığı2.8  ·  3.2  ·  3.4
R9Bildirim yorgunluğu yönetimi3B.13
Ç10Kanıt zinciri2.15   ·  7.1  ·  7.8
R10İş tanımı kütüğü3B.1
Ç11Dürüst red2.16   ·  7.3
R11Süreç haritası3B.1
Ç12Kalibre edilmiş güven rozeti2.17   ·  2.18   ·  7.2
R12Organizasyon ve rol/yetki matrisi3B.1
Ç13Kök-neden analizi4.8  ·  6.9  ·  6.15
R13Ürün/hizmet kataloğu + reçete
## (BOM)
## 3B.2
Ç14Tahmin ve senaryo (what-if)6.3  ·  6.4  ·  12.2
R14Tedarikçi ve müşteri kartları3B.2
Ç15Karar motoru6.11   ·  6B.1   ·  6B.5   ·  6B.8
R15Sözleşme envanteri3B.2
Ç16Dışa aktarım2.4  ·  3.1
R16Kurumsal takvim ve mevsimsellik3B.3
Ç17Veri egemenliği ve AI-kapalı mod2.12   ·  4.12   ·  7.4  ·  7.10
R17Bilgi sahipliği + tazelik SLA3B.4   ·  5.12
Ç18Çok kullanıcılı yetki (RLS/CLS)7.5  ·  8.1  ·  9B.3
R18Bağlam bakım ajanı5.12
R19İş terimleri sözlüğü3B.5
R20Paydaş haritası3B.3
R21Kişi hafızası5.11
R22Departman hafızası5.11
R23Şube/tesis hafızası5.11
R24Şirket/holding hafızası5.11
R25Sektör/benchmark hafızası5.11
R26Sistem geneli hafıza5.11
R27Çürüme ve unutma motoru5.9
R28Hafıza çelişki yönetimi5.7
R29Hafıza şeffaflığı5.10
DİMA · 0→100 Görev Takip Dosyası92 / 126

KodAçıklamaGörev(ler)
R30Chat'ten görev oluşturma ve
atama
## 3B.6
R31Görev takibi ve durum3B.6
R32Görev önerisi3B.7
R33Dış görev aracı entegrasyonu9.12
R34İç görev tahtası3B.6
R35Görev–karar/bulgu bağı3B.8
R36Görev sağlığı izleme3B.9
R37Taahhüt yakalama3B.10
R38Eskalasyon matrisi7.9
R39Üretim/operasyon podu6.12
R40Finans/muhasebe podu6.12
R41Satış/pazarlama podu6.12
R42İK/prosedür podu6.12
R43Satınalma/tedarik podu6.12
R44Kalite podu6.12
R45IT/güvenlik podu6.12
R46Departman hakemi6B.14
R47Pod sağlık skoru6.12
R48ERP okuma entegrasyonu8B.1
R49Agentic veri girişi8B.2
R50Şema ve politika doğrulama8B.3
R51İnsan onaylı yazma8B.4
R52Geri alma ve tam denetim izi8B.5
R53ERP-agnostik adaptör8B.1
R54Giriş hızı ölçümü8B.6
R55Chat'ten ayar ve yetki yönetimi8.20
R56Chat'ten metrik/kural öğretme8.20
R57Yetenek keşfi8.20
R58Kullanım rehberliği8.20
R59Kendi kendini teşhis8.21   ·  8.24
R60Kurulum kalitesi skoru8.21
R61Nedensellik grafı6.13
R62Telos/OKR senkronizasyonu6B.13
R63Refleks yayı4.17
R64Hakemlik çekirdeği6B.14    ·  6B.16
R65Dikkat ve bütçe motoru (nazar)8.22
R66Durum çatallama12.11
R67Kök motor gözlemevi12.12
DİMA · 0→100 Görev Takip Dosyası93 / 126

KodAçıklamaGörev(ler)
R68Kamu şeması9B.1
R69Tampon bölge (staging)9B.2
R70Müşteri-RLS + OTP9B.3
R71Üretken arayüz kataloğu9B.4
R72Kapasite-farkında randevu9B.5
R73Satış niyeti skoru9B.6
R74İnsana devir protokolü9B.7
R75Müşteri sesi → iç istihbarat9B.9
R76Omnichannel kimlik çözümleme9B.8
R77Dikey paketler9B.10
R78Pazarlık hazırlık motoru12B.1
R79Marj kalkanı / dinamik fiyat12B.2
R80Micro-churn radarı12B.3
R81Sözleşme risk eleği12B.4
R82İç proje/fikir eleği12B.5
R83Görsel saha denetçisi12B.6
R84Yetenek boşluğu ve halef planı12B.7
R85Nakit arbitrajı12B.8
R86Suistimal ve mükerrer ödeme
dedektifi
## 12B.9
R87Karar–sonuç kütüphanesi6B.15    ·  8.25
R88Playbook kütüphanesi8.23
DİMA · 0→100 Görev Takip Dosyası94 / 126

## ÜRÜN YOL HARİTASI
Faz haritası “ne inşa edilecek” sorusunun cevabıdır; bu bölüm “her aşamada hangi ÜRÜN ortaya çıkacak, kime, hangi sözle
satılacak” sorusunun cevabıdır. Sürümler kümülatiftir: v3 çekirdek üründür (%100), v4-v6 nihai vizyondur.
SürümÜrün kimliğiFazlarKonumlandırmaHedef kitleGeçiş kapısı
v1Denetlenebilir
GenBI & Kanıt
## Motoru
## FAZ 0–
## 3
“Sıradan yapay zekâ
uydurur. Dima hesap
verir.”
Raporu hazırlayan
şampiyon + patron ·
veri-acısı olan ERP'li
orta-büyük firma
5–8 ödeyen müşteri + 1
yayınlanmış vaka; altın
yol oranı %50+
v2Proaktif Analist, İş
## Bağlamı & Görev
## Motoru
## FAZ
## 3B–6
“Dashboard'lar öldü.
Soruyu siz sorun, cevabı
Dima getirsin.”
C-Level, operasyon ve
satış direktörleri
15–20 müşteri; haftalık
aktif kullanım ≥3 kişi/
hesap; patron ayda 4+
oturum
v3KARAR MERKEZİ +
## ERP SEMBİYOZU +
## FRONTDESK
## FAZ
## 6B–9B
“Kararınızın arkasında ne
var? Dima gösterir.”
Yönetim kurulu, CFO/
GM, regüle kurumlar
(banka, kamu, sağlık)
Kurumsal sözleşmeler +
denetim geçmişi
birikmeye başladı; churn
## ≈ 0
v4Kurumsal Bilgi Hub'ı
## & Külli Hafıza
FAZ 10“Şirketin 10 yıllık hafızası
tek akılda — ve nereden
geldiği belli.”
İK, operasyon, saha
ekipleri, danışmanlık
ve denetim firmaları
Bilgi Hub'ı aktif
kullanımı; yeni personel
adaptasyon süresinde
ölçülebilir düşüş
v5Canlı Akıl: Toplantı
## Ajanı & Red Team
FAZ 11“Toplantıdaki tek tarafsız
akıl.”
Holdingler, yönetim
kurulları, strateji ve
risk komiteleri
Toplantı kararlarının
Karar Kaydı'na akması;
Red Team önerilerinin
karar değiştirme oranı
v6KÜLLİ ŞİRKET BEYNİ
· Enterprise AI OS
## FAZ
## 12–12B
“Şirketinizin yaşayan,
sorgulayan, hatırlayan
beyni.”
Global kurumsal,
holding, çok tesisli
üretici
Kurumsal hafıza +
denetim tarihçesi +
benchmark üçlüsü tam;
kategori sahipliği
v1 → Nihai Vizyon
DİMA · 0→100 Görev Takip Dosyası95 / 126

v1  Denetlenebilir GenBI & Kanıt Motoru
Şirketin verisi ilk kez konuşulabilir hale gelir. Kullanıcı Excel atar veya veritabanını bağlar; sistem kolonları onunla
birlikte anlamlandırır, ilk metrikleri kurar. Sonrasında soru sorup saniyeler içinde grafik ve yorum alır, beğendiğini
panoya sabitler, biriktirdiğini rapora çevirir.
## ✓ BU SÜRÜMDE YAPAR
Bağlanan veriye Türkçe soru sorup saniyeler içinde sayı,
grafik ve yorum almak
Her sayının kaynağını (formül + SQL + tarih) tek tıkla
görmek
Beğenilen grafiği panoya sabitlemek, biriken analizleri
rapora çevirmek
Tanımlı metrikleri yapay zekâ hiç devreye girmeden
hesaplamak (altın yol)
Bilinmeyen bir şey sorulduğunda uydurmak yerine 'bu
veri sistemde yok' demek
## ✕ HENÜZ YAPMAZ
Çok adımlı araştırma yapmaz — 'ciro neden düştü'
sorusuna tek grafikle cevap verir, kök nedene inmez
Tahmin ve senaryo üretmez (v2)
Kendiliğinden haber vermez; sorulmadan konuşmaz (v2)
Görev oluşturmaz, atamaz, takip etmez (v2)
Toplantı, sözleşme, e-posta gibi veritabanı dışı bilgiyi
bilmez (v4)
Karar süreci yönetmez; seçenek kıyaslamaz (v3)
Gelen yetenekler
Sohbetle kurulum sihirbazı (Excel/DB → anlamlandırma → onay)
Metrik ve cube katmanı; altın yolda LLM'siz kesin cevap
Grafik + zorunlu içgörü yorumu (ne oluyor / neden / ne yapmalı)
Tıklanabilir öneri zinciri ve büyüyen analiz tuvali
Rapor ve pano üretimi; kanıt kartı, dürüst red, güven rozeti
Örnek kullanım — bu sürüm sahada nasıl görünür
KullanıcıMart ayında hangi şubede en çok fire verdik?
## Dima
Kadıköy şubesi, %4,2 fire (şirket ortalaması %2,8). Grafik yandaki gibi. Bu oran son 3 aydır yükseliyor.
Kullanıcı(sayıya tıklar)
## Dima
Kaynak: fire_orani metriği = ikinci_kalite / toplam_uretim · sales+production tabloları · 12 Tem 09:14 · MDL a3f9c1 ·
磊 altın
KullanıcıÜrün grubuna göre kır
## Dima
(aynı ekranın altına yeni grafik ekler) Örme grubunda %6,1 ile öne çıkıyor...
Tipik gün: Sabah raporunu hazırlayan kişi, 3 saatlik Excel işini 15 dakikaya indirir; patron akşam panodan bakar.
Kim içinRaporu hazırlayan şampiyon + patron · veri-acısı olan ERP'li orta-büyük firma
Konumlandırma“Sıradan yapay zekâ uydurur. Dima hesap verir.”
Rakibe darbeKanıtsız chatbot'ları ve statik dashboard'ları ‘doğrulanamaz’ konumuna düşürmek
Ticari anlamıBu sürüm satılabilir. Tek başına 'raporu hazırlayan kişinin haftalık 8 saatini geri veren' bir üründür.
Ana riskiKurulum sürtünmesi. Değer, veri bağlanıp anlamlandırıldıktan sonra doğduğu için ilk 30 dakika kritiktir.
Geçiş kapısı5–8 ödeyen müşteri + 1 yayınlanmış vaka; altın yol oranı %50+
## · FAZ 0–3
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası96 / 126

v2  Proaktif Analist, İş Bağlamı & Görev Motoru
Sistem soru cevaplayan olmaktan çıkıp analiz yapan hale gelir. 'Ciro neden düştü' sorusuna tek grafikle değil, çok
adımlı bir araştırmayla cevap verir; kök nedeni bulur, tahmin üretir, senaryo dener.
## ✓ BU SÜRÜMDE YAPAR
Tek soruyla çok adımlı araştırma yapmak: kırılım →
karşılaştırma → kök neden
Sapmanın kaynağını yüzde katkılarıyla ayrıştırmak
('düşüşün %70'i X şubesinden')
Aralıklı tahmin ve what-if senaryosu üretmek ('kur %20
artarsa marj şu bandda')
Eşik aşımında kimse sormadan bildirim göndermek
(WhatsApp/e-posta)
Şirketi tanıyıp boş ekran yerine hazır açılış panosu açmak
## ✕ HENÜZ YAPMAZ
Kararı yönetmez — seçenek üretip kıyaslamaz, karar
kaydı tutmaz (v3)
Kendi başına işlem yapmaz; e-posta atmaz, ERP'ye
yazmaz (v6 · onaylı)
Veritabanı dışındaki belgeleri okumaz (v4)
ERP’ye yazmaz; dış müşteriyle konuşmaz (v3)
Tahminlerini kesin sayı olarak sunmaz; her zaman aralık
ve varsayım verir
Gelen yetenekler
Agentic döngü: planla → araç çalıştır → doğrula → sentezle
Kök-neden ve varyans ayrıştırma motoru
Trend, anomali, tahmin (aralıklı) ve what-if simülasyonu
Şirketi tanıyan global hafıza ve otomatik açılış panosu
İş bağlamı kütüğü: ne satıyoruz, süreç, sorumluluk, takvim (Faz 3B)
Görev motoru: chat’ten oluştur–ata–takip + görev–bulgu bağı
Sabah brifingi ritüeli + departman/genel çift görünüm
Departman podları: üretim, finans, satış, İK, satınalma, kalite, IT
Eşik alarmları, zamanlanmış rapor ve WhatsApp brifingi
Örnek kullanım — bu sürüm sahada nasıl görünür
KullanıcıBu ay ciro neden düştü?
## Dima
(3 araç çağrısı) Düşüşün %70'i Ege bölgesinden; onun da %60'ı tek bir müşterinin sipariş ertelemesinden. Kalan
%30 fiyat etkisi.
KullanıcıO müşteri ne zamandır böyle?
## Dima
Son 4 ayda sipariş sıklığı 12 günden 26 güne çıkmış — churn riski sinyali. Tahsilat gecikmesi de 18 gün arttı.
## Dima
(kimse sormadan, ertesi sabah) Aynı örüntü ikinci bir müşteride başladı. Bakmak ister misiniz?
Tipik gün: Satış direktörü pazartesi 08:00'de telefonuna düşen 5 satırlık brifingle güne başlar; ekrana bakmadan durumu
bilir.
Kim içinC-Level, operasyon ve satış direktörleri
Konumlandırma“Dashboard'lar öldü. Soruyu siz sorun, cevabı Dima getirsin.”
Rakibe darbeStatik BI panellerini patron gözünde ‘ölü yatırım’a çevirmek
Ticari anlamıÜrün burada 'panel' algısından çıkar, 'analist' algısına geçer. Fiyat çıpası da bu noktada analist maaşına
bağlanabilir.
Ana riskiMaliyet kontrolü. Agentic analiz pahalıdır; bütçe tavanı ve altın yol oranı sıkı izlenmelidir.
Geçiş kapısı15–20 müşteri; haftalık aktif kullanım ≥3 kişi/hesap; patron ayda 4+ oturum
## · FAZ 3B–6
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası97 / 126

v3  KARAR MERKEZİ + ERP SEMBİYOZU + FRONTDESK
Çekirdek ürün tamamlanır. Sistem artık analiz üretmekle kalmaz, kararın kendisini yönetir: seçenekleri çıkarır,
kriterlere göre kıyaslar, neyin veri neyin varsayım olduğunu söyler, kararı imzalı bir kayda dönüştürür ve
varsayımları sonradan izler.
## ✓ BU SÜRÜMDE YAPAR
Bir kararı uçtan uca yönetmek: çerçeveleme →
seçenekler → kriterler → kanıt matrisi → tavsiye
Her hücrenin veri mi varsayım mı bilinmeyen mi
olduğunu açıkça göstermek
Neden A değil B seçilmedi sorusunu cevaplamak ve
kırılma eşiğini hesaplamak
Kararı imzalı, değişmez kayda dönüştürmek ve
varsayımları sonradan izlemek
Yapay zekâ tamamen kapalıyken (DCM) menü üzerinden
çalışmak — banka/kamu için
## ✕ HENÜZ YAPMAZ
Karar VERMEZ, veto etmez, imzalamaz — imza her
zaman insandadır
Toplantı dinlemez, belge okumaz (v4–v5)
Kararı otomatik uygulamaz; hiçbir sisteme yazma
yapmaz
Sektör ortalamasıyla kıyaslamaz (v6)
Gelen yetenekler
Karar motoru: çerçeveleme, seçenek üretimi, ağırlıklı kıyas matrisi
Ret gerekçesi ve tersine soru ('kazanması için ne gerekirdi?')
İmzalı Karar Kaydı, varsayım defteri ve karar takibi
Tam güven katmanı: contract, eligibility, DCM, RLS/CLS, audit, policy
Nedensellik grafı + telos/OKR senkronizasyonu + departman hakemi
ERP sembiyozu: sesli/görsel agentic veri girişi, insan onaylı yazma (Faz 8B)
Dış katman FrontDesk: kamu şeması, müşteri-RLS+OTP, randevu, katalog (Faz 9B)
Sistem uzmanı copilot: ayar, yetki ve kural yönetimi sohbetten
Terfi motoru ve sektör paketleri; kullandıkça ucuzlayan yapı
Örnek kullanım — bu sürüm sahada nasıl görünür
Kullanıcıİkinci vardiya mı açalım, fasona mı verelim?
## Dima
Bu geri dönülemez bir karar (yatırım + işe alım), tam analiz açıyorum. 3 seçenek + mevcut durumu koruma
senaryosu kurdum.
## Dima
Kriterler: birim maliyet, teslim süresi, kalite riski, nakit etkisi. Ağırlıkları siz belirler misiniz?
KullanıcıNakit en önemli, sonra teslim.
## Dima
Matris hazır. Öneri: fason (ağırlıklı skor 7,4). İkinci vardiya ancak sipariş hacmi %25 artarsa öne geçer. Bu kararın
%55'i veriye, %35'i varsayıma dayanıyor — en kırılgan varsayım fason kalite fire oranı.
## Dima
(6 hafta sonra) Bu kararı 'fason fire %3' varsayımıyla verdiniz; gerçekleşen %5,8. Kararı gözden geçirmenizi
öneririm.
Tipik gün: Yönetim kurulu toplantısına, her sayısı tıklanınca kaynağına giden 2 sayfalık karar memosuyla girilir.
Kim içinYönetim kurulu, CFO/GM, regüle kurumlar (banka, kamu, sağlık)
Konumlandırma“Kararınızın arkasında ne var? Dima gösterir.”
Rakibe darbeDenetime giremeyen AI araçlarını ihale ve uyum masasında elemek
Ticari anlamıRegüle sektörlere (banka, kamu, sağlık) satışın kilidi bu sürümdür. Denetlenebilirlik olmadan o kapılar
açılmaz.
Ana riskiKarar motoru ürünün ağırlık merkezini değiştirir: demo artık panoyla değil Karar Kaydı ile bitmelidir.
Geçiş kapısıKurumsal sözleşmeler + denetim geçmişi birikmeye başladı; churn ≈ 0
## · FAZ 6B–9B
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası98 / 126

v4  Kurumsal Bilgi Hub'ı & Külli Hafıza
Şirketin veritabanı dışındaki bilgisi de sisteme girer: sözleşmeler, prosedürler, şikayetler, haberler, yöneticinin sesli
stratejik notları. Bunlar ERP kayıtlarıyla ilişkilendirilir ve çalışan 'bu işi nasıl yaparım' sorusunun cevabını buradan
alır.
## ✓ BU SÜRÜMDE YAPAR
Sözleşme, prosedür, şikayet, e-posta, taranmış belge gibi
yapılandırılmamış bilgiyi içine almak
Metindeki varlıkları ERP kayıtlarıyla bağlamak ('X
müşterisi' → hem cirosu hem şikayeti)
Çalışana 'bu işi nasıl yaparım' sorusunda adım adım
prosedür rehberliği vermek
Yöneticinin sesli stratejik notunu kalıcı şirket kuralına
çevirmek
Kesin veri ile duyumu asla karıştırmadan, ikisini ayrı
bloklarda sunmak
## ✕ HENÜZ YAPMAZ
Duyumu kesin veri gibi göstermez; bağlam notu grafiğe
girmez, toplama katılmaz
Toplantıya katılmaz, canlı dinlemez (v5)
Belge içeriğine dayanarak işlem yapmaz
Erişim yetkisi olmayan dokümanı hiçbir cevapta
kullanmaz
Gelen yetenekler
Yapılandırılmamış veri alım sihirbazı (PDF, sözleşme, SOP, e-posta, OCR)
Knowledge Graph: metindeki varlıkları ERP kayıtlarına bağlama
Kurumsal prosedür ve oryantasyon merkezi (rol bazlı rehberlik)
CEO Mind-Dump: sesli not → şirket stratejisi kuralı
Kanıt sınıfı ayrımı: kesin veri ile duyum asla karışmaz
Örnek kullanım — bu sürüm sahada nasıl görünür
KullanıcıABC Tekstil ile ilişkimiz nasıl?
## Dima
磊 ERP verisi: son 12 ayda 4,2M TL ciro, ortalama tahsilat 47 gün, açık bakiye 380K TL.
## Dima
 Bağlam notu (doğrulanmamış): 12 Mart tedarik toplantısında ödeme vadesi konusunda sıkıntı dile getirilmiş
(kaynak: toplantı notu). Ayrıca sözleşmede 60 gün vade var, fiili 47 gün — uyumlu.
Yeni çalışanHatalı parçayı nasıl iade alırım?
## Dima
1) ERP'de İade Fişi ekranını aç... 2) Kalite kodunu seç... (kaynak: İade Prosedürü v3, s.4) Yetki gerekiyor: depo
sorumlusu onayı.
Tipik gün: Yeni işe giren operasyon uzmanı, kimseye sormadan ilk haftasında prosedürleri uygulayabilir hale gelir.
Kim içinİK, operasyon, saha ekipleri, danışmanlık ve denetim firmaları
Konumlandırma“Şirketin 10 yıllık hafızası tek akılda — ve nereden geldiği belli.”
Rakibe darbeSadece veritabanına bakan rakipleri ‘şirketi tanımayan yabancı’ konumuna düşürmek
Ticari anlamıChurn'ü sıfıra yaklaştıran sürüm budur: şirketin hafızası sisteme taşındığında çıkmak imkânsızlaşır.
Ana riskiEn büyük risk kanıt kirlenmesidir. 10.1 görevi bitmeden bu fazın hiçbir parçası devreye alınmamalıdır.
Geçiş kapısıBilgi Hub'ı aktif kullanımı; yeni personel adaptasyon süresinde ölçülebilir düşüş
## · FAZ 10
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası99 / 126

v5  Canlı Akıl: Toplantı Ajanı & Red Team
Sistem toplantı odasına girer. Konuşmaları dinler, kimin ne dediğini ayırır, kararları ve aksiyonları çıkarır; veriyle
çelişen bir iddia duyduğunda uyarır ve kararlara karşıt akıl olarak itiraz eder.
## ✓ BU SÜRÜMDE YAPAR
Toplantıya katılıp konuşmaları dinlemek, kimin ne
dediğini ayırmak
Toplantıdan karar, aksiyon, sorumlu ve tarih çıkarıp karar
kaydına bağlamak
Söylenen bir iddia veriyle çeliştiğinde kanıtlı ve diskret
uyarı vermek
Karara karşıt akıl olarak kör noktaları ve bilişsel
yanılsamaları raporlamak
## ✕ HENÜZ YAPMAZ
Kararı veto etmez, engellemez — yalnız uyarır ve itiraz
eder
Rıza alınmadan kayıt yapmaz; opt-out eden katılımcıyı
işlemez
Kişi bazlı performans değerlendirmesi yapmaz
Ses verisini kurum dışına çıkarmaz (yerel model)
Gelen yetenekler
Toplantı ajanı: platform entegrasyonu, yerel STT ve konuşmacı ayrımı
Toplantıdan karar/aksiyon/sorumlu çıkarımı → Karar Kaydı'na akış
Canlı müdahale: veriyle çelişen ifadede kanıtlı uyarı
Red Team (Şeytanın Avukatı): kör nokta raporu
Bilişsel yanılsama sensörü (batık maliyet, grup düşüncesi)
Örnek kullanım — bu sürüm sahada nasıl görünür
Toplantıda...o bölgede 5 şube açalım, bütçeyi zorlamaz.
Dima (ekran kenarı)
Bu karar Q3 yatırım bütçesini %12 aşıyor (kanıt: bütçe_gerceklesme metriği).
Toplantı sonrası(otomatik) 3 karar, 7 aksiyon, 2 açık soru çıkarıldı. Kararlardan biri Karar Kaydı'na aday.
Dima (Red Team)
Bu karara dair 3 kör nokta: (1) 2023'te aynı bölgede açılan 2 şube 14 ayda kapandı, (2) bölgedeki en
büyük müşterimiz sözleşme yenilemedi, (3) toplantıda finans müdürünün dile getirdiği nakit çekincesi karşılıksız kaldı.
Tipik gün: Yönetim kurulu, kimsenin yüksek sesle söylemediği itirazı masada görür; karar aynı gün kayda geçer.
Kim içinHoldingler, yönetim kurulları, strateji ve risk komiteleri
Konumlandırma“Toplantıdaki tek tarafsız akıl.”
Rakibe darbeSığ ‘AI not-taker’ araçlarını veri bağlantısızlığıyla anlamsız kılmak
Ticari anlamıRakiplerin ulaşamayacağı yer burasıdır: not alan araçlar veriye bağlı değildir, veriye bağlı araçlar
toplantıda değildir.
Ana riskiHukuki risk en yüksek fazdır. 11.1 (rıza, aydınlatma, saklama) tamamlanmadan tek satır kod
yazılmamalıdır.
Geçiş kapısıToplantı kararlarının Karar Kaydı'na akması; Red Team önerilerinin karar değiştirme oranı
## · FAZ 11
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası100 / 126

## VİZYON · MİSYON · NİHAİ KONUMLANDIRMA
Vizyon: Her kurumun; kendi verisinden, hafızasından ve konuşmalarından beslenen, kararlarını kanıtlayabilen bir beyni
olması.
Misyon: Kurumsal kararı sezgiden kanıta taşımak — veriyi kurumdan çıkarmadan, uydurmadan, her adımı denetlenebilir
kılarak.
Nihai konumlandırma: Dima bir iş zekâsı aracı değil, kurumun Denetlenebilir Karar ve Kontrol Merkezidir; nihai
halinde şirketin veritabanını, hafızasını, toplantısını, prosedürünü ve stratejisini tek bir denetlenebilir akılda birleştiren
## Kurumsal Yapay Zekâ İşletim Sistemi.
Ürün özü (değişmeyen): Hız → Güven → Muhakeme → Karar → Hafıza. Her sürüm bir öncekinin üstüne bunlardan birini
ekler; hiçbiri öncekini bozmaz.
v6  KÜLLİ ŞİRKET BEYNİ · Enterprise AI OS
Şirketin dijital ikizi kurulur. Sistem gece veriyi tarayıp sormadığınız fırsatları getirir, kriz senaryolarında dayanma
sürenizi hesaplar, kurucunun ilkelerini hatırlar, mevzuat değişikliklerini yakalar ve sektör ortalamasıyla kıyaslar.
## ✓ BU SÜRÜMDE YAPAR
Gece veriyi tarayıp sormadığınız fırsatları sabah önünüze
getirmek
Şirketin dijital ikizi üzerinde kriz senaryosu koşup
dayanma süresini hesaplamak
Kurucunun ilkelerini ve geçmiş karar mantığını yıllar
sonra hatırlatmak
Anonim sektör havuzuyla kıyaslamak ('su tüketiminiz
benzer ölçekte %18 yüksek')
Mevzuat değişikliğini yakalayıp etkilenen kuralı bildirmek
## ✕ HENÜZ YAPMAZ
Hiçbir kararı tek başına vermez; gölge kurul görüşü bile
veto değil ikinci-imza tetikleyicisidir
Ham müşteri verisini havuza koymaz; yalnız k-anonim
toplulaştırılmış istatistik
Kişi bazlı iletişim/performans takibi yapmaz
Hukuki tavsiye vermez; mevzuat çıktısı bilgilendirmedir
Gelen yetenekler
Hipotez ve fırsat keşif motoru (gece taraması, sabah bildirimi)
Dijital ikiz ve siyah kuğu kriz simülasyonları
Kurucu hafızası ve gölge kurul değerlendirmesi (veto değil, ikinci imza)
Anonim sektör kıyası (k-anonimlik korumalı)
Durum çatallama: paralel senaryo evrenleri (Git dalı gibi)
İleri iş motorları: pazarlık, marj kalkanı, micro-churn, sözleşme eleği (Faz 12B)
Sürekli mevzuat kalkanı ve çok modlu saha verisi
Örnek kullanım — bu sürüm sahada nasıl görünür
Dima (sabah bildirimi)
Dün gece 4.100 kombinasyon tarandı. X ürününü alan müşterilerin %34'ü Y hizmetini de alıyor ama
61 müşteriye bu teklif hiç yapılmamış. Tahmini yıllık etki: 8,5M TL. Kampanya taslağı hazırlayayım mı?
KullanıcıDolar bir gecede %30 artarsa?
## Dima
Mevcut nakit ve açık pozisyonla dayanma süresi 41 gün. İlk kırılma tedarik ödemelerinde. B planı taslağı: 3 ödeme
ötelenirse süre 78 güne çıkıyor.
Yeni GMKurucumuz 2021 krizinde tedarikçi pazarlığını nasıl yönetmişti?
## Dima
Kayıtlı 3 ilke: (1) vade uzatmak yerine hacim taahhüdü ver... (kaynak: Founder Cortex, 14 Eki 2021 karar kaydı)
Tipik gün: CEO sabah telefonuna bakar; gece kimsenin fark etmediği bir fırsat ve bir risk zaten önündedir.
Kim içinGlobal kurumsal, holding, çok tesisli üretici
Konumlandırma“Şirketinizin yaşayan, sorgulayan, hatırlayan beyni.”
Rakibe darbeSistemin sökülüp atılmasını imkânsız kılan kurumsal organik bağımlılık
Ticari anlamıKategori sahipliği bu sürümle gelir: artık bir yazılım değil, kurumsal işletim sistemi konuşulur.
Ana riskiKapsam patlaması riski. Bu fazın parçaları ancak v3-v4 gerçek müşteride oturduktan sonra sıraya
alınmalıdır.
Geçiş kapısıKurumsal hafıza + denetim tarihçesi + benchmark üçlüsü tam; kategori sahipliği
## · FAZ 12–12B
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası101 / 126

DEĞİŞMEZ KURALLAR — vizyon büyürken korunacak dört çizgi
İki Düzlem Garantisi: ERP kesinliği (磊 Gold) ile toplantı/haber/duyum (Bağlam Notu) hiçbir çıktıda karışmaz.
Bu kural bozulursa ürünün tüm değeri çöker (görev 10.1).
Veri egemenliği: Ses, transkript, doküman dahil hiçbir ham içerik kurum dışına çıkmaz; on-prem/yerel model
tercih edilir.
İnsan imzası: Dima karar vermez, veto etmez — çerçeveler, kanıtlar, uyarır, kaydeder. ‘Gölge kurul’ bile veto
değil ikinci-imza tetikleyicisidir.
Hukuki kapı: Toplantı dinleme, çalışan iletişimi analizi ve kolektif veri paylaşımı, yazılı hukuki dayanak ve açık
rıza olmadan devreye alınmaz (görev 11.1, 12.7, 12.9).
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası102 / 126

TİCARİ STRATEJİ · 1 · Sürüm × Pazar × Fiyat Eşlemesi
Bu tablo, dosyanın iki yarısını birbirine bağlar: soldaki teknik fazlar hangi ticari
sonucu doğurur. Yeni bir faza başlamadan önce buradan kontrol edin — inşa ettiğiniz şeyin kime, hangi fiyatla satılacağı belli
değilse o faz erkendir.
SürümFazlarKime satılırHangi paket
Yıllık büyüklük
## (öneri)
Ticari kilometre taşı
v10–3Raporu hazırlayan
şampiyon + patron
## Başlangıç /
## Profesyonel
## $2.280 – $5.400
+ kurulum
İlk 5–8 ödeyen müşteri, 1
yayınlanmış vaka
v23B–6C-Level, operasyon ve
satış direktörleri
Profesyonel$5.400 + kurulum
## $4.500
15–20 müşteri; fiyat çıpası
analist maaşına taşınır
v36B–9BYönetim kurulu, CFO/GM,
regüle kurumlar
Kurumsal / On-Prem$11.880 –
## $22.800+
Kurumsal sözleşme; denetim
geçmişi birikmeye başlar
v410İK, operasyon, denetim
ve danışmanlık
## Kurumsal + Bilgi
Hub eklentisi
+%20–30 paket
primi
Churn ≈ 0; kurumsal hafıza
kilidi devreye girer
v511Holding, yönetim kurulu,
risk komitesi
On-Prem /
## Kurumsal+
## $22.800+
(oturum bazlı)
Toplantı kararlarının Karar
Kaydı'na akması
v612–
## 12B
Global kurumsal, çok
tesisli üretici
Kurumsal+ / özelSözleşme bazlıKategori sahipliği; benchmark
tekeli
Kural: ürün sürümü ile fiyat katmanı birlikte yükselir
v1'i kurumsal fiyattan satmaya çalışmak (henüz denetim katmanı yokken) güveni yakar; v3'ü başlangıç fiyatından satmak
ise kurulum ve destek maliyetini karşılamaz. Her sürüm kendi paketiyle satılır. Kurulum ücreti sürümden bağımsızdır
— anlamlandırma emeği her zaman ücretlendirilir (bkz. bölüm T9).
ürün ile ticaretin birleştiği yer
DİMA · 0→100 Görev Takip Dosyası103 / 126

TİCARİ STRATEJİ · 2 · Pazar Teşhisi ve Rekabet
Gerçek rakip yazılım değil, statüko
Dima'nın en büyük rakibi Snowflake ya da ChatGPT değil; mevcut düzen: Excel + 'IT'ye rapor talebi aç' + 'analist alalım'
+ 'patron sezgisiyle karar verir'. Statükonun gücü kimseyi kovdurmamasıdır. O yüzden savaş özellik savaşı değil
alışkanlık değiştirme savaşıdır — ve alışkanlık ancak akut, tekrarlayan, ölçülebilir bir acıdan kırılır. Stratejinin tamamı
bu cümleye yaslanır; ürün tarafındaki karşılığı truva atı özelliğidir: patronun her hafta istediği o tek rapor.
Üç katmanlı değer merdiveni — satış sırası da budur
KatmanVaatKime satar
## Üründeki
karşılığı
## Kanıt
1 · HızGünler süren rapor saniyeye inerŞampiyon (raporu
hazırlayan)
v1 · Faz 1–3Kendi raporlarıyla
demo
2 · GüvenUydurmaz, kaynağı gösterir,
bilmediğinde susar
Patron + IT + denetçiv1–v3 · Faz 2.15–
## 2.19, 7
Kanıt kartı, altın yol,
## DCM
## 3 ·
## Muhakeme
Yorumlar, kök-neden bulur, öngörür,
karar kaydeder
Kurul / CFOv2–v3 · Faz 4–6BSWOT, kök-neden,
## Karar Kaydı
Sıra önemlidir: hızla kapıyı aç, güvenle kalıcı ol, muhakemeyle vazgeçilmez ol. Muhakemeyi ilk turda satmak
inandırıcılığı düşürür.
Rekabet manzarası ve boşluk
OyuncuGücüBizim için açığı
Hyperscaler-native (Snowflake Cortex,
Databricks Genie, Power BI Copilot)
Olgun motor, dev bütçe,
ekosistem
Veri yabancı bulutta · kara-kutu model · Türkçe/
KVKK yok · kendi warehouse'una kilitli
Wren AI (açık motor)Apache çekirdek, agent-
native, hızlı
Egemenlik/Türkçe/KVKK yok; ürün değil motor
— zaten bizim altımızda
oneAgent (Almanya)Egemenlik modelini kanıtlıyor
(GDPR + yerel hosting)
Türkiye/Türkçe/KVKK'da yok — model
kanıtlandı, saha boş
Yerel KVKK/BGYS satıcılarıKurumsal hesaplar, uyum
güveni
Konuşan/agentic karar katmanı yok — yalnız
uyum yazılımı
Yeni girenlerHız, çeviklikOdak dağınık; kimse 'egemen + kanıtlanabilir
karar merkezi' kategorisini sahiplenmemiş
Pazar anı ve pencerenin ömrü
KVKK 12 Mart 2026'da Etken Yapay Zekâ (Agentic AI) rehberini yayımladı; ceza tavanı 17.092.242 TL, ihlal bildirimi
72 saat, ve şeffaflık ilkesi gereği kararın algoritmik mantığı açıklanabilir olmalı. Bu, Dima'nın mimarisini bir 'özellik'
olmaktan çıkarıp mevzuat cevabı haline getirdi.
Pencere ne kadar açık: Hyperscaler'lar bir gün TR/EU bölgesi açarsa 'veri çıkmaz' argümanı zayıflar. Bu yüzden hendeği
yalnız egemenliğe değil hafıza + benchmark + dikey pakete kaydırıyoruz (v4–v6). Yeni girenlerin yapamayacağı şey
birikmiş denetim tarihçesi ve sektör kıyas verisidir — bu yalnız zamanla kazanılır. Varsayım: 12–18 aylık öncelik
penceresi. Hedef pazar payı değil; ilk 20 referans ve bir dikeyde kaçınılmazlık.
Dürüst kısıtlarımız (strateji bunları hesaba katar)
5 kişi, bilinmeyen marka → tepeden kurumsal satış ve pazar-eğitimi bize göre değil.
Değer, DB bağlama + anlamlandırma sonrası doğuyor → saf self-serve viralite kırılır (asistanlı melez şart).
Doğrulama borcu: Ürün henüz ödeme yapan gerçek müşteride uçtan uca kanıtlanmadı. Strateji ne kadar iyi olursa
olsun ilk 2-3 deniz feneri gelmeden tekelleşme başlamaz.
gerçekte neredeyiz
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası104 / 126

TİCARİ STRATEJİ · 3 · Marka Kimliği, Konumlama ve Dil
Konumlama cümlesi (iç referans)
“Verisi olan ama cevabı olmayan orta-büyük Türk şirketleri için Dima, sorularını kendi dilinde sorup kaynağı kanıtlanmış
cevap alabildikleri denetlenebilir karar merkezidir — dashboard'lardan farkı soru sorabilmeniz, genel yapay zekâdan
farkı verinizin çıkmaması ve uydurmamasıdır.”
Mesaj hiyerarşisi: bir öz, üç sütun, her sütuna kanıt
SütunMesajDemoda gösterilen kanıt
Hangi görev
üretir
HızSorun, saniyede cevap — IT kuyruğu yokKendi raporları canlı; 3 saniyede sonuç1.11 · 2.1 · 2.11
GüvenUydurmaz; kaynağı gösterir; bilmiyorsa susarKanıt kartı + 'bunu veriniz söylemiyor'
anı
## 2.15 · 2.16 · 7.1 ·
## 7.3
EgemenlikVeriniz şirketten çıkmaz; AI kapalıyken de
çalışır
İki-düzlem mimarisi + DCM modu2.12 · 4.12 · 7.4
Üç kitle, üç ayrı anlatı (aynı ürün)
KitleKorkusu / arzusuAçılış cümlesi
Patron / sahipKandırılmak; rakamların süslenmesi; mahcup
olmak
“Rakamları senin yerine kimse süsleyemez.”
## Şampiyon
## (raporcu)
İşsiz kalmak; görünmez emek“Seni değiştirmez — patronun gözünde yıldız yapar.”
IT / veri ekibiKontrol kaybı; gölge-BT; sorumluluk“Kim neye erişiyor, hangi soru nereye gitti — kontrol
sende.”
Kategori stratejisi: icat değil, kaçırma
5 kişilik ekip için sıfırdan kategori icat etmek (pazarı tek başına eğitmek) kibirdir. Bunun yerine kategori kaçırma:
hyperscaler'lar milyon dolar harcayıp 'AI ile veri sorgulama' talebini yaratsın; biz her talebin üstüne tek cümleyle oturalım:
“Evet, aynısı — ama veriniz çıkmadan ve kanıtlanabilir.”
Sahiplenilecek kelimelerKaçınılacak kelimelerAsla söylenmeyecek
kanıtlanabilir cevap · veri şirketten çıkmaz ·
uydurmayan yapay zekâ · denetlenebilir
karar · şirketin beyni
BI aracı · dashboard · chatbot ·
raporlama yazılımı (hepsi emtia
rafına koyar, fiyatı düşürür)
“her şeyi yapar” · “tam otonom” ·
“insana gerek kalmaz” (inandırıcılık +
düzenleyici riski)
Marka dili: cesur otorite
Kışkırtıcı ama kanıtlı. Kural: her iddia bir kanıta veya sayıya yaslanır; sıfat değil, kanıt satarız.
Başlık bankası (kampanya / landing / LinkedIn)
“Şirket verinizi yapay zekâya yüklüyorsanız, aslında yurt dışına gönderiyorsunuz.”
“Toplantıda bir daha ‘bilmiyorum, kontrol edip döneyim’ demeyin.”
“Rakamları sizin yerinize kimse süsleyemez.”
“Yapay zekânız bu cevabı nereden buldu? Kanıtlayabiliyor musunuz?”
“Veri analisti ilanınızı kapatmadan önce iki hafta bize verin.”
Konuşma dili kuralları (Türkiye gerçeği)
Patronla sonuç ve para dili; müdürle zaman ve statü dili; IT ile kontrol ve güvenlik dili. Aynı slaytı üçüne
gösterme.
Teknik jargonu (LLM, RAG, semantic layer, MDL) müşteri tarafında kullanma — yalnız IT odasında.
WhatsApp'ta kısa ve somut; e-posta uzun ve resmi; 40 saniyelik ekran kaydı her ikisinden güçlü.
Abartı yerine eksiltme: “bu kadarını yapar, şunu yapmaz” demek Türk patronunda güveni artırır.
kim olduğumuz, nasıl konuşuruz
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası105 / 126

Kurucu içerik motoru (haftalık ritim)
FormatSıklıkİçerik
LinkedIn kısa yazıHaftada 2–3Bir gerçek Kurul kararı / bir müşteri anekdotu / bir 'veri yalanı' örneği
40 sn ekran kaydıHaftada 1Tek soru → tek cevap → kanıt kartı; jenerik değil sektöre özel
Uzun analiz / raporAyda 1'Türkiye Kurumsal AI & KVKK' serisi — atıf alınacak kaynak
Webinar (partnerle)Ayda 1KVKK danışmanı veya mali müşavirle ortak; onun kitlesi, senin çözümün
Üstat notu · markanın üç katmanı ve hangi sırayla inşa edileceği
Marka, logo değil tekrartır. Üç katman sırayla kurulur, atlanamaz:
1 · Tanınırlık (0–6 ay): kurucunun yüzü + tek cümle + tek görsel dil. Bu aşamada 'ne yaptığımız' değil 'kim olduğumuz'
akılda kalmalı. Ölçüt: hedef listedeki 30 firmanın 10'u adı duymuş olmalı.
2 · Anlam (6–18 ay): kelimeyi sahiplen — 'kanıtlanabilir cevap'. Ölçüt: müşteri kendi cümlesiyle bizi anlatabilmeli ('bu,
kaynağını gösteren AI'). Anlam katmanı vaka çalışmalarıyla inşa edilir, reklamla değil.
3 · Standart (18+ ay): ölçüt hâline gel — 'Dima Verified' ve şartnamelerde geçen maddeler. Ölçüt: bizi kullanmayan
firmalar bile bizim kriterlerimizle konuşmalı.
Sık yapılan hata: 3. katmanı 1. katmandayken denemek (kimse tanımıyorken standart dayatmak) — kibirli görünür ve
boşa düşer.
Üstat notu · isim, dil ve görsel kimlikte kaçınılacak tuzaklar
Türkçe-İngilizce kararsızlığı: Ürün adı sabit (Dima), ama arayüz ve dokümanlar tamamen Türkçe olmalı. Yarı
İngilizce arayüz, KOBİ patronunda 'bu bana göre değil' hissi yaratır — en pahalı sessiz kayıp budur.
Teknoloji övünmesi: 'Rust motor', 'semantic layer', 'agentic' kelimeleri müşteri tarafında değer değil mesafe
üretir. Bunlar yalnız IT odasında ve teknik şartnamede kullanılır.
Aşırı kurumsal görsel dil: Bilinmeyen bir markanın holding gibi görünmeye çalışması güven değil şüphe üretir.
Doğru ton: ciddi ama insan; kurucunun gerçek fotoğrafı, gerçek müşteri sözü, gerçek rakam.
Slogan enflasyonu: Tek cümlede kal. Üç farklı slogan, sıfır slogan demektir.
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası106 / 126

TİCARİ STRATEJİ · 4 · Hedef Kitle, Anti-ICP ve Tetikleyiciler
Firmografik filtre (ICP)
Ölçek: 50–500 çalışan; yaklaşık 100M–2B TL ciro bandı.
Ön şart: ERP zaten var (Logo / Netsis / Mikro / SAP) — veri bir yerde duruyor.
Karmaşıklık: Birden fazla şube, hat, depo veya ürün grubu. Karmaşıklık = acı = bütçe.
Acı kanıtı: En az bir kişi haftada 8+ saatini Excel'de rapor hazırlamaya veriyor.
Anti-ICP — kimi kovalamayacağız (bu liste ICP'den değerli)
ERP'si olmayan firmalar → veri kaosu → başarısız proje → kötü referans.
20 kişiden küçük işletmeler → bütçe yok, veri yok, karar süreci yok.
Tek şubeli, tek ürünlü basit işler → acı yok, ödeme isteği yok.
Patronun rakamlara zaten bakmadığı şirketler → satarsın, kullanılmaz, iptal eder. En sinsi tuzak budur.
“Önce bir POC yapalım, sonra bakarız” diyen ama bütçe sahibi olmayan muhataplar.
Karar birimi: kim kullanır, kim imzalar, kim engeller
RolKonumuNe satarızÜründe karşılığı
Şampiyon (birim/orta yönetici,
raporcu)
Kullanır, içeride yayarGüç + statü + 'bilmiyorum'
demeden karar
v1 hız katmanı, kişisel
hafıza (3.7)
Ekonomik alıcı (CFO/GM/
patron)
Bütçeyi onaylarDanışmanlık maliyeti + risk
düşüşü + hız
Karar Kaydı (6B.8), kanıt
kartı
Engelleyici (IT/veri ekibi)Erişimi tutar, tehdit
hisseder
'Seni değiştirmez, seni çoğaltır' +
yönetişim
RLS/audit paneli (7.5, 7.6)
Satın alma tetikleyicileri — 'ne zaman' sorusunun cevabı
TetikleyiciNeden güçlüNasıl tespit edilir
‘Veri Analisti / Raporlama
Uzmanı’ ilanı
Acıyı kamuya itiraf etmiş + bütçe ayrılmış +
konu gündemde
Kariyer.net / LinkedIn ilan taraması
## (haftalık)
Kuşak değişimi (2./3. nesil)Modernleşmeyi kanıtlama baskısı + AI'a güven
+ yetki
Basın, dernek haberleri, LinkedIn
unvan değişimi
Yeni CFO / GMİlk 90 günde hızlı zafer arıyorLinkedIn iş değişikliği bildirimleri
ERP geçişi yeni bittiVeri temiz, dönüşüm bütçesi hâlâ açıkERP bayisi kanalı — en iyi haber
kaynağı
Denetim / kredi / müşteri
denetimi
Kanıt üretme zorunluluğuSektör takvimi, bağımsız denetim
dönemleri
Patron toplantıda mahcup
oldu
En güçlü duygusal kancaYalnız sohbette çıkar — keşif
sorusuyla avlanır
Av sahaları: isim listesi çıkan kaynaklar
“Kurumsal hesaplar” soyuttur; şunlar somut isim listesi verir: İSO 500 / İkinci 500 (tam hedef ölçekte üretici), OSB firma
rehberleri,  TİM ihracatçı listeleri,  sektör dernek üye listeleri,  ERP bayilerinin müşteri portföyü ve   iş ilanı
siteleri (canlı acı radarı).
kimi, ne zaman, nereden
## •
## •
## •
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası107 / 126

TİCARİ STRATEJİ · 5 · Pazara Giriş Modeli ve Kanallar
Neden tepeden (Palantir) değil: O model dev satış ordusu, kurumsal
marka güveni ve büyük sermaye ister — bizim en zayıf üç yerimiz. Neden aşağıdan (Slack): Ürün anında değer
gösterir, risk düşük, şampiyon içeriden yukarı satar. Neden saf değil melez: Değer, DB bağlama + anlamlandırma
sonrası doğduğu için hafif asistanlı bir el şarttır — bu da üründe kurulum sihirbazıdır (Faz 1).
İlk 10 müşterinin mekaniği
DönemHamleÇıktı
Hafta 1–4Tek dikey + tek coğrafya seç; isim isim 30 firmalık hedef
listesi (İSO/OSB/dernek + ilan taraması)
30 isim, 30 tetikleyici notu
## Hafta 4–
## 10
Kurucu-liderliğinde temas (ilan / kuşak / bedava içgörü kancaları);
keşif görüşmeleri
5 keşif, 2 design partner
## Hafta 10–
## 20
Takıntılı teslim; haftalık kullanım takibi; vaka çalışması üretimi1 vaka + 2 sıcak tanıştırma
## Hafta 20–
## 30
Aynı OSB/dernekte yoğunlaşma; kanal aktivasyonu5–8 ödeyen müşteri; ERP bayisine 'X ve Y
bizi kullanıyor' girişi
Kural: ilk 10 müşteri satışçıyla değil kurucuyla kapanır
İtirazları, kelimeleri, tereddüt anlarını birebir öğrenmek için. Satış ekibi ancak oyun kitabı (bölüm T6) gerçek konuşmalardan
yazıldıktan sonra kurulur. Erken işe alınan satışçı, olmayan bir oyun kitabını satmaya çalışır ve yanar.
Tepeden modele geçiş eşiği
Palantir-tarzı tepeden giriş kapatılmaz, ertelenir. Tetik üçlüsü: (a) 5+ gösterilebilir deniz feneri, (b) bir dikeyde/bölgede
tanınırlık, (c) kurumsal satışı finanse edecek runway. Bu üçü birikince regüle/kurumsal segmente tepeden girilir. Ürün
tarafında karşılığı v3'ün tamamlanmasıdır (Faz 7 güven katmanı olmadan regüle kapı açılmaz).
Kanal stratejisi: başkasının dağıtımına yapış
KanalOnlara ne satarız (WIIFM)Aktivasyon mekaniğiKomisyon/model
Mali müşavirMüşterisine katma değer +
danışmanlık geliri + canlı finansal
görünüm
5–10 müşavirle pilot; ortak
markalı aylık 'firma karnesi'
Tavsiye başına gelir payı;
ilk yıl %15–20
KVKK danışmanı /
veri avukatı
Korkuttuğu müşteriye satacak
somut çözüm
Ortak webinar + risk taraması
aracını onların markasıyla sun
Gelir payı + ortak vaka
ERP bayisi (Logo/
Netsis/SAP)
Yeni hizmet günü + portföyden ek
gelir; 'AI' talebine cevap
Bayi teknik ekibine 1 günlük
eğitim + demo ortamı + satış
kiti
Yeniden satış marjı %25–
35 veya beraber satış
Sektör derneği /
oda
Üyelerine değer, etkinlik içeriğiStant değil: rapor sponsorluğu
ve sahne konuşması
Ücretsiz içerik karşılığı
erişim
Sigorta / hukuk
## (özgün)
Ölçülebilir risk düşüşü / bilirkişi
kolaylığı
Denetim izi olan müşteri için
prim indirimi görüşmesi
Hukuki teyit sonrası
tasarlanacak
Kanal işletme kuralları
Kanal çatışması önleme: Kayıt (deal registration) zorunlu — ilk kaydeden partnerin. Yazılı kural olmazsa kanal
küser.
Partner etkinleştirme kiti: 10 slaytlık sunum, 3 dakikalık demo videosu, itiraz bankası, fiyat tablosu, 1 sayfalık
broşür. Kitsiz partner satmaz.
Kademe: Kayıtlı → Yetkin (2 satış + eğitim) → Elit (5+ satış). Kademe komisyonu ve öncelikli desteği belirler.
Tek kanal bağımlılığı yasak: Hiçbir kanal cironun %40'ını geçmesin; geçerse fiyatı ve şartları onlar belirlemeye
başlar.
Üstat notu · 'yoğunluk' matematiği — neden tek OSB, tek dernek?
Dağınık 20 müşteri, tek bölgede 6 müşteriden daha az değerlidir. Sebep: referans ancak aynı çevrede çalışır. Bir OSB'de
3 firma sizi kullanıyorsa dördüncüsü için satış görüşmesi değil, teyit görüşmesi yaparsınız. Ayrıca destek maliyeti düşer
aşağıdan-yukarı, asistanlı melez
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası108 / 126

(aynı ERP, aynı sektör, aynı sorunlar), sektör paketi ikinci müşteride bedavaya kurulur, ve tek bir etkinlikle 10 hedefe
birden ulaşırsınız.
Ölçüt: Bir bölgede/dikeyde %20 penetrasyon, ülke genelinde %1'den kıymetlidir. Kural: ikinci bölgeye, birinci bölgede 5
referans olmadan geçilmez.
Üstat notu · satış döngüsünü kısaltan üç yapısal hamle
Pilotu ürünleştir: 'Pilot' kelimesi belirsizlik üretir. Bunun yerine paketlenmiş bir teklif: '6 haftalık Karar Hızlandırma
Programı — kurulum + 3 metrik + 1 pano + eğitim, sabit fiyat, sonunda karar sizin.' Aynı iş, ama satın alınabilir bir
nesne hâline gelir ve onay süreci kısalır.
Bütçe kalemini önceden seç: Müşteri 'hangi bütçeden çıkacak' diye takılır. Cevabı sen ver: danışmanlık, dijital
dönüşüm, IT bakım veya KOSGEB destekli yatırım. Doğru kalemi önermek 2-3 hafta kazandırır.
Karar vericiyi ilk toplantıda masaya al: Şampiyonla 3 toplantı yapıp sonra patrona çıkmak döngüyü ikiye katlar.
Kural: 2. toplantıda imza yetkisi olan kişi yoksa, satış değil eğitim yapıyorsundur.
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası109 / 126

TİCARİ STRATEJİ · 6 · Satış Oyun Kitabı
Satış akışı: 5 adım
Kanca (ilan / kuşak / bedava içgörü) → 15 dk keşif görüşmesi.
Keşif:    “Geçen hafta hangi soruya cevap ararken en çok zaman kaybettiniz?” + “O raporu kim hazırlıyor, ne kadar
sürüyor?” + “Cevaba güveniyor musunuz?”
Rapor cenazesi demosu: Onların gerçek Excel'iyle kurulmuş demo.
Ücretli pilot: 6–8 hafta, başarı kriteri önceden yazılı.
Kapanış: Kriter tuttu mu → yıllık sözleşme + referans maddesi.
Rapor cenazesi demosu — kapanış oranını katlayan tek taktik
Toplantıdan önce firmanın en çok acı çektiği haftalık Excel'ini iste ('hazırlık için').
Dima'da kur; demoyu jenerik veriyle değil onların kendi verisiyle aç.
İlk 60 saniyede kendi rakamlarını görsünler — ürünü değil, kendi hayatlarını izlerler.
Bilinçli olarak bir soruya 'bunu veriniz söylemiyor' dedirt: dürüstlük anı, en güçlü satış anıdır (görev 2.16).
Kapanışta kanıt kartını aç: 'bu rakam nereden geldi' — patron için gerçek kilit budur (görev 2.15).
İtiraz bankası (birebir cevaplar)
İtirazCevap
“Pahalı”“Bir raporlama uzmanının aylık maliyeti X. Dima'nın yıllık bedeli onun iki aylık maliyeti — ve
izne çıkmaz, istifa etmez.”
“Verimiz dağınık”“Herkesin verisi dağınık; temizlenmesini bekleyen kimse ilerlemiyor. Sihirbaz sizinle birlikte
anlamlandırır; tek tablodan başlarız.”
“IT izin vermez”IT'yi toplantıya çağır, kontrol panelini göster: erişim, RLS, denetim izi. “Kontrol sizde kalıyor.”
“AI uyduruyor”“Haklısınız — o yüzden altın yolda AI SQL bile yazmaz; her cevabın kaynağı görünür,
bilmediğinde susar.” Canlı göster.
“KVKK riski”“Veri şirketten çıkmıyor; istersen yapay zekâyı tamamen kapatıp çalıştırırız. Kanıtı da her
cevabın altında.”
“Küçük firmasınız,
batarsanız?”
“Model ve tanımlarınız sizin deponuzda (Git), veriniz sizde, dışa aktarım garantili. Kaynak-
emanet (escrow) maddesi de koyabiliriz.”
“ERP'de zaten rapor var”“Var — kaç tıkla ve kaç günde? Yeni bir soru sorduğunuzda ne oluyor?” Kuyruk acısını
konuştur.
“Şimdi sırası değil”Tetikleyiciye bağla: bütçe dönemi, denetim, ilan, yeni yönetici. “Gelecek yılın altyapısını bu
bütçede konuşalım.”
“Bedava deneyelim”“Pilot ücretli ama başarı kriterine bağlı: kriter tutmazsa devam etmezsiniz.” Bedava pilot,
sahipsiz pilottur.
Battle card: rakip bazlı karşı hamleler
Karşı tarafOnların iddiasıBizim tek cümlemiz
ChatGPT / genel AI“Zaten
kullanıyoruz”
“Aynı soruyu ikisine soralım: biri uydurur, biri kaynağını gösterir. Ayrıca
yüklediğiniz veri yurt dışına gidiyor.”
Power BI / mevcut
## BI
“Dashboard'umuz
var”
“Dashboard soru sormaz, siz sorarsınız — ve yeni her soru IT kuyruğunda iki
hafta bekler.”
## Snowflake /
## Databricks
“Kurumsal standart”“Önce tüm veriyi onların bulutuna taşımanız gerekiyor: göç projesi + yurt dışı
veri ikameti. Biz mevcut veritabanınızın üstünde çalışırız.”
Yerel ajans /
custom proje
“Bize özel yaptırırız”“6 ay proje, tek kişiye bağımlılık, bakım yok. Bizde iki hafta ve sürekli gelişen
ürün.”
akış, demo, itiraz bankası, battle card
## 1.
## 2.
## 3.
## 4.
## 5.
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası110 / 126

Karşı tarafOnların iddiasıBizim tek cümlemiz
‘Analist alalım’“İnsan alırız”“Aramak 6 ay, kalması ortalama kısa, bilgisi giderken gidiyor. Dima gitmez ve
her ay keskinleşir.”
Yeni rakip startup“Aynısını yapıyoruz”Üç test sorusu: “Veri nerede işleniyor? Cevabın kanıtı var mı? AI kapalıyken
çalışıyor mu?”
Üstat notu · fiyat konuşmasının koreografisi
Fiyat,    değer kurulmadan söylendiği an pahalıdır; çok geç söylendiğinde ise güvensizlik üretir. Doğru sıra: (1) acıyı
sayısallaştır ('haftada 8 saat × 4 hafta × kişi maliyeti'), (2) alternatifin maliyetini hatırlat (analist maaşı, danışmanlık
faturası, yanlış karar), (3) fiyatı bu iki sayının arasında konumla, (4) hemen ardından kurulum kapsamını anlat (fiyatın
karşılığını somutlaştırır).
İndirim istendiğinde ilk cevap asla evet ya da hayır olmamalı:'Neyi çıkarırsak bu fiyata olur?' Kapsamı küçültmek,
fiyatı düşürmekten her zaman iyidir — çünkü fiyat bir kez düşerse bir daha yükselmez, kapsam ise sonradan satılır.
Üstat notu · kaybedilen satıştan değer çıkarmak
Her kayıpta tek soru sor: 'Bizi seçmemenize sebep olan tek şey neydi?' — çoğul sorma, tek sebep iste; gerçek
cevap oradan çıkar.
Kayıpları üç kovaya ayır: zamanlama (6 ay sonra tekrar ara), güven (referans eksikliği — vaka üret), ürün   (gerçek
eksik — faz haritasına yaz). Üçü farklı aksiyon gerektirir; hepsine 'pahalı bulundu' demek en yaygın hatadır.
Kaybedilen müşteriyi listeden silme; 90 gün sonra bir içgörüyle geri dön (satış değil, değer). Türkiye'de ikinci
temas dönüşümü yüksektir.
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası111 / 126

TİCARİ STRATEJİ · 7 · Pazarlama, İçerik ve Gerilla
Hamleİnfaz adımlarıAmaç
İş ilanı avcılığıHaftalık ilan taraması → firmaya kişisel mesaj: 'bu pozisyonu 6 ayda
zor bulursunuz; 2 hafta bize verin'
En keskin lead kaynağı
Bedava içgörü'Bir Excel gönderin, 3 içgörü çıkarıp ücretsiz göndereyim'Sürtünmesiz değer
gösterimi
## Halüsinasyon
düellosu
Aynı şirket sorusu: genel AI vs Dima; ekran kaydı; kısa videoFarkı 30 saniyede kanıtla
KVKK risk taraması
aracı
Web'de 8 soruluk mini test → rapor + randevu çağrısıLead motoru + korku
üretimi
'Model provenance'
talebi
'AI'ınız hangi modele gitti, kanıtlayabiliyor musunuz?' kampanyasıRakip mimarisi bu testi
geçemez
OSB baskınıTek OSB seç; 2–3 firma kap; yerel etkinlik + saha ziyaretleriYoğunluk = bölgesel
kaçınılmazlık
Deniz feneri vaka
tiyatrosu
Video vaka + rakam + patron ağzından tek cümleB2B'de en güçlü kanıt
Dima Verified rozetiMüşteri sitesine asacağı KVKK-güvenli AI mührüStandart olma hamlesi
## Dima Verimlilik
## Raporu
Aylık: 'sorularınızın %71'i AI'sız cevaplandı, maliyet %38
düştü' (görev 8.17)
Rakibin üretemeyeceği
belge
Türkiye kaldıraçları
KOSGEB / dijital dönüşüm destekleri → 'destek kapsamında' konumlama maliyet bariyerini düşürür.
WhatsApp-öncelikli ritim → karar verici e-postadan çok oraya bakar; 40 sn video en yüksek dönüşümlü format.
Faydalı model tescili (6769 SMK m.142; 10 yıl, buluş basamağı şartı yok) → ucuz IP hendeği.
Takvim gerçekliği: Eylül–Aralık (bütçe) ve Şubat–Mayıs satış pencereleri; Ağustos ve Ramazan ölü sezon.
Üstat notu · içerikte '1 kaynak, 8 parça' disiplini
5 kişilik ekip haftada 8 içerik üretemez — ama ayda 1 derin kaynak üretip onu 8 parçaya bölebilir. Örnek: bir vaka
çalışması → (1) uzun LinkedIn yazısı, (2) 40 sn ekran kaydı, (3) 3 kısa alıntı görseli, (4) webinar bölümü, (5) e-posta dizisi,
(6) partner sunumuna slayt, (7) satış itiraz cevabı, (8) sektör raporuna bölüm. Üretim maliyeti sabit, görünürlük 8 katı.
Ölçüt: içerikten gelen randevu sayısı. Beğeni sayısı bir metrik değildir; B2B'de 200 doğru kişinin okuduğu bir yazı, 20.000
yanlış kişininkinden değerlidir.
cephanelik
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası112 / 126

TİCARİ STRATEJİ · 8 · Maliyet Modeli
Bu bölüm dosyanın teknik yarısıyla doğrudan bağlıdır: Router (2.11), çift cache (8.2) ve terfi motoru (8.14–8.16) birer
maliyet aracıdır. Her LLM'siz cevaplanan soru, doğrudan brüt marja yazılır. Aşağıdaki rakamlar Temmuz 2026 liste fiyatlarıdır;
sağlayıcılar sık değiştirir — sözleşmeye model adı değil model sınıfı yazın.
Girdi maliyeti: model sınıfları (1M token, giriş/çıkış)
SınıfÖrnek modellerFiyat (in/out)Dima'da rolü
EkonomikDeepSeek V4 Flash $0.14/$0.28 · Gemini 2.5
## Flash $0.30/$2.50
## ~$0.1–0.3 / $0.3–
## 2.5
Sınıflandırma, beautifier,
Başlangıç paketi
DengeGemini 3.1 Pro $2/$12 · Claude Sonnet 5
## $2/$10* · GPT-5.4 $2.50/$15
~$2–3 / $10–15Varsayılan sohbet + agentic
analiz
PremiumClaude Opus 4.8 $5/$25 · GPT-5.5 $5/$30$5 / $25–30Kurumsal pakette seçmeli; kritik
karar analizi
## Yerel (on-
prem)
Açık ağırlıklı modeller; GPU $0.5–5/saattoken başı ≈ $0 +
sabit GPU
Regüle / air-gap müşteri (v3+,
## Faz 7.4)
- Tanıtım fiyatı; süre sonunda $3/$15'e döner — sözleşmede sınıf bazlı fiyatlama bu yüzden şart.Çarpanlar: prompt
cache tekrarlayan sistem+şema bağlamında giriş maliyetini 0.1×'e kadar düşürür; batch API %50 indirim sağlar
(zamanlanmış raporlar buraya yönlendirilir — görev 8.9). Embedding maliyeti ihmal düzeyinde ($1–5/ay/müşteri).
İşlem başına LLM maliyeti ($)
İşlemToken profili (giriş+çıkış)EkonomikDengePremium
Sohbet sorgusu~4K + 0.6K0.0030.020.035
Agentic analiz (3–5 tur)~30K + 3K0.0170.120.23
Rapor üretimi~10K + 3K0.0110.070.13
Artifact / pano üretimi~12K + 8K0.0240.150.26
Altın yol / DCM / cache isabeti—000
Yapısal maliyet avantajı — hendeğin sayısal hali
Intent Router + MetricStore/cube + çift cache sayesinde işlemlerin büyük payı LLM'siz biter. Sistem kullanıldıkça (altın
metrik ve cache isabeti arttıkça) müşteri başına maliyet DÜŞER. Rakiplerin çoğunda her soru bir LLM çağrısıdır; bu tablo
bizim marj hendeğimizdir ve aynı zamanda satış argümanıdır (Dima Verimlilik Raporu, görev 8.17).
Kaldıraç: altın yol oranını her %10 artırmak, tüm müşteri tabanında COGS'u yaklaşık %15–20 düşürür. Bu yüzden terfi
motoru (8.14–8.16) bir 'nice-to-have' değil, doğrudan finansal üründür.
Müşteri başına aylık maliyet senaryoları
Yönlendirme karması varsayımı: %55 altın/DCM/cache (0 maliyet) · %25 sohbet · %12 agentic · %5 rapor · %3 artifact.
Kullanımİşlem/ayEkonomikDengePremium
Hafif (KOBİ)1.500~$6~$41~$75
## Orta5.000~$20~$137~$249
## Yoğun20.000~$81~$548~$1.000
Altyapı (LLM hariç): paylaşımlı SaaS tenant $10–30/ay · ayrılmış (dedicated) $150–400/ay · on-prem = müşteri
donanımı (yerel LLM için başlangıçta tek bir kurumsal GPU yeterli). Duyarlılık: agentic payı %12'den %24'e çıkarsa
Denge sınıfında orta müşteri ~$137 → ~$210. Aşağıdaki kredi ağırlıkları bu riski otomatik fiyatlar.
mimarinin fatura karşılığı
DİMA · 0→100 Görev Takip Dosyası113 / 126

TİCARİ STRATEJİ · 9 · Fiyatlandırma, Paketler ve Pazarlık
Çıpalama betiği (sırayla söylenir)
SıraSöylenecek
1“Bu raporu kim hazırlıyor, ayda kaç saat gidiyor?”
2“Bir raporlama uzmanının şirkete aylık maliyeti nedir sizce?”
3“Dima'nın yıllık bedeli, o kişinin yaklaşık iki aylık maliyeti.”
Fiyatı asla ilk telefonda söyleme; önce acıyı ve çıpayı kur. Fiyat, çıpasız söylendiği anda pahalıdır.
Kredi sistemi — işlem bazlı, müşterinin anlayacağı dil
Rakipler token bazlı sayaç kullanır (şeffaf ama müşteri anlamaz). Dima işlem   sayar:
İşlemKrediNot
Altın yol metrik · DCM · cache isabeti · AI'sız API çağrısı0Sistem öğrendikçe faturanız büyümez
Sohbet sorgusu1
Rapor üretimi4
Agentic analiz6Bütçe tavanı görev 4.16 ile korunur
Artifact / pano üretimi8
Başarısız işlem0Asla ücretlendirilmez — güven veren kural (görev 8.6)
Model sınıfı çarpanı: Ekonomik ×1 · Denge ×2 · Premium ×3 (premium yalnız Kurumsal+). Devir: aylık planda
kullanılmayanın %50'si bir sonraki aya devreder; yıllıkta havuz yıllıktır. Ek kredi: $0,15/kredi (1.000'lik blok $120). COGS
eşlemesi: 1 kredi ≈ Denge sohbeti ≈ $0,02 maliyet → $0,15 satış ≈ %85 brüt marj; agentic 6 kredi = $0,90 satış vs
$0,12 maliyet — marj korunur.
Aylık paketler
USD-endeksli; TL faturada çeyreklik kur sabitleme; KDV hariç; yıllık ödemede 2 ay bedava.
BaşlangıçProfesyonelKurumsal BulutOn-Prem / Regüle
## Aylık$190$450$990$1.900+ (yıllık
sözleşme)
## Ürün
sürümü
v1v1–v2v2–v3v3+ (DCM, air-gap)
## Veri
kaynağı
13SınırsızSınırsız
Kullanıcı52050Eşzamanlı oturum: 5
dahil, ek $250/ay
Aylık kredi6002.5006.0008.000 veya BYO-key
## Model
sınıfı
EkonomikDengeDenge + PremiumYerel LLM / BYO-key
## Öne
çıkanlar
## Chat+grafik,
rapor, 2 pano
+ Skills, hafıza, zamanlanmış
rapor/WhatsApp, sınırsız pano
+ RLS/RBAC/SSO, audit, 1
sektör paketi, Karar Motoru
+ DCM/air-gap, KVKK
dosyası, SLA, eskalasyon
## Tahmini
## COGS
$15–25$90–150$250–420Altyapı müşteride
Brüt marj~%88~%72–80~%60–75~%85+
danışmanlık rafında oyna
DİMA · 0→100 Görev Takip Dosyası114 / 126

BYO-API-Key (Kurumsal+)
Müşteri kendi model anahtarını bağlar → kredi limiti kalkar, biz platform ücreti alırız. Maliyet riski müşteriye geçer, marjımız
sabitlenir. Regüle müşteride yerel LLM aynı işi görür (görev 0.6 model soyutlaması bunu mümkün kılar).
Kurulum ücretleri (tek seferlik) — hem gelir hem hendek
PaketÜcretKapsamBizim maliyetMarj
Standart$1.5001 kaynak, ≤25 tablo modelleme, 10 altın metrik, 2
pano, 2 saat eğitim
~2–3 mühendis-
günü (~$600)
## ~%60
Profesyonel$4.5003 kaynak, sektör paketi uyarlama, 30 metrik+kural,
Excel tarihçe yükleme, 1 gün eğitim
~6–8 gün
## (~$1.600)
## ~%64
Kurumsal$12.000+On-prem kurulum, SSO/RLS/politika, güvenlik
incelemesi desteği, özel metrik kütüphanesi, ekip
eğitimleri
~15–20 gün~%60
Sektör paketi
(UpcySustain)
## $3.000 +
## $150/ay
OEE + karbon/su/enerji + DPP + CBAM/CSRD
şablonları (görev 8.5)
Bir kez üret, çok
sat
## Artan
Pazarlık kuralları
Kurulumdan indirim yok, aylıktan ver. Kurulum = anlamlandırma emeği = geçiş maliyeti = hendek. Bedavaya
inerse emeğin değeri sıfırlanır.
İndirim karşılıksız verilmez: peşin ödeme, 2 yıllık sözleşme, kamuya referans, vaka çalışması, 2 sıcak tanıştırma.
İndirimi para değil dağıtım karşılığı ver.
Pilot ücretlidir ve başarı kriteri sözleşmede yazılıdır (ör. 'haftalık raporu 3 saatten 15 dakikaya indirmek'). Kriter
tutarsa kapanış otomatik olur.
İlk 2 deniz feneri istisnası: kurulum %50 indirimli olabilir — karşılığında referans + vaka çalışması sözleşmeye
yazılır.
Vade gerçeği: 60–90 gün istenir; peşin indirimiyle yönet, nakit planını buna göre kur.
Kur riski: USD endeksli fiyat veya çeyreklik TL sabitleme.
Pazar kıyası — konum doğrulama
RakipFiyatDima'nın konumu
Wren Cloud$179 / $559 ayProfesyonel $450 arada; farkımız kurulum hizmeti + Türkçe + KVKK + 0-
kredili altın yol
Wren self-
hosted
Eşzamanlı oturum, min 5–
## 10
On-Prem'de aynı metriği benimsedik (kanıtlanmış model)
oneAgent (DE)€25/kullanıcıProfesyonel 20 kullanıcıda ≈ $22,5/kullanıcı — parite, ama sektör paketiyle
üstün
Power BI
## Copilot
~€5.000/ayKurumsal $990: 'kurumsal değerin beşte biri fiyatı' anlatısı
Querio / Sequel~$14k/yıl · $99/ayBaşlangıç $190 KOBİ'yi yakalar, alt segmentten ciddi ayrışır
Örnek müşteri ekonomisi (tekstil, Profesyonel + UpcySustain)
KalemYıl 1Yıl 2+
Kurulum (Profesyonel)$4.500—
Sektör paketi kurulumu$3.000—
## Abonelik (12 × $450)$5.400$5.400
Sektör paketi aylık (12 × $150)$1.800$1.800
Toplam gelir$14.700$7.200
LLM + altyapı~$1.800~$1.500 (altın yol arttıkça düşer)
Kurulum işçiliği~$1.600—
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası115 / 126

KalemYıl 1Yıl 2+
Destek payı~$600~$600
Brüt marj~%73~%80+
Ölçek okuması: 10 böyle müşteri ≈ $147k Yıl-1 geliri — 5 kişilik ekip için ayakta kalma eşiği. 30 müşteri sürdürülebilir
büyüme. Yıl-2'de kurulum geliri düşer ama marj yükselir; büyüme yeni müşteri + paket genişlemesinden gelir (v4
Bilgi Hub'ı ve v5 toplantı ajanı birer yukarı-satış kalemidir).
Uygulama kuralları ve riskler
Sözleşmeye model sınıfı    yazın (tanıtım fiyatları biter).
Her müşteride gerçek token tüketimini ölçüp bu tablodaki varsayımları 60 günde bir revize edin (görev 8.6).
Zamanlanmış raporları batch API'ye yönlendirin (−%50, görev 8.9).
Premium modeli yalnız kanıtlanmış ihtiyaçta açın.
Fair-use maddesi: altın yol 0 kredili olduğu için API bombardımanına karşı istek/dk limiti (görev 8.12).
Agentic'i sınırlı kredi hediyesiyle açın (100–500) — kontrollü benimseme.
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası116 / 126

TİCARİ STRATEJİ · 10 · Hendekler ve Rekabet Savaşı
Hendek inşa sırası — hangi hendek ne zaman oluşur
SıraHendek
Ne zaman devreye
girer
Üründeki kaynağıGücü
1Anlamlandırma emeğiKurulumdan itibarenFaz 1 sihirbaz + MDLOrta — taklit edilebilir ama zahmetli
2Kurumsal hafıza2–6 ayFaz 5 + Faz 10 (Bilgi
## Hub)
Yüksek — taşınamaz kurumsal beyin
3İtiraf kilidi (denetim
tarihçesi)
6+ ayFaz 7.1 contract arşiviÇok yüksek — ayrılmak savunmasız
kalmaktır
4Benchmark ağ etkisi20–50 müşteriden
sonra
## Görev 12.7 (k-anonim
hive)
En yüksek — rakip asla toplayamaz
Rakibi kendi gücünden vur
Bulut/LLM oyuncularının 'her şey bulutta, her şey LLM' gücü aynı zamanda açığıdır: model kara-kutu, veri sınır ötesi, cevap
kanıtsız. 'Model provenance' ve 'veri ikameti' testlerini sektör standardı talebine çevir; rakip mimarisi gereği bu
testleri geçemez. Tetiği sen değil, düzenleyici ve müşterinin kendi denetçisi çeker.
Acil durum planları
SenaryoErken sinyalKarşı hamle
Hyperscaler TR/EU
bölgesi açar
Duyuru, partner
brifingleri
Mesajı egemenlikten kanıt + kurumsal hafıza + dikey pakete
kaydır; benchmark'ı öne çıkar (v4–v6 hızlandırılır)
Büyük rakip fiyat kırarTekliflerde agresif
iskonto
Fiyat savaşına girme; danışmanlık rafına ve sonuç-bazlı modele kaç
Rakip aynı
konumlamayı kopyalar
Aynı kelimeler, aynı
kampanya
Kanıtla ayrış: yayınlanmış vaka, sertifika, denetim tarihçesi,
benchmark verisi — kopyalanamayan varlıklar
Kilit müşteri kaybıKullanım düşüşü,
şampiyon ayrılması
Her hesapta 2 kullanıcı yedekle; kayıp analizini 48 saatte yap ve
oyun kitabına işle
Kurucu bağımlılığıHer satış kurucuya bağlıOyun kitabını yazıya dök; 10. müşteriden sonra ilk satışçıyı işe al
Doğrulama borcu
kapanmıyor
6 ay geçti, ödeyen
referans yok
İnşayı durdur; tek dikeye ve tek acıya odaklan (truva atı özelliği)
Üstat notu · hendek testi — bir avantajın gerçek hendek olup olmadığı nasıl anlaşılır?
Üç soruyu geçemeyen şey hendek değil, sadece özelliktir:
1 · Kopyalanabilir mi? İyi finanse edilmiş bir rakip 6 ayda yapabiliyorsa hendek değildir (arayüz, grafik çeşitliliği, hız).
2 · Zamanla derinleşiyor mu? Kullanıldıkça güçlenmiyorsa sabit bir avantajdır, aşınır (kurumsal hafıza ve denetim
tarihçesi derinleşir; egemenlik derinleşmez — regülasyon değişirse zayıflar).
3 · Müşteri ayrılırken kaybediyor mu? Kaybettiği şey yalnız 'alışkanlık' ise zayıf; 'savunulabilir geçmiş' veya 'sektör
kıyas verisi' ise güçlüdür.
Sonuç: Bizim en güçlü hendeğimiz teknoloji değil, zamanla biriken kanıt arşividir. Bu yüzden ilk müşterinin ilk
gününden itibaren contract yazmak stratejik bir karardır (görev 7.1).
neden kimse geçemez
DİMA · 0→100 Görev Takip Dosyası117 / 126

TİCARİ STRATEJİ · 11 · Kademeli Fetih ve Tekelleşme
FazHedef
## Ürün
sürümü
Geçiş kapısı (numerik)
Bu fazda HAYIR
denecekler
F1 · KöprübaşıTek dikey + tek bölge;
truva atı özelliği
v15–8 ödeyen müşteri + 1
yayınlanmış vaka
Başka sektör, özel proje,
büyük kurumsal ihale
F2 · BitişikAynı acı, yeni dikeyler +
kanal aktivasyonu
v215–20 müşteri + kanal-
kaynaklı boru hattı
Kanal dışı dağınık talep,
yurtdışı
## F3 · Yatay +
## Kurumsal
ERP yayılımı + regüle
segment (tepeden)
v3Kurumsal sözleşmeler +
SOC2/ISO yolu
Küçük KOBİ uzun kuyruğu
## F4 · Altyapı /
tekel
Egemen karar katmanı
olarak API/standart
v4–v6Ekosistem bağımlılığı,
rozet yaygınlığı
## —
Otorite merdiveni — kaçınılmazlık nasıl otoriteye dönüşür
Kanıt: yayınlanmış vaka çalışmaları (rakamla).
Kaynak: yıllık sektör raporu — atıf alınan taraf ol.
Sahne: dernek/oda konuşmaları; stant değil sahne.
Standart: 'Dima Verified' rozeti ve kontrol listesi — başkalarının uyduğu ölçüt.
Ekosistem: kanal ve API bağımlılığı — rakip senin sahanda oynar.
Tekelleşme doktrini
B2B'de tekel pazar payı değil; kategori tanımını + sertifika standardını + kanalı + kaçış maliyetini aynı anda
sahiplenmektir. Kral en çok satan değil kaçınılmaz olandır. Otorite bir başlangıç değil, kaçınılmazlığın sonucudur.
adım adım kral olma
## 1.
## 2.
## 3.
## 4.
## 5.
DİMA · 0→100 Görev Takip Dosyası118 / 126

TİCARİ STRATEJİ · 12 · Metrikler ve Erken Uyarı
MetrikHedef/eşikNe söylerKaynak görev
Aktivasyonİlk gerçek soru < 48
saat
Kurulum sürtünmesi kabul edilebilir miFaz 1
Haftalık aktif kullanıcı/hesapEn az 3 kişiTek kişiye bağımlılık = churn riski—
Patron kullanımıAyda 4+ oturumÖdeme kararı verenin bağlılığı5.5 brifing
Altın yol oranı%50+ ve artanCOGS ve güven; düşüyorsa mimari
kayıyor
## 2.11 · 2.18 ·
## 8.17
Demo → pilot dönüşümü%40+Düşükse mesaj/ICP sorunu—
Pilot → ödeme%60+Düşükse başarı kriteri yanlış kurulmuş—
Cevap doğruluğu (golden
set)
%95+Ürün güveni; düşüş = acil müdahale8.7
Referans üretimiHer 3 müşteriden 1 vakaBüyüme motorunun yakıtı—
Kanal payıTek kanal < %40Bağımlılık riski—
Brüt marjYıl-2'de %80+Terfi motoru çalışıyor mu8.6 · 8.16
Erken uyarı: bu üç sinyalden biri kırmızıysa haftalık gündeme girer
Bir hesapta 2 hafta üst üste kullanım düşüşü → churn öncüsü; kurucu arar.
Şampiyon işten ayrıldı → hesap sahipsiz; 72 saat içinde yeni şampiyon atanır.
Golden-set doğruluğu düştü → sürüm/model/MDL değişimi araştırılır, gerekirse geri alınır.
neyi ölçeriz
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası119 / 126

TİCARİ STRATEJİ · 13 · Riskler ve Kırmızı Çizgiler
Tek yasak hamle
Güven ürününde sahte demo, şişirilmiş sayı, abartılı otonomi vaadi acımasız değil intihardır — ilk ifşa tüm kaleyi düşürür.
FUD'a, kategori savaşına, kanal ele geçirmeye, kilitlemeye sonuna kadar agresif ol; yalana asla. Bu kategoride kralı
dürüstlük taçlandırır — etik tercih değil, stratejinin kendisi.
RiskÖnlemİlgili görev
Hukuki (kara liste, ceza-bazlı fiyat,
sigorta kanalı)
Uygulamadan önce hukuk görüşü; iddiaları yalnız kamuya açık ve
mimari gerçeklere dayandır
## —
Demo dürüstlüğüTahmin/what-if canlı LLM'e serbest bırakılmaz; referans parametreli
deterministik gösterilir
## 6.3 · 6.4
Aşırı genişlemeFaz geçiş kapıları numerik; kapı açılmadan yeni segment yokbölüm 11
Kurulum sürtünmesiSihirbaz + asistanlı onboarding kritik yolda; aktivasyon metriği
haftalık izlenir
## 1.3 · 1.10
Veri sızıntısı / güvenlik olayıİki-düzlem mimarisi + maskeleme + denetim; olay planı ve 72 saat
bildirim prosedürü hazır
## 2.12 · 7.5 ·
## 7.7
Kanıt kirlenmesi (v4 riski)Kanıt sınıfı ayrımı ön şart; otomatik test10.1 · 10.2
Yetenek/kurucu darboğazıOyun kitabı yazılı; 10. müşteriden sonra ilk satış işe alımı—
Maliyet patlamasıBütçe tavanı + model sınıfı yönlendirme + batch4.16 · 2.11 ·
## 8.9
neyi asla yapmayız
DİMA · 0→100 Görev Takip Dosyası120 / 126

TİCARİ STRATEJİ · 14 · Stratejik Büyüme Motorları
Büyüme tek bir muslukla olmaz. Aşağıdaki beş motor sırayla devreye alınır; her biri bir öncekinin ürettiği varlığı yakıt olarak
kullanır. Sıra bozulursa motorlar birbirini beslemez.
#  MotorYakıtıNasıl çalışır
Ne zaman devreye
alınır
## 1  Referans
motoru
Memnun müşteriHer 3 müşteriden 1 vaka; her vaka 2 sıcak
tanıştırma sözleşmede
İlk müşteriden
itibaren
2  Hesap içi
genişleme
Tek departmandaki
başarı
Şampiyonun panosu yönetim toplantısında
paylaşılır → diğer birimler ister
- aydan sonra
3  Kanal motoruReferans + partner kitiMali müşavir/ERP bayisi kendi portföyüne satar5 referans sonrası
4  Dikey paket
motoru
Aynı sektörde 3+
müşteri
Sektör paketi ürünleşir; 4. müşteride kurulum
yarıya iner
Bir dikeyde 3
müşteri
5  Veri ağı motoru20+ müşterinin anonim
verisi
Benchmark yeteneği tek başına satın alma
sebebi olur
20+ müşteri
Büyümenin sırrı: NRR (mevcut müşteriden büyüme)
Yeni müşteri kazanmak, mevcut müşteriyi büyütmekten 5–7 kat pahalıdır. Dima'nın yapısı buna çok uygun: aynı hesap
içinde     kullanıcı sayısı (departman yayılımı), veri kaynağı sayısı,  sektör paketi ve   sürüm yükseltme (v1→v3→v4)
olmak üzere dört ayrı yukarı-satış ekseni var.
Hedef: Net Gelir Tutundurma (NRR) %120+. Yani 100 birim gelirle başlayan müşteri, ertesi yıl churn'e rağmen 120 birim
üretmeli. Bu sağlanırsa yeni müşteri gelmese bile şirket büyür — 5 kişilik ekip için hayati kaldıraç budur.
Yukarı-satış tetikleyicileri — ne zaman hangi teklif
SinyalTeklifÜrün karşılığı
Aynı hesapta 3+ aktif kullanıcı, sık pano paylaşımıKullanıcı paketi genişletme—
İkinci bir veri kaynağı sorusu gelmeye başladıVeri kaynağı ekleme + Profesyonel'e geçişFaz 9.3 konnektörler
Denetim/sertifikasyon dönemi yaklaşıyorKurumsal pakete geçiş (audit, RLS, contract)Faz 7
Aynı sorular tekrarlanıyor, ekip büyüdüSektör paketi + SkillsFaz 8.5
Kararlar toplantıda tartışılıyor ama kayıt yokKarar Motoru modülü (v3)Faz 6B
Prosedür/oryantasyon şikayeti varBilgi Hub'ı (v4)Faz 10
Büyümeyi durduran üç sessiz katil
Tek kullanıcılı hesaplar: Şampiyon ayrılınca hesap ölür. Kural: 90 gün içinde her hesapta en az 3 aktif kullanıcı
(metrik olarak izlenir).
Kurulum kuyruğu: Satış hızlanır, kurulum yetişmez, kalite düşer. Kural: aynı anda 3'ten fazla aktif kurulum yapma;
kuyruk oluşursa sektör paketiyle kurulumu kısalt (Faz 8.5) veya partneri devreye al.
Özel istek batağı: Her müşteriye özel geliştirme, ürünü ajans işine çevirir. Kural: özel istek ancak ikinci bir
müşteri de isterse yol haritasına girer; tek müşterilik iş ücretli danışmanlık olarak fiyatlanır.
Coğrafi genişleme sırası ve ön koşulları
AşamaPazarÖn koşulNeden bu sıra
1Tek şehir/OSB + tek
dikey
—Yoğunluk ve referans matematiği
2Türkiye geneli aynı
dikey
5 referans + sektör paketiPaket tekrar satılır, kurulum ucuzlar
3Bitişik dikeylerKanal aktif + 15 müşteriAynı acı, farklı sektör
tek müşteriden ölçeğe
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası121 / 126

AşamaPazarÖn koşulNeden bu sıra
4Körfez / MENAv3 tamam + İngilizce/Arapça + yerel
ortak
Benzer veri yerelleştirme rejimi, düşük
hyperscaler kilidi
5Daha genişKategori sahipliği + sermayeAncak kanıtlanmış model ihraç edilir
Kural: yeni coğrafya, yeni ürün ve yeni segment aynı çeyrekte açılmaz. Aynı anda en fazla bir eksende genişle.
DİMA · 0→100 Görev Takip Dosyası122 / 126

TİCARİ STRATEJİ · 15 · Stratejik İş Birlikleri ve Ekosistem
5 kişilik bir ekip için iş birliği bir 'kanal taktiği' değil, varlık kiralama stratejisidir:
başkasının güvenini, erişimini, altyapısını ve meşruiyetini ödünç alırsın. Aşağıda dört farklı ortaklık türü ve her birinin kuralları
var — hepsi aynı şekilde yönetilemez.
Dört ortaklık türü
TürOrtakBiz ne alırızOnlar ne alırKritik risk
DağıtımMali müşavir, KVKK
danışmanı, ERP bayisi
Erişim + hazır güvenYeni gelir kalemi,
müşteri bağlılığı
Kanal çatışması, marka
kontrolü kaybı
MeşruiyetSektör derneği, oda,
üniversite
Sahne, atıf, kurumsal
itibar
İçerik, üyeye değer,
veri raporu
İçeriğin reklama
dönüşüp güven kaybı
TeknolojiYerel bulut, GPU sağlayıcı,
ERP satıcısı
Altyapı + entegrasyon
+ eş-satış
AI katmanı,
farklılaşma
Bağımlılık; tek
sağlayıcıya kilitlenme
## Sermaye/
stratejik
Kurumsal yatırımcı,
holding, entegratör
Sermaye + ilk
müşteriler + itibar
Erken erişim, iç
verimlilik
Yön kaybı; tek müşterinin
ürünü olma
Üstat notu · ortaklıkta tek altın kural: asimetrik değer
Bir ortaklık ancak onların size verdiği şey sizin onlara verdiğinizden pahalıysa anlamlıdır — ve tersi de doğru olmalı:
onlar için de öyle görünmeli. Bunu sağlamanın yolu farklı para birimlerinde takas etmektir: biz ürün ve gelir payı
veririz, onlar erişim ve güven verir. İkisi de kendi tarafında ucuz, karşı tarafta pahalıdır.
Kötü ortaklık işareti: Her iki taraf da aynı şeyi (satış) getirmeye çalışıyorsa, o bir ortaklık değil rekabettir.
Ortaklık kurma sırası ve ilk 12 ay
DönemHedef ortaklıkSomut adımBaşarı ölçütü
Ay 1–32 mali müşavir + 1 KVKK
danışmanı
Ortak webinar + gelir payı sözleşmesi + partner
kiti
İlk kanal-kaynaklı 3 randevu
Ay 3–61 sektör derneğiÜcretsiz sektör raporu + sahne konuşmasıDernek etkinliğinde stant değil
sahne
Ay 6–91 ERP bayisi (bölgesel)Teknik ekip eğitimi + demo ortamı + 2 ortak
müşteri ziyareti
Bayi kendi başına 1 satış
kapatır
Ay 9–121 yerel bulut/altyapı sağlayıcıOn-prem/egemen kurulum referans mimarisiOrtak 'egemen AI' teklifi
Ortaklık yönetim kuralları (yazılı olmazsa ortaklık çürür)
Kayıt (deal registration): Fırsatı ilk kaydeden partnerindir. Çakışma kuralı yazılı olmalı; sözlü mutabakat 3. ayda
patlar.
Aktivasyon yükümlülüğü: Partner 90 gün içinde en az 1 fırsat getirmezse kademesi düşer. Pasif partner listesi,
hayali dağıtımdır.
Marka koruması: Partner sunumlarında bizim onayladığımız materyaller kullanılır; abartılı vaat ortaklığı bitirir (tek
yasak hamle bizim için de geçerli).
Müşteri sahipliği: Sözleşme kimin adına? Net yaz. Belirsizlik yenilemede kavgaya döner.
Tek partner %40 kuralı: Hiçbir ortak cironun %40'ını geçmemeli; geçerse şartları o belirlemeye başlar.
Çıkış maddesi: Ortaklık biterse müşteri kimde kalır, veri ne olur — baştan yazılmalı.
Değerlendirme çerçevesi: bir ortaklık teklifine evet demeden önce
SoruEvet iseHayır ise
Bize    erişim mi getiriyor yoksa sadece iş
mi?
DevamÜcretli iş olarak fiyatla, ortaklık
deme
Ürün yol haritamızı saptırıyor mu?Reddet veya kapsamı daraltDevam
kendi gücünü çarpanla büyüt
## •
## •
## •
## •
## •
## •
DİMA · 0→100 Görev Takip Dosyası123 / 126

SoruEvet iseHayır ise
Münhasırlık (exclusivity) istiyor mu?Süre + bölge + hacim taahhüdü olmadan
asla
## Devam
Bizi tek müşteriye/ortağa bağımlı yapar
mı?
%40 kuralını uygulaDevam
Kaynağımızın ne kadarını yiyor?Ay başına 5 gün üstündeyse erteleDevam
Özel fırsat · 'egemen AI' ittifakı
Yerel bulut sağlayıcıları, GPU sunucu satıcıları ve KVKK danışmanlıkları şu anda aynı hikâyeyi satmaya çalışıyor ama
ellerinde son kullanıcıya gösterilecek bir uygulama yok. Dima o uygulamadır. Ortak teklif kurgusu: 'Veriniz
Türkiye'de kalır — altyapı onlardan, akıl bizden.'
Bu ittifak üç şey sağlar: (1) kurumsal ihalelerde birlikte girme meşruiyeti, (2) on-prem satışta donanım sorununun
çözülmesi, (3) bizim tek başımıza kuramayacağımız 'kurumsal ölçek' algısı. Karşılığında onlar farklılaşma kazanır. Asimetrik
değer testinden geçen en temiz ortaklıktır.
DİMA · 0→100 Görev Takip Dosyası124 / 126

TİCARİ STRATEJİ · 16 · İlk 90 Gün: Haftalık İnfaz Planı
Sol sütun ticari hamle, sağ sütun aynı hafta yürüyen teknik iş. İkisi paralel
gitmezse ya satacak ürün olmaz ya ürünü alacak müşteri.
HaftaTicari hamleParalel teknik işÇıktı
1Dikey + bölge kararı; kimlik/kategori kelimelerini
kilitle
Faz 0 iskeletTek sayfalık konumlama
1–230 firmalık hedef listesi (İSO/OSB/dernek/ilan
taraması)
Faz 0 tamamlanırİsim + tetikleyici notu
2–3Truva atı özelliğini seç ve demo kalitesine getirFaz 1: Excel→DB +
sihirbaz
Kendi verisiyle 10 dk demo
3–4KVKK risk taraması aracı + landing + ilk 3 LinkedIn
yazısı
Faz 1 metrik katmanıLead motoru canlı
4–6İlk 15 temas (ilan avı + bedava içgörü kancası)Faz 2: grafik + yorum +
öneri
5 keşif görüşmesi
5–73–5 mali müşavir/KVKK danışmanıyla kanal
görüşmesi
Faz 2 kanıt kartı + dürüst
red
2 partner mutabakatı
6–92 design partner pilotu (ücretli, kriterli, referans
maddeli)
Faz 3: rapor + pano +
hafıza
2 canlı kurulum
8–10Halüsinasyon düellosu videosu + ilk webinar
## (partnerle)
Faz 3 tamamlanır (v1
hazır)
İlk organik boru hattı
10–12İlk vaka çalışması + dernek sahne başvurusu +
metrik incelemesi
Faz 4 başlar (agentic)1 yayınlanmış vaka; ölç-ve-dön
kararı
Kural: 12. haftada veri hangi kapının (kanca, kanal, dikey) gerçekten açıldığını gösterir; tüm kaynak kazanan kapıya
yığılır. Plan değil, yön sabittir.
teknik ve ticari paralel yürür
DİMA · 0→100 Görev Takip Dosyası125 / 126

TİCARİ STRATEJİ · 17 · Kilit Kararlar Özeti
KonuKarar
KimlikDenetlenebilir Şirket Beyni / Kurumsal Karar Merkezi
Marka özü“Kurumunuzun asla yalan söylemeyen beyni”
Gerçek rakipStatüko (Excel + IT kuyruğu + 'analist alalım')
ICP50–500 çalışan, ERP'li, çok şubeli/hatlı üretici-dağıtıcı
Şampiyon / imzaPatronun raporunu hazırlayan kişi / patron
Truva atıPatronun her hafta istediği o tek rapor
Giriş modeliAşağıdan-yukarı, product-led + asistanlı melez
İlk kanallarMali müşavir + KVKK danışmanı → dernek → ERP bayisi
Fiyat çıpasıAnalist maaşı + danışmanlık bütçesi; kurulumdan indirim yok
Kredi felsefesiAltın yol 0 kredi · başarısız işlem 0 kredi
Hendek sırasıAnlamlandırma → kurumsal hafıza → itiraf kilidi → benchmark
Yoğunluk taktiğiTek OSB/dernek baskını (erişim değil yoğunluk)
Faz kapılarıNumerik; kapı açılmadan yeni segment yok
İkinci perdeEgemen karar altyapısı (kürek satıcısı) — tekel
Kral yoluKaçınılmazlık → otorite (Slack modeli, Palantir değil)
Tek yasakYalan
Sen “kaçınılmaz olarak” başlarsın, “otorite olarak” büyürsün. Kral, tahttan inmeyi imkânsız
kılan zincirleri kurandır — pazarlamayla değil, terk-edilemezlikle.
tek sayfada tüm strateji
DİMA · 0→100 Görev Takip Dosyası126 / 126
