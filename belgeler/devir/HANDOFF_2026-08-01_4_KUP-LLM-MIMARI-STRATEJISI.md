> ⚠️ **TARİHSEL KAYIT — NORMATİF DEĞİLDİR.** Bu belge yazıldığı andaki durumu ve o turda alınan
> kararları anlatır. Mimari otorite `backend/MIMARI.md`'dir; çelişkide o kazanır.
> Özellikle: bu belgelerdeki JOIN/derleyici teşhisleri `MIMARI.md §3.2`'de **düzeltilmiştir**.

# Rapor: LLM ↔ Küp Mimarisi — Sorun, Durum, Çözüm Seçenekleri

*(1 Ağustos 2026 — Dima backend, `wren-bağımsız` dalı — HANDOFF belgesi #4, repo kökünde
`HANDOFF_2026-08-01_4_KUP-LLM-MIMARI-STRATEJISI.md` olarak yaşıyor)*

## 0. Bu belge nedir, kimin için

Bu belge, sistemi bu haliyle devralacak bir geliştiricinin — daha önce bu konudaki
tartışmaların İÇİNDE olmadan — okuyup anlayabileceği şekilde yazıldı. Amaç: Dima'nın
"LLM ne zaman ham SQL yazıyor, ne zaman yapısal bir sorgu dolduruyor" mimarisindeki
GERÇEK, canlı bir sorunu; bunun kök nedenini; kod tabanında zaten var olan ilgili
altyapıyı; ve olası çözüm yollarını belgeler. Bir UYGULAMA PLANI değil — henüz hiçbir
çözüm seçilmedi, karar bekliyor. `backend/CLAUDE.md`'de anlatılan genel mimariye (rol,
katmanlar, ADR'ler) aşinalık varsayılıyor; burada yalnız BU konuya özel, CLAUDE.md'nin
kapsamadığı derinlikteki bulgular var.

**Önce okunması gereken temel kavramlar** (aşağıda tanımlı, sonra rapor boyunca serbestçe
kullanılıyor): *küp (cube)*, *base_object*, *zengin (enriched) view*, *Intent-JSON*,
*Discovery*, *kırılım (breakdown)*.

### Temel kavramlar (sözlük)

- **Küp (cube)**: Bir iş alanının (OEE, parti/üretim, İK...) NL sorgularına açılan
  yapısal tanımı — ölçüler (measures, `SUM`/`AVG` gibi agregasyonlar), boyutlar
  (dimensions, kırılım eksenleri), sinonimler. `backend/demo/packs/*/cubes/*/
  metadata.yml` dosyalarında yaşar, `WrenService`/`wren_core` tarafından SQL'e derlenir.
- **`base_object`**: Bir küpün BAĞLI OLDUĞU TEK model ya da view adı
  (`backend/demo/packs/modul/oee/cubes/oee/metadata.yml` → `base_object: oee_vardiya`).
  Küpün TÜM ölçü/boyutları bu TEK
  kaynağın kolonlarından türer — bu raporun kök-neden bölümünün (§3) merkezinde bu var.
- **Zengin (enriched) view**: Birden fazla tabloyu ELLE `JOIN`'leyip düzleştiren, küpün
  `base_object`'i olarak kullanılan bir SQL view (örnek: `parti_zengin` — partiler+
  personel+personel_ozluk'u birleştirir). Bugün çapraz-tablo verinin küpe girmesinin TEK
  yolu bu — otomatik değil, birinin elle yazması gerekiyor.
- **Intent-JSON (`source=cube+llm`)**: LLM'in ham SQL YAZMADIĞI, bunun yerine yapısal bir
  `CubeQuery` (hangi küp/ölçü/boyut/filtre) DOLDURDUĞU üçüncü bir yol — `route()`
  (sıfır-LLM deterministik eşleştirme) soruyu çözemezse devreye girer, sonucu AYNI
  deterministik motor derler. `source=cube` ile AYNI interaktiviteye (chip/kırılım/
  drill-down) sahiptir.
- **Discovery (`source=llm:<sağlayıcı>`)**: LLM'in HAM SQL yazıp doğrudan çalıştırdığı,
  hiçbir yapısal `cube_query` üretmeyen, son-çare yol. Sonuç tek-atımlık düz bir tablo —
  chip/kırılım/tarih-değiştirme/follow-up YOK, çünkü deterministik derleyici yalnız
  ÖNCEDEN TANIMLI küp yapılarından SQL üretebiliyor, ham SQL'den değil.
- **Kırılım (breakdown)**: Bir raporu farklı bir boyuta göre bölme ("makine bazında" →
  "operatör bazında" gibi). Yalnız `source=cube`/`cube+llm` cevaplarında chip'le
  yapılabilir; Discovery cevaplarında bugün MÜMKÜN DEĞİL.

---

## 1. Bu rapor neden var

Ürünün nihai hedefi: her soru kırılabilir, kök nedene inilebilir, tarih değiştirilebilir,
chip'lerle takip edilebilir bir rapora dönüşsün. Bu yalnız yapısal `cube_query` üreten
cevaplarda (source=`cube` / `cube+llm`) mümkün — LLM'in ham SQL yazdığı "Discovery"
cevapları (source=`llm:<sağlayıcı>`) tek-atımlık, düz tablo, hiçbir chip'le manipüle
edilemeyen sonuçlar. Kullanıcı canlı testte tekrar tekrar bunu gördü: "personel bazlı
verimlilikleri karşılaştır son 6 ay" gibi sorular saf LLM cevabına düşüyor — kırılım yok,
kök neden yok, tarih seçilmiyor, chip gelmiyor. Endişe açık: **eğer bu sık oluyorsa, üstüne
inşa edilecek hiçbir analiz katmanı (agentic kök-neden, otomatik kırılım/kıyaslama) sağlam
bir zemine oturmaz.**

Bu raporun amacı: sorunu kesin biçimde teşhis etmek (varsayımla değil, koda ve canlı
kanıta bakarak), sistemde ZATEN var olan ilgili altyapıyı envantere çıkarmak, ve
gerçekçi çözüm seçeneklerini artı/eksileriyle sunmak — karar kullanıcıya ait.

## 2. 1 Ağustos 2026'da ZATEN düzeltilen kısım (özet — ayrıntı: `UX-KRITIK-BULGULAR-YOLHARITASI_2026-08-01.md` §RAW-FOLLOWUP)

İki kontrol-akışı hatası ("tuzak") vardı ve düzeltildi:

- **raw_followup tuzağı**: bir thread'in ilk turu Discovery'ye düşünce, o thread bir daha
  ASLA `route()`/Intent-JSON'a dönemiyordu — konu tamamen değişse bile.
- **Yapısal zincir çıkmazı**: yapısal bir takipte deterministik+LLM zinciri tükenince,
  Discovery GERÇEKTEN cevaplayabilecekken bile doğrudan "anlayamadım" dönüyordu.

Bu ikisi düzeltilince: **"tek bir küpün zaten cevaplayabileceği" sorular artık gereksiz
yere LLM'e kaçmıyor.** Ama bu raporun konusu olan asıl problemi ÇÖZMEDİ — çünkü "personel
bazlı verimlilik" türü sorular tek bir küpün cevaplayabileceği bir şey DEĞİL, gerçekten
çapraz-alan (cross-domain) bir istek. O sınıf soru için hâlâ sıfır yapısal yol var.

## 3. Kök neden — mekanik olarak KESİN teşhis edildi

### 3.1 Derleyici tek-kaynaklı, ilişki grafiğini sorgu anında GEZMİYOR

Her küp (`backend/demo/packs/*/cubes/*/metadata.yml`) `base_object:` alanıyla **TEK BİR**
model/view'a bağlanır (örn. `backend/demo/packs/sektor/boyahane/cubes/parti/metadata.yml:2`
→ `base_object: parti_zengin`, `backend/demo/packs/modul/oee/cubes/oee/metadata.yml:2` →
`base_object: oee_vardiya`). Yapısal `CubeQuery → SQL` derlemesi `wren_core.cube_query_to_sql`
(native/Rust motor, `backend/app/wren_service.py:491,507`) tarafından yapılır; kendi
docstring'i "the cube definitions in the supplied manifest" der — yani **yalnız o TEK
küpün önceden tanımlı ölçü/boyut listesinden** SQL üretir. `backend/demo/wren-projects/
demo-boyahane/relationships.yml`'de TAM bir join grafiği var (30+ ilişki:
`partiler_personel`, `oee_vardiya_makineler`, `bordro_personel`, vb.) — ama bu grafik
**sorgu zamanında dinamik gezilmiyor**. Yalnız Wren'in KENDİ tek-sıçramalı `is_calculated`
alanları (örn. `personel.dogum_tarihi ← personel_ozluk.dogum_tarihi`,
`backend/demo/wren-projects/demo-boyahane/models/personel/metadata.yml:24-27`) için
kullanılıyor, o da güvenilir bulunmamış (bkz. 3.2).

### 3.2 Çapraz-tablo veri, YALNIZ elle yazılmış "zengin" (enriched) view'larla küpe giriyor

Kanıt: `backend/demo/wren-projects/demo-boyahane/views/parti_zengin/metadata.yml` — `partiler +
personel + personel_ozluk`'u elle `LEFT JOIN`'leyip düzleştiren bir SQL view. Yorumu net:
*"calc field'lar cube_query_to_sql'de JOIN'lenmiyor (düz base-SQL) → demografiyi VIEW'da
denormalize ederiz."* `parti` küpü bu view'a bağlı olduğu için `operatör/cinsiyet/
departman/eğitim` boyutları TAM interaktif (chip, kırılım, hepsi çalışıyor) — ama bu,
birinin GERÇEKTEN oturup bu spesifik join'i yazmasıyla oldu, otomatik değil.

### 3.3 OEE↔personel eksikliği bir HATA değil, BİLİNÇLİ bir tasarım kararıymış

`backend/demo/packs/modul/oee/cubes/oee/metadata.yml:6-8` yorumu kelimesi kelimesine:
*"Kişi/cinsiyet OEE'de DEĞİL (oee_vardiya kişi taşımaz — OEE makine metriğidir);
kişi-bazlı verimlilik `parti` cube'unda (operatör köprüsü). Böylece hiçbir yetenek kaybı
yok, doğru cube'a taşındı."* Yani: OEE, ISO 22400 anlamında saf bir MAKİNE metriği; kişi
bazlı üretkenlik kasıtlı olarak `parti`'ye taşınmış. `oee_vardiya`'nın kendisi kişi FK'sı
taşımıyor — kişiye ancak `oee_vardiya → partiler → personel` 2-sıçramalı bir köprüyle
ulaşılabilir (Gemini'nin yazdığı ham SQL TAM OLARAK bunu yaptı — `interaction_log`'dan
görüldü), ve bu köprü istatistiksel olarak BULANIK (bir vardiyada birden fazla parti/
operatör olabilir — kişiye "OEE payı" atfetmek varsayımsal olur). Bu muhtemelen NEDEN
hiç inşa edilmediğini açıklıyor: yanlış/yanıltıcı bir "OEE-kişi" metriği üretmektense hiç
üretilmemiş.

**Sonuç**: kullanıcının test sorusu ("personel bazlı verimlilikleri karşılaştır") aslında
İKİ farklı şeyden biri olabilir — (a) `parti`'nin ZATEN sahip olduğu kişi-bazlı üretkenlik
verisi (ilk-seferde-tamam-yüzdesi, işlenen ağırlık — ama "verimlilik" kelimesi bilinçli
olarak yalnız OEE'ye ayrılmış, bu yüzden bu ifadeyle asla `parti`'ye yönlenmiyor), ya da
(b) gerçekten "OEE'nin kişi bazında kırılımı" — ki bu, altta yatan veri modeliyle
GÜVENİLİR biçimde temsil edilemeyebilir. Bu ayrım **kullanıcının niyetine bağlı**, kod
okuyarak çözülemez.

## 4. Envanterde ZATEN olan, bu sorunu çözmeye yardımcı altyapı

### 4.1 5 katmanlı "önce dikey, sonra sektör, sonra şirket" compose sistemi ZATEN var

`backend/app/compose.py` (ADR-0005+0017): `backend/demo/packs/kaynak/<erp>/` (logo-3,
mikro-v16, netsis — fiziksel şema) → `backend/demo/packs/modul/<dikey>/` (bakim, enerji,
**ik**, kpi, **oee**, turev — sektörden BAĞIMSIZ fonksiyonel dikeyler) →
`backend/demo/packs/sektor/<sektor>/` (boyahane, geri-donusum, kumas-ticareti,
tarim-ticareti) → kesişim katmanı → `backend/demo/companies/<şirket>/` (en spesifik,
en son kazanır). Yani kullanıcının önerdiği "önce dikeyleri mükemmelce kapsama al, sonra
sektöre, sonra şirkete özelleş" mimarisi **zaten bu iskelette var** — yeni bir tasarım
gerekmiyor, iskeletin DOLDURULMASI gerekiyor.

**Somut boşluk**: `ik` (8 ölçü + 8 boyut, ERP'den bağımsız,
`backend/demo/packs/modul/ik/cubes/ik/metadata.yml` +
`backend/demo/packs/modul/ik/views/ik_zengin/metadata.yml`) ve `oee` gibi dikeyler olgun.
Ama **muhasebe/satış henüz jenerik bir dikey DEĞİL** — muhasebe verisi yalnız
`backend/demo/packs/kaynak/netsis/models/muhasebe_hareketleri` içinde (tek ERP'ye özel),
satış/ticaret verisi yalnız `backend/demo/packs/kaynak/logo-3/cubes/{ticaret,mal,cari}`
içinde (yine tek ERP'ye özel) — `ik`/`oee` gibi 3 ERP'ye ortak, normalleştirilmiş bir
modül yok.

### 4.2 "Ad-hoc veriden otomatik küp türetme" ZATEN çalışan bir örneği var

`backend/app/dataset.py` (Excel/CSV yükleme, ADR-0021): dosya → oturum-scoped DuckDB tablosu →
`DESCRIBE` ile şema → kolon rolleri otomatik sınıflanır (sayısal=ölçü→`SUM`, tarih=zaman,
diğeri=boyut, `_role()` satır 31-38) → **minimal bir MDL (model+küp) anında üretilir**
(`build_mdl()`, satır 124-151) → `build_service()` bu MDL'i yeni bir `WrenService`'e
bağlar → yüklenen veri **tüm route/chip/kırılım/yorum/KPI pipeline'ından "bedava" geçer**
(docstring'in kendi ifadesi, satır 4). Bu, "veriden cube türetme" fikrinin bu kod
tabanında YABANCI olmadığının doğrudan kanıtı — bir kez inşa edilmiş, çalışıyor, yalnız
tetikleyicisi "dosya yükleme," "Discovery'nin ürettiği sonuç" değil.

### 4.3 Cross-cube "blend" mekanizması var ama SINIRLI

`backend/app/cube_router.py`'de `cross_cube_add()` (satır 394-425) ve `cross_cube_dim_switch()`
(satır 428-452) — ikisi de GERÇEK bir SQL JOIN yapmıyor, iki küpü AYNI kırılım düzeyinde
(paylaşılan boyut adı üzerinden) yan yana getiriyor ya da TEK bir küpe geçiş yapıyor.
Hedef küpte mevcut TÜM ölçü/boyutlar birebir bulunmalı — "personel bazlı verimlilik" gibi
GERÇEKTEN join gerektiren (bir küpün ölçüsü + başka küpün, ancak bir köprü tablo üzerinden
ulaşılabilen boyutu) istekleri çözemez, çözmesi de tasarlanmamış.

## 5. Rakip araştırması

### 5.1 Birinci tur (tamamlandı) — "LLM ham SQL mi yazmalı, yapısal sorgu mu doldurmalı"

Cube.dev'in kendi AI API'si ham SQL ÜRETMİYOR — yapısal bir sorgu dolduruyor, semantic
katman çalıştırıyor (Dima'nın Intent-JSON'uyla AYNI felsefe — `ask.py`'nin kendi
docstring'i zaten bunu ilham kaynağı gösteriyor). LangChain'in `create_sql_agent`'ı
(ham-SQL-yazan agent) artık LangChain'in KENDİSİ tarafından "legacy, production için
önerilmiyor" deniyor. Vanna.ai aynı kampta. Zenlytic/Upsolve'un iç mimarisi doğrulanamadı
(yalnız pazarlama sayfası seviyesi bilgi). **Sonuç**: Dima'nın "LLM yapısal sorgu
doldursun" tercihi zaten sektörün olgun tarafında — bu KISIM mimari olarak sağlam.

### 5.2 İkinci tur (TAMAMLANDI) — "dikey şablon kütüphaneleri" + "ad-hoc sorgudan dinamik şema çıkarımı"

**Soru 1 — dikey şablon kütüphaneleri:**
- **Doğrulandı (resmi dokümantasyon)**: Looker, Looker Marketplace üzerinden dağıtılan
  hazır LookML parçaları ("Looker Blocks") sunuyor — bazıları yaygın 3. parti veri
  kaynaklarını (Google Analytics) modelliyor, bazıları AÇIKÇA genel bir ANALİTİK KALIBI
  ("Retail Analytics" örneği dokümante edilmiş). "Plug-and-play, LookML'i özelleştir"
  deniyor — yani jenerik şablon → müşteriye özel özelleştirme, Dima'nın YAML-katmanlama
  yöntemine EN yakın doğrulanmış emsal.
- **Doğrulandı, daha zayıf eşleşme**: dbt'nin Package Hub'ı pratikte KAYNAK-BAZLI
  paketlerle dolu (Fivetran'ın dbt_shopify, dbt_quickbooks, dbt_netsuite paketleri gibi)
  — bunlar TEK bir kaynak sistemden standart tablo üretiyor, Dima'nın `kaynak/` katmanına
  benziyor, `modul/` (ERP'DEN BAĞIMSIZ dikey) katmanına DEĞİL. "Muhasebe"yi rastgele
  ERP'ler arasında genellemiş bir dbt paketi BULUNAMADI.
- **Kontrol edildi, kanıt yok**: Cube.dev'in yeniden-kullanılabilir dikey küp kütüphanesi
  yok — yalnız "Recipes" (38 nasıl-yapılır rehberi, dağıtılabilir model değil) ve
  pazarlama sayfaları var. Zenlytic/dbt Semantic Layer için somut bir şey bulunamadı.
- **En iyi-pratik sinyali**: hiç kimse "önce jenerik, sonra sektöre/şirkete özelleş"i bir
  anti-pattern olarak işaretlemiyor — Looker Blocks ve dbt'nin kendi staging→marts
  katmanlaması da (dolaylı olarak) jenerikten başlamayı destekliyor. **Sonuç: A
  seçeneğinin yönü (önce jenerik dikey, sonra özelleş) rakip pratikleriyle ÇELİŞMİYOR,
  destekleniyor.**

**Soru 2 — ad-hoc sorgudan dinamik/interaktif model çıkarımı:**
- **Doğrulandı, EN yakın emsal**: Looker'ın SQL Runner'daki "Explore from Here" özelliği
  TAM OLARAK bunu yapıyor — ad-hoc bir SQL sonucunun kolonlarını "geçici bir model"e
  sarıyor, sayısal kolonları otomatik ölçü sayıyor, sonucu "modelde kayıtlı bir tabloymuş
  gibi" keşfedilebilir hale getiriyor. AMA: kural-tabanlı (yalnız kolon adı/tipi), zaman-
  granülaritesi ya da ilişki çıkarımı YOK, LLM yok, NL-öncesi bir dönemin özelliği.
- **Doğrulandı, TERS örnek**: Metabase'in "Explore results"ı TAM TERSİ ders veriyor —
  dokümantasyon açıkça "native SQL sonuç tiplerini OTOMATİK anlayamıyoruz" diyor, bir
  insan ELLE kolonları bir "Model"e etiketlemeden yeniden-keşif çalışmıyor. Terfi
  OPT-IN ve MANUEL, çıkarımsal değil.
- **Doğrulandı, OLUMSUZ bulgu**: WrenAI'de ham-SQL-yedeğinden-sonra-yapısala-terfi YOK —
  bir GitHub issue'su MDL dışı sorularda "İlgili SQL bulunamadı" ile SERT başarısızlık
  olduğunu doğruluyor (pazarlama metni "zarif yönlendirme" diyor ama bu issue kanıtıyla
  DOĞRULANMADI). Dima'nın bugünkü ham-SQL yedeği bile WrenAI'nin görünürdeki
  davranışının ÖTESİNDE — ama ikisi de o yedeği geri yapısala TERFİ ETTİRMİYOR.
- **Doğrulandı, OLUMSUZ bulgu**: Vanna.ai'nin "takip soruları" bağımsız, TAZE NL→SQL
  round-trip'leri (tıklanabilir öneriler) — sabit bir sonuç setinde yeniden-kırılım/
  toplama DEĞİL, "yeni bir soru öner"e daha yakın.
- **Yalnız pazarlama iddiası, kapsam da tam örtüşmüyor**: AtScale'in ML-tabanlı "One-Click
  Modeling"i şema+sorgu-günlüklerinden ilişki/hiyerarşi çıkardığını iddia ediyor —
  kendi blog'ları dışında doğrulanamadı, VE geçmiş şema/kullanımdan çıkarım yapıyor,
  TEK BİR ad-hoc sorgunun sonucundan değil — Soru 2'nin sorduğu şeyle tam örtüşmüyor.
- **SONUÇ (Soru 2)**: "LLM'in ürettiği ad-hoc sonucu yönetilebilir/kırılabilir bir modele
  terfi ettirme" pazarda **NADİR-İLA-YOK** görünüyor. Tek gerçek emsal (Looker) on yıllık,
  dar kapsamlı, kural-tabanlı bir analist aracı — konuşmasal son-kullanıcı kırılımı değil.
  **Bu, B seçeneğini "kanıtlanmış bir deseni kopyalamak" değil, "gerçek bir potansiyel
  farklılaştırıcı ama kanıtlanmamış bir bahis" yapıyor.**

- **ÖNEMLİ YAN-BULGU (doğrulandı, dokümantasyon üzerinden)**: **Cube.dev'in derleyicisi
  GERÇEKTEN dinamik join çözüyor** — bildirilen ilişkiler üzerinden ÇOK-SIÇRAMALI
  (transitive) join'leri SORGU ANINDA, ÖNCEDEN MATERYALİZE EDİLMİŞ bir düzleştirilmiş
  view GEREKMEDEN otomatik üretiyor (belirsiz çoklu-yol durumları için tek seferlik bir
  `join_path` bildirimi yeterli — düzleştirilmiş tablo değil). **Bu, Dima'nın bugünkü
  yalnız-materyalize-view mekanizmasından (§3.1-3.2) DAHA YETENEKLİ bir mimari — ve
  §6.C'nin "kanıtlanmamış, çok riskli" değerlendirmesini DEĞİŞTİRİYOR** (bkz. §6.C, revize
  edildi).

## 6. Çözüm seçenekleri

### A) Dikey modül genişletme — `backend/demo/packs/modul/muhasebe/`, `backend/demo/packs/modul/satis/`

`ik`/`oee` ile AYNI kalıp: jenerik cube + (gerekirse) "zengin" enrichment view + 3 ERP'ye
(logo-3/mikro-v16/netsis) eşleme. **Artı**: kanıtlanmış desen, düşük risk, her tamamlanan
dikey KALICI olarak o alandaki TÜM soruları tam interaktif hale getirir. **Eksi**: her
dikey gerçek mühendislik işi (ERP'ler arası kolon eşleme + doğrulama) — hızlı değil, ama
öngörülebilir. **Kapsam dışı bırakılmaz**: bu seçenek §3.3'teki "personel×OEE" gibi
BİLİNÇLİ olarak ayrılmış çapraz-alan sorunları ÇÖZMEZ — yalnız her dikeyin KENDİ İÇİNDEKİ
kapsamı genişletir.

### B) Discovery sonucunu geçici/oturum-scoped bir küpe "yükseltme" — KISMİ/GEÇİCİ çözüm

`dataset.py`'nin `_role()`/`build_mdl()` mantığını Discovery'nin ürettiği SQL'in SONUÇ
kolonlarına uygulamak: LLM ham SQL'i yazıp çalıştırdıktan SONRA, sonuç setinin kolonları
otomatik sınıflanır (ölçü/boyut/zaman), oturum-scoped bir MDL/küp kaydedilir, cevaba bu
küpe bağlı bir `cube_query` iliştirilir. **Artı**: mevcut altyapının büyük kısmını yeniden
kullanır, Discovery'nin SEÇTİĞİ kolonlar üzerinde (tarih değiştirme, sıralama, filtreleme)
chip'leri GERİ getirir, DÜŞÜK mühendislik maliyeti.

**Kesin sınır (kullanıcının "tam kırılım" talebi bağlamında ÖNEMLİ)**: bu seçenek YAPISI
GEREĞİ **asla TAM kırılım vermez** — SQL'in SEÇMEDİĞİ yeni bir boyutu sonradan ekleyemez,
yalnız o SPESİFİK sorgunun "dondurulmuş" görünümüdür. **Bu yüzden B, A/C'nin YERİNE
GEÇMEZ — yalnız onlar tamamlanana kadar (ya da hiç kapsanmayacak uzun-kuyruk sorular için)
bir ara-durum iyileştirmesidir.**

**Rakip araştırması (§5.2) sonucu**: bu fikir pazarda NADİR — tek gerçek emsal (Looker'ın
"Explore from Here"ı) on yıllık, kural-tabanlı, konuşmasal olmayan bir analist aracı.
Yani B, "kanıtlanmış bir deseni kopyalamak" değil, gerçek ama KANITLANMAMIŞ bir bahis —
mütevazı kapsamla (Looker'ın yaptığı gibi salt tip-tabanlı sınıflama) başlanmalı.

### C) Derleyiciye dinamik join/ilişki-gezme yeteneği ekleme — TAM kırılıma giden KESİN yol

`relationships.yml`'deki TAM grafiği sorgu anında kullanan bir mekanizma — bir küp
`route()`/Intent-JSON aşamasında talep edilen bir boyutu KENDİ `base_object`'inde
bulamazsa, ilişki grafiğinde bir yol varsa (örn. `oee_vardiya → partiler → personel`)
bunu OTOMATİK JOIN'leyerek derlemesi. **Bu, kullanıcının "küpler mükemmelleşsin, tam
kırılım alalım" talebinin TEK GERÇEK, ÖLÇEKLENEBİLİR karşılığı** — B gibi kısmi/geçici
değil, A gibi tek-tek elle inşa edilen view'lara da bağımlı değil: HER YENİ ilişki
`relationships.yml`'e bir kez eklendiğinde OTOMATİK olarak tüm küplere yayılır.

**Rakip araştırması (§5.2) bu seçeneğin risk değerlendirmesini DEĞİŞTİRDİ**: bu
KANITLANMAMIŞ bir spekülasyon değil — **Cube.dev'in derleyicisi TAM OLARAK bunu yapıyor**
(doğrulanmış, dokümante edilmiş): bildirilen ilişkiler üzerinden çok-sıçramalı join'leri
sorgu anında, materyalize view GEREKMEDEN çözüyor. Yani "bu mimari mümkün mü" sorusu
artık YANITLANMIŞ durumda — sektörde kanıtlanmış bir yol var.

**Gerçek belirsizlik artık FARKLI bir yerde**: Dima Cube.dev'in KENDİ motorunu değil,
`wren_core`'u (native/Rust, vendored bağımlılık, `backend/app/wren_service.py:491`) kullanıyor —
`cube_query_to_sql`'in docstring'i yalnız "manifest'teki küp tanımları"ndan bahsediyor,
dinamik graph-walk'tan bahsetmiyor. **Bilinmeyen şu**: wren_core bunu zaten (belgelenmemiş
biçimde) destekliyor mu, yoksa Dima'nın KENDİ derleme katmanında (cube_router.py'nin SQL
üretim seviyesinde) yeni bir join-planlayıcı mı yazması gerekecek? **Bunun cevabı ucuz bir
fizibilite adımıyla (wren_core kaynağını/dokümantasyonunu okumak, küçük bir deney) kısa
sürede netleşir** — büyük bir mühendislik taahhüdüne girmeden ÖNCE atılabilecek, düşük
maliyetli bir ilk adım.

**Hâlâ gerçek olan kavramsal risk**: §3.3'teki "çoklu-sıçrama istatistiksel bulanıklık"
(bir OEE-vardiyasına birden fazla operatör/parti düşebilir) sorunu OTOMATİK join'de de
AYNEN var — motor "doğru" bir join YOLU bulsa bile SONUÇ anlamlı olmayabilir. Yani C,
saf bir mühendislik projesi değil; HANGİ ilişkilerin "güvenle otomatik join'lenebilir"
(örn. `partiler→personel`, tekil-yönlü MANY_TO_ONE, bulanıklık yok) HANGİLERİNİN
"otomatik join'lenmemeli, elle onay/zengin-view gerektirir" (örn. `oee_vardiya→partiler`,
bire-çok, atıf belirsiz) olduğuna dair bir SINIFLANDIRMA/politika katmanı da gerektirir.

### D) Önerilen yol haritası (kullanıcının "tam kırılımı göz ardı etme" talebini yansıtacak şekilde revize edildi)

**Kesin/tam çözüm A+C'dir, B onların YERİNE geçmez — yalnız aradaki boşluğu geçici doldurur:**

1. **C için ÖNCE ucuz bir fizibilite adımı**: `wren_core`'un dinamik join/relationship
   yeteneğini (belgelenmemiş de olsa) gerçekten destekleyip desteklemediğini araştır —
   kaynak koduna/yayınlanmış dokümantasyonuna bak, küçük bir manuel deney yap. Bu, C'nin
   "Dima'nın kendi motoruna yeni bir join-planlayıcı yazma" (büyük iş) mi yoksa "var olan
   ama kullanılmayan bir yetenek mi" (çok daha küçük iş) olduğunu AYIRT EDER — sıralamayı
   bu belirler.
2. **A'yı PARALELDE, sürekli devam eden bir iş olarak yürüt**:
   `backend/demo/packs/modul/muhasebe/`, `backend/demo/packs/modul/satis/` — `ik`/`oee`
   kalıbında. C ne kadar güçlü olursa olsun, HER
   dikeyin KENDİ ölçü/boyut SÖZLÜĞÜNÜN (sinonimler, hangi ölçü neyi ifade ediyor) elle
   kürasyona ihtiyacı olacak — C, join'i otomatikleştirir, dikey-içi ANLAM işini değil.
   Hangi dikeyin önce geleceği gerçek kullanım verisiyle (interaction_log) önceliklensin.
3. **B'yi KÜÇÜK bir prototip olarak, A/C'nin YANINDA (yerine değil) dene** — Discovery
   cevaplarının HEPSİNE değil, en azından tarih/sıralama/filtre chip'i geri kazandırır;
   C tamamlanana kadar (ya da C'nin hiç kapsamayacağı gerçekten tek-seferlik/egzotik
   sorular için) kalıcı bir ara-katman olarak KALABİLİR — "geçici" demek "değersiz"
   demek değil, yalnız "TAM çözümün yerine sayılmasın" demek.
4. **§3.3'teki "personel×OEE" örneği C'nin İLK test vakası olabilir** — küçük, iyi
   anlaşılmış, tek bir ilişki zinciri (`oee_vardiya→partiler→personel`) üzerinden C'nin
   fizibilitesini kanıtlamak için ideal, düşük-riskli bir pilot.

## 7. Açık, kullanıcının karar vermesi gereken sorular

- **Öncelik**: C'nin fizibilite adımıyla mı (wren_core'un gerçek kapasitesini araştırmak,
  ucuz, hızlı, büyük taahhüt yok) başlansın, yoksa A (muhasebe/satış dikeyi) ile mi —
  yoksa ikisi paralel mi yürüsün? (Rapor D'de paralel öneriyor, ama kaynak/zaman kısıtı
  varsa sıra kullanıcının tercihine bağlı.)
- §3.3: "personel bazlı verimlilik" derken kastın `parti`'nin zaten sahip olduğu kişi-
  bazlı üretkenlik mi, yoksa gerçekten "OEE'nin kişiye bölünmesi" mi (ki bu istatistiksel
  olarak bulanık olabilir, C'nin "otomatik join'lenmemeli" sınıfına girebilir)? Cevap,
  hem A'da hem C'nin ilk pilot vakasında hangi yöne gidileceğini belirler.
- Dikey önceliklendirme (A.2): muhasebe mi satış mı üretim mi önce? Gerçek kullanım
  sıklığına mı, yoksa stratejik öneme mi göre karar verilsin?
- B (Discovery→geçici küp) prototipi onaylanırsa: bu YALNIZ session-scoped mi kalsın
  (dataset.py'nin bugünkü davranışı gibi, kalıcılık yok), yoksa sık tekrar eden bir
  Discovery-sorgu deseni fark edilirse bunu KALICI bir küp/view'a "terfi ettirme" (yarı-
  otomatik, insan onaylı) bir mekanizma da düşünülsün mü?
- C'nin "otomatik join'lenebilir vs. elle-onay-gerekir" sınıflandırma politikası: bu
  KURAL-tabanlı mı olsun (örn. "yalnız tekil-yönlü MANY_TO_ONE zincirleri otomatik,
  ONE_TO_MANY/çoklu-sıçrama elle onay ister" — `relationships.yml`'deki `join_type`
  alanı zaten bu ayrımı kısmen taşıyor), yoksa her ilişki için ayrı, elle bir "güvenli
  mi" bayrağı mı eklensin?
