<!-- 🅦 Bu bir ÖZET DEĞİL, bir TESLİM TUTANAĞIDIR. `ONGORU-DURUM.md` operasyonun
     günlüğüdür (bölüm bölüm, gerekçeleriyle); bu dosya devralanın sorduğu üç soruya
     cevap verir: NE ÇALIŞIYOR · NE ÇALIŞMIYOR VE NEDEN · NEREYE BASARSAM KIRILIR. -->

# DİMA — Öngörü Katmanı / **Rol Değişikliği** Devir Tutanağı (13 Ağustos 2026)

**Kod tabanı:** `dfb0246` · **Canlı imaj:** `dima-backend-temiz:s35` (kap `dima-oneri-8002`, `:8002`)
**Aralık:** `e521e46..dfb0246` — **14 commit**, `§63`–`§72`

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
| `_RRF_K = 10` | doğrudan prob: 5 soru × 3 farklı `K` → **top-2 hiç değişmiyor**, yalnız 3. sıra 3 kez oynadı | 🟡 ölçülmüş **kusur yok** |
| `_RRF_K` kalibrasyonu | `lab/oneri_olcum.py` **füzyonu ölçmüyor** (`fuzyon={}`, üç `K` için birebir aynı) | ⊘ **araç yetersiz** 🆆 — kalibrasyon için önce **aracın** RRF'i ölçmesi gerek |
| `_norm` yinelenmesi | **6** modülde tanımlı | 🟡 temizlik; ölçülmüş kullanıcı kusuru yok |

⊙ **Ölçüm tabanı (37 vaka, `s36` kodu):** leksik `R@1 70,3 · R@3 75,7 · MRR 0,749` ·
vektör `R@1 81,1 · R@3 91,9 · MRR 0,868`. *(Vektör ayağı test kabında ancak canlı
gömme önbelleği bağlanınca koşuyor — `-v …_dima_hf_cache:/tmp/fastembed_cache`.)*

---

## §7 — DEVİR, TEK CÜMLE

> Öngörü katmanının **karar mekaniği bitti, kapılı ve canlıda** (`s36`); geriye **tek bir
> doğrulanmamış şey** kaldı: arayüzü **ekranda bir kez görmek** (`localhost:3000` altı
> turdur kapalı) — kod tarafında açık bir iş yok.
