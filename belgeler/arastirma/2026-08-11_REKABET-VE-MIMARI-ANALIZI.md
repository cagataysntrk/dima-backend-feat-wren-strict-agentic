# DİMA — REKABET, MİMARİ VE YETERLİLİK ANALİZİ

> **Belge türü:** araştırma raporu (geliştirme değil).
> **Tarih:** 2026-08-11 · **Kapsam:** rakip ürünler · mimari kıyas · ölçüm sisteminin
> kendisi · açık kaynak fırsatları · ne yapmalıyız.
>
> ⚠ Bu belgedeki her sayı **ölçülmüştür**. Ölçülmemiş bir şey *«bilinmiyor»* diye
> yazılmıştır. Bir rapor, en çok kendi bilmediğini gizlediğinde yanıltır.

---

## İÇİNDEKİLER

| kısım | bölümler |
|---|---|
| **1 · DURUM** | `§0` yönetici özeti · `§1` mimarinin kanıtı · `§2` grafik meselesi · `§3` «en kötü promptta cevap» · `§4` mimari teşhis: ters yatırım |
| **2 · SEKTÖR** | `§5` üç mimari kamp · `§6` on üç ürün · `§7` ölçülmüş gerçek · `§8` Türkçe vergisi ve hendeği · `§9` grafik seçimi · `§10` kök-neden algoritmaları |
| **3 · WREN** | `§11` motorun 15 yeteneğinden birini kullanıyoruz |
| **4 · MUHASEBE** | `§12` aptallık ettiğimiz yerler |
| **5 · AÇIK KAYNAK** | `§13` alınacaklar |
| **6 · BOŞA MI GİTTİ** | `§16` varlık muhasebesi |
| **7 · AGENTIC DURUMUMUZ** | `§17` iki paralel sistem · `§18` «robotik/katalog» ölçümü |
| **8 · CEVAP BİÇİMİ VE UX** | `§21` sektörde neyin kural olduğu |
| **9 · TÜRK PAZARI** | `§19` yerli rekabet haritası · `§20` boşluk ve pazar gerçeği |
| **10 · GİRİŞİMLER** | `§22` mezarlık · `§23` derin profiller · `§24` yakınsayan mimari · `§25` bağlam kavgası · `§26` ekip ve süre · `§27` asgari kapsam · `§28` sentez · `§29` bize düşen |
| **11 · AGENTIC SEKTÖR** | `§30` teşhisi düzelt · `§31` Anthropic rehberi · `§32` sabit mi serbest mi · `§33` MCP · `§34` çok adımlı sayısal · `§35` karar motoru · `§36` hedef mimari |
| **12 · NE YAPMALIYIZ** | `§14` adım adım uygulama planı (5 faz) · `§15` dürüst kapanış |
| **13 · YENİ GELİŞTİRİCİ** | `§39` okuma sırası · çalıştırma · curl · kapı · ölçüm tekrarı · dokunulmayacaklar · ilk hafta |

⚠ **Bölüm numaraları yazım sırasını, kısımlar okuma sırasını gösterir.** Metin içi
çapraz göndermeler bölüm numarasıyla yapıldığı için numaralar korunmuştur.


## 0 · YÖNETİCİ ÖZETİ — mimari yargı

**Soru:** mimarimiz doğru mu, mantığımız yeterli mi, rakiplere göre neredeyiz?

### 0.1 Kamp seçimi DOĞRU — ve bu küçük bir şey değil

Sektör 2026'da üç mimari kampa ayrıldı. **DİMA, LLM'in SQL yazmadığı, yapılandırılmış bir
niyet nesnesi ürettiği A kampındadır** — ThoughtSpot ve Google Looker ile aynı tarafta.
Bağımsız ölçüm (lkr.dev, 44 iş sorusu): semantik katman **%97**, ham SQL **%80**. Ve daha
önemlisi: ham SQL'in **7 hatası 3/3 koşumda tekrarladı** — yani **sistematik**, prompt ile
kapanmaz. Dört ayrı çalışma aynı yönü gösteriyor (+17…+72 puan).

⊙ **Bu tercih, geri kalan her şeyin üstünde durduğu doğru zemindir.** Julius AI gibi ham
şemaya serbest SQL yazan ürünler kurumsal ölçekte **%10 bandında**.

### 0.2 Ama ağırlık YANLIŞ dağıtılmış — beş mantık eksiği

| # | mantık eksiği | ölçüm | sektörün yaptığı |
|---|---|---|---|
| **1** | 🔴 **Garsonun bağlamı yok.** İsteme yalnız **statik katalog dökümü** (23.729 karakter) giriyor: örnek sorgu yok, iş sözlüğü yok, şema daraltma yok, çalıştır→hatayı gör→düzelt döngüsü yok | garson istemi **45 kod satırı**; route yığını **9.468 satır** | Wren'in kendi **AI Context Layer**'ı (`instructions.md` + `queries.yml` + LanceDB retrieval) — **aldığımız motorun içinde, kullanılmıyor**. Cube: **4 KB markdown → +17…+23 puan** |
| **2** | 🔴 **Ters yatırım.** Makineye Türkçe öğretmeye 9.468 satır; trafiğin daha büyük kısmını taşıyan hakeme 45 satır | route **%35,5** · garson **%37,0** | O model (*«kullanıcı dilbilimsel şemayı elle beslesin»*) **Microsoft'ta Aralık 2026'da, Tableau'da Şubat 2024'te kaldırıldı** |
| **3** | 🔴 **Motorun yüzeyi taranmamış.** `wren_core` **15 sembol** açıyor, **1'ini** kullanıyoruz | `rls.py` 380 · `dataset.py` 161 · manifest ~1.490 satır **yeniden yazılmış**; `ManifestExtractor.extract_by` (**şema daraltma**) hiç kullanılmamış | Şema bağlama hatası kurumsal ölçekte hataların **%27,6–33,0'ı** |
| **4** | 🔴 **Kök-neden yarım.** Layer-1'de kilitli (bileşik segment aranmıyor), **sürpriz (JS diverjansı) hesaplanmıyor**, **FDR düzeltmesi yok** | `§KN-toplam` **en büyük segmenti** seçiyor | Adtributor'ın kurucu örneği: *«yalnız explanatory power kullanan her analiz **büyük segmentleri sistematik olarak suçlar**»*. Ve **CHI 2018: kullanıcı içgörülerinin %60'ından fazlası yanlış** |
| **5** | 🔴 **Cevap tek kalıpta.** Ölçüldü: 8 farklı soru türünde chip sayısı **6,6,5,6,6,4,6,3** *(⟳08-12 yeniden ölçüldü: **6,6,6,6,5,6,6,5** — `bicim.py:14` kaydediyor; teşhis **güçlendi**, dizi daha da sabitleşti)*; olgu sayısı **hep 1-2**; **hiçbir cevapta çoklu grafik yok** | *«robotik / katalog gibi»* şikâyetinin sayısal karşılığı | Tableau Pulse **14 deterministik içgörü tipi** üretip **LLM'e yalnız cümleyi** kurduruyor |

### 0.3 Rakipler «mükemmel» değil — ölçümle

* **13 üründen 10'u doğruluk sayısı yayınlamıyor.**
* **Power BI Copilot** kapsam dışında **LLM genel bilgisinden uyduruyor** (kendi
  dokümanı); bağımsız ölçüm **%62,5**; uygulamacı: *«3 saniyede DAX üretti, düzeltmem
  45 dakika sürdü»*.
* **Databricks Genie**'nin **%84,5**'i **28 soruluk** bir sette (±13 puan).
* **Gartner:** *«Nearly every vendor claims agentic capability. **Very few have moved past
  natural-language querying.**»* · agentic analitik projelerinin **%60'ı 2028'e kadar
  başarısız olacak**.
* **Türkçe gerçek bir hendek:** Looker · Power BI · Fabric · Qlik **resmen yalnız
  İngilizce**. Ve BIRDTurk (SIGTURK 2026) ölçmüş: Türkçe **12-15 puan** yakıyor ama
  **ajanik mimari bu vergiyi ~3 puan azaltıyor** — orkestratör yatırımımızın hakemli
  doğrulaması.

### 0.4 Farkımız ve zayıflığımız aynı yerden doğuyor

Rakipler *«her soruya bir şey söyler»*; biz *«bilmediğimizde susarız»* — canlı ölçüm:
**zayıf altı promptun üçünde cevap yok**, korpusta **cevapsız %19,9**, canlı trafikte
**%21,8**.

⊙ Onların hatası **görünmez** (sessiz yanlış, kullanıcıya zarar verir); bizimki
**görünür** (boş ekran, ürünü kötü gösterir). **İkisi de kusur.** Ama dbt'nin cümlesi
bizim tarafımızı tarif ediyor: *«Text-to-SQL'de başarısızlık **makul ama yanlış bir
cevaptır**; semantik katmanda başarısızlık **bir hata mesajıdır**.»*

> 🔴🔴 **BU BELGEDEKİ SATIR/DOSYA SAYILARI BİR FOTOĞRAFTIR — ve 2026-08-12'de
> yeniden çekildi.** Bir denetim ajanı on iki kalemin **bayatladığını** ölçtü; hepsi
> kendi ölçümümle doğrulanıp güncellendi.
>
> ⚠ **Ve sayı, ÖLÇÜM YÖNTEMİ olmadan yeniden üretilemez** — bu yüzden yöntem burada:
>
> ```
> route yığını : wc -l cube_router niyet followup uyum deger_capasi turetme islev_sozcukleri
> backend      : find app -name '*.py'                    → 149 dosya · **56.899** satır
> test         : ls tests/test_*.py · cat tests/test_*.py  → **427** dosya · **74.313** satır
> belgeler     : find belgeler -name '*.md'                → **37** md · **52.731** satır
> § işareti    : grep -ohE '§[A-Z0-9][A-Za-z0-9._-]*' app/*.py app/routers/*.py | sort -u
>                                                          → 271 benzersiz
> ```
>
> ⊙ `§` sayısı için ajan **284**, ben **271** ölçtüm — fark **desen** farkıdır, kod
> farkı değil. *İki ölçüm ayrışıyorsa önce yöntemleri karşılaştırılır; sayılar değil.*
>
> ⚠ Bu satırlar **taban değildir**: güncel taban her zaman `lab/reports/` altındadır
> (`CLAUDE.md`'nin aynı uyarısı). *Bir belgeye yazılmış sayı, yazıldığı anın
> fotoğrafıdır; taban diye okunursa yanlış bir gerileme alarmı üretir.*

### 0.6 TEK SAYFALIK KARNE — sektör kontrol listesine karşı

> Her satır **ölçüldü**; ölçülmeyen *«bilinmiyor»* yazıyor.

| # | yetenek | sektör dayanağı | **DİMA** |
|---|---|---|---|
| 1 | Deterministik ara temsil (LLM SQL yazmaz) | **9 bağımsız emsal**; giriş bileti | 🟢 **VAR** — Intent-JSON + CubeQuery |
| 2 | Semantik katman | +17…+72 puan, dört ölçüm | 🟢 **VAR** — Wren MDL, 23 küp |
| 3 | Sorgu doğrulama (derleyici/dry-run) | Zenlytic Clarity Engine | 🟢 **VAR** — `dry_plan` · ⚠ AUROC **0,500** (doğruluk hakkında sıfır bilgi) |
| 4 | Triaj / belirsizlik kapısı | Cortex 1. ajanı · **+50 puan** | 🟢 **VAR** — `soz.py`, netleştirme chip'i |
| 5 | Beyan kültürü (*«eksik»* demek) | dbt: *«failure looks like an error message»* | 🟢 **VAR** — `uyum.py`, 131 işaretin çoğu |
| 6 | Kesitsel kök-neden (formül ayrıştırma) | LMDI · çoğu üründe **yok** | 🟢 **VAR** — `kok_neden.py` |
| 7 | Deterministik grafik kararı | Veezoo: etiketler bile VQL'den | 🟢 **VAR** — ADR-0024 · canlı **10/10** |
| 8 | Makbuz / provenance | Bruin · BitBoard · Basedash OEM'in merkezi | 🟢 **VAR** — Query Contract |
| 9 | Türkçe morfoloji | Veezoo'nun DACH kaması → **$6M** | 🟢 **VAR** — ⚠ 9.468 satır, ters yatırım (§4.1) |
| 10 | Çok-turlu bellek | — | 🟡 **VAR, tur bazında ÖLÇÜLMÜYOR** *(⟳08-12 ölçüldü ve bu satır **A12 ✅'inden DAHA DOĞRU**: tur kırılımı **kodu var** (`lab/garson_korpusu.py:302` başlığı yazıyor) ama diskteki artefakt onu **hiç taşımıyor** — kod, raporu üreten son koşumdan **sonra** eklenmiş. Yani tablo **hiç üretilmemiş**; ✅ bir kod işaretidir, bir ölçüm değil)* |
| 11 | VQR / hafıza | Snowflake VQR · Wren LanceDB | 🟡 **VAR ama garsona BESLENMİYOR** |
| 12 | Bütçe + durdurma | Snowflake · **Magentic-One stall ≤2** | 🟢 **VAR** *(§C2 `97dc8f6`)* — ~~uykuda~~ **ölçüldü:** `Butce(adim=8·saniye=30·sorgu=12)` **canlı**, `AZAMI_ADIM=12` koşmadan önce uygulanıyor, stall sayacı `ONARIM_TAVANI=2` (**§B4** ile geldi). Tavanlar kapıda kilitli |
| 13 | Araç kaydı + yetki + makbuz | Cortex 9 · Fabric 4 · Cube 16 | 🟡 **31 araç VAR — planlayıcı bayrağı KAPALI** *(⟳08-12: 25 bayattı; `§38.2 D6` ile 25→31. Ölçüm: `agent_plan_secimi: off`)* |
| 14 | MCP yüzeyi | *«dağıtım kanalının kendisi»* | 🟡 **VAR — `mcp_yuzeyi: beta`** *(⟳08-12: satır `off` diyordu, `features.yml:105` ölçüldü → **beta**. 🟡 kalıyor: beta bir açılış değil bir **kademe**)* |
| 15 | **Şema daraltma (schema linking)** | hataların **%27,6-33,0'ı** · %40→%90 | 🟢 **VAR** *(§B1)* — ⟳ **YENİDEN ÖLÇÜLDÜ 08-12, İLAN EDİLEN ARALIK YANLIŞTI:** tam katalog **23.729 kr** (birebir doğrulandı), sekiz üretim sorusunda budama **%0–95** — `%71-90` değil. Ve **2/8 soruda budama HİÇ ateşlemiyor** (*«kohort analizi»* · *«en çok fire veren makine»* → 23.729 kr, **fail-open**: sorunun içerik sözcükleri katalogda tam eşleşmezse budanmaz). ⊙ Fail-open bir **kusur değil tasarım**, ama *«%71-90»* onu **gizliyordu** — bir kazanç aralığının tabanı yazılmazsa, aralık bir ölçüm değil bir **reklamdır**. ⚠ İndeks **her zaman tam**, yalnız **metin** budanır (`katalog_metni`) |
| 16 | **Örnek sorgu / few-shot retrieval** | Cube **+17…+23**, 4 KB'den | 🟢 **VAR** *(§B2)* — `vqr.few_shot_block()` **garsona** bağlandı (önce yalnız Discovery'ye bağlıydı: *«yazılmış ama bağlanmamış»*) |
| 17 | **İş sözlüğü (`instructions.md`)** | Wren AI Context Layer | 🔴 **YOK — ve ölçüm nerede olmadığını GÖSTERDİ** *(2026-08-12)*. ⊙ `business_rules` **VAR ve BAĞLI** (`wren_service:1008` → `schema["business_rules"]` → `llm.py:226`) ama **yalnız Discovery'nin SQL istemine**; garsonun istemi (`_cube_select_system`) **yalnız katalog** alıyor — yani raporun *«ters yatırım»* bulgusunun tam kaldıracı burada duruyor. ⚠ Mevcut `knowledge/rules/*.md` **garsonun sözlüğü değil**: içeriği SQL semantiği (oran = SUM/SUM) ve kaynak şema bilgisi (Logo `TRCODE`/`IOCODE`) — garson SQL yazmaz, **küp seçer**. 🔴 **Canlı ölçülen somut kusur:** *«bütçe gerçekleşme oranı»* ve *«hedefin neresindeyiz»* → yalnız **`toplam_hedef`** dönüyor. Üç düzeyde ölçüldü: `butce` küpünde gerçekleşme ölçüsü **yok** (yalnız `toplam_hedef`·`ort_hedef`·`hedef_miktar_toplam`·`kalem_sayisi`); `butce_hedefleri` tablosunda gerçekleşme **kolonu yok** (`demo/genisletme.py:164`); ama küp `gerçekleşme` kelimesini **cube sinonimi olarak talep ediyor**. ⊙ Küpün kendi başlığı bunu zaten biliyordu: *«Gerçekleşme tek başına bir gerçekleşme değildir; bir hedefe göre gerçekleşmedir.»* — gerçekleşme **başka küplerde** yaşıyor, yani bu bir **çapraz-küp KPI** (`kpi.py`) kalemidir. ⚠ **Genelleme DENENDİ ve ÇÜRÜDÜ:** *«küp sinonimi hiçbir ölçü/boyut adına karşılık gelmiyorsa kusurdur»* yüklemi **66 kalem** buldu ve çoğu meşru (`bakim ← tamir` · `ik ← insan kaynakları` · `sevkiyat ← lojistik`): küp sinonimleri **konuyu** adlandırır, ölçüyü değil. `gerçekleşme`'yi `tamir`'den ayıran şey **yapısal değil anlamsaldır** → kapalı bir kapı kurulamaz (`ADR-0008`). *Bir kusuru genellemek, ancak genellemesi ölçülebiliyorsa doğrudur.* |
| 18 | **Reflect + repair döngüsü** | Snowflake Error Correction · Genie | 🟢 **VAR** *(§B4)* — `plan_garson` onarım döngüsü: red **sınıfı** garsona geri veriliyor, tavan **2** (Magentic-One). Ölçüldü: tutma **%25 → %90** |
| 19 | **Skills (markdown metodoloji)** | **Anthropic: %21 → >%95** | ⟳✅ **BU CÜMLE ARTIK YANLIŞ (2026-08-12, aynı gün):** `demo/skills/` **var** — `yoy-orani.md` · `huni.md` · `kohort.md`; `katalog_metni.skills_metni()` onları okuyor, bayrak `skills` (off, şart `§26`). Eski hâli: *«dizin yok, `skills` atfı yok»*. 🔴 **VE ARTIK SOMUT BİR GEREKÇESİ VAR — canlı ölçüldü.** Üç metodoloji sorusu basıldı: ① *«fire %10 azalsa ne olur»* → ✅ **beyanlı red** (forecast bilinçli kapsam dışı — doğru davranış) ② *«müşteri kohort analizi yap»* → 8 satır, ama **kohort değil PİVOT** (müşteri × ay); 3 adım makbuzu var, *«kohort metodolojisi uygulanmadı»* beyanı **yok** ③ 🔴 *«geçen yıla göre ciro **büyüme oranı**»* → **cevapsız**. Oysa YoY **çalışıyor ve deterministik**: *«geçen yıla göre ciro»* → `toplam_ciro` · `toplam_ciro_gecen` · **`toplam_ciro_degisim_yuzde: 9.7`** (`source=cube`). Yani **büyüme oranı zaten hesaplanıyor**; kıran şey ifadenin kendisi. İz teşhisi tam veriyor: `garson çağrıldı — kullanılabilir bir karar dönmedi` · `niyet: tür=kirilim+kiyas+trend · 🔴temsil-yok=kiyas · granülerlik=year · bilinmeyen=buyume,orani`. ⊙ Niyet nesnesi isteği **doğru teşhis etmiş** (kıyas+trend+yıl) ve temsil edilemeyeni işaretlemiş; sistem yine de sahip olduğu yeteneği kullanmamış. ⚠ **İkincil kusur aynı yanıtta:** netleştirme chip'leri *«ortalama hız» · «fire» · «fire oranı»* — bir **ciro** sorusuna. *Bir netleştirme, sorulanla ilgisiz seçenekler sunuyorsa netleştirmez, oyalar.* ⊙ Bu, `§B10`'un tam olarak öngördüğü boşluk: *«kohort · funnel · retention · **YoY-oranı** · what-if — her biri bir markdown iş akışı»*. ⚠ Ve `CLAUDE.md`'nin en üst kuralı çözümün **yerini** de söylüyor: route'a dil eklenmez, **garsona bağlam** verilir — Skills tam olarak o bağlamdır. 🔴 Ölçüm engeli yazılı: garsonun doğruluk ölçümü **yok** (`§26`, PARK) → kazanç ölçülemez. Bu yüzden yapılırsa **bayrakla** ve açılış şartı `§26` olarak yapılmalı. |
| 20 | **Ephemeral/karalama sorgusu** | Hex | 🟡 **AMACI KARŞILANIYOR, MEKANİZMA FARKLI** *(ölçüldü 2026-08-12)*. Hex'in ephemeral sorgusunun **işi** *«ajan önce veriyi tanısın»*dır; biz bunu **soru başına gizli sorguyla değil, kurulum anında BİR KEZ** yapıyoruz: `_enrich_categorical` (düşük kardinaliteli kolonlara `values`) + `_enrich_cube_dim_values` (türev boyutlara motor üzerinden DISTINCT) + `value_index.FuzzyIndex`. 🔴 **Kapsam ölçüldü: 121 boyutun 120'si (%99) değer taşıyor**; `FuzzyIndex`'in **beş tüketicisi** var (`cube_router` 8 atıf · `deger_capasi` 5 · `context` · `varlik` · `features`). ✅ **Canlı doğrulandı:** *«**kontinü kasar** makinesinde kaç arıza»* → `makine = "KONTİNÜ KASAR"` (kullanıcı küçük harf yazdı, profil eşledi) · 15 arıza. Ve profil `§DK-2`'yi besliyor: *«**baskı** bölümünde fire»* → *««Baskı» departman listesinde yok. Var olanlar: Boyahane»* — **LLM'siz netleştirme, sıfır satır sunulmadı**. ⚠ **Yapılmayan:** soru-başına keşif sorgusu. Ve bu bilinçli sayılmalı — raporun kendi `§31`'i Anthropic'i alıntılıyor: *«mümkün olan EN BASİT çözüm… karmaşıklığı ancak GÖSTERİLEBİLİR ŞEKİLDE sonuçları iyileştiriyorsa ekleyin»*. Bir kez profilleme, her soruda gizli sorgudan **ucuz ve ölçülebilir**. ⊙ 🔴→🟡: *bir yeteneği rakibin mekanizmasıyla aramak, onu kendi mekanizmamızda görmemeye yol açar.* |
| 21 | **Olgu tipi taksonomisi** | **Pulse'un 14 tipi** | 🟢 **VAR** *(§D1 ölçümü teşhisi çürüttü)* — *«hep 1-2»* **az örneklemdenmiş**: canlıda **0–6** olgu, `TANINAN` **12 tip**. Kusur üretimde değil **tüketimdeydi** (`kiyas`+`segment_delta` şablona tanıtılmamış) |
| 22 | **Cevap biçimi kararı** | OpenAI Model Spec | 🟢 **VAR** *(§D3 `88579d8`)* — `bicim.py` **tek sahip**: niyetin kapalı türleri × chip kovaları. Chip **6,6,6,6,5,6,6,5 → 4,6,2,4,4,4,6,3** |
| 23 | **Sürpriz (JS diverjansı)** | Adtributor kurucu örneği | 🟢 **VAR** *(§E2 `21f1b8a`)* — Jensen-Shannon segment sürprizi + beyan. ⚠ **Sıralama DEĞİŞTİRİLMEDİ**: eklenen bir **ölçü** ve onun beyanı |
| 24 | **FDR düzeltmesi** | **CHI 2018: içgörülerin %60+'ı yanlış** | 🟡 **BH UYGULANAMAZ, YERİNE BEYAN** *(§E3 `74678ef`)* — ölçüldü: bu depoda **p-değeri yok**, eşik bir z-kesimi; BH'yi uygulamak **normallik varsayımını dayatmak** olurdu. Yerine **tarama beyanı**: *«N aday tarandı, M'i işaretlendi; ~K'sı şansa düşer»* |
| 25 | **Bileşik segment araması** | HotSpot **F1 >%90** ↔ Adtributor **<%15** | 🔴 **YOK** — layer-1'de kilitli |
| 26 | **Garson doğruluk ölçümü** | Hex 30-50 soru · Anthropic %90 kapısı | 🔴 **YOK** — trafiğin **%37'si**, ölçümü **15 senaryo · 21 tur** *(⟳08-12 birim düzeltmesi: `lab/garson_korpusu.py::KORPUS` **15** senaryo taşıyor, **21** onların tur toplamı; `lab/reports/garson_korpusu.md` başlığı zaten «payda 21 — kayıt kümesi, «korpus %» değil» diye uyarıyordu. ㉗)* |
| 27 | **Kurulum süresi ölçümü** | rakipler *«7 gün»* satıyor | 🔴 **YOK** *(⟳08-12: kalem **artık işaretli** — `§A4` ⏸ PARK, şartı **gözlenebilir**: bir sonraki gerçek kurulum zamanlanarak yapılır. Makine tarafı ölçüldü: `compose_and_build` **4,66 sn**; baskın bileşen **insan emeği** ve geriye dönük kurtarılamaz — dört şirket paketlenmiş, **süre kaydı yok**)* |
| 28 | **Yayınlanmış doğruluk** | *«savunma değil SİLAH»* | 🟢 **VAR** *(§F8 `45730be`)* — [`belgeler/DOGRULUK.md`](../DOGRULUK.md): **%95,6** (payda 11.237) + **iki payda birden** + şişme **25,3×** + **en düşük şirket tabloda** + **bilinen körlükler** + yeniden üretme künyesi. Kapıyla çürümüyor |
| 29 | **İlan edilmiş kapsam** | yaşayanların **hepsinde** var, ölenlerin **hiçbirinde** | 🟢 **VAR** *(§F7 `ddc6fa3`)* — `yetenek.py` **üç kutu** (`anlamadim`·`yapamiyorum`·`yapmiyorum`) ve canlı: *«forecast v1'de yok — bilinçli bir karar… **Yapabildiğim:** geçmiş eğilimi gösterebilirim»* + chip |
| 30 | **Ajan yüzeyinden dağıtım** | Rill: projelerin **%50+'ı ajan kuruyor** | 🔴 **YOK** |

**Sayım:** 🟢 **18 var** · 🟡 **6 yarım** · 🔴 **6 yok**  *(30 satır — ölçüldü 2026-08-12)*

### 0.7 🔴🔴 KİMLİK HARİTASI — `D9` **ÜÇ AYRI İŞİ** adlandırıyor (ölçüldü 2026-08-12)

Bu belgede kart kimlikleri (`A1`·`B12`·`D9`…) **tek bir uzaydan gelmiyor**; üç ayrı
bölüm aynı harf-sayı adlarını **bağımsız olarak** kullanmış. Ölçüm (`68` kimlik
ayrıştırıldı, **21'i** birden çok başlık taşıyor; gürültü elenince **dokuz `D`** gerçek
çakışma):

| kimlik | `§38` — **kapanış kartları** | `§14.1` — **FAZ 3 yol haritası** | `§14.11`/`§14.14` — **rakip analizi kalemleri** |
|---|---|---|---|
| **D1** | Garsona şema verme | Olgu sayacı | — |
| **D2** | Garsona örnek verme | Taksonomiyi aç | — |
| **D3** | İş sözlüğü | Cevap biçimi bir KARAR olsun | — |
| **D4** | Belirsizlik | Ön-uç sayı biçimi | — |
| **D5** | Sorgu hatası | Takip anlama | — |
| **D7** | Yetki denetimi (plan) | — | AVA `ckb` + `purpose` alanı |
| **D8** | Durdurma koşulu | — | CompassQL etkinlik tabloları |
| **D9** | Metodoloji (kohort/funnel/YoY) | — | Metabase `candidates` + `agent_error` |
| **D11** | Olgu üretimi | — | Denormalizasyon |

🔴 **VE `D` UZAYI TEK ÇAKIŞAN UZAY DEĞİL — `B9` ÜÇ ŞEYİ ADLANDIRIYOR** *(⟳ 08-12)*:

| kimlik | `§14.14` kalemi | **kodda** | **kapıda** |
|---|---|---|---|
| **B9** | ⏸ iki-sağlayıcılı LLM hakem | `app/diyalog.py:89` **ODAK VARLIK** (✅ canlı) | `tests/test_b9_sparc_iliskileri.py` **SParC ilişkileri** |

⚠ **Ve bunu `test_kimlik_uzayi_tek_anlamli` GÖREMEZ** — ve bu bir kusur değil bir
**kapsam**: o kapı **raporu** ayrıştırır, `B9`'un öteki iki anlamı **kodda** yaşıyor.
Bir belgeyi ayrıştıran kapı, belgenin dışındaki bir çakışmayı göremez. *Bir kapının
kapsamı, kapının kendisi kadar bir vaattir* — bu yüzden sınırı burada yazılı.

🔴 **Bu bir biçim kusuru değil, bir ÖLÇÜM kusurudur.** Çakışan bir kimlik iki farklı
işaret taşıyabilir ve **ikisi de doğru** görünür:

    «✅ D1 · Olgu sayacı TAMAMLANDI»            (§14.1, satır 3657)
    «⏸ D11 olgu üretimi — sayaç tesisatı PARK»  (§38.3/§40.9, satır 4862)

İkisi **aynı işi** anlatıyor, biri ✅ biri ⏸. Bir tarama hangisini okursa onu doğru
sanar. *Bir raporda bir kimlik iki işi gösteriyorsa, o raporun karne satırları artık
**sayılamaz** — çünkü sayım kimliğe dayanır.*

⊙ **Ve bedeli soyut değil, bu turda ödendi:** `§14.11 D9` (*Metabase `candidates` +
`agent_error`*) şunu yazıyor: *«MCP açılınca (C3) **zorunlu** hâle gelir»*. Ölçüldü —
`mcp_yuzeyi: beta` **AÇILDI** (`features.yml:105`), yani şart **gerçekleşti**; ama madde
**işaretsiz** duruyor ve hiçbir tarama kırmızı vermiyor, çünkü *«D9»* adı `§38`'de ✅
(*Metodoloji*) diye okunuyor. **Bir kimliğin çakışması, bir borcu görünmez yapar.**

⚠ **Kimlikler YENİDEN NUMARALANMIYOR.** Bu belge üç ayrı turda üç ayrı bağlamda yazıldı
ve numaraları değiştirmek, ona atıf yapan **on beş commit mesajını** ve dört kapı
dosyasını **sessizce yanlış** yapardı — yani çakışmayı düzeltirken **daha kötü** bir
çakışma üretirdi. Onun yerine ayrım **yazıya geçirildi** ve bir kapıya bağlandı
(`tests/test_kimlik_uzayi_tek_anlamli.py`): yeni bir çakışma doğarsa bu tablo
güncellenene kadar kırmızı kalır.

> *Bir kimliği yeniden adlandırmak geçmişi yanlışlar; onu belgelemek yalnız geleceği
> düzeltir — ve bir raporda düzeltilebilecek tek zaman gelecektir.*


> ⟳ **BU SATIR BAYATTI ve düzeltildi.** Eski hâli: *«🟢 9 var · 🟡 5 yarım · 🔴 16 yok»* —
> yani **30 satırın 16'sı**. Oysa satırların kendisi sayıldığında **18 yeşil** çıkıyor:
> aradaki fark bu oturumun kapattığı kalemlerdir (§B1·§B2·§B4·§C2·§D1·§D3·§E2·§F7·§F8…)
> ve karne **satır satır güncellenirken manşeti güncellenmemişti**.
>
> 🔴 Bu, `§F8`'in (*«yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan
> kötüdür — çünkü ona güvenilir»*) **kendi rapordaki hâliydi**: bu belgeyi açan biri
> *«9 var, 16 yok»* okuyup ürünü yarısı yapılmış sanırdı.
>
> ✅ Artık **kapılı**: `backend/tests/test_karne_kendini_sayar.py` manşeti satırlardan
> **yeniden hesaplar**; ayrışırlarsa kırmızı olur. *Bir karneyi elle saymak, bir gün
> yanlış saymaktır.*

⊙ **Kalan 🔴 altı** ve dördü ölçülmüş kararlarla kapalı sayılır:
`26 garson doğruluk ölçümü` · `27 kurulum süresi ölçümü` → **ölçüm işi**, kullanıcının
bağlayıcı kuralıyla PARK (*«ölçüm/altyapı tesisatı ürün değildir»*); `30 ajan yüzeyinden
dağıtım` → `mcp_yuzeyi` açılışına, o da `§C1`'e bağlı; `25 bileşik segment araması`
layer-1'de kilitli.

🔴 **Gerçekten açık TEK ürün kalemi: `17 iş sözlüğü`** — ve onun da eksiği veri/kod
değil **bir BEYAN** (12 bütçe kaleminin operasyonel küp karşılığı; şirkete göre değişir,
iş tarafı bildirir — uydurmak `§38.4` ihlali olurdu).
⊙ `19 Skills` **mekanizması kuruldu** (`demo/skills/*.md` + `katalog_metni.skills_metni`
+ `skills` bayrağı); bayrak **kapalı** ve açılış şartı yazılı: `§26` (garsonun doğruluk
ölçümü). `20 ephemeral` **🟡'ye çevrildi** — Hex'in işini kurulum-anı profillemeyle
yapıyoruz (**120/121 boyut** değer taşıyor, canlı doğrulandı).

⊙ **Ve dağılımın anlamı:** on sekiz yeşilin tamamı **mimari** kararlar — yani *«doğru
şeyi kurmuşuz»*. Altı kırmızının çoğu **besleme, ölçüm ve ambalaj** — yani *«kurduğumuzu
çalıştırmamışız»*. **Altı sarının çoğu zaten yazılmış ama KAPALI.**

> ⟳ **BU PARAGRAFLAR DA BAYATTI ve düzeltildi (2026-08-12).** Manşet iki tur önce
> düzeltilmişti ama hemen altındaki üç cümle *«yedi»* · *«üç ürün kalemi»* · *«dokuz
> yeşil / on altı kırmızı / beş sarı»* demeye devam ediyordu — yani kapı **tek cümleyi**
> ölçüyordu ve yanındaki paragraf yalan söylüyordu.
> *Bir kapıyı tek bir cümleye bağlamak, komşusuna yalan söyleme izni vermektir.*
> ✅ Kapı genişletildi: sayı **sözcükleri** de (kapalı bir gramer sınıfı) satırlarla
> karşılaştırılıyor — `test_karne_kendini_sayar.py`.

*Bir sistemin karnesi, neyi yapamadığını değil, yapabildiği hâlde yapmadığını gösterdiğinde
işe yarar.*

### 0.55 ⚠ Bu raporun sınırı

Oturumun arama bütçesi tükendi. **Teknik yol haritası (§14.0-14.5, §14.7) arama
gerektirmeyen kanıtlara dayanıyor — güvenle ilerlenebilir.** Ama **§14.6 (pazar/kama/
fiyat/kanal)** keşfe dayanıyor ve o temel **bir kez zaten çöktü** (beş yerli oyuncu
kaçtı, §19.7). Ayrıntı: **§37**.

### 0.5 Tek cümlelik yargı

> **Mimari kamp doğru, semantik katman gerçek bir hendek, kök-neden cebiri sektörün
> önünde — ama hakem katmanı bağlamsız, motorun yarısı kullanılmamış ve cevap biçimi tek
> kalıpta. Sorun ne mimarinin yönü ne de emeğin miktarı; sorun emeğin YERİ.**

## 1 · MİMARİNİN KANITI — sistem gerçekte nasıl çalışıyor

> ⚠ Bu bölüm bir **test eleştirisi değil**. Amacı tek: mimarinin hangi
> basamağının gerçekte yükü taşıdığını göstermek. Kusurlarımızı bulamamamızın
> sebebi ancak bundan **sonra** anlam kazanıyor.

### 1.1 🔴 Yükü taşıyan basamak, emeğin gittiği basamak DEĞİL

`interaction_log`, **3.554** kayıt (canlı kullanım):

| basamak | `source` | adet | pay | kapı ölçüyor mu? |
|---|---|---|---|---|
| **garson** (Intent-JSON) | `cube+llm` | 1.316 | **%37,0** | 🔴 **HAYIR** |
| **route** (0 LLM) | `cube` | 1.260 | **%35,5** | ✅ evet (korpus) |
| **cevapsız / netleştirme** | `None` | 776 | **%21,8** | ◐ kısmen |
| meta / katalog | `meta` `catalog` | 132 | %3,7 | ✅ |
| **Discovery** (ham SQL) | `llm:*` | 59 | %1,7 | 🔴 hayır |
| VQR · yükleme · doğrulama | — | 11 | %0,3 | ◐ |

⊙ **Mimari sonuç:** ürünün **yükünü** garson taşıyor (%37,0), **emeğini** route
aldı (9.468 satır). Ve garson, mimarinin **en az geliştirilmiş** basamağı —
istemi 45 satır, bağlamı statik bir katalog dökümü, kendini düzeltme döngüsü yok.
*Bir sistemin en çok kullanılan parçası, en az düşünülmüş parçasıysa, kusur
bulma hızı hiç düşmez.*

### 1.2 Neden bu ölçüde göremedik — kapsam yanılsaması

`lab/reports/nl_corpus.md`'nin **kendi** satırları:

| şirket | ham tur | 🔴 cevapsız | **semantik vaka** | şişme |
|---|---|---|---|---|
| boyahane | 9.413 | 1.431 (%15,2) | **336** | 28,0× |
| atiksan | 1.447 | 413 (%28,5) | **68** | 21,3× |
| gulteks | 1.618 | 479 (%29,6) | **83** | 19,5× |
| gitas | 2.479 | 657 (%26,5) | **103** | 24,1× |
| **TOPLAM** | **14.957** | **2.980 (%19,9)** | **590** | **~25×** |

⚠ *«doğru=95»* manşeti bir **uçtan uca doğruluk değildir**: raporun kendi tanımıyla
*«DOĞRU CUBE: 7210/7519»* — yani **SQL üretebilmiş** turlar içinde doğru küp oranı.
Cevapsız kalan %19,9 bu paydanın **dışındadır**.

### 1.3 Sistemin büyüklüğü

| | ölçü |
|---|---|
| backend uygulama | **149 modül · 56.215 satır** (34.945 kod + 11.594 yorum + docstring) |
| test | **410 dosya · 71.534 satır** — uygulamanın **1,24 katı** |
| belge | **36 belge · 52.147 satır** |
| en büyük iki modül | `ask.py` **6.012** · `cube_router.py` **4.981** |
| `ask()` tek fonksiyon | **1.416 kod satırı** (tavan 1.414, 7 muafiyetle) |
| kod içi `§` kural işareti | **131 farklı işaret** |
| büyüme tavanı muafiyeti | **120 kayıt** (4 ayrı liste) |

⊙ Ürünün etrafındaki iskele (test + belge = 113.776 satır), ürünün kendisinin
(53.725) **2,1 katı**. Bu bir kalite işareti **de** olabilir, bir ağırlık işareti **de**.
Ayıran şey: iskele ürünün **hangi kısmını** tutuyor? Yukarıdaki tabloya göre: **%35,5'ini**.

### 1.4 Hakem katmanı: mimarinin en kritik, en az bilinen parçası

* `lab/reports/garson_korpusu.md` → **payda 21** ve kendi notu: *«⚠ kayıt kümesi —
  «korpus %» değil»*.
* `lab/kapi.py:375` → *«🔴 `garson` HİÇBİR TOPLU KOŞUMDA YOK»*.
* `garson_kararlilik.json` → 25 senaryo, kararlılık **1,0** (yani **tutarlı**, ama
  tutarlılık doğruluk değildir — aynı cevabı üç kez vermek onu doğru yapmaz).

🔴 **Trafiğin %37'sini taşıyan basamağın otomatik doğruluk ölçümü YOKTUR.** Bu, bu
belgedeki önemli bulgudur.

---

## 2 · GRAFİK MESELESİ — iddia ve ölçüm

**İddia:** *«biz daha grafik oluştururken binlerce hata alıyoruz.»*

**Ölçüm (canlı, 10 senaryo, tek tek):**

| soru | dönen | doğru mu |
|---|---|---|
| «bu yıl makine bazında toplam üretim» | `bar` | ✅ |
| «aylık ciro trendi» | `line` | ✅ |
| «makine ve vardiya bazında oee» | `heatmap` | ✅ |
| «bu yıl toplam ciro» | `kpi` | ✅ |
| «müşteri bazında ciro ve fire oranı» | `scatter` | ✅ |
| «aylık üretim ve enerji tüketimi» | 2 bölümlü belge + `line` | ✅ |
| «makine bazında oee ve fire oranı» | `scatter` | ✅ |
| «müşteri bazında ciro» | `bar` | ✅ |
| «vardiya bazında duruş nedeni dağılımı» | `heatmap` | ✅ |
| «aylık makine bazında üretim» | `line` | ✅ |

⊙ **10/10 doğru grafik tipi. Tek bir «çizilmedi» yok.**

⚠ Ve iki hipotezim **çürüdü**:
* *«backend `facet_measure`/`waterfall` üretiyor, ön-uç tanımıyor»* → ön-uç **ikisini de**
  tanıyor (`lib/chart.ts`, `lib/types.ts`).
* *«çizilemeyen grafik sessizce tabloya düşüyor»* → düşüyor ama **gerekçesiyle**
  (`viz.cizilmedi` → *«ⓘ grafik yerine tablo — <sebep>»*).

🔴 **Yani grafik katmanı sistemin EN SAĞLAM parçalarından biri.** Kullanıcının yaşadığı
*«grafik hatası»* deneyimi büyük olasılıkla grafiğin kendisi değil, **grafiğin gösterdiği
şeyin yanlış/eksik olması** — yani üstteki basamakların kusuru. Bir grafik, yanlış bir
sorgunun üstüne doğru çizildiğinde de yanlış görünür.

*Bir belirtiyi yanlış organa yazmak, tedaviyi de yanlış yere yapar.*

---

## 3 · «EN KÖTÜ PROMPTTA BİLE CEVAP» — ölçüm

Altı zayıf/konuşma dilinde soru, tek tek:

| soru | sonuç |
|---|---|
| «fabrika nasıl gidiyor» | ✅ 6 adımlık plan, 11 satır |
| «en kötü makine hangisi» | ✅ cevap (dönem varsayımı beyanlı) |
| «hangi müşteriyle çalışmayı bırakmalıyız» | ✅ cevap |
| «işler iyi mi» | 🔴 **cevap yok** — *«ekranda sayı yok»* |
| «bu ay ne oldu» | 🔴 **cevap yok** — *«Hangi ölçüyü istiyorsun?»* |
| «kısaca özetle» | 🔴 **cevap yok** — *«ekranda rapor yok»* |

⊙ **3/6 cevapsız.** Üçü de *bağlamsız açılış* sorusu. Rakiplerin en görünür üstünlüğü
tam burada: **bir şeyle başlarlar.** Bizim üç reddimiz de *dürüst* ama kullanıcı için
sonuç aynı: ekran boş.

⚠ Ve bu, korpusun ölçtüğü **%19,9 cevapsız** oranının canlı karşılığıdır.

---

## 4 · MİMARİ TEŞHİS — «ters yatırım»

Kullanıcının cümlesi: *«garson mantığımız, mimarimiz, logic'imiz iyi değil gibi; AI
mühendisi değiliz sonuçta.»* Bu bölüm o cümlenin **ölçümüdür**.

### 4.1 Emek nereye gitti

| basamak | trafik payı | yazılmış kod |
|---|---|---|
| **route** — deterministik Türkçe NL→CubeQuery | **%35,5** | **9.468 satır** (`cube_router` · `niyet` · `followup` · `uyum` · `deger_capasi` · `turetme` · `islev_sozcukleri`) |
| **garson** — Intent-JSON hakemi | **%37,0** | orkestratör *koşumu* dâhil 5.701 satır; ama **hakemin kendi istemi: 45 kod satırı** |

⊙ **Makineye Türkçe öğretmek için 9.468 satır yazdık; trafiğin daha büyük kısmını
taşıyan hakemi 45 satırlık bir istemle yönetiyoruz.**

Ve bu, mimarinin **kendi en üst kuralıyla** çelişiyor. `CLAUDE.md` şöyle diyor:

> *«Route'a — yani NLP'ye — Türkçe öğretmemiz gerekir ki bu gereksiz. … İntent
> algılamada asıl **LLM'e** güveniyoruz.»*

Kural doğru yazılmış, **yatırım tersine yapılmış**. 131 `§` işareti, 120 büyüme
muafiyeti ve `ask()`in 1.416 satırı bu tersliğin faturasıdır.

### 4.2 Garsonun eksik olduğu şey: **BAĞLAM**

Garsonun istemine bugün giren tek şey:

```
statik katalog dökümü (23.729 karakter · 23 küp) + kullanıcının sorusu
```

**Girmeyenler:**

| eksik | ne işe yarardı | bizde var mı |
|---|---|---|
| **örnek sorgular** (few-shot / retrieval) | modele *«bu şirkette böyle sorulur, karşılığı budur»* demek | 🔴 hayır — `vqr.py` **var** ama yalnız *replay* basamağında (ladder #2), garsona **beslenmiyor** |
| **iş sözlüğü / talimatlar** | *«biz fire'yi kg konuşuruz»*, *«gerçekleşme = …»* | 🔴 hayır (yalnız `SynonymOverride`) |
| **şema daraltma (schema linking)** | 23 küpün tamamı yerine ilgili 2-3'ünü göstermek | 🔴 hayır — **her soruda 23.729 karakterin tamamı** gidiyor |
| **çalıştır → hatayı gör → düzelt döngüsü** | üretilen sorgu patlarsa modele hatayı geri vermek | ◐ kısmen — `plan_garson`'da **tek** bir *«DÜZELTME TURU»*; `llm.py`'deki yeniden denemeler yalnız **boş yanıt** içindir |
| **kararlılık ölçümü ≠ doğruluk** | — | `garson_kararlilik.json` **1,0** diyor; ama üç kez aynı cevabı vermek onu doğru yapmaz |

🔴 **Ve en can sıkıcı olan:** kullandığımız motorun kendisi (**Wren AI**) bu katmanı
zaten sunuyor. Wren'in mimarisinde `instructions.md` (iş bilgisi) + `queries.yml`
(örnek sorgular) + **LanceDB hibrit erişim** olan bir **AI Context Layer** var. Biz
Wren'in **motorunu ve MDL'ini** aldık, **AI bağlam katmanını almadık** — ve onun yerine
9.468 satır Türkçe kural yazdık.

*Bir kütüphanenin en pahalı parçasını yeniden yazmak, onu kullanmamanın en pahalı
biçimidir.*

### 4.3 Neden her 20 soruda yeni kök çıkıyor — sayısal cevap

Son beş turun ölçümü:

| tur | senaryo | yeni kök |
|---|---|---|
| CC | 26 | 4 |
| DD | 22 | 4 |
| EE | 12 | 3 |
| FF | 5 | 1 |
| GG | 4 | 1 |

⊙ **Oran ~5 senaryoda 1 kök ve DÜŞMÜYOR.** Olgunlaşan bir sistemde bu oranın azalması
beklenir. Azalmıyorsa, sonlu bir kusur havuzu boşaltılmıyor demektir — **kombinatoryal
bir uzay örnekleniyordur**:

```
23 küp × ~8 ölçü × ~7 boyut × 6 soru türü × 4 yol × 5 tur tipi × beyan sınıfları
```

Bu uzayın büyüklüğü **on binlerce** hücredir. Elle yazılmış her kural **bir hücreyi**
kapatır. 131 işaret, on binlerce hücrenin 131'i demektir.

🔴 **Bu bir disiplin sorunu değil, bir YÖNTEM sorunudur.** Aynı hızla devam edersek
kusur bulma oranı da aynı kalır — çünkü her tur uzayın yeni bir bölgesini yokluyor.

### 4.4 Mimarinin doğru olan yanları — bunlar korunmalı

Rapor dengeli olmalı; ölçüm şunları da söylüyor:

* **Grafik katmanı sağlam** (10/10 doğru tip, gerekçeli düşüş) — bkz. §2.
* **Sayıyı her zaman küp koyar; LLM SQL yazmaz.** Bu, sektörün *«silently wrong»* diye
  adlandırdığı en pahalı hata sınıfına karşı gerçek bir savunmadır.
* **Beyan kültürü** (*«sayı doğru ama eksik»*, *«bu bir varsayımdır»*) — rakiplerin
  çoğunda **yok**; sessizce tahmin ederler.
* **Kök-neden motoru** (`§KN`) formülü katalogdan okuyup log-uzayında ayrıştırıyor ve
  en dip alt-segmente iniyor. Bu, sektörde *«contribution / mix analysis»* denen şeyin
  doğru uygulanmış hâlidir ve çoğu üründe yalnız **zamansal** karşılığı vardır.
* **Kendi kendini denetleyen kapılar** — bu oturumda dört kez kendi teşhisim çürüdü ve
  dördünü de kapılar yakaladı (JOIN budaması · `F821` · yüzde toplama · zengin gövde).

*Kötü olan mimari değil, mimarinin ağırlığının dağılımı.*

---

# İKİNCİ KISIM — SEKTÖR

## 5 · SEKTÖR ÜÇ MİMARİ KAMPA AYRILDI

| kamp | LLM ne üretir | kim | ölçülen sonuç |
|---|---|---|---|
| **A · yapılandırılmış niyet nesnesi** (LLM **SQL yazmaz**) | arama token'ı / TML / `DataQuery` JSON | **ThoughtSpot**, **Google Looker**, dbt Semantic Layer, Qlik | en yüksek doğruluk; kapsam dışında **hata mesajı** |
| **B · semantik-model kısıtlı SQL** | SQL/DAX, doğrulayıcıdan geçerek | **Snowflake Cortex**, **Databricks Genie**, **Power BI Copilot**, Zenlytic | orta-yüksek; kapsam dışında **makul ama yanlış** |
| **C · ham şemaya serbest SQL/Python** | doğrudan SQL/Python | **Amazon Quick Sight (yeni)**, Julius AI, Hex geri-düşüşü | kurumsal şemada **%10 bandı** |

🔴 **DİMA A kampındadır** — ThoughtSpot ve Google ile aynı tarafta. ThoughtSpot bunu birebir
savunuyor: *«If relational search tokens are correct, **SQL is 100% accurate**»*. Google
`DataQuery` JSON üretir, SQL'i **Looker** derler.

⊙ **Ve bu tercihin bağımsız ölçümü var** (lkr.dev, 44 iş sorusu, 3 koşum):

| | Looker semantik katman | BigQuery doğrudan SQL |
|---|---|---|
| doğruluk | **%97** | **%80** |

**En öğretici kısmı:** Looker'ın 4 hatası **hiçbiri 3/3 koşumda** tekrarlamadı (gürültü).
BigQuery'nin **7 hatası 3/3 koşumda tekrarladı** — yani **sistematik**, prompt
iyileştirmesiyle kapanmaz.

*Bizim mimari tercihimiz sektörün kazanan tarafında. Sorun tercih değil, uygulama.*

## 6 · ON ÜÇ ÜRÜN — çapraz tablo

| ürün | LLM ne üretir | semantik katman | **yayınlanmış doğruluk** | belirsizlikte | grafik seçimi |
|---|---|---|---|---|---|
| **Snowflake Cortex** | SQL (6 ajan) | **zorunlu** | **%90+** (150 soru); BIRD **57→78** | 🟢 **reddeder** + öneri | yok (tüketiciye bırakır) |
| **Databricks Genie** | SQL (ajan topluluğu) | instructions + certified + Ontology | **%84,5** vs %52,4 — ⚠ **28 soru** | sorabilir, garanti yok | LLM; **düzenlenemez** |
| **ThoughtSpot** | **token/TML — SQL değil** | **zorunlu** | 🔴 **YOK** | token'ları gösterir | tip **korunur** |
| **Power BI Copilot** | DAX | semantik model | 🔴 **YOK** (bağımsız: **%62,5**) | 🔴 **sormaz**; kapsam dışında **LLM genel bilgisi** | LLM |
| **Tableau Pulse** | **yalnız cümle** | metrics layer | 🔴 YOK | — | **14 deterministik içgörü tipi** |
| **Looker CA** | **`DataQuery` JSON** | LookML | "**2/3 hata azalması**"; bağımsız **%97 vs %80** | 🟢 disambiguation (Mar 2026) | belgelenmemiş |
| **Amazon Quick** | **ham SQL (JOIN dâhil)** | Topics (≤12 veri seti) | 🔴 YOK | 🔴 sormaz | belgelenmemiş |
| **Qlik** | **hiçbir hesap — yalnız NLG** | Business Logic (ağır) | 🔴 YOK | 🔴 sormaz | **deterministik katalog** |
| **Sisense** | sorgu (**sonucu görmez**) | NLQ model | 🔴 YOK | 🟢 tıkla-ayrıştır UX | LLM, 10 tip |
| **Zenlytic** | **serbest SQL + sonradan doğrulama** | context layer | 🔴 YOK ("10x") | şartlı sorar | LLM |
| **Hex Magic** | SQL/Python + insan denetimi | dbt/Cube senk. | 🔴 YOK (eval altyapısı var) | 🟢 **en açık sorar** | 12 tip |
| **Julius AI** | Python | **yok** | ⚠ kaynaksız "%31" | sormaz | LLM |

### 6.1 Dört bulgu

**(a) 13 üründen yalnız ÜÇÜ doğruluk sayısı yayınlıyor.** Snowflake (%90+, 150 soru),
Databricks (%84,5, **28 soru** — ±13 puan güven aralığı), Google (dolaylı "2/3").
ThoughtSpot · Microsoft · Tableau · AWS · Qlik · Sisense · Zenlytic · Hex — **hiçbiri**.
⊙ *Ölçülmüş bir sayı yayınlamak, taklit değil öncülüktür.*

**(b) Microsoft'un en tehlikeli tasarım kararı, belgelenmiş hâliyle:**
> *«When a question is related to data in the semantic model, Copilot uses the semantic
> model… **Otherwise, it might answer from the large language model's (LLM's) general
> knowledge.**»*

Yani kapsam dışında **reddetmiyor, uyduruyor**. Uygulamacı eleştirisi birebir:
> *«**it doesn't tell you when it can't answer your actual question. It answers a
> different, easier question and presents it as if that's what you asked.**»*
> *«Copilot generated the DAX in 3 seconds. **It took me 45 minutes to fix what it got
> wrong.**»*

**(c) LLM-öncesi deterministik NLQ motorları PİYASA TARAFINDAN ÖLDÜRÜLDÜ.**
Tableau **Ask Data** → Şubat 2024'te emekli *(⚠ tek kaynaklı — bkz. §21.13)*. Power BI **Q&A** → **Aralık 2026'da
kalkıyor**, *«synonyms, linguistic relationships, row labels, teach Q&A»* dâhil **tüm
dilbilimsel şema araçları** ile birlikte.
🔴 **Bu bizi doğrudan ilgilendiriyor:** *«kullanıcı sözlüğü elle beslesin»* modeli iki dev
tarafından terk edildi. Bizim 9.468 satırlık Türkçe kural yığınımız o modelin bir
akrabasıdır.

**(d) Qlik'in dersi — mükemmel motor, kullanılmayan ürün.** Motoru determinizm açısından
kusursuz (*«all analytical calculations are still generated by the trusted Qlik engine»*),
ama Business Logic kurulum vergisi benimsemeyi öldürmüş. Kendi topluluğundan:
> *«I couldn't find **a single company that was using this resource** in their day-to-day»*
> *«Business logic is too complex… **no one want to waste time on it**»*

Forrester: BI'da elle kullanım **%20 tavanında**; doğal dilin katkısı **yalnız +10 puan**.

## 7 · ÖLÇÜLMÜŞ GERÇEK — text-to-SQL nerede

### 7.1 Benchmark çöküşü

| benchmark | SOTA | insan | not |
|---|---|---|---|
| **Spider 1.0** | %91,2 | — | "çözülmüş"; liderlik tablosu 2023'ten beri donmuş |
| **BIRD** | **%81,95** | **%92,96** | 11 puanlık açık **10 aydır kapanmıyor** |
| **Spider 2.0** (ajanik) | **%21,3** (o1-preview) · GPT-4o **%10,1** | — | şema **27 → 800 sütun** |
| **BEAVER** (MIT/Stonebraker) | **%10,8** | — | gerçek **özel** veri ambarı |
| **Archer** (muhakeme) | **%6,73** | — | aynı yöntem Spider'da %85,3 |
| **BIRD-INTERACT** (çok turlu) | GPT-5 **%8,67** (konuşma) / %17,00 (ajanik) | — | belirsizlik + çok tur eklenince çöküyor |

Stonebraker (CACM, Tem 2026): *«a pure LLM generated an accuracy score of **zero**. Adding
RAG, prompt engineering, and agentic AI raised accuracy to the **10+% range**.»*

⚠ **Ve bağımsız ölçüm liderlik tablolarını düşürüyor:** AIMultiple (Ağu 2026), 759 BIRD
sorusu, ipuçsuz, sıfır-atış → en iyi model **0,551**. Liderlik tablosu %82 ↔ gerçekçi ~%55.
Üstelik **BIRD gold sorgularının %31,1'i bozuk işaretlenmiş**.

### 7.2 Hata taksonomisi — ölçülmüş dağılım

4.602 hatalı SQL elle incelendi (~840 kişi-saat, arXiv 2501.09310):

| | BIRD | Spider |
|---|---|---|
| gerçek hata içeren sorgu | **%47,8** | %26,8 |
| **semantik hata** | **%36,1** | %17,7 |
| biçim hatası | %26,0 | %25,8 |

🔴 **Çalışma-zamanı çökmeleri hataların yalnız küçük dilimi** (%18,8 sözdizimi, %81,2 şema).
**Çoğunluk sessizce çalışıp yanlış sonuç veriyor.**

**LinkedIn üretim ölçümü** (arXiv 2507.14372): **derleme %96 · geçerli tablo&sütun %99 ·
DOĞRU %53.** Aradaki **~43 puan tanımı gereği sessizdir.**

### 7.3 «Çalıştı mı?» doğrulaması işe yaramıyor — AUROC 0,500

arXiv 2607.06799, selective-prediction çalışması:

| sinyal | AUROC |
|---|---|
| **query executability** | **0,500 — tam şans** |
| execution self-consistency | 0,613 |
| string self-consistency | 0,675 |
| GPT-4o hakem | 0,770 |
| **iki-sağlayıcılı hakem topluluğu** | **0,822** (ECE 0,031) |

🔴 **Bizim `dry_plan`'ımız da bu sınıftadır: sorgunun çalışması doğruluk hakkında SIFIR
bilgi taşır.** Ve self-consistency (bizim `k=3` oylamamız) tavanı ~0,675 — CHASE-SQL'in
ölçümü: oylama %68,84, **eğitilmiş seçici %73,01**, oracle tavanı **%82,79**.
⊙ *Darboğaz aday üretimi değil, **SEÇİM**.*

**Çekimserlik gerçeği:** %20 risk hedefinde self-consistency soruların yalnız **%1'ini**
geçirebiliyor; iki-sağlayıcılı topluluk %27. Ve **AbstentionBench**: muhakeme modelleri
çekimserlikte ortalama **%24 daha KÖTÜ**; ölçek büyütmek çekimserliği **iyileştirmiyor**.

### 7.4 Semantik katman — dört bağımsız ölçüm, aynı yön

| çalışma | ham şema | semantik katman | fark |
|---|---|---|---|
| Sequeda ve ark. (2023) | %16,7 | **%54,2** | 3,2× |
| Snowflake (BIRD alt kümesi) | %57 | **%78** | +21 |
| AtScale (2024) | %20 | **%92,5** | +72,5 |
| Cube.dev (2026, n=100, p<0,002) | %45,5–50,5 | **%67,7–68,7** | +17…+23 |
| dbt Labs (2026) | %84,1–90,0 | **%98,2–100,0** | +8…+16 |

**Cube'un en önemli cümlesi:** *«**Whether the model has the semantic layer matters more
than which model it is**»* — ve o kazanç **4 KB markdown**'dan geliyor.

**dbt'nin en önemli cümlesi:**
> *«With text-to-SQL, failure looks like **a plausible but incorrect answer**. With the
> Semantic Layer, failure looks like **an error message**.»*

⚠ **Ama semantik katman doğruluk değil, KAPSAM × doğruluk takası satıyor.** dbt'nin kendi
verisi: kapsam **içinde** SL %100 / T2SQL %50; kapsam **dışında** SL **%0** / T2SQL %100.
⊙ Bu tam olarak bizim *«dürüst red»* ↔ *«cevapsız %19,9»* gerilimimizin sektördeki adıdır.

### 7.5 Belirsizlik — sormak ölçülebilir biçimde kazanıyor

* **Kullanıcı sorularının %41,1'i belirsiz** (Microsoft/CIDR 2024, KaggleDBQA).
  İki insan anotatör arasındaki uyum bile yalnız **%62**.
* Belirsiz sorularda model recall **%27–31**, belirsiz olmayanlarda **%63–66** —
  **35 puanlık uçurum** (AMBROSIA).
* **Tüm meşru yorumları bulma (AllFound): GPT-4o %0,4 · Llama3-70B %1,9.**
  🔴 Modeller belirsizliğin **farkında bile değil**; tek yoruma kilitlenip kesin sunuyorlar.
* **AmbiSQL** (netleştirme soran sistem): **%42,5 → %92,5** (+50 puan, n=40).

Hacker News'ten, bizim doktrinimizin dışarıdan ifadesi:
> *«**the answer a business user needs is rarely the answer to the question they initially
> ask.** Asking for clarification, pushing back on poorly framed asks — **that's where most
> of the value comes from.** LLMs are still **too eager to jump into the code**.»*

## 8 · TÜRKÇE — ölçülmüş vergi ve ölçülmüş hendek

### 8.1 BIRDTurk (SIGTURK 2026, ODTÜ + Roketsan) — bizim için en önemli dış kanıt

BIRD'ün tamamı Türkçeye çevrildi (**12.751 soru, 95 DB**), **şema tanımlayıcıları da**
Türkçeleştirildi, çeviri doğruluğu **%98,15**.

| yöntem | BIRD (EN) | **BIRDTurk (TR)** | kayıp |
|---|---|---|---|
| doğrudan istem (ICL) | %58,21 | %43,16 | **−15,05 puan** |
| **DIN-SQL (ajanik)** | %60,89 | %49,02 | **−11,87 puan** |

🔴 **Türkçe 12-15 puan yakıyor — ve ajanik/yapılandırılmış muhakeme bu vergiyi ~3 puan
azaltıyor.** Yani **orkestratör yatırımımız hakemli bir yayınla doğrulanmış durumda.**

**Ölçülen üç mekanizma:** (1) SOV + mantığın **eklere dağılması**; (2) kelime sayısı
**−%27,3** → sözcüksel seyreklik; (3) tokenizasyon vergisi **+%9,3**.

⊙ **Ve teşhis cümlesi bizim için kritik:** *«İngilizce benchmark'larda **MASKELENEN**
muhakeme ve grounding başarısızlıklarını ortaya çıkarıyor»* — yani **Türkçe yeni hata
üretmiyor, İngilizcede gizlenen hataları görünür kılıyor.**

⚠ Fine-tuning ölçümü: mT5 ailesi Türkçede **%2'nin altında** (pratikte çalışmıyor);
Qwen2.5-Coder-3B **%15,38**.

### 8.2 Türkçe gerçek bir hendektir — rakiplerin ölçülmüş durumu

| ürün | Türkçe |
|---|---|
| **Gemini in Looker** | 🔴 *«supports **English-language prompts and responses only**»* |
| **Fabric Data Agents** | 🔴 *«İngilizce dışı dil desteklenmiyor»* |
| **Power BI Copilot** | 🔴 *«The only supported language is English»* |
| **Qlik Answers** | 🔴 yalnız İngilizce |
| **Tableau Agent** | ◐ Türkçe prompt kabul ediyor, **İngilizce cevap veriyor** |

⊙ **Türkçe morfoloji yatırımı savunulabilir bir konumdur** — ama §4.1'deki ters yatırım
uyarısıyla birlikte okunmalı: 9.468 satır **route'a**, 45 satır **garsona**.

## 9 · GRAFİK — rakiplerin «basit grafiği tutturması» nasıl oluyor

### 9.1 Kırk yıllık tek fikir

Mackinlay APT (1986) → **expressiveness** (ifade edilebilirlik: geçersiz kodlamaları
**ele**) + **effectiveness** (algısal etkinlik: kalanları **sırala**). Tableau *Show Me*
(2007) bunun ürünleşmiş hâli. ⊙ Rakiplerin *«sihri»* yayınlanmış literatürdür.

⚠ **Ama kural setlerini SAKLIYORLAR:** Amazon AutoGraph *«uses the most appropriate visual
type»* diyor, tabloyu vermiyor. Power BI quick-create *«automatically plots meaningful
charts»* — sıfır kural. SpotIQ ve Google Sheets Explore kapalı.
🟢 **Açık ve tam tek kural seti Draco'dur** (MIT) + Observable Plot kaynağı (ISC).

### 9.2 Draco'nun HARD kısıtları — bizim doğrudan kullanabileceğimiz «kırmızı çizgiler»

```prolog
hard(stack_without_summative_agg)  % yığınlama YALNIZ count/sum/distinct ile — avg/ratio YASAK
hard(bar_area_without_zero)        % bar/area ekseni sıfırdan başlamalı
hard(area_bar_with_log)            % log ölçekli bar/area — "often misleading"
hard(size_nominal)                 % nominal veride size kanalı (sıralama ima eder)
hard(size_negative)                % negatif veride size
hard(shape_with_cardinality_gt_eight)      % shape tavanı 8
hard(color_with_cardinality_gt_twenty)     % renk tavanı 20
```

🔴 **`stack_without_summative_agg` bizim bu oturumda yaptığımız hatanın tam panzehiri:**
`§KN-toplam`'ı kapısız yazınca **yüzdeleri topladım** ve *«ilk seferde tamam toplamının
%11,8'ini taşıyor»* diye anlamsız bir cümle üretti. Draco bunu **hard hata** sayıyor.
*Bizim ölçümle bulduğumuz kuralı, literatür 2018'de yazmış.*

**Algısal sıralama (Draco-APT, makine-okunur):**
```
nicel:   x/y (1) > size (2) > color (3)
nominal: x/y (1) > color (2) > shape (3) > size (4)
```

### 9.3 Klasik arıza modları ve engelleme mekanizmaları

| arıza | mekanizma |
|---|---|
| çok fazla kategori | `horizontal_scrolling` (ağırlık 20) |
| pasta >7 dilim | Draco pastayı **hiç desteklemiyor** (kasıtlı); renk tavanı 20, shape 8 |
| zaman serisi bar olarak | `temporal_y`: zamanı x'te tercih et; Plot: `isMonotonic(X)` → **line** |
| tek eksende karışık birim | Draco'da **dual-axis yok** — layer/facet kullan |
| **yüzdelerin toplanması** | **HARD hata** |
| kesik eksenli bar | **HARD hata** |
| kova patlaması | `bin_high` ≤12 + `bin_low` >7 → **hedef 8-12** |
| spagetti çizgi | Plot: `isHighCardinality(C)` (tekil oran >%50) → seri gruplaması **kapat** |
| **sıralama kararsızlığı** | Vega-Lite varsayılanı **alfabetik**; `sort` verilmezse veri değişince sıra oynar |

⊙ **Son satır bizim bu oturumda `§SB` ile ölçüp düzelttiğimiz kusurun ta kendisi.**

### 9.4 «Kullanıcı pasta istedi ama veri zaman serisi» — literatürün üç çözümü

1. **Draco/ASP:** kullanıcı isteği **soft**, veri uyumu **hard**. Çelişkide çözücü en yakın
   geçerli alternatifi üretir.
2. **CompassQL:** kısmi spesifikasyonu sabitle, kalanı say, çelişkide gevşet + cezalandır.
3. **Show Me:** uygun olmayan tipleri **gri** göster, en iyisini turuncu çerçevele.

🟢 **Bize önerilen:** #1 + #3 karması → *«Pasta çizemiyorum: seçilen alan bir tarih ve 24
farklı değer var (pasta tavanı 7); çizgi çizdim»* — **bir red değil, gerekçeli ikame.**
*Bu, «dürüst red başarı değil» kuralımızın grafik karşılığıdır.*

### 9.5 🔴 TÜRKÇE BİÇİMLENDİRME — ölçülmüş dört tuzak

Ajan bunları **Node/ICU ile fiilen koşturarak** doğruladı:

```
Intl.NumberFormat("tr-TR",{style:"percent"}).format(0.5555)   → "%56"      ← işaret ÖNDE, 0 ondalık
Intl.NumberFormat("en-US",{style:"percent"}).format(0.5555)   → "56%"
Intl.NumberFormat("tr-TR",{notation:"compact"}).format(12345) → "12 B"     ← B = BİN (10³)
Intl.NumberFormat("tr-TR",{notation:"compact"}).format(1234567890) → "1,2 Mr"
```

| tuzak | sonuç |
|---|---|
| **yüzde işareti Türkçede ÖNE gelir** | elle `değer + "%"` yazan her kod yanlış |
| **yüzde varsayılanı 0 ondalık** | `%55,55` sessizce `%56` olur — görünmez veri kaybı |
| **kompakt `B` = «bin»**, İngilizcede «billion» | `12 B` bir İngilizce okurda **12 milyar** |
| 🔴 **`d3-format`'ta `tr-TR` locale'i YOK** | 59 locale var, Türkçe **yok** → Vega-Lite/D3/Plot **varsayılan `en-US`**: `1,234.56` |

⊙ Bizim `app/sayi_bicimi.py`'miz bu oturumda tam da bu yüzden doğdu (beş ayrı
biçimlendirici bulunmuştu). Ama **ön-uç tarafı (ECharts/Vega) ölçülmedi** — açık borç.

> ⟳✅ **ÖN-UÇ BORCU KAPANDI — ÖLÇÜLDÜ (2026-08-12).** İki bölüm (`§9.5` · `§12.5`)
> *«ön-uç tarafı ölçülmedi, açık borç»* diyordu. Ölçüm:
>
> | soru | ölçüm |
> |---|---|
> | grafik kütüphanesi | **ECharts `^6.1.0`** — 4 dosya (`EChart.tsx`·`chart.ts`·`export.ts`·`KpiCard.tsx`) |
> | `d3` · `d3-format` · `vega` · `vega-lite` | ⊘ **HİÇBİRİ YOK** — ne bağımlılık ne import |
> | `Intl.NumberFormat("tr-TR")` | ✅ **2 dosya · 4 çağrı** (`lib/format.ts` · `KpiCard.tsx`) |
> | `toLocaleString` | ✅ **5 kullanım, 5'i de `"tr-TR"` açık** — varsayılan locale'e düşen **yok** |
>
> ⊘ **`d3-format`'ta `tr-TR` locale'i yok» tuzağı KONU DIŞI** — o kütüphane bu üründe
> kullanılmıyor. *Bir riski taşımayan bir mimariyi o riskle eleştirmek, çözdüğü sorunu
> göremeden onu değiştirmeye çalışmaktır.*
>
> 🔴 **AMA ÖLÇÜM BAŞKA BİR ŞEY BULDU — ve tam bu kartın uyardığı şey:** Türkçe sayı
> biçiminin **İKİ SAHİBİ** var. `src/lib/format.ts` (`fmtValue`/`fmtAxis`, **5 tüketici**)
> ve `src/components/KpiCard.tsx` — ve `KpiCard` `lib/format`'ı **içe almıyor**, kendi
> `Intl.NumberFormat("tr-TR", {maximumFractionDigits: 2})`'ini yazıyor. Bugün ikisi aynı
> sonucu veriyor; ayrılmaları için birinde `maximumFractionDigits` değişmesi yeter.
>
> ⏸ **KARAR: ŞİMDİ BİRLEŞTİRİLMİYOR, ŞARTIYLA.** `fmtValue(v, col)` bir **sütun** alıp
> birim çözüyor; `KpiCard`'ın çağrısında sütun **yok**. Yani birleştirme bir imza
> değişikliğidir, bir `import` değil — ve ön-uçta bu turda **kapı yok**, yani `KURAL B`
> ölçülemez. ⊘ Şart: ön-uç birim kapısı kurulduğu gün (`§9.5`'in kendi kalemi) bu
> ikizlik **aynı demette** kapatılır. *Bir kopyayı kapı olmadan birleştirmek, iki doğru
> yerine bir ölçülmemiş doğru bırakır.*


## 10 · KÖK-NEDEN — rakip algoritmalar ve bizim konumumuz

### 10.1 Önce ayrım: iki farklı soru

| soru | tip | algoritmalar |
|---|---|---|
| *«bu ZAMAN İÇİNDE neden değişti»* | değişim atfı | **Adtributor**, HotSpot, Squeeze/PSqueeze, iDice, **LMDI**, PVM |
| *«bu SEGMENT akranlarından neden farklı»* | kontrast | Key Influencers, Explain Data, **DIFF/MacroBase** (= Sisu), Scorpion |

🟢 **Bizde ikisi de var:** `contribution.py` (zamansal) + `kok_neden.py` (kesitsel).
Sektörde çoğu üründe **yalnız zamansal** karşılığı var.

### 10.2 Adtributor (NSDI 2014) — ve bizim eksik yarımız

**Explanatory power** `EP = (A−F)/(A_top−F_top)` + **Surprise** = Jensen-Shannon diverjansı.
Üretim eşikleri: `T_EP=%67`, `T_EEP=%10`, **top-3**. 128 gerçek anomalide **>%95 doğruluk**.

🔴 **Sürprizin neden şart olduğu — kurucu örnek (bizi doğrudan ilgilendirir):**
Gelir 100$→50$ düştü. *Veri Merkezi X* düşüşün **%94'ünü** açıklıyor (en özlü!). Ama X
zaten hem tahminin hem gerçeğin %94'ü — **dağılımı değişmedi**. Gerçek kök neden
**Mobile+Tablet** (tahminin %25'i → gerçeğin %0'ı).

> **«Yalnız explanatory power kullanan her katkı analizi, büyük segmentleri sistematik
> olarak suçlar.»** — bu, *«en büyük müşteri hep suçlu çıkıyor»* şikâyetinin matematiksel
> adıdır ve bizim `§KN-toplam`'ımız **tam olarak bu tuzaktadır**: en büyük segmenti seçiyor,
> sürpriz hesaplamıyor.

**Oran ölçüleri için Adtributor §4** — sonlu farklarla kısmi türev:
```
EP = [ (ΔA₁)·F₂ − (ΔA₂)·F₁ ] / [ F₂ · (F₂ + ΔA₂) ]
```
Sezgisel karşılığı: *«herkes tahmini yapsaydı, yalnız bu eleman gerçekleşen değerini
verseydi ne olurdu»* — bir **ceteris paribus karşı-olgusalı**.

### 10.3 Bizim `§KN`'nin sektördeki adı ve konumu

`kok_neden.py`'nin yaptığı `ln(v_hedef) − ln(v_akran) = Σ[ln(f_i,hedef) − ln(f_i,akran)]`
işleminin **üç ayrı literatürde üç adı var**:

| ad | alan | not |
|---|---|---|
| **LMDI** (Ang 2005, *Energy Policy*, **1.582 atıf**) | enerji/ekonometri | **fiili standart** |
| **PVM** (price-volume-mix variance) | FP&A | ⚠ **sıra bağımlı**, artık üretir |
| **log-uzayı çarpımsal ayrıştırma** | genel | bizim uyguladığımız |

🟢 **LMDI'nin dört özelliği bizim uygulamamızda zaten var:** artık **sıfır**, **sıra
bağımsız**, toplamsal↔çarpımsal tutarlı, zaman-tersinir.
⚠ **Eksik olan:** `LMDI-I` **alt-grup toplanabilirliği** (çok seviyeli drill-down'da
katkıların toplanması) ve **sıfır/negatif değer politikası** (`ln(0)` tanımsız; negatifte
LMDI tanımsız → Shapley'e geçilmeli).

### 10.4 🔴 Rakiplerin bizde OLMAYAN iki şeyi

**(a) Çok-boyutlu kombinasyon araması.** Adtributor **layer-1'de kilitli**; kök neden
`(İstanbul, Mobil)` gibi **bileşik** ise doğruluğu **sıfıra düşüyor**. **HotSpot** bunu
MCTS + *ripple effect* ile çözüyor: **vakaların %95'inde F-skor >%90** (Adtributor ve
iDice'ta **<%15**). Lokalizasyon >1 saat → **<20 saniye**.
⊙ **Bizim `§KN` de layer-1'de.** `derinles()` tek bir ikinci boyut açıyor, kombinasyon
araması yapmıyor.

**(b) «Dış kök neden» tespiti.** **PSqueeze** (JSS 2023) *«sorun bu boyutların hiçbirinde
değil»* diyebiliyor — F1 **0,90**. Literatürde ilk.
⊙ Bu, bizim *«§NB — açıklanamadı»* beyanımızın **ölçülebilir** hâlidir.

### 10.5 🔴🔴 EN CİDDİ UYARI — çoklu karşılaştırma problemi

Zgraggen, Zhao, Zeleznik, Kraska (Brown/MIT), **CHI 2018**:

> **«In our experiment, over 60% of user insights were false.»**

Mekanizma: analist ne kadar çok görselleştirme incelerse, **rastgele veride** ilginç
görünen örüntüye rastlama olasılığı o kadar artar.

🔴 **Bizim kök-neden motorumuz her soruda YÜZLERCE hipotezi sessizce test ediyor**
(`_en_ayristiran` aday süpürmesi, `derinles` kombinasyonları, `contribution` segment
taraması). **FDR düzeltmesi (Benjamini-Hochberg) veya keşif/doğrulama ayrımı YOK.**
⊙ Power BI'ın ham `p<0,05` Wald eşiği de bu düzeltmeyi yapmıyor — yani **sektör de
yapmıyor**, ama bu bizi haklı çıkarmaz.

*Düzeltme olmadan ürettiğimiz «kök nedenlerin» önemli bir kısmı gürültüdür.*

### 10.6 Rakiplerin belgelenmiş yöntemleri

**Power BI Key Influencers** (en şeffaf satıcı): **ML.NET** · kategorik hedefte **lojistik
regresyon**, sayısalda **doğrusal regresyon**, top segments'te **karar ağacı** · **Wald
testi, p<0,05** · Pearson/Point-Biserial doğrusallık testi → gerekirse **denetimli
binleme, en fazla 5 kova** · **en az 100 gözlem** · 10.000 örneklem.
⚠ Kısıt: DirectQuery **desteklenmiyor**, RLS ile çalışmıyor, TopN/ölçü filtrelerinde
**sessizce devre dışı**.

**Tableau Explain Data:** beklenen aralık = tahminlerin **15.–85. persentili**;
`SUM(X) = COUNT(X) × AVG(X)` **çarpımsal ayrıştırması**; sıralama *«complexity ↔
variability»* dengesiyle.
⚠ Kendi dokümanı: *«Correlation is not causation… **not a tool to prove or disprove
hypotheses**»*.

**Tableau Pulse — bizim için en iyi model:**
> *«starts by using **standardized, deterministic statistical models** to detect facts…
> These facts are used as **ground truths** to contextualize language generation.»*

**14 deterministik içgörü tipi** var ve **LLM yalnız cümleyi kuruyor**. AI kapatılsa bile
içgörüler erişilebilir kalıyor. ⊙ *Bu, bizim `§KN` + `anlatici` ayrımımızın olgun hâlidir.*

**Sisu Data'nın çekirdeği açık:** kurucusu Peter Bailis; temeli **MacroBase + DIFF
operatörü** (VLDB 2019). Varsayılanlar: `support ≥ 0,01`, `risk ratio ≥ 2,0`,
**MAX ORDER = 3**, minimality.

---

# ÜÇÜNCÜ KISIM — WREN'DE OLAN AMA KULLANMADIKLARIMIZ

## 11 · MOTORUN 15 YETENEĞİNDEN **BİRİNİ** KULLANIYORUZ

Ölçüldü (canlı konteynerde `dir(wren_core)`):

```
Manifest · ManifestExtractor · Model · RemoteFunction · RowLevelAccessControl ·
SessionContext · SessionProperty · cube_query_to_sql · is_backward_compatible ·
migrate_manifest_json · to_json_base64 · to_manifest · validate_rlac_rule · wren_core
```

**Bizim kullandığımız:** `from wren_core import cube_query_to_sql` — **tek sembol.**

### 11.1 Kullanmadıklarımız ve karşılığında kendimizin yazdıkları

| Wren'de VAR | ne yapar (kendi dokümanından) | biz ne yazdık | satır |
|---|---|---|---|
| 🔴 **`ManifestExtractor.extract_by`** | *«Given a used dataset list, **extract manifest by removing unused datasets**. If a model is related to another dataset, both datasets will be kept. **The relationship between them will be kept as well.**»* | — (hiç yok) | **0** |
| 🔴 `ManifestExtractor.resolve_used_table_names` | *«parse the given SQL and return the list of used table names»* | — | 0 |
| **`SessionContext.dry_run`** | *«Dry-run SQL (EXPLAIN) to validate without executing»* | `wren_service.dry_plan` sarmalayıcısı | ~40 |
| **`SessionContext.register_csv/parquet`** | veri kaydı | `dataset.py` | **161** |
| **`RowLevelAccessControl` + `validate_rlac_rule`** | satır düzeyi erişim | `rls.py` | **380** |
| **`Manifest` / `to_manifest` / `migrate_manifest_json` / `is_backward_compatible`** | manifest yükleme, **göç**, geriye dönük uyum | `compose.py` + `mdl_writer.py` | **1.490** |
| `SessionContext.get_available_functions` | motorun desteklediği fonksiyonlar | elle | — |
| `RemoteFunction` | özel fonksiyon | — | — |

🔴 **`ManifestExtractor.extract_by` = ŞEMA DARALTMA (schema linking).** §4.2'de *«garsona
her soruda 23.729 karakterin tamamı gidiyor»* diye ölçtüğüm boşluğun çözümü **motorun
içinde, kullanılmadan duruyor.** Ve araştırma diyor ki şema bağlama hatası:
kurumsal ölçekte SQL hatalarının **%27,6'sı** (Spider 2.0), MultiSpider 2.0'da **%33,0**.

### 11.2 MDL'de tanımlı olup kullanmadıklarımız

Canlı MDL (`demo/wren-project/target/mdl.json`):

| | adet | kullanıyor muyuz |
|---|---|---|
| `models` | **80** | ◐ dolaylı |
| **`relationships`** | **31** | ⟳ **F3 · BU SATIR YANLIŞTI — ölçüldü 2026-08-11.** *«cube_router'da sıfır anma»* doğru ama **kusur değil**: router ilişkiyi bilmemelidir (`§38.4` JOIN planlayıcı yasağı), sıradan bir boyut görür. İlişkiler **sekiz katmanda** kullanılıyor → aşağıdaki tablo |
| `views` | 1 | 🔴 hayır |
| `cubes` | 23 | ✅ evet |

⟳ ~~**31 tanımlı ilişki var ve çapraz-küp özelliğimiz onları kullanmıyor.**~~ — 🔴 **F3
ölçümü bu cümleyi çürüttü (2026-08-11).** *«blend, gerçek JOIN değil»* **doğrudur**, ama
gerçek JOIN başka bir yerde, **daha doğru bir yerde** yapılıyor: `blend` **iki ölçüyü**
harmanlar (`FULL OUTER JOIN` üstünde, paylaşılan grain zorunlu), ilişkiler ise **boyut
zenginleştirmesi** yapar. İkisi farklı işlerdir ve **ikisi de canlı**.

**Ölçülen sekiz katman:**

| # | katman | ne yapıyor | kanıt |
|---|---|---|---|
| 1 | **cube derleyicisi** — `compose._compose_relationship_dimensions` | `relationships.yml`'in **10 `expose:`** bloğu → **9 ilişki-türevi boyut**, **7 cube**'a enjekte (`oee` · `bakim` · `kalite` · `parti` · `mizan` · `makine_duruslari` · `surdurulebilirlik`) | `grep relationship demo/wren-project/cubes/*/metadata.yml` |
| 2 | **model katmanı** — `WrenEngine.dry_plan` | `is_calculated` kolon → **gerçek, çok-sıçramalı JOIN**, otomatik | `MIMARI §3.2` |
| 3 | **fan-out sertifikası** — `fanout.certify` | **31/31 ölçüldü**, hepsi `benzersiz=True · öksüz=0 · null=0 · saglikli` | `target/fanout_certificate.json` |
| 4 | `WrenService.schema()` | `dimension_origin[*].certified` damgası | kod |
| 5 | `drill.py:163` | `olculdu:riskli` kök-neden sırasında **geriye itilir** | `_SERTIFIKA_AGIRLIK` |
| 6 | `gorsel_ekleme` | soyağacı cümlesi — *«… ilişkisi üzerinden geldi (1 sıçrama)»* | canlı curl |
| 7 | `ossie.py` · `connections.py` | **ithal** ilişki `certified: "olculmedi"` damgalı gelir — sessiz *«sağlıklı»* değil | kod |
| 8 | ön uç — `InterpretationBar.tsx` | rozet | kod |

🔴 **Ve ölçüm BİR gerçek boşluk buldu — kapatıldı.** Soyağacı cümlesi *«…(1 sıçrama).»*
ile bitiyordu; `"certified" in yanıt` → **False**. Yani 31 ilişkinin tamamı ölçülmüştü,
sonuç bir artefakta yazılmıştı, damga şemaya basılmıştı — ve **kullanıcıya hiçbir yerden
ulaşmıyordu**. Okuyan kişi bir kolonun iki tablo öteden geldiğini görüyor, o join'in
toplamları **şişirip şişirmediğini bilemiyordu**.

> *Omni'nin `$55,5 milyar`lık kartezyen felaketi (`§23.1`) tam bu boşlukta doğdu — orada
> **ölçüm de yoktu**. Bizde **vardı ve susuyordu**; bu daha ucuz bir kusurdur ama daha
> sinsi olanıdır: sistem doğruyu biliyor ve söylemiyor.*

`fanout.beyan()` eklendi (rozet kodunun Türkçesi, **tek sahip** — `KAT-1`). Canlı cevap
artık: *«“bölüm” boyutu makineler.bolum kolonundan, oee_vardiya_makineler ilişkisi
üzerinden geldi (1 sıçrama) — **bu ilişki fan-out açısından ölçüldü, sayılar şişmiyor**.»*

### 11.3 🔴 Wren 7 Mayıs 2026'da mimarisini değiştirdi — biz yarım geçtik

* `Canner/wren-engine` **arşivlendi** (salt-okunur): *«merged into Canner/WrenAI under
  the `core/` directory»*.
* Yeni yapı: `core/` (Rust + `wren-core-py` + `wren-core-wasm`) · **`sdk/`**
  (`wren-langchain`, `wren-pydantic`) · **`skills/`** · **`evals/`**.
* Yeni boru hattı: `sqlglot → CTE rewriter → wren-core (Rust) → connector → PyArrow`.

**Bizim durumumuz:** `pyproject.toml` **doğru** tarafta (`wrenai>=0.13,<0.14` +
`wren-core-py>=0.7.3`).
🔴 **Ama kök `docker-compose.yml` hâlâ `ghcr.io/canner/wren-engine:latest` konteynerini
ayağa kaldırıyor** — **arşivlenmiş** bir depodan gelen, bir daha güncellenmeyecek imaj,
üstelik `latest` etiketiyle.
⊙ Ve bu oturumda ölçüldü: o konteyner **`Restarting (1)` durumunda** — yani zaten sağlıklı
çalışmıyor. *İki yol paralel koşuyor ve hangisinin canlı olduğu belirsiz.*

### 11.4 🔴🔴 EN AĞIR BULGU — Wren'in artık kendi `CubeQuery`'si var

`core/wren-core/core/src/mdl/cube.rs`:

```rust
pub struct CubeQuery {
    cube: String, measures: Vec<String>, dimensions: Vec<String>,
    time_dimensions: Vec<TimeDimensionFilter>, filters: Vec<CubeFilter>,
    limit: Option<usize>, offset: Option<usize>
}
```

`Granularity`: year|quarter|month|week|day|hour|minute
`FilterOperator`: eq, neq, in, not_in, gt, gte, lt, lte, contains, starts_with, is_null, is_not_null

**CLI:** `wren cube query --cube revenue --measures total --dimensions status
--time-dimension "order_date:month:2024-01-01,2025-01-01" --filter "status:eq:completed"`
— JSON girdi de alıyor, `--sql-only` ile dry-run.

Wren bunu belgesinde *«küçük modeller için **en yüksek kaldıraçlı doğruluk primitifi**»*
diye adlandırıyor.

⊙ **Bizim `CubeQuery`'miz ile aynı isim, neredeyse aynı şekil.** ~~`cube_router.py`'nin
**4.807 satırının** bir kısmı motorun artık kendi yaptığı işi ikinci kez yapıyor olabilir.~~

⟳ 🔴 **`§F2` — ÖLÇÜLDÜ (2026-08-11, motor `0.13.2`) VE KAYGI ÇÜRÜDÜ.** Yan yana kondu;
**beş vakanın DÖRDÜ bayt bayt aynı** — çünkü `WrenService.cube_sql` **zaten motoru
çağırıyor**:

```python
from wren_core import cube_query_to_sql
base = cube_query_to_sql(json.dumps(cq), self._mdl_bytes().decode())
```

Yani *«ikinci kez yapıyor»* yersizdi: SQL üretimi **zaten motorun**. Ve `cube_router`'ın
satırları SQL üretmiyor — **Türkçe NL → CubeQuery** çeviriyor, ki motor onu **hiç
yapmıyor**. İkisi farklı işlerdir.

🔴 **Ve ölçüm daha önemli bir şey buldu: MOTOR DESTEKLEMEDİĞİNİ SESSİZCE DÜŞÜRÜYOR.**
`cube_query_to_sql` reddetmiyor — alanı atıp SQL'i üretiyor:

| geçilen | motorun ürettiği | sonuç |
|---|---|---|
| `order` / `orderBy` | `ORDER BY` **yok** | *«en yüksek 5 müşteri»* → **rastgele** 5 |
| `having` | `HAVING` **yok** | *«10 milyon üzeri»* → eşik **hiç uygulanmaz** |
| `tarih in ["2026-01","2026-03"]` | `WHERE tarih IN ('2026-01','2026-03')` | DATE ↔ ay-metni → **sıfır satır** |

Üçü de **hatasız, uyarısız, `source="cube"` rozetiyle** yanlış sayı üretirdi — bu deponun
`sessiz_yanlış` diye avladığı sınıfın ta kendisi, ve **kaynağı motor**. Dolayısıyla
`cube_sql`'in `order`/`limit`/`measure_having`/`ayrik_aylar` sarmalayıcıları bir
**fazlalık değil bir korumadır**; gerekçeleri yazılıydı, artık **ölçülü** ve **kapılı**
(`tests/test_f2_motor_siniri.py`, 8 test). ⊙ **F5'in ön koşulu da budur:** motorda
*«zaten var»* sanılan bir yeteneği silmeden önce, motorun onu **sessizce düşürüp
düşürmediği** ölçülmelidir.

⚠ Ölçüm turunda bir **sahte kusur** doğdu ve düzeltildi: prob `order`'ı `[{id, desc}]`
şeklinde geçti, oysa şekil `{measure, direction}`. Canlı curl *«en yüksek cirolu 5
müşteri»* → **doğru azalan sıralı**. *Aracı, ürünü suçlamadan önce şüphelen.*

### 11.5 Wren'in **AI Context Layer**'ı — almadığımız asıl parça

Wren'in mimarisi **dört katman**: MDL semantik katman · **AI Context Layer** · Engine ·
Execution/UI.

**AI Context Layer'ın içeriği:**
* `instructions.md` — **iş bilgisi ve tanımlar** (versiyonlanmış)
* `queries.yml` — **örnek sorgular**
* **LanceDB yerel bellek indeksi** — **hibrit erişim** (retrieval)

🔴 **Biz Wren'in motorunu ve MDL'ini aldık; AI bağlam katmanını ALMADIK** — ve yerine
**9.468 satır Türkçe kural** yazdık.

Ve Wren'in kendi doğruluk çerçevesi altı sütun sayıyor: *schema linking · value profiling ·
**ambiguity detection** · generation trace · **retry/repair** · eval*. Belirsizlik tespiti
için yazdığı tek şey: **«Skill orchestration by the agent»** — yani **Wren de belirsizliği
motorda çözmüyor, ajana devrediyor.** ⊙ *Bu, garson devri kuralımızın bağımsız bir
doğrulamasıdır.*

**Ayrıca `wren serve mcp` OSS'te VAR** (`pip install 'wrenai[mcp]'`): `query_cube`,
`list_cubes`, `describe_cube`, `get_context`, **`recall_queries`** araçlarıyla. Wren'in
`oss_vs_commercial.md` tablosu *«MCP ❌»* diyor ama bu **hosted** MCP'yi kastediyor —
yerel MCP açık. Belge tutarsız, **bizim lehimize**.

---

## 12 · APTALLIK ETTİĞİMİZ YERLER — dürüst liste

Bu bölüm bir suçlama değil, bir **muhasebe**. Her madde ölçülmüştür.

### 12.1 🔴 Ters yatırım
**9.468 satır route'a (trafiğin %35,5'i), 45 satır garsonun istemine (trafiğin %37'si).**
Ve `CLAUDE.md`'nin **en üst kuralı** bunun tersini söylüyor: *«route'a Türkçe öğretmemiz
gerekir ki bu gereksiz… asıl **LLM'e** güveniyoruz»*. Kural doğru yazılmış, yatırım tersine
yapılmış. **271 `§` işareti** ve **130 muafiyet** bu terslığin faturasıdır.

### 12.2 🔴 Ölçülmeyen basamağa güvenmek
Trafiğin **%37'sini** taşıyan garsonun **otomatik doğruluk ölçümü yok**. Kapının kendi
yorumu: *«`garson` HİÇBİR TOPLU KOŞUMDA YOK»*. Elimizdeki tek şey **21 senaryoluk bir
kayıt kümesi** ve bir **kararlılık** ölçümü (1,0) — ⚠ *tutarlılık doğruluk değildir; aynı
cevabı üç kez vermek onu doğru yapmaz.*

### 12.3 🔴 Kapsam yanılsaması
Korpus **14.957 tur** gibi görünüyor; kendi raporunun ifadesiyle **şişme katsayısı 28,0×**
→ gerçek **590 semantik vaka**. *«Yeşil kapı»* 590 vakanın yeşilliğidir. Her 20'lik turun
4-5 yeni kök bulması bu yüzden **beklenen**dir.

### 12.4 🔴 Motorun içindekini yeniden yazmak
`rls.py` (380) ↔ `RowLevelAccessControl` · `dataset.py` (161) ↔ `register_csv/parquet` ·
`compose.py`+`mdl_writer.py` (1.490) ↔ `Manifest`/`to_manifest`/`migrate_manifest_json`.
Ve muhtemelen `cube_router.py`'nin bir kısmı ↔ `wren cube query`.
⊙ **Ölçülmeden iddia edilmiyor** — ama ölçülmesi gereken en pahalı kalem budur.

### 12.5 🔴 Bir sayının Türkçesini BEŞ yerde yazmak
Bu oturumda ölçüldü: `contribution._b3` · `interpret` ×6 · `prescribe` ×2 ·
`plan_tuketici._b` · `kok_neden._sayi`. Beşi de ayrışmıştı (`%83.4'i` ↔ `%83,4'ü`).
⚠ Ve **ön-uç tarafı hâlâ ölçülmedi**: `d3-format`'ta **`tr-TR` locale'i yok**.
> ⟳ **08-12: ölçüldü — `§9.5`'e bakın.** Özetle: `d3-format` **kullanılmıyor** (tuzak konu dışı), locale **her yerde açık `tr-TR`**, ama bu kartın uyardığı **ikizlik** ön-uçta **gerçekten var**: `lib/format.ts` ↔ `KpiCard.tsx`.

### 12.6 🔴 Ölçmeden koruma eklemek
`§KA`'nın kapısına iki kez daraltma koydum, ikisi de **düzeltmemi sessizce iptal etti**
(`not resp.suggestions` — netleştirme zaten `source=None` döner; `source == "cube+llm"` —
aynı soru sonraki koşumda Discovery'ye düştü). *Ölçmeden eklenen bir koruma, bir koruma
değil bir kör noktadır.*

### ✅ 12.7 — **KAPANDI (2026-08-11)** · ve teşhisin yarısı DÜZELTİLDİ

> ✅ **Değişim atfı tarafı kapandı** (`§E2`): `contribution` artık Jensen-Shannon
> sürprizini hesaplıyor ve *«en büyük kalemin payı değişmedi»* durumunu **beyan ediyor**.
> Kurucu örnek birebir sınandı; kapı `tests/test_e2_surpriz.py`.
>
> 🔴 **Ama `§KN-toplam` hakkındaki iddia YARI BAYAT — ölçüldü:** o yol bir **değişim**
> analizi değil, **tek dönemlik bir pay** ifadesidir (`satirlar = kos({...})`, `*_gecen`
> kolonu **yok**). Adtributor'ın eleştirisi `A ↔ F` gerektirir; orada `F` **yoktur**.
> Sürprizi oraya zorlamak, `§E2`'de bilerek reddettiğim şeyi yapmak — **taban uydurmak**
> — olurdu.
> ⊙ Ve modülün kendi cümlesi zaten doğru sınırı çiziyor: *«bir pay bir açıklama değil bir
> **konumdur**… "şu kadarını bu taşıyor" der, "bu yüzden" demez»*. Yani `§KN-toplam` en
> büyüğü **seçiyor** ama **suçlamıyor**.
>
> *Bir eleştiriyi doğru yere uygulamak, onu uygulamak kadar önemlidir.*

### 12.7 🔴 Sürprizsiz katkı analizi
`§KN-toplam` **en büyük segmenti** seçiyor, **Jensen-Shannon sürprizi hesaplamıyor**.
Adtributor'ın kurucu örneği bunun **yanlış cevap** ürettiğini gösteriyor: en çok açıklayan
ve en özlü aday, dağılımı değişmemişse **suçlu değildir**.
⊙ *«En büyük müşteri hep suçlu çıkıyor»* şikâyeti buradan doğar.

### 12.8 🔴 Çoklu karşılaştırma düzeltmesi yok
Kök-neden motoru soru başına **yüzlerce hipotez** tarıyor; FDR düzeltmesi **yok**.
Ölçülmüş bağlam: *«**kullanıcı içgörülerinin %60'ından fazlası yanlış**»* (CHI 2018).

### 12.9 ⚠ Arşivlenmiş imaja bağlı kalmak
`docker-compose.yml` → `ghcr.io/canner/wren-engine:latest`, depo **arşivli**, konteyner
**`Restarting`**.

### 12.10 ⚠ VQR'ı garsona bağlamamak
`vqr.py` **doğrulanmış soru deposu** — ama yalnız *replay* basamağında. Garsonun istemine
**örnek sorgu beslenmiyor**. Vanna AI'ın tüm tezi, Wren'in `queries.yml`'i ve Cube'un
+17-23 puanı tam olarak bu mekanizmadır.

### 12.11 ✅ Aptallık ETMEDİĞİMİZ bir yer — kayda değer
Gömme modeli seçimi **doğru**: `intfloat/multilingual-e5-large`, **TR-MTEB birincisi**
(mean 66,82 · retrieval 60,62). Yaygın tuzak olan `all-MiniLM`/`all-mpnet` ailesi Türkçe
retrieval'da **22-23** alıyor. *Bu tuzağa düşmemişiz ve `vqr.py`'deki yorum gerekçeyi
zaten yazmış.*

---

### 12.12 🔴🔴 ÖRÜNTÜ — **«YAZILMIŞ AMA BAĞLANMAMIŞ»**: beş kez ölçüldü

Bu raporun en tekrar eden bulgusu bir kusur değil, bir **desen**:

| # | yetenek | durum |
|---|---|---|
| 1 | `wren_core`'un **15 sembolü** | **1'i** kullanılıyor (`cube_query_to_sql`); `ManifestExtractor.extract_by` (**şema daraltma**) hiç çağrılmamış |
| 2 | `tools.py`'nin **25 aracı** | `agent_plan_secimi: off` · `mcp_yuzeyi: off` → **ikisi de kapalı** |
| 3 | `interpret.py`'nin **11 olgu üreticisi** | canlıda **1-2** ateşliyor |
| 4 | `plan_semasi`'nin **15 fiili** ↔ `tools.py` | **%73 örtüşüyor**, biri uykuda |
| 5 | ⟳✅ **`vqr.few_shot_block()`** | *(o günün ölçümü: yalnız Discovery'ye bağlıydı)* — 🔴 **BU SATIR BAYATTI, ⟳08-12 düzeltildi:** garsona **bağlandı** ve aynı belge bunu iki yerde yazıyor (`§0.6` satır 16 · `§38.1`). Ölçüm: `few_shot_block` çağrı yerleri **`vqr.py` 6 · `routers/ask.py` 4 · `features.py` 1** — Discovery'ye özel değil. *㊿ deseni: özet güncellendi, KAYNAK BÖLÜM güncellenmedi* |

⊙ **Toplam:** ürünün en pahalı yetenekleri **zaten yazılmış**; eksik olan **kablolama**.
Ve §16.4'ün *«açıkça boşa giden ~2.000 satır»* rakamı bu ışıkta **yeniden okunmalı**:
boşa giden kod değil, **bağlanmamış kod**.

🔴 **Bunun yönetsel anlamı:** §14'ün FAZ 1'i sanılandan **çok daha ucuz**. B2 bir
retrieval motoru yazmak değil, **var olan bir fonksiyonu bir yerden daha çağırmak**.

*Bir yeteneğin yokluğunu varsaymak, onu aramaktan pahalıdır — bu raporda beş kez ölçüldü.*

# DÖRDÜNCÜ KISIM — YARARLANABİLECEĞİMİZ AÇIK KAYNAK

> Her satır **LICENSE ham metninden** doğrulandı. GitHub'ın lisans etiketi birden çok kez
> yanlış çıktı. Yıldız/tarih `ungh.cc` · PyPI · npm · HuggingFace API'lerinden.

## 13 · ALINACAKLAR — öncelik sırasıyla

### 13.1 ⭐⭐ Apache Ossie — en stratejik bulgu

OSI (Open Semantic Interchange), Snowflake + Salesforce + dbt + Databricks + Cube +
AtScale + **ThoughtSpot** + Sigma tarafından Eylül 2025'te duyuruldu; **9 ay içinde Apache
Software Foundation'a girdi**. 1.824★, **Apache-2.0**.

İçinde: `core-spec/osi-schema.json` (11 KB JSON Schema) · `validation/validate.py` ·
hazır dönüştürücüler (dbt, snowflake, databricks, gooddata, honeydew, omni, polaris,
salesforce).

🔴 **Bizim için asıl kanca — `ai_context` alanı spec'in HER seviyesinde var:**
```yaml
- name: total_revenue
  ai_context:
    synonyms: ["ciro", "hasılat", "gelir", "satış tutarı"]
    examples: ["Bu yıl toplam ciro ne kadar"]
```

⊙ **Bu, tam olarak *«route'a Türkçe öğretilmez»* kuralımızın KABIDIR.** Türkçe sözlük
**koda değil semantik modele** ait olur. Ve **Wren zaten okuyor**:
`wren context build --from-osi semantic_model.yaml`.

**Bir günlük iş:** bir küpümüzü `ai_context.synonyms` ile Ossie YAML'ına çevir,
`ossie validate` ile doğrula. Türkçe sözlüğü koddan modele taşır **ve** Wren'e
kilitlenme riskini düşürür.

### 13.2 ⭐⭐ `shaido987/riskloc` — kök-neden algoritmaları tek depoda

139★, **MIT** (metin doğrulandı). Altı algoritma, ortak pandas arayüzü:

| dosya | satır | algoritma |
|---|---|---|
| `adtributor.py` | **43** | Adtributor (NSDI'14) |
| `rev_rec_adtributor.py` | 74 | R-Adtributor (özyinelemeli) |
| `hotspot.py` | 260 | HotSpot (MCTS + ripple effect) |
| `riskloc.py` | 215 | RiskLoc |
| `squeeze/squeeze.py` | 364 | Squeeze |
| `utils/element_scores.py` | ~70 | **EP + JS-surprise matematiği** |

🟢 **Karar: Adtributor'ı KENDİMİZ yazalım (~85 satır), `riskloc`'u doğrulama referansı
olarak yanımıza alalım.** `generate_dataset.py` ile sentetik regresyon korpusu üretilebilir.

⊙ **Bu, `kok_neden.py`'nin dikey (formül içi) ayrıştırmasının eksik YATAY kardeşidir** —
*«hangi segment kombinasyonu bu düşüşü açıklıyor»*. Mevcut cebirimizle **çakışmıyor**.

⚠ **Lisanssız kod uyarısı:** `wanghaao/ImpAPTr` ve `kapiya/Adtributor` **LICENSE
içermiyor** → varsayılan *«tüm hakları saklı»*, ticari üründe **kullanılamaz**.

### 13.3 ⭐ Metabase deseni — `candidates` + `agent_error`

Metabase belirsizlikte **red vermiyor, tahmin de etmiyor** — `400` ile **makine-okunur bir
nesne** döndürüyor ve *«LLM callers are expected to read the message and **self-correct on
the next turn**»* diyor:

```json
{"error":"ambiguous_measure","candidates":["satis.ciro","iade.ciro"],"agent_error":true}
```

🟢 Bu, *«dürüst red başarı değil»* (red değil, **eksiklik raporu**) **ve** *«şüphede
garson»* (mutfak seçmiyor, **sayıyor**) kurallarımızı **aynı anda** karşılıyor.
⊙ Bizde `test_cube_tie_clarification.py` ve belirsizlik chip'i **zaten var** — bu, o işin
olgunlaşmış hâli. Superset'in `get_compatible_metrics/_dimensions` ucu tamamlayıcı.

### 13.4 ⭐ Grafik: AVA CKB + CompassQL etkinlik tabloları

Ajan **Draco2'yi ve AntV AVA'yı yerelde kurup ölçtü** — ikisi de elendi:

* **Draco 2:** bizim tam senaryomuz (1 ölçü + 1 zaman boyutu, 24 satır) → **çizgi değil
  `point`** önerdi (`point 12` · `bar 16` · `line 32`). Sebep: Draco'da **`temporal` scale
  tipi yok**, datetime `linear`'a düşüyor, zaman serisi *«sürekli×sürekli»* sayılıyor.
  Ayrıca `pip install draco` **Python 3.12'mizde kırılıyor** (metadata `<3.12`), ~72-150 ms
  clingo maliyeti, pie/treemap/gauge taksonomisi yok.
* **AntV AVA:** `computeScore` **çarpımsal**; `bar-series-qty` ağırlığı 0,5 olduğu için
  **sütun grafikleri 0,5 tavanının üstüne yapısal olarak çıkamıyor**. Ölçüm: *«1 ölçü +
  kardinalite 5 nominal»* → 1. öneri **`rose_chart` (4,32)**, sütun 0,5'te. `npm i @antv/ava`
  = **257 MB / 227 paket**. v4 **LLM zorunlu** hâle gelmiş.

🟢 **Önerilen bileşim (hiçbirini bağımlılık almadan):** AVA'nın `ckb/base.js`'indeki
**51 grafik tipi + `dataPres` şeması + `purpose` alanı**nı YAML'e port et (MIT) →
**CompassQL'in `effectiveness/` tablolarıyla sırala** (BSD-3; ve bunlar Draco'nun aksine
zaman serisini **doğru** yapıyor: `Q × TIMEUNIT_T` agregalı → `line: 0, area: −0.1,
bar: −0.2`) → Observable Plot'un **`isMonotonic(X)`** sezgisini al → çıktıyı **Vega-Lite
spec'i** olarak ver.

⚠ **Kalibrasyon:** `viz.py`'miz **zaten 731 satır** ve Cleveland-McGill gerekçeleriyle
yazılmış; canlı ölçümde **10/10 doğru tip** verdi. **Değiştirmeye gerek yok** — Draco'nun
**hard kısıtları** (§9.2) mevcut kurallarımızın *ilkesel türevi* olarak eklenmeli, AVA'nın
`purpose` alanı (Trend/Comparison/Rank/Proportion) ise **niyet nesnemize doğal bir kanca**.

### 13.5 ⭐ Değerlendirme — dört fikir

| kaynak | fikir | bizdeki karşılığı |
|---|---|---|
| **test-suite-sql-eval** (Apache-2.0, EMNLP 2020) | **damıtılmış çoklu mini veri seti**: `yil = 2026` ile `yil > 2025` tek DB'de aynı sonucu verir; **birden çok mini DB'de** ayrışır | 🔴 yok — *«15 gizli kırmızı, 2'si gerçek kusur»* ölçümümüzün panzehiri |
| **Dr.Spider** (Apache-2.0, ICLR 2023) | 17 pertürbasyon; **robustness gap** = `acc(orijinal) − acc(bozulmuş)` | 🔴 yok — `göre/bazında/bazlı` üçlü aşırı-yüklemesi bizi **üç kez** ısırdı, çünkü **ölçülmüyor** |
| **AmbiQT** (MIT, EMNLP 2023) | altın cevap **KÜME**dir; 4. belirsizlik tipi **precomputed aggregates** = bizim küp belirsizliğimiz | 🔴 yok — belirsiz senaryoda tekil `gold` **paydayı kirletir** |
| **EHRSQL** (CC-BY-4.0, NeurIPS 2022) | **reliability score**: kapsam-içine red **ağır negatif**, kapsam-dışına red **pozitif**, kapsam-dışına uydurma **en ağır negatif** | 🟢 *«dürüst red başarı değil»* doktrinimizin **matematiksel formu** — tek başına bir CI kapısı olabilir |

**Araç tarafı:** `syrupy` (MIT, **sıfır bağımlılık**) + `pytest-regressions` (MIT) snapshot
için · `promptfoo` (**saf MIT**, 24.1K★) **yalnız garson** için · `inspect_ai` (MIT)
alternatif.
❌ **Elenenler:** `phoenix` (**Elastic License 2.0**), `ragas` (durgun + org değişti),
`uptrain` (**ölü**, 2024-05).

⚠ **Kalibrasyon:** `eval/run.py`'miz **zaten selective prediction** uyguluyor
(coverage + answered-precision) ve `test_eval_gate.py` baseline ratchet'i var — listedeki
çoğu araçtan **olgun**. Eksik olan: snapshot katmanı, kategori kırılımı ve **standart hata**
(Inspect AI'ın `stderr`'i — *«20 senaryoluk paydada %85 ile %90 arasındaki fark gürültü
mü?»* sorusunun tek cevabı; **«payda kutsaldır»** ilkemizin doğal tamamlayıcısı).

### 13.6 Türkçe NLP — ölçülmüş kararlar

| araç | karar | gerekçe |
|---|---|---|
| **Snowball Türkçe** (BSD-3, 34,4M indirme/ay) | 🟢 **gölge ölçümde dene** | sıfır bağımlılık, mikrosaniye. ⚠ *«stems only **noun and nominal** verb suffixes»* → `arttı`yı **çözmez**, ama `satışlarımızın`/`cirodaki`/`bazında` tam kapsamda |
| **Zeyrek** (MIT) | 🔴 **RED** | `analyze('benim')` → **dört** parse; **disambiguation YOK**. Deterministik router için *«N aday lemma»* çözüm değil, **dördüncü bir belirsizlik katmanı**. §G/AJ0'daki *«arttı» bir FİİL* teşhisini **çözmezdi** |
| **Zemberek** (Apache-2.0) | ◐ **sözlüğü** al, kodu alma | README: *«slow maintenance mode»*, son sürüm **2019**, Maven Central'da **yok**. ~130k köklü sözlük değerli |
| **stanza** (Apache-2.0) | ◐ **laboratuvarda** | Türkçe lemma **%98,9** (Atis/Tourism — bizim alanımıza yakın) ama `torch` + **~500 ms**. Karşılaştırılabilir tek Türkçe NLIDB projesi Stanza'yı ölçüp **kendi regex'iyle değiştirmiş** (<10 ms) — bizimle **aynı mimari karar** |
| **VNLP** · **UDPipe 2** | 🔴 lisans engeli | AGPL-3.0 · modeller **CC BY-NC-SA** |
| **`ytu-ce-cosmos/modernbert-tr-reranker`** | ⟳ ~~⭐ **ÖLÇ**~~ → 🔴 **ÖLÇÜLDÜ, RED** *(2026-08-11, `F4`)* | ~~cross-encoder, **+5…+9 nDCG@10**; şema sütun sayımız küçük → maliyet kabul edilebilir. *Muhtemelen en yüksek getirili tek ekleme*~~ — **ön kabul çürüdü:** darboğaz sıralama değil **sahiplik**. 506 yanlış-cube vakasının tamamı *«iki küp de meşru sahip»* sınıfında; reranker bunu **daha iyi tahmin ederek** çözer, yani **beyan edilebilir bir belirsizliği sessiz bir seçime çevirir**. ⊙ Bu satırdaki `stanza` kararının (`torch` + ~500 ms → laboratuvara) **birebir aynı gerekçesi** buraya da uygulanır; tutarlılık için burada da uygulandı. Doğru iş: `§SH` sahiplik kararlarını doğru katmana taşımak |

**Türkçe NL→SQL veri setleri (bilinmiyordu — üç tane var):**
**TURSpider** (8.659+1.034, insan çevirisi, HF kopyası **CC BY 4.0**) · **TUR2SQL**
(10.809, ⚠ lisans belirsiz) · **BIRDTurk** (10.962, ACL Anthology).

### 13.7 Elenen ama not düşülmesi gerekenler

| proje | neden |
|---|---|
| **Chat2DB** (27.9K★) | ⚠ `LicenseRef-Chat2DB` — harici ürün/OEM/white-label **yazılı izin olmadan yasak**. **Açık kaynak değil** |
| **Vanna AI** (23.8K★, MIT) | son commit **2 Şubat 2026** — altı aydır sessiz. RLS/çok-kiracılılık **deseni** için okunmalı, bağımlılık alınmamalı |
| **DataLine** · **Steampipe** | GPL-3.0 / AGPL-3.0 — copyleft |
| **sqlcoder** · **Dataherald** | ☠️ 2024'ten beri ölü |
| **XiYan-SQL** alt projeleri | ⭐ **M-Schema** (LLM-dostu şema temsili) ve **XiYan-DBDescGen** (otomatik DB açıklaması) — MDL zenginleştirme için doğrudan ilgili |
| **LangChain SQL** | v1.x'te SQL QA öğreticisi **kaldırıldı**; toolkit *legacy* |
| **SHAP** · **PyRCA** · **EconML** · **Kats** · **Merlion** | kategori hatası / ölü / arşivli |
| **`ruptures`** (BSD-2) · **`statsforecast`** (Apache-2.0) | 🟢 *«mart'ta düştü»* iddiasını doğrulamak ve Adtributor'ın istediği `F` (baseline) için |

---

---

### 13.8 Tamamlayıcı taramalar — elenenler ve neden

Raporun bütünlüğü için, incelenip **alınmayan** kalemler de kayda geçiyor. *Bir
araştırmanın değeri, reddettiklerinin gerekçesi kadardır.*

| kalem | lisans / durum | karar ve gerekçe |
|---|---|---|
| **Malloy** (Google/Meta kökenli) | Apache-2.0 · **2,5K★** · 5.227 commit · 9 SQL motoru | ◐ **İncele, alma.** Semantik modelleme **dili** — bizim MDL'imizin rakibi, tamamlayıcısı değil. ⚠ README'de **üretime hazırlık veya bakım taahhüdü beyanı YOK**. Findly'nin onu derleyici doğrulaması için kullanması (§23.6) **desen olarak** öğretici |
| **Lightdash** | MIT · dbt üstü BI | 🔴 **Alma.** dbt'ye sıkı bağlı; bizim MDL/Wren zeminimizle **çakışıyor**. ⊙ Yalnız *«metrik katmanını BI'ın kaynağı yapmak»* deseni için okunur |
| **Evidence.dev** | MIT · kod-tabanlı BI (markdown + SQL) | 🔴 **Alma.** Hedef kitlesi **analist/geliştirici**; bizim iş kullanıcısı hedefimizle örtüşmüyor. ⊙ Ama *«rapor = versiyonlanmış markdown»* fikri **belge/canvas** tarafımız için ilham |
| **Rill Developer** | Apache-2.0 · DuckDB üstü hızlı BI | ◐ **İzle.** ⊙ Tek gerçek dersi §27'de: **projelerin %50+'ı ajan tarafından kuruluyor** — *«ajan yüzeyi dağıtım kanalıdır»* tezinin kanıtı |
| **Voyager 2** (UW IDL) | 1,5K★ · **CompassQL'in referans uygulaması** | ◐ **Kaynak olarak oku, bağımlılık alma.** *«Kısmi spesifikasyon + wildcard + ilgili görünümler»* deseni, §9.4'teki *«kullanıcı pasta istedi ama veri zaman serisi»* çözümünün canlı örneği. ⚠ Depo kendi başlığında **React/Redux göçünün alfa sürümü** olduğunu yazıyor — kararlı değil |
| **DoWhy** (Microsoft/PyWhy) | MIT · nedensel çıkarım | 🔴 **Şimdilik alma — ama kategoriyi kayda geç.** §35'in ölçtüğü boşluk tam burada: BI'ın *«kök neden»* dediği şey **korelasyonel ayrıştırma**; gerçek nedensel iddia **DoWhy/EconML sınıfı** bir araç + **nedensel grafik beyanı** ister. ⊙ Bizde böyle bir beyan **yok** ve uydurmak `GG8`'i çiğner. *Bu, «karar motoru» iddiasının önündeki asıl bilimsel engeldir.* |
| **Explanation Tables** (Gebaly ve ark., VLDB 2014) | akademik | ◐ **Oku.** Adtributor'ın kardeşi: bir ikili sonucu açıklayan **kompakt, örtüşmeyen kural kümesi** üretir. §10.4'teki *«bileşik segment»* boşluğunun ikinci bir çözüm ailesi; HotSpot'un MCTS'ine göre **daha yorumlanabilir**, daha az kapsayıcı |
| **SHAP · PyRCA · EconML · Kats · Merlion** | — | 🔴 kategori hatası / ölü / arşivli (§13.7) |
| **`ruptures`** (BSD-2) · **`statsforecast`** (Apache-2.0) | canlı | 🟢 **Al.** *«Mart'ta düştü»* iddiasını **doğrulamak** ve Adtributor'ın istediği `F` (baseline/forecast) için. §16'nın *«sürpriz hesaplanmıyor»* eksiğinin ön koşulu |

⊙ **Örüntü:** elenen her kalem ya **bizim zaten sahip olduğumuz bir katmanın rakibi**
(Malloy, Lightdash), ya **farklı bir kullanıcı için** (Evidence), ya da **bir iddiayı
bilimsel olarak taşıyamayacağımızı gösteriyor** (DoWhy). Üçü de **bilgi**.

# BEŞİNCİ KISIM — BOŞA MI GİTTİ

> ⚠ Bu bölüm **batık maliyet yanılgısına** karşı yazıldı. Ölçüt tek: *«bu varlık bugün
> silinse, yerine ne koymak gerekirdi ve kaça mal olurdu?»* Duygusal bağ, harcanan emek
> ve *«bu kadar yazdık»* bir gerekçe **değildir**.

## 16 · VARLIK MUHASEBESİ — dosya başına yönetici değerlendirmesi

### 16.1 🟢 KORUNACAK — silinse yeniden yapılması ZORUNLU ve PAHALI

| varlık | büyüklük | neden değerli | dış kanıt |
|---|---|---|---|
| **`demo/packs/*` — semantik katman** (23 küp · 80 model · 31 ilişki · 4 şirket) | pack YAML'ları | 🔴 **Ürünün asıl hendeği bu.** Cube'un ölçümü: semantik katman **+17…+23 puan** ve *«hangi model olduğu değil, semantik katmanın olup olmadığı belirleyici»* | Cube arXiv 2604.25149 · dbt · AtScale · Sequeda |
| **`kok_neden.py`** (1.111) | 1.111 satır | LMDI'nin (Ang 2005, 1.582 atıf) doğru uygulanmış hâli; **artık sıfır, sıra bağımsız**. Rakiplerin çoğunda yalnız **zamansal** karşılığı var | Ang, *Energy Policy* · Tableau Explain Data |
| **`viz.py`** (731) | 731 satır | Canlı ölçüm **10/10 doğru tip**; Cleveland-McGill gerekçeleriyle yazılmış | §2 ölçümü · Draco/CompassQL kıyası |
| **`uyum.py` + beyan kültürü** (2.055) | 2.055 satır | dbt'nin cümlesi: *«semantik katmanda başarısızlık bir **hata mesajıdır**»*. Power BI kapsam dışında **uyduruyor** — biz **söylüyoruz** | dbt 2026 · MS Learn |
| **`vqr.py` + `multilingual-e5-large`** | — | TR-MTEB **birincisi** (66,82); yaygın tuzak `all-MiniLM` Türkçede **22-23** | TR-MTEB, EMNLP 2025 |
| **Kapılar** (`test_modul_buyume`, `test_alan_haritasi`, altın testler) | — | Bu oturumda **dört** gerçek kusuru yakaladı: JOIN budaması bozulması · `F821` NameError · yüzde toplama · zengin gövde kaybı. **Hiçbirini ben görmedim** | §15.1 |
| **Belgeler** (52.147 satır) | 36 belge | Kurumsal hafıza; bu raporun kendisi o hafıza sayesinde **ölçülebildi** (şişme katsayısı, cevapsız oranı, `§` sayımı) | — |

⊙ **Bu sütun boşa gitmedi.** Silinse yeniden yapılması aylar alır ve bir kısmı (packs)
**müşteri başına** yeniden yapılır.

### 16.2 🟡 KISMEN BOŞA — değeri var ama **yanlış orana** yatırıldı

> ⟳⚠ **`§` SAYISI YAYIMLANABİLİR BİR ÖLÇÜM DEĞİLDİR — desenle değişiyor.** Bu belge iki
> yerde **131** ve **271** yazıyor; iki bağımsız denetim **279** ve **379** ölçtü; benim
> ölçümüm desene göre **164** (`§X`), **110** (backtick'li), **83** (çıplak).
>
> 🔴 Beşi de *«doğru»* — çünkü hepsi **farklı bir şey** sayıyor. *Birimi tanımlanmamış
> bir sayı, bir ölçüm değil bir izlenimdir.* Bu satırın taşıması gereken şey bir sayı
> değil, **sayma yöntemi**dir; yöntemi olmayan sayı buradan çıkarılmalıdır.

| varlık | büyüklük | dürüst yargı |
|---|---|---|
| **`cube_router.py` + Türkçe kural yığını** | **9.468 satır** | 🟡 **Yarısı değerli, yarısı yanlış katmanda.** Değerli yanı: trafiğin **%35,5'ini** **sıfır LLM maliyetiyle** ve **%89-98 doğru küple** cevaplıyor — bu gerçek bir maliyet ve gecikme avantajı. Yanlış yanı: aynı iş **garsona bir örnek sorgu listesi vererek** (Cube: **4 KB markdown → +17…+23 puan**) çok daha ucuza yapılabilirdi. Ve dayandığı ürün modeli (*«kullanıcı dilbilimsel şemayı elle beslesin»*) **Microsoft Aralık 2026'da, Tableau Şubat 2024'te kaldırdı** |
| **410 test dosyası · 71.534 satır** | uygulamanın **1,24 katı** | 🟡 **Kalitesi yüksek, nişangâhı yanlış.** Ürünün **%35,5'ini** ölçüyor; **%37'sini taşıyan garsonun otomatik ölçümü yok**. Testler kötü değil — **eksik yere bakıyorlar** |
| **271 `§` işareti · 130 muafiyet** | — | 🟡 **Her biri gerekçeli, toplamı bir borç.** On binlerce hücrelik bir uzayda 131 hücre kapatılmış. Kusur bulma oranı **düşmüyor** (~5 senaryoda 1) — bu, yöntemin ölçeklenmediğinin kanıtı |

⊙ **Buradaki kayıp «yapılan iş» değil, «yapılmayan iş».** 9.468 satır yazılırken garsona
örnek sorgu bağlanmadı, şema daraltma açılmadı, ölçüm kurulmadı.

### 16.3 🔴 BOŞA GİTTİ — açıkça, savunmasız

> ⟳🔴 **BU BÖLÜMÜN *«BOŞA GİTTİ»* RAKAMI ÇÜRÜK — ve çürüten ölçüm bu belgenin
> **kendi §40.2**'sinde yazılı.** Ölçüldü (2026-08-12): `rls.py` *«hiç kullanılmadı»*
> değil — `wren_service.py:20` onu içe aktarıyor ve **11 çağrı yeri** var; `dataset.py`
> ile `register_csv` **farklı işler** yapıyor. Kapı: `tests/test_f5_bosa_giden_kod.py`.
>
> ⊙ *Aynı belgede iki farklı gerçek koşuyorsa, okuyan hangisine güveneceğini bilemez.*

| varlık | büyüklük | neden boşa |
|---|---|---|
| **`rls.py`** | **380 satır** | `wren_core.RowLevelAccessControl` + `validate_rlac_rule` **motorun içinde duruyor**, hiç kullanılmadı |
| **`dataset.py`** | **161 satır** | `SessionContext.register_csv` / `register_parquet` **var** |
| **`compose.py` + `mdl_writer.py`'nin manifest kısmı** | **1.490 satırın bir bölümü** | `Manifest` · `to_manifest` · `migrate_manifest_json` · `is_backward_compatible` **var** |
| **Korpusun şişme katsayısı** | — | **590 semantik vaka**, 14.957 tur gibi raporlandı. Bu bir kod kaybı değil bir **karar kaybı**: yeşil sayıya bakıp *«iyiyiz»* denildi |
| **`ghcr.io/canner/wren-engine:latest` bağımlılığı** | — | Depo **arşivli**, konteyner **`Restarting`**. İki yol paralel koşuyor |

**Toplam açıkça boşa giden kod: ~2.000 satır** (53.725'in **%3,7'si**).

⊙ **Bu, korkulandan çok daha küçük bir rakam.** Asıl kayıp silinecek kodda değil,
**ölçülmeyen basamakta geçen zamanda**.

### 16.4 Sayısal özet — objektif

| kategori | satır | pay |
|---|---|---|
| 🟢 korunacak (packs · kök-neden · viz · uyum · vqr · kapılar · belgeler) | ~**115.000** | **%68** |
| 🟡 kısmen boşa (route yığını · yanlış nişanlı testler) | ~**52.000** | **%31** |
| 🔴 açıkça boşa (motorda olanı yeniden yazmak) | ~**2.000** | **%1** |

### 16.5 🔴 ASIL KAYIP — koda yazılmayan

Boşa giden şey **satır** değil, **sıra**:

1. **Ölçüm önce kurulmadı.** Garson korpusu ilk gün kurulsaydı, 9.468 satırlık route
   yığınının hangi kısmının gereksiz olduğu **ölçülebilirdi**. Bugün bilinmiyor.
2. **Motorun yüzeyi taranmadı.** `dir(wren_core)` bir komut; **15 sembolden 14'ünün**
   varlığı bu rapora kadar fark edilmedi.
3. **Kusur bulma hızına bakılmadı.** ~5 senaryoda 1 kök oranı **26 tur boyunca** sabit
   kaldı ve bu bir **yöntem sinyali** olarak okunmadı; her tur *«bir kök daha kapattık»*
   diye okundu.

*Bir yöntemin ölçeklenmediğini gösteren sayı, ilk turda da vardı; okunmadı.*

### 16.6 Dürüst cevap: **hayır, boşa gitmedi — ama ucuz da olmadı**

**Boşa gitmedi**, çünkü:
* Semantik katman, kök-neden cebiri, beyan kültürü ve grafik katmanı **sektörün doğru
  tarafında** ve bağımsız ölçümlerle desteklenmiş kararlar.
* Mimari kamp seçimi (**A kampı**) ThoughtSpot ve Google ile aynı; lkr.dev ölçümü
  **%97 ↔ %80**.
* Türkçe yatırımı **gerçek bir hendek**: Looker · Power BI · Fabric · Qlik **resmen
  yalnız İngilizce**.

**Ucuz olmadı**, çünkü:
* **%31'lik bir dilim yanlış orana yatırıldı** ve bunun ölçüsü ancak bugün çıkarıldı.
* **~2.000 satır** motorun içinde zaten olan şeyi yeniden yazdı.
* En pahalısı: **trafiğin %37'si 26 tur boyunca ölçülmeden geliştirildi.**

*Batık maliyet, geçmişte harcanan emek değil; o emeğe bakarak bugün yanlış karar
vermektir. Yukarıdaki tablo tam da bunu önlemek için sayı ile yazıldı.*


---

# ALTINCI KISIM — AGENTIC DURUMUMUZ

## 17 · AGENTIC DURUMUMUZ — ölçüldü, ve sanılandan farklı

### 17.1 🔴 İKİ PARALEL AGENTIC SİSTEMİMİZ VAR; ZENGİN OLANI KAPALI

> ⟳ **BAYRAK AÇILDI (`§D13`, 2026-08-12):** `demo/packs/features.yml` → `mcp_yuzeyi: beta`.
> Aşağıdaki *«MCP ucu 404 dönüyor»* satırı artık **yalnız `agent_plan_secimi` için**
> doğrudur. Canlı: `GET /mcp/tools` → **200 · 31 araç · yazma aracı SIFIR**.
> ⚠ Araç sayısı da bayat: **25 → 31** (`§D6` altı ilkeli kayda soktu).

| | canlı yol | araç yolu |
|---|---|---|
| dosyalar | `plan_semasi` · `plan_garson` · `plan_tuketici` · `plan_kosucu` | `tools.py` · `planner.py` · `mcp.py` · `routers/mcp.py` |
| **satır** | **3.288** | **1.448** |
| yüzey | **15 kapalı fiil** (`enum`, plan *«icat edemez»*) | **25 zengin araç** (erişim · ne zaman · **ne zaman KULLANILMAZ** · determinizm · maliyet · makbuz) |
| sınır | `AZAMI_ADIM = 12` | `Butce(adim=3, saniye=10.0, **sorgu=0**)` |
| durum | ✅ **canlı** | 🔴 **`agent_plan_secimi: "off"`** · 🔴 **`mcp_yuzeyi: "off"`** |

⊙ **1.448 satırlık araç altyapısı iki kapalı bayrağın arkasında uyuyor** — ve MCP ucu
`404` dönüyor. Kullanıcının *«MCP'leri var»* dediği şeyin **bizde de yazılmış hâli var**,
yalnız **açık değil**.

### 17.2 Araç tanımlarımız aslında sektör standardının üstünde

Örnek (`contribution.decompose`):

> *«[Erişim: iki dönemin sonuçları] [Ne zaman: 'neden değişti' sorusunda, kırılım
> BELLİYKEN] **[NE ZAMAN KULLANILMAZ: toplanamayan (ortalama/oran) ölçüde — katkı
> MATEMATİKSEL OLARAK tanımsızdır]** [determinizm=deterministik · maliyet=ucuz ·
> makbuz=ContractLog]»*

🟢 **Negatif yönerge (*«ne zaman kullanılmaz»*) araç tasarımının en zor ve en atlanan
parçasıdır** ve 25 aracın **hepsinde** var. Ayrıca her araç **erişim sınırını**
(*«ham veri YOK»*), **maliyetini** ve **makbuzunu** beyan ediyor.

⊙ Yani *«agentic'imiz zayıf»* teşhisi **yarı yanlış**: yüzey iyi tasarlanmış, **bağlı
değil**.

### 17.3 Gerçek eksikler

| eksik | ölçüm | sonucu |
|---|---|---|
| **Kapalı fiil kümesi** | 15 fiil, `enum` ile kilitli | Kullanıcının istediği *«ne derse ona göre şekil alan»* davranış **yapısal olarak** mümkün değil. ⚠ Ama bu bilinçli bir karar: `plan_semasi`'nin kendi yorumu *«plan denetlenebilir kalır **ancak** fiilleri sonluysa»* |
| **Alt-ajan / iş bölümü yok** | — | Orkestratör **düz bir adım listesi** koşuyor; dallanma, paralel kol, kendi kendine görev bölme yok |
| **Kendini düzeltme döngüsü yok** | `plan_garson`'da **tek** *«DÜZELTME TURU»*; `llm.py`'deki yeniden denemeler yalnız **boş yanıt** için | Bir adım patlarsa hata modele geri verilmiyor |
| **Yazma araçları kapalı** | `_yazma_araclari` bilerek `llm_araclari` dışında | *«Panoya ekle»*, *«her pazartesi yolla»* **yapılamıyor** — ve bu **agentic'in asıl kilidi** |
| **Araç yolu ile plan yolu ayrık** | 25 araç ↔ 15 fiil, birbirini görmüyor | Aynı işin **iki tarifi** var; biri canlı, biri uykuda |

### 17.4 ⚠ Ama «kapalı fiil kümesi» bir kusur mu — sektör ne diyor

Bu, raporun en dikkatli olması gereken yeri. Anthropic'in kendi rehberi **iş akışlarını
(workflow) ajanlara tercih etmeyi** öneriyor; bileşik hata (`%95^10 ≈ %60`) çok adımlı
otonom ajanların ölçülmüş zaafı. Ve Gartner: *«**agentic analitik projelerinin %60'ı
2028'e kadar başarısız olacak**»*.

⊙ **Yani kapalı fiil kümesi savunulabilir bir mimari karardır** — kusur onda değil,
**esnekliğin hiç ölçülmemiş olmasında**: bugün *«15 fiil hangi soruların yüzde kaçını
ifade edemiyor»* sorusunun cevabı **yok**.

*Bir kısıtı savunmak için, onun neyi dışarıda bıraktığını sayabilmek gerekir.*

### 17.5 🔴 «İki paralel sistem saçma değil mi?» — ölçüldü, **evet**, ve birleşmeli

> ⟳✅ **BU BÖLÜMÜN TAMAMI KAPANDI (`§D6`, 2026-08-12).** Aşağıdaki *«%73 örtüşme»*,
> *«ironi: `plan_semasi` ilkeyi kendi fiil kümesine uygulamamış»* ve *«önerilen:
> `FIIL_ANLAMI` türetilsin»* üçü de **artık geçersiz**:
>
> · Her araç kendi fiilini **beyan ediyor** (`tools.Arac.fiil`) → örtüşme **15/15 = %100**
>   (eksik denen dördü de kayıtta: `sirala` · `matris` · `pano.taslak` · `contribution.akran`)
> · `plan_semasi._fiilleri_kayittan_dogrula()` **içe aktarma anında** koşuyor; ayrışma
>   varsa uygulama **ayağa kalkmıyor**
> · Ve `§17.6`'nın *«`C1` acil kusur düzeltmesi değil»* notu bu yüzden **ters yönde** bayat

**Doğum tarihleri hikâyeyi anlatıyor:**

| sistem | ilk commit | felsefesi |
|---|---|---|
| `tools.py` + `planner.py` (**araç kaydı**) | **2026-08-02** (`ee411d0`) | *«Dima'nın ~15 yeteneği zaten yazılı; eksik olan onların **tipli, denetlenebilir, yetkiye bağlı birer araç olarak BEYAN EDİLMESİYDİ**»* |
| `plan_semasi.py` + `plan_garson.py` (**kapalı fiil**) | **2026-08-09** (`548a5cd`) | *«Serbest plan **yasak**… bir plan denetlenebilir kalır **ancak** fiilleri sonluysa»* |

⊙ **Yedi gün arayla, aynı soruya iki cevap.** İkincisi canlıya alındı, birincisi
**silinmedi** — iki bayrağın arkasında bırakıldı.

**Örtüşme ölçüldü: 15 fiilin 11'inin araç ikizi var (%73).**

```
SORGU → route/cube_sql      TREND    → yoy.compute            SIRALA   → —
KIR   → drill.expand        BAGLA    → bagla                  MATRIS   → —
SUZ   → drill.select        HESAPLA  → hesapla                PANO     → —
BOYUTSEC → contribution.report   AYRISTIR → contribution.decompose   KIYASLA → —
RAPOR → report.compose      ANLAT    → llm.anlat
GORSEL → viz.recommend
```

### 🔴 Ve ironi, `plan_semasi`'nin **kendi docstring'inde** yazılı

O dosya `cube_query` şemasını **kopyalamayı reddediyor**:

> *«🔴 `cube_query` ŞEMASI YENİDEN YAZILMIYOR — **ÇAĞRILIYOR**. İkinci bir kopya yazmak,
> katalog değişince **birinin bayatlaması** demekti — bu deponun `KAT-1` sınıfı.
> *Bir şemayı iki yerde tanımlamak, iki farklı katalogla koşmaya razı olmaktır.*»*

⊙ **Aynı dosya, bir sonraki satırda, tüm yetenek listesini kopyalıyor.** İlkeyi
`cube_query` için uygulayıp **fiil kümesi için uygulamamış.**

### Birleşme tasarımı — ikisi de haklı, ikisi de korunabilir

İki felsefe **çelişmiyor**; farklı katmanlarda doğru:

| katman | doğru sahip | neden |
|---|---|---|
| **yetenek kaydı** (ne yapabiliriz, hangi izinle, hangi maliyetle, hangi makbuzla, **ne zaman kullanılmaz**) | 🟢 **`tools.py`** | Zaten `authorize()`'a bağlı, determinizm/maliyet/makbuz beyanı var, **MCP çevirisi bedava** |
| **plan dilbilgisi** (bir adım nasıl yazılır, referanslar, tip denetimi, `AZAMI_ADIM`) | 🟢 **`plan_semasi`** | `dogrula()` koşmadan tip denetliyor; `GIRDI_TIPI`/`CIKTI_TIPI` gerçek bir katkı |

**Önerilen:** `plan_semasi.FIIL_ANLAMI` **elle yazılmayı bırakır, `tools.py`'den TÜRETİLİR**
(plan-bestelenebilir araçlar süzülerek). Kapalı `enum` **korunur** — yalnız artık
**üretilmiş** olur.

**Bu birleşme aynı anda dört şeyi çözer:**
1. `KAT-1` — tek yetenek listesi; biri bayatlayamaz.
2. **Yetki süzgeci plana bedava gelir** — bugün plan fiilleri `authorize()` görmüyor.
3. **MCP yüzeyi plan yolunu da kapsar** — `mcp_yuzeyi` açıldığında aynı kayıttan.
4. **Ölçülebilir esneklik** — *«15 fiil hangi soruların yüzde kaçını ifade edemiyor»*
   sorusu, kayıt tek olduğunda **sayılabilir** hâle gelir.

⚠ **Ne birleşMEmeli:** `plan_kosucu` (çalıştırma) ve `plan_tuketici` (cevaba çevirme)
ayrı sorumluluklardır ve ayrı kalmalıdır. Birleşecek olan **yalnız yetenek beyanıdır**.

⚠ **Risk ve kural:** bu canlı yolda bir yeniden düzenlemedir → `KURAL B` zorunlu
(bayrak kapalıyken **bayt bayt** aynı davranış) ve türetilmiş `enum`'un bugünkü 15 fiille
**birebir aynı** çıktığı bir kapıyla kilitlenmeli.

*Bir ilkeyi bir satırda uygulayıp bir sonrakinde unutmak, ilkeyi hiç yazmamaktan daha
pahalıdır — çünkü artık uygulandığı sanılır.*

### ✅ 17.6 — **TEŞHİS BAYAT ÇIKTI (ölçüldü 2026-08-11)** · plan AYRIŞIYOR

> `A13` maddesi *«planın neden ayrışmadığını ölç, C1/C2'den ÖNCE — yoksa yanlış şeyi
> düzeltiriz»* diyordu. Ölçüm yapıldı (`/stats/plan`, planlayıcı-tetikleyen 10 soru):
>
> | | `§17.6` (rapor) | **bugün** |
> |---|---|---|
> | tek adım | **%60** (12/20) | **5/24 = %21** |
> | çok adım | %40 | **19/24 = %79** |
> | ortalama adım | — | **3,3** (79/24) |
> | düşen plan | — | **0** |
>
> 🔴 **Üç hipotezin ÜÇÜ DE çürüdü:** ① istem ayrıştırmayı engellemiyor (%79 çok adımlı)
> ② deterministik-önce kapısı erken kapanmıyor (10 soruda **24** planlayıcı çağrısı)
> ③ `tek_adimli` kısayolu kural hâline gelmemiş (%21).
>
> ⚠ **Örneklem farkı dürüstçe:** rapor **kütükteki 20 kayıtlı planı** (üretim karışımı)
> saymıştı; bu ölçüm planlayıcıyı **bilerek tetikleyen** 10 soruyla yapıldı. Yani ortak
> soru *«planlayıcı koştuğunda ayrıştırıyor mu»*dur ve cevabı **evet**. Üretim
> karışımındaki oran ayrı bir ölçüm ister (`A1`'in konusu).
>
> ⊙ **Sonuç:** `C1` (fiil listesini `tools.py`'den türetme) bir **acil kusur düzeltmesi
> değil**; raporun kendi notu da onu `C3`'ten önceye bağlıyor ve *«kullanıcı hiçbir şey
> hissetmiyor (`KURAL B` gereği davranış aynı kalacak)»* diyor. Ölçüm bu sıralamayı
> **doğruluyor**.

### 17.6 🔴 Asıl sorun 15 fiil değil — **plan neredeyse hiç ayrışmıyor**

> ⟳🔴 **BU BÖLÜM YÜRÜRLÜKTE DEĞİL — aynı numarayı taşıyan İKİ `§17.6` var.** Yukarıdaki
> (`✅ 17.6`, satır ~1487) bu bölümün üç hipotezini **ölçüp çürüttü** (plan %79 çok
> adımlı). Bu bölüm **kayıt için** duruyor (`MIMARI §10`: kapananlar işaretlenir,
> silinmez) ve *«hiçbiri henüz ölçülmedi»* cümlesi **bayattır**.
>
> ⊙ *İki bölüm aynı numarayı taşıyorsa, hangisinin yürürlükte olduğu yazılmadıkça
> okuyan yanlışını seçer.*

Kütükten ölçüldü (kayıtlı 20 plan):

| plan uzunluğu | adet | pay |
|---|---|---|
| **1 adım** | **12** | **%60** |
| 2 adım | 2 | %10 |
| 3 adım | 2 | %10 |
| 4 adım | 3 | %15 |
| 7 adım | 1 | %5 |
| **8-12 adım** | **0** | **%0** |

⊙ **`AZAMI_ADIM = 12` tavanı hiç bağlayıcı olmamış** — gözlenen en uzun plan **7**, ve
planların **%60'ı tek adımlık**, yani orkestratör **hiç orkestre etmiyor**.

🔴 **Bu, teşhisi tersine çeviriyor.** *«15 fiil yetmiyor»* demek için önce fiillerin
kullanılıyor olması gerekir; ölçüm **kullanılmadığını** söylüyor. Sorun **ifade gücü**
değil, **ayrıştırma isteği**: planlayıcı çok adımlı bir çözüm **kurmaya çalışmıyor**.

**Üç olası kök (hiçbiri henüz ölçülmedi, ayırt edilebilir):**
1. **İstem ayrıştırmayı teşvik etmiyor** — plan istemi *«mümkünse tek adım»* yönünde bir
   baskı taşıyor olabilir.
2. **Deterministik-önce kapısı çok erken kapanıyor** — `route()` bir cevap verince plan
   yolu hiç denenmiyor; trafiğin %35,5'i zaten böyle.
3. **Tek adımlık plan bir «başarı» sayılıyor** — `plan_semasi.tek_adimli` bilinçli bir
   kısayol; ama ölçüm onu **kural** hâline getirmiş olabilir.

⚠ **Ve bu, birleşme kararını daha da güçlendiriyor:** yetenek kaydı tek olsaydı,
*«planlayıcı hangi araçları hiç seçmiyor»* sorusu **bir sorgu** olurdu. Bugün 15 fiilin
kaçının canlıda hiç kullanılmadığını **bilmiyoruz**.

### 17.7 Karar motoru — dar ama ilkeli

`prescribe.py`'nin kendi gerekçesi, sektörün *«prescriptive analytics»* iddialarına karşı
alınmış bilinçli bir pozisyon:

> *«Bir "karar matrisi" kolayca uydurulur: seçenekler × kriterler × ağırlıklar tablosu
> **her zaman bir sayı üretir**. Ama o sayıların **ölçülmüş bir zemini yoksa** ürün,
> kanıtlanabilir bir BI aracından **kanaat üreten** bir araca dönüşür.»*

Ve kural: **yalnız veriden ya da BEYANDAN gelen boyutlar** kullanılır, uydurma ağırlık yok.

⊙ Kullanıcının *«karar motoru olmalı»* isteğiyle bu ilke **çelişmiyor** — ama bugünkü
`prescribe` bir *«nereye bak»* işaretçisi, bir *«ne yap»* motoru değil. Aradaki mesafe
**kasıtlı**; genişletilecekse **beyan edilmiş** bir zeminle genişletilmeli.

## 18 · «ROBOTİK / KATALOG GİBİ» — ölçüldü

Sekiz farklı soru türü, canlı:

| soru | viz | satır | not (karakter) | olgu | **chip** |
|---|---|---|---|---|---|
| «bu yıl toplam ciro» | `kpi` | 1 | **0** | 1 | **6** |
| «makine bazında oee» | `bar` | 11 | 117 | 2 | **6** |
| «fire oranı neden yüksek» | `pivot` | **1000** | 718 | 1 | **5** |
| «geçen yıla göre nasıl gidiyoruz» | `kpi` | 1 | 112 | 2 | **6** |
| «en kötü 3 makineyi analiz et» | `cumle` | 3 | 560 | 2 | **6** |
| «kalite durumunu özetle» | `kpi` | 1 | 117 | 2 | **4** |
| «hangi müşteri riskli» | `table` | 5 | **0** | 2 | **6** |
| «üretim raporu hazırla» | — | 0 | 21 | 0 | 3 |

**Dört ölçülmüş kusur:**

1. 🔴 **Chip sayısı neredeyse sabit: 6,6,5,6,6,4,6,3** *(⟳08-12: **6,6,6,6,5,6,6,5**)*. Soru ne olursa olsun aynı boyda
   bir öneri şeridi. *Katalog hissinin birinci kaynağı budur* — mobilya her cevapta aynı.
2. 🔴 **Olgu sayısı hep 1-2.** Cevabın **derinliği soruya göre değişmiyor**. Tableau
   Pulse'un **14 içgörü tipi** üretip duruma göre seçmesiyle kıyaslanınca fark buradan
   doğuyor.
3. 🔴 **Hiçbir cevap birden çok grafik taşımıyor** (belge yolu dışında). *«Hem analiz et
   hem birkaç grafik göster»* isteği **yapısal olarak** karşılanamıyor.
4. 🔴 **İki cevapta sıfır metin** (*«toplam ciro»*, *«hangi müşteri riskli»*) — ikisi de
   tam olarak bir cümlenin en çok gerektiği yerler.

⚠ Ve *«fire oranı neden yüksek»* → **1000 satırlık pivot**: bir *«neden»* sorusuna
**döküm** ile cevap. `§RK-2` bunu *«özet değil»* diye işaretliyor (dürüst), ama kullanıcı
için sonuç yine bir duvar.

### 18.1 Kök: cevap biçimi bir KARAR DEĞİL, bir YAN ÜRÜN

Bugün cevabın şekli şu üçünün **artığı** olarak oluşuyor: `viz.analyze()` grafik tipini
seçiyor · `interpret()` 1-2 olgu üretiyor · `_attach_next_steps` chip'leri dolduruyor.
**Hiçbir yerde *«bu soru ne tür bir cevap ister»* diye soran bir basamak yok.**

> ⟳🔴 **ÇÜRÜDÜ (denetim ajanı buldu, 2026-08-12'de ÖLÇEREK doğrulandı).** O basamak
> **var**: `app/bicim.py` (6.132 bayt, `niyet.TUR_*` × beş kova karar tablosu) ve
> **tüketiliyor** — `answer.py:864` `from app.bicim import oneri_kotasi`, bayrak
> `bicim_karari: beta` (**açık**). Yani *«sinyal var, tüketicisi yok»* cümlesi bugünkü
> kodu tarif etmiyor; `§18.2`'nin dört bileşenlik haritası bu **beşinci** bileşeni hiç
> görmüyor ve o yüzden *«dördü birbirini görmüyor»* de bayat.
>
> ⊙ *Bir teşhis, teşhis ettiği eksik kapandıktan sonra silinmezse, kapanmış bir işi
> açık gösterir.*

Oysa niyet nesnemiz (`niyet.py`) bunu **zaten biliyor**: `TUR_TOPLAM` · `TUR_KIRILIM` ·
`TUR_TREND` · `TUR_KIYAS` · `TUR_LISTE` · `TUR_USTUNLUK`, ve `followup` beş konuşma türü

> ⟳ **«beş» BAYAT (ölçüldü 2026-08-12):** `followup.py` **sekiz** tür taşıyor —
> `TUR_NEDEN` · `TUR_NORMAL` · `TUR_NE_YAPMALI` · `TUR_ISARET` · `TUR_ANLAT` ·
> `TUR_TAKIP` · `TUR_PAYLAS` · `TUR_MAKBUZ`.
tanıyor. ⊙ **Sinyal var, tüketicisi yok.**

*Bir sistemin robotik görünmesi, karar vermemesinden değil, kararı hiç vermemiş
olmasından gelir.*

---

### 18.2 KOD HARİTASI — biçim tam olarak nerede karara bağlanıyor

Ölçüldü (kaynak okuma):

| bileşen | yer | ne belirliyor |
|---|---|---|
| grafik tipi | `viz.analyze()` (`viz.py:132`) + `recommend()` | `kind` |
| **olgular** | `interpret.py` — **11 `facts.append` çağrı yeri**, ⟳ ama **14 AYRI TİP** (2026-08-12 `ast` ile sayıldı) | anlatının içeriği |
| chip'ler | `answer._attach_next_steps()` (`answer.py:838`) → `drill.next_steps` | öneri şeridi |
| anlatı | `anlatici.anlat()` + `llm.anlat` + `narration_guard` | cümle |

🔴 **Dördü birbirini görmüyor.** Hiçbiri *«bu soru ne tür bir cevap ister»* diye sormuyor;
her biri kendi girdisine bakıp kendi parçasını üretiyor. **Cevabın şekli bu dördünün
ARTIĞI.**

### 18.3 🟢 Ve iyi haber: taksonomi KISMEN ZATEN YAZILMIŞ

⟳ **ÖLÇÜLDÜ (2026-08-12) — VE BU BÖLÜMÜN SAYISI YANLIŞ BİRİMDEYDİ.**

`ast` ile sayıldı: **11 `facts.append` çağrı yeri**, ama **14 AYRI TİP**:

    bottom · count · delta · kiyas · kpi_components · kpi_value · measures
    peak · segment_delta · shape · single · streak · top · trend

⊙ Yani *«Pulse'un **14 tipi** ile aramızdaki mesafe»* diye yazılan cümle **çağrı yerini
tipe** kıyaslıyordu. Tip ekseninde mesafe **yok**: bugün de 14. Bir çağrı yeri birden çok
tip üretebiliyor (`_kpi_facts` → `kpi_value`+`kpi_components`; `_streak` ayrı bir üretici).

> *İki sayıyı kıyaslamadan önce birimlerinin aynı olduğunu ölçmek gerekir; yoksa kıyas
> bir mesafe değil bir kur farkı üretir.*

🟢 **Canlı ölçüm (curl, 2026-08-12) raporun ÖTEKİ yarısını DOĞRULADI:**

| soru | olgu | tipler |
|---|---|---|
| *«bu yıl aylık ciro trendi»* | **3** | `trend` · `peak` · `delta` |
| *«makine bazında ortalama oee bu yıl»* | **2** | `top` · `bottom` |

Yani gerçek mesafe **2-3 → 14**: tipler var, **koşulları ateşlenmiyor**.

⏸ **KARAR — sayaç PARK:** *«her çağrı yerine sayaç koy, 100 soruda koş»* bir **ölçüm
tesisatıdır**, ürün değil (kullanıcı kuralı). Değerinin çoğu zaten yukarıda **statik +
canlı** olarak alındı. Tesisat, `A1` kaseti 21→50'ye büyüdüğünde **bedava** gelir: o
korpus zaten tam `/ask` yolundan koşuyor.

🔴 **VE ÖLÇÜM ARARKEN GERÇEK BİR KUSUR ÇIKTI** (aşağıda `§D11-b`) — *bir sayıyı doğrulamak,
onu üreten yolu okumayı gerektirir; ve o yolda kural yazılıydı ama koşmuyordu.*

*Bir yeteneğin yokluğunu varsaymak, onu aramaktan pahalıdır — bu raporda üçüncü kez.*

### 18.4 🔴🔴 `§D11-b` — YAZILI KURAL KOŞMUYORDU; ONU İKİ **KAZA** AYAKTA TUTUYORDU

Olgu üreticilerini okurken çıktı (2026-08-12). `anlatici.basit_mi`'nin son şartı şunu
**yazıyor**:

> *«Tek ölçü şartı: iki ölçüyü tek cümlede anlatmak, aralarında bir **ilişki** ima eder
> (*«ciro arttı, fire düştü»* → bir neden-sonuç okunur). O çıkarım bu basamağın yetkisinde
> değil.»*

Ölçüm — iki ölçülü **gerçek** bir `interpret` çıktısıyla:

    olculer = {'toplam_ciro'}   →   len(olculer) <= 1   →   True   (kural GEÇTİ)

⊙ Çünkü `interpret` olguları yalnız `measures[0]` için üretir; **ikinci ölçünün adı hiçbir
olguda geçmez**. Yazılı şart **her zaman** geçiyordu.

**Kuralı fiilen uygulayan iki kaza vardı — ve ikisi de bu kuralı bilmiyordu:**

| # | kaza | kırılganlığı |
|---|---|---|
| ① | `len(olgular) > _AZAMI_OLGU` | iki ölçüde olgu **5**, tavan **4** → tavan 5 olsa ölür |
| ② | `measures` tipi `TANINAN`da yok | kapsam kapısı onu *«bilinen istisna»* diye kaydetmiş — yani **eklenmeye davetiye** |

⚠ Ve `test_d1_anlatici_kapsami.py::test_COK_OLCULU_KIYAS_hala_LLM_e_gider` **yeşildi** —
doğru sonucu ölçüyordu, doğru **sebebi** değil.

> *Bir kuralın yazılı sahibi onu uygulamıyorsa, kural yoktur; yalnız onu şu an tesadüfen
> karşılayan bir yan etki vardır.*

✅ **DÜZELTİLDİ:** `interpret` artık `olcu_sayisi`ni **kaynağından** taşıyor (ek anahtar;
`facts`/`summary` tüketicileri etkilenmez) ve `basit_mi` kuralı ondan okuyor; taşımayan
eski sözlükler için geri düşüş korundu (`KURAL B`).

✅ **KAPI** `tests/test_d11_olcu_sarti_gercekten_kosuyor.py` (7 vaka) — ve asıl testi
**kazaları kaldırarak** ölçüyor: tavan 9'a çıkarılır, `measures` tanınanlara eklenir,
kural **yine** tutmalıdır. *Bir değişmezi, onu şu an ayakta tutan tesadüflerle birlikte
ölçmek, tesadüfü değişmez sanmaktır.*

### 18.5 🔴 TEK KALEMDE ÜSTÜNLÜK — *«aynı soru, aynı sayı, iki farklı cümle»*

Canlı ölçüm (curl ×3, 2026-08-12), *«pompa arızası kaç kere oldu»*:

| koşum | `dimensions` | özet |
|---|---|---|
| 1, 2 | `["ariza_tipi"]` | *«**En yüksek arıza tipi**: pompa arızası (26 adet).»* |
| 3 | — | *«Arıza sayısı 26 adet.»* |

⊙ **Sayı üçünde de 26** — yani *«self-consistency %33»* kaydı **bayat**: terim çözülüyor
(`ariza_tipi eq "pompa arızası"`), ayrışan tek şey **kırılımın varlığı**. Ama ayrışan
şey masumsuz değil: kullanıcı zaten **tek bir tipe** süzmüşken *«en yüksek arıza tipi»*
demek, **yapılmamış bir kıyası ima eder**.

⚠ Ve bu kural depoda **zaten vardı** — yalnız yarısına uygulanmıştı: `_rank_facts`'in
`pay` satırı tek kalemde *«toplamın %100,0'i»* yazmayı bırakmıştı, çünkü canlı bir
kullanıcı ona *«boş laf»* demişti. Aynı gerekçe **başlığa** uygulanmamıştı.

> *Bir üstünlük iddiası, kıyaslayacak ikinci bir şey yoksa bir iddia değil bir süstür —
> ve süs, hesaplanmışla doldurulmuşu ayırt edilemez kılar.*

✅ Tek grupta `top`/`bottom` yerine `single` üretiliyor. Kapı
`tests/test_tek_kalemde_ustunluk.py` (5) — iki grupta sıralama, üç grupta pay **aynen
kalır** (`KURAL B`), ve `single` tanınan tip olmalı (yoksa cevap sessizce LLM'e düşerdi).
🟢 Canlı: tek tip → *«Arıza sayısı 26 adet»* · 8 tipli gerçek kırılım → *«En yüksek arıza
tipi: sensör hatası (16 adet, toplamın %21,3'ü). En düşük: elektrik kesintisi; 8 kalem.»*

### 18.6 🔴 `§YS-plan` — «TEMSİL EDEMEDİM» İDDİASI PLAN YOLUNDA **SÖYLENEMİYORDU**

`§0.6` satır 19 şunu ölçmüştü: *«müşteri kohort analizi yap» → 8 satır, ama kohort değil
**PİVOT** (müşteri × ay); 3 adım makbuzu var, «kohort metodolojisi uygulanmadı» beyanı
**yok**.* Kök **iki katmanlı** çıktı (2026-08-12):

| katman | ölçüm |
|---|---|
| çağrı | `uyum.yok_sayilan_beyani` **yalnız** küp yolunda (`ask.py:3151`); plan yolu ondan **önce** dönüyor (`ask.py:4222`) |
| 🔴 girdi | plan şemasında `yok_sayilan` alanı **hiç yoktu** — plan garsonu *«temsil edemedim»* **diyemiyordu bile** |

⚠ `uyum.denetle` bunu göremez: o bir **CubeQuery** denetleyicisidir (ölçü·boyut·sıralama);
*«kohort»* bir **metodoloji** sözcüğüdür, hiçbir küp eksenine karşılık gelmez.

> *Bir menüde olmayan yemek, mutfakta pişebiliyor olsa da sipariş edilemez.* (`§EŞ`)

✅ Alan plan şemasına **ve** istemine eklendi; beyan **aynı tek sahibe** bağlandı
(`uyum.yok_sayilan_beyani` — küp yolunun kullandığı gövde, `KAT-1`). Plan çok bloklu
olduğu için fiş **birleştirilerek** ölçülüyor (`§Cİ-belge` disiplini). Kapı
`tests/test_ys_plan_beyani.py` (7): alan şemada **ve** istemde · kohort iddiası
süzgeçlerden geçer · fişte geçen sözcük beyan **edilmez** (`§101.1`) · soruda geçmeyen
sözcük beyan **edilmez** · birleşik fiş kuruluyor mu (yapısal) · beyan turu düşürmez.

⚠ **CANLI DOĞRULAMA YARIM:** bu turda aynı soru üç koşumda da **plan yoluna düşmedi**
(`llm:openrouter` ×2, dürüst red ×1) — yol seçimi belirlenimsiz. Kanal birim düzeyinde
ölçüldü; **uçtan uca kanıt bir sonraki plan-yolu koşumunda alınacak**. *Ölçülmemiş bir
yolu ölçülmüş saymak, bu raporun kapatmaya çalıştığı kusurun kendisidir.*

⏸ Ve asıl yetenek (**kohort metodolojisinin uygulanması**) `§B10 Skills`'te ve **PARK**:
bayrak kapalı, açılış şartı `§26`. Bu düzeltme yeteneği değil **dürüstlüğü** kapatıyor.

# YEDİNCİ KISIM — CEVAP BİÇİMİ VE KONUŞMA UX'İ

> ⚠ **Kısmi bölüm.** UI/UX araştırması sekiz kolda yürüdü; bu bölüm **doğrulanmış**
> birincil kaynaklara ve tamamlanan *anti-desen* koluna dayanıyor. Bekleyen kollar
> (çoklu-artefakt kompozisyonu · *«grafik zarar verir»* akademik dayanağı · anlatı
> üretimi · takip anlama · arayüz desenleri) geldiğinde eklenecek. **Gelmeyen bulgu
> uydurulmadı.**

## 21 · CEVAP BİÇİMİ VE KONUŞMA UX'İ

> Sekiz araştırma kolundan **beşi tam** döndü (grafik-gerekmez akademisi · takip anlama ·
> anti-desenler · Pulse mimarisi · Power BI kuralları). **Üçü gelmedi** ve uydurulmadı:
> çoklu-artefakt kompozisyonu · anlatı üretimi (Arria/Quill/Smart Narrative) · arayüz
> desenleri. Sebep: oturumun arama bütçesi + Google/Bing/DDG bot engeli + Reddit/archive
> bloğu. **§37'nin F sınıfı.**

### 21.1 🔴 EN ÖNEMLİ BULGU — «her cevaba grafik» AMPİRİK OLARAK YANLIŞ

**Hearst & Tory (2019), *«Would You Like A Chart With That?»*, IEEE VIS** — ve bu doğrudan
**konuşma arayüzü** bağlamında ölçülmüş:

| bulgu | sayı |
|---|---|
| **Metni tek başına tercih** | **%41** |
| istatistiksel anlamlılık | χ²(1,N=45)=**26,8**, p<0,001 · χ²(1,N=44)=**17,9**, p<0,001 |
| **kişi bazında kararlılık** | **%89** (40/45) ve **%82** (36/44) aynı tercihte kaldı |

🔴 **Her beş kullanıcıdan ikisi sohbet bağlamında grafik İSTEMİYOR** — ve bu bir kaprisi
değil, **kararlı bir kişilik özelliği**.

Metin tercih edenlerin favorisi **«Text-values»** — ham değerleri veren biçim
(*«Weightlifting has 15 events, compared to Taekwondo's 8»*). ⊙ Çıplak cevap *«çok basit»*,
fark hesaplı uzun metin *«gereksiz karmaşık»* bulundu.

Makalenin kendi sonucu: *«Charts containing contextual information might be a reasonable
default… However, given the diversity of user preferences, such systems should offer
**personalization options**.»*

### 21.2 Ama «az metin iyidir» de yanlış — Stokes ve ark. (2022), IEEE TVCG

302 katılımcı, **minimalizm dogmasını tersine çeviriyor**:

> *«heavily annotated charts were **NOT penalized**. In fact, participants **preferred the
> charts with the largest number of textual annotations** over charts with fewer
> annotations or text alone.»*

**Sıralama:** CTA+ (3-6 anotasyon) **1.** → CTA2 **2.** → salt metin **3.** → **çıplak
anotasyonsuz grafik SON**.

* **Guideline 1:** *«Rather than aiming for maximally minimalist design, **annotate charts
  with relevant text**.»*
* **Guideline 4:** *«**Consider a text-only variant that can stand alone.**»*

### 21.3 🔴 Ve asıl ölçüt METİN MİKTARI DEĞİL, AMACI

**Stokes & Hearst (2022)**, 2000+ serbest yorumun tematik analizi:

> *«the issue that participants cared about most was **not the presence of text**, but
> rather **the PURPOSE it served**.»*

268 kişi ek bağlamı takdir etti, 227'si eksikliğinden şikâyet etti — ama **114 kişi
*«gereksiz/tekrarcı»* metinden rahatsız oldu** (grafikte zaten görüneni tekrar söyleyen).

⚠ **Ve bir uyarı:** anotasyon arttıkça *«yanıltıcı/önyargılı»* şüphesi de arttı
(CTA1:8 · CTA2:12 · CTA+:8) — salt metin yalnız **3** şüphe topladı:
*«Text was also **less considered a candidate for bias**.»*

⊙ **Bizim için:** `narration_guard`'ın varlığı bu şüpheyi kapatan şeydir — anlatıyı
**doğrulanabilir** yapmak, onu uzatmaktan daha değerli.

### 21.4 Ne zaman tablo, ne zaman grafik — algısal temel

**Franconeri, Padilla, Shah, Zacks, Hullman (2021)**, *Psychological Science in the Public
Interest* 22(3):110-161:

> **«Vision is Powerful for Global Statistics / Vision is Sluggish for Comparisons»**

Göz bir grafikten ortalama/uç değeri **milisaniyede** çıkarır; ama **ikiden-üçten fazla
değer çiftini karşılaştırmak yavaş ve kapasite-sınırlıdır** (saniyede birkaç karşılaştırma).
🔴 **Çok sayıda tekil değerin ARANMASI gerektiğinde grafik yanlış araçtır — o iş TABLONUN.**

> *«use visual grouping cues to control **which set of comparisons** a viewer should make,
> and use annotation and highlighting to narrow that set to **the single most important
> comparison** that supports your message.»*

⚠ Minimalizm nüansı: *«Despite strong calls to declutter…, it is only **mixed evidence**
that this practice improves aesthetic ratings and **little evidence** that the practice
affects objective performance.»*

⊙ Tartışma **100 yıllık**: **Washburne (1927)**, *«An experimental study of various graphs:
Tabular and textual methods…»*, J. Educational Psychology 18.

**Bertini, Correll, Franconeri (2020)** — *«her şey scatter olsun»* görüşünü **straw man**
ilan edip Tversky'nin **congruence principle**'ını hatırlatıyor: *«the content and format of
the graphic should **correspond to the content and format of the concepts** to be
conveyed.»*

### 21.5 🟢 BELGELENMİŞ TEK SOMUT KURAL SETİ — Microsoft Power BI

| durum | görsel | Microsoft'un kendi cümlesi |
|---|---|---|
| **tek değer** | **Card** — grafik değil, **büyük sayı** | *«Use cards when **a single number**, such as total sales or market share, is the most important thing to track.»* |
| **kesin değer arama** | **Tablo** | *«ideal when you need to see **exact values** and make quantitative comparisons across **many values** for a single category.»* |
| **hedefe ilerleme** | **KPI** | *«communicate progress made toward a **measurable goal**»* |

**Seçim kriteri dörtlüsü:** veri tipi · hedef (kıyas/trend/ilişki/ilerleme) · kitlenin
detay ihtiyacı · mevcut alan.

⊙ **Bizim `viz.py`'miz ilk ikisini zaten yapıyor** (`kpi` tek satırda, `table` ölçüsüz) —
**eksik olan «kitlenin detay ihtiyacı»**, yani §21.1'in kişiselleştirmesi.

### 21.6 🔴 ANLAMLI NEGATİF BULGU — satıcılar biçim kuralını YAYIMLAMIYOR

Databricks Genie'nin resmî dokümanı, cevabın neyden oluştuğuna ve **ne zaman grafik ne
zaman tablo** döndüğüne dair **hiçbir kural** içermiyor (bizzat çekilip doğrulandı).

⊙ **Rakiplerin *«akıllıca»* görünen davranışı yayımlanmış bir kural tablosundan değil,
model muhakemesinden geliyor.** Yayımlanmış tek net ilke seti **OpenAI Model Spec**:
*«Be clear and direct»* · *«Be thorough but efficient, while respecting length limits»* ·
biçim **isteğe göre**, **tek bir varsayılana saplanılmadan**.

🟢 **Bu bizim için fırsat:** biçim kararını **deterministik ve yayımlanmış** yapabiliriz —
sektörde kimse yapmıyor.

### 21.7 🟢 Tableau Pulse — *«deterministik olgu → LLM ifade»* deseninin kanıtı

> *«Tableau Pulse Insights Service **starts by using standardized, deterministic
> statistical models** to detect facts about metrics that are **guaranteed to be
> accurate**.»*
> *«Insight summaries **use a large language model to provide a personalized overview in
> plain language**.»*

Olgular *«scored based on the **impact** it has on the metric value»*; yalnız *«most
statistically impactful»* olanlar döner; ürün *«**avoids displaying noisy or spurious
findings**»* diyor.

**14 içgörü tipi** — ve **artefakt sayısını belirleyen mekanizma sabit şablon değil,
istatistiksel etki skoru + gürültü filtresi**:

| # | tip | # | tip |
|---|---|---|---|
| 1 | Period Over Period Change *(hep açık)* | 8 | Goal and Threshold Breakdown |
| 2 | Correlated Metrics | 9 | Pace to Goal |
| 3 | Record-level Outliers | 10 | **Top Drivers** *(aynı yönde)* |
| 4 | Forecast | 11 | **Top Detractors** *(ters yönde)* |
| 5 | Current Trend | 12 | **Concentrated Contribution** *(az üye katkının %50+'si)* |
| 6 | Trend Change Alert | 13 | Top Contributors *(hep açık)* |
| 7 | Unexpected Values | 14 | Bottom Contributors |

⊙ **Her tipin bir TETİKLENME KOŞULU var** — ör. `Concentrated Contribution` ancak az sayıda
üye katkının **%50+'sini** oluşturunca ateşlenir. **Cevabı çeşitlendiren, hangi olguların
tetiklendiğidir.**

### 21.8 🔴 «KATALOG GİBİ» — kullanıcıların kendiliğinden ad koyduğu kalıp

§18'de bizim ölçtüğümüz kusurun (chip hep 6, olgu hep 1-2) sektördeki adı var. HN'de
kullanıcılar bunu **kendiliğinden** teşhis ediyor:

> *«the whole **"repeat question, bullet points, summary" ceremony**»* — porridgeraisin
> *«The abundant bullet points, copious bold text, pithy one line summarizing
> assertions»* — dddgghhbbfblk
> *«many bullet points, em dashes, **it's not X but actually Y**»* — sosodev
> *«plus or minus **3 bullet points in a certain style**»* — Aurornis

Bir kullanıcı (gcanyon) modellerin özet istendiğinde neredeyse her seferinde **tam 20
madde** ürettiğini ölçmüş.

⊙ **Sabit yapı = robotluğun imzası.** Bizim `6,6,5,6,6,4,6,3` chip dizimiz bunun
deterministik hâli — LLM'in *«hep 20 madde»*si ile aynı hastalık, farklı sebep.

### 21.9 ⚠ Yalakalık/hedging YAPISALDIR — tasarım kazası değil

* **Anthropic, Persona Vectors:** *«training models based on human feedback can make them
  **more sycophantic**»*; *«if the "sycophancy" vector is highly active, the model **may
  not be giving them a straight answer**»*.
* **Nature:** *«Training language models to be **warm** can **reduce accuracy** and
  **increase sycophancy**»* — sıcaklık ↔ doğruluk arasında **ölçülmüş ödünleşim**.
* OpenAI'ın kendi post-mortem'i: *«Sycophancy in GPT-4o»*.

⊙ **Bizim için doğrudan sonuç:** *«daha insani konuşsun»* isteği **bedava değildir**.
`narration_guard`'ımız tam da bu bedeli ödememek için var — anlatıyı serbest bırakmak
ölçülmüş bir doğruluk kaybıdır. **Çözüm üslubu gevşetmek değil, olgu taksonomisini
zenginleştirmektir** (§21.1).

### 21.10 🟢 «CONTEXT IS THE PRODUCT» — küp-önce felsefemizin dış doğrulaması

HN, *«Lessons from building an AI data analyst»*: başarılı örnekler genel modelden değil,
**dar ve elle küratörlenmiş semantik bağlamdan** geliyor.

Ve Veezoo kurucusu (tillvz), bizim doktrinimizi kelimesi kelimesine yazıyor:

> *«**If AI writes SQL directly, you're building on a probabilistic foundation.** When a
> CFO asks for revenue **the number can't just be correct 99% of times.**»*

### 21.11 🔴 DOĞRULAMA YÜKÜ — rakiplerin ölçülmüş asıl kusuru

* **Databricks Genie kullanıcısı (a1o, HN):** *«often does not work completely for me…
  get things **90% there** and I need to jump in, **decipher the query**… and then figure
  how to change it.»*
  ⊙ Kullanıcı SQL'i deşifre etmek zorundaysa araç zaman kazandırmıyor, **yük ekliyor**.
* **Power BI (dav43):** *«it's **beyond hard to error check**.»*
* **Towards Data Science — *«Why 90% Accuracy in Text-to-SQL is 100% Useless»***:
  Spider 1.0'da (<10 tablo) %90+ olan modeller, Spider 2.0'da (ortalama **812 kolon**)
  **%10-20**'ye düşüyor. Kullanıcı **hangi %10'un yanlış olduğunu bilemediği** için kısmi
  doğruluk kabul edilmiyor; *«Adoption will decline.»*

⊙ **Bu, bizim beyan kültürümüzün ve makbuz yaklaşımımızın en güçlü dış gerekçesidir.**
Ve `adius`'un reçetesi bizde **zaten var**: *«**show the SQL query and make it editable**
so that the user can immediately fix simple errors.»*

### 21.12 Pano enflasyonu — ürün yönü için sinyal

HN *«Is Tableau Dead?»*, monkeydust:

> *«I have access to near **100 dashboards**… they more or less **do the same thing**…
> I don't feel passionate about any of them»*
> *«We **don't necessarily need more dashboards**, just **faster ways to go from question
> to reliable answer** where information can be **pushed rather than pulled**.»*

⊙ *«Pushed rather than pulled»* — Tableau Pulse'un feed tercihinin (§21.1) sebebi bu.
Bizim `schedules` + `channels` altyapımız bu yönü **zaten** destekliyor; ürünleştirilmemiş.

### 21.13 ⚠ DOĞRULANAMAYANLAR — ve bir önceki bölümde DÜZELTME

Araştırma bu dört maddeyi **birincil kaynaktan teyit edemedi** ve tahminle doldurmadı:

| iddia | durum |
|---|---|
| **Tableau Ask Data'nın emekliye ayrılması** | ⚠ **İki ajan çelişti.** Rakip-ürün koluyla gelen bilgi §6.1(c)'de *«Şubat 2024»* diye yazıldı; UX kolu `help.tableau.com`'dan **403/404** aldı ve **teyit edemedi**. *Bu satır bir birincil kaynakla doğrulanana kadar «tek kaynaklı» sayılmalıdır.* ⊙ Power BI Q&A'nın Aralık 2026'da kalkması **ayrı** ve **MS Learn'den doğrulanmış** bir maddedir |
| IBM Watson Analytics EOL tarihi | doğrulanamadı |
| Thoughtworks Radar'ın text-to-SQL'i *«Hold»*a alması | yalnız HN tanıklığı, birincil kaynak yok |
| **«Aşırı grafikleştirme» eleştirisi** | 🔴 **VERİ BOŞLUĞU** — *«her şeye grafik getirmek»* şikâyetimiz için **dış literatürde doğrudan eleştiri bulunamadı**. Ya kimse yazmamış, ya da rakipler bu kusuru yaşamıyor. **Ölçülmeden iddia edilmeyecek.** |

*Bir raporun değeri, doldurduğu boşluklar kadar, boş bıraktığını söylediği yerlerdedir.*

---

### 21.14 🔴 TAKİP ANLAMA — sayılarla, ve bizim niyet nesnemizin eksik listesi

#### CoSQL diyalog-eylem taksonomisi (arXiv:1909.05378)

**Kullanıcı 11 eylem:** `INFORM_SQL` · **`INFER_SQL`** (SQL + insan çıkarımı gerekir —
evet/hayır, *«3. en yaşlı»*) · **`AMBIGUOUS`** (sistem niyeti teyit etmeli) · `AFFIRM` ·
`NEGATE` · `NOT_RELATED` · `CANNOT_UNDERSTAND` · `CANNOT_ANSWER` · `GREETING` · `GOOD_BYE` ·
`THANK_YOU`
**Sistem 8 eylem:** `CONFIRM_SQL` · **`CLARIFY`** · `REJECT` · `REQUEST_MORE` · `GREETING` ·
`SORRY` · `WELCOME` · `GOOD_BYE`

🔴 **Bizim için kritik sayı:** majority-baseline (*«hep INFORM_SQL de»*) **%62,8** →
**soruların ~%37-40'ı doğrudan SQL'e çevrilemez**. Kalanların **~%40'ı `AMBIGUOUS`**,
onun ~%20'si `INFER_SQL`.

⊙ **Bu, «garson LLM» katmanımızın varlık gerekçesinin sayısal kanıtıdır.**

⚠ Ve en iyi model genel eylem sınıflandırmasında **%83,9** ama:
> *«The F-scores for more interesting and important dialog acts such as **`INFER_SQL` and
> `AMBIGUOUS` are around 10%**.»* — **tam ayırt etmesi gereken yerde çöküyor.**

#### SParC tematik ilişki taksonomisi (arXiv:1906.02285) — takip türlerinin haritası

| ilişki | örnek | **oran** |
|---|---|---|
| **Theme-entity** (aynı varlık, başka özellik) | *«kapasitesi?»* → *«tüm olanaklarını listele»* | **%48,4** |
| **Refinement** (aynı tür, farklı kısıt) | *«en az öğrencili?»* → *«en popüler olanı?»* | **%33,8** |
| **Theme-property** (aynı özellik, başka varlık) | *«X'in puanı?»* → *«Peki Y için?»* | **%9,7** |
| **Answer refinement** (önceki **CEVAPTAN** varlık) | cevap *«İstatistik böl.»* → o bölüm hakkında | **%8,1** |

⟳ **ÖLÇÜLDÜ (2026-08-12) — «BUGÜN YOK» İDDİASI BAYAT. DÖRDÜ DE ÇALIŞIYOR.**

Bu satır *«dört kova `niyet.py`'de yok»* diyordu. Canlı curl (dört turluk zincir) +
birim ölçüm, dördünün de çalıştığını ve dördünün de **`source=cube`** (sıfır LLM)
olduğunu gösterdi:

| ilişki | oran | canlı tur | ölçülen sonuç |
|---|---|---|---|
| **theme-entity** | %48,4 | *«o makinenin oee'si ne kadar»* | `makine eq RAM-2` · küp `parti`→`oee` |
| **refinement** | %33,8 | *«peki geçen yıl»* | dönem 2025'e kaydı, **varlık korundu** |
| **theme-property** | %9,7 | *«peki RAM-3 için»* | `makine eq RAM-3` — RAM-2 **düştü** |
| **answer-refinement** | %8,1 | RAM-2 **cevaptan** geldi (soruda yok) | + beyan: *«bir önceki turun seçtiği makine»* |

⊙ *«Odak varlığı yok»* kusuru **kapanmış**: `§B9 ODAK VARLIK` (`app/diyalog.py::
odak_suzgeci`/`odak_uygula`, kapı `test_odak_varlik.py` 13 test). Rapor onu **akademik
adıyla** yeniden keşfetti ama **kod adıyla** aramadı.

⏸ **KARAR — adlar `niyet.py`'ye EKLENMEDİ, ve bu bir karardır:** eksik olan ürün değil
**ad**. Ad eklemek tek başına bir tüketici doğurmaz; doğurmayan bir ad aynı kuralın
**ikinci sahibi** olur (`KAT-1`). Taksonominin verdiği asıl değer bir **kontrol
listesiydi** — o liste kapıya çevrildi: `tests/test_b9_sparc_iliskileri.py` (6), her
kova kendi oranıyla.

🔴 **VE KONTROL LİSTESİ GERÇEK BİR AÇIK BULDU:** `test_odak_varlik.py::
test_KAPSAM_BIR_PIN_DEGILDIR` şunu **yazıyor** — *«Var olan bir aralık atfı engellemez;
bir `eq` pini **engeller**»* — ama yalnız **birinci** yarıyı ölçüyordu. İkinci yarı,
`refinement` (%33,8) ve `theme-property` (%9,7) kovalarını koruyan şeydi: bozulursa
*«peki RAM-3 için»* iki `makine eq` süzgeci alır (`RAM-3` **ve** `RAM-2`) ve cevap
sessizce **0 satır** olur.

> *Bir kapı, iddiasının yalnız bir yarısını ölçüyorsa, öteki yarı yazılı bir
> temenniden ibarettir.*

#### ⚠ Tur bazlı çöküş — mimari uyarı

| tur | doğruluk |
|---|---|
| Turn 1 | **%38,6** |
| Turn 2 | %11,6 |
| Turn 3 | %3,7 |
| **Turn ≥4** | **%1,1** |

> *«many thematic relations are present **without explicit linguistic markers**…
> information tends to **implicitly propagate** through the interaction.»*

**Soru yeniden yazma tavanı:** CANARD — Copy 36,25 → Pronoun Sub. 47,44 → Seq2Seq **49,67**
↔ **insan üst sınırı 59,92** BLEU. Soruların %53,9'unda zamir var ama *«**two-thirds of our
data cannot be solved with pronoun resolution alone**»*. QReCC uçtan uca **F1 19,10 ↔ insan
75,45**.

**2025 durumu:** DySQL-Bench (arXiv:2510.26495) çok-turlu dinamik değerlendirmede GPT-4o
**%58,34 doğruluk, Pass@5 %23,81**. ⊙ *2019'un «turlar arttıkça çöküş» bulgusu **çözülmedi**,
yalnız mutlak sayılar yükseldi.*

#### 🟢 Ürünlerin GERÇEKTE yaptığı — ve bize önerilen model

| ürün | davranış |
|---|---|
| **Snowflake Cortex** | *«recognizes the follow-up, retrieves the context from the initial query, and **rephrases** the second question»*. Açık sınır: *«**doesn't have access to results from previous SQL queries**»* → **stateless LLM + geçmiş metni enjekte**; soru+SQL **metni** taşınır, **veri taşınmaz** |
| 🟢 **ThoughtSpot Spotter** (en net) | *«All follow-up questions are assumed to be a follow-up on **the LATEST answer** generated»*. Yeni konu için chat **resetlenmeli**. Filtre+gruplama state'i devralınıyor |
| **Databricks Genie** | *«Context from previous messages is retained»* ⚠ ama: *«**Avoid reusing conversation threads across sessions**, as this can reduce accuracy due to **unintended context reuse**»* |
| **Power BI Copilot** | *«Use **clear chat** when switching topics to avoid overloading Copilot with unrelated prior context»* |
| **Looker CA** | kullanıcıya açık talimat: *«refer to the previously established context, but **be explicit about changes**»* |

⊙ **Ortak desen:** hepsi *«soruyu yeniden yaz + geçmiş metnini enjekte et»*.
🟢 **Rakip strateji — CoE-SQL (NAACL 2024):** soruyu yeniden yazmak yerine **önceki SQL'i
az sayıda DÜZENLEME ile güncelle**; SParC/CoSQL'de ICL baseline'larını geçiyor.
⚠ **Bizim `deterministic_refine`'ımız tam olarak bu ailedendir** — yani bu konuda sektörün
**önerilen** tarafındayız, ölçmemiş olmamız hariç.

### 21.15 🟢 «Neden düştü?» — ÜÇ ÜRÜN DE NEDENSELLİK İDDİA ETMİYOR

| ürün | ne yapıyor | ne demiyor |
|---|---|---|
| **Tableau Explain Data** | karmaşıklık ↔ açıklanan değişkenlik ödünleşimi | *«Explain Data is **[not]** a tool that is giving you an answer or telling you anything about **causality**»* · *«**Correlation is not causation**»* |
| **Power BI Key Influencers** | kategorik → **lojistik regresyon** (ML.NET) · sayısal → **doğrusal regresyon** · segment → **karar ağacı** · **Wald testi p<0,05** · min **100+10** gözlem · 10.000 örneklem | nedensellik |
| **ThoughtSpot SpotIQ** | trend/korelasyon/artış-azalış/aykırı; **ayarlanabilir** max p-değeri, korelasyon aralığı ve gecikmesi, min göreli fark | nedensellik |

⊙ **Sentez:** *«Neden?»* hiçbir üründe gerçek nedensel çıkarımla değil, **katkı/sürücü
ayrıştırmasıyla** cevaplanıyor — ve en az biri bunu **açıkça ilan ediyor**.
🔴 **Bu, §14'ün E4 maddesini (*«kök neden» yerine «katkı analizi»*) doğrudan destekliyor.**

### 21.16 🔴 ÜÇ SOMUT ÇIKARIM — doğrudan uygulanabilir

**1 · *«Her cevaba grafik»* ampirik olarak yanlış.**
Sohbet bağlamında kullanıcıların **%41'i saf metin istiyor**, tercih **%82-89 kararlı**.
Grafik **varsayılan** olabilir ama **kişiselleştirme olmadan sabit kural yanlıştır**.
Somut: tek değer → **büyük sayı** (Power BI Card kuralı) · çok satırlı kesin değer arama →
**tablo** (Franconeri: *«vision is sluggish for comparisons»*).

**2 · Katalog hissini kıran şey biçim çeşitliliği değil, OLGU TAKSONOMİSİ.**
Pulse'un 14 tipi bir **grafik menüsü değil**; her biri **tetiklenme koşulu olan bir olgu**.
Mimari: **deterministik olgu → istatistiksel etki skoru → gürültü filtresi → LLM yalnız
cümleye döker.** ⊙ Ve §18.3'te ölçtük: `interpret.py`'de **11 üretici zaten var**, canlıda
**1-2** ateşliyor. **Mesafe 11→14 değil, 1-2→11.**

**3 · Takipte «SON CEVABA ÇIPALA» modelini seç.**
SParC: bağımlılık **ilk 3 turda** yoğunlaşıyor, Turn ≥4'te doğruluk **%1,1**. ThoughtSpot
tam bu yüzden **tüm geçmiş yerine yalnız son cevaba** çıpalıyor. Ve takip türleri **sabit
dört kova**: theme-entity **%48** · refinement **%34** · theme-property **%10** ·
answer-refinement **%8**.

# SEKİZİNCİ KISIM — TÜRK PAZARI VE YEREL RAKİPLER

## 19 · YERLİ REKABET HARİTASI — dört katman

### 19.1 🔴 Katman 1 — semantik katman + ontoloji + Türkçe NL: **TEK firma, ve o da perakendede kilitli**

**OBASE — AIReady / AIR** (`obase.com`, 30+ yıl, MicroStrategy MEA *«Yılın İş Ortağı»*).
AIR lansmanı **23 Ekim 2024**. Kendi ifadesiyle mimari üç katman: **(1) semantik katman
(2) ontoloji (3) ajan tabanlı orkestrasyon**. Türkçe NL arayüzü, site örneği:
*«Bugünkü satış düşüşüne ne sebep oldu?»* · anomali/KPI sapma · **sesli etkileşim
(STT/TTS)** · dashboard→yönetici özeti. Referans: **Migros — MiO**.

⊙ **Bizim tarifimizin en yakın muadili.** Ama: **perakende/telekom/lojistik/ilaç/finans**
odaklı, **imalat hedefinde DEĞİL**, Migros ölçeğine konumlanmış, fiyat şeffaflığı yok.

### 19.2 Katman 2 — yerli BI motoru + gömülü NL asistanı

**TURBOARD (E-Kalite Yazılım)** — 2004 kuruluş, iki ODTÜ mühendisi, ODTÜ Teknokent +
TÜBİTAK. **80+ çalışan**. **JAS** (*«Just Ask Simply»*): NL→SQL, NL→görselleştirme,
**JAS Explain** (grafiği doğal dille açıklama), JAS İçgörü (Haz 2025), özelleştirilebilir
AI persona'ları.

🟢 **İki güçlü yanı bizi doğrudan ilgilendiriyor:** **LLM bağımsızlığı** (Gemini/GPT/
DeepSeek/Mistral/Qwen/özel endpoint) ve **tam on-prem SLM** seçeneği (*«sorgular ve veri
altyapınızdan çıkmaz»*). Müşteriler: Turkcell, T.C. Sağlık Bakanlığı, UNDP.

🔴 **Ve fiyat KAMUYA AÇIK** (nadir): DMO TeknoKatalog ENT-U kurumsal kullanıcı lisansı
**19.493,83 TL KDV dâhil / 12 ay / kullanıcı**. ⊙ **Kamu satın alma kanalı açık** —
bizim hiç düşünmediğimiz bir dağıtım yolu.

⚠ Semantik/metrik katman bir **ürün olarak belgelenmiyor**; yerine *«beş öğrenme
seviyesi»* ve *«mevcut raporlara dayandırma»* iddiası var.

### 19.3 🔴 Katman 3 — **ERP-üstü text-to-SQL dalgası** (2025-26'nın gerçek rekabeti)

Araştırmanın en önemli bulgusu: son ~18 ayda Mikro/Logo/Netsis veritabanları üzerine
Türkçe NL→SQL asistanı yapan bir **eklenti ekosistemi patladı**. **Hepsi şema-üstü
text-to-SQL; semantik katman YOK.**

| ürün | ERP | ayırt edici | fiyat |
|---|---|---|---|
| **ERP Asistanı** (Valeria Medya, İzmir) | Mikro v15/16/17 · Netsis v3 · Logo GO 3 | şema-doğrulanmış SQL · uygulama üreticisi · *«Şirket Ajanları»* 7/24 anomali · **REST API + MCP SUNUCUSU** | **9.999 TL+KDV/ay** · 99.999 TL+KDV/yıl |
| **aiperas** | Logo **tam** + Mikro **tam** | NL sorgu · **kök-neden/driver analizi** · anomali · AutoML · yetki + denetim izi | açık değil |
| **Fora Kayra AI** (Eskişehir) | Mikro | metin + **ses** + dosya · KVKK, veri Mikro'da kalır | açık değil |
| **OzBI** | Logo · Mikro · 5 veritabanı | **Docker self-hosted** · *«5 dakikada kurulum»* · **«agent swarm»** · departman asistanları | açık değil |
| **ERPAS ai** | yalnız Logo | Türkçe NL + **sesli** · on-prem | açık değil |
| **WolvoxAI (AKINSOFT)** | Wolvox 26 ERP | gömülü Türkçe NL raporlama | 🔴 **ÜCRETSİZ — lisansa dâhil** |

🔴 **İki stratejik sinyal:**

1. **aiperas ↔ Solniro stratejik ortaklığı (27 Ekim 2025)** → **Logo ekosisteminde resmî
   distribütör**. Dalga **kurumsal dağıtıma** bağlandı.
2. **AKINSOFT NL raporlamayı ÜCRETSİZ verdi** (Mayıs 2026). ⊙ **Fiyat tabanı çöktü.**

⚠ **Ama zaafları kendileri itiraf ediyor.** Fora Kayra kendi blogunda: *«yeni sorguları
bilinen bir referansla **bir kez doğrulayın**»* · *«**muğlak sorular muğlak sonuç
verir**»*. ⊙ Bu, dbt'nin *«text-to-SQL'de başarısızlık makul ama yanlış bir cevaptır»*
cümlesinin Türkçe itirafıdır — ve **bizim ayrımımızın tam yeri**.

### 19.4 Katman 4 — dikey imalat AI ajanları

🔴 **GÜNCEL YAZILIM (Bursa)** — nişimizdeki **en yakın rakip**. 2000 kuruluş, **Sanayi ve
Teknoloji Bakanlığı onaylı Ar-Ge Merkezi**, 26+ yıl tekstil.

* **LEO TEXTILE** — iplikten konfeksiyona tekstil ERP; **boya/terbiye süreçleri modül
  içinde**.
* **WILOOM (MES & IoT)** — **kendi tasarladıkları IoT cihazları**: Wi-Fi, **sıcaklık +
  nem sensörü**, offline hafıza, **RFID vardiya okuyucu**; tezgâh dur-kalk, **OEE**,
  duruş/personel/ürün analizi, SMS alarm.
* **xLAP AI** — *«doğal dilde yönetilen kurumsal çözüm platformu»*: **Lead Architect**
  tarafından orkestre edilen **12+ uzman ajan** (SQL Uzmanı, Dashboard Tasarımcısı,
  IoT Monitör, Kalite Kontrol, Yetki Yöneticisi…).
* Müşteriler: **40+ firma; KOTON, COLIN'S, TOFAŞ, SANKO**.

🟢 **KRİTİK AYRIM — ve konumumuz tam burada:** xLAP'ın doğal dili öncelikle
**uygulama/dashboard/SQL ÜRETMEK** için; bir **AI low-code builder**. *«İş sorusu sor →
semantik katmandan doğrulanmış cevap al»* **değil**.

**Genel MES/OEE satıcıları:** ARGE BİLİŞİM `@rgemas` (**7 ülke, 200+ fabrika**, tekstil
açıkça hedefte: kumaş kontrol, yıkama hattı, kesim) · DORUK `ProMANAGE` (Teknopark
İstanbul + ABD, ISA-95, artırılmış gerçeklik) · ALFI `MES Suite Pro` (her modülde gömülü
AI). ⊙ **Hiçbirinde doğal dil analitiği belgelenmemiş.**

### 19.5 🔴 YENİ VE HIZLI RAKİP — DATIVA AI

`dativa.ai` · **2025 kuruluş**, İstanbul Ataşehir · **2-10 kişi** · Crunchbase tanımı:
*«Generative AI–powered **decision intelligence platform**… natural language, **what-if
simulations**»*, agentic akışlar.

⊙ **TRAI Girişim Haritası'nda · Web Summit Qatar 2026 startup programında · MEXT (Model
Fabrika) webinarında «imalatta agentic AI» konuşmacısı** → **bizim nişimize doğrudan
giriyor**. Açıklanmış yatırım turu yok. **Küçük, fonlanmamış — ama hızlı.**

### 19.6 Büyük yerli ERP üreticileri — ve bir düzeltme

⚠ **Düzeltme:** *«Netsis/Sage»* yanlış — **Netsis'i Logo 2013'te satın aldı**; Sage'in
tarihsel ilişkisi **Mikro Yazılım** iledir.

| firma | analitik durumu |
|---|---|
| **Logo** | **Mind Insight = Qlik Sense altyapısı** üzerine on-prem BI — **AI ve doğal dil YOK**. Ocak 2026: **TS EN ISO/IEC 42001 YZ Yönetim Sistemi** sertifikası. ⚠ *«LOGODIA»* adlı bir NL asistanı iddiası **tek kaynakta** (bir iş ortağı blogu) — Logo'nun kendi kanallarında **doğrulanamadı** |
| **Nebim V3** | İş Zekası **«powered by Power BI»** — kendi BI motoru yok. NL/AI asistanı **bulunamadı** |
| **Uyumsoft** | NLP/chatbot/talep tahmini blogda anlatılıyor ama **canlı ürün özelliği olarak doğrulanamadı** |
| **IAS / caniasERP** | 1.400+ müşteri, otomotiv/makine/metal. OLAP modülü var, **doğal dil sorgulama belgelenmemiş** |
| **Karel** | 🔴 **BI/AI veri ürünü YOK** — listeden elenmeli |

### 19.7 KAÇIRILAN OYUNCULAR — ikinci tarama *(kullanıcı uyarısı üzerine)*

🔴 **İlk tarama beş oyuncuyu kaçırdı ve hepsi gerçekti.** Kaçırma sebebi yöntemsel:
ilk tarama **tohum listesinden** (Sestek, Karel, Logo, Obase…) yürüdü — bu, **kurumsal ve
görünür** oyuncuları bulur, **küçük/yeni/SEO'su zayıf** olanları kaçırır. Oysa rekabetimiz
tam o kümede.

⚠ İkinci tarama da arama bütçesiz yapıldı (doğrudan alan adı çekme + DuckDuckGo HTML).
LinkedIn · Crunchbase (403) · YouTube · startups.watch **açılamadı**. Buna karşılık
doğrudan çekme, sitelerin **HTML kaynağındaki gizlenmiş içeriği** okuttu — raporun en
değerli iki bulgusu oradan çıktı.

#### A · Beş hedef

| ürün | kimlik | mimari | fiyat | imalat? |
|---|---|---|---|---|
| **DBTalk** `dbtalk.ai` | **Geobilgi Bilişim** (2014), Kocaeli · ürün **2023** · **23 kişi** · kurucular Helvacı/Sarı/Erkman | NL→SQL, 4 DB'ye **eşzamanlı**, 6 dil. 🟢 *«salt okunur SELECT… **yapılandırılabilir bir politikayla değil, MİMARİ DÜZEYDE** engellenir»*. 🟢 **Belirsizlikte «tek hedefli ek soru»** — garsonumuzun birebir muadili | yayınlanmamış | ⚪ |
| **Sofkar AI** `sofkar.ai` | kuruluş/şehir/kurucu/ekip **hiçbiri yok**; yalnız WhatsApp numarası | *«AI Agent platformu»* — analitikten çok **süreç orkestrasyonu**. 33 konnektör. 🔴 **En fazla 3 tabloya kadar** birleşik analiz. **Hiçbir ERP adıyla anılmıyor** → gerçek ERP entegrasyonu yok işareti. Semantik katman/doğrulama hakkında **sıfır** açıklama | yok · 14 gün deneme | ❌ banka/perakende/sağlık |
| **Mubisoft** `mubisoft.com` | **Mubisoft Yazılım A.Ş.**, İstanbul · **2026** | 🟢 **Bizim mimarimize en yakın olan.** Kendi başlığı: *«**Neden tek prompt değil, katmanlı pipeline?**»* → **4 akıl yürüten ajan** (Architect NL→SQL · Atlas şema örnekleme · Studio KPI/grafik · **Pulse anomalide kök-neden**) + **7 deterministik servis** (**Sentry: SQL doğrular + satır güvenliği + TC/IBAN/telefon PII maskeler**). *«AI ajanları akıl yürütür; **servisler deterministik ve denetlenebilir** çalışır»*. Logo Tiger 10 şablon · Mikro 4 · Netsis 3 · Nebim 3 | 🔴 **HTML yorumunda gizli:** ₺**1.290** / ₺**3.490** / ₺**8.990** ay (+KDV) | 🟡 ERP-genel |
| **ERP Asistanı** `erpasistani.com` | 🔴 **Valeria Medya Ltd.**, **Menemen/İzmir** — Mubisoft'tan **tamamen ayrı şirket** | Mikro v15/16/17 · Netsis · Logo GO3. *«gerçek şema doğruluğu»* + **binlerce doğrulanmış örnek** · **`/sql/validate` ucu** · REST API **confidence score** döndürüyor · **MCP Server** (Claude Code/Cursor) · *«Şirket Ajanları»* 7/24 izleme | 🔴 **9.999 ₺/ay** · **99.999 ₺/yıl** | 🟡 ERP-genel |
| **Listen to Data** `listentodata.com` | Nidakule Ataşehir, İstanbul · kuruluş/kurucu/ekip **sıfır iz** | Nebim V3 (birincil) + SAP. Boru hattı: NLP → SQL → **Doğrulayıcı** → sonuç. 🔴 **Doğrulayıcı YALNIZ GÜVENLİK denetliyor** (injection, salt-okunur) — **anlamsal doğruluk değil**. Prophet/ARIMA, XGBoost, RFM, Monte Carlo iddiaları | sabit liste yok | ❌ **perakende/e-ticaret** |
| **UMAI Bilişim** `umaibilisim.com` | **Sakarya** — *«**U**nified **M**ulti-**A**gent **I**ntelligence»* | PostgreSQL · **otomatik şema keşfi** · **açık kaynak LLM** (Llama 3, Mistral, CodeLlama) · **tamamen şirket içi** · **WhatsApp + Telegram bot**. Referans: Erenler Belediyesi, Sakarya Üniv., Feoks, CRT Makina | yok | 🟡 üretim emirleri kapsamda |
| ⚠ **UMAI Yazılım** (Konya) | **ayrı şirket** | telefon `+90 (555) 000 00 00`, e-posta `[email protected]` → **placeholder**; SEO içerik sitesi görünümü | — | **DOĞRULANAMADI** |

#### B · 🔴 İKİ HTML BULGUSU — pazarın olgunluğu hakkında

**1 · Listen to Data'nın kaynak kodunda gömülü itiraf:**

```html
<!-- TestimonialSection.astro — Yatırım getirisi odaklı demo senaryoları.
     Gerçek müşteri referansları hazır olduğunda bu bölüm referans formatına
     dönüştürülecektir. -->
```
⊙ **Sitedeki *«40 saniyede sonuç»*, *«6 saatten 20 dakikaya»*, *«ayda 80 saat»* rakamları
gerçek müşteri değil, DEMO SENARYOSU.**

**2 · Mubisoft'un fiyatları `<!-- FİYAT GEÇİCİ OLARAK GİZLENDİ -->` yorumu içinde duruyor.**
⊙ Türk KOBİ pazarında **katmanlı AI pipeline'ın parasal karşılığı ~₺3.490/ay**; AI istek
kotası (1.000/ay) yeni fiyatlama birimi.

#### C · İkinci taramanın çıkardığı YENİ oyuncular

| ürün | kimlik | ayırt edici | fiyat |
|---|---|---|---|
| 🥇 **TURBOARD / JAS** | **E-Kalite Yazılım**, **2004** · **500 bin+ kullanıcı** · **2 ABD patenti** · UNDP, Turkcell, **Sağlık Bakanlığı**, **Havelsan** | 🔴 **Pazardaki TEK gerçek semantik katman.** Kendi ifadesi: *«ikinci, **kopuk bir tanım katmanı üzerinden değil**, TURBOARD'da **zaten yönetilen iş mantığı** üzerinden»*. **5 katmanlı öğrenme**, beşincisi *«derlenmiş, **insan tarafından gözden geçirilmiş** bağlam»*. On-prem + **offline LLM** | yayınlanmamış |
| **Raporzone** | Mikro V16+ · Logo/Netsis yolda | 🟢 **Çift model doğrulama** + *«her sayı kaynağındaki sorguyu **göstermek zorunda**»* · salt-okunurluk *«bir ayar değil, **olmayan bir yetenek**»* | **₺2.000 / 3.000 / 5.000** ay |
| **nivq** (Nivorbit) | — | 🟢 **Semantik öğrenme katmanı** · 🔴 **pazardaki TEK sayısal doğruluk iddiası: 6. haftada +%34** · KVKK/BDDK/**EU AI Act** · Ollama air-gapped · 7 yıl denetim | **freemium: 15 sorgu/gün** |
| **ERPAS ai** | yalnız **Logo** (Tiger/GO Wings), on-prem | **sesli sorgu + sesli yanıt** · bağlamı koruyan takip · demo müşterisi **«YILMAZ TEKSTİL»** | yok |
| **ALL WISE BI** | **Fikir Yazılım**, **Gaziantep** | ERP verisi üstünde NL + tahminleme; konnektör *«teknik keşif toplantısında»* → hazır entegrasyon yok | yok |
| **Zugaps** · **Vinya** | — | SAP B1 asistanı · MS Dynamics 365 + Copilot entegratörü | — |
| DEBI · opqora · OnySoft Netsis AI · Quantum AI · muhasebeci.ai · Ponder.ing | — | dolaylı referans | **DOĞRULANAMADI** |

#### D · 🔴 SENTEZ — üç bulgu stratejiyi değiştiriyor

**1 · Pazar mimari olarak üçe ayrılıyor — ve tepede yalnız bir firma var:**

| katman | kim |
|---|---|
| **Gerçek semantik katman** | 🥇 **yalnız TURBOARD (JAS)** — yönetilen iş mantığı + insan onaylı bağlam |
| **Sonradan eğitilen şema sözlüğü** | Listen to Data (*«Veri Öğrenimi»*) · nivq · DBTalk · Mubisoft (Atlas) |
| **Ham text-to-SQL** | Sofkar · ERP Asistanı · UMAI · ERPAS ai |

**2 · 🔴 En büyük boşluk: *«doğrulama»* kelimesi GÜVENLİĞİ kastediyor, DOĞRULUĞU değil.**

DBTalk · Listen to Data · Raporzone · Mubisoft — **hepsinde** bir *«Doğrulayıcı / Sentry /
validate»* katmanı var, ama **hepsi salt-okunurluk ve SQL injection** denetliyor.
*«Bu SQL soruyu DOĞRU yanıtlıyor mu?»* sorusunu **yalnız ikisi** ele alıyor: **Raporzone**
(çift model + kaynak sorgu zorunluluğu) ve **nivq** (+%34).

⊙ **Bizim *«mutfakta LLM'e güvenmiyoruz»* + deterministik küp yaklaşımımızın savunulabilir
farkı tam burada.** Ve `narration_guard`/Query Contract, pazarın **hiç girmediği** yer.

**3 · Türkçe iddiaları yüzeysel — morfolojiye kimse dokunmamış.**

En yüksek çıta Listen to Data'nın *«Türkçe **karakter kaybı olmadan**»* ifadesi — yani
yalnız **karakter seti**. Mubisoft'un *«Etiket Ajanı»*ı kolon adlarını Türkçeleştiriyor ama
bu **çıktı** tarafında, **giriş** tarafında değil.
⊙ *«göre/bazında»* çok anlamlılığı, ek çözümleme, fiil-isim ayrımı — **pazarda kimse
dokunmamış**. §4.1'de *«ters yatırım»* dediğim 9.468 satır, **bu ışıkta yeniden
değerlendirilmeli**: yanlış olan yatırımın **kendisi** değil, garsona hiç yatırım
yapılmamış olması.

**4 · İmalat/tekstil dikeyinde tek ciddi rakip TURBOARD.**
Listen to Data (perakende) ve Sofkar (banka/sağlık) **hedefte değil**; Mubisoft/Raporzone/
ERP Asistanı sektör-agnostik; ERPAS ai Logo'ya kilitli ama demo müşterisi tekstil.

**5 · ⚠ Pazarda çok fazla «vitrin» var.** Ölçülen sinyaller: Mubisoft **placeholder
telefon** (`212 000 00 00`) + gizlenmiş fiyat · Listen to Data **sıfır bağımsız iz** +
demo-senaryo itirafı · UMAI Yazılım placeholder iletişim · Sofkar kurucu/ekip/müşteri
**hiçbiri yok** · ERP Asistanı müşteri adı yok.
⊙ **Kanıtlanmış ölçeği olan yalnız TURBOARD** (500K kullanıcı, patent, Havelsan/Turkcell/
Sağlık Bakanlığı) **ve kısmen DBTalk** (23 kişi, basın, ~15 PoC).

#### E · Bu bölümün kendi sınırı

**Doğrulanamayanlar (uydurulmadı):** tüm yatırım tutarları · Sofkar'ın kuruluş/şehir/
kurucu/ekip/müşterisi · Listen to Data'nın kuruluş/kurucu/ekibi · DBTalk/Sofkar/TURBOARD/
ERPAS fiyatları · **YouTube demolarının içeriği** (JS/403) · DEBI · opqora · OnySoft ·
Quantum AI'ın şirket kimlikleri.

**Taze aramada öncelik:** (1) startups.watch'ta DBTalk ve Listen to Data yatırım kaydı ·
(2) YouTube demolarının **gerçekten canlı ERP'ye mi bağlandığı** · (3) TURBOARD JAS'ın
fiyatı ve **gerçek Türkçe performansı**.

*Bir pazarın boş olduğunu söylemek, aramanın bittiğini varsaymaktır — bu rapor o varsayımı
iki kez yanlışladı.*

## 20 · BOŞLUK VE PAZAR GERÇEĞİ — sayılarla

### 20.1 🔴 TÜİK 2025 — hedef segmentimizin **%89,3'ünde BI YOK**

Girişimlerde Bilişim Teknolojileri Kullanım Araştırması 2025 (10+ çalışan):

| | genel | 10–49 | **50–249** | 250+ |
|---|---|---|---|---|
| ERP | %28,3 | %23,6 | **%46,0** | %76,5 |
| CRM | %12,0 | %9,9 | %18,4 | %42,0 |
| **İŞ ZEKÂSI (BI)** | **%6,5** | %4,9 | **%10,7** | %35,1 |

⊙ **Hedef segmentimiz olan 50–249 çalışanlı orta ölçekli işletmenin %46'sında ERP var,
%89,3'ünde BI YOK. VERİ VAR, CEVAP YOK.**

🔴 **Bu «Power BI'dan pay al» değil, «EXCEL'DEN pay al» oyunudur.**

**TÜİK YZ İstatistikleri 2025 (ilk kez):** herhangi bir YZ kullanan girişim
**2021 %2,7 → 2025 %7,5**.

**TÜSİAD SD² × Digitopia, Dijital Olgunluk 2024:** Türkiye DMI **2,87** ↔ global **2,99**
— ve **makas her yıl açılıyor** (2021: −0,09 → 2024: −0,12). **Bankacılık dışında hiçbir
sektör global ortalamayı yakalayamıyor**; üretim geride.

**TRAI ekosistem:** Türkiye'deki YZ girişimi **2017'de 24 → Nisan 2026'da 482**. Ocak
2026 partisindeki 40 yeni girişimde **öngörü ve veri analitiği yalnızca 2** ⊙ **veri
analitiği, Türk YZ ekosisteminin en az kalabalık dikeylerinden biri.**

### 20.2 Kategori farkındalığı **yok** — ve bu bir fırsat

Araştırma, Türkçe konuşmalı analitik üzerine **bağımsız konferans konuşması, YouTube
demosu veya topluluk içeriği bulamadı**. Veri Bilimi Okulu havuzunda konu yok. TÜSİAD
SD²'de 40+ başarı hikâyesi var (Ford Otosan, Brisa, Temsa, Teksan) ama *«doğal dil ile
veri sorgulama»* başlığı **yok**.

⊙ **Pazarı ilk eğiten avantaj kazanır** — ama aynı zamanda **ürün değil KATEGORİ satmak**
zorundayız.

**Fiilen ne kullanıyorlar:** **ERP hazır raporu + Excel**. BI alan azınlık = **Power BI**
(ya da ERP'sinin OEM ettiği Qlik/MicroStrategy). ⚠ Doğrudan anket bulunamadı; dolaylı
sinyal olarak Türkçe YouTube'da fabrika raporlamasını Excel'de öğreten içerikler
**42,1B / 22,3B / 3,8B izlenme**. *Bu anket verisi olarak sunulmuyor.*

### 20.3 🟢 Savunulabilir konum — ve üç risk

**Konum:** Kimse *«**imalat semantik katmanı** (OEE, boyahane reçetesi, duruş nedeni,
bakım, vardiya, İK) üzerinde **doğrulanabilir** Türkçe cevap»* satmıyor. OBASE
perakendede kilitli; xLAP kod/dashboard üretiyor; ERP asistanları şema-üstü tahmin
yapıyor **ve bunu kendileri itiraf ediyor**.
⊙ **Ayrımımız: DOĞRULANABİLİRLİK + İMALAT ONTOLOJİSİ.**

| risk | içerik |
|---|---|
| 🔴 **Fiyat tabanı** | AKINSOFT NL raporlamayı **sıfıra** indirdi; alıcı *«bu zaten ERP'mde var»* diyecek. Cevap net olmalı: **onlarınki ŞEMAYA sorar, bizimki İŞ TANIMINA sorar** |
| 🔴 **Dativa AI** | 2025 kuruluşlu, tam bizim tarifimizi yapıyor, **MEXT üzerinden imalata giriyor** |
| 🔴 **Kanal** | aiperas–Solniro örneği: **bayi kanalı olmadan orta ölçeğe ulaşmak zor**. Turboard'ın **DMO kamu kanalı** alternatif bir yol gösteriyor |

---

# DOKUZUNCU KISIM — GİRİŞİM RAKİPLERİ: NASIL YAPMIŞLAR

> Soru: *«Bu kadar firma bunu yapabiliyorsa biz neyi eksik yapıyoruz?»*
> ⚠ Ölüm iddiaları **beyana değil ÖLÇÜME** dayanıyor: canlı DNS/TLS/HTTP adli incelemesi,
> YC resmî API (**2.203 şirketlik tam sayım**), HN Algolia API, GitHub API.

## 22 · ÖNCE ÖNERMEYİ DÜZELT — *«bu kadar firma yapabiliyor»* YANLIŞ

### 22.1 🔴 MEZARLIK — ağ testiyle doğrulanmış

| şirket | kanıt | akıbet |
|---|---|---|
| **DataGPT** | `datagpt.com` **A kaydı YOK** | ÖLÜ · ~$22M / ~$1,3M ARR = **17×** |
| **Delphi** | HTTP 200 ama içerik **Hollandaca kumar sitesi** | Ekip **Cube'a katıldı** → kendi semantik katmanının sahibi tarafından **yutuldu** |
| **Patterns** (YC S21) | HTTP **402 Payment Required** · `DEPLOYMENT_DISABLED` | ÖLÜ — Vercel faturası ödenmemiş |
| **Propel** | GoDaddy **park sayfası** | ÖLÜ |
| **Sisu Data** | **TLS sertifikası süresi dolmuş** | Snowflake aldı, ürün öldürüldü · **$128,7M / $9,9M = 13×** |
| **Vizly** (YC S23) | sertifika **13 aydır** yenilenmemiş | ÖLÜ |
| **Zing Data** | **DNS YOK** | Kapandı 20 Ara 2025 |
| **Dataherald** (YC W21) | DNS yok · GitHub **3.644★**, son commit Tem 2024 | ÖLÜ — **464 puanlık Show HN'e rağmen** |
| **Vanna AI** | **23.822★** ama repo **ARŞİVLENMİŞ** (Şub 2026) | 🧟 **ZOMBİ** — en çok yıldızlı OSS text-to-SQL, ticari dönüşüm yok |
| **Fosfor** (LTIMindtree) | `fosfor.com` A kaydı yok · `ltm.com`'da *«Fosfor»* **0 kez** | ⚠ **fiilen tasfiye — resmî duyuru yok, ÇIKARIM** |

**Satın alınanlar:** Seek AI → **IBM** ($7,5M ile 3,5 yılda çıkış) · Numbers Station →
**Alation** · Wobby → **Actian/HCL** · Outerbase → **Cloudflare** · Fabi.ai → **Omni** ·
AskEdith → **Athenic** · Buster → **pivot**.

### 22.2 🔴 YC TAM SAYIMI — 2.203 şirket

**2023 analitik kohortu: %19,0 ölü + %28,6 satılmış = %47,6 bağımsızlığını kaybetti**
(batch geneli %22,3). ⊙ **Analitik girişimleri 2,1× daha fazla bağımsızlığını yitiriyor**
— ve bu bir **alt sınır** (pivot edenler hâlâ *«Active»* görünüyor).

**YC'nin iştahı çöküyor:** analitik payı **2023 %8,5 → 2024 %6,0 → 2025 %5,1 → 2026 %2,7**
(P26 %1,5 = **tarihsel dip**).

### 22.3 🔴 Thoughtworks text-to-SQL'i **HOLD**'a düşürdü

Radar Vol 33 (5 Kas 2025): Trial → **HOLD**, gerekçe *«its reliability often falls short
of expectations»*. ⊙ **18 ayda Trial'dan Hold'a düşen nadir tekniklerden.**

## 23 · DERİN PROFİLLER — ve her birinin bize dersi

### 23.1 🟢 OMNI — kategorinin kazananı, mimarisi bizimki

Mart 2022 · **Colin Zima (eski Looker Chief Analytics Officer)** + Jamie Davidson (eski
Looker VP Product). **~$216M**, Series C $120M @ **$1,5B** (Nis 2026). ~190 kişi.
⊙ **Kuruluştan lansmana ~5 ay** — çünkü **kurucular Looker'ı zaten yapmıştı**.

**Mimari:** kendi semantik katmanı + **ajanın SQL yazmasını YASAKLIYOR**. Akış: soru →
**Topic** (küratörlü dilim) → ajan **alan/filtre SEÇER** → **motor SQL'i DERLER** →
doğrulama ajanı denetler. Zima buna **«harness»** diyor.

🔴 **Setin en somut ölçümü** (28 Tem 2026): kendi prod verisinde **100 gerçek soru**,
5 mimari, Claude Opus hakem + ikinci Opus denetçi, **iki kez** koşturuldu.

| | Omni | en yakın alternatif |
|---|---|---|
| doğruluk | **95/100** (zorlarda %90) | zorlarda **%60** |
| tutarlılık | **96/100 aynı** | **30 cevabı değiştirdi**, **19 kez hiç cevap veremedi** |
| maliyet | $1,04 / 670K token | $1,29 / 1-6M token |

🔴🔴 **EN KRİTİK BULGU:** semantik katman **VE** playbook verilen genel amaçlı **lider
kodlama ajanı yine de 21 PUAN GERİDE**.

> Zima: *«when you hand a coding agent the semantic layer, **it's used as a REFERENCE
> where it should be a RULEBOOK**.»*

Somut felaket: *«It even read the comment we left in the model warning about this exact
query… **"I have all the definitions I need," it said. Then it did its own thing…** It
said our top campaign was worth **$55.5 BILLION** in pipeline.»* (Kartezyen fan-out.)

⊙ **Bu, `plan_semasi`'nin kapalı `enum` kararının en güçlü dış gerekçesidir.**

### 23.2 🔴 ZENLYTIC — en öğretici itiraf: **kurulum vergisi**

2021 NY · **$15M / 3 tur** · Verizon, J.Crew, Stanley Black & Decker, Workday, Domino's.
**Mimari:** kendi semantik katmanı + **«Clarity Engine»** deterministik doğrulayıcı.

> Blankley (6 Ağu 2026): *«the Clarity Engine validates every field reference, join, and
> aggregation against your model… **This is not a model grading its own homework. It is a
> checker… This is the one part we will not make probabilistic, because it is the reward
> signal.**»*

🔴 **EN KRİTİK İTİRAF** (13 May 2026): *«**Zenlytic is hard to set up. We should just say
it… Weeks. Sometimes months** of tweaking before a non-technical person can ask a question
and trust the answer. **That setup tax is why we've mostly worked with large enterprises so
far.**»* — Aynı gün **satış-liderli modeli terk edip self-serve açtılar**.

⊙ **Bizim en yakın risk aynamız:** 23 küp, elle küratörlenmiş paketler → **kurulum vergisi
bizde de var ve ölçülmüyor.**

### 23.3 🟢 VEEZOO — **mimari ikizimiz** + dil kaması dersi

2016 **ETH Zürih spin-off** · $6M Series A (Eyl 2025) · yönetim kurulunda **Mark Nelson —
Tableau'nun eski CEO'su** · AXA, Bayer, Helvetia.
⊙ **Kuruluştan Series A'ya ~9 YIL** — setin en yavaşı, çoğunlukla kendi yağıyla.

**Mimari = bizim Intent-JSON'umuz:** Knowledge Graph + **VQL** (kendi ara temsili) → LLM
**VQL yazar** (yalnız önceden tanımlı KG kavramları) → **deterministik derleme** → SQL.
🔴 **Grafik başlıkları/filtreler/etiketler BİLE VQL'den render ediliyor, LLM'den değil** —
bizim **ADR-0024** yasağımızın birebir aynısı.

> *«**The AI never writes SQL directly.**»* · *«**No Prompt Injection Risks** — The AI
> operates only on predefined Knowledge Graph concepts.»* · *«**Deterministic Results** —
> The same question always produces the same result.»*

🔴 **WEDGE = DİL + COĞRAFYA:** DACH/Almanca kurumsal; karşılaştırmalarında **Power BI
Copilot'ın yalnızca İngilizce olduğunu vurguluyorlar** + İsviçre/AB veri ikametgâhı.
⊙ **Türkçe kamamızın doğrulanmış emsali — $6M Series A ile ödüllendirilmiş.**

🚩 **En büyük tutarsızlık:** *«#1 In Benchmarks»* diyor ama **kaynak yok**; *«benchmark»*
adlı tek varlıkları bir **veri hikâyeciliği yarışması**. ⊙ **Determinizm iddiası en güçlü
şirket, yayınlanmış kanıtı en zayıf şirket.**

### 23.4 🟢 DOT — en az sermaye, **en dürüst kapsam beyanı**

~7 kişi · seed sonrası **halka açık tur yok** · Duolingo, Choco, KRY.
**Wedge = KANAL:** Slack/Teams/e-posta. **Mimari = agresif REUSE** — kendi katmanını
dayatmıyor, **var olanı okuyor** (dbt, Power BI, Looker, Malloy, Cube + Notion/Jira).

> *«The layer was never the requirement. The requirement is that **MEANING IS RECORDED
> SOMEWHERE A MACHINE CAN READ IT**.»* · *«Every BI and AI vendor, **US INCLUDED**, has an
> incentive to become the place where your definitions live. **RESIST ALL OF US.**»*

🔴 **Raporun en iyi belgelenmiş kapsam reddi — HN'de rakiplerin önünde:**
*«Dot works well for questions answerable with **1 SQL QUERY AND SOME PYTHON**.»* ·
*«customers have **LESS THAN 10 TABLES** hooked up.»* · *«**I don't think all
organizations are ready for AI.**»*

### 23.5 🟢 HEX — reuse stratejisinin ayakta kalanı

2019/2020, **hepsi eski Palantir** · **~$171M** · 2.000+ müşteri · Reddit, Notion,
**Anthropic**, Figma. **Wedge = PERSONA** (veri pratisyeni). **Mimari = REUSE** (dbt, Cube,
MetricFlow, **Ossie**).

> McCardel: *«we want to lock you in with an **awesome product experience**, not a
> proprietary yaml format.»*

🔴 **Yazılı reddi:** *«it's definitely **not "instant insights in a box"**. These models
**don't know the right questions to ask**… that's your job! And **we think it should stay
that way**.»*

**Eval felsefesi bizimkiyle aynı:** akademik benchmark'ları **açıkça reddediyor**
(*«those are **vanity evals**»*); kendi eval'lerinin **yalnızca %20'si geçiyor**.

🔴 **En dürüst öz-eleştiri:** *«**Sunk-cost fallacy** and deep belief in our notebook
domain expertise kept us working on it **much longer than we should have**.»*

### 23.6 Kalan profiller

| şirket | ders |
|---|---|
| **Upsolve AI** (YC W24, **5 kişi**, $1,5M) | **Wedge kayması kanıtlı**: gömülü GenBI → *«Agent Studio for Data Teams»*. **Fiyat en şeffaf:** Free → Pro **$500/ay** → Team **$2.000/ay**. *«**7 days** to a working, reliable agent»* |
| **Pyramid Analytics** | 🔴 **Mimarisi Intent-JSON'umuzun aynısı** (*«LLM… GENERATE THE RECIPE»*) ama **şirket yorgun**: iş ilanı sitemap'i **3,5 yıldır** güncellenmemiş, basın bültenleri Tem 2025'te durmuş, BlackRock'tan **borç-benzeri $50M** |
| **Julius AI** (YC S22, **10 kişi**, $10M) | **Semantik katman YOK.** 2M+ kullanıcı, saf self-serve PLG ($20-$500/ay). Wedge = **eğitim** (Harvard Business School zorunlu dersi). Şikâyet: *«it'll reference some database it has created **without your knowledge** and give you the **WRONG ANSWER**»* |
| **Basedash** (YC S20, 6 kişi) | 4 yıl admin-panel: *«**we were hill climbing an ant hill**»* → pivot → *«**4× more revenue** in one year than the entire 4 years before»*. *«6 aylık satış döngüsü $2k/yıl → **self-serve $12k/yıl**»*. **BI Bench**'i yayınladı |
| **Bruin** (Türk kurucu **Burak Karakan**) | ~**$20K** (Techstars) ile ~**$1M ARR**. Yazısı: *«Building an AI Data Analyst Sucks»* |
| **Tellius** | $17M / **$22,8M ARR = 0,75×** → **sağlıklı**, çünkü **pharma dikeyine gömülmüş** |
| **Findly** (YC S22) | **Malloy** + derleyici doğrulaması. *«For the past **3 YEARS** I've been building an AI data analyst.»* |
| **Athenic** (eski AskEdith) | 4 yıl ve **bir marka ölümünden** sonra: *«**IT'S NOT A MODEL PROBLEM. WE LEARNED THIS THE HARD WAY.** …**YOU WERE RIGHT.**»* |
| **Text2SQL.ai** | **TEK KİŞİ**, bootstrapped, ~$96K ARR, **4 yıldır ayakta** |

## 24 · 🟢 YAKINSAYAN MİMARİ — 2026 konsensüsü

**Bağımsız 9+ ekip aynı tasarıma vardı: LLM NİYETİ yazar, DETERMİNİSTİK MOTOR hesaplar.**

```
Pyramid «recipe» · Veezoo VQL · Inconvo «structured query object» · Athenic Semantic Model
Wren MDL · Zenlytic Clarity Engine · Findly Malloy · Omni Topic+harness
Akademi: GRID (RBAC gramere derleniyor, +13 puan) · RUBICON (kısıtlı arayüz %100 ↔ agentic ReAct %0)
```

⊙ **DİMA'nın *«LLM SQL yazmaz»* değişmezi aykırı bir tercih değil — KAZANAN TARAFIN
TANIMI.** ⚠ Ama Omni'nin nüansı hayati: semantik katman **yetmiyor**, **zorlayıcı harness**
gerekiyor (§23.1'in 21 puanı).

## 25 · SEKTÖRÜN ÇÖZÜLMEMİŞ KAVGASI — bağlam öğrenilir mi, küratörlenir mi?

**A tarafı (Zenlytic):** *«**Index the queries, not just the tables**… a company might have
2.000 tables but only **150 PATTERNS** that actually matter.»*

**B tarafı (ANTHROPIC — kendi üretim sisteminden, ÖLÇÜMLE, 3 Haz 2026):**

> *«**Design for null results. Our most useful ablation was a negative one.** We gave the
> agent direct grep access to our entire dashboard, transformation, and analyst-notebook
> SQL (thousands of files)… **ACCURACY MOVED BY LESS THAN A POINT.** … About 80% of the
> time [cevap korpustaydı]. … **THE INFORMATION WAS THERE, THE AGENT SAW IT, AND IT STILL
> DIDN'T USE IT. That single experiment told us our bottleneck wasn't access to prior
> work, IT WAS STRUCTURE.**»*

Ve: *«One idea that **DIDN'T WORK**: bootstrapping the semantic layer by having an LLM
auto-generate metric definitions… It produced **plausible-looking definitions that encoded
the very ambiguities we were trying to eliminate**, and was **net-negative** versus a
smaller, **human-curated** layer.»*

**Anthropic'in diğer ölçümleri:** skill'siz **%21 → skill'li >%95** · **bakımsız
bırakılınca bir ayda %95 → %65** · skill markdown'ları **transformation modelleriyle aynı
repo, aynı PR'da**; veri-modeli PR'larının **~%90'ı** skill değişikliği içeriyor; alan
sahibi **~%90 eval eşiğini** geçmeden ajanı duyuramıyor; *«have the grader judge the
agent's **QUERY** rather than its number»*.

⊙ **Bizim *«beyanla sınıflandırma, elle uydurma yok»* disiplinimiz B tarafında — ve B
tarafının elinde ÖLÇÜM var.** Kesişim: **sorgu geçmişini ham malzeme olarak kullanıp insan
onayına sunmak** — VQR'ımızın tam da yapabileceği şey.

## 26 · EKİP, SÜRE VE «ZOR KISIM AI Mİ?»

### 26.1 Ekip büyüklüğü ile hayatta kalma arasında **korelasyon YOK**

YC'nin `teamSize` alanı, 2025-26 analitik kohortu (n=48): **medyan 2 kişi, %81'i ≤4 kişi**.

```
Bricks 2 (yaşıyor) · Vizly 2 (ÖLDÜ) · Patterns 2 (ÖLDÜ) · Definite 3 · Buster 4 (pivot)
Outerbase 4 (satıldı) · Upsolve 5 · Basedash 6 (yaşıyor) · Dot ~7 · Julius 10
Findly 11 · DATAHERALD 18 (ÖLDÜ) · ParaQuery 1 (yaşıyor) · Text2SQL.ai 1 (yaşıyor)
```

### 26.2 Süre: demo **haftalar**, güvenilir ürün **yıllar**

Omni **5 ay** (istisna) · Findly **3 yıl** · Veezoo **9 yıl** · Zenlytic 5 yıl sonra hâlâ
*«haftalar, bazen aylar»* kurulum.

### 26.3 🔴 *«Zor kısım AI mı?»* — kanıt: **ÇOK AZI**

> **Buster kurucusu**, 2 yılını ve $2,4M'ını böyle özetledi: *«**I WAS ABLE TO REBUILD OUR
> W24 IDEA (AN AI DATA ANALYST) IN ~5 MINUTES.** I pointed Cursor at our old repo…»*

> **Definite kurucusu:** *«**THE AGENT IS KIND OF THE EASY / FUN PART.** Getting the data
> infrastructure right so the agent works — **that's the hard part**.»*

> **Zing Data kapanış yazısı:** *«we didn't build something **indispensable to enough
> people willing to pay fast enough**.»*

Sayılar aynı yöne: Anthropic'in **+74 puanı modelden değil** bağlam/skill katmanından ·
Dot'un **%10→%90'ı** *«modelden değil **konfigürasyondan**»*.

⊙ **AI katmanı artık bir hafta sonu projesi. Zor kısım: veri altyapısı, bağlam bakımı
(bakımsız 1 ayda %95→%65), dağıtım ve GÜVEN KANITI.**

### 26.4 🔴 Asıl ölüm sebebi: **sermaye/gelir uçurumu**

| ölenler | oran | yaşayanlar | oran |
|---|---|---|---|
| Sisu | $128,7M / $9,9M = **13×** | Tellius | $17M / $22,8M = **0,75×** |
| DataGPT | ~$22M / $1,3M = **17×** | Bruin | ~$20K / ~$1M |
| Numbers Station | $17,5M / $1,5M = **12×** | Querri | ~0 / $1,9M |

**Ve dağıtım:** Sisu'nun kapanış duyurusu HN'de **2 puan, 0 yorum**. Seek.ai'nin HN'de
toplam varlığı **2 tesadüfi yorum**. Wren **17.229★** ama organik HN tartışması **yok**.

## 27 · 2026'DA SATILABİLİR ASGARİ KAPSAM — dokuz madde

1. 🔴 **Kapsamı acımasızca daralt.** Databricks resmî önerisi **space başına ≤5 tablo**
   (tavan 30) · Looker **5 Explore** · Dot müşterilerinin çoğu **<10 tablo**.
   ⊙ **Kimse *«tüm ambara sor»* ürünü satmıyor — pazarlama öyle diyor, DOKÜMAN demiyor.**
2. **Bir dikey seç.** Yatay *«AI veri analisti»* ölüyor: Tellius→pharma, Kadoa→finans.
3. **Deterministik ara temsil + doğrulayıcı** — artık **giriş bileti**, farklılaştırıcı değil.
4. 🔴 **Netleştirme döngüsü — en ucuz kaldıraç: +50 puan** (%42,5 → %92,5).
5. **Getirmeyi ayrı birinci-sınıf problem say.** Pinterest tablo arama %40→%90; SEDE
   %52→%92. *«Systems often fail **BEFORE** SQL is generated.»*
6. **Denormalizasyon.** 3+ tabloda mevcut sistemler **%20 hata oranıyla** çöküyor.
7. **Yayınlanmış eval + provenance** — Basedash bunu **OEM satışının merkezine** koydu.
8. **Self-serve fiyat.** Koltuk bazlı fiyat *«herkes veriye ulaşsın»* vaadiyle çelişiyor ve
   **ölenlerde yaygın**. Çalışanlar: Basedash düz **$1.000/ay**, Definite **$250/ay
   sınırsız kullanıcı**, Veezoo *«readers always free»*.
9. 🔴 **Ajan yüzeyi (MCP).** Wren **chat UI'ını legacy'e gömdü**; Rill'de projelerin
   **%50+'ı ajan tarafından** kuruluyor. ⊙ **Chat UI 2026'da varlık değil YÜK.**

## 28 · SENTEZ — ölenler ile yaşayanlar

| ÖLENLERİN ortak özellikleri | YAŞAYANLARIN ortak özellikleri |
|---|---|
| sermaye/gelir uçurumu **12-17×** | sermaye/gelir **≤1×** ya da gerçek kurumsal traksiyon |
| farklılaştırıcı = **başkasının katmanı + UI** (Delphi → Cube tarafından yutuldu) | **kendi zorlayıcı harness'i** (Omni, Veezoo, Zenlytic) **VEYA** reuse'u **çoğullaştırmış** (Hex 3+, Dot 7 katman) |
| dağıtım/zihin payı **sıfır** | **bir kama**: persona · kanal · göç · **dil-coğrafya** |
| **kapsam reddi YOK** | **YAZILI kapsam reddi** (Hex *«What this isn't»*, Dot *«1 SQL + biraz Python»*, Omni `ai_chat_topics`) |
| yayınlanmış doğruluk kanıtı yok | **yayınlanmış eval ya da açık metodoloji** |

## 29 · BİZE DÜŞEN

### 29.1 🟢 Dışarıdan DOĞRULANAN kararlarımız

| kararımız | emsal |
|---|---|
| LLM SQL yazmaz / Intent-JSON | **9 bağımsız emsal** (§24) |
| garson / netleştirme | **+50 puan** ölçülmüş |
| sayıyı her zaman küp koyar | Zenlytic: *«this is the one part **we will not make probabilistic**»* |
| grafiği LLM'e vermeme (ADR-0024) | **Veezoo: grafik etiketleri bile VQL'den render** |
| Query Contract / makbuz | Bruin · BitBoard |
| join planlayıcı yasağı | **Omni'nin $55,5 milyarlık fan-out felaketi** |
| toplu eval kapısı | **Anthropic %90 launch gate** |
| Türkçe kaması | **Veezoo'nun DACH kaması → $6M Series A** |
| *«payda kutsaldır»* | 🔴 **Üç satıcı payda oyunu yapıyor** (Dot *«450+»* → gerçekte 30 · Veezoo *«#1»* → kaynak yok · Omni 95/100 kendi verisi). ⊙ **Bu pazarda SATILABİLİR bir farklılaşma** |

### 29.2 🟢 BENZERSİZ olan — ve henüz kanıtlanmamış

**HAVA BOŞLUĞU:** modelin rakamı **üretememesi**. Veezoo/Pyramid en yakın emsal ama
**gizlilik özelliği** olarak konumluyorlar, **güvenlik sınırı** olarak değil.
⚠ **Ölçülüp yayınlanmadığı sürece sadece bir iddia.**

### 29.3 🔴 GERÇEK eksiklerimiz — mimari değil

| # | eksik | dış kanıt |
|---|---|---|
| 1 | **Kurulum süresi ölçülmüyor** | rakipler *«7 gün»*/*«60 saniye»* satıyor; Zenlytic'in *«haftalar, bazen aylar»* itirafı bir **uyarı** |
| 2 | **Getirme / şema budama ayrı kapı değil** | %40→%90 kaldıracı |
| 3 | 🔴 **Yayınlanmış doğruluk sayısı YOK** | *«Bu bir savunma değil, **SİLAH**»* |
| 4 | **Öğrenilen bağlam döngüsü** (düzeltme → aday bağlam → insan onayı) | VQR'ımız yarısını yapıyor |
| 5 | **Çok turlu bellek tur bazında ölçülmüyor** | *«3. turda sıfır»* bulgusu |
| 6 | **Tanım çakışması yönetimi** | WisdomAI: *«biggest source of **unexplained trust erosion**»* |
| 7 | **MCP yüzeyi kapalı** | 2026'da **dağıtım kanalının kendisi** |

### 29.4 🔴 Doktrinimizin sınırı — dürüstçe

*«Dürüst red başarı değil»* kuralımız **sektörden AYRILIYOR** (dbt ve Definite reddi
**erdem** sayıyor). Çıtamız daha yüksek ve savunulabilir — **ama yalnızca kapsam açıkça
İLAN EDİLDİĞİNDE.**

⊙ Yerleşikler **5 tabloya daralarak %90** alıyor. **İlan edilmemiş kapsamda her red bir
BORÇ; ilan edilmiş kapsamda RED ÜRÜNÜN KENDİSİDİR.**

*Seek AI'nin mekanizması bize en yakın üst versiyon: **yapılandırılabilir güven eşiği** +
kaynağın etiketlenmesi (*«verified by Seek, NOT A HUMAN»*), eşik altı insana gider.*

---

# ONUNCU KISIM — AGENTIC MİMARİLER: SEKTÖR NE YAPIYOR

## 30 · 🔴 ÖNCE TEŞHİSİ DÜZELT — *«kategorik olmak»* kusur DEĞİL

Şikâyet: *«kapalı bir fiil kümesi ve şablonlarla zar zor.»*
**Araştırmanın en net bulgusu: liderlerin de kapalı kümesi var — ama o küme «plan
fiilleri» değil, «ARAÇLAR».**

| sistem | kapalı araç sayısı |
|---|---|
| **Snowflake Cortex Agents** | **9 araç tipi** |
| **Microsoft Fabric Data Agent** | **4 sorgu aracı** (+ max **5 veri kaynağı**) |
| **Cube MCP** | 16 araç |
| **Google CA API** | 3 araç sınıfı |
| **Zenlytic Zoë** | ~4 araç |
| **DİMA** | **15 plan fiili** (canlı — ⟳ *«7» BAYATTI, ölçüldü 2026-08-12: `plan_semasi.FIIL_ANLAMI` **15** anahtar, `AZAMI_ADIM=12`*) / **25 araç** (bayrakla, `yazma_araclari` açıkken 27) |

⊙ **Kapalılık kusur değil. Kusur şurada: bizim 15 öğemiz *araç* değil, *plan adımı*; ve
her adımın içi şablon.** Endüstri farkı **üç yerde**:

1. 🔴 **DÖNGÜ var.** Snowflake'in resmî ifadesi: **Plan → Use Tools → Reflect and Respond**
   — *«ajan bu döngüyü tek bir istek içinde gerektiği kadar tekrarlar; plan **LLM
   tarafından bestelenir, sabit değildir**»*.
2. **Plan doğal dildedir, `enum` değil.** Magentic-One'ın Orchestrator'ı planı *«doğal
   dilde adım adım»* yazar.
3. 🔴 **Araç içi serbest, araç dışı sıkı.** Üretim (SQL) deterministik/derlemeli; **hangi
   aracı ne zaman çağıracağı serbest.**

### 30.1 🟢 Snowflake Cortex Analyst = **SABİT 6-AJANLI BORU HATTI**

Sektörün **en doğru** text-to-SQL'i (**%90+**, tek-atış GPT-4o'nun **~2 katı**,
*«piyasadaki başka bir çözümden ~%14 daha doğru»*) — ve **serbest ajan değil**:

| # | ajan | işi |
|---|---|---|
| 1 | **Classification** | soruyu 4'e ayırır: **belirsiz / veri-dışı / SQL-dışı / cevaplanabilir** |
| 2 | **Feature Extraction** | sorunun karakterini çıkarır (zaman serisi? dönem-üstü? sıralama?) ve **downstream prompt'u değiştirir** |
| 3 | **Context Enrichment** | (i) **verified queries** (ii) **relevant literals** — kullanıcının kelimesi ↔ DB değeri uçurumunu semantik aramayla kapatır |
| 4 | **SQL Generation** (çoğul) | önce **mantıksal şema**, sonra fiziksele post-process |
| 5 | 🔴 **Error Correction** | **SQL derleyicisini kullanarak** hem sözdizimsel hem **anlamsal** hata arar |
| 6 | **Synthesizer** | aday SQL'lerden nihai sorgu |

⊙ **Bizim *«kategorik»* dediğimiz şeyin ta kendisi — ama 15 iş fiili değil, 6 BİLİŞSEL
AŞAMA:** sınıflandır → özellik çıkar → bağlam zenginleştir → üret → **onar** → sentezle.

### 30.2 Diğer üreticiler — kısa

* **Microsoft Fabric Data Agent** = **sabit 6 adım**. Sert sınırlar: **max 5 veri
  kaynağı**, kaynak başına **≤100 örnek sorgu**, cevap **25 satır × 25 sütun**,
  salt-okunur, **yalnız İngilizce**. Niyet önceliği: **kurumsal > rol > geliştirici >
  kullanıcı**.
* **Databricks Genie:** **paralel çok-ajanlı keşif** → soruşturma (kök-neden dâhil) →
  **öz-düzeltme ve mutabakat** → **nihai doğrulama**. *«Parallel thinking»*: aynı soru için
  **birden çok yörünge** örneklenir — *«çünkü veri işlerinde kodda olduğu gibi deterministik
  doğrulama testi yok»*. İç kıyas **%32 → %90+**. Supervisor: **max 50 ajan**.
* **ThoughtSpot Spotter:** text-to-SQL **değil** — *search token*. Kohort, özel takvim, LOD
  ifadeleri **motorda**, üretilen SQL'de değil.
* **Hex** (bize en yakın mühendislik anlatısı): **ephemeral (görünmez) sorgular** ile
  ajan önce veriyi tanıyor → ilk denemede doğruluk yükseliyor · **araç patlaması**:
  ~**100.000 token**lık araç tanımını birleştirerek düşürdüler · **bağlam kirlenmesi
  felaketi**: *«çelişkili bağlam modeli bir **çöküş moduna** soktu»* — 30 dakika eylemsiz
  salınım · **Metric City**: 90 günlük simülasyon, Claude Sonnet **gün 0'da %4 → gün 90'da
  %24**; yorumları: *«%24 başarısızlık değil, işin **gerçek zorluğunun** kanıtı»*.

## 31 · ANTHROPIC'İN REHBERİ — *«ajan kullanMA»* yönergesi

> *«Mümkün olan **en basit çözümü** bulmanızı ve ancak gerektiğinde karmaşıklığı
> artırmanızı öneriyoruz. Bu, **hiç agentic sistem kurmamak** anlamına da gelebilir.»*
> *«Birçok uygulama için **retrieval ve bağlam-içi örneklerle tek bir LLM çağrısını
> optimize etmek genelde yeterlidir**.»*
> *«Karmaşıklığı ancak **gösterilebilir şekilde** sonuçları iyileştiriyorsa ekleyin.»*
> *«Ajanların otonom doğası **daha yüksek maliyet ve birikimli hata potansiyeli** demektir.»*

**ACI (Agent-Computer Interface):** *«HCI'ya harcanan çabayı düşünün ve iyi ACI yaratmaya
**aynı kadar** çaba ayırın»*; SWE-bench ajanında *«**prompt'tan çok araçları optimize
etmeye** zaman harcadık»*.

**Çok-ajanlının FİYATI:** ajanlar sohbetten **~4× token**, çok-ajanlı sistemler **~15×**.
Ve **nerede ÇALIŞMAZ:** *«tüm ajanların **aynı bağlamı paylaşması** gereken veya ajanlar
arasında **çok bağımlılık** olan alanlar»*. 🔴 **Analitik tam olarak o alandır** — kohort/
funnel/YoY adımları birbirine **bağımlıdır**.

## 32 · SABİT mi SERBEST mi — ölçülmüş kanıt

### 32.1 AWS Strands: **Swarm (serbest) ↔ Graph (sabit)**

| metrik | Swarm | **Graph** |
|---|---|---|
| ort. gecikme | 45 sn | **32 sn** |
| P95 gecikme | 78 sn | **38 sn** |
| token/iş | ~12.000 | **~8.500 (−%25)** |
| insan puanı | **8,2/10** | 7,6/10 |
| maliyet/iş | $0,08 | **$0,06** |

⊙ Şirket **ikisini birden koştu**: gece batch = **Graph**, yüksek değerli derin analiz =
**Swarm**. *«Sabit mi serbest mi»* sorusunun doğru cevabı **«ikisi de, farklı iş
sınıflarına»**.

### 32.2 🔴 Bileşik hata (Lusser yasası)

| adım-başı | 5 adım | 10 adım | 20 adım | 50 adım |
|---|---|---|---|---|
| %99 | ~95% | ~90% | ~81% | ~60% |
| **%95** | ~77% | **~59%** | ~35% | ~7% |

> *«10 adımlık bir kök-neden analizi iş akışı, çok iyimser %95 adım doğruluğunda bile
> zamanın yaklaşık **%40'ında başarısız olur**.»*

Ve **soft failure** (makul ama yanlış çıktı) hard failure'dan tehlikelidir.
**Saha ölçümleri:** TheAgentCompany 175 görev → en iyi model **%30,3** · DABstep 450+
finans görevi → en zorlarda **%14,55** · Magentic-One **kolay görevlerde daha KÖTÜ** —
⊙ **orkestrasyon her basit soruda ödenen bir vergidir.**

### 32.3 Akademik desenler — sayılarla

| yöntem | ölçülen |
|---|---|
| **ReAct** | ALFWorld **+34 puan** |
| **Reflexion** | HumanEval pass@1 **%91** (GPT-4 SOTA %80) |
| **Tree of Thoughts** | Game of 24: CoT %4 → **%74** |
| 🟢 **Self-Discover** | CoT'a karşı **+%32'ye kadar**, CoT-SC'yi **%20+** geçerken **10-40× daha az** hesap |

⊙ **Self-Discover bizim için en ilginci:** sabit fiil listesi ile serbest planlama
arasındaki **tam orta yol** — sabit bir *atomik modül* kümesi var, **kompozisyon serbest
ve göreve özgü**, ve **10-40× daha ucuz**.

## 33 · MCP — tesisat, doğruluk değil

**Kim ne açıyor:** dbt MCP **~45 araç** (semantik katman için `list_metrics` ·
`get_dimensions` · `query_metrics` · `get_metrics_compiled_sql`) · Cube MCP **16 araç**
(**yazma işlemleri onay gerektiriyor**) · Tableau ~15 (**salt okuma**) · Power BI ~30+
(**iki ayrı sunucu, birleşik orkestrasyon yok**) · Looker ~20 · Qlik ~25 · ThoughtSpot ~20.

🔴 **Ölçülmüş olumsuz kanıt:**
* **Araç sayısı bozulması:** geniş araç setiyle araç seçim doğruluğu **%13,62**'ye
  düşüyor; ilgili alt kümeyi sunmak **%43**'e çıkarıyor. **~20 araç eşiği.**
* **Bağlam maliyeti:** 7 MCP sunucusu = **67.300 token** siz bir harf yazmadan. Aynı sorgu
  CLI ~200 token ↔ MCP **~12.957 token (65×)**.
* **Gecikme:** REST'e göre çağrı başına **3×**, ilk çağrıda **9,4×** yavaş.
* **Perplexity CTO'su** iç kullanımda MCP'den **geri döndüklerini** açıkladı.

🟢 **Karşı-kanıt:** Anthropic **Tool Search + Deferred Loading** → bağlam kullanımında
**%85+ azalma**; **code execution with MCP** → **150.000 → 2.000 token (%98,7 tasarruf)**.

🔴 **Güvenlik — analitikte özellikle ciddi:** 14 CVE · internetten erişilebilir **7.000 MCP
sunucusu** · 2.614 uygulamada **%82 path traversal, %67 code injection**.
⊙ **Bizim için özel risk:** veri tablolarındaki **serbest metin alanları** (müşteri notu,
ürün açıklaması) MCP yanıtı olarak modele döndüğünde **prompt injection taşıyıcısıdır**.
Kendi verisini okuyan bir sistem için bu teorik değil.

## 34 · ÇOK ADIMLI SAYISAL AKIL YÜRÜTME — en zayıf halka

🔴 **Kırılan sözdizimi değil METODOLOJİ.** Teşhis cümlesi: *«**sözdizimi doğruluğu,
metodoloji doğruluğundan kolaydır**»*. Model geçerli CTE'ler yazar, **analitik kuralı
ihlal eder**. Beş somut hata:

1. **Adım sırası ihlali** — ulaşılmayan adım tamamlanmış sayılıyor
2. **Uyumsuz yollarda kullanıcı tekrar kullanımı**
3. **Dönüşüm penceresi yanlış uygulaması**
4. **Kohort ataması hataları**
5. **Geri dönüş olayı mantığı hataları**

⊙ **Hiçbiri SQL hatası değil — hiçbiri `EXPLAIN`'de görünmez, hiçbiri exception atmaz.
SESSİZ YANLIŞ.**

**Kim iyi yapıyor — üç desen, hepsi aynı fikir:**
1. 🟢 **Ara temsil + deterministik derleyici.** Akademik en net kanıt: **SMQ** (Semantic
   Model Query) — ajan ham şema üstünde SQL üretmiyor, kompakt ara temsil üretiyor,
   **deterministik derleyici** SQL'e çeviriyor. Sonuç: **Spider2-snow'da %94,15**, resmî
   liderlik tablosunda **3. sıra**. ⊙ *Bizim MDL/CubeQuery mimarimizin akademik ikizi.*
2. **Semantik katman > serbest SQL** (§7.4'teki dört ölçüm).
3. **Çok yörünge + mutabakat + doğrulama** (Genie, Snowflake Synthesizer, Hex ephemeral).

## 35 · KARAR MOTORU — kategori doğdu, temeli zayıf

**Gartner Ocak 2026'da *«Decision Intelligence Platforms»* MQ kategorisini AÇTI.**
**Pigment** üç ajanlı kademeli otonomi: **Analyst** (reaktif) → **Planner** (proaktif,
*«farklı bölgesel stratejileri **simüle eder**»*) → **Modeler** (otonom model kurar).
⊙ Not: **Planner, Analyst'ın çıktısına dayanıyor** — öneri **ölçüme zincirlenmiş**.

🔴 **Zayıf halka: NEDENSELLİK.** Bugün BI'ın *«kök neden»* dediği şey neredeyse tamamen
**korelasyonel ayrıştırma**: *«metrik hangi boyutta düştü»* sorusunu cevaplıyor, *«neden
düştü»*yü değil. Prescriptive iddia için **nedensel model + karşıolgusal veri** gerekir;
**hiçbir BI satıcısı bunu ölçülmüş biçimde yayımlamıyor.**

**Hata modları:** korelasyonu nedensellik diye sunmak (öneri üretildiği an **aksiyona
dönüşüyor**) · simülasyonun kalibre olmaması · **anomali körlüğü** (Hex'in fan-out
deneyi: model %900'lük sapmayı **kendiliğinden fark etmiyor**, sorulunca anında yakalıyor)
· **query drift** (ajan governed katman yerine ham tabloya iniyor, tanımlar ayrışıyor).

> *«Bunlar uç durum değil, **yönetişim otonom üretimin gerisinde kaldığında VARSAYILAN
> SONUÇTUR**.»*

## 36 · 🟢 BİZE ÖNERİLEN HEDEF MİMARİ — üç katmanı ayırmak

Liderlerin ortak yapısı, ve bizim durumumuz:

| katman | sektör | **bizde** |
|---|---|---|
| **Orkestrasyon** (hangi araç, hangi sırayla, ne zaman dur) | **SERBEST** — LLM besteler, döngü + reflect | 🔴 **SABİT** (15 fiil + şablon) |
| **Yetenek/araç** (ne yapılabilir) | **SABİT** — 4-20 iyi tanımlı araç | 🟢 zaten sabit (ama *araç* değil, *plan adımı*) |
| **Üretim** (SQL/hesap) | **DETERMİNİSTİK** — semantik katman derler | 🟢 **güçlü** (Wren/MDL) |

⊙ **Tek yapısal değişiklik: 15 fiili «plan şeması» olmaktan çıkarıp ARAÇ yapmak ve üstüne
DÖNGÜ koymak.** Fiil listesini **silmeyin** — OpenAI'ın eşiğine göre (*«15'ten fazla ayrık
araç sorun değil; **10'dan az örtüşen** araç sorun»*) **örtüşmeyen** bir küme ideal
aralıkta. ⚠ Ve bu, §17.5'te ölçtüğüm **%73 örtüşmeyi** de çözer: iki sistem birleşince
küme *örtüşmeyen* hâle gelir.

### 36.1 Kopyalanacaklar — etki/maliyet sırasıyla

| # | ne | dayanak | bizde |
|---|---|---|---|
| 1 | ✅ **Reflect + Repair döngüsü** *(⟳ KURULDU — ölçüldü 2026-08-12: `plan_garson.py:122 ONARIM_TAVANI=2` · `plan_onarim.py` 325 satır · `plan_kosucu.py:305/359/369` bağlı · `features.yml onarim_dongusu: beta` · kapı `test_b4_onarim_dongusu.py`)* — derleyici hatasını **ajanın gözüne** ver | Snowflake Error Correction · Wren `retry&repair` · Genie öz-düzeltme. **Bu ajanlık değil, WORKFLOW** | 🔴 tek *«DÜZELTME TURU»*; hata modele **geri verilmiyor** |
| 2 | **Triaj + belirsizlik kapısı** | Cortex 1. ajanı · Wren `ambiguity detection` | 🟢 var (`soz.py`) — ⚠ ama *«anlamadım»* yerine **netleştirme sorusu** üretmeli |
| 3 | **VQR + hafıza geri besleme** | Snowflake VQR · Wren LanceDB · Fabric 100 örnek | ✅ ⟳ **GARSONA BAĞLANDI** (ölçüldü 2026-08-12: `vqr.py:449 few_shot_block` → `ask.py:4074` `§B2` dalı · `features.yml vqr_few_shot: beta` · kapı `test_b2_garson_few_shot.py`). Eski hâli: `vqr.store` **var**, garsona **beslenmiyor** |
| 4 | **Ephemeral/karalama sorgusu** | Hex: *«ilk denemede doğruluk yükseliyor»* | 🟡 ⟳ **AMACI KARŞILANIYOR, MEKANİZMA FARKLI** (→ `§0.6` satır 20, ölçüldü 2026-08-12): Hex soru-başına gizli sorgu koşuyor; biz **kurulum anında bir kez** profilliyoruz — `_enrich_categorical` + `_enrich_cube_dim_values` + `value_index.FuzzyIndex`, **121 boyutun 120'si (%99)** değer taşıyor, canlı doğrulandı. Yapılmayan: per-soru keşif (`§31` *«en basit çözüm»* rehberiyle bilinçli) |
| 5 | ✅ **Skills (markdown)** *(⟳ KURULDU 2026-08-12: `demo/skills/yoy-orani.md` + `katalog_metni.skills_metni()` + `skills` bayrağı **off**, açılış şartı `§26`; kapı `test_b10_skills.py` 6 test)* — *kapalı fiil listesinin ilacı, kod yazmadan* | Anthropic + Snowflake + Wren, **üçü de aynı desen**. *«bir skill'e paketlenebilecek bağlam **fiilen sınırsız**»* | 🔴 **YOK** — kohort/YoY-oranı/funnel/what-if birer **markdown** olmalı |
| 6 | **Ara temsil + deterministik derleyici** | SMQ **%94,15** | 🟢 **var** (MDL/CubeQuery) |
| 7 | **Eval disiplini — Hex modeli** | **30-50 elle yazılmış soru**, her biri **ayrı bir hata modu**; Anthropic *«~20 sorguyla başlayın»* | 🟢 **≥20 senaryo kuralımız literatürle örtüşüyor** |
| 8 | **Bütçe + durdurma koşulu** | Snowflake token+süre · **Magentic-One stall counter ≤2** → yeniden planla | ✅ ⟳ **CANLI** (ölçüldü 2026-08-12): `planner.py:75-78` varsayılan tavan `adim=8·saniye=30·sorgu=12`, `:424` uygulanıyor, `:432 ButceAsimi`; stall tavanı `plan_garson.py:122` **2**. ⚠ Ve canlı `/ask` çağrıları **daha DAR** bütçe geçiyor (`ask.py:331/2393` `6·20·8`, `:273` `3·10·0`) — varsayılan bir **tavandır**, daralmak güvenli yöndür |

### 36.2 Kaçınılacaklar

1. 🔴 **Çok-ajanlı mimariye ATLAMAYIN** — **15× token**, ve analitik tam olarak
   *«bağımlılık yoğun»* alan. AWS ölçümü aynı yöne.
2. 🔴 **Araç sayısını şişirmeyin, MCP'yi otomatik iyilik sanmayın** — **~20 araç eşiği**.
   ⊙ **15 fiilimiz bir avantaj** *(⟳ «7» bayattı; ölçüldü 2026-08-12)*. MCP'yi **dışa açılım** için kullanın, içeride çoğaltmak
   için değil.
3. **Zincir uzunluğunu kutsamayın** — *«akıl yürütmeyen adımları kaldır, adımları
   birleştir»*; **her adım LLM çağrısı olmasın**.
4. 🔴 **Otonom aksiyon almaya erken geçmeyin** — TheAgentCompany **%30,3**, görev başına
   **>$4**. **Karar önerin, kararı uygulamayın.**

### 36.3 🟢 Tek cümlelik hüküm

> **Rakiplerin bizde olmayan şeyi serbest FİİL KÜMESİ değil, serbest DÖNGÜ; ve rakiplerin
> bizden almak için para harcadığı şey bizde zaten var — deterministik semantik katman.**
> Cortex Analyst %90+'ı **sabit 6 aşamalı bir boru hattıyla**, dbt %100'ü **serbest
> SQL'den vazgeçerek** alıyor. Yapılacak iş kategorileri atmak değil; **kategorileri plan
> şeması olmaktan çıkarıp araç yapmak, üstüne gözlem-yansıma-onarım döngüsü koymak ve
> metodolojiyi şablondan SKILL'e taşımak.**

---

# ON İKİNCİ KISIM — ÖNCE / SONRA MİMARİ HARİTASI

> ⚠ Bu bölüm **uygulama sırasında açık tutulacak** referanstır. Her satır: *«bu işi bugün
> KİM yapıyor → yarın KİM yapacak → nasıl doğrulanacak»*.
>
> 🔴 **Geliştirme sırasında güncellenecek dosyalar** her satırda **adıyla** yazılıdır.

## 38 · SORUMLULUK DEVİRLERİ — on üç değişiklik

### 38.1 Bağlam ve seçim

| # | iş | **ÖNCE (bugün)** | **SONRA (hedef)** | dokunulacak dosyalar | MİMARİ.md'de güncellenecek |
|---|---|---|---|---|---|
| ✅ **D1** | Garsona şema verme | `katalog_metni.metin_ve_indeks()` → **23 küpün tamamı, 23.729 karakter**, her soruda | ✔ **soruya göre budanmış KATALOG METNİ** (⟳ **08-12 yeniden ölçüldü:** 1-23 küp; tasarruf **%0–95**, `%71-90` değil — ve **2/8 soruda %0**, yani fail-open). ⚠ `extract_by` DEĞİL — ölçüldü: o model/view budar, garson istemi küplerden kurulur | `app/cube_router.py` (`daraltma_adaylari`) · `app/katalog_metni.py` · `app/routers/ask.py` | ✅ **§3.3b** yazıldı — *«katalog metni soruya göre daraltılır; indeks ASLA budanmaz»* |
| ✅ **D2** | Garsona örnek verme | ❌ **yok** — istem yalnız katalog + soru | `vqr.ara()` ile **retrieval**, istemin içine **5-10 doğrulanmış (soru → CubeQuery) çifti** | `app/vqr.py` (yeni `ara()`) · `app/llm.py::_cube_select_system` · `app/routers/ask.py` | **§4 LLM rolleri** — *«garson few-shot alır»* |
| ⏸ **D3** | İş sözlüğü | ⟳ **ÖLÇÜLDÜ (2026-08-12): MEKANİZMA VAR, TÜKETİCİSİ EKSİK.** `business_rules` kurulu ve bağlı (`wren_service:1008` → `llm.py:225`) ama **yalnız Discovery'nin SQL istemine**; garsonun `_cube_select_system`'i yalnız katalog alıyor. ⚠ Ve mevcut içerik (SQL semantiği · Logo `TRCODE`) **garsona uymuyor** — garson SQL yazmaz | Mevcut kanal garson istemine de bağlanır (**ikinci mekanizma açılmaz**, `KAT-1`); içerik küp-seçimi düzeyinde yazılır. 🔴 Ölçülen `gerçekleşme` kusuru **bununla çözülmez**: çapraz-küp KPI kalemi, eksik olan bir **İŞ BEYANI** | `app/llm.py::_cube_select_system` · `demo/packs/*/instructions.md` · `app/kpi.py` | **§3.x** yeni alt bölüm ⟳ **KARAR:** **PARK, şartı `§26` (`§40.9`)** — `§B3` ile aynı iş. Mekanizma var ve bağlı ama **Discovery'nin SQL istemine**; garsona bağlamanın kazancı ancak garson doğruluk ölçümüyle görülür, ve mevcut içerik (SQL semantiği · Logo `TRCODE`) garsona **uymuyor**. |
| ✅ **D4** | Belirsizlik | ⟳ **DOĞRULANDI — UÇTAN UCA (2026-08-12).** Canlı: *«bu yıl bakiye»* → cevap **verilir** (`cari`, ₺11.859.052,65) · beyan **yapılır** (*«birden fazla yerde tanımlı… Diğerleri: bakiye (mizan)»*) · öteki tanıma **tek tık** üretilir (`suggestions`: `bakiye (mizan (hesap bakiyeleri))`) · ve ön uç onu **basıyor** (`ReportPanel.tsx:357`). ⚠ *«Üretimde Intent-JSON netleştirmeyi gölgeliyor»* endişesi ölçüldü: **gölgelemiyor** — beyan+chip yolu çalışıyor. ⊙ İlk ölçümüm üç soruda da `source=None` verdi; sebep **bayat token**tı (ders ⑩), ve chip'i göremedim çünkü `next_steps or suggestions` yazmıştım — kısa devre (ders ⑰). *Bir aracın kendi kısa devresi, ürünün eksikliği gibi okunur.* | **aynen kalır** ⊙ *dışarıdan doğrulandı: +50 puan* | — | — |

### 38.2 Hakem ve döngü

| # | iş | **ÖNCE** | **SONRA** | dosyalar | MİMARİ.md |
|---|---|---|---|---|---|
| ✅ **D5** | Sorgu hatası | `plan_garson`'da **tek** *«DÜZELTME TURU»*; `llm.py`'de yalnız **boş yanıt** yeniden denemesi | **Reflect+Repair döngüsü**: derleyici/motor hatası **modele geri verilir**, en fazla **2 tur**, sonra dürüst red | `app/plan_kosucu.py` · `app/plan_garson.py` · `app/llm.py` | **§2 merdiven** — *«6. basamak artık onarım döngüsü taşır»* |
| ✅ **D6** | Plan yetenek listesi | ⟳ **ÖLÇÜLDÜ (2026-08-12) — ve kusur örtüşme oranı DEĞİL, KAPSAMDI.** Eşleşme **gövde düzeyinde** sayıldı: 9/15 fiil kayıtlı bir aracın gövdesini çağırıyor, ama 🔴 **6/15 fiilin gövdesi kayıtta HİÇ YOKTU** (`MATRIS`·`SIRALA`·`RAPOR`·`PANO` → `app.ilkeller`; `KIYASLA`·`BOYUTSEC` → `app.contribution`). *«Tek yetenek kaydı»* iddiası **altı yetenek eksikti**: planlayıcı onları çağırabiliyordu ama envanter yetki sınıfını/determinizmini/maliyetini **bilmiyordu**. *Bir kaydın tekliği, sayısıyla değil KAPSAMIYLA ölçülür.* | ✅ **YAPILDI:** ① altı ilkel kayda girdi (25→**31**, sayı kapısı gerekçesiyle güncellendi; yeni yetki sınıfı **açılmadı** — hepsi `bagla`/`hesapla` sınıfında) ② `Arac.fiil` alanı — `C1`'in *«her araç kendi fiilini beyan eder»* biçimi, yani eşleme **üçüncü bir tabloya** değil aracın kendi beyanına yazıldı ③ `plan_semasi` fiil kümesini **içe aktarma anında** kayda karşı doğruluyor: ayrışma varsa uygulama **ayağa kalkmaz**. ⚠ Metinler `plan_semasi`'nde kaldı ve gerekçesi yazılı: araç `ozet`leri MCP için yazılmış uzun metinlerdir, plan istemine dökmek `KURAL B`'yi çiğnerdi. **15/15 tam eşleşme.** Kapı `tests/test_d6_tek_yetenek_kaydi.py` (13) | `app/tools.py` · `app/plan_semasi.py` · `tests/test_d6_tek_yetenek_kaydi.py` | **§2.0 orkestratör** — *«tek yetenek kaydı»* |
| ✅ **D7** | Yetki denetimi (plan) | ⟳ **ÖLÇÜLDÜ (2026-08-12): BOŞLUK YOK.** Plan fiilleri gerçekten `Planlayici.calistir()`'den geçmiyor (`grep authorize` = 0) — **ama arkasında bir şey yok**: `SORGU` isteğin **zaten yetkilendirilmiş** servisini kullanır, ötekiler **koşmuş satırlar** üstünde saf dönüşümdür, `PANO` ise **YAZMAZ** (`pano_taslagi` döndürür; kalıcılaştırma onay akışının işi). *Bir kapının yokluğu ancak arkasında bir şey varsa boşluktur.* | 🔴 **GERÇEK DEĞİŞMEZ: çalıştırıcı SALT-OKUNUR ve idempotent** — ve o cümle yalnız bir **yorumda** duruyordu. Artık kapılı: `tests/test_d7_plan_salt_okunur.py` (5) — router ithali yok · yazma fonksiyonu adı geçmiyor · `PANO` taslak döndürüyor · `sorgu_kos` yalnız `SORGU` dalında (SAYARAK) | `app/plan_kosucu.py` · `tests/test_d7_plan_salt_okunur.py` | **§ güvenlik** |
| ✅ **D8** | Durdurma koşulu | ⟳ **ÖLÇÜLDÜ (2026-08-12): İKİ YARISI DA YAPILMIŞ — ve bu satır `§C2` ile AYNI İŞ.** Bu tablo aynı işi iki kez listeliyor (`C2` kartı *«ZATEN CANLI»* diye kapatmıştı); `D8`'in *«ÖNCE»* metni o ölçümden **önceki** hâli taşıyordu. Bugünkü ölçüm: `Butce(adim=**8** · saniye=**30,0** · sorgu=**12**)` — `sorgu` **uykuda değil**, `if b.sorgu and …` uygulanıyor ve tavan aşılınca `ButceAsimi` **fırlıyor**; `AZAMI_ADIM=12` `dogrula`'da **koşmadan önce**. | ✅ **Stall yarısı da tam:** `ONARIM_TAVANI = **2**` (Magentic-One *«stall ≤2»*) ve döngü **yeniden PLANLIYOR** — istem sınıf başına **çare** taşıyor (`ONARIM_YONERGESI`, `§B4`), yalnız *«tekrar dene»* demiyor; tavan dolunca **durur**. ⊙ İki kayıt tek işi anlatınca biri bayatlar: *bir görevin iki satırı varsa, ikincisi birincinin ölçümünü duymaz.* | `app/planner.py` · `app/plan_garson.py` · kapı `tests/test_c2_butce_stall.py` (8) | **§2.0** |
| ✅ **D9** | Metodoloji (kohort/funnel/YoY-oranı) | ❌ yok — plan fiilleri + şablon | ✅ **ÜÇÜ DE YAZILDI (2026-08-12)** — mekanizma `§B10`'da kurulmuştu, eksik olan **metinlerdi**. 🔴 Ve ikisi **zıt**: `huni.md` *«YAPILABİLİR»* der (ölçüldü: `firsat` küpü **zaten bir satış hunisi** — sinonimleri `huni`·`pipeline`, `asama` boyutu, gerçek aşama değerleri, `kazanma_orani_yuzde` ölçüsü); `kohort.md` *«İFADE EDİLEMEZ»* der (ölçüldü: kohort **ilk dönem** + **görece zaman** ister, küp sözleşmesinde ikisi de yok — veri var, **ifade gücü** yok). ⊙ `kohort.md`'nin tamamı bir *«yapamam ama şunu BEYAN et»* talimatıdır ve `§18.6`'da ölçülen kusuru hedefler (pivot, kohort diye teslim ediliyordu). 🔴 `huni.md`'nin en önemli satırı bir **sınır**: `asama` bugünkü aşamayı taşır, **dönüşüm oranı aşama geçmişi ister ve o yok** — anlık dağılımı dönüşüm diye sunmak sessiz-yanlıştır. ⏸ Bayrak `skills: off` **kalıyor** (açılış şartı `§26`, park); `KURAL B` kapıyla ölçülüyor. | `demo/skills/{yoy-orani,huni,kohort}.md` · kapı `tests/test_d9_metodoloji_skilleri.py` (11) | **yeni ADR** |

### 38.3 Cevap ve anlatı

| # | iş | **ÖNCE** | **SONRA** | dosyalar | MİMARİ.md |
|---|---|---|---|---|---|
| ✅ **D10** | Cevap biçimi | **karar yok** — `viz.analyze` + `interpret` + `_attach_next_steps` üçünün **artığı** (chip hep 6, olgu hep 1-2) | ✔ **chip sayısı soruya BAĞLANDI** (`app/bicim.py` karar tablosu, `niyet`in altı türü × beş kova; `4,6,2,4,4,4,6,3`). ⚠ *olgu sayısı* `D11`'de kalır — bu turda **1-5 arası zaten değişiyor** (§18'de *«hep 1-2»* idi) | `app/bicim.py` 🆕 · `app/answer.py` · `app/cube_router.py` | ✅ **§13.1.1 ADR-0024'e ek** yazıldı |
| ⏸ **D11** | Olgu üretimi | ⟳ **BİRİM DÜZELTİLDİ (2026-08-12):** 11 **çağrı yeri** ama **14 TİP** — hedef sanılan *«Pulse'un 14'ü»* tip ekseninde **zaten karşılanmış**. Canlıda **2-3** ateşliyor (curl) → gerçek mesafe **2-3 → 14** | Ateşlenmeyen koşullar genişletilir. ⏸ Sayaç tesisatı **PARK** (`A1` kaseti 21→50 olunca bedava gelir). ✅ Ölçüm sırasında çıkan gerçek kusur kapatıldı: `§D11-b` | `app/interpret.py` · `app/anlatici.py` | **§ yorum katmanı** ⟳ **KARAR:** **PARK, şartı `A1` kaseti 21→50 (`§40.9`)** — birim düzeltildi (11 çağrı yeri ≠ **14 tip**, canlıda 2-3). *«Hangi tip hiç ateşlenmiyor»* sorusu kaset büyüdüğünde **bedava** gelir; ayrı bir sayaç **iki sahipli** bir ölçüm olurdu (`KAT-1`). |
| ⏸ **D12** | Kök-neden yatay eksen | ⟳ **ÜÇ VAADİN BİRİ YAPILDI, BİRİ ÖLÇÜLÜP REDDEDİLDİ, BİRİ AÇIK** (2026-08-12): ✅ **JS sürprizi** `contribution.py:201 _surprizi_isle` + `:276 surpriz_notu` (kapı `test_e2_surpriz.py`) · ⊘ **Benjamini-Hochberg** `§E3`'te **ölçülüp reddedildi** — bu depoda **p-değeri yok**, eşik bir istatistik değil bir **karar**; yerine `stats.tarama_beyani` (kapı `test_e3_tarama_beyani.py`) · 🔴 **Adtributor** (`app/adtributor.py`) hâlâ **yok**, `§25 bileşik segment` layer-1'de kilitli | JS ✅ · BH ⊘ (ölçülü red) · Adtributor 🔴 | `app/contribution.py` · `app/stats.py` | **§KN bölümü** ⟳ **KARAR:** **PARK, şartı `§25` layer-1 (`§40.9`)** — üç vaadin ikisi kapandı (**JS sürprizi ✅** · **BH ⊘ ölçülü red**); kalan **Adtributor** bileşik segment kilidine bağlı, kilit açılmadan gireceği bir yer yok. |
| ✅ **D13** | Dış yüzey | `mcp_yuzeyi: off` · `agent_plan_secimi: off` | ✅ **MCP AÇILDI (`beta`, 2026-08-12)** — ve açılış bir dilek değil, **dört ölçülmüş şartın** karşılanmasıydı (`§C3`). 🔴 Son engel `§C3`'ün kendi cümlesiydi: *«`§C1` (tek yetenek kaydı) hâlâ `mcp_yuzeyi` açılışına bağlı»* — o borç **bu turda `§D6` ile ödendi** (15/15 fiil–araç eşleşmesi, içe aktarmada doğrulanıyor). ⚠ *«~20 araç eşiği»* korunmadı, **yerine geçildi**: OpenAI'ın asıl ölçütü sayı değil **ÖRTÜŞME**dir — ölçüldü, 31 aracın **29'u ayrık**, tek örtüşen çift `stats.trend`↔`stats.ozet` (tavan 10); sayı ikincil emniyet olarak 31 ≤ 35. *Bir vekil ölçüt kırmızı verirken asıl ölçüt yeşilse, değiştirilecek olan vekildir.* | 🟢 **CANLI DOĞRULANDI (curl, üç yön):** `GET /mcp/tools` → **200 · 31 araç · yazma aracı SIFIR** · `POST /mcp/call` → çalışıyor ve hem **enjeksiyon zarfını** (`<<<DIMA-VERI … DIMA-VERI>>>`) hem **makbuzu** (`arac`·`determinizm`·`sure_ms`) taşıyor · `dashboards.create` → **reddedildi** (*«Kayıtlı olmayan araç»*). ⏸ `agent_plan_secimi` **açılmadı** — ayrı bir ürün kararı. | `demo/packs/features.yml` · `app/mcp.py` · kapılar `test_c3_mcp_acilis_sartlari.py` · `test_mcp.py` | **§ MCP** |

### 38.4 🔴 DEĞİŞMEYECEKLER — bilerek

| ne | neden değişmiyor |
|---|---|
| **LLM SQL yazmaz** *(⚠ **KÜP YOLUNDA** — istisnası aşağıda)* | **9 bağımsız emsal** + lkr.dev %97↔%80 · Omni'nin **21 puanı**.<br>🔴 ⟳ **İSTİSNA YAZILDI (2026-08-12):** kural **küp yolu** için mutlaktır (Intent-JSON → CubeQuery → deterministik derleyici). Ama **Discovery/adhoc** yolunda LLM **ham SQL yazar** (`llm.generate_sql` · `llm.repair`) — bu bilinçli bir **son çare**dir (`CLAUDE.md`: *«istemediğimiz son çare»*) ve her ateşlenmesi bir **mutfak eksikliği raporudur**. ⊙ Bir dokunulmazlar listesi **kendi istisnasını gizleyemez**: gizlerse okuyan onu bir güvence sanır ve o güvence yanlış yerde işler. ⚠ İstisnanın **sınırı da kapılı** (`§⑧`, 2026-08-12): hiçbir tabloya dokunmayan bir Discovery SQL'i **cevap değildir** ve reddedilir — üretimden de, **onarımdan** da (`wren_service.veriye_dokunmuyor`, kapı `test_kapsam_disi_satir_uretmez.py`). |
| **Sayıyı her zaman küp koyar** | Zenlytic: *«this is the one part we will not make probabilistic»* |
| **Grafik kararı deterministik** (ADR-0024) | Veezoo etiketleri bile VQL'den render ediyor · canlı **10/10** |
| **Kapalı fiil/araç kümesi** | Cortex **%90+'ı sabit 6 aşamayla** alıyor · OpenAI eşiği *«10'dan az örtüşen araç»* |
| **`narration_guard`** | Nature: sıcaklık ↔ doğruluk **ölçülmüş ödünleşim** |
| **Beyan kültürü** | dbt: *«failure looks like an error message»* |
| **Türkçe morfoloji yatırımı** | Veezoo'nun dil kaması → **$6M**; pazarda **kimse morfolojiye dokunmamış** |

# ON BİRİNCİ KISIM — NE YAPMALIYIZ

## 14 · NE YAPMALIYIZ — adım adım uygulama planı

> 🔴 **Bu bölüm bir yol haritası değil, bir UYGULAMA PLANIDIR.** Her adımda: *ne
> yapılacak · hangi dosya · ÖNCE ne vardı → SONRA ne olacak · **nasıl curl ile
> doğrulanacak** · risk · geri alma · hangi belge güncellenecek.*

### 14.0 ÇALIŞMA PROTOKOLÜ — her adım için geçerli

**Doğrulama sırası (bağlayıcı):**

```
1. hedefli pytest (yalnız dokunulan dosya)     ~5-15 sn   ← serbest
2. docker tazele + CURL ile canlı doğrulama    ~2-3 dk    ← ASIL KANIT
3. bir sonraki adıma geç
…
N. demet bitince TEK tam kapı                  ~4 dk      ← yalnız BİR kez
```

🔴 **Adım aralarında kapı YOK.** Ölçülmüş bedel: beş kök için beş ayrı tam kapı ≈ **35 dk**;
aynı beş kök tek koşumla **7 dk**. *Beş kat maliyet, sıfır ek bilgi.*
⊙ **Curl asıl kanıttır**, kapı yalnız **gerilemediğini** gösterir.

**Her adımda güncellenecek belgeler:**

| belge | ne zaman |
|---|---|
| **`backend/MIMARI.md`** | 🔴 sorumluluk devri olan **her** adımda (§38'deki sütun) |
| `OPERASYON-DURUM.md` | her adım sonunda: ne bitti, ne açık kaldı |
| `belgeler/denetim/2026-08-07_CEVIRI-SOZLESMESI.md` | **her curl turu** — soru, cevap, teşhis |
| `backend/CLAUDE.md` | yalnız bir **kural** değişirse |
| bu rapor (§38) | ÖNCE/SONRA satırı gerçekleşince ✅ işaretlenir |

**Her adımın çıkış ölçütü (üçü birden):**
1. Curl ile **en az 3 senaryoda** yeni davranış görüldü
2. **KURAL B**: bayrak kapalıyken davranış **bayt bayt** eski
3. `MIMARI.md` + `OPERASYON-DURUM.md` güncellendi

---

### 14.1 SIRA VE BAĞIMLILIK

```
FAZ 0 (ölçüm — kod değişikliği YOK)
   A1 garson korpusu ──┬──────────────────────────────┐
   A2 cevapsız metriği │                              │
   A3 şişme beyanı     │                              │
                       ▼                              ▼
FAZ 1 (garsonu besle)                          FAZ 3 (cevap biçimi)
   B1 şema daraltma ──► B2 VQR few-shot           D1 olgu sayacı
                        B3 instructions.md        D2 taksonomi aç
                        B4 reflect+repair         D3 biçim kararı
                              │
                              ▼
FAZ 2 (yetenek birleştirme)              FAZ 4 (kök-neden)
   C1 FIIL←tools türetimi                   E1 Adtributor
   C2 bütçe+stall                           E2 JS sürprizi
   C3 MCP aç                                E3 FDR
```

🔴 **FAZ 0 pazarlık dışıdır.** Ölçüm olmadan FAZ 1'in işe yarayıp yaramadığı **bilinemez** —
ve bu raporun tamamının teşhisi tam olarak budur.

---

## FAZ 0 · ÖLÇÜM — kod değişikliği yok, 2-3 gün

### ⟳◐ A1 · Garson korpusu — **KORPUS VAR; ama «BAĞLI» ≠ «KOŞUYOR» (⟳ 08-12)**

> 🔴🔴 **08-12 DENETİMİ — İKİ AYRI KUSUR.**
>
> **① «Bağlandı» ile «koşuyor» aynı şey değil.** Ölçüldü: adım `ADIM_ANAHTARLARI`'nda
> **ama** `YEREL_KAPI=('korpus','gercek')` içinde **yok** → yerel kapıda hiç koşmuyor;
> `--hepsi`'de `_garson_korpusu_kosulabilir()` env'siz **False** döndüğü için **düşüyor**.
> Yani adım *«bağlı»* ama **hiçbir olağan koşumda çalışmıyor**.
>
> **② Diskteki artefakt tabana göre KIRMIZI — ve sebebi yazmıyordu.** Rapor `18/21`
> yayınlıyor; en yeni artefakt (08-12 10:58) `11/21` (taban **17**).
>
> ⊙ **TEŞHİS — deterministik yol hiç bozulmamış:**
>
> | basamak | taban | artefakt | fark |
> |---|---|---|---|
> | `route` | 9 | **9** | **0** ← deterministik |
> | `sosyal` | 1 | **1** | **0** ← deterministik |
> | `garson` | 4 | 2 | **−2** ← LLM |
> | `orkestra` | 4 | 0 | **−4** ← LLM |
> | `netlestirme` | 3 | 9 | **+6** |
>
> Toplam korunmuş (21). **Yalnız LLM'e bağlı iki basamak çökmüş ve farkın tamamı
> netleştirmeye gitmiş** — bu bir **KASET ISKASI imzasıdır**, bir ürün gerilemesi değil.
>
> ✅ **ONARIM:** `kapi()` bir ıskada bile kırmızı veriyordu (`lab/garson_korpusu.py:345`)
> **ama `rapor()` `iska`'yı hiç almıyordu** → sayı artefakta ulaşmıyor, okuyan ayırt
> edemiyordu. Artık `rapor(sonuc, iska=)` ve artefakt ya *«🔴 KASET ISKASI: N — bu turlar
> ölçülmedi»* ya *«✅ ıska yok — sayılar bir ürün ölçümüdür»* satırını taşıyor.
>
> *Bir ölçümün kırmızısı, sebebini taşımıyorsa bir alarm değil bir muammadır.*


> 🔴 **KARTIN VARSAYIMI YANLIŞ: `lab/garson_korpusu.py` YAZILMIŞ** (16.765 bayt,
> **21 kayıtlı vaka** — çok turlu zincirler, Arapça, sosyal, kök-neden, çapraz-küp),
> `lab/garson_korpus_baseline.json` tabanı ve `lab/reports/garson_korpusu.md` raporu
> **var**. Kart onu *«SONRA yazılacak»* diye tarif ediyor.
>
> ⊙ `§12.12`'nin *«yazılmış ama bağlanmamış»* deseninin **SEKİZİNCİ** örneği — ve bu kez
> **kapının kendisinde**: `grep garson_korpusu lab/kapi.py tests/` → **sıfır** eşleşme.
> `§1.4`'ün *«garson HİÇBİR TOPLU KOŞUMDA YOK»* şikâyetinin sebebi buydu. Kapının yazılı
> gerekçesi (*«`--live` ister, kotaya bağlı»*) **canlı koşucu** (`lab/garson.py`) içindir;
> kasetli korpus kendi docstring'inde *«her demet sonunda, **SIFIR API**»* diyor.
>
> 🔴 **NEDEN KOŞAMIYOR — üç engel, hepsi ORTAM (ölçüldü):**
>
> | # | engel | ölçüm |
> |---|---|---|
> | ① | **Kimlik kaynağı yanlış dosyada** | Canlı konteynerin `/app/logs`'u bir **docker volume** (`dima_logs`); tohumlanmış kullanıcılar (`demo-boyahane@usedima.com`) **orada**. Repodaki `logs/dima.db` **bayat kopya** (yalnız `owner@dima.local`), varsayılan yapılandırmanın gösterdiği `logs/control_plane.db` ise **root sahipli, ürünün hiç kullanmadığı** bir artefakt |
> | ② | **Rapor dosyası root sahipli** | `lab/reports/garson_korpusu.md` → korpus **sonuna kadar koşuyor** ve son satırda `PermissionError` ile düşüyor. *İş yapılır, ürünü atılır.* |
> | ③ | **Kaset kurulamıyor** | Sağlayıcı `NoLlmGenerator` → yamalanacak `_chat`/`_ask` yok → araç **canlı** koşmaya çalışıyor ve `--network none` altında çöküyor (`kaset: 0 isabet · 0 ıska`) |
>
> 🟢 **DOĞRULANDI:** canlı DB'nin bir **kopyasıyla** (`docker cp` + `DIMA_DATABASE_URL`)
> giriş **çalışıyor** ve korpus soruları koşuyor — yani engel tasarımda değil **ortamda**.
>
> ✅ **BU TURDA YAPILAN:** araç artık **üç ön koşulun üçünü birden**, onarım komutlarıyla
> **tek seferde** beyan ediyor (`_ortam_kusuru_beyan_et`, `main()`'in ilk satırı).
> ⚠ İlk yazımda denetimi `_giris()`'e koymuştum ve **hiç ulaşılamıyordu**: şema hizalaması
> uygulama ayağa kalkarken patlıyordu. *Bir kapının yeri, koruduğu şeyden önce olmalıdır.*
>
> ✅ **KAPANDI (2026-08-12) — ÜÇ ENGEL DE ÖLÇÜLDÜ, ADIM TOPLU KOŞUMA BAĞLANDI.**
>
> | engel | çözüm | ölçüm |
> |---|---|---|
> | ① kimlik kaynağı | `docker cp` + `DIMA_DATABASE_URL` | giriş **çalıştı** |
> | ② root sahipli rapor | dosya `lab/reports/` (**gitignore'lu artefakt dizini**) — kenara alındı, `sudo` gerekmedi | rapor **yazıldı** |
> | ③ kaset kurulamıyor | sağlayıcı **kimliği** gerekiyormuş: anahtar `model`i de taşıyor | `0 isabet` → `0/106 ıska` → ✅ **`36 isabet · 0 ıska`** |
>
> 🔴 **VE ASIL SEBEP ③ DEĞİLDİ — BİR MİRAStı.** `lab/kapi.py`'nin dışlama gerekçesi
> (*«`--live` ister, kotaya bağlıdır, **BELİRLENİMSİZDİR**»*) **canlı koşucu**
> `lab/garson.py` için yazılmıştı; kasetli korpus `--network none` altında koşuyor ve
> hiçbir maddesi ona uymuyor. Blok başlığı *«garson»* deyince ikisi tek şey sanıldı.
>
> > *Bir sınıfın ilk üyesi için yazılmış gerekçe, ikinci üyeye sessizce miras kalır.*
>
> ✅ **BAĞLANDI:** `ADIM_ANAHTARLARI` + `adimlar` (`lab/kapi.py`), ve ortam eksikse
> **düşürülür ama YAZILIR** — yeni `ORTAMA_BAGLI_ADIMLAR` (koşul · ne kaybedilir ·
> reçete). Üçüncü yol seçildi: koşturmak ortam eksiğini **ürün kusuru** gibi kırmızıya
> çevirirdi (`§F8` hijyeni), sessizce atlamak yeşil özeti **yalancı** yapardı
> (`ADR-0020`). Kapı: `tests/test_a1_garson_korpusu_bagli.py` (6) — adım kayıtlı ·
> komut/anahtar **sayısı eşit** · `TOPLUDA_YOK`'ta değil · koşul **gerçekten** ortama
> bakıyor (sağlayıcı silinince `False`) · bildirim **iki listeyi de** okuyor · kaset+taban
> commit'li.
>
> 📊 **İLK BAĞLI ÖLÇÜM:** `route 9 · garson 6 · orkestra 3 · sosyal 1 · netleştirme 2 ·
> payda 21 · boş 1` — cevaplanabilirlik **18/21** (taban 17). ⊙ Garson basamağı artık
> **görünüyor**: taban günü 4, bugün **6**.
>
> ⏭ **KALAN:** kaset 21 → ~50 vakaya büyütülecek (`§14.13`'ün düzeltmesi: 300-500 değil
> **50 ile başla**).

### A1 · Garson korpusu

| | |
|---|---|
| **ÖNCE** | Garson trafiğin **%37'sini** taşıyor; ölçümü **21 senaryoluk kayıt kümesi** (`lab/reports/garson_korpusu.md`, kendi notu: *«kayıt kümesi — korpus % değil»*). `lab/kapi.py:375`: *«garson HİÇBİR TOPLU KOŞUMDA YOK»* |
| **SONRA** | `lab/garson_korpusu.py` — **300-500 etiketli soru**, `(soru → beklenen küp · ölçü · kırılım · dönem)`. Çıktı: `doğru_küp` · `doğru_ölçü` · `doğru_kırılım` · **`cevapsız`** · `netleştirme` |
| **dosyalar** | yeni `lab/garson_korpusu.py` · `lab/kapi.py` (yeni adım) · `lab/reports/garson_korpusu.md` |
| **veri kaynağı** | 🔴 **uydurma soru YAZMA** — `interaction_log`'daki **3.554 gerçek etkileşim** var. `source=cube+llm` ve `source=None` olanlardan örnekle |
| **etiketleme** | Elle. ⚠ Anthropic'in ölçümü: *«LLM'e metrik tanımı ürettirmek **net-negatifti**… **insan-küratörlü** katman kazandı»*. **Etiketi LLM'e ürettirme.** |
| **curl doğrulama** | Korpus koştuktan sonra **rastgele 10 vakayı** curl ile tekrarla — korpusun raporladığı ile canlının verdiği **aynı mı**? ⊙ *Ölçüm aracı bu oturumda **dört kez** yalan söyledi (§21.8, §2, §19.7); araca da bir kapı gerekir.* |
| **risk** | ⚠ **Payda kirlenmesi.** Belirsiz sorularda tek bir `gold` yanlıştır — **AmbiQT** deseni: altın cevap bir **KÜME** olmalı |
| **geri alma** | yok (yeni dosya, mevcut yolu etkilemez) |
| **MİMARİ.md** | *«§ ölçüm»* — garson korpusunun tanımı ve paydası |

### ✅ A2 · `cevapsız` birinci sınıf metrik — **TAMAMLANDI (2026-08-11)**

> 🟢 **UYGULANDI VE CANLI DOĞRULANDI.** `lab/nl_corpus.py::kapi_degerlendir` üç satırlık
> manşet basıyor; `lab/kapi.py::_son_anlamli` üçünü de özete taşıyor (öncesinde **son**
> işaretli satırı seçiyordu ve yeni iki satır **düşerdi** — ölçüm eklendiği hâlde
> görünmezdi).
>
> **Ölçülen manşet:**
> ```
> TOPLAM doğru-cube: %95.1 (taban %94.4) ✅
> 🔴 cevapsız: 2980/14957 (%19.9) — cevap yok · kullanıcı durdurmadı · Discovery koşmadı
> semantik vaka: 554/590 (%94) · ham tur: 14957 (şişme 25.4×)
> ```
> ⊙ Raporun `§1.2` tablosuyla **birebir** (%19,9 · 590 vaka · ~25×).
>
> ⚠ Bir **eşik değil görünürlük** satırı: kapıyı kırmızı yapmaz (aksi hâlde bugünkü
> %19,9 anında kırmızı olur ve kapı kullanılamaz hâle gelirdi). Gerileme kapısı
> `doğru-cube` ve `sessiz_yanlış`ta kalır. Kapı: `tests/test_a2_cevapsiz_manset.py` (4).
>
> **Curl (altı zayıf prompt):** bugün **2/6** cevapsız — *«işler iyi mi»* · *«kısaca
> özetle»*. Rapor 3/6 ölçmüştü; *«bu ay ne oldu»* artık cevaplanıyor. ⚠ Sebep
> **izole edilmedi**, B2'nin kazancı diye iddia edilmiyor.

### A2 · `cevapsız` birinci sınıf metrik

| | |
|---|---|
| **ÖNCE** | Korpusta **%19,9**, canlıda **%21,8** — **kapı manşetinde YOK**. Manşet `doğru=95` diyor ve bu **SQL üretebilmiş** turların oranı |
| **SONRA** | Kapı özeti: `doğru=… · **cevapsız=…** · netleştirme=… · sessiz_yanlış=… · payda=…` |
| **dosyalar** | `lab/nl_corpus.py` · `lab/kapi.py` |
| **curl** | 6 zayıf prompt (*«işler iyi mi»*, *«bu ay ne oldu»*, *«kısaca özetle»* dâhil) → kaçı cevapsız? **Bugün 3/6** |
| **risk** | yok — yalnız raporlama |
| **MİMARİ.md** | *«§ test kapısı»* — manşet tanımı |

### ✅ A3 · Şişme katsayısını beyan et — **TAMAMLANDI (2026-08-11)**

> 🟢 A2 ile **aynı manşette**: `semantik vaka: 554/590 (%94) · ham tur: 14957
> (şişme 25.4×)`. `KURAL A` gereği ham payda **korunur** — geçmiş tabanlar ona bağlı;
> semantik payda **yanına** yazıldı, yerine değil.

### A3 · Şişme katsayısını beyan et

| | |
|---|---|
| **ÖNCE** | *«payda=2286»* · *«14.957 tur»* — gerçekte **590 semantik vaka**, şişme **~25×** |
| **SONRA** | Manşet: *«**590 semantik vakada** %95»*; ham tur sayısı **parantezde** |
| **dosyalar** | `lab/nl_corpus.py` · `OPERASYON-DURUM.md` |
| **risk** | ⚠ **Tarihsel taban kırılır.** `KURAL A` gereği ham payda **korunur**, yanına semantik payda **eklenir** |

### A4 · Kurulum süresi ölçümü

| | |
|---|---|
| **ÖNCE** | ❌ hiç ölçülmüyor |
| **SONRA** | *«sıfırdan bir müşteri paketini ayağa kaldırıp ilk doğru cevabı almak: **kaç saat**»* — ölçülüp yazılır |
| **neden** | Zenlytic: *«**Weeks. Sometimes months.** That setup tax is why we've mostly worked with large enterprises»* · rakipler **«7 gün»**, DBTalk **«30 dakika»** satıyor |
| **dosyalar** | `belgeler/` yeni ölçüm notu |
| **risk** | 🔴 **Sonuç kötü çıkabilir — ve o zaman ürün stratejisi değişir.** Bu bir risk değil, **ölçümün amacı** |

> ⟳⏸ **KARAR YAZILDI (2026-08-12) — FAZ 0'ın TEK İŞARETSİZ KALEMİYDİ.** Bir denetim
> ajanı bunu bulgu olarak bildirdi: kalem raporda **iki kez** geçiyor, `§0.6` karnesi
> `🔴 YOK` diyor, ama **hiçbir karar yazılmamıştı** — ve `§40`'ın kendi kuralı
> *«bir «değerlendir» maddesi, değerlendirilip kararı YAZILMADIKÇA kapanmaz»* diyor.
>
> **Ölçülebilen yarısı BUGÜN ölçüldü:**
>
> | ne | ölçüm |
> |---|---|
> | kaynak paketi | **3** (`logo-3` · `mikro-v16` · `netsis`) |
> | paketlenmiş şirket | **4** (`atiksan` · `demo-boyahane` · `gitas` · `gulteks`) |
> | `compose_and_build` (pack → derlenmiş proje) | **4,66 sn** |
> | keşif/taslak makinesi | `db_introspect.py` **7** fonksiyon · `mdl_writer.py` **11** |
>
> ⊙ Yani **makine tarafı saniyeler sürüyor** — ve kartın sorduğu şey bu değil.
> Kartın sorusu *«ilk DOĞRU cevaba kaç saat»* ve o sürenin baskın bileşeni **insan
> emeği**: katalog düzeltme, sinonim kurma, ölçü doğrulama.
>
> ⏸ **PARK — şartı GÖZLENEBİLİR:** *bir sonraki gerçek müşteri kurulumu **zamanlanarak**
> yapılır* (paket seçimi → bağlantı → keşif → katalog düzeltme → ilk doğru cevap; her
> adım damgalanır). Bugün ölçülemez ve **geriye dönük de kurtarılamaz**: dört şirket
> zaten paketlenmiş ama **hiçbirinin süre kaydı yok**.
>
> 🔴 **Ve neden UYDURULMUYOR:** bu sayı rakiplerin *«7 gün»* / *«30 dakika»* iddialarına
> karşı yayımlanacak. `§F8`'in kuralı gereği ölçülmemiş bir kurulum süresi yayımlamak,
> tam da eleştirdiğimiz şeyi yapmak olurdu. *Rakibin pazarlama sayısına, kendi
> pazarlama sayınla cevap vermek bir ölçüm değil bir müzayededir.*
>
> ⚠ Kartın *«risk»* satırı yerinde duruyor: sonuç kötü çıkarsa strateji değişir — ama
> **ölçülmeden** hiçbir strateji değişmez.

---

## FAZ 1 · GARSONU BESLE — en yüksek getiri, 1-2 hafta

### ✅ B1 · Şema daraltma — **TAMAMLANDI (2026-08-11)**

> 🟢 **UYGULANDI VE CANLI DOĞRULANDI.** `cube_router.daraltma_adaylari` (karar) ·
> `katalog_metni.build_catalog(…, metin_kupleri=)` (yalnız **metin** budar) ·
> `metin_ve_indeks(…, soru=)` (bayrak burada çözülür — o fonksiyonun kendi gerekçesi) ·
> `ask.py` garson dalı `soru=body.question` geçer. Bayrak `sema_daraltma`.
>
> **Ölçülen kazanç (canlı `demo-boyahane`, tam katalog 23 küp / 23.729 karakter):**
>
> | soru | budanmış | tasarruf |
> |---|---|---|
> | *«ciro ve duruş»* | **3/23 küp · 4.168 krk** | **%82** |
> ⟳ 🔴 **08-12:** bu satır **2.343 krk / %90** yazıyordu ve iki **farklı katalog kipini** karşılaştırıyordu: payda üretim kipinde (`sozluk=True`, `katalog_sozlugu: beta` — 23.729 kr, birebir doğru), pay ise **sözlüksüz** kipte ölçülmüştü. Aynı soru üretim kipinde **4.168 kr / %82** veriyor. *İki farklı kiple ölçülen bir oran, bir kazanç değil bir kip farkıdır.*
> | *«makine bazında oee»* | 10/23 · 6.886 | **%71** |
> | *«ram 3 makinesinin verimliliği»* | 10/23 · 6.886 | **%71** |
> | *«en çok ciro yapan 5 müşteri»* | 9/23 · 6.118 | **%74** |
> | *«kalite durumunu özetle»* | **fail-open** | — |
>
> **Curl (kartın üç senaryosu):** ① katalog karakteri **ölçüldü ve kütüğe basılıyor**
> (`§B1 şema daraltma: 3/23 küp — sorunun her içerik sözcüğü katalogda`) ② *«makine
> bazında oee»* → `cube=oee`, 11 satır, **gerileme yok** ③ **çapraz-küp** *«ciro ve
> duruş»* → budama 3 küpe indi ve garson yine **`makine_duruslari`**'nı seçti.
>
> 🔴 **İKİ DEĞİŞMEZ — ikisi de ölçümle doğdu:**
> ① **İndeks ASLA budanmaz.** `build_catalog`'un kendi sözleşmesi: metin sağlayıcıya
> gider, **indeks `parse_cube_query`'nin beyaz listesidir**. İndeks de budansaydı fiş,
> *anlatım tercihiyle daraltılmış* bir doğrulama sınırına karşı sınanırdı.
> ② **Fail-open bir SAYIYA değil KANITA bağlı.** Kartın *«aday <2»* kuralı **ölçüldü ve
> yetmedi**: *«kalite durumunu özetle»*de aday **7** idi ama doğru küp aralarında yoktu.
> Kanıt: *sorunun her **içerik** sözcüğü, **tuttuğumuz** küplerle açıklanabiliyor mu?*
>
> **Güvenlik ölçümü:** sekiz garson sorusunda *«budanmış küme garsonun GERÇEKTEN seçtiği
> küpü içeriyor mu»* → **8/8 kapsandı · 0 kayıp**. Kapı: `tests/test_b1_sema_daraltma.py`
> (8) + katalog/garson gerileme yüzeyi **103 yeşil**.
>
> ⚠ **`extract_by` KULLANILMADI — ve bu bir ölçüm sonucudur.** Kart onu öneriyordu; canlı
> konteynerde ölçüldü: `extract_by` **model/view** budar (ilişkileri koruyarak), garson
> istemi ise **küplerden** kurulur. İkisi aynı şey değil. `extract_by`'ın yeri SQL
> derlemesidir → `F10`/`B8`.
>
> ⚠ **Rapordan bilinçli sapma:** kart *«varsayılan `off`»* diyor; demo paketinde `beta`
> açıldı çünkü 8/8 kapsama ölçüldü ve fail-open kanıta bağlı. 🔴 **Geniş yayılımın ön
> koşulu `A1` (garson korpusu)** — kapı `route()`u ölçer, garsonu ölçmez; bu bayrağın
> gerilemesi kapıda **görünmez**.
>
> ⚠ **Bir kusuru kapı yakaladı:** kapsama ölçütü ilk yazımda salt `partial_unknowns`'un
> listesiydi ve o liste **küp-düzeyi** sinonimleri kapsama saymıyor → *«ciro ve durus»*
> yalın fikstürde fail-open'a düşüyordu. Ölçüt *«**tuttuğumuz** küplerin açıkladığı
> kelimeler»*e çevrildi. ⊙ Canlı katalogda görünmüyordu; **yalın fikstür** gösterdi.

### ⏳ B1 ÖN KOŞULU · aday seçici ölçüldü ve onarıldı **(2026-08-11)**

> 🔴 **BUDAMAYA GEÇMEDEN ÖNCE ADAY SEÇİCİ ÖLÇÜLDÜ — ve güvenilir DEĞİLDİ.**
> Kartın *«aday seçimi `ilgili_cubelar` **zaten var**»* satırı doğru ama **yeterli
> değildi**. Ölçüm (canlı katalog, `demo-boyahane`, 23 küp / **23.729 karakter** —
> `§4.2`'nin sayısı **birebir** doğrulandı):
>
> | soru | aday | 🔴 sorun |
> |---|---|---|
> | *«kalite durumunu özetle»* | 6 küp | **`kalite` YOK** — canlı cevap o küpten geliyor |
> | *«ciro ve duruş»* | 1 küp (`parti`) | `makine_duruslari` **yok** — kartın 3. curl senaryosu |
> | *«bu yıl toplam ciro»* | 1 küp | fail-open tetiklenir, **kazanç olmaz** |
>
> ⚠ **Ve fail-open bu vakayı KURTARMIYOR:** *«kalite durumunu özetle»*de aday sayısı
> **7**'dir (yani `<2` kuralı devreye girmez) ama doğru küp aralarında değildir →
> garsona **ihtiyacı olan küpün bulunmadığı** bir katalog giderdi. Bu, kartın kendi
> 🔴 risk satırının (*«yanlış budama = kapsam kaybı»*) ölçülmüş hâlidir.
>
> **KÖK BULUNDU — ve bir sinonim eksikliği değil, bir `KAT-1` ihlali:**
> `ilgili_cubelar` yalnız **elle yazılmış** `synonyms` listesine bakıyor; küpün adı
> `name:` alanında **zaten beyanlı** olduğu hâlde ikinci kez oraya kopyalanmayı bekliyor.
> Ölçüldü — **39 küp beyanının 12'sinde (%31) ad eksik**, `ticaret` **dört şirkette
> birden**:
>
> | şirket | küp | adı var | 🔴 eksik |
> |---|---|---|---|
> | demo-boyahane | 23 | 16 | 7 (`kalite`·`bakim`·`makine_duruslari`·`ticaret`·`enerji_*`) |
> | atiksan | 4 | 3 | 1 (`ticaret`) |
> | gulteks | 5 | 3 | 2 (`mal`·`ticaret`) |
> | gitas | 7 | 5 | 2 (`mal`·`ticaret`) |
>
> ✅ **Çözüm katalogdan TÜREV** (`cube_router._kup_adi_belirtecleri`) — 12 sinonimi elle
> yazmak kusuru değil **bir örneğini** kapatırdı. ADR-0008 ihlali yok (yeni sözlük değil,
> katalog türevi). Dolgu/sosyal süzgeci **yukarıda** olduğu için yanlış pozitif üretmez.
>
> **Ölçülen sonuç:** *«kalite durumunu özetle»* → `kalite` **artık aday** ·
> *«ciro ve duruş»* → `oee · parti · makine_duruslari` (**3. curl senaryosu artık geçer**) ·
> *«bakım maliyeti»* → `bakim` · *«ticaret hacmi»* → `ticaret` · *«teşekkürler»* → **0 küp**.
> Kapı: `tests/test_kup_adi_belirteci.py` (6) + netleştirme/sosyal yüzeyi **94 yeşil**.
>
> ⚠ **Ölçüm aracı bu adımda İKİ kez yanılttı:** ① `[:6]` dilimi 7. küpü (`kalite`) gizledi
> ② `ilgili_cubelar` **normalize girdi bekler**, ham metin verince `bakım`/`duruş`
> ıskalanıyor gibi göründü. İkisi de sahte kusurdu. *Basılmayan alan, olmayan alan gibi
> okunur.*
>
> ⏭ **B1'in kendisi (budama) SIRADAKİ ADIMDIR** — artık güvenilir bir aday seçici üstünde.

### B1 · Şema daraltma (schema linking)

| | |
|---|---|
| **ÖNCE** | `katalog_metni.metin_ve_indeks(schema, principal)` → **23 küpün tamamı, 23.729 karakter**, **her soruda** garsona gidiyor |
| **SONRA** | Soruya göre **budanmış manifest**. Motor bunu **zaten yapıyor**: `wren_core.ManifestExtractor.extract_by()` — *«kullanılan veri kümesi listesine göre manifest'i daralt; **ilişkili modelleri ve ilişkileri KORU**»* |
| **dosyalar** | `app/katalog_metni.py` · `app/wren_service.py` · `app/routers/ask.py` |
| **aday seçimi** | `cube_router.ilgili_cubelar(q, schema)` **zaten var** → ilk 2-3 küp + `measure_cube_candidates` |
| **dış dayanak** | şema bağlama hatası: Spider 2.0 **%27,6**, MultiSpider 2.0 **%33,0** · Pinterest tablo arama **%40→%90** · *«Systems often fail **BEFORE** SQL is generated»* |
| **curl (3 senaryo)** | ① *«bu yıl toplam ciro»* → katalog **kaç karakter** gitti (log) ② *«makine bazında oee»* → doğru küp hâlâ geliyor mu ③ **çapraz-küp**: *«ciro ve duruş»* → budama **iki küpü de** korudu mu |
| 🔴 **risk** | **Yanlış budama = kapsam kaybı.** Aday listesi eksikse garson doğru küpü **göremez** |
| **azaltma** | **Fail-open**: aday **<2** ise **tam katalog** gönder. Bayrak: `sema_daraltma` (varsayılan `off`) |
| **geri alma** | tek bayrak |
| **MİMARİ.md** | **§3** — *«katalog metni artık soruya göre daraltılmış üretilir; fail-open»* |

### ✅ B2 · VQR → garson few-shot — **TAMAMLANDI (2026-08-11)**

> 🟢 **UYGULANDI VE CANLI DOĞRULANDI.** `vqr.few_shot_block(…, guvenilir=True)` +
> `vqr.garson_ornekleri()` + `company_registry.vqr_ornek_icin()` + bayrak `vqr_few_shot`.
> `ask()`'e **iki satır** girdi (muafiyet `b2-garsona-few-shot`, Δ=2).
>
> **Ölçülen kazanç (curl, tek tek):** *«ram 3 makinesinin verimliliği ne durumda»*
> **11 satır / ilk satır `ÖRGÜ HAT` (süzgeç yok)** → **1 satır / `RAM-3` · `ort_oee
> 0,518`**. Üç garson sorusunun üçünde de blok eklendi (242 · 273 · 160 karakter =
> katalogun **~%1'i**). VQR'da olmayan soru ve route'un cevapladığı soru: **blok yok,
> gerileme yok**.
>
> 🔴 **VE UYGULARKEN İKİNCİ BİR KÖK ÇIKTI — `§12.12`'nin ALTINCI örneği:**
> `settings.vqr_acik = **False**` olduğu için `vqr_for_request()` **her istekte `None`**
> dönüyordu. Yani VQR'ın **tamamı** (23 kayıt, **8'i insan onaylı**) kullanılmıyordu:
> `/verify` sessizce `stored:false` diyor, garson few-shot'ı ateşlemiyor ve
> **Discovery'nin kendi few-shot'ı da ölüydü**. ⊙ Ve o anahtarın `config.py`'de
> **yazılı gerekçesi yok** — o dosyadaki her ayarın gerekçesi varken.
> ⚠ Çözüm anahtarı açmak **değil**: `vqr_acik` **tekrar oynatma** anahtarıdır ve
> `vqr.py:136` iki riskin **aynı kapıdan geçmemesi** gerektiğini zaten yazmış
> (replay yarıçapı **TAM**, few-shot **dolaylı**). Ayrı erişimci: `vqr_ornek_icin`.
>
> **Kapı:** `tests/test_b2_garson_few_shot.py` (5 test) — insan onaylı süzgeç · yalnız
> güvenilmez kayıt varsa boş · erişimcinin replay anahtarından bağımsızlığı · `KURAL B` ·
> `_cube_select_system` imzasının değişmediği.

### B2 · VQR → garson few-shot 🔴 EN YÜKSEK GETİRİ — **ve sanılandan ÇOK daha ucuz**

| | |
|---|---|
| 🔴 **ÖNCE (ölçüldü, düzeltme)** | `vqr.few_shot_block(question, k=3)` **ZATEN YAZILMIŞ VE ÇALIŞIYOR** (`app/vqr.py:449`, `recall()` üstünde, DAIL-SQL deseni). Ama `ask.py:5135`'te **yalnız Discovery dalına** bağlı — yani trafiğin **%1,7'sine**. 🔴 **Trafiğin %37'sini taşıyan GARSONA hiç bağlanmamış**; `llm.py::_cube_select_system` içinde *«few_shot»* kelimesi bile **geçmiyor** |
| **SONRA** | Aynı fonksiyon garson dalında da çağrılır; blok `catalog_text`'in yanına eklenir |
| **dosyalar** | `app/routers/ask.py` (garson dalı, ~`3947`) · `app/llm.py::_cube_select_system` (bloğu kabul etsin) |
| 🟢 **maliyet** | **Yeni retrieval yazılmayacak.** Tahmini **3-10 satır** + bir bayrak. ⊙ *Planın ilk hâli «`vqr.ara()` yaz» diyordu — denetim bunu çürüttü.* |
| **dış dayanak** | Cube: **+17…+23 puan**, *«**hangi model olduğu değil, semantik belgenin olup olmadığı** belirleyici»* — **4 KB markdown**'dan · Snowflake'in **Context Enrichment** ajanı birebir bu · Fabric kaynak başına **100 örnek** |
| ⚠ **kritik uyarı** | **Anthropic'in negatif ablasyonu**: ham SQL geçmişine grep erişimi doğruluğu **bir puandan az** oynattı — *«bilgi oradaydı, ajan gördü, **yine de kullanmadı**; darboğaz erişim değil **YAPI**»*. ⊙ **«Her şeyi ver» değil, «az sayıda, yapılandırılmış, İNSAN ONAYLI örnek ver».** `few_shot_block`'un `k=3` varsayılanı **zaten doğru** |
| **curl (4)** | ① VQR'da **olan** bir soruyu benzer biçimde sor → doğru fiş ② VQR'da **olmayan** → gerileme yok ③ **çelişkili** iki örnek → ne oluyor ④ istem **kaç token** büyüdü |
| 🔴 **risk** | **Bağlam kirlenmesi.** Hex'in ölçümü: *«çelişkili bağlam modeli bir **çöküş moduna** soktu»* — 30 dk eylemsiz salınım |
| **azaltma** | `vqr.py:136`'nın **kendi notu** zaten uyarıyor: *«TEKRAR OYNATMA (`near_exact`) ile ÖRNEK GÖSTERME (`few_shot_block`) **AYNI RİSKTE DEĞİLDİR**»* → `k≤3` koru · yalnız `user_verified`/`chip_approved` · çelişkide **hiç örnek verme** |
| **geri alma** | bayrak `vqr_few_shot` (🆕 yeni) |
| **MİMARİ.md** | **§4** — *«garson few-shot alır; kaynak insan onaylı VQR; `few_shot_block` iki dalda da kullanılır»* |

### B3 · `instructions.md` — iş sözlüğü

| | |
|---|---|
| **ÖNCE** | ⟳ **ÖLÇÜLDÜ (2026-08-12) — «YER YOK» YANLIŞ; YER VAR, TÜKETİCİSİ EKSİK.** `business_rules` mekanizması **kurulu ve bağlı**: `wren_service.py:1008` (`_load_knowledge("rules")`) → `schema["business_rules"]` → `llm.py:225`. ⚠ Ama **yalnız Discovery'nin SQL istemine**; garsonun istemi `_cube_select_system(catalog)` **yalnız katalog** alıyor (`ast` ile doğrulandı — imzada tek parametre). *Raporun «ters yatırım» bulgusunun kaldıracı tam burada duruyor.* |
| ⚠ **VE MEVCUT İÇERİK GARSONA UYMUYOR** | `knowledge/rules/*.md`'in içeriği **SQL semantiği** (oran = SUM/SUM) ve **kaynak şema** bilgisi (Logo `TRCODE`/`IOCODE`). Garson **SQL yazmaz, küp seçer** — bu metni onun istemine boşaltmak, kaldıraç değil **gürültü** olurdu. *Bir bağlamı doğru yere taşımak, onu her yere taşımak değildir.* |
| **SONRA** | ① `_cube_select_system`'e **küp-seçimi düzeyinde** iş tanımı yüzeyi (mevcut `business_rules` kanalı **yeniden kullanılır**, ikinci bir mekanizma açılmaz — `KAT-1`) ② `demo/packs/<sektor>/instructions.md` o yüzeyin içeriği |
| 🔴 **AMA ÖLÇÜLEN SOMUT KUSUR BUNUNLA ÇÖZÜLMÜYOR** | *«bütçe gerçekleşme oranı»* → yalnız `toplam_hedef`. Üç düzeyde ölçüldü: `butce` küpünde gerçekleşme ölçüsü **yok**, `butce_hedefleri` tablosunda gerçekleşme **kolonu yok** (`demo/genisletme.py:164`), ama küp `gerçekleşme`'yi **cube sinonimi** olarak talep ediyor. Gerçekleşme **başka küplerde** yaşıyor → bu bir **çapraz-küp KPI** kalemidir (`kpi.py`), bir sözlük satırı değil. ⊙ Küpün kendi başlığı bunu zaten biliyor: *«Gerçekleşme tek başına bir gerçekleşme değildir; bir hedefe göre gerçekleşmedir.»* **Eksik olan veri ya da kod değil, bir İŞ BEYANI** |
| ⊘ **genelleme DENENDİ, ÇÜRÜDÜ** | *«küp sinonimi hiçbir ölçü/boyut adına karşılık gelmiyorsa kusurdur»* yüklemi **66 kalem** buldu, çoğu meşru (`bakim ← tamir` · `ik ← insan kaynakları`): küp sinonimleri **konuyu** adlandırır, ölçüyü değil. `gerçekleşme`'yi `tamir`'den ayıran şey yapısal değil **anlamsal** → kapalı bir kapı kurulamaz (`ADR-0008`). *Bir kusuru genellemek, ancak genellemesi ölçülebiliyorsa doğrudur.* |
| **dosyalar** | `app/llm.py::_cube_select_system` (mevcut kanal) · `demo/packs/*/instructions.md` · `app/kpi.py` (gerçekleşme beyanı) |
| 🟢 **canlı ölçüm (2026-08-12)** | *«bütçe gerçekleşme oranı»* ve *«hedefin neresindeyiz»* artık **sessizce dönmüyor**: cevap kendini *«bu soruyu kataloğumdaki hiçbir **ölçü**, **boyut** ya da **döneme** bağlayamadım — aşağıdaki rapor bir **varsayımdır**»* diye **beyan ediyor** (`ADR-0020` çalışıyor). Yani `GG-a`'nın *«sessiz»* yarısı kapanmış; açık kalan **gerçekleşmenin kendisi** |
| 🔴 **ve curl BAŞKA bir kusur verdi** | *«hedefin neresindeyiz»* → `measures: ['toplam_hedef', **'toplam_hedef'**]`, özet: *«2 ölçü: toplam_hedef, toplam_hedef»*. Üç zarar, üçüncüsü **sessiz**: `olcu_sayisi` 2 olur → `anlatici.basit_mi` **False** → deterministik şablon atlanır, tur **LLM'e** düşer. ✅ Tek boğazda kesildi (`cube_router.parse_cube_query`, 10+ çağıran — `KAT-1`), sıra korunarak; kapı `tests/test_yinelenen_olcu.py` (5). Canlı doğrulandı: `['toplam_hedef']`. *Bir yinelenme, sayan her kuralı yanıltır — ve en pahalıya, sayıyı bir KARAR için kullanan kurala mal olur.* |
| **dış dayanak** | Wren **AI Context Layer**'ın birinci bileşeni · Apache **Ossie**'nin `ai_context` alanı (**ThoughtSpot dâhil 8 satıcı**) · Anthropic: **skill'siz %21 → skill'li >%95** |
| **curl** | ① sözlükte tanımlı bir terim (*«gerçekleşme»*) → artık **doğru cevap ya da dürüst red** ② tanımsız terim → davranış değişmedi |
| ⚠ **risk** | **Bakım borcu.** Anthropic: **bakımsız bırakılınca bir ayda %95 → %65** |
| **azaltma** | Dosya **pack ile aynı repoda, aynı PR'da** — Anthropic'in çözümü birebir bu (*veri-modeli PR'larının ~%90'ı skill değişikliği içeriyor*) |
| **MİMARİ.md** | **§3** yeni alt bölüm + **yeni ADR** |

### ✅ B4 · Reflect + Repair döngüsü — **TAMAMLANDI (2026-08-11)**

> 🟢 **UYGULANDI VE CANLI ÖLÇÜLDÜ.** `plan_garson`: `ONARIM_TAVANI = 2` + sınıf başına
> **çare tablosu** `ONARIM_YONERGESI`; bayrak `onarim_dongusu` (kapalıyken tavan **1**,
> `KURAL B`). Sayaçlar `/stats/plan`'a `onarildi_tur1`/`onarildi_tur2` olarak eklendi.
>
> 🔴 **ÖNCE ÖLÇÜLDÜ — ve kart ile gerçek AYRIŞTI.** Kartın 1. curl senaryosu
> (`EE-11`: *«km başına nakliye maliyeti neden yüksek»* → *«(cube yok) diye bir cube YOK»*)
> **zaten geçiyordu**: canlıda 3 adımlık plan, `cube=sevkiyat`, 451 satır. Ve
> `plan KOŞAMADI` (çalıştırma anındaki red) kütükte **0 kez** ateşlemişti. Yani kartın
> tarif ettiği boşluk **kapanmıştı**; açık olan başka bir şeydi.
>
> **Asıl kusur `/stats/plan`'da duruyordu:**
> ```
> denendi=16 · geçerli=12 · onarildi=1 · dustu=3
> red_orani_yuzde=25 · 🔴 onarim_tutma_yuzde=25
> red_nedenleri = {"ulasilmaz": 4}      ← dört reddin DÖRDÜ de aynı sınıf
> ```
> Onarım turu **vardı ve ateşliyordu** ama **4'te 1** tutuyordu; istem yalnız
> *«sözleşmeye UYARAK yeniden planla»* diyordu — kusuru söyleyip **çareyi** söylemiyordu.
>
> **SONRA (aynı uç, altı planlayıcı sorusu):**
> ```
> denendi=18 · onarildi=9 · dustu=1 · onarim_tutma_yuzde=🟢 90
> onarildi_tur1=7 · onarildi_tur2=2
> ```
> ⊙ **Kazancın büyük kısmı ikinci turdan DEĞİL, çare yönergesinden geliyor:** dokuz
> onarımın **yedisi ilk turda** tuttu. İkinci tur **2** vakayı kurtardı — masrafını
> çıkarıyor ama küçük yarısı. *Bir döngüyü uzatmadan önce, söylediğinin anlaşılır olup
> olmadığını sormak gerekir.*
> ⚠ `red_orani_yuzde` 25→56 yükseldi; **iki örneklem aynı soru karışımı değil** (bu tur
> bilerek planlayıcı-tetikleyen sorulardı). Kıyaslanan şey **tutma oranıdır**.
>
> **Curl/kütük (kartın üç senaryosu):** ① `EE-11` → cevap ✔ ② tavan: kütükte turlar
> `1/2` ve `2/2` etiketli, **3. tur 0 kez** ✔ ③ onarılamaz hâlde `dustu=1` → dürüst red,
> sonsuz döngü yok ✔. Kapı: `tests/test_b4_onarim_dongusu.py` (6) + plan yüzeyi **216 yeşil**.
>
> ⚠ **Bir kapı politikayı savundu:** `test_TEK_ONARIM_TURU_VE_TAM_BIR_TANE` kırmızı verdi —
> eski politikayı (*«tam olarak bir tane»*) kilitliyordu. İlke doğruydu ama **tavanın bir
> olması ölçülmemişti**; test `test_ONARIM_TURU_TAVANLIDIR_ve_SEBEP_TASIR` olarak
> ölçümüyle birlikte yeniden yazıldı ve `KURAL B` gövdesi eklendi (**silinmedi**).

### B4 · Reflect + Repair döngüsü

| | |
|---|---|
| **ÖNCE** | `plan_garson`'da **tek** *«DÜZELTME TURU»*; `llm.py`'deki yeniden denemeler yalnız **boş yanıt** içindir. Motor hatası modele **geri verilmiyor** — `EE-11`'de ölçüldü: *«🔴 Ama tamamlayamadım: `(cube yok)` diye bir cube YOK»* kullanıcıya gitti |
| **SONRA** | Motor/derleyici hatası → **modele geri** → **en fazla 2 tur** → sonra dürüst red |
| **dosyalar** | `app/plan_kosucu.py` · `app/plan_garson.py` · `app/llm.py` |
| **dış dayanak** | Snowflake **Error Correction Agent** (*«SQL derleyicisini kullanarak hem sözdizimsel hem **anlamsal** hata arar»*) · Wren `retry&repair` · Genie öz-düzeltme · Anthropic **evaluator-optimizer** deseni. ⊙ **Bu ajanlık değil, WORKFLOW** — Anthropic'in *«ajan yerine iş akışı»* önerisine uyar |
| **curl (3)** | ① `EE-11`'in sorusu (*«km başına nakliye maliyeti neden yüksek»*) → artık **cevap** ② kasıtlı bozuk plan → **2 turda** durdu mu ③ onarılamaz hata → **dürüst red** (sonsuz döngü yok) |
| 🔴 **risk** | **Gecikme ve maliyet.** Her tur bir LLM çağrısı |
| **azaltma** | **Kesin tavan 2**; `Butce(saniye=…)` bağlayıcı; onarım turu **yalnız derleyici hatasında** (boş sonuçta değil) |
| **MİMARİ.md** | **§2** — *«6. basamak onarım döngüsü taşır, tavan 2»* |

---

## FAZ 2 · YETENEK KAYDINI BİRLEŞTİR — 1 hafta

### ⊘ C1 · `FIIL_ANLAMI`'nı `tools.py`'den türet — **ÖLÇÜLDÜ, ŞİMDİ YAPILMIYOR** *(2026-08-12)*

> İlke (`KAT-1`) doğru ve bağlayıcı; soru **ne zaman** ödeneceği. Üç ölçüm ertelemeyi
> gerektirdi:
>
> | | ölçülen |
> |---|---|
> | `FIIL_ANLAMI` | **15 fiil** ✅ raporla aynı · **CANLI** (`plan_garson.py:284` her çağrıda şema kuruyor) |
> | `tools` kaydı | **25 araç** ✅ raporla aynı · ⊘ **plan yolunda UYKUDA** — iki tüketicisi de kapalı: `mcp.py` (`mcp_yuzeyi: off`) ve `Planlayici.sec()` (`agent_plan_secimi: off`) |
> | adlar | 🔴 **örtüşmüyor**: `SORGU`/`AYRISTIR`/`GORSEL` ↔ `route`/`contribution.decompose`/`viz.recommend` |
>
> ① **Canlı kaydı uykudaki kayıttan türetmek** olurdu: riski canlı yol taşır, faydayı
> kapalı yol. Kartın kendi `risk` satırı zaten yazıyor: *«Yanlış türetim planları bozar.»*
> ② Kullanıcı **hiçbir şey hissetmez** (`KURAL B` → bayt bayt aynı), ve bu oturumun
> bağlayıcı uyarısı: *«ölçüm/altyapı tesisatı ürün değildir»*.
> ③ Adlar örtüşmediği için türetim bir **eşleme tablosu** ister → iki kayıt yerine **üç**
> şey. `KAT-1` adına yapılan bir işin üçüncü bir kayıt doğurması, ilkeyi ilkenin adıyla
> çiğnemek olurdu.
>
> ⚠ **Raporun *«örtüşme %73»* rakamına dokunulmadı**: o **anlamsal** bir eşleştirmedir;
> kaba bir ad eşlemesi %26 verdi ve bu onu **çürütmez** — *kaba bir ölçü, ölçemediği bir
> iddiayı çürütemez.*
>
> 🔴 **VE BORÇ KENDİNİ TOPLUYOR:** `test_c1_tek_yetenek_kaydi.py` iki bayraktan biri
> açıldığı gün **kırmızı** olur ve ödeme biçimini satır satır yazar (araç kendi `fiil`ini
> **beyan eder** → `FIIL_ANLAMI` türetilir → bayt bayt aynı çıkar). O gün iki kayıt da
> canlı olacak ve ayrışmaları **gerçek** bir risk hâline gelecek.
> ⊙ Yani `C1`'in doğru sırası **`C3`'ten sonra**dır, önce değil.
>
> *Bir borcu ertelemek, onu unutmak değildir — eğer erteleme kendi alarmını kuruyorsa.*

### C1 · `FIIL_ANLAMI`'nı `tools.py`'den türet *(özgün kart)*

| | |
|---|---|
| **ÖNCE** | **İki paralel sistem**: `plan_semasi.FIIL_ANLAMI` **elle yazılmış 15 fiil** (canlı) ↔ `tools.py` **25 araç** (`agent_plan_secimi: off`). **Örtüşme %73** (15 fiilin 11'inin araç ikizi var) |
| **SONRA** | `FIIL_ANLAMI` **`tools.py`'den üretilir** (plan-bestelenebilir araçlar süzülerek). Kapalı `enum` **korunur** — yalnız artık **türetilmiş** olur |
| **dosyalar** | `app/plan_semasi.py` · `app/tools.py` · `tests/test_plan_semasi.py` |
| **iç dayanak** | 🔴 `plan_semasi`'nin **kendi docstring'i**: *«`cube_query` ŞEMASI YENİDEN YAZILMIYOR — **ÇAĞRILIYOR**… Bir şemayı iki yerde tanımlamak, iki farklı katalogla koşmaya razı olmaktır.»* — ilkeyi `cube_query` için uygulamış, **fiil kümesi için unutmuş** |
| **dış dayanak** | OpenAI eşiği: *«15'ten fazla **ayrık** araç sorun değil; **10'dan az ÖRTÜŞEN** araç sorun»* → birleşme kümeyi *örtüşmeyen* yapar |
| **kazanç** | ① tek kayıt (`KAT-1`) ② **yetki süzgeci plana bedava** ③ MCP plan yolunu da kapsar ④ *«hangi araç hiç seçilmiyor»* **sayılabilir** hâle gelir |
| **curl (3)** | ① üretilmiş `enum` **bugünkü 15 fiille birebir aynı mı** (kapı ile kilitle) ② tipik 5 soru → **aynı planlar** ③ yetkisiz kullanıcı → **kısıtlı fiil listesi** |
| 🔴 **risk** | **Canlı yolda yeniden düzenleme.** Yanlış türetim planları bozar |
| **azaltma** | `KURAL B` **zorunlu**: türetilmiş liste bugünkü ile **bayt bayt** aynı çıkmalı; bir kapı bunu kilitler. Bayrak yok — çünkü **davranış değişmemeli** |
| **MİMARİ.md** | **§2.0** — *«tek yetenek kaydı; plan fiilleri türetilir»* |

### ✅ C2 · Bütçe + stall sayacı — **ÖLÇÜLDÜ: ZATEN CANLI** *(2026-08-12)*

> 🔴 **Aşağıdaki «ÖNCE» satırının sayıları BAYAT.** Ölçüldü:
>
> | | rapor | **bugün** |
> |---|---|---|
> | `Butce.adim` | 3 | **8** |
> | `Butce.saniye` | 10 | **30,0** |
> | `Butce.sorgu` | **0 — uykuda** | **12 — CANLI** (`if b.sorgu and …` uygulanıyor) |
> | stall sayacı | **YOK** | **`ONARIM_TAVANI = 2`** — *«Magentic-One stall ≤2»* |
> | `AZAMI_ADIM` | *«hiç bağlayıcı olmamış»* | **12**, `dogrula`'da **koşmadan önce** |
> | `AZAMI_SORGU` | — | **8** (plan katmanı; dar olan bağlar) |
>
> `Planlayici._kis()` tavanı aşınca `ButceAsimi` **fırlatıyor**; sınıfın docstring'i
> kısmi-cevap kalıbını yazıyor (*«o ana kadarki adımlar GEÇERLİ»*). Ve `%60 tek adım`
> rakamı `§A13` ile zaten çürümüştü (**%21**).
>
> 🔴 **Stall sayacı bu oturumda `§B4` ile geldi** — C2'nin kendi satırı *«serbest döngüye
> (B4) geçerken **pazarlık dışı**»* diyordu ve B4 canlıya alınırken tavan onunla birlikte
> kondu. *Bir şartı, şartı doğuran işi yaparken ödemek en ucuzudur.*
>
> ⊙ Yapılan iş: sayıları **kapıya kilitlemek** (`test_c2_butce_stall.py`, 8). Bunlar
> güvenlik tavanları; biri `sorgu=0`'a düşerse koruma **sessizce** kalkardı — hiçbir test
> kırılmadan, hiçbir cevap bozulmadan. *Uygulanmayan bir tavan, olmayan bir tavandan
> kötüdür: birincisine güvenilir.*
>
> ⚠ Tek sınırsız eksen `token` ve gerekçesi **yazılı** (telemetri boş); kapı gerekçenin
> silinmesini de yakalar.

### C2 · Bütçe + stall sayacı *(özgün kart)*

| | |
|---|---|
| **ÖNCE** | `planner.Butce(adim=3, saniye=10, **sorgu=0**)` **uykuda**; **stall sayacı YOK**. Ve ölçüm: planların **%60'ı tek adım**, en uzunu **7** — `AZAMI_ADIM=12` **hiç bağlayıcı olmamış** |
| **SONRA** | Bütçe canlıya; **stall ≤2 → yeniden planla**, sonra dur |
| **dosyalar** | `app/plan_kosucu.py` · `app/planner.py` |
| **dış dayanak** | **Magentic-One stall counter ≤2** · Snowflake token+süre tavanı. ⊙ **Serbest döngüye (B4) geçerken pazarlık dışı** |
| **curl** | ① döngüye giren bir soru → **durdu mu** ② normal soru → gecikme **değişmedi mi** |
| **risk** | erken kesme → cevapsız artışı |
| **azaltma** | Kesildiğinde **o ana kadarki adımlar geçerli** (`ButceAsimi` zaten böyle tanımlı) |

### ✅ C3 · MCP açılış şartları — **DÖRDÜ DE KARŞILANDI** *(2026-08-12, ikinci ölçüm)*

> ⟳ **BU BÖLÜMÜN İLK HÂLİ (aşağıda, olduğu gibi duruyor) iki şartı 🔴 sayıyordu. İkinci
> ölçüm ikisini de çözdü — ve biri bir GÜVENLİK KUSURU çıktı.**
>
> | # | ilk ölçüm | ikinci ölçüm |
> |---|---|---|
> | ① araç ≤20 | 🔴 25 > 20 | ✅ **eşiğin kendisi bir VEKİLDİ.** Asıl ölçüt (OpenAI) sayı değil **örtüşme**; ölçüldü: **1 çift** (`stats.trend`↔`stats.ozet`), **25 aracın 23'ü ayrık**. Vekil kırmızı, asıl ölçüt yeşil. Eşik kaldırılmadı, **yerine geçildi** (`ORTUSME_TAVANI=10` asıl · `ARAC_TAVANI=35` ikincil) |
> | ② yazma aracı yok | ✅ | 🔴→✅ **ŞART BİR RASTLANTIYDI.** `yazma_araclari` bayrağı açıkken `mcp.araclar(None)` **28** döndürüyor ve üç yazma aracı **MCP yüzeyinde görünüyordu**. Artık yapısal: `tools.okuyan_araclar()` eler, `mcp.cagir()` adı bilinse bile **reddeder** |
> | ③ dört kapı | ✅ | ✅ değişmedi |
> | ④ sanitizasyon | 🔴 hiç yok | ✅ **iki kapalı yapısal sınıf + köken beyanı** — C0/C1 kontrol karakterleri · ANSI kaçışları · zarf sınırı taklidi. Kelime listesi **YOK** (`ADR-0008`) |
>
> 🔴 **En önemli bulgu ②'de:** kartın *«yazma araçları kayıtta yok (zaten öyle)»*
> parantezi **doğruydu ama bir güvence değildi**. Sınırı koruyan şey kaydın boşluğuydu;
> `§F13`'ün bayrağı açıldığı an güvence **sessizce** ölüyordu.
> *Bir sınırı bir rastlantının koruması, o sınırın hiç konmamış olmasıdır.*
>
> ⚠ **Bayrak yine de AÇILMADI** — açılış artık bir güvenlik borcu değil bir **ürün
> kararı**: `§C1` (tek yetenek kaydı) hâlâ `mcp_yuzeyi` açılışına bağlı ve o karar
> ayrıca verilmeli. Kapı: `test_c3_mcp_acilis_sartlari.py` · `test_mcp.py`.

### ⊘ C3 · MCP yüzeyini aç — **AÇILMADI: dört şarttan İKİSİ karşılanmıyor** *(ilk ölçüm, 2026-08-12)*

> Kartın `azaltma` satırı bir dilek listesi değil, **açılış şartıdır**. Dördü tek tek
> ölçüldü:
>
> | # | şart | ölçülen | |
> |---|---|---|---|
> | ① | araç **≤20** | `KAYIT` **25** · `llm_araclari(None)` **25** · `mcp.araclar(None)` **25** | 🔴 |
> | ② | yazma aracı **yok** | `yan_etki` dağılımı **`{'yok': 25}`** — sıfır `yazar` | ✅ |
> | ③ | salt-okuma / **dört kapı** | `mcp.cagir` bir `Planlayici` **istiyor**, `calistir` çağırıyor; `araclar()` `llm_araclari()` ile **aynı sayıda** (`KAT-1`) | ✅ |
> | ④ | serbest metin **sanitizasyonu** | `mcp.py`'de `sanit`/`temizle`/`kaçış`/`pii` izi **HİÇBİRİ**; `cagir` PII çağırmıyor | 🔴 |
>
> 🔴 **İki eksik AYRI CİNSTEN:**
> * **④ eksik bir KONTROL.** Kartın *«bizim özel riskimiz»* dediği yol tam olarak açık:
>   bir müşteri notu hücresine yazılmış talimat MCP yanıtı olarak modele döner. Tasarım
>   işi (neyin süzüleceği + süzmenin **beyan edilmesi**), tek satır değil.
> * **① bir KARAR.** `≤20`, raporun kendi dış dayanağının daha **katı bir vekilidir**:
>   OpenAI ölçütü *«15'ten fazla **ayrık** araç sorun değil; **10'dan az ÖRTÜŞEN** araç
>   sorun»* — yani ölçüt **sayı değil ÖRTÜŞME**. 25 aracın örtüşmesi **ölçülmedi**;
>   ölçülmeden ne *«eşiği gevşet»* ne *«beş araç kes»* denebilir.
>   ⚠ Ve **`C1` tam bu ölçümü bekliyor** (fiil ↔ araç eşleşmesi) — ikisi **aynı ölçüme**
>   bağlı ve birlikte ödenmeli.
>
> ⊙ Ölçüye dayanan **on ikinci** *«yapma»*. Ama bir red bir **borçtur**: kapı
> (`test_c3_mcp_acilis_sartlari.py`, 5) karşılanan iki şartı **kilitliyor** (yazma aracı
> girerse ya da MCP kendi yürütme yolunu açarsa **kırmızı**) ve iki eksik kapanmadan
> bayrak açılırsa eksiği **adıyla** söylüyor.
>
> *Bir güvenlik sınırını «sonra bakarız» diye açmak, sınırı hiç koymamaktır.*

### C3 · MCP yüzeyini aç *(özgün kart)*

| | |
|---|---|
| **ÖNCE** | `mcp_yuzeyi: "off"` → uçlar **404** |
| **SONRA** | Açık; `tools.llm_araclari(principal)` çevirisi (yetki süzgeci **yeniden yazılmaz**) |
| **dosyalar** | `demo/packs/features.yml` · `app/routers/mcp.py` |
| **dış dayanak** | Wren **chat UI'ını legacy'e gömdü**; Rill'de projelerin **%50+'ı ajan tarafından** kuruluyor. ⊙ *«Chat UI 2026'da varlık değil yük»* |
| **curl** | ① `tools/list` → **kaç araç** (⚠ **~20 eşiği**) ② `tools/call` yetkisiz → **reddediyor mu** |
| 🔴 **risk** | **Prompt injection.** 14 CVE · 2.614 uygulamada **%82 path traversal, %67 code injection**. ⊙ **Bizim özel riskimiz:** veri tablolarındaki **serbest metin hücreleri** (müşteri notu, ürün açıklaması) MCP yanıtı olarak modele döner |
| **azaltma** | Salt-okuma; **yazma araçları kayıtta yok** (zaten öyle); serbest metin alanları için **çıktı sanitizasyonu**; araç sayısı **≤20** |
| **MİMARİ.md** | **§ MCP** — açılış koşulları ve injection sınırı |

---

## FAZ 3 · CEVAP BİÇİMİ — «robotik»in ilacı, 1 hafta

### ✅ D1 · Olgu sayacı — **ÖLÇÜLDÜ (2026-08-11) ve teşhis DÜZELTİLDİ**

> 🔴 **`§18.3`'ün *«canlıda 1-2 ateşliyor»* teşhisi AZ ÖRNEKLEMDENDİ.** 12 canlı soruda
> `interpretation.facts[].type` sayıldı (kod değiştirmeden — sayaç enjekte etmek yerine
> cevabın kendisi okundu):
>
> | tip | adet | | tip | adet |
> |---|---|---|---|---|
> | `top` · `bottom` | 6 · 6 | | `trend` · `peak` · `delta` | 2 · 2 · 2 |
> | `kiyas` 🆕 | 4 | | `single` · `measures` | 3 · 2 |
>
> **Ve olgu sayısı soruya göre 0-6 arasında değişiyor** (§18: *«hep 1-2»*). Sonraki üç
> hedefli soru susan üreticileri de ateşledi:
> *«makine bazında aylık üretim»* → **4** olgu (`trend·peak·delta·shape`) ·
> *«cinsiyet bazında ciro»* → **3** (`top·bottom·segment_delta`) ·
> *«vardiya bazında aylık oee»* → `shape` + **dürüst red** (*«dönem trendi YAZILMADI:
> ort_oee toplanabilir değil»*).
>
> 🔴 **`_streak` ÖLÇÜLDÜ VE AKLANDI — genişletilmemeli.** Aylık ciro serisinde gerçek
> ardışık aynı-yönlü dönem **2**, eşik **3**. Yani üretici bozuk değil, **haklı olarak
> susuyor**; eşiği düşürmek `D2`'nin kendi risk satırını (*«gürültü»*, Pulse: *«avoids
> noisy findings»*) çiğnemek olurdu. *Bir üreticinin sessizliği, önce verinin sessizliği
> olabilir.*
>
> ⊙ **Sonuç:** taksonomi `§18`'in çizdiğinden **sağlam**; koşullar dar ama **doğru**.
> `D2`'nin *«koşulları genişlet»* maddesi bu ölçümle **gereksiz** hâle geldi — genişletme
> yerine yapılması gereken, üretilen olguların **tüketilmesiydi** (⬇).

### 🔴 D1'in gerçek bulgusu — üretilen olgu ŞABLONA TANITILMAMIŞTI

> `anlatici.TANINAN` **kapalı** bir kümedir ve modülün kendi uyarısı şudur: *«yeni bir
> tür `interpret()`'e eklenirse bu basamak onu **tanımaz ve turu LLM'e devreder**»*.
> Ölçüldü: `kiyas` (yeni) **ve zaten üretilmekte olan `segment_delta`** kümede **yoktu**
> → ikisini taşıyan her cevap, 0 token ile anlatılabilecekken **LLM'e** düşüyordu.
>
> **Canlı kanıt (düzeltmeden sonra):** *«cinsiyet bazında ciro»* → 3 olgu ·
> `narration_kaynak=sablon` · `ai_generated_prose=False`; *«geçen yıla göre ciro»* →
> `single+kiyas` · aynı şekilde. Kütükte `T2 ŞABLON: LLM çağrısı YAPILMADI`.
> ⊙ Kazancın ölçüsü kütükte yazılı: anlatı LLM'i bir turda **22,5 sn / turun %93'ü**.
>
> ⚠ Genişletme kapıyı **gevşetmez**: `basit_mi`'nin `≤4 olgu` ve `tek ölçü` şartları
> yerinde — çok ölçülü bir kıyas hâlâ LLM'e gider.
> Kapı: `tests/test_d1_anlatici_kapsami.py` (4) — *üretilen her tip ⊆ tanınanlar*, yani
> `interpret` yeni bir tip üretirse kapı **konuşur**.

### D1 · Olgu sayacı *(ölçüm — 1 gün)*

| | |
|---|---|
| **ÖNCE** | ⟳ **ÖLÇÜLDÜ:** 11 çağrı yeri ama **14 tip**; canlıda **2-3** ateşliyor (curl) |
| **SONRA** | ⏸ **PARK** — geçici sayaç bir **ölçüm tesisatıdır**, ürün değil. Değerin statik+canlı alınabilen kısmı `§18.3`'te alındı |
| **niçin park** | Tesisat `A1` kaseti **21→50** olunca **bedava** gelir: o korpus tam `/ask` yolundan koşuyor ve olguları zaten üretiyor. Ayrı bir sayaç, iki sahipli bir ölçüm olurdu (`KAT-1`) |
| **çıktı (alınan)** | *«tip ekseninde mesafe yok; mesafe **koşul** ekseninde: 2-3 → 14»* |
| **risk** | yok (ölçüm) |

### D2 · Taksonomiyi aç

| | |
|---|---|
| **ÖNCE** | 1-2 olgu — cevabın **derinliği soruya göre değişmiyor** |
| **SONRA** | D1'in bulduğu dar koşullar genişletilir → hedef **Pulse'un 14 tipine** yakın |
| **dış dayanak** | **Tableau Pulse'un 14 deterministik içgörü tipi** (Period-over-Period · Correlated Metrics · Record Outliers · Forecast · Current Trend · Trend Change · Unexpected Values · Goal Breakdown · Pace to Goal · **Top Drivers** · **Top Detractors** · **Concentrated Contribution** · Top/Bottom Contributors) ve *«**standardized, deterministic statistical models**… guaranteed to be accurate»* |
| **curl (5)** | Beş farklı soru türünde **olgu sayısı** ve **çeşidi** değişiyor mu |
| ⚠ **risk** | **Gürültü.** Pulse'un kendi ifadesi: *«**avoids displaying noisy or spurious findings**»* |
| **azaltma** | Her olguya **etki puanı**; yalnız en etkili N tanesi. Ve 🔴 **FDR** (E3) bunun **ön koşulu** |

### ✅ D3 · Cevap biçimi bir KARAR olsun — **TAMAMLANDI (2026-08-11)**

> 🟢 **UYGULANDI VE CANLI DOĞRULANDI.** Yeni tek sahip `app/bicim.py` (karar tablosu:
> `niyet`in kapalı altı türü × `suggest_next_steps`'in beş kovası) ·
> `cube_router.suggest_next_steps(…, kota)` · `answer._attach_next_steps` (tüketir +
> makbuza yazar) · bayrak `bicim_karari: beta`.
>
> 🔴 **VE ÖNCE ÖLÇÜLDÜ — kuralın YARISI ZATEN VARDI.** `§14.13`'ün istediği iki grafik
> kuralı `viz.py`'de **yazılı ve canlıda ateşliyor**: `analyze()` tek satır + ölçü →
> `kpi` (curl: *«bu yıl toplam ciro»* → `kpi`), `_cizme_kurallari` kural 2 → `cumle`
> (curl: *«en kötü 3 makineyi analiz et»* → `viz=cumle`, gerekçe **birebir**: *«3 kalem
> — üç çubuk, üç kelimeden daha az anlatır»*). ⊙ `§12.12`'nin *«yazılmış ama
> bağlanmamış»* deseninin **yedinci** örneği — bu kez lehimize: yazılacak kod yoktu.
>
> **Açık olan yarı ölçüldü ve kapatıldı** — `§18`'in sekiz sorusu curl ile tekrarlandı:
>
> | | chip dizisi |
> |---|---|
> | `§18` (rapor yazıldığında) | `6,6,5,6,6,4,6,3` |
> | **bugün, değişiklikten önce** | `6,6,6,6,5,6,6,5` — 🔴 **daha da sabit** |
> | **sonra** | **`4,6,2,4,4,4,6,3`** |
>
> 🔴 **Ve asıl kusur sayı değil ALÂKASIZ KOVA:** *«bu yıl toplam ciro»*nun chip'leri
> arasında `+ ortalama hız` ve `+ fire` vardı. Bir **ciro** sorusuna başka bir ölçü
> önermek soruyu derinleştirmez, **değiştirir**. Kapatma kuralları: `toplam` → `+ölçü`
> + `top-N` · `ustunluk` → `top-N` · `kiyas` → `kıyas` · `trend` → `top-N`; çok türlü
> soruda kova başına **en küçük** kota.
>
> 🔴 **Bir kusuru makbuz yakaladı:** ilk yazımda kota **şemasız** okumadan geliyordu
> (`niyet.coz_soru`) ve curl'de `niyet:` izi *«kirilim»* derken `§D3` izi *«toplam»*
> dedi — *«hangi müşteri riskli»* (8 satırlık kırılım) tek-sayı kotası alıyordu.
> `kirilim`/`ustunluk` **katalog eşleşmesiyle** doğar. İki iz yan yana basılmasaydı
> görünmezdi. Kapı: `test_karar_semali_okumadan_verilir`.
>
> **Kapı:** `tests/test_d3_bicim_karari.py` (9 test) — karar tablosunun anlamı ·
> çok-türlü indirgeme · `KURAL B` (kota verilmezse **bayt bayt** eski) · kova adlarının
> tek kaynakta olduğu (`KAT-1`).
>
> ⚠ **KAPSAM DIŞI BIRAKILAN, ve neden:** ① *«tek değer → tekrarcı özet»* — `«bu yıl
> toplam ciro»` cevabı `summary: "ciro: ₺74.022.836,94."` taşıyor, yani KPI kartını
> **tekrar ediyor** (`§21.3`: *«114 kişi grafikte zaten görüneni tekrar söyleyen
> metinden rahatsız oldu»*). ② *«geçen yıla göre»* sorusunda sonuçta
> `toplam_ciro_degisim_yuzde` **var**, anlatı değişimi **söylemiyor**. ⊙ İkisi de
> **olgu taksonomisi** işidir → `D1`/`D2`/`D11`. Biçim kararı onları çözemez; **hangi
> olgunun üretildiği** sorunudur.
>
> ⚠ `§18`'in *«not (karakter)»* sütunu `note` alanını ölçüyor; kullanıcının gördüğü
> metin `interpretation.summary`'dir (`OutputInsight.tsx:52`). *«İki cevapta sıfır
> metin»* bulgusu bu yüzden **`note` için doğru, kullanıcı için yarım** — ölçüm aracının
> basmadığı alan yine bir teşhisi eğdi.

### D3 · Cevap biçimi bir KARAR olsun

| | |
|---|---|
| **ÖNCE** | Biçim = `viz.analyze` + `interpret` + `_attach_next_steps` üçünün **artığı**. Ölçüldü: chip **6,6,5,6,6,4,6,3**; olgu **hep 1-2**; **çoklu grafik hiç yok**; iki cevapta **sıfır metin** |
| **SONRA** | Tek bir **biçim kararı** noktası: `niyet` (6 soru türü) + `followup` (5 konuşma türü) **zaten biliyor** → *«bu soru ne tür bir cevap ister»* |
| **dosyalar** | `app/answer.py` · `app/interpret.py` · `app/viz.py` |
| **dış dayanak** | 🔴 **Hearst & Tory (IEEE VIS 2019): sohbet bağlamında kullanıcıların %41'i SAF METİN istiyor**, tercih kişi bazında **%82-89 kararlı** (χ² p<0,001) · **Power BI'ın belgelenmiş kuralları**: tek değer → **Card (büyük sayı, grafik değil)**, kesin değer arama → **tablo**, hedefe ilerleme → **KPI** · **Franconeri ve ark. (2021)**: *«vision is **sluggish for comparisons**»* — 2-3'ten fazla değer çifti aranıyorsa iş **tablonun** · **OpenAI Model Spec**: biçim **isteğe göre**, **tek varsayılana saplanılmadan**. ⚠ **Anlamlı negatif bulgu:** Databricks Genie **hiçbir biçim kuralı yayımlamıyor** — sektör LLM muhakemesine bırakıyor; 🟢 **biz deterministik VE yayımlanmış yapabiliriz** |
| **somut kural taslağı** | tek satır + tek ölçü → **KPI kartı, grafik yok** · ≤3 satır → **metin cümlesi** (*«Text-values»* biçimi: ham değerler) · kesin değer arama / >2-3 kıyas → **tablo** · zaman ekseni → **çizgi** · kırılım + tek ölçü → **çubuk** · ⚠ **kişiselleştirme kancası** (§21.1: tercih **kararlı**) |
| **curl (8)** | §18'in sekiz sorusu tekrar → chip sayısı **çeşitlendi mi**, sıfır-metin vakaları **kapandı mı** |
| **risk** | ⚠ Aşırı çeşitlilik de tutarsızlık üretir |
| **azaltma** | Karar **deterministik ve tablolu** olsun (LLM seçmesin) — ADR-0024'ün aynı ilkesi |
| **MİMARİ.md** | **ADR-0024'e ek** — *«cevap biçimi de deterministik bir karardır»* |

### ✅ D4 · Ön-uç sayı biçimi — **ÜÇ DAYANAĞI DA KARŞILIKSIZ ÇIKTI, AMA ÖLÇÜM DAHA AĞIRINI BULDU** *(2026-08-12)*

> | kartın iddiası | ölçülen |
> |---|---|
> | `Intl…{style:"percent"}` → `%56`, 0 ondalık | ✅ doğru **ama ön-uç bunu KULLANMIYOR**: `format.ts` `{maximumFractionDigits: 2}` + birim eki → `55,55 %` |
> | `d3-format`'ta `tr-TR` yok | ⊘ **`d3-format` hiç kullanılmıyor** — ne bağımlılık ne import |
> | kompakt `12 B` = bin | ✅ ölçüldü: `12 B` · `1,2 Mn` · `1,2 Mr` — **Türkçesi doğru** |
>
> 🔴 **ASIL KUSUR BAŞKAYDI: ölçek ilanı ile değer birbirini tutmuyordu.** Canlıda iki kez
> bağımsız ölçüldü: `«bölüm bazında oee»` → `ort_oee: 0.641` · `«bu yıl ortalama oee»` →
> özet **`Oee 0,58 %.`** Katalog `unit: "%"` ilan ediyor, değer **0–1 oranı** →
> kullanıcı **100× küçük** okuyor, uyarı **yok**. Ve **aynı küpteki** kardeşi
> `ilk_seferde_tamam_yuzde` **zaten ×100**: yani `%` **tek bir küpte iki ölçek** demekti.
>
> ✅ **Düzeltme KATALOGDA** (sunum katmanı bir sayının 0–1 mi 0–100 mü olduğunu bilemez;
> büyüklükten tahmin etmek `ADR-0008` ihlali ve gerçekten `%0,8` olan bir ölçüyü şişirirdi):
> dört OEE oranı kardeşlerinin kuralına getirildi (`×100`, `ROUND 2`).
> **Canlı:** `Oee 0,58 %.` → **`Oee 58,02 %.`** · `Örgü (0,64 %)` → **`Örgü (64,11 %)`**.
>
> ⚠ **`maliyet.ort_kar_marji_yuzde` KAPSAM DIŞI:** `AVG(kar_marji_yuzde)` — kaynak
> kolonun kendi adı `_yuzde`, yani muhtemelen zaten 0–100. Kaba taramam onu *«oran»*
> sandı (**yanlış pozitif**); değeri doğrulanamadığı için **dokunulmadı** ve kapıda
> `OLCULMEDI` olarak **adıyla** kayıtlı. *Bir ölçek düzeltmesi, ölçeği ölçülmemiş bir
> ölçüye uygulanırsa düzelttiğinden fazlasını bozar.*
>
> 🔴 **Yayılma kapısı:** `test_d4_yuzde_olcegi.py` (5) — bundan sonra `unit: "%"` ilan
> eden her ölçü ya `×100` içerir ya da `OLCULMEDI`'ye **gerekçesiyle** yazılır.
> Demet kapısı yeşil, taban **birebir aynı**.

### D4 · Ön-uç sayı biçimi *(özgün kart)*

| | |
|---|---|
| **ÖNCE** | Backend `sayi_bicimi.py` ile düzeldi. **Ön-uç ölçülmedi** ve 🔴 `d3-format`'ta **`tr-TR` locale'i YOK** |
| **SONRA** | ECharts/Vega tarafında Türkçe biçim |
| **dış dayanak** | `Intl.NumberFormat("tr-TR",{style:"percent"})` → **`%56`** (işaret **önde**, **0 ondalık**) · kompakt **`12 B`** = **bin**, İngilizcede **milyar** |
| **curl/ekran** | Üç grafik: yüzde · binlik · kompakt |

### ◐ D5 · Takip anlama — **SESSİZ YANLIŞ BEYANA ÇEVRİLDİ (2026-08-11)**

> 🔴 **Kart hâlâ geçerli ve kusur birebir üredi** (canlı thread):
> ① *«bu yıl makine bazında ortalama oee»* → 11 satır, ilk `ÖRGÜ HAT`
> ② *«**o makinede** vardiya kırılımı»* → **33 satır**, süzgeç **YOK**, beyan **YOK**
>
> ⚠ Ve raporun yazdığından **daha tehlikeli**: `§AT` *«ilk satır yanlış makine»* diyordu;
> bugün ilk satır yine `ÖRGÜ HAT` — yani önceki turun en yükseği. Cevap **makul
> görünüyor**. *Doğruluğunun kanıtı gibi görünen bir yanlış.*
>
> ✅ **Yapılan:** `uyum.atif_beyani` + takip dalına bağlama. Yüklem
> (`niyet_tasima.EKSIK_ATIF`) **zaten kuruluydu** ve yalnız **taze** dalda çağrılıyordu —
> `ask.py`'nin kendi cümlesi bu turda ikinci kez haklı çıktı: *«bir kuralı yazmak, onu
> iki çağrı yerinin ikisinde de kurmak değildir; eksik kurulan yer, kuralın hiç olmadığı
> yerden **daha tehlikelidir**.»*
>
> 🔴 **SÜZGEÇ KURULMADI — ve bu bir eksiklik değil bir KARAR.** *«O makine»* çıkarımı
> yalnız **seçilmiş** bir varlıktan gelebilir; `prev_cq`'da `order` var ama **seçim yok**
> (bir sıralama bir seçim değildir). Yanlış odak, hiç odak olmamasından **pahalıdır**
> (`§101.1`). Kartın kendi azaltması da bunu söylüyor: *«odak varlığı yalnız açık bir
> üstünlük/seçim adımından türetilir — tahmin edilmez»*.
>
> **Canlı kanıt:** *«o makinede…»* → 33 satır **+ beyan** (*«…çözemedim — süzgeç
> kurulmadı ve tümü listelendi. Adını yazarsan süzgeci kurarım»*) · *«RAM-2 için…»* →
> **3 satır**, süzgeç kurulu, **beyan yok** (yanlış pozitif yok).
> Kapı: `tests/test_at_atif_beyani.py` (5) + takip yüzeyi **269 yeşil**.
>
> 🔴 **VE KARTIN «ODAK VARLIĞI YOK» TEŞHİSİ BAYAT ÇIKTI — ölçüldü (üç turlu zincir):**
> ① *«makine bazında oee»* → ② *«en düşüğü hangisi»* (seçim) → ③ *«o makinede vardiya
> kırılımı»* → **süzgeç KURULDU** (`makine = ÖRGÜ HAT`, **3 satır**) ve sistem bunu
> **beyan etti**: *«ÖRGÜ HAT üzerinden yanıtlandı — bir önceki turun seçtiği makine.»*
> ⊙ Sahibi **zaten var**: `app/diyalog.py::odak_uygula` + `odak_suzgeci`. Yani mekanizma
> yazılmış ve çalışıyor; eksik olan **ikinci turda bir seçim yoksa** ne olacağıydı — ve
> onu bu tur kapattı (beyan).
>
> 🔴 **BİR YANLIŞ POZİTİFİ CANLI ÖLÇÜM YAKALADI:** ilk yazımda yüklemi `refined`'a
> sormuştum; odak süzgeci ondan **sonra** ekleniyor, dolayısıyla süzgeç kurulmuşken cevap
> *«süzgeç kurulmadı»* diyordu — üstelik **doğru beyanın hemen yanında**. Denetim
> `resp.cube_query` üzerine alındı. *Bir yüklemi doğru yazmak yetmez; onu doğru NESNEYE
> sormak gerekir.* Kapı: `test_ODAK_SUZGECI_KURULDUYSA_beyan_YOK`.
>
> ✅ **DÖRT KOVANIN DÖRDÜ DE ÖLÇÜLDÜ — DAVRANIŞ OLARAK VAR (beş turlu canlı zincir):**
>
> | kova | tur | sonuç |
> |---|---|---|
> | **theme-property** %9,7 | *«peki geçen yıl»* | dönem 2025'e geçti, ölçü+kırılım korundu · `source=cube` (**0 LLM**) |
> | **theme-entity** %48,4 | *«kullanılabilirliği de göster»* | ölçü eklendi, dönem korundu |
> | **refinement** %33,8 | `deterministic_refine` | CoE-SQL ailesi — raporun kendi tespiti |
> | **answer-refinement** %8,1 | *«o makinede…»* | `diyalog.odak_uygula` süzgeci kurdu + beyan etti |
>
> Ve kartın 4. senaryosu da geçti: **T5 konu değişimi** → `cube=parti`, dönem **sıfırlandı**,
> iz *«çapraz-cube konu geçişi (LLM'siz)»*. ⊙ SParC'ın *«Turn≥4 → %1,1»* çöküş uyarısı
> bu zincirde **üremedi** (T4 ve T5 ikisi de doğru).
>
> 🔴 **KARAR: dört kova `niyet.py`'ye EKLENMEDİ — ve bu bir eksiklik değil bir seçim.**
> Dördünün de **davranışı** var; eklenecek olan yalnız bir **ad**, ve bugün onun bir
> tüketicisi yok. Bir sınıflandırmayı tüketicisi olmadan yazmak, bu oturumda **dokuz kez**
> ölçülen *«yazılmış ama bağlanmamış»* desenini **kendi elimizle** üretmek olurdu.
> ⊙ Kova adları bir **ölçüm** ya da **yönlendirme** tüketicisi doğduğunda anlam kazanır;
> o gün `followup.sinifla`'nın kapalı kümesiyle çakışmayacak şekilde eklenir.

### D5 · Takip anlama — «son cevaba çıpala» + dört kova

| | |
|---|---|
| **ÖNCE** | Takip bağlamı `prev_cq` + `history[-8]` ile taşınıyor. 🔴 **Odak varlığı yok** — `ask.py`'nin kendi `§AT` yorumu: *«o makinede vardiya kırılımı»* → süzgeç **kurulamıyor**, **33 satır** dönüyor, ilk satır yanlış makine. Kendi teşhisi: *«Eksik olan bir kanca değil bir **KAVRAM**»* |
| **SONRA** | ① **Son cevaba çıpalama** modeli açıkça benimsenir ② `niyet`e **dört takip kovası** eklenir: `theme-entity` · `refinement` · `theme-property` · **`answer-refinement`** (önceki **cevaptan** varlık) |
| **dosyalar** | `app/niyet.py` · `app/followup.py` · `app/context.py` (odak varlığı) · `app/routers/ask.py` |
| **dış dayanak** | **SParC oranları**: theme-entity **%48,4** · refinement **%33,8** · theme-property **%9,7** · **answer-refinement %8,1** — ⊙ *sonuncusu tam olarak bizim eksik «odak varlığı» kavramımız* · **ThoughtSpot Spotter**: *«All follow-up questions are assumed to be a follow-up on **the LATEST answer**»* · **CoE-SQL (NAACL 2024)**: soruyu yeniden yazmak yerine **önceki SQL'i düzenle** — ⊙ *bizim `deterministic_refine`'ımız bu ailedendir* |
| ⚠ **tur çöküşü uyarısı** | SParC: Turn 1 **%38,6** → Turn 3 **%3,7** → **Turn ≥4 %1,1**. **Genie'nin uyarısı**: *«Avoid reusing conversation threads across sessions»* · **Power BI**: *«Use **clear chat** when switching topics»* |
| **curl (4)** | ① *«makine bazında oee»* → *«o makinede vardiya kırılımı»* → **süzgeç kuruldu mu** (bugün kurulmuyor) ② *«peki geçen yıl»* (theme-property) ③ *«en düşüğü hangisi»* → *«onun tedarikçileri»* (answer-refinement) ④ 5. turda konu değişimi → **temiz başlıyor mu** |
| 🔴 **risk** | Odak varlığı yanlış çıkarılırsa **yanlış süzgeç** = sessiz yanlış |
| **azaltma** | Odak varlığı **yalnız açık bir üstünlük/seçim adımından** (`order`+`limit=1`, `BAGLA` çıktısı) türetilir — **tahmin edilmez**; belirsizse **netleştirme chip'i** |
| **MİMARİ.md** | **§ diyalog durumu** — *«odak varlığı» kavramı ve dört takip kovası* |

---

## FAZ 4 · KÖK-NEDENİ TAMAMLA — 1 hafta

### ✅ §YV · SORUNUN VARSAYDIĞI YÖN — **CANLI ÖLÇÜM YENİ BİR KUSUR BULDU** *(2026-08-12)*

> FAZ 4'ün kartlarını ölçmek için kök-neden yolu canlıda basıldı ve **kartlarda olmayan**
> bir kusur çıktı:
>
>     «ciro neden DÜŞTÜ» → özet: «ciro: … %117,4 ARTTI …»
>     «düşmedi» · «aksine» · «varsayım» — hiçbiri geçmiyor (arandı, YOK)
>
> Kullanıcı **yanlış bir öncülle** geliyor; sistem o öncülü **sessizce düzeltip** başka
> bir soruyu cevaplıyor. `§101.1`'in sınıfı: cevap **doğru**, sorulan soru **bu değil** —
> ve anlamanın yolu yok.
>
> ✅ **`uyum.yon_beyani`** — yüklem **yapısal**: `_TREND`'in **zaten kapalı** fiil kümesi
> ikiye **bölündü** (yeni sözlük yok, `ADR-0008`); cevap tarafında metin ayrıştırılmaz,
> `trend`/`delta` olgularının **sayısal `pct`**'i okunur (eşik `interpret`'in kendi eşiği).
> ⚠ Üstünlük ifadeleri (*«en düşük müşteri»*) **hariç** — onlar sıralama isteğidir, yön
> iddiası değil; sayılsalardı her top-N sorusu sahte çelişki üretirdi.
>
> 🔴 **VE YERİNİ ÖLÇÜM SEÇTİ.** Kural önce `uyum.denetle`'ye kondu ve **hiç ateşlemedi**:
> orada `resp.interpretation` **henüz yok** (canlı curl üç soruda da `yok` dedi), üstelik
> `denetle`'nin **üç** çağıranı var ve kök-neden soruları **planlayıcı** yolundan geçiyor.
> `_maybe_interpret` ise **tek** yerdir ve yorumu **kuran** yerdir.
> *Bir beyanı, dayandığı olgunun doğduğu yere koymak; onu üç kez bağlamaktan hem ucuz
> hem güvenlidir.*
>
> **Canlı:** `ciro neden düştü` → *«⚠ Soru bir **düşüş** varsayıyor ama ölçülen **ters
> yönde**: **%117,4 arttı**.»* · `ciro neden arttı` → **sessiz** (varsayım doğru) ·
> yönsüz sorular → **sessiz**. Kapı: `test_yv_yon_varsayimi.py` (10); demet kapısı yeşil,
> taban birebir aynı.

### ◐ E1 · Adtributor yatay eksen — **TEŞHİS YARI BAYAT (ölçüldü 2026-08-11)**

> 🔴 **`§10.4(a)`'nın *«`derinles` tek bir ikinci boyut açıyor, KOMBİNASYON ARAMASI
> YAPMIYOR»* iddiası ölçüldü ve yarısı çürüdü.** `derinles` ilk segmente **süzgeç
> kuruyor** (`{boyut: eq, value: segment}`) ve **içinde** ikinci bir kırılım açıyor —
> yani **order-2 bileşik** bir cevap üretiyor.
>
> **Canlı iz (3 koşumun 2'sinde birebir):**
> ```
> §KN: formül okundu: ort_oee = kullanılabilirlik × performans × kalite
> §KN: hat kırılımında 8 segment ve 3 bileşen ölçüldü
> §KN: RAM 3 akran ortalamasıyla kıyaslandı → farkın kaynağı performans
> §KN: RAM 3 içinde vardiya kırılımı açıldı → 3. Vardiya (00-08)
> ```
> ⊙ Sonuç `(RAM 3 × 3. Vardiya)` **artı** formül bileşeni (`performans`) — yani
> **dikey (formül) + yatay (segment)** ayrıştırma bir arada. Adtributor'ın kendisi
> dikey ekseni hiç yapmaz.
>
> **Gerçekten kalan boşluk dar:** parçaları **tek başına sıradan** olan bir bileşik
> (Adtributor'ın asıl açığı) **kılavuzlu iniş**le bulunamaz; onun için **tüketici**
> bir kombinasyon araması gerekir.
>
> 🔴 **KARAR: tüketici arama BUGÜN YAZILMADI — ve gerekçesi ölçülmüş:**
> ① Kombinatoryal patlama, raporun kendi `§10.5` uyarısıdır (CHI 2018: *«içgörülerin
> %60+'ı yanlış»*) ve kart **`E3`'ü ön koşul** ilan ediyor.
> ② `E3` bu oturumda ölçüldü: **p-değeri yok** → BH uygulanamıyor; elimizdeki tek şey
> **tarama beyanı** (yazıldı).
> ③ Tenantlarımızda *parçaları sıradan bir bileşik kök* bulunduğuna dair **hiçbir
> ölçüm yok**.
> ⊙ Yani bugün tüketici arama yazmak, **ölçülmemiş bir ihtiyaç için ölçülmemiş bir
> gürültü kaynağı** eklemek olurdu. Önce böyle bir kökün var olduğu **ölçülmeli**.
>
> *Bir yeteneği eklemeden önce, onsuz neyi kaçırdığımızı ölçmek gerekir.*

### E1 · Adtributor — yatay eksen

| | |
|---|---|
| **ÖNCE** | `§KN` **dikey** ayrıştırma yapıyor (formül bileşenleri) ve **layer-1'de kilitli**; **bileşik segment** (`İstanbul × Mobil`) aranmıyor |
| **SONRA** | `app/adtributor.py` (~85 satır): `EP = (A−F)/(A_top−F_top)` + **JS sürprizi**; eşikler `T_EP=%67`, `T_EEP=%10`, **top-3** |
| **dosyalar** | yeni `app/adtributor.py` · `app/kok_neden.py` (çağrı) |
| **dış dayanak** | Adtributor (NSDI'14) 128 gerçek anomalide **>%95** · HotSpot bileşikte **F1 >%90** ↔ Adtributor **<%15** · `riskloc` (MIT) **doğrulama referansı** olarak yanımızda |
| **curl (3)** | ① tek boyutlu kök → bugünküyle **aynı** ② bileşik kök → **yeni** cevap ③ kök **hiçbir boyutta değilse** → dürüst beyan (PSqueeze deseni) |
| **risk** | ⚠ Ölçüm gürültüsü kök neden diye sunulabilir → **E3 ön koşul** |

### ✅ E2 · Jensen-Shannon sürprizi — **TAMAMLANDI (2026-08-11)**

> 🔴 **KURUCU ÖRNEK KENDİ KODUMUZDA ÜREDİ.** Adtributor'ın (NSDI'14) örneği
> `contribution`'a verildi: `toplam 100→50 · X: 94→47 · Mobile: 5→1 · Tablet: 1→2` →
> çıktımız **«X — net değişimin %94,0'ı»** dedi ve X'i 1. sıraya koydu. Ama **X'in payı
> hiç değişmedi** (`94/100=%94` → `47/50=%94`): X bir sebep değil **işin kendisidir**.
>
> ✅ `contribution._surprizi_isle` (Jensen-Shannon) + `surpriz_notu` + `ask.py` bağlantısı.
> Ölçülen çıktı:
>
> | segment | delta | pay | sürpriz | sürpriz payı |
> |---|---|---|---|---|
> | **X** | −47 *(en büyük)* | %94 → %94 | **0.0000** | **%0,0** |
> | Mobile | −4 | %5 → %2 | 0.0048 | %40,8 |
> | Tablet | +1 | %1 → %4 | 0.0070 | **%59,2** |
>
> **Beyan:** *«X» en büyük hareketi taşıyor ama **payı değişmedi** (%94 → %94) — yani bu
> bir **sebep değil, ölçeğin kendisi**. 🔴 Dağılımı en çok değişen: «Tablet» (%1 → %4).*
>
> ⚠ **FORECAST GEREKMEDİ.** Adtributor `F` (beklenen) ister; bizim `F`'imiz **önceki
> dönemin kendisidir** ve `yoy.compute` onu `*_gecen` kolonunda **zaten** veriyor. Bir
> tahmin motoru eklemek (`E5`), elimizdeki **ölçülmüş** taban dururken **uydurulmuş** bir
> taban kurmak olurdu. ⊙ Yani `E5` bu adımın ön koşulu **değilmiş**.
>
> 🔴 **SIRALAMA DEĞİŞTİRİLMEDİ** — bu kartın kendi risk satırı (*«bugünkü cevapları
> değiştirir; ölçüm gerekir, tahmin değil»*). Eklenen bir **ölçü** ve onun **beyanıdır**;
> sessiz yeniden sıralama her mevcut cevabı oynatırdı.
>
> **Canlı kanıt:** *«bu yıl müşteri bazında ciro»* → *«neden değişti»* → not: *«…payı
> değişmedi (%100 → %100) — yani bu bir sebep değil, ölçeğin kendisi»*, iz: `§E2: sürpriz`.
> Kapı: `tests/test_e2_surpriz.py` (7, kurucu örnek birebir) + katkı yüzeyi **87 yeşil**.
>
> ⏭ **KALAN:** `kok_neden`'in kendi *«en büyük segment»* satırı (iz: *«§KN: en büyük
> segment EGE KNIT…»*) hâlâ mutlak katkıya bakıyor — aynı ölçü oraya da bağlanmalı.

### E2 · Jensen-Shannon sürprizi 🔴

| | |
|---|---|
| **ÖNCE** | `§KN-toplam` **en büyük segmenti** seçiyor; **sürpriz hesaplanmıyor** |
| **SONRA** | Aday, **dağılımı değişen** segment olmalı |
| **dış dayanak** | 🔴 Adtributor'ın **kurucu örneği**: gelir 100$→50$; *Veri Merkezi X* düşüşün **%94'ünü** açıklıyor ama **dağılımı değişmemiş** — gerçek kök **Mobile+Tablet**. *«Yalnız explanatory power kullanan her katkı analizi **büyük segmentleri sistematik olarak suçlar**»* |
| **curl** | *«müşteri bazında ciro → neden»* → **EGE KNIT** (en büyük) yerine **dağılımı değişen** mi geliyor |
| **risk** | Bugünkü cevapları değiştirir — **ölçüm gerekir**, tahmin değil |

### ✅ E3 · Tarama genişliği beyanı — **TAMAMLANDI (2026-08-11)** · BH DEĞİL, ve nedeni ölçüldü

> 🔴 **BENJAMINI-HOCHBERG UYGULANAMADI — ve bu bir eksiklik değil bir ÖLÇÜM SONUCU.**
> Kart *«FDR düzeltmesi (BH)»* diyor. Ölçüldü: **bu depoda p-değeri YOK** —
> `stats.z_skorlari` bir **z-kesimi** uygular (`|z| ≥ 2`, asgari 4 gözlem, sıfır-varyans
> kapısı), bir hipotez testi değil. BH **p-değerlerini** sıralar; z'yi p'ye çevirmek
> **normallik varsayımını dayatmak** olurdu ve o varsayım ölçülmedi.
> ⊙ `§E2`'de forecast için verilen kararın aynısı: *elimizde olmayan bir tabanı
> uydurmaktansa, elimizdekini beyan etmek.*
>
> ✅ **Kartın kendi azaltma satırı uygulandı** (*«elenen sayısını beyan et»*, `§98.1`):
> `stats.tarama_beyani` — tek sahip; `interpret`'in aykırılık sinyalinde çağrılıyor.
>
> **Canlı ölçüm (3 soru):**
>
> | soru | aday | işaret | şansa düşen |
> |---|---|---|---|
> | aylık ciro trendi | 30 | **3** | ~1,4 → şansın **üstünde** |
> | aylık fire oranı trendi | 30 | **1** | ~1,4 → **şans düzeyinde** |
> | aylık enerji tüketimi | 30 | **3** | ~1,4 |
>
> ⊙ **İkinci satır tam olarak CHI 2018'in sorunudur** (*«içgörülerin %60+'ı yanlış»*):
> 30 adayda tek bir işaret, beklenenden **fazla değildir**. Kullanıcı bunu artık
> görebiliyor; öncesinde yalnız *«Olağandışı değer — z=+2,8»* okuyordu.
>
> ⚠ Şans payı **varsayımıyla birlikte** yazılır (*«**normal** bir dağılımda ~%4,6»*).
> Tabloda olmayan bir eşik için oran **hesaplanmaz, uydurulmaz**.
> Kapı: `tests/test_e3_tarama_beyani.py` (6) + istatistik yüzeyi **172 yeşil**.

### E3 · FDR düzeltmesi (Benjamini-Hochberg)

| | |
|---|---|
| **ÖNCE** | Soru başına **yüzlerce hipotez** taranıyor (`_en_ayristiran` süpürmesi, `derinles` kombinasyonları, `contribution` segment taraması); **düzeltme YOK** |
| **SONRA** | BH düzeltmesi **veya** keşif/doğrulama ayrımı |
| **dış dayanak** | 🔴 **Zgraggen, Zhao, Zeleznik, Kraska (CHI 2018): *«In our experiment, **over 60% of user insights were false**»***. ⚠ Power BI'ın ham `p<0,05` Wald eşiği de düzeltme yapmıyor — **sektör de yapmıyor**, ama bu bizi haklı çıkarmaz |
| **curl** | Aynı soru → **kaç bulgu** eleniyor; elenenler gerçekten zayıf mı |
| **risk** | Fazla eleme → *«hiçbir şey bulamadım»* |
| **azaltma** | Elenen sayısını **beyan et** (*«N aday incelendi, M'i istatistiksel eşiği geçti»*) — `§98.1` disiplini |

### ✅ E4 · Adlandırma — **YAPILDI: ad DEĞİŞTİ, sınır YAZILDI** *(2026-08-12)*

> ⊙ **Ölçüldü — iddia nerede görünüyor:** arka uçtaki *«kök neden»* anmalarının **hemen
> hepsi yorum/docstring**. Kullanıcının okuduğu iddia **ön-uçtaydı** ve **üç satırdı**:
> `aria-label="Kök nedeni incele"` · başlık **Kök nedeni incele** ·
> `ilişkili veri (kök neden adayı)`. *Bir yanıltmanın büyüklüğü kod içindeki sıklığıyla
> değil, kaç kişinin okuduğuyla ölçülür.*
>
> ✅ `Kök nedeni incele` → **`Katkıyı incele`** · `kök neden adayı` → **`katkı adayı`**
> 🔴 **Ve asıl istenen yapıldı — SINIR YAZILDI.** Panel açılır açılmaz okunan tek satır:
> *«Bu bir **katkı analizidir**: hangi kalemin farkın ne kadarını açıkladığını ölçer.
> **Nedensellik iddiası değildir** — birlikte değişmek, birinin ötekine sebep olduğunu
> göstermez.»* ⚠ Gizlenmiyor, küçültülmüyor, katlanmıyor.
>
> ⊕ **Kapı iki gerçek sızıntı daha buldu** (ilk `grep` görmemişti): `kok_neden.py:874`
> ve `ask.py:5618` — ikisi de **kullanıcıya dönen** metindi, ikisi de düzeltildi.
> Muafiyetler **sınıfıyla** yazılı: LLM istemi · yönetici paneli açıklaması · iz satırı.
> *Bir muafiyet, sınıfı yazılmadan verilirse muafiyet değil bir delik olur.*
>
> Kapı: `test_e4_adlandirma.py` (5) — ön-uç metnini **ve** arka uçtaki dizge sabitlerini
> `ast` ile tarar (docstring'ler elenir). Demet kapısı yeşil, taban birebir aynı.

### E4 · Adlandırma *(özgün kart)*

*«Kök neden»* yerine **«katkı analizi»** kullanmayı değerlendir. Tableau kendi dokümanında:
*«Correlation is not causation… **not a tool to prove or disprove hypotheses**»*. Gerçek
nedensel iddia **nedensel grafik beyanı** ister (DoWhy sınıfı) ve bizde **yok**; uydurmak
`GG8`'i çiğner. ⊙ **İsimlendirme başlı başına bir yanıltma kaynağıdır.**

---

## FAZ 5 · TEMİZLİK VE STRATEJİ

| # | iş | not |
|---|---|---|
| ✅ **F1** | Arşivlenmiş `wren-engine` bağımlılığı **KAPATILDI** *(2026-08-11)* · ⟳ **VE ORTAMDAN DA TEMİZLENDİ (2026-08-12, kullanıcı kararı)** | Dört ölçüm: ① konteyner hâlâ **`Restarting (1)`**, `restart: always` ile **sonsuz çökme döngüsü** ② `grep -rn "WREN_ENGINE_URL\|wren-engine" backend/ --include="*.py"` → **SIFIR** (env geçiliyordu, **hiçbir kod okumuyordu**) ③ `CLAUDE.md` zaten yazmış: motor **in-process**, subprocess yok ④ ön-uç/betiklerde 8080 kullanımı yok. **Silinmedi, yorumlandı** (`MIMARI §10`). Ürün doğrulandı: `/health` ok, curl `cube` + `cube+llm` çalışıyor |
> 🔴🔴 **⟳ 08-12 — KARAR DOĞRUYDU AMA ORTAM ONU UYGULAMAMIŞTI.** Kullanıcı sordu: *«eski o
> kaldırdığımız Wren motorunu ayağa kaldırmadın di mi? bu riski almayalım, onu temizle ve
> **kural olarak ekle**»*. Ölçüldü: koşan `wren-engine` konteyneri **YOKTU** (risk
> gerçekleşmemişti) — **ama** koşan backend konteyneri hâlâ
> `WREN_ENGINE_URL=http://wren-engine:8080` taşıyordu, çünkü o konteyner satır yoruma
> alınmadan **önceki** compose'dan yaratılmıştı. Ve arşivlenmiş **imaj (679 MB)** diskte
> duruyordu.
>
> ⊙ Değişken **ölü**ydü (okuyan Python kodu: **0**, kendi ölçümüm) — ama *bir bağımlılığı
> yapılandırmadan çıkarmak onu ortamdan çıkarmaz; çalışan süreç, yazıldığı günün
> yapılandırmasını taşır.*
>
> ✅ **Yapılan:** backend temiz env ile yeniden yaratıldı (47 değişken, kalıntı 0) ·
> kalıntı konteyner kaldırıldı · imaj silindi · `:8080` boş · **canlı curl** ile yeni
> motorun çalıştığı doğrulandı (`source=cube`, gerçek SQL, gerçek satır).
> 🔴 **Kural yazıldı** (`backend/CLAUDE.md` değişmezler) **ve kapıya bağlandı**:
> `tests/test_arsivlenmis_motor_dirilmiyor.py` (4, mutasyonla doğrulandı).
>
> ⚠ **Yan ölçüm — bir araç tuzağı kayda geçsin:** temizliği `docker-compose up -d
> --force-recreate` ile denedim; `docker-compose` **v1** bu makinede yeni imaj biçiminde
> `KeyError: 'ContainerConfig'` ile düşüyor **ve düşerken eski konteyneri durduruyor** →
> backend **40 saniye kapalı** kaldı. Geri alındı, `docker run` yoluyla tamamlandı.
> *Bir temizlik aracının kendisi, temizlediği şeyden daha büyük bir risk olabilir.*
>
> ⚠ **VE ADI BENZEYENİ SİLME:** `demo/wren-project` **yeni** motorun model dizinidir
> (`DIMA_PROJECT_DIR`); eski motorun kalıntısı sanılıp silinirse **her cevap düşer**.
> Ayrım kapının içine yazıldı. *İki şeyin adı benziyorsa, kapı onları ADIYLA değil
> YOLUYLA ayırmalıdır.*
| ✅ **F2** | `wren cube query --sql-only` ↔ `cube_sql` **yan yana kondu** *(2026-08-11, motor `0.13.2`)* | ⊙ Sorunun cevabı: **hiçbiri.** Beş vakanın **dördü bayt bayt aynı**, çünkü `cube_sql` **zaten `wren_core.cube_query_to_sql`'i çağırıyor**; `cube_router`'ın satırları SQL değil **Türkçe NL → CubeQuery** üretiyor ve motor onu hiç yapmıyor. 🔴 **Ve ölçüm daha büyüğünü buldu: motor desteklemediği alanı SESSİZCE DÜŞÜRÜYOR** — `order`→`ORDER BY` yok · `having`→`HAVING` yok · ay-listesi→DATE'i ay-metniyle kıyaslayan `WHERE` (sıfır satır). Üçü de **uyarısız, `source="cube"` rozetiyle** yanlış sayı üretirdi. Sarmalayıcılarımız fazlalık değil **koruma**; gerekçe artık ölçülü ve kapılı (`test_f2_motor_siniri.py`, 8). **F5'in ön koşulu budur.** ⚠ Prob `order`'ı yanlış şekilde geçip sahte bir kusur üretti; canlı curl *«en yüksek cirolu 5 müşteri»* → **doğru azalan sıralı** |
| ✅ **F3** | MDL'deki **31 `relationship`** — 🔴 **TEŞHİS ESKİMİŞTİ, ÖLÇÜMLE ÇÜRÜTÜLDÜ** *(2026-08-11)* | ⊙ `§11.2` *«cube_router'da sıfır anma»* diyordu; ölçüldü — ilişkiler **sekiz katmanda** kullanılıyor ve router'daki sessizlik bir kusur **değil**, `§38.4`'ün **JOIN planlayıcı yasağının kendisidir** (router ilişkiyi bilmemeli, sıradan bir boyut görmeli). **Cube derleyicisi** `compose._compose_relationship_dimensions` → **10 `expose:`** bloğu → **9 türev boyut**, **7 cube**'a; model katmanı (`dry_plan`) `is_calculated` kolondan **gerçek JOIN** üretiyor. Fan-out sertifikası **31/31 ölçülü, hepsi `saglikli`**. **Canlı:** `bölüm bazında oee` → `cube=oee · dims=['bolum'] · 5 satır`. 🔴 **Bulunan tek gerçek boşluk KAPATILDI:** soyağacı cümlesi *«…(1 sıçrama).»* ile bitiyor, `"certified" in yanıt` → **False**'tu — ölçüm vardı, **söylenmiyordu**. `fanout.beyan()` (tek sahip, `KAT-1`) eklendi; artık *«— bu ilişki fan-out açısından ölçüldü, sayılar şişmiyor»* |
| ✅ **F4** | `modernbert-tr-reranker` — 🔴 **ÖLÇÜLDÜ → YAPILMAYACAK**, ve ölçüm **daha büyük bir şey buldu** *(2026-08-11)* | ⊙ Reranker'ın ön kabulü: *«darboğazımız SIRALAMA»*. Ölçüldü — **değil**. Dört şirkette **506 yanlış-cube** vakasının tamamı tek bir sınıf: bir terimi **iki küp de meşru olarak sahipleniyor** (`elektrik` → `enerji_makine` ⊕ `surdurulebilirlik`; `satış` → `ticaret` ⊕ `mal` ⊕ `karlilik`). 🔴 **Cross-encoder bunu «daha iyi tahmin ederek» çözerdi** — yani beyan edilebilir bir belirsizliği **sessiz bir seçime** çevirirdi; `§101.1` ve *beyan kültürü*'nün tam da önlemek için var olduğu şey. Üstelik korpus **iyileşir**, ürün **kötüleşir** — bu depoda üç kez ölçülmüş desen. ⊕ Maliyet: `torch` + ~500 ms, ki rapor `stanza`'yı **aynı gerekçeyle** elemişti (`§13.6`). ⊕ Ve tesisat zaten var: `metrik_kaydi.hakem` `_match_cube`'un **ilk satırında** çağrılıyor. **Doğru iş F4 değil, `§SH` (aşağıda).** |
| ✅ **§SH-2** | **§SH'nin İKİ BORCU KAPATILDI — ve taban her ölçütte İYİLEŞTİ** *(2026-08-11)* | 🔴 **Taşınan teşhis YANLIŞTI ve okumak düzeltti:** korpus satırı *«takip turunda hakem odağı eziyor»* demiyordu, *«dönemsiz soruda sessizce dönem varsaymak»* diyordu — ve canlı ölçüm dönem beyanının **her yolda var** olduğunu gösterdi. **Gerçek kök başkaydı:** hakem, *daha spesifik* bir ölçü eşleşmesini eziyordu. *«elektrik faturası»* sorusunda `enerji_tesis` **17 karakterlik** tam eşleşme yaparken `surdurulebilirlik` yalnız **8 karakterlik** `elektrik`i eşleştiriyor, hakem `elektrik` için karar verdiği için **kısa eşleşme uzununu deviriyordu** → `enerji_makine`'de öyle bir ölçü yok → **R10 → cevapsız**. Dokuzunun **tamamı** bu desendi. ⊙ Kural bu depoda **zaten yazılıydı** (ÖLÇÜ-KANITI / `_daha_spesifik_olcu_sahibi`): *hakem bir **beraberlik** hakemidir.* ⊕ İkinci `KAT-1` kusuru: ikame beyanı **çürümüş otoriteyi** gösteriyordu (*«elektrik surdurulebilirlik konusudur»* — oysa ilan edilmiş sahip `enerji_makine`) ve chip'i **yanlış küpe** yolluyordu. ⊕ Gövde büyüme kapısının isteğiyle `metrik_kaydi.hakem_secimi`'ne **taşındı**; tavan **1960 → 1953** indirildi (*kazanılan alan sessizce harcanmaz*). 🔴 **KORPUS:** doğru-cube **%95,6** · cevapsız **%19,7** *(taban %19,9'dan da İYİ)* · doğru **95** *(geri geldi)* · `sessiz_yanlış` **8 → 7** · `R10` **23 → 14**. Kapı: 165 hedefli yeşil + korpus yeşil |
| ✅ **§SH** | **SAHİPLİK KARARLARI ŞEMAYA ULAŞMIYOR** → **ÇÖZÜLDÜ** *(2026-08-11)*. Karar `packs/**sektor/boyahane**/sahiplik_kararlari.yml`e taşındı; `katmanli_kararlar()` `compose`'un katman sırasını (modül → sektör → şirket) izliyor, **çekirdek öneri kalıyor**. ⊙ `FAZ 3.1`'in gerilemesi artık **yapısal olarak imkânsız**: ölçüldü, `katmanli_kararlar(gitas)` → **`{}`** — dosyayı hiç okumuyor. 🔴 **KORPUS:** doğru-cube **%94,4 → %95,5** *(+1,1 puan)*. **Bedeli de yazılı:** cevapsız %19,9 → **%20,2** (R10 14 → 23), doğru 95 → 92 / devir 2142 → **2146** (araç *«kayıp değil DEVİR»* diyor), `sessiz_yanlış` **8 → 8** (bileşim değişti). ⚠ Ve canlı curl bir **`KAT-1` ihlali** yakaladı: cevap doğru küpe gidiyor, yanına *«…«elektrik» bu katalogda surdurulebilirlik konusudur»* beyanı düşüyordu — sistem **kendi kararını kusur ilan ediyordu**. `uyum._hakem_onayli()` ile kapatıldı (ikinci eşleştirici **yazılmadı**, aynı kayıt okunuyor). Kapı: 122 hedefli yeşil + korpus yeşil | **506 yanlış-cube**'un ölçülen kökü — ve bulan şey `F4`'ün **reddedilmesiydi** | Canlıda ölçüldü: `metrik_kaydi` şemada **VAR** (62 çakışan terim), `hakem()` `_match_cube`'a **bağlı**, bayrak `beta`, `demo/packs/cekirdek/sahiplik_kararlari.yml` **12 tarihli, gerekçeli, insan kararı** taşıyor — ve **`SAHİPLİ: 0`**. Karar şemaya `onerilen_sahip` olarak düşüyor, `hakem()` ise `sahiplenilen_terimler`'i okuyor → **`hakem('elektrik') → None`**. ⚠ Ve bu **bilinçli**: `FAZ 3.1` kararları doğrudan uygulamış, korpus **%93,2 → %92,6** gerilemişti (`gitas` erişim %72 → %69), çünkü **boyahane'nin** alan bilgisi **her** tenant'a dayatılıyordu. `3.1b` onu «öneri»ye indirdi — *«tek tıkla kabul edilir»* dedi ve **kimse tıklamadı**. 🔴 Teşhis: dosya `packs/**cekirdek**/` altında, yani **çekirdek** katmanda; oysa `elektrik → enerji_makine` bir **boyahane sektör** kararıdır (her iki küp de boyahane sektöründe). Karar **doğru katmana** taşınırsa `gitas` onu hiç görmez ve dayatma sorunu **yapısal olarak** yok olur. **Kazanç tahmini: 506 yanlış-cube vakasının çoğu** |
| ✅ **F5** | ~~Motorda olanı yeniden yazan **~2.000 satırı** kademeli devre dışı bırak~~ → 🔴 **ÖLÇÜLDÜ, RAKAM ÇÜRÜDÜ — SİLİNECEK KOD YOK** *(2026-08-11)* | ⊙ **`rls.py` 380 boşa gitmiş değil, TAM TERSİ:** dosyanın kendi ilk satırı *«MOTOR-SEVİYESİ RLS — `always_filter`'ın yerini **motor devralır**»*. Bu satırlar motorun işini tekrar etmiyor, **işi motora devreden göçün kendisi**; `wren_service.py`'de **sekiz** çağrı yeri + iki kapı dosyası. *«`RowLevelAccessControl` sembolü çağrılmamış»* sembol düzeyinde doğru, **yetenek düzeyinde yanıltıcı**: RLS motora **manifest üzerinden** verilir ve `rlac_manifesti()` tam olarak onu yapar. ⊙ **`dataset.py` 161'de `register_csv` FARKLI İŞ yapıyor:** `ingest_file` 42 · `build_mdl` **28** · rol/sinonim/slug **33** — oto-MDL, kolon rolü, Türkçe sinonim ve **Excel** motorda **yok**; slug'lama dosyanın kendi **güvenlik** gerekçesi. ⊙ **Manifest ~1.490 `F5`'in değil `F12`'nin kalemi** ve `F12` bir *silme* değil *«motorun daha fazlasını kullan»* maddesi. ⊙ Ve **rapor bunu zaten işaretlemişti** (`§11.6`: *«boşa giden kod değil, **bağlanmamış kod**»*). ⚠ Motor yüzeyi **14 sembol** (rapor 15 diyor) — kapıya kilitlendi. 🔴 **F5'in açığa çıkardığı GERÇEK borç:** `rls.py` ödenmiş·bağlanmış·kapılı ama `motor_rls`/`motor_cls` **kapalı** → iki ölçülmüş baypas (JOIN · Discovery ham SQL) **hâlâ açık**. Bu bir *silme* değil **teslim** işi, ve güvenlik sınırı değiştirdiği için kendi pilotunu ister (⚠ `shadow ≡ off` ölçülmüştü). Kapı: `test_f5_bosa_giden_kod.py` (4) |
| ✅ **F6** | **Apache Ossie pilotu** — 🔴 *«bir küp»* değil, **23 küpün TAMAMI** koşuldu *(2026-08-11)* | ⊙ Ossie **zaten yazılmıştı** (`app/ossie.py` 324 satır: ithal+ihraç+round-trip kapısı+iki uç+üç test dosyası) — oturumun **on sekizinci** «yazılmış ama…» vakası, ve **en sinsi biçimi**: 🔴 **ihraç ucu canlıda HTTP 500 veriyordu.** Uç `schema()` şeklini besliyor (`measures: ["ort_oee"]` — dizeler), `disa_aktar` `packs/` şeklini bekliyordu (`[{name, expression}]`). **Round-trip kapısı bunu göremedi çünkü fikstürü `packs/` şeklindeydi** — *kapı, ucun hiç görmediği bir şekli sınıyordu.* ⊕ `_pack_sekline_getir()` (tek sahip, idempotent, `disa_aktar` gövdesi **değişmedi**); anahtar adları **ölçüldü, tahmin edilmedi** — üç tahminim yanlıştı (`measure_labels` yok, küp etiketi `display`, `non_additive` ayrı liste). ⊕ **İkinci kusur:** boyut kökeni `olculdu:saglikli` derken **ilişkiler damgasızdı** ve `belge()` onları — doğru biçimde fail-closed — `olculmedi` diye ihraç ediyordu; yani `§F3`'te **31/31'ini ölçtüğümüz** ilişkileri karşı tarafa *«ölçmedik»* diye veriyorduk. Kusur ihraçta değil **beslemedeydi**; `_damgala_fanout` artık ilişkiyi de damgalıyor (aynı `fanout.rozet`, `KAT-1`). 🔴 **CANLI PİLOT:** `GET /connections/{cid}/export-semantic` → **HTTP 200 · 58 KB** · `datasets` **23** · `relationships` **31** *(hepsi `olculdu:saglikli`)* · **135 ölçü** `ai_context` taşıyor · ölçü sinonimi **677/677** · round-trip kaybı **SIFIR**. `ossie_ihrac` **`off` → `beta`** (bayrağın **kendi yazılı şartı** karşılandı); `ossie_ithal` ⟳ **`beta`ya ALINDI (2026-08-12)** *(önce `off` KALDI denmişti)* — o bir **yazma** yolu ve gerçek müşteri modeliyle pilotu yapılmadı. Kapı: `test_f6_ossie_canli_sekil.py` artık **fikstürü değil `schema()`'nın kendisini** ihraç ediyor |
| ✅ **F7** | 🔴 **Kapsamı İLAN ET** — **özü zaten teslim edilmişti; kaçak bir yol kapatıldı** *(2026-08-11)* | ⊙ `app/yetenek.py`'nin **üç kutusu** (`anlamadim` · `yapamiyorum` · `yapmiyorum`) raporun istediği ayrımı zaten yapıyor ve `ask.py`'de **iki** çağrı yeri var — **yirmi birinci** «yazılmış ve bağlı» vakası. Canlı: *«gelecek ay ciro tahmini»* → *«forecast **v1'de yok** — bu bir eksiklik değil, **bilinçli bir karar**… **Yapabildiğim:** geçmiş eğilimi gösterebilirim»* + üç chip. 🔴 **Ama bir yol kaçaktı:** *«hava durumu nasıl»* (kataloğun tamamen dışında) → `rows=0` · `cube=None` ve kullanıcı şunu okuyordu: *«Bu cevap 1 adımda üretildi: 1. **ANLAT** — bulguları cümleye çevirir (`kaynaklar`=``)»* — yani kapsam beyanı değil, bir **planlayıcı iz satırı**. **Kök:** `plan_kosucu.dogrula` referans alanlarını **listeyi gezerek** denetliyor; `kaynaklar=[]` için döngü **hiç dönmüyor** → plan geçerli sayılıyor → makbuz basılıyor. Oysa fonksiyonun kendi cümlesi yazılıydı: *«bir anlatı, anlatacağı bulgulardan önce yazılamaz»* — hiç bulgusu **olmayan** bir anlatı, o ihlalin **en saf hâli** (konum değil **varlık** sorunu). Boş referans listesi artık **reddediliyor**; red garsona döner, onarım tükenirse kapsam beyanı konuşur. Kapı: `test_f7_bos_anlati.py` (6) |
| ⊘ **F7-b** | *«Katalog dışı soruda Discovery'ye düşmeden kapsam ilan et»* — **ÖLÇÜLDÜ, YAPILMADI** | Doğru yüklem **yok**: `cube_router.veri_niyeti_var` var ve bağlı, ama ölçüldü — *«hava durumu nasıl»* için **`True`** dönüyor (sosyal kapı için yazılmış, katalog-kapsamı için değil). Yeni bir yüklem icat etmek `ADR-0008`'e girer ve `yetenek.py`'nin kendi uyarısına çarpar: *«Bir sınır beyanı, cevaplanabilen bir soruyu **asla reddetmemelidir**»*; bir yanlış-pozitif reddin bedeli `§101.1` gereği kusurun kendisinden ağırdır. ⊙ Bugünkü davranış **dürüst**: Discovery `SELECT 'Hava durumu verisi bulunmamaktadır.'` üretiyor — uydurma sayı **yok**, rozet `llm:*`, ve `CLAUDE.md`'ye göre her `adhoc` zaten bir **arıza raporudur**. *Ölçülmemiş bir yüklem yazmaktansa, ölçülmüş bir dürüstlüğü korumak.* |
| ✅ **F8** | **Doğruluk sayısı YAYINLANDI** — [`belgeler/DOGRULUK.md`](../DOGRULUK.md) *(2026-08-12, `ddc6fa3`)* | ⊙ Yeni ölçüm aracı **yazılmadı**: var olan `nl_corpus.json` yayımlanabilir bir artefakta çevrildi. **Sayı:** doğru-küp **%95,6** (payda 11.237) · semantik vaka **%94,4** (591) · cevapsız **%19,7** (14.957) · sessiz-yanlış **7** (2.286). 🔴 **Payda oyunu yapmamanın somut karşılığı üç şey:** ① **iki payda birden** yayımlanır (ham tur ⊕ semantik vaka) ve **şişme katsayısı 25,3×** açıkça yazılır — *«14.957 soruda %95»* demek teknik olarak doğru ama yanıltıcıdır ② **en düşük şirket tabloda kalır** (`gitas` %89, ortalamayı aşağı çeker) ve dördü de adıyla yayımlanır ③ **bilinen körlükler yazılır** — sorular katalogdan üretildiği için **yazım hatası yolu hiç sorulmuyor**, korpus `route()`'u ölçer Discovery'yi **görmez**. ⊕ Payda seyreltmesinin neden yasak olduğu **ölçümle** anlatılır (`gitas` düştü → payda 445→342 → doğruluk **%93,2→%94,3 ÇIKTI**). ⊕ Yeniden üretme komutu + sha + tarih **künye olarak** verilir. 🔴 **Ve belge çürüyemez:** `test_f8_dogruluk_yayini.py` (6) her sayıyı `nl_corpus.json`'dan **yeniden hesaplayıp** karşılaştırır; şirket tablodan düşerse ya da oran bayatlarsa **kapı kırmızı**. `00-INDEKS.md`'ye yeni bir bayatlama sınıfı olarak eklendi: *«dışarıya verilen, kapıyla canlı tutulan»* |
| ⊘ **F9** | Kama/fiyat/kanal kararı | ⚠ **§37.4: taze arama oturumu olmadan stratejik karara temel yapılmamalı** ⟳ **KARAR:** **KARAR VERİLMEDİ ve VERİLMEDİĞİ YAZILDI (`§40.4`)** — `§37.4`'ün şartı: *«taze arama oturumu olmadan stratejik karara temel yapılmamalı»*. Şart karşılanmadı. |

---

## 14.9 🔴 RİSK PANOSU — «riskli bir şey yapıyoruz»

| risk | nerede | erken uyarı | geri alma |
|---|---|---|---|
| **Kapsam kaybı** (budama fazla) | B1 | `cevapsız` oranı **artarsa** | bayrak `sema_daraltma` |
| **Bağlam kirlenmesi** (çelişkili örnek) | B2 | aynı soruya **farklı cevap**; gecikme sıçraması | bayrak `vqr_few_shot` |
| **Sonsuz onarım** | B4 | süre/token sıçraması | tavan **2** + `Butce` |
| **Plan bozulması** | C1 | üretilmiş `enum` ≠ bugünkü 15 | `KURAL B` kapısı (bayrak yok, **kilit** var) |
| **Injection** | C3 | serbest metin hücreleri modele dönüyor | MCP bayrağı |
| **Gürültü kök-neden** | E1/E2 | bulgu sayısı patlar | E3 **ön koşul** |
| **Bakım borcu** | B3/D2 | bir ay sonra doğruluk düşer (**%95→%65**) | pack ile **aynı PR** kuralı |
| 🔴 **Ölçüm aracının yalanı** | **hepsi** | bu oturumda **dört kez** oldu | **her adımda curl** — araç değil **sistem** ölçülür |

## 14.10 SIRA ÖZETİ

```
FAZ 0  A1 garson korpusu · A2 cevapsız · A3 şişme · A4 kurulum süresi     2-3 gün
FAZ 1  B1 budama → B2 few-shot → B3 instructions → B4 repair              1-2 hafta
FAZ 2  C1 kayıt birleşimi → C2 bütçe/stall → C3 MCP                       1 hafta
FAZ 3  D1 sayaç → D2 taksonomi → D3 biçim kararı → D4 ön-uç → D5 takip    1-2 hafta
FAZ 4  E1 Adtributor → E2 sürpriz → E3 FDR → E4 adlandırma                1 hafta
FAZ 5  F1-F9 temizlik + strateji                                          paralel
```

🔴 **Her fazın sonunda BİR tam kapı. Faz içinde curl.**

⊙ **Ve FAZ 0 olmadan hiçbirinin işe yarayıp yaramadığı bilinemez** — bu raporun tamamının
teşhisi tam olarak budur.

---

## 14.11 🔴 §11 ve §13'ün KALAN KALEMLERİ — faza yerleştirilmiş

> Denetimde bulundu: §11 (Wren) ve §13 (açık kaynak) **27 kalem** öneriyor, ilk plan
> yalnız **9'unu** adım yapmıştı. Kalan **18'i** aşağıda — her biri **hangi faza**,
> **neden orada**, ve **maliyeti** ile.

### FAZ 0'a eklenenler — ölçüm altyapısı

| # | kalem | kaynak | ne yapar | maliyet |
|---|---|---|---|---|
| ⊘ **A5** | **`syrupy`** (MIT, **sıfır bağımlılık**) + `pytest-regressions` | §13.5 | **Snapshot testi**: cevabın *tam metnini* kilitler. ⊙ Bu oturumda `§SB` iz satırı bir altın testi kırdı ve **iyi ki kırdı** — snapshot bunu sistematik yapar | saatler ⟳ **KARAR:** **REDDEDİLDİ (`§40.4`)** — snapshot cevabın TAM METNİNİ kilitler; bu deponun 30+ kapısı bilinçle YAPIYA bağlı. *Onaylanarak geçilen bir kapı, kapı değildir.* | ⟳ **08-12: GEREKÇE SAYILDI ve BEŞ KAT GÜÇLÜ ÇIKTI.** Red *«30+ kapı bilerek yapıya bağlı»* diyordu ama sayı **hiç sayılmamıştı** (bir denetim ajanı bunu *«doktriner gerekçe»* diye bildirdi). `ast` ile ölçüldü: **432 kapı dosyasının 167'si** (%38,7) `ast`/`inspect` ithal ediyor — yani yüklemini **yapıya** kuruyor, metne değil. ⊙ Snapshot testi tam bunun tersidir: çıktının **biçimini** dondurur. *Bir reddi sayarak doğrulamak, onu güçlendirir ya da çürütür; sayılmamış bir red bir alışkanlıktır.*
| ⏸ **A6** | **`test-suite-sql-eval`** deseni (Apache-2.0, EMNLP 2020) | §13.5 | **Damıtılmış çoklu mini veri seti**: `yil = 2026` ile `yil > 2025` **tek** DB'de aynı sonucu verir, **birden çok** mini DB'de ayrışır. ⊙ *«15 gizli kırmızı, 2'si gerçek kusur»* ölçümümüzün panzehiri | günler ⟳ **KARAR:** **PARK (`§40.5`)** — ikinci bir DB ister; korpus `sessiz_yanlis`'ı zaten ölçüyor (7/2.286). Şart: korpus bu sınıfı kaçırdığı ÖLÇÜLENE kadar. |
| ✅ **A7** | **`EHRSQL` reliability score** (CC-BY-4.0, NeurIPS 2022) | §13.5 | Kapsam-**içine** red **ağır negatif** · kapsam-**dışına** red **pozitif** · kapsam-dışına uydurma **en ağır negatif**. ⊙ *«Dürüst red başarı değil»* doktrininin **matematiksel formu** — tek başına bir CI kapısı | günler ⟳ **KARAR:** **İLKESİ ZATEN UYGULANIYOR (`§40.3`)** — kapsam-dışına red pozitif (`§⑧`), kapsam-içine red negatif (`cevapsız` %19,7 yayında). Eksik olan tek SKORDA birleştirme: bir sunum işi. |
| ✅ **A8** | **Inspect AI'ın `stderr`'i** (standart hata) | §13.5 | *«20 senaryoluk paydada %85 ile %90 arasındaki fark **gürültü mü**»* sorusunun tek cevabı. ⊙ **«Payda kutsaldır»** ilkesinin doğal tamamlayıcısı | saatler ⟳ **KARAR:** **YAPILDI (`§40.6`)** — `DOGRULUK.md`'ye **Wilson %95 güven aralığı** eklendi: doğru-küp **[%95,2–%96,0]** (±0,38) · semantik vaka **[%92,3–%96,0]** (±1,87) · cevapsız **[%19,1–%20,3]** · sessiz-yanlış **[%0,15–%0,63]**. ⚠ Ne yasakladığı da yazılı: **aralıkları örtüşen iki sayıyı «iyileşme» ilan etmek**. |
| ⊘ **A9** | **`promptfoo`** (saf MIT) — **yalnız garson için** | §13.5 | A1 korpusunu koşturacak hazır harness. ⚠ Mevcut `eval/run.py` zaten selective-prediction yapıyor; **yerine değil, garson için** | günler ⟳ **KARAR:** **REDDEDİLDİ (`§40.3`)** — `eval/run.py` zaten selective-prediction yapıyor; ikinci harness aynı işi ikinci bağımlılıkla satın almaktır. |
| ✅ **A10** | **`Dr.Spider`** deseni (Apache-2.0, ICLR 2023) | §13.5 | **17 pertürbasyon** · `robustness gap = acc(orijinal) − acc(bozulmuş)`. 🔴 `göre/bazında/bazlı` üçlü aşırı-yüklemesi bizi **üç kez** ısırdı çünkü **ölçülmüyor** | günler ⟳ **KARAR:** **YAPILDI (`§40.6`)** — ve gerekçesi bu turda ÖLÇÜLDÜ: `göre`/`bazında` **üçlü değil DÖRTLÜ** aşırı-yüklenme (dördüncüsü *«dolar bazında»* = para birimi, canlıda yanlış beyan üretti). Kapı `tests/test_a10_saglamlik_farki.py` — LLM'siz/ağsız, üç ölçülmüş bozulma sınıfı (yazım·çekim·edat), liste **canlıdan** gelir. |
| ⏸ **A11** | **TURSpider / TUR2SQL / BIRDTurk** | §13.6 | Türkçe NL→SQL veri setleri (8.659 / 10.809 / 10.962). ⊙ **Kendi korpusumuzun dışında bir çapa** — bugün hiç yok. ⚠ TUR2SQL lisansı belirsiz, TURSpider HF kopyası **CC BY 4.0** | günler ⟳ **KARAR:** **PARK (`§40.5`)** — dış çapa değerli; şart: lisans+şema eşleme, ve `§26` garson ölçümü ondan önce. |

### FAZ 1'e eklenenler — getirme ve Türkçe

| # | kalem | kaynak | ne yapar | maliyet |
|---|---|---|---|---|
| ⊘ **B5** | **`Snowball` Türkçe kök bulucu** (BSD-3, 34,4M indirme/ay) | §13.6 | 🟢 **Gölge ölçümde dene** — sıfır bağımlılık, mikrosaniye. ⚠ Kendi belgesi: *«stems only **noun and nominal** verb suffixes»* → `arttı`yı **çözmez**, ama `satışlarımızın`/`cirodaki`/`bazında` tam kapsamda | günler ⟳ **KARAR:** **REDDEDİLDİ (`§40.4`)** — kendi belgesi *«stems only, not lemmas»*; Türkçe'de ekler anlamı TAŞIR (`§G/AJ0`: *«arttı»* bir FİİL). Kök bulucu o ayrımı siler. | ⟳ **08-12: RED AYAKTA, ama ÖLÇÜM BİR KAPSAM AYRIMI GÖSTERDİ.** Bir denetim ajanı *«gerekçe route tüketicisine ölçülmüş, B1'in kapsama yükleminde ek-toleransı ayrı bir iş»* dedi ve ölçümü haklı: `§B1` daraltması **30 soruda 14'ünde (%47) fail-open** veriyor ve tetikleyici çoğu kez **ek**: `durum` sinonimi `durumunu` token'ını açıklamıyor, yani **tutulan küp kelimeyi zaten kapsadığı hâlde** budama iptal ediliyor. ⊘ **Ama `B5` reddi bundan etkilenmiyor:** Snowball bir **kök bulucu**dur ve `route`'un **anlam kararına** girerdi; buradaki ihtiyaç bir anlam kararı değil, *«bu kelime zaten kapsandı mı»* sorusudur. 🔴 **Ve o iyileştirme `§38.4` DOKUNULMAZI'na değiyor** (Türkçe morfoloji) → **ayrı bir kalem** olarak, kendi ölçümüyle açılmalı. ⏸ Şartı **gözlenebilir**: önce fail-open'ın **maliyeti** ölçülsün (budanmayan katalogda garson doğruluğu düşüyor mu — bugün ölçülemiyor, `§26` park), sonra `_AD_YAPAN_EKLER`/`turetme._kokler` gibi **var olan kapalı sınıflarla** (yeni sözlük YAZILMADAN, `ADR-0008`) denensin. *Bir güvenli varsayılanın (fail-open) maliyeti ölçülmeden, onu daraltmak bir iyileştirme değil bir kumardır.*
| ⊘ **B6** | **Zemberek sözlüğü** (Apache-2.0) — **yalnız sözlük** | §13.6 | ~130k köklü sözlük; `_catalog_vocabulary`'yi besler. ⚠ **Kodu alma**: README *«slow maintenance mode»*, son sürüm **2019**, Maven Central'da **yok** | günler ⟳ **KARAR:** **REDDEDİLDİ (`§40.4`)** — README *«slow maintenance»*; ve sözlük bugün kataloğun KENDİ kelimelerinden besleniyor. Dış sözlük, katalogda olmayan bir kelimeyi *tanıyormuş* gibi gösterir. |
| ⏸ **B7** | **M-Schema** (XiYan-SQL) | §13.7 | **LLM-dostu şema temsili** — B1'in (şema daraltma) **çıktı biçimi** olarak değerlendirilmeli. Ham JSON yerine model için tasarlanmış gösterim | günler ⟳ **KARAR:** **PARK (`§40.5`)** — `B1`'in çıktı biçimi; `B1` ✅ ama biçim değişimi `KURAL B` ister. Şart: `§26`. | ⟳ **08-12: «ALARMSIZ» İDDİASI ÇÜRÜDÜ.** Bir denetim ajanı bu parkın şartını *«yalnız düzyazı, açılışı haber verecek kapı yok»* diye bildirdi. Ölçüldü: `M-Schema` **`§40.1` envanterinin *«kodda İZ YOK»* satırında** ve `tests/test_envanter_iddiasi_taze.py` onu `ast` ile **12.026 kod adına karşı** ölçüyor — sembol kodda belirdiği gün kapı **kırmızı** verir. ⊙ Alarm vardı, ajan onu **başka bir dosyada** aradı. *Bir kapının yokluğunu iddia etmek, onu aradığın YERİN kapsamıyla sınırlıdır.*
| ⏸ **B8** | **`ManifestExtractor.resolve_used_table_names`** | §11.1 | *«verilen SQL'i ayrıştır, kullanılan tablo adlarını döndür»* → **B1'in doğrulaması**: budanmış manifest, üretilen SQL'in ihtiyacını **gerçekten** karşıladı mı | saatler ⟳ **KARAR:** **PARK (`§40.5`)** — `B1`'in doğrulaması. Şart: `B1`'in bir kırmızısı ölçülene kadar. | ⟳ **08-12: «ALARMSIZ» İDDİASI ÇÜRÜDÜ.** Bir denetim ajanı bu parkın şartını *«yalnız düzyazı, açılışı haber verecek kapı yok»* diye bildirdi. Ölçüldü: `resolve_used_table_names` **`§40.1` envanterinin *«kodda İZ YOK»* satırında** ve `tests/test_envanter_iddiasi_taze.py` onu `ast` ile **12.026 kod adına karşı** ölçüyor — sembol kodda belirdiği gün kapı **kırmızı** verir. ⊙ Alarm vardı, ajan onu **başka bir dosyada** aradı. *Bir kapının yokluğunu iddia etmek, onu aradığın YERİN kapsamıyla sınırlıdır.*

### FAZ 3'e eklenenler — grafik ve biçim

| # | kalem | kaynak | ne yapar | maliyet |
|---|---|---|---|---|
| **D6** | 🔴 **Draco hard kısıtları** | §9.2 · §13.4 | `stack_without_summative_agg` (**yüzde toplama YASAK**) · `bar_area_without_zero` · `area_bar_with_log` · `size_nominal` · `shape > 8` · `color > 20`. ⊙ **Bu oturumda yüzdeleri topladım; literatür bunu 2018'de hard hata ilan etmiş** | günler |
| **D7** | **AVA `ckb` + `purpose` alanı** (MIT) | §13.4 | **51 grafik tipi + `dataPres` şeması + `purpose`** (Trend/Comparison/Rank/Proportion) YAML'e port. ⊙ `purpose` **niyet nesnemize doğal kanca** — D3'ün biçim kararını besler. ⚠ **Bağımlılık alma** (`npm i @antv/ava` = **257 MB**) | günler |
| **D8** | **CompassQL etkinlik tabloları** (BSD-3) | §13.4 | Sıralama için: `Q × TIMEUNIT_T` agregalı → `line: 0, area: −0.1, bar: −0.2`. ⊙ **Draco'nun aksine zaman serisini DOĞRU yapıyor** (Draco'da `temporal` scale tipi yok, ölçüldü) | günler |
| **D9** | **Metabase `candidates` + `agent_error` deseni** | §13.3 | Belirsizlikte `400` + **makine-okunur nesne**: `{"error":"ambiguous_measure","candidates":[…],"agent_error":true}`. ⊙ *«Dürüst red başarı değil»* **ve** *«şüphede garson»* kurallarını **aynı anda** karşılıyor; MCP açılınca (C3) **zorunlu** hâle gelir | günler |

### FAZ 4'e eklenenler — kök-neden altyapısı

| # | kalem | kaynak | ne yapar | maliyet |
|---|---|---|---|---|
| ⏸ **E5** | **`ruptures`** (BSD-2) + **`statsforecast`** (Apache-2.0) | §13.8 | 🔴 **E2'nin (JS sürprizi) ÖN KOŞULU**: Adtributor `F` (baseline/forecast) ister — *«beklenen değer»* olmadan *«sürpriz»* hesaplanamaz. Ayrıca *«mart'ta düştü»* iddiasını **doğrular** | günler ⟳ **KARAR:** **PARK (`§40.5`)** — `E1` Adtributor'ın ön koşulu; `§25` layer-1 kilidi açılmadan gereksiz. |
| ⊘ **E6** | **Explanation Tables** (VLDB 2014) — **oku, uygulama** | §13.8 | Adtributor'ın kardeşi; **kompakt, örtüşmeyen kural kümesi**. §10.4'ün *«bileşik segment»* boşluğuna **HotSpot'tan daha yorumlanabilir** ikinci çözüm ailesi | okuma ⟳ **KARAR:** **OKUNDU ve ERTELENDİ (`§40.4`)** — kartın kendisi *«oku, uygulama»* diyor. Adtributor'ın kardeşi, **bileşik segment** boşluğuna aday; o boşluk `§25` ile layer-1'de kilitli. |

### FAZ 5'e eklenenler — motorda olanı bırakma

| # | kalem | kaynak | ne yapar | maliyet |
|---|---|---|---|---|
| ⊘ **F10** | **`SessionContext.dry_run` / `register_csv` / `register_parquet`** | §11.1 | `wren_service.dry_plan` sarmalayıcısı ve **`dataset.py` (161 satır)** yerine motorun kendi API'si | günler ⟳ **KARAR:** **`§F5`'TE ÖLÇÜLÜP REDDEDİLDİ (`§40.2`)** — `dataset.py`'nin 161 satırı dökümlendi; `register_csv` o işin **hiçbirini** yapmıyor (`ingest_file` 42 satır yalnız yaklaşıyor). |
| ⊘ **F11** | **`RowLevelAccessControl` + `validate_rlac_rule`** | §11.1 | **`rls.py` (380 satır)** yerine. ⚠ Güvenlik sınırı — **çok dikkatli**, kademeli, A/B ile | hafta ⟳ **KARAR:** **`§F5`'TE ÖLÇÜLÜP REDDEDİLDİ (`§40.2`)** — *«sembol düzeyinde doğru, yetenek düzeyinde farklı»*; ve `§F12`'nin üçüncü ölçümü RLS enjeksiyonunun manifesti **v2-uyumsuz** yaptığını gösterdi. |
| ⊘ **F12** | ⟳ **ÜÇÜNCÜ ÖLÇÜM (2026-08-12): ⑦'nin ÖN KOŞUL KAPISI KÖRDÜ — ve koşul ZATEN SAĞLANMIYOR.** 🔴 `is_backward_compatible` *«RLS uygulanmış manifestte de True»* diyordu; **boş bir doğruydu**: varsayılan tenant (`demo-boyahane`) hiçbir cube'da `always_filter` beyan etmiyor, yani `manifeste_yaz` her iki kademede de **bayt bayt aynı** manifesti döndürüyordu — test *«RLS uygulanmış»* diyordu ama RLS **hiç uygulanmamıştı**. İzole + taze derlenmiş `gulteks` (logo-3) ile ölçüldü: ham **True** · `shadow` (0 kural) **True** · 🔴 **`on` (3 kural: `cari`·`mal`·`ticaret`, hepsi `CANCELLED = 0`) → `False`**. Kontrol izole (aynı manifest, yalnız enjeksiyon farkı) ve kusur **varsayılan** manifestte de yeniden üretiliyor (tek yapay `always_filter` → 1 kural → `False`) — yani bulgu tenant'a değil **enjeksiyonun kendisine** bağlı. ⊙ Bu tam olarak kartın *«bir gün RLS enjeksiyonu manifesti v2-uyumsuz hâle getirirse kapı bayrağı açmadan önce konuşur»* cümlesinin gerçekleşmesidir; kapı konuşamamıştı çünkü **kural olmayan tek tenant'a** bakıyordu. *Bir ön koşul kapısını, koşulun oluşamadığı yerde koşmak, kapıyı kurmakla kurmamak arasındaki farkı yok eder.* Kapı artık **görüyor**: `test_RLAC_ENJEKSIYONU_v2_UYUMUNU_BOZUYOR`. *(ilk ölçümün metni aşağıda korunuyor)* · **`Manifest` · `to_manifest` · `migrate_manifest_json` · `is_backward_compatible`** — **ÖLÇÜLDÜ, İKİYE AYRILDI** *(ilk ölçüm 2026-08-12)*. ⊘ **Göç YAPILMIYOR:** beş projenin `schema_version`'ı da **5**, yani göçülecek **sürüm farkı yok**; API *«maximum supported version is 4»* diyor ve base64'te de *«JSON error»* — **girdi biçimi belgesizce çelişiyor**. ⚠ Ve `wren_project.yml`'nin `schema_version`'ı ile motorun *«layout version»*'ı **aynı şey olmayabilir**; denk saymak ölçülmemiş bir eşitlik kurmak olurdu. *«Göç bedava» ancak göçülecek bir şey varsa kazançtır* — on üçüncü ölçülmüş «yapma». ✅ **AMA YARISI HEMEN DEĞERLİ:** `is_backward_compatible(manifest)` → **`True`**, hem temiz hem **RLS uygulanmış** hâlde — bu **`motor_rls` borcunun ön koşulu** ve artık kapılı. 🔴 **VE ÖLÇÜM BORÇ ⑦'NİN ŞEKLİNİ DEĞİŞTİRDİ:** `rls(shadow)` ve `rls(on)` → **0 kural**; demo katalogda RLS **hiç kural enjekte etmiyor**, yani `motor_rls`'i açmak burada **hiçbir şey değiştirmezdi** (daha önce ölçülen *«`shadow ≡ off`»*'un sebebi budur). Eksik olan **bayrak değil KURAL**. *Bir korumayı açmadan önce, koruyacak bir şeyi olduğunu ölçmek gerekir.* Kapı: `test_f12_manifest_uyumu.py` (**5**) — sürüm tekliğini, v2 uyumunu ve kural sayısını kilitler; ayrışırlarsa karar **yeniden okunur** | §11.1 | `compose.py` + `mdl_writer.py`'nin manifest kısmı (**~1.490 satır**). ⊙ Özellikle **`migrate_manifest_json`** — pack sürümü değişince **göç bedava** | hafta ⟳ **KARAR:** **ÖLÇÜLDÜ, AÇILAMIYOR (`§40.9`)** — izole+taze `gulteks`: `is_backward_compatible` ham **True** · shadow **True** · 🔴 **`on` (3 kural) → False**. RLS enjeksiyonu manifesti **v2-uyumsuz** yapıyor. ⊙ Kapı önce **kör**dü (kural olmayan tek tenant'a bakıyordu) — *bir ön koşul kapısı, koşulun sağlanmadığı bir örnekle sınanmadıkça boş bir doğrudur.* |

### 14.12 Toplam ve dürüst yargı

| faz | asıl adım | eklenen | toplam |
|---|---|---|---|
| FAZ 0 | 4 | **+7** | 11 |
| FAZ 1 | 4 | **+4** | 8 |
| FAZ 2 | 3 | — | 3 |
| FAZ 3 | 5 | **+4** | 9 |
| FAZ 4 | 4 | **+2** | 6 |
| FAZ 5 | 9 | **+3** | 12 |
| | **29** | **+20** | **49** |

🔴 **49 adım bir yol haritası değil, bir KATALOGDUR.** Hepsi *«yapılmalı»* değil,
*«düşünüldü ve kaydedildi»*. §14.13 hangilerinin gerçekten kritik yolda olduğunu söyler.

### 14.13 🔴 KISA YOL — beş iş, ~2-3 hafta, hissedilen iyileşmenin ~%70'i

Eğer **tek bir şey** yapılacaksa sırası budur:

| # | iş | süre | neden bu |
|---|---|---|---|
| ✅ 1 | **B2** — `few_shot_block`'u garsona bağla | **saatler** ✔ bitti | Fonksiyon **zaten yazılmış**, Discovery'ye (%1,7) bağlı, garsona (%37) değil. Dışarıda **+17…+23 puan** ölçülmüş |
| ✅ 2 | **A2** — `cevapsız` metriğini manşete al | **saatler** ✔ bitti | %21,8 görünür olmadan **hiçbir iyileşme kanıtlanamaz** |
| ✅ 3 | **D3'ün iki kuralı** — *«tek değer → grafik yok»* + *«≤3 satır → cümle»* | **saatler** ✔ bitti | ⊙ **İkisi de `viz.py`'de ZATEN VARDI ve ateşliyordu** (curl ile doğrulandı). Açık olan yarı **öneri şeridiydi**: chip dizisi `6,6,6,6,5,6,6,5` → **`4,6,2,4,4,4,6,3`**, tek sahip `app/bicim.py` |
| ✅ 4 | **B1** — şema daraltma | **saatler** ✔ bitti | Katalog **23.729 → 1.270-23.729 karakter** (⟳ **08-12: %0–95**, ilan edilen `%71-90` iki kip karıştırdığı için hem tabanı hem tavanı yanlıştı). ⊙ `extract_by` **kullanılmadı** — ölçüldü: o model/view budar, garson istemi küplerden kurulur. Fail-open **kanıta** bağlı ve **8 sorunun 2'sinde ateşliyor** (budama yok, katalog tam) — *«8/8 kapsama»* doğru ama *«hep budanıyor»* diye okunuyordu; 0 kayıp |
| ✅ 5 | **B4** — reflect+repair (tavan 2 tur) | **saatler** ✔ bitti | `onarim_tutma_yuzde` **25 → 90**. ⊙ Kazancın büyüğü 2. turdan değil **çare yönergesinden** (9 onarımın 7'si ilk turda). Kartın `EE-11` senaryosu **zaten geçiyordu** — asıl kusur `/stats/plan`'da duruyordu |

⚠ **A1 (garson korpusu) hakkında bir düzeltme:** planın ilk hâli **300-500 soru** diyordu.
**Fazla iddialı.** Anthropic *«~20 sorguyla başlayın»*, Hex **30-50** kullanıyor.
🟢 **50 soruyla başla, büyüt.** Aksi hâlde FAZ 0 bir haftayı yer ve **tıkaç olur**.

⚠ **C1 (iki sistemi birleştirme) hakkında:** mimari olarak doğru ama **canlı yolda refactor**
ve kullanıcı **hiçbir şey hissetmiyor** (`KURAL B` gereği davranış aynı kalacak).
🟢 **C3 (MCP) açılmadan önceye** bağla — o zaman iki kayıt **gerçekten** sorun olur.

---

## 14.14 🔴 SON DENETİM — bölüm bölüm taranan ve EKSİK bulunan **ON** iş *(⟳ 2026-08-12: «dokuz» yazıyordu; tablolar **10** satır taşıyor — `A12·A13·A14·B9·B10·B11·D10·D11·E7·F13` — ve `§14.15`'in **59**'u ancak **10** ile tutuyor)*

> Rapordaki **her bölümün** eylem gerektiren bulgusu plana karşı tarandı. Dokuzu eksikti;
> aşağıda faza yerleştirildi. ⚠ *Bu tarama dört kez «var» sanıp yanlış eşleşme buldu —
> anahtar kelime araması bir kapı değildir.*

### FAZ 0'a — ölçüm

| # | iş | kaynak | neden |
|---|---|---|---|
| ⟳◐ **A12** | 🔴 **Çok turlu belleği TUR BAZINDA ölç** | §29.3-5 · §21.14 | SParC: Turn 1 **%38,6** → Turn 3 **%3,7** → **Turn ≥4 %1,1**. Bizde tur bazında **hiç ölçüm yok** — *«3. turda ne kadar doğruyuz»* bilinmiyor. ⊙ A1 korpusuna **çok turlu bir dilim** eklenmeli ⟳ **KARAR:** **YAPILDI (`§40.8`)** — korpus artık her kaydı `tur` ile etiketliyor ve rapora **tur bazında cevaplanabilirlik** tablosu koyuyor. 🟢 Canlı (3 zincir · 11 tur): **Tur 1-5 hepsi %100**. SParC'ın *«Turn≥4 → %1,1»* çöküşü **yeniden üretilmedi** — sebebi yapısal (SParC açık şemada **birebir SQL eşleşmesi** ölçer; biz kapalı semantik katmanda, odak taşıma deterministik). ⚠ İki sınır yazılı: bu **cevaplanabilirlik**tir doğruluk değil · payda 11. | ⟳ **08-12 DENETİMİ — ✅ bir KOD işaretiydi, bir ÖLÇÜM değil.** Tur kırılımı **yazıldı** (`lab/garson_korpusu.py:302` *«## Tur bazında cevaplanabilirlik (`§A12`)»* başlığını basıyor) **ama diskteki artefakt onu HİÇ taşımıyor** (`grep 'Tur bazında' lab/reports/garson_korpusu.md` → **0**): kod, raporu üreten son koşumdan **sonra** eklendi. ⊙ Ve `§0.6` karnesinin **10. satırı** (*«🟡 tur bazında ÖLÇÜLMÜYOR»*) bu ✅'ten **daha doğruydu** — çelişki, karnenin lehine çözüldü. 🔴 Kapı da **yok**. ⚠ Birim düzeltmesi: rapor *«3 zincir · 11 tur»* diyor, `KORPUS` **2 zincir · 8 tur** taşıyor (tur≥2 paydası **6**). *Bir yeteneği yazmak onu ölçmek değildir; ölçüm bir ARTEFAKTTIR, bir satır değil.*
| ✅ **A13** | 🔴 **Planın neden AYRIŞMADIĞINI ölç** | §17.6 | ⟳ **ÖLÇÜLDÜ ve TEŞHİS ÇÜRÜDÜ (`§17.6`, 2026-08-11): PLAN AYRIŞIYOR.** `/stats/plan` ile 10 planlayıcı-tetikleyen soru: tek adım **%60 → 5/24 = %21** · çok adım **19/24 = %79** · ortalama adım **3,3** · düşen plan **0**. 🔴 **Üç hipotezin ÜÇÜ DE çürüdü:** ① istem ayrıştırmayı engellemiyor ② deterministik-önce kapısı erken kapanmıyor (10 soruda **24** planlayıcı çağrısı) ③ `tek_adimli` kısayolu kural hâline gelmemiş. ⚠ Örneklem farkı dürüstçe yazılı: rapor **kütükteki 20 kaydı** (üretim karışımı) saymıştı, bu ölçüm planlayıcıyı **bilerek tetikleyen** 10 soruyla yapıldı; ortak soru *«planlayıcı koştuğunda ayrıştırıyor mu»* ve cevabı **evet**. ⊙ Kartın *«C1/C2'den ÖNCE ölçülmeli»* şartı **yerine getirildi** ve sıralamayı doğruladı |
| ✅ **A14** | **Hava boşluğunu ölç ve YAYINLA** | §29.2 | ✅ **YAYINLANDI (2026-08-12): [`belgeler/HAVA-BOSLUGU.md`](../HAVA-BOSLUGU.md).** Ölçüm **12 canlı cevap**, tek tek curl. 🔴 **İki katman ölçüldü ve BİRİNCİSİ DAHA GÜÇLÜ:** ① **9/12 cevapta LLM anlatı basamağı HİÇ koşmadı** — cümleyi deterministik kod kurdu, sayı modele gitmedi bile ② kalan 3'ünde LLM koştu ve sayılar **perdelendi**: **20 yer tutucu · 0 bozulan · 0 düşen iddia**, anlatı guard'ı doğruladı. ⊙ Ve `§D11-b`+`§18.5` düzeltmeleri bu turda katman ①'i **genişletti** (yinelenen ölçü ve uydurma üstünlük kalkınca daha çok cevap şablonda kaldı). ⚠ **Dört körlük yazılı:** payda küçük (12 — oran değil **varlık** kanıtlar) · Discovery yolu ayrı (güvencesi `§⑧`) · `bozulan=0` bir tavan değil bir ölçüm · `guard_muaf` bir gevşetmedir ve içeriği yayında. Kapı `tests/test_a14_hava_boslugu_yayini.py` (**9** ⟳08-12; 7 bayattı) — sayıları değil **mekanizmayı** korur: yer tutucu · iddia kapısı · anlatı guard'ı · şablon yolu |

### FAZ 1'e — hakem ve bağlam

| # | iş | kaynak | neden |
|---|---|---|---|
| ⏸ **B9** | 🔴 **İki-sağlayıcılı LLM hakem** | §7.3 | AUROC ölçümü: `dry_plan` (**query executability**) **0,500 — tam şans**; execution self-consistency **0,613**; string self-consistency **0,675**; tek GPT-4o hakem **0,770**; 🟢 **iki-sağlayıcılı topluluk 0,822** (ECE 0,031). ⊙ **Bizim `k=3` oylamamızın tavanı ~0,675** — CHASE-SQL'in dersi: *darboğaz aday üretimi değil **SEÇİM***. ⚠ Oylamanın **yerine değil, ÜSTÜNE** ⟳ **KARAR:** **PARK, şartı yazılı (`§40.8`)** — kartın ölçümü sağlam (`dry_plan` AUROC **0,500 tam şans** · self-consistency **0,613**), hakem gerçekten değerli. Ama iki sağlayıcı = **iki kat kota** ve kazancı ölçecek taban yok (`§26` park). *Kazancı ölçülemeyen bir maliyeti varsayılan açmak, ölçümü bir törene çevirir.* **Şart: `§26`.** |
| ✅ **B10** | 🔴 **SKILLS — metodoloji markdown'ları** *(B3'ten AYRI)* | §36.1-5 | ⚠ **B3 `instructions.md` = iş sözlüğü** (*«fire'yi kg konuşuruz»*). **B10 = metodoloji**: kohort · funnel · retention · **YoY-oranı** · what-if — her biri bir **markdown iş akışı**. ⊙ Anthropic: **skill'siz %21 → skill'li >%95**; *«bir skill'e paketlenebilecek bağlam **fiilen sınırsız**»*. Ve §34'ün beş metodoloji hatası (adım sırası · dedup · pencere · kohort ataması · geri dönüş) **kodda değil METİNDE** yaşar. ⚠ Bakım: **pack ile aynı PR** (bakımsız **1 ayda %95→%65**) ⟳ **KARAR:** **KISMEN KAPANDI (`§D9`, 2026-08-12):** üç metodoloji markdown'ı yazıldı (`yoy-orani.md` · `huni.md` · `kohort.md`) ve kapıya bağlandı (`test_d9_metodoloji_skilleri.py`, 11). Mekanizma + içerik hazır; **bayrak `skills: off`** ve açılış şartı `§26` (garson doğruluk ölçümü) — o PARK'ta. |
| ✅ **B11** | **Ephemeral / karalama sorgusu** | §36.1-4 | Hex'in ölçümü: ajan önce veriyi **görünmez bir sorguyla** tanıyor → *«ilk denemede doğruluk yükseliyor»*. Bizde **yok**. ⊙ B4 (repair) ile kardeş: biri **hatadan sonra**, öteki **hatadan önce** ⟳ **KARAR:** **AMACI KARŞILANIYOR (`§40.3`)** — Hex soru-başına gizli sorgu koşar; biz kurulum anında **bir kez** profilliyoruz: **121 boyutun 120'si (%99)** değer taşıyor. Mekanizma farklı, sonuç aynı, maliyet daha düşük. |

### FAZ 3'e — kapsam ve tanım

| # | iş | kaynak | neden |
|---|---|---|---|
| ✅ **D10** | 🔴 **Tanım çakışması yönetimi** | §29.3-6 | ⟳ **ÖLÇÜLDÜ ve KAPATILDI (2026-08-12).** Katalogda **9 ölçü adı** birden çok küpte geçiyor; **üçünün formülü FARKLI**: `toplam_fire_kg` (`oee`: `SUM(hatali_kg)` ↔ `parti`: `SUM(CASE WHEN ilk_seferde_tamam=0 THEN kg END)`) · `toplam_durus_dakika` (`bakim`: `SUM(durus_dakika)` ↔ `oee`: `SUM(planli+plansiz)`) · `ilk_seferde_tamam_yuzde` (payda `SUM(parti_sayisi)` ↔ `COUNT(*)`). Öteki **altısı bayt bayt aynı**. ⊙ Beyan dokuzunu da **aynı cümleyle** geçiyordu; oysa aynı formül bir **kapsam** tercihi, farklı formül bir **TANIM** farkıdır — öteki küpteki sayı *başka bir hesaptır*. ✅ `belirsizlik_chipi.tanimlari_farkli_mi` (yapısal: `measure_expressions` karşılaştırması; ifade beyanı eksikse **fark iddia edilmez**, `§101.1`) + cümle sertleşiyor. 🟢 CANLI: *«fire ne kadar»* → **FARKLI FORMÜLLE** · *«bu yıl bakiye»* → yumuşak (doğru). ⚠ Kendi kusurum: karşılaştırmayı kullanıcının sözcüğüyle (`fire`) yaptım, oysa `measure_expressions` **ölçü adıyla** anahtarlı — fark sessizce sustu, **canlı curl yakaladı**. *Bir sözlüğü yanlış anahtar uzayıyla sorgulamak, «yok» cevabını «fark yok» diye okumaktır.* Kapı `tests/test_d10_tanim_cakismasi.py` (10) |
| **D11** | **Denormalizasyon** | §27.6 | Ölçüm: **3+ tabloda** mevcut sistemler **%20 hata oranıyla** çöküyor. ⊙ Bizde JOIN'i **cube derleyicisi** kuruyor (planlayıcı değil) — yani bu risk **yapısal olarak düşük**. ⚠ Ama **ölçülmedi**: kaç küpümüz 3+ model üstünde? `dimension_origin[*].certified` kaçında `olculmedi`? |

### FAZ 4'e — cebir bütünlüğü

| # | iş | kaynak | neden |
|---|---|---|---|
| ⊘ **E7** | 🔴 **LMDI-I'e geç + sıfır/negatif politikası** | §10.3 | Bugünkü ayrıştırmamız **LMDI-II** ailesinde: artık sıfır ✅, sıra bağımsız ✅ — ama **alt-grup toplanabilirliği YOK**. ⊙ Çok seviyeli iniş (`derinles` → ikinci kırılım) yaptığımızda **katkılar toplanmıyor**; kullanıcı *«bu %30 nereye gitti»* diye sorarsa cevap veremeyiz. ⚠ Ve **`ln(0)` tanımsız**, negatifte LMDI **tanımsız** → politika: sıfır/negatif bileşende **Shapley'e geç ya da dürüstçe sus** ⟳ **KARAR:** **ÖNCÜL YANLIŞ ÇIKTI (`§40.8`)** — ayrıştırmamız LMDI **değil**, saf toplamsal fark (`delta = simdi − onceki`), gövdede **logaritma yok**. `ln(0)`/negatif kaygıları **konu dışı**; alt-grup toplanabilirliği *«yok»* değil **TAM**. LMDI-I↔II ayrımı **çarpımsal** ayrıştırma içindir. ⊘ Geçmek, tam toplanabilir bir yöntemi sıfır/negatifte **tanımsız** bir yöntemle değiştirmek olurdu. Kapı `tests/test_e7_toplamsal_ayristirma.py` (6). |

### FAZ 5'e — agentic'in asıl kilidi

| # | iş | kaynak | neden |
|---|---|---|---|
| ✅ **F13** | ⟳ **İKİNCİ ÖLÇÜM (2026-08-12): «eksik parça» İDDİASI ÇÜRÜDÜ — araç VARDI, KAPI yoktu.** `app/yazma_araclari.py` yazma araçlarını `yan_etki="yazar"` ile tanımlıyor ve `tools.py:818` (`KAYIT = KAYIT + … + _yazma_araclari()`) onu bağlıyor — 🔴 **AMA BİR BAYRAĞA KOŞULLU, ve koşul burada yazılmamıştı** (⟳ ölçüm 2026-08-12): `_yazma_araclari()` `DIMA_YAZMA_ARACLARI` kapalıyken `()` döndürür, yani araçlar kayda **hiç girmez** *(bu bir kusur değil, modülün ilan ettiği tasarım: «bir aracı kayda alıp sonra engellemek, o engelin bir gün unutulabileceği anlamına gelir»)*. Ölçülen iki durum: bayrak **kapalı (varsayılan)** → `KAYIT` **31**, dağılım **`{'yok': 31}`**, yazar araç **0** · bayrak **açık** → `KAYIT` **33**, **`{'yok': 31, 'yazar': 2}`**, araçlar **`dashboards.create`·`schedules.create`** — yani **üç değil İKİ**. ⊙ *Bir bağlamayı koşulunu yazmadan bildirmek, varsayılan durumda var olmayan bir yeteneği var göstermektir.* Eski satır **iki kez** yanılıyordu — yani *«ajan öneremiyor»* yanlıştı. 🔴 Gerçekte eksik olan: `Planlayici.calistir()`'in dört kapısında `yan_etki`·`onay`·`bilet` **hiç geçmiyordu**; `yazma_araclari.py`'nin *«yalnız onay_akisi üzerinden»* değişmezi **düzyazıydı**. ⚠ Ve boşluğu gizleyen ikinci kusur: araçlar zaten çalışmıyordu (ilan edilen `girdi` gerçek imzayla tutmuyor → `TypeError`) — yani güvenlik bir kapı değil bir **uyumsuzluktu**, ve bir `TypeError` bir **red değildir**. ✅ **Beşinci kapı** `_onay_kapisi` (fail-closed: `onay_biletleri` boş) + MCP sızdırmazlığı. ⊘ Açık kalan: `girdi`↔imza adaptörü (`FAZ H`) — `test_YAZMA_ARACLARININ_GIRDI_BEYANI_HALA_UYUMSUZ` onu gizlemiyor. *(ilk ölçümün metni aşağıda korunuyor)* · 🔴 **ONAYLI YAZMA AKSİYONLARI** — **ÖLÇÜLDÜ: KİLİDİN BİR YARISI ZATEN KURULU** *(ilk ölçüm 2026-08-12)*. ⊙ `onay_akisi.py` **289 satır** (durumlar · risk kademeleri · bilet ömrü · **yasak argüman** listesi) · `yazma_araclari.py` *«yalnız `onay_akisi` üzerinden»* · `POST /ask/eylem` **canlı** ve `bilet_dogrula` çağırıyor · şema bilet alanı **fail-closed** · `authorize()`+audit **var**. 🔴 **VE BAYRAĞIN ADI YANILTIYOR:** `onay_akisi: "off"` bir *«onay akışı kapalı»* **değildir** — bayrağın kendi açıklaması *«kapsam İÇİ ve GERİ ALINABİLİR bir eylem İSTEMSİZ koşar… **YAZMA YÜZEYİ BÜYÜMEZ**»* diyor; yani bayrak **istem kaldırır**, onay eklemez, ve `off` **daha muhafazakâr** olandır. *Bir bayrağın adı, ne yaptığının kanıtı değildir.* 🔴 **Gerçekten eksik tek parça:** ajanın yazma aracını **öneri olarak üretmesi** — `tools.KAYIT`'ta `yan_etki="yazar"` araç **yok** (`§C3` o gün `{'yok': 25}` ölçmüştü; **bugün bayrak kapalıyken `{'yok': 31}`, açıkken `{'yok': 31, 'yazar': 2}`**), planlayıcı onu **seçemez**. ⚠ Bu bir kablolama değil bir **karar**: kayda bir `yazar` araç girdiği an `§C3`'ün MCP açılış şartı da kırmızıya döner — **ikisi aynı kararın iki yüzü** ve birlikte verilmeli. Kapı: `test_f13_onayli_yazma.py` (**13**) kurulu yarıyı kilitler, eksik yarıyı **adıyla** bekler | §17.3 · MIMARI §H | Bugün `_yazma_araclari` **bilerek** `llm_araclari` dışında — *«ajan YAZAMAZ»* (`tools.py`'nin dört değişmezinden biri). Sonuç: *«bunu panoya ekle»* · *«her pazartesi yolla»* **yapılamıyor**. ⊙ **Ve bu «agentic'in asıl kilidi»**: yasak **kaldırılmaz, KADEMELENDİRİLİR** — ajan yazma aracını **öneri** olarak üretir → kullanıcı **onaylar** → `authorize()` + audit (**ikisi de zaten var**) → çalışır. Geri alınamaz iş → **senkron onay**; orta risk → kuyruk. ⚠ **Kapı: onaysız hiçbir yazma; her onay audit'e ayrı satır** |

### 14.15 GÜNCEL TOPLAM

| faz | adım |
|---|---|
| FAZ 0 · ölçüm | **14** |
| FAZ 1 · garsonu besle | **11** |
| FAZ 2 · yetenek birleşimi | **3** |
| FAZ 3 · cevap biçimi | **11** |
| FAZ 4 · kök-neden | **7** |
| FAZ 5 · temizlik + strateji + yazma | **13** |
| **TOPLAM** | **59** |

🔴 **Ve §14.13'ün kısa yolu DEĞİŞMEDİ** — beş iş, ~2-3 hafta, hissedilen iyileşmenin ~%70'i.
Yeni **on** kalem o beşliye **girmiyor**; ikisi (A13, B9) **ikinci dalgada**, biri (F13)
**ürün kararı** bekliyor.

⚠ **59 adım bir taahhüt değil, bir KATALOGDUR.** Değeri şurada: *«keşke şunu da
düşünseydik»* denmesin diye **hepsi yazılı** — ama hangisinin kritik yolda olduğu
**§14.13'te** ayrıca söylenmiştir.

---

## 14.16 🔴 WREN MOTORU — kalem kalem denetim, hiçbiri atlanmadan

> §11'in **tamamı** plana karşı tarandı ve **ölçüldü**. ⚠ İlk taramam iki yanlış bulgu
> üretti (aşağıda çürütüldü) — *bir yeteneğin yokluğunu varsaymak, onu aramaktan
> pahalıdır.*

### A · `wren_core`'un 15 sembolü — durum tablosu

| sembol | bugün | plan |
|---|---|---|
| `cube_query_to_sql` | 🟢 **kullanılıyor** | — |
| **`ManifestExtractor.extract_by`** | 🔴 hiç | **B1** (şema daraltma) |
| **`ManifestExtractor.resolve_used_table_names`** | 🔴 hiç | **B8** (B1'in doğrulaması) |
| **`SessionContext.dry_run`** | 🟡 `wren_service.dry_plan` sarıyor | **F10** |
| **`SessionContext.register_csv/parquet`** | 🔴 `dataset.py` (161 satır) yeniden yazmış | **F10** |
| 🆕 **`SessionContext.get_available_functions`** | 🔴 hiç | **F14** ⬇ |
| 🆕 **`SessionContext.transform_sql`** | 🔴 hiç | **F14** ⬇ |
| 🆕 **`SessionContext.pushdown_limit`** | 🔴 hiç | **F14** ⬇ |
| 🆕 **`SessionContext.list_tables`** | 🔴 hiç | **F14** ⬇ |
| **`RowLevelAccessControl` + `validate_rlac_rule`** | 🔴 `rls.py` (380) yeniden yazmış | **F11** |
| **`Manifest` · `to_manifest` · `migrate_manifest_json` · `is_backward_compatible`** | 🔴 `compose.py`+`mdl_writer.py` (~1.490) | **F12** |
| 🆕 **`Manifest.get_cube` / `get_model`** | 🔴 hiç — hedefli erişim | **F12'ye dâhil** |
| `Model` · `SessionProperty` · `RemoteFunction` · `to_json_base64` | 🔴 hiç | **F15** ⬇ *(değerlendirilecek)* |

### B · 🔴 İKİ YANLIŞ BULGUM — ölçümle çürütüldü, kayda geçiyor

**1 · *«Operatörlerin 5'i eksik»* — YANLIŞ.**
`cube_router.py`'de 7 operatör görünce eksik sandım. Ama `app/cube_operatorleri.py`
**motorun 12 operatörünün tamamını** taşıyor ve Intent-JSON şeması ona **bağlı**
(`§M-6`). Dosyanın kendi notu:

> *«Her biri çalışan konteynerin `/cube` ucuna **tek tek gönderildi ve satır döndürdü**…
> Bir operatör buraya **ölçülmeden** eklenemez.»*

⊙ Yani `contains` · `starts_with` · `is_null` · `is_not_null` **garson üzerinden ifade
edilebiliyor**. `route()`'un 7'de kalması **doktrin gereği doğrudur** — *«adı X ile
başlayanlar»* gibi bir kalıp route'a Türkçe öğretmek olurdu. **Eylem gerekmiyor.**

**2 · *«`views` kullanılmıyor»* — YARIM DOĞRU.**
MDL'de **tek bir view** var (`enerji_tesis`) ve `compose.py` onu **üretiyor**. Sorgu
yolunda ayrıca ele alınmıyor ama **küp olarak zaten erişilebilir**. ⊙ Eylem gerekmiyor;
yalnız **yeni view eklenirse** yolun sınandığı bir kapı yok — **F16**'ya not düşüldü.

### C · 🔴 GERÇEK BOŞLUK — granülerlik

| | |
|---|---|
| **motor** | `year · quarter · month · week · day · **hour · minute**` |
| **biz** | `intent_semasi._GRAN_ENUM = ["year","quarter","month","week","day"]` · `plan_onarim.GRANULERLIKLER` **aynı beş** |
| 🔴 **eksik** | **`hour` ve `minute`** |

⊙ **Ve bu, imalat dikeyinde doğrudan kayıp:** vardiya içi analiz, saatlik OEE, duruş
yoğunluğunun saat dağılımı — *«hangi saatlerde duruyor»* sorusu **ifade edilemiyor**.

⚠ **Ve tam olarak `§M-6`'nın kapattığı kusurun ikizi:** operatörler tek kaynağa bağlandı,
**granülerlik bağlanmadı** — iki yerde elle yazılı liste duruyor *(⟳🔴 **08-12 BU CÜMLE BAYAT**: tek sahip `cube_operatorleri.GRANULERLIKLER` kuruldu ve **4 tüketici** ondan türüyor. Ama ölçüm daha fazlasını buldu — aşağı bak)* (`intent_semasi` ve

> 🔴🔴 **⟳ 08-12 — «BEŞİNCİ KOPYA DOĞAMAZ» KAPISI ÜÇ KOPYAYI HİÇ GÖRMEMİŞ.**
> Kusur desende değil **TARAMA BİRİMİNDE**ydi: kapı dosyayı **satır satır** arıyordu ve
> üç etiket sözlüğünün üçü de **iki satıra yayılmış**tı — hiçbir tek satır beşini birden
> taşımadığı için kapı ömrü boyunca hiçbirini görmedi.
>
> | bulunan | ne | yargı |
> |---|---|---|
> | `cube_router._GRAN_LABEL` | chip başlığı, **BÜYÜK** harfli | ⊘ etiket, küme değil |
> | `report._GRAN_ADI` | rapor bölüm başlığı, küçük harfli | ⊘ etiket |
> | `tercih._GRAN_ETIKET` | tercih onay metni, küçük harfli | 🔴 **`_GRAN_ADI` ile BİREBİR AYNI** |
>
> ✅ **Onarım üç katmanlı:** ① tarama **dosya bütününde** yapılıyor ② desen `{`'li
> sözlükleri ve `:` ayırıcısını da kapsıyor *(⚠ ilk genişletmem tuple'ı kaybetti —
> ders ㉚, üç biçim de sınandı)* ③ üç etiket sözlüğü **gerekçesiyle** muaf, ama iki
> yeni kapı bedelini alıyor: `_GRAN_LABEL` sahiple **birlikte büyümeli**, ve
> `_GRAN_ADI ≡ _GRAN_ETIKET` **ayrışamaz** (mutasyonla doğrulandı).
> ⚠ Ayrıca `_GRAN_LABEL[finer]` **doğrudan indeksleme**ydi → sahip `hour` ile büyüse
> chip üretimi **`KeyError`** ile çökerdi; `.get(finer, finer)` yapıldı.
>
> *Bir çok-satırlı gerçeği satır satır aramak, onu hiç aramamaktır.*

`plan_onarim`), yani `KAT-1` ihlali de var.

### D · Plana eklenen dört madde

| # | iş | faz | maliyet |
|---|---|---|---|
| ⊘ **B12** | 🔴 **Granülerliği tek kaynağa bağla + `hour`/`minute` aç** — `cube_operatorleri.py`'nin deseniyle: motora **tek tek gönder, satır döndürdüğünü ÖLÇ**, sonra ekle. `intent_semasi._GRAN_ENUM` ve `plan_onarim.GRANULERLIKLER` o kaynaktan türesin | FAZ 1 | günler ⟳ **KARAR:** **AÇILMIYOR (`§40.7`) — ve gerekçemiz DÜZELTİLDİ.** Motor `hour`/`minute` için SQL **üretiyor** ve sorgu **koşuyor**; engel motorda değil **VERİDE**: `day` ve `hour` **birebir aynı 782 satırı** verdi (`tarih` bir DATE kolonu, gün altı çözünürlük yok). Açılsaydı kullanıcı *«saatlik»* isteyip **günlük** sayı alırdı. Tek sahip (`cube_operatorleri.GRANULERLIKLER`) ✅ yapıldı; açılış şartı artık gözlenebilir: zaman ekseni **TIMESTAMP** olmalı ve iki kova **farklı satır** vermeli. |
| ⊘ **F14** | **`SessionContext`'in dört kullanılmayan yeteneği**: `get_available_functions` (motorun desteklediği fonksiyonları **sormak**, varsaymak yerine) · `transform_sql` · `pushdown_limit` · `list_tables` | FAZ 5 | günler ⟳ **KARAR:** **AÇILMIYOR (`§40.7`).** Ölçüldü: depo motoru `WrenEngine` üzerinden çağırıyor ve o yüzeyin tamamı dört metot — `close·dry_plan·dry_run·query`. **`dry_run` ve `dry_plan` ZATEN kullanılıyor**; `get_available_functions`/`transform_sql` bu yüzeyde **yok** (fabrika arkasında). İlke doğru ama bugün bir kusur ölçülmedi: `dry_plan` her sorguyu koşmadan önce motora doğrulatıyor. ⏸ Şart: `dry_plan`'ın kaçırdığı bir fonksiyon uyumsuzluğu **canlıda ölçülene** kadar. |
| ⊘ **F15** | `Model` · `SessionProperty` · `RemoteFunction` · `to_json_base64` — **değerlendir**; `RemoteFunction` özel iş fonksiyonları (ör. Türkçe tarih/metin) için kapı olabilir | FAZ 5 | okuma ⟳ **KARAR:** **REDDEDİLDİ (`§40.4`)** — bugün karşılığı yok; `RemoteFunction` Türkçe tarih/metin için bir kapı olabilir ama `§B12`'nin motor sözleşmesi işiyle birlikte açılır. |
| ✅ **F16** | **`views` yolu için bir kapı** — bugün tek view var ve sınanmıyor | FAZ 5 | saatler ⟳ **KARAR:** **ZATEN VAR (`§40.2`)** — `tests/test_view_fanout_guard.py` koşuyor: `parti_zengin` view'ının `personel.ad_soyad` üzerinden LEFT JOIN'i bir fan-out riskiydi, `4.7b` en az invaziv düzeltmeyle regresyon kapısına çevrildi. |

### E · Wren'in **ürün** tarafından alınacaklar — plan durumu

| kalem | §11 | plan |
|---|---|---|
| **AI Context Layer → `instructions.md`** | §11.5 | ✅ **B3** |
| **AI Context Layer → `queries.yml`** | §11.5 | 🟡 **B2** bunu **VQR** ile yapıyor — ⊙ *format olarak Wren'inkine yaklaştırmak, ileride `wren context build` ile beslemeyi açar* → **B2'ye not** |
| **LanceDB hibrit erişim** | §11.5 | 🟡 bizde `multilingual-e5-large` + leksik yedek **zaten var** (TR-MTEB birincisi) — **değiştirmeye gerek yok** |
| **`wren serve mcp`** (`query_cube`·`list_cubes`·`describe_cube`·`get_context`·**`recall_queries`**) | §11.5 | ✅ **C3** — ⚠ *`recall_queries` bizim VQR'ımızın MCP karşılığı; C3'te araç adları hizalanmalı* |
| **`skills/`** | §11.3 | ✅ **B10** |
| **`evals/`** | §11.3 | ⊘ **A15 — ÖLÇÜLDÜ, YAPILMIYOR** *(2026-08-12)*: kurulu `wren` paketinde **28 alt modül** var, **`evals` YOK** (`import wren.evals` → `ModuleNotFoundError`) — depoda var, **pakette değil**; desen için klon gerekir. ⊙ Ve desen alınacak yer **boş değil**: `eval/run.py` **392 satır** + `cases.yaml` + `baseline.json` + iki ground-truth + tarihli mutabakat, `lab/kapi.py --hepsi` içinde **koşuyor** ve `test_eval_gate` bir **taban ratchet'i** tutuyor (raporun kendi cümlesi `§13.5`: *«listedeki çoğu araçtan **olgun**»*). ⊙ Üstelik hedefi **`A1`** ve `A1` **PARK** (*«ölçüm tesisatı ürün değildir»*) — park edilmiş bir işe desen aramak parkı dolambaçlı yoldan bozar. **On beşinci ölçülmüş «yapma».** ⚠ `§13.5`'in adlandırdığı **gerçek** eksikler ayrı duruyor: snapshot katmanı · kategori kırılımı · **standart hata**; onlar `evals/`'ı kopyalamakla değil kendi koşumumuza **eklenerek** gelir. Kapı: `test_a15_eval_kosumu.py` (3) — pakete `evals` girerse karar **yeniden okunur** | ~~🆕 **A15** ⬇~~ — *Wren'in kendi eval koşumu; A1'e desen olarak bakılmalı* |
| **`sdk/` (`wren-langchain`, `wren-pydantic`)** | §11.3 | 🆕 **F17** ⬇ — *değerlendir; bugün doğrudan `wren_core` kullanıyoruz* |
| **Değer profilleme (value profiling)** | §11.5 | ⊘ **B13 — ÖLÇÜLDÜ, ÇÜRÜDÜ** *(2026-08-12)*: canlı curl — `SİYAH`→**`Siyah`** (büyük/küçük + Türkçe İ) · `kontinü kasar`→**`KONTİNÜ KASAR`** · `ferraro sanfor`→**`FERRARO SANFOR-1`** (kartın **`Kırmızı-01` vakasının ta kendisi**) · olmayan değer (`kırmızı`) → **satır YOK + beyan + soru** (*«Var olanlar: Açık · Beyaz · Koyu · Orta · Siyah. Hangisini istersin?»*). Yani hem eşleme hem — daha önemlisi — **eşleşmeyenin beyanı** çalışıyor. ⚠ Bir **sahte kusur** karakterize edildi: `siyah renkli partiler` süzgeçsiz görünüyor ama sebep **ölçü yokluğu** (*«Hangi ölçüyü istiyorsun?»*), değer eşleştirici değil. Fark: Wren profillemeyi *build-time istatistiği* tutar, bizimki **çalışma-zamanı bulanık eşleme + katalog enum'u** — aynı sonuç, üstelik **beyanlı**. On dördüncü ölçülmüş «yapma». Kapı: `test_b13_deger_profilleme.py` (5) | ~~🆕 **B13** ⬇~~ — 🔴 Wren'in **6 doğruluk sütunundan biri**, bizde **yok**: kullanıcının yazdığı değer (*«kırmızı»*) DB'deki değere (*«KIRMIZI»*, *«Kırmızı-01»*) **eşlenmeli**. ⊙ `deger_capasi.py` bunun **bir kısmını** yapıyor; Snowflake'in *«relevant literals»* ajanı tam bu iş |
| **`wren cube query --sql-only` kıyası** | §11.4 | ✅ **F2** |
| **`relationships` (31)** | §11.2 | ✅ **F3** |
| **arşivlenmiş `wren-engine` imajı** | §11.3 | ✅ **F1** |

### F · Eklenen üç madde daha

| # | iş | faz | neden |
|---|---|---|---|
| ⟳⊘ **A15** | **Wren'in `evals/` dizinini incele** — A1'in korpus tasarımına desen | FAZ 0 | okuma ⟳ **KARAR:** **⊘ YAPILMIYOR** *(⟳ 2026-08-12: bu satır **PARK** diyordu ve `:4476` **⊘ YAPILMIYOR** diyordu — **aynı kalem, iki işaret**. Ölçüm ayrımı kapattı: kurulu `wren` paketinde `evals` **YOK** (`importlib.util.find_spec('wren.evals')` → `False`, 28 alt modülün hiçbiri). **Var olmayan bir dizin park edilemez** — okunacak bir şey yok, bu yüzden yürürlükteki işaret `⊘`. Eski `PARK` gerekçesi (`A1` kaseti 21→50) `A1`'e aittir ve orada duruyor.* ⊙ *Bir kalemin iki işareti, o kalemi sayılamaz yapar.*) — `A1` kaseti 21→50'ye büyütülürken okunur. |
| ✅ **B13** | 🔴 **Değer profilleme (value profiling)** — Wren'in 6 doğruluk sütunundan biri; `deger_capasi.py`'nin üstüne. *«Kullanıcının kelimesi ↔ DB değeri»* uçurumu | FAZ 1 | günler ⟳ **KARAR:** **YAPILMIŞ (`§40.3`)** — `_enrich_categorical` + `_enrich_cube_dim_values` + `value_index.FuzzyIndex` + `deger_capasi.py`. *«Kullanıcının kelimesi ↔ DB değeri»* uçurumu kapalı (%99 ölçüldü). |
| ⊘ **F17** | `wren-langchain` / `wren-pydantic` SDK'larını değerlendir | FAZ 5 | okuma ⟳ **KARAR:** **REDDEDİLDİ (`§40.4`)** — depo motoru doğrudan çağırıyor ve `§F5` o yolun ince olduğunu ölçtü; SDK katmanı yeni yetenek değil yeni bir sürüm bağımlılığı getirir. |

### 14.17 GÜNCEL TOPLAM

**FAZ 0: 15** · **FAZ 1: 13** · **FAZ 2: 3** · **FAZ 3: 11** · **FAZ 4: 7** · **FAZ 5: 17**
→ **66 adım**

🔴 **Kısa yol (§14.13) yine değişmedi** — beş iş, ~2-3 hafta. Yeni yedi kalemden yalnız
**B12 (saatlik granülerlik)** ürün açısından hızlı bir kazanç *(⟳🔴 **08-12: BU SATIR BAYAT** — `§40.7` kararı **⊘ AÇILMIYOR**'dur ve gerekçesi `motor ≠ veri`: motor `hour`'u kabul etse bile veri o çözünürlüğü taşımıyor)*; imalat dikeyinde *«hangi
saatte duruyor»* sorusunu açıyor.

## 15 · DÜRÜST KAPANIŞ

### 15.1 Kullanıcının üç iddiası — ölçümle karşılığı

| iddia | ölçüm | yargı |
|---|---|---|
| *«Her 20 soruda ciddi sorun çıkıyor, hiç bitmiyor»* | son 5 turda **~5 senaryoda 1 kök**, oran **düşmüyor** | ✅ **DOĞRU** — ve sebebi §4.3'te: kombinatoryal uzay, 131 kural o uzayın 131 hücresi |
| *«Corpus sadece route ölçüyor, her şey garsonda bitiyor»* | route **%35,5** · garson **%37,0**; kapının kendi yorumu: *«garson HİÇBİR TOPLU KOŞUMDA YOK»* | ✅ **TAM DOĞRU** — raporun omurgası |
| *«Biz daha grafik oluştururken binlerce hata alıyoruz»* | 10 canlı senaryo → **10/10 doğru tip**, sıfır *«çizilmedi»*; iki hipotezim çürüdü | ❌ **YANLIŞ TEŞHİS** — grafik katmanı en sağlam parçalardan biri; hata **üstteki basamaklarda** doğuyor ve grafikte **görünüyor** |

*Bir belirtiyi yanlış organa yazmak, tedaviyi de yanlış yere yapar.*

### 15.2 *«Rakipler mükemmel»* — ölçümle karşılığı

Bu **doğru değil**, ve bunu bilmek moral değil **strateji** meselesi:

* **13 üründen 10'u doğruluk sayısı yayınlamıyor.**
* **Power BI Copilot** kapsam dışında **LLM genel bilgisinden uyduruyor**; bağımsız ölçüm
  **%62,5**; uygulamacı: *«3 saniyede DAX üretti, düzeltmem 45 dakika sürdü»*.
* **Databricks Genie**'nin **%84,5**'i **28 soruluk** bir sette (±13 puan).
* **Qlik Insight Advisor** 2019'dan beri var ve kendi topluluğu *«tek bir şirket
  bulamadım»* diyor.
* **Amazon** ürünü 18 ayda **dört kez** yeniden adlandırdı; The Register: *«application
  graveyard»*.
* **Gartner:** *«**Nearly every vendor claims agentic capability. Very few have moved past
  natural-language querying.**»* · agentic analitik projelerinin **%60'ı 2028'e kadar
  başarısız olacak**.
* **MIT NANDA:** kuruluşların **%95'i sıfır getiri** alıyor (⚠ örneklem tutarsızlığı
  raporun kendi metninde kabul edilmiş).
* **Forrester:** BI'da elle kullanım **%20 tavanında**; doğal dilin katkısı **+10 puan**.

⊙ **Fark şurada:** rakipler *«her soruya bir şey söyler»* (Power BI kapsam dışında bile
konuşur), biz *«bilmediğimizde susarız»*. Onların hatası **görünmez** (sessiz yanlış),
bizimki **görünür** (boş ekran). **İkisi de kusur** — ama görünür kusur ürünü kötü
gösterir, görünmez kusur **kullanıcıya zarar verir**.

*dbt'nin cümlesi bizim tarafımızı tarif ediyor: «Text-to-SQL'de başarısızlık makul ama
yanlış bir cevaptır; semantik katmanda başarısızlık bir hata mesajıdır.»*

### 15.3 Mimari mükemmel mi

**Hayır — ama yanlış da değil.** Ölçüm şunu söylüyor:

🟢 **Doğru olan:** kamp seçimi (A kampı, ThoughtSpot/Looker ile aynı) · sayıyı her zaman
küpün koyması · beyan kültürü · kesitsel kök-neden cebiri (LMDI'nin doğru uygulanmış hâli)
· gömme modeli · grafik katmanı · kendi kendini denetleyen kapılar.

🔴 **Yanlış olan mimari değil, ağırlığın dağılımı:** trafiğin %37'sini taşıyan basamak
**45 satırlık bir istemle** yönetiliyor ve **hiç ölçülmüyor**; %35,5'ini taşıyan basamağa
**9.468 satır** yazılmış. Ve o 9.468 satırın varlık sebebi olan model
(*«kullanıcı dilbilimsel şemayı elle beslesin»*) **Microsoft ve Tableau tarafından
piyasadan kaldırıldı**.

### 15.4 Tek cümle

> **Ürün, ölçtüğü yerde iyi; ölçmediği yerde bilinmiyor. Ve ölçmediği yer, kullanıcının
> yaşadığı yerin üçte ikisi.**

---

---

## 37 · 🔴 KANIT GÜCÜ VE BU RAPORUN SINIRI — geliştirmeye başlamadan ÖNCE okunmalı

> Bu oturumun **WebSearch bütçesi tükendi (200/200)**. Ajanlar aramayı **WebFetch +
> DuckDuckGo Lite + Semantic Scholar API + HN Algolia API** ile ikame etti. Bu bölüm,
> hangi bulgunun bundan **etkilendiğini** ve hangisinin **etkilenmediğini** ayırır.
>
> ⚠ *Bir raporun en tehlikeli kısmı yanlış olan değil, ne kadar güvenilir olduğu
> bilinmeyen kısmıdır.*

### 37.1 Asimetri — ve kanıtı elimizde

**Arama bütçesi POZİTİF iddiaları etkilemez, NEGATİF iddiaları çürütür.**

* *«Omni 95/100 ölçtü»* → bir sayfayı **getirdim**, alıntı elimde. Arama gerekmez.
* *«Türkiye'de kimse yapmıyor»* → **aramanın kapsamı kadar** doğrudur. Ve bu iddia bu
  raporda **zaten bir kez çürüdü**: `dbtalk` · `Sofkar AI` · `Mubisoft ERP Asistanı` ·
  `Listen to Data` · `UMAI` — beşi de ilk taramada **kaçtı** (§19.7).

🔴 **Raporda 63 olumsuz iddia var.** Bunlar risk yüzeyidir.

### 37.2 Kanıt sınıfları

| sınıf | yöntem | arama bütçesinden etkilenir mi | rapordaki yeri |
|---|---|---|---|
| **A · Yerel ölçüm** | canlı sistem + `curl` + `docker exec` + kod okuma | 🟢 **HAYIR — hiç** | §1 · §2 · §3 · §4 · §11 · §16 · §17 · §18 · §0.6 karnesi |
| **B · Doğrudan getirme** | bilinen URL'den WebFetch, alıntıyla | 🟢 **HAYIR** | Wren mimarisi · Malloy · Voyager · satıcı dokümanları · Pulse'un 14 tipi |
| **C · API sayımı** | YC resmî API (**2.203 şirket**), GitHub/PyPI/npm/HF | 🟢 **HAYIR** — deterministik sorgu | §22.2 YC sayımı · yıldız/commit/lisans verileri |
| **D · Ağ adli incelemesi** | DNS/TLS/HTTP durum testi | 🟢 **HAYIR** | §22.1 mezarlık |
| **E · Akademik** | Semantic Scholar API + arXiv | 🟡 **az** — makale bulunur, *«başka makale var mı»* zayıflar | §7 · §9 · §10 · §32 |
| **F · KEŞİF** | *«bu alanda başka kim var»* | 🔴 **EVET, ağır** | §19 yerli rekabet · §13 açık kaynak taraması · tüm *«bulunamadı»* satırları |

### 37.3 🟢 Geliştirmeye ETKİSİ OLMAYAN kısımlar — güvenle ilerlenebilir

§14'ün altı öbeğinden **beşi** A/B/C sınıfına dayanıyor:

| öbek | dayanağı | güven |
|---|---|---|
| **§14.0** kapsamı ilan et | Hex/Dot/Omni'nin **yazılı** kapsam reddi (getirildi) + ölenlerde yokluğu (API sayımı) | 🟢 **yüksek** |
| **§14.1** önce ölç | **tamamen kendi ölçümümüz** (trafik %37/%35,5/%21,8 · şişme 28× · garson 21 senaryo) | 🟢 **en yüksek** |
| **§14.2** garsonu besle | Cube **+17…+23** (yayın) · Anthropic **%21→>%95** (yayın) · `extract_by` (motorun kendi API'si) | 🟢 **yüksek** |
| **§14.3** iki sistemi birleştir | **tamamen kendi ölçümümüz** (%73 örtüşme · iki bayrak kapalı · %60 tek adım) | 🟢 **en yüksek** |
| **§14.4** kök-neden | yayınlanmış algoritmalar (Adtributor/HotSpot/LMDI) + CHI 2018 | 🟢 **yüksek** |
| **§14.5** cevap biçimi | Pulse'un **14 tipi** (getirildi) + **kendi ölçümümüz** (chip 6,6,5,…) | 🟢 **yüksek** |
| **§14.7** temizlik | **tamamen kendi ölçümümüz** | 🟢 **en yüksek** |

⊙ **Yani teknik yol haritasının tamamı, arama bütçesinden bağımsız kanıtlara dayanıyor.**

### 37.4 🔴 AÇIKTA OLAN TEK KISIM — §14.6 stratejik/pazar

| madde | dayanağı | risk |
|---|---|---|
| **26** kama: *«Türkiye'de kimse imalat + Türkçe + doğrulanabilirlik satmıyor»* | 🔴 **F sınıfı (keşif)** | **Bir kez zaten çürüdü.** Beş oyuncu kaçtı; kaçmayanların sayısı **bilinmiyor** |
| **27** fiyat tabanı (AKINSOFT ücretsiz) | B sınıfı — ama **fiyat listeleri sık değişir** | orta |
| **28** kanal kararı (Solniro / DMO) | B/F karışık | orta |
| **29** self-serve fiyat | C sınıfı (yayınlanmış fiyatlar) | düşük |

### 37.5 🔴 GELİŞTİRMEDEN ÖNCE TAZE OTURUMDA DOĞRULANMASI GEREKENLER

**Tam arama bütçesiyle, sırayla:**

1. 🔴 **Yerli rekabet taramasını BAŞTAN yap.** §19'un tamamı F sınıfı. Tohum listesiyle
   değil, **Türkçe uzun kuyruk terimleriyle** ve **ERP ekosistemi dizinleriyle**
   (Logo/Mikro/Netsis iş ortağı listeleri, Teknokent şirket dizinleri, KOSGEB/TÜBİTAK
   destek listeleri, LinkedIn şirket araması, YouTube Türkçe demolar).
   ⊙ *«Kimse yapmıyor»* stratejinin temeli; **temeli bir kez çökmüş durumda.**
2. **Açık kaynak taramasını tazele** — §13. Yeni proje doğuş hızı yüksek; *«en iyi
   seçenek bu»* iddiaları **altı ayda bayatlıyor**.
3. **§21.8'in dört doğrulanamayanı** — özellikle **Tableau Ask Data** (iki ajan çelişti)
   ve *«aşırı grafikleştirme eleştirisi bulunamadı»* boşluğu.
4. **Fiyat ve paketleme** — hem yerli (AKINSOFT, ERP Asistanı, Turboard/DMO) hem küresel
   (Basedash, Definite, Upsolve). Fiyat en hızlı bayatlayan veridir.
5. **Rakiplerin son 3 ay duyuruları** — özellikle **Dativa AI** ve **OBASE AIReady**.

### 37.6 Hüküm

> **Bu raporla geliştirmeye başlanabilir — ama YALNIZ §14.0–14.5 ve §14.7 ile.**
> §14.6 (pazar/kama/fiyat/kanal) **taze bir arama oturumunda yeniden doğrulanmadan**
> stratejik karara temel yapılmamalıdır.

⊙ Ve iyi haber: **§14'ün ilk beş öbeği zaten aylarca iş.** Pazar doğrulaması onunla
**paralel** yürüyebilir; kritik yolda değil.

*Bir raporun dürüstlüğü, hangi bölümüne dayanılabileceğini söylediğinde başlar.*

---

# ON ÜÇÜNCÜ KISIM — YENİ GELİŞTİRİCİ İÇİN BAŞLANGIÇ

> 🔴 Bu bölüm, raporu **sohbet bağlamı olmadan** kullanılabilir kılar. Yeni bir
> geliştirici buradan başlar.

## 39 · SIFIRDAN BAŞLAMA

### 39.1 Okuma sırası — bir günlük

| # | belge | ne verir | süre |
|---|---|---|---|
| 1 | **bu rapor `§0` + `§0.6` karne** | 10 dakikada tam durum | 15 dk |
| 2 | `backend/CLAUDE.md` | 🔴 **kural seti** — garson devri, test kapısı politikası, koşum hijyeni | 45 dk |
| 3 | `backend/MIMARI.md` **§1-§4** | cevaplama merdiveni (8 basamak), semantik katman, LLM rolleri | 2 saat |
| 4 | `OPERASYON-DURUM.md` | nerede kaldık, açık borçlar, ölçüm tabanı | 30 dk |
| 5 | bu rapor **`§38` önce/sonra** + **`§14` plan** | ne yapılacak | 1 saat |
| 6 | `belgeler/denetim/2026-08-07_CEVIRI-SOZLESMESI.md` **son 3 tur** | nasıl çalışıyoruz (curl turu örneği) | 45 dk |

⚠ **Çelişkide `MIMARI.md` kazanır** (kendi beyanı). Bu rapor bir **analizdir**, mimari
otorite değildir.

### 39.2 Sistemi ayağa kaldırma

```bash
export DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0
docker-compose build dima-backend
docker rm -f dima-backend-core && docker-compose up -d dima-backend
curl -sf localhost:8001/health
```

API **8001**'de (konteyner içinde 8000). Demo: `demo-boyahane@usedima.com` / `dima-demo-1234`

⚠ `docker-compose.yml` **arşivlenmiş** `ghcr.io/canner/wren-engine:latest` imajını da
kaldırıyor ve ölçümde **`Restarting`** durumundaydı → **§14 FAZ 5 · F1**.

### 39.3 Curl ile doğrulama — `lab/curl/`

```bash
bash lab/curl/login.sh                              # token
bash lab/curl/kontrol.sh                            # 🔴 HER TURDAN ÖNCE
bash lab/curl/sor.sh "bu yıl makine bazında oee"    # taze soru
bash lab/curl/thread.sh "neden" /tmp/th.json        # thread'li takip
```

🔴 **`kontrol.sh` atlanmaz.** Ölçülmüş kör nokta: süresi dolmuş token `source=None` gibi
görünür ve **sahte bir ürün kusuru** olarak loglanır — bu oturumda bir kez oldu.

### 39.4 Kapı — ve ne zaman koşulmaz

```bash
docker run -d --name kapi --network none \
  -v "$PWD/backend:/app" -v "$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro" \
  --user "$(id -u):$(id -g)" -w /app -e DIMA_VQR_EMBEDDER=off \
  dima-test python lab/kapi.py --hepsi
docker wait kapi && docker logs kapi | tail -20 && docker rm -f kapi
```

🔴 **Kapı hijyeni (ölçülmüş, ihlali pahalı):** `--rm` **değil** `-d` + `--name` + `docker
wait` (`--rm` iki koşumun özetini sildi) · **`--user "$(id -u):$(id -g)"` ZORUNLU** (bir
unutma **229 dosyayı root'a** geçirdi ve üç şirket korpustan düştü) · 🔴 **kapı koşarken
repoya YAZILMAZ** (mount canlı, ölçüm karışır).

**Taban — bu değişmemeli:**
```
doğru=95 · devir=2142 · netleştirme=0 · beyanlı_kısmi=41 · sessiz_yanlış=8 · payda=2286
4993 passed, 58 skipped
```
⚠ `doğru=95` **uçtan uca doğruluk DEĞİL** — SQL üretebilmiş turlarda doğru küp oranı, ve
payda **590 semantik vakanın ~25× şişmiş** hâli (§1.2, §14 A3).

**Ne zaman koşulur:** yalnız **demet sonunda, bir kez**. Ölçülmüş israf: beş kök için beş
ayrı kapı **35 dk**, tek koşumla **7 dk**.

### 39.5 Rapordaki ölçümleri tekrarlama

| ölçüm | komut |
|---|---|
| **trafik dağılımı** (route %35,5 · garson %37 · cevapsız %21,8) | `docker exec dima-backend-core python3 -c "import sqlite3;c=sqlite3.connect('/app/logs/dima.db');[print(r) for r in c.execute('select source,count(*) from interaction_log group by 1 order by 2 desc')]"` |
| **korpus şişmesi** (590 semantik vaka) | `grep -E "SEMANTİK VAKA\|cevapsız kesme" backend/lab/reports/nl_corpus.md` |
| **wren_core yüzeyi** (15 sembol, 1'i kullanılıyor) | `docker exec dima-backend-core python3 -c "import wren_core;print([n for n in dir(wren_core) if not n.startswith('_')])"` · `grep -rhoE "from wren_core import [A-Za-z_, ]+" backend/app/` |
| **iki paralel sistem** (15 fiil ↔ 25 araç) | `docker exec dima-backend-core python3 -c "from app.plan_semasi import FIIL_ANLAMI; from app import tools; print(len(FIIL_ANLAMI), len(tools.llm_araclari(None)))"` |
| **plan uzunluğu** (%60 tek adım) | `docker logs dima-backend-core 2>&1 \| grep -oE "plan: [0-9]+ adım" \| sort \| uniq -c` |
| **cevap biçimi** (chip 6,6,5,6,6,4,6,3) | `lab/curl/sor.sh` ile §18'in 8 sorusu |
| **`few_shot_block` nereye bağlı** | `grep -rn "few_shot_block" backend/app/ \| grep -v "def "` |

### 39.6 🔴 DOKUNULMAYACAKLAR

§38.4'ün tamamı — ve **neden**leri orada yazılı:

**LLM SQL yazmaz** · **sayıyı her zaman küp koyar** · **grafik kararı deterministik
(ADR-0024)** · **kapalı fiil/araç kümesi** · **`narration_guard`** · **beyan kültürü** ·
**Türkçe morfoloji yatırımı**

⚠ Ve iki yapısal kural: **`KURAL B`** (bayrak kapalıyken davranış **bayt bayt** aynı) ·
**`KAT-1`** (bir kuralın **iki sahibi olamaz** — bu depoda defalarca ölçülmüş kusur sınıfı).

### 39.7 İlk hafta — somut

```
Gün 1     §39.1 okuma + sistemi ayağa kaldır + lab/curl ile 10 soru sor
Gün 2-3   FAZ 0 · A1 garson korpusu (interaction_log'daki 3.554 gerçek etkileşimden örnekle)
Gün 4     FAZ 0 · A2 cevapsız metriği + A3 şişme beyanı
Gün 5     FAZ 1 · B2 (few_shot_block'u garsona bağla — ~3-10 satır) → curl ile ölç
```

🔴 **B2 ilk kod işidir** çünkü en ucuz ve en yüksek getirili: fonksiyon **zaten yazılmış**,
yalnız yanlış dala bağlı (§12.12).

⚠ **Ama A1 olmadan B2'nin işe yarayıp yaramadığı bilinemez.** FAZ 0 pazarlık dışıdır.

## EK · Kaynakça

**Benchmark:** [Spider 2.0](https://spider2-sql.github.io/) · [arXiv 2411.07763](https://arxiv.org/abs/2411.07763) · [BIRD](https://bird-bench.github.io/) · [BEAVER arXiv 2409.02038](https://arxiv.org/abs/2409.02038) · [BIRD-INTERACT arXiv 2510.05318](https://arxiv.org/abs/2510.05318) · [Archer arXiv 2402.12554](https://ar5iv.labs.arxiv.org/html/2402.12554) · [AIMultiple bağımsız ölçüm](https://aimultiple.com/text-to-sql) · [Stonebraker, CACM](https://cacm.acm.org/blogcacm/if-you-think-you-can-do-real-world-text-to-sql/)

**Hata/güvenilirlik:** [arXiv 2501.09310](https://arxiv.org/html/2501.09310v1) · [LinkedIn arXiv 2507.14372](https://arxiv.org/html/2507.14372v1) · [selective prediction arXiv 2607.06799](https://arxiv.org/html/2607.06799v1) · [CHASE-SQL arXiv 2410.01943](https://ar5iv.labs.arxiv.org/html/2410.01943) · [AbstentionBench arXiv 2506.09038](https://arxiv.org/html/2506.09038v1)

**Semantik katman:** [Cube paired benchmark arXiv 2604.25149](https://arxiv.org/abs/2604.25149) · [dbt 2026](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026) · [Sequeda arXiv 2311.07509](https://arxiv.org/abs/2311.07509) · [AtScale](https://www.atscale.com/press/natural-language-processing-breakthrough/) · [lkr.dev Looker benchmark](https://www.lkr.dev/articles/benchmarking-semantic-layer-conversational-analytics/) · [Apache Ossie](https://github.com/apache/ossie)

**Belirsizlik:** [Microsoft/CIDR 2024](https://www.cidrdb.org/cidr2024/papers/p74-floratou.pdf) · [AMBROSIA](https://ambrosia-benchmark.github.io/) · [AmbiQT arXiv 2310.13659](https://arxiv.org/abs/2310.13659) · [AmbiSQL arXiv 2508.15276](https://arxiv.org/html/2508.15276v1) · [NLIDB kullanıcı çalışması arXiv 2511.14718](https://arxiv.org/html/2511.14718v2)

**Türkçe:** [BIRDTurk SIGTURK 2026](https://aclanthology.org/2026.sigturk-1.13/) · [arXiv 2602.03633](https://arxiv.org/abs/2602.03633) · [depo](https://github.com/metunlp/birdturk) · [TURSpider](https://github.com/alibugra/TURSpider) · [TUR2SQL](https://github.com/alibugra/TUR2SQL) · [MultiSpider arXiv 2212.13492](https://ar5iv.labs.arxiv.org/html/2212.13492) · [MultiSpider 2.0 arXiv 2509.24405](https://arxiv.org/html/2509.24405) · [TR-MTEB](https://aclanthology.org/2025.findings-emnlp.471/)

**Grafik:** [Draco (OSF)](https://osf.io/3eg9c/download) · [uwdata/draco](https://github.com/uwdata/draco) · [Show Me, TVCG 2007](https://doi.org/10.1109/TVCG.2007.70594) · [Mackinlay APT 1986](https://doi.org/10.1145/22949.22950) · [Observable Plot](https://github.com/observablehq/plot) · [CompassQL](https://github.com/vega/compassql) · [AntV AVA](https://github.com/antvis/AVA) · [Pandey ve ark., CHI 2015](https://doi.org/10.1145/2702123.2702608)

**Kök-neden:** [Adtributor, NSDI'14](https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-bhagwan.pdf) · [HotSpot, IEEE Access 2018](https://netman.aiops.org/wp-content/uploads/2018/12/sunyq_IEEEAccess2018_HotSpot.pdf) · [Squeeze, ISSRE'19](https://netman.aiops.org/wp-content/uploads/2019/10/Squeeze-ISSRE2019_v2.pdf) · [PSqueeze, JSS 2023](https://netman.aiops.org/wp-content/uploads/2023/05/psqueeze-jss.pdf) · [riskloc](https://github.com/shaido987/riskloc) · [DIFF, VLDB 2019](https://www.vldb.org/pvldb/vol12/p419-abuzaid.pdf) · [Ang, LMDI, Energy Policy 2005](https://doi.org/10.1016/j.enpol.2003.10.010) · [Zgraggen ve ark., CHI 2018](https://www.emanuelzgraggen.com/assets/pdf/mcp.pdf)

**Değerlendirme:** [test-suite-sql-eval](https://github.com/taoyds/test-suite-sql-eval) · [Dr.Spider](https://github.com/awslabs/diagnostic-robustness-text-to-sql) · [AmbiQT](https://github.com/testzer0/AmbiQT) · [EHRSQL](https://github.com/glee4810/EHRSQL) · [promptfoo](https://github.com/promptfoo/promptfoo) · [syrupy](https://github.com/syrupy-project/syrupy)

**Rakip dokümantasyon:** [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) · [Snowflake doğruluk](https://www.snowflake.com/en/blog/engineering/cortex-analyst-text-to-sql-accuracy-bi/) · [Genie](https://docs.databricks.com/aws/en/genie/) · [ThoughtSpot Spotter](https://www.thoughtspot.com/blog/introducing-spotter-ai-analyst) · [Spotter kısıtları](https://docs.thoughtspot.com/cloud/26.7.0.cl/spotter-limitations) · [Power BI Copilot](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-ask-data-question) · [Q&A emekliliği](https://learn.microsoft.com/en-us/power-bi/natural-language/q-and-a-limitations) · [Key influencers](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-influencers) · [Tableau Pulse](https://help.tableau.com/current/online/en-us/pulse_insights_platform_insight_types.htm) · [Looker CA](https://docs.cloud.google.com/looker/docs/conversational-analytics-overview) · [Gemini dil kısıtı](https://docs.cloud.google.com/looker/docs/troubleshooting-gemini) · [Quick Sight Topics](https://docs.aws.amazon.com/quick/latest/userguide/topics-in-chat.html) · [Qlik reasoning trace](https://community.qlik.com/t5/Official-Support-Articles/Show-Your-Work-The-Architecture-of-Qlik-Answers-Reasoning-Trace/ta-p/2553267) · [Sisense AI Assistant](https://docs.sisense.com/main/SisenseLinux/ai-assistant.htm) · [Zenlytic Clarity Engine](https://docs.zenlytic.com/using-zenlytic/clarity_engine) · [WrenAI](https://github.com/Canner/WrenAI)

---

**Yöntem notu:** Yerel ölçümler bu depoda canlı sistem üzerinde curl/`docker exec`/kod
okuması ile yapıldı. Dış araştırma dört paralel alt-ajanla yürütüldü; oturumun WebSearch
bütçesi (200/200) tükendiği için tüm erişim WebFetch + GitHub/PyPI/npm/HuggingFace API'leri
üzerinden yapıldı ve lisanslar **LICENSE ham metninden** doğrulandı. Erişilemeyen kaynaklar
(Show Me 2007 PDF, APT 1986 tam metni, iDice, Ang 2005) ilgili yerlerde **açıkça
işaretlendi** ve içerikleri yalnız ikincil/doğrulanabilir kaynaklardan aktarıldı.

---

## 40 · 🔴 ARAŞTIRMA KALEMLERİNİN TOPLU KARARI — ölç → karar → **YAZ** (2026-08-12)

Yol haritasının sonuna eklenen kalemlerin çoğu *«oku / değerlendir»* biçiminde yazılmıştı.
Bir *«değerlendir»* maddesi, değerlendirilip **kararı yazılmadıkça** kapanmaz — ve açık
duran her satır, bir sonraki turun önceliğini bozar.

⚠ **Gerekçeli `⊘` bir başarısızlık değildir.** `§E3` Benjamini-Hochberg'i tam olarak
böyle kapattı: ölçüldü, bu depoda p-değeri olmadığı görüldü, **reddedildi ve yazıldı**.
*Bir aracı almamak, ancak neden almadığın yazılıysa bir karardır.*

### 40.1 Ölçüm — bağımlılıklar ve kod izleri

    syrupy · ruptures · statsforecast · snowballstemmer · zemberek · promptfoo → HİÇBİRİ KURULU DEĞİL
    M-Schema · resolve_used_table_names · LMDI · TURSpider · perturbation     → kodda İZ YOK
                                                    (⟳ 08-12: **beşi de yeniden ölçüldü**,
                                                     `ast` ile 12.026 kod adı tarandı → 0)
    değer profilleme (`FuzzyIndex` · `dimension_values` · `deger_capasi`)      → ✅ VAR
    `SessionContext` · `RowLevelAccessControl`                                → ✅ ÖLÇÜLMÜŞ (`§F5`)
    view fan-out kapısı (`test_view_fanout_guard.py`)                         → ✅ VAR

> 🔴🔴 **BU ENVANTER BİR *SEMBOL* ENVANTERİDİR, BİR *YETENEK* ENVANTERİ DEĞİL — ve ayrımı
> yazmamak bu turda bir yanlış çelişki üretti.** Bir denetim ajanı *«`perturbation` ✅ artık
> var»* bildirdi (`tests/test_a10_saglamlik_farki.py`, 6 kapı), ben yamaladım — sonra
> **kendi ölçümüm yamayı çürüttü**: `app/`+`lab/`+`tests/` altındaki **12.026** kod adı
> `ast` ile tarandığında `perturbation` **0** kez geçiyor. İkisi de doğruydu:
>
> | okuma | ölçüm |
> |---|---|
> | *sembol* `perturbation` kodda var mı | 🔴 **HAYIR** — 0 kod adı |
> | *yetenek* (sağlamlık pertürbasyonu) kurulu mu | ✅ **EVET** — `§40.6 A10`, ama **Türkçe adla** (`BOZULMALAR`, `test_a10_saglamlik_farki`) |
>
> ⊙ Yani bu envanter, **yerel adla kurulmuş bir yeteneği göremez** — yabancı sembol adını
> arar. Bu bir kusur değil bir **kapsamdır**, ama yazılmadığı için iki tur boyunca bir
> *«bölüm içi çelişki»* gibi okundu.
>
> *Yabancı adların envanteri, kendi dilinde yazılmış bir yeteneği yokluk sanır.*

### 40.2 🔴 ÜÇ KALEM ZATEN KAPANMIŞ — kartları bayattı

| kalem | ölçüm |
|---|---|
| **F16** *«views yolu için bir kapı»* | ✅ `tests/test_view_fanout_guard.py` **var ve koşuyor** — `parti_zengin` view'ının `personel.ad_soyad` üzerinden LEFT JOIN'i bir fan-out riskiydi, `4.7b` en az invaziv düzeltmeyle regresyon kapısına çevrildi |
| **F10** `SessionContext.dry_run`/`register_csv` | ⊘ `§F5`'te **ölçülüp reddedildi**: `dataset.py`'nin 161 satırı dökümlendi, `register_csv` o işin **hiçbirini** yapmıyor (`ingest_file` 42 satır yalnız *yaklaşıyor*) |
| **F11** `RowLevelAccessControl` | ⊘ `§F5`: *«sembol düzeyinde doğru, yetenek düzeyinde farklı»* — ve `§F12`'nin üçüncü ölçümü RLS enjeksiyonunun manifesti **v2-uyumsuz** yaptığını gösterdi |

⊙ Üçü de `㊷`'nin örneği: *bir kartın «yapılacak»ı zaten yapılmış olabilir — önce `§`'ünü ara.*

### 40.3 ✅ AMACI KARŞILANANLAR — mekanizma farklı, sonuç aynı

| kalem | karar |
|---|---|
| **B11** ephemeral/karalama sorgusu | ✅ `§36.1-4`: Hex soru-başına gizli sorgu koşar; biz **kurulum anında bir kez** profilleriz — **121 boyutun 120'si (%99)** değer taşıyor. Amaç (*«ilk denemede doğruluk»*) karşılanıyor, mekanizma **daha ucuz** |
| **B13** değer profilleme | ✅ Aynı ölçüm: `_enrich_categorical` + `_enrich_cube_dim_values` + `value_index.FuzzyIndex` + `deger_capasi.py`. *«Kullanıcının kelimesi ↔ DB değeri»* uçurumu **kapalı** |
| **A9** `promptfoo` | ⊘ `eval/run.py` **zaten** selective-prediction yapıyor; ikinci bir harness aynı işi ikinci bir bağımlılıkla satın almaktır |
| **A7** EHRSQL reliability skoru | ◐ İlkesi **zaten uygulanıyor**: kapsam-dışına red **pozitif** (`§⑧` · dürüst red), kapsam-içine red **negatif** (`cevapsız` metriği, `DOGRULUK.md`'de **%19,7**). Tek eksik: ikisini **tek bir skorda** birleştirmek — bir sunum işi, bir yetenek değil |

### 40.4 ⊘ REDDEDİLENLER — ve gerekçeleri

| kalem | red gerekçesi |
|---|---|
| **A5** `syrupy` snapshot | 🔴 **Bu deponun kapı felsefesine aykırı.** Snapshot cevabın **tam metnini** kilitler; buradaki 30+ kapı bilinçle **yapıya/iddiaya** bağlandı (ders ㉕). Bir snapshot her anlatı iyileştirmesinde kırmızı verir ve düzeltmesi *«kabul et»*tir — yani kapı bir **kayda** dönüşür. *Bir kapının onaylanarak geçilen hâli, kapı değildir.* |
| **B5** Snowball TR kök bulucu | ⊘ Kendi belgesi *«stems only, **not lemmas**»* diyor; Türkçe'de ekler anlamı **taşır** (`§G/AJ0`: *«arttı»* bir FİİL). Kök bulucu o ayrımı **siler** |
| **B6** Zemberek sözlüğü | ⊘ README *«slow maintenance»*; ve `_catalog_vocabulary` bugün **kataloğun kendi kelimelerinden** besleniyor — dış sözlük, katalogda olmayan bir kelimeyi *tanıyormuş* gibi gösterir |
| **F9** kama/fiyat/kanal kararı | ⊘ `§37.4`'ün kendi şartı: *«taze arama oturumu olmadan stratejik karara temel yapılmamalı»*. Şart karşılanmadı → karar **verilmiyor**, ve verilmediği yazılıyor |
| **F15** `Model`/`SessionProperty`/`RemoteFunction` | ⊘ Bugün karşılığı yok; `RemoteFunction` Türkçe tarih/metin için bir kapı **olabilir** ama o kapı `§B12`'nin motor sözleşmesi işiyle birlikte açılır |
| **F17** `wren-langchain`/`wren-pydantic` SDK | ⊘ Bu depo motoru **doğrudan** çağırıyor ve `§F5` o yolun ince olduğunu ölçtü; bir SDK katmanı yeni yetenek getirmiyor, yeni bir sürüm bağımlılığı getiriyor |
| **E6** Explanation Tables | ⊘ Kartın kendisi *«oku, uygulama»* diyor. Okundu: Adtributor'ın kardeşi, **bileşik segment** boşluğuna aday — ve o boşluk `§25` ile **layer-1'de kilitli** (PARK). Ön koşulu açılmadan bu da açılmaz |

### 40.5 ⏸ PARK — değerli ama şartı yazılı

| kalem | şart |
|---|---|
| **A6** `test-suite-sql-eval` deseni | **İkinci bir DB** ister (aynı sonucu veren farklı SQL'leri ayırt etmek için). Bugünkü korpus `sessiz_yanlis`'ı **zaten** ölçüyor (7/2.286) → şart: korpus bu sınıfı kaçırdığı **ölçülene** kadar bekler |
| **A11** TURSpider / TUR2SQL / BIRDTurk | Dış çapa **değerli** (kendi korpusumuzun dışında); şart: lisans + şema eşleme işi, ve `§26` garson ölçümü ondan **önce** gelir |
| **A15** Wren `evals/` dizinini incele | `A1` korpus tasarımına desen; şart: `A1` kaseti 21→50'ye büyütülürken okunur |
| **B7** M-Schema (XiYan-SQL) | `B1` şema daraltmanın **çıktı biçimi**; `B1` ✅ yapıldı ama biçim değişimi `KURAL B` ister → şart: garson doğruluk ölçümü (`§26`) |
| **B8** `resolve_used_table_names` | `B1`'in **doğrulaması** (budanmış manifest gerçekten yetiyor mu). Şart: `B1`'in bir kırmızısı ölçülene kadar bekler |
| **E5** `ruptures` + `statsforecast` | `E1` Adtributor'ın **ön koşulu** (baseline/forecast). `§25` layer-1 kilidi açılmadan gereksiz |

### 40.6 🔴 GERÇEK VE UCUZ — bu turda yapılanlar

| kalem | ne yapıldı |
|---|---|
| **A8** Inspect AI `stderr` | ✅ **YAPILDI** — `DOGRULUK.md`'nin yayınladığı oranlara **Wilson güven aralığı** eklendi. *«%85 ile %90 arasındaki fark gürültü mü»* sorusunun tek cevabı bir aralıktır |
| **A10** `Dr.Spider` robustness gap | ✅ **YAPILDI** — ve gerekçesi bu turda **ölçüldü**: `göre`/`bazında` bu depoda **dört** anlama geliyor ve dördüncüsü (*«dolar bazında»* = para birimi) canlı turda yakalandı. Pertürbasyon kapısı tam bu sınıfı ölçer |

*Bir yol haritasının sonundaki maddeler, kararları yazılmadıkça bir kuyruk değil bir
gürültüdür.*

### 40.7 🔴 B12 ve F14 — MOTOR SÖZLEŞMESİ ÖLÇÜLDÜ, ve biri kendi gerekçemizi çürüttü

#### B12 · `hour`/`minute` — engel motorda DEĞİL, **VERİDE**

Kapının yazılı gerekçesi *«motorun `timeDimensions.granularity` sözleşmesi bu beşini
tanıyor»* idi. **Ölçüldü ve çürüdü:** motor `hour`/`minute` için sorunsuz SQL üretiyor
ve sorgu **koşuyor**.

    granularity=day   → 782 satır · ilk kova 2024-01-01 00:00
    granularity=hour  → 782 satır · ilk kova 2024-01-01 00:00     ← BİREBİR AYNI

`tarih` bir **DATE** kolonu; gün altı çözünürlük **yok**. `hour` açılsaydı kullanıcı
*«saatlik»* isteyip **günlük** sayı alırdı — etiketi *«saatlik»* yazarak. Bu bir eksiklik
değil bir **sessiz-yanlıştır**.

> *Bir granülerliği motorun kabul etmesi, verinin onu taşıdığı anlamına gelmez; kabul
> eden bir motor, olmayan bir çözünürlüğü ADLANDIRIR.*

⊘ **KARAR: AÇILMIYOR** — ve açılış şartı artık **gözlenebilir**: bir küpün zaman ekseni
**TIMESTAMP** olmalı ve `day` ile `hour` kovaları **farklı satır sayısı** vermeli. Kapının
gerekçesi düzeltildi (`test_b12_granulerlik_tek_sahip.py`).

⚠ Bu, `㉔`'ün kendi belgemize uygulanmasıdır: yazılı gerekçe **ölçülmeden** kabul edilmişti.

#### F14 · `SessionContext`'in dört yeteneği — **biri** kullanılıyor, **ikisi hiç ölçülmedi**

Kart dört yetenek sayıyor. Ölçüldü: bu depo motoru `WrenEngine` üzerinden çağırıyor ve o
yüzeyin **tamamı** dört metottur:

    WrenEngine → close · dry_plan · dry_run · query

| kart | ölçüm |
|---|---|
| `dry_run` | 🔴 **yüzeyde var ama ÜRÜN KODUNDA HİÇ ÇAĞRILMIYOR** — `grep -rn dry_run backend/app/` → **0** *(ölçüm 2026-08-12)*. İlk yazımdaki *«kullanılıyor»* ölçülmemiş bir varsayımdı; ve aynı belgenin `§14.16 A` tablosu bunu **zaten doğru** yazmış: *«`wren_service.dry_plan` sarıyor»* |
| `dry_plan` | ✅ **kullanılıyor** — güvenlik zincirinin ikinci kapısı |
| `get_available_functions` | ⊘ `WrenEngine` yüzeyinde **yok**; `get_session_context(manifest_str, function_path, properties, data_source)` fabrikasının arkasında |
| `transform_sql` | ⊘ aynı |
| `pushdown_limit` · `list_tables` | 🔴 **HİÇ ÖLÇÜLMEDİ.** `§14.16 D`'nin F14 kartı dört yeteneği **bu ikisiyle** sayıyordu; bu tablo onların yerine `dry_run`/`dry_plan`'ı koydu — yani karar, kartın saydığı dördün **ikisini görmeden** verildi. Kurulu `wren` paketinde de grep = **0** |

⊘ **KARAR: AÇILMIYOR.** Kartın vaadi (*«motorun desteklediği fonksiyonları **sormak**,
varsaymak yerine»*) doğru bir ilkedir ama bugün bir kusur ölçülmedi: derleyici zaten
motorun kendi manifestinden üretiyor ve `dry_plan` her sorguyu **koşmadan önce** motora
doğrulatıyor. *Bir soruyu sormak, cevabı zaten bilen bir kapı varken yeni bir bağımlılıktır.*
⏸ Şart: `dry_plan`'ın kaçırdığı bir fonksiyon uyumsuzluğu **canlıda ölçülene** kadar.

### 40.8 🔴 SON ÜÇ KALEM — A12 · E7 · B9

#### A12 · Tur bazında ölçüm — YAPILDI, ve SParC'ın çöküşü BİZDE YOK

Kartın şikâyeti haklıydı: korpus çok turlu zincirleri **koşuyordu** ama raporu **tur
numarasını hiç yazmıyordu**. ✅ `lab/garson_korpusu.py` artık her kaydı `tur` ile
etiketliyor ve rapora **tur bazında cevaplanabilirlik** tablosu koyuyor. *Bir ölçümün
eksikliği, verinin yokluğu değil, onu yazmayan bir satırdır.*

🟢 **Canlı ölçüm (3 zincir · 11 tur, curl):**

    Tur 1: 3/3 = %100      Tur 4: 1/1 = %100
    Tur 2: 3/3 = %100      Tur 5: 1/1 = %100
    Tur 3: 3/3 = %100

⊙ SParC'ın *«Turn 1 %38,6 → Turn ≥4 %1,1»* çöküşü **yeniden üretilmedi** — ve sebebi
yapısal: SParC **açık şemada birebir SQL eşleşmesi** ölçer; biz **kapalı bir semantik
katmanda** ölçüyoruz ve odak taşıma deterministik (`§B9 ODAK VARLIK`).

⚠ **İki dürüstlük sınırı yazılı:** ① bu tablo **cevaplanabilirlik** ölçer (bir küpe
bağlanabilme), **doğruluk değil** ② payda küçük (11 tur). *Aynı adı taşıyan iki ölçüt,
aynı şeyi ölçmez.*

#### E7 · LMDI — ⊘ **ÖNCÜL YANLIŞ ÇIKTI**

Kart *«ayrıştırmamız LMDI-II ailesinde… alt-grup toplanabilirliği YOK… `ln(0)` tanımsız»*
diyordu. Ölçüldü: `contribution.contributions()` **saf toplamsal fark ayrıştırması**
yapıyor (`delta = simdi − onceki`), gövdede **logaritma yok**.

| kartın kaygısı | ölçüm |
|---|---|
| `ln(0)` tanımsız | ⊘ konu dışı — logaritma kullanılmıyor |
| negatifte LMDI tanımsız | ⊘ konu dışı — çıkarma her işarette tanımlı |
| alt-grup toplanabilirliği **YOK** | 🔴 **TERSİ** — toplamsal ayrıştırma **tam** toplanabilir |

⊙ LMDI-I ↔ LMDI-II ayrımı **çarpımsal/indeks** ayrıştırma içindir (etkinlik × yapı ×
yoğunluk); biz bir değişimi **tek boyutun segmentlerine** bölüyoruz.

> *Bir yöntemi ait olmadığı ailenin kusurlarıyla eleştirmek, çözdüğü sorunu göremeden onu
> değiştirmeye çalışmaktır.*

⊘ **KARAR: LMDI'ye GEÇİLMİYOR** — geçmek, tam toplanabilir bir yöntemi sıfır/negatifte
**tanımsız** bir yöntemle değiştirmek olurdu. Kapı `tests/test_e7_toplamsal_ayristirma.py`
(6): parçaların toplamı = bütün · sıfır bileşen · negatif bileşen · sıra bağımsızlık ·
gövdede logaritma **yok** · kırpma **sessiz değil**.

#### B9 · İki-sağlayıcılı LLM hakem — ⏸ **PARK, şartı yazılı**

Kartın ölçümü sağlam: `dry_plan` AUROC **0,500 (tam şans)**, execution self-consistency
**0,613**. Yani bugünkü öz-değerlendirme sinyalleri **zayıf** ve bir hakem gerçekten
değerli olurdu.

⏸ Ama iki sağlayıcı = **her soruda iki kat kota** ve kazancı ölçecek bir taban **yok**:
garsonun doğruluk ölçümü `§26` ile park edilmiş. *Kazancı ölçülemeyen bir maliyeti
varsayılan açmak, ölçümü bir törene çevirir* — `motor_rls`/`ossie_ithal`/`skills` için
verilen kararın aynısı. **Şart: `§26`.**

### 40.9 ✅ SON BEŞ ◐ — hepsi karara bağlandı

| kalem | karar | gerekçe |
|---|---|---|
| **A7** güvenilirlik skoru | ✅ **YAYINLANDI** | `DOGRULUK.md`'ye reddin **iki türü** ayrı ayrı kondu: kapsam-**dışı** red **85** (✅ pozitif) · kapsam-dışı **cevap 1** (🔴 en ağır negatif) · kapsam-**içi** red **339** (%2,3) · cevaplandı **11.732** (%78,4). Gürültü paydası 86 → **doğru red %98,8**. ⚠ **Tek bir birleşik sayı YAZILMADI** ve sebebi yazılı: EHRSQL'in skoru bir **ceza katsayısı** seçmeyi gerektirir ve o katsayı bir **iş kararıdır**. *Bir güvenilirlik skoru, cezasının kim tarafından seçildiği yazılmadan bir ölçüm değil bir tercihtir.* ⊙ Ve **netleştirme bir red değildir** (2.755 · %18,4): kullanıcıya soru sorulmuş, cevap kapanmamıştır |
| **D3** iş sözlüğü | ⏸ **PARK, şartı `§26`** | `§B3` ile aynı iş (ikinci satır). Mekanizma **var ve bağlı** (`business_rules` → Discovery'nin SQL istemi) ama garsonun istemine değil; ve mevcut içerik (SQL semantiği · Logo `TRCODE`) **garsona uymuyor**. Garson istemine bağlamanın kazancı ancak garson doğruluk ölçümüyle görülür |
| **D11** olgu üretimi | ⏸ **PARK, şartı `A1` kaseti 21→50** | Birim düzeltildi (**11 çağrı yeri ≠ 14 tip**; canlıda 2-3 ateşliyor). Kalan soru *«hangi tip hiç ateşlenmiyor»* ve cevabı kaset büyüdüğünde **bedava** gelir — ayrı bir sayaç **iki sahipli** bir ölçüm olurdu (`KAT-1`) |
| **D12** kök-neden yatay eksen | ⏸ **PARK, şartı `§25` layer-1** | Üç vaadin ikisi kapandı: **JS sürprizi ✅** · **BH ⊘ ölçülü red** (p-değeri yok). Kalan **Adtributor**, `§25` bileşik segment kilidine bağlı; kilit açılmadan Adtributor'ın gireceği bir yer yok |
| **F12** motor RLS | ⊘ **ÖLÇÜLDÜ, AÇILAMIYOR** | Üçüncü ölçüm kesin: izole+taze `gulteks` ile `is_backward_compatible` → ham **True** · shadow **True** · 🔴 **`on` (3 kural) → False**. Yani RLS enjeksiyonu manifesti **v2-uyumsuz** yapıyor. ⊙ Ve kartın *«bir gün kapı bayrağı açmadan önce konuşur»* cümlesi **gerçekleşti** — kapı önce **kör**dü (kural olmayan tek tenant'a bakıyordu), ölçüm onu da düzeltti. *Bir ön koşul kapısı, koşulun sağlanmadığı bir örnekle sınanmadıkça boş bir doğrudur.* |