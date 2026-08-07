# DİMA · GARSON — ARA FAZ YOL HARİTASI

> **Konum:** v1 (mutfak) **bitti** ⟶ **[BU BELGE]** ⟶ Bölüm II / v2 (analist + karar ortağı)
> **Tarih:** 2026-08-07 · **Taban tur:** `294eb67` · **Ölçüm tabanı:** korpus **%95,1** ·
> gerçek-dünya {kabul **1150** · doğru **83** · sessiz_yanlış **12** · beyanlı_kısmi **58**} ·
> süit **3869 yeşil** · `eval` **+0,0 / +0,0 / +0,0**
>
> 🔴 **Sağlayıcı kararı:** garsonun LLM'i **OpenRouter + NVIDIA açık kaynak model** —
> mimari sonuçları **§7.4**'te, ve bir garantiyi iptal ediyor.
> ✅ **Kanıt durumu:** belgedeki `dosya:satır` iddiaları **koda karşı doğrulandı**
> (2026-08-07); dört bayat atıf bulunup düzeltildi — kayıt **§13.8**'de.
>
> **Kardeş belgeler:** `~/.claude/plans/DIMA-V1-YOL-HARITASI.md` (5279 satır, §G) ·
> `backend/MIMARI.md` (mimari otorite) · `OPERASYON.md` / `OPERASYON-DURUM.md` ·
> `dima v2 v3 için mimari karar (1).md` (danışman girdisi — **denetlenmiş hâli §9'da**)

---

## §0 · BU BELGE NEDİR

Bir **ara fazdır**. v1'in mutfağı kuruldu: sayı doğru, mühürlü, RLS'li, kanıtlı. Eksik olan
**garson** — müşteriyi karşılayan, siparişi kendi diliyle alan, menüyü bilen, emin olmadığında
soran, siparişi tekrarlayan, tabağı getirip ne olduğunu anlatan katman.

Bu belge **§G'nin yerine geçmez**; §G'yi *ölçülmüş gerçeklikle* yeniden sıralar. Yol haritası
**2026-08-04'te donmuş**; depoda 08-05→08-07 arası ~30 commit var ve üç yerde belge ile kod
ayrışıyor (§4.4).

**Yöntem.** On bir ajan koştu. Yedisi dış araştırma (semantik katman kanıtı · Türkçe yüzey
üretimi · ürünler nasıl yaptı · maliyet/gecikme · belgelenmiş başarısızlıklar · diyalog
yönetimi · sayı uydurmasını önleme), biri kod envanteri, biri yol haritası haritası, biri
danışman belgesinin çıkarımı. On birincisi bir koordinatördü; yedi akışı bekleme döngüsünde
asılı kaldı ve **hiçbir şey üretmedi** — sentezi bu belge yapıyor. Her sayı kaynaklıdır;
kaynaksız olan **kaynaksız diye işaretlidir**.

🔴 **Ve bir dördüncü kaynak, sonradan katıldı ve iki yargıyı düzeltti:**
`belgeler/denetim/2026-08-05_ANLAMA-KATMANI.md` (1311 satır) — bu fazın **kendi deposundaki
teşhisidir**, dışarıdan değil. Dokuz bulgu (B1…B9), yedi kök neden (KN-1…KN-7), on iki
belirti maddesi (Ö1…Ö12) ve **sekiz kök çözüm** (KÇ-0…KÇ-7) taşıyor. §4.4 ve §6/G1·G6 onun
sonucunda düzeltildi.

---

## §1 · KARAR — GARSON LLM'DİR VE BİR SEÇENEK DEĞİLDİR

### 1.1 · Kararın kendisi

> **Sistem makine kadar kesin, insan kadar insan olmak zorundadır.**
> Bu bir *"olsa iyi olur"* özelliği değildir. Kapatma ihtimali yoktur.

Bundan **üç şey** çıkar ve üçü de bağlayıcıdır:

**(a) LLM artık bir YEDEK değil, dilin ÖN KAPISIDIR.**
Bugünkü merdiven şudur: `route()` başaramazsa → Intent-JSON → Discovery. Yani LLM **pes
edilince** çağrılan şeydir. Garson mimarisinde bu ters döner: **dil işini LLM yapar, sayı
işini küp yapar**, ve `route()` bir *kapı bekçisi* değil bir **hızlı yoldur**.

**(b) `doğru-cube %` bir kalite ölçüsü değil, bir MALİYET ölçüsüdür.**
Korpusun ölçtüğü şey tam olarak şudur: *"mutfak, garsona hiç uğramadan kaç soruyu
cevapladı?"* Garsonun zorunlu olduğu bir sistemde bu sayı **ne kadar ucuza çalıştığımızı**
söyler, **ne kadar iyi olduğumuzu** değil. Maliyet ölçüsü ürünü veto edemez.

**(c) Ayrım katmandadır, taviz değildir.**
Yol haritasının kendi cümlesi (§G.0d, `YH:894`): *"**TAVİZ GEREKTİRMİYOR — çünkü farklı
katmanlarda duruyorlar.**"* Ve MIMARI §11.6d: *"**SEÇİM ≠ ÇALIŞTIRMA.** Seçicinin yanılması
yeni bir risk açmaz."*

### 1.1b · 🔴 Kök neden — ve bunu depo kendisi yazmış

Kullanıcının restoran metaforu bir benzetme değil, **ölçülmüş bir teşhisin birebir aynısı**.
`belgeler/denetim/2026-08-05_ANLAMA-KATMANI.md`, bu sohbetten bağımsız olarak, aynı cümleyi
kuruyor:

> *"Ürünün tezi (**«LLM garson, küp aşçı»**) doğru — ama bugün **garson yok, siparişi aşçı
> alıyor.**"*

Ve tek satırlık mimari kök neden (aynı belge, §14.4):

> 🔴 ***`route()` bir EŞLEŞTİRİCİDİR, ama ona ÇÖZÜMLEYİCİ işi yaptırılıyor.***
> *Yedi kök neden, tek bir mimari kararın yedi belirtisidir.*

**Bu fazın tanımı budur:** çözümleme işini eşleştiriciden almak ve **ona ait olan katmana**
— garsona — vermek. `route()` kötü bir eşleştirici değil; **yanlış işi yapan iyi bir
eşleştiricidir.**

Denetimin ölçtüğü fatura, aynı cümlenin sayısal hâli:

| Bulgu | Ölçüm |
|---|---|
| Gerçek-dünya korpusunda deterministik yolun ürettiği cevap | **41 vakanın 0'ı** |
| 🔴 Cube **ve** ölçü **bulunmuşken** atılan cevap | **11/42** |
| Tanınan terim + gündelik fiil → ölüm | **77/112 (%68,8)**, ölüm kodu **%100 R10** |
| Ay adı çekim ekiyle | **60/60 düştü** (`mart`✓ · `martta`✗) |

⚠ Ve denetimin kendi uyarısı, bu belgenin §2'siyle aynı yere çıkıyor: iki bayrağın kapalı
tutulma gerekçesi **"kendi nüfusunu göremeyen bir aletle" üretilmiş**.

### 1.1c · 🔴 KESİNLİK EŞİĞİ SORUSU — *"%95 üstü deterministik, altı LLM"* — KARAR

> Danışman belgesindeki kademeli şelale: **Kademe 1 (≥%95)** refleks/deterministik ·
> **Kademe 2 (%80–95)** SLM Intent-JSON · **Kademe 3 (<%80)** netleştirme.
> **Bu belgede cevabı yoktu — burada veriliyor.**

#### Karar: **yazıldığı biçimde REDDEDİLDİ.** Sebep bir tercih değil, bir imkânsızlık.

Eşik koymak için **bir sayı** gerekir. Kodda öyle bir sayı **yok** — ve olan şey bir güven
değil, bir **etiket**:

```python
# app/answer.py:84 — _EXPLAIN_PATH  (SÖZLÜK, hesap DEĞİL)
"cube":       ("route() — LLM'siz, sıfır maliyet",       1.0)
"vqr":        ("önceden doğrulanmış sorgu",              0.95)
"cube+llm":   ("cube + LLM-destekli alan seçimi",        0.85)
"rule":       ("kural-tabanlı yedek",                    None)
```

`confidence`, sorunun ne kadar iyi anlaşıldığını **ölçmüyor**; hangi yoldan geçildiğini
**söylüyor**. `1.0` *"%100 eminim"* değil, *"bu cevap `route()`'tan çıktı"* demek. Aynı `1.0`
hem doğru hem yanlış bir cube seçiminde döner.

Ve MIMARI bunu zaten karara bağlamış (`MIMARI.md:1390-1394`):
> *"…kalibre edilmediği sürece o sayı bir güven değil bir **SÜStür**."* … *"Bunu bir yüzde
> gibi sunmak, tam da yasaklanan süs olurdu — üstelik kullanıcı onu **kalibre edilmiş**
> sanacağı için **daha zararlı** bir süs."*

→ **Bir eşik uydurmak, olmayan bir ölçüme karar verdirmek olurdu.** Danışman belgesinin
kendi *"Yalancı Doğru"* bölümü de bunu itiraf ediyor: *"yerel NLP kendine **%95 üzeri sahte
güven** verirse…"* — yani belge, eşiğini kuracağı sayının **güvenilmez** olduğunu aynı
belgede yazıyor (§9/Ç-6).

#### Yerine geçen: **İLİŞKİSEL sinyaller** — mutlak olasılık gerektirmez

Danışman belgesinin **kendi doğru cevabı** yine kendi içinde: *"Çakışma ve Marjin Kontrolü"*
(Y-1). İki sinyal, ikisi de *"ne kadar eminim"* değil **"alternatiflere göre ne kadar
ayrıştım"** sorusunu sorar — ve bu, kalibrasyon **gerektirmez**:

| Sinyal | Ne sorar | Durum |
|---|---|---|
| **Eşsizlik** | Bu terim **kaç** ölçüye dokunuyor? | ✅ **VAR** — `cube_router.py:1864 measure_cube_candidates` · `metrik_kaydi` · `belirsizlik_chipi` |
| **Marjin** | 1. ve 2. aday arasındaki fark **dar mı**? | ✅ **VAR** *(üç yerde)* — `cube_router:947` **4-harf** cube marjini · `:908-937` ölçü/boyut kanıtı · `value_index:28` `AUTO_MARGIN=0.08`. ⚠ İlk sürüm *"yok"* demişti: **Türkçe arandı, kod İngilizce yazmış** (§13.8) |

**Yönlendirme kararı bir yüzdeye değil, üç sorunun cevabına bağlanır — ama dikkat: bu ağaç
YALNIZ «hangi sorgu koşacak» sorusunu yanıtlar (Eksen 1, §1.1e):**

#### 🔴 ÖNCE GÜVEN MODELİ — belgenin tek en önemli cümlesi

> **Kullanıcının formülü:** *"Garson olarak LLM'e **güveniyoruz kesinlikle**, ama mutfakta
> **hiç güvenmiyoruz**."*

| İş | LLM'e güven | Gerekçe |
|---|---|---|
| **GARSON İŞİ** — anlamak · sormak · hatırlamak · anlatmak | 🟢 **TAM** | Dilde LLM `route()`'tan **açık ara** iyidir. Ölçüldü: 41 gerçek cümlenin **0'ında** `route()` cevap üretiyor; doğal ifadelerin **13-14/15'ini** Intent-JSON çözüyor |
| **MUTFAK İŞİ** — sayı · hesap · SQL · yetki | 🔴 **SIFIR** | Sayı yalnız küpten. `parse_cube_query` · `dry_plan` · RLS · sözleşme mührü — hiçbiri LLM'e sormaz |

**İki kapı tam bu sınırda durur:** `narration_guard` ve `iddia.py`, garsonun konuşurken
**mutfağın alanına girmesini** engeller. *Garsona sonuna kadar güveniyoruz; tencereye
karışmasına izin yok.*

🔴 **Ve güvenin İKİNCİ ekseni var: LLM neyi YAPABİLİR ≠ LLM neyi GÖREBİLİR.**

| | LLM ne **YAPAR** | LLM ne **GÖRÜR** |
|---|---|---|
| **Garson işi** | 🟢 tam güven — anlar · sorar · anlatır | ⚠ **sınırlı** — soru + katalog **adları** + `{{yer tutucu}}`lar |
| **Mutfak işi** | 🔴 sıfır — sayıyı asla o koymaz | 🔴 **hiç** — ham satır · gerçek değer · gerçek sayı **çıkmaz** |

*Bir garsona menüyü ezberletirsiniz; kasayı ve müşteri dosyalarını göstermezsiniz.*
Bu ikinci eksenin kapısı **`G0b` · hava boşluğudur** — ve bugün **yoktur**
(`grep mask_text app/llm.py` → 0 isabet).

#### `route()` neden yalnız *"%95 üstünde"* — doğru gerekçe

⚠ **Yanlış okuma** *(ve bu belgenin ilk sürümünün düştüğü hata)*: *"LLM'e güvenilmediği
için, ancak çok eminken LLM'siz gidiyoruz."*

🔴 **Gerçek bunun tersi:** LLM'siz intent algılamak **zordur** — güven duyulmayan
`route()`'tur. Her şey LLM'e gitse **daha net** olurdu. `route()` yalnız **maliyet ve hız**
için, ve **yalnız kendini ispat edebildiği yerde** kullanılıyor — *güvenden ödün vermeden*.

→ **İspat yükü `route()`'un üzerindedir, LLM'in değil. Şüphede LLM'e düşülür.**

```
EKSEN 1 · Sipariş fişini kim yazacak?          [güven sırasına göre]

  ① Katalog GERÇEKTEN belirsiz mi?
     (aynı terim ≥2 ölçüye MEŞRU şekilde düşüyor — ör. «bakiye»)
        ├─ EVET ─────────────────────────────► SOR  (chip · 0 token)
        │     ↑ Anlama kusuru DEĞİL — dünyanın kendisi belirsiz.
        │       LLM de çözemez; tahmin etmesi ZARARLI olur.
        └─ HAYIR ↓

  ② route() bu cümlede KENDİNİ İSPAT EDEBİLİYOR MU?
     (tek eşleşme · geniş marjin · çözülemeyen terim yok)
        ├─ EVET ─────────────────────────────► route()  · 0 token · hızlı
        │     ↑ KANITLANMIŞ güvenli kısayol — güvenden ödün YOK
        └─ HAYIR ────────────────────────────► LLM (Intent-JSON)
              ↑ 🔴 VARSAYILAN BUDUR. Şüphede LLM.

EKSEN 2 · Konuşmayı kim yürütecek?
  🔴 HER ZAMAN GARSON. Yukarıdaki dalın hangisi olduğuna BAKILMAZ.
     temellendir (G1) → gerekirse sor (G1.4c) → hatırla (G2) → anlat (G5) → menü (G8)
```

⚠ **Ağacın SIRASI bu düzeltmeyle değişti ve fark önemli:** eskiden *"≥2 sahip → SOR"* en
başta, `route()` ise **varsayılan** daldı. Şimdi:
**(a)** yalnız **gerçek katalog belirsizliği** kullanıcıya sorulur; `route()`'un zayıflığı
**LLM'e** devredilir, kullanıcıya değil — *sistemin kendi eksikliği için kullanıcıyı
sorgulamak, tam da şikâyet edilen "form doldurtma" davranışıydı (`KN-2`)*;
**(b)** `route()` artık **varsayılan değil, ispatlı istisnadır**.

🔴 **`route()` dalı bir «LLM'siz TUR» değildir — bir «LLM'siz SORGU»dur.** O turda da
temellendirme basılır, gerekirse soru sorulur, cevap anlatılır. *Küp yemeği pişirdi diye
garson masaya gelmemezlik etmez.*

Üçü de **deterministik**, üçü de **açıklanabilir**, hiçbiri kalibrasyon istemez. Ve MIMARI'nin
kendi cümlesiyle (`:2701`): *"kalibre edilmemiş bir float aynı kararı verip **gerekçesini
gizlerdi**."*

#### 🔴 Ve bir çelişki: danışman belgesi kendi kısıtını UNUTMUŞ

Kaynak sohbette **iki farklı yerde iki farklı mimari** var, ve ikincisi birincinin kısıtını
çiğniyor:

| Nerede | Ne diyor |
|---|---|
| **Satır 1** *(kullanıcının açılış cümlesi — kısıtı koyan)* | *"**maliyet hesabını tamamen unut halledicez onu**"* … *"insani taraf opsiyonel değil **birinci seçenek** ve zorunlu, **fallback sadece küpler sadece sistem**"* |
| **Satır 755-761** *(danışmanın cevabı)* | *"LLM'i birinci seçenek yapmak … **finansal hem operasyonel olarak bir intihardır**"* → *"Deterministik birincil, LLM ikincil"* |

Danışmanın üç *"LLM-first çöküş noktası"*ndan:

| # | Argüman | Yargı |
|---|---|---|
| 1 | **Maliyet (COGS)** — *"2+2 için jet motoru"* | ❌ **GEÇERSİZ** — kullanıcı satır 1'de maliyeti **açıkça feragat etti** |
| 2 | **Gecikme** | ⚠ **Endişe gerçek, RAKAMLARI değil.** Feragat edilmedi — ama belgenin verdiği *"10-30 ms ↔ 800 ms-2 sn"* **kaynaksız** ve kendi içinde tutarsız (§9.3/Ç-5: aynı belge Kademe 2'ye *"~500 ms"* diyor, kendi alt sınırının altında). §7.2 bu yüzden **rakam değil bütçe** koyuyor |
| 3 | **Basit soruda aşırı düşünme** | ⚠ **Spekülatif** — hiçbir yerde ölçülmemiş |

**Ve daha derin kusur:** danışmanın cevabı, LLM ile `route()`'un **aynı işi** yaptığını
varsayıyor. §1.1e gösterdi ki yapmıyorlar — biri **sorgu kurar**, öteki **konuşma yürütür**.
🔴 *Bu, Eksen 1'in cevabının Eksen 2'nin sorusuna verilmesidir.*

**Sonuç — kullanıcının iki cümlesi de doğru, farklı eksenlerde:**
- *"İnsani taraf birinci seçenek, fallback sadece küpler"* → ✅ **Eksen 2'de aynen geçerli.**
  Konuşma katmanı her turda çalışır; **çıplak deterministik çıktı, bozulma hâlidir** (LLM
  erişilemezse) — normal hâl değil.
- *"%95 üstü deterministik, altı LLM"* → **Eksen 1'in sorusu**, ve orada başka bir sebeple
  düşüyor: **kalibre skor yok**. Yerine eşsizlik + marjin.

#### Ve şelalenin hangi yarısı SAĞ KALDI

⚠ Sizin sezginizin doğru yarısı korunuyor, ama **anlamı değişiyor**:

| Danışman belgesi | Bu belge |
|---|---|
| Şelale bir **GÜVEN hiyerarşisidir** — LLM'e güvenilmez, en sona konur | Şelale bir **MALİYET yoludur** — `route()` temiz çözdüyse anlamak için LLM'e **gerek yok** |
| LLM = pahalı **son çare** | LLM = dilin **ön kapısı** *(§1.1/(a))* — anlatım için **yine de** çağrılır |
| Eşik: **%95 / %80** | Eşik yok: **eşsizlik + marjin + çözülemeyen terim** |

🔴 **Yani soru *"LLM'i ne zaman çağıralım"* değil, *"küp mü karar versin garson mı"*dır** —
ve iki katman farklı şeylere karar verdiği için (sayı ↔ dil) yarışmıyorlar.

🔴 **Bu fazda YAPILACAK İŞ YOK — ikisi de kurulu.** Bu bölüm bir **tasarım emri** değil,
zaten uygulanmış bir davranışın **adlandırılmasıdır**. Katkısı: `%95` eşiği sorusuna
*"o eşik zaten yok ve olmasına gerek de yok"* cevabını **kanıtla** vermek.

### 1.1d · `prompt_enhancer` — **mimari olarak gereksiz**, ölçümle değil

> **Karar (kullanıcı):** *"LLM'e gitmişken direkt gitsin; neden deterministik için gitsin?
> Manyaklık bu. O yüzden tamamen devre dışı bıraktık."*

**Bu gerekçe, ölçüm gerekçesinden daha güçlüdür ve kararı tartışmadan çıkarır.**

Enhancer'ın yaptığı: `route()` boş dönünce **LLM-1**'i çağırıp soruyu katalog diliyle
yeniden yazmak, sonra **deterministik `route()`'a geri dönmek**; o da başarısız olursa
**LLM-2** (Intent-JSON). Yani **bir turda iki LLM çağrısı**, ve ikincisi zaten birincinin
çözemediğini çözecek olan.

🔴 **Garson mimarisinde bu yapı bir tuzak değil, bir ÇELİŞKİDİR:** §1.1/(a) *"LLM dilin ön
kapısıdır"* diyor. Enhancer ise LLM'i **eşleştiricinin yardımcısı** yapıyor — dili anlayan
katmanı çağırıp, anladığını **anlamayan** katmana geri veriyor. *Garsonu çağırıp siparişi
yine aşçıya bağırtmak.*

| | Enhancer yolu | Doğrudan yol |
|---|---|---|
| LLM çağrısı | **2** | **1** |
| Gecikme | iki tur bekleme | tek tur |
| Kim karar veriyor | `route()` *(eşleştirici)* | Intent-JSON *(çözümleyici)* |
| Mimari | LLM = yardımcı | LLM = **ön kapı** |

**Sonuç:** `prompt_enhancer` **kalıcı olarak `off`**. Ve gerekçesi artık *"ölçtük, kazanç
yok"* **değil** — çünkü o ölçüm tartışmalıydı (§9.4: ikinci sağlayıcıda 14/15→15/15, yani
**lehine** çıkmıştı ve MİMARİ *"karar yeniden açılabilir"* diyordu). Yeni gerekçe ölçüme
bağlı değil: **yapı yanlış.** Kazansa bile yanlış yerde kazanırdı.

⚠ **Ve bu, §9.4'teki eleştirimi geçersiz kılmaz, KAPSAMINI daraltır:** danışman belgesinin
*"resmen kilitlendi"* diye seçici alıntı yapması hâlâ bir kusurdur; ama **kararın kendisi**
artık ölçüme değil mimariye dayandığı için doğrudur. *Doğru karar, yanlış gerekçeyle
savunulmuştu.*

📌 **Kayıt borcu:** `features.yml:89`'un yorumu bugün ölçüm gerekçesini yazıyor →
**mimari gerekçeyle değiştirilir** (`G0` commit'inde, §13.6).

### 1.1e · 🔴 *"`cube+llm` zaten garsonun yarısı değil mi?"* — **HAYIR.** İki ayrı eksen

> **Soru (kullanıcı):** *"Sistemde LLM zaten intent algılamada vardı; `discovery` ve
> `cube+llm` dediğimiz şey işleyişle alakalı değil mi? Garson olarak yapmak istediğimiz
> daha başka."*
>
> **Cevap: evet, tam olarak öyle.** Ve bu ayrım bu fazın **temel mantığıdır**.

Bugün LLM üç yerde çağrılıyor — ve **üçü de aynı sorunun cevabı**: *"hangi sorguyu
koşturayım?"*

| Bugünkü LLM kullanımı | Ne üretiyor | **Kim tüketiyor** |
|---|---|---|
| `llm.select_cube` *(`cube+llm`)* | **JSON** → `CubeQuery` | **makine** — `parse_cube_query` |
| `llm.refine_cube` | **JSON** → daraltılmış `CubeQuery` | **makine** |
| `generate_sql` *(Discovery)* | **SQL** | **makine** — `dry_plan` → motor |

🔴 **Üçünün de çıktısı makineye gidiyor. Bugün LLM'in ürettiği HİÇBİR KELİME kullanıcıya
ULAŞMIYOR.** Kod bunu kendi alanında itiraf ediyor:

```python
# app/answer.py:955
resp.ai_generated_prose = bool((resp.interpretation or {}).get("narration"))
# ve :421-426 — t2_anlatici KAPALI olduğu için `narration` HİÇ dolmuyor
#              → ai_generated_prose bugün DAİMA False
```

Kullanıcının okuduğu her cümle **deterministik**: `interpret.summary` (nokta ile
birleştirilmiş olgular) · `soz.py` katalogu (13 kayıt) · `uyum.kismi_cevap_notu`.

#### İki eksen, birbirine karışmasın

```
EKSEN 1 · SİPARİŞ FİŞİ (çeviri)  — "cümle hangi sorguya çevrilecek?"  [BUGÜN VAR]
   route()  →  Intent-JSON (cube+llm)  →  Discovery
   ↑ üçü de aynı işin ÜÇ KAPISI: mutfağa sipariş fişi yazmak

EKSEN 2 · KONUŞMA KATMANI   — "insan ne dedi, ona ne diyeceğiz?"  [BUGÜN YOK]
   anla → temellendir → sor → hatırla → onar → anlat → menüyü söyle
   ↑ hiçbiri bir sorgu üretmez; sorgunun ETRAFINI yönetir
```

**`cube+llm` Eksen 1'dedir.** Orada LLM bir **form dolduruyor** — yol haritasının kendi
cümlesiyle (`YH:1103-1106`): *"Bugün LLM'in rolü üç şeyle sınırlı… **Üçünde de LLM
konuşmuyor, FORM DOLDURUYOR.**"* Ve denetim belgesinin cümlesiyle: *"garson yok, siparişi
aşçı alıyor."*

#### 🔴 Ve kritik bir sınır düzeltmesi: `route()` MUTFAK DEĞİL, GARSONUN KULAĞIDIR

> **Soru (kullanıcı):** *"%95 dediğimiz şu andaki deterministik dil anlama sistemimiz —
> o sadece garsonla alakalı, mutfaktan bağımsız, intenti algılamaktan ibaret değil mi?"*
> **Cevap: evet. Ve bu, belgenin bir etiketini düzeltti** *(eskiden buraya "icraat
> merdiveni" yazıyordu — yanlıştı)*.

Kodda doğrulandı:

```python
# app/cube_router.py — route()
def route(question: str, schema: dict, ...) -> dict | None
#        ^^^^^^^^ metin      ^^^^^^ katalog        ^^^^ CubeQuery
# Gövdesinde dry_plan · execute · wren · sql · SELECT geçişi: SIFIR
```

`route()` **hiçbir şey çalıştırmaz.** Metin + katalog alır, yapısal bir sipariş fişi
üretir. Bu **dil işidir** — mutfak işi değil.

**Mutfağın gerçek sınırı `parse_cube_query`'dir** (`cube_router.py:3715`): sipariş fişi
oradan içeri girer ve katı beyaz listeden geçer. Öncesi garson, sonrası aşçı.

```
   ┌──────────── GARSON ────────────┐ ┌──────── AŞÇI ────────┐
   │  route()      · deterministik  │ │  parse_cube_query    │
   │  Intent-JSON  · LLM            │ │  compose · dry_plan  │
   │  Discovery    · LLM            │ │  wren-core · RLS     │
   │  ⌐ hiçbiri bir şey ÇALIŞTIRMAZ │ │  ⌐ hiçbiri DİL bilmez│
   └────────────────────────────────┘ └──────────────────────┘
                        ▲
                 CubeQuery burada el değiştirir
```

**Bunun üç sonucu var ve üçü de belgenin okunuşunu değiştirir:**

1. 🔴 **`%95` sorusu tamamen GARSONUN İÇİNDEDİR.** *"Deterministik mi LLM mi"* tartışması
   *"garson mı mutfak mı"* değil — **garsonun iki kulağından hangisine güveneceğimizdir**:
   kural kulağı (`route()`) mı, dil kulağı (Intent-JSON) mı. Bu yüzden §1.1c'nin cevabı
   (eşsizlik + marjin) doğru yerde duruyor: o sinyaller **kural kulağının ne kadar iyi
   duyduğunu** ölçer ve duymadığında **dil kulağına** devreder.

2. **Garsonun bugün var olan tek yarısı sipariş fişidir.** Yani garson *"hiç yok"* değil —
   **yarısı var ama kekeme, yarısı hiç yok**:

   | Garsonun işi | Bugün |
   |---|---|
   | **Sipariş fişi yazmak** *(Eksen 1)* | ◐ **var, ama mekanik** — 41 gerçek cümlenin 0'ında `route()` cevap üretiyor |
   | **Müşteriyle konuşmak** *(Eksen 2)* | 🔴 **hiç yok** — LLM'in tek kelimesi kullanıcıya ulaşmıyor |

3. **`route()`'u iyileştirmek MUTFAĞI iyileştirmek DEĞİLDİR** — garsonun kural kulağını
   iyileştirmektir. Bu yüzden §11'in *"mutfak paralel gelişir"* kuralı `route()`'u
   **kapsamaz**: `route()` bu fazın konusudur (`G3` · `G6`), mutfağın değil.

⚠ **Ve bu, korpusun ne ölçtüğünü de netleştirir:** `nl_corpus` mutfağı değil,
**garsonun kural kulağını** ölçüyor. §2'nin *"korpus bir maliyet ölçüsüdür"* tespiti bu
yüzden doğru — ölçtüğü şey *"garson LLM'e sormadan kaç siparişi doğru yazdı"*dır.

⚠ **Bu yüzden `cube+llm`'in var olması, garsonun *"yarısı hazır"* anlamına GELMEZ.** Bir
restoranda aşçının siparişi telefondan kendi yazması, garson işinin yarısının yapıldığı
anlamına gelmez — **sipariş alınmıştır, ama kimse müşteriyle konuşmamıştır.**

#### Sayısal karşılığı

| | Eksen 1 *(sipariş fişi)* | Eksen 2 *(konuşma)* |
|---|---|---|
| Bugün var mı | ✅ üç kapı da çalışıyor | 🔴 **hiçbiri yok** |
| Kullanıcıya ulaşan LLM kelimesi | **0** | — |
| Bu fazın işi | `G3` *(merdiven)* · `G6` *(dil genişliği)* | **`G1`·`G2`·`G4`·`G5`·`G8` — beşi de yeni** |

🔴 **Ve bu, `G0`'ın neden bloklayıcı olduğunu da açıklıyor:** korpus ve `eval` **Eksen 1'i**
ölçüyor. Eksen 2'nin **hiç ölçüsü yok** — sekiz koşumda `⊘` veren satırın sebebi bu.

### 1.2 · Dört katman — kim neyi yapar, kim neyi yapamaz

```
K3 · GARSON (LLM)   anlar · sorar · anlatır          kapı: app/iddia.py + narration_guard
K2 · DİYALOG (det.) slot · devam · onarım ·          kapı: deterministik testler
                    temellendirme · inisiyatif
K1 · KÜP            SAYIYI KOYAR                     kapı: parse→dry_plan→contract→guard
K0 · DÖRT KAPI      kayıt · yetki · det-önce · bütçe  kapı: planner.py
```

🔴 **K1 ve K0 bu fazda DEĞİŞMEZ.** Tek bir satırı gevşemez. Garson K3 ve K2'de yaşar.

### 1.2b · 🔴 TAM MİMARİ — bu faz bittiğinde bir turun tam yolculuğu

> **Bu, hedefin resmidir.** Her kutunun altında ya `[VAR]` *(bugün çalışıyor)* ya bir
> `[G#]` *(bu fazda inecek)* etiketi var. Etiketsiz kutu yoktur.

```
┌─ KULLANICI ───────────────────────────────────────────────────────────────────┐
│  serbest Türkçe · dağınık · eksik · yazım hatalı · takip cümlesi              │
└──────────────────────────────────┬────────────────────────────────────────────┘
                                   ▼
╔══ K2 · DİYALOG BELLEĞİ ══════════ deterministik · 0 token ════════════════════╗
║   context.coz() · followup.sinifla() · diyalog.acik_slotlar()                 ║
║                                                                               ║
║   ├─ SOSYAL mi?          → 0 LLM · 0 SQL · tur biter               [VAR]      ║
║   ├─ TAKİP mi?           → önceki CubeQuery'ye ÇAPALA               [VAR]      ║
║   ├─ ONARIM mı?          → TEK slotu düzelt, baştan başlama         [G2.8]     ║
║   └─ AÇIK SLOT var mı?   → cevabı slota yaz, turu SÜRDÜR            [G2.7]     ║
╚══════════════════════════════════┬════════════════════════════════════════════╝
                                   ▼
╔══ K3a · ANLAMA ══════════════════ EKSEN 1: "hangi sorgu koşacak?" ════════════╗
║   niyet.coz_soru(q)   çözümleme — şemasız, salt dilbilgisi          [VAR]     ║
║   niyet.coz(q, şema)  eşleştirme — katalog                          [VAR]     ║
║        │                                                                      ║
║        ├─ eşsizlik: terim ≥2 ölçüye mi düşüyor? ──── EVET ──► ❸ SOR  [VAR]    ║
║        ├─ marjin: 1. ve 2. aday dar mı? ──────────── EVET ──► ❸ SOR  [G1.4b]  ║
║        ├─ çözülemeyen terim kaldı mı? ───────────── EVET ──► LLM      [VAR]    ║
║        │                                            Intent-JSON               ║
║        └─ hepsi temiz ────────────────────────────────────► route()  [VAR]    ║
║                                                             0 token           ║
║   ⚠ HANGİ DAL OLURSA OLSUN ÇIKTI TEK TİPTİR — aşağısı dalı bilmez.           ║
╚══════════════════════════════════┬════════════════════════════════════════════╝
                                   │  CubeQuery
                                   │  {cube · measures · dimensions · filters
                                   │   timeDimensions · referans[G6] }
                                   ▼
╔══ K1 · MUTFAK ═══════════════ 🔴 DOKUNULMAZ · %100 deterministik ═════════════╗
║   parse_cube_query()  KATI BEYAZ LİSTE — şema dışı ad ÇALIŞTIRILAMAZ  [VAR]   ║
║   compose()           kaynak→modül→sektör→kesişim→şirket               [VAR]   ║
║   dry_plan()          motor doğrulaması — çalıştırmadan ÖNCE           [VAR]   ║
║   wren-core           SQL üretimi + lehçe çevirisi                     [VAR]   ║
║   RLS / always_filter tenant + satır seviyesi · fail-closed            [VAR]   ║
║   QueryContract       SHA-256 mühür + MDL sürümü                       [VAR]   ║
║   stats + interpret   trend · anomali · pay · segment · eşik           [VAR]   ║
╚══════════════════════════════════┬════════════════════════════════════════════╝
                                   │  FACT-SHEET  (~150-250 token)
                                   ▼
   ╔═══════════════════════════════════════════════════════════════════════════╗
   ║  🔴 HAVA BOŞLUĞU · app/llm_guard.py::safe_call — TEK ÇIKIŞ GEÇİDİ         ║
   ║     PII kalıpları [VAR] · korunan yayılım [G0b]                           ║
   ║                                                                           ║
   ║   ham satır ─────────────────────────► ⛔ ASLA ÇIKMAZ                     ║
   ║   gerçek sayı      12.430 ───────────► {{NUM_1}}                          ║
   ║   boyut değeri     "RAM 3" ──────────► {{DIM_1}}                          ║
   ║   varlık adı       "Ahmet Tekstil" ──► {{ENT_1}}   (value_index yerelde)  ║
   ║   TCKN·e-posta·telefon·IBAN ─────────► pii.py maskesi                     ║
   ║   çıkış kütüğü: tür + SAYI · değer YAZILMAZ                               ║
   ╚═══════════════════════════════════════════════════════════════════════════╝
                                   │  yalnız yer tutuculu yük
                                   │  🔴 binadan çıkan tek şey budur
                                   ▼
╔══ K3b · SERVİS ══════════════════ EKSEN 2: "insana ne diyeceğiz?" ════════════╗
║   ❹ TEMELLENDİR  "anladığım şu: Mart 2026 · Satış Cirosu · Merkez"   [G1]     ║
║   ❺ ANLAT        Fact-Sheet → akıcı Türkçe paragraf                  [G5]     ║
║   ❻ EK MOTORU    enjekte edilen yuvalar doğru çekimlenir             [G7]     ║
║   ❼ MENÜ         yapamadıysa NE YAPABİLDİĞİNİ söyler                 [G8]     ║
╚══════════════════════════════════┬════════════════════════════════════════════╝
                                   ▼
          ╔══ ÜÇ KAPI · fail-closed · çıkıştan ÖNCE ════════════════════════╗
          ║   ① GERİ KOYMA   {{NUM_1}} → 12.430 · harita renderer'da  [G0b] ║
          ║      ⌐ eksik/fazla yer tutucu → cümle DÜŞER (yapısal)           ║
          ║   ② narration_guard  her SAYI ±%2 → cümle DÜŞER           [VAR] ║
          ║   ③ iddia.py         her İDDİA şemaya karşı               [G4]  ║
          ╚══════════════════════════┬══════════════════════════════════════╝
                                     ▼
┌─ KULLANICI ───────────────────────────────────────────────────────────────────┐
│  rozet · TEMELLENDİRME · tablo/grafik · ANLATI · chip'ler · MAKBUZ            │
└───────────────────────────────────────────────────────────────────────────────┘

   ╭─ K0 · DÖRT KAPI ── her araç çağrısının altında ────────────────────╮
   │  kayıt (tools.KAYIT) · yetki (authorize) · det-önce · bütçe [VAR]  │
   ╰────────────────────────────────────────────────────────────────────╯
```

#### Sınırlarda ne garanti ediliyor — ve neyle

| Sınır | Garanti | Mekanizma | Bu fazda |
|---|---|---|---|
| K2 → K3a | Takip turu **yeni SQL yazmaz** | `context.coz` çapası | `G2` sürdürür |
| K3a → K1 | 🔴 **Şema dışı hiçbir ad çalıştırılamaz** | `parse_cube_query` beyaz listesi — **sağlayıcıdan bağımsız** | dokunulmaz *(§7.4'ün dayanağı)* |
| K1 içi | **Sayı yalnız küpten** · sorgu **çalıştırılmadan doğrulanır** | `dry_plan` · RLS · sözleşme mührü | dokunulmaz |
| K1 → K3b | 🔴 **LLM ham satır GÖRMEZ** | Fact-Sheet · `test_t2_anlatici` 3. değişmezi | `G5` korur |
| 🔴 **K1 ↔ dış dünya** | PII binadan çıkmaz | `llm_guard.safe_call` fail-closed | ✅ **VAR** — `_ask`/`_arac_ile`/`_chat` sarılı |
| 🔴 **K1 ↔ dış dünya** | **Gerçek DEĞER ve SAYI da çıkmaz** | korunan yayılım `{{NUM_i}}`/`{{DIM_i}}` | 🔴 **`G0b` — bugün YOK** *(PII kalıbı olmayan değer serbestçe geçiyor)* |
| K3b → çıkış | **Uydurma sayı yayımlanamaz** | `narration_guard` fail-closed | `G5.3-5.4` sıkılaştırır |
| K3b → çıkış | **Uydurma yetenek/şema iddiası yayımlanamaz** | `iddia.py` | 🔴 **`G4` — bugün YOK** |

#### 🔴 Bozulma merdiveni — *"fallback sadece küpler"*

Kullanıcının satır-1 kısıtının kod karşılığı. **Her basamakta cevap hâlâ DOĞRUdur;
kaybedilen tek şey akıcılıktır.**

| # | Ne bozuldu | Sistem ne yapar | Kullanıcı ne görür |
|---|---|---|---|
| **0** | — | tam akış | 🟢 **Tam garson** — anlar · sorar · hatırlar · anlatır |
| **1** | Guard bir cümleyi düşürdü | o cümle yayımlanmaz | anlatı **kısalır**, sayılar doğru |
| **2** | Guard/`iddia` **tüm** cümleleri düşürdü | anlatı **hiç eklenmez** | `interpret.summary` — *"süssüz ama doğru"* |
| **3** | LLM erişilemez *(kota · ağ · 429)* | Intent-JSON yok → **`route()` tek başına** | deterministik cevap **+ temellendirme** *(0 token, hayatta kalır)* |
| **4** | `route()` de çözemedi | **dürüst red + MENÜ** | *"bunu yapamam — ama şunu yapabilirim"* `[G8]` |
| **5** | Katalogda hiç karşılık yok | dürüst red + terfi kuyruğuna kayıt | *"kapsam dışı"* — ve yönetici görür |

🔴 **Tasarımın en önemli özelliği bu tabloda:** `temellendirme` (`G1`) **0 token** olduğu için
**3. basamakta bile hayatta kalır**. Yani LLM tamamen düşse bile sistem *"ne anladığını"*
söylemeye devam eder. *Garson hastalanırsa mutfak yine de siparişi tekrar eder.*

⚠ Ve **hiçbir basamakta yanlış sayı yok.** Bozulma **akıcılığı** düşürür, **doğruluğu**
değil — §2.3'ün ayrımının mimarideki karşılığı budur.

#### Bu fazın dokuz maddesi resimde nerede

| Faz | Resimdeki yeri | Katman |
|---|---|---|
| `G0` | *(resimde yok — resmi ÖLÇEN alet)* | — |
| 🔴 `G0b` | **hava boşluğu geçidi** + çıkışta **geri koyma** | K1 ↔ K3b **sınırı** |
| `G1` | ❹ temellendir · ❸ marjin kapısı | K3b + K3a |
| `G2` | K2'nin tamamı | K2 |
| `G3` | K3a'nın dal seçimi *(kesme yerine aday)* | K3a |
| `G4` | çıkış kapılarından **ikincisi** | kapı |
| `G5` | ❺ anlat + korunan yayılımlar | K3b |
| `G6` | CubeQuery'nin `referans` alanı | K3a → K1 sınırı |
| `G7` | ❻ ek motoru | K3b |
| `G8` | ❼ menü · bozulma merdiveni 4. basamak | K3b |

### 1.2c · 🔴 ALAN HARİTASI — ne garson, ne mutfak, ve KAPILAR

> *"Karıştırılmamalı. Ne yaptığımızı bilmeliyiz."* — Bu bölüm o sözleşmedir. Karıştırılan
> her sınır, bu deponun adını koyduğu kusuru doğurur: **aynı kuralın iki sahibi**.

#### Ayrım testi — üç soru, herkes uygulayabilir

```
① Bu modül DOĞAL DİL okuyor ya da yazıyor mu?          → GARSON
② Bu modül VERİ / SORGU / MOTOR ile mi çalışıyor?      → MUTFAK
③ İKİSİ DE mi?  → 🔴 O zaman KAPI olmak ZORUNDA.
                    Kapı olmayan bir "ikisi de", tanımı gereği bir KUSURDUR.
```

#### Alanlar

| Alan | Ne yapar | Modüller *(bu fazı ilgilendirenler)* |
|---|---|---|
| 🗣 **GARSON** | dil okur/yazar · **hiçbir şey çalıştırmaz** | `cube_router.route` · `llm` · `niyet` · `turetme` · `typo_onerisi` · `followup` · `context` · `donem_capasi` · `netlestirme` · `belirsizlik_chipi` · `soz` · `intent_semasi` · `kapsam` · `embed_kapsam` · `yetenek` · `vqr` · **`diyalog`**`[G2]` · **`temellendirme`**`[G1]` · **`ek`**`[G7]` |
| 🍳 **MUTFAK** | veri/sorgu ile çalışır · **dil bilmez** | `wren_service` · `compose` · `contracts` · `rls` · `fanout` · `katman_b` · `stats` · `contribution` · `yoy` · `kpi` · `statements` · `drill` · `metrik_kaydi` · `audit_zinciri` · `lineage` · `tazelik` |
| 🚪 **KAPI** | **ikisinin arasında durur** | aşağıdaki tablo |
| 🌉 **KÖPRÜ** | biri üretir, öteki tüketir | `interpret` · `value_index` |
| 🎨 **SUNUM** | garson tarafı çıktı biçimi | `viz` · `report` · `prescribe` · `fmt` |

#### 🚪 KAPILAR — tam liste, yön ve zorladıkları

| Kapı | Yön | Ne zorlar | Durum |
|---|---|---|---|
| `parse_cube_query` `cube_router.py:3715` | 🗣→🍳 | 🔴 **Katı beyaz liste** — şema dışı ad **çalıştırılamaz**. *Sağlayıcıdan bağımsız asıl emniyet ağı* | ✅ VAR |
| `uyum.denetle` | 🗣→🍳 | Niyet ↔ sorgu uyumu · **beyan-açık** (`uyum.py:169`) | ✅ VAR |
| `dry_plan` `wren_service.py:1504` | 🍳 içi | Sorgu **çalıştırılmadan** motorca doğrulanır | ✅ VAR |
| `planner` dört kapı | her araç | kayıt · yetki · det-önce · bütçe | ✅ VAR |
| `interpret()` `interpret.py:359` | 🍳→🗣 | 🔴 **Ham satır değil, OLGU çıkar** | ✅ VAR |
| `narration_guard` | 🗣→👤 | Metindeki her **SAYI** ±%2 → cümle düşer | ✅ VAR |
| `iddia.py` | 🗣→👤 | Her **İDDİA** şemaya karşı | 🔴 **YOK** → `G4` |
| `llm_guard.safe_call` | 🗣→🌐 **dış dünya** | PII fail-closed · `_ask`/`_arac_ile`/`_chat`'i sarar | ✅ VAR · yayılım 🔴 `G0b` |
| `pii.py` | sistem→👤 | Maskeleme, tek çıkış | ✅ VAR |

#### ⚠ Üç tehlikeli vaka — bilinçli, ama görünür olmalı

**1 · `cube_router.py` (3799 satır) İKİ ALANI BİRDEN barındırıyor.**

| Satır | Ne | Alan |
|---|---|---|
| `:3165` `route()` | NL → CubeQuery | 🗣 **GARSON** |
| `:1864` `measure_cube_candidates()` | terim → aday ölçüler | 🗣 **GARSON** |
| `:3715` `parse_cube_query()` | metin → doğrulanmış sorgu | 🚪 **KAPI** |

Bu bir kusur **değil** *(kapı, koruduğu şeyin yanında durur)* ama bir **risktir**: dosyayı
düzenleyen kişi **hangi tarafta olduğunu bilmek zorundadır**. 🔴 `G3` bu dosyaya
dokunuyor — adımlarında bu ayrım yazılı olacak.

**2 · `interpret.py` — köprü.** Mutfak üretir, garson tüketir.
**Kural:** ham satır **sızdırmaz**; yalnız hesaplanmış olgu çıkarır (`test_t2_anlatici`
3. değişmezi bunu kilitliyor).

**3 · `value_index.py` — köprü.** Veri **değerlerini** okur ama garson kullanır (varlık
çözümü). **Kural:** çözülen değer LLM'e **ham gitmez**, `{{ENT_i}}` olarak gider `[G0b.6]`.

#### 🔴 Yasaklar — kim neyi YAPAMAZ

| Alan | Yapamaz |
|---|---|
| 🗣 **Garson modülü** | SQL yazamaz · motora dokunamaz · **sayı hesaplayamaz** · ham satır göremez |
| 🍳 **Mutfak modülü** | doğal dil ayrıştıramaz · kullanıcıya cümle yazamaz · katalog dışına çıkamaz |
| 🌐 **Hiçbir modül** | `llm_guard.safe_call`'ı **atlayarak** sağlayıcıya gidemez |
| ⚖ **Hiçbir modül** | **iki kapıyı birden sahiplenemez** (KAT-1) |

#### Kapı: haritanın kendisi teste bağlanır

`tests/test_alan_haritasi.py` **(yeni, `G0b` ile)** — AST tabanlı:
- 🗣 listesindeki bir modül `wren_service` · `dry_plan` · `execute` **import edemez**.
- 🍳 listesindeki bir modül `llm` · `soz` · `followup` **import edemez**.
- `safe_call` sarmayan yeni bir sağlayıcı metodu → **CI kırmızı**.
- Yeni bir modül eklendiğinde haritada **sınıfı yoksa** → CI kırmızı.
  *(`test_modul_buyume.py`'nin muafiyet-listesi deseni — sınıfsız modül bırakılamaz.)*

### 1.3 · Neden bu mimari doğru — ve bu bizim iddiamız değil

Araştırmanın en güçlü tek bulgusu: **on üründen onu da aynı yere geldi.** Anlatım her yerde
*"zaten çalıştırılmış, zaten doğrulanmış bir sonucun üstünde"* yapılıyor — LLM'e ham veri
verip *"hesapla ve anlat"* diyen **tek bir üretim ürünü yok**.

| Ürün | Deterministik derleme katmanı |
|---|---|
| ThoughtSpot Spotter | patentli **arama jetonları** → SQL derleyici (*"text-to-SQL değil"*) |
| Snowflake Cortex Analyst | semantik model YAML + SQL derleyici doğrulama + doğrulanmış sorgu deposu |
| Databricks Genie | Unity Catalog **Metric Views** + bilgi deposu |
| Google Looker CA | LookML → yapısal Looker sorgu nesnesi |
| Power BI Copilot | tabular model + DAX ayrıştırıcı |
| Cube.dev | **Semantic SQL** (`MEASURE()`) — ambar'a doğrudan erişim **yok** |
| WrenAI | **MDL** + dry-plan doğrulama |
| dbt MetricFlow + MCP | LLM **araç seçer**, SQL **yazmaz** |
| Tableau Pulse | LLM **hiç sorgu görmez** — önceden hesaplanmış istatistik olguları anlatır |
| Vanna.ai | ❌ yok (saf RAG → ham SQL) — **ve deposu 29 Mart 2026'da arşivlendi** |

DİMA bu tablonun **en katı ucundadır** ve bu bir avantajdır. Ama tablonun ikinci yarısı
uyarıdır: **hiçbiri konuşmuyor.**

---

## §2 · KABUL REJİMİ — HANGİ KAPI NEYİ VETO EDEBİLİR

> Bu bölüm, bu fazın **en önemli** bölümüdür. Yanlış anlaşılırsa geri kalan her şey çürür.

### 2.1 · Ölçülen kusur: aletin kendisi garsonu göremiyor

Bu operasyonda `--hepsi` sekiz kez koştu. Her koşumda aynı satır çıktı:

```
✓ konuşma senaryoları    ⊘ ÖLÇÜLEMEDİ — ölçüm ön koşulu sağlanmadı (cube+llm yolu gerekir)
```

Ve `lab/deneyim.py`'nin kendi çıktısı, `--live` olmadan, kendi kelimeleriyle:
*"**yapısal duman — KAPI DEĞİL**"*.

🔴 **Yani garsonu görebilecek iki aletin ikisi de hiç koşmadı.** Garson hakkında bugüne
kadar alınan **her karar**, yalnızca mutfak metrikleriyle alındı.

### 2.2 · Ve bir ölçüm YANLIŞ ortamda yapıldı

`MIMARI.md:442`'deki kayıt: kısa devre yasağının tam uygulaması korpusu **%95,1→%93,5**
düşürdü, `eval` precision'ı **−%1,8**, süitte 7 kırmızı → **geri alındı**.

O düşüşün fiziksel anlamı: **sorular Discovery'ye düştü.** Ve kapı ortamında Discovery
`DIMA_LLM_PROVIDER=rule` — anahtarsız, boyahane şemasına gömülü, kasıtlı olarak aptal bir
yedek (`app/llm.py:657`, `:699-703`).

🔴 **Ölçülen şey *"garson devreye girince kötüleşiyor"* değildi; *"garsonun yerine mutfağın
en aptal yedeğini koyunca kötüleşiyor"*du.** Üretimde o basamakta gerçek bir LLM var. Bu bir
bulgu değil, bir **ortam artefaktıdır**, ve geri alma kararı ona dayandı.

### 2.3 · Bağlayıcı kural

> **Kapılar «DOĞRULUK» üzerindeki vetolarını KORUR, «KAPSAM PAYI» üzerindeki vetolarını
> KAYBEDER.**

| Hâlâ mutlak veto | Artık veto DEĞİL |
|---|---|
| 🔴 **Yanlış sayı** — küp ne diyorsa o | ⚪ `doğru-cube %` düşüşü |
| 🔴 **Uydurma sayı** — `narration_guard` fail-closed | ⚪ Discovery payının artması |
| 🔴 **Onaysız yazma** — `tools.py:26-29` değişmezi | ⚪ LLM çağrı sayısının artması |
| 🔴 **Sessiz başarısızlık** — dürüst red korunur | ⚪ p50 gecikmenin artması *(bütçelenir, §7)* |
| 🔴 **Şema iddiası** — `iddia.py` (G4) | ⚪ Bir turun iki LLM çağrısı yapması |

Ve bu ayrım yol haritasının **kendi kuralıdır** (§G.6a, `YH:1336`):
> *"🔴 **Kazancı ölçen alet, gerilemeyi ölçenden FARKLI OLMAK ZORUNDA.**"*

### 2.4 · Üç kodda duran engel — ve akıbetleri

| Nerede | Ne yapıyor | Bu fazda |
|---|---|---|
| `tests/test_kisa_devre_yok.py:228`<br>`assert not (app/merdiven.py).exists()` | Bir **dosyanın var olmasını** yasaklıyor → bir **tasarımı** yasaklıyor | 🔴 **Yeniden yazılır.** Bir test güvenlik sınırı koyabilir; mimari tercih donduramaz |
| aynı dosya `:174`<br>`assert len(kisa) == 11` | Merdiveni kesen dal sayısını dondurup yalnız **artışa** kırmızı veriyor | 🔴 **Cırcır tersine çevrilir:** sayı **azalmalı**; muafiyet listesi gerekçeli kalır |
| `features.yml:159`<br>`netlestirme_onceligi: "off"`<br>*(kurtarılan 0 · kaybedilen 5)* | Kararı **korpusta** ölçtü — korpus katalogdan üretilir, içinde **belirsiz soru yoktur** | 🔴 Karar **askıya alınır**, G0'ın aletinde yeniden ölçülür |

### 2.5 · Yeni kabul aleti: `lab/garson.py`

Üç ölçüm, üç **ayrı** soru:

| Alet | Sorduğu soru | Rolü |
|---|---|---|
| `lab/nl_corpus.py --kapi` | *"Cevaplanan sorunun sayısı hâlâ doğru mu?"* | **Mutfak tabanı** — doğruluk vetosu |
| `eval.run` | *"Uçtan uca cevap bozuldu mu?"* | **Mutfak tabanı** — doğruluk vetosu |
| 🆕 `lab/garson.py --live` | *"Bu bir insanla konuşmaya benziyor mu?"* | **Garson kapısı** — bu fazın tek onay kapısı |

`lab/garson.py` sıfırdan yazılmaz: `lab/deneyim.py`'nin **yedi satırlık ürün sözleşmesini**
ve `lab/konusma_senaryolari.py`'nin dokuz sınıfını **import eder**, üstüne §5'in sekiz
davranışını ekler ve `_canli_ortami_geri_yukle` ile **gerçek sağlayıcıda** koşar.

🔴 **Ve bir kural, `⊘ ÖLÇÜLEMEDİ`'nin kendi dersinden:** garson kapısı `--live` olmadan
koşarsa **yeşil vermez**, `⊘` verir. Ölçülemeyen bir şey geçmiş sayılmaz.

---

## §3 · DÜNYA NE YAPTI — KANIT

### 3.1 · Ham LLM'in üretimdeki gerçek doğruluğu (ve semantik katmanın değeri)

| Kaynak | Ölçüm | Not |
|---|---|---|
| **Anthropic, kendi iç analitiği** (2026-06-03) | Ham ambara doğrudan: **<%21**. Semantik katman + runbook + doğrulama: **>%95** | Ve: **bir ay bakım gevşetilince %95 → %65**. Doğruluk bir **defalık kazanım değil** |
| **Stonebraker** (Turing ödüllü, MIT ambarı, 1400 tablo) | **~%10** — join bağlantıları elle verilince **~%30** | Akademik kıyaslarda aynı modeller %80+ |
| **Spider 2.0** (ICLR 2025 sözlü) | GPT-4o: Spider 1.0'da %86,6 → Spider 2.0'da **%6–10,1** | Gerçek kurumsal şema = çöküş |
| **dbt Labs 2026** (ACME Insurance, açık kaynak, boylamsal) | 2023: text-to-SQL %32,7 vs semantik %60,5 · **2026: %64,5 vs %72,7** · **kapsam-içi sorularda semantik %100** | Fark **27,8 → 8,2 puana indi** |
| **Cube.dev eşli kıyas** (arXiv 2604.25149) | Semantik doküman **olmadan** üç öncü model: **%45,5–50,5** | +17…+23 puan |
| **GitLab** (Cortex Analyst, üretim) | Basit sorular %85–95 · **karmaşık sorular %75** | Ekibin kendi ifadesi: *"kusurlu kalıyor"* |

🔴 **En önemli tek cümle — dbt'nin kendi sonucu:**
> *"Text-to-SQL'de başarısızlık **makul görünen yanlış bir cevaptır**. Semantik katmanda
> başarısızlık **bir hata mesajıdır**… Text-to-SQL yanlış sayıyı **neşeyle** verir."*

Yani semantik katmanın gerçek değeri **ortalama doğruluk değil, başarısızlığın SESLİ
olmasıdır**. DİMA'nın dürüst reddi tam olarak budur — ve garson, o sesi **kısan** değil,
**kullanılabilir** kılan katmandır.

### 3.2 · Nasıl başarısız oluyorlar — ve DİMA neden bağışık

| Başarısızlık | Ölçüm | DİMA'daki karşılığı |
|---|---|---|
| `WRONG_FILTER` (yanlış kısıt) | **%54,6** | Küp koyar; `always_filter` fail-closed |
| `WRONG_SCOPE` (yanlış dönem/birim) | **%14,4** | `_period_gate`, dönem çapası |
| Fan-out join ile **çift sayma** | Power BI Copilot saha vakası: *"Q3'te %15 sıçrama"* — sıçrama yoktu, 3 işlem iki kez sayılmıştı | **Fan-out sertifikası** |
| **Belirlenimsizlik** | Aynı sorgu 1000 kez: **en sık cevap yalnız 78 kez** | Küp yolu belirlenimci |
| Sayısal alan halüsinasyonu | DefAn: GPT-4o **%46** | Sayı LLM'den **hiç geçmiyor** |
| Toplama-sonrası aritmetik | Exaone/BI: **%54 semantik hata, %4 cevap doğruluğu** | `stats.py` + `interpret.py` |

**Ve genel halüsinasyon kıyasları bu riski GİZLİYOR:** Vectara'nın liderlik tablosunda genel
özetleme halüsinasyonu **%0,8–3,1**. Sayısal içerik izole edilince **%46–54**. *Genel bir
halüsinasyon ölçüsüne bakıp sayısal anlatımı güvenli sanmak, bu alanın en yaygın hatasıdır.*

### 3.3 · Ürün mezarlığı — üç kuşak NL-BI öldü

- **Tableau Ask Data** — Şubat 2024'te emekli (Cloud), 2024.2'de (Server)
- **ThoughtSpot SearchIQ** — 7.0'da düştü; kendi belgeleri: *"her zaman Beta'daydı, üretime hiç çıkmadı"*
- **ThoughtSpot Sage** (GPT-3'lü) — GA'ya **hiç ulaşmadı**, Spotter'la değiştirildi
- **Power BI Q&A** — Aralık 2026 hedefiyle kaldırılıyor
- **Narrative Science / Quill / Lexio** — satın alındı, ürün olarak öldü
- **Vanna.ai** — deposu 29 Mart 2026'da **arşivlendi**

⚠ Ama dikkat: **toplu bir kırım değil, bir DARALMA.** Hayatta kalanlar (ThoughtSpot,
Snowflake, dbt) kapsamlarını **daralttı** — ThoughtSpot açık NL aramadan deterministik
jetonlara çekildi. *Ölçek yerine kesinlik satın aldılar.* DİMA zaten o tarafta duruyor.

### 3.4 · 🔴 Kimsenin yapmadığı şey — fırsat tam burada

Araştırmanın en net boşluğu:

> **On üründen yalnız Snowflake belgeli bir ön-sınıflandırma yapıyor** (belirsiz soruyu
> *reddediyor*). **Etkileşimli «sor–cevapla–devam et» netleştirme döngüsü HİÇBİRİNDE YOK.**
> Genie · Looker · Cube · WrenAI örtük çözüm kullanıyor (kullanım sıklığı ağırlığı, değer
> sözlüğü). ThoughtSpot kasıtlı olarak **kullanıcı başlatsın** diyor.
> Power BI'ın **kendi belgeleri** netleştirme sorması gereken bir vakada sistemin
> **kendinden emin yanlış cevap verdiğini** örnek olarak gösteriyor.

Ve Cortex Analyst'in **kendi belgelenmiş sınırları**:
- *"Önceki SQL sorgularının sonuçlarına **erişimi yok**."*
- *"Yalnız SQL ile çözülebilen soruları yanıtlar. *«Ne trendler görüyorsun?»* gibi geniş iş
  sorularına içgörü **üretmez**."*
- *"Çok fazla tur içeren ya da niyet sık değişen konuşmalarda takipleri yorumlamakta
  **zorlanabilir**."*

🔴 **DİMA'nın `interpret.py`'si (519 satır, deterministik olgu üretimi) bu üç sınırın
üçünü de bugün aşabilecek durumda ve kullanılmıyor.** Garson fazının en büyük tek
farklılaşma fırsatı burada.

### 3.5 · Diyalog: ölçülmüş sayılarla

| Bulgu | Sayı | Sonuç |
|---|---|---|
| **JPMorgan, çok-turlu text-to-SQL bellek mimarileri** (arXiv 2605.26394, Mayıs 2026 · ön baskı) | Tur-1: **%67–73**. **Tur-3 durumsuz: BEŞ MODELİN BEŞİNDE DE %0.** 2 turluk çalışma penceresiyle: **%87,6–100** | 🔴 Durum taşımak *iyileştirme* değil, **var olma koşulu** |
| aynı çalışma | Karmaşık bellek (epizodik erişim, semantik zenginleştirme): **−12,6 … +14,1 puan** | 🔴 **Fazla bellek ZARAR verebilir** — basit tut |
| **SParC / CoSQL** (Yale/Salesforce) | Soru-eşleşmesi %74,0 vs **etkileşim-eşleşmesi %52,6** (RASAT+PICARD) | ~20 puanlık yapısal fark: **zor olan takip** |
| **AmbiSQL** (SIGMOD 2025) | Belirsizlik tespiti **%87,2 hassasiyet**; dar çoktan-seçmeli netleştirme → SQL exact-match **+%50** | 🔴 **Netleştirmenin ölçülmüş getirisi** |
| **Amazon Alexa** (ASRU 2021, üretim ölçeği) | Aşırı netleştirme **UX'i bozar** → *seçici* tetikleme, sabit eşik değil | Ne zaman sorulacağı **öğrenilen bir karardır** |
| **Wang & Ai** (ACM TOIS 2022) | *"Netleştirme sormak sonuç döndürmenin güvenli alternatifi **değildir**"* — kötü soru üretilebilir, iyi soru bile sabır harcar | Sorma **bedava değildir** |
| **EACL 2024** (MIMICS, 2464 sorgu) | Özgül sorular genelden iyi · **3–5 seçenek 2'den iyi** · en yüksek puanlı kalıp: *"[X] hakkında ne bilmek istersiniz?"* | Chip tasarımı için doğrudan reçete |
| **Clark & Brennan 1991** (*en az ortak çaba* ilkesi) | İnsan konuşmasında **kabul et → sonra onar**, genellikle **önce sor**'dan ucuzdur | Varsayımı **beyan ederek cevaplamak** meşru bir stratejidir |

⚠ Ve dürüst bir boşluk: **«varsayımı beyan ederek cevapla» ile «önce sor» arasında kontrollü
bir karşılaştırma çalışması YOK.** Ürünlerde yaygın, teorik zemini 1991'e dayanıyor, ama
ölçülmemiş. **`lab/garson.py` bunu ölçebilecek konumdadır** — bu fazın yan ürünü olarak
alanın açık sorusuna veri üretebiliriz.

### 3.6 · Sayı uydurmasını önleme — kanıtlanmış iki katman

**Katman 1 — ÖNLEME (asıl savunma).** Tableau Pulse'ın kendi mühendislik yazısı:
istatistik servisi olguları üretir, o olgular **yer gerçeği** sayılır, LLM'in tek işi cümle
kurmaktır. Ve kritik teknik: **«formatting tags»** ile belirli yayılımlar (kullanıcının
seçtiği metrik adı gibi) LLM ne yaparsa yapsın **birebir korunur**.

**Katman 2 — TESPİT (arka durak).** *Proof-Carrying Numbers* (arXiv 2509.06902): sayısal
yayılımlar **iddia-bağlı jeton** olarak üretilir, **model değil renderer** doğrular,
**varsayılan doğrulanmamıştır** ve fail-closed'dur. Sahada da var: Grid-Mind, düzenli-ifade
tabanlı sayısal iddia tarayıcısı kullanıyor.

🔴 **Ve yapılmayacak olan şey — ölçülmüş negatif sonuç:**
Huang ve ark. (ICLR 2024): **dış bir doğruluk kaynağı olmadan öz-düzeltme performansı
DÜŞÜRÜR.** GPT-3.5, CommonSenseQA: **%75,8 → %41,8** (iki turda −34 puan). GPT-4, GSM8K:
%95,5 → %89,0.
→ **LLM'e *"sayılarını bir kontrol et"* dedirtmek yasaktır.** Doğrulama daima **veriye**
karşı yapılır, modele karşı değil.

⚠ Ve kısıtlı çözümleme (Outlines/XGrammar/native tool-use) bu sorunu **çözmez**: JSON'un
**yapısını** garanti eder, **içeriğini** etmez. Hiçbir kütüphane *"rakamlar yalnız kaynak
kümesinden kopyalanabilir"* kısıtı sunmuyor — bu **özel iş**.

### 3.7 · Türkçe yüzey üretimi — dürüst tablo

| Seçenek | Gerçek durum |
|---|---|
| **Zemberek** `WordGenerator` | Gerçek, doğru, sözlük destekli (istisna kelimeleri *bedavaya* çözer). **Ama:** son sürüm **0.17.1 · Temmuz 2019**, README'si *"slow maintenance mode"*, sağlıklı Python bağlayıcısı **yok** (JPype ile JVM taşımak gerekir). ⚠ Ve `MIMARI.md:1929`: `pip install zeyrek` **ağ ister**; CI `--network none` |
| **google-research/turkish-morphology** | **19 Nisan 2026'da arşivlendi** — salt okunur |
| **TRmorph** | Tazelik işareti **2015-11** |
| Hafif ek kütüphaneleri (`affixi`, `Turkish.js`) | Hobi ölçeği; **elle bakılan istisna listesi** gerektiriyor |
| **LLM** | Türkçe **türetimsel bileşimsellikte** ölçülmüş zayıf: GPT-4 %54,2 (dağılım içi) / %43,9 (dışı) — **insan %97,1 / %95,0**. ⚠ Ama bu **en zor uç**; *"bilinen bir özel ada hâl eki ekle"* hiçbir kıyasla ölçülmemiş |

🔴 **Karar (§6, G7):** Zemberek **alınmaz** (JVM + ağ + ölü bakım, üç ayrı risk). LLM'e de
bırakılmaz. **Kapalı bir alan için küçük, deterministik bir ek motoru yazılır** — ve o alan
gerçekten kapalıdır: anlatıcının enjekte ettiği şeyler yalnızca *metrik adı · boyut değeri ·
sayı · tarih*.

⚠ **Ve danışman belgesinin *"son harfe bakar"* önerisi YANLIŞ:** ek, sayının **okunuşuna**
göre değişir (`3'te` ← *üç*; `1.000.000'a` ← *milyon*). Sayı→okunuş tablosu **zorunludur**.

---

## §4 · BUGÜN NE VAR — KANITLI ENVANTER

> Notasyon: **VAR** = kod + tüketici + varsayılan açık · **KAPALI** = kod + tüketici, bayrak `off`
> · **YETİM** = kod var, tüketici yok · **YOK** = kod yok.
> ⚠ `features.resolve_for()` yalnız `"off"` olanı eler (`features.py:602`) → **`beta` = AÇIK**.

### 4.1 · Garsonun AĞZI — neredeyse hazır

| Yetenek | Durum | Kanıt |
|---|---|---|
| `interpret()` deterministik olgular (8 tür) | **VAR** | `interpret.py:359`; `cikti_yorumlama: beta` |
| `narration_guard` (±%2, cümle-bazında düşürme, fail-closed) | **VAR** | `narration_guard.py:180,215`; `TOLERANS=0.02` |
| `t2_anlatici` — akıcı Türkçe paragraf | 🔴 **KAPALI** | `features.yml:94`; **tek tüketici hazır ve bağlı** `answer.py:426`; 20 test |
| `soz.py` metin katalogu (tek hitap "sen", jargon yasağı) | **VAR** | `soz.py:50-61` |
| Chip türleri: `turetme` · `tanim` · devam sorusu | **VAR + render** | `ReportCard.tsx:1114,1137,1165` |
| Makbuz (üç katmanlı) | **VAR** | `Makbuz.tsx`; `ui_kanit_gorunurlugu: beta` |
| AI Act Md.50 işareti | **VAR** | `answer.py:955` |
| Konuşma türleri (`neden`·`normal_mi`·`ne_yapmali`·`isaret`·`anlat`) | **VAR** | `followup.py:65-71` |
| `_cevap_ustunde_konus` — yeni SQL yazmadan konuşma | **VAR** | `ask.py:1702` |

**Bugün kullanıcının gördüğü nesir:** `interpret.summary` — nokta ile birleştirilmiş olgu
cümleleri. Tek cümle, şablon, deterministik. **Akıcı paragraf yok.**

### 4.2 · Garsonun BELLEĞİ — yok

| Yetenek | Durum | Kanıt |
|---|---|---|
| `Baglam` + 7 kural + iki turluk pencere | **VAR** (saf fonksiyon, LLM yok) | `context.py:52-60,88,180` |
| **Diyalog durum makinesi / slot** | 🔴 **YOK** | `bekleyen_netlestirme` → repo genelinde **0 isabet** |
| `netlestirme.birlestir` *(AJ0b'nin "çekirdeği")* | 🔴 **YOK** | `netlestirme.py` yalnız `duzey·sorar_mi·govde_notu·kanit_sinifi` tanımlıyor |
| `app/diyalog.py` | 🔴 **YOK** | — |
| Turlar/oturumlar arası hafıza | 🔴 **YOK** | `ConversationMessage` bir **arşiv**; hiçbir karar yolu okumuyor |
| `netlestirme.py` `yuksek` düzeyi | ⚠ **BEYAN** | Kod yalnız `kapali`yı uyguluyor (`ask.py:2613-2621` açık itiraf) |

🔴 **Bu, yol haritasının en büyük yanlışını çürütür.** AJ0b'nin en güçlü argümanı
*"sıfırdan yazmıyoruz — `0.5b`'nin `netlestirme.birlestir`'i çekirdek"* idi (`YH:998`).
**O fonksiyon yok. `0.5b` FAZ 0'da ✅ ilan edilmiş ama kodda hiçbir izi yok.**
AJ0b **sıfırdan yazılacaktır** ve fiyatı buna göre konulmalıdır.

### 4.3 · Garsonun DİLİ — Intent-JSON dar

`intent_semasi.py:57-101` destekliyor: `cube` (tek) · `measures[]` · `dimensions[]` ·
`timeDimensions[]` · `filters[]` · ret dalı.

🔴 **Desteklemiyor** (`intent_semasi.py:51-55`, *"bilerek dışarıda"*):
`compare` / **YoY** · **çoklu dönem** · `blend` (çapraz-küp) · `order` / `limit`.

→ **LLM *"şubata göre"*yi anlıyor ama mutfağa SÖYLEYEMİYOR.** Kuzey yıldızının "B" harfi
budur (`YH:815`) ve v1'in `5.6` maddesini **bloke** ediyor.

⚠ Ve bir sessiz garanti kaybı: `llm_sema_kisitli: beta` açık, ama şema kısıtı **yalnız
Anthropic'te gerçek**; OpenAI-uyumlu sağlayıcılar şemayı **bilerek yok sayıyor**
(`llm.py:574-580`). Failover ikinci sağlayıcıya düştüğü an garanti **sessizce** kayboluyor.

### 4.4 · Planla kodun ayrıştığı dört yer

| # | Belge diyor | Kod diyor |
|---|---|---|
| Ş1 | AJ0 hiç inmedi (gelecek zaman) | **Yarısı indi** (kapı: `test_kisa_devre_yok.py`), **yarısı ölçülüp geri alındı** (`MIMARI.md:442`). Ve o ölçümden doğan **dördüncü koşul** (*"bir sonraki basamak gerçekten daha yetenekli olmalı"*) **yol haritasında yok** |
| Ş2 | `MIMARI.md:67` — 18. yasak ⟳ **UYGULANMADI** | `MIMARI.md:442` aynı yasağı **inmiş** olarak, kapısı ve geri alma ölçümüyle anlatıyor. **İkisinden biri bayat** |
| Ş3 | `0.5b` ✅ bitti | Kodda **sıfır iz** (§4.2) |
| Ş4 | ⚠ **DÜZELTİLDİ** — `app/niyet.py` *"plansız"* değil | Katman **planlıydı**, ama **yol haritasında değil, denetim belgesinde**: `KÇ-0 · ÇÖZÜMLEME ve EŞLEŞTİRME AYRILSIN`. Ve o belge rolünü de yazmış: *"Uyum kapısı ancak bir **niyet nesnesi** varsa yazılabilir; **KÇ-1, KÇ-0'ın ilk müşterisidir**"* ve *"KÇ-0 **çatıdır** — kademeli, önce yalnız gözlemci"*. 🔴 **Sonuç güçlenir: `Niyet`, `referans`ın (G6) doğal taşıyıcısıdır ve bu bir tercih değil, belgelenmiş bir tasarım kararıdır** |

### 4.4b · Denetimin sekiz kök çözümü — bugünkü durum

| # | Kök çözüm | Durum | Nerede |
|---|---|---|---|
| **KÇ-0** | Çözümleme ↔ eşleştirme ayrımı | ◐ **çatı kuruldu** | `app/niyet.py`, `niyet_izi: prod`; iki müşteri taşındı, üçü taşınmadı (gerekçeli) |
| **KÇ-1** | Niyet–sorgu **uyum kapısı** | ⚠ **indi — ama fail-closed DEĞİL** | `app/uyum.py`, yedi değişmez. `:169`: *"Kapı **fail-closed değil, BEYAN-AÇIK**: cevabı öldürmez, **etiketler**"* |
| **KÇ-2** | `in q` sözlük taraması yasağı | ✅ | KÖK-7a; `test_kok7a_in_q_yasagi.py` |
| **KÇ-3** | Sözlük → kural dönüşümü | ◐ **kısmi** | `app/turetme.py` (KÖK-7d) fiil/isim ayırıcısını verdi |
| **KÇ-4** | Çok-geçiş zorunluluğu (`finditer`) | ✅ | KÖK-7c; `test_kok7c_cok_gecis.py` |
| **KÇ-5** | Tek teşhis kaynağı | ✅ | `cube_router.teshis()`; `test_kok9_tek_teshis.py` |
| **KÇ-6** | Belirsizlik sıraya değil **chip'e** | ✅ | `app/belirsizlik_chipi.py` (KÖK-9) |
| **KÇ-7** | **Yetenek beyanı** — *"anlamadım"* ≠ *"yapamıyorum"* | 🔴 **AÇIK** | → 🔴 **bu belgenin `G8`'i.** Bağımsız olarak aynı sonuca varıldı |

🔴 **Ve `KÇ-1`'in sapması kayda geçer.** Denetimin `Ö8` maddesi *"ACİL — HEPSİNDEN ÖNCE"*
işaretliydi ve kabul ölçütü **fail-closed**ti: *"`mart cirosunu şubat ile kıyasla` tek
birleşik sayı **DÖNDÜRMESİN**"*. Uygulama **beyan-açık** seçti: cevap döner, **ihlal
etiketlenir** (`kismi_cevap_notu`). Kapı ölçümündeki `beyanli_kismi: 58` tam olarak bu
sayıdır.

Bu **savunulabilir bir sapmadır** ve araştırma da destekliyor (Clark & Brennan 1991,
*en az ortak çaba*: kabul et → sonra onar, önce sor'dan ucuzdur). **Ama sessiz kalmamalı:**
`G1` bu mekanizmayı *"bir şey ters gittiğinde"*den *"her turda"*ya genelleştirir — yani
beyan-açık kapının **eksik yarısını tamamlar**.

### 4.5 · Ölü kontroller — kullanıcı tıklıyor, hiçbir şey olmuyor

| Kontrol | Durum |
|---|---|
| `mod` (hızlı/derin) anahtarı | UI'da var (`ChatPanel.tsx:398-421`); sunucu `hizli_derin: off` → **alan yok sayılıyor** |
| SSE akışı + durdurma düğmesi | Sunucu + istemci **tam yazılmış**; `ask_async_discovery: off` → **hiç tetiklenmiyor**. Ve aktı bile yalnız **iz adımı** taşıyor, **metin akmıyor** |
| `Planlayici.sec()` | İki tüketici de `agent_plan_secimi: off` arkasında; açılsa bile pilot **23 aracın 3'ünü** çağırıyor |
| 🔴 `llm_sema_kisitli` | Bayrak **`beta` = AÇIK** görünüyor, ama seçilen sağlayıcıda (OpenRouter → `OpenAICompatibleSqlGenerator`) **etkisi sıfır** — şema bilerek kullanılmıyor. **Açık görünen üçüncü ölü kontrol** (§7.4) |

---

## §5 · GARSON SÖZLEŞMESİ — SEKİZ SATIR

`lab/garson.py`'nin ölçtüğü şey. `deneyim.py`'nin yedi satırının **üstüne** kurulur.

| # | Davranış | Nasıl ölçülür | Kaynak |
|---|---|---|---|
| **1** | **Karşılar.** Sosyal ifade → 0 LLM · 0 SQL | telemetri + `source` | mevcut, `sosyal_sinif: prod` |
| **2** | **Kendi diliyle sipariş alır.** Kullanıcı katalog dili öğrenmek zorunda değil | 15 gerçek ifade, `--live` | §3.1 |
| **3** | 🔴 **Siparişi TEKRARLAR.** Cevaptan önce *"anladığım şu: Mart 2026 · Satış Cirosu · Merkez şube"* | her cevapta `temellendirme` alanı dolu | §3.2 (%69 hata bu sınıfta) |
| **4** | **Belirsizde SORAR — ama seçici.** Dar, 3–5 seçenekli, özgül | soru/tur oranı **bir tavanla sınırlı**; sorulan turda doğruluk artmalı | AmbiSQL +%50 · ASRU 2021 |
| **5** | 🔴 **Sorduğunu HATIRLAR.** Cevap geldiğinde tur baştan başlamaz | 5 turluk thread'de *"ilişkilendiremedim"* **0 kez** | JPMorgan %0→%87,6 |
| **6** | 🔴 **Düzeltilir.** *"hayır, fire demiştim"* → slot düzelir, baştan başlamaz | onarım senaryosu yeşil | §3.5 |
| **7** | **Tabağı ANLATIR.** Guard'lı akıcı paragraf; her sayı doğrulanmış | `narration` dolu · guard düşürme oranı **ölçülü** | Tableau Pulse · PCN |
| **8** | 🔴 **Menüyü BİLİR.** Yapamadığında *ne yapabileceğini* söyler | ret cevabında `kapasite` alanı dolu | dbt *"sesli başarısızlık"* |

**Değişmeyen güvence:** sayıyı **her zaman** küp koyar. En kötü durum *"süssüz ama doğru"*.

---

## §6 · FAZLAR

**Sıra:** `G0` → 🔴 `G0b` → `G1` → `G2` → `G3` → `G4` → `G5` → `G8`
**Paralel yürüyebilir:** `G6` (AJ2 — v1'in `5.6`'sını açar) · `G7` (ek motoru)

Her madde **yedi bloklu** (`D5` disiplini + adım kılavuzu) — **on faz**:
**NEDEN · NE · NASIL · KAPI · GERİ AL · BÜYÜKLÜK · ADIMLAR**.
⚠ **Gün/saat tahmini YOK** — bilinçli: adım düzeyinde süre uydurmak §13.8'in (zan yasağı)
ihlali olurdu. Yerine **büyüklük** (küçük/orta/büyük) ve **bağımlılık** yazılır.

---

### G0 · ALET — *garsonu görebilen ölçüm* 🔴 **BLOKLAYICI**

**NEDEN.** Ölçüldü: `konusma_senaryolari` sekiz koşumun sekizinde de `⊘ ÖLÇÜLEMEDİ`;
`deneyim.py` `--live` olmadan kendi çıktısında *"KAPI DEĞİL"* diyor. **Garson hakkındaki
her karar bugüne kadar yalnız mutfak metrikleriyle alındı** (§2.1). Alet kurulmadan atılan
her adım ölçülemez, ölçülemeyen her adım geri alınamaz.

**NE.** `lab/garson.py` — §5'in sekiz satırı, `--live` zorunlu.
· `deneyim.py`'nin yedi satırı + `konusma_senaryolari.py`'nin dokuz sınıfı **import edilir**
(kopyalanmaz — `deneyim.py:34-55`'in kendi kuralı).
· `_canli_ortami_geri_yukle` + `LIVE_BEKLE` aynı yerden.
· Çıktı: `lab/reports/garson/<senaryo>.md` — aynı zamanda **ürün demosu**.
· `lab/kapi.py`'ye **yeni bir seviye değil**, yeni bir hedef: `--garson` (yalnız açık talep).

**NASIL.** Sıfırdan senaryo yazılmaz: `konusma_ifadeleri.py` + `gercek_dunya.py`'nin
persona×zorluk matrisi zaten 15 gerçek ifade taşıyor. Üstüne §5'in 3·5·6·8 numaralı
davranışları için **yeni senaryo sınıfları** eklenir (temellendirme · süreklilik · onarım ·
kapasite).
⚠ **Ölçüm aracı şemasını KENDİ derlemesinden alır** (`test_olcum_semasi_taze.py` kuralı) —
`gercek_dunya.py`'nin bu turda öğrendiği ders burada da geçerli.

**KAPI.**
- `lab/garson.py --live` **koşuyor** ve bir taban raporluyor.
- `--live` olmadan koşulursa **yeşil vermiyor**, `⊘` veriyor.
- Bilinen bir farkı yeniden üretebiliyor: `t2_anlatici` açık/kapalı arasında §5/7 satırı
  **farklı** çıkmalı. Çıkmıyorsa **alet kör**dür ve düzeltilene kadar hiçbir faz inmez.

**GERİ AL.** Yok — yeni bir ölçüm aleti hiçbir davranışı değiştirmez.

**BÜYÜKLÜK.** Küçük · bağımlılık: **yok** · 🔴 **BLOKLAYICI — bundan önce hiçbir kod inmez.**

**ADIMLAR** — *hedef: sekiz koşumda `⊘` veren satır ilk kez bir SAYI üretsin*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G0.1** ✅ | 🔴 **Sağlayıcı kararını YAZ** *(ölçümden ÖNCE)* | `.env`: `DIMA_LLM_PROVIDER=openrouter` **açıkça** + `DIMA_OPENROUTER_MODEL=<nvidia/…>` + `DIMA_OPENROUTER_SELECT_MODEL`. Failover'a **bırakılmaz** — `llm.py:1295`'te openrouter 5. sırada | `/health` etkin sağlayıcıyı **openrouter** gösteriyor |
| **G0.2** ✅ | Kota ön uçuşu | `konusma_senaryolari._kota_on_ucusu` (`:138`) **çağrılır**, yenisi yazılmaz | Kota yetersizse koşum **başlamadan** durur |
| **G0.3** ✅ | `lab/garson.py` iskeleti | `_canli_ortami_geri_yukle` (`:68`) + `LIVE_BEKLE` (`:218`) **import** edilir *(kopyalanmaz — `deneyim.py:34-55`'in kuralı)* | `python lab/garson.py --live` koşuyor |
| **G0.4** ✅ | Sekiz satırlık sözleşme | `deneyim.py`'nin 7 satırı **devralınır** + §5/3 (temellendirme) ve §5/8 (menü) eklenir | `SOZLESME` sabiti **8 satır** |
| **G0.5** ✅ | Üçüncü durum devralınır | `KAPSAM_DISI` · `ON_KOSUL_YOK` (`deneyim.py:229-230`) import | `--live` **olmadan** koşunca yeşil **vermiyor**, `⊘` veriyor |
| **G0.6** ✅ | Dört yeni senaryo sınıfı | `temellendirme` · `sureklilik` · `onarim` · `kapasite` — her biri ≥1 vaka; ifadeler `lab/konusma_ifadeleri.py`'den | Sınıf başına vaka sayısı raporda |
| **G0.7** ✅ | 🔴 **Şema-dışı çıktı oranı** *(§7.4'ün ölçüm borcu)* | `parse_cube_query`'nin reddettiği Intent-JSON yüzdesi rapora yazılır | Sayı `lab/reports/garson/` altında |
| **G0.8** ✅ | Taban dondurma | `_tabani_dondur` deseni (`konusma_senaryolari.py:814`) | `lab/garson_baseline.json` doğdu |
| **G0.9** ✅ | Kapı değerlendirici | `kapi_degerlendir` deseni (`:769`) — sınıf başına taban, `⊘` **gerileme sayılmaz** | Taban altına düşünce **kırmızı** |
| **G0.10** ✅ | 🔴 **İKİ KOŞUM** *(KURAL G-1, §12.3)* | İki koşum; ayrışırlarsa karar **verilmez**, `⊘` + borç kaydı | İki rapor dosyası |
| **G0.11** ✅ | Kapıya bağla | `lab/kapi.py` → **yeni hedef `--garson`** *(yeni seviye DEĞİL)* | `--tam` / `--hepsi` süreleri **değişmedi** |
| **G0.12** ✅ | Kör alet testi | `t2_anlatici` açık/kapalı → §5/7 satırı **farklı** çıkmalı | Çıkmıyorsa **alet kör**; G1 başlamaz |
| **G0.14** ✅ | 🔴 **Ölü kontrol kararı** | `hizli_derin`: ya sunucuya **bağlanır** ya UI'dan **kaldırılır** *(§15.5)*. Çalışıyormuş gibi görünen kontrol, garson fazında **ürün kusurudur** | Tıklama bir şey **yapıyor** ya da düğme **yok** |
| **G0.15** ✅ | **Kaset iskeleti** *(§12.2b/`K` katmanı)* | `--live` koşumunda sağlayıcı yanıtları `lab/kasetler/<senaryo>.json`'a **kaydedilir**; `K` modunda kayıt oynatılır. VQR deseni — yeni motor yazılmaz | Kaset koşumu **sağlayıcısız** yeşil |
| **G0.13** ✅ | 📌 **COMMIT** | `feat(G0): garson ölçüm aleti — ilk taban` · **`MIMARI.md`**: `llm_sema_kisitli` NO-OP (§13.6/4) · `features.yml` yorumları: `prompt_enhancer` **mimari gerekçe** (§1.1d) + `agent_plan_secimi` **bayat gerekçe** düzeltmesi | `OPERASYON-DURUM.md` `B-G1` kapandı |

---

### G0b · HAVA BOŞLUĞU — *mutfakla garson arasındaki sınır* 🔴 **G5'in ÖN KOŞULU**

**NEDEN.** Ölçüldü ve **açık**: `grep -rn "mask_text\|pii\." app/answer.py app/llm.py` →
**0 isabet**. `app/pii.py` var (`mask_tckn` · `mask_email` · `mask_phone` · `mask_iban`)
ama **kullanıcıya giden cevabı** maskeliyor — **LLM'e gideni değil**.

Bugün LLM'e giden **üç kanal**, üçü de ham:

| # | Kanal | Ne gidiyor | Risk |
|---|---|---|---|
| ① | `select_cube(question, catalog)` — `ask.py:756` | **ham kullanıcı sorusu** + katalog adları | Soru PII taşıyabilir: *"Ahmet Tekstil'in bakiyesi"* |
| ② | `generate_sql(question, schema)` — `ask.py:3598` | ham soru + **tam şema** | ① + şema/iş sırrı sızıntısı |
| ③ | `anlat(soru, gercekler)` — `answer.py` | ham soru + **hesaplanmış olgular** | 🔴 **En ağırı** — gerçek boyut değerleri (makine adı · müşteri adı) **ve gerçek sayılar** |

🔴 **Sağlayıcı `auto`→`openrouter` olduğu an bu «binadan çıkan veri»ye dönüşür.** Ve `G5`
kanal ③'ün hacmini **artırıyor**. Kapı önce kurulmalı.

> 🔴 **DÜZELTME (2026-08-07, kod denetimi):** bu maddenin ilk taslağı *"yeni bir
> `app/hava_boslugu.py` yazılacak"* diyordu. **YANLIŞTI — kapı ZATEN VAR.**
> `app/llm_guard.py::safe_call()` fail-closed bir çıkış geçidi ve `llm.py`'nin **üç
> sağlayıcı metodunu** sarıyor (`_ask:375` · `_arac_ile:457` · `_chat:521`) — yani
> **yapısal olarak atlanamaz**, yukarıda yeni bir çağrı yeri açılsa bile.
> Yeni modül yazmak **ikinci sahip** doğururdu; bu deponun **1 numaralı kusuru**.

**NE.** 🔴 **`llm_guard` GENİŞLETİLİR — yeni modül YAZILMAZ.**

**Bugün ne yakalıyor** (`llm_guard.py:49-64`, `pii.py` tek sahip):

| Yakalanan | Nasıl |
|---|---|
| TCKN · e-posta · telefon · IBAN | `pii.mask_x(yuk) != yuk` → ihlal → **çağrı YAPILMAZ** |
| Kütük disiplini | Değerin kendisi **loglanmaz**, yalnız **tür adı** — *"sızıntıyı raporlarken sızdırmamak"* |
| Girdi tarafı *(üç ayrı süzgeç)* | `sensitivity.prompt_safe_values` · `cube_router.build_catalog` · `ask.py` |

🔴 **Bugün ne KAÇIYOR — ve boşluk tam burada:**

| Kaçan | Örnek | Neden kaçıyor |
|---|---|---|
| **Boyut değeri** | `"RAM 3"` · `"Ahmet Tekstil A.Ş."` | PII **kalıbı** değil — hiçbir maskeye uymuyor |
| **Gerçek sayı** | `12.430` · `%62` · `18.200 TL` | aynı |
| **Fact-Sheet'in tamamı** | `interpret()` olguları | kanal ③ (`anlat`) bunları **olduğu gibi** gönderiyor |

**G0b'nin eklediği iki parça:**
· **Korunan yayılım**: Fact-Sheet'teki gerçek değer/sayı → `{{DIM_i}}` / `{{NUM_i}}` /
`{{ENT_i}}`; gerçek değer **hiç çıkmaz**.
· **Geri koyma**: renderer haritadan gerçek değeri koyar; eksik/fazla yer tutucu →
cümle **düşer** *(yapısal doğrulama)*.
· **Çıkış kütüğü genişler**: bugünkü *"tür adı"* disiplini korunur — yer tutucu **sayısı**
yazılır, değer **asla**.

**NASIL.** 🔴 **Ve bu, kaydettiğim bir çelişkiyi ÇÖZÜYOR** (§9.3/Ç-24): danışman belgesinin
anonimleştirme önerisi `narration_guard` ile bağdaşmıyordu, çünkü LLM'e **soyutlama**
gönderiyordu (*"Segment_A"*, *"1,2 std üstü"*) — gerçek sayıyı hiç görmeyen LLM'in yazdığı
metinde guard'ın doğrulayacağı bir şey kalmıyordu.

**Korunan yayılım bu tuzağa düşmez ve guard'ı ZAYIFLATMAZ — GÜÇLENDİRİR:**

| | ±%2 eşleştirme *(bugün)* | Korunan yayılım *(G0b+G5)* |
|---|---|---|
| LLM gerçek sayıyı görür mü | ✅ evet → **bina dışına çıkar** | ❌ **hayır** |
| Doğrulama nasıl | metindeki sayıyı DB çıktısıyla **karşılaştır** | her `{{NUM_i}}` **tam bir kez** geçmiş mi — **yapısal** |
| Uydurma sayı mümkün mü | ⚠ tolerans içinde **evet** | 🔴 **hayır** — LLM rakam üretemez ki |
| Yıl/sıra muafiyeti gerekli mi | evet *(`YIL_ARALIGI` · `SIRA_ESIGI`)* | **hayır** — muafiyet kavramı ortadan kalkar |

⚠ **Dürüst sınır:** hava boşluğu **mutlak değildir.** Kullanıcının **sorusu** LLM'e gitmek
zorundadır — anlaşılacak şey odur. Orada yapılabilecek: `value_index` ile çözülen varlıklar
**yerelde** çözülür ve `{{ENT_1}}`'e çevrilir; serbest metindeki TCKN/e-posta/telefon/IBAN
`pii.py` ile maskelenir. **Geriye kalan risk yazılıdır**: kullanıcı kendi cümlesine
maskelenemeyen bir sır yazarsa, o sır çıkar. Bu, kurumsal kipte `yol_siniri` ile
kapatılabilir *(kanal ② tamamen kapanır)*.

**KAPI.** `tests/test_hava_boslugu.py` + `tests/test_alan_haritasi.py`:
- 🔴 **Kaçak testi:** `safe_call` sarmayan yeni bir sağlayıcı metodu → **CI kırmızı**
  (AST kapısı — `test_kisa_devre_yok.py` deseni).
- 🔴 **Alan haritası testi** (§1.2c): 🗣 modül `wren_service`/`dry_plan` **import edemez**;
  🍳 modül `llm`/`soz`/`followup` **import edemez**; sınıfsız yeni modül → CI kırmızı.
- Gerçek boyut değeri / sayı **giden yükte bulunamaz** (fixture: bilinen değerler aranır).
- TCKN · e-posta · telefon · IBAN → maskeli.
- Her `{{X_i}}` dönen metinde **tam bir kez**; eksik/fazla → cümle **düşer**.
- Çıkış kütüğü **değer yazmaz**, yalnız tür+sayı yazar *(kütüğün kendisi sızıntı olmasın)*.
- `yol_siniri=yalnız küp` → kanal ② hiç açılmaz.

**GERİ AL.** Geçit **fail-closed**: kapatılamaz. `safe_call` ihlal bulursa **LLM çağrısı
yapılmaz** — bozulma merdiveninin 3. basamağına düşülür *(deterministik cevap + temellendirme)*.
*Bir güvenlik kapısının geri alma yolu, kapıyı kaldırmak değil, korunan yolu kapatmaktır.*

**BÜYÜKLÜK.** Orta · bağımlılık: `G0` · 🔴 **`G5`'in zorunlu ön koşulu** · güvenlik kalemi.

**ADIMLAR**

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G0b.1** ✅ | Envanter | Üç kanalın giden yükü **birebir** kayda geçer *(ne gidiyor, hangi alan)* | Tablo `MIMARI.md`'de |
| **G0b.2** ✅ | 🔴 **Geçidi GENİŞLET** *(yeni modül YAZMA)* | `app/llm_guard.py`'ye yayılım politikası eklenir. `safe_call` **zaten** `_ask`/`_arac_ile`/`_chat`'i sarıyor | `hava_boslugu.py` **doğmadı** *(ikinci sahip yok)* |
| **G0b.3** ✅ | Kanal envanteri | Üç kanal **zaten** `safe_call`'dan geçiyor *(sağlayıcı metodu seviyesinde)* — doğrulanır, yeniden bağlanmaz | AST: `safe_call`'suz sağlayıcı metodu **yok** |
| **G0b.4** ✅ | AST kaçak kapısı | `safe_call` sarmayan yeni bir sağlayıcı metodu → **CI kırmızı** | Test yeşil |
| **G0b.5** ✅ | PII maskesi | ✅ **ZATEN VAR** (`llm_guard.ihlalleri_bul`) — yalnız **regresyon testi** yazılır | 4 vaka yeşil |
| **G0b.6** ✅ | Varlık çözümü | `value_index` ile çözülen değer → `{{ENT_i}}`; LLM'e **kural** olarak gider | ✅ **İNDİ** (`app/varlik.py` · `tests/test_varlik_perdesi.py`). ⊙ Ölçüm önce yapıldı ve **bir yarısı zaten kapalıydı**: `corrected_q` LLM'e hiç gitmiyor (artık kilitli). 🔴 Açık kapı **başkasıydı** — `build_catalog` boyut **değerlerini** prompt'a yazıyor; perde oraya kuruldu. ⚠ Ve ölçüm bir tuzak buldu: `ciro` bu katalogda **hem ölçü sinonimi hem boyut değeri** — perde onu yutunca sorudan ÖLÇÜ siliniyordu. Sözlükle çakışan değer artık perdelenmiyor (`typo_suggest`'in *çapraz-konu* kuralının aynısı) |
| **G0b.7** ✅ | Korunan yayılım | Fact-Sheet'teki sayı ve boyut değeri → `{{NUM_i}}` / `{{DIM_i}}` | Fixture taraması temiz |
| **G0b.8** ✅ | Geri koyma | Renderer haritadan gerçek değeri koyar; eksik/fazla yayılım → **cümle düşer** | Yapısal doğrulama |
| **G0b.9** ✅ | Çıkış kütüğü | ✅ disiplin **zaten var** (`llm_guard`: değer loglanmaz) — yer tutucu **sayısı** eklenir | Kütükte değer yok |
| **G0b.9a** ✅ | 🖥 **ÖN YÜZ — güven sinyali** | `Makbuz.tsx`'in **mevcut** *"tam iz"* bloğuna (`:205-215`) tek satır: `hava boşluğu · 3 yer tutucu · dışarı çıkan: yok`. 🔴 Kullanıcı **verisinin çıkmadığını görmeli** — görünmeyen güvenlik, satılamayan güvenliktir. Yeni panel/blok **YOK** | `ui_kanit_gorunurlugu` altında |
| **G0b.9b** ✅ | 🔴 **Alan haritası kapısı** | **yeni** `tests/test_alan_haritasi.py` — §1.2c'nin sınıflandırması AST ile kilitlenir | 🗣/🍳 çapraz import **yok** |
| **G0b.10** ✅ | 📌 **COMMIT** | `feat(G0b): hava boşluğu — korunan yayılım llm_guard'a eklendi` · `MIMARI.md`: **üçüncü değişmez** *(§13.6/6)* | `Ç-24` **çözüldü** kaydı |

---

### G1 · TEMELLENDİRME — *siparişi tekrarla* · 0 LLM · 0 token

**NEDEN.** Üretimdeki başarısızlığın **%69'u** (`WRONG_FILTER` %54,6 + `WRONG_SCOPE` %14,4)
*"SQL çalıştı, makul bir sayı döndü, ama başka bir sorunun cevabıydı"* sınıfındadır.
Power BI'ın **kendi belgeleri** bu vakayı örnekliyor: kullanıcı 2024 sorar, Copilot yanlış
tarih tablosuna filtreleyip *"2024 verisi yok"* der. Bir garson bunu **ilk saniyede**
görünür kılar — ve bu, sıfır token maliyetiyle yapılabilir.

Ve DİMA'daki karşılığı ölçülü: `belirsizlik_chipi` (KÖK-9) çok-sahipli terimi zaten
söylüyor, ama **doğru anlaşılmış** bir soruda sistem ne anladığını **hiç söylemiyor**.

**NE.** `AskResponse.temellendirme: dict | None` —
`{olcu: "Satış Cirosu (TL)", donem: "Mart 2026", kirilim: ["Şube"], filtreler: [...], cube: "satis"}`
· Kaynağı **yalnız `CubeQuery`** — anlatı değil, muhasebe.
· Frontend: `ReportCard`'ın en üstünde, tablodan **önce**, tek satır rozet dizisi.
· Her rozet **tıklanabilir** → o alanı değiştiren chip (`POST /cube` ile 0 LLM).

**NASIL.** ⚠ **Düzeltme — kural ZATEN YAZILI, uygulaması dar.** `app/soz.py:19` birebir:
*"**Kural: ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR.**"* ve `:62-66`'daki netleştirme metinleri
**`{ne}` yuvası** taşıyor — *"çağıranın anladığı şey"*. 🔴 **Yani ilke var ama yalnız
NETLEŞTİRMEDE**; başarılı turda hiç kullanılmıyor. `G1` o kuralı **her tura** genişletir —
yeni kural icat etmez. Yeni sözlük de yazılmaz: `interpret.py:397 _ad()` +
`answer.py:330-343 build_catalog` **tek kaynak**. 🔴 **Bu madde LLM çağırmaz, sayı üretmez, şema iddiası kurmaz** — güven
modeline hiç dokunmaz.

🔴 **Ve mekanizma zaten yarısı yazılmış hâlde duruyor.** `app/uyum.py` yedi değişmezi
denetliyor ve ihlal bulduğunda `kismi_cevap_notu()` ile **kullanıcıya söylüyor** — yani
sistem *"ne anladığını beyan etme"* yeteneğine **sahip**, ama yalnız **bir şey ters
gittiğinde** kullanıyor (`beyanli_kismi: 58`). G1 bunu genelleştirir:

| | Bugün | G1'den sonra |
|---|---|---|
| Bir değişmez ihlal edildiğinde | `kismi_cevap_notu` → *"kıyas istendi ama…"* | **aynı** |
| **Her başarılı turda** | 🔴 **hiçbir şey söylenmiyor** | `temellendirme` → *"anladığım şu: …"* |

*Yani `KÇ-1`'in beyan-açık kararı doğruydu, ama yarım kaldı: sistem yanıldığını söylüyor,
**anladığını söylemiyor**.* G1 o yarıyı tamamlar — ve `uyum.py`'nin `Ihlal` üretecini
**ikinci kez yazmaz**, aynı beyan kanalını kullanır (tek sahip).

⚠ **Ve bir sınır dürüstçe yazılır:** temellendirme hatayı **kullanıcıya devreder**. Etiketi
okumayan kullanıcı yanlış sayıyı yine taşır. Bu bir **garanti değil**, bir **görünürlük**
kazanımıdır. (Danışman belgesi bunu garanti gibi sunuyor — §9/Y-2.)

**KAPI.** `tests/test_temellendirme.py`:
- Başarılı her cevapta alan **dolu** (boşsa CI kırmızı).
- İçeriği `CubeQuery` ile **birebir tutarlı** (uydurma alan yok).
- Ham kolon adı **basılmıyor** (`_ad()` üzerinden).
- `test_cevap_alani_yetim_degil.py`: frontend tüketicisi **var**.
- `lab/garson.py` §5/3 satırı **yeşil**.
- 🔴 `nl_corpus --kapi` + `eval`: **gerilemez** (bu madde cevabı değiştirmiyor, etrafını).

**GERİ AL.** Alan `None` bırakılır; frontend zaten `?? null` ile davranıyor. **Bayrak
gerekmez** — geri alma yüzeyi yok.

**BÜYÜKLÜK.** Küçük · bağımlılık: `G0` · **bu fazın en yüksek fayda/maliyet oranlı maddesi.**

**ADIMLAR** — *arka uç 4 adım, ön yüz 3 adım, kapı 3 adım*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G1.1** ✅ | Saf üretici | **yeni** `app/temellendirme.py::kur(cq, cube_meta, catalog) -> dict \| None` — **LLM yok, sayı yok**; `interpret.py:397 _ad()` ile görünen adlar | Birim test: aynı `cq` → aynı çıktı |
| **G1.2** ✅ | Sözleşme alanı | `app/schemas.py:306 AskResponse` → `temellendirme: dict \| None = None`; alan **`explain` ile karıştırılmaz** (o **yol**, bu **anlam**) | `openapi.json`'da görünüyor |
| **G1.3** ✅ | Tek çağrı yeri | `app/answer.py::seal()` zincirine — `_maybe_interpret`'ten **sonra**, `_build_explain`'den **önce** | `grep -c "temellendirme.kur"` = **1** *(tek sahip)* |
| **G1.4** ✅ | Beyan kanalı **paylaşılır** | `uyum.py::kismi_cevap_notu` **yeniden yazılmaz**; ihlal varsa o, yoksa `temellendirme` — aynı kanal | İki ayrı beyan üreteci **yok** (AST kapısı) |
| ~~G1.4b-d~~ | 🔴 **DÜŞÜRÜLDÜ — marjin ZATEN VAR** | Ölçüldü (`G1`, 2026-08-07): `cube_router._match_cube` **çok sinyalli** bir marjin sistemi taşıyor — ölçü-sinonim uzunluğu (`:908`) · alt-dize spesifikliği (`:932`) · boyut-kanıtı (`:937`) · **4-harf cube marjini** (`:947`); kırılamazsa `None` → `cube_tie_candidates` chip → **SORUYOR**. Ve `value_index:28` `AUTO_MARGIN=0.08` değer eşleşmesinde aynısını yapıyor. 🔴 Dördüncü bir marjin sahibi yazmak **KAT-1 ihlali** olurdu | §1.1c'nin ağacı **zaten uygulanmış** — belge onu TARİF ediyor, EMRETMİYOR |
| **G1.5** ✅ | Ön yüz tipi | `src/lib/types.ts` → `temellendirme?: Temellendirme \| null` *(`:202 interpretation` komşuluğu)* | `tsc` temiz |
| **G1.6** ✅ | Ön yüz render | `ReportCard.tsx` — `SourceBadge`'in (`:537`) **hemen altına**, tablodan **önce** rozet dizisi | Görsel: tek satır, taşmıyor |
| **G1.7** ✅ | Rozetler tıklanabilir | Her rozet → o alanı değiştiren chip; `POST /cube` (`ask.py:948`) ile **0 LLM** | Tıklama LLM çağırmıyor *(telemetri)* |
| **G1.8** ✅ | Kapı testi | **yeni** `tests/test_temellendirme.py`: başarılı cevapta alan **dolu** · `cq` ile **birebir tutarlı** · **ham kolon adı yok** | 4 test yeşil |
| **G1.9** ✅ | Yetim kapısı | `tests/test_cevap_alani_yetim_degil.py` yeni alanı **görüyor** | Kapı yeşil |
| **G1.10** ✅ | Kazanç + gerileme | `lab/garson.py --live` §5/3 **yeşil** ‖ `kapi.py --tam` + `eval` **gerilemedi** | İkisi de kayıtlı |
| **G1.11** ✅ | 📌 **COMMIT** | `feat(G1): temellendirme — sistem ne anladığını SÖYLÜYOR` · `MIMARI.md`'ye **§13.6/3** (`KÇ-1` beyan-açık sapması) | |

---

### G2 · DİYALOG BELLEĞİ — `app/diyalog.py`

**NEDEN.** JPMorgan (Mayıs 2026): **tur-3'te durumsuz beş modelin beşi de %0**; iki turluk
çalışma penceresiyle **%87,6–100**. Durum taşımak bir iyileştirme değil, **var olma
koşuludur**.

DİMA'da bugün: netleştirme **stateless**. Chip tam bir soru metni taşır (`belirsizlik_chipi.py:106`),
sunucu **hiçbir açık slot saklamaz**, tur **sıfırdan koşar**. Çok adımlı daraltma
(*"hangi küp? → hangi ölçü? → hangi dönem?"*) **yapısal olarak imkânsız**.

🔴 **Ve planın "sıfırdan yazmıyoruz" argümanı ÇÜRÜK:** `netlestirme.birlestir` ve
`bekleyen_netlestirme` **kodda yok** (§4.2). Bu madde **sıfırdan yazılıyor** ve fiyatı
buna göre konuluyor.

**NE.** `app/diyalog.py` — saf fonksiyonlar (`context.py` felsefesi), dört yetenek:

| # | Yetenek | Bugün | Sonra |
|---|---|---|---|
| 1 | **Slot durumu** | 11 dal `cube_query=None` ile **return** | Açık slot kaydedilir, tur bitmez |
| 2 | **Devam** | Netleştirme cevabı **yepyeni soru** sanılır (`KURAL_TAZE`) | Özgün niyet **korunur**, slot dolar |
| 3 | **Onarım** | *"hayır şubat demiştim"* → **baştan başlar** | Tek slot düzelir, kalan korunur |
| 4 | **Temellendirme** | — | G1'in çıktısı **buraya bağlanır** |

· Sözleşme: `AskResponse.diyalog_durumu: {acik_slotlar, sorulan, dolu, tur_no} | None`
· Frontend: açık slot **görünür** (yeni panel yok — mevcut chip satırında).

**NASIL.** 🔴 **Bellek BASİT tutulur.** Aynı JPMorgan çalışması: karmaşık bellek
(epizodik erişim, semantik zenginleştirme) **−12,6 … +14,1 puan** — yani zarar verebilir.
`context.py`'nin bilinçli **iki turluk** penceresi (`context.py:83-85`) **doğru sınırdır ve
genişletilmez**. Retrieval **eklenmez** (deponun kendi ölçümü: +14/−16).

· `Baglam`'ın yedi kuralı (`KURAL_CAPA` … `KURAL_ATIF`) **devam ve onarımın zeminidir** —
yeniden yazılmaz, **çağrılır**.
· 🔴 **`app/niyet.py` ile ilişki BU MADDEDE karara bağlanır** (Ş4): `Niyet` nesnesi zaten
`donemler · kirilimlar · filtreler · olcu_adaylari · bilinmeyenler` taşıyor. **Açık slot =
`Niyet`'in boş alanı.** İki ayrı temsil **yazılmaz** (KAT-1).

**KAPI.** `tests/test_diyalog.py`:
- **Devam:** netleştirme cevabı sonrası özgün niyet korunur, `KURAL_TAZE` **ateşlenmez**.
- **Onarım:** *"hayır, şubat"* **yalnız dönem slotunu** değiştirir; ölçü/kırılım korunur.
- **Tek sahip:** `Niyet` dışında ikinci bir slot temsili **yok** (AST kapısı).
- **Basitlik kilidi:** bağlam penceresi **>2 tur** olamaz (test bunu kilitler).
- `lab/garson.py` §5/5 ve §5/6 satırları **yeşil**.
- 🔴 `nl_corpus --kapi`: **gerilemez** — bu katman cevap üretmiyor, cevabın etrafını yönetiyor.

**GERİ AL.** `diyalog: off` → slot saklanmaz, bugünkü stateless davranış **birebir**.
⚠ **§G'nin geri alma riski en düşük maddesi budur** — ne LLM çağırır, ne sayı üretir, ne
şema iddiası kurar.

**BÜYÜKLÜK.** 🔴 **Büyük — bu fazın en büyük tek maddesi** · bağımlılık: `G0`.
⚠ Planın *"taşınıyor"* varsayımı **çürüdü** (§4.2): sıfırdan yazılıyor.

**ADIMLAR** — *🔴 sıra bağlayıcı: önce SLOT, sonra DEVAM, en son ONARIM*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G2.1** ✅ | 🔴 **ÖNCE KARAR: tek temsil** | `app/niyet.py`'nin `Niyet`'i **açık slotun taşıyıcısıdır**. *Açık slot = `Niyet`'in boş alanı.* İkinci bir slot dataclass'ı **yazılmaz** *(`KÇ-0`, KAT-1)* | Karar `MIMARI.md`'de yazılı |
| **G2.2** ✅ | Modül iskeleti | **yeni** `app/diyalog.py` — saf fonksiyonlar, `context.py:37-41` felsefesi. **`re` import etmez** *(dil işi `niyet.py`/`turetme.py`'nin)* | AST kapısı: `re` yok |
| **G2.3** ✅ | **Slot durumu** | `acik_slotlar(niyet) -> list[str]` — `Niyet`'in boş zorunlu alanları | Birim test: 3 vaka |
| **G2.4** ✅ | Sözleşme alanı | `schemas.py:306` → `diyalog_durumu: dict \| None` `{acik_slotlar, sorulan, dolu, tur_no}` | `openapi.json` |
| **G2.5** ✅ | Netleştirme **slot yazar** | 11 netleştirme dalı `sorulan` slotunu **kaydeder** *(davranış değişmiyor — yalnız kayıt)* | `diyalog_durumu` dolu dönüyor |
| **G2.6** ✅ | 📌 **ARA COMMIT** | `feat(G2/1): slot durumu — sistem NE SORDUĞUNU biliyor` | Davranış **birebir bugünkü** |
| **G2.7** ✅ | **Devam** | Netleştirme cevabı gelince `KURAL_TAZE` **ateşlenmez**; özgün niyet `Baglam`'dan **birleştirilir** | `test_diyalog.py::test_devam` |
| **G2.8** ✅ | **Onarım** | *"hayır, şubat demiştim"* → **yalnız dönem slotu** değişir; ölçü/kırılım **korunur**. `followup.py`'nin kalıp disiplini *(kelime sınırı)*, yeni sözlük **yok** *(ADR-0008)* | `test_diyalog.py::test_onarim` |
| **G2.9** ✅ | Ücretsiz kapanış | `netlestirme.py`'nin `yuksek` düzeyi burada **gerçekten uygulanır** *(`ask.py:2613-2621`'in itirafı kapanır)* | Üç düzey ayrışıyor |
| **G2.10** ✅ | 🔴 **Basitlik kilidi** | Bağlam penceresi **>2 tur olamaz**; retrieval **eklenmez** *(JPMorgan −12,6 · deponun kendi +14/−16)* | Test pencereyi **kilitler** |
| **G2.11** ✅ | Bayrak | `features.py` + `features.yml` → `diyalog: "alpha"` | `off` → davranış birebir bugünkü |
| **G2.12** ✅ | Ön yüz | Açık slot **mevcut chip satırında** görünür — 🔴 **yeni panel YOK** *(PK-1)* | Panel sayısı **değişmedi** |
| **G2.13** ✅ | Kazanç + gerileme | `garson.py --live` §5/5 ve §5/6 **yeşil** ‖ `--tam` **gerilemez** *(bu katman cevap üretmiyor)* | Kayıtlı |
| **G2.14** ✅ | 📌 **COMMIT** | `feat(G2): diyalog belleği — sorduğunu HATIRLIYOR` · `MIMARI.md`'ye **Katman 2** | `B-G2` kapandı |

---

### G3 · MERDİVEN — *AJ0'ın davranış yarısı, DOĞRU ortamda*

**NEDEN.** Yol haritasının kendi ölçümü, §G'nin en yüksek kaldıraçlı maddesi:
**13 turun dördünde** yazım-benzerliği kısa devresi turu öldürüyor (`YH:1518`).
Ve kullanıcının kendi vakası: *"mart ayında ciro şubata göre nasıl değişti"* →
*"«eğitim» mi demek istediniz?"*

🔴 **Ama karar askıya alınmıştır, reddedilmiş değil.** Geri alma ölçümü (`MIMARI.md:442`,
korpus %95,1→%93,5) **`rule` sağlayıcısıyla** yapıldı — yani *"garsonun yerine mutfağın en
aptal yedeğini koyunca"* (§2.2). Üretimde o basamakta gerçek bir LLM var.

**NE.** Merdiven bitiricileri **iki**ye iner: (a) pozitif bir cevap, (b) kullanıcının açık
`yol_siniri`'si. Cevapsız bir dal **aday** olarak kaydedilir, merdiven devam eder, sonda **en
iyi sonuç** seçilir.
· `explain.path` bir **merdiven izine** çevrilir: hangi basamak karar verdi, hangileri
atlandı, hangi adaylar birikti.
· Frontend: iz **makbuzda görünür** (yeni panel yok).

**NASIL.** 🔴 **Dördüncü koşul yazılıdır ve bu maddenin merkezidir:**
> *Bir dalı adaya çevirmek ancak **bir sonraki basamak gerçekten daha yetenekliyse**
> doğrudur.*

Bu yüzden madde **iki koldan** ölçülür ve **ikisi ayrı raporlanır**:
1. **`rule` sağlayıcı ile** — bugünkü ölçümün tekrarı, karşılaştırma tabanı olarak.
2. 🔴 **Gerçek sağlayıcı ile** (`--live`) — **asıl ölçüm.**

Ve G2 bir **ön koşuldur**: *"kesme"* ile *"sorup bekleme"* farklı şeylerdir. Slot belleği
olmadan bir dalı adaya çevirmek, kullanıcıyı cevapsız bırakıp süreci de uzatır.

**KAPI.** `tests/test_kisa_devre_yok.py` **yeniden yazılır**:
- 🔴 `assert not (app/merdiven.py).exists()` **KALDIRILIR.** *Bir test bir güvenlik sınırı
  koyabilir; bir mimari tercihi donduramaz.*
- 🔴 `assert len(kisa) == 11` → `assert len(kisa) <= <önceki>` **cırcır tersine çevrilir**:
  sayı azalabilir, artamaz. Muafiyet listesi ve gerekçe zorunluluğu **korunur**.
- Yeni metrik: **«cevapsız kesme oranı»** — cevap üretmeyen bir basamağın karar verdiği ama
  altında hâlâ çalışabilir basamak bulunan turların oranı. `nl_corpus` bunu **bugün sayabilir**.
- `lab/garson.py --live`: §5/2 ve §5/4 satırları **iyileşir**.
- 🔴 **Doğruluk vetosu duruyor:** `eval` precision ve `sessiz_yanlis` **artmayacak**.
  Kapsam payı düşebilir; **yanlış cevap sayısı düşemez**.

**GERİ AL.** Muafiyet listesine gerekçeli bir dal eklemek **geri alma değil, görünür
istisnadır**. Yasağın kendisi `MIMARI.md §5`'e girer.

**BÜYÜKLÜK.** Orta · bağımlılık: `G0` + `G2` · **iki ölçüm koşumu** içerir.

**ADIMLAR** — *🔴 ölçüm önce, kod sonra*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G3.1** ✅ | 🔴 **ÖNCE ÖLÇ — `rule` ile** | Bugünkü geri almayı **aynı ortamda tekrarla** (`MIMARI.md:442`'nin sayısı üretilebiliyor mu?) | %95,1→%93,5 **yeniden çıkıyor** → taban geçerli |
| **G3.2** ✅ | 🔴 **SONRA ÖLÇ — gerçek sağlayıcı** | Aynı değişiklik, `DIMA_LLM_PROVIDER=openrouter` | İki sayı **yan yana** raporda |
| **G3.3** ✅ | Karar | İki sayı ayrışıyorsa → geri alma bir **ortam artefaktıydı**; ayrışmıyorsa → gerçek maliyet | Karar + gerekçe yazılı |
| **G3.4** ✅ | Cevapsız kesme oranı | `nl_corpus`'a yeni metrik: cevap üretmeyen basamağın karar verdiği **ama altında çalışabilir basamak olan** tur oranı | Şirket başına sayı |
| **G3.5** ⊘ | Aday defteri | Merdiven bitiricileri **ikiye** iner: pozitif cevap · açık `yol_siniri`. Cevapsız dal **aday** olur | `app/merdiven.py` *(adı serbest)* — ⊘ **BİLEREK YAZILMADI.** Mekanizma bir kez yazılmış, ölçülmüş ve geri alınmıştı (`test_kisa_devre_yok.py`); bu turda yeniden yazıldı ve **yine geri alındı** — bağlanmamış modül = **yetim** (`OPERASYON.md §6/1`). *Bir mekanizmayı ölçemeden kurmak, kararı ertelemenin pahalı bir biçimidir.* |
| **G3.6** ⊘ | 🔴 **Kapıyı YENİDEN YAZ** | `tests/test_kisa_devre_yok.py`: `assert not (app/merdiven.py).exists()` **KALDIRILIR** · `len(kisa) == 11` → `<= <önceki>` **cırcır ters** | Muafiyet + gerekçe zorunluluğu **korunuyor** — ⊘ `G3.5`'e bağlı — aday defteri olmadan kapı neyi yeniden yazacağını bilmez |
| **G3.7** ⊘ | 🖥 Merdiven izi | ⚠ *Düzeltme:* **render ZATEN VAR** — `Makbuz.tsx:209-213` `explain.path`'i *"tam iz"* `<details>` bloğunda basıyor. 🔴 **Yeni UI yazılmaz**, `explain.path`'in **içeriği** zenginleşir: hangi basamak karar verdi · hangileri atlandı · hangi adaylar birikti | Aynı blokta, yeni panel yok — ⊘ `G3.5`'e bağlı — defter yoksa `explain.path` zenginleşemez |
| **G3.8** ✅ | 🔴 **Doğruluk vetosu** | `eval` precision ve `sessiz_yanlis` **artmadı** | Kapsam düşebilir; **yanlış artamaz** |
| **G3.9** ✅ | 📌 **COMMIT** | `feat(G3): kısa devre yasağı — cevapsız dal cevaplı yolu KESMİYOR` · `MIMARI.md` **§5'in 18. yasağı + dördüncü koşulu + ÖLÇÜM ORTAMI** | `B-G5` kapandı *(§5 ↔ `:442` çelişkisi biter)* |

---

### G4 · İDDİA KAPISI — `app/iddia.py` 🔴 **G5'in ÖN KOŞULU**

**NEDEN.** `narration_guard`'ın **kendi docstring'i** itiraf ediyor:
*"Sayı **İÇERMEYEN** cümleler geçer: bu kapı **sayı uydurmasını** engeller, **üslubu
değil**."*

Yani bugün şu üç cümle **hiçbir kapıdan takılmaz**:
- *"Fire verisi 2019'dan beri kayıtlı."* → **şema iddiası**, doğrulanmamış
- *"İstersen tedarikçi kırılımı da ekleyebilirim."* → **yetenek iddiası**; o boyut yoksa
  kullanıcı *"olsun"* der ve **sistem çuvallar**
- *"Hesabın doğru olduğundan eminim."* → **doğrulanamaz güven beyanı**

⚠ Ve ironik biçimde bu üçüncüsü **danışman belgesinin kendi örnek çıktısında** var (§9/K-4).

🔴 **`t2_anlatici` bu kapı olmadan açılırsa, korunmayan bir yüzey açılır.**

**NE.** `app/iddia.py::dogrula(metin, schema, sonuc) -> Rapor`
· Metindeki **her katalog sözcüğü** `service.schema()`'da bulunmalı.
· **İzinli söz-edimi beyaz listesi:** *sor · var olanı öner · ne yaptığını açıkla ·
bilmediğini söyle*.
· **Yasak:** olmayan yetenek vadetmek · sonuçta olmayan bir olguyu iddia etmek ·
doğrulanamaz güven beyanı.

**NASIL.** 🔴 **`narration_guard` deseniyle BİREBİR** — ikinci bir doğrulama mimarisi
icat edilmez: cümle cümle çalışır, **düşen cümleyi düşürür** (metnin tamamını değil),
**fail-closed**, ve **düşme oranını loglar**. İkisi de `answer.py::seal()`'in önünde.

**KAPI.** `tests/test_iddia_kapisi.py` — `narration_guard`'ın 20 testlik titizliğiyle:
- Katalogda olmayan boyut adı geçen cümle **düşer**.
- Yetenek vaadi **düşer**. İzinli söz-edimi **geçer**.
- Sağlayıcı çökerse **fail-closed** (metin yok, cevap yine döner).
- 🔴 **Düşme oranı ÖLÇÜLÜR ve raporlanır.** `narration_guard`'ın kendi dersi:
  *"kullanılamayan kapı kapatılır ve o zaman hiç yoktur"*. Oran bir tavanı aşarsa kapı
  **agresif**tir ve gevşetilir — sessizce değil, ölçüyle.
- **Bedava denetim:** kapı deterministik metinlerde de koşar. Orada bir cümle düşerse
  **deterministik yolda bir kusur var demektir**.

**GERİ AL.** Kapı fail-closed olduğu için geri alma = **anlatıcıyı kapatmak**. Kapının
kendisi bayrak taşımaz.

**BÜYÜKLÜK.** Orta · bağımlılık: `G0` · 🔴 **`G5`'in ön koşulu.**

**ADIMLAR** — *`narration_guard`'ın ikizi; ikinci mimari icat edilmez*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G4.1** ✅ | Modül | **yeni** `app/iddia.py::dogrula(metin, schema, sonuc) -> Rapor` — `narration_guard.py`'nin **birebir deseni**: cümle cümle, düşeni düşür, fail-closed, oranı logla | İmza + docstring |
| **G4.2** ✅ | Katalog sözcüğü denetimi | Metindeki her katalog terimi `service.schema()`'da **bulunmalı** | Olmayan boyut adı → cümle **düşer** |
| **G4.3** ✅ | İzinli söz-edimi beyaz listesi | *sor · var olanı öner · ne yaptığını açıkla · bilmediğini söyle* | İzinli cümle **geçer** |
| **G4.4** ✅ | Yasak sınıflar | olmayan **yetenek** vaadi · sonuçta olmayan **olgu** iddiası · doğrulanamaz **güven beyanı** | Üçü için ayrı test |
| **G4.5** ✅ | `seal()` önüne bağla | `answer.py::seal()` — `narration_guard` ile **aynı hizada**, ondan **önce** | İki kapı da metni görüyor |
| **G4.6** ✅ | 🔴 **Düşme oranı ölçülür** | Oran raporlanır; bir tavanı aşarsa kapı **agresif**tir ve **ölçüyle** gevşetilir *(`narration_guard`'ın kendi dersi: kullanılamayan kapı kapatılır)* | Oran `lab/reports/`'ta |
| **G4.7** ✅ | **Bedava denetim** | Kapı **deterministik** metinlerde de koşar; orada düşen cümle = **deterministik yolda kusur** | Bugün 0 düşmeli |
| **G4.8** ✅ | Kapı testi | **yeni** `tests/test_iddia_kapisi.py` — `narration_guard`'ın 20 testlik titizliğiyle; sağlayıcı çökünce **fail-closed** *(metin yok, cevap yine döner)* | ≥12 test yeşil |
| **G4.8b** ✅ | 🖥 **ÖN YÜZ — düşen cümle izi** | `Makbuz.tsx`: *"iddia kapısı: N cümle düşürüldü"*. `narration_guard`'ın izi neredeyse **aynı yerde** durur — ikinci bir panel açılmaz | Sayı görünüyor · panel sayısı değişmedi |
| **G4.9** ✅ | 📌 **COMMIT** | `feat(G4): iddia kapısı — LLM'in her İDDİASI şemaya karşı doğrulanıyor` · 🔴 `MIMARI.md` **§4'ün değişmezi İKİYE BÖLÜNÜR** *(§13.6/1 — bu fazın en önemli mimari kaydı)* | `B-G3` kapandı |

---

### G5 · ANLATICI — `t2_anlatici` açılır, iki yükseltmeyle

**NEDEN.** On üründen onu da anlatımı *"çalıştırılmış, doğrulanmış sonucun üstünde"*
yapıyor (§1.3) — DİMA'da bu desen **yazılı, testli (20 test), bağlı ve KAPALI**
(`features.yml:94`; tek tüketici `answer.py:426`). Kapalı olmasının gerekçesi bir karar
değil, **ölçülmemişlik**: `MIMARI §6.19z`'de `t2_anlatici` kazanç ölçümü **`⊘ ÖLÇÜLEMEDİ —
kota`**.

Ve bugünkü nesir tek cümlelik `interpret.summary`. Kullanıcının *"robotik"* dediği şey
tam olarak bu.

**NE.** Bayrak `alpha` → ölç → `beta`. Üstüne **iki yükseltme**:

**(a) Birebir korunan yayılımlar** *(Tableau Pulse deseni — ÖNLEME)*
Metrik adı, boyut değeri ve sayı, LLM'e **işaretli yayılım** olarak verilir ve çıktıda
**birebir** korunur. Tespit etmekten iyidir: uydurulmasını **engeller**.

**(b) PCN disiplini** *(arXiv 2509.06902 — TESPİT)*
· **Varsayılan: doğrulanmamış.** Bir sayı ancak bir kaynağa **bağlanabiliyorsa**
"doğrulanmış" sayılır.
· ⚠ **Mevcut muafiyetler yeniden değerlendirilir ve GÖRÜNÜR olur:**
`narration_guard` bugün **1900–2100 arası tam sayıları** (yıl) ve **10'dan küçük tam
sayıları** (`SIRA_ESIGI=10`) **hiç doğrulamıyor**. Bu bilinçli, ama **belgesiz**: kullanıcı
"her sayı doğrulanır" sanıyor. Muafiyet ya kalkar ya **makbuzda yazar**.

🔴 **YAPILMAYACAK — ölçülmüş negatif sonuç:** LLM'e *"sayılarını bir kontrol et"*
dedirtilmez. Huang ve ark. (ICLR 2024): dış kaynak olmadan öz-düzeltme **−34 puana** kadar
**bozar**. Doğrulama daima **veriye** karşı yapılır.

**NASIL.** Girdi **yalnız** `interpret()` olgularıdır (`test_t2_anlatici.py`'nin 3. değişmezi).
Fact-Sheet 150–250 token; ham satır **hiç gitmez**. Model: `_select_model` (ucuz katman,
`config.py:68`). Prompt caching tasarımı §7'de.

**KAPI.** Mevcut `test_t2_anlatici.py` 3 değişmezi + `test_numeric_fidelity.py` **korunur**, üstüne:
- İşaretli yayılımlar çıktıda **birebir** (bozulursa cümle düşer).
- Guard **düşme oranı** ölçülür ve raporlanır.
- 🔴 **G4 kapısından geçmeden anlatı yayımlanamaz** (test kilitler).
- `lab/garson.py --live` §5/7 **yeşil**; §5/2 (analiz et → ≥3 olgu + guard'lı anlatı + ≥2 chip)
  **yeşil**.
- 🔴 **Doğruluk vetosu:** `eval` `sessiz_yanlis` **artmaz**. Uydurma sayı **sıfır**.
- ⚠ Kazanç yoksa `off` **ve gerekçesi `MIMARI.md`'ye yazılır** (§6.19z disiplini).

**GERİ AL.** `t2_anlatici: off` → bugünkü `interpret.summary`. Tek bayrak.

**BÜYÜKLÜK.** Orta · bağımlılık: 🔴 **`G4` + `G0b` (ikisi de zorunlu)** · kota planlaması gerekir —
§6.19z'nin **54×429** dersi.

**ADIMLAR** — *🔴 `G4` inmeden hiçbir adım başlamaz*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G5.1** ✅ | Ön koşul kilidi | Test: `t2_anlatici` açıkken `iddia.py` **yoksa** anlatı **yayımlanamaz** | Kilit testi yeşil |
| **G5.2** ✅ | **Birebir korunan yayılımlar** *(Tableau Pulse deseni — ÖNLEME)* | Metrik adı · boyut değeri · sayı, LLM'e **işaretli** gider ve çıktıda **birebir** korunur; bozulursa cümle **düşer** | Bozma testi: 3 vaka |
| **G5.3** ✅ | **PCN disiplini** *(TESPİT)* | Varsayılan **doğrulanmamış**; sayı ancak bir kaynağa **bağlanabiliyorsa** doğrulanmış sayılır | Bağlanamayan sayı → cümle düşer |
| **G5.4** ✅ | 🔴 **Muafiyetler görünür olur** | `narration_guard`'ın `YIL_ARALIGI=(1900,2100)` ve `SIRA_ESIGI=10` muafiyetleri: ya **kalkar** ya **makbuzda yazar**. Bugün kullanıcı *"her sayı doğrulanır"* sanıyor | Karar + kayıt |
| **G5.5** ✅ | Fact-Sheet sınırı | Girdi **yalnız** `interpret()` olguları *(`test_t2_anlatici.py`'nin 3. değişmezi)*; ham satır **hiç gitmez**; 150–250 token | Token telemetrisi |
| **G5.6** ✅ | 🔴 **Öz-düzeltme YASAK** | LLM'e *"sayılarını kontrol et"* **dedirtilmez** *(Huang ICLR 2024: −34 puan)*. Doğrulama daima **veriye** karşı | AST/prompt kapısı |
| **G5.7** ✅ | Bayrak `alpha` | `features.yml` → `t2_anlatici: "alpha"`, tek test kullanıcısı | Yalnız o kullanıcıda |
| **G5.8** ✅ | 🔴 **İKİ KOŞUM ölç** *(KURAL G-1)* | `garson.py --live` ×2; kota planı: `LIVE_BEKLE` + `_kota_on_ucusu` | İki rapor |
| **G5.9** ✅ | Karar | Kazanç varsa `beta`; yoksa `off` **+ gerekçe `MIMARI.md`'ye** | Karar yazılı |
| **G5.10** ◐ | Akış *(kolay kazanç)* | `ask_async_discovery` açılır; anlatı **token token** akar *(`ask.py:3864` hattı hazır)* — bugün yalnız **iz adımı** taşıyor | ◐ **AÇILDI, ÖLÇÜLDÜ, GERİ ALINDI.** Bayrak `off`; hat ve ön yüz tüketicisi **doğrulandı**. ⊙ A/B (aynı kod, yalnız bayrak): açıkken telemetri kapısı **2 kırmızı**, kapalıyken **12 yeşil** — LLM yoluna düşen soru **red gerekçesiz** kaydediliyor (`_teshis` şemayı arka-plan thread'inde okuyamıyor). O kolonun tek varlık sebebi *kapsam boşluğunun EN BÜYÜK kümesi*ydi. 🔴 **ÖN KOŞUL:** teşhis kuyruğa girmeden ÖNCE hesaplanıp işe taşınmalı (`_log_interaction` artık `red_gerekcesi` alıyor — mekanizma hazır). *Bir taşımayı değiştirmek ölçümü de değiştirir.* Eski kayıt: `ask_async_discovery: beta` açıldı (hat **ve** ön yüz tüketicisi ikisi de yazılıydı, tek eksik bayraktı); iz adımları **canlı** akıyor. 🔴 **Anlatı akmıyor ve AKAMAZ**: (1) `app/llm.py`'de tek bir `stream` çağrısı yok — akıtılacak token dizisi üretilmiyor; (2) olsaydı bile `narration_guard` her cümledeki **her sayıyı** doğruluyor ve **yarım cümlenin sayısı doğrulanamaz**. `Ö1`'in *cümle-tamponlu* şartı tam budur; taşıma katmanı işi, faz `S` |
| **G5.10b** ✅ | 🖥 **ÖN YÜZ — akış tüketicisi** | `ChatPanel.tsx` + `api-client.ts:306 streamAskJob` + `DurdurDugmesi.tsx` **zaten yazılı** — bayrak açılınca **gerçekten** akıyor mu, elle doğrulanır | Yazıyor-animasyonu çalışıyor |
| **G5.10c** ✅ | 🖥 **ÖN YÜZ — anlatı zaten bağlı** | `OutputInsight.tsx:82-93` (`narration`) + `ReportCard.tsx:945-955` (AI Act Md.50 işareti) — **yeni render YAZILMAZ**, yalnız doğrulanır | İşaret yalnız `narration` varken |
| **G5.11** ✅ | 🔴 **Doğruluk vetosu** | `eval` `sessiz_yanlis` **artmadı** · uydurma sayı **sıfır** | Kayıtlı |
| **G5.12** ✅ | 📌 **COMMIT** | `feat(G5): anlatıcı — guard ve iddia kapısı altında` | §5/2 ve §5/7 yeşil |

---

### G6 · KIYAS CEBİRİ — `referans` *(AJ2 · paralel yürür)*

**NEDEN.** 🔴 **Garson *"şubata göre"*yi anlıyor ama mutfağa SÖYLEYEMİYOR.**
Intent-JSON'da `compare` **hiç yok** (`intent_semasi.py:51-55`). Sonuç: LLM ya kural dışına
çıkıyor ya yazım tahmincisine düşüyor — kullanıcının şikâyet ettiği vakanın **ikinci** kök
nedeni budur.

Ve bir **v1 borcu**: `5.6` (peer kıyası) `AJ2`'ye bağlı ve **BLOKE**. §B'nin *"§G v1'e
paralel, ona bağımlı değil"* iddiasının fiilî istisnası. **v1 bugün §G'siz kapanamıyor.**

**NE.** `referans: {eksen, kaynak, hedef}` — `eksen ∈ {dönem, kohort, hedef, bütçe, sabit}`;
`yoy`/`mom`/`peer` **onun değerleri**.
· 🔴 **`compare` VE `blend` Intent-JSON şemasına GİRER.** Danışman belgesi `blend`'i sessizce
düşürüyor (§9/Ç-14) — burada düşmüyor: kuzey yıldızı ikisini birden istiyor.
· Yeni red kodu **`R11`** — *"anlaşıldı ama İFADE EDİLEMEZ"*. Bugün `R1..R10` var.
· Frontend: kıyas chip'leri **tek şablondan** (bugün `yoy` için özel dal var).

**NASIL.** 🔴 **`app/niyet.py` bu maddenin taşıyıcısıdır** — ikinci bir sahip doğmaz (Ş4).
`Niyet` bugün `donemler · donem_sayisi · turler · cok_donem · temsil_edilemeyen` taşıyor;
`TUR_KIYAS` ve `cok_donem` **zaten `temsil_edilemeyen` listesini üretiyor**. `referans` o
listenin **çözümüdür**, yeni bir kavram değil.

· Doğrulayıcılar **zaten kurulu** ve alan bu yüzden genişletilebilir: `parse_cube_query` katı
beyaz liste · `dry_plan` · fan-out sertifikası · `always_filter` fail-closed.
· Göç: `compare`'ın 7 dokunuşu `referans`'a çevrilir, eski `compare` bir süre **kabul edilir**.

🔴 **BAĞLAYICI SIRA KURALI — denetim belgesinden, birebir:**
> *"**Ö2 (ay çekimi) kıyas kapısı kurulmadan inerse**, `şubata göre` bugünkü **görünür
> reddinden** §12.2'deki **sessiz yanlışa** taşınır. **Kapsam açmak, kıyas kapısı olmadan
> iyileştirme değildir.**"*

Yani bu maddenin iki yarısının **sırası vardır ve tersi yasaktır**:
1. **ÖNCE** kıyas **kapısı** — iki adlandırılmış dönem + kıyas fiili **aralık toplamına
   çökemez**. Bugün beyan-açık (`uyum.py`); G6 ile birlikte **temsil edilebilir** hâle gelir.
2. **SONRA** kapsam — `referans` alanı ve `R11`.

⚠ **Bu, bu belgedeki tek "kapsam açmadan önce dur" kuralıdır** ve §2'nin kapsam-payı
serbestisiyle çelişmez: §2 *"kapsam düşebilir"* der; bu kural *"kapsam **yanlış cevap
üreterek** artamaz"* der. İkisi aynı ilkenin iki yönüdür — **doğruluk vetosu duruyor.**

⚠ **Ve bir sessiz risk kapatılır:** `llm_sema_kisitli` yalnız Anthropic'te gerçek
(`llm.py:574-580`). Yeni alanlar eklenirken bu **görünür** olmalı — failover ikinci
sağlayıcıya düştüğünde şema garantisi kaybolduğu **makbuza yazılır**.

**KAPI.** `tests/test_referans_dili.py`:
- `yoy`/`mom` **birebir aynı SQL** (eşdeğerlik önce ölçülür — Faz 2 deseni).
- *"mart ↔ şubat"* **adlı dönem kıyası** çalışır.
- Intent-JSON `referans` üretebiliyor (**canlı**, `--live`).
- **Tek sahip:** `referans` bilgisi `Niyet` dışında ikinci bir yerde tutulmaz.
- `R11` **kapalıyken de sayılır** (yalnız ölçüm).
- 🔴 `nl_corpus --kapi`: doğru-cube **gerilemez**.

**GERİ AL.** `referans_dili: off` → `compare` bugünkü 7 dokunuşuyla, Intent-JSON eski
biçimde. **Davranış birebir.**

**BÜYÜKLÜK.** Orta · bağımlılık: `G0` *(diğerlerinden bağımsız — **paralel yürür**)* ·
🔴 **v1'in `5.6`'sını açar** — bu fazın v1'e olan tek doğrudan borcu.

**◇ Denetimin `Ö9…Ö12` maddeleriyle eşleşme** *(§12.5 — bağımsız olarak aynı tasarıma
varılmış; kabul ölçütleri oradan **aynen** alınır)*:

| # | Denetimin maddesi | Nereye düşer |
|---|---|---|
| **Ö9** | *"`compare` göreli değil **adlandırılmış** dönem alsın"* | 🔴 **G6'nın `referans: {eksen, kaynak, hedef}` alanının ta kendisi.** Kabul: `mart cirosunu şubata göre` → **iki seri + %değişim** |
| **Ö11** | *"Taze soruda çapraz-cube birleştirme (ortak zaman ekseni)"* | 🔴 **G6'nın `blend`'i.** Kabul: `verimlilik ve ciro` → iki seri **ya da** netleştirme; **R1 değil**. *Danışman belgesinin `blend`'i düşürmesi (§9/Ç-14) bu yüzden reddedildi* |
| **Ö10** | *"`göre`'den sonra gelen **ay adı** boyut adayı sayılmasın"* | ⚪ **Mutfak/çözümleme** — `KÇ-0` (`niyet.py`) + `KÇ-6`. §11.2'de kayıtlı. ⚠ `göre`/`bazında`/`bazlı` **üç yönlü aşırı yüklü**; bu depoyu **üç kez** ısırdı — yeni bir `_BREAKDOWN_HINTS` koruması *"son N ay'a göre"* ifadesine karşı sınanmadan inmez |
| **Ö12** | *"Ölçü→ölçü **etki/ilişki** niyeti"* | 🔴 **İKİYE BÖLÜNÜR.** Chip yarısı (*"ilişki mi, iki ayrı seri mi?"*) → **bu faz** (G6'nın netleştirmesi). Analiz yarısı (ilişki/korelasyon hesabı) → **v2 · II-D**, ve §8'in çoklu-karşılaştırma gerekçesiyle **bu fazda kapalı** |

**ADIMLAR** — *🔴 önce KAPI, sonra KAPSAM — tersi sessiz-yanlış üretir*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G6.1** ✅ | 🔴 **ÖNCE KAPI** | İki adlandırılmış dönem + kıyas fiili **aralık toplamına çökemez**. `uyum.py`'nin `kiyas`+`cok_donem` değişmezleri **temsil edilebilir** hâle gelir | `mart cirosunu şubat ile kıyasla` → **tek birleşik sayı DÖNMÜYOR** |
| **G6.2** ✅ | Eşdeğerlik önce ölçülür *(Faz 2 deseni)* | `yoy`/`mom` → `referans`'a çevrildikten sonra **birebir aynı SQL** | SQL diff **boş** |
| **G6.3** ✅ | Alan | `CubeQuery.referans: {eksen, kaynak, hedef}`; `eksen ∈ {dönem, kohort, hedef, bütçe, sabit}` | `parse_cube_query` beyaz listesinde |
| **G6.4** ✅ | 🔴 **Taşıyıcı `Niyet`** | `referans` bilgisi `app/niyet.py`'de doğar *(`KÇ-0`'ın müşterisi)*; ikinci sahip **yok** | AST kapısı: tek temsil |
| **G6.5** ✅ | Intent-JSON şeması | `intent_semasi.py` → **`compare` VE `blend`** girer. `oneOf` **korunur** *(§7.4/(c))* | Şema testi |
| **G6.6** ✅ | `Ö9` — adlandırılmış dönem | `mart cirosunu şubata göre` → **iki seri + %değişim** | Denetimin kabul ölçütü |
| **G6.7** ✅ | `Ö11` — `blend` | `verimlilik ve ciro` → iki seri **ya da** netleştirme; **R1 değil** | Denetimin kabul ölçütü |
| **G6.8** ✅ | `Ö12` chip yarısı | *"ilişki mi, iki ayrı seri mi?"* netleştirmesi | Chip `route()` ile **doğrulanmış** |
| **G6.9** ✅ | `R11` | Yeni red kodu — *"anlaşıldı ama İFADE EDİLEMEZ"*. **Kapalıyken de sayılır** | `R1..R11` |
| **G6.10** ✅ | Göç | `compare`'ın 7 dokunuşu `referans`'a; eski `compare` bir süre **kabul edilir** *(deprecation)* | Eski çağrılar çalışıyor |
| **G6.11** ✅ | Sağlayıcı görünürlüğü | Failover Anthropic'ten düşünce şema garantisinin kaybolduğu **makbuza yazılır** *(§7.4)* | Makbuzda alan |
| **G6.12** ✅ | Ön yüz | Kıyas chip'leri **tek şablondan** *(bugün `yoy` için özel dal var — o dal silinir)* | Özel dal yok |
| **G6.13** ✅ | 🔴 Gerileme | `nl_corpus --kapi` doğru-cube **gerilemedi** | Kayıtlı |
| **G6.14** ✅ | 📌 **COMMIT** | `feat(G6): referans cebiri — LLM kıyası SÖYLEYEBİLİYOR` · `MIMARI.md` **§13.6/5** · 🔴 **v1'in `5.6`'sı açılır** | `B-G4` kapandı |

---

### G7 · TÜRKÇE EK MOTORU *(paralel yürür)*

**NEDEN.** Hem şablon hem LLM çıktısı Türkçe eklerde tökezliyor. Ve ölçülmüş: LLM'ler
Türkçe **türetimsel bileşimsellikte** zayıf (GPT-4 %54,2/%43,9 · insan %97,1/%95,0). ⚠ Ama
dürüstlük gerektiren nokta: bu **en zor uçtur**; BI'da asıl gereken *"bilinen bir ada hâl
eki"*dir ve o **hiçbir kıyasla ölçülmemiştir**.

**NE.** `app/ek.py::ek_bagla(sozcuk, ek_tipi, *, sayi=None) -> str`
Kapsam **kapalı ve küçük**: anlatıcının enjekte ettiği dört şey — *metrik adı · boyut değeri
· sayı · tarih*.

**NASIL.** 🔴 **Zemberek ALINMAZ.** Üç ayrı risk: (a) son sürüm **Temmuz 2019**, README
*"slow maintenance mode"*; (b) sağlıklı Python bağlayıcısı yok → **JVM taşımak** gerekir;
(c) `pip install zeyrek` **ağ ister**, CI `--network none` (`MIMARI.md:1929`). Ve
google-research'ün FST'si **19 Nisan 2026'da arşivlendi** — kurumsal ilgi çekiliyor.

Yerine **dört parçalı deterministik fonksiyon**:
1. **Ünlü uyumu** (kalın/ince, düz/yuvarlak) — kapalı kural
2. **Ünsüz yumuşaması/sertleşmesi** — kapalı kural
3. 🔴 **Sayı → okunuş tablosu** — çünkü ek **okunuşa** göre değişir: `3'te` (*üç*),
   `1.000.000'a` (*milyon*). ⚠ *"Son harfe bakar"* önerisi **yanlıştır** (§9/L-2)
4. **İstisna sözlüğü** — TDK'nın belgelediği kapalı liste (`saat→saati`, `kitap→kitabı`)

**KAPI.** `tests/test_ek_motoru.py`:
- Bir **test korpusu**: katalogdaki tüm metrik/boyut adları × beş ek tipi, beklenen çıktı.
- Sayı okunuş vakaları (`3'te` · `1.000.000'a` · `%12'ye` · `2026'da`).
- İstisna kelimeleri.
- 🔴 **Kapsam kilidi:** fonksiyon yalnız dört kapalı sınıfa uygulanır; serbest metne
  **uygulanmaz** (AST kapısı). *Serbest Türkçe bu motorun işi değildir.*

**GERİ AL.** Fonksiyon çağrılmaz, bugünkü çıktı. Bayrak gerekmez.

**BÜYÜKLÜK.** Küçük · bağımlılık: **yok** *(paralel yürür)* · deterministik; hem şablonu
hem LLM çıktısını temizler.

**ADIMLAR** — *kapalı alan, kapalı kural, kapalı liste*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G7.1** ✅ | Kapsamı **yaz ve kilitle** | Yalnız dört sınıf: *metrik adı · boyut değeri · sayı · tarih*. **Serbest metne uygulanmaz** | AST kapısı: çağrı yerleri sayılı |
| **G7.2** ✅ | Ünlü uyumu | 🔴 **`cube_router._ek_gecerli` TEK SAHİPTİR** (`:216` — *"Karar `_ek_gecerli`nin (tek sahip)"*). O **doğrulama** yapıyor, `ek.py` **üretim**; ama **kural tablosu ORTAK olmalı** — ikinci bir ünlü-uyumu tablosu KAT-1 ihlali | Tek tablo, iki tüketici |
| **G7.3** ✅ | Ünsüz yumuşaması/sertleşmesi | aynı modül | Test matrisi |
| **G7.4** ✅ | 🔴 **Sayı → okunuş tablosu** | `3'te` ← *üç* · `1.000.000'a` ← *milyon* · `%12'ye` · `2026'da`. ⚠ *"Son harfe bakar"* **yanlıştır** (§9/L-2) | 4 vaka yeşil |
| **G7.5** ✅ | İstisna sözlüğü | TDK'nın belgelediği **kapalı** liste (`saat→saati` · `kitap→kitabı`) | Liste kapalı, gerekçeli |
| **G7.6** ✅ | Test korpusu | Katalogdaki **tüm** metrik/boyut adları × beş ek tipi | Üretilmiş beklenen çıktı |
| **G7.7** ✅ | Zemberek **alınmadı** kaydı | Üç gerekçe *(2019 sürümü · JVM · `--network none`)* + google-research arşivi **2026-04-19** | `MIMARI.md`'de ADR notu |
| **G7.7b** ✅ | 🖥 **ÖN YÜZ — bilinçli olarak YOK** | Ek motoru **metin biçimlendirir**; çıktı mevcut `OutputInsight`/`ReportCard` yolundan geçer. 🔴 Gerekçe **yazılır** ki *"unutuldu"* sanılmasın | Kayıt `MIMARI.md`'de |
| **G7.8** ✅ | 📌 **COMMIT** | `feat(G7): Türkçe ek motoru — enjekte edilen yuvalar doğru çekimleniyor` | |

---

### G8 · MENÜ — kapasite beyanı

**NEDEN.** dbt'nin bulgusu DİMA'nın en büyük avantajı: *"semantik katmanda başarısızlık bir
hata mesajıdır"*. Ama bugün o hata mesajı **kapıyı kapatıyor**, bir sonraki adımı
göstermiyor. Ve Cortex Analyst'in belgelenmiş sınırı (*"geniş iş sorularına içgörü
üretmez"*) tam da DİMA'nın `interpret.py` ile aşabildiği yer.

> 🔴 **DÜZELTME (2026-08-07, kod denetimi):** ilk taslak *"yeni `kapasite` alanı"* diyordu.
> **Yarısı zaten var:** `app/yetenek.py` (KÖK-6, *"YETENEK BEYANI: üç kutu, iki değil"*)
> `kapsam_disi(q, schema) -> Sinir` üretiyor ve **bağlı** (`ask.py:3554-3555`).
> Sahip **odur**; ikinci bir alan sahibi doğurmak KAT-1 ihlali olurdu.

**NE.** 🔴 **`yetenek.py` GENİŞLETİLİR — yeni sahip YAZILMAZ.**

| | Bugün | `G8`'den sonra |
|---|---|---|
| **Sınırı tanıma** | ✅ `kapsam_disi()` — forecast · olumsuzluk · iki-cube ölçüsü | aynen |
| **"Yapamam" demek** | ✅ `Sinir.mesaj` + `trace` (`yanit_alanlari`) | aynen |
| 🔴 **"Ama şunu yapabilirim"** | ❌ **YOK** — `yanit_alanlari` yalnız `note`+`trace` döndürüyor | ✅ `Sinir`'e **üç alan**: `yakin_olculer[]` · `mevcut_kirilimlar[]` · `onerilen_soru` |
| **Discovery'ye düşmeyi kesme** | ✅ zaten kesiyor | aynen |

· Kaynağı **katalog** — LLM değil.
· ⚠ **G4'ten geçer:** öneri bir **yetenek iddiasıdır**; `iddia.py` onu denetler.

**NASIL.** Katalog listesi zaten var (`ask.py:617,658` meta/katalog yolu) ve `yetenek.py`
zaten kataloğu okuyor (`_katalog_terimleri`). Bu madde `Sinir`'i **zenginleştirir** ve
mesajı **reaktiften proaktife** çevirir — *yeni motor değil, var olan kapının ikinci yarısı*.

⚠ **Ve `yetenek.py`'nin kendi disiplini korunur:** `_FORECAST` sözlüğü *"kapalı, belgeli"*
ve dosyanın kendi notu açık — *"bu liste «Türkçede gelecek nasıl anlatılır» sorusunu
cevaplamaya çalışmıyor; ADR-0008 tam olarak onu yasaklar"*. **Yeni kelime eklenmez.**

**KAPI.** `tests/test_kapasite_beyani.py`:
- Ret cevabında alan **dolu**.
- Önerilen her ölçü/kırılım **katalogda var** (`iddia.py` üzerinden — fail-closed).
- Önerilen soru `route()` ile **doğrulanır** — *"aynı duvara ikinci kez çarptıran chip, chip
  olmamasından kötüdür"* (`ask.py:428` deseninin tekrarı).
- `lab/garson.py` §5/8 **yeşil**.

**GERİ AL.** Alan `None`. Bayrak gerekmez.

**BÜYÜKLÜK.** Küçük · bağımlılık: 🔴 **`G4`** *(kapasite beyanı bir yetenek iddiasıdır)*.

**ADIMLAR** — *denetimin `KÇ-7`'si: "anlamadım" ≠ "yapamıyorum"*

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **G8.1** ✅ | İki ret sınıfını **ayır** | *"anlamadım"* (dil) ↔ *"yapamıyorum"* (katalog). `teshis()` + `Niyet.bilinmeyenler` zaten ayrımı **taşıyor** — kullanılmıyor | Ret kodu sınıfa eşleniyor |
| **G8.2** ✅ | Alan | `schemas.py:306` → `kapasite: dict \| None` `{yakin_olculer[], mevcut_kirilimlar[], onerilen_soru}` | `openapi.json` |
| **G8.3** ✅ | Kaynak **katalog** | `ask.py:617,658`'in meta/katalog yolu **çağrılır**; LLM **yok** | 0 token |
| **G8.4** ✅ | 🔴 **`iddia.py`'den geçer** | Kapasite beyanı bir **yetenek iddiasıdır** — G4 onu denetler | Olmayan boyut **önerilemiyor** |
| **G8.5** ✅ | Öneri `route()` ile doğrulanır | `ask.py:428 _dogrulanmis_chipler` deseni — *"aynı duvara ikinci kez çarptıran chip, chip olmamasından kötüdür"* | Doğrulanmamış öneri **çıkmıyor** |
| **G8.6** ✅ | Ön yüz | Ret kartında, `soz ?? note`'un (`ReportCard.tsx:643`) altında | Yeni panel **yok** |
| **G8.7** ✅ | Kapı testi | **yeni** `tests/test_kapasite_beyani.py` — 4 değişmez | Yeşil |
| **G8.8** ✅ | 📌 **COMMIT** | `feat(G8): kapasite beyanı — yapamadığını söylerken YAPABİLDİĞİNİ de söylüyor` | `B-G6` kapandı · §5/8 yeşil |

---

### ⏭ FAZ KAPANIŞI — dokuz adım bittiğinde

| # | Adım | ✅ | **KOŞULDU (2026-08-07)** |
|---|---|---|---|
| **Z.1** | `lab/kapi.py --hepsi` **bir kez** *(gecelik değil, kapanış turu)* | 4:06 | ✅ koşuldu · **9 kırmızı / 4045 yeşil** (6:43) → dokuzu da o turun kendi eksiğiydi, **hepsi kapandı** (`615f990`) |
| **Z.2** | `lab/garson.py --live` **iki koşum** — sekiz satırın tamamı | Taban raporu | ✅ **beş koşum** *(alet düzeltildikten sonra üçü)* · `KURAL G-1` sağlandı · taban donduruldu |
| **Z.3** | `MIMARI.md`'nin beş zorunlu kaydı **tam** *(§13.6)* | §5 ↔ `:442` çelişkisi **yok** | ◐ altı kaydın **altısı** yazıldı ama **hiçbiri kendi commit'inde değil** → `§13.6` ihlali kayıtlı |
| **Z.4** | `OPERASYON-DURUM.md` — altı borç (`B-G1…B-G6`) **kapalı** | Güncel | ◐ **beşi kapandı**, `B-G4` **yarım** (`compare` hâlâ enum, `blend` yok) |
| **Z.5** | 🔴 **v2 kapısı:** `5.6` açıldı mı (G6) · `3.0` tenant açılışı başladı mı (§10/W2) | §10 tablosu | 🔴 **`5.6` AÇILMADI** — ilk beyan fazla iddialıydı, düzeltildi |
| **Z.6** | Push + üç denetim ajanı *(`OPERASYON.md §7`)* | A plan · B bütünlük · C canlı kullanıcı | ✅ üçü koştu · **13 bulgu**, biri yanlış çıktı (`DA-6`) |
| 🔴 **Z.7** | *(yeni)* Denetim bulgularının kapatılması | — | ✅ `DA-1…DA-10`'un **dokuzu kapandı**, `DA-6` **reddedildi** |

---

## §6.Ω · KAPANIŞ SONRASI — DENETİM TURU VE AÇIK HARİTA *(2026-08-07)*

> 🔴 **Bu bölüm fazın kapanışından SONRA eklendi.** Sebebi: üç denetim ajanı + bir dış
> danışman değerlendirmesi, fazın bittiği noktada **yeni bir yapılacaklar haritası**
> doğurdu. Kaynak belgeler **kopyalanmadı** (`D1`): tam gerekçeler
> `DIKKAT-EDILECEKLER.md` (repo kökü) ve `OPERASYON.md §10b/§10c`'de; buraya giren
> **harita** — ne yapıldı, ne kaldı.

### (a) ✅ YAPILDI — denetim turu

| # | Ne | Kanıt |
|---|---|---|
| `DA-1` | `app/ek.py` (G7) üretimde **sıfır çağıranı** vardı → `yayilim.geri_koy`'a bağlandı; `ek_bagla(kesme=True)` özel ad kipi (TDK) eklendi | 3 ajan da bağımsız buldu |
| `DA-2` | Ölçüm aleti **10 satırın 4'ünü** hiç ölçmüyordu (`2·anlat` dâhil — anlatıcının kendi satırı) → iki senaryo + *kör satır* **kırmızı test** | taban donduruldu, 3 koşum aynı |
| `DA-3` | `raporlanabilir()` **totolojiydi** (`kanit_sinifi` her cevapta dolu) → kapandı; altından `soz` çıktı | netleştirme/ret artık saf-not dalında |
| `DA-4` | `narration_guard.Rapor.makbuza()` **çağransızdı** → makbuza bağlandı, muafiyetler adlandırıldı | `G5.4`'ün sözü tutuldu |
| `DA-5` | `G2`'nin **kill-switch'i yoktu** → `diyalog_bellegi` bayrağı, tek noktada | ⚠ ilk yazımda YAML **boolean** tuzağına düştü |
| `DA-6` | *"`== 11` cırcırı ters"* | ⊘ **BULGU YANLIŞ — reddedildi** (meta-kapı deseni doğru) |
| `DA-7` | `temellendirme.cube` üretiliyordu, **çizilmiyordu** → ilk rozet + `flex-wrap` | `WRONG_SCOPE` %14,4 |
| `DA-8` | Backend `**kalın**` yazıyor, ekranda yorumlayıcı **yoktu** → `lib/vurgu.tsx` | kütüphane DEĞİL (enjeksiyon yüzeyi) |
| `DA-9` | Kıyas chip'i `mom`'u yok saymıyor, **BOZUYORDU** → kipe duyarlı | `G6`'nın kendi çıktısı |
| `DA-10` | `netlestirme.donem` katalog metni **ölü koddu** → bağlandı | netleştirmelerin **%79'u** |
| 🔴 `G2` teli | `AskRequest.diyalog_durumu` istemcide **yoktu** → `KURAL_DEVAM` üretimde **hiç ateşlenmedi** | + yetim kapısı sertleştirildi (`test_K2c`) |
| 🔴 `tsc` | Frontend `G1`'den beri **derlenmiyordu** (4 hata) | + `test_frontend_derlenir.py` |
| `B5` | `oneOf` şeması üretilip **atılıyordu** (~10k token) → sağlayıcı yeteneğini kendi beyan ediyor | `sema_kullanir` |
| `Ö5` | Guard **düşme oranı** hiç ölçülmüyordu → `app/guard_alarmi.py` (📊 telemetri) + `/health/ready` | kapının kendi sözü tutuldu |
| 🔴 `G8` kapısı | `test_kapasite_beyani.py`'nin **fikstürü bozuktu** (`dimensions` sözlük listesi) → `onerileri_kur` **boş** dönüyordu ve **altı test de yeşildi** | `test_ONERI_URETILIYOR_MU_hic` |
| 🔴 `G0.12` | `2·anlat` **ayırt edici değildi** (`narration or summary`) → alet artık **anlatı kaynağını** ayrı basıyor | `t2` kapalıyken `narration=0` |
| 🔴 `eval` LLM | `--slice llm` **vardı, hiçbir kapı koşmuyordu** → `--sadece eval_llm` adımı + yetim kapısı | varsayılan yolun tek kancası |
| kendi testim | `test_KIYAS_CEVABI_ARTIK_ETIKETSIZ_GITMIYOR` **hiç iddia koşmadan** yeşil geçebiliyordu | `olculen` sayacı |

### (b) 🔴 YAPILACAK — sıra ve sahibi

| # | Ne | Nerede yazılı | Ağırlık |
|---|---|---|---|
| ⊘ `B1·B3` | **Şema budaması ASKIYA ALINDI** — doğru nüfusta ölçüldü ve tasarım **çöktü**: birleşim `ilgili_cubelar`'a düşüyor, recall **%78,1 · 464 KAYIP** *(n=2 116)*. Fail-open kurtarmıyor: kayıp **dolu ama yanlış** seçimden geliyor | `OPERASYON.md §10b` | 🔴 yeni sinyal gerekiyor |
| ◐ `B2` | ~~*"~100 vaka üretilmeli, bugün 2"*~~ → **YANLIŞTI.** Etiketli + `route()=None` **2 116** vaka **zaten var** (`senaryo_uretec.py:863` her soruya kaynak cube'unu yazıyor). İş **üretmek değil AYIKLAMAK**: üreteç `kabul` beklentisi de taşıyor, bazı vakalarda doğru cevap **netleştirmedir**. ⚠ Ayrıca `lab/nl_accuracy.py:354` `ab_kurtarma_kos()` zaten LLM'i yer gerçeğiyle ölçüyor — **genişletilir, yeniden yazılmaz** | aynı | 🔴 yüksek |
| `B6` | Prompt caching — üç katmanlı önek | aynı | orta |
| `Ö5` | **Guard düşme oranı alarmı** — agrege ölçüm hiç yok | `OPERASYON.md §10c` | 🔴 yüksek |
| ⊘ `Ö2` | ~~Çok-turlu bozulma sahipsiz~~ → **BULGU BAYAT.** Borç ölçülüp kapanmış: **−%18,2 → −%4,5**, bayrak `olcu_ekleme_takibi` `beta` (`OPERASYON-DURUM.md:112`). Ajan `cube_router` docstring'ini okumuş, kapanış kaydını görmemiş | — | ✅ kapalı |
| `Ö1` | Akış inerse **cümle-tamponlu** olmak zorunda | aynı | kısıt *(faz `S`)* |
| `Ö3` | Eksen 1 p95 > 1,5 sn ise `openrouter_select_model` | aynı | env işi |
| `B-G4` | `compare` **enum→ALAN** + `blend` → `5.6` hâlâ **BLOKE** | `OPERASYON-DURUM.md` | orta |
| `S2·S4·S5·S6·S7` | Kayıtsız sapmalar *(en ağırı `S5`: `{{ENT_i}}` varlık perdesi inmedi)* | aynı | orta |
| `P1·P3·P4·P5·P6` | Planın kendi eksikleri *(en ağırı `P3`: budamadan hiç söz etmiyor; `P5`: `viz` dışı grafik türleri)* | aynı | orta |
| 🔴 `tsc` | **Gecelik CI'da HİÇ koşmuyor** — `backend-ci.yml`/`nightly.yml`'de node adımı yok, dolayısıyla `test_TSC_TEMIZ` **her zaman** atlanıyor. `K3`'ün açık borcu | `DIKKAT-EDILECEKLER.md §5` | 🔴 yüksek |
| ⚠ `diyalog.py` | Fazın en büyük yeni katmanının `MIMARI` kaydı **yok** | aynı | orta |
| ⚠ iz | `Niyet.temsil_edilemeyen` indirgemeden habersiz — iz yanıltıcı | aynı | düşük |
| ⚠ `kapasite` | 🔴 **PLAN KENDİ İÇİNDE ÇELİŞİYOR:** `§13.5b` *"üç yeni alan kapıya bağlanır: … `kapasite`"* ⟷ `§13.5c/G8.2` *"üçüncü kanal açma"*. Kod ikincisini seçti ve **testle kilitledi** (`test_kapasite_beyani.py`: `assert "kapasite" not in alanlar`); ama `lab/garson.py` hâlâ `d.get("kapasite")` okuyor — **ölü dal**. Planın bir yarısı bir alanı şart koşarken öteki yarısı yasaklıyor | denetim bulgusu | orta |

### (c) 🔴 BU FAZIN EN DÜRÜST ÖZ-ELEŞTİRİSİ — ÖLÇÜM AĞIRLIK MERKEZİ YANLIŞ YERDE

Bu belgenin `:208`'i şöyle diyor: ***"`route()` artık varsayılan değil, ispatlı
istisnadır."*** Yani niyet çevirisinin **asıl sahibi LLM**'dir; deterministik yol yalnız
**ispatlanmış** olduğu yerde çalışır.

🔴 **Ama bu fazda koşulan her kapı `route()`'u ölçtü.** Korpus `dogru_cube`, `sessiz_yanlis`,
`gercek_dunya` — üçü de **deterministik yolun** metriği. `CLAUDE.md` bunu zaten itiraf
ediyor: *"korpus `route()`u ölçer, Discovery'yi değil."*

Sonuç: **varsayılan yolu (LLM) neredeyse hiç ölçmüyoruz.** Ve bu, budama tasarımında
somut bir sayıya dönüştü: budama yalnız `route()` **pes ettiğinde** önemlidir, ama o
nüfusta elimizde **2 etiketli vaka** var.

*Bir mimaride varsayılan olan yol, en az ölçülen yol olmamalıdır — yoksa ölçüm sistemi,
sistemin kendisinden farklı bir şeye inanmaya başlar.*

→ Bu yüzden `B2` (etiketli route-başarısızlık korpusu) bir **budama ön koşulu değil**,
bağımsız bir **ölçüm borcudur**: LLM yolunun ilk gerçek metriği o olacak.

---

## §7 · ÇAPRAZ KESEN — MALİYET, GECİKME, SAĞLAYICI

### 7.1 · Prompt caching — ve danışman belgesinin fark etmediği çelişki

Dört sağlayıcı da **~%90 indirim** ve **~1024 token asgari önek** üzerinde birleşti.
Anthropic somut: 5 dk TTL yazma **1,25×**, okuma **0,1×** → **bir okumada** başabaş;
1 saat TTL yazma **2×** → **iki okumada** başabaş.

🔴 **Ama danışman belgesinin iki tekniği birbirini yiyor** (§9/Ç-8): "şema budama" her
sorguda **farklı** küp şeması enjekte ediyor; prompt caching **sabit önek** istiyor. İkisi
"4 kaldıraç" diye **toplanarak** sunuluyor; gerçekte kısmen birbirini iptal ediyorlar.

**Karar — üç katmanlı önek:**
```
[SABİT · cache'lenir]   sistem kuralları · söz katalogu · çıktı sözleşmesi
[YARI-SABİT · cache'lenir] tenant kataloğu (mdl özeti) — tenant başına, gün boyu sabit
[DEĞİŞKEN · cache'lenmez]  soru + bağlam + fact-sheet
```
Budama **değişken** katmanda yapılır, yarı-sabit katman **budanmaz**. Böylece cache isabeti
korunur.

### 7.2 · Gecikme bütçesi

⚠ Danışman belgesinin gecikme rakamları **kendi içinde tutarsız** (§9/Ç-5) ve hiçbirinin
ölçüm kaynağı yok. Bu belge **rakam vermiyor, bütçe koyuyor**:

| Yol | Bütçe | Nasıl tutulur |
|---|---|---|
| Küp yolu (garson yalnız temellendirir + anlatır) | **p50 ≤ bugünkü + anlatıcı TTFT** | Anlatı **akışlı** verilir; tablo/grafik **önce** çizilir |
| Intent yolu | **p95 ≤ 3 sn** | Ucuz model + caching + `consistency_k` gözden geçirilir |
| Discovery | bütçesiz (son çare) | Kullanıcı `yol_siniri` ile kapatabilir |

🔴 **Ve algılanan gecikmeyi düşüren tek gerçek kaldıraç kodda hazır ve kapalı:** SSE hattı
tam yazılmış (`ask.py:3864` + `api-client.ts:306`), `ask_async_discovery: off` olduğu için
hiç tetiklenmiyor — ve tetiklense bile yalnız **iz adımı** taşıyor, **metin akmıyor**.
Anlatının token token akması bu fazın **kolay kazancıdır**; G5'ten sonra sıraya alınır.

⚠ **Ajanik maliyet uyarısı:** ajanlar tur başına **5–30×** token yakıyor; pilotlar üretim
faturasının **%15–25'inde** koşuyor. Bu faz **ajan açmıyor** (§8) — bu uyarı v2 içindir.

### 7.3 · Yapısal çıktı — garantinin sınırı

Anthropic açık: *"gramer-kısıtlı örnekleme"*, şema uyumu **garanti**. Ama:
🔴 **Kısıtlı çözümleme bir ayrıştırma-hatası yok edicidir, bir halüsinasyon yok edicisi
değildir.** JSON kusursuz geçerli olup **yanlış küp** seçebilir. Danışman belgesi bunu
*"%0 halüsinasyon"* diye satıyor (§9/Ç-6) — kategori hatası.

### 7.4 · 🔴 SAĞLAYICI KARARI — OpenRouter + NVIDIA açık kaynak model

> **Karar (kullanıcı, 2026-08-07):** garsonun LLM'i **OpenRouter üzerinden bir NVIDIA açık
> kaynak modeli** olacaktır.

Bu karar bir yapılandırma ayrıntısı değil; **belgedeki bir garantiyi iptal ediyor** ve
kodda doğrulandı.

**Zincir — üç adımda, hepsi okundu:**

| # | Bulgu | Kanıt |
|---|---|---|
| 1 | `openrouter` sağlayıcısı **`OpenAICompatibleSqlGenerator`**'a gider | `llm.py:1244-1248` |
| 2 | O sınıfın `select_cube`'ü şemayı **bilerek kullanmaz** | `llm.py` — docstring birebir: *"`sema` KABUL EDİLİR ama BU SAĞLAYICIDA KULLANILMAZ (bilinçli). OpenAI-uyumlu uçların `strict` fonksiyon şeması **`oneOf`'u desteklemiyor**; kısıtı yarım uygulamak, uygulamamaktan **kötüdür**"* |
| 3 | Intent şeması **tümüyle `oneOf` üzerine kurulu** | `intent_semasi.py:101` → `{"type":"object","oneOf": dallar}`; `:73` → `"cube": {"const": ad}`; `:40` gerekçe: *"her cube kendi dalını taşır"* |

🔴 **Sonuç: `llm_sema_kisitli` bayrağı, seçilen sağlayıcıda kalıcı bir NO-OP'tur.**
Bayrak `beta` (açık) görünüyor, ama etkisi **sıfır**. Bir bayrağın açık görünüp hiçbir şey
yapmaması, bu deponun *"ölü kontrol"* sınıfıdır (`mod` anahtarı gibi — §4.5) ve **görünür
kılınmalıdır**.

#### Ne KAYBEDİLİYOR — ve dürüst boyutu

⚠ **Kaybedilen şey bir GÜVENLİK garantisi değil, bir MALİYET garantisidir.** Sebebi
kodda: gerçek emniyet ağı `parse_cube_query`'nin **katı beyaz listesidir** ve o
**sağlayıcıdan bağımsızdır**. Model uydurma bir ölçü adı üretebilir; sistem onu
**çalıştıramaz**.

| | Şema kısıtı VARKEN | Şema kısıtı YOKKEN |
|---|---|---|
| Model geçersiz ad üretebilir mi? | ❌ hayır (token seviyesinde engel) | ✅ evet |
| Sistem geçersiz adı **çalıştırır** mı? | ❌ hayır | ❌ **hayır** — `parse_cube_query` reddeder |
| Bedeli | — | **red oranı + tekrar denemesi + gecikme** |

→ **Doğruluk vetosu (§2.3) etkilenmiyor.** Etkilenen şey `G5`/`G6`'nın **fiyat kalemidir**.

#### Karar — üç seçenek ölçüldü, biri seçildi

| Seçenek | Yargı |
|---|---|
| (a) Şemayı `oneOf`'tan **düzleştir** (`cube` bir enum, ölçü/boyut serbest dizi) | ❌ **Reddedildi.** Küp-başına kısıt üretim anında kaybolur; `intent_semasi.py:40`'ın gerekçesi tam da bunu önlüyor. Kazanç yok, şema zayıflar |
| (b) **İki çağrı** (önce küp, sonra o küpün düz şeması) | ❌ **Reddedildi.** İki LLM çağrısı — danışman belgesinin kendi *"çift çağrı tuzağı"* argümanı burada geçerli (§9/P-1) |
| (c) 🟢 **`oneOf` korunur; serbest-JSON + `parse_cube_query` + HATA GERİ BESLEMELİ tekrar** | ✅ **SEÇİLDİ.** WrenAI'ın *"structured errors with hints"* deseni. Red oranı **ölçülür**; yüksekse tekrar denemesi eklenir, düşükse hiçbir şey yapılmaz |

🔴 **Ve bu bir varsayım değil, bir ÖLÇÜM maddesidir → `G0`'a eklenir:**
> `lab/garson.py --live` ilk koşumunda **şema-dışı çıktı oranı** raporlanır
> (`parse_cube_query`'nin reddettiği Intent-JSON yüzdesi). Bu sayı bilinmeden (c)'nin
> tekrar-denemesi yazılmaz. *Ölçülmemiş bir kusura çözüm yazmak bu deponun yasak listesinde.*

#### Diğer üç sonuç

1. **Failover sırası.** `llm.py:1295`: `anthropic → gemini → groq → xai → openrouter → ollama`
   — OpenRouter **beşinci**. Karar gereği ya `DIMA_LLM_PROVIDER=openrouter` **açıkça**
   ayarlanır (failover atlanır) ya sıra **başa alınır**. 🔴 **Karar yazılmadan `G0` koşulamaz**
   — yoksa ölçüm hangi modelle yapıldığı belirsiz olur (bu turun `rule`-sağlayıcı hatasının
   tekrarı olurdu).
2. **Model adı yapılandırmada.** `config.py:95` bugün `openrouter_model = "openai/gpt-oss-120b"`.
   NVIDIA modeline geçiş bir **env değişikliğidir**, kod değişikliği değil
   (`openrouter_model` + `openrouter_select_model`).
3. 🔴 **KARAR (kullanıcı, 2026-08-07): TEK MODEL.** `DIMA_OPENROUTER_SELECT_MODEL` **boş
bırakılır** — `llm.py:365` `select_model or model` gereği Intent-JSON de aynı modele gider.
*Gerekçe: iki modelli kurulum ölçümü kirletirdi — hangi katmanın hangi modelden geldiği
karışırdı. Tek model, tek değişken.* ⚠ Bedeli **gecikme**: 550B model sıcak yolda.
`G0` bunu **ölçecek**, varsaymayacak; §7.2'nin bütçesi bu yüzden rakam değil **bütçedir**.

⚠ **Prompt caching VARSAYILMAZ.** §7.1'in *"~%90 indirim, dört sağlayıcıda birleşti"*
   bulgusu **birinci taraf uçlar** içindir. OpenRouter bir **aracıdır**; önbellek davranışı
   alttaki sunucuya bağlıdır ve açık kaynak modellerde çoğu zaman **yoktur**.
   → §7.1'in üç katmanlı öneki **yine de doğru tasarımdır** (cache olmasa da token'ı azaltır),
   ama **indirim rakamı bu sağlayıcıda ölçülene kadar sıfır sayılır**.

---

## §8 · KAPSAM DIŞI — VE GEREKÇESİ

| Ne | Neden bu fazda değil |
|---|---|
| **Yerel BERT/DeBERTa niyet sınıflandırıcı** | **Etiketli eğitim verisi** ister; danışman belgesi bunun nereden geleceğini, kaç örnek gerektiğini, kim etiketleyeceğini, yeni metrik eklendiğinde nasıl yeniden eğitileceğini **hiç konuşmuyor**. *"0 TL"* muhasebesi yanlış. Ve sabit bir niyet enum'u, AJ2'nin **cebirsel açıklık** hedefiyle ters yönde çalışır |
| **30 varyasyonlu şablon NLG (Tracery/SimpleNLG)** | 🔴 **Kullanıcının kaçmak istediği duygunun ta kendisi.** 30 cümle ezberlemiş bir robot, hâlâ bir robottur. Bakım maliyeti *"$0.00"* sayılıyor — 30 varyasyon × her olgu tipi × Türkçe ek uyumu elle yazılacak. Ve belge kendi tablosunda LLM'siz yapıya *"insani esneklik: çok yüksek"* verip iki soru sonra *"pes eder"* diyor (§9/Ç-4) |
| **Karar motoru** (maaş · fiyatlama · Weibull · TCO · Adalet Süzgeci) | v3. Ve `◆ FAIRNESS VERIFIED` rozeti istatistiksel ve hukuki olarak **savunulamaz**; ayrıca cinsiyet/yaş analizi **özel nitelikli veri** işlemeyi gerektirir ve belgenin kendi PII bölümüyle çatışır (§9/Ç-27) |
| **What-if / simülasyon** | v2 (II-D.3). Ve *"bütçe %20 → satış +%12"* bir **ekonometrik tahmindir**, deterministik hesap değil; güven aralığı olmadan SHA-256 mührüyle sunmak, LLM halüsinasyonundan **daha tehlikelidir** (§9/Ç-22) |
| **DoWhy / nedensellik** | v3. Gözlemsel BI verisinden nedensellik *"kanıt"* diye sunulamaz; DAG ve karıştırıcı varsayımları belgede hiç anılmıyor (§9/Ç-23) |
| **Anonimleştirme proxy** *(danışmanın soyutlama biçimi)* | v3 — mevcut tasarımıyla `narration_guard` ile **karşılıklı imkânsız** (§9/Ç-24). 🔴 **AMA hedefi `G0b` ile ULAŞILDI:** *korunan yayılım* gerçek değeri dışarı çıkarmıyor **ve** guard'ı yapısal olarak güçlendiriyor. Reddedilen **yöntemdi**, gereksinim değil |
| **Otomatik korelasyon taraması** (`r>0,70` → *"güçlü ilişki"*) | 🔴 **Çoklu karşılaştırma düzeltmesi yok** → ölçekte **garantili sahte keşif**. Halüsinasyonu ölümcül günah ilan edip deterministik yola bir yanlış-keşif makinesi koymak olur (§9/Ç-17) |
| **Ajan yazma yetkisi** (panoya ekle · her pazartesi yolla) | `tools.py:26-29` değişmezi. Kademelendirilebilir ama **onay akışı** (6.1) ile — v2 |
| **AJ5 / AJ5b / AJ6** (planlayıcı · adım zinciri · bileşik rapor) | Garson **konuşur**; çok adımlı rapor **v2**'dir. ⚠ Ama `agent_plan_secimi`'nin bloklayıcısı (`0.22`) **inmiş** — bayrağın gerekçesi bayat, **ölçülmeli** (Ş9) |

---

## §9 · DANIŞMAN BELGESİNİN DENETİMİ

> `dima v2 v3 için mimari karar (1).md` (2203 satır) tümüyle okundu. Fikirlerinin çoğu
> doğru; **ama belge kod tabanının bugünkü hâline değil, bir dönem önceki hâline yazılmış**
> ve iç tutarsızlıkları var. Bu bölüm, belgeyi **düz okuyan birinin alacağı yanlış bilgiyi**
> engellemek içindir.

### 9.1 · Bitmiş işi planlıyor

| Belge *"yapılacak"* diyor | Gerçek |
|---|---|
| `0.22` — `migration_trace` `UnboundLocalError` onarımı | **Yapılmış** — `ask.py:3148` |
| `0.23` — `ReportPanel.tsx` `it.result \|\| it.kpi` kapısı | **Yapılmış** — `ReportPanel.tsx:184` |
| VQR: `auto_cube` replay'den çıkarılsın | **Yapılmış 2026-08-03** — `vqr.py:159` |
| *"Rendering motorunu ECharts'a taşımak"* | **Zaten ECharts** — `EChart.tsx` |

**Sprint 1'inin yarısı ve Sprint 4'ün bir maddesi zaten kapalı.**

### 9.2 · Var olmayan modülleri var sayıyor

`iddia.py` · `diyalog.py` · `driver_graph.py` · `simulation.py` · `unit_splitter.py` ·
`base_100_index()` · `unit_type`/`multi_chart` — **hiçbiri yok**.
Ve 8 kez atıf yaptığı **`DIMA-V1-YOL-HARITASI.md` Sürüm 8** repoda bulunmuyor.
→ *"%70-80'i zaten kodlanmış"* **ölçülmüş bir oran değil, retorik bir rahatlatmadır.**

### 9.3 · On iki çelişki — kısa liste

| # | Çelişki |
|---|---|
| **Ç-1** | `narration_guard` toleransı dört yerde **±%2**, bir yerde **0,00**. Kodda `0.02`. 0,00 guard'ı **kullanılamaz** kılardı |
| **Ç-2** | *"LLM %100 garson kalır"* iddiası belgenin kendisi tarafından **beş kez** çiğneniyor (DAG böler · ECharts spec üretir · kampanya tasarlar · karar gerekçesi kurar · nedensellik hikâyeleştirir). Guard yalnız **sayıyı** denetler |
| **Ç-3** | *"%70-80 soru 0 token"* — deponun kendi §6.19z ölçümü **tersini** söylüyor: doğal ifadelerin **13/14'ünü Intent-JSON** cevaplıyor |
| **Ç-4** | LLM'siz mimariye *"insani esneklik: çok yüksek"* (satır 627), iki soru sonra *"pes eder"* (satır 648) |
| **Ç-5** | Gecikme aritmetiği tutmuyor: *"LLM en iyi 800ms-2sn"* ↔ *"Kademe 2 ~500ms"*; ve *"2-10 ms"* iddiası **DB sorgu süresini tamamen dışarıda bırakıyor** |
| **Ç-6** | *"%0 halüsinasyon / %100 kesinlik"* — belgenin kendi *"Yalancı Doğru"* bölümü (satır 1625) bunu **çürütüyor**: yerel NLP sahte %95 üretebiliyor |
| **Ç-7** | Aynı senaryoda iki farklı eğim: *"%5 → +%2,1"* ve *"%10 → +%3,2"*. Sayılar **üretilmiş** |
| **Ç-8** | Prompt caching ile şema budama **birbirini yiyor** (§7.1) |
| **Ç-9** | *"Kriptografik kanıt"* örneği `e3b0c442…` = **boş dizenin SHA-256'sı**. Ve hash **değişmezliği** mühürler, **doğruluğu** değil |
| **Ç-10** | ADR-0008 (*"kelime kelime yama yazılmayacak"*) **dokuz satır önce** ihlal ediliyor |
| **Ç-14** | `blend` teşhiste var, çözümde **sessizce düşüyor** — 3 alanlı referans tuple'ı çapraz-küp harmanını ifade edemez |
| **Ç-17** | Otomatik korelasyon taraması **çoklu karşılaştırma düzeltmesi olmadan** = garantili sahte keşif |
| 🔴 **Ç-29** | **EN AĞIR — ve yapılandırılmış çıkarımın KAÇIRDIĞI.** Belge, kullanıcının **satır 1'de koyduğu kısıtı satır 755'te çiğniyor**: kullanıcı *"maliyet hesabını **tamamen unut**"* + *"insani taraf **birinci seçenek**, fallback sadece küpler"* demişken, danışman 755'te *"LLM'i birinci seçenek yapmak … **intihardır**"* deyip **birincil gerekçe olarak maliyeti** gösteriyor. ⚠ Ve daha derini: cevap, LLM ile `route()`'un **aynı işi** yaptığını varsayıyor — §1.1e bunun yanlış olduğunu gösterdi. **Eksen 1'in cevabı, Eksen 2'nin sorusuna verilmiş.** *(Bu madde ancak KAYNAK okunarak bulundu; 28 maddelik çıkarımda yoktu — §15.1'in dersi.)* |

### 9.4 · Ve tek en ciddi kusur: seçici alıntı

Belge, `prompt_enhancer` kararını *"resmen kilitlenmiştir"* diye sunuyor (satır 1206-1217).
`MIMARI §6.19z` aynı ölçümün şunları da söylüyor ve belge **hiçbirini aktarmıyor**:
- **İkinci sağlayıcıyla tekrar: KAPALI 14/15 → AÇIK 15/15** — yani ikinci koşum enhancer'ın
  **lehine** çıkmış
- İlk koşumda **2×HTTP 429**; MİMARİ açıkça: *"kaybedilen tek vaka bir 429 artefaktı
  **olabilir**"*
- MİMARİ: *"Bu karar **yeniden açılabilir**"* ve *"«kaybedilen 1» kesin bir gerileme kanıtı
  **DEĞİLDİR**"*

→ **Koşullu bir karar, kesin bir kilit gibi sunulmuş.**

### 9.5 · Belgeden ALINAN — ve neden

| Fikir | Nerede kullanıldı |
|---|---|
| **Kısa devre yasağı** (AJ0) | **G3** — en somut, en yüksek getirili tek madde |
| **Metrik rozetleri / temellendirme** (Y-2) | **G1** — hatayı ilk saniyede görünür kılar |
| **Çakışma + marjin kapısı** (Y-1) | **G1'in kapısı** — mutlak olasılık gerektirmeyen **ilişkisel** sinyaller; `metrik_kaydi` + `belirsizlik_chipi` ile eşsizlik zaten var, **marjin yok** |
| **Diyalog yöneticisi / slot** (AJ0b) | **G2** |
| **İddia kapısı** (AJ1) | **G4** — belgede tanımsızdı; buradaki ölçülebilir tanımı yol haritasından alındı |
| **Referans cebiri** (AJ2) | **G6** — `blend` **düşürülmeden** |
| **Türkçe ek bağlayıcı** (L-2) | **G7** — *"son harfe bakar"* mantığı **düzeltilerek** |
| **Onarım çipleri + sözel onarım** (Y-3) | **G2/onarım** |
| **Fact-Sheet Synthesizer** (T-3) | **G5** — zaten var (`interpret.py`) |

⚠ **Bir uyarı, kayıt için:** belge boyunca kullanıcının her sezgisi doğrulanıyor
(*"%100 doğrudur"* × 2, *"tam isabet"*, *"içinizi rahat tutun"*); hiçbir öneri reddedilmiyor,
hiçbir gerçek gerilim kurulmuyor. Bu, çelişkilerini fark etmemesinin muhtemel sebebidir.
**Bu belge o hatayı tekrarlamamak için yazıldı.**

---

## §10 · BÖLÜM II'YE (v2) DEVİR — BEŞ BORÇ

Bölüm II'nin **başlayabilmesi** için kapatılması gerekenler:

| # | Borç | Bugün | Bu fazın katkısı |
|---|---|---|---|
| **W1** | §C'nin **16 ölçütü** yeşil | 10 ✅ · 5 🟡 · 1 🔴 · 13 ⊘ | 🔴 **G6 → `5.6` bloğunu açar** |
| **W2** | FAZ **8.1** — 1-2 kullanıcı × 2-4 hafta · **≥300 tur** | ⏳ hiç koşmadı | 🔴 **Gizli bloklayıcısı `3.0` tenant açılışı** — *"v1'in tek sessizce atlanan maddesi"*. Pencere onsuz açılmaz |
| **W3** | §II-0'ın **9 maddesine** karar bağlanmış (**telemetriden**, kullanıcıdan değil) | Sıfır madde işaretli | W2'ye sıkı bağlı |
| **W4** | Bölüm II'nin **17 maddesine `GERİ AL` bloğu** + kapının birleşik başlık ayrıştırması | 🔴 açık borç | Belge işi, kod değil |
| **W5** | Enabler zinciri: metrik kaydı (0.18) ✅ · onay akışı (6.1) ✅ · **motor-RLS (1.1)** | `motor_cls` hâlâ `off` — ölçüt 4'ün kırmızısı | Gölge 7 günü koşulmalı |

🔴 **Ve bu, fazın gizli kapsamıdır:** v2'nin üç ön koşulunun **ikisi kod değil, ZAMANDIR**
(W2 pencere · W3 telemetri kararı). Yani *"beklerken ne yapılır"* sorusunun cevabı:
**8.1 penceresini AÇAN işler** — `3.0` tenant açılışı · `7.3`/`7.7`'nin kalanı ·
`motor_cls` gölge turu. Bunlar §G'ye hiç dokunmadan v2 kapısını açmaya başlar ve
**garson fazıyla paralel yürüyebilir.**

⚠ Ve bir belge düzeltmesi zorunlu: `OPERASYON-DURUM.md:6` *"yol haritası §10'daki sıra"*
diyor; **yol haritasında §10 yok** — kastedilen `OPERASYON.md §10`. Bağlamı sıfırlanan bir
ajan bu satırı takip ederse sırayı bulamaz.

---

## §11 · MUTFAK MÜKEMMEL DEĞİL — VE BU FAZI BLOKLAMAZ

> Kullanıcının kendi cümlesi: *"Mutfak mükemmel değil ama en azından birçok şey çıkıyor;
> vakit bevakit mutfak da gelişecek, ama önce sistemi tamamlamak lazım."*

Bu, §1.2'deki *"K1 ve K0 bu fazda DEĞİŞMEZ"* kuralıyla **çelişmiyor** — ama ayrımı yazmak
zorunlu, yoksa mutfak dondurulmuş sanılır.

### 11.1 · Ayrım: GÜVENCE dokunulmaz, KAPSAM gelişmeye devam eder

| Mutfağın | Bu fazda | Neden |
|---|---|---|
| **Güvenceleri** — sayıyı küp koyar · `dry_plan` · fan-out sertifikası · `always_filter` · RLS · sözleşme mührü | 🔴 **DOKUNULMAZ** | Garsonun tüm değeri buna dayanıyor. Güvence gevşerse garson bir yalan taşıyıcısına döner |
| **Kapsamı** — kaç soru cevaplanabiliyor, katalog ne kadar zengin | ⚪ **Gelişmeye devam eder, paralel** | Bu fazın maddesi değil ama **engeli de değil** |

### 11.2 · Mutfağın bilinen açık kusurları — kayıt için

Denetim belgesinin ölçtükleri, bu fazın **kapsamı dışında** ama **unutulmaması gereken**:

| Kusur | Ölçüm | Sahibi |
|---|---|---|
| `R1`'in kökü **kodda değil KATALOGDA** | Kaybın **%62'si**; **55 sinonim çarpışması** | FAZ 3 (kapsam) · katalog turu |
| Türkçe **türetme** katmanının eksikliği | `KÇ-3` ◐ kısmi (`turetme.py` yalnız fiil/isim ayırıcısı) | FAZ 2/3 |
| `motor_cls` hâlâ `off` | §C ölçüt 4'ün kırmızısı | v2 borcu `W5` |
| `netlestirme.py`'nin `yuksek` düzeyi uygulanmıyor | `ask.py:2613-2621` açık itiraf | G2 sırasında **ücretsiz** kapanır |

### 11.3 · İki yönlü bloklama yasağı — ve bir istisna

🔴 **Bir mutfak kusuru bir garson maddesini bloklamaz.** Garson, mutfağın cevapladığını
*anlatır* ve cevaplayamadığını *dürüstçe söyler*; mutfağın dar olması garsonun işini
geçersiz kılmaz — tersine, **dar bir mutfakta iyi bir garson daha da gereklidir** (`G8`).

🔴 **Ve bir garson maddesi bir mutfak kusurunu ÖRTEMEZ.** Bu, deponun en pahalı dersinin
tekrarıdır: *"`gitas` korpustan düştü, payda 445→342 indi, **doğruluk %93,2→%94,3'e ÇIKTI**"*
— sistem bozulurken sayı iyileşti. Aynı desen `--user` unutulduğunda tekrarlandı (229 dosya
root oldu, üç şirket öldü, **toplam yine ✅ %94,8 göründü**).
→ **Kapı: `KURAL A` — payda kutsaldır.** Garson bir soruyu *"güzelce reddedip"* korpustan
düşüremez. Ret, **paydada sayılmaya devam eder**.

⚠ **Tek istisna — `G6`:** kıyas kapısı kurulmadan kapsam açmak yasaktır (§6/G6'nın sıra
kuralı). Yani mutfak ve garson **paralel yürür**, ama `referans` alanı **kapıdan sonra** iner.

---

## §12 · TEST POLİTİKASI — *az koş, doğru koş*

> **Sahibi `OPERASYON.md §3` + `backend/CLAUDE.md`'dir. Bu bölüm onları KOPYALAMAZ**, bu
> faza özel **deltayı** yazar. Çelişkide `OPERASYON.md` kazanır — *ikinci sahip yasağı
> (KAT-1)*, deponun kendi adlandırdığı kusur sınıfıdır.

### 12.1 · Değişmeyen merdiven — üç seviye, dördüncüsü yok

| # | Ne zaman | Komut | Süre |
|---|---|---|---|
| **0** | 🔴 **Bir dosya düzenledikten sonra** | `pytest tests/test_<o_dosya>.py` | **3–15 sn** |
| **1** | **Demet sonunda, BİR KEZ** | `kapi.py --hizli --degisen <tüm değişenler>` | ~15–60 sn |
| **2** | **Demet sonunda, BİR KEZ** | `kapi.py --tam` *(yalnız korpus)* | **1 dk 50 sn** |
| **3** | **Gecelik CI** *(insan beklemez)* | `kapi.py --hepsi` | **4 dk 06 sn** |

🔴 **Seviye 3 YEREL KOŞULMAZ.** Ne demet sonunda, ne commit öncesi, ne *"bir de şuna
bakayım"* diye.

### 12.2 · 🔴 STRATEJİ BAYATLADI — ve neden

> *"Bu özel bir geliştirme olduğundan, eski mutfağı kontrol eden test stratejisi de
> bayatlamış olabilir."* — **Doğru. İki yerinden.**

**Bayatlayan (1): merdiven SÜREYE göre dizilmiş.**
Üç seviye *"ne kadar sürer"*e göre ayrılmış (15 sn · 1:50 · 4:06). Bu, tek türden bir
sistemde — **tümüyle deterministik bir mutfakta** — doğru eksendir. Garson katmanı o eksende
yaşamıyor: onun bazı parçaları **tam deterministik**, bazıları **tümüyle belirlenimsiz**, ve
ikisi arasında üçüncü bir tür var. Süre eksenine dizilince belirlenimsiz parça ya **hiç
koşmaz** (pahalı diye atlanır) ya **her koşumda farklı sonuç verir** (gürültü sanılır).

**Bayatlayan (2): korpusun NÜFUSU yanlış tarafta.**
Korpus soruları **katalogdan üretiliyor** — hepsi doğru yazılmış, hepsi katalog dilinde. Bu,
mutfağı ölçmek için doğru nüfustur. Ama garsonun nüfusu **dağınık insan cümlesidir** ve
korpusta o cümle **hiç yok**. Deponun kendi yazısı bunu zaten kabul ediyor:
*"Typo yolu korpusta hiç sorulmuyor… sayı yalan söylemiyor, o yolu GÖRMÜYOR."*

### 12.2b · YENİ EKSEN — süre değil **TABİAT** (belirlenimlilik)

| Tür | Ne ölçer | Belirlenimli mi | Sıklık | Alet |
|---|---|---|---|---|
| **D · DETERMİNİSTİK** | Mutfak + **garsonun deterministik yarısı**: temellendirme · slot · onarım · marjin · kapasite · ek motoru | ✅ tam | **her düzenleme / demet** | hedefli `pytest` · `--hizli` · `--tam` |
| **K · KAYITLI** *(kaset)* | LLM'in **etrafındaki tesisat**: model X derse akış doğru çalışıyor mu? | ✅ **kayıtla** | **demet sonu** | 🆕 kaydedilmiş sağlayıcı yanıtları |
| **C · CANLI** | **Kalite**: insana benziyor mu? | ❌ hayır | **faz sonu · ×2** | `lab/garson.py --live` |

🔴 **Asıl kazanç `K` katmanındadır ve bugün YOK.** Garsonun kodunun büyük kısmı LLM'in
*cevabını* değil, *cevabın etrafındaki akışı* yönetiyor: slot dolduruldu mu, onarım doğru
slotu mu değiştirdi, guard doğru cümleyi mi düşürdü, iddia kapısı doğru mu reddetti. Bunların
hepsi **LLM'in ne dediğini SABİTLEYEREK** deterministik olarak test edilebilir.

**Kaset nasıl kurulur** *(yeni motor yazılmaz)*: `--live` koşumunda sağlayıcı yanıtları
`lab/kasetler/<senaryo>.json`'a **kaydedilir**; `K` koşumunda sağlayıcı yerine kayıt
konur. Depo bu deseni zaten tanıyor — **VQR** birebir bu fikirdir (doğrulanmış soru → tekrar
oynatma), ve `konusma_senaryolari.py` zaten **canlı/yapısal** iki modlu.

⚠ **Kasetin sınırı yazılı olsun:** kaset **kaliteyi ölçmez**, yalnız **tesisatı** ölçer. Bir
kaset yeşilken ürün kötü olabilir — o yüzden `C` katmanı **kaldırılmaz**, seyrekleştirilir.

### 12.2c · `gercek_dunya.py` TERFİ EDİYOR

Bu fazda **kapı statüsü değişen tek mevcut alet**: `lab/gercek_dunya.py` persona × zorluk
matrisiyle **dağınık insan cümlesini** ölçüyor ve **LLM'siz koşabiliyor** — yani garsonun
nüfusuna en yakın **deterministik** ölçüm.

| | Önce | **Bu fazda** |
|---|---|---|
| Rolü | lab aracı | 🔴 **`D` katmanında birinci sınıf kapı** |
| Ne zaman | ara sıra | **demet sonu**, `--tam` ile birlikte |
| Ölçtüğü | kabul · doğru · sessiz_yanlış · beyanlı_kısmi | **aynı** — ve `sessiz_yanlış` **artamaz** *(doğruluk vetosu)* |

*Korpus paydayı korur (KURAL A), gerçek-dünya nüfusu doğru tutar. İkisi rakip değil, iki
farklı körlüğün panzehiri.*

### 12.2d · Bu fazın EK kapısı

| # | Ne zaman | Komut | Rolü |
|---|---|---|---|
| **G** | 🔴 **Bir G-fazı bittiğinde, BİR KEZ** *(ve gecelik)* | `lab/garson.py --live` | **Kazanç kapısı** — bu fazın tek onay kapısı |

**Neden ayrı:** LLM'e bağlı, kotaya bağlı, belirlenimsiz ve yavaş. Geliştirme döngüsünde
koşarsa hem kotayı yakar hem geliştirmeyi durdurur. **Yeri faz sonudur, tur arası değil.**

### 12.2e · Sonuç — geliştiricinin gerçek ritmi

```
dosya düzenledin        →  pytest tests/test_<o dosya>.py           (3-15 sn · D)
demet bitti             →  --hizli --degisen  +  --tam  +  gercek_dunya   (~3 dk · D)
                           +  kaset koşumu                           (~30 sn · K)
G-fazı bitti            →  garson.py --live  ×2                      (kota · C)
gecelik CI              →  --hepsi                                   (4:06 · D+K)
```

🔴 **Ve bu, eskisinden DAHA AZ koşum demektir:** `K` katmanı, bugün ancak `--live` ile
görülebilen kusurları **demet sonunda ve bedavaya** yakalar; böylece pahalı `C` katmanı
**faz sonuna** ertelenebilir ve orada iki kez koşulabilir (KURAL G-1).

### 12.3 · 🔴 Bu fazın YENİ kuralı — belirlenimsiz kapı TEK KOŞUMLA karar vermez

Kanıt:
- **Power BI ölçümü:** 1000 kez aynı sorgu; **en sık cevap yalnız 78 kez**.
- **Deponun kendi tarihi:** `prompt_enhancer` kararı tek koşumla verildi (*"kaybedilen 1"*);
  **ikinci sağlayıcıyla tekrar 14/15 → 15/15**, yani **tersine döndü**. Ve MİMARİ dürüstçe
  yazmış: *"kaybedilen tek vaka bir 429 artefaktı **olabilir**; tek koşumla ayırt edilemez."*

> **KURAL G-1:** `lab/garson.py --live` ile alınan **hiçbir karar tek koşuma dayanamaz.**
> En az **iki koşum**, tercihen **iki farklı sağlayıcı**. İki koşum ayrışırsa karar
> **verilmez** — `⊘ ÖLÇÜLEMEDİ` yazılır ve borç kaydına girer.

⚠ Bu kural **daha çok test demek değildir** — daha **az** demektir: kapı seyrek koşar (faz
başına bir kez), ama koştuğunda **kararlık** taşır. *Bir kapıyı beş kez koşmak onu bir kez
koşmaktan güvenli yapmaz; iki kez koşup ayrışmayı görmek yapar.*

### 12.4 · Yasaklar — hepsi ölçülmüş bir israftan doğdu

| # | Yasak | Ölçülen bedel |
|---|---|---|
| **Y1** | 🔴 *"Bu kod ne yapıyor?"* sorusunu **kapı koşarak** cevaplama — **kaynağı OKU** | `motor_cls` sorusu için **üç tam süit** (~7 dk) koşuldu; cevap **tek satırdı** ve okunacaktı |
| **Y2** | Demet başına **birden fazla** `--hizli` | Bir turda `--hizli` **dört kez** koşuldu; kullanıcı iki kez uyardı |
| **Y3** | Faz ortasında yerel `--hepsi` | Yeri gecelik CI'dır ve orada **bedava**dır |
| **Y4** | 🔴 Geliştirme döngüsünde `garson.py --live` | Kota + duvar saati + belirlenimsizlik |
| **Y5** | **Kapı koşarken repoya yazma** | Mount canlıdır, ölçüm karışır |
| **Y6** | 🔴 **Korpus seyreltme** — *"uzunsa soru azaltalım"* | Payda kırpılırsa korpusun tek gerçek yakalaması görünmez olur. **KURAL A: payda kutsaldır** |
| **Y7** | `--rm` ile koşum · `--user` unutma | `--rm`: iki koşumun özeti kayboldu. `--user` unutuldu: **229 dosya root**, üç şirket öldü, **toplam yine yeşil göründü** |

### 12.5 · Hız kaynaktan değil çekirdekten satın alınır

Kapsam kırpılmaz, **payda bölünür**: korpus şirket×dilim → 16 süreç; süit `pytest -n 8`.
Ölçüldü: korpus **13:18 → 1:50**, süit **8:30 → 2:15**, tam kapı **~15 dk → 4:06**, ve
sayılar seri koşumla **birebir aynı**. İki test konteynerinin paralel koşum yasağı
**2026-08-04'te kapandı** (`lab/izolasyon.py` her sürece kendi derlenmiş ağacını verir).

### 12.6 · Bu fazın kapı sözleşmesi — hangi kapı neye karar verir

| Kapı | Neye **KARAR VERİR** | Neye **KARAR VEREMEZ** |
|---|---|---|
| `kapi.py --tam` (korpus) | 🔴 Cevaplanan sorunun **doğruluğu** · payda bütünlüğü | ⚪ Garsonun inip inmeyeceği |
| `eval.run` | 🔴 Uçtan uca **bozulma** · `sessiz_yanlis` | ⚪ Konuşmanın kalitesi |
| `lab/garson.py --live` | 🔴 **Garsonun inip inmeyeceği** | ⚪ Sayının doğruluğu |
| Hedefli `pytest` | Değişmezlerin kilidi | — |

🔴 **Ve `⊘ ÖLÇÜLEMEDİ` bir geçiş değildir.** Ölçülemeyen bir madde *"riski yok"* diye
yeşile yuvarlanmaz; **borç kaydına** girer ve son kullanma tarihi taşır.

---

## §13 · GELİŞTİRME POLİTİKASI

> Sahibi `OPERASYON.md §2 · §4 · §5 · §6 · §9`'dur. Aşağıdakiler bu faza özel **delta** ve
> **hatırlatmadır**.

### 13.1 · Döngü — her madde için, istisnasız

```
1 OKU      ilgili kaynağı ve kuralı OKU  (kapı koşarak öğrenme — Y1)
2 ÖLÇ      kusuru ÖNCE ölç              (ölçülmemiş kusur düzeltilmez)
3 YAZ      en dar biçimi yaz            (genel motor yazma)
4 KAPIYA   düzeltmeyi bir KAPIYA çevir  (tekrarı yapısal olarak imkânsız kıl)
5 DOĞRULA  hedefli pytest → demet sonu --hizli + --tam
6 COMMIT   açıklayıcı mesaj, Claude footer YOK (saka standardı)
```

🔴 **Adım 4 atlanamaz.** Kapıya çevrilmemiş bir düzeltme, aynı kusurun bir sonraki turda
tekrar doğmasına açıktır — denetim belgesinin kaydı: aynı hata **üç kez** çağrı yerinde
yamalandı, *"kapının kendisinde hiç"*.

### 13.2 · Altı bloklu madde biçimi — bu belgedeki her G maddesi taşır

`NEDEN` *(ölçülmüş)* · `NE` · `NASIL` · `KAPI` · `GERİ AL` · `BÜYÜKLÜK` · `ADIMLAR`

🔴 **`GERİ AL` bloğu olmayan madde sıraya alınmaz.** Blok, madde **planlandığında** yazılır,
teslim edildiğinde değil. *(Bölüm II'nin 17 maddesi bu yüzden borçlu — `W4`.)*

### 13.3 · Beş değişmez — bu fazda özellikle kırılgan olanlar

| # | Değişmez | Bu fazdaki riski |
|---|---|---|
| **KAT-1** | 🔴 **Tek sahip.** Bir kuralın iki sahibi olamaz | En yüksek risk: `Niyet` ↔ `referans` ↔ slot durumu **üçü de aynı şeyi** temsil edebilir. G2 ve G6 kapıları bunu AST ile kilitler |
| **ADR-0008** | 🔴 **Dili kelime listesiyle kovalama** | `_SOSYAL`, dolgu sözlüğü, kalıp sözlükleri — hepsi bu yasağın sınırında. Kural yaz, liste değil |
| **Fail-closed** | Şüphede **kapat** | `iddia.py` (G4) ve `narration_guard` fail-closed; sağlayıcı çökerse metin yok, **cevap yine döner** |
| **Yetim yasağı** | Backend yeteneği frontend tüketicisi olmadan **bitmiş değildir** | `temellendirme`·`diyalog_durumu`·`kapasite` üçü de yeni `AskResponse` alanı → `test_cevap_alani_yetim_degil.py` |
| **Ajan yazamaz** | `tools.py:26-29` | Bu faz ajan açmıyor; ama G8'in *"şunu yapabilirim"* beyanı bir **yetenek iddiasıdır** ve G4'ten geçer |

### 13.4 · Bayrak disiplini

```
off  →  alpha (tek test kullanıcısı)  →  ÖLÇ  →  beta  ya da  off + YAZILI GEREKÇE
```

🔴 **Ölçüm sonucu `off` ise gerekçe `MIMARI.md`'ye yazılır.** Sessizce kapalı bırakmak
yasaktır — `t2_anlatici`'nin bugüne kadar kapalı kalmasının sebebi tam olarak buydu:
gerekçe **ölçülmemişlikti**, ama belge **karar** gibi okunuyordu.

⚠ Ve `features.resolve_for()` yalnız `"off"` olanı eler → **`beta` = AÇIK**. Bir bayrağı
*"beta'da bıraktım, kapalı"* diye anmak yanlıştır.

### 13.5 · Demet disiplini — commit ≠ kapı

Commit **sık**, kapı **seyrek**. Bir demet şu üç sınırdan hangisi **önce** gelirse kapanır:
merkezî dosyaya dokunuldu · davranış değişti · madde bitti. Demet kapanınca **bir kez**
seviye 1+2; G-fazı bitince **bir kez** seviye G.

### 13.5b · 🔴 YETİM YASAĞI — *"bir köşede kalmak"* yapısal olarak imkânsız

> *"Geliştirip bir köşede kalırsa çok kötü olur."* — Bu depoda o riske karşı **dört kapı**
> zaten var. Bu bölüm onları adlandırır ve bu fazın ne eklediğini yazar.

#### Mevcut dört kapı — hepsi kurulu

| Kapı | Neyi tarar | Yön |
|---|---|---|
| `tests/test_uc_yetim_degil.py` | **Uç seviyesi** — *"Tanım Tamamlandı = arka + ön + test"* | uç → UI |
| `tests/test_cevap_alani_yetim_degil.py` | **Alan seviyesi** — `AskResponse`'a eklenen her alanın **tüketicisi** olmalı | alan → UI |
| `tests/test_ters_yetim.py` | 🔴 **TERS yetim** — frontend'in beklediği ama backend'in **VERMEDİĞİ** alan | UI → uç |
| `tests/test_frontend_buyume.py` | Frontend modül **büyüme tavanı** | boyut |

*Dördü birlikte iki yönü de kapatıyor: üretilip tüketilmeyen **ve** beklenip üretilmeyen.*

#### 🔴 Bu fazın «tamamlandı» tanımı — beş şart, hepsi birden

Bir G-fazı ancak şunların **beşi de** sağlanınca kapanır:

```
① arka uç kodu           ② ön yüz tüketicisi       ③ kapı testi
④ belge (MIMARI + DURUM) ⑤ ölçüm (D/K katmanı yeşil · C katmanı faz sonu)
```

**Dördü var beşincisi yoksa madde AÇIKTIR.** *Bu fazın kendi tarihi bunu doğruluyor:
`Planlayici.sec()` yazıldı, testlendi, belgelendi — ve **iki yıl tüketicisiz** durdu.
`mod` anahtarı UI'da duruyor, sunucu **yok sayıyor**. SSE hattı **tam yazılmış**, bayrak
kapalı olduğu için hiç tetiklenmiyor.* Üçü de *"bitti"* sayılmıştı.

#### Bu fazın ön yüz envanteri — faz faz, boşluk yok

| Faz | Ön yüz işi | Nerede |
|---|---|---|
| `G0` | *(alet — UI yok, bilinçli)* | — |
| `G0b` | 🖥 **güven sinyali**: *"hava boşluğu · N yer tutucu · dışarı çıkan: yok"* | `Makbuz.tsx` `[G0b.9a]` |
| `G1` | 🖥 tip · render · **tıklanabilir rozet** | `types.ts` · `ReportCard.tsx` `[G1.5-1.7]` |
| `G2` | 🖥 açık slot **mevcut chip satırında** *(yeni panel YOK)* | `[G2.12]` |
| `G3` | 🖥 merdiven izi | `Makbuz.tsx` `[G3.7]` |
| `G4` | 🖥 **düşen cümle sayısı** — guard'ın iziyle aynı yerde | `Makbuz.tsx` `[G4.8b]` |
| `G5` | 🖥 akış tüketicisi + anlatı render'ı **doğrulanır** *(ikisi de yazılı)* | `[G5.10b-c]` |
| `G6` | 🖥 kıyas chip'leri **tek şablon** · eski `yoy` dalı **silinir** | `[G6.12]` |
| `G7` | 🖥 **bilinçli olarak YOK** — gerekçe yazılır | `[G7.7b]` |
| `G8` | 🖥 kapasite, ret kartında | `ReportCard.tsx` `[G8.6]` |

🔴 **Ve üç yeni alan kapıya bağlanır:** `temellendirme` · `diyalog_durumu` · `kapasite` —
üçü de `test_cevap_alani_yetim_degil.py`'nin taramasına girer. Tüketicisiz alan **CI
kırmızısıdır**, tartışma konusu değil.

⚠ **Panel enflasyonu yasağı korunur (PK-1):** bu fazın **hiçbir maddesi yeni panel
açmıyor**. Her şey mevcut üç yüzeyde: `ReportCard` · `Makbuz` · chip satırı.

### 13.5c · 🔴 ARAYÜZ ŞARTNAMESİ — *ne, nereye, neye benzeyecek*

> *"Geliştirip frontta karşılığı olması gereken şeyin karşılığı olmazsa hiçbir anlamı
> kalmaz."* — Bu bölüm, her fazın ön yüz işini **adım değil, tasarım** olarak yazar.
> ⚠ **Ön yüz taraması yapıldı (2026-08-07):** 44 bileşen · `src/lib/types.ts` ·
> `api-client.ts`. Aşağıdaki *"zaten var"* işaretleri o taramadan.

#### Yerleşim — üç yüzey, dördüncüsü açılmıyor

```
┌─ ReportCard ────────────────────────────────────────────────┐
│  ① SourceBadge            ◆ CUBE / ▚ CUBE+LLM      [:537]    │
│  ② 🆕 TEMELLENDİRME       rozet dizisi              [G1]      │
│  ③ soz ?? note                                      [:643]    │
│  ④ tablo / grafik                                             │
│  ⑤ OutputInsight          summary · 🆕 narration    [G5]      │
│  ⑥ calculation_explanation                          [:962]    │
│  ⑦ chip satırı            turetme·tanim·devam·🆕slot [G2]      │
│  ⑧ Makbuz  ▸ "tam iz"     yol · 🆕merdiven · 🆕hava · 🆕iddia │
└──────────────────────────────────────────────────────────────┘
🔴 Dördüncü panel YOK (PK-1). Her şey bu üç yüzeyde: kart · chip satırı · makbuz.
```

#### Faz faz tasarım

**`G1` · TEMELLENDİRME** — kartın **en üstünde**, tablodan **önce**

```
┌──────────────────────────────────────────────────────────┐
│ ◆ CUBE                                                    │
│ ┌ anladığım ─────────────────────────────────────────┐   │
│ │ [Satış Cirosu (TL)] [Mart 2026] [Şube: Merkez] [↻]│   │
│ └────────────────────────────────────────────────────┘   │
```
· Her rozet **tıklanabilir** → o alanı değiştiren chip → `POST /cube` (**0 LLM**)
· Ham kolon adı **yasak** — `interpret._ad()` üzerinden görünen ad
· Boşsa **hiç basılmaz** *(başarılı turda boş olamaz — `G1.8` kapısı)*
· Dosya: `types.ts` *(tip)* · `ReportCard.tsx` `SourceBadge`'in **hemen altı** (`:537`)

**`G2` · AÇIK SLOT** — **mevcut chip satırında**, yeni kutu yok

```
⑦  [ Mart mı Nisan mı? ]  [ bunu mu demek istedin: fire ]   ← bugünkü chip'ler
    ⌐ bekleyen: dönem                                        ← 🆕 tek satır, soluk
```
· `diyalog_durumu.acik_slotlar` doluysa chip satırının **altına** soluk bir satır
· Slot dolunca **kaybolur** — kalıcı bir gösterge değil, **bir bekleyiş işareti**

**`G3` · MERDİVEN İZİ** — ⚠ **render ZATEN VAR**, içerik zenginleşir
`Makbuz.tsx:209-213` `explain.path`'i *"tam iz"* `<details>`'inde basıyor.
Yeni: `route → (aday: yazım önerisi) → Intent-JSON ✓` biçiminde **basamak dizisi**.

**`G0b` · HAVA BOŞLUĞU** — aynı *"tam iz"* bloğunda tek satır
`hava boşluğu · 3 yer tutucu · dışarı çıkan: yok`
🔴 Bu bir **güven sinyalidir**; görünmeyen güvenlik satılamaz.

**`G4` · İDDİA KAPISI** — aynı blokta, guard'ın iziyle **yan yana**
`guard: 0 cümle düştü · iddia: 1 cümle düştü`

**`G5` · ANLATI** — ⚠ **ikisi de ZATEN bağlı**, yalnız doğrulanır
· `OutputInsight.tsx:82-93` → `narration` render'ı
· `ReportCard.tsx:945-955` → AI Act Md.50 işareti *(yalnız `narration` varken)*
· 🆕 **akış**: `api-client.ts:306 streamAskJob` + `DurdurDugmesi.tsx` yazılı → bayrak açılınca
  **yazıyor-animasyonu** gerçekten çalışmalı

**`G6` · KIYAS CHIP'LERİ** — **tek şablon**
Bugün `yoy` için **özel dal** var; `referans` inince o dal **silinir** ve tüm kıyaslar
(dönem · kohort · hedef · bütçe) aynı chip şablonundan çıkar.

**`G7` · YOK — bilinçli.** Ek motoru metni biçimlendirir; çıktı mevcut render'dan geçer.

**`G8` · KAPASİTE** — **ret kartında**, `soz ?? note`'un (`:643`) altında

```
│ Bunu yapamam: v1'de tahmin (forecast) yok.                │
│ ┌ ama şunları yapabilirim ───────────────────────────┐    │
│ │ [Aylık ciro trendi]  [Son 6 ay karşılaştırma]      │    │
│ └────────────────────────────────────────────────────┘    │
```
· Öneriler `route()` ile **doğrulanmış** *(`G8.5`)* — çalışmayan öneri **basılmaz**
· ⚠ `G8.2`'nin borcu: `suggestions`/`next_steps` zaten var → **üçüncü kanal açma**

#### Kapı — şartname teste bağlanır

`tests/test_ters_yetim.py` **zaten** frontend'in beklediği-backend'in vermediği alanı
tarıyor. Bu fazda **ters yönü de** kilitlenir: yukarıdaki her 🆕 için
`test_cevap_alani_yetim_degil.py`'de bir tüketici **gösterilebilir olmalı**.
🔴 **Tasarımı yazılmamış bir alan, sıraya alınmaz** *(`13.2`'nin yedi bloğu gibi)*.

### 13.6 · 🔴 BELGE BAKIMI — iki dosya her G-fazında güncellenir

> Bu faz **mimari ağırlıklıdır**: yeni katman (`diyalog.py`), yeni kapı (`iddia.py`), yeni
> alan (`referans`), yeni sözleşme alanları, ve bir **değişmezin ikiye bölünmesi** (§G.1).
> Bunların hiçbiri yalnız kodda kalamaz.

| Belge | Rolü | Ne zaman güncellenir | Ne yazılır |
|---|---|---|---|
| 🔴 **`backend/MIMARI.md`** | **Mimari otorite** — çelişkide **o** kazanır | **Her G-fazının commit'inde**, kodla **aynı** commit'te | Yeni katman/kapı · §5'in yasak listesi · ADR · **ölçülmüş geri almalar ve ortamı** · bilinen kusurlar |
| 🔴 **`OPERASYON-DURUM.md`** | *"Nerede kaldık"* — bağlam sıfırlanınca **tek dayanak** | **Her G-fazı bitişinde** | Faz durumu · ölçüm tabanı · **açık borçlar** · atlanan maddeler |

🔴 **Kapı: kod ve belge AYNI COMMIT'te gider.** *"Sonra yazarım"* bu depoda ölçülmüş bir
kusurdur — `MIMARI.md`'nin §5'i 18. yasağı **⟳ UYGULANMADI** diye taşırken `:442` aynı
yasağı **inmiş** olarak anlatıyor (§4.4/Ş2). **İki satır aynı belgede çelişiyor** çünkü biri
zamanında güncellenmedi.

**Bu fazda `MIMARI.md`'ye girmesi ZORUNLU olan beş şey:**

| # | Ne | Hangi fazda |
|---|---|---|
| 1 | 🔴 **Değişmez İKİYE BÖLÜNÜR:** *"sayıyı küp koyar"* (guard) **ayrı**, *"LLM'in her iddiası şemaya karşı doğrulanır"* (`iddia.py`) **ayrı**. §4 bugün ikisini tek kural sayıyor ve **bu bölümle çelişir** | `G4` |
| 2 | **18. yasak** — *"cevapsız bir dal cevaplı bir yolu KESEMEZ"* + **dördüncü koşulu** (*bir sonraki basamak gerçekten daha yetenekli olmalı*) ve **hangi ortamda ölçüldüğü** | `G3` |
| 3 | **`KÇ-1`'in beyan-açık sapması** — denetim `fail-closed` istedi, uygulama `beyan-açık` seçti; gerekçesiyle | `G1` |
| 4 | 🔴 **`llm_sema_kisitli`'nin seçilen sağlayıcıda NO-OP olduğu** (§7.4) — ölü bayrak görünür kılınır | `G0` |
| 5 | **`referans` cebiri + `R11`** ve `compare`'ın deprecation'ı | `G6` |
| 6 | 🔴 **ÜÇÜNCÜ DEĞİŞMEZ — HAVA BOŞLUĞU:** *"LLM'e giden her yük tek geçitten geçer; ham satır · gerçek değer · gerçek sayı **binadan çıkmaz**"*. Bugün §4 iki değişmez tanıyor (sayı · iddia); bu **üçüncüsüdür** ve bir **güvenlik sınırıdır** | `G0b` |

### 13.7 · Belge disiplini — genel

- 🔴 **Kaynağı güncelle, kopyalama.** Bir belgeyi ikinci dosyaya kopyalayıp orada çalışmak
  yasak; özgün metin korunur, üstüne işaretli annotation eklenir.
- **Kapananlar işaretlenir, silinmez** (MIMARI §10).
- **Bir belgeye yazılan sayı, yazıldığı anın fotoğrafıdır.** Taban diye okunursa yanlış
  gerileme alarmı üretir. Güncel taban daima `lab/reports/`'tadır.
- 🔴 **Ölçülen her geri alma, gerekçesiyle yazılır** — *ve hangi ORTAMDA ölçüldüğü de*
  (§2.2'nin dersi: `rule` sağlayıcıyla ölçülmüş bir geri alma, ölçülmüş sayılmaz).

### 13.8 · 🔴 ZAN YASAĞI — her iddia kodla doğrulanır

> *"Zan ile hareket etme, böyle bir şansımız yok; kanıtlı olmalıyız."*

- Bir belgeye `dosya:satır` yazılıyorsa, **o satır okunmuş olmalıdır**.
- Bir ajan raporundaki atıf **ikinci elde kanıttır** — kullanılmadan önce **doğrulanır**.
- **Ölçüldü:** bu belgenin ilk sürümünde dört atıf bayattı (`answer.py:441`→`426` ·
  `context.py:82-87`→`83-85` · `ask.py:1701`→`1702` · `ask.py:3799`→`3864`). İddialar
  doğruydu, **satırlar kaymıştı** — ve bayat bir atıf, yanlış bir iddiadan **daha
  tehlikelidir**: yanlış iddia sorgulanır, bayat atıf **güvenilir görünür**.
  *(Aynı ders `demo/wren-project` artefaktında ödendi: bayat okuma, yanlış sonuçtan kötüdür.)*
- **Kapı:** bir G-fazı commit'inde belgeye yeni bir `dosya:satır` giriyorsa, o satır
  `grep`/`sed` ile **gösterilebilir** olmalı.
- 🔴 **«YOK» İDDİASI EN TEHLİKELİ CÜMLEDİR** — çünkü **ikinci sahip** doğurur.
  Ölçüldü: bu belgede **iki** modül (`llm_guard` · `yetenek`) *"yok"* sanıldı, **vardı**;
  üç kavram (`marjin` · temellendirme kuralı · ek kuralları) *"yeni"* sanıldı, **emsali vardı**.
  **Yöntem kuralı:** bir şeye *"yok"* demeden önce (a) **kavrama** göre ara, ada göre değil;
  (b) **iki dilde** ara — depo Türkçe yazar ama sabitleri İngilizce adlandırır
  (`AUTO_MARGIN` ≠ `marjin`); (c) `ls app/*.py` **tamamını say** — 95 modül, arama değil **sayım**.

### 13.9 · Bu fazın tek kırmızı çizgisi

> 🔴 **`G0` inmeden hiçbir kod yazılmaz.**
> Ölçemediğimiz bir şeyi geliştiremeyiz; ve bu fazın tamamı, tam olarak bunun bir kez daha
> olmasını engellemek için bu sırayla dizildi.

---

## §14 · RİSK KAYDI

| # | Risk | Ölçüsü | Karşılık |
|---|---|---|---|
| **R1** | 🔴 **Bakım çürümesi.** Anthropic'in kendi ölçümü: bir ay semantik katman bakımı gevşeyince **%95 → %65** | `nl_corpus` haftalık | Garson **doğruluğu artırmaz** — onu görünür kılar. Katalog bakımı bu fazın ön koşuludur ve **azalmaz** |
| **R2** | **Aşırı sorma.** Amazon ASRU 2021: aşırı netleştirme UX'i bozar | soru/tur oranı | §5/4'e **tavan** konur; Wang & Ai'nin risk modeli: sorma bedava değil |
| **R3** | **Karmaşık bellek zarar verir.** JPMorgan: −12,6 puana kadar | `lab/garson.py` §5/5 | İki turluk pencere **genişletilmez** (G2 kapısı kilitler) |
| **R4** | **Sessiz garanti kaybı.** Şema kısıtı yalnız Anthropic'te gerçek | failover kaydı | G6'nın kapısı: kayıp **makbuza yazılır** |
| **R5** | **Kota.** §6.19z'de **54×429** yaşandı; küçük modeller gürültülü | canlı koşum | `lab/garson.py --live` turlar arası **bekleme** taşır (`LIVE_BEKLE`); kapı **gecelik** |
| **R6** | **Maliyet sürprizi.** Pilotlar üretim faturasının %15-25'inde koşar | token telemetrisi | §7.1'in üç katmanlı öneki; anlatı **ucuz modelde** |
| **R7** | 🔴 **Garson yavaşlatırsa terk edilir.** *"Kendinden emin yanlış cevap yavaş olandan pahalıdır"* — ama yavaş doğru cevap da terk edilir | p50/p95 | §7.2 bütçesi + akış (SSE zaten yazılı) |
| **R8** | **Kendi çelişkimiz.** `t2_anlatici` açılınca `interpret.summary` ile **iki anlatı sahibi** doğar | AST kapısı | `test_t2_anlatici.py`'nin 2. değişmezi zaten kilitliyor: `summary`/`facts` **ezilmez** |

---

## §15 · KAPANIŞ DENETİMİ — *her girdi nereye düştü*

> 🔴 **Bu bölümün amacı:** *"analiz edildi ama belgeye girmedi"* sınıfını **yapısal olarak
> imkânsız** kılmak. Dört girdi kaynağının **her maddesi** aşağıda ya bir faza bağlıdır ya
> **yazılı gerekçeyle** düşürülmüştür. Boş bırakılan satır **yoktur**.

### 15.1 · Danışman belgesi — 2203 satır, önerilerin akıbeti

**Bu faza GİRENLER** *(dokuz)* — §9.5'te ayrıntılı:
`AJ0` kısa devre → **G3** · metrik rozetleri → **G1** · çakışma+marjin → **G1.4b-d** ·
diyalog yöneticisi → **G2** · iddia kapısı → **G4** · referans cebiri → **G6** ·
Türkçe ek → **G7** · onarım çipleri → **G2.8** · Fact-Sheet → **G5** *(zaten var)*.

**DÜŞÜRÜLENLER — ve gerekçeleri:**

| Öneri | Neden düşürüldü |
|---|---|
| **Kademeli şelale %95/%80** | 🔴 Kalibre skor **yok**, MIMARI uydurmayı yasaklıyor → **§1.1c**'de ilişkisel sinyallerle değiştirildi |
| **Yerel BERT/DeBERTa (N-1)** | Etiketli eğitim verisi kaynağı **hiç konuşulmamış**; sabit niyet enum'u AJ2'nin cebirsel açıklığıyla **ters** → §8 |
| **30 varyasyonlu şablon NLG (L-1)** | 🔴 Kullanıcının kaçtığı duygunun kendisi; *"$0.00"* muhasebesi yanlış → §8 |
| **Generative UI mikro-kartlar (U-1)** | *"%80'i görselliktir"* **uydurma istatistik**; ad yanıltıcı (koşullu render) + panel enflasyonu → §8 |
| **Eylem kartları / tek tıkla CRM (U-2)** | Ürünü **yazma-yetkili aktöre** çevirir; yetki/geri alma/onay zinciri hiç konuşulmamış → v2/v3 |
| **Karar motoru (S-1…S-11)** | v3; `◆ FAIRNESS VERIFIED` rozeti istatistiksel+hukuki olarak savunulamaz; korumalı kategori verisi PII bölümüyle çelişiyor → §8 |
| **What-if / simülasyon (S-4)** | Ekonometrik **tahmin**, deterministik hesap değil; SHA-256 mührüyle sunmak daha tehlikeli → §8 |
| **DoWhy / nedensellik (S-10)** | Gözlemsel veriden nedensellik *"kanıt"* diye sunulamaz → §8 |
| **Anonimleştirme proxy (R-1…R-3)** | Yöntem reddedildi (Ç-24) → §8; 🔴 **gereksinim `G0b`'de KARŞILANDI** — korunan yayılım |
| **Otomatik korelasyon taraması (L-3)** | Çoklu karşılaştırma düzeltmesi yok → **garantili sahte keşif** → §8 |
| **`AJ5`/`AJ5b`/`AJ6` (A-1…A-5)** | Garson **konuşur**; çok adımlı rapor v2 → §8 |
| **`AJ3` `tur_yoneticisi` (F-4)** | 🔴 Belgede **tanımsız** — bir kez geçiyor, nihai plana **hiç girmiyor**. Ölü madde |
| **`AJ3b` çalışırken sorma (F-5)** | SSE'de `soru` olayı ve `awaiting_input` **yok**; `G2`+akış inmeden anlamsız → v2 |
| **`AJ4` oturumlar-arası hafıza** | JPMorgan: karmaşık bellek **−12,6 puana** kadar zarar → `G2.10` basitlik kilidiyle **bilinçli dışarıda** |
| **Base-100 endeks (Z-4)** | `Veri_0 = 0` veya negatifse patlar; t0 seçimi sonucu değiştirir — *"deterministik"* sunumu yanıltıcı → v2 |
| **`unit_splitter` / çoklu birim (Z-3)** | Gerçek boşluk ama **görselleştirme** işi, garson değil → v2 |
| **Güvenli LLM Spec-Generator (Z-6)** | LLM'e **üretim** rolü açar; `jsonschema` geçerliliği doğrular, **doğruluğu değil** → §8 |
| **`TUR_GORUNUM_DONUSUMU` (Z-1)** | Zaten var (`viz.py` + `followup.py`); yeni iş yok |

**28 çelişkinin akıbeti:** Ç-1·Ç-5·Ç-6·Ç-7·Ç-9 → §9.3 tablosunda · Ç-2 → §9.3 + `G4`'ün
gerekçesi · Ç-3 → §3.1 ölçümüyle çürütüldü · Ç-4 → §8 · Ç-8 → **§7.1**'de üç katmanlı
önekle çözüldü · Ç-10 → `G7`'nin *"kural yaz, liste değil"* kilidi · Ç-11 *(chip: kusur mu
erdem mi)* → **§1.1c** ve `G3`'ün aday defteriyle çözüldü · Ç-12 → `G1.4b` marjin ·
Ç-13 *(yerel NLU bölümü plana bağlanmamış)* → §8 · Ç-14 → **`G6.5`'te `blend` geri alındı** ·
Ç-15 → **§1.1d** · Ç-16·Ç-19·Ç-21·Ç-28 → §9.1/9.2/9.5 · Ç-17·Ç-22·Ç-23·Ç-24·Ç-25·Ç-26·Ç-27
→ §8'in kapsam-dışı gerekçeleri · Ç-18 *(tek ampirik kapı en sonda)* → 🔴 **bu belgenin
`G0`'ı tam bunun düzeltmesidir** · Ç-20 → §9.1.

### 15.2 · Denetim belgesi — `B1…B9` · `KN-1…7` · `Ö1…Ö12` · `KÇ-0…7`

| Grup | Durum |
|---|---|
| **B1 · B2 · B3** *(0/41 cevap · 11/42 atılan · %68,8 fiil ölümü)* | → **§1.1b**'de sayılarıyla; çözümü **G3** |
| **B4 · B5 · B6** *(ay çekimi · çift sahip · elle sözlük)* | ✅ **KÖK-7a/7c/7d turunda kapandı** (`KÇ-2`·`KÇ-4`) |
| **B7** *(belirsizlik biliniyor, chip'e çevrilmiyor)* | ✅ `KÇ-6` — `belirsizlik_chipi.py` |
| **B8 · B9** *(canlı sessiz-yanlış)* | ⚠ **beyan-açık** olarak kapandı (`uyum.py`), fail-closed değil → **§4.4b**'de sapma kaydı; `G1` tamamlıyor |
| **KN-1…KN-7** | `KN-1`·`KN-2`·`KN-3`·`KN-5`·`KN-6` ✅ KÖK turu · **`KN-4`** *(uyum denetimi yok)* → `uyum.py` ⚠ beyan-açık · **`KN-7`** *("yokluk, anlamadım diye raporlanıyor")* → 🔴 **`G8`** |
| **Ö1 · Ö2** *(fiil/soru kelimesi · ay çekimi)* | ✅ KÖK-7 turunda kapandı |
| **Ö3** *(korpus yeniden koşulsun)* | ✅ korpus %95,1 |
| **Ö4 · Ö5** *(bayrak A/B'leri)* | 🔴 **Ö4 iptal** — `prompt_enhancer` mimari olarak kapandı (**§1.1d**). **Ö5** *(netleştirme önceliği)* → **§2.4**'te askıya alındı, `G0`'ın aletinde ölçülecek |
| **Ö6** *(hafıza kaydı düzeltilsin)* | ✅ hafıza dosyası güncel |
| **Ö7** *(senaryo üreteci `_norm` kusuru)* | ⚪ Mutfak/lab işi — §11.2'ye komşu, bu fazın kapsamı dışı |
| **Ö8** | ⚠ beyan-açık indi → §4.4b |
| **Ö9 · Ö11 · Ö12** | → **G6**'nın adım tablosunda birebir |
| **Ö10** *(`göre` ayrımı)* | ⚪ Mutfak — §11.2; ⚠ üç kez ısırmış tuzak, uyarısıyla kayıtlı |
| **KÇ-0…KÇ-7** | → **§4.4b**'de tam durum tablosu; tek açık olan **`KÇ-7` = `G8`** |

### 15.3 · §G maddeleri ve **kabul rejimi** — uzlaştırma

| §G | Bu belgede |
|---|---|
| `AJ0` | **G3** *(davranış yarısı, doğru ortamda)* |
| `AJ0b` | **G2** — ⚠ *"sıfırdan yazmıyoruz"* argümanı **çürüdü** (§4.2) |
| `AJ1` | **G4** |
| `AJ2` | **G6** — `blend` **geri alındı** |
| `AJ3` · `AJ3b` · `AJ4` · `AJ5` · `AJ5b` · `AJ6` | **v2** → §8 + §15.1 |

**🔴 §G.6'nın kabul rejimi — bu belge onu DEĞİŞTİRİYOR, ve gerekçesi yazılı:**

| §G.6 kuralı | Bu belge | Gerekçe |
|---|---|---|
| **G.6a** *"kazancı ölçen alet gerilemeyi ölçenden farklı olmalı"* | ✅ **AYNEN alındı** — §2.3'ün temeli | Doğru kural |
| **G.6b** *dört-yönlü VE* | ⚠ **GEVŞETİLDİ** → §2.3 | Dördünden biri *"korpus gerilemesin"*di; §2 onu **kapsam payında** kaldırdı, **doğrulukta** korudu |
| **G.6f/(a)** *`N`=3: B, A'nın kırmızılarından ≥3'ünü yeşile çevirmeli* | ✅ korunur — ama **taban yeniden ölçülür** (`G0`) | Belgenin kendi kuralı: *"payda değişince taban yeniden ölçülür"*; ⚠ üç farklı `deneyim.py` tabanı var ve `AJ0b`'nin kapısı **bayat olanı** gösteriyor |
| **G.6f/(c)** *GEÇTİ · KALDI · ⊘* | ✅ **AYNEN** — `G0.5`'te kod düzeyinde | — |
| **G.6d** *T1 klasik · T2 canlı · T3 vaka; üçü yeşil olmadan `beta` yok* | ✅ korunur; **§12.2b'nin D/K/C ekseniyle ÖRTÜŞÜR** | T1≈D · T2≈C · T3≈vaka; K katmanı **yeni** ve T1 ile T2 arasını dolduruyor |
| **G.6e** *VK-1…VK-6* | ⚠ **Tablosu BAYAT** — kendi ölçüm kutusu üç satırını çürütüyor, tablo düzeltilmemiş | `G0`'da yeniden ölçülür; düz okuyan geliştirici **üç yanlış bilgi alır** |

### 15.4 · 🔴 KARŞI KANIT — tezimizi ZAYIFLATAN bulgular

> *"Objektif ol, olumlayıcı olma."* Bu bölüm, bu belgenin **kendi tezine karşı** bulduğu
> kanıtları taşır. Hiçbiri kararı değiştirmedi, ama **hiçbiri gizlenmedi**.

| # | Karşı kanıt | Etkisi |
|---|---|---|
| **1** | **Semantik katmanın avantajı KÜÇÜLÜYOR.** dbt: 2023'te +27,8 puan → 2026'da **+8,2 puan**; ham text-to-SQL üç yılda %32,7→%64,5 | Tezimizi çürütmüyor ama *"semantik katman şart"* argümanının **ortalama doğruluk** kanadı zayıflıyor. Sağ kalan gerekçe: **sesli başarısızlık** ve **kapsam-içi %100** |
| **2** | **"Schema Linking'in Ölümü"** (arXiv 2408.07702): güçlü akıl yürüten modellerde şema **daraltmak** eskisi kadar önemli değil; tüm şemayı verip modele bırakmak SOTA vermiş | §7.1'in budama tasarımına **doğrudan bir itiraz**. ⚠ Kayda geçer: budamanın kazancı **ölçülmeden** varsayılmayacak |
| **3** | **Spider 2.0-DBT** *(metrik katmanına en yakın alt görev)*: en yüksek skor yalnız **%65,6** | *"Semantik katman işi çözer"* anlatısının en zayıf noktası: **metrik-bitişik görev en zor olanı** |
| **4** | **Kıyasların kendisi bozuk:** BIRD Mini-Dev'de **%52,8**, Spider 2.0-Snow'da **%66,1** açıklama hatası; düzeltince sıralamalar 9 basamak oynuyor | 🔴 Bu bölümdeki **hiçbir yüzde** dar hata payıyla okunmamalı — **kendi lehimize olanlar dâhil** |
| **5** | **Netleştirme bedava değil:** Wang & Ai (TOIS 2022) *"sormak güvenli alternatif değildir"*; Amazon ASRU 2021 aşırı sormanın UX'i bozduğunu ölçmüş | `G1.4c`'nin marjin tabanı **veriden** seçilecek; §5/4'e **tavan** konuldu |
| **6** | **"Varsayımı beyan et" ile "önce sor" arasında kontrollü çalışma YOK** | `G1`'in dayanağı 1991 tarihli bir teori (Clark & Brennan) + `uyum.py`'nin mevcut kararı. **Bir yargı, kanıt değil** — ve `lab/garson.py` bunu ölçebilecek konumda |
| **7** | **LLM'in Türkçe morfolojisi** yalnız **en zor uçta** ölçülmüş (türetimsel bileşimsellik); *"bilinen ada hâl eki"* **hiçbir kıyasla ölçülmemiş** | `G7`'nin gerekçesi bu yüzden *"LLM beceremiyor"* değil, **"kapalı alanda deterministik daha ucuz"** |
| **8** | **Kısıtlı çözümlemenin akıl yürütmeye zararı tartışmalı:** *"Let Me Speak Freely"* büyük düşüşler ölçmüş; dottxt'in yeniden koşumu **tersini** bulmuş — fark, *gerçek gramer kısıtı* ile *gevşek JSON-modu* arasında | §7.4'ün (c) kararını **destekler**: `oneOf`'u koruyup serbest-JSON kullanmak, *gevşek JSON-modu* riskine girmez çünkü doğrulayıcı `parse_cube_query` |
| **9** | **Kimsenin sayısal-kopya kısıtı yok:** Outlines/XGrammar/llguidance hiçbiri *"rakamlar yalnız kaynaktan"* kısıtı sunmuyor; Guardrails/NeMo **cümle düzeyinde NLI** yapıyor, **sayı düzeyinde değil** | `G5`'in iki katmanı **satın alınamaz**, yazılacak. Fiyat kalemi buna göre |
| **10** | **Ölçek tavanları gerçek:** Genie **30 tablo / 20 soru-dk**; Looker CA **8192 token çıktı** + *"büyük veri akıl yürütmeyi bozar"*; dbt MCP *"araç seçimi kusurlu, gereksiz çağrı döngüsüne giriyor"* | Bizim de bir tavanımız olacak; `G0`'ın telemetrisi onu **ölçmeli**, varsaymamalı |
| **11** | **MIT NANDA *"%95 pilot başarısız"*** | ⚪ **KULLANILMADI** — 52 görüşme + 153 konferans anketi, hakemsiz, yöntemi birden çok bağımsız eleştirmen tarafından çürütülmüş. *Lehimize bir sayı olsa da kullanılmadı* |
| **12** | **Gartner %30/%40 terk tahminleri** | ⚪ **KULLANILMADI** — bunlar **tahmin**, ölçüm değil |

### 15.5 · Ölü kontroller ve kapalı bayraklar — **karar tablosu**

> Envanterde bulunan ama bir faza bağlanmamış her bayrak/kontrol burada karara bağlandı.
> *Karara bağlanmamış bayrak bırakmak, bu belgenin kendi §13.4'ünü ihlal ederdi.*

| Kontrol / bayrak | Durum | **KARAR** |
|---|---|---|
| `hizli_derin` (`mod` anahtarı) | UI'da var, sunucu **yok sayıyor** | 🔴 **`G0.14`: ya bağlanır ya UI'dan KALDIRILIR.** Çalışıyormuş gibi görünen ölü kontrol, garson fazında **ürün kusurudur** |
| `ask_async_discovery` (SSE) | Yazılı, kapalı | → **`G5.10`**'da açılır *(anlatının akması)* |
| `llm_sema_kisitli` | `beta` ama **NO-OP** | → **§7.4**; `G0.13`'te `MIMARI.md`'ye kaydı |
| `prompt_enhancer` | `off` | 🔴 **Kalıcı `off`** — mimari gerekçe **§1.1d**; `features.yml` yorumu değişir |
| `netlestirme_onceligi` | `off`, ölçüm tartışmalı | → **§2.4** askıda; `G1.4c` sonrası yeniden ölçülür |
| `tur_takip` (6. tür) · `tur_paylas` (7. tür) | Motorları **var**, bayrak `off` | ⚪ **Bu fazda AÇILMAZ** — ikisi de **eylem** türü (zamanla/paylaş), garsonun *konuşma* işi değil. `onay_akisi` ile birlikte **v2**. *Gerekçe yazıldı ki "unutuldu" sanılmasın* |
| `agent_plan_secimi` | `off`, bloklayıcısı (`0.22`) **inmiş** | ⚪ v2 — ama ⚠ **YAML'deki gerekçe bayat**; `G0.13`'te düzeltilir |
| `threaded_chat` | `off` | ⚪ Kapsam dışı — büyük UX değişikliği, garson tezine bağlı değil |
| `t2_anlatici` | `off` | → **`G5`** |
| `capa_zinciri` · `metrik_kaydi` · `niyet_izi` · `sosyal_sinif` | **açık** | ✅ Garsonun mevcut altyapısı — dokunulmaz |

### 15.6 · Bu belgenin BİLİNEN sınırları

*Kapatılmamış olanı saklamak, §13.8'in ihlali olurdu.*

1. **`G2`'nin büyüklüğü en zayıf yargım** — yeni modül, ve bu turda yeni modül tahminleri yanıldı.
2. **`G5`'in kazancı ölçülmemiş** (§6.19z kotaya çarptı). *"Kazanç yok"* çıkabilir; §13.4 bunu kaldırıyor ama faz umulandan az teslim edebilir.
3. **Kaset (`K`) katmanı bu depoda hiç denenmedi** — VQR deseni benzer, ama kaset **yeni bir alet**; `G0`'da kurulurken sürprizi olabilir.
4. **Marjin tabanı henüz yok** — `G1.4d` onu veriden çıkaracak; çıkmazsa `G1.4c` **inmez** (eşik uydurmak yasak).
5. **OpenRouter'da önbellek davranışı ölçülmedi** — §7.4/3'te sıfır sayıldı.
6. **`§G.6e`'nin VK tablosu bayat** ve bu belge onu düzeltmedi, yalnız **işaretledi** (§15.3).

### 15.7 · 🔴 KOD DENETİMİNİN ÇÜRÜTTÜĞÜ İKİ KENDİ İDDİAM

*Bu belgenin ilk taslağı iki modülü **yok** sayıp sıfırdan planlamıştı. İkisi de **vardı**.*
*Kayda geçmesinin sebebi §13.8 (zan yasağı): bir belgenin en tehlikeli cümlesi, kontrol*
*edilmemiş bir "yok" iddiasıdır — çünkü **ikinci sahip** doğurur.*

| İddiam | Gerçek | Sonuç |
|---|---|---|
| *"Hava boşluğu yok, `app/hava_boslugu.py` yazılacak"* | 🔴 **`app/llm_guard.py::safe_call` VAR** — fail-closed, `_ask`/`_arac_ile`/`_chat`'i sarıyor, `pii.py` tek sahip, değer loglamıyor | `G0b` **genişletmeye** çevrildi; yeni modül **yazılmayacak** |
| *"Kapasite beyanı yok, yeni `kapasite` alanı"* | 🔴 **`app/yetenek.py` VAR** (KÖK-6) — `kapsam_disi()` bağlı (`ask.py:3554`), üç sınır tanıyor | `G8` `Sinir`'i **zenginleştirmeye** çevrildi |

#### Tam tarama — 2026-08-07, kavram bazlı

*İlk iki kaçak sonrası belgedeki **her** "yeni/yok/yazılacak" iddiası kodda arandı —
ada göre değil **kavrama göre**, ve **iki dilde**.*

| İddia | Sonuç |
|---|---|
| `app/iddia.py` — şema iddia kapısı | ✅ **gerçekten yok** |
| `app/diyalog.py` · açık slot | ✅ **gerçekten yok** (`acik_slot\|bekleyen_\|pending_clar` → 0) |
| `app/temellendirme.py` | ⚠ modül yok **ama KURAL VAR** — `soz.py:19` |
| `cube_router.marjin()` | ⚠ isim yok **ama DESEN VAR** — `value_index.py:28 AUTO_MARGIN` |
| `app/ek.py` — ek üretimi | ⚠ üretim yok **ama KURAL SAHİBİ VAR** — `_ek_gecerli` (doğrulama) |
| Kaset / kayıtlı sağlayıcı yanıtı | ✅ **gerçekten yok** (`cassette\|record.*replay\|FakeLlm` → 0) |
| Korunan yayılım / yer tutucu | ✅ **gerçekten yok** *(bulunanlar SQL `{where}` şablonu — farklı şey)* |
| `referans` alanı · `R11` | ✅ **gerçekten yok** *(`katman_b.referans_modeller` farklı şey; `R11` yalnız lab notunda tartışılmış)* |
| `AskResponse.temellendirme` · `.diyalog_durumu` · `.kapasite` | ✅ 3/3 **gerçekten yok** |
| `lab/garson.py` | ✅ yok — ama `deneyim.py` + `konusma_senaryolari.py` **devralınacak** |

#### Ön yüz ve YAML taraması — 2026-08-07

| Alan | Sonuç |
|---|---|
| **44 bileşen** (`src/components/*.tsx`) | ⚠ **İki gerçek isabet:** `Makbuz.tsx:209-213` **`explain.path`'i zaten render ediyor** (`G3.7` → *yeni UI yazma, içeriği zenginleştir*) · `types.ts:99` *"önce ne anladığını söyle"* kuralı ön yüzde de yazılı |
| Kalan aramalar *(slot · kapasite · maskeleme)* | ✅ hepsi **yanlış pozitif** — Türkçe kelime çakışması (`bekleyen` yorumu · `kapasite` kolon sezgisi · paylaşım linkinin `maskelenmiş`i) |
| **74 YAML** (`demo/packs/**`) | ✅ Andığım **7 bayrağın 7'si** tanımlı · yeni iki bayrağım (`diyalog` · `referans_dili`) **yok** — doğru · tek isabet bir **yorum satırı** (*"kapasite kaybı"*) |

🔴 **Ve bir tasarım borcu çıktı:** `AskResponse` bugün **iki** öneri kanalı taşıyor
(`suggestions` · `next_steps`). `G8`'in `onerilen_soru`'su **üçüncüyü açmamalı** —
`G8.2`'de karara bağlanır: ya `next_steps` yeniden kullanılır, ya gerekçesi yazılır.

⚠ **Ve ikisi de aynı sebeple kaçtı:** ajan envanteri (§0) *"garson"* ve *"diyalog"*
anahtar sözcükleriyle tarandı; bu iki modül **güvenlik** ve **kapsam** başlıkları altında
yazılmıştı. 🔴 **Ders `G0`'a bağlandı:** yeni bir modül planlanmadan önce
`ls app/*.py` **tamamı** okunur — 95 modül, arama değil **sayım**.

---

## §16 · KAYNAKÇA

**Semantik katman ↔ doğruluk:** dbt Labs 2026 kıyası (`dbt-labs/dbt-llm-sl-bench`, ACME
Insurance) · Sequeda ve ark., GRADES-NDA 2024 (arXiv:2311.07509) · Cube.dev eşli kıyas
(arXiv:2604.25149) · Spider 2.0, ICLR 2025 (arXiv:2411.07763) · *Pervasive Annotation Errors*
(VLDB/CIDR 2026) — ⚠ BIRD Mini-Dev'de **%52,8**, Spider 2.0-Snow'da **%66,1** açıklama hatası;
**bu alandaki hiçbir nokta tahmini dar hata payıyla okunmamalı**

**Üretim başarısızlıkları:** Anthropic, *How Anthropic enables self-service data analytics*
(2026-06-03) · Stonebraker/Rubicon (RecceHQ, 2026-04-28) · Power BI Copilot resmî sınırlar
(learn.microsoft.com) · Cortex Analyst resmî sınırlar (docs.snowflake.com) · Tableau Ask Data
emeklilik (help.tableau.com) · ThoughtSpot kullanımdan kaldırma (developers.thoughtspot.com)

**Diyalog:** JPMorgan bellek mimarileri (arXiv:2605.26394, ön baskı) · SParC/CoSQL
(yale-lily.github.io/sparc) · AmbiSQL (arXiv:2508.15276) · Kim ve ark., ASRU 2021
(arXiv:2109.12451) · Wang & Ai, ACM TOIS 2022 (arXiv:2201.00235) · *Clarifying the Path to
User Satisfaction*, EACL 2024 (arXiv:2402.01934) · Clark & Brennan 1991 · AMBROSIA (NeurIPS
2024) · PRACTIQ (NAACL 2025)

**Sayı sadakati:** DefAn (arXiv:2406.09155) · *Fact-Consistency Evaluation of Text-to-SQL for
BI* (arXiv:2505.00060) · Huang ve ark., ICLR 2024 (arXiv:2310.01798) · *Proof-Carrying
Numbers* (arXiv:2509.06902) · Tableau Pulse mühendislik yazısı (engineering.salesforce.com)

**Türkçe:** Zemberek `WordGenerator` (github.com/ahmetaa/zemberek-nlp) ·
google-research/turkish-morphology (**arşiv: 2026-04-19**) · Ismayilzada ve ark.
(arXiv:2410.12656) · Cetvel (arXiv:2508.16431)

**Maliyet/gecikme:** Anthropic prompt caching + pricing (platform.claude.com/docs) · OpenAI
prompt caching (developers.openai.com) · DeepSeek (api-docs.deepseek.com) · Artificial
Analysis sağlayıcı sayfaları · XGrammar (arXiv:2411.15100) · JSONSchemaBench
(arXiv:2501.10868)

**Depo içi:** 🔴 `belgeler/denetim/2026-08-05_ANLAMA-KATMANI.md` (1311 satır — **bu fazın
kendi teşhisi**: B1…B9 · KN-1…KN-7 · Ö1…Ö12 · KÇ-0…KÇ-7 · §12'nin iki canlı vakası ·
§14.4'ün mimari kök nedeni) · `backend/MIMARI.md` (§4 · §5 · §6.19z · §7 · §11.6d · `:442` ·
`:1929`) · `backend/CLAUDE.md` (test kapısı politikası + ölçülen fatura) ·
`OPERASYON.md` (§2 döngü · §3 test kapısı · §4 KAT-1…5 · §5 D1…D5 · §6 geliştirme
değişmezleri · §9 commit · §10 sıra) · `~/.claude/plans/DIMA-V1-YOL-HARITASI.md` §G
(`YH:771-1680`) · `dima v2 v3 için mimari karar (1).md` (danışman girdisi — denetimi §9'da)

---

### 📊 DURUM — 2026-08-07 · adım adım DOĞRULANDI

| | adım |
|---|---|
| ✅ **indi** | **113** |
| ⊘ **bilerek ertelendi** *(gerekçesi satırında)* | **3** |

⚠ Bu tablo **beyan değil ölçüm**: her adımın kanıtı kaynakta arandı (dosya · fonksiyon ·
kapı · bayrak), *"belgede yazıyor"* kanıt sayılmadı. Tarama üç kez yanlış pozitif verdi
(`G0.4` · `G4.4` · `G7.6` — dedektör kelimeyi aradı, kod başka ad kullanıyordu) ve
düzeltildi. *Bir denetim aracının kendisi de ölçülmeden güvenilmez.*

🔴 **Ve tarama üç GERÇEK eksik buldu** — hepsi bu turda kapatıldı:
* `G8.4` — `yetenek` beyanı `iddia` kapısını **atlıyordu**; dahası ikisi aynı katalog
  taramasının **iki sahibiydi** ve `iddia`'nınki gerçek şema şeklini **eksik okuyordu**
  (`dimension_labels` diye var olmayan bir alan) → fail-closed bir kapı **kör** olmuştu.
* `G6.11` — failover'da şema garantisinin kaybı makbuza **yazılmıyordu**.
* `G6.8` — `blend` indikten sonra *"birleştirmiyorum"* diyen sınır beyanı **bayatlamıştı**.
  *Yanlış bir «yapamam», yanlış bir «yapabilirim» kadar pahalıdır.*


---

## §AJ2 · CANLI DENETİM BULGUSU — *en çok güvendiğimiz basamak, en kör hâliyle koşuyordu*

> **Kaynak:** `belgeler/denetim/2026-08-07_CANLI-ARIZA-TESHISI.md` (canlı ajan denetimi),
> **ve iddianın her sayısı yerinde yeniden ölçüldü** — biri düzeltildi.

### Bulgu

`route()` zengin bir Türkçe eşanlam katmanı kullanıyor: `oee` → *"verim"*, *"randiman"*,
*"performans"*; `ort_oee`'nin sekiz sinonimi var. Bu katman şemada **beyan edilmiş**.

⊙ **LLM'e giden katalogda hiçbiri yoktu.** Ölçüldü: `verim` **0 kez** · `randiman` **0** ·
`verimlilik` **0** · `hasılat` **0** · `bordro` **0**. 23 cube'un **23'ünde** `synonyms`
**ve** `measure_synonyms` beyan edilmiş olmasına rağmen.

| | eşanlam katmanı |
|---|---|
| `route()` — *en az güvendiğimiz basamak* | ✅ **tam** |
| LLM — 🔴 *en çok güvendiğimiz basamak* | 🔴 **HİÇ** |

Canlı sonucu: *"verimlilik"* sorusunda **9/9 Intent çağrısı `{"cube":null}`** — oylama
uyuşmazlığı değil, **aday yokluğu**. Model reddetti çünkü elindeki listede o kelime yoktu.

🔴 Bu, kullanıcının bu fazdaki en net talimatıyla doğrudan çelişiyordu:
> *"burada asıl güvendiğimiz llm… sistemi burada deterministiğe yıkamayız."*

### ⚠ `ADR-0008` ile çelişmiyor — tam tersi

Yasak olan **sözlük icat etmek**tir. Burada yeni liste yazılmıyor; şemanın **zaten beyan
ettiği** liste ikinci tüketicisine gösteriliyor.
*Bir bilgiyi beyan edip tüketicilerinden birine göstermemek, onu iki kez tanımlamaya
davettir — çünkü göremeyen taraf er ya da geç kendi listesini yazar.*

### 🔴 AJANIN SAYISI DÜZELTİLDİ

Denetim maliyeti *"+2.192 token (%54)"* diye raporladı. Yerinde ölçüm:

| kapsam | katalog | oran |
|---|---|---|
| bugünkü (sözlüksüz) | 12.115 karakter | 1,00× |
| + cube sinonimleri | 14.709 | 1,21× |
| **+ ölçü sinonimleri** *(seçilen)* | **23.417** | **1,93×** |
| + boyut sinonimleri | 29.889 | **2,47×** |

*Bir maliyet tahmini, ölçülene kadar bir maliyet değildir.*

**Kapsam kararı:** boyut sinonimleri **dışarıda** — maliyetin %30'unu yiyor ama ölçülen
kusuru (**cube seçimi**) çözmüyor; boyut eşleştirmesi `route()`'un güçlü olduğu yer ve
model boyut **adlarını** zaten görüyor.

### ADIMLAR

| # | Adım | Dosya / iş | ✅ Bitti kontrolü |
|---|---|---|---|
| **AJ2.1** ✅ | Ölçüm önce | Katalogda eşanlam **var mı** — kapının konusu taze mi | ✅ 23/23 beyanlı, katalogda 0 |
| **AJ2.2** ✅ | Modül | `build_catalog` → `app/katalog_metni.py` *(`cube_router` tavanda; ve *"LLM'in gördüğü metin"* onun sorusu değil)* | ✅ Tavan **1760 → 1739** indi |
| **AJ2.3** ✅ | Sözlük eki | cube + ölçü sinonimleri, `«…»` içinde, **dedup**'lu | ✅ `test_ESANLAMLAR_ARTIK_KATALOGDA` |
| **AJ2.4** ✅ | Maliyet kapısı | Oran bandı **ölçümün etrafına** kondu (1,5–2,1×) | ✅ *"sınırı ölçüye çekmek ≠ ölçüyü sınıra çekmek"* |
| **AJ2.5** ✅ | Kapsam kararı | Boyut sinonimleri dışarıda — **kaynak düzeyinde** kilitli | ✅ Kapı iki kez yanlış yere baktı, kaydı yazılı |
| **AJ2.6** ✅ | Tek çözüm noktası | `catalog_text` **dört** yerde üretiliyor → hepsi `metin_ve_indeks`'ten | ✅ `test_BAYRAGI_TEK_YERDE_COZUYORUZ` |
| **AJ2.7** ✅ | Bayrak | `katalog_sozlugu: beta` — kapalıyken metin **bayt bayt bugünkü** | ✅ `KURAL B` |
| **AJ2.8** 🔴 | **Ölçüm borcu** | Kazanç **gerçek sağlayıcı** ister; `eval --slice llm` bugün **4 vaka** | ⊘ `G3.2` ile **aynı** alet sorunu |
| **AJ2.9** 🔴 | **Önbellek borcu** | Sabit önek → `B6` (üç katmanlı önek) ödendiğinde maliyet tekrar etmez | ⊘ Bu modül `B6`'nın **ilk müşterisi** |

### Denetimin öteki iki bulgusu — akıbetleri

| # | bulgu | akıbet |
|---|---|---|
| **#2** | Anlatı merdiveninde deterministik ilk basamak yok | ⊘ `G5.10`'da ölçüldü: `llm.py`'de **akış yok** ve guard cümle bütünlüğü istiyor. Şablon basamağı ayrı bir iştir — faz `S` |
| **#3** | Takip turunda 500 | ⊘ **Backend'den çıkmamış**: `restarts=0`, erişim logunda **sıfır 5xx**, 22 dk hiç istek yok. Next rewrite-proxy üretmiş; `apiClient`'ta **timeout tanımsız** (39,4 sn'lik bir cevap ölçüldü) → ön yüz işi |

---

## §AJ3 · LLM NİYETİ NEDEN SEÇEMİYOR — üç kusur, bir ÖLÇÜM TUZAĞI, bir çürütülen öneri

> **Kaynak:** canlı denetim ajanı (iki tur, ikincisi **kendi önerisini çürüterek**).
> Her sayı yerinde doğrulandı; ikisi **düzeltildi**.

### Önce: merdiven darboğaz DEĞİL

İlk tur *"netleştirme/sınır dalları LLM'i kesiyor"* demişti. **Ölçüldü, öyle değil**
(42 gerçek soru): `route()` çözdü **%0** · netleştirme kesti **%0** · yetenek sınırı
kesti **%2,4** · **LLM'e gidiyor %97,6**. Ve `netlestirme_onceligi` bugün `off`.

🔴 Yani soru LLM'e **ulaşıyor** ve LLM **reddediyor** (canlı: 9/9 `{"cube":null}`).
*Elimizde "LLM yanlış anlıyor" diye bir kanıt yok; elimizdeki kanıt "LLM'in konuşmasına
izin verilmiyor".*

### 🔴 ÇÜRÜTÜLEN ÖNERİ — ve neden kaydı değerli

İkinci tur *"sistemin kendi anladığını da gönder"* diye öneri getirdi (`route()`'un
kısmi tahmini: *"randiman = ort_oee, takıldığım kelime `kotu`"*). Sonra **kendi ölçtü**:

| | vaka | oran |
|---|---|---|
| kısmi tahmin **hiç yok** | 31 | **%74** |
| tahmin var, yer gerçeği başka cube diyor | 9 | %21 |
| 🔴 tahmin var ve **YANLIŞ** | 2 | **%18'i (11 içinde)** |

`ne kadar fire verdik` → sistem `oee.toplam_fire_kg` diyor, doğrusu `parti`. Bunu modele
*"ben şunu anladım"* diye vermek, onu **ölçülmüş bir hataya çapalamak** olurdu.

> *Bir tahmini paylaşmak, onu doğrulamak değil yaymaktır.*

⚠ Ayrım net: **tahmin** gönderilmez, **olgu** gönderilir. Konuşma geçmişi · önceki
`cube_query` · diyalog belleği tahmin değildir ve **bugün hiç gitmiyor** —
`select_cube` çağrısı `(system=katalog, user=ham soru)`'dan ibaret, yani çok turlu bir
konuşmada model **her turda sıfırdan** başlıyor.

### 🔴🔴 EN AĞIR UYARI: ölçüm korpusu bu mimarinin TERSİNİ kodluyor

42 vakanın kabul ölçütleri: `netlestirme` **38** · `durust_ret` **19** · `dogru` **22** —
ve 🔴 **20/42'sinde cevap vermek YASAK**:

```
"işler nasıl gidiyor"        → kabul=[netlestirme, durust_ret]
                               yasak="rastgele ölçü seçip kendinden emin sayı vermek"
"bu ay iyi miyiz kötü müyüz" → yasak="iyi/kötü yargısını bir eşik uydurarak vermek"
```

🔴 **Mimariyi *"LLM niyeti seçsin"* yönünde değiştirirsen, korpus her iyileşmeyi
GERİLEME diye raporlar.** Bu depoda tam bu sınıftan bir olay yaşandı (`gitas` düştü,
doğruluk **yükseldi**). Karar verilmeden **önce** kapatılması gereken şey budur.

### ADIMLAR

| # | Adım | Durum |
|---|---|---|
| **AJ3.1** ✅ | 🔴 **Oy paydası** — `{cube:null}` oyları paydadan düşüyordu: 1 cevap + 2 *"bilmiyorum"* → uyum **1,0**. *Şüphe en yüksekken sistem en emin görünüyordu*, ve `MIMARI` bunu açıkça yasaklıyor (*"kalibre edilmemiş sayı bir güven değil bir süstür"*) | ✅ Mekanizma indi, bayrak **`off`** — eşik aynı orandan geçiyor, kapsam bedeli **ölçülemez** (`eval --slice llm` 4 vaka). *Ölçülemeyen bir takası varsayılan yapmak, kullanıcı adına karar vermektir* |
| **AJ3.2** ✅ | 🔴 **YTD sessiz-yanlışı** — *"yılbaşından bugüne"* → `gte 2026-08-07` (**bugünden İLERİYE**). `bugune` çekimi `bugun` kuralına takılıyordu; rozet `◆ CUBE`, güven yüksek, sayı **yanlış** | ✅ `mali_takvim.yil_basi` + `lte bugün`. Yeni sözlük YOK — var olan sahip **bağlandı** |
| **AJ3.3** 🔴 | **İfade boşluğu** — taze yolda dönem yazılacak **alan yok** (`period_expr` yalnız takip yolunda). Model *"geçen çeyrek"*i hiçbir yere koyamıyor; tutarlı tek davranışı dönemi düşürmek ya da `{cube:null}` | ⊘ Kazancı **bugünkü aletlerle ölçülemez** |
| **AJ3.4** 🔴 | **Red yanlılığı** — prompt *"karmaşıksa **KESİNLİKLE** null"* diyor; *"yorumlamak senin işin"* diyen tek satır yok, şemada red **ilk** dal. Model üç kez reddetmeye davet ediliyor, bir kez bile yorumlamaya değil | ⊘ aynı |
| **AJ3.5** 🔴 | **Sıfır örnek** — `refine_cube`'de 4 örnek var, `select_cube`'de **0**. Dar düzenleme yapana örnek verilmiş, doğal dili yorumlayana verilmemiş | ⊘ aynı |
| **AJ3.6** 🔴 | **İki red aynı koda düşüyor** — `cq is None` hem *"model reddetti"* hem *"model uydurdu, beyaz liste düşürdü"* demek. Hangisinin kaç kez olduğu **bilinmiyor** → 3.3–3.5'in hangisinin işe yaradığı **ölçülemez** | ⊘ **3.3–3.5'in ön koşulu** |
| **AJ3.7** 🔴 | **Olgu devri** — konuşma geçmişi · önceki `cube_query` · diyalog belleği `select_cube`'e **hiç** gitmiyor. Bunlar tahmin değil **olgu**, çapa riski yok | ⊘ |
| **AJ3.8** 🔴🔴 | **ÖLÇÜM TUZAĞI** — korpusun 20/42 vakasında cevap vermek **yasak**. Mimari değişirse korpus iyileşmeyi **gerileme** sayar | ⊘ **Hepsinin üstünde duran ön koşul** |

⚠ `AJ3.3…3.8`'in ortak engeli tektir ve bu belgede üçüncü kez yazılıyor (`G3.2` · `§AJ2` ·
burada): **`eval --slice llm` 4 vaka**, `nl_corpus` tanımı gereği `rule` sağlayıcıyla
koşuyor. Bu maddeleri **uygulamak kolay, doğru olduğunu göstermek imkânsız.**

*Bir düzeltmeyi ölçemeden uygulamak, kusurun yerini değiştirmenin pahalı bir biçimidir.*

---

## KAPANIŞ — BU FAZIN TEK CÜMLESİ

> Mutfak, **dünyanın en katı ucunda** kuruldu: on üründen dokuzunun taklit etmeye çalıştığı
> deterministik derleme katmanı bizde en baştan var, ve sektörün *"asıl kazanç"* dediği şey
> — **sesli başarısızlık** — bizim varsayılan davranışımız.
>
> Eksik olan, o sesin **anlaşılır** olması. Garson bunu yapar: siparişi tekrarlar, emin
> değilse sorar, sorduğunu hatırlar, düzeltilir, tabağı anlatır, menüyü bilir.
>
> Ve hiçbiri sayıya dokunmaz.

**Sıra:** `G0` (alet) → 🔴 `G0b` (hava boşluğu) → `G1` (temellendirme) →
`G2` (bellek) → `G3` (merdiven) →
`G4` (iddia) → `G5` (anlatıcı) → `G8` (menü) ‖ `G6` (kıyas cebiri) ‖ `G7` (ek motoru)

🔴 **`G0` inmeden hiçbir kod yazılmaz.** Ölçemediğimiz bir şeyi geliştiremeyiz — ve bu fazın
tamamı, tam olarak bunun bir kez daha olmasını engellemek için bu sırayla dizildi.
