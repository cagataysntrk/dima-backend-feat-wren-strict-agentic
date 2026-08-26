# BELGELER — indeks ve **yerleşim kuralı**

> Bu dosya bir içindekiler listesi değil; **nerenin neye ait olduğunun kuralı**.
> Yeni bir belge yazmadan önce buraya bak: *yeri belli olmayan bir belge, kökte
> birikir ve altı ay sonra kimse hangisinin güncel olduğunu bilmez.*

---

## 🔴 TEK KURAL

**Bir belgenin yeri, ne olduğuna değil — NE ZAMAN BAYATLADIĞINA göre belirlenir.**

| dizin | içindekiler ne zaman bayatlar | dolayısıyla |
|---|---|---|
| **kök** (`OPERASYON*`) | ⟳ **hiç** — sürekli güncellenir | operasyonun giriş noktası, taşınmaz |
| `kilavuz/` | ⟳ ürün değişince — **güncellenir** | *nasıl yapılır* — canlı belge |
| `mimari/` | ⟳ mimari kararla — **güncellenir** | *neden böyle* — canlı belge |
| `urun/` | ⟳ şartname değişince | ürün tanımı |
| `denetim/` | 🔒 **anında** — yazıldığı anın fotoğrafı | **tarih damgalı, DEĞİŞTİRİLMEZ** |
| `devir/` | 🔒 anında | oturum devri, tarihsel kayıt |
| `arsiv/` | 🔒 zaten bayat | kaldırılmış ama silinmemiş |

> ⚠ **`denetim/` ve `devir/` içindeki bir dosya güncellenmez** — yeni ölçüm **yeni
> tarihli yeni dosyadır**. *Bir denetim raporunu güncellemek, ölçümün ne zaman
> alındığını silmek demektir; ve tarihi olmayan bir ölçüm, kıyaslanamaz bir sayıdır.*

---

## Kök — **üçü ve yalnız üçü**

Operasyonun giriş noktası. `backend/CLAUDE.md` doğrudan bunlara işaret ediyor; bağlam
sıfırlansa bile operasyon buradan devam eder.

| dosya | ne |
|---|---|
| [`README.md`](../README.md) | 🔴 **depoya giriş** — *bu nedir · nasıl koşar · ilk gün okuma sırası*. ⚠ Bir **yön tabelasıdır**, referans değil: bilgiyi taşımaz, işaret eder |
| [`OPERASYON.md`](../OPERASYON.md) | kural seti · döngü adımları · test kapısı · öz-denetim |
| [`OPERASYON-DURUM.md`](../OPERASYON-DURUM.md) | **nerede kaldık** · açık borçlar · ölçüm tabanı |
| [`OPERASYON-DENETIM.md`](../OPERASYON-DENETIM.md) | denetim ajanlarının görev metinleri |

---

## `belgeler/` kökü — **DIŞARIYA VERİLEN, KAPIYLA CANLI TUTULAN**

🔴 Yukarıdaki tabloda **yeni bir bayatlama sınıfı**: ne *«hiç bayatlamaz»* ne *«anında
bayatlar»* — **bayatlaması bir kapıyla yasaklanmıştır**. Bir denetim raporu yazıldığı anın
fotoğrafıdır ve **değiştirilmez**; bu ise **yayımlanmış bir iddiadır** ve her zaman
**güncel** olmak zorundadır, çünkü dışarıdaki biri ona bakıp karar verir.

| dosya | ne | çürümemesini ne sağlıyor |
|---|---|---|
| [`DOGRULUK.md`](DOGRULUK.md) | 🔴 **yayımlanan doğruluk sayısı** — oran · payda tanımı · yöntem · **bilinen körlükler** · yeniden üretme komutu | `backend/tests/test_f8_dogruluk_yayini.py` her sayıyı `nl_corpus.json`'dan yeniden hesaplar; ölçüm değişip belge güncellenmezse **kapı kırmızı** |

> *Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan kötüdür — çünkü ona
> güvenilir.* İçindeki tarih ve sha bir **arşiv damgası değil**, o anki sayıyı üreten
> koşumun **künyesidir**.

---

## `kilavuz/` — *nasıl yapılır* (canlı)

| dosya | kime |
|---|---|
| [`SERVER_COMMANDS.md`](kilavuz/SERVER_COMMANDS.md) | sistemi **ayağa kaldıracak** herkese — **derle→değiştir** sırası, port **8002** (öngörü/geliştirme kabı `dima-oneri-8002`; ⚠ ayrıca **8001**'de ikinci bir kap koşuyor olabilir — `docker ps` ile bak), frontend **pnpm** |
| [`TEST-ORTAMI-KILAVUZU.md`](kilavuz/TEST-ORTAMI-KILAVUZU.md) | 🔴 **test koşacak/yazacak herkese** — süre kuralları, parçalar, kapılar |
| [`CANLI_TEST_REHBERI.md`](kilavuz/CANLI_TEST_REHBERI.md) | canlı LLM turu koşacaklara (kota kısıtı!) |
| [`KULLANIM-KILAVUZU-v1.md`](kilavuz/KULLANIM-KILAVUZU-v1.md) | son kullanıcı bakışı |

## `mimari/` — *neden böyle* (canlı)

⚠ **Mimari otorite `backend/MIMARI.md`'dir**; buradakiler onu tamamlar, çelişkide o kazanır.

| dosya | ne |
|---|---|
| [`V1-MIMARI-HARITASI.md`](mimari/V1-MIMARI-HARITASI.md) | v1'in uçtan uca haritası |
| [`Wren_Hibrit_GenBI_SaaS_Strateji.md`](mimari/Wren_Hibrit_GenBI_SaaS_Strateji.md) | hibrit GenBI stratejisi |

## `urun/` — şartname

| dosya | ne |
|---|---|
| [`Dima-0-100-Gorev-Takip.md`](urun/Dima-0-100-Gorev-Takip.md) | ürün şartnamesi — ⚠ **mimari otorite değildir** |

## `plan/` — **yürürlükteki ve kapanmış operasyonların planı** (canlı)

Bir *operasyon* tek plana bağlı bir çalışma dönemidir; her operasyonun bir **durum**
dosyası vardır ve bağlam sıfırlansa bile iş oradan devam eder.

| dosya | ne |
|---|---|
| [`2026-08-12_ONGORU-KATMANI-KARARI.md`](plan/2026-08-12_ONGORU-KATMANI-KARARI.md) | 🔴 **öngörü katmanı planı** — *route ve garson TAHMİNCİ oluyor, kararı kullanıcı verir* |
| [`ONGORU-DURUM.md`](plan/ONGORU-DURUM.md) | 🔴 **nerede kaldık** (en son çalışılan operasyon) |
| [`DIMA-V1-YOL-HARITASI.md`](plan/DIMA-V1-YOL-HARITASI.md) · [`DIMA-GARSON-ARA-FAZ.md`](plan/DIMA-GARSON-ARA-FAZ.md) | ⟳ kapanmış operasyonlar — *işaretlenir, silinmez* |
| [`2026-08-09_ORKESTRATOR-KATMANI-VE-OLCEKLENME.md`](plan/2026-08-09_ORKESTRATOR-KATMANI-VE-OLCEKLENME.md) · [`2026-08-13_ONGORU-KATMANI-DURUM-VE-SARTNAME.md`](plan/2026-08-13_ONGORU-KATMANI-DURUM-VE-SARTNAME.md) | tarih damgalı plan belgeleri |
| [`2026-08-26_PLAYWRIGHT-BULGULARI-YOL-HARITASI.md`](plan/2026-08-26_PLAYWRIGHT-BULGULARI-YOL-HARITASI.md) | 🔴 **canlı test kampanyasının düzeltme rehberi** — sorun→kanıt→çözüm→doğrulama, 4 faz, K1-K13 |

⚠ **Kök `OPERASYON-DURUM.md` ile karıştırma:** o **önceki** operasyonun durumudur. En son
durum **`plan/ONGORU-DURUM.md`**'dedir; ikisini birden *«nerede kaldık»* diye okumak,
`KAT-1`'in belge düzeyindeki ihlalidir.

## `arastirma/` — **karardan ÖNCEKİ girdi** (🔒 tarih damgalı)

Bir kararın gerekçesi değil, **hammaddesi**: literatür taraması, rakip analizi, ham
tasarım sohbeti. *Karar `mimari/`'ye ya da `plan/`'a yazılır; buradaki metin onun
kaynağıdır ve **değiştirilmez**.*

| dosya | ne |
|---|---|
| [`2026-08-11_REKABET-VE-MIMARI-ANALIZI.md`](arastirma/2026-08-11_REKABET-VE-MIMARI-ANALIZI.md) | rekabet + mimari analiz |
| [`2026-08-07_v2-v3-MIMARI-KARAR-SOHBETI.md`](arastirma/2026-08-07_v2-v3-MIMARI-KARAR-SOHBETI.md) | 🔴 **garson devrinin doğduğu ham sohbet** — *«LLM anlar → makine diline çevirir → küpler işler → LLM insan diliyle servis eder»* |
| [`2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md`](arastirma/2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md) | mimari çıkmaz araştırması — vizyon→teorik teşhis→canlı ölçüm→§13/§15 düzeltmeleri |
| [`2026-08-26_PLAYWRIGHT-CANLI-TEST-KAMPANYASI.md`](arastirma/2026-08-26_PLAYWRIGHT-CANLI-TEST-KAMPANYASI.md) | 15 gerçek kullanıcı senaryosu, tarayıcıda tek tek test edildi — K1-K13 kök sorunlar (veri+UI) |

## `denetim/` — 🔒 tarih damgalı ölçümler (**değiştirilmez**)

Adlandırma: **`YYYY-AA-GG_KONU.md`**. Tarih **başta** ki dizin kendiliğinden
kronolojik sıralansın.

| dosya | ne ölçtü |
|---|---|
| [`2026-08-05_DENETIM.md`](denetim/2026-08-05_DENETIM.md) | genel sistem denetimi |
| [`2026-08-05_V1-SON-KONTROL.md`](denetim/2026-08-05_V1-SON-KONTROL.md) | v1 çıkış kontrolü |
| [`2026-08-05_UI-UX-DENETIM.md`](denetim/2026-08-05_UI-UX-DENETIM.md) | arayüz denetimi |
| [`2026-08-05_TEST-ORTAMI-RAPORU.md`](denetim/2026-08-05_TEST-ORTAMI-RAPORU.md) | test ortamının **durum** ölçümü |
| [`2026-08-05_TEST-ORTAMI-ARASTIRMA.md`](denetim/2026-08-05_TEST-ORTAMI-ARASTIRMA.md) | literatür taraması (Spider 2.0 · BEAVER · InsightBench · MT-TEQL) |
| [`2026-08-05_ANLAMA-KATMANI.md`](denetim/2026-08-05_ANLAMA-KATMANI.md) | ⏸ anlama katmanı kök-neden analizi — *ilerinin konusu* |
| [`2026-08-07_CANLI-ARIZA-TESHISI.md`](denetim/2026-08-07_CANLI-ARIZA-TESHISI.md) | 🔴 canlı üç arıza: **Intent-JSON 9/9 `cube:null`** (katalog Türkçe eşanlamları taşımıyor) · anlatıda deterministik basamak yok · 500 backend'den **çıkmadı** |
| [`2026-08-07_LLM-YOLU-TESHISI-ve-GERI-DONULEBILIR-DENEY.md`](denetim/2026-08-07_LLM-YOLU-TESHISI-ve-GERI-DONULEBILIR-DENEY.md) | 🔴 iki inanış ÇÜRÜDÜ: deterministik katman **kesmiyor** (gerçek dilde %93,3'ü devrediyor, 42 vakada 0 çözüyor) ve LLM **yanlış anlamıyor, REDDEDİYOR**. LLM #1 (çevirmen) ↔ Discovery (ham SQL) ayrımı · beş eksik · **geri dönülebilir deney planı** — yarısı bugün `yol_siniri:"llm"` ile kodsuz koşulabilir |
| [`2026-08-07_CEVIRI-SOZLESMESI.md`](denetim/2026-08-07_CEVIRI-SOZLESMESI.md) | 🔴 **«LLM anlıyor; SÖYLEYEMİYOR».** Sistem dili net ama garsonun fişi eksik: `route()` **12 anahtar** üretebiliyor, şema modele **7** alan sunuyor — `order`·`limit`·`entity_limit`·`measure_having`·`ayrik_aylar`·`referans` mutfakta çalışıyor, LLM ifade **edemiyor**. ⊙ Model **kolay** işte (takip: 21 örnek, 6 ek alan, `reason`) **zor** işten (taze: 5 örnek, sebepsiz `cube:null`) daha yetkili. 🔴 Ve *neyin ne yaptığı* bir yerde gerçekten karışık: sorgunun sahibi LLM, *«ne istendi»* iddiasının sahibi deterministik `Niyet` → ölçülmüş **yanlış beyan** |
| [`2026-08-10_TABAN-BORCLARI-ve-KATALOG-KOKU.md`](denetim/2026-08-10_TABAN-BORCLARI-ve-KATALOG-KOKU.md) | 🔴🔴 **DÖNGÜ KURALINA DAHİL** — `OPERASYON.md §2c/T`, her demet kapanışında denetlenir. **Orkestratör bir TAVAN açtı, tabanı yükseltmedi**: tabanı `route()`+**katalog** belirliyor ve bu turun iki sessiz-yanlışının **ikisi de** katalogdan geldi. Kullanıcı tezi (*"garson güvenilir olsun, sinonim gerekmesin"*) **düzeltildi**: katalog route'un sözlüğü değil **garsonun menüsüdür** (kanıt: sözlüksüz dönemde **9/9 `cube:null`**) — doğru okunuşu *"route sahte kesinlik üretmesin"*. ⊙ Taze statik ölçüm: **28 küp · 173 ölçü · 141 benzersiz ad · 13 çok sahipli · yön beyanı 125'te YOK (%72)** · «müşteri» **5 ad, 3 ayrık aile** → `blend` yapısal olarak kurulamıyor · `cekirdek/` katmanında `metrikler` var **`varliklar` YOK** · `eval --slice llm` **4 vaka**, `nl_corpus` **LLM'siz**. **Yedi borç** (`B-0`…`B-7`) teşhis · kanıt · kök · kök çözüm ile. 🔴 `B-1` (garson korpusu) birinci sırada: kurulmadan öteki hiçbir kararın kazancı okunamaz. ⊘ **Hiçbir test koşulmadı**; canlı derlenmiş şema okunmadı |
| [`2026-08-09_KAPI-YAVASLAMASI-TESHISI.md`](denetim/2026-08-09_KAPI-YAVASLAMASI-TESHISI.md) | 🔴🔴 **DÖNGÜ KURALINA DAHİL · ÖNCELİKLİ** *(günde ~3s 32dk saf bekleme — ölçüldü)*. **Kapı 1:50 → 13:00 (7,1×) — ve sebep kapı değil ÜRÜN.** Paralellik sağlam, payda kırpılmadı (tersine **+%38**); `/ask` **47→177 ms** yavaşladı (×3,8). Mekanizma: 5 günde 335 commit · sıcak yola **41 yeni modül** (17'si `ask.py`'de) · `cube_router`'da **sıfır** memoizasyon · `partial_unknowns` 4→7 çağrı. Vaka: **11 satırlık commit = +94 sn**. ⊙ Yan bulgular: `--hepsi` kendi belgesine aykırı `eval_llm` koşuyor · `_AGIR` dilim sabiti bayat · wren-engine **3209 restart**. 🔴 En kalıcı öneri: **latency tavanı kapısı** — 47→177 ms görünmedi çünkü ölçen kapı yoktu. ⚠ **Hiçbir test koşulmadan** ölçüldü (26 tarihsel konteyner kütüğü + git); profil **yapılmadı** |

### ⟳ `denetim/` içinde **üçüncü bir sınıf**: canlı kayıt defteri

`DENETIM-FAZ-A-F.md` ve `DENETIM-A-G.md` bir **fotoğraf değil**, sürekli eklenen **tek
kayıt**tır (*«ajan bulgularının TEK KAYDI»*). Tarih damgası vermek *«değiştirilmez»*
sözünü yalan yapardı; `belgeler/` köküne taşımak ise yanlış olurdu — orası **kapıyla**
canlı tutulan yayın sınıfıdır, bu ikisini tutan bir kapı yok. Sınıf `test_belge_duzeni.py
::DENETIM_CANLI_DEFTER`'de **adıyla** ilan edildi; listeye ad eklemek **yazılı gerekçe**
ister.

## `devir/` — 🔒 oturum devri (**değiştirilmez**)

`HANDOFF_*.md` — tarihsel kayıt. ⚠ *Mimari otorite değildir* (`backend/CLAUDE.md`).

## `arsiv/` — kaldırıldı ama silinmedi

`legacy/` — eski backend ve yol haritaları. *Kapananlar işaretlenir, silinmez*
(`MIMARI.md` §10).

---

## Yeni bir belge yazacaksan — üç soru

| soru | cevap |
|---|---|
| **Bir ölçüm mü?** (tarih damgalı, o anın fotoğrafı) | `denetim/YYYY-AA-GG_KONU.md` — ve **bir daha değiştirme** |
| **Bir talimat mı?** (nasıl yapılır, güncellenir) | `kilavuz/` |
| **Bir karar mı?** (neden böyle) | `mimari/` — ama önce `backend/MIMARI.md`'ye mi ait diye bak |

🔴 **Hiçbiri değilse köke koyma.** Kök üç dosyalıktır ve bir kapı bunu sınıyor
(`backend/tests/test_belge_duzeni.py`). *Bir istisna, bir sonraki istisnanın gerekçesi
olur; ve üç istisna sonra kural kalmaz.*
