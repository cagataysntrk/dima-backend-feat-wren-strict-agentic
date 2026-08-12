# ÖNGÖRÜ OPERASYONU — DURUM & PROTOKOL

> 🔴🔴 **BU DOSYA HER TURDA GÜNCELLENİR.** Bağlam sıfırlansa (compact) bile operasyon
> buradan devam eder. Sohbet geçmişine ihtiyaç **yoktur**.
> **Plan:** `belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md` · **Otorite:** çelişkide
> `backend/MIMARI.md` kazanır.

---

## §0 · COMPACT KURTARMA — *bağlam sıfırlandıysa ÖNCE BUNLARI OKU*

Sırayla, **başka hiçbir şey yapmadan**:

| # | dosya | ne verir |
|---|---|---|
| 1 | **bu dosya** (`ONGORU-DURUM.md`) | nerede kaldık · kurallar · sıradaki adım |
| 2 | `belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md` | **plan** — `§0` dizin, `§42` fazlar, `§44` bağımlılık |
| 3 | `backend/CLAUDE.md` | kapı politikası · koşum hijyeni · garson devri |
| 4 | `backend/MIMARI.md` `§0` dizini | mimari otorite (5.700 satır, dizinden gez) |

⚠ `OPERASYON.md` / `OPERASYON-DURUM.md` (repo kökü) **v1 operasyonuna** aittir; bu
operasyonun dosyası **bu dosyadır**. İkisini karıştırma (`KAT-1`).

🔴 **Compact döngüyü DURDURMAZ.** Compact'ten önce de sonra da her turun son eylemi
`ScheduleWakeup`'tır. Yeni bağlam bu dosyayı okur ve **kaldığı yerden** devam eder.

---

## §1 · BAĞLAYICI KURALLAR

### 1.1 Döngü
- 🔴 **Her turun son eylemi `ScheduleWakeup`.** İstenen: **30 sn**.
  ⚠ **ÖLÇÜLDÜ: araç `delaySeconds`'i `[60, 3600]`'e KIRPIYOR** — 30 istenirse 60 olur.
  Bu yüzden **`delaySeconds: 60`** yazılır; bu aracın verebileceği **en kısa** aralıktır.
  *Bir sınırı bilmeden istemek, istediğini aldığını sanmaktır.*
- 🔴 Yanıta *«tamam, en kısa aralıkla (60 sn) wake up zamanlayacağım»* ile başla.
- 🔴 **Yalnız kullanıcı «dur/bekle» derse** `stop: true`. Kapı kırmızısı · ajan bildirimi ·
  hata · compact — **hiçbiri** durma sebebi değildir.
- 🔴 `prompt` alanına **tam `/loop` metni + güncel durum özeti** yazılır.

### 1.2 Ölçüm
- 🔴 **Hiçbir sayıyı ölçmeden alma — kendi bulgunu da.** Bu oturumda iddialar **22 kez**
  daraldı; **24'ü** kendi probum/testim/teşhisimdi.
- 🔴 **Kapının yeşili de kapsamıyla sınırlıdır** 🅣. *(Ölçüldü: üç kez «kapı temiz» dedim,
  süitin **%5,6**'sını ölçüyormuşum — sebep `zsh`'ın tırnaksız değişkeni bölmemesiydi.)*
- 🔴 **Tek koşum kanıt değildir** 🅢 — garson örneklemesi turdan tura değişir ㉝.
- 🔴 Sayıyı **artefakttan** oku, belgeden değil ㉔.

### 1.3 Değişiklik
- 🔴 **Mutasyonla kanıtla** 🅑 — `grep -c` **VE** `diff` ile doğrula. Gövdeye gömülü bir
  karar kanıtlanamaz; yüklem taşıyan yeri **modül düzeyine** çıkar 🅯.
- 🔴 **Komşuyu koş** ⑯ — `ast` ile bağımlıları bul.
- 🔴 **İkinci sahip açma** (`KAT-1` ㊲). Aynı kuralın **iki tüketicisi** olabilir ㉚.
- 🔴 **Gerekçeli ⊘ da bir sonuçtur** ㊸. Ödenmeyecek borcun **nedeni yazılır** 🅗.
- ⚠ `§38.4` dokunulmazları: LLM SQL yazmaz **küp yolunda** · sayıyı küp koyar · grafik
  deterministik · kapalı fiil kümesi · `narration_guard` · beyan kültürü · Türkçe
  morfoloji · JOIN planlayıcı yasağı · `KURAL B` · `KAT-1` · motor in-process · `E-8` ·
  `ADR-0024`.

### 1.4 Ortam *(ölçülmüş yasaklar)*
- ⚠ **`docker-compose up` DENENMEZ** — v1 `KeyError: ContainerConfig` verir **ve koşan
  konteyneri durdurur** (ölçüldü: 40 sn kesinti).
- ⚠ `demo/wren-project` **SİLİNMEZ** — motorun semantik model dizini.
- ⚠ **Dosya silme yok.** ⚠ Paylaşılan repo — ana dizinde **checkout/stash yok**.
- ⚠ **`interaction_log`'a DB probu YASAK** *(kod okumak serbest)*.
- ⚠ **Commit footer YASAK** (`backend/CLAUDE.md`, saka standardı).
- ⚠ Kapı koşarken repoya **yazma**.

### 1.5 Koşum kalıpları *(kopyala-yapıştır)*

```bash
# HER Bash'in ilk satırı:
cd /home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic

# HEDEFLİ TEST
docker run -d --name X$$ --network none -v "$PWD/backend:/app" \
  -v "$PWD/belgeler:/belgeler:ro" -v "$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro" \
  -w /app --user "$(id -u):$(id -g)" -e DIMA_VQR_EMBEDDER=off dima-test \
  python -m pytest -q -p no:randomly tests/test_X.py

# TAM KAPI  ⚠ ${=D} ZORUNLU — zsh tırnaksız değişkeni BÖLMEZ
cd backend
D=$(cd .. && git diff --name-only 294eb67..HEAD | grep "^backend/" | sed 's|^backend/||' | tr '\n' ' ')
docker run -d --name Xk$$ --network none -v "$PWD:/app" -v "$PWD/../belgeler:/belgeler:ro" \
  -v "$PWD/../dima-frontend-demo-master:/dima-frontend-demo-master:ro" -w /app \
  --user "$(id -u):$(id -g)" -e DIMA_VQR_EMBEDDER=off dima-test \
  python lab/kapi.py --hizli --degisen ${=D}
# ✅ başlıkta «değişen=606 → seçilen 383/456» GÖRÜNMELİ; görünmüyorsa KAPI YALAN SÖYLÜYOR

# KORPUS
docker run -d ... dima-test python lab/nl_corpus.py --kapi     # ~2 dk, çıkış 0 beklenir

# BELGE DÜZENİ KAPISI — ⚠ TEK KOŞUM BİÇİMİ VAR (tur 0'da bulundu)
# Kapı repo KÖKÜNÜ görmek zorunda; standart koşumda (yalnız backend/ bağlı) 7 test
# SESSİZCE ATLANIYOR, ana makinede ise bağımlılık yok. Çalışan tek kombinasyon:
docker run -d --name Xbd$$ --network none -v "$PWD:/repo" -w /repo/backend \
  --user "$(id -u):$(id -g)" -e DIMA_VQR_EMBEDDER=off dima-test \
  python -m pytest -q -p no:randomly tests/test_belge_duzeni.py
# ⊙ Kökü /repo'ya bağla, ÇALIŞMA DİZİNİ /repo/backend olsun — böylece hem bağımlılıklar
#   (imajdan) hem repo kökü (parent zincirinden) görünür.

# CANLI (backend :8001, imaj dima-backend-temiz:s06)
TK=$(curl -s -m 25 -X POST localhost:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
# ⚠ takip çapası `cube_query` (thread_id PASS-THROUGH) · chip'ler `next_steps`'te
```

---

## §2 · TABAN SAYILAR *(2026-08-13, ölçülmüş)*

```
SÜİT      4.843 ✅ · 1 🔴 (d11, GEREKÇELİ) · 43 atlandı   → 383/456 dosya
KORPUS    ✅ çıkış 0 · erişim 83/69/68/72 (dördü de tabanında)
          doğru-cube %95,6 (t.94,4) · semantik vaka %94,4 (t.93,5) · cevapsız %19,7
KATALOG   23 küp · 136 ölçü · 816 terim · yön beyansız 68/136 (kapılı)
YÜZEY     HTTP ucu 77 (8 gerekçeli yetim) · app/ 138 modül (4 yetim) · MCP 29 araç
TAVAN     ask() 1444/1444 · ask.py 2888/2888
```

⚠ **Raporun `§1.1`/`§1.2`'sindeki `54/53/58` BAYATTI ve düzeltildi** — o düşüş bir payda
kovası hatasıydı (`b2f3edb`), gerileme **hiç olmadı**.

---

## §3 · KARAR VERİLMİŞ SIRA

| # | faz | ölçüme bağlı mı | durum |
|---|---|---|---|
| 1 | **`FAZ 0`** Türkçe gömme ölçümü (`Recall@3`) | — | ✅ **BİTTİ — %89,5 → 🟢 DEVAM** |
| 2 | ~~katalog borcu (68 yön beyanı)~~ | ⊘⟳ | ⟳ **ÇERÇEVE ÇÜRÜDÜ** — 68'in ~50'si gerçekten yönsüz; gerçek borç **~18** ve `§7`'de ⑫ olarak kayıtlı |
| 3 | **`FAZ 4`** kıyas temeli chip'i | ⊘ | ⏭ |
| 4 | **`FAZ 1`** `emin_miyim` (şekil birleştir) | ⊘ | ⏭ |
| 5 | **`FAZ 2`** marj kapısı (varsayılan `∞`) | ⊘ | ⏭ |
| 6 | `FAZ 3` aday yan kanalı | ⊘ | ⚠ `FAZ 6` ile **aynı demette** (yetim uç riski) |
| 7 | `FAZ 5–8` öneri motoru · uç+FE · pill · hasat | 🔴 **`FAZ 0`'a bağlı** | ⏸ |

🔴 **`FAZ 0` %70'in altında çıkarsa `FAZ 5–8` RAFA KALDIRILIR** — teşhis geçerli kalır,
çare değişir. *(Raporun kendi ölüm şartı, `§13.1`.)*

---

## §4 · AÇIK BORÇLAR

| # | borç | durum |
|---|---|---|
| **d11** | 9 boyutun fan-out sertifikası | 🔴 kapı **kırmızı KALIYOR** — ön koşul: sertifikaya `mdl_version` damgası |
| ① | Discovery dalına beyan taşıma | ⊘ ertelendi — o dal `uyum.denetle`'den hiç geçmedi |
| ③ | `netlestirme_sorusu` çağrı yeri | ⏭ `adaylar` boşken `diyalog_durumu.kismi_cq` okunabilir |
| ④ | `CLARIFY:dönem` (181–296 soru/şirket) | ⏭ ölçülmedi |
| ⑥ | `demo/OLMAYAN-DIZIN` (1,2 MB, 0 referans) | ⏭ **silinmez**, karar kullanıcının |
| ⑩ | fan-out sertifikası sürüm damgası | ⏭ `d11`'in ön koşulu |
| ⑪ | `belgeler/` kökünde **yeri olmayan iki belge** — `DIKKAT-EDILECEKLER.md` · `dima v2 v3 için mimari karar (1).md` | 🔵 **kullanıcı kararı bekliyor**: `denetim/` mi `kilavuz/` mu `mimari/` mi? ⚠ **taşınmadı, silinmedi** |

---

## §5 · TUR KAYDI

> Her tur **buraya** bir satır. En yeni **üstte**. ⚠ Bu bölüm **kısa tutulur** — uzarsa
> eski satırlar `belgeler/denetim/`'e taşınır, **silinmez**.

| tur | ne yapıldı | kapı | commit |
|---|---|---|---|
| 1 | **`FAZ 0` ÖLÇÜLDÜ** — `Recall@3 = %89,5` 🟢 · vektör leksikten **+10,6 puan** · ⚠ mutlak eşik **kullanılamaz** | hedefli ✅ | *(bu tur)* |
| 0 | operasyon kuruldu: bu dosya · memory · raporun bayat sayıları düzeltildi · **taşınan belge yolları onarıldı** | 27 ✅ | `1ee3d14`+ |

⚠ **Tur 0'da ölçülen ortam değişikliği:** `1ee3d14` `belgeler/DOGRULUK.md`'yi
`belgeler/denetim/`e **taşımış**; üç kapı eski yolu arıyordu ve **7 kırmızı** verdi.
Yol sabitleri güncellendi — kapı **gevşetilmedi**, aradığı yer düzeltildi.
🅣 *Taşınma fark edilmeseydi kapılar «belge yok» diye **sessizce atlanır** ve yayın
çürümesi görünmez olurdu.*

---

## §6 · `FAZ 0` SONUCU *(2026-08-13, ölçüldü — `lab/oneri_olcum.py`)*

```
havuz     136 ölçü · 865 görünüm (ad + etiket + 677 sinonim)
vaka      19 ölçülebilir (+1 gürültü)   ⚠ payda küçük — eğilim işareti, kanıt değil
                        R@1     R@3     R@5    MRR
leksik (difflib)      %78,9   %78,9   %78,9   0,807
vektör (e5-large)     %89,5   %89,5   %89,5   0,909
birleşik max()        %89,5   %89,5   %89,5   0,909
```

### 🟢 KARAR: `§13.1` eşiği geçildi — `%89,5 ≥ %85` → **DEVAM**

**Ve vektör hakkını veriyor:** leksik tabana göre **+10,6 puan** (`MRR +0,102`). Yani
gömme altyapısı taşımak **gerekçeli** — `difflib` yolu aynı işi yapmıyor.
*Bir bileşeni eklemenin gerekçesi, onsuz ölçülen sayıdır.*

### 🔴 ÖLÇÜMÜN İKİNCİ BULGUSU — **MUTLAK EŞİK KULLANILAMAZ**

Gürültü vakası *«vardya»* (katalogda karşılığı **yok**) en iyi kosinüsü **0,851** aldı —
gerçek eşleşmelerle **aynı bantta**. Yani:

> 🔴 `FAZ 2`'nin marj kapısında **taban skor bir eşik olarak konulamaz**; yalnız
> **sıralama ve marj** anlamlıdır. E5 kosinüsü `0,7–1,0`'da sıkışıyor.

⚠ Bu, `§24`'ün *«taban skor altındaysa sınır beyanı»* dalını **doğrudan etkiler**: o dal
kosinüs eşiğiyle **kurulamaz**; ya leksik skora ya da *«birinci ile ikinci arasındaki
fark**sız**lığa»* bağlanmalıdır. `FAZ 2` bu bulguyla tasarlanacak.

### `R@1 = R@3 = R@5` — ve bu neden anlamlı

Üç sayı **eşit**: hedef ya **birinci** sırada geliyor ya **hiç** gelmiyor. Yani kusur bir
*«sıralama»* kusuru değil bir **kapsam** kusuru — iki vaka (`%10,5`) katalogda hiçbir
görünümle eşleşmiyor. Bu, öneri katmanının değil **katalog borcunun** alanı ⑤.

### ⚠ Bu ölçümün SINIRI — dürüstlük notu

| ölçülmedi | neden |
|---|---|
| **BGE-M3** karşılaştırması | ağsız ortamda **indirilemiyor** (~2 GB); `--network none` |
| gerçek gecikme (p95) | ayrı ölçüm; burada toplu gömme yapıldı |
| kabul oranı | kullanıcı gerektirir (`§13.2`) |

🅜 **Payda 19** — `§13.1` *«30–40 ifade»* diyordu. Bu bir **eğilim işaretidir**, kanıt
değil; `FAZ 5` öncesi payda büyütülmeli. Karar eşiği geçildi ama **rahat bir farkla
değil**: bir vaka değişse oran %84,2'ye düşer ve karar **sarıya** döner.

---

## §7 · KATALOG BORCU — **ÇERÇEVE ÖLÇÜMLE ÇÜRÜDÜ** *(2026-08-13)*

`FAZ 0`'ın ② bulgusu katalog borcunu işaret etmişti. Araştırıldı ve **borcun tanımı
yanlıştı**.

### Ölçüm

```
136 ölçü = 68 `lower_is_better` beyanlı + 68 BEYANSIZ
```

Ama 68 beyansızın **etiketlerine** bakınca sınıf ayrışıyor:

| sınıf | ~adet | örnek |
|---|---|---|
| 🟢 **gerçekten YÖNLÜ** (yüksek iyi), beyan **eksik** | ~18 | `ort_oee` · `ilk_seferde_tamam_yuzde` · `kar_marji_yuzde` · `zamaninda_teslim_yuzde` · `planli_bakim_yuzde` · `basari_orani_yuzde` · `kazanma_orani_yuzde` |
| ⚪ **gerçekten YÖNSÜZ** — beyan **eksik değil, YOK** | ~50 | adet (`is_emri_adedi`·`personel_sayisi`·`fatura_sayisi`) · hedef (`toplam_hedef`) · bakiye (`bakiye`·`toplam_borc`) · kur (`ort_kur`·`kapanis_kuru`) · hacim (`toplam_uretim_kg`·`toplam_metre`) · tutar (`toplam_kdv`·`siparis_tutari`) |

🔴 **Yani *«68/136 yön beyansız = borç»* çerçevesi YANLIŞ.** Elli ölçünün yönü **yok** —
bir adedin, bir bakiyenin, bir kurun *«iyi yönü»* diye bir şey yoktur. Onları
*«beyansız»* saymak, olmayan bir borcu **her turda** raporlamaktır.

> 🆋 *Bir listede olmamak, karşıt listede olmak değildir* — **ve üçüncü bir hâl de
> vardır: yönü olmamak.** Bugünkü şema iki hâl tanıyor (`lower_is_better` ↔ *«bilinmiyor»*),
> oysa gerçekte **üç** hâl var.

### Kod yüzeyi ölçüldü

```
lower_is_better okuyan  : kok_neden._yon_beyanli:413 (TEK SAHİP) + interpret (5 yer, hep _yon_beyanli mantığı)
higher_is_better        : app/ altında 2 geçiş — ikisi de kok_neden'in AÇIKLAMA satırı, KOD YOK
```

⊙ `_yon_beyanli` **tek sahip** (`KAT-1`) — üçüncü hâl eklenecekse **tek yerden** eklenir.

### ⏭ KARAR — ve neden bu tur UYGULANMIYOR

Doğru iş **iki parça**: ① şemaya `higher_is_better` **üçüncü listesi** ② ~18 ölçünün
oraya yazılması. Ama ⓐ bu bir **şema sözleşmesi** değişikliğidir (`compose` · pack
YAML'leri · `_yon_beyanli` · `interpret`), ⓑ `test_a_yon_beyani.py`'nin
`AZAMI_YONSUZ_ORAN=0.50` tavanı bu tanımla **anlamını yitirir** (payda değişir 🅜).

⚠ Bu **bir faz büyüklüğünde** iş ve `FAZ 4`/`FAZ 1`'den **önce** gelmesi için bir
sebep yok: öneri katmanı yönü **kullanmıyor**; yön yalnız *«en kötü/en iyi»* sorularında
devreye giriyor. 🅗 **Borç ödenmiyor, ve nedeni bu satır.**

📌 **Yeni borç ⑫:** üçüncü hâl (`higher_is_better`) — ~18 ölçü. Ön koşulu yok, ama
`AZAMI_YONSUZ_ORAN` tavanı **onunla birlikte** yeniden tanımlanmalı.

---

## §8 · `FAZ 4` SONUCU — **YETENEK VARDI, ZİNCİR YOKTU** *(2026-08-13)*

**Planın gerekçesi ölçümde çürüdü** 🅟 — ㊷ **on ikinci** kez. *«"RAM-3 neden düşük"
cevapsız»* artık doğru değil; **iki kipte de** cevaplanıyor:

| kip | ölçülen |
|---|---|
| çapalı (`cube_query` verilmiş) | *«RAM-3, öteki 10 makine ortalamasından **%10,7 düşük** (52,45 ↔ akran ort. 58,76)»* · **11 satır** |
| çapasız (fresh) | `source=cube+llm`, makbuzun 2. adımı **`KIYASLA`** — *«bir varlığı akranlarıyla karşılaştırır»* |

Motor `contribution._akran_kiyasi` (`:600`), ilkel `ilkeller.py:82`, fiil adı
`plan_semasi.FIIL_ANLAMI`. Chip şeridi: **5 chip, hepsi `cube_query` taşıyor** (süs yok 🆈).

### Kalan iş yetenek değil **zincirdi** ㉕

㉙ ile arandı: `_akran_kiyasi` / `akran_ortalamasi` adını anan test **sıfır** dosya.
Yani çalışan bir yetenek **kapısızdı** — gerilese kimse duymazdı. Bu turun teslimi
**kapının kendisi**: `tests/test_kiyas_temeli_chipi.py`, **7 yüklem**, ürün kodu
**değişmedi**.

🅑 **İki mutasyonla kanıtlandı** (ikisi de `sed` ile uygulanıp `diff` ile geri alındı):

| mutasyon | öldürdüğü yüklem |
|---|---|
| küpün zaman ekseni şartını kaldır | `test_tetikleyici_SORGUNUN_degil_KUPUN_zaman_ekseni` |
| chip'ten `compare`'i düşür (süse çevir) | + `test_kiyas_temeli_chipi_URETILIR` |

⑯ komşu: `d3_bicim` · `kiyas_cebiri` · `d11_kiyas_olgusu` · `temellendirme` + yeni kapı
→ **53 ✅**.

### Planın `③` maddesi **yanlıştı** — uygulansaydı çalışan cevabı kırardı

Plan *«yön beyansız ölçüde `[akran]` chip'i sunulmasın»* diyordu. Ama `ort_oee`
`_yon_beyanli()` gözünde beyansızdır **ve** *«RAM-3 neden düşük»* onun üstünde çalışır.
Doğru ölçüt yönün **beyanı** değil, yargının **yokluğu**dur (`GG8`): akran kıyası bir
**olgudur**, yargı değil. Kapı `③`'ü *«yargı üretilmesin»* diye yazdı.

### ⚠ ⑫'nin çerçevesi de düzeldi — ve **kendi dünkü sayım yanlıştı**

`ort_oee` **beyanlıdır**: `oee/metadata.yml:23` → `lower_is_better: false`
(*«B-5 · yüksek = İYİ»*). Kaybı yapan **projeksiyondur**: `wren_service.py:853` listeye
**yalnız doğru olanları** alıyor (`if m.get("lowerIsBetter") or m.get("lower_is_better")`)
→ `false` ile *«alan yok»* **aynı kovaya** düşüyor.

🆋 **Üç kova sayıldı** (`demo/packs/**/metadata.yml`, ham YAML):

| kova | sayı | anlam |
|---|---|---|
| `lower_is_better: true` | **72** | düşük = iyi |
| `lower_is_better: false` | **55** | **yüksek = iyi — ÜÇÜNCÜ HÂL, ZATEN VAR** |
| alan yok | **46** | gerçekten yönsüz (kur · adet · tutar · maaş · metre) |

⟳ Dünkü *«68 `lower` + 68 beyansız, üçüncü hâl kodda YOK»* ölçümü **`false`'u beyansız
saymıştı**. Üçüncü hâl **kaynakta var**; kaybolduğu yer tek satırlık bir projeksiyon.
⑫ yine de açık kalır — çünkü tüketiciyi yazmak bir **davranış** değişikliğidir (yargı
üretimi), ama maliyeti *«şema sözleşmesi»* değil.

### ③ İki yüklemim de önce yanlış yazıldı, ikisini de ölçüm düzeltti

1. *«`compare` taşıyan chip»* süzgeci **yanlıştı**: chip'ler `{**cube_query, …}` ile
   üretilir → kaynak `compare` taşıyorsa **hepsi** miras alır. Süzgeç mirası değil
   **eklemeyi** aramalı.
2. *«Sorguda zaman ekseni yoksa dönem kıyası teklif edilmemeli»* dedim; **ürün
   haklıydı**. `/cube` ile ölçüldü: eksensiz `cube_query` + `compare: yoy` → **11
   satır**, `ort_oee_gecen` · `ort_oee_degisim_yuzde` doldu. Vaat **tutuluyor** 🆈.
   Tetikleyici **küpün** ekseni, sorgunun değil.

📌 **`FAZ 4` ✅** — ürün kodu değişmeden, çünkü ürün zaten doğruydu; teslim **kapı +
düzeltilmiş teşhis**. Sırada **`FAZ 1` `emin_miyim`**.
