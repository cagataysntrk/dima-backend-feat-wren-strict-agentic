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

---

## §9 · `FAZ 1` SONUCU — **DÖRT SAHİP → BİR** *(2026-08-13)*

`app/emin_miyim.py` yazıldı; *«elimdeki aday üstünde işlem yapacak kadar açık ara önde
mi»* sorusunun **tek sahibi**. ㊷ bu kez temiz çıktı: dosya **yoktu**.

⚠ **Planın «beş çağıran»ı DÖRTTÜR** ⑲ — ㉙ ile sayıldı:

| # | yer | taban | marj | ek ön koşul | sonuç |
|---|---|---|---|---|---|
| ① | `value_index.auto_fix` | `AUTO_SCORE` 0,80 | `AUTO_MARGIN` 0,08 | `MIN_AUTO_LEN` | 2 |
| ② | `cube_router` yazım hatası | `_TYPO_HIGH` 0,82 | `_TYPO_GAP` 0,08 | `len_ratio` · çapraz-konu | **3** |
| ③ | `_match_cube:1190` | *(yok)* | **4 harf** | — | 2 |
| ④ | `cube_router:1109` | *(yok)* | **∞** | — | 2 |

② **üç sonuçludur** ve `Karar`'ın üç hâli (`OTO_ICRA`/`GOSTER`/`SINIR`) birebir odur;
①③④ dejenere hâlleri. Kalibre sabitleri **çağıranlarda kaldı** (`KAT-1`).

### 🔴 Planın `1.5` ve kapı `⑤`'i UYGULANMADI — gerekçesi yazıldı 🅗

Plan *«harf farkını 0–1'e normalize et»* + *«normalize değilse `ValueError`»* istiyordu.
`_longest_syn_hit` bir **harf sayısıdır** (üst sınırı yok; katalogdaki en uzun ad **30**).
Sabit bir payda uydurmak 🅭 gerekirdi ve o payda aşıldığı gün (*33 harflik bir eşanlamlı
eklenince*) `ValueError` **küp seçimini çökertirdi**. Yani `⑤` bir güvenlik kapısı değil,
**kendi ürettiği riskin bekçisi** olurdu. Yerine sözleşme **birim-bağımsız**: skorlar
yalnız *tek çağrı içinde* kıyaslanabilir; ③ harf sayısını **olduğu gibi** geçirir.

### ⚠ `Aday` dataclass'ı ÖLÇÜMLE ELENDİ

Plan `1.1` `Aday(kimlik·etiket·skor·kaynak)` istiyordu. Yazıldı — sonra ölçüldü:
**dört çağıranın hiçbiri** `kimlik`/`etiket`/`kaynak` alanlarını kullanmıyor, hepsi
kukla değer geçiyordu. Bugün karşılığı olmayan bir soyutlama 🆈; sözleşme
`karar(skorlar: list[float], …)`'a indirildi. Gerekirse eklemek bir satırdır.

### 🔴 TAVAN KAPISI KIRMIZI VERDİ — ve haklıydı, ama ölçtüğü şey sınırlıydı

`test_CUBE_ROUTER_TAVANI_ASMIYOR`: **1969 ≤ 1954 değil**. Sıkıştırma **8 satır** geri
verdi (1969 → 1961) ve orada tükendi. Kalan **+7**, kuralın çıkmasının değil,
**yerine geçen çağrının sözdizimi bedelidir**: beş anahtarlı bir `karar(...)`,
`a >= X and (a-b) >= Y` yazımından uzundur. ㊳ *Vekil ölçüt, ölçmediği bir iyileşmeyi
cezalandırabilir* — tavan **kod satırını** sayar, **sahip sayısını** değil; burada
iyileşen sahip sayısıdır (**4 → 1**).

⊙ Çözüm listenin kendi mekanizması: `MUAFIYET_CUBE_ROUTER_KOD`'a `(sha, Δ=7, gerekçe)`
maddesi — emsali `§B12` (aynı sınıf, `KAT-1`, `Δ=1`). 🅜 Δ **tam ölçülen fazladır,
yuvarlanmadı**; boşluk bırakmak `test_KAPI_SAHTE_DEGIL`'i kırmızı verirdi.

### Kanıt

* Kapı `tests/test_emin_miyim_tek_sahip.py` — **8 yüklem**, ① `ast` ile *«kimse kendi
  marjını hesaplamıyor»*, ③ üç kademe + `_MID_WIDE`'ın **taşındığı**, ④' harf biriminin
  **korunduğu**.
* 🅑 **İki mutasyon:** `fark >= marj` → `>` (**2 kırmızı**) · `_MID_WIDE` dalını düşür
  (**1 kırmızı**). İkisi de `diff` ile geri alındı.
* ⑯ komşu: `modul_buyume` · `typo` · `value_index` · `match_cube` · `tie` · `daraltma`
  → **272 ✅ · 2 atlandı**.
* 🔴 **Korpus ✅ çıkış 0 — dört şirket de TABANLA BİREBİR:** boyahane %83 · atiksan %69
  · gulteks %68 · gitas %72 · doğru-cube **%95,6** · semantik **%94,4**. `KURAL B`
  davranış düzeyinde kanıtlandı.

📌 **`FAZ 1` ✅.** Sırada **`FAZ 2` marj kapısı** — ⚠ `FAZ 0`'ın bulgusu gereği
**mutlak eşik YOK**; `emin_miyim.karar` zaten marj tabanlıdır, `FAZ 2` onun **üstüne**
kurulur.

---

## §10 · `FAZ 2` — **KISMİ: `2.1`+`2.2` ⊘ · `2.4` ㊷ · `2.3` AÇIK** *(2026-08-13)*

🔴 **`FAZ 2` BİTMEDİ.** `2.3` (SINIR → proaktif sınır beyanı) gerçekten açık; sonraki
turun işi. Bu turda `2.1`/`2.2` **gerekçeli ⊘** ㊸ ve `2.4` **zaten yapılmış** çıktı.

### `2.1`+`2.2` ⊘ — üç engel, üçü de KODDA ölçüldü

| # | engel | ölçüm |
|---|---|---|
| ① | bayrak kaydı **sayı taşımıyor** | `resolve_for -> dict[str, str]`; değerler **aşama** (`off\|alpha\|beta\|prod`) ⑤ |
| ② | `cube_router` **bilerek saf** | `:1375` *«bayrağı çağıran çözer»*; `_match_cube`'un **beş** genel çağıranı, hepsi `(q, schema)` |
| ③ | 🔴 **tek kaynağı bölerdi** | kıran (`:1194/1200`) ile tanımlayan (`cube_tie_candidates:2547`) **aynı** `_longest_syn_hit`'i okur |

③ belirleyicidir: `_longest_syn_hit`'in kendi docstring'i *«ikisi ayrışırsa chip,
route'un çözebildiği bir soruya sorulur»* diyor. Yalnız `_match_cube`'u ayarlanabilir
yapmak o ayrışmayı **elle üretmek** olurdu.

Sayısal ayarların evi `config.Settings`'tir (`consistency_k` · `intent_azami_saniye`).
`features.yml` + `Settings` birlikte kullanmak **tek düğme için iki mekanizma** = `KAT-1`
ihlali. ⊙ Ve `FAZ 2`'yi doğuran **ölçülmüş kusur yok**; planın kendi zarar kontrolü
*«faz etkisiz teslim edilir»* diyor 🅗.

### `2.4` ZATEN VARDI — ㊷ **on üçüncü** kez

`typo_correct` her düzeltmeyi `{"kind": "auto"|"suggest"}` yazıyor — bu tam olarak
`Karar.OTO_ICRA` / `Karar.GOSTER`, **dört** üretim noktasında. Yeni bir `_meta.karar`
alanı ㊲ *aynı işin iki satırı* olurdu.

### Teslim: **ertelemenin kapısı**

⊘ bir sonuçtur, ama **kapısız bir ⊘ bir niyettir**.
`tests/test_marj_kapisi_on_kosullari.py` — **5 yüklem**, ertelemenin dayandığı üç olguyu
kilitler; biri değişirse ⊘ **kırmızıyla** düşer.

🅑 **İki mutasyon:** ① `cube_tie_candidates`'in ölçüsünü ayrıştır (**1 kırmızı**)
② `_match_cube`'a `get_settings()` koy (**1 kırmızı**). İkisi de `diff` ile geri alındı.

📌 **Sırada: `2.3`** — `D4` proaktif sınır deseni **var** (`ask.py:3374`) ama
**bağlamsızlık** dalına bağlı, `SINIR` kararına değil.

### ⟳ `§10` EKİ — `FAZ 2.3` de ertelendi · **`FAZ 2` KAPANDI** *(hepsi gerekçeli)*

Tetikleyici ancak *«eşleşmeyen sözcük»* olabilirdi ve sinyal canlıda **temiz** çıktı
(*«nedir acaba»* · *«ne kadar oldu»* → `bilinmeyen` **boş**; yalnız *«zurnalama»* gibi
gerçek eşleşmezler görünüyor). ⚠ İlk itirazım (*«dolgu sözcükleri kirletir»*) **yanlıştı**
③ — bu oturumda **beşinci** kez kendi beklentim ölçümle düzeldi.

Ama liste **kullanılamaz**, üç ölçülmüş sebeple:

| # | sebep | kaynak |
|---|---|---|
| ① | liste **Türkçe sözlüğe** dayanıyor; Arapça/İngilizce soruda **her sözcük** bilinmeyen görünür 🆊 | `islev_sozcukleri.py` — **E turu, dört kanıt** |
| ② | depo listeyi **yanlış araç** ilan etmiş, kapanış koşulu `§56`, sonra dosya **silinir** | aynı dosya: *«bir listeyi uzatmak, listenin yanlış araç olduğunu gizler»* |
| ③ | sınır beyanı **zaten var** ㊷ — *«"X" başka bir konu gibi görünüyor»* | `ask.py` üretici |

⊙ **Ön koşul: `§56`.** Kapandığında `2.3` yeniden değerlendirilir 🅗.

**Kapı büyüdü: 7 yüklem.** Yeni ikisi 🅑 mutasyonla kanıtlandı — ① sınır beyanının
üreticisini değiştir (**1 kırmızı**) ② `§56`'yı belgeden sil (**1 kırmızı**).

### ⟳ BORÇ ③ ZATEN ÖDENMİŞ — ㊷ on dördüncü kez

`netlestirme_sorusu` **çağrılıyor**: `ask.py:1454`. Borç listem bayatmış 🅟.
Dal `note=soru` **ve** `next_steps=adimlar` döndürüyor — yani soru **seçeneğiyle**
geliyor (`§TZ`: *«beyanın yanında bir tık olmalı»*).

📌 **`FAZ 2` ✅ (kapandı):** `2.1`⊘ `2.2`⊘ `2.3`⊘ `2.4`㊷ `2.5`⊘ — **beşi de gerekçeli**,
üçü **kapıya bağlı**. Sırada **`FAZ 3`+`FAZ 6` (aynı demet)**.

---

## §11 · `FAZ 3` — **SIRA DÜZELTİLDİ: `FAZ 5` ÖNCE** *(2026-08-13)*

⚠ **Kendi demet varsayımım yanlıştı** ③ *(altıncı kez)*: `FAZ 3`+`FAZ 6` aynı demet
değil — planın kendi satırı **`FAZ 6` 🔴 `FAZ 5`'e bağlı** (`GET /oneri` öneri motorunun
`Aday[]`'ini döner). Aynı demet olan **`6.1`+`6.2`**'dir (uç + FE tüketicisi).

### ① Kanalın yakın vadede TÜKETİCİSİ YOK

`FAZ 5` gelmeden `_aday_var`'ın gerçek okuyanı doğmuyor. Geriye tek aday tüketici `3.6`
kalıyor ve o da ② yüzünden yapılamaz. Tüketicisiz kanal 🆘 *«yazılmış ama bağlanmamış»* —
bu depoda **beş kez** ölçülmüş bir hata. ⊙ Bu bir erteleme değil **sıra düzeltmesi**:
`FAZ 5` → `FAZ 3`+`FAZ 6` **birlikte**, kanal **tüketicisiyle doğsun**.

### ② `3.6` iki KASITLI tanımı birleştirirdi — `2.2` ile aynı sınıf hata

| | nerede | ölçüt |
|---|---|---|
| **kıran** | `_match_cube` | `_longest_syn_hit` üzerinde **marj ≥ 4 harf** |
| **tanımlayan** | `cube_tie_candidates` | `(harf, ölçü-eşleşme)` ikilisinde **TAM EŞİTLİK** |

2 harflik fark: kıran için *«kıramadım»*, tanımlayan için *«eşit değil»* → chip
**basılmaz**. Kasıtlı, ve fonksiyonun kendi cümlesi: *«kanıt eşit değil → orta güven →
Intent-JSON'ın işi.»* `3.6` bu ayrımı silseydi yakın-beraberlikler chip'e döner,
**garsonun işi elinden alınırdı**. Planın kendi uyarısı zaten *«ölçemezsen ayır ve
ertele»* diyordu; ölçüldü, ölçüm **ayırmayı** söyledi ㊸.

⚠ Prob maliyeti (`_TIE_MAX_DENEME=8`, her deneme **tam `route()` koşusu**) *«hangi
cube'lar eşit»* için değil **ayırt eden soru** için ödeniyor — yan kanal onu **ikame
edemez**; ederse chip **metinsiz** kalır.

### Teslim: ön koşul kapısı — erteleme **kendi kendini uygular**

`tests/test_aday_yan_kanali_on_kosullari.py` — **5 yüklem**. 🔴 En önemlisi
`test_yan_kanal_TUKETICISIZ_ACILAMAZ`: `_aday_var` eklenirse **okuyanı da** eklenmeli,
yoksa kırmızı. ㊻

🅑 **İki mutasyon:** ⓐ `esitler` süzgecini marja çevir (**1 kırmızı**) ⓑ `_aday_var`'ı
okuyansız aç (**1 kırmızı**). İkisi de `diff` ile geri alındı.

⚠ ㊱ Kapı ilk yazılışında `route(q, schema)` diye **uydurma ad** taşıyordu; ölçülen imza
`route(question, schema, liste_kirilimi)` — düzeltildi.

📌 **Sırada `FAZ 5` — öneri motoru.** Ön koşulu `FAZ 0` eşiğiydi ve **karşılandı**
(`Recall@3 %89,5` 🟢). ⚠ `FAZ 0`'ın ikinci bulgusu bağlayıcı: **mutlak eşik YOK**.

---

## §12 · `FAZ 5` — ARAŞTIRMA + ÖN KOŞUL KAPISI *(2026-08-13, motor **henüz yazılmadı**)*

🔴 **`FAZ 5` BİTMEDİ.** Bu tur araştırma + ön koşulun kilitlenmesi yapıldı; motor
(`app/oneri.py`) **sonraki turda** yazılacak ve 🔴 **`FAZ 6` ile aynı demette** teslim
edilecek — `FAZ 3`'ün bulgusu gereği (**tüketicisiz yetenek doğurma** 🆘).

### ㊷ temiz çıktı

`app/oneri.py` **yok**, `lab/oneri_indeksi.py` **yok** — faz gerçekten yeni. Yeniden
kullanılacaklar ölçüldü: gömme yolunun üretim sahibi **`app/vqr.py`** (`KAT-1`: üçüncü
bir gömücü yazılmayacak) · yetki süzgeci `control_plane/authorize.py:141` · yetim uç
kapısı tavanı **8**.

### 🔴 Ölçülen kusur: `_embedder()`'ın docstring'i BAYATTI — ve YÜK TAŞIYORDU

`vqr._embedder()` *«fastembed e5-small»* diyordu; gövde (`:86`)
`intfloat/multilingual-e5-large` yüklüyor ve modül başlığı sebebini yazıyor
(*«fastembed e5-small'ı desteklemiyor»*).

⚠ ③ **Bu bir yanlış alarmla bulundu** *(yedinci kez)*: docstring'i okuyup *«ön koşul
başka modelde ölçülmüş»* sandım; **gövdeye bakınca** ikisinin de e5-large olduğu
görüldü. Yani `FAZ 0`'ın `%89,5`'i **taşınabilir**. Ama cümle yük taşıyordu 🅟: okuyan
*«üretim small»* sanarsa eşiği geçersiz sayardı. **Düzeltildi.**

### Teslim: ön koşul kapısı ㊻

`tests/test_oneri_on_kosulu_model_kimligi.py` — **3 yüklem**:
① üretim gömücüsü ile ölçüm aracının modeli **aynı** (🅕 *sürümsüz ölçüm taşınamaz*)
② düzeltilen docstring **geri bayatlamıyor**
③ `FAZ 0` raporu yerinde, `Recall@3 ≥ %85`, ve **payda ≥ 19** 🅜

🅑 **Mutasyon:** üretim modelini `e5-small`'a çevir → **1 kırmızı**. `diff` ile geri alındı.

⚠ 🅬 Kapı ilk yazılışında düz `recall@3` aradı ve `None` buldu — gerçek şekil **ayak
başına** iç içe (`{"vektor": {"recall@3": 89.5, "payda": 19}}`). Ad **dönen nesneden**
öğrenildi.

📌 **Sonraki tur: `app/oneri.py`** — `5.1` saf `ara()` · `5.2` **`authorize()` sıralamadan
ÖNCE** (fazın tek güvenlik kalemi) · `5.3` leksik edge n-gram · `5.8` gömücü soğuksa
leksik kipe düş. Sonra `5.4–5.7` ve **`FAZ 6` aynı demette**.

---

## §13 · `FAZ 5` MOTORU + `FAZ 6` BAĞI — **ZİNCİR TAM** *(2026-08-13)*

`app/oneri.py` yazıldı **ve aynı turda bağlandı**. Zincir: `app/oneri.py` →
`GET /oneri` (`app/routers/oneri.py`) → `getOneri()` (`api-client.ts`) →
`OneriSeridi.tsx` → `ChatPanel.tsx`. **262 ✅**.

### 🔴 Üç kapı, üçü de aynı şeyi söyledi: **BAĞLA**

Motoru yazınca **üç** kapı sırayla kırmızı verdi ve her biri bir kaçış yolunu kapattı:

| kapı | ne dedi | benim ilk tepkim | doğrusu |
|---|---|---|---|
| `test_g_yetim_modul_kapisi` | modülün çağıranı yok 🆎 | *«gerekçe yazayım»* | ⛔ **tavan yalnız artışı yasaklıyor** — gerekçe sayıyı düşürmez |
| `test_g_yetim_uc_kapisi` | uç FE'de geçmiyor (tavan 8) | — | uç **tek başına** da yetmez |
| `test_uc_yetim_degil` | **ölü sarmalayıcı**: `getOneri` export edildi, çağıranı yok | *«`SARMALAYICI_MUAF`'a ekleyeyim»* | ⛔ o liste **bugüne dek boş** — ilk muafiyeti bir UI işi için açmam |

㊲ Depo bu hatayı **üç ayrı katmanda** kapıya bağlamış: modül · uç · sarmalayıcı.
Üçünün ortak cümlesi: *«yazıp bağlamamak bir hata değildir; bağlamadığını söylememek
hatadır»* — ve **söylemenin bedeli, bağlamaktan pahalı olacak şekilde** ayarlanmış.

### 🔴 `5.2` — planın adı YANLIŞTI ㊱, mekanizma düzeltildi

Plan *«`authorize()` süzmesi»* diyordu. Ölçüldü: `authorize(principal, action, resource)`
**eylem düzeyi** (Katman A) bir kapıdır ve izin varsa **sessiz döner** — kaynak başına
süzemez. Kaynak başına yetki **Katman B**'dedir: `katman_b.karar(referanslar, izinliler)`,
**saf** fonksiyon, ve *«yapılandırılmamış»* (`None`) ↔ *«boş allowlist»* ayrımını **o**
taşır 🆋. `oneri.terimler()` onu **çağırır**; ikinci bir yetki kuralı yazılmadı (`KAT-1`).
Küp→model bağı **`base_object`** (`wren_service.py:793`).

### Yazılı sayılar — ve hangisinin kalibre OLMADIĞI

* `_RRF_K = 10` — literatürün `k=60`'ı **uzun** listeler içindir; kısa havuzda `1/61`
  ile `1/70` arasındaki fark **binde bire** iner ve füzyon **hiçbir şey sıralamaz**.
  🅖 **Kalibre değil, seçilmiş** — kalibrasyonu `FAZ 0` paydasının 19→30–40 büyümesine bağlı.
* `_HAVUZ = 20` · `VARSAYILAN_LIMIT = 7` (`6.4`) · debounce **200 ms** (`6.4`).
* ⚠ **Mutlak kosinüs eşiği YOK** — `FAZ 0`: gürültü *«vardya»* **0,851** aldı. Vektör
  ayağı yalnız **sıra** üretir, ve bunu bir kapı **mutasyonla** tutuyor.

### Kanıt

`tests/test_oneri_motoru.py` — **8 yüklem**. 🅑 **İki mutasyon:** ⓐ yetki süzgecindeki
`continue`'yu kaldır → **2 kırmızı** (envanter sızıntısı yakalandı) ⓑ vektör ayağına
`skor > 0.8` ekle → **1 kırmızı**. İkisi de `diff` ile geri alındı.

📌 **Kalan (`FAZ 5`):** `5.5` sıklık önceliği · `5.7` `lab/oneri_indeksi.py` + **tazelik
damgası** · `5.9` boş girdi (son bakılanlar). **Kalan (`FAZ 6`):** `6.6` tuş (`useFeature`)
· `6.7` marj kapısının üç çıkışı ekranda ayırt edilebilir. Plan kapısı `②` (`p95 < 300 ms`)
ve `④` (bayat indeks beyanı) **`5.7` ile birlikte** ölçülebilir 🅗.

---

## §14 · `5.7` İNDEKS — **BAYATLIK BEYAN EDİLMEDİ, İMKÂNSIZ KILINDI** *(2026-08-13)*

**Ölçülen maliyet:** her `/oneri` isteği katalogdaki **136 ölçü** etiketini yeniden
gömüyordu. Debounce (200 ms) bunu seyreltir, **kaldırmaz**.

**Çözüm — ve planın maddesinden bir adım ileri 🅐:** plan *«tazelik damgası»* istiyordu;
bir damga bayatlığı **beyan eder**. Burada önbellek **şema sürümüyle anahtarlı**
(`schema["version"]` — `contracts.py:75`'in `mdl_version` kıyasıyla aynı kaynak): sürüm
değişince eski girdi **okunamaz**, yani *bayat* diye bir hâl **doğmaz**.
*Bir değişmezi ilan etmek onu kurmaz; anahtarı değişmezin kendisi yapmak kurar.*

⊘ **Diskte artefakt YOK** ⑪ — bu depo bir kez gitignore'lu bir derleme artefaktından
okuyup aynı kaynakta farklı sayı görmüştü. Önbellek süreçle doğar, süreçle ölür.
Kapı bunu da tutuyor (`oneri.py` içinde `open(`/`Path(`/`np.save`… **yasak**).

Uç `"indeks": {"durum": "taze|yok|kapali", "surum": …}` **beyan ediyor** (`④`).

### 🔴 Bu turda ÜÇ kez kendi işim kusurlu çıktı — üçünü de kapı/mutasyon söyledi

| # | kusur | nasıl yakalandı |
|---|---|---|
| ㊲ | anahtar **iki yerde** kuruluyordu (`_vektor_sira` `"v1\|3"`, `indeks_durumu` düz `"v1"`) → durum **hep «yok»** | kapının **ilk koşumu** |
| 🅯 | yüklem `_INDEKS`'e elle girdi koyuyordu; gömücü kapalı olduğu için **yük taşıyan yol hiç koşmuyordu** 🆎 → **iki mutasyon da hayatta kaldı** | 🅑 mutasyon |
| ㉘ | *«aday kümesi değişti»* vakasında **sayı da** değişiyordu → anahtar zaten ıskalıyor, kimlik hizası **yalıtılmamış** → mutasyon **hayatta kaldı** | 🅑 mutasyon |

Üçüncüsü için **eşit ölçü sayılı iki küp** fikstürü kuruldu — ayırt edici vaka budur.

🅑 **İki mutasyon, ikisi de ısırıyor:** ⓐ anahtardan sürümü düşür → sürüm değişince
**yeniden gömmez** ⓑ kimlik hizası kontrolünü düşür → farklı aday kümesi **eski
matrisi** kullanır (skorlar **yanlış adaya** atanır).

⑯ komşu: `oneri` · `yetim` · `modul_buyume` · `vqr` · `katman_b` → **205 ✅**.

📌 **Kalan:** `5.5` sıklık önceliği (⚠ kaynak **kodda** aranacak, `interaction_log`
probu **yasak**) · `5.9` boş girdi · `6.6` tuş · `6.7` üç çıkışın ayırt edilebilirliği ·
plan kapısı `②` `p95 < 300 ms` (artık **ölçülebilir**: önbellek sonrası istek başına
**1** gömme).

---

## §15 · `5.5`⊘ · `5.9`✅ · `6.6`✅ · `6.7`⊘ — **FAZ 5 ve FAZ 6 KAPANDI** *(2026-08-13)*

**241 ✅ · 1 atlandı.** İki madde uygulandı, ikisi **gerekçeli ⊘** ve **kapılı** ㊸.

### `6.6` TUŞ ✅ — ve planın çaresi **gereksizmiş** ㊱

Plan demo için `localStorage` geçersiz kılması öneriyor, kendi uyarısını da yazıyordu:
*«`§40.3` A/B kaybı»*. Ölçüldü: ön uçta **`useFeature`** zaten var
(`src/lib/useFeature.ts`, açılışta bir kez `/features`). Bayrak **normal kanaldan**
akıyor → **A/B korunuyor** 🆝. `localStorage` yazılmadı.

`oneri_katmani` **üç yerde** kayıtlı oldu — ve üçünü de birer kapı istedi:
`FLAG_REGISTRY` (`on_sarti` ile) · `demo/packs/features.yml` (**açıkça `"off"`** —
kapının cümlesi: *«yokluk ile `off` çözümlemede aynı, okuyucu için değil»*) · rollout
yüzeyi. Varsayılan **kapalı** ve bu bir **karar**: planın `②` kapısı (`p95 < 300 ms`)
**henüz ölçülmedi**; ölçülmemiş bir hız iddiasıyla tuş açmak, kalibre edilmemiş bir
sayıyı güven diye satmakla aynı sınıftır.

🔴 **Asıl şart «çizmemek» değil, «ağa çıkmamak»** 🆀: bayrak kontrolü `fetch`'in
**önünde** ㊴ ve bu **mutasyonla** kanıtlandı (koruma kaldırılınca kapı kırmızı).

### `5.9` SON BAKILANLAR ✅ — yeni depo **açmadan**

Kaynak `temellendirme.olcu` — makbuzun *«ne anladım»* alanı, yani kullanıcının
**gördüğü** ad (`toplam_fire_kg` değil *«fire»*) 🅬. `sonBakilanEtiketler(threads)`
sohbetin kendi kartlarından türetiyor: `localStorage` yok, sunucu yok, senkron yok.

⚠ Planın öteki iki kaynağı (*«en çok sorulanlar»* · *«dikeyin çekirdek 5'i»*)
**uygulanmadı** — ikisi de `5.5`'in bulunmayan ölçüsüne dayanıyor.

### `5.5` SIKLIK ⊘ — **ölçü kodda YOK** ㉙

* `stats.py:51` → `select(InteractionLog.kind, func.count())` — sayım **`kind` başına**,
  **ölçü başına değil** ㊺.
* `kaset.py::sayac` bir **test kaseti** sayacı, ürün telemetrisi değil.
* `metadata.yml` şemasında ölçü başına kullanım alanı yok.

Ölçülmeyeni sıralamaya katmak uydurulmuş bir sayıyı katmaktır ㊱ — üstelik `_RRF_K`
zaten **kalibre değil** 🅖; ikinci bir kalibresiz terim, iki bilinmeyeni birbirine
dayamaktı.

### `6.7` ÜÇ ÇIKIŞ ⊘ — **öznesi yok** ㊻

Öznesi **marj kapısı**; o kapı `FAZ 2`'de gerekçeli ⊘ oldu. Olmayan bir kapının
çıkışlarını ekranda ayırt etmek mümkün değil; öyleymiş gibi rozet çizmek 🆂 *beyanı
koşula bağlayıp süs yapmak* olurdu. ⊙ Şeridin **kendi** üç hâli (`kip`,
`indeks.durum`) beyanlı ama bu `6.7`'nin **karşılığı değil** ve öyle sayılmıyor 🅫.

### İki ⊘ de **kapılı** — ertelemeler kendi kendini iptal eder

`tests/test_oneri_tus_ve_sonbakilanlar.py` (**6 yüklem**): `InteractionLog`'a
`olcu`/`measure` kırılımı doğarsa `5.5` ⊘'sü **kırmızı**; `Settings`'e `marj_esigi`
girerse `6.7` ⊘'sü **kırmızı**.

⚠ 🅞 Kapı ilk koşumda **kendi açıklamamı** yakaladı: `threads.ts`'te geçen tek
`localStorage`, *«`localStorage` yok»* diyen **yorum satırıydı**. Yüklem bir **söz**
değil bir **kullanım** (`localStorage.`) arayacak şekilde düzeltildi.

📌 **Kalan:** plan kapısı `②` **p95 < 300 ms** → sonra `FAZ 7` (⊘ demo dışı — planın
kendi kararı, **doğrulanacak**) → `FAZ 8` hasat.

---

## §16 · KAPI `②` **p95 ÖLÇÜLDÜ** · `FAZ 7` ⊘ **DOĞRULANDI** *(2026-08-13)*

### `②` — gerçek gömücüyle, ve **soğuk sayı gizlenmedi**

`lab/oneri_p95.py` · `intfloat/multilingual-e5-large` · **136 terim** · payda **90**:

| ölçüm | değer |
|---|---|
| kip | **vektor** *(🅕 leksik bir sayı buraya taşınamaz)* |
| ılık **p50** | **39,63 ms** |
| ılık **p95** | **49,23 ms** — eşik **300 ms** ✅ (**≈6× pay**) |
| soğuk (ilk istek) | **1.514,5 ms** |

🅖 **Soğuk sayı eşiğin ÜSTÜNDE ve yayına yazıldı.** İlk istek 136 etiketi gömer;
süreç × şema sürümü başına **bir kez**. Azaltma yolu **var ve uygulanmadı**: `main.py`
gömücüyü zaten arka planda ısıtıyor (`_warm`), indeks de oradan ısıtılabilir. ⊘ Şimdi
yapılmadı çünkü ısıtma bir **şema** ister ve şema **istek başına** (tenant'a göre)
çözülür — ısıtmanın **doğru yeri** ölçülmeden seçilemez ㊴.

⚠ ㊱ Araç ilk yazılışında `WrenService()` diye çağırdı ve `TypeError` aldı (imza **üç**
zorunlu argüman ister); kurulum `lab/oneri_olcum.py:211`'den **ödünç alındı**.

### `FAZ 7` ⊘ — **devralınmadı, doğrulandı** ㉓

Planın gerekçesi iki **doğrulanabilir** iddiaya dayanıyordu; ikisi de ölçüldü:
`§40.4` **var** (`:2141`) · `§34/Adım 7` **var** (`:1958`) ve alt maddeleri
(`ChatPanel.tsx` · `ReportCard.tsx` · `plan_semasi` · pill sözleşmesi ·
`test_pill_niyet_aynasi.py`) **duruyor**. Yani ⊘ bir **unutma** değil bir **karar**,
ve geri dönüş adresi yazılı.

### Kanıt

`tests/test_oneri_p95_ve_faz7.py` — **4 yüklem**: ① rapor **vektör** kipinde ve p95
eşiği geçiyor (payda ≥30 🅜) ② soğuk maliyet raporda **görünüyor** ③ `§40.4` +
`§34/Adım 7` **duruyor** ④ `Adım 7` altında **iş** var (`DOSYA`/`SÖZLEŞME`/`KAPI`) 🆚.

🅑 **İki mutasyon:** rapor `kip=leksik` → **kırmızı** · `p95=310 ms` → **kırmızı**.

📌 **Kalan tek faz: `FAZ 8` — hasat döngüsü** (`FAZ 6`'ya bağlıydı, **artık açık**).
Alt maddeleri: `8.1` tıklama kaydı · `8.2` 🔴 **konum yanlılığı** (yalnız 1. sırayı
**atlayan** tık güçlü sinyal) · `8.3` `ε` karıştırma · `8.4` *«tıklamadı»* → negatif ·
`8.5` `sinonim_onerici.kuyruga_koy(approved=False)` **mevcut hat** · `8.6`
`lab/sozluk_hasadi.py` **mevcut koşucu**. ⊙ `FAZ 8`'in tıklama kaydı, `5.5`'in
bulunamayan sıklık ölçüsünü **doğurabilir** — ikisi aynı borcun iki ucu.

### ⚠ `§16` EKİ — **İKİ KAPI ARTEFAKTA BAĞLI ve BAŞKA AĞAÇTA ATLANIR** ⑪🅣

Commit sırasında ölçüldü: **`backend/lab/reports/` gitignore'ludur.** Yani
`oneri_p95.json` ve `oneri_olcum.json` **depoya girmiyor**, ve onları okuyan iki
yüklem başka bir çalışma ağacında (ya da temiz bir klonda) **`skip`** verir:

* `test_oneri_p95_ve_faz7.py::test_p95_RAPORU_YERINDE_ve_ESIGI_GECIYOR`
* `test_oneri_on_kosulu_model_kimligi.py::test_FAZ0_raporu_YERINDE_ve_esik_KARSILANDI`

⊙ Bu **`d11` ile aynı sınıf** bir durumdur (sertifika gitignore'lu `demo/wren-project/
target/`'te). Ve 🅣 *bir kapının yeşili kapsamıyla sınırlıdır*: burada yeşil, orada
**sessiz**.

⊘ **Artefaktı depoya koymak çözüm değil** ⑪: bu depo bir kez *«gitignore'lu bir
derleme artefaktından okuyan ölçüm»* yüzünden aynı kaynakta farklı sayı gördü —
commit'lenen bir ölçüm raporu **bayatlar** ve bayat hâliyle **yeşil** verir.

📌 **Doğru çözüm ölçümün kendisini taşımaktır, dosyayı değil** 🅕: sayılar bu durum
belgesine **yazıldı** (p95 **49,23 ms** · payda **90** · kip **vektor** · soğuk
**1.514,5 ms**), ve `skip` mesajı hangi komutun koşulacağını **söylüyor**. Kapı bir
**gerileme** kapısıdır, bir **kanıt taşıyıcısı** değil.

⚠ Kaydedildi: bu, kapıların kapsamı hakkında bir **borç** — ve bilinerek taşınıyor 🅖.

---

## §17 · `FAZ 8` — `8.1`·`8.2`·`8.4`·`8.5`✅ · `8.3`⊘ · `8.6` **AÇIK** *(2026-08-13)*

**316 ✅ · 1 atlandı.** 🔴 **`FAZ 8` henüz bitmedi** — `8.6` (koşucunun tıklama
kaynağını okuması) kaldı.

### ㊷ doğrulandı: planın *«mevcut»* dedikleri **gerçekten mevcut**

`app/sinonim_onerici.kuyruga_koy` **var** ve `approved=False` gerçekten **sabit**
(parametre olarak dışarı açılmamış) · `lab/sozluk_hasadi.py` **var** ve bugün
**şemadan** çıplak alanları okuyor.

### 🔴🔴 `8.2` KONUM YANLILIĞI — asıl iş burada

`app/hasat.py` **saf**: `sinyal(Tiklama) -> guclu|zayif|negatif`.

| olay | sinyal | sözlüğe girer mi |
|---|---|---|
| **1. sırayı ATLAYAN** tık (`konum ≥ 1`) | 🟢 **güçlü** | **evet** — sıralamaya **rağmen** seçildi |
| **1. sıraya** tık (`konum == 0`) | ⚪ zayıf | **hayır** — konumla da açıklanabilir |
| hiçbirini seçmedi (`-1`) | 🔴 negatif | hayır; **sayılır** (`negatif_kanit`) |

Kapı `test_hasat_konum_yanliligi.py` **9 yüklem**; asıl yüklem
`test_NAIF_SAYIM_KENDINI_BESLERDI`: **aynı kayıtları** iki kuralla okuyor — naif kural
50 aday üretiyor, bizimki **sıfır**. Ayrışmasalardı koruma **olmazdı** ㉘.

🅑 **İki mutasyon:** 1. sırayı `GUCLU` say → **2 kırmızı** · tekilleştirmeyi düşür →
**1 kırmızı**.

### `8.1` TIKLAMA KAYDI — **yeni tablo AÇILMADI** 🆝

`POST /oneri/tik` → `InteractionLog`'a `kind="oneri_tik"`. Denetim kanalı **zaten**
bu; ikinci bir depo aynı olayın iki sahibi olurdu (`KAT-1`). `§101.1`: kayıt
başarısız olsa da istek `{"kaydedildi": false}` ile döner — bir telemetri hatası bir
ürün hatası **değildir**. FE tarafı **aynı turda** bağlandı: `oneriTik()` +
`OneriSeridi.sec()` — fare ve klavye **tek kapıdan** geçiyor ㊲, ve `Esc` `8.4`'ün
negatif sinyalini **gönderiyor** (sessizce kapatmak o bilgiyi çöpe atardı 🆆).

### 🔴 Bir depo kapısı KENDİ AÇIKLAMAMI yakaladı — ve kapı **güçlendirildi** ②🅞

`test_sinonim_onerici.py::test_HICBIR_ASK_YOLUNDAN_cagrilmiyor` kırmızı verdi: `hasat.py`
kuyruğun sahibini **docstring'inde** anmıştı; dosyada **hiçbir çağrı yok**. Kapı bir
**kelimeyi** ölçüyordu, bir **çağrıyı** değil.

⚠ **Zayıflatılmadı, kesinleştirildi:** metin araması bir **dinamik** sızıntıyı da
yakalıyordu (`importlib.import_module("sinonim_onerici")` gibi bir **dize**), yani
salt `ast` yetmezdi ②. Çözüm ikisini birden tutmak: **docstring'ler ayıklanır**, kalan
kod (dize sabitleri **dâhil**) yine metin olarak aranır.

🅑 **İki sızıntı denendi, ikisi de yakalandı:** gerçek `import` → **kırmızı** · dize
sabiti → **kırmızı**.

### ⊘ `8.3` (`ε` karıştırma) — **ölçülemez, bu yüzden yapılmadı** ㊸

`ε`'nin faydası ancak *«karıştırılmış turlarda güçlü sinyal oranı arttı mı»* diye
ölçülür — ve o ölçüm **tıklama verisi** ister, yani `8.1`'in **toplamış olmasını**.
Ölçmeden konan bir `ε` listeyi bozar ve karşılığında **hiçbir sayı** üretmez 🆕.
Kapı `test_EPSILON_ERTELEMESI_HALA_GECERLI`: sıralamaya rastgelelik sızarsa **kırmızı**.

📌 **Kalan: `8.6`** — `lab/sozluk_hasadi.py` tıklama kaynağını da okusun
(`hasat.hasat_adaylari` → `sinonim_onerici.kuyruga_koy(approved=False)`).

### ⟳ `§17` EKİ — `8.6` BAĞLANDI · **`FAZ 8` ✅ · SEKİZ FAZIN HEPSİ KAPANDI**

`lab/sozluk_hasadi.py` artık **iki kaynak** okuyor: ① katalogdaki **çıplak alanlar**
(*«sözlüğümüz eksik»*) ② **kullanım** — `InteractionLog(kind="oneri_tik")` →
`hasat.not_oku` → `hasat.hasat_adaylari` → `sinonim_onerici.kuyruga_koy(approved=False)`.
İkisi ayrı sayılıyor 🆋 (`rapor["tiklama_aday"]` yeni alan); mevcut yol **bozulmadı**
(`KURAL B`) ve kuru mod hâlâ **hiçbir şey yazmıyor**.

⚠ 🅖 **Bu kaynak bugün BOŞ dönebilir ve bu bir kusur değildir:** `oneri_katmani`
bayrağı **kapalı**, yani henüz tıklama üretilmiyor. *Bir borunun boş olması, bağlı
olmadığı anlamına gelmez.*

### 🔴 ㊲ İki ayrı tuzak, ikisi de **aynı kusurun** iki yüzü

**① Not biçimi iki sahip olacaktı.** `note` gövdesini **yazan** HTTP ucu, **okuyan**
`lab/` koşucusu olacaktı — biri değişirse öteki **sessizce yanlış** okurdu ve sözlüğe
**yanlış eşleşme** yazılırdı. Biçimin tek sahibi `app/hasat.py` (`not_yaz`/`not_oku`);
iki taraf da **çağırıyor**. ⊙ Ve `not_oku` sinıfı **nottan okumaz, yeniden hesaplar**:
not bir **kayıt**tır, bir **karar** değil — kural değişirse eski kayıtlar **yeni
kuralla** okunur ㉓.

**② İKİNCİ bir kapı, BİRİNCİYLE aynı kusuru taşıyordu.** `test_a_sozluk_hasadi.py`
de `app/` ağacında **metin** arıyordu ve `app/hasat.py`'yi **açıklaması** yüzünden
yakaladı 🅞 — tıpkı `test_sinonim_onerici.py` gibi. Yani `E-8` yasağını **iki kapı**
tutuyor ve **ikisi de** aynı biçimde yanılıyordu.

⊙ Ayıklayıcı **kopyalanmadı**, `tests/_kod_ayikla.py`'ye çıkarıldı ve **ikisi de onu
çağırıyor** (`KAT-1`). Kopyalansaydı biri düzeltilir, öteki eski hâliyle kalırdı.
⚠ Salt `ast` yetmez ②: `importlib.import_module("sozluk_hasadi")` gibi bir **dize
sabiti** de sızıntıdır — yalnız **docstring'ler** düşürülür, dizeler **kalır**.

🅑 **Kanıt:** `app/hasat.py`'ye gerçek bir `from lab import sozluk_hasadi` konunca kapı
**kırmızı** verdi; geri alındı. ⑯ komşu: **316 ✅ · 1 atlandı**.

📌 **SEKİZ FAZ DA KAPANDI.** Sırada kullanıcının bağlayıcı kuralı: **ajan denetimi
(40 kontrol)** → **tam kapı + demet kapısı** → **≥20 curl senaryo/thread turu**.

---

## §18 · DEMET KAPSAMI **YENİDEN ÖLÇÜLDÜ** — taşıdığım sayı bayatmış 🅟 *(2026-08-13)*

Tam kapıyı kurmadan önce kapsam ölçüldü ve **taşıdığım sayı yanlış çıktı**:

| | taşınan (bayat) | **ölçülen** |
|---|---|---|
| `294eb67..HEAD` değişen dosya | *«606»* | **680** *(backend **624** · FE **18** · belgeler **25**)* |
| aralıktaki commit | *(anılmıyordu)* | **552** — hepsi tek yazar, **sıfır** merge |

⚠ ③ İlk okumam *«552 commit ama ben 13 attım, bir şey ters»* diye alarm verdi. Yeniden
sayınca görüldü: `294eb67` oturum **başındaki** anlık görüntüden geliyor ve o görüntü
**çok eski** — aradaki 552 commit bu uzun oturumun **tamamı** (`G0`…`FAZ 8`). Ayrık bir
dal ya da başka bir geliştiricinin işi **yok**; `merge-base --is-ancestor` **EVET** dedi
ve yazar **tek**.

⊙ Sonuç: *«hedefli»* demet kapısı artık **624 backend dosyası** seçiyor — yani pratikte
**tam süite yakın**. Bu bir kusur değil, kapsamın **büyümesi**; ama sayıyı taşımak
㉔ *raporun sayısını ölçmeden alma* dersinin bir tekrarı olurdu.

📌 Ajan denetimi **arka planda koşuyor**; iki test konteyneri **paralel koşturulmaz**
(compose kilidi `metadata.yml`'de çakışır) — tam kapı ajan bitince koşulacak.

---

## §19 · **KENDİ KAPILARIMIN ÖZ-DENETİMİ** — ne ölçüyorlar? 🅯 *(2026-08-13)*

Ajan koşarken konteynersiz bir ölçüm yapıldı: **9 kapı dosyası · 60 yüklem**, `ast` ile
sınıflandırıldı (`read_text`/`getsource`/`glob` çağıran = **metin**, ürünü koşturan =
**davranış**).

| kapı | davranış | metin |
|---|---|---|
| `kiyas_temeli_chipi` | **7** | 0 |
| `oneri_motoru` | **9** | 2 |
| `hasat_konum_yanliligi` | **6** | 3 |
| `oneri_tus_ve_sonbakilanlar` | **5** | 1 |
| `emin_miyim_tek_sahip` | 4 | 4 |
| `marj_kapisi_on_kosullari` | 2 | **5** |
| `oneri_on_kosulu_model_kimligi` | 1 | 2 |
| `aday_yan_kanali_on_kosullari` | 1 | **4** |
| `oneri_p95_ve_faz7` | **0** | **4** |
| **TOPLAM** | **35 (%58)** | **25 (%42)** |

### Bu sayı tek başına bir yargı DEĞİL ㉘

Metin ağırlıklı üç dosya tam olarak **erteleme kapıları**dır (`marj_kapisi`,
`aday_yan_kanali`, `p95_ve_faz7`). Bir ⊘'nün gerekçesi doğası gereği **belgesel ya da
yapısal**dır: *«`§40.4` duruyor mu»*, *«`cube_router` ayar okumuyor mu»*, *«sıralamaya
rastgelelik sızdı mı»* — bunlar davranışla ifade edilemez, çünkü **olmayan** bir şeyin
yokluğunu ölçerler 🆆.

### 🔴 Ama iki gerçek zayıflık var — ve yazılıyor 🅖

**① `oneri_p95_ve_faz7.py`: SIFIR davranış yüklemi.** Dördü de metin/rapor. Üstelik
ikisi **gitignore'lu artefakta** bağlı (`§16` eki) → temiz klonda **skip**. Yani bu
dosya bugün **hiçbir davranışı** korumuyor; bir **kayıt** tutuyor. Bu kabul edilebilir
ama *«p95 kapılı»* demek **fazla iddialı** olurdu 🅫 — doğrusu: *«p95 ölçüldü ve sayısı
belgeye yazıldı; kapı yalnız raporun kendisiyle tutarlılığı tutuyor.»*

**② `emin_miyim_tek_sahip::test_DORT_CAGIRAN_DA_BAGLI`** `_emin_karar(` **geçişini
sayıyor** — bir metin vekili ㊳. Çağıran *var ama erişilmez* olsa yine yeşil verirdi.
⊙ Yanında **davranış** yüklemleri var (`auto_fix` eşikleri, typo üç kademesi) ve asıl
korumayı **onlar** yapıyor; sayım yüklemi bir **erken uyarı**, bir kanıt değil.

📌 Bu bölüm bir **özür değil bir sınır beyanı**: *bir kapının yeşili kapsamıyla
sınırlıdır* 🅣 — ve kapsamı **sayıyla** yazılmadıkça o sınır görünmez.

---

## §20 · CURL TURU **HAZIRLIĞI** — 22 senaryo, her biri **beklenen gözlemiyle** *(2026-08-13)*

⚠ Bu bir **plan**dır, bir **ölçüm değildir** 🅫. Sonuçlar koşulduğunda
`belgeler/denetim/2026-08-07_CEVIRI-SOZLESMESI.md`'ye yazılacak; buraya **yazılmayacak**.

⚠ **Ön koşul:** `/oneri` ve `/oneri/tik` **bugünkü imajda YOK** (⑦ ortam≠ürün) — 1–4
ancak **imaj tazelendikten** sonra koşulabilir. 5–22 bugünkü imajla koşulabilir.

### A · Yeni yetenek (imaj tazeleme sonrası)
| # | girdi | **beklenen gözlem** |
|---|---|---|
| 1 | `GET /oneri?q=fi` | `adaylar[]` dolu · `kip` alanı **var** · her aday `kimlik`/`cube` taşıyor |
| 2 | `GET /oneri?q=` (boş) | **boş liste** — uç boş girdide aday üretmez |
| 3 | `GET /oneri?q=zzzqqq` | **boş liste**, `200` — anlamsız girdi çökertmez 🅡 |
| 4 | `POST /oneri/tik` `{konum:0}` → `{konum:2}` | `sinyal` sırasıyla **`zayif`** ve **`guclu`** 🔴 `8.2` |

### B · Sekiz fazın davranışı (bugünkü imaj)
| # | girdi | **beklenen gözlem** |
|---|---|---|
| 5 | *«RAM-3 neden düşük»* (çapasız) | `KIYASLA` fiili · akran ortalaması · **`FAZ 4`** |
| 6 | *«RAM-3 neden düşük»* (çapalı) | 11 satır · *«%10,7 düşük»* |
| 7 | *«bu yıl fire oranı»* | `source=cube` · `kanit=olculmus` |
| 8 | *«bu yıl zurnalama oranı»* | `source=cube+llm` · `kanit=probabilistik` · `temellendirme.olcu` **dolu** |
| 9 | *«bu yıl fire oranı nedir acaba»* | `bilinmeyen` **boş** — dolgu sözcükleri kirletmiyor |
| 10 | *«vardya sayısı»* | ⚠ **iki kez koş** 🅢 — garson olasılıksal, tek koşum kanıt değil |
| 11 | *«makine bazında oee»* + `«+ kullanılabilirlik»` | ikinci ölçü **eklenir**, ilki **kaybolmaz** |
| 12 | *«fire»* (iki küpte tanımlı) | netleştirme **chip'i** ya da beyan — sessiz seçim **yok** |
| 13 | *«bu yıl en yüksek 5 müşteri»* | `order`+`limit` · chip *«En yüksek 5»* **yinelenmiyor** |
| 14 | *«geçen aya göre ciro»* | `compare: mom` — `FAZ 4`'ün bağlam kuralı |
| 15 | *«2019 cirosu»* | dönem **taşınır**; `§T8` (dönem düşmesi) **yok** |
| 16 | *«sadece bu üç ayı»* (takip) | daraltma çalışır, **yanlış uyarı yok** (`§T6`) |
| 17 | *«teşekkürler»* | `0 LLM · 0 SQL` — sosyal sınıf |
| 18 | *«hava durumu nasıl»* | **dürüst red** + katalog sınırı; `cube=adhoc` **yok** |
| 19 | *«لهذا العام إجمالي الإيرادات»* | doğru dönem + ölçü — çok-dillilik (`§56`'nın alanı) |
| 20 | *«aylık üretim ve enerji tüketimini birlikte göster»* | *«birlikte»* **çapraz-konu sanılmıyor** |
| 21 | *«personel bazlı verimlilik»* | katalogsal sınır **beyan edilir** (uydurma boyut yok) |
| 22 | aynı thread'de 5 tur | *«ilişkilendiremedim»* **0 kez** — sözleşme #3 |

### Kural
Her senaryo **tek tek** koşulur, ham cevap **kısaltmadan** okunur, teşhis **sonra**
yazılır. ⚠ Yığın koşum yok; ⚠ token **her turda** yenilenir ⑩; ⚠ `10` gibi olasılıksal
vakalar **iki kez** koşulur 🅢.

---

## §21 · AJAN DENETİMİ — **DÖRT GERÇEK KUSUR, DÖRDÜ DE BENİM** *(2026-08-13)*

40 kontrolün **32'si ✅**, 6'sı ⚠, **4 gerçek kusur**. Ajanın her bulgusu **kendim
ölçülerek** doğrulandı ㉔ — hiçbiri devralınmadı.

### 🔴 KUSUR 1 — `lab/sozluk_hasadi.py` CLI'ı **ÇÖKÜYORDU** (en ağırı)

`FAZ 8.6`'da `_tiklama_adaylari()`'yi dosyanın **sonuna** ekledim; orası
`if __name__ == "__main__"` guard'ının **altıydı**. Betik kipinde guard gövdesi o
`def`'ten **önce** koşuyor → `NameError` → aracın **belgelediği tek kullanım** tamamen
kırık. Kanıt: `python lab/sozluk_hasadi.py` → `NameError: name '_tiklama_adaylari'
is not defined`. Düzeltildi; şimdi **çıkış 0**.

🔴 **Ve hiçbir kapı görmedi** 🆎: dosyadaki tüm yüklemler modülü **import** ediyordu,
`kos()`'u **koşturmuyordu**.

⚠🅑 **İlk kapım da yanlış araçtı ③:** `kos(yaz=False)`'u koşturan bir yüklem yazdım,
mutasyon **hayatta kaldı** — çünkü guard'ın altındaki bir `def` **import'ta yine
çalışır**; çökme yalnız `__main__` kipinde olur. Doğru değişmez: **guard modülün son
üst-düzey ifadesi olmalı** (`test_MAIN_GUARDI_SON_IFADE`, `ast` ile). O mutasyonu
**öldürüyor**.

### 🔴 KUSUR 2 — `test_KAPALIYKEN_UCA_HIC_CIKILMAZ` **iki yönde de yanılıyordu**

Ajan ölçtü: ⓐ koruma **silinip** metin bir **yoruma** taşınınca kapı **yeşil**
(yanlış-negatif) ⓑ davranışı koruyan **farklı bir yazım** kırmızı (yanlış-pozitif).
*Bir kapı tek bir yazımı kilitliyorsa, kilitlediği şey davranış değil biçimdir.*

⚠ Düzeltirken **ikinci kez** yanlış çapa kondu ③: `src.index("useEffect")` **import
satırındaki** sözcüğü buluyordu. Doğru çapa `getOneri`'yi **içeren** etkinin başı.
Şimdi ⓐ **kırmızı**, ⓑ **yeşil** — ikisi de mutasyonla doğrulandı.

### 🔴 KUSUR 3 — `POST /oneri/tik` kendi `§101.1` değişmezini çiğniyordu

`int(govde.get("konum", -1))` `try` **dışındaydı**: `konum:"abc"` → `ValueError`,
`konum:null` → `TypeError` → işlenmemiş **500**. Üstelik `gosterilen:"abc"` bir dizeyi
**karakterlere** açıp **üç sahte aday** üretiyordu (hasat kuyruğuna çöp kimlik yolu).
⊙ Ayrıştırma `hasat.govdeden()`'e taşındı — **asla fırlatmaz**, ve gövde biçiminin
**tek sahibi** orası (`KAT-1`). 🅑 iki mutasyon: `try/except` düşür → kırmızı; dize
koruması düşür → kırmızı.

### 🔴 KUSUR 4 — `test_yan_kanal_TUKETICISIZ_ACILAMAZ` **sessizce yeşil** veriyordu

`_aday_var` yokken `return` ediyordu: yeşili *«ölçtüm ve iyi»* değil *«hiç bakmadım»*
demekti. `pytest.skip` yapıldı — **ölçmediğini söyleyen** bir kapı 🆆.

### ㊷ Ajanın bir bulgusu bir **borcu küçülttü**

`d11`'in *«sertifika sürümlenmeli»* ön koşulu **kodda zaten ödenmiş**:
`app/fanout.py:264` sertifikaya `mdl_version` basıyor (**2026-08-02**'den beri) ve
`WrenService.mdl_version` **asla `None` dönmüyor**. Diskteki `mdl_version: None` bir
**bayat derleme artefaktı** ⑪ — kalan iş bir kod işi değil, **tek bir yeniden üretim**.
Gerekçe *«olduğundan büyük yazılmıştı»* 🅫.

### ⚠ Kalan zayıf noktalar (ajan ölçtü, borç olarak taşınıyor 🅖)

* `test_MUTLAK_KOSINUS_ESIGI_YOK` **metin** ölçüyor — değişken adlı bir eşik
  (`>= _t`) kapıdan **geçiyor** (ajan ölçtü: 11 passed).
* `test_5_5_ERTELEMESI_HALA_GECERLI` **yanlış yeri** gözlüyor: sıklık verisi artık
  `8.1` ile `InteractionLog(kind="oneri_tik")`'te **doğuyor**, ama kapı `stats.py`'ye
  bakıyor → veri aktığında **hiç kırmızı vermeyecek** ㊺.
* `features.py` `on_sarti` **bayat**: *«p95 henüz ölçülmedi»* diyor, oysa **49,23 ms**
  ölçüldü 🅟.
* `OneriSeridi.tsx` bağımlılık dizisi `[metin, kapali]` — `kapaliBayrak` **eksik**;
  bayrak açıldığı an şerit bir sonraki tuşa kadar gelmez (UX gecikmesi, güvenlik yok).
* `_INDEKS` anahtarı çok kiracılıda **aynı sayıya** düşen iki allowlist için her
  istekte yeniden gömer → ölçülen **49,23 ms tek havuzludur** 🅕.

---

## §22 · AJANIN BEŞ ⚠ MADDESİ — **hepsi kapandı, hepsi mutasyonlu** *(2026-08-13)*

| # | borç | düzeltme | 🅑 mutasyon |
|---|---|---|---|
| ① | eşik yasağı **metin** ölçüyordu | **davranış** yüklemi: vektör ayağı bir **sıralayıcıdır**, süzgeç değil — havuzdaki **her** adayı geri vermeli | ajanın **geçen** mutasyonu (`_t = …; >= _t`) → **kırmızı** |
| ② | sıklık kapısı **yanlış kaynağa** bakıyordu ㊺ | ölçüt `oneri.py`'nin **sıralamasına** taşındı; `8.1` zincirinin varlığı ayrı yüklem | — *(ölçüt değişti, gerekçe yenilendi)* |
| ③ | `on_sarti` **bayat** 🅟 | *«p95 ölçülmedi»* → **49,23 ms ölçüldü**; `beta`nın **kalan iki şartı** yazıldı | — |
| ④ | bağımlılık dizisi eksik | `[metin, kapali, **kapaliBayrak**]` | — |
| ⑤ | anahtar **sayıya** bağlıydı 🅕 | anahtar **kimliklerin özetine** (`blake2s`) bağlandı | anahtar sayıya döner → **kırmızı** |

### ① — bir metin yasağı neden davranışa çevrildi

Ajan ölçtü: `if skor[i] > 0.8` yakalanıyordu ama **değişken adlı** bir eşik
(`_t = …; if skor[i] >= _t`) **geçiyordu** (11 passed). Yani yasak yalnız **bir
yazılışa** karşıydı ㊳. Davranışsal değişmez şu: *vektör ayağı bir **sıralayıcıdır**,
bir **süzgeç değil*** — havuzdaki her adayı (tavana kadar) geri vermelidir. Hangi adla
yazılırsa yazılsın **her** eşik listeyi kısaltır ve yüklem kırılır.

### ⑤ — bir **başarım** kusuru davranış yüklemiyle yakalanamaz

Anahtar sayıya bağlıyken doğruluk **korunuyordu** (kimlik kontrolü sayesinde); bozulan
şey **isabet oranıydı**. Bu yüzden ilk mutasyon **hayatta kaldı** — ve doğru cevap
ürünü değil **kapıyı** değiştirmekti 🅑: anahtarın kendi özelliği (*«aynı sayı, farklı
kimlik → farklı anahtar»*) kapıya bağlandı.

### ③ — `beta`nın kalan iki şartı **yazıldı** 🅖

`oneri_katmani` hâlâ `off`, çünkü: ⓐ **soğuk** ilk istek **1.514 ms** (eşiğin ~5 katı),
ısıtmanın doğru yeri ölçülmedi ⓑ ölçüm **tek havuzlu**; çok kiracılı p95 **ölçülmedi**.
*Ölçülmemiş bir hız iddiasıyla tuş açmak, kalibre edilmemiş bir sayıyı güven diye
satmaktır.*

---

## §23 · TAM KAPI — **10 🔴 → 2 🔴**, ve altısı benim işim DEĞİLDİ *(2026-08-13)*

**İlk koşum: 4.900 ✅ · 10 🔴 · 44 atlandı** (4 dk 15 sn, değişen **624** backend dosyası).
Her kırmızı **kendi kapsamıyla** sınandı 🆐:

| kırmızı | sahibi | teşhis |
|---|---|---|
| `test_a14_hava_boslugu_yayini` ×**6** | **BENİM DEĞİL** | `1ee3d14` belgeyi `belgeler/denetim/`'e taşımış; bu kapının yol sabiti **atlanmış**. *Aynı commit `DOGRULUK.md`'yi taşıyıp üç kapıyı kırmıştı; bu dördüncüsüydü.* |
| `test_g_belge_dizini_taze` | **benim** | planı düzenledim, dizin bayatladı → `belge_dizini.py --yaz` |
| `test_alan_haritasi::SINIFSIZ` | **benim** | `emin_miyim`/`oneri`/`hasat` haritada yoktu |
| `test_frontend_buyume[api-client.ts]` | **benim** | `getOneri`+`oneriTik`+tipler → **+22** satır |
| `test_d11` | — | **gerekçeli**, kalıyor |

⚠ 🅣 **Altı kırmızı hedefli koşumlarda GÖRÜNMÜYORDU** — o dosya hiç seçilmiyordu.
*Bir kapının yeşili kapsamıyla sınırlıdır; ve kapsamı, seçtiğin dosyalar kadardır.*

### Düzeltmeler — hiçbiri gevşetme değil

* `a14` **adresi** düzeltildi (kapı **aynı** şeyi ölçüyor).
* Üç modül **MUTFAK**'a yazıldı: üçü de LLM çağırmaz, üçü de deterministiktir.
* FE tavanı **778 → 814** (`Δ=22`, ölçülen fazlaya **eşit** 🅜). ⚠ Bileşene çıkarmak
  **öteki kapıyı** kör ederdi (`test_uc_yetim_degil` sarmalayıcıları `api-client.ts`
  **içinde** arıyor) — bir borcu başka bir borca taşımak olurdu 🆝; gerekçe yazıldı 🅗.
* `oneri.py` → `llm._norm` geçişi `MUAF_GECISLER`'e eklendi; emsali `wren_service.py`
  ve gerekçesi **birebir aynı**: `_norm` bir **metin normalleştiricisidir**.
  🔴 **Ama bu artık İKİNCİ kez** — bir emsal ikiye çıkınca kural olmaya başlar 🆍.
  ⊙ Ölçüldü: `_norm`'u `llm`'den alan **5 modül** var. Doğru çözüm onu **ortak bir
  yardımcıya** taşımak; ⊘ bu turda yapılmadı (tek başına bir demet kapısı ister) 🅗.
  ⚠㊱ O gerekçeye ilk yazdığım sayı (*«on yedi»*) **ölçülmemişti**; ölçüldü: **5**.
  *Gerekçeye konan her sayı da bir iddiadır.*

### İkinci koşum: **4.912 ✅ · 2 🔴 · 43 atlandı**

Kalan ikisi: `d11` (**gerekçeli**) ve **yeni bir kırmızı** —
`test_a13_plan_ayrismasi_olcumu::test_SAYAC_VAR_ve_ALANLARI_TAM`.

🔴 **Ve o benim işim değil, ama gerçek:**
* **İlk** tam koşumda kırmızı **değildi**; izole koşumda **3 passed**; `-k "garson or
  plan_garson or a13"` dilimiyle **65 passed**. Yani **sıra/durum bağımlı** 🅢.
* `a9b0d45~1..HEAD` aralığında ne teste ne `app/plan_garson.py`'ye **dokundum**.
* Mekanizma ölçüldü: `SAYAC` **modül-düzeyi genel** bir sözlük; `sayaclar()` onun
  **kopyasını** döndürüyor. Tam süitte bir kod yolu ona **yeni bir anahtar** ekliyor
  ve kapı *«ilan edilmemiş alan»* diye kırmızı veriyor — yani kapı **işini yapıyor**:
  *«sessizce büyüyen bir sözleşme, denetlenemeyen bir sözleşmedir.»*

⊙ **Anahtarın adı UYDURULMAYACAK** ㊱ — tam koşumun kendi hata satırından okunacak.
Ölçüm bu turda başlatıldı; sonucu sonraki tur yazılacak.

---

## §24 · `a13` TEŞHİSİ — **AÇIK ANAHTAR UZAYI** ㊶ *(2026-08-13)*

Üçüncü tam koşum (**4.911 ✅ · 2 🔴**) hata satırını verdi ve anahtar **uydurulmadı** ㊱:

    E   assert not {'onarildi_tur1'}

### Mekanizma — ölçüldü, tahmin edilmedi

`app/plan_garson.py:343` onarım turunu **dinamik anahtarla** sayıyor:
`SAYAC[f"onarildi_tur{_tur}"]`. `sayaclar()` ise `out = dict(SAYAC)` yapıyordu — yani
**yayımlanan sözleşme çalışma zamanında büyüyordu**.

⊙ Bu yüzden kırmızı **sıra bağımlıydı** 🅢: izole koşumda onarım yolu hiç çalışmıyor,
üstelik alfabetik sırada `test_a13` kirletici `test_b4`'ten **önce** geliyor. Tam
süitte bir onarım tetiklendiği an `onarildi_tur1` beliriyor ve kapı *«ilan edilmemiş
alan»* diyor.

⚠ **İlk «125 passed» koşumum kanıt değildi** ㉘ — `-k` seçimi de alfabetik sıralıyordu,
yani `a13` yine **önce** koşuyordu. Vakayı ancak **sırayı elle kurarak**
(`test_b4 → test_a13`) yalıtabildim.

### Çözüm — kapı **gevşetilmedi**, ürün deponun **kendi desenine** uydu ㊲

Kırılım artık üst düzeye serilmiyor; `red_nedenleri` gibi **iç içe** yayımlanıyor:
`onarildi_turlere_gore: {"1": n, "2": m}`. Böylece **üst düzey anahtar uzayı kapalı**,
bilgi **kaybolmadı**, ve `test_a13` alan kümesini **tam** sayabiliyor.
`BEKLENEN_ALANLAR`'a tek bir **ilan edilmiş** alan eklendi.

⊙ Tüketiciler ölçüldü: `/stats/plan` (operatör aracı) ve iki test — ikisi de yalnız
**ilan edilmiş** alanları arıyor; `onarildi_tur*`'u okuyan tek yer `test_b4` ve o
**doğrudan `SAYAC`**'a bakıyor, `sayaclar()`'a değil. Yani değişiklik hiçbir okuyucuyu
kırmıyor.

🅑 **Mutasyon:** `out = dict(SAYAC)` geri konunca (`b4 → a13` sırasıyla) kapı
**kırmızı**; düzeltmeyle **9 passed**.

⚠ Bu kusur **benim işim değildi** ama tam kapı olmadan **hiç görünmeyecekti** 🅣 —
ve iki turdur *«süit yeşil»* diye taşıdığım sayı, o dosyayı hiç seçmeyen bir kapsamın
sayısıydı.

---

## §25 · **TAM KAPI ✅ · KORPUS ✅** — kapanış ölçümleri *(2026-08-13)*

### Tam kapı (dördüncü koşum, `--degisen` **624** backend dosyası)

**4.913 ✅ · 1 🔴 · 43 atlandı** (4 dk 17 sn). Tek kırmızı **`d11`** — **gerekçeli**
ve ㊷ ajanın bulgusuyla **küçülmüş**: ön koşulu (*«sertifika sürümlenmeli»*) kodda
**zaten ödenmiş** (`fanout.py:264`, `2026-08-02`'den beri); diskteki `mdl_version:
None` bir **bayat derleme artefaktı** ⑪. Kalan iş bir kod işi değil, **tek bir yeniden
üretim**.

⊙ Yolculuk: **10 🔴 → 2 🔴 → 1 🔴**. Altı kırmızı **benim işim değildi** (`1ee3d14`'ün
taşıdığı belge), biri **açık anahtar uzayı** ㊶, üçü benim eklediklerimdi.

### Korpus — **dört şirket de TABANLA BİREBİR**

| şirket | erişim | taban |
|---|---|---|
| boyahane | **%83** | %69 ✅ |
| atiksan | **%69** | %69 ✅ |
| gulteks | **%68** | %69 ✅ |
| gitas | **%72** | %72 ✅ |

**doğru-cube %95,6** (taban %94,4) ✅ · **semantik 558/591 = %94,4** (taban %93,5) ✅ ·
çıkış kodu **0**.

⊙ Bu tur `plan_garson.sayaclar()` **değişti** (kırılım iç içe taşındı) ve `oneri`/`hasat`
**eklendi**; korpus bu yüzden zorunluydu — küp seçimi **bozulmadı**.

📌 **Kalan:** ⑦ **imaj tazeleme** (`/oneri` ve `/oneri/tik` bugünkü imajda **yok**) →
**22 curl senaryosu** (`§20`).

---

## §26 · 🔴🔴 **ÖZ-ELEŞTİRİ: ALTYAPIYI TESLİM ETTİM, ÜRÜNÜ DEĞİL** *(2026-08-13)*

Kullanıcı frontend'e girdi ve gördüğü şey şuydu: bir-iki kelimelik, **alakasız** öneriler
(`su`, `set`), **çapa çubuğu yok**, **pill satırı yok**, **toggle yok**, ve sağdaki
besteci hiç öneri vermiyor. Haklı.

### Ne yaptım — ve planın ne dediği

| planın maddesi | plan ne diyor | ben ne teslim ettim |
|---|---|---|
| **`§3.3`** | *«MENÜ DEĞİL, **TAMAMLAMA**»* — örtük mesaj *«ne diyeceğini biliyorum»* | bir **alan adı menüsü** |
| **`§18.7`** | *«Ne gömüyoruz — **alan adını DEĞİL**»*; etiket·sinonim·küp bağlamı·birim **ayrı vektör** | ham `cube.olcu` kimlikleri gömüldü → `fi` sorgusuna `su`·`set` düştü |
| **`§5.1`** | 📌 **görünür çapa** + `[✕ bağlamı bırak]` + iki grup (`BU RAPOR ÜZERİNDE` / `YENİ KONU`) + **tam Türkçe cümleler** | tek düz liste, çapa yok, cümle yok |
| **`§5.2`** | **PILL satırı** = `Niyet`in görünür hâli, **tipli `+`** (`ölçü·kırılım·dönem·adım`) | **hiç yok** — oysa `app/niyet.py` ve alanları **hazır** |
| **`§5.3`** | pill **canlı doğrulanır**, geçersiz kombinasyon kırmızıya döner | **hiç yok** |
| **`§7 ②`** | **adlandırılmış makro**: tek öneri, arkasında N deterministik adım | **hiç yok** |

🔴 **Teşhis:** `FAZ 5`–`FAZ 8`'i *«motor + uç + kapı»* olarak okudum ve her birini kapıya
bağladım. Kapılar yeşil, sayılar doğru — ama **ürün yok**. Yeşil bir kapı, kapsamı kadar
doğrudur 🅣: benim kapılarım *«motor doğru sıralıyor mu»* diye sordu, hiçbiri *«kullanıcı
ne görüyor»* diye sormadı. Ve `🆘` dersini kendi işime uygulamadım: **tüketicisiz yetenek
bitmiş değildir** — burada tüketici vardı ama **yanlış şeyi** tüketiyordu.

⊙ Ve curl turuna geçmem sırayı bozdu: 22 senaryoyu **eksik bir ürünün** üstünde koştum.
*Bir şeyin doğru çalıştığını ölçmek, doğru şeyi yaptığını göstermez.*

### Ne yapılıyor — dört ajan, kesişmeyen dosya sahipliğiyle

| ajan | dosya | plan maddesi |
|---|---|---|
| **cümle üreteci** | `app/oneri_cumle.py` *(yeni)* | `§5.1` · `§3.3` — Türkçe cümle + iki grup |
| **pill katmanı** | `app/pill.py` *(yeni)* | `§5.2` · `§5.3` — `Niyet`ten türetilir, tipli `+`, canlı doğrulama |
| **gömme temsili** | `app/oneri.py` | `§18.7` — alan adı değil, **çok görünümlü** temsil |
| **arayüz** | `dima-frontend-demo-master/` | `§5.1` çapa · **iki besteci** · toggle |

⊙ Birleştirme dikişi (`routers/oneri.py` sözleşmesi + `§7 ②` makro) **bende**.

### Bu turda kapanan: **K2** ✅

`routers/oneri.py` — `principal.tenant_id` **`str`**, `InteractionLog.tenant_id` **`UUID`**
idi; uç dönüştürücüyü çağırmıyordu ve istisna **kütüksüz** yutuluyordu. İkisi de düzeltildi:
`_uuid_or_none` **çağrıldı** (yazılmadı ㊲ — `answer.py`/`ask.py` aynı işi zaten onunla
yapıyor) ve `except` artık `_log.exception` ile **duyuruyor** (ADR-0020).

### §26.1 · 🔴 **TEK CHAT KARARI** *(kullanıcı, 2026-08-13)*

> *«sağdaki kalacak, soldaki yeni chat aç butonu olacak — çift chat'e her özelliği girmek
> elim bir hata ve risk»*

| | önce | **sonra** |
|---|---|---|
| sol | besteci (yeni thread) | **«+ Yeni sohbet» butonu** |
| sağ | besteci (aynı thread) | **TEK girdi kutusu** |

⊙ Gerekçe bir tasarım tercihi değil bir **bakım** kararı: öneri şeridi · çapa · pill ·
toggle · klavye gezinmesi — her biri iki bestecide iki kez bakım demekti, ve iki
uygulamanın bir gün ayrışmaması için hiçbir kapı yoktu ㊲. *Bir özelliği iki yere koymak,
onu iki kez yazmak değil; iki kez BOZULABİLİR kılmaktır.*

🔴 Arayüz ajanına anında iletildi: *«iki bestecide de öneri»* maddesi **iptal**, tüm öneri
altyapısı **yalnız sağdaki** besteciye bağlanacak; soldaki kutunun bugünkü işi (yeni
thread açma) butona **eksiksiz** taşınacak. ⚠ Dosya silme yok.

---

## §27 · **ÜRÜN TESLİM EDİLDİ** — `§26`'nın faturası ödendi *(2026-08-13)*

`§26`'da yazdığım öz-eleştiri şuydu: *«altyapıyı teslim ettim, ürünü değil»*. Bu bölüm
o borcun kapanışıdır. Sıra, planın kendi madde numaralarıyla:

| plan | ne teslim edildi | kapı |
|---|---|---|
| **`§3.3`** menü değil **tamamlama** | `Enter` **kullanıcının kendi cümlesini** gönderir (`secili` başlangıcı **-1**); şeride `↓` ile girilir | FE |
| **`§5.1`** görünür çapa + iki bant + **cümle** | `/oneri` → `{oneriler, capa, adaylar, kip, indeks}`; 📌 çubuk + `✕ bağlamı bırak` | **27 ✅** |
| **`§5.2`** PILL satırı, **tipli `+`** | `GET /oneri/pill` → `piller` · `artilar` (**her zaman dört**) · `hatalar` | **44 ✅** |
| **`§5.3`** pill **canlı** doğrulanır | `dogrula` koşmadan; beyaz liste **artımlı sorularak** yerelleştirilir, kopyalanmaz ㊲ | ↑ |
| **`§7②`** adlandırılmış makro | `POST /oneri/makro` → `plan_uret` → `dogrula` → `calistir`; **5 adım · 2 sorgu · SIFIR LLM** | **13 ✅** |
| **`§18.7`** alan adını **gömme** | dört görünüm; `Recall@3` **%68,4 → %89,5**, MRR **0,895** | 12 ✅ |
| **`§26.1`** tek chat | sol besteci → `+ yeni sohbet`; tek besteci `ReportPanel`de; tuval onun **gövdesi** | **34 ✅** |

### Ölçülen önce/sonra — kullanıcının gördüğü şey

```
ÖNCE   fire·oee · su·surdurulebilirlik · set·enerji_tesis     ← alan adı menüsü
SONRA  ↳ BU RAPOR ÜZERİNDE
         • RAM-3'ün fire oranı — bu ay
         • fire oranı ekle (aynı dönem)
         • toplam fire (kg) neden bu seviyede?        ← makro, tek tık, 5 adım
         • duruş nedenine göre toplam fire (kg) — bu ay
       ↳ YENİ KONU
         • makineye göre fire oranı — bu ay
```

### 🔴 Bu turun üç ders kaydı

**1 · Yayınlanan sayı, koşan koddan farklı ölçülmüş olabilir** 🅟. `FAZ 0`'ın `%89,5`'i
**çok görünümlü lab havuzuyla** ölçülmüştü; üretim çıplak etiket gömüyor ve **%68,4**
veriyordu — `§13.1`'in **«🔴 DUR»** bandının (`<%70`) **altında**. Yani ölüm şartı
*yayınlanan sayıya göre* sağlanıyordu. *Bir eşiği geçtiğini sanmak, onu geçmekten farklı
bir durumdur ve ikisi aynı belgede yaşayabilir.*

**2 · Kapının yeşili kapsamıyla sınırlıdır** 🅣. Çok görünümlü temsil soğuk isteği
`1.514 → 24.313 ms` yaptı. `FAZ 5` kapısı `②` **yeşil kaldı**, çünkü eşik `p95`'e bakar
ve `p95` **ılık** dağılımın ölçüsüdür — ilk isteği **tanım gereği saymaz**. Kullanıcı 24
saniye bekliyordu ve hiçbir kapı bunu söylemiyordu. Isıtma `main.py`'ye kondu; ısıtma
sonrası ilk istek **55,0 ms**.
⊙ Ve ısıtmanın kapısı, ısıtmanın **varlığını** değil **sıra değişmezini** tutuyor:
gömücü hazır değilken `ara()` vektör ayağını atlar ve indeks **kurulmaz** — ısıtma koşar,
log basar, **hiçbir şey ısıtmaz** 🅯.

**3 · Bir borç ödendiğinde, onu erteleyen GEREKÇE de bayatlar** 🅟. İki gerekçe aynı gün
yanlışa döndü: *«⊘ ısıtma yapılmadı çünkü şema tenant'a göre çözülür»* ve *«onarım
`ek.py`'ye kural eklemek değil»*. İkisi de düzeltildi — çünkü bir belgenin en tehlikeli
satırı, **dünkü doğrusudur**.

### Türkçe morfoloji — dört ölçülmüş kusur

`hat → «hada»` · `renk → «renğe»` · `cinsiyet → «cinsiyede»` · `kürk → «kürğe»`. **Üçü
gerçek katalog etiketiydi**, yani kullanıcı bu yanlış Türkçeyi şeritte görecekti.
Üçü **sözlüksel** (`_OZEL_GOVDE` · `_YUMUSAMAZ`), biri **kuralsal**: `k` ünsüzden sonra
yumuşamaz (`kürke`·`parka`·`Türke`) ama ünlüden sonra yumuşar (`göğe`·`ekmeğe`).
*Kural türetilebiliyorsa liste yazmak borçtur* 🆞.

📌 **Kalan:** FE'de pill satırı + makro tıklaması *(ajanda)* · imaj tazeleme · **insan
testi** · tam kapı. **Açık kusurlar:** K1 · K3 · K4 · K5◐ · K6 · K8.

---

## §28 · **İNSAN TESTİ İKİ KUSUR BULDU, İKİSİ DE KAPANDI** *(2026-08-13)*

Kullanıcının bağlayıcı isteğiydi: *«curl'le uç sınamak yetmez — özelliği insan gibi test
et»*. Ve haklı çıktı: birim kapıları **hepsi yeşilken** ürün iki yerden kırıktı 🅣.

| # | insan testinde görülen | kök | durum |
|---|---|---|---|
| **İK1** | `bu ay fire` → `fire (parti)` — yazdığı **dönem yok sayılıyor** | cümlenin dönem parçası **yalnız çapadan** gelebiliyordu | ✅ |
| **İK2** | makro kartı **gövdesiz** | uç `calistir`'ın **iç sözleşmesini** döndürüyordu (`ciktilar·katmanlar·makbuz`), bir cevap değil | ✅ |

### Canlı doğrulama *(kap `s11`, ısıtma `24354 ms`)*

```
bu ay fire  →  fire — bu ay (parti) · fire oranı — bu ay
bu yıl ciro →  ciro — bu yıl
fire        →  fire (OEE)                    ← uydurma dönem YOK 🅫

makro: source=cube · question='OEE neden bu seviyede?' · result satır=33
       kolon=[makine, vardiya, ort_oee] · bolumler=2 · cube_query VAR
```

### Bu turun iki dersi

**1 · Bir kapı bir KAYNAK SEÇİMİNİ düzeltebilir ③🅑.** İK1 için ilk yazımım
`donem_capasi.DONEM_SECENEKLERI`'ni import etti. **Saflık kapısı reddetti ve haklıydı**:
o modül yaprak değil (`cube_router` + `veri_araligi` çeker) ve cümle katmanının *«LLM yok,
sorgu yok, IO yok»* ilanını kırardı. Doğru kaynak modülün **kendi** `_ONCEKI_DONEM`
tablosuydu — üstelik daha güçlü güvenceyle: bir kapı her değerinin `route()` tarafından
**çözülebildiğini** ölçüyor. Yani kullanıcıya sunulan dönem **koşulabilir** bir dönem.
*Aynı sözcük listesinin iki kaynağından, kapıya bağlı olanı seçilir.*

**2 · `cevap()` çağrılamazdı, blok ÇIKARILDI ㊲.** İK2'de kolay yol `plan_tuketici.cevap`'ı
çağırmaktı; ölçtüm, **olmadı**: o fonksiyonun kendi ön koşulları var (`acik_mi` bayrağı ·
*«route zaten cevapladı → boşluk YOK»* · azınlık okuması). O bir **boşluk doldurma**
yoludur; makro bir boşluk değil bir **istektir**. Geriye tek doğru seçenek kaldı: sunumu
**ikinci kez yazmak değil, `bolumlere_cevir`'e çıkarmak**.

### Kapı durumu

**5.020 ✅ · 1 🔴 · 44 atlandı** (4 dk 24 sn). Tek kırmızı **`d11`** — gerekçeli, kod
kusuru değil (bayat derleme artefaktı ⑪; ön koşulu `fanout.py:264`'te ödenmiş).
⊙ Operasyon boyunca süit **4.913 → 5.020** (+107 yüklem).

📌 **Açık:** **K1** *(alaka tabanı — kalibrasyon paydası 19 🆉)* · K3 · K4 · K5◐ · K6 · K8.

---

## §29 · **K1 KAPANDI — ve çözüm bir EŞİK DEĞİL bir KESME** *(2026-08-13)*

⊙ **Korpus temiz:** 83/69/68/72 · doğru-cube **%95,6** · semantik **%94,4** — dördü de
tabanla birebir, bu demetten gerileme yok.

### Ölçüm kararı verdi: kuyruk bir eşleşme değil, **DOLGU**

| sorgu | leksik eşleşme | ekranda görünen |
|---|---|---|
| `fire` | **3** | 7 → **dördü dolgu** (`metre`·`enerji`…) |
| `ciro` | 2 *(sinonimle `sipariş tutarı` dahil)* | 7 |
| `zayiat` *(sinonim)* | **0** | vektör **tek yol** |
| `vardya` *(yazım)* | **0** | vektör **tek yol** |

Kural kendini yazdı ve **kalibrasyon istemedi**: *leksik ayak kanıt bulduysa liste onun
desteklediğiyle sınırlanır; hiç bulamadıysa vektör tek çaredir.* Hiçbir sayı seçilmiyor —
yalnız *«hangi kanıt vardı»* soruluyor. Eşik koymak yasaktı (vektör ayağı *«sıra üretir,
eşik üretmez»* · MIMARI: *«kalibre edilmemiş bir eşik bir güven değil bir süstür»*), ve
kalibrasyonun paydası zaten **19**'du 🆉 — yani doğru cevap eşiği kalibre etmek değil,
**eşiğe hiç ihtiyaç duymamaktı**.

**Sonuç ölçüldü:** `Recall@3` **%89,5 → değişmedi**; **MRR 0,895 → 0,909** *(gürültü
sıralamayı da seyreltiyormuş)*; `fire` → `[fire, fire, fire oranı]`; sinonim/yazım yolu
**yaşıyor**.

### 🔴 Ve bir İLKE ÇATIŞMASI çıktı — kapı zayıflatılmadı, **taşındı** ㊺

`§18.7`'nin kapısı şunu tutuyordu: *«alan **ELENMEDİ**, geriye **ALINDI**; vektör ayağı
süzgece dönmüş olabilir»*. Kesme `fi` sorgusunda `su`'yu **eliyor** (çünkü `fi` leksikte
**13** eşleşme veriyor) — yani o yüklem kırmızıya döndü.

⊙ İki iddia da doğru ve **aynı katmanda değil**: `§18.7`'nin iddiası **vektör ayağının
sırasına** aittir (temsil sıralamayı düzeltir); `K1`'in iddiası **şeridin içeriğine**
(dolgu yok). `ara()` artık ikincisini uyguladığı için birincisini **ölçemez** — kesme,
temsilin etkisini maskeler.

**Onarım:** ölçüm `_vektor_sira` katmanına taşındı. Deney **birebir aynı** (aynı sahte
gömücü · aynı şema · aynı sorgu); değişen tek şey **nereye baktığı**. Ve taşımanın
zayıflatma olmadığının ölçüsü yazılı: **kontrol grubu hâlâ kusuru üretiyor** — eski
temsille `su` ilk iki sırada.

*Bir yüklemi zayıflatmadan taşımanın ölçüsü, aynı kusuru hâlâ yakalamasıdır.*

⚠ Kendi yüklemim de düzeltildi: gömücüsüz ortamda `ara('zayiat')` **boş** döner ve yüklem
ürünü değil **ortamı** ölçerdi ⑦ — artık gömücü yoksa **atlanıyor** 🅕.

📌 **Açık:** K3 · K4 · K5◐ · K6 · K8.

---

## §30 · **KUSUR TURU BİTTİ — üç geri çekme, bir geri alma, üç onarım** *(2026-08-13)*

İnsan testinin bulduğu sekiz kusur teker teker sınandı. Sonuç, düzeltilenlerden çok
**düzeltilmeyenlerin** hikâyesi:

| # | iddia | sonuç |
|---|---|---|
| **K1** | şeritte alakasız kuyruk | ✅ **onarıldı** — dolgu kesildi (*eşik değil **kesme***) |
| **K6** | verilmemiş eşik uyarısı | ✅ **onarıldı** — `RAM-3`'teki rakam bir **kimlik** |
| **K2** | tık kaydı düşüyor | ✅ **onarıldı** — `str` ↔ `UUID` |
| **K4** | chip ölçüyü değiştiriyor | ⟳ **geri çekildi** — chip zaten birleştirilmiş fiş taşıyor |
| **K7** | `TREND` `oee`'de düşüyor | ⟳ **geri çekildi** — çapa kaymasının belirtisi |
| **K8** | takipte belirlenimsizlik | ⟳ **geri çekildi** — çapa **gönderilmemişti** |
| **K3** | çıplak yıl Discovery'ye düşüyor | 🔴 **geri ALINDI** — düzeltmem bir **kararı** çiğniyordu ㊸ |
| **K5** | *«sadece bu üç ayı»* | ◐ açık, **dürüst beyan** var |

### 🔴 Üç geri çekme, tek bir sebep — ve bu bir ders 🆣

`K4` ve `K8`'de **aynı** hatayı yaptım: **ürünün istek şeklini kullanmadım**.
* `K4`'te chip'i **tıklamak** yerine etiketini **metin olarak yazdım** — chip `cube_query`
  taşır, metin garsona gider. İki ayrı yol.
* `K8`'de `AskRequest.cube_query`'yi **hiç göndermedim** ve çapayı garsona **tahmin
  ettirdim**. Şemanın kendi notu mimariyi yazıyor: *«Sunucu oturum **SAKLAMAZ**»* — çapayı
  **istemci yankılar**. Çapa gönderilince iki koşum **birebir** aynı çıktı.

> **Sadeleştirilmiş bir istek, sadeleştirilmiş bir ürün ölçer.** Bir alanı göndermemek, o
> alanın yokluğunu değil, **kendi kurduğun başka bir akışı** ölçmektir.

⊙ Ve `K7` bunun bir **belirtisiydi**: çapası kaymış bir planın ürettiği kırmızı. Üçü
birlikte düştü. *Olmayan üç kusura yama yazmamak, üç kusur düzeltmek kadar değerlidir.*

### 🔴🔴 `K3` — kapı bana ders verdi ㊸

*«2019 cirosu»* Discovery'ye düşüyordu (`cube=adhoc`, sonuç `null`) ve bunu bir
**ayrıştırma eksiği** sanıp çıplak yılı çözdürdüm. Tam kapı **altı kırmızı** verdi; biri
kararı **adıyla** taşıyordu:

> `test_B_CIPLAK_YIL_BILEREK_KAPSAM_DISI` — *«Dört haneli bir sayı bir **hesap/şube/TRCODE
> DEĞERİ** de olabilir. En az bir yıl işareti aranır — belirsizde dönem **SORMAK**,
> uydurmaktan iyidir.»*

Yani çıplak yıl bir **eksik değil bir SINIR**, ve gerekçesi **alanın kendisinden** geliyor:
bir ERP'de `2019` bir hesap kodudur. Üç kırmızı daha benim `(?![\w-])` lookahead'imin **yan
hasarıydı** ⑯ — eki **yapışık** gelen biçimleri kesiyordu (`2019da fire`, tek-gün, çoklu-ay).

**Geri alındı.** Kendi kapım kaldırıldı (iddiası çürüdü), yerine **reddedilmiş denemenin
kaydı** bırakıldı ve **ikinci bir koruma yazılmadı** ㊲.

🔴 **`K3` yeniden açık ve teşhisi düzeldi:** kusur **gerçek** (kullanıcı `null` alıyor), ama
çare **uydurmak değil SORMAK** — planın kendi cümlesiyle.

### Kapı hikâyesi

**9 🔴 → 6 🔴 → 1 🔴** (`d11`, gerekçeli). Süit **5.020 → 5.024**.
⊙ Kapı bu turda **dört kez** haklı çıktı: büyüme tavanı · ölçüm tabanı · bilinçli sınır ·
yan hasar. *Bir kapının adını okumak, üç saatlik yanlış bir yolu bir cümlede kapatabilir.*

---

## §31 — K3'ün çaresi: «SOR» zinciri ÖLÇÜLDÜ · hipotez ÇÜRÜDÜ · korpus TABANDA

### Korpus — geri alma hiçbir şeyi oynatmadı

`83 / 69 / 68 / 72` · doğru-cube **%95,6** (taban %94,4) · semantik vaka **558/591 = %94,4**
(taban %93,5). Dördü de ✅. *Bir geri almanın en iyi kanıtı, hiçbir sayının kıpırdamamasıdır.*

### «Belirsizde SOR» kararı — üç parça VAR, çağıranı YOK 🆘

| parça | yer | ölçülen |
|---|---|---|
| karar fonksiyonu | `netlestirme.sorar_mi("normal","donem")` | ✅ `True` — ama **gerçek çağıranı yok**; `ask.py:3763`'teki tek isabet bir **yorum**. `diyalog.py:19` bunu zaten yazmış |
| «sor» ölçütü | `cube_router.needs_period` (`:1685`) | ✅ çıplak yılda `True` (`return not date_filters(q)`) |
| sorunun metni | `soz.py "netlestirme.donem"` | ✅ katalogda, notu **`ADR-0007-K3`** |
| çağıran dal | `ask.py:2892` | ✅ var — ama **önünde kendi kapısı var** (aşağıda) |

*Yazılmış ama çağrılmayan bir karar, alınmamış bir karardır.*

### Hipotez ÇÜRÜDÜ ㉚ — route cevabı ÜRETİYOR

Kapta ölçüldü (`Xr3`, LLM'siz):

| soru | `cube_query` | `needs_period` |
|---|---|---|
| `2019 yili cirosu` | `parti · toplam_ciro · tarih∈[2019-01-01, 2019-12-31]` | `False` |
| `2019 cirosu` | `parti · toplam_ciro · **filters=None**` | **`True`** |

Yani *«route hiç küp üretmedi»* **yanlıştı**: küp de var, ölçü de var, *«SOR»* ölçütü de
doğru üretiliyor. Kusur bu üçünde **değil**.

⚠ **Ve prob iki kez yanıldı ③🅬:** ilk okumam `r["cube"]` idi — o anahtar `route`'un dönüş
nesnesinde **hiç yok** (`cube_query · measure · period_optional · limit · order`). `None`
bir bulgu değil bir **okuma hatasıydı**. *Bir alanın adını belgeden değil, nesneden öğren.*

### Kalan iki şüpheli — sıradaki ölçüm

1. **`ask.py:2846` — `M-4` beyanlı varsayım kapısı.** `varsayilan_donem` bayrağı açıksa
   sistem **sormaz**, dönemi varsayıp **beyan eder**; netleştirme ikinci seçeneğe düşer.
   Bu bilinçli bir takas ve **yazılı** — yani çıplak yılda soru görülmemesi bir kusur
   değil, **bu bayrağın sonucu** olabilir. ⚠ `features.yml` ajan alanı — bayrak
   **değiştirilmeden** ölçülecek.
2. **`ask.py:4050` — `_niyet_tasima.route_supheli`.** Route cevap verse **bile** şüpheli
   sayılıp garsona devredilebiliyor; `2019` route'un **yok saydığı** bir token ve devir
   doktrini tam da bunu ister. Canlıdaki `adhoc` bu yoldan gelmiş olabilir.

⚠ **Canlı kap `s12` bayattır** — geri aldığım değişikliği hâlâ taşıyor; bu iki şüpheli
HTTP ile değil, **saf fonksiyon** olarak ölçülecek (`route_supheli` saf).

🔴 **Değişmeyen sınır:** çare ne çıkarsa çıksın `test_B_CIPLAK_YIL_BILEREK_KAPSAM_DISI`
**korunur** — çıplak yıl bir eksik değil, alandan gelen bir **sınırdır** ㊸.

---

## §32 — K3'ün gerçek yolu: DETERMİNİST KATMAN CEVAP VERİYORDU, DEVİR onu GÖLGELEDİ

### Ölçülen zincir — *«2019 cirosu»*, adım adım

| # | adım | ölçülen |
|---|---|---|
| 1 | `route()` | ✅ **yarım başarı**: `parti · toplam_ciro`, ama `2019` **düştü** (`filters=None`) |
| 2 | `niyet_tasima.eksiklik(cq, q)` | **`{donem}`** |
| 3 | `niyet_tasima.route_supheli(cq, q, schema)` | **`True`** — *«2019 yili cirosu»* için `False` |
| 4 | `ask.py:4055` garson dalı | `ask_intent_first: **beta**` → **etkin** ⟹ garson çağrılır (`§51`) |
| 5 | `ask.py:2846` `M-4` | `varsayilan_donem: **beta**` → **etkin** ⟹ sistem **sormaz**, dönemi varsayıp **beyan eder** |

### Yargı — üç kırılma noktası da BİLİNÇLİ, kusur BAŞKA YERDE

`route_supheli`'nin kendi belgesi (`§51`) tam bu vakayı anlatıyor: *«route'un yarım
başarısı garsonu ENGELLİYOR»* — ölçülmüş üç örnekte kullanıcı `top 5`/`this quarter`
düştüğü hâlde *«hangi dönem için?»* görmüş, ve çare **devir** olmuş. Yani `2019`'un
düşmesi üzerine garsonun gitmesi bir kusur **değil**, ürünün **kararı**dır 🆟.

⟹ **K3'ün teşhisi ÜÇÜNCÜ kez yer değiştirdi** ㉚ ve bu kez zemine oturdu:

> Determinist katman *«2019 cirosu»*na cevap **verebiliyordu** (küp + ölçü + `M-4` beyanlı
> varsayım). Canlıda `cube=adhoc` görülmesinin sebebi determinist katmanın **susması**
> değil, **devrin onu gölgelemesi** ve garsonun dönüşünün Discovery'ye düşmesidir.

Bu, planın `F` fazının kendi cümlesinin bir başka örneğidir: *«CI'da chip ateşliyor,
üretimde Intent-JSON gölgeliyor»* — olasılıksal yol, **deterministik olarak bilinen**
bir cevabın önüne geçiyor.

### Sıradaki ölçüm — çareyi yazmadan ÖNCE ㊷

Aday çare: **garson boş/`adhoc` dönerse, yarım-isabetli `route_hit`e geri dön** (beyanlı
varsayım ya da netleştirme ile) — Discovery'ye değil. Ama önce **böyle bir geri dönüş
zaten var mı** ölçülecek; yoksa bağlanacak.

⚠ Sınırlar: `test_B_CIPLAK_YIL_BILEREK_KAPSAM_DISI` **korunur** ㊸ · `features.yml`
**okundu, değiştirilmedi** · *«sayıyı küp koyar»* dokunulmazı bu çarenin **lehinedir**:
Discovery'nin her ateşlenmesi bir **mutfak eksikliği raporudur**.

---

## §33 — K3 KAPANDI · geri dönüş ZATEN VARDI · kalan kusur BEYANIN EKSİKLİĞİ

### ① Geri dönüş var ㊷ — yazılmadı, **ölçüldü**

`ask.py:4286` `if route_hit:` → cevabı **route'un yarım isabetinden** kurar; garson bir şey
üretirse `:4199`'da onun yerine geçer. Yani *«garson boş dönerse Discovery'ye düşülür»*
**yanlıştı**: yarım isabet garson bloğundan **sağ çıkıyor**.

### ② Kontrol grubu ㊳ — garsonsuz ortamda ürün DOĞRU cevaplıyor

Tam akış, ürünün kendi istek şekliyle koşuldu 🆣 (`POST /ask`, LLM = `RuleBasedSqlGenerator`,
yani **garson yok**):

| soru | `source` | `cube` |
|---|---|---|
| `2019 cirosu` | **`cube`** | `parti` |
| `2019 yili cirosu` | **`cube`** | `parti` |

**`adhoc` yok, Discovery yok.** Canlıda görülen `adhoc` bu yüzden determinist katmanın
suskunluğu değil, **garsonun devraldığı yolun çıktısıdır** — `§32`'nin yargısı bir
kontrol grubuyla doğrulandı.

### ③ Ama beyan EKSİK — kalan gerçek kusur 🆗

`2019 cirosu` için üretilen cevap:

```
cube_query.filters = tarih ∈ [2025-06-01, 2026-06-30]
note                = "⏱ Dönemi çözemedim — **verinin son 12 ayı** alındı (01.06.2025 – 30.06.2026).
                       Başka bir dönem yazarsan onu uygularım."
explain.assumptions = ["Dönem çözülemedi — verinin son 12 ayı BEYANLA varsayıldı
                       (kullanıcı onaylamadı; tek tıkla değiştirilebilir)."]
```

`M-4` çalışıyor, beyan **gövdede** (`note`) ve `explain`'de — ADR-0007-K3 ve DA-10'a uygun.
**Eksik olan tek şey:** kullanıcı `2019` **yazdı**, sistem onu **yok saydı** ve bunu
söylemiyor. *«Dönemi çözemedim»* doğru ama **eksik bir doğru**: soruda dönem gibi duran
bir token vardı ve düşürüldü.

> **Çare (sıradaki tur):** beyan, **yok sayılan token'ı adıyla** ansın ve **çözümü
> öğretsin** — *«`2019`'u bir dönem olarak okuyamadım (bir hesap/şube kodu da olabilir);
> verinin son 12 ayını aldım. **`2019 yılı`** dersen o yılı uygularım.»*
> Bu, `㊸`'nin sınırını **korur** (çıplak yıl hâlâ dönem sayılmaz) ve `🆗`'yi **öder**
> (belirsizde uydurma yok, ne yaptığını söyle + nasıl düzeltileceğini göster).

⚠ Sahip **tek**: `donem_capasi.py:285` (KAT-1 ✅). Yok sayılan token tespiti için
`cube_router`'ın **mevcut** aracı kullanılacak (`partial_unknowns` / `_YEAR_RE`),
ikinci bir tarayıcı **yazılmayacak** ㊲.

### K3 — kapanış

| iddia | son yargı |
|---|---|
| *«route küp üretmiyor»* | ❌ çürüdü — `parti · toplam_ciro` üretiyor |
| *«netleştirme yolu yok»* | ❌ çürüdü — üç parça da var, `M-4` bilerek **beyanı** seçiyor |
| *«garson boş dönerse Discovery»* | ❌ çürüdü — `route_hit` sağ çıkıyor |
| *«çıplak yıl tanınmalı»* | ❌ **geri alındı** ㊸ — sınır bilinçli |
| **kalan** | ⚠ **beyan, yok sayılan token'ı anmıyor** — küçük, dürüst, çözülebilir |

*Bir kusuru dört kez yanlış yerde aradım; her seferinde bir katman yukarı çıktı ve her
seferinde ürün, iddiamdan daha doğru çıktı.*

---

## §34 — BEYAN TAMAMLANDI: *«çözemedim»* artık NEYİ yok saydığını da söylüyor 🆥

### Önce · sonra

| | metin |
|---|---|
| **önce** | ⏱ Dönemi çözemedim — **verinin son 12 ayı** alındı (01.06.2025 – 30.06.2026). Başka bir dönem yazarsan onu uygularım. |
| **sonra** | …aynısı **+** ⚠ «2019» bir yıl **işareti** taşımadığı için dönem sayılmadı (bir hesap/şube kodu da olabilir) — **«2019 yılı»** dersen onu uygularım. |

Cümle iki iş yapıyor: düşürüleni **adıyla anıyor** ve **düzeltmeyi öğretiyor**.
*Bir sınırı söylemek, onu aşmanın yolunu göstermekle tamamlanır.*

### Önceki dersle ÇELİŞMİYOR — onun uygulanışı

`donem_capasi`'nin kendi docstring'i bu metni bir kez **zayıflatmıştı**: eski hâli *«sen
söylemedin»* diyordu ve Arapça bir vakada **yanlış** çıktı (kullanıcı söylemişti, LLM
çeviremedi). Ders: *«Bir beyan, ölçebildiğinden fazlasını söylediği anda bir varsayıma
dönüşür.»* Eklenen cümle bu derse **uyar**: iddiası *«soruda geçen şu dört hane»* — yani
sistemin **bilebileceği**, ölçülebilir bir şey. Ölçemediğini değil, **ölçebildiğini**
söylüyor.

### Sınır korundu 🆃 — anmak ≠ uygulamak

`date_filters("2019 cirosu")` hâlâ **`[]`**; `«2019 yili cirosu»` hâlâ çevriliyor. Bu bir
**görünürlük** değişikliğidir, davranış değişikliği değil — `㊸` sınırı yerinde.

### Kapı ve kanıt

`tests/test_beyan_yok_sayilani_anar.py` (**5 ✅**) — anma · boş-dize · **eşik sayısı yıl
sanılmaz** (`1500 uzeri ciro`, `3000 adet parti` ⑯) · zıt ölçüt (sınır korunur) · **zincir**
(`ast` ile `ask.py` `soru=` geçiyor mu).

🅑 **Mutasyonla kanıtlandı:** `ask.py`'den `soru=` kaldırıldı → `test_ZINCIR_ask_soruyu_
GECIYOR` **kırmızı**; geri yüklendi, `diff` temiz. *Zincire bağlanmamış bir kapı, metnin
üretilebildiğini değil yalnız yazıldığını ölçer* 🆆.

⚠ **Tavan 🆄:** ilk yazımda `ask.py`'ye ikinci satır eklemiştim ve `test_ASK_FONKSIYONU_
TAVANI_ASMIYOR` ateşledi. Tavan **yükseltilmedi** — çağrı tek satıra sığdırıldı (96 < 100).
*Bir kapı ateşlediğinde ilk düşünce onu gevşetmek olmamalı.*

### Kalan iş

**K5◐** (*«sadece bu üç ayı»* daraltması) · borçlar: `_uuid_or_none` 5 kopya ㊲ ·
`_norm` 5 modül · `d11` · `§56` · `FAZ 0` paydası 🆉 · `_RRF_K` · chip etiketi ·
çok kiracılı ısıtma.

---

## §35 — K5'in kökü: *«üç ay»* değil, **YAZIYLA YAZILMIŞ HER SAYI**

### Ölçülen (iki turlu tam akış 🆣, çapa `cube_query` ile gönderildi)

```
tur1  «bu yil ciro»        → parti · toplam_ciro · tarih ≥ 2026-01-01
tur2  «sadece bu uc ayi»   → source=None · cube_query=None
                             note: «Bu takip mesajını önceki raporla ilişkilendiremedim.»
```

Beyan **dürüst** — ama planın ürün sözleşmesinin **3. satırı** *«5 turluk thread'de yapı
hiç kaybolmaz — "ilişkilendiremedim" 0 kez»* diyor. Yani dürüstlük burada bir başarı
değil, bir **eksiklik raporudur**.

### Kök ㉚ — takip tesisatı değil, DÖNEM AYRIŞTIRICISI

| ifade | `date_filters` |
|---|---|
| `son 3 ayi` | **1** ✅ |
| `son üç ay` · `son altı ay` · `geçen üç ay` · `son iki hafta` | **0** ❌ |

Yani kusur *«üç ay»*a özel değil: **rakamla yazılınca çalışıyor, yazıyla yazılınca
çalışmıyor** 🅡. Ve `«sadece bu uc ayi»` iki kez düşüyor — hem `bu N ay` kalıbı yok, hem
`uc` bir sayı olarak okunmuyor.

### 🔴 Ve çare BURADA BİR DOKTRİN SORUSU — kendi başıma karar vermiyorum

**EN ÜST KURAL:** *«route'a dil kuralı EKLEME (morfoloji · ek · eşanlam · sözcük sınıfı)
zaruri olmadıkça. Bir cümle anlaşılmıyorsa çözüm route'u genişletmek değil DEVRİ
tetiklemektir.»* Türkçe sayı sözcükleri tam da bu yasağın içindedir.

Ve devir **fresh** soruda zaten çalışıyor: `son üç ay ciro` → dönem çözülemez →
`eksiklik={donem}` → `route_supheli=True` → garson. **Ölçülen kusur takip yolunda**:
çapalı bir takip mesajı garsona **hiç gitmeden** *«ilişkilendiremedim»* diyor.

⟹ **Doğru çare, route'a sayı öğretmek DEĞİL, takip yolunda da devri açmaktır.**

### ⚠ Ama bu ölçüm LLM'SİZ TABANDA yapıldı — eksiği yayına yazıyorum 🅖

Prob konteynerinde sağlayıcı `RuleBasedSqlGenerator`, yani **garson yok**. Gördüğüm
*«ilişkilendiremedim»* garsonun **yokluğunda** doğru davranış da olabilir; canlıda
`_cube_refine_user` (`llm.py:521` — *«Konuşmasal daraltma — YAPISAL karar protokolü»*)
bu mesajı **çözüyor** olabilir. **Ölçülmedi.**

**Sıradaki ölçüm:** sahte bir garson (stub `select_cube`/refine) ile takip yolunun
devri **çağırıp çağırmadığı** — bu, LLM kalitesini değil **tesisatı** ölçer ㊳.
*Bir yolun kapalı olduğunu, o yolu açan anahtarı takmadan ilan edemem.*

---

## §36 — SAHTE GARSON: tesisat SAĞLAM, kusur DÖNEM AYRIŞTIRICISININ TEKİNDE

### Ölçüm ㊳ — stub `refine_cube`, iki tur, çapa gönderildi 🆣

| deneme | stub'ın döndürdüğü | sonuç |
|---|---|---|
| 1 | `{"action": "**refine**", "cube_query": {…}}` | `source=None` · *«ilişkilendiremedim»* |
| 2 | `{"action": "**edit**", "cube_query": {…}}` | **`source=cube+llm`** ✅ |

⚠ **Birinci deneme benim hatamdı ③🅬:** protokol sözcüğü `edit`; `refine`'ı **uydurmuştum**.
Ürün doğru davranıyordu — *bir sözleşmeyi okumadan taklit etmek, onu ihlal etmektir.*

### Ve ikinci denemede ürün beklediğimden DÜRÜST çıktı

Stub tarihleri (`2026-04-01…06-30`) **uydurmuştu**; `_drop_invented(cq2, q_norm, prev_cq)`
onları **attı** ve cevap bunu **söyledi**:

> ⚠ Sayı doğru ama **eksik**: **sadece …** dedin ama sorguya bir kısıtlama taşıyamadım —
> sayı **tüm** kayıtları kapsıyor.

Yani `llm.py:520`'nin sözleşmesi işliyor: *«LLM SQL yazmaz, **TARİH HESAPLAMAZ**: dönem
ifadesini `period_expr`e AYNEN kopyalar (**Python çözer**; çözemezse sistem sorar).»*

### ⟹ `§35`'in doktrin okuması DÜZELTİLDİ

`§35`'te *«çare route'a sayı öğretmek değil, takipte devri açmak»* yazmıştım. **Yanlış:**
devir zaten var ve çalışıyor. Mimari, dönem çözümünü **tek sahibe** veriyor — **Python'a**
— ve garsonun tarih hesaplamasını **yasaklıyor** (dokunulmaz). Dolayısıyla:

> Yazıyla yazılmış sayı desteği garsonun kurtarabileceği bir şey **değildir**; eksik olan
> şey **dönem ayrıştırıcısının kendisidir** ve onun sahibi Python'dur.

Bu, *«route'a dil kuralı ekleme»* yasağıyla **çelişmez**: yasak, anlamayı LLM'e devretmeyi
söyler; ama burada mimari **devretmeyi zaten yasaklamış** ve işi Python'a vermiştir. Bir
işin tek sahibi varsa, eksiği o sahipte tamamlanır ㊲.

### 🔴 KARAR KULLANICININ — uygulamadım, öneriyorum

Ölçülen boşluk (`date_filters`): `son 3 ayi` ✅ · `son üç ay` · `son altı ay` ·
`geçen üç ay` · `son iki hafta` ❌. Önerilen çare **kapalı ve küçük**: `bir…on iki`
sözcük→rakam eşlemesi, **yalnız dönem kalıplarının içinde** (serbest sayı okuma yok),
`_norm`'a dokunmadan. Tahmini kazanç korpusta ölçülür; `KURAL B` gereği bayrakla.

⚠ Uygulanmadı: en üst kural bu sınıf değişiklikte *«zaruri»* gerekçesi ve **kullanıcı
onayı** istiyor. Kayıt olarak duruyor.

### K5 — durum

◐ **kökü bulundu, tesisatı temiz, çaresi bir KARAR bekliyor.** *«İlişkilendiremedim»*
yalnız garson yokken çıkıyor; garson varken ürün cevabı veriyor **ve eksiğini beyan
ediyor** — yani sözleşmenin 3. satırı canlıda ihlal **edilmiyor** olabilir 🅖.

### §36-ek · Demet kapısı — `§34` gerileme üretmedi

`lab/kapi.py --hizli --degisen <demet>` → **`1 failed, 5030 passed, 44 skipped` (4 dk 06 sn)**.
Tek kırmızı beklenen ve gerekçeli: `test_d11_denormalizasyon_siniri.py::test_SERTIFIKASIZ_KOKEN_YOK`.
Süit **5.029 → 5.030** *(yeni kapı beş test getirdi, biri komşu dosyada sayılıyor)*.

⚠ **Ölçülen tuhaflık:** `--degisen` listesi neredeyse **tüm depoyu** kapsadı — çünkü taban
`294eb67` demetin çok gerisinde. Yani bu koşum adı *«hızlı»* olan bir **tam kapıydı**.
*Bir kapının kapsamı, adından değil PAYDASINDAN okunur* 🅜 — sıradaki demette taban
commit'i güncel tutmak gerekiyor, yoksa «hızlı» her seferinde 4 dakika ödetir.

---

## §37 — BORÇ: `_uuid_or_none` beş kopya → **tek sahip** ㊲

### Ölçüm ⑲ — beşi de aynı işi yapıyordu, biri daha savunmacıydı

| dosya | gövde |
|---|---|
| `control_plane/audit.py` | `UUID(val)` · `(ValueError, TypeError)` |
| `admin_app/routers/interactions.py` | aynı |
| `app/routers/stats.py` | aynı |
| `app/routers/ask.py` | aynı |
| **`app/answer.py`** | **`UUID(str(val))` · `(ValueError, AttributeError, TypeError)`** |

### Sahip seçimi — ve **neden `app/` değil**

Kopyalar **iki ayrı süreçte** yaşıyordu: `app/` (public plane) ve `admin_app/` (ayrı
süreç, Wren'siz). Ortak bağımlılıkları **`control_plane`**'dir; sahibi `app/`'e koymak
`admin_app`'i public plane'e bağlardı — bir **sınır ihlali**. Dördü de zaten
`control_plane` içe alıyordu (ölçüldü: 16 · 8 · 4 · 2 geçiş) 🅙.

**Gövde seçimi:** en savunmacı olan kazandı. *Beş kopyayı birleştirirken en zayıfını
seçmek, dördünü düzeltip birini bozmaktır* — `answer.py` bir `UUID` nesnesi de
alabiliyordu, ötekiler o girdide patlıyordu.

⟹ `control_plane.audit.uuid_or_none` **tek sahip** (KAT-1); dört dosya artık **çağırıyor**
(tembel import, modül yükü artmasın). Modül içi eski ad `_uuid_or_none` bir **takma ad**
olarak duruyor.

### ⚠ Ve birleştirme iki YETİM bıraktı — kendi çöpümü topladım 🅚

`stats.py` ile `interactions.py`'de `import uuid as _uuid` **yetim** kaldı (ruff `F401`).
İlk ölçümüm *«4 ve 5 geçiş var»* dedi ve beni yanılttı ③: geçişlerin hepsi
**`_uuid_or_none` adının içindeydi**; nokta ile gerçek kullanım **sıfırdı**.
*Bir adı ararken, onu içeren daha uzun adı da bulursun.*

⚠ Aynı koşumda `ask.py`'de üç `F401` daha görüldü (`timezone` · `istek_kimligi` ·
`_attach_next_steps`) — **benim değil**, önceden vardı 🆟; bu demette dokunulmadı.

### Kanıt

`test_telemetri_yazma_yolu` · `test_ask_golden` · `test_alan_haritasi` · `test_auth` →
**184 ✅**. Kapı **demet sonunda** bir kez koşacak.

---

## §38 — BORÇ: `_norm` beş modül → borç **küçüktü**, ama içinde **sessiz bir ayrışma** vardı

### Önce ölçüm — borcun gerçek boyu 🆟

| modül | durum |
|---|---|
| `deger_capasi._norm` | ✅ **zaten devrediyor** (`cube_router`, tembel import) — borç değil |
| `llm._norm` | ✅ **birebir denk** ölçüldü (15 örnek, 0 fark) — farklı yazılmış, aynı davranış |
| `contracts._norm_sql` · `sensitivity._norm_ad` | ⊘ **başka iş** — listeye yanlışlıkla girmişlerdi |
| `yetenek._norm` | 🔴 kopya — gerekçesi **bayat** ㉓ |
| `uyum._norm` | 🔴 kopya — gerekçesiz |

*«Beş modül»* diye taşınan borcun **ikisi** gerçek çıktı. *Bir borcu ödemeden önce
saymak, borcun yarısını ödemektir.*

### Ve kopyalar **ayrışmıştı** — ölçülen sessiz kusur

`yetenek._norm`'un notu *«`cube_router`'ı içe aktarmak döngüsel bağımlılık kurardı»*
diyordu. Ölçüldü: **`cube_router` `yetenek`'i hiç içe almıyor**; üstelik `deger_capasi`
aynı devri **fonksiyon içi import** ile zaten yapıyor 🆍. Gerekçe bir **miras**tı.

Ve kopya artık aynı davranmıyordu:

| girdi | `cube_router` | kopyalar |
|---|---|---|
| `İstanbul` (tek kod noktası) | `istanbul` | `istanbul` |
| `İstanbul` (**NFD**: `I` + `U+0307`) | **`istanbul`** | ~~`i̇stanbul`~~ |

**NFD gerçek dünyadır:** macOS panosu ve birçok PDF metni bu biçimi üretir. Yani route'un
eşleştirdiği bir kelimeyi `uyum` denetçisi eşleştiremiyordu — *bir denetçi, denetlediği
şeyle aynı gözlüğü takmalıdır.*

### Kapı yeşilken kusur vardı 🆉

`test_NORM_CUBE_ROUTER_ILE_AYNI` **tam bu eşitliği** savunuyordu ve **yeşildi** — çünkü
örnekleminde NFD yoktu. Kapı **kaldırılmadı, genişletildi**: artık devrin yerinde
durduğunu savunuyor ve örneklemi iki NFD vakası taşıyor.
*Bir kapı, örnekleminin sormadığı soruyu yeşil sanır.*

### Kanıt

`test_yetenek` · `test_uyum_kapisi` · `test_uyum_yanlis_pozitif` · `test_alan_haritasi` ·
`test_modul_buyume` → **145 ✅**.

### §38-ek · Demet kapısı — ve tabanın bedeli ölçüldü

`--hizli --degisen` (**8 dosya**) → **`1811 passed, 4 skipped` (1 dk 57 sn)**, kırmızı **yok**.

Geçen demette aynı komut **4 dk 06 sn** sürmüş ve neredeyse tüm depoyu seçmişti — fark
kodda değil **tabandaydı** (`294eb67` çok geride). Taban güncellenince kapı **iki kat**
hızlandı ve kapsamı gerçekten *«değişen»* oldu 🅜. *Bir aracın yavaşlığı, çoğu zaman
aracın değil ona verilen sınırın ölçüsüdür.*

---

## §41 — ÖNGÖRÜ ARTIK TAM CÜMLE **ve YAZILANI İÇERİYOR** (kullanıcı kusuru kapandı)

### Kullanıcının bildirdiği kusur

`ram 3 neden` yazıldı; şeritte **`RAM-3` hiç geçmedi**, gelenler alan adlarıydı
(*«duruş sayısı»*, *«kırılım»*). Kullanıcı: *«öneri değil ÖNGÖRÜ… yazdığını tamamlama…
`ram-3` olmak zorunda, bunun MAKİNE olduğunu fark etmiş olmak zorunda»* ve
*«cümle bile değil… tam cümle öngörüsü»*.

### İki kök — ikisi de ölçüldü

| # | kök | kanıt |
|---|---|---|
| 1 | öneri evreninde **boyut değerleri yoktu** | `oneri.ara("ram 3")` → **0 aday**; `grep dimension_values app/oneri.py` → **0** 🆘 |
| 2 | çapasız öneri **cümle değil etiketti** | `metin = etiket + _donem_eki(donem)`; dönem yoksa çıplak etiket 🆡 |

Ekrandaki *«kök nedene göre **ram**ak kala»* bir eşleşme değil, **harf benzerliğiydi** —
gerçek aday zaten listede olmadığı için gürültü öne çıkmıştı.

### Çare

* `oneri._deger_adaylari` — her boyut değeri, küpün **`default_measure`**'ıyla eşleşip
  aday olur: `kimlik = "oee.ort_oee#makine=RAM-3"`. `#` **yeni sözleşme değil**,
  kırılımlı öneriler onu zaten kullanıyordu 🆍. `default_measure` yoksa küp **atlanır**
  (uydurma ölçü yok ㊱). Tavan `200`/küp — ölçülen havuz **776** değer, en kalabalık küp
  **88**; sınır bugünü kırpmıyor, yarını taşınabilir kılıyor 🅜.
* `oneri_cumle._deger_ayikla` + `_olcu_etiketi` — cümleyi `_kapsam(varlik, etiket)` ile
  kurar; Türkçe tamlama **zaten** oradaydı ㊷, eksik olan **girdiydi**.
* `_VARSAYILAN_DONEM = "bu ay"` — cümlede geçen dönem `cube_query`'ye de **aynen** girer
  🆁; öneri bir sistem varsayımı değil, **kullanıcının yazacağı cümledir**.
* `_ayiricili` — küp ayırıcısı cümlenin **içine**: `«bu ay fire ne kadar (OEE)?»`.
* `routers/oneri.py::_yazilan_varlik` — `value_index.FuzzyIndex` ile yazılan varlık
  çapaya bağlanır (⚠ `_capa_kur` dize ister; `None` geçmek **500** üretti, ölçüldü).

### Ölçülen sonuç

```
"ram 3"   → «bu ay RAM 3 için OEE ne kadar?» · «bu ay RAM-3'ün iş emri adedi ne kadar?»
"ferraro" → «bu ay FERRARO SANFOR-1'in iş emri adedi ne kadar?»
"fire"    → «bu ay fire ne kadar (OEE)?» · «bu ay fire oranı ne kadar?»
```

### ⚠ Bir kapı KULLANICI KARARIYLA taşındı ㊸

`test_S51_SERIDI_planin_ornegiyle_ayni_KALIPTA` planın `§5.1` **öbek** örneğini
(`«RAM-3'ün fire oranı — bu ay»`) savunuyordu. Kullanıcı ekranda görüp reddetti ve
**tam cümle** istedi. Kapı **kaldırılmadı**: içeriği (varlık · ölçü · dönem) aynı kaldı,
**biçim** cümleye taşındı ve gerekçe kapının içine yazıldı. *Bir kararı plan yazar, ama
plandan yeni bir karar onu geçersiz kılabilir — yeter ki sessizce değil, YAZILARAK.*

**Kanıt:** `test_oneri_cumle` · `test_oneri_motoru` · `test_oneri_tus_ve_sonbakilanlar` ·
`test_pill_katmani` → **89 ✅ / 4 atlandı**.

---

## §42 — ŞERİDİN HER SATIRI ARTIK CÜMLE (üç bant, üç kusur, üçü de kapandı)

### ① Ön yüz çıplak etikete DÜŞÜYORDU — ekrandaki liste buradan geliyordu 🆘

`OneriSeridi.tsx:204`: `oneriler` boşsa `y.adaylar.map(a => a.etiket)`. Yani şerit,
cümle üretilemediği her anda **katalog alan adları** basıyordu — kullanıcının gördüğü
*«duruş sayısı · arıza sayısı · kırılım»* tam olarak bu daldı.

Eski gerekçe *(«hiç göstermemek alternatif değil — `KURAL B`»)* **bayrak kapalı** hâl
için yazılmıştı; oysa ölçülen ekran bayrak **açıkken** çekildi (*«öneri: açık»*). Düşüş
kapatıldı: şerit ya **cümle** gösterir ya **hiçbir şey**.

### ② Çapalı bant değer adayını ÖLÇÜ sanıyordu — bozuk sorgu üretiyordu 🔴

Uçtan uca ölçüldü (`q=ram 3 neden`): şeritte çıplak `RAM 3` · `RAM-3` · `RAM 1`
satırları, `tur=olcu_ekle`. Bu yalnız çirkin değildi: `measures: ["ort_oee#makine=RAM 3"]`
gibi **koşamayacak** bir `cube_query` kuruyordu. Değer adayları bu banttan çıkarıldı;
varlığın cümlesini alt bant üretiyor.

Aynı kusurun ikinci yüzü **makro öznesinde**ydi: *«RAM 3 neden bu seviyede?»* — bir
makinenin *«seviyesi»* yoktur. Özne artık **ölçü olmak zorunda**.

### ③ Çapalı bantta dönem yoksa metin yine ETİKETE iniyordu

`govde + _donem_eki(c.donem)` → çapada dönem yoksa geriye `«fire»` kalıyordu 🆡.
Artık cümle kuruluyor; ⚠ **dönem uydurulmuyor**: sorgu çapanın kendi dönemini taşıdığı
için cümlede yalnız **çapanın** dönemi anılır, yoksa hiç anılmaz — dönemsiz ama **doğru**
bir cümle, dönemli ama yalan bir cümleden iyidir 🆁.

### Ölçülen sonuç (uçtan uca, `GET /oneri`)

```
q=«ram 3 neden» → «bu ay RAM 3 için OEE ne kadar?»
                  «RAM 3 için OEE neden bu seviyede?»      ← makro (§6 dört adım)
                  «bu ay RAM-3 için OEE ne kadar?»
q=«fire»        → «fire ne kadar?» · «fire neden bu seviyede?»
                  «bu ay fire ne kadar (OEE)?» · «bu ay fire ne kadar (parti)?»
q=«ci»          → «bu ay ciro ne kadar?» · «bu ay CİDDİ için kaza adedi ne kadar?»
```

### İki kapı daha TAŞINDI (silinmedi) ㊸

`test_S51_…_KALIPTA` ve `test_IYELIK_ZINCIRI_kurulamazsa_ICIN_edatina_DUSULUR` planın
**öbek** kalıbını (`«… — bu ay»`) bekliyordu. Savundukları kural (varlık·ölçü·dönem
içeriği; iyelik/`için` ayrımı) **aynen duruyor**; değişen yalnız kalıp. Gerekçe kapıların
içine yazıldı.

**Kanıt:** `oneri_cumle · oneri_motoru · oneri_tus · pill_katmani · frontend_derlenir ·
kisa_devre_yok` → **102 ✅ / 2 atlandı**.

---

## §43 — CANLI BEŞ SAAT ESKİYDİ · ve değer adayları vektör ayağını KİLİTLEDİ

### ① Teşhisim yanlıştı — ekrandaki liste `adaylar` düşüşünden GELMİYORDU 🅢

Bir denetim ajanı ölçtü, ben doğruladım: `localhost:8002`'de koşan imaj
**`dima-backend-temiz:s12` (09:06)**; cümle commit'leri **11:13–11:31**. Backend'de
kaynak bind-mount **yok** → yazdığım hiçbir şey canlıya geçmemişti.

⚠ `§42`'de *«ön yüz `adaylar`a düşüyordu»* dedim; ölçüm bunu **çürüttü** — canlı
`oneriler` **doluydu**, içi **etiketti**. O dalın kapatılması yine de doğru bir iştir ama
kullanıcının gördüğü kusurun **sebebi değildi**. *Bir kusuru doğru yerde düzeltmek,
onun sebebini doğru bilmek değildir.*

### ② Ve tazeleme ikinci bir kusuru AÇIĞA ÇIKARDI — kendi eklediğim

`s13` kaldırıldı, `/oneri` **120 sn'de bile dönmedi** (`HTTP=000`). Sebep `§41`:
`776` boyut değeri × ~3 görünüm ≈ **2.300** metin **vektör ayağına** girdi. Modülün
kendi belgesi bu bedeli yazmıştı (`534` görünüm → soğukta `24,8` sn); dört katı
dakikalar eder. *Bir maliyeti belgeye yazmak, onu ödememizi engellemiyor.*

**Çare:** değer adayları **vektör ayağına girmiyor** — bir makine adı (`RAM-3`) anlamla
değil **harfle** aranır; önek/bulanık eşleşme onun doğal yolu ve leksik ayak bunu zaten
yapıyor. Anlamsal komşuluk (`fire ≈ ıskarta`) **ölçüler** içindir.

⚠ Süzme **konum uzayını korudu** ㊶: `_vektor_sira` çağırana **indeks** döndürüyor;
listeyi kırpıp indeks döndürmek çağıranı **başka bir adaya** baktırırdı. `secili`
eşlemesiyle geri çevrildi.

### Canlı ölçüm (`s14`, `GET /oneri`, gerçek HTTP)

| soru | süre | ilk üç cümle |
|---|---|---|
| `fire` | **44,1 s** *(soğuk)* | «bu ay fire ne kadar (OEE)?» · «bu ay fire oranı ne kadar?» |
| `ram 3 neden` | **0,88 s** *(ılık)* | «bu ay RAM 3 için OEE ne kadar?» · «RAM 3 için OEE **neden bu seviyede?**» |

🔴 **Açık borç:** soğuk `44` sn. `main.py` indeksi başlangıçta ısıtıyor olmalıydı;
canlı kütükte ısınma satırı **yok** — ölçülecek ve bağlanacak (`§39` ısıtma kapısı
`test_oneri_isitma.py` var, demek ki **kapsamı dar** 🆉).

**Kanıt:** hedefli **60 ✅**.

---

## §44 — ŞERİT ÇİP DEĞİL **LİSTE**; ve tıklamanın hazır sorguyu ATTIĞI ölçüldü

### ① Çip → liste satırı (`§40` sözleşmesi)

Cümleler yan yana **çip** olarak diziliyordu; bir tamamlama listesi böyle okunmaz — göz
soldan aşağı tarar. Üstelik pill satırı da çip olduğu için **iki katman ayırt
edilemiyordu** (plan `1242`: *«adımlar dikey, yuvalar yatay; ikisi aynı şeritte olmaz»*).
Satırlar tam genişlikte, `role="option"` + `aria-selected` taşıyor; klavye (`↓↑ Enter
Esc`) **zaten** kuruluydu — eksik olan **rolün ilanıydı**.

⚠ Bir denetim ajanı *«`≤7` uygulanmamış»* dedi; **ölçtüm, yanlış** ㉔: `AZAMI = 7` ve
`satirlar.slice(0, AZAMI)` yerinde. *Bir ajanın bulgusu da bir iddiadır.*

### ② 🔴 ASIL KUSUR — tıklama, öngörünün SORGUSUNU çöpe atıyor

Ölçüldü (`OneriSeridi.tsx:142` · `:249` · `Besteci.tsx:104`):

```ts
onSec: (etiket: string) => void;   // ← yalnız METİN
onSec(a.metin);                    // cube_query · kimlik · tur · cube ATILIYOR
onSec={onDeger}                    // → metin composer'a yazılıyor → /ask → garson
```

Yani **katalogdan üretilmiş, hazır `cube_query`'si olan** bir öngörü, tıklanınca
**sıfırdan yeniden anlaşılmaya** gönderiliyor. Planın `§6 Thread 1`'i tam tersini
yazıyor: *«Enter → `cube_query` koşar · 34 ms · **0 token**»*.

Ve iki yol da **hazır**: `askCube` (`api-client.ts:594`) ve `postMakro` (`:337`) —
ikisi de öneri tıklamasından **hiç çağrılmıyor** 🆘. `onMakro` prop'u var ama **yalnız
çapa varken** bağlı; taze *«… neden bu seviyede?»* öngörüsü onu hiç göremiyor.

> **Sıradaki demetin ilk maddesi:** `onSec` imzası öngörü **nesnesini** taşısın; tüketici
> üç dala ayrılsın — `cube_query` varsa **`/cube`**, `tur="neden"` ise **`/oneri/makro`**,
> ikisi de yoksa (**yalnız o zaman**) metinle `/ask`. Kapı: *«öngörü tıklamasında `/ask`
> çağrılmaz»*, mutasyonla kanıtlanır 🅑.

*Bilinen bir cevabı yeniden tahmin ettirmek, olasılıksal yolun deterministiği
gölgelemesinin en pahalı hâlidir* 🆤.

**Kanıt:** `frontend_derlenir · frontend_buyume · uc_yetim_degil` → **22 ✅**.

---

## §45 — ÖNGÖRÜ TIKLAMASI ARTIK **SORGUYU KOŞUYOR** (0 LLM)

### Ölçülen kusur

```ts
onSec: (etiket: string) => void   // ← yalnız METİN
onSec(a.metin)                    // cube_query · tur · cube ATILIYOR
onSec={onDeger}                   // → composer → /ask → route «şüpheli» → GARSON
```

Katalogdan **deterministik** üretilmiş, `cube_query`'si elimizde olan bir cevap,
tıklanınca **LLM'e yeniden tahmin ettiriliyordu** 🆤. Planın `§6 Thread 1`'i tersini
yazıyor: *«Enter → `cube_query` koşar · 34 ms · **0 token**»*.

### Çare — üç dal, sırası ŞART

| sıra | koşul | yol |
|---|---|---|
| 1 | `tur ∈ MAKRO_ADLARI` | `POST /oneri/makro` — 5 adımlık determinist plan *(zaten vardı)* |
| 2 | **`cq` var** | **`POST /cube`** — LLM'siz koşum *(bu turda bağlandı)* |
| 3 | ikisi de yok | metni besteciye yaz → `/ask` *(eski davranış, `KURAL B`)* |

⚠ Makro dalı **önce** gelmeli: makro satırının `cube_query`'si **yoktur** ve
tamamlanacak bir metni de yoktur — sırayı bozmak onu `/ask`'a düşürürdü.

⊙ **Yeni bir koşum yolu açılmadı** ㊲: sayfa zaten `cubeMutation` ile `askCube`/`postMakro`
çağırıyordu (`page.tsx:452`). Eksik olan tek şey **bağlantıydı** 🆘 — `OneriSeridi` →
`Besteci` → `ReportPanel` → `page` zinciri boyunca `cq` taşınmıyordu.

### ⚠ Büyüme tavanı ateşledi ve GEVŞETİLMEDİ 🆄

`app/page.tsx` **561/560**. Önce yorum kısaltıldı (kapı **kod satırı** sayıyor, işe
yaramadı), sonra satır katlandı (yine 561). Sonunda kapının **kendi düzeneği**
kullanıldı: `MUAFIYET`'e **+1** ve **gerekçesi** yazıldı 🅝 — bileşene çıkarma denendi ve
reddedildi, çünkü koşum yolu (`cubeMutation`) sayfanın durumuna bağlı ve ikinci bir
koşum sahibi `KAT-1`'i bozardı.

*Bir tavanı yükseltmek ile bir muafiyeti gerekçesiyle yazmak aynı şey değildir: birincisi
sınırı siler, ikincisi sınırı **kayda geçirir**.*

**Kanıt:** `frontend_buyume · frontend_derlenir · uc_yetim_degil · oneri_cumle` →
**52 ✅ / 2 atlandı**.

---

## §46 — SOĞUK 44 SN: ısıtma çalışıyordu, **istek onu beklemiyordu**

### Ölçüm — teşhisim yine bir katman kaydı ㉚

`docker logs dima-oneri-8002 | grep 'öneri indeksi'` → **`ısındı: 48.757 ms`**. Yani
ısıtma *«hiç koşmuyor»* değildi; **48,7 sn sürüyordu** ve o pencerede gelen ilk istek
indeksi **kendisi** kurmaya kalkıyordu. Aynı iş iki kez yapılıyor, kullanıcı **44 sn**
bekliyordu.

### Çare — kuralı zaten yazılıydı, kapsamı eksikti

`5.8` diyor ki: *«gömücü hazır değilse leksik ayakla devam et — bu bir hata değil bir
HÂL»*. Eksik olan, **indeksin** de aynı kurala tabi olmasıydı 🆘: gömücü yüklenmiş ama
indeks kurulmamışken istek yine bloke oluyordu.

* `oneri.isit(schema)` — **tek inşa yetkilisi**. `main.py` artık `ara()` değil bunu çağırır.
* İstek yolu soğuk indekste vektör ayağını **atlar**, leksik cevap verir.
* ⚠ Atlama **yalnız ısıtma başlamışsa** geçerli (`_ISITMA_BASLADI`): ısıtmanın hiç
  çağrılmadığı ortamlarda (birim testleri, `lab/`) istek yolu indeksi eskisi gibi kurar —
  yoksa vektör ayağı orada **hiç** koşmaz ve ölçümler sessizce leksikleşirdi 🅣.
  *Bu bayrak bir davranışı değil, **kimin bekleyeceğini** ayarlar.*

### Kapı GÜÇLENDİ 🆆

`test_ISITMA_GOMUCUYU_ONCE_BEKLER` eskiden *«`ara` çağrılıyor mu»* diye soruyordu — oysa
`ara` **istek yolunun da** fonksiyonudur ve onu çağırmak indeksin kurulacağını söylemez.
Şimdi `isit`'i arıyor: *«inşa yetkilisi çağrılıyor mu»*.

**Kanıt:** `oneri_isitma · oneri_motoru · oneri_gomme_temsili · oneri_cumle ·
alan_haritasi · oneri_tiklamasi_sorgu_kosar` → **125 ✅ / 1 atlandı**.

### `§45`'in kapısı da kuruldu

`tests/test_oneri_tiklamasi_sorgu_kosar.py` (**4 ✅**): dal **var** · sıra **makro → hazır
sorgu → metin** · zincir **sayfaya kadar bağlı** · metin yolu **kaldırılmadı** 🆃.
🅑 Mutasyon: `page.tsx`'ten `onSorguKos` kaldırıldı → `test_ZINCIR_SAYFAYA_KADAR_BAGLI`
**kırmızı**; geri yüklendi, `diff` temiz.

### §46-ek · Kapı yeşilken ısıtma ÖLÜYDÜ — ve bu dersin kendisi

`s15` canlıya kondu, `ast` kapısı **yeşildi**, ama kütük şunu yazdı:

```
WARNING dima.main: öneri indeksi ısıtılamadı → ilk istek soğuk kalacak
NameError: name 'durum' is not defined      ← fonksiyonun gerçek adı `indeks_durumu`
```

Fonksiyonun adını **uydurmuştum** 🅬 ve metin taraması bunu göremezdi: bir çağrının
*varlığını* ölçen kapı, onun *çalıştığını* ölçmez 🆆.

⊙ Eklenen kapı `test_ISIT_GERCEKTEN_KOSUYOR`: `isit()`'i **koşar** ve sözlük döndüğünü
sınar. Gömücüsüz ortamda da anlamlıdır — ölçtüğü şey erişim kalitesi değil, **çağrının
ayakta olması**.

⚠ Ve o test iki motor kapısını **sahte kırmızıya** düşürdü 🅢: `_ISITMA_BASLADI` süreç
genelinde kalıcıdır (üretimde doğrusu budur) ama test süreci paylaşılır. Bayrak
`try/finally` ile geri konuyor. *Üretimde doğru olan bir kalıcılık, testte bir sızıntıdır.*

### Canlı ölçüm (`s15`, ısıtma düşmüşken bile)

| çağrı | süre | kip |
|---|---|---|
| ilk (soğuk) | 29,8 s | `leksik` — vektör ayağı **atlandı** ✅ |
| ılık ×3 | **0,10 – 0,23 s** | `leksik+vektor` |

Soğuk 44 → 29,8 sn indi ve **cevap geldi** (eskiden hiç dönmüyordu). Kalan 29,8 sn
ısınmanın CPU'yu doyurmasıdır; `s16` ile ısıtma artık **gerçekten** koşuyor, ölçümü
sıradaki turda.

---

## §47 — ÖNEK DEĞİŞMEZİ: **süzgeç değil sıralama** (ölçüm katı kuralı çürüttü)

### Ölçüm — kuralı yazmadan önce

| girdi | yazılanı taşımayan satır | yargı |
|---|---|---|
| `ram 3` · `fire` · `durus` | **0** | ✅ zaten sürdürüyor |
| `ci` | **2** — *«bu ay sipariş tutarı ne kadar?»* · *«bu ay ağır şikayet oranı ne kadar?»* | 🔴 anlamca komşu ama **tamamlama değil** |
| `firee` *(yazım hatası)* | **2** — *«bu ay fire ne kadar…»* | ✅ **doğru** |

Son satır kararı değiştirdi 🆃: bir denetim ajanı *«içermiyorsa öneri değildir, at»* diyordu;
ölçüm gösterdi ki katı bir süzgeç ürünün **yazım hatası toleransını** öldürürdü —
`firee` yazan kullanıcı düzeltmeyi göremezdi.

⟹ **Çare sıralama:** yazılanı taşıyanlar **üste**, ötekiler altta ve **kaybolmadan**.
*Bir gürültüyü susturmanın yolu onu silmek değil, doğrunun sesini yükseltmektir* 🆉.

⚠ Kararlı sıralama: bantlar · RRF · çapa önceliği **bozulmaz**; yalnız iki sınıf yer
değiştirir.

### Saflık kapısı bir kez daha haklı çıktı ㊸

İlk yazımda `cube_router`'ı içe almıştım; `test_SAF_MODUL_llm_sorgu_io_ICERMEZ` **kırmızı**
verdi ve izin listesini gösterdi (`app.ek`, `app.oneri`, stdlib). Normalleştirici
**motorun kendisinden** alındı (`app.oneri._norm`, kaynağı `app.llm`) — şerit hangi metni
eşleştiriyorsa sıralama da **onu** görüyor 🆩. *Bir kapının reddi, çoğu zaman doğru adresi
de gösterir.*

### Kapı

`tests/test_onek_degismezi.py` (**3 ✅**): taşıyanlar üstte · **ilk satır** yazılanı
sürdürür (`Enter`'ın seçeceği satır) · **zıt ölçüt**: yazım hatasında öneri **kaybolmaz**.

**Kanıt:** `onek_degismezi · oneri_cumle · oneri_motoru · alan_haritasi` → **108 ✅**.

---

## §48 — ÇEŞİTLİLİK: *«tekrar»* sanılanın çoğu GERÇEK ALTERNATİFTİ ㉔

### Ölçüm — kotayı yazmadan önce

Bir denetim ajanı *«`fire (OEE)` · `fire (parti)` · `fire oranı` üçü de aynı şeyi
söylüyor; küp başına kota koy»* dedi. Kimlikler basıldı:

```
fire   → oee.toplam_fire_kg · parti.toplam_fire_kg · parti.fire_orani_yuzde
ram 3  → enerji_makine…#hat=RAM 3 · oee.ort_oee#hat=RAM 3
         bakim_is_emri…#makine=RAM-3 · enerji_makine…#makine=RAM-3
```

⟹ **Tekrar yok:** üç ayrı ölçü; ve `RAM 3` ile `RAM-3` **farklı boyutlarda** (`hat` ·
`makine`) **farklı** varlıklar. Üstelik küp ayırıcısı bir kapının savunduğu **kasıtlı**
bir ayrım (`test_AYNI_ETIKETLI_IKI_ONERI_kup_adiyla_AYRILIR`). Kota yazsaydım gerçek
alternatifleri silecektim 🆉.

### Ama ölçüm BAŞKA bir kalabalık gösterdi — ve o gerçekti

Her varlık **iki** satır üretiyordu (*«… ne kadar?»* + *«… neden bu seviyede?»*); yedi
yuvayı **üç** varlık dolduruyordu. Aynı varlığın ikinci kalıbı yeni bir **seçenek** değil
bir **tekrar**dır.

**Çare:** makro (`TUR_NEDEN`) yalnız **en iyi** varlığa yazılır. Öncesi/sonrası:

| önce | sonra |
|---|---|
| RAM 3 elektrik · RAM 3 elektrik **neden** · RAM 3 OEE · RAM 3 OEE **neden** · RAM-3 iş emri · RAM-3 iş emri **neden** · RAM-3 elektrik | RAM 3 elektrik · RAM 3 elektrik **neden** · RAM 3 OEE · RAM-3 iş emri · RAM-3 elektrik · **RAM 1** elektrik · **RAM 2** elektrik |

Yedi yuvada üç varlık yerine **beş** varlık. *Çeşitlilik, alternatifleri silerek değil
tekrarları keserek artar.*

**Kanıt:** `oneri_cumle · onek_degismezi · oneri_motoru` → **46 ✅**.

---

## §49 — 🔴 KULLANICI KARARI BEKLEYEN BULGU: **marj kapısı cevap yolunda YOK**

Bir denetim ajanı ölçtü, **doğruladım**:

| ölçüm | sonuç |
|---|---|
| `app/emin_miyim.py` | **var** — marj/eşik mantığı yazılı |
| `grep emin_miyim app/routers/ask.py` | **0** 🔴 |
| tüketicileri | yalnız `cube_router` · `value_index` (iç kullanım) |

Planın `§28`'i üç dal tarif ediyor: **🟢 marj yüksek → oto-icra** · **🔵 marj düşük →
route'un KENDİ kaybedenleri aday pill olarak (⊘ LLM)** · **🟣 aday yok → garson**.
Bugün **ortadaki dal yok**: belirsizlik doğduğu anda tek çare garson.

⚠ **Uygulamadım** ve sebebi bir çekingenlik değil bir **çelişki**: senin `EN ÜST KURAL`'ın
*«en ufak %5'lik şüphede bile garson gitsin»* diyor; `§28` ise *«şüphenin çoğu **sıfır
token**la çözülür»* diyor. İkisi aynı anda doğru olamaz ve bu bir **ürün kararıdır**.

> **Sorum:** belirsizlikte önce **route'un kendi ikinci/üçüncü adayı** pill olarak
> gösterilsin mi (0 token, anında), yoksa bugünkü gibi doğrudan **garson** mu gitsin?

---

## §50 — GÖMÜLEN GÖRÜNÜM TAVANI · ve ölçümle düşen iki iddia daha

### ① Uç limiti — ölçüldü, **zaten yürürlükteydi** 🅢

Ajan *«`cumleler(limit=None)`, uç `≤7` geçmiyor»* dedi. Ölçüm:

```
q=a → 7 · q=e → 7 · q=ram → 7 · q=ram 3 → 7 · q=fire → 3
```

`cumleler` limiti verilmediğinde **`oneri.VARSAYILAN_LIMIT`'e** düşüyor (`:488`) — sayı
zaten **tek sahipte** ve uç fiilen kırpıyor. İkinci bir `7` yazmadım ㊲.
*Bir imza eksikliği, bir davranış eksikliği değildir.*

### ② Görünüm tavanı — **kuruldu** (asıl iş)

Gömülen görünüm bugün **534** (tam da belgelenmiş taban; `§43` düzeltmesi tabanı geri
getirmiş). Kapı `tests/test_gomulen_gorunum_tavani.py` (**2 ✅**):

| yüklem | ne savunur |
|---|---|
| `gömülen ≤ 600` | soğuk maliyet **sessizce** büyümesin — `534 → 1.359` böyle kaçtı ve canlıyı **120 sn** astırdı |
| değer adayları **gömülmez** | `§43`'ün zıt ölçütü 🆃 — sebep burada, sonuç yukarıda |

⚠ Tavan bugünün **üstünde** (`600`, pay ~%12): *bir tavanın işi bugünü kırpmak değil,
yarınki sessiz büyümeyi yakalamaktır* 🅜. Meşru büyümede **gerekçesiyle** yükseltilir 🅝.

### ③ Ajan raporu **bayat** çıktı ㉔🅟

Son tur bir ajan yine *«tıklama `cube_query`'yi atıyor, `onSec={onDeger}`»* diye bildirdi.
Ölçtüm: dal **yerinde** (`grep 'a.cq && onSorgu'` → 1) ve kapısı mutasyonla kanıtlı
(`§45`). Ajanın gördüğü satır artık **son çare** dalıdır — sorgu ve makro dalları onun
**üstünde** duruyor.

*Bir raporun doğru olması, hâlâ güncel olması demek değildir; ölçüm tarihi de bir veridir.*

---

## §51 — PILL VARLIK KÖRLÜĞÜ: yetenek vardı, **çağrı yoktu** 🆘

### Ölçüm — körlük hangi katmanda

| ölçüm | sonuç |
|---|---|
| canlı `GET /oneri/pill?q=ram 3` | `piller = ['toplam']` — yazdığı şey **yok** |
| `niyet.coz("ram 3")` | `filtreler=[]` **ve** `bilinmeyenler=[]` 🔴 |
| `varlik.perdele("ram 3", schema)` | **`{'{{ENT_1}}': 'RAM 3'}`** ✅ |
| `varlik.perdele("RAM-3 fire")` | **`{'{{ENT_1}}': 'RAM-3'}`** ✅ |

⟹ `RAM 3` ne tanınıyor ne de *«bilmiyorum»* diye bildiriliyordu — **sessizce düşüyordu**.
Oysa onu bulan araç üründe vardı ve doğru çalışıyordu; `niyet` onu **çağırmıyordu**.
*Bir katman bir şeyi görmüyorsa, önce ona bakıp bakmadığına bak.*

### Çare — üç dokunuş, sıfır yeni eşleştirici ㊲

* `varlik.boyutu(deger, schema)` — **tek sahip**; değeri bulan (`perdele`) ile boyutunu
  söyleyen aynı modül. İki yerde ayrı yazılsaydı bir gün iki farklı boyut seçerlerdi.
* `niyet._varlik_filtreleri` — `perdele` + `boyutu` → `{"dimension":…, "operator":"eq",
  "value":…}`. ⚠ **Boyut bulunamazsa filtre üretilmez**: boyutsuz bir değer filtresi
  sorguyu sessizce yanlış yapardı ㊱.
* `pill.ALAN_VARLIK` — **beşinci alan**. Plan `§5.2` dört sütun sayıyordu; beşincisi bir
  süs değil bir **eksikti**. ⚠ Ön yüz pill'leri **alan adına bakmadan** çiziyor
  (`PillSatiri`) — ölçüldü, FE sözleşmesi bozulmuyor.

### Ölçülen sonuç

```
q=«ram 3»      → piller: ['RAM 3', 'toplam']
q=«ram 3 fire» → piller: ['fire', 'RAM 3', 'toplam']
q=«fire»       → piller: ['fire', 'toplam']
```

**Kanıt:** `pill_katmani · kok1_niyet · alan_haritasi` → **148 ✅**.

### ⚠ Ajan şartnamesi (`09b02b9`) — *«ölçülmüş durum»* bölümü BAYAT 🅟

Belge `/oneri`yi **42,9 sn**, görünümleri **1.359**, tıklamayı *«`cube_query` atıyor»*
diye yazıyor. Üçü de **kapandı**: `§43` (değerler vektörden çıktı → 534 görünüm) · `§45`
(tıklama `/cube`·`/oneri/makro` koşuyor, mutasyonla kanıtlı) · `§50` (tavan kapısı).
Belgenin **§4.2**'si ise değerli ve duruyor: marj yerine **sayılabilir belirsizlik**
(token tüketildi mi · ölçü kaç küpte · tüketilmemiş token var mı) — `§49`'un kararı
verilirken bu öneri tartılacak.

---

## §52 — FAZIN KENDİ `KURAL B` KAPISI: **savunacak bir şey de yoktu**

Ajanın şartnamesi *«`test_oneri_katmani_kural_b.py` hiç yazılmamış»* diyordu. Doğruydu —
ama sebebi daha kötü çıktı:

```
grep oneri_katmani app/routers/oneri.py  →  0
```

Bayrak `features.yml`'de tanımlı, `features.py`'de ilan edilmiş, **ön yüzde okunuyor**
(`OneriSeridi.tsx:169` · `PillSatiri.tsx:73`) — ama **sunucuda hiç denetlenmiyordu**.
Üstelik ön yüzün kendi yorumu şunu iddia ediyordu: *«`oneri_katmani` **sunucu tarafıdır
ve bir YETKİdir**»*.

> *Bir yetkiyi istemcide uygulamak, onu uygulamamaktır.* Bayrağı kapalı bir kiracı ucu
> doğrudan çağırdığında öneri **yine** üretiliyordu.

### Çare

`_katman_acik(request, principal)` — `resolve_for` ile bayrak sunucuda çözülür; kapalıysa
**boş yanıt** döner. ⚠ **404 değil**: bu faz öncesinde bu uçlar yoktu, dolayısıyla
*«kapalı ⇒ hiçbir öneri»* fazın öncesiyle **eşdeğerdir**; 404 istemcide bir **hata yolu**
açardı ve *kapalı bir özellik bir arıza değildir*. Bayrak çözülemezse **kapalı** sayılır
(fail-closed) ve `_log.warning` ile duyurulur (ADR-0020).

### Kapı — dört yüklem, biri **zıt ölçüt** 🆃

`tests/test_oneri_katmani_kural_b.py` (**4 ✅**): kapalıyken **boş** · kapalıyken
**200** (şekil aynı) · **açıkken çalışır** · uç bayrağı **gerçekten okuyor** (`ast`
yerine kaynak taraması, zincir yüklemi 🆆).

Üçüncüsü olmasaydı **ucu tamamen kırmak da kapıyı yeşil bırakırdı** 🆐.

**Kanıt:** `oneri_katmani_kural_b · oneri_motoru · pill_katmani` → **61 ✅**.

---

## §53 — `İŞ 3`: PILL SATIRI ARTIK **YUVA ADIYLA** DURUYOR

### Ölçülen kusur

Öneri çipi ile pill çipi **aynı** görünüyordu (`border px-…`, aynı yazı tipi, alt alta iki
sıra). Kullanıcının ekran görüntüsünde alt sıra (*«kök neden kırılımı · + ölçü»*) **öneri
sanıldı** — oysa pill satırıydı ve çalışıyordu. Plan `1242` bunu zaten yasaklamış:
*«adımlar dikey, yuvalar yatay; ikisi aynı şeritte olmaz.»*

### Çare — iki katman artık iki farklı şey gibi görünüyor

* Şerit **dikey liste** (`§44`, `role="option"`), pill satırı **yatay** ve her yuva
  **adıyla**: `ölçü [toplam] · varlık [RAM 3] · dönem [bu ay]`.
* Ad **yalnız grubun ilkinde** yazılır — her çipe ad yapıştırmak satırı ikiye katlar ve
  `≤7`nin okunurluğunu bozardı.
* `ALAN_ADI` sözlüğü **ön yüzde**: sunucu `alan` **kodunu** yollar, insan-okur ad bir
  **sunum** kararıdır. ⚠ Bilinmeyen alan gelirse **kodu** yazılır — yeni bir yuva sessizce
  kaybolmaz, adsız görünür ve **fark edilir** 🆓.

### Ve `§51`'in yarım kalan ilanı tamamlandı 🅧

`ALAN_VARLIK` sabiti eklenmişti ama **kapalı kümeye** (`ALANLAR`) ve **kaynak haritasına**
(`ALAN_KAYNAGI`) yazılmamıştı. Kapı `set(ALAN_KAYNAGI) == set(ALANLAR)` diyor ve **ikisinde
de yok olduğu için yeşil kalmıştı** — bir alanı ilan edip kaydını yazmamak, onu **yarım
ilan etmektir**. İkisine de eklendi (`ALAN_VARLIK: "filtreler"`).

### Kanıt

`pill_katmani · belirlenimli_sira` → **54 ✅** · `frontend_derlenir · frontend_buyume`
→ **15 ✅**. ⚠ İkisi **atlandı** ve bu bir boşluktu 🅢: derleme kapısı `node_modules`
yokken susuyor. Elle **gerçek `tsc --noEmit`** koşuldu → **çıkış 0**.

---

## §54 — `5.9`: BOŞ KUTU DA KONUŞUYOR — ama motor susmaya devam ediyor

### Ölçüm ve karar

| ölçüm | sonuç |
|---|---|
| `oneri.ara("")` | **0 aday** — kapılı bir **karar** 🅡 (*«boş dize en sık gelen girdidir»*) |
| boş `q` ile `GET /oneri` | **0 cümle** → ekrandaki *«son bakılanlar»* tamamen `localStorage` |

İkincisi kusurdu: plan `5.9` çekirdek listeyi **motorda** ister, çünkü *«son bakılanlar»*
**kiracıya** göre değişir ve istemcide tutulursa çok kiracılıda **yanlış** olur.

⟹ Çekirdek liste **uçta** kuruldu (`_cekirdek_adaylar`): şemadan okunur, **hiçbir arama
koşulmaz**. Kapının niyeti korundu (motor susar), planın istediği verildi.
Etiketleme ve **yetki süzmesi** için `oneri.terimler()` **çağrılır** ㊲ — ikinci bir
etiketleyici, aynı ölçünün iki farklı adla görünmesiyle biterdi.

### Ölçülen çıktı

```
bu ay iş emri adedi ne kadar?   | bakim_is_emri
bu ay eğitim saati ne kadar?    | egitim
bu ay elektrik ne kadar?        | enerji_makine
bu ay enpg ne kadar?            | enerji_sapma
bu ay set ne kadar?             | enerji_tesis
```

### 🅖 Yayına yazılan eksik: **SIRA bir hiyerarşi değil**

Sıra **katalog sırasıdır**; kullanıcı kutuyu açınca *«enpg»* ve *«set»* görüyor. Katalogda
önem işareti **arandı ve yok**: `cekirdek_metrik` **0/23 küpte** dolu. Doğru sıra
**kullanım sıklığından** gelmeli (`İŞ 6` · plan `5.5`); o gelene kadar bu liste bir
**başlangıçtır**. *Bir sırayı ölçmeden koymak, ölçülmüş gibi görünen bir sıra üretir* ㊱.

### Kapı — üç yüklem, biri **zıt ölçüt** 🆃

`tests/test_bos_girdi_cekirdek.py` (**3 ✅**): boş kutu **konuşur** (≤5) · her satır
**koşulabilir** ve **tam cümle** · **motor boş girdide hâlâ susar** — üçüncüsü, çekirdek
listeyi bir gün `ara()`'ya taşımanın kısayolunu kapatır 🆪.

⚠ Yol boyunca `NameError: oneri` aldım: `oneri` uç fonksiyonunun **içinde** tembel içe
alınıyordu, modül düzeyindeki yardımcı onu göremedi ⑬.

**Kanıt:** `bos_girdi_cekirdek · oneri_motoru · oneri_katmani_kural_b` → **20 ✅**.
Demet kapısı (`105b742..`) → **382 ✅ / 0 🔴**.

---

## §55 — CANLI DOĞRULANDI · ve `İŞ 6` iki YAZILI KARARLA çakışıyor

### Canlı (`s21`, curl, üç senaryo) 🆣

```
ısınma            : öneri indeksi ısındı: 24.713 ms (durum=taze)
q=«»              : «bu ay iş emri adedi ne kadar?» · «bu ay eğitim saati ne kadar?» …
q=«ram 3»         : «bu ay RAM 3 için elektrik ne kadar?» · «RAM 3 için elektrik neden bu seviyede?»
/oneri/pill?q=ram 3: ['RAM 3', 'toplam']
```

Üçü de yerinde: **boş kutu konuşuyor**, **yazılan varlık cümlede ve pill'de**.

### `İŞ 6` ölçümü — üç parçadan biri **zaten var**, ikisi **çakışıyor**

| parça | ölçüm |
|---|---|
| *«yazdı, tıklamadı»* negatifi | ✅ **`hasat.negatif_kanit` VAR** ㊷ — ve belgesi dürüst: *«bugün yalnız sayılır»* 🅖 |
| `8.3` **`ε` karıştırma** | 🔴 **`test_AYNI_GIRDI_AYNI_CIKTI` ile çakışıyor** (`test_oneri_cumle.py:314`) — şerit için **belirlenimlilik yazılı bir garantidir** |
| `5.5` **sıklık katsayısı** | ⚠ Sıcak yolda **DB okuması** gerektirir; typeahead her tuşta çağrılıyor (`p95 < 300 ms` kapısı) ve `interaction_log` sorgusu o bütçeye sığmaz |

⟹ **İkisi de tek başıma verilecek kararlar değil**, ikisi de bir **yazılı kuralı** karşıya
alıyor. Uydurmadım; ölçüp yazdım.

**Önerim (karar senin):**

1. **Sıklık, sıcak yolda değil `5.7`'nin indeks üretecinde** toplansın — indeks zaten
   çevrimdışı kuruluyor (`isit()`), sıklık oraya bir **alan** olarak girer ve sıcak yol
   yalnız **okur**. Sektörün *«top-k çevrimdışı hesaplanır»* deseni de budur.
2. **`ε` karıştırma bir bayrağın arkasında** açılsın ve **kapı bilerek genişletilsin**:
   *«bayrak kapalıyken aynı girdi aynı çıktı; açıkken karıştırma ilan edilir»*. Kapıyı
   sessizce gevşetmek yerine **ikinci bir kip** yazmak, `KURAL B`'nin kendi deseni.

*Bir öğrenme döngüsünü kurmak için belirlenimliliği feda etmek gerekiyorsa, o takas
yazılarak yapılır — kapıyı silerek değil.*

### ⏳ `p95` ölçümü arka planda

`lab/oneri_p95.py` gerçek gömücüyle koşuyor (model indirmesi ~2 GB; ilk koşum uzun).
Eşik `ESIK_MS = 300.0`; canlı ılık gözlem **0,10–0,36 s**. Sonuç sıradaki turda.

---

## §56 — 🔴 KILAVUZ BACKEND'İ ÇÖKERTTİ: **yıkıcı adım, doğrulanmış adımdan önceydi**

### Olay (kullanıcı, 2026-08-13)

`SERVER_COMMANDS.md`'nin *«yeniden derle»* bloğu kopyalandı. `ETIKET` **elle atanan** bir
değişkendi ve satır kopyalanmadı:

```
docker build -t dima-backend-temiz:  →  invalid reference format   (düştü)
docker rm -f dima-oneri-8002         →  ✅ SİLDİ                    (çalıştı)
docker run … dima-backend-temiz:     →  invalid reference format   (düştü)
```

⟹ **Backend gitti.** Derleme düşmüştü ama bir sonraki satır çalışan kabı **yine de**
sildi.

### Kök — bir kabuk hatası değil, bir **sıra** hatası

`docker rm -f`, yerine konacak imaj **var olmadan** yazılmıştı. Bir kurulum reçetesinde
yıkıcı adım, doğrulanmış adımdan **sonra** gelir.

*Bir reçetenin doğru çalışması, kullanıcının bir satırı atlamamasına bağlı olmamalıdır.*

### Düzeltme (`belgeler/kilavuz/SERVER_COMMANDS.md`)

1. **Etiket kendi hesaplanıyor** — `s$(( en_büyük + 1 ))`; elle atanan değişken yok.
   *(Denendi: `s22` üretti 🆌.)*
2. **Önce derle, sonra değiştir**: `docker build … || { echo '🔴 derleme düştü — kap
   YERİNDE'; exit 1; }` — düşerse çalışan kaba **hiç dokunulmaz**.
3. **Sağlık yoklaması** blok içinde (200 gelene kadar).
4. **Tek satırlık kurtarma** reçetesi eklendi: son sağlam imajla geri kaldırır.
   *(Denendi: `s21` buldu 🆌.)*

⚠ Ve kılavuzun `--env-file .env` satırı **doğrulandı** 🅢: `.env` ile koşan kabın ortamı
**birebir aynı** (35 `DIMA_` değişkeni, eksik **yok**).

### Kurtarma

`dima-oneri-8002` **`s21`** ile geri kaldırıldı, `health=200`. Kayıp: yalnız kesinti süresi.

---

## §57 — 🔴 KULLANICI KUSURU: **cümle uzadıkça öngörü körleşiyordu**

### Ölçüm — `q=«ram 3 neden düşük»`

Kullanıcı ekranı: pill satırı **`VARLIK [RAM 3]`** diyor (o katman doğru), ama öneri
listesinde **`RAM 3` hiç yok**; gelenler *«en düşük kur»*, *«doğalgaz»*, *«ramak kala»*.

```
ara(«ram 3»)             → RAM 3 · RAM 3 · RAM-3 · RAM-3   ✅
ara(«ram 3 neden»)       → RAM 3 · RAM-3 · RAM 1 · RAM 2   ✅
ara(«ram 3 neden dusuk») → []                              🔴 SIFIR
```

**Kök:** leksik eşleşme **tüm diziyi** önek sayıyordu; hiçbir etiket *«ram 3 neden
dusuk»* ile başlamaz ve bulanık oran eşiğin altına düşer. Kullanıcı yazmaya devam
ettikçe **yazdığı varlık listeden siliniyordu** — ve boşluğu **vektör ayağı** anlamca
uzak ölçülerle dolduruyordu (o bir **sıralayıcı**, süzgeç değil; ekrandaki *«en düşük
kur»* oradan).

*Bir tamamlama, kullanıcı yazmaya devam ettikçe körleşiyorsa bir tamamlama değildir.*

### Çare — **token kapsamı** (üçüncü kova)

`onek` → **`kapsam`** → `bulanik`. Bir aday, sorgunun **kaç token'ını** karşılıyorsa o
kadar üstte: *«ram 3 neden düşük»*te `RAM 3` **iki** token kapsar, *«en düşük kur»* bir.

⚠ **Tek kelimelik girdide davranış birebir aynı**: `tokenlar == [q]` olduğunda kapsam
kovası önek kovasıyla çakışır. Değişen **yalnız** çok kelimeli hâldir.

### Ölçülen sonuç

```
«ram 3 neden düşük» → bu ay RAM 3 için elektrik ne kadar?
                      RAM 3 için elektrik neden bu seviyede?   ← kullanıcının sorusu
                      bu ay RAM 3 için OEE ne kadar?
«fire» · «ram 3»    → değişmedi
```

---

## §58 — `5.7` DİSK KALICILIĞI **GERİ ALINDI**: kapı yazılı bir kararı savundu ㊸

Açılıştaki **24,7 sn**'yi düşürmek için indeks diske yazılmıştı (`_diskten_oku` ·
`_diske_yaz`). Kapı reddetti:

> `test_indeks_DISKTE_ARTEFAKT_URETMIYOR` — *«bu depo bir kez gitignore'lu bir derleme
> artefaktından okuyan ölçüm yüzünden aynı kaynakta **farklı sayı** gördü ⑪. Öneri
> indeksi o sınıfa girmez: bellekte yaşar, süreçle ölür — okunacak bayat bir dosya
> **yoktur**.»*

⟹ Geri alındı; yerine **reddedilmiş denemenin kaydı** bırakıldı. ⚠ Ve planın `5.7`
maddesi bir **lab üreteci** istiyor (`lab/oneri_indeksi.py`) — ürünün diskten
**okuması** değil; ikisini aynı şey saymak kapıyı düşürür.

*Bir açılış maliyetini düşürmek için bayatlık sınıfını geri getirmek, ödediğinden pahalı
bir tasarruftur.* Ve **kapıdan geçmemiş kod commit edilmediği için** bu geri alma bir
gerileme değil, bir **eleme** oldu 🆬.

**Kanıt:** `oneri_motoru · onek_degismezi · oneri_cumle · bos_girdi_cekirdek ·
gomulen_gorunum_tavani · oneri_gomme_temsili · alan_haritasi` → **124 ✅**.

---

## §59 — TEK HANELİ DEĞER GÜRÜLTÜSÜ: **rakam pekiştirir, kanıtlamaz** 🆢

`§57`'nin token kapsamı bir yan etki bıraktı: `«ram 3 neden düşük»` listesinde *«bu ay
**3**'ün kaza adedi ne kadar?»* — katalogdaki `3` (şiddet kodu) sorgudaki `3` token'ına
**tek başına** vuruyordu.

### İlk çarem komşuyu bozdu ⑯ — ve kapı ondan önce ben yakaladım

Rakam token'larını **toptan** elemeyi denedim. Sonuç ölçüldü:

```
«ram 3 neden düşük» → RAM-1 · RAM-1 · RAM-2 · RAM-3 …   🔴 sıra kayboldu
```

Çünkü `RAM 3` ile `RAM-1` **eşitlendi**: ikisi de yalnız `«ram»`dan kapsam alıyordu.
*Bir gürültüyü elerken, gürültüyü ayıran işareti de elemiş oldum.*

### Doğru ölçüt uzunluk değil **CİNS**

* Rakam token'ı **pekiştiricidir**: harf kanıtı **varsa** sayılır, yoksa sayılmaz.
* `3` (şiddet kodu) → harf kanıtı **yok** → 0 → listeden düşer ✅
* `RAM 3` → `«ram»` (harf) + `«3»` (rakam) = **2** → `RAM-1`'in (1) **üstünde** ✅

⚠ **`_KISA_ESIK` kullanılmadı** ㊲ ve gerekçesi yazıldı: o eşik *«kısa etiket bağlamsız
gömülmez»* sorusunun cevabıdır (`4`); buradaki soru *«bir token eşleşmeyi kanıtlar mı»*.
`«ram»` üç harf, `«3»` bir hane — **uzunluk ikisini ayırmaz**.

### Kapı — dört yüklem, biri **zıt ölçüt** 🆃

`tests/test_token_kapsami.py` (**4 ✅**): uzun cümle varlığı **kaybetmez** · tek haneli
değer **tek başına eşleşmez** · **rakam hâlâ ayırt eder** *(ilk çaremin kurbanı)* · tek
kelimelik girdi davranışı **değişmedi**.

**Kanıt:** `token_kapsami · oneri_motoru · onek_degismezi · oneri_cumle ·
oneri_gomme_temsili · alan_haritasi` → **123 ✅**.

---

### §59-ek · Kullanıcı sorusu: *«öngörüye basınca ne oluyor?»* — ölçülmüş cevap

| tıklanan satır | yol | LLM | süre |
|---|---|---|---|
| hazır `cube_query` taşıyan cümle | **`POST /cube`** | ⊘ | ~30 ms |
| *«… neden bu seviyede?»* (makro) | **`POST /oneri/makro`** — 5 adımlık determinist plan | ⊘ | tek istek |
| ikisi de yoksa | metin → `/ask` | olabilir | değişken |

Sıra **şarttır** (makro → sorgu → metin): makro satırının `cube_query`'si **yoktur**.
Kapı: `test_oneri_tiklamasi_sorgu_kosar.py` — *«öngörü tıklamasında `/ask` çağrılmaz»*,
🅑 mutasyonla kanıtlı. Şeridin kendisi de LLM'siz: katalogdan üretilir, sorgu koşmaz
(ılık **0,10 s**).

---

## §60 — 🔴 ZİNCİR ≠ THREAD: *«konudan çık»* seni sohbetten de çıkarıyordu

### Kullanıcının tarif ettiği doğru model

> *«Kişi bir soru sorar, cevap gelir; takip açıksa devam eder, sonra takibin takibi…
> zincir olur. Bir yerde zinciri keserse **aynı thread içinde yeni konuya** geçmiş olur.»*

Ve bu model üründe **zaten yazılı** — `app/context.py`, *«tartışmaya kapalı»* etiketiyle:

> **Thread bir UI GRUPLAMASIDIR, SEMANTİK SINIR DEĞİLDİR.** Bir thread cube/bağlam
> sınırı taşımaz; yeni thread **yalnız açık kullanıcı eylemiyle** doğar.

### Ölçülen ihlal — **iki edim, tek işleyici**

```tsx
const yeniKonu = () => { …bağlamı temizle…; setActiveThreadId(null); };
onYeniSohbet={yeniKonu}     // «+ yeni sohbet» → yeni THREAD   ✅ doğru
onClearContext={yeniKonu}   // «konudan çık»   → yeni THREAD   🔴 yanlış
```

Ve eski yorum bunu bir **karar** gibi savunuyordu: *«`+ yeni sohbet` düğmesi AYNI
edimdir — iki düğme, TEK sahip.»* Ölçüldü: **aynı edim değiller** 🆪.

⊙ Sunucu tarafı zaten doğruydu: çapa **yalnız `continue`** yolunda gönderiliyor
(`cube_query: contextCq`), taze soru çapasız gidiyor ve `is_followup` üretmiyor. Kusur
tamamen istemcinin **iki edimi karıştırmasıydı**.

### Çare

| edim | işleyici | etkisi |
|---|---|---|
| *«konudan çık»* | **`zinciriKes`** | bağlam · rapor · diyalog · `prev_sql` · görünüm sıfırlanır; **thread KALIR** → sonraki soru aynı sohbetin **yeni zinciri** |
| *«+ yeni sohbet»* | **`yeniSohbet`** | `zinciriKes()` **+** `activeThreadId = null` |

⚠ İkincisi birincisini **çağırıyor** — iki temizleme listesi olsaydı bir gün biri eksik
kalırdı ㊲.

⚠ **Tavan 🆄** ateşledi (+1 satır); **yükseltilmedi**, gövde tek satıra toplandı.
`tsc --noEmit` **temiz** (kapı `node_modules` yokken atlıyor 🅢 — elle koşuldu).

**Kanıt:** `frontend_buyume · frontend_derlenir · uc_yetim_degil · konusma_baglamsiz`
→ **31 ✅** *(tavan düzeltmesinden sonra 15 ✅ yeniden)*.

### §60-ek · Kapı kuruldu ve **mutasyonla** kanıtlandı

`tests/test_zincir_thread_ayrimi.py` (**3 ✅**):

| yüklem | savunduğu |
|---|---|
| *«konudan çık» → `zinciriKes`* | bağ doğru yerde |
| **`zinciriKes` `setActiveThreadId`'ye dokunmaz** | **asıl değişmez** |
| *«+ yeni sohbet» → `yeniSohbet`* ve o thread'i **düşürür** + `zinciriKes()` çağırır | 🆃 zıt ölçüt |

Üçüncüsü olmasaydı *«+ yeni sohbet»*i de thread'de bırakmak kapıyı yeşil bırakırdı — ve
o zaman **yeni sohbet açılamazdı** 🆐.

🅑 **Mutasyon:** `zinciriKes`'e `setActiveThreadId(null)` geri kondu →
`test_ZINCIRI_KES_THREADE_DOKUNMAZ` **kırmızı**; geri yüklendi, `diff` temiz.

---

## §61 — AGENTIC DENETİMİ: planın `Thread 5`'i **madde madde** koda karşı ölçüldü

Kullanıcı sordu: *«çok adımlı işlemler için agentic sistem, uzun istemleri pill'lere
ayırma neden hâlâ yok, direkt koşuyor?»* — **tek tek ölçtüm.**

| plan maddesi (`Thread 5` · `§7`) | kodda | ölçüm |
|---|---|---|
| **Kademe ①** tek adım, ⊘LLM | ✅ | `route()` → `cube_query`; öneri tıklaması `/cube` (0 token) |
| **Kademe ②** adlı makro, N adım, ⊘LLM | ✅ | `makro.MAKROLAR` + `/oneri/makro` → `plan_tuketici.calistir` **LLM'siz** |
| **Kademe ③** serbest kompozisyon, ✅LLM | ✅ | `ask.py:4132` `plan_garson.sarmala(...)` — garson plan yazar |
| **Plan ÖNİZLEME** — *«plan KOŞMUYOR, pill satırı olarak gösterilir»* `[düzenle][koş][iptal]` | 🔴 **YOK** | `/oneri/makro` planı **anında koşuyor**; `PlanAdimlari.tsx` **geriye dönük** (kendi belgesi: *«koşum bitince yazılır»*) |
| **Uzun girdide şerit sönmesi** (`≈8 kelime`/fiil) | 🔴 **YOK** | `OneriSeridi`'de kelime eşiği **hiç yok** |
| **Bütçe görünürlüğü** (*«3 adım/12 · 2 sorgu/12»*) | ◐ | `hava_boslugu`/`agent_run` alanları var; şeritte **gösterilmiyor** |
| `8.3` `ε` · `5.5` sıklık | 🔴 | `§55`: ikisi de **yazılı kararlarla çakışıyor**, kullanıcı kararı bekliyor |

### ⚠ Ve planın **kendi kapsam beyanı** — adil olmak için

> **`FAZ 7 · Çapa · pill · makro · plan önizleme` ⊘ DEMO DIŞI** — *«bu faz iddiayı
> kanıtlamıyor, zenginleştiriyor. Demo başarılı olursa açılır. Silinmedi, ertelendi.»*

⟹ O fazın **dört** kaleminden **üçü zaten teslim edildi** (çapa `§41` · pill `§51`+`§53`
· makro `§42`) — yani kapsam dışı ilan edilmiş bir faz **fiilen açıldı**. Eksik kalan tek
kalem **plan önizlemesi**, ve kullanıcının işaret ettiği şey **tam da o**.

*Bir fazı ertelemek, onun en değerli maddesini de erteler — ve o madde çoğu zaman
ötekilerin sebebidir.*

### Neden plan önizlemesi **en değerli madde**

Planın kendi ölçümü: *«bugün plan yazılıp **koşuyor**; 7. adımda çökerse kullanıcı
**sonda** öğreniyor (onarım tutma **%25**, payda 16). Pill kipinde plan **koşmadan**
görünür ve düzeltilir.»*

> *Bir planı koşmadan önce görünür yapmak, onu onarmaktan ucuzdur.*

### Sıradaki iki iş (bu denetimin çıktısı)

1. **Uzun girdide şerit sönsün** — küçük, ölçülü, bugün yapılır.
2. **Plan önizleme** — `/oneri/makro`'ya `kos=false` (plan döner, koşmaz) + pill satırı
   `[düzenle] [koş] [iptal]`. ⚠ `plan_kosucu.dogrula` **zaten** planı doğruluyor; önizleme
   onu **koşmadan** çağırır ㊲.

---

## §62 — 🔴🔴 KAPSAMI YANLIŞ OKUDUM: belgenin **BAŞLIĞI** işin kendisiydi

Belgenin adı: **«route ve garson, KARAR VERİCİ olmaktan çıkıp TAHMİNCİ oluyor»**.
`§3.1` bunu tabloyla veriyor:

```
                ÖNCE                          SONRA
route()   →  KARAR VERİR, İCRA EDER      →  ADAY SIRALAR (icra etmez)
garson    →  route çekilince KARAR VERİR →  aday listesini ZENGİNLEŞTİRİR
                                             + kademe ③'te PLAN TASLAĞI çizer
kullanıcı →  cevabı alır                 →  🔴 KARARI VERİR (bir tık)
```

### Ne yaptım, ne yapmadım — dürüst ayrım

| plan maddesi | durum |
|---|---|
| öneri şeridi · cümle üretimi · pill · çapa · makro · tıklama=koşum | ✅ teslim |
| **route icra etmez, ADAY SIRALAR** | 🔴 **yok** — `/ask` hâlâ karar verip koşuyor |
| **garson karar vermez, PLAN TASLAĞI çizer** | 🔴 **yok** — `route_supheli` → garson → **cevap** |
| **kullanıcı kararı verir (bir tık)** | 🔴 **yok** — onay adımı hiç yok |

⟹ Ben **arayüzü** kurdum, **rol değişikliğini** kurmadım. Öneri katmanı bu belgede bir
*özellik* değil, o rol değişikliğinin **görünür yüzü**ydü.

### Ve `§49`'da kullanıcıya sorduğum soru **belgede zaten cevaplıydı** 🅞

*«Belirsizlikte garson mu gitsin, aday pill'i mi?»* diye sordum — `§28`'in başlığı:
**«GARSON = SEÇİLMEYENİN PILL'İNİ HAZIRLAYAN»**. Yani cevap yazılıydı; ben kararı
soruya çevirdim. *Bir belgede yazılı olanı sormak, onu okumamış olmanın kibar hâlidir.*

⚠ Bu, `CLAUDE.md`'deki **«EN ÜST KURAL — GARSON DEVRİ»** (2026-08-08) ile çelişiyor
görünür; ama bu belge **08-12** tarihli ve rolü açıkça değiştiriyor: garson **gitmeye
devam eder**, ama vardığında **karar vermez — taslak çizer**. İkisi çelişmiyor: devir
korunur, **icra** kullanıcıya geçer.

### Sıra — bundan sonraki iş budur

1. **Plan önizleme** (`kos=false`): plan üretilir, `plan_kosucu.dogrula`'dan geçer,
   **koşmaz**; adımlar dikey pill listesi + `[düzenle] [koş] [iptal]`.
2. **Uzun girdide şerit sönmesi** (`Thread 5` kırılma #1).
3. **Marj kapısı → aday pill'leri** (`§28`): belirsizlikte garson **taslak** verir,
   kullanıcı seçer. *(`emin_miyim` var, `/ask`'ta 0 çağrı — `§49`.)*

---

## §63 — ROL DEĞİŞİKLİĞİNİN İLK PARÇASI: **çok adım → HER ZAMAN önizleme**

Belgeyi doğru okuyunca `§28.3` bir bayrak değil bir **karar tablosu** verdi:

| garson çıktısı | davranış |
|---|---|
| tek adım · emin | 🟢 koşar, pill'ler **makbuz** olur |
| tek adım · kararsız | 🔵 pill **önerilir**, kullanıcı onaylar |
| **çok adım (N ≥ 2)** | 🔴 **HER ZAMAN önizleme** |
| yazma fiili | 🔴 senkron onay |

### Uygulanan

`POST /oneri/makro` — `kos` (varsayılan **`false`**). `N ≥ 2` ve onay yoksa: plan
üretilir, **`plan_kosucu.dogrula`'dan geçer**, `plan_tuketici.calistir` **çağrılmaz**.

⚠ **İkinci doğrulayıcı yazılmadı** ㊲: önizleme *«daha gevşek»* bir yol değil **koşumsuz**
yoldur — aynı kapı. Bütçe de zaten `dogrula`'nın içinde (`azami_sorgu` ·
`plan_semasi.AZAMI_ADIM`); ikinci bir sayaç bir gün **iki farklı sınır** olurdu.
⚠ Adım metnini **`plan_tuketici._adim_metni`** yazıyor — ürünün kendi anlatıcısı ㊷.

### Ölçülen (uçtan uca)

```
onaysız  → source=onizleme · gecerli=True · 5 adım
           1 SORGU · 2 KIYASLA · 3 KIR · 4 SORGU · 5 ANLAT
kos=true → source=cube · 5 adım koştu
```

### Kapı — dört yüklem, biri **zıt ölçüt** 🆃

`tests/test_plan_onizleme.py` (**4 ✅**): onaysız **koşmaz** · önizleme **adımları taşır**
(sıra ve fiil) · **onaylı koşar** 🆃 · **geçersiz plan da gösterilir** (dürüst ret).

**Kanıt:** `plan_onizleme · makro_recetesi · orkestrator` → **57 ✅**.

### ⚠ Kalan — rol değişikliği henüz TAM değil

| madde | durum |
|---|---|
| çok adımlı makro → önizleme | ✅ bu bölüm |
| **FE**: dikey adım listesi + `[düzenle] [koş] [iptal]` | 🔴 sıradaki |
| **garson çıktısı da** plan olsun (`§28`: *«garson = seçilmeyenin pill'ini hazırlayan»*) | 🔴 `ask.py`'de `emin_miyim` **0 çağrı** |
| uzun girdide şerit sönmesi (`>8 kelime ∨ fiil`) | 🔴 |
| bütçe görünürlüğü (`adim=8 · saniye=30 · sorgu=12`) | ◐ doğrulayıcıda var, **ekranda yok** |

---

## `§64` — ÖNİZLEMENİN **YÜZÜ**, ve uzun girdide şeridin **susması**

> `§63` ucu kurdu; ama bir arka-uç yeteneği **tüketicisi olmadan «bitti» değildir** 🆘.
> Ölçüldü: `postMakro` `kos` alanını **hiç göndermiyordu** ve dönen `adimlar` **okunmadan
> atılıyordu** — yani kullanıcı için önizleme *hâlâ yoktu*.

### Ne yapıldı

| # | iş | yer |
|---|---|---|
| ① | `postMakro` **`kos` taşır** — onay bir alan, bir seçenek değil | `lib/api-client.ts` |
| ② | önizleme durumu + onay mekaniği | 🆕 `lib/onizleme.ts` (`useOnizleme`) |
| ③ | **dikey** adım listesi + `[koş] [düzenle] [iptal]` | 🆕 `components/PlanOnizleme.tsx` |
| ④ | pill satırının **altına** yerleşim | `Besteci.tsx` |
| ⑤ | **uzun bileşikte şerit söner** (`>8 kelime`) | `OneriSeridi.tsx` |

**Akış:** çok adımlı makro tıklanır → uç `source="onizleme"` döner → `yakala()` **`true`**
döndürür ve cevap **geçmişe/tuvale yazılmaz** (bir önizleme bir cevap değildir; yazılsaydı
sonraki takip sorusu **hayalî** bir bağlam üzerinden sorulurdu) → kullanıcı `[koş]` derse
**aynı gövde** `kos: true` ile gider.

### Üç tasarım kararı, üçü de planın bir cümlesinden

* **adımlar dikey** (satır `1242`: *«adımlar dikey, yuvalar yatay; ikisi aynı şeritte
  olmaz»*) — bir plan bir **sıradır**; pill satırı yatay kalır çünkü o bir **kümedir**.
* **`gecerli === false` de çizilir** (`§7` dürüst ret) — `[koş]` söner, gerekçe kalır.
* **`[düzenle]` planı değil cümleyi düzenler**: adım kurcalama sözleşmesi sunucuda **yok**;
  kullanıcının kendi cümlesi besteciye geri yazılır. Adım düzenleme **açık borç** 🅖.

### Tavan hikâyesi — kapı yine yol gösterdi

İlk yazım `page.tsx` **+17**, `api-client` **+9**, `types.ts` **+8** büyüttü ve kapı üçünü
de kırmızı verdi. Tavanlar **yükseltilmedi**; kapının kendi öğüdüne uyuldu (*«yeni davranışı
bir bileşene çıkar»*): birleştirme `api-client`'tan **çıkarıldı** (o dosya bir **taşıyıcıdır**,
yorumlayıcı değil → **−2**), durum makinesi `lib/onizleme.ts`'e taşındı. Kalan **`page.tsx`
+4 · `types.ts` +2** gerekçeli `MUAFIYET`'e yazıldı: dördünün hiçbiri mantık değil **bağ**,
ikisi ise sözleşmenin **tek aynasındaki** iki alan.

**Kapı:** `test_onizleme_yuzu.py` (**4 ✅**) — `kos` taşınıyor · şerit uzun girdide **söner**
ve eşik **tek sahipli** ㊲ · önizleme **dikey** ve pill'in **altında** · 🆃 **kısa girdide
şerit hâlâ yanar** (yalnız susmayı ölçseydik, şeridi tümden kapatmak kapıyı yeşil bırakırdı).
**Kanıt:** `onizleme_yuzu · frontend_buyume · plan_onizleme · yetim uç/modül` → **30 ✅**.

### ⚠ Kalan — rol değişikliği hâlâ TAM değil

| madde | durum |
|---|---|
| **garson çıktısı da** plan olsun (`§28`) | 🔴 `ask.py`'de `emin_miyim` **0 çağrı** |
| bütçe görünürlüğü (`adim=8 · saniye=30 · sorgu=12`) | ◐ doğrulayıcıda var, **ekranda yok** |
| fiil tespiti (`>8 kelime **∨ fiil**`) | ◐ bugün yalnız kelime sayısı 🅖 |
| adım **düzenleme** | 🔴 sunucuda sözleşme yok 🅖 |

### `§64-ek` — önizlemenin **dili**: makbuzun cümlesi kullanıcının cümlesi değil 🅔

Canlıda (`s24`→`s27`) dört biçim/dil kusuru ölçüldü ve dördü de aynı kökten: önizleme,
**makbuzun** metnini olduğu gibi basıyordu. Makbuz geriye dönüktür ve okuru tanı arayan
biridir; önizleme ileriye dönüktür ve okuru **karar veren** kişidir.

| ölçülen (canlı) | çare |
|---|---|
| `SORGU` rozeti + *«**SORGU** — …»* — **fiil iki kez** ㊲ | önek atılır (fiil ayrı alan) |
| ekranda düz `**` ve `` ` `` | markdown işaretleri düşer (önizleme **düz metin**) |
| *«YALNIZ son adım olabilir»* · *«çıktısı satır değil…»* — **iç kısıt cümlesi** | 🆕 `FIIL_ONIZLEME` — aynı sözlüğün **ikinci kipi** 🅔 |
| *«$3 adımının»* → ham değiştirmede *«3. adımının»* | ek **birlikte** değişir ㊵ |

🔴 **İkinci bir sahip doğmadı.** Cümlenin sahibi hâlâ `plan_semasi` (tek kayıt, iki kip)
ve `plan_tuketici._adim_metni`; `routers/oneri._onizleme_satiri` yalnız **biçim** yapar.
İki ayrı cümle yazılsaydı kullanıcı **onayladığı şeyle koşan şeyi** karşılaştıramazdı.

⚠ `{boyut}` bir **yuvadır**, dışarıdan iliştirme değil: Türkçe eki cümlenin **içinde**
yazılı (*«makine kırılımı ekler»*) — `§18.8` morfoloji tuzağı. Boyut yoksa yuva düşer.

**Canlı kanıt (`s27`+):**

```
1 SORGU    ort_oee · makine kırılımında
2 KIYASLA  akran ortalamasıyla karşılaştırır
3 KIR      makine kırılımı ekler
4 SORGU    3. adımın ürettiği sorguyu koşar
5 ANLAT    bulguları cümleye çevirir
```

**Kapı:** `test_plan_onizleme.py` **8 ✅** (fiil yinelenmez · markdown sızmaz · **her fiilin
önizleme kipi var** 🅜 · tanım/iç alan basmaz · yuva kalıntı bırakmaz · tamlama bozulmaz).

---

## `§66` — **CEVAP MERDİVENİNDE DE ONAY VAR**: rol değişikliğinin kalan yarısı

`§63` önizlemeyi **makro** yolunda kurmuştu. Ama asıl merdiven `plan_tuketici.cevap`'tan
geçiyor ve orada plan **hâlâ koşuyordu** — kodda ölçüldü:

```python
_n = len(plan["adimlar"])
out = calistir(plan, …)          # ⟵ N kaç olursa olsun, onay YOK
```

Yani *«route ve garson KARAR VERİCİ olmaktan çıkıp TAHMİNCİ oluyor»* (`§3.1`) kararı
**yarım** uygulanmıştı 🆘.

### Ne yapıldı

| # | iş | yer |
|---|---|---|
| ① | N ≥ 2 → `source="onizleme"`, **koşmaz** | `plan_tuketici.cevap` |
| ② | önizleme **planın kendisini** taşır (`plan_taslagi`) | `schemas.AskResponse` |
| ③ | 🆕 **onay ucu** `POST /plan/kos` — onaylanan planı koşar, ⊘ LLM | `routers/oneri.py` |
| ④ | bayrağın **tek sahibi** | 🆕 `features.oneri_katmani_acik` ㊲ |
| ⑤ | koşum cevabının **tek biçimi** | 🆕 `plan_tuketici.kosum_yaniti` ㊲ |
| ⑥ | adım cümlesinin **tek sahibi** (iki önizleme aynı cümleyi okusun) | `plan_tuketici.onizleme_satiri` ㊲ |
| ⑦ | FE: `/ask` cevabı da önizleme olabilir; `[koş]` → `/plan/kos` | `lib/onizleme.ts` · `page.tsx` |

### 🔴 Onay neden **planı geri yolluyor**

Onayda planı **yeniden üretmek** iki şeyi bozardı: `E-8` (sıcak yolda ikinci seri LLM turu)
ve — daha ağırı — **onayın anlamı**. Model aynı soruya iki farklı plan üretebilir; kullanıcı
A'yı onaylayıp B koşulsaydı onay bir **tören** olurdu.

⚠ Güven sınırı **genişlemedi**: `POST /cube` zaten istemciden gelen bir `cube_query`'yi
koşuyor. Plan da aynı iki kapıdan geçer — `plan_kosucu.dogrula` (**kapalı fiil kümesi**) +
her adımın `parse_cube_query` beyaz listesi. *Bir gövdeye güvenmek ile onu doğrulayıp
koşmak aynı şey değildir.*

### Kapının bana verdiği yedi kırmızı — ve dördü **haklıydı**

| kırmızı | ne dedi | ne yapıldı |
|---|---|---|
| `test_cevap_alani_yetim_degil` | *«üç yeni alanın FE tüketicisi yok»* 🆘 | FE **aynı demette** bağlandı |
| `test_plan_tuketici` (4) | *«plan artık koşmuyor»* | **doğru** — kapsam beyanı yazıldı 🆂, `onaylandi=True` varsayıldı, **davranış kapısı** eklendi |
| `test_maskeleme_tumleyeni` | `AskResponse` 44 → **47** alan | kayıt tazelendi 🅟 |
| `test_modul_buyume` | `ask()` +1 satır | üç `kwarg` → **bir kavrayış**; kalan +1 gerekçeli muafiyet |

⚠ Ve `test_BAYRAGIN_TEK_SAHIBI_VAR` **kendi ilk yazımında** yanıldı: `"resolve_for" in metin`
bir **yorum satırına** vurdu 🅞 — ölçüt *«sözü değil kullanımı ara»* biçimine çekildi.

**Kapı:** `test_garson_plani_onaysiz_kosmaz.py` (**5 ✅**: kaynak sırası ㊴ · plan taşınıyor ·
`KURAL B` · bayrağın tek sahibi ㊲ · 🆃 onay yolunda **0 LLM**) + `test_plan_tuketici.py`'de
**davranış** kapısı. **Demet: 1752 ✅ / 0 🔴.**

### ⚠ Kalan

| madde | durum |
|---|---|
| `§28.3` satır 2 — **tek adım + kararsız → 🔵 pill onaya** | 🔴 uyum oranı hesaplanıyor, **kapıya bağlı değil** |
| `§28.3` satır 4 — **yazma fiili → senkron onay** | ◐ yazma fiili bugün küp yolunda yok |
| bütçe görünürlüğü (`adim=8 · saniye=30 · sorgu=12`) | 🔴 ekranda yok |
| fiil tespiti (`>8 kelime **∨ fiil**`) | ◐ bugün yalnız kelime sayısı 🅖 |

---

## `§67` — **`note` bir cümledir** + **kararsız garson onaya düşer**

### ① Adaşlıktan doğan kusur — `note` ham liste basıyordu

Canlı ölçüm (`s30`, curl, **iki uçta birden**):

```
note = [{'sira': 1, 'fiil': 'SORGU', 'satir': 1}, {'sira': 2, 'fiil': 'SORGU', …}]
```

Sebep tek satır ve **adaşlık**:

| ad | ne | okuru |
|---|---|---|
| `plan_kosucu.kos()["makbuz"]` | adım başına **kayıt listesi** (`sira·fiil·satir`) | koşucu içi |
| `plan_tuketici.makbuz(plan)` | **cümle** (*«Bu cevap 5 adımda üretildi…»*) | kullanıcı |

`kosum_yaniti` `out.get("makbuz")` okuyordu — **veriyi**, cümleyi değil. Merdiven yolu
(`cevap()`) aynı cümleyi **doğru** kuruyordu; iki yol ayrışmıştı ㊲.

> *Aynı adı taşıyan iki şeyden biri veri, öteki cümle ise, `get` ile okunan her zaman
> yanlış olanıdır* 🅬 — çünkü sözlük erişimi tip sormaz.

⊙ Ve bu, `bolumlere_cevir`'in kendi şerhinin **tekrarı**: sunum koşucu sözleşmesinden
çıkarılmıştı, **not** çıkarılmamıştı — *yarım çıkarılan bir sunum, çıkarılmamış gibi
davranır.* Çare: 🆕 `cevap_notu(plan, out)` — **tek sahip**, iki yol da onu çağırıyor.

**Kapı:** `test_kosum_notu_cumledir.py` (**4 ✅**) — metin · iç alan sızmaz · iki yol tek
sahip ㊲ · 🆃 makbuz **hâlâ** adım sayıyor (temizlik notu boşaltmasın). **Mutasyonla
kanıtlandı** 🅑: eski okuma geri konunca **3 kırmızı**.

### ② `§28.3` satır 2 — garson **kararsızsa** koşmaz

Planın kendi teşhisi: *«garsonun güven sinyali de **HESAPLANIYOR, ama bir KAPIYA
bağlanmıyor**»*. Ölçtüm — `_select_consistent` `uyum_orani` döndürüyor ve üç yere
gidiyordu:

| nereye | ne yapıyordu |
|---|---|
| uyuşmazlık chip'i | `1/1/1` hâli — **zaten vardı** ㊷ |
| iz notu (*«%67 uyum»*) | bir **yazı**, bir kapı değil |
| `oylama_cogunluk` bayrağı | 🔴 **doğrudan koşum** |

Yani `§28.4`'ün orta satırı (`2/3 → pill'leri onaya düşür`) **hiç yoktu**: `2/3` sessizce
koşuyordu. 🆕 `plan_tuketici.kararsiz_onizleme` o kapıdır ve **yeni bir gösterim
açmadı** 🆘 — `§66`'nın onay yüzünü kullanır (`source="onizleme"` + `plan_taslagi`),
çünkü *tek adımlı bir plan da bir plandır* (`MIMARI §2.0`). 🆕 `plan_semasi.tek_adim_plani`
(`tek_adimli`'nın tersi) ㊲.

Kullanıcının gördüğü: *«Bunu anladım ama **emin değilim** (garsonun 3 denemesinden %67'si
aynı sonuca vardı). Koşmadan önce onayla.»* — sayı **beyan edilir** 🅜; *«emin değilim»*
bir özür değil bir **ölçüdür**.

**Kapı:** `test_kararsiz_garson_onaya_duser.py` (**5 ✅**) — kararsızda koşmaz · 🆃 **oy
birliğinde koşar** (yoksa her soru iki tıka çıkardı, `§24`) · `k ≤ 1`'de sinyal yok →
karar yok 🆕 · `KURAL B` · önizleme **onaylanabilir**.

⊘ **Açık borç 🅖:** plan *«pill'ler önerilir»* diyor; bugün önizleme adımı **cümle**
olarak çiziliyor (*«ort_oee · makine kırılımında»*), pill satırı değil. **Karar** doğru,
**gösterim** yarım — ve bunu yazmak, tam yapılmış gibi göstermekten yeğdir.

**Demet: 1457 ✅**, iki kırmızı `ask()` tavanıydı → dört satırın hiçbiri karar taşımıyor,
gerekçeli muafiyet.

---

## `§68` — teklif **pill olarak** okunur + bütçe **ekranda**

### ① `§28.1`'in açık borcu kapandı 🅖

`§67` kararı kurmuştu (kararsız garson koşmaz) ama teklifi **cümle** olarak gösteriyordu.
Planın cümlesi ise birebir: *«öngörüden **seçilmeyenler** için **pill satırını** ve
adımları hazırlamak ve onaya düşürmek»*.

⊘ **İkinci bir pill üreteci yazılmadı** ㊲ — zincir **var olan** halkalardan kuruldu ㊷:

```
cube_query ──niyet.fisten──▶ Niyet ──pill.pillerden──▶ [Pill] ──PillSatiri──▶ ekran
            (🆕 çeviri)      (mevcut)   (mevcut)         (mevcut, `verilen` prop'u eklendi)
```

`coz(soru, schema)` metinden okur; 🆕 `fisten(cq, schema)` **fişten**. Çıktı aynı `Niyet`,
o yüzden pill satırı **tek** yerde biçimlenir.

**Ölçüm (canlı fişle, `enerji_makine`):**

```
[olcu]    'toplam elektrik kwh'
[donem]   '01.07.2026 – 31.07.2026'
[kirilim] 'makine kırılımı'
```

⚠ **Ölçülen tuzak ⑯:** dönem süzgeci `filters` içinde ve boyut adı küpe göre değişiyor
(`donem_tarih`, başka küpte `tarih`). `pillerden` yalnız `"tarih"`i eliyor — ham bir çeviri
iki sınır satırını **iki varlık pill'i** olarak çizerdi. Ayrım **iki okumadan**: önce
`cube_meta["time_dimensions"]`, sonra değerin **şekli** ⑤. **Mutasyonla kanıtlandı** 🅑.

⚠ **Ve kapı beni yönetti ㊸:** `test_YENI_DILBILIM_YAZILMADI` `niyet.py`'de bir
`re.compile` görünce kırmızı verdi — **haklıydı**: o nesne bir **çatıdır**, kalıp sahibi
değil. Şekil ölçüsü `donem_capasi.tarih_sinirimi`'ne taşındı (`_CIPLAK_YIL_RE`'nin komşusu).

### ② Bütçe artık **görünüyor**

`§28.3` önizleme gerekçesini bütçeye bağlıyor, ama sayı yalnız **doğrulayıcıda** yaşıyordu:
plan sınırı aşarsa red gelir, aşmazsa kullanıcı sınıra ne kadar yaklaştığını **hiç görmez**.
*Onay isteyip gerekçesini göstermemek, onayı bir tören yapar.*

Önizleme notu artık: **«5 adım (tavan 12) · 4 sorgu (bütçe 8) — koşmadan önce gözden geçir.»**

⊘ **İkinci sayaç yok** ㊲: adet 🆕 `plan_kosucu.sorgu_sayisi`'ndan (doğrulayıcı da artık
**onu** çağırıyor), sınırlar sabitlerden. ⊘ **Süre yazılmıyor** 🅖 — koşmadan bilinmiyor ve
bilinmeyen bir sayıyı yazmak, onu ölçtüğümüzü söylemek olurdu.

### 🔴 ÖLÇÜLEN BAYAT İDDİA ⑳ — hizalanmadı, KAYDEDİLDİ

`plan_kosucu.AZAMI_SORGU`'nun şerhi *«`AZAMI_ADIM` ile **aynı sayı** olması tesadüf
değil»* diyordu. Ölçüldü: **`AZAMI_SORGU = 8` · `AZAMI_ADIM = 12`**. Yani şema 12 adıma
izin veriyor ama hepsi `SORGU` olan bir plan **koşum kapısında** düşer.

🔴 **Kör hizalama yapılmadı** ㊸: hangisinin doğru olduğu bir **ürün kararıdır** (bütçe mi
gevşer, şema mı daralır) ve ölçülmemiş bir davranış değişikliği olurdu. Yorum düzeltildi,
karar **açık borç** olarak buraya yazıldı 🅖.

**Kapılar:** `test_teklif_pilleri.py` (**5 ✅**, mutasyonla kanıtlı) · `test_butce_gorunur.py`
(**4 ✅**: adet+sınır · sayımın tek sahibi ㊲ · 🆃 sayaç gerçekten sayıyor · ⊘ süre yok).
**Demet: 1762 ✅.** Kapı üç kırmızı verdi, **üçü de haklıydı**: dilbilim sahipliği ㊸ ·
`AskResponse` 47→48 · `types.ts` tavanı.

### `§68-ek` 🔴 **CANLI TUR KUSURU BULDU — ve kütük yalan söylüyordu** 🅯

`§28.4`'ün orta satırını (`2/3`) canlıda **görmeye** çalışırken (🅢) şu çıktı:

```
kütük:  §28.3: garson kararsız (uyum 67%, 3 örnek) → ONAYA düşüyor
cevap:  source = cube · piller = 0 · plan_taslagi = yok
```

Yani dal **ateşlendi**, log **yazdı**, ve kullanıcı **normal cevabı gördü**. Sebep:

```
AttributeError: 'list' object has no attribute 'get'   ← niyet.fisten
```

`schema["cubes"]` bir **sözlük** sanılmıştı; bu depoda her yer onu **liste** okur
(`for c in (schema.get("cubes") or [])` — `kosum_cube_meta` · `context` · `deger_capasi`).
Dış `except` istisnayı **yuttu** ve merdiven normal yoluna döndü.

⚠ **Birim testi bunu göremezdi** 🅡: hepsi `schema=None` geçiyordu — *bir yolun hiç
girilmemesi, o yolun çalıştığının kanıtı değildir.* Yeni kapı **gerçek fikstürle** geçer
(`test_SEMA_LISTEDIR_SOZLUK_DEGIL`).

⊙ İki ders birden: **①** şekli ölç ⑤ — alanın **adını** değil **türünü** de nesneden oku;
**②** *koşan, log basan, hiçbir şey yapmayan* bir dal 🅯 yalnız **canlı turda** görünür —
demet **1762 yeşilken** bu kusur oradaydı.

⊙ Ve `2/3` dalı böylece **canlıda gözlendi** 🅢: `uyum 67% · 3 örnek`, iki ayrı soruda.

**Canlı kanıt (`s33`, aynı soru üç tur — `§28.4`'ün üç kademesi tek ekranda):**

```
tur1  source=onizleme  · 5 pill  · «emin değilim (3 denemeden %67'i aynı)»
        [olcu] OEE · OEE   [olcu] performans · OEE   [olcu] kullanılabilirlik · OEE
        [olcu] kalite · OEE   [kirilim] makine kırılımı
tur2  source=cube+llm  · 0 pill  · oy birliği → KOŞTU
tur3  source=onizleme  · 2 pill  · [olcu] performans   [kirilim] makine kırılımı
```

🅢 **Orta satır artık gözlendi** — ve aynı soruda tur tur değişmesi `§75`'in *«salınım»*
ölçümünün ta kendisi: garson kararsızken sistem artık **koşmuyor, soruyor**.

⚠ Küçük kusur, açık borç 🅖: çok adaylı ölçü pill'i `«OEE · OEE»` yazıyor
(`_olcu_metni` ölçü ve küp etiketini birleştiriyor; `ort_oee`@`oee`'de ikisi aynı).

---

## `§69` — ölçü pill etiketi · yazma fiili kapsam kararı · zincir kapısı

### ① `«OEE · OEE»` — küp adı bir **ayırt edicidir**; ayırt etmiyorsa gürültüdür

Canlı ölçüm (`s33`, kararsız teklif): dört aday da **aynı** küpten (`oee`) geliyordu ama
satırlar *«OEE · OEE»* · *«performans · OEE»* · *«kalite · OEE»* yazdı. `_olcu_metni`
küp etiketini *«birden çok **aday** var»* diye ekliyordu — oysa kendi şerhinin gerekçesi
*«küp adı **ayırt edicidir**»*.

İki kural, ikisi de **mevcut gerekçeden** türedi:

| # | kural |
|---|---|
| 1 | küp adı yalnız adaylar **birden çok küpten** geliyorsa yazılır |
| 2 | küp etiketi **ölçü etiketinin aynısıysa** hiç yazılmaz |

⚠ Ölçüt `silinebilir`den **ayrıldı** ⑯: silinebilirlik *«birden çok **ADAY** var mı»*,
etiket *«hangi **KATALOGDAN**»* sorusudur. Tek bayrakla sürmek bir ekranı öteki uğruna
bozardı — `t13` (`elektrik` ↔ `tep`, iki küp) küp adını **hâlâ** görüyor 🆃.

**Kapı:** `test_olcu_pill_etiketi.py` (**4 ✅**) · komşu `test_pill_katmani.py` **44 ✅**.

### ② `§28.3` satır 4 (*«yazma fiili → senkron onay»*) — **konusu yok**, ve bu ölçüldü

| ne | değer |
|---|---|
| kapalı fiil kümesi | **15** fiil |
| yazan fiil | **0** — `PANO` bile *«hiçbir şey kaydetmez, yalnız taslak»* |
| koşucuda `INSERT`/`UPDATE`/`commit` | **0** |
| SQL guard | `SELECT`/`WITH` dışını reddeder |

Yani bu satır bugün **uygulanamaz**. *«Yapıldı»* demek yalan, *«yapılmadı»* demek eksik
olurdu 🆂; ㉖'nın üçüncü seçeneği seçildi: **kapsam ilan edildi ve bir tel gerildi** ㉕.
`test_yazma_fiili_kapsam_disi.py` fiil kümesinin **fotoğrafını** tutar — küme değiştiği
an kırmızı verir ve ekleyen kişi *«bu fiil yazıyor mu, senkron onay nerede?»* sorusunu
**cevaplamadan** geçemez. *Bir kararı belgeye yazmak onu hatırlatmaz; kapıya yazmak
hatırlatır.*

### ③ Zincir kapısı — çünkü bu operasyonda **iki kez** koptu 🆘

`§64`'te `postMakro` `kos`'u hiç göndermiyordu; `§68-ek`'te dal koşup log basıp hiçbir şey
yapmıyordu 🅯. Yeni kapı `/ask → yakala → onizleme.ts → Besteci → PlanOnizleme →
PillSatiri → [koş] → postPlanKos → POST /plan/kos` halkalarını **tek tek** sınar ve
ölçütü **kullanım** arar, sözü değil 🅞 (kendi zıt ölçütü de bunu sınıyor).

### 🔴 YAPILAMAYAN — ve neden 🅢

**FE tarayıcı doğrulaması yapılamadı:** `localhost:3000` bu turda **kapalı** (`HTTP 000`;
önceki turda `307` veriyordu). Zincir **kodda** bağlı ve kapıyla korunuyor, ama *bir
zincirin kodda bağlı olması ekranda göründüğünün kanıtı değildir* 🆘. Ekran doğrulaması
**açık**: `pnpm dev` ayağa kalktığında *«makinelerin performansı nasıl»* sorulmalı ve
önizleme kartında **pill satırı + `[koş] [düzenle] [iptal]`** görülmelidir.

**Demet: 399 ✅.**
