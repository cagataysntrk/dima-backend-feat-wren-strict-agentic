# OPERASYON DURUMU — *nerede kaldık*

> 🔴 **BAĞLAM SIFIRLANDIYSA BURADAN BAŞLA.** Sırayla oku:
> 1. **`OPERASYON.md`** — kural seti (nasıl çalışılır) · **sıra `OPERASYON.md §10`'dadır**
> 2. **bu dosya** — nerede kaldık
> 3. 🔴 **`~/.claude/plans/DIMA-GARSON-ARA-FAZ.md`** — **AKTİF FAZ** (garson/insani katman;
>    kendi test ve geliştirme politikasını §12/§13'te taşır)
> 4. **`~/.claude/plans/DIMA-V1-YOL-HARITASI.md`** — v1 gövdesi + §G (ara faz onu yeniden
>    sıralar, yerine geçmez)
> 5. `backend/MIMARI.md` — mimari değişmezler *(çelişkide **o** kazanır)*
>
> Bu beş dosya operasyonun **tam durumunu** taşır. Sohbet geçmişine ihtiyaç YOKTUR.
>
> ⚠ **Düzeltilmiş çapraz atıf:** eskiden burada *"yol haritası — ne yapılacak (§10'daki
> sıra)"* yazıyordu; **yol haritasında §10 YOKTUR**, kastedilen `OPERASYON.md · §10`'dur.
> Bu satırı takip eden bir ajan sırayı bulamıyordu.

**Son güncelleme:** 2026-08-07 · HEAD @`b297e6c` ·
🟢 **GARSON ARA FAZI TAMAMLANDI** — `G0…G8` + `Z` indi (13 commit), push edildi

⚠ **VE BU BAŞLIK BİR KEZ DAHA BAYATLADI.** Faz boyunca 13 commit atıldı; başlık hâlâ
*"planlama bitti, `G0` bekliyor"* diyordu ve bunu **bir denetim ajanı yakaladı** — tam
olarak aşağıdaki uyarının ikinci kez gerçekleşmesi. Bağlam sıfırlanan bir ajan bütün
fazı **baştan** yapardı. 🔴 *Bir kuralı yazmak, onu uygulamak değildir.*

⚠ **Bu başlık BİR KEZ BAYATLADI ve bir denetim onu yakaladı:** *"HEAD → FAZ 0 · adım 1"*
yazıyordu, gerçek HEAD **FAZ 4.4**'teydi. Bu dosya *"bağlam sıfırlanırsa buradan başla"*
diye ilan edilmiş olduğu için bayat bir başlık, sıfırlanan bir ajanı **yanlış fazdan**
devam ettirir. 🔴 **Kural: her faz commit'inden sonra bu blok güncellenir.**

---

## 🔵 ŞU AN

| | |
|---|---|
| **Aktif faz** | 🟢 **GARSON ARA FAZI ✅ BİTTİ** *(`G0…G8` + `Z`, HEAD `b297e6c`)* — sırada v1'in kalanı / Bölüm II | ⟵ *(eski satır aşağıda)* |
| ~~eski~~ | ~~🔵 **GARSON ARA FAZI** — `~/.claude/plans/DIMA-GARSON-ARA-FAZ.md` · **planlama BİTTİ**, sıradaki madde **`G0` (ölçüm aleti)** · 🔴 *G0 inmeden kod yazılmaz* |
| **Önceki** | v1 gövdesi ✅ *(FAZ 0…8; FAZ 7.3/7.7'nin kalanı ve `3.0` tenant açılışı açık)* |
| **Korpus** | 🟢 **%95,1** — kapı çıktısı `kapi.py --tam` *(şirket kırılımı `backend/lab/reports/nl_corpus.md`)* |
| **Garson kapısı** | 🟢 **10/10 satır YEŞİL** — `garson_baseline.json` donduruldu *(3 canlı koşum, `KURAL G-1` ✓)*. ⚠ `2·anlat` sekiz koşum boyunca `0\|0\|0` idi çünkü **hiç ölçülmüyordu** |
| **Gerçek-dünya** | kabul **1138** · doğru **69** · sessiz_yanlış **12** · beyanlı_kısmi **72** *(⚠ `dogru` düşüşü gerileme DEĞİL: `dogru+beyanli` 140→141 korundu, `uyum` kapısı keskinleşti — `gercek_dunya_baseline.json` gerekçeli)* |
| **Süit** | ⚠ **3869 sayısı BAYAT** — faz boyunca ~1000 satır yeni test indi; `--hizli` son koşumu **1526 yeşil** (kapı seçimi), `--hepsi` faz kapanışında **koşulmadı** (borç) |
| **§C ölçütü** | **10 yeşil · 5 sarı · 1 kırmızı** (ölçüt 4 — `motor_cls` hâlâ `off`) · 13 ⊘ *(kod değil)* |
| **Push** | ✅ `origin/wren-bağımsız` ile **fark 0** |
| **Sağlayıcı** | 🔴 **OpenRouter + NVIDIA açık kaynak model** *(karar 2026-08-07)* — mimari sonucu: `llm_sema_kisitli` bu sağlayıcıda **NO-OP** (ara faz §7.4) |

### 🔴 GARSON FAZININ AÇIK BORÇLARI *(ara faz belgesinden)*

| # | Ne | Nerede |
|---|---|---|
| **B-G1** ✅ | ~~`lab/garson.py --live` **yok**~~ → `G0`'da indi ve `Z.2`'de canlı koştu (3 koşum). ⚠ **Ama alet 10 satırın 4'ünü hiç ölçmüyor** — yeni borç aşağıda. Eski: `lab/garson.py --live` **yok** — garsonu görebilen tek alet kurulmadı; `konusma_senaryolari` sekiz koşumun sekizinde de `⊘ ÖLÇÜLEMEDİ` verdi | ara faz `G0` |
| **B-G2** ✅ | `G2`'de **sıfırdan** yazıldı (`app/diyalog.py`) ve `Z` turunda istemci yankısı bağlandı. Eski: `0.5b` FAZ 0'da ✅ ilan edilmiş ama **kodda sıfır iz** (`netlestirme.birlestir` · `bekleyen_netlestirme` → 0 isabet) → `AJ0b` **sıfırdan** yazılacak | ara faz `G2` |
| **B-G3** ✅ | `G4`'te indi; `Z`'de canlı kapı onun **şemasız koştuğunu** bulup düzeltti. Eski: `app/iddia.py` **yok** — `t2_anlatici` bu kapı olmadan açılamaz | ara faz `G4` |
| **B-G4** ◐ | **YARIM.** `compare` şemaya ve `parse_cube_query`'ye girdi; ama **`blend` girmedi** ve `compare` hâlâ **enum** (`yoy`/`mom`), plan onu **ALAN**'a çevirmek istiyordu. 🔴 Bu yüzden `5.6` (peer) **hâlâ bloke** — önceki turda «açıldı» denmişti, **fazla iddialıydı**. Eski: Intent-JSON'da `compare`/`blend`/çoklu dönem **yok** → `5.6` (peer) **BLOKE**, v1 §G'siz kapanamıyor | ara faz `G6` |
| **B-G5** ✅ | Çelişki çözüldü: `§5` satırı bayattı, `:442` güncel → `§5` ◐ **KISMEN İNDİ** oldu. Eski: `MIMARI.md` §5 (*18. yasak ⟳ UYGULANMADI*) ile `:442` (*inmiş + ölçülmüş geri alma*) **çelişiyor** — biri bayat | ara faz `G3` + §13.6 |
| **B-G6** ✅ | `G8`'de indi (`app/yetenek.py` · `Sinir.oneriler`, katalogdan `route()` ile doğrulanmış öneriler). Eski: `KÇ-7` (*"anlamadım" ≠ "yapamıyorum"*) denetim belgesinden **açık** | ara faz `G8` |

### ✅ BU TURDA KAPANANLAR

| # | iş | ölçüm |
|---|---|---|
| **UI/UX F1-F6** | **altısı da** kapandı | hard-delete ihlali · geri alma · hata yüzeyi · tek ses · büyüme kapısı · görünmeyen özellikler |
| **Yetim modül** | **12 → 0 gerçek** | 8 bağlandı; 4'ü **meşru bekleyiş** *(bir sayıyı kusur listesi sanmak, dördünü haksız borç yazar)* |
| **Ölçüt 6** | *"süre aşımı 30 dk"* **yoktu** | imzalı onay bileti; ölçüt 🟢 işaretliyken **üçte biri eksikti** |
| **Ölçüt 12** | tazelik zinciri | `SyncState → kademe → freshness → ekran`; **ortası** eksikti |
| **Borç 1** | motor-RLS tesisatı | `motor_cls=on` ile **3319 yeşil / 0 kırmızı** |
| **Borç 7** | modül tavanları | `ask()` 1206→1150 · `ask.py` 2498→2377 · `cube_router` 1749→1703 |
| **Hızlı kapı** | **iki kör nokta** | `.tsx` → 0 kapı seçiyordu · dosya **yolunu** okuyan kapılar hiç seçilmiyordu |
| **CLS gölgesi** | **hiçbir şey ölçmüyordu** | `shadow ≡ off` idi; artık plan farkını **ölçüyor** |

### 🔴 AÇIK KALANLAR — ve hangisi KOD değil

| # | ne | tür |
|---|---|---|
| **Ölçüt 4** | `motor_cls` — gölge ölçümü **kuruldu**, sıra: `shadow` aç → **7 gün · sapma 0** → `on` | ⏳ **süre** |
| **FAZ 8.1** | gerçek kullanım penceresi: 1-2 kullanıcı × 2-4 hafta · **≥300 tur** | ⏳ **süre** |
| **§9.6** | 🔴 **gerçek-dünya korpusu** — persona × zorluk merdiveni | 🔨 kod |
| **FAZ 7.7** | `/settings` tam sayfa + `admin_app`'in 13 router tüketicisi | 🔨 kod |
| **FAZ 7.3** | 10 alt madde (a-kısmi · c · d · f · g · h · i · j · l · m) + 6 rota | 🔨 kod |
| **`3.0`** | tenant açılışı — v1'in **tek sessizce atlanan** maddesi | 🔨 kod |
| **Bayrak** | `public_api` · `threaded_chat` **kapısız**; `cekirdek_katman` **iki sahipli** | 🔨 kod |
| **F2 kalanı** | bağlantı · tercih geri alma — ⚠ **gerekçesi yazılı**: ikisi de yeniden kurulabilir | ◐ karar |

### 🔴 KULLANICI TESPİTİ — *"bayrakları hep `off` tuttuk, hiç değişiklik olmadı"*

**Ölçüldü: iki ayrı sebep aynı belirtiyi üretiyordu** ve ayrım yapılmadan hiçbir A/B
kararı verilemezdi.

| sebep | belirti | durum |
|---|---|---|
| **(a)** bayrak **bağlı değil** — açmak hiçbir şey yapmaz | *"fark yok"* | ✅ **beşi bağlandı** (§11/GRUP 2) |
| **(b)** korpus değişimi **göremiyor** — `execute=False`, LLM yok, sorular kataloğun kendi sözlüğünden | *"fark yok"* | 🔴 **açık** — §9.6 |

> 🔴 *Bir A/B'nin sonucu "fark yok" ise, önce ölçen aletin o farkı **görebildiği**
> kanıtlanmalıdır.* Korpus bugün *"sistem kendi kelimelerini tanıyor mu"* sorusunu
> ölçüyor (**≥%97,1 katalog türevi**) — kullanıcının kelimelerini değil.

---|---|
| **Aktif faz** | **FAZ 7 · ARAYÜZ** *(FAZ 0·1·2·3·4·5·6 ✅ bitti)* — panel tavanı **13/13 DOLU** |
| **Biten** | 🎉 **FAZ 4·5·6 KAPANDI** + denetim **D1–D5**. FAZ 6: `6.0` D9 geri alma · `6.1` onay akışı · `6.2` yazma araçları · `6.3` araç kaydı 16→23 · `6.4` planlayıcı sertleştirmesi · `6.5` public API · `6.6` kanal kimliği |
| ⏸ **5.6 BLOKE** | peer kıyası **AJ2**'ye bağlı (`compare` enum→ALAN). AJ2 inmeden 5.6 üçüncü bir enum değeri çakar ve dördüncüsü aynı konuşmayı yeniden doğurur |
| **§C/16 ÖLÇÜLDÜ** | **%76,1** doğru · netleştirme **%16,8 ayrı satırda** · n=**155** · `demo-boyahane`. Üç şirket `⊘` (mssql fixture, altın cevap üretilemedi) |
| **Sıradaki madde** | **FAZ 7.3** + **7.7**'nin `/settings` yarısı — `7.0`·`7.1`·`7.2`·`7.4`·`7.5`·`7.6`·`7.8`·`7.9`·`7.10`·`7.11` ✅ · `7.7` kimlik yarısı ✅ |
| ⏸ **6.5/embed BLOKE** | 🔴 **P0 ölçüldü**: `motor_cls=off` — motor-RLS hiç açık değil, `always_filter` tek başına yeterli sayılmaz. Kapı `embed_kapsam.p0_engeli()`de |
| **Korpus** | **%93,1** — FAZ 5·6·7 boyunca **sabit** (taban %93,2); semantik vaka 407/444 = %91,7 |
| 🆕 **FAZ 7'de ölçülen ve GERÇEK çıkan kusurlar** | (a) `opacity-40` **14 kez `disabled:` + 14 kez düz** → *"soluk"* ile *"devre dışı"* aynı piksel · (b) `focus-trap` **0 kullanım**, üç modal odağı hiç tutmuyordu · (c) `window.prompt` **4 yerde** birincil yüzey · (d) `max-md:`/`max-lg:` **0** → 375px'te sağ bölmeye **7px** kalıyordu · (e) cevap kartında `<details>` **0** (D3 yanlış kapatılmıştı) · (f) `Yüksek güven (100%)` — kalibre edilmemiş, MIMARI §9'un **canlı ihlali** · (g) `PivotTable.tsx`'te **iki gömülü NUL** (UTF-8 geçerli, hiçbir linter görmedi) · (h) `AuthUser.email` **zorunlu** ama `/auth/me` onu hiç göndermiyordu |
| **Sonraki faz** | FAZ 8 (3 madde — gerçek kullanım penceresi) → **v1 son kontrol** |
| ✅ **Borç 1 TESİSATI KAPANDI** | `motor_cls=on` ile **3319 yeşil / 0 kırmızı** (39'du). Bayrak yine **açılmıyor**: (a) ölçüt 4 *"gölge modda 7 gün"* ister — süre, kod değil; (b) 🔴 **CLS gölge modu bugün hiçbir şey ölçmüyor** (`shadow` ≡ `off`), `off→shadow` ilerleme gibi görünen bir hiçlik olurdu; (c) açmak `6.5/embed` P0'ını yeniden açar |
| ✅ **Borç 7 (yeni) KAPANDI** | Modül tavanları: `ask()` 1206→1150 · `ask.py` 2498→2377 · `cube_router` 1749→1703. ⚠ Kapı **hiçbir hızlı koşumda seçilmiyordu** — `.tsx` kör noktasıyla aynı sınıf |
| ~~◐ eski borç 1~~ | Kimliğin **tek sahibi** kuruldu (`app/istek_kimligi.py`, ContextVar — bu depoda 3. kez); üç giriş noktası (HTTP · zamanlayıcı · MCP) kimliği **kendisi** kuruyor. 🔴 `motor_cls=on` hâlâ **39 kırmızı**, ama sebep DEĞİŞTİ: 36 çağrı sitesi değil, `WrenService`'i **doğrudan kuran test/lab yolları**. Kalan iş: fixture düzeyinde açık kimlik — **ürün kodunda sıfır değişiklik** |
| ✅ **Borç 2 KAPANDI** | FAZ 4.3 — çıplak ikinci ölçü adı: **−%18,2 → −%4,5**, `kaldi` → `gecti`, korpus sabit. Bayrak `olcu_ekleme_takibi` **beta** |
| 🔴 **Açık borç 3** | **11 bayrak `off`** — ödenmiş, testli, kullanıcıya kapalı. Üçü FAZ 1'in ana teslimatı (`tazelik` · `lineage` · `metrik_sertifikasi`). ⚠ `capa_zinciri` ve `olcu_ekleme_takibi` bu turda **ölçümle açıldı** |
| ✅ **Borç 4 KAPANDI** | **ADR-0025…0034** yazıldı (10 karar) ve kararın yaşadığı yere atıflandı; kapı **köken beyanına** çevrildi (`REKONSTRÜKSİYON` ↔ `GÜNÜ YAZILDI`) |
| ✅ **Denetim D3/D5** | `is_period_only` **kaldırıldı** (şartnamesi önce gerçek akışa taşındı) · deneyim süitinde `⊘`'nin **iki anlamı ayrıldı**: *"%60 koşmuyor"* aslında **60 tasarım + 3 gerçek risk** |
| **Tempo** | 🔴 **YENİ TEST POLİTİKASI** (`backend/CLAUDE.md`): geliştirmede `--hizli --degisen` (~1 dk) · demet sonunda `--tam` = **yalnız korpus** (1 dk 50 sn) · `--hepsi` **yalnız gecelik CI** |
| **v1 bitiş ölçütü** | §C'nin **16 ölçütü** yeşil |

---

## ✅ BİTEN

### FAZ −2 · Belge onarımı *(kod yok — 2026-08-04)*
Yol haritası **4881 → 5213 satır**. Yedek: `~/.claude/plans/.yedek/` *(md5 doğrulandı)*.

| # | Ne | Nerede |
|---|---|---|
| **#5** | **`§G.6f`** — `N`=3 (simetri şartıyla) · hakem protokolü (2 hakem · 10 vaka · ayrışma→`⊘`) · 🔴 **`⊘ KOŞULAMADI` ≠ «kaybetti»** · kısmi benimseme | §G.6f |
| **#1** | v2 giriş **döngüsel kilidi** kırıldı: *"teyitli"* → **"kararı bağlanmış"**; v3'e ait 2 madde kapıdan çıkarıldı | §B · Bölüm II girişi · II-0 |
| **#4** | FAZ 0'ın **dört `KAT-3` ihlali** + **bağlayıcı koşum sırası**; `0.23`'ün *"bağımlı değil"* çelişkisi kapatıldı | FAZ 0 girişi · 0.23 |
| **#3** | **`6.0` YENİ MADDE** — *"D9 ters uygulanmış · yapılanı geri al"*; `6.1`'in çelişkili `KAPI` bloğu kaldırıldı | 6.0 · 6.1 |
| **#2** | Bölüm II şablon borcu: **18 bayraklı maddenin 17'sinde `GERİ AL` yok** + kök neden (denetim regex'i `II-X.N` başlıklarını kapsamıyordu) kapıya çevrildi | Bölüm II girişi |
| **+** | **VK-5 üç kalıntısı** düzeltildi *(aşağıdaki ölçümle)* | §G.6e |

### FAZ −1 · `MIMARI.md` ön hazırlığı *(kod yok — 2026-08-04)*

| Kutu | Ne indi | Kanıt |
|---|---|---|
| **A** (`−1.1`) | MIMARI'de **12 satır** düzeltildi (A1…A13; **A6 geri çekildi**) | `MIMARI.md` diff |
| **B** (`−1.2`) | **`§0 · ⟳ YÜRÜRLÜKTE` toplu indeksi** — 13 satır. 🔴 Blok **kural BEYAN ETMEZ**, yalnız **otorite işaret eder** | `MIMARI.md §0` |
| **C** (`−1.3`) | Her `⟳` satırı için **tuzak** + 2 meta-test → `test_beyanlar_curumesin.py` **27 yeşil** | dosya |
| **KAPI** | **yeni** `tests/test_MIMARI_dosya_atiflari_var.py` — MIMARI'de anılan her `tests/test_*.py` var olmalı | 12 ✅ · 2 ⊘ |

> 🔴 **Kutu C'nin dersi — üç kırmızının ÜÇÜ DE tuzakların değil BENİM BELİRTECİMİN kusuruydu.**
> Tam olarak *"ölçüm aracının kendisi de bir bağımlılıktır"* sınıfı; her biri **metni** ölçüyordu, **kodu** değil:
> · `§3.4-osi` gevşek alt-dize (`"ossie" in <tüm app kaynağı>`) **yorum satırını** yakaladı → **dosya varlığına** indirildi
> · `§4` alt-dize taraması `tools.py`'nin **docstring'ini** yakaladı → **AST**'ye indirildi (`_yazan_arac_sayisi`)
> · kural-beyanı kapısı bloğun **kendi açıklamasını** ihlal sandı → yalnız **tablo satırlarını** tarar
> **Yasağı anlatmak, yasağı çiğnemek değildir.**

**Yol haritasında kapanan borçlar** *(5213 → 5239 satır; yedek + md5 doğrulandı)*:
`A5` → **D2 biçimi** (sabit sayı silindi, `A5-KOMUT` kutusu yazıldı; **6 kalem bayatlamıştı**,
4 kalem doğruydu) · `A6` → geri çekildi + kütük · `KAPI` atfı → dosya değil **fonksiyon**
(`test_beyanlar_curumesin.py::test_MIMARI_TEST_SAYILARI_gercekle_uyusuyor`) · *"altı satır"* ↔
13 satır çelişkisi *(açık borç #3'ün bir kalemi)*.

> ⛔ **A6 neden düştü:** *"`tests/test_member_sweep.py` YOK"* iddiasının kanıtı
> (`grep -rl member_sweep` → boş) **hiç koşulmamıştı**. Dosya **VAR**: 113 satır, 5 test,
> commit `f5f4048`. **Kanıt cümlesi de kanıt ister.**

### FAZ 0 · adım 1 — `0.22` · `0.2` · `0.23` *(2026-08-04)*

| Madde | Ne indi | Kapı |
|---|---|---|
| **0.22** | `migration_trace` **fonksiyon gövdesine** taşındı *(tanım `if structural_followup:` bloğunun içindeydi, 4b dalı blok DIŞINDA okuyordu)* | `test_agent_plan_secimi_yapisal_olmayan_turda_cokmez` + `test_MIGRATION_TRACE_blok_disinda_TANIMLI` |
| **0.2** | `sec()` reddi `kapisiz=True · dis_maliyet="sifir" · notlar` ile kaydedilir; **ayrıca** `Kosum.sorgu_sayisi` **fail-safe** oldu | `test_uydurma_arac_makbuzu_dusurmez` + `test_MAKBUZ_bilinmeyen_arac_adinda_da_AYAKTA_kalir` |
| **0.23** | `raporlanabilir()` **tek sahip**; `ReportPanel`'in İKİ kapısı ona bağlandı; **saf-not dalına `next_steps`** | `test_cevap_alani_yetim_degil.py` **+4 test** · `tsc --noEmit` 0 · `eslint .` 0 hata |

> 🔴 **HER İKİ HATA DA «ÖNCE ÖLÇ» ile kanıtlandı** — hatalar koda geri konup kapılar
> **kırmızıya** düşürüldü, sonra düzeltmeyle yeşile: `UnboundLocalError: ... 'migration_trace' ...`
> @ `ask.py:3217` · `KeyError` @ `planner.py` `sorgu_sayisi`.

> ⚠️ **0.22'nin kapısını ÜÇ KEZ yanlış yazdım, üçünü de ölçerek yakaladım:**
> (1) soru `route()` ile cevaplanıyordu → test **boşa koşuyordu**;
> (2) doğru soru **yanlış çağrı yerini** vuruyordu — pilotun `[]` literali geçen ikinci
> çağrı yeri hatalı kodda bile çökmüyor, yani test **hatayla birlikte yeşil kalıyordu**;
> (3) `code_context` tek satır verdiği için iki satıra yayılan çağrıyı göremiyordu.
> Kapı artık **çağrı yerini de** iddia ediyor. *Bir kapı, ölçmediği şeyi «geçti» diyemez.*

> 🔴 **VE DÖRDÜNCÜ KEZ AYNI SINIF — kapı turunda:** `⟳` sayacı `mimari.count("⟳ UYGULANMADI")`
> idi; §0'a bloğun kendi kapılarını anlatan paragraf eklenince o **ifade düzyazıda** da geçti
> → sayaç **14**, tablo **13**. Belge doğruydu, **sayaç yanlıştı**. Kök neden: satır
> ayrıştırma **tek sahibe** alındı (`_yururlukte_satirlari`) — üç test de artık düzyazıyı hiç
> görmeden tablo satırı üzerinden ölçüyor, kaçışlı `\|` tek yerde ele alınıyor.

### FAZ 0 · adım 2 — `0.1` yeniden ölçüm turu *(2026-08-04)*

**Teslimat:** `backend/lab/faz0_taban.py` → `backend/lab/reports/faz0_taban.md`.
§C'nin *"Bugün"* sütunu **artık elle yazılmıyor**; yol haritası bu araca işaret ediyor.

> 🔴 **Ölçüt 1'de TANIM BULANIKLIĞI ölçüldü:** *"yanlış-cube 493"* aslında
> **458 yanlış cube + 35 Discovery'ye düşme**dir. Hedef *"azalır"* olduğu için hangi
> sayının azalacağı belirsiz kalamaz → **1a / 1b / 1c** olarak ayrıştırıldı.

> ⚠ **Aracın kendi kusuru (bu turda BEŞİNCİ kez «ölçüm aracı bir bağımlılıktır»):**
> ilk sürüm host'ta `pytest --collect-only` koşup **1806** yazıyordu — konteynerde
> **2056**. Eksik bağımlılık yüzünden modüller toplanamıyor, `pytest` yine de
> *"collected"* diyor. Araç artık **toplama hatası varsa sayı yazmıyor** (`⊘`).
> İkinci kusur: markdown hücresindeki `|` kaçışlanmıyordu → tablo sessizce bozuluyordu.
> Üçüncüsü: `receipt`/`supersedes` için sayaç **1** deyip *"tüketiliyor"* okunmuştu —
> o isabet `lib/types.ts`'teki **tip beyanıydı**. **Bir tip beyanı tüketici değildir.**

**[KANIT §0.1]'in 12 kusuru @`0619bfd`** — ✅ **3 kapandı** · ◐ **3 kısmen** · 🔴 **6 açık**:

| # | Kusur | Durum | Sahibi |
|---|---|---|---|
| 1 | `sec()` → makbuz düşüyor · bütçe kapısı atlanıyor | ✅ **kapandı** | *bu operasyon, `0.2`* |
| 9 | `_META_HINTS` çıplak alt-dize | ✅ kapandı | — |
| 11 | `eval/baseline.json` bayat · katı monkeypatch | ✅ kapandı | `baseline.n` 129 ↔ `report.n` 129 |
| 2 | `AnalysisCanvas` rozet basmıyor *(SourceBadge **0**)* | 🔴 açık | **0.3** |
| 3 | Netleştirme, Intent-JSON'dan sonra | ◐ mekanizma indi, bayrak `off` | **0.4** *(ölçüm kararı)* |
| 4 | Çapa zinciri üretimde ölü *(`capalar=` **0**, `SureklilikOlcumu` **0**)* | 🔴 açık | **0.5** |
| 5 | `GET /contracts` tüketicisiz *(kapı yanlış-pozitif yeşil)* | 🔴 açık | **0.6** |
| 6 | `POST /query` + `runQuery()` ölü | 🔴 açık | **0.7** |
| 7 | Alan yetimleri — hâlâ yetim: **`receipt` · `explain.path` · `supersedes` · `execute`** *(`kpi_components` **2** tüketici ile kapandı)* | ◐ kısmen | **0.8 · 0.9 · 0.11** |
| 8 | `interpret` `"top"` fact'i UI'da yok | 🔴 açık | **0.10** *(+ 0.10b)* |
| 10 | `sinifla(baglam_var=True)` sabit kodlu | 🔴 açık | **5.0** |
| 12 | Sosyal sınıf teslim borcu — **bayrak YOK** *(MIMARI düzeltildi, test var)* | ◐ kısmen | **0.13** |

> ✅ **Sonuç: FAZ 0'ın iş listesi ÖLÇÜMLE DOĞRULANDI** — açık kalan dokuz kusurun
> **dokuzu da** zaten bir FAZ 0/5 maddesinin konusu. Yeni madde doğmadı, üç madde düştü.

### 🔴 P0 · CANLI KULLANICI TURUNUN BULDUĞU SESSİZ-YANLIŞ *(2026-08-04)*

Denetçi **C** (gerçek kullanıcı gibi, 16 tur, canlı `gemini-flash-lite`) `makine × ay`
kırılımlı fire raporunda **aynı veri için üç ayrı yüzde** gördü:
`+%88,1 arttı` → `−%72,3 azaldı — İYİLEŞTİ` → `+%98,3 arttı`.

> *"Aynı veriye üç farklı yüzde. Sarı satırı okumayı bıraktım."*
> *"Veriyi çekmek için kullanırım, ama yorumunu müdürler toplantısında ekrana
> yansıtmam — çünkü yanlış yüzdeyi bir kez okursam, o toplantıda benim itibarım gider."*

**Kök neden (kendim ölçtüm):** `interpret._series_facts` **satır başına** bir nokta
alıyordu; pivotta aynı ay onlarca kez tekrarlanır ve *"ilk→son"* **iki farklı makinenin**
değeridir. Kod pivot olduğunu **zaten fark ediyordu** (`entity`) ama sayıyı yine yayımlıyordu.

**Düzeltme iki katmanlı, ve ikinci katman asıl olan:**
1. Trend **dönem toplamları** üzerinden (`_donem_bazinda_topla`).
2. 🔴 Toplanabilirlik kuralı **zaten tek sahipteydi** — `contribution.ayristirilabilir_mi`.
   `interpret` onu **tanımıyordu**: katkı yolu *"oran → katkı payı tanımsız"* diye dürüstçe
   reddederken yorum satırı aynı ölçü için hem payı hem trendi basıyordu. **Kimlik
   asimetrisi.** Artık sahip çağrılıyor; toplanamayan ölçüde trend **hiç yazılmıyor**,
   *"toplamın %X'i"* payı da yalnız toplanabilir ölçüde yayımlanıyor.

**Önce ölçüldü:** eski kod geri konunca kapı üç kırmızı verdi — `%0.0` (doğrusu %100) ·
oran ölçüsünde trend yayımlandı · *"toplamın %55,7'si"*. Kapı: `tests/test_pivot_trend_yanlis_degil.py`.

### 🔴 P0 · DENETÇİ B'NİN BULDUĞU — onay kartı ekranda yoktu *(aynı tur)*

`raporlanabilir()` gövde alanlarını **SAYIYORDU** (`result|kpi|contribution|prescription`)
— bir **`KAT-5` ihlali**. Listede olmayan **beşinci** gövde alanı `eylem_onerisi`, yani
**FAZ H'nin *"Onayla"* kartı**; `ReportCard`'ın TEK tüketicisi bu kapının arkasında olduğu
için kullanıcı *"bundan sonra hep aylık göster"* dediğinde **sarı bir not** görüyor,
**Onayla düğmesi hiç çıkmıyordu**. 🔴 *0.23'ün düzelttiği hatanın birebir aynısı,
düzeltmenin **kendi içine** kodlanmıştı* — ve kapının testi de aynı dört adı sabitlediği
için **ölçülemezdi**.

**Düzeltme — SAYMA, KAPAT:** gövde alanları sayılmıyor; **saf-not** (yalnız açıklama/
taşıma alanı taşıyan cevap) kapatılıyor. Yeni bir gövde alanı eklendiğinde liste
güncellenmek zorunda değil. Hata yönü de tersine çevrildi: unutulan bir *taşıma* alanı
**görünür** bir gerileme üretir; unutulan bir *gövde* alanı **sessiz** kayıptı.

**B'nin diğer işlenen bulguları:**

| Bulgu | Ne yapıldı |
|---|---|
| **İhlal 1** — *"tek sahip"* kutlanırken `next_steps` chip bloğu `ReportPanel`'e **22 satır kopyalandı** (19'u birebir) | **`NextStepChips.tsx`** tek sahip olarak çıkarıldı; ikon eşlemesi de tek yerde *(backend `NextStep.kind` kısıtsız — dördüncü tür artık iki yerde birden sessizce `∑` olmuyor)* |
| **İhlal 2** — bilinmeyen araç adı makbuzda **işaretsiz**: `query_count` tahmin taşıyor, `error`/`gated` yok | `Adim.ozet()` artık işaretliyor (`tools.kayitli_mi`) — *"tahmine dayanan her sınır GÖRÜNÜR olur"* |
| **R9** — netleştirme şıkları *"sonraki adım"* başlığıyla sunuluyordu *(`ReportCard`'ın kendi yasakladığı yanlış başlık)* | başlık çağırana ait: not dalında **"şunlardan biri mi?"** |
| **R6** — `_yorumsuz_kod` yalnız tek satırlık yorumları atıyordu, **8 satır sızıyordu** | çok satırlı `{/* */}` blokları da atılıyor |
| **R7** — `test_SAF_NOT_dalinda_NEXT_STEPS_var` **dosyanın tamamını** tarıyordu (bir yorum satırı testi yeşil tutardı) | dal bulunup **yalnız o dal** ölçülüyor |
| **İhlal 4 (D2)** — ölçüm tablosunun damga sütununda sha yerine faz adı; `--collect-only` geçen/atlanan ayrımı vermez | damgalar **sha**'ya çevrildi, komutlar ayrıştırıldı |
| *(bu turda doğan)* `test_REPORTCARD_…_gizleme_KORUNDU` birebir ifade arıyordu → chip tek sahibe taşınınca **yanlış-kırmızı** | koruyucuya yapısal olarak bakıyor *(bu turda **beşinci** metin-ölçen kapı)* |

**Ertelenen (borç):** `R1` `raporlanabilir`'in ikinci işi (`viewHint` sahipliği, testsiz) ·
`R4` 0.22 kapısının metin penceresi · `R5` `_yururlukte_satirlari` biçim bağımlılığı ·
`R8` chip'lerin maskeli-boyut süzgecini paylaşmaması · `R10` `page.tsx:100`/`ChatPanel:196`.

### FAZ 0 · adım 3 — `0.16` ölçüm bütçesi + koşum hijyeni *(2026-08-04)*

| Parça | Ne indi | Kapı |
|---|---|---|
| **Ayrılmış anahtar** | `DIMA_MEASURE_KEY` (+ `DIMA_MEASURE_PROVIDER`) — ürün trafiğiyle **kota rekabeti biter**. Tanımsızsa davranış **birebir bugünkü** *(GERİ AL)* | `test_OLCUM_ANAHTARI_AYARDA_var` · `test_TANIMSIZSA_BUGUNKU_DAVRANIS` |
| **Kota ön uçuşu** | *"Sağlayıcı kuruldu"* ≠ *"cevap veriyor"*. Tek ucuz çağrı; **429 ya da boş cevap → KOŞMAZ** (fail-closed), hata mesajı çözümü gösterir | `test_KOTA_DOLUYSA_KOSMAZ` · `test_BOS_CEVAP_da_KOSMAZ` |
| **Kaçış kapağı** | Ağ arızası bir turu kilitlemesin diye kapatılabilir — ama **sessiz değil**, *"KORUMASIZ"* diye bağırır | `test_ON_UCUS_KAPATILABILIR_ama_SESSIZ_DEGIL` |
| **Koşum hijyeni** | `--rm` **yasak**, `-d` + `--name` + `docker wait` + `docker rm -f`. *Ölçüldü: `--rm` kütüğü siler ve kabuk ölürse özet **tamamen kaybolur** — bu operasyonda **iki kapı özeti böyle kayboldu*** | `test_KOSUM_HIJYENI_KURALI_YAZILI` |

**Tek sahip:** üçü de `konusma_senaryolari._canli_ortami_geri_yukle`'de — `--live` koşan
**dört aracın dördü de** oradan geçiyor (`deneyim` · `vk_taban` · `nl_accuracy` · kendisi);
tüketicilere tek tek yazmak, dördüncüsünü unutmak demekti. *(Ölçüldü: `faz3a_sema_kazanci`
`--live` yalnız docstring'de geçiyor — içi boş bir canlı mod **yok**.)*

> ⚠ **Kapının kendi kusuru da düzeltildi:** hijyen testi `OPERASYON.md`'yi repo kökünde
> arıyordu ve kapı konteynerine kök **mount edilmediği** için her koşumda `skip` oluyordu.
> **Atlanan bir kapı, kapı değildir** → kural `backend/CLAUDE.md`'ye de yazıldı (her zaman
> mount edilir) ve test iki kaynağı da okuyor.

### 🔵 TEMPO KARARI — **commit ≠ kapı** *(ölçülerek benimsendi)*

Bir turda FAZ 0'ın ~4 maddesi indi ve tam kapı **6 kez** koştu (~90 dk). Ama sürenin
**%75'i kapıda değildi**; madde başına tekrarlanan 10 adımlık döngüdeydi. Ve `--tam`'ın
**dört bileşeninin üçü** o turda **hiç kıpırdamadı**, çünkü onları besleyen dosyalara
dokunulmamıştı. → **Her madde kendi commit'ini alır; tam kapı demet sonunda bir kez.**
**Risk sınırı** (`cube_router · interpret · answer · followup · routers/ask · contribution ·
demo/packs`) demete girmez, kendi kapısını hemen koşar.

**İkinci ağ ölçüldü:** `.github/workflows/backend-ci.yml` her push'ta `pytest -q` koşuyor
ve `tests/test_eval_gate.py` süitin içinde → **eval + süit kapıları CI'da ZATEN VAR**
(`2/4`). 🔴 Bu, önceki turun *"ölçüm kapısı taşıyan 0 workflow"* ölçümünü **çürütür** —
o probe kapıyı **çağıran komuta göre** arıyordu ve başka yoldan koştuğunu göremiyordu
*(ölçüm aracının kusuru, düzeltildi)*. `FAZ 0.15`'in gerçek kapsamı: sıfırdan kurulum
**değil**, mevcut workflow'a **korpus + senaryo** eklemek.

### FAZ 0 · adım 4 — `0.14` beş entegrasyon kapısı *(2026-08-04)*

Kapılar artık **güvenilir**: bu belgenin 100+ maddesi onlara dayanacak.
Ortak iskelet **tek sahipte** (`tests/kapi_ortak.py`) — `0.14`'ün `NASIL`'ı zaten
*"ikinci tarayıcı yazılmaz"* diyordu.

| Kapı | Ne indi | İlk av |
|---|---|---|
| **K1** uç yetimi | **tam yol** eşleştirme (`(?![\w/-])`) + **yorumsuz** tarama + *"sarmalayıcı var, çağıranı yok"* | 🔴 **`GET /contracts`** — alt-dize taraması onu `` `/contracts/${cid}` `` içinde VE bir **yorum satırında** buluyordu. `[KANIT §0.1-5]` kapı tarafından **yeniden üretildi** → FAZ 0.6 |
| **K2** alan yetimi | **(a)** iç içe alanlar · **(b)** `DrillResponse`/`ContributionResponse`/`DecisionIn`/`AskRequest` · **(c)** 🔴 **erişilebilirlik** — *"geçiyor mu"* değil *"ULAŞILABİLİR mi"* | `AskRequest.limit`'in *"tüketiliyor"* sanılması: tek isabet `DrillDownPanel`'deki `limit: 50` = **DrillRequest**; sayaç **sınıf ayrımı yapmıyordu** |
| **K3** ters yetim | **YENİ** — FE'nin okuduğu ama backend'in **vermediği** alan; TypeScript bunu yakalamaz (`types.ts` elle yazılmış bir **beyandır**) | bugün temiz — *kapı temiz kalsın diye kuruldu* |
| **K4** yüzey sadakati | **YENİ** — aynı cevap her yüzeyde **aynı rozeti** basar (MIMARI §5: `source` gizlenemez) | `AnalysisCanvas` rozetsiz → **FAZ 0.3** *(muafiyet SAHİBİYLE, «KALKAR» tarihiyle)* |
| **K5** panel sayısı | **YENİ** — 🔴 **önce TANIM** (export sayımı, `export default` dâhil), sonra sayı, sonra test | **export 13 / tavan 13 · pay 0** — bir panel daha eklenirse anında kırılır |
| **D5** belge kapısı | **YENİ** — `NE`/`KAPI` zorunluluğu · bayraklı maddede `GERİ AL` · *"zaten var"* denen dosya · planlanan kapı sayısı **73** dondurdu | 🔴 **130 maddenin biri** (`−1.2`) `NE`/`KAPI` taşımıyordu — düzeltildi |

> 🔴 **D5'in `GERİ AL` testi `xfail(strict=True)`** — 54 bayraklı maddenin **17'sinde**
> `GERİ AL` yok, **hepsi `II-*`** (v2/v3, bu döngünün dışında). `0.14`'ün kendi kuralı:
> *"Kapı testi geri alınmaz — `xfail` işaretlenir. Bir kapının kırmızısı bir **bilgidir**;
> kaldırıldığında o bilgi de kaybolur."* `strict=True`: 17'si kapandığı gün test
> **beklenmedik geçiş** verir ve işaret kaldırılır.

> ⚠ **Kapı kurarken kapının kendi premisi iki kez kusurluydu** — ikisi de ölçülerek yakalandı:
> · `test_SARMALAYICI_VAR_CAGIRANI_YOK` `ad(` arıyordu → `queryFn: listConversations` gibi
>   **referans** kullanımlarını göremedi, **dört canlı** sarmalayıcıyı *"ölü"* ilan etti.
> · `test_D5_PLANLANAN_DOSYALAR_SAHIPSIZ_DEGIL` *"her planlanan dosyanın bir `KAPI` satırı
>   olmalı"* diyordu ve **metni kovalamaya** başladı (73 → 5 yanlış-pozitif). Ölçülemeyen
>   bir iddiayı zorlamak, kapıyı **yanlış-kırmızı üretecine** çevirir → iddia
>   *"sessizce ARTMAZ"*a daraltıldı.

### FAZ 0 · adım 5 — `0.19` semantik-vaka paydası *(2026-08-04)*

🔴 **ŞİŞME ÖLÇÜLDÜ: 16,2×.** Ham tur paydası bir **kartezyen üründür**
(`ölçü × 11 dönem × boyut`) — yani `elektrik`in **TEK** sahiplik hatası ham paydada
**16 ayrı başarısızlık** olarak sayılıyor. Semantik vaka `(cube, ölçü, niyet)`; dönem ve
boyut çarpımı **tek vakaya çöker**.

| Payda | Değer @`f1050e6` | Not |
|---|---|---|
| **Ham tur** | **%93,2** (6720/7213) | `KURAL A`: **korunur**, geçmiş tabanlar ona bağlı |
| **Semantik vaka** | **%92,1** (410/445) | 🔴 ham sayı **iyimserdi** |

**Sayım KATI (AND):** bir vakanın varyantlarından biri bile yanlış cube'a giderse vaka
**yanlıştır**; Discovery'ye düşmek de bir başarısızlıktır. Gevşek sayım, tek doğru
varyantla bir sahiplik hatasını **gizlerdi**.

> 🔴 **ASIL KAPI — iki payda TERS YÖNE giderse KIRMIZI.** *"Birkaç terimi düzelttim, sayı
> uçtu"* yanılsamasının kapanı: tek bir terimi düzeltmek ham yüzdeyi birkaç puan
> zıplatabilir, **hiçbir yeni semantik vaka kazanılmadan**. **Kanıtlandı:** taban
> ayrıştırıldığında `ÇIKIŞ KODU 1`.

### FAZ 0 · adım 6 — `0.18` METRİK KAYDI = HAKEM *(2026-08-04)*

🔴 **Belgenin tek en büyük ölçülmüş kazancı.** `CLARIFY:konu` %11,5 + yanlış-cube %6,8
≈ **turların ~%18'i**, ve ikisinin de **kanıtlanmış baskın kökü aynı**: bir iş terimi
**iki cube tarafından sahiplenilmiş, hakem yok**. Korpus: boyahane yanlış-cube listesinin
**ilk 10'unun 10'u** `elektrik`; atiksan'ın (**%98, en iyi şirket**) **ilk 9'unun 9'u**
`satış`. Canlı tur aynı sınıfı **bağımsız** buldu: *"bu yıl bakiye"* → `cari` **₺11,86M**,
`mizan` **₺0**.

| Parça | Ne indi |
|---|---|
| **Sınıflandırma** | `app/metrik_kaydi.py` — çakışma envanteri · taslak üretimi · hakem · çift-sahiplik denetimi. **Tek sahip.** |
| **`_match_cube`'un İLK SATIRI** | Paralel yol **değil**: kayıt bir sahip beyan etmişse o kazanır, etmemişse bugünkü zincir **aynen** koşar |
| **Çift sahiplik reddi** | **fail-closed** — iki sahip, hakemsizlikten *daha kötüdür*: hakem yine yoktur ama üstüne *"hakem var"* beyanı eklenir |
| **Sözleşme** | `GET /metrics` — kayıt + çakışan terim envanteri. *(Sahiplik **ekranı** 2.2b'de)* |
| **Bayrak** | `metrik_kaydi = off` → kayıt şemaya **hiç yazılmaz** → `cube_router` görmez → **birebir bugünkü** |

> 🔴 **`cube_router` SAF kaldı.** Bayrak, ayarların erişilebilir olduğu **derleme
> sınırında** (`wren_service.schema()`) durur; sıcak yolda değil. `cube_router` hiçbir
> bayrak okumaz ve bu testle kilitli — sıcak yola bayrak sızarsa determinizm iddiası çürür.

> ✅ **Madde kendi kendine güvenli:** taslak `sahiplenilen_terimler: []` ile gelir, yani
> *"bu terim çakışıyor"* der ama *"sahibi şudur"* **demez**. Karar **FAZ 3.1'in sahiplik
> turudur**. Bu madde **çakışmayı görünür kılar** — görünmeyen bir çakışma düzeltilemez.

> 🔴 **K1 yeni ucu KURULDUĞU ANDA yakaladı:** `GET /metrics` tüketicisiz → `api-only`
> beyanı gerekçesiyle yazıldı. Kapı, kurulmasının üzerinden bir madde geçmeden iş gördü.

### FAZ 0 · adım 7 — `0.5` ÇAPA ZİNCİRİ UYANDI *(2026-08-04)*

**19 altın vakalı, testli bir modül üretimde ÖLÜYDÜ.** `KURAL_CAPA`/`COKLU`/`CELISKI`
hiç ateşlenmiyordu; ölçüldü: `grep -n "capalar=" routers/ask.py` → **0 isabet**.

🔴 **Kök neden engel değil, DÜZLEŞTİRMEYDİ.** `ask.py`'nin yorumu *"thread paneli Faz
H4'te yeniden kurulacak"* diyordu — panel **2026-08-01'de kuruldu**. İstemci çapayı
**zaten biliyordu**, onu **genel `cube_query` yuvasına düzleştiriyordu**; sunucu bu yüzden
hep `KURAL_YAPISAL` görüyordu. *Bayat bir gerekçe kodda kilitli kalmıştı* — madde inerken
yorum da güncellendi ve bu **testle kilitlendi**.

| Parça | Ne indi |
|---|---|
| **sözleşme** | `AskRequest.reply_to_cube_query` + `reply_to_extra_cube_queries` — çapa **kimliğiyle** taşınır; `cube_query` DEĞİŞMEDEN durur |
| **backend** | `coz(..., capalar=…)` bağlandı; tek kart → yanıt, çok kart → **kesişim**, farklı cube → **SOR** |
| **frontend** | `page.tsx` çapayı ve çok-kart seçimini gönderiyor *(`extra_context` insan-okur özet; bu ise **yapısal** sorgu — ayrı alanlar, ayrı iş)* |
| **bayrak** | `capa_zinciri = off` → liste boş → **birebir bugünkü** |

> 🔴 **KAPI KENDİ BOŞLUĞUNU YAKALADI.** İlk koşumda log `kural=capa:karta-yanit` yazıyordu
> ama cevap *"bu takip mesajını ilişkilendiremedim"* diyordu: `coz()` doğru kuralı
> üretiyor, **takip zinciri hâlâ `body.cube_query`'yi okuyordu** — yani çapa **çözülüp
> yok sayılıyordu**. Kullanıcı için sonucu: işaret ettiği karta yanıt verirken cevap
> **başka bir raporun** bağlamına kayıyor, üstelik **sessizce**. Düzeltildi: çözülen çapa
> `KURAL_CAPA`/`KURAL_COKLU`'da **uygulanıyor**; `KURAL_CELISKI`'de **uygulanmıyor** —
> ADR-0008, belirsizlikte tahmin yok.

### FAZ 0 · adım 8 — **ÖLÇÜLMÜŞ YETİMLER KAPANDI** *(0.3 · 0.7 · 0.8 · 0.9 · 0.11)*

[KANIT §0.1]'in envanterinden **beş yetim** kapandı — ve her biri bir **muafiyeti
sildi**. *Yaşayan bir muafiyet, kapının kendisini eritir.*

| Madde | Yetim | Ne yapıldı | Kalkan muafiyet |
|---|---|---|---|
| **0.3** | `AnalysisCanvas` rozetsiz *(SourceBadge 0)* — aynı cevap sohbette `▚ LLM`, tuvalde **rozetsiz** (§5 ihlali) | `ChatPanel.SourceBadge` **yeniden kullanıldı**, ikinci render edici yazılmadı | **K4** `ROZETSIZ_MUAF` → **boş** |
| **0.7** | `runQuery()` sarmalayıcı var, **çağıranı yok** | **Silindi.** Uç duruyor + `api-only` *(ham-SQL yürütme bilinçli olarak kullanıcıya kapalı)* | **K1** `SARMALAYICI_MUAF` → **boş** |
| **0.8** | `agent_run.steps[].receipt` yalnız `types.ts`'te | Adım satırına **⛓ makbuz** — tıklanınca `/contracts/{id}` | `IC_ICE_MUAF` |
| **0.9** | `explain.path` tip var, render yok | Trace bloğuna **yol:** satırı *(rozet «ne» der, yol «nereden»)* | `IC_ICE_MUAF` |
| **0.11** | `DecisionIn.supersedes` **yazılamıyor** | **BAĞLANDI** (silinmedi — II-E.7 ona dayanıyor): revizyon zinciri `PrescriptionLayer`'da | `IC_ICE_MUAF` |

> ⚠ **`AskRequest.execute`/`limit` muafiyeti KALDI — ama gerekçesi DEĞİŞTİ.** Artık
> *"yetim, 0.11'de bağlanacak"* değil: ikisi de `lab/` araçları ve `/ask/verify` için
> **gerçekten kullanılıyor** (SQL üretip **çalıştırmadan** doğrulama). Kaldırmak o yolu
> kırardı. 🔴 Ve K2/(b) burada bir **ölçüm hatası** açığa çıkardı: ham alt-dize taraması
> `AskRequest.limit`'i *"tüketiliyor"* sanmıştı — tek isabet `DrillDownPanel`'deki
> `limit: 50`, yani **DrillRequest**. Sayaç **sınıf ayrımı yapmıyordu**.

### FAZ 0 · adım 9 — `0.12` · `0.13` · `0.6` *(2026-08-04)*

| Madde | Ne indi | Kalkan muafiyet |
|---|---|---|
| **0.12** taban tazeliği | Bugünkü tur tabana eklendi *(kök **dokunulmadı** — KURAL A)* · kapı artık tabanın **yaşını** ve **iki paydayı** kontrol ediyor | — |
| **0.13** sosyal sınıf | 🔴 **Kill-switch GERÇEK oldu:** bayrak `FLAG_REGISTRY` + `features.yml` (`prod`) **ve** `ask.py` gerçekten ona bakıyor. Ad↔iddia çelişkisi + tüketici sayısı (3→**4**) düzeltildi | — |
| **0.6** kanıt geçmişi | `GET /contracts` bağlandı — **`ContractDetailPanel`'in giriş görünümü**, yeni panel **DEĞİL** *(tavan 13/13, pay 0)* | **K1** `/contracts` |

> 🔴 **`0.12` kurulurken KAPI KENDİ KUSURUNU BULDU.** Tabana **şirket rakamı taşımayan**
> bir tur eklenince `_taban_beklenen()` şirket değerlerini **köke (%64)** düşürüyordu —
> yani *bir tur eklemek tabanı SESSİZCE geriletiyordu* ve sonraki kapı 5 puanlık bir
> gerilemeyi **yeşil** görürdü. Kök neden: yalnız **son** tur birleştiriliyordu.
> Artık **tüm turlar sırayla** birleşir (son **beyan eden** kazanır) ve bu
> `test_TUR_EKLEMEK_TABANI_GERILETMEZ` ile kilitli.

> 🔴 **`0.13`'ün asıl borcu bayrağın KENDİSİYDİ.** MIMARI §6.13z/9.11: *"bir kill-switch
> yalnız KOD'da varsa **YARIMDIR**."* Sınıf çalışıyordu ama **geri alma yolu yoktu**.
> Kapı `cube_router`'a değil **çağırana** kondu — `cube_router` hiçbir bayrak okumaz
> (FAZ 0.18'in değişmezi); sıcak yola bayrak sızarsa determinizm iddiası çürür.

> ✅ **Dört muafiyetin dördü de kalktı** (`K1` × 2 · `K4` · `IC_ICE` × 3). Bir muafiyetin
> metni *"…'de KALKAR"* diyorsa, o faz indiğinde **silinmesi** gerekir; yaşayan muafiyet
> kapının kendisini eritir.

### FAZ 0 · adım 10 — `0.10` + `0.10b` GÖRÜNEN ADLAR *(2026-08-04)*

🔴 **Canlı kullanıcı turunun şikâyeti kapandı.** Ekranda şu görünüyordu:
*"En yüksek **tarih__year: 2026-01-01 00:00:00** (454.477,90, toplamın %100,0'i)"* —
kullanıcı: *"Ben yıl sordum, bana **veritabanı sütun adı** ve **saat 00:00** gösteriliyor."*

| Parça | Ne indi |
|---|---|
| **0.10** | `FACT_ICON`'a **`top`** — `interpret` bu fact'i üretiyordu ama sözlükte olmadığı için filtre onu **sessizce eliyordu**. *"En yüksek makine: RAM-2"* bir raporun en çok işe yarayan cümlesidir ve rozet listesinde hiç görünmüyordu |
| **0.10b** | `interpret(..., etiketler=…)` — fact metinleri **görünen ad** basıyor; sözlükte yoksa `tarih__year` → `tarih · year` |

> 🔴 **İKİNCİ ETİKET KAYNAĞI AÇILMADI.** Etiketler `build_catalog`'dan gelir —
> `eylem._rapor_adi` ve `cube_router.next_step_chips` ile **aynı kaynak**.
> `eylem.py:241`'in kendi uyarısı: *"bu depoda «ikinci bir etiket kaynağı» deseni
> **beş kez** ayrışmayla sonuçlandı."* Testle kilitli: `interpret.py` kendi etiket
> kaynağını kuramaz.

> ✅ **`t2_anlatici`'nin SERT ÖN KOŞULU karşılandı.** Bu metin `answer._anlati_ekle`'de
> LLM'e `gercekler` **girdisi** oluyor; `0.10b` inmeden bayrak açılsaydı model
> `toplam_fire_kg` **etrafında cümle kurardı** — akıcı ama iç adlı bir cümle robotikliği
> kaldırmaz, **üstüne para ödetir**.

> ⚠ **Geriye uyum testle kilitli:** `etiketler=None` iken metin **birebir bugünkü**.
> Bir iyileştirme, kendi yokluğunda davranışı değiştirmemelidir.

### FAZ 0 · adım 11 — `0.15` CI KAPILARI · **§C/8 hedefine ulaştı** *(2026-08-04)*

🔴 **Sıralama hatası düzeltildi.** Bu madde başta **FAZ 4.1**'di: regresyon ağı,
belgenin kendi ifadesiyle *"en yüksek etki alanlı faz"* olan **FAZ 2**'nin semantik
ameliyatından **SONRA** kurulacaktı. Oysa `elektrik` deneyi tam orada erişimi
**%64 → %56** düşürmüştü — doktrin (*"düzelt → kapıya çevir"*) **tersine** işliyordu.

**Yeni kod YOK.** Koşucu (`lab/kapi.py --tam`) zaten yazılmıştı; eksik olan onu
**çağıran workflow**du. `.github/workflows/nightly.yml`: gecelik + elle tetik, raporlar
`if: always()` ile yükleniyor *(kırmızıda kanıt kaybolmaz)*.

| §C/8 | Önce | Sonra |
|---|---|---|
| Ölçüm kapıları CI'da | **2/4** *(eval + süit — `pytest -q` içinde)* | ✅ **4/4** |

> 🔴 **Bu maddenin en öğretici kısmı ölçüm aracının kendisiydi.** `olcut_8_ci` probe'u
> **iki kez** yanıldı ve ikisi de aynı sınıftan: *"bir kapıyı, onu ÇAĞIRAN KOMUTA göre
> aramak."*
> · İlk sürüm yalnız `eval.run|nl_corpus|kapi.py` dizelerini arıyordu → `pytest -q`
>   içinde koşan `test_eval_gate.py`'yi göremedi, **"0 kapı"** dedi.
> · Düzeltilince bu kez `kapi.py --tam`'ın **dördünü birden** koştuğunu göremedi,
>   **"korpus eksik"** dedi.
> Doğru ölçüm: **koşucunun NE KAPSADIĞINI** bilmek. `--tam` dört kapının **tek sahibidir**.

> ⚠ **Gecelik, her push'ta DEĞİL** — ve bu testle kilitli. Tam kapı ~15 dk; her commit'e
> bağlamak, demet disiplinini **araç seviyesinde** çiğnemek olurdu.


### 🔴 FAZ 7.3 — **ON ÜÇ ALT MADDENİN DURUMU, MADDE MADDE** *(2026-08-05)*

> *Bir fazı "bitti" ilan edip yarısını söylememek, bitmemiş olmaktan kötüdür.*
> 7.3 tek bir madde değil, **kendi başına bir faz**: on üç alt madde + **altı yeni rota**.

| # | Madde | Durum | Gerekçe / ölçüm |
|---|---|---|---|
| **b** | Landing / boş-durum | ✅ **KAPANDI** | `placeholder` **hiç yoktu** ve sebebi bir unutma değil bir **yapıydı**: `<textarea>` `text-transparent`, ipucu kaplamada çizilmeliydi. Örnekler `/starters`'tan — `HelpPanel`'in **aynı kaynağı** |
| **e** | Her grafik tipinden drill | ✅ **KAPANDI (ayrıştırılarak)** | Üç şekil **aynı sınıf değil**: `scatter` çapası tekil → **kısıt kalktı**; `facet`/`heatmap` **İKİ filtre** ister ve `DrillRequest` tekil → kısıt kalır, ama artık **sebep söylüyor**. Beş erken-çıkışın dördü **sessizdi** |
| **a** | Cevap kartının kanonik anatomisi | ◐ **KISMİ** | 10 katmanlı sıra fiilen var; **üç şeritli İçgörü Kartı** (`NE OLUYOR/NEDEN/NE YAPMALI`) ölçüldü → `OutputInsight`'ta **yok**. Şerit ayrımı `interpret.py`'nin olgu türlerine bir **sınıflandırma** ister |
| **c** | Capability Explorer + komut paleti | ⊘ **YAPILMADI** | Paletin **kendisi yok**; MDL + `MetricDefinition`'dan katalog üretimi + arama motoru — kendi başına bir madde |
| **d** | Kök Neden ön-skorlama | ⊘ **YAPILMADI** | `drill.flag_outliers` z-skoru uzantısı (backend, sıfır-LLM). **PK-13'ün sinyal kaynağı**: koyu/soluk ayrımı bugün *hangi sinyale* dayandığını söyleyemiyor |
| **f** | Yol diyagramlı düğüm notu | ⊘ **YAPILMADI** | Kök-neden yolunun mini diyagramı + reply-to-card iliştirmesi |
| **g** | Kurulum sonu = anında değer | ⊘ **BLOKE** | `/kurulum` rotası yok; **h**'ye bağlı |
| **h** | E-posta doğrulama · şifre sıfırlama · davet uçları | ⊘ **YAPILMADI** | `/register`·`/invite` **backend uçları**. ⚠ Rota yazılıp uç yazılmazsa **mock riski** (7.9) doğar — bu yüzden ikisi birlikte inmeli |
| **i** | Analiz Tuvali iki sabit düğme | ⊘ **YAPILMADI** | Küçük; `AnalysisCanvas`'ta düğmeler koşullu |
| **j** | Pano genişlemesi | ⊘ **YAPILMADI** | Global filtre şeridi + filtre durumunun paylaşılabilir bağlantıya gömülmesi + widget'tan kök-neden |
| **k** | Sarı drift uyarı bandı | ⊘ **YAPILMADI** | **B8'in TEK kullanıcı-görünür yüzeyi** — arkası kurulu, önü yok |
| **l** | 5 grafik tipi | ⊘ **YAPILMADI** | Sankey · Pareto · Bubble · Gauge · **Harita** (harita **yeni veri gereksinimi**: il/ilçe sınırı + koordinat eşleme) |
| **m** | Embed paketi + portföy ekranı | ⊘ **BLOKE** | `6.5/embed` P0'ına bağlı: `motor_cls=off` |
| — | **Altı yeni rota** | ⊘ | `/register` · `/invite/[token]` · `/kurulum` · `/settings` · `/karar-memosu` · `/decisions`. Bugün **5** rota var; PK-22 tavanı 12 |

**FAZ 7.7'nin durumu da ikiye ayrıldı:** kimlik yarısı ✅ (`/auth/me` + `KimlikSeridi`,
ve **tip yalanı** düzeltildi); `/settings` **8 sekmeli tam sayfa** + `admin_app`'in
**13 router'ının** tüketicisi + üç sekme içeriği (sinonim onayı · *"Dima kendini nasıl
geliştiriyor"* · sağlık skoru) ⊘ **YAPILMADI** — `V-1` o 13 router için **kırmızı kalıyor**
ve bu, kapının **beyan edilmiş kırmızısıdır** (0.14/K1 disiplini), gizlenen bir eksik değil.

## FAZ 3 · KAPSAM

## FAZ 4 · ÖLÇÜM ve KANIT

### FAZ 4 · adım 1 — `4.2` **RİSK-KAPSAM EĞRİSİ** — iddia sayıya döndü *(2026-08-04)*

Kapı: **8 test** (`tests/test_risk_kapsam.py`). Yeni araç: `lab/risk_kapsam.py` →
`lab/reports/risk_kapsam.md`.

> **MIMARI §9.1** *"hiçbir sevk edilmiş BI ürünü risk-kapsam eğrisi yayınlamıyor"* diyordu.
> Artık bir **sayı**: deterministik kapsam `gulteks %97,4 · gitas %96,9 · atiksan %94,1`.

> 🔴 **SKALER `confidence` UYDURULMADI.** Eğri kara-kutu bir puan üzerinde değil, **ayrık
> kapılarımız** üzerinde: `route → tie-chip → intent → discovery`. Literatürün kara-kutu
> sinyalleri **0,61–0,68 AUROC**'ta platoluyor; bizimki bir **tahmin değil, mimari
> beyandır** — hangi yoldan geçildiği **ölçülür**.

> 🔴 **`hata_orani` BİLEREK YOK.** Bir kapının hata oranını bu araç **ölçemez** (doğruluk
> korpusun işi); yazsaydık **uydurma** olurdu — ve uydurma bir risk sayısı, risk-kapsam
> eğrisinin **tam tersini** yapardı. Her nokta bunun yerine **determinizm sınıfını** taşır.

> 🔴 **BAĞLAYICI YAN KURAL uygulandı:** `consistency_k` uyumu bir güven eşiğine
> **dönüştürülmedi** — *"bir model son derece self-consistent olup yine de **tutarlı
> biçimde YANLIŞ** olabilir."* Kapı bunu **AST ile** doğruluyor.

> ⚠ **Ölçülemeyen kapıya yazılmadı:** `intent`/`discovery` LLM'siz koşumda ölçülemez →
> `llm_gerekli` kovası. *Ölçülmeyeni bir kapıya yazmak, eğriyi olduğundan iyimser
> gösterirdi.*

> ⚠ **Onuncu kez metin taraması kendi belgemi yakaladı:** `consistency` dizisini arayan
> kapı, onu **kendi yan-kural açıklamasında** buldu → AST'ye çevrildi.

---

### FAZ 3 · adım 7 — `3.6` **COLD-START + GÖRÜNMEZ KOLON** — 🔴 **FAZ 3 BİTTİ** *(2026-08-04)*

Kapı: **12 test** (`tests/test_coldstart.py`), hızlı sinyal **532**.

> 🔴 **GÖRÜNMEZ KOLON — maddenin kapısı birebir:** *"kapatılan kolon üretilen MDL'de
> **YOK**."* Kolon **hiç yazılmaz**, dolayısıyla **LLM onu asla göremez**.
> *"Gösterme" ile "yazma" arasındaki fark bu maddenin bütün değeridir:* gizlenen **ama
> yazılan** bir kolon, bir prompt sızıntısında ya da Discovery sorgusunda **geri gelir**.
> ⚠ `pii.py` maskeler (veri **çıkışında**), burası hiç **üretmez** (şema **girişinde**) —
> iki farklı katman ve **biri ötekinin yerine geçmez**.

> 🔴 **KAPI GERÇEK BİR KUSURUMU YAKALADI.** `gorunur_kolonlar` ilk sürümde
> `ad = ... else k` yazıyordu: kolon bir **nesne** ise (`IntrospectedColumn` — yazıcının
> gerçekte aldığı tip) `str(nesne)` bir ad değil bir **repr** üretiyor, hiçbir zaman
> eşleşmiyor ve **gizleme sessizce çalışmıyordu**. *Çalıştığı sanılan bir kapı, olmayan
> bir kapıdan tehlikelidir* — ve o satır tam olarak bu cümlenin **kendi koduna düşmüş
> hâliydi**. Kullanıcı gizlediğini sanar, kolon MDL'ye yazılırdı.

> ⚠ **AĞIRLIK UYDURULMADI:** önem puanı iki sinyalin **eşit ortalaması**. `0.7 × satır +
> 0.3 × sinyal` gibi **kalibre edilmemiş** bir ağırlık, *"kalibre edilmemiş bir sayı güven
> değil süstür"* kuralının sıralama tarafındaki hâli olurdu. **Eşit ağırlık, bilmediğimizi
> beyan eden ağırlıktır.**
> ⚠ **Sıralama ELEMEZ:** düşük puanlı tabloyu listeden düşürmek, müşterinin **kendi
> verisini göremediği** bir onboarding üretirdi. *Sıralama bir öneridir; gizleme bir
> karardır ve kararı kullanıcı verir.*

### FAZ 3 · adım 6 — `3.5` **YENİ KAYNAK SİSTEMLER** — ⊘ **ÖLÇÜLEMEDİ** *(2026-08-04)*

Kapı: **3 test** (`tests/test_yeni_kaynak_sistemler.py`).

> 🔴 **⊘ ÖLÇÜLEMEDİ olarak kapandı ve nedeni yazılı.** Maddenin kapısı birebir *"zincir
> **gerçek bir müşteri DB'sinde** uçtan uca koşulur"* diyor; bu koşum **canlı bir müşteri
> veri tabanı** ister ve `--network none` altında yapılamaz. *Ölçülemeyeni yeşil saymak,
> "risk yok" yalanı üretir.* Kapı boşluğu **tutuyor**: koşum yapıldığında **ters çevrilir**.

> ⚠ **YOL HARİTASININ SAYISI DÜZELTİLDİ.** Madde *"17 değil, hiç geçmeyen **12**
> konnektör"* diyor. Ölçüldü: motor **15** konnektör taşıyor (`base`/`factory` **altyapı**,
> konnektör değil), backend **4**'ünü kullanıyor → **11** hiç geçmiyor.
> *Bir sayıyı düzeltmek onu küçültmek değildir: 11 konnektör hâlâ "kod yazmadan yeni
> müşteri" demektir.*

### FAZ 3 · adım 5 — `3.4` **APACHE OSSIE İTHALİ** *(2026-08-04)*

Kapı: **21 test** (`tests/test_ossie_ithal.py`), hızlı sinyal **420**.
Bayrak: `ossie_ithal` = **`off`** (kapalıyken uç **404**).

> **Neden:** sektörün fiili standardı (eski adı OSI, Haziran 2026'da **ASF**'e bağışlandı).
> YAML üst-yapıları **bizim `packs/` yapımızla neredeyse birebir** — ve ithal tarafı,
> kapsam tavanına **küratörlük emeği olmadan** saldıran tek kaldıraç.
> ⚠ MIMARI §3.4'ün *"Bilerek ALINMAYANLAR: `osi`"* kararı **bilinçli olarak geri alındı**.

> 🔴 **ÇEVİRİCİ YAZILDI, MOTOR YAZILMADI.** Hedef şekil zaten bizimki:
> `datasets→models` · `metrics→measures` · `fields→dimensions` · **`ai_context→synonyms`**.
> Son eşleme standardın **en değerli** alanı: kullanıcı kelimeleri küratörlük emeği
> olmadan geliyor.

> 🔴 **İTHAL İLİŞKİ `olculmedi` DAMGASIYLA GELİYOR** — ve bu **ekranda söyleniyor**.
> *Bir başkasının modelinin doğru olduğunu **varsaymak**, bu deponun en pahalı hatasının
> (sessiz-yanlış) **ithal edilmiş hâli** olurdu.*

> 🔴 **UÇ YAZMIYOR, ÖNİZLEME ÜRETİYOR.** *Yarım ithal edilmiş bir model, ithal edilmemiş
> bir modelden kötüdür:* katalogda görünür ama sayılarını kimse denetlememiştir. Yazma
> yine sihirbazın `confirm` adımının işi ve oradaki fail-closed kapılardan geçiyor.

> ⚠ **SERBEST METİN SİNONİM SAYILMIYOR:** *"bu bizim aylık toplam sipariş tutarımızdır"*
> bir sinonim değildir. Katalogu cümlelerle şişirmek `_uncovered` kapısını her soruda
> çektirir — yani ithal, **kapsamı artırmak yerine düşürürdü**.

> ⚠ **ADSIZ KAYIT REDDEDİLİYOR** (fail-closed): adsız bir şeyi *"varsayılan"* bir adla
> içeri almak, katalogda **kimsenin arayamayacağı** bir kayıt bırakırdı — ve o kayıt bir
> gün bir soruya cevap olurdu.
> ⚠ **Bilinmeyen sürüm REDDEDİLMİYOR, UYARIYOR:** bir standardın ilerlemesini ithal
> kapısını kapatarak karşılamak kapsamı **dondururdu**.

### FAZ 3 · adım 4 — `3.3` **TERFİ KUYRUĞU KAPANIŞ ORANI** *(2026-08-04)*

Kapı: **14 test** (`tests/test_terfi_kapanis.py`), hızlı sinyal **247**.
Yeni: `app/terfi_kapanis.py` · `GET /measures/candidates/kapanis` · `ReviewPanel` satırı.

> **Ölçülen boşluk:** MIMARI §9 ilke 4 *"her Discovery cevabı bir kapsam boşluğunun
> belgesidir"* diyor ve o belge `MeasureCandidate` olarak kuyruğa giriyor — ama **kaçının
> kapandığını kimse ölçmüyordu**. *Ölçülmeyen bir kuyruk, kuyruk değil bir çöp kutusudur.*

> 🔴 **REDDEDİLEN DE KAPANIŞTIR** — maddenin en kritik kararı. *"Bu bir metrik değil"*
> kararı boşluğun kapandığı anlamına gelir; aday kuyruktan **çıkmıştır**. Yalnız onayları
> saymak, **doğru reddi bir başarısızlık gibi** gösterir ve incelemeciyi **onaylamaya**
> iterdi. Etiket bunu ekranda da söylüyor.

> 🔴 **HİÇ ADAY YOKKEN ORAN `None`, `0.0` DEĞİL.** *"%0 kapanış"* demek, çalışmayan bir
> kuyruğu **başarısız** gibi gösterirdi — *yokluk bir başarısızlık değildir.* Ekran da
> ayırıyor: `⊘ henüz aday yok`.

> ⚠ **Bilinmeyen durum toplama GİRİYOR** ama ne açık ne kapalı sayılıyor — sessizce
> düşürmek oranı **olduğundan yüksek** gösterirdi.

> ⚠ **EŞİK BU TURDA KONMADI ve nedeni yazılı:** eşik bir **iş kararıdır** (haftada kaç
> aday kapatılmalı?) ve **veri olmadan konulamaz**. Ölçüm bugün başlıyor; taban oluştuktan
> sonra eşik bir sonraki turun işi. *Ölçülmemiş bir eşik, uydurulmuş bir hedeftir.*

> ⚠ **Yol sırası tuzağı:** `/candidates/kapanis` uç kaydı `/candidates/{cid}`'den **önce**
> tanımlı — ters olsaydı FastAPI `kapanis`'i bir aday **kimliği** sanardı (ilk eşleşen
> kazanır) ve uç **hiç çalışmazdı**. Kapı sırayı da doğruluyor.

### FAZ 3 · adım 3 — `3.2` **R1 ENVANTERİ** — ölçüm teşhisi DÜZELTTİ *(2026-08-04)*

Kapı: **6 test** (`tests/test_r1_envanteri.py`), hızlı sinyal **917**. Yeni araç:
`lab/r1_envanteri.py`.

> **ÖLÇÜLDÜ — R1 = 170** (dört şirket, 470+ sonda). Yol haritası tabanı 99; payda farklı
> (o bir sonda kümesiydi, bu **şirket başına tüm ölçü sinonimleri**).

> 🔴 **ÖLÇÜM, YOL HARİTASININ TEŞHİSİNİ DÜZELTTİ.** §6.1h *"R1'in **TAMAMI** gerçek
> ölçü-düzeyi belirsizliğidir"* diyor. Dağılım bunu **çürütüyor**:
>
> | aday kümesi | n | gerçekte ne? |
> |---|---|---|
> | `cari` ↔ `mizan` | **42** | 🔴 gerçek belirsizlik → chip (`bakiye` kararı) |
> | `mal` ↔ `ticaret` | **30** | **grain ikizi** (fatura ↔ stok hareketi, 2.1c) |
> | `oee` ↔ `parti` | **20** | grain/kapsam ikizi |
> | `cari` ↔ `cari_finans` | **16** | **türev ikiz** — aynı kavram, iki kimlik |
> | üçlü/altılı kümeler | **18** | jenerik terim (`adet`) |
> | tek sahipli | **18** | sahiplik kararı **kapatır** |
>
> Yani R1'in gövdesi **kullanıcı belirsizliği değil, KATALOG İKİZLİĞİDİR**. *Bir kullanıcı
> "debt" derken iki şey arasında kalmıyor — katalog iki kez aynı şeyi söylüyor.*

> 🔴 **SONUÇ: hedefe (≤30) SAHİPLİK KARARLARIYLA ULAŞILAMAZ** — yalnız **18**'i tek
> sahipli. Kalanın büyük kısmı **modelleme borcudur** (2.4 sınıfı) ve ayrı bir tur.
> *Ölçüm, hedefin yolunu değiştirdi; hedefi düşürmedi.*

> ✅ **ARAÇ KARAR VERMİYOR, RAPOR ÜRETİYOR** — `3.1`'in dersi taze: kararı araç verirse
> bir tenant'ın alan bilgisi hepsine dayatılır ve korpus geriler. Kapı bunu da kilitliyor
> (araçta yazma yolu **yok**).

> ✅ **Sahipsiz terimler artık EKRANDA bir İŞ KALEMİ:** *"N terimin sahibi yok · M tanesi
> için öneri var"*. *Sahipsiz bir terim, yönlendiricinin her seferinde **tahmin** ettiği
> bir terimdir* — sayıyı göstermek onu **görünmez bir borç** olmaktan çıkarır.

### FAZ 3 · adım 2 — `3.1b` **PACK ÖNERİR, TENANT UYGULAR** — bayrak güvenle açıldı *(2026-08-04)*

Kapı: **17 test**, hızlı sinyal **277** · korpus **%93,1** (taban %93,2) ✅.
Bayrak: `metrik_kaydi` → **`beta`** *(öneri modunda güvenli — ölçüldü)*.

> 🔴 **ÖLÇÜM BU ÇÖZÜMÜ ZORLADI.** `3.1`'de pack kararları doğrudan **uygulanıyordu** ve
> korpus geriledi (%93,2→%92,6 · `gitas` %72→%69). Artık pack yalnız **ÖNERİR**
> (`onerilen_sahip`); **uygulayan** tek şey **tenant'ın kendi kararıdır**
> (`MetrikSahipligi`, FAZ 2.2b — zaten tenant kapsamlıydı).

> ✅ **Alan bilgisi KAYBOLMADI, yalnız DAYATILMIYOR.** Öneri ekranda `○ öneri: …` olarak
> görünüyor ve ilgili küpe **tek tıkla** kabul ediliyor — o andan itibaren **tenant**
> kararı olur. ⚠ Aday olmayan bir öneri **hiç gösterilmiyor**: çalışmayan bir şeyi teklif
> etmek, hiç teklif etmemekten kötüdür.

> ✅ **Bayrak güvenle açıldı ve korpusla DOĞRULANDI:** bayrak açık ama tenant kararı
> yokken davranış **birebir bugünkü** (%93,1). Yani `0.18` + `2.2b` + `3.1` zinciri artık
> **atıl değil** — çalışıyor ama **kimseye dayatmıyor**.

> ⟳ **Tuzak ters çevrildi (silinmedi):** *"bayrak `off` kalmalı"* → *"gerileme ölçümü ve
> çözümü yazılı kalmalı"*. Bir sonraki tur pack kararlarını yeniden dayatmayı denerse,
> `%92,6` sayısı orada duruyor.

### FAZ 3 · adım 1 — `3.1` **SAHİPLİK TURU** — kararlar yazıldı, **ÖLÇÜM geri aldırdı** *(2026-08-04)*

Kapı: **13 test** (`tests/test_sahiplik_turu.py`), hızlı sinyal **674**.
Bayrak: `metrik_kaydi` **`off` KALDI** — ölçüm öyle dedi.

> **ÖLÇÜLDÜ — çakışan terim sayısı:** `demo-boyahane` **62** · `gitas` **48** ·
> `gulteks` **39** · `atiksan` **25**. Yol haritasının adlandırdığı vakaların hepsi
> doğrulandı (`bakiye` → cari↔mizan · `arıza duruşu` → bakim↔oee · `alim` → mal↔ticaret).

> **NE indi:** `packs/cekirdek/sahiplik_kararlari.yml` — her karar **kalem · sahip ·
> tarih · gerekçe · kutu** taşıyor. Üç kutu: **(1) tek sahip** (`elektrik`→`enerji_makine`,
> `satis`→`ticaret`) · **(2) gerçek belirsizlik → chip** (`bakiye`, `borc`, `arıza duruşu`
> — sahip **YAZILMAZ**) · **(3) grain hatası** (`yogunluk` → 2.4'ün borcu).

> 🔴 **`bakiye` KORUNDU** — ders kitabı örneği: cari bakiyesi ile mizan bakiyesi **farklı
> sorulardır**; birini seçmek kullanıcının **sormadığı** soruya cevap vermektir.
> ⚠ Ve belirsiz kararı **kayıtta duruyor**: *"henüz bakılmadı"* ile *"bakıldı, belirsiz
> olduğuna karar verildi"* aynı şey değildir — kaybolursa terim her turda yeniden tartışılır.

> 🔴 **BİRİNCİ ÖLÇÜMÜM HİÇBİR ŞEY ÖLÇMEDİ.** `DIMA_METRIK_KAYDI=on` ile korpus koştum,
> *"etki sıfır"* aldım — oysa `metrik_kaydi` bir **YAML bayrağı**, env değil: bayrak hiç
> açılmamıştı. Zinciri doğrudan yoklayınca göründü (`kayıt şemada: False`).
> *Açılmadığını bilmediğin bir bayrağın altında ölçüm yapmak, ölçüm değil varsayımdır.*

> 🔴 **İKİNCİ ÖLÇÜM (bayrak GERÇEKTEN açık) GERİLEME GÖSTERDİ:**
> TOPLAM doğru-cube **%93,2 → %92,6** ❌ · `gitas` erişim **%72 → %69** ❌.
> Yol haritasının kuralı: *"erişim düşerse **GERİ ALINIR**."* **Geri alındı** ve taban
> doğrulandı (%93,1 ✅). Bu bir başarısızlık değil, **kuralın çalışması**.

> 🔴 **TEŞHİS:** kararlar `boyahane`/`atiksan`'ın **ölçülen** kusurları için yazıldı ama
> **pack düzeyinde her şirkete** uygulanıyor. `gitas` (netsis) için `satis → ticaret`
> kararı yanlış olabilir — orada `mal` da meşru bir sahip. *Bir tenant'ın alan bilgisini
> bütün tenant'lara dayatmak, alan bilgisi olmaktan çıkıp **varsayım** olur.*
> → **Çözüm:** kararlar **tenant kapsamlı** olmalı — `2.2b`'nin `MetrikSahipligi` tablosu
> bunu **zaten destekliyor**; pack düzeyi yalnız **taslak** önerir. Ayrı bir tur.

> ✅ **Mekanizma DOĞRU çalışıyor** (bağımsız doğrulandı): `_match_cube("elektrik")` →
> `enerji_makine` (önce belirsizdi). Kusur mekanizmada değil, **kapsamda**.

---

### FAZ 2 · adım 13 — `2.4` **aynı-grain çifti beyan edildi** — 🔴 **FAZ 2 BİTTİ** *(2026-08-04)*

Kapı: **6 test** · korpus **%93,1** (taban %93,2) ✅. Bayrak: `ayni_grain_gocu`.

> **Ölçüldü:** `surdurulebilirlik` ile `parti` **aynı `base_object`** üstünde (`partiler`)
> — iki cube, tek grain. Yoğunluk ölçüleri `parti` grain'ine ait **metriklerdir**.

> 🔴 **KİMLİK SİLİNMEDİ — ve bu ölçülmüş bir karardır.** Ham kaynak adlarını kimlikten
> çıkarmak *"yanlış cube 245→135"* getirdi **ama** erişimi **%64→%56** düşürdü ve
> `test_eval_gate`'i kırdı: iki cube da `elektrik` iddia ediyor → `_match_cube` hiçbirini
> seçemiyor → `R1`. *Doğru çözüm bir **SAHİPLİK KARARIDIR**, kimlik silmek değil.*

> ✅ **VE O HAKEM ARTIK VAR** — `2.2b`'de indi (`MetrikSahipligi` + `hakem`). Bu madde
> yalnız **çifti beyan ediyor** (`ayni_grain: parti` + `departman:` mercek işareti);
> `elektrik`'in sahibini seçmek bir **iş kararıdır** (hangi cube'un metriği?), bir kod
> kararı değil. Sahiplik **boş** olduğu sürece davranış **bugünküyle birebir aynı**.
> *Kullanıcının vermesi gereken bir kararı sistemin vermesi, bu maddenin ölçülmüş kusuru.*

> ⚠ **AYRI BAYRAK** (denetim düzeltmesi): sürüm 1'de `cekirdek_katman`'ı paylaşıyordu →
> `2.4`'ü geri almak `2.1`'i de geri alırdı.

---

## 🎯 FAZ 2 · SEMANTİK ÇEKİRDEK — **BİTTİ** (13 adım, 2026-08-04)

| Madde | Ne indi |
|---|---|
| `2.1` (a·b·c·c2·d + açma kararı) | Çekirdek katman · grain sözleşmesi (fail-closed) · `mdl_diff` · ad göçü · türev katman damgası |
| `2.2b` | Metrik kaydının yüzeyi — **hakem artık beslenebiliyor** |
| `2.3` | Departman = **mercek**, küp değil |
| `2.4` | Aynı-grain çifti **beyan edildi**, kimlik korundu |
| `2.5` | Hedef kıyası — **hedef uydurulmaz** |
| `2.6` | Mali takvim — **sessiz-yanlış kapandı** (bayraksız) |
| `2.7` | Adlandırma sözleşmesi — yalnız yeni küplere |
| borç #11 | Çapraz-cube geçişi **grain-farkında** |

**Korpus tüm faz boyunca sabit: %93,1** (taban %93,2). Hiçbir madde erişimi düşürmedi.

### FAZ 2 · adım 12 — `2.3` **DEPARTMAN = MERCEK, KÜP DEĞİL** *(2026-08-04)*

Kapı: **16 test** (`tests/test_kapsam_mercegi.py`), hızlı sinyal **520**.
Bayrak: `kapsam_mercegi` = **`off`** (varsayılan: bugünkü tam katalog).

> **Neden küp değil mercek:** *"Bize bir satış küpü lazım"* isteğinin meşru karşılığı bir
> **kapsam parametresidir** (Plan 3 §7.8). Bir departmanı küp yapmak, o departmanın **tüm
> sözlüğünü** kimliğe yapıştırır — `surdurulebilirlik` felaketinin kökü buydu (%64→%56).

> 🔴 **MERCEK GÜVENLİK SINIRI DEĞİL** — maddenin en kritik değişmezi. Kapı bunu
> **tersinden** ölçüyor: her kapsam × her departman kombinasyonunun çıktısı, mercek
> kapalıyken görünen kümenin **alt kümesi** olmak zorunda. *Merceği bir güvenlik katmanı
> gibi kullanmak, "kapsamı genişlet" düğmesini bir YETKİ YÜKSELTME aracına çevirirdi.*

> 🔴 **YOL HARİTASINDAN SAPMA — ve gerekçesi ölçüldü.** Yol haritası `AskRequest.scope`
> diyor; merceği **cevaplama yoluna** bağlamak, *aynı sorunun kapsam değişince farklı sayı
> döndürmesi* demekti. Mercek **`/schema`**'ya (katalog) bağlandı: kullanıcının **gördüğü
> küme** değişir, **aldığı sayı** değişmez. Ve **yetim-alan kapısı bunu doğruladı** —
> alanı `AskRequest`'e koyduğumda tüketicisi olmadığı için kırmızı verdi.
> *Bir sözleşme alanı, tüketicisi olmadan yalnız bir vaattir.*

> 🔴 **UYDURMA İZİN ADI — kapı yakaladı.** `portfoy` için `"tenant:read_all"` diye bir
> izin **uydurmuştum**; matriste öyle bir eylem yok. *Var olmayan bir izne dayanan kontrol,
> hiç yapılmayan bir kontroldür:* `izinli_mi` her zaman `False` döner, `portfoy` **hiç
> kimseye** açılmazdı. Deponun çok-tenant sınırı `is_superadmin`'dir (ADR-0015 K7).

> ⚠ **Ataması olmayan küp GİZLENMİYOR:** atanmamışlık bir *"gizle"* kararı değildir —
> sessizce gizlemek, kullanıcının katalogdan **haberi olmamasına** yol açardı.

> ⚠ **Bayrak kapalıyken anahtar HİÇ ÇİZİLMİYOR:** *bir görünürlük aracı, kapalıyken
> kullanıcıya var olduğunu bile söylememelidir.* Ve kapsam React Query **anahtarında** —
> olmasaydı mercek değişince önbellekten **eski katalog** dönerdi.

> ⚠ **YAML tuzağı:** `kapsam_mercegi: off` çıplak yazılınca YAML 1.1 onu **boolean**
> okuyor; bayrak kaydı kapısı yakaladı, tırnak eklendi.

### FAZ 2 · adım 11 — `2.5` **HEDEF KIYASI** — hedef UYDURULMAZ *(2026-08-04)*

Kapı: **14 test** (`tests/test_hedef_kiyasi.py`), hızlı sinyal **1148**.

> ⚠ **NEYİN KUSUR OLMADIĞI ÖNCE ÖLÇÜLDÜ.** Yol haritası *"grafikteki referans çizgisi
> hedef değil ORTALAMA"* diyor. Ölçtüm: `viz.py` çizgiyi `{"kind": "average"}` üretiyor ve
> `chart.ts` onu **`Ort.`** diye etiketliyor — yani **yanlış etiketleme YOK**, sistem
> bugün dürüst. Eksik olan **mekanizmanın kendisiydi**: `target:` beyanı hiçbir cube'da
> yoktu, kullanıcı *"hedefimin altında mıyım"* diye **soramıyordu**.

> 🔴 **DEĞİŞMEZ: HEDEF UYDURULMAZ.** Beyan yoksa bayrak açık olsa bile hedef çizilmez ve
> etiket `Ort.` kalır. *"Hedef yok"* ile *"hedef 0"* asla karıştırılmaz — **sıfır hedef
> ULAŞILMIŞ bir hedeftir**, hedefsizlik ise **ölçülemezliktir**. Bozuk bir beyan da
> **beyan yok** sayılır; `0` kabul etmek o ayrımı yok ederdi.

> ⚠ **Sıfır hedefte sapma yüzdesi `None`** — `inf`/`0` yazmak, bir **tanımsızlığı** bir
> ölçüm gibi gösterirdi.

> 🔴 **BELİRSİZLİK SESSİZCE ÇÖZÜLMÜYOR:** iki ölçülü bir raporda *"hangi hedef"* sorusunun
> cevabı **yoktur** → blok `None`. Birini seçmek, kullanıcının **sormadığı** bir kıyası
> cevabın yerine koymak olurdu.

> ✅ **YÖN İKİNCİ KEZ BEYAN EDİLMİYOR:** `lower_is_better`'dan **türüyor** — ikinci bir
> yön beyanı, biri *"85 iyi"* derken ötekinin *"85 kötü"* göstermesi demekti.

> ✅ **ALTI ÇAĞRI YERİNE DOKUNULMADI:** hedefler `viz.meta_args`'a eklendi — o fonksiyonun
> var olma sebebi tam olarak bu (bir alanın beşinci çağıranını unutmak imkânsız olsun diye).

> ⚠ **KAPSAM SINIRI YAZILI:** yol haritası `MetricTarget`'ı SCD-2 tanımlıyor (kapsam ·
> tarih · `as_of` yeniden oynatma). Bu dilim **yalnız beyan yolunu** açtı; kişi/şube
> kapsamlı ve tarihli hedefler **ayrı bir dilim** ve o gelene kadar **uydurulmuyor**.
> *Yarım inmiş bir mekanizmayı tam gibi göstermek, hiç indirmemekten kötüdür.*

### FAZ 2 · adım 10 — `2.7` **adlandırma sözleşmesi** *(2026-08-04)*

Kapı: **8 test**. Var olan adlar **kalıyor** — toplu yeniden adlandırma **ölçümle
reddedildi** (%64→%56, 388 cevap kaybı). Kural yalnız **yeni** küplere: olayla + tekil;
departman adı küp adı **olamaz** (departman bir **mercektir**).

> ⚠ **Taban kümesini elle TAHMİN etmiştim ve kapı beni yakaladı:** listem `personel`/
> `stok`/`satis` gibi **var olmayan** küpler içeriyor, `enerji_*` üçlüsünü ise
> **kaçırıyordu** — kapı onları *"yeni doğmuş"* ilan etti. *Beyan var, sayım yok.*
> Liste artık **ölçümden** geliyor (16 küp).

### FAZ 2 · adım 9 — `2.6` **MALİ TAKVİM** — ölçülen sessiz-yanlış kapandı *(2026-08-04)*

Kapı: **18 test** (`tests/test_mali_takvim.py`), hızlı sinyal **1483**. **Bayraksız.**

> 🔴 **NEDEN BAYRAKSIZ:** ölçülen şey bir **sessiz-yanlış**. `"bu yıl"` iki yerde birden
> takvim yılı varsayılıyordu — `cube_router._current_period_filter`
> (`today.replace(month=1, day=1)`) ve `yoy.compute` (`f"{yıl}-01-01"`). Mali yılı
> Ocak'ta başlamayan her müşteride cevap **yanlış**, ama rozet `◆ CUBE`, güven `1.0`,
> makbuz **tam**. *Sessiz-yanlışın tanımı budur: sistem emin, sayı yanlış.* Bir bayrağın
> arkasına koymak, **yanlışı varsayılan yapmak** olurdu.

> 🔴 **İKİ KOPYA, KUSURUN DOĞUŞ BİÇİMİYDİ.** Hesap tek sahibe alındı
> (`app/mali_takvim.py::yil_penceresi`); iki çağıran da onu **çağırıyor**.
> ⚠ Bitiş `12-31` **sabiti değil**, *"bir sonraki mali yılın ilk gününden bir gün önce"* —
> sabit yazmak, Ocak'ta başlamayan bir mali yılda pencereyi **bir çeyrek kaydırırdı**.

> ⚠ **YENİ MEKANİZMA İCAT EDİLMEDİ.** `date_filters(q, time_dim)` imzası beş çağıran
> taşıyor; mali ayı parametre yapmak hepsini kırardı. Bu deponun **iki kez kanıtlanmış**
> kalıbı (`llm._llm_usage_var` · `cube_router._reddi_var`) **üçüncü kez** kullanıldı:
> derin fonksiyon okur, sığ fonksiyon kurar, imzalar sabit kalır.

> 🔴 **AYAR `wren_for_request`'te KURULUYOR** — veriye giden **her** yolun geçtiği tek
> nokta. Başka bir yere koymak, bazı yolların onu **görmemesi** ve sessizce takvim yılına
> düşmesi demekti; yani tam olarak kapatılan kusura.

> ✅ **VARSAYILAN `1` = takvim yılı:** yapılandırılmamış her tenant **bugünkü** davranışı
> görüyor. *Bir düzeltme, düzeltmediği kurulumları değiştirmemelidir.*

> 🔴 **KULLANICI PENCEREYİ GÖRÜYOR:** `AskResponse.mali_donem` (yalnız takvimden
> **farklıysa** dolar) → `ReportCard`'da `◷ mali yıl: … → …`. *Takvim yılından farklı bir
> pencereyi "bu yıl" diye sunmak, doğru sayıyı yanlış soruya cevap yapar.*

> ⚠ **§C/3 kesişimi korundu:** bu madde dönem **çözümünü** değiştirir, **netleştirme
> oranını değil** — kapı `_current_period_filter`'ın `return None` dalının durduğunu ve
> mali takvimin o **karara** karışmadığını AST'ten doğruluyor.

> ⚠ **Kendi yorumum kendi kapımı yakaladı (8. kez):** `f"{date.today().year}-01-01"`
> dizisini arayan kapı, onu **kendi açıklama yorumumun içinde** buldu. AST'ye çevrildi.
> Ve `1.2c` tümleyeni yine iş gördü: `AskResponse` **31 → 32** alan oldu, maskeleme
> tarafına **hiçbir şey yazılmadı**, yine de kapsandı.

### FAZ 2 · adım 8 — `2.2b` **metrik kaydının YÜZEYİ: hakem artık BESLENEBİLİYOR** *(2026-08-04)*

Kapı: **11 test** (`tests/test_metrik_sahipligi.py` — 2.2b'nin **kendi** kapısı, 0.18'inki
değil), hızlı sinyal **592**. Bayrak: `metric:certify` yetkisi (yeni bayrak **yok**).

> 🔴 **0.18 KENDİ KENDİNE ATILDI — ölçüldü.** Hakem (`metrik_kaydi.hakem`) kurulmuştu ama
> kayıt katalogdan **taslak** üretiliyor ve `sahiplenilen_terimler` **boş** başlıyordu;
> boşu dolduracak bir yol **yoktu**, yani hakem **hiçbir zaman** karar veremezdi.
> *Kurulmuş ama beslenemeyen bir hakem, kurulmamış bir hakemdir.*

> **NE indi:** `MetrikSahipligi` (kalıcı sahiplik) · göç `a1d7f4c8e250` ·
> `metrik_kaydi.sahiplikle_birlestir` · `PATCH /metrics/{terim}` ·
> ekran (**yeni panel YOK** — `SchemaPanel`'in içinde bir bölüm).

> ⚠ **ALAN LİSTESİ BİLEREK DARALTILDI.** Yol haritası `display_name · unit · rounding ·
> description · target_ref` da sayıyor; hepsi **cube YAML'ında zaten var** ve oradan
> şemaya akıyor. DB'ye kopyalamak *"aynı kuralın iki sahibi"* olurdu — biri güncellenir,
> öteki unutulur ve kullanıcı hangi birimin doğru olduğunu bilemez. **DB'nin eklediği tek
> yeni bilgi SAHİPLİKTİR:** çakışan bir terimi hangi cube'un sahiplendiği bir **karardır**,
> katalogdan türetilemez. Kapı bu daraltmayı ve gerekçesini kilitliyor.

> 🔴 **ADAY OLMAYAN SAHİP SESSİZCE YUTULMUYOR.** Kayıtta aday olmayan bir cube'u sahip
> yazmak **hiçbir şey yapmazdı** (hakem onu döndürse `_match_cube` bulamazdı). Karar
> **kaydedilir ama uygulanmaz** ve ekranda `⚠ geçersiz` olarak **görünür**.
> *Sessizce yok saymak, kullanıcının kararını çöpe atıp ona söylememektir.*

> ⚠ **Sahiplik kaldırılınca kayıt SİLİNMİYOR** — *kararın geri alındığı da bir kayıttır*:
> kim, ne zaman geri aldı görülebilmeli. Her karar ayrıca **audit'e** yazılıyor.

> 🔴 **YENİ PANEL AÇILMADI** (K5 tavanı **13/13**, ölçüldü): sahiplik bir **katalog**
> bilgisidir (*"şu terim hangi cube'a ait"*) ve yeri kataloğun kendisi. Ayrı bir ekran,
> kullanıcıyı aynı soruyu **iki yerde** aramaya iterdi.

> ⚠ **ÖLÇÜLEN KUSUR — 222 test birden düştü.** FK'yi `user.id` yazmıştım; tablo adı
> **`app_user`** (`user` PostgreSQL'de ayrılmış sözcük ve bu depo onu bilerek yeniden
> adlandırmış). FK çözülemeyince **tüm** metadata kurulumu patlıyor — yani tek bir yanlış
> ad, ilgisiz 222 testi düşürüyor. Model ve göç düzeltildi; gerekçe modelin yanında yazılı.

### FAZ 2 · adım 7 — **BORÇ #11 KAPANDI**: grain-farkında çapraz-cube geçişi *(2026-08-04)*

Kapı: **37 test** (`test_cekirdek_katman.py`) + `test_kpi.py`, hızlı sinyal **1326**.
🔴 Risk sınırı (`cube_router` · `routers/ask.py` · `demo/packs`) → kendi korpus kapısı.

> **Kendi açtığım yetenek kaybını kapattım.** Ad göçü `cross_cube_dim_switch`'i kırmıştı:
> *"ürün bazlı satış"* cevaplanamıyordu. Şimdi çalışıyor — ama **doğru** biçimde.

> 🔴 **EŞLEŞME ARTIK AD DÜZEYİNDE DEĞİL, KAVRAM DÜZEYİNDE.** Ölçüler `cekirdek_metrik`
> bağıyla eşleşiyor (`mal.satis_tutari_hareket` ↔ kavram `satis_tutari`) ve şema bunu
> `units`/`lower_is_better` ile **aynı yan-harita deseniyle** taşıyor — ikinci bir sözlük
> **yok**, kaynak hâlâ cube YAML'ı.

> 🔴 **GRAIN DEĞİŞTİYSE CEVAP BUNU SÖYLÜYOR.** *Sessiz bir grain değişimi, sessiz bir
> yanlıştır.* Kullanıcı *"ürün bazlı satış"* dediğinde cevabı alıyor **ama** aldığı sayının
> başka bir **taneliğe** ait olduğunu da görüyor (`— ⚠ ölçünün TANELİĞİ değişti …; iki sayı
> doğrudan kıyaslanamaz`). Uyarı **var olan** konu-değişimi notunun içine giriyor: yeni
> alan, yeni panel, yeni uç **yok**.

> 🔴 **KIYASLANAMAZ ölçüye ASLA geçilmiyor.** `karlilik` de `stok_adi` taşıdığı için geçiş
> oraya düşebilirdi; `satis_tutari_turev`'in grain'i ERP'ye göre değişir ve oraya geçmek,
> kullanıcıya *"aynı şeyin kırılımı"* diye **başka bir şeyi** göstermek olurdu.

> ⚠ **BELİRSİZLİK SESSİZCE ÇÖZÜLMÜYOR:** hedef cube aynı kavramın **iki** varyantını
> taşıyorsa geçiş **reddediliyor**. Birini seçip ötekini yok saymak, tam olarak bu maddenin
> engellemek için var olduğu şeydir.

> ✅ **TAŞINABİLİR OLAN HER ŞEY TAŞINDI:** `olcu_eslemesi` + `grain_uyarisi`
> `app/cekirdek.py`'de — *"bu iki ölçü aynı kavramın farklı grain'i mi"* sorusu **çekirdek
> katmanın** sorusudur, router'ın değil. `cube_router`'da kalan yalnız **çağrı** (muafiyet
> 5 satır), `ask()`'te kalan yalnız uyarıyı **cevaba taşıyan** satır (muafiyet 1).

### FAZ 2 · adım 6 — `2.1` **AÇMA KARARI: `off` KALDI, ölçümle** — 🔴 **`2.1` BİTTİ** *(2026-08-04)*

> **Ölçüldü** (`DIMA_CEKIRDEK_KATMAN=on python lab/kapi.py --tam`):
>
> | | `off` | `on` |
> |---|---|---|
> | TOPLAM doğru-cube | %93,1 | **%93,1** |
> | `gitas` doğru/payda | 1515/1694 | 1517/1696 |
> | semantik vaka | %91,5 | %91,7 |
>
> **Kazanç ölçülemedi** → yol haritasının karar kuralı (§C) gereği bayrak **`off` kalıyor
> ve nedeni yazılıyor**. Bu bir unutma değil, ölçülmüş bir karar; kapıyla kilitli.

> ⚠ **SÖZLEŞMENİN DİŞLERİ BAYRAĞA BAĞLI DEĞİL.** Grain ihlallerini `on` beklemeden
> `tests/test_cekirdek_katman.py` (**34 test**) + `lab/mdl_diff.py` yakalıyor — ikisi de
> bayraktan **bağımsız** koşar ve türev katmandaki **gizli ihlali bulan da tam olarak
> buydu**. *Bir sözleşmenin değeri, uygulandığı anda değil, İHLALİ GÖRÜLDÜĞÜ anda başlar.*

### FAZ 2 · adım 5 — `2.1(d)` **türev katman: sürüklenme BİR KAT YUKARIDA tekrar üretiliyordu** *(2026-08-04)*

Kapı: **35 test**, hızlı sinyal **328**. 🔴 Risk sınırı (`demo/packs`).

> 🔴 **KAPIYI KÖR EDEN ŞEY, ONUN KENDİ GÜVENLİ VARSAYIMIYDI.** `karlilik` türev küpü aynı
> sürüklenmeyi bir kat yukarıda tekrar üretiyordu — `base_model` mikro'da
> `stok_hareketleri`, logo-3'te `fatura_satirlari`, netsis'te `stok_hareketleri`. Ama
> küpün `base_object`'i **türetilmiş görünüm adıdır** (`karlilik_src`) ve o ad hiçbir
> sözleşmede geçmez → *"bilinmeyen grain SERBEST"* kuralı **gerçek bir ihlali koruyordu**.
> `compose` artık türev küpe kaynağın `base_model`'ini **damgalıyor** (`grain_kaynak`).

> **KARAR:** `karlilik.satis_tutari` → **`satis_tutari_turev`** — dördüncü kimlik.
> Kanonik ad **olamaz** (hiçbir ERP'de fatura grain'inde değil), `_hareket`/`_kalem` de
> olamaz (grain'i **sabit değil**, ERP'nin bağlamasına bağlı). Grain **bilinçli olarak
> beyan edilmiyor** ve bu bir eksiklik değil, **ölçülen gerçeğin kaydı**.
> 🔴 `kiyaslanamaz: true` — *iki şirketin bu sayısını yan yana koymak, iki farklı şeyi
> karşılaştırmaktır.* Kârlılık hesabının **girdisidir**, bir satış cirosu değil.

> ⚠ **ÖLÇÜLEN YETENEK KAYBI — gizlenmiyor.** `cross_cube_dim_switch` **ada** bakıyordu:
> `ticaret.satis_tutari` + *"ürün bazlı"* → `mal`/`karlilik`'in `satis_tutari`'sine
> geçiyordu. O ad **üç ayrı grain** taşıyordu; yani mekanizma **karşılaştırılamaz iki
> sayıyı** sessizce aynı raporun içine koyuyordu — üstelik `source="cube"` rozetiyle.
> Ad göçü bunu **yapısal olarak imkânsız** kıldı: geçiş artık `None` dönüyor ve *"ürün
> bazlı satış"* bu yoldan cevaplanmıyor.
> *Sessizce yanlış bir sayı vermektense, açıkça cevap verememek yeğdir.*
> **Borç:** geçişi **grain-farkında** yap (çekirdek sözlüğün varyant bilgisini sorgu
> zamanında oku) ve cevabın grain değiştirdiğini **SÖYLE**.

### FAZ 2 · adım 4 — `2.1(c2)` **AD GÖÇÜ** — sözleşme artık dört şirkette de uyuyor *(2026-08-04)*

Kapı: **31 test** · korpus **%93,1** (taban %93,2) ✅. 🔴 Risk sınırı (`demo/packs`).

> **Göç (tek atomik adım):** `mikro-v16/ticaret.satis_tutari` → `satis_tutari_hareket` ·
> `netsis/mal.satis_tutari` → `satis_tutari_hareket` · `logo-3/mal.satis_tutari` →
> `satis_tutari_kalem`. `ticaret`@fatura (logo-3 · netsis) **dokunulmadı** — sözleşmeye
> zaten uyuyordu.

> 🔴 **SİNONİMLER DEĞİŞMEDİ.** Kullanıcı hâlâ *"satış"* / *"ciro"* / *"satış tutarı"* diye
> sorabiliyor; değişen yalnız metriğin **kimliği**. *Bir kullanıcıyı kendi kelimesinden
> etmek, sözleşmenin amacı değildir.* Kapı bunu ölçüyor: göç edilen her ölçünün sinonim
> listesi **boşalmamış** olmalı.

> ✅ **Sözleşme artık DÖRT şirkette de uyuyor** — `cekirdek_katman=on` açılabilir hâle
> geldi (gölge diff: dördünde de **sayı-etkisi 0 fark**). Bayrak yine de `off` kalıyor:
> açma kararı ayrı bir maddedir ve `shadow` turu görülmeden açılmaz.

> ⚠ **ÖLÇÜLEN YAN ETKİ — gizlenmiyor.** `gitas` (netsis) korpusunda payda **1703 → 1694**
> (−9 soru) ve erişim **%73 → %72**; semantik vaka paydası **445 → 446**, doğruluk
> **%91,7 → %91,5**. Sebep yapısal: `netsis`'te `satis_tutari` **iki cube'da** vardı
> (`ticaret` ve `mal`) ve korpus üreteci soruları katalogdan türetiyor — ad ayrışınca
> üretilen soru kümesi değişti. **Kapı yeşil** (her şirket kendi tabanında ya da üstünde,
> TOPLAM %93,1 sabit) ama bu bir *"hiçbir şey olmadı"* değil: **9 soru yer değiştirdi** ve
> bunu yazmamak, paydanın sessizce oynamasına göz yummak olurdu — korpusun var olma
> sebebinin ta kendisi.

### FAZ 2 · adım 3 — `2.1(c)` **`ticaret` GRAIN KARARI** — karar kalemi · sahip · tarih *(2026-08-04)*

Kapı: **31 test**. 🔴 **Risk sınırı** (`demo/packs`) → kendi korpus kapısını koştu.

> 🔴 **ÖLÇÜM, YOL HARİTASININ TEŞHİSİNDEN AĞIR ÇIKTI.** Yol haritası *"`ticaret` üç ERP'de
> farklı grain"* diyordu. Sayım **üç grain / beş cube** gösterdi:
>
> | cube | `base_object` | grain |
> |---|---|---|
> | `logo-3/mal` | `fatura_satirlari` | **fatura kalemi** |
> | `logo-3/ticaret` | `faturalar` | fatura |
> | `mikro-v16/ticaret` | `stok_hareketleri` | stok hareketi |
> | `netsis/mal` | `stok_hareketleri` | stok hareketi |
> | `netsis/ticaret` | `faturalar` | fatura |
>
> ⚠ **Ve ayrışma ŞİRKET İÇİNDE:** `gitas` (netsis) tek başına `satis_tutari`'yi hem
> `ticaret`@fatura hem `mal`@stok_hareketi olarak taşıyor — aynı ad, aynı sinonim
> (`satış`, `ciro`), **iki farklı sayı, aynı şirkette**. *"Bu yıl satış"* sorusunun cevabı
> yönlendiricinin hangi cube'u seçtiğine bağlı. Bu, şirketler arası sürüklenmeden **daha
> kötüdür**: kullanıcı iki sayıyı yan yana bile göremez.

> **KARAR** — `satis_tutari` **kanonik grain = `fatura`**. *Gerekçe:* satış ticari olarak
> **faturayla doğar**; stok hareketi bir **sonuçtur** (ve iptal/iade faturada görünür,
> hareket kaydında her zaman değil). Karşı grain'ler **ayrı metrik** olarak kayıtlı —
> `satis_tutari_hareket` @stok_hareketi · `satis_tutari_kalem` @fatura_kalem. *Tek metrik
> iki anlama BÜKÜLMEZ.* **Sahip:** ad göçü ayrı bir tur (NL yönlendirmesini değiştirir,
> kendi korpus ölçümünü ister). **Tarih:** 2026-08-04.

> 🔴 **SÖZLEŞMENİN KENDİ İÇİNDEKİ HATA — ölçümle bulundu.** İlk yazımda `fatura_kalem`,
> `fatura` grain'inin **takma adları** arasındaydı: yani *"fatura"* ile *"fatura kalemi"*
> aynı sayılıyordu. Değiller — bir faturanın **çok** kalemi olur ve kalem düzeyinde
> toplanan tutar, fatura düzeyindekinden farklı olabilir (satır bazlı iskonto/iade).
> *Bu, sözleşmenin engellemek için var olduğu hatanın, sözleşmenin kendi içindeki hâliydi.*

> ✅ **KARAR BUGÜN KAPIYI ATEŞLİYOR — ve bu istenen davranış.** `cekirdek_katman=on` iken
> üç şirketin üçünde de `compose()` **reddediyor** ve **hangi cube** olduğunu tek tek
> söylüyor (`gitas: mal.satis_tutari` · `atiksan: ticaret.satis_tutari` · `gulteks:
> mal.satis_tutari`). Bayrak `off` olduğu için bugünkü derleme etkilenmiyor; **ad göçü
> inene kadar `on` AÇILAMAZ** ve bu bir eksiklik değil, **kilidin kendisidir**.
> *Bir sözleşmeyi, ihlal edildiği için yazmamak, ihlali sözleşme yapmaktır.*

> ⟳ Kabul ölçütü **anlam değiştirdi, gevşemedi**: *"`on`'da sayı-etkisi 0"* ölçütü
> `demo-boyahane`'de (ERP pack'i yok) **aynen duruyor**; üç ERP şirketinde ise ölçüt artık
> *"sözleşme ateşliyor mu"*. Gölge diff aracı `GrainIhlali`'yi **ölçüm hatasından ayırıyor**
> — çalışan bir kapıyı *"ölçülemedi"* diye raporlamak, onu bir arıza gibi gösterirdi.

### FAZ 2 · adım 2 — `2.1(b)` **`cari`: grain sözleşmesi GERÇEK pack'lerde ateşliyor** *(2026-08-04)*

Kapı: **29 test**, hızlı sinyal **262**. Gölge diff: **sayı-etkisi 0** · sözlük **7·14·9·11**.

> **Neden `cari` ile başlandı:** üç ERP'de de **aynı grain** (cari hareket), **aynı ölçü
> adları**; farklı olan yalnız **ifade**. Yani sözleşmeyi burada beyan etmek **risksiz** ve
> kapı gerçek veri üstünde **çalıştığını** kanıtlıyor. `ticaret` uymuyor — bilerek adım (c).

> 🔴 **KAPI SESSİZCE KAPALIYDI — ve ölçüm onu gösterdi.** `cari_hareket` sözleşmesinin
> `base_object` listesinde gerçek adlar (`cari_hareketleri` · `cari_hesap_hareketleri`)
> **yoktu**; `grain_adi()` üçünde de `None` dönüyordu, yani kapı **ARMED görünüp hiç
> ateşlemiyordu**. *Tanımadığı bir tabloyu "serbest" sayan bir kapı, sessizce kapalı bir
> kapıdır.* Adlar **ölçülerek** eklendi, tahmin edilmedi.

> 🔴 **ÖLÜ SÖZLÜK GİRDİLERİ.** İlk sözlükte `borc_toplami`/`alacak_toplami` yazıyordu;
> cube'lardaki gerçek adlar `toplam_borc`/`toplam_alacak`. Eşleşme **adla** olduğu için o
> iki girdi **hiçbir şeye dokunmuyordu**. *Kimseyle eşleşmeyen bir sözlük girdisi,
> yazılmamış bir girdiyle aynı şeydir.* Yeni kapı: her çekirdek metrik **en az bir**
> gerçek cube ölçüsüyle eşleşmek zorunda.

> ⟳ **Tuzak ters çevrildi (silinmedi):** *"hiçbir metrik grain beyan etmiyor, kapı
> ateşlemiyor"* → *"`cari` metrikleri beyan ediyor ve üç ERP'nin üçü de uyuyor"*.
> `satis_tutari`'nın beyan **etmediği** ise ayrı bir kapıyla korunuyor: bugün beyan etmek,
> üç ERP'den ikisini **derleme zamanında reddetmek** demekti. *Yazılmamış bir kararı kapıya
> çevirmek, kararı vermiş gibi yapmaktır.*

### FAZ 2 · adım 1 — `2.1(a)` **çekirdek katman + grain sözleşmesi kapısı** *(2026-08-04)*

Kapı: **25 test** (`tests/test_cekirdek_katman.py`), hızlı sinyal **929**.
Bayrak: `cekirdek_katman` = `off|shadow|on`, **varsayılan `off`**.
🔴 **Risk sınırı** (`demo/packs`) → kendi korpus kapısını koştu.

> **Ölçülen kusur — ve doğrulandı:** `ticaret` cube'u **üç ERP'de** aynı adı, aynı
> sinonimi ve aynı ölçü adını (`satis_tutari`) taşıyor ama **farklı grain**'de:
> mikro-v16 → `stok_hareketleri`, logo-3 · netsis → `faturalar`. Yani *"bu yıl satış"*
> üç şirkette **karşılaştırılamaz üç sayı** döndürüyor ve **hiçbir yerde beyan yok**.
> *Aynı adı taşıyan iki sayının farklı şeyler olduğunu söylemeyen bir semantik katman,
> semantik katman değildir.*

> ✅ **KABUL ÖLÇÜTÜ ÖNCE — ve tuttu.** `lab/mdl_diff.py` (yeni) gölge derleme yapıyor:
> `off` ↔ `on` iki MDL, karşılaştırma birimi **cube × ölçü × boyut × ifade × `additive`**.
> Ölçüldü
> (`python lab/mdl_diff.py`): **dört şirketin dördünde de sayı-etkisi 0 fark**; sözlük
> zenginleşmesi `demo-boyahane 2 · gitas 8 · atiksan 5 · gulteks 7`. Ölçüm **teste
> gömüldü** — çekirdek katman bir gün bir ifadeye dokunursa kapı kırmızı verir.

> 🔴 **ÖLÇÜM ARACI, GÖNDERMEK ÜZERE OLDUĞUM DAVRANIŞ DEĞİŞİKLİĞİNİ YAKALADI.** İlk
> sürüm `additive`'i de birleştiriyordu (yol haritası onu *"sözlük"* diye sayıyor) ve
> gölge diff **0 fark** diyordu — çünkü **aracın kendisi** `additive`'i *sözlük*
> (zararsız) kovasına koymuştu. Kovayı düzeltir düzeltmez **beş gerçek fark** göründü:
> `mal` ve `ticaret` cube'ları `additive` beyan etmiyor ve çekirdek onlara `additive:
> full` **yazıyordu** — yani *"hiçbir sayıya dokunmuyor"* diye ilan edilen bir göç,
> motorun **toplama semantiğini** değiştiriyordu. `additive` artık **birleştirilmiyor**:
> doğru değeri **ifadeye** bağlıdır (`cari.bakiye` üç ERP'de `SUM(borç − alacak)`, yani
> hareket toplamı; stok anlık görüntüsü olsaydı `semi` olurdu) ve karar **adım (c)**'nin.
> *Ölçüm aracının kendisi de bir bağımlılıktır* — bu turda **ikinci kez** kanıtlandı.

> 🔴 **SÖZLÜK ile İFADE AYRI — fazın en kritik kararı.** Adım (a) yalnız *anlamı*
> birleştirir (sinonim · birim · `additive` · grain). Yol haritasının kendi denetim
> düzeltmesi: `cari` *"saf tekrar"* **DEĞİL** — ölçü **adları** aynı ama **ifadeleri
> farklı** (`SUM(CASE WHEN cha_tip=0…)` ↔ `SUM(BORC)`), `base_object`'leri dört ayrı tablo.
> *Aynı ada sahip iki ifadeyi "saf tekrar" sanıp birleştirmek, bu fazın üretebileceği en
> sessiz hatadır.*

> ⚠ **Çekirdek EKSİK olanı tamamlar, VAR OLANI DÜZELTMEZ:** `unit`/`additive` yalnız
> **yoksa** yazılır. ERP bir birimi bilerek farklı yazmış olabilir (miktar `kg` ↔ `adet`);
> ezmek **sessizce yanlış birim** demekti — `1.9`'un numeric-fidelity kapısının tam olarak
> engellediği şey.

> 🔴 **BEŞİNCİ ÜRETEÇ, yeni desen DEĞİL.** `compose()` zaten dört YAML üreteci taşıyordu
> (`_merge_cube_synonyms` · `_compose_derived_metrics` · `_compose_relationship_dimensions`
> · `_compose_kpis`); `_merge_cube_metadata` beşincisi. **Anahtar düzeyinde** birleştiriyor
> çünkü `copy2` **dosya düzeyinde** eziyor — bir çekirdek katman yazılsaydı ERP katmanı onu
> **sessizce silerdi** ([KANIT §10.2]).

> 🔴 **GRAIN İHLALİ = COMPOSE REDDİ** (fail-closed, `G5`/`G10` sınıfı). Uyarı **değil**:
> bir uyarı derlenmiş ve dağıtılmış bir MDL bırakır, o MDL'yi kimse geri almaz ve yanlış
> sayı **üretimde** çıkar. ⚠ **Bilinmeyen grain SERBEST** — sözleşmede sayılmamış bir
> tabloyu ihlal saymak, sözlük büyümeden **her yeni ERP'yi reddederdi**.

> ⚠ **KAPI ARMED AMA GERÇEK PACK'LERDE HENÜZ ATEŞLEMİYOR — ve bu yazılı.** Hiçbir metrik
> henüz `grain:` beyan etmiyor: `satis_tutari`'nın kanonik grain'i bir **karardır** ve
> göç reçetesinin **adım (c)**'sine ait (*"ikisi de meşru olabilir → çekirdekte İKİ ayrı
> metrik"*). Bunu yazmadan bırakmak, bir sonraki turun *"ihlal bulmadı, demek ki temiz"*
> diye okumasına yol açardı. *Ateşlemeyen bir kapıyı «yeşil» sanmak, kapının olmamasından
> beterdir.* Kapı ayrıca **ayrışmanın hâlâ durduğunu** da ölçüyor (2 farklı grain).

> ⚠ **Gölge YAZMIYOR** — FAZ 1.1'in birebir dersi: *yazan bir gölge, gölge değildir.*
> **SİLME YOK:** üç ERP'nin `ticaret/metadata.yml` dosyaları **yerinde**; geri alma =
> bayrağı kapatmak (kapı dosyaların varlığını da doğruluyor).

### FAZ 1 · adım 19 — `1.13` **düşman denetim paneli yenilendi** *(2026-08-04)* — 🔴 **FAZ 1 BİTTİ**

Kapı: **19 test** (`tests/test_panel_tazeligi.py`). Kod değişikliği **yok** (belge + kapı).

> **Neden:** panel `2026-07-24`'te dondu ve o tarihten sonra en az altı madde kapandı —
> ama panel bunu **bilmiyordu**. *Bayat bir denetim paneli iki yönde birden yalan söyler:*
> kapanmış maddeler *"hâlâ açık"* görünür (boşa iş), açık maddeler **kalabalıkta kaybolur**.

> ✅ **Beyan ölçüldü ve DOĞRU çıktı:** *"47 açık aksiyon"* — dosyalardaki gerçek sayım da
> **47** (`9+10+9+10+9`). Bu deponun *"beyan var, sayım yok"* sınıfı burada **yakalanmadı**.

> **Durum: ✅ 6 kapandı · ◐ 3 kısmen · ⊘ 2 · ⬜ 36 açık.** Kapananların **hepsi kaynak
> koddan** doğrulandı: `R5-1` scheduler tenant motoru · `R5-2` compose yarışı ·
> `R3-1` ek-farkında kapsam (`firesiz` ⊄ `fire`) · `R3-2` `neq`/`not_in` üretimi ·
> `R4-4` tablo-allowlist (**bu turun `1.3b/2`'si kapattı**) · `R2-8` `period_optional`.

> 🔴 **HER «KAPANDI» İDDİASI KAPIYA ÇEVRİLDİ.** *Yanlış bir «kapandı» işareti, hiç
> işaretlenmemiş bir maddeden daha tehlikelidir: kimse ona bir daha bakmaz.* Her ✅ satırı
> çalıştırılabilir bir yükleme bağlı ve **mutasyon testiyle** kırmızı olabildiği
> kanıtlandı (boş kaynak → yüklem `False`).

> ⚠ **Kod okumakla ölçülemeyen iddialar «kapandı» İŞARETLENMEDİ.** `R2-6` (top-N
> monotonluğu) bir **davranış** iddiasıdır → `⊘ ÖLÇÜLEMEDİ`. `R3-3` ise **karar değişti**:
> panelin önerdiği çözüm denendi ve **kırdı** (`grafi`+`k` geçerli ek zinciri değil →
> grafik soruları kapsam kapısına takıldı, 4 test); sorun `_STOP_EXACT` tam-kelime
> listesiyle **başka yoldan** kapandı.

> 🔴 **DURUMUN TEK SAHİBİ `index.md`.** `findings/*.md`'ye durum sütunu **eklenmedi**:
> *tarihsel kayıt, güncellenmediği için değerlidir* — ve iki sahip ayrışırdı.

> ⚠ **Kapı kendi metnimi yakaladı:** özet satırına *"38 açık"* yazmıştım, tablodaki gerçek
> sayım **36**'ydı. Yani panelin teşhis ettiği kusur sınıfı, panelin **kendi özet
> satırında** yaşıyordu. Toplam artık `6+3+2+36 = 47`'ye **eşit olmak zorunda**.

### FAZ 1 · adım 18 — `1.3b/2` **Katman B'nin İKİNCİ çağrı yolu: `/ask` Discovery** *(2026-08-04)*

**Demet kapısı (korpus): YEŞİL** — TOPLAM doğru-cube **%93,1** (taban %93,2) ·
boyahane %69 · atiksan %69 · gulteks %69 · gitas %73, dördü de tabanda ya da üstünde.
Kapı: **19 test** (`tests/test_katman_b.py`), hızlı sinyal **498**.

> 🔴 **YENİ TEST POLİTİKASI YÜRÜRLÜKTE** (kullanıcı kararı, 2026-08-04): yerel demet
> kapısı **yalnız korpus**; süit · `eval` · senaryo **silinmedi**, gecelik CI'ya
> (`--hepsi`) taşındı. Bu madde o politikayla kapatıldı.

> ⚠ **İLAN EDİLEN SÜRE YANLIŞTI — ölçüldü ve düzeltildi.** `--tam` **13 dk 18 sn**
> sürüyor (`docker inspect`: `15:51:07 → 16:04:25`), *"~3,5 dk"* değil: o rakam dört
> adımlı koşumun **içindeki** korpus dilimiydi ve süit compose'u çoktan yaptığı için
> **ısınmış** sistemde ölçülmüştü. Duvar saatinin **%71'i `boyahane`** (5306 soru /
> 8 dk 49 sn); öteki üçünün toplamı ~3,5 dk — yani ilan edilen sayı farkında olmadan
> *"boyahane hariç"* ölçümüydü. **Seyreltme YAPILMADI:** korpusun tek yakalaması
> paydanın değişmesiydi; soru matrisini seyreltmek tam da paydayı değiştirmektir.

> **Neden:** `1.3b` ilk turda `enforce_query`'yi doldurdu ve `/query`'ye bağladı, ama
> `/ask`'in Discovery dalı **bağlanmamıştı** — ve bu, sessizce atlanmış değildi: sırası
> `query.py`'ye **yazılmıştı** ve bir kapı onu bekliyordu. Bu tur o sırayı kapattı.
> Discovery, ham SQL'in **ikinci** yolu ve **kataloğun dışına çıkabilen tek** yol.

> 🔴 **SARMAL, YAMA DEĞİL.** Discovery dalında SQL'in motora gittiği **beş** nokta var
> (üretim · onarım · çalıştırma · onarımlı çalıştırma · plan tekrarı). Beşini tek tek
> yamamak, **altıncısını ekleyen kişinin unutmasına** açık kalırdı — bu deponun
> `pii.muhurle` kararında birebir yaşadığı şey (*"`raw` dalı düzeltilmiş, kardeşleri
> unutulmuştu"*). Motor **bir kez** sarılıyor; kapı, kapsamı **yapıyla** ölçüyor
> (`_run_discovery` içinde çıplak `service.dry_plan/query` kalmışsa kırmızı).

> 🔴 **TEK SAHİP.** Zorlama gövdesi `query.py`'den `app/katman_b.py`'ye **taşındı**,
> kopyalanmadı: iki kopya zamanla ayrışırdı ve bir güvenlik katmanı için bu **en sessiz**
> kırılma biçimidir. `query.py` artık aynı fonksiyonu çağırıyor.

> 🔴 **ÖLÇÜLEN KUSUR — yetki reddi `422` dönüyordu.** `/query`'de Katman B reddi genel
> `except Exception`'a düşüp **422 "engine / DB errors"** oluyordu: istemci bunu *"sorgum
> bozuk"* diye okur, geliştirici motorda arar. **403**'e çevrildi. *Bir yetki sınırının
> kendini ARIZA gibi göstermesi, sınırın kendisini görünmez kılar.*

> ⚠ **Yetki reddi ONARIMA düşmüyor.** Discovery'nin `dry_plan` hatası `llm.repair`'e
> gider; bir yetki reddi ise **onarılamaz** — yalnız bir LLM çağrısı harcar ve sonunda
> *"güvenilir bir sorgu üretemedim"* der. Ayrı bir dal eklendi: dürüst ret + gerekçe
> `trace`'te. **Tavan 2 satır ucuza gelirdi ama dürüst olmayan bir mesajı SATIN ALMAZ.**

> ⚠ **Ret notu allowlist içeriğini SIZDIRMIYOR:** *"`personel_ozluk`'a erişemezsin"*
> cümlesi, erişilemeyen şeyin **varlığını** sızdırır. Gerekçenin tamamı `trace`'e ve
> audit'e yazılır — **kaybolmaz**, yalnız yetkili olan yerde durur.

> ⟳ **İKİ KAPI TERS ÇEVRİLDİ (silinmedi):** *"Discovery'nin sırası yazılı olmalı"* →
> *"Discovery gerçekten BAĞLI olmalı"* (yapısal, AST). Ve `enforce_query`'nin yetimlik
> kapısı **kendi taşımamdan kırmızı oldu**: *"`katman_b.py` dışında bir dosyada geçiyor
> mu"* diye bakıyordu, zorlama tek sahibe taşınınca kapı bağın **güçlendiği** yerde
> kırmızı verdi. Doğru soru bir dosya adı değil, **zincirin kendisi**: `zorla` →
> `enforce_query` **ve** en az **iki uç** → `zorla`/`sarmala`.

### FAZ 1 · adım 17 — `1.12` **AI Act / NIST RMF / ISO 42001 karşılığı** *(2026-08-04)*

**Kendi tam kapısı: 4/4 YEŞİL** — süit **2477** (7 atlanan · 3 xfail, 8 dk 42 sn) ·
eval **±%0** · korpus **%93,1** (taban %93,2) · senaryolar **düşürülen 0** · 1 ⊘ (`vqr_kalicilik`).
Kapı: **31 test** (`tests/test_ai_act_uyumu.py`), hızlı sinyal **949**.
🔴 **Risk sınırı** (`answer.py` · `routers/ask.py`) → demete girmedi, **kendi kapısını hemen** koştu.

> ⚠ **Yürürlük TARİHİ kapıya çevrilmedi.** Yol haritası *"Md.50 2 Ağustos 2026'dan
> yürürlükte"* derken yanına **kendi eliyle** `[DOĞRULANMADI — birincil kaynak EK F'ye
> eklenecek]` yazmış. Kapı **tarihi doğrulamaz**, yükümlülüğün **kod karşılığının var
> olduğunu** doğrular ve bunu **kendi içinde** yazılı tutar. *Doğrulanmamış bir tarihi
> kapıya çevirmek, ölçmediğimiz bir şeyi ölçtük gibi göstermek olurdu.*

> **Md.50 · içerik işareti:** `ai_generated_prose` — 🔴 **sayı değil, ÜSLUP.** Sayıyı bu
> üründe her zaman küp koyar ve `narration_guard` eşleşmeyen sayı taşıyan cümleyi
> **düşürür**; işaretlenmesi gereken şey **metnin makine yazımı olduğudur**. Ekranda
> **anlatının yanında** durur, kartın tepesinde değil — tepedeki bir rozet *"bu cevabın
> TAMAMI yapay zekâ ürünü"* diye okunurdu ve tablo/sayı/kırılım küpten gelirken bu
> **yanlış** olurdu.

> **Kanıt sınıfı:** `kanit_sinifi ∈ {olculmus, probabilistik}` — ⚠ skaler bir *"güven"*
> **uydurulmadı** (MIMARI §5: *kalibre edilmediği sürece o sayı güven değil **süstür***).
> `cube+llm` **probabilistik** sayılıyor: sayı küpten gelse bile **alan seçimi**
> olasılıksaldır ve seçim yanlışsa **doğru sayı yanlış soruya cevap** olur. **Bugünden**
> eklendi ki geçmiş kayıtlarda *"ölçülmüş mü tahmin mi"* sorusu cevapsız kalmasın.

> **Md.14 · durdurma:** `DELETE /ask/jobs/{id}` + `DurdurDugmesi` (sol **ve** sağ panel).
> 🔴 **İptal işi ÖLDÜRMEZ, sonucunu YAYIMLATMAZ** — thread'i zorla sonlandırmak yarım
> yazılmış bir sonuç/kayıt bırakabilirdi. Koşucunun **iki dalı da** (başarı ve hata)
> durumu yazmadan önce soruyor; durduğu için `failed` **demiyor**. Akışa ayrı bir `iptal`
> olayı eklendi: dalsız bırakılsaydı düğme UI'yi **6 dk dönerken** bırakırdı.

> 🔴 **KENDİ SINAMAM KENDİ KUSURUMU GÖREMEDİ — ve bu düzeltildi.** İlk sürüm iptali
> süreç-içi bir `set()`'te tutuyor, durumu `request.app.state.ask_jobs`'tan okuyordu:
> **öyle bir depo yok** (işler `AskJob` tablosunda). Uç *"böyle bir iş yok"* demekten
> başka bir şey yapamazdı — ve sınama bunu göremezdi çünkü **o olmayan deponun sahtesini
> kuruyordu**. İki tanıdık sınıf birden: *"beyan var, kod onu tanımıyor"* + *"testler
> METNİ ölçtü, davranışı değil"*. Depo artık `AskJob` satırıdır; durum adları (`completed`
> /`failed`) modelin **kendi sözlüğünden** doğrulanıyor.

> **Md.13 · denetleyici-okunabilir ihraç:** `GET /audit/export` (JSON-LD/PROV-O) —
> ⚠ **ikinci bir eşleme yazılmadı**: standart adlara çeviri `1.8`'in `otel_nitelikleri`'nde
> zaten vardı, ikincisi iki ihracın **farklı adlar** kullanması demekti. İhraç
> `zincir_bulgulari`'yı **birlikte** taşır — *bir kanıt defterini bütünlük raporu olmadan
> teslim etmek, "işte kayıtlarım" deyip **eksik olup olmadığını söylememektir**.* Kırpma
> da sessiz değil (`toplam`/`kirpildi`). Ekran tüketicisi **yeni panel açmadan**
> `ContractDetailPanel`'e kondu — ihracın yetkisi (`contract:read`) o panelin yetkisiyle
> **aynı**; K5 tavanı 13/13, pay 0.

> **Md.12/19 · saklama:** `TenantConfig.audit_saklama_gun` — ⚠ **SİLME YAPMIYOR, POLİTİKA
> BEYAN EDİYOR.** Bir saklama süresini uygulamak geri alınamaz bir **silme** eylemidir ve
> FAZ 6'nın onay değişmezine bağlıdır. *Beyan edilmiş ama uygulanmamış bir politika,
> beyan edilmemiş bir politikadan iyidir: denetleyici ne beklediğimizi okuyabilir.*
> Göç `f8c1e3a7d259` (tek head).

> ✅ **ÖLÇÜM ARACININ KENDİSİ DÜZELTİLDİ (`0.21`).** `ask.py` dosya tavanı `TAVAN_ASK_KOD
> + 1259` idi; yani **modül düzeyine** eklenen bir satır için muafiyet yazmak `ask()`
> **gövdesinin** tavanını da yükseltirdi — ve `ask()` tam tavanında (1147/1147) duruyor.
> Dosya muafiyeti artık **ayrı liste** (`MUAFIYET_ASK_DOSYA`, Δ=9, gerekçesi satır satır
> yazılı) ve `ask()` tavanına **dokunmuyor**; yeni kapı bunu doğruluyor.
> *Bir tavanı yanlışlıkla yükselten muafiyet, muafiyet değil sessiz bir tavan artışıdır.*

> ✅ **`1.2c`'nin tümleyeni kendini kanıtladı:** `AskResponse` 29 → **31** alan oldu ve iki
> yeni alan için maskeleme tarafına **hiçbir şey yazılmadı** — yine de kapsandılar. Sayılan
> bir liste olsaydı ikisi de sessizce dışarıda kalırdı. (`pii.py`'nin ölçüm notu güncellendi;
> kapı bayat sayıyı yakaladı.)

> ⚠ **Metin tarayan kapı, kendi belgesini yakaladı — bu oturumda 6. ve 7. kez.** `"_IPTAL"
> not in kaynak` sınaması `DURUM_IPTAL` **sabitinin adını**, `"state.ask_jobs"` sınaması
> ise modülün **kendi hata anlatısını** yakaladı. İkisi de **AST'ye** çevrildi.
> *Belgeyi tarayan bir kapı, hatayı ANLATMAYI cezalandırır.*

### FAZ 1 · adım 16 — `1.10` **eskalasyon matrisi** *(2026-08-04)*

**Demet 12 kapısı: 4/4 YEŞİL** — süit **2426** · eval ±%0 · korpus **%93,1**.
Kapı: **23 test**, hızlı sinyal **564**.

> **Neden:** bir eşik aşıldığında bildirim gider — ve orada **biter**. Kimse bakmazsa
> sistem *"haber verdim"* der ve susar. Ama bir uyarının **işlevi** haber vermek değil,
> **bir karara yol açmaktır**: *on iki saat kimsenin bakmadığı bir alarm, hiç
> gönderilmemiş bir alarmla aynı sonucu üretir.*

> ✅ **YENİ CRON YOK** (yol haritası birebir). Değerlendirici **mevcut 60 sn** döngüsüne
> bindi. İkinci bir zamanlayıcı iki ayrı *"şimdi saat kaç"* sahibi yaratırdı ve ikisi
> kaydığında hangi kuralın ne zaman koştuğu **bilinemezdi**. Kapı bunu **AST ile**
> ölçüyor: `_scheduler_loop` **bir tane** ve eskalasyon onun **içinden** çağrılıyor.

> 🔴 **KİLİTLEME UYGULANMIYOR — KARAR ÜRETİLİYOR.** Bir hesabı otomatik kilitlemek
> **geri alınamaz** bir kullanıcı etkisidir ve FAZ 6'nın *"onaysız hiçbir yazma"*
> değişmezine bağlıdır. Kararı üretip **uygulamamak** bir eksiklik değil, o değişmezin
> **korunmasıdır** — ve karar `AuditLog`'a yazıldığı için **görünürdür**.
> *Uygulanmayan ama kaydedilen bir karar, uygulanan ama kaydedilmeyen bir karardan her
> zaman daha iyidir.* Kapı, modülde `suspend`/`lock`/`delete` gibi bir **eylem**
> olmadığını da doğruluyor; kararın **sahibi** (FAZ 6.1) yazılı.

> ⚠ **Üç fail-safe dal, üçü de gerekçeli:** `ilk_asim=None` → tetiklenmez (`None`'ı
> *"çok eski"* saymak hiç tetiklenmemiş bir kuralı **anında ve her 60 sn'de** yükseltirdi)
> · gelecekteki zaman → tetiklenmez (saat kayması bir gerekçe değildir) · `sure_dakika=0`
> → varsayılana düşer (kural **sürekli** tetiklenirdi).
> ⚠ **`owner`'da yükselme YOK:** kendisine yükseltmek bir **döngü** ve sonsuz audit satırı
> üretirdi; orada artık **insan kararı** bekler.
> ⚠ **Eşik mantığı bu modülün işi DEĞİL** — `asim_zamani` bir **çağrılabilir**; buraya bir
> sorgu koymak eşik mantığının **ikinci bir sahibini** doğururdu. Rol merdiveni de
> `authorize.ROLE_RANK`'ten **türetiliyor**, kopyalanmıyor (kapı ikisini karşılaştırıyor).

### FAZ 1 · adım 15 — `1.11` **kademeli düşüş: kayıt + gösterge** *(2026-08-04)*

Kapı: **16 test**, hızlı sinyal **699**.

> ✅ **YOL HARİTASI HAKLIYDI: «yeni kod YOK».** `FailoverSqlGenerator` **zaten** sırayla
> deniyordu. Eksik olan iki şeydi: **kayıt** (bir düşüş `AuditLog`'a **hiç** yazılmıyordu,
> yalnız bir `WARNING` kütüğü vardı — *kütük aranabilir değildir*; *"dün kaç kez ikinci
> seviyeye düştük"* sorusu **cevapsızdı**) ve **gösterge** (kullanıcı hangi seviyede cevap
> aldığını **göremiyordu**).

| seviye | ne | kullanıcıya |
|---|---|---|
| **1** | birincil LLM | normal (yeşil) |
| **2** | yedek LLM | *"birincil yanıt vermiyor"* (amber) |
| **3** | `rule` — **LLM YOK** | 🔴 **kategorik olarak farklı** cevap (amber + halka) |

> 🔴 **SEVİYE 3 BİR HATA DEĞİL BİR DURUMDUR.** Sistem **çalışıyor**, ama cevaplar
> **kategorik olarak farklı** bir yoldan geliyor. Kırmızı göstermek kullanıcıyı **yanlış
> eyleme** (sistemi yeniden başlatmaya) iterdi — *"çalışıyor ama LLM yok"* ile *"hiç
> çalışmıyor"* aynı şey değildir ve aynı renk kanalını paylaşamazlar.

> ⚠ **ÜÇ SEVİYE, sağlayıcı sayısı DEĞİL.** Failover beş sağlayıcı taşıyabilir; *beş
> seviyeli bir gösterge, kullanıcının kararını değiştirmeyen bir ayrımı ekrana taşırdı.*
> Seviye 2↔3 farkı **kararı değiştirir**; gemini↔groq farkı **değiştirmez** — ve o yüzden
> gemini→groq geçişi audit'e **yazılmaz**: *gürültüyle dolan bir kanıt defteri okunmaz olur.*

> ⚠ **Sıra 0 her zaman seviye 1 DEĞİLDİR:** anahtarsız bir kurulumda `rule` **birinci**
> sıradadır ve zaten seviye **3**'tür. Sırayı seviyeyle karıştırmak, LLM'siz bir kurulumu
> *"normal"* gösterirdi.

> 🔴 **KENDİ SINAMAM GİZLİ BİR VARSAYIM BULDU.** `dusus_kaydi` önceki **üreticiyi** alıp
> seviyesini `sira=0` ile hesaplıyordu — *"önceki her zaman listenin başıdır"*. Aynı
> üretici, aynı seviye, yine de bir **olay** üretiyordu. *Gizli bir varsayım, doğru olduğu
> sürece görünmez; yanlış olduğu gün açıklanamaz bir kayıt bırakır.* Taban seviye artık
> **açıkça** veriliyor.

> ⚠ **Yeni bir UÇ AÇILMADI:** rozet `/schema`'yı **zaten** yokluyor. İkinci bir poll, aynı
> bilgiyi iki kanaldan taşımak ve ikisinin **ayrışması** demekti.
> ⚠ **Kayıt hatası cevabı DÜŞÜRMÜYOR:** kademeli düşüş bir **dayanıklılık** mekanizmasıdır;
> onu **kayıt** yüzünden kırmak amacının tam tersi olurdu.

> ⚠ **Metin ölçme kusuru BEŞİNCİ kez** — bu kez `seviye === 3`'ün **ilk** geçişi (etiket
> dalı) ölçüldü, renk dalı değil. Kapı artık **renk bloğunu** soruyor.

### FAZ 1 · adım 14 — `1.9` **numeric fidelity zorlaması** *(2026-08-04)*

Kapı: **13 test**, hızlı sinyal **508**.

> 🔴 **YOL HARİTASININ SAYDIĞI ÜÇ YÜZEY BUGÜN YOK — ölçüldü.** Madde *"`izinli_degerler()`
> yeni türevleri kapsar (MASE · kırılma-noktası % · karar rozeti %)"* diyor;
> `grep` → **0 isabet**. Olmayan metrikler için türetme eklemek, bu deponun avladığı
> *"beyan var, karşılığı yok"* sınıfının **kendisi** olurdu: kapı genişler, koruduğu bir
> şey olmaz, ve genişlemenin **doğru olup olmadığı hiç ölçülemez**.
> → İnen şey maddenin **kalıcı** yarısı: **zorlama mekanizması**. Üç yüzey birer **tuzak**
> olarak dondu — doğdukları gün test **kırılır** ve beyan edilmelerini zorlar.

> ✅ `narration_guard.dogrula` **araç kaydına girdi** (`makbuz=None`, **kapıdır**).
> Kayıtta **görünmeyen** bir kapı, planlayıcının **bilmediği** bir kapıdır: yeni bir
> anlatı yüzeyi onu atladığında bu bir *"unutma"* değil, *"kaydın söylemediği bir şeyi
> bilmemek"* olur.

> 🔴 **MEVCUT KAPI GERÇEK BİR ANLAM HATASI YAKALADI.** Guard'ı `anlatim` etiketiyle
> kaydettim; planlayıcının **DETERMİNİSTİK-ÖNCE** kuralı onu `llm.anlat`'ın **alternatifi**
> sandı ve LLM aracını **reddetti** (`AracReddi: llm.anlat: DETERMİNİSTİK-ÖNCE ihlali`).
> Üç T2 testi anında kırmızı verdi. **BİR KAPI, BİR ALTERNATİF DEĞİLDİR:** guard anlatı
> **üretmez**, üretileni **doğrular**. Aynı etiketi paylaşmak `KAT-1`'in (*bir mekanizma =
> bir iş*) ihlaliydi → etiket `dogrulama` oldu.

> ⚠ **KD-21 sınırı ölçüldü ve donduruldu:** guard **rakamsız** cümlede **yetkisizdir**.
> Yeni yüzeyler **sayı taşıyan** cümleler üretmelidir, yoksa kapı onları **görmez** ve
> *"guard'dan geçti"* cümlesi **karşılıksız** kalır.

> ⚠ **Beyan kanalı iki adla anılıyor** (`izinli_degerler(ek=)` · `dogrula(ek_degerler=)`)
> — ilk yazımda yanlış adı kullandım ve test takıldı. Yeniden adlandırmak ölçülmüş bir
> kazanç getirmiyor (churn); farkın **yazılı olması** yeterli. Kanal artık **uçtan uca**
> sınanıyor (`guvenli_anlatim` → `dogrula`): yalnız iç fonksiyonu test etmek, dışa açık
> yolun kanalı **geçirdiğini** kanıtlamazdı.

### FAZ 1 · adım 13 — `1.8` **audit zinciri** *(2026-08-04)*

**Demet 11 kapısı: 4/4 YEŞİL** — süit **2376** · eval ±%0 · korpus **%93,1** (taban %93,2).
Kapı: **18 test**, hızlı sinyal **562**.

> 🔴 **«APPEND-ONLY» BİR BEYANDIR, BİR MEKANİZMA DEĞİL.** `AuditLog`'un docstring'i
> *"append-only erişim kanıtı"* diyordu; ama bir satır `DELETE` edilirse geriye **hiçbir
> iz** kalmıyordu. *Bir kanıt kaydı, eksildiğini **kendisi** söyleyemiyorsa kanıt değildir.*
> Her kayıt artık bir öncekinin hash'ini taşıyor (ilki `genesis`).

> ✅ **ÜÇ BULGU SINIFI, ÜÇÜ DE ADIYLA:** `KOPUK` (silme/değiştirme) · `BOZULMUŞ` (içerik
> hash'iyle uyuşmuyor) · `ÇATAL` (eşzamanlı yazım). Üçünü tek bir *"zincir bozuk"*
> mesajına indirmek **hangi** olayın yaşandığını gizlerdi — ve **silme** ile
> **eşzamanlılık** çok farklı şeylerdir.

> 🔴 **ZİNCİRİN ETMEDİKLERİ DE YAZILI — ve testle kilitli.**
> · Eşzamanlı yazımları **sıralamaz** (çatal mümkün) — ama çatal **tespit edilir**.
> Kilitle serileştirmek her audit yazımına kilit maliyeti bindirirdi.
> · **Son** kaydı silmek zinciri **koparmaz** (ondan sonra kimse yok). Bunu *"tespit
> ediliyor"* diye yazmak **olmayan bir garanti satmak** olurdu; harici bir çıpa (dış zaman
> damgası / WORM) gerekir ve bu maddede **yok** — o yüzden *"korunuyoruz"* denmiyor.
> Sınırın kendisi bir **testle** dondurdu.

> 🔴 **OTel GenAI: YENİ KOLON YAZILMADI, EŞLEME YAPILDI.** Ölçüldü — veri **zaten**
> oradaydı (`llm_model` · `llm_input_tokens` · `llm_output_tokens` · `llm_latency_ms` ·
> `source`). OTel adlarıyla ikinci bir kolon kümesi açmak aynı gerçeğin **iki kopyası**
> olurdu ve ikisi zamanla ayrışırdı. `otel_nitelikleri()` bir **çeviricidir**, bir depo
> değil — ve yalnız **dolu** alanları yayınlar: OTel'de eksik bir nitelik **yokluktur**,
> `gen_ai.usage.input_tokens=null` *"ölçüldü ve sıfırdı"* gibi okunur.

> ⚠ **Zincir hatası kaydı DÜŞÜRMÜYOR.** Bir kanıt kaydını *"zincir kurulamadı"* diye
> düşürmek, korumaya çalıştığı şeyi **yok etmek** olurdu — ve eksik hash zaten
> doğrulamada **görünür**.

### FAZ 1 · adım 12 — `1.7` **tazelik merdiveni** *(2026-08-04)*

`grep -rl freshness backend/app/` → **0** idi. `SyncState.last_synced_at` yalnız admin
klon yolundaydı ve `/ask`'e **hiç ulaşmıyordu**: kullanıcı *"8 gündür veri gelmiyor"*u
**göremiyordu** — ve *"bu sayı neden düşük?"* sorusunun **en sık gerçek cevabı** budur.
Kapı: **25 test**, hızlı sinyal **677**.

| kademe | sayı gösterilir mi |
|---|---|
| `taze` | ✅ işaret bile yok |
| `uyari` | ✅ **ama** dalgalı turuncu çizgiyle |
| `hata` | 🔴 **HAYIR** — yerine açıklama kartı |
| `bilinmiyor` | 🔴 **HAYIR** — `hata` ile **aynı** muamele |

> 🔴 **B4 — BİLİNMEYEN TAZELİK, TAZE DEĞİLDİR.** Kaynak planlar bunun **tersini**
> yazıyordu; yol haritası *"bugünkü davranıştan **kasıtlı bir sertleşme**"* diye
> düzeltti ve burada o düzeltme uygulandı. Ölçemediğimiz bir şeyi **iyi** varsaymak,
> `⊘ ÖLÇÜLEMEDİ` üçüncü hâlinin tam tersi olurdu. *Sekiz gün eski bir sayıyı normal gibi
> göstermek, kullanıcıyı yanlış bir karara götürür — ve o karar geri alınamaz.*

> 🔴 **TEK SAYI YAPILANDIRILIR, İKİ EŞİK TÜRETİLİR.** `warn_after` ve `error_after` ayrı
> ayrı ayarlanabilseydi biri ötekini geçebilirdi (`warn=10g`, `error=3g`) ve kullanıcı
> `uyari`'yı **hiç görmeden** `hata`'ya düşerdi. *Çelişebilen iki ayar, çelişecek
> demektir.* `TenantConfig.tazelik_periyot_saat` tek sayı; eşikler **2×** ve **5×**.

> ⚠ **`son_veri_ts` son BAŞARILI SENKRONdur, verinin kendi damgası DEĞİL** — ve ayrım
> yazılı, çünkü boru hattı çalışıp **boş** dönebilir. Keskin sinyal (zaman boyutunun
> `max()`'ı) **her soruda ek bir DB sorgusu** ister; FAZ 0.17'nin gecikme bütçesi tam
> bunun için kurulmuştu ve karar **ölçülmeden alınmadı**.

> ⚠ **Gelecekteki bir zaman damgası → `bilinmiyor`**: saat kayması bir tazelik kanıtı
> değildir; *"çok taze"* diye okumak bozuk bir saati **güvence** yapardı.
> ⚠ **`uyari` farklı bir görsel kanal** kullanıyor (dalgalı alt çizgi), güven rozetinin
> emoji kanalıyla **yarışmıyor** — iki uyarı üst üste binerse ikisi de okunmaz.

> ✅ **`1.2c`'NİN TÜMLEYEN KAPISI ATEŞLEDİ VE İŞ GÖRDÜ.** `AskResponse` **26 → 29** alana
> çıkınca `test_ASKRESPONSE_ALAN_SAYISI_KAYITLI` kırmızı verdi. Üç yeni alan **varsayılan
> olarak maskeleniyor** (doğru sınıf); tek yapılan ölçüm notunu güncellemek oldu.
> *Sayma-değil-kapat deseninin bedeli bir satır, kazancı bir sessiz sızıntı.*

### FAZ 1 · adım 11 — `1.5` **metrik sertifikasyonu** *(2026-08-04)*

`source=cube` rozeti *"deterministik bir yoldan geldi"* der — doğru ama yetersiz.
Cevaplamadığı soru: *"bu metriğin tanımını **kim onayladı**, ve o onaydan beri **tanım
değişti mi**?"* Bir metrik **doğru hesaplanıp yanlış tanımlanmış** olabilir; determinizm
onu yakalamaz. Kapı: **17 test**, hızlı sinyal **883**.

> ✅ **B8 üç kapıdan da düşüyor:** tanım (`definition_hash`) · **üst-akış kolon kümesi**
> (`lineage_set_hash`, `1.6`'dan) · TTL **90 gün**. Birden fazla neden varsa **hepsi**
> yazılır — bir kapının düşmesi ötekini gizlemez.

> 🔴 **ÇÜRÜYEN SERTİFİKA SİLİNMEZ:** seviyesi **korunur**, üstüne bayrak düşer. Silmek,
> *"hiç sertifikalanmamış"* ile *"sertifikalanmış ama tanım değişmiş"*i karıştırırdı — ve
> ikincisi kullanıcı için **daha bilgilendiricidir** (biri bu metriğe bakmış, sonra dünya
> değişmiş). Çürümüş sertifika **kademe vermez**, `⚠` verir: çürük bir onayı
> *"sertifikalı"* diye göstermek rozeti bir **süse** çevirirdi.

> ⚠ **TANIMIN KENDİSİ SAKLANMIYOR** — hash bir **parmak izidir**: değişip değişmediğini
> söyler, neyin değiştiğini değil, ve sertifikanın sorduğu soru tam olarak *"değişti mi"*.
> Tanımı kopyalamak aynı gerçeğin **ikinci bir kaynağı** olurdu.
> ⚠ **Sinonim eklemek sertifikayı DÜŞÜRMEZ:** bir eşanlamlı **tanımı** değiştirmez, yalnız
> **bulunabilirliği** artırır — hash'e katmak sertifikayı katalog bakımının **her turunda**
> düşürürdü ve *gürültüyle ateşleyen bir kapı kapatılır*.

> ⚠ **Frontend: rozetin KADEMESİ, yeni panel DEĞİL** (K5 tavanı **13/13**, boşluk 0).
> Kademe kararı **backend'de**; frontend'de ikinci bir eşik kümesi *"aynı kuralın iki
> sahibi"* olurdu — kapı frontend'de `definition_hash`/`90` gibi **sızıntı** arıyor.

> 🔴 **BİR KAPI, KENDİ ÖLÇÜM HATAMDAN DOĞDU.** `down_revision`'ları **tek tırnak**
> varsayan bir betikle **iki Alembic head'i** ölçtüm ve *"canlı bir göç engeli"* ilan
> ettim. Alembic'in **kendisine** sorunca **tek head** çıktı (`a4d8f2c6e903` çift tırnak
> kullanıyor). *Olmayan bir soruna yama yazmaktan, aracın kendisine sormak kurtardı.*
> Kapı artık Alembic'in **kendi grafiğini** kullanıyor: iki head gerçekten oluşursa
> `alembic upgrade head` patlar ve Postgres dağıtımı **göç edemez**.

> ⚠ **Metin ölçme kusuru bu oturumda DÖRDÜNCÜ kez** (`⟳` sayacı · `0.21` tavan operatörü ·
> `TODO(faz-2)` · burada *"yeni panel DEĞİL"* cümlesinin **satır sonuna bölünmesi**).
> Dördü de yapısal ölçüme çevrildi.

### FAZ 1 · adım 10 — `1.6` **kolon kökeni** *(2026-08-04)*

**Demet 10 kapısı: 4/4 YEŞİL** — süit **2308** · eval ±%0 · korpus **%93,1** (taban %93,2) ·
senaryo dokuz sınıf tabanda. Kapı: **26 test**, hızlı sinyal **577**.

> 🔴 **KİLİT İŞE YARADI — VE BİR SAYIYI DÜZELTTİ.** `gitas` korpusa **geri döndü**
> (semantik payda **342 → 445**). Bu, bir önceki turda yazdığım bir cümleyi **çürütüyor**:
> *"korpusun +1,1 puanı AJ0 düzeltmesinden"* demiştim. **Yanlış.** O artış `gitas`'ın
> düşmesinin **yarattığı şişmeydi**; `gitas` dönünce sayı %94,3 → **%93,1**'e indi.
> AJ0 düzeltmesinin korpus etkisi **≈0** (gürültü içinde) — çünkü **korpus typo yolunu
> yapısal olarak göremez** (soruları katalogdan üretilir, hepsi doğru yazılmıştır).
> *Bir sayının yükselmesi, ölçülen kümenin değişmediğini kanıtlamaz.*

`1.6` · **kolon düzeyi köken.** `answer.koken()` **ilişki** düzeyindeydi (*hangi kırılım
hangi join'den*); bu **kolon** düzeyi: *"bu sayı hangi tablonun hangi kolonundan, hangi
DÖNÜŞÜMLE geldi?"* İkisi farklı sorulardır ve biri ötekinin **yerine geçmez**.

> ✅ **YENİ BİR BEYAN YAZILMADI.** Dönüşüm tipi **manifestten türüyor** — ölçü `expression`'ı
> zaten oradaydı, yalnız **sorulmuyordu**: `SUM`/`COUNT`→`toplam` · `AVG`/bölme/`*100`→
> `oran` · `CASE WHEN`/`FILTER`→`filtre` · düz kolon→`dogrudan` · ilişki→`birlestirme`.
> Bir `lineage:` alanı beyan ettirmek **ikinci bir kaynak açmak** olurdu.

> 🔴 **«BİLİNMİYOR» ≠ «HİÇ SORULMADI».** Discovery ham SQL'inde `cube_query` yoktur;
> köken türetilemez. `"bilinmiyor"` bir eksiklik değil bir **beyandır** — `⊘ ÖLÇÜLEMEDİ`
> üçüncü hâliyle aynı disiplin.

> 🔴 **ŞABLONLARIN TEK SAHİBİ BACKEND.** Cümleleri frontend'de üretmek *"aynı kuralın iki
> sahibi"* olurdu ve ikisi ayrışıp kullanıcıya **aynı kanıtı farklı cümlelerle** gösterirdi.
> Kapı frontend'de şablon **kopyası** aramıyor — **olmadığını** doğruluyor.
> **KD-13:** ham köken **yapısı** (graf) frontend'e **basılmıyor** — kullanıcının sorusu
> *"bu sayı nereden geldi"*dir ve cevabı bir **cümledir**; graf bir geliştirici artefaktıdır
> (`D3`'ün *"geliştirici katmanı son kullanıcıda"* kusurunun tekrarı olurdu).

> ⚠ **ÜÇÜNCÜ CÜMLE BİLİNÇLE GELMEDİ.** *"Bir üst-akış tablo N gün önce değişti"* **FAZ
> 1.7**'nin verisini ister (`SyncState.last_synced_at`) ve o veri `/ask`'e **hiç ulaşmıyor**
> (`grep -rl freshness backend/app/` → **0**). Uydurma bir gün sayısı, `pvm:`/`target:`
> eşleştirmesinde **reddedilen** şeyin aynısı olurdu: **güvenle yanlış** bir sayı.

> ✅ **SIRA DÜZELTMESİ İŞE YARADI:** `1.6` önce indiği için `1.5`'in `lineage_set_hash`'i
> artık **üretilebilir**. Bugünkü sırayla `1.5` inseydi o alan ya **uydurulur** ya **hep
> `None`** olurdu.

> ⚠ Bayrak kaydını yanlış şemayla yazdım (`stage`/`owner`/`note` yerine
> `label`/`description`/`category`) — `test_bayrak_kaydi` **anında** yakaladı.

### FAZ 1 · adım 9 — `1.4` **süreç-arası derleme kilidi** *(2026-08-04)*

Kilit **süreç-içiydi** (`threading.Lock`). Artık **iki kademeli**: `threading` (ucuz,
süreç-içi) **+** `fcntl.flock` (süreç-arası), zaman aşımı **60 sn**, aşımda
**`RuntimeError`**. Kapı: **10 test**, hızlı sinyal **303**.

> 🔴 **GEREKÇESİ BU TURDA CANLIDA GÖZLENDİ — ve bir KAPIYI KIRDI.** Demet 9 kapısında
> `gitas` korpustan **tamamen düştü**; dosya sonradan **yerindeydi**, yani okuyucu
> compose'un **ortasına** denk gelmişti. `1.4`'ün gerekçesi 2026-08-02'de bir kez
> üretilmişti; bu **ikinci ve kendiliğinden** gelen gözlem.

> 🔴 **KİLİT DOSYASI DİZİNİN İÇİNDE DEĞİL, KARDEŞİ — ölçülmüş bir tuzak.** `compose()`
> çıktı dizinindeki `target` **dışındaki her çocuğu siler**. İçeriye konan bir kilit
> dosyası **tutulurken unlink edilirdi**: kilidi tutan süreç silinmiş inode üzerinde
> bekler, ikinci süreç **YENİ bir inode** açıp `flock`'u **anında** alır — kilit
> **sessizce çalışmaz** hâle gelirdi. ⚠ Yol haritası içeriyi (`<slug>/.compose.lock`)
> söylüyordu; sapma **ölçüye dayanıyor**. *Dosyayı koruma listesine eklemek kilidi bir
> listenin bakımına bağlardı; kardeş konum **yapısal olarak** bağışıktır.*

> ⚠ **Zaman aşımında süreç-içi kilit de bırakılıyor** — yoksa ilk aşım o dizini bu süreçte
> **kalıcı olarak** kilitlerdi (deadlock). Ayrı testle kilitli.
> ⚠ **Sessiz geçiş YOK:** kilidi alamadan derlemeye girmek, kilidin olmamasıyla aynı
> şeydir — üstüne bir de *"korunuyoruz"* beyanı ekler.
> ⚠ **`fcntl` yoksa** süreç-arası kademe düşer ama **gürültülü**: uyarı loglanır. Sessizce
> düşürmek, kilidin var olmadığı bir ortamda *"korunuyoruz"* sanmak olurdu; süreci
> reddetmek ise orantısız (tek süreçli kurulumda iç kademe doğru ve yeterli).

> ✅ **gunicorn/çok-worker dağıtımının ön koşulu kapandı** (→ II-G.7).

### FAZ 1 · adım 8 — `1.2c` redactor TÜMLEYENİ *(2026-08-04)*

**Demet 9b kapısı: süit 2282 geçti, 2 kırmızı — ikisi de `0.21` modül büyüme kapısı.**
Kapı **tam da kurulduğu işi** yaptı: AJ0 düzeltmesi `ask()`'e **10 kod satırı** eklemişti.

> ✅ **KAPI DOĞRU MİMARİYİ ZORLADI.** Kendi talimatı (*"yeni davranışı **modüle çıkar**,
> tavanı yükseltme"*) uygulandı: mantık `app/typo_onerisi.py`'ye taşındı, `ask()` **tek
> satırlık** bir çağrıya indi. Sonuç: `ask()` **1147/1147** · `ask.py` **2406/2406** —
> **boşluk 0**, yani fonksiyon **hiç büyümedi**. *Tavanı yükseltmek kapıyı kapının
> kendisiyle çürütürdü.*

`1.2c` · **redactor tümleyene çevrildi.** Ölçüldü: `apply_to_ask_response` yalnız **üç**
yeri maskeliyordu (`result.rows` · `facts[].text` · `summary`) — `AskResponse`'un **26**
alanı var.

> 🔴 **MASKELENMEYENLER:** `interpretation.narration` (LLM metni, **olgulardan** üretilir)
> · `contribution` (**cevabın gövdesi**, `0.23`'ün ölçtüğü alan) · `next_steps` ·
> `suggestions` (chip **etiketleri**, boyut değeri taşır) · `prescription` ·
> `recommendations` · `kpi` · `note` · `calculation_explanation`.
> **Sayılan bir liste, yeni alanı sessizce dışarıda bırakır** — `KAT-5`: *SAYMA, KAPAT*.
> Artık varsayılan **maskelemek**; muaf tutmak **açık ve gerekçeli** bir karar
> (`MUAF_ALANLAR`, `ReportPanel`'in `SAF_NOT_ALANLARI` tümleyeniyle aynı desen).

> 🔴 **YOL HARİTASININ VARSAYIMI ÖLÇÜLDÜ VE DOĞRU ÇIKTI** — ama kilitlenmemişti.
> *"Grafik etiketleri maskelenmezse §D.2/2 doğru değil"* deniyordu. Ölçüm: grafik
> `option`'ı `buildOption(effResult, …)` ile **maskeli sonuçtan** türüyor; CSV
> `exportTableCsv(result, …)` **aynı** satırlardan; PNG/SVG **aynı option**'dan; `VizSpec`
> yalnız **kolon adları** taşıyor. → **Dışa aktarım zinciri zaten maskeliydi**; asıl boşluk
> **yanıt gövdesindeydi**. Zincir yine de kapıya çevrildi: *bir doğru varsayım,
> kilitlenmemişse bir sonraki turda yanlış olabilir.*

> ⚠ **Pydantic modelleri de geziliyor:** `suggestions` bir `list[Suggestion]`'dır, sözlük
> değil. Yalnız `str`/`dict`/`list` gezen bir maskeleyici onu **sessizce** atlar ve chip
> etiketleri maskesiz kalırdı.

> ⚠ **Muafiyetler gerekçeli:** `cube_query` **yapısal bir kanıttır** (`POST /cube` onu
> birebir yeniden koşar) — maskelemek checkpoint'i (D4) kırardı: *bir kanıt,
> değiştirilirse kanıt değildir*. `sql`/`planned_sql` maskelenirse **çalıştırılamaz** olur.
> `question` kullanıcının **kendi** metnidir.

### FAZ 1 · adım 7 — `1.2b` LLM tek kapı · `AJ0/1` yazım önerisi *(2026-08-04)*

> 🔴 **DEMET 9'UN İLK KAPI KOŞUMU KIRMIZIYDI VE İKİ AYRI ŞEY ÇIKTI.**
> Korpus **%94,3** (taban %93,2) — yani doğruluk **ARTTI** — ama kapı **kırmızı**, çünkü
> `gitas` korpustan **tamamen düşmüştü**: `FileNotFoundError: demo/wren-project/cubes/
> enerji_makine/metadata.yml`. Dosya **şimdi var** ve dizin **gitignore'da** (derlenmiş
> çıktı) → bu bir **COMPOSE YARIŞI**. `1.4`'ün gerekçesi 2026-08-02'de bir kez
> üretilmişti; artık **bir kapıyı kırdığı** ikinci bir gözlem var.
> ⚠ **Payda 445 → 342 düştü ve yüzde YÜKSELDİ.** Bir metriğin iyileşmesi, ölçülemeyenlerin
> denklemden çıkmasıyla da olur — *"sayı arttı"* tek başına bir haber değildir.

`1.2b` · **LLM'e giden tek kapı.** *"Ham veri LLM'e gitmez"* kuralının **üç sahibi** vardı
(`sensitivity.prompt_safe_values` · `cube_router.build_catalog` · `ask.py`) ve üçü de
**girdi** tarafındaydı. `app/llm_guard.py::safe_call` **çıkış** tarafında durur: üç
gönderim noktası (`anthropic._ask` · `anthropic._arac_ile` · `openai-uyumlu._chat`)
artık ondan geçiyor. Kapı: **9 test** + mevcut 11.

> ⚠ **Girdi süzgeçleri KALIYOR.** `safe_call` onların **yerine** değil **arkalarına**
> durur. Ateşlerse bu bir **BULGUDUR**: üç süzgecin kapsamadığı bir yol açılmış demektir.
> ⚠ Tespit `pii.py`'den — **dördüncü bir desen sözlüğü yazılmadı**. Ve ihlalde **değerin
> kendisi loglanmaz**: bir sızıntıyı raporlarken sızdırmak, kapıyı sızıntı yüzeyi yapardı.

`AJ0/1` · **yazım önerisi cevaplı yolu kesemez.** Arka plan ölçüm turunun bıraktığı
düzeltme incelendi ve **tutuldu**: öneri artık `route()` ile doğrulanıyor (sıfır-LLM).
Ölçüldü — düzeltmeden önce **doğru yazılmış** sorular kesiliyordu (`arttı`→`parti`),
korpusun **+1,1 puanı** buradan.

> 🔴 **AMA BİR İDDİA ÇÜRÜTÜLDÜ.** O tur *"gerçek hatalar 0,833–0,909, saçmalar 0,667;
> bantlar **AYRIK**"* demiş ve *"eşiği yükselt"* sonucunu çıkarmıştı. Bağımsız ölçüm
> (geniş örneklem): saçma **0,600–0,769**, gerçek **0,714–0,923** → **ÇAKIŞIYORLAR**.
> Eşiği yükseltmek `fıre→fire` (0,750) ve `musteri→müşteri` (0,714) gibi **gerçek**
> hataları kaybettirirdi. **Kanıtlanmamış bir düzeltme sevk edilmedi**; ölçüm
> `test_BANTLAR_AYRIK_DEGIL_olculdu` ile donduruldu — *çürütülmüş bir gerekçe, yazılı
> değilse tekrar edilir.*

> ⚠ **KUSUR KAPANMADI, GÖRÜNÜR BIRAKILDI.** Saçma düzeltme de route ediyor
> (`"…parti iplik"` katalog terimlerinden oluşuyor). Üç uçtan uca vaka
> **`xfail(strict=True)`** — düzeldiği gün test **kırılır** ve işareti kaldırmaya zorlar.
> Gerçek ayırıcı sinyal benzerlik oranı değil **Türkçe fiil çekimi** (saçmaların hepsi
> fiil→isim); o iş AJ0'ın morfoloji kalemine ait.

### FAZ 1 · adım 6 — `1.2a` **kolon düzeyi erişim denetimi** *(2026-08-04)*

`sensitivity` → CLAC **eşik** eşlemesi + `motor_cls=off|shadow|on` (varsayılan **`off`**).
Kapı: **16 test**, hızlı sinyal **850**.

| seviye | sonuç *(boyahane, 20 kolon)* |
|---|---|
| `session_gizlilik = 0` | 🔴 kolon **plandan tamamen DÜŞER** — `SELECT *` onu döndürmez |
| `session_gizlilik = 2` | gelir |
| property **yok** | **fail-closed** |

> 🔴 **VARSAYILAN `off` — ve `motor_rls`'ten farkı ölçüme dayanıyor.** CLS `pii.py`'den
> **kategorik olarak farklıdır**: maskeleme kolonu **gösterir** (`123****89`), CLS onu
> **yok eder** — ve yok etme **sessizdir**. *Sessizce eksik bir tablo, maskeli bir
> tablodan daha kötüdür, çünkü eksiklik fark edilmez.*

> 🔴 **`on` KADEMESİ BİR KAPIYLA KİLİTLİ — bayrak kendi ön koşulunu biliyor.** CLS session
> property'yi **zorunlu** kılar; bugün **36** `query`/`dry_plan` çağrı sitesi kimlik
> geçmiyor ve `on` açılırsa her biri **fail-closed patlar**. Kapı bayrağı ancak tesisat
> tamamlandığında açılabilir kılıyor ve kalanı **sayıyla** raporluyor.

> ⚠ **`1.1`'de ERTELENEN session tesisatı GELDİ** — çünkü artık **gerçek tüketicisi var**.
> `1.1`'de yazsaydım `K3` (ters yetim) ihlali olurdu; sırayı doğru tutmanın karşılığı bu.

> ⚠ **Seviyeler UYDURULMADI:** `authorize.py` zaten `"pii:view": 2` diyor,
> `gizlilik_seviyesi()` o kararı **okuyor**. Hassasiyet sınıfı da tek sahipten
> (`sensitivity.classify`) — `pii.py` ile CLS ayrı sözlük okusaydı aynı kolon bir katmanda
> maskeli, ötekinde **görünür** olurdu.

> 🔴 **KENDİ BELGELEDİĞİM TUZAĞA YANLIŞ KATMANDA DÜŞTÜM.**
> `wren_core.SessionContext(properties=…)` **`frozenset`** ister;
> `wren.engine.WrenEngine.dry_plan/query(properties=…)` **`dict`** ister ve dönüşümü
> **kendi** yapar. Probe `SessionContext`'i doğrudan kullandığı için `frozenset` gördüm ve
> onu **bir katman yukarı** taşıdım → `'frozenset' object has no attribute 'items'`, **üç
> PII testi kırmızı**. *Belgelenmiş bir tuzak, yanlış katmanda uygulanınca yine tuzaktır.*
> Süit yakaladı; ayrım artık `test_HANGI_KATMAN_HANGI_BICIM`'de kilitli.

> ⟳ **`§3.4-session` TUZAĞI ATEŞLEDİ** (bu operasyonda **dördüncü** kez) ve satır
> **kuyruğa** nişanlandı: `§3.4-kuyruk` → *"SessionProperty **TÜM** çağrı sitelerinde"*.
> 36 sıfıra indiği gün yine kırılacak ve `motor_cls=on` açılabilir hâle gelecek. Sayaç
> `test_motor_cls.py`'nin sahibinde; tuzak onu **çağırıyor**, ikinci bir sayaç yazmadı.

### FAZ 1 · adım 5 — `1.1b` **arka plan işi kimliksiz koşmaz** *(2026-08-04)*

**Demet 8 kapısı: 4/4 YEŞİL** — süit **2243 geçti** · eval ±%0 · korpus **%93,2** (taban
%93,2) · senaryo dokuz sınıf tabanda.

`1.1` yalnız **istek yolunu** kapatmıştı. Zamanlayıcı döngüsü `run_schedule`'ı **kimliksiz**
çağırıyordu → `authorize()` **hiç çalışmıyordu**. Kapı: **11 test**, hızlı sinyal **325**.

> 🔴 **ZAMANLANMIŞ RAPOR, YETKİ İPTALİNİ ATLATAN KALICI BİR KANALDI.** Kullanıcı `viewer`'a
> düşürülse, hatta **silinse** bile raporu koşmaya devam ediyordu. Üç fail-closed kapısı
> kuruldu, üçü de ayrı gerekçeli: **sahip yok** · **sahip çözülemiyor** (silinmiş/pasif) ·
> **sahip artık yetkili değil**. Sonuncusunun kuralı: *yetki, verildiği an değil
> **KULLANILDIĞI AN** geçerli olmalıdır.*

> 🔴 **FAIL-CLOSED KESİNTİ ÜRETMEDEN — çünkü cevap zaten kayıttaydı.** Yol haritası
> *"`principal=None` reddedilir"* diyor; harfi harfine uygulanırsa **her zamanlanmış rapor
> durur**. Ölçüldü: kayıt **`created_by`'ı zaten taşıyor** — yani *"bu iş kimin adına
> koşuyor"* sorusunun cevabı **duruyordu, hiç sorulmuyordu**. `run_as_user_id` → yoksa
> `created_by`; ikisi de yoksa **red**. Bu bir gevşetme değil, **geriye doldurma**.

> ⚠ **Kimlik SAKLANMIYOR, her koşumda KAYNAKTAN kuruluyor** (`app_user` + `membership` +
> `role`). Token saklamak bir **sır** saklamaktır ve süresi dolar; saklanmış bir yetki,
> **iptal edilemeyen** bir yetkidir. Böylece rol değişikliği **bir sonraki koşumda** etkili.

> ⚠ **Sahipsiz kayıt bir «eski veri» DEĞİL, bir BULGUDUR.** Genel `except`e düşürmek onu
> *"tek zamanlama hatası"* diye meşrulaştırır ve delik **sessizce** açık kalırdı — özel
> yakalayıcı genel olandan **önce** duruyor ve zamanlamanın **adıyla** logluyor
> (kapı sıranın doğruluğunu da ölçüyor: sonra gelseydi hiç ateşlenmezdi).

> ✅ **ÜÇ PARÇA DA İNDİ (K1/K2):** backend *(kimlik kapısı)* · sözleşme *(`GET /schedules`
> → `run_as`)* · **frontend** *(`SchedulesPanel`: *"… adına"* / **"⚠ sahipsiz — koşmuyor"**)*.
> Sahipsiz kayıt artık **koşmuyor**; bunu göstermemek kullanıcıyı **sessizce durmuş** bir
> raporu beklemeye bırakırdı. **Görülemeyen bir yetki devri, devredilmemiş sayılır.**

### FAZ 1 · adım 4 — `1.3b` **Katman B artık var** *(2026-08-04)*

`enforce_query` bir **stub**'dı (gövde tek satır `return`, üstünde `# TODO(faz-2)`) —
ve **çağıranı da yoktu**. Yani ADR-0014 Karar 5'in beyan ettiği katman ne iş yapıyordu
ne de bağlıydı. Kapı: **12 test**. Hızlı sinyal: **407 geçti**.

> 🔴 **BEYAN VAR, KATMAN YOK — üstelik İKİ KATLI.** Bir stub'ı doldurmak yetmez; katman
> ancak **çağrıldığı yerde** vardır. `grep enforce_query app/` → **0 isabet**. Bu,
> `0.5`'in *"19 altın vakalı ölü modül"* bulgusunun **güvenlik katmanındaki** hâli.

> 🔴 **«Boş allowlist geçer» düzeltmesi göründüğü kadar basit DEĞİL.** Yol haritası
> *"fail-open → fail-closed"* diyor ve **yön doğru**; ama `ModelPermission` **her
> tenant'ta boş** — harfi harfine uygulanırsa **her sorgu reddedilir**, yani bir güvenlik
> katmanı adına **tam kesinti**. Ayrım kurtarıyor:
> **«yapılandırılmamış» ile «boş allowlist» AYNI ŞEY DEĞİL.**
>
> | tenant'ın satırı | anlamı | karar |
> |---|---|---|
> | **hiç yok** | Katman B kurulmamış | Katman A yönetir |
> | **var, model listede yok** | allowlist **aktif** | 🔴 **RED** (fail-closed) |
>
> Böylece şart **anlamlı hâliyle** sağlanır: bir kez yapılandırıldığında eksik allowlist
> **artık geçmez** — ve bugün **hiçbir davranış değişmez**, yani madde `bayraksız`
> kalabiliyor (yol haritasının sınıflandırması korunuyor).

> ⚠ **Rol köprüsü:** `Principal` rol **ANAHTARI** taşır (`["owner"]`), `ModelPermission`
> rol **KİMLİĞİ** (UUID FK). Köprü `Role` tablosundan kuruluyor. Çevirmeden tenant
> genelinde birleştirmek, allowlist'i **rol ayrımı olmadan** uygulamak olurdu — istenenden
> **geniş** bir izin, sessizce. Rol çözülemezse `None` döner: **kısmen anlaşılmış** bir
> yetki kuralını uygulamak, yanlış yönde hata yapma riskini ikiye katlar.

> ⚠ **DB ulaşılamazsa tam kesinti YOK:** ulaşılamayan bir **yetki deposunu** boş allowlist
> saymak, bir altyapı arızasını tam kesintiye çevirirdi.

> ⚠ **Model çözümü motorun KENDİ fonksiyonuyla** (`wren.policy.resolve_model_name`).
> Yetkilendirdiğimiz küme, motorun **gerçekten planladığı** küme olmalı; ikisi ayrışırsa
> *"izin verdik"* ile *"dokunuldu"* farklı şeyler olur — bir güvenlik katmanının **en
> sessiz** kırılma biçimi.

> ⚠ **İKİNCİ ÇAĞRI YOLUNUN SIRASI YAZILI:** `/ask`'in Discovery dalı ayrı turda bağlanır
> çünkü `routers/ask.py` **risk sınırındadır** (demete girmez, kendi kapısını koşar).
> Sessizce atlanmadı; kapı bunu **test ediyor** ki bir sonraki tur *"zaten bağlı"* sanmasın.

> 🔴 **METİN ÖLÇME KUSURUNA BU OTURUMDA ÜÇÜNCÜ KEZ DÜŞTÜM** (`⟳` sayacı · `0.21` tavan
> operatörü · burada `TODO(faz-2)`): kapı, fonksiyonun **kendi tarihçe yorumunu** yakalayıp
> doğru yazılmış kodu kırmızı ilan etti. Üçü de **AST**'e çevrildi. Doğru soru *"şu dizi
> geçiyor mu"* değil, **"gövde ne yapıyor"**.

### FAZ 1 · adım 3 — `1.1` **MOTOR RLS İNDİ** *(2026-08-04)*

`always_filter` → `rowLevelAccessControls` çevirisi. Bayrak **`motor_rls=off|shadow|on`**,
varsayılan **`shadow`**. Kapı: **15 test** (`test_motor_rls.py`) + **7** ön koşul.
Hızlı sinyal: **803 geçti**.

| kademe | manifest | servis edilen cevap |
|---|---|---|
| `off` | dokunulmaz | bugünkü |
| **`shadow`** *(varsayılan)* | **dokunulmaz** | **bugünkü** — gölge yalnız **ÖLÇER** |
| `on` | RLAC yazılır | motor filtreliyor; `_inject_always_filter` o cube'da **elini çeker** |

> 🔴 **KENDİ TASARIMIMDA TUTARSIZLIK BULDUM VE DÜZELTTİM.** İlk sürüm `shadow`'da da
> manifeste RLAC yazıyordu — o hâlde motor filtreyi **uygular** ve **ham-SQL yolundaki
> cevap DEĞİŞİRDİ**. Yani *"gölge"* adı altında **canlı bir davranış değişikliği** sevk
> edilecekti. Doğru desen **komşuda zaten yazılıydı**: `_sql_policy`'nin gölgesi motoru
> gevşek kurar, katı politikayı **AYRI bir motorla PARALEL** dener.
> ⚠ **803 yeşil test bunu YAKALAMADI** ve nedeni kayda değer: `alwaysFilter` yalnız
> **gulteks**'te var (3 cube, logo-3 tenant'ı) ve süit o tenant'ın **ham SQL** yolunu
> ölçmüyor. **Yeşil bir süit, ölçmediği bir davranış hakkında hiçbir şey söylemez.**

> 🔴 **`SessionProperty` BİLİNÇLE GELMEDİ.** `always_filter` **sabit** yüklemdir
> (`CANCELLED = 0`) ve ölçüldü ki motor sabit koşullu kuralı `requiredProperties`
> **olmadan** da uyguluyor. Session tesisatını şimdi yazmak **çağıranı olmayan bir
> yetenek** üretirdi — `K3` (ters yetim) kapısının avladığı sınıf. İlk session'a bağlı
> kural doğduğunda (`1.2`) `sql_literal()` ile birlikte gelecek; gerekçe `rls.py`'nin
> başında yazılı ki *"unutuldu"* sanılmasın.

> 🔴 **ÖLÇÜLMÜŞ BİR FAIL-OPEN YASAKLANDI:** `required=False` + `defaultExpr` verilirse
> property **hiç gönderilmese bile** sorgu **varsayılanla** koşar (`WHERE tenant =
> 'HERKES'`). Kimlik enjeksiyonunu unuttuğumuz gün sistem **hata vermez**, başka bir
> filtreyle cevap verir — filtresiz cevaptan **daha sinsi**, çünkü sonuç makul görünür.

> ⚠ **Gecikme bütçesi (0.17) gölgeye uygulandı:** gölge denetimi HER sorguda koşar ve
> `json.loads` 117 KB'lık manifesti her turda ayrıştırırdı. **Beş tenant'ın dördünde**
> hiç `alwaysFilter` yok → ucuz bayt taraması onları ayrıştırmadan eliyor.

> ⚠ **JSONL'dan sapma bilinçli:** yol haritası `logs/rls_shadow.jsonl` diyordu; gölge
> bulgularının bu depoda **zaten bir sahibi var** (`_shadow_policy_check` →
> `_log.warning`). İkinci bir kayıt mekanizması *"aynı kuralın iki sahibi"* olurdu; 7
> günlük ölçüt aynı greple ölçülür (`RLS (gölge)`).

> ⟳ **`§3.4-RLS` TUZAĞI ATEŞLEDİ ve TERS ÇEVRİLDİ** (bu operasyonda **üçüncü** kez).
> §0 satırı **daraltıldı** (geriye `SessionProperty` · FAZ 1.2 kaldı), ⟳ sayısı **13**.
> 🔴 **Yeni belirteç iki kez yanlış yazıldı ve ikisi de kayıtlı sınıf:** (1) alt-dize
> taraması `rls.py`'nin **YORUMUNU** yakaladı — `§3.4-osi`'nin iki kez düştüğü yer;
> (2) `_app_kaynagi(x)` bir dosyayı **DIŞLAR**, seçmez — imzayı ters kullandım. Şimdi
> **tanımın kendisi** aranıyor (`^def oturum_ozellikleri`).

### FAZ 1 · adım 2 — `1.1` **ÖN KOŞUL ÖLÇÜMÜ** *(2026-08-04)*

Bir katmanı **kanıtlanmamış** bir yeteneğin üstüne kurmak `KAT-3` ihlalidir. `1.1` motorun
`rowLevelAccessControls` + `SessionProperty` yeteneğine dayanacak — o yüzden yetenek
**önce ölçüldü**, sonra `tests/test_motor_rls_onkosul.py` ile **donduruldu** (7 test).

| # | Soru | Ölçüm |
|---|---|---|
| **1** | Koşul SQL'e enjekte oluyor mu? | ✅ modelin alt sorgusuna `WHERE … = 'değer'` |
| **2** | **JOIN** ile baypas edilebiliyor mu? | ✅ **HAYIR** — filtre join'in **iki tarafına da** iniyor |
| **3** | Property verilmezse? | ✅ **fail-closed** (planlama hatası, filtresiz sorgu DEĞİL) |
| **4** | Kötücül/kaçışsız değer? | ✅ reddediliyor — *"allow only literal value"* |
| **5** | Manifest daraltmasında RLAC düşüyor mu? | ✅ **hayır**, round-trip'te korunuyor |
| **6** | `dry_plan`/`query`/`dry_run` üçü de `properties` alıyor mu? | ✅ **üçü de** |

> 🔴 **(2) MADDENİN VARLIK SEBEBİ.** `always_filter` bir **uygulama katmanı** yamasıdır ve
> `compose.py:434` (**G10**) onun **join altında baypas edildiğini** zaten ölçmüştü: filtre
> yalnız o cube'un kendi SQL'ine ekleniyor, join `__source` seviyesinde gerçekleşiyor.
> Motor RLS'i o deliği **yapısal olarak** kapatıyor — ve bu artık bir umut değil, bir ölçüm.

> 🔴 **MOTOR HAZIR, TESİSAT YOK.** `wren_core` `RowLevelAccessControl` · `SessionProperty` ·
> `validate_rlac_rule` **taşıyor** ve `wren.engine`'in üç yolu da `properties` parametresi
> **kabul ediyor**. Ama `grep -c rowLevelAccessControl backend/app/` → **0** ve
> `WrenService.dry_plan(self, sql)` `properties`'i **hiç geçmiyor**. Yani eksik olan
> **yetenek değil, onu çağıran satırlar**.

> ⚠ **(4) BİR GÜVENLİK YÜZEYİNİ KONUMLANDIRIYOR:** session property değerleri **SQL
> literali** olarak veriliyor → tırnaklama/kaçış **bizim tarafımızda**. Motor tek literal
> dışındaki her şeyi reddederek **ikinci** savunmayı koyuyor; `1.1`'in
> `oturum_ozellikleri()`'si **birinci** savunma olacak.

> ⚠ **Ölçüm sırasında bir tuzağa düşüldü ve kilitlendi:** `properties` düz `dict` kabul
> etmiyor, `frozenset(dict.items())` istiyor (`wren.engine._plan` onu böyle kuruyor).
> Düz sözlük `TypeError` verir — ve bu hata **çalışma anında, kimlik yolunda** patlardı.

### FAZ 1 · adım 1 — `1.3c` sahte güvenlik sınırı · `1.3` yetki granülerliği *(2026-08-04)*

**FAZ 0 kapanış kapısı: 4/4 YEŞİL.** süit **2199 geçti** (2 atlandı · 1 xfail) · eval
precision/coverage **±%0** · korpus **%93,2** (taban %93,2) · senaryo dokuz sınıf tabanda.

> 🔴 **`1.3c` — MIMARI İKİ YERDE OLMAYAN BİR GARANTİ SATIYORDU.** `§3.4` tablosu ve `§5`
> *"yapılmayacaklar"* satırı ikisi de *"45 veri-okuyucu TVF'yi **her AST konumunda**
> bloklar"* diyordu. Motorun **kendi kaynağı** (`wren/policy.py`) tam tersini söylüyor ve
> alıntı birebir MIMARI'ye geçti: *"for non-source positions this named list **is** the
> security boundary: a reader that is **not enumerated** here **will pass** in a
> projection / subquery / nested-arg position. The list must therefore be **MAINTAINED
> PER-CONNECTOR**."* Kaynak konumu (`FROM`/`JOIN`) **gerçekten** fail-closed; kaynak-dışı
> konumlar **blocklist**. İkisi aynı cümle değil ve fark **güvenlik kararı** doğuruyor.

> 🔴 **VE «KONNEKTÖR BAŞINA BAKIM» ANA KONNEKTÖRÜMÜZDE HİÇ YAPILMAMIŞ.** Ölçüldü: 45 adın
> **0'ı** SQL Server okuyucusu — ve `wren_service.py:143`'ün kendi notu *"üretimdeki
> tenant'larımız (gitas, atiksan) tam olarak **mssql**"* diyor.
> ⚠ **Bu bir «sömürülebiliriz» iddiası DEĞİL ve öyle yazılmadı:** mssql'in tehlikeli
> okuyucuları ya **kaynak konumundadır** (`OPENROWSET`/`OPENQUERY` → `FROM` → zaten
> fail-closed) ya da `SELECT` bile değildir (`xp_cmdshell` → `EXEC` → `guard_sql` zaten
> reddeder). Ölçülen şey bir **kapsama boşluğudur**, bir açık değil. Boşluğu *"açık"*
> yazmak da *"yok"* yazmak kadar yanlış olurdu. Kapı: `tests/test_blocklist_tazeligi.py`
> — muafiyet **gerekçesiz olamaz** ve **bitiş koşulu** taşımak zorunda.

> ✅ **`1.3` — 15/15 `query:run` → BEŞ AKSİYON.** `query:run` 7 · `drill:run` 2 ·
> `contribution:run` 2 · **`contribution:scan` 1** · `llm:invoke` 3.
> **Tek davranış değişikliği** ve o da yol haritasının KAPI'sının adıyla istediği:
> *"viewer rolü `contribution.report` (maliyet **`pahali`**, 6 boyut tarama) çağıramıyor."*
> Diğer dördü bilinçle **rütbe 0** → birebir aynı davranış (KURAL B).
> ⚠ **`llm:invoke` = 0 bir KARARDIR:** LLM araçlarını analyst+ yapmak **güvenlik** değil
> **ÜRÜN** kararıdır (viewer'ın cevabı küple sınırlanır) ve bu madde onu vermek için
> kurulmadı. ⚠ **`metric:certify` bilinçle EKLENMEDİ** — sertifikasyon FAZ 1.5'in işi ve
> henüz yok; karşılığı olmayan bir aksiyon, kapanın kendi içinde *"beyan var, kod tanımıyor"*
> üretirdi.
> ⚠ **Erişilebilirlik dürüstçe:** üründe bugün yalnız `owner` var → **bugünkü kullanıcıya
> etkisi sıfır**. Kapatılan şey bir açık değil, bir **değişmezin uygulanabilirliği**.

> ⟳ **`§11-yetki` TUZAĞI ATEŞLEDİ ve TERS ÇEVRİLDİ** (ikinci kez bu operasyonda). §0'ın
> `§11` satırı **daraltıldı** (geriye FAZ 6.1 · onaylı yazma kaldı), belirteç
> `_yazan_arac_sayisi() > 0`'a nişanlandı, ⟳ sayısı **13'te** kaldı. Yeni kapı yalnız
> *"birden çok izin var"* demiyor — biri `contribution.report`'u `query:run`'a geri
> çekerse sayı **yeşil** kalır, kusur **geri döner**; kapı granülerliğin **işe yaradığı**
> noktayı tutuyor.

> 🔴 **FAZ 1'DE BİR SIRA İHLALİ BULDUM (`KAT-3`, FAZ 0'da dört kez çıkan sınıf):**
> `1.5` metrik sertifikasyonu alanları arasında **`lineage_set_hash`** var ve KAPI'sı
> *"**üst-akış kolon kümesi** değişince sertifika düşer"* diyor — ama o kümeyi **`1.6`
> column-level lineage** üretiyor. Bugünkü sırayla `1.5` inerse `lineage_set_hash` ya
> **uydurulur** ya **hep `None`** olur; ikisi de *"beyan var, karşılığı yok"*.
> → **`1.6` ÖNCE, `1.5` SONRA.** *(Madde numaraları D5 gereği DEĞİŞMEZ, yalnız sıra yazılır.)*

### FAZ 0 · adım 14 — `0.21` modül büyüme kapısı **(FAZ 0'IN SON MADDESİ)** *(2026-08-04)*

| Ölçüt | FAZ 0 ÖNCESİ (`c3fcfe7`) | Muafiyet | Tavan | Bugün | Boşluk |
|---|---|---|---|---|---|
| `ask()` kod satırı | 1135 | `9a138a9` **+11** *(0.5)* · `98a5071` **+1** *(0.12/0.13/0.6)* | **1147** | 1147 | **0** |
| `ask()` iç fonksiyon | 19 | **yok** | **19** | 19 | **0** |
| `ask.py` toplam kod | 2394 | *(taşınabilir pay)* | **2406** | 2406 | **0** |
| `cube_router.py` kod | 1723 | `9164806` **+13** *(0.18)* | **1736** | 1736 | **0** |

> 🔴 **BİRİMİ ÖLÇÜM SEÇTİ, TERCİH DEĞİL.** İlk niyet *"ham satır"*dı. Ölçüldü: FAZ 0
> `ask.py`'ye **+44 ham** satır kattı ama yalnız **+12 kod** — **%73'ü belgeleme**. Ham
> satır sayan bir kapı, bu deponun **ölçülmüş kusurları kaydettiği mekanizmayı**
> vergilendirir ve geliştiriciyi *"yorumu silersem yeşile döner"* diye **ödüllendirirdi**.
> Kapı, korumaya çalıştığı bilgiyi yok ederdi. *(`cube_router.py` **%52 belge**.)*

> 🔴 **`ask()` FONKSİYONU, `ask.py` DOSYASI DEĞİL.** Zarar dosyada değil gövdede: 19 iç
> fonksiyon **aynı kapsamı paylaşıyor**. Kodu `ask()`'ten çıkarıp aynı dosyada modül
> düzeyine almak **istenen** yöndür — dosya kapısı onu **cezalandırırdı**. Yine de dosya
> bütünü ayrıca sınırlı, yoksa `ask()` küçülürken gerisi sessizce şişerdi.

> ⚠ **`0619bfd` (0.22) muafiyet listesinde YOK ve bu bir karar:** ham satırda **+8**,
> kod satırında **0** — bildirim `if` bloğundan gövde başına **taşındı**. Bir taşıma borç
> değildir. *Neden listede olmadığı* kapının içinde yazılı, yoksa bir sonraki okuyucu
> eksiklik sanır.

> 🔴 **KAPI KENDİ KIRMIZISINI KANITLIYOR.** Bu operasyonda bir kapı **üç kez** yanlış
> yazıldı ve *"yeşil"* kaldığı için kusuru **taşıyarak** geçti. `test_KAPI_SAHTE_DEGIL_*`
> gerçek kaynağa **bellekte** tek bir kod satırı enjekte edip tavanın aşıldığını
> gösteriyor — ve aynı satır **yorum** olsaydı kapının **sessiz** kaldığını da. Birim
> kararının davranıştaki karşılığı budur, bir niyet beyanı değil.

> ⚠ **İki kendi kusurum daha, ikisi de metin ölçmekten:** (1) *"tavan `==` ile kilitlenmiş
> mi"* testi **kendi assert satırını** yakaladı → AST'e çevrildi (⟳ sayacının 14↔13
> kusuruyla aynı sınıf). (2) MIMARI'ye *"14 test"* yazdım, dosyada **9** vardı — 14 iki
> dosyanın toplamıydı; `test_MIMARI_TEST_SAYILARI` onu **anında** yakaladı.

### FAZ 0 · adım 13 — `§7-CI` yaşam döngüsü · `0.4` netleştirme önceliği *(2026-08-04)*

**Demet 6 kapandı.** Kapı: **3/4 yeşil**, tek kırmızı **kasten kurulmuş bir tuzağın
ateşlemesi** (`test_YURURLUKTE_satiri_HALA_dogru[§7-CI]` — FAZ 0.15 indi). Korpus
**%93,2** (taban %93,2) · semantik vaka **%92,1** · eval precision/coverage **%100** ·
senaryo dokuz sınıf tabanda · süit **2167 geçti**.

| İş | Ne indi |
|---|---|
| **`§7-CI`** | Tuzağın üç adımı: §0 satırı **daraltıldı** · MIMARI §7'ye **ölçümlü ✅** · tuzak **ters çevrildi** |
| **`0.4`** | Karar **`off` KALIYOR** — gerekçesi MIMARI'ye yazıldı · ölçüm aleti + 23 test |

> ⚠ **`§7-CI` talimatı harfi harfine uygulanmadı — ve nedeni ölçüldü.** Tuzak *"§0 satırını
> **SİL**"* diyor; ama o satır **üç şey birden** işaret ediyordu (*çerçeve · CI kapıları ·
> risk-kapsam*) ve **yalnız CI kapıları** indi. Bütünüyle silmek, **inmemiş** bir maddenin
> işaretçisini de silerdi — yani tuzağın engellemek için var olduğu şeyi, **tuzağa uyarak**
> yapardım. Satır daraltıldı, tuzak daralan iddiaya (**FAZ 4.2 · risk-kapsam**) yeniden
> nişanlandı; ⟳ sayısı **13'te** kaldı. Yol haritasının kendi §0 tablosu zaten bu satırı
> yalnız `FAZ 4` ile eşliyordu — daraltma MIMARI'yi yol haritasıyla **hizaladı**.

> 🔴 **`0.4`: İŞ ZATEN ÖLÇÜLMÜŞTÜ, ama KARARIN EVİ YOKTU.** Canlı ölçüm 2026-08-03'te
> yapılmış ve sonucu `features.yml`'nin **YORUMUNDA** duruyordu. Yol haritasının KAPI'sı
> birebir *"nedeni **`MIMARI.md`'ye yazılır**"* diyor — ve MIMARI'de bu maddeden **hiç söz
> edilmiyordu**. Bir YAML yorumu mimari otorite değildir; çelişkide MIMARI kazanır.
> Bir sonraki tur *"ölçülmemiş"* sanıp **kotayı yeniden yakardı**.

> 🔴 **AD ÇAKIŞMASI — MIMARI'de İKİ AYRI «Faz 0.4» varmış.** Eski olan 2026-08-02'nin
> **kapsam kapısı** fazı (`475e691`) ve *"OK **+6** · CUBE-SAPMA **−25**"* taşıyor — yani
> **sıkılaştırma lehine** sayılar. Yeni 0.4'ün kararı **tam tersi**. Ayrıştırılmasaydı
> okuyucu yanlış sayıya bakıp **bayrağı açardı**. Kimlik asimetrisi bu kez **ad düzeyinde**.

> 🔴 **İLAN EDİLEN KAPI BOŞ ÇIKTI — ölçüldü, tahmin edilmedi.** Yol haritası 0.4'ün
> kapısını `lab/nl_corpus.py --kapi` öncesi/sonrası diye yazmıştı. **LLM'siz A/B farkı:
> `0`/41.** Sebep yapısal: `ask.py:2601` ile `:2757` **aynı** netleştiriciyi çağırır,
> ikincisi Intent'ten sonradır ve LLM yoksa Intent dalı hiç koşmaz. Üstelik korpus bu
> nüfusa **hakemlik edemez**: beklenen cube'u soruyu üreten cube'dur, oysa nüfus tam
> olarak *"aynı terimi ≥2 cube sahiplenmiş"* kümesidir — yer gerçeğinin **kendisi
> yazı-turadır**. → Ölçüt **doğruluk değil KARARLILIK**.

> 🔴🔴 **ALETİM YANLIŞ-YEŞİL BASTI — ve kök neden ön uçuşun kendisiydi.** Canlı doğrulamada
> sağlayıcıların **hepsi** `429`/`503` verdi, ama alet **«B · bağlamdan çözüyor»** kararı
> bastı: her tur aynı deterministik düşüşe uğradığı için sonuç *"kararlı"* göründü.
> Ölçülen kararlılık, LLM'in değil **BAŞARISIZLIĞIN** kararlılığıydı.
> **Kök neden:** `_kota_on_ucusu` `generate_sql` ile ön uçuş yapıyor, koşum ise
> **`select_cube`** çağırıyor — **ayrı model, ayrı kota**. Ön uçuş, koşumun kullanmadığı
> yolu sertifikalıyordu. İki düzeltme, ikisi de tek sahipte: (a) ön uçuş artık
> `select_cube`'u **da** deniyor · (b) `karar_ver` LLM katılımını **son koşul** olarak
> arıyor (`self-consistency` izi yoksa `⊘`) — çünkü kota koşumun **ortasında** da tükenir.

> ⚠ **41 ≠ `ask.py`'nin 53'ü — ve ikisi de doğru.** `ask.py` *"≥2 sahip + route çözemiyor"*
> sayıyor; **41** ise chip'in **gerçekten kurulabildiği** küme. *"Belirsiz"* ile
> *"belirsizliği SORULABİLİR"* aynı sayı değil.

### FAZ 0 · adım 12 — `0.17` gecikme bütçesi · `0.20` bayrak profilleri *(2026-08-04)*

| Madde | Ne indi | Ölçüm |
|---|---|---|
| **0.17** | Yol başına **p50/p95** + ilan edilen bütçe (`GET /stats/gecikme`) — **yeni enstrümantasyon YOK**, `duration_ms` zaten `interaction_log`'da | EK D'de 60+ eşik vardı, **tek gecikme eşiği yoktu** |
| **0.20** | Üç profil: **`taban`** (hepsi off) · **`v1-varsayilan`** · **`v1-tam`** + **yaşam döngüsü** borç ölçümü | `taban` 0 açık · `v1-varsayilan` **11/17** · `v1-tam` **19/19** · **ölü bayrak 2** |

> 🔴 **`0.17`'nin çerçevesi DIŞ KANITLA tersine çevrildi.** 240 katılımcılı bir çalışma
> (TTFT 2s/9s/20s): **2 saniyede gelen cevap, 9 saniyede gelenden DAHA AZ** faydalı
> bulundu; **9s en faydalı** koşuldu. *"Streaming algılanan kaliteyi artırır"* iddiasının
> **hakemli çalışması yok**. → Bütçe bir **hız yarışı değil, bir SÜRPRİZ KAPANI**:
> `t2_anlatici`'yi kapalı tutan asıl soru gecikme değil **KAZANÇ** olmalı. Bütçe yalnız
> *"30-85× fark, fark edilmeden büyümesin"* diye var.

> 🔴 **`0.20`'nin asıl işi YAŞAM DÖNGÜSÜ.** `v1-varsayilan`'da **iki sürüm** açık kalan
> bayrak **silinir** (kod kalıcılaşır, bayrak gider) — yoksa §C/10'un *"ölü bayrak 0"*
> hedefi, sayı büyüdükçe **matematiksel olarak** tutturulamaz: her yeni özellik bir
> bayrak ekler, hiçbiri kaldırılmaz. **Bir bayrak bir KARAR ANIDIR, bir mülk değil.**
> ⚠ *"Sürüm"* bu depoda bir **karardır**, otomatik türetilebilir bir sayı değil —
> uydurmak, **ölçüm gibi görünen bir tahmin** üretirdi. Ölçülmemiş borç, borç değildir (`⊘`).

> 🔴 **K1 üçüncü kez yeni bir ucu kurulduğu ANDA yakaladı** (`/metrics` · `/stats/gecikme`).
> Her seferinde `api-only` beyanı **sahibiyle** yazıldı, sessizce değil.

### Taban ölçümü · `lab/vk_taban.py` *(commit `8f87e40`)*
VK-1…VK-6 **yapısal ve canlı** (gemini) ölçüldü. `§G.6e`'nin *"Bugün"* sütunu artık
**yeniden üretilebilir**. Üç satır düzeltilmesi gerekti (VK-4 · VK-5 · VK-6).

> 🔴 **OPERASYONUN EN ÖNEMLİ SAYISI:** **13 turun DÖRDÜNDE** yazım-benzerliği kısa devresi
> öldürüyor → **`AJ0` §G'nin tek en yüksek kaldıraçlı maddesi**; VK-1 · VK-5 · VK-6'yı
> **ilk kapıda** kesiyor, `AJ2`/`AJ5b` sıraya bile gelmiyor.

> ✅ **Çürütülen iddia:** *"`verimlilik` katalogda YOK"* **yanlıştı** — `verim` + geçerli ek
> zinciriyle kapsanıyor (`oee.ort_oee`). Asıl eksik **ÜRÜN BOYUTU** (`R9`), ve o
> **tenant-özel** (`stok_adi` gitas'ta VAR).

---

## 📋 AÇIK BORÇLAR — unutulmayacak

| # | Borç | Nerede kapanır |
|---|---|---|
| 1 | `0.23` **kapısız iner** (düzeltmesi bağımsız, `KAPI`'sı `K2/(c)`) | **FAZ 0.14** — geriye dönük |
| 2 | Bölüm II'nin **17 maddesinde `GERİ AL` yok** | Madde **sıraya alındığında** (kapı: 0.14'ün `test_yol_haritasi_butunlugu.py`) |
| 3 | Belgede **8 kusur** kaldı *(FAZ −1'de `−1.1` 6↔13 ve `A6` kapandı)*: sayı çelişkileri (v2 kapsamı · §G aralığı · `KAT-1…4` başlığı · EK K 24↔29) · **4 ölü bayrak** · `II-D.1b` tanımsız · **iki biçim hatası** (`GERİ AL` blokları yanlış faz başlığı altında) · FAZ 7 kapsamı (Plan 2 dalı) | İlgili faza gelindiğinde — **ayrı tur AÇILMAZ** |
| 4 | `is_period_only` hâlâ **0 çağıran** | 0.14/K2 |
| 5 | Deneyim süitinin **bilerek açık kırmızısı**: *"o ayı makine bazında aç"* | II-D *(satır çapası)* |
| 6 | **`A13` yarım indi:** `§1.5 · §2.1 · §3.2 · §4.4` düzeltildi, **`§1.6` + `§1.7` atıfları duruyor** — `MIMARI.md` satır **559 · 621 · 663 · 886 · 916 · 1298 · 1844 · 1965 · 2001 · 2079 · 2092 · 2582** *(denetim A/(a)1 · kendi ölçümüm doğruladı)* | FAZ 0.14'ün belge kapısı |
| 7 | **`A11` yarım indi:** uzlaştırma bloğu yazıldı ama **sabit sayılar yerinde** — `93` → `MIMARI.md:605 · 737 · 738`, `105` → `2762 · 2765`. Bir kısmı **tarihli olay kaydı** (meşru), bir kısmı **bugünü anlatıyor** (D2 ihlali); ayrımı madde sırası gelince yap | FAZ 0.1 *(yeniden ölçüm turu)* |
| 8 | **`D1` beyanı FAZ −1'in üç maddesinde YOK** — `backend·sözleşme·frontend` üçlüsü de `api-only`/`belge` muafiyeti de yazılmamış *(muafiyet meşru, **beyan** eksik)* | FAZ 0.14 |
| 10 | 🔴 **Korpus kapısı 13 dk 18 sn** — ilan edilen *"3,5 dk"* yanlıştı (düzeltildi). Duvar saatinin **%71'i `boyahane`** (5306 soru / 8'49"). ⚠ **Seyreltme YAPILMAMALI:** `nl_corpus.py:141` *"ham tur paydası KORUNUR (KURAL A)"* diyor ve korpusun tek yakalaması **paydanın değişmesiydi**. Doğru yol **paralelleştirme** (şirketler ayrı süreç) — payda birebir aynı kalır | Kullanıcı kararı bekliyor *(kapsam: ölçüm aracı)* |
| 11 | ✅ **KAPANDI** — çapraz-cube geçişi **kavram düzeyinde** eşleşiyor (`cekirdek_metrik`), grain değişimi cevabın notunda **söyleniyor**, `kiyaslanamaz` ölçüye geçilmiyor, belirsiz varyant **reddediliyor** | ✅ 2026-08-04 |
| 9 | **Yol haritası `−1.2` tablosu (12 satır) ↔ `MIMARI §0` (13 satır) ayrıştı**, D5 kütüğü bırakılmadan: MIMARI'de **eklenen** `§5/18. yasak → §G/AJ0`; **değişen otoriteler** §8.2 `4.7→4.6` · §9 `2.2→0.18·2.1` · §12 `6./7./8.→6./7.` · §7 `FAZ 4→0.15·FAZ 4` · §4 `6.1→6.0→6.1→6.2`. 🔴 **Beşinde de MIMARI DOĞRU, yol haritası bayat** | FAZ 0.14 |
| 10 | **`A9`/`A12`'nin kanıt satır numaraları bayat** — `A9` *"2567·2571·2630"* diyor, gerçek `2804·2808·2867`; `A12` notu *"1309. satır"* diyor, bugün `1348`. *(A6'nın düştüğü hatanın aynısı; ikisi de **zararsız** çünkü düzeltmeler indi)* | FAZ 0.1 |
| 11 | 🔴 **KENDİ BULGUM (0.23'ü koşarken ölçüldü): raporlanabilirlik kuralının BEŞ sahibi varmış, 0.23 yalnız İKİSİNİ kapatıyor.** Kalan üç sahip: `page.tsx:100` (`latestReportable` — tuvale ekle hedefi) · `page.tsx:114` (`addToCanvas`) · `page.tsx:139` (`lastReport` — **resume çapası**) · `ChatPanel.tsx:196` (thread listesi önizlemesi). **Neden AYNI TURDA kapatılmadı:** ikisi (tuval) `AnalysisCanvas.tsx:82`'nin `it.cube_query && it.result` kapısına bağlı — genişletmek **sessizce boş bir tuval kartı** doğururdu; o yüzey **`0.3`'ün konusu** (K4 `test_yuzey_sadakati.py`). Diğer ikisi (`page.tsx:139` · `ChatPanel.tsx:196`) **serbest ve güvenli**, ama `0.23`'ün `NE`'si açıkça yalnız `ReportPanel` diyor → kapsam sessizce genişletilmedi. `raporlanabilir()` **export edildi**, üçü de ona bağlanacak | **FAZ 0.3** *(aynı fazda, «kalan» adımı)* |
| 12 | `R1` **`raporlanabilir()` İKİ İŞ yapıyor** — hem *"kart render et"* hem *"`viewHint` kime gider"*. Contribution kartı `lastReportableIdx` olunca önceki tablo kartı `viewHint={null}` alır → `ResultView` remount, hint'li görünüm sıfırlanır. **Kilitleyen test YOK** (`grep viewHint backend/tests` → 0) | **FAZ 0.14** *(K2 kapıları)* |
| 13 | `R4` **0.22 kapısı metin penceresiyle** ayırt ediyor (3 satır). Bugün doğru; 2773 civarına *"migration_trace"* geçen bir **yorum** eklendiği gün yanlış-yeşil. Yapısal alternatif: `stack()[1].frame.f_locals["migration_trace"] is <arg>` **kimlik kıyası** | **FAZ 0.14** |
| 14 | `R5` **`_yururlukte_satirlari` biçime bağlı** — `satirlar[2:]` §0'da tek tablo + tam iki başlık satırı varsayıyor; başlık metni değişirse `str.index` **ValueError**. *(Yön fail-closed, sessiz-yanlış değil)* | **FAZ 0.14** |
| 15 | `R8` **Chip'ler maskeli-boyut süzgecini paylaşmıyor** — `answer.py:441-447` maskeli kolona filtre kuran chip'leri eliyor; `_intent_uyusmazlik_chipi` kendi chip'lerini kuruyor ve `_attach_next_steps` `result is None` diye erken dönüyor. 0.23 bu chip'leri **görünür yaptı**, süzgeci paylaşmadı → *"boş dönen chip"* riski | **FAZ 0.14** |
| 16 | 🔴 **Canlı turun kalan beş bulgusu** *(C)*: (a) çelişki sorulduğunda cevap yok, aynı rapor yeniden çiziliyor → **5.0/5.3** · (b) *"ne yapmalıyız"* çıkmaz sokak, `prescription` hiç dolmuyor ve kullanıcının *"o zaman kg üzerinden bak"* düzeltmesi **yok sayılıyor** → **FAZ 5** · (c) tek kelimelik düzeltme (*"yok haziran olsun"*) arkada `Unknown filter dimension 'tarih' in cube 'enerji_tesis'` **iç hatası** + konu kaybı → **hata, 0.x'e alınmalı** · (d) chip'e tıklayınca küp değişti (`enerji_tesis` → `surdurulebilirlik`) — iki *"elektrik"* iki farklı sayı → **0.4 netleştirme** · (e) **veri sonu tarihi hiç söylenmiyor**; kullanıcı üç turunu bunu keşfetmeye harcadı → **§C ölçüt 12 (tazelik), bugün 0** |
| 17 | 🔴 **SESSİZ-YANLIŞ: *"değişim"* istendi, **TOPLAM** verildi.** Canlı tur t14: *"ocak ile haziran arasında makine bazında fire değişimi"* → `compare=None`, kıyas yok, ay yok, **uyarı da yok**; kendinden emin bir toplam tablosu. Kullanıcı: *"veri doğru, **cevap yanlış soruya**"*. Kök neden `cube_router.compare_mode` bu ifadeyi tanımıyor | **FAZ 0.5b / cube_router** *(kıyas ekseni)* |
| 18 | 🔴 **AJ0 canlıda DOĞRULANDI — çıkışsız yazım düzeltmesi.** t12/t13: *"…fire ne kadar arttı"* → *"«artti» yerine «parti» mi demek istedin?"*, **doğru yazınca da aynı**, ve sunulan tek şık gramersiz bir cümle (*"…fire ne kadar parti"*). Kullanıcı: *"Ben «artti» yazmadım ki… düzeltmenin yolu yok, çıkış kapısı kapalı."* VK ölçümü *"13 turun dördü buradan ölüyor"* demişti — **canlıda tekrar üretildi** | **§G/AJ0** *(operasyonun en yüksek kaldıraçlı maddesi)* |
| 19 | 🔴 **`bakiye` iki cube'ta, seçim SESSİZ — ve fark ₺11,86 MİLYON.** t11 `cari` → **₺11.859.052,65**; t15 `mizan` → **₺0**. Sistem birini kura ile seçti, sormadı, seçtiğini yazmadı; `next_steps`'in 6 şıkkının hiçbiri *"cari mi mizan mı?"* demiyor. ⚠ **SAHİP DEĞİŞTİ (2026-08-04):** `0.4` ölçüldü ve bayrak **`off` kaldı** — yani bu borcu `0.4` **KAPATMIYOR**. Ölçüm ayrıca gösterdi ki model *"bu yıl bakiye"*de **kararlı** biçimde `mizan`'ı seçiyor: bu bir motor kusuru değil **katalog kararıdır** (*bare `bakiye` hangi cube'un?*). Kapalı bir bayrağı borcun sahibi göstermek, borcu **görünmez** kılardı | **FAZ 3.1** *(sahiplik turu; `metrik_kaydi` çakışmayı görünür kılar, KARARI VERMEZ)* |
| 19b | 🔴 **AYRIŞTIRILDI (#19'dan):** mizan sorgusunda *"bu yıl"* filtresi **sessizce düştü**. Bu bir katalog kararı DEĞİL, bir **kusurdur** — ve #19 ile aynı satırda durduğu sürece sahibi `bakiye` tartışmasının altında kalıyordu. Dönem filtresinin bir cube'ta uygulanıp ötekinde düşmesi, `0.10`'un dönem ekseni işiyle aynı sınıf | **`cube_router` / dönem ekseni** *(sahip atanacak — FAZ 1 girişinde)* |
| 20 | **Üstünlük ifadesi cevaplanmıyor:** t06 *"hangi makinenin fire oranı en yüksek bu yıl"* → `source=catalog`, **satır yok**, ürün kataloğu dökümü. Ama t07 *"makine bazında fire oranı bu yıl"* → 11 satır, doğru cevap. Kullanıcı: *"Sistem kendi bildiği şeyi bana yasaklıyor… kendimi aptal hissettim"* | **cube_router** *(liste/üstünlük niyeti)* |
| 21 | **Onay kartına SÖZLE «evet» işlemiyor:** t08 kart *"…panona ekleyeyim mi?"* diye **cümleyle** soruyor; t09 *"evet ekle"* → *"geçerli bir alan veya değişiklik belirtmemektedir"*. Halka yalnız **fareyle** kapanıyor. *(Düğme yolu ✅ çalışıyor: t10 «Rapor panona eklendi».)* | **FAZ 6** *(eylem/onay akışı)* |
| 22 | **Ham kolon adı + saat damgası ekranda:** `tarih__year: 2026-01-01 00:00:00`. Kullanıcı: *"Ben yıl sordum, bana veritabanı sütun adı ve saat 00:00 gösteriliyor."* | **FAZ 0.10b** *(görünen adlar)* |
| 23 | **330 satır, sıfır içgörü:** t05'te kırılıma tıklamanın sebebi *"hangi makine kötü"* idi; dönen tek cümle sistemin **yapmadığı** işi anlatıyor. Kırılımlı oran görünümünde en azından **sıralama** verilebilmeli *(bugün toplanamadığı için susuyor — doğru ama yetersiz)* | **FAZ 5** *(anlatı) + 0.10b* |
| 24 | 🔴 **`pytest-xdist` ÖLÇÜLDÜ: 100 sn ↔ 510 sn — ama 360 hata.** Paralel koşum süiti **5 kat** hızlandırıyor, ancak `session` fixture'ları ve compose kilidi (`metadata.yml`) worker'lar arasında çakışıyor. **Bedava değil**; benimsenmeden önce izolasyon işi gerekir *(muhtemelen worker başına ayrı `DIMA_DATABASE_URL`/pack dizini)*. Kazanç büyük olduğu için borç olarak duruyor | **FAZ 0.15** *(CI kapıları — aynı izolasyon işi orada da lazım)* |

---

## ✅ DENETİM — **AJANLAR KULLANILIR** *(yanlış teşhis geri alındı, 2026-08-04)*

> 🔴 **DÜZELTİLMİŞ TEŞHİS.** Bir süre burada *"arka plan ajanları ana sohbeti sildi →
> alt-ajan KESİN YASAK, `OPERASYON-DENETIM.md` silindi"* yazıyordu. **O teşhis YANLIŞTI**
> ve dosya da **silinmemişti** (`git status`: ` M`, duruyor). Olayı inceleyen kişi ölçtü:
> sebep başarısız bir **daemon yükseltmesiydi**, arka plan işçilerini öksüz bıraktı.
> Kullanıcı: *"ben yanlış anlamışım, en güçlü yanımız olan ajanlarmış."*
>
> **Ders — teşhisin kendisi de kanıt ister.** Bir olayla **aynı anda** olmak, o olayın
> sebebi olmak değildir. Bu depo tam bu sınıfı avlıyor (`A6`'nın düşme gerekçesi) ve aynı
> hata **kural setinin kendisine** uygulandı: ölçülmemiş bir nedenle çalışan bir mekanizma
> kapatıldı. **Denetim `OPERASYON.md §7`'ye göre üç ajanla koşar** (`A` plan · `B` bütünlük ·
> `C` canlı kullanıcı); görev metinleri `OPERASYON-DENETIM.md`'de.

**Disiplin korunuyor** — çünkü değeri ölçüldü: o turlar belgede **15 kusur** buldu, ölçüm
aracı **12+ kez** yanlış çıktı, ve iki **P0 sessiz-yanlış** (pivot trend · `eylem_onerisi`
kartı) yalnız **canlı kullanıcı turunda** göründü. **Aşağıdaki bulgular tarihsel kayıttır
ve silinmez** (ADR-0019).

**Geçmiş turların işlenen bulguları** *(kritik olanlar sıradaki maddeden ÖNCE kapatıldı)*:

| Bulgu | Ne yapıldı |
|---|---|
| `§3.4-osi` tuzağı **yanlış-NEGATİF** — faz indiğinde susardı (belirteç `ossie_import.py` arıyordu, FAZ 3.4 ise `POST /connections/{id}/import-semantic` + `ossie_ithal` bayrağı vaat ediyor) | belirteç **fazın kendi vaadine** bağlandı (uç ∨ bayrak ∨ modül) |
| Kural-beyanı kapısı hâlâ **METİN** ölçüyordu (üç birebir Türkçe ifade) | **yapısal kapı** eklendi: her satır **dört hücreli işaretçi** + `Durum == ⟳ UYGULANMADI` + otorite fazı; ifade taraması artık *"tel tuzağı"* olarak **sınırı yazılı** duruyor |
| `test_MIMARI_ANILAN_MODULLER_VAR` **biçim körlüğü** — MIMARI `cube_router`'ı 18 kez anıyor, hep `app/` öneksiz → deponun en merkezî modülü `skip` ediliyordu | çıplak modül adı da (kelime sınırıyla) sayılır → **12 ✅ · 2 ⊘** yerine **14 ✅** |
| Yeni kapının `MUAF` listesi **ölü doğmuştu** (üç girdinin üçü de MIMARI'de hiç geçmiyor) | liste **boşaltıldı**, gerekçesi yazıldı |
| `A9` üçüncü satırı (`MIMARI.md` *"8984 turda ~%64"*) ve `A5`'in MIMARI tarafı (*"pytest 1016 geçti"*) **D2 ihlali olarak duruyordu** | ikisi de **komuta çevrildi** |
| Yeni kapı dosyası MIMARI'de anılmıyordu (D4) | §0'a **kendi kapıları** satırı eklendi |
| `test_orkestrator.py` MIMARI'de **25**, gerçek **29** | ⚠ **kapı kendi kendini yakaladı** — düzeltildi |

---

## 📌 ÖLÇÜM TABANI *(D2: sayı + damga + komut)*

| Ölçüt | Değer | Damga | Komut |
|---|---|---|---|
| Test *(toplanan)* | **2068** | `0619bfd`+ | `python lab/faz0_taban.py` |
| Test *(geçen/atlanan)* | kapı özetinden | `0619bfd`+ | `python lab/kapi.py --tam` |
| eval | `+0,0 / +0,0 / +0,0` | `0619bfd` | `python -m eval.run` |
| Korpus doğru-cube | **%93,2** · yanlış cube **458/7213** | `0619bfd` | `python lab/nl_corpus.py --kapi` |
| Konuşma senaryoları | **düşürülen 0** · 1 ⊘ (`vqr_kalicilik`) | `0619bfd` | `python lab/kapi.py --tam` |
| TypeScript | **0 hata** | `0619bfd`+ | `./node_modules/.bin/tsc --noEmit` |
| ESLint | **0 hata** *(4 eski uyarı)* | `0619bfd`+ | `./node_modules/.bin/eslint .` |

> ⚠ **D2 düzeltmesi (denetim buldu):** damga sütununda sha yerine faz adı yazılmıştı ve
> `--collect-only` *"2056 ✅ · 0 ⊘"* iddiasını **üretemez** (geçen/atlanan ayrımı vermez).
> Tek komut iki iddiaya kaynak gösterilemez — satırlar ayrıştırıldı.
| Deneyim süiti (canlı) | **41 ✅ · 1 ❌ · 63 ⊘** | `88bde2a` | `python lab/deneyim.py --live` |
| VK taban | **§G.6e kutusu** | `8f87e40` | `python lab/vk_taban.py --live` |
| Motor-RLS | **0** | `8f87e40` | `grep -rc rowLevelAccessControl backend/app/` |
| Bayrak | `FLAG_REGISTRY` **16** ↔ `features.yml` **14** | `8f87e40` | — |
| Panel export | **13** *(tavan DOLU)* | `88bde2a` | `grep -rE "export (default )?function [A-Za-z]+Panel" src/ \| wc -l` |
| Konuşma türü | **5** *(v1 hedefi 7)* | `8f87e40` | `grep -cE "^TUR_[A-Z_]+ = " backend/app/followup.py` |

### 🔴 FAZ 4.3'ün ÖLÇTÜĞÜ BORÇ — `deterministic_refine`'ın ölçü-ekleme kapısı DAR

**Ölçüm** (`python lab/sharding.py`, `demo-boyahane`, 44 konuşmalık sabit kohort):
tur 1 **%63,6** → tur 5 **%45,5** = **−%18,2**. Hedef **−%10** idi → **KALDI**.
*(Makalenin ölçtüğü −%39'un yarısından az; ama kendi hedefimizi tutturmadık.)*

**Kök neden isimlendirildi** — kayıp turlar tek tek okundu, hepsi **aynı şekilde**:
takip mesajı **çıplak bir ikinci ölçü adı** (*"fire orani yuzde"*, *"ort brut maas"*).
`deterministic_refine` ölçü eklemeyi *"bir de … ekle"* ipucuyla tanıyor (FAZ B1'de
canlıda doğrulanmıştı); **ipuçsuz çıplak ölçü adı** bir yenileme sayılmıyor, tur
`route()`'a düşüyor ve orada tek başına bir ölçü adı taban üretmiyor (R1/R10).

⚠ **Bu turda DÜZELTİLMEDİ, bilerek.** FAZ 4.3'ün `GERİ AL` şartı: *"ölçüm harness'i —
davranış değiştirmez"*. Ölçtüğü kusuru aynı turda düzelten bir alet, bir dahaki sefere
neyi ölçtüğünü bilemez — taban kaybolur.

**Kapatma şartı:** `deterministic_refine` çıplak ölçü adını *"aynı cube'un ikinci
ölçüsü"* olarak tanıdığında `lab/sharding.py` yeniden koşulur ve karar `gecti` olmalı.
⚠ Aynı turda `nl_corpus` gerilememeli — ölçü-ekleme kapısını genişletmek, bugün
**boyut** sanılan kelimeleri ölçüye çekebilir.

**Diğer üç şirket `⊘`:** kohortları 7–10; hedef o çözünürlükte ayırt edilemez.

---

## ⟳ DENETİM RAPORU KÖK ÇÖZÜMLERİ — 2026-08-06 turu

### İnenler (demet kapısı ✓ yeşil · korpus %94,3 · dört şirket ayakta)

| # | Ne | Ölçülen kazanç | Commit |
|---|---|---|---|
| **7e** | ay çekimi tek sahipten (`_AY_ADI_RE` + `_ek_gecerli`, iki tüketicide) | %18 → **%100** (60/60) | `4cc2ab5` |
| **7c** | çok-geçiş: yedi dönem kalıbı `.search` → `.finditer` | `beyanli_kismi` 57→**58**, sessiz-yanlış **12 sabit** | `befafbb` |
| **7a** | `in q` yasağı: **25** sözlük taraması `_syn_hit`e bağlandı | `trendyol`→trend · `bu ayrica`→bu ay · `uygun`→gun kapandı; hiçbir ölçü gerilemedi | `5b834ab` |
| **ölçüm** | gerçek-dünya korpusu **bayat artefakttan** okuyordu | aynı kaynakta 8↔17 sapması bitti | `771137c` |
| **hijyen** | `--user` zorunluluğu + taze şema kuralı `CLAUDE.md`'ye | üç şirketin sessizce düşmesi kapıya bağlandı | `1d4ea92` |
| **7b** | ⊘ denendi, ölçüldü, **inmedi** — karar kaydı | — | `67684f3` |

### 🔴 BU TURUN EN PAHALI DERSİ — ölçüm aracı yalan söyledi

`backend/demo/wren-project` **gitignore'lu bir derleme artefaktıdır** ve `git checkout`
onu geri almaz. `lab/gercek_dunya.py` şemayı oradan okuyordu (`nl_corpus.py` ise taze
derliyordu) → **aynı kaynak durumda** `sessiz_yanlis` **8 ve 17**, `dogru` **83 ve 80**.

⊙ Bedeli somut: bu turda **üç katalog çakışması** "çözüldü", yeşil göründü, sonra bayat
çıktı ve geri alındı. **7b bir kez 8 sessiz-yanlışla yeşil görünüp neredeyse indi**;
taze derlemeyle gerçek sayı **30**'du.

> *Bir ölçüm aracının bayat okuması, yanlış bir sonuçtan daha kötüdür: yanlış sonuç
> sorgulanır, bayat okuma güvenilir.*

Kapılar: `tests/test_olcum_semasi_taze.py` (5) · `CLAUDE.md` koşum hijyeni (2 yeni kural).

### ⊘ KÖK-7b — ölçütü tutturdu, ürünü bozdu

§4 probu **%31,2 → ≥%90**, `_STOP_STEMS`'e **0** kelime eklendi — ölçüt tam tuttu.
Ama gerçek-dünya: **kabul 1150 → 1117**, **sessiz_yanlis 12 → 30**. Kayıp `kabul`den
`sessiz_yanlis`e **taşındı**: yapısal dolgu anlamlı kelimeleri de yutunca soru
*anlaşılmış gibi* görünüp yanlış cube'a gidiyor.

🔴 **7b'nin evi kapsam kapısı değil, KÖK-9'dur** (belirsizlik→chip). Raporun kendi
şartı: *"kapı, «bilmiyorum» ile «iki adaydan hangisi?» ayrımını korumak zorundadır."*
Tam gerekçe + sonraki tur yönü: `tests/test_kok7b_karar_kaydi.py`.

### Sıradaki

1. **KÖK-9** — tek teşhis kaynağı (R10'u kapı sırasında başa al) + **belirsizlik→chip**.
   ⚠ Ön ölçüm var: `metrik_kaydi` `sapma`→2 aday, `parti sayisi`→2, `adet`→**6** aday
   biliyor ve `sahiplenilen_terimler` hepsinde **BOŞ** — yani sistem belirsizliği
   *deterministik olarak biliyor* ve yine de tahmin ediyor.
   🔴 Ve bir anti-çözüm ÖLÇÜLDÜ: belirsizlikte **koşulsuz** reddetmek korpusu
   %94,3 → **%83,6** düşürdü. Cube-düzeyi eşleşme **gerçek bir kanıttır**;
   *bir ilkeyi doğru bulmak, onu her yere uygulamak için yetmez.*
2. **7d** (türetme, fail-closed) — 7b'nin dersinden sonra: kapsamı açmasın, chip üretsin.
3. **KÖK-1** — Niyet nesnesi (mimari).

### ⟳ İkinci demet — KÖK-9 ve zincirleme bulgular (2026-08-06)

| # | Ne | Ölçülen | Commit |
|---|---|---|---|
| **KÖK-9** | bilinen belirsizlik **chip'e** bağlandı (reddetmeye değil) | kayıt **62/62** terim çok-sahipli, cevapların **%11,7'si** beyansız → beyanlı; **kapsam maliyeti 0** | `684acbc` |
| **kapı seçimi** | büyüme tavanları ÇEKİRDEĞE | frontend kapısı **üç commit** kırmızıymış, görülmemiş | `99f5250` |
| **uydurma sayı** | koşulsuz `COUNT(*)` dalı kapatıldı | 4 anlamsız soru → aynı **37 878**; korpus **%94,3 → %95,1** | `ce5177d` |
| **KÇ-5** | tek teşhis kaynağı (`teshis()`) | reddin **%43,2'si** yanlış yeri işaret ediyordu (R1'in **646'sı**) | `de52c00` |

### 🔴 BU DEMETİN DERSİ — bir düzeltme, üç gizli kusuru ortaya çıkardı

`test_uydurma_sayi_yok` kural motorunun "her şeye SQL üret" dalını kapatınca:
1. `test_kok8a::test_UCTAN_UCA_KAYIT` **yıllardır atlanıyordu** ve ilk kez koştu;
2. koşunca kırmızı verdi ama sebebi **red yolu değildi** — bu ortamda **başarılı bir
   soru da** kayıt yazmıyor (ölçüldü: 0 satır) → ⊘ gerçek sebebiyle yazıldı;
3. `_sema()` yardımcısında unutulan bir import **`except Exception`de yutuldu** ve
   etkileşim kaydını tamamen sessizleştirdi.

> *Bir kapının ölçemediğini ölçtüğünü sanması, hiç ölçmemesinden kötüdür.*
> *En tehlikeli hata, bir hata yolunun içinde doğan hatadır.*

### Sıradaki

1. **7d** — türetme (`sattık`→`satis_tutari`), **fail-closed**: 7b'nin dersinden sonra
   kapsamı AÇMAYACAK, chip üretecek.
2. **KÖK-1** — Niyet nesnesi (mimari; en büyük kalem).
3. ⊘ Açık kalanlar: `_STOP_STEMS` asimetrisi (`yaptık`✅/`verdik`❌) —
   `tests/test_kok7b_karar_kaydi.py`'de yazılı; evi KÖK-9 idi ama **chip yolu** üzerinden
   çözülmeli, kapsam kapısı üzerinden değil.

### ⟳ Üçüncü demet — KÖK-7d + tam süit taraması (2026-08-06)

| # | Ne | Ölçülen | Commit |
|---|---|---|---|
| **7d** | türetme katmanı, **fail-closed** | 3 hedef vaka chip alıyor; korpusta sahte aday **191 → 0** | `87efacc` |
| **tarama** | tam süit bir kez koşuldu | 🔴 **15 kapı kırmızıymış** — 2'si gerçek ürün kusuru | `89a2c4d` |

🔴 **KÖK-7 TAMAMLANDI**: 7a · 7c · 7d · 7e indi; 7b ölçülüp **reddedildi** (karar kaydı
`tests/test_kok7b_karar_kaydi.py`).

### 🔴 EN PAHALI DERS — yerel kapının korpusa indirilmesi 15 kırmızıyı gizledi

Bunların **ikisi gerçek**: `MeasurePreview.unit` eksikliği önizleme ucunu bir demet
boyunca **409**'da tuttu; uydurma-sayı düzeltmem meşru **satır dökümü** yolunu da kesti.
Korpus ikisini de göremez — o `route()`u ölçer, Discovery'yi ve HTTP uçlarını değil.

⚠ Politika DEĞİŞMEDİ (kullanıcı kararı), iki şart eklendi (`backend/CLAUDE.md`):
gecelik CI'ın `--hepsi`yi gerçekten koştuğu **doğrulanmalı**; merkezî dosya değiştiren
demetlerde demet sonu `--hepsi` (4-6 dk).

### Sıradaki
1. **KÖK-1** — Niyet nesnesi (mimari; raporun son büyük kalemi).
2. ⊘ `_STOP_STEMS` asimetrisi (`yaptık`✅/`verdik`❌) — 7b'nin karar kaydında yazılı;
   çözümü **chip yolu** üzerinden olmalı, kapsam kapısı üzerinden değil.

### ⟳ Dördüncü demet — KÖK-1 FAZ 1 (2026-08-06)

**🔴 DENETİM RAPORUNUN DOKUZ KÖK ÇÖZÜMÜNÜN HEPSİ ELE ALINDI.**

| # | Ne | Durum |
|---|---|---|
| KÖK-1 | Niyet nesnesi | ✅ **Faz 1 indi** (gözlemci + iz + bayrak) · Faz 2 sıradaki |
| KÖK-2/3 | Uyum kapısı + beyanlı kısmi | ✅ indi |
| KÖK-4 | Takip turunda dönem çapası | ✅ indi |
| KÖK-5 | Derleme-zamanı katalog kapısı | ✅ indi |
| KÖK-6 | Yetenek beyanı | ✅ indi |
| KÖK-7 | Tek biçimbirim sahibi | ✅ 7a·7c·7d·7e indi · **7b ölçülüp REDDEDİLDİ** |
| KÖK-8 | Kendini bildiren ölçüm | ✅ indi |
| KÖK-9 | Tek teşhis + belirsizlik→chip | ✅ indi |

#### KÖK-1 Faz 1 — raporun kendi ölçütüyle

> *"`Niyet` üretilir ve **loglanır**; `route()` davranışı **BİREBİR aynı** kalır.
> Sıfır gerileme, tam görünürlük."*

⊙ `app/niyet.py` — **tek bir regex yok**; her alan mevcut bir çözümleyicinin çağrısı
(`test_YENI_DILBILIM_YAZILMADI` AST ile kilitler). Bayrak `niyet_izi: "prod"`,
kapalıyken **tek satır bile** eklenmez.

🔴 Ölçülebilir hâle gelen şey: `ocak ve haziran ciro` → `dönem=2(çözülemedi)` ·
`🔴temsil-yok=cok_donem`. *Bir sistemin temsil edemediği şeyi SAYABİLMESİ, onu
görebilmesinin ilk adımıdır.*

⚠ Ve kapı iki gerçek ayrışma buldu: `_cok_donem` göreli dönemi saymıyordu (iz kendi
verisiyle çelişiyordu); `AskJob.trace_json` yayımlanan izle ayrışıyordu — *bir kaydın
canlı hâli, yayımlanan hâline yakınsamalıdır; yoksa kayıt bir tarih değil bir taslaktır.*

#### ✅ KÖK-1 FAZ 2 — ilk müşteri (`app/uyum.py`) TAŞINDI

⊙ Göç **ölçüldü, tahmin edilmedi**: 2 270 korpus sorusunda yedi soru-sinyalinin
**YEDİSİ DE** birebir aynı → sonra taşındı. Kapı: `test_FAZ2_ESDEGERLIK`.

🔴 Ve göç bir **tasarım gerçeği** ortaya çıkardı: `Niyet` çözümleme ile eşleştirmeyi
karıştırıyordu (*"kırılım İSTENDİ mi"* ≠ *"hangi boyut EŞLEŞTİ"*). Raporun KÖK-1
başlığı zaten buydu. Nesne ikiye ayrıldı: `coz_soru()` **şemasız** (dil), `coz()`
**şemalı** (katalog).
⊙ Ayrımı zorlayan şey bir tercih değil **ilk müşterinin sözleşmesiydi**: `uyum.denetle`
şema almıyor. *Bir soyutlamanın doğru sınırını, onu ilk kullanan çizer.*

⊘ **ÜSTÜNLÜK bilerek taşınmadı**: `_ustunluk_mu` `ic`+`cube_meta` ister (ipucu bir ölçü
adının içindeyse ipucu değildir — `kur` cube'unun ölçüsü literal *"en yüksek kur"*).
O denetim **eşleştirme** tarafıdır. `test_USTUNLUK_BILEREK_TASINMADI` sınırı yazılı tutar.

#### ⊙ KÖK-1 FAZ 2 — kalan dört tüketici ÖLÇÜLDÜ, üçü TAŞINMAYACAK

| tüketici | soru tarafında ne okuyor | karar |
|---|---|---|
| `donem_capasi` | 1 sinyal (`is_all_time`) — **zaten tek sahipli** | ⊘ taşınmaz |
| `yetenek` | 3 sinyal, 2'si **şemalı** kendi dedektörü | ⊘ taşınmaz |
| `turetme` | **0** — `bilinmeyen` listesini ALIR | ✅ **çağrı yeri taşındı** |
| `belirsizlik_chipi` | **0** — eşleşmiş `terim`i ALIR | ⊘ taşınacak bir okuma yok |

🔴 KÖK-1'i doğuran **çoklu-sahiplik bu dörtte yok**. `uyum` soruyu yedi kez tarıyordu;
bunlar ya hiç taramıyor ya zaten tek sahipli birini çağırıyor. *Taşımak kusur kapatmaz,
yalnız bir dolaylama ekler* — ve bu deponun kuralı dolaylamayı bedava saymaz.

#### ✅ Ama GERÇEK bir tekrar ölçüldü ve kapatıldı
Reddedilen bir soruda `partial_unknowns` **4 kez** koşuyordu. İki iş yapıldı:
· **istek-kapsamlı bellek** (`niyet.bellek_sifirla()`, `reset_llm_usage()` ile aynı yerde)
· `_turetme_adaylari` artık `Niyet.bilinmeyenler` okuyor
⊙ **4 → 3.** *Bir soyutlamanın benimsenmesi, ona girmenin maliyetiyle ters orantılıdır.*

#### Sıradaki
Kalan **tek** doğrudan çağrı `ask.py:2959` — `unknown` ve `hits`i **birlikte** kullanıyor.
`Niyet`e `hits` alanı eklenirse 3 → 2 olur; eklemeden yarım taşımak, alanı iki yerde
tutmak olurdu.

---

## ⟳ GARSON FAZI — `G6` KIYAS CEBİRİ (2026-08-07)

### İnen üç şey

| # | Ne | Ölçü |
|---|---|---|
| 1 | **Kapı yarısı** — kıyas fiili artık *sayılıyor*, `" ile "` aşırı-yüklenmesi çözüldü | sessiz **244 → 0** |
| 2 | **Kapsam yarısı** — `app/kiyas_cebiri.py`: mutlak kıyas → göreli kıyas indirgemesi | **122** soru gerçek kıyas hesaplıyor |
| 3 | **`B-G4` kapandı** — Intent-JSON'a `compare` girdi, `parse_cube_query` artık düşürmüyor | `5.6` (peer) **açıldı** |

⊙ 408 kıyas sorusu: reddedilen 103 · cevaplandı 305 → *(122 kıyaslı · 183 etiketli ·
**0 sessiz**)*.

### ⊘ `R11` DENENDİ ve GERİ ALINDI — kapı bir kararı çürüttü

*"Anlaşıldı ama ifade edilemez"* kodu yazıldı; tarama **30/408** nüfus gösterdi. Kapı
(`test_TANINAN_SORUDA_HAM_KOD_KORUNUYOR`) çürüttü: o sorularda **gerçek** gerekçe zaten
vardı (`R9`, `R1`, …) ve `R11` onu **örtüyordu**. `KÖK-9`'un dersi birebir geçerli:
*kusuru gizlemekten daha kötüsü yanlış yeri işaret etmektir.*

⊙ **Ders:** *bir sayının varlığı, o sayının doğru şeyi saydığının kanıtı değildir.* Ters yön: kıyas **istemeyen** 554 soruda **0 yeni etiket**.

### 🔴 BU DEMETİN EN PAHALI DERSİ — frontend iki demettir DERLENMİYORDU

`G6`'da `tsc` **ilk kez** çağrıldı. Dört hata çıktı, hiçbiri o gün doğmamıştı:
`ReportCard.tsx` `TS1005` (fragment'sız kardeş JSX — `G2`) · `DiyalogDurumu.tsx` +
`Temellendirme.tsx` `TS2305` (var olmayan tip `AskItem` — `G1`/`G2`) · `TS7006` (örtük
`any`). Testler **yeşildi**, çünkü yerel kapı yalnız `pytest` koşuyor.

*Bir dilin derleyicisi koşulmuyorsa, o dilde yazılan her şey denetimsizdir.*

→ `tests/test_frontend_derlenir.py` (tip-adı denetimi + koşullu JSX tek-kök + `tsc`).
⚠ **Açık borç:** `tsc` **gecelik CI'da koşmuyor**; bugün yalnız geliştirici makinesinde.

### Ölçüm bir "fırsatı" çürüttü — `R3`

Tarama `R3`'ü en büyük red sınıfı gösterdi (**243/880**, %27,6). Açmaya niyetlendim;
`ask.py:2693` okundu: `route()` `_COMPARE_HINTS`'te **bilerek** `None` döner ve `ask()`
`strip_compare` + yeniden route + `_kiyas_cevabi` ile onu **zaten kurtarıyor**. O 243
soru LLM'e gitmiyor. Dokunulmadı.
*Bir sayının büyüklüğü, onun bir kayıp olduğunun kanıtı değildir.*

### Borç durumu — dürüst muhasebe

| borç | durum |
|---|---|
| **#17** *(«değişim» istendi, TOPLAM verildi)* | ◐ **YARIM.** *"Uyarı da yok"* yarısı **KÖK-3** ile zaten kapanmıştı (ölçüldü: `eksik=['trend']` + yol gösteren not). `G6` **iki uçlu kıyas** eksenini kapatır; bu vakanın kalanı bir **zaman ekseni** işidir ve açık kalır |
| **B-G4** | ✅ **KAPANDI** — `compare` Intent-JSON şemasına (yalnız zaman boyutlu dalda, `oneOf` korunarak) ve `parse_cube_query` beyaz listesine girdi. `5.6` (peer) bloğu kalktı |
| **B-G5** | ✅ **KAPANDI** — çelişki çözüldü: `§5` satırı **bayattı** (*"⟳ UYGULANMADI"*), `:442` güncel. `§5` → ◐ **KISMEN İNDİ**. Yasağın tam uygulaması ölçülüp geri alınmıştı (korpus %95,1→%93,5) ve **dördüncü koşulu** oradan doğdu |
| **KÇ-1** | ✅ **KAYDA GEÇTİ** *(zorunlu kayıt #3)* — ve `G6` denetimin kabul ölçütünü **karşıladı**: *"«mart cirosunu şubat ile kıyasla» tek birleşik sayı döndürmesin"* → artık gerçek kıyas dönüyor |
| **yeni** | 🔴 `tsc` gecelik CI'da koşmuyor |
| ⚠ **mount** | `test_plan_kopyasi_taze.py` ve `test_frontend_derlenir::test_TSC_TEMIZ` **konteynerde atlanıyor** — koşum reçetesi yalnız `backend/`'i mount ediyor. İkisi de geliştirici makinesinde gerçek, CI'da sessiz. Çözüm ikisinde de aynı: reçeteye repo kökünü ekle (`-v $REPO/belgeler:/belgeler:ro`) |
| ✅ **Ö5** | **KAPANDI** — `app/guard_alarmi.py` (📊 telemetri): kayan pencere (50 cevap), oran + **ham sayılar**, `/health/ready`'de görünür ama `status`'ü **etkilemez**. Payda `narration_guard`/`iddia` `Rapor`'una eklendi — bölmeyi yapan yer üretiyor, çağıran yeniden bölmüyor. ⟵ eski: **Guard düşme oranı AGREGE ölçülmüyor** (`grep dusme_orani|drop_rate` → 0). Model/prompt değişirse guard'lar **sessizce** tüm anlatıyı düşürür; kullanıcı yanlış sayı görmez ama sistem sürekli *"soğuk"* cevap verir ve **kimse fark etmez**. 🔴 Bu, `app/iddia.py`'nin **kendi docstring'inin sözü**: *"düşme oranı ölçülür — kapı agresifse gevşetilir, ama ÖLÇÜYLE."* Söz yazıldı, ölçüm kurulmadı. → kayan pencere + eşik uyarısı; eşik **ölçümle** konur *(dış öneri, kodla doğrulandı)* |
| 🔴 **Ö2** | **Çok-turlu bozulma ÖLÇÜLMÜŞ ve sahipsiz:** `lab/sharding.py` — 44 konuşmalık sabit kohort, tur 1 **%63,6** → tur 5 **%45,5** = **−%18,2** (hedef −%10). Kümülatif `cube_query` taşıma **var** (`context.py:185` ham pencereyi 2 turla sınırlar, cq ayrı yankılanır) ama derinleşmede yine bozuluyor. *Bir mekanizmanın var olması, işini yaptığının kanıtı değildir* |
| ⚠ **Ö1** | **Akış (`S` fazı) indiği gün cümle-tamponlu OLMAK ZORUNDA.** Bugün SSE metin akıtmıyor (yalnız iz adımı + sonda tek parça), yani risk yok; ama token token akıtılırsa fail-closed kapı **geri alınamaz** bir kanalın arkasında kalır. Kısıt `OPERASYON.md §10c/Ö1`'de yazılı |
| ⚠ **Ö3** | **Eksen 1 gecikme kaçış kapısı hazır ama ÖLÇÜLMEMİŞ:** `config.py:96` `openrouter_select_model` **boş**. Ölçüldü: ilk çağrı **33,7 sn**, sonrakiler ~**1,4 sn**. Eksen 1 p95 > **1,5 sn** çıkarsa o alan doldurulur — kod değil, **env** işi |
| ⊘ **Ö4** | **REDDEDİLDİ** — `garson.py` için 150+ sentetik varyasyon kümesi *aynı kuralın iki sahibi*ni doğururdu; `lab/gercek_dunya.py` o ekseni **2 312 vakayla** zaten ölçüyor (aletin kendi docstring'i bunu yazıyor). ⚠ Gerçek boşluk **çok-turlu** varyasyon: `gercek_dunya` tek turlu, `garson` 6 senaryo/16 tur. Genişletilecekse `garson.py` **içinde** — ve *"testleri yığma"* sınırı geçerli |
| 🔴 **S5** | **`MIMARI` bir mekanizmayı VAR GİBİ okutuyordu — DÜZELTİLDİ.** *"Orada `value_index` **varlık çözümü** çalışır"* yazıyordu; `G0b.6`'nın `{{ENT_i}}` varlık perdesi **inmedi** (`grep ENT_ app/` → 0). Yani hava boşluğu **cevabı** perdeliyor, **soruyu** perdelemiyor. Cümle düzeltildi ve sınır yazıldı. 🔴 Perdenin **kendisi** hâlâ borç. *Mimari otoritenin yanlış olması, kodun yanlış olmasından pahalıdır: kod kırmızı verir, belge güven verir.* |
| ⚠ **S2** | `G6`: `blend` Intent-JSON'a **girmedi** ve kaydı yoktu. `compare` girdi, `blend` girmedi; `Ö11`'in kabul ölçütü (*"verimlilik ve ciro"* → iki seri ya da netleştirme) **test edilmedi** |
| ⚠ **S4** | `G2.9`: netleştirmenin `yuksek` düzeyi **uygulanmıyor** — yalnız `kapali` uygulanıyor (`ask.py`), kodun kendi itirafı yerinde duruyor. Plan *"itiraf kapanır"* diyordu |
| ⚠ **S6** | `G1.7`: temellendirme rozetleri **tıklanabilir** olacaktı (`POST /cube`, 0 LLM); düz `<span>` kaldı |
| ⚠ **S7** | `G0.13`: `features.yml`'de `prompt_enhancer` (mimari gerekçe) ve `agent_plan_secimi` (bayat gerekçe) yorumları **düzeltilmedi** |
| ⚠ **P1** | Planın `§13.6`'sı *"beş şey"* diyor ama **altı** satır listeliyor (`Z.3` de *"beş"*). Bir sayım hatası, **kayıt #4'ün düşmesini kolaylaştırdı** — o kayıt `MIMARI`'ye hiç girmemişti |
| 🔴 **P3** | **Plan şema budamasından hiç söz etmiyor.** Ölçüldü (23 cube'luk demo): intent katalog metni **4.038 token**, Discovery şema prompt'u **16.767 token**, `oneOf` şeması **10.038 token** — ve o sonuncusu **üretilip ATILIYOR** (sağlayıcı `oneOf` desteklemiyor). Tasarım `DIKKAT-EDILECEKLER.md §4`'te dört ölçümle hazır |
| ⚠ **P4** | Plan **prompt caching**'i §7.1'de tartışıyor ama bir **faz maddesi** yapmıyor; kodda `cache_control` → **0 isabet** |
| ⚠ **P6** | Planın kabul ölçütleri **route-BAŞARISI** nüfusunda tanımlı; budama gibi *"route pes ettiğinde"* devreye giren şeyler o nüfusta **ölçülemez**. Etiketli route-başarısızlık korpusu **42'de 2 vaka** |
| ⚠ **belge** | `app/diyalog.py` — fazın en büyük yeni katmanı, `MIMARI`'de **mimari kaydı yok** |
| ✅ **DA-1** | **KAPANDI** — `ek.py` `app/yayilim.py::geri_koy`'a bağlandı (yer tutucunun sınırını bilen tek modül); ayrıca `ek_bagla(kesme=True)` özel ad kipi eklendi (TDK: özel adda yumuşama yazıya geçmez). ⟵ eski: **`app/ek.py` (G7) üretimde SIFIR çağıranı var** — yalnız kendi testi import ediyor. Commit başlığı *"enjekte edilen yuvalar doğru çekimleniyor"* diyor; hiçbir yuva çekimlenmiyor. `G7.1`'in AST kapısı da kurulmadı. **Yetim yasağının doğrudan ihlali** — üç denetim ajanının **üçü de** bağımsız buldu |
| ✅ **DA-2** | **KAPANDI** — iki senaryo eklendi (`anlati` · `sosyal_ve_donus`), *kör satır* artık **kırmızı test**, taban **üç koşum aynı** çıkınca donduruldu (`1·1·3·1·1·5·1·2·1·1`). ⟵ eski: **`lab/garson.py` 10 satırın DÖRDÜNÜ hiç ölçmüyor** (`1·çapa` · `2·anlat` · `4·sosyal` · `7·geri dönüş`): senaryoların `olculen` demetlerinde yoklar, sekiz raporun sekizinde de `0\|0\|0`. En ağırı `2·anlat` — **anlatıcının kendi satırı** ve `G5` `t2_anlatici`'yi açtıktan sonra da 0 kaldı. `G0.12`'nin *"alet körse G1 başlamaz"* kırmızı çizgisi bu yüzden fiilen sınanmadı |
| ✅ **DA-3** | **KAPANDI** — `kanit_sinifi` (+ ortaya çıkan `soz`) «saf not» kümesine alındı. Ölçüldü: netleştirme ve ret artık `raporlanabilir()=False` (saf-not dalı, *«şunlardan biri mi?»* başlığı), gerçek rapor `True` (`result`/`interpretation`/`viz`). Kapı: `test_RAPORLANABILIRLIK_BIR_TOTOLOJI_DEGIL` — varsayılanı dolu her alanı denetler. ⟵ eski: **`raporlanabilir()` bir totoloji**: `kanit_sinifi` her cevapta dolu (`schemas.py:396`, `test_ai_act_uyumu` kilitliyor) ve `SAF_NOT_ALANLARI` dışında → kapı **daima true**. Sonuç: `Z`'de eklediğim `temellendirme`/`diyalog_durumu` sınıflandırması **etkisiz**, ve netleştirme cevapları `"şunlardan biri mi?"* başlığı yerine `"sonraki adım"` başlığıyla çiziliyor |
| ✅ **DA-4** | **KAPANDI** — `rapor.makbuza()` çağrılıyor; `anlati_dogrulandi`/`anlati_dusen`/`guard_muaf` **mevcut** `hava_boslugu` bloğuna girdi (yeni panel YOK) ve muafiyetler tooltip'te **adlandırılıyor**. ⟵ eski: `narration_guard.Rapor.makbuza()` üretimde **sıfır çağıranı** var (`answer.py:529` yalnız `reddedilen`'i okuyor) — `MIMARI:1545`'in *"artık yazıyor"* iddiası karşılıksız |
| ✅ **DA-5** | **KAPANDI** — `diyalog_bellegi` bayrağı `features.yml`'e yazıldı ve `ask.py`'de **tek noktada** okunuyor: kapalıyken durum sunucuya hiç girmez → `KURAL_DEVAM` ateşlenmez. ⟵ eski: `G2`'nin **kill-switch'i yok** (`features.py`/`features.yml`'de `diyalog` → 0 isabet); GERİ AL sözleşmesi uygulanamaz |
| ⊘ **DA-6** | **BULGU YANLIŞ — incelendi ve reddedildi.** İki assert **farklı iş** yapıyor: `<= 11` gerçek kapıdır (*artamaz*), `== 11` ise **boşluksuz tavan** meta-kapısıdır ve kırmızı mesajı düşüşü *«🟢 bu bir KAZANÇ — tavanı bu değere çek»* diye karşılıyor. Desen `test_frontend_buyume::test_KAPI_SAHTE_DEGIL` ile **birebir aynı** ve bu oturumda beş kez o yolla tavan çekildi. *Bir ajan raporu ikinci el kanıttır; kodu okumadan uygulanan bir düzeltme, olmayan bir kusuru «düzelterek» gerçek bir kapıyı söker.* |
| ✅ **DA-7** | **KAPANDI** — `temellendirme.cube` rozeti **ilk sırada** çiziliyor; ebeveyn çubuğa `flex-wrap` eklendi (rozetler soru başlığını eziyordu); anahtar çakışması giderildi. ⟵ eski: `temellendirme.cube` üretiliyor + testleniyor + tipli, ama `Temellendirme.tsx` onu **render etmiyor** — `G1`'in gerekçesi `WRONG_SCOPE` %14,4'tü, kapsamı söyleyen alan düşmüş |
| ✅ **DA-8** | **KAPANDI** — `src/lib/vurgu.tsx` (kapalı kapsam: `**kalın**` · `*eğik*`, React düğümü döner → enjeksiyon yapısal olarak imkânsız) + `whitespace-pre-line`; liste önizlemesinde işaretler sökülüyor. ⟵ eski: Kullanıcıya giden metinler **markdown `**`** taşıyor (`yetenek.py:335` · `uyum.py:387`), arayüzde markdown yorumlayıcı **yok** → kullanıcı yıldızları okuyor; `ChatPanel.tsx:292` notu ayrıca `truncate` ile tek satıra kırpıyor |
| ✅ **DA-9** | **KAPANDI** — chip kipe duyarlı; `mom` aktifken *«geçen aya göre»* yazıyor ve kapatma artık `mom`'u `yoy`'a **çevirmiyor**. ⟵ eski: `InterpretationBar.tsx:521` kıyas anahtarı `=== "yoy"` sabit kodlu; `kiyas_cebiri` `mom` üretiyor ama ön yüz onu ne gösteriyor ne kaldırabiliyor |
| ✅ **DA-10** | **KAPANDI** — dönem netleştirmesi `netlestirme.donem` katalogundan okuyor, `{ne}` yuvasını `temellendirme` dolduruyor (ikinci adlandırıcı YOK). ⟵ eski: `netlestirme.donem`/`donem_sade`/`olcu` katalog girdilerinin **üretimde çağıranı yok**; `_PERIOD_TEXT` (`ask.py:585`) elle yazılmış eski metin basılıyor — netleştirmelerin %79'u dönem sorusu |
| **yeni** | ⚠ `kanit_sinifi` `ReportPanel.SAF_NOT_ALANLARI` kümesinin **dışında** ve netleştirme cevaplarında **dolu geliyor** → o cevaplar `raporlanabilir()` kapısından geçiyor. Garson fazından **önce de** böyleydi; düzeltmek ölçülmemiş bir davranış değişikliği olacağı için faz kapanışında **yapılmadı** |
| **yeni** | ⚠ `Niyet.temsil_edilemeyen` izi, `route`'un indirgeme yaptığını **bilmez** (soruya bakar, sorguya değil): kıyas kurulmuş bir cevapta iz hâlâ `temsil-yok=cok_donem` yazar. Zararsız — `uyum` cq'yu görüp doğru susuyor — ama **iz yanıltıcı** |
