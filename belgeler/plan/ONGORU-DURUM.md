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
