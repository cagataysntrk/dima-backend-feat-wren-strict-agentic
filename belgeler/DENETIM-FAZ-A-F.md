# 🔴 FAZ DENETİMİ A→F — ajan bulgularının TEK KAYDI

> **Bu dosya bir yapılacaklar listesi değil, bir ÖLÇÜM KAYDIDIR.** Kullanıcı kararı
> (2026-08-12): *«her faz için ayrı bir ajan kontrol edecek — A için bir, B için bir,
> F'ye kadar. Sadece raporda **yapıldı işareti olması önemli değil**, cidden kontrol
> edilmeli… ajanlar bunları **daha da mükemmelleştirmek** için neler yapılmalıyı da
> düşünmeli, araştırmalı.»* Ve: *«dikkatlice yaz ki **unutulmasın atlanmasın**.»*

⚠ **Ajan iddiası ölçülmeden kapatılmaz.** Bu oturumda iki ajan iddiası kısmen yanlış
çıktı (*«iki kapı bir kural»* → 12 yüklemin 1'iydi · *«perturbation artık var»* → kod adı
olarak 0). Her satır **kendi ölçümümle** doğrulanıp öyle işlenir.

## Durum sütunu

| işaret | anlamı |
|---|---|
| 🔵 **BEKLİYOR** | ajan bildirdi, **kendi ölçümüm yapılmadı** |
| 🟣 **DOĞRULANDI** | kendi ölçümümle doğrulandı, düzeltme bekliyor |
| ✅ **KAPANDI** | düzeltildi + kapısı mutasyonla sınandı + işlendi |
| ⊘ **REDDEDİLDİ** | ölçüldü, iddia yanlış çıktı — gerekçesi yazıldı |

## Ajan raporları (ayrıntı için)

| faz | kapsam | görev kimliği |
|---|---|---|
| **A** | A1–A15 · ölçüm/değerlendirme altyapısı | `a167921e44173557c` |
| **B** | B1–B13 · garsona giren bilgi + route yığını | `a4d530a32799deb69` |
| **C** | C1–C3 · ajan/orkestrasyon + MCP yüzeyi | `a193929d2db5f1f8c` |
| **D** | üç ayrı `D` kimlik kümesi | `a947d55b52b4a42de` *(hâlâ koşuyor)* |
| **E** | E1–E7 · istatistik / kök-neden | `a4f92f15410cd1d7b` |
| **F** | F1–F16 · motor / platform / yayın | `a7c13f57f5a6544a4` |

---

# ⚠ ÖNCE: EN AĞIR SEKİZ BULGU (fazlardan bağımsız sıra)

Bunlar **ürün kusuru** ya da **sahte güvence**; ötekiler bayat sayı/işaret.

| # | bulgu | sınıf | durum |
|---|---|---|---|
| **①** | 🔴🔴 **MCP sözleşmesi yanlış yayımlanıyor** — `mcp.araclar()` **31 aracın 77 alanının tamamını `"string"`** ilan ediyor; **23'ü dict/list** bekliyor, **5'inde zorunlu parametre eksik**, **3'ünün kaynağı sağlanmıyor** → **sözleşmeye uyarak çağrılabilen araç 0/31**. `route` bile çağrılamıyor | 🔴 **ÜRÜN — yayımlanmış yanlış sözleşme** | 🟣 **DOĞRULANDI** *(31 araç · 77 alan · hepsi `string`)* |
| **②** | `mcp._arindir` — köken zarfının sınırı **yeniden kurulabiliyor** (prompt-injection sınırı kırık) | 🔴 **GÜVENLİK** | 🟣 **DOĞRULANDI** *(`_zarfla`'da `ZARF_SON` 2 kez)* |
| **③** | `kok_neden.toplam_turu` — *«toplamın %P'ini taşıyor»* derken payda **mutlak değerler toplamı**; karışık işaretli ölçüde **12 kat yanlış + işaret ters** | 🔴 **SESSİZ-YANLIŞ (yayında)** | 🔵 bekliyor |
| **④** | `test_a10_saglamlik_farki` — `a.get("cube")` daima `None`; kapı **iki farklı küpü bile** eşit sayıyordu | 🔴 **SAHTE YEŞİL** | ✅ **KAPANDI** *(bugün · 10 geçti · 0 atlandı)* |
| **⑤** | `test_view_fanout_guard` — **9 view'ın 1'ini** görüyor; `karlilik_src`'nin 2 `LEFT JOIN`'i korunmasız | 🔴 **KÖR KAPI** | 🔵 bekliyor |
| **⑥** | `kirpilan_esik_yuzde` ön-uçta `*100` → ekranda *«eşiğin altında (|pay| < **%100.0**)»* | 🔴 **BİRİM HATASI (kullanıcıya görünür)** | 🔵 bekliyor |
| **⑦** | `test_kimlik_uzayi_tek_anlamli` — deseni `**`'ta duruyor, **`D6` ve `D10` çakışmalarını kaçırıyor**; taban kapısı 62 sayıp yeşil kalıyor | 🔴 **KÖR KAPI (bugün yazdığım)** | 🟣 **DOĞRULANDI** *(dar desen YOK ↔ geniş desen VAR)* |
| **⑧** | `test_c3…:152` · ~~`test_a15…:71`~~ · `test_arsivlenmis…:135` — kendi metnini ölçüyor | 🔴 **DEKORATİF KAPI** | ◐ **A15 KAPANDI**, C3 ve F1 bekliyor |

---

# FAZ A — ölçüm/değerlendirme altyapısı

| # | kalem | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|---|
| **A1** | garson korpusu | ✅ *«BAĞLANDI»* | ◐ **bağlı ama hiçbir olağan koşumda KOŞMUYOR**: `YEREL_KAPI=("korpus","gercek")` → yerel kapıda yok; `--hepsi`'de `_garson_korpusu_kosulabilir()` **False** (env'siz). 🔴 Diskteki **en yeni** artefakt (08-12 10:58) `route 9·garson 2·orkestra 0` → **11/21**, taban **17** → `kapi()` kuralına göre **KIRMIZI**; rapor **18/21** yayınlıyor. Kaset ıskası mı gerçek gerileme mi — **ayırt eden yok** | ✅ |
| **A2** | cevapsız manşet | ✅ | ✅ gerçek (`lab/nl_corpus.py:534`, f-string append) | ⊘ *(iddia doğru)* |
| **A3** | şişme beyanı | ✅ | ✅ gerçek (`lab/nl_corpus.py:544-545`) | ⊘ |
| **A4** | kurulum süresi | **işaretsiz** | 🔴 **HİÇBİR KARAR YAZILMAMIŞ** — raporda 2 kez geçiyor (`:3332`, `:4234`), karne #27 `🔴 YOK`. FAZ 0'ın **tek işaretsiz** kalemi; `§40`'ın kendi kuralını (*«kararı yazılmadıkça kapanmaz»*) ihlal ediyor | ✅ |
| **A5** | `syrupy` | ⊘ red | ◐ karar doğru (paket **yok**), **gerekçe varsayım**: *«30+ kapı yapıya bağlı»* hiç sayılmamış | ✅ |
| **A6** | `test-suite-sql-eval` | ⏸ park | ✅ şart yazılı **ve bugün doğru** (`sessiz_yanlis=7`, payda `2286`) | ⊘ |
| **A7** | EHRSQL güvenilirlik | ✅ yayınlandı | ◐ **YAYINLANDI, KORUMASIZ** — `test_f8_dogruluk_yayini.py`'de bu bölüme ait **sıfır** yüklem; bölüm silinse süit yeşil kalır | ✅ |
| **A8** | Inspect AI `stderr` | ✅ | ◐ **YAYINLANDI, KORUMASIZ** (Wilson aralıkları kapısız). ⊙ Ve yetenek **yeni değil**: `eval/run.py` `coverage_ci95`'i **2026-07-30**'dan beri taşıyor (`9456d21`), A8 *«bu turda yapıldı»* diyor | ✅ |
| **A9** | `promptfoo` | ⊘ red | ✅ ölçüme dayalı ve doğru (`eval/run.py` gerçekten selective-prediction) | ⊘ |
| **A10** | `Dr.Spider` sağlamlık | ✅ | 🔴🔴 **KAPI ÖLÜYDÜ** → **ONARILDI (bugün)**: yüklem `cube_query.cube`'a bağlandı · 2 skip'li çift ölçülmüş 4 çiftle değiştirildi · **ölçülen 2 gerçek devir vakası** (`toplam ciro`→`toplm ciro`, `ortalama oee`→`ortalama oe`) ayrı bir *sessiz-yanlış* kapısına kondu · **meta kapı**: hiçbir vaka atlanamaz. **10 geçti · 0 atlandı** | ✅ |
| **A11** | TURSpider | ⏸ park | ✅ kodda iz yok, şart yazılı | ⊘ |
| **A12** | tur bazında ölçüm | ✅ | ◐ **kod var, kanıt+kapı yok**: en yeni artefakt `tur` sütunu **taşımıyor** (kod commit'inden **önce** yazılmış) → tablo hiç üretilmemiş. Rapor *«3 zincir · 11 tur»*, `KORPUS` **2 zincir · 8 tur** (tur≥2 paydası **6**). 🔴 Karne satır 10 hâlâ `🟡 tur bazında ÖLÇÜLMÜYOR` → **kendi içinde çelişki** | ✅ |
| **A13** | plan ayrışması | ✅ | ◐ araç gerçek (`/stats/plan`), **kapı yok**, sayaç bellek içi. Canlı: `tek_adimli 3 · cok_adimli 0` — yayınlanan %79'u ne doğrular ne çürütür, **korunmadığını** gösterir | ✅ |
| **A14** | hava boşluğu | ✅ *(7)* | ✅ gerçek ve sağlam — ama kapı sayısı **9** (rapor 7 diyor → **düzeltildi**) | ✅ |
| **A15** | Wren `evals/` | ⊘ **ve** ⏸ | 🔴 **İKİ FARKLI İŞARET AYNI BELGEDE**: `:4476`=`⊘ YAPILMIYOR`, `:4487`+`:4863`=`⏸ PARK`. 🔴 Kapının 3. testi `assert "eval" in kapi` — `"eval"` dosyada **22 kez** geçiyor → **hiçbir mutasyonla kırmızı veremez** | ✅ |

**A · iyileştirme önerileri (ajan):** ① A10 yüklemini düzelt + `skipped==0` meta-testi *(yapıldı)* · ② `test_f8`'e Wilson **ve** EHRSQL yüklemleri ekle (`85+1+339+11.732+45 == 14.957`) · ③ `test_a15`'i `ADIM_ANAHTARLARI`/`TOPLUDA_YOK` desenine bağla + A15'in tek işareti olsun · ④ yeni `test_a12_tur_kirilimi.py` + `§40.8` birimini düzelt + karne satır 10 hizala · ⑤ `_garson_korpusu_kosulabilir()` **hangi ön koşulun** düştüğünü söylesin; A1 bir faz-sonu demetine girsin; 11/21 araştırılsın; **A4'e karar yazılsın**.

---

# FAZ B — garsona giren bilgi + route yığını

| # | kalem | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|---|
| **B1** | şema daraltma | ✅ *(%0–95)* | ✅ ama **KISMİ**: 30 soruda **%0–90,9 · ort %37,3 · fail-open 14/30 (%47)**. 🔴 `soru=` **5 çağrı yerinin yalnız 1'ine** geçiliyor — `ask.py:4003` ✅ ama `:270`·`:359`·`:5017` ve `plan_tuketici.py:411` **YOK**. Yani takip turları (`refine_cube`) ve plan içi garson **her seferinde 23.729 karakterin tamamını** alıyor. Fail-open tetikleyicisi **Türkçe morfoloji** (`durum` sinonimi `durumunu` token'ını açıklamıyor) | ✅ |
| **B2** | VQR few-shot | ✅ | ✅ ama **KISMİ**: tek çağrı yeri; `_cube_select_system`'in **6 çağrısından 1'i** besleniyor. Canlı doğrulandı (*«ram 3 makinesinin verimliliği»* → `RAM-3`, `ort_oee 51,78`) | ✅ |
| **B3** | iş sözlüğü | ⏸ park (§26) | ✅ gerekçe birebir doğru (`business_rules` yalnız Discovery istemine giriyor) | ⊘ |
| **B4** | reflect+repair | ✅ | ✅ doğru **ve kapısı canlı** — mutasyon (tavan 2→5) **kırmızı** verdi | ⊘ |
| **B5** | Snowball TR kök | ⊘ red | ◐ karar doğru, **kapsamı fazla geniş**: gerekçe route tüketicisine ölçülmüş; B1'in kapsama yükleminde ek-toleransı **güvenli ve gerekli** | 🔵 |
| **B6** | Zemberek | ⊘ red | ✅ **FAZ B'nin en iyi belgelenmiş reddi** (`app/ek.py:8-14`, üç somut engel) | ⊘ |
| **B7** | M-Schema | ⏸ park | ✅ doğru ama **ALARMSIZ** — şart yalnız düzyazı, açılışı haber verecek kapı yok | 🔵 |
| **B8** | `resolve_used_table_names` | ⏸ park | ✅ doğru ama **ALARMSIZ** (aynı sınıf) | 🔵 |
| **B9** | iki-sağlayıcılı hakem | ⏸ park | ✅ doğru + 🔴 **KİMLİK ÇAKIŞMASI**: `B9` **üç şeye** bağlı — §14.14 hakem · `app/diyalog.py:89` **ODAK VARLIK** · `tests/test_b9_sparc_iliskileri.py` **SParC** | 🔵 |
| **B10** | SKILLS | ✅ *(off)* | ✅ **KISMİ**: 🔴 **İKİ kapı dosyası aynı üç kuralı** ölçüyor (`test_b10_skills.py:60,79,91` ↔ `test_d9_metodoloji_skilleri.py:80,98,110`) → `KAT-1`. 🔴 `skills_metni()` **KİRACI KÖRÜ**: `project_dir` parametresi **var, hiç geçilmiyor** → her kiracı aynı skill metnini alıyor (bayrak `off` olduğu için bugün zararsız) | 🔵 |
| **B11** | ephemeral sorgu | ⊘ | ✅ doğru — **120/121 = %99,2** boyut değer taşıyor; `FuzzyIndex` **1.306** girdi | ⊘ |
| **B12** | granülerlik | ⊘ + tek sahip ✅ | ✅ tek sahip 4/4 doğrulandı. 🔴 **§14.16 C BAYAT** (*«iki yerde elle yazılı… KAT-1 ihlali»*) · 🔴 **satır 4497 BAYAT** (*«hızlı bir kazanç»*) · 🔴 **BEŞİNCİ kopya var**: `_GRAN_LABEL` (`cube_router.py:4579,4639`) — *«beşinci kopya doğamaz»* kapısı `{`'li sözlüğü **kaçırıyor** · 🔴 **canlı sessiz-yanlış AZALTILMAMIŞ**: *«bu yıl saatlik duruş dağılımı»* → **`neden`** kırılımı, `note` **BOŞ** | ✅ |
| **B13** | değer profilleme | ✅ | ✅ doğru | ⊘ |

**B · iyileştirme önerileri (ajan):** ① B1 kapsama yüklemini **var olan** kapalı ek sınıfına bağla (`_AD_YAPAN_EKLER`/`turetme._kokler` — yeni sözlük yazılmaz, `ADR-0008`+`KAT-1` uygun) · ② `soru=`'yu **unutulamaz** yap (kapı: *«garson yolundaki her `metin_ve_indeks` çağrısı `soru=` taşır»*) · ③ B12: `hour` kapalı kalsın **ama** *«saatlik»* isteyen soru `ADR-0020` beyanı alsın · ④ `_GRAN_LABEL`'i sahipten türet + beşinci-kopya kapısını `{`'ye genişlet · ⑤ `skills_metni`'ni kiracıya bağla + iki kapıyı birleştir.

---

# FAZ C — ajan/orkestrasyon + MCP yüzeyi

| # | kalem | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|---|
| **C1** | tek yetenek kaydı | ⊘ + ✅(`§D6`) | ✅ **GERÇEK** — 15/15 fiil↔araç birebir, ayrışma **içe aktarmada** patlıyor | ⊘ |
| **C1** | *«`KAT-1` ihlali»* iddiası | — | ◐ **KISMEN**: `c1`=4 · `d6`=8 yüklem → **12 yüklem, örtüşen 1**. Ana ajanın ölçümü doğru, denetim ajanı yanılmış | ⊘ |
| **C2** | bütçe + stall | ✅ *(kapı 8)* | ◐ **ürün ✅ / kapı eksik**: kapı **7** test (8 değil) · kapı **yalnız varsayılanı** ölçüyor · 🔴 **İKİ CANLI ÇAĞRI `sorgu=0` geçiyor** (`routers/ask.py:273`, `answer.py:567`) = *o eksende sınırsız* — kapının **adıyla yasakladığı hâl**, ve gerekçesi yazılı değil | 🔵 |
| **C3①** | araç örtüşmesi | ✅ | ✅ doğrulandı (örtüşen çift 1, `KAYIT` 31 ≤ 35) | ⊘ |
| **C3②** | yazma aracı yok | ✅ | ✅ doğrulandı **bayrak açıkken de**: `KAYIT`=33 ama `mcp.araclar`=31, kesişim **∅**; ad bilinse bile reddediyor | ⊘ |
| **C3③** | dört kapı | ✅ | 🔴 **KAPI SAHTE-YEŞİL** — `assert "Planlayici" in inspect.getsource(...)`; iki jeton da `cagir`'ın **docstring'inde** geçiyor → gövdedeki çağrı silinse kapı yeşil kalır (`test_c3…:152-155`) | 🔵 |
| **C3④** | sanitizasyon | ✅ | 🔴🔴 **GÜVENLİK — ENGELLENMİYOR.** `mcp.py:181` tek geçişli `str.replace`, ve yerine konan dize sentinel'in **öneki/soneki**: `ZARF_SON` → `">>>"`. Sonuç: `"DIMA-VERI"+"DIMA-VERI>>>"` → `"DIMA-VERI>>>"` **yeniden kuruluyor**. **KENDİ ÖLÇÜMÜM:** `_zarfla` çıktısında `ZARF_SON` **2 kez** → zarf **erken kapanıyor**, hücredeki *«YENİ TALİMAT»* beyan edilmiş veri bölgesinin **dışında** kalıyor. Kapının yüklemi doğru, **test vektörü** eksik (`test_c3…:108` yalnız tek sentinel besliyor) | 🟣 **DOĞRULANDI** |
| **C4/C5** | — | — | ✅ **YOK** — `§14.1:3197-3199` FAZ 2'yi `C1·C2·C3` olarak sayıyor; kapsam tam | ⊘ |
| **+** | `§14.11 D9` MCP borcu | işaretsiz | 🔴 **ŞART GERÇEKLEŞTİ, İŞ YAPILMADI**: `agent_error`/`ambiguous_measure` `app/` altında **0**. Canlı: `/ask` → `suggestions[{kind:"tanim",…}]` **yapısal**; `/mcp/call route` → `text:"null"`. Aday üreten üç fonksiyon `tools.KAYIT` **dışında** — bilgi *kaybolmuyor*, **hiç üretilmiyor**. Ajan `null` alıyor: bu *«dürüst red»* bile değil, **sessiz red** | 🔵 |
| **+** | `§14.16 E` Wren ad hizalaması | — | 🔴 **İKİNCİ SAYILMAMIŞ BORÇ**: `query_cube`·`list_cubes`·`describe_cube`·`get_context`·`recall_queries` **hiçbiri** yok; şartı (`C3` açılışı) doldu, karar **kararsız** | 🔵 |
| **+** | `tools.get` hata mesajı | — | ⚠ `KeyError` **tüm 31 aracı** listeliyor (`tools.py:839`), `principal`'a göre **süzülmüyor** → rol matrisi açıldığı gün **envanter sızıntısı** | 🔵 |
| **+** | MCP bütçesi | — | ⚠ `routers/mcp.py:59` her istekte **taze** `Planlayici(butce=Butce())` → `§C2` tavanı **oturum değil çağrı** tavanı; ajan N çağrıyla N×tavan harcayabilir | 🔵 |

**C · iyileştirme önerileri (ajan):** ① zarf sınırını **sabit-noktaya** taşı + kapı vektörünü **çiftle** · ② `belirsizlik.adaylar` **aracı** aç (`§14.11 D9`'un ödemesi; `KAT-1` korunur) · ③ üç kapıyı metinden **davranışa** çevir (sahte planlayıcı + gerçek aşım + `ast` ile tüm `Butce(...)` çağrıları) · ④ MCP'ye **oturum bütçesi** ya da en azından `_meta`'da **kalan bütçe** · ⑤ `tools.get` hata mesajını yetkiye göre süz.

---

# FAZ E — istatistik / kök-neden

| # | kalem | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|---|
| **E1** | Adtributor | ◐ | ⊘ dürüst — ama gerekçe zinciri kırık: *«E3 ön koşuldu, yapıldı»* deniyor; E3 kartın saydığı **4 tarama yerinin 1'ini** kapsıyor | 🔵 |
| **E2** | JS sürprizi | ✅ | ◐ **YARIM** — matematik **DOĞRU** (bağımsız JSD ile fark `4,2e-07`, sıfır olasılık doğru atlanıyor). 🔴 Ama **tel üstünde DÜŞÜYOR**: `/ask/contribution` (ön-ucun çağırdığı **tek** uç) `surpriz_notu` **taşımıyor**, bulgularda `surpriz`/`surpriz_pay` **yok**. 🔴 Ve `surpriz_notu` adayını **kırpılmış** listeden seçiyor → dağılımı en çok değiştiren segment (JS payı **%43,3**) hareketi küçük diye **sessizce siliniyor** | 🔵 |
| **E3** | FDR → tarama beyanı | ✅ | 🟡 **VEKİL ÖLÇÜT** — BH reddi doğru ölçülmüş, ama beyan **tek çağrı yerinde** (`interpret.py:425-427`) ve `n_aday = len(rows)` = *tek serideki nokta sayısı*. Kartın saydığı 3 tarama yeri (`_en_ayristiran`·`derinles`·`contribution`) **hiçbir şey beyan etmiyor** | 🔵 |
| **E4** | Adlandırma | ✅ | ✅ kapı gerçek (`ast` + ön-uç metni), 5 yeşil | ⊘ |
| **E5** | `ruptures`+`statsforecast` | ⏸ park | ✅ doğru park — ⚠ rapor **kendisiyle çelişiyor**: `:4289` *«E2'nin ÖN KOŞULU»* ↔ `:4074-4077` *«ön koşulu değilmiş»* | 🔵 |
| **E6** | Explanation Tables | ⊘ | ✅ doğru (kartın kendisi *«oku»* diyor) | ⊘ |
| **E7** | LMDI | ⊘ | ✅ **BAĞIMSIZ DOĞRULANDI**: `|Σδ − Δbütün| = 0,00e+00`, gövdede log yok, alt-grup toplanabilirliği **TAM**; `ast` göçü doğrulandı (yorumda `log2` yanlış-kırmızı yapmıyor). 🔴 Ama bir kapı **kör**, beyan **ön-uçta bozuk** (aşağıda) | 🔵 |
| **+** | 🔴 `kok_neden.toplam_turu` | — | 🔴🔴 **SESSİZ YANLIŞ PAY, YAYINDA.** `_toplam = sum(abs(...))` ama metin *«toplamın %P'i»* diyor; `_akran` **mutlak** ortalama, metin *«ortalaması»* diyor. Yayınlanmış karışık-işaretli ölçüyle (`enerji_sapma.toplam_enpg`) ölçüldü: cümle *«%51,4'ünü taşıyor … öteki ortalaması 4.250»* — **gerçek pay %600**, **gerçek ortalama −3.750**. Akıcı, doğru biçimli, **12 kat yanlış ve işareti ters**. `contribution.py:191-196` aynı kapıyı **zaten koyuyor** → aynı pay cebrinin **iki sahibi** (`KAT-1`) | 🔵 |
| **+** | 🔴 `kirpilan_esik_yuzde` | — | 🔴 **BİRİM HATASI, KULLANICIYA GÖRÜNÜR.** Backend `1.0` (yüzde), ön-uç `(x*100).toFixed(1)` → *«N segment eşiğin altında kaldı (|pay| < **%100.0**)»*. Kapı göremez: `test_KIRPMA_SESSIZ_DEGIL` yalnız **anahtar varlığına** bakıyor, hiç kırpma olmayan veride de yeşil. ⚠ Ayrıca beyan yalnız **SAYI** taşıyor, **kütle** taşımıyor: 41 segmentin 40'ı kırpılınca gösterilen toplam **%83,3**, gerçek **%99,3** → **16 puan görünmez** | 🔵 |
| **+** | `stats.py` | *«56 satır, forecast/regresyon yok»* | 🔴 **İKİSİ DE BAYAT**: dosya **156 satır**; forecast yok ✅ ama **regresyon VAR** (`trend()` en küçük kareler + `r²`, `stats.py:63-101`) — dürüstlüğü iyi (`n<5 → None`) ama önerme yanlış | 🔵 |

**E · iyileştirme önerileri (ajan):** ① `toplam_turu`'nun pay cebrini `contribution`'a **devret** (tek sahip); işaret/büyüklük ayrışıyorsa pay **basılmasın** · ② kırpma beyanına **KÜTLE** ekle (`kirpilan_pay_yuzde`) + ön-uçtaki `*100`'ü kaldır + kapı **render edilen dizgeyi** ölçsün · ③ E2'yi **tele bağla** (4 alan) · ④ `surpriz_notu` adayını **kırpılmamış** listeden seç, kırpılanların JS payı ≥%20 ise **beyan et** · ⑤ E3'ü kalan üç tarama yerine genişlet — genişletilmiyorsa **rapora yaz**.

---

# FAZ F — motor / platform / yayın

| # | kalem | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|---|
| **F1** | motor temizliği | ✅ ⟳08-12 | ✅ **ÖZÜ DOĞRU**: `app/`+`lab/` izi **0** · env **47 değişken** · imaj **yok** · `:8080` **boş** · motor `wren 0.13.2` + `wren-core-py 0.7.3` in-process, canlı curl 5 gerçek satır. 🔴 Ama **4. kapı DEKORATİF**: kendi kaynak dosyasını okuyup içinde `"wren-project"` arıyor (`:135`) → `demo/wren-project` **tamamen silindiğinde 4/4 YEŞİL** kaldı. ⊙ Ve kartın *«silinirse her cevap düşer»* uyarısı da **abartılı**: derleme artefaktı, `main.py:57` her açılışta yeniden üretiyor | 🔵 |
| **F2** | `cube_sql` ↔ motor | ✅ | ✅ doğru (2 gerçek çağrı, kapı 8/8) | ⊘ |
| **F5** | silinecek kod yok | ✅ | ✅ doğru — ⚠ bir nüans yanlış: kart *«`motor_rls`/`motor_cls` kapalı»* diyor, ölçüm `motor_rls="shadow"` · `motor_cls="off"` | 🔵 *(nüans)* |
| **F7** | ilan edilmiş kapsam | ✅ | ⚠ **özü teslim, KALINTI KUSUR**: beyanın içindeki **elle yazılmış** örnek *«son 6 ayda ciro nasıl gitti»* → `route()` = **`None`** (çıkmaz, ikinci duvar); chipler **konu-kör** (`schema["cubes"][:6]`, ilk cube dolunca dönüyor → hep `bakim`). `yetenek.py:366` bu kusuru **kendi docstring'inde** yazmış | 🔵 |
| **F8** | yayınlanmış doğruluk | ✅ | ✅ **AYRIM KAPANIYOR**: `sum(cats)=14.957 ≡ sum(kesme_payda)=14.957`, **fark 0**; `CUBE-SAPMA(None)` **45 (%0,30)** adıyla yayında; 13 kapı yeşil | ⊘ |
| **F10** | `dry_run`/`register_csv` | ⊘ | ✅ doğru | ⊘ |
| **F11** | RLS | ⊘ | ✅ doğru | ⊘ |
| **F12** | manifest uyumu | ⊘ | ✅ doğru, kör kapı düzeltilmiş | ⊘ |
| **F13** | onaylı yazma | ✅ | ✅ **birebir doğrulandı**: kapalı → `31 {'yok':31}` · açık → `33 {'yok':31,'yazar':2}` → **üç değil İKİ**. 🔴 `EYLEM_KAYIT=3` ↔ `ARAC_EYLEM=2` → **`tercih.kaydet` hâlâ araçsız**, bağlama **tek yönlü**. ⊙ Ve gerekçe ayrımı: `measures.approve` **haklı olarak** dışarıda (eylem karşılığı yok, fail-closed), ama `tercih.kaydet` **`EYLEM_KAYIT`'ta VAR** (`eylem.py:104-112`) — onay yolu **kurulu**, yalnız araç yok | 🔵 |
| **F14** | dört yetenek | ⊘ | ⚠ **KARAR SAVUNULABİLİR, GEREKÇE YANLIŞ**: `dry_run` app/lab/tests **0** · `dry_plan` **25 gerçek çağrı** (grep 70 = metin) · `pushdown_limit` **0** · `list_tables` **0** · `transform_sql` *«yüzeyde yok»* **YANLIŞ** — deponun kendi testleri **7 kez** çağırıyor | 🔵 |
| **F15** | `Model`/`RemoteFunction` | ⊘ | ✅ doğru | ⊘ |
| **F16** | views fan-out kapısı | ✅ *«ZATEN VAR»* | 🔴🔴 **KÖR KAPI — 9 view'ın 1'ini görüyor.** `_view_files(settings.resolved_project_dir())` yalnız **varsayılan tenant**: `enerji_tesis`(1). Görülmeyenler: `gitas` **3** · `gulteks` **2** · `atiksan` **2** · `demo-boyahane` **1**. `karlilik_src` **2 LEFT JOIN** taşıyor (`stok_kartlari ON STOK_KODU`) — `parti_zengin`'in **tam sınıfı**; fan-out `sale_amount`'ı şişirir ve `source="cube"` rozetiyle çıkar | 🔵 |
| **+** | `pyproject` | rapor `:983` *«`wrenai` + `wren-core-py>=0.7.3`»* | 🔴 **RAPOR YANLIŞ YAZMIŞ**: `pyproject.toml:10` **yalnız** `wrenai>=0.13,<0.14`. `wren-core-py 0.7.3` kurulu ama **geçişli** (`wrenai`'nin bağımlılığı); depo `wren_core`'u **doğrudan** import ediyor (`wren_service.py:1494,1733`) → **beyan edilmemiş doğrudan bağımlılık**; `wrenai` bırakırsa **sorgu anında** düşer | 🔵 |

**F · iyileştirme önerileri (ajan):** ① F16 kapısını **tüm tenant'lara** aç + paydayı kilitle (`len(views) >= 9`) · ② F1'in 4. kapısını **tautolojiden** çıkar (yapısal yüklem: dizin var **ve** `SERVIS_IZLERI` ile çakışmıyor **ve** `compose_and_build` üretebiliyor) · ③ F7'nin elle yazılmış örneğini **tek sahibe** indir + `onerileri_kur`'a **soruyu** ver · ④ F14'ün gerekçesini tazele, sonra **yalnız `get_available_functions`**'ı ölçülü aç · ⑤ F13'ün tek yönlü bağlamasını kapat (`preferences.set → tercih.kaydet`) ya da asimetriyi kapıya **adıyla** yaz. *(Ek: `pyproject`'e `wren-core-py>=0.7.3` beyan et.)*

---

# FAZ D — üç ayrı `D` kimlik kümesi

> D-ilişkili **15 kapı dosyası · 112 test, hepsi yeşil**. Aşağıdaki yargılar yeşilliği
> değil, **kapının ne ölçtüğünü** ölçer.

## D-A · `§38` KAPANIŞ KARTLARI (D1–D13)

| kimlik | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|
| **§38 D1** garsona şema | ✅ | ✅ gerçek — 8 soruda tasarruf `%0/49/60/91/91/93`, indeks **23=23** hiç budanmıyor. ⚠ *«2/8 %0»* ajanın setinde **3/8**, tavan %95 değil **%93** → payda farklı, **yeniden ölçülmeli** | 🔵 |
| **§38 D2** garsona örnek | ✅ | ✅ **gerçek ve canlı** (`ask.py:4093-4096`, bayrak `beta`). ⚠ Kart *«`vqr.ara()` yeni»* diyor; ölçüldü **`vqr.ara` YOK** — iş `few_shot_block` ile yapıldı, kartın ÖNCE/SONRA metni **bayat** | 🔵 |
| **§38 D3** iş sözlüğü | ⏸ | ✅ gerekçe ölçüme dayanıyor (`business_rules` tek çağrı: `llm.py:225`, Discovery istemi) | ⊘ |
| **§38 D4** belirsizlik | ✅ | ✅ gerçek (canlı: `note` + `suggestions[{kind:"tanim"}]`). 🔴 **Ön uç `kind`'ı GÖRMÜYOR** — `ReportPanel.tsx:357` jenerik basıyor; `belirsizlik_chipi.py:51` *«FE bunu AYRI grupta, KENDİ açıklamasıyla»* diyor → **sözleşme yerine getirilmemiş**; en kritik chip en sıradan görünüyor | 🔵 |
| **§38 D5** sorgu hatası | ✅ | ✅ gerçek (`ONARIM_TAVANI=2`, 11 hata sınıfı çare taşıyor) | ⊘ |
| **§38 D6** plan yetenek listesi | ✅ | ✅ **gerçek ve tam** (15/15, `{'yok':31}`, kapı 13). ⚠ `MIMARI.md §2.0 «tek yetenek kaydı»` → **grep 0**, yazılmamış | 🔵 *(belge)* |
| **§38 D7** yetki denetimi | ✅ *(5)* | ✅ gerçek — ama kapı **6** test. 🔴 **`§14.14 F13` ile ÇELİŞİYOR** (aşağıda çelişki #5) | 🔵 |
| **§38 D8** durdurma koşulu | ✅ *(8)* | ✅ gerçek (`Butce(8, 30.0, 12)` birebir, `AZAMI_ADIM=12`) — kapı **7** test | 🔵 *(sayı)* |
| **§38 D9** metodoloji skills | ✅ | 🟡 **YARIM** — 3 dosya var, yükleyici okuyor, **ama `skills: off`** → `katalog_metni.py:380` metni **hiç eklemiyor**. `§14.14 B10` aynı işe *«KISMEN KAPANDI»* diyor, `§38` **düz ✅** | 🔵 |
| **§38 D10** cevap biçimi | ✅ | ✅ **CANLI DOĞRULANDI, en güçlü kalem** — *«bu yıl toplam ciro»* → 4 chip, iz: *«§D3 biçim: soru türü «toplam» — kapatılan kova: +ölçü, top-N»* | ⊘ |
| **§38 D11** olgu üretimi | ⏸ | ✅ gerekçe sağlam (`ast`: 14 tip sabiti, 0 dinamik; `TANINAN` 12 + 2 gerekçeli istisna) | ⊘ |
| **§38 D12** kök-neden yatay eksen | ⏸ | ✅ gerekçe ölçüldü (`adtributor.py` yok; `surpriz_notu` + `tarama_beyani` var) | ⊘ |
| **§38 D13** dış yüzey (MCP) | ✅ | 🔴🔴 **İŞARET FAZLA İYİMSER** — aşağıdaki `D9/MCP` bölümüne bak: mekanizma ✅ ama **yayımlanmış sözleşme YANLIŞ** | 🔵 |

## D-B · `§14.1` FAZ 3 YOL HARİTASI (D1–D5)

| kimlik | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|
| **§14.1 D1** olgu sayacı | ✅ başlık / ⏸ kart | ✅ **kapı doğru şeyi ölçüyor** (bağımsız `ast` ölçümü regex'le birebir → kör nokta yok). ⚠ **aynı satırda iki işaret** (`:3732` ✅ ↔ `:3777` ⏸) | 🔵 |
| **§14.1 D2** taksonomiyi aç | **işaretsiz** | 🟡 **KARARI YAZILMAMIŞ** — D1'in ölçümü kalemi *«gereksiz»* ilan etmiş, `_streak` eşiği 3 aklanmış, ama kalem ne ✅ ne ⊘ (`:3787`). `§40`'ın kendi kuralına aykırı | 🔵 |
| **§14.1 D3** cevap biçimi | ✅ | ✅ gerçek (6 tür × 5 kova, `min` indirgemesi, `None`→`KURAL B`). ⊙ Rapor `6,6,5,…` ↔ `bicim.py:14` `6,6,6,6,5,6,6,5` **çelişki değil** — rapor-anı ↔ ölçüm-anı, ikisi de yazılı | ⊘ |
| **§14.1 D4** ön-uç sayı biçimi | ✅ | ✅ kapı 5/5 — 🔴 **RAPOR BAYAT**: *«`maliyet.ort_kar_marji_yuzde` kapıda `OLCULMEDI` olarak kayıtlı»*; ölçüldü **`OLCULMEDI = set()` BOŞ**, kalem canlı ölçülüp (28,13) kanıtlı `OLCULDU_ZATEN_YUZDE`'ye taşınmış. **Kod rapordan ileride** | 🔵 |
| **§14.1 D5** takip anlama | ◐ *(5)* | ✅ **dürüst ◐** — kapı **6** test; kart *«odak varlığı yok»* diyor, gövde onu çürütüyor ama işaret ◐ doğru | 🔵 *(sayı)* |

## D-C · `§14.11`/`§14.14` RAKİP ANALİZİ (D6–D11)

| kimlik | rapor | **ÖLÇÜLEN** | durum |
|---|---|---|---|
| **§14.11 D6** Draco hard kısıtları | işaretsiz | Kalem kalem ölçüldü: `stack_without_summative_agg` → ✅ **eşdeğeri var** (`viz.py:474 _additive()`) · `color>20` → 🟡 kısmi (`_KATEGORI_TAVANI=20`, yalnız `bar`+sıralanmamış) · `size_nominal`/`shape>8` → ⊘ **konu dışı** (backend spec'inde size/shape kanalı **yok**) · `bar_area_without_zero`/`area_bar_with_log` → 🔴 **YOK**, ikisi de **ön-uç eksen** işi. ⊙ **Gerçek kalan yüzey 2 kısıt**; kart olduğundan **çok büyük** görünüyor | 🔵 |
| **§14.11 D7** AVA `ckb`+`purpose` | işaretsiz | ⊘ **İTHALAT GEREKSİZ** (257 MB npm) — `purpose`'un karşılığı **zaten var** (`niyet`'in kapalı 6 türü, `bicim.py` tüketiyor). 🟢 **Ama gerçek bir delta var**: `viz.recommend` **niyeti hiç almıyor**, grafik kararı yalnız veri şeklinden | 🔵 |
| **§14.11 D8** CompassQL etkinlik tabloları | işaretsiz | 🟡 açık ama **düşük getirili**: skor tablosu yok (dallı karar var), bugünkü karar canlıda **10/10**; skor tablosu **yeni bir kalibrasyon borcu** getirir | 🔵 |
| **§14.11 D9** Metabase `candidates`+`agent_error` | işaretsiz *(şart gerçekleşti)* | 🔴 **GERÇEK BOŞLUK, ve sanılandan GENİŞ** — aşağıda ayrı bölüm | 🔵 |
| **§14.14 D10** tanım çakışması | ✅ | ✅ **RAPORUN EN İYİ KALEMİ** — bağımsız yeniden üretildi: 9 çok-küplü ölçü, **tam 3'ü farklı formüllü**; kapı 10, `test_ASK_YOLUNA_BAGLI` **adrese değil zincire** bağlı | ⊘ |
| **§14.14 D11** denormalizasyon | işaretsiz | 🟢 **ÖLÇÜLDÜ, BUGÜN KAPATILABİLİR**: ① *«kaç küp 3+ modelde»* → **7/23 (%30)**, `kalite` 4 tablo ② *«`certified` kaçında `olculmedi`»* → **0/9** (hepsi `olculdu:saglikli`, `hops=1`). Kartın hipotezi (*«JOIN'i derleyici kurar, risk yapısal düşük»*) **doğrulandı** — ama sayı **yazılı değil** | 🔵 |

## D-D · 🔴 ÇELİŞEN İŞARET AVI — **7 tane** *(raporun bildiği: 1)*

| # | çelişki | not |
|---|---|---|
| 1 | `✅ §14.1 D1 Olgu sayacı` ↔ `⏸ §38.3 D11 Olgu üretimi` | `§0.7`'de yazılı. ⚠ Üstelik `§14.1 D1` **kendi içinde**: başlık ✅ (`:3732`), kart gövdesi ⏸ (`:3777`) |
| 2 | 🔴 **`§0.7` HARİTASI EKSİK: `D6` ve `D10` satırları YOK** | Harita **9 `D`** sayıyor, gerçek **11**. `D6`=`Plan yetenek listesi`✅ ↔ `Draco hard kısıtları` · `D10`=`Cevap biçimi`✅ ↔ `Tanım çakışması`✅ |
| 3 | 🔴🔴 **VE KAPIM ONLARI GÖREMİYOR — kör nokta** | `test_kimlik_uzayi_tek_anlamli._cakisanlar()` deseni `[^|*\n]` **`**`'ta duruyor** → hücre `🔴 **Draco…**` ile başlayınca başlık kesiliyor. **KENDİ ÖLÇÜMÜM:** dar desen `D6`/`D10`→**YOK**, geniş desen (`[^|\n]{4,60}`)→**VAR**. Taban kapısı (`≥40`) 62 sayıp **yeşil kalıyor** → kapı sağlıklı görünürken iki satırı **sessizce düşürüyor** | 🟣 **DOĞRULANDI** |
| 4 | `✅ §38.2 D9 Metodoloji ÜÇÜ DE YAZILDI` ↔ `✅ §14.14 B10 KISMEN KAPANDI` + `skills: off` | aynı iş, **iki farklı tamlık** işareti |
| 5 | 🔴 `✅ §38.2 D7` *«boşluk yok, arkasında bir şey yok»* ↔ `✅ §14.14 F13` *«`Planlayici.calistir()`'in dört kapısında `yan_etki`·`onay`·`bilet` hiç geçmiyordu»* → **beşinci kapı** eklendi | **İkisi de `Planlayici.calistir()`'i adıyla anıyor**, zıt sonuca varıyor, ikisi de ✅ — **uzlaştırılmamış** |
| 6 | `✅ §38.2 D8 Durdurma` ↔ `✅ §14.1 C2 Bütçe+stall` | Rapor *«aynı iş»* diyor ama **iki satır** sayıyor → `§14.15`'in **59** toplamı **1 fazla** |
| 7 | `§38.1 D2` kartı *«`vqr.ara()` yeni»* ↔ gerçek `vqr.ara` **yok** | işaret ✅ doğru, **gerekçe** bayat |

**Bayat kapı sayıları (4):** `§38 D7` «(5)»→**6** · `§14.1 D5` «(5)»→**6** · `§38 D8/C2` «(8)»→**7** · `§14.14 A14` «(7)»→**9**.

## D-E · 🔴🔴 `§14.11 D9` + MCP SÖZLEŞMESİ — **en ağır D bulgusu**

**① Şart gerçekleşti:** `mcp_yuzeyi: beta`; `agent_error` `app/` altında **0** (tek geçiş bir kapı assert'inde).

**② Boşluk gerçek ve raporun sandığından geniş.** Belirsizlik beyanının **tek** tüketicisi
`routers/ask.py:1976` — yani **yalnız HTTP `/ask`**. MCP yolu o zincire **hiç uğramıyor**:

| | HTTP `/ask` | MCP `route` |
|---|---|---|
| beyan | *««fire» birden fazla yerde ve **FARKLI FORMÜLLE** tanımlı… başka bir hesaptır»* | **YOK** |
| aday | `suggestions:[{kind:"tanim", label:"fire (OEE)", query:"OEE fire"}]` | **YOK** |

⊙ Yani MCP'deki ajan `toplam_fire_kg`'yi alır, `oee`'deki **aynı adlı başka hesaplı**
ölçüyü **bilemez** — `§14.14 D10`'un insanlar için kapattığı sessiz-yanlış, ajan yüzeyinde
**açık**. Raporun *«`Adim` makbuzunda aday alanı yok»* çerçevesi eksik: **beyan metni de yok**.

**③ 🔴🔴 VE DAHA AĞIRI: boşluk «aday» değil, YÜZEYİN KENDİSİ.**

    POST /mcp/call {"name":"route","arguments":{"question":"…","schema":"auto"}}
    → isError:true  "AttributeError: 'str' object has no attribute 'get'"

`route` — merdivenin **birinci basamağı** — MCP'den **çağrılamıyor**. Yapısal ölçüm (31 araç):

| sınıf | adet |
|---|---|
| `inputSchema` **`"string"`** ilan ediyor, gerçek **dict/list** | **23/31** |
| ilan edilen `girdi`'de **zorunlu parametre eksik** | **5/31** |
| **kaynağı MCP router'da hiç sağlanmıyor** (`servis:llm`, router yalnız `{"servis:wren"}`) | **3/31** |
| **sözleşmeye uyarak çağrılabilir** | **0/31** |

🟣 **KENDİ ÖLÇÜMÜM:** `mcp.araclar()` → **31 araç, 77 alanın tamamı `"string"`**. Doğrulandı.
Canlı ikili kanıt: `stats.ozet {"degerler":"[1,2,3]"}` (**şemaya uyuyor**) → `isError`;
`{"degerler":[1,2,3,10]}` (**şemayı yok sayıyor**) → 200.

⊙ Bu, `§14.14 F13`'ün **yazma** araçları için ölçtüğü kusurun (*«ilan edilen `girdi`
gerçek imzayla tutmuyor»*, `FAZ H`'ye ertelendi) **okuma yüzeyinin 31/31'inde** tekrarı —
ve kimse ölçmemiş. `§38 D13`'ün *«🟢 CANLI DOĞRULANDI»* satırı bu yüzden fazla iyimser:
**tek bir başarılı çağrı, 31 araçlık bir sözleşme için kanıt değildir.**

**④** `test_BORC_KENDINI_TOPLUYOR_mcp_acilirsa_KIRMIZI` bu borcu **görmüyor** — üç şart
sayıyor, `§14.11 D9` listesinde yok. *Kimlik çakışması borcu görünmez yaptı, ve borcu
toplamak için yazılmış kapı da onu göremedi.*

### ⊘/✅ KARAR ÖNERİSİ — kartı **İKİYE BÖL**

**⊘ `400 + agent_error` REDDEDİLİR**, üç ölçülmüş gerekçeyle:
1. Deponun **ölçülmüş** davranışı zaten daha iyi (`§38 D4` canlı): cevap **verilir** +
   beyan yapılır + öteki tanıma **tek tık**. Metabase deseni cevabı **geri çeker** →
   *«kullanıcı asla cevapsız kalmaz»* + *«dürüst red başarı değil»* ile **doğrudan çelişir**.
2. MCP'de `400`'ün karşılığı `isError:true` ve bir ajan için bu bir **araç arızasıdır**,
   netleştirme daveti değil — ajan ya yeniden dener ya **uydurur**.
3. `§40.9`'un kendi ölçümü: **netleştirme bir red değildir** (2.755 · %18,4). Belirsizliği
   redde çevirmek o %18,4'ü `cevapsız`a yazmak olurdu.

**✅ `candidates` ALINIR** — `_meta.belirsizlik = {terim, secilen_cube, adaylar[], tanim_farkli, beyan}`;
sahip `belirsizlik_chipi` (`KAT-1` korunur), `isError` **değişmez** (`§101.1`), alan yoksa
çıktı bayt bayt aynı (`KURAL B`).
⚠ **Ama sırası İKİNCİ.** Bir ajan `route`'u çağıramıyorken aday listesi eklemek, **kapalı
bir kapının arkasına tabela asmaktır.** Önce `inputSchema` üreteci.

## D-F · iyileştirme önerileri (ajan)

① **`mcp.araclar()`'ın `inputSchema` üretecini GERÇEK İMZADAN türet** (`inspect.signature` +
annotation; `girdi`'de olmayan zorunlu parametre **içe aktarmada** patlasın — `§D6`'nın
`plan_semasi` deseni). **Tek kapı 31 aracın 31'ini onarır ve `F13`'ün `FAZ H` borcunu da kapatır.**
② `§0.7` kapısının **kör noktasını kapat** (desen `[^|\n]{4,60}`) + `D6`/`D10` satırlarını
haritaya ekle + *«dokuz `D`»* → **on bir** + yeni kapı: harita satır sayısı `_cakisanlar()`'daki
`D` sayısına **eşit** olmalı.
③ `viz.recommend`'e **`niyet` kancası** — `§14.11 D7`'nin ithalatsız hâli (yalnız **daraltıcı**
yönde; `ADR-0024` determinizmi ve `KURAL B` korunur).
④ Belirsizlik chip'inin **ön-uç sözleşmesini ya uygula ya sil** (`ReportPanel.tsx:357` `kind`'ı
okumuyor; `belirsizlik_chipi.py:51` aksini vaat ediyor).
⑤ `§14.14 D11`'i **bugün ✅ kapat** — iki sorusu da cevaplandı (7/23 · 0 `olculmedi`); kapı:
*«bir küp 5+ tabloya çıkarsa ya da `hops > 1` olursa kırmızı»*.

---

# EK — `A3` TEST SÜİTİ HIZLANDIRMA *(kullanıcı ayrıca istedi; araştırma bitti)*

*«Testler aşırı şişmiş, 20 dk sürüyor, tekrarlar vakit kaybı… 2-3 dk'ya düşürebilir.
Ama sürekli test çalıştırıp vakit kaybedemeyiz. **PAYDAYI DA KORU**.»*

**Ölçülen tablo (süit koşulmadan, tek örneklem profiliyle):**

| ölçüm | değer |
|---|---|
| çekirdek | **20** — kapı `-n 8` kullanıyor (`lab/kapi.py:518`) → **12 çekirdek BOŞ** |
| toplanan test | **5.505** (431 dosya · 4.292 fonksiyon · 224 parametrize) |
| oturum kurulumu | **10,72 sn/işçi** = `compose_and_build` **4,66 sn** (🔴 **HİÇ ÖNBELLEKLENMİYOR**, 2. çağrı 4,48 sn) + app/TestClient/login ~6 sn |
| `client` fikstürlü test | **381** (86 dosya) ~**0,85 sn** ≈ **324 sn** |
| uzun kutup | `test_ask_golden.py` **80 test ≈ 60 sn** — `--dist loadfile` yüzünden **TEK işçide** |
| en yavaş tek test | **7,87 sn** — kapalı porta (`127.0.0.1:9`) bağlantı **zaman aşımını bekliyor** |

⊙ **İki hipotez ölçümle çürüdü:** `WrenService()` kurulumu **bedava** (tembel, 0,000 sn) →
*«28 dosya kendi servisini kuruyor»* bir maliyet **değil**; test içinde taze app kuran
yalnız **6** yer (sistemik değil).

**Sıra:** ① `-n 8` → `-n 16` *(tek satır, en yüksek getiri/risk)* · ② dev dosyaları böl
(`test_ask_golden` 80 · `test_cube_router` 79 · `test_belge_zenginligi` 54) · ③
`compose_and_build` önbelleği *(en büyük kazanç, **en riskli** — compose yarışı tarihi
var)* · ④ 7,87 sn'lik beklemeyi kes + 14 `time.sleep`'i tek tek ölç.
🔴 **PAYDA KAPISI:** `--collect-only` sayısı **5.505**'in altına düşerse **KIRMIZI**.

> *Hız kapsamdan değil çekirdekten satın alınır — ve payda kutsaldır.*
