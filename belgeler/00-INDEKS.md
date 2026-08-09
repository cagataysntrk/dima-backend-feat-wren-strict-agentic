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
| [`OPERASYON.md`](../OPERASYON.md) | kural seti · döngü adımları · test kapısı · öz-denetim |
| [`OPERASYON-DURUM.md`](../OPERASYON-DURUM.md) | **nerede kaldık** · açık borçlar · ölçüm tabanı |
| [`OPERASYON-DENETIM.md`](../OPERASYON-DENETIM.md) | denetim ajanlarının görev metinleri |

---

## `kilavuz/` — *nasıl yapılır* (canlı)

| dosya | kime |
|---|---|
| [`SERVER_COMMANDS.md`](kilavuz/SERVER_COMMANDS.md) | sistemi **ayağa kaldıracak** herkese — port 8001, frontend **pnpm** |
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
| [`2026-08-09_KAPI-YAVASLAMASI-TESHISI.md`](denetim/2026-08-09_KAPI-YAVASLAMASI-TESHISI.md) | 🔴🔴 **DÖNGÜ KURALINA DAHİL · ÖNCELİKLİ** *(günde ~3s 32dk saf bekleme — ölçüldü)*. **Kapı 1:50 → 13:00 (7,1×) — ve sebep kapı değil ÜRÜN.** Paralellik sağlam, payda kırpılmadı (tersine **+%38**); `/ask` **47→177 ms** yavaşladı (×3,8). Mekanizma: 5 günde 335 commit · sıcak yola **41 yeni modül** (17'si `ask.py`'de) · `cube_router`'da **sıfır** memoizasyon · `partial_unknowns` 4→7 çağrı. Vaka: **11 satırlık commit = +94 sn**. ⊙ Yan bulgular: `--hepsi` kendi belgesine aykırı `eval_llm` koşuyor · `_AGIR` dilim sabiti bayat · wren-engine **3209 restart**. 🔴 En kalıcı öneri: **latency tavanı kapısı** — 47→177 ms görünmedi çünkü ölçen kapı yoktu. ⚠ **Hiçbir test koşulmadan** ölçüldü (26 tarihsel konteyner kütüğü + git); profil **yapılmadı** |

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
