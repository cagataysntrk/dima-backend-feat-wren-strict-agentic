# DENETİM A–G — *faz denetiminden sonraki yedi kalem*

> **Disiplin aynı:** bulgu → **ölçüm** → karar → kapı. Hiçbir sayı ölçülmeden alınmaz;
> denetim ajanları bu oturumda **altı kez** yanıldı, kendi problarım **iki kez**.
>
> ⟳ Açıldı 2026-08-12. Faz denetimi (`DENETIM-FAZ-A-F.md`) **kapandı**, gerçek kalem 0.

| kalem | konu | durum |
|---|---|---|
| **A** | iş sözlüğü: elle değil **kullanımdan hasat** | 🟣 ölçüldü — *aşağıda* |
| **B** | route'un **çürütülebilirliği** + garson | ✅ **KAPANDI** — *aşağıda* |
| **C** | Wren motorunun **kullanılmayan** yetenekleri | ✅ **KAPANDI** — *aşağıda* |
| **D** | agentic önerileri **tek tek** | ✅ **KAPANDI** — *aşağıda* |
| **E** | cevap biçimi + UX önerileri **tek tek** | ✅ **KAPANDI** — *aşağıda* |
| **F** | LLM girdi token'ı / maliyet | ✅ **KAPANDI** — *aşağıda* |
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

### C.4 ÖLÇÜLDÜ — **dört sorunun dördü de cevaplandı, ve üçü iddiayı DARALTTI**

#### ① `wren.memory` ↔ bizim `vqr` — **ÖRTÜŞÜYOR**, ama motorun **iki fazlası** var

```
WrenMemory : describe_schema · get_context · index_manifest · recall_queries
             reset · schema_is_current · status · store_query
VQR (biz)  : few_shot_block · garson_ornekleri · near_exact · recall · remove · store
```

| motor | bizde karşılığı |
|---|---|
| `store_query` | `store` ✅ |
| `recall_queries` | `recall` · `near_exact` ✅ |
| `get_context` | `few_shot_block` · `garson_ornekleri` ✅ |
| **`index_manifest`** | ⊘ **yok** |
| **`schema_is_current`** | ⊘ **yok** |

⊘ **KARAR: ithalat GEREKSİZ** (㊷ *kartın yapılacağı yapılmış olabilir*) — üç çekirdek
yetenek **bizde var** ve **Türkçe morfolojiye bağlı** (`_tokens`/`_lex_score`), motorunki
değil. 🟢 **Ama iki fazlası bir BOŞLUK işaret ediyor**: *«şema değişti mi, bellek bayat
mı»* sorusu. Bu ayrı bir kaleme yazıldı — ithalat değil, **soru** alınıyor.

#### ② `wren.skills_content` ↔ `demo/skills/*.md` — **BAŞKA KÜME, başka iş**

```
motor : dlt-connector · enrich-context · genbi · generate-mdl · onboarding · usage
biz   : huni.md · kohort.md · yoy-orani.md
```

⊘ **KARAR: örtüşme YOK, eksiklik de yok.** Motorunkiler **semantik katmanı KURMA**
becerileri (bağlayıcı yazma, MDL üretme, onboarding); bizimkiler **analiz metodolojisi**
(huni, kohort, YoY oranı). Aynı ada sahip iki farklı şey — 🅒 *ödünç şema, tanımadığı
kategoriyi görünmez yapar*'ın tersi: **ödünç ad, farklı kategoriyi aynı sanmıştı**.

#### ③ 🔴 **EN AĞIR İDDİA ÇÜRÜDÜ: `rls.py` motorun işini TEKRARLAMIYOR**

`app/rls.py:1` — dosyanın **kendi başlığı**:

> *«FAZ 1.1 — **MOTOR-SEVİYESİ RLS.** `always_filter`'ın yerini **motor devralır**.»*

Ve gerekçesi **ölçülmüş iki baypasla** yazılı: ① **JOIN** (`compose.py:434`) —
*«filtreli bir modele join'lemek `always_filter`'ı BAYPAS EDER»* ② **Discovery ham SQL** —
`_inject_always_filter` yalnız `cube_sql()` yolundan çağrılıyor.

⊙ Yani `rls.py` motorun `transform_sql`'inin **rakibi değil**, motorun RLS'i **her model
referansına indirebilmesi için gereken GİRDİYİ** üretiyor. *«Yeniden yazılmış 380 satır»*
teşhisi **yanlış çerçeve**: bu satırlar motoru **kullanmak için** yazılmış.

> 🆚 *Bir modülün satır sayısı, onun neyin yerine geçtiğini söylemez; başlığı söyler.*

#### ④ `motor_rls="shadow"` — **YAZMIYOR, ve bu bir DÜZELTME**

`rls.py:160` tablo: `shadow` → manifest **dokunulmaz**, *«gölge yalnız ÖLÇER»*.
`:163` **açıkça**: *«`shadow` MANİFESTE YAZMAZ — ve bu bir DÜZELTMEDİR. İlk sürüm
`shadow`'da da yazıyordu.»* `:222`: *«`shadow`'da uygulama katmanı sahibi KALIR.»*

⚠ Kullanıcının hipotezi (*«karşılaştırma verisi zaten üretiliyor olabilir»*) **kısmen**
doğrulandı: `:191` bir **gölge denetimi**nden söz ediyor (*«`shadow`'da yalnız kıyas
için»*). 🔴 **Ama kıyasın ÇIKTISININ nereye gittiği ve okuyanı olup olmadığı bu turda
ölçülemedi** — bir sonraki turun ilk işi.

### C.5 ⏭ `C` için kalan — ve şimdiden görünen iki iş

| # | iş | risk |
|---|---|---|
| 1 | **Gölge kıyasının çıktısı**: nereye yazılıyor, okuyanı var mı — **ölç** | 🟢 ölçüm |
| 2 | **`schema_is_current` boşluğu**: bellek bayatlığı bizde kapılı mı? (`vqr` şema-sürüm kapısı olduğu **yazılı**, **ölçülmedi**) | 🟢 ölçüm |
| ⊘ | `wren.memory` · `skills_content` ithalatı | **reddedildi, gerekçesi yukarıda** |
| ⏭ | `dataset.py` (161) ↔ `register_csv/parquet` · manifest (~1.490) ↔ `load_mdl` — **aynı çerçeve hatasına düşmemek için** başlıklarından oku | 🟢 ölçüm |

### C.6 ✅ `C` KAPANDI — son üç ölçüm

#### ① Gölge kıyasının çıktısı — **VAR ve LOGLANIYOR**; kullanıcının hipotezi **doğrulandı**

`rls.rlac_manifesti` → `(manifest, sayı)` döndürüyor ve **kademe kararı vermiyor**
(*«bir dönüşümün kendi anahtarını okuması, aynı kuralın iki sahibini doğurur»* — `KAT-1`).
Çıktının gittiği yer **ölçüldü**: `compose.py:808` → `_log.warning("çekirdek katman
(shadow) — %s", mesaj)`.

⊙ Ve `compose.py:773` bu turda ölçtüğüm dersi **kendi diliyle** yazmış:

> *«`shadow`'un yazmaması bilinçli: **yazan bir gölge, gölge değildir** — FAZ 1.1'de
> ölçülen kusurun aynısı (`motor_rls` gölgesi manifeste RLAC yazıyordu).»*

✅ **Kullanıcının teşhisi doğruydu**: karşılaştırma verisi **gerçekten üretiliyor**.
⚠ Ama *«kimse ölçüsüne bakmamış»* kısmı da doğru: çıktı bir **`warning` satırı**, bir
**sayaç değil** — yani *«gölge kaç kez ayrıştı»* sorusu bir log taramasıyla cevaplanır,
bir metrikle değil. → **`§F` kuyruğuna** yazıldı (telemetri kalemi).

#### ② ⟳🔴 `vqr`'ın *«şema-sürüm kapısı»* — **BENİM BULGUM YANLIŞTI, kapı VAR**

`app/vqr.py`'de `schema_version` · `surum` · `version` → **0 isabet**. Yani `wren.memory`
karşılaştırmasında bulduğum boşluk (`schema_is_current`) **gerçek**: şema değiştiğinde
belleğin bayatlayıp bayatlamadığı **bilinmiyor**.

⟳ **DÜZELTME (aynı oturum, `§D`'nin ilk işi): İDDİA DOĞRUYMUŞ, ÖLÇÜMÜM YANLIŞTI.**

`app/vqr.py`'de `schema_version|surum|version` aramak **yanlış ad, yanlış dosyaydı**.
Gerçek ad **`mdl_version`** (repo genelinde **26** referans) ve kapı `vqr`'da değil
**sözleşme kimliğinde**:

> `app/contracts.py:145` — *«`mdl_version`, `company`, `tenant_id` **kimliğe GİRER**:
> şema değişince aynı `cube_query` **başka bir kimlik** üretir.»*
> (`:169` `payload = {"cq": cq, "mdl": mdl_version, "company": …, "tenant": …}`)

✅ Yani bayatlık **yapısal olarak** kapalı: şema sürümü değişince hash değişir, eski kayıt
**eşleşmez**. `wren.memory`'nin `schema_is_current`'ının karşılığı **bizde var** — başka
bir yerde ve **daha güçlü** (kimliğin parçası, bir kontrol değil).

> 🅣 *Bir kapının yokluğunu iddia etmek, aradığın YERİN kapsamıyla sınırlıdır* — ve bu
> oturumda **yedinci** kez kendi probum yanılttı. ㉙ **KOD ADIYLA ARA**: `version` diye
> aradım, alanın adı `mdl_version`'dı.

#### ③ `dataset.py` ↔ `register_csv` — **AYNI ÇERÇEVE HATASI, aynı cevap**

`app/dataset.py:1` **kendi başlığı**:

> *«Yüklenen Excel/CSV → oturum-scoped DuckDB + **oto-MDL/cube**… Böylece yüklenen veri
> **MEVCUT cube/NL pipeline'ından geçer** (route + yorum + KPI bedava).»*

⊘ **Motorun `register_csv`'sinin işi değil**: o bir dosyayı motor oturumuna **kaydeder**;
`dataset.py` ise ondan bir **cube** üretir ki `route()`·`interpret`·KPI **bedava** çalışsın.
Bir dosyayı tanıtmak ile onu **semantik katmana** sokmak aynı iş değildir (㊹ *motor ≠ veri*).

### C.7 `C` — KARAR TABLOSU

| yetenek | karar | gerekçe |
|---|---|---|
| `dry_run` · `pushdown_limit` · `list_tables` · `transform_sql` · `load_mdl` · `register_csv` · `register_parquet` | ⊘ **açılmıyor** | `dry_plan` **25 çağrı** her sorguyu koşmadan doğruluyor; ötekiler için **ölçülmüş bir kusur yok** (`§F14`) |
| `get_available_functions` | 🟢 **tek açılabilir** | desteklenen fonksiyon kümesi bugün bir **varsayım**; `§B12` aynı sınıfın ölçümle çürüdüğünü gösterdi |
| `wren.memory` | ⊘ **ithal edilmez** | `vqr` ile örtüşüyor **ve Türkçe morfolojiye bağlı**; ithalat o bağı koparırdı |
| `wren.skills_content` | ⊘ **konu dışı** | semantik katmanı **kurma** becerileri ↔ bizimki **analiz metodolojisi** |
| `wren.ask_templates` · `wren.genbi` | ⊘ **konu dışı** | grafik kararı **deterministik** (`ADR-0024`); şablon/GenBI ithalatı o kararı LLM'e devrederdi |
| `rls.py` · `dataset.py` · manifest | ⊘ **tekrar DEĞİL** | üçü de motora **girdi** üretiyor; başlıkları bunu yazıyor |
| gölge kıyası | 🟢 **sayaç eksik** | log var, metrik yok → `§F` |
| `vqr` şema-sürüm | ✅ **VAR** — `contracts.cube_query_hash`'te `mdl_version` **kimliğin parçası** | ⟳ benim ölçümüm yanlıştı |

> 🆛 *Bir motoru «az kullanıyoruz» diye suçlamadan önce, onun hangi işini bizim
> yaptığımızı değil, bizim hangi işimizi onun yapamayacağını sormak gerekir.*

---

## D · AGENTIC — **ÜÇ KALEM ZATEN KAPALI, BİRİ BU OTURUMDA KAPANDI**

### D.1 ✅ Plan onarım döngüsü — *«yalnız tekrar dene»* **DEĞİL**, **11 sınıf başına çare**

Rapor: *«`/stats/plan`: denendi 16 · onarıldı 1 · düştü 3 → **%25**»* ve endişe: onarım
gerçekten bir **çare** mi taşıyor, yoksa modele *«tekrar dene»* mi diyor?

**Ölçüldü:** `plan_garson.ONARIM_YONERGESI` → **11 sınıf**, her biri **eyleme dönüşebilir**
bir talimat:

```
ad_yok · bilinmeyen_fiil · boyut_yok · cozulmemis_referans · eksik_alan
fazla_alan · ileri_referans · json · olcu_yok · tavan · ulasilmaz
```

Örnek (`cozulmemis_referans`): *«Bir adım referansı bir alanın **TAMAMI** olmalıdır
(`"cube_query": "$1"`); süzgeç değerinin içine yazılamaz. Önceki adımın seçtiği varlığı
süzgeç yapmak için `BAGLA` çıktısını sonraki adımın `hedef` alanında kullan.»*

⊘ **KARAR: kalem kapalı.** Bu bir *«tekrar dene»* değil, **kusur sınıfını adlandırıp
düzeltmesini gösteren** bir yönerge. ⚠ **%25'lik onarım tutma oranı bir SONUÇ, bir kusur
değil**: paydası **16** ve `§F14`'ün dersi geçerli — bir oranı iyileştirmeden önce
**neyin ölçüldüğünü** bilmek gerekir.

### D.2 ✅ Ajan bütçe görünürlüğü — **bu oturumda kapandı**

🅩 *Harcadığını göremeyen ajan tutumlu olmayı seçemez.*

**Ölçüldü:** `Planlayici.kalan()` **var** ve `mcp.py:203` onu `_meta.kalan` olarak
**taşıyor**. Kodun kendi notu (`:194-198`, ⟳ 08-12): *«`Planlayici.kalan()` **zaten
hesaplıyordu, hiçbir yere** [gitmiyordu]»* — yani klasik *«yazılmış ama bağlanmamış»*, ve
bu oturumda `§38.3 D13` çalışmasıyla **bağlandı**.

⊘ **KARAR: kapalı.** ⏭ Kalan tek soru: ajan `_meta`'yı **okuyor** mu — bu bir **istem**
tasarımı sorusu ve `B.5`'in **garson korpusu** ölçüm tabanı kurulmadan cevaplanamaz.

### D.3 ✅ Çok adımlı plan — tavanlar **kurulu ve kapılı**

`§C2`'de ölçülmüştü ve bu oturumda **doğrulandı**: `Butce(adim=8 · saniye=30,0 ·
sorgu=12)` · `AZAMI_ADIM=12` (`dogrula`'da, **koşmadan önce**) · `ONARIM_TAVANI=2`
(Magentic-One *«stall ≤2»*) · tavan dolunca **`ButceAsimi` fırlıyor**. Kapı
`test_c2_butce_stall.py` (**8**).

⊘ **KARAR: kapalı.** ⚠ `app/butce.py` bir **sınıf değil bir koşucu** (`kos` · `ASIM`) —
㉙ *kod adıyla ara*: `Butce` adı `planner`'da yaşıyor.

### D.4 ✅ MCP dış yüzey — **29 araç**, ve `servis:llm` **bilinçli açık değil**

Bu oturumda kapandı (`§38.3 D13`): yayımlanan liste ucun **gerçekten sağladığı** kaynak
kümesinden **türetiliyor**; `llm.*` üçü **süzüldü** (32 → **29**), çünkü çağrılamıyorlardı.

⊘ **KARAR: kapalı — ve `servis:llm` bilerek dışarıda.** Dış bir çağıranın **LLM bütçesi
harcaması** ayrı bir **yönetişim** kararıdır; ilan edilmeden verilemez. Verildiği gün
`_KAYNAK_ADLARI`'na bir ad eklenir, **başka hiçbir satır değişmez**.

### D.5 ⏭ `D`'den çıkan tek yeni iş

🔴 **Ajanın `_meta`'yı gerçekten okuyup okumadığı ölçülmedi.** `kalan` taşınıyor ama
*«ajan onu görünce davranışını değiştiriyor mu»* sorusu bir **davranış** ölçümüdür ve
`B.6/②`'nin garson korpusu **canlı** koşulmadan cevaplanamaz. → `B` kuyruğuna **bağlandı**,
`D`'de ayrı bir borç açılmadı (㊲ *aynı işin iki satırı*).

---

## E · CEVAP BİÇİMİ + UX — **E.1 KAPANDI**

### E.1 ⊘ `viz.recommend` niyet kancası — **AÇILMAZ, çünkü daraltmalar ZATEN yürürlükte**

Raporun (`§14.11 D7`) `@antv/ava` ithalatını reddederken bıraktığı **tek 🟢 delta**:
*«`viz.recommend` imzası niyeti hiç almıyor… kanca yalnız daraltıcı yönde açılır»*.

**İmza ölçümü doğru** — `(result, units, lower_set, cube_query, non_additive, hedefler,
paket)`, niyet yok. **Ama önerilen iki daraltmanın ikisi de zaten var**, ve bir
**etiketten** değil **yapıdan** türetilerek:

| raporun istediği | bugünkü hâli | nereden |
|---|---|---|
| `TUR_KIYAS` → `partition` kapansın | ✅ **kapalı** | `viz.py:497` pay grafiği `len(measures)==1` ister; kıyas ailesi (`_gecen`·`_degisim_yuzde`) **her zaman** çok ölçülü |
| `TUR_TREND` → tabloya daraltma yasak | ✅ **yasak** | `viz.py:220` `time_col and measures≥1` → **`line`**; `table` için ya **ölçü 0** ya **boyut >2** gerek |

⊘ **KARAR: kanca açılmaz.** `niyet=` eklemek, yapının söylediğine **ikinci bir sahip**
vermek olurdu (`KAT-1`) — ve iki sahip bir gün ayrışır: kullanıcı *«trend»* der ama
sonuçta zaman sütunu **yoktur**; o an etiket `line`, yapı `table` der. `ADR-0024`
determinizmi kararı **veriye** bağladığı için çalışıyor.

✅ **Yapılan iş, kararı DEĞİŞMEZ yapmaktı:** `test_e1_grafik_niyeti_yapidan.py` (**5**,
🅑 mutasyonla kanıtlı — tek-ölçü şartı kaldırılınca kapı kırmızı). Raporun beyanı artık
bir cümle değil bir **yüklem**.

⊙ **Yan ölçüm — raporun *«6 tür zaten bağlı»* iddiası DOĞRU:** üretici zincir
`niyet.coz(soru, schema).turler` → `bicim.oneri_kotasi` (`answer.py:872`) **koşuyor**.
⚠ ㊺ **Aynı adlı iki ölçüt:** `followup`'ın `niyet.tur`'u (konuşma sınıfı) ile
`app/niyet.py`'nin 6 türü (sorgu şekli) **ayrı** kavramlar — karıştırılmadı.

⊙ **E.3 önden kapandı:** `narration_guard` uydurma-sayı **oranı** ölçülüyor —
`makbuza()` hem `rejected_sentences` hem **`total_sentences`** (payda) basıyor
(`narration_guard.py:171-186`). Planın `B3` kalemi (*«ölçülmemiş olan oran»*) **kapalı**.
🅜 payda kutsal — ve burada **var**.

### E.2 ⊘ Chip'lerin üç edim ayrımı — **DÖRT ŞERİT VAR, ve ayrım ŞEMADA**

Soru: *«`suggest_next_steps` chip'leri FE'de üç edim olarak ayrışıyor mu, yoksa hepsi
aynı şerit mi?»* **Ölçüldü — ayrışıyor, hem de dört şeritte** (`ReportCard.tsx`):

| şerit | satır | edim |
|---|---|---|
| **devam sorusu** (`suggestions`) | `:1120` | *«bu cevabın **üstünde** konuşur — yeni sorgu yazılmaz»* |
| **belirsizlik** (`kind="tanim"`) | `:1151` | aynı soruyu **başka bir tanımla** yeniden sorar |
| **türetme** (`kind="turetme"`) | `:1160` | `KÖK-7d` |
| **sonraki adım** (`next_steps` → `NextStepChips`) | `:1211` | **sorguyu düzenler** — `cube_query` taşır |

🔴 **Ve ayrım bir yorum satırı değil, bir ŞEMA:** `NextStep` **`cube_query` alanını
ZORUNLU** taşır (`schemas.py:295`), `Suggestion` ise **hiç taşımaz** (`:268`). Yani
*«bu chip yeni sorgu yazar mı»* sorusunun cevabı **tipten** okunuyor; bir gün ikisi
karışsa Pydantic **sınırda** durdurur.

⊙ Kodun kendi notu (`schemas.py:272`) bunun **ölçülmüş** bir kusurdan doğduğunu
söylüyor: `kind` alanı *«**üçüncü bir edim doğduğu için**»* eklendi (`KÖK-9`), çünkü
belirsizlik chip'i *«yeni sorgu yazılmaz»* açıklamasıyla basılırken **tam da yeni bir
sorgu yazıyordu**. 🆈 *Bir chip'in yanındaki açıklama, chip'in kendisi kadar bir vaattir.*

⊘ **KARAR: yeni iş yok.** Kapılar **zaten var**: `test_chipler.py` · `test_next_steps.py`.

### E.4 ⊘ `ReportCard` makbuz katmanlaması — **ÜÇ KATMAN, bayraklı, ayrıntı SİLİNMİYOR**

`§D3`'ün istediği *«tek satır + katlanır ayrıntı»* **kurulu**: `ReportCard.tsx:763`
**KATMANLI MAKBUZ**, bayrak `useFeature("ui_kanit_gorunurlugu")` (`:128`), `contract_id`
**katman 3**'te (`:1240`).

Bayrağın **bugünkü hâli ölçüldü** — `features.yml:541` **`beta`** (kapalı değil), ve
kararın gerekçesi bayrağın yanında yazılı:

> *«Ölçüldü: cevap kartında `<details>` **SIFIRDI** — `D3` **yanlış kapatılmıştı**.
> Varsayılan KISA (Steyvers 2025: uzun açıklama doğruluğu artırmadan **güveni** artırır).
> **Ayrıntı SİLİNMEZ, katlanır.** KAPALIYKEN eski üç-yüzeyli davranış birebir (`KURAL B`).»*

⊘ **KARAR: yeni iş yok** — ve dikkat: bu kart bir kez *«yanlış kapatılmış»*, sonra
**ölçümle** yeniden açılmış. ㊷'nin tersi de doğru: *bir kartın «yapıldı» işareti,
yapılmadığının da kaydı olabilir.* Kapı **zaten var**: `test_kanit_gorunurlugu.py`.

### ✅ `E` KAPANDI — dörtte dördü ölçüldü

| kalem | karar | kapı |
|---|---|---|
| **E.1** grafik niyet kancası | ⊘ **açılmaz** (daraltmalar yapıdan) | `test_e1_grafik_niyeti_yapidan.py` (**5**, bu turda yazıldı) |
| **E.2** chip üç edim ayrımı | ⊘ **var** — ayrım **şemada** | `test_chipler.py` · `test_next_steps.py` |
| **E.3** anlatı guard oranı | ⊘ **ölçülüyor** — payda dahil | `narration_guard.makbuza()` |
| **E.4** makbuz katmanlaması | ⊘ **var** — `beta`, ayrıntı katlanır | `test_kanit_gorunurlugu.py` |

⊙ Üç mevcut kapı birlikte koşuldu: **33 yeşil** (6,2 sn).
🔴 **`E`'nin dersi:** dört kalemin **üçü zaten yapılmıştı** ve rapor bunu bilmiyordu.
㊷ bu oturumda **onuncu** kez doğrulandı — *bir denetim kartının asıl işi, işi yapmak
değil, yapılıp yapılmadığını ÖLÇMEKTİR.*

---

## F · LLM GİRDİ TOKEN'I / MALİYET — **KAPANDI**

### F.1 ⊘ İstem boyutu — **kırpma VAR, bayrağı `beta`**

Soru: katalog metni isteme **tam mı** gidiyor? **Hayır — daraltılıyor.**
`katalog_metni.py:353` → `_dar = "sema_daraltma" in _bayraklar`; bayrak
`features.yml:224` **`beta`**. Kapalıyken `soru` **yok sayılır** ve metin tam gider
(`KURAL B`). ⊘ **Yeni iş yok.**

### F.2 ⚠ Gölge sayacı — **loglanıyor, TOPLANMIYOR**

`compose.py:808-810`: `shadow` kademesi *«%d cube birleşecekti, YAZILMADI»* diye
**loglar** ve grain ihlallerini `warning`'e basar. Ama **kaç kez koştuğu / kaç kez
ayrıştığı** hiçbir yerde **toplanmıyor**. `C`'den devralınan kalem **doğrulandı**.

### F.3 ✅ Token telemetrisi — **VAR ve KALICI** (㊷ on birinci kez)

`llm.record_llm_usage(model, input_tokens, output_tokens, latency_ms)` (`llm.py:109`,
**5 çağrı**) → istek-kapsamlı `ContextVar` → `answer.py:258`
`InteractionLog.llm_input_tokens` · `llm_output_tokens` · `llm_model` · `llm_latency_ms`.
Sıfırlama `ask.py:2128` `reset_llm_usage()` — istek başına.

### 🔴 `F`'nin ASIL bulgusu — `F.2` ve `F.3` **aynı kusurun** iki hâli

**Ölçüldü:** `app/routers/` altında `input_tokens` arayan **hiçbir uç yok (0)**.

> Sayı **üretiliyor**, hiçbir yerden **okunamıyor**. 🆓 Adı: **toplama katmanı yok.**

⊘ **KARAR: uç AÇILMAZ, boşluk RAPORLANIR** — iki gerekçeyle:
① Bir `/stats/maliyet` ucu bugün yazılsa **ön uç tüketicisi olmayan** bir uç olurdu; yani
`§G`'nin **tam da kapatmak üzere olduğu** yetim-uç sınıfını **elimizle üretirdik**.
② Kullanıcının açık talimatı: *«riskliyse sadece raporlansın»*.

✅ **Yapılan iş — var olanı KİLİTLEMEK:** `test_f_maliyet_zinciri.py` (**5**,
🅑 mutasyonla kanıtlı — `llm_input_tokens` yazımdan düşünce kapı kırmızı).
Zincirin dört halkası (`llm_model`·`llm_input_tokens`·`llm_output_tokens`·
`llm_latency_ms`) `ast` ile denetleniyor; biri sessizce koparsa **hiçbir cevap
bozulmazdı**, yalnız **ne harcadığımız** kaybolurdu. 🅩
⊙ Beşinci yüklem **boşluğun kendisini** kapıya bağlıyor: bir gün maliyet ucu açılırsa
kapı kırmızı olur ve *«FE tüketicisi var mı»* sorusu **sorulmak zorunda** kalır.

### ⏭ `F`'den `G`'ye devreden

**Gölge sayacı** ve **maliyet toplaması** — ikisi de bir **okuma yüzeyi** ister ve o
yüzeyin meşruiyeti `§G`'nin yetim-uç kararına bağlı. `G` o kararı verdikten **sonra**
açılabilirler; önce açılırlarsa kuralı ihlal ederler.

---

## G · REPO DÜZENİ — **G.1 KAPANDI**

### G.1 ✅ YETİM UÇ KAPISI — *«geliştirdik, uç açtık, ön uç hiç çağırmadı»*

Kullanıcının `G` teşhisinin **ikinci yarısı**. `test_g_yetim_modul_kapisi.py` birinci
yarıyı kapatmıştı (modül yazılıp import edilmezse kırmızı); ama bir modül **import
edilip** bir uç açabilir ve o uç **hiç çağrılmayabilir** — modül kapısı bunu **göremez**.
🅣 *Bir kapının yokluğu, aradığın yerin kapsamıyla sınırlıdır.*

**Ölçüldü (`ast`, `@router.<fiil>`):**

```
app/routers/ altında HTTP ucu                         : 77  (19 dosya)
statik yolu ön uç kaynağında HİÇ geçmeyen             :  8
```

⚠ **İlk ölçütüm NAİFTİ ve düzelttim** (㊳ 🆊): yolun **son parçasını** aramıştım
(`/ask/{id}/cube` → `"cube"`) — tesadüfen eşleşiyor ve borcu **4** gibi düşük gösteriyordu.
Doğru ölçüt **statik önektir** (`/stats/plan`), ve o **8** diyor.

**Sekizi de meşru — ve ÜÇ ayrı sebeple** *(kapı bir «hepsi bağlansın» dayatması değil)*:

| sebep | uçlar |
|---|---|
| altyapı yoklaması | `/health` · `/health/ready` |
| **başka istemci** (ön uç değil, **ajan**) | `/mcp/tools` · `/mcp/call` |
| işletme aracı (`lab/` + curl) | `/stats/plan` · `/stats/gecikme` · `/stats/katalog` · `/dry-plan` |

✅ **Kapı:** `test_g_yetim_uc_kapisi.py` (**5**). 🅑 Mutasyonla kanıtlı — tüketicisiz bir
uç eklenince **iki** yüklem birden kırmızı (beyansız + tavan). Maliyet **4,7 sn**
(önbellekli; modül kapısının ilk yazımı önbeleksiz **2 dk+** sürmüştü, aynı hata
tekrarlanmadı).

🔴 **Ve kapı ilk koşumunda KENDİ YAZARINI yakaladı:** `/stats/katalog` için yazdığım
gerekçe *«aynı fonksiyon, tek sahipli»* diyordu — doğru, ama **çağıranı söylemiyordu**.
`test_HER_GEREKCE_CAGIRANI_SOYLUYOR` onu kırmızıya çevirdi ve gerekçe düzeltildi.
🆏 *Bir yetimliğin gerekçesi «neden bağlı değil»i değil, «bağlı olmadan nasıl
çalışıyor»u anlatmalıdır.*

⊙ **`F`'nin devrettiği karar burada kapandı:** maliyet/gölge sayacı için bir uç açılsaydı
bugün **dokuzuncu yetim uç** olurdu ve bu kapı onu **kırmızı** yapardı. `F`'nin ⊘ kararı
`G`'nin kapısıyla **tutarlı** çıktı 🆃.

### G.2 ✅ `MIMARI.md` ŞİŞKİNLİĞİ — **çare silmek değil, GEZİNMEK**

Kullanıcı: *«aşırı şişti o yüzden kullanılamıyor.»* **Ölçüldü:** `MIMARI.md` **5.652
satır · 262 başlık** (h2 **16** · h3 **123**) · `CLAUDE.md` **433 satır · 21 başlık**.

🆚 **Asıl sorun satır sayısı DEĞİL.** 5.652 satır bir mimari otorite için fazla değil;
**123 eşit görünen alt başlık** arasında aradığını bulamamak fazla. Ve silmek çare
olamazdı: `MIMARI.md §10` *«kapananlar işaretlenir, silinmez»* ve ㊿ *özeti korumak,
özetlediğini korumaz* — bir kararın gerekçesi kısaltılırsa altı ay sonra o karar
**yeniden tartışılır**.

✅ **Yapılan:** `lab/belge_dizini.py` — bölümleri **satır numarasıyla** ve alt başlık
sayısıyla listeleyen **üretilmiş** dizin (26 satır), `MIMARI.md`'nin başına işaretler
arasına işlendi. Okuyucu artık **16 bölüm** arasından seçiyor.
⚠ `CLAUDE.md` **bilerek dizinsiz**: 21 başlıkla zaten geziliyor, dizin orada **gürültü**
olurdu 🆊.

✅ **Kapı:** `test_g_belge_dizini_taze.py` (**4**, 🅑 belgeye bölüm eklenince kırmızı).
Dördüncü yüklem **silmeyi de** yasaklıyor: belge 5.652'nin altına düşerse kırmızı.

🔴 **Yazarken İKİ kez yanıldım, ikisi de koda yazıldı:**
① **Çapa:** `ı`→`i` çeviriyordum; GitHub `ı`'yı **korur** → ürettiğim bağlantılar
**hiçbir yere gitmezdi**. Görünür ama tıklanmaz bir dizin, dizinsizlikten kötüdür 🆈.
② ㉛ **Dizin kendini sayıyordu:** blok içindeki `## 🧭 DİZİN` başlığı bölüm sanılıyor,
her yazım satırları kaydırıyor, dizin **hiçbir zaman** *«taze»* olamıyordu — kendi
kuyruğunu kovalayan bir kapı. Onarım: blok **taranmıyor** + **sabit nokta** (≤5 geçiş,
oturmazsa **söylüyor**).

### G.3 ✅ *«TEK YETENEK KAYDI»* — `MIMARI.md §2.0`'a yazıldı

`§38 D6`'nın cümlesi `MIMARI.md`'de **0 eşleşmeydi**; artık `§2.0`'da (`#### 🔴 TEK
YETENEK KAYDI`). İçerik **rapordan** alındı ㉔: planlayıcının fiil kümesi `app/tools.py`
kaydından **türetilir**, eşleme **aracın kendi beyanına** (`Arac.fiil`) yazılır, doğrulama
**içe aktarma anında** koşar — ayrışırsa **uygulama ayağa kalkmaz**. **15/15** eşleşme,
**31** ilkel, kapı `test_d6_tek_yetenek_kaydi.py`.

⊙ Ve raporun **ölçülmüş dersi** de yazıldı: iddia ilk konduğunda *«tek kayıt»* doğru
**görünüyordu** (9/15 fiil kayıtlı bir aracı çağırıyordu), ama **6/15 fiilin gövdesi
kayıtta HİÇ YOKTU** — planlayıcı onları çağırabiliyor, envanter yetki sınıfını
**bilmiyordu**. *Bir kaydın tekliği, sayısıyla değil kapsamıyla ölçülür.*

---

# ✅ A–G KAPANIŞ KARNESİ

| harf | konu | karar | kapı |
|---|---|---|---|
| **A** | iş sözlüğü kullanımdan hasat | ✅ hat kuruluydu, **kolu takıldı** | `test_a_sozluk_hasadi.py` · `test_a_yon_beyani.py` |
| **B** | route çürütülebilirliği + garson | ✅ `cekilme_sebebi` **türetilmiş** · korpus **40 vaka** | `test_b_cekilme_sebebi.py` · `test_b_sebep_sayaci.py` · `test_b_garson_korpusu.py` |
| **C** | motorun kullanılmayan yetenekleri | ⊘ 7 metot + 4 alt sistem **gerekçeli**; *«2.000 satır»* iddiası **çürüdü** | `test_wren_bagimliligi_beyanli.py` |
| **D** | agentic öneriler | ⊘ üçü **zaten kapalıydı**, biri (`kalan`) **bu oturumda** bağlandı | `test_c2_butce_stall.py` |
| **E** | cevap biçimi + UX | ⊘ dördün **üçü** zaten yapılmıştı; kanca **açılmadı** | `test_e1_grafik_niyeti_yapidan.py` |
| **F** | LLM token / maliyet | ⚠ ölçülüyor ama **okunamıyor**; uç **açılmadı**, boşluk **adlandırıldı** | `test_f_maliyet_zinciri.py` |
| **G** | repo düzeni | ✅ **yetim uç kapısı** + belge dizini + `§2.0` cümlesi | `test_g_yetim_uc_kapisi.py` · `test_g_belge_dizini_taze.py` |

## Bu denetimin TEK cümlelik dersi

㊷ **on bir kez** doğrulandı: bir denetim kartının asıl işi **işi yapmak** değil,
**yapılıp yapılmadığını ölçmektir**. Yirmi iddia ölçüm altında daraldı — ve **on tanesi
benim kendi probum ya da kapımdı**. En pahalı hata, olmayan bir kusuru *«düzeltmek»*
olurdu.
### ⏭ `G`'de kalan

**G.2** `MIMARI.md` şişkinliği — ölçüldü: **5.652 satır · 262 başlık** (h2 **16** · h3
**123**); `CLAUDE.md` **433 satır · 21 başlık**. 🆚 *Satır sayısı değil başlık söyler*:
asıl sorun **123 h3**'ün tek düzlemde durması. ⚠ **Silme yok** — dizinleme/özetleme.
**G.3** `§38 D6`'nın *«tek yetenek kaydı»* cümlesi — `MIMARI.md`'de **0 eşleşme**,
`§2.0`'a yazılacak.
