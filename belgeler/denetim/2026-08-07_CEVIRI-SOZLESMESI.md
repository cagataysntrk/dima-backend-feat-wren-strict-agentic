# ÇEVİRİ SÖZLEŞMESİ — *"LLM anlıyor; SÖYLEYEMİYOR"*

> **Sorular:** (1) LLM ile sistem diline çeviri neden başarılı değil — sistem dili mi net
> değil, neyin ne yaptığı mı karışık? (2) Kesin olanda deterministik, şüphede LLM — bu
> nasıl birleşir?
>
> **Kapsam:** araştırma + rapor. Bu belgede **kod değişikliği önerilir, yapılmaz.**
> Her sayı bu depoda yerinde ölçüldü; kaynağı satır numarasıyla yazılı.

---

## 0 · ÜÇ CÜMLELİK CEVAP

1. **Sistem dili net.** Karışıklık çevirinin **sözleşmesinde**: mutfak on iki şey
   pişirebiliyor, garsonun sipariş fişinde **yedi** satır var.
2. **İstenen merdiven zaten kurulu** (`VQR → route() → LLM → Discovery`) — eksik olan
   mimari değil, `route()`'un *"eminim"* kararının **kalibrasyonu**.
3. Ve bir yerde *neyin ne yaptığı* **gerçekten karışık**: sorgunun sahibi LLM, ama
   *"kullanıcı ne istedi"* iddiasının sahibi **deterministik** katman.

---

---

## 0 · 🔴 ÇALIŞMA KURALLARI — BAĞLAYICI (bu belgenin sözleşmesi)

> Bu bölüm belgenin **başında** durur çünkü geri kalan her ölçüm ona dayanır. Bağlam
> sıfırlansa bile buradan devam edilir.

### 0.0 · 🔴🔴 EN ÜST KURAL — **GARSON DEVRİ** *(kullanıcı kararı 2026-08-08)*

> *"Route hatalarını düzeltmeye kalksak sonsuza kadar sürer ve route'a — yani NLP'ye —
> Türkçe öğretmemiz gerekir ki bu gereksiz. NLP bizim için güvenilir olmayan bir araç;
> sadece **kesin doğrulukla** sonuç getirirse cevabına güveniyoruz. Biliyorsun ki
> çoğunlukla hata yapıyor, anlamıyor — **anlama yok zaten**, sadece kelimeleri
> kurallamaktan ibaret.*
>
> *O yüzden intent algılamada asıl **LLM'e** güveniyoruz: tam bir dil modeli ve gerçekten
> bir sözü anlıyor — ister Türkçe ister Arapça, kullanıcı **ne'ce** yazarsa yazsın.*
>
> *Bu turun asıl amacı: siparişte **en ufak %5'lik bir şüphe** bile varsa, azıcık bile
> anlamama varsa, **hemen LLM çalışsın, garson gitsin siparişi düzgün alsın**. Asıl
> güvendiğimiz hakem devreye girsin."*

#### Üç rol — ve ikisi ASLA karıştırılmaz

| rol | kim | ne yapar | tutum |
|---|---|---|---|
| 🗣 **GARSON** | **Intent LLM** (`select_cube` → Intent-JSON) | Kullanıcının sözünü **sistem diline çevirir** — küp · ölçü · boyut · dönem | ✅ **ASIL GÜVENDİĞİMİZ HAKEM** |
| 🍳 **AŞÇI** | küpler + `route()` | Yemeği **kendisi** yapar; sayıyı **her zaman** o koyar | ✅ Mutfakta LLM'e hiç güvenmiyoruz |
| 🥡 **YAN DÜKKÂN** | **Discovery LLM** (ham SQL) | Aşçının yapamadığını dışarıdan sipariş eder | ⚠ İstemediğimiz son çare |

🔴 **BU TURLARIN KONUSU GARSONDUR. DISCOVERY DEĞİL.**

#### Kural

> Müşteri aşçıya bağırdı. Aşçı **kesinlikle** duyduysa (NLP %100 anladıysa) hemen yapar.
> **En ufak anlamama varsa garson gider, siparişi düzgün alır.**

**Devir tetikleyicileri — herhangi biri yeterlidir:**
kısmi kapsam · bilinmeyen token · belirsiz eşleşme · yazım şüphesi · morfolojik ıskalama ·
çapraz-konu şüphesi · **ve *"anlayamadım"* üretecek her dal**.

🔴 **KULLANICI ASLA CEVAPSIZ KALMAZ.** *"…kısmını anlayamadım"* bir **son cevap
olamaz** — garsona sorulmadan o cümle yayımlanmaz.

#### Bu belgenin kendi turları bu kuralı ihlal etti

`§32` (fiil çekimi) · `§42` (`yarı` sınıfı) · `§45` (ek + ünsüz yumuşaması) · `§43`
(`dağılım` sözcüğü) — **dördü de route'a Türkçe öğretme** işiydi. Hiçbirinin yamanması
gerekmiyordu: dördü de garsona gitseydi **ilk turda** doğru cevap gelirdi.

⊙ Ve ölçüt bunu zaten gösteriyordu: `şubattan ocağa` yumuşaması route'ta bilinmiyor →
route'a öğretmek yerine **devretmek** gerekirdi. Kullanıcı İngilizce/Arapça yazsa route
**tamamen** çaresizdir; garson için fark etmez.

> *Bir dili kurallarla yakalamaya çalışmak, ufka doğru yürümektir; dili bilen birine
> sormak ise bir adımdır.*

#### 🔴 İKİ EKSEN — ve aralarındaki TEŞHİS KURALI

Geliştirme **iki** eksende yürür ve **karıştırılmaz**:

| # | eksen | hedef | araç |
|---|---|---|---|
| **1** | 🗣 **SİPARİŞ ALMA** | Kullanıcı **ne'ce** yazarsa yazsın niyet doğru alınsın. **«Anlamadım» YOK** — Arapça bile yazılsa. | **Garson LLM** *(hakem, güvendiğimiz)* |
| **2** | 🍳 **MUTFAK** | Küpler **her yemeği** sunabilsin; Discovery'ye hiç düşülmesin. | Küp / semantik katman geliştirme |

> **Teşhis kuralı:** *"Garson devreye girdi ve sisteme sorunsuz, doğru bir girdi sağladı —
> ama yine çalışmadıysa, sorun küplerde, **mutfaktadır**. O zaman mutfağı geliştiririz."*

| gözlem | eksen | doğru iş |
|---|---|---|
| niyet yanlış/eksik alındı · *"anlayamadım"* · yabancı dil | **1 · sipariş** | garsona **devret** — route'a dil öğretme |
| niyet **doğru** ama küp o soruyu karşılayamıyor | **2 · mutfak** | küpü / ölçüyü / boyutu **geliştir** |
| `source=llm:*` ya da `cube=adhoc` görüldü | **2 · mutfak eksiği** | 🔴 bir çözüm değil, bir **arıza raporu** |

🔴 **Discovery'nin her ateşlenmesi bir MUTFAK EKSİKLİĞİ RAPORUDUR.** Onu bir yol değil bir
**ölçü** olarak okuyun: hangi yemeği yapamadığımızı söyler. Hedef, oranını **sıfıra**
yaklaştırmaktır.

⚠ **İki LLM'in güven derecesi ZITTIR ve bu bilinçlidir:** birincisi (**garson**) *asıl
güvendiğimiz hakem*; ikincisi (**Discovery**) *hiç güvenmediğimiz*. Aynı teknolojinin iki
role konması bir çelişki değil bir **iş bölümüdür**: biri **anlar**, öteki **uydurabilir**.

> *Bir siparişi yanlış almakla, doğru alıp yapamamak aynı kusur değildir — ve aynı yerde
> düzeltilmezler.*

#### Sınırlar — kural neyi BOZMAZ

* ⚠ **Garson yalnız ÇEVİRİR.** Sayıyı yine küp koyar; guard'lar · beyanlar · doğruluk
  vetosu **aynen** yürürlükte. Garson bir **cevap** değil bir **sipariş** üretir.
* ⚠ Devir bir **bayrakla** kapatılabilir olmalı; kapalıyken davranış bugünküyle birebir
  (`KURAL B`).
* ⚠ Uygulanabilmesi için `route()`'un **derece** kavramı olmalı — bugün yok
  (`§AJ4.6`: marj hesaplanıp **atılıyor**, *"eminim"* aslında %98,9). Devir kuralının
  ön koşulu budur.

---

### 0.1 · DÖNGÜ — sırası değişmez

1. **≥20 ÖZGÜN senaryo** yaz: öncekileri **tekrar etmeyen**, **basitten zora**,
   **kısadan uzun zincire** (çok turlu thread'ler dahil).
2. **`curl` ile TEK TEK koş.** 🔴 **Toplu koşum YASAK.** Her turdan sonra dur, çıktıyı
   **ve konteyner loglarını anbean** oku.
3. **Her turu tek tek raporla ve bu belgeye yaz.**
4. **Ancak ondan sonra** teşhise geç: **TÜM** kök nedenleri çıkar.
5. **TÜM** düzeltmeleri yaz — 🔴 **aralarında KAPI KOŞMA** (yalnız hedefli
   `pytest tests/test_x.py`, 3–15 sn).
6. **BİR kez** docker tazele → **BİR kez** curl ile hepsini doğrula → **BİR kez** kapı koş.
7. **Durmadan tekrarla** — en zor senaryolarda bile thread'ler mükemmel akana kadar.

#### 🔴🔴 0.1.a · KAPI **TOPLU** KOŞULUR *(kullanıcı kararı 2026-08-08, BAĞLAYICI)*

> *"Sen tek tek düzeltip tek tek uzun testlere sebep oluyorsun. Sakın bir daha böyle
> yapma. **En az 20 senaryo ve toplu düzeltme sonrası** test yapabilirsin. Teste bu kadar
> vakit harcayamayız — tam kapı, demet kapısı vs. **toplu** yapılmalı, tek tek değil."*

🔴 **YASAK:** her kök için ayrı `--hepsi` / ayrı `--tam` / ayrı `--hizli`.

**Ölçülen israf (bu belgenin kendi turu, `§40`–`§46`):** beş kök için **beş ayrı tam
kapı** koşuldu — her biri ~7 dk, toplam **≈35 dakika**. Aynı beş kök **tek** koşumla
**7 dakikada** doğrulanabilirdi. **Beş kat maliyet, sıfır ek bilgi:** hiçbir koşum
öncekinin görmediği bir şey görmedi.

⚠ **Hedefli test bir kapı DEĞİLDİR ve serbesttir** (`pytest tests/test_x.py`, 3–15 sn) —
düzeltmeyi yazarken kullanılır. Kapı olan üç şey `--hizli`, `--tam`, `--hepsi`'dir ve
üçü de **yalnız 6. adımda** koşar.

> *Bir kapıyı her düzeltmeden sonra koşmak onu beş kat güvenli yapmaz — beş kat pahalı
> yapar. Ve pahalı bir kapı, atlanan bir kapıya dönüşür.*

### 0.2 · İki değişmez

* 🔴 **Tam çalışma = DOĞRU cevap.** Cevap gelmesi yetmez. `source=cube` görmek başarı
  değildir; `cq`'nun **doğru** olması başarıdır (ölçü · kapsam · dönem · beyan).
* 🔴 **Bu belge her bulguyu KANITIYLA taşır.** Soru · `source` · `cq` · `note` · `iz` ·
  süre · ilgili log satırı. *Hafıza gitse bile belge duracak.*

### 0.3 · Ortam — üç tuzak, üçü de bir kez ısırdı

| tuzak | belirti | çözüm |
|---|---|---|
| **Bayat imaj** | düzeltme etkisiz görünür | 🔴 `docker restart` **YETMEZ** — aşağıdaki `build` |
| **Token 15 dk** | `{"detail":"Geçersiz veya süresi dolmuş token"}` · **~8 ms** | yeniden login (ürün kusuru **değil**) |
| **Sağlayıcı kotası** | `402 Payment Required` · LLM susar | anahtar zinciri (§0.5) ya da `DIMA_LLM_PROVIDER=gemini` |

```bash
export DOCKER_BUILDKIT=0 && export COMPOSE_DOCKER_CLI_BUILD=0 && \
docker-compose build dima-backend && \
docker rm -f dima-backend-core && \
docker-compose up -d dima-backend
until curl -sf localhost:8001/health >/dev/null; do sleep 3; done && echo hazır
```

⚠ Kaynak **bind-mount edilmiyor**; `restart` aynı imajı başlatır. Bu bir kez oldu ve
**bütün bir ölçüm turu** dünkü kodu ölçtü.

### 0.4 · Yerel test kapısı — üç seviye, başkası yok

| ne zaman | komut | süre | kapı mı? |
|---|---|---|---|
| düzeltmeyi yazarken, serbestçe | `pytest tests/test_x.py` (yalnız hedef) | 3–15 sn | ❌ hayır |
| 🔴 **TÜM düzeltmeler bittikten sonra, BİR kez** | `lab/kapi.py --hizli --degisen <hepsi>` → `--tam` | ~2 + ~2 dk | ✅ evet |
| gecelik CI | `--hepsi` | 🔴 **yerelde ASLA** *(istisna: merkezî dosya + davranış değişikliği → demet sonunda BİR kez)* | ✅ evet |

🔴 **Ve `--degisen`'e demetin TÜM dosyaları birlikte verilir** — dosya başına ayrı koşum
`§0.1.a`'nın yasakladığı şeyin ta kendisidir.

🔴 Ve bu belgenin kendi dersi: **birim testleri bu kusurların hiçbirini görmedi.**
*"Bağlam 2. turdan sonra kopuyor"* · *"kök-neden sorusu veda sanıldı"* · *"anlatıcı 24
sn"* · *"tahmin sorusu 30 satır geçmiş veri"* — **hepsi yalnız canlı curl turunda**
göründü.

> **En önemli testler bu curl testleridir.**

### 0.5 · 🔴 ANAHTAR ZİNCİRİ — ölçüm durmasın diye

`.env` → `DIMA_OPENROUTER_API_KEYS` (virgüllü). Kota dolunca (`402`/`429`) **sıradakine**
geçilir; zincir **döngüseldir**, tur başa döndüğünde ilkinin kotası tazelenmiştir.

⚠ Rotasyon **çağrı başına değil HATA başına** ve **yeniden denemez**: çağrı bu tur düşer,
sonraki tur yeni anahtarla açılır. *Bir yedeğe geçmek, hatayı silmek değil bir sonrakini
kurtarmaktır.*
Kapı: `tests/test_anahtar_zinciri.py`.

*Bir ölçüm aracının durması, ölçtüğü şeyin bozulmasından daha sinsidir: biri kırmızı
verir, öteki sessizce sıfır ölçer.*


## 1 · MERDİVEN GERÇEĞİ — *"her şey LLM'e mi gidiyor?"*

### 1.1 · Sıra deterministik-önce, ve bu doğrulandı

`ask.py:2895` birebir:

```python
if route_hit is None and "ask_intent_first" in resolve_for(settings, principal):
```

🔴 **LLM ancak `route()` PES EDERSE çağrılıyor** (`route()` `:2734`). Bayrağın adı
yanıltıcı (*"intent first"*), davranışı değil. Ve LLM devreye girse bile **sayıyı küp
koyuyor**: model JSON'u `parse_cube_query`'nin katı beyaz listesinden geçiyor, sonra
`cube_sql` derliyor. **Model hiçbir koşulda sayıya dokunmuyor.**

Tam merdiven:

| # | basamak | LLM | ne zaman |
|---|---|---|---|
| 1 | **VQR** — doğrulanmış soru deposu (`ask.py:2509-2558`) | **0** | soru daha önce `/verify` ile onaylandıysa |
| 2 | **`route()`** — deterministik eşleştirme | **0** | katalog eşleşmesi kırılırsa |
| 3 | **Intent-JSON** — *garson* | ✅ | `route()` pes ederse |
| 4 | **Discovery** — ham SQL | ✅ | Intent de pes ederse |

⚠ VQR bile *"eşleşti, gönder"* demiyor: dönerken `parse_cube_query` **ve**
`_period_gate`'ten geçiyor — bayat bir eşleşme sessizce sunulmuyor.

### 1.2 · Chip'ler — ölçüldü, LLM'e gitmiyorlar

| chip türü | uç | LLM |
|---|---|---|
| **refine** (kırılım · dönem · kıyas · granülerlik) | `POST /cube` | **0 — her zaman** |
| **açılış** (starter) | `POST /ask` *(metin taşır)* | `route()` çözerse **0** |

⊙ **Açılış chip'leri ölçümü: 10 chip · 9'unu `route()` çözüyor → %90 deterministik.**

🔴 Düşen tek chip: `duruş nedenlerine göre toplam süre bu ay` → **`R10`**. İronik ve
öğretici: bu liste `starters.yml`'in kendi şerhinde *"BİLEREK önceden test edilmiş/kanıtlı
ifadeler"* diye tanımlı — yani **kanıtlanmış bir ifade bayatlamış**. Muhtemel sebep `göre`
belirsizliği (§5.1).

> *Gözlemin doğru ama sebebi başka: chip'ler LLM'e gitmiyor; **serbest yazdığın metinler**
> gidiyor — çünkü `route()` gerçek dilde zaten konuşmuyor (§2).*

---

## 2 · 🔴 BİRİNCİ BOŞLUK: `route()`'un *"EMİNİM"*İ KALİBRE DEĞİL

Senin şartın: *"%100 kesinse, dilsel olarak anlamı bariz ise, LLM'e gitmeden küp
çalışsın."* Bu şartın bugünkü karşılığı ölçüldü — **2285 gerçek kullanıcı sorusu**:

| kademe | toplam | **konuştu** | doğru | 🔴 sessiz-yanlış | ⚠ beyanlı kısmi | **etiketsiz** | 🔴 **hata** |
|---|---|---|---|---|---|---|---|
| K1 *(kolay)* | 386 | 43 | 30 | 1 | 12 | 31 | **%3,2** |
| K2 | 549 | 63 | 21 | **9** | 33 | 30 | 🔴 **%30,0** |
| K3 | 537 | 37 | 11 | 2 | 24 | 13 | **%15,4** |
| K4 | 543 | **0** | 0 | 0 | 0 | 0 | — |
| K5 | 270 | 10 | 7 | 0 | 3 | 7 | %0,0 |
| **TOPLAM** | **2285** | **153** | **69** | **12** | **72** | **81** | 🔴 **%14,8** |

Üç oran, üç farklı soruya cevap veriyor:

| soru | oran |
|---|---|
| `route()` gerçek dilde ne sıklıkla konuşuyor? | **%6,7** (153/2285) |
| Konuştuğunda ne sıklıkla sessizce yanılıyor? | **%7,8** (12/153) |
| 🔴 **Etiketsiz** konuştuğunda — yani *"eminim"* dediğinde? | 🔴 **%14,8** (12/81) |

> 🔴 **Senin şartın bugün karşılanmıyor.** `route()` çekincesiz cevap verdiğinde **her 7
> sorudan 1'inde** yanılıyor — ve yanıldığında `◆ CUBE` rozetiyle, yüksek güvenle
> yanılıyor. K2 kademesinde bu oran **%30**.

### 2.1 · Sebep: `route()`'un DERECE kavramı yok

İçeride **çok sinyalli bir marjin sistemi var** — ölçü-sinonim uzunluğu (`:908`) ·
alt-dize spesifikliği (`:932`) · boyut kanıtı (`:937`) · 4-harf cube marjini (`:947`) ·
`value_index` `AUTO_MARGIN=0.08`. Kıramazsa `None` dönüyor.

🔴 **Ama çıktısı ikili: bir `cube_query` ya da `None`.** *"Kıl payı kazandım"* ile
*"tartışmasız kazandım"* **aynı kapıdan** çıkıyor.

Senin istediğin ayrım tam burada duruyor ve **hesap zaten yapılıyor, sadece atılıyor**:

| bugün | istenen |
|---|---|
| eşleşti → **cevapla** | **tartışmasız** eşleşti → cevapla (0 LLM, anında) |
| — | **kıl payı** eşleşti → **LLM'e sor** *(bugün yanlış cevaplıyor: 12 vaka)* |
| eşleşmedi → LLM | eşleşmedi → LLM |

⚠ **Karşı maliyet ölçülmeli:** eşiği yükseltmek 12 sessiz-yanlışı kapatırken doğru
cevapların bir kısmını da LLM'e yollar (yavaşlar). Bu takas bugün **ölçülemiyor** (§8).

---

## 3 · 🔴 İKİNCİ BOŞLUK: GARSONUN FİŞİ EKSİK

### 3.1 · Mutfak 12 şey pişiriyor, fişte 7 satır var

`route()`'un bir `cube_query`'ye yazabildiği **tüm** anahtarlar (kaynak taraması) ile
Intent-JSON şemasının modele **sunduğu** alanlar:

| alan | ne yapar | mutfak | **şema** |
|---|---|---|---|
| `cube` | konu | ✅ | ✅ |
| `measures` | ölçü(ler) | ✅ | ✅ |
| `dimensions` | kırılım | ✅ | ✅ |
| `timeDimensions` | zaman kovası (aylık/haftalık) | ✅ | ✅ |
| `filters` | boyut filtresi | ✅ | ✅ |
| `compare` | `yoy`/`mom` dönemsel kıyas | ✅ | ✅ *(yeni)* |
| `blend` | çapraz-cube harman | ✅ | ✅ *(yeni)* |
| `period_expr` | dönem ifadesi *(Python çözer)* | ✅ | ✅ *(yeni)* |
| 🔴 `order` | sıralama (`asc`/`desc`) | ✅ | **❌** |
| 🔴 `limit` | ilk N satır | ✅ | **❌** |
| 🔴 `entity_limit` | *"en yüksek **5 makine**"* | ✅ | **❌** |
| 🔴 `measure_having` | **ölçü eşiği** — *"10 milyon üzeri"* (SQL `HAVING`) | ✅ | **❌** |
| 🔴 `ayrik_aylar` | **ayrık** dönemler — *"ocak **ve** haziran"*, aradakiler HARİÇ | ✅ | **❌** |
| 🔴 `referans` | adlandırılmış dönem kıyası `{eksen, kaynak, hedef}` | ✅ | **❌** |

⊙ **12 üretilebilir anahtar · 7 sunulan alan.**

🔴 Bu, *"sistemde yoksa hata versin"* ilkesinin **ihlalidir**: sistem o altı şeyi
**yapabiliyor**, ama LLM onları ifade edemediği için sonuç *"yapamadım"* diye çıkıyor.
*Bir yeteneği söyleyememek, ona sahip olmamakla aynı sonucu verir.*

### 3.2 · Ve mutfak, garsonun hiç bilmediği yemekleri de yapıyor

Bunlar `cube_query` alanı değil — ayrı yollar, LLM'in tetikleyebileceği bir yüzeyleri
**yok**:

| yetenek | modülü | LLM erişimi |
|---|---|---|
| katkı ayrıştırması (*"neden değişti?"*) | `contribution.py` | ◐ **takipte VAR** (§17.1) · tazede ⊘ |
| kök-neden kırılımı (drill) | `drill.py` | ⊘ |
| çapraz-cube KPI | `kpi.py` | ⊘ |
| gelir tablosu / bilanço | `statements.py` | ⊘ |
| hedef kıyası (*"hedefimin altında mıyım"*) | `hedef.py` | ⊘ |
| görünüm seçimi (grafik/tablo/panel) | `viz.py` · `view` | ◐ **yalnız takip yolunda** |

---

## 4 · 🔴 ÜÇÜNCÜ BOŞLUK: SÖZLEŞME RED'E YANLI

### 4.1 · Model, KOLAY işte ZOR işten daha yetkili

Aynı model iki prompt görüyor:

| | `select_cube` — **taze soru** *(zor iş)* | `refine_cube` — **rapor düzenle** *(kolay iş)* |
|---|---|---|
| görevi | ham Türkçeyi sıfırdan çevir | tek bir alanı değiştir |
| verilen alanlar | 8 çekirdek alan | + **`action`** · **`order`** · **`direction`** · **`limit`** · **`view`** · **`reason`** |
| örnek sayısı *(`→` sayımı)* | **5** | **21** |
| *"yapamıyorum"* kanalı | `{"cube":null}` — **sebepsiz bir hayır** | `action:"unavailable"` **+ `reason`** |

🔴 **Zor işi yapana daha az alan, daha az örnek, daha kaba bir red kanalı verilmiş.**

### 4.2 · Metin üç kez *"reddet"*, bir kez *"yorumla"* diyor

| yönlendirme | kaç kez |
|---|---|
| **reddet** — metinde *"KESİNLİKLE `{"cube":null}`"* · şemanın **ilk** dalı red · araç açıklamasında bir kez daha | 🔴 **3** |
| **yorumla** — *"günlük Türkçeyi ölçüye çevirmek senin işin"* | 1 *(bu turda eklendi; öncesinde **0**)* |

⊙ **Canlı sonuç (öncesi):** *"verimlilik"* içeren bir soruda **9/9 Intent çağrısı
`{"cube":null}`**.

> 🔴 Bu bir **yanlış anlama değil, bir REDDİR.** Bugün elimizde *"LLM niyeti yanlış
> anlıyor"* diye bir ölçüm **yok**; elimizdeki ölçüm *"LLM'in konuşmasına izin
> verilmiyor"*.

### 4.3 · Bağlam hiç gitmiyor

`select_cube` çağrısı `(system=katalog, user=ham soru)`'dan ibaret. Gitmeyenler:

* `body.history` — konuşma geçmişi
* önceki `cube_query` — kullanıcının **baktığı** rapor
* `G2` diyalog belleği — *sistemin az önce sorduğu soru*

⚠ Bunlar **tahmin değil olgu**; göndermenin çapa (anchoring) riski yok. Bugün model çok
turlu bir konuşmada **her turda sıfırdan** başlıyor.

### 4.4 · Katalog eşanlamsız gidiyordu *(bu turda kapatıldı)*

23 cube'un **23'ünde** Türkçe eşanlam beyan edilmiş (`oee` → *verim · randiman ·
performans*); LLM'e giden katalogda `verim` **0 kez** geçiyordu. `route()` o katmanı tam
kullanıyordu.

⊙ Kazanç dürüst ve **küçük**: 107 içerik kelimesinde eşleşmeyen **94 → 81**. Kalanların
çoğu katalogda **hiç olamaz** (`nasil` · `gidiyor` · `kaybediyoruz`) — bunlar terim değil
**analiz niyeti** (§6).

---

## 5 · 🔴 DÖRDÜNCÜ BOŞLUK: İKİ NİYET AYRIŞTIRICI *(karışıklığın yeri)*

LLM sorguyu üretse bile cevap **`_answer_from_cube_query`**'den geçiyor (`ask.py:2080`) ve
orada `uyum.denetle` çalışıyor (`ask.py:2194`). `uyum` ise niyeti **`app/niyet.py`'nin
deterministik ayrıştırıcısından** okuyor (`uyum.py:212`).

> 🔴 **Sorgunun sahibi LLM, ama *"kullanıcı ne istemişti"* iddiasının sahibi deterministik
> katman.** İkisi aynı cümlede farklı şey anlarsa, kullanıcı **deterministik olanın
> fikrini** LLM'in cevabına iliştirilmiş görüyor.

### 5.1 · Canlı vaka — kullanıcının kendi örneği

`şubatta ciro ocağa göre nasıl değişti`

| katman | ne anladı |
|---|---|
| deterministik `Niyet` | `tür=**kirilim**+trend` · dönem=**1** (yalnız şubat) |
| gerçek niyet | **kıyas** (şubat ↔ ocak) |
| kullanıcının gördüğü | *"Sayı doğru ama eksik: bir **kırılım** istedin ama boyut taşıyamadım"* |

🔴 Kullanıcı kırılım **istemedi.** Sistem ona **söylemediği bir şeyi söylediğini** söyledi.

İki kök neden, ikisi de deterministik tarafta:

1. **`gore` üç yönlü aşırı yüklü** (kırılım · granülerlik · dönem aralığı) — ve bu tam
   olarak *LLM'in anında anladığı* ayrım.
2. **`ocağa` hiç tanınmıyordu**: `ocak` + ünlüyle başlayan ek → `k`→`ğ` yumuşaması.
   `app/ek.py` (G7) ek **üretiyor** ama **sökmüyor**.

⚠ İkisi de bu turda kapatıldı — **ama tedavi semptoma yapıldı.** Asıl soru duruyor:
*deterministik katmanın, LLM'in cevapladığı bir soru hakkında ikinci bir fikir beyan
etmesi doğru mu?*

---

## 6 · SİSTEM DİLİNDE GERÇEKTEN OLMAYANLAR — dürüst sınır

Bunlar için hata vermek **doğrudur**; eksik olan hatanın **kalitesi**:

| istek | karşılığı | bugün ne oluyor |
|---|---|---|
| *"işler nasıl gidiyor"* · *"iyi miyiz"* | ⊘ yargı/eşik yok | `{cube:null}` → *"anlayamadım"* |
| *"ne yapmalıyız"* | ⊘ öneri motoru yok | aynı |
| ölçü→ölçü **ilişki/korelasyon** | ⊘ (v2) | *"yan yana koyabilirim, ilişkiyi hesaplayamam"* ✅ |
| adlandırılmış **indirgenemez** kıyas (*"mart ↔ haziran"*) | ◐ `referans` var, derleyicisi yalnız `donem` | etiketli kısmi cevap |
| tahmin / forecast | ⊘ | yetenek sınırı ✅ |

🔴 Ölçülen nüfus: `R11` (*"anlaşıldı ama **ifade edilemez**"*) sınıfı **30/408**. Kod
yazıldı, ölçüldü ve **geri alındı** (gerçek red kodunu örtüyordu) — ama **kullanıcıya
bakan yarısı hiç yapılmadı.** Bu sınıf bugün *"anlamadım"* diye çıkıyor; doğru cümle
*"anladım, bunu **söyleyemiyorum**"*.

⚠ Ayrıca ölçüm sırasında **27 katalog sızıntısı** kaydedildi (`bakiye` · `kar` ·
`dogalgaz` · `sapma`) — vaka korpusa girmedi. Bu terimler kataloğun kendi kapsam
boşluğudur, çevirinin değil.

---

## 7 · YAPILACAKLAR — **bağımlılık** sırasına göre

> Sıra maliyet/getiri değil, **bağımlılık** sırasıdır: 0 olmadan hiçbirinin etkisi
> ölçülemez.

### 0 · ÖNCE ALET *(her şeyin ön koşulu)*

| # | iş | neden |
|---|---|---|
| **0.1** | `eval --slice llm` **4 → ~200 vaka**, gerçek sağlayıcıyla | `nl_corpus` tanımı gereği `rule` ile koşar → **LLM yolunu göremez** |
| **0.2** | İki redi **ayır** | `cq is None` bugün hem *"model reddetti"* hem *"model uydurdu, beyaz liste düşürdü"* demek → **hangi düzeltmenin işe yaradığı bilinemez** |
| **0.3** | 🔴 **Yer gerçeğini gözden geçir** | 42 gerçek vakanın **20'sinde cevap vermek YASAK** (kabul: yalnız *sor* ya da *reddet*). Mimari LLM'e kayarsa korpus her iyileşmeyi **gerileme** raporlar — bu depoda tam bu sınıftan bir olay yaşandı (`gitas` düştü, doğruluk **yükseldi**) |

### 1 · MARJİNİ DIŞARI VER *(senin "%100 kesin" şartın)*

| # | iş | kanıt |
|---|---|---|
| **1.1** | `route()` bir **marjin/güven** de döndürsün — hesap zaten yapılıyor, atılıyor | etiketsiz cevapların **%14,8'i yanlış**; K2'de **%30** |
| **1.2** | Eşiğin **altında** kalan eşleşme cevap değil **LLM'e devir** olsun | 12 sessiz-yanlışın kapanma yolu |
| **1.3** | Eşiği **ölç**, seçme — kapsam↓ / doğruluk↑ takası sayıyla kararlaştırılsın | 0.1'e bağlı |

⚠ Bu, mimariyi değiştirmez: merdiven aynı kalır, yalnız 2. basamağın *"eminim"* eşiği
görünür ve ayarlanabilir olur.

### 2 · SİPARİŞ FİŞİNİ TAMAMLA — *"sistemde olanı söyleyebilsin"*

| # | iş |
|---|---|
| **2.1** | `order` + `limit` + `entity_limit` şemaya *(mutfak yapıyor, garson söyleyemiyor)* |
| **2.2** | `measure_having` şemaya *(“10 milyon üzeri”)* |
| **2.3** | `ayrik_aylar` şemaya. ⚠ `blend` ile birlikte **yasak** (fail-closed) — açıklamada yazılmalı |
| **2.4** | `referans` şemaya *(`parse_cube_query` kabul ediyor, şema sunmuyor)* |
| **2.5** | `view` taze yola *(takip yolunda **var**)* |
| **2.6** | 🔴 **`reason`** — model *"yapamıyorum, **çünkü**…"* diyebilsin *(takip yolunda **var**)* |

⚠ Ortak kural: alan şemaya **girer**, `parse_cube_query` onu **doğrular**. Beyaz liste
gevşetilmez — *"model geçersiz bir ad üretemez"* garantisi korunur.

### 3 · SÖZLEŞMENİN DİLİNİ DENGELE

| # | iş |
|---|---|
| **3.1** | Örnek sayısı taze yolda **5 → ~20** *(takip yolunda 21 var)* |
| **3.2** | `{"cube":null}` = *"gerçekten yanıtlanamıyorsa"*, *"emin değilsen"* değil *(başlandı)* |
| **3.3** | 🔴 **Kısmi anlama yolu:** *"cube'u seçebiliyorum, ölçüden emin değilim"*. Bugün ya **tam** bir `CubeQuery` ya **hiç** — ve netleştirme tam o aradadır |

### 4 · BAĞLAMI DEVRET *(tahmin değil, olgu)*

`body.history` · önceki `cube_query` · `G2` diyalog durumu → prompt.

🔴 **GÖNDERİLMEYECEK:** `route()`'un kısmi **tahmini**. Ölçüldü: tahmin **%74 vakada
yok**, olan 11 vakanın **2'si yanlış** (`ne kadar fire verdik` → sistem `oee` diyor,
doğrusu `parti`). *Bir tahmini paylaşmak, onu doğrulamak değil yaymaktır.*

### 5 · İKİ AYRIŞTIRICI KARARINI VER

| seçenek | ne demek |
|---|---|
| **A** | LLM cevabında `uyum` **yalnız sorguyu** denetlesin, soruyu değil |
| **B** | `uyum`'un niyet kaynağı LLM'in kendi beyanı olsun *(`reason` → 2.6'ya bağlı)* |

⚠ Bugünkü hâl **ölçülmüş bir yanlış beyan** üretti (§5.1). Bu bir tercih değil,
kapatılması gereken bir **ikinci sahip** (`KAT-1`).

### 6 · SINIRI DÜRÜSTÇE SÖYLE

*"Anlamadım"* ile *"anladım ama söyleyemiyorum"* ayrı cümleler olmalı — nüfus **30/408**.
Zemin hazır: `yetenek.py` + `soz.py` + `iddia.py` üçü de duruyor.

### 7 · VQR'ı BESLE *(bedava hız)*

Doğrulanmış soru deposu **zaten merdivenin ilk basamağı** ve **0 LLM**. Eksik olan
mekanizma değil, **dolması** — ve `/verify` geri bildiriminden besleniyor. Her onaylanan
cevap, o sorunun bir daha asla LLM'e gitmemesi demek.

---

## 8 · ÖLÇÜM ENGELİ — bu belgede ÜÇÜNCÜ kez

`§2`'nin eşiği, `§7/2`'nin alanları ve `§7/3`'ün prompt'u — **hiçbirinin kazancı bugünkü
aletlerle ölçülemez**:

| alet | ölçtüğü | LLM yolunu görür mü |
|---|---|---|
| `lab/nl_corpus.py` | `route()` tavanı, **`rule`** sağlayıcıyla | ❌ tanımı gereği kör |
| `lab/gercek_dunya.py` | `route()`, tek turlu | ❌ aynı sebep |
| `eval --slice llm` | uçtan uca, **gerçek sağlayıcı** | ◐ **4 vaka** |

> *Bir düzeltmeyi ölçemeden uygulamak, kusurun yerini değiştirmenin pahalı bir biçimidir.*

---

## 9 · KULLANICININ TEZİNE KARŞI TEK ÖLÇÜLMÜŞ İTİRAZ

> *"Deterministik burada sadece kafa karıştırıyor olabilir."*

Karıştırdığı yer **gerçek ve ölçülü** (§5). Ama *"kaldıralım"* için ölçüm **yok**:

| | ölçülen |
|---|---|
| `route()` gerçek dilde | konuşuyor **%6,7** · sessiz-yanlış **%0,53** *(korpus geneli)* |
| LLM aynı sorularda | **9/9 `{cube:null}`** |

🔴 Deterministik katman **zaten yoldan çekiliyor**. Onu kaldırmak çalışan %6,7'yi
kaldırır ve **bozuk olan yere hiç dokunmaz**.

⚠ Ve bir ayrım kritik:

| | kaldırılabilir mi | neden |
|---|---|---|
| **`route()`** — niyet ayrıştırıcı | ✅ evet *(maliyeti %6,7)* | bir hızlandırıcıdır |
| **`CubeQuery` IR** — yürütme dili | 🔴 **hayır** | `/cube` chip yolu (0 LLM) · `dashboards` · `schedules` · **Query Contract** ona bağlı. LLM her gün farklı SQL üretirse zamanlanmış her rapor **sahte "tanım değişti" alarmı** verir |

> **Doğru sıra:** önce aleti kur (§7/0), sonra marjini dışarı ver (§7/1) ve fişi tamamla
> (§7/2), *sonra* `route()`'un niyet rolünü tartış. Bugün *"LLM anlamıyor"* diye bir kanıt
> yok — çünkü LLM'e daha **hiç sorulmadı**.

---

## 10 · ÖZET

| soru | cevap |
|---|---|
| Sistem dili net mi? | ✅ **Net** — ama **dar**, ve darlığı kullanıcıya söylenmiyordu |
| Model o dili tam kullanabiliyor mu? | 🔴 **Hayır** — **12** yetenek, **7** sunulan alan |
| Model yanlış mı anlıyor? | ⊘ **Bilinmiyor** — ölçülen davranış **red** (9/9), yanlış anlama değil |
| *"Kesinse deterministik, şüphede LLM"* kurulu mu? | ✅ **Kurulu** (`VQR → route → LLM → Discovery`) |
| Peki `route()` gerçekten *"kesin"* mi? | 🔴 **Hayır** — etiketsiz cevaplarının **%14,8'i yanlış**; K2'de **%30** |
| Chip'ler LLM'e mi gidiyor? | ❌ **Hayır** — refine %100 `/cube`; açılış **9/10** deterministik |
| Neyin ne yaptığı karışık mı? | 🔴 **Evet, bir yerde:** sorgunun sahibi LLM, *"ne istendi"* iddiasının sahibi deterministik `Niyet` |
| Bugün ölçebiliyor muyuz? | 🔴 **Hayır** — `eval --slice llm` **4 vaka**; her şeyin ön koşulu bu |

---

## 11 · 🔴 CANLI ŞİKÂYETİN İZİ — *"makine bazında oee son 3 ay bile LLM'e gidiyor"*

### 11.1 · Lab'da bu soru LLM'e GİTMİYOR — ölçüldü

| soru | `route()` sonucu | teshis | ihlal |
|---|---|---|---|
| `makine bazında oee son 3 ay` | ✅ `cube=oee` · `ort_oee` · `dimensions=[makine]` · `tarih ≥ 2026-05-07` | `None` | `[]` |
| `makine bazinda oee son 3 ay` *(şapkasız)* | ✅ aynı | `None` | `[]` |
| `makine bazında oee` | ✅ aynı *(dönemsiz)* | `None` | `[]` |
| `son 3 ay oee` | ✅ `cube=oee` · `ort_oee` | `None` | `[]` |

🔴 **`route()` bu soruyu tam çözüyor.** Ve merdivenin sırası kaynaktan çıkarıldı — **NLP
önce**:

```
ask() gövdesi (1490–3862), karar noktaları sırayla:
  2527  🟢 VQR                    ← 0 LLM
  2734  🟢 route()                ← NLP intent      ◀ BURADA ÇÖZÜLÜYOR
  2801  🟡 cube_tie chip          ← 0 LLM, ama KESER
  2840  🔴 prompt_enhance         ← LLM
  2953  🔴 select_cube (Intent)   ← LLM
  ...
  3434  🟢 deterministic_refine   ← NLP takip
  3460  🟢 cross_cube_add         ← NLP
  3545  🔴 refine_cube            ← LLM
  3859  🔴 Discovery              ← LLM
```

`ask.py:2895` koşulu birebir: `if route_hit is None and "ask_intent_first" in …` —
**LLM ancak `route()` pes ederse.**

### 11.2 · O hâlde canlıda LLM'e gidiyorsa sebep DİLSEL DEĞİL

Kalan üç aday — ve ayırt edici kanıtları:

| # | hipotez | nasıl ayırt edilir |
|---|---|---|
| **A** | 🔴 **Soru bir THREAD içinde gönderiliyor.** O zaman istek `cube_query`/`history` taşır ve **takip dalına** girer (`:3434`). `deterministic_refine` **dar düzenleme** için yazılmıştır (*"aylara göre"*, *"temmuzu çıkar"*); **tam yeni bir soru** ona uymaz → `refine_cube`'e (**LLM**, `:3545`) düşer | İstek gövdesinde `cube_query` var mı? Boş bir thread'de aynı soru 0 LLM mi? |
| **B** | Farklı tenant kataloğu — `oee`/`makine` o şirkette eşleşmiyor | `source` ve `trace` hangi cube diyor? |
| **C** | LLM çağrısı **başka** bir soruya ait *(`consistency_k=3` → tek soruda 3 çağrı)* | Log'daki soru metni ile chip metni aynı mı? |

🔴 **En güçlü aday A** ve o gerçek bir tasarım boşluğu: **bir thread'in içinde, tamamen
deterministik bir soru bile LLM'e düşebiliyor** — çünkü takip dalı *"bu bir düzenleme mi"*
diye soruyor, *"bu kendi başına çözülebilir mi"* diye sormuyor.

> *Bir sorunun kendi başına çözülebilir olması, bağlam içinde sorulduğunda unutuluyor.*

**Öneri (7.1'in kardeşi):** takip dalında `deterministic_refine` başarısız olduğunda,
`refine_cube`'e (LLM) düşmeden **önce** soruyu **taze** `route()`'a bir kez daha sor.
Maliyeti sıfır (0 LLM, ~1 ms), kazancı: thread içindeki her deterministik soru anında
döner. ⚠ Sıra önemli — taze `route()` **düzenleme** niyetini ezmemeli: yalnız
`deterministic_refine` **ve** `cross_cube_add` ikisi de pes ettiyse denenir.

### 11.3 · Ve kullanıcının kuralı, sayıyla

> *"Aşçı tam duyarsa sorun yok; azıcık bile şüpheye düşerse hemen garson yollamalıdır."*

Bugün aşçı şüphesini **dışarı vermiyor** (§2.1): çıktısı ikili. Ölçülen sonuç —
**etiketsiz cevaplarının %14,8'i yanlış** (K2'de %30). Yani aşçı bugün *"tam duymadığı"*
12 vakada da yemeği çıkarıyor.

**Kuralın kodu tam olarak §7/1'dir:** `route()` marjini döndürsün, eşiğin altı garsona
gitsin. Hesap zaten yapılıyor — sadece atılıyor.

---

## 12 · MANUEL DOĞRULAMA SETİ — 10 THREAD *(kolaydan zora)*

> ⚠ **Bu bölüm ÇALIŞTIRILMADI ve neden çalıştırılmadığı yazılı:** canlı örneğe
> (`:8001`) giriş **reddedildi** — `owner@dima.local`, üç lab hesabı ve tenant hesabı
> (`demo-boyahane@usedima.com`) denendi, hepsi `401`. Aşağıdaki set **elle koşulmak
> üzere** hazır; her turun beklenen basamağı deterministik katmanın **ölçülmüş**
> davranışından yazıldı.

**Koşum biçimi** *(fronttan yazıyor gibi — pytest YOK)*:

```bash
TOK=$(curl -s -X POST localhost:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"<kullanıcı>","password":"<parola>"}' | jq -r .access_token)

# T1 — açılış (thread YOK: cube_query gönderme)
curl -s -X POST localhost:8001/ask -H "Authorization: Bearer $TOK" \
  -H 'Content-Type: application/json' \
  -d '{"question":"<soru>","execute":true,"session_id":"m1"}' \
  | jq '{source, note, eksik_niyet, cube_query, trace, explain}'

# T2 — takip (T1'in cube_query'sini AYNEN yankıla — frontend böyle yapıyor)
curl -s -X POST localhost:8001/ask -H "Authorization: Bearer $TOK" \
  -H 'Content-Type: application/json' \
  -d '{"question":"<takip>","execute":true,"session_id":"m1",
       "cube_query":<T1.cube_query>,"history":["<soru>"]}' \
  | jq '{source, note, eksik_niyet, cube_query, trace}'
```

🔴 **Her turda bakılacak dört şey:** `source` *(`cube` = 0 LLM · `cube+llm` = garson
devrede · `vqr` = önbellek)* · `note` *(beyan var mı)* · `eksik_niyet` *(sistem neyi
yapamadığını söylüyor mu)* · `trace` *(hangi basamak)*.

| # | T1 — açılış | T2 — takip | beklenen T1 | neyi sınar |
|---|---|---|---|---|
| **1** | `makine bazında oee son 3 ay` | `aylara göre` | 🟢 `cube` *(ölçüldü)* | **§11.2/A**: T1 0 LLM iken T2 de 0 LLM mi? Takip dalı deterministik kalıyor mu |
| **2** | `bu ay toplam üretim` | `hat bazında` | 🟢 `cube` | En basit hat — chip'lerin de yolu |
| **3** | `son 3 ay fire` | `bir de ciro ekle` | 🟢 `cube` | `cross_cube_add` (0 LLM) çalışıyor mu — **çapraz-cube harman** |
| **4** | `duruş nedenlerine göre toplam süre bu ay` | `en yüksek 5` | 🔴 `cube+llm` *(ölçüldü: `R10`)* | **Kendi açılış chip'imiz bayatlamış.** T2: `entity_limit` şemada YOK (§3.1) |
| **5** | `şubatta ciro ocağa göre nasıl değişti` | `peki mart nasıldı` | 🟡 kıyas, **beyanlı** | `göre` ayrımı + ay çekimi (§5.1). Yanlış *"kırılım istedin"* beyanı **gitti mi** |
| **6** | `yılbaşından bugüne hasılat` | `çeyreklere böl` | 🟢 `cube` *(YTD onarıldı)* | Onarılan **sessiz-yanlış**: eskiden `gte bugün` (ileriye) bakıyordu |
| **7** | `10 milyon üzeri ciro yapan müşteriler` | `sırala en yüksekten` | 🟡 `route` çözerse `cube` | 🔴 `measure_having` + `order` **şemada yok** — `route()` pes ederse LLM **ifade edemez** |
| **8** | `ocak ve haziran cirosunu karşılaştır` | `neden bu kadar fark var` | 🟡 **indirgenemez kıyas** → etiketli | `ayrik_aylar` şemada yok · T2 `contribution` LLM'e kapalı (§3.2) |
| **9** | `personel verimliliklerini kıyasla` | `o zaman sadece üretim bölümü` | 🔴 sınır beyanı | *"Verimlilik = OEE"* biliniyor ama `personel` yok → **doğru** sınır mı, yoksa *"anlamadım"* mı |
| **10** | `işler nasıl gidiyor bu ay` | `iyi mi kötü mü` | 🔴 `{cube:null}` → *"anlamadım"* | **§6'nın kalbi**: sistemde karşılığı **yok**. Doğru cevap *"anladım, söyleyemiyorum"* — bugün *"anlamadım"* diyor |

⊙ **Beklenen dağılım:** 1·2·3·6 → **0 LLM** · 5·7·8 → **beyanlı/kısmi** · 4·9·10 → **LLM
ya da sınır**. Gerçekleşen dağılım bundan **saparsa**, sapan satır §11.2'nin A/B/C
hipotezlerinden hangisinin doğru olduğunu söyler.

⚠ Thread 1 **kritik**: T1'de `source=cube` ama T2'de `cube+llm` çıkarsa **hipotez A
doğrulanmış** olur ve §11.2'nin önerisi (takip dalında taze `route()` denemesi) doğrudan
uygulanabilir.


---

## 13 · 🔴🔴 CANLI KOŞUM — TEŞHİS DEĞİŞTİ: LLM **INTENT'TE DEĞİL, ANLATIDA**

> Canlı örneğe (`:8001`, tenant `boyahane`) **gerçek HTTP** ile iki tur atıldı ve
> konteyner logları satır satır izlendi. Aşağıdaki her sayı o koşumdan.

### 13.1 · Tur 1 — `makine bazında oee son 3 ay` *(taze, thread YOK)*

```
13:42:52  BAĞLAM  kural=taze:capa-yok  cube=None  eksen=()
13:42:52  İSTEK   q='makine bazında oee son 3 ay'  followup=False
13:42:54  yayilim: perdeleme: 2 metin · 5 yer tutucu     ← ANLATI maskeleme
13:42:57  dima.llm: openrouter BAŞARILI (deepseek-v4-flash, 2936ms)   ← 🔴 LLM
13:42:58  CEVAP   source=cube  satır=11  süre=5420ms
```

| ölçüt | değer |
|---|---|
| `source` | **`cube`** |
| `explain.path` | *"cube (`route()` — **LLM'siz, sıfır maliyet**)"* · güven **1.0** |
| `trace` | *"Intent-path: `cube_router.route()` (LLM'siz)"* · *"niyet: tür=kirilim · kırılım=makine,donem"* |
| LLM çağrısı | **1** — ve **intent'ten SONRA**, `yayilim.perdele`'nin hemen ardından |

🔴 **Intent için LLM ÇAĞRILMADI.** Tek LLM çağrısı **anlatıcı** (T2) — ve toplam sürenin
**%54'ü** (2936/5420 ms).

### 13.2 · Tur 2 — `aylara göre` *(aynı thread, `cube_query` yankılanmış)*

```
13:43:18  BAĞLAM  kural=yapisal:cube_query  cube=oee  eksen=('makine',)
13:43:18  İSTEK   q='aylara göre'  followup=True(yapısal=True)
13:43:19  yayilim: perdeleme: 1 metin · 1 yer tutucu     ← ANLATI maskeleme
13:43:41  dima.llm: openrouter BAŞARILI (deepseek-v4-flash, 22564ms)  ← 🔴🔴 LLM
13:43:42  CEVAP   source=cube  satır=22  süre=24285ms
```

| ölçüt | değer |
|---|---|
| `source` | **`cube`** |
| `trace` | *"refine → **deterministik** düzenleme"* — `deterministic_refine`, 0 LLM |
| cevabın kendisi | ~**1 saniye** (istek → 22 satır) |
| 🔴 anlatıcı LLM | **22 564 ms** — toplam sürenin **%93'ü** |

### 13.3 · 🔴 SONUÇ — hipotez A ÇÜRÜDÜ, gerçek sebep başka

| iddia | ölçüm |
|---|---|
| *"Thread içinde deterministik soru LLM'e düşüyor"* (§11.2/A) | ❌ **ÇÜRÜDÜ** — `deterministic_refine` çalıştı, 0 LLM |
| *"Intent LLM'e gidiyor"* | ❌ **ÇÜRÜDÜ** — iki turda da `route()`/`refine` çözdü |
| 🔴 *"Her istekte LLM çağrısı var"* | ✅ **DOĞRU** — ama **anlatıcı**, intent değil |

> 🔴 **Kullanıcının gördüğü LLM çağrısı gerçek; attığı yer yanlıştı.** Garson siparişi
> **almıyor** — garson tabağı **anlatıyor**. Ve anlatmak, yemeği pişirmekten **20 kat**
> uzun sürüyor.

### 13.4 · Ve deterministik özet ZATEN ORADA — yeterli

Aynı cevapta iki metin birden üretiliyor:

| kaynak | metin | maliyet |
|---|---|---|
| 🟢 `interpret()` — **deterministik** | *"En yüksek makine: DİJİTAL BASKI (0,63 %). En düşük: RAM-3 (0,55 %); 11 kalem."* | **0 LLM · 0 ms** |
| 🔴 `t2_anlatici` — **LLM** | *"Geçen 3 aylık dönemde en yüksek OEE değerine sahip makine DİJİTAL BASKI oldu ve 0,63% seviyesinde gerçekleşti. En düşük OEE ise RAM-3 makinesinde 0,55%…"* | **2 936 ms** *(T2'de 22 564 ms)* |

🔴 **İkisi aynı üç olguyu söylüyor.** LLM'in kattığı şey **üslup**, bilgi değil — ve bu
vakada üslubun fiyatı cevabın kendisinin **20 katı**.

### 13.5 · YAPILACAK — anlatı merdiveni *(§7'ye 1.5 olarak girer, en yüksek öncelik)*

Bu, canlı denetimin ilk turunda da bulunmuştu (*"anlatıda deterministik ilk basamak
yok"*) ve şimdi **fiyatlandı**:

| # | iş |
|---|---|
| **1.5a** | 🔴 **Basit vakada anlatı `interpret()`'in `summary`'sinden gelsin** — tek ölçü · ≤1 kırılım · kıyas yok. Ölçülen kazanç: **−2,9 sn** (T1) · **−22,6 sn** (T2) |
| **1.5b** | LLM anlatıcısı yalnız **karmaşık** vakaya kalsın (çok ölçü · kıyas + segment · katkı ayrıştırması) — *"ne yüksek ne düşük"* zaten şablonla söylenebiliyor |
| **1.5c** | Karmaşıklık ölçütü **yapıdan** okunsun (`measures` · `dimensions` · `compare` · `blend` sayısı), metinden değil — ikinci bir dil ayrıştırıcısı doğmasın |
| **1.5d** | ⚠ Sağlayıcı gecikmesi ayrıca bakılmalı: `deepseek-v4-flash` **22,5 sn** sürdü. *"Flash"* bir modelde bu bir sapma; failover/zaman aşımı eşiği ölçülmeli |

⚠ Ve `narration_guard` korunur: deterministik özet zaten **sayıyı sistemden** alıyor,
yani guard'ın koruduğu şey **yapısal olarak** garanti — LLM anlatısında olmayan bir güvence.

*Bir cevabı süslemek için, cevabın kendisinden yirmi kat uzun beklemek, süslemek değil
geciktirmektir.*


---

## 14 · CANLI THREAD KOŞUMU — 6 thread · 12 tur · tek tek API üzerinden

> Tenant `boyahane` · `:8001` · gerçek HTTP · her turun logu izlendi.
> Sağlayıcı: `openrouter / deepseek-v4-flash`.

| # | tur | soru | `source` | satır | **süre** | anlatı | not |
|---|---|---|---|---|---|---|---|
| 1 | T1 | `makine bazında oee son 3 ay` | 🟢 `cube` | 11 | **5 420 ms** | LLM | intent 0 LLM |
| 1 | T2 | `aylara göre` | 🟢 `cube` | 22 | 🔴 **24 285 ms** | LLM | `deterministic_refine` |
| 2 | T1 | `bu ay toplam üretim` | 🟢 `cube` | 1 | **602 ms** | LLM | ⚠ *"«uretim» birden fazla yerde tanımlı"* — **belirsizlik beyanı** ✅ |
| 2 | T2 | `hat bazında` | 🟢 `cube` | **0** | **568 ms** | — | boş sonuç **dürüstçe** anlatıldı ✅ |
| 3 | T1 | `son 3 ay fire` | 🟢 `cube` | 1 | **10 109 ms** | LLM | *"«fire» birden fazla yerde"* ✅ |
| 3 | T2 | `bir de ciro ekle` | 🟢 `cube` | 1 | **12 098 ms** | LLM | **çapraz-cube harman** 0 LLM ✅ |
| 4 | T1 | `duruş nedenlerine göre toplam süre bu ay` | 🔴 `cube+llm` | 0 | 🔴 **16 687 ms** | — | **kendi açılış chip'imiz** |
| 4 | T2 | `en yüksek 5` | 🟢 `cube` | 0 | **655 ms** | — | `entity_limit` takipte **çalışıyor** |
| 5 | T1 | `şubatta ciro ocağa göre nasıl değişti` | 🟡 **`vqr`** | 30 | **434 ms** | LLM | 🔴 `eksik_niyet=['kiyas','trend']` |
| 6 | T1 | `yılbaşından bugüne hasılat` | 🔴 `cube+llm` | 1 | 🔴 **24 269 ms** | LLM | |
| 6 | T2 | `çeyreklere böl` | 🔴 `cube+llm` | 2 | 🔴🔴 **69 399 ms** | LLM | *"Takip: **LLM-destekli** yapısal düzenleme"* |

### 14.1 · 🔴 Süre dağılımı — asıl bulgu

| yol | süre aralığı |
|---|---|
| 🟢 intent 0 LLM **+ anlatı yok** | **434 – 655 ms** |
| 🟢 intent 0 LLM **+ anlatı LLM** | **5 420 – 24 285 ms** |
| 🔴 intent LLM **+ anlatı LLM** | **16 687 – 69 399 ms** |

> 🔴 **Anlatıcıyı kapatmak, en hızlı turu 434 ms'de tutuyor; açmak aynı işi 24 saniyeye
> çıkarıyor.** Ve 0 satır dönen turlarda anlatı **zaten çalışmıyor** (T2.2 · T4.1 · T4.2)
> — yani mekanizma **zaten koşullu**, koşulu **yanlış** (boş-mu? diye soruyor,
> **karmaşık-mı?** diye sormuyor).

### 14.2 · 🔴🔴 69 saniyelik tur — `çeyreklere böl`

`deterministic_refine` bu düzenlemeyi **çözemedi** → `refine_cube`'e (LLM) düştü
(*"Takip: LLM-destekli yapısal düzenleme"*), sonra üstüne anlatı LLM'i bindi.

⚠ Oysa *"çeyreklere böl"* bir **granülerlik** düzenlemesidir ve `_time_gran` `quarter`'ı
tanıyor. Yani **iki LLM çağrısı**, deterministik olarak çözülebilecek bir istek için.

### 14.3 · 🔴 VQR EKSİK BİR CEVABI ÖNBELLEKLİYOR

Thread 5 · `source=vqr` · **434 ms** — ve beraberinde:

```
eksik_niyet : ['kiyas', 'trend']
note        : ⚠ Sayı doğru ama eksik —
              · iki dönemi kıyaslamanı istedin ama tek bir toplam üretebildim
              · değişimi/trendi istedin …
```

🔴 **Doğrulanmış soru deposu, *"beyanlı kısmi"* bir cevabı dondurmuş.** Yani bu soru
artık **her seferinde** eksik cevaplanacak ve deterministik yol iyileşse bile VQR onu
**es geçecek** — merdivenin ilk basamağı olduğu için.

⚠ Kapı önerisi: VQR'a yazma koşuluna *"`eksik_niyet` boş olmalı"* eklenmeli.
*Bir önbellek, doğruladığı şeyin eksik olduğunu bilmiyorsa, eksikliği kalıcılaştırır.*

### 14.4 · İYİ ÇALIŞAN ÜÇ ŞEY — kayda geçsin

| ne | kanıt |
|---|---|
| **Belirsizlik beyanı** | *"«uretim» birden fazla yerde tanımlı — bu cevap **OEE** tanımıyla; diğerleri: uretim (parti)"* — sessiz seçim **yok** |
| **Boş sonuç dürüstlüğü** | *"Rapor doğru kuruldu — elimdeki veri 01.01.2024–30.06.2026"* — *"veri yok"* demiyor, **sınırı** söylüyor |
| **Çapraz-cube harman** | `bir de ciro ekle` → iki ölçü tek tabloda, **0 LLM** (`cross_cube_add`) |

### 14.5 · ⚠ CANLI ÖRNEK ESKİ KOD KOŞUYOR

`yılbaşından bugüne hasılat` canlıda **`cube+llm`** (24,3 sn) — oysa depodaki onarılmış
`route()` bunu **deterministik** çözüyor (§ YTD onarımı). Yani canlı konteyner
(`dima-backend-core`, ~1 saattir ayakta) bu turdaki düzeltmeleri **taşımıyor**.

🔴 Ölçüm okunurken bu ayrım korunmalı: **canlı sayılar bugünkü kodun değil, dünkü kodun
faturasıdır.** Yeniden derleme sonrası aynı 12 tur tekrarlanmalı.

### 14.6 · ⚠ SAĞLAYICI GECİKMESİ AYRI BİR BULGU

`deepseek-v4-flash` tek çağrıda **2,9 sn → 22,6 sn → 69,4 sn** aralığında salındı.
*"Flash"* sınıfı bir modelde bu bir **sapma**; zaman aşımı eşiği ve failover sırası
ayrıca ölçülmeli. ⚠ Ölçümlerin bir kısmı sağlayıcıya ait olabilir — anlatı merdiveni
kararı bundan **bağımsız** olarak doğrudur (0 satırda zaten çalışmıyor).


---

## 15 · RUNBOOK — düzeltmelerden SONRA aynı usulle nasıl koşulur

> Bu bölüm §14'ün **birebir tekrarı** içindir. Aynı adımlar, aynı okunacak alanlar,
> aynı log satırları — ki *"düzeldi mi"* sorusu **aynı ölçüyle** yanıtlansın.
> ⚠ Test koşucusu (`pytest`) **kullanılmaz**: amaç ürünün gerçek HTTP yüzeyini,
> kullanıcının yazdığı gibi sınamaktır.

### 15.0 · 🔴 ÖNCE KONTEYNERİ TAZELE — yoksa dünkü kodu ölçersin

§14.5'te ölçüldü: canlı konteyner düzeltmeleri **taşımıyordu** (`yılbaşından bugüne`
canlıda `cube+llm`, depoda deterministik). Kaynak bind-mount **edilmiyor**.

```bash
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}' | grep dima-backend
# → dima-backend-core  Up X  0.0.0.0:8001->8000/tcp
curl -s localhost:8001/health        # → {"status":"ok"}
```

🔴 **KOD DEĞİŞTİYSE `restart` YETMEZ — YENİDEN DERLE.** Kaynak bind-mount edilmiyor;
`docker restart` **aynı imajı** yeniden başlatır, yani dünkü kodu ölçmeye devam edersin
(§14.5'te tam bu oldu). Doğru komut:

```bash
export DOCKER_BUILDKIT=0 && export COMPOSE_DOCKER_CLI_BUILD=0 && \
docker-compose build dima-backend && \
docker rm -f dima-backend-core && \
docker-compose up -d dima-backend
```

⚠ Derleme sonrası **`/health` 200 dönene kadar bekle** (VQR embedder soğuk açılışta
dakikalarca askıda kalabiliyor — bilinen kusur):

```bash
until curl -sf localhost:8001/health >/dev/null; do sleep 3; done && echo "hazır"
```

⚠ `:8000` **başka bir uygulamadır** (`akis-main`); Dima `:8001`.

### 15.1 · Kimlik

Parola kodda sabit: `backend/control_plane/seed.py` → `DEMO_OWNER_PASSWORD`.
E-posta kalıbı: `{tenant-slug}@usedima.com` (`seed.py:150`).

```bash
TK=$(curl -s -X POST localhost:8001/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
echo "${#TK} karakter"
```

🔴 **Hız sınırı vardır.** Yanlış parola denemeleri
`{"detail":"Çok fazla deneme — bir süre bekleyin"}` üretir ve pencere kapanana kadar
**doğru parola da reddedilir** (ölçüldü: ~30–60 sn). Parolayı önce koddan **oku**, deneme
yapma.

### 15.2 · Tek turluk çağrı — kopyala/yapıştır

```bash
ask(){ # ask <session> <soru> [cube_query_json] [history_json]
  local sid="$1" q="$2" cq="$3" hist="$4" body
  if [ -n "$cq" ]; then
    body="{\"question\":\"$q\",\"execute\":true,\"session_id\":\"$sid\",\"cube_query\":$cq,\"history\":[$hist]}"
  else
    body="{\"question\":\"$q\",\"execute\":true,\"session_id\":\"$sid\"}"
  fi
  local T0=$(date +%s%3N)
  curl -s --max-time 120 -X POST localhost:8001/ask \
       -H "Authorization: Bearer $TK" -H 'Content-Type: application/json' \
       -d "$body" -o /tmp/cur.json
  local T1=$(date +%s%3N)
  python3 -c "
import json
d=json.load(open('/tmp/cur.json')); i=d.get('interpretation') or {}
print(f\"  src={str(d.get('source')):9} satır={str((d.get('result') or {}).get('row_count')):4} ${T1}-${T0}ms\")
print('  eksik_niyet:', d.get('eksik_niyet'))
print('  note       :', (d.get('note') or '—')[:180])
print('  explain    :', json.dumps(d.get('explain'), ensure_ascii=False))
print('  iz         :'); [print('     -', x) for x in (d.get('trace') or [])]
print('  anlatı     :', 'LLM' if i.get('narration') else '—', '| özet:', (i.get('summary') or '—')[:100])
"
  python3 -c "import json;print(json.dumps(json.load(open('/tmp/cur.json')).get('cube_query'),ensure_ascii=False))" > /tmp/cq.json
}
```

**Thread kurmak** — frontend'in yaptığının aynısı: T1'in `cube_query`'sini T2'ye **aynen**
yankıla.

```bash
ask t1 "makine bazında oee son 3 ay"                       # T1 — taze
CQ=$(cat /tmp/cq.json)
ask t1 "aylara göre" "$CQ" '"makine bazında oee son 3 ay"' # T2 — thread içi
```

### 15.3 · 🔴 HER TURDA OKUNACAK ALTI ALAN

| alan | ne söyler | 🟢 iyi | 🔴 kötü |
|---|---|---|---|
| `source` | hangi basamak cevapladı | `cube` · `vqr` | `cube+llm` *(intent LLM'e gitti)* |
| `explain.path` | **aynı şeyin doğrulaması** | *"route() — LLM'siz"* | *"LLM Intent-JSON"* |
| `trace[0]` | ilk basamak | *"cube_router.route()"* · *"refine → **deterministik** düzenleme"* | *"Takip: **LLM-destekli** yapısal düzenleme"* |
| `eksik_niyet` | sistem neyi **yapamadığını** söylüyor mu | `None` | dolu → cevap **kısmi** |
| `note` | beyan kanalı | belirsizlik/boş-sonuç açıklaması | sessizlik |
| `interpretation.narration` | anlatıcı LLM koştu mu | `—` *(basit vaka)* | `LLM` *(basit vakada = israf)* |

⚠ `source` ile `explain.path` **birbirini doğrular**; ayrışırlarsa biri bayattır — bu
depoda bir kez oldu (Intent-JSON cevabı `route()` güveniyle rozetlenmişti).

### 15.4 · LOGU İZLE — sürenin nereye gittiği YALNIZ orada görünür

```bash
docker logs --since 10m dima-backend-core 2>&1 \
  | grep -E "İSTEK|CEVAP|BAĞLAM|dima\.llm|yayilim|Discovery|vqr"
```

Okunuşu — §14'ten gerçek bir tur:

```
13:43:18  BAĞLAM  kural=yapisal:cube_query cube=oee eksen=('makine',)   ← thread ALGILANDI
13:43:18  İSTEK   q='aylara göre'  followup=True(yapısal=True)          ← takip dalı
13:43:19  yayilim: perdeleme: 1 metin · 1 yer tutucu                    ← ANLATI maskeleme
13:43:41  dima.llm: openrouter BAŞARILI (…, 22564ms)                    ← 🔴 anlatı LLM
13:43:42  CEVAP   source=cube  satır=22  süre=24285ms
```

🔴 **Ayrıştırma kuralı — bu raporun bütün teşhisi buna dayanıyor:**

| log deseni | ne demek |
|---|---|
| `dima.llm` satırı **`yayilim: perdeleme`'den SONRA** | çağrı **ANLATICIDIR** (intent değil) |
| `dima.llm` satırı `İSTEK` ile `CEVAP` arasında, **perdeleme YOK** | çağrı **INTENT**'tir |
| `dima.llm` **hiç yok** | tur tamamen deterministik |
| `süre` − `dima.llm ms` | **cevabın kendi maliyeti** *(ölçüldü: ~1 sn)* |

### 15.5 · 🔴 KABUL TABLOSU — düzeltmeler sonrası beklenen

| # | soru | bugün *(ölçüldü)* | düzeltme sonrası **beklenen** |
|---|---|---|---|
| 1·T1 | `makine bazında oee son 3 ay` | `cube` · 5 420 ms · anlatı **LLM** | `cube` · **< 1 sn** · anlatı **şablon** *(§13.5a)* |
| 1·T2 | `aylara göre` | `cube` · **24 285 ms** | `cube` · **< 1 sn** |
| 2·T1 | `bu ay toplam üretim` | `cube` · 602 ms · anlatı LLM *(özet: **"1 satırlık sonuç"**)* | anlatı **YOK** — özeti boş olan vakada LLM çağrılmamalı |
| 4·T1 | `duruş nedenlerine göre toplam süre bu ay` | 🔴 `cube+llm` · 16 687 ms | 🟢 `cube` — **kendi açılış chip'imiz** deterministik olmalı |
| 5·T1 | `şubatta ciro ocağa göre nasıl değişti` | `vqr` · `eksik_niyet=['kiyas','trend']` | 🔴 **VQR'dan DÜŞMELİ** *(§14.3)* → `compare=mom` ile tam cevap |
| 6·T1 | `yılbaşından bugüne hasılat` | 🔴 `cube+llm` · 24 269 ms | 🟢 `cube` — YTD onarımı **canlıya inince** |
| 6·T2 | `çeyreklere böl` | 🔴🔴 `cube+llm` · **69 399 ms** | 🟢 `cube` · *"refine → **deterministik**"* — `_time_gran` `quarter`'ı tanıyor |

### 15.6 · Koşum disiplini

1. **Tur tur ilerle.** Bir turun `cube_query`'si sonrakinin girdisidir; toplu koşmak
   thread'i bozar.
2. **Her turdan sonra logu oku.** `source=cube` görüp geçmek yetmez — §14'ün bütün
   bulgusu *"`source=cube` ama yine de LLM çağrısı var"* satırındaydı.
3. **Süreyi iki parçaya ayır** (§15.4). Toplam süre tek başına hangi katmanın yavaş
   olduğunu **söylemez**.
4. ⚠ **Sağlayıcı gecikmesini karıştırma.** `deepseek-v4-flash` aynı oturumda
   2,9 → 22,6 → 69,4 sn salındı. Şüpheliyse aynı turu **iki kez** koş; fark büyükse sorun
   mimaride değil sağlayıcıdadır (`KURAL G-1`'in aynı ilkesi).
5. **Boş sonuç bir kusur değildir.** Demo verisi **30.06.2026**'da bitiyor; *"bu ay"*
   soruları 0 satır döner ve sistem bunu **dürüstçe** söyler — bu ✅ bir davranıştır.


---

## 16 · 🔴🔴 UZUN THREAD KOŞUMU — İKİ YENİ KUSUR, biri AĞIR

### 16.1 · Thread 7 — *"bu neden düşük"* zinciri (4 tur)

| tur | soru | `source` | satır | süre | iz |
|---|---|---|---|---|---|
| 1 | `mayıs ayında hat bazında oee` | 🟢 `cube` | 8 | 7 626 ms | `route()` — LLM'siz |
| 2 | `en düşük hangisi` | 🟢 `cube` | 8 | 11 638 ms | `refine → deterministik düzenleme` |
| 3 | `peki bu neden düşük` | 🔴🔴 **`meta`** | — | **371 ms** | 🔴 **`sosyal sınıf (kapanis)`** |
| 4 | `nisanla kıyasla` | 🔴 `cube+llm` | 1 | 19 783 ms | `eksik_niyet=['kiyas']` |

### 16.2 · 🔴🔴 KUSUR A — kök-neden sorusu **VEDA** sanıldı

```
soru : "peki bu neden düşük"
iz   : sosyal sınıf (kapanis) → deterministik yanıt (LLM'siz, sıfır maliyet)
cevap: "Görüşürüz! İstediğin zaman buradayım."
süre : 371 ms
```

🔴 **Kullanıcı bir kök-neden sorusu sordu; sistem hoşça kal dedi.** Ve bunu **0 LLM ile,
371 ms'de, kendinden emin** yaptı — yani en ucuz, en hızlı, en yanlış cevap.

**Tetikleyici izole edildi** — beş varyant, tek tek:

| soru | `source` | cevap | yargı |
|---|---|---|---|
| `peki bu neden düşük` | 🔴 `meta` | *"Görüşürüz!"* | **YANLIŞ** |
| `peki neden böyle` | 🔴 `meta` | *"Görüşürüz!"* | **YANLIŞ** |
| `neden düşük` | 🟢 `None` | *"ort oee çıkarabilirim — hangi dönem için?"* | ✅ netleştirme |
| `peki bu ay ciro` | 🟢 `cube` | rapor | ✅ |
| `bu neden düşük` | ⚠ — | **bozuk JSON** *(§16.3)* | ⚠ |

⊙ **Teşhis:** tetikleyici **`peki`**. Ama tek başına değil — `peki bu ay ciro` **doğru**
çalışıyor. Yani sosyal sınıf kapısı (`D1`) şöyle davranıyor:

> `peki` sosyal sözlükte **var** *(kapanış ailesi)*; cümlede **veri sinyali** bulunmazsa
> sosyal sınıf kazanıyor. `bu neden düşük` bir katalog terimi taşımadığı için veri sinyali
> **sayılmıyor** → *"peki"* kapanış diye okunuyor.

🔴 Kusur `peki`'nin sözlükte olmasında değil, **veri sinyalinin tanımında**: bir **takip
sorusu** (`bu`, `neden`, `düşük`) katalog terimi taşımaz — ama bir thread'in ortasında
gelmiştir ve önceki turun `cube_query`'si **elde durmaktadır**. Kapı ona bakmıyor.

> *Bir cümlenin veri sorusu olup olmadığı, yalnız kendi kelimelerinden okunamaz —
> bağlamı elde tutan bir sistem için bu bilgi zaten mevcuttur.*

⚠ Ve bu, `D1`'in kendi kapı cümlesiyle **çelişiyor**: *"veri sinyali varsa sosyal kelime
kapıyı AÇMAZ"*. Kural doğru; **sinyalin tanımı** thread bağlamını kapsamıyor.

### 16.3 · ⚠ KUSUR B — bozuk JSON yanıtı

`bu neden düşük` → istemci tarafında:

```
json.decoder.JSONDecodeError: Invalid control character at: line 1 column 415
```

🔴 Yanıt gövdesinde **kaçırılmamış bir kontrol karakteri** var (muhtemelen bir metin
alanına giren ham `\n`). Bu, `curl | jq` ya da herhangi bir katı JSON çözücüsünde
**yanıtın tamamını** düşürür — ön yüz bunu *"sunucu hatası"* diye gösterir.

⚠ Ayrı bir bulgu ve `§16.2`'den bağımsız: aynı soru `peki` olmadan sorulduğunda ortaya
çıktı.

### 16.4 · Thread 7'nin öteki iki dersi

| bulgu | kanıt |
|---|---|
| 🟢 `en düşük hangisi` **deterministik** çözüldü | `refine → deterministik düzenleme`, 0 LLM intent |
| 🔴 `nisanla kıyasla` **kıyas kuramadı** | `cube+llm` · `eksik_niyet=['kiyas']` · *"iki dönemi kıyaslamanı istedin ama tek bir toplam üretebildim"* — §3.1'in `referans`/`ayrik_aylar` boşluğunun canlı hâli |

### 16.5 · Bu iki kusurun `§15` runbook'una eklenmesi

| # | soru | bugün | beklenen |
|---|---|---|---|
| 7·T3 | `peki bu neden düşük` | 🔴 `meta` — *"Görüşürüz!"* | thread içinde **asla sosyal** olmamalı; `contribution`/netleştirme |
| — | `peki neden böyle` | 🔴 `meta` | aynı |
| — | `bu neden düşük` | ⚠ bozuk JSON | geçerli JSON |
| 7·T4 | `nisanla kıyasla` | 🔴 `eksik_niyet=['kiyas']` | `compare=mom` ile tam kıyas |

⚠ **Regresyon kapısı önerisi:** sosyal sınıf kapısına *"istekte `cube_query` varsa sosyal
sınıf kapalıdır"* şartı. Bir thread'in içinde veda edilmez.


---

## 17 · THREAD 8–9 — bir DÜZELTME, iki YENİ KUSUR

### 17.1 · ✅ DÜZELTME: kök-neden analizi ÇALIŞIYOR *(§3.2 kısmen yanlıştı)*

```
soru : "neden bu kadar fark var"        (T8, 2. tur)
iz   : Takip: üçüncü sınıf → cevap üstünde konuşma (neden, LLM'siz)
note : "Değişimi en çok sürükleyen segmentler aşağıda — her biri tıklanınca
        tek başına açılır ve kendi kanıtını üretir."
süre : 3 018 ms · 0 LLM
```

🔴 **§3.2'nin *"`contribution.py` → LLM erişimi ⊘"* satırı DÜZELTİLİR:** katkı
ayrıştırması **takip yolundan** erişilebiliyor (`followup.py`'nin `NEDEN` sınıfı) ve
**0 LLM** ile çalışıyor. Erişilemeyen şey **taze** soruda tetiklenmesi.

### 17.2 · 🔴🔴 VE BU, `peki` KUSURUNU KESİNLEŞTİRİYOR

Aynı niyet, iki thread, iki farklı akıbet:

| soru | `source` | cevap |
|---|---|---|
| `neden bu kadar fark var` | ✅ takip/`NEDEN` | **katkı ayrıştırması** — doğru |
| `peki bu neden düşük` | 🔴 `meta` | **"Görüşürüz!"** |

> 🔴 Tek fark **`peki`**. Sistem *"neden?"* sorusunu **cevaplayabiliyor** — ama başına
> bir bağlaç geldiğinde onu **vedaya** çeviriyor.

*Bir niyeti cevaplayabilen sistemin, aynı niyeti bir kelime yüzünden kaybetmesi, kapsam
sorunu değil sınıflandırma sorunudur.*

### 17.3 · 🔴 KUSUR C — netleştirme YANLIŞ ÖLÇÜ öneriyor

```
soru : "personel verimliliklerini kıyasla"
iz   : Intent-path: dönem belirsiz → netleştirme (LLM'siz)
note : "toplam agirlik kg çıkarabilirim — hangi dönem için?"
süre : 21 403 ms
```

🔴 Kullanıcı **personel verimliliği** sordu; sistem **`toplam ağırlık kg`** öneriyor —
alakasız bir ölçü. Ve *"hangi dönem için?"* diye soruyor, yani **yanlış ölçüyü
varsayılmış kabul edip** üstüne dönem istiyor.

⊙ Daha önce ölçülmüştü: bu soruda sistem `ort_oee`'yi eşleştiriyor ve `personel`'i
bilinmeyen sayıyor. Canlıda **üçüncü** bir ölçü öneriliyor — yani netleştirmenin ölçü
seçimi ile `route()`'un eşleştirmesi **ayrışmış** durumda.

⚠ Ve 21,4 sn: netleştirme *"LLM'siz"* diyor, ama süre bir LLM çağrısına işaret ediyor
(muhtemelen önce Intent-JSON denendi, sonra netleştirmeye düşüldü).

### 17.4 · 🔴 KUSUR D — YETENEK SINIRI ATLANIYOR *(tahmin sorusu)*

```
soru : "gelecek ay ciro tahmini"
iz   : VQR eşleşme bulundu: dönem belirsiz → netleştirme (LLM'siz)
note : "toplam ciro çıkarabilirim — hangi dönem için?"
```

🔴 Kullanıcı **tahmin** istedi. Sistemde tahmin **yok** ve `app/yetenek.py` bunun için
bir sınır beyanı taşıyor (*"forecast yok"*). Ama beyan **hiç konuşmadı**: netleştirme
önce fırladı ve *"hangi dönem için?"* diye sordu.

> 🔴 Kullanıcı **gelecek** sordu, sistem **geçmiş** için dönem soruyor. Ve bir dönem
> söylerse, yapamadığı şeyi yapmış gibi bir sayı dönecek.

⚠ Bu, denetimin *"netleştirme çıkışları yetenek kapısını atlatıyor"* bulgusunun **canlı
doğrulaması**. Sıra kusuru: `yetenek.kapsam_disi` `ask.py:3690`'da — netleştirme
dallarının **çok sonrasında**.

*Bir sınırı bilmek, onu doğru anda söylemekten farklıdır; geç söylenen sınır,
söylenmemiş sınırdır.*

### 17.5 · ⚠ KOŞUM NOTU — token 15 dakikada doluyor

Thread 8–10'un ilk denemesi **5–8 ms**'de boş döndü; ham yanıt:
`HTTP 401 {"detail":"Geçersiz veya süresi dolmuş token"}`.

🔴 `access_ttl_seconds = 15 * 60`. Uzun koşumlarda **token yenilenmeli**, yoksa boş
`source=None` satırları **bulgu sanılır**. Runbook'a girdi (§15.1).

```bash
# her ~10 dakikada bir, ya da HTTP 401 görünce
TK=$(curl -s -X POST localhost:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
```

⚠ Ve `ask()` kabuğu **HTTP kodunu da basmalı** (`-w "%{http_code}"`) — aksi hâlde 401
sessizce *"cevap yok"* gibi okunur.

### 17.6 · Kabul tablosuna eklenenler

| # | soru | bugün | beklenen |
|---|---|---|---|
| 8·T1 | `ocak ve haziran cirosunu karşılaştır` | 🟡 `cube` · `eksik_niyet=['kiyas']` · 1 642 ms | `ayrik_aylar` ile **iki ayrı seri** |
| 8·T2 | `neden bu kadar fark var` | ✅ katkı ayrıştırması · 0 LLM | korunmalı — **regresyon kapısı** |
| 9·T1 | `personel verimliliklerini kıyasla` | 🔴 *"toplam agirlik kg çıkarabilirim"* | ya doğru ölçü ya **sınır beyanı** |
| 9·T2 | `gelecek ay ciro tahmini` | 🔴 *"hangi dönem için?"* | 🔴 **yetenek sınırı**: *"tahmin yapamıyorum"* |


---

## 18 · THREAD 10–11 — İKİ KANIT, ve oylama kusurunun CANLI GÖRÜNTÜSÜ

### 18.1 · 🔴🔴 OY PAYDASI KUSURU CANLI İZDE GÖRÜNDÜ

```
soru : "işler nasıl gidiyor bu ay"
iz   : Intent-path: self-consistency uyuşmazlığı (%50 uyum / 3 örnek, eksen=measures)
       → netleştirme
note : "Hangi ölçüyü istiyorsun?"
süre : 41 565 ms
```

🔴 **`%50 uyum / 3 örnek` matematiksel olarak İMKÂNSIZDIR** — payda 3 olsaydı olası
değerler `%33` · `%67` · `%100`'dür. `%50` yalnız **payda 2** iken çıkar.

> Yani üç örnekten **biri `{cube:null}` döndü ve paydadan DÜŞTÜ**. §2.1'de kaynak
> okunarak bulunan kusur, burada **üretim izinde** görünüyor.

⊙ Bu, oylama kusurunun **teorik değil ölçülmüş** olduğunun kanıtıdır — ve bu vakada
lehimize çalıştı (netleştirmeye düştü). Ters yönde çalıştığında (1 cevap + 2 çekimser →
**%100 uyum**) sistem en şüpheli anında **en emin** görünecek.

⚠ Ve maliyet: `consistency_k=3` → **üç** LLM çağrısı → **41,5 sn** — sonuç yalnız
*"Hangi ölçüyü istiyorsun?"*.

### 18.2 · 🔴 `iyi mi kötü mü` — yargı sınırı yine konuşmadı

```
iz   : Intent-path: dönem belirsiz → netleştirme (LLM'siz)
note : "ort oee çıkarabilirim — hangi dönem için?"
```

Kullanıcı **yargı** istedi (*iyi mi kötü mü*); sistemde eşik/hedef yok. Yine netleştirme
fırladı ve **ölçü + dönem** sordu. `KUSUR D`'nin (§17.4) ikinci örneği: **sınır beyanı
merdivenin çok altında.**

### 18.3 · ✅✅ `peki` TEŞHİSİ KONTROLLÜ KARŞILAŞTIRMAYLA KANITLANDI

Thread 11, aynı oturumda, aynı bağlaçla iki soru:

| soru | katalog terimi | `source` | sonuç |
|---|---|---|---|
| `peki bu neden düşük` *(T7)* | **yok** | 🔴 `meta` | **"Görüşürüz!"** |
| `peki fire ne durumda` *(T11)* | **`fire`** ✅ | 🟢 `cube` | `refine → deterministik` ✅ |

> 🔴 **Teşhis kesinleşti:** `peki` tek başına kusur değil. Kusur, **veri sinyalinin
> yalnız kelimelerden** aranmasında: cümlede katalog terimi yoksa sosyal sınıf kazanıyor —
> **istekte önceki turun `cube_query`'si dursa bile.**

*Bir takip sorusu, tanımı gereği kendi terimlerini taşımaz; onları bir önceki tur taşır.*

### 18.4 · ✅ Sosyal sınıf DOĞRU çalıştığında

```
soru : "teşekkürler"   (thread içinde, cube_query elde)
iz   : sosyal sınıf (tesekkur) → deterministik yanıt (LLM'siz, sıfır maliyet)
note : "Rica ederim. Başka neye bakmak istersin?"  ·  418 ms · 3 öneri
```

✅ `D1` amacına uygun çalışıyor: 0 LLM, 0 SQL, 418 ms, üstüne devam önerileri.
🔴 Sorun sınıfın **varlığı** değil, **sınırı**.

### 18.5 · ✅ Belirsizlik beyanı takip turunda da korunuyor

`peki fire ne durumda` → *"«fire» birden fazla yerde tanımlı — bu cevap **OEE**
tanımıyla hesaplandı. Diğerleri: fire (parti)."* — thread içinde de sessiz seçim **yok**.

---

## 19 · TOPLAM BİLANÇO — 11 thread · 24 tur · canlı API

### 19.1 · Bulunan kusurlar, ağırlık sırasına göre

| # | kusur | kanıt | sınıf |
|---|---|---|---|
| **A** | 🔴🔴 Kök-neden sorusu **VEDA** sanıldı | `peki bu neden düşük` → *"Görüşürüz!"* · 371 ms · 0 LLM | **sessiz-yanlış** |
| **B** | 🔴🔴 Anlatıcı LLM her cevaba biniyor | sürenin **%54–%93'ü**; `çeyreklere böl` **69 399 ms** | **performans** |
| **C** | 🔴 Yetenek sınırı atlanıyor | `gelecek ay ciro tahmini` → *"hangi dönem için?"* · `iyi mi kötü mü` → *"ort oee"* | **sessiz-yanlış adayı** |
| **D** | 🔴 VQR **eksik** cevabı önbellekliyor | `source=vqr` · `eksik_niyet=['kiyas','trend']` | **kalıcılaşan eksik** |
| **E** | 🔴 Oy paydası çekimserleri düşürüyor | üretim izi: *"%50 uyum / **3 örnek**"* | **kalibrasyon** |
| **F** | 🔴 Netleştirme **alakasız ölçü** öneriyor | `personel verimliliklerini kıyasla` → *"toplam agirlik kg"* | **yanlış yönlendirme** |
| **G** | ⚠ Bozuk JSON yanıtı | `bu neden düşük` → kontrol karakteri | **protokol** |
| **H** | ⚠ Sağlayıcı gecikmesi salınıyor | `deepseek-v4-flash` 2,9 → 22,6 → **69,4 sn** | **altyapı** |

### 19.2 · ✅ Doğrulanan iyi davranışlar — regresyon kapısı hak ediyor

| davranış | kanıt |
|---|---|
| Belirsizlik beyanı *(taze **ve** takip)* | *"«fire» birden fazla yerde tanımlı — bu cevap OEE tanımıyla"* |
| Boş sonuç dürüstlüğü | *"Rapor doğru kuruldu — elimdeki veri 01.01.2024–30.06.2026"* |
| Çapraz-cube harman | `bir de ciro ekle` → iki ölçü, **0 LLM** |
| Kök-neden analizi | `neden bu kadar fark var` → katkı segmentleri, **0 LLM** |
| Sosyal sınıf *(yerinde)* | `teşekkürler` → **418 ms**, 3 öneri |
| Kıyas eksiğini **beyan etme** | `ocak ve haziran…` → `eksik_niyet=['kiyas']` + açıklama |
| Takip düzenlemesi | `en düşük hangisi` · `aylara göre` · `en yüksek 5` → hepsi **deterministik** |

### 19.3 · 🔴 EN ÖNEMLİ TEK CÜMLE

> **Sistemin çevirisi bozuk değil — sistemin KONUŞMASI bozuk.**
> Intent 24 turun 20'sinde deterministik çözüldü. Kaybedilen şey ya **hız** (anlatıcı),
> ya **sınırın söylenmesi** (yetenek kapısı geç), ya **bağlamın kullanılması** (`peki`),
> ya **kalibrasyon** (oy paydası) — dördü de çeviriden **sonraki** katmanlar.


---

*Ölçüm kaynakları: `app/cube_router.py` (anahtar taraması · `parse_cube_query` ·
`_measure_threshold` · `_top_n` · marjinler `:908`·`:932`·`:937`·`:947`) ·
`app/intent_semasi.py` (şema alanları) · `app/llm.py` (`_cube_select_system` ↔
`_cube_refine_user`) · `app/uyum.py:212` · `app/routers/ask.py:2080`·`2194`·`2509`·`2734`·`2895` ·
`demo/packs/starters.yml` (10 chip, route ölçümü) · **canlı koşum** (`:8001`, tenant `boyahane`, 2 tur, konteyner logları) · `lab/reports/gercek_dunya.md`
(2285 vaka · kademe kırılımı) · canlı Intent turu (9 çağrı).*

---

## 20 · YENİ SENARYO TURU — `T-A` · `T-B` (curl, taze konteyner, tek tek)

> ✅ Önceki sekiz kusurdan **yedisi doğrulandı kapandı** (§20.0). Bu bölüm **yeni**
> senaryolarla bulunan **dört** kusuru taşıyor.

### 20.0 · Kapanan kusurların CANLI doğrulaması

| # | önce | **sonra (curl)** |
|---|---|---|
| **A** | `peki bu neden düşük` → *"Görüşürüz!"* | ✅ *"cevap üstünde konuşma"* + `ort_oee` ortalama uyarısı |
| **B** | `makine bazında oee son 3 ay` **5.420 ms** | ✅ **1.190 ms** · log: `T2 ŞABLON: LLM çağrısı YAPILMADI` |
| **B** | takip `aylara göre` 🔴 **24.285 ms** | ✅ **503 ms** — **48×** |
| **C** | `gelecek ay ciro tahmini` → *"hangi dönem?"*, sonra `cube+llm` **30 satır** | ✅ *"forecast v1'de yok"* · **1.008 ms** |
| **C/2** | `iyi miyiz kötü müyüz` → *"ort oee… hangi dönem?"* | ✅ *"eşik uydurmam"* · **1.536 ms** |
| **D** | VQR eksik cevabı dondurdu | ✅ tamamen kapatıldı (`vqr_acik=False`) |
| **H** | 69.399 ms'e kadar salınım | ✅ 8 sn tavan — aşımda **anlatı düşer, cevap yaşar** |

🔴 Ve bir kusuru **düzeltmenin kendisi doğurdu**: `§AJ3` modeli istekli yapınca
*"gelecek ay ciro tahmini"* `cube+llm` ile **30 satır geçmiş veri** döndü. Sınır üç dala
birden taşındı (LLM'den önce · kısmi-anlama · dönem netleştirmesi), sözleşme **tek**.

### 20.1 · `T-A` — kümülatif thread (4 tur)

| tur | soru | sonuç |
|---|---|---|
| 1 | `bu yıl toplam ciro` | ✅ `gte 2026-01-01` · 0 LLM · **510 ms** |
| 2 | `müşteri bazında göster` | ✅ dönem **korundu**, boyut eklendi · **431 ms** |
| 3 | `en yüksek 3 tanesi` | 🔴 **iki kusur** — aşağıda |
| 4 | `geçen yıla göre nasıl` | 🔴 kıyas **koştu ama söylenmedi** |

### 20.2 · 🔴 KUSUR I — deterministik takip LLM'e düştü (**23,5 sn**)

```
"en yüksek 3 tanesi"  →  source=cube+llm · 23 489 ms
iz: "Takip: LLM-destekli yapısal düzenleme"
    "niyet: tür=ustunluk · üstünlük=3 · bilinmeyen=tanesi"
```

⊙ **Ayrıştırıcı çalışıyor** — doğrudan ölçüldü: `_top_n("en yuksek 3 tanesi")` → **3**.
Ve tüketici de var: `deterministic_refine:1346` `cq["limit"]`'i tam bu durumda kuruyor.

🔴 Yani kusur ne ayrıştırıcıda ne tüketicide — **çağrı koşulunda**: `bilinmeyen=tanesi`
bir kapsam kapısını kapatıp refine'ı erken düşürüyor olabilir. *Bir yolun iki ucu da
çalışırken yol çalışmıyorsa, kusur uçlarda değil kapıdadır.*

### 20.3 · 🔴 KUSUR J — `limit` var, `order` YOK (tekrarlanabilirlik)

Aynı turun çıktısı: `{… "limit": 3}` — **`order` yok**. Bugün doğru satırlar geldi, ama
kayıtlı sorgu bir daha koşulduğunda (`/cube` chip'i · pano · zamanlanmış rapor)
**başka üç satır** dönebilir.

🔴 Ve bu `contracts.py`'nin *"SQL farklı → TANIM DEĞİŞTİ"* alarmını **yanlış** ateşler.
*Sıralamasız bir limit, sonucu değil kuyruğu keser.*

### 20.4 · 🔴 KUSUR K — kıyas KOŞTU ama SÖYLENMEDİ

```
"geçen yıla göre nasıl"  →  iz: "Takip: dönemsel kıyas (yoy, LLM'siz)"  ✅
summary: (bir önceki turla BİREBİR AYNI)                                 🔴
niyet  : 🔴temsil-yok=kiyas                                              🔴
```

Kullanıcı *"geçen yıla göre nasıl"* diye sordu; sorgu kıyası **kurdu**, `interpret()`
özeti **kıyastan hiç söz etmedi** ve `eksik_niyet` de boş — yani ne cevap ne beyan.

🔴 En sinsi biçim: sistem **doğru olanı yaptı** ve **söylemedi**.
*Hesaplanan ama söylenmeyen bir kıyas, hesaplanmamış bir kıyastan ayırt edilemez.*

### 20.5 · 🔴 KUSUR L — eşik ayrıştırıldı, uygulanmadı

```
"bu yıl 5 milyon üzeri ciro yapan müşteriler"
→ cq'da `measure_having` YOK · eksik_niyet=['esik'] · 8 satır (hepsi)
```

⊙ Ayrıştırıcı **çalışıyor**: `_measure_threshold(...)` → `{'op': '>', 'value': 5000000.0}`.
Ve tüketici de var: `route():3651` `cq["measure_having"]`'i kuruyor.

⚠ Beyan **dürüst** (*"eşiği ölçü adıyla yaz"*) — ama yanlış: ölçü adı **zaten** cümlede
(*"ciro yapan"*). Yani sistem kullanıcıya, kullanıcının **zaten yaptığı** şeyi öneriyor.

*Bir çözüm önerisi, kullanıcının hâlihazırda denediği şeyse, öneri değil bir yankıdır.*

### 20.6 · Sıradaki döngü — kök neden sırası

`I` ve `L` **aynı sınıf**: ayrıştırıcı ✅ · tüketici ✅ · **çağrı koşulu** 🔴. Önce o
koşullar okunmalı (`_coverage_ok` · `bilinmeyen` kapıları), sonra `K` (özetin kıyası
görmesi), sonra `J` (`limit`→`order` eşleşmesi).

---

## 21 · 🔴🔴 KÖK NEDEN BULUNDU — *"bağlam 2. turdan sonra kopuyor"*

> **Kullanıcının şikâyeti birebir üretildi** ve tek bir satırda çözüldü. Bu bölüm
> kanıtlarıyla eksiksizdir: bağlam kaybolsa bile buradan devam edilebilir.

### 21.1 · Üretim — `T-C` threadi, curl, tek tek

| tur | soru | sonuç | süre |
|---|---|---|---|
| 1 | `bu yıl toplam ciro` | ✅ `cube` · `gte 2026-01-01` | 510 ms |
| 2 | `müşteri bazında göster` | ✅ `cube` · dönem korundu + `dimensions:[musteri]` | 431 ms |
| 3 | `en yüksek 3 ünü getir` | 🔴 **`source=None` · `cq={}`** | 3 325 ms |

Turun tam çıktısı:

```
note : "Bu takip mesajını önceki raporla ilişkilendiremedim. Yeni bir soru olarak sorar mısın?"
iz   : "Takip: deterministik/LLM düzenleme tükendi → dürüst ret"
       "niyet: tür=ustunluk · üstünlük=3 · bilinmeyen=unu"
```

🔴 **`bilinmeyen=unu`** — kök neden bu üç karakter.

### 21.2 · Kanıt: ayrıştırıcı ÇALIŞIYOR, kapı ÖLDÜRÜYOR

Doğrudan ölçüldü (izole konteyner, `cube_router` üzerinde):

```
'en yuksek 3 unu getir'  →  _top_n = 3     ✅
'en yuksek 3 tanesi'     →  _top_n = 3     ✅
'en yuksek 3 unu'        →  _top_n = 3     ✅
'ilk 3 unu'              →  _top_n = 3     ✅
```

Ve tüketici de yerinde: `deterministic_refine:1346` tam bu durumda `cq["limit"]`'i kurar.

> 🔴 Yani sayı **okunuyor**, limit **kurulabiliyor** — ama tur `unu` kelimesi yüzünden
> kapsam kapısından geçemiyor ve **tüm takip zinciri** düşüyor.

*Bir yolun iki ucu da çalışırken yol çalışmıyorsa, kusur uçlarda değil kapıdadır.*

### 21.3 · Ve emsal KODUN İÇİNDE duruyor

`cube_router:3636-3638` — eşik için **tam bu bağışıklık** zaten yazılmış:

```python
having = _measure_threshold(q)
if having:
    known |= _gecenler(q, _TH_WORDS)     # eşik kelimeleri KAPSAMDAN SAYILIR
```

🔴 Aynı bağışıklık **`_top_n` için verilmemiş**. Sabitler hazır: `_TOPN_CUE` mevcut.

⊙ Bu, `§20.2` (`I` — *"en yüksek 3 tanesi"* 23,5 sn) ve `§20.5` (`L` — eşik uygulanmadı)
kusurlarının da **aynı sınıfı**: ayrıştırıcı ✅ · tüketici ✅ · **kapsam kapısı** 🔴.

### 21.4 · Türkçe boyutu — `ocağa` ile AYNI ders

`3'ünü` → normalize `3 unu`. Ek (`-ünü`) sayıdan koparak **bağımsız bir kelime** oluyor ve
katalogda karşılığı olmadığı için *"bilinmeyen"* sayılıyor. `ocak`+ünlü → `ocağa` vakasının
(§`Ö10`) birebir kardeşi: **çekim eki, kapsam kapısını tetikliyor.**

⚠ Ek üretiminin sahibi `app/ek.py` (G7) — **üretiyor ama sökmüyor**. Sökme tarafı bu
depoda üç kez ısırdı: `ocağa` · `3'ünü` · `çeyreklere`.

*Bir dilin eklerini üretebilen sistem, onları sökebilmelidir de; yoksa kendi ürettiği
biçimi tanımaz.*

### 21.5 · 🔴 DÜZELTME REÇETESİ (sonraki tur — kanıtlarıyla hazır)

1. `_top_n` eşleştiğinde `known |= _gecenler(q, _TOPN_CUE)` — **eşiğin emsaliyle
   birebir aynı desen**, yeni sözlük yok.
2. Sayıya bitişen çekim ekini (`3 unu` · `3 tanesi` · `5 ini`) kapsam kapısında **sayının
   parçası** say — bir sayıyı okuyabilen kapı, onun ekini de tanımalı.
3. `§20.3` (`limit` var `order` yok) aynı turda kapanmalı: `_top_n` bir **sıralama
   niyeti**dir; limit kurulurken `order` da kurulmalı.
4. Sonra `§20.4` (kıyas koştu ama söylenmedi) ve `§20.5` (eşik).

### 21.6 · ⚠ YENİ SENARYO SINIFI — kök-neden ANLATIMI (henüz test edilmedi)

Kullanıcının talebi, kayda geçiyor:

> *"OEE istedin, RAM-3 düşük geldi. «Neden düşük» deyince gerçekten analiz yapmasa bile
> diğerlerine oranla düşük çıkmasına sebep olan kök nedenleri **listeleyebilmeli,
> sunabilmeli, anlatabilmeli**: «vardiya 1'de mal beklediği için hep geç başlamış» gibi."*

⊙ Bugünkü davranış (§20 T-A/1 turu): *"`ort_oee` bir ortalama/oran — parçaların toplamı
bütünü vermez — katkı payı matematiksel olarak tanımsız"*. **Dürüst ama yetersiz**:
ortalama için katkı payı gerçekten tanımsızdır, ama *"neden düşük"* sorusunun cevabı
katkı payı **değildir** — kırılım karşılaştırmasıdır (vardiya · duruş nedeni · hat).

🔴 Yani sınır **doğru yerde ama fazla geniş**: hesaplanamayan şey `contribution`, ama
`drill.py` + `makine_duruslari` + `oee.dimensions` ile *"RAM-3'ü ötekilerden ayıran
boyut hangisi"* **deterministik olarak** yanıtlanabilir.

**Sonraki tur bunu senaryo olarak koşacak** ve ölçecek.

---

## 22 · TUR 2 — ortam bulguları ve ilk iki senaryo

### 22.1 · ⚠ İKİ ORTAM ENGELİ — bulgu sanılmasın diye kayıtta

| | belirti | gerçek |
|---|---|---|
| `{"detail":"Geçersiz veya süresi dolmuş token"}` · **8 ms** | ürün kusuru gibi | 🔴 **token 15 dk'da doldu** — yeniden login |
| `openrouter … 402 Client Error: Payment Required` | LLM sessiz | 🔴 **kredi bitti** → `.env`'de `DIMA_LLM_PROVIDER=gemini` |

⚠ Ölü bir sağlayıcıyla ölçülen tur, ürünün davranışını değil **faturayı** ölçer.
`gemini-flash-lite-latest` ile devam edildi (**1.028–3.102 ms** — OpenRouter'ın
2,9/22,6/69,4 sn salınımına karşı **kararlı**; `H` kusuru bu sağlayıcıda görünmüyor).

### 22.2 · 🔴 KUSUR M — fiil çekimi turu öldürüyor (`I`/`L`/`§21` ile AYNI SINIF)

```
"geçen ay kaç parti üretildi"
→ src=None · cq={} · 4 330 ms
  not: "«uretildi» kısmını anlayamadım, bu yüzden rapor düşülmedi."
  iz : "Intent-path: kısmi anlama → rapor düşülmedi, netleştirme (LLM'siz)"
```

🔴 `uretildi` — `üretim`in **çekimli fiil hâli**. Katalogda `uretim`/`uretilen` var,
`uretildi` yok → kapsam kapısı turu düşürüyor.

⊙ Bu **dördüncü** kez: `ocağa` (§Ö10) · `3'ünü` (§21) · `çeyreklere` · şimdi `üretildi`.
Dördü de aynı sınıf: **çekim eki, kapsam kapısını tetikliyor.**

*Bir dilin eklerini üretebilen sistem (`app/ek.py`), onları sökebilmelidir de.*

### 22.3 · ✅ S2 — doğru davranış

```
"en çok fire veren makine"
→ cq={oee · toplam_fire_kg · dimensions:[makine]} · not: "hangi dönem için?"
```

✅ Ölçü **ve** kırılım doğru çözüldü; dönem yokken **sormak** doğru (`ADR-0007-K3`).
⚠ *"en çok"* niyeti `cq`'ya `order` olarak **girmedi** — `§20.3`'ün (`J`) kardeşi:
sıralama niyeti okunuyor, sorguya yazılmıyor.

### 22.4 · 🔴 BİRLEŞİK TEŞHİS — beş kusur, TEK kök

`I` (`3 tanesi`) · `L` (`5 milyon üzeri`) · `§21` (`3'ünü`) · `M` (`üretildi`) ·
kısmen `J` (`order` yazılmıyor):

> **Ayrıştırıcı ✅ · tüketici ✅ · kapsam kapısı 🔴.**
> `_top_n`, `_measure_threshold`, ölçü eşleştirmesi — hepsi doğru çalışıyor. Tur,
> ayrıştırıcının **zaten tükettiği** kelime *"bilinmeyen"* sayıldığı için ölüyor.

🔴 **Emsal kodun içinde**: `cube_router:3636` eşik için bu bağışıklığı **zaten** veriyor
(`known |= _gecenler(q, _TH_WORDS)`). Kural genelleştirilmeli:

> **Bir ayrıştırıcı bir kelimeyi tükettiyse, o kelime kapsam kapısında BİLİNMEYEN
> sayılamaz.**

Bu tek kural beş kusuru birden kapatır ve **yeni sözlük gerektirmez**.

### 22.5 · S3 ✅ · S4 🔴🔴 — iki ağır bulgu

```
S3  "mart ayında toplam ciro"
    ✅ cube · 2026-03-01..03-31 · ₺11.974.792,05 · 0 LLM · 1 042 ms
```

```
S4  "şubatta ciro ocağa göre nasıl değişti"
    🔴 src=None · cq={} · 99 386 ms
    not: "«ocaga degisti» kısmını anlayamadım"
    log: openrouter … 74 919 ms  ·  openrouter … 98 176 ms
```

#### 🔴 KUSUR N — Intent çağrısının ZAMAN SINIRI YOK (**98 sn**)

`§H` için konan bütçe (8 sn) **yalnız anlatıcıyı** kapsıyor. Intent-JSON çağrısı
sınırsız: ölçülen **98.176 ms**. Bir kullanıcı 1,5 dakika bekliyor ve sonunda
*"anlayamadım"* alıyor.

🔴 Ve bu **döngünün kendisini** engelliyor: senaryo turu sağlayıcının salınımına esir.

*Bir bütçeyi yalnız bir basamağa koymak, ötekini sınırsız ilan etmektir.*

#### 🔴 KUSUR O — `ocaga` ALTINCI kez aynı sınıf

`Ö10` ile `_MONTH_ALT`'a `oca[kğ]` eklendi ve `date_filters` artık `ocaga`'yı **çözüyor**.
Ama kapsam kapısı onu hâlâ **bilinmeyen** sayıyor → tur ölüyor.

⊙ Aynı kök, **altıncı** örnek: `ocağa` · `3'ünü` · `çeyreklere` · `üretildi` ·
`3 tanesi` · `5 milyon üzeri`.

> 🔴 **§22.4'ün tek kuralı bunların HEPSİNİ kapatır:**
> *Bir ayrıştırıcı bir kelimeyi tükettiyse, o kelime kapsam kapısında BİLİNMEYEN
> sayılamaz.*

⚠ Ve dikkat: `Ö10` düzeltmesi `niyet`i onardı (kırılım yanlış beyanı bitti) ama **turu
kurtarmadı** — çünkü kusur `niyet`te değil **kapsam kapısındaydı**. *Bir kusuru doğru
teşhis edip yanlış katmanda düzeltmek, onu ikinci kez bulmayı gerektirir.*

---

## 23 · 🔴🔴 `T-N` — *"yıkama neden yüksek"* · frontta **500**'ün kökü

> curl, taze konteyner, **tek tek** koşuldu. Kullanıcının canlıda gördüğü
> `Request failed with status code 500` burada birebir üretildi.

### 23.1 · Turlar

```
n1/1  "aşama bazında toplam fire"
      ✅ cq={parti · toplam_fire_kg · dimensions:[asama]} · not:"hangi dönem için?" · 489 ms

n1/2  "bu yıl"
      ✅ src=cube · 6 satır · gte 2026-01-01
      özt: "En yüksek aşama: YIKAMA (113.840,10 kg, toplamın %25.0'i)…" · 487 ms

n1/3  "yıkama neden yüksek"
      🔴 src=llm:openrouter · cq={"cube":"adhoc"} · 78 834 ms
      iz : "Discovery: ham-SQL üretimi (Intent-path kapsamadı)"
```

### 23.2 · 🔴 KUSUR P — frontta 500'ün sebebi **süre**, hata değil

Kullanıcının paylaştığı canlı logda kritik ayrıntı: `POST /ask … 200 OK` satırı
**HİÇ YOK**. Backend `CEVAP` yazdı (36 835 ms), ama erişim satırı yazılmadı — yani
**istemci çoktan kopmuştu**.

🔴 Yani **500 backend'den çıkmıyor**: cevap 36–79 saniye sürüyor, Next rewrite-proxy
vazgeçiyor ve ön yüz onu *"sunucu hatası"* diye gösteriyor.

*Bir cevabın geç gelmesi, kullanıcı için gelmemesiyle aynıdır — ve hata mesajı yanlış
yeri işaret eder.*

### 23.3 · 🔴 KUSUR R — *"neden"* sorusu Discovery'ye düşüyor

`TUR_NEDEN` sınıflandırıcısı **var** ve çalışıyor:

| soru | sınıf |
|---|---|
| `neden yüksek` | ✅ `neden` |
| `bu neden yüksek` | ✅ `neden` |
| `yıkama neden bu kadar yüksek` | ✅ `neden` |
| 🔴 **`yıkama neden yüksek`** | **`None`** |

⊙ Fark: başta bir **segment değeri** (`yıkama`) var ve sınıflandırıcı onu tanımıyor →
tur `TUR_NEDEN`'e girmiyor → Intent kapsamıyor → **Discovery** (ham SQL, en pahalı ve en
az güvenilen basamak).

🔴 **Yedinci kez aynı sınıf**: sistemin **çözebildiği** bir kelime (burada bir boyut
değeri) bir kapıda **tanınmadığı** için tur yanlış yola gidiyor.
(`ocağa` · `3'ünü` · `çeyreklere` · `üretildi` · `3 tanesi` · `5 milyon üzeri` · `yıkama`)

### 23.4 · ⚠ Ve cevabın kendisi ASLINDA doğruydu

```
özt: "En yüksek neden: Malzeme/Parti Bekleme (14.019, toplamın %84.7'i).
      En düşük: Enerji Kesintisi (95); 6 kalem."
```

🔴 Bu **tam olarak** kullanıcının istediği kök-neden anlatımı (*"vardiya 1'de mal
beklediği için…"*). Ama:

* **78,8 saniyede** geldi (proxy kopar → 500),
* `cube=adhoc` — yani **ham SQL**, doğrulanmış küp değil,
* ve `duruş nedeni` kırılımı **deterministik olarak zaten mümkün**
  (`makine_duruslari` cube'u · `drill.py` · `contribution.py`).

> **Sistem doğru cevabı biliyor ve onu en pahalı, en yavaş, en az güvenilen yoldan
> alıyor.** Kullanıcının kuralı burada birebir geçerli: *"cevabı sistem verecek, LLM
> sadece garson."*

### 23.5 · Düzeltme sırası (kanıtlarıyla hazır)

1. **`yıkama neden yüksek` → `TUR_NEDEN`**: sınıflandırıcı, önündeki **boyut değerini**
   dolgu saymalı — `§22.4`'ün kuralının yedinci uygulaması.
2. **`TUR_NEDEN` deterministik kalsın**: `contribution`/`drill` ile duruş-nedeni
   kırılımı, **0 LLM**. Ölçüm: bugünkü 78,8 sn → beklenen **< 1 sn**.
3. **Ön yüz zaman aşımı**: `apiClient`'ta tanımlı değil; 20 sn'lik Intent bütçesi bile
   proxy'yi kurtarmayabilir — sınır ön yüzde de olmalı.

---

## 24 · TUR 2 BİLANÇOSU — 8 senaryo · 1 düzeltme · **77× hızlanma**

### 24.1 · Senaryo tablosu (curl, tek tek, taze konteyner)

| # | senaryo | sonuç | süre |
|---|---|---|---|
| s1 | `geçen ay kaç parti üretildi` | 🔴 `üretildi` bilinmeyen | 4 330 ms |
| s2 | `en çok fire veren makine` | ✅ ölçü+kırılım doğru, dönem sorar | 1 954 ms |
| s3 | `mart ayında toplam ciro` | ✅ `2026-03-01..03-31` · 0 LLM | 1 042 ms |
| s5 | `bu yıl hangi müşteri en çok iade etti` | 🔴 `hangi`/`etti` bilinmeyen | — |
| s6 | `geçen çeyrek toplam fire` | 🔴 çeyrek **dönem sayılmadı** | — |
| s7 | `bu ay makine bazında duruş süresi` | ✅ boş-sonuç dürüstlüğü | — |
| s8/1 | `bu yıl vardiya bazında oee` | ✅ 3 satır | — |
| s8/2 | `en düşük hangisi` | ✅ `order` kuruldu · 0 LLM | — |
| s8/3 | `3. vardiya neden düşük` | 🔴 **54 231 ms** · 0 satır (LLM yanlış filtre) | 54 231 ms |
| n1/3 | `yıkama neden yüksek` | 🔴 **78 834 ms** · `cube=adhoc` | 78 834 ms |

### 24.2 · ✅ DÜZELTME — *"neden"* soruları artık deterministik

**Kök neden:** `TUR_NEDEN` bir **işaret zamiri** istiyordu. `yıkama neden yüksek` ve
`3. vardiya neden düşük` zamir taşımıyor — oysa raporun **bir satırını adlandırıyorlar**.
Ve *"yüksek/düşük"* zaten bir **karşılaştırma**: neye göre? Ekranda durana göre.

> *Bir cümleyi eldeki cevaba bağlayan tek şey zamir değildir; bir karşılaştırma da
> bağlar — çünkü karşılaştırmanın öteki ucu zaten ekrandadır.*

**Curl doğrulaması (aynı senaryo, yeniden derlenmiş konteyner):**

```
"yıkama neden yüksek"
önce  🔴 llm:openrouter · cube=adhoc · 78 834 ms → proxy kopar → frontta 500
sonra ✅ "Takip: üçüncü sınıf → cevap üstünde konuşma (neden, LLM'siz)" · 1 018 ms
      not: "Değişimi en çok sürükleyen segmentler aşağıda — her biri tıklanınca
            tek başına açılır ve kendi kanıtını üretir."
```

🔴 **77× hızlandı ve cevabı artık SİSTEM veriyor** — *"LLM sadece garson."*

### 24.3 · ⚠ Kapı kuralı bir kez DARALTTI

İlk hâli fazla genişti: `test_UZUN_neden_sorusu_ZAMIR_ister` kırmızı verdi —
*"fire oranı neden yüksek olur genel olarak"* bir **yeni konudur**, takip değil.
Sınır `_kisa_soru`'nun **kendi ölçüsüyle** daraltıldı (2 → 4 kelime).

*Bir gevşemeyi, gevşettiği kuralın kendi ölçüsüyle sınırlamak, ikinci bir kural yazmaktan
güvenlidir.*

### 24.4 · 🔴 KALAN ÜÇ KUSUR — hepsi AYNI SINIF (sekizinci–onuncu örnek)

| soru | tanınmayan | sistem bunu çözebiliyor mu |
|---|---|---|
| `geçen ay kaç parti üretildi` | `üretildi` | ✅ `uretim` katalogda |
| `hangi müşteri en çok iade etti` | `hangi`·`etti` | ✅ `iade` bir ölçü |
| `geçen çeyrek toplam fire` | çeyrek dönemi | ✅ `_quarter_period_filters` var |

> **Bir ayrıştırıcı bir kelimeyi tükettiyse, o kelime kapsam kapısında BİLİNMEYEN
> sayılamaz** — kural iki kapıda uygulandı (`route()` · `deterministic_refine`), ama
> **fiil çekimleri ve soru sözcükleri** için henüz uygulanmadı.

🔴 Sıradaki tur bunu ele alacak: `üretildi`/`etti` gibi **fiil** biçimleri ve `hangi`
gibi **soru sözcükleri** dolgu sınıfına girmeli — `_LISTE_RE`/`rm_verb_words` için zaten
var olan desenin genişletilmesi, yeni sözlük değil.

### 24.5 · ⚠ ÖZ-DENETİM — son düzeltme KÖK ÇÖZÜM DEĞİL, kısmi

Kullanıcının kuralı: **kök neden ve kök çözüm; tikel çözüm yasak.** Bu ölçüte göre
`§24.2`'nin düzeltmesi **geçer not almıyor**:

```python
_KARSILASTIRMA = ("yuksek", "dusuk", "fazla", "az", "kotu", "iyi", …)   # 🔴 KELİME LİSTESİ
_KARSILASTIRMA_AZAMI_KELIME = 4                                         # 🔴 EŞİK
```

🔴 Bu bir **liste + eşik**, yani tam olarak `ADR-0008`'in yasakladığı biçim. Bugün
çalışıyor ama *"yıkama neden geride kaldı"*, *"3. vardiya neden zayıf"*, *"bu aşama neden
sorunlu"* yine düşer — ve her biri listeye bir kelime daha eklettirir.

#### Kök çözüm — yapısal, ve zaten elimizde

Takip sorusunu eldeki cevaba bağlayan şey **zamir ya da sıfat değil**, sorunun
**ekrandaki raporun bir satırını adlandırması**dır:

| soru | bağ |
|---|---|
| `yıkama neden yüksek` | `yıkama` ∈ `asama` değerleri **(mevcut raporun kırılımı)** |
| `3. vardiya neden düşük` | `3. Vardiya (00-08)` ∈ `vardiya` değerleri |
| `fire oranı neden yüksek olur genel olarak` | `fire oranı` bir **ölçü adı** → bağ YOK |

> **Kural:** bir takip sorusu, mevcut raporun **kırılım değerlerinden birini** anıyorsa
> bağlıdır — zamire de sıfata da gerek yoktur. Bir **ölçü adını** anıyorsa yeni konudur.

⊙ Bu ayrım *"genel olarak"* sorusunu da **kendiliğinden** dışarıda bırakır — uzunluk
eşiğine gerek kalmaz.

⚠ Gereken veri **zaten var**: `cube_query.dimensions` + katalogun `dimension_values`'ı
(`value_index` bunu okuyor). Yani kök çözüm yeni bir sözlük değil, **var olan bir
kaynağın ikinci tüketicisi**.

*Bir kusuru gördüğü yerde yamamak, sınıfını görmemenin en pahalı biçimidir: her yeni
örnek yeni bir yama ister ve yamalar birbirini tanımaz.*

🔴 **Sıradaki tur bunu uygulayacak** ve `_KARSILASTIRMA` listesi **silinecek**.

### 24.6 · ✅ KÖK ÇÖZÜM İNDİ — kelime listesi silindi, curl doğruladı

```
"yıkama neden geride kaldı"        ← eski KELİME LİSTESİNDE YOKTU
önce  🔴 cube+llm · "LLM-destekli yapısal düzenleme" · 28 498 ms
sonra ✅ "cevap üstünde konuşma (neden, LLM'siz)" ·  1 778 ms · 0 LLM
```

| | önce (tikel) | sonra (kök) |
|---|---|---|
| ölçüt | `_KARSILASTIRMA` **kelime listesi** + 4-kelime eşiği | soru, kırılımın bir **DEĞERİNİ** anıyor mu |
| `yıkama neden yüksek` | ✅ | ✅ |
| `yıkama neden **geride kaldı**` | 🔴 | ✅ **liste büyümeden** |
| `fire oranı neden yüksek olur genel olarak` | eşikle elenir | **kendiliğinden** elenir (ölçü adı, değer değil) |

*Zamir "şu" der; değer **HANGİSİ** olduğunu söyler.*

#### ⚠ Ve kök çözümün kendisi bir kez YANLIŞ KAYNAKTAN okudu

İlk yazım `previous_result.rows`'u okuyordu. Curl **çalışmadığını** gösterdi:
`AskRequest`'te öyle bir alan **YOK** — istemci satırları hiç göndermiyor, yani kod her
zaman `None` alıyor ve **sessizce hiçbir şey yapıyordu**. Birim testi de geçmişti
(fikstür alanı elle veriyordu).

> *Var olmayan bir alanı okuyan kod, sessizce hiçbir şey yapar — ve testi geçer.
> Onu yalnız canlı tur yakalar.*

Doğru kaynak kataloğun `dimension_values`'ı — ve **daha iyi**: kullanıcı ikinci
sayfadaki bir satırı da adıyla anabilir; ekran görünenle sınırlıdır, katalog değil.

#### Sahiplik ve kapı

*"Ekranda ne var"* sorusunun sahibi **bağlam katmanı** (`app/context.py::capa_degerleri`);
`followup.sinifla` değerleri **alır**, okumaz (`KAT-1`). Kapı bunu **AST** ile ölçüyor —
metin taraması iki kez yanlış pozitif verdi, çünkü şerhler kararı anlatmak için o
isimleri anmak **zorunda**. *Bir kapı, koruduğu şeyin kaydını da yasaklarsa kararı siler.*

---

## 25 · TUR 3 — göreli çeyrek · kök çözüm · curl doğrulaması

### 25.1 · İzolasyon (curl, tek tek)

| soru | önce |
|---|---|
| `2. çeyrek toplam fire` | ✅ `2026-04-01..06-30` |
| `bu çeyrek toplam fire` | ⚠ **kovaya** döndü (`granularity=quarter`, 10 satır) — dönem değil |
| 🔴 `geçen çeyrek toplam fire` | **dönem hiç yok** → *"hangi dönem için?"* |

### 25.2 · Kök: bir birim, bir ailede tanınıp ötekinde tanınmıyordu

`ceyrek` bu dosyada **zaten bilinen** bir takvim birimi (`_QUARTER_RE` · `_GRAN_LADDER` ·
`mali_takvim`). Göreli dönem ailesi (`geçen ay`/`geçen yıl`/`geçen hafta`/`dün`) onu
**taşımıyordu**.

⚠ Düzeltme bir kelime eklemek **değil**, var olan **birim kümesini tutarlı kılmak**:
`ay`·`hafta`·`yil`·`gun` göreli olabiliyorsa `ceyrek` de olabilmeli.

🔴 Hesap `mali_takvim.yil_basi`'na dayanır — Ocak'ta başlamayan mali yılda da doğru
(`FAZ 2.6`'nın aynı dersi) — ve ay sonu `calendar` ile, elle `30/31` yazmadan.

*Bir birimi bir ailede tanıyıp ötekinde tanımamak, kullanıcıya dilin kurallarını değil
bizim dosya düzenimizi öğretmektir.*

### 25.3 · ✅ Curl doğrulaması

```
"geçen çeyrek toplam fire"
önce  🔴 src=None · "toplam fire kg çıkarabilirim — hangi dönem için?"
sonra ✅ src=cube · dönem filtresi kuruldu · 1 satır
```

Kapı: `tests/test_goreli_ceyrek.py` (5) — üç aylık pencere · mali yıl bağı ·
ordinal çeyreğin bozulmadığı · birim kümesinin tutarlılığı.

### 25.4 · Kalan iki kusur (aynı sınıf, sıradaki tur)

| soru | tanınmayan |
|---|---|
| `geçen ay kaç parti üretildi` | `üretildi` — **fiil çekimi** |
| `bu yıl hangi müşteri en çok iade etti` | `hangi`·`etti` — **soru sözcüğü + fiil** |

⊙ İkisi de `rm_verb_words`'ün (ölçü-çıkarma fiilleri dolgu sayılır) **kardeşi**: bir
fiil çekimi ya da soru sözcüğü, katalogda karşılığı olan bir ölçüyü **anlatan** kelimedir,
kapsamı delmemeli.

---

## 26 · 🔴🔴 MİMARİ ÖNCELİK DÜZELTİLDİ — mesele `route()` değil, **DEVİR**

> **Kullanıcı (2026-08-07):** *"Meselemiz `route`'u iyileştirmek değil aslında; `route`'un
> cevaplayamadığı **her şeyi LLM'e yıkabilmek** — bunun çok iyi çalışması. Bu olduktan
> sonra `route` iyileştirmek. Mesela bu LLM'e gitseydi zaten bu sorun çıkmazdı: küpü LLM
> çalıştırırdı, **intent LLM** yani — Discovery değil, **garson** olan."*

### 26.1 · Ve ölçüm bu önceliği DOĞRULADI — kendi düzeltmemi çürüterek

`§25.4`'ün kalan iki kusuru (`hangi`·`etti`) için dolgu sınıfını genişlettim: `hangi` bir
soru sözcüğü (`nedir`/`nasil` zaten oradaydı), `etti` bir yardımcı fiil. Gerekçe sağlamdı,
kapıları geçti, **1 435 test yeşil**.

🔴 **Korpus çürüttü:**

```
✓ korpus kapısı          %95.1 (taban %95.1) ✅
✗ gerçek-dünya korpusu   🔴 sessiz_yanlis ARTTI: 12 → 13
```

⊙ Dolgu sınıfını genişletmek, kapsam kapısını **gevşetir**; gevşeyen kapı bir soruyu daha
**yanlış cube'a** gönderdi. Yani `route()`'u daha hoşgörülü yapmanın bedeli **sessiz
yanlış**tır — ve doğruluk vetosu bunu reddeder.

**Geri alındı.** *Bir kapıyı gevşeterek kazanılan kapsam, kaybedilen doğrulukla ödenir —
ve bu takas hep aynı yöne bakar.*

### 26.2 · Doğru hedef: `route()` **temiz pes etsin**, tur LLM'e gitsin

Ölçülen kusur şu değil: *"route bunu anlayamadı"*. Şu:

```
"bu yıl hangi müşteri en çok iade etti"
iz : "Intent-path: çapraz konu (rakip cube kimliği) → netleştirme (LLM'siz)"
not: "«hangi etti» başka bir konu gibi görünüyor. Hangisini istiyorsun?"
```

🔴 `route()` pes etti — **doğru**. Ama tur **LLM'e gitmedi**: araya bir **netleştirme
dalı** girdi ve merdiveni kesti. Oysa Intent-JSON bu soruyu büyük olasılıkla çözerdi
(`iade` bir ölçü, `müşteri` bir boyut, `en çok` bir sıralama).

> **Kural:** `route()`'un pes etmesi bir **cevap** değil bir **devirdir**. Devri kesen her
> dal, sistemin en yetenekli basamağını kullanıcının önünden çekiyor demektir.

### 26.3 · Aynı sınıftan üç dal (ölçülmüş)

| dal | iz | ne yapıyor |
|---|---|---|
| çapraz konu | *"rakip cube kimliği → netleştirme"* | 🔴 LLM'den **önce** kesiyor |
| kısmi anlama | *"kısmi anlama → rapor düşülmedi"* | 🔴 aynı |
| dönem belirsiz | *"dönem belirsiz → netleştirme"* | ◐ meşru (`ADR-0007-K3`) ama sırası tartışılır |

⚠ İlk ikisi **kapsam kapısının çıktısıdır**: `route()` *"şu kelimeyi tanımadım"* diyor ve
bu, kullanıcıya **bir soru** olarak dönüyor — oysa cevabı LLM verebilir.

### 26.4 · 🔴 SIRADAKİ KÖK ÇÖZÜM (bu belgede bağlayıcı)

1. **Netleştirme dalları Intent-JSON'dan SONRA çalışsın.** `route()` pes ettiğinde tur
   **doğrudan** garsona gider; garson da çözemezse **o zaman** netleştirme.
2. Ölçüt: `iz`'de *"netleştirme (LLM'siz)"* gören her tur, **LLM hiç denenmeden**
   kesilmiş demektir — bu sayı düşmeli.
3. ⚠ Ve bunun **ön koşulu** `§AJ3`/`§AJ4`: garsonun fişi eksikken (12 anahtar ↔ 7 alan)
   devir arttıkça yanlış cevap da artabilir. Sıra: **önce fişi tamamla, sonra devri aç.**

*Bir merdivenin basamağını atlamak, o basamağı hiç yazmamakla aynı sonucu verir.*

---

## 27 · 🔴 DEVİR ZATEN AÇIK — kesen sıra DEĞİL, **LLM'in kendisi**

### 27.1 · Ölçüm sıralamayı aklıyor

`§26.2`'de *"netleştirme dalı LLM'den önce kesiyor"* diye teşhis koymuştum. **Kaynak
okundu ve yanlış çıktı**: Intent bloğu `ask.py:3018`, netleştirme `:3256` — yani Intent
**önce** koşuyor ve bayrak `ask_intent_first: beta` **açık**.

Curl (taze konteyner, tüm `§AJ2`–`§AJ4` düzeltmeleri yüklü):

```
"bu yıl hangi müşteri en çok iade etti"
src : None · cq={} · 49 782 ms
iz  : "Intent-path: çapraz konu (rakip cube kimliği) → netleştirme (LLM'siz)"
log : openrouter … 7 642 ms
      openrouter … 47 544 ms          ← LLM İKİ KEZ KOŞTU
```

🔴 **LLM çağrıldı ve `{cube:null}` döndü.** Yani devir **çalışıyor**; kaybedilen tur
garsonun **reddi**yle kayboluyor — `§AJ3`'ün red sınıfı, hâlâ açık.

> *Bir teşhisi kaynağı okumadan koymak, doğru kusuru yanlış katmanda aramaktır.*
> (`§26.2` düzeltildi; kaydı burada duruyor.)

### 27.2 · 🔴 KUSUR S — Intent bütçesi TUTMADI

`§22.5/N` ile `intent_azami_saniye = 20` konmuştu. Ölçülen: tek çağrı **47 544 ms**,
toplam istek **49 782 ms**. Bütçe **uygulanmıyor**.

⊙ Olası sebep: oylar sırayla toplanıyor (`for _f in _isler: _f.result(timeout=…)`) ve
her `result()` **kendi anından** saymaya başlıyor — yani toplam bütçe değil, **kalan oy
başına** bütçe oluyor. İlk oy 7,6 sn sürerse ikinciye 20 sn daha tanınır.

🔴 Doğru tasarım: bütçe **turun tamamına** ait olmalı — bir son tarih (`deadline`)
hesaplanıp her `result()` ona göre kısaltılmalı.

*Bir bütçeyi parça başına vermek, bütçeyi parça sayısıyla çarpmaktır.*

### 27.3 · Sıradaki iki iş (sırasıyla)

1. **`S`** — Intent bütçesi bir **son tarihe** çevrilsin (`monotonic() + azami`).
2. **`§AJ3`'ün red sınıfı** — bu soru neden reddediliyor? `iade` bir ölçü, `müşteri` bir
   boyut, `en çok` bir sıralama; şema artık `order`+`limit`+`measure_having` de tanıyor
   (`§AJ4`). Yani fiş tamam, **red hâlâ var** → prompt tarafı ölçülmeli
   (`AJ3.4` red yanlılığı · `AJ3.5` örnek sayısı).

### 27.4 · ⚠ `s5` YANLIŞ SINIFLANDIRILMIŞ — LLM'in reddi DOĞRUYMUŞ

`§24.4` ve `§27.3`'te *"`hangi müşteri en çok iade etti` — sistem bunu çözebiliyor,
`iade` bir ölçü"* yazmıştım. **Katalog okundu: yanlış.**

`iade` bu katalogda **bir ölçü değil** — yalnızca `metrik_sozlugu.yml`'de bir **yorum
satırında** geçiyor (*"iptal/iade faturada görünür"*). Yani:

* `route()`'un pes etmesi ✅ doğru
* Intent-JSON'un `{cube:null}` demesi ✅ **doğru**
* kusur yalnızca **sunumda**: *"«hangi etti» başka bir konu gibi görünüyor"* — anlamsız
  bir cümle; kullanıcıya *"**iade** diye bir ölçüm tutmuyorum"* denmeliydi.

🔴 Ders bende: *"sistem bunu çözebiliyor"* iddiasını **katalogdan doğrulamadan** yazdım
ve bir turu yanlış kusur sınıfına harcadım.

> *Bir kusuru sınıflandırmadan önce, sistemin o soruya verecek cevabı olup olmadığını
> katalogdan doğrula — yoksa doğru davranışı kusur sanarsın.*

⊙ Yeniden sınıflandırma:

| soru | eski teşhis | **doğru teşhis** |
|---|---|---|
| `hangi müşteri en çok iade etti` | 🔴 kapsam kapısı kusuru | ✅ **doğru red** · ⚠ kötü **cümle** |
| `geçen ay kaç parti üretildi` | 🔴 `üretildi` bilinmeyen | 🔴 **açık** — `uretim` katalogda var |

**Kalan gerçek iş:** red **cümlesi**. Kullanıcı *"«hangi etti» başka bir konu"* değil,
*"iade diye bir ölçüm yok; şunlar var…"* duymalı — ve o cümlenin sahibi `app/yetenek.py`
(kapasite beyanı), netleştirme değil.

---

## 28 · İKİ SORU, İKİ LİSTE — ve bütçe bir SON TARİH oldu

### 28.1 · ✅ `S` — Intent bütçesi son tarihe çevrildi

Ölçüm ilk tasarımı çürütmüştü (`§27.2`): `intent_azami_saniye=20` konulu hâlde tek çağrı
**47 544 ms**. Sebep: her oy için ayrı `result(timeout=azami)` ve her çağrı **kendi
anından** sayıyor.

*Bir bütçeyi parça başına vermek, bütçeyi parça sayısıyla çarpmaktır.*

Son tarih **gönderimden önce** hesaplanıyor — sonra hesaplamak, iş kuyrukta beklerken
geçen süreyi bütçe dışında bırakırdı. Kapı üç şartı da ölçüyor.

### 28.2 · ✅ Anlamsız red cümlesi kapandı

```
"bu yıl hangi müşteri en çok iade etti"
önce  🔴 "«hangi etti» başka bir konu gibi görünüyor. Hangisini istiyorsun?"
sonra ✅ "Birden fazla konu anlaşıldı — hangisini istiyorsun?"
```

🔴 **Kök: bir liste, iki soru.** `unknown` **kapsam kapısının** listesidir (*"kaç kelimeyi
açıklayamadım"*); kullanıcıya gösterilecek liste başka bir sorunun cevabıdır (*"neyi
anlamadım"*).

⚠ Ve kapı onları **saymak zorunda**: `hangi`/`etti`'yi dolgu sınıfına eklemek denendi ve
`sessiz_yanlis` **12 → 13** çıktı (`§26.1`). Yani **sayılmalı ama gösterilmemeli**.

*Aynı kelime bir kapıda kanıt, bir cümlede gürültü olabilir; listeyi soruya göre ayırmak,
kelimeyi iki kez tanımlamaktan ucuzdur.*

⊙ Yedek cümleler **zaten yazılıydı**: `netlestirme.olcu` (bir denetim ajanının bulduğu
**sıfır tüketicili** söz) ve `netlestirme.konu`. Çözüm yeni metin değil, **devir**.

### 28.3 · ⚠ Ve düzeltme bir kez YARIM kaldı

Süzgeci önce yalnız *kısmi anlama* dalına uyguladım; curl aynı cümleyi **aynen**
döndürdü — ölçülen vaka `other_topic` dalından geçiyordu.

*Bir düzeltmeyi tek dala uygulamak, iki dalı olan bir kusuru yarım kapatır.*

Kapı artık **her iki** dalın yedeğini ayrı ayrı ölçüyor.

### 28.4 · YENİ SENARYOLAR — `P` serisi (curl, tek tek)

| # | senaryo | sonuç |
|---|---|---|
| P1 | `bu yıl kalite red oranı` | ⚠ `cube+llm` · `tolerans_asma_sayisi` seçildi — **oran değil sayı**; özet *"1 satırlık sonuç"* (değer yok) |
| P2 | `bu yıl en uzun duruş hangi makinede` | 🔴 *"«uzun» başka bir konu gibi görünüyor"* |
| P3 | `2025 toplam ciro` | 🔴 *"hangi dönem için?"* — çıplak **yıl** dönem sayılmıyor |

#### 🔴 P2 — sıfat, konu sanılıyor

`uzun` bir **niteleme sıfatıdır** (*"en uzun duruş"* = `toplam_durus_dakika` + `desc`),
bir konu değil. Gösterim süzgeci (`§28.2`) işlev sözcüklerini eledi ama **sıfatları**
elemiyor — ve daha önemlisi, kapsam kapısı hâlâ turu düşürüyor.

⚠ `§26.1`'in dersi burada bağlayıcı: dolgu sınıfını genişletmek **sessiz-yanlışı
artırdı** (12 → 13). Yani `uzun`'u dolguya eklemek **yasak**; doğru yol, sıfatın
**sıralama niyetine** çevrilmesi (`_direction` zaten *"en uzun"*u okuyabilir mi —
ölçülmeli).

#### 🔴 P3 — çıplak yıl dönem sayılmıyor

`_calendar_year_filters` *"2019 yılında"* · *"2019'da"* · *"2019 senesinde"* biçimlerini
tanıyor; **çıplak `2025`** tanınmıyor ve bu **bilinçliydi** (belgede: *"çıplak 2019 ise
dönem SORUYORDU — sessiz-yanlış YOK"*).

⊙ Yani P3 bir **kusur değil, kayıtlı bir karar** olabilir. ⚠ Ama ölçüt kullanıcı
tarafında değişmiş olabilir: *"2025 toplam ciro"* günlük dilde tartışmasız bir yıl
ifadesidir. **Karar yeniden tartılmalı** — ve tartı `nl_corpus`'ta, tahminle değil.

*Bir kararı kusur sanmadan önce kaydını ara; kayıtlı bir kararı değiştirmek, onu ölçen
sayıyı da değiştirmeyi gerektirir.*

---

## 29 · ÜSTÜNLÜK BİR YAPIYA ÇEVRİLDİ — korpusta **+22 doğru**

### 29.1 · Kök: liste değil yapı

`_direction` on bir kalıplık bir **sıfat listesiydi** (`en dusuk`·`en cok`·`en yuksek`…)
ve `en uzun` içinde yoktu; yarın `en kısa`, `en ağır`, `en hızlı` olacaktı (`ADR-0008`).

⊙ Türkçede üstünlük **kapalı bir yapıdır**: `en` + sıfat. Yapıyı tanımak için sıfatı
bilmek gerekmez — **yön** için gerekir, ve o da küçük bir **kutupluluk** kümesiyle çözülür.

🔴 Liste **büyümedi, küçüldü**: 11 kalıp → 1 yapı + 7 kutup.
Ve `§22.4`'ün kuralı uygulandı: yapının tükettiği iki kelime kapsam kapısında **konu
sayılmaz**.

*Bir dilin yapısını tanımak, o yapının bütün örneklerini saymaktan hem kısadır hem
doğrudur.*

### 29.2 · ⊙ ÖLÇÜLEN KAZANÇ (gerçek-dünya korpusu, 2285 vaka)

| | önce | **sonra** | Δ |
|---|---|---|---|
| kabul | 1 138 | **1 156** | +18 |
| 🔴 **doğru** | 69 | **91** | **+22** |
| beyanlı kısmi | 72 | **50** | −22 |
| 🔴 **sessiz-yanlış** | 12 | **12** | **0** |

> Doğru cevap **%32 arttı**, sessiz-yanlış **hiç artmadı**. Kapsam beyandan değil,
> **beyanlı kısmiden** kazanıldı: daha önce *"sıralayamadım"* diye etiketlenen 22 cevap
> artık gerçekten sıralanıyor.

### 29.3 · ⚠ İki kez kapı yakaladı — ikisi de yapıya geçişin bedeli

1. **`hangisi` kısayolu yapıyı eziyordu**: *"en düşük hangisi"* → **DESC**. Kullanıcı en
   düşüğü ister, sistem en yükseği sıralar. *Bir kısayol, kestirdiği yolun kendisinden
   daha çok şey bilemez.* → yapı önce, kısayol sonra.
2. **Kutupluluk TAM eşleşmeydi**: *"en düşükleri göster"* → `dusukleri` ∉ küme → DESC.
   Eski liste (`_herhangi`) zaten **çekim toleranslıydı**; yapıya geçerken o toleransı
   düşürmüşüm. *Bir listeyi yapıya çevirirken, listenin sessizce yaptığı işi de taşımak
   gerekir.*

### 29.4 · 🔴 P2 İLERLEDİ, YENİ ENGEL ÇIKTI (sekizinci morfoloji vakası)

```
"bu yıl en uzun duruş hangi makinede"
önce  🔴 "«uzun» başka bir konu gibi görünüyor"
sonra 🔴 "«hangi makinede» yerine «hangi gun» mi demek istedin?"
```

⊙ `uzun` artık engel değil. Yeni engel: **`makinede`** — `makine`'nin bulunma hâli — ve
üstüne **absürt bir öneri** (`hangi gun`).

🔴 İki kusur birden:
* **morfoloji**: `makine` bir boyut adı; `makinede` onun çekimi (sekizinci vaka —
  `ocağa`·`3'ünü`·`çeyreklere`·`üretildi`·`3 tanesi`·`5 milyon üzeri`·`yıkama`·`makinede`)
* **öneri kalitesi**: `typo_correct`'in *"çapraz-konu terimi — yazım hatası değil"*
  koruması burada çalışmıyor; içinde **gerçek bir boyut adı** geçen bir parçaya düzeltme
  önerilmemeli.

*Bir yazım önerisi, düzeltmeye çalıştığı metinde katalogun kendi kelimesi varsa öneri
değil bir yanlış anlamadır.*

---

## 30 · `A` SERİSİ — 20 AGENTIC SENARYO (sıralı işlem · çok grafik · sohbet)

> **Kullanıcı talebi (2026-08-07):** *"Artık daha karmaşık, aslında **agentic**
> diyebileceğimiz sıralı işlemler, birden fazla grafik ya da bir grafikte birden çok
> eksen, modern grafikler… sohbet tarzı öneriler isteyelim, soralım, konuşalım, grafik
> dönüşümü isteyelim (bar yerine pie)."*
>
> 🔴 Her senaryo **thread**tir; turlar **tek tek** `curl` ile koşulur ve **her turun**
> `source` · `cq` · `note` · `iz` · süre'si buraya yazılır.

### 30.1 · Senaryo listesi (20 thread · 58 tur)

| # | thread | turlar |
|---|---|---|
| **A1** | çok adımlı etki analizi | `makine verimliliklerinin bu yılki karlılığa etkisini analiz et` → `en düşük 3 makineyi göster` → `bunların duruş nedenlerini kır` |
| **A2** | kıyas + kök-neden zinciri | `personel çalışma süreleri ve verimliliklerini kıyasla` → `en düşüğü listele` → `neden diğerlerinden düşük` |
| **A3** | üç yönlü dallanma | `ciromun en büyük 3 kaynağı olan müşterilerimi bul` → `bunlara en çok neler sattığımı karşılaştır` → `üçü için ayrı ayrı göster` |
| **A4** | grafik dönüşümü | `bu yıl aşama bazında fire` → `pasta grafik yap` → `yine bar yap` |
| **A5** | çok eksen | `aylık ciro ve fire birlikte` → `ikisini tek grafikte göster` |
| **A6** | sohbet + öneri | `bu ay nasıl gidiyoruz` → `ne önerirsin` → `ilkini uygula` |
| **A7** | dönem daraltma zinciri | `2026 ciro` → `sadece ilk çeyrek` → `aylık kır` → `en iyi ayı söyle` |
| **A8** | ölçü ekleme + kaldırma | `makine bazında oee` → `bir de fire ekle` → `oee'yi çıkar` |
| **A9** | filtre diyaloğu | `vardiya bazında üretim` → `sadece gece vardiyası` → `geçen yılla kıyasla` |
| **A10** | belirsizlik → netleştirme → devam | `fire ne durumda` → *(chip seç)* → `aylara göre` |
| **A11** | yetenek sınırı → alternatif | `gelecek çeyrek tahmini` → `peki geçmiş eğilim` |
| **A12** | çapraz-cube harman | `bu yıl ciro` → `bir de enerji maliyeti ekle` → `oranını göster` |
| **A13** | top-N + drill | `en çok fire veren 3 aşama` → `ilkini makinelere kır` |
| **A14** | eşik + sıralama | `10 milyon üzeri ciro yapan müşteriler` → `en yükseğinden sırala` |
| **A15** | zaman serisi + anomali | `aylık fire trendi` → `sıra dışı ay var mı` |
| **A16** | konu değişimi (tuzak) | `bu yıl ciro` → `kalite red oranı nedir` *(yeni konu — takip DEĞİL)* |
| **A17** | çoklu kırılım | `müşteri ve aşama bazında fire` → `en kötü ikiliyi bul` |
| **A18** | oran hesabı | `fire oranı yüzde kaç` → `geçen yıla göre değişimi` |
| **A19** | özet + paylaşım | `bu yılın özetini çıkar` → `müdüre 3 cümle yaz` |
| **A20** | geri alma / düzeltme | `mart ciro` → `pardon nisan olacaktı` → `ikisini kıyasla` |

### 30.2 · Kabul ölçütü — *"cevap geldi"* YETMEZ

Her tur için üç soru:

1. **Doğru mu** — `cq` sorulan şeyi mi kuruyor (ölçü · kapsam · dönem · sıralama)?
2. **Dürüst mü** — yapamadığını **söylüyor** mu (`eksik_niyet`/sınır beyanı), yoksa
   sessizce eksik mi cevaplıyor?
3. **Deterministik mi** — `iz`'de LLM görünüyorsa **neden**? (garson mu, Discovery mi?)

⚠ Ve süre: **>10 sn** bir turda ön yüz proxy'si kopabiliyor (`§23.2`) — o tur **kırmızı**
sayılır, cevap doğru olsa bile.

### 30.3 · Koşum — ilk parti (curl, tek tek)

| tur | soru | sonuç |
|---|---|---|
| **A1/1** | `makine verimliliklerinin bu yılki karlılığa etkisini analiz et` | 🔴 *"«karliliga etkisini analiz» başka bir konu"* |
| **A2/1** | `personel çalışma süreleri ve verimliliklerini kıyasla` | 🔴 *"«personel sureleri» başka bir konu"* |
| **A3/1** | `ciromun en büyük 3 kaynağı olan müşterilerimi bul` | ✅ cube+ölçü+boyut çözüldü · dönem soruyor |
| **A3/2** | `bu yıl` | 🔴 **8 satır** — *"en büyük **3**"* niyeti turlar arası **KAYBOLDU** |
| **A4/1** | `pasta grafik yap` | ✅✅ *"saf görünüm değişikliği → pie (rapor korunur, LLM'siz)"* · `view_hint=pie` |

#### 🔴 KUSUR T — TOP-N NİYETİ TURLAR ARASI KAYBOLUYOR

```
tur 1: "ciromun en büyük 3 kaynağı olan müşterilerimi bul"  → cq: {musteri, toplam_ciro}
       (dönem sorulur; ⚠ `limit:3` cq'ya HİÇ yazılmadı — soru cevaplanamadı ki yazılsın)
tur 2: "bu yıl"                                            → 8 satır
```

⊙ Kök: netleştirme turu `cq`'yu **taşıyor** ama kullanıcının **ilk cümlesindeki** top-N
niyetini taşımıyor. İkinci turda soru yalnız *"bu yıl"* — orada `3` yok.

🔴 Bu, `§28.2`'nin *"iki soru iki liste"* dersinin kardeşi: **niyet** ile **sorgu** ayrı
şeyler ve netleştirme yalnız sorguyu köprülüyor.

> **Kural:** bir netleştirme turu, cevaplanmamış sorunun **niyetini** de taşımalı —
> yoksa kullanıcı sorusunu ikinci kez sormak zorunda kalır ve sistem *"anladım"* dediği
> şeyi **unutmuş** olur.

*Bir soruyu yarım cevaplayıp yarısını unutmak, hiç cevaplamamaktan daha yanıltıcıdır:
kullanıcı cevabın tam olduğunu sanır.*

#### 🔴 KUSUR U — *"analiz et"* / *"kıyasla"* fiilleri konu sanılıyor

`A1` ve `A2` aynı biçimde düştü: **çok ölçülü, çok adımlı** bir istek, kapsam kapısında
*"başka bir konu"* diye etiketlendi.

⚠ `karliliga etkisini analiz` ve `personel sureleri` — bunlar **konu** değil, **eylem**
(`analiz et` · `kıyasla`) ve **çekim** (`karlılığa` · `süreleri`). Dokuzuncu ve onuncu
morfoloji vakası.

⊙ Ve bu iki soru, kullanıcının *"agentic"* dediği sınıfın **tam merkezi**: birden çok
ölçü + sıralı işlem. Sistem bugün onları **ilk adımda** kaybediyor.

### 30.4 · Koşum — ikinci parti

| tur | soru | sonuç |
|---|---|---|
| **A5/1** | `bu yıl aylık ciro ve fire birlikte` | ✅✅ iki ölçü tek sorguda · aylık kova · belirsizlik beyanı |
| **A6/1** | `bu ay nasıl gidiyoruz` | ✅ dürüst: *"tanıdığım bir konu geçmiyor — şunlardan biri mi?"* + öneriler |
| **A8/1** | `bu yıl makine bazında oee` | ✅ 11 satır |
| **A8/2** | `bir de fire ekle` | ✅✅ ölçü eklendi · dönem+kırılım korundu · belirsizlik beyanı · **0 LLM** |
| **A13/1** | `bu yıl en çok fire veren 3 aşama` | 🔴 *"«veren» başka bir konu gibi görünüyor"* |

⚠ **Ortam:** A5/A6 ilk denemede **tamamen boş** döndü — `{"detail":"Geçersiz veya süresi
dolmuş token"}`. `§0.3`'ün kayıtlı tuzağı; ürün kusuru **değil**. *Kayıtlı bir tuzağı
ikinci kez bulgu sanmamak, kaydın tek işlevidir.*

### 30.5 · 🔴 ONBİRİNCİ MORFOLOJİ VAKASI — ve artık bir DESEN

`veren` (sıfat-fiil, *vermek*) — `en çok fire **veren** 3 aşama`.

⊙ Biriken liste: `ocağa` · `3'ünü` · `çeyreklere` · `üretildi` · `3 tanesi` ·
`5 milyon üzeri` · `yıkama` · `makinede` · `karlılığa/analiz` · `personel süreleri` ·
**`veren`**.

🔴 **Onbir vakanın onu tek bir sınıf**: katalogda karşılığı olan ya da dilbilgisel bir
öğe, **çekimli** hâliyle tanınmıyor ve kapsam kapısı turu düşürüyor.

⚠ Ve `§26.1` bağlayıcı: **dolgu sınıfını genişletmek yasak** (sessiz-yanlış 12 → 13).
Yani çözüm liste değil **morfoloji**: `app/ek.py` (G7) ekleri **üretiyor ama sökmüyor** —
bu belgede **dördüncü kez** yazılıyor.

> **Kök çözüm adayı:** kapsam kapısı bir kelimeyi bilinmeyen saymadan önce, **ek
> soyulmuş** kökünü katalogda aramalı. `_covers`/`_syn_hit` zaten ek zinciri doğruluyor
> (üretim yönü); eksik olan **ters yön**: verilen kelimeden köke inmek.

*Bir dilin eklerini üretebilen sistem, onları sökebilmelidir de; yoksa kendi ürettiği
biçimi tanımaz.*

### 30.6 · ⊙ VE İYİ HABER: agentic çekirdek ÇALIŞIYOR

`A5` (çok ölçü + zaman kovası), `A8` (ölçü ekleme, cube'lar arası belirsizlik beyanıyla)
ve `A4` (grafik dönüşümü, 0 LLM) **tam istendiği gibi** çalışıyor.

🔴 Yani kullanıcının *"agentic"* dediği yeteneklerin **mutfağı hazır**; kaybedilen turlar
**dil kapısında** kaybediliyor — `§AJ4`'ün *"garsonun fişi"* teşhisiyle aynı yöne bakıyor.

### 30.7 · Koşum — üçüncü parti

| tur | soru | sonuç |
|---|---|---|
| **A7/1** | `2026 ciro` | ◐ dönem soruyor (çıplak yıl — kayıtlı karar, `§28.4/P3`) |
| **A7/2** | `sadece ilk çeyrek` | ✅ `2026-01-01..03-31` · ₺27.767.945,12 · **0 LLM** |
| **A16/1** | `kalite red oranı nedir` *(yeni konu)* | 🔴 **takip sanıldı** |

#### 🔴 KUSUR V — KONU DEĞİŞİMİ TAKİP SANILDI

```
bağlam: {parti · toplam_ciro · 2026 Q1}
soru  : "kalite red oranı nedir"
cq    : {parti · [toplam_ciro, fire_orani_yuzde] · 2026 Q1}   🔴 CİRO KORUNDU
iz    : "Takip: LLM-destekli yapısal düzenleme"
```

🔴 Kullanıcı **artık ciro sormuyor**; yeni bir konu açtı. Sistem eskisini **koruyup**
üstüne ekledi — ve özet *"ciro: ₺27.767.945,12. 2 ölçü…"* diyerek **sorulmayan sayıyı
başa** koydu.

⚠ Ve `cube` **`parti`** kaldı: kullanıcı *"kalite"* dedi, cevap `parti` cube'undan geldi.
`fire_orani_yuzde` bir yakınsama olabilir ama **kalite cube'u ayrı bir cube**.

⊙ `followup.sinifla`'nın `konu_degisimi` sınıfı **var** ve bu turda çalışmadı: soru
`nedir` ile bitiyor (dolgu), `kalite` bir **cube adı** — yani konu değişiminin en güçlü
sinyali (rakip cube kimliği) elde olmasına rağmen takip kazandı.

> **Kural adayı:** takip düzenlemesi, sorunun **başka bir cube'un kimliğini** taşıdığı
> durumda kazanamaz — o bir düzenleme değil **yeni bir sorudur**.

*Bir raporu düzenlemek ile yeni bir rapor istemek arasındaki farkı kaçıran sistem,
kullanıcının sormadığı sayıyı ona ilk satırda gösterir.*

---

## 31 · MORFOLOJİ KÖK ÇÖZÜMÜ — bir kat indi, **bir kat daha var**

### 31.1 · İnen kat: katalog terimi artık KÖKÜNE iniyor

Onbir/oniki vakanın ortak kökü: katalogda **ad** var (`uretim`·`islem`), kullanıcıda
**fiil** (`üretildi`·`işlenen`). `_covers` ikisini bağlayamıyordu çünkü hiçbiri ötekinin
öneki değil — ortak olan **kök**tür.

`_kok()` eklendi: ad-yapan ekleri (`-im/-ım/-um/-üm` · `-me/-ma` · `-iş/-ış/-uş/-üş`)
soyup `uretim → uret` yapıyor, sonra `_covers` **aynen** yeniden koşuyor.

⚠ İki sınır yazılı: kök **en az dört harf** (`kar ⊂ ankara` sessiz-yanlışı geri gelmesin)
ve soyma **yalnız katalog terimine** — *bir eşleşmeyi genişletirken, tahmin edilen tarafı
değil beyan edilen tarafı esnet.*

⊙ **Korpus: `sessiz_yanlis` 12'de SABİT**, `dogru` 91'de sabit — yani genişleme
**bedelsiz**, ama bu vakayı da **açmadı**.

### 31.2 · 🔴 KALAN KAT: ek zinciri doğrulayıcısı AD çekimi biliyor, FİİL çekimi bilmiyor

```
"geçen ay kaç parti üretildi"   →  hâlâ 🔴 "«uretildi» kısmını anlayamadım"
```

⊙ Ölçüm: `_kok("uretim")` → `uret` ✅ ve `"uretildi".startswith("uret")` ✅ — ama
`_covers`'ın **ek zinciri doğrulaması** kalan `ildi` parçasını reddediyor.

🔴 Sebep: o doğrulayıcı **ad çekimini** tanıyor (hâl · çoğul · iyelik). `-il` (edilgen)
ve `-di` (görülen geçmiş) **fiil çekimidir** ve envanterde yok.

> **Kalan kök çözüm:** ek zinciri doğrulayıcısına **fiil çekimi** eklenmeli — edilgen
> (`-il/-ıl/-ul/-ül`, `-in/-ın`), sıfat-fiil (`-en/-an`, `-dik/-dık`), zaman ekleri
> (`-di/-dı/-du/-dü`, `-yor`, `-miş/-mış`).
>
> ⚠ Bu, ad çekiminden **daha geniş** bir yüzeydir ve `§26.1`'in dersi burada da geçerli:
> genişleme `sessiz_yanlis`'i artırırsa **geri alınır**. Korpus tek hakem.

*Bir dili yarısıyla tanımak, tanımamaktan yalnızca daha az görünür biçimde eksiktir:
sistem bazı cümleleri anlar ve neden ötekileri anlamadığını kimse söyleyemez.*

### 31.3 · Koşum kaydı

| tur | soru | sonuç |
|---|---|---|
| A9/1 | `bu yıl vardiya bazında işlenen kg` | 🔴 `işlenen` — **12.** morfoloji vakası |
| A9/2 | `sadece gece vardiyası` | ◐ `makine_duruslari` · `vardiya=3` çözüldü ama dönem soruyor (bağlam tur 1'de kırıldığı için) |
| V1 | `geçen ay kaç parti üretildi` | 🔴 kalan kat (fiil çekimi) |

Kapılar: hızlı kapı **1425 yeşil** · korpus **%95,1 = taban**, `sessiz_yanlis` **12 sabit**.

---

## §32 · FİİL MORFOLOJİSİ — ve *"kısa ek tehlikeli görünür ama değildir"* iddiasının ÇÜRÜTÜLMESİ

### 32.1 · Ne eksikti

`§31.1`'de `_kok()` indi: katalog terimlerinden **ad yapan** ekler soyuluyor
(`uretim → uret`), böylece `uretildi` bir katalog terimine bağlanabiliyordu. Korpus
yeşildi (`sessiz_yanlis` **12** sabit). Ama curl hâlâ kırmızıydı:

```
geçen ay kaç parti üretildi   →  eksik: ['olcu']
```

İzole edilen sebep — **iki koşul, biri sağlanmıyordu**:

| kontrol | sonuç |
|---|---|
| `_kok("uretim")` → `"uret"` | ✅ |
| `"uretildi".startswith("uret")` | ✅ |
| `_ek_gecerli("ildi")` — kalan ek zinciri geçerli mi? | 🔴 **HAYIR** |

`_SUFFIX_ATOMS` envanteri **ad** çekimini biliyordu (hâl · çoğul · iyelik). `-il`
(edilgen) ve `-di` (görülen geçmiş) **fiil** çekimidir ve envanterde **hiç yoktu**.
Yani `§31.1` doğru bir kökü buluyor, sonra kalanı tanımadığı için **reddediyordu**.

### 32.2 · İlk yazım — ve kapının çürüttüğü iddia

İlk denemede envantere şunlar kondu:

```python
"ildi","ıldı","uldu","üldü",  "il","ıl","ul","ül",  "en","an",
"dik","dık","duk",  "yor",  "di","du","ti","tu",
```

Ve muafiyet gerekçesine şu cümle yazıldı:

> *«Kısa oldukları için tek başlarına tehlikeli görünürler — ama zincir kalanın
> **tamamını** eşlemek zorunda **ve** kök zaten bir katalog terimidir: yüzey iki yandan
> sınırlı.»*

🔴 **Bu cümle yanlıştı ve demet kapısı onu tek satırda çürüttü:**

```
E   AssertionError: assert not True
E    +  where True = _covers('mal', 'maliyeti')
```

`maliyeti` = `mal` + `i` + `ye` + `ti` — ve `ti` yeni envanterdeydi. Yani `_covers`'ın
**var olma sebebi** olan `mal ⊂ maliyeti` sessiz-yanlışı geri gelmişti.

⊙ **Yanıldığım nokta:** *"iki yandan sınırlı"* bir yüzeyin **hâlâ geniş** olabileceği.
İki harflik bir ek zincirde **her yere** sığar; kısalık bir güvence değil, tehlikenin
ta kendisidir.

> *Bir ekin kısalığı onun tehlikesidir: kısa ek her kelimenin sonunda bulunur.*

### 32.3 · Düzeltilmiş envanter — bileşik biçimler

Kısa olanlar düşürüldü, yerlerine **bileşik** olanlar kondu. Aynı işi görürler, kazayla
eşleşemezler:

```python
"ildi","ıldı","uldu","üldü",   # edilgen+geçmiş bileşiği:  "üret"+"ildi"
"ilen","ılan","ulan","ülen",   # edilgen+sıfat-fiil
"en","an",                     # sıfat-fiil: "ver"+"en"
"dik","dık","duk","dük",       # ortaç
"yor",                         # şimdiki zaman
```

| biçim | çözülüş |
|---|---|
| `üretildi` | `uret` + **`ildi`** ✅ |
| `veren` | `ver` + **`en`** ✅ |
| `işlenen` | `isle` + `n` + **`en`** ✅ |
| `maliyeti` | `mal` + `i` + `ye` + `ti` → **`ti` YOK** ⛔ ✅ doğru red |

### 32.4 · İki kapının işbölümü — ölçülmüş bir gerçek

🔴 **Korpus bu gerilemeyi GÖREMEDİ.** `kkO` koşumu kısa eklerle koştu ve
`sessiz_yanlis` **12**'de sabit kaldı. Gerilemeyi yakalayan `--hizli`'nin seçtiği
birim testiydi.

Sebep yapısal: korpus soruları **katalogdan üretilir**, yani `maliyeti` gibi bir
terimin **yanlış bir kökle** eşleşmesi korpusun sorduğu bir soru değildir. Korpus
*"kaç soru cevaplanabiliyor"* sorusunu sorar; birim testi *"bu eşleşme doğru mu"*
sorusunu.

> *İki kapı aynı şeye bakmıyorsa, birinin yeşili ötekinin yeşili değildir — ve bir
> demet ancak ikisi birden yeşilse yeşildir.*

Bu, `CLAUDE.md`'deki *"korpusun bilinen körlüğü"* maddesinin **ikinci** kanıtıdır
(ilki: typo yolu korpusta hiç sorulmuyor).

### 32.5 · Meta-kapı da konuştu

Kısa ekler düşünce net Δ **7 → 6** oldu ve meta-kapı **kırmızı** verdi:

```
🔴 KAPI SAHTE: bir kod satırı eklendi ve tavan hâlâ aşılmadı.
   Tavanda boşluk var demektir (1) — kapı büyümeyi DURDURMUYOR.
```

Doğru tepki tavanı **elle yükseltmek değil**, muafiyet Δ'sını gerçeğe eşitlemekti
(tavan zaten `sum(Δ)`'dan türetiliyor). *Bir tavanda boşluk bırakmak, tavanı bir
sonraki artışta sessizce kabul etmektir.*

### 32.6 · Tazeleme sonrası curl doğrulaması — üçü de DOĞRU

`docker-compose build` + `up` sonrası, tek tek:

| # | soru | önce | **sonra** | süre |
|---|---|---|---|---|
| `m32a` | `geçen ay kaç parti üretildi` | `eksik: ['olcu']` | ✅ `cq={parti, parti_sayisi, 2026-07}` + **dürüst sınır**: *«Bu aralıkta kayıt yok… elimdeki veri 01.01.2024 – 30.06.2026»* | 12.909 ms |
| `m32b` | `en çok fire veren 3 aşama` | `veren` anlaşılmıyor | ✅ `cq={parti, toplam_fire_kg, dims:[asama]}` + *«hangi dönem için?»* | 14.335 ms |
| `m32c` | `bu yıl vardiya bazında işlenen kg` | `işlenen` anlaşılmıyor | ✅ **3 satır**, `cq={oee, toplam_uretim_kg, dims:[vardiya], 2026-01-01…}` | 20.425 ms |

⊙ `m32a`'nın cevabı **veri yok** — ve bu **doğru** cevaptır: veri 2026-06-30'da bitiyor,
*"geçen ay"* 2026-07. Sistem boş tablo göstermiyor, **sınırını beyan ediyor**.

### 32.7 · Doğrulama turunun AÇTIĞI üç kayıt

**(a) 🔴 Üçü de `source=cube+llm` — yani `route()` hâlâ çözemiyor.**
Morfoloji onarımı `_covers`'ı düzeltti ama bu üç cümle deterministik yoldan **geçmedi**;
cevabı **garson LLM** verdi. Kullanıcının mimari duruşuna göre bu **tasarımın çalışması**
(*"route'un cevaplayamadığı her şeyi LLM'e yıkabilmek"*), ama **fiyatı 12–20 sn**.

**(b) ⚠ `Kusur T` yine göründü** — `en çok fire veren **3** aşama`'da hem `order` hem
`limit` **kayboldu**: `cq`'da ne `order` var ne `limit`. Netleştirme turuna girerken
üstünlük+sayı niyeti düşüyor.

**(c) ✅ Beyaz-liste reddi bir KUSUR DEĞİL — kapının işi.**
Log: `intent: whitelist REDDİ (sema=kapali) — ham={"cube":"parti","measures":
["toplam_agirlik_kg"],"dimensions":["vardiya"],…}`. LLM `parti` küpüne **olmayan** bir
ölçü/boyut uydurdu; `parse_cube_query` oyu düşürdü. Üç oydan biri gitti, kalan ikisi
uyuştu, cevap doğru çıktı.

> *Bir uydurmanın sessizce düşürülmesi bir kayıp değil, kapının tek görünür kanıtıdır —
> ve bu satır loga yazıldığı için görünür.*

---

# B TURU · 20 agentic senaryo — *"sıralı işlemler, grafik dönüşümü, sohbet"*

Kullanıcının bu tur için koyduğu çıta: *"artık daha karmaşık… aslında agentic
diyebileceğimiz sıralı işlemler… sohbet tarzı öneriler isteyelim, grafik dönüşümü
isteyelim bar yerine pie gibi."*

## §33 · BÜTÇE YAZILIYDI, ÇALIŞMIYORDU — iki yerde, tek satırlık kök

### 33.1 · Ölçüm

| senaryo | bütçe | **ölçülen** | log |
|---|---|---|---|
| `b2` `bu yıl en çok fire veren makine hangisi` | Intent 20 sn | **30.408 ms** | *«oy düştü»* |
| `b5` `personel çalışma süreleri…` | Intent 20 sn | **39.115 ms** | *«oy düştü»* |
| `b3` `ikisini tek grafikte çift eksende göster` | anlatı 8 sn | **82.049 ms** | *«süssüz ama doğru»* |
| `b6` `ciromun en büyük 3 kaynağı…` | — | 🔴 **656.689 ms** | — |

⊙ Üçü de aşımı **doğru tespit etti, logladı** — sonra yine sonuna kadar bekledi.

🔴 **En keskin tek ölçüm (`b5`):** iki oy **6.775 ms**'de aynı cevapta uzlaştı
(`{"cube":null}` — dürüst red). Üçüncü oy **37.840 ms** sürdü ve **aynı** cevabı verdi.
Kullanıcı, sistemin **6,7 saniyede bildiği** cevap için **39 saniye** bekledi.

### 33.2 · Kök — ve bir yorumun kendi kodunu yalanlaması

```python
with cf.ThreadPoolExecutor(...) as ex:      # ← çıkışta shutdown(wait=True)
    fut.result(timeout=kalan)               # ← TimeoutError atar, oy düşer
# ← ve BURADA yavaş iş parçacığı beklenir
```

`future.result(timeout=…)` **beklemeyi** keser, **işi** değil. `__exit__` →
`shutdown(wait=True)` onu geri koyar.

🔴 `answer.py`'de bu, kodun **kendi yorumuyla** çelişiyordu:

> *«⚠ İş arka planda bitmeye devam eder (thread öldürülemez) — ama cevabı bekletmez.»*

Niyet doğruydu; `with` onu sessizce iptal ediyordu.

> *Bir bütçe, çıkışında bekleyen bir bağlam yöneticisinin içindeyse bütçe değildir —
> yalnız bir log satırıdır.*
>
> *Bir yorumun anlattığı davranış ölçülmemişse, o bir belge değil bir dilektir.*

### 33.3 · Kök çözüm — `app/butce.py`, tek sahip

İki kopya vardı ve **ikisi de aynı hatayı** taşıyordu (`KAT-1`). Uygulama tek modüle
taşındı; `finally: ex.shutdown(wait=False, cancel_futures=True)`.

⚠ **Sınır yazılı:** bu bir **iptal değil vazgeçiş**tir — thread öldürülemez, iş arka
planda biter ve sonucu atılır. Nitekim `b6`'nın terk edilen anlatı çağrısı loglara
`45.282 ms` diye düştü: tasarım **görünür**.

⚠ **`ASIM` sentinel `None` DEĞİL:** `None` meşru bir sonuçtur (model çekimser kalabilir).
İkisini tek değere çökertmek *"bilmiyor"* ile *"geç kaldı"*yı kaybetmek olurdu.

### 33.4 · Doğrulama (tazelenmiş konteyner)

| senaryo | önce | **sonra** |
|---|---|---|
| `b5` Intent bütçesi | 39.115 ms | **21.276 ms** (aşımdan 0,2 sn sonra döndü) |
| `b3` anlatı bütçesi | 82.049 ms | **22.224 ms** (aşım tam 8. saniyede) |

Log artık `BÜTÇEYİ AŞTI (20.0 sn) — BEKLENMİYOR` diyor ve **gerçekten beklemiyor**.

### 33.5 · Kapılar — metin çapası neden yetmedi

Eski üç kapı **yeşildi** ve bütçe çalışmıyordu, çünkü **üçü de kaynağa bakıyordu**.
Çapalar taşındı (silinmedi) ve yanlarına **davranışsal** biri kondu:

- `test_BUTCE_GERCEKTEN_BEKLEMEZ` — 0,3 sn bütçeli çağrı 3 sn'lik işi beklemeyecek
- `test_ASIM_NONE_DEGILDIR` — çekimserlik ile aşım ayrı kalacak
- `test_HICBIR_BUTCE_WITH_EXECUTOR_ICINDE_DEGIL` — **kusur sınıfının** kapısı: `app/`
  altında hiçbir yerde `with ThreadPoolExecutor` + `result(timeout=` birleşimi olmayacak

> *Bir metin çapası, metnin anlattığı davranışı kanıtlamaz; onu yalnız iddia eder.*

## §34 · SIRALAMA, KESME SAYISINA BAĞLANMIŞTI

### 34.1 · Ölçüm — dört tur, tek kök

| soru | `cq` | beyan |
|---|---|---|
| `bu yıl en çok fire veren makine hangisi` | sırasız, 11 satır | `eksik_niyet:['ustunluk']` |
| `bu üçüne en çok hangi renkleri sattığımı göster` | sırasız, 40 satır | `eksik_niyet:['ustunluk']` |
| `ciromun en büyük 3 kaynağı olan müşterilerimi bul` | sırasız, 8 satır | — |
| `en az üretim yapan 3 makine` | ✅ `order:asc` + `limit:3` | — |

Dördüncüsü çalışıyordu, ilk üçü değil. Ve sistemin **kendi cevabı** kusuru yazıyordu:

> *«en yüksek/en çok dedin ama sıralama uygulayamadım. **«en yüksek 5 makine» gibi sayı
> verirsen** sıralayıp keserim.»*

🔴 **Sıralama bir kesme sayısına ihtiyaç duymaz.** *"En çok fire veren makine hangisi"*
sorusunun cevabı **sıralı bir tablonun ilk satırıdır**; sayı kaç satır **gösterileceğini**
söyler, hangisinin **önce** geleceğini değil.

⊙ Ve sistem her şeyi **biliyordu**: `uyum.py` eksikliği tespit edip beyan ediyor, yön
`_direction(q)`'dan deterministik geliyor, ölçüt `cq`'nun kendi ölçüsü. Elinde her şey
vardı; yalnız **uygulamıyordu**.

> *Bir eksikliği doğru teşhis edip yalnız anlatmak, onu kapatmanın yerine geçmez.*

### 34.2 · İkinci yarı — niyet netleştirmeden sağ çıkmıyordu

`ciromun en büyük 3 kaynağı…` → *"hangi dönem için?"* → kullanıcı *"bu yıl"* dedi →
**8 müşteri sırasız**. Üstünlük niyeti netleştirme turunda **sessizce düştü**, çünkü
sonraki tur o `cq`'yu taban alır ve *"bu yıl"*da hiçbir üstünlük yoktur.

⚠ En keskin çift: `en az üretim yapan 3 makine` **aynı** netleştirmeye gidiyor ve
`order`+`limit`'i **taşıyor** — çünkü orada sayı boyut adına bitişikti (`3 makine`).

> *Bir niyetin taşınması, cümledeki kelime sırasına bağlı olmamalıdır.*

### 34.3 · Kök çözüm — `app/siralama.py`, üç tüketici

Kural üç yerde yaşıyordu (`route` · `deterministic_refine` · Intent-JSON sonrası **hiç**)
ve üçü aynı cümleye farklı davranıyordu. Tek sahibe taşındı; tüketiciler:

1. `cube_router.deterministic_refine` (takip yolu)
2. `ask.py`'nin **ortak hunisi** `_answer_from_cube_query` — kendi docstring'i zaten
   *"her yeni Intent-path kaynağında yeniden yazılmasın"* diyor
3. dönem netleştirmesi — `cq`'yu cevaba koymadan **önceki son an**

⚠ **Yalnız sıralama konur, `limit` konmaz:** *sıralamak bilgi ekler, kesmek bilgi çıkarır
— ikisi aynı izinle yapılmaz.*

### 34.4 · Doğrulama (tazelenmiş konteyner)

| senaryo | önce | **sonra** |
|---|---|---|
| `bu yıl en çok fire veren makine hangisi` | sırasız, `eksik_niyet` | ✅ `order:desc`, RAM-2 → RAM-1 → RAM-3, beyan **temiz**, 11.276 ms |
| `ciromun en büyük 3 kaynağı…` → `bu yıl` | sırasız 8 satır | ✅ EGE KNIT 13,4M → AKDENİZ 10,9M → MAVİ 9,9M — **ilk üç satır tam olarak istenen üç** |
| `bu üçüne en çok hangi renkleri…` | sırasız 40 satır | ✅ sıralı, `eksik_niyet` kayboldu |
| `en az üretim yapan 3 makine` *(gerileme)* | `order:asc`+`limit:3` | ✅ **aynı**, 474 ms |

### 34.5 · Bu turun kendi dersi — hedefli test yetmedi

İlk bağlamada `_answer_from_cube_query` içinde `cube_meta` kapsamda değildi →
**`NameError` → HTTP 500**. Hedefli seçtiğim **101 test yeşildi**; kusuru **curl** buldu.

⊙ Sebep yapısal: değiştirdiğim şey *dört üreticinin buluştuğu huni*ydi ve hiçbir
hedefli test dosyası o huniyi adıyla çağırmıyor. Arama modüle taşındı (`ask.py`'de o
`next(c for c in schema["cubes"] …)` kalıbı zaten **beş kez** tekrarlanıyor).

> *Bir aramanın tekrarı, aranan şeyin sahibinin belirsiz olduğunun işaretidir.*

## §35 · BOŞLUK, SATIR SAYISI DEĞİL — ÖLÇÜ DEĞERİ MESELESİ

### 35.1 · Ölçüm — iki tur, tek kök

| soru | dönen | kullanıcının okuduğu |
|---|---|---|
| `b13` `geçen ay ciro düştü mü` | `[{"toplam_ciro": null}]` | **«1 satırlık sonuç.»** |
| `b7` `bu ay neye dikkat etmeliyim` | `[{ort_oee:null, plansiz_durus:null, fire:null}]` | **«1 satırlık sonuç.»** · anlatı: **«1 satır.»** |

Dürüst boş-sonuç notu (*«Bu aralıkta kayıt bulunamadı… elimdeki veri 01.01.2024 –
30.06.2026»*) **ikisinde de sustu**.

### 35.2 · Kök — SQL'in kendisi

> **Gruplamasız bir toplulaştırma boş kümede sıfır satır değil, BİR NULL satır döndürür.**

`SUM(x)` üzerinde `WHERE` hiçbir şey tutmazsa sonuç `[(None,)]`'dır. Dedektörün koşulu
`row_count == 0` idi — yani boşluğun **en sık** biçimini tam olarak kaçırıyordu:
kırılımsız, tek dönemli soruyu. Ki en çok sorulan soru odur.

⚠ Ve aynı kusur `m32a`'da **görünmüyordu**: `geçen ay kaç parti üretildi` bir
`granularity: month` taşıyordu — gruplanmıştı, gerçekten 0 satır döndü, not oradaki tek
doğru cevabını verdi.

> *Bir dedektörün çalıştığı vaka, çalışmadığı vakayı gizleyebilir.*

### 35.3 · Kök çözüm — `veri_araligi.bos_mu`, iki tüketici

Yüklem, metnin zaten sahibi olan modüle kondu (`KAT-1`) ve **iki** tüketici çağırıyor:

1. `ask.py`'nin boş-sonuç notu — `row_count == 0` yerine
2. `interpret()` — *"1 satırlık sonuç."* özeti bir **yokluğun** özeti olamaz

⚠ **FAIL-OPEN:** ölçü adı satırlarda hiç görünmüyorsa (takma ad/ham SQL) **boş denmez**.
Bir sonucu yanlışlıkla *"kayıt yok"* diye örtmek, göstermekten kötüdür.

> *Boş bir küme üstündeki toplam, bir sayı değil bir yokluktur — ve yokluk «1 satır»
> diye sunulamaz.*

### 35.4 · Doğrulama

| soru | önce | **sonra** |
|---|---|---|
| `geçen ay ciro düştü mü` | *«1 satırlık sonuç.»* | ✅ *«Bu aralıkta (2026-07-01 – 2026-07-31) kayıt bulunamadı… Elimdeki veri **01.01.2024 – 30.06.2026**»* — yanıltıcı özet **kayboldu** |
| `bu ay neye dikkat etmeliyim` | `null,null,null` + *«1 satırlık sonuç.»* | ✅ *«sorunda tanıdığım bir konu geçmiyor — şunlardan birini mi demek istedin?»* 9.284 ms |

Kapılar: 6 yeni (tek-NULL · çok-ölçülü NULL · bir dolu değer varsa boş **değil** ·
fail-open · `interpret` yokluğu sonuç sanmaz · **yüklem tek sahipli**).

## §36 · *"NEDEN"* SORUSU BİR SIRALAMAYA ÇEVRİLİYORDU — kök: eksik bir ZAMİR SINIFI

### 36.1 · Ölçüm

`b2` zinciri, T3: `neden diğerlerinden yüksek` → `cq`'ya yalnız `order:{desc}` eklendi,
satırlar **aynı 66**, anlatı **önceki turun birebir kopyası**, süre **23.646 ms**.
Kullanıcı yeni bir soru sordu, **eski cevabı** aldı.

### 36.2 · İki aday kök — ve hangisi olduğunu TEK curl ayırdı

Bu depo *"bir kusuru doğru teşhis edip yanlış katmanda düzeltme"*yi iki kez ödedi. Bu
yüzden tahmin edilmedi, **ayrıştırıldı**: aynı soru **zamirli** yazıldı.

```
bu neden yüksek   →  2.202 ms · 0 LLM · GERÇEK kök-neden:
   «iplik grubu: Örme Kumaş — 35.583 kg arttı (net değişimin %100'ü)»
   «hat: RAM 2 — 19.111 kg arttı (net değişimin %53,7'si)»
```

⊙ **Makine kusursuz çalışıyordu. Kapı açılmıyordu.**

### 36.3 · Kök

`followup.py`'nin takip şartı `_ISARET_ZAMIRI` — yani yalnız **işaret** zamirleri
(`bu`·`şu`·`buradaki`). *"Diğerleri"* bir **belgisiz zamirdir** ve listede yoktu;
`_kisa_soru` eşiği 2 kelime, cümle 3 kelime; `_capaya_deger` de tutmadı (*"diğerlerinden"*
bir boyut değeri değil).

🔴 Ve bu bağlamda belgisiz zamir, işaret zamirinden **daha güçlü** bir çapadır:
*"şu"* bir şeyi işaret eder, *"diğerleri"* **ekranda kalan satırlardan başka bir şey
olamaz**.

⚠ Gövde eşlemesi (`diger|oteki|beriki` + herhangi bir ek) bilerek: çekimleri tek tek
yazmak bir **kelime listesi** olurdu, gövdeyi yazmak bir **kapalı sınıf** — `ADR-0008`'in
açıkça serbest bıraktığı şey. Aynı biçim `_USTUNLUK_RE`'de de kullanılıyor.

⚠ Kapsam `TUR_NEDEN` + `baglam_var` ile sınırlı: `ANLAT`/`TAKİP`'te aynı gevşeme konu
değişimini çalardı (*"diğer makineleri göster"* yeni bir sorudur).

### 36.4 · Doğrulama

| | önce | **sonra** |
|---|---|---|
| `neden diğerlerinden yüksek` | 23.646 ms · LLM · sıralamaya çevrildi · anlatı kopya | ✅ **1.033 ms · 0 LLM** · *«Örme Kumaş net değişimin %100'ü · RAM 2 %53,7»* |

**23 kat hızlı — ve cevabı sistem veriyor, LLM yalnız garson.**

## §37 · GRAFİK DÖNÜŞÜMÜ — dal VARDI, ateşlenmiyordu

### 37.1 · Ölçüm

| soru | ne oldu | süre |
|---|---|---|
| `bunu pasta grafik yap` | LLM'e gitti, `view_hint` yok, grafik değişmedi | 6.520 ms |
| `çizgi yerine bar yap` | LLM'e gitti, grafik değişmedi | 8.633 ms |

### 37.2 · İlk teşhisim YANLIŞTI — ve neredeyse ikinci bir sahip yazıyordum

*"Sunum talebinin evi yok"* diye teşhis edip `app/gorsel_talep.py` diye **yeni bir modül**
yazdım. Sonra kaynağı okudum: `ask.py:3648`'de **`SAF GÖRÜNÜM DEĞİŞİKLİĞİ`** dalı zaten
var ve tam doğru şeyi yapıyor — raporu **LLM'siz aynen** döndürüp yalnız `view_hint`'i
değiştiriyor. Modül silindi.

> *Bir evi olmadığını sanıp ikinci bir ev yapmak, `KAT-1`'in kendisidir — ve bu turda
> bir dosya yazıldıktan sonra fark edildi.*

### 37.3 · Gerçek kök — İKİ tane, ikisi de dar

**(a) İsteğin kendi işlev sözcükleri kapsam kapısını kapatıyordu.** Dalın koşulu
*"görünüm kelimeleri sökülünce geriye anlamlı kelime kalmasın"*. Ama artakalan
`bunu pasta grafik yap` → **`bunu`**, `çizgi yerine bar yap` → **`yerine`** idi. İkisi de
**isteğin dilbilgisidir**: işaret zamiri hangi raporu, `yerine` hangi yönü söyler —
ve ikisi de bu dalın kendi ayrıştırıcısı tarafından **tüketilir**. Depoda ölçülmüş
*"ayrıştırıcı tüketti → bilinen sayılır"* kuralının aynısı.

**(b) `bar` ve `pie` sözlükte HİÇ YOKTU.** `_VIZ_MAP` yalnız `pasta`·`sutun`·`cizgi`
tanıyor. Kullanıcının kendi örneği *"bar yerine pie gibi"*ydi ve **iki kelimesi de
tanınmıyordu**. Ayrıca `çizgi yerine bar` sorusunda ilk eşleşme kazanıyor, yani sistem
kullanıcının **terk ettiği** tipi seçiyordu.

⚠ Yeni adlar **ayrı listede** (`_VIZ_TAM`), çünkü **ayrı eşleşme kuralı**: `_VIZ_MAP`
alt-dize eşler (`grafi` → `grafik`/`grafiğe` tutsun diye); aynı kuralı `bar`'a uygulamak
**`barkod`**'u grafik isteği sanardı. `§32`'nin dersi burada da geçerli: *kısa bir dizge
her yere sığar.*

### 37.4 · Doğrulama

| soru | önce | **sonra** |
|---|---|---|
| `bunu pasta grafik yap` | 6.520 ms · LLM · değişiklik yok | ✅ **439 ms · 0 LLM** · `view_hint: pie` · iz: *«saf görünüm değişikliği → pie (rapor korunur, LLM'siz)»* |
| `çizgi yerine bar yap` | 8.633 ms · LLM · değişiklik yok | ✅ **442 ms · 0 LLM** · `view_hint: **bar**` — doğru yön |

## §38 · TAM KAPININ FATURASI — ve ÖLÇÜM ARACINA SIZAN KALINTI

`--hepsi` koşuldu: korpus **yeşil** (`sessiz_yanlis` 12 sabit) ama süit
**5 kırmızı + 15 error** verdi. Beşi de benimdi ve beşi de haklıydı:

| # | ne | sınıf |
|---|---|---|
| 1 | `execute=false` iken `bos_mu` "boş" deyip **SQL çalıştırıyordu** | 🔴 **gerçek gerileme** |
| 2 | `butce.py`·`siralama.py` **sınıfsız modül** (garson/mutfak/muaf) | harita borcu |
| 3 | boş-sonuç çapası `row_count == 0` metnini arıyordu | çapa kayması |
| 4-5 | oylama kapıları `oylar = []` / `_bitis = …` metnini arıyordu | çapa kayması |

🔴 **(1) en pahalısı ve dersi `§33`'ün birebir tekrarı:** `result is None` (ölçüm
yapılmadı) ile `rows == []` (ölçüldü, boş) aynı değere çökertilmişti. *Bir ölçüm
yapılmadıysa «boş» denemez; ölçülmemiş bir küme, boş bir küme değildir.*

### 38.1 · 15 error — ölçüm aracına sızan test kalıntısı

Hepsi `test_measure_preview`/`promote`'un teardown'ıydı: geçici bir eval vakası
(`faz2d-test-gecici-vaka`) **altın dosyada kalmıştı**.

⊙ Sebep bende: iki kapı koşumunu (`kkR`, `kkS`) **ortasında öldürdüm** — teardown
çalışmadı — ve sonraki `git add -A` kalıntıyı **commit etti**. Yani bir test fikstürü
ölçüm korpusuna kalıcı olarak girdi.

> *Bir kapıyı yarıda kesmek onu koşmamaktan kötüdür: koşmayan kapı bir şey söylemez,
> yarıda kesilen kapı arkasında bir kalıntı bırakır — ve `git add -A` onu gerçek sanar.*

Kalıntı `eval/cases.yaml`'dan silindi; 15 error'ın hepsi kapandı.

### 38.2 · İkinci `--hepsi` — ve aynı dersin ÜÇÜNCÜ tekrarı

Beş kırmızı onarıldıktan sonra tam kapı **1 kırmızıya** indi:

```
FAILED tests/test_interpret.py::test_empty_result_returns_none
TypeError: 'NoneType' object is not subscriptable
```

`bos_mu(None, …)`'ı `False` yapınca (`§38`'in 1 numaralı onarımı) `interpret`'in
`result is None` erken dönüşü **kayboldu** ve `result["rows"]` patladı.

⊙ Ama bu bir tasarım hatası değil, **ayrımın kendisinin kanıtı**: iki tüketici aynı
yüklemden farklı şey istiyor —
- `ask.py`'nin not dalı: `None` iken **konuşmamalı** (aksi hâlde `execute=false` SQL koşar)
- `interpret`: `None` iken de **susmalı** (yorumlanacak bir şey yok)

> *Bir ayrımın değeri, iki tarafın ondan farklı şeyler isteyebilmesidir.* Ayrım
> olmasaydı biri ötekinin davranışını taşımak zorunda kalırdı — ki kusur tam olarak oydu.

### 38.3 · Ölçülemeyen kalem — dürüstçe kayıtta

`eval LLM dilimi` her iki koşumda da `coverage -66,7%` verdi ve kapı **yeşil** saydı.
Sebep `§AJ3.4`'ün kayıtlı borcu: **dilim 4 vaka**. Tek bir vakanın yönü %25, üçü %75
oynatır — yani bu sayı bir gerileme sinyali **değildir**, bir ölçüm eksikliğidir.
İki koşumda da aynı çıktığı için bu demetin ürünü de değildir.

> *Paydası üç haneli olmayan bir yüzde, bir ölçüm değil bir izlenimdir.*

## §39 · B TURUNUN BİLANÇOSU — 20 senaryo, 6 kök, hepsi kapandı

**Kapı (son koşum, `--hepsi`):** ✅ **4237 test yeşil** · korpus `{vaka 2285, kabul 1156,
dogru 91, sessiz_yanlis **12**, beyanli_kismi 50}` · `eval` **+0,0%**.

| § | kök | ölçülen (önce → sonra) |
|---|---|---|
| 33 | iki bütçe `with ThreadPoolExecutor` içinde — aşımı ilan edip yine bekliyordu | 39.115 → **21.276 ms** · 82.049 → **22.224 ms** |
| 34 | sıralama, kesme sayısına bağlanmıştı | 4 vaka sırasız → **hepsi sıralı**, `eksik_niyet` kayboldu |
| 35 | boşluk `row_count == 0` sanılıyordu | *«1 satırlık sonuç.»* → **dürüst aralık beyanı** |
| 36 | belgisiz zamir sınıfı yoktu → *"neden"* soruları LLM'e düşüyordu | 23.646 → **1.033 ms** (23×), cevabı **sistem** veriyor |
| 37 | görünüm dalı kendi işlev sözcükleri yüzünden ateşlenmiyordu; `bar`/`pie` sözlükte yoktu | 6.520 → **439 ms** · 8.633 → **442 ms**, ikisi de 0 LLM |
| 38 | `ölçülmemiş` ile `boş` aynı değere çökmüştü | `execute=false` artık SQL koşmuyor |

### Bu turun üç dersi

🔴 **1 · Aynı ders üç kez geldi: iki farklı sebebi tek değere çökertme.**
`ASIM`↔`None` (§33) · `ölçülmemiş`↔`boş` (§38) · `interpret`'in `None`'ı (§38.2).
Üçünde de kusur *"iki durum aynı görünüyor"*du ve üçünde de çözüm ayrımı **isimlendirmek**
oldu. *Bir ayrımın değeri, iki tarafın ondan farklı şeyler isteyebilmesidir.*

🔴 **2 · Metin çapası bir davranışı kanıtlamaz.** `§33`'te üç kapı yeşilken bütçe
çalışmıyordu, çünkü üçü de kaynağa bakıyordu. Yanlarına **süre ölçen** bir kapı kondu ve
kusur **sınıfının** kapısı yazıldı (`with ThreadPoolExecutor` + `result(timeout=)`
birleşimi `app/` altında yasak).

🔴 **3 · Bir evi olmadığını sanmadan önce kaynağı oku.** `§37`'de *"sunum talebinin evi
yok"* diye teşhis edip **yeni bir modül yazdım**; dal `ask.py:3648`'de zaten vardı. Modül
silindi — ama bir dosya yazıldıktan **sonra**. *Yeni bir sahip yazmak, eskisini aramaktan
her zaman kolaydır; `KAT-1` tam olarak bu kolaylıktan doğar.*

### Kapanmayan, kayıtlı kalan üç borç

| # | ne | kanıt |
|---|---|---|
| **G2** | zamir bir **değere** bağlanmıyor: `onun aylık trendini` → 11 makine × 6 ay = 66 satır | `b2` T2 |
| **G4** | *"toplam ciro **nasıl hesaplanıyor**"* bir **tanım** sorusu; sistem *"hangi dönem için?"* diyor — katalog tanımı taşıyor, sorunun evi yok | `b17` |
| **G5** | `bir de **fire ve oee** ekle` → yalnız `fire` eklendi; `ort_oee` chip'te duruyor ama sorguya girmedi | `b14` T2 |

---

# C TURU (başladı)

## §40 · SESSİZ YANLIŞ — ve `§34`'ün kapatmadığı SINIF

### 40.1 · Ölçüm

```
T1: fire oranı yüzde 5 üzerindeki partileri listele  →  "hangi dönem için?"
T2: bu yıl                                            →  tek sayı: 19.79
```

Eşik uygulanmadı, liste gelmedi, **ve hiçbir şey beyan edilmedi** (`eksik_niyet` boş).
Kullanıcı **19.79'u cevap sanabilir** — `sessiz_yanlis` sınıfının tanımı.

### 40.2 · Ayrıştırıcı kusursuzdu — kayıp netleştirme turundaydı

Tek atışlık sondaj:

```
_measure_threshold("fire orani yuzde 5 uzerindeki partileri listele")
  → {'op': '>', 'value': 5.0}     ✅
_measure_threshold("5 milyon uzerinde ciro yapan musterileri listele")
  → {'op': '>', 'value': 5000000.0} ✅
```

Ve `Niyet` de eşiği **sayıyordu**. Kayıp yeri: uyum kapısı **o turun** sorusuna bakar ve
o tur *"bu yıl"*dır — içinde hiçbir eşik yoktur.

🔴 **Bu, `§34.2`'nin birebir aynı sınıfı.** Orada üstünlük niyeti aynı şekilde düşüyordu
ve çözüm **yalnız `order`'a** uygulanmıştı.

> *Bir sınıfı bir örneğinde kapatmak, sınıfı kapatmaz — yalnız bir sonraki örneğini daha
> şaşırtıcı yapar.*

### 40.3 · Kök çözüm — `app/niyet_tasima.py` + KAYITLI BİRLEŞME KURALI

Yeni modül `esik(cq, q)` taşır ve docstring'i borcu **yazılı** bırakır:
`siralama.tamamla` ile aynı sınıftır; **üçüncü** parça geldiğinde ikisi tek bir
`parcalar` kaydında (`(ad, tanı, yerleştir)` üçlüsü) birleşir. Üç kopyaya izin yok.

⚠ Kapı bunu `cube_router`'da bırakmadı (+11 satır → tavan kırmızı) ve **haklıydı**:
kural bir modüle çıktı, harita sınıfı yazıldı (🗣 GARSON).

### 40.4 · Doğrulama

| soru | sonuç |
|---|---|
| `bu yıl fire oranı yüzde 5 üzerindeki makineleri listele` | ✅ 11 satır **doğru veri** + `eksik_niyet:['esik']` + dürüst not — **beyanlı kısmi**, sessiz yanlış değil |
| netleştirme yolu | ✅ eşik artık `cq`'ya yerleşiyor (`esik_tamamla`), niyet turdan sağ çıkıyor |

### 40.5 · Kayıtlı, HENÜZ KAPANMAMIŞ adım

Eşik hâlâ yalnız **beyan ediliyor**, **uygulanmıyor**: `§34`'te `siralama.tamamla` hem
netleştirmeye hem **ortak huniye** bağlanmıştı; `esik` şimdilik yalnız netleştirmede.
Huniye bağlanması beyanlı-kısmiyi **tam cevaba** çevirir ve sıradaki adımdır.

*Bir düzeltmeyi ikizinin yarısı kadar bağlamak, sınıfın yarısını açık bırakmaktır.*

## §41 · C turunun diğer bulguları (kayıtlı)

| # | soru | bulgu |
|---|---|---|
| `c1` | `kumaş türüne göre **ortalama** parti ağırlığı` | ⚠ `toplam_agirlik_kg` verildi — **toplulaştırma türü** `uyum.py`'nin altı ihlal sınıfında **yok** |
| `c3` | `geçen yılın aynı dönemiyle kıyasla` | ✅ *"hangi ölçüyü istiyorsun?"* + chip'ler `period_expr: "geçen yılın aynı dönemi"` taşıyor |

## §42 · YANLIŞ BEYAN — sınıfın eksik bir üyesi yüzünden

**Ölçüm (`c10`):** `2025 ile 2026 **ilk yarısını** kıyasla` → `eksik_niyet:['ustunluk']`
ve cevapta *«**en yüksek/en çok** dedin ama sıralama uygulayamadım»*.
🔴 Kullanıcı öyle bir şey **demedi**.

**Kök:** `_ustunluk_mu`'nun kuralı **zaten doğruydu** — *"ipucundan sonra bir zaman birimi
geliyorsa üstünlük değildir"* (`son 3 ay` bu sayede geçiyor). Eksik olan **sınıfın bir
üyesiydi**: `_ZAMAN_BIRIMI` `yarı`/`yarıyıl`ı tanımıyordu.

> *Bir kuralın yanlış çalışması her zaman kuralın yanlışlığından gelmez; bazen kuralın
> baktığı kümenin eksikliğindendir.*

**Doğrulama:** `2025 ile 2026 ilk yarısını kıyasla` → ✅ *"Hangi ölçüyü istiyorsun?"* +
chip'ler `period_expr: "2025 ile 2026 ilk yarısı"` taşıyor. Yanlış beyan **kayboldu**.

⚠ **KAYITLI BORÇ:** `ilk yarı` bir **dönem olarak da çözülmüyor** (`date_filters("ilk
yari")` boş; oysa `ilk ceyrek` dolu). Bu madde yalnız yanlış beyanı kapatır.

## §43 · SAÇMA BİR YAZIM ÖNERİSİ BİR THREAD'İ ÖLDÜRDÜ

### 43.1 · Ölçüm (`c7`) — ve bedelin iki turda katlanması

```
T1: bu yıl renk bazında ciro dağılımı
    → «"dagilimi" yerine "agirlik" mi demek istedin?»   (rapor YOK)
T2: bunu pie olarak göster
    → source=llm:openrouter · cube=adhoc · toplam_vardiya × gun · 19.836 ms
```

🔴 T1 rapor üretmeyince T2 **çapasız** kaldı ve merdivenin en alt basamağı — **uydurma** —
devreye girdi: LLM alakasız bir `adhoc` sorgu kurdu.

> *Bir turun boş dönmesi o turda bitmez: sonraki tur çapasını kaybeder.*

### 43.2 · Kök

`dağılım` bir ölçü adı değil, bir **görünüm niyetidir** — *"kırılımı göster"* demenin
başka biçimi, `dökümü`·`detay`·`listele` ile **aynı kapalı sınıf**. Sınıf `_LISTE_RE`'de
zaten yaşıyor; eksik olan bir üyeydi. Terim tanınmayınca yazım düzeltici devreye girdi ve
katalogdan en yakın bulduğunu (`agirlik`) önerdi.

### 43.3 · Doğrulama

| tur | önce | **sonra** |
|---|---|---|
| T1 | saçma öneri, rapor yok | ✅ **1.291 ms · `source=cube` · 0 LLM** · `cq={parti, toplam_ciro, dims:[renk]}` |
| T2 | 19.836 ms · uydurma `adhoc` | ✅ **559 ms · `source=cube`** · `view_hint: pie` · 5 satır korundu |

## §44 · C turunun kalan bulguları (kayıtlı, açık)

| # | soru | bulgu |
|---|---|---|
| `c4` | `mart ile nisan arasındaki fire **farkını** açıkla` | 🔴 `fark` bir **ölçü adı** (`enerji_sapma`) sanıldı → çapraz-konu reddi. Oysa iki adlı dönem + *"arasındaki fark"* ders kitabı **kıyas**tır. Sözcük çakışması sınıfı (`varlik.py`'deki `ciro` ile aynı) |
| `c11` | `ciro ve fire arasında **ilişki** var mı` | ⚠ İki ölçü döndü, ilişki ne hesaplandı ne **reddedildi**. `c4`'te aynı sınır **güzelce** konuşuyor (*"ilişki bir çıkarımdır"*) — demek sınır yalnız **çapraz-cube**'da ateşleniyor, aynı cube'da susuyor |
| `c5` T2 | `neden diğerlerinden iyi` | ✅ §36 çalıştı (585 ms, 0 LLM) + **matematiksel olarak dürüst** red (*"ort_oee bir oran — katkı payı tanımsız"*). ⚠ Ama *ne yapabileceğini* söylemiyor |
| `c6` | `duruş süresi en yüksek 5 makine` → `bunların oee'si ne` | ✅ **gerçek agentic zincir**: 518 ms top-5, sonra **aynı 5 makineye** ölçü eklendi, sıra+limit korundu |
| `c9` | `kalite red oranı nedir` | ⚠ `fire_orani_yuzde`'ye eşlendi; ikame **beyan edilmiyor** |

## §45 · `\b` TÜRKÇE EKİ GÖREMİYOR — kural yarısında ölüydü

### 45.1 · Ölçüm

`§42` konduktan **hemen sonra** aynı yanlış beyan başka bir cümlede çıktı:

| soru | eskiden | sebep |
|---|---|---|
| `son 3 **ay** ciro` | ✅ geçiyordu | ek yok |
| `son 3 **ayın** ortalama günlük üretimi` | 🔴 *«en yüksek/en çok dedin»* | **ek var** |

### 45.2 · Kök — tek karakter

`_ustunluk_mu`'nun deseni `{_ZAMAN_BIRIMI}\b` idi. `ay\b`, `ayin` içinde **`y` ile `i`
arasında** bir sözcük sınırı arar — ve orada sınır **yoktur**. Yani kural zaman biriminin
**çekimsiz** hâlinde çalışıyor, **çekimli** hâlinde susuyordu.

🔴 Ve Türkçede dönem ifadeleri neredeyse **her zaman** çekimlidir: `ayın`·`ayda`·`aylık`·
`yılın`·`çeyreğin`. Yani kural, gerçek cümlelerin çoğunda **hiç çalışmıyordu**.

> *Bir sınır kontrolü, sınırladığı dilin biçimbilgisini tanımıyorsa yalnız o dilin en
> yalın hâlinde çalışır — ve gerçek cümleler yalın değildir.*

### 45.3 · Ve kapı bir ikinci katmanı daha buldu — ÜNSÜZ YUMUŞAMASI

`\w{0,4}` eklendikten sonra yeni yazdığım kapı `son çeyreğin karlılığı` ile **kırmızı**
verdi: `çeyrek` + ek → **`çeyreğ`**. Kök `k` ile bitiyor ve ek alınca **kökün kendisi
değişiyor** (`k→ğ`), yani hiçbir sağ-taraf genişlemesi onu yakalayamaz.

`ceyre[kg]` yazıldı. *Bir kökü tanıyıp yumuşamışını tanımamak, aynı kelimenin yarısını
bilmektir.*

⚠ **Sağ taraf bilerek DAR** (`\w{0,4}`): sınırsız olsaydı `ay` ile başlayan her kelime
(`ayrıntılı`) zaman birimi sayılırdı — `§32`'nin dersi. Kapı bunu ayrıca sınıyor.

### 45.4 · Doğrulama

`son 3 ayın ortalama günlük üretimi` → ✅ yanlış beyan **kayboldu**; notta yalnız meşru
cube-belirsizliği açıklaması kaldı (14.053 ms).

**Yeni kapılar (11):** yedi dönem ifadesi üstünlük **sayılmayacak** · üç gerçek üstünlük
**sayılmaya devam edecek** (gevşemenin sınırı) · ek penceresi **sınırsız olmayacak**.

## §46 · KATALOG KEŞFİ KAPISI VERİ SORUSUNU YUTUYORDU — sınırsız bir `.*`

### 46.1 · Ölçüm — ve düşen cümleler kullanıcının KENDİ tarzı

| soru | sonuç |
|---|---|
| `bu yıl makine bazında fire oranını kıyasla ve **listele** ve en yüksek olanı **analiz et**` | 🔴 `source=catalog` — **tüm menü dökümü** |
| `bu yıl kar marjı en düşük 3 müşteri ve nedenini **analiz et**` | 🔴 *«"analiz" başka bir konu gibi görünüyor»* |
| `bu yıl vardiya bazında oee **yorumla**` | ✅ çalışıyor |

Kullanıcının bu tur için verdiği örnek aynen böyleydi: *"…en düşüğün neden diğerlerinden
düşük olduğunu bul **analiz et**"*.

### 46.2 · İki kök, iki kat

**(a) Kapsam kapısı konuşma fiillerini bilinmeyen sayıyordu.** `_ANLAT` `analiz et`'i
**zaten** tanıyor — ama `followup.sinifla()` yalnız **takip** turunda koşar; taze soruda
`route()` o sözcükleri *"tanımadığım bir konu"* sayıyordu.
⊙ Depoda ölçülmüş *"ayrıştırıcı tüketti → bilinen sayılır"* kuralının **üçüncü** örneği
(`ustunluk_sozcukleri` · `_LISTE_RE` · bu).
⚠ **Kelime listesi yazılmadı:** sınıflandırıcının **kendi** kalıpları çağrılıyor
(`followup.konusma_sozcukleri`), yoksa iki taraf ayrışırdı — ki kusur bir kat aşağıda tam
olarak buydu.

**(b) 🔴 Asıl kök: `_is_catalog_query`'de SINIRSIZ bir `.*`.**

```python
r"\b(hangi|neler|ne\s+tur|listele|liste|mevcut)\b.*(kpi|rapor|metrik|olcu|analiz|oran|…)"
```

Cümlenin **başındaki** `listele` ile **sonundaki** `analiz` eşleşiyor; aradaki gerçek soru
görünmüyor. Yani iki yaygın sözcüğü içeren her uzun cümle bir *"katalog keşfi"* sayılıyordu.

### 46.3 · Kök çözüm — yapısal ayrım

> Katalog keşfi katalog **hakkında** bir sorudur; veri sorusu katalog **ile** sorulur.

Soruda gerçek bir ölçü/boyut/dönem varsa kullanıcı *ne sorabileceğini* değil **cevabı**
istiyordur. Yüklem **yeni yazılmadı**: `veri_niyeti_var` zaten bu iş için var (`D1`,
sosyal kapı) ve `KAT-1` ikinci bir sahip yasaklıyor.

> *Bir menüyü, yemeği söyleyen müşteriye uzatmak, onu dinlememektir.*

### 46.4 · Doğrulama — iki yön

| soru | önce | **sonra** |
|---|---|---|
| `…fire oranını kıyasla ve listele ve en yüksek olanı analiz et` | menü dökümü | ✅ **913 ms · `source=cube` · 0 LLM** · RAM-2 %22,12 · `order:desc + limit:1` · tek eksik (`kiyas`) **beyan edildi** |
| `neler sorabilirim` *(gerileme kontrolü)* | katalog | ✅ **aynı**, 375 ms |

### 46.5 · KORPUS KIPIRDADI — ve doğru yönde

`§46` bu operasyonda korpus sayılarını **oynatan ilk değişiklik** oldu:

| ölçüt | önce | **sonra** | okuma |
|---|---|---|---|
| `dogru` | 91 | **93** | 🔴 **+2 — en katı ölçüt yükseldi** |
| `beyanli_kismi` | 50 | **51** | +1 — bir vaka dürüst beyana dönüştü |
| `kabul` | 1156 | 1153 | −3 (yukarıdaki üçü buradan çıktı) |
| `sessiz_yanlis` | 12 | **12** | ✅ sabit — doğruluk vetosu geçildi |
| doğru-cube | %95,1 | %95,1 | sabit |

⊙ Üç vaka *"kabul"*ten çıktı: **ikisi doğru cevaba**, biri **beyanlı kısmiye**. `kabul`
düşerken `dogru` yükselmesi bir kayıp değil bir **keskinleşme**dir: aynı sorular artık
daha kesin sınıflanıyor.

⚠ Ve `CLAUDE.md`'nin uyardığı tersi desen **burada yok**: orada *"sistem bozulurken sayı
iyileşir"* (payda düşerse doğruluk yükselir) anlatılıyor. Burada **payda sabit** (2285) ve
yükselen şey mutlak sayı — yani iyileşme gerçek.

> *Bir metriğin yükselmesi ancak paydası sabitken bir kazançtır.*

---

# D TURU — **EN ÜST KURALIN İLK ÖLÇÜMÜ**

## §47 · GARSONUN KARARI GÖRÜNMEZDİ *(ölçüm aleti onarımı)*

**Ölçüldü:** `show me total revenue by customer this year` → *"anlayamadım"*. Logda:
**üç LLM çağrısı başarılı**, **sıfır** whitelist reddi, **sıfır** uyuşmazlık chip'i.
Yani üç oy bir yere gitti ve **nereye gittiği hiçbir yerde yazmıyordu**.

Sebep: `_select_consistent.one()`'ın `except Exception: return None` dalı — **log yok**
(`ADR-0020` *"sessiz yutma yok"* ihlali). Ve kazanan oyun **oranı** da yazılmıyordu.

> *Bir çağrının başarısı loglanıp başarısızlığı yutuluyorsa, log bir kanıt değil bir
> reklamdır.*

Onarıldı: düşen oy `WARNING` + `exc_info`; her turda `intent: N oy · M farklı aday ·
kazanan K oy`. **Ve bu satır kökü tek turda gösterdi.**

## §48 · 🔴🔴 GARSON ANLADI, MUTFAĞA GİDEN GİRDİ **SİSTEMİN KENDİ AYRIŞTIRICISINDA** BOZULDU

### 48.1 · Ölçüm — iki dil, tek desen

| # | soru | garson ne yaptı | kullanıcı ne gördü |
|---|---|---|---|
| `d1` | `show me total revenue by customer this year` *(İngilizce)* | ✅ `intent: 3 oy · 1 farklı aday · **kazanan 3 oy**` → `{parti, toplam_ciro, dims:[musteri]}` | 🔴 *"toplam ciro çıkarabilirim — **hangi dönem için?**"* |
| `d2` | `ما هو إجمالي الإيرادات لهذا العام` *(Arapça)* | ✅ 3 oy → `{parti, toplam_ciro}` | 🔴 *"…**hangi dönem için?**"* |

⊙ **Garson kusursuz çalıştı.** Oybirliği. Ölçüyü de, kırılımı da doğru çevirdi — hem
İngilizceden hem Arapçadan. `this year` / `لهذا العام` ifadesini de **anladı**.

🔴 **Kaybolan yer:** dönem, `cq`'ya **çözülmüş bir filtre olarak değil**, `period_expr`
diye **serbest metin** olarak giriyor; sistem onu **`date_filters` ile — yani Türkçe-only
deterministik ayrıştırıcıyla — yeniden çözüyor**. İngilizce/Arapça metin orada boş döner,
dönem düşer, `_period_gate` ateşlenir.

### 48.2 · Bu, EN ÜST KURALIN tam olarak tarif ettiği kusur

`§0.0`'ın teşhis kuralı: *"Garson devreye girdi ve sisteme sorunsuz doğru bir girdi
sağladıysa ama yine çalışmadıysa, sorun mutfaktadır."*

Burada garson doğru girdiyi sağladı **ama sınırda geri alındı**: sistem, dil modelinin
anladığı şeyi kendi kelime kuralına **yeniden sordu** ve cevabı beğenmeyince attı.

> *Bir çevirmene güvenip çevirisini kendi sözlüğünle yeniden denetlemek, çevirmeni hiç
> çağırmamakla aynı sonucu verir — yalnız daha pahalıya.*

### 48.3 · Kök çözüm yönü *(sıradaki iş)*

Dönem, garsonun **anladığı** biçimde `cq`'ya girmeli:
* ya garson **çözülmüş** `filters` (ISO tarih) üretir — sistem ona **bugünün tarihini**
  verir, çünkü tarihi bilen sistemdir;
* ya da `period_expr` çözülemediğinde **garsona normalize ettirilir** — asla *"hangi
  dönem?"* diye kullanıcıya dönülmez.

⚠ Değişmez korunur: **sayıyı yine küp koyar.** Tarih bir **filtredir**, bir sayı değil —
garsonun oraya dokunması `MIMARI`'nin *"LLM önerir, motor doğrular"* ilkesini bozmaz.

⚠ `KURAL B`: bayrakla kapatılabilir, kapalıyken davranış birebir bugünkü.

### 48.4 · Yan bulgu — aynı turda LLM belirsizliği

`d1` **iki kez** koşuldu: ilkinde *"«show total customer this year» kısmını
anlayamadım"*, ikincisinde *"hangi dönem için?"*. Aynı soru, aynı sistem, **iki farklı
cevap**. Bu, garsonun belirlenimsizliğinin **kullanıcıya sızdığını** gösterir ve
`consistency_k=3` oylamasının onu tamamen örtmediğini.

### 48.5 · Kök çözüm — **garson dönemi de ÇEVİRİR** *(ADR-0008 K3 korunarak)*

Prompt'taki talimat *"dönem ifadesini **AYNEN kopyala**"* idi. Bu, garsondan **cümlenin
yarısını çevirip yarısını olduğu gibi bırakmasını** istemekti.

Yeni talimat (her iki prompt'ta da):

> *Soru başka bir dildeyse dönem ifadesini **sistemin dilinde** yaz — `this year`→«bu
> yıl», `هذا العام`→«bu yıl», `since January`→«ocaktan beri». Soru zaten Türkçeyse aynen
> kopyala. **TARİHİ YİNE SEN HESAPLAMA** — çeviriyorsun, hesaplamıyorsun.*

🔴 **`ADR-0008 K3` (*"LLM tarih YAZMAZ"*) bozulmadı, GEREĞİ yapıldı:** tarihi hâlâ Python
hesaplıyor; garson yalnız **kullanıcının dilinden sistemin diline** çeviriyor — tıpkı
ölçü ve boyut adlarında yaptığı gibi. Dönem, katalogda olmayan **tek** alandı ve tam da o
yüzden yabancı dilde düşüyordu.

### 48.6 · Doğrulama

| # | soru | önce | **sonra** |
|---|---|---|---|
| `v48a` | `show me total revenue by customer this year` | *"anlayamadım"* / *"hangi dönem?"* | ✅ **7.552 ms · 8 satır** · `filters:[tarih ≥ 2026-01-01]` |
| `v48b` | `ما هو إجمالي الإيرادات لهذا العام` | *"hangi dönem?"* | ✅ **12.374 ms** · `toplam_ciro` + doğru yıl filtresi |
| `v48c` | `compare this year with last year revenue` | *"anlayamadım"* | 🔴 **hâlâ kırık** — ayrı kök *(aşağıda)* |

## §49 · KALAN KÖK — **İKİ-DÖNEM KIYASI** *(sonraki demet)*

Aynı desen iki dilde:

| soru | sonuç |
|---|---|
| `compare this year with last year revenue` *(İngilizce)* | 🔴 *"anlayamadım"* |
| `şubattan ocağa fire nasıl değişti` *(Türkçe)* | 🔴 yalnız **şubat** kaldı; *"ocağa"* düştü, `eksik_niyet:['trend']` |

⊙ Yani kusur **dilden bağımsız**: `period_expr` **tek** bir dönem taşıyabiliyor; iki
dönemli bir kıyas ifadesi ya yarısını kaybediyor ya tamamen çözülemiyor.

⚠ Depoda karşılığı **var**: `kiyas_cebiri` · `compare_mode` · `referans` ekseni. Yani bu
bir **mutfak eksiği değil**, bir **taşıma** eksiği: garsonun anladığı iki dönem `cq`'ya
girecek alanı bulamıyor (`§AJ4.1`'in kayıtlı borcu: `referans` Intent-JSON şemasında yok).

## §50 · D TURUNUN ÇALIŞAN TARAFI — kanıt için

| # | soru | sonuç |
|---|---|---|
| `d4` | `hangi makine en çok bozuluyor **ya**` *(argo)* | ✅ `bakim` · `ariza_sayisi` · `dims:[makine]` · **`order:desc`** — 8.032 ms |
| `d6` | `makinlerin **frie** oranlarnı listele` *(ağır yazım hatası)* | ✅ `fire_orani_yuzde` × `makine` — 3.924 ms |
| `d7` | `which shift has the lowest efficiency and why` *(İngilizce)* | ◐ küp/boyut **doğru** (`oee` × `vardiya`, 4 ölçü); `lowest` sıralamaya, `why` kök-nedene **bağlanmadı** |
| `d8` | `bu yıl müşteri bazında kar marjı ve bunu pasta yap` | ✅ veri doğru (`kar_marji_yuzde` × `musteri`, bu yıl) |

⊙ Argo · ağır yazım hatası · yabancı dil — üçünde de **garson işini yaptı**. Bu, en üst
kuralın lehine doğrudan kanıttır: route bu üç sınıfın hiçbirini tek başına çözemezdi.

## §51 · ŞÜPHE GARSONU ÇAĞIRIR — en üst kuralın ilk uygulaması *(KISMEN AÇIK)*

### 51.1 · Ölçülen kök

`_try_fresh_intent`'in garson dalı `route_hit is None` ile bağlıydı: **route herhangi
bir şey bulduysa**, o şey ne kadar eksik olursa olsun, garson **hiç** devreye girmiyordu.

| soru | route ne yaptı | kullanıcı ne gördü |
|---|---|---|
| `top 5 customers by profit this quarter` | ölçü+boyut buldu; `top 5` ve `this quarter` **düştü** | *"hangi dönem için?"* |
| `en çok duruş yaşayan hattı bul ve nedenini **açıkla**` | 🔴 **uydurma** değer filtresi: `neden = "Açık"` *(«açıkla» → «Açık»)* | *"hangi dönem için?"* |
| `geçen hafta hangi gün en verimliydi` | yanlış küpler önerdi (bakım/cari/kalite) | *"hangi ölçüyü istiyorsun?"* |

⊙ `§0.0`: *"aşçı **kesinlikle** duyduysa hemen yapar; en ufak anlamama varsa garson
gider."* **Yarım duymak bir duyma değildir** — ve `d10`'da yarım duyma bir **uydurmaya**
dönüştü: sahte kesinlik garsonu engelledi.

### 51.2 · Uygulama

* Yüklem `niyet_tasima.route_supheli` — route'un `cq`'sunda dönem yoksa ya da üstünlük
  istenip sıralama kurulmadıysa **şüphe** vardır.
* Koşul `route_hit is None` → **`route_hit is None or _supheli`**.
* ⚠ Garsonun sonucu **yalnız şüpheyi gideriyorsa** alınır: *bir devir, elde olanı
  kötüleştirmemelidir.*

### 51.3 · 🔴 VE İLK YAZIMIM KENDİ KURALINI ÇİĞNEDİ

Şüphe yüklemi ilk hâlinde `\b(bu|gecen|son|ilk|…)\b` diye bir **Türkçe** dönem sözcüğü
arıyordu. Ölçüldü: `top 5 customers by profit this quarter` → hiçbir Türkçe sözcük yok →
şüphe **yok** sayıldı → garson **yine** çağrılmadı.

> *Bir kuralın uygulaması, kuralın yasakladığı şeyi yapmamalıdır.*

Dil-bağımsız hâle getirildi: **route dönemi hiç kuramadıysa şüphe vardır.** Kullanıcının
dönemden söz edip etmediğini anlamak **garsonun** işidir, bu yüklemin değil.

### 51.4 · Durum — açık, kanıtıyla

✅ **Garson artık şüphede çağrılıyor.** Log kanıtı (`§47` sayesinde görünür):

```
intent: 3 oy · 1 farklı aday · kazanan 2 oy      ← garson çağrıldı
```

🔴 **Ama vaka kapanmadı:** cevap hâlâ *"hangi dönem için?"*. Garsonun `cq`'su da dönemsiz
geldiği için *"yalnız daha iyisini al"* süzgeci onu reddetti. İki olası sebep, ikisi de
ölçülmeli:

1. `period_expr` üretilmedi ya da `bu çeyrek` çevirisi yapılmadı *(§48'in kapsamı)*
2. uyum oranı **2/3** — eşiğin tam sınırında; oy dağılımı `1 farklı aday` olduğuna göre
   üçüncü oy **çekimser** (`{cube:null}`) olmalı

⊙ Sıradaki iş bu ikisini ayırmaktır — ve `§47`'nin log satırı artık bunu **tek turda**
söyleyebilecek durumda.

### 51.5 · D turunun tam envanteri (20 senaryo)

**Çalışan (7):** `d4` argo · `d6` ağır yazım hatası · `d8` veri+grafik · `d11` hedef
(kısmi) · `d13` **İngilizce takip** (5.011 ms, ölçü eklendi) · `d18` en iyi 3 + renk ·
`d20` boş aralık beyanı

**Kırık (kök sınıfına göre):**

| kök | kanıt |
|---|---|
| **§49 iki-dönem kıyası** | `d3` `şubattan ocağa` · `d5` `compare this year with last year` · `d9` `geçen yıl ile bu yılı kıyasla` |
| **§51 route'un yarım başarısı** | `d10` · `d12` · `d15` |
| **ölçü ikamesi beyan edilmiyor** | `d16` *"fire **maliyetimiz**"* → `toplam_fire_kg` (**kg**, ₺ değil) · `c1` ortalama→toplam · `c9` kalite red→fire oranı |
| **`analiz`/`ilişki` çapraz-konu reddi** *(§46 yarım kaldı)* | `d17` `…ilişkiyi **analiz et**` → *"«arasindaki analiz» başka bir konu"* |
| **paylaş/özetle Discovery'ye düşüyor** | `d19` `bu raporu müdüre 3 cümleyle özetle` → `cube=adhoc` 🔴 **mutfak eksiği raporu** |
| **yanlış kırılım beyanı** | `d9` `ciro **bazında**` → `eksik_niyet:['kirilim']` |

---

# E TURU — 20 özgün senaryo · thread'li · agentic

## §52 · Envanter

### Çalışan (8)

| # | soru | sonuç |
|---|---|---|
| `e1`T1 | `makinelerin bu yılki verimliliğini göster` | ✅ **1.263 ms** `cube` |
| `e1`T3 | `en zayıf olanı nasıl iyileştiririz` | ✅ **494 ms · 0 LLM** · dürüst matematiksel red (*"oran — katkı payı tanımsız"*) |
| `e7` | `bu yıl haftalık fire` → `ısı haritası yap` | ✅ 514 ms → **469 ms** · `view_hint: heatmap` · rapor korundu |
| `e13` | `bu yıl hangi renkte en çok fire veriyoruz` | ✅ 8.269 ms · `order:desc` · 5 satır |
| `e16`T1 | `bu yıl günlük üretim trendi` | ✅ **478 ms** · 155 satır |
| `e17` | `show downtime by line as a pie chart` *(İngilizce)* | ✅ küp+ölçü+boyut doğru (`makine_duruslari` × `hat`) |
| `e18` | `en yüksek ve en düşük vardiyayı aynı grafikte` | ✅ 3 satır sıralı · `view: chart` |
| `e20` | `bu yıl ciro` → `aylara böl` → `en kötü ayı bul…` | ✅ **uzun zincir**: 495 ms → 6 satır → `order:asc + limit:1` |

### Kök sınıfları (5)

**🔴 R-E1 · ÇAPRAZ-KONU REDDİ İŞLEV SÖZCÜKLERİNİ KONU SANIYOR — 4 kanıt (bu turun baskın kusuru)**

| soru | reddedilen "konu" |
|---|---|
| `aylık üretim ve enerji tüketimini **birlikte** göster` | *"«birlikte» başka bir konu gibi görünüyor"* |
| `which machines had the highest downtime last month` | *"«which had the highest last month» başka bir konu"* |
| `bakım maliyeti ile arıza sayısı **ilişkili** mi` | *"«bakim maliyeti iliskili» başka bir konu"* |
| `personel çalışma süreleri…` | *"«personel sureleri» başka bir konu"* |

⊙ `§46` bu sınıfı **iki** dalda kapatmıştı (kapsam kapısı + katalog dökümü); **üçüncü**
dal — `partial_unknowns` çapraz-konu reddi — açık kaldı. `birlikte`·`ilişkili` bağlaç ve
sıfattır; İngilizce sözcükler ise **hiçbir konunun** adı değildir.

**🔴 R-E2 · DISCOVERY ATEŞLEMESİ = MUTFAK EKSİĞİ RAPORU — 4 kanıt**

| soru | uydurulan ölçü | süre |
|---|---|---|
| `ortalama parti süresi nedir` | `toplam_ortalama_parti_suresi_dk` | 16.655 ms |
| `bu yıl enerji maliyetimiz ne kadar` | `toplam_toplam_enerji_maliyeti_tl` | **49.311 ms** |
| `stok devir hızımız ne` | `toplam_stok_devir_hizi_kg` | 🔴 **63.526 ms** |
| `bu çeyrek geçen çeyreğe göre nasıl` | `toplam_bu_ceyrek_oee` | 31.005 ms |

⊙ `§0.0`'a göre bunlar **çözüm değil arıza raporudur**: mutfakta *ortalama parti süresi*,
*enerji maliyeti*, *stok devir hızı* ölçüleri **yok**.
🔴 Ve ikinci bir kusur: **Discovery yolunda bütçe yok** — 63,5 sn'lik bir tur `§33`'ün
kapattığı iki bütçenin de dışında.

**⚠ R-E3 · SESSİZCE UYGULANMAYAN FİLTRE** — `sadece hafta içi günleri göster` → **155
satır aynen** döndü, filtre uygulanmadı, **beyan da edilmedi**. (`hafta_gunu` boyutu
katalogda **var**.)

**⚠ R-E4 · ÜSTÜNLÜK+SAYI yabancı dilde/parafrazda düşüyor** — `أفضل 5 آلات` (Arapça
*"en iyi 5 makine"*) → küp/ölçü/boyut doğru, **sıra ve limit yok**; `en çok ciro getiren
3 müşteri` → `order` var, `limit 3` yok.

**⚠ R-E5 · ZAMİR KIRILIMI TAŞIMIYOR** — `bunların karlılığa etkisi ne` → küp doğru
değişti (`oee`→`maliyet`) ama **`makine` kırılımı düştü**; sonuç tek bir toplam.

## §53 · Bu turun okuması — iki eksenin ölçülmüş dağılımı

`§0.0`'ın teşhis kuralı bu 20 senaryoyu **temiz** ayırıyor:

| eksen | kaç kök | ne yapılacak |
|---|---|---|
| 🗣 **sipariş alma** (garson) | R-E1 · R-E4 · R-E5 | garsona devret / niyeti taşı — **route'a dil öğretme** |
| 🍳 **mutfak** (küpler) | R-E2 *(4 eksik ölçü)* · R-E3 | küpe ölçü/filtre **ekle** |

⊙ Yani bu tur, kullanıcının kurduğu ayrımın **işlediğini** gösteriyor: bir kusura bakıp
hangi eksene ait olduğunu söylemek artık bir tartışma değil, bir **okuma**.

## §54 · İŞLEV SÖZCÜKLERİ BİR KONU DEĞİLDİR — süzgeç **yalnız gösterimdeydi**

Süzgeç (`_islev_sozcugu`) vardı ama **cümleyi güzelleştiriyordu**; dalın **ateşlenmesini**
engellemiyordu. Sistem anlamadığını **gizliyor**, yine de **reddediyordu**.

Yapılan: süzgeç **kapıya** çevrildi (adlandırılacak konu kalmadıysa dal düşer, merdiven
devam eder) + İngilizcenin **kapalı** sınıfları eklendi (artikel · yardımcı · soru
sözcüğü · edat · **zaman birimi**) — `ADR-0008` bunu serbest bırakır, çünkü bunlar bir
alan sözlüğü değil **dilbilgisidir**.

| soru | önce | **sonra** |
|---|---|---|
| `aylık üretim ve enerji tüketimini **birlikte** göster` | *"«birlikte» başka bir konu"* | ✅ **9.596 ms** · 30 satır |
| `which machines had the highest downtime last month` | *"«which had the highest last month» başka bir konu"* | ✅ **14.168 ms** · `makine_duruslari` × `makine` + temmuz filtresi + dürüst boş-aralık beyanı |

> *Bir cümlenin dilbilgisi, o cümlenin konusu değildir.*
> *Bir cümleyi reddetmek için, reddedilen şeyin adı olmalıdır.*

⚠ **§56 · KAYITLI BORÇ — bu liste UZAMAMALI.** Her yeni dilde yeni bir kapalı sınıf
yazmak, `§0.0`'ın yasakladığı *"route'a dil öğretme"*nin başka bir biçimidir. Yapısal
çözüm: **garson bir aday ürettiyse Türkçe kapsam reddi hiç koşmamalı** — o reddin dayanağı
Türkçe bir sözlüktür ve soru Türkçe değildir. *Bir listeyi uzatmak, listenin yanlış araç
olduğunu gizler.*

## §55 · EN GÜVENMEDİĞİMİZ BASAMAK EN UZUN BEKLETİYORDU

`§33` iki bütçe onarmıştı (Intent oyları · T2 anlatısı) ama **Discovery açıkta kaldı** —
ve `§0.0`'a göre o *"yan dükkândan sipariş"*, yani **hiç güvenmediğimiz** basamak.

| soru | önce | **sonra** |
|---|---|---|
| `stok devir hızımız ne` | 🔴 **63.526 ms** → uydurma `adhoc` ölçü | ✅ **34.301 ms** → *"zamanında güvenilir bir sorgu üretemedim"* |

⚠ Aşımda **cevap düşmez, yol düşer**: dürüst ret zaten oradaydı. En kötü durum
*"yapamadım"* — bir dakika bekletip *"yapamadım"* demekten iyidir.

> *En güvenmediğimiz basamağın en uzun bütçeye sahip olması, bir sıralama hatasıdır.*

⊙ Ve `§0.0`'ın okumasıyla: bu dört tur (`ortalama parti süresi` · `enerji maliyeti` ·
`stok devir hızı` · çeyrek kıyası) birer **mutfak eksiği raporudur**. Bütçe onları
**susturmaz**, yalnız faturasını düşürür — asıl iş küplere o ölçüleri **eklemektir**.

## §56 · GARSON KONUŞTUYSA TÜRKÇE KAPSAM REDDİ SUSAR — `§54`'ün listesini gereksiz kılan madde

`§54` kelime listesiyle yamamıştı ve o yamanın kendisi borç olarak kaydedilmişti
(*"liste uzamamalı"*). Yapısal cevap:

> **Garson bir aday ürettiyse o cümlenin konusu VARDIR — yalnız dili farklıdır.**
> Türkçe sözlüğe dayanan bir reddin orada söz hakkı yoktur.

⚠ Kapsam dar: garson **hiç** konuşmadıysa (kota yok, bayrak kapalı) dal aynen çalışır —
en kötü durum bugünkü davranış (`KURAL B`).

| soru | önce | **sonra** |
|---|---|---|
| `bakım maliyeti ile arıza sayısı ilişkili mi` | *"«bakim maliyeti iliskili» başka bir konu"* | ✅ **30 satır cevap** |
| `personel çalışma süreleri ve verimliliklerini kıyasla` | *"«personel sureleri» başka bir konu"* | ✅ **29 satır cevap** |

⊙ İkisi de `cube=adhoc` — yani `§0.0`'a göre birer **mutfak eksiği raporu**. Bu **doğru
davranıştır**: kullanıcı artık reddedilmiyor, eksik olan **görünür** oluyor.

> *Bir cümleyi tanımayan sözlük, o cümle hakkında hüküm veremez.*

⚠ **Yeni kayıt:** `bakim_is_emri` küpünde `bakim_maliyeti` ölçüsü **var** (chip'lerde
görüldü) — garson yanlış küpe gitti. Yani bu vaka bir mutfak eksiği **değil**, bir
**sipariş** kusuru; `§53`'ün eksen ayrımı bunu bir sonraki turda ayırmalı.

## §57 · Kapı kırmızısı ve onarımı *(E demeti)*

| kırmızı | sınıf | onarım |
|---|---|---|
| `test_KISMI_ANLAMA_CUMLESI_KELIME_SAYMIYOR` | çapa kayması — `§54` yorumları `+1600` penceresini taşırdı | pencere **genişletildi** (silinmedi): *bir çapa, çakıldığı tahta büyüdükçe yerini korumaz* |
| `test_ASK_PY_DOSYASI_ASK_DISINDA_SESSIZCE_SISMIYOR` | dosya tavanı — kelime listesi modül düzeyinde büyüdü | liste **`app/islev_sozcukleri.py`'ye taşındı** — kapının kendi talimatı |

⊙ İkinci onarım bir yan kazanç verdi: borç artık **kendi dosyasında** ve o dosyanın
docstring'i **kapanış koşulunu** taşıyor (*"`§56` yapıldığında bu dosya silinir"*).
*Bir dosyanın adı, içindeki şeyin ne olduğunu söyler.*

---

# F TURU — 20 yeni özgün senaryo

## §58 · ÖZEL TİP, GENEL SÖZCÜĞE YENİLİYORDU

**Ölçüldü (`f19`):** `bunu **bar** grafikle göster` → `view_hint: **chart**`.
Sıra kusuru: `_VIZ_MAP` önce taranıyor ve orada `grafi` **var**; `bar` ise `_VIZ_TAM`'da,
yani **sonra**. Kullanıcı *"bar"* dedi, sistem *"grafik"* duydu.

**Kural:** özel bir tür adı, genel bir tür sözcüğünü **yener**. `bar grafik` bir grafik
isteğidir ama **hangi** grafik olduğu da söylenmiştir; genel olanı seçmek, cümlenin daha
bilgilendirici yarısını atmaktır.

> *İki ad aynı şeyi gösteriyorsa, dar olanı seçilir — geniş olan zaten onun içindedir.*

## §59 · F turunun envanteri

### Çalışan (11)

| # | soru | sonuç |
|---|---|---|
| `f1` | `bu yıl hangi hat en çok çalıştı` | ✅ 9.543 ms · `order:desc` · 8 satır |
| `f6`T1 | `kumaş cinsine göre fire` | ✅ **492 ms** |
| `f7` | `wie hoch war der Umsatz dieses Jahr` *(**Almanca**)* | ✅✅ **13.935 ms** · `toplam_ciro` + yıl filtresi — `§48` **genelleşti** |
| `f9` | `bu yıl günlük enerji tüketimi` | ✅ **523 ms** · 155 satır |
| `f11` | `hangi operatör en az hata yapıyor` | ✅ `kalite` × `operator` · **`order:asc`** *(doğru kutup)* · 9 satır |
| `f12` | `bu yıl aylık ciro` → `tabloya çevir` | ✅ 493 ms → **448 ms** · `view: table` |
| `f13` | `ortalama sipariş büyüklüğü` | ✅ **490 ms** |
| `f14` | `makine bazında oee` → `en düşük ikisini al` | ✅✅ 501 ms → `order:asc` + **`limit:2`** · 2 satır |
| `f16` | `show me a breakdown of waste by fabric type` *(İngilizce)* | ✅ 4.178 ms · doğru `cq` |
| `f18` | `haftanın hangi günü en verimliyiz` | ✅✅ `hafta_gunu` × `order:desc` · 6 satır |
| `f19`T1 | `enerji yoğunluğu trendi` | ✅ **487 ms** |

⊙ `f18` ayrıca bir **kanıt**: `hafta_gunu` boyutu **var** — yani `e16`'daki *"sadece
hafta içi"* sessiz atlaması gerçek bir kusurdu, bir kapasite sınırı değil.

### Kalan kökler

| # | kanıt | sınıf |
|---|---|---|
| **RF-a** `kır` bir KIRILIM isteğidir | `f14`T3 `bunların duruş nedenlerini **kır**` → kök-neden reddi döndü (*"oran — katkı payı tanımsız"*); oysa istenen `neden` boyutunu eklemekti | 🗣 sipariş |
| **RF-b** ölçü ikamesi **beyan edilmiyor** *(5. kanıt)* | `f4` `bakım maliyetleri` → **`ort_birim_maliyet`** (708 ms, `source=cube`, sessiz) | 🗣 sipariş |
| **RF-c** saçma yazım önerisi *(3. kanıt)* | `f3` `kaç farklı müşteri` → *"«kac farkli» yerine «kac yas» mi?"* | 🗣 sipariş |
| **RF-d** iki-dönem kıyası *(§49, 4. kanıt)* | `f2` `ilk çeyrek ile ikinci çeyreği karşılaştır` → **İK/bordro** küpü | 🗣 sipariş |
| **RF-e** kapsam dışı soru Discovery'ye düşüyor | `f17` `sektör ortalamasının üstünde mi` → `adhoc` uydurma ölçü; oysa doğru cevap *"sektör kıyas verim yok"* | 🍳 mutfak sınırı |
| **RF-f** ilişki sorusu ne cevaplanıyor ne reddediliyor *(3. kanıt)* | `f10` `üretim ile fire arasında ters orantı var mı` | 🗣 sipariş |
| **RF-g** *"en iyi ve en kötü"* tekilleştirilmiyor | `f15` → 6 satır (tüm aylar) | 🗣 sipariş |
| **RF-h** zamir tekilleştirmiyor *(2. kanıt)* | `f6`T2 `en yüksek **olanın** aylık trendi` → 42 satır (tüm kumaş cinsleri × ay) | 🗣 sipariş |

⊙ **Eksen dağılımı:** 7 sipariş · 1 mutfak. `§0.0`'ın ayrımı bu turda da temiz çalıştı —
ve dağılım, işin ağırlığının hâlâ **garson tarafında** olduğunu söylüyor.

✅ **Mutfak eksikleri bu turda azaldı:** `ort_siparis_buyuklugu`·`enerji_yogunlugu_kwh_kg`·
`rework_sayisi`·`hafta_gunu` hepsi **vardı** ve doğru bulundu. E turundaki dört `adhoc`
düşüşünün üçü küp eksiğiydi; F turunda yalnız **bir** (`f17`, ve o da gerçek bir kapsam
dışı).

## §60 · ÖLÇÜ İKAMESİ — beş kez ölçüldü, hiç beyan edilmedi

| soru | istenen | **verilen** |
|---|---|---|
| `bakım maliyetleri`ni makine bazında | bakım maliyeti | `ort_birim_maliyet` |
| `fire **maliyetimiz**` | ₺ | **`toplam_fire_kg`** (kg) |
| `**ortalama** parti ağırlığı` | ortalama | `toplam_agirlik_kg` |
| `kalite red oranı` | red oranı | `fire_orani_yuzde` |

⊙ Beşinde de cevap **sessizce** başka bir ölçüyle geldi — `KÖK-3`'ün tanımladığı
**sessiz-yanlış adayının** tam tanımı: sayı doğru hesaplanmıştır ama **başka bir şeyin**
sayısıdır.

`uyum.py`'ye sekizinci ihlal sınıfı kondu (`olcu_ikamesi`): soruda bir birim/toplulaştırma
sözcüğü geçiyor ama seçilen ölçünün **birimi** ya da **toplulaştırması** onunla uyuşmuyorsa
**beyan edilir** — cevap öldürülmez (`KÖK-3`'ün beyan-açık sözleşmesi).

> *Bir sayıyı doğru hesaplayıp yanlış şeyin adıyla sunmak, yanlış hesaplamaktan daha zor
> fark edilir.*

### 60.1 · İki kez yanıldım, kapı ikisini de yakaladı

**(a) Var olmayan bir alanı okudum.** İlk yazımda `cube_meta["measure_meta"][m]["unit"]`
diye bir yol uydurdum; o anahtar **yok** ve kapı sessizce hiç ateşlemedi. Birimin sahibi
`viz._unit_of`'tur (MDL `units`, yoksa regex yedeği) — ikinci bir çözücü `KAT-1` olurdu.
*Var olmayan bir alanı okuyan kod sessizce hiçbir şey yapar — ve testi geçer.*

**(b) Türü eşitlikle sınadım.** Test `_birim != "₺"` idi; `birim maliyet` ölçüsünün birimi
**`₺/kg`** olduğu için **meşru** bir soru *"ikame"* diye damgalandı — kapı **beş korpus
vakasıyla** kırmızı verdi. Doğru test eşitlik değil **tür**: birim bir para işareti
taşıyor mu? *Bir türü eşitlikle sınamak, o türün bütün biçimlerini reddetmektir.*

### 60.2 · Doğrulama

| soru | önce | **sonra** |
|---|---|---|
| `bu yılki fire maliyetimiz ne kadar` | sessizce `toplam_fire_kg` (**kg**) | ✅ *"Birim maliyet / kârlılık, parti ile ilgili görünüyor — hangi ölçüyü istiyorsun?"* |
| `bu yıl birim maliyet ne kadar` *(yanlış-pozitif kontrolü)* | ✅ | ✅ **918 ms** · `ort_birim_maliyet` — beyan **yok**, doğru |

---

# G TURU — 20 yeni özgün senaryo

## §61 · GEÇERLİ BİR TERİMİ *"DÜZELTMEK"* — en kötü öneri

| soru | öneri |
|---|---|
| `bu yıl **vardiyalara** göre fire oranı` | 🔴 *"«vardiyalara gore» yerine «calisanlara gore» mi?"* |
| `bu yıl **kaç farklı** müşteriye satış yaptık` | *"«kac farkli» yerine «kac yas» mi?"* |
| `renk bazında ciro **dağılımı»** *(§43'te ayrı çözüldü)* | *"«dagilimi» yerine «agirlik» mi?"* |

🔴 Birincisi en ağırı: **`vardiya` katalogda var** ve onlarca soruda doğru çalışıyor.
Sistem, **kendi bildiği** bir terimi *"acaba başka bir şey mi demek istedin"* diye
sorguluyordu — yani kullanıcıya **kendi kataloğunu yanlış tanıtıyordu**.

**Kural:** bir sözcük katalogda karşılığı olan bir terimi **kapsıyorsa**, o sözcük bir
yazım hatası **değildir**. Ölçüt `_covers` (çekimi de yakalar); sözlük `cube_router`'ın
kendi `_catalog_vocabulary`'si — ikinci bir eşleştirici yazılmadı (`KAT-1`).

> *Bir sözlüğün kendi kelimesini yanlış sayması, sözlüğe duyulan güveni bitirir.*

**Doğrulama:** ikisinde de saçma öneri **kayboldu**; yerine dürüst beyan
(`eksik_niyet:['kirilim']`) ve doğru küpleri sunan netleştirme geldi.

## §62 · G turunun envanteri

### Çalışan (13)

`g1` parti sayısı · **`g4` `quel est le chiffre d'affaires de cette année` — FRANSIZCA
✅✅ 7.710 ms** · `g5` en çok kâr eden ay (`order:desc`) · `g6` **olumsuzluk sınırı
dürüstçe beyan** (*"«plansız» bir olumsuzluk ifadesi ve bunu henüz sorguya
çeviremiyorum"*) · `g8` makine başına ort. duruş · `g9` `koyu renk` **değer filtresi
uygulandı** · `g11` iki boyut + **`view: heatmap`** 35 satır · `g13` boş-aralık beyanı ·
`g14` kâr marjı × müşteri · `g16` `en az fire` → **`order:asc`** · `g17` vardiya
performansı · **`g19` `müşteri bazında ciro` → `ilk beşini pasta yap` → `order:desc` +
`limit:5` + `view: pie`** ✅✅

⊙ **Dört dil doğrulandı:** Türkçe · İngilizce · Arapça · Almanca · **Fransızca**.
`§48`'in *"dönemi sistemin diline çevir"* talimatı **dilden bağımsız** olduğu için her
yeni dil kendiliğinden çalışıyor — kullanıcının *"ne'ce yazarsa yazsın"* şartı artık
**ölçülmüş** durumda.

### Kalan kökler

| # | kanıt | eksen |
|---|---|---|
| §49 iki-dönem kıyası *(**5. kanıt**)* | `g10` `geçen ay ile bu ayı ciro açısından kıyasla` → yalnız temmuz, `eksik:['kiyas']` | 🗣 sipariş |
| `limit N` sayı boyut adına bitişik değilse düşüyor *(3. kanıt)* | `g12` `en yüksek **3 makinenin** duruş sürelerini de göster` | 🗣 sipariş |
| trend sorusu zaman ekseni kurmuyor | `g18` `geçen 6 ayda üretim arttı mı azaldı mı` → `eksik:['trend']` | 🗣 sipariş |
| gecikme kavramı yanlış küplere gidiyor | `g2` `hangi müşterinin siparişi en çok gecikti` | 🍳 mutfak |
| `vardiyalara göre` kırılımı taşınmıyor *(§61 sonrası)* | `v61a` → `eksik:['kirilim']` | 🗣 sipariş |

⊙ **Eksen dağılımı:** 4 sipariş · 1 mutfak. Mutfak eksikleri turdan tura azalıyor
(E: 4 · F: 1 · G: 1).

---

# H TURU — 20 yeni özgün senaryo

## §63 · *"EN"* ÖNÜNDEYSE O BİR ÜSTÜNLÜK, OLUMSUZLUK DEĞİL

**Ölçüldü (`h12`):** `bu yıl **en verimsiz** hattı bul` → *"«verimsiz (= «verim» olmayan)»
bir **olumsuzluk** ifadesi ve bunu henüz sorguya çeviremiyorum"*.

Oysa kullanıcı *"verimi olmayan"* demedi; **"en düşük verimli"** dedi — ve
`cube_router._AZLIK_KUTBU` `verimsiz`'i **zaten azlık kutbu** olarak tanıyor, yani
`_direction` ondan `ASC` üretiyor. İki okuma da dilbilgisel olarak mümkün; ayıran şey
**yapı**: `en` + sıfat bir **üstünlük derecesidir**, bir yokluk değil.

⚠ Kapsam dar: yalnız token'ın **hemen öncesinde** `en` varsa. `firesiz partiler`
(üstünlüksüz) aynen olumsuzluk sayılır — o soru gerçekten *"firesi olmayan"* der.

> *Bir sıfatı derecelendirmek, onu yok saymaktan başka bir şeydir.*

**Doğrulama:** `en verimsiz hattı bul` → red **kalktı**; `firesiz partiler kaç tane` →
olumsuzluk beyanı **korundu** (1.055 ms).

## §64 · H turunun envanteri

### Çalışan (10)

`h1` ortalama fire oranı · `h4` en çok rework (`order:desc`) · **`h6` `parti başına
ortalama ciro` → `eksik_niyet:['olcu_ikamesi']`** *(🔴 `§60` **sahada** çalıştı:
«ortalama sordun ama `toplam_ciro` bir toplam»)* · **`h7` `¿cuál fue la producción total
este año?` — İSPANYOLCA ✅✅** · **`h8` `aylara göre ciro` → `en yüksek **üç** ayı seç` →
`order:desc` + `limit:3`** *(yazıyla sayı!)* · `h10` **`toplam_enerji_tl` 423 ms** ·
`h11` `su_yogunlugu_lt_kg` + dürüst `kirilim` beyanı · `h14` **530 ms · `view: line`** ·
`h17` geçen yıl üretim · `h19` en fazla parti işlenen ay

⊙ **ALTI DİL doğrulandı:** Türkçe · İngilizce · Arapça · Almanca · Fransızca ·
**İspanyolca**.

### 🔴 Bir sınıflandırma hatamı düzeltiyorum

`§52`'de `enerji maliyeti`'ni **mutfak eksiği** diye kaydetmiştim. `h10` gösterdi ki
**`toplam_enerji_tl` katalogda VAR** ve `bu yıl toplam enerji maliyeti ne kadar tl`
sorusu **423 ms**'de çözülüyor. Yani o vaka bir **sipariş** kusuruydu: aynı kavram
farklı sözcüklerle sorulduğunda garson/route onu bulamıyor.

> *Bir kusuru yanlış eksene yazmak, onu yanlış yerde aramaya mahkûm eder.*

⊙ Ve `§0.0`'ın ayrımı bu düzeltmeyi **mümkün kıldı**: eksen sorusu sorulmasaydı, o vaka
"küpte yok" diye kapanırdı.

### Kalan kökler

| # | kanıt |
|---|---|
| ölçü **cümlede adıyla geçiyor** ama bulunamıyor | `h3` `…enerji tüketimine göre sırala` → *"hangi ölçüyü istiyorsun?"* · `h13` `kaç **kg** kumaş boyadık` · `h16` `**kar marjı** yüzde 20 altındaki` *(oysa `g14`'te `kar_marji_yuzde` çalıştı)* |
| eşikli soru küp seçimini bozuyor | `h16` · `h15` |
| çoklu ölçü + kırılım birlikte istenince ölçü sorusu | `h18` · `h20` |
| iki-dönem/çok-dönem *(6. kanıt)* | `h2` `2025 ve 2026 cirolarını ayrı ayrı ver` → `eksik:['cok_donem']` *(dürüst)* |

---

# I TURU — 20 senaryo · ve baskın kusurun KÖKÜ

## §65 · 🔴🔴 GARSON CEVAP VERDİ, **UYUM EŞİĞİ ONU ATTI**

### 65.1 · Ölçüm — `§47`'nin logu tek satırda gösterdi

I turunun **beş** senaryosu aynı cümleyle bitti: *"«…» ile ilgili görünüyor ama **hangi
ölçüyü** istediğini anlayamadım"* (`i8`·`i9`·`i11`·`i14`, ayrıca `h3`·`h13`·`h18`·`h20`).

Logdan okunan sebep:

```
intent: 3 oy · 2 farklı aday · kazanan 1 oy
intent: 3 oy · 3 farklı aday · kazanan 1 oy
```

⊙ **Garson sustuğu için değil, UYUŞMADIĞI için** cevap yok. Üç oy da bir `cq` üretti;
uyum oranı `1/3` olduğu için eşik (`≥ 2/3`) tutmadı ve `parsed` `None` kaldı. Sistem
kullanıcıya *"anlamadım"* dedi — oysa elinde **üç somut cevap** vardı.

🔴 Bu, `§0.0`'ın *"kullanıcı asla cevapsız kalmaz"* şartının doğrudan ihlali. Ve `§47`
olmasaydı **hiç görünmeyecekti**: dışarıdan bakınca *"LLM anlamadı"* gibi duruyor.

### 65.2 · Kök çözüm yönü *(sıradaki iş)*

Uyuşmazlık **tek eksende** ise chip zaten üretiliyor (`_intent_uyusmazlik_chipi`).
Eksik olan **çok eksenli** uyuşmazlık: bugün **sessiz düşüş**. Doğru davranış:

* ya **çoğunluk adayı** ile cevapla ve belirsizliği **beyan et** (`beyanlı kısmi`),
* ya da **farklı adayları chip olarak sun** — kullanıcı seçsin.

Ama **asla** *"hangi ölçüyü istiyorsun"* deme: garson zaten söyledi, üç kere.

⚠ Ve `2/3` eşiğinin kendisi de sorgulanmalı: `consistency_k=3`'te **iki farklı aday**
%67'lik bir uyum üretemez; eşik pratikte *"üç oyun ikisi birebir aynı"* demektir ve
serbest-metin bir JSON'da bu **nadir**dir.

### 65.3 · Yan bulgu — model soruyu geri yankıladı

```
intent: whitelist REDDİ (sema=kapali) — ham=Bu yıl kalite puanı en yüksek vardiya
```

Bir oy JSON yerine **sorunun kendisini** döndürdü. Beyaz liste onu düşürdü (doğru) ama
bu, `sema` (şema-kısıtlı çıktı) bayrağının **neden açılması gerektiğinin** ölçülmüş
gerekçesidir.

## §66 · I turunun envanteri

### Çalışan (8)

`i1` eşikli soru + dürüst `esik` beyanı · `i2` kar marjı × müşteri · **`i3` `enerji
tüketimi en yüksek 4 makine` → `order:desc` + `limit:4` ✅✅** · `i5` **486 ms** ·
`i6` renk bazında kâr (`order:desc`) · `i10` kalite puanı × vardiya · `i12` **499 ms** ·
`i13` **470 ms**

### 🔴 Sözcük SIRASI kusuru — iki cümle, aynı anlam, farklı sonuç

| cümle | sonuç |
|---|---|
| `enerji tüketimi **en yüksek 4 makine**` | ✅ `order:desc` + `limit:4` · 4 satır |
| `**en yüksek 4 makineyi** enerji tüketimine göre sırala` | 🔴 *"hangi ölçüyü istiyorsun?"* |

Aynı biçimde: `kar marjı yüzde 20 **altında olan**` ✅ · `… **altındaki**` 🔴.

⊙ İkisi de `§65`'in belirtisi: route yetişemiyor, garson uyuşmuyor, sistem susuyor.
**Route'a sözcük sırası öğretmek çözüm değildir** (`§0.0`) — çözüm garsonun cevabını
**atmamaktır**.

### Kalan kökler *(değişmedi, kanıt sayıları arttı)*

`§49` iki-dönem kıyası **7. kanıt** (`i7`'de üstelik **yanlış** beyan: kullanıcı iki
**ölçü** kıyaslamak istedi, sistem *"iki dönem"* dedi) · `kaç kg` ölçüye bağlanmıyor
(`i4`) · çoklu ölçü tek cümlede (`i12` yalnız `toplam_ciro` aldı, `kar` düştü).

### 65.4 · Kök çözüm ve doğrulama

Koşuldan `and eksen` **kaldırıldı**: adaylar varsa, eksen tek olmasa da chip üretilir.
Çok eksenli hâlde etiket **bileşik** kurulur (küp · ölçü · kırılım) ki kullanıcı **neyi**
seçtiğini görsün.

⚠ **Tahmin yok:** adaylar sunulur, seçen kullanıcıdır ve seçim `/cube` ile **LLM'siz**
koşar — ikinci bir LLM turu doğmaz.

| soru | önce | **sonra** |
|---|---|---|
| `bu yıl hangi makine en az duruş yaşadı` | *"…hangi ölçüyü istediğini anlayamadım"* | ✅ **tam cevap**: `makine_duruslari` × `makine` · **`order:asc`** *(doğru kutup)* · 11 satır |
| `bu yıl en uzun süren 5 partiyi göster` | *"…anlayamadım"* | ◐ hâlâ netleştirme — ama **dürüst**: *parti süresi* diye bir ölçü katalogda yok |

⊙ İkinci satır bir **eksen ayrımı** örneği: birincisi sipariş kusuruydu ve kapandı;
ikincisi bir **mutfak** eksiği ve netleştirme orada **doğru** cevaptır.

**Üç yeni kapı:** çok eksenli uyuşmazlık sessizce düşmeyecek · etiket çok eksende bileşik
olacak · **oy dağılımı loglanmaya devam edecek** *(bu kusur tam olarak o satır sayesinde
bulundu — log giderse kusur geri döner ve görünmez olur)*.

> *Üç farklı cevabı olan bir soruya «anlamadım» demek, cevapları saklamaktır.*

---

# J TURU

## §67 · *"KIYASLA"* HER ZAMAN İKİ DÖNEM DEMEK DEĞİL — ve teşhisimin yarısı yanlıştı

**Ölçüldü (8 kanıt):** `ciro ile kar marjını makine bazında **kıyasla**` → *"iki dönemi
kıyaslamanı istedin ama tek bir toplam üretebildim"*. Kullanıcı **iki ölçüyü** kıyaslamak
istedi; ortada dönem yok. `Ö10`'un kuralı: **yanlış bir beyan sessizlikten kötüdür**.

**Yapılan:** `kiyas` ihlali, sorguda **iki ya da daha çok ölçü** varken ve soru birden çok
dönem saymıyorken **susar** — o kıyas ölçüler arasıdır ve sorguda **zaten karşılanmıştır**.

### 67.1 · 🔴 Doğrulama teşhisimi düzeltti

Düzeltmeden sonra aynı soru **hâlâ** `eksik:['kiyas']` beyan etti. Sebep: `cq`'da **tek**
ölçü var — **`ciro` düşmüş**. Yani bu vakada asıl kusur beyan değil, **ölçü kaybı**:
cümlede iki ölçü adı geçiyor, sorguya biri giriyor.

⊙ `§67` yine de doğru bir daraltma (iki ölçü **gerçekten** varken artık susacak), ama bu
vakayı kapatan şey **olmayacak**. *Bir beyanı susturmak, beyanın işaret ettiği eksikliği
kapatmaz — yalnız yanlış adlandırmayı düzeltir.*

**Kayıtlı kök (öncelikli):** *"iki ölçü adı geçen cümlede biri düşüyor"* — `i12` `toplam
ciro ve toplam kar` *(J turunda `j1`'de düzelmiş görünüyor: iki ölçü de geldi)* · `v67`
`ciro ile kar marjı` · `i7` `fire oranı ve oee`.

## §68 · `\b` KUSURU BİR KAT YUKARIDA TEKRARLADI

**Ölçüldü (`j12`):** `aylık fire trendini **alan grafikle** ver` → `view: chart` (genel),
çünkü `\balan grafi\b` deseni `grafi` ile `k` arasında sınır arıyor — orada sınır **yok**.

🔴 Bu `§45`'in **birebir aynı kusuru**, farklı bir sözlükte. Türkçede her ad ek alır; sağ
tarafı `\b` ile kapatmak deseni **yalın hâle hapseder**.

⚠ Sol sınır `\b` **kalır**: `bar`ın `barkod`u tutmaması ona bağlı (`§37`).

**Doğrulama:** `alan grafikle` → ✅ **`view: area`**.

> *Aynı kusur iki farklı sözlükte çıktıysa, üçüncü bir sözlükte de vardır.*

## §69 · J turunun envanteri

**Çalışan (8):** `j1` iki ölçü birlikte · `j2` `kaç kilogram kumaş` → `toplam_agirlik_kg`
**5.400 ms** · **`j8` `quanto abbiamo prodotto quest'anno` — İTALYANCA ✅✅** ·
`j4`T1 **480 ms** · `j6` **524 ms** · `j9` fire oranı × makine · **`j10` iki boyut,
504 ms, 33 satır** · `j12` alan grafik *(§68 sonrası)*

⊙ **YEDİ DİL:** Türkçe · İngilizce · Arapça · Almanca · Fransızca · İspanyolca ·
**İtalyanca**.

**Kalan kökler:** `sadece hafta içi` filtresi **yine** sessizce düştü *(2. kanıt, `j4`T2)*
· zamir/tekilleştirme *(`j7` → 66 satır)* · *"ortalamanın üstünde"* eşiği uygulanmıyor
*(`j9`)* · `Hangisini istiyorsun?` küp beraberliği *(`j5`·`j11`)* · ölçü kaybı *(§67.1)*.

## §70 · *"SADECE …"* DEDİ, HİÇBİR ŞEY KISITLANMADI — iki kez sessizce

**Ölçüldü (`e16`T2 · `j4`T2):** `aylık üretim` → `**sadece** hafta içi günleri al` →
**satırlar aynen** döndü, filtre uygulanmadı, **hiçbir şey beyan edilmedi**.

⊙ Sebebi bir **mutfak** eksiği: `hafta içi` katalogda bir **değer değil** (`hafta_gunu`
boyutunun değerleri tek tek günlerdir), yani **garson da onu ifade edemiyor**. Ama bu,
susmayı haklı çıkarmaz: kullanıcı bir kısıtlama istedi ve **kısıtlanmamış** bir sayı
gördü — sessiz-yanlışın tanımı.

**Dokuzuncu ihlal sınıfı** (`kisitlama`): kısıtlayıcı zarf var (`sadece`·`yalnız`·
`yalnızca`·`only`·`just` — kapalı dilbilgisi sınıfı) ama `cq`'da **tarih dışı** hiçbir
filtre yoksa **beyan edilir**. Yalnız beyan; cevap öldürülmez (`KÖK-3`).

| soru | önce | **sonra** |
|---|---|---|
| `sadece hafta içi günleri al` | 6 satır, **beyan yok** | ✅ *"**sadece …** dedin ama sorguya bir kısıtlama taşıyamadım — sayı **tüm** kayıtları kapsıyor"* · `eksik:['kisitlama']` |
| `bu yıl sadece siyah renkli partilerin cirosu` *(gevşemenin sınırı)* | ✅ | ✅ **511 ms**, 2 filtre, beyan **yok** — doğru |

> *Bir kısıtlamayı uygulayamamak bir sınırdır; uygulamadığını söylememek bir hatadır.*

⊙ Ve bu, `§0.0`'ın eksen ayrımının **üçüncü** biçimi: kusur **mutfakta** (kavram yok) ama
onarım **siparişte** (beyan). *Bir eksikliği kapatamıyorsan, hiç değilse adını koy.*

---

# K TURU

## §71 · ÖLÇÜ KAYBI — kök **izole edildi**, çözüm **geri alındı**

### 71.1 · Kanıt kusursuz: route son ölçüyü tutar, öncekini atar

| soru | yol | sonuç |
|---|---|---|
| `bu yıl **ciro ve fire oranını** makine bazında ver` | `route` **1.134 ms** | yalnız `fire_orani_yuzde` — **`ciro` düştü** |
| `bu yıl **oee ve kullanılabilirliği** vardiya bazında ver` | `route` **718 ms** | yalnız `ort_kullanilabilirlik` — **`oee` düştü** |
| `bu yıl **ciro kar ve fire** birlikte` | **garson** 24.576 ms | ✅ **üç ölçü de var** |

⊙ Üçüncü satır bir **karşı-kanıt** ve tanıyı kesinleştiriyor: garson hepsini taşıyor,
route taşımıyor. Ve kayıp **sessiz** — hiçbir `eksik_niyet` üretilmiyor.

🔴 `§0.0` birebir uygulanır: **route yarım duydu, garson gitmeli.** Ama route "başarılı"
göründüğü (dönem var, ölçü var, boyut var) için `route_supheli` ateşlemiyor.

### 71.2 · 🔴 Denediğim çözüm ve NEDEN GERİ ALINDI

`route_supheli`'ye bir sinyal daha ekledim: *"sorudaki ölçü adı sayısı `cq`'nun
taşıdığından çoksa şüphe vardır"* — ölçü adlarını `measure_synonyms_display`'den sayarak.

**Ölçüm iki yönde de tatmin etmedi:**

| soru | sonuç |
|---|---|
| `ciro ve fire oranını…` | ◐ sessiz kayıp → **netleştirme** (*"Hangisini istiyorsun?"*). Doktrine göre **daha iyi** (sessiz-yanlış → dürüst soru) ama **istenen değil**: iki ölçü de gelmeliydi |
| `oee ve kullanılabilirliği…` | 🔴 **hiç değişmedi** — sinyal ateşlemedi |

Sebep: yüklem **görünen adı** (`ort oee`) soruda alt-dize olarak arıyor; kullanıcı **kısa
adı** (`oee`) yazıyor. Yani sinyalin kendisi eşanlamlı sözlüğünü yanlış uçtan okuyor.

**Geri alındı.** Bu deponun kuralı: yarım çalışan bir düzeltme, ölçülmüş bir kazanç
değildir. *Bir kusuru yarı yarıya kapatan bir yama, kusurun ölçüsünü de yarıya indirir —
ve bir dahaki sefere daha zor bulunur.*

### 71.3 · Sıradaki iş için kayıtlı yön

Sinyal **eşleştiriciden** okunmalı, görünen addan değil: `cube_router`'ın soruda kaç
**ayrı ölçü** eşleştirdiğini söyleyen bir sayaç (`_match_measure` ailesinin kendi
sonucu). O sayaç `cq`'nun ölçü sayısından büyükse şüphe vardır.

⚠ Ve asıl kök hâlâ `route()`'un kendisinde: **son eşleşen ölçü öncekini eziyor.** Ama
`§0.0` gereği orayı düzeltmiyoruz — garsonu çağırmak yeterli olmalı.

### 71.4 · İKİNCİ deneme de ateşlemedi — ve buradan çıkan ders

İlk deneme görünen addan okuyordu (`§71.2`); ikincisinde **eşleştiricinin kendi
sözlüğüne** geçtim (`measure_synonyms` + `_syn_hit` — route neyi görüyorsa onu say).

| soru | sonuç |
|---|---|
| `ciro ve fire oranını makine bazında ver` | ◐ davranış **değişti** (küp beraberliği chip'i) → şüphe **ateşledi** |
| `oee ve kullanılabilirliği vardiya bazında ver` | 🔴 **902 ms, `source=cube`** → garson **hiç çağrılmadı**; şüphe **ateşlemedi** |

⊙ İkisi de aynı yüklemden geçiyor ve biri ateşliyor, öteki ateşlemiyor. Yani yüklem
**çalışıyor ama girdisi eksik** — büyük olasılıkla `_cm` (küp meta) bulunamıyor ya da
`measure_synonyms` beklediğim şekle sahip değil.

🔴 **Geri alındı (ikinci kez).** Ve asıl ders bu:

> *Aynı kökte iki kör deneme, kökün orada olmadığını değil, benim ona bakmadığımı
> gösterir.* Sıradaki adım bir **yama denemesi değil, doğrudan bir sondaj** olmalı:
> `route_supheli`'nin o iki soru için ne gördüğünü (`_cm` var mı, `_gecen` kaç eleman)
> tek atışta yazdırmak.

⚠ Ve bu, `§0.3`'ün ölçüm disiplininin aynısı: *bir düzeltmeyi denemeden önce, düzeltmenin
gireceği yerin ne gördüğünü ölç.* İki demettir bunu atladım.

### 71.5 · Sondaj yapıldı — ve BAYAT ARTEFAKTA düştü *(tuzak ikinci kez ısırdı)*

`§71.4`'ün dediği gibi kör yama bırakılıp sondaj yapıldı. Çıktı:

```
bu yil oee ve kullanilabilirligi …  | cube: oee
   measure_synonyms anahtar sayısı: 0
   _syn_hit ile eşleşen ölçüler: []
   _match_measure (tekil): (None, None)
```

🔴 `_match_measure` **`(None, None)`** dönüyor — oysa **canlı sistem aynı soruda
`ort_kullanilabilirlik`'i buluyor**. Yani sondaj, sistemin gerçekten kullandığı şemayı
okumuyor: kaynak `demo/wren-project`, ve `CLAUDE.md`'nin açıkça uyardığı **gitignore'lu
derleme artefaktı**.

⊙ Bu, `project_olcum_araci_bayat_sema` hafızasının **birebir** tekrarı — ve bu oturumda
**ikinci** kez oldu (`§31` sondajında da olmuştu).

> *Bir ölçüm aracının yanlış kaynaktan okuması, yanlış bir cevaptan sinsidir: yanlış cevap
> sorgulanır, yanlış kaynak güvenilir görünür.*

**Sıradaki adım (kayıtlı):** sondaj **canlı konteynerin** şemasıyla yapılmalı — `/ask`
akışının kullandığı derlenmiş şirket şeması. Doğru yol: konteyner içinde
`app.state`/`WrenService`'ten şemayı almak ya da `/ask`'in kendi loguna `_gecen` sayısını
geçici olarak yazdırmak.

⚠ **Ve `§71` üçüncü kez körlemesine denenmeyecek:** önce bu sondaj doğru kaynaktan
koşacak, ne gördüğü **yazılacak**, ancak ondan sonra kod değişecek.

### 71.6 · CANLI SONDAJ — ve iki başarısızlığın tek açıklaması

Geçici bir log satırı `/ask`'in **kendi akışına** kondu (`route()`'un ilk çağrısının hemen
ardına) ve tek turda cevabı verdi:

```
SONDAJ71: cube=None  syn=0  eslesen=[]  cq_olcu=None
```

**İki gerçek çıktı:**

1. 🔴 **`route()`'un ilk geçişi HİÇBİR ŞEY bulmuyor** (`cube=None`) — oysa aynı soru
   canlıda **902 ms**'de `source=cube` ile cevaplanıyor. Yani ölçüyü çözen şey ilk
   `route()` değil, **sonraki bir geçiş** (yazım düzeltmeli tekrar ya da
   `prompt_enhancer`).
2. 🔴 **`measure_synonyms` bu kurulumda BOŞ** (`syn=0`). Eşleştirme bu sözlükten
   yapılmıyor; başka bir katmandan geliyor.

⊙ **Ve bu, `§71.2` ile `§71.4`'ün ikisini birden açıklıyor:** her iki denemem de
`measure_synonyms`/`measure_synonyms_display` üzerine kuruluydu — yani **hiç dolu olmayan
bir sözlüğü** sayıyordum. Sinyal yanlış değildi; **kaynağı yoktu**.

> *İki kez aynı yerde yanılmak bir tesadüf değildir; ikisinin de aynı boş kovadan su
> çekmesidir.*

**Sıradaki adım (kesin):** ölçüyü gerçekten kimin eşleştirdiğini bul — `route()`'un ikinci
geçişi mi (`typo_correct` sonrası), `prompt_enhancer` mı, yoksa sinonim katmanı mı
(`app/synonyms`·`value_index`·`archetypes`). Sayaç **oradan** okunacak.
⚠ Sondaj satırı **kaldırıldı** (geçiciydi); tekrar gerekirse aynı yere konur.

## §72 · YABANCI DİL BİR HEDEF DEĞİL, BİR **ÖLÇÜM ALETİ** *(kullanıcı düzeltmesi)*

> *"Meselemiz dil sayısını artırmak değil. Farklı diller **route'tan bağımsız** olduğu
> için, LLM'in işini mükemmelce yapıp yapmadığını daha rahat anlamamızı sağlıyor."*

⊙ Bu, önceki turların **okunuşunu** düzeltiyor: *"yedi dil çalışıyor"* bir ürün kazancı
değil, **garsonun sağlam olduğunun kanıtıdır**. Türkçe bir soru çalıştığında bunu route
mu garson mu yaptı belirsizdir; **Arapça bir soru çalıştığında yapan kesinlikle
garsondur.**

**Sonuç — okuma kuralı:**

| gözlem | doğru okuma |
|---|---|
| yabancı dilde soru **çalışıyor** | ✅ garson yolu sağlam |
| yabancı dilde soru **çalışmıyor** | 🔴 **garson yolu o soruda kırık** — bir *"dil eksiği"* değil |

Dolayısıyla `k5` (`hoeveel omzet hebben we dit jaar` → *"Hangisini istiyorsun?"*) bir
Hollandaca eksiği **değil**: garson devreye girmedi ya da cevabı atıldı. Aynı sınıf
`§65`'in ölçtüğü şey.

> *Bir aleti ürün sanmak, ölçtüğü şeyi kaybetmektir.*

## §73 · `kar ⊂ karşılaştır` — YAPIM EKİ, ÇEKİM EKİ SANILDI

**Ölçüm (`k12`):** `bu yıl en verimli 2 makineyi seç ve **karşılaştır**` → *"Bu soru
**iki ayrı konunun** ölçüsünü birlikte istiyor («**kar**» (parti) + «verim» (oee))"*.
Kullanıcı kârdan hiç söz etmedi; `kar` ölçüsü **`karşılaştır`** sözcüğünün içinde eşleşti.

**Sondaj** (canlı konteyner — kör yama yapılmadan, `§71.4`'ün kuralı gereği):

```
_syn_hit(kar)                  → True
_covers("kar", "karsilastir")  → True
_ek_gecerli("silastir")        → True      ← kökün ta kendisi
```

### 73.1 · Kök — dilbilgisel ve keskin

`_SUFFIX_ATOMS` envanteri **çekim** ile **yapım** ekini ayırmıyor:

| ek türü | örnek | kimliği korur mu? |
|---|---|---|
| **çekim** (hâl · çoğul · iyelik) | `kar` → `kar**ın**`, `kar**lar**` | ✅ hâlâ *kâr* |
| **yapım** (isimden fiil/isim) | `kar` → `kar**şılaştır**`, `kar**lı**`, `kar**sal**` | 🔴 **başka bir sözcük** |

> *Bir sözcüğü çekmek onu kendisi olarak bırakır; ondan yeni bir sözcük türetmek başka bir
> şeye çevirir. Bir eşleştirici bu ikisini ayırmıyorsa, kelimeleri değil harfleri eşler.*

⊙ Ve bu, `§32`'nin **ters yönü**: orada katalog teriminden yapım eki **soymuştum**
(`uretim → uret`); burada yapım eki **eklenmiş** bir sözcük kökün çekimi sanılıyor.

### 73.2 · Çözüm yönü — **kod DEĞİŞMEDİ**, korpus hakemliği şart

`_SUFFIX_ATOMS` ikiye ayrılmalı: kimliği koruyan **çekim** atomları (eşleşmeye izin) ve
kimliği değiştiren **yapım** atomları (`-laş`·`-lan`·`-lı`·`-sal`·`-cı`·`-lık` — eşleşmeyi
**keser**).

⚠ Bu deponun **en merkezî** eşleştiricisi. `§26.1` bağlayıcı: korpus `sessiz_yanlis`'i
artırırsa geri alınır. Ve `§32`'nin `_kok()` yolu bundan **etkilenir** — ikisi **birlikte**
ölçülmeli. Bu yüzden bu turda **yazılmadı**: tek başına bir demete sığmaz.

## §74 · K turunun envanteri (20 senaryo)

**Çalışan (9):** `k3` üç ölçü birlikte · `k4` müşteri başına parti (`order:desc`) ·
`k6` **517 ms** · `k10` **dürüst olumsuzluk sınırı** · `k11` **dürüst çapraz-küp sınırı**
(862 ms) · `k15`T1 **495 ms** · `k16` **764 ms** · **`k18` `ciro dağılımını pasta yap` →
`view: pie` + müşteri kırılımı ✅✅** · `k9` doğru şekil + dürüst boş-aralık

**Kökler:**

| # | kanıt |
|---|---|
| **§73** `kar ⊂ karşılaştır` | `k12` |
| **ters cevap** — `en yükseğini **çıkar** kalanları göster` → tam tersi (`limit:1`) | `k15`T2 · `çıkar` *dışla* değil *üret* okundu |
| `limit N` kaybı *(4. kanıt)* | `k8` `en yüksek **3** hattın aylık trendi` → 48 satır |
| **ölçü netleştirmesi baskın sınıf** *(6 kanıt)* | `k5`(NL) · `k7` · `k14` · `k17` · `k19` · `k20` |
| `§49` iki-dönem/YoY *(8. kanıt)* | `k13` `geçen yılın aynı ayıyla yan yana` |

⊙ `§72` gereği `k5` bir **Hollandaca eksiği değil**: garson yolunun o soruda kırık
olduğunun kanıtı — ve `§65`'in sınıfına ait.

### 73.3 · 🔴 SONDAJ HİPOTEZİMİ ÇÜRÜTTÜ — kök çekim/yapım değil, **TEK HARFLİK ATOM**

`§73.2`'de çözüm yönünü *"envanteri çekim/yapım diye ikiye ayır"* diye yazmıştım. Bir
sonraki adım olarak — kendi kuralıma uyup kod yazmadan — ayrışmayı **ölçtüm**:

```
silastir → ('si', 'la', 's', 'tir')      ← suçlu: TEK HARFLİK 's'
lasma    → ('la', 's', 'm', 'a')
lanma    → ('la', 'n', 'm', 'a')
atom sayısı: 85
```

🔴 **Envanterde tek harflik atomlar var** (`s`·`m`·`a`·`n`) ve bunlar neredeyse **her**
harf dizisini geçerli bir ek zinciri yapıyor. `kar ⊂ karşılaştır` bir yapım eki sorunu
**değil**; `s` tek harfli olduğu için zincir kapanıyor.

⊙ Bu, `§32`'nin dersinin **uç noktası**: orada *"iki harflik bir ek zincirde her yere
sığar"* demiştim ve kısa ekleri düşürmüştüm. **Tek harflik bir atom ise her yerdedir.**

> *Bir ek envanterinde tek harflik bir üye, envanteri bir doğrulayıcı olmaktan çıkarıp
> bir onaylayıcıya çevirir.*

⚠ **Ve bu, iki demettir tekrarlanan hatamın üçüncü örneği:** çözüm yönünü **ölçmeden**
yazdım (`§71.2` görünen ad · `§71.4` boş sözlük · şimdi bu). Üçünde de sondaj tek turda
doğruyu verdi. *Bir çözüm yönü, ölçülmeden yazıldığında bir tahmindir — ve tahminler
belgeye yazılınca gerçek görünür.*

### 73.4 · Düzeltilmiş çözüm yönü *(kod hâlâ DEĞİŞMEDİ)*

Tek harflik atomlar **kaynaştırma harfleridir** (`y`·`n`·`s`·`ş`) ve Türkçede yalnız **iki
ünlü arasında** görünürler. Kural: bir zincirde tek harflik atom **tek başına bir adım
olamaz** — ancak komşu atomların arasında bir tampon olarak geçerlidir.

⚠ Uygulama hâlâ **korpus hakemliği** ister (`§26.1`) ve `§32`'nin `_kok()` yolunu etkiler;
ikisi birlikte ölçülmeli. Ama artık **doğru şeyi** ölçeceğiz.

### 73.5 · YAZILDI — kaynaştırma ünsüzleri envanterden çıkarıldı

Sondaj (kod yazılmadan **önce**, `§71`'in üç kez ısırdığı dersin gereği) iki yönlü ölçüm
verdi ve ancak ondan sonra yazıldı:

| | ölçüm |
|---|---|
| **sahte zincirler** | `silastir`·`go`·`iyeti`·`sal`·`lasma` → **beşi de reddedildi** ✅ |
| **meşru çekimler** | 30 biçim (`lar`·`leri`·`ndan`·`sini`·`imiz`·`deki`…) → **hepsi geçti** ✅ |

⚠ İlk denemede `ndan`·`nda` kırılıyordu; sondaj bunu **önceden** gösterdi ve kaynaştırma
bileşikleri (`ndan`·`nden`·`nda`·`nde`·`sini`·`sindan`…) envantere eklendi. Ünlüler
(`i`·`u`·`e`·`a`) gerçek tek harflik eklerdir ve **kaldı**.

**Doğrulama (canlı):**
```
_covers("kar", "karsilastir")  → False ✅   (önce True)
_syn_hit(q, "kar")             → False ✅
_ek_gecerli("silastir")        → False ✅
```
Ve gerileme kontrolü: `bu yıl makinelerin fire oranlarını göster` → **946 ms**, 11 satır,
doğru `cq` — meşru çekim (`oranlarını`) bozulmadı.

### 73.6 · 🔴 AMA BİR TÜKETİCİ HÂLÂ SAHTE EŞLEŞME ÜRETİYOR

`bu yıl en verimli 2 makineyi seç ve karşılaştır` **hâlâ** *"iki ayrı konu: «kar» +
«verim»"* diyor — oysa çekirdek eşleştirici artık reddediyor.

Sahibi `yetenek._iki_cube_olcusu` ve o, `_match_measure(q, c)` çağırıyor — **ham `q` ile**,
normalize edilmiş `qn` ile değil. Yani aynı sorunun iki farklı girdiyle iki farklı cevabı
var.

⊙ Bu, deponun `KAT-1` sınıfının bir alt biçimi: **aynı eşleştirici, farklı ön işlemle**.

> *Bir eşleştiriciyi düzeltmek yetmez; onu kimin nasıl çağırdığını da bilmek gerekir.*

⚠ Sıradaki adım yine **sondaj**: `_match_measure`'ın ham ve normalize girdiyle ne
döndürdüğünü ölç, sonra düzelt. Kör yama yok.

### 73.7 · 🔴 KORPUS HAKEMLİK ETTİ — **GERİ ALINDI**

| ölçüt | önce | **§73 ile** | okuma |
|---|---|---|---|
| `sessiz_yanlis` | 12 | **12** | ✅ doğruluk vetosu geçildi |
| `kabul` | 1153 | **1157** (+4) | daha çok soru cevaplandı |
| `dogru` | 93 | **91** (−2) | 🔴 **en katı ölçüt DÜŞTÜ** |
| `beyanli_kismi` | 51 | 49 (−2) | |
| tam süit | yeşil | 🔴 **4 kırmızı** | |

⊙ `§46.5`'te *"kabul düşerken `dogru` yükselmesi bir **keskinleşme**"* diye yazmıştım.
Burada tam **tersi** oldu: `kabul` yükseldi, `dogru` düştü — yani **körelme**. Dört
kırmızı testle birlikte karar tartışmasız.

**Geri alındı.** Ve gerekçe yalnız sayı değil, **doktrin**:

> `§73` bir **route'a Türkçe öğretme** işidir — `§0.0`'ın önceliksizleştirdiği eksen.
> `kar ⊂ karşılaştır` gerçek bir kusurdur ama doğru onarımı morfolojiyi sıkmak değil,
> **garsona sormaktır**: bir dil modeli `karşılaştır`ı asla *"kâr"* diye okumaz.

⚠ **Kusur AÇIK kalıyor ve bu bilinçli:** kapatmak için doğru yer sipariş ekseni.

### 73.8 · Bu üç turun asıl kazancı — üç ölçülmüş ders

`§71`·`§73` boyunca **üç düzeltme yazıldı ve üçü de geri alındı**. Kod net sıfır; ama
üç ders **ölçülerek** kazanıldı:

1. **Çözüm yönünü ölçmeden yazma** (`§71.2` görünen ad · `§71.4` boş sözlük · `§73.2`
   yanlış hipotez). Üçünde de tek bir sondaj doğruyu verdi.
2. **Sondajın kaynağı da ölçülür** (`§71.5`): `demo/wren-project` bayat artefakt;
   canlı akışa konan **tek log satırı** cevabı tek turda verdi.
3. **Yeşil bir veto, yeşil bir karar değildir** (`§73.7`): `sessiz_yanlis` sabit kaldı
   ama `dogru` düştü. Veto bir **alt sınır**dır, bir onay değil.

> *Geri alınan bir düzeltme bir başarısızlık değildir; ölçülmemiş bir düzeltmeyi
> bırakmak başarısızlıktır.*

---

# L TURU — ve baskın kusurun ASIL kökü

## §75 · AYNI SORU, ARKA ARKAYA İKİ KOŞUM, İKİ BAMBAŞKA CEVAP

L turunun 20 senaryosunun **11'i** *"hangi ölçüyü / hangisini istiyorsun?"* ile bitti.
Sınıfı ölçmek için aynı soruyu iki kez koştum:

```
09:08:18  intent: 3 oy · 2 farklı aday · kazanan 1 oy  → "Hangi ölçüyü istiyorsun?"  17.165 ms
09:08:56  intent: 3 oy · 1 farklı aday · kazanan 3 oy  → source=cube+llm · 11 satır  15.337 ms
```

🔴 **Aynı soru. Aynı sistem. Aynı dakika. Biri netleştirme, öteki tam ve doğru cevap.**
Tek fark: **oyların rastgele uyuşup uyuşmaması.**

### 75.1 · Kök — anlama değil, EŞİK

Baskın kusur sınıfı *"garson anlamıyor"* **değil**:

> **`2/3` uyum eşiği, anlamayı bir yazı-turaya çeviriyor.** Üç oy üç **geçerli** `cq`
> ürettiğinde cevap **atılıyor**; tesadüfen aynı JSON'u ürettiklerinde cevap kusursuz.

⊙ Ve `k=3`'te matematik acımasız: **iki farklı aday %67 uyum üretemez** (en iyi hâl 2/3 =
tam eşik). Yani eşik pratikte *"üç örneklemin ikisi **birebir aynı JSON**"* demektir —
serbest metin üreten bir modelde bu **nadir**dir.

🔴 `§0.0`'a göre garson **asıl güvendiğimiz hakemdir**. Cevabını üç örneklem uyuşmadı diye
atmak, tam olarak ona **güvenmemektir**.

> *Bir hakemin kararını üç kez sorup ikisi aynı çıkmadı diye atmak, hakemi hiç
> çağırmamaktan farksızdır — yalnız üç kat pahalıdır.*

### 75.2 · Çözüm yönü *(ölçülecek, yazılmadı)*

* Uyuşmazlıkta **çoğunluk adayıyla cevapla + belirsizliği beyan et** (`beyanlı kısmi`) —
  ya da adayları chip yap; **asla** *"hangi ölçüyü istiyorsun"* deme.
* Eşiğin kendisi yeniden değerlendirilmeli: `k=3` + `2/3` bir **oy birliği** şartıdır.
* ⚠ `KURAL B` + korpus hakem (`§73.7`'nin dersi: **yeşil bir veto, yeşil bir karar
  değildir** — `dogru` düşerse geri alınır).

## §76 · L turunun envanteri (20 senaryo)

**Çalışan (9):** **`l1` §60 sahada** (*"ortalama sordun ama `toplam_fire_kg` bir toplam"*) ·
**`l3` §60'ın BİRİM dalı sahada** (*"₺ tutarı sordun ama ölçü **dk** cinsinden"*) ·
`l4` rework × kumaş (`order:desc`) · `l6` vardiya payları · `l9` `ilk çeyrekte` çözüldü ·
**`l12` `en yüksek fireli 3 partinin müşterisi` → `order:desc` + `limit:3`** ✅✅ ·
`l13` 6.343 ms · **`l18` `kaç adet parti ve toplam kaç kg` → İKİ ÖLÇÜ birden** ✅✅ ·
**`l20` 501 ms · `view: line`** ✅✅

⊙ **Karşıtlık kanıt niteliğinde:** garson cevabı **kullanıldığında** sonuçlar kusursuz
(`limit:3` · iki ölçü · doğru grafik); **atıldığında** kullanıcı soru alıyor. Aradaki fark
kabiliyet değil, **eşik**.

**Kırık (11):** `l2`·`l5`·`l7`·`l8`·`l10`·`l11`·`l14`·`l15`·`l16`·`l17`·`l19` — hepsi
netleştirme, hepsi `§75` sınıfı.

### 75.3 · 🔴 SONDAJ KENDİ SINIFLANDIRMAMI DÜZELTTİ — *"11 kırık"* ŞİŞİRİLMİŞTİ

`§76`'da L turunun 11 senaryosunu *"netleştirmeyle bitti, hepsi `§75` sınıfı"* diye
yazdım. Sonra aynı soruları tek tek yeniden koşup **izlerini** okudum:

| soru | iz | gerçek okuma |
|---|---|---|
| `toplam üretimin yüzde kaçı fire` | `self-consistency **%67** (3 örnek)` + 6 chip | ✅ **bu koşumda GEÇTİ** — L turundaki başarısızlık **oy salınımıydı** |
| `en çok hangi makinede rework oldu` | `self-consistency %67` · 11 satır | ✅ aynı — **iki koşum, iki sonuç** |
| `renk ve makine kırılımını ısı haritasıyla ver` | `cube belirlendi, ölçü belirsiz → netleştirme **(LLM'siz)**` | ⊘ farklı sınıf: garson **iz bırakmadı** |

⊙ **İki ders:**

1. **`§75`'in tezi güçlendi:** aynı soru koşumdan koşuma geçiyor/kalıyor — kusur
   kabiliyet değil **salınım**. Eşik tartışması yerinde.
2. 🔴 **Ama sayım şişikti:** *"11 kırık"* dediğim kümenin bir kısmı **o koşumda** kırıktı,
   sistemik olarak değil. Bir turu bir kez koşup *"şu kadar kırık"* demek, salınımlı bir
   sistemde **bir ölçüm değil bir fotoğraftır**.

> *Belirlenimsiz bir sistemi tek koşumla saymak, zarı bir kez atıp «bu zar hep üç gelir»
> demektir.*

⚠ **Usul düzeltmesi (bundan sonra):** LLM yolundan geçen bir senaryo **kırık** diye
kaydedilmeden önce **en az iki kez** koşulmalı. Tek koşumluk kırmızı, bir **aday**dır —
bir bulgu değil.

### 75.4 · Ayrı ve gerçek bir kusur: `netleştirme (LLM'siz)`

`renk ve makine kırılımını ısı haritasıyla ver` izinde **hiç** `self-consistency` satırı
yok — yani garson o turda ya hiç konuşmadı ya da tüm oyları düştü, ve dal *"(LLM'siz)"*
diye kendini işaretleyerek kullanıcıya soru sordu.

⊙ Bu, `§0.0`'ın ihlali: soruda **iki kırılım adı** (`renk`, `makine`) ve bir **görselleştirme**
isteği var; eksik olan yalnız ölçü. Garsona sorulmadan kullanıcıya sorulmuş.

### 75.5 · 🔴 VE `§75.4`'Ü DE SONDAJ ÇÜRÜTTÜ — iki turda ikinci kez

`§75.4`'te `renk ve makine kırılımını ısı haritasıyla ver` için şunu yazmıştım:

> *"Tek koşumluk salınım **değil**, dalın kendi imzası — garsona sorulmadan kullanıcıya
> soruluyor."*

Aynı soruyu bir kez daha koşup logu okudum:

```
intent: 3 oy · 1 farklı aday · kazanan 1 oy
CEVAP: source=cube+llm · satır=55 · 20.750 ms          ✅ TAM CEVAP
```

⊙ **Garson çalıştı ve bu koşum başarılı oldu.** *"Dalın imzası"* dediğim şey de
**salınımdı** — ve bunu, bir turda önce kendi koyduğum kuralı (`§75.3`: *"iki kez koş"*)
uygulamadan yazmıştım.

> *Bir kuralı koymak onu uygulamak değildir; ve en zor uygulandığı yer, kuralı koyan
> kişinin kendi bulgusudur.*

### 75.6 · İki turun BİLEŞİK sonucu — asıl kusur SALINIMIN KENDİSİ

Üç ayrı sondaj (`§75.3` iki soru · `§75.5` bir soru) aynı şeyi söyledi: **L turunda
"kırık" diye kaydettiğim vakaların büyük kısmı yeniden koşulunca geçiyor.**

Yani sistemin baskın sorunu belirli bir dal, belirli bir sözcük ya da belirli bir küp
**değil**:

> 🔴 **Aynı soru, aynı sistem, aynı dakika — bazen tam cevap, bazen netleştirme.**
> Kullanıcının gördüğü kalite bir **yazı-tura**.

Ve bu, `§0.0`'ın en üst kuralıyla doğrudan çelişir: garson **hakemdir**, ama hakemin
kararı üç örneklemin rastgele uyuşmasına bağlanmıştır.

**Sonuç — sıradaki işin tanımı netleşti:** dal yamamak değil, **salınımı yönetmek**:
1. uyuşmazlıkta **çoğunluk adayıyla cevapla + belirsizliği beyan et** (`beyanlı kısmi`),
2. `k` ve eşiği yeniden değerlendir (`k=3` + `2/3` bir **oy birliği** şartıdır),
3. ⚠ `KURAL B` + korpus hakem — ve `§73.7`: **yeşil bir veto, yeşil bir karar değildir.**

*Belirlenimsiz bir sistemde tek tek dalları yamamak, dalgalı bir denizde tek tek dalgaları
düzeltmeye benzer.*

## §77 · SALINIM YÖNETİMİ YAZILDI — ve **ölçülemediği** için KAPALI doğdu

`§75.6`'nın tanımladığı iş yazıldı: uyuşmazlıkta **çoğunluk adayıyla** cevapla, uyum
oranını ize yaz, eksikleri `uyum.py` beyan etsin.

* `_select_consistent` artık eşiğin altında **çoğunluk adayını** dönebiliyor
* Bayrak `oylama_cogunluk`, `features.yml`'de **`off`**, kayıt `FLAGS`'te gerekçesiyle
* `KURAL B`: kapalıyken davranış **bayt bayt bugünkü**

### 77.1 · 🔴 AMA TAKAS ÖLÇÜLEMİYOR — ve bu, bayrağı kapalı tutmanın SEBEBİ

Doğrulamak için aynı soruyu bayrak kapalıyken iki kez koştum:

```
q1  «toplam üretimin yüzde kaçı fire»  8.604 ms  ✅
q2  «toplam üretimin yüzde kaçı fire»  8.052 ms  ✅
```

İkisi de geçti — yani o soru **o an salınmıyordu**. Salınımı **isteğe bağlı** üretecek bir
soru yok; salınım tanımı gereği **rastlantısaldır**.

⊙ Ve asıl sınır daha derin: **korpus bu bayrağı ölçemez.** `nl_corpus` tanımı gereği
`rule` sağlayıcıyla koşar (LLM'siz) ve `eval --slice llm` **4 vaka**dır. Yani bu bayrağın
kazancı da kaybı da bugünkü aletlerle **görünmez**.

🔴 Bu, `oylama_paydasi`'nın **aynı** sebeple kapalı durmasının tekrarı — ve deponun kendi
kuralı bağlayıcı:

> *"Ölçülemeyen bir takası varsayılan yapmak, kullanıcı adına karar vermektir."*

**Kapalı kalıyor.** Açılması için önce **ölçüm aleti** gerekir: LLM yolunu tekrar tekrar
koşan, aynı soruyu N kez sorup **kararlılık oranı** üreten bir koşucu (`§AJ3.4`'ün kayıtlı
borcu: *"`eval --slice llm` 4 vaka; LLM yolunda hiçbir şey ölçülemez"*).

### 77.2 · Bu üç turun dürüst bilançosu

| tur | yazılan | akıbet |
|---|---|---|
| `§71` | ölçü kaybı sinyali (iki deneme) | **geri alındı** — sinyal boş sözlükten okuyordu |
| `§73` | kaynaştırma ünsüzleri | **geri alındı** — korpus `dogru` 93→91, süit 4 kırmızı |
| `§75/§77` | salınım yönetimi | **yazıldı, KAPALI** — takas ölçülemiyor |

⊙ Üç turda **kalıcı davranış değişikliği sıfır**. Ama kazanç sıfır değil: dört yeni kural
(`§73.8` üç ders + `§75.3` iki-kez-koş), üç çürütülmüş hipotez ve **asıl kusurun adı**
(`salınım`) elde edildi.

> *Bir turun ürünü her zaman kod değildir; bazen bir sonraki turun neyi yapmaması
> gerektiğidir.*

## §78 · KURALI DEPO ÇOKTAN YAZMIŞ — `§75.3` bir KEŞİF DEĞİL, bir YENİDEN KEŞİF

`§77.1`'de *"LLM yolunun kararlılığını ölçen alet yok"* diye borç yazdım ve yeni bir
koşucu yazmaya hazırlandım. Önce `lab/`'a baktım — ve **zaten vardı**:

`lab/garson.py`, açılış notunda:

> ## 🔴 KURAL G-1 — tek koşumla karar YOK
> Bu kapı **belirlenimsizdir** (LLM'e bağlı). Ölçüldü: Power BI'da 1000 aynı sorgunun en
> sık cevabı yalnız **78 kez** çıkmış; bu deponun kendi tarihinde `prompt_enhancer`
> kararı tek koşumla verilip **ikinci sağlayıcıda tersine dönmüştü** (14/15 → 15/15).
> → **En az iki koşum.** İkisi ayrışırsa karar **verilmez**: `⊘` yazılır.

⊙ Yani `§75.3`'te *"yeni usul"* diye yazdığım kural **aynen buradaydı** — hem gerekçesi
hem sayısal kanıtıyla. Ve ben onu iki demet boyunca **iki kez ihlal ettim** (`§75.3`
şişik sayım · `§75.4` yanlış imza teşhisi).

> *Bir depoda yazılı olan bir kural, okunmadığı sürece yazılı değildir — ve onu yeniden
> keşfetmenin bedeli, öğrenmenin bedelinden yüksektir.*

### 78.1 · Gerçek boşluk daha dar — ve yeri belli

`garson.py` **iki koşumu karşılaştırır** (`--muhur` damgası + `_tabani_dondur`). Eksik
olan, `§77`'nin ihtiyacı: **soru başına N koşumluk kararlılık oranı** (aynı `cq` / farklı
`cq`).

⚠ Ve bu, **yeni bir dosya değil** `garson.py`'nin bir kipi olmalı (`KAT-1`): canlı ortam
kurulumu, tur koşucusu ve üçüncü-durum sabitleri orada; ikinci bir kopya `--live`'ın
sessizce `rule`'a düşmesi kusurunu geri getirir (dosyanın kendi notu bunu yazıyor).

**Kayıtlı iş:** `lab/garson.py --kararlilik N` — sabit soru kümesini N kez koşar, soru
başına *"kaç farklı `cq`"* ve toplam **kararlılık oranı** üretir; `oylama_cogunluk` ve
`oylama_paydasi` bayrakları ancak bu sayı varken açılıp kapanabilir.

### 78.2 · Bu turun kazancı

Kod yazılmadı — ve **doğrusu buydu**: yazsaydım `garson.py`'nin ikizi doğacaktı. Yerine
üç şey oldu:

1. `§75.3`'ün *"yeni kural"* sanılan maddesi **`KURAL G-1`'in kopyası** olarak işaretlendi
2. `§77.1`'in *"alet yok"* borcu **daraltıldı**: alet var, **kipi** yok
3. `KAT-1` bir kez daha **önlendi** — yazmadan önce arayarak

> *Bir aletin eksik olduğunu söylemeden önce, laboratuvara bakmak gerekir.*

## §79 · KARARLILIK KİPİ ÇALIŞIYOR — ve ilk ölçüm `§75.6`'yı DARALTIYOR

`§78.1`'in tanımladığı kip `lab/garson.py`'ye eklendi (**yeni dosya değil**, `KAT-1`:
canlı ortam kurulumu ve tur koşucusu zaten orada).

### 79.1 · Alet önce kendi doğruluğuyla sınandı

| koşum | beklenen | ölçülen |
|---|---|---|
| belirlenimli duman (LLM yok) | tam kararlı | ✅ **%100 · 25/25 senaryo** |

⊙ Bilinen bir gerçeği yeniden üretti — `§A3`'ün kuralı (*"alet bilinen bir farkı yeniden
üretebilmeli"*) sağlandı.

### 79.2 · İlk CANLI ölçüm — ve tezimin daralması

Gerçek sağlayıcıyla (`openrouter`), 3 koşum:

```
konu_degisimi    farklı=1   hâkim=3/3     → kararlılık %100
```

🔴 **Bu senaryo TAM KARARLI.** Yani `§75.6`'da yazdığım *"asıl kusur salınımın kendisi"*
tezi **fazla geniş**ti: salınım **her yerde değil**, belirli soru sınıflarında.

> *Bir kusuru «sistemik» ilan etmek, onu ölçmekten kolaydır — ve ölçüm çoğu zaman sınırını
> daraltır.*

### 79.3 · Artık cevaplanabilir olan soru

Kip elde olduğu için `§77`'nin kapalı bayrağı (`oylama_cogunluk`) ve `oylama_paydasi`
**ölçülebilir** hâle geldi. Sıradaki iş, tanımı net:

1. `--live --kararlilik 3` **tüm** senaryo kümesinde koş → **taban** kararlılık oranı
2. `oylama_cogunluk` **açık** aynı koşum → fark
3. Karar: kararlılık yükseliyorsa **ve** korpus `dogru`'yu düşürmüyorsa aç
   *(`§73.7`: yeşil bir veto, yeşil bir karar değildir)*

⚠ Maliyet dürüstçe: 25 senaryo × 3 koşum × tur arası 5 sn — **uzun**. Ama `§77`'nin bayrağı
o sayı olmadan **hiç** açılamaz; ölçmeden açmak, deponun kendi kuralını çiğnemektir
(*"ölçülemeyen bir takası varsayılan yapmak, kullanıcı adına karar vermektir"*).

---

# M TURU — `KURAL G-1` ilk kez ayrımı YAPTI

## §80 · İki koşum, dört doğrulanmış bulgu

20 senaryo koşuldu; netleştirmeyle biten dördü `KURAL G-1` gereği **ikinci kez** koşuldu:

| soru | 1. koşum | 2. koşum | karar |
|---|---|---|---|
| `toplam duruş dakikasını hat bazında sırala` | *"Hangisini istiyorsun?"* | **aynı** | 🔴 **bulgu** |
| `en çok enerji harcayan 3 makineyi bul` | *"Hangi ölçüyü…"* | **aynı** | 🔴 **bulgu** |
| `fire oranı en düşük vardiya hangisi` | İK/İSG/kalite küpleri | **aynı** | 🔴 **bulgu** |
| `bakım süresi en uzun makine` | *"Hangisini istiyorsun?"* | **aynı** | 🔴 **bulgu** |

⊙ **İlk kez** bir turda *"kırık"* ile *"o an kırık"* ayrıldı. `§75.3`'ün şişik sayımı
(`11 kırık`) bu usulle olsaydı hiç yazılmazdı.

🔴 **En ağırı üçüncüsü:** `fire oranı en düşük vardiya` → **İK / İSG / kalite** küpleri
öneriliyor. Oysa aynı turda `kumaş cinsine göre ortalama fire oranı` (`m17`)
`fire_orani_yuzde` × `kumas_cinsi` ile **10.829 ms**'de çözüldü. Aynı ölçü, farklı kırılım
— biri çalışıyor, öteki bambaşka küplere gidiyor. **İki kez.**

## §81 · M turunun çalışan tarafı (12)

`m1` kâr marjı × kumaş (`order:desc`) · `m3` kalite × vardiya · **`m6` 487 ms** ·
**`m7` 582 ms · iki boyut · 40 satır** · **`m8` 808 ms** · `m9` renk sayımı ·
**`m10` `§60` sahada** (*"ortalama sordun ama toplam"*) · **`m11` `oee ve üretim birlikte`
→ İKİ ÖLÇÜ** ✅✅ · **`m14` `ciro ve fire birlikte çizgi grafik` → iki ölçü + `view: line`**
✅✅ · **`m15` 464 ms** · `m16` en kârlı ay · **`m18` 486 ms**

⊙ `m11` ve `m14`, `§71`'in *"ölçü kaybı"* sınıfının **garson çözdüğünde çalıştığını**
gösteriyor — iki ölçü de `cq`'ya giriyor.

## §82 · TABAN KARARLILIK — ilk beş senaryo

`--live --kararlilik 3` koşumu sürüyor; şu ana kadar:

```
temellendirme      farklı=1  hâkim=3/3
sureklilik_slot    farklı=1  hâkim=3/3
onarim             farklı=1  hâkim=3/3
anlati             farklı=1  hâkim=3/3
sosyal_ve_donus    farklı=1  hâkim=3/3
konu_degisimi      farklı=1  hâkim=3/3   (§79)
```

🔴 **Altı senaryonun altısı da TAM KARARLI.** `§75.6`'nın *"asıl kusur salınımın kendisi"*
tezi giderek daralıyor: salınım **senaryo kümesinde görünmüyor**; L turunda gördüğüm
oynaklık, kümede olmayan **serbest** sorularda.

> *Bir kusurun sınırı, onu aramadığın yerde değil, aradığın yerde bulunmamasıyla
> belirlenir.*

## §83 · NETLEŞTİRME YANLIŞ KÜPLERİ SUNUYOR — sondajla ayrıştı

`§80`'in en ağır bulgusu (`fire oranı en düşük vardiya hangisi` → **İK/İSG/kalite**)
sondalandı — kör yama yapılmadan, canlı konteynerin şemasıyla:

```
'fire orani en dusuk vardiya hangisi'      _match_cube: None   ilgili_cubelar: ['oee','parti']
'kumas cinsine gore ortalama fire orani'   _match_cube: parti  ilgili_cubelar: ['parti']
'vardiya bazinda fire orani'               _match_cube: None   ilgili_cubelar: ['oee','parti']
```

### 83.1 · İki ayrı gerçek — biri kusur DEĞİL

**(a) Beraberlik GERÇEK ve doğru.** `vardiya` **hem `oee` hem `parti`**'de bir boyut;
`fire` de ikisinde birden bir ölçü. Yani *"vardiya bazında fire oranı"* **hakikaten**
belirsizdir ve netleştirme **doğru** cevaptır. Karşı örnek bunu kanıtlıyor: `kumaş cinsi`
yalnız `parti`'de olduğu için o soru **tek küpe** çözülüyor.

⊙ Yani `§80`'de *"aynı ölçü, biri çalışıyor öteki çalışmıyor"* diye yazdığım şey bir
tutarsızlık **değil** — iki sorunun **belirsizlik derecesi farklı**.

**(b) 🔴 AMA SUNULAN KÜPLER YANLIŞ.** `ilgili_cubelar` doğru cevabı biliyor
(`['oee','parti']`) ama kullanıcı **İK / İSG / kalite** görüyor. Yani sistem doğru adayları
hesaplıyor ve **başkalarını gösteriyor**.

> *Belirsizliği sormak doğrudur; yanlış seçenekleri sunmak, soruyu bir engele çevirir.*

### 83.2 · Kök çözüm yönü *(kod DEĞİŞMEDİ — sahibi bulunmalı)*

Netleştirme mesajını kuran yer, adayları `ilgili_cubelar`'dan **almıyor** olmalı; ikinci
bir kaynak kullanıyor (`KAT-1` kokusu). Sıradaki adım: o mesajın sahibini bulup adayları
**tek kaynaktan** okutmak.

⚠ Ve `§78.2`'nin kuralı geçerli: **yazmadan önce ara** — mesajı üreten dal `yetenek.py`
mi, `ask.py`'nin `cube_tie_candidates`'i mi, önce o belirlensin.

## §84 · TABAN KARARLILIK — dokuz senaryo, dokuzu da tam kararlı

```
temellendirme · sureklilik_slot · onarim · anlati · sosyal_ve_donus
kapasite · capa_neden · capa_normal_mi · capa_ne_yapmali        → hepsi 3/3
```

🔴 **Dokuzda dokuz.** `§75.6`'nın *"asıl kusur salınımın kendisi"* tezi artık **iyice
dar**: senaryo kümesinde salınım **yok**. L turundaki oynaklık kümede olmayan **serbest**
sorularda ve muhtemelen **belirsiz** sorularda (`§83`'ün beraberlik sınıfı) yoğunlaşıyor —
ki orada birden çok geçerli cevap **gerçekten** vardır.

> *Belirsiz bir soruya verilen cevabın koşumdan koşuma değişmesi, modelin kararsızlığı
> değil sorunun kendisinin çok cevaplı olmasıdır.*

### 83.3 · 🔴 `§83.1(b)` YANLIŞTI — ve sebebi ÜÇÜNCÜ KEZ aynı tuzak

`§83.1(b)`'de şunu yazdım:

> *"`ilgili_cubelar` doğru cevabı biliyor (`['oee','parti']`) ama kullanıcı İK/İSG/kalite
> görüyor. Sistem doğru adayları hesaplayıp **başkalarını** gösteriyor."*

Mesajın sahibini aradım (`§78.2`: yazmadan önce ara) ve `ask.py:3606`'da buldum:

```python
ilgili = cube_router.ilgili_cubelar(q_norm, schema)
...
konular = ", ".join(c.get("display") ... for c in ilgili[:3])
```

⊙ **Dal zaten `ilgili_cubelar`'ı kullanıyor.** Yani *"başka bir kaynaktan okuyor"* iddiam
yanlış. O hâlde çalışma anında `ilgili_cubelar` **gerçekten** İK/İSG/kalite döndürüyor —
ve benim sondajımın `['oee','parti']` demesinin tek açıklaması, **iki şemanın farklı
olması**.

🔴 **Bu, aynı tuzağın ÜÇÜNCÜ ısırığı:** `§71.5` (`demo/wren-project` bayat artefakt) ·
`§71.6` (per-şirket dosyası da çalışma anıyla aynı değil) · şimdi bu. Sondajlarım
**çalışma anının gördüğü şemayı** okumuyor.

> *Bir ölçüm aracının yanlış kaynaktan okuması bir kez talihsizlik, üç kez bir yöntem
> hatasıdır.*

### 83.4 · Bağlayıcı düzeltme — sondajın TEK meşru yeri

Bundan sonra bir eşleştirme sorusu **yalnız** şu iki yoldan biriyle ölçülür:

1. **Canlı akışa geçici log** (`§71.6`'da işe yaradı: tek satır, tek tur, kesin cevap)
2. **Çalışan konteynerin `/ask` cevabı ve izi** (`trace` alanı hangi dalın konuştuğunu
   söylüyor)

🔴 **Dosyadan şema yükleyip `cube_router`'ı doğrudan çağırmak YASAK** — üç kez yanlış
sonuç verdi ve üçünde de sonucu **gerçek sandım**.

⚠ Ve bu, `§83.1(a)`'yı da şüpheli kılar: *"`vardiya` hem `oee` hem `parti`'de"* iddiası da
aynı bayat şemadan geliyordu. Beraberliğin gerçek olup olmadığı **yeniden** ölçülmeli —
bu kez doğru yoldan.

---

## §85 · N TURU — 20 özgün senaryo, üç kök, ve **ölçüm aletinin üç kez yanılması**

> Kullanıcının turun ortasında verdiği senaryo (`şubat ayı personel verimlilikleri`)
> kökü açan anahtar oldu. Bir soru, üç ayrı kusuru aynı anda gösterdi.

### §85.0 · Taban kararlılık — **ölçüldü ve tez ÇÜRÜDÜ**

    ▶ kararlılık oranı: 100% (25/25 senaryo tam kararlı)

`lab/garson.py --kararlilik 3`, 25 senaryo, 75 koşum. **Sıfır** salınım.

🔴 Ve bu sayı, benim *"salınım baskın kusurdur"* tezimi **çürütür** — ama yalnız
**ölçülen küme** için. Aynı dakikada, canlı `/ask` üzerinde `bu yıl vardiya bazında fire
oranı` iki koşumda **iki farklı yol** izledi (biri 8 satırlık tam cevap, öteki
netleştirme). Yani:

> **Alet %100 diyor çünkü zaten çalışan soruları ölçüyor.**

*Bir kararlılık ölçütü, yalnız kararlı olanları içeriyorsa bir ölçüt değil bir aynadır.*

### §85.1 · Ölçüm aletim bu turda **ÜÇ KEZ** yanıldı — üçü de yazılmadan yakalandı

| # | yanlış okuma | gerçek | nasıl yakalandı |
|---|---|---|---|
| 1 | *"thread'li turlar bağlamı kaybediyor"* | `AskRequest`'te **`thread_id` bağlam taşımaz**; bağlam `history`+`cube_query` ile taşınır — testim thread **kurmamıştı** | şemayı okudum |
| 2 | *"her sorgu 0 satır dönüyor"* | satırlar `result.rows` altında; ben `rows` okuyordum | tam JSON dökümü |
| 3 | *"garson yolunda DÖNEM cq'ya yazılmıyor"* (3 kanıt!) | dönem **yazılıyor**; yazıcım `filters` alanını basmıyordu | tam `cq` + `sql` dökümü |

🔴 Üçü de **kök neden ilan edilmek üzereydi**. Üçüncüsü en tehlikelisiydi: elimde
*"üç bağımsız kanıt"* vardı ve üçü de aynı **alet kusurundan** doğmuştu.

*Aynı yönde üç kanıt, üçü de aynı aletten geliyorsa bir kanıt değil bir kalibrasyon
hatasıdır.*

### §85.2 · KÖK-N1 — **sıralanmamış bir listeye dilim atmak bir seçim değil, bir kuradır**

Sondaj (canlı akışa geçici log, `§83.4` yol-1 — **dosyadan şema yüklenmedi**):

    q='bu yil vardiya bazinda fire orani'
    ilgili=['ik','isg','kalite','makine_duruslari','oee','parti']
    ölçü_sahibi=[]  boyut_sahibi=[('ik','personel_vardiya'),('isg','kaza_vardiya'),
                                  ('kalite','vardiya'),('makine_duruslari','vardiya')]

`ilgili_cubelar` **altı** küp döndürdü; çağıran `[:3]` dedi. Ölçünün gerçek sahipleri
(`parti.fire_orani_yuzde`, `oee.toplam_fire_kg`) listenin **5. ve 6.** sırasındaydı — ve
o sıra **`schema["cubes"]`'in dosya sırasıydı**, bir güç sırası değil.

Kullanıcının gördüğü:

| soru | sunulan konular | sunulan chip'ler |
|---|---|---|
| `…fire oranı` | İK / bordro · İSG · kalite | **brüt maaş · net maaş · işveren maliyeti** |
| `…kaç şikayet geldi` | cari hesap · Satış hunisi · kalite | **borç · alacak · bakiye** |

İkincisinde `sikayet` küpü **vardı** ve gösterilmedi.

**Düzeltme:** sıra artık üç mevcut sinyalden okunur (ölçü sahipliği · küp-düzeyi isabet ·
boyut-düzeyi isabet). **Yeni kelime listesi yazılmadı** (`ADR-0008`); eşitlikte Python'un
kararlı sıralaması dosya sırasını korur.

**Curl doğrulaması (aynı sorular, düzeltmeden sonra):**

| soru | sunulan konular | sunulan chip'ler |
|---|---|---|
| `…fire oranı` | **OEE · parti** · İK | **oee · kullanılabilirlik · performans · fire…** |
| `…kaç şikayet geldi` | **Müşteri şikâyeti** · parti · cari | **şikayet adedi · iade · çözüm süresi** |

*Bir listeyi kesmeden önce sıralamak, kesmenin kendisinden daha önemlidir.*

### §85.3 · KÖK-N2 — 🔴🔴 **HAKEM KONUŞTU, KARARI DUYULMADI**

Canlı log zinciri, **tek istek**, soru `bakım süresi en uzun makine`:

    route ŞÜPHELİ → garson çağrılıyor (§51)      ← route yarım duydu
    intent: 3 oy · 1 farklı aday · kazanan 2 oy  ← garson OYBİRLİĞİYLE geçerli cevap
    CEVAP: not='Hangisini istiyorsun?'           ← ikisi de çöpe

`§51`'in *"garsonun sonucu yalnız daha iyiyse alınır"* süzgeci, uygulamada
*"garsonun cevabı **kusursuz** mu"* diye soruyordu. Ölçüt: **dönem var mı**. Soruda hiç
dönem yoksa — ki bu sorunun bir özelliğidir, cevabın kusuru değil — cevap **her zaman**
*"hayır"* çıkıyordu. Sonuç: **dönemsiz her soruda garsonun kararı otomatik eleniyordu.**

🔴 Ve bedeli yalnız sessizlik değil. Aynı süzgeç route'un **uydurduğu** filtreyi de
hayatta bırakıyordu:

| soru | route'un ürettiği filtre |
|---|---|
| `en verimsiz hattı bul ve nedenini **açıkla**` | `hat = "Açık"` ← *"açıkla"* fiilinden |
| `en düşük OEE'ye sahip makineyi **hariç tut**` | `makine ≠ "en düşük OEE'ye sahip makine"` |

Birincisi `§51`'in **kendi kanıt tablosundaki 2. satırdır** — yamandığı sanılan kusur,
süzgeç yüzünden hâlâ kullanıcıya gidiyordu.

**Düzeltme:** süzgeç **mutlaktan karşılaştırmalıya** çevrildi. `niyet_tasima.eksiklik`
artık bir `bool` değil **adlandırılmış eksiklikler kümesi** döndürür; garsonun cevabı,
bıraktığı eksik route'unkinin **altkümesiyse** kabul edilir. `route_supheli` aynen durur
ve o kümenin boşluğunu okur — **tek sahip** (`KAT-1`).

**Curl doğrulaması** (`bakım süresi en uzun makine`, **iki koşum, birebir aynı** — `G-1` ✅):

    ÖNCE:  not='Hangisini istiyorsun?'                         cq = yok
    SONRA: not='toplam sure dk çıkarabilirim — hangi dönem?'   cq = {makine_duruslari,
           toplam_sure_dk, dims=[makine], filters=[bolum eq "Bakım"], order=desc}

Netleştirme hâlâ dönem soruyor — **doğrusu bu**, soruda dönem yok. Ama artık chip'e
basıldığında elde **doğru kurulmuş** bir rapor var; önce hiçbir şey yoktu.

Ve `en verimsiz hattı bul ve nedenini açıkla`'daki `hat="Açık"` filtresi **yok oldu**.
(Soru şimdi Discovery'ye düşüyor — bu bir **mutfak eksikliği raporudur**, ama *sessiz bir
yanlış* değil **görünür bir eksiktir**. Takas bilinçlidir.)

*Bir eleme ölçütü, elenenin yerine ne konacağını bilmiyorsa bir ölçüt değil bir kayıptır.*

### §85.4 · KÖK-N4 — **sistem sayabildiği şeyi temsil edemiyordu**

`niyet` nesnesi `üstünlük=3` yazıyor, `cube_query.limit` boş kalıyordu:

    T1·5  `en yüksek 3 ayı göster`
    niyet: tür=kirilim+ustunluk · kırılım=donem · üstünlük=3
    cq:    order=desc  ·  limit=YOK      →  kullanıcıya **12 satır**

Sebep: satır limiti *"zaman kovası varsa seriyi keser"* diye **hiç** konmuyordu. Gerekçe
doğru, **kapsamı geniş**: limit seriyi ancak seri **başka bir boyut** üzerinde akıyorsa
keser. Zaman **tek** kırılımsa sıralanan varlık ayın kendisidir.

**Düzeltme:** engel `timeDimensions ∧ dimensions`'a daraltıldı. `dimensions` doluyken
davranış **birebir** korunur (`entity_limit` zaten o işin sahibi).

**Curl doğrulaması:** `limit: 3` · **3 satır** (önce 12).

### §85.5 · N turu tablosu — 20 senaryo

| # | soru | sonuç |
|---|---|---|
| N1 | `geçen ay kaç adet üretim yaptık` | ◐ cevap var; garsonun 2 oyu **uydurma küp** (`uretim`) → beyaz liste reddi |
| N2 | `en yüksek fireli 5 parti` | ◐ dönem sorusu; `5` boyutsuz olduğu için limit anlamsız (ayrı kök) |
| N3 | `bu yıl vardiya bazında fire oranı` | 🔴→🟢 KÖK-N1 |
| N4 | `şubat ayı personel verimlilikleri` *(kullanıcının senaryosu)* | 🔴→◐ KÖK-N1 düzeldi; **mutfak sınırı gerçek** (aşağıda) |
| N5·N13 | `toplam duruş dakikasını hat bazında sırala` | 🔴 `sırala` kayıp — **açık kök** |
| N6 | `bakım süresi en uzun makine` | 🔴→🟢 KÖK-N2 |
| N7 | `en çok enerji harcayan 3 makineyi bul` | ◐ salınım (2/3 aday) |
| N8 | `bu yıl toplam fire kg` | ✅ |
| N9 | `peki geçen yıl?` *(takip)* | ✅ **ölçü korundu**, dönem taşındı |
| N10 | `ikisini karşılaştır` *(takip)* | 🔴 `temsil-yok=kiyas` içeride yazılı, **kullanıcıya beyan yok** |
| N11 | `bunu aylara böl` *(takip)* | ✅ |
| N12 | `en yüksek 3 ayı göster` *(takip)* | 🔴→🟢 KÖK-N4 |
| N14 | `which machine had the most downtime last month?` **[EN]** | ✅ + dürüst boş-aralık beyanı |
| N15 | `ما هو إجمالي الإنتاج هذا العام؟` **[AR]** | ✅ (küp seçiminde salınım) |
| N16 | `iyi çalışmalar, bu ay kaç iş kazası oldu` | ✅ sosyal+veri ayrımı çalıştı |
| N17 | `geçen çeyrek OEE ortalaması kaç` | ✅ |
| N18 | `en verimsiz hattı bul ve nedenini açıkla` | 🔴→🟢 uydurma filtre yok oldu |
| N19 | `en düşük OEE'ye sahip makineyi hariç tut` | 🔴 uydurma filtre — **açık kök** |
| N20 | `son 3 ayda hangi müşteriden kaç şikayet geldi` | 🔴→🟢 KÖK-N1 |

**Discovery ateşlemesi (mutfak eksikliği raporu): E=4 · F=1 · G=1 · N=1.**

### §85.6 · Ve bir MUTFAK sınırı — garson suçsuz, `§0.0`'ın teşhis kuralı işledi

Canlı şemadan (çalışan konteynerin `/schema` ucu) okundu:

| istek | ölçü nerede | kırılım nerede | tek küpte buluşuyor mu |
|---|---|---|---|
| `vardiya bazında fire oranı` | `parti.fire_orani_yuzde` | `vardiya` → `oee`·`kalite`·`isg`·`ik` | ❌ |
| `personel verimlilikleri` | `oee.ort_oee` | `personel` → `parti`·`ik`·`egitim` | ❌ |

Garson `{"cube": null}` derken **doğruyu söylemişti**: hiçbir küp siparişi tek başına
karşılayamıyor. `§0.0`'ın teşhis kuralı aynen: *"garson doğru girdi sağladı ve yine
çalışmadıysa kusur **mutfaktadır**."*

🔴 Ama sistemin kullanıcıya söylediği cümle bir **yalan**: *"hangi **ölçüyü** istediğini
anlayamadım."* Ölçüyü biliyor — **birleştiremiyor**. Doğru cümle bunu söylemelidir
(`KÖK-3`, beyan-açık). **Açık borç.**

*Bilmediğini söylemek dürüstlüktür; bildiğini bilmediğini söylemek değildir.*

---

## §86 · 🔴🔴 GERİ ALINMIŞ SAYILAN BİR DEĞİŞİKLİK, GERİ ALINMAMIŞTI

### §86.1 · Nasıl ortaya çıktı — **tabanı ölçmeden okumayı reddederek**

`§85`'in kapısı `dogru: 91` verdi. Belgede yazılı son sayı **93**'tü. Doğruluk vetosunun
kuralı açık (`§73.7`): *"`sessiz_yanlis` sabit kalsa bile `dogru` düşerse geri alınır."*
Yani üç düzeltmeyi geri almak üzereydim.

🔴 **Almadım — çünkü tabanı ölçmemiştim.** İzole bir `git worktree`de HEAD (`0ec34da`)
aynı kapıyla koşuldu:

| ölçüt | HEAD **tabanı** | `§85` demeti | okuma |
|---|---|---|---|
| `vaka` | 2285 | 2285 | payda sabit |
| `kabul` | 1157 | 1157 | — |
| `dogru` | **91** | **91** | ✅ düşüş **benim demetimin değil** |
| `sessiz_yanlis` | 12 | 12 | ✅ veto geçildi |
| `beyanli_kismi` | 49 | 49 | — |

**Birebir aynı.** Yani üç düzeltme korpusu ne iyileştirdi ne bozdu — ve `93 → 91` düşüşü
**çok daha önce** olmuştu.

*Bir sayının düştüğünü görmek, onu senin düşürdüğün anlamına gelmez. Tabanı ölçmeden
verilen geri-alma kararı, doğru bir kuralın yanlış uygulanmasıdır.*

### §86.2 · Kök — belgeye yazılmış bir geri alma, geri alma değildir

`git log`:

    9c4d0f5  revert(§73): korpus hakemlik etti — dogru 93→91, süit 4 kırmızı, GERİ ALINDI

Commit mesajı ölçümü satır satır taşıyor. **Dokunduğu dosyalar:**

    belgeler/denetim/2026-08-07_CEVIRI-SOZLESMESI.md | 37 +
    belgeler/mimari/V1-MIMARI-HARITASI.md            | 15 +

🔴 **Koda sıfır satır.** `§73`'ün tek satırlık kod farkı (`_SUFFIX_ATOMS`'tan
`y`·`n`·`s`·`m` çıkarılması) HEAD'de **hâlâ duruyordu**:

    git diff 761928d^ HEAD -- backend/app/cube_router.py
    -    "i", "u", "e", "a", "y", "n", "s", "m",
    +    "i", "u", "e", "a",

Ve HEAD'in korpus sayıları (`1157 · 91 · 49`) **§73'ün tedavi sayılarının birebir aynısı**.
Dört ölçütün dördünün rastlantıyla eşleşmesi mümkün değil: **tedavi hâlâ uygulanmış
hâldeydi.**

### §86.3 · Neden on commit boyunca görünmedi

Çünkü **kapı toplu koşuluyor** (`SIFIRINCI KURAL`) ve `9c4d0f5` ile `0ec34da` arasında
hiç koşmadı. Kural doğrudur ve beş kat israfı önlemiştir — ama bir yan etkisi ölçüldü:

> **Toplu kapı, aradaki bir kararın uygulanıp uygulanmadığını sormaz.**

Bu, deponun `KAT-1` sınıfının (*"aynı kuralın iki sahibi"*) **süreç düzeyindeki** hâlidir:
karar iki yerde yaşıyordu — **belgede** ve **kodda** — ve ikisi ayrıştı. Belge *"Geri
alındı."* diyordu; o cümle **yanlıştı** ve on commit boyunca doğru sanıldı.

⚠ Bedeli yalnız iki puan değil: `§73.7` *"tam süit **4 kırmızı**"* diye ölçmüştü. O dört
test, geri alma uygulanmadığı için **hâlâ kırmızıydı** — ve `--hepsi` yerelde koşulmadığı
için görünmüyordu.

### §86.4 · Karar UYGULANDI

`y`·`n`·`s`·`m` envantere **döndürüldü**. Bedeli bilinçli: `kar ⊂ karşılaştır` kusuru geri
geldi ve **açık bırakıldı** — `§0.0` onu route'ta değil **garsonda** çözmeyi emrediyor.

*Bir ölçüm, kararını koda dokundurmadıysa bir ölçüm değil bir anıdır.*

### §86.5 · Ve bu turun kendi dersi

Bu tur üç kez ölçüm aletine (`§85.1`), bir kez de **tabana** yanıldı. Dördünde de aynı
şey kurtardı: *iddiayı yazmadan önce ölç.* Dördünün de yazılmış hâli bir **kök neden**
olacaktı ve dördü de **yanlış** olacaktı.

> 🔴 **YENİ BAĞLAYICI (`§86.6`):** bir kapı sayısı beklenenden düşükse, **önce tabanı
> ölç** — izole `worktree` + aynı kapı + aynı artefakt. Taban ölçülmeden verilen bir
> geri-alma kararı, doğru düzeltmeleri de çöpe atar.

### §86.7 · Demetin kapanış tablosu — **tek** `--hepsi` koşumu

| ölçüt | HEAD tabanı | `§85` demeti | **+ `§86` geri alma** |
|---|---|---|---|
| `vaka` | 2285 | 2285 | 2285 |
| `kabul` | 1157 | 1157 | 1153 |
| `dogru` | 91 | 91 | **93** (+2) |
| `sessiz_yanlis` | 12 | 12 | **12** ✅ doğruluk vetosu |
| `beyanli_kismi` | 49 | 49 | 51 |
| tam süit | — | — | **4257 yeşil · 32 atlandı** |
| `eval` | — | — | precision **+0,0%** · coverage **+0,0%** |
| korpus doğru-cube | %95.1 | %95.1 | **%95.1** (taban %95.1) |

⊙ Okuma: `§85`'in üç düzeltmesi korpusu **hiç oynatmadan** dört ölçülmüş canlı kusuru
kapattı; `§86`'nın uygulanmamış geri alması `dogru`'yu **+2** yükseltti ve `§73.7`'nin
ölçtüğü **dört kırmızı testi** kapattı. İkisi ayrı ayrı ölçüldüğü için hangi kazancın
kimin olduğu **karışmadı**.

### §86.8 · 🔴 AÇIK KÖK (O turuna devreder) — **bir fiil, bir kategori değeri değildir**

Geri almadan sonra aynı sorunun **yeni kılıkta** ürettiği uydurma filtre:

| soru | üretilen filtre | gerçek |
|---|---|---|
| `en verimsiz hattı bul ve nedenini **açıkla**` | `renk = "Açık"` | *"açıkla"* bir **fiil** |
| `en düşük OEE'ye sahip makineyi **hariç tut**` | `makine ≠ "en düşük OEE'ye sahip makine"` | değer değil, **cümlenin kendisi** |

⊙ Bu, `§G/AJ0`'ın yazım önerisinde çözdüğü ayrımın **değer eşleştirmesindeki** hâlidir
(*«arttı» bir FİİL, yazım hatası DEĞİL*). Orada bir sahip var; burada yok — yani `KAT-1`
değil, **sahipsizlik**. Çözüm yeri route'un değer eşleştiricisidir ve ölçütü zaten
yazılmıştır: *çekimli bir fiil biçimi bir kategori değeri olamaz.*

⚠ İkincisi daha ağır: filtre değeri **kullanıcının kendi cümlesi**. Hiçbir katalog değeri
o dizeye eşit olamayacağı için sorgu **sessizce boş** dönebilir — yani `KÖK-3`'ün
(beyan-açık) kapsamadığı bir sessiz yanlış.

*Bir değer eşleştiricisi, eşleştiremediğinde durmayı bilmiyorsa bir eşleştirici değil bir
uydurucudur.*

---

## §87 · O TURU — 20 yeni senaryo · ve deponun kendi kaydı bir hipotezimi çürüttü

*(Kullanıcının turun ortasında verdiği senaryo `o1` olarak ilk sıraya alındı.)*

### §87.1 · O1 — `şubatta ocağa göre ciro değişimi` **[kullanıcının senaryosu]**

**İki koşum, birebir aynı** (`KURAL G-1` ✅ — yani salınım değil, **gerçek ve kararlı**):

    not   = "Hangisini istiyorsun?"
    trace = self-consistency uyuşmazlığı (%33 uyum / 3 örnek, eksen=None)
            niyet: tür=kiyas+trend · 🔴temsil-yok=kiyas · dönem=1 · bilinmeyen=ocaga

Sistem soruyu **anlıyor** (`tür=kiyas+trend`), temsil edemediğini de **biliyor**
(`temsil-yok=kiyas`) — ve kullanıcıya bunların hiçbirini söylemeden *"Hangisini
istiyorsun?"* diyor.

### §87.2 · 🔴 Ve iki senaryo, kökü **çürütücü** biçimde aydınlattı

| # | soru | sonuç |
|---|---|---|
| `o8` **[EN]** | `compare february and january revenue` | 🟢 **2 satır** · Ocak + Şubat ciro · **%100 uyum** |
| `o19` **[takip]** | `bu ay fire` → `geçen aya göre nasıl` | 🟢 `Takip: dönemsel kıyas (mom, LLM'siz)` · `toplam_fire_kg`+`_gecen`+`_degisim_yuzde` |

⊙ Birincisi: **`CubeQuery` iki dönemi temsil EDEBİLİYOR** (ay granülerliği + kapsayan
aralık). Yani `o1`'in kusuru bir **temsil** kusuru değil.
⊙ İkincisi: **kıyas makinesi VAR ve çalışıyor** — ama yalnız **takip** yolunda
(`kiyas_cebiri`/`mom`). Taze soru ona **erişemiyor**.

🔴 **KÖK-O4 · KİMLİK ASİMETRİSİ, ÜÇÜNCÜ KEZ.** `MIMARI §6.1h`'nin adını koyduğu desen:
bir yetenek takip yolunda var, taze yolda yok. Daha önce **Discovery** için ve
**çapraz-alan pilotu** için ölçülmüştü; bu üçüncüsü. Ve `§72` tam da bunun için:
**İngilizce soru, Türkçe sorunun gizlediği şeyi gösterdi** — eksik olan dil değil, **yol**.

*Bir yeteneğin iki yoldan yalnız birinde bulunması, o yeteneğin yarısının olmamasıdır.*

⚠ Bu tur **yazılmadı** — ölçüldü, adı kondu, `P` turuna devredildi. Kör yama yok.

### §87.3 · 🔴 Deponun kendi kaydı hipotezimi çürüttü — turun **dördüncü** öz-düzeltmesi

`o7` (`2025 ve 2026 fire kg farkı`) *"«fark» (enerji_sapma) + «fire»"* diye iki konu
gördü. *"«fark» bir kıyas sözcüğü, dolgu sözlüğüne eklenmeli"* diye yazmak üzereydim.
`_misc_hit_words`'ün docstring'i:

> **`fark` BİLEREK EKLENMEDİ** — ölçüldü: `enerji_sapma.toplam_enpg`'nin **gerçek ölçü
> sinonimi**. Dolgu saymak onu gölgelerdi; `2a-1`'in (`elektrik`) tam olarak ölçümle
> reddedilen hatası.

**Reddedilmiş bir deneyi tekrarlayacaktım.** `YAZMADAN ÖNCE ARA` kuralı dördüncü kez
kurtardı.

⊙ Doğru okuma başka: `niyet` o soruda **`dönem=2(çözülemedi)`** yazıyor. Yani ayırt edici
işaret sözcük değil **yapı**: *soruda iki dönem varsa, bir kıyas sözcüğü kıyas
sözcüğüdür.* Bu bir hipotezdir ve **ölçülmeden yazılmayacaktır**.

### §87.4 · KÖK-O2 — beyan sınıfı belgede vardı, **kodda yoktu**

`uyum.py`'nin `olcu_ikamesi` yükleminin docstring'i dört sınıf sayıyor:
`maliyet`·`₺`·`ortalama`·**`oran`**·**`yüzde`**. Kodu **ikisini** uyguluyordu.

Ölçüldü (`o16`): `iş kazası **oranı** yıllara göre nasıl değişti` → `isg.kaza_adedi`
(birim **boş** — bir sayım), 5 satır, **hiçbir beyan yok**. `niyet` biliyordu:
`bilinmeyen=orani`.

🔴 Bu, `§86`'nın **kardeşidir**: orada bir **geri alma**, burada bir **beyan sınıfı**
yazılmış ama yapılmamıştı. Deponun kendi cümlesi: *"belgelenmiş davranışla kodun
ayrışması, bu depoda tekrar eden en pahalı hata sınıfıdır."*

**Curl doğrulaması:**

> *"⚠ Sayı doğru ama **eksik**: bir **oran/yüzde** sordun ama `kaza_adedi` bir **adet** —
> payda katalogda tanımlı değil."*

Cevap **yaşıyor** (5 satır), ikame **beyan ediliyor** — `KÖK-3` sözleşmesi aynen.

### §87.5 · KÖK-O3 — sıralamayı kurtardık, **sayıyı yerde bıraktık**

Sondaj (canlı akışa geçici log, **iki koşum birebir** — `G-1` ✅):

    o11: `en az arıza veren 5 makine`
    SONDAJ-O11: order=None limit=None cq_limit=None dims=['makine'] gran=None
    niyet:      tür=kirilim+ustunluk · üstünlük=5

`route()` **ikisini birden** düşürdü; `§34` (`siralama.tamamla`) sıralamayı geri koydu,
**sayıyı kimse geri koymadı**. Kullanıcı *"5"* dedi, sıralanmış ama **kesilmemiş** bir
tablo aldı.

⊙ Ve `§34`'ün kendi sınırı bunu **zaten** ayırıyordu: *"**sayı vermediyse** kesmemek
doğrudur"*, ve kendi tablosunun 4. satırı (`en az üretim yapan 3 makine → order:asc +
limit:3`) sayının verildiği hâli **beklenen davranış** diye gösteriyor. Kural iki durumu
ayırıyordu; **uygulaması ayırmıyordu**.

Bu, `§N4`'ün **taze yoldaki ikizidir** ve aynı seri-koruma kaydını taşır.

**Curl doğrulaması:** `cq` artık `… order:asc, **limit: 5**`.

*Sayı verilmişse kesmek bilgi çıkarmaz — sözü yerine getirir.*

### §87.6 · O turu tablosu

| # | soru | sonuç |
|---|---|---|
| O1 | `şubatta ocağa göre ciro değişimi` **[kullanıcı]** | 🔴 kararlı — KÖK-O4 |
| O2 | `hangi hatta en çok rework var` | ◐ doğru `cq`, dönem sorusu |
| O3 | `kalite maliyeti nedir` | ◐ dürüst *"şunları çıkarabilirim"* |
| O4·O5 | `bu yıl OEE` → `hat bazında` | ✅ 8 satır |
| O6 | `en düşük olanı hangisi` | ◐ sıralı 8 satır (`§34` kararı: kesmiyor) |
| O7 | `2025 ve 2026 fire kg farkı` | 🔴 `«fark»`=ölçü — **hipotezim çürüdü**, bkz. §87.3 |
| O8 **[EN]** | `compare february and january revenue` | 🟢 **2 satır, %100** |
| O9 **[DE]** | `Wie hoch war der Ausschuss im letzten Monat?` | 🔴 %33 salınım |
| O10 | `geçen hafta üretim adedi` | 🔴 %50 salınım |
| O11 | `en az arıza veren 5 makine` | 🔴→🟢 KÖK-O3 |
| O12 | `ortalama çözüm süresi kaç gün` | ✅ doğru `cq` |
| O13·O14·O15 | `toplam ciro` → `müşteriye göre böl` → `en yüksek 5'i` | ✅ `limit:5` |
| O16 | `iş kazası oranı yıllara göre nasıl değişti` | 🔴→🟢 KÖK-O2 |
| O17 | `en çok eğitim alan personel` | ◐ sıralı, sayısız (doğru) |
| O18 | `bu ay fire` | ✅ dürüst boş-aralık beyanı |
| O19 | `geçen aya göre nasıl` | 🟢 **mom kıyası çalıştı** |
| O20 | `hedefin altında kalan hatlar` | 🔴 %50 salınım |

**Discovery ateşlemesi: 0.** (E=4 · F=1 · G=1 · N=1 · **O=0**)

### §87.7 · 🔴 EN BÜYÜK **SINIF**: garson salınımı — 4/20

`o1` %33 · `o9` %33 · `o10` %50 · `o20` %50. Dördünde de garson **cevap üretti**, oylar
uzlaşmadı ve kullanıcı **hiçbir şey** almadı.

⚠ `§77`'nin `oylama_cogunluk` bayrağı bu sınıf için yazılmıştı ama **çare değil**:
%33 (1-1-1) ve %50 (1-1) beraberliklerinde çoğunluk **yok**. Ölçülecek asıl kaldıraç
`consistency_k` (3 → 5): daha çok örnek, daha net çoğunluk. **Ölçülmeden açılmayacak.**

⊙ Ve `kartaban`ın `%100 (25/25)` taban kararlılığı bu dördünü **görmüyor** — çünkü o
küme zaten çalışan soruları ölçüyor (`§85.0`).

### §87.8 · O demetinin kapısı — **tek** `--hepsi` koşumu

| ölçüt | `§86` sonrası taban | **O demeti** |
|---|---|---|
| `vaka` | 2285 | 2285 |
| `kabul` | 1153 | **1153** |
| `dogru` | 93 | **93** |
| `sessiz_yanlis` | 12 | **12** ✅ doğruluk vetosu |
| `beyanli_kismi` | 51 | **51** |
| tam süit | 4257 yeşil | **4257 yeşil · 32 atlandı** |
| `eval` | +0,0% | **precision +0,0% · coverage +0,0%** |

⊙ Okuma: iki düzeltme (`§O2` beyan sınıfı · `§O3` sayı kurtarma) **korpusu hiç
oynatmadan** iki ölçülmüş canlı kusuru kapattı. `beyanli_kismi` **artmadı** — yeni beyan
sınıfı korpusta yanlış-pozitif üretmiyor; canlıda ise `o16`'da ateşliyor. *Dar bir
yüklem, geniş bir yüklemin veremeyeceği güveni verir.*

### §87.9 · Turun bilançosu — iki demet, dört düzeltme, iki keşif

| # | ne | ölçülen |
|---|---|---|
| `§85.2` | sıralanmamış listeye dilim | fire sorusuna `brüt maaş` chip'i → `şikayet adedi · iade · çözüm süresi` |
| `§85.3` | hakem konuştu, kararı duyulmadı | *"Hangisini istiyorsun?"* → tam kurulmuş `cq` (+ uydurma filtre yok oldu) |
| `§85.4` | `üstünlük=3` niyette, `limit` yok *(takip)* | 12 satır → **3 satır** |
| `§O3` | aynı kusurun **taze yol** ikizi | `limit` yok → **`limit: 5`** |
| `§O2` | beyan sınıfı belgede vardı, kodda yoktu | sessiz ikame → **beyanlı ikame** |
| `§86` | **geri alma yazılmış, yapılmamış** | `dogru` 91 → **93** · **4 kırmızı test kapandı** |

**Açık kökler (P turuna):** `KÖK-O4` kimlik asimetrisi (kıyas yalnız takip yolunda) ·
garson salınımı 4/20 (`consistency_k` 3→5 ölçülecek) · fiil/cümle bir kategori değeri
sanılıyor (`§86.8`) · `temsil-yok=kiyas` takip yolunda **yanlış-pozitif** (kıyas
çalışırken bile beyan ediliyor).

---

## §88 · P TURU — agentic zincirler · ve MUTFAK DENETİMİ raporunun ilk demeti

Bu tur iki girdiyle kuruldu: **(1)** kullanıcının üç agentic örneği birer **thread
zinciri** olarak, **(2)** `belgeler/denetim/2026-08-08_MUTFAK-DENETIMI.md`'nin kök
listesini canlıda yoklayan dört tur. 20 senaryonun 12'si thread, 8'i tekil.

### §88.1 · P turu tablosu

| # | senaryo | sonuç |
|---|---|---|
| P1 | `makine verimliliklerini listele` | ◐ doğru `cq`, dönem sorusu |
| **P2** | `bunların bu yılki karlılığa etkisini analiz et` | 🔴 **karlılık sessizce düştü** — `Ajan koşusu: 0 adım · 0 sorgu`, beyan yok |
| P3 | `en çok etkileyen üçünü grafikte göster` | 🟢 `limit:3` (`§O3` çalışıyor) |
| **P4** | `aynı grafikte hem verimliliği hem karlılığı göster` | 🔴→🟢 KÖK-P5 |
| P5 | `personel çalışma süreleri ve verimliliklerini kıyasla ve listele` | ◐ Discovery **iyi cevap verdi** (29 satır) — mutfak eksikliği |
| **P6·P7·P8** | `en düşüğü hangisi` · `neden düşük olduğunu analiz et` · `dağılım grafiğine çevir` | 🔴→🟢 **üçü de ÖLÜ** — KÖK-P1 |
| P9 | `ciromun en büyük 3 kaynağı olan müşterilerimi bul` | 🟢 `limit:3` |
| **P10** | `bunlara en çok neler sattığımı karşılaştır` | 🔴 `limit` **3 → 100**, çapa kayıp |
| P11 | `bu yıl` *(çip cevabı)* | ◐ 8 satır ama `limit:100` **kalıcı** |
| **P12** | `üçü için de ayrı ayrı göster` | 🔴 `ort_renk_sapmasi` **uyduruldu**, `üçü` anlaşılmadı |
| P13 | `bu yıl toplam üretimin yüzde kaçı fire` | 🟢 **%19,79** — raporun *"cevapsız"* dediği vaka **artık çalışıyor** |
| P14 | `bu yıl en çok enerji harcayan 3 makineyi bul` | 🔴 **M-2 canlıda doğrulandı** |
| **P15** | `bu yıl aylık kümülatif fire toplamını göster` | 🔴 `kümülatif` **sessizce düştü** |
| **P16** | `bu yıl her hattın toplam fire içindeki payı` | 🔴 `payı` **sessizce düştü** |
| P17 | `hedefin üzerinde kalan makineleri bul ve nedenlerini sırala` | 🔴 «kalan» → `cari/mizan` ölçüsü |
| **P18 [EN]** | `show me the top 3 lines by OEE and their scrap rate side by side` | 🔴 `üstünlük=3` **bulundu**, `order`/`limit` **yok** |
| P19 | `vardiya ve hat kırılımında fire oranını ısı haritası yap` | 🔴 M-1 ortak boyut |
| P20 | `son 6 ayda fire artan makineleri artış yüzdesiyle sırala` | 🔴 M-9 pencere |

**Discovery ateşlemesi: 1** (P5). *(E=4 · F=1 · G=1 · N=1 · O=0 · P=1)*

### §88.2 · 🔴🔴 KÖK-P1 — **DISCOVERY CEVABI THREAD'İ ÖLDÜRÜYOR** (3/3)

`T-P2` zincirinde Discovery **iyi bir cevap verdi** — 29 satır, personel çalışma saati +
ortalama OEE, tam da `M-1`'in *"ölçü bir küpte, boyut başkasında"* vakası. Sonraki **üç**
turun **üçü de** şunu aldı:

    "Önceki rapor artık çalıştırılamadı (şema değişmiş olabilir). Yeni bir soru olarak sorar mısın?"

⊙ Kök: `adhoc` şemada bir küp **değildir**, bu yüzden Gitaş 500'ü için yazılmış *"bayat
`cube_query`"* koruması (`ask.py:3803`) **her** Discovery takibinde ateşliyordu. Ve cümle
bir **yalandı** — şema değişmemişti.

🔴 `adhoc` **bayat bir `cq` değildir**; yeniden çalıştırılabilir bir **yapısı olmayan**
bir cevaptır. İkisi aynı sanılınca kullanıcı bir cevap alıp üstüne **tek kelime** edemez
hâle geliyor — yani sistemin en çok yardıma muhtaç olduğu anda thread **tamamen** ölüyor.

**Düzeltme:** çapa `adhoc` ise yapısal takip sayılmaz; tur **tazedir** ve garson devreye
girer (`§0.0`: *kullanıcı asla cevapsız kalmaz*).

**Curl doğrulaması (dalın doğrudan sınanması):**

    ÖNCE : "Önceki rapor artık çalıştırılamadı (şema değişmiş olabilir)."
    SONRA: "is emri adedi çıkarabilirim — hangi dönem için?"   yeni_konu=True

*Bir cevabın üstüne devam edilemiyorsa sebebi söylenir; sebebi uydurulmaz.*

### §88.3 · KÖK-P5 — `refine_cube` tek çağrı, yedeği yok

`p4`'ün logu:

    SaglayiciYaniti: openrouter BOŞ içerik döndürdü (finish_reason=stop).
    Model AKIL YÜRÜTÜYOR ve token bütçesi `reasoning`'e gitti.
    → "Bu takip mesajını önceki raporla ilişkilendiremedim."

⊙ Kardeşi `select_cube` bu dersi **zaten öğrenmişti** (`_select_consistent` onu `k` kez
örnekler, bir örneğin düşmesi turu düşürmez). `refine_cube` **tek** çağrıdır: modelin bir
tökezlemesi, kullanıcıya `§0.0`'ın yasakladığı cümle olarak dönüyordu.

**Düzeltme:** yalnız **boş yanıt** için **bir kez** yeniden deneme, ve düşen deneme
loglanır (`ADR-0020`). *Her hatayı yeniden denemek, hiçbirini denememektir.*

### §88.4 · M-7 UYGULANDI — **menü pusulası** *(raporun 1 numaralı önceliği)*

Rapor doğrulandı ve koda karşı sınandı: `_uncovered` kelimeleri `re.findall(r"[a-z]+")`
ile ayırıyor; Türkçe harfler `[a-z]` dışında olduğu için ham metin kelimenin
**ortasından** bölünüyor (`müşteri`→`teri` · `bazında`→`baz`+`nda`). Altı çağıranın beşi
normalize gönderiyor, `app/answer.py:181` **ham** gönderiyor — ve orası tam olarak
**telemetriyi** yazan yer.

⊙ Ve raporun görmediği bir yarısı daha var: **aynı satırdaki** `measure_cube_candidates`
de ham besleniyor ve `_syn_hit` de normalize girdi varsayıyor (`[a-z0-9]` kalıpları) —
yani `aday_cubelar` telemetrisi de aynı körlüğü taşıyordu. Düzeltme **ikisine birden**
uygulandı.

**Ölçülen bedel (canlı kütük, 769 tur):** `uncovered_words` dolu **196 satırın 115'i
(%58,7)** parça içeriyor; en sık *"bilinmeyen kelimelerimiz"* `nda` (36) · `baz` (29) ·
`duru` (16) · `nas` (13). Menüyü hangi yönde büyüteceğimize karar verirken baktığımız
**tek sinyal** budur.

⚠ **Geriye dönük değildir:** kütükteki 115 bayat satır düzelmez, ölçüm bu commit'ten
sonra yeniden başlar. *Bir ön koşulu ortadan kaldırmak, onu doğrulamaktan ucuzdur.*

### §88.5 · Ölçülüp YAZILMAYAN kökler — P turunun devri

| kök | kanıt | neden bu turda yazılmadı |
|---|---|---|
| **P2 · agentic kapsam sessizce daralıyor** | `karlılığa etkisini` → `Ajan koşusu: 0 adım`, OEE raporu yeniden yorumlandı, **beyan yok** | yüklem dar yazılmalı; `bilinmeyenler`'in **hangi** üyesi bir dönüşüm talebidir? |
| **P15·P16 · aynı sınıf** | `kümülatif` · `payı` → `bilinmeyen`'e yazıldı, cevaptan düştü, beyan yok | ⇧ aynı yüklem |
| **P10·P11 · `limit` çapası 3→100** | `limit:100` nereden geliyor, sondajlanmadı | 🔴 KÖR YAMA YASAK |
| **P18 · [EN] top-N kayıp** | garson 3 oyun **2'sinde çekimser**, hayatta kalan oy `order`/`limit` taşımıyor | kök garsonun **istem metni**nde (`§48` sınıfı), route'ta değil |
| **P14 · M-2 varsayılan ölçü** | `üstünlük=3`+`kırılım=makine`+`dönem=1` tam, eksik olan **menü** | menü dosyası işi — kendi demetinde inmeli |
| **`en düşüğü` → `order:desc`** | doğrulama turunda görüldü: *en düşük* isteniyor, **azalan** sıralanıyor | tek koşum — `KURAL G-1` gereği ikinci koşum bekliyor |

*Bir turda ölçülen her kusuru yazmak, hiçbirini doğru yazmamaktır.*

### §88.6 · P demetinin kapısı — **tek** `--hepsi` koşumu

| ölçüt | O sonrası taban | **P demeti** |
|---|---|---|
| `vaka` · `kabul` | 2285 · 1153 | **2285 · 1153** |
| `dogru` | 93 | **93** |
| `sessiz_yanlis` | 12 | **12** ✅ doğruluk vetosu |
| `beyanli_kismi` | 51 | **51** |
| tam süit | 4257 yeşil | **4257 yeşil · 32 atlandı** |
| `eval` | +0,0% | **precision +0,0% · coverage +0,0%** |

⊙ Üç düzeltme (`KÖK-P1` · `KÖK-P5` · `M-7`), **sıfır** korpus hareketi. Üçü de canlı
yoldaki bir **ölü uç**u kapatıyor ve hiçbiri korpusun ölçtüğü şeye dokunmuyor — çünkü
korpus `rule` sağlayıcıyla koşuyor, yani takip yolunun LLM dalını **hiç görmüyor**.

🔴 **Bu, korpusun bir sınırıdır ve kayda geçirilir:** son **üç** demette de korpus
**tamamen** sabit kaldı (`93/12/51`), oysa üçünde de canlı davranış **ölçülebilir**
biçimde düzeldi. *Bir kapı, ölçmediği bir yerde yeşil kalır — ve bu yeşil bir onay
değildir.*

### §88.7 · MUTFAK DENETİMİ raporunun durumu

| kök | rapor önceliği | durum |
|---|---|---|
| **M-7** telemetri normalizasyonu | 1 | ✅ **UYGULANDI** (+ raporun görmediği ikiz `measure_cube_candidates`) |
| **M-2** ölçü rolü + varsayılan | 2 | 🔴 canlıda **doğrulandı** (`p14`) — menü demeti, sırada |
| **M-5** toplanabilirlik beyanı | 3 | ⏳ sınanmadı (`E` ailesi) |
| **M-4** varsayılan dönem | 4 | 🔴 P turunda **8 senaryoda** görüldü (*"hangi dönem için?"*) |
| **M-6** operatör tek kaynak | 5 | ⏳ bugün NO-OP |
| **M-3** türev ölçü | 6 | ◐ `p13` **artık çalışıyor**; `p16` (`payı`) hâlâ düşüyor |
| **M-9** pencere katmanı | 7 | 🔴 `p15` (`kümülatif`) · `p20` (artış %) doğrulandı |
| **M-1** uyumlu boyut | 8 | 🔴 `p19` · `p5` (Discovery bu yüzden ateşledi) doğrulandı |
| **M-8** kaynak farkı beyanı | 9 | ⏳ |

⊙ Raporun bir iddiası **çürüdü ve bu iyi bir haber**: *"bu yıl toplam üretimin yüzde kaçı
fire → cevapsız"* dediği vaka **artık %19,79 döndürüyor** (`p13`). Rapor eski kütükten
okuduğu için son turların kazancını göremiyordu. *Bir denetim raporu da bayatlar.*

---

## §89 · R TURU — üç agentic zincir · ve **sözünü yarım tutan sistem**

### §89.1 · R turu tablosu (20 senaryo · 14'ü thread)

| # | senaryo | sonuç |
|---|---|---|
| R1 | `geciken siparişlerin müşteri bazında dağılımı` | 🟢 `geciken` → `termin_durumu ≠ ZAMANINDA` |
| R2 | `bunların toplam tutarı ne kadar` | 🟢 filtre korundu, ölçü değişti |
| R3 | `bu yıl` *(çip)* | 🟢 dürüst boş-aralık beyanı (`28.11.2023 – 22.06.2026`) |
| **R4** | `en çok geciken **üç** müşteriyi ayrı ayrı incele` | 🔴 sayı **yazıyla** → `üstünlük` çözülmedi |
| R5 | `bunun zaman içinde nasıl değiştiğini göster` | 🟢 aylık trend uygulandı |
| R6 | `enerji maliyetinin toplam üretim maliyeti içindeki payı` | 🔴 Discovery bütçe aşımı (25 sn) |
| R7·R8 | `hangi bölüm en çok tüketiyor` → `bu yıl` | 🟢 5 bölüm, sıralı |
| **R9** | `o bölümün tüketimini geçen yılla kıyasla` | 🟢🟢 **YoY çalıştı** — `_gecen` + `_degisim_yuzde` |
| **R10** | `ikisini tek grafikte üst üste bindir` | 🔴 kıyas kolonları **sessizce düştü** |
| **R11** | `bu yıl en çok rework yapılan **3** makineyi bul` | 🔴→🟢 **KÖK-R1** |
| R12 | `her biri için en sık rework sebebini göster` | 🟢 66 satır, `facet` görünüm ◐ *(grup-içi ilk-1 yok — M-9)* |
| R13 | `sebep dağılımını yüzde olarak ver` | 🟢 **`§O2` beyanı takipte de ateşledi** |
| **R14** | `bunu ısı haritasına çevir` | 🔴 `viz.kind` değişmedi (`stacked` kaldı) |
| R15 | `bu ay en düşük OEE'ye sahip hattı bul` | 🟢 `order: asc` **doğru** |
| **R16 [EN]** | `which 5 customers contributed most to revenue growth this year` | 🔴 `5` **ve** `growth` — ikisi de sessizce düştü |
| **R17 [AR]** | `أعطني نسبة الهدر لكل خط إنتاج هذا الشهر` | 🟢🟢 `parti.fire_orani_yuzde` × `hat` — **garson Arapçada işini yaptı** |
| **R18** | `son 12 ayın hareketli 3 aylık fire ortalamasını çiz` | 🔴 `hareketli` sessizce düştü (M-9) |
| R19 | `makine ve vardiya kırılımında duruş süresini çapraz tablo yap` | ◐ iki boyut doğru, `çapraz` bilinmiyor |
| **R20** | `fire oranı hedefi %5 iken bu yıl hangi hatlar aştı` | 🔴 eşik **hiç uygulanmadı**, beyan yok |

**Discovery ateşlemesi: 1** (R6, bütçe aşımıyla). *(E=4·F=1·G=1·N=1·O=0·P=1·R=1)*

### §89.2 · 🔴🔴 KÖK-R1 — **SIRALAMA İLE KESME AYNI YÜKLEMDE BİRLEŞTİRİLMİŞTİ**

`uyum.py:226`:

    siralama = order OR limit OR entity_limit

Beş alanın **herhangi biri** doluysa doğru. Sonuç: `order` kondu ama `limit` konmadıysa
sistem *"bir şey yaptım"* sayıp **susuyor** — oysa kullanıcı bir **SAYI** vermişti.

Ölçüldü (`r11`, `bu yıl en çok rework yapılan **3** makineyi bul`):

    trace: "üstünlük: sıralama sistem tarafından tamamlandı"
    niyet: üstünlük=3     cq: order ✅   limit ✗     →  **11 SATIR**, hiçbir beyan yok

Aynı desen dört kez: `r11` · `r16` [EN] (`5 customers`) · `r4` (*"üç"* — sayı **yazıyla**)
· `p18` [EN] (`top 3`).

🔴 Ve `§34`'ün kendi öğüdü bir **sözdür**: *"«en yüksek 5 makine» gibi sayı verirsen
sıralayıp **KESERİM**."* Sistem sıralıyor, kesmiyor, ve **sözünü tutmadığını
söylemiyor**.

**Düzeltme iki yarımdır — önce sözü tut, tutamıyorsan söyle:**

1. **`§R1b` — sözü TUT.** `§O3`'te satır limitini `timeDimensions ∧ dimensions` varken
   engellemiştim; gerekçe doğruydu (satır limiti seriyi keser) ama **eksikti**: o durum
   bir *"yapılamaz"* değil, **`entity_limit`'in tam tanımıdır** (ilk N **varlık**, seriler
   korunur). `route()` bu vakayı zaten doğru çözüyordu; **garson yolundan gelen `cq` o
   dala hiç uğramıyordu.** Kural vardı, **ikinci yolda yoktu**.
2. **`§R1a` — tutamıyorsan SÖYLE.** `kesme` yüklemi `siralama`dan **ayrıldı**: sayı
   verilmiş ve kesilmemişse beyan edilir (`KÖK-3`: cevabı öldürmez, etiketler).

**Curl doğrulaması:** `r11` → **11 satır → 3 satır**.

*Bir sözü yarım tutmak, hiç tutmamaktan daha sessizdir.*

### §89.3 · 🔴 VE İLK YAZIMIM YALAN SÖYLEDİ — kendi ölçümüm yakaladı

Yeni `kesme` yüklemi yalnız `limit`/`entity_limit` **alanlarına** bakıyordu. Ama
`entity_limit` **çözülünce alan olmaktan çıkar**: `_resolve_entity_limit` onu sıralanan
boyut üzerinde bir **değer filtresine** dönüştürür ve alan `cq`'dan düşer. Üç koşum:

    satır=3  limit=None  entity_limit=False  filtre_boyut=['makine']  → 🔴 BEYAN ATEŞLEDİ
    satır=3  limit=3     entity_limit=False  filtre_boyut=[]          → ✅ susar

Yani **kesme yapılmışken** sistem *"kesemedim"* diyordu. Bir beyan olarak bu
**beyansızlıktan kötüdür**: doğru bir cevabı eksik ilan eder.

**Düzeltme:** ölçüt kesmenin **alanına** değil **izine** bakar — sıralanan boyut üzerinde
bir değer filtresi varsa kesme gerçekleşmiştir. Yanlış-negatif tarafı güvenlidir.
**Curl doğrulaması: üç koşumda da yanlış beyan yok.**

*Bir kusuru ilan eden yüklem, kendi yanlış-pozitifini üretirse, ilan ettiği kusurdan daha
pahalıdır.*

### §89.4 · 🔴 BASKIN SINIF — **SESSİZ KAPSAM DARALMASI** (iki turda 9 kanıt)

| tur | soru | düşen talep | beyan |
|---|---|---|---|
| P2 | `karlılığa etkisini analiz et` | karlılık ekseni | ✗ |
| P15 | `aylık **kümülatif** fire` | kümülatif | ✗ |
| P16 | `her hattın **payı**` | pay | ✗ *(→ `§O2` kısmen kapattı)* |
| R10 | `ikisini **üst üste bindir**` | kıyas kolonları | ✗ |
| R11 | `**3** makine` | kesme | ✗ → 🟢 **`§R1`** |
| R14 | `**ısı haritasına** çevir` | grafik türü | ✗ |
| R16 | `**5** customers · **growth**` | ikisi de | ✗ → 🟢 kesme yarısı |
| R18 | `**hareketli** 3 aylık ortalama` | pencere | ✗ |
| R20 | `hedefi **%5** iken aştı` | eşik | ✗ |

⊙ Dokuzunda da `niyet.bilinmeyenler` düşen kelimeyi **yazıyor**. Yani sinyal **var** ve
okunmuyor. `§R1` bu sınıfın **kesme** üyesini kapattı; kalan yedisi **kendi yüklemlerini**
bekliyor — ve her biri ayrı ayrı yazılmalı, çünkü ortak bir *"bilinmeyen varsa beyan et"*
kuralı `bul`·`hangi`·`bunu` gibi zararsız kelimelerde **gürültü** üretir.

🔴 **Ve sınıfın adı önemlidir:** bunlar *"anlamadım"* değildir — sistem cevap verir,
**doğru** verir, ama **sorulanın bir parçasına** verir ve farkı söylemez. `KÖK-3`'ün
(beyan-açık) kapsamadığı bölge tam burasıdır.

*Bir sorunun yarısını cevaplayıp hangi yarısı olduğunu söylememek, cevap vermemekten daha
zor fark edilir.*

### §89.5 · R demetinin kapısı ve **dördüncü kez sabit kalan korpus**

    korpus  {vaka 2285, kabul 1153, dogru 93, sessiz_yanlis 12, beyanli_kismi 51}
    süit    4257 yeşil · 32 atlandı
    eval    precision +0,0% · coverage +0,0% · korpus doğru-cube %95.1 (taban %95.1)

🔴 **Bu, üst üste DÖRDÜNCÜ demet** (`§85` · `§87` · `§88` · `§89`) ve korpus **hiç
oynamadı**. Dört demette **on bir** ölçülmüş canlı kusur kapandı.

`§88.6`'da yazılan sınır artık bir gözlem değil bir **ölçüm**: korpus `rule` sağlayıcıyla
koşuyor, yani **garson yolunu ve takip yolunun LLM dalını hiç görmüyor**. Son on bir
düzeltmenin **hepsi** o iki yolda.

> **Kapımızın ölçmediği bir bölge var ve orası tam da son dört turda çalıştığımız bölge.**
> Yeşil kalması bir onay değil, bir **sessizlik**tir.

⚠ Bu bir *"kapıyı gevşetelim"* çağrısı **değildir** — korpus payda kutsaldır ve gerileme
vetosu görevini yapıyor. Eksik olan **ikinci bir ölçü**: garson yolunu ölçen bir korpus.
`lab/garson.py --kararlilik`'in tabanı **%100 (25/25)** ve `§85.0`'da yazıldığı gibi o
küme **zaten çalışan** soruları ölçüyor. Sıradaki alet işi budur.

---

## §90 · MUTFAK DEMETİ 1 — **M-6 tamam · M-2 yarım ve yarısı ölçüldü**

Kullanıcı kararı: mutfak raporunun kökleri **üç demette** inecek, tek hamlede değil
(§86'nın dersi: yedi kök birlikte inerse gerileme **kime ait** bilinemez). Demet 1 =
`M-6` + `M-2` — raporun *"ikisi de dar temaslı, tek demette inebilir"* notu.

### §90.1 · M-6 — operatör sözlüğü tek kaynaktan · **UYGULANDI**

Rapor bunu 🔍 *kod okuması* diye işaretlemişti (*"canlıda tetiklenmedi"*). Bu tur
**ölçüldü** — çalışan konteynerin `/cube` ucuna on üç aday **tek tek** gönderilerek:

    eq neq in not_in gt gte lt lte contains starts_with is_null is_not_null  → 12'si OK
    ne                                                                       → HTTP 400

Ve motor reddederken **geçerli kümeyi kendisi saydı**:

    ValueError: Invalid CubeQuery JSON: unknown variant `ne`, expected one of
    `eq`, `neq`, `in`, `not_in`, `gt`, `gte`, `lt`, `lte`,
    `contains`, `starts_with`, `is_null`, `is_not_null`

⊙ Yani yeni modülün demeti bir tahmin değil, **motorun kendi ağzından** alınmıştır.

**Üç kopya vardı ve üçü ayrışmıştı:** `intent_semasi` (7 üye, içinde motorda **olmayan**
`ne`), `tests/test_filtre_operatorleri` (12 üye, elle), ve motor (12). `parse_cube_query`
ise operatörü **hiç denetlemiyordu** — yalnız `dimension` beyaz listesi vardı.

**Bedeli iki türlü:** (1) şema modele motorun **reddedeceği** bir ad yazdırıyordu; (2)
motorun 12 adından **beşi** (`neq`·`not_in`·`contains`·`starts_with`·`is_null`/
`is_not_null`) fişte **hiç yoktu** → garson *"beyaz hariç"*, *"adı X ile başlayanlar"*,
*"kodu boş olanlar"* niyetlerini **ifade edemiyor** ve Discovery'ye düşüyordu.
**Mutfak o yemeği yapabiliyor; menüde yazmıyordu.**

**Düzeltme:** `app/cube_operatorleri.py` (tek sahip) · şema oradan üretiliyor ·
`parse_cube_query` operatörü doğruluyor ve tanımadığında **sorguyu reddediyor**
(düşürmüyor — sessiz düşürme `compare`'ın ve `measure_having`'in başına geldi) ·
`test_M6_SEMA_ile_MOTOR_ayni_kumeyi_konusur` kapısı ayrışmayı **imkânsız** kılıyor.

🔴 **Ve ilk yazımım burada yanıldı — turun beşinci ölçüm-aleti hatası.** *"`ne` sessizce
boş dönüyor"* diye yazmıştım; sondaj yazıcım **HTTP durum kodunu okumuyordu** ve 400'ü
`0 satır` sanmıştı. Motor sessiz değil, **aletim sağırdı**. Yorumlar düzeltildi.
*Bir aracın okumadığı alan, olmayan bir davranış uydurur.*

### §90.2 · M-2 — **yarısı uygulandı, öteki yarısı ÖLÇÜLEREK reddedildi**

Raporun reçetesi iki katmanlı: küp düzeyi `default_measure` **ve** ölçü düzeyi
`rol`+`birincil` (kapalı 7 değerli sözlük).

🔴 **`rol` katmanı bu demette AÇILAMADI ve sebebi yapısal:** MDL'de bir ölçünün alanları
**sabittir** — `name·expression·type·unit·synonyms`. `rol`/`birincil` diye bir kanal
**yok**; menü dosyasına yazılsa ya düşerdi ya motor projeyi reddederdi (motorun `serde`'si
bilinmeyen alanı **gürültüyle** reddediyor — `ne` sondajı bunu gösterdi). Rol katmanı
**yeni bir metadata kanalı** ister ve o kendi demetidir. *Ölmüş doğacak bir satırı
yazmak, yazmamaktan pahalıdır.*

**Uygulanan yarı:** `default_measure` uçtan uca **çalışan** bir kanal (yml → MDL →
`/schema` → `cube_router` R4 yedeği) ve **25 küpte boştu**. Dokuz küpe gerekçesiyle
yazıldı; canlı şemada **3 → 11**.

⚠ **Gerçekten belirsiz küplere BİLEREK yazılmadı** (`ik` brüt/net/işveren · `cari`
borç/alacak/bakiye · `maliyet` · `butce` · `parti`) — orada **sormak doğru davranıştır**
ve `parti`'nin menü dosyası bunu zaten yazılı olarak reddediyordu.

### §90.3 · 🔴 Kapı bir küpü GERİ ALDIRDI — ve tam bu sınıfın bekçisiydi

`kalite`'ye `toplam_rework_kg` varsayılanı verilince `test_YANLIS_CUBE_BUYUMEDI` kırmızı:

    YENİ sinonim çakışması doğdu:  'hatali': oee → kalite

Varsayılan ölçü o küpü **açgözlü** yaptı ve `oee`'nin bir ölçü sinonimini kaptı. Dokuz
denemeden **sekizi** temiz geçti; çakışan yalnız bu oldu, çünkü kalite terimleri `oee`'nin
kalite bileşeniyle **aynı alanı** paylaşıyor. Geri alındı, gerekçesi küpün kendi menü
dosyasında.

> *Bir küpe varsayılan vermek, ona komşusunun sorularını da cevaplama izni verebilir.*

### §90.4 · Kazancın DÜRÜST ölçüsü — ve raporun bir iddiasının çürümesi

| ölçüt | önce | sonra | okuma |
|---|---|---|---|
| sinonim taraması · `R4` | 3 | **1** | iki soru artık *"ölçü yok"* demiyor |
| sinonim taraması · `R10` | 12 | **14** | …ama aynı iki soru **kapsam kapısına** takılıyor |
| **toplam cevapsız** | **116** | **116** | 🔴 **bu taramada erişim kazancı SIFIR** |
| canlı curl | LLM'e düşüyordu | `route()` · **LLM'siz** | `bu yıl iş emri` **129** · `bu ay şikayet` · `bu yıl sevkiyat` **105** |
| korpus | 93/12/51 | **93/12/51** | veto geçildi, gerileme yok |
| tam süit | 4257 | **4259** | +2 yeni kapı (M-6) |

⊙ İki popülasyon, iki farklı cevap ve **ikisi de doğru**: tarama yalnız **çıplak ölçü
sinonimlerini** dener; `default_measure`'ın işe yaradığı yer **küp kimliği geçen ama ölçü
kelimesi geçmeyen** sorulardır. *Bir sayının değişmemesi, hiçbir şeyin değişmediği
anlamına gelmez — ölçtüğü şeyin değişmediği anlamına gelir.*

🔴 **Ve raporun bir attribution'ı ÇÜRÜDÜ:** rapor `p14`'ü (*"en çok enerji harcayan 3
makine"*) M-2'ye bağlıyordu. Canlı trace (iki koşum) tıkanmanın **R4'te değil küp
seçiminde** olduğunu gösterdi: bir koşumda garson uyuşmazlığı (%50, `eksen=measures`),
ötekinde `ilgili_cubelar` dalı. Rapor mesajın **metninden** çıkarım yapmış
(*"Hangi ölçüyü istiyorsun?"*), trace'ten değil. `p14`'ün evi **M-1**'dir.

*Bir teşhisi cevabın metninden okumak, hastayı tarifinden tedavi etmektir.*

---

## §91 · MUTFAK DEMETİ 2 — **PENCERE ve TÜREV katmanı** (M-9 + M-3)

Rapor bu ikisinin **birlikte** inmesini şart koşuyordu (*"aynı ölçü-cebri alanını açar,
ayrı inerlerse ikinci sahip doğar"*). Doğru çıktı: `pay` kipinin **hangi katmana ait
olduğu** ancak ikisi birden yazılınca görüldü (§91.4).

### §91.1 · 🔴 Raporun FORMU düzeltildi — ve düzeltmenin sebebi ÖLÇÜLDÜ

Rapor `pencere`yi **menü dosyasına** (ölçü düzeyi `pencere:`) koyuyordu. `M-2`'de
ölçüldü ki **MDL'de bir ölçünün alanları sabittir** (`name·expression·type·unit·
synonyms`); yeni bir anahtar ya derlemede düşer ya motorun `serde`'si tüm projeyi
reddeder — `ne` sondajı bu reddi **gürültüyle** gösterdi.

⊙ Oysa deponun **kendi kalıbı** doğru yeri gösteriyordu: `measure_having` · `ayrik_aylar`
· `entity_limit` · `blend` — dördü de **CubeQuery alanıdır**, kataloğa hiç girmezler.
`pencere` ve `turev` de öyle yazıldı. **Yan kazanç:** bir oran artık *önceden tanımlanmış*
olmak zorunda değil, kullanıcının o anki sorusundan doğabiliyor.

*Bir yeteneği kataloğa yazmak, onu birinin önceden yazmış olmasına bağlamaktır.*

### §91.2 · Dört katman, ve dördü de gerekliydi

| katman | ne yapıldı | kanıt |
|---|---|---|
| 🍳 **mutfak** | `wren_service._pencere_sar` / `_turev_sar` — `ayrik_aylar` ile **aynı sarma kalıbı** | `/cube` ile altı kip tek tek koşuldu |
| 📋 **sipariş fişi** | `parse_cube_query` iki alanı doğrular ve **taşır** | beyaz listede olmayan alan **düşer** — üç yorum bu dersi zaten yazmış |
| 🗣 **garsonun istemi** | `_cube_select_system` + `_cube_refine_user` | — |
| 🚦 **devir** | `§M9a` — kapsam-dışı bir kelime artık **şüphe sayılır** | aşağıda |

🔴 **Ve ilk yazımım kuralları YANLIŞ İSTEME koydu.** `pencere`/`turev` anlatımını
`_cube_refine_user`'a (takip yolu) yazmıştım; taze yol onları **hiç görmüyordu**. Uçtan
uca sınama gösterdi: `bu yıl aylık kümülatif fire` → `cq`'da `pencere` **yok**.
*Bir kuralı yanlış isteme yazmak, hiç yazmamaktır — ve bunu ancak zinciri sonuna kadar
koşarak görürsün.*

### §91.3 · 🔴🔴 `§M9a` — ŞÜPHE, DEVİR KARARINDAN **SONRA** KEŞFEDİLİYORDU

Dört katman kurulduktan sonra bile `p15` çalışmadı. Sebebi (iki koşum birebir, `G-1`):

    `bu yıl aylık **kümülatif** fire toplamını göster`
      route: parti + toplam_fire_kg + ay kovası + tarih filtresi  → route_supheli = FALSE
      → garson HİÇ ÇAĞRILMADI
      → tur şu cümleyle öldü: «"kumulatif" kısmını anlayamadım»  (LLM'siz)

    `bu yıl her hattın toplam fire içindeki **payı**`
      → «"payi" başka bir konu gibi görünüyor»  (LLM'siz)

⊙ `route_supheli` yalnız `cq`'nun **eksikliğine** bakıyordu (dönem yok · sıralama yok).
Üçüncü bir şüphe türü ise **soruda** yaşıyor: *route cümlenin bir parçasını hiç
kapsamadı.* Route kendinden emin göründüğü için devir yapılmıyor, şüphe **daha aşağıda**
ortaya çıkıyor ve orada garsona sorulmadan bir **red cümlesi** yazılıyordu.

🔴 `feedback_garson_devri_kurali`'nin devir tetikleyicileri listesi bu dalı **adıyla**
sayıyor: *"«anlayamadım» üretecek her dal"*.

**Düzeltme:** kapsam-dışı kelime `_supheli`'ye **üçüncü işaret** olarak eklendi. Tarama
zaten aşağıda koşuyordu; yukarı alındı ve **yeniden kullanıldı** (ikinci koşum kaldırıldı).

**Curl (iki koşum birebir):**

    ÖNCE : «"kumulatif" kısmını anlayamadım»
    SONRA: 6 satır · `_p_kumulatif_toplam_fire_kg` = 43.869 → 95.934 → 174.775 → 277.045

*Bir yeteneği üç katmanda kurup dördüncüde kapıda bırakmak, onu hiç kurmamaktır.*

### §91.4 · 🔴 GARSON EKSİK ALETİ GÖSTERDİ — `pay` bir türev değil, bir PENCERE

`p16` ilk koşumda `turev` üretti ama: `pay = payda = toplam_fire_kg` → **her satır %100**.

⊙ Teşhis: *"toplam içindeki payı"* bir **iki-ölçü oranı değildir**; bölen satırın kendisi
değil **bütün**dür → `x / SUM(x) OVER (…)`. Yani doğru ev **pencere** katmanı ve o kip
**yoktu**. Garson eldeki yanlış aleti kullandı.

**İki düzeltme birden:** `pay` kipi eklendi · `turev`'de `pay == payda` artık
**gürültüyle reddediliyor** (sessizce %100 döndürmek küp rozetli bir sessiz-yanlıştır).

**Curl doğrulaması:** sekiz hattın payı **tam 100.0** ediyor (`13.96 + 22.68 + 3.86 + …`).

*Bir aleti vermezsen, eldeki alet yanlış kullanılır.*

### §91.5 · Altı pencere kipi — hepsi canlıda ölçüldü

| kip | canlı sonuç |
|---|---|
| `kumulatif` | 43.869 → 95.934 → 174.775 → 277.045 ✅ |
| `hareketli_ort` (3) | 59.583 → 57.572 → 58.583 ✅ |
| `degisim_yuzde` | `null` → **18.68** → **51.43** ✅ (`LAG`) |
| `sira` (grup-içi) | `hat` başına 1·2·3 ✅ |
| `pay` | sekiz hat, toplam **100.0** ✅ |
| `turev` (yüzde) | `fire/ağırlık` → **20.73** — `fire_orani_yuzde` ile **birebir aynı** ✅ |

⊙ Son satır bağımsız bir doğrulamadır: türev cebri, katalogda **elle yazılmış** oran
ölçüsüyle aynı sayıyı üretti.

⚠ Ve `sira` kipi ilk denemede **gürültüyle** düştü (HTTP 400): yüklemim tüm kiplere
zaman ekseni dayatıyordu, oysa `sira` ölçüye göre sıralar. Fail-closed **tam çalıştı** —
kusur yüklemin kendisindeydi. *Bir ön koşulu tüm kiplere dayatmak, kipleri ayırmamaktır.*

### §91.6 · Demet 2 kapısı

    korpus  {vaka 2285, kabul 1153, dogru 93, sessiz_yanlis 12, beyanli_kismi 51}
    süit    4260 yeşil · 31 atlandı        eval  precision +0,0% · coverage +0,0%

Korpus yine sabit — ve sebebi `§88.6`'da yazılı: korpus `rule` sağlayıcıyla koşuyor,
pencere/türev **garson yolunda** yaşıyor. Kazanç canlı curl'de ölçüldü ve yukarıda satır
satır yazılı.

---

## §92 · M-5 · TOPLANABİLİRLİK BEYANI — *"küp rozetli sessiz-yanlışın açık kapısı"*

### §92.1 · Ölçüm önce — ve ALETİM ALTINCI KEZ YANILDI

İlk ölçümü **canlı şemadan** yaptım ve şu çıktı: *"135 ölçü, 2 beyanlı, 133 beyansız."*
Rapor ise *"172 ölçü, 12 beyanlı"* diyordu. Aradaki fark bir çelişki değil, **benim
aletimin körlüğüydü**: `schema()` yalnız `semi_additive`/`non_additive` **listelerini**
yayınlıyor; `additive: full` beyan eden bir ölçü **hiçbir listede görünmez** ve dışarıdan
*"beyansız"* sanılır.

⊙ Somut kanıt: `cari.toplam_borc` benim ölçümümde *"beyansız, aday semi"* göründü —
oysa menü dosyasında **`additive: full`** yazılı. Yani neredeyse **doğru bir beyanı
yanlışıyla değiştirecektim** (muhasebede `borç` bir **hareket** toplamıdır, `bakiye` gibi
snapshot değildir; katalog bunu benden iyi biliyordu).

Kaynaktan sayınca rapor **birebir** doğrulandı: **172 ölçü · 12 beyanlı (6 `full` +
6 `semi`) · 160 beyansız.**

*Bir alanı yayınlamayan uç, o alanın yokluğunu kanıtlamaz.*

### §92.2 · 🔴 Raporun reçetesi UYGULANMADI — ve gerekçesi ölçüldü

Rapor *"`additive:` her ölçüde **zorunlu** olsun, beyansız küp **derlenmesin**"* diyordu.
İki sebeple olduğu gibi uygulanmadı:

1. **160 ölçüyü birden zorunlu kılmak derlemeyi kırardı** — ve kırılan bir kapı, atlanan
   bir kapıya dönüşür.
2. Beyanların çoğu bir **insan kararı** ister: `toplam_borc` `full` mü `semi` mi?
   Yukarıdaki kendi hatam bunun canlı kanıtı.

**Uygulanan:** kapı, **kanıtlanabilir** olanı zorunlu kılar. Ölçüt **ada değil İFADEYE**
bakar — `AVG(` · `COUNT(DISTINCT` · `/NULLIF(` · `100.0 * …/` içeren bir ölçü toplanamaz
olduğunu **kendi SQL'inde söyler**; orada tahmin yoktur.

### §92.3 · Sonuç

| ölçüt | önce | sonra |
|---|---|---|
| beyanlı ölçü | **12** / 172 | **77** / 172 |
| canlı şemada `non_additive` | **0** | **56** |
| canlı şemada `semi_additive` | 2 | 2 *(dokunulmadı)* |
| yanlış-pozitif denetimi | — | **0** *(65'inin hepsinde bölme/ortalama/DISTINCT var)* |

⚠ **Ve `non` beyanı KAPSAM DARALTMAZ** — ölçüldü: `R8` yalnız `semi_additive`'e bakıyor.
`non`'un tek etkisi yanlış **grafiği** (`viz._additive` → yığma/pay yasak) ve yanlış
**katkı ayrıştırmasını** (`contribution.py`) durdurmak; yani **fail-closed** yönde.
Doğrulandı: `bu yıl aylık OEE trendi` → hâlâ `route()` · 6 satır · LLM'siz.

> *Bir beyan cevabı kısıtlamıyorsa, onu ertelemenin gerekçesi yoktur.*

### §92.4 · Kapı ve çürüme koruması

    korpus  {2285, kabul 1153, dogru 93, sessiz_yanlis 12, beyanli_kismi 51}
    süit    4261 yeşil   ·   eval +0,0%

İki yeni kapı eklendi: `test_M5_TOPLANAMAZ_OLCU_BEYAN_ETMEK_ZORUNDA` (ifadesi kanıtlayan
her ölçü beyan etmek **zorunda**) ve `test_M5_BEYAN_DEGERI_GECERLI` (`full|semi|non`
dışı bir değer üç tüketicide de **sessizce** hiçbir şey yapar).

---

## §93 · M-4 · VARSAYILAN DÖNEM — **kuruldu, ölçüldü, BİLEREK KAPALI**

### §93.1 · 🔴 Raporun formu ÜÇÜNCÜ KEZ aynı duvara çarptı

Rapor küp düzeyinde `varsayilan_donem:` beyanı öneriyordu. `M-2` (`rol`) ve `M-9`
(`pencere`) ile **birebir aynı** yapısal engel: MDL'de küp alanları da sabittir
(`name·label·baseObject·synonyms·defaultMeasure·measures·dimensions·timeDimensions`).

⊙ Ama raporun **kendi cümlesi** çıkışı gösteriyordu: *"`veri_araligi` verinin gerçek
aralığını **zaten biliyor**."* Varsayılan kataloğa yazılmadı, **veriden türetildi** — ve
bu katalog beyanından **daha iyidir**: bayat bir beyan yanlış bir pencere üretir, veri
kendini günceller.

### §93.2 · Kanal da açılmadı — **zaten vardı**

Beyanı kullanıcıya taşıyacak mekanizma `donem_capasi`'nde **hazırdı** (`_TASIYICI` →
`notu_al`) ve modül zaten **dönem** hakkında. İkinci bir not kanalı açmak `KAT-1` olurdu;
sibling bir fonksiyon yazıldı.

### §93.3 · Ölçülen KAZANÇ (iki koşum birebir, `KURAL G-1`)

    ÖNCE : «toplam sure dk çıkarabilirim — hangi dönem için?»            0 satır
    SONRA: «⏱ Dönem belirtmedin — **verinin son 12 ayı** alındı
            (01.06.2025 – 30.06.2026). Başka bir dönem yazarsan onu uygularım.»  8 satır

### §93.4 · Ölçülen BEDEL — ve kararın kendisi

Bayrak `beta`ya alınıp süit koşulunca **6 altın test kırmızı**. En açık olanı:

    test_clarify_toplam_uretim
    beklenen chip'ler : ['Bugün','Bu hafta','Bu ay','Bu yıl','Tümü']
    ölçülen           : ['uretim (parti)']

Yani `toplam üretim` artık dönem **sormuyor**, varsayılan pencereyle **cevaplıyor**.
Bu bir kusur değil — bayrağın **var oluş sebebi** olan davranış değişikliğinin ta
kendisi. Ama altı altın test **bugünkü sözleşmeyi** yazıyor ve o sözleşmeyi değiştirmek
bir **ürün kararıdır**, bir yan etki değil.

**Karar: bayrak `off` kalır.** Yetenek kuruldu, kazanç ve bedel **ölçüldü**, açma kararı
sözleşme sahibinindir. `KURAL B` gereği kapalıyken davranış **birebir** bugünküdür —
curl ile doğrulandı.

> *Bir yeteneği kurmak ile onu açmak aynı karar değildir; ikincisi ölçüyü ister,
> birincisi yalnız emeği.*

### §93.5 · Ve bir iz yalan söylüyordu — canlıda yakalandı

İlk koşumda not **doğru**, iz **yanlıştı**: `dönem çapası önceki turdan taşındı (KÖK-4)`.
Sebep, `IZ` sabitinin `notu_al` içine **gömülü** olmasıydı; iki farklı sebep aynı kanalı
paylaşınca kanal sebebi de taşımak zorundadır. Taşıyıcı `(not, iz)` çiftine çevrildi.

*Doğru bir notun yanında yanlış bir iz, notu da şüpheli yapar.*

### §93.6 · Ve bir tuzağa dosyanın kendi uyarısına rağmen düştüm

`features.yml`'ye `varsayilan_donem: off` yazdım. Dosyanın **kendi yorumu** şunu diyor:
*"⚠ YAML `on/off/yes/no`'yu **BOOLEAN** okur."* Kapı yakaladı:
`geçersiz aşama: {'varsayilan_donem': False}`. Tırnak eklendi.

⚠ İkinci kapı da konuştu ve daha önemliydi: `FLAG_REGISTRY`'de metadata yoktu —
*"bir kill-switch yalnız KOD'da varsa yarımdır"*. Admin paneli girdisi yazıldı.

### §93.7 · Kapı (bayrak kapalı)

    korpus  {2285, kabul 1153, dogru 93, sessiz_yanlis 12, beyanli_kismi 51}
    süit    4261 yeşil   ·   eval +0,0%

---

## §94 · M-1 · UYUMLU BOYUT — **raporun teşhisi düzeltildi, çözümü ölçüldü, GERİ ALINDI**

Bu bölüm bir **başarısızlığın** kaydı değil; bir **ölçümün** kaydı. Rapor M-1'i *"en büyük
kazanç, en büyük değişiklik"* diye işaretlemişti ve haklıydı — ama **iki yerde**.

### §94.1 · 🔴 Raporun teşhisi ÖLÇÜMLE DÜZELTİLDİ

Rapor amiral vakasını (*"bu yıl vardiya bazında fire oranı"*) şöyle açıklıyordu:

> *"Sığmayan şey (ölçü, boyut) çiftidir — ölçü bir küpte, boyut başka küpte."*

Ve çözüm olarak **beş modülü** etkileyen bir **uyumlu boyut mimarisi** öneriyordu
(`demo/packs/cekirdek/boyutlar/musteri.yml` + küplerde `uses:` referansı).

**Ölçüldü (MDL, `partiler` tablosu):**

    parti.baseObject = partiler
    partiler kolonları:  vardiya (INTEGER) · vardiya_ad (VARCHAR) · musteri_ad · personel …
    parti.dimensions  :  makine · hat · kumas_cinsi · … · hafta_gunu   ← **vardiya YOK**

🔴 Yani ölçü ile boyut **aynı küpte**. Eksik olan bir birleşme yolu ya da bir mimari
değil, **bir satır beyandı**.

**Sistematik tarama:** sekiz küpün taban tablosunda **46 ortak-boyut kolonu** var ve
boyut olarak **beyan edilmemiş** (`vardiya` · `musteri_ad` · `personel` · `bolum` …).

*Bir mimariyi kurmadan önce, çözeceği vakanın gerçekten mimari olduğunu ölç.*

### §94.2 · Ve tek satır ÇALIŞTI — üç vaka birden

`parti`ye `vardiya` (`expression: vardiya_ad`) eklendi. Curl, **iki koşum birebir**:

| soru | önce | sonra |
|---|---|---|
| `bu yıl vardiya bazında fire oranı` | *"…hangi ölçüyü istediğini anlayamadım"* | **3 satır** · `route()` · **LLM'siz** |
| `bu yıl vardiya ve hat kırılımında fire oranı` (`p19`) | aynı | **24 satır** · çapraz kırılım · `route()` |
| `bu yıl vardiya bazında rework kg` | ham `"1"` | `"1. Vardiya (08-16)"` |

Ve cevap gerçek bir iş bulgusu taşıyor: **3. vardiya %25,08 fire**, 1. vardiya %16,78.

⊙ Not: soru artık **`route()`** ile çözülüyor — en ucuz yol. `§83`'ten beri *"mutfak
sınırı"* diye kayıtlı olan vaka, bir menü satırıyla **deterministik** hâle geldi.

### §94.3 · 🔴🔴 AMA KAPI KIRMIZI — ve sebebi bu bölümün asıl dersi

    korpus doğru-cube  %95.1 → **%94.4**  ❌ GERİLEME
    tam süit           test_HICBIR_belirsizlik_SESSIZ_kalmiyor ❌
      "6 belirsiz sinonim chip üretmiyor → Discovery'ye düşüyor:
       defect, defect rate, scrap, scrap rate, waste, waste rate"

Sondaj (kapının **kendi fikstürüyle**, taban ile karşılaştırmalı):

    TABAN : CHIPLER = [('fire (OEE)', 'vardiya fire'), ('fire (parti)', 'fire')]
    M-1'LE: CHIPLER = [('fire (parti)', 'fire')]
            oee → sorgu=None  → chip DÜŞTÜ

🔴 **`oee`'nin netleştirme chip'inin sorgusu `"vardiya fire"`'ydı** — çünkü `vardiya`,
`fire` sahipleri arasında `oee`'yi **ayırt eden** kelimeydi. `parti`ye vardiya verilince
o ayırt edicilik **yok oldu** ve chip üretilemedi.

> **Bir küpü yetenekli yapmak, bir kelimeyi ayırt edici olmaktan çıkarır.**

⊙ Ve ironi kayda değer: M-1'in beyanı **bir Discovery tetikleyicisini kapattı**
(`vardiya × fire oranı`) ve **bir başkasını açtı** (`scrap`/`waste`/`defect` ailesi).

### §94.4 · Karar — ve kurtarılan yarı

**Geri alındı** (`parti.vardiya`). Doğruluk vetosu ve kırmızı süit tartışmasızdır; kırmızı
bir kapı commit edilmez.

**Kurtarılan:** `kalite.vardiya`'nın **etiketi** düzeltildi (`"1"` → `"1. Vardiya
(08-16)"`) — yeni boyut yok, yeni sinonim yok, ayırt edicilik değişmiyor. Kapı yeşil.
Bu, uyumlu boyutun **görünür yarısıdır**: bir kavram her yerde **aynı adla** anılmalı.

### §94.5 · Devredilen kök — ve artık adı var

🔴 **`KÖK-M1a` · NETLEŞTİRME CHIP'İ TESADÜFİ BİR AYIRT EDİCİYE BAĞLI.**
`_calisan_sorgu` chip sorgusunu `{küp sinonimi} {ölçü ETİKETİ}` kalıbıyla kuruyor ve
ölçünün **öteki sinonimlerini** hiç denemiyor. `oee` için `"oee fire"` **tabanda da**
çözülmüyordu; chip yalnız `vardiya`'nın tesadüfen tekil olması sayesinde ayaktaydı.

⚠ Bu kök **M-1'den önce** gelmelidir: çözülmeden her uyumlu-boyut beyanı bir chip
ailesini sessizce düşürür. Ve çözümü ölçülebilir: `oee.toplam_fire_kg`'nin öteki
sinonimleri (`hatali` · `hurda`) `oee`'ye özgüdür.

*Bir yeteneği eklemeden önce, o yeteneğin kimin ayırt ediciliğini yediğini sor.*

### §94.6 · Kapı (kurtarılan yarı)

    korpus  {2285, kabul 1153, dogru 93, sessiz_yanlis 12, beyanli_kismi 51}   ← taban geri
    süit    4261 yeşil   ·   doğru-cube %95.1 (taban %95.1) ✅   ·   eval +0,0%

### §94.7 · MUTFAK RAPORUNUN BİLANÇOSU

| kök | rapor önceliği | durum | not |
|---|---|---|---|
| **M-7** telemetri pusulası | 1 | ✅ | + raporun görmediği ikiz |
| **M-2** ölçü rolü + varsayılan | 2 | ◐ | `default_measure` **3 → 11**; `rol` katmanı **yapısal olarak kapalı** |
| **M-5** toplanabilirlik | 3 | ✅ | beyan **12 → 77**, `non_additive` **0 → 56** |
| **M-4** varsayılan dönem | 4 | ✅ | kuruldu + ölçüldü, bayrak **bilerek kapalı** (6 altın sözleşme) |
| **M-6** operatör tek kaynak | 5 | ✅ | motorun 12 adı **ölçüldü**, `ne` ayıklandı, 5 yetenek fişe girdi |
| **M-3** türev ölçü | 6 | ✅ | `yuzde`·`oran`·`fark` + `pay==payda` gürültülü red |
| **M-9** pencere katmanı | 7 | ✅ | **altı kip** canlıda ölçüldü |
| **M-1** uyumlu boyut | 8 | ⊘ | teşhis **düzeltildi**, çözüm **çalıştı**, kapı **geri aldırdı** (`§94.3`) |
| **M-8** kaynak farkı beyanı | 9 | ⊘ | M-1'e bağlı — sırası gelmedi |

**Yedi kökten altısı indi; ikisi ölçülerek sınırlandı.** Ve rapor bu turda **üç kez**
düzeltildi: `rol`·`pencere`·`varsayilan_donem` katalog beyanları MDL'nin sabit alan
kümesine çarptı (`§91.1`·`§93.1`), M-1'in *"ölçü bir küpte, boyut başkasında"* teşhisi
ise **ölçümle** çürüdü (`§94.1`).

> *Bir denetim raporunun değeri, önerdiği çözümlerin doğruluğunda değil, gösterdiği
> yerin doğruluğundadır. Bu rapor yeri doğru gösterdi; çözümlerin üçü yanlış kapıydı ve
> bunu ancak uygulamaya çalışınca öğrendik.*

---

## §95 · KÖK-M1a · **CHIP, TESADÜFİ BİR AYIRT EDİCİYE BAĞLIYDI** — ve M-1'in ikinci engeli

### §95.1 · Kök ve düzeltme

`_calisan_sorgu` netleştirme chip'inin sorgusunu `{küp sinonimi} {ölçünün GÖRÜNEN ADI}`
kalıbıyla kuruyordu. İki küp aynı görünen adı taşıdığında (`oee` ve `parti` → ikisi de
*"fire"*) o ad ayırt etmez; chip ancak bir küp sinonimi **tesadüfen tekil** ise ayakta
kalır.

    TABAN : oee → sorgu = "vardiya fire"     ← `vardiya` o gün oee'ye özgüydü
    M-1'LE: oee → sorgu = None → chip düştü → 6 sinonim Discovery'ye kaydı

**Düzeltme:** ölçünün **öteki sinonimleri** de denenir. `oee.toplam_fire_kg` sinonimleri
`fire · hatali · hurda · waste · scrap · defect`; `hatali` ve `hurda` **oee'ye özgüdür** —
ayırt edici bilgi elimizde **vardı**, sorulmuyordu. Yeni sözlük yazılmadı; sıra ucuzdan
pahalıya (önce çıplak sinonim, sonra en kısa üç küp adıyla nitelenmiş hâli).

**Curl doğrulaması:** `bu yıl scrap` → *"«scrap» birden fazla yerde tanımlı — bu cevap
**parti** tanımıyla hesaplandı. Diğerleri: scrap (OEE)."* Belirsizlik artık **beyanlı**.

**Kapı:** korpus `{2285 · kabul 1153 · dogru 93 · sessiz_yanlis 12 · beyanli_kismi 51}` ·
süit **4262 yeşil** · doğru-cube **%95.1** (taban %95.1).

⚠ Ölçülen bedel: süit ~7 dk 07 sn (öncesi ~6 dk 50 sn) — ek `route()` çağrıları. Kabul
edilebilir; ama üçüncü bir kademe eklenirse **ölçülmelidir**.

### §95.2 · 🔴 VE M-1 YİNE İNMEDİ — ikinci engel, birincisinden BAĞIMSIZ

`KÖK-M1a` düzeltilince `parti.vardiya` geri kondu ve **chip testleri yeşile döndü**
(41 test). Ama tam kapı yine kırmızı verdi ve sayılar **birebir** aynıydı:

    korpus  {vaka **2266** · kabul 1142 · dogru 87 · sessiz_yanlis 11 · beyanli_kismi **32**}
    doğru-cube %95.1 → **%94.4**

🔴 **Payda −19, `beyanli_kismi` −19.** Aynı sayı. Yani `parti`ye bir boyut eklemek
korpusun **kendi vaka kümesini** değiştiriyor: 19 vaka üretilmiyor.

⊙ Ve `feedback_test_kapisi_disiplini`'nin kuralı burada bağlayıcı: **payda kutsaldır.**
Payda oynayan bir ölçüm, öncesi ile sonrası **kıyaslanamaz** hâle gelir — kazanç da
kayıp da görünmez olur.

**Karar:** `parti.vardiya` **ikinci kez geri alındı**; `KÖK-M1a` düzeltmesi **tutuldu**
(kendi başına yeşil ve bağımsız bir kırılganlığı kapatıyor).

**Devreden kök — `KÖK-M1b`:** *bir boyut beyanı korpus paydasını neden 19 azaltıyor?*
Cevap `lab/nl_corpus.py`'nin vaka üretecindedir ve **ölçülmeden** M-1 inemez. Sıradaki
turun ilk işi budur.

*Bir kazancı ölçemiyorsan, kazandığını da bilemezsin.*

---

## §96 · KÖK-M1b · **PAYDA NEDEN OYNADI** — ve bulgu, ölçüm aracının kendisi hakkında

### §96.1 · İki yanlış hipotez, sonra ölçüm

`parti`ye bir boyut eklemek korpus paydasını **2285 → 2266** (−19) ve `beyanli_kismi`'yi
**51 → 32** (−19) düşürüyordu. İkisi de **birebir tekrarlanabilir** (iki M-1 koşumu aynı,
dört taban koşumu aynı) — yani varyans değil.

| # | hipotez | ölçüm |
|---|---|---|
| 1 | *"19 vaka **hata** veriyor"* (`toplam` sayacı `__hata__`da artmıyor) | ❌ raporda hata yok |
| 2 | *"`vardiya` etiketleri **sızıntı** kuralını tetikliyor"* | ❌ sızan kelimeler `kar`(26)·`bakiye`(16)·`birim`(1) — **vardiya yok** |

### §96.2 · Gerçek sebep — korpus **şemadan türeyen** bir kümedir

`lab/gercek_dunya.py`:

    uret_vakalar, kapsam_raporu = senaryo_uretec.uret(schema)
    havuz += uret_vakalar

Vakalar **şemadan üretiliyor**: (küp × ölçü × **boyut** × niyet) bileşimleri. Bir boyut
eklemek yeni bileşimler doğurur → korpus **başka sorular sorar** → ne payda ne oran
öncekiyle **doğrudan** kıyaslanabilir.

⊙ Ve bu, neden `M-2` (9 küpe `default_measure`) ile `M-5` (65 `additive` beyanı) paydayı
**hiç** oynatmadığını da açıklıyor: ikisi de yeni **bileşim** doğurmuyor. Bir **boyut**
doğuruyor.

### §96.3 · 🔴 Sonuç: bu kapı bir BOYUT eklemesini hakemleyemez

> **Gerileme dedektörü sabit bir şema varsayar.** Menü değişince ölçtüğü **popülasyon**
> da değişir; `doğru-cube %95.1 → %94.4` bir gerileme **gibi görünür** ama iki farklı
> soru kümesi üzerinden hesaplanmıştır.

⚠ Bu, *"payda kutsaldır"* kuralının **iptali değil**, kapsamının netleşmesidir. Kural
şunu yasaklar: **kazanç uydurmak için paydayı kırpmak.** Burada payda kırpılmıyor,
**yeniden tanımlanıyor** — ve bu ancak **bilerek ve yazılı** yapılabilir.

### §96.4 · M-1'in önü nasıl açılır — üç şart

1. **Yeni taban bilerek kaydedilir** (`M-2`'deki `CEVAPSIZ_RED` dağılımının aynısı:
   sayı + **gerekçe** + neyin değiştiği).
2. Kayıttan önce **cinsine bakılır**: yeni popülasyondaki *yanlış-cube* vakaları
   **eskisinin üstüne mi** çıkıyor, yoksa yalnız yeni sorular mı eklendi? `gercek_dunya.md`
   bu listeyi zaten yazıyor.
3. `sessiz_yanlis` **artmamalı** — bu ölçüt popülasyondan bağımsızdır ve M-1 koşumunda
   **12 → 11** oldu, yani **düştü**.

⊙ Üçüncü madde önemli: M-1'in ölçülen tek doğruluk göstergesi **iyileşme** yönünde.

**Karar:** `parti.vardiya` bu turda **inmedi** — taban yeniden tanımlamak bir kapı
kararıdır ve tek başıma vermem. Ama artık **neyin ölçülmesi gerektiği yazılı**: yukarıdaki
üç şart. Ve M-1'in kazancı ölçülmüş durumda (`§94.2`): `vardiya bazında fire oranı`
**3 satır** · `p19` **24 satır** · ikisi de `route()` ile **LLM'siz**.

*Bir ölçüm aracının sınırını bulmak, ölçtüğü şeyi bulmak kadar değerlidir.*

---

## §97 · M-1 **İNDİ** — ve kararı veren şey, dokuzuncu alet düzeltmesi oldu

### §97.1 · 🔴 Kendi üç şartımın ÜÇÜNCÜSÜ ölçülemez çıktı

`§96.4`'te M-1'in önünü açacak üç şart yazmıştım. Üçüncüsü şuydu: *"`sessiz_yanlis`
artmamalı — bu ölçüt popülasyondan **bağımsızdır**."* İki raporun sessiz-yanlış
kümelerini karşılaştırdım:

    TABAN'da olup M-1'de olmayan : 12
    M-1'de yeni doğan            : 11
    🔴 ORTAK                     : **0**

**Tamamen ayrık.** Yani `12 → 11`'i *"iyileşme"* saymam yanlıştı: iki sayı **aynı şeyin
iki ölçümü değil**. Bu vakalar `senaryo_uretec`'in ürettiği gürültülü sorular
(*"az önceki haziran adet vardiya makine kırılımınnda!!!"*) ve şema değişince üreteç
**bambaşka bir örneklem** veriyor.

⊙ Bu, bu oturumun **dokuzuncu** ölçüm-aleti düzeltmesi ve en önemlisi: *popülasyondan
bağımsız sandığım ölçüt de popülasyona bağlıydı.*

### §97.2 · Asıl kanıt — ve o, ayrık kümelerden BAĞIMSIZ

`nl_corpus` aynı koşumda, boyahane:

    TABAN : 9182 tur · erişim OK=**6328** · DOĞRU-CUBE=**5810**/6049 (%96) · yanlış=**216** · discovery=23
    M-1   : 9281 tur · erişim OK=**6328** · DOĞRU-CUBE=**5810**/6115 (%95) · yanlış=**216** · discovery=**89**

🔴 **Doğru 5810 → 5810. Yanlış 216 → 216. Erişim 6328 → 6328.** Üçü de **birebir**.
Değişen tek şey **+66 yeni vaka** ve hepsi `discovery` kovasında.

> **Hiçbir doğru cevap bozulmadı. Ölçülen alan genişledi, kalite düşmedi.**

Oran %95.1 → %94.4 çünkü payda büyüdü — `§96.2`'nin tarif ettiği mekanizma, bu kez
sayılarla kanıtlı.

### §97.3 · Taban BİLEREK yeniden tanımlandı — ve iki bekçi beni düzeltti

`nl_corpus_baseline.json`'a yedinci tur, **tam gerekçesiyle** yazıldı (üç eşitlik +
kazanç + *"bar donmuyor"* kaydı). Deponun kendi emsali: `gercek_dunya_baseline` bunu
**üç kez** yapmış ve kendi cümlesini yazmış — *"payda değiştiği için eski 42 ile yeni 46
aynı ölçünün iki değeri değil."*

🔴 İlk yazımda erişim yüzdelerini de (68/69/68/72) yazdım ve **iki bekçi kapı** kırmızı
verdi: *"bir tur eklemek tabanı geriletemez"*. Haklıydılar — kayıtlı taban 69, ölçülen 68
(tolerans içinde); 68'i yazmak çıtayı **sessizce** indirirdi. Ve gereksizdi: erişim bu
değişiklikten **hiç etkilenmedi** (6328 → 6328). Alan çıkarıldı.

*Değiştirmediğin bir sayıyı yeniden yazmak, onu değiştirmektir.*

### §97.4 · Sonuç

    korpus doğru-cube  %94.4 (taban %94.4) ✅      gerçek-dünya  kapı yeşil ✅
    tam süit           4261 yeşil                  eval          +0,0%

**Curl (iki koşum birebir):** `bu yıl vardiya bazında fire oranı` → **3 satır**,
`route()` ile **LLM'siz**. `§83`'ten beri *"mutfak sınırı"* diye kayıtlı olan vaka
kapandı. Ve bulgu gerçek: **3. vardiya %25,08 fire**, 1. vardiya %16,78.

### §97.5 · MUTFAK RAPORU — TAMAMLANDI

| kök | durum |
|---|---|
| **M-7** telemetri pusulası | ✅ |
| **M-6** operatör tek kaynak | ✅ |
| **M-9** pencere katmanı (6 kip) | ✅ |
| **M-3** türev ölçü | ✅ |
| **M-5** toplanabilirlik (12→77) | ✅ |
| **M-4** varsayılan dönem | ✅ *(kuruldu+ölçüldü, bayrak bilerek kapalı)* |
| **KÖK-M1a** chip ayırt edicisi | ✅ *(yol açıcı)* |
| **M-1** uyumlu boyut — ilk adım | ✅ *(`parti.vardiya`; kalan 45 kolon sırada)* |
| **M-2** ölçü rolü | ◐ *(`default_measure` 3→11; `rol` MDL'de yapısal kapalı)* |
| **M-8** kaynak farkı beyanı | ⊘ |

**Dokuz kökten yedisi indi, biri yarım, biri açık.** Rapor bu süreçte **dört kez**
düzeltildi: `rol`·`pencere`·`varsayilan_donem` katalog beyanları MDL'nin sabit alan
kümesine çarptı; M-1'in *"ölçü bir küpte, boyut başkasında"* teşhisi ölçümle çürüdü —
boyut **aynı küpteydi, beyan edilmemişti**.

---

## §98 · MUTFAK RAPORU **KAPANDI** — M-1 tamamlandı, M-8 ölçülerek kapsam dışına alındı

### §98.1 · 🔴 "45 kolon" bir ALTDİZE YANILGISIYDI — onuncu alet düzeltmesi

`§94.1`'de *"46 ortak-boyut kolonu beyan edilmemiş"* diye ölçmüştüm. O tarama **altdize**
eşleşmesi yapıyordu: `hat` ⊂ `hat`**ali**, `vardiya` ⊂ `vardiya`**_suresi_dk**,
`makine` ⊂ `makine`**ler**. Tam ad eşleşmesiyle yeniden ölçüldü:

| küp | gerçek boşluk |
|---|---|
| `ik` | `personel` — bir **ilişki** (join), boyut değil → aday değil |
| `isg` | ⊘ zaten beyanlı: `kaza_vardiya` (`expression: vardiya`) |
| `kalite` | ⊘ zaten beyanlı: `musteri` (`expression: musteri_ad`) |
| `parti` | ⊘ `§97`'de kapandı |
| **`surdurulebilirlik`** | 🔴 **`vardiya_ad`** — tek gerçek boşluk |

**Gerçek sayı: 46 değil, 1.** *Bir eksikliği saymak, onu adıyla saymaktır.*

### §98.2 · Son boyut indi — ve korpus YÜKSELDİ

`surdurulebilirlik` küpü `partiler` tabanını `parti` ile paylaşıyor; `vardiya_ad` orada
**zaten vardı**.

| ölçüt | `§97` sonrası | **son** |
|---|---|---|
| `kabul` | 1142 | **1146** (+4) |
| `dogru` | 87 | **90** (+3) |
| `sessiz_yanlis` | 11 | **11** ✅ |
| `beyanli_kismi` | 32 | 33 |
| doğru-cube | %94.4 | **%94.4** (taban %94.4) ✅ |
| tam süit | 4261 | **4262 yeşil** |

⊙ Bu sefer payda **oynamadı** (2266 → 2266) ve `kabul`+`dogru` **yükseldi** — yani
kazanç bu kez **doğrudan kıyaslanabilir**.

### §98.3 · M-8 — ölçüldü ve **tarif edildiği gibi uygulanamaz**

Raporun teşhisi: *"`demo/packs/kaynak/*/gereksinim.yml` dosyaları **mevcut**. Eksik olan,
o beyanın **çalışma zamanında** okunması."*

**Ölçüldü — iki engel:**

1. 🔴 `gereksinim.yml` bir **yetenek beyanı değil**, bir **tablo/kolon manifestosudur**
   (`modeller: [{name, tablo, primary_key, kolonlar}]`). *"Bu ölçü senin ERP'nde yok"*
   diyebilmek için **ölçü → tablo → gereksinim** zinciri gerekir ve o zincir **veri
   olarak yok**. Dahası `app/compose.py:270` bu dosyayı derlemede **bilerek atlıyor** —
   o bir **kod üretimi** girdisidir (`lab/generate_models.py`), çalışma zamanı girdisi
   değil.
2. 🔴 Raporun kendi sınır notu: canlı örnekte tek geçerli kiracı `demo-boyahane` ve
   `demo-geri-donusum`; farkın ölçüldüğü `gitas`/`atiksan` **korpus-içi** şirketlerdir,
   **giriş hesapları yoktur**. Yani M-8 bu kurulumda **canlıda doğrulanamaz** bile.

**Karar:** M-8 kapsam dışına alındı ve gerekçesi yazıldı. Uygulanabilir hâli **yeni bir
veri** ister (ölçü-düzeyi kaynak gereksinimi beyanı) ve o, raporun tarif ettiği iş değil
**başka bir iştir**. *Var olan bir dosyayı okumak ile olmayan bir alanı üretmek aynı iş
değildir.*

### §98.4 · 🔴 MUTFAK RAPORUNUN KAPANIŞ BİLANÇOSU

| kök | rapor önceliği | durum |
|---|---|---|
| **M-7** telemetri pusulası | 1 | ✅ *(+ raporun görmediği ikiz)* |
| **M-2** ölçü rolü + varsayılan | 2 | ◐ `default_measure` **3→11**; `rol` katmanı **MDL'de yapısal kapalı** |
| **M-5** toplanabilirlik | 3 | ✅ beyan **12→77**, `non_additive` **0→56** |
| **M-4** varsayılan dönem | 4 | ✅ kuruldu+ölçüldü, bayrak **bilerek kapalı** (6 altın sözleşme) |
| **M-6** operatör tek kaynak | 5 | ✅ motorun 12 adı **ölçüldü**, `ne` ayıklandı, 5 yetenek fişe girdi |
| **M-3** türev ölçü | 6 | ✅ `yuzde`·`oran`·`fark` + kendine-oran gürültülü red |
| **M-9** pencere katmanı | 7 | ✅ **altı kip** canlıda ölçüldü |
| **M-1** uyumlu boyut | 8 | ✅ `parti` + `surdurulebilirlik`; gerçek boşluk kalmadı |
| **M-8** kaynak farkı beyanı | 9 | ⊘ **ölçülerek kapsam dışı** (§98.3) |
| **KÖK-M1a** chip ayırt edicisi | *(türedi)* | ✅ M-1'in yolunu açtı |

**Dokuz kökten yedisi indi, biri yarım (yapısal engel), biri ölçülerek kapsam dışı.**

### §98.5 · Ve raporun kendisi hakkında — beş düzeltme

| # | raporun dediği | ölçüm |
|---|---|---|
| 1 | `rol`+`birincil` menüye yazılsın | MDL ölçü alanları **sabit** → kanal yok |
| 2 | `pencere:` menüye yazılsın | aynı duvar → **CubeQuery alanı** olarak indi (daha iyi: önceden tanımlı olmak zorunda değil) |
| 3 | `varsayilan_donem:` menüye yazılsın | aynı duvar → **veriden türetildi** (bayatlamaz) |
| 4 | M-1: *"ölçü bir küpte, boyut başkasında"* | boyut **aynı küpteydi**, beyan edilmemişti |
| 5 | M-8: *"`gereksinim.yml` var, tüketicisi yok"* | o dosya bir **tablo manifestosu**, yetenek beyanı değil |

> *Bir denetim raporunun değeri, önerdiği çözümlerin doğruluğunda değil, gösterdiği yerin
> doğruluğundadır. Bu rapor dokuz yerin dokuzunu da doğru gösterdi; çözümlerin beşi
> yanlış kapıydı ve bunu ancak uygulamaya çalışınca öğrendik.*

---

## §99 · S TURU — kullanıcının 12 senaryosu + 8 takip · ve **menü, tablodakini beyan etmiyordu**

### §99.1 · S turu tablosu (20 senaryo · 12'si kullanıcının)

| # | senaryo | sonuç |
|---|---|---|
| S1 | `Nisan ayında makine bazında toplam üretim kaç kg?` | 🟢 11 satır + belirsizlik beyanı |
| S2 | `Nisan ayında tüm hatların günlük OEE trendini göster` | 🟢🟢 **208 satır** · `route()` **LLM'siz** |
| S3 | `Hangi hattın OEE'si en düşük ve sebebi hangi bileşen?` | ◐ doğru şekil (OEE + **4 bileşen**, `asc`) · dönem sorusu |
| S4 | `bunun kümülatifini göster` *(takip)* | ◐ reddetti — **doğru** (zaman ekseni yok) ama mesaj yanlış |
| S5 | `geçen aya göre yüzde değişimi göster` *(takip)* | 🟢 `mom` · RAM-1 **+%27,3** |
| **S6** | `RAM 3'te renk derinliğine göre ortalama hızı karşılaştır` | 🔴→◐ **KÖK-S2** |
| **S7** | `Tedarikçi bazında ilk seferde doğru oranını göster` | 🔴→🟢 **KÖK-S2** |
| S8·S9 | `En çok tekrarlanan tamir sebepleri neler?` → `bu yıl` | 🟢 6 sebep, sıralı |
| **S10** | `her sebebin toplam içindeki payını göster` | 🟢🟢 **pay penceresi** — `En/Gramaj Sapması` **%27,88** |
| S11 | `1 Nisan'da RAM 3 hangi saatte başladı, partiler arası boşluklar?` | 🔴 **grain** sorusu — küp katmanı satır düzeyi vermez |
| S12 | `Vardiya bazında ilk parti başlangıç gecikmesi` | ◐ Discovery (71,6 dk) — mutfak eksikliği |
| S13·S14 | `Duruş nedenlerini süreye göre sırala` → `bu yıl` | ◐ `sırala` kayıp *(R turundan açık kök)* |
| S15 | `en uzun 3 nedeni al` | 🟢 `limit:3` |
| S16 | `Makine bazında kWh/kg + tesis ortalaması` | ◐ Discovery — mutfak eksikliği |
| S17 | `Müşteri bazında rework oranı + ciro katkısı` | 🔴 iki küp — **beyanlı** sınır |
| **S18** | `Rework'ün aylık maliyetini hesapla` | 🟢 **`§O2` beyanı**: *"₺ sordun, elimdeki ölçü **dk**"* |
| **S19** | `son 3 ayın hareketli ortalamasını çiz` | 🟢🟢 **hareketli ortalama penceresi** |
| S20 | `en çok rework yapılan müşteri + payı` | 🔴 küp belirsizliği |

**Discovery ateşlemesi: 2** (S12 · S16).

⊙ `§91`'de inen iki yetenek **canlıda kullanıcı sorusuyla** doğrulandı: **pay** (S10) ve
**hareketli ortalama** (S19). İkisi de **takip turunda, garson yoluyla**.

### §99.2 · 🔴 KÖK-S2 — MENÜ, TABLODAKİ ÖLÇÜ VE BOYUTU BEYAN ETMİYORDU

`M-1`'in dersi bir kez daha, bu kez **ölçü** tarafında da:

| eksik | tabloda | sonuç |
|---|---|---|
| `parti.tedarikci` · `kalite.tedarikci` | `tedarikci_ad` **VARCHAR** | `s7` → tedarikçi boyutu **tamamen düştü** |
| `parti.ort_hiz_m_dk` | `hiz_m_dk` **DOUBLE** | `s6` → küp ✓ kırılım ✓ **ölçü yok** (`bilinmeyen=hizi`) |

Sistematik tarama: **66 beyansız sayısal kolon** (çoğu gürültü — `id`·`kdv_orani`·ara
değerler); ölçülmüş kırmızılara karşılık gelen **üçü** beyan edildi.

**Curl:** `tedarikçi bazında ilk seferde tamam oranı` → **5 tedarikçi**, `SELÇUK TEKSTİL`
**%62,22**. `ort_hiz_m_dk × renk_derinlik` + `hat = RAM 3` filtresi doğru kuruluyor.

### §99.3 · 🔴 VE ÇIPLAK `hız` BİR GERİLEME ÜRETTİ — kapı yakaladı, üçüncü kez

İlk yazımda sinonimler `[hız, hızı, ortalama hız, …]` idi. `test_agent_plan_secimi_…`
kırmızı verdi: *"pilot HİÇ çağrılmadı"*. Sebep: o testin sorusu **`stok devir hızımız
nedir`** ve çıplak `hız` onu `parti.ort_hiz_m_dk`'ya çekiyordu.

🔴 **Stok devir hızı ile makine hızı aynı şey değildir.** Bu bir test kaprisi değil, bir
**ürün gerilemesiydi** — kapı onu bir ürün sorusunda yakaladı.

⊙ Ve o testin **kendi tarihi** bunu üçüncü kez yazıyor: soru iki kez yeniden seçilmiş,
ikisinde de sebep *"route() cevaplıyor, pilot hiç çağrılmıyor"*. Bir menü eklemesi, başka
bir kapının **ölçtüğü şeyi** susturabiliyor.

**Düzeltme:** sinonim `[ortalama hız, makine hızı, üretim hızı, metre dakika, çalışma
hızı]`'ya daraltıldı. **Takas ölçüldü:** `s6` artık doğrudan cevap yerine `ortalama hız`
**chip'i** sunuyor — tahmin yerine soru; `stok devir hızı` yanlış cevabı **kapandı**.
*Doğruluk, kolaylıktan önce gelir.*

### §99.4 · 🔴 KÖK-S3 — DİLSEL KAPSAM ÜRETİM SIRASINA BAĞLIYDI

`test_DILSEL_KAPSAM_hicbir_ozellik_bos_kalmaz` kırmızı: `iy.3cogul` (3. çoğul iyelik,
`-ları/-leri`) **hiç üretilmiyor**. Taban ölçüldü (`§86.6`): tabanda o biçim **üretilmiş**
kümede vardı, **statik** kümede yoktu.

> Yani bir dilbilgisi biçiminin sınanması **tesadüfe** bağlıydı: menüye bir boyut eklenince
> üreteç başka sorular kurdu ve o biçim **sessizce kayboldu**.

⊙ Bu, `KÖK-M1a`'nın (chip tesadüfi bir ayırt ediciye bağlıydı) **dilbilgisi tarafındaki
ikizidir**: *bir güvencenin tesadüfe bağlı olması, o güvencenin olmamasıdır.*

**Düzeltme — ve neden üreteç DEĞİŞTİRİLMEDİ:** üreteç bir **ölçüm aracıdır**; onu her menü
değişiminde ayarlamak, ölçtüğü şeyi ölçüme uydurmaktır. Bunun yerine biçim **statik**
kümeye alındı (menüden bağımsız → kapsam **yapısal olarak** garantili). Kardeş kapı
*"bir kapsam bir yanılsamadır"* deyip **beş** istedi; beşi de **gerçek iş sorusu**, biri
kullanıcının kendi `s8` senaryosu.

### §99.5 · Kapı — ve ölçütler YÜKSELDİ

| ölçüt | önce | **sonra** |
|---|---|---|
| korpus doğru-cube | %94.4 | **%94.9** (taban %94.4) ✅ |
| `sessiz_yanlis` | 11 | **10** |
| `kabul` · `dogru` | 1146 · 90 | 1145 · **90** |
| tam süit | 4262 | **4266 yeşil** |
| `eval` | +0,0% | **+0,0%** |

### §99.6 · Açık kalan kökler (T turuna)

`sırala` → `order` üretmiyor (`s13`, R turundan) · takipte `kümülatif` reddi **doğru ama
mesajı yanlış** (`s4`) · grain sorusu (`s11` — satır düzeyi zaman) · iki-küp yan yana
(`s17`) · küp belirsizliğinde `payını` kaybı (`s20`) · `kWh/kg + tesis ortalaması`
(`s16` — genel ortalamayı satırın yanına koyma; `pay` penceresinin kardeşi).

---

## §100 · T TURU — **sistem cevabı hesaplıyor, chip'e yazıyor ve «anlamadım» diyordu**

### §100.1 · 🔴🔴 KÖK-T1 — beş kanıt, tek desen

| # | soru | not | `next_steps` |
|---|---|---|---|
| `t1` | `hangi müşteri bize en çok kâr bıraktı` | *"Hangisini istiyorsun?"* | `parti · kar · müşteri` |
| `t11` | `vardiya bazında kaza sayısını sırala` | *"Hangisini istiyorsun?"* | `İSG · kaza adedi · vardiya` |
| `t13` **[AR]** | `أكثر استهلاكاً للطاقة` | *"Hangi ölçüyü istiyorsun?"* | `elektrik` · `tep` |
| `t16` | `her makinenin toplam duruş içindeki payı` | *"Hangisini istiyorsun?"* | `duruş nedenleri · toplam duruş dakikası · makine` |
| `t18` | `geçen çeyrek ile bu çeyreği hat bazında kıyasla` | *"Hangisini istiyorsun?"* | `parti · fire oranı · hat` |

Dördünde chip listesi **TEK ELEMANLI**. Yani sorulacak bir şey yok — sistem cevabı
**hesaplamış**, chip'e **yazmış**, ve kullanıcıya *"anlamadım"* demiş.

**Kök:** oy `_canon_cq` ile **tam `cq`** üzerinde sayılıyor. İki oy önemsiz bir alanda
ayrılınca (biri `order` yazmış, öteki yazmamış) uyum **%50**'ye düşüyor ve kazanan ilan
edilmiyor — oysa **kullanıcının sorduğu şey** (küp · ölçü · kırılım) ikisinde de
**birebir aynı**. Chip listesinin tekilleşmesi bunun **kanıtıdır**.

**Düzeltme:** chip listesi ikiden azsa netleştirme **atlanır**, ilk aday cevaplanır.

⚠ Bu bir **çoğunluk kuralı DEĞİLDİR** (`§77`'nin ölçülerek reddedilen yolu): oylar
arasında **tercih** yapılmıyor; adayların anlamca **aynı** olduğu chip listesinin
kendisiyle **gösteriliyor**. Gerçek belirsizlikte (`t13`: `elektrik` vs `tep` → **iki**
chip) dal aynen sorar.

> *Bir soruyu sormak için önce iki farklı cevabın olması gerekir.*

**Curl doğrulaması:**

    t1  → EGE KNIT · **4.916.014 ₺** kâr · sıralı
    t11 → `kaza_vardiya` + **`_p_sira_kaza_adedi: 1`**  ← sistem SIRA penceresini kullandı
    t16 → **`_p_pay_toplam_sure_dk: 9.57`** — RAM-1 toplam duruşun %9,57'si
    t13 [AR] → `enerji_makine.toplam_tep` · dönem soruyor  (sahte belirsizlik kalktı)

### §100.2 · T turu tablosu (20 senaryo · 14'ü thread)

| # | senaryo | sonuç |
|---|---|---|
| T1 | `hangi müşteri bize en çok kâr bıraktı` | 🔴→🟢 **KÖK-T1** |
| T2 | `bu üçünün fire oranlarını da yanına koy` | ◐ çapa yoktu (T1 cevapsızdı) |
| T3·T4·T5 | `kâr marjı en düşük 5 müşteri` → `renkleri kır` → `renk bazında sırala` | 🟢 `limit:5` · çapa korundu · kırılım değişti |
| T6 | `enerji yoğunluğu en yüksek makine` | 🔴 chip'te sunduğu kelimeyi soruda tanımıyor |
| T7·T8 | `o makinenin OEE'si` → `aylık göster` | ◐ makine çapası kayıp · aylık ✓ |
| **T9** | `kaza sayısı en yüksek departman` | 🟢 `isg × departman`, sıralı |
| **T10** | `o departmanın eğitim saatleri` | 🟢🟢 **küpler arası takip** (`isg`→`egitim`) · dönem çapası **beyanlı** taşındı · yazım düzeltmesi |
| T11 | `vardiya bazında kaza sayısını sırala` | 🔴→🟢 **KÖK-T1** |
| **T12 [EN]** | `which supplier has the worst first pass yield` | 🟢🟢 yeni `tedarikci` boyutu · belirsizlik **beyanlı** |
| T13 **[AR]** | `أكثر استهلاكاً للطاقة` | 🔴→◐ sahte belirsizlik kalktı |
| **T14** | `son 6 ayda fire oranı **artan** makineleri bul` | 🟢🟢 garson kendiliğinden `pencere: degisim_yuzde` üretti |
| T15 | `bakım maliyeti ile arıza sayısı ilişkisi` | 🔴 Discovery bütçe aşımı |
| T16 | `her makinenin toplam duruş içindeki payı` | 🔴→🟢 **KÖK-T1** + pay penceresi |
| T17 | `payı %10 üstünde olanlar` | 🔴 çapa kayıp → Discovery |
| T18 | `çeyrek kıyası, hat bazında` | 🔴→◐ **KÖK-T1** |
| **T19** | `ortalama çözüm süresi en uzun 3 şikayet konusu` | 🔴 **uydurma filtre**: `siddet='ORTA'` + `renk='Orta'` ← *"**ortalama**"* |
| **T20** | `3 aylık hareketli ortalamasını çiz` | 🟢🟢 garson `pencere: hareketli_ort, pencere_boyu: 3` üretti |

**Discovery ateşlemesi: 2** (T15 · T17).

⊙ **Garson artık pencere yeteneğini doğal dilden kendisi sipariş ediyor** (`t14` · `t20`)
— `§91`'de inen katman, iki turda kullanıcı diliyle doğrulandı.

### §100.3 · Açık kalan kök (U turuna) — **sıfat bir kategori değeri değildir**

`t19`: *"**ortalama** çözüm süresi en uzun 3 şikayet konusu"* →

    filters: [{siddet eq "ORTA"}, {renk eq "Orta"}]

*"Ortalama"* bir **ölçü niteleyicisidir**; `ORTA` bir **şiddet değeri**, `Orta` bir
**renk**. Sistem üçünü karıştırdı ve cevabı **sessizce** o iki filtreye daralttı.

⊙ Bu, `§86.8`'in (fiil bir kategori değeri değildir — `açıkla` → `renk="Açık"`) **sıfat
tarafındaki ikizidir** ve artık **iki** kanıtı var. Ortak kök: değer eşleştiricisi,
kelimenin **cümledeki işlevine** bakmıyor.

### §100.4 · Kapı

    korpus doğru-cube %94.9 (taban %94.4) ✅ · sessiz_yanlis 10 ·
    gerçek-dünya {2287 · kabul 1145 · dogru 90} · süit **4267 yeşil** · eval +0,0%
