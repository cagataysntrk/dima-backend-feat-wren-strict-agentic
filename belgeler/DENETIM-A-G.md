# DENETİM A–G — *faz denetiminden sonraki yedi kalem*

> **Disiplin aynı:** bulgu → **ölçüm** → karar → kapı. Hiçbir sayı ölçülmeden alınmaz;
> denetim ajanları bu oturumda **altı kez** yanıldı, kendi problarım **iki kez**.
>
> ⟳ Açıldı 2026-08-12. Faz denetimi (`DENETIM-FAZ-A-F.md`) **kapandı**, gerçek kalem 0.

| kalem | konu | durum |
|---|---|---|
| **A** | iş sözlüğü: elle değil **kullanımdan hasat** | 🟣 ölçüldü — *aşağıda* |
| **B** | route'un **çürütülebilirliği** + garson | ✅ **KAPANDI** — *aşağıda* |
| **C** | Wren motorunun **kullanılmayan** yetenekleri | 🟣 ölçüldü — *aşağıda* |
| **D** | agentic önerileri **tek tek** | 🔵 |
| **E** | cevap biçimi + UX önerileri **tek tek** | 🔵 |
| **F** | LLM girdi token'ı / maliyet | 🔵 |
| **G** | repo düzeni · **yetim uç kapısı** · belge şişkinliği | 🔵 |

---

## A · İŞ SÖZLÜĞÜ — **ÜÇ İDDİADAN İKİSİ ÖLÇÜMLE DÜŞTÜ**

### A.0 Ölçüm (kendi koşumum, gerçek katalog · `schema` fikstürü)

```
küp 23 · toplam ölçü 136 · sözlükteki ayrık terim 816
```

| iddia | ölçüm | yargı |
|---|---|---|
| *«aynı kavram **üç adla**»* | **135 / 136** ölçünün 3+ adı var | ⊘ **ÇÜRÜDÜ — ve tersi doğru** |
| *«**dokuz** ölçü sahipsiz»* | çok-sahipli terim **73 / 816** (%8,9) | ⚠ **sayı yanlış**, olgu gerçek |
| *«**on dokuz** ölçü yönsüz»* | yön beyansız **68 / 136** (%50) | 🔴 **çok daha ağır** |

### A.1 🔴 *«Üç adla»* bir çürüme DEĞİL, **tasarımın kendisi**

Ölçülen üç örnek:

```
bakim.ariza_sayisi        → adet · arıza adedi · arıza sayısı · breakdown count ·
                            failure count · fault count · kaç arıza        (8 ad)
bakim.toplam_durus_dakika → arıza duruşu · arıza kaybı · arıza süresi · downtime ·
                            stoppage · kayıp süre                          (8 ad)
bakim.ort_durus_dakika    → mttr · mean time to repair · ortalama onarım …  (8 ad)
```

Bunlar **eşanlamdır** ve zenginlikleri kasıtlıdır: Türkçe + İngilizce + kısaltma +
sektör argosu. *«Üç adla»* ölçütü uygulanınca **136 ölçünün 135'i** kırmızı görünüyor —
yani ölçüt hiçbir şeyi ayırt etmiyor.

> 🆊 *Her şeyi işaretleyen bir ölçüt, hiçbir şeyi işaretlemez.*

⊘ **KARAR: bu iddia kapatıldı.** Çürüme ölçütü *«bir ölçünün kaç adı var»* değil,
*«bir ADIN kaç sahibi var»* olmalıdır — aşağıdaki A.2.

### A.2 ⚠ Asıl sinyal: **çok sahipli terim 73** *(ajan «dokuz» demişti)*

En ağır beşi ölçüldü:

```
adet                → bakim · cari · kalite · oee · parti · ticaret     (6 sahip)
tep                 → enerji_makine · enerji_tesis · surdurulebilirlik  (3 sahip)
enerji tep          → aynı üçü
ton eşdeğer petrol  → aynı üçü
tonne of oil equiv. → aynı üçü
```

⊙ **Ve bu, `§38 D4`'ün kapattığı kusurun kaynağıdır**: çok sahipli bir terim geldiğinde
sistem **bir tanımı seçip beyan ediyor** ve öteki tanıma **tek tık** veriyor
(`suggestions[{kind:"tanim"}]`, ön uçta ayrı şerit — bu oturumda kapandı). Yani mekanizma
**var**; eksik olan, sahipliğin **kataloğa yazılması** (her tur yeniden çıkarım yapmak
yerine).

### A.3 🔴 En ağır bulgu: **yön beyansız 68/136 (%50)** — ve belirsizlik KODDA YAZILI

`app/kok_neden.py:400 _yon_beyanli` bunu kendi docstring'inde **ölçmüş**:

> *«Şema **yalnız** `lower_is_better` listesini taşıyor; bir `higher_is_better` listesi
> **yok**. Yani «listede değil» iki farklı şey demek olabilir: «yüksek iyidir» ya da
> «yönü yoktur» (adet gibi nötr bir sayı). `GG8` gereği ikisi **ayrılmaz sayılır**:
> beyan yoksa yön **bilinmiyordur**.»*
>
> *Bir listede olmamak, karşıt listede olmak değildir.*

✅ **Davranış doğru ve fail-safe**: yön bilinmiyorsa `ayristir` bir *«kötü yön»*
varsaymıyor, yalnız **en çok açıklayanı** seçiyor ve anlatı bunu **yargı olarak
sunmuyor**. Yani **sessiz-yanlış YOK**.

🔴 **Ama bedeli ölçülmedi:** 136 ölçünün **68'inde** *«arttı, iyi mi kötü mü»* sorusu
cevapsız kalıyor ve kullanıcı bunu **fark etmiyor** — çünkü eksiklik **sessiz**.
`§E2`'nin dersi burada birebir geçerli: **hesaplayamadığını söylemek de bir ölçümdür.**

### A.4 ⏭ KARAR — *(bir sonraki turda uygulanacak)*

1. 🟢 **Ucuz ve risksiz:** yön beyansız ölçüde anlatı **söylesin** (`§E2`/`§E3` kalıbı:
   *«bu ölçüde yönün iyi/kötü olduğu katalogda beyan edilmemiş»*). Uydurma yok, yeni
   liste yok — yalnız **var olan bilgisizliğin beyanı**.
2. 🟢 **Kapı:** yön beyansız oran **bugünkü %50'nin üstüne çıkarsa kırmızı** — yani
   katalog büyürken borç **sessizce** büyümesin.
3. ⏸ **`higher_is_better` listesi eklemek** ayrı bir karar: `ADR-0008` açısından meşru
   (kapalı liste), ama **136 ölçü elle etiketlenecek** demek — ve bu tam da kullanıcının
   *«elle küratörlemeyi bırak»* dediği iş. → **A.5'in kuyruğuna** girer.

### A.5 ✅ *«Kullanımdan hasat»* — **HAT ZATEN KURULU; ÇEVİREN YOK**

Kullanıcının önerdiği yer değişikliği — *eşleme çevrimdışı üretilir → **aday kuyruğu** →
**insan onaylar** → sonra deterministik ve bedava* — **zaten mimarinin kendisi**. Ölçüldü:

| parça | kod | durum |
|---|---|---|
| **madenci** (LLM taslak üretir) | `app/sinonim_onerici.py::oner` · `ciplak_cube_icin` | ✅ **yazılı** |
| **aday kuyruğu** | `kuyruga_koy` → `SynonymOverride(approved=False)` | ✅ **yazılı** |
| **insan onayı** | `admin_app/routers/synonyms.py:98` | ✅ **bağlı** |
| **tüketim** | `compose` **yalnız `approved=True`** okur (`ADR-0018 1e`) | ✅ **kapılı** |
| **`E-8` koruması** | *«yalnız çağrıldığında çalışır — hiçbir `/ask` yolundan tetiklenmez»* | ✅ **tasarım** |

⊙ Ve koruma **parametre değil sabit**: `V1-MIMARI-HARITASI.md:2345` — *«`approved=False`
**SABİT** (parametre değil!)»*. Yani bir LLM çıktısı **insan onaylamadan hiçbir sorguyu
etkileyemez** ve bu bir yapılandırma değil bir **yapı**.

🔴 **AMA: madencinin ÇAĞIRANI YOK.** Tüm repo tarandı — `sinonim_onerici` yalnız
**testlerde ve belgelerde** geçiyor, hiçbir uçtan/işten/CLI'dan **tetiklenmiyor**.
`belgeler/denetim/2026-08-05_V1-SON-KONTROL.md:212` bunu **yetim modül** listesinde
*«meşru — tasarım: offline»* diye sınıflandırmış.

> ⚠ **Sınıflandırma doğru, sonuç eksik.** *«Offline»* bir **çalışma kipidir**, bir
> **çalışmama gerekçesi değil**. Hat kurulu ve kapılı; eksik olan tek şey **kolu çeviren**:
> bugün sözlük kullanımdan **hiç** büyümüyor, çünkü hasat **hiç koşmuyor**.
>
> 🆌 *Bir motoru doğru kurmak onu çalıştırmaz; gerekçeli bir yetimlik, çalıştırılmamış bir
> motoru «tasarım» diye kaydeder.*

### A.6 ⏭ KARAR — `A` için yapılacaklar

| # | iş | risk | gerekçe |
|---|---|---|---|
| 1 ✅ | **Yön beyansızlığını anlatıda söyle** (68/136) — *yapıldı, mutasyonlu* | 🟢 yok | uydurma yok, yeni liste yok — *var olan bilgisizliğin beyanı* |
| 2 ✅ | **Kapı:** yön beyansız oran **%50'yi geçerse kırmızı** — *`test_a_yon_beyani.py` (4)* | 🟢 yok | katalog büyürken borç **sessizce** büyümesin |
| 3 | **Madencinin kolunu çevir**: `lab/` altında bir **çevrimdışı koşucu** (route-edilemeyen soruları `interaction_log`'dan al → `oner` → `kuyruga_koy`) | 🟡 orta | hat kurulu; eklenen tek şey **tetik**. `E-8` **korunur** (sıcak yol değil) |
| 4 | **Kapı:** `sinonim_onerici`'nin **bir çağıranı olmalı** — yoksa kırmızı | 🟢 yok | *bir motoru kurmak onu çalıştırmaz* |
| ⏸ | `higher_is_better` listesi | — | **136 ölçüyü elle etiketlemek** = tam da bırakılması istenen iş → **3 numaranın kuyruğuna** |

---

## B · ROUTE'UN ÇÜRÜTÜLEBİLİRLİĞİ — **KURAL VAR, UYGULANIYOR, VE ÖLÇÜLDÜ**

### B.1 ✅ *«Bir token birden çok sahibe işaret ediyorsa route çekilir»* — **uygulanıyor**

Ölçüldü (gerçek katalog, `route(_norm(q), schema)`):

| soru | `measure_cube_candidates` | `route()` |
|---|---|---|
| *«bu yıl adet»* | **5+ sahip** (`bakim·cari·kalite·oee·parti`) | **`None`** ✅ çekildi |
| *«bu yıl tep»* | **2 sahip** (`enerji_makine·enerji_tesis`) | **`None`** ✅ çekildi |
| *«bu yıl bakiye»* | **2 sahip** (`cari·mizan`) | **`None`** ✅ çekildi |
| *«bu yıl fire»* | 1 aday görünüyor ama ölçü **iki küpte** | **`None`** ✅ çekildi |

⊙ Yani kural **çürütülebilir** hâlde: çok sahipli bir terimde route **karar vermiyor**,
ve bu davranış **dört ayrı girdiyle** doğrulandı. `§A.2`'nin **73 çok-sahipli terimi** bu
mekanizmanın girdisi; `adet` (**6 küp**) en ağır vaka.

### B.2 🔴 Ama çözüm *«dur ve sor»* değil, *«cevapla ve beyan et»* — **ve bu bilinçli**

Ölçüldü: `_belirsizlik_beyani` `ask.py:3125`'te çağrılıyor — yani **`cq` oluştuktan
sonra**. Sıra şu:

```
route çekilir (None)  →  garson (Intent-JSON) bir tanım SEÇER  →  cevap üretilir
                      →  belirsizlik SONRADAN beyan edilir + öteki tanıma tek tık
```

Kartın *«CI'da chip ateşliyor, üretimde Intent-JSON gölgeliyor»* teşhisi **yarı doğru**:
Intent **gerçekten** seçiyor, ama beyan **kaybolmuyor** — `§38 D4` bu turda kapandı ve
chip artık ön uçta **ayrı şeritte** (*«başka tanım»*, ⇄, *«yeni bir sayı gelir»*).

⊙ Ve bu bir eksiklik değil **yazılı bir karar**: `§38.3 D13`'te Metabase'in
*«400 + `agent_error`»* deseni **üç ölçülmüş gerekçeyle reddedildi** — cevabı geri
çekmek *«kullanıcı asla cevapsız kalmaz»* ve *«dürüst red başarı değil»* kurallarıyla
**doğrudan çelişiyor**.

> 🆑 *Bir belirsizliği cevapsız bırakmakla, cevaplayıp beyan etmek aynı dürüstlük
> sınıfında değildir — ikincisi kullanıcıya bir sonraki adımı da verir.*

### B.3 ⚠ SEKTÖRÜN BIRAKTIĞI ŞEY ROUTE DEĞİLDİ — kayda geçti

MS Q&A ve Tableau Ask Data'nın kaldırdığı model *«kullanıcı dilbilimsel şemayı **elle**
beslesin»*di: eşanlam listeleri, ifade kalıpları, *«şunu şöyle de sorabilirim»* —
**anlama sorumluluğunu son kullanıcının bakımına yıkmak**. O gün **LLM yoktu**; kural
listesi tükenince **cevap da tükeniyordu**.

Bizde route bir **tek yol değil, bir hızlı yol**: tükendiği yerde **garson** devralıyor
(`§0.0` *«en ufak %5 şüphede garson gitsin»*). Ölçülü kazanç: küp **145–434 ms** ·
garson k=3 **98 sn** · Discovery **12,5 sn** · korpus **LLM'siz %94,9**.

> ⊙ *Bir hızlı yolu, onun yerine geçmeye çalışan bir modelin başarısızlığıyla yargılamak,
> çözdüğü sorunu görmeden onu kaldırmaktır.*

### B.4 ⏭ ÖLÇÜLMEMİŞ OLAN — bir sonraki turun işi

🔴 **Route kaç kez, hangi sebeple çekiliyor?** Bugün `route()` `None` dönüyor ama
**sebebi** kayda geçmiyor: *«çok sahipli terim»* mi, *«tanınmayan token»* mı, *«dönem
yok»* mu? Bu ayrım olmadan garsonun yükünün **ne kadarının** belirsizlikten geldiği
bilinemez — ve `§A.2`'nin 73 terimlik borcunun **ürün maliyeti** ölçülemez.
✅ **KAPANDI (08-12):** `Niyet.cekilme_sebebi` — kapalı küme (`cok_sahipli_terim` · `bilinmeyen_token` · `olcu_bulunamadi`), **alan değil TÜREV** (`referans`'ın gerekçesiyle aynı: *bir değeri iki yerden yazılabilir yapmak, iki değeri garanti etmektir*). Nesnenin **zaten taşıdığı** alanlardan okunuyor — yeni ölçüm/liste/eşik **yok**. Kapı `test_b_cekilme_sebebi.py` (7), mutasyonlu; en ince yüklem: ölçüt **küp kümesi**, aday sayısı **değil**.

⏭ **Kalan:** sebep **sayılmıyor** henüz — bir sayaç/telemetri bağlanmalı ki *«garsonun yükünün %kaçı belirsizlikten»* sorusu cevaplanabilsin.

### B.5 🔴 GARSON — *«hiç geliştirmedik»* İDDİASI **ÇÜRÜDÜ**; asıl boşluk **ölçüm**

Ölçüldü (2026-08-12, kendi koşumum):

| yatırım | ölçüm | durum |
|---|---|---|
| `select_cube` istemi (`llm.py:358`) | **161 satır** — küratörlü, kısıtlı | ✅ geliştirilmiş |
| **tool-calling** yolu (`_arac_ile`) | **var** — serbest metin değil **yapısal** çıktı | ✅ |
| few-shot (`few_shot_block`) | `app/` altında **11** referans; `§B2` ile garsona **bağlandı** | ✅ |
| istem zenginleştirme (`prompt_enhance`) | **24** referans | ✅ |
| öz-tutarlılık (`consistency_k=3`) | **15** referans | ✅ |
| çoğunluk oylaması (`oylama_cogunluk`) | **3** referans, bayraklı; *«belirsizlik atılmaz»* | ✅ |
| şema daraltma (`sema_daraltma: beta`) | `§38 D1` — 8 soruda **8/8** kapsandı, **0 kayıp** | ✅ |

⊘ Yani *«garsonu hiç geliştirmedik»* **ölçümle çürüdü** — bu, bu oturumda bir iddianın
**yedinci** kez ölçümle daralması.

🔴 **AMA ASIL BOŞLUK VAR VE DEPO ONU KENDİ YAZMIŞ** — `demo/packs/features.yml:222`:

> *«Geniş yayılım için ön koşul `A1` (garson korpusu): **kapı `route()`'u ölçer, garsonu
> ölçmez** — bu bayrağın gerilemesi kapıda **GÖRÜNMEZ**.»*

Yani garson **geliştirildi ama ölçülmüyor**: korpus (**%94,9**, LLM'siz) yalnız `route()`
yolunu sınıyor. Sonuç:

- bir garson iyileştirmesinin **kazandırdığı** ölçülemiyor,
- bir garson **gerilemesi** kapıda **görünmüyor**,
- ve `sema_daraltma` gibi bayraklar `beta`'da **kanıtla** tutuluyor, **sayıyla** değil.

> 🆕 *Ölçülmeyen bir bileşen geliştirilebilir ama iyileştirilemez: iyileştirme, iki
> ölçüm arasındaki farktır.*

### B.6 ⏭ `B` için kalan iki iş

| # | iş | risk | not |
|---|---|---|---|
| 1 ✅ | **Çekilme sebebini SAY** — *yapıldı: `sebep::<x>` kovası, **yalnız kesilen turda**; payda `ast` kapısıyla korunuyor, mutasyonlu* | 🟢 | `lab/nl_corpus.py`'nin `cats` kovasına ekle; **payda kutsal** (🅜) |
| 2 ✅ | **Garson korpusu (`A1`)** — *yapıldı: `lab/garson_korpusu.py`, **40 vaka** (tek sahipli ölçülerden), kuru mod varsayılan, sağlayıcı yoksa koşmaz, `E-8` ve payda kapılı; mutasyonlu* | 🟡 | deponun **kendi** ilan ettiği ön koşul; `sema_daraltma`/`few_shot` yayılımının şartı |

⚠ Sektör karşılaştırması (Snowflake Cortex Analyst · Databricks Genie · Wren AI) ancak
**②** kurulduktan sonra anlamlı olur: karşılaştırma bir **sayı** ister, bugün elimizde
garson için o sayı **yok**.

---

## C · WREN MOTORU — **ÜÇ METOT DEĞİL, DÖRT ALT SİSTEM KULLANILMIYOR**

### C.1 Hiç ölçülmemiş üçü — **ölçüldü, üçü de sıfır**

`ast` ile gerçek `Call` düğümü (`app` + `lab` + `tests`):

```
load_mdl          app 0 · lab 0 · tests 0
register_csv      app 0 · lab 0 · tests 0
register_parquet  app 0 · lab 0 · tests 0
transform_sql     app 0 · lab 0 · tests 7      (§F14'te ölçülmüştü)
```

⊙ Yani `§F14`'ün *«dört yetenek kullanılmıyor»* tablosu **eksikti**: kullanılmayan metot
sayısı **dört değil yedi** (`dry_run`·`pushdown_limit`·`list_tables`·
`get_available_functions` + bu üçü).

### C.2 🔴 **AI Context Layer'ın ADLARI PAKETTE YOK — ama DÖRT ALT SİSTEM VAR ve HİÇBİRİ KULLANILMIYOR**

Araştırmacının verdiği adlar (`instructions.md` · `queries.yml` · **LanceDB**) `wren`
paketinde **bulunamadı** (`rglob` → **0** isabet). ⚠ *Yabancı bir ad envanteri, yerel adı
yokluk sanar* (🅓). Gerçekte duran şey **başka adlarla** ve **daha fazlası**:

| alt paket | içerik (ölçüldü) | bizim **gerçek** import'umuz |
|---|---|---|
| `wren.memory` | **18 dosya** — `WrenMemory` · `embeddings.py` · `cli.py` | **0** |
| `wren.skills_content` | **13 dosya** — çoklu `SKILL.md` | **0** |
| `wren.ask_templates` | `direct.md.tmpl` · `guided.md.tmpl` | **0** |
| `wren.genbi` | **20 dosya** | **0** |

⚠ **İlk ölçümüm 7 isabet demişti ve YANILTICIYDI**: kelime araması `memory`/`genbi`
geçen kendi satırlarımızı sayıyordu. `ast` ile gerçek `ImportFrom`/`Import` arandığında
**0** çıktı. *Bir kullanımı metinle ölçmek, kendi kelimelerini kullanım sanmaktır.*

### C.3 ⏭ Bir sonraki turda ölçülecek — **karar bundan sonra**

`§F14`'ün dersi bağlayıcı: **yanlış gerekçeli bir ⊘, bir sonraki turda yeniden okunmaz.**
O yüzden karar **ölçümden sonra**:

1. **`wren.memory` ↔ bizim `vqr`** — ikisi de *«doğrulanmış soru → geri getirme»* yapıyor
   olabilir (㊷ *kartın yapılacağı yapılmış olabilir*). Örtüşüyorsa ⊘ **gerekçeli**;
   örtüşmüyorsa gerçek bir boşluk.
2. **`wren.skills_content` ↔ bizim `demo/skills/*.md`** — `§38.2 D9`'da ölçtük: üç metin
   **yazılı** ama `skills: "off"` (bağlı değil). Motorun kendi SKILL'leri **ayrı bir
   küme** mi, yoksa aynı iş mi?
3. **`rls.py` (380) · `dataset.py` (161) · manifest (~1.490)** — **satır satır değil,
   yetenek yetenek**: bu modüller motorun `transform_sql`/`register_*`/`load_mdl`
   işini mi yapıyor, ve **gerekçesi yazılı mı**?
4. **`motor_rls="shadow"`** — `rls.py:160` *«manifest dokunulmaz, gölge yalnız ÖLÇER»*.
   **Gölge bir şey yazıyor mu, nereye, okuyan var mı?** Kullanıcının teşhisi:
   *«karşılaştırma verisi zaten üretiliyor olabilir ve kimse ölçüsüne bakmamış.»*

> 🆘 *Bir yeteneği «kullanılmıyor» diye işaretlemek ucuzdur; onun işini başka bir yerde
> kendimizin yapıp yapmadığını ölçmek pahalıdır — ve karar ancak ikincisinden sonra
> verilebilir.*
