> ⚠️ **TARİHSEL KAYIT — NORMATİF DEĞİLDİR.** Bu belge 2 Ağustos 2026 turunda YAPILAN İŞİ ve
> alınan kararları anlatır. Mimari otorite `backend/MIMARI.md`'dir; çelişkide o kazanır.

# Faz 0–5 uygulaması: join üreteci, router güveni, terfi kapıları, "neden değişti?"

*(2 Ağustos 2026 — `wren-bağımsız` dalı — HANDOFF #5. Önceki tur: HANDOFF #4, mimari
strateji. Bu tur o stratejinin **uygulanmasıdır**.)*

## 0. Tek paragraf

HANDOFF #4'ün merkezî tezi yarı yanlıştı ve bu tur onu düzeltip uyguladı: `cube_query_to_sql`
gerçekten JOIN üretmiyor, **ama model katmanı üretiyor** — otomatik, çok-sıçramalı, join
pruning'li. Yani bu bir derleyici projesi değil, bir **manifest üretimi** projesiydi. Üreteç
yazıldı (10 güvenlik kapısıyla), dört view-tabanlı cube'un üçü modele taşındı ve view'lar
silindi, router belirsizlikte artık **tahmin etmek yerine soruyor**, VQR'ın incelenmemiş ham
SQL'i tekrar oynatması durduruldu, terfi kuyruğuna diff önizlemesi geldi ve *"neden değişti?"*
kategorisi CubeQuery üzerinde açıldı. **26 commit, 843 test, eval baseline'da sapma yok.**

---

## 1. Ne değişti — fazlara göre

### FAZ 0 — zemin (ölç, güvenceye al, sessiz-yanlışları kapat)

| # | İş | Sonuç |
|---|---|---|
| 0.0 | **`backend/MIMARI.md`** — tek kanonik mimari referansı | Yazıldı; `CLAUDE.md` ona işaretçi verir, HANDOFF'lar "tarihsel kayıt" damgası aldı |
| 0.1 | Telemetri kalıcı | `dima_logs` + `dima_hf_cache` named volume; `_route_path`'e drill/upload/verify sınıfları |
| 0.2 | MDL derlemesi atomik | `build_lock_for(out)` süreç-geneli kilit · `target/` compose sırasında **korunuyor** · `os.replace` ile atomik yazım |
| 0.3 | Ölçüm onarıldı | eval `source`-farkında (`expect_source`) + deterministik-pay kapısı; baseline gerçek değere sabitlendi |
| 0.4 | **Kapsam kapısı ek-farkında** | `_covers` artık Türkçe ek zinciri tanıyor; `kar⊂ankara`, `fire⊂firesiz` sınıfı kapandı |
| 0.5 | `_match_dims` tahkimi | En spesifik eşleşme kazanır — `"yaş grubu bazında fire"` artık 2 değil 1 boyut |
| 0.6 | `always_filter` kaçakları | VQR ham-SQL replay'ine **şema-sürüm kapısı**; manifest-okuma yutması fail-closed |

**Yol boyunca bulunan üretim hatası:** `Dockerfile` ↔ `pyproject` bağımlılık sapması —
`mrml`, `jinja2`, `ruamel.yaml`, `alembic` imajda YOKTU; zamanlanmış rapor e-postaları ve
ölçü terfisi **üretimde patlıyordu**. Ancak testler koşabilir hale gelince görüldü.

**Testlerin 10 saat asılmasının kök nedeni bulundu:** `vqr._embedder()` HF Hub'dan ~2,2 GB
ONNX indiriyor, kimliksiz indirme rate-limit'te **takılıyor** ve `fastembed`/`requests`
tarafında timeout yok. `DIMA_VQR_EMBEDDER=auto|off` eklendi, conftest `off` yapıyor →
**843 test 3 dakikada**, `--network none` ile.

### FAZ 1 — join üreteci (Seçenek C, doğru şekliyle)

`compose.py`'ye 4. post-pass: `_compose_relationship_dimensions`. `relationships.yml`'de bir
`expose:` bloğu → **handle kolonu + calc kolon + boyut** üçlüsü, `base_object`'i o model olan
HER cube'a yayılır.

**On kapının hepsi build-time ve zorunlu.** Bu turda ikisi eksikti ve genel kontrolde bulundu:

- **G7 (sıçrama sınırı = 2)** — zorlanmıyordu ve `hops` provenance'a **sabit 1** yazılıyordu.
  Artık `_hop_derinligi` ölçüyor (hedefteki kolon calc ise 2) ve 3. sıçrama build'i kırıyor.
- **G9 (kompozisyonellik)** — hiç yazılmamıştı, oysa plan onu *"G2/G3'ün tek ucuz otomatik
  dedektörü"* diye tanımlıyordu. `tests/test_kompozisyonellik.py` eklendi: bir ölçünün değeri
  YANINDAKİ ölçülere göre değişiyorsa altta bir join satırları çoğaltıyordur — kullanıcının
  asla fark edemeyeceği hata sınıfı. **Bugün yeşil**, yani G2 işini yapıyor.

Diğer kapıların ölçülmüş gerekçeleri `MIMARI.md §9`'da. En sertleri: **G3** (fan-out
sertifikası — yanlış beyan edilmiş bir MANY_TO_ONE'da +%64 ve bir testte ×3.519 sessiz şişme
ölçüldü) ve **G10** (`always_filter` taşıyan modele join → 34M TL `alis` verisi filtreyi geçti).

**Plan maddesi 1.4 veriyle çürütüldü:** `cari_kodu` **polimorfiktir** (`M1001` müşteri, `T-204`
tedarikçi). `cari_hareketler → musteriler` eklemek satırların **%52,9'unu öksüz** bırakırdı.
`tests/test_relationship_health.py` bu kararı kalıcı olarak koruyor.

### FAZ 2 — view-tabanlı cube'lar modele taşındı

| Cube | Eski taban | Yeni taban | Doğrulama |
|---|---|---|---|
| `parti` | `parti_zengin` (view) | `partiler` | 26 kontrol birebir |
| `mizan` | `mizan_kaynak` (view) | `yevmiye_satirlari` | 21 kontrol birebir |
| `ik` | `ik_zengin` (view) | `bordro` | **73 kontrolün 73'ü birebir** |
| `enerji_tesis` | — | **VIEW KALIYOR** | bileşik `(yil, ay)` anahtarı — MDL ilişkileri tek kolonlu |

Her göçün kabul kriteri **uygulamadan önce** ölçüldü. `ik` göçü Faz 2'nin gerçek sınavıydı:
view `personel_ozluk`'a **doğrudan** join'liyordu (iki bağımsız 1-sıçrama), göç ise
`bordro → personel → personel_ozluk` zinciri kuruyor. İki topoloji ancak öksüz satır YOKSA
aynı sonucu verir — her yönde sıfır ölçüldü ve test bunu bir **ön koşul** olarak kaydediyor.

**Bakım dışında ölçülen ikinci kazanç: join pruning.** `statements.py`'nin gelir tablosu
sorgusu 2 join yerine **0**; `ik.personel_sayisi` 3 tablo taraması yerine **0 join**.

Üç view silindi. Koruma kaybolmadı, **katman değiştirdi**: `parti_zengin`'in tehlikeli join'i
(`partiler.operator = personel.ad_soyad` — benzersizliği DB'de garanti EDİLMEYEN metin alanı)
bugün `partiler_personel` ilişkisi olarak duruyor ve tekilliği artık `test_relationship_health`
**31 ilişkinin hepsi için** ölçüyor. Tek view'a özel bir kontrol genelleşti.

### FAZ 3 — router güveni

**Önce ölçtüm, sonra yazdım.** 5011 soruluk korpusta `route()` 1057 soruda `None` dönüyor —
ama **872'sinde zaten bir netleştirme chip'i vardı**. Yani *"belirsizlik Discovery'ye düşüyor"*
tezi **%82 oranında çoktan çözülmüştü**. Gerçek boşluk 185 soruydu.

- **3.1 ✅ cube-düzeyi beraberlik chip'i.** En büyük kapsanmayan sınıf (88 soru) kanıta göre
  ikiye ayrıldı: 55 soru **birebir eşit kanıt** taşıyor (`bakim` vs `oee`, ikisi de
  *"arıza duruşu"*nu aynı güçle eşliyor ve ikisi de meşru) → chip. 33 soruda kanıt eşit değil
  → **dokunulmadı**, orta güven bandı Intent-JSON'ın. Chip Intent-JSON'dan **önce** geliyor:
  eşit kanıtta LLM'e seçtirmek *"belirsizlikte sor, tahmin etme"* değişmezinin ihlalidir.
  Chip metni `route()` ile **doğrulanıyor** — ilk sürüm yalnız cube adına bakıyordu ve gerçek
  koşuda iki sessiz-yanlış üretti (ölçü kayması + fazladan boyut).
- **3.2 ⏸️ ölçüldü ve ERTELENDİ.** Planın öngörüsünün ilk yarısı tuttu (`dim_owners>1` artık
  norm: %66), ikinci yarısı tutmadı — TB3'ün ölmesi maliyet doğurmuyor, `_match_cube` o 969
  sorunun **%94'ünü** başka kırıcılarla zaten çözüyor. Kalan 55 soru zaten 3.1'in chip'lediği
  beraberlik ve sıçrama derinliği onları **çözemez** (boyut iki cube'da da aynı derinlikte).
- **3.3 ✅ dışlama operatörleri.** Motorun 12 operatörü çalıştırılarak doğrulandı. `neq`/`not_in`
  açıldı: *"beyaz hariç rework"* artık beyazı **eliyor** — eskiden beyazın rework'ünü
  `source="cube"` rozetiyle döndürüyordu. Kural kelime listesi değil **konumsal** (Türkçe
  son-çekim edatı tümlecini izler) ve ek zinciri için Faz 0.4'ün makinesi yeniden kullanılıyor.
  Önek/içerme operatöre **değil değer indeksine** bağlandı, çünkü `starts_with` harf duyarlı
  (`'B'`→Beyaz, `'b'`→boş) ve NL katmanı normalize ediyor — doğrudan bağlamak **güvenle boş**
  sonuç üretirdi.
- **3.4 ✅ chip'lerde üretilen boyutlar.** 7 üretilen boyutun **sıfırı** görünüyordu; sebep
  sıralama değil **kesme**. Planın önerdiği "hop-derinliğine göre sırala" tek başına etkisiz
  olurdu (yerli boyutlar zaten manifest başında).

### FAZ 4 — VQR/terfi kapıları

- **4.1 ✅ güven kapısı — bu turun en ciddi bulgusu.** `ask.py` başarılı **her** bağımsız
  Discovery cevabını ham LLM SQL'iyle birlikte incelenmeden VQR'a yazıyordu ve `near_exact`
  **kaynağa bakmıyordu**. Yani LLM'in kendi tahmini, insan onaylı bir kayıtla **aynı otoriteyle**,
  üstelik yalnızca **benzer** (birebir değil — eşik 0,92/0,85) bir soru için tekrar oynatılıyordu.
  `always_filter` baypası bu yolla **öğrenilmiş** hale geliyordu. Artık replay ile few-shot ayrı
  kapılardan geçiyor: replay yalnız güvenilir kaynaklar (`user`, `user_verified`, `chip_approved`,
  `auto_cube`), `auto_discovery` depoda kalıyor ama oynatılmıyor.
- **4.2 ✅ diff önizlemesi.** `POST /measures/candidates/{cid}/preview` — onayın kuru koşumu,
  yan etkisiz. **Önizlemenin ortaya çıkardığı kusur:** `mdl_writer._yaml()` liste girintisini
  sabitlemişti ve bir ölçü eklemek 266 satırlık dosyanın **266 satırını** değiştirmiş
  gösteriyordu. Modülün kendi başlığı *"git diff asgari kalmalı"* diyordu. Diff 503 → 6 satır.
- **4.3 ✅ kanonik CubeQuery hash'i.** **Cache kurulmadı** (tekrar oranı ölçülmedi); kurulan
  şey doğru **anahtar**. `filters` sıraya duyarsız, `measures`/`dimensions` duyarlı, akış
  bayrakları düşürülür, `mdl_version`+tenant kimliğe girer, `eq` ≠ `neq`.
- **4.4 ⏸️ yapılmadı** — plan onu "opsiyonel, Faz 1-3 sonrası değeri düşer" diye işaretlemişti
  ve öyle oldu: Discovery'nin oturum-cube'una terfisi, kapsam artık üreteçle büyüdüğü için
  daha az gerekli. `dataset.py`'nin bilinen kusurları (`_role()` agregeyi yeniden agrege
  ediyor) hâlâ geçerli ve bir tur ister.

### FAZ 5 — "neden?" (kategori boşluğu)

`app/contribution.py` + `POST /ask/contribution`. Rakiplerin hepsinde bir karşılığı var ve
hepsi semantic layer'ın **dışında**. Buradaki fark: **her bulgu kendi başına bir CubeQuery** —
tıklanır, `/cube` ile LLM'siz koşar, kendi Query Contract'ını üretir. Test bunu iddiada
bırakmıyor, bulgunun sorgusunu gerçekten `/cube`'a gönderip satır döndüğünü ölçüyor.

Üç kural bunu kopya olmaktan çıkarıyor:
1. **Toplanabilirlik kapısı** — katkı payı yalnız toplanabilir ölçülerde tanımlıdır.
   `AVG`/oran/`COUNT(DISTINCT)` için *"bu segment değişimin %40'ını açıklıyor"* cümlesi
   **matematiksel olarak yanlış** olur; bu, bu araç sınıfının klasik sessiz hatasıdır. Kapı
   ada değil **kanıta** bakıyor ve kapının kendisi **veriyle** sınanıyor.
2. **İki ayrı pay** — segmentler birbirini götürebilir (+100/−100 → net 0 ama hikâye var).
   `net_pay` net ~0 iken **None** döner, uydurulmaz.
3. **PVM eşleştirmesi beyan edilir, tahmin edilmez** — `ciro/kg` gerçek bir TL/kg fiyatıdır,
   `tutar/fatura` değildir. Ayrışma **artıksız**: fiyat+miktar+birleşik = ΔV birebir.

---

## 2. Ölçüm — önce/sonra

**`lab/nl_corpus.py`** (~10.800 tur, 4 şirket, LLM'siz, `execute=False`):

| Şirket | Faz 0 sonrası | Faz 5 sonrası | Not |
|---|---|---|---|
| boyahane | 3014/3729 (**%80**) · discovery 490 | 2996/3674 (**%81**) · discovery **435** | −55 discovery = chip'lenen beraberlik sınıfı |
| atiksan | 926/944 (%98) | 926/944 (%98) | değişmedi |
| gulteks | 912/957 (%95) | 912/957 (%95) | değişmedi |
| gitas | 1407/1586 (%88) | 1407/1586 (%88) | değişmedi |

Toplam doğru-cube **%86,6 → %87,2**. `eval/run.py`: precision/coverage/deterministik pay
**+0,0%** (sıfır regresyon, kapı baseline'ın altına düşmedi). Test: **489 → 843**.

**Ölçüm aracının kendisi de düzeltildi** (Faz 0.3): `nl_corpus` eskiden **erişimi** ölçüyordu
(`expected` = tüm cube adları), doğruluğu değil — yani üretecin `"bölüm bazında oee"`yi yanlış
cube'dan doğruya taşımasını **göremiyordu**. Üç yollu doğruluk kanalı eklendi. Ayrıca korpus
`dims[:2]` kestiği için ilişki-türevi boyutları (metadata'nın **sonuna** eklenirler) hiç
sormuyordu — yapısal körlüktü, düzeltildi.

---

## 3. Bilinçli olarak YAPILMAYANLAR (ve nedenleri)

| Yapılmadı | Neden |
|---|---|
| **Join planlayıcı** | `wren_core` "önceden bildirilmiş adlandırılmış geçiş" ailesinde; bu ailenin işi bir **üreteç**. Cube Dijkstra'yı yazdı sonra "view kullanın" dedi. Planlayıcı = denetlenemez tie-break = Query Contract'ın varlık sebebine aykırı. |
| **Skaler `confidence`** | Karar noktaları ayrık ve her biri **karşılaştırılabilir kanıta** dayanıyor. 0–1 arası bir sayı aynı kararı verir ama **gerekçesini gizler**; kalibre edilmedikçe güven değil süs olur. |
| **Sıçrama-derinlikli cube tercihi (3.2)** | Ölçüldü: uygulanabileceği soru sayısı 11 ve o 11'de derinlik **ayırt etmiyor** (boyut iki cube'da da aynı derinlikte). Gerçek bir belirsizliği denetlenemez bir tercihle kapatmak olurdu. |
| **Sonuç cache'i (4.3)** | Tekrar oranı **ölçülmedi** — telemetri yeni kalıcı oldu, veri birikmedi. Anahtar yazıldı, cache yazılmadı. |
| **Aday kümeleme (4.2)** | Doğrulanacak üretim verisi yok, embedder testlerde kapalı. Ölçülmemiş kuyruk şişmesi için altyapı kurulmaz. |
| **`is_null` / eşik olumsuzluğu (3.3)** | *"firesiz partiler"* kategorik değer dışlaması değil, bir ÖLÇÜ üzerinde koşul; bu katalogda tutamak yok (`maliyet` ne boyut ne ölçü). Faz 0.4 sayesinde en azından **sessiz-yanlış değil dürüst red**. |
| **`starts_with`/`contains` operatörü** | Motor tarafı **harf duyarlı**, NL katmanı normalize ediyor → doğrudan bağlamak **güvenle boş** sonuç üretirdi ve boş sonuç "veri yok" gibi okunur. Değer indeksinde çözülüp `in`e indirgendi. |
| **`tedarikciler.sehir/tur` boyutları** | SQL doğruydu ama **tek satır** döndürüyordu (tüm partiler Çorlu'lu). Kardinalite 1 = sıfır ayırt edicilik + gerçek belirsizlik maliyeti. Geri çekildi, `test_uretilen_boyutlar_AYIRT_EDICI_olmali` kapı oldu. |
| **Kişi-verisi derleyici kapısı** | Kullanıcı kararı (ertelendi). Ucuz kanca hazır: `dimension_origin`'e `sensitivity` etiketi eklemek konfigürasyon işi olur, göç işi değil. |

---

## 4. Açık kalanlar

**Doğruluk / güvenlik**
- ❌ **Discovery ham SQL'i `always_filter`'ı baypas ediyor** — *öğrenilmesi* Faz 4.1'de
  durduruldu ama üretimi açık. Kalıcı çözüm uygulama katmanında değil **motor seviyesinde**
  (session property / DB RLS).
- ❌ **`drill.py` raw leaf** aynı baypasta.
- ❌ **`dry_plan` kolon varlığını doğrulamıyor** (`strict_mode=False`) → uydurma kolonlu bir
  ölçü ifadesi **onaydan geçer** ve müşteri DB'sinde patlar. `test_member_sweep.py` build-time
  `LIMIT 0` taraması yapıyor ama **terfi onayı** o taramayı çalıştırmıyor. Bir tur ister.
- ❌ **`_syn_hit` altdizi körlüğü** — `_uncovered` düzeltildi ama `_syn_hit` aynı hastalıkta ve
  **boyut seçimini** bozuyor (`"yas" ⊂ "kıyasla"`). Etki alanı daha geniş, ayrı tur.

**Altyapı**
- ⚠️ **Compose kilidi süreç-içidir** (`threading`), süreçler arası değil. Bu turda **yeniden
  üretilerek** teşhis edildi (iki test konteyneri aynı bind mount'a paralel). Üretimde tek
  konteyner olduğu için ısırmıyor; çok-süreçli dağıtımda `fcntl.flock` gerekir.
  **Testleri paralel iki konteynerde koşturmayın.**
- ⚠️ **Telemetri boş.** Volume eklendi ama veri birikmedi → *Intent ≥%70 / Discovery <%30* KPI'ı
  ve `route-distribution` hâlâ **ölçülemez**. Faz 4.3/4.4 kararlarının önkoşulu budur.

**Bilinen sınırlar (belgelenir, çözülmez)** — `MIMARI.md §9.2`: rol-oynayan boyut yok,
ölçü-A × ölçü-B tek CubeQuery'de olamaz, view'lar ilişkilere katılamaz, bileşik anahtarlı
ilişki ifade edilemez.

---

## 5. Devralacak kişi için

1. **Önce `backend/MIMARI.md`'yi oku** — özellikle §5 (YAPILMAYACAKLAR, gerekçeleriyle) ve
   §6 (bilinen kusurlar). Bu belge tarihsel kayıttır, o normatiftir.
2. **Ölçmeden değiştirme.** Bu turun en değerli üç bulgusu (VQR güven kapısı, `mdl_writer`
   girinti kusuru, `_uncovered` altdizi körlüğü) hiçbiri koda bakarak değil, **bir şeyi
   çalıştırıp çıktısına bakarak** bulundu. Planın kendi öngörülerinden ikisi (1.4, 3.2)
   ölçümle **çürütüldü**.
3. **Kelimeye özel yama yok.** Bir soru yanlış cevaplanıyorsa kök nedeni düzelt, örneği değil.
   Bu turda dört kez cazip oldu, dördünde de genel kural yazıldı.
4. **Testler `--network none` ile ve `DIMA_VQR_EMBEDDER=off` koşar.** Aksi halde embedder
   indirmesi asılır (10 saat vakası).
5. **Backend Docker'da ve bind-mount YOK** → her kod değişikliğinde `docker compose build && up -d`.
   (Bu ortamda yalnız `docker-compose` v1 var; önceki konteyner varsa `KeyError: 'ContainerConfig'`
   verir, önce eski konteyneri silin.)
