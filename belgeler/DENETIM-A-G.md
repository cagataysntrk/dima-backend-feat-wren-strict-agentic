# DENETİM A–G — *faz denetiminden sonraki yedi kalem*

> **Disiplin aynı:** bulgu → **ölçüm** → karar → kapı. Hiçbir sayı ölçülmeden alınmaz;
> denetim ajanları bu oturumda **altı kez** yanıldı, kendi problarım **iki kez**.
>
> ⟳ Açıldı 2026-08-12. Faz denetimi (`DENETIM-FAZ-A-F.md`) **kapandı**, gerçek kalem 0.

| kalem | konu | durum |
|---|---|---|
| **A** | iş sözlüğü: elle değil **kullanımdan hasat** | 🟣 ölçüldü — *aşağıda* |
| **B** | route'un **çürütülebilirliği** + garson | 🔵 |
| **C** | Wren motorunun **kullanılmayan** yetenekleri | 🔵 |
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
| 1 | **Yön beyansızlığını anlatıda söyle** (68/136) | 🟢 yok | uydurma yok, yeni liste yok — *var olan bilgisizliğin beyanı* |
| 2 | **Kapı:** yön beyansız oran **%50'yi geçerse kırmızı** | 🟢 yok | katalog büyürken borç **sessizce** büyümesin |
| 3 | **Madencinin kolunu çevir**: `lab/` altında bir **çevrimdışı koşucu** (route-edilemeyen soruları `interaction_log`'dan al → `oner` → `kuyruga_koy`) | 🟡 orta | hat kurulu; eklenen tek şey **tetik**. `E-8` **korunur** (sıcak yol değil) |
| 4 | **Kapı:** `sinonim_onerici`'nin **bir çağıranı olmalı** — yoksa kırmızı | 🟢 yok | *bir motoru kurmak onu çalıştırmaz* |
| ⏸ | `higher_is_better` listesi | — | **136 ölçüyü elle etiketlemek** = tam da bırakılması istenen iş → **3 numaranın kuyruğuna** |

