# OPERASYON — DİMA v1 · kural seti ve yürütme sözleşmesi

> ⟳ **Bu ARŞİV değil ama AKTİF de değil.** Kayıt olarak duruyor (`MIMARI §10`: *kapananlar işaretlenir, silinmez*); **güncel durum** `belgeler/plan/ONGORU-DURUM.md`'dedir. İkisini birden *«nerede kaldık»* diye okumak, `KAT-1`'in belge düzeyindeki ihlalidir.

---

> 🔴 **BU DOSYA HER OTURUMDA OKUNUR.** Bağlam sıfırlanırsa (compact / yeni oturum) buradan
> devam edilir. Yanında **`OPERASYON-DURUM.md`** vardır: *nerede kaldık*. İkisi birlikte
> operasyonun **tam durumunu** taşır — sohbet geçmişine bağımlılık YOKTUR.

---

## 0 · OPERASYONUN TANIMI

**Hedef:** `DIMA-V1-YOL-HARITASI.md`'nin **v1 kısmını** (FAZ −1 → FAZ 8) uçtan uca teslim
etmek. **v2/v3 bu döngünün kapsamı DIŞINDA** — ayrı döngülerde yapılacak.

**Nihai vaat (kullanıcının kendi cümlesi):** *"verinizi bilen, ayrıştırabilen,
konuşabilen, onayla iş yapabilen ve her sayısını kanıtlayabilen bir meslektaş."*
Ve teknik hedefi: ***"Mükemmel motor + insani yüz tek sistemde."***

**Bitiş ölçütü:** §C'nin **16 ölçütü** yeşil. *"Bitti" bir kanaat değil, bir sayıdır.*

---

## 1 · OTORİTE SIRASI *(çelişkide yukarıdaki kazanır)*

| # | Belge | Yol |
|---|---|---|
| 1 | **MIMARI değişmezleri (§4) ve yasakları (§5)** | `backend/MIMARI.md` |
| 2 | **YOL HARİTASI** — ne, hangi sırayla, hangi kapıyla | `belgeler/plan/DIMA-V1-YOL-HARITASI.md` 🔴 **repoda** |
| 3 | **BU DOSYA** — nasıl çalışılır | `OPERASYON.md` |
| 4 | **DURUM** — nerede kaldık | `OPERASYON-DURUM.md` |
| 5 | Kanıt / ölçümler | `~/.claude/plans/polymorphic-tumbling-riddle.md` |
| 6 | Ürün şartnamesi *(mimari otorite DEĞİL)* | `belgeler/urun/Dima-0-100-Gorev-Takip.md` |

> ⚠ **İSTİSNA:** Yol haritası FAZ −1'in `⟳ YÜRÜRLÜKTE` bloğunda listelenen `MIMARI.md`
> başlıklarında **yol haritası kazanır** — ve o işaret, ilgili madde indiğinde **silinip
> ölçümlü bir `✅` kaydına dönüşür**.

**Yol haritasının yedeği:** `~/.claude/plans/.yedek/` — belge **git altında değildir**,
her düzenlemeden **önce** zaman damgalı yedek alınır ve `md5sum` ile doğrulanır.

---

## 2 · 🔴 DÖNGÜNÜN ADIMLARI — her madde için, istisnasız

```
1. OKU      → yol haritasının İLGİLİ maddesini (ve atıf verdiği yerleri) yeniden oku
2. PLANLA   → terminale kapsamlı TO-DO bas: backend · sözleşme · frontend · kapı
3. ÖLÇ      → kusuru ÖNCE ölç (sayıyla, HEAD damgasıyla). Ölçülmemiş kusur düzeltilmez
4. GELİŞTİR → backend + sözleşme + frontend BİRLİKTE (yetim bırakma yasağı)
5. KAPI     → düzeltmeyi TESTE çevir; kapısız inen madde "bitti" DEĞİLDİR
6. DOĞRULA  → seviye 0 + `--hizli` YALNIZCA. 🔴 UZUN TEST BU ADIMDA KOŞMAZ
7. BELGELE  → MIMARI.md'yi AYNI commit'te güncelle (⟳ → ✅, ölçümle)
8. COMMIT   → açıklayıcı mesaj: kusur · kök neden · düzeltme · ölçüm
9. DURUM    → OPERASYON-DURUM.md'ye TEK SATIR ekle (tam tur demet sonunda)
10. → bir sonraki maddeye geç. DEMET KAPANDIYSA §3'ün demet kapanış listesini koş
```

🔴 **HER COMMIT'TE UZUN TEST KOŞMAZ.** `--tam` · `eval` · korpus · senaryo · Ajan C
bu döngünün **hiçbir adımında** yer almaz — hepsi **demet kapanışına** aittir (§3).
Madde başına doğrulama tavanı **~1 dakikadır**; aşıyorsa kural çiğneniyordur.

**Bir sonraki maddeye geçmek için izin İSTENMEZ.** Döngü v1 bitene kadar sürer.

---

## 2c · 🔴🔴 DÖNGÜNÜN SABİT DENETİM LİSTESİ — **her demet kapanışında, istisnasız**

> Aşağıdaki kalemler bir öneri listesi **değildir**. Döngü **her demet kapanışında**
> bunları **kontrol eder, denetler ve geliştirir**; hangisinin kıpırdadığı
> `OPERASYON-DURUM.md`'ye **sayıyla + HEAD damgasıyla** yazılır.
> 🔴 **Ölçülmemiş bir kapanış, kapanış değildir** — ve bir kalem *"geçersiz"*
> bulunursa **silinmez**, çürüten ölçümle işaretlenir (`MIMARI.md §10`).

### `T` · TABAN BORÇLARI — kaynak: [`belgeler/denetim/2026-08-10_TABAN-BORCLARI-ve-KATALOG-KOKU.md`](belgeler/denetim/2026-08-10_TABAN-BORCLARI-ve-KATALOG-KOKU.md)

> ✅ **ÇIKIŞ ÖLÇÜTÜ, o raporun `§6b` KONTROL LİSTESİDİR** — `A1…A11` (ölçüm altyapısı) ·
> `B1…B10` (taban) · `C1…C6` (sinonim) · `D1…D10` (bayrak fazları) · `E1…E3` (performans).
> 🔴 **`A` bölümü olmadan B/C/D'nin hiçbiri kanıtlanamaz.** Bir kalem ancak
> `OPERASYON-DURUM.md`'ye **sayı + HEAD damgasıyla** yazıldığında işaretlenir;
> *«iyileştirildi» diye işaretlenen bir kalem, işaretlenmemiş bir kalemdir.*

**Teşhis:** orkestratör bir **tavan** açtı, tabanı yükseltmedi. Tabanı `route()` +
**katalog** belirliyor; ölçülen sessiz-yanlışların kökü orkestratörde değil **katalogda**.

| # | borç | demet kapanışında sorulacak soru |
|---|---|---|
| **T-1** | **garson korpusu yok** — `eval --slice llm` **4 vaka**, `nl_corpus` `rule` sağlayıcıyla koşuyor (LLM **yok**). 🔴 **Payda CANLI ÇAĞRIYLA büyütülmez** (API tıkanır — kullanıcı kısıtı): canlı yanıt `--live --kaset` ile **bir kez** kaydedilir, sonraki koşumlar **diskten** → **koşum başına sıfır API**. ⚠ Kaset **kaliteyi değil tesisatı** ölçer; **curl döngüsü kaldırılmaz** (gerçeği o ölçer), kaset yalnız **gerilemeyi** durdurur | Bu turun `§`-kodlu canlı bulguları **kasete** çevrildi mi? Kaset (soru+istem sürümü) ile anahtarlı mı? |
| **T-0** | **katalog envanteri tek sayı vermiyor** (127 / 132 / 141 — üç yüzey, üç sayı) | envanter + kapı indi mi? Sayı hangi yüzeyden okundu? |
| **T-2** | **route'un kesinliği çürütülemez** — çok sahipli/dilbilgisiyle çakışan token'da çekilmiyor | bu turun eşleşmelerinden kaçı tek-sahiplilik kanıtı taşıyor? |
| **T-3** | **kanonik varlık ekseni yok** — «müşteri» **5 ad, 3 ayrık aile**; `blend` yapısal olarak kurulamıyor | `cekirdek/varlik_sozlugu` kararı alındı mı? |
| **T-4** | **çok sahipli ölçülerde sahip beyanı boş** (13 ad; `bakiye` vakası **₺11,86 milyon** sessiz seçim) | kaç kalem beyanlandı? |
| **T-5** | **yön beyanı eksik** — `lower_is_better` **125/173**'te yok; *«en kötü»* sessizce ters cevaplanıyor | oran düştü mü? Yeni ölçü kapısı var mı? |
| **T-6** | **ifade edilemezler** — `her <boyut>` (beyan var, yetenek yok) · `compare` hâlâ enum (`5.6` bloke) · mutfak **12** anahtar üretiyor, garsona **7** sunuluyor | yetenek envanteri kapısı indi mi? |
| **T-7** | **odak varlığı yok** — *«o makinede»* takibi üç yerleşimde de başarısız; eksik olan **bilgi**, kanca değil | diyalog durumuna odak varlığı girdi mi? |
| **T-8** | **ters yön — taşıyıcı YANLIŞ, fikir DOĞRU.** ⊙ Sinonim korpusunun **%55'i** (788/1432) elle yazılmamalıydı; kalan **B2 sınıfı** (`zayiat`↔`fire`, `iade`↔`şikâyet`) **LLM'in bilemeyeceği yerel sözleşmedir**. 🔴 **`prompt_enhancer` AÇILMAZ** — ikinci bir **seri** LLM turudur (`consistency_k=3` paralel koşar, yani Intent **tek tur**; enhancer **iki** yapar) ve gerçek dilde route **%93,3** pes ettiği için *"yalnız route boşsa"* bir güvence **değildir**. Bütçe: `llm` **20.000 ms**, Discovery **12.567 ms** → kullanıcı **iki kez** bekler 🟢 **Doğru biçim: AÇIK ÜRETİM değil KAPALI SEÇİM** — *«soruyu çevir»* değil, *«bu kelimenin katalogda karşılığı var mı, yoksa hiçbiri mi?»*. Girdisi **hazır**: `cube_router.partial_unknowns()` artakalan kelimeleri **deterministik** veriyor; `uncovered_words` kütükte **sıklık sıralı** birikiyor (`§M7` ile yeni düzeltildi). 🟢 **Bu yüzden sıcak yolda HİÇ koşmaz:** çevrimdışı, toplu, günde bir → aday kuyruğu → onay → overlay. Maliyet **soru başına değil kelime başına bir kez** | Çevrimdışı hasat koştu mu? `eslesen_terim` alanı Intent turuna girdi mi? ⚠ Çok eşleşen kelime kuyruğa **girmemeli** (o bir belirsizlik, `netlestirme_onceligi`'nin konusu); *«hiçbiri»* bir başarısızlık değil **menü boşluğu** sinyalidir. *(Enhancer'ın `on` olması bir hedef DEĞİLDİR)* |
| **T-9** | 🔴 **PLAN REDDİ — `plan_semasi`'de `operator` kelimesi SIFIR kez geçiyor.** Intent şeması operatörü **enum** olarak veriyor, plan istemi **hiç** vermiyor → model `equals` yazıyor, red yiyor, bir LLM turu harcanıyor. Süzgeç **biçimi** de (`dimension`/`operator`/`value`) plan isteminde yok → `dimension: None`. Onarım turu *"yanlış"*ı söylüyor, *"doğru"*yu söylemiyor — oysa çözüm aynı fonksiyonda `bilinen_boyutlar()` olarak **zaten var** | red oranı **sayılıyor mu** (`plan_garson.SAYAC` kapısız)? Sebep dağılımı yayımlandı mı? `ALAN_REHBERI` süzgeç bölümü indi mi? |

| **T-10/F** | 🔴🔴 **BAYRAK AÇMA FAZLARI PLANLANDI** — raporun `§4h`'i sekiz faz taşıyor. ⊙ En önemli bulgu: **ölçüm aleti zaten var** (`lab/nl_accuracy.py --ab <bayrak>` gerileme · `--ab-kurtarma` kazanç) → çoğu bayrak **haftalık değil saatlik** iş. Sıra: `F6` ucuz demet (`hizli_derin`·`hedef_kiyasi`·`tur_takip`·`tur_paylas` — ikisi **sıfır davranış değişikliği**) → `F2` `oylama_paydasi` → `F1` `varsayilan_donem` → `F7` `oylama_cekirdek` **kapı** (`beta` ama **0 test!**) → `F5` `tazelik` (**8 test/7 kod, kapalı — gerekçesi hiçbir yerde yazılı DEĞİL**) → `F3` netleştirme ikilisi + `T-4` → `F8` sağlayıcı → `F4` çekirdek + `T-3` | Bu turda hangi faz ilerledi? `F1`/`F2` korpusta **kayıp** gösterecek — `(a)/(b)/(c)` ayrımı yapıldı mı? |
| **T-10** | 🔴🔴 **49 BAYRAK, `on` OLAN SIFIR.** 21 `beta` · 28 `off` · **5'i `features.yml`'de bile yok** (`diyalog_bellegi`·`niyet_izi`·`sosyal_sinif`·`t2_anlatici`·`ayni_grain_gocu` → **hiçbir kiracı açamaz**). Ölçülmüş sorunlarımızı çözen kapalı yetenekler: **`varsayilan_donem`** (korpusun **%13,7'si** dönem netleştirmesi) · **`oylama_paydasi`** (*1 cevap + 2 «bilmiyorum» → uyum **%100** görünüyor*) · **`netlestirme_onceligi`** (`T-2`'nin çalışma-zamanı yarısı, **yazılmış**) · **`katalog_belirsizlik`** · **`cekirdek_katman`** (`T-3`'ün evi) · `tazelik` · `hedef_kiyasi` · `tur_takip`/`tur_paylas` | Bu turda hangi bayrak bir kademe ilerledi? İlerlemeyene **gerekçe** yazıldı mı? |

---

### 🔴🔴 `E` · BAYRAK GELİŞTİRME DOKTRİNİ — **kullanıcı emri, 2026-08-10**

> *"Bir özellik sorun çözecekse geliştirmesi emirdir; o bayrak `on` olana kadar devam
> edilir. Korpusla, kapıyla vazgeçmeyiz."*

| # | emir |
|---|---|
| **E-1** | Bir bayrak **ölçülmüş** bir sorunu çözüyorsa **geliştirmek EMİRDİR**. `off` bırakmak bir karar değil bir **erteleme**dir; ertelemenin sahibi ve gerekçesi olmak zorundadır. *Ödenmiş, testli, kapalı duran bir yetenek harcanmış emektir* |
| **E-2** | 🔴 **Hiçbir bayrak `nl_corpus` (rule) tek başına düştü diye REDDEDİLEMEZ.** Red üçlü ister: (1) korpus, (2) `--slice llm`/canlı, (3) düşüşün `(a)/(b)/(c)` ayrımı. Ayrım yoksa karar **verilmez** → `⊘` |
| **E-3** | `sessiz_yanlis` **mutlak vetodur**, korpus yüzdesi değildir. Kapsamı düşürüp `sessiz_yanlis`'ı düşüren bayrak **kazançtır** — *bir soruyu cevaplamamak, yanlış cevaplamaktan iyidir* |
| **E-4** | Her bayrağın yazılı bir **`on` ŞARTI** olmalı (`app/features.py`). Şartsız bayrak `beta`'da süresiz yaşar — bugün **21** bayrak öyle |
| **E-5** | LLM'li her kararda **iki koşum** (`KURAL G-1`). Ölçüldü: `prompt_enhancer` kararı tek koşumla verildi, **ikinci sağlayıcıda tersine döndü** |
| **E-6** | Rollout yüzeyi olmayan bayrak **yoktur**. *Bir kill-switch yalnız kodda varsa yarımdır* — **açma anahtarı** için de aynısı |
| **E-7** | Sıcak yola maliyet eklemek **ayrı bir karardır**: kalite ve gecikme **birlikte** raporlanır (`/ask` 47→177 ms, tavan kapısı yok) |
| 🔴🔴 **E-8** | **SICAK YOLA SERİ İKİNCİ LLM TURU EKLENEMEZ — ölçümle bile açılmaz.** Takas değil **sınır**. `consistency_k=3` örnekleri **paralel** koşar → Intent **tek turdur**; girdisi bir öncekinin çıktısı olan mekanizma **paralelleştirilemez**. Ölçüldü: `llm` bütçesi **20.000 ms** · Discovery **12.567 ms** · gerçek dilde route **%93,3** pes ediyor (yani *"yalnız route boşsa"* güvence değil). 🔴 Böyle bir bayrak `off` bırakılmaz, **YENİDEN TASARLANIR**: yetenek var olan turun **içine bir alan** olarak girer. ⚠ Aynı sınıf: `agent_plan_secimi` — `stats.py`'nin ölçümü *"kapalı dört LLM bayrağının gerekçesi **üç kez aynı cümle**: «sıcak yola LLM çağrısı ekliyor»"*. *Fikir doğruysa taşıyıcısı değişir, fikir atılmaz* |

### 🔴🔴 `K` · KORPUS BU KARARLARDA HAKEM DEĞİLDİR — **düşüş bazen BAŞARIDIR**

`nl_corpus` **`rule` sağlayıcıyla** koşar — **içinde hiç LLM yoktur**. Bir düşüş üç
ayrı olayın toplamıdır ve **ayrıştırılmadan karar verilemez**:

| | sebep | üretimdeki karşılığı |
|---|---|---|
| **(a)** | gerçek gerileme | 🔴 geri al |
| **(b)** | **route çekildi, tur garsona devredildi** | 🟢 **KAZANÇ** — üretimde orada gerçek bir LLM var ve doğru cevaplıyor; korpusta LLM olmadığı için **kayıp görünür** |
| **(c)** | **totolojik doğrular düştü** — korpus sorularının **≥%97,1'i katalog türevi**: soru da beklenen cevap da aynı kaynaktan. Route'un emin biçimde yanlış eşleştiği vaka **DOĞRU sayılabiliyor**; garsona geçince korpus düşer çünkü **sessiz-yanlış sayılmayı bırakır** | 🟢 **KAZANÇ** |

⊙ **Ödenmiş fatura:** `G3` korpus `%95,1→%93,5` dedi diye geri alındı; o `%1,6`'nın
**(a)** mı **(b)** mi olduğu **hiç sorulmadı** — mekanizma olarak **(b)** idi.
⊙ **Karşı örnek:** `§EB/A`'da korpus **haklıydı** — o bir **kapsam** değişikliğiydi ve
kapsamın ölçüsü korpustur; **yol dağılımının** ölçüsü değildir.

🔴 **Yapısal düzeltme — kapı çıktısı ikiye ayrılır:**
`route %X (n)` · `garson %Y (n)` · `devir %Z` · `sessiz_yanlış N`.
*Tek sayı iki yolun ortalamasıdır ve hangi yolun bozulduğunu gizler.*

### 🔴 `K-2` · KAPININ YETKİSİ DARALTILDI — *«20 dakika bize ne katıyor?»*

⊙ **Kapının bu operasyondaki gerçek hesabı:** `eval.run` **0** kırmızı · senaryolar
**0** · tam süit *"aynı kusurları seviye 1 de yakaladı"* · **korpus 2 gerçek yakalama**
(payda `445→342` iken doğruluğun `%93,2→%94,3` **çıkması**; `§EB/A`'da `sessiz_yanlis`
`12→18`) **ve 1 yanlış kırmızı** (`G3` — `(b)` sınıfı düşüş, üretimde kazançtı).

| korpus şunu ölçerken | yetkisi |
|---|---|
| **payda** *(kaç soru cevaplanabiliyor)* — bunu ondan başka **hiçbir şey görmüyor** | ✅ **VETO** |
| **`sessiz_yanlis`** | ✅ **VETO** (`E-3`) |
| **doğruluk %** *(kalite arttı mı)* | 🔴 **VETO YOK** — LLM'siz koşuyor, devir kayıp görünüyor, sorular **≥%97,1 katalog türevi** |

⚠ **Ve 13–20 dk'nın sebebi kapı DEĞİL ÜRÜN:** kapı `1:50 → 13:00` çıkarken payda
**+%38** büyüdü; yavaşlayan `/ask` (**47→177 ms**). Kapıyı kısaltmak yanlış hedef,
`P-2` (latency tavanı) doğru hedef.

🔨 **Eklenecek — KAPI DEFTERİ:** her koşumda *ne yakaladı / hangi kararı yanlış
verdirdi*. Bugün **2 haklı ↔ 1 haksız** ve bu tally **hiçbir yerde tutulmuyor**.
*Bir ölçüm aracının değeri kaç kez kırmızı verdiğiyle değil, kaç kez **haklı** kırmızı
verdiğiyle ölçülür.*

### 🔴🔴 `K-3` · YENİ KAPI DÜZENİ — **seyrek ve TEŞHİS EDİLEBİLİR** *(kullanıcı kararı, 2026-08-10)*

> *"Bu test mentalini değiştirebiliriz — çok fazla vakit kaybı. Tam kapı çok daha az
> sıklıkta ve **teşhis edilebilir** hâlde."*

**Gerekçe ölçülmüş:** kapı `1:50 → 13:00` çıktı ve sebebi **kapı değil ürün**
(`/ask` 47→177 ms); ayrıca korpusun doğruluk-yüzdesi ekseni zaten **veto yetkisini
kaybetti** (`K-2`). Yani en pahalı adım, en az güvenilir sayı için ödeniyordu.

| kademe | hangi soruya cevap verir | kapsam | süre | **ne zaman** |
|---|---|---|---|---|
| **0 · anlık** | *dokunduğum şey bozuldu mu* | hedefli `pytest` | 5–15 sn | her düzenlemeden sonra |
| **1 · hızlı** | *yakın çevre bozuldu mu* | `kapi.py --hizli --degisen` | 15–60 sn | geliştirme sırasında |
| 🟢 **2 · GARSON KORPUSU (kasetli)** — 🔴 **YENİ MERKEZ** | ***kalite*** — route **+** garson **+** devir **+** `sessiz_yanlis`, **tam `/ask` yolu** | kaset kümesi *(ilan edilmiş, sürümlenmiş payda)* | dk'lar · 🔴 **sıfır API** | **her tur/demet sonunda** |
| 🆕 **2b · NABIZ** | *felaket var mı* — şirket düştü mü, `sessiz_yanlis` fırladı mı | sabit tohumlu alt küme | ~2 dk | ~2 saatte bir |
| 🔵 **3 · ROUTE KORPUSU (tam payda, LLM'siz)** | ***kapsam*** — ~10.800 sorunun kaçı cevaplanabiliyor (`gitas`ı yakalayan tek şey) | tam korpus | 13–20 dk | 🔴 **DEĞİŞİKLİK TETİKLİ**: `cube_router` · katalog · `demo/packs/**` **+** günde 1 |
| 🟠 **C · CURL (canlı)** | ***gerçek*** — ürün ne yapıyor, insan yargısıyla | döngü kuralı | canlı API | **değişmez** |

🔴 **Neden garson korpusu merkeze alınabilir:** `/ask`'te **`route()` her zaman denenir**
(bayraktan bağımsız) — yani tam yoldan koşan bir garson korpusu **route'u da koşturur**
ve bugünkü LLM'siz korpusun ölçtüğü her şeyi **artı devri** ölçer. *Bugünkü korpus,
garson korpusunun LLM'i sökülmüş hâlidir.*

⚠ **Kasetin iki sınırı kapının parçasıdır:** (1) payda **kayıt kümesidir** — ilan
edilir, sürümlenir, *«korpus %»* demek **onun hakkı değildir**; (2) kaset **istem
sürümüne** bağlıdır — istem değişince (`§AR/Ö` gibi) **bayattır** ve küçük bir canlı
turla **yeniden kaydedilir**, yoksa kapı **eski kanıtla yeşil** verir.

🟢 Ve bu düzen `K-2`'yi **tamamlar**: doğruluk ekseni veto yetkisini LLM'siz koştuğu
için kaybetmişti; kasetli garson korpusunda **LLM var** → o eksen **yetkisini geri
kazanır**. *Bir sayıya güvenmemek onu atmak değil, ölçtüğü şeyi düzeltmektir.*

#### ⚠ *"Seyreltme yasağı"* ile ÇELİŞMEZ — ve ayrım önemlidir

Yasağın gerekçesi şuydu: `gitas` korpustan **kazara** düştü, payda `445→342` indi ve
doğruluk **yükseldi**. 🔴 **Günah seyreltmek değil, paydanın FARK EDİLMEDEN
değişmesiydi.**

| | payda | meşru mu |
|---|---|---|
| kazara düşen şirket | **değişken**, gizli | 🔴 hayır — kapının yakaladığı kusur budur |
| **sabit tohumlu, sürümlenmiş alt küme** | **sabit**, ilan edilmiş | ✅ evet |

🔴 **İki kademe iki AYRI sayı basar ve ikisi asla karşılaştırılmaz.** `NABIZ`
kendi tabanına göre okunur; *"korpus %"* demek **yalnız kademe 3'ün** hakkıdır.
`NABIZ` bir kapsam ölçüsü **değildir** — bir **felaket alarmıdır**.

#### 🔴 TEŞHİS EDİLEBİLİRLİK — bugünkü tek yüzde yerine

| bugün | olması gereken |
|---|---|
| `%94,3` | `route %X (n)` · `garson %Y (n)` · `devir %Z` · `sessiz_yanlış N` · **şirket başı payda** |
| *"düştü"* | 🔴 **DEĞİŞEN SORULARIN LİSTESİ** — yeşil→kırmızı **ve** kırmızı→yeşil, her biri route kararıyla |
| yorum insana kalır | 🟢 **her değişim otomatik etiketlenir** |

🔴🔴 **Ve `(a)/(b)` ayrımı ARTIK HESAPLANABİLİR — kural olmaktan çıkıp sayı olur:**
bir soru `source=cube` → `source=llm` diye değiştiyse bu bir **gerileme değil DEVİRdir**
`(b)`; `source` aynı kalıp sonuç bozulduysa **gerçek gerileme** `(a)`.
*`G3` tam olarak bu satırın yokluğu yüzünden geri alındı.* Rozet zaten kayıtlı —
yalnız **fark raporunda gösterilmiyor**.

*Bir ölçüm ancak neyin değiştiğini söylüyorsa karar aracıdır; yalnız bir sayı
veriyorsa bir kaygı kaynağıdır.*

---

🔴 **T-9 SIRADA T-1'DEN DE ÖNCEDİR:** dört adımının üçü mekanik (istem eki · mesaj
kuyruğu · eşleme tablosu), karar gerektirmiyor, ve bedeli **her red için bir LLM
çağrısı + gecikme** olarak *her gün* ödeniyor. ⚠ `plan_onarim.py`'nin kendi uyarısı
zaten bunu söylüyordu ve kimse okumamıştı: *"izde bir onarım sık görünüyorsa istem
(seviye 1) yetersiz demektir."*

🔴 **T-1 SIRADA BİRİNCİDİR ve gerekçesi ölçülmüştür:** garson yolunun paydası
kurulmadan, `T-2`'nin kazancı **okunamaz** — `G3` tam bu yüzden haksız yere geri alındı
(korpus `%95,1→%93,5` dedi; kaybın gerçek anlamı *"turu LLM'siz yedeğe devretmenin
maliyeti"*ydi).

### `P` · PERFORMANS — kaynak: [`belgeler/denetim/2026-08-09_KAPI-YAVASLAMASI-TESHISI.md`](belgeler/denetim/2026-08-09_KAPI-YAVASLAMASI-TESHISI.md)

⚠ **Bu rapor indekste *"DÖNGÜ KURALINA DAHİL"* yazılıydı ama bu dosyada hiç
geçmiyordu** — yani döngüye dahil **değildi**. *Bir belgeyi «döngüye dahil» ilan etmek,
onu döngüye koymak değildir.* Bağlandı:

| # | borç | demet kapanışında sorulacak soru |
|---|---|---|
| **P-1** | `/ask` **47 → 177 ms** (×3,8); kapı **1:50 → 13:00**. Sebep kapı değil **ürün** | bu demet gecikmeyi artırdı mı? |
| **P-2** | **latency tavanı kapısı YOK** — yavaşlama görünmedi çünkü ölçen kapı yoktu | kapı indi mi? |
| **P-3** | `cube_router`'da **sıfır** memoizasyon · sıcak yolda **41 yeni modül** | sıcak yola modül eklendi mi? |

---

## 3 · 🔴 TEST KAPISI — **YENİ POLİTİKA (kullanıcı kararı, 2026-08-04)**

> *"Kapı testlerini iptal edelim, sadece korpus koşsun — o da sadece en gerekli
> zamanlarda, sıklığı düşük, demet sonu gibi. Çok daha hızlı geliştirmeliyiz;
> fazları hızlıca ama mükemmelce tamamlamalıyız."*

**Yerel kapı dört adımdan tek adıma indi** (~15 dk → **1 dk 57 sn**, ölçüldü — aşağıdaki
düzeltmeye bak). Kaybedilen ağ **gecelik CI'ya** taşındı, **silinmedi**.

| Seviye | Komut | Ne zaman | Süre |
|---|---|---|---|
| **0 · anlık** | `pytest tests/test_<dokunulan>.py` | her düzenlemeden sonra | 5–15 sn |
| **1 · hızlı sinyal** | `python lab/kapi.py --hizli --degisen <dosyalar>` | geliştirme sırasında | ~15–60 sn |
| **2 · DEMET kapısı** | `python lab/kapi.py --tam` → 🔴 **YALNIZ KORPUS** | **demet sonu**, commit'lerden sonra, **TEK sefer** | **1 dk 57 sn** |
| **3 · gecelik CI** | `python lab/kapi.py --hepsi` *(korpus + süit + eval + senaryo)* | 🔴 **YEREL KOŞULMAZ** — `nightly.yml` koşar | ~15 dk |

### 🔴 NEDEN korpus KALDI, öteki üçü ÇIKTI — ölçüm

| Adım | Bu operasyonda kaç kez **kırmızı** verdi | Maliyeti |
|---|---|---|
| `eval.run` | **0** *(her koşum `+0,0 / +0,0 / +0,0`)* | ~1,5 dk |
| konuşma senaryoları | **0** *(dokuz sınıf tabanda sabit)* | ~1,5 dk |
| tam süit | birkaç kez — **aynı kusurları seviye 1 de yakaladı** | ~8,5 dk |
| **korpus** | 🔴 **1 kez — ve başka hiçbir şeyin göremeyeceği bir kusuru** | **1 dk 57 sn** |
> ⚠ **ÖLÇÜLDÜ — ve ilan edilen sayı yanlıştı (düzeltildi, 2026-08-04).** `--tam` **13 dk
> 18 sn** sürüyor, *"~3,5 dk"* değil (`docker inspect dima-k1`: `15:51:07 → 16:04:25`).
> O rakam, dört adımlı koşumun **içindeki** korpus dilimiydi — ve o dilim, süit çoktan
> compose ettiği için **ısınmış** bir sistemde ölçülmüştü. Tek başına koşan korpus
> compose + MDL derlemesini **kendisi** yapıyor.
>
> Duvar saatinin **%71'i tek şirkette**: `boyahane` **5306 soru / 8 dk 49 sn** (10 soru/sn);
> öteki üçünün **toplamı** ~3,5 dk (atiksan 1462/1'05" · gulteks 1618/1'16" · gitas 2479).
> Yani ilan edilen sayı, farkında olmadan *"boyahane hariç"* ölçümüydü.
>
> ⟳ **VE SONRA PARALELLEŞTİRİLDİ (ölçüldü, aynı gün):** `13 dk 18 sn → **1 dk 57 sn**`
> (`docker inspect dima-k3`: `17:05:04 → 17:07:01`). **Kapsamdan tek soru gitmedi** —
> doğrulandı: payda **445**, doğruluk **%93,1**, dört şirket de tabanda ya da üstünde,
> yani seri koşumun sayılarıyla **birebir aynı**. Hız, boşta duran çekirdeklerden alındı:
> kapı 20 çekirdekli makinede tek çekirdeği %91'de tutuyordu.
>
> 🔴 **Seyreltme YAPILMADI ve bu bilinçli:** korpusun bu operasyondaki **tek** yakalaması
> (`gitas` compose yarışı) payda **445 → 342'ye düşerken** doğruluğun **%93,2 → %94,3'e
> ÇIKMASIYDI**. Soru matrisini seyreltmek tam da paydayı değiştirmektir — *"sistem
> bozulurken sayı iyileşir"* kusurunu gören mekanizmayı, o kusura benzeyen bir işlemle
> ucuzlatmak olurdu. Seyreltme bir **kullanıcı kararıdır**; sayı burada dürüstçe duruyor.


O tek yakalama, kararın **tamamıdır**: `gitas` bir compose yarışıyla korpustan
**tamamen düştü**, payda **445 → 342** indi, doğruluk **%93,2 → %94,3'e ÇIKTI**.
Sistem bozulurken **sayı iyileşti**; süit · `eval` · senaryolar üçü de **yeşildi**,
çünkü hiçbiri *"kaç soru cevaplanabiliyor"* sorusunu sormuyor.
*Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla da olur.*

⚠ **Korpusun bilinen körlüğü yazılıdır:** soruları **katalogdan üretiliyor**, hepsi
**doğru yazılmış** — typo yolu korpusta **hiç sorulmuyor**. Yeşil bir korpus, kırık bir
kullanıcı deneyimini **DIŞLAMAZ**. O kusurlar canlı turlardan çıkar (aşağıda, Ajan C).

⚠ **Silinen bir şey YOK** (MIMARI §10: *"kapananlar işaretlenir, silinmez"*). Geri alma
tek bayrak: `--hepsi`.

### 🔴 COMMIT ≠ KAPI — demet disiplini *(ölçülerek benimsendi)*

**Ölçüldü:** bir turda FAZ 0'ın ~4 maddesi indi ve tam kapı **6 kez** koştu (~90 dk).
Ama sürenin **%75'i kapıda değildi**; madde başına koşan 10 adımlık döngüdeydi
(ölç → düzelt → kapı → MIMARI → commit → DURUM → denetim). Ve `--tam`'ın **dört
bileşeninin üçü** (`eval` · korpus · senaryo) o turda **hiç kıpırdamadı**, çünkü
onları besleyen dosyalara dokunulmamıştı.

**Karar:** *commit ucuzdur, kapı pahalıdır.* Geri alınabilirlik **commit'ten** gelir,
kapıdan değil — ikisini ayırmak **hiçbir güvenlik kaybettirmez**.
Her madde kendi commit'ini alır (seviye 0+1 ile); **tam kapı demet sonunda bir kez** koşar.

🔴 **RİSK SINIRI — demete GİRMEYEN maddeler.** Aşağıdakilere dokunan bir madde
**kendi tam kapısını hemen koşar** (demet beklemez), çünkü kapının üç sessiz bileşenini
besleyen yollar bunlardır:

```
app/cube_router.py · app/interpret.py · app/answer.py · app/followup.py
app/routers/ask.py · app/contribution.py · demo/packs/**   (katalog/metadata)
```

Belge · frontend · test-aracı · `lab/` maddeleri **serbestçe demetlenir**.

### 🔴 DEMET NE ZAMAN KAPANIR — üç sınırdan hangisi ÖNCE gelirse

| # | Sınır | Neden bu sınır |
|---|---|---|
| **D-a** | **6 madde** doldu | Kırmızı çıkarsa şüpheli küme 6 commit'le sınırlı — `git bisect` ucuz kalır |
| **D-b** | **Risk dosyasına** dokunuldu *(yukarıdaki liste)* | O madde demeti **hemen kapatır**; kapı onunla birlikte koşar |
| **D-c** | **~2 saat** geliştirme geçti | Kırmızıyı 6 saat sonra öğrenmek, 6 madde geri sarmak demektir |

**Demet kapanış listesi** *(sırayla, TEK sefer)*:
```
1. python lab/kapi.py --tam        → ~2 dk    KORPUS (yeşil değilse buradan çıkılmaz)
   ⤷ KIRMIZI ÇIKARSA: düzelt ve YALNIZ onu tekrar koş (zaten tek adım).
   ⤷ 🔴 "Bir de süiti koşayım" YASAK — o gecelik CI'nın işi (`--hepsi`).
      Yerel bir `--hepsi` koşumu, bu kararın TAM OLARAK iptal ettiği şeydir.
2. MIMARI.md + OPERASYON-DURUM.md  → demetin TAMAMI için tek pas, tek commit
3. git push                        → 🔴 ARTIK BİRİNCİ AĞ: süit·eval·senaryo YALNIZ
                                      orada koşuyor. Push ERTELENMEZ.
4. Ajan C canlı turu               → AŞAĞIDAKİ SIKLIKLA (her demette DEĞİL)
```

🔴 **`git push` artık isteğe bağlı değil.** Süit · `eval` · senaryo yerel kapıdan
çıktığı için tek koşum yerleri gecelik CI'dır; push edilmemiş bir demet, o üç adım
tarafından **hiç ölçülmemiş** demektir. *Ağı CI'ya taşımak, ancak kod CI'ya ulaşırsa
bir ağdır.*

### 🔴 AJAN C — canlı kullanıcı turu, sabit sıklıkla

C **pahalıdır** (~10 dk + LLM kotası) ama bu operasyonun **en verimli kusur kaynağıdır**:
*"değişim istendi, TOPLAM verildi"* · *"`bakiye` iki cube'ta, fark ₺11,86M"* · *"ham kolon
adı ekranda"* — üçünü de süit değil, **C** buldu. Bu yüzden azaltılır, **kaldırılmaz**.

| Demet türü | C koşar mı |
|---|---|
| Risk dosyasına dokunan demet *(D-b)* | ✅ **Zorunlu** — kullanıcıya dönen anlam değişti |
| Kullanıcı yüzeyi *(frontend · chip · `next_steps` · görünen ad)* değişen demet | ✅ **Zorunlu** |
| Yalnız belge · test-aracı · `lab/` demeti | ⛔ **Koşmaz** — ölçecek davranış yok |
| Yukarıdakilerin hiçbiri | **Her 2. demette bir** |
| **Faz sonu** | ✅ **Her hâlükârda zorunlu**, atlanamaz |

C atlandığında **gerekçesi `OPERASYON-DURUM.md`'ye yazılır** — sessiz atlama, *"koşuldu ve
temizdi"* gibi okunur. Atlama kaydı bunu imkânsız kılar.

**Bağlayıcı kurallar:**
* 🔴 **PLANSIZ KAPI YASAKTIR.** `--tam` · `eval` · korpus · senaryo · Ajan C **yalnız**
  `D-a` · `D-b` · `D-c` · faz sonu · **kırmızı doğrulama** anlarında koşar. Bu beş
  andan **herhangi biri dışında** koşturmak — *"bir de şuna bakayım"*, *"emin olayım"*,
  *"nasılsa değiştirdim"* — **kural ihlalidir**, iyi niyetli olması durumu değiştirmez.
  Ölçüldü: bu turda kaybedilen sürenin **çoğu** tam bu plansız tekrar koşumlardandı.
* 🔴🔴 **TESTİN TESTİ DE YASAKTIR — en çok kullanılan kaçamak budur.**
  *"Yeni bir kapı yazdım, çalışıyor mu diye tam süiti koşturayım"* · *"kapıyı kırmızıya
  düşürüp doğrulayacağım"* · *"kapının kapsamını göreyim"* — **hiçbiri** uzun koşum
  gerekçesi değildir. Kullanıcı kararı (2026-08-04): *"kapı testlerini çalıştığını
  kontrol etmek için sürekli uzun test koşuyorsun; bu da yasak. **Uzun test kesinlikle
  demet harici, ne sebeple olursa olsun yasak.**"*

  **Bir kapı nasıl doğrulanır (tek yol):**
  ```
  pytest tests/test_<yeni_kapi>.py        # saniyeler — TEK dosya
  # "önce ölç": kusuru geri koy → AYNI tek dosyayı koş → kırmızı gör → düzelt
  ```
  *"Önce ölç"* disiplini **korunur**, ama tam süitle değil **tek dosyayla** yapılır;
  kusuru geri koyup bir dosya koşmak ~3 saniyedir. Yeni kapının süitin geri kalanıyla
  etkileşimi **demet kapısında** ölçülür — orası zaten koşacak.
* **Gerekçe BEYAN EDİLİR.** Her `--tam` koşumu, yukarıdaki beş andan **hangisi** olduğunu
  söyleyerek başlar ve bu `OPERASYON-DURUM.md`'ye yazılır. Beyansız koşum plansız kapıdır.
  ⟳ **YÜRÜRLÜKTE değil:** kuralı araca gömecek `kapi.py --tam --neden <D-a|D-b|D-c|
  faz-sonu|kirmizi>` kapısı **henüz yazılmadı** — bugün kural yalnız belgede, yani
  unutulabilir. Araca gömülene kadar bu satır bir **niyet**, bir kapı değil.
* **Demet içinde ara `--tam` YOK.** *"Bir de şuna bakayım"* diye tam süit koşturulmaz.
* **Kapsam KIRPILMAZ.** Hız **tekrarı azaltarak** kazanılır, kapıyı gevşeterek değil.
* 🔴 **İki test konteyneri ASLA paralel koşmaz** (compose kilidi `metadata.yml`'de çakışır).
* 🔴 **Kapı konteyneri koşarken repoya YAZILMAZ** — mount canlıdır; bu turda iki sahte hata üretti.
* **Konteyner ADLANDIRILIR** (`--name`) ve bitmeden ikincisi açılmaz.
* `--hizli` bir **KAPI DEĞİL, SİNYALDİR** — kapsanmayan dosya sayısını kendisi yazar.
* 🔴 **Kapı `--rm` ile koşturulmaz, `-d` ile koşturulur.** Ölçüldü: `--rm` konteyner
  çıkınca kütüğü **siler** ve kabuk sarmalayıcısı ölürse özet **tamamen kaybolur** —
  bu turda iki koşum böyle kayboldu. Doğrusu: `docker run -d --name dima-kapi<N> …`,
  sonra `docker wait` + `docker logs`, en sonda `docker rm -f`.
* **İKİNCİ AĞ — CI.** `.github/workflows/backend-ci.yml` her push'ta `pytest -q` koşar
  ve `tests/test_eval_gate.py` süitin içindedir → **eval + süit kapıları CI'da ZATEN VAR**
  *(ölçüldü: `2/4`; eksik olan **korpus + senaryo**, `FAZ 0.15`'in gerçek kapsamı budur —
  sıfırdan kurulum DEĞİL, mevcut workflow'a iki aşama eklemek)*. Demet sonunda push →
  yerelde kaçan bir kırmızıyı CI **eşzamansız ve bedava** yakalar.

**Canlı ortam nasıl üretilir** *(anahtarlar repoda DEĞİL — çalışan servisten alınır):*
```bash
T=$(mktemp -d)
docker inspect dima-backend-core --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | grep -E "^DIMA_(LLM_PROVIDER|LLM_MODEL|ANTHROPIC|GEMINI|GROQ|XAI|OPENROUTER|OLLAMA)" > $T/llm.env
echo "DIMA_VQR_EMBEDDER=off" >> $T/llm.env      # embedder soğuk başlangıcı turu kilitler
docker run --rm --name dima_canli --env-file $T/llm.env -v "$PWD/backend:/app" -w /app \
  dima-test python lab/<arac>.py --live
```
⚠ `$T` **geçicidir ve repoya YAZILMAZ** — anahtar sızıntısı yasağı. Her canlı turdan önce
yeniden üretilir.

**Canlı test (LLM yolunu değiştiren her maddede):**
* `--live` **fail-closed**: gerçek üretici kurulmuyorsa **koşmaz**, sessizce `rule`'a düşmez.
* **Tur arası 5 sn** — ölçülen sınır **10 sn / 10 istek**; bir Intent turu `consistency_k=3` ile **üç** çağrı.
* Rapor başlığı **üreticinin adını** taşır.

---

## 4 · 🔴 MİMARİ KURALLAR — `KAT-1…KAT-5` *(yol haritası §A.5)*

| # | Kural |
|---|---|
| **KAT-1** | **Bir mekanizma iki iş yapmaz.** İki iş yapıyorsa ikiye ayrılır, her birinin **kendi kapısı** olur |
| **KAT-2** | **Cevapsız bir dal, cevaplı bir yolu KESEMEZ.** `source=None` dönen dal `return` etmez |
| **KAT-3** | **Bir katman, kendisini BESLEYEN katmandan önce inşa edilmez** (enabler ≺ tüketici) |
| **KAT-4** | **Kazanç ve gerileme FARKLI ALETLERLE ölçülür** |
| **KAT-5** | **SAYMA — KAPAT.** Kullanıcıya dönük anlam ekseni literal kümeyle tanımlanamaz; **kayıttan türetilir**, **bileşimseldir**, ya da `[SAYIM MUAF]` gerekçesiyle ilan edilir |

> **`KAT-5` bu operasyonun kalbi:** *"bir case veriyorum, bin açık çıkıyor"*un mekanik
> cevabı. **Vaka sayısı sonsuz; kapı sayısı sonlu.**

---

## 5 · 🔴 BELGE KURALLARI — `D1…D5` *(yol haritası §A.2)*

| # | Kural |
|---|---|
| **D1** | **`NE` üç parçalıdır**: backend · sözleşme · frontend. Frontend'i olmayan madde yalnız **`api-only`** beyanıyla geçer |
| **D2** | **Sayı, HEAD damgası ve yeniden ölçüm komutu olmadan yazılmaz**: `<sayı> @<sha> · <komut>` |
| **D3** | **Kanıtsız madde `[DOĞRULANMADI]` işaretlenir**, gizlenmez |
| **D4** | **Her yeni kalıcı artefakt bir MAKBUZA bağlanır** |
| **D5** | **Taşınan madde eski yerinde KÜTÜK bırakır** — istisnasız |

---

## 6 · 🔴 GELİŞTİRME DEĞİŞMEZLERİ — bu depoya özel

1. **Yetim bırakma yasağı.** Backend yeteneği **frontend tüketicisi olmadan "bitti" değildir**.
   Yeni sözleşme alanı → tüketicisi **aynı commit'te**. Yeni uç → çağıranı **aynı commit'te**.
2. **Yeni özellik yeni panel doğurmaz** (PK-1). Panel tavanı **13 export** — doludur.
3. **Kök neden, tikel yama değil** (ADR-0008). Kelime listesi büyütmek çözüm **değildir**.
4. **Aynı kuralın iki sahibi olmaz.** Bu deponun **bir numaralı kusur sınıfı**; kopya yerine
   **çağır**.
5. **Ölçüm aracının kendisi de bir bağımlılıktır** (§6.4). Bu oturumda araç **12+ kez**
   yanlış ölçtü. *Bir kapının doğru sonuç vermesi, doğru şeyi ölçtüğünü göstermez.*
6. **Beyan var, kod onu tanımıyor** — en sık kusur sınıfı. Beyan yazıldıysa **kapısı** olmalı.
7. **Sessiz kesme / sessiz kırpma YOK.** Bir şey yapılmadıysa **nedeni yazılır**.
8. **Üçüncü durum `⊘ ÖLÇÜLEMEDİ`** — ne geçti ne kaldı. Yeşile yuvarlamak *"risk yok"*
   yalanı üretir.
9. **KURAL A** (dondurulmuş taban) · **KURAL B** (her canlı-yol maddesine kill-switch;
   bayrak kapalıyken davranış **birebir bugünkü**, testle kilitli).
10. **Paylaşılan repo:** her git işleminden önce durum yeniden kontrol edilir; ana dizinde
    **asla** `checkout`/`stash` yapılmaz.

### 🔴 `K1…K8` — GARSON FAZININ BEDELİ ÖDENMİŞ SEKİZ KURALI *(2026-08-07)*

> Hepsi bu turda **gerçek bir kusurdan** doğdu; hiçbiri önlem değil **fatura**.
> Kaynak: `belgeler/denetim/2026-08-07_DIKKAT-EDILECEKLER.md §3` + üç denetim ajanının bulguları.

11. **`K1` · Ajan raporu İKİNCİ EL KANITTIR.** Üç ajanın 13 bulgusundan **biri yanlıştı**
    (`DA-6`); kodu okumadan uygulasaydım **çalışan bir meta-kapıyı sökmüş** olurdum.
    *Kodu okumadan uygulanan bir düzeltme, olmayan bir kusuru «düzelterek» gerçek bir
    kapıyı söker.*
12. **`K2` · `except Exception` YAZILMAMIŞ KODU DA GİZLER.** Bir `NameError` bir demet
    boyunca yutuldu ve iddia kapısı **şemasız** koştu. → Bir `except`'in kapsadığı çağrı
    testte **en az bir kez gerçekten** koşmalı (yapısal kapı: AST ile import denetimi).
13. **`K3` · Bir dilin derleyicisi koşulmuyorsa, o dilde yazılan her şey DENETİMSİZDİR.**
    `tsc` bu operasyonda **ilk kez** çağrıldı; frontend iki demettir derlenmiyordu ve
    Python süiti yeşildi. ⚠ Açık borç: `tsc` gecelik CI'da hâlâ koşmuyor.
14. **`K4` · Her cevapta dolu olan bir alan, bir AYRIM ÖLÇÜTÜ olamaz.** `kanit_sinifi`
    raporlanabilirlik kapısını totolojiye çevirmişti. *İki kusur üst üste bindiğinde,
    birini kapatmak ötekini bulur* — altından `soz` çıktı.
15. **`K5` · Bir alanın VAR OLMASI, taşınması demek değildir.** `G2`'nin bellek zinciri
    tamamen yazılmış ve testliydi; istemci tipinde **tek satır** eksikti ve `KURAL_DEVAM`
    üretimde **hiç ateşlenmedi**. Yetim kapısı da yeşil veriyordu (sınıf körlüğü):
    cevap alanı **okunur**, istek alanı **doldurulup gönderilir** — kanıt sınıfa göre değişir.
16. **`K6` · Bir satırı RAPORLAMAK, onu ölçmek değildir.** Ölçüm aleti on satır basıyor,
    dördünü hiç ölçmüyordu; `0|0|0` **başarısız** gibi okunuyordu. *Raporlanan ölçülmemiş
    bir satır, başarısız bir satırdan zararlıdır: sessizdir.*
17. **`K7` · Merkezî dosyaya dokunan DEMETİ KÜÇÜK TUT.** Bu turda dokuz kırmızı en sona
    kadar görünmedi. ⚠ Bu, `--hepsi`'yi **sıklaştırmak** demek DEĞİL — o yerelde koşulmaz
    (`CLAUDE.md`, ihlal edildi ve bedeli ~40 dk oldu). Doğru okuma: demeti küçük tut,
    sonunda **bir kez** ölç. *Bir kapıyı sona bırakmak onu teftişe çevirir; sık koşmak ise
    atlanan bir kapıya.*
18. **`K8` · Bir kill-switch YAML'de GÖRÜNMESİ yetmez, OKUNDUĞU ölçülmeli.**
    `diyalog_bellegi: on` → YAML bunu **boolean** okur, `resolve_for` elemez → bayrak
    **sessizce açık** kalır. Yani kapatmak için yazılmış madde kendi kusurunu üretti.
    → Geçerli aşamalar yalnız `off` · `alpha` · `beta` · `prod`; bayrak ayrıca
    `FLAG_REGISTRY`'de **adlandırılmış** olmalı.

---

## 7 · 🔴 ARKA PLAN DENETİMİ — üç ajan, her faz sonunda

> ✅ **Ajanlar bu operasyonun EN GÜÇLÜ YANI.** Bir ara *"arka plan ajanları ana sohbeti
> sildi"* teşhisiyle yasaklanmışlardı; **o teşhis yanlış çıktı** — olayı inceleyen kişi
> ölçtü: sebep başarısız bir **daemon yükseltmesiydi**, ajanlar değil. Yasak kaldırıldı.
>
> 🔴 **Dersi kayda geçiyor:** *teşhisin kendisi de kanıt ister.* Bir olay bir mekanizmayla
> **aynı anda** olduğu için o mekanizmanın suçlusu sayılamaz — bu depo tam bu sınıfı
> avlıyor (`A6`'nın düşme gerekçesi: *"kanıt cümlesi de kanıt ister"*), ve aynı hata
> **kural setinin kendisine** uygulandı: ölçülmemiş bir nedenle çalışan bir mekanizma
> kapatıldı.

Geliştirme **tek başına** yapılmaz. Her faz commit'inden sonra **paralel** üç ajan koşar;
raporları bir sonraki fazın **girdisidir**.

| Ajan | Sorusu | Çıktısı |
|---|---|---|
| **A · PLAN DENETÇİSİ** | *"Yol haritasının o maddesi **tam** uygulandı mı? `NE`'nin üç parçası (backend·sözleşme·frontend) da indi mi? `KAPI` gerçekten kuruldu mu?"* | Eksik kalem listesi + madde/satır atfı |
| **B · BÜTÜNLÜK DENETÇİSİ** | *"Yetim uç/alan doğdu mu? `KAT-1…KAT-5` çiğnendi mi? İkinci sahip doğdu mu? MIMARI güncel mi? Sayı beyanları bayat mı?"* | İhlal listesi + kanıt (dosya:satır) |
| **C · CANLI KULLANICI** | *"Gerçek bir kullanıcı gibi **tek tek** dene — toplu değil. Ne hissettim, nerede takıldım, ne anlaşılmadı?"* | Tur tur deneyim raporu + kırılma anları |

**Getirisi ölçüldü** — bu üç tur olmasa kaybedilecek olanlar:
* **A** → `§3.4-osi` tuzağının **yanlış-negatif** olduğu (faz indiğinde susacaktı)
* **B** → `raporlanabilir()`'in gövde alanlarını **sayması** (`KAT-5`) → `eylem_onerisi`,
  yani **onay kartı ekranda hiç yoktu** — üstelik kusur, o turda *"düzelttim"* denen
  kodun **içindeydi**
* **C** → aynı veriye **üç farklı yüzde** (`+%88` → `−%72 "iyileşti"` → `+%98`)

> 🔴 **C'nin kuralı:** **toplu koşum YAPMAZ.** İnsan gibi tek tek yazar, cevabı okur,
> ona göre bir sonrakini sorar. Rate limit: **tur arası 5 sn**.
> ⚠ **Konteyner:** C canlı tur için konteyner açar; o koşarken **ikinci test konteyneri
> açılmaz** (compose kilidi `metadata.yml`'de çakışır).

> ⚠ **Ajan raporu bir OTORİTE DEĞİLDİR.** İki kez düşük saydılar (14 ↔ gerçek 17 ·
> *"1/47"* ↔ gerçek 13). Kritik bir sayı **kendim ölçmeden** belgeye yazılmaz (§6/5).

**Denetim bulgusu = bir sonraki fazın girdisi.** Kritik bulgu varsa **sıradaki maddeden
önce** işlenir. Görev metinleri: **`OPERASYON-DENETIM.md`**.

---

## 8 · 🔴 BAĞLAM SIFIRLAMASINA KARŞI — üç katman

1. **`OPERASYON-DURUM.md`** — her faz sonunda güncellenir ve **commit edilir**:
   hangi faz · hangi madde · ne yapıldı · ne kaldı · bir sonraki adım · açık borçlar.
2. **`backend/CLAUDE.md`** — bu dosyalara **işaret eder** (her oturumda otomatik yüklenir).
3. **Kalıcı bellek** — `project_dima_v1_operasyon.md` (yol + kural seti + durum dosyası yolu).

> **Test:** bağlam tamamen silinse, `OPERASYON.md` + `OPERASYON-DURUM.md` + yol haritası
> okunarak **kaldığı yerden** devam edilebilmeli. Bu üçü yeterli değilse eksiklik burada
> giderilir.

---

## 9 · COMMIT DİSİPLİNİ

**Mesaj yapısı:**
```
<tip>(<faz>.<madde>): <tek cümle — NE düzeldi>

ÖLÇÜLEN KUSUR: <sayıyla, komutla>
KÖK NEDEN:     <sınıfı — tikel değil>
DÜZELTME:      <backend · sözleşme · frontend>
KAPI:          <test dosyası::test adı>
ÖLÇÜM:         <önce → sonra · eval · korpus · tsc>
```
* Claude footer **KULLANILMAZ** (saka standardı).
* `MIMARI.md` güncellemesi **aynı commit'te**.
* Faz sonu commit'i **tam kapı yeşil** olmadan atılmaz.

---

## 10 · SIRA — v1 yolu

```
FAZ −2  ✅ BİTTİ (belge onarımı: §G.6f · v2 kilidi · FAZ 0 sırası · 6.0 · Bölüm II borcu · VK-5)
FAZ −1     MIMARI ön hazırlığı (kod yok)
FAZ  0     25 madde — BAĞLAYICI KOŞUM SIRASI yol haritasında yazılı:
           0.22+0.2+0.23 → 0.1 → 0.16 → 0.14 → 0.19 → 0.18 → 0.4/0.5/0.5b → kalan → 0.21
FAZ  1     GÜVENCE (motor-RLS · yetki granülerliği · tazelik)
FAZ  2     SEMANTİK ÇEKİRDEK (hakem — en yüksek etki)
FAZ  3     KAPSAM (sahiplik turu · R1'i kapat)
FAZ  4     ÖLÇÜM ve KANIT
FAZ  5     KONUŞMA ve DENEYİM
FAZ  6     AGENTIC ve ONAYLI YAZMA (6.0 = D9 geri alma ÖNCE)
FAZ  7     ARAYÜZ
FAZ  8     AÇILMA (8.1 kod değil, takvim penceresi — FAZ 1'den sonra AÇILIR)
§G         AJAN KATMANI — v1'e PARALEL, ona bağımlı değil
```

⚠ **Kalan 10 belge kusuru** (sayı çelişkileri · 4 ölü bayrak · `II-D.1b` · iki biçim
hatası · FAZ 7 kapsamı) **ayrı tur açılmadan**, ilgili faza gelindiğinde düzeltilir.

---

## 10b · 🔴 SIRADAKİ FAZ — ŞEMA BUDAMASI *(`B1…B6`, tasarım hazır)*

> **Tasarım `belgeler/denetim/2026-08-07_DIKKAT-EDILECEKLER.md §4`'te** — dört ölçümle yazıldı. Buraya **kopyalanmaz**
> (`D1`: kaynağı güncelle, kopyalama); buraya giren yalnız **bağlayıcı sıra ve şartlar**.

### Neden bu faz

Ölçüldü (23 cube'luk demo): intent yolunun katalog metni **4.038 token**, Discovery şema
prompt'u **16.767 token**, ve `oneOf` şeması **10.038 token** — sonuncusu üretilip
**atılıyordu** (`B5` ✅ kapandı: sağlayıcı artık `sema_kullanir` ile yeteneğini beyan
ediyor). Kalan iki kalem **hiç ele alınmadı**; planın kendisi budamadan **söz etmiyor**
(`P3`).

⚠ Bu **23 cube**'luk bir demo. 100 cube'lu bir müşteride sayı ~4 katına çıkar.

### 🔴 ÖLÇÜLDÜ — VE TASARIM DOĞRU NÜFUSTA ÇÖKTÜ *(2026-08-07)*

> Aşağıdaki üç ön koşul yazıldıktan **sonra** doğru nüfusta ölçüm yapıldı ve sonuç
> tasarımı **çürüttü**. Bu bölüm o ölçümü taşır; ön koşullar altta **kayıt için** duruyor.

**Nüfus düzeltmesi — iki bağımsız ajan da yanılmıştı.** *"Etiketli route-başarısızlık
vakası **2**"* deniyordu; ikisi de yalnız **elle yazılmış** 42 vakaya bakmış.
`lab/senaryo_uretec.py:863` her üretilen soruya **`"cube": cad`** yazıyor ve
`gercek_dunya.py:509`'daki `setdefault` onu **ezmiyor**:

| küme | toplam | etiketli | **etiketli ∧ `route()=None`** |
|---|---|---|---|
| elle (`VAKALAR`) | 42 | 2 | 2 |
| **üreteç** | 2 270 | **2 270** | 🔴 **2 116** |

Yani korpus **zaten vardı**. Bu, bu fazın tekrar eden sınıfının **tersi**: *"beyan var,
karşılığı yok"* değil — **karşılık var, beyan yok**.

**Ve o nüfusta ölçülen recall** *(n=2 116, katalog 23 cube)*:

| tasarım | recall | 🔴 KAYIP | fail-open | tasarruf |
|---|---|---|---|---|
| `ilgili_cubelar` | %78,1 | **464** | 599 | %60,7 |
| `measure_cube_candidates` | %100 | 0 | **2 116 (hepsi)** | **%0** |
| 🔴 **birleşim + fail-open** | **%78,1** | **464** | 599 | %60,7 |

🔴 **Birleşim `ilgili_cubelar`'a ÇÖKÜYOR.** Sebep yapısal: bu sorular `route()`'un pes
ettiği dağınık ifadeler ve içlerinde **tanınan bir ölçü adı yok** — dolayısıyla ölçü
sinyali **2 116'nın 2 116'sında** boş dönüyor. *İki eksenden bakan bir tasarım, ikinci
eksenin hiç veri görmediği bir nüfusta tek eksenlidir.*

⚠ **Ve fail-open kurtarmıyor:** 464 kayıp **boş seçimden** değil, **dolu ama yanlış**
seçimden geliyor. Fail-open yalnız boşlukta devreye girer; yanlış menü sessizce gider.

#### Önceki ölçüm neden %100 demişti — ve dersi

Dış tasarım *"birleşim %100 · 0 kayıp"* ölçmüştü. O ölçüm `route()`'un **başarılı olduğu**
sorularda yapıldı — ve orada ölçü adı **zaten tanınır**, çünkü `route()` tam da onu
tanıdığı için başarılıdır. **Ölçüm, ölçtüğü şeyin varlık koşulunu içeriyordu.**

*Bir ölçümün sayısı değil, hangi nüfustan geldiği karar verir.*

#### 🔴 KARAR: budama bu tasarımla İNMEZ

`B1`/`B3` **askıya alındı**. Yeni sinyal gerekiyor — aday eksenler *(hiçbiri ölçülmedi)*:
gövde/kök eşleşmesi · `value_index` üzerinden **değer** sinyali · gömme (embedding)
benzerliği. Her biri **aynı nüfusta** ölçülmeden yazılmaz.

⊙ Kalan geçerli kalemler: `B5` ✅ (indi) · `B2` *(aşağıda, metni düzeltildi)* · `B6`.

---

### ÖN KOŞULLAR *(kayıt için — ilki ölçümle düzeltildi)*

1. ~~**Etiketli route-BAŞARISIZLIK korpusu (~100 vaka); bugün elde 2 var.**~~
   🔴 **YANLIŞ ÇIKTI.** Korpus **var**: 2 116 etiketli + `route()=None` vaka. İş
   **üretmek** değil **ayıklamak**: üreteç `kabul` beklentisi de taşıyor, bazı vakalarda
   doğru cevap **netleştirmedir** — temiz yer gerçeği bir **alt kümedir** ve o ayrım
   yapılmalı. Ayrıca `lab/nl_accuracy.py:354` `ab_kurtarma_kos()` **zaten** `route()`
   pes ettiğinde LLM'i yer gerçeğiyle ölçüyor (`REAL_PHRASINGS`, ~43 doğal ifade) —
   sıfırdan bir alet **yazılmaz**, o genişletilir. *İkinci bir sahip yaratmak, ölçüm
   aracında en pahalı hatadır.*
2. **Bayrak + FAIL-OPEN.** `sema_budama: alpha`; seçim **boş** dönerse **tam katalog**.
   Ölçüldü: yalnız `ilgili_cubelar` ile budama vakaların **%13,4'ünde doğru cube'u
   DÜŞÜRÜYOR** — bazılarında boş dönüyor. Doğru cube budanırsa LLM **yanlış menüyü**
   görür ve **sessiz-yanlış** üretir: bu deponun en pahalı hata sınıfı.
3. **`KURAL G-1`** — canlı sağlayıcıyla **iki koşum**; ayrışırsa karar yok (`⊘`).

### Tasarım kararı — tek sinyal DEĞİL, BİRLEŞİM

`ilgili_cubelar` (cube kimliği **ve boyut** sinonimleri) ∪ `measure_cube_candidates`
(**ölçü** sinonimleri). Üç bağımsız kümede ölçüldü: birleşim **%100 recall · 0 kayıp ·
%83–88 tasarruf**; tek sinyaller sırasıyla %95,8 (15 kayıp) ve %89,7 (37 kayıp).
*İki sinyal farklı eksenlerden bakıyor; birini seçmek ötekinin gördüğünü kör etmektir.*

### Sıra ve kapıları

| adım | ne | kapı |
|---|---|---|
| `B1` | `budanmis_index(q, schema)` — **saf fonksiyon**, birleşim + fail-open | birim test: üç küme, **recall %100** |
| `B2` | Etiketli route-başarısızlık korpusu (~100 vaka) | `test_budama_recall.py` — **kayıp 0** şartı |
| `B3` | `ask.py`'de **bayrak arkasında** bağla | korpus gerilemesin · `sessiz_yanlis` **artmasın** |
| `B4` | Token ölçümü: gerçek çağrıda önce/sonra | `lab/` raporu — **beyan değil SAYI** |
| `B5` | ✅ **KAPANDI** — boşuna üretilen `oneOf` şeması | `test_sema_kisitli.py` |
| `B6` | Prompt caching — **üç katmanlı önek** | ⚠ aşağıdaki gerilim |

🔴 **`B6`'nın gerilimi yazılı olsun:** budama her sorguda **farklı** önek üretir, caching
**sabit** önek ister. İkisi *"iki kaldıraç"* diye **toplanamaz** — kısmen birbirini iptal
eder. Çözüm katmanlamadır: sabit kurallar · **yarı-sabit tenant kataloğu (BUDANMAZ)** ·
değişken soru. Budama **değişken** katmanda kalır.

---

## 10c · 🔴 BEŞ KÖŞE VAKASI — dış öneri, **kodla sınandı** *(2026-08-07)*

> Sistemi tanımayan bir danışman beş teknik köşe vakası önerdi. Beşi de **koda karşı
> doğrulandı** (`K1`: dış rapor ikinci el kanıttır). Sonuç: **ikisi kabul, ikisi zaten
> var ama bir borcu ortaya çıkardı, biri reddedildi.**

### ✅ `Ö1` KABUL — Akış, **cümle-tamponlu** olmak zorunda *(gelecek faz kısıtı)*

Öneri: SSE metni token token akıtırsa, `narration_guard`/`iddia.py` **cümle
tamamlandıktan sonra** karar verdiği için düşen bir cümle **ekranda çoktan görünmüş**
olur.

⊙ Doğrulandı: bugün SSE **metin akıtmıyor** — `ask.py`'nin üreticisi yalnız `adim` (iz)
olayları ve sonda **tek parça** `tamam` yayınlıyor. Yani risk **bugün yok**, ama akış
maddesi (`S`) indiği gün **yapısal olarak** doğar: fail-closed bir kapı, çıktısı çoktan
gönderilmiş bir cümleyi geri alamaz.

🔴 **Bağlayıcı kısıt, şimdiden yazılı:** anlatı akışı **cümle tamponlu** olur. Metin
cümle sınırına kadar tamponda birikir, `narration_guard` + `iddia.py`'den geçer, **sonra**
blok hâlinde akar. Düşen cümle istemciye **hiç** ulaşmaz.
*Bir kapıyı geri alınamaz bir kanalın arkasına koymak, o kapıyı kaldırmaktır.*

### ◐ `Ö2` ZATEN VAR — ama işaret ettiği kayıp **ÖLÇÜLMÜŞ ve AÇIK**

Öneri: sohbet geçmişi 2 turla sınırlıyken **kümülatif CubeQuery**'yi uzun ömürlü taşı.

⊙ Doğrulandı: **tam olarak bunu yapıyoruz.** `context.py:185` ham metin penceresini
`(history or [])[-2:]` ile sınırlıyor; `cube_query` ise **ayrı ve yapısal** olarak her
turda yankılanıyor (`ask.py:1569`), `deterministic_refine(prev, …)` de düzenlemeyi
**önceki sorgunun üstüne** uyguluyor. Yani mekanizma mevcut.

🔴 **Ama önerinin işaret ettiği KAYIP gerçek ve bizde ÖLÇÜLMÜŞ:** `lab/sharding.py`,
44 konuşmalık sabit kohortta **tur 1 %63,6 → tur 5 %45,5 = −%18,2** (hedef −%10).
Yani kümülatif taşıma **var** ama çok-turlu derinleşmede yine bozuluyor.
*Bir mekanizmanın var olması, işini yaptığının kanıtı değildir.*
→ Borç: çok-turlu bozulma (`FAZ 4.3`'ün ölçülmüş borcu) — sahibi atanmalı.

### ✅ `Ö3` KABUL — kaçış kapısı **zaten config'de**, ölçüm eşiği yazıldı

Öneri: tek büyük model Eksen 1'de (Intent-JSON) yüksek TTFT üretebilir; Eksen 1 için
küçük bir model **B planı** olarak yedekte dursun.

⊙ Doğrulandı: `config.py:96` `openrouter_select_model: str = ""` — **kaldıraç var**,
yalnız boş. Yani B planı bir **kod işi değil, bir env satırı**.

⊙ Ve ölçüm önemsiz değil: bu turda canlı kapıda **ilk çağrı 33,7 sn**, sonrakiler
**~1,4 sn** (önbellek ısınıyor). Yani sıcak p95 önerinin eşiğinin (**1,5 sn**) tam
sınırında, **soğuk başlangıç** ise onun çok ötesinde.

🔴 **Kural:** Eksen 1 p95 > **1,5 sn** ölçülürse `openrouter_select_model` doldurulur —
mimari değişmez, yalnız o alan yazılır. ⚠ Kullanıcı kararı *"tek model"*di; bu kaldıraç
o kararı **değiştirmez**, ölçüm onu gerektirirse diye **görünür** durur.

### ⊘ `Ö4` REDDEDİLDİ — ikinci sahip yaratırdı

Öneri: `garson.py`'nin 15 ifadesinden **150+ sentetik varyasyon** üretilip ayrı bir
küme (`garson_variations.json`) olarak stress-test edilsin.

🔴 Reddin gerekçesi aletin **kendi docstring'inde** yazılı: *"§5/2 «kendi diliyle sipariş
alır» bilinçle DIŞARIDA: onu `lab/gercek_dunya.py` persona×zorluk matrisiyle **zaten
ölçüyor** — ikinci bir sahip yaratmayız."* O araç bugün **2 312 vaka** koşuyor ve dağınık
/ yazım hatalı ifadeleri içeriyor. İkinci bir varyasyon kümesi, bu deponun bir numaralı
kusur sınıfını (*aynı kuralın iki sahibi*) doğrudan üretirdi.

⚠ **Ama önerinin bir yarısı gerçek bir boşluğa değiyor ve kayda geçer:**
`gercek_dunya.py` **tek turlu** ve yalnız `route()`'u ölçüyor; `garson.py` çok turlu ama
yalnız **6 senaryo / 16 tur**. Yani *"aynı isteği farklı biçimde, ÇOK TURLU sor"* ekseni
hiçbir alette yok. Genişletilecekse **`garson.py` içinde** genişletilir, yeni bir küme
açılmaz — ve kullanıcının bağlayıcı sınırı geçerlidir: *"testleri yığma, 10-20 istek bile
akıllıca yapılırsa yeterli."*

### ✅ `Ö5` KABUL — **en değerli öneri**; kapının kendi sözü tutulmamış

Öneri: model/prompt değişirse guard'lar **sessizce** tüm anlatıyı düşürmeye başlayabilir;
kullanıcı yanlış sayı görmez (güvenli) ama sistem sürekli *"soğuk"* cevap verir ve
**kimse fark etmez**. → Son N istekte düşme oranı eşiği aşarsa **alarm**.

⊙ Doğrulandı: agrege düşme oranı **hiçbir yerde ölçülmüyor** (`grep dusme_orani|drop_rate`
→ **0**). Tek tek loglar var, makbuzda tek cevaplık sayı var — **oran yok**.

🔴 Ve bu, `app/iddia.py`'nin **kendi docstring'inin** sözüdür: *"düşme oranı **ölçülür** —
kapı agresifse gevşetilir, ama **ölçüyle**, sezgiyle değil."* Söz yazıldı, ölçüm
kurulmadı. *Bir kapının sessizce her şeyi düşürmesi, hiç olmamasından farksızdır — tek
fark, sistemin kendini güvende sanmasıdır.*

→ Faz maddesi: `interaction_log` üzerinden **kayan pencere** düşme oranı + eşik uyarısı.
⚠ Eşik **ölçümle** konur (bugün taban bilinmiyor); önerinin **%30**'u bir başlangıç
tahminidir, bir karar değil.

---

## 11 · DURMA ŞARTLARI — sadece bunlar

Döngü **v1 bitene kadar** sürer. Yalnız şu üç durumda durulur ve sorulur:

1. **Geri alınamaz / dışa dönük** bir işlem gerekiyorsa (push · dış servis · veri silme).
2. **Alan bilgisi kararı** gerekiyorsa (ör. FAZ 3.1 sahiplik turu: *hangi cube `bakiye`'nin
   sahibi* — bu mühendislik değil **iş** kararıdır).
3. **Ölçüm, planın bir varsayımını çürütüyorsa** — plan değişikliği kullanıcının kararıdır.

*Bunların dışında izin istenmez.*
