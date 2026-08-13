<!-- 🅦 Bu bir ÖZET DEĞİL, bir TESLİM TUTANAĞIDIR. `ONGORU-DURUM.md` operasyonun
     günlüğüdür (bölüm bölüm, gerekçeleriyle); bu dosya devralanın sorduğu üç soruya
     cevap verir: NE ÇALIŞIYOR · NE ÇALIŞMIYOR VE NEDEN · NEREYE BASARSAM KIRILIR. -->

# DİMA — Öngörü Katmanı / **Rol Değişikliği** Devir Tutanağı (13 Ağustos 2026)

**Kod tabanı:** `778211f` · **Canlı imaj:** `dima-backend-temiz:s39` (kap `dima-oneri-8002`, `:8002`)
**Aralık:** `e521e46..778211f` — **23 commit**, `§63`–`§85`
**Giriş noktası:** kök [`README.md`](../../README.md) · **belge kuralı:** [`belgeler/00-INDEKS.md`](../00-INDEKS.md)

> 🔴 **İşin tanımı bir arayüz işi değildi.** Planın başlığı: *«route ve garson, KARAR
> VERİCİ olmaktan çıkıp **TAHMİNCİ** oluyor … **kullanıcı KARARI VERİR (bir tık)**»*
> (`§3.1`). Bu operasyon o rol değişikliğini uçtan uca kurdu.

---

## §1 — NE ÇALIŞIYOR (canlı doğrulandı)

| yetenek | uç / yer | kanıt |
|---|---|---|
| Çok adımlı plan **koşmadan** önizlenir | `POST /ask` · `POST /oneri/makro` | `source="onizleme"` · 5 adım · `gecerli=True` |
| Onaylanan plan **birebir** koşar, ⊘ LLM | 🆕 `POST /plan/kos` | **1,14 sn** · 4 bölüm · 6 satır |
| Garson **kararsızsa** koşmaz, onaya düşer | `plan_tuketici.kararsiz_onizleme` | canlı: `uyum %67` → `onizleme` + pill'ler |
| Teklif **pill satırı** olarak okunur | `niyet.fisten` → `pill.pillerden` → `PillSatiri` | canlı: `['performans','makine kırılımı']` |
| Bütçe **ekranda** | `plan_tuketici.onizleme_notu` | *«5 adım (tavan 12) · 2 sorgu (bütçe 8)»* |
| Bütçe aşımı **koşumdan önce** ve iki sınır ayrı | aynı yer | *«İki ayrı sınır var…»* |
| Hasat döngüsü (tıklama sinyali) | `POST /oneri/tik` | `zayif` / `guclu` / `negatif`, üçü de kaydedildi |
| Isınma penceresinde uç **bloke olmuyor** | `oneri._insa_hakki` (`threading.local`) | `0,5 sn` (önce: **90 sn'de HTTP=000**) |

**Korpus (13 Ağustos):** erişim **83/69/68/72** · doğru-cube **%95,6** (taban %94,4) ·
semantik **558/591 = %94,4** (taban %93,5) · **payda kırpılmadı** 🅜.
⊙ Yani on bölümlük iş `route()` davranışını **bozmadı**.

---

## §2 — NE **YAPILMADI** VE NEDEN 🅖

| madde | durum | gerekçe |
|---|---|---|
| **FE ekran doğrulaması** | 🔴 **YAPILAMADI** | `localhost:3000` **dört tur** boyunca `HTTP 000`. Zincir kodda bağlı ve kapılı (`test_onizleme_zinciri_kopuk_degil.py`) — ama *bir zincirin kodda bağlı olması ekranda göründüğünün kanıtı değildir* 🆘. **Devralanın ilk işi budur.** |
| **Fiil tespiti** (`§33` s.11'in *«∨ fiil»* yarısı) | ⊘ **ölçüldü, reddedildi** | İki aday da yanlış pozitif üretiyor: `fiil_bicimi_mi` → **`oran`**'ı fiil sanıyor ve emir kipini hiç görmüyor; kapalı fiil + `_syn_hit` → *«müşteri kırılımı»* → `KIR`. Üçüncü yol sözcük listesi (㊱ + *«route'a dil kuralı ekleme»* yasağı), dördüncüsü tuş başına LLM (`E-8`). Kapı: `test_fiil_tespiti_olculdu.py` |
| **`ε` karıştırma** (`FAZ 8.3`) | ⊘ **bilerek ertelendi** | Faydası ancak tıklama verisiyle ölçülür; ölçmeden konan `ε` listeyi bozar, karşılığında **sayı üretmez** 🆕. Bekçisi: `test_EPSILON_ERTELEMESI_HALA_GECERLI` |
| **Adım/pill düzenleme** | ⊘ **planın kendi sınırı** | Plan `1840` ve `2150`: *«`Niyet` aynası; iddiayı kanıtlamıyor · **en pahalı FE işi**»*. Bir zaman *«borç»* diye yazılmıştı — **yanlıştı** ㊸ |
| `lab/sozluk_hasadi.py` çıktısı | ⊘ **görülmedi** | `interaction_log` okuması bu operasyonda yasaklı 🅛. Araç hazır ve kapılı; **çıktısını görmedim** 🅢 |

---

## §3 — ✅ **KAPANDI: yazıyla yazılmış sayı (K5)** — `§74`, canlı `s36`

<!-- ⑳ Bu bölüm bir tur boyunca *«devralanın ilk işi»* diyordu; iş **aynı gün** bitti.
     Bayat bir tutanak, yanlış bir tutanaktır 🅦 — bu yüzden düzeltildi, silinmedi. -->

Ölçülen kusur (`s35`) ve düzeltilmiş hâli (`s36`):

```
önce:  «son üç ayda fire»  → source=cube+llm · dönem 2025-06-01 → 2026-06-30  🔴 13 AY
sonra: «son üç ayda fire»  → source=cube     · dönem 2026-05-13 →             ✅ rakamlıyla BİREBİR
```

Küme `donem_capasi.SAYI_SOZCUKLERI` (`bir…on iki`, **kapalı ve sonlu**) + `sayi_coz`
(tek okuma noktası); `cube_router` yalnız **kalıba** koyar (`_REL_DATE` **ve** komşusu
`_PERIOD_RANGE_REF` ⑯). ⚠ `«bir ay»` belirsizliği bir eşikle değil **kalıbın şekliyle**
dışarıda: sözcük ancak `son <SAYI> <birim>` üçlüsünün **ortasında** eşleşir. Canlıda o
soru `source=onizleme` dönüyor — sistem tahmin etmiyor, **soruyor**.

**Kapı:** `test_yaziyla_sayi_donemi.py` (6 yüklem, mutasyonla kanıtlı) · **korpus birebir
aynı** (`83/69/68/72 · %95,6 · 558/591`).

---

## §4 — HANGİ KAPI NEYİ SAVUNUYOR (bu operasyonda yazılan **11 yeni** kapı)

| kapı | savunduğu |
|---|---|
| `test_plan_onizleme.py` | çok adım onaysız **koşmaz** · adımlar taşınır · onaylı **koşar** 🆃 · geçersiz plan da **gösterilir** |
| `test_garson_plani_onaysiz_kosmaz.py` | merdivende onay · plan cevaba iliştirilir · `KURAL B` · bayrağın **tek sahibi** · onay yolunda **0 LLM** |
| `test_kararsiz_garson_onaya_duser.py` | `uyum<1` → onaya · 🆃 oy birliğinde **koşar** · `k≤1`'de karar yok |
| `test_teklif_pilleri.py` | fişten niyet · dönem sınırı **varlık pill'i olmaz** ⑯ · gerçek şemayla (🅡) |
| `test_butce_gorunur.py` · `test_iki_ayri_sinir.py` | bütçe görünür · sayımın **tek sahibi** · **iki ayrı sınır** (kullanıcı kararı, `§70`) |
| `test_kosum_notu_cumledir.py` | `note` bir **cümle**, koşucu iç listesi değil |
| `test_onizleme_yuzu.py` · `test_onizleme_zinciri_kopuk_degil.py` | önizlemenin **yüzü** ve **zinciri** (bu operasyonda zincir **iki kez** koptu 🆘) |
| `test_soguk_pencere_bloke_etmez.py` | ısınmada istek **atlar** (inşa hakkı ipliğe ait) |
| `test_olcu_pill_etiketi.py` | küp adı **ayırt ediyorsa** yazılır |
| `test_yazma_fiili_kapsam_disi.py` | 15 fiilin **0'ı yazıyor** — küme değişirse `§28.3.4` kararı **yeniden** sorulur ㉕ |
| `test_fiil_tespiti_olculdu.py` · `test_faz_kapanisi.py` | reddedilen ölçüm ve *«kapandı»* beyanı **donduruldu** |

---

## §5 — NEREYE BASARSAN KIRILIR ⚠

* **`AZAMI_SORGU=8` ↔ `AZAMI_ADIM=12`** — tutarsız **görünür ama kullanıcı kararıdır**
  (`§70`: *«kalsın, yalnız beyan düzelsin»*) ve `test_iki_ayri_sinir.py`'ye bağlıdır.
  Hizalamak **karar gerektirir**, refaktör değildir.
* **`page.tsx` · `ask()` · `lib/types.ts` tavana dayalı** — her yeni satır gerekçeli bir
  `MUAFIYET` ister; doğru çözüm **tavansız bir modüle çıkarmaktır** (`lib/onizleme.ts`
  böyle doğdu).
* **`niyet.py` bir çatıdır, kalıp sahibi değil** — bir `re.compile` eklersen
  `test_YENI_DILBILIM_YAZILMADI` kırmızı verir ve **haklıdır**.
* **`schema["cubes"]` bir LİSTEDİR** ⑤ — sözlük sanan kod dış `except`'e yakalanır ve
  *«koşar, log basar, hiçbir şey yapmaz»* 🅯 hâline düşer (bu operasyonda **oldu**).
* **Isınma ~50 sn** — o pencerede `/oneri` **leksik** cevap verir; bu bir arıza değil.

---

## §6 — ÖLÇÜLÜP **KAPATILAN** LİSTE SATIRLARI (borç değil) 🆞

`§73`'te sınıflanan kalemler `§75`'te **ölçüldü**; ikisi sayıyla kapandı:

| kalem | ölçüm | sonuç |
|---|---|---|
| `FAZ 0` paydası 🆉 | `VAKALAR` **38** üye (`GURULTU` 1) → **payda 37** | ✅ planın istediği aralıkta (*«30–40 gerçek iş ifadesi»*) |
| ölçüm aracı | üç ayak ölçüyordu (`leksik`·`vektor`·`birlesik`=**max**), **ürünün RRF'ini ölçmüyordu** 🆆 | ✅ `§76`'da **`urun` ayağı** eklendi — ürün **çağrılıyor**, taklit edilmiyor ⑦ |
| `_RRF_K = 10` | doğru aletle: `K ∈ {5,10,20,37,60}` → **beşinde de birebir aynı** | ✅ **kapandı** — *fark ölçülemedi → sabite dokunulmadı* 🆕 |
| ürün sıralaması | 🔴 `R@3` **83,8** ↔ vektör **91,9**; üç anlamsal vaka `sıra=None` | ✅ `§77` teşhis → `§78` çare: `_VEK_GECIS=1` → **86,5 · MRR 0,820** |
| `_norm` yinelenmesi | **6** modülde tanımlı | 🟡 temizlik; ölçülmüş kullanıcı kusuru yok |

⊙ **Ölçüm tabanı (37 vaka, `s37` kodu):**

| ayak | `R@1` | `R@3` | `R@5` | `MRR` |
|---|---|---|---|---|
| leksik | 70,3 | 75,7 | 81,1 | 0,749 |
| vektör | 81,1 | **91,9** | 91,9 | 0,868 |
| birleşik (max) | 78,4 | 91,9 | 91,9 | 0,854 |
| **ürün** (bugün) | **81,1** | **86,5** | **91,9** | **0,845** |

⊙ `§78`–`§85`'te üç ölçünün üçü de vektör ayağının **tavanına** çekildi ve **gürültü
kontrolü ㊳ her adımda birebir temiz** kaldı. İki karar da *«gerekçesi bitmiş bir kuralı
sürdürme»* biçimindeydi: leksik kapı **önek yokken** gevşer, eşitlik kuralı **önek yokken**
uygulanmaz.

*(Vektör ayağı test kabında ancak canlı gömme önbelleği bağlanınca koşar —
`-v …_dima_hf_cache:/tmp/fastembed_cache`, **`DIMA_VQR_EMBEDDER=off` verilmez**.)*

✅ **AÇIK KAPANDI** (`§79`·`§85`): koşulsuz gevşetme gürültü üretiyordu; **koşullu**
hâlde (önek kovası boşken) aynı kazanç **bedelsiz** geldi. *Bedeli ödeten şey sayı değil
**koşulsuzluktu*** ㊴.

---

## §6b — BELGELER NASIL DÜZENLENDİ, HANGİ KAPI NEYİ TUTUYOR 🅦

Devralanın belgeye **güvenebilmesi** için, belgelerin doğruluğu artık kapılıdır.

| kapı | neyi tutuyor | nasıl koşulur |
|---|---|---|
| `test_belge_duzeni.py` | kök **dört** dosyalık (`README` + `OPERASYON*`) · `denetim/` adları **tarih damgalı** *(canlı kayıt defterleri hariç, adıyla ilan edilmiş)* · her belge **git'te** · indeks **her dizini** anlatıyor · indekste **kırık bağ yok** | 🔴 **kök mount**: `-v "$PWD:/repo" -w /repo/backend` |
| `test_belge_yollari_gercek.py` | 🆕 **canlı belgede anılan her yol gerçekten var** (satır içi kod dâhil, **602 yol**) | aynı |
| `test_f8_dogruluk_yayini.py` + 3 kardeş | **yayımlanan sayı** çürümüyor (`belgeler/DOGRULUK.md` · `HAVA-BOSLUGU.md`) | standart mount |

⚠ **`skipped` bir onay değildir** 🅯: bu iki belge kapısı standart test kabında **atlar**
(repo kökü görünmez) ve bir zamanlar **7/7 atlanıyordu** — kimse görmedi.

**Yerleşim kuralı** `belgeler/00-INDEKS.md`'de ve **bayatlama süresine** göre: kök =
giriş · `kilavuz`·`mimari`·`urun`·`plan` = canlı · `denetim`·`devir`·`arastirma` = 🔒
tarihsel · `belgeler/` kökü = **kapıyla canlı tutulan yayın**.

**Giriş noktası:** kök [`README.md`](../../README.md) — *ne olduğu · depo haritası ·
ayağa kaldırma · **ilk gün okuma sırası** · nerede kaldık · dokunulmazlar · test
disiplini · yeni gelenin çarpacağı beş şey*.

---

## §6c — 🔴 DEVRALANIN İLK GÜNÜ (sırayla, atlanmadan)

| # | ne | nerede |
|---|---|---|
| 1 | **Depoyu tanı** — 30 dk | kök [`README.md`](../../README.md): ne olduğu · harita · ayağa kaldırma · **ilk gün okuma sırası** |
| 2 | **Backend'i kaldır** | `README §3` (kısa) ya da [`SERVER_COMMANDS.md`](../kilavuz/SERVER_COMMANDS.md) (**reçetenin sahibi**) — ⚠ **ÖNCE derle, SONRA `rm -f`** |
| 3 | **Frontend'i aç** | `cd dima-frontend-demo-master && pnpm dev` → `:3000` |
| 4 | 🔴 **İLK İŞ: ekranda doğrula** | *«makinelerin performansı nasıl»* yaz (salınımlı, 2-3 kez). Beklenen: önizleme kartında **pill satırı + `[koş] [düzenle] [iptal]`**; `[koş]` → `docker logs dima-oneri-8002 \| grep 'POST /plan/kos'` |
| 5 | **Nerede kaldık** | [`belgeler/plan/ONGORU-DURUM.md`](../plan/ONGORU-DURUM.md) `§63`–`§85` |
| 6 | **Değiştirmeden önce** | `backend/CLAUDE.md` (en üst kural + test kapısı) · `backend/MIMARI.md §0` (otorite) |

⚠ **4. madde bu tutanağın tek doğrulanmamış satırıdır** 🅢: zincir kodda bağlı ve
`test_onizleme_zinciri_kopuk_degil.py` ile korunuyor, ama `localhost:3000` **on bir tur
boyunca kapalıydı** — *bir zincirin kodda bağlı olması ekranda göründüğünün kanıtı
değildir* 🆘.

---

## §7 — DEVİR, TEK CÜMLE

> Öngörü katmanının **karar mekaniği bitti, kapılı ve canlıda** (`s39`); öneri sıralaması
> ölçülüp **vektör tavanına** çekildi (`81,1 / 86,5 / 91,9`); **belgeler yeniden düzenlendi
> ve doğruluğu kapıya bağlandı** (kök `README` + iki belge kapısı); geriye **tek bir
> doğrulanmamış şey** kaldı: arayüzü **ekranda bir kez görmek**.
